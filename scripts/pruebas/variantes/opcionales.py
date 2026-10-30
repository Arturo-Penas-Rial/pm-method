#!/usr/bin/env python3
"""Nivel «opcionales» de la suite de variantes: pm-kb con modelos (simulados), BMAD, skills externas de diagramas y su
interacción con pm-method (docs/PRUEBAS.md §2.5; docs/PM-KB.md §12). Sin red externa.

Unidades (corren en paralelo; cada una con su proyecto de pm-kb `zz-opc-*`, que se quita al terminar):
  kb-pruebas      probar_kb.py (núcleo y --con-base), pantallas.py (si el Python de la suite tiene Playwright con
                  Chromium; si no, omisión «pm-kb-pantallas») y consultas_oro.py sobre el proyecto de la guía E2E-1
                  (léxica, y con vectores simulados como nota); las cifras se leen de la salida y se comparan con las
                  registradas en docs/PM-KB.md §11.2 y §12
  kb-vectores     simulador de vectores (TEI y compatible con OpenAI) y de re-ranqueo: verificar, indexar con vectores,
                  caché en la segunda indexación, búsqueda híbrida (RRF) que trae lo que BM25 solo no trae, re-ranqueo que
                  reordena, y fallas (servidor caído o con 500) que degradan con aviso y sin traza (CLI, MCP y web)
  kb-respuesta    simulador de respuesta (API de Anthropic y compatible con OpenAI): «Preguntar» de la web con respuesta
                  citada, cita inválida, sin citas, 401, 404, sin clave, plazo vencido y sin modelo; evidencia citada por
                  `contexto` en la CLI y el MCP
  kb-pm-method    escrituras de registro.py (bitácora) y una propuesta → reindexar → historia y propuesta encontradas;
                  interesados sin contacto ni valoración confidencial; circulación restringida fuera (MCP stdio y HTTP);
                  BMAD (_bmad-output) indexado y _bmad excluido; pm-kb no escribe en el proyecto; MCP consultado como un
                  agente por JSON-RPC (stdio y HTTP)
  kb-portal       el portal con pm-method (portal.py): instantáneas de las puertas en el historial, «actualizar ahora»
                  con la carpeta en solo lectura, propuestas como sombra, enlaces compartidos por actor y por instantánea
                  con aislamiento, revocación y vencimiento, proyecto en inglés, `pm-kb enlaces` tras mover y BMAD intacto
  externas        en un contenedor `--network none` de la imagen pm-method (con el código de esta copia montado en solo
                  lectura): INS-03 con cada skill presente o ausente, contrato de delegación de pm-visuales §1.3/§1.4 con
                  diagram-design, archify y visual-explainer (salidas en 02-planificacion/visuales/, artefactos
                  registrados y reconocidos por la sanidad, BMAD intacto) y el caso DD de probar_paquete.py; después, en
                  el anfitrión, esas salidas en la pestaña Documentos del portal (motor, CSP aislada, descarga, SVG y PNG)
Proyecto de trabajo: el de la guía E2E-1 (portal-socios, copia del fixture BMAD 6.12.4 real), generado una vez por
corrida con guias_e2e/correr.py --guias 1 (sin pm-kb) y copiado a cada unidad.

Requisitos y omisiones explícitas (se informan en INFORME.md; no son fallas):
  pm-kb           lanzador pm-kb/pm-kb con su entorno (PMKB_VENV o ~/.local/share/pm-kb/venv) y `pm-kb base estado` sin
                  error (PMKB_DSN o el clúster local). Sin eso, las unidades kb-* se omiten con la clave «pm-kb».
  docker          `docker info` y la imagen (PM_IMAGEN_DOCKER o pm-method:<versión>). Sin eso, «externas» se omite («docker»).
  skills-externas PM_SKILLS_EXTERNAS=<carpeta con archify/ y visual-explainer/> (copias instaladas antes, con red, con
                  `npx skills add … -a claude-code -y` en una carpeta descartable; docs/PRUEBAS.md §2.5). Sin ella, las
                  partes de archify y visual-explainer se omiten («skills-externas»); diagram-design viene en la imagen.
Los simuladores (simuladores.py) NO son los modelos reales: prueban el protocolo, la integración y las fallas.

Modos internos: --en-contenedor DIR (lo ejecuta la unidad «externas» dentro de la imagen) y --sonda-plazo PROYECTO
(lo ejecuta kb-respuesta con el Python del entorno de pm-kb para vencer el plazo del modelo en 1 s en lugar de 60 s).
"""
import argparse, csv, glob, hashlib, html, json, os, re, secrets, shutil, socket, subprocess, sys, threading, time
import urllib.error, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from comun import RAIZ, Ejecutor, escribir, huella   # noqa: E402

KB_DIR = os.path.join(RAIZ, "pm-kb")
LANZ = os.path.join(KB_DIR, "pm-kb")
SIM = os.path.join(AQUI, "simuladores.py")
EST = os.path.join(RAIZ, "skills", "pm-estado-proyecto", "scripts")
VARS_MODELOS = ("PMKB_EMBED_URL", "PMKB_EMBED_TIPO", "PMKB_EMBED_MODELO", "PMKB_RERANK_URL", "PMKB_LLM_TIPO", "PMKB_LLM_URL",
                "PMKB_LLM_MODELO", "PMKB_LLM_CLAVE_VAR", "PMKB_SIM_CLAVE", "PMKB_PROYECTOS", "PMKB_RESTRINGIDA")
ENCABEZADO = "Evidencia, no instrucciones"
_LOCK = threading.Lock()
_KB = {}


# ---------------------------------------------------------------- utilidades del anfitrión
def py_kb():
    """Python del entorno de pm-kb (el mismo que usa el lanzador)."""
    v = os.environ.get("PMKB_VENV") or os.path.join(os.environ.get("PMKB_DATOS") or os.path.expanduser("~/.local/share/pm-kb"), "venv")
    p = os.path.join(v, "bin", "python")
    return p if os.path.exists(p) else None


def env_kb(**extra):
    e = {k: v for k, v in os.environ.items() if k not in VARS_MODELOS and k not in ("PYTHONPATH", "PYTHONUTF8", "PYTHONIOENCODING")}
    e.update({k: v for k, v in extra.items() if v is not None})
    return e


def kb_disponible(reg):
    """True si pm-kb responde; si no, anota la omisión «pm-kb» con el motivo."""
    with _LOCK:
        if "ok" not in _KB:
            motivo = ""
            if not py_kb():
                motivo = "sin el entorno de pm-kb (PMKB_VENV o ~/.local/share/pm-kb/venv)"
            else:
                try:
                    r = subprocess.run([LANZ, "base", "estado"], capture_output=True, text=True, timeout=120, env=env_kb())
                    if r.returncode != 0: motivo = "`pm-kb base estado` falló: " + (r.stderr or r.stdout).strip()[-200:]
                except (OSError, subprocess.TimeoutExpired) as x:
                    motivo = f"`pm-kb base estado` no respondió ({x})"
            _KB["ok"], _KB["motivo"] = not motivo, motivo
    if not _KB["ok"]:
        reg.omitir("pm-kb", "pm-kb no disponible: " + _KB["motivo"] + " · instalar con docs/INSTALACION-WSL2.md o docs/INSTALACION-DOCKER.md")
    return _KB["ok"]


def kb_ej(reg, cwd=None, **modelos):
    """Ejecutor del lanzador de pm-kb con las variables de modelos exactas (las del entorno se quitan)."""
    x = Ejecutor(reg, "bash", cwd=cwd)          # bash pm-kb/pm-kb …: el subcomando nunca se confunde con un script de comun.SCR
    x.env = env_kb(**modelos)
    return lambda *a, **k: x(LANZ, *a, **k)


_PUERTOS = set()


def puerto_libre():
    """Puerto libre de 127.0.0.1 entre 8820 y 8899 (rango de las pruebas de pm-kb: probar_kb.py y pantallas.py toman el
    primero libre desde 8800), sin repetir uno ya entregado a otra unidad de la misma corrida."""
    import random
    with _LOCK:
        if len(_PUERTOS) > 60: _PUERTOS.clear()
        for x in random.sample(range(8820, 8900), 80):
            if x in _PUERTOS: continue
            with socket.socket() as s:
                try: s.bind(("127.0.0.1", x))
                except OSError: continue
            _PUERTOS.add(x); return x
    raise RuntimeError("no hay un puerto libre entre 8820 y 8899")


def http(url, datos=None, cabeceras=None, metodo=None, tiempo=30):
    """(código, cuerpo JSON o texto)."""
    h = {"Content-Type": "application/json", **(cabeceras or {})}
    req = urllib.request.Request(url, data=json.dumps(datos).encode() if datos is not None else None, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=tiempo) as r:
            cuerpo, cod = r.read().decode("utf-8", "replace"), r.status
    except urllib.error.HTTPError as x:
        cuerpo, cod = x.read().decode("utf-8", "replace"), x.code
    try:
        return cod, json.loads(cuerpo)
    except ValueError:
        return cod, cuerpo


class Simulador:
    """simuladores.py en un proceso aparte; la clave esperada viaja solo por el entorno."""
    def __init__(self, clave="", retardo=4):
        self.p = subprocess.Popen([sys.executable, SIM, "--puerto", "0", "--retardo", str(retardo)], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, env=dict(os.environ, PMKB_SIM_CLAVE=clave))
        linea = self.p.stdout.readline()
        if not linea.startswith("SIMULADOR "):
            self.cerrar(); raise RuntimeError("el simulador no arrancó: " + (linea + (self.p.stderr.read() or ""))[-300:])
        self.url = linea.split()[1]

    def registro(self):
        return http(self.url + "/registro")[1]

    def limpiar(self):
        http(self.url + "/registro", metodo="DELETE")

    def cerrar(self):
        if self.p.poll() is None:
            self.p.terminate()
            try: self.p.wait(10)
            except subprocess.TimeoutExpired: self.p.kill()


