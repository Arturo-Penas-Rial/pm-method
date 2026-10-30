"""Texto compacto de las respuestas (MCP y línea de comandos): pocas líneas por unidad, siempre con la cita."""
import json

from .busqueda import ENCABEZADO, tokens


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


def _ubicacion(f):
    u = f.get("ubicacion")
    if not u:
        return []
    donde = u["ruta"] + (f":{u['rango']}" if u.get("rango") else "")
    tipo = {"fila": "fila de registro", "artefacto": "artefacto de estado.json", "documento": "documento",
            "puerta": "puerta de estado.json", "producto": "producto (estado.py productos)"}.get(u["tipo"], u["tipo"])
    L = [f"ubicación ({tipo} {u['ref']}): {donde or '—'}" + (f" · desde {u['desde'][:10]}" if u.get("desde") else "")
         + (f" · verificación: {u['lista']}" if u.get("lista") else "")]
    return L


def _en_tablero(f):
    b = f.get("tablero")
    if not b:
        return []
    return [f"en el tablero (versión {b.get('tablero_version')}, corte {b.get('corte')}): vista {b.get('vista')} · columna {b.get('columna') or '—'}"
            + (f" · señales: {', '.join(b['senales'])}" if b.get("senales") else "")]


def ficha(f):
    if "error" in f:
        return "Error: " + f["error"]
    L = [ENCABEZADO, f["titulo"] if f["titulo"].startswith(f["id"]) else f"{f['id']} · {f['titulo']}", f"cita: {f['cita']} · {f['insignia'] or f['tipo']}" + ("" if f["vigente"] else " · no vigente")]
    if f.get("otros_proyectos"):
        L.append("también existe en: " + ", ".join(f["otros_proyectos"]) + " (usar proyecto=…)")
    L += _ubicacion(f)
    L += _en_tablero(f)
    for a in f.get("avisos") or []:
        L.append("aviso: " + a)
    v = f.get("versiones")
    if v:
        L.append(f"versiones: vigente v{v['vigente'] or '—'} · aprobada v{v['aprobada'] or '—'} ({v['doc_id']}, {v['n']} en total)")
    L += ["", f["texto"]]
    if f["relaciones"]:
        L.append("\nRelaciones (ids):")
        for a in f["relaciones"]:
            flecha = "→" if a["sentido"] == "sale" else "←"
            L.append(f"  {flecha} {a['id']} ({a['tipo']})" + (f" · {a['titulo'][:70]}" if a["titulo"] else " · sin ficha"))
    else:
        L.append("\nRelaciones: ninguna declarada ni mencionada (por ids).")
    rel = f.get("relacionados") or {}
    if rel:
        L.append("\nRelacionados por id: " + " · ".join(f"{g} " + ", ".join(x["id"] for x in xs[:12]) + (" …" if len(xs) > 12 else "")
                                                      for g, xs in rel.items()))
    if f.get("tambien_en"):
        L.append("También en: " + ", ".join(f["tambien_en"]))
    if len(f.get("movimientos") or []) > 1:
        L.append("\nMovimientos: " + "; ".join(m["texto"] for m in f["movimientos"][1:]))
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


def enlaces(e):
    if "error" in e:
        return "Error: " + e["error"]
    L = [f"Enlaces de {e['proyecto']} (indexado {e['indexado_en']}; carpeta {e['raiz']})"]
    if e["artefactos"]:
        L.append(f"\nArtefactos con la ruta de estado.json inexistente ({len(e['artefactos'])}):")
        for a in e["artefactos"]:
            L.append(f"  {a['ref']}: estado.json → {a['declarada']} (no existe)" +
                     (f" · encontrado en {a['sugerida']} por {a['encontrada_por']}" if a["sugerida"] else " · no se encontró por huella ni por nombre"))
            L.append(f"    acción: {a['accion']}")
    if e["citas"]:
        L.append(f"\nCitas a rutas que no existen ({len(e['citas'])}):")
        for c in e["citas"]:
            L.append(f"  {c['fuente']}" + (f":{c['rango']}" if c["rango"] else "") + f" ({c['id']}) cita «{c['ruta_citada']}»" +
                     (f" · ahora en {c['sugerida']} (por {c['como']})" if c["sugerida"] else ""))
            nota = "" if c.get("historica") else (" (opcional: el movimiento registrado ya la resuelve)" if c.get("resuelta") else "")
            L.append(f"    acción{nota}: {c['accion']}")
    if e["movimientos"]:
        L.append(f"\nMovimientos detectados ({len(e['movimientos'])}; el enlace por id sigue funcionando):")
        for m in e["movimientos"][:50]:
            L.append(f"  {m['fecha'][:10]} · {m['ref']} ({m['tipo']}): {m['de']} → {m['a']} ({m['motivo']})")
        if len(e["movimientos"]) > 50:
            L.append(f"  … y {len(e['movimientos']) - 50} más (--json)")
    if not (e["artefactos"] or e["citas"]):
        L.append("Sin referencias rotas." + ("" if e["movimientos"] else " Sin movimientos."))
    for a in e.get("avisos") or []:
        L.append(f"(aviso: {a})")
    return "\n".join(L)


GRUPOS = ("decidir", "escalar", "desbloquear", "vigilar")


def _recortar(L, tope):
    """Líneas dentro del tope de tokens (estimación de busqueda.tokens), con aviso si se corta."""
    out, usados = [], 0
    for l in L:
        usados += tokens(l) + 1
        if out and usados > tope:
            out.append(f"(recortado por max_tokens={tope}; pedir el detalle de cada tarjeta con `ficha`)")
            break
        out.append(l)
    return "\n".join(out)


