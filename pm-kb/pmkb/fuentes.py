"""Lectura de la carpeta del proyecto → documentos y unidades citables (sin base de datos).

Unidad = el fragmento mínimo que se busca y se cita: una fila de un registro (su id de negocio), una sección de un
Markdown (por encabezado, partida en trozos de hasta MAX_SECCION caracteres), una diapositiva, una hoja, una ventana de
una transcripción o un objeto con `id` de un JSON. Cada unidad lleva fuente, rango (líneas, diapositiva o tiempo),
título, texto, circulación (`equipo` | `restringida`) y confianza (`gestion` | `externo`: transcripciones y correos
son evidencia de terceros, no instrucciones).

Exclusiones al construir (nunca llegan a la base):
- registros `preferencias` y `envios` y la carpeta `03-control/comunicaciones/` (datos y mensajes personales de
  interesados);
- de `stakeholders`, los datos de contacto (`correo`, `usuario_chat`) y, con `confidencial=si`, la valoración;
- `.bitacora.jsonl` (su historia se indexa aparte, ya sin valores sensibles), `.pm-bloqueo/`, `.git/`, `_bmad/`,
  `.bmad-core/`, `exportados/`, entornos virtuales y lo que diga `.pmkbignore` o `--excluir`.
La clave `integraciones` de `estado.json` tampoco se indexa (configuración de canales).
"""
import csv, email, email.policy, email.utils, fnmatch, hashlib, html.parser, io, json, os, re, sys
from pathlib import Path

RAIZ_PAQUETE = Path(__file__).resolve().parents[2]
_NUCLEO = RAIZ_PAQUETE / "skills" / "pm-estado-proyecto" / "scripts"
if str(_NUCLEO) not in sys.path:
    sys.path.insert(0, str(_NUCLEO))
import esquema as E  # noqa: E402  (REGISTROS: columnas y referencias declaradas)

MAX_SECCION = 1200
MAX_ARCHIVO = 25 * 1024 * 1024
VENTANA_TRANSCRIPCION = 6
OMITIR_DIRS = {".git", ".pm-bloqueo", "node_modules", "_bmad", ".bmad-core", "exportados", "__pycache__", ".venv",
               "venv", ".claude", ".pytest_cache", ".mypy_cache"}
OMITIR_ARCHIVOS = {".bitacora.jsonl", ".pmkbignore", ".gitignore", ".DS_Store"}
REGISTROS_EXCLUIDOS = {"preferencias", "envios"}
EXCLUIR_DEFECTO = ["03-control/comunicaciones", "*/03-control/comunicaciones"]   # mensajes a interesados (como envios)
CAMPOS_CONTACTO = {"correo", "usuario_chat"}
SENSIBLES_STK = {"poder", "interes", "actitud", "nivel_compromiso_actual", "nivel_compromiso_deseado", "expectativas",
                 "notas", "responsable_relacion", "estereotipo", "canal", "frecuencia"}
CAMPOS_PRIMERO = ["estado", "titulo", "evento", "decision", "decidido_por", "fecha_decision", "notas", "respuesta", "causa",
                  "efecto", "descripcion", "justificacion", "propietario"]     # lo que más pesa va antes (extractos); el estado, primero: sin él un extracto recortado parece abierto
CAMPOS_TITULO = ["titulo", "evento", "decision", "nombre", "leccion", "descripcion", "accion", "supuesto", "objetivo",
                 "requisito", "enunciado", "texto", "detalle"]
EXT_MD = {".md", ".markdown"}
EXT_TEXTO = {".txt"}
EXT_TRANS = {".srt", ".vtt"}
EXT_OFFICE = {".docx", ".pptx", ".xlsx", ".pdf"}
EXT_HTML = {".html", ".htm"}
EXT_CORREO = {".eml"}
EXT_DATOS = {".csv", ".json", ".yaml", ".yml"}
EXTERNO_RUTA = re.compile(r"(^|/)(03-control/(reuniones|fuentes)|transcripciones?)(/|$)|transcrip", re.I)


def sha(texto, n=None):
    h = hashlib.sha256(texto.encode("utf-8") if isinstance(texto, str) else texto).hexdigest()
    return h[:n] if n else h


