"""Nivel «opcionales» de la suite de variantes: el portal de pm-kb con los demás componentes (docs/PRUEBAS.md §2.5;
docs/PM-KB.md §11.5 a §11.8). Solo la interacción: lo que el portal hace por sí solo (rutas, CSP, sesiones, límites,
RLS, pantallas) lo cubren pm-kb/pruebas/probar_kb.py --con-base y pantallas.py, que corren en la unidad kb-pruebas.

Unidad kb-portal (proyecto de la guía E2E-1, `portal-socios` con BMAD 6.12.4 real, más un proyecto en inglés):
  historial   las instantáneas que congela pm-method al decidir cada puerta (`estado.py puerta`) son las que publica el
              índice, en el mismo orden y con la misma decisión que `tablero.py listar`; decidir otra puerta en la copia
              suma la instantánea del estado previo a la decisión, igual al archivo de la carpeta
  actualizar  «actualizar ahora» con la carpeta montada en solo lectura para el servicio (root con `unshare`; si no, la
              misma prueba sin montaje): toma la puerta y las propuestas escritas por pm-method sin crear ni cambiar nada
              en la carpeta (los mismos archivos con la misma huella y ninguna carpeta nueva, tampoco un bloqueo)
  propuestas  `registro.py proponer` → sombra punteada en Entrega (alta y cambio con la marca en la tarjeta objetivo);
              su ficha después de reindexar (con el tablero regenerado sin reindexar, 404: nota, docs/PM-KB.md §15);
              `registro.py aprobar` → la sombra se va y queda la fila
  compartir   enlaces por actor y por instantánea con los actores de la RACI real: el tablero del enlace coincide con
              `tablero.py generar --actor` del núcleo; ficha de una tarjeta propia sí y de otra no; otro proyecto,
              buscar, preguntar y MCP rechazados; revocación y vencimiento cortan la sesión abierta
  inglés      proyecto nuevo con idioma en: instantánea de la puerta rechazada con etiqueta y HTML en inglés, sombras
              en inglés, enlace compartido; sirve además de «otro proyecto» para el aislamiento
  enlaces     mover un artefacto y un documento en la copia → `pm-kb enlaces` sugiere el comando de pm-method; ejecutarlo
              (estado.py artefacto) y reindexar deja el artefacto sin aviso, la ficha por id en la ruta nueva y la
              tarjeta del tablero con la fuente encontrada
  BMAD        _bmad/ y _bmad-output/ intactos tras todo lo anterior; ficha por id del PRD aprobado de BMAD (bmad-prd) y
              nada de _bmad/ en Documentos
Puertos: los de opcionales.puerto_libre (8820–8899). La URL de un enlace compartido (con su token) no se anota en el
registro de comandos.

documentos_externos(): llamada desde la unidad «externas» (opcionales.py) con las salidas reales de diagram-design,
archify y visual-explainer que dejó el contenedor: el portal las lista con su motor y las sirve con la CSP aislada;
pm-kb corre en el anfitrión con el código de esta copia (no el de la imagen).
"""
import json, os, re, shlex, shutil, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from comun import RAIZ, Ejecutor, escribir, huella   # noqa: E402
from opcionales import (EST, INICIO_MCP, LANZ, env_kb, foto, kb_disponible, kb_ej, llamada, proyecto_e2e, puerto_libre,  # noqa: E402
                        quitar, revocar, sql_admin, token)

POR = "Ejecutiva: Laura Méndez"


# ---------------------------------------------------------------- utilidades
def pedir(url, datos=None, cabeceras=None, metodo=None, tiempo=60):
    """(código, cabeceras, cuerpo JSON o texto)."""
    h = {"Content-Type": "application/json", **(cabeceras or {})}
    req = urllib.request.Request(url, data=json.dumps(datos).encode() if datos is not None else None, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=tiempo) as r:
            cuerpo, cod, cab = r.read(), r.status, r.headers
    except urllib.error.HTTPError as x:
        cuerpo, cod, cab = x.read(), x.code, x.headers
    t = cuerpo.decode("utf-8", "replace") if cuerpo[:4] != b"\x89PNG" else cuerpo
    try:
        return cod, cab, json.loads(t)
    except (ValueError, TypeError):
        return cod, cab, t


def arbol(raiz):
    """Carpetas y sha256 de cada archivo (para comprobar que el servicio no crea ni cambia nada, tampoco .pm-bloqueo/)."""
    out = foto(raiz)
    for d, ds, _ in os.walk(raiz):
        for n in ds: out[os.path.relpath(os.path.join(d, n), raiz) + "/"] = "carpeta"
    return out


