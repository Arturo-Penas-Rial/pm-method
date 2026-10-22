#!/usr/bin/env python3
"""Documentos del webinar de pm-method en HTML autocontenido para presentar, repartir o imprimir.

Convierte, por caso E2E-N, la guía paso a paso (`docs/guias/E2E-N-*.md`), el guion del instructor
(`docs/webinar/E2E-N/guion-instructor.md`) y el ejercicio (`docs/webinar/E2E-N/ejercicio.md`) en HTML de un solo
archivo, con la misma estética que las diapositivas de `generar.py`, y escribe en `docs/webinar/E2E-N/`:

    E2E-N-guia.html                    guía paso a paso (asistentes e instructor)
    E2E-N-guion-instructor.html        guion del instructor
    E2E-N-ejercicio.html               ejercicio (asistentes e instructor): empieza por «Cómo funciona este ejercicio» y
                                       termina con el «Ejemplo resuelto» dentro de un bloque plegable

y, con --todos, `docs/webinar/index.html`, que enlaza todo el material de los cinco casos.

Cada página: índice navegable (lateral o plegable en el teléfono), tema claro u oscuro, impresión en A4 sin navegación,
imágenes como data URI, bloques Mermaid dibujados con `mmdc` como SVG en línea (con el código fuente plegable),
enlaces a otros documentos convertidos llevados a su `.html` y a los demás archivos del repositorio, a GitHub.
Sin marca ni logo de empresa: recuadro rotulado «Logo IEEE» (o la imagen que se pase con --logo).

Uso:
    python3 scripts/webinar/documentos.py --todos [--salida DIR] [--logo logo-ieee.png]
    python3 scripts/webinar/documentos.py --caso docs/webinar/E2E-1 [--salida DIR]
    python3 scripts/webinar/documentos.py --todos --validar          # valida (imágenes, enlaces, Mermaid); no escribe
    python3 scripts/webinar/documentos.py --archivo X.md --tipo ejercicio --salida DIR   # un Markdown suelto

Requiere Python 3.9+ (solo biblioteca estándar) y, para los diagramas, mermaid-cli (`mmdc`); sin `mmdc`, error
(o --sin-mermaid: el bloque queda como código, con aviso). Con --salida, la carpeta repite la estructura de
docs/webinar/ (E2E-N/… e index.html) y copia las diapositivas y las fichas del taller ya generadas, para repartir el conjunto.
Salida: 0 sin errores (puede haber avisos), 1 con errores (con errores no se escribe el caso), 2 uso incorrecto.
EN: Self-contained HTML handouts (guide, instructor script, exercise with a folded worked example) and an index page.
"""
import argparse
import base64
import glob
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
import generar as G  # noqa: E402  (misma carpeta: versión, tamaño de imágenes, logo y tokens de color)

REPO_URL = "https://github.com/Arturo-Penas-Rial/pm-method"   # la del README (clonar)
RAMA = "main"                                                # la de .github/workflows
WEB = "docs/webinar"
e = html.escape

TIPOS = {
    "guia": {"nombre": "Guía paso a paso", "corto": "Guía", "para": "asistentes e instructor", "archivo": "{caso}-guia.html"},
    "guion": {"nombre": "Guion del instructor", "corto": "Guion", "para": "instructor", "archivo": "{caso}-guion-instructor.html"},
    "ejercicio": {"nombre": "Ejercicio", "corto": "Ejercicio", "para": "asistentes e instructor", "archivo": "{caso}-ejercicio.html"},
}
INSTRUCTOR = ("guion",)
RX_MECANICA = re.compile(r"^c[oó]mo funciona este ejercicio\b", re.I)
RX_EJEMPLO = re.compile(r"^ejemplo resuelto\b", re.I)
RESUMEN_EJEMPLO = "Ver el ejemplo resuelto (después de intentarlo)"
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp"}


# ====================================================================== utilidades
def rel_repo(p):
    """Ruta relativa a la raíz del repositorio (posix) o None si queda fuera."""
    try:
        return Path(p).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return None


def url_github(rel, carpeta=False, ancla=""):
    return f"{REPO_URL}/{'tree' if carpeta else 'blob'}/{RAMA}/{rel}" + (f"#{ancla}" if ancla else "")


def slug_github(texto):
    """Ancla de encabezado como la calcula GitHub: minúsculas, sin puntuación ni símbolos, espacios → guiones."""
    out = []
    for c in texto.lower():
        if c == " ":
            out.append("-")
        elif c in "-_" or unicodedata.category(c)[0] in "LNM":
            out.append(c)
    return "".join(out)


class Slugger:
    """Anclas únicas como GitHub: la segunda «x» es «x-1», la tercera «x-2»."""

    def __init__(self):
        self.vistos = {}

    def __call__(self, texto):
        base = slug_github(texto)
        s = base
        while s in self.vistos:
            self.vistos[base] += 1
            s = f"{base}-{self.vistos[base]}"
        self.vistos[s] = 0
        return s


def texto_plano(md):
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", md)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.replace("`", "")
    t = re.sub(r"(\*\*|__)(.+?)\1", r"\2", t)
    t = re.sub(r"(?<![\w*])\*(\S(?:.*?\S)?)\*(?![\w*])", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\\([!-/:-@\[-`{-~])", r"\1", t).strip()


RX_FENCE = re.compile(r"^( {0,3})(`{3,}|~{3,})[ \t]*([^`\s]*)[^`]*$")
RX_H = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
RX_HR = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
RX_ITEM = re.compile(r"^( *)([-*+]|\d{1,9}[.)])( +|$)(.*)$")
RX_QUOTE = re.compile(r"^ {0,3}> ?(.*)$")
RX_DELIM = re.compile(r"^ {0,3}\|?[ \t]*:?-+:?[ \t]*(\|[ \t]*:?-+:?[ \t]*)*\|?[ \t]*$")
RX_DET_INI = re.compile(r"^ {0,3}<details( open)?>[ \t]*$", re.I)
RX_DET_FIN = re.compile(r"^ {0,3}</details>[ \t]*$", re.I)
RX_SUMMARY = re.compile(r"^ {0,3}<summary>(.*)</summary>[ \t]*$", re.I)
RX_IMG_SOLA = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")


def anclas_md(texto):
    """Anclas de encabezado de un Markdown (fuera de los bloques de código), como las calcula GitHub."""
    sl, anclas, valla = Slugger(), set(), None
    for l in texto.splitlines():
        m = RX_FENCE.match(l)
        if m and (valla is None or (m.group(2)[0] == valla[0] and len(m.group(2)) >= len(valla) and not m.group(3))):
            valla = None if valla else m.group(2)
            continue
        if valla:
            continue
        h = RX_H.match(l)
        if h and h.group(2) is not None:
            anclas.add(sl(texto_plano(h.group(2))))
    return anclas


def secciones_n2(lineas):
    """[(línea, título en texto plano)] de los encabezados de nivel 2 fuera de los bloques de código."""
    valla, out = None, []
    for i, l in enumerate(lineas):
        m = RX_FENCE.match(l)
        if m and (valla is None or (m.group(2)[0] == valla[0] and len(m.group(2)) >= len(valla) and not m.group(3))):
            valla = None if valla else m.group(2)
            continue
        if valla:
            continue
        h = RX_H.match(l)
        if h and len(h.group(1)) == 2 and h.group(2) is not None:
            out.append((i, texto_plano(h.group(2))))
    return out


# ====================================================================== Markdown → árbol de bloques
def _sangria(l):
    return len(l) - len(l.lstrip(" "))


def _quitar(l, n):
    k = 0
    while k < n and k < len(l) and l[k] == " ":
        k += 1
    return l[k:]


def es_tabla(lineas, i):
    return (i + 1 < len(lineas) and "|" in lineas[i] and "|" in lineas[i + 1] and RX_DELIM.match(lineas[i + 1]) is not None
            and len(celdas(lineas[i])) == len(celdas(lineas[i + 1])))


def inicia_bloque(lineas, i, en_parrafo=True):
    l = lineas[i]
    if not l.strip():
        return True
    if RX_FENCE.match(l) or RX_HR.match(l) or RX_QUOTE.match(l) or RX_DET_INI.match(l) or RX_DET_FIN.match(l) or RX_SUMMARY.match(l):
        return True
    h = RX_H.match(l)
    if h and h.group(2) is not None:
        return True
    m = RX_ITEM.match(l)
    if m and m.group(4).strip() and (not en_parrafo or not m.group(2)[0].isdigit() or m.group(2)[:-1] == "1"):
        return True
    return es_tabla(lineas, i)


