#!/usr/bin/env python3
"""Corre los recorridos E2E de docs/guias/ con los scripts reales y guarda la evidencia.

Uso:  python3 scripts/pruebas/guias_e2e/correr.py [--guias 1,2,3,4,5] [--salida DIR]
Cada guía crea su propio proyecto temporal (copia de scripts/pruebas/fixtures/bmad-v6.12-real), ejecuta los comandos
que las skills usan por detrás y escribe en DIR salida-g<N>.md (comandos y salidas) y sus imágenes:
  g1 (13): g1-mapa-inherente-residual, g1-opciones-valor-neto, g1-sensibilidad-r003, g1-exposicion-respuestas,
      g1-tablero, g1-decision-r007, g1-revisiones-vencidas, g1-exposicion-tendencia, g1-consumo-reserva,
      g1-tarjetas-etapa y, con pm-kb, g1-kb-busqueda, g1-kb-ficha, g1-kb-versiones
  g2 (11): g2-gantt, g2-capacidad-release, g2-decision-release, g2-business-case, g2-impacto-c002, g2-decision-c002,
      g2-roadmap-c001, g2-trazabilidad, g2-consumo-cambio, g2-alcance-evm, g2-indicadores
  g3 (11): g3-interesados-matriz, g3-interesados-raci-perfiles, g3-decision-kr-b02, g3-candidatos-reunion, g3-radar,
      g3-highlight-indicadores, g3-okr-salud, g3-tablero, g3-tablero-actor, g3-cadencia-stk12, g3-brecha-compromiso
  g4 (9): g4-burnup, g4-tablero, g4-calidad-entregas, g4-recorrido, g4-tablero-mapas-169, g4-lecciones-ciclo,
      g4-cierre, g4-expediente, g4-beneficios
  g5 (17): g5-mapa-supuestos, g5-van-opciones, g5-matriz-opciones, g5-enfoque-entrega, g5-wardley, g5-recorrido,
      g5-hacer-comprar-c2, g5-tablero-mapas, g5-tablero-mapas-169, g5-presupuesto, g5-personas-mapa, g5-tres-disenos,
      g5-tablero, g5-personas-mapa-bmad, g5-recorrido-bmad, g5-wardley-bmad, g5-tablero-mapas-bmad
(61 imágenes, todas .png de 1600×900 salvo las capturas; los -169 son recortes 16:9 para diapositivas). Los gráficos usan visuales.py (matplotlib); las capturas de tableros,
reportes HTML, recorridos y la interfaz web de pm-kb usan playwright (sin playwright se omiten con un aviso); g5-wardley*.png usa mmdc.
pm-kb es opcional: con él (lanzador `pm-kb` en el PATH, PMKB_LANZADOR o pm-kb/pm-kb del repositorio, y `pm-kb base estado`
sin error), las guías 1 (paso 16) y 4 (paso 9c) indexan su proyecto con un nombre fijo (portal-socios, producto-bmad),
consultan y lo quitan al terminar; sin él, esos pasos se omiten ("OMITIDO pm-kb") y la guía termina igual, sin las
tres capturas g1-kb-*. Lo que cambia en cada corrida (fecha del indexado, puerto y token de la sesión web, fechas reales
de la bitácora) se enmascara en la evidencia.
La guía 3 levanta un servidor SMTP y un receptor de webhooks de prueba en 127.0.0.1 para mostrar el envío real por la
capa de canales sin salir a la red.
La guía 5 (de la idea al proyecto diseñado) no parte del fixture en su variante principal: crea un proyecto sin BMAD,
los tres diseños del bloque C y, para la variante con BMAD, una copia del fixture.
Las decisiones humanas están simuladas con los nombres del escenario; el contenido redactado por el modelo (texto de
informes, planes) se reemplaza por archivos mínimos: lo que se verifica es el gobierno, los registros y los cálculos.
Las fechas del escenario se fijan con --fecha y --corte (también la creación del proyecto: comun.base_su), de modo que
dos corridas dan la misma evidencia; los nombres de archivo que fechan bmad.py handoff, paquete.py y exportar.py llevan
el día de la corrida.
"""
import argparse, os, subprocess, sys, time
AQUI = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--guias", default="1,2,3,4,5"); ap.add_argument("--salida", default=os.getcwd())
a = ap.parse_args(); os.makedirs(a.salida, exist_ok=True)
fallos = 0
for g in a.guias.split(","):
    t = time.time()
    r = subprocess.run([sys.executable, os.path.join(AQUI, f"g{g}.py"), os.path.join(a.salida, f"salida-g{g}.md")],
                       cwd=AQUI, env={**os.environ, "GUIAS_SALIDA": a.salida}, capture_output=True, text=True)
    ok = r.returncode == 0
    fallos += not ok
    print(f"{'OK   ' if ok else 'FALLO'} guía E2E-{g} · {time.time() - t:.0f} s · {os.path.join(a.salida, f'salida-g{g}.md')}")
    for l in r.stdout.splitlines():
        if l.startswith("OMITIDO"): print("      " + l)
    if not ok: print(r.stdout[-2000:], r.stderr[-2000:])
sys.exit(1 if fallos else 0)
