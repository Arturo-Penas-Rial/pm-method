"""Servicio HTTP de pm-kb: portal web (cartera, tableros, búsqueda, artefactos, preguntar y fichas), vista de enlaces
compartidos (`/v`) y MCP por HTTP en `/mcp`, con token por persona. docs/PM-KB.md §11.

Seguridad: todo pide sesión o token, salvo `/salud` y las páginas estáticas de ingreso y de enlace compartido. Sesiones
web con identificador propio (docs/PM-KB.md §11.7): `/ingresar` (token personal) y `/v/canje` (token de un enlace
compartido, que llega en el fragmento de `/v#<token>` y la página manda por POST) dejan una cookie HttpOnly y
SameSite=Strict (Secure con https) con un id de sesión aleatorio, nunca el token; la base guarda solo su sha256 y la
sesión cae en la petición siguiente si el token o el enlace se revoca o vence. `Authorization: Bearer <token>` sigue
valiendo para la API y `/mcp`. Una sesión de enlace compartido solo ve su proyecto y su tablero (el actual o una
instantánea, filtrado por actor si el enlace lo tiene) y las fichas de las tarjetas de ese tablero: nada de buscar,
preguntar, MCP, cartera, artefactos, documentos ni «actualizar ahora» (403), ni otros proyectos, instantáneas o fichas
(404). Los canjes fallidos tienen un límite por IP (429) y exigen un `Origin` de PMKB_ORIGENES.

Las consultas leen como `pmkb_lector` con RLS por proyecto y circulación; cabeceras CSP sin scripts en línea; los POST
y `/mcp` validan el origen; con host de bucle local (127.0.0.1) se crea un token de la sesión y se muestra el enlace de
ingreso. Única escritura de contenido: «actualizar ahora» (`POST /api/tablero/actualizar`), que regenera el tablero de
un proyecto visible en el índice con la conexión del dueño del índice (nunca en la carpeta), solo para sesiones de token
personal, con el origen exigido y un límite por token; las sesiones y los usos de los enlaces los escriben funciones
SECURITY DEFINER de la base. Los documentos HTML del proyecto (`/archivo/…`) se entregan con
su propia CSP aislada (`sandbox`) para mostrarlos en un iframe sin acceso al portal.
"""
import hashlib, ipaddress, json, os, queue, secrets, sys, threading, time, urllib.parse
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from . import VERSION, config, documentos, mcp, tablero as TB
from .busqueda import Sesion

ESTATICO = Path(__file__).parent / "estatico"
COOKIE = "pmkb"
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")


class Pool:
    """Conexiones de solo lectura reutilizables (hilos del servidor); se descarta la que falla."""

    def __init__(self, maximo=8):
        self.libres, self.maximo, self.creadas, self.lock = queue.LifoQueue(), maximo, 0, threading.Lock()

    def tomar(self):
        try:
            c = self.libres.get_nowait()
            if not c.closed:
                return c
        except queue.Empty:
            pass
        with self.lock:
            if self.creadas < self.maximo:
                self.creadas += 1
                try:
                    return config.conectar(lector=True)
                except Exception:
                    self.creadas -= 1
                    raise
        c = self.libres.get(timeout=30)
        return c if not c.closed else config.conectar(lector=True)

    def devolver(self, c, roto=False):
        if roto or c.closed:
            try:
                c.close()
            finally:
                with self.lock:
                    self.creadas -= 1
            return
        if c.info.transaction_status != 0:
            c.rollback()
        self.libres.put(c)


POOL = Pool()
_IDENT = {}          # sha → (vence, identidad) de los tokens que llegan por Authorization: Bearer
SESION_HORAS = 12    # duración máxima de una sesión web (nunca más que el token o el enlace)
SOLO_TABLERO = "un enlace compartido solo da acceso a su tablero y a las fichas de sus tarjetas"


def _sha(x):
    return hashlib.sha256(x.encode("utf-8")).hexdigest()


def _consulta(sql, params):
    """Filas de una sentencia como `pmkb_lector` en su propia transacción (no de solo lectura: las funciones de sesión
    escriben con SECURITY DEFINER). Reintenta ante un interbloqueo con `pm-kb verificar`/`base crear` (Sesion._tx)."""
    import psycopg
    c = POOL.tomar()
    try:
        for intento in range(3):
            try:
                with c.transaction():
                    cur = c.execute(sql, params)
                    filas = cur.fetchall() if cur.description else []
                break
            except (psycopg.errors.DeadlockDetected, psycopg.errors.SerializationFailure):
                if intento == 2:
                    raise
                time.sleep(0.2 * (intento + 1))
        POOL.devolver(c)
    except Exception:
        POOL.devolver(c, roto=True)
        raise
    return filas