def celdas(linea):
    s = linea.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    partes, actual, k = [], "", 0
    while k < len(s):
        if s[k] == "\\" and k + 1 < len(s) and s[k + 1] == "|":
            actual += "|"
            k += 2
            continue
        if s[k] == "|":
            partes.append(actual.strip())
            actual = ""
        else:
            actual += s[k]
        k += 1
    partes.append(actual.strip())
    return partes


def bloques(lineas):
    """Árbol de bloques: ('h', nivel, md) ('p', md) ('fig', img_md, pie_md) ('code', lenguaje, texto) ('hr',)
    ('table', alineaciones, cabecera, filas) ('quote', hijos) ('list', ordenada, inicio, suelta, items)
    ('details', resumen_md, hijos, abierto). Cada item: (tarea None|bool, hijos)."""
    out, i, n = [], 0, len(lineas)
    while i < n:
        l = lineas[i]
        if not l.strip():
            i += 1
            continue
        m = RX_FENCE.match(l)
        if m:
            ind, valla, lang = len(m.group(1)), m.group(2), m.group(3).lower()
            cierre = re.compile(r"^ {0,3}" + re.escape(valla[0]) + "{" + str(len(valla)) + r",}[ \t]*$")
            cuerpo, i = [], i + 1
            while i < n and not cierre.match(lineas[i]):
                cuerpo.append(_quitar(lineas[i], ind))
                i += 1
            out.append(("code", lang, "\n".join(cuerpo)))
            i += 1
            continue
        h = RX_H.match(l)
        if h and h.group(2) is not None:
            out.append(("h", len(h.group(1)), h.group(2)))
            i += 1
            continue
        if RX_HR.match(l):
            out.append(("hr",))
            i += 1
            continue
        if RX_DET_INI.match(l):
            prof, j = 1, i + 1
            while j < n:
                if RX_DET_INI.match(lineas[j]):
                    prof += 1
                elif RX_DET_FIN.match(lineas[j]):
                    prof -= 1
                    if not prof:
                        break
                j += 1
            interior = lineas[i + 1:j]
            resumen = "Detalle"
            k = next((x for x, t in enumerate(interior) if t.strip()), None)
            if k is not None and RX_SUMMARY.match(interior[k]):
                resumen = RX_SUMMARY.match(interior[k]).group(1)
                interior = interior[:k] + interior[k + 1:]
            out.append(("details", resumen, bloques(interior), bool(RX_DET_INI.match(l).group(1))))
            i = j + 1
            continue
        if es_tabla(lineas, i):
            cab = celdas(l)
            alin = []
            for c in celdas(lineas[i + 1]):
                c = c.strip()
                alin.append("center" if c.startswith(":") and c.endswith(":") else "right" if c.endswith(":") else "left" if c.startswith(":") else "")
            filas, i = [], i + 2
            while i < n and lineas[i].strip() and "|" in lineas[i] and not RX_FENCE.match(lineas[i]):
                f = celdas(lineas[i])
                f = (f + [""] * len(cab))[:len(cab)]
                filas.append(f)
                i += 1
            out.append(("table", alin, cab, filas))
            continue
        if RX_QUOTE.match(l):
            dentro = []
            while i < n and lineas[i].strip():
                q = RX_QUOTE.match(lineas[i])
                if q:
                    dentro.append(q.group(1))
                elif inicia_bloque(lineas, i):
                    break
                else:
                    dentro.append(lineas[i])
                i += 1
            out.append(("quote", bloques(dentro)))
            continue
        m = RX_ITEM.match(l)
        if m and m.group(4).strip():
            nodo, i = lista(lineas, i)
            out.append(nodo)
            continue
        par = [l.strip()]
        i += 1
        while i < n and not inicia_bloque(lineas, i):
            par.append(lineas[i].strip())
            i += 1
        if RX_IMG_SOLA.match(par[0]):
            out.append(("fig", par[0].strip(), "\n".join(par[1:])))
        else:
            out.append(("p", "\n".join(par)))
    return out


def lista(lineas, i):
    n = len(lineas)
    m0 = RX_ITEM.match(lineas[i])
    base, ordenada = len(m0.group(1)), m0.group(2)[0].isdigit()
    inicio = int(m0.group(2)[:-1]) if ordenada else 1
    items, suelta = [], False
    while i < n:
        m = RX_ITEM.match(lineas[i])
        if not m or not m.group(4).strip() or m.group(2)[0].isdigit() != ordenada or abs(len(m.group(1)) - base) > 1:
            break
        cont = len(m.group(1)) + len(m.group(2)) + min(len(m.group(3)), 4)
        texto = m.group(4)
        tarea = None
        t = re.match(r"^\[([ xX])\][ \t]+(.*)$", texto)
        if t:
            tarea, texto = t.group(1) != " ", t.group(2)
        propias, i = [texto], i + 1
        while i < n:
            l = lineas[i]
            if not l.strip():
                k = i
                while k < n and not lineas[k].strip():
                    k += 1
                if k < n and _sangria(lineas[k]) >= cont:
                    propias.extend([""] * (k - i))
                    suelta = True
                    i = k
                    continue
                break
            if _sangria(l) >= cont:
                propias.append(_quitar(l, cont))
            elif RX_ITEM.match(l) and RX_ITEM.match(l).group(4).strip():
                break
            elif inicia_bloque(lineas, i, en_parrafo=False):
                break
            elif propias[-1].strip() and not RX_FENCE.match(propias[-1]):
                propias.append(l.strip())       # continuación perezosa del párrafo
            else:
                break
            i += 1
        items.append((tarea, bloques(propias)))
        if i < n and not lineas[i].strip():
            k = i
            while k < n and not lineas[k].strip():
                k += 1
            m2 = RX_ITEM.match(lineas[k]) if k < n else None
            if m2 and m2.group(4).strip() and m2.group(2)[0].isdigit() == ordenada and abs(len(m2.group(1)) - base) <= 1:
                suelta = True
                i = k
                continue
            break
    return ("list", ordenada, inicio, suelta, items), i


# ====================================================================== Mermaid
def tmp_corto():
    """Carpeta temporal de ruta corta: Chromium (mmdc) no arranca si la ruta de su socket supera ~107 caracteres."""
    base = "/tmp" if os.path.isdir("/tmp") and os.access("/tmp", os.W_OK) else tempfile.gettempdir()
    return tempfile.mkdtemp(prefix="pmw-", dir=base)


def render_mermaid(codigo, svg_id, tmp):
    d = tempfile.mkdtemp(dir=tmp)
    ent, sal = os.path.join(d, "d.mmd"), os.path.join(d, "d.svg")
    with open(ent, "w", encoding="utf-8") as f:
        f.write(codigo)
    conf = os.path.join(d, "c.json")
    with open(conf, "w", encoding="utf-8") as f:
        f.write('{"handDrawnSeed": 1}')    # semilla fija: sin ella, los nodos redondeados cambian en cada corrida
    env = dict(os.environ, TMPDIR=tmp)
    try:
        r = subprocess.run([shutil.which("mmdc"), "-q", "-i", ent, "-o", sal, "-b", "white", "-I", svg_id, "-c", conf],
                           capture_output=True, text=True, timeout=240, env=env)
    except (OSError, subprocess.SubprocessError) as ex:
        return None, f"mmdc no se pudo ejecutar: {ex}"
    salida = (r.stderr or "") + (r.stdout or "")
    svg = ""
    if os.path.isfile(sal):
        with open(sal, encoding="utf-8", errors="replace") as f:
            svg = f.read()
    if r.returncode != 0 or not svg:
        if re.search(r"Failed to launch the browser|Could not find (Chrome|Chromium|browser)|socket path|ENAMETOOLONG", salida, re.I):
            return None, ("mmdc no pudo iniciar el navegador (Chromium headless); revisar la instalación de mermaid-cli y "
                          f"de su navegador (TMPDIR usado: {tmp})")
        lineas = [x for x in salida.splitlines() if x.strip()]
        return None, "mmdc terminó con error: " + (" | ".join(lineas[:3])[:300] if lineas else f"código {r.returncode}")
    if "Syntax error" in svg:
        return None, "Mermaid no pudo dibujar el bloque (error de sintaxis: mmdc dibujó «Syntax error»)"
    svg = re.sub(r"^\s*<\?xml[^>]*>\s*", "", svg)
    return svg, None


def mermaid_id(codigo):
    return "mmd-" + hashlib.sha1(codigo.encode("utf-8")).hexdigest()[:10]