def refs(d):
    """Refs de todas las tarjetas de un pm-tablero/1 (cualquier dict con `ref` y `enlace`)."""
    out = set()
    def rec(x):
        if isinstance(x, dict):
            if "ref" in x and "enlace" in x: out.add(x["ref"])
            for v in x.values(): rec(v)
        elif isinstance(x, list):
            for v in x: rec(v)
    rec(d)
    return out


def solo_lectura_disponible(carpeta):
    """Montar la carpeta en solo lectura para el servicio exige root y `unshare` (como pantallas.py)."""
    if os.name != "posix" or os.geteuid() != 0 or not shutil.which("unshare"):
        return False
    r = subprocess.run(["unshare", "-m", "sh", "-c", 'mount --bind "$1" "$1" && mount -o remount,bind,ro "$1" "$1" && ! touch "$1/.prueba-ro" 2>/dev/null',
                        "sh", carpeta], capture_output=True)
    return r.returncode == 0 and not os.path.exists(os.path.join(carpeta, ".prueba-ro"))


class Portal:
    """`pm-kb servir` en un puerto libre con PMKB_ORIGENES = su propia dirección; `ro` monta esa carpeta en solo lectura
    solo para el servicio (el anfitrión sigue escribiendo con pm-method)."""
    def __init__(self, reg, env, ro=None):
        self.reg, self.puerto = reg, puerto_libre()
        self.base = f"http://127.0.0.1:{self.puerto}"
        cmd = [LANZ, "servir", "--puerto", str(self.puerto)]
        if ro:
            cmd = ["unshare", "-m", "sh", "-c", 'mount --bind "$1" "$1" && mount -o remount,bind,ro "$1" "$1" && shift && exec "$@"', "sh", ro] + cmd
        self.p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=dict(env, PMKB_ORIGENES=self.base))
        for _ in range(150):
            if self.p.poll() is not None: break
            try:
                if pedir(self.base + "/salud", tiempo=2)[0] == 200: return
            except OSError:
                pass
            time.sleep(0.2)
        raise RuntimeError(f"pm-kb servir no arrancó: {self.cerrar()[-300:]}")

    def api(self, ruta, token=None, cookie=None, datos=None, origen=None, metodo=None):
        h = {}
        if token: h["Authorization"] = f"Bearer {token}"
        if cookie: h["Cookie"] = f"pmkb={cookie}"
        if origen: h["Origin"] = origen
        return pedir(self.base + ruta, datos, h, metodo)

    def canjear(self, url):
        """Abre un enlace compartido como el navegador: el token del fragmento por POST /v/canje → id de la sesión."""
        tok = url.split("#", 1)[1] if "#" in url else ""
        cod, cab, j = self.api("/v/canje", datos={"token": tok}, origen=self.base)
        sid = ""
        for c in cab.get_all("Set-Cookie") or []:
            m = re.match(r"pmkb=([^;]+)", c)
            if m: sid = m.group(1)
        return cod, sid, j

    def cerrar(self):
        if self.p.poll() is None:
            self.p.terminate()
            try: self.p.wait(10)
            except subprocess.TimeoutExpired: self.p.kill()
        err = self.p.stderr.read() if self.p.stderr else ""
        self.reg.log.append({"cmd": f"pm-kb servir --puerto {self.puerto} (registro del servicio)", "cwd": "", "rc": self.p.returncode, "s": 0, "out": "", "err": err[-3000:]})
        if "Traceback (most recent call last)" in err:
            self.reg.trazas.append({"paso": "pm-kb servir", "comando": "pm-kb servir", "cola": err[-600:]})
            self.reg.check("pm-kb servir: sin traza de Python en su registro", False, err[-400:])
        return err


def compartir(reg, env, *args, paso=""):
    """`pm-kb compartir crear …` → (id, url). La URL (con el token) no se anota en el registro de comandos."""
    r = subprocess.run([LANZ, "compartir", "crear", *args], capture_output=True, text=True, env=env, timeout=120)
    lineas = r.stdout.strip().splitlines()
    m = re.search(r"Enlace (e-[0-9a-f]{8})", r.stdout)
    reg.log.append({"cmd": f"pm-kb compartir crear {' '.join(args)} ({paso})", "cwd": "", "rc": r.returncode, "s": 0,
                    "out": "\n".join(lineas[:-1])[-2000:], "err": r.stderr[-1500:]})
    if r.returncode != 0 or not m or not lineas or "/v#" not in lineas[-1]:
        reg.check(f"{paso}: pm-kb compartir crear terminó con el enlace", False, (r.stderr or r.stdout)[-300:].replace(lineas[-1] if lineas else "\0", "<url>"))
        return "", ""
    return m.group(1), lineas[-1].strip()


