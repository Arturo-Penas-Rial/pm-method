"""Servicio HTTP de pm-kb: interfaz web y MCP por HTTP en `/mcp`, con token por persona. docs/PM-KB.md §11.

Seguridad: todo pide token (cookie HttpOnly y SameSite=Strict tras `/ingresar`, o `Authorization: Bearer`), salvo
`/salud`; solo lectura en la base (rol `pmkb_lector` + RLS por proyecto y circulación); cabeceras CSP sin scripts en
línea; los POST y `/mcp` validan el origen; con host de bucle local (127.0.0.1) se crea un token de la sesión y se
muestra el enlace de ingreso.
"""
import hashlib, ipaddress, json, queue, sys, threading, time
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from . import VERSION, config, mcp
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
_IDENT = {}          # sha → (vence, identidad)


def identidad(token):
    if not token or len(token) > 200:
        return None
    sha = hashlib.sha256(token.encode("utf-8")).hexdigest()
    ahora = time.time()
    if sha in _IDENT and _IDENT[sha][0] > ahora:
        return _IDENT[sha][1]
    c = POOL.tomar()
    try:
        with c.transaction():
            r = c.execute("SELECT persona, proyectos, restringida FROM pmkb.identidad(%s)", (sha,)).fetchone()
        POOL.devolver(c)
    except Exception:
        POOL.devolver(c, roto=True)
        raise
    ident = {"persona": r[0], "proyectos": r[1], "restringida": r[2]} if r else None
    _IDENT[sha] = (ahora + 60, ident)
    return ident


def token_de(req):
    h = req.headers.get("authorization", "")
    if h.lower().startswith("bearer "):
        return h[7:].strip()
    return req.cookies.get(COOKIE, "")


def origen_valido(req):
    o = req.headers.get("origin")
    if not o:
        return True
    propio = f"{req.url.scheme}://{req.headers.get('host', '')}"
    return o.rstrip("/") in [propio] + config.origenes()


def con_sesion(req, fn):
    ident = identidad(token_de(req))
    if not ident:
        return None
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


def api(fn):
    def ruta(req: Request):
        try:
            r = con_sesion(req, lambda s: fn(s, req))
        except Exception as x:
            print(f"pm-kb: error en {req.url.path}: {type(x).__name__}: {x}", file=sys.stderr)
            return _json({"error": "error interno del servicio (ver el registro del servidor)"}, 500)
        if r is None:
            return _json({"error": "sin sesión: ingresar con el enlace o el token"}, 401)
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
        return con_sesion(req, lambda s: s.preguntar(pregunta, cuerpo.get("historial") or [], proyecto=cuerpo.get("proyecto") or None,
                                                      estado="aprobado" if cuerpo.get("aprobado") else None))
    try:
        r = await run_in_threadpool(fn)
    except Exception as x:
        print(f"pm-kb: error en /api/preguntar: {type(x).__name__}: {x}", file=sys.stderr)
        return _json({"error": "error interno del servicio"}, 500)
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
    tok = token_de(req)
    ident = await run_in_threadpool(identidad, tok)
    if not ident:
        return Response(status_code=401, headers={"WWW-Authenticate": 'Bearer realm="pm-kb"'})

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
    if not identidad(token_de(req)):
        return FileResponse(ESTATICO / "ingresar.html")
    return FileResponse(ESTATICO / "index.html")


async def ingresar(req: Request):
    if req.method == "POST":
        if not origen_valido(req):
            return PlainTextResponse("origen no permitido", 403)
        form = await req.form()
        tok = str(form.get("token") or "").strip()
    else:
        tok = req.query_params.get("token", "").strip()
    from starlette.concurrency import run_in_threadpool
    if not tok or not await run_in_threadpool(identidad, tok):
        return RedirectResponse("/?error=token", status_code=303)
    r = RedirectResponse("/", status_code=303)
    r.set_cookie(COOKIE, tok, httponly=True, samesite="strict", secure=req.url.scheme == "https", max_age=12 * 3600, path="/")
    return r


async def salir(req: Request):
    r = RedirectResponse("/", status_code=303)
    r.delete_cookie(COOKIE, path="/")
    return r


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
                for k, v in (("content-security-policy", CSP), ("x-content-type-options", "nosniff"), ("referrer-policy", "no-referrer"),
                             ("x-frame-options", "DENY"), ("cache-control", "no-store"), ("permissions-policy", "camera=(), microphone=(), geolocation=()")):
                    h.append((k.encode(), v.encode()))
                m["headers"] = h
            await send(m)
        await self.app(scope, receive, enviar)


def crear_app():
    rutas = [
        Route("/", inicio), Route("/salud", salud), Route("/ingresar", ingresar, methods=["GET", "POST"]), Route("/salir", salir, methods=["POST"]),
        Route("/api/estado", api(lambda s, r: s.estado_indice())),
        Route("/api/buscar", api(lambda s, r: s.buscar(q(r, "q", ""), proyecto=q(r, "proyecto"), tipo=q(r, "tipo"), registro=q(r, "registro"),
                                                      estado=q(r, "estado"), historia=_b(q(r, "historia", "")), k=int(q(r, "k", 10)),
                                                      max_tokens=int(q(r, "max_tokens", 6000)), facetas=True))),
        Route("/api/ficha", api(lambda s, r: s.ficha(q(r, "id", ""), proyecto=q(r, "proyecto"), historia=True, max_tokens=3000))),
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
    import socket
    import uvicorn
    from .cli import crear_token
    with socket.socket(socket.AF_INET6 if ":" in host else socket.AF_INET) as so:
        try:
            so.bind((host, puerto))
        except OSError as x:
            sys.exit(f"pm-kb: no se puede escuchar en {host}:{puerto} ({x.strerror}). ¿Ya hay un `pm-kb servir` en marcha? "
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
            t = crear_token(a, "sesión local (servir)", "*", True)
            a.close()
            print(f"pm-kb {VERSION}: abrí http://{'localhost' if host in ('127.0.0.1', '::1') else host}:{puerto}/ingresar?token={t}\n"
                  "  (enlace de esta sesión: el token anterior de la sesión local queda revocado)", flush=True)
        except Exception as x:
            print(f"pm-kb: sin token de sesión local ({str(x)[:120]}); crear uno con `pm-kb token crear`", flush=True)
    else:
        print(f"pm-kb {VERSION}: escuchando en {host}:{puerto}; ingresar con un token personal (`pm-kb token crear`). "
              "Fuera de una red de confianza, poner delante un proxy con TLS.", flush=True)
    uvicorn.run(crear_app(), host=host, port=puerto, log_level="warning", proxy_headers=False, server_header=False)