def renderizar_mermaid(codigos):
    """{codigo: (svg|None, error|None)} renderizando en paralelo con un TMPDIR corto."""
    if not codigos:
        return {}
    if not shutil.which("mmdc"):
        return {c: (None, "no se encontró mmdc (mermaid-cli): instalalo con `npm install -g @mermaid-js/mermaid-cli` "
                          "o usá --sin-mermaid para dejar el código sin dibujar") for c in codigos}
    tmp = tmp_corto()
    try:
        with ThreadPoolExecutor(max_workers=min(4, len(codigos))) as ex:
            res = list(ex.map(lambda c: render_mermaid(c, mermaid_id(c), tmp), codigos))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(zip(codigos, res))


# ====================================================================== documento
class Documento:
    def __init__(self, caso, tipo, fuente, salida_rel, texto=None):
        self.caso, self.tipo, self.fuente = caso, tipo, Path(fuente).resolve()
        self.fuente_rel = rel_repo(self.fuente)
        self.salida_rel = salida_rel                       # ruta de salida relativa a la raíz (estructura de docs/webinar)
        self.errores, self.avisos = [], []
        texto = texto if texto is not None else self.fuente.read_text(encoding="utf-8")
        self.lineas = texto.replace("\r\n", "\n").replace("\x02", "").replace("\x03", "").split("\n")
        self.arbol = bloques(self.lineas)
        self.ejemplo = False
        if tipo == "ejercicio":
            self._estructura_ejercicio()
        self.titulo, sl, self.toc = "", Slugger(), []
        self._ids(self.arbol, sl)
        self.anclas = set(sl.vistos)

    def _estructura_ejercicio(self):
        """El ejercicio empieza por «Cómo funciona este ejercicio» y tiene un único «Ejemplo resuelto» de nivel 2, cuyo
        contenido (hasta el siguiente encabezado de nivel 1 o 2) queda en un bloque plegable que se abre al imprimir."""
        h2 = secciones_n2(self.lineas)
        if not h2 or not RX_MECANICA.match(h2[0][1]) or sum(1 for _, t in h2 if RX_MECANICA.match(t)) != 1:
            self.error("el ejercicio debe empezar con una única sección de nivel 2 «Cómo funciona este ejercicio» (la mecánica)")
        if sum(1 for _, t in h2 if RX_EJEMPLO.match(t)) != 1:
            self.error("el ejercicio debe tener una única sección de nivel 2 «Ejemplo resuelto»")
            return
        k = next(x for x, b in enumerate(self.arbol) if b[0] == "h" and b[1] == 2 and RX_EJEMPLO.match(texto_plano(b[2])))
        j = next((x for x in range(k + 1, len(self.arbol)) if self.arbol[x][0] == "h" and self.arbol[x][1] <= 2), len(self.arbol))
        contenido = self.arbol[k + 1:j]
        while contenido and contenido[-1][0] == "hr":
            contenido = contenido[:-1]
        if not contenido:
            self.error("la sección «Ejemplo resuelto» está vacía")
            return
        self.arbol[k + 1:j] = [("details", RESUMEN_EJEMPLO, contenido, False, "ejemplo")]
        self.ejemplo = True

    def _ids(self, arbol, sl):
        for k, b in enumerate(arbol):
            if b[0] == "h":
                id_ = sl(texto_plano(b[2]))
                arbol[k] = ("h", b[1], b[2], id_)
                if b[1] == 1 and not self.titulo:
                    self.titulo = texto_plano(b[2])
                elif b[1] in (2, 3):
                    self.toc.append((b[1], id_, texto_plano(b[2])))
            elif b[0] == "quote":
                self._ids(b[1], sl)
            elif b[0] == "details":
                self._ids(b[2], sl)
            elif b[0] == "list":
                for _, hijos in b[4]:
                    self._ids(hijos, sl)

    def error(self, msg):
        self.errores.append(msg)

    def aviso(self, msg):
        self.avisos.append(msg)

    def mermaid(self, arbol=None):
        res = []
        for b in self.arbol if arbol is None else arbol:
            if b[0] == "code" and b[1] == "mermaid":
                res.append(b[2])
            elif b[0] == "quote":
                res += self.mermaid(b[1])
            elif b[0] == "details":
                res += self.mermaid(b[2])
            elif b[0] == "list":
                for _, hijos in b[4]:
                    res += self.mermaid(hijos)
        return res


class Conjunto:
    """Documentos convertidos y su mapa fuente → salida (para reescribir enlaces)."""

    def __init__(self):
        self.docs = []
        self.mapa = {}          # fuente_rel → {tipo: Documento}

    def agregar(self, d):
        self.docs.append(d)
        if d.fuente_rel:
            self.mapa.setdefault(d.fuente_rel, {})[d.tipo] = d


def caso_de_ruta(rel):
    m = re.match(r"^docs/webinar/(E2E-\d+)(?:/|$)", rel or "")
    return m.group(1) if m else None