def instantaneas_nucleo(x, gestion):
    r = x(os.path.join(EST, "tablero.py"), "--proyecto", gestion, "listar", "--json", paso="tablero.py listar --json")
    return r.json() or []


# ---------------------------------------------------------------- unidad kb-portal
def kb_portal(trabajo, reg, cache):
    if not kb_disponible(reg): return
    repo = proyecto_e2e(cache, os.path.join(trabajo, "portal-socios"))
    G = os.path.join(repo, "gestion")
    en = os.path.join(trabajo, "member-portal")
    P, PE = "zz-opc-portal", "zz-opc-portal-en"
    persona = "zz-opc portal"
    x = Ejecutor(reg, sys.executable, cwd=repo)
    xe = Ejecutor(reg, sys.executable, cwd=en)
    kb = lambda *a, ok=(0,), paso="": kb_ej(reg)(*a, ok=ok, paso=paso)
    bmad0 = huella(repo, ("_bmad", "_bmad-output"))
    s = None
    try:
        # 1 · historial: las instantáneas de las puertas de E2E-1 publicadas tal cual las congeló pm-method
        r = kb("indexar", "--proyecto", P, "--ruta", repo, "--sin-vectores", paso="indexar E2E-1")
        nuc = instantaneas_nucleo(x, G)
        m = re.search(r"tablero de .* publicado · versión \d+ .*· (\d+) instantánea", r.out)
        reg.check("indexar publica el tablero con tantas instantáneas como congeló pm-method en las puertas de E2E-1 (tablero.py listar)",
                  m and nuc and int(m.group(1)) == len(nuc) and all(i["tipo"] == "puerta" for i in nuc), [m and m.group(0), len(nuc)])

        # 2 · proyecto en inglés: puerta rechazada (congela «stage 0»), propuesta en inglés, indexado como otro proyecto
        os.makedirs(en, exist_ok=True)
        xe("nuevo", "--ruta", "gestion", "--nombre", "Member portal", "--idioma", "en", "--enfoque", "hibrido", "--ejecutivo", "Laura Mendez",
           "--gestor", "Martin Suarez", "--fecha", "2026-10-01", paso="nuevo_proyecto --idioma en")
        xe("estado", "--proyecto", "gestion", "puerta", "autorizar-inicio", "--decision", "rechazado", "--por", "Executive: Laura Mendez",
           "--fecha", "2026-10-02", "--motivo", "no mandate yet", paso="puerta autorizar-inicio rechazada (en)")
        xe("registro", "--proyecto", "gestion", "proponer", "acciones", "--campo", "descripcion=Draft the project mandate with the sponsor",
           "--campo", "responsable=Martin Suarez", "--por", "agent: pm-inicio", paso="registro.py proponer acciones (en)")
        kb("indexar", "--proyecto", PE, "--ruta", en, "--sin-vectores", paso="indexar el proyecto en inglés")

        # 3 · servicio con la carpeta de E2E-1 en solo lectura; token personal de los dos proyectos
        ro = solo_lectura_disponible(repo)
        if not ro:
            reg.notas.append("kb-portal: sin root o sin `unshare`, «actualizar ahora» corre sin montar la carpeta en solo lectura (se comprueba igual que no escribe)")
        tok = token(env_kb(), persona, f"{P},{PE}")
        s = Portal(reg, env_kb(), ro=repo if ro else None)
        cod, _, h0 = s.api(f"/api/tablero/historial?proyecto={P}", tok)
        ids0 = [i["id"] for i in (h0 or {}).get("instantaneas", [])] if cod == 200 else []
        reg.check("historial del portal = instantáneas del núcleo, en orden y con la misma puerta, etapa y decisión",
                  ids0 == [i["id"] for i in nuc] and [(i["puerta"], i["etapa"], i["decision"], i["decision_id"]) for i in h0["instantaneas"]]
                  == [(i["puerta"], i["etapa"], i["decision"], i["decision_id"]) for i in nuc], [cod, ids0, [i["id"] for i in nuc]])
        cod, _, t0 = s.api(f"/api/tablero?proyecto={P}", tok)
        v0 = (t0 or {}).get("version") if cod == 200 else None

        # 4 · pm-method escribe (en el anfitrión): otra puerta y dos propuestas; el servicio solo lee
        x("estado", "--proyecto", "gestion", "puerta", "autorizar-etapa", "--decision", "condicionado", "--condiciones", "cerrar los hallazgos de la verificación",
          "--por", POR, "--fecha", "2027-03-10", paso="puerta autorizar-etapa condicionada (congela el tablero previo)")
        r = x("registro", "--proyecto", "gestion", "proponer", "acciones", "--campo", "descripcion=Revisar el contrato de soporte del proveedor de SMS",
              "--campo", "responsable=Martín Suárez", "--campo", "fecha_compromiso=2027-04-01", "--por", "agente: pm-riesgos", paso="registro.py proponer acciones")
        p_alta = (re.findall(r"\bP-\d{3}\b", r.out) or [""])[0]
        r = x("registro", "--proyecto", "gestion", "proponer", "cambios", "C-001", "--campo", "estado=implementado", "--por", "agente: pm-cambios",
              "--motivo", "las respuestas ya están financiadas", paso="registro.py proponer cambios C-001")
        p_cambio = (re.findall(r"\bP-\d{3}\b", r.out) or [""])[0]
        nuc1 = instantaneas_nucleo(x, G)
        nueva = nuc1[-1] if len(nuc1) == len(nuc) + 1 else {}
        antes = arbol(repo)
        cod, _, ac = s.api("/api/tablero/actualizar", tok, datos={"proyecto": P}, origen=s.base)
        reg.check("«actualizar ahora» (token personal, Origin del portal" + (", carpeta en solo lectura para el servicio" if ro else "")
                  + "): 200, versión nueva y una instantánea más", cod == 200 and ac.get("cambio") and ac.get("version", 0) > (v0 or 0)
                  and ac.get("instantaneas") == len(nuc) + 1, [cod, ac])
        despues = arbol(repo)
        reg.check("«actualizar ahora» no escribe en la carpeta del proyecto: los mismos archivos con la misma huella y ninguna carpeta nueva (tampoco un bloqueo)",
                  despues == antes, sorted(k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k))[:10])
        cod, _, h1 = s.api(f"/api/tablero/historial?proyecto={P}", tok)
        ult = (h1 or {}).get("instantaneas", [{}])[-1] if cod == 200 else {}
        cod2, _, ti = s.api(f"/api/tablero?proyecto={P}&instantanea={nueva.get('id', '-')}", tok)
        arch = json.load(open(os.path.join(G, nueva["archivo"]), encoding="utf-8")) if nueva else None
        reg.check("la puerta decidida con estado.py aparece en el historial del portal (autorizar-etapa · etapa 2 · condicionado) y su instantánea "
                  "es el archivo congelado, con el estado previo a la decisión",
                  nueva and ult.get("id") == nueva["id"] and (ult.get("puerta"), ult.get("etapa"), ult.get("decision")) == ("autorizar-etapa", 2, "condicionado")
                  and cod2 == 200 and ti.get("datos") == arch and arch["ciclo"]["etapa"] == 2 and arch["instantanea"]["decision"] == "condicionado",
                  [nueva.get("id"), ult, cod2, (arch or {}).get("instantanea")])

        # 5 · propuestas pendientes: sombras en Entrega
        cod, _, t1 = s.api(f"/api/tablero?proyecto={P}", tok)
        ctl = ((t1 or {}).get("datos") or {}).get("entrega", {}).get("control", {})
        sa = [z for z in ctl.get("acciones", {}).get("propuestas", []) if z["ref"] == p_alta]
        sc = [z for z in ctl.get("cambios", {}).get("propuestas", []) if z["ref"] == p_cambio]
        c001 = [z for z in ctl.get("cambios", {}).get("tarjetas", []) if z["ref"] == "C-001"]
        reg.check(f"propuestas pendientes como sombra: {p_alta} (alta en acciones, columna «abierta») y {p_cambio} (cambio de C-001, columna «implementado»), "
                  "con «espera aprobación» y la marca en la tarjeta C-001",
                  p_alta and p_cambio and sa and sc and sa[0]["tipo"] == "propuesta" and sa[0]["columna"] == "abierta" and sc[0]["columna"] == "implementado"
                  and "espera aprobación" in sc[0]["descripcion"] and c001 and "propuesta-pendiente" in c001[0]["senales"], [sa, sc, c001])
        cod0, _, _ = s.api(f"/api/ficha?proyecto={P}&id={p_alta}", tok)
        kb("indexar", "--proyecto", P, "--ruta", repo, "--sin-vectores", paso="reindexar (lo que hace vigilar ante el cambio)")
        cod, _, fp = s.api(f"/api/ficha?proyecto={P}&id={p_alta}", tok)
        if cod0 != 200:
            reg.notas.append(f"kb-portal: con el tablero regenerado sin reindexar, la ficha de una tarjeta nueva ({p_alta}) respondió {cod0} hasta la "
                             "indexación siguiente (docs/PM-KB.md §15)")
        reg.check(f"ficha de la sombra {p_alta} después de reindexar (lo que hace vigilar): por id, con la propuesta de 03-control/propuestas/",
                  cod == 200 and f"propuestas/{p_alta}.json" in json.dumps(fp, ensure_ascii=False), [cod0, cod, str(fp)[:200]])
        completo = refs((t1 or {}).get("datos") or {})
        r = x("registro", "--proyecto", "gestion", "aprobar", p_alta, "--por", POR, paso=f"registro.py aprobar {p_alta}")
        nueva_a = (re.findall(r"\bA-\d{3}\b", r.out) or [""])[-1]
        kb("tablero", "--proyecto", P, paso="pm-kb tablero tras aprobar")
        cod, _, t2 = s.api(f"/api/tablero?proyecto={P}", tok)
        acc = ((t2 or {}).get("datos") or {}).get("entrega", {}).get("control", {}).get("acciones", {})
        reg.check(f"registro.py aprobar {p_alta} → la sombra se va y la fila {nueva_a or 'A-###'} queda en la columna «abierta»",
                  nueva_a and not [z for z in acc.get("propuestas", []) if z["ref"] == p_alta]
                  and [z for z in acc.get("tarjetas", []) if z["ref"] == nueva_a and z["columna"] == "abierta"], [nueva_a, acc.get("propuestas"), [z["ref"] for z in acc.get("tarjetas", [])]])

        # 6 · compartir: por actor (RACI real de E2E-1) y por instantánea
        actor = "Diego Ferreira"
        ra = x(os.path.join(EST, "tablero.py"), "--proyecto", G, "generar", "--json", "--actor", actor, paso="tablero.py generar --actor")
        nucleo_actor = ra.json() or {}
        eid_a, url_a = compartir(reg, env_kb(PMKB_ORIGENES=s.base), "--proyecto", P, "--actor", actor, "--para", "Proveedor", paso="enlace por actor")
        cod, sid_a, cj = s.canjear(url_a) if url_a else (0, "", {})
        cod_t, _, ta = s.api(f"/api/tablero?proyecto={P}", cookie=sid_a)
        datos_a = (ta or {}).get("datos") or {}
        propias, ajenas = refs(datos_a), sorted(completo - refs(datos_a) - refs(nucleo_actor))
        reg.check(f"enlace por actor ({actor}, ST-005): el tablero compartido tiene las mismas tarjetas que `tablero.py generar --actor` del núcleo, "
                  "menos que el completo, y el bloque actor con su RACI",
                  cod == 200 and sid_a and cod_t == 200 and (datos_a.get("actor") or {}).get("nombre") == actor and propias == refs(nucleo_actor)
                  and len(propias) < len(refs((t2 or {}).get("datos") or {})) and (datos_a.get("actor") or {}).get("id") == "ST-005",
                  [cod, cod_t, datos_a.get("actor"), sorted(propias ^ refs(nucleo_actor))[:10]])
        propia = next((r_ for r_ in sorted(propias) if re.match(r"^\d+(\.\d+)*$", r_)), next(iter(sorted(propias)), ""))
        ajena = next((r_ for r_ in ajenas if re.match(r"^[CI]-\d{3}$", r_)), ajenas[0] if ajenas else "")
        c1, _, _ = s.api(f"/api/ficha?proyecto={P}&id={urllib.parse.quote(propia)}", cookie=sid_a)
        c2, _, _ = s.api(f"/api/ficha?proyecto={P}&id={urllib.parse.quote(ajena)}", cookie=sid_a)
        c2t, _, _ = s.api(f"/api/ficha?proyecto={P}&id={urllib.parse.quote(ajena)}", tok)
        c3, _, _ = s.api(f"/api/tablero?proyecto={PE}", cookie=sid_a)
        c4, _, _ = s.api(f"/api/ficha?proyecto={PE}&id=autorizar-inicio", cookie=sid_a)
        c5, _, _ = s.api(f"/api/buscar?q=proveedor&proyecto={P}", cookie=sid_a)
        c6, _, _ = s.api("/api/preguntar", cookie=sid_a, datos={"pregunta": "¿qué pasó con el proveedor de SMS?", "proyecto": P}, origen=s.base)
        c7, _, _ = s.api("/mcp", cookie=sid_a, datos=INICIO_MCP[0], origen=s.base)
        reg.check(f"aislamiento del enlace por actor: ficha de su tarjeta {propia} 200; de {ajena} (de otro actor; con el token del equipo, 200) 404; "
                  "el proyecto en inglés 404; buscar, preguntar y MCP 403",
                  propia and ajena and (c1, c2, c2t, c3, c4) == (200, 404, 200, 404, 404) and (c5, c6) == (403, 403) and c7 in (401, 403),
                  [propia, ajena, c1, c2, c2t, c3, c4, c5, c6, c7])
        prim = nuc[0]["id"] if nuc else ""
        eid_i, url_i = compartir(reg, env_kb(PMKB_ORIGENES=s.base), "--proyecto", P, "--instantanea", prim, "--para", "Junta", paso="enlace a una instantánea")
        cod, sid_i, _ = s.canjear(url_i) if url_i else (0, "", {})
        cod_t, _, tin = s.api(f"/api/tablero?proyecto={P}", cookie=sid_i)
        cod_o, _, _ = s.api(f"/api/tablero?proyecto={P}&instantanea={nueva.get('id', '-')}", cookie=sid_i)
        arch0 = json.load(open(os.path.join(G, nuc[0]["archivo"]), encoding="utf-8")) if nuc else None
        reg.check(f"enlace a la instantánea {prim} (la primera puerta de E2E-1): muestra ese archivo congelado y no otra instantánea",
                  cod == 200 and cod_t == 200 and (tin.get("instantanea") or {}).get("id") == prim and tin.get("datos") == arch0 and cod_o == 404, [cod, cod_t, cod_o])
        # revocación y vencimiento con la sesión abierta
        kb("compartir", "revocar", "--id", eid_a, paso="compartir revocar el enlace por actor")
        c_rv, _, _ = s.api(f"/api/tablero?proyecto={P}", cookie=sid_a)
        sql_admin("UPDATE pmkb.enlace SET vence = now() - interval '1 minute' WHERE id = %s", [eid_i])
        c_vn, _, _ = s.api(f"/api/tablero?proyecto={P}", cookie=sid_i)
        c_rc, _, _ = s.canjear(url_i) if url_i else (0, "", {})
        ls = kb("compartir", "listar", "--proyecto", P, "--json", paso="compartir listar").json() or []
        est = {z.get("id"): z.get("estado") for z in (ls if isinstance(ls, list) else ls.get("enlaces", []))}
        reg.check("revocar y vencer cortan la sesión abierta en la petición siguiente (401), el enlace vencido no se vuelve a canjear y `compartir listar` lo informa",
                  eid_a and eid_i and c_rv == 401 and c_vn == 401 and c_rc == 401 and est.get(eid_a) == "revocado" and est.get(eid_i) == "vencido", [c_rv, c_vn, c_rc, est])

        # 7 · proyecto en inglés en el portal
        cod, _, he = s.api(f"/api/tablero/historial?proyecto={PE}", tok)
        ie = (he or {}).get("instantaneas", [])
        cod_t, _, te = s.api(f"/api/tablero?proyecto={PE}", tok)
        de = (te or {}).get("datos") or {}
        sombra = (de.get("entrega", {}).get("control", {}).get("acciones", {}).get("propuestas") or [{}])[0]
        html_en = open(os.path.join(en, "gestion", ie[0]["archivo"][:-5] + ".html"), encoding="utf-8").read() if ie else ""
        reg.check("proyecto en inglés: tablero «en», instantánea de la puerta rechazada «autorizar-inicio · stage 0» (HTML lang=en) y la sombra «awaiting approval»",
                  cod == 200 and cod_t == 200 and de.get("idioma") == "en" and len(ie) == 1 and ie[0]["etiqueta"] == "autorizar-inicio · stage 0"
                  and ie[0]["decision"] == "rechazado" and '<html lang="en"' in html_en and "awaiting approval" in sombra.get("descripcion", ""),
                  [de.get("idioma"), [(i["etiqueta"], i["decision"]) for i in ie], sombra.get("descripcion"), html_en[:60]])
        eid_e, url_e = compartir(reg, env_kb(PMKB_ORIGENES=s.base), "--proyecto", PE, paso="enlace al proyecto en inglés")
        cod, sid_e, _ = s.canjear(url_e) if url_e else (0, "", {})
        c1, _, tbe = s.api(f"/api/tablero?proyecto={PE}", cookie=sid_e)
        c2, _, _ = s.api(f"/api/tablero?proyecto={P}", cookie=sid_e)
        reg.check("enlace del proyecto en inglés: su tablero (idioma en) y no el de E2E-1 (404)", cod == 200 and c1 == 200 and (tbe.get("datos") or {}).get("idioma") == "en" and c2 == 404, [cod, c1, c2])

        # 8 · BMAD en el portal: ficha por id del PRD aprobado y Documentos sin nada de _bmad/
        cod, _, fb = s.api(f"/api/ficha?proyecto={P}&id=bmad-prd", tok)
        cod_d, _, dd = s.api(f"/api/documentos?proyecto={P}", tok)
        fd = [z["fuente"] for z in (dd or {}).get("documentos", [])] if cod_d == 200 else []
        reg.check("BMAD en el portal: ficha por id del artefacto bmad-prd (copia aprobada del PRD de _bmad-output) con su ubicación; Documentos sin archivos de _bmad/",
                  cod == 200 and "bmad-prd-v1.0/prd.md" in json.dumps(fb, ensure_ascii=False) and cod_d == 200 and not any(f.startswith("_bmad/") for f in fd), [cod, cod_d, fd[:5]])
        s.cerrar(); s = None

        # 9 · enlaces: mover un artefacto y un documento; aplicar la acción sugerida con pm-method
        os.makedirs(os.path.join(G, "00-direccion", "caso"), exist_ok=True)
        os.rename(os.path.join(G, "00-direccion", "business-case.md"), os.path.join(G, "00-direccion", "caso", "caso-de-negocio.md"))
        os.makedirs(os.path.join(G, "03-control", "reportes", "riesgos"), exist_ok=True)
        os.rename(os.path.join(G, "03-control", "reportes", "2026-12-16-candidatos-riesgo.md"), os.path.join(G, "03-control", "reportes", "riesgos", "2026-12-16-candidatos-riesgo.md"))
        kb("indexar", "--proyecto", P, "--ruta", repo, "--sin-vectores", paso="reindexar tras mover")
        e1 = kb("enlaces", "--proyecto", P, "--json", paso="pm-kb enlaces tras mover").json() or {}
        art = next((a for a in e1.get("artefactos", []) if a["ref"] == "business-case"), {})
        movs = {(m_["ref"], m_["tipo"]) for m_ in e1.get("movimientos", [])}
        tb_m = (kb("tablero", "--proyecto", P, "--json", paso="tablero publicado con la ruta rota").json() or {})
        bc = ((tb_m.get("artefactos") or {}).get("elementos") or {}).get("business-case", {})
        reg.check("pm-kb enlaces tras mover: business-case con la ruta sugerida por huella y el comando `estado.py artefacto`, los dos movimientos "
                  "(artefacto y documento) y la tarjeta del tablero con la fuente no encontrada",
                  art.get("sugerida") == "gestion/00-direccion/caso/caso-de-negocio.md" and "estado.py" in art.get("accion", "") and " artefacto business-case " in art.get("accion", "")
                  and ("business-case", "artefacto") in movs and any(t_ == "documento" for _, t_ in movs) and bc.get("existe") is False,
                  [art, sorted(movs), {k: bc.get(k) for k in ("existe", "ruta")}])
        acc_ = shlex.split(art.get("accion", "")) if art.get("accion", "").startswith("python3 ") else []
        if acc_:
            x(*acc_[1:], paso="acción sugerida por pm-kb enlaces (estado.py artefacto)")
        kb("indexar", "--proyecto", P, "--ruta", repo, "--sin-vectores", paso="reindexar tras la corrección")
        e2 = kb("enlaces", "--proyecto", P, "--json", paso="pm-kb enlaces tras la corrección").json() or {}
        fi = kb("ficha", "business-case", "--proyecto", P, "--json", paso="ficha business-case").json() or {}
        tb_c = (kb("tablero", "--proyecto", P, "--json", paso="tablero tras la corrección").json() or {})
        bc2 = ((tb_c.get("artefactos") or {}).get("elementos") or {}).get("business-case", {})
        san = x("sanidad", "--proyecto", "gestion", "--json", ok=(0, 1), paso="sanidad tras la corrección").json() or {}
        reg.check("ejecutar la acción sugerida (estado.py artefacto) y reindexar: enlaces sin el artefacto, ficha por id en la ruta nueva, tarjeta con la fuente "
                  "encontrada y sanidad sin ART-01 de business-case",
                  acc_ and not [a for a in e2.get("artefactos", []) if a["ref"] == "business-case"] and "00-direccion/caso/caso-de-negocio.md" in json.dumps(fi, ensure_ascii=False)
                  and bc2.get("existe") is True and not [h for h in san.get("hallazgos", []) if h["codigo"] == "ART-01" and "business-case" in h["mensaje"]],
                  [e2.get("artefactos"), bc2.get("existe"), [h["mensaje"][:80] for h in san.get("hallazgos", []) if h["codigo"].startswith("ART")]])
        reg.check("BMAD intacto: ningún archivo de _bmad/ ni _bmad-output/ cambió (puertas, propuestas, índice, actualizar ahora, enlaces compartidos y movimientos)",
                  huella(repo, ("_bmad", "_bmad-output")) == bmad0)
    finally:
        if s: s.cerrar()
        revocar(env_kb(), persona)
        kb_ej(reg)("compartir", "revocar", "--proyecto", P, ok=None, paso="revocar los enlaces que queden")
        quitar(reg, P, PE)


