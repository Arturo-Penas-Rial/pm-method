"""Indexar un proyecto: carpeta → unidades, versiones y aristas → PostgreSQL, en una sola transacción.

El índice de un proyecto se reemplaza entero dentro de la transacción: quien consulta ve el índice anterior o el nuevo,
nunca la mitad. Los vectores (si hay modelo configurado) se reutilizan por huella del texto (`cache_vector`). Las
ubicaciones por id estable se recalculan comparando con las de la indexación anterior, y los movimientos detectados se
acumulan en `pmkb.movimiento` (docs/PM-KB.md §5.1).
"""
import csv, json, os, re, subprocess
from pathlib import Path

from . import VERSION, config, enlaces, fuentes, modelos, relaciones, versiones

ESQUEMA = 4          # versión del esquema que usa este código (pmkb.meta.esquema; esquema.sql)
_NOMBRE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")


def validar_nombre(nombre):
    if not _NOMBRE.match(nombre or ""):
        raise SystemExit("pm-kb: nombre de proyecto inválido (minúsculas, cifras, '.', '_' o '-'; hasta 63 caracteres): " + repr(nombre))
    return nombre


def carpeta_gestion(raiz):
    """Ruta relativa ('' o 'gestion' …) de la carpeta con estado.json, o None si no hay proyecto pm-method."""
    raiz = Path(raiz)
    if (raiz / "estado.json").is_file():
        return ""
    candidatos = sorted(p for p in raiz.glob("*/estado.json")) + sorted(p for p in raiz.glob("*/*/estado.json"))
    candidatos = [p for p in candidatos if not any(x in fuentes.OMITIR_DIRS for x in p.relative_to(raiz).parts)]
    return str(candidatos[0].parent.relative_to(raiz)).replace(os.sep, "/") if candidatos else None


