#!/usr/bin/env python3
"""Vigencia y contradicciones de decisiones (decisiones.csv): quién reemplaza a quién, cuáles siguen vigentes, qué
decisiones del mismo asunto parecen contradecirse sin marca y cuáles tienen la revisión vencida. Funciones puras sobre
las filas; las usan registro.py (validación de `reemplaza` y `conviven`), sanidad.py (DEC-05, DEC-06), esquema.py
(reemplazo automático al aprobar una versión nueva) y pm-direccion-decisiones/decision.py (`vigentes`, `expediente`).
Decision validity and contradictions: pure functions over decisiones.csv rows (SPEC.md §1.10.8 y §1.10.15).

Columnas (al final de decisiones.csv, migración transparente): `reemplaza` (D-### que esta decisión deja sin efecto,
separados por «;») y `conviven` (D-### que la persona decidió mantener vigentes a la vez aunque parezcan contradecirse).
"Reemplazada por" se deriva, no se escribe. Revisión vencida (DEC-06): `revisar_en` anterior al corte, sin decisión
posterior del mismo asunto y con algún id citado de un registro con estado todavía abierto (o sin ids conocidos). Reemplazar exige nivel igual o superior (NIVELES_DECISION): una decisión
posterior de nivel inferior no anula la de la junta; la fecha más nueva no decide sola.

Asunto (para comparar solo lo comparable): dos decisiones tratan el mismo asunto si comparten un id de registro citado
en `decision` o `artefactos_afectados` (R-, I-, C-, S-, L-, Q-, A-, PU-; no D- ni los del maestro de interesados); si
ninguna cita ids, si comparten un artefacto (ruta con carpeta en `artefactos_afectados`, sin los CSV de registros); y si
ninguna cita ids ni artefactos, si su texto es parecido (Jaccard ≥ 0,6 de los lemas de texto.py, sin cifras ni fechas).
Dos decisiones que citan ids distintos nunca son del mismo asunto (D-005 "residual de R-005" y D-006 "… de R-002").
Contradicción probable (DEC-05): mismo asunto, texto parecido (Jaccard ≥ 0,6 y al menos 2 lemas) y valor distinto:
versión, cifra normalizada (39.800 = 39800), fecha, negación (no, nunca, jamás, ni, tampoco, not, never; "sin" no
cuenta) o una palabra cambiada (predictivo → híbrido); sin `reemplaza` ni `conviven` entre ellas y las dos vigentes.
"""
import datetime, re
import esquema as E
import texto as T

ID_D = re.compile(r"^D-\d{3,}$")
ID_ASUNTO = re.compile(r"\b(?:R|I|C|S|L|Q|A|PU)-\d{3,}\b")
CARPETAS_RAIZ = ("00-direccion/", "01-inicio/", "02-planificacion/", "03-control/", "04-cierre/", "_bmad-output/", "docs/")
UMBRAL_PARECIDO = 0.6
APROBACION = re.compile(r"^(aprobado|approved|línea base|linea base|baseline) (\S+) v\S+")
# decisiones de estado.py con valores clave=valor (presupuestos) o un único valor (enfoque de entrega; veredicto del gate de
# preparación de BMAD de puertas.py, que estado.json guarda uno solo): una posterior que fija todas las claves de la
# anterior la reemplaza; una que fija solo algunas la actualiza en parte (no es contradicción)
PREFIJOS_ESTADO = ("presupuestos de la junta:", "board budgets:", "enfoque de entrega:", "delivery approach:", "gate de preparación de bmad:")
PREFIJOS_UNICO = ("enfoque de entrega:", "delivery approach:", "gate de preparación de bmad:")      # un solo valor: sin claves
CLAVE_VALOR = re.compile(r"\b([a-z_]+)=")


def _estado(decision):
    d = (decision or "").strip()
    pref = next((x for x in PREFIJOS_ESTADO if d.lower().startswith(x)), "")
    return pref, set(CLAVE_VALOR.findall(d[len(pref):])) if pref and pref not in PREFIJOS_UNICO else set()