def limpio(t):
    return re.sub(r"[ \t]+", " ", re.sub(r"\r\n?", "\n", t or "")).strip()


# ------------------------------------------------------------------ recorrido de la carpeta
def _patrones(raiz, excluir):
    pats = list(EXCLUIR_DEFECTO) + list(excluir or [])
    p = Path(raiz) / ".pmkbignore"
    if p.is_file():
        for l in p.read_text(encoding="utf-8").splitlines():
            l = l.strip()
            if l and not l.startswith("#"):
                pats.append(l.rstrip("/"))
    return pats


def _coincide(rel, pats):
    partes = rel.split("/")
    for p in pats:
        if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(partes[-1], p) or any(fnmatch.fnmatch("/".join(partes[:i]), p) for i in range(1, len(partes))):
            return True
    return False


def archivos(raiz, excluir=None):
    """Rutas relativas (con '/') de los archivos a indexar, en orden estable."""
    raiz = os.path.abspath(raiz)
    pats = _patrones(raiz, excluir)
    salida = []
    for d, dirs, fs in os.walk(raiz):
        dirs[:] = sorted(x for x in dirs if x not in OMITIR_DIRS and not _coincide(os.path.relpath(os.path.join(d, x), raiz).replace(os.sep, "/"), pats))
        for f in sorted(fs):
            if f in OMITIR_ARCHIVOS or f.startswith("~$"):
                continue
            rel = os.path.relpath(os.path.join(d, f), raiz).replace(os.sep, "/")
            if _coincide(rel, pats):
                continue
            salida.append(rel)
    return salida


def indexable(rel):
    """True si la extensión es de un formato que se indexa (§3.1)."""
    return Path(rel).suffix.lower() in EXT_MD | EXT_TEXTO | EXT_TRANS | EXT_OFFICE | EXT_HTML | EXT_CORREO | EXT_DATOS


def huella(raiz, excluir=None):
    """Huella barata de todo lo que se indexa (para `pm-kb vigilar`): ruta, tamaño y fecha de modificación de cada
    archivo indexable de la carpeta (con las mismas exclusiones que `indexar`: .pmkbignore, --excluir, carpetas
    omitidas), más las bitácoras `.bitacora.jsonl` (de ahí sale la historia) y el propio `.pmkbignore`. No lee contenidos."""
    raiz = os.path.abspath(raiz)
    partes = []
    for rel in archivos(raiz, excluir):
        if indexable(rel):
            partes.append(rel)
    for extra in (".pmkbignore", ".bitacora.jsonl", "*/.bitacora.jsonl", "*/*/.bitacora.jsonl"):
        partes += sorted(os.path.relpath(p, raiz).replace(os.sep, "/") for p in Path(raiz).glob(extra)
                         if not any(x in OMITIR_DIRS for x in Path(p).relative_to(raiz).parts[:-1]))
    firmas = []
    for rel in partes:
        try:
            st = os.stat(os.path.join(raiz, rel))
            firmas.append(f"{rel}:{st.st_size}:{st.st_mtime_ns}")
        except OSError:
            pass
    return sha("|".join(firmas), 16)


# ------------------------------------------------------------------ utilidades de texto
def frontmatter(txt):
    """(dict, cuerpo, líneas que ocupa) de un front matter YAML simple (clave: valor) al inicio de un Markdown."""
    if not txt.startswith("---"):
        return {}, txt, 0
    m = re.match(r"---[ \t]*\n(.*?)\n---[ \t]*(\n|$)", txt, re.S)
    if not m:
        return {}, txt, 0
    fm = {}
    for l in m.group(1).splitlines():
        mm = re.match(r"\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$", l)
        if mm:
            fm[mm.group(1).lower()] = mm.group(2).strip().strip('"').strip("'")
    return fm, txt[m.end():], m.group(0).count("\n")


def trozos(texto, maximo=MAX_SECCION):
    """Parte un texto largo por párrafos (y por tamaño si un párrafo solo lo excede); devuelve (offset_linea, trozo)."""
    if len(texto) <= maximo:
        return [(0, texto)]
    partes, actual, ini, linea = [], "", 0, 0
    for par in re.split(r"(\n\s*\n)", texto):
        if not par.strip():
            linea += par.count("\n")
            continue
        if actual and len(actual) + len(par) + 2 > maximo:
            partes.append((ini, actual)); actual = ""
        if not actual:
            ini = linea
        while len(par) > maximo:
            corte = par.rfind(" ", 0, maximo)
            corte = corte if corte > maximo // 2 else maximo
            partes.append((linea, par[:corte])); linea += par[:corte].count("\n"); par = par[corte:].lstrip(); ini = linea
        actual = (actual + "\n\n" + par) if actual else par
        linea += par.count("\n")
    if actual:
        partes.append((ini, actual))
    return partes


