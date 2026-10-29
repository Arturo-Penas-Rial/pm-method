"""Texto compacto de las respuestas (MCP y línea de comandos): pocas líneas por unidad, siempre con la cita."""
import json

from .busqueda import ENCABEZADO


def _sin_marcas(t):
    return (t or "").replace("«", "").replace("»", "")


def buscar(r):
    if "error" in r:
        return "Error: " + r["error"]
    L = [ENCABEZADO, f"Consulta: {r['consulta']} · búsqueda {r['modo']} · filtro {r['filtro']} · ~{r['tokens']} tokens"]
    if r.get("equivalencias"):
        L.append("Equivalencias: " + "; ".join(r["equivalencias"]))
    if not r["resultados"]:
        L.append("Sin resultados en los proyectos visibles.")
    for n, x in enumerate(r["resultados"], 1):
        L.append(f"\n[{n}] " + (x["titulo"] if x["titulo"].startswith(x["id"]) else f"{x['id']} · {x['titulo']}"))
        L.append(f"    cita: {x['cita']} · {x['insignia'] or x['tipo']} · sha {x['sha256']}" + (f" · {x['por_que']}" if x["por_que"] else ""))
        if x["avisos"]:
            L.append("    aviso: " + "; ".join(x["avisos"]))
        if x["tambien_en"]:
            L.append("    también en: " + ", ".join(x["tambien_en"]))
        L.append("    " + _sin_marcas(x["extracto"]))
    for a in r.get("avisos") or []:
        L.append(f"({a})")
    return "\n".join(L)


def ficha(f):
    if "error" in f:
        return "Error: " + f["error"]
    L = [ENCABEZADO, f["titulo"] if f["titulo"].startswith(f["id"]) else f"{f['id']} · {f['titulo']}", f"cita: {f['cita']} · {f['insignia'] or f['tipo']}" + ("" if f["vigente"] else " · no vigente")]
    if f.get("otros_proyectos"):
        L.append("también existe en: " + ", ".join(f["otros_proyectos"]) + " (usar proyecto=…)")
    L += ["", f["texto"]]
    if f["relaciones"]:
        L.append("\nRelaciones (ids):")
        for a in f["relaciones"]:
            flecha = "→" if a["sentido"] == "sale" else "←"
            L.append(f"  {flecha} {a['id']} ({a['tipo']})" + (f" · {a['titulo'][:70]}" if a["titulo"] else " · sin ficha"))
    else:
        L.append("\nRelaciones: ninguna declarada ni mencionada (por ids).")
    if f.get("tambien_en"):
        L.append("También en: " + ", ".join(f["tambien_en"]))
    if f.get("historia"):
        L.append("\nHistoria (bitácora):")
        for h in f["historia"]:
            L.append(f"  #{h['n']} {h['fecha'][:10]} {h['operacion']}" + (f" por {h['por']}" if h["por"] else "") +
                     (f" · {json.dumps(h['cambios'], ensure_ascii=False)[:160]}" if h["cambios"] else ""))
    return "\n".join(L)


def relaciones(r):
    if "error" in r:
        return "Error: " + r["error"]
    L = [f"Relaciones de {r['id']} ({r['proyecto']}): {len(r['nodos'])} nodos, {len(r['aristas'])} aristas" + (" (recortado)" if r["recortado"] else "")]
    tit = {n["id"]: n["titulo"] for n in r["nodos"]}
    for a in r["aristas"]:
        L.append(f"  {a['origen']} → {a['destino']} ({a['tipo']}) · {tit.get(a['destino'], '')[:60] or 'sin ficha'} · {a['cita']}")
    return "\n".join(L)


def documento(d):
    if "error" in d:
        return "Error: " + d["error"]
    L = [ENCABEZADO, f"{d['fuente']} ({d['proyecto']}) · ~{d['tokens']} tokens" + (" · recortado" if d["recortado"] else "")]
    for x in d["fragmentos"]:
        L += [f"\n--- {x['titulo']} · {x['cita']}", x["texto"]]
    return "\n".join(L)


def versiones(v):
    if "error" in v:
        return "Error: " + v["error"]
    L = [f"{v['titulo']} ({v['doc_id']}, {v['proyecto']}) · vigente v{v['version_vigente'] or '—'} · aprobada v{v['version_aprobada'] or '—'}"]
    for x in v["versiones"]:
        marca = " ← vigente" if x["vigente"] else (" ← aprobada" if x["aprobada"] else "")
        L.append(f"  v{x['version'] or '—'} · {x['estado'] or 'sin estado'} · {x['fecha'] or '—'}" +
                 (f" · aprobó {x['aprobado_por']}" if x["aprobado_por"] else "") + (f" ({x['decision']})" if x["decision"] else "") +
                 f" · {x['fuente']}" + (" · copia congelada" if x["copia"] else "") + f" · sha {x['sha256']}{marca}")
    return "\n".join(L)


def cambios(c):
    if "error" in c:
        return "Error: " + c["error"]
    if not c["cambios"]:
        return c.get("aviso") or "Sin cambios por secciones."
    r = c["resumen"]
    L = [f"{c['doc_id']}: v{c['desde']} → v{c['hasta']} · {r['agregada']} agregadas, {r['quitada']} quitadas, {r['modificada']} modificadas"]
    for x in c["cambios"]:
        L += [f"\n[{x['tipo']}] {x['titulo']}", x["resumen"]]
    if c["recortado"]:
        L.append("(recortado por max_tokens)")
    return "\n".join(L)


def contexto(c):
    L = [c["encabezado"], f"Pregunta: {c['pregunta']} · ~{c['tokens']} tokens · {c['modo']}"]
    for n, x in enumerate(c["resultados"], 1):
        L.append(f"\n[{n}] {x['titulo'] if x['titulo'].startswith(x['id']) else x['id'] + ' · ' + x['titulo']} · {x['cita']} · {x['insignia'] or x['tipo']}" + (f" · aviso: {'; '.join(x['avisos'])}" if x["avisos"] else ""))
        L.append(_sin_marcas(x["extracto"]))
    if c["fichas"]:
        L.append("\nFichas de ids citados:")
        for f in c["fichas"]:
            L.append(f"- {f['id']} · {f['titulo']} · {f['cita']}\n  {f['texto'][:400]}")
    return "\n".join(L)


def estado(e):
    L = [f"pm-kb · {len(e['proyectos'])} proyecto(s) visibles" + (f" para {e['persona']}" if e.get("persona") else "")]
    for p in e["proyectos"]:
        L.append(f"  {p['proyecto']}: {p['unidades']} unidades ({p['vigentes']} vigentes), {p['documentos']} documentos "
                 f"({p['documentos_con_versiones']} con versiones), commit {p['commit']}, indexado {p['indexado_en']}, "
                 f"vectores: {p['modelo_vectores']}, omitidos {p['omitidos']}")
    L.append(f"  re-ranqueo: {'sí' if e['re_ranqueo'] else 'no'} · respuesta con modelo: {'sí' if e['respuesta_con_modelo'] else 'no'}")
    return "\n".join(L)
