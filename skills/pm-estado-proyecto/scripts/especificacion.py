#!/usr/bin/env python3
"""Fachada única de especificación: todas las skills consultan requisitos, épicas e historias por aquí,
sin leer directamente BMAD ni requisitos.md. Single specification façade used by every skill.

Proveedores (según estado.json.integraciones.especificacion):
  - "bmad"     → BMAD es la fuente (vía pm-bmad-puente/scripts/bmad.py, solo lectura).
  - otro valor → pm-method es la fuente: 02-planificacion/requisitos.md (filas REQ-nnn), backlog.csv y wbs.csv.
El índice 02-planificacion/especificacion/spec-index.json (esquema pm-spec-index/1) es un CACHÉ derivado:
se reconstruye solo cuando cambian las fuentes (lectura a través). Nunca se edita ni se usa como fuente.

Uso / Usage:
  especificacion.py --proyecto ./p fuente                          # proveedor, dueños de cada dato, frescura
  especificacion.py --proyecto ./p resumen [--json]
  especificacion.py --proyecto ./p consultar FR-3 | REQ-004 | 1-2-login | E-2   [--json]
  especificacion.py --proyecto ./p listar requisitos|historias|epicas [--estado done] [--epica E-1] [--cobertura sin-cobertura|planificado|en-curso|terminado] [--limite 60] [--json]
  especificacion.py --proyecto ./p indice                          # fuerza la reconstrucción
"""
import argparse, csv, datetime, hashlib, json, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import esquema as E

ESQUEMA = "pm-spec-index/1"
REQ = re.compile(r"\b(REQ|FR|NFR|UJ|SM|AD|UX-DR)-?(\d+)\b")

def ruta_indice(p): return os.path.join(p, "02-planificacion", "especificacion", "spec-index.json")

def bmad_mod():
    cand = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-bmad-puente", "scripts"))
    if not os.path.isdir(cand): sys.exit("Proveedor bmad configurado pero no se encuentra la skill pm-bmad-puente instalada junto a pm-estado-proyecto.")
    sys.path.insert(0, cand)
    import bmad
    return bmad

def sha_archivos(rutas):
    h = hashlib.sha256()
    for r in rutas:
        if os.path.exists(r): h.update(open(r, "rb").read())
        h.update(os.path.basename(r).encode())   # independiente de cómo se escriba la ruta
    return h.hexdigest()

def fuentes_nativas(p):
    return [os.path.join(p, "02-planificacion", x) for x in ("requisitos.md", "backlog.csv", "wbs.csv")]

def huella(p, e):
    if e.get("integraciones", {}).get("especificacion") == "bmad":
        return bmad_mod().huella_actual(p, e) + sha_archivos([os.path.join(p, "02-planificacion", x) for x in ("backlog.csv", "wbs.csv")])
    return sha_archivos(fuentes_nativas(p))

def norm(t, n): return f"{t}-{int(n):03d}" if t == "REQ" else f"{t}-{int(n)}"

