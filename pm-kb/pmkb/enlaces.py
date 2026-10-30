"""Ids estables, ubicaciones y movimientos (sin base de datos). docs/PM-KB.md §5.1.

Una tarjeta o un enlace apunta a un **id estable**, nunca a una ruta:
- fila de registro → su id (`R-003`); ubicación: el CSV y sus líneas;
- artefacto de gobierno → su clave de `estado.json.artefactos` (`business-case`); ubicación: la ruta declarada o, si ya no
  existe, la que se encontró por huella o por nombre (y entonces el aviso de corregir `estado.json` con pm-method);
- documento sin clave → su `doc_id` de pm-kb (`ruta:…`, `nom:…`); si el archivo se mueve, el id anterior queda como alias
  de la ubicación nueva (se detecta por la huella sha256 del archivo).

En cada indexación se resuelve `id → ubicación vigente` y se compara con la indexación anterior para registrar los
movimientos («se movió de A a B»). pm-kb no escribe en la carpeta: corregir `estado.json` o una cita le corresponde a
pm-method o a quien edita el documento (`pm-kb enlaces` sugiere la acción).
"""
import datetime, os, posixpath, re, shlex
from pathlib import Path

from . import fuentes, versiones

NUCLEO = fuentes.RAIZ_PAQUETE / "skills" / "pm-estado-proyecto" / "scripts"
ESTADOS_ARTEFACTO = ("borrador", "en-revision", "aprobado", "obsoleto")      # esquema.ESTADOS_ARTEFACTO (estado.py artefacto --estado)
EXT_CITA = r"(?:md|markdown|csv|json|ya?ml|txt|html?|docx|pptx|xlsx|pdf|svg|png|jpe?g|mmd|vtt|srt|eml)"
_RUTA = re.compile(r"(?<![\w./:@$-])((?:\.{1,2}/)*(?:[\w.-]+/)+[\w.-]+\." + EXT_CITA + r")(?![\w/-])", re.I)
_ENLACE_MD = re.compile(r"\]\(([^)\s#?]+\." + EXT_CITA + r")(?:[#?][^)\s]*)?\)", re.I)


def _norm(r):
    """Ruta con '/' y sin './' inicial."""
    return re.sub(r"^(\./)+", "", str(r or "").replace(os.sep, "/"))


def _sin_subidas(r):
    return re.sub(r"^(\.\.?/)+", "", posixpath.normpath(r))


def _en_historial(fuente, gestion=""):
    return "/00-direccion/historial/" in "/" + fuente