def lista_ids(v):
    return [x for x in re.split(r"[;,\s]+", v or "") if x]


def rango(nivel):
    try: return E.NIVELES_DECISION.index(nivel)
    except ValueError: return -1


def reemplazada_por(filas):
    """{id reemplazada: id de la decisión que la reemplaza} (la última por fecha si hubiera más de una)."""
    out = {}
    for f in sorted(filas, key=lambda f: (f.get("fecha") or "", f.get("id") or "")):
        for x in lista_ids(f.get("reemplaza")): out[x] = f.get("id")
    return out


def conviven(filas):
    """Pares {frozenset(a, b)} declarados en `conviven` (en cualquiera de las dos filas)."""
    return {frozenset((f.get("id"), x)) for f in filas for x in lista_ids(f.get("conviven")) if x != f.get("id")}


def cadena(i, filas, rp=None):
    """Ids del más antiguo al más nuevo que pasan por `i` siguiendo `reemplaza` (una rama hacia atrás)."""
    rp = reemplazada_por(filas) if rp is None else rp
    por_id = {f.get("id"): f for f in filas}
    atras, x, vistos = [], i, {i}
    while True:
        prev = [y for y in lista_ids((por_id.get(x) or {}).get("reemplaza")) if y not in vistos]
        if not prev: break
        x = prev[0]; vistos.add(x); atras.insert(0, x)
    adelante, x = [], i
    while x in rp and rp[x] not in vistos:
        x = rp[x]; vistos.add(x); adelante.append(x)
    return atras + [i] + adelante


def vigentes(filas):
    """Ids de las decisiones vigentes (ninguna otra las reemplaza), en el orden del archivo."""
    rp = reemplazada_por(filas)
    return [f.get("id") for f in filas if f.get("id") not in rp]


def artefactos(f):
    out = set()
    for parte in (f.get("artefactos_afectados") or "").split(";"):
        p = parte.strip().split(" ")[0].split("§")[0].strip().rstrip("/").replace("\\", "/")
        for raiz in CARPETAS_RAIZ:
            k = p.find(raiz)
            if k > 0: p = p[k:]; break
        if "/" not in p or re.search(r"(?:^|/)registros/[a-z]+\.csv$", p): continue
        out.add(p)
    return out


def perfil(f):
    a = T.analizar(f.get("decision") or "", expandir=False)
    return {"id": f.get("id"), "fecha": f.get("fecha") or "", "nivel": f.get("nivel") or "", "decision": f.get("decision") or "",
            "ids": set(ID_ASUNTO.findall((f.get("decision") or "") + " " + (f.get("artefactos_afectados") or ""))),
            "arts": artefactos(f), "lemas": set(a["palabras"]), "negado": bool(a["negaciones"]),
            "valores": {"cifra": set(a["numeros"]), "fecha": set(a["fechas"]), "versión": set(a["versiones"])}}


def parecido(p, q):
    u = p["lemas"] | q["lemas"]
    return len(p["lemas"] & q["lemas"]) / len(u) if u else 0.0


def mismo_asunto(p, q):
    if p["ids"] or q["ids"]: return bool(p["ids"] & q["ids"])
    if p["arts"] or q["arts"]: return bool(p["arts"] & q["arts"])
    return parecido(p, q) >= UMBRAL_PARECIDO