def identidad(token):
    """Identidad de un token personal (Authorization: Bearer), con caché de 60 s (SEG-19)."""
    if not token or len(token) > 200:
        return None
    sha = _sha(token)
    ahora = time.time()
    if sha in _IDENT and _IDENT[sha][0] > ahora:
        return _IDENT[sha][1]
    filas = _consulta("SELECT persona, proyectos, restringida, vence FROM pmkb.identidad(%s)", (sha,))
    r = filas[0] if filas else None
    ident = {"persona": r[0], "proyectos": r[1], "restringida": r[2], "tipo": "persona", "clave": _sha(sha)} if r else None
    hasta = ahora + 60
    if r and r[3] is not None:
        hasta = min(hasta, r[3].timestamp())      # un token vencido no sobrevive en la caché
    _IDENT[sha] = (hasta, ident)
    return ident


def sesion(sid):
    """Identidad de una cookie de sesión (personal o de enlace compartido), sin caché: revocar o vencer el token o el
    enlace la corta en la petición siguiente."""
    if not sid or len(sid) > 200:
        return None
    filas = _consulta("""SELECT tipo, persona, proyectos, restringida, vence, clave, enlace, alcance, actor, actor_nombre, enlace_vence
                         FROM pmkb.sesion_identidad(%s)""", (_sha(sid),))
    if not filas:
        return None
    t, persona, proyectos, restr, vence, clave, enl, alc, actor, actor_nombre, enl_vence = filas[0]
    ident = {"tipo": t, "persona": persona, "proyectos": proyectos, "restringida": bool(restr), "clave": clave, "vence": vence}
    if t == "enlace":
        ident["enlace"] = {"id": enl, "proyecto": proyectos, "alcance": alc or "actual", "actor": actor or "", "actor_nombre": actor_nombre or "",
                           "restringida": bool(restr), "vence": enl_vence}
    return ident


def ident_de(req):
    """Identidad del pedido: `Authorization: Bearer <token personal>` o la cookie de sesión."""
    h = req.headers.get("authorization", "")
    if h.lower().startswith("bearer "):
        return identidad(h[7:].strip())
    return sesion(req.cookies.get(COOKIE, ""))


def origen_valido(req, exigir=False):
    """El origen del pedido es el propio servicio o uno de PMKB_ORIGENES; sin cabecera Origin vale, salvo con `exigir`."""
    o = req.headers.get("origin")
    if not o:
        return not exigir
    propio = f"{req.url.scheme}://{req.headers.get('host', '')}"
    return o.rstrip("/") in [propio] + config.origenes()


def origen_canje_valido(req):
    """Canje de un enlace compartido: Origin obligatorio y de PMKB_ORIGENES (el origen con que se arman los enlaces).
    Sin PMKB_ORIGENES, solo el propio servicio en una dirección de bucle local (`pm-kb servir` en 127.0.0.1)."""
    o = (req.headers.get("origin") or "").rstrip("/")
    if not o:
        return False
    conf = config.origenes()
    if conf:
        return o in conf
    return o == f"{req.url.scheme}://{req.headers.get('host', '')}" and _es_local(req.url.hostname or "")


def con_ident(ident, fn):
    c = POOL.tomar()
    try:
        r = fn(Sesion(c, ident["proyectos"], ident["restringida"], ident["persona"]))
        POOL.devolver(c)
        return r
    except Exception:
        POOL.devolver(c, roto=True)
        raise


def _json(datos, estado=200):
    return JSONResponse(json.loads(json.dumps(datos, default=str, ensure_ascii=False)), status_code=estado)


def api(fn, enlace=None):
    """Ruta JSON de la API. `fn(sesion, pedido)` para sesiones y tokens personales; `enlace(sesion, pedido, enlace)` para
    una sesión de enlace compartido (si es None, el enlace recibe 403). Un dict con solo `error` responde 404."""
    def ruta(req: Request):
        try:
            ident = ident_de(req)
            if not ident:
                return _json({"error": "sin sesión: ingresar con el enlace o el token"}, 401)
            if ident["tipo"] == "enlace":
                if enlace is None:
                    return _json({"error": SOLO_TABLERO}, 403)
                r = con_ident(ident, lambda s: enlace(s, req, ident["enlace"]))
            else:
                r = con_ident(ident, lambda s: fn(s, req))
        except Exception as x:
            print(f"pm-kb: error en {req.url.path}: {type(x).__name__}: {x}", file=sys.stderr)
            return _json({"error": "error interno del servicio (ver el registro del servidor)"}, 500)
        if isinstance(r, Response):
            return r
        return _json(r, 404 if isinstance(r, dict) and "error" in r and len(r) == 1 else 200)
    return ruta


def _b(v):
    return str(v).lower() in ("1", "true", "si", "sí", "on")


def q(req, k, defecto=None):
    v = req.query_params.get(k)
    return v if v not in (None, "") else defecto


