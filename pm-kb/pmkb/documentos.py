"""Documentos HTML del proyecto en el portal (pestaña Artefactos › Documentos). docs/PM-KB.md §11.1 y SEGURIDAD §14.

Muestra los HTML que dejan en la carpeta las skills externas de pm-visuales (archify, diagram-design, visual-explainer,
SPEC §1.10.14) y los de pm-method, siempre en un `iframe` aislado: el servicio los entrega con su propia CSP (`sandbox`,
sin acceso al origen del portal, sin red) y solo si están dentro de la carpeta indexada y son documentos visibles para
el token. No ejecuta código de esas skills ni reescribe sus archivos: solo los lee.

Reconocimiento (heurístico, solo para la etiqueta): archify escribe `<meta name="generator" content="archify …">` y deja
al lado `<nombre>.candidate.json`, `.finalize.json` y otros recibos; visual-explainer renderiza `<nombre>.src.html` en
`<nombre>.html` con el kit en línea (`data-ve-kit`); diagram-design copia su plantilla (`.diagram-container`) y, si se le
pide exportar, deja `<nombre>.svg` y `<nombre>.png` al lado. Para los diagramas se ofrecen el SVG y el PNG con el mismo
nombre que existan en la misma carpeta.
"""
import os, re
from pathlib import Path

CABECERA = 96 * 1024
TIPOS = {".html": "text/html; charset=utf-8", ".htm": "text/html; charset=utf-8", ".svg": "image/svg+xml",
         ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
MAX_BYTES = 25 * 1024 * 1024
DIR_TABLEROS = "03-control/reportes/tableros/"
_SCRIPT = re.compile(r"<script\b(?![^>]*\btype\s*=\s*[\"']?(?:application/(?:ld\+)?json|text/template)\b)[^>]*>", re.I)
_GENERADOR = re.compile(r"<meta\s+name=[\"']generator[\"']\s+content=[\"']([^\"']{1,80})[\"']", re.I)


def dentro(raiz, ruta):
    """Ruta absoluta real de `ruta` si es un archivo dentro de la carpeta indexada `raiz` (sin salir por `..` ni por un
    enlace simbólico); None si no."""
    if not raiz or not ruta or "\x00" in ruta or ruta.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", ruta):
        return None
    base = os.path.realpath(raiz)
    p = os.path.realpath(os.path.join(base, ruta))
    try:
        if os.path.commonpath([base, p]) != base:
            return None
    except ValueError:
        return None
    return p if os.path.isfile(p) else None


def _cabecera(p):
    try:
        with open(p, "rb") as f:
            return f.read(CABECERA).decode("utf-8", "replace")
    except OSError:
        return ""


def _todo(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def con_scripts(p):
    """True si el HTML tiene un <script> ejecutable (no los bloques de datos JSON): el marco necesita `allow-scripts`."""
    return bool(_SCRIPT.search(_todo(p)))


def motor(p):
    """(motor, detalle): archify | visual-explainer | diagram-design | pm-method | html, por las marcas del archivo y los
    subproductos con el mismo nombre en la carpeta."""
    cab = _cabecera(p)
    base = os.path.splitext(p)[0]
    gen = _GENERADOR.search(cab)
    if (gen and gen.group(1).lower().startswith("archify")) or any(os.path.exists(base + x) for x in (".candidate.json", ".finalize.json", ".delivery.json")):
        return "archify", gen.group(1) if gen else ""
    if "data-ve-kit" in cab or os.path.exists(base + ".src.html"):
        return "visual-explainer", ""
    if "diagram-container" in cab and "--color-paper" in cab:
        return "diagram-design", ""
    if gen and gen.group(1).startswith("pm-method"):
        return "pm-method", gen.group(1)
    return "html", gen.group(1) if gen else ""


def hermanos(raiz, fuente):
    """SVG y PNG con el mismo nombre en la misma carpeta (exportaciones de un diagrama), relativos a la raíz."""
    stem = os.path.splitext(fuente)[0]
    out = []
    for ext in (".svg", ".png"):
        if dentro(raiz, stem + ext):
            out.append(stem + ext)
    return out


def listar(raiz, docs):
    """Documentos HTML para la pestaña: los de `docs` (versión vigente, visibles) salvo las fuentes de visual-explainer
    (`.src.html`) y las instantáneas del tablero (están en la pestaña Tableros), con el motor, si necesita scripts, el
    tamaño y sus SVG/PNG."""
    out = []
    for d in docs:
        f = d["fuente"]
        if f.lower().endswith(".src.html") or ("/" + DIR_TABLEROS) in ("/" + f):
            continue
        p = dentro(raiz, f)
        if not p:
            out.append({**d, "existe": False, "motor": "", "scripts": False, "bytes": 0, "exportaciones": []})
            continue
        m, det = motor(p)
        out.append({**d, "existe": True, "motor": m, "generador": det, "scripts": con_scripts(p), "bytes": os.path.getsize(p),
                    "exportaciones": hermanos(raiz, f), "carpeta": os.path.dirname(f)})
    orden = {"archify": 0, "diagram-design": 1, "visual-explainer": 2, "pm-method": 3, "html": 4, "": 5}
    out.sort(key=lambda x: (orden.get(x["motor"], 5), x["fuente"]))
    return out


def csp(scripts):
    """CSP del documento servido: aislado (`sandbox`: origen opaco, sin cookies ni acceso al portal), sin red ni
    formularios, enmarcable solo por el portal; con scripts en línea solo si el documento los necesita para verse."""
    return ("sandbox" + (" allow-scripts" if scripts else "") + "; default-src 'none'; "
            + ("script-src 'unsafe-inline'; " if scripts else "script-src 'none'; ")
            + "style-src 'unsafe-inline'; img-src data: blob:; font-src data:; media-src data: blob:; connect-src 'none'; "
            "form-action 'none'; base-uri 'none'; frame-ancestors 'self'")


def nombre_descarga(ruta):
    """Nombre de archivo seguro para Content-Disposition (ASCII y su forma RFC 5987 con UTF-8)."""
    from urllib.parse import quote
    n = os.path.basename(ruta) or "documento"
    ascii_ = re.sub(r"[^A-Za-z0-9._-]+", "_", n) or "documento"
    return f"attachment; filename=\"{ascii_}\"; filename*=UTF-8''{quote(n)}"
