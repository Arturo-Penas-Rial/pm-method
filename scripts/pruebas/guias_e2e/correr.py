#!/usr/bin/env python3
"""Corre los recorridos E2E de docs/guias/ con los scripts reales y guarda la evidencia.

Uso:  python3 scripts/pruebas/guias_e2e/correr.py [--guias 1,2,3,4,5] [--salida DIR] [--comparar DIR] [--conservar]
                                                  [--python RUTA]
Cada guía crea su propio proyecto temporal (copia de scripts/pruebas/fixtures/bmad-v6.12-real), ejecuta los comandos
que las skills usan por detrás y escribe en DIR salida-g<N>.md (comandos y salidas) y sus imágenes:
  g1 (13): g1-mapa-inherente-residual, g1-opciones-valor-neto, g1-sensibilidad-r003, g1-exposicion-respuestas,
      g1-tablero, g1-decision-r007, g1-revisiones-vencidas, g1-exposicion-tendencia, g1-consumo-reserva,
      g1-tarjetas-etapa y, con pm-kb, g1-kb-busqueda, g1-kb-ficha, g1-kb-versiones
  g2 (11): g2-gantt, g2-capacidad-release, g2-decision-release, g2-business-case, g2-impacto-c002, g2-decision-c002,
      g2-roadmap-c001, g2-trazabilidad, g2-consumo-cambio, g2-alcance-evm, g2-indicadores
  g3 (16): g3-interesados-matriz, g3-interesados-raci-perfiles, g3-decision-kr-b02, g3-candidatos-reunion, g3-radar,
      g3-highlight-indicadores, g3-okr-salud, g3-tablero, g3-tablero-actor, g3-cadencia-stk12, g3-brecha-compromiso y,
      con pm-kb, g3-kb-cartera, g3-kb-historial, g3-kb-comparar, g3-kb-actor, g3-kb-compartido
  g4 (9): g4-burnup, g4-tablero, g4-calidad-entregas, g4-recorrido, g4-tablero-mapas-169, g4-lecciones-ciclo,
      g4-cierre, g4-expediente, g4-beneficios
  g5 (17): g5-mapa-supuestos, g5-van-opciones, g5-matriz-opciones, g5-enfoque-entrega, g5-wardley, g5-recorrido,
      g5-hacer-comprar-c2, g5-tablero-mapas, g5-tablero-mapas-169, g5-presupuesto, g5-personas-mapa, g5-tres-disenos,
      g5-tablero, g5-personas-mapa-bmad, g5-recorrido-bmad, g5-wardley-bmad, g5-tablero-mapas-bmad
(66 imágenes, todas .png de 1600×900 salvo las capturas; los -169 son recortes 16:9 para diapositivas). Los gráficos usan visuales.py (matplotlib); las capturas de tableros,
reportes HTML, recorridos y la interfaz web de pm-kb usan playwright (sin playwright se omiten con un aviso); g5-wardley*.png usa mmdc.
pm-kb es opcional: con él (lanzador `pm-kb` en el PATH, PMKB_LANZADOR o pm-kb/pm-kb del repositorio, y `pm-kb base estado`
sin error), las guías 1 (paso 16), 3 (paso 15) y 4 (paso 9c) indexan su proyecto con un nombre fijo (portal-socios,
portal-socios, producto-bmad), consultan y lo quitan al terminar (la 3 crea, además, un enlace compartido y lo revoca);
sin él, esos pasos de pm-kb se omiten ("OMITIDO pm-kb") y la guía termina igual, sin las capturas g1-kb-* y g3-kb-*.
Lo que cambia en cada corrida (fecha del indexado, puerto y token de la sesión web, token, id y fechas del enlace
compartido, fechas reales de la bitácora, corte del día del tablero publicado) se enmascara en la evidencia
(comun.sin_variables_kb).
La guía 3 levanta un servidor SMTP y un receptor de webhooks de prueba en 127.0.0.1 para mostrar el envío real por la
capa de canales sin salir a la red.
La guía 5 (de la idea al proyecto diseñado) no parte del fixture en su variante principal: crea un proyecto sin BMAD,
los tres diseños del bloque C y, para la variante con BMAD, una copia del fixture.
Las decisiones humanas están simuladas con los nombres del escenario; el contenido redactado por el modelo (texto de
informes, planes) se reemplaza por archivos mínimos: lo que se verifica es el gobierno, los registros y los cálculos.
Las fechas del escenario se fijan con --fecha y --corte (también la creación del proyecto: comun.base_su), de modo que
dos corridas dan la misma evidencia; los nombres de archivo que fechan bmad.py handoff, paquete.py y exportar.py llevan
el día de la corrida.

Intérprete: las guías y los scripts corren con --python RUTA, PM_PY o el intérprete que ejecuta este archivo (nunca el
`python3` del PATH; base.py antepone un lanzador `python3` propio). Temporales: todos los proyectos de la corrida van a
una carpeta `e2e-corrida-*` del directorio temporal, que se borra al terminar (--conservar la deja e informa la ruta).
--comparar DIR compara cada salida-gN.md con DIR/salida-gN.md (normalmente docs/guias/evidencia) después de
enmascarar el día de la corrida en los nombres de archivo (traspasos de BMAD, exportados y paquetes), rutas temporales,
Message-ID y datos variables de pm-kb (comun.sin_variables_kb); sin pm-kb, los bloques de pm-kb de la referencia y el
aviso «OMITIDO pm-kb» de la corrida se excluyen de la comparación (omisión esperada, informada). Si difieren, muestra
el diff y la guía cuenta como FALLO.
"""
import argparse, difflib, os, re, shutil, subprocess, sys, tempfile, time
AQUI = os.path.dirname(os.path.abspath(__file__))