async def preguntar(req: Request):
    if not origen_valido(req):
        return _json({"error": "origen no permitido"}, 403)
    try:
        cuerpo = await req.json()
    except ValueError:
        return _json({"error": "JSON inválido"}, 400)
    pregunta = str(cuerpo.get("pregunta") or "").strip()[:1000]
    if not pregunta:
        return _json({"error": "falta la pregunta"}, 400)
    from starlette.concurrency import run_in_threadpool

    def fn():
        ident = ident_de(req)
        if not ident:
            return None
        if ident["tipo"] == "enlace":
            return _json({"error": SOLO_TABLERO}, 403)
        return con_ident(ident, lambda s: s.preguntar(pregunta, cuerpo.get("historial") or [], proyecto=cuerpo.get("proyecto") or None,
                                                       estado="aprobado" if cuerpo.get("aprobado") else None))
    try:
        r = await run_in_threadpool(fn)
    except Exception as x:
        print(f"pm-kb: error en /api/preguntar: {type(x).__name__}: {x}", file=sys.stderr)
        return _json({"error": "error interno del servicio"}, 500)
    if isinstance(r, Response):
        return r
    return _json(r) if r is not None else _json({"error": "sin sesión"}, 401)


async def mcp_http(req: Request):
    if req.method != "POST":
        return Response(status_code=405, headers={"Allow": "POST"})
    if not origen_valido(req):
        return _json({"error": "origen no permitido"}, 403)
    from starlette.concurrency import run_in_threadpool
    try:
        msg = json.loads(await req.body())
    except ValueError:
        return _json(mcp._error(None, -32700, "JSON inválido"), 400)
    ident = await run_in_threadpool(ident_de, req)
    if not ident:
        return Response(status_code=401, headers={"WWW-Authenticate": 'Bearer realm="pm-kb"'})
    if ident["tipo"] == "enlace":
        return _json({"error": SOLO_TABLERO}, 403)

    def fn():
        c = POOL.tomar()
        roto = False
        try:
            s = Sesion(c, ident["proyectos"], ident["restringida"], ident["persona"])
            if isinstance(msg, list):
                return [x for x in (mcp.manejar(m, lambda: s) for m in msg) if x] or None
            return mcp.manejar(msg, lambda: s)
        except Exception:
            roto = True
            raise
        finally:
            POOL.devolver(c, roto)
    r = await run_in_threadpool(fn)
    if r is None:
        return Response(status_code=202)
    return JSONResponse(r)


def inicio(req: Request):
    """Las pantallas del portal (cartera `/`, proyecto `/p/<proyecto>/…`, ficha `/p/<proyecto>/ficha/<ref>`, `/buscar` y
    `/preguntar`) son la misma página; la dibuja estatico/app.js según la ruta. Sin sesión, la de ingreso; una sesión de
    enlace compartido va a su tablero (`/v`)."""
    ident = ident_de(req)
    if not ident:
        return FileResponse(ESTATICO / "ingresar.html")
    if ident["tipo"] == "enlace":
        return RedirectResponse("/v", status_code=303)
    return FileResponse(ESTATICO / "index.html")


# ------------------------------------------------------------------ «actualizar ahora»
class Limite:
    """Límite de uso por token: uno cada `cada` segundos y `por_hora` por hora (en memoria del servicio)."""

    def __init__(self, cada=30, por_hora=20):
        self.cada, self.por_hora, self.usos, self.lock = cada, por_hora, {}, threading.Lock()

    def pedir(self, clave):
        """0 si se admite (y lo cuenta); si no, los segundos que faltan."""
        ahora = time.monotonic()
        with self.lock:
            usos = [x for x in self.usos.get(clave, []) if ahora - x < 3600]
            if usos and ahora - usos[-1] < self.cada:
                return int(self.cada - (ahora - usos[-1])) + 1
            if len(usos) >= self.por_hora:
                return int(3600 - (ahora - usos[0])) + 1
            usos.append(ahora)
            self.usos[clave] = usos
            return 0


LIMITE = Limite()