class Servicio:
    """`pm-kb servir` en un puerto libre de 127.0.0.1. El enlace de la sesión (con token) no se anota en ningún registro."""
    def __init__(self, reg, env):
        self.reg, self.puerto = reg, puerto_libre()
        self.base = f"http://127.0.0.1:{self.puerto}"
        self.p = subprocess.Popen([LANZ, "servir", "--puerto", str(self.puerto)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env)
        for _ in range(150):
            if self.p.poll() is not None: break
            try:
                if http(self.base + "/salud", tiempo=2)[0] == 200: return
            except OSError:
                pass
            time.sleep(0.2)
        err = self.cerrar()
        raise RuntimeError(f"pm-kb servir no arrancó: {err[-300:]}")

    def pedir(self, ruta, token=None, datos=None, origen=None):
        h = {}
        if token: h["Authorization"] = f"Bearer {token}"
        if origen: h["Origin"] = origen
        return http(self.base + ruta, datos, h)

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


def token(env, persona, proyectos, restringida=False):
    """Token personal de un día; se devuelve sin anotarlo en el registro de comandos."""
    r = subprocess.run([LANZ, "token", "crear", "--persona", persona, "--proyectos", proyectos, "--dias", "1"] + (["--restringida"] if restringida else []),
                       capture_output=True, text=True, env=env, timeout=120)
    t = (r.stdout.strip().splitlines() or [""])[-1].strip()
    if r.returncode != 0 or not t.startswith("pmkb_"):
        raise RuntimeError("pm-kb token crear falló: " + r.stderr[-200:])
    return t


def revocar(env, persona):
    subprocess.run([LANZ, "token", "revocar", "--persona", persona], capture_output=True, text=True, env=env, timeout=120)


def mcp_stdio(reg, env, mensajes, paso):
    """Sesión JSON-RPC por stdio con `pm-kb mcp`: respuestas en orden, y si alguna línea de stdout no es JSON-RPC."""
    r = subprocess.run([LANZ, "mcp"], input="\n".join(json.dumps(m, ensure_ascii=False) for m in mensajes) + "\n",
                       capture_output=True, text=True, env=env, timeout=120)
    reg.log.append({"cmd": f"pm-kb mcp ({paso})", "cwd": "", "rc": r.returncode, "s": 0, "out": r.stdout[-4000:], "err": r.stderr[-2000:]})
    resp, ajenas = [], []
    for l in r.stdout.splitlines():
        if not l.strip(): continue
        try: resp.append(json.loads(l))
        except ValueError: ajenas.append(l)
    if "Traceback (most recent call last)" in r.stderr:
        reg.trazas.append({"paso": paso, "comando": "pm-kb mcp", "cola": r.stderr[-600:]})
        reg.check(f"{paso}: sin traza de Python", False, r.stderr[-400:])
    return resp, ajenas


def llamada(i, nombre, argumentos):
    return {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": nombre, "arguments": argumentos}}


INICIO_MCP = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                                                             "clientInfo": {"name": "suite-variantes", "version": "1"}}},
              {"jsonrpc": "2.0", "method": "notifications/initialized"}]


def texto_mcp(r):
    try: return r["result"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError): return ""


def sql_admin(sql, params):
    """Una sentencia con la conexión del dueño del índice (Python del entorno de pm-kb)."""
    subprocess.run([py_kb(), "-c", "import sys, json; sys.path.insert(0, sys.argv[1]); from pmkb import config; "
                    "config.conectar().execute(sys.argv[2], json.loads(sys.argv[3]))", KB_DIR, sql, json.dumps(params)],
                   capture_output=True, text=True, env=env_kb(), timeout=120)


def sql_valor(sql, params):
    """Primer valor de una consulta con la conexión del dueño del índice (Python del entorno de pm-kb); None si falla."""
    r = subprocess.run([py_kb(), "-c", "import sys, json; sys.path.insert(0, sys.argv[1]); from pmkb import config; "
                        "f = config.conectar().execute(sys.argv[2], json.loads(sys.argv[3])).fetchone(); print(json.dumps(f[0] if f else None))",
                        KB_DIR, sql, json.dumps(params)], capture_output=True, text=True, env=env_kb(), timeout=120)
    try: return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError): return None


def quitar(reg, *proyectos):
    for p in proyectos:
        kb_ej(reg)("quitar", "--proyecto", p, ok=None, paso=f"quitar {p}")


_G1 = threading.Lock()


def proyecto_e2e(cache, destino):
    """Copia del proyecto de la guía E2E-1 (portal-socios con BMAD 6.12.4 real); se genera una vez por corrida, sin pm-kb."""
    with _G1:
        base = os.path.join(cache, "opcionales-g1", "portal-socios")
        if not os.path.isdir(base):
            tmp = os.path.join(cache, "opcionales-g1-tmp"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
            env = dict(os.environ, PMKB_LANZADOR=os.path.join(tmp, "sin-pm-kb"), TMPDIR=tmp)
            r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "pruebas", "guias_e2e", "correr.py"), "--guias", "1",
                                "--salida", os.path.join(tmp, "salida"), "--conservar"], capture_output=True, text=True, env=env, timeout=1800, cwd=RAIZ)
            cands = glob.glob(os.path.join(tmp, "e2e-corrida-*", "*", "portal-socios"))
            if r.returncode != 0 or not cands:
                raise RuntimeError("guias_e2e/correr.py --guias 1 no generó el proyecto: " + (r.stdout + r.stderr)[-400:])
            os.makedirs(os.path.dirname(base), exist_ok=True)
            shutil.move(cands[0], base); shutil.rmtree(tmp, ignore_errors=True)
    if os.path.exists(destino): shutil.rmtree(destino)
    shutil.copytree(base, destino, symlinks=True)
    return destino