def normalizar(texto, sin_kb=False):
    """Evidencia comparable entre corridas y días (ver el docstring)."""
    sys.path.insert(0, AQUI)
    from comun import sin_variables_kb
    texto = sin_variables_kb(texto.replace("\r\n", "\n"))
    texto = re.sub(r"handoff-bmad-\d{4}-\d{2}-\d{2}", "handoff-bmad-<día>", texto)
    texto = re.sub(r"(exportados/)\d{4}-\d{2}-\d{2}-", r"\1<día>-", texto)
    texto = re.sub(r"(?:/private)?/(?:tmp|var/folders)/[^\s'\"`)]*e2e-[^\s'\"`)]*", "<tmp>", texto)
    texto = re.sub(r"<\d+\.\d+\.\d+@[^>]+>", "<message-id>", texto)
    if sin_kb:   # bloques ```\n$ pm-kb …``` de la referencia y ```\n$ (OMITIDO pm-kb …``` de la corrida
        texto = re.sub(r"```\n\$ (?:pm-kb |\(OMITIDO pm-kb)[^\n]*\n.*?```\n\n?", "", texto, flags=re.S)
    return texto


def comparar(obtenida, referencia):
    """Lista de líneas del diff unificado (vacía si coinciden) y si se excluyó pm-kb."""
    a = open(obtenida, encoding="utf-8").read()
    b = open(referencia, encoding="utf-8").read()
    sin_kb = "OMITIDO pm-kb" in a and "OMITIDO pm-kb" not in b
    na, nb = normalizar(a, sin_kb), normalizar(b, sin_kb)
    if na == nb: return [], sin_kb
    return list(difflib.unified_diff(nb.splitlines(), na.splitlines(), referencia, obtenida, lineterm="", n=2)), sin_kb


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--guias", default="1,2,3,4,5"); ap.add_argument("--salida", default=os.getcwd())
    ap.add_argument("--comparar", metavar="DIR", help="carpeta de referencia (p. ej. docs/guias/evidencia)")
    ap.add_argument("--conservar", action="store_true", help="no borrar la carpeta temporal de la corrida")
    ap.add_argument("--python", metavar="RUTA", help="intérprete de las guías y los scripts (o PM_PY)")
    a = ap.parse_args(); os.makedirs(a.salida, exist_ok=True)
    py = a.python or os.environ.get("PM_PY") or sys.executable
    tmp = tempfile.mkdtemp(prefix="e2e-corrida-")
    env = {**os.environ, "GUIAS_SALIDA": a.salida, "PM_PY": py, "TMPDIR": tmp}
    fallos = 0
    try:
        for g in a.guias.split(","):
            t = time.time()
            sal = os.path.join(a.salida, f"salida-g{g}.md")
            r = subprocess.run([py, os.path.join(AQUI, f"g{g}.py"), sal], cwd=AQUI, env=env, capture_output=True, text=True)
            ok = r.returncode == 0
            fallos += not ok
            print(f"{'OK   ' if ok else 'FALLO'} guía E2E-{g} · {time.time() - t:.0f} s · {sal}")
            for l in r.stdout.splitlines():
                if l.startswith("OMITIDO"): print("      " + l)
            if not ok: print(r.stdout[-2000:], r.stderr[-2000:]); continue
            if a.comparar:
                ref = os.path.join(a.comparar, f"salida-g{g}.md")
                if not os.path.exists(ref):
                    print(f"FALLO evidencia E2E-{g}: no existe {ref}"); fallos += 1; continue
                dif, sin_kb = comparar(sal, ref)
                nota = " (sin pm-kb: sus bloques quedan fuera de la comparación)" if sin_kb else ""
                if dif:
                    fallos += 1
                    print(f"FALLO evidencia E2E-{g} normalizada distinta de {ref}{nota} · {sum(1 for l in dif if l[:1] in '+-') - 2} líneas:")
                    print("\n".join("      " + l for l in dif[:80]) + ("\n      …" if len(dif) > 80 else ""))
                else:
                    print(f"OK    evidencia E2E-{g} normalizada idéntica a {ref}{nota}")
    finally:
        if a.conservar: print(f"Temporales conservados en {tmp}")
        else: shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