async def actualizar(req: Request):
    """POST /api/tablero/actualizar {"proyecto": P}: regenera el tablero del proyecto con el núcleo de pm-method (solo
    lectura de la carpeta) y lo publica en el índice. Solo sesiones de token personal, con Origin propio o de
    PMKB_ORIGENES, un pedido cada 30 s y 20 por hora por token (429 con Retry-After)."""
    from starlette.concurrency import run_in_threadpool
    if not origen_valido(req, exigir=True):
        return _json({"error": "origen no permitido (actualizar ahora exige la cabecera Origin del portal)"}, 403)
    ident = await run_in_threadpool(ident_de, req)
    if not ident:
        return _json({"error": "sin sesión"}, 401)
    if ident.get("tipo") != "persona":
        return _json({"error": "actualizar ahora solo está disponible con un token personal"}, 403)
    try:
        cuerpo = json.loads((await req.body())[:4096] or b"{}")
    except ValueError:
        return _json({"error": "JSON inválido"}, 400)
    proyecto = str((cuerpo or {}).get("proyecto") or "").strip()[:200] if isinstance(cuerpo, dict) else ""
    if not proyecto:
        return _json({"error": "falta el proyecto"}, 400)

    try:
        res = await run_in_threadpool(lambda: con_ident(ident, lambda s: s.carpeta(proyecto)))
    except Exception as x:
        print(f"pm-kb: error en /api/tablero/actualizar: {type(x).__name__}: {x}", file=sys.stderr)
        return _json({"error": "error interno del servicio"}, 500)
    if not res:
        return _json({"error": f"el proyecto '{proyecto}' no existe o no es visible"}, 404)
    p, raiz, gestion = res
    if gestion is None:
        return _json({"error": f"'{p}' no es un proyecto de pm-method (sin estado.json): no tiene tablero"}, 404)
    if not raiz or not os.path.isdir(os.path.join(raiz, gestion)):
        return _json({"error": "la carpeta indexada no está accesible desde el servicio"}, 503)
    espera = LIMITE.pedir(ident["clave"])
    if espera:
        return JSONResponse({"error": f"demasiados pedidos: probá de nuevo en {espera} s", "reintentar_en": espera}, status_code=429,
                            headers={"Retry-After": str(espera)})

    def publicar():
        a = config.conectar(lector=False)
        try:
            return TB.publicar(a, p, raiz, gestion, origen="web", por=ident["persona"])
        finally:
            a.close()
    try:
        r = await run_in_threadpool(publicar)
    except TB.ErrorTablero as x:
        return _json({"error": f"no se pudo generar el tablero: {x}"}, 502)
    except Exception as x:
        print(f"pm-kb: actualizar ahora ({p}): {type(x).__name__}: {str(x)[:300]}", file=sys.stderr)
        return _json({"error": "actualizar ahora no disponible: el servicio no pudo escribir el tablero en el índice "
                               "(necesita la conexión del dueño del índice, PMKB_DSN)"}, 503)
    return _json({"proyecto": p, "version": r["version"], "cambio": r["cambio"], "corte": r["datos"].get("corte"),
                  "instantaneas": r["instantaneas"], "avisos": r["avisos"]})


# ------------------------------------------------------------------ documentos del proyecto (marco aislado)
def api_documentos(s, req):
    d = s.documentos_html(q(req, "proyecto", ""))
    if "error" in d:
        return d
    accesible = bool(d["raiz"]) and os.path.isdir(d["raiz"])
    docs = documentos.listar(d["raiz"], d["documentos"]) if accesible else []
    return {"proyecto": d["proyecto"], "accesible": accesible, "documentos": docs}


def archivo(req: Request):
    """GET /archivo/<proyecto>/<ruta>[?descargar=1]: un documento HTML indexado y visible (o el SVG/PNG con su mismo
    nombre) de la carpeta indexada, con una CSP aislada propia; nunca un archivo fuera de esa carpeta."""
    ident = ident_de(req)
    if not ident:
        return PlainTextResponse("sin sesión", 401)
    if ident["tipo"] == "enlace":
        return PlainTextResponse(SOLO_TABLERO, 403)
    proyecto, ruta = req.path_params["proyecto"], req.path_params["ruta"]
    ext = os.path.splitext(ruta)[1].lower()
    if ext not in documentos.TIPOS:
        return PlainTextResponse("no disponible", 404)
    candidatas = [ruta] if ext in (".html", ".htm") else [os.path.splitext(ruta)[0] + x for x in (".html", ".htm")]
    try:
        res = con_ident(ident, lambda s: [s.archivo_visible(proyecto, c) for c in candidatas])
    except Exception as x:
        print(f"pm-kb: error en /archivo: {type(x).__name__}: {x}", file=sys.stderr)
        return PlainTextResponse("error interno del servicio", 500)
    ok = [x for x in res or [] if x and x[2]]
    if not ok:
        return PlainTextResponse("no disponible", 404)
    pa = documentos.dentro(ok[0][1], ruta)
    if not pa or os.path.getsize(pa) > documentos.MAX_BYTES:
        return PlainTextResponse("no disponible", 404)
    scripts = ext in (".html", ".htm") and documentos.con_scripts(pa)
    h = {"Content-Security-Policy": documentos.csp(scripts), "X-Frame-Options": "SAMEORIGIN", "Cross-Origin-Resource-Policy": "same-origin"}
    if _b(q(req, "descargar", "")):
        h["Content-Disposition"] = documentos.nombre_descarga(ruta)
    with open(pa, "rb") as f:
        return Response(f.read(), media_type=documentos.TIPOS[ext], headers=h)