# ------------------------------------------------------------------ artefactos
def resolver_artefactos(raiz, gestion, estado, docs, previas=None):
    """Ruta real de cada artefacto de `estado.json`.

    Devuelve (rutas, artefactos): `rutas` = {clave: fuente} de los artefactos cuya ruta declarada no existe y se
    encontraron en otro lugar (para `versiones.asignar`); `artefactos` = una entrada por clave con `declarada`, `ruta`,
    `estado` (vigente | movida | no-encontrada | externa), `encontrada_por` (huella | nombre | '') y la versión y el
    estado del artefacto. Orden de búsqueda de una ruta que no existe: la ubicación de la indexación anterior (si sigue
    existiendo), el mismo sha256 que el archivo de la indexación anterior o que su copia congelada de
    `00-direccion/historial/`, y el mismo nombre de archivo (o la clave como nombre) si hay un solo candidato. Nunca un
    archivo de `historial/` ni la ruta declarada de otro artefacto."""
    raiz = Path(raiz)
    g = (gestion.rstrip("/") + "/") if gestion else ""
    previas = previas or {}
    arts = (estado or {}).get("artefactos") or {}
    por_ruta = {d["fuente"]: d for d in docs}
    por_sha = {}
    for d in docs:
        por_sha.setdefault(d["sha_archivo"], []).append(d["fuente"])
    declaradas = {g + _norm(a.get("ruta")) for a in arts.values() if isinstance(a, dict) and a.get("ruta") and not a.get("externo")}
    ocupadas = {r for r in declaradas if (raiz / r).exists()}

    def libres(fs, cerca=""):
        """Candidatos posibles, el más cercano a la ruta declarada primero (dentro de la carpeta de gestión y con más
        carpetas en común)."""
        def comun(f):
            a, b = f.split("/"), cerca.split("/")
            n = 0
            while n < min(len(a), len(b)) and a[n] == b[n]:
                n += 1
            return n
        return sorted((f for f in fs if f not in ocupadas and not _en_historial(f, gestion)),
                      key=lambda f: (bool(g) and not f.startswith(g), -comun(f), f))

    rutas, salida = {}, []
    for clave, a in sorted(arts.items()):
        if not isinstance(a, dict):
            continue
        decl = g + _norm(a.get("ruta")) if a.get("ruta") else ""
        item = {"ref": clave, "declarada": decl, "ruta": decl, "estado": "vigente", "encontrada_por": "",
                "version": str(a.get("version") or ""), "estado_artefacto": str(a.get("estado") or "")}
        if a.get("externo"):
            item["estado"] = "externa"
            salida.append(item); continue
        if decl and (raiz / decl).exists():
            salida.append(item); continue
        cand, como = None, ""
        p = previas.get(clave) or {}
        if p.get("tipo") == "artefacto" and p.get("ruta") and p["ruta"] != decl and p["ruta"] in por_ruta and not _en_historial(p["ruta"], gestion):
            cand, como = p["ruta"], p.get("encontrada_por") or "huella"
        if not cand and p.get("sha256"):
            fs = libres(por_sha.get(p["sha256"], []), decl)
            if fs:
                cand, como = fs[0], "huella"
        if not cand:
            copia = a.get("copia_congelada")
            copia = g + _norm(copia) if copia else f"{g}00-direccion/historial/{clave}-v{item['version']}{Path(decl).suffix}"
            if copia in por_ruta:
                fs = libres(por_sha.get(por_ruta[copia]["sha_archivo"], []), decl)
                if fs:
                    cand, como = fs[0], "huella"
        if not cand and decl:
            nombre, ext = Path(decl).name.lower(), Path(decl).suffix.lower()
            fs = libres(f for f in por_ruta if Path(f).name.lower() == nombre
                        or (Path(f).suffix.lower() == ext and versiones.nombre_normalizado(Path(f).stem)[0] == clave.lower()))
            if len(fs) == 1:
                cand, como = fs[0], "nombre"
        if cand:
            rutas[clave] = cand
            item.update(ruta=cand, estado="movida", encontrada_por=como)
        else:
            item["estado"] = "no-encontrada"
        salida.append(item)
    return rutas, salida