def foto(raiz):
    """sha256 de cada archivo de la carpeta (para comprobar que pm-kb no escribe en el proyecto)."""
    out = {}
    for d, _, fs in os.walk(raiz):
        for f in fs:
            p = os.path.join(d, f)
            with open(p, "rb") as fh: out[os.path.relpath(p, raiz)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def ids(res):
    return [x["id"] for x in (res or {}).get("resultados", [])]


# ---------------------------------------------------------------- unidad kb-pruebas
PMKB_MD = os.path.join(RAIZ, "docs", "PM-KB.md")


def documentado(patron, defecto=None):
    """Cifra registrada en docs/PM-KB.md (§11.2 y §12): las comprobaciones la comparan con la salida real."""
    m = re.search(patron, open(PMKB_MD, encoding="utf-8").read())
    return m.groups() if m else defecto


def conteo(reg, r, prog, nombre, patron_doc):
    """«N OK · 0 FALLO» de una prueba de pm-kb: N se lee de la salida (el nombre de la comprobación lo muestra) y no puede
    ser menor que la cifra registrada en docs/PM-KB.md §12 (menos comprobaciones = una prueba perdida)."""
    m = re.search(prog + r": (\d+) OK · (\d+) FALLO", r.out)
    doc = documentado(patron_doc)
    ok, fallo = (int(m.group(1)), int(m.group(2))) if m else (0, -1)
    reg.check(f"{nombre}: {ok} OK · {fallo} FALLO (docs/PM-KB.md §12 registra {doc[0] if doc else '?'})",
              m and fallo == 0 and ok > 0 and doc and ok >= int(doc[0]),
              (m.group(0) if m else r.out[-300:]) + " · " + "; ".join(l for l in r.out.splitlines() if l.startswith("FALLO"))[:400])


def kb_pruebas(trabajo, reg, cache):
    if not kb_disponible(reg): return
    x = Ejecutor(reg, sys.executable)
    r = x(os.path.join(KB_DIR, "pruebas", "probar_kb.py"), paso="probar_kb.py (núcleo)")
    conteo(reg, r, "pm-kb", "probar_kb.py (núcleo, sin base)", r"python3 pm-kb/pruebas/probar_kb.py` \| `pm-kb: (\d+) OK")
    xv = Ejecutor(reg, py_kb()); xv.env = env_kb()
    r = xv(os.path.join(KB_DIR, "pruebas", "probar_kb.py"), "--con-base", paso="probar_kb.py --con-base", timeout=900)
    conteo(reg, r, "pm-kb", "probar_kb.py --con-base", r"probar_kb.py --con-base` \| `pm-kb: (\d+) OK")
    # pantallas del portal (Playwright con Chromium): las corre el Python de la suite si tiene Playwright
    pw = subprocess.run([sys.executable, "-c", "from playwright.sync_api import sync_playwright as s\nwith s() as p: p.chromium.launch().close()"],
                        capture_output=True, text=True, timeout=120)
    if pw.returncode != 0:
        reg.omitir("pm-kb-pantallas", "sin Playwright con Chromium en el Python de la suite: pm-kb/pruebas/pantallas.py se omite ("
                   + (pw.stderr.strip().splitlines() or ["?"])[-1][:120] + ")")
    else:
        xp = Ejecutor(reg, sys.executable); xp.env = env_kb()
        r = xp(os.path.join(KB_DIR, "pruebas", "pantallas.py"), "--salida", os.path.join(trabajo, "pantallas"), "--python-kb", py_kb(),
               paso="pantallas.py (portal en claro, oscuro y móvil)", timeout=900)
        conteo(reg, r, "pm-kb pantallas", "pantallas.py (portal)", r"pantallas.py \[--salida DIR\].*?\| `pm-kb pantallas: (\d+) OK")
    repo = proyecto_e2e(cache, os.path.join(trabajo, "portal-socios"))
    P, M = "zz-opc-oro", "sim-bolsa-oro"
    sim = Simulador()
    try:
        sql_admin("DELETE FROM pmkb.cache_vector WHERE modelo = %s", [M])
        emb = {"PMKB_EMBED_URL": sim.url, "PMKB_EMBED_MODELO": M}
        r = kb_ej(reg, **emb)("indexar", "--proyecto", P, "--ruta", repo, paso="indexar el proyecto de E2E-1 (con vectores simulados)")
        e1 = documentado(r"\*\*Índice de E2E-1\*\* \(`portal-socios`\): (\d+) unidades \((\d+) vigentes\), (\d+) documentos, (\d+) relaciones, (\d+) entradas de\s+historia")
        m = re.search(r"(\d+) unidades \((\d+) vigentes\) · (\d+) documentos .*· (\d+) relaciones · (\d+) entradas de historia", r.out)
        reg.check("E2E-1 indexado: unidades (vigentes), documentos, relaciones y entradas de historia = las de docs/PM-KB.md §12 ("
                  + (f"{e1[0]} ({e1[1]}), {e1[2]}, {e1[3]}, {e1[4]}" if e1 else "cifra no encontrada") + ")", m and e1 and m.groups() == e1,
                  [m.groups() if m else r.out[-300:], e1])
        oro = os.path.join(KB_DIR, "pruebas", "consultas_oro.py")
        r = xv(oro, "--proyecto", P, paso="consultas_oro.py (léxica)")
        m = re.search(r"aciertos@5 (\d+)/(\d+) · MRR@5 ([\d.]+)", r.out)
        reg.check("consultas_oro.py (búsqueda léxica): aciertos@5 14/15 y MRR@5 0.75 (docs/PM-KB.md §12)", m and m.groups() == ("14", "15", "0.75"),
                  (m.group(0) if m else r.out[-300:]) + " · " + "; ".join(l for l in r.out.splitlines() if l.startswith("Q") and " -- " in l)[:300])
        xh = Ejecutor(reg, py_kb()); xh.env = env_kb(**emb)
        r = xh(oro, "--proyecto", P, paso="consultas_oro.py (híbrida con vectores simulados)")
        m2 = re.search(r"aciertos@5 (\d+)/(\d+) · MRR@5 ([\d.]+)", r.out)
        reg.check("consultas_oro.py con vectores simulados: termina y mide (búsqueda híbrida)", bool(m2), r.out[-300:])
        if m2:
            reg.notas.append(f"consultas de oro con vectores SIMULADOS (bolsa de palabras, no bge-m3): aciertos@5 {m2.group(1)}/{m2.group(2)}, "
                             f"MRR@5 {m2.group(3)} (léxica: {m.group(1) if m else '?'}/15, {m.group(3) if m else '?'}); no mide la calidad de un modelo real")
    finally:
        quitar(reg, P); sql_admin("DELETE FROM pmkb.cache_vector WHERE modelo = %s", [M]); sim.cerrar()


# ---------------------------------------------------------------- unidad kb-vectores
def kb_vectores(trabajo, reg, cache):
    if not kb_disponible(reg): return
    repo = proyecto_e2e(cache, os.path.join(trabajo, "portal-socios"))
    P, PO, PC = "zz-opc-vec", "zz-opc-oai", "zz-opc-vec-caido"
    M, MO, MC = "sim-bolsa-vec", "sim-bolsa-oai", "sim-bolsa-caido"
    sim = Simulador()
    cerrado = f"http://127.0.0.1:{puerto_libre()}"            # nadie escucha: «no responde»
    tok, persona = None, "zz-opc vectores"
    try:
        sql_admin("DELETE FROM pmkb.cache_vector WHERE modelo = ANY(%s)", [[M, MO, MC]])
        emb = {"PMKB_EMBED_URL": sim.url, "PMKB_EMBED_MODELO": M}
        kb = lambda *a, ok=(0,), paso="", **mod: kb_ej(reg, **mod)(*a, ok=ok, paso=paso)
        # verificar
        r = kb("verificar", paso="verificar con el simulador de vectores", **emb)
        reg.check("pm-kb verificar: «modelo de vectores» OK con dimensión 256 y verificación completa sin fallos",
                  re.search(r"OK +modelo de vectores · .* · dimensión 256", r.out) and "completa sin fallos" in r.out, r.out[-400:])
        r = kb("verificar", ok=(1,), paso="verificar con el servidor de vectores caído", PMKB_EMBED_URL=cerrado, PMKB_EMBED_MODELO=M)
        reg.check("pm-kb verificar con el servidor de vectores caído: FALLO «modelo de vectores … no responde», código 1, sin traza",
                  re.search(r"FALLO modelo de vectores · .*no responde", r.out) and r.rc == 1, r.out[-400:])
        # indexar con vectores (TEI) y caché
        sim.limpiar()
        r = kb("indexar", "--proyecto", P, "--ruta", repo, paso="indexar con vectores (TEI simulado)", **emb)
        calc, vig = re.search(r"calculando (\d+) vectores", r.out), re.search(r"\((\d+) vigentes\)", r.out)
        distintos = sql_valor("SELECT count(DISTINCT sha) FROM pmkb.unidad WHERE proyecto = %s AND vigente", [P])
        reg.check("indexar con vectores: calcula un vector por texto distinto de las unidades vigentes (las repetidas comparten el de la caché) y lo informa (vectores: sim-bolsa-vec)",
                  calc and vig and distintos and int(calc.group(1)) == distintos <= int(vig.group(1)) and f"vectores: {M}" in r.out,
                  [r.out[-300:], distintos])
        llam = [z for z in sim.registro() if z["ruta"] == "/embed"]
        reg.check("protocolo TEI: POST /embed con {inputs, truncate} en lotes de 32 como máximo, tantos textos como vectores calculados",
                  llam and all(z["claves"] == ["inputs", "truncate"] and z["n"] <= 32 for z in llam)
                  and calc and sum(z["n"] for z in llam) == int(calc.group(1)), [sum(z["n"] for z in llam), calc and calc.group(1)])
        sim.limpiar()
        r = kb("indexar", "--proyecto", P, "--ruta", repo, paso="segunda indexación (caché de vectores)", **emb)
        reg.check("segunda indexación: reutiliza la caché (sin «calculando», ninguna llamada a /embed) y conserva los vectores",
                  "calculando" not in r.out and f"vectores: {M}" in r.out and not [z for z in sim.registro() if z["ruta"] == "/embed"], r.out[-300:])
        r = kb("estado", paso="estado del índice con vectores")
        reg.check("pm-kb estado: el proyecto figura con «vectores: sim-bolsa-vec»", re.search(rf"(?m)^  {P}: .*vectores: {M}", r.out), r.out[-400:])
        # búsqueda híbrida
        q = "texting outage"
        lex = kb("buscar", q, "--proyecto", P, "--k", "5", "--json", paso="buscar sin vectores (BM25)").json() or {}
        hib = kb("buscar", q, "--proyecto", P, "--k", "5", "--json", paso="buscar con vectores (híbrida)", **emb).json() or {}
        nuevos = [x for x in hib.get("resultados", []) if x["id"] not in ids(lex)]
        reg.check("búsqueda híbrida: el modo lo dice («híbrida», modelo sim-bolsa-vec) y BM25 solo no lo dice",
                  hib.get("modo") == "híbrida" and hib.get("modelo") == M and lex.get("modo") == "léxica (BM25)", [hib.get("modo"), lex.get("modo")])
        reg.check("búsqueda híbrida: con una consulta sin términos del corpus («texting outage») trae por semántica lo que BM25 solo no trae (R-003, SMS)",
                  nuevos and all(x["por_que"] == "semántica" for x in nuevos)
                  and any("R-003" in x["titulo"] + x["extracto"] or "sms" in (x["titulo"] + x["extracto"]).lower() for x in nuevos),
                  [(x["id"], x["por_que"]) for x in hib.get("resultados", [])] + ["léxica:"] + ids(lex))
        h2 = kb("buscar", "proveedor de SMS", "--proyecto", P, "--k", "5", "--json", paso="híbrida con términos del corpus", **emb).json() or {}
        reg.check("búsqueda híbrida con términos del corpus: RRF conserva R-003 entre los 3 primeros", "R-003" in ids(h2)[:3], ids(h2))
        # vectores compatibles con OpenAI
        sim.limpiar()
        embo = {"PMKB_EMBED_URL": sim.url + "/v1", "PMKB_EMBED_TIPO": "openai", "PMKB_EMBED_MODELO": MO}
        r = kb("indexar", "--proyecto", PO, "--ruta", repo, paso="indexar con vectores compatibles con OpenAI", **embo)
        llam = [z for z in sim.registro() if z["ruta"] == "/v1/embeddings"]
        ho = kb("buscar", q, "--proyecto", PO, "--k", "3", "--json", paso="híbrida con vectores compatibles con OpenAI", **embo).json() or {}
        reg.check("vectores compatibles con OpenAI: POST /v1/embeddings con {input, model}, índice con sim-bolsa-oai y búsqueda híbrida",
                  f"vectores: {MO}" in r.out and llam and all(z["claves"] == ["input", "model"] and z["modelo"] == MO for z in llam)
                  and ho.get("modo") == "híbrida" and ho.get("resultados"), [r.out[-200:], llam[:1], ho.get("modo")])
        # fallas del servidor de vectores en la búsqueda (CLI, MCP y web)
        for nombre, url in (("caído", cerrado), ("con error 500", sim.url + "/falla")):
            b = kb("buscar", "proveedor de SMS", "--proyecto", P, "--json", paso=f"buscar con el servidor de vectores {nombre}",
                   PMKB_EMBED_URL=url, PMKB_EMBED_MODELO=M).json() or {}
            reg.check(f"servidor de vectores {nombre} en la búsqueda (CLI): sin traza, búsqueda léxica con aviso y resultados",
                      b.get("modo") == "léxica (BM25)" and any("modelo de vectores no respondió" in a for a in b.get("avisos", [])) and "R-003" in ids(b),
                      [b.get("modo"), b.get("avisos"), ids(b)])
        resp, ajenas = mcp_stdio(reg, env_kb(PMKB_EMBED_URL=cerrado, PMKB_EMBED_MODELO=M, PMKB_PROYECTOS=P),
                                 INICIO_MCP + [llamada(2, "buscar", {"consulta": "proveedor de SMS", "proyecto": P})], "MCP stdio con vectores caídos")
        t = texto_mcp(resp[-1]) if resp else ""
        reg.check("servidor de vectores caído en el MCP (stdio): `buscar` responde sin isError, léxica y con el aviso",
                  resp and not resp[-1]["result"]["isError"] and "búsqueda léxica (BM25)" in t and "no respondió" in t and not ajenas, t[:300])
        tok = token(env_kb(), persona, P)
        s = Servicio(reg, env_kb(PMKB_EMBED_URL=cerrado, PMKB_EMBED_MODELO=M))
        try:
            cod, b = s.pedir("/api/buscar?q=proveedor%20de%20SMS&proyecto=" + P, tok)
        finally:
            s.cerrar()
        reg.check("servidor de vectores caído en la web (/api/buscar): 200, léxica con aviso y resultados (antes: 500)",
                  cod == 200 and isinstance(b, dict) and b.get("modo") == "léxica (BM25)" and b.get("avisos") and b.get("resultados"),
                  [cod, b if not isinstance(b, dict) else b.get("avisos")])
        # falla al indexar
        r = kb("indexar", "--proyecto", PC, "--ruta", repo, paso="indexar con el servidor de vectores caído", PMKB_EMBED_URL=cerrado, PMKB_EMBED_MODELO=MC)
        reg.check("servidor de vectores caído al indexar: código 0, aviso, índice léxico («vectores: no») y sin traza",
                  r.rc == 0 and "aviso: el modelo de vectores no respondió" in r.out and "vectores: no" in r.out, r.out[-300:])
        b = kb("buscar", "proveedor de SMS", "--proyecto", PC, "--json", paso="buscar en el índice sin vectores con el modelo activo",
               PMKB_EMBED_URL=sim.url, PMKB_EMBED_MODELO=MC).json() or {}
        reg.check("índice sin vectores de ese modelo: la búsqueda sigue léxica sin error", b.get("modo") == "léxica (BM25)" and "R-003" in ids(b), b.get("modo"))
        # re-ranqueo
        qr = "riesgos del padrón"
        base = kb("buscar", qr, "--proyecto", P, "--k", "5", "--json", paso="híbrida sin re-ranqueo", **emb).json() or {}
        sim.limpiar()
        rr = kb("buscar", qr, "--proyecto", P, "--k", "5", "--json", paso="híbrida con re-ranqueo", PMKB_RERANK_URL=sim.url, **emb).json() or {}
        reg_rr = [z for z in sim.registro() if z["ruta"] == "/rerank"]
        punt = []
        for x in rr.get("resultados", []):
            pts = [p for t, p in (reg_rr[-1]["puntajes"] if reg_rr else []) if t.startswith(x["titulo"][:100])]
            punt.append(max(pts) if pts else None)
        reg.check("re-ranqueo: POST /rerank con {query, texts, truncate}; el modo dice «+ re-ranqueo»",
                  reg_rr and reg_rr[-1]["claves"] == ["query", "texts", "truncate"] and rr.get("modo") == "híbrida + re-ranqueo", [rr.get("modo"), reg_rr[:1]])
        reg.check("re-ranqueo: reordena (orden distinto del híbrido) y el orden final sigue el puntaje del re-ranqueador",
                  ids(rr) != ids(base) and None not in punt and punt == sorted(punt, reverse=True), [ids(base), ids(rr), punt])
        for nombre, url in (("caído", cerrado), ("con error 500", sim.url + "/falla")):
            rc_ = kb("buscar", qr, "--proyecto", P, "--k", "5", "--json", paso=f"re-ranqueo {nombre}", PMKB_RERANK_URL=url, **emb).json() or {}
            reg.check(f"re-ranqueo {nombre}: sin traza, aviso y el mismo orden que sin re-ranqueo",
                      rc_.get("modo") == "híbrida" and any("re-ranqueo no respondió" in a for a in rc_.get("avisos", [])) and ids(rc_) == ids(base),
                      [rc_.get("modo"), rc_.get("avisos"), ids(rc_)])
    finally:
        if tok: revocar(env_kb(), persona)
        quitar(reg, P, PO, PC)
        sql_admin("DELETE FROM pmkb.cache_vector WHERE modelo = ANY(%s)", [[M, MO, MC]])
        sim.cerrar()


# ---------------------------------------------------------------- unidad kb-respuesta
PREGUNTA = "¿Qué pasó con el proveedor de SMS?"


def kb_respuesta(trabajo, reg, cache):
    if not kb_disponible(reg): return
    repo = proyecto_e2e(cache, os.path.join(trabajo, "portal-socios"))
    P, persona = "zz-opc-resp", "zz-opc respuesta"
    clave = secrets.token_hex(16)                               # clave de prueba de esta corrida: solo en el entorno
    sim = Simulador(clave, retardo=4)
    tok = None
    try:
        kb_ej(reg)("indexar", "--proyecto", P, "--ruta", repo, paso="indexar (léxico)")
        tok = token(env_kb(), persona, P)
        ant = {"PMKB_LLM_TIPO": "anthropic", "PMKB_LLM_URL": sim.url, "PMKB_LLM_MODELO": "sim-respuesta",
               "PMKB_LLM_CLAVE_VAR": "PMKB_SIM_CLAVE", "PMKB_SIM_CLAVE": clave}

        def preguntar(cfg):
            sim.limpiar()
            s = Servicio(reg, env_kb(**cfg))
            try:
                return s.pedir("/api/preguntar", tok, {"pregunta": PREGUNTA, "proyecto": P})
            finally:
                s.cerrar()
        cod, d = preguntar({})
        reg.check("Preguntar sin modelo (web): evidencia numerada con cita, sin redactar",
                  cod == 200 and d.get("modo") == "evidencia (sin modelo configurado)" and d.get("fuentes") and not d.get("respuesta")
                  and all(f["cita"].startswith(P + "@") for f in d["fuentes"]), [cod, d.get("modo") if isinstance(d, dict) else d])
        cod, d = preguntar(ant)
        llam = [z for z in sim.registro() if z["ruta"] == "/v1/messages"]
        reg.check("Preguntar con el simulador de la API de Anthropic (web): respuesta citada, modo «respuesta citada (sim-respuesta)», sin avisos",
                  cod == 200 and d.get("modo") == "respuesta citada (sim-respuesta)" and "[1]" in d.get("respuesta", "") and d.get("fuentes")
                  and not d.get("avisos") and d["fuentes"][0]["titulo"][:15] in d["respuesta"], [cod, d])
        reg.check("protocolo de Anthropic: POST /v1/messages con x-api-key, anthropic-version 2023-06-01, max_tokens 900, temperature 0, system y messages",
                  llam and llam[-1]["x_api_key"] and llam[-1]["anthropic_version"] == "2023-06-01" and llam[-1]["max_tokens"] == 900
                  and llam[-1]["temperature"] == 0 and {"system", "messages", "model"} <= set(llam[-1]["claves"]), llam[-1:])
        cod, d = preguntar(dict(ant, PMKB_LLM_MODELO="sim-cita-invalida"))
        reg.check("cita inexistente: se reemplaza por [cita inválida] y se avisa «citas inexistentes quitadas: 99»",
                  "[cita inválida]" in d.get("respuesta", "") and "[99]" not in d.get("respuesta", "") and "citas inexistentes quitadas: 99" in d.get("avisos", []), d)
        cod, d = preguntar(dict(ant, PMKB_LLM_MODELO="sim-sin-citas"))
        reg.check("respuesta sin citas: aviso «la respuesta no cita evidencia: revisarla»", "la respuesta no cita evidencia: revisarla" in d.get("avisos", []), d)
        for nombre, cfg, esperado in (("clave rechazada (401)", dict(ant, PMKB_SIM_CLAVE=secrets.token_hex(16)), "respondió 401"),
                                      ("modelo inexistente (404)", dict(ant, PMKB_LLM_MODELO="modelo-inexistente"), "respondió 404"),
                                      ("la clave ausente", dict(ant, PMKB_LLM_CLAVE_VAR="PMKB_SIM_CLAVE_AUSENTE"), "falta la clave de la API")):
            cod, d = preguntar(cfg)
            reg.check(f"Preguntar con {nombre}: 200 con la evidencia citada y el error claro («{esperado}»), sin traza",
                      cod == 200 and d.get("modo") == "evidencia" and d.get("fuentes") and esperado in d.get("error", ""), [cod, d.get("modo"), d.get("error")])
        oai = {"PMKB_LLM_TIPO": "openai", "PMKB_LLM_URL": sim.url + "/v1", "PMKB_LLM_MODELO": "sim-respuesta",
               "PMKB_LLM_CLAVE_VAR": "PMKB_SIM_CLAVE", "PMKB_SIM_CLAVE": clave}
        cod, d = preguntar(oai)
        llam = [z for z in sim.registro() if z["ruta"] == "/v1/chat/completions"]
        reg.check("Preguntar con un servidor compatible con OpenAI: POST /v1/chat/completions con Bearer y respuesta citada",
                  d.get("modo") == "respuesta citada (sim-respuesta)" and "[1]" in d.get("respuesta", "") and llam and llam[-1]["authorization"], [d, llam[-1:]])
        # plazo vencido: en proceso (Python de pm-kb) con plazo de 1 s; el simulador tarda 4 s; se mide solo la espera del modelo
        r = subprocess.run([py_kb(), os.path.abspath(__file__), "--sonda-plazo", P], capture_output=True, text=True, timeout=120,
                           env=env_kb(**dict(ant, PMKB_LLM_MODELO="sim-lento")))
        reg.log.append({"cmd": "opcionales.py --sonda-plazo", "cwd": "", "rc": r.returncode, "s": 0, "out": r.stdout[-2000:], "err": r.stderr[-2000:]})
        try: j = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError): j = {}
        reg.check("Preguntar con el modelo que no responde a tiempo: evidencia citada y «no responde», sin esperar al modelo (plazo de 1 s en la prueba; 60 s por defecto)",
                  j.get("modo") == "evidencia" and "no responde" in j.get("error", "") and j.get("fuentes", 0) > 0 and j.get("espera_modelo") is not None and j["espera_modelo"] < 3
                  and j.get("tiempo_defecto") == 60 and "Traceback" not in r.stderr, [j, r.stderr[-300:]])
        # el servicio mientras otro proceso reaplica el esquema (pm-kb base crear / verificar): sin 500
        s = Servicio(reg, env_kb())
        codigos, esquema = [], []
        hilo = threading.Thread(target=lambda: [esquema.append(subprocess.run([LANZ, "base", "crear"], capture_output=True, text=True, env=env_kb(), timeout=120))
                                                for _ in range(8)])
        try:
            hilo.start()
            while (hilo.is_alive() or len(codigos) < 10) and len(codigos) < 300:
                codigos.append(s.pedir("/api/preguntar", tok, {"pregunta": PREGUNTA, "proyecto": P})[0])
            hilo.join()
        finally:
            s.cerrar()
        reg.check("«Preguntar» en la web mientras `pm-kb base crear` reaplica el esquema 8 veces: todas las respuestas 200 y los 8 `base crear` sin error (reintento ante interbloqueo)",
                  codigos and all(c == 200 for c in codigos) and len(esquema) == 8 and all(z.returncode == 0 and "Traceback" not in z.stderr for z in esquema),
                  [{c: codigos.count(c) for c in set(codigos)}] + [z.stderr[-200:] for z in esquema if z.returncode])
        # CLI y MCP: evidencia citada (contexto) para que el agente redacte
        r = kb_ej(reg)("contexto", PREGUNTA, "--proyecto", P, paso="contexto (CLI)")
        reg.check("CLI `pm-kb contexto`: evidencia citada con el encabezado de evidencia y R-003", r.out.startswith(ENCABEZADO) and "R-003" in r.out and f"{P}@" in r.out, r.out[:300])
        resp, ajenas = mcp_stdio(reg, env_kb(PMKB_PROYECTOS=P, **ant), INICIO_MCP + [llamada(2, "contexto", {"pregunta": PREGUNTA, "proyecto": P})], "MCP stdio contexto")
        t = texto_mcp(resp[-1]) if resp else ""
        reg.check("MCP stdio `contexto` (con modelo de respuesta configurado): evidencia citada, sin llamar al modelo",
                  t.startswith(ENCABEZADO) and "R-003" in t and f"{P}@" in t and not ajenas, t[:300])
    finally:
        if tok: revocar(env_kb(), persona)
        quitar(reg, P); sim.cerrar()