def secciones_md(md, titulo_doc, base=1):
    """[(título, línea_inicio, línea_fin, texto)] por encabezados #..### y por diapositivas de MarkItDown.
    Ignora encabezados dentro de bloques de código."""
    lineas = md.splitlines()
    out, ruta, inicio, buf, en_codigo = [], [titulo_doc], 1, [], False
    titulo = titulo_doc

    def cerrar(fin):
        texto = "\n".join(buf).strip()
        if texto:
            out.append((titulo, base + inicio - 1, base + fin - 1, texto))

    for n, l in enumerate(lineas, 1):
        if l.strip().startswith("```"):
            en_codigo = not en_codigo
        m = None if en_codigo else re.match(r"^(#{1,3})\s+(.+?)\s*#*\s*$", l)
        s = None if en_codigo else re.match(r"^<!--\s*Slide number:\s*(\d+)\s*-->", l)
        if m or s:
            cerrar(n - 1)
            if m:
                nivel = len(m.group(1))
                ruta = ruta[:nivel] + [m.group(2).strip()]
                vis = [x for i, x in enumerate(ruta) if x and (i == 0 or x != ruta[i - 1])]
                titulo = vis[0] if len(vis) == 1 else f"{vis[0][:80]} › {vis[-1]}"
                buf = [l]
            else:
                titulo = f"{titulo_doc} › diapositiva {s.group(1)}"
                buf = []
            inicio = n
        else:
            buf.append(l)
    cerrar(len(lineas))
    return out


class _Texto(html.parser.HTMLParser):
    BLOQUES = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "table"}

    def __init__(self):
        super().__init__(); self.partes, self.saltar = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.saltar += 1
        elif tag in ("h1", "h2", "h3"):
            self.partes.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in self.BLOQUES:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.saltar = max(0, self.saltar - 1)
        elif tag in self.BLOQUES:
            self.partes.append("\n")

    def handle_data(self, data):
        if not self.saltar:
            self.partes.append(data)


def html_a_md(txt):
    p = _Texto(); p.feed(txt)
    return re.sub(r"\n{3,}", "\n\n", "".join(p.partes))


_MARKITDOWN = None


def markitdown(ruta):
    """Markdown de un DOCX/PPTX/XLSX/PDF/HTML con MarkItDown (dependencia opcional). None si no está instalado."""
    global _MARKITDOWN
    if _MARKITDOWN is None:
        try:
            from markitdown import MarkItDown
            _MARKITDOWN = MarkItDown(enable_plugins=False)
        except ImportError:
            _MARKITDOWN = False
    if not _MARKITDOWN:
        return None
    return _MARKITDOWN.convert(str(ruta)).text_content or ""


# ------------------------------------------------------------------ unidades
def unidad(uid, tipo, fuente, rango, titulo, texto, **extra):
    texto = limpio(texto)
    u = {"id": uid, "tipo": tipo, "fuente": fuente, "rango": rango, "titulo": limpio(titulo)[:240], "texto": texto,
         "sha": sha(texto, 16), "registro": "", "circulacion": "equipo", "confianza": "gestion", "seccion": ""}
    u.update(extra)
    return u


def _titulo_fila(fila):
    for c in CAMPOS_TITULO:
        if (fila.get(c) or "").strip():
            return fila[c].strip()
    for k, v in fila.items():
        if k != "id" and (v or "").strip():
            return v.strip()
    return ""


def filas_csv(ruta):
    """[(línea_inicio, línea_fin, fila)] con números de línea reales (filas con saltos de línea incluidas)."""
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        try:
            cab = next(rd)
        except StopIteration:
            return [], []
        prev, out = rd.line_num, []
        for valores in rd:
            if any(v.strip() for v in valores):
                out.append((prev + 1, rd.line_num, dict(zip(cab, valores))))
            prev = rd.line_num
    return cab, out