# ====================================================================== render
class Render:
    def __init__(self, doc, conjunto, svgs, sin_mermaid):
        self.d, self.c, self.svgs, self.sin_mermaid = doc, conjunto, svgs, sin_mermaid
        self.primer_h1 = True

    # ---------------------------------------------------------------- enlaces e imágenes
    def href_relativo(self, destino_rel, ancla=""):
        r = os.path.relpath(destino_rel, os.path.dirname(self.d.salida_rel) or ".").replace(os.sep, "/")
        return r + (f"#{ancla}" if ancla else "")

    def enlace(self, href, texto_html, texto_md):
        """(url, texto) o (None, texto) si el enlace no se puede resolver (se registra el error)."""
        d = self.d
        if href.startswith("#"):
            ancla = unquote(href[1:])
            if ancla not in d.anclas:
                d.error(f"enlace roto: {href} (no hay un encabezado con esa ancla en el documento)")
                return None, texto_html
            return href, texto_html
        if re.match(r"^(https?:|mailto:)", href, re.I):
            return href, texto_html
        if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I):
            d.error(f"enlace con esquema no permitido: {href}")
            return None, texto_html
        ruta, _, ancla = href.partition("#")
        ancla = unquote(ancla)
        destino = (d.fuente.parent / unquote(ruta)).resolve() if ruta else d.fuente
        if not destino.exists():
            d.error(f"enlace roto: {href} (no existe {destino})")
            return None, texto_html
        rel = rel_repo(destino)
        if rel is None:     # fuera del repositorio (por ejemplo, un Markdown suelto): solo la ruta, sin enlace
            return None, texto_html + (f' <span class="ruta">({e(href)})</span>' if texto_md.strip("`") != href else "")
        nombre_txt = texto_md.strip().strip("`")
        if destino.is_dir():
            caso = caso_de_ruta(rel + "/")
            if caso and rel.count("/") == 2:
                return self.href_relativo(f"{WEB}/index.html", caso), texto_html
            return url_github(rel, carpeta=True), texto_html
        if rel in self.c.mapa:
            docs = self.c.mapa[rel]
            obj = next(iter(docs.values()))
            if ancla and ancla not in obj.anclas:
                d.error(f"enlace roto: {href} (no hay un encabezado con el ancla «{ancla}» en {obj.salida_rel})")
                return None, texto_html
            if obj is d:
                return (f"#{ancla}" if ancla else "#"), texto_html
            nuevo = texto_html
            if nombre_txt == destino.name:
                nuevo = e(Path(obj.salida_rel).name) if not texto_md.strip().startswith("`") else f"<code>{e(Path(obj.salida_rel).name)}</code>"
            return self.href_relativo(obj.salida_rel, ancla), nuevo
        caso = caso_de_ruta(rel)
        if caso and destino.name == "diapositivas.json":
            html_d = f"{WEB}/{caso}/{caso}-diapositivas.html"
            if not (RAIZ / html_d).is_file():
                d.error(f"enlace a {rel}: falta {html_d} (generalo con scripts/webinar/generar.py)")
                return None, texto_html
            nuevo = e(f"{caso}-diapositivas.html") if nombre_txt == "diapositivas.json" else texto_html
            if texto_md.strip().startswith("`") and nombre_txt == "diapositivas.json":
                nuevo = f"<code>{nuevo}</code>"
            return self.href_relativo(html_d), nuevo
        if ancla and destino.suffix == ".md" and ancla not in anclas_md(destino.read_text(encoding="utf-8")):
            d.error(f"enlace roto: {href} (no hay un encabezado con el ancla «{ancla}» en {rel})")
            return None, texto_html
        return url_github(rel, ancla=ancla), texto_html

    def imagen(self, alt, src, figura=False):
        d = self.d
        if re.match(r"^[a-z][a-z0-9+.-]*:", src, re.I):
            d.error(f"imagen externa no permitida (el HTML debe ser autocontenido): {src}")
            return f'<span class="falta">[imagen: {e(alt)}]</span>'
        ruta = (d.fuente.parent / unquote(src)).resolve()
        if not ruta.is_file():
            d.error(f"imagen inexistente: {src} (se busca en {ruta})")
            return f'<span class="falta">[imagen: {e(alt)}]</span>'
        tipo = MIME.get(ruta.suffix.lower())
        if not tipo:
            d.error(f"imagen con formato no admitido: {src} (PNG, JPEG, GIF, SVG o WebP)")
            return f'<span class="falta">[imagen: {e(alt)}]</span>'
        uri = f"data:{tipo};base64," + base64.b64encode(ruta.read_bytes()).decode()
        tam = G.tam_imagen(str(ruta)) if tipo in ("image/png", "image/jpeg") else None
        dim = f' width="{tam[0]}" height="{tam[1]}"' if tam else ""
        img = f'<img src="{uri}" alt="{e(alt)}"{dim}>'
        if figura:
            return f'<button type="button" class="zoom" title="Ampliar imagen" aria-label="Ampliar imagen: {e(alt)}">{img}</button>'
        return img

    # ---------------------------------------------------------------- en línea
    def inline(self, texto):
        store = []

        def ph(s):
            store.append(s)
            return f"\x02{len(store) - 1}\x03"

        def codigo(m):
            c = m.group(2).replace("\n", " ")
            if len(c) > 2 and c[0] == " " and c[-1] == " " and c.strip():
                c = c[1:-1]
            return ph(f"<code>{e(c)}</code>")

        t = re.sub(r"(`+)(.+?)(?<!`)\1(?!`)", codigo, texto, flags=re.S)
        t = re.sub(r"( {2,}|\\)\n", lambda m: ph("<br>") + "\n", t)
        t = re.sub(r"\\([!-/:-@\[-`{-~])", lambda m: ph(e(m.group(1))), t)
        t = re.sub(r"!\[([^\]]*)\]\(\s*<?([^\s)>]+)>?(?:\s+\"[^\"]*\")?\s*\)",
                   lambda m: ph(self.imagen(texto_plano(m.group(1)), m.group(2))), t)

        def link(m):
            txt_html = self.resto(m.group(1), store)
            url, txt = self.enlace(m.group(2), txt_html, self.restaurar(m.group(1), store, plano=True))
            if url is None:
                return ph(txt)
            ext = url.startswith(REPO_URL + "/")
            extra = ' class="ext" title="Abre el archivo en GitHub"' if ext else ""
            return ph(f'<a href="{e(url)}"{extra}>{txt}</a>')
        t = re.sub(r"\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?([^\s)>]*)>?(?:\s+\"[^\"]*\")?\s*\)", link, t)
        t = re.sub(r"<(https?://[^\s<>]+)>", lambda m: ph(f'<a href="{e(m.group(1))}">{e(m.group(1))}</a>'), t)
        t = re.sub(r"<(/?)(br|sub|sup|kbd)\s*/?>", lambda m: ph(f"<{m.group(1)}{m.group(2).lower()}>"), t, flags=re.I)
        return self.restaurar(self.resto(t, store), store)

    @staticmethod
    def resto(t, store):
        t = e(t, quote=False)
        t = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", t, flags=re.S)
        t = re.sub(r"(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)", r"<strong>\1</strong>", t, flags=re.S)
        t = re.sub(r"(?<![\w*])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])", r"<em>\1</em>", t, flags=re.S)
        t = re.sub(r"(?<![\w_])_(?=[^\s_])(.+?)(?<=[^\s_])_(?![\w_])", r"<em>\1</em>", t, flags=re.S)
        return t

    @staticmethod
    def restaurar(t, store, plano=False):
        for _ in range(8):
            if "\x02" not in t:
                break
            t = re.sub(r"\x02(\d+)\x03", lambda m: store[int(m.group(1))], t)
        return re.sub(r"<[^>]+>", "", html.unescape(t)) if plano else t

    # ---------------------------------------------------------------- bloques
    def bloques(self, arbol, apretada=False):
        return "\n".join(self.bloque(b, apretada) for b in arbol)

    def bloque(self, b, apretada=False):
        t = b[0]
        if t == "h":
            nivel, md, id_ = b[1], b[2], b[3]
            if nivel == 1 and self.primer_h1:
                self.primer_h1 = False
                return ""
            return (f'<h{nivel} id="{e(id_)}">{self.inline(md)}'
                    f'<a class="ancla" href="#{e(id_)}" aria-label="Enlace a esta sección">#</a></h{nivel}>')
        if t == "p":
            return self.inline(b[1]) if apretada else f"<p>{self.inline(b[1])}</p>"
        if t == "fig":
            m = re.match(r"^\s*!\[([^\]]*)\]\(\s*<?([^\s)>]+)>?", b[1])
            pie = f"<figcaption>{self.inline(b[2])}</figcaption>" if b[2].strip() else ""
            return f'<figure class="img">{self.imagen(texto_plano(m.group(1)), m.group(2), figura=True)}{pie}</figure>'
        if t == "code":
            lang, codigo = b[1], b[2]
            if lang == "mermaid":
                return self.mermaid(codigo)
            cls = f' class="language-{e(lang)}"' if lang else ""
            return (f'<div class="codigo"><pre><code{cls}>{e(codigo)}</code></pre>'
                    '<button type="button" class="copiar" title="Copiar al portapapeles">Copiar</button></div>')
        if t == "hr":
            return "<hr>"
        if t == "table":
            alin, cab, filas = b[1], b[2], b[3]
            st = [f' style="text-align:{a}"' if a else "" for a in alin]
            th = "".join(f"<th{st[k]}>{self.inline(x)}</th>" for k, x in enumerate(cab))
            tb = "".join("<tr>" + "".join(f"<td{st[k]}>{self.inline(x)}</td>" for k, x in enumerate(f)) + "</tr>" for f in filas)
            return f'<div class="tabla"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'
        if t == "quote":
            return f"<blockquote>{self.bloques(b[1])}</blockquote>"
        if t == "details":
            cls = "desplegable" + (f" {b[4]}" if len(b) > 4 else "")
            return (f'<details class="{cls}"{" open" if b[3] else ""}><summary>{self.inline(b[1])}</summary>'
                    f'<div class="det">{self.bloques(b[2])}</div></details>')
        if t == "list":
            ordenada, inicio, suelta, items = b[1], b[2], b[3], b[4]
            lis = []
            for tarea, hijos in items:
                caja, cls_li = "", ""
                if tarea is not None:
                    caja = f'<input type="checkbox" class="caja"{" checked" if tarea else ""} aria-label="Marcar">'
                    cls_li = ' class="tarea"'
                lis.append(f"<li{cls_li}>{caja}{self.bloques(hijos, apretada=not suelta)}</li>")
            tag = "ol" if ordenada else "ul"
            ini = f' start="{inicio}"' if ordenada and inicio != 1 else ""
            cls = ' class="tareas"' if any(x[0] is not None for x in items) else ""
            return f"<{tag}{ini}{cls}>" + "".join(lis) + f"</{tag}>"
        return ""

    def mermaid(self, codigo):
        fuente = (f'<details class="fuente-mermaid"><summary>Código Mermaid (respaldo)</summary>'
                  f'<pre><code class="language-mermaid">{e(codigo)}</code></pre></details>')
        if self.sin_mermaid:
            self.d.aviso("bloque Mermaid sin dibujar (--sin-mermaid)")
            return f'<figure class="mermaid sin-dibujo"><figcaption>Diagrama Mermaid sin dibujar</figcaption>{fuente}</figure>'
        svg, err = self.svgs.get(codigo, (None, "no se renderizó"))
        if err:
            linea = next((k + 1 for k, l in enumerate(self.d.lineas) if l.strip() == codigo.split("\n", 1)[0].strip()), "?")
            self.d.error(f"Mermaid que no renderiza (cerca de la línea {linea}): {err}")
            return f'<figure class="mermaid sin-dibujo">{fuente}</figure>'
        return f'<figure class="mermaid"><div class="svg">{svg}</div>{fuente}</figure>'