def token_del_formulario(cuerpo):
    """Campo `token` de un formulario application/x-www-form-urlencoded (el de ingresar.html), con la biblioteca
    estándar: `Request.form()` de Starlette exige el paquete python-multipart, que pm-kb no instala."""
    try:
        campos = urllib.parse.parse_qs(cuerpo[:4096].decode("utf-8"), max_num_fields=5)
    except (UnicodeDecodeError, ValueError):
        return ""
    return (campos.get("token") or [""])[0].strip()


def _https(req):
    """¿Se llegó por https? (el propio servicio o, detrás de un proxy con TLS, el Origin del navegador)."""
    return req.url.scheme == "https" or (req.headers.get("origin") or "").startswith("https://")


def _poner_cookie(resp, req, sid, vence):
    """Cookie de sesión: solo el id aleatorio (nunca el token), HttpOnly, SameSite=Strict, Secure con https, y que no
    dure más que la sesión."""
    edad = max(1, min(SESION_HORAS * 3600, int(vence.timestamp() - time.time())))
    resp.set_cookie(COOKIE, sid, httponly=True, samesite="strict", secure=_https(req), max_age=edad, path="/")


async def ingresar(req: Request):
    """Ingreso con un token personal (formulario POST o `?token=` del enlace que imprime `pm-kb servir`): abre una sesión
    de hasta 12 horas (sin pasar del vencimiento del token) y deja su id en la cookie."""
    if req.method == "POST":
        if not origen_valido(req):
            return PlainTextResponse("origen no permitido", 403)
        tok = token_del_formulario(await req.body())
    else:
        tok = req.query_params.get("token", "").strip()
    from starlette.concurrency import run_in_threadpool
    if not tok or len(tok) > 200:
        return RedirectResponse("/?error=token", status_code=303)
    sid = secrets.token_urlsafe(32)
    filas = await run_in_threadpool(_consulta, "SELECT pmkb.abrir_sesion(%s, %s, %s)", (_sha(tok), _sha(sid), SESION_HORAS))
    vence = filas[0][0] if filas else None
    if vence is None:
        return RedirectResponse("/?error=token", status_code=303)
    r = RedirectResponse("/", status_code=303)
    _poner_cookie(r, req, sid, vence)
    return r


async def salir(req: Request):
    """Borra la sesión de la cookie (en la base y en el navegador)."""
    from starlette.concurrency import run_in_threadpool
    sid = req.cookies.get(COOKIE, "")
    destino = "/"
    if sid and len(sid) <= 200:
        ident = await run_in_threadpool(sesion, sid)
        if ident and ident["tipo"] == "enlace":
            destino = "/v"
        await run_in_threadpool(_consulta, "SELECT pmkb.cerrar_sesion(%s)", (_sha(sid),))
    r = RedirectResponse(destino, status_code=303)
    r.delete_cookie(COOKIE, path="/")
    return r


# ------------------------------------------------------------------ enlaces compartidos (/v)
class Fallos:
    """Canjes fallidos por IP: `maximo` en `ventana` segundos; después, 429 hasta que venza el más viejo (en memoria)."""

    def __init__(self, maximo=10, ventana=900):
        self.maximo, self.ventana, self.fallos, self.lock = maximo, ventana, {}, threading.Lock()

    def _vigentes(self, clave, ahora):
        return [x for x in self.fallos.get(clave, []) if ahora - x < self.ventana]

    def espera(self, clave):
        ahora = time.monotonic()
        with self.lock:
            xs = self._vigentes(clave, ahora)
            return int(self.ventana - (ahora - xs[0])) + 1 if len(xs) >= self.maximo else 0

    def anotar(self, clave):
        ahora = time.monotonic()
        with self.lock:
            if len(self.fallos) > 10000:            # no crecer sin límite: se descartan las IP sin fallos recientes
                self.fallos = {k: v for k, v in ((k, self._vigentes(k, ahora)) for k in self.fallos) if v}
            self.fallos[clave] = self._vigentes(clave, ahora) + [ahora]


FALLOS = Fallos()


def vista_compartida(req: Request):
    """`/v` y `/v/ficha/<ref>`: página estática del enlace compartido; lee el token del fragmento (#), que el navegador
    no envía al servidor, lo canjea por POST y dibuja el tablero o la ficha."""
    return FileResponse(ESTATICO / "compartido.html")


