"""Identidad de documentos y versiones (independiente del motor). docs/PM-KB.md §4.

Documento lógico → versiones → unidades. La identidad sale, en este orden, de:
1. `estado.json.artefactos` (clave, ruta, versión, estado, aprobó, fecha) y las copias congeladas de
   `00-direccion/historial/<clave>-v<versión><ext>` (o la carpeta `<clave>-v<versión>/` de una línea base de BMAD);
2. `decisiones.csv`: "aprobado <clave> v<x>" y "línea base <clave> v<x>" dan la decisión y quién aprobó;
3. el front matter (`version`, `estado`, `aprobado_por`) de un Markdown;
4. el nombre normalizado en la misma carpeta (sin marcas `v2`, `_v1.3`, `rev3`, `final`, `definitivo`, `copia`,
   `borrador`); una fecha en el nombre NO es una versión (serie periódica: documentos distintos).
Nunca se unen dos documentos por parecido de contenido: un casi duplicado no se fusiona solo.

Vigente: la última versión de cada documento (aunque esté en revisión), con su estado a la vista. Aprobada: la última
versión aprobada. Duplicados exactos (misma huella de texto) quedan una vez: la copia canónica es la de gobierno (nunca
la de `historial/`); las demás se listan como "también en".
"""
import os, re
from pathlib import Path

ESTADOS = ["borrador", "en-revision", "aprobado", "obsoleto", "modificado"]
_MARCA = re.compile(r"(?i)(?:[ _.-]+)(?:v(?:ersi[oó]n)?[ _.-]?(\d+(?:[._]\d+)*)|rev[ _.-]?(\d+)|(final|definitivo|definitiva|copia|borrador|draft|copy))(?=$|[\s_.-])")
_DECISION = re.compile(r"^(aprobado|l[ií]nea base)\s+(\S+)\s+v([\w.]+)", re.I)


def orden_version(v):
    partes = re.findall(r"\d+", str(v or ""))
    return tuple(int(p) for p in partes) if partes else (0,)


def nombre_normalizado(stem):
    """(stem sin marcas de versión, versión encontrada o '')."""
    version, base = "", stem
    for m in list(_MARCA.finditer(stem))[::-1]:
        if m.group(1) or m.group(2):
            version = version or (m.group(1) or m.group(2)).replace("_", ".")
        base = base[:m.start()] + base[m.end():]
    return base.strip(" _.-").lower(), version


def prioridad_canonica(fuente, gestion):
    """Menor = preferida como copia canónica de un duplicado exacto."""
    if "/00-direccion/historial/" in "/" + fuente:
        return 9
    if gestion and (fuente == gestion or fuente.startswith(gestion.rstrip("/") + "/")) or not gestion:
        return 0 if "/03-control/registros/" in "/" + fuente or fuente.endswith("estado.json") else 1
    if fuente.startswith("_bmad-output/"):
        return 2
    return 5


def decisiones_aprobacion(filas):
    """{(clave, versión): {decision_id, aprobado_por, fecha}} desde decisiones.csv."""
    out = {}
    for f in filas:
        m = _DECISION.match((f.get("decision") or "").strip())
        if m:
            out[(m.group(2), m.group(3))] = {"decision_id": f.get("id", ""), "aprobado_por": f.get("decidido_por", ""), "fecha": f.get("fecha", "")}
    return out