# ====================================================================== página
CSS_DOC = r"""
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:72px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--page);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.55;font-size:16px}
a{color:var(--accent)}
code{font-family:"Courier New",monospace;font-size:.92em;background:var(--soft);padding:.05em .3em;border-radius:4px;overflow-wrap:anywhere}
.barra{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;padding:10px 16px;background:var(--surface);
border-bottom:1px solid var(--line)}
.barra .marca{font-weight:700;color:var(--title-ink);text-decoration:none;margin-right:6px}
.barra nav{display:flex;flex-wrap:wrap;gap:6px}
.barra nav a{padding:4px 10px;border-radius:8px;background:var(--soft);text-decoration:none;font-size:.9rem;color:var(--ink)}
.barra nav a:hover{background:var(--tint)}
.barra nav a[aria-current]{background:var(--blue);color:#fff}
.barra .ctl{display:flex;flex-wrap:wrap;gap:6px;margin-left:auto;align-items:center}
.barra button{font:inherit;font-size:.85rem;padding:4px 8px;border-radius:8px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.marco{display:grid;grid-template-columns:250px minmax(0,1fr);gap:32px;max-width:1240px;margin:0 auto;padding:24px 16px 48px}
.lateral{position:sticky;top:64px;align-self:start;max-height:calc(100vh - 80px);overflow:auto}
details.toc{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font-size:.88rem}
details.toc summary{cursor:pointer;font-weight:700;color:var(--title-ink)}
details.toc ol{list-style:none;margin:8px 0 0;padding:0}
details.toc li{margin:0}
details.toc li.n3{padding-left:14px;font-size:.95em}
details.toc a{display:block;padding:3px 6px;border-radius:6px;color:var(--ink);text-decoration:none;line-height:1.3}
details.toc a:hover{background:var(--soft)}
details.toc a.activo{background:var(--tint);color:var(--title-ink);font-weight:700}
main{min-width:0;max-width:920px}
.cab{position:relative;background:var(--dark);color:#fff;border-radius:14px;padding:26px clamp(18px,4vw,36px) 22px;box-shadow:var(--shadow);margin-bottom:22px}
.cab .logo{position:absolute;top:20px;right:20px;width:120px;height:50px;border:1px dashed #7f9bb8;border-radius:4px;display:grid;place-items:center;
font-size:.78rem;color:#a9bfd6}
.cab .logo.con-img{border:0}.cab .logo img{max-width:100%;max-height:100%}
.cab .kicker{margin:0 140px 6px 0;color:var(--sky);font-weight:700;font-size:.92rem}
.cab h1{margin:0 140px 10px 0;font-size:1.85rem;line-height:1.2}
.cab .meta{margin:0;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;color:#d6e4f0;font-size:.92rem}
.etiqueta{display:inline-block;background:var(--dark2);color:#fff;border-radius:999px;padding:3px 12px;font-weight:700}
.etiqueta.instr{background:var(--orange)}
.aviso-doc{margin:14px 0 0;background:var(--dark2);border-left:4px solid var(--sky);border-radius:8px;padding:10px 14px;color:#fff;font-size:.95rem}
.md{background:var(--surface);border-radius:14px;box-shadow:var(--shadow);padding:8px clamp(16px,4vw,40px) 28px;overflow-wrap:break-word}
.md>*:first-child{margin-top:18px}
.md h2{color:var(--title-ink);font-size:1.45rem;line-height:1.25;margin:2em 0 .6em;padding-bottom:.25em;border-bottom:2px solid var(--line)}
.md h3{color:var(--title-ink);font-size:1.15rem;margin:1.6em 0 .5em}
.md h4,.md h5,.md h6{font-size:1rem;margin:1.4em 0 .4em}
.md h2 .ancla,.md h3 .ancla,.md h4 .ancla{margin-left:.4em;color:var(--gray);text-decoration:none;opacity:0;font-weight:400}
.md h2:hover .ancla,.md h3:hover .ancla,.md h4:hover .ancla,.md .ancla:focus{opacity:1}
.md p{margin:.7em 0}
.md ul,.md ol{margin:.6em 0;padding-left:1.5em}
.md li{margin:.25em 0}
.md li>ul,.md li>ol{margin:.2em 0}
.md ul.tareas{list-style:none;padding-left:.4em}
.md li.tarea{position:relative;padding-left:1.8em}
.md li.tarea .caja{position:absolute;left:0;top:.2em;width:1.05em;height:1.05em;margin:0;accent-color:var(--blue)}
.md hr{border:0;border-top:1px solid var(--line);margin:2em 0}
.md blockquote{margin:1em 0;padding:.6em 1em;background:var(--tint);border-left:4px solid var(--accent);border-radius:0 8px 8px 0}
.md blockquote p{margin:.4em 0}
.md strong{color:var(--title-ink)}
.md .ruta{color:var(--gray)}
.md .falta{color:#b00020;font-weight:700}
.tabla{overflow-x:auto;margin:1em 0;border:1px solid var(--line);border-radius:8px}
.tabla table{width:100%;border-collapse:collapse;font-size:.92rem}
.tabla th{background:var(--navy);color:#fff;text-align:left;padding:.5em .65em;vertical-align:bottom}
.tabla th code{background:var(--dark2);color:#fff}
.tabla td{padding:.5em .65em;border-top:1px solid var(--line);vertical-align:top}
.tabla tbody tr:nth-child(even) td{background:var(--soft)}
.doc-ejercicio .tabla td:empty{height:2.6em;min-width:4em}
.codigo{position:relative;margin:.8em 0}
.codigo pre{margin:0;background:var(--code);color:var(--codefg);border-radius:8px;padding:14px 76px 14px 16px;font-family:"Courier New",monospace;
font-size:.9rem;line-height:1.45;white-space:pre-wrap;overflow-wrap:anywhere}
.codigo pre code{background:none;padding:0;color:inherit;font-size:1em}
.copiar{position:absolute;top:8px;right:8px;font:inherit;font-size:.75rem;border:0;border-radius:6px;padding:.3em .7em;background:var(--dark2);color:#fff;cursor:pointer}
figure{margin:1.1em 0}
figure.img{display:flex;flex-direction:column;align-items:center}
figure.img .zoom{all:unset;cursor:zoom-in;display:block;max-width:100%}
figure img{display:block;max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff}
figure figcaption{margin-top:.5em;font-size:.92rem;color:var(--gray);max-width:760px;text-align:center}
figure.mermaid .svg{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto;text-align:center}
figure.mermaid svg{max-width:100%;height:auto}
details.fuente-mermaid{margin-top:6px;font-size:.85rem}
details.fuente-mermaid summary{cursor:pointer;color:var(--gray)}
details.fuente-mermaid pre{background:var(--code);color:var(--codefg);border-radius:8px;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem}
details.desplegable{margin:1em 0;border:1px solid var(--line);border-radius:10px;padding:8px 14px;background:var(--soft)}
details.desplegable>summary{cursor:pointer;font-weight:700;color:var(--accent)}
details.ejemplo{border:1px solid var(--accent);border-left-width:5px;background:var(--tint);padding:10px 16px}
details.ejemplo>summary{font-size:1.05rem;padding:4px 0}
details.ejemplo[open]>summary{margin-bottom:.4em}
details.ejemplo .det>*:first-child{margin-top:.4em}
.pie-doc{margin:22px 4px 0;color:var(--gray);font-size:.85rem}
.fuente-imp{display:none}
dialog.visor{border:0;padding:0;background:transparent;max-width:96vw;max-height:94vh}
dialog.visor::backdrop{background:rgba(0,0,0,.8)}
dialog.visor img{display:block;max-width:96vw;height:auto;background:#fff;border-radius:6px}
dialog.visor .cerrar{position:fixed;top:10px;right:14px;font-size:1.1rem;padding:6px 12px;border-radius:8px;border:0;cursor:pointer}
/* índice del webinar */
.intro{background:var(--surface);border-radius:14px;box-shadow:var(--shadow);padding:6px clamp(16px,4vw,32px) 14px;margin-bottom:22px}
.casos{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,520px),1fr));gap:18px}
.caso{background:var(--surface);border-radius:14px;box-shadow:var(--shadow);padding:18px clamp(16px,3vw,26px)}
.caso h2{margin:0 0 .2em;color:var(--title-ink);font-size:1.25rem;line-height:1.25}
.caso .sub{margin:0 0 .6em;color:var(--warm);font-weight:700}
.caso .clases{margin:0 0 .8em;font-size:.9rem;color:var(--gray)}
.caso h3{margin:.9em 0 .4em;font-size:.95rem;color:var(--title-ink)}
.enlaces{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.enlaces a,.enlaces span{display:inline-block;padding:6px 12px;border-radius:8px;background:var(--tint);text-decoration:none;color:var(--ink);font-size:.92rem}
.enlaces a:hover{background:var(--soft);outline:1px solid var(--accent)}
.enlaces a.instr{background:var(--ortint)}
.enlaces small{color:var(--gray)}
.marco.sin-toc{grid-template-columns:minmax(0,1fr)}
.marco.sin-toc main{max-width:none}
@media (max-width:999px){
.marco{grid-template-columns:minmax(0,1fr);gap:16px;padding:16px 16px 40px}
.lateral{position:static;max-height:none}
.barra{position:static}
.barra .ctl{margin-left:0}
html{scroll-padding-top:8px}
}
@media (max-width:600px){
body{font-size:15px}
.cab{padding:18px 16px}
.cab .logo{position:static;width:96px;height:40px;margin-bottom:10px}
.cab .kicker,.cab h1{margin-right:0}
.cab h1{font-size:1.4rem}
.md{padding:4px 14px 20px}
.md h2{font-size:1.25rem}
.codigo pre{padding:12px 12px 12px 12px;padding-top:34px;font-size:.84rem}
.tabla table{font-size:.85rem}
details.ejemplo{padding:8px 10px;border-left-width:4px}
}
@media print{
:root,:root:not([data-theme="light"]),:root[data-theme="light"],:root[data-theme="dark"]{--page:#fff;--surface:#fff;--soft:#f4f6f8;--tint:#e9f1f8;
--ortint:#fbf1e6;--line:#d5d8de;--ink:#1d1b1c;--gray:#5d5d5d;--dark:#002855;--dark2:#173d66;--title-ink:#002855;--accent:#00629b;--warm:#b5651d;
--code:#f4f6f8;--codefg:#1d1b1c;color-scheme:light}
@page{size:A4;margin:15mm 14mm 16mm}
body{background:#fff;font-size:10pt;line-height:1.45}
.barra,.lateral,.copiar,.ancla,dialog.visor,details.fuente-mermaid,.enlaces small{display:none!important}
.marco{display:block;max-width:none;padding:0}
main{max-width:none}
.cab,.md,.caso,.intro{box-shadow:none;border-radius:0}
.cab{border-radius:6px;padding:14px 18px;margin-bottom:10px}
.md{padding:0}
.md h2{font-size:14pt;margin-top:1.4em}
.md h3{font-size:11.5pt}
h1,h2,h3,h4{break-after:avoid;page-break-after:avoid}
tr,figure,.codigo,blockquote,li,.caso{break-inside:avoid;page-break-inside:avoid}
thead{display:table-header-group}
.tabla{overflow:visible;border:0}
.tabla table{font-size:8.5pt}
.tabla td,.tabla th{padding:.3em .45em;overflow-wrap:break-word}
.tabla code,.md code{overflow-wrap:break-word}
p:has(+ .tabla),p:has(+ .codigo),p:has(+ figure){break-after:avoid;page-break-after:avoid}
.pie-doc{display:none}
.cab .fuente-imp{display:block;margin:8px 0 0;font-size:7.5pt;color:#d6e4f0}
.cab .fuente-imp code{background:none;color:inherit;padding:0}
figure.mermaid svg{max-height:240mm}
.codigo pre{border:1px solid #d5d8de;padding:8px 10px;font-size:8.5pt}
figure img{max-height:200mm;width:auto}
figure.mermaid .svg{border:0;padding:0}
a{color:inherit;text-decoration:none}
a.ext{text-decoration:underline dotted}
.cab,.cab *,.tabla th,.etiqueta,.aviso-doc,.md blockquote,.tabla tbody tr:nth-child(even) td{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.casos{display:block}.caso{margin-bottom:12px;border:1px solid #d5d8de;border-radius:6px}
details.ejemplo{border:0;padding:0;background:none}
details.ejemplo>summary{display:none}
}
@media print{details.ejemplo::details-content{content-visibility:visible}}
"""