# ------------------------------------------------------------------ ubicaciones y movimientos
def ubicaciones(prep, previas=None, ahora=None):
    """(filas de `pmkb.ubicacion`, movimientos nuevos) de un índice preparado, comparando con las ubicaciones de la
    indexación anterior (`previas`: {ref: fila}). Un movimiento es una ruta distinta para el mismo id estable: una fila
    en otro archivo (`id`), un artefacto con otra ruta en estado.json (`clave`) o encontrado fuera de ella (`huella`,
    `nombre`), o un documento sin clave cuyo archivo apareció con el mismo sha256 en otra ruta (`huella`; el id anterior
    queda como alias de la ubicación nueva). Un documento que desaparece sin dejar huella deja de resolverse."""
    previas = previas or {}
    ahora = ahora or datetime.datetime.now(datetime.timezone.utc)
    arch = prep.get("archivos") or {}
    filas, movs = {}, []

    def poner(ref, tipo, ruta, rango, doc_id, sha, circ, estado="vigente", declarada="", encontrada_por="", detalle=None, motivo=None):
        prev = previas.get(ref) or {}
        desde = prev.get("desde") if prev.get("ruta") == ruta and prev.get("desde") else ahora
        if motivo and prev.get("ruta") and ruta and prev["ruta"] != ruta and estado != "no-encontrada":
            movs.append({"ref": ref, "tipo": tipo, "ruta_anterior": prev["ruta"], "ruta_nueva": ruta, "sha256": sha,
                         "detectado": ahora, "motivo": motivo, "circulacion": circ})
        filas[ref] = {"ref": ref, "tipo": tipo, "ruta": ruta, "rango": rango or "", "sha256": sha or "", "desde": desde,
                      "doc_id": doc_id or "", "declarada": declarada, "estado": estado, "encontrada_por": encontrada_por,
                      "circulacion": circ, "detalle": detalle}

    for u in prep.get("unidades") or []:
        if u.get("registro") and u.get("vigente") and "#" not in u["id"]:
            poner(u["id"], "fila", u["fuente"], u["rango"], u["doc_id"], (arch.get(u["fuente"]) or {}).get("sha", ""),
                  u["circulacion"], motivo="id")
    for a in prep.get("artefactos") or []:
        info = arch.get(a["ruta"]) or {}
        ruta = a["declarada"] if a["estado"] == "no-encontrada" else a["ruta"]
        motivo = a["encontrada_por"] or "clave"
        poner(a["ref"], "artefacto", ruta, "", info.get("doc_id") or f"art:{a['ref']}", info.get("sha", ""),
              info.get("circulacion", "equipo"), estado=a["estado"], declarada=a["declarada"], encontrada_por=a["encontrada_por"],
              detalle={"version": a["version"], "estado": a["estado_artefacto"]}, motivo=None if a["estado"] == "externa" else motivo)
    for d in prep.get("documentos") or []:
        if d["doc_id"].startswith("art:") or d["doc_id"] in filas:
            continue
        info = arch.get(d["fuente_vigente"]) or {}
        poner(d["doc_id"], "documento", d["fuente_vigente"], "", d["doc_id"], info.get("sha", ""), info.get("circulacion", "equipo"))
    rutas_previas = {p.get("ruta") for p in previas.values()}
    for ref, p in sorted(previas.items()):
        if ref in filas or p.get("tipo") != "documento":
            continue
        if p.get("ruta") in arch:               # sigue en su lugar con otro doc_id (p. ej., ahora tiene varias versiones)
            info = arch[p["ruta"]]
            poner(ref, "documento", p["ruta"], "", info["doc_id"], info["sha"], info["circulacion"])
            continue
        cands = sorted(f for f, i in arch.items() if p.get("sha256") and i["sha"] == p["sha256"] and f not in rutas_previas)
        if cands:
            info = arch[cands[0]]
            poner(ref, "documento", cands[0], "", info["doc_id"], info["sha"], info["circulacion"], motivo="huella")
    return list(filas.values()), movs


# ------------------------------------------------------------------ citas a rutas
def rutas_citadas(texto):
    """Rutas de archivo citadas en un texto (con al menos una carpeta, o enlaces Markdown a un archivo), sin URLs."""
    vistas, out = set(), []
    for m in list(_RUTA.finditer(texto or "")) + list(_ENLACE_MD.finditer(texto or "")):
        r = m.group(1)
        if r.startswith(("/", "~")) or "://" in r or r in vistas:
            continue
        vistas.add(r); out.append(r)
    return out


def _bases(fuente, gestion):
    """Carpetas desde las que se resuelve una cita: la del documento y sus superiores hasta la raíz, y la de gestión."""
    bases, d = [], posixpath.dirname(fuente)
    while True:
        bases.append(d)
        if not d:
            break
        d = posixpath.dirname(d)
    if gestion and gestion not in bases:
        bases.append(gestion)
    return bases


def existe_cita(raiz, gestion, fuente, ruta, solo_carpeta=False):
    """True si la ruta citada existe desde la carpeta del documento que la cita (o una superior), la de gestión o la raíz.
    Con `solo_carpeta`, basta con que exista su primera carpeta (la cita apunta dentro del proyecto)."""
    raiz = Path(raiz)
    if solo_carpeta:
        ruta = ruta.split("/")[0] if not ruta.startswith(".") else _sin_subidas(ruta).split("/")[0]
    for b in _bases(fuente, gestion):
        p = posixpath.normpath(posixpath.join(b, ruta))
        if not p.startswith("../") and p != "." and (raiz / p).exists():
            return True
    return False