def diferencias(p, q, idioma="es"):
    """Diferencias de valor entre dos decisiones de texto parecido ([] = dicen lo mismo)."""
    t = lambda es, en: E.t(idioma, es, en)
    out = []
    for k, (a, b) in ((k, (p["valores"][k], q["valores"][k])) for k in ("versión", "cifra", "fecha")):
        if a and b and a != b:
            nombre = {"versión": t("versión", "version"), "cifra": t("cifra", "figure"), "fecha": t("fecha", "date")}[k]
            out.append(f"{nombre} {', '.join(sorted(a - b) or sorted(a))} → {', '.join(sorted(b - a) or sorted(b))}")
    if p["negado"] != q["negado"]: out.append(t("una niega lo que la otra afirma", "one negates what the other states"))
    if not out and p["lemas"] != q["lemas"]:
        out.append(t("texto distinto: ", "different wording: ") + f"{', '.join(sorted(p['lemas'] - q['lemas'])) or '—'} → {', '.join(sorted(q['lemas'] - p['lemas'])) or '—'}")
    return out


def contradicciones(filas, idioma="es"):
    """[(anterior, posterior, [diferencias])] de pares vigentes del mismo asunto que parecen contradecirse sin marca."""
    rp = reemplazada_por(filas); cv = conviven(filas)
    vig = [perfil(f) for f in sorted(filas, key=lambda f: (f.get("fecha") or "", f.get("id") or "")) if f.get("id") and f.get("id") not in rp]
    out = []
    for n, p in enumerate(vig):
        for q in vig[n + 1:]:
            if frozenset((p["id"], q["id"])) in cv or not mismo_asunto(p, q): continue
            if len(p["lemas"]) < 2 or len(q["lemas"]) < 2 or parecido(p, q) < UMBRAL_PARECIDO: continue
            (pp, kp), (pq, kq) = _estado(p["decision"]), _estado(q["decision"])
            if pp and pp == pq and not kp <= kq: continue      # actualización parcial de claves (presupuestos): no se contradicen
            d = diferencias(p, q, idioma)
            if d: out.append((p, q, d))
    return out


def abiertos(registros):
    """{id: True si sigue abierto} de las filas de los registros con estados abiertos (esquema: `abiertos`)."""
    out = {}
    for reg, fs in (registros or {}).items():
        ab = (E.REGISTROS.get(reg) or {}).get("abiertos")
        if ab is None or (E.REGISTROS.get(reg) or {}).get("catalogo"): continue
        for f in fs:
            if f.get("id"): out[f["id"]] = (f.get("estado") or "") in ab
    return out


def revisiones_vencidas(filas, corte, registros=None):
    """Decisiones vigentes con `revisar_en` (AAAA-MM-DD) anterior al corte, sin una decisión posterior del mismo asunto
    (a partir de su fecha) y, si cita ids de registros con estado, con alguno todavía abierto (`registros`: {registro:
    filas}; un asunto ya cerrado o validado no pide revisión)."""
    rp = reemplazada_por(filas); out = []; ab = abiertos(registros)
    perfiles = {f.get("id"): perfil(f) for f in filas if f.get("id")}
    for f in filas:
        r = (f.get("revisar_en") or "").strip()
        if f.get("id") in rp or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r) or r >= corte: continue
        p = perfiles[f["id"]]
        conocidos = [i for i in p["ids"] if i in ab]
        if conocidos and len(conocidos) == len(p["ids"]) and not any(ab[i] for i in conocidos): continue
        if any(g.get("id") != f["id"] and (g.get("fecha") or "") > (f.get("fecha") or "") and mismo_asunto(p, perfiles[g["id"]])
               for g in filas if g.get("id") in perfiles):
            continue
        out.append(f)
    return out