def unidades_registro(rel, ruta, reg):
    cab, filas = filas_csv(ruta)
    us = []
    for a, b, f in filas:
        rid = (f.get("id") or "").strip()
        if not rid:
            continue
        omitir = set(CAMPOS_CONTACTO) if reg == "stakeholders" else set()
        conf = reg == "stakeholders" and (f.get("confidencial") or "").strip().lower() == "si"
        if conf:
            omitir |= SENSIBLES_STK
        orden = [k for k in CAMPOS_PRIMERO if k in f] + [k for k in f if k not in CAMPOS_PRIMERO]
        campos = [f"{k}: {f[k].strip()}" for k in orden if k and k != "id" and k not in omitir and (f[k] or "").strip()]
        if conf:
            campos.append("(valoración confidencial omitida)")
        titulo = f"{rid} · {_titulo_fila({k: v for k, v in f.items() if k not in omitir})}"
        us.append(unidad(rid, "fila", rel, f"L{a}" if a == b else f"L{a}-L{b}", titulo, "\n".join(campos),
                         registro=reg, fila={k: v for k, v in f.items() if k not in omitir}))
    return us


def unidades_csv(rel, ruta):
    cab, filas = filas_csv(ruta)
    us = []
    if "id" in cab:
        for a, b, f in filas:
            rid = (f.get("id") or "").strip() or f"L{a}"
            campos = [f"{k}: {v.strip()}" for k, v in f.items() if k and k != "id" and (v or "").strip()]
            us.append(unidad(f"{rel}#{rid}", "fila", rel, f"L{a}" if a == b else f"L{a}-L{b}",
                             f"{Path(rel).stem} · {rid} · {_titulo_fila(f)}", "\n".join(campos), fila=f))
        return us
    for i in range(0, len(filas), 20):
        grupo = filas[i:i + 20]
        texto = "\n".join(" | ".join(f"{k}: {v}" for k, v in f.items() if (v or "").strip()) for _, _, f in grupo)
        us.append(unidad(f"{rel}#L{grupo[0][0]}", "tabla", rel, f"L{grupo[0][0]}-L{grupo[-1][1]}",
                         f"{Path(rel).stem} (filas {i + 1}–{i + len(grupo)})", texto))
    return us


def unidades_md(rel, md, titulo_doc, base=1, tipo="seccion", rango_lineas=True):
    us, vistos = [], {}
    for titulo, a, b, texto in secciones_md(md, titulo_doc, base):
        clave = re.sub(r"\W+", "-", E._plano(titulo.split(" › ")[-1]) if hasattr(E, "_plano") else titulo.lower()).strip("-")[:60] or "seccion"
        vistos[clave] = vistos.get(clave, 0) + 1
        sec = clave if vistos[clave] == 1 else f"{clave}-{vistos[clave]}"
        for off, tr in trozos(texto):
            n = len([u for u in us if u["seccion"] == sec])
            uid = f"{rel}#{sec}" + (f"~{n + 1}" if n else "")
            la = a + off
            lb = min(b, la + tr.count("\n"))
            rango = (f"L{la}" if la == lb else f"L{la}-L{lb}") if rango_lineas else (titulo.split(" › ")[-1] if " › " in titulo else "")
            us.append(unidad(uid, tipo, rel, rango, titulo, tr, seccion=sec))
    return us


def unidades_transcripcion(rel, txt, ext):
    bloques = re.split(r"\n\s*\n", txt.replace("\r", ""))
    cues = []
    for b in bloques:
        ls = [l for l in b.strip().split("\n") if l.strip()]
        if not ls or ls[0].strip().upper().startswith("WEBVTT"):
            continue
        tiempo = next((l for l in ls if "-->" in l), "")
        texto = " ".join(l for l in ls if "-->" not in l and not re.fullmatch(r"\d+", l.strip()) and not l.startswith("NOTE"))
        if texto.strip():
            ini = tiempo.split("-->")[0].strip().split(".")[0].split(",")[0] if tiempo else ""
            fin = tiempo.split("-->")[1].strip().split(" ")[0].split(".")[0].split(",")[0] if tiempo else ""
            cues.append((ini, fin, texto))
    us = []
    for i in range(0, len(cues), VENTANA_TRANSCRIPCION):
        g = cues[i:i + VENTANA_TRANSCRIPCION]
        us.append(unidad(f"{rel}#t{i // VENTANA_TRANSCRIPCION + 1}", "transcripcion", rel, f"{g[0][0]}–{g[-1][1]}",
                         f"{Path(rel).stem} ({g[0][0]})", "\n".join(c[2] for c in g), confianza="externo"))
    return us