def citas_rotas(unidades, raiz, gestion, movimientos=(), archivos=()):
    """Citas a rutas que no existen en las unidades vigentes de gestión (no las copias congeladas ni estado.json, cuyas
    rutas controla la lista de artefactos). `unidades`: dicts con id, fuente, rango, registro y texto. Sugiere la ruta
    nueva por un movimiento registrado (`movimiento`) o por un único archivo indexado con el mismo nombre (`nombre`).
    Una cita cuya primera carpeta no existe en el proyecto y sin ruta sugerida se ignora: apunta a otro repositorio
    (por ejemplo, el código que citan los documentos de BMAD)."""
    out = []
    archivos = sorted(set(archivos))
    for u in unidades:
        if u["fuente"].endswith("estado.json") or _en_historial(u["fuente"], gestion):
            continue
        for r in rutas_citadas(u["texto"]):
            if existe_cita(raiz, gestion, u["fuente"], r):
                continue
            plano = _sin_subidas(r)
            sug, como = "", ""
            for m in movimientos:
                ant = m["ruta_anterior"]
                if ant == plano or ant.endswith("/" + plano):
                    sug, como = m["ruta_nueva"], "movimiento"
                    break
            if not sug:
                mismos = [f for f in archivos if posixpath.basename(f) == posixpath.basename(plano) and not _en_historial(f, gestion)]
                if len(mismos) == 1:
                    sug, como = mismos[0], "nombre"
            if not sug and not existe_cita(raiz, gestion, u["fuente"], r, solo_carpeta=True):
                continue            # ni su carpeta existe en el proyecto ni hay a dónde se movió: cita de otro repositorio (p. ej., código)
            col = ""
            if u.get("registro"):
                col = next((l.split(":", 1)[0] for l in u["texto"].splitlines() if ":" in l and r in l.split(":", 1)[1]), "")
            out.append({"id": u["id"], "fuente": u["fuente"], "rango": u.get("rango") or "", "registro": u.get("registro") or "",
                        "columna": col, "ruta_citada": r, "sugerida": sug, "como": como,
                        "cita_sugerida": _como_cita(r, sug, raiz, gestion, u["fuente"]) if sug else "", "texto": u["texto"]})
    return out


def _como_cita(citada, nueva, raiz, gestion, fuente):
    """La ruta nueva escrita con la misma base que la citada: relativa a la carpeta de gestión si la cita empieza por una
    carpeta de gestión (`03-control/…`), si no, relativa a la raíz."""
    primero = _sin_subidas(citada).split("/")[0]
    if gestion and nueva.startswith(gestion.rstrip("/") + "/") and (re.match(r"\d\d-", primero) or (Path(raiz) / gestion / primero).exists()):
        return posixpath.relpath(nueva, gestion)
    return nueva


# ------------------------------------------------------------------ acciones sugeridas
def _py(script):
    return "python3 " + shlex.quote(str(NUCLEO / script))


def accion_artefacto(raiz, gestion, a):
    """Comando de pm-method que registra en estado.json la ruta donde se encontró un artefacto (`estado.py artefacto`:
    `--estado` va siempre, porque sin él vuelve a borrador; la versión se conserva)."""
    det = a.get("detalle") or {}
    carpeta = str(Path(raiz) / gestion) if gestion else str(raiz)
    ruta = posixpath.relpath(a["ruta"], gestion) if gestion else a["ruta"]
    partes = [_py("estado.py"), "--proyecto", shlex.quote(carpeta), "artefacto", shlex.quote(a["ref"])]
    if a["estado"] == "movida":
        partes += ["--ruta", shlex.quote(ruta)]
    else:
        partes += ["--ruta", "<ruta-nueva>"]
    if det.get("estado") in ESTADOS_ARTEFACTO:
        partes += ["--estado", det["estado"]]
    if det.get("version"):
        partes += ["--version", shlex.quote(det["version"])]
    cmd = " ".join(partes)
    if a["estado"] == "movida":
        return cmd
    return f"restaurar {a['declarada']} o registrar la ruta correcta: {cmd}"