def asignar(docs, estado, decisiones, gestion="", rutas=None):
    """Completa en cada unidad doc_id, version, estado_doc, vigente, aprobada, duplicado_de y copia.
    `rutas` ({clave: fuente}) da la ruta real de un artefacto cuya ruta de estado.json ya no existe y que se encontró en
    otro lugar (enlaces.resolver_artefactos): ese archivo conserva la identidad `art:<clave>` y su versión.
    Devuelve (documentos, versiones): filas para las tablas `documento` y `version`."""
    g = (gestion.rstrip("/") + "/") if gestion else ""
    por_ruta = {d["fuente"]: d for d in docs}
    aprob = decisiones_aprobacion(decisiones)
    ident = {}                      # fuente → dict(doc_id, version, estado, aprobado_por, fecha, decision_id, origen, copia, clave)

    def poner(fuente, **kw):
        if fuente in por_ruta and fuente not in ident:
            ident[fuente] = kw

    arts = (estado or {}).get("artefactos") or {}
    for clave, a in sorted(arts.items()):
        ver = str(a.get("version") or "")
        dec = aprob.get((clave, ver), {})
        base = {"estado": a.get("estado", ""), "aprobado_por": a.get("aprobado_por") or dec.get("aprobado_por", ""),
                "fecha": a.get("fecha") or dec.get("fecha", ""), "decision_id": dec.get("decision_id", ""), "clave": clave}
        if a.get("externo") == "bmad":
            copia_dir = g + (a.get("copia") or os.path.dirname(a.get("ruta", ""))).replace(os.sep, "/")
            for r in a.get("rutas_bmad") or []:
                nombre = os.path.basename(r)
                copia = f"{copia_dir}/{nombre}"
                doc_id = f"art:{clave}:{nombre}"
                poner(copia, doc_id=doc_id, version=ver, origen="historial", copia=True, **{**base, "estado": "aprobado"})
                viva = r.replace(os.sep, "/")
                if viva in por_ruta and copia in por_ruta and por_ruta[viva]["sha_texto"] != por_ruta[copia]["sha_texto"]:
                    poner(viva, doc_id=doc_id, version=f"{ver}+", origen="bmad", copia=False,
                          **{**base, "estado": "modificado", "aprobado_por": "", "decision_id": ""})
                else:
                    poner(viva, doc_id=doc_id, version=ver, origen="bmad", copia=False, **base)
            continue
        ruta = (rutas or {}).get(clave) or g + str(a.get("ruta", "")).replace(os.sep, "/")
        doc_id = f"art:{clave}"
        hist = f"{g}00-direccion/historial/"
        copias = sorted(f for f in por_ruta if f.startswith(hist) and re.fullmatch(re.escape(clave) + r"-v([\w.]+?)(\.\w+)?", f[len(hist):]))
        for c in copias:
            vc = re.fullmatch(re.escape(clave) + r"-v([\w.]+?)(\.\w+)?", c[len(hist):]).group(1)
            dc = aprob.get((clave, vc), {})
            poner(c, doc_id=doc_id, version=vc, estado="aprobado", aprobado_por=dc.get("aprobado_por", ""), fecha=dc.get("fecha", ""),
                  decision_id=dc.get("decision_id", ""), origen="historial", copia=True, clave=clave)
        copia_misma = f"{hist}{clave}-v{ver}{Path(ruta).suffix}"
        if a.get("estado") == "aprobado" and copia_misma in por_ruta and ruta in por_ruta and por_ruta[ruta]["sha_texto"] != por_ruta[copia_misma]["sha_texto"]:
            poner(ruta, doc_id=doc_id, version=f"{ver}+", origen="estado.json", copia=False,
                  **{**base, "estado": "modificado", "aprobado_por": "", "decision_id": ""})
        else:
            poner(ruta, doc_id=doc_id, version=ver or "1", origen="estado.json", copia=False, **base)

    # front matter y nombre normalizado para el resto
    grupos = {}
    for d in docs:
        if d["fuente"] in ident:
            continue
        p = Path(d["fuente"])
        base, vnom = nombre_normalizado(p.stem)
        grupos.setdefault((str(p.parent), base, p.suffix.lower()), []).append((d, vnom))
    for (carpeta, base, ext), miembros in grupos.items():
        varias = len(miembros) > 1
        for d, vnom in miembros:
            fm = d.get("fm") or {}
            ver = str(fm.get("version") or vnom or "")
            if varias:
                doc_id, origen = f"nom:{carpeta}/{base}{ext}", "nombre"
            else:
                doc_id, origen = f"ruta:{d['fuente']}", ("frontmatter" if fm.get("version") else "ruta")
            est = (fm.get("estado") or "").lower()
            ident[d["fuente"]] = {"doc_id": doc_id, "version": ver, "estado": est if est in ESTADOS else "",
                                  "aprobado_por": fm.get("aprobado_por", ""), "fecha": fm.get("fecha_aprobacion") or fm.get("fecha", ""),
                                  "decision_id": "", "origen": origen, "copia": False, "clave": ""}

    # versiones por documento: orden, vigente (última) y aprobada (última aprobada)
    por_doc = {}
    for d in docs:
        i = ident[d["fuente"]]
        por_doc.setdefault(i["doc_id"], []).append(d)
    documentos, versiones = [], []
    for doc_id, ds in por_doc.items():
        def clave_orden(d):
            i = ident[d["fuente"]]
            return (orden_version(i["version"]) if i["version"] else (0,), i["version"].endswith("+"), d.get("fecha_archivo", 0), not i["copia"])
        ds.sort(key=clave_orden)
        ultima = ds[-1]
        ver_ult = ident[ultima["fuente"]]["version"]
        canonicas_ult = [d for d in ds if ident[d["fuente"]]["version"] == ver_ult and d["sha_texto"] == ultima["sha_texto"]]
        vig = min(canonicas_ult, key=lambda d: (ident[d["fuente"]]["copia"], prioridad_canonica(d["fuente"], gestion), d["fuente"]))
        aprobadas = [d for d in ds if ident[d["fuente"]]["estado"] == "aprobado"]
        apr = None
        if aprobadas:
            va = ident[aprobadas[-1]["fuente"]]["version"]
            mismas = [d for d in aprobadas if ident[d["fuente"]]["version"] == va]
            # si la vigente es la misma versión aprobada con el mismo texto, la canónica es la vigente
            apr = vig if (vig in mismas or any(m["sha_texto"] == vig["sha_texto"] for m in mismas) and ident[vig["fuente"]]["estado"] == "aprobado") \
                else min(mismas, key=lambda d: (ident[d["fuente"]]["copia"], d["fuente"]))
        primero = ident[vig["fuente"]]
        documentos.append({"doc_id": doc_id, "titulo": vig["titulo"], "tipo": vig["formato"], "clave_pm": primero.get("clave", ""),
                           "version_vigente": ident[vig["fuente"]]["version"], "version_aprobada": ident[apr["fuente"]]["version"] if apr else "",
                           "fuente_vigente": vig["fuente"], "fuente_aprobada": apr["fuente"] if apr else "",
                           "versiones": len({ident[d["fuente"]]["version"] for d in ds})})
        for n, d in enumerate(ds):
            i = ident[d["fuente"]]
            versiones.append({"doc_id": doc_id, "version": i["version"], "orden": n, "fecha": i["fecha"], "estado": i["estado"],
                              "aprobado_por": i["aprobado_por"], "decision_id": i["decision_id"], "fuente": d["fuente"],
                              "sha256_archivo": d["sha_archivo"], "sha256_texto": d["sha_texto"], "origen": i["origen"], "copia": i["copia"]})
            es_vig, es_apr = d is vig, d is apr
            for u in d["unidades"]:
                u.update({"doc_id": doc_id, "version": i["version"], "estado_doc": i["estado"], "vigente": es_vig,
                          "aprobada": es_apr, "copia": i["copia"], "duplicado_de": ""})
                if u.get("registro"):
                    u["aprobada"] = True          # las filas de registro son la fuente de gobierno
                if not es_vig and d["sha_texto"] == vig["sha_texto"]:
                    u["duplicado_de"] = vig["fuente"]

    # duplicados exactos entre documentos distintos: una sola unidad vigente por huella
    vistos = {}
    vig_units = [u for d in docs for u in d["unidades"] if u["vigente"]]
    vig_units.sort(key=lambda u: (prioridad_canonica(u["fuente"], gestion), u["fuente"], u["id"]))
    for u in vig_units:
        if len(u["texto"]) < 40:          # textos muy cortos (un encabezado suelto) no se colapsan
            continue
        if u["sha"] in vistos and vistos[u["sha"]]["doc_id"] != u["doc_id"]:
            u["vigente"] = False
            u["duplicado_de"] = vistos[u["sha"]]["id"]
            vistos[u["sha"]].setdefault("tambien_en", []).append(u["fuente"] + (f":{u['rango']}" if u["rango"] else ""))
        else:
            vistos.setdefault(u["sha"], u)
    return documentos, versiones


def cambios(secciones_a, secciones_b, max_diff=600):
    """Diff por secciones entre dos versiones: listas de (seccion_id, titulo, texto) → [{tipo, seccion, titulo, resumen}]."""
    import difflib
    a = {s: (t, x) for s, t, x in secciones_a}
    b = {s: (t, x) for s, t, x in secciones_b}
    out = []
    for s, (t, x) in b.items():
        if s not in a:
            out.append({"tipo": "agregada", "seccion": s, "titulo": t, "resumen": x[:max_diff]})
        elif a[s][1] != x:
            dif = [l for l in difflib.unified_diff(a[s][1].splitlines(), x.splitlines(), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
            out.append({"tipo": "modificada", "seccion": s, "titulo": t, "resumen": "\n".join(dif)[:max_diff]})
    for s, (t, x) in a.items():
        if s not in b:
            out.append({"tipo": "quitada", "seccion": s, "titulo": t, "resumen": x[:max_diff]})
    return out
