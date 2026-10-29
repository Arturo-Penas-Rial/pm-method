"""Utilidades de los recorridos E2E de docs/guias/: corren los mismos scripts que usan las skills sobre una copia del fixture BMAD 6.12.4."""
import os, sys, shutil, subprocess, tempfile, json, csv
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
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
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout + ("\n" + r.stderr if r.stderr.strip() else "")).rstrip()
    if r.returncode not in ok:
        print("FALLO", cmd, "\n", out); sys.exit(1)
    out = out.replace(cwd, "<repo>")
    out = __import__("re").sub(r"<\d+\.\d+\.\d+@[^>]+>", "<message-id>", out)   # Message-ID de SMTP: varía en cada corrida
    out = __import__("re").sub(r"índice reconstruido ahora \(\d{4}-\d{2}-\d{2}T[\d:]+\)", "índice reconstruido ahora (<fecha-hora>)", out)   # marca de tiempo de la corrida
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
