"""Utilidades de los recorridos E2E de docs/guias/: corren los mismos scripts que usan las skills sobre una copia del fixture BMAD 6.12.4."""
import os, sys, shutil, subprocess, tempfile, json, csv, re, shlex, atexit
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

# Intérprete de los scripts: PM_PY o el que corre la guía (no el `python3` del PATH). Los comandos se arman como texto
# (así se ven en la evidencia, con `python3`), de modo que se antepone al PATH una carpeta propia con un lanzador
# `python3` que ejecuta ese intérprete: lo usan run(), las llamadas directas a subprocess de las guías y los scripts.
# Si la ruta del repositorio tiene espacios u otros caracteres de shell, los comandos usan un enlace simbólico sin ellos.
PY = os.environ.get("PM_PY") or sys.executable
_PROPIAS = []
def _carpeta_ejecutable():
    """Carpeta temporal donde se puede ejecutar el lanzador: la temporal del sistema o, si está montada sin permiso de
    ejecución (p. ej. el /tmp en tmpfs del contenedor de pruebas), una dentro de la carpeta personal."""
    for base in (None, os.path.join(os.path.expanduser("~"), ".cache")):
        if base:
            os.makedirs(base, exist_ok=True)
        d = tempfile.mkdtemp(prefix="e2e-py-", dir=base)
        lanzador = os.path.join(d, "python3")
        with open(lanzador, "w", encoding="utf-8") as fh: fh.write(f"#!/bin/sh\nexec {shlex.quote(PY)} \"$@\"\n")
        os.chmod(lanzador, 0o755)
        try:
            subprocess.run([lanzador, "-c", "pass"], check=True, capture_output=True, timeout=60)
            return d
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            shutil.rmtree(d, ignore_errors=True)
    raise SystemExit("guias_e2e: no hay una carpeta temporal donde ejecutar el lanzador de python3 (ni la del sistema ni ~/.cache)")


def _preparar():
    d = _carpeta_ejecutable(); _PROPIAS.append(d)
    os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
    if shlex.quote(RAIZ) != RAIZ:
        enlace = os.path.join(d, "pm-method"); os.symlink(RAIZ, enlace)
        return enlace
    return RAIZ
RAIZ = _preparar()
atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in _PROPIAS])

EST = f"{RAIZ}/skills/pm-estado-proyecto/scripts"
BMAD = f"{RAIZ}/skills/pm-bmad-puente/scripts/bmad.py"
OKR = f"{RAIZ}/skills/pm-okr/scripts/okr.py"
PAQ = f"{RAIZ}/skills/pm-exportar/scripts/paquete.py"
IN = f"{RAIZ}/skills/pm-interesados/scripts/interesados.py"
EV = f"{RAIZ}/skills/pm-integraciones/scripts/envios.py"
# pm-kb (componente opcional): el comando instalado o, si no está en el PATH, el lanzador del repositorio; en la
# evidencia se muestra como `pm-kb`
KB = os.environ.get("PMKB_LANZADOR") or shutil.which("pm-kb") or f"{RAIZ}/pm-kb/pm-kb"
LOG = []
def run(cmd, cwd, mostrar=True, corte=110, ok=(0,)):
    real = cmd.replace(KB, shlex.quote(KB), 1) if cmd.startswith(KB) and shlex.quote(KB) != KB else cmd
    r = subprocess.run(real, shell=True, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout + ("\n" + r.stderr if r.stderr.strip() else "")).rstrip()
    if r.returncode not in ok:
        print("FALLO", cmd, "\n", out); sys.exit(1)
    out = out.replace(cwd, "<repo>")
    out = re.sub(r"<\d+\.\d+\.\d+@[^>]+>", "<message-id>", out)   # Message-ID de SMTP: varía en cada corrida
    out = re.sub(r"índice reconstruido ahora \(\d{4}-\d{2}-\d{2}T[\d:]+\)", "índice reconstruido ahora (<fecha-hora>)", out)   # marca de tiempo de la corrida
    lineas = out.split("\n")
    rec = "\n".join(lineas[:corte]) + (f"\n… ({len(lineas)-corte} líneas más)" if len(lineas) > corte else "")
    vis = cmd.replace(KB, "pm-kb").replace(EST, "$EST").replace(BMAD, "$BMAD").replace(OKR, "$OKR").replace(PAQ, "$PAQ").replace(IN, "$IN").replace(EV, "$EV").replace(RAIZ, "$PLUGIN")
    LOG.append((vis, rec))
    if mostrar: print("$", vis); print(rec); print()
    return out
def proyecto(nombre_dir):
    base = tempfile.mkdtemp(prefix="e2e-")
    repo = os.path.join(base, nombre_dir)
    shutil.copytree(f"{RAIZ}/scripts/pruebas/fixtures/bmad-v6.12-real", repo)
    return repo
def E(sub): return f'python3 {EST}/{sub}'