def unidades_correo(rel, datos):
    m = email.message_from_bytes(datos, policy=email.policy.default)
    asunto = str(m.get("subject") or Path(rel).stem)
    de = email.utils.parseaddr(str(m.get("from") or ""))[0]          # solo el nombre: sin direcciones de correo
    fecha = str(m.get("date") or "")
    cuerpo = m.get_body(preferencelist=("plain", "html"))
    txt = cuerpo.get_content() if cuerpo else ""
    if cuerpo and cuerpo.get_content_type() == "text/html":
        txt = html_a_md(txt)
    txt = re.sub(r"\S+@\S+\.\w+", "[correo omitido]", txt)
    return [unidad(f"{rel}#{i + 1}" if i else rel, "correo", rel, f"parte {i + 1}" if i else "", f"{asunto}" + (f" · {de}" if de else ""),
                   (f"Fecha: {fecha}\n\n" if fecha and not i else "") + tr, confianza="externo")
            for i, (_, tr) in enumerate(trozos(txt))]


def _escalares(o):
    return "\n".join(f"{k}: {v}" for k, v in o.items() if not k.startswith("_") and isinstance(v, (str, int, float)) and str(v).strip())


def _campos_propuesta(d):
    """Contenido propuesto de una propuesta de registro.py (03-control/propuestas/P-###.json, `campos`), con las mismas
    exclusiones que los registros: nada de `preferencias` ni `envios`; de `stakeholders`, sin contacto ni valoración
    (la propuesta no dice si la fila es confidencial, así que la valoración se omite siempre)."""
    reg = str(d.get("registro") or "")
    if reg in REGISTROS_EXCLUIDOS:
        return "(campos omitidos: registro con datos personales de interesados)"
    omitir = (CAMPOS_CONTACTO | SENSIBLES_STK) if reg == "stakeholders" else set()
    lineas = [f"campos.{k}: {v}" for k, v in d["campos"].items()
              if k not in omitir and isinstance(v, (str, int, float)) and str(v).strip()]
    if reg == "stakeholders" and any(k in omitir for k in d["campos"]):
        lineas.append("(contacto y valoración de interesados omitidos)")
    return "\n".join(lineas)


RESUMEN_ESTADO = ("proyecto", "fase", "proceso_actual", "etapa_actual", "enfoque_entrega", "idioma")   # claves de estado.json (SPEC §1.10)