REGISTROS_HISTORICOS = ("decisiones",)     # filas que no se editan para corregir una cita: son el registro de lo decidido


def accion_cita(raiz, gestion, c):
    if c.get("registro") in REGISTROS_HISTORICOS:
        donde = f"{c['fuente']}" + (f" ({c['rango']})" if c["rango"] else "") + f", {c['id']}"
        if c["sugerida"] and c["como"] == "movimiento":
            return (f"ninguna: {donde} es un registro histórico y no se edita; el archivo se movió a «{c['sugerida']}» y el enlace "
                    "por id ya lo resuelve (la ficha muestra la ubicación vigente)")
        if c["sugerida"]:
            return (f"ninguna: {donde} es un registro histórico y no se edita; la ruta citada hoy está en «{c['sugerida']}» "
                    f"(por {c['como']}); si hace falta, citarla así en una decisión nueva")
        return f"ninguna en la fila: {donde} es un registro histórico y no se edita; la ruta citada no existe y no se encontró"
    if not c["sugerida"]:
        return f"revisar la cita en {c['fuente']}" + (f" ({c['rango']})" if c["rango"] else "") + ": la ruta no existe y no se encontró por movimiento ni por nombre"
    if c["registro"] and c["columna"]:
        valor = next((l.split(":", 1)[1].strip() for l in c["texto"].splitlines() if l.startswith(c["columna"] + ":")), "")
        if valor and c["ruta_citada"] in valor:
            carpeta = str(Path(raiz) / gestion) if gestion else str(raiz)
            nuevo = valor.replace(c["ruta_citada"], c["cita_sugerida"])
            return " ".join([_py("registro.py"), "--proyecto", shlex.quote(carpeta), "actualizar", c["registro"], shlex.quote(c["id"]),
                             "--campo", shlex.quote(f"{c['columna']}={nuevo}")])
    return f"editar {c['fuente']}" + (f" ({c['rango']})" if c["rango"] else "") + f": «{c['ruta_citada']}» → «{c['cita_sugerida']}»"


def informe(proyecto, raiz, gestion, indexado_en, artefactos, movimientos, unidades, archivos, carpeta_accesible=True):
    """Informe de `pm-kb enlaces` (dict para --json y para el texto)."""
    arts = []
    for a in artefactos:
        arts.append({"ref": a["ref"], "declarada": a["declarada"], "estado": a["estado"],
                     "sugerida": a["ruta"] if a["estado"] == "movida" else "", "encontrada_por": a["encontrada_por"],
                     "accion": accion_artefacto(raiz, gestion, a)})
    citas, avisos = [], []
    if carpeta_accesible:
        for c in citas_rotas(unidades, raiz, gestion, movimientos, archivos):
            citas.append({**{k: c[k] for k in ("id", "fuente", "rango", "ruta_citada", "sugerida", "como")},
                          "resuelta": c["como"] == "movimiento", "historica": c.get("registro") in REGISTROS_HISTORICOS,
                          "accion": accion_cita(raiz, gestion, c)})
    else:
        avisos.append(f"la carpeta indexada no está accesible desde aquí ({raiz}): no se revisan las citas a rutas")
    movs = [{"ref": m["ref"], "tipo": m["tipo"], "de": m["ruta_anterior"], "a": m["ruta_nueva"], "motivo": m["motivo"],
             "fecha": m["detectado"].isoformat(timespec="seconds") if hasattr(m["detectado"], "isoformat") else str(m["detectado"])}
            for m in movimientos]
    return {"proyecto": proyecto, "raiz": str(raiz), "gestion": gestion, "indexado_en": indexado_en,
            "artefactos": arts, "citas": citas, "movimientos": movs,
            "totales": {"artefactos": len(arts), "citas": len(citas), "movimientos": len(movs)}, "avisos": avisos}


def texto_movimiento(m):
    f = m.get("fecha") or m.get("detectado")
    f = f.strftime("%Y-%m-%d") if hasattr(f, "strftime") else str(f or "")[:10]
    return f"se movió de {m.get('de') or m.get('ruta_anterior')} a {m.get('a') or m.get('ruta_nueva')} el {f}"
