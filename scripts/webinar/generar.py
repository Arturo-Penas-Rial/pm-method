#!/usr/bin/env python3
"""Generador de diapositivas del webinar de pm-method (PPTX + HTML autocontenido con glosario).

Lee `docs/webinar/E2E-N/diapositivas.json` (esquema en docs/webinar/README.md), lo valida y escribe en la carpeta del
caso (o en --salida): `E2E-N-diapositivas.pptx` y `E2E-N-diapositivas.html`. Agrega la portada del caso, la portada
de cada clase con sus objetivos y el glosario al final. Sin marca ni logo de empresa: un recuadro rotulado
"Logo IEEE" (o la imagen que se pase con --logo).

Uso:
    python3 scripts/webinar/generar.py --caso docs/webinar/E2E-1 [--salida DIR] [--logo logo-ieee.png]
    python3 scripts/webinar/generar.py --todos [--salida DIR]
    python3 scripts/webinar/generar.py --caso docs/webinar/E2E-1 --validar      # solo valida, no escribe nada

Requiere Python 3.9+ (solo biblioteca estándar) y, para el PPTX, Node.js con pptxgenjs (`npm install -g pptxgenjs@4.0.1`).
Salida: 0 sin errores (puede haber avisos), 1 con errores de validación o de generación, 2 uso incorrecto.
EN: Webinar slide generator (PPTX + self-contained HTML with glossary) from diapositivas.json.
"""
import argparse
import base64
import glob
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
TIPOS = ("seccion", "gancho", "contenido", "imagen", "indicadores", "demo", "pregunta", "ejercicio", "tabla", "cierre")
CLAVES_DIAPO = {"tipo", "titulo", "subtitulo", "puntos", "imagen", "tabla", "pregunta", "prompt", "nota"}
CLAVES_CLASE = {"numero", "titulo", "duracion_min", "objetivos", "diapositivas"}
CLAVES_CASO = {"caso", "titulo", "subtitulo", "clases", "glosario"}
MAX_PUNTOS, MAX_FILAS, MAX_COLS = 5, 6, 4
DIAPOS_MIN, DIAPOS_MAX, GLOS_MIN, GLOS_MAX = 12, 20, 10, 25
e = html.escape


def version_paquete():
    try:
        return json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return "[verificar versión]"