def tablero(r, tope=1500):
    """Tablero (actual o instantánea) en texto compacto: pulso, puertas, atención, entrega y artefactos, con la ref de cada tarjeta."""
    if "error" in r:
        return "Error: " + r["error"]
    d, ins = r.get("datos") or {}, r.get("instantanea")
    c, at = d.get("ciclo") or {}, d.get("atencion") or {}
    L = [ENCABEZADO,
         f"Tablero de {r['proyecto']} ({d.get('proyecto', '')}) · " + (f"instantánea {ins['id']} «{ins.get('etiqueta', '')}»" if ins
                                                                     else f"actual, versión {r.get('version')} publicada {str(r.get('generado_en', ''))[:16]}")
         + f" · corte {d.get('corte')} · huella {d.get('huella')}",
         f"Fase {c.get('fase')} · proceso {c.get('proceso')} · etapa {c.get('etapa')}" + (f" «{c['nombre_etapa']}»" if c.get("nombre_etapa") else "")
         + (f" · fin previsto {c['fin_previsto']}" if c.get("fin_previsto") else "") + (f" · EXCEPCIÓN ABIERTA {c['excepcion']}" if c.get("excepcion") else "")]
    if ins and ins.get("decision"):
        L.append(f"Congelada antes de: {ins.get('puerta') or ins.get('etiqueta')} → {ins['decision']}" + (f" ({ins['decision_id']})" if ins.get("decision_id") else ""))
    for col in c.get("columnas") or []:
        if col.get("puerta") and col.get("estado") == "proxima":
            hs = col.get("hallazgos") or []
            L.append(f"Próxima puerta [{(col.get('tarjeta') or {}).get('ref', '')}]: {col.get('tipo')} · "
                     + (", ".join(f"{h.get('severidad')} {h.get('id')}" for h in hs) or "sin hallazgos"))
        for x in col.get("decisiones") or []:
            L.append(f"  puerta [{x['ref']}] {x.get('decision')} {x.get('fecha')} {x.get('decision_id') or ''}".rstrip()
                     + (" · " + ", ".join(x["senales"]) if x.get("senales") else ""))
    tot = at.get("totales") or {}
    L.append("Atención: " + " · ".join(f"{g} {tot.get(g, 0)}" for g in GRUPOS))
    for i in sorted(at.get("items") or [], key=lambda i: (i.get("prioridad") or 9)):
        L.append(f"  [{i['ref']}] {i.get('grupo')} P{i.get('prioridad')} {i.get('regla')} · {i.get('nombre')}" + (f" · {i['responsable']}" if i.get("responsable") else ""))
    ent = d.get("entrega") or {}
    pr = (ent.get("productos") or {}).get("tarjetas") or []
    if pr:
        cuenta = {}
        for x in pr:
            cuenta[x.get("estado")] = cuenta.get(x.get("estado"), 0) + 1
        L.append(f"Productos ({len(pr)}): " + ", ".join(f"{k} {v}" for k, v in cuenta.items()))
    for reg, v in (ent.get("control") or {}).items():
        if v.get("tarjetas") or v.get("propuestas"):
            L.append(f"{reg.capitalize()} abiertos: " + ", ".join(f"[{x['ref']}] {x.get('estado')}" for x in v.get("tarjetas") or [])
                     + (f" · propuestas pendientes: {', '.join(x['ref'] for x in v['propuestas'])}" if v.get("propuestas") else ""))
    A = d.get("artefactos") or {}
    for g in A.get("grupos") or []:
        if g.get("claves"):
            el = A.get("elementos") or {}
            L.append(f"Artefactos · {g.get('nombre')}: " + ", ".join(f"{k} ({(el.get(k) or {}).get('estado') or '—'})" for k in g["claves"]))
    for a in d.get("avisos") or []:
        L.append(f"aviso: {a}")
    return _recortar(L, tope)


def historial(h):
    if "error" in h:
        return "Error: " + h["error"]
    L = [f"Historial del tablero de {h['proyecto']}: {len(h['instantaneas'])} instantánea(s) congelada(s)"]
    for x in h["instantaneas"]:
        L.append(f"  {x['id']} · {x.get('etiqueta')}" + (f" · {x['decision']}" if x.get("decision") else "")
                 + (f" ({x['decision_id']})" if x.get("decision_id") else "") + (f" · fase {x['fase']}" if x.get("fase") else "")
                 + ("" if x.get("en_bitacora") is not False else " · MODIFICADA fuera de los scripts"))
    a = h.get("actual")
    L.append(f"  actual: versión {a['version']} publicada {a['generado_en'][:16]} (corte {a['corte']})" if a else "  actual: sin tablero publicado")
    return "\n".join(L)


def comparacion(c, tope=1500):
    if "error" in c:
        return "Error: " + c["error"]
    L = [f"{c['proyecto']}: {c['a']} ({c['corte_a']}) → {c['b']} ({c['corte_b']}): {len(c['entraron'])} entraron · "
         f"{len(c['salieron'])} salieron · {len(c['cambiaron'])} cambiaron"]
    for k, s in (("entraron", "+"), ("salieron", "-")):
        L += [f"  {s} [{x['vista']}] {x['ref']} {x['nombre']} ({x['columna'] or x['estado']})" for x in c[k]]
    L += [f"  ~ [{x['vista']}] {x['ref']} {x['nombre']}: {x['de']['columna'] or x['de']['estado']} → {x['a']['columna'] or x['a']['estado']}"
          for x in c["cambiaron"]]
    return _recortar(L, tope)