async def canje(req: Request):
    """POST /v/canje {"token": …}: canjea el token de un enlace compartido vigente por una sesión (cookie con un id
    aleatorio) y registra el uso. Exige Origin de PMKB_ORIGENES (403); 10 canjes fallidos por IP cada 15 min → 429."""
    from starlette.concurrency import run_in_threadpool
    if not origen_canje_valido(req):
        return _json({"error": "origen no permitido: el enlace se abre desde la dirección configurada del portal (PMKB_ORIGENES)"}, 403)
    ip = req.client.host if req.client else "?"
    espera = FALLOS.espera(ip)
    if espera:
        return JSONResponse({"error": f"demasiados intentos fallidos: probá de nuevo en {espera} s", "reintentar_en": espera},
                            status_code=429, headers={"Retry-After": str(espera)})
    try:
        cuerpo = json.loads((await req.body())[:4096] or b"{}")
    except ValueError:
        cuerpo = {}
    tok = str(cuerpo.get("token") or "").strip() if isinstance(cuerpo, dict) else ""
    filas = []
    sid = secrets.token_urlsafe(32)
    if tok and len(tok) <= 200:
        try:
            filas = await run_in_threadpool(_consulta, """SELECT id, proyecto, alcance, actor_nombre, restringida, vence, enlace_vence
                                                          FROM pmkb.canjear(%s, %s, %s)""", (_sha(tok), _sha(sid), SESION_HORAS))
        except Exception as x:
            print(f"pm-kb: error en /v/canje: {type(x).__name__}: {x}", file=sys.stderr)
            return _json({"error": "error interno del servicio"}, 500)
    if not filas:
        FALLOS.anotar(ip)
        return _json({"error": "el enlace no es válido, venció o fue revocado: pedí uno nuevo a quien te lo envió"}, 401)
    eid, proyecto, alcance, actor_nombre, restr, vence, enl_vence = filas[0]
    r = _json({"proyecto": proyecto, "alcance": alcance, "actor": actor_nombre, "restringida": restr,
               "vence": enl_vence.isoformat(timespec="minutes")})
    _poner_cookie(r, req, sid, vence)
    return r


def _tablero_del_enlace(s, e, solo_version=False):
    """El tablero que da el enlace (actual o instantánea), filtrado por su actor; un dict con `error` (404) o una
    respuesta 503 si el filtro por actor no puede leer la carpeta."""
    inst = None if e["alcance"] == "actual" else e["alcance"]
    r = s.tablero(e["proyecto"], inst, solo_version=solo_version)
    if "error" in r:
        return {"error": "el tablero de este enlace ya no está publicado"}
    if e["actor"] and not solo_version:
        try:
            r["datos"] = _por_actor(s, e["proyecto"], r["datos"], e["actor"])
        except _SinCarpeta as x:
            return _json({"error": str(x)}, 503)
        except TB.ErrorTablero as x:
            return _json({"error": f"no se pudo armar el tablero de {e['actor_nombre'] or e['actor']}: {x}"}, 503)
    return r


def _mismo_proyecto(s, req, e):
    p = q(req, "proyecto")
    return not p or s.instancia(p) == e["proyecto"]


def tablero_enlace(s, req, e, solo_version=False):
    """GET /api/tablero[/version] con una sesión de enlace: solo su proyecto y su tablero (otro → 404)."""
    inst = q(req, "instantanea")
    if not _mismo_proyecto(s, req, e) or (inst and inst != e["alcance"]):
        return {"error": "no disponible con este enlace"}
    return _tablero_del_enlace(s, e, solo_version)


def ficha_enlace(s, req, e):
    """GET /api/ficha con una sesión de enlace: solo de una tarjeta del tablero del enlace (otra → 404), completa, sin los
    relacionados que no están en ese tablero (se informa cuántos se omitieron)."""
    ref = (q(req, "id", "") or "").strip()
    if not _mismo_proyecto(s, req, e):
        return {"error": "no disponible con este enlace"}
    t = _tablero_del_enlace(s, e)
    if not isinstance(t, dict) or "error" in t:
        return t
    permitidos = TB.refs(t["datos"])
    if ref not in permitidos:
        return {"error": f"'{ref}' no está en el tablero de este enlace"}
    f = s.ficha(ref, proyecto=e["proyecto"], historia=True, max_tokens=3000)
    if "error" in f:
        return f
    omitidos = 0
    rel = {}
    for g, xs in (f.get("relacionados") or {}).items():
        quedan = [x for x in xs if x.get("id") in permitidos]
        omitidos += len(xs) - len(quedan)
        if quedan:
            rel[g] = quedan
    aristas = [x for x in f.get("relaciones") or [] if x.get("id") in permitidos]
    omitidos += len(f.get("relaciones") or []) - len(aristas)
    f.update(relacionados=rel, relaciones=aristas, otros_proyectos=[], fuera_del_tablero=omitidos)
    if e["alcance"] != "actual":           # la tarjeta tal como está en la instantánea, no la del tablero de hoy
        x = TB.tarjeta(t["datos"], ref)
        f["tablero"] = ({**{k: v for k, v in x[1].items() if k != "enlace"}, "vista": x[0], "tablero_version": None,
                         "corte": t["datos"].get("corte", ""), "instantanea": e["alcance"]} if x else None)
    return f