def tam_imagen(ruta):
    """(ancho, alto) en píxeles de un PNG o JPEG, o None si no se reconoce."""
    with open(ruta, "rb") as f:
        cab = f.read(26)
        if cab[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", cab[16:24])
        if cab[:2] != b"\xff\xd8":
            return None
        f.seek(2)
        while True:
            b = f.read(1)
            while b and b != b"\xff":
                b = f.read(1)
            while b == b"\xff":
                b = f.read(1)
            if not b:
                return None
            if b[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                f.read(3)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            largo = struct.unpack(">H", f.read(2))[0]
            f.seek(largo - 2, 1)


# ====================================================================== validación
class Informe:
    def __init__(self, caso):
        self.caso, self.errores, self.avisos = caso, [], []

    def error(self, donde, msg):
        self.errores.append(f"{donde}: {msg}")

    def aviso(self, donde, msg):
        self.avisos.append(f"{donde}: {msg}")


def _texto(v):
    return isinstance(v, str) and v.strip() != ""


def resolver_imagen(valor, carpeta):
    for base in (RAIZ, carpeta):
        p = (base / valor).resolve() if not os.path.isabs(valor) else Path(valor)
        if p.is_file():
            return p
    return None


def validar(datos, carpeta, inf):
    """Valida el JSON y devuelve el mazo normalizado (o None si hay errores)."""
    if not isinstance(datos, dict):
        inf.error("raíz", "el JSON debe ser un objeto {caso, titulo, subtitulo, clases, glosario}")
        return None
    for k in sorted(set(datos) - CLAVES_CASO):
        inf.aviso("raíz", f"clave desconocida «{k}» (se ignora); claves válidas: {', '.join(sorted(CLAVES_CASO))}")
    for k in ("caso", "titulo"):
        if not _texto(datos.get(k)):
            inf.error("raíz", f"falta «{k}» (texto)")
    if _texto(datos.get("caso")) and datos["caso"] != carpeta.name:
        inf.aviso("raíz", f"«caso» es {datos['caso']!r} pero la carpeta se llama {carpeta.name!r}")
    if "subtitulo" in datos and not isinstance(datos["subtitulo"], str):
        inf.error("raíz", "«subtitulo» debe ser texto")
    clases = datos.get("clases")
    if not isinstance(clases, list) or not clases:
        inf.error("raíz", "falta «clases» (lista con al menos una clase)")
        clases = []
    mazo = {"caso": datos.get("caso", carpeta.name), "titulo": datos.get("titulo", ""), "subtitulo": datos.get("subtitulo", ""),
            "clases": [], "glosario": []}
    numeros = set()
    for ic, c in enumerate(clases, 1):
        dc = f"clase {ic}"
        if not isinstance(c, dict):
            inf.error(dc, "debe ser un objeto {numero, titulo, duracion_min, objetivos, diapositivas}")
            continue
        for k in sorted(set(c) - CLAVES_CLASE):
            inf.aviso(dc, f"clave desconocida «{k}» (se ignora)")
        num = c.get("numero")
        if not isinstance(num, int) or isinstance(num, bool) or num < 1:
            inf.error(dc, "«numero» debe ser un entero ≥ 1")
            num = ic
        elif num in numeros:
            inf.error(dc, f"«numero» {num} repetido")
        numeros.add(num)
        dc = f"clase {num}"
        if not _texto(c.get("titulo")):
            inf.error(dc, "falta «titulo»")
        dur = c.get("duracion_min")
        if not isinstance(dur, int) or isinstance(dur, bool) or dur <= 0:
            inf.error(dc, "«duracion_min» debe ser un entero positivo (minutos)")
        obj = c.get("objetivos", [])
        if not isinstance(obj, list) or not all(_texto(o) for o in obj):
            inf.error(dc, "«objetivos» debe ser una lista de textos")
            obj = []
        elif not obj:
            inf.aviso(dc, "sin «objetivos»: la portada de la clase queda vacía")
        elif len(obj) > 6:
            inf.aviso(dc, f"{len(obj)} objetivos; la portada muestra los 6 primeros")
        diapos = c.get("diapositivas")
        if not isinstance(diapos, list) or not diapos:
            inf.error(dc, "falta «diapositivas» (lista no vacía)")
            diapos = []
        elif not DIAPOS_MIN <= len(diapos) <= DIAPOS_MAX:
            inf.aviso(dc, f"tiene {len(diapos)} diapositivas; lo recomendado son {DIAPOS_MIN}–{DIAPOS_MAX} por clase de 90 minutos")
        clase = {"numero": num, "titulo": c.get("titulo", ""), "duracion_min": dur if isinstance(dur, int) else 0,
                 "objetivos": obj, "diapositivas": []}
        for idd, d in enumerate(diapos, 1):
            dd = f"clase {num}, diapositiva {idd}"
            if not isinstance(d, dict):
                inf.error(dd, "debe ser un objeto")
                continue
            tipo = d.get("tipo")
            if _texto(d.get("titulo")):
                dd += f" «{d['titulo'][:40]}»"
            if tipo not in TIPOS:
                inf.error(dd, f"tipo desconocido {tipo!r}; tipos válidos: {', '.join(TIPOS)}")
                continue
            for k in sorted(set(d) - CLAVES_DIAPO):
                inf.aviso(dd, f"clave desconocida «{k}» (se ignora); claves válidas: {', '.join(sorted(CLAVES_DIAPO))}")
            if not _texto(d.get("titulo")):
                inf.error(dd, "falta «titulo»")
            for k in ("subtitulo", "pregunta", "prompt", "nota"):
                if k in d and not isinstance(d[k], str):
                    inf.error(dd, f"«{k}» debe ser texto")
            puntos = d.get("puntos", [])
            if not isinstance(puntos, list) or not all(_texto(p) for p in puntos):
                inf.error(dd, "«puntos» debe ser una lista de textos")
                puntos = []
            elif len(puntos) > MAX_PUNTOS:
                inf.error(dd, f"tiene {len(puntos)} puntos; el máximo es {MAX_PUNTOS} (partí la diapositiva)")
            if any(len(p) > 160 for p in puntos):
                inf.aviso(dd, "hay puntos de más de 160 caracteres; en la diapositiva conviene que sean cortos")
            img = None
            if tipo == "imagen" and not _texto(d.get("imagen")):
                inf.error(dd, "el tipo imagen necesita «imagen» (ruta bajo docs/guias/img/)")
            if _texto(d.get("imagen")):
                if tipo not in ("imagen", "indicadores"):
                    inf.aviso(dd, f"«imagen» solo se usa en los tipos imagen e indicadores; en {tipo} se ignora")
                else:
                    ruta = resolver_imagen(d["imagen"], carpeta)
                    if ruta is None:
                        inf.error(dd, f"la imagen citada no existe: {d['imagen']} (se busca desde la raíz del repositorio)")
                    else:
                        tam = tam_imagen(ruta)
                        if not tam:
                            inf.error(dd, f"la imagen no es PNG ni JPEG: {d['imagen']}")
                        else:
                            img = {"ruta": str(ruta), "rel": d["imagen"], "w": tam[0], "h": tam[1], "alt": d.get("titulo", "")}
                            if tam[1] > 1.3 * tam[0]:
                                inf.aviso(dd, f"la imagen {d['imagen']} es muy alta ({tam[0]}×{tam[1]}): en la diapositiva se verá chica; "
                                              "preferí un PNG 16:9 (visuales.py) o un recorte")
            tabla = None
            if tipo == "tabla":
                t = d.get("tabla")
                if not isinstance(t, dict) or not isinstance(t.get("cab"), list) or not isinstance(t.get("filas"), list):
                    inf.error(dd, "el tipo tabla necesita «tabla»: {\"cab\": [...], \"filas\": [[...]]}")
                else:
                    cab, filas = t["cab"], t["filas"]
                    if not cab or not all(isinstance(x, str) for x in cab):
                        inf.error(dd, "«tabla.cab» debe ser una lista de textos")
                    elif len(cab) > MAX_COLS:
                        inf.error(dd, f"la tabla tiene {len(cab)} columnas; el máximo es {MAX_COLS}")
                    if not filas:
                        inf.error(dd, "«tabla.filas» está vacía")
                    elif len(filas) > MAX_FILAS:
                        inf.error(dd, f"la tabla tiene {len(filas)} filas; el máximo es {MAX_FILAS} (tabla máx. {MAX_FILAS}×{MAX_COLS})")
                    for k, f in enumerate(filas, 1):
                        if not isinstance(f, list) or not all(isinstance(x, (str, int, float)) for x in f):
                            inf.error(dd, f"la fila {k} de la tabla debe ser una lista de textos")
                        elif len(f) != len(cab):
                            inf.error(dd, f"la fila {k} tiene {len(f)} celdas y la cabecera {len(cab)}")
                    tabla = {"cab": [str(x) for x in cab], "filas": [[str(x) for x in f] for f in filas if isinstance(f, list)]}
            elif "tabla" in d:
                inf.aviso(dd, f"«tabla» solo se usa en el tipo tabla; en {tipo} se ignora")
            if tipo == "demo" and not _texto(d.get("prompt")):
                inf.error(dd, "el tipo demo necesita «prompt» (el prompt exacto de la guía)")
            if tipo == "pregunta" and not _texto(d.get("pregunta")):
                inf.error(dd, "el tipo pregunta necesita «pregunta»")
            if not _texto(d.get("nota")):
                inf.aviso(dd, "sin «nota» del orador")
            clase["diapositivas"].append({"tipo": tipo, "titulo": d.get("titulo", ""), "subtitulo": d.get("subtitulo", "") or "",
                                          "puntos": puntos[:MAX_PUNTOS], "imagen": img, "tabla": tabla,
                                          "pregunta": d.get("pregunta", "") or "", "prompt": d.get("prompt", "") or "",
                                          # para mostrar: los saltos de línea simples (ajuste de la guía) pasan a espacios
                                          "prompt_vista": re.sub(r"(?<!\n)\n(?!\n)", " ", d.get("prompt", "") or ""),
                                          "nota": d.get("nota", "") or ""})
        mazo["clases"].append(clase)
    glos = datos.get("glosario", [])
    if not isinstance(glos, list):
        inf.error("glosario", "debe ser una lista de {termino, definicion}")
        glos = []
    vistos = set()
    for k, g in enumerate(glos, 1):
        if not isinstance(g, dict) or not _texto(g.get("termino")) or not _texto(g.get("definicion")):
            inf.error("glosario", f"la entrada {k} necesita «termino» y «definicion»")
            continue
        clave = normal(g["termino"])
        if clave in vistos:
            inf.aviso("glosario", f"término repetido: {g['termino']}")
            continue
        vistos.add(clave)
        mazo["glosario"].append({"termino": g["termino"].strip(), "definicion": g["definicion"].strip()})
    if not GLOS_MIN <= len(mazo["glosario"]) <= GLOS_MAX:
        inf.aviso("glosario", f"tiene {len(mazo['glosario'])} términos; lo recomendado son {GLOS_MIN}–{GLOS_MAX}")
    mazo["glosario"].sort(key=lambda g: normal(g["termino"]))
    return None if inf.errores else mazo


def normal(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lstrip("`$.[(")


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", normal(t)).strip("-") or "termino"


# ====================================================================== HTML
class Enlazador:
    """Enlaza al glosario la primera aparición de cada término por diapositiva (fuera del código)."""

    def __init__(self, glosario):
        self.mapa, pats = {}, []
        for g in glosario:
            base = re.sub(r"\s*\([^)]*\)", "", g["termino"]).strip() or g["termino"]
            for variante in {base, g["termino"]}:
                if len(variante) >= 3:
                    self.mapa[normal(e(variante))] = (slug(g["termino"]), g["definicion"])
                    pats.append(e(variante))
        pats.sort(key=len, reverse=True)
        self.rx = re.compile(r"(?<![\w-])(" + "|".join(re.escape(p) for p in pats) + r")(?:es|s)?(?![\w-])", re.I) if pats else None
        self.usados = set()

    def nueva_diapo(self):
        self.usados = set()

    def __call__(self, texto):
        if not self.rx:
            return texto

        def rep(m):
            info = self.mapa.get(normal(m.group(1)))
            if not info or info[0] in self.usados:
                return m.group(0)
            self.usados.add(info[0])
            return f'<a class="term" href="#g-{info[0]}" title="{e(info[1])}">{m.group(0)}</a>'
        return self.rx.sub(rep, texto)


def inl(s, enl=None):
    """`código` y **negrita** → HTML seguro; enlaza términos del glosario si se pasa un enlazador."""
    codigos = []

    def guarda(m):
        codigos.append(m.group(1))
        return f"\x01{len(codigos) - 1}\x02"
    t = e(re.sub(r"`([^`]*)`", guarda, s or ""), quote=False)
    if enl:
        t = enl(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\x01(\d+)\x02", lambda m: f"<code>{e(codigos[int(m.group(1))])}</code>", t)


def data_uri(ruta, cache={}):
    if ruta not in cache:
        tipo = "image/png" if ruta.lower().endswith(".png") else "image/jpeg"
        cache[ruta] = f"data:{tipo};base64," + base64.b64encode(Path(ruta).read_bytes()).decode()
    return cache[ruta]


def logo_html(logo, clase="logo"):
    if logo:
        return f'<div class="{clase} con-img"><img src="{data_uri(str(logo))}" alt="Logo IEEE"></div>'
    return f'<div class="{clase}" aria-label="Espacio reservado para el logo de IEEE">Logo IEEE</div>'


def lista(puntos, enl, clase="vin"):
    if not puntos:
        return ""
    return f'<ul class="{clase}">' + "".join(f"<li>{inl(p, enl)}</li>" for p in puntos) + "</ul>"


def cuerpo_diapo(d, c, enl):
    t, P = d["tipo"], d["puntos"]
    sub = f'<p class="sub">{inl(d["subtitulo"], enl)}</p>' if d["subtitulo"] else ""
    if t == "contenido":
        filas = "".join(f'<li><span class="n">{i}</span><div>{inl(p, enl)}</div></li>' for i, p in enumerate(P, 1))
        return sub + (f'<ol class="filas">{filas}</ol>' if P else "")
    if t == "gancho":
        frase = f'<p class="frase">{inl(d["subtitulo"], enl)}</p>' if d["subtitulo"] else ""
        cards = "".join(f'<div class="card{" oscura" if i == 0 else ""}"><div>{inl(p, enl)}</div></div>' for i, p in enumerate(P))
        return frase + (f'<div class="tarjetas" style="--n:{min(len(P), 5)}">{cards}</div>' if P else "")
    if t == "seccion":
        return ((f'<p class="sub-osc">{inl(d["subtitulo"], enl)}</p>' if d["subtitulo"] else "")
                + lista(P, enl, "vin claro"))
    if t in ("imagen", "indicadores"):
        sub = f'<p class="lectura">{inl(d["subtitulo"], enl)}</p>' if d["subtitulo"] else ""
        if not d["imagen"]:
            kpi = [re.match(r"^\*\*([^*]+)\*\*\s*(\S[\s\S]*)$", p) for p in P]
            if P and all(kpi):   # "**valor** texto" → tarjeta de indicador
                cards = "".join(f'<div class="card kpi{" oscura" if i == 0 else ""}"><b class="v">{inl(k.group(1))}</b><div>{inl(k.group(2), enl)}</div></div>'
                                for i, k in enumerate(kpi))
                return sub + f'<div class="tarjetas kpis" style="--n:{min(len(P), 3)}">{cards}</div>'
            cards = "".join(f'<div class="card{" oscura" if i == 0 else ""}"><div>{inl(p, enl)}</div></div>' for i, p in enumerate(P))
            return sub + f'<div class="tarjetas" style="--n:{min(len(P), 3)}">{cards}</div>'
        im = d["imagen"]
        fig = (f'<figure class="img"><button type="button" class="zoom" title="Ampliar imagen" aria-label="Ampliar imagen">'
               f'<img src="{data_uri(im["ruta"])}" alt="{e(im["alt"])}" width="{im["w"]}" height="{im["h"]}"></button>'
               f'<figcaption>{e(im["rel"])}</figcaption></figure>')
        if not P:
            return sub + f'<div class="conimg solo">{fig}</div>'
        rotulo = "Cómo leerlo" if t == "indicadores" else "Para mirar"
        return sub + f'<div class="conimg{" lect" if t == "indicadores" else ""}">{fig}<aside><h3>{rotulo}</h3>{lista(P, enl)}</aside></div>'
    if t == "demo":
        ver = f'<div class="ver"><h3>Qué deberías ver</h3>{lista(P, enl, "vin check")}</div>' if P else ""
        return (sub + '<p class="rotulo">Prompt · escribilo tal cual</p>'
                f'<div class="prompt"><pre>{e(d["prompt_vista"])}</pre><button type="button" class="copiar" data-copiar="{e(d["prompt"])}">Copiar</button></div>' + ver)
    if t == "pregunta":
        ops = "".join(f'<div class="op">{inl(p, enl)}</div>' for p in P)
        return ((f'<p class="sub-osc">{inl(d["subtitulo"], enl)}</p>' if d["subtitulo"] else "")
                + f'<div class="q"><span class="qm" aria-hidden="true">?</span><p>{inl(d["pregunta"], enl)}</p></div>'
                + (f'<div class="ops" style="--n:{len(P)}">{ops}</div>' if P else ""))
    if t == "ejercicio":
        cards = "".join(f'<div class="card paso"><span class="num">{i}</span><div>{inl(p, enl)}</div></div>' for i, p in enumerate(P, 1))
        porfila = len(P) if len(P) <= 3 else -(-len(P) // 2)
        return sub + f'<div class="tarjetas" style="--n:{porfila}">{cards}</div>'
    if t == "tabla":
        tb = d["tabla"]
        cab = "".join(f"<th>{inl(x)}</th>" for x in tb["cab"])
        corta = lambda x: ' class="nw"' if len(x) <= 12 else ""   # celdas cortas (ids, cifras) sin cortar en el guion
        filas = "".join("<tr>" + "".join(f"<td{corta(x)}>{inl(x, enl)}</td>" for x in f) + "</tr>" for f in tb["filas"])
        return sub + f'<div class="tabla"><table><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>'
    if t == "cierre":
        return (f'<p class="sub-osc fuerte">{inl(d["subtitulo"], enl)}</p>' if d["subtitulo"] else "") + lista(P, enl, "vin claro check")
    return ""


OSCURAS = {"seccion": "azul", "pregunta": "oscura", "cierre": "oscura"}


def armar_html(m, version, logo):
    enl = Enlazador(m["glosario"])
    caso = m["caso"]
    pie_base = f"pm-method {version} · Webinar {caso}"
    partes, opciones, n = [], [], 0

    def diapo(id_, clase_css, titulo, cuerpo, pie, nota, con_logo=True, etiqueta="", pre=""):
        nonlocal n
        n += 1
        opciones.append((id_, f"{n}. {etiqueta or titulo}"))
        nota_html = (f'<details class="nota"><summary>Notas del orador</summary><div>{inl(nota)}</div></details>' if nota else "")
        tit = f'<h2 class="tit">{inl(titulo)}</h2>' if titulo else ""
        partes.append(f'<article class="diapo" id="{id_}" data-n="{n}"><div class="slide {clase_css}">'
                      f'{logo_html(logo) if con_logo else ""}{pre}{tit}<div class="cuerpo">{cuerpo}</div>'
                      f'<footer class="pie"><span>{e(pie)}</span><span>{n}</span></footer></div>{nota_html}</article>')

    # portada del caso
    clases_html = "".join(f'<a class="cl" href="#c{c["numero"]}"><b>Clase {c["numero"]} · {c["duracion_min"]} min</b>'
                          f'<span>{e(c["titulo"])}</span></a>' for c in m["clases"])
    nota_portada = (f'Caso {caso}: {m["titulo"]}. ' + ("Una clase" if len(m["clases"]) == 1 else f'{len(m["clases"])} clases')
                    + " de " + " y ".join(sorted({str(c["duracion_min"]) for c in m["clases"]})) + " minutos. Presentá el problema que "
                    "resuelve el caso y qué se van a llevar los asistentes.")
    diapo("portada", "portada oscura", "",
          f'{logo_html(logo, "logo grande")}<p class="kicker">Webinar · pm-method {e(version)} · {e(caso)}</p>'
          f'<h1>{e(m["titulo"])}</h1>' + (f'<p class="sub-osc">{inl(m["subtitulo"])}</p>' if m["subtitulo"] else "")
          + f'<nav class="clases" style="--n:{len(m["clases"])}">{clases_html}</nav>', pie_base, nota_portada, con_logo=False,
          etiqueta="Portada")
    for c in m["clases"]:
        pie = f"{pie_base} · Clase {c['numero']}"
        indice = "".join(f'<li><a href="#c{c["numero"]}-d{i:02d}">{e(d["titulo"])}</a></li>' for i, d in enumerate(c["diapositivas"], 1))
        objetivos = "".join(f'<li><span class="n">{i}</span><div>{inl(o)}</div></li>' for i, o in enumerate(c["objetivos"][:6], 1))
        opciones.append(("", f"— Clase {c['numero']} —"))
        diapo(f'c{c["numero"]}', "portada-clase oscura", c["titulo"],
              f'<p class="kicker arriba">Clase {c["numero"]} · {c["duracion_min"]} minutos</p>'
              f'<h3 class="obj-t">Objetivos de la clase</h3><ol class="filas osc">{objetivos}</ol>'
              f'<details class="indice"><summary>Diapositivas de esta clase ({len(c["diapositivas"])})</summary><ol>{indice}</ol></details>',
              pie, f'Clase {c["numero"]} ({c["duracion_min"]} minutos): {c["titulo"]}. Objetivos: ' + "; ".join(c["objetivos"]) + ".",
              etiqueta=f'Clase {c["numero"]} · portada')
        for i, d in enumerate(c["diapositivas"], 1):
            enl.nueva_diapo()
            css = f't-{d["tipo"]} ' + OSCURAS.get(d["tipo"], "clara")
            pre = f'<p class="kicker">Clase {c["numero"]}</p>' if d["tipo"] == "seccion" else ""
            diapo(f'c{c["numero"]}-d{i:02d}', css, d["titulo"], cuerpo_diapo(d, c, enl), pie, d["nota"], pre=pre)

    # glosario
    # glosario: un ancla por término (#g-<término>) y otra por letra inicial (#g-letra-X) en la primera fila de cada letra
    letras, filas = [], []
    for g in m["glosario"]:
        L = normal(g["termino"])[:1].upper() or "#"
        ancla = ""
        if not letras or letras[-1] != L:
            letras.append(L)
            ancla = f'<span class="ancla-letra" id="g-letra-{L}"></span>'
        filas.append(f'<tr id="g-{slug(g["termino"])}"><th scope="row">{ancla}{inl(g["termino"])}</th><td>{inl(g["definicion"])}</td></tr>')
    glosario = ""
    if m["glosario"]:
        opciones.append(("glosario", "Glosario"))
        glosario = (f'<section class="glosario" id="glosario"><h2>Glosario</h2><p class="nota-g">{len(m["glosario"])} términos del caso. '
                    'En las diapositivas, los términos subrayados llevan a su definición.</p>'
                    '<nav class="letras">' + "".join(f'<a href="#g-letra-{L}">{L}</a>' for L in letras) + '</nav>'
                    '<table><thead><tr><th>Término</th><th>Definición</th></tr></thead><tbody>' + "".join(filas)
                    + "</tbody></table></section>")
    nav_clases = "".join(f'<a href="#c{c["numero"]}">Clase {c["numero"]}</a>' for c in m["clases"])
    sel = "".join(f'<option value="{i}"{"" if i else " disabled"}>{e(t)}</option>' for i, t in opciones)
    titulo_pag = f"Webinar {caso} · {m['titulo']}"
    return PAGINA.format(titulo=e(titulo_pag), css=CSS, js=JS, caso=e(caso), nav_clases=nav_clases,
                         glos_link='<a href="#glosario">Glosario</a>' if m["glosario"] else "", opciones=sel,
                         cuerpo="".join(partes) + glosario, pie=e(pie_base))


CSS = r"""
:root{--navy:#002855;--blue:#00629b;--orange:#b5651d;--gray:#696969;--ink:#272425;--page:#e9edf1;--surface:#fff;--soft:#f4f6f8;
--tint:#e9f1f8;--ortint:#fbf1e6;--line:#e2e2e6;--sky:#9fd0f0;--dark:#002855;--dark2:#173d66;--azul:#00629b;--code:#0f2238;--codefg:#e8eef5;
--title-ink:#002855;--accent:#00629b;--warm:#b5651d;--shadow:0 6px 24px rgba(0,40,85,.10);color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--page:#0b1118;--surface:#131c27;--soft:#1a2633;--tint:#16283b;--ortint:#2c2116;
--line:#2a3644;--ink:#e6ebf0;--gray:#a3acb6;--dark:#08203d;--dark2:#173d66;--azul:#0a4f7d;--title-ink:#cfe3f3;--accent:#4ea3dc;--warm:#e39a5f;
--shadow:0 6px 24px rgba(0,0,0,.45);color-scheme:dark}}
:root[data-theme="dark"]{--page:#0b1118;--surface:#131c27;--soft:#1a2633;--tint:#16283b;--ortint:#2c2116;--line:#2a3644;--ink:#e6ebf0;
--gray:#a3acb6;--dark:#08203d;--dark2:#173d66;--azul:#0a4f7d;--title-ink:#cfe3f3;--accent:#4ea3dc;--warm:#e39a5f;--shadow:0 6px 24px rgba(0,0,0,.45);color-scheme:dark}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--page);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.4}
a{color:var(--accent)}
code{font-family:"Courier New",monospace;font-size:.92em;background:var(--soft);padding:.05em .3em;border-radius:4px;overflow-wrap:anywhere}
.barra{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;padding:10px 16px;background:var(--surface);
border-bottom:1px solid var(--line)}
.barra .marca{font-weight:700;color:var(--title-ink);margin-right:6px}
.barra nav{display:flex;flex-wrap:wrap;gap:6px}
.barra nav a{padding:4px 10px;border-radius:8px;background:var(--soft);text-decoration:none;font-size:.9rem;color:var(--ink)}
.barra nav a:hover{background:var(--tint)}
.barra .ctl{display:flex;flex-wrap:wrap;gap:6px;margin-left:auto;align-items:center}
.barra select,.barra button{font:inherit;font-size:.85rem;padding:4px 8px;border-radius:8px;border:1px solid var(--line);background:var(--surface);color:var(--ink);max-width:100%}
.barra select{max-width:260px}
.barra button{cursor:pointer}
main{max-width:1240px;margin:0 auto;padding:24px 16px 48px}
.diapo{container-type:inline-size;margin:0 0 28px}
.slide{position:relative;aspect-ratio:16/9;background:var(--surface);border-radius:14px;box-shadow:var(--shadow);
padding:3.75cqw 3.75cqw 6.2cqw;display:flex;flex-direction:column;gap:1.6cqw;font-size:clamp(13px,1.55cqw,21px)}
.slide.oscura{background:var(--dark);color:#fff}
.slide.azul{background:var(--azul);color:#fff}
.slide.oscura code,.slide.azul code{background:var(--dark2);color:#fff}
.logo{position:absolute;top:3cqw;right:3.75cqw;width:12cqw;height:5.85cqw;border:1px dashed #a9a9a9;border-radius:4px;display:grid;
place-items:center;font-size:.72em;color:#8a8a8a}
.oscura .logo,.azul .logo{border-color:#7f9bb8;color:#a9bfd6}
.logo.grande{position:static;width:16.5cqw;height:6.6cqw;margin-bottom:2cqw}
.logo.con-img{border:0}.logo img{max-width:100%;max-height:100%}
.tit{margin:0 14cqw 0 0;background:var(--blue);color:#fff;border-radius:10px;padding:0 1.6cqw;min-height:5.85cqw;display:flex;align-items:center;
font-size:1.7em;line-height:1.15}
.oscura .tit,.azul .tit{background:none;padding:0;font-size:2.4em}
.t-seccion .tit{font-size:2.9em}
.t-seccion .kicker{margin-top:9cqw}
.t-pregunta .tit{font-size:1.5em;color:var(--sky);min-height:5.85cqw}
.cuerpo{flex:1;display:flex;flex-direction:column;gap:1.6cqw;min-height:0}
.pie{position:absolute;left:3.75cqw;right:3.75cqw;bottom:2cqw;display:flex;justify-content:space-between;font-size:.66em;color:var(--gray)}
.oscura .pie,.azul .pie{color:#d6e4f0}
.sub{margin:0;color:var(--warm);font-weight:700;font-size:1.15em}
.lectura{margin:0;font-size:1.05em}
.sub-osc{margin:0;font-size:1.3em;color:#d6e4f0}
.sub-osc.fuerte{color:var(--sky);font-weight:700}
.kicker{margin:0;color:var(--sky);font-weight:700;font-size:1.1em}
.portada h1{margin:0 0 1cqw;font-size:2.6em;line-height:1.12}
.clases{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:1.6cqw;margin-top:auto;max-width:92cqw}
.clases .cl{background:var(--dark2);border-radius:10px;padding:1.4cqw 1.6cqw;color:#fff;text-decoration:none;display:flex;flex-direction:column;gap:.3em}
.clases .cl b{color:var(--sky)}
.portada-clase .kicker.arriba{position:absolute;top:4.2cqw;left:3.75cqw}
.portada-clase .tit{margin-top:4.5cqw}
.obj-t{margin:.4em 0 0;font-size:1.2em}
ol.filas{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1.1cqw;flex:1}
ol.filas li{display:flex;align-items:center;gap:1.4cqw;background:var(--tint);border-radius:10px;padding:1cqw 1.4cqw;flex:1;max-height:9cqw;font-size:1.2em}
ol.filas li:nth-child(even){background:var(--soft)}
ol.filas .n{flex:0 0 auto;width:3.8cqw;height:3.8cqw;border-radius:7px;background:var(--blue);color:#fff;font-weight:700;display:grid;place-items:center;font-size:.85em}
ol.filas.osc li,ol.filas.osc li:nth-child(even){background:var(--dark2);color:#fff}
ol.filas.osc .n{background:none;color:var(--sky);font-size:1.1em;width:2.4cqw}
.frase{margin:.4cqw 0;font-size:2em;font-weight:700;color:var(--title-ink);line-height:1.2}
.tarjetas{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:2.2cqw;flex:1}
.card{background:var(--tint);border-radius:10px;padding:1.6cqw;display:flex;align-items:center;font-size:1.2em}
.card.oscura{background:var(--dark);color:#fff;border:1px solid rgba(255,255,255,.14)}
.tarjetas.kpis{flex:0 0 auto;margin:auto 0}
.card.kpi{flex-direction:column;align-items:flex-start;justify-content:center;gap:.4em;min-height:17cqw}
.card.kpi .v{font-size:2.1em;line-height:1.05;color:var(--title-ink)}
.card.kpi.oscura .v{color:#fff}.card.kpi.oscura div{color:var(--sky)}
.card.paso{background:var(--ortint);flex-direction:column;align-items:flex-start;gap:.5em}
.card .num{font-size:1.8em;font-weight:700;color:var(--warm);line-height:1}
.conimg{display:grid;grid-template-columns:minmax(0,1fr) 30cqw;gap:2.2cqw;flex:1;min-height:0}
.conimg.lect{grid-template-columns:minmax(0,1fr) 34.5cqw}
.conimg.solo{grid-template-columns:1fr}
.conimg aside{background:var(--soft);border-radius:10px;padding:1.6cqw}
.conimg.lect aside{background:var(--tint)}
.conimg aside h3,.ver h3{margin:0 0 .5em;font-size:1.15em;color:var(--warm)}
.conimg.lect aside h3,.ver h3{color:var(--title-ink)}
figure.img{margin:0;display:flex;flex-direction:column;align-items:center;min-height:0}
figure.img .zoom{all:unset;cursor:zoom-in;display:flex;justify-content:center;max-width:100%}
figure.img img{display:block;max-width:100%;max-height:33cqw;width:auto;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff}
figure.img figcaption{font-size:.6em;color:var(--gray);margin-top:.4em}
ul.vin{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:.6em;font-size:1.1em}
ul.vin li{position:relative;padding-left:1.3em}
ul.vin li::before{content:"▪";position:absolute;left:0;color:var(--accent);font-weight:700}
ul.vin.check li::before{content:"✓"}
ul.vin.claro{font-size:1.3em}
ul.vin.claro li::before{color:var(--sky)}
.rotulo{margin:0;font-size:.8em;font-weight:700;color:var(--gray)}
.prompt{position:relative;background:var(--code);border-radius:8px}
.prompt pre{margin:0;padding:1.6cqw 8cqw 1.6cqw 1.8cqw;color:var(--codefg);font-family:"Courier New",monospace;font-size:1.2em;white-space:pre-wrap;overflow-wrap:anywhere}
.copiar{position:absolute;top:.8cqw;right:.8cqw;font:inherit;font-size:.7em;border:0;border-radius:6px;padding:.3em .7em;background:var(--dark2);color:#fff;cursor:pointer}
.ver{background:var(--soft);border-radius:10px;padding:1.4cqw 1.8cqw;flex:1}
.q{display:flex;align-items:center;gap:2.4cqw;flex:1}
.q .qm{flex:0 0 auto;width:9.5cqw;height:9.5cqw;border-radius:50%;background:var(--orange);color:#fff;font-weight:700;font-size:3.6em;display:grid;place-items:center}
.q p{margin:0;font-size:2em;font-weight:700;line-height:1.2}
.ops{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:1.8cqw}
.op{background:var(--dark2);border-radius:10px;padding:1.4cqw 1.6cqw;font-size:1.15em}
.tabla{overflow-x:auto}
.tabla table{width:100%;border-collapse:collapse;font-size:1.05em}
.tabla th{background:var(--navy);color:#fff;text-align:left;padding:.55em .7em}
.tabla td{padding:.55em .7em;border-bottom:1px solid var(--line);vertical-align:top}
.tabla tbody tr:nth-child(odd) td{background:var(--soft)}
.tabla td:first-child{font-weight:700;color:var(--title-ink)}
.tabla td.nw{white-space:nowrap}
a.term{color:inherit;text-decoration:underline dotted;text-underline-offset:.18em}
.oscura a.term,.azul a.term{color:inherit}
details.nota{margin:8px 4px 0;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:8px 14px;font-size:.95rem}
details.nota summary{cursor:pointer;color:var(--accent);font-weight:700}
details.nota div{margin-top:6px}
details.indice{margin-top:auto;font-size:.85em}
details.indice summary{cursor:pointer;color:var(--sky)}
details.indice ol{columns:2;margin:.5em 0 0;padding-left:1.4em}
details.indice a{color:#fff}
.glosario{background:var(--surface);border-radius:14px;box-shadow:var(--shadow);padding:28px clamp(16px,4vw,44px)}
.glosario h2{margin:0 0 .3em;color:var(--title-ink)}
.nota-g{margin:0 0 1em;color:var(--gray)}
.letras{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.letras a{min-width:2em;text-align:center;padding:3px 6px;border-radius:6px;background:var(--soft);text-decoration:none}
.glosario table{width:100%;border-collapse:collapse}
.glosario th,.glosario td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--line)}
.glosario thead th{background:var(--navy);color:#fff}
.glosario tbody th{color:var(--title-ink);width:28%}
.glosario tr:target{background:var(--tint)}
.ancla-letra{position:relative;top:-70px}
dialog.visor{border:0;padding:0;background:transparent;max-width:96vw;max-height:94vh}
dialog.visor::backdrop{background:rgba(0,0,0,.8)}
dialog.visor img{display:block;max-width:96vw;height:auto;background:#fff;border-radius:6px}
dialog.visor .cerrar{position:fixed;top:10px;right:14px;font-size:1.1rem;padding:6px 12px;border-radius:8px;border:0;cursor:pointer}
.pie-pag{text-align:center;color:var(--gray);font-size:.85rem;padding:0 16px 32px}
@media (max-width:760px){
.slide{aspect-ratio:auto;padding:16px 16px 40px;font-size:14px;gap:12px}
.logo{top:14px;right:14px;width:84px;height:40px}
.logo.grande{width:120px;height:48px}
.tit{margin-right:96px;min-height:40px;padding:6px 10px;font-size:1.25em}
.oscura .tit,.azul .tit{font-size:1.6em}
.t-seccion .kicker{margin-top:32px}
.pie{bottom:12px;left:16px;right:16px}
.portada-clase .kicker.arriba{position:static}.portada-clase .tit{margin-top:0}
.tarjetas,.ops,.clases{grid-template-columns:1fr}
.card,.op,.clases .cl,.conimg aside,.ver{padding:12px 14px}.card.kpi{min-height:0}
.conimg,.conimg.lect{grid-template-columns:1fr}
figure.img img{max-height:none}
ol.filas li{max-height:none}
.q .qm{width:56px;height:56px;font-size:2em}.q p{font-size:1.3em}
.frase{font-size:1.4em}.portada h1{font-size:1.8em}
.prompt pre{padding:12px 64px 12px 12px;font-size:1em}
details.indice ol{columns:1}
.barra{position:static}
.barra .ctl{margin-left:0;width:100%}
.barra label{flex:1 1 100%;min-width:0}
.barra select{width:100%;max-width:100%}
html{scroll-padding-top:8px}
}
@media print{
:root,:root:not([data-theme="light"]),:root[data-theme="light"],:root[data-theme="dark"]{--page:#fff;--surface:#fff;--soft:#f4f6f8;--tint:#e9f1f8;--ortint:#fbf1e6;--line:#e2e2e6;--ink:#272425;--gray:#696969;
--dark:#002855;--azul:#00629b;--title-ink:#002855;--accent:#00629b;--warm:#b5651d;color-scheme:light}
@page{size:13.333in 7.5in;margin:0}
body{background:#fff}
.barra,.copiar,.pie-pag,details.indice{display:none}
main{max-width:none;padding:0}
.diapo{margin:0;break-after:page;width:13.333in}
.slide{width:13.333in;height:7.5in;aspect-ratio:auto;border-radius:0;box-shadow:none;overflow:hidden}
.slide,.slide *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
details.nota{display:none}
body.con-notas details.nota{display:block;break-before:page;border:0;font-size:14pt;padding:.6in}
body.con-notas details.nota summary{list-style:none}
.glosario{box-shadow:none;border-radius:0;padding:.5in}
.glosario tr{break-inside:avoid}
}
"""

JS = r"""
(function(){
  var raiz=document.documentElement, diapos=[].slice.call(document.querySelectorAll('.diapo,#glosario'));
  function guardar(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function leer(k){try{return localStorage.getItem(k)}catch(e){return null}}
  var tema=leer('webinar-tema'); if(tema==='light'||tema==='dark') raiz.setAttribute('data-theme',tema);
  var bTema=document.getElementById('b-tema');
  function rotTema(){var t=raiz.getAttribute('data-theme'); bTema.textContent=t==='dark'?'Tema: oscuro':(t==='light'?'Tema: claro':'Tema: automático');}
  rotTema();
  bTema.addEventListener('click',function(){var t=raiz.getAttribute('data-theme'); var s=!t?'light':(t==='light'?'dark':'');
    if(s){raiz.setAttribute('data-theme',s)}else{raiz.removeAttribute('data-theme')} guardar('webinar-tema',s); rotTema();});
  var bNotas=document.getElementById('b-notas'), abiertas=false;
  function notas(v){abiertas=v; [].forEach.call(document.querySelectorAll('details.nota'),function(d){d.open=v});
    document.body.classList.toggle('con-notas',v); bNotas.textContent=v?'Ocultar notas':'Mostrar notas';}
  bNotas.addEventListener('click',function(){notas(!abiertas)});
  function actual(){var y=window.innerHeight*0.35, k=0; for(var i=0;i<diapos.length;i++){if(diapos[i].getBoundingClientRect().top<=y) k=i;} return k;}
  function ir(k){k=Math.max(0,Math.min(diapos.length-1,k)); location.hash=diapos[k].id;}
  document.getElementById('b-ant').addEventListener('click',function(){ir(actual()-1)});
  document.getElementById('b-sig').addEventListener('click',function(){ir(actual()+1)});
  var sel=document.getElementById('ir');
  sel.addEventListener('change',function(){if(sel.value) location.hash=sel.value;});
  document.addEventListener('keydown',function(ev){
    if(/INPUT|SELECT|TEXTAREA/.test((ev.target||{}).tagName||'')||ev.altKey||ev.ctrlKey||ev.metaKey) return;
    if(ev.key==='ArrowRight'||ev.key==='PageDown'){ev.preventDefault(); ir(actual()+1);}
    else if(ev.key==='ArrowLeft'||ev.key==='PageUp'){ev.preventDefault(); ir(actual()-1);}
    else if(ev.key==='n'||ev.key==='N'){notas(!abiertas);}
  });
  var visor=document.getElementById('visor'), vimg=visor.querySelector('img');
  [].forEach.call(document.querySelectorAll('figure.img .zoom'),function(b){b.addEventListener('click',function(){
    var im=b.querySelector('img'); vimg.src=im.src; vimg.alt=im.alt; if(visor.showModal) visor.showModal();});});
  visor.addEventListener('click',function(){visor.close()});
  [].forEach.call(document.querySelectorAll('[data-copiar]'),function(b){b.addEventListener('click',function(){
    var t=b.getAttribute('data-copiar')||b.parentNode.querySelector('pre').textContent;
    if(navigator.clipboard){navigator.clipboard.writeText(t).then(function(){b.textContent='Copiado'; setTimeout(function(){b.textContent='Copiar'},1500)},function(){});}
  });});
})();
"""

PAGINA = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title><style>{css}</style></head>
<body>
<header class="barra">
  <span class="marca">Webinar {caso}</span>
  <nav aria-label="Clases"><a href="#portada">Portada</a>{nav_clases}{glos_link}</nav>
  <div class="ctl">
    <label><span class="sr" hidden>Ir a</span><select id="ir" aria-label="Ir a la diapositiva"><option value="">Ir a la diapositiva…</option>{opciones}</select></label>
    <button type="button" id="b-ant" title="Anterior (←)">◀</button><button type="button" id="b-sig" title="Siguiente (→)">▶</button>
    <button type="button" id="b-notas" title="Notas del orador (N)">Mostrar notas</button>
    <button type="button" id="b-tema">Tema: automático</button>
  </div>
</header>
<main>{cuerpo}</main>
<p class="pie-pag">{pie} · ← → para avanzar · N muestra u oculta las notas · para imprimir con notas, mostralas antes</p>
<dialog class="visor" id="visor"><button type="button" class="cerrar">Cerrar</button><img alt=""></dialog>
<script>{js}</script>
</body></html>"""


# ====================================================================== PPTX (Node + pptxgenjs)
def entorno_node():
    env = dict(os.environ)
    rutas = [p for p in env.get("NODE_PATH", "").split(os.pathsep) if p]
    if shutil.which("npm"):
        try:
            g = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=30).stdout.strip()
            if g:
                rutas.append(g)
        except (OSError, subprocess.SubprocessError):
            pass
    env["NODE_PATH"] = os.pathsep.join(rutas)
    return env


def armar_pptx(mazo, version, logo, salida):
    node = shutil.which("node")
    if not node:
        return False, ["no se encontró Node.js: instalalo para generar el PPTX (el HTML sí se generó)"], []
    datos = dict(mazo, version=version, logo=str(logo) if logo else None)
    r = subprocess.run([node, str(AQUI / "pptx.js"), str(salida)], input=json.dumps(datos, ensure_ascii=False),
                       capture_output=True, text=True, env=entorno_node())
    avisos = [l[len("AVISO: "):] for l in r.stderr.splitlines() if l.startswith("AVISO: ")]
    if r.returncode != 0:
        err = r.stderr.strip()
        if "Cannot find module 'pptxgenjs'" in err:
            err = "falta pptxgenjs: instalalo con `npm install -g pptxgenjs@4.0.1` (el HTML sí se generó)"
        return False, [err], avisos
    return True, [r.stdout.strip()], avisos


# ====================================================================== principal
def procesar(carpeta, salida, logo, solo_validar, version):
    carpeta = Path(carpeta).resolve()
    archivo = carpeta / "diapositivas.json"
    inf = Informe(carpeta.name)
    print(f"== {carpeta.name} ({archivo})")
    if not archivo.is_file():
        print(f"  ERROR: no existe {archivo}")
        return False
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except ValueError as ex:
        print(f"  ERROR: JSON inválido en {archivo}: {ex}")
        return False
    mazo = validar(datos, carpeta, inf)
    for a in inf.avisos:
        print(f"  AVISO: {a}")
    for er in inf.errores:
        print(f"  ERROR: {er}")
    if mazo is None:
        print(f"  {len(inf.errores)} error(es): no se genera nada")
        return False
    nd = sum(len(c["diapositivas"]) for c in mazo["clases"])
    print(f"  válido: {len(mazo['clases'])} clase(s), {nd} diapositivas de contenido, {len(mazo['glosario'])} términos, {len(inf.avisos)} aviso(s)")
    if solo_validar:
        return True
    destino = Path(salida).resolve() if salida else carpeta
    destino.mkdir(parents=True, exist_ok=True)
    base = destino / f"{mazo['caso']}-diapositivas"
    Path(f"{base}.html").write_text(armar_html(mazo, version, logo), encoding="utf-8")
    print(f"  HTML: {base}.html")
    ok, msgs, avisos = armar_pptx(mazo, version, logo, f"{base}.pptx")
    for a in avisos:
        print(f"  AVISO (PPTX): {a}")
    if ok:
        info = json.loads(msgs[0]) if msgs and msgs[0].startswith("{") else {}
        print(f"  PPTX: {base}.pptx ({info.get('diapositivas', '?')} diapositivas)")
    else:
        for m_ in msgs:
            print(f"  ERROR (PPTX): {m_}")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera las diapositivas del webinar (PPTX + HTML) desde diapositivas.json.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--caso", help="carpeta del caso, por ejemplo docs/webinar/E2E-1")
    g.add_argument("--todos", action="store_true", help="recorre docs/webinar/E2E-*/diapositivas.json")
    ap.add_argument("--salida", help="carpeta de salida (por defecto, la del caso)")
    ap.add_argument("--logo", help="PNG del logo de IEEE (opcional; sin él se deja un recuadro rotulado «Logo IEEE»)")
    ap.add_argument("--validar", action="store_true", help="solo valida el JSON; no escribe archivos")
    a = ap.parse_args(argv)
    logo = None
    if a.logo:
        logo = Path(a.logo).resolve()
        if not logo.is_file() or not str(logo).lower().endswith(".png"):
            print(f"ERROR: --logo debe ser un archivo PNG existente: {a.logo}")
            return 2
    version = version_paquete()
    if a.todos:
        carpetas = sorted({str(Path(p).parent) for p in glob.glob(str(RAIZ / "docs" / "webinar" / "E2E-*" / "diapositivas.json"))},
                          key=lambda s: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)])
        if not carpetas:
            print("No hay casos con diapositivas.json en docs/webinar/E2E-*/")
            return 1
    else:
        carpetas = [a.caso]
    oks = [procesar(c, a.salida, logo, a.validar, version) for c in carpetas]
    print(f"Resultado: {sum(oks)}/{len(oks)} caso(s) sin errores")
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
