#!/usr/bin/env python3
"""Valida los bloques Mermaid del repositorio (documentación, plantillas y docs/diagramas/*.mmd).

Dos capas:
  1. Lint estático (siempre): errores que GitHub no puede renderizar y que ya ocurrieron en este repo
     - ';' dentro de mensajes de sequenceDiagram (corta la línea)
     - etiquetas de arista |...| con paréntesis sin comillas
     - '{{' (marcadores de plantilla) en etiquetas de arista sin comillas, datos de gantt o números de xychart/quadrant
     - wardley-beta: nombres sin comillas con caracteres no ASCII o con una palabra que empieza por dígito (el parser
       falla), title entre comillas (se dibujan las comillas), note sin comillas, coordenadas fuera de 0–1
     - journey: puntaje que no es un entero de 1 a 5, ':' de más en el texto de la tarea
  2. Render real con mmdc (opcional, si está instalado): --render [--config puppeteer.json]. mmdc puede terminar sin
     error y dibujar un SVG con "Syntax error" (pasa con wardley-beta): el render se hace a SVG y se busca ese texto.

Uso:
  python3 scripts/validar_mermaid.py                 # lint
  python3 scripts/validar_mermaid.py --render        # lint + render con mmdc
  python3 scripts/validar_mermaid.py --render --png DIR   # además guarda PNG para inspección visual
Salida: código 0 si no hay errores.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUIR = {".git", "node_modules", "_bmad", "_bmad-output", ".bmad-core", "salida-v2.1"}
BLOQUE = re.compile(r"^```mermaid[^\n]*\n(.*?)^```", re.S | re.M)


def bloques():
    for base, dirs, archivos in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in EXCLUIR and not d.startswith("fixtures")]
        for a in sorted(archivos):
            ruta = os.path.join(base, a)
            rel = os.path.relpath(ruta, RAIZ)
            if a.endswith(".md"):
                texto = open(ruta, encoding="utf-8").read()
                for m in BLOQUE.finditer(texto):
                    linea = texto[: m.start()].count("\n") + 1
                    yield rel, linea, m.group(1)
            elif a.endswith(".mmd"):
                yield rel, 1, open(ruta, encoding="utf-8").read()


def tipo(codigo):
    lineas = codigo.splitlines()
    if lineas and lineas[0].strip() == "---":  # frontmatter de configuración
        fin = next((i for i, l in enumerate(lineas[1:], 1) if l.strip() == "---"), 0)
        lineas = lineas[fin + 1:]
    for l in lineas:
        l = l.strip()
        if l and not l.startswith("%%"):
            return l.split()[0]
    return ""


def lint(codigo):
    errores = []
    t = tipo(codigo)
    for n, l in enumerate(codigo.splitlines(), 1):
        s = l.strip()
        if s.startswith("%%"):
            continue
        if t == "sequenceDiagram" and re.search(r"-[->x)]+[+-]?\s*\w+\s*:", s):
            msg = s.split(":", 1)[1]
            if ";" in msg:
                errores.append(f"l.{n}: ';' en mensaje de secuencia (usar ',')")
        for et in re.findall(r"\|([^|]*)\|", s) if t in ("flowchart", "graph") else []:
            et_s = et.strip()
            if ("(" in et_s or ")" in et_s or "{{" in et_s) and not (et_s.startswith('"') and et_s.endswith('"')):
                errores.append(f"l.{n}: etiqueta de arista sin comillas con paréntesis o '{{{{': |{et}|")
        if t in ("gantt", "xychart-beta", "quadrantChart"):
            # marcadores de plantilla donde Mermaid espera fechas o números
            if re.search(r":[^%]*\{\{", s) and t == "gantt" and not s.startswith("title"):
                errores.append(f"l.{n}: marcador '{{{{…}}}}' en datos de gantt (usar un valor de ejemplo + comentario %%)")
            if t != "gantt" and re.search(r"\[[^\]]*\{\{|\{\{[^}]*\}\}\s*,", s):
                errores.append(f"l.{n}: marcador '{{{{…}}}}' en lugar de un número")
        if t == "wardley-beta":
            errores += lint_wardley(n, s)
        if t == "journey":
            errores += lint_journey(n, s)
    return errores


NOMBRE_W = r'(?:"[^"]*"|[^\[\]"]+?)'


def _nombre_mal(nombre):
    nombre = nombre.strip()
    if nombre.startswith('"') and nombre.endswith('"'):
        return False
    return bool(re.search(r"[^\x00-\x7f]", nombre) or re.search(r"(^|\s)\d", nombre))


def lint_wardley(n, s):
    errores = []
    if s.startswith("title ") and s[6:].strip().startswith('"'):
        errores.append(f"l.{n}: title de wardley-beta entre comillas (Mermaid dibuja las comillas)")
    m = re.match(rf"^(anchor|component)\s+({NOMBRE_W})\s*\[([^\]]*)\]", s)
    if m:
        if _nombre_mal(m.group(2)):
            errores.append(f"l.{n}: nombre sin comillas con tildes, eñe u otro carácter no ASCII, o con una palabra que empieza por dígito: {m.group(2).strip()}")
        try:
            if not all(0 <= float(x) <= 1 for x in m.group(3).split(",")):
                errores.append(f"l.{n}: coordenadas fuera de 0–1: [{m.group(3)}]")
        except ValueError:
            errores.append(f"l.{n}: coordenadas no numéricas: [{m.group(3)}]")
    m = re.match(rf"^({NOMBRE_W})\s*(?:-+>|<-+>|-\.->)\s*({NOMBRE_W})\s*$", s)
    if m and not s.startswith(("evolution", "title")):
        for x in (m.group(1), m.group(2)):
            if _nombre_mal(x):
                errores.append(f"l.{n}: nombre sin comillas en un enlace: {x.strip()}")
    m = re.match(rf"^evolve\s+({NOMBRE_W})\s+[\d.]+\s*$", s)
    if m and _nombre_mal(m.group(1)):
        errores.append(f"l.{n}: nombre sin comillas en evolve: {m.group(1).strip()}")
    if s.startswith("note ") and not s[5:].strip().startswith('"'):
        errores.append(f"l.{n}: texto de note sin comillas")
    return errores


def lint_journey(n, s):
    if s.startswith(("journey", "title", "section")) or ":" not in s:
        return []
    partes = s.split(":")
    if len(partes) != 3:
        return [f"l.{n}: tarea de journey con ':' de más o sin actores (formato 'tarea: puntaje: actores'): {s[:60]}"]
    p = partes[1].strip()
    if not (p.isdigit() and 1 <= int(p) <= 5):
        return [f"l.{n}: puntaje de journey '{p}' (debe ser un entero de 1 a 5)"]
    return []


def render(codigo, config, png_dir, nombre):
    with tempfile.TemporaryDirectory() as d:
        ent = os.path.join(d, "d.mmd")
        open(ent, "w", encoding="utf-8").write(codigo)
        svg = os.path.join(d, "d.svg")
        salidas = [svg] + ([os.path.join(png_dir, nombre + ".png")] if png_dir else [])
        for sal in salidas:
            cmd = ["mmdc", "-i", ent, "-o", sal, "-b", "white"]
            if sal.endswith(".png"):
                cmd += ["-s", "2"]
            if config:
                cmd += ["-p", config]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if r.returncode != 0:
                ultima = [x for x in (r.stderr or r.stdout).splitlines() if x.strip()]
                return (ultima[0] if ultima else "error de mmdc")[:300]
            if sal == svg and "Syntax error" in open(svg, encoding="utf-8", errors="replace").read():
                return "mmdc dibujó un diagrama de 'Syntax error' (el bloque no se puede interpretar)"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--render", action="store_true", help="renderizar con mmdc (si está instalado)")
    ap.add_argument("--config", help="archivo de configuración de puppeteer para mmdc (-p)")
    ap.add_argument("--png", help="carpeta donde guardar PNG para inspección visual")
    a = ap.parse_args()

    lista = list(bloques())
    fallos = 0
    for rel, linea, codigo in lista:
        for e in lint(codigo):
            print(f"ERROR {rel}:{linea} {e}")
            fallos += 1

    if a.render:
        if not shutil.which("mmdc"):
            print("AVISO mmdc no está instalado; se omite el render (npm i -g @mermaid-js/mermaid-cli)")
        else:
            if a.png:
                os.makedirs(a.png, exist_ok=True)

            def tarea(i):
                rel, linea, codigo = lista[i]
                nombre = f"{i:03d}-" + re.sub(r"[^A-Za-z0-9]+", "_", rel)[-60:] + f"-{linea}"
                return i, render(codigo, a.config, a.png, nombre)

            with ThreadPoolExecutor(max_workers=6) as ex:
                for i, err in ex.map(tarea, range(len(lista))):
                    if err:
                        rel, linea, _ = lista[i]
                        print(f"ERROR {rel}:{linea} render: {err}")
                        fallos += 1

    print(f"{'OK' if not fallos else 'FALLO'} · {len(lista)} bloques Mermaid · {fallos} error(es)")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