def controles(filas, corte=None, idioma="es", registros=None):
    """Avisos de sanidad DEC-05 (contradicción probable sin reemplaza ni conviven) y DEC-06 (revisar_en vencido;
    `registros` {registro: filas} para saber si el asunto citado sigue abierto)."""
    corte = corte or datetime.date.today().isoformat(); t = lambda es, en: E.t(idioma, es, en); out = []
    for p, q, d in contradicciones(filas, idioma):
        asunto = ", ".join(sorted(p["ids"] & q["ids"]) or sorted(p["arts"] & q["arts"])) or t("texto parecido", "similar wording")
        out.append(("AVISO", "DEC-05",
                    t(f"{p['id']} ({p['fecha']}, {p['nivel'] or '—'}) y {q['id']} ({q['fecha']}, {q['nivel'] or '—'}) tratan el mismo asunto ({asunto}) con valor distinto ({'; '.join(d)}) y ninguna marca reemplaza ni conviven.",
                      f"{p['id']} ({p['fecha']}) and {q['id']} ({q['fecha']}) deal with the same subject ({asunto}) with different values ({'; '.join(d)}) and neither marks reemplaza or conviven."),
                    t(f"Si {q['id']} deja sin efecto a {p['id']}: registro.py actualizar decisiones {q['id']} --campo reemplaza={p['id']} (exige nivel igual o superior; si no, la decide pm-director). "
                      f"Si deben valer las dos: --campo conviven={p['id']}.",
                      f"If {q['id']} supersedes {p['id']}: registro.py actualizar decisiones {q['id']} --campo reemplaza={p['id']} (same or higher level). If both stand: --campo conviven={p['id']}.")))
    for f in revisiones_vencidas(filas, corte, registros):
        out.append(("AVISO", "DEC-06",
                    t(f"Decisión {f['id']} con la revisión vencida (revisar_en {f['revisar_en']}; {f.get('decidido_por') or '—'}, nivel {f.get('nivel') or '—'}): {f.get('decision', '')[:90]}",
                      f"Decision {f['id']} is past its review date (revisar_en {f['revisar_en']}; {f.get('decidido_por') or '—'}): {f.get('decision', '')[:90]}"),
                    t("Reevaluarla con quien decidió: confirmarla (registro.py actualizar decisiones D-### --campo revisar_en=<nueva fecha>) o registrar la decisión nueva con reemplaza=D-### (decision.py vigentes muestra lo vigente).",
                      "Review it with the decision maker: confirm it (new revisar_en) or record the new decision with reemplaza=D-###.")))
    return out


def motivos_reemplazo(e, fila, filas, idioma="es"):
    """Errores de `reemplaza` y `conviven` de `fila` frente a las demás filas: (formato, autoridad). formato: ids
    inexistentes, propios, ya reemplazados por otra, ciclos o una decisión anterior que reemplaza a una posterior (se
    omiten con --forzar); autoridad: nivel menor que el de la reemplazada o quien decide sin esa autoridad
    (esquema.nivel_autoridad; no se omite con --forzar: lo decide pm-director)."""
    t = lambda es, en: E.t(idioma, es, en)
    yo = fila.get("id"); por_id = {f.get("id"): f for f in filas if f.get("id") != yo}
    formato, autoridad = [], []
    rp = reemplazada_por([f for f in filas if f.get("id") != yo])
    for col in ("reemplaza", "conviven"):
        for x in lista_ids(fila.get(col)):
            if not ID_D.match(x): formato.append(t(f"{col}: '{x}' no es un id D-###", f"{col}: '{x}' is not a D-### id")); continue
            if x == yo: formato.append(t(f"{col}: {x} es la misma decisión", f"{col}: {x} is this same decision")); continue
            if x not in por_id: formato.append(t(f"{col}: {x} no existe en decisiones.csv", f"{col}: {x} does not exist in decisiones.csv")); continue
            if col != "reemplaza": continue
            vieja = por_id[x]
            if x in rp: formato.append(t(f"reemplaza: {x} ya está reemplazada por {rp[x]} (reemplazar a {rp[x]}, que es la vigente)", f"reemplaza: {x} is already superseded by {rp[x]}"))
            atras = cadena(x, filas)
            if yo and yo in atras[:atras.index(x)]:
                formato.append(t(f"reemplaza: {x} ya reemplaza (directa o indirectamente) a {yo}: ciclo", f"reemplaza: {x} already supersedes {yo}: cycle"))
            if (fila.get("fecha") or "") and (vieja.get("fecha") or "") > (fila.get("fecha") or ""):
                formato.append(t(f"reemplaza: {x} ({vieja.get('fecha')}) es posterior a esta decisión ({fila.get('fecha')})", f"reemplaza: {x} ({vieja.get('fecha')}) is later than this decision"))
            nv, nn = vieja.get("nivel") or "", fila.get("nivel") or ""
            if rango(nn) < rango(nv):
                autoridad.append(t(f"reemplaza: {x} es de nivel {nv or '—'} y esta decisión es de nivel {nn or '—'}: reemplazar exige nivel igual o superior",
                                   f"reemplaza: {x} has level {nv or '—'} and this decision {nn or '—'}: superseding requires the same or a higher level"))
            elif fila.get("decidido_por"):
                na, fuente = E.nivel_autoridad(e, fila.get("decidido_por"))
                if na and rango(na) < rango(nv):
                    autoridad.append(t(f"reemplaza: {x} es de nivel {nv} y '{fila['decidido_por']}' tiene autoridad {na} ({fuente})",
                                       f"reemplaza: {x} has level {nv} and '{fila['decidido_por']}' holds {na} authority ({fuente})"))
    return formato, autoridad