JS_DOC = r"""
(function(){
  var raiz=document.documentElement;
  function guardar(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function leer(k){try{return localStorage.getItem(k)}catch(e){return null}}
  var tema=leer('webinar-tema'); if(tema==='light'||tema==='dark') raiz.setAttribute('data-theme',tema);
  var bTema=document.getElementById('b-tema');
  function rotTema(){var t=raiz.getAttribute('data-theme'); bTema.textContent=t==='dark'?'Tema: oscuro':(t==='light'?'Tema: claro':'Tema: automático');}
  if(bTema){rotTema(); bTema.addEventListener('click',function(){var t=raiz.getAttribute('data-theme'); var s=!t?'light':(t==='light'?'dark':'');
    if(s){raiz.setAttribute('data-theme',s)}else{raiz.removeAttribute('data-theme')} guardar('webinar-tema',s); rotTema();});}
  var bImp=document.getElementById('b-imprimir'); if(bImp) bImp.addEventListener('click',function(){window.print()});
  var toc=document.querySelector('details.toc');
  if(toc&&window.matchMedia){var mq=window.matchMedia('(min-width: 1000px)');
    function ajustar(){toc.open=mq.matches} ajustar();
    if(mq.addEventListener) mq.addEventListener('change',ajustar); else if(mq.addListener) mq.addListener(ajustar);
    toc.addEventListener('click',function(ev){if(ev.target.tagName==='A'&&!mq.matches) toc.open=false;});}
  var enl={}; [].forEach.call(document.querySelectorAll('details.toc a[href^="#"]'),function(a){enl[decodeURIComponent(a.getAttribute('href').slice(1))]=a});
  if('IntersectionObserver' in window&&toc){var obs=new IntersectionObserver(function(ents){ents.forEach(function(en){
      if(en.isIntersecting){var a=enl[en.target.id]; if(a){[].forEach.call(document.querySelectorAll('details.toc a.activo'),function(x){x.classList.remove('activo')}); a.classList.add('activo');}}});},
      {rootMargin:'0px 0px -70% 0px'});
    [].forEach.call(document.querySelectorAll('.md h2[id],.md h3[id]'),function(h){obs.observe(h)});}
  [].forEach.call(document.querySelectorAll('.codigo .copiar'),function(b){b.addEventListener('click',function(){
    var t=b.parentNode.querySelector('pre').textContent;
    if(navigator.clipboard){navigator.clipboard.writeText(t).then(function(){b.textContent='Copiado'; setTimeout(function(){b.textContent='Copiar'},1500)},function(){});}});});
  var visor=document.getElementById('visor');
  if(visor){var vimg=visor.querySelector('img');
    [].forEach.call(document.querySelectorAll('figure.img .zoom'),function(b){b.addEventListener('click',function(){
      var im=b.querySelector('img'); vimg.src=im.src; vimg.alt=im.alt; if(visor.showModal) visor.showModal();});});
    visor.addEventListener('click',function(){visor.close()});}
  function abrirHasta(id){var el=id&&document.getElementById(id); while(el){if(el.tagName==='DETAILS'&&!el.open) el.open=true; el=el.parentElement;}}
  function hashActual(){try{return decodeURIComponent(location.hash.slice(1))}catch(e){return ''}}
  [].forEach.call(document.querySelectorAll('a[href^="#"]'),function(a){a.addEventListener('click',function(){
    var h=a.getAttribute('href').slice(1); try{h=decodeURIComponent(h)}catch(e){} abrirHasta(h);});});
  window.addEventListener('hashchange',function(){abrirHasta(hashActual())}); if(location.hash) abrirHasta(hashActual());
  var abiertos=[];
  function abrirTodo(){[].forEach.call(document.querySelectorAll('details.desplegable:not([open])'),function(d){d.open=true; abiertos.push(d)});}
  function cerrarAbiertos(){abiertos.forEach(function(d){d.open=false}); abiertos=[];}
  window.addEventListener('beforeprint',abrirTodo);
  window.addEventListener('afterprint',cerrarAbiertos);
  if(window.matchMedia){var mp=window.matchMedia('print'); var alCambiar=function(e){if(e.matches) abrirTodo(); else cerrarAbiertos();};
    if(mp.addEventListener) mp.addEventListener('change',alCambiar); else if(mp.addListener) mp.addListener(alCambiar);}
})();
"""

PAGINA = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="pm-method {version} · scripts/webinar/documentos.py">
<title>{titulo}</title><style>{css}</style></head>
<body class="{clase_body}">
<header class="barra">
  <a class="marca" href="{indice}">{marca}</a>
  <nav aria-label="Material del caso">{nav}</nav>
  <div class="ctl"><button type="button" id="b-imprimir">Imprimir</button><button type="button" id="b-tema">Tema: automático</button></div>