def commit_git(raiz):
    try:
        c = subprocess.run(["git", "-C", str(raiz), "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True, timeout=10)
        if c.returncode != 0:
            return ""
        sucio = subprocess.run(["git", "-C", str(raiz), "status", "--porcelain"], capture_output=True, text=True, timeout=20).stdout.strip()
        return c.stdout.strip() + ("+" if sucio else "")
    except (OSError, subprocess.SubprocessError):
        return ""


def preparar(raiz, excluir=None, restringir=None, previas=None):
    """Lectura y armado en memoria (sin base): devuelve un dict con todo lo que se carga. `previas` ({ref: fila} de
    `pmkb.ubicacion` de la indexación anterior) permite reconocer un artefacto movido por la huella del archivo."""
    raiz = Path(raiz).resolve()
    if not raiz.is_dir():
        raise SystemExit(f"pm-kb: no existe la carpeta {raiz}")
    g = carpeta_gestion(raiz)
    gestion = g or ""
    estado, decisiones = {}, []
    if g is not None:
        try:
            estado = json.loads((raiz / gestion / "estado.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            estado = {}
        p = raiz / gestion / "03-control" / "registros" / "decisiones.csv"
        if p.is_file():
            with open(p, newline="", encoding="utf-8") as f:
                decisiones = list(csv.DictReader(f))
    docs, omitidos = fuentes.escanear(raiz, excluir, restringir)
    rutas_art, artefactos = enlaces.resolver_artefactos(raiz, gestion, estado, docs, previas)
    documentos, vers = versiones.asignar(docs, estado, decisiones, gestion, rutas=rutas_art)
    archivos = {d["fuente"]: {"sha": d["sha_archivo"], "doc_id": d["unidades"][0]["doc_id"],
                              "circulacion": "restringida" if any(u["circulacion"] == "restringida" for u in d["unidades"]) else "equipo"}
                for d in docs}
    unidades = [u for d in docs for u in d["unidades"]]
    # ids repetidos dentro del proyecto (dos filas con el mismo id en dos CSV): se conserva la primera vigente
    vistos, unicas = set(), []
    for u in sorted(unidades, key=lambda u: (not u["vigente"], u["fuente"])):
        if u["id"] in vistos:
            u["id"] = f"{u['fuente']}#{u['id']}"
            if u["id"] in vistos:
                continue
        vistos.add(u["id"]); unicas.append(u)
    aristas = relaciones.aristas(unicas)
    historia = fuentes.bitacora(raiz / gestion) if g is not None else []
    return {"raiz": str(raiz), "gestion": g, "unidades": unicas, "documentos": documentos, "versiones": vers,
            "aristas": aristas, "historia": historia, "omitidos": omitidos, "commit": commit_git(raiz),
            "nombre_proyecto": estado.get("proyecto", ""), "artefactos": artefactos, "archivos": archivos,
            "previas": previas is not None}


def _copy(cur, tabla, columnas, filas):
    with cur.copy(f"COPY pmkb.{tabla} ({', '.join(columnas)}) FROM STDIN") as cp:
        for f in filas:
            cp.write_row(f)


def version_esquema(conn):
    """Versión del esquema de la base (0 si no hay esquema)."""
    r = conn.execute("""SELECT CASE WHEN to_regclass('pmkb.meta') IS NULL THEN NULL
                               ELSE (SELECT valor FROM pmkb.meta WHERE clave = 'esquema') END""").fetchone()
    try:
        return int(r[0]) if r and r[0] else 0
    except ValueError:
        return 0


def exigir_esquema(conn):
    v = version_esquema(conn)
    if v < ESQUEMA:
        raise SystemExit(f"pm-kb: la base tiene el esquema {v or 'ninguno'} y este pm-kb usa el {ESQUEMA}: ejecutá `pm-kb base crear` "
                         "(lo crea o lo actualiza sin perder el índice ni los tokens)")


_COLS_UBICACION = ["proyecto", "ref", "tipo", "ruta", "rango", "sha256", "desde", "doc_id", "declarada", "estado", "encontrada_por",
                   "circulacion", "detalle"]


def ubicaciones_previas(conn, proyecto):
    """{ref: fila} de las ubicaciones de la indexación anterior del proyecto (vacío si no hay)."""
    cur = conn.execute(f"SELECT {', '.join(_COLS_UBICACION[1:])} FROM pmkb.ubicacion WHERE proyecto = %s", (proyecto,))
    cols = [c.name for c in cur.description]
    return {r[0]: dict(zip(cols, r)) for r in cur.fetchall()}


def indexar(conn, proyecto, ruta, excluir=None, restringir=None, con_vectores=True, avisar=print):
    """preparar + cargar, con las ubicaciones anteriores (para reconocer un artefacto movido por su huella)."""
    proyecto = validar_nombre(proyecto)
    exigir_esquema(conn)
    prep = preparar(ruta, excluir, restringir, previas=ubicaciones_previas(conn, proyecto))
    return prep, cargar(conn, proyecto, prep, con_vectores=con_vectores, avisar=avisar)


def cargar(conn, proyecto, prep, con_vectores=True, avisar=print):
    """Reemplaza el índice del proyecto en una sola transacción. Si PostgreSQL la aborta por un interbloqueo (por ejemplo,
    con `pm-kb base crear` o `verificar` reaplicando el esquema a la vez), se repite entera: no deja nada a medias."""
    import random
    import time
    import psycopg
    proyecto = validar_nombre(proyecto)
    exigir_esquema(conn)
    for intento in range(5):
        try:
            return _cargar(conn, proyecto, prep, con_vectores, avisar)
        except psycopg.errors.DeadlockDetected:
            if intento == 4:
                raise
            time.sleep(0.5 * (intento + 1) + random.random() / 2)


def _cargar(conn, proyecto, prep, con_vectores, avisar):
    us = prep["unidades"]
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(BLOQUEO_ESQUEMA_COMPARTIDO)   # antes que cualquier tabla: no se cruza con `base crear` reaplicando el esquema
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('pmkb.indexar:' || %s))", (proyecto,))   # dos indexaciones del mismo proyecto, en fila
        previas = ubicaciones_previas(conn, proyecto)
        if not prep.get("previas") and previas:      # preparado sin las ubicaciones anteriores: se resuelven ahora los artefactos
            estado_rel = {a["ref"]: a for a in prep.get("artefactos") or []}
            for a in estado_rel.values():
                p = previas.get(a["ref"]) or {}
                if a["estado"] == "no-encontrada" and p.get("sha256"):
                    fs = sorted(f for f, i in (prep.get("archivos") or {}).items() if i["sha"] == p["sha256"] and "/00-direccion/historial/" not in "/" + f)
                    if fs:
                        a.update(ruta=fs[0], estado="movida", encontrada_por="huella")
        ubs, movs = enlaces.ubicaciones(prep, previas)
        for t in ("unidad", "documento", "version", "lexema", "arista", "historia", "vector", "indice", "ubicacion"):
            cur.execute(f"DELETE FROM pmkb.{t} WHERE proyecto = %s", (proyecto,))
        _copy(cur, "unidad", ["proyecto", "id", "doc_id", "version", "tipo", "registro", "titulo", "texto", "fuente", "rango",
                              "seccion", "estado_doc", "vigente", "aprobada", "copia", "duplicado_de", "circulacion", "confianza",
                              "sha", "tambien_en"],
              ([proyecto, u["id"], u["doc_id"], u["version"], u["tipo"], u.get("registro") or "", u["titulo"], u["texto"], u["fuente"],
                u["rango"], u.get("seccion") or "", u.get("estado_doc") or "", u["vigente"], u["aprobada"], u.get("copia", False),
                u.get("duplicado_de") or "", u["circulacion"], u["confianza"], u["sha"], u.get("tambien_en") or None] for u in us))
        circ_v = {v["fuente"]: ((prep.get("archivos") or {}).get(v["fuente"]) or {}).get("circulacion", "equipo") for v in prep["versiones"]}
        circ_d = {}
        for v in prep["versiones"]:        # un documento es restringido si alguna de sus versiones lo es (título y rutas incluidos)
            if circ_v[v["fuente"]] == "restringida":
                circ_d[v["doc_id"]] = "restringida"
        _copy(cur, "documento", ["proyecto", "doc_id", "titulo", "tipo", "clave_pm", "version_vigente", "version_aprobada",
                                 "fuente_vigente", "fuente_aprobada", "versiones", "circulacion"],
              ([proyecto, d["doc_id"], d["titulo"], d["tipo"], d["clave_pm"], d["version_vigente"], d["version_aprobada"],
                d["fuente_vigente"], d["fuente_aprobada"], d["versiones"], circ_d.get(d["doc_id"], "equipo")] for d in prep["documentos"]))
        _copy(cur, "version", ["proyecto", "doc_id", "version", "orden", "fecha", "estado", "aprobado_por", "decision_id", "fuente",
                               "sha256_archivo", "sha256_texto", "origen", "copia", "circulacion"],
              ([proyecto, v["doc_id"], v["version"], v["orden"], v["fecha"], v["estado"], v["aprobado_por"], v["decision_id"],
                v["fuente"], v["sha256_archivo"], v["sha256_texto"], v["origen"], v["copia"], circ_v[v["fuente"]]] for v in prep["versiones"]))
        _copy(cur, "arista", ["proyecto", "origen", "destino", "tipo", "fuente", "rango"], ([proyecto, *a] for a in prep["aristas"]))
        _copy(cur, "ubicacion", _COLS_UBICACION,
              ([proyecto] + [json.dumps(u[c], ensure_ascii=False) if c == "detalle" and u[c] is not None else u[c] for c in _COLS_UBICACION[1:]]
               for u in ubs))
        _copy(cur, "movimiento", ["proyecto", "ref", "tipo", "ruta_anterior", "ruta_nueva", "sha256", "detectado", "motivo", "circulacion"],
              ([proyecto, m["ref"], m["tipo"], m["ruta_anterior"], m["ruta_nueva"], m["sha256"], m["detectado"], m["motivo"], m["circulacion"]]
               for m in movs))
        _copy(cur, "historia", ["proyecto", "id", "n", "fecha", "operacion", "script", "por", "registro", "detalle"],
              ([proyecto, h["id"], h["n"], h["fecha"], h["operacion"], h["script"], h["por"], h["registro"],
                json.dumps(h["detalle"], ensure_ascii=False)] for h in prep["historia"]))
        cur.execute("UPDATE pmkb.unidad u SET dl = (SELECT coalesce(sum(cardinality(x.positions)), 0) FROM unnest(u.tsv) x) WHERE proyecto = %s", (proyecto,))
        cur.execute("""INSERT INTO pmkb.lexema (proyecto, lexema, ndoc)
                       SELECT %s, s.word, s.ndoc FROM ts_stat(format('SELECT tsv FROM pmkb.unidad WHERE vigente AND proyecto = %%L', %s::text)) s""",
                    (proyecto, proyecto))
        cur.execute("SELECT count(*) FILTER (WHERE vigente), coalesce(avg(dl) FILTER (WHERE vigente), 1) FROM pmkb.unidad WHERE proyecto = %s", (proyecto,))
        n_vig, avgdl = cur.fetchone()
        modelo = ""
        emb = config.embed() if con_vectores else None
        if emb:
            modelo = emb["modelo"] or emb["url"]
            vig = [u for u in us if u["vigente"]]
            cur.execute("SELECT sha FROM pmkb.cache_vector WHERE modelo = %s AND sha = ANY(%s)", (modelo, [u["sha"] for u in vig]))
            hechos = {r[0] for r in cur.fetchall()}
            faltan = {u["sha"]: (u["titulo"] + "\n" + u["texto"])[:4000] for u in vig if u["sha"] not in hechos}
            if faltan:
                avisar(f"pm-kb: calculando {len(faltan)} vectores con {modelo} …")
                shas = list(faltan)
                try:
                    vs = modelos.vectores(emb, [faltan[s] for s in shas])
                    if len(vs) != len(shas):
                        raise RuntimeError(f"devolvió {len(vs)} vectores para {len(shas)} textos")
                except RuntimeError as x:   # servidor caído o con error: se indexa sin vectores (búsqueda léxica), sin traza
                    avisar(f"pm-kb: aviso: el modelo de vectores no respondió ({str(x)[:200]}); se indexa sin vectores "
                           "(búsqueda léxica). Volver a indexar cuando responda (los vectores que ya estaban en caché se reutilizan).")
                    modelo, vs = "", None
                if vs is not None:
                    _copy(cur, "cache_vector", ["sha", "modelo", "emb"], ([s, modelo, "[" + ",".join(f"{x:.6f}" for x in v) + "]"] for s, v in zip(shas, vs)))
            if modelo:
                cur.execute("""INSERT INTO pmkb.vector (proyecto, unidad_id, modelo, emb)
                               SELECT u.proyecto, u.id, c.modelo, c.emb FROM pmkb.unidad u JOIN pmkb.cache_vector c ON c.sha = u.sha AND c.modelo = %s
                               WHERE u.proyecto = %s AND u.vigente""", (modelo, proyecto))
        cur.execute("""INSERT INTO pmkb.indice (proyecto, raiz, commit_git, unidades, documentos, vigentes, avgdl, version_kb, modelo, omitidos, gestion, nombre)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (proyecto, prep["raiz"], prep["commit"], len(us), len(prep["documentos"]), n_vig, float(avgdl), VERSION, modelo,
                     json.dumps([{"fuente": f, "motivo": m} for f, m in prep["omitidos"]], ensure_ascii=False), prep["gestion"],
                     prep.get("nombre_proyecto") or ""))
    return {"unidades": len(us), "vigentes": n_vig, "documentos": len(prep["documentos"]),
            "con_versiones": sum(1 for d in prep["documentos"] if d["versiones"] > 1), "aristas": len(prep["aristas"]),
            "historia": len(prep["historia"]), "omitidos": len(prep["omitidos"]), "modelo": modelo, "commit": prep["commit"],
            "movimientos": movs, "sin_fuente": [u["ref"] for u in ubs if u["tipo"] == "artefacto" and u["estado"] in ("movida", "no-encontrada")]}


# Aplicar el esquema toma bloqueos exclusivos de las tablas; una carga del índice o del tablero toma bloqueos de fila en
# varias. Para que no se crucen (interbloqueo), las dos toman primero este bloqueo consultivo: exclusivo al aplicar el
# esquema, compartido al cargar. Las consultas de solo lectura no lo toman (son cortas y se reintentan).
BLOQUEO_ESQUEMA_EXCLUSIVO = "SELECT pg_advisory_xact_lock(hashtext('pmkb.esquema'))"
BLOQUEO_ESQUEMA_COMPARTIDO = "SELECT pg_advisory_xact_lock_shared(hashtext('pmkb.esquema'))"


def crear_esquema(conn):
    """Aplica esquema.sql en una transacción. Si PostgreSQL la aborta por un interbloqueo con consultas del servicio en
    marcha (toma bloqueos exclusivos de las tablas), se repite: es idempotente y no deja nada a medias."""
    import time
    import psycopg
    sql = (Path(__file__).parent / "esquema.sql").read_text(encoding="utf-8")
    import random
    for intento in range(6):
        try:
            with conn.transaction():
                conn.execute(BLOQUEO_ESQUEMA_EXCLUSIVO)   # espera a las cargas en curso (que lo toman compartido)
                conn.execute(sql)
            return
        except psycopg.errors.DeadlockDetected:
            if intento == 5:
                raise
            time.sleep(0.5 * (intento + 1) + random.random() / 2)   # espera creciente con dispersión: no volver a chocar a la par


def quitar(conn, proyecto):
    """Borra el índice del proyecto, con sus ubicaciones, movimientos, tablero e instantáneas, y sus enlaces compartidos
    (con sus sesiones). La carpeta no se toca."""
    tablas = ("unidad", "documento", "version", "lexema", "arista", "historia", "vector", "indice")
    v = version_esquema(conn)
    if v >= 3:
        tablas += ("ubicacion", "movimiento")
    if v >= 4:
        tablas += ("tablero", "instantanea")
        if conn.execute("SELECT to_regclass('pmkb.enlace') IS NOT NULL").fetchone()[0]:
            tablas += ("enlace",)
    with conn.transaction():
        conn.execute(BLOQUEO_ESQUEMA_COMPARTIDO)
        for t in tablas:
            conn.execute(f"DELETE FROM pmkb.{t} WHERE proyecto = %s", (proyecto,))