def estado_enlace(s, req, e):
    """GET /api/estado con una sesión de enlace: qué abre el enlace (sin datos del índice) y `puede_actualizar: false`."""
    inst = None
    if e["alcance"] != "actual":
        r = s.tablero(e["proyecto"], e["alcance"], solo_version=True)
        x = r.get("instantanea") or {}
        inst = {"id": e["alcance"], "etiqueta": x.get("etiqueta", ""), "fecha": x.get("fecha", ""), "corte": x.get("corte", "")}
    return {"persona": "enlace compartido", "puede_actualizar": False, "respuesta_con_modelo": False, "proyectos": [],
            "compartido": {"proyecto": e["proyecto"], "alcance": e["alcance"], "instantanea": inst, "actor": e["actor_nombre"] or e["actor"],
                           "restringida": e["restringida"], "vence": e["vence"].isoformat(timespec="minutes") if e.get("vence") else None}}


# ------------------------------------------------------------------ tableros por actor (sesiones personales)
class _SinCarpeta(RuntimeError):
    pass


def _gestion(s, proyecto):
    """Carpeta de gestión (con estado.json) de un proyecto visible, accesible desde el servicio; si no, _SinCarpeta."""
    res = s.carpeta(proyecto)
    if not res or res[2] is None:
        raise _SinCarpeta(f"'{proyecto}' no es un proyecto de pm-method visible")
    p, raiz, gestion = res
    g = Path(raiz or "") / gestion
    if not raiz or not (g / "estado.json").is_file():
        raise _SinCarpeta("la carpeta indexada no está accesible desde el servicio: el tablero por actor la necesita (raci.csv y registros)")
    return g


def _por_actor(s, proyecto, datos, actor):
    return TB.por_actor(datos, _gestion(s, proyecto), actor)


def tablero_persona(s, req, solo_version=False):
    """GET /api/tablero[/version]?proyecto=P[&instantanea=ID][&actor=…]: el actual o una instantánea; con `actor`, solo lo
    de esa persona (reglas del núcleo; actor inexistente → 404 con la lista de actores)."""
    r = s.tablero(q(req, "proyecto", ""), q(req, "instantanea"), solo_version=solo_version)
    actor = (q(req, "actor") or "").strip()[:120]
    if actor and not solo_version and "error" not in r:
        try:
            r["datos"] = _por_actor(s, r["proyecto"], r["datos"], actor)
        except _SinCarpeta as x:
            return _json({"error": str(x)}, 503)
        except TB.ErrorTablero as x:
            return {"error": str(x)}
    return r


def actores_persona(s, req):
    """GET /api/tablero/actores?proyecto=P: personas que pueden ser actor (stakeholders.csv y roles de estado.json)."""
    p = s.instancia(q(req, "proyecto", ""))
    if not p:
        return {"error": f"el proyecto '{q(req, 'proyecto', '')}' no existe o no es visible"}
    try:
        return {"proyecto": p, "actores": TB.actores(_gestion(s, p))}
    except _SinCarpeta as x:
        return _json({"error": str(x)}, 503)
    except TB.ErrorTablero as x:
        return _json({"error": f"no se pudieron leer los actores: {x}"}, 503)


def comparar_persona(s, req):
    """GET /api/tablero/comparar?proyecto=P&a=ID&b=ID|actual[&actor=…]: con `actor`, compara los dos tableros filtrados."""
    p, a, b, actor = q(req, "proyecto", ""), q(req, "a", ""), q(req, "b", "actual"), (q(req, "actor") or "").strip()[:120]
    if not actor:
        return s.comparar_tableros(p, a, b)
    ta, tb = s.tablero(p, None if a == "actual" else a), s.tablero(p, None if b == "actual" else b)
    for t in (ta, tb):
        if "error" in t:
            return t
    try:
        da, db = (_por_actor(s, ta["proyecto"], t["datos"], actor) for t in (ta, tb))
    except _SinCarpeta as x:
        return _json({"error": str(x)}, 503)
    except TB.ErrorTablero as x:
        return {"error": str(x)}
    return {"proyecto": ta["proyecto"], **TB.comparar(da, db)}


def salud(req):
    return PlainTextResponse("ok")


class Cabeceras:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def enviar(m):
            if m["type"] == "http.response.start":
                h = list(m.get("headers", []))
                propias = {k.lower() for k, _ in h}       # los documentos servidos traen su CSP aislada y su X-Frame-Options
                for k, v in (("content-security-policy", CSP), ("x-content-type-options", "nosniff"), ("referrer-policy", "no-referrer"),
                             ("x-frame-options", "DENY"), ("cache-control", "no-store"), ("permissions-policy", "camera=(), microphone=(), geolocation=()")):
                    if k.encode() not in propias:
                        h.append((k.encode(), v.encode()))
                m["headers"] = h
            await send(m)
        await self.app(scope, receive, enviar)