def indice_nativo(p):
    reqs = []
    pr = os.path.join(p, "02-planificacion", "requisitos.md")
    if os.path.exists(pr):
        pos = {}   # columnas por encabezado de la tabla (Interesado, Categoría, Prioridad, Estado); sin encabezado, el orden de la plantilla
        for i, l in enumerate(open(pr, encoding="utf-8"), 1):
            cab = [c.strip().split("/")[0].strip().lower() for c in l.strip().strip("|").split("|")] if l.lstrip().startswith("|") else []
            if cab and cab[0] in ("id", "ids") and len(cab) >= 3:
                pos = {}
                for j, c in enumerate(cab):
                    for k, pref in (("interesado", ("interesado", "stakeholder", "solicitante")), ("categoria", ("categor",)),
                                    ("prioridad", ("prioridad", "priority")), ("estado_req", ("estado", "status"))):
                        if c.startswith(pref) and k not in pos: pos[k] = j
                continue
            m = re.match(r"^\|\s*(REQ-?\d+)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|", l)
            if m and "{{" not in l:
                mm = REQ.match(m.group(1)); cols = [c.strip() for c in l.strip().strip("|").split("|")]
                celda = lambda k: cols[pos[k]] if k in pos and pos[k] < len(cols) else ""
                reqs.append({"id": norm(mm.group(1), mm.group(2)), "tipo": "REQ", "titulo": m.group(2).strip()[:200], "fuente": "02-planificacion/requisitos.md",
                             "linea": i, "interesado": celda("interesado") if pos else m.group(3).strip(),
                             "categoria": celda("categoria") if pos else m.group(4).strip(), "prioridad": celda("prioridad") if pos else m.group(5).strip(),
                             "estado_req": celda("estado_req") if pos else (cols[-1] if len(cols) >= 10 else "")})
    hist, wref = [], {}
    pw = os.path.join(p, "02-planificacion", "wbs.csv")
    if os.path.exists(pw):
        for r in csv.DictReader(open(pw, encoding="utf-8")):
            for x in re.split(r"[;, ]+", r.get("ref") or ""):
                x = x.strip()
                m = REQ.match(x)
                if m: wref.setdefault(norm(m.group(1), m.group(2)), []).append(r["codigo"])
                elif x: wref.setdefault(x, []).append(r["codigo"])
    pb = os.path.join(p, "02-planificacion", "backlog.csv")
    if os.path.exists(pb):
        for f in csv.DictReader(open(pb, encoding="utf-8")):
            if f.get("tipo", "historia") not in ("historia", "story", "") and f.get("tipo") != "epica": continue
            refs = sorted({norm(m.group(1), m.group(2)) for m in REQ.finditer((f.get("refs") or "") + " " + (f.get("producto_pbs") or "") + " " + (f.get("criterios_aceptacion") or ""))})
            hist.append({"id": f["id"], "numero": f["id"], "epica": f.get("epica") or "", "titulo": f.get("titulo", ""), "estado": f.get("estado", ""),
                         "refs": refs, "paquetes_wbs": wref.get(f["id"], []), "gobierno": {k: f.get(k, "") for k in ("prioridad", "moscow", "estimacion", "iteracion", "release", "producto_pbs")}})
    for q in reqs:
        hh = [h["id"] for h in hist if q["id"] in h["refs"]]
        q["historias"] = hh; q["paquetes_wbs"] = wref.get(q["id"], [])
        est = [h["estado"] for h in hist if h["id"] in hh]
        if not hh and q["paquetes_wbs"]: q["cobertura"] = "planificado"      # cubierto por la WBS aunque no haya historias
        elif not hh: q["cobertura"] = "sin-cobertura"
        elif all(x in ("done", "terminado", "hecho") for x in est): q["cobertura"] = "terminado"
        elif any(x not in ("backlog", "ready-for-dev", "pendiente", "") for x in est): q["cobertura"] = "en-curso"
        else: q["cobertura"] = "planificado"
    return {"esquema": ESQUEMA, "generado": datetime.datetime.now().isoformat(timespec="seconds"), "proveedor": "pm-method",
            "fuente": {"archivos": ["02-planificacion/requisitos.md", "02-planificacion/backlog.csv", "02-planificacion/wbs.csv"]},
            "dueños": {"requisitos": "pm-method requisitos.md (pm-planificacion-por-productos)", "backlog y gobierno": "pm-method backlog.csv",
                       "paquetes_wbs": "pm-method wbs.csv (columna ref)"},
            "requisitos": reqs, "epicas": [], "historias": hist,
            "resumen": {"requisitos": len(reqs), "sin_cobertura": [q["id"] for q in reqs if q["cobertura"] == "sin-cobertura"], "historias": len(hist)}}