def reemplazo_automatico(filas, decision, nivel, artefactos_txt, fecha=""):
    """Decisión anterior que una decisión escrita por los scripts deja sin efecto, o "": la aprobación vigente anterior
    del mismo artefacto y la misma ruta ("aprobado <clave> v<x>", "línea base <clave> v<x>"), los presupuestos de la junta
    anteriores cuyas claves vuelven a fijarse todas, o el enfoque de entrega anterior. Solo si la anterior no tiene nivel
    mayor ni fecha posterior."""
    m = APROBACION.match(decision or ""); pref, claves = _estado(decision)
    if not ((m and artefactos_txt) or pref): return ""
    rp = reemplazada_por(filas)
    for f in reversed(filas):
        if f.get("id") in rp or f.get("decision") == decision or rango(f.get("nivel") or "") > rango(nivel) or (f.get("fecha") or "") > (fecha or "9999"): continue
        m2 = APROBACION.match(f.get("decision") or ""); pref2, claves2 = _estado(f.get("decision"))
        if m and m2 and m2.group(1) == m.group(1) and m2.group(2) == m.group(2) and f.get("artefactos_afectados") == artefactos_txt: return f.get("id")
        if pref and pref2 == pref and claves2 <= claves: return f.get("id")
    return ""


if __name__ == "__main__":
    import argparse, json, os, sys
    ap = argparse.ArgumentParser(description="Vigencia de decisiones: DEC-05 y DEC-06 de decisiones.csv (solo lectura). "
                                 "Uso: vigencia.py --proyecto <dir> [--corte AAAA-MM-DD] [--json]; para el detalle, decision.py vigentes.")
    ap.add_argument("--proyecto", required=True); ap.add_argument("--corte"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    p = E.ruta_registro(a.proyecto, "decisiones")
    if not os.path.exists(p): sys.exit(f"{p}: no existe / not found")
    filas = E.leer_csv(p)[1]; idioma = E.idioma_de(a.proyecto)
    regs = {r: E.leer_csv(E.ruta_registro(a.proyecto, r))[1] for r in E.REGISTROS if os.path.exists(E.ruta_registro(a.proyecto, r))}
    out = controles(filas, a.corte, idioma, regs)
    if a.json: print(json.dumps({"vigentes": vigentes(filas), "reemplazadas": reemplazada_por(filas), "hallazgos": [{"severidad": s, "codigo": c, "mensaje": m, "arreglo": r} for s, c, m, r in out]}, ensure_ascii=False, indent=2))
    else:
        print(E.t(idioma, f"{len(vigentes(filas))} decisiones vigentes de {len(filas)}", f"{len(vigentes(filas))} decisions in force of {len(filas)}"))
        for s, c, m, r in out: print(f"  {s} {c} {m}\n        → {r}")
