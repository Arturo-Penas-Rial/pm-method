#!/usr/bin/env python3
"""Corre los recorridos E2E de docs/guias/ con los scripts reales y guarda la evidencia.

Uso:  python3 scripts/pruebas/guias_e2e/correr.py [--guias 1,2,3,4] [--salida DIR]
Cada guía crea su propio proyecto temporal (copia de scripts/pruebas/fixtures/bmad-v6.12-real), ejecuta los comandos
que las skills usan por detrás y escribe en DIR:  salida-g<N>.md (comandos y salidas) y, si playwright está instalado,
las capturas del tablero (g1-tablero.png, g3-tablero.png, g3-tablero-actor.png, g4-tablero.png).
Las decisiones humanas están simuladas con los nombres del escenario; el contenido redactado por el modelo (texto de
informes, planes) se reemplaza por archivos mínimos: lo que se verifica es el gobierno, los registros y los cálculos.
"""
import argparse, os, subprocess, sys, time
AQUI = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--guias", default="1,2,3,4"); ap.add_argument("--salida", default=os.getcwd())
a = ap.parse_args(); os.makedirs(a.salida, exist_ok=True)
fallos = 0
for g in a.guias.split(","):
    t = time.time()
    r = subprocess.run([sys.executable, os.path.join(AQUI, f"g{g}.py"), os.path.join(a.salida, f"salida-g{g}.md")],
                       cwd=AQUI, env={**os.environ, "GUIAS_SALIDA": a.salida}, capture_output=True, text=True)
    ok = r.returncode == 0
    fallos += not ok
    print(f"{'OK   ' if ok else 'FALLO'} guía E2E-{g} · {time.time() - t:.0f} s · {os.path.join(a.salida, f'salida-g{g}.md')}")
    if not ok: print(r.stdout[-2000:], r.stderr[-2000:])
sys.exit(1 if fallos else 0)