def obtener(p, forzar=False):
    e = E.cargar_estado(p)
    h = huella(p, e); ri = ruta_indice(p)
    if not forzar and os.path.exists(ri):
        idx = json.load(open(ri, encoding="utf-8"))
        if idx.get("esquema") == ESQUEMA and idx.get("_huella") == h: return idx, False
    idx = bmad_mod().construir_indice(p, e) if e.get("integraciones", {}).get("especificacion") == "bmad" else indice_nativo(p)
    idx["_huella"] = h
    os.makedirs(os.path.dirname(ri), exist_ok=True); E.escribir_json(ri, idx)   # atómica: otra consulta simultánea no lee un índice a medias
    return idx, True

def mostrar(x, como_json):
    if como_json: print(json.dumps(x, ensure_ascii=False, indent=2)); return
    if isinstance(x, list):
        for i in x: print(" | ".join(f"{k}={v}" for k, v in i.items() if v not in ("", [], {}, None) and k not in ("fuente", "linea")))
    else:
        for k, v in x.items():
            if v not in ("", [], {}, None): print(f"{k}: {v}")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fuente"); sub.add_parser("indice")
    r = sub.add_parser("resumen"); r.add_argument("--json", action="store_true")
    c = sub.add_parser("consultar"); c.add_argument("id"); c.add_argument("--json", action="store_true")
    l = sub.add_parser("listar"); l.add_argument("tipo", choices=["requisitos", "historias", "epicas"]); l.add_argument("--estado"); l.add_argument("--epica"); l.add_argument("--limite", type=int, default=60, help="máximo de filas (0 = sin límite); protege el contexto en proyectos grandes")
    l.add_argument("--cobertura"); l.add_argument("--json", action="store_true")
    a = ap.parse_args()
    idx, nuevo = obtener(a.proyecto, forzar=(a.cmd == "indice"))
    if a.cmd == "indice": print(f"Índice reconstruido ({idx['proveedor']}): {len(idx['requisitos'])} requisitos/ids, {len(idx['historias'])} historias → {os.path.relpath(ruta_indice(a.proyecto))}"); return
    if a.cmd == "fuente":
        print(f"Proveedor de especificación: {idx['proveedor']} · índice {'reconstruido ahora' if nuevo else 'vigente'} ({idx['generado']})")
        for k, v in idx.get("dueños", {}).items(): print(f"  dueño de {k}: {v}")
        if idx["proveedor"] == "bmad": print(f"  BMAD {idx['fuente']['layout']} · soporte {idx['fuente']['soporte']} · líneas base: {idx.get('lineas_base') or 'ninguna'}")
        return
    if a.cmd == "resumen": mostrar(idx["resumen"], a.json); return
    if a.cmd == "consultar":
        q = a.id.strip()
        m = REQ.match(q)
        if m: q = norm(m.group(1), m.group(2))
        for col in ("requisitos", "historias", "epicas"):
            for x in idx.get(col, []):
                if x["id"] == q or x.get("numero") == q: mostrar({"tipo_entidad": col[:-1] if col != "epicas" else "epica", **x}, a.json); return
        if re.match(r"^\d+[-.]\d+[a-z]?$", q):   # historia por número: 1-2 o 1.2 (clave BMAD 1-2-slug)
            for x in idx.get("historias", []):
                if x.get("numero") == q.replace("-", ".") or x["id"].startswith(q.replace(".", "-") + "-"): mostrar({"tipo_entidad": "historia", **x}, a.json); return
        sys.exit(f"No se encontró {a.id} en la especificación ({idx['proveedor']}).")
    if a.cmd == "listar":
        xs = idx.get(a.tipo, [])
        if a.estado: xs = [x for x in xs if x.get("estado") == a.estado]
        if a.epica: xs = [x for x in xs if x.get("epica") == a.epica or x.get("id") == a.epica]
        if a.cobertura: xs = [x for x in xs if x.get("cobertura") == a.cobertura]
        total = len(xs)
        if a.limite and total > a.limite and not a.json:
            mostrar(xs[:a.limite], a.json)
            print(f"… {total - a.limite} de {total} más sin mostrar: filtrar con --estado/--epica/--cobertura o usar --limite 0 · "
                  f"{total - a.limite} of {total} more not shown: filter or use --limite 0")
            return
        mostrar(xs, a.json)

if __name__ == "__main__":
    main()