def unidades_json(rel, txt):
    try:
        d = json.loads(txt)
    except ValueError:
        return []
    if Path(rel).name == "estado.json" and isinstance(d, dict):
        us = []
        etapa = d.get("etapa_actual") if isinstance(d.get("etapa_actual"), dict) else {}
        resumen = {"proyecto": d.get("proyecto"), "fase": d.get("fase"), "proceso_actual": d.get("proceso_actual"),
                   "etapa_actual": " · ".join(str(x) for x in (etapa.get("numero"), etapa.get("nombre")) if x not in (None, ""))
                   + (f" ({etapa.get('inicio', '')} → {etapa.get('fin_previsto', '')})" if etapa.get("inicio") or etapa.get("fin_previsto") else ""),
                   "enfoque_entrega": d.get("enfoque_entrega"), "idioma": d.get("idioma")}
        resumen = {k: v for k, v in resumen.items() if v not in (None, "")}
        us.append(unidad(f"{rel}#resumen", "estado", rel, "", f"Estado del proyecto · {d.get('proyecto', '')}", _escalares(resumen)))
        for k, v in d.items():
            if k in ("integraciones", "artefactos") + RESUMEN_ESTADO or v in (None, "", [], {}):
                continue
            cuerpo = json.dumps(v, ensure_ascii=False, indent=1) if not isinstance(v, str) else v
            for i, (_, tr) in enumerate(trozos(cuerpo)):
                us.append(unidad(f"{rel}#{k}" + (f"~{i + 1}" if i else ""), "estado", rel, k, f"estado.json › {k}", tr))
        arts = d.get("artefactos") or {}
        if arts:
            lineas = [f"{c}: {a.get('ruta', '')} · v{a.get('version', '')} · {a.get('estado', '')}" + (f" · aprobó {a['aprobado_por']}" if a.get("aprobado_por") else "")
                      for c, a in sorted(arts.items())]
            for i, (_, tr) in enumerate(trozos("\n".join(lineas))):
                us.append(unidad(f"{rel}#artefactos" + (f"~{i + 1}" if i else ""), "estado", rel, "artefactos", "estado.json › artefactos", tr))
        return us
    objs = []

    def recorrer(o, prof):
        if prof > 3:
            return
        if isinstance(o, dict):
            if isinstance(o.get("id"), str) and o["id"].strip():
                objs.append(o)
            for v in o.values():
                recorrer(v, prof + 1)
        elif isinstance(o, list):
            for v in o:
                recorrer(v, prof + 1)

    recorrer(d, 0)
    titulo = d.get("titulo") or d.get("title") or Path(rel).stem if isinstance(d, dict) else Path(rel).stem
    us = []
    if isinstance(d, dict):
        cab = _escalares({k: v for k, v in d.items() if k != "id"})
        if re.search(r"(^|/)03-control/propuestas/P-\d+\.json$", rel) and isinstance(d.get("campos"), dict):
            cab = "\n".join(x for x in (cab, _campos_propuesta(d)) if x)
        if cab:
            us.append(unidad(f"{rel}#datos", "json", rel, "", str(titulo), cab))
    vistos = set()
    for o in objs:
        oid = o["id"].strip()
        if oid in vistos:
            continue
        vistos.add(oid)
        nombre = o.get("nombre") or o.get("titulo") or o.get("accion") or ""
        us.append(unidad(f"{rel}#{oid}", "json", rel, oid, f"{titulo} · {oid}" + (f" · {nombre}" if nombre else ""), _escalares(o),
                         menciones=[r for r in (o.get("refs") or []) if isinstance(r, str)]))
    if not us:
        for i, (_, tr) in enumerate(trozos(json.dumps(d, ensure_ascii=False, indent=1))):
            us.append(unidad(f"{rel}#{i + 1}", "json", rel, "", str(titulo), tr))
    return us


# ------------------------------------------------------------------ documento
def registro_de(rel):
    m = re.search(r"(?:^|/)03-control/registros/([\w-]+)\.csv$", rel)
    return m.group(1) if m and m.group(1) in E.REGISTROS else ""