# ---------------------------------------------------------------- documentos de las skills externas (unidad externas)
def documentos_externos(trabajo, reg, repo, presentes):
    """Las salidas reales de las skills (en `repo`, que dejó el contenedor) en la pestaña Documentos: motor, marco aislado
    (CSP con sandbox; allow-scripts solo si el HTML trae scripts), descarga y exportaciones; la fuente .src.html y las
    instantáneas del tablero no se listan. pm-kb corre en el anfitrión (el de esta copia), no dentro de la imagen."""
    if not kb_disponible(reg): return
    P, persona = "zz-opc-docs", "zz-opc documentos"
    s = None
    try:
        kb_ej(reg)("indexar", "--proyecto", P, "--ruta", repo, "--sin-vectores", paso="indexar el proyecto con los visuales de las skills")
        tok = token(env_kb(), persona, P)
        s = Portal(reg, env_kb())
        cod, _, d = s.api(f"/api/documentos?proyecto={P}", tok)
        docs = {z["fuente"]: z for z in (d or {}).get("documentos", [])} if cod == 200 else {}
        esperados = {"diagram-design": "gestion/02-planificacion/visuales/wbs-diagram-design.html", "archify": "gestion/02-planificacion/visuales/wbs-archify.html",
                     "visual-explainer": "gestion/02-planificacion/visuales/one-pager-project-brief.html"}
        esperados = {k: v for k, v in esperados.items() if k in presentes}
        reg.check(f"Documentos: las salidas reales de {', '.join(sorted(esperados))} se listan con su motor; sin la fuente .src.html ni las instantáneas del tablero",
                  esperados and all(docs.get(v, {}).get("motor") == k for k, v in esperados.items())
                  and not any(f.endswith(".src.html") or "/reportes/tableros/" in f for f in docs), {f: z.get("motor") for f, z in docs.items()})
        for motor_, fuente in sorted(esperados.items()):
            cod, cab, cuerpo = s.api(f"/archivo/{P}/{urllib.parse.quote(fuente)}", tok)
            csp = cab.get("Content-Security-Policy", "") if cab else ""
            scripts = docs.get(fuente, {}).get("scripts")
            reg.check(f"{motor_}: /archivo con la CSP aislada (sandbox{' allow-scripts' if scripts else ''}, sin red ni acceso al portal) y el contenido del archivo",
                      cod == 200 and csp.startswith("sandbox") and ("allow-scripts" in csp) == bool(scripts) and "default-src 'none'" in csp and "connect-src 'none'" in csp
                      and "allow-same-origin" not in csp and isinstance(cuerpo, str) and cuerpo == open(os.path.join(repo, fuente), encoding="utf-8").read(),
                      [cod, csp, scripts])
        if "diagram-design" in esperados:
            f = esperados["diagram-design"]
            exp = docs.get(f, {}).get("exportaciones", [])
            cod_s, cab_s, _ = s.api(f"/archivo/{P}/{urllib.parse.quote(f[:-5] + '.svg')}", tok)
            cod_d, cab_d, _ = s.api(f"/archivo/{P}/{urllib.parse.quote(f)}?descargar=1", tok)
            reg.check("diagram-design: el SVG y el PNG de export_svg.py y export_png.py se ofrecen junto al HTML; el SVG se sirve aislado y «descargar» va como adjunto",
                      sorted(os.path.basename(z) for z in exp) == ["wbs-diagram-design.png", "wbs-diagram-design.svg"] and cod_s == 200
                      and cab_s.get("Content-Security-Policy", "").startswith("sandbox") and cod_d == 200 and cab_d.get("Content-Disposition", "").startswith("attachment"),
                      [exp, cod_s, cod_d])
    finally:
        if s: s.cerrar()
        revocar(env_kb(), persona)
        quitar(reg, P)


UNIDADES = {"kb-portal": kb_portal}