</header>
<div class="marco{marco_cls}">
{lateral}<main>
<header class="cab">{logo}<p class="kicker">{kicker}</p><h1>{h1}</h1><p class="meta">{meta}</p>{aviso}<p class="fuente-imp">{pie}</p></header>
{cuerpo}
<footer class="pie-doc">{pie}</footer>
</main>
</div>
<dialog class="visor" id="visor"><button type="button" class="cerrar">Cerrar</button><img alt=""></dialog>
<script>{js}</script>
</body></html>
"""


def css_familia():
    tokens = G.CSS.split("*{box-sizing", 1)[0]
    if ":root{" not in tokens:
        raise SystemExit("ERROR: no se encontraron los tokens de color en scripts/webinar/generar.py (CSS)")
    return tokens + CSS_DOC


def logo_cab(logo):
    if logo:
        return f'<div class="logo con-img"><img src="{G.data_uri(str(logo))}" alt="Logo IEEE"></div>'
    return '<div class="logo" aria-label="Espacio reservado para el logo de IEEE">Logo IEEE</div>'


def nav_caso(caso, tipo_actual, existentes):
    """Material hermano del caso. Los documentos para asistentes (guía y ejercicio) no enlazan al guion."""
    items = [("diapositivas", f"{caso}-diapositivas.html", "Diapositivas"), ("guia", TIPOS["guia"]["archivo"].format(caso=caso), "Guía")]
    if tipo_actual in INSTRUCTOR:
        items += [("guion", TIPOS["guion"]["archivo"].format(caso=caso), "Guion")]
    items += [("ejercicio", TIPOS["ejercicio"]["archivo"].format(caso=caso), "Ejercicio")]
    out = []
    for clave, archivo, rot in items:
        if clave not in existentes:
            continue
        cur = ' aria-current="page"' if clave == tipo_actual else ""
        out.append(f'<a href="{e(archivo)}"{cur}>{e(rot)}</a>')
    return "".join(out)


def armar_documento(doc, conjunto, svgs, version, logo, sin_mermaid, existentes):
    r = Render(doc, conjunto, svgs, sin_mermaid)
    cuerpo = f'<article class="md">{r.bloques(doc.arbol)}</article>'
    info = TIPOS[doc.tipo]
    toc = "".join(f'<li class="n{n}"><a href="#{e(i)}">{e(t)}</a></li>' for n, i, t in doc.toc)
    lateral = (f'<aside class="lateral"><details class="toc" open><summary>Contenido</summary>'
               f'<nav aria-label="Contenido del documento"><ol>{toc}</ol></nav></details></aside>\n') if toc else ""
    instr = doc.tipo in INSTRUCTOR
    meta = (f'<span class="etiqueta{" instr" if instr else ""}">{e(info["nombre"])}</span>'
            f'<span>Para: {e(info["para"])}</span>')
    aviso = ""
    fuente = doc.fuente_rel or doc.fuente.name
    pie_fuente = f'<a href="{e(url_github(fuente))}" class="ext">{e(fuente)}</a>' if doc.fuente_rel else e(fuente)
    pie = (f"Fuente: {pie_fuente} · pm-method {e(version)} · {e(info['nombre'])} del caso {e(doc.caso)} · "
           "generado con <code>scripts/webinar/documentos.py</code>")
    return PAGINA.format(
        version=e(version), titulo=e(f"{doc.caso} · {info['nombre']} · {doc.titulo or doc.fuente.stem}"), css=css_familia(), js=JS_DOC,
        clase_body=f"doc doc-{doc.tipo}", indice="../index.html", marca=e(f"Webinar {doc.caso}"),
        nav=nav_caso(doc.caso, doc.tipo, existentes), marco_cls="" if toc else " sin-toc", lateral=lateral, logo=logo_cab(logo),
        kicker=e(f"Webinar {doc.caso} · {info['nombre']} · pm-method {version}"), h1=e(doc.titulo or doc.fuente.stem),
        meta=meta, aviso=aviso, cuerpo=cuerpo, pie=pie)


def armar_indice(casos, version, logo):
    """docs/webinar/index.html: los cinco casos con todo su material y para quién es cada archivo."""
    leyenda = [
        ("Ficha del taller (HTML y PPTX)", "posibles asistentes e interesados; quien organiza",
         "antes del taller, para difundirlo: el HTML se imprime como volante A4"),
        ("Diapositivas (HTML y PPTX)", "instructor (proyectar); el HTML también sirve para repartir", "en clase"),
        ("Guía paso a paso", "asistentes e instructor", "práctica individual, antes o después de clase"),
        ("Guion del instructor", "instructor", "preparar y dar la clase (agenda, mensajes, preguntas, plan B)"),
        ("Ejercicio", "asistentes e instructor",
         "cierre de cada clase; al final, plegado, un ejemplo resuelto con el escenario del caso para comparar después de intentarlo"),
    ]
    filas = "".join(f"<tr><td><strong>{e(a)}</strong></td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in leyenda)
    tarjetas = []
    for c in casos:
        caso = c["caso"]
        ruta = lambda k: e(f"{caso}/{TIPOS[k]['archivo'].format(caso=caso)}")
        diap = []
        for ext, rot in (("html", "Diapositivas (HTML)"), ("pptx", "Diapositivas (PPTX)")):
            if c["diapositivas"].get(ext):
                diap.append(f'<li><a href="{e(caso)}/{e(caso)}-diapositivas.{ext}">{rot}</a></li>')
            else:
                diap.append(f'<li><span>{rot}: sin generar</span></li>')
        ficha = []
        for ext, rot in (("html", "Ficha del taller (HTML, volante A4)"), ("pptx", "Ficha del taller (PPTX)")):
            if c["ficha"].get(ext):
                ficha.append(f'<li><a href="{e(caso)}/{e(caso)}-ficha.{ext}">{rot}</a></li>')
        clases = " · ".join(f"Clase {k['numero']}: {e(k['titulo'])} ({k['duracion_min']} min)" for k in c["clases"])
        tarjetas.append(
            f'<section class="caso" id="{e(caso)}"><h2>{e(caso)} · {e(c["titulo"])}</h2>'
            + (f'<p class="sub">{e(c["subtitulo"])}</p>' if c["subtitulo"] else "")
            + (f'<p class="clases">{clases}</p>' if clases else "")
            + ('<h3>Para difundir</h3><ul class="enlaces">' + "".join(ficha) + "</ul>" if ficha else "")
            + '<h3>En clase</h3><ul class="enlaces">' + "".join(diap) + "</ul>"
            + '<h3>Para asistentes</h3><ul class="enlaces">'
            + f'<li><a href="{ruta("guia")}">Guía paso a paso</a></li>'
            + f'<li><a href="{ruta("ejercicio")}">Ejercicio <small>(con ejemplo resuelto plegado)</small></a></li></ul>'
            + '<h3>Para el instructor</h3><ul class="enlaces">'
            + f'<li><a class="instr" href="{ruta("guion")}">Guion del instructor</a></li></ul></section>')
    cuerpo = (
        '<section class="intro"><p>Material del webinar de pm-method por caso de punta a punta (E2E): dos clases de 90 '
        'minutos por caso. Todos los archivos son HTML de un solo archivo (sin conexión, imprimibles en A4, con tema claro '
        'u oscuro) salvo los PPTX de la ficha y de las diapositivas.</p><div class="tabla"><table><thead><tr><th>Material</th><th>Para quién</th>'
        f'<th>Cuándo se usa</th></tr></thead><tbody>{filas}</tbody></table></div></section>'
        f'<div class="casos">{"".join(tarjetas)}</div>')
    nav = "".join(f'<a href="#{e(c["caso"])}">{e(c["caso"])}</a>' for c in casos)
    pie = (f"pm-method {e(version)} · generado con <code>scripts/webinar/documentos.py --todos</code> desde "
           f'<a class="ext" href="{e(url_github("docs/webinar", carpeta=True))}">docs/webinar/</a> y '
           f'<a class="ext" href="{e(url_github("docs/guias", carpeta=True))}">docs/guias/</a>')
    return PAGINA.format(
        version=e(version), titulo=e(f"Webinar pm-method {version} · material por caso"), css=css_familia(), js=JS_DOC,
        clase_body="doc doc-indice", indice="#", marca="Webinar pm-method", nav=nav, marco_cls=" sin-toc", lateral="",
        logo=logo_cab(logo), kicker=e(f"Webinar · pm-method {version}"), h1="Material del webinar por caso",
        meta=f'<span class="etiqueta">Índice</span><span>{len(casos)} casos · ficha del taller, diapositivas, guía, guion y ejercicio</span>',
        aviso="", cuerpo=cuerpo, pie=pie)


# ====================================================================== principal
def documentos_del_caso(carpeta):
    """[(tipo, fuente)] del caso o (None, error)."""
    caso = carpeta.name
    guias = sorted(glob.glob(str(RAIZ / "docs" / "guias" / f"{caso}-*.md")))
    faltan = []
    if len(guias) != 1:
        faltan.append(f"se esperaba una guía docs/guias/{caso}-*.md y hay {len(guias)}")
    for nombre in ("guion-instructor.md", "ejercicio.md"):
        if not (carpeta / nombre).is_file():
            faltan.append(f"falta {carpeta / nombre}")
    if faltan:
        return None, faltan
    return [("guia", Path(guias[0])), ("guion", carpeta / "guion-instructor.md"), ("ejercicio", carpeta / "ejercicio.md")], []


def datos_indice(carpeta):
    caso = carpeta.name
    info = {"caso": caso, "titulo": "", "subtitulo": "", "clases": [], "diapositivas": {}, "ficha": {}}
    try:
        j = json.loads((carpeta / "diapositivas.json").read_text(encoding="utf-8"))
        info.update(titulo=j.get("titulo", ""), subtitulo=j.get("subtitulo", ""),
                    clases=[c for c in j.get("clases", []) if isinstance(c, dict) and "numero" in c])
    except (OSError, ValueError):
        pass
    for ext in ("html", "pptx"):
        info["diapositivas"][ext] = (carpeta / f"{caso}-diapositivas.{ext}").is_file()
        info["ficha"][ext] = (carpeta / f"{caso}-ficha.{ext}").is_file()
    return info


def escribir(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Convierte la guía, el guion y el ejercicio de cada caso del webinar en HTML autocontenido.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--caso", help="carpeta del caso, por ejemplo docs/webinar/E2E-1")
    g.add_argument("--todos", action="store_true", help="los cinco casos docs/webinar/E2E-*/ y docs/webinar/index.html")
    g.add_argument("--archivo", help="convertir un Markdown suelto (con --tipo y --salida)")
    ap.add_argument("--tipo", choices=sorted(TIPOS), help="con --archivo: guia, guion o ejercicio")
    ap.add_argument("--salida", help="carpeta de salida (por defecto, docs/webinar/); repite la estructura E2E-N/ e index.html")
    ap.add_argument("--logo", help="PNG del logo de IEEE (opcional; sin él se deja un recuadro rotulado «Logo IEEE»)")
    ap.add_argument("--validar", action="store_true", help="valida imágenes, enlaces, secciones y Mermaid sin escribir archivos")
    ap.add_argument("--sin-mermaid", action="store_true", help="no dibujar los bloques Mermaid (quedan como código, con aviso)")
    a = ap.parse_args(argv)
    if a.archivo and (not a.tipo or not a.salida):
        ap.error("--archivo necesita --tipo y --salida")
    logo = None
    if a.logo:
        logo = Path(a.logo).resolve()
        if not logo.is_file() or logo.suffix.lower() != ".png":
            print(f"ERROR: --logo debe ser un archivo PNG existente: {a.logo}")
            return 2
    version = G.version_paquete()
    conjunto, grupos = Conjunto(), []       # grupos: (nombre, [docs], errores previos)
    if a.archivo:
        fuente = Path(a.archivo).resolve()
        if not fuente.is_file():
            print(f"ERROR: no existe {a.archivo}")
            return 1
        m = re.search(r"E2E-\d+", str(fuente))
        caso = m.group(0) if m else "E2E"
        d = Documento(caso, a.tipo, fuente, f"{WEB}/{caso}/" + TIPOS[a.tipo]["archivo"].format(caso=caso))
        conjunto.agregar(d)
        grupos.append((fuente.name, [d], []))
    else:
        if a.todos:
            carpetas = sorted({Path(p).parent for p in glob.glob(str(RAIZ / WEB / "E2E-*" / "ejercicio.md"))},
                              key=lambda p: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", p.name)])
            if not carpetas:
                print("No hay casos en docs/webinar/E2E-*/")
                return 1
        else:
            carpetas = [Path(a.caso).resolve()]
        for carpeta in carpetas:
            if rel_repo(carpeta) is None or not re.match(r"^docs/webinar/E2E-\d+$", rel_repo(carpeta)):
                grupos.append((carpeta.name, [], [f"la carpeta del caso debe ser docs/webinar/E2E-N del repositorio: {carpeta}"]))
                continue
            lista_docs, errs = documentos_del_caso(carpeta)
            docs = []
            for tipo, fuente in lista_docs or []:
                d = Documento(carpeta.name, tipo, fuente, f"{WEB}/{carpeta.name}/" + TIPOS[tipo]["archivo"].format(caso=carpeta.name))
                conjunto.agregar(d)
                docs.append(d)
            grupos.append((carpeta.name, docs, errs))
    # Mermaid: todos los bloques distintos, en paralelo
    codigos = sorted({c for d in conjunto.docs for c in d.mermaid()})
    svgs = {} if a.sin_mermaid else renderizar_mermaid(codigos)
    raiz_salida = Path(a.salida).resolve() if a.salida else RAIZ / WEB
    oks, total_docs = [], 0
    for nombre, docs, errs in grupos:
        print(f"== {nombre}")
        html_docs = {}
        existentes = {d.tipo for d in docs}
        if docs and (RAIZ / WEB / docs[0].caso / f"{docs[0].caso}-diapositivas.html").is_file():
            existentes.add("diapositivas")
        elif docs and not a.archivo:
            print(f"  AVISO: falta {WEB}/{docs[0].caso}/{docs[0].caso}-diapositivas.html (generalo con generar.py); la barra no lo enlaza")
        for d in docs:
            html_docs[d] = armar_documento(d, conjunto, svgs, version, logo, a.sin_mermaid, existentes)
        for er in errs:
            print(f"  ERROR: {er}")
        n_err = len(errs)
        for d in docs:
            for av in d.avisos:
                print(f"  AVISO: {d.fuente_rel or d.fuente.name} ({d.tipo}): {av}")
            for er in d.errores:
                print(f"  ERROR: {d.fuente_rel or d.fuente.name} ({d.tipo}): {er}")
            n_err += len(d.errores)
        # el ejercicio lleva el ejemplo resuelto dentro del bloque plegable
        for d in docs:
            if d.tipo == "ejercicio" and d.ejemplo and not d.errores:
                if '<details class="desplegable ejemplo"><summary>' + e(RESUMEN_EJEMPLO) not in html_docs[d]:
                    print(f"  ERROR: {d.fuente_rel or d.fuente.name}: el ejemplo resuelto no quedó dentro del bloque plegable")
                    n_err += 1
                else:
                    print(f"  ejemplo resuelto plegable: {Path(d.salida_rel).name}")
        if n_err:
            print(f"  {n_err} error(es): no se escribe {nombre}")
            oks.append(False)
            continue
        for d in docs:
            n_m = len(d.mermaid())
            if a.validar:
                print(f"  válido: {Path(d.salida_rel).name} ({len(d.toc)} secciones, {n_m} diagrama(s) Mermaid)")
                continue
            if a.archivo:
                destino = raiz_salida / Path(d.salida_rel).name
            else:
                destino = raiz_salida / Path(d.salida_rel).relative_to(WEB)
            escribir(destino, html_docs[d])
            total_docs += 1
            print(f"  HTML: {destino} ({len(d.toc)} secciones, {n_m} diagrama(s) Mermaid, {destino.stat().st_size // 1024} KB)")
        if not a.validar and not a.archivo and a.salida and docs:
            caso = docs[0].caso
            for nombre in (f"{caso}-diapositivas.html", f"{caso}-diapositivas.pptx", f"{caso}-ficha.html", f"{caso}-ficha.pptx"):
                src = RAIZ / WEB / caso / nombre
                if src.is_file():
                    shutil.copy2(src, raiz_salida / caso / src.name)
                    print(f"  copia: {raiz_salida / caso / src.name}")
        oks.append(True)
    if a.todos and all(oks):
        casos = [datos_indice(RAIZ / WEB / n) for n, _, _ in grupos]
        if not a.validar:
            destino = raiz_salida / "index.html"
            escribir(destino, armar_indice(casos, version, logo))
            print(f"== índice\n  HTML: {destino} ({len(casos)} casos)")
    print(f"Resultado: {sum(oks)}/{len(oks)} " + ("documento(s)" if a.archivo else "caso(s)") + " sin errores"
          + (f" · {total_docs} archivo(s) HTML escritos" if not a.validar else " · validación (no se escribió nada)"))
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