def leer_documento(raiz, rel, restringir=None):
    """dict con los metadatos del archivo y sus unidades, o None si no se indexa; ('omitido', motivo) si se salta."""
    ruta = Path(raiz) / rel
    ext = ruta.suffix.lower()
    try:
        tam = ruta.stat().st_size
    except OSError as x:
        return ("omitido", f"no se pudo leer ({x})")
    if tam > MAX_ARCHIVO:
        return ("omitido", f"supera {MAX_ARCHIVO // (1024 * 1024)} MB")
    if ext not in EXT_MD | EXT_TEXTO | EXT_TRANS | EXT_OFFICE | EXT_HTML | EXT_CORREO | EXT_DATOS:
        return None
    datos = ruta.read_bytes()
    doc = {"fuente": rel, "sha_archivo": sha(datos), "formato": ext.lstrip("."), "fm": {}, "titulo": ruta.stem,
           "unidades": [], "fecha_archivo": int(ruta.stat().st_mtime)}
    externo = bool(EXTERNO_RUTA.search(rel))
    try:
        if ext in EXT_MD | EXT_TEXTO:
            txt = datos.decode("utf-8", errors="replace")
            fm, cuerpo, nfm = frontmatter(txt) if ext in EXT_MD else ({}, txt, 0)
            doc["fm"] = fm
            h1 = re.search(r"(?m)^#\s+(.+)$", cuerpo)
            doc["titulo"] = fm.get("titulo") or fm.get("title") or (h1.group(1).strip() if h1 else ruta.stem)
            doc["unidades"] = unidades_md(rel, cuerpo, doc["titulo"], base=nfm + 1)
            if externo or ext in EXT_TEXTO and "transcrip" in rel.lower():
                for u in doc["unidades"]:
                    u["confianza"] = "externo"
        elif ext in EXT_TRANS:
            doc["unidades"] = unidades_transcripcion(rel, datos.decode("utf-8", errors="replace"), ext)
        elif ext in EXT_CORREO:
            doc["unidades"] = unidades_correo(rel, datos)
        elif ext == ".csv":
            reg = registro_de(rel)
            if reg in REGISTROS_EXCLUIDOS:
                return ("omitido", "registro con datos personales de interesados (no se indexa)")
            doc["unidades"] = unidades_registro(rel, ruta, reg) if reg else unidades_csv(rel, ruta)
            doc["registro"] = reg
        elif ext == ".json":
            doc["unidades"] = unidades_json(rel, datos.decode("utf-8", errors="replace"))
        elif ext in (".yaml", ".yml"):
            doc["unidades"] = [unidad(f"{rel}#{i + 1}" if i else rel, "texto", rel, "", ruta.name, tr)
                               for i, (_, tr) in enumerate(trozos(datos.decode("utf-8", errors="replace")))]
        elif ext in EXT_HTML | EXT_OFFICE:
            md = markitdown(ruta)
            if md is None:
                if ext in EXT_HTML:
                    md = html_a_md(datos.decode("utf-8", errors="replace"))
                else:
                    return ("omitido", "falta MarkItDown (pip install -r pm-kb/requirements.txt)")
            h1 = re.search(r"(?m)^#\s+(.+)$", md)
            doc["titulo"] = h1.group(1).strip() if h1 and ext != ".pptx" else ruta.stem
            tipo = {".pptx": "diapositiva", ".xlsx": "hoja"}.get(ext, "seccion")
            doc["unidades"] = unidades_md(rel, md, doc["titulo"], tipo=tipo, rango_lineas=False)
            if externo:
                for u in doc["unidades"]:
                    u["confianza"] = "externo"
    except Exception as x:  # un archivo dañado no detiene el índice: se informa
        return ("omitido", f"no se pudo convertir ({type(x).__name__}: {str(x)[:120]})")
    restr = (doc["fm"].get("circulacion", "").lower() == "restringida" or doc["fm"].get("confidencial", "").lower() == "si"
             or any(fnmatch.fnmatch(rel, p) for p in (restringir or [])))
    if restr:
        for u in doc["unidades"]:
            u["circulacion"] = "restringida"
    doc["sha_texto"] = sha("\n".join(u["texto"] for u in doc["unidades"]))
    return doc


def escanear(raiz, excluir=None, restringir=None):
    """(documentos, omitidos) de toda la carpeta."""
    docs, omitidos = [], []
    for rel in archivos(raiz, excluir):
        r = leer_documento(raiz, rel, restringir)
        if r is None:
            continue
        if isinstance(r, tuple):
            omitidos.append((rel, r[1]))
            continue
        if r["unidades"]:
            docs.append(r)
    return docs, omitidos


def bitacora(raiz_gestion):
    """Historia de filas, del estado y de los artefactos desde `.bitacora.jsonl` (ya sin valores sensibles: SPEC
    §1.10.16). Una escritura de estado.json que cambia `artefactos.<clave>` (estado.py artefacto, aprobar…) entra en la
    historia de esa clave: la ficha del artefacto la muestra (docs/PM-KB.md §5.1)."""
    p = Path(raiz_gestion) / ".bitacora.jsonl"
    out = []
    if not p.is_file():
        return out
    for l in p.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        cambios = d.get("cambios") or {}
        ids = list(d.get("ids") or list(cambios) or [])
        if (d.get("archivo") or "") == "estado.json":
            for c in d.get("claves") or []:
                if isinstance(c, str) and c.startswith("artefactos.") and len(c) > 11 and c[11:] not in ids:
                    ids.append(c[11:])
        for i in ids:
            out.append({"id": i, "n": d.get("n"), "fecha": d.get("fecha", ""), "operacion": d.get("operacion", ""),
                        "script": d.get("script", ""), "por": d.get("por", ""), "registro": d.get("registro", ""),
                        "detalle": cambios.get(i) or {}})
    return out