def crear_app():
    rutas = [
        Route("/", inicio), Route("/salud", salud), Route("/ingresar", ingresar, methods=["GET", "POST"]), Route("/salir", salir, methods=["POST"]),
        Route("/buscar", inicio), Route("/preguntar", inicio), Route("/p/{proyecto}", inicio), Route("/p/{proyecto}/{resto:path}", inicio),
        Route("/v", vista_compartida), Route("/v/ficha/{ref:path}", vista_compartida), Route("/v/canje", canje, methods=["POST"]),
        Route("/api/estado", api(lambda s, r: {**s.estado_indice(), "puede_actualizar": True}, enlace=estado_enlace)),
        Route("/api/cartera", api(lambda s, r: s.cartera())),
        Route("/api/tablero", api(tablero_persona, enlace=tablero_enlace)),
        Route("/api/tablero/version", api(lambda s, r: tablero_persona(s, r, solo_version=True), enlace=lambda s, r, e: tablero_enlace(s, r, e, solo_version=True))),
        Route("/api/tablero/actores", api(actores_persona)),
        Route("/api/tablero/historial", api(lambda s, r: s.historial(q(r, "proyecto", "")))),
        Route("/api/tablero/comparar", api(comparar_persona)),
        Route("/api/tablero/actualizar", actualizar, methods=["POST"]),
        Route("/api/artefactos", api(lambda s, r: s.artefactos(q(r, "proyecto", "")))),
        Route("/api/documentos", api(api_documentos)),
        Route("/archivo/{proyecto}/{ruta:path}", archivo),
        Route("/api/buscar", api(lambda s, r: s.buscar(q(r, "q", ""), proyecto=q(r, "proyecto"), tipo=q(r, "tipo"), registro=q(r, "registro"),
                                                      estado=q(r, "estado"), historia=_b(q(r, "historia", "")), k=int(q(r, "k", 10)),
                                                      max_tokens=int(q(r, "max_tokens", 6000)), facetas=True))),
        Route("/api/ficha", api(lambda s, r: s.ficha(q(r, "id", ""), proyecto=q(r, "proyecto"), historia=True, max_tokens=3000), enlace=ficha_enlace)),
        Route("/api/relaciones", api(lambda s, r: s.relaciones(q(r, "id", ""), proyecto=q(r, "proyecto"), saltos=int(q(r, "saltos", 1))))),
        Route("/api/versiones", api(lambda s, r: s.versiones(q(r, "doc", ""), proyecto=q(r, "proyecto")))),
        Route("/api/cambios", api(lambda s, r: s.cambios(q(r, "doc", ""), q(r, "desde"), q(r, "hasta"), proyecto=q(r, "proyecto"), max_tokens=4000))),
        Route("/api/documento", api(lambda s, r: s.documento(q(r, "fuente", ""), q(r, "rango"), proyecto=q(r, "proyecto"), max_tokens=4000))),
        Route("/api/preguntar", preguntar, methods=["POST"]),
        Route("/mcp", mcp_http, methods=["GET", "POST", "DELETE"]),
        Mount("/estatico", StaticFiles(directory=str(ESTATICO)), name="estatico"),
    ]
    return Starlette(routes=rutas, middleware=[Middleware(Cabeceras)])


def _es_local(host):
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host == "localhost"


def servir(host="127.0.0.1", puerto=8765):
    import uvicorn
    from .cli import crear_token
    error = config.puerto_ocupado(host, puerto)
    if error:
        sys.exit(f"pm-kb: no se puede escuchar en {host}:{puerto} ({error}). ¿Ya hay un `pm-kb servir` en marcha? "
                 f"Usar otro puerto: pm-kb servir --puerto {puerto + 1}")
    try:
        c = config.conectar(lector=True); c.close()
    except Exception as x:
        sys.exit(f"pm-kb: el rol de lectura no puede conectarse ({str(x).strip()[:200]}). Ver `pm-kb verificar`.")
    if _es_local(host):
        try:
            a = config.conectar()
            with a.transaction():
                a.execute("UPDATE pmkb.acceso SET revocado = now() WHERE persona = 'sesión local (servir)' AND revocado IS NULL")
            t = crear_token(a, "sesión local (servir)", "*", True, horas=24)
            a.close()
            print(f"pm-kb {VERSION}: abrí http://{'localhost' if host in ('127.0.0.1', '::1') else host}:{puerto}/ingresar?token={t}\n"
                  "  (enlace de esta sesión, vence en 24 h: el token anterior de la sesión local queda revocado)", flush=True)
        except Exception as x:
            print(f"pm-kb: sin token de sesión local ({str(x)[:120]}); crear uno con `pm-kb token crear`", flush=True)
    else:
        print(f"pm-kb {VERSION}: escuchando en {host}:{puerto}; ingresar con un token personal (`pm-kb token crear`). "
              "Fuera de una red de confianza, poner delante un proxy con TLS.", flush=True)
    uvicorn.run(crear_app(), host=host, port=puerto, log_level="warning", proxy_headers=False, server_header=False)
