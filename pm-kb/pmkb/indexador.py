"""Indexar un proyecto: carpeta → unidades, versiones y aristas → PostgreSQL, en una sola transacción.

El índice de un proyecto se reemplaza entero dentro de la transacción: quien consulta ve el índice anterior o el nuevo,
nunca la mitad. Los vectores (si hay modelo configurado) se reutilizan por huella del texto (`cache_vector`).
"""
import csv, json, os, re, subprocess
from pathlib import Path

from . import VERSION, config, fuentes, modelos, relaciones, versiones

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


def preparar(raiz, excluir=None, restringir=None):
    """Lectura y armado en memoria (sin base): devuelve un dict con todo lo que se carga."""
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
    documentos, vers = versiones.asignar(docs, estado, decisiones, gestion)
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
            "nombre_proyecto": estado.get("nombre", "")}


def _copy(cur, tabla, columnas, filas):
    with cur.copy(f"COPY pmkb.{tabla} ({', '.join(columnas)}) FROM STDIN") as cp:
        for f in filas:
            cp.write_row(f)


def cargar(conn, proyecto, prep, con_vectores=True, avisar=print):
    proyecto = validar_nombre(proyecto)
    us = prep["unidades"]
    with conn.transaction():
        cur = conn.cursor()
        for t in ("unidad", "documento", "version", "lexema", "arista", "historia", "vector", "indice"):
            cur.execute(f"DELETE FROM pmkb.{t} WHERE proyecto = %s", (proyecto,))
        _copy(cur, "unidad", ["proyecto", "id", "doc_id", "version", "tipo", "registro", "titulo", "texto", "fuente", "rango",
                              "seccion", "estado_doc", "vigente", "aprobada", "copia", "duplicado_de", "circulacion", "confianza",
                              "sha", "tambien_en"],
              ([proyecto, u["id"], u["doc_id"], u["version"], u["tipo"], u.get("registro") or "", u["titulo"], u["texto"], u["fuente"],
                u["rango"], u.get("seccion") or "", u.get("estado_doc") or "", u["vigente"], u["aprobada"], u.get("copia", False),
                u.get("duplicado_de") or "", u["circulacion"], u["confianza"], u["sha"], u.get("tambien_en") or None] for u in us))
        _copy(cur, "documento", ["proyecto", "doc_id", "titulo", "tipo", "clave_pm", "version_vigente", "version_aprobada",
                                 "fuente_vigente", "fuente_aprobada", "versiones"],
              ([proyecto, d["doc_id"], d["titulo"], d["tipo"], d["clave_pm"], d["version_vigente"], d["version_aprobada"],
                d["fuente_vigente"], d["fuente_aprobada"], d["versiones"]] for d in prep["documentos"]))
        _copy(cur, "version", ["proyecto", "doc_id", "version", "orden", "fecha", "estado", "aprobado_por", "decision_id", "fuente",
                               "sha256_archivo", "sha256_texto", "origen", "copia"],
              ([proyecto, v["doc_id"], v["version"], v["orden"], v["fecha"], v["estado"], v["aprobado_por"], v["decision_id"],
                v["fuente"], v["sha256_archivo"], v["sha256_texto"], v["origen"], v["copia"]] for v in prep["versiones"]))
        _copy(cur, "arista", ["proyecto", "origen", "destino", "tipo", "fuente", "rango"], ([proyecto, *a] for a in prep["aristas"]))
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
                vs = modelos.vectores(emb, [faltan[s] for s in shas])
                _copy(cur, "cache_vector", ["sha", "modelo", "emb"], ([s, modelo, "[" + ",".join(f"{x:.6f}" for x in v) + "]"] for s, v in zip(shas, vs)))
            cur.execute("""INSERT INTO pmkb.vector (proyecto, unidad_id, modelo, emb)
                           SELECT u.proyecto, u.id, c.modelo, c.emb FROM pmkb.unidad u JOIN pmkb.cache_vector c ON c.sha = u.sha AND c.modelo = %s
                           WHERE u.proyecto = %s AND u.vigente""", (modelo, proyecto))
        cur.execute("""INSERT INTO pmkb.indice (proyecto, raiz, commit_git, unidades, documentos, vigentes, avgdl, version_kb, modelo, omitidos)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (proyecto, prep["raiz"], prep["commit"], len(us), len(prep["documentos"]), n_vig, float(avgdl), VERSION, modelo,
                     json.dumps([{"fuente": f, "motivo": m} for f, m in prep["omitidos"]], ensure_ascii=False)))
    return {"unidades": len(us), "vigentes": n_vig, "documentos": len(prep["documentos"]),
            "con_versiones": sum(1 for d in prep["documentos"] if d["versiones"] > 1), "aristas": len(prep["aristas"]),
            "historia": len(prep["historia"]), "omitidos": len(prep["omitidos"]), "modelo": modelo, "commit": prep["commit"]}


def crear_esquema(conn):
    sql = (Path(__file__).parent / "esquema.sql").read_text(encoding="utf-8")
    with conn.transaction():
        conn.execute(sql)


def quitar(conn, proyecto):
    with conn.transaction():
        for t in ("unidad", "documento", "version", "lexema", "arista", "historia", "vector", "indice"):
            conn.execute(f"DELETE FROM pmkb.{t} WHERE proyecto = %s", (proyecto,))