def sonda_plazo(proyecto):
    """(Python de pm-kb) «Preguntar» con el plazo del cliente HTTP en 1 s: el simulador «sim-lento» tarda más."""
    sys.path.insert(0, KB_DIR)
    from pmkb import config, modelos
    from pmkb.busqueda import Sesion
    defecto = modelos.TIEMPO
    modelos._post.__defaults__ = (None, 1.0)
    original, espera = modelos.responder, []

    def medir(*a, **k):   # solo la llamada al modelo de respuesta: la búsqueda previa depende de la carga del equipo
        t0 = time.time()
        try:
            return original(*a, **k)
        finally:
            espera.append(time.time() - t0)
    modelos.responder = medir
    t = time.time()
    r = Sesion(config.conectar(), "*", True).preguntar(PREGUNTA, proyecto=proyecto)
    print(json.dumps({"modo": r["modo"], "error": r.get("error", ""), "fuentes": len(r["fuentes"]),
                      "segundos": round(time.time() - t, 1), "espera_modelo": round(sum(espera), 1) if espera else None,
                      "tiempo_defecto": defecto}, ensure_ascii=False))


# ---------------------------------------------------------------- unidad kb-pm-method
def kb_pm_method(trabajo, reg, cache):
    if not kb_disponible(reg): return
    repo = proyecto_e2e(cache, os.path.join(trabajo, "portal-socios"))
    P = "zz-opc-pm"
    personas = ("zz-opc pm-method", "zz-opc pm-method restringida")
    x = Ejecutor(reg, sys.executable, cwd=repo)
    kb = lambda *a, ok=(0,), paso="": kb_ej(reg)(*a, ok=ok, paso=paso)
    bmad0 = huella(repo, ("_bmad", "_bmad-output"))
    try:
        r = kb("indexar", "--proyecto", P, "--ruta", repo, paso="indexar antes de escribir")
        u0, h0 = re.search(r"(\d+) unidades", r.out), re.search(r"(\d+) entradas de historia", r.out)
        # escrituras de pm-method (scripts, bitácora)
        r = x("registro", "--proyecto", "gestion", "agregar", "riesgos", "--campo", "evento=Falla del lector QR de sucursales por el firmware nuevo",
              "--campo", "categoria=tecnico", "--campo", "probabilidad=3", "--campo", "impacto=4", "--campo", "propietario=Martín Suárez", paso="registro.py agregar riesgos")
        rid = (re.findall(r"\bR-\d{3}\b", r.out) or [""])[-1]
        x("registro", "--proyecto", "gestion", "actualizar", "riesgos", rid, "--campo", "estado=en-seguimiento", "--campo", "notas=revisado con el proveedor",
          paso="registro.py actualizar riesgos")
        r = x("registro", "--proyecto", "gestion", "proponer", "riesgos", "--campo", "evento=Saturación del centro de llamadas durante la migración de socios",
              "--por", "agente: pm-riesgos", paso="registro.py proponer riesgos")
        pid = (re.findall(r"\bP-\d{3}\b", r.out) or [""])[0]
        r = x("registro", "--proyecto", "gestion", "agregar", "stakeholders", "--campo", "nombre=Ana Opcionales", "--campo", "correo=ana.opcionales@example.org",
              "--campo", "usuario_chat=@ana.opcionales", "--campo", "confidencial=si", "--campo", "actitud=resistente",
              "--campo", "expectativas=Teme perder la conducción del área", paso="registro.py agregar stakeholders (confidencial)")
        sid = (re.findall(r"\bST-\d{3}\b", r.out) or [""])[-1]
        escribir(os.path.join(repo, "gestion", "03-control", "reportes", "nota-reservada-opcionales.md"),
                 "---\ncirculacion: restringida\n---\n# Nota reservada\n\nNegociación salarial con el proveedor: clave zafiro.\n")
        r = x("registro", "--proyecto", "gestion", "historial", paso="registro.py historial")
        reg.check("bitácora íntegra tras las escrituras (registro.py historial)", "cadena íntegra" in r.out, r.out[-300:])
        antes = foto(repo)
        r = kb("indexar", "--proyecto", P, "--ruta", repo, paso="reindexar después de escribir")
        u1, h1 = re.search(r"(\d+) unidades", r.out), re.search(r"(\d+) entradas de historia", r.out)
        reg.check("reindexar: más unidades y más entradas de historia que antes de las escrituras",
                  u0 and u1 and h0 and h1 and int(u1.group(1)) > int(u0.group(1)) and int(h1.group(1)) > int(h0.group(1)), [u0 and u0.group(0), u1 and u1.group(0), h0 and h0.group(0), h1 and h1.group(0)])
        reg.check("pm-kb no escribe en la carpeta del proyecto (huella de todos los archivos igual tras indexar)", foto(repo) == antes)
        b = kb("buscar", "lector QR firmware", "--proyecto", P, "--json", paso="buscar el riesgo nuevo").json() or {}
        reg.check(f"el riesgo agregado con registro.py ({rid}) aparece primero, citado en registros/riesgos.csv",
                  rid and ids(b)[:1] == [rid] and "03-control/registros/riesgos.csv" in b["resultados"][0]["cita"], ids(b))
        f = kb("ficha", rid, "--proyecto", P, "--historia", "--json", paso="ficha con historia").json() or {}
        ops = [h.get("operacion") for h in f.get("historia", [])]
        reg.check(f"ficha {rid} --historia: la bitácora trae el alta y la actualización", len(ops) >= 2 and any("actualiz" in (o or "") for o in ops), ops)
        b = kb("buscar", "saturación del centro de llamadas", "--proyecto", P, "--json", paso="buscar la propuesta").json() or {}
        reg.check(f"la propuesta {pid} (03-control/propuestas/) se indexa y se encuentra", pid and any(f"03-control/propuestas/{pid}.json" in x_["cita"] for x_ in b.get("resultados", [])),
                  [x_["cita"] for x_ in b.get("resultados", [])])
        d = kb("documento", "gestion/03-control/registros/stakeholders.csv", "--proyecto", P, "--json", paso="documento stakeholders.csv").json() or {}
        txt = " ".join(fr["texto"] for fr in d.get("fragmentos", []))
        reg.check("interesados: sin correo ni usuario de chat en el índice (el nombre sí)", "Ana Opcionales" in txt and "example.org" not in txt and "@ana" not in txt, txt[-300:])
        f = kb("ficha", sid, "--proyecto", P, "--json", paso="ficha del interesado confidencial").json() or {}
        reg.check(f"interesado confidencial ({sid}): sin la valoración (actitud, expectativas)",
                  sid and "resistente" not in f.get("texto", "") and "Teme" not in f.get("texto", "") and "omitida" in f.get("texto", ""), f.get("texto", "")[:300])
        b = kb("buscar", "ana.opcionales@example.org", "--proyecto", P, "--json", paso="buscar el correo").json() or {}
        reg.check("buscar el correo del interesado no devuelve su correo", not any("example.org" in x_["extracto"] for x_ in b.get("resultados", [])), ids(b))
        # BMAD
        b = kb("buscar", "notificaciones por correo y SMS opcional", "--proyecto", P, "--k", "10", "--json", paso="buscar en BMAD").json() or {}
        reg.check("BMAD: los documentos de _bmad-output/ se indexan y se citan", any(":_bmad-output/planning-artifacts/" in x_["cita"] for x_ in b.get("resultados", [])),
                  [x_["cita"] for x_ in b.get("resultados", [])])
        rl = kb("relaciones", "FR-12", "--proyecto", P, "--json", paso="relaciones de un requisito de BMAD").json() or {}
        reg.check("BMAD ↔ especificación de pm-method: FR-12 (requisitos-bmad.csv) se relaciona por id con documentos de _bmad-output/",
                  any(z["origen"].startswith("_bmad-output/") and z["destino"].endswith("#FR-12") for z in rl.get("aristas", [])), (rl.get("aristas") or [])[:3])
        r = kb("documento", "_bmad/_config/manifest.yaml", "--proyecto", P, paso="documento de _bmad/")
        reg.check("BMAD: _bmad/ (instalación) no se indexa", r.out.startswith("Error: "), r.out[:200])
        # circulación restringida: dueño, MCP stdio y HTTP
        b = kb("buscar", "zafiro negociación salarial", "--proyecto", P, "--json", paso="buscar lo restringido (dueño)").json() or {}
        reg.check("circulación restringida: el dueño del índice (CLI) la ve", any("nota-reservada-opcionales" in x_["cita"] for x_ in b.get("resultados", [])), ids(b))
        for restr, ve in (("no", False), ("si", True)):
            resp, ajenas = mcp_stdio(reg, env_kb(PMKB_PROYECTOS=P, PMKB_RESTRINGIDA=restr), INICIO_MCP + [llamada(2, "buscar", {"consulta": "zafiro negociación salarial"})],
                                     f"MCP stdio PMKB_RESTRINGIDA={restr}")
            t = texto_mcp(resp[-1]) if resp else ""
            reg.check(f"MCP stdio con PMKB_RESTRINGIDA={restr}: lo restringido {'aparece' if ve else 'no aparece'}", ("nota-reservada-opcionales" in t) == ve and t and not ajenas, t[:300])
        # agente por MCP stdio (JSON-RPC completo)
        msgs = INICIO_MCP + [{"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                             llamada(3, "buscar", {"consulta": "lector QR firmware", "proyecto": P}),
                             llamada(4, "ficha", {"id": rid, "proyecto": P, "historia": True}),
                             llamada(5, "contexto", {"pregunta": "¿qué riesgos nuevos hay con los lectores QR?", "proyecto": P}),
                             llamada(6, "no-existe", {}), {"jsonrpc": "2.0", "id": 7, "method": "ping"}]
        resp, ajenas = mcp_stdio(reg, env_kb(PMKB_PROYECTOS=P), msgs, "MCP stdio, sesión de agente")
        por = {z.get("id"): z for z in resp}
        herr = por.get(2, {}).get("result", {}).get("tools", [])
        nh = documentado(r"Son (\d+) herramientas")
        reg.check(f"MCP stdio (agente): initialize 2025-06-18, {len(herr)} herramientas de solo lectura (docs/PM-KB.md §11.2: {nh[0] if nh else '?'}), "
                  "stdout solo JSON-RPC, la notificación sin respuesta",
                  por.get(1, {}).get("result", {}).get("protocolVersion") == "2025-06-18" and nh and len(herr) == int(nh[0])
                  and all(h["annotations"]["readOnlyHint"] for h in herr) and not ajenas and len(resp) == 7, [len(resp), ajenas[:2]])
        reg.check(f"MCP stdio (agente): buscar trae {rid} con cita, ficha con la historia de la bitácora y contexto con el encabezado de evidencia",
                  rid in texto_mcp(por.get(3, {})) and "cita:" in texto_mcp(por.get(3, {})) and "Historia (bitácora)" in texto_mcp(por.get(4, {}))
                  and texto_mcp(por.get(5, {})).startswith(ENCABEZADO) and rid in texto_mcp(por.get(5, {})), [texto_mcp(por.get(i, {}))[:120] for i in (3, 4, 5)])
        reg.check("MCP stdio (agente): herramienta desconocida → error -32602; ping → {}",
                  por.get(6, {}).get("error", {}).get("code") == -32602 and por.get(7, {}).get("result") == {}, [por.get(6), por.get(7)])
        # MCP por HTTP con tokens personales
        t1 = token(env_kb(), personas[0], P)
        t2 = token(env_kb(), personas[1], P, restringida=True)
        s = Servicio(reg, env_kb())
        try:
            ini = INICIO_MCP[0]
            c0, _ = s.pedir("/mcp", None, ini)
            c1, j1 = s.pedir("/mcp", t1, ini)
            c2, j2 = s.pedir("/mcp", t1, llamada(2, "buscar", {"consulta": "lector QR firmware"}))
            c3, _ = s.pedir("/mcp", t1, ini, origen="http://otro.example")
            c4, j4 = s.pedir("/mcp", t1, llamada(3, "buscar", {"consulta": "zafiro negociación salarial"}))
            c5, j5 = s.pedir("/mcp", t2, llamada(4, "buscar", {"consulta": "zafiro negociación salarial"}))
            c6, j6 = s.pedir("/api/buscar?q=zafiro&proyecto=" + P, t1)
        finally:
            s.cerrar()
        reg.check("MCP por HTTP (agente con token): sin token 401, initialize 200, buscar trae el riesgo nuevo, origen ajeno 403",
                  c0 == 401 and c1 == 200 and j1.get("result", {}).get("serverInfo", {}).get("name") == "pm-kb" and c2 == 200
                  and rid in texto_mcp(j2) and c3 == 403, [c0, c1, c2, c3])
        reg.check("MCP por HTTP y web: un token sin circulación restringida no la ve; uno con --restringida, sí",
                  c4 == 200 and "nota-reservada-opcionales" not in texto_mcp(j4) and c5 == 200 and "nota-reservada-opcionales" in texto_mcp(j5)
                  and c6 == 200 and not j6.get("resultados"),
                  [texto_mcp(j4)[:120], texto_mcp(j5)[:120], c6])
        reg.check("BMAD intacto: ningún archivo de _bmad/ ni _bmad-output/ cambió (escrituras de pm-method e índice de pm-kb)", huella(repo, ("_bmad", "_bmad-output")) == bmad0)
    finally:
        for p in personas: revocar(env_kb(), p)
        quitar(reg, P)


# ---------------------------------------------------------------- unidad externas (Docker)
def imagen_docker():
    """(imagen, motivo si no se puede usar)."""
    if not shutil.which("docker"): return None, "docker no está en el PATH"
    try:
        if subprocess.run(["docker", "info"], capture_output=True, timeout=60).returncode != 0: return None, "`docker info` falló (¿daemon detenido?)"
    except (OSError, subprocess.TimeoutExpired) as x:
        return None, f"`docker info` no respondió ({x})"
    pedida = os.environ.get("PM_IMAGEN_DOCKER")
    if not pedida:
        sys.path.insert(0, EST)
        import esquema
        pedida = f"pm-method:{esquema.VERSION_PAQUETE}"
        if subprocess.run(["docker", "image", "inspect", pedida], capture_output=True).returncode != 0:
            tags = sorted(subprocess.run(["docker", "images", "pm-method", "--format", "{{.Tag}}"], capture_output=True, text=True).stdout.split(),
                          key=lambda t: [int(n) if n.isdigit() else 0 for n in re.split(r"[.-]", t)])
            if tags: pedida = "pm-method:" + tags[-1]
    if subprocess.run(["docker", "image", "inspect", pedida], capture_output=True).returncode != 0:
        return None, f"no está la imagen {pedida} (docs/DOCKER.md: docker compose -f docker/compose.yaml build)"
    return pedida, ""


def externas(trabajo, reg, cache):
    img, motivo = imagen_docker()
    if not img:
        reg.omitir("docker", "sin Docker o sin la imagen de pm-method: " + motivo); return
    reg.notas.append(f"skills externas: imagen {img}")
    sk = os.environ.get("PM_SKILLS_EXTERNAS", "")
    repo = proyecto_e2e(cache, os.path.join(trabajo, "repo"))
    for d, ds, fs in os.walk(trabajo):                               # el contenedor corre como pm (uid 1000)
        for n in ds + fs: os.chmod(os.path.join(d, n), 0o777 if n in ds else 0o666)
    os.chmod(trabajo, 0o777)
    base = ["docker", "run", "--rm", "--network", "none", "--tmpfs", "/tmp:exec,mode=1777", "-v", f"{RAIZ}:/opt/pm-method:ro",
            "-v", f"{trabajo}:/trabajo", "-w", "/trabajo"]
    if sk and os.path.isdir(sk): base += ["-v", f"{os.path.abspath(sk)}:/skills-externas:ro", "-e", "PM_SKILLS=/skills-externas"]
    t0 = time.time()
    r = subprocess.run(base + [img, "python3", "-I", "/opt/pm-method/scripts/pruebas/variantes/opcionales.py", "--en-contenedor", "/trabajo/repo"],
                       capture_output=True, text=True, timeout=1800)
    reg.log.append({"cmd": f"docker run --network none {img} opcionales.py --en-contenedor", "cwd": trabajo, "rc": r.returncode,
                    "s": round(time.time() - t0, 1), "out": r.stdout[-6000:], "err": r.stderr[-3000:]})
    vistos = 0
    for l in r.stdout.splitlines():
        if l.startswith("RESULTADO "):
            z = json.loads(l[10:]); reg.check(z["nombre"], z["ok"], z.get("detalle", "")); vistos += 1
        elif l.startswith("OMITIDO "):
            z = json.loads(l[8:]); reg.omitir(z["clave"], z["motivo"])
        elif l.startswith("NOTA "):
            reg.notas.append(l[5:])
    reg.check("contenedor de skills externas: terminó y produjo resultados", r.returncode in (0, 1) and vistos > 0, (r.stdout + r.stderr)[-500:])
    if "Traceback (most recent call last)" in r.stdout + r.stderr:
        reg.trazas.append({"paso": "contenedor de skills externas", "comando": "docker run", "cola": (r.stderr or r.stdout)[-600:]})
    # caso DD de probar_paquete.py dentro de la imagen
    r = subprocess.run(base + [img, "python3", "/opt/pm-method/scripts/probar_paquete.py", "--casos", "DD", "--sin-integracion", "--json", "/trabajo/dd.json"],
                       capture_output=True, text=True, timeout=900)
    reg.log.append({"cmd": f"docker run --network none {img} probar_paquete.py --casos DD", "cwd": trabajo, "rc": r.returncode, "s": 0, "out": r.stdout[-3000:], "err": r.stderr[-2000:]})
    try: d = json.load(open(os.path.join(trabajo, "dd.json"), encoding="utf-8"))
    except (OSError, ValueError): d = {}
    c = (d.get("casos") or {}).get("DD", {})
    reg.check(f"caso DD de probar_paquete.py en la imagen (con diagram-design): {c.get('ok', 0)} OK · {c.get('fallo', '?')} FALLO, sin omisiones",
              c.get("ok", 0) >= 5 and c.get("fallo") == 0 and not d.get("omitidas"), [c, d.get("omitidas"), r.stdout[-300:]])
    # las salidas reales de las skills en el portal de pm-kb (en el anfitrión, con el pm-kb de esta copia)
    import portal
    presentes = ["diagram-design"] + [n for n in ("archify", "visual-explainer") if sk and os.path.isfile(os.path.join(sk, n, "SKILL.md"))]
    portal.documentos_externos(trabajo, reg, os.path.join(trabajo, "repo"), presentes)


# ---------------------------------------------------------------- dentro del contenedor (sin red, Python de la imagen)
def en_contenedor(repo):
    """Corre en la imagen con --network none. Imprime RESULTADO/OMITIDO/NOTA {json} por línea."""
    def res(nombre, ok, detalle=""):
        print("RESULTADO " + json.dumps({"nombre": nombre, "ok": bool(ok), "detalle": "" if ok else str(detalle)[:700]}, ensure_ascii=False), flush=True)

    def omit(clave, motivo):
        print("OMITIDO " + json.dumps({"clave": clave, "motivo": motivo}, ensure_ascii=False), flush=True)

    plugin = os.environ.get("PM_METHOD_DIR", "/opt/pm-method")
    est = os.path.join(plugin, "skills", "pm-estado-proyecto", "scripts")
    g = os.path.join(repo, "gestion")

    def run(cmd, cwd=g, env=None, timeout=300):
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env or os.environ, timeout=timeout, stdin=subprocess.DEVNULL)
        if "Traceback (most recent call last)" in r.stdout + r.stderr:
            res(f"sin traza de Python: {' '.join(os.path.basename(c) for c in cmd[:3])}", False, (r.stderr or r.stdout)[-400:])
        return r

    def py(script, *a, env=None, cwd=g):
        return run([sys.executable, os.path.join(est, script)] + list(a), env=env, cwd=cwd)

    def ins03(env=None):
        r = py("sanidad.py", "--proyecto", ".", "--json", env=env)
        try: h = json.loads(r.stdout)["hallazgos"]
        except (ValueError, KeyError): return []
        return [x for x in h if x["codigo"] == "INS-03"]

    dd = os.environ.get("PM_DIAGRAM_DESIGN", "")
    skx = os.environ.get("PM_SKILLS", "")
    fuentes = {"diagram-design": dd if os.path.isfile(os.path.join(dd, "SKILL.md")) else ""}
    for n in ("archify", "visual-explainer"):
        p = os.path.join(skx, n)
        fuentes[n] = p if skx and os.path.isfile(os.path.join(p, "SKILL.md")) else ""
        if not fuentes[n]:
            omit("skills-externas", "sin PM_SKILLS_EXTERNAS (copias de archify y visual-explainer): sus pruebas se omiten")
    if not fuentes["diagram-design"]:
        res("la imagen trae diagram-design (PM_DIAGRAM_DESIGN)", False, dd)
    bmad0 = huella(repo, ("_bmad", "_bmad-output"))
    proy_sk = os.path.join(repo, ".claude", "skills")
    usr_sk = os.path.join(os.path.expanduser("~"), ".claude", "skills")
    chrome = "/usr/local/bin/chromium-headless-shell"
    sin_chrome = {k: v for k, v in os.environ.items() if k != "ARCHIFY_CHROME"}

    # 1. detección: INS-03 con cada skill ausente, en el proyecto y en ~/.claude/skills
    for n, src in fuentes.items():
        if not src: continue
        py("estado.py", "--proyecto", ".", "integracion", f"diagramas={n}")
        shutil.rmtree(os.path.join(proy_sk, n), ignore_errors=True)
        h = ins03(sin_chrome)
        res(f"INS-03 sin la skill {n}: AVISO «no se encontró la skill '{n}'» con el respaldo Mermaid como arreglo",
            any(x["severidad"] == "AVISO" and f"no se encontró la skill '{n}'" in x["mensaje"] and "diagramas=mermaid" in x["arreglo"] for x in h), h)
        shutil.copytree(src, os.path.join(proy_sk, n))
        h = ins03(sin_chrome)
        res(f"INS-03 con {n} en .claude/skills del proyecto: INFO «instalada: invocar como '{n}'» y sin AVISO",
            any(x["severidad"] == "INFO" and f"Skill externa '{n}' ({n}) instalada: invocar como '{n}'" in x["mensaje"] and "proyecto (" in x["mensaje"] for x in h)
            and not any(x["severidad"] == "AVISO" for x in h), h)
        if n == "archify":
            res("INS-03 archify sin Chrome en el PATH: INFO «no se encontró Chrome/Chromium»", any("no se encontró Chrome" in x["mensaje"] for x in h), h)
            h2 = ins03(dict(sin_chrome, ARCHIFY_CHROME=chrome))
            res("INS-03 archify con ARCHIFY_CHROME (Chromium de la imagen): sin el INFO de Chrome", not any("Chrome" in x["mensaje"] for x in h2), h2)
        if n in ("archify", "visual-explainer"):
            h3 = ins03(dict(sin_chrome, PATH="/sin-node"))   # el intérprete va por ruta absoluta
            res(f"INS-03 {n} sin Node.js en el PATH: AVISO «necesita Node.js»", any(x["severidad"] == "AVISO" and "necesita Node.js" in x["mensaje"] for x in h3), h3)
        os.makedirs(usr_sk, exist_ok=True)
        shutil.move(os.path.join(proy_sk, n), os.path.join(usr_sk, n))
        h = ins03(sin_chrome)
        res(f"INS-03 con {n} en ~/.claude/skills: INFO con origen «usuario (~/.claude/skills)»",
            any(x["severidad"] == "INFO" and f"'{n}'" in x["mensaje"] and "usuario (~/.claude/skills)" in x["mensaje"] for x in h), h)
        shutil.move(os.path.join(usr_sk, n), os.path.join(proy_sk, n))
    presentes = [n for n, s in fuentes.items() if s]
    lista = ",".join(presentes)
    py("estado.py", "--proyecto", ".", "integracion", f"diagramas={lista}")
    h = ins03(dict(sin_chrome, ARCHIFY_CHROME=chrome))
    integ = json.load(open(os.path.join(g, "estado.json"), encoding="utf-8")).get("integraciones", {})
    res(f"lista por prioridad diagramas={lista}: estado.json la guarda y INS-03 informa cada skill de la lista como instalada, sin AVISO",
        integ.get("diagramas") == lista and sum(1 for x in h if x["severidad"] == "INFO" and "instalada: invocar como" in x["mensaje"]) == len(presentes)
        and not any(x["severidad"] == "AVISO" for x in h), [integ.get("diagramas"), h])

    # 2. contrato de delegación (pm-visuales guía §1.3 y §1.4) con la WBS del proyecto
    vis = os.path.join(g, "02-planificacion", "visuales"); os.makedirs(vis, exist_ok=True)
    r = run([sys.executable, os.path.join(est, "wbs.py"), "02-planificacion/wbs.csv", "--titulo", "Portal de socios", "--mermaid", "02-planificacion/visuales/wbs.md"])
    filas = list(csv.DictReader(open(os.path.join(g, "02-planificacion", "wbs.csv"), encoding="utf-8")))
    codigos = [f["codigo"] for f in filas]
    mmd = open(os.path.join(vis, "wbs.md"), encoding="utf-8").read() if r.returncode == 0 else ""
    res(f"respaldo primero: wbs.py --mermaid escribe 02-planificacion/visuales/wbs.md (flowchart con los {len(codigos)} elementos)",
        "flowchart TD" in mmd and all(f'"{c} ' in mmd or f'("{c} ' in mmd for c in codigos), r.stdout[-300:] + r.stderr[-300:])
    registrados = []
    if fuentes["diagram-design"]:
        s = os.path.join(proy_sk, "diagram-design", "scripts")
        r = run([sys.executable, "-I", os.path.join(s, "mermaid_extract.py"), "02-planificacion/visuales/wbs.md", "--json"])
        try: ir = json.loads(r.stdout)["diagrams"][0]
        except (ValueError, KeyError, IndexError): ir = {"nodes": [], "edges": []}
        res("diagram-design: mermaid_extract.py importa el respaldo de wbs.py (todos los nodos, kind flowchart)",
            ir.get("kind") == "flowchart" and len(ir["nodes"]) == len(codigos) + 1, r.stdout[-300:] + r.stderr[-200:])
        salida = "02-planificacion/visuales/wbs-diagram-design.html"
        open(os.path.join(g, salida), "w", encoding="utf-8").write(dibujo_dd(os.path.join(proy_sk, "diagram-design", "assets", "template.html"), ir))
        r = run([sys.executable, "-I", os.path.join(s, "self_check.py"), "--offline", salida])
        res("diagram-design: self_check.py --offline da OK (fuentes del sistema, sin Google Fonts)", r.returncode == 0 and r.stdout.startswith("OK"), r.stdout[-300:])
        r = run([sys.executable, "-I", os.path.join(s, "export_svg.py"), "--system-fonts", salida])
        svg = os.path.join(g, salida[:-5] + ".svg")
        res("diagram-design: export_svg.py --system-fonts deja el SVG junto a la salida, con los códigos de la WBS",
            r.returncode == 0 and os.path.isfile(svg) and all(c in open(svg, encoding="utf-8").read() for c in codigos), r.stdout[-200:] + r.stderr[-300:])
        r = run([sys.executable, "-I", os.path.join(s, "export_png.py"), salida, salida[:-5] + ".png", "2"], timeout=180)
        res("diagram-design: export_png.py (Playwright de la imagen, sin red) deja el PNG junto a la salida",
            r.returncode == 0 and os.path.getsize(os.path.join(g, salida[:-5] + ".png")) > 1000 if os.path.exists(os.path.join(g, salida[:-5] + ".png")) else False, r.stdout[-200:] + r.stderr[-300:])
        registrados.append(("visual-wbs-diagram-design", salida))
    if fuentes["archify"]:
        a = os.path.join(proy_sk, "archify")
        salida = "02-planificacion/visuales/wbs-archify.html"
        cand = "02-planificacion/visuales/wbs-archify.candidate.json"
        nodos = [{"id": "raiz", "label": "Portal de socios", "sublabel": "WBS · BORRADOR"}]
        for f in filas:
            c = f["codigo"]; padre = c.rsplit(".", 1)[0] if "." in c else ""
            nodos.append({"id": "n" + c.replace(".", "_"), "label": f"{c} {f['nombre']}"[:60], "parent": "n" + padre.replace(".", "_") if padre else "raiz",
                          "sublabel": f["tipo"]})
        json.dump({"schema_version": 1, "diagram_type": "tree", "meta": {"title": "WBS · Portal de socios", "subtitle": "Fuente: 02-planificacion/wbs.csv · BORRADOR",
                                                                          "output": salida, "quality_profile": "showcase"},
                   "layout": {"direction": "down"}, "nodes": nodos}, open(os.path.join(g, cand), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        env = dict(os.environ, ARCHIFY_UPDATE_CHECK_DISABLED="1", ARCHIFY_CHROME=chrome, ARCHIFY_CHROME_NO_SANDBOX="1")
        r = run(["node", os.path.join(a, "bin", "archify.mjs"), "finalize", "tree", cand, salida, "--quality", "showcase", "--json"], env=env, timeout=300)
        try: j = json.loads(r.stdout)
        except ValueError: j = {}
        res("archify: finalize tree desde la tabla de la WBS con ok true y validate, deliver, check y browser-check en pass (Chromium de la imagen, sin red)",
            j.get("ok") is True and j.get("gates") == {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"}, [j.get("gates"), j.get("diagnostics")])
        out = open(os.path.join(g, salida), encoding="utf-8").read() if os.path.exists(os.path.join(g, salida)) else ""
        res("archify: la salida contiene cada elemento de la WBS (sin nodos inventados: tantos nodos como filas + raíz)",
            all(f"{f['codigo']} {f['nombre']}"[:60] in out for f in filas) and len(nodos) == len(filas) + 1, len(out))
        lado = sorted(os.path.basename(p) for p in glob.glob(os.path.join(vis, "wbs-archify.*")))
        res("archify: subproductos junto a la salida con el mismo prefijo; nada en .archify/ del cwd ni en ~/.agent/",
            "wbs-archify.finalize.json" in lado and not os.path.exists(os.path.join(g, ".archify")) and not os.path.exists(os.path.expanduser("~/.agent")), lado)
        r = run(["node", os.path.join(a, "bin", "archify.mjs"), "finalize", "tree", cand, "02-planificacion/visuales/wbs-archify-sin-chrome.html", "--quality", "showcase", "--json"],
                env={k: v for k, v in env.items() if not k.startswith("ARCHIFY_CHROME")}, timeout=300)
        try: j = json.loads(r.stdout)
        except ValueError: j = {}
        res("archify sin Chrome: browser-check «skipped» y las otras tres puertas en pass («verificado sin navegador», guía §1.4)",
            j.get("gates") == {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "skipped"}, j.get("gates"))
        malo = "02-planificacion/visuales/malo.candidate.json"
        json.dump({"schema_version": 1, "diagram_type": "tree", "meta": {"title": "x", "output": "02-planificacion/visuales/malo.html"},
                   "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B", "parent": "no-existe"}]}, open(os.path.join(g, malo), "w"))
        r = run(["node", os.path.join(a, "bin", "archify.mjs"), "finalize", "tree", malo, "02-planificacion/visuales/malo.html", "--json"], env=env)
        try: j = json.loads(r.stdout)
        except ValueError: j = {}
        res("archify con un candidato inválido (padre inexistente): ok false, validate en fail (tree/missing-parent), código distinto de 0 y el respaldo Mermaid sigue en su lugar",
            j.get("ok") is False and r.returncode != 0 and (j.get("gates") or {}).get("validate") == "fail"
            and "tree/missing-parent" in [x.get("code") for x in j.get("diagnostics", [])] and os.path.isfile(os.path.join(vis, "wbs.md")), [r.returncode, j.get("gates"), [x.get("code") for x in j.get("diagnostics", [])][:3]])
        for p in glob.glob(os.path.join(vis, "malo*")) + glob.glob(os.path.join(vis, "wbs-archify-sin-chrome*")): os.remove(p)
        registrados.append(("visual-wbs-archify", salida))
    if fuentes["visual-explainer"]:
        v = os.path.join(proy_sk, "visual-explainer")
        e = json.load(open(os.path.join(g, "estado.json"), encoding="utf-8"))
        cuerpo = re.search(r"```mermaid\n(.*?)```", mmd, re.S)
        src = os.path.join(vis, "one-pager-project-brief.src.html")
        open(src, "w", encoding="utf-8").write(
            '<!doctype html>\n<html lang="es" data-register="paper">\n<head><title>One-pager · ' + html.escape(e["proyecto"]) + ' (BORRADOR)</title>'
            '<link rel="stylesheet" href="kit.css" data-ve-kit></head>\n<body><main>\n<h1>' + html.escape(e["proyecto"]) + ' · resumen de una página · one-page summary</h1>\n'
            '<p>BORRADOR · fase ' + html.escape(e.get("fase", "")) + ' · fuente 01-inicio/project-brief.md y 02-planificacion/wbs.csv</p>\n'
            '<figure><pre class="mermaid" aria-label="WBS del proyecto">' + html.escape(cuerpo.group(1) if cuerpo else "") + '</pre>'
            '<figcaption>WBS: ' + ", ".join(codigos) + '.</figcaption></figure>\n</main></body></html>\n')
        r = run(["node", os.path.join(v, "kit", "render.mjs"), os.path.basename(src)], cwd=vis, timeout=180)
        salida = "02-planificacion/visuales/one-pager-project-brief.html"
        out = open(os.path.join(g, salida), encoding="utf-8").read() if os.path.exists(os.path.join(g, salida)) else ""
        res("visual-explainer: kit/render.mjs (sin --open) renderiza la fuente .src.html junto a la salida, con «✓», el kit en línea y la WBS dibujada",
            r.returncode == 0 and "✓" in r.stdout and "<svg" in out and all(c in out for c in codigos) and e["proyecto"] in out, r.stdout[-300:] + r.stderr[-300:])
        res("visual-explainer: nada en ~/.agent/diagrams/", not os.path.exists(os.path.expanduser("~/.agent/diagrams")))
        if "fonts.googleapis.com" in out:
            print("NOTA visual-explainer 0.14.0 enlaza Google Fonts en la página (kit de su registro): sin red se ve con fuentes del sistema", flush=True)
        registrados.append(("one-pager-project-brief", salida))
    # 3. registro de artefactos y sanidad
    for clave, ruta in registrados:
        r = py("estado.py", "--proyecto", ".", "artefacto", clave, "--ruta", ruta, "--estado", "borrador")
        res(f"estado.py artefacto {clave} --estado borrador", r.returncode == 0, r.stderr[-200:])
    if registrados:
        r = py("sanidad.py", "--proyecto", ".", "--json")
        try: h = json.loads(r.stdout)["hallazgos"]
        except (ValueError, KeyError): h = []
        res("sanidad reconoce los visuales registrados (sin ART-01 de esas claves)", not any(x["codigo"] == "ART-01" and any(c in x["mensaje"] for c, _ in registrados) for x in h),
            [x for x in h if x["codigo"].startswith("ART")])
        clave, ruta = registrados[0]
        os.rename(os.path.join(g, ruta), os.path.join(g, ruta + ".bak"))
        r = py("sanidad.py", "--proyecto", ".", "--json")
        try: h = json.loads(r.stdout)["hallazgos"]
        except (ValueError, KeyError): h = []
        os.rename(os.path.join(g, ruta + ".bak"), os.path.join(g, ruta))
        res(f"sanidad: si falta la salida de {clave}, ERROR ART-01", any(x["codigo"] == "ART-01" and clave in x["mensaje"] for x in h), [x for x in h if x["codigo"].startswith("ART")])
    res("BMAD intacto tras la detección y los visuales (huella de _bmad/ y _bmad-output/)", huella(repo, ("_bmad", "_bmad-output")) == bmad0)


def dibujo_dd(plantilla, ir):
    """Redibujo mínimo del árbol en la plantilla de diagram-design (lo que haría el agente siguiendo la skill): fuentes del
    sistema (sin el <link> a Google Fonts), un nodo por elemento del respaldo y una flecha por arista. No es un diagrama
    curado: sirve para comprobar el camino de la skill (self_check, export_svg y export_png) con la entrada de pm-method."""
    t = open(plantilla, encoding="utf-8").read()
    t = re.sub(r'\s*<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>', "", t)
    hijos, padre = {}, {}
    for e in ir.get("edges", []):
        hijos.setdefault(e["source"], []).append(e["target"]); padre[e["target"]] = e["source"]
    raiz = next((n["id"] for n in ir["nodes"] if n["id"] not in padre), ir["nodes"][0]["id"] if ir["nodes"] else "")
    nivel, orden = {raiz: 0}, [raiz]
    for n in orden:
        for h in hijos.get(n, []):
            nivel[h] = nivel[n] + 1; orden.append(h)
    por_nivel = {}
    for n in orden: por_nivel.setdefault(nivel[n], []).append(n)
    ancho = max(len(v) for v in por_nivel.values()) * 150 + 40
    alto = len(por_nivel) * 110 + 40
    pos = {n: (20 + i * 150 + (ancho - 40 - len(v) * 150) / 2, 20 + k * 110) for k, v in por_nivel.items() for i, n in enumerate(v)}
    etiqueta = {n["id"]: n["label"].split("\n")[0] for n in ir["nodes"]}
    g = []
    for a, b in padre.items():
        if a in pos and b in pos:
            g.append(f'<line x1="{pos[b][0] + 65:.0f}" y1="{pos[b][1] + 44:.0f}" x2="{pos[a][0] + 65:.0f}" y2="{pos[a][1]:.0f}" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>')
    for n, (x, y) in pos.items():
        g.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="130" height="44" rx="6" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>'
                 f'<text x="{x + 65:.0f}" y="{y + 26:.0f}" text-anchor="middle" font-size="10" fill="#2d3142">{html.escape(etiqueta[n][:24])}</text>')
    t = t.replace('viewBox="0 0 960 600"', f'viewBox="0 0 {ancho:.0f} {alto:.0f}"').replace("[diagram-slug]", "wbs-portal")
    t = t.replace("[Diagram title]", "WBS · Portal de socios (BORRADOR)").replace("[Type] · Diagram Design", "Tree · Diagram Design")
    t = t.replace("[One sentence describing what the diagram shows]", "Elementos de la WBS desde 02-planificacion/wbs.csv; fuente pm-method, borrador.")
    return t.replace("<!-- Draw arrows first, then nodes. Replace with your content. -->", "\n        ".join(g))


# ---------------------------------------------------------------- correr (llamado por correr.py)
UNIDADES = {"kb-pruebas": kb_pruebas, "kb-vectores": kb_vectores, "kb-respuesta": kb_respuesta, "kb-pm-method": kb_pm_method, "externas": externas}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="\n".join(__doc__.splitlines()[1:]))
    ap.add_argument("--en-contenedor", metavar="DIR"); ap.add_argument("--sonda-plazo", metavar="PROYECTO")
    a = ap.parse_args()
    if a.en_contenedor: en_contenedor(a.en_contenedor)
    elif a.sonda_plazo: sonda_plazo(a.sonda_plazo)
    else: ap.print_help()


if __name__ == "__main__":
    main()
