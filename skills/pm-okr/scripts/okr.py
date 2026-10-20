#!/usr/bin/env python3
"""OKR del proyecto: validación, puntuación, salud, check-ins y vínculo con beneficios (PRINCE2), métricas de éxito (PRD)
y el maestro de interesados. Project OKRs: validation, scoring, health, check-ins and links.

CSV 00-direccion/okr.csv. Columnas base (obligatorias):
  id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas
Columnas opcionales (si faltan, se usan los valores por defecto):
  tipo_kr      de-a (defecto) | mantener-sobre | mantener-bajo | binario | hito
  compromiso   aspiracional (defecto) | comprometido      → umbrales 0,7/0,4 o 1,0/0,7 (convención de la práctica OKR)
  peso         peso del KR en el objetivo (defecto 1)
  padre_id     objetivo padre (O-n de este archivo u OBJ-n del business case): alineación en cascada
  nivel        organizacion | proyecto | equipo · ciclo (p. ej. 2027-T1) · fecha_inicio (para la salud)
  estado       activo | cerrado | cancelado · ref_externa (p. ej. tability:outcome/123, perdoo:result/abc)
  tipo = objetivo | kr | iniciativa (iniciativa: objetivo_id = KR al que contribuye; vinculo = épica, historia o paquete)
Puntuación de un KR de-a = (actual − base) / (meta − base), acotada a 0–1. mantener-sobre/-bajo y binario: 0 o 1.
hito: proporción (ponderada) de iniciativas completadas. Objetivo = promedio ponderado de sus KR.
Salud (en-camino | en-riesgo | desviado) = puntuación contra el avance esperado lineal entre fecha_inicio y fecha_meta.
Check-ins: 00-direccion/okr_checkins.csv (fecha,kr_id,valor,confianza,nota,autor,fuente,publicado_en,ref_externa), solo se
agrega; 'actual' = último check-in con fecha ≤ corte (si no hay, la columna actual).

Uso / Usage:
  okr.py 00-direccion/okr.csv [--umbrales 0.7,0.4] [--markdown salida.md] [--json] [--corte AAAA-MM-DD] [--interesados RUTA]
  okr.py 00-direccion/okr.csv --checkin KR-1.1 --valor 42 [--confianza 7] [--nota "…"] [--autor "…"] [--fecha AAAA-MM-DD]
  okr.py 00-direccion/okr.csv --propuesta-sync tability|perdoo [--json]       # check-ins sin publicar → herramienta MCP
  okr.py 00-direccion/okr.csv --marcar-publicado KR-1.1@2026-11-15 --destino tability --ref <id externo>
  okr.py --plantilla 00-direccion/okr.csv       # crea el CSV vacío con la cabecera completa
"""
import argparse, csv, json, os, re, sys, datetime, unicodedata

COLS = ["id", "tipo", "objetivo_id", "enunciado", "metrica", "linea_base", "meta", "actual", "unidad", "responsable",
        "fecha_meta", "vinculo", "confianza", "notas"]
EXT = ["tipo_kr", "compromiso", "peso", "padre_id", "nivel", "ciclo", "fecha_inicio", "estado", "ref_externa"]
COLS_CHECKIN = ["fecha", "kr_id", "valor", "confianza", "nota", "autor", "fuente", "publicado_en", "ref_externa"]
TIPOS_KR = {"", "de-a", "mantener-sobre", "mantener-bajo", "binario", "hito"}
COMPROMISOS = {"", "aspiracional", "comprometido"}
VERBOS_ACTIVIDAD = re.compile(r"^\s*(realizar|hacer|ayudar|apoyar|analizar|consultar|participar|asistir|revisar|trabajar en|investigar|explorar|"
                              r"definir|preparar|coordinar|organizar|help|assist|analy[sz]e|consult|participate|review|work on|investigate|explore|"
                              r"support|prepare|coordinate|organi[sz]e)\b", re.I)
HECHO = {"1", "si", "sí", "yes", "true", "hecho", "done", "completada", "completado", "100", "100%"}

def num(v):
    v = (v or "").strip().replace(",", ".").rstrip("%")
    try: return float(v) if v else None
    except ValueError: return None

def norm(s):
    s = (s or "").split(":")[-1]
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip()

def leer_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f); return list(rd), list(rd.fieldnames or [])

def ruta_checkins(p_okr): return os.path.join(os.path.dirname(os.path.abspath(p_okr)), "okr_checkins.csv")

def ruta_interesados(p_okr):
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(p_okr)), "..", "03-control", "registros", "stakeholders.csv"))

def confianza_semaforo(c):
    """1–3 rojo, 4–6 ámbar, 7–10 verde. Criterio del paquete para alinear con herramientas que usan rojo/amarillo/verde."""
    n = num(c)
    if n is None: return ""
    return "rojo" if n <= 3 else ("ambar" if n <= 6 else "verde")

def dias(a, b):
    try: return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days
    except (ValueError, TypeError): return None

# ------------------------------------------------------------------ puntuación
def puntuar_kr(f, act, iniciativas, avisos):
    tipo = (f.get("tipo_kr") or "de-a").strip()
    base, meta = num(f.get("linea_base")), num(f.get("meta"))
    if tipo == "de-a":
        if None in (base, meta): avisos.append(f"{f['id']}: falta línea base o meta numérica (un KR mide un resultado, no una tarea)"); return None
        if meta == base: avisos.append(f"{f['id']}: meta igual a la línea base"); return None
        a = num(act)
        return None if a is None else max(0.0, min(1.0, (a - base) / (meta - base)))
    if tipo in ("mantener-sobre", "mantener-bajo"):
        if meta is None: avisos.append(f"{f['id']}: KR {tipo} sin meta numérica (umbral)"); return None
        a = num(act)
        if a is None: return None
        return 1.0 if (a >= meta if tipo == "mantener-sobre" else a <= meta) else 0.0
    if tipo == "binario":
        v = (act or "").strip().lower()
        if not v: return None
        return 1.0 if v in HECHO or (num(v) or 0) >= 1 else 0.0
    if tipo == "hito":
        if iniciativas:
            tot = sum(max(num(i.get("peso")) or 1, 0) for i in iniciativas) or 1
            hechas = sum(max(num(i.get("peso")) or 1, 0) for i in iniciativas
                         if (i.get("estado") or "").lower() in ("completada", "cerrado", "hecho", "done") or (i.get("actual") or "").strip().lower() in HECHO)
            return hechas / tot
        a = num(act)
        if a is None: return None
        return max(0.0, min(1.0, a / 100 if a > 1 else a))
    return None

def salud(f, obj, score, corte, inicio_ck):
    ini = (f.get("fecha_inicio") or obj.get("fecha_inicio") or inicio_ck or "").strip(); fin = (f.get("fecha_meta") or "").strip()
    if score is None: return "sin-dato", None
    total, trans = dias(ini, fin), dias(ini, corte)
    if not ini or not fin or not total or total <= 0 or trans is None: return "", None
    esperado = max(0.0, min(1.0, trans / total))
    if (f.get("tipo_kr") or "") in ("binario", "mantener-sobre", "mantener-bajo"):
        return ("en-camino" if score >= 1 else ("en-riesgo" if corte < fin else "desviado")), round(esperado, 2)
    if score >= esperado - 0.10: return "en-camino", round(esperado, 2)
    if score >= esperado - 0.25: return "en-riesgo", round(esperado, 2)
    return "desviado", round(esperado, 2)

# ------------------------------------------------------------------ check-ins
def leer_checkins(p):
    return leer_csv(p)[0] if os.path.exists(p) else []

def escribir_checkins(p, filas):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS_CHECKIN, extrasaction="ignore"); w.writeheader(); w.writerows(filas)

def cmd_checkin(a, filas):
    kr = next((f for f in filas if f.get("id") == a.checkin), None)
    if not kr or kr.get("tipo") not in ("kr",): sys.exit(f"--checkin {a.checkin}: no es un KR de {a.csv}")
    if a.valor is None: sys.exit("--checkin requiere --valor")
    tipo = kr.get("tipo_kr") or "de-a"
    if tipo != "binario" and num(a.valor) is None: sys.exit(f"--valor '{a.valor}' no es numérico (KR {tipo})")
    if a.confianza is not None and not (a.confianza.isdigit() and 1 <= int(a.confianza) <= 10): sys.exit("--confianza debe ser un entero 1–10")
    fecha = a.fecha or datetime.date.today().isoformat()
    p = ruta_checkins(a.csv); cks = leer_checkins(p)
    if any(c.get("kr_id") == a.checkin and c.get("fecha") == fecha for c in cks):
        sys.exit(f"Ya hay un check-in de {a.checkin} el {fecha}: los check-ins solo se agregan (registrar uno nuevo con otra fecha o corregir en la nota del siguiente)")
    cks.append({"fecha": fecha, "kr_id": a.checkin, "valor": a.valor, "confianza": a.confianza or "", "nota": a.nota or "", "autor": a.autor or "", "fuente": a.fuente or "manual"})
    cks.sort(key=lambda c: (c.get("fecha", ""), c.get("kr_id", "")))
    escribir_checkins(p, cks); print(f"Check-in {a.checkin} {fecha} = {a.valor} → {p}")

# ------------------------------------------------------------------ evaluación completa
def evaluar(p_okr, corte, umbrales, p_int=None):
    filas, cols = leer_csv(p_okr)
    cks = leer_checkins(ruta_checkins(p_okr))
    avisos = []
    ids = {f.get("id") for f in filas}
    for c in cks:
        if c.get("kr_id") not in ids: avisos.append(f"check-in {c.get('fecha')} cita {c.get('kr_id')}, que no existe en okr.csv")
    ult = {}; hist = {}; primero = {}
    for c in sorted(cks, key=lambda c: c.get("fecha", "")):
        if c.get("fecha", "") <= corte:
            ult[c["kr_id"]] = c; hist.setdefault(c["kr_id"], []).append(c); primero.setdefault(c["kr_id"], c.get("fecha", ""))
    objs = {f["id"]: {**f, "krs": []} for f in filas if f.get("tipo") == "objetivo"}
    inis = {}
    for f in filas:
        if f.get("tipo") == "iniciativa":
            inis.setdefault(f.get("objetivo_id"), []).append(f)
            if f.get("objetivo_id") not in ids: avisos.append(f"{f['id']}: iniciativa ligada a {f.get('objetivo_id') or '(vacío)'}, que no existe")
            elif not re.search(r"\b(E-?\d+|\d+-\d+[\w-]*|\d+(\.\d+)+|EP-?\d+|WP-[\w.]+)\b", f.get("vinculo") or ""):
                avisos.append(f"{f['id']}: iniciativa sin vínculo a épica, historia o paquete de la WBS")
    # interesados (maestro): valida responsables si existe y tiene filas
    p_int = p_int or ruta_interesados(p_okr); maestro = []
    if os.path.exists(p_int): maestro = leer_csv(p_int)[0]
    ids_st = {s.get("id") for s in maestro}; nombres_st = {norm(s.get("nombre")) for s in maestro}
    for f in filas:
        if f.get("tipo") not in ("objetivo", "kr", "iniciativa"): avisos.append(f"{f.get('id')}: tipo '{f.get('tipo')}' desconocido (objetivo|kr|iniciativa)")
        if f.get("tipo_kr", "") not in TIPOS_KR: avisos.append(f"{f['id']}: tipo_kr '{f.get('tipo_kr')}' desconocido ({', '.join(sorted(x for x in TIPOS_KR if x))})")
        if f.get("compromiso", "") not in COMPROMISOS: avisos.append(f"{f['id']}: compromiso '{f.get('compromiso')}' desconocido (aspiracional|comprometido)")
        if f.get("peso") and (num(f["peso"]) is None or num(f["peso"]) < 0): avisos.append(f"{f['id']}: peso '{f['peso']}' inválido (número ≥ 0)")
        r = (f.get("responsable") or "").strip()
        if maestro and r and r not in ids_st and norm(r) not in nombres_st:
            avisos.append(f"{f['id']}: responsable '{r}' no figura en el maestro de interesados (stakeholders.csv)")
        pid = (f.get("padre_id") or "").strip()
        if pid and re.match(r"^O-", pid) and pid not in objs: avisos.append(f"{f['id']}: padre_id {pid} no existe en este archivo")
    for f in filas:
        if f.get("tipo") != "kr": continue
        o = objs.get(f.get("objetivo_id"))
        if not o: avisos.append(f"{f['id']}: objetivo_id inexistente ({f.get('objetivo_id')})"); continue
        ck = ult.get(f["id"]); act = ck["valor"] if ck else f.get("actual")
        if (f.get("tipo_kr") == "hito") and inis.get(f["id"]):
            hechas = sum(1 for i in inis[f["id"]] if (i.get("estado") or "").lower() in ("completada", "cerrado", "hecho", "done") or (i.get("actual") or "").strip().lower() in HECHO)
            etiqueta_hito = f"{hechas}/{len(inis[f['id']])} iniciativas"
        else: etiqueta_hito = ""
        score = puntuar_kr(f, act, inis.get(f["id"], []), avisos)
        # sin medición todavía: dejar 'actual' vacío (sin-dato), no copiar la línea base (daría rojo)
        if not re.search(r"\b(B|SM|SM-C|OBJ)-?\d+", f.get("vinculo") or ""): avisos.append(f"{f['id']}: sin vínculo a beneficio (B-n), métrica de éxito (SM-n) u objetivo de negocio (OBJ-n)")
        if not f.get("responsable"): avisos.append(f"{f['id']}: sin responsable")
        if f.get("fecha_meta") and f["fecha_meta"] < corte and (score is None or score < 1) and (f.get("estado") or "activo") == "activo":
            avisos.append(f"{f['id']}: fecha meta vencida sin cumplir")
        if VERBOS_ACTIVIDAD.search(f.get("enunciado") or ""): avisos.append(f"{f['id']}: el enunciado empieza con un verbo de actividad; un KR describe un resultado medible, no una tarea")
        if (f.get("tipo_kr") == "hito") and not inis.get(f["id"]) and num(act) is None: avisos.append(f"{f['id']}: KR de hito sin iniciativas ni avance cargado")
        sal, esperado = salud(f, o, score, corte, primero.get(f["id"]))
        conf = (ck.get("confianza") if ck and ck.get("confianza") else f.get("confianza", ""))
        o["krs"].append({**f, "actual_usado": etiqueta_hito or act or "", "puntuacion": score, "salud": sal, "esperado": esperado, "confianza_usada": conf,
                         "confianza_semaforo": confianza_semaforo(conf), "historial": [{"fecha": c["fecha"], "valor": c["valor"], "confianza": c.get("confianza", "")} for c in hist.get(f["id"], [])]})
    for o in objs.values():
        n = len(o["krs"])
        if n == 0: avisos.append(f"{o['id']}: objetivo sin resultados clave")
        if n > 5: avisos.append(f"{o['id']}: {n} resultados clave (recomendado 2–5)")
        ps = [(k["puntuacion"], num(k.get("peso")) if num(k.get("peso")) is not None else 1.0) for k in o["krs"] if k["puntuacion"] is not None]
        tot = sum(w for _, w in ps)
        o["puntuacion"] = (sum(p * w for p, w in ps) / tot) if ps and tot else None
        cerrado = (o.get("estado") == "cerrado") or (o["krs"] and all(k.get("fecha_meta") and k["fecha_meta"] <= corte for k in o["krs"]))
        if cerrado and o["krs"] and all(k["puntuacion"] == 1.0 for k in o["krs"]) and (o.get("compromiso") or "aspiracional") == "aspiracional":
            avisos.append(f"{o['id']}: todos los KR aspiracionales en 1,0 al cierre; revisar si las metas eran demasiado fáciles")
    verde, ambar = umbrales
    def color(p, comp=""):
        v, am = (1.0, 0.7) if comp == "comprometido" else (verde, ambar)
        return "sin-dato" if p is None else ("verde" if p >= v - 1e-9 else ("ambar" if p >= am else "rojo"))
    # orden en cascada: padres antes que hijos
    orden = []
    def visitar(oid, nivel):
        if oid in [x for x, _ in orden]: return
        orden.append((oid, nivel))
        for h in objs.values():
            if (h.get("padre_id") or "") == oid: visitar(h["id"], nivel + 1)
    for o in objs.values():
        if not o.get("padre_id") or o["padre_id"] not in objs: visitar(o["id"], 0)
    for o in objs.values():
        if o["id"] not in [x for x, _ in orden]: orden.append((o["id"], 0))
    return {"objs": objs, "orden": orden, "avisos": avisos, "color": color, "checkins": cks, "extendido": any(c in cols for c in EXT) or bool(cks)}

# ------------------------------------------------------------------ sincronización (propuesta para MCP)
HERRAMIENTA = {"tability": "tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp)",
               "perdoo": "update_goal_progress (MCP oficial de Perdoo: https://mcp.perdoo.com)"}
COLOR_TABILITY = {"rojo": "red", "ambar": "yellow", "verde": "green"}

def propuesta_sync(p_okr, destino, como_json):
    filas, _ = leer_csv(p_okr); krs = {f["id"]: f for f in filas if f.get("tipo") == "kr"}
    cks = [c for c in leer_checkins(ruta_checkins(p_okr)) if not c.get("publicado_en")]
    out, avisos = [], []
    for c in cks:
        k = krs.get(c.get("kr_id"))
        if not k: avisos.append(f"check-in de {c.get('kr_id')}: KR inexistente"); continue
        ref = (k.get("ref_externa") or "")
        if not ref.startswith(destino + ":"):
            w = f"{k['id']}: sin ref_externa '{destino}:…' (vincular el KR con su par en {destino} antes de publicar)"
            if w not in avisos: avisos.append(w)
            continue
        item = {"kr_id": k["id"], "fecha": c["fecha"], "valor": c["valor"], "nota": c.get("nota", ""), "ref_externa": ref.split(":", 1)[1], "herramienta": HERRAMIENTA[destino],
                "marcar_despues": f"okr.py {p_okr} --marcar-publicado {k['id']}@{c['fecha']} --destino {destino} --ref <id devuelto>"}
        sem = confianza_semaforo(c.get("confianza"))
        if destino == "tability" and sem: item["confidence"] = COLOR_TABILITY[sem]
        if destino == "perdoo" and sem: item["status_sugerido"] = {"rojo": "off track", "ambar": "needs attention", "verde": "on track"}[sem] + " [verificar nombres de estado en Perdoo]"
        out.append(item)
    res = {"destino": destino, "pendientes": out, "avisos": avisos,
           "regla": "Publicar solo tras mostrar esta vista previa y obtener confirmación explícita (pm-integraciones); okr.csv sigue siendo la fuente."}
    if como_json: print(json.dumps(res, ensure_ascii=False, indent=2)); return
    for i in out: print(f"{i['kr_id']} {i['fecha']} = {i['valor']} → {destino}:{i['ref_externa']} · {i['herramienta']}" + (f" · confidence {i['confidence']}" if i.get("confidence") else ""))
    for w in avisos: print("AVISO", w)
    if not out and not avisos: print("No hay check-ins pendientes de publicar.")

def marcar_publicado(p_okr, clave, destino, ref):
    if "@" not in clave: sys.exit("--marcar-publicado espera KR-x@AAAA-MM-DD")
    kr, fecha = clave.split("@", 1); p = ruta_checkins(p_okr); cks = leer_checkins(p)
    for c in cks:
        if c.get("kr_id") == kr and c.get("fecha") == fecha:
            c["publicado_en"] = f"{destino}:{datetime.date.today().isoformat()}"; c["ref_externa"] = ref or c.get("ref_externa", "")
            escribir_checkins(p, cks); print(f"{kr}@{fecha} marcado como publicado en {destino}"); return
    sys.exit(f"No hay check-in {kr} del {fecha}")

# ------------------------------------------------------------------ salida
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--umbrales", default="0.7,0.4"); ap.add_argument("--markdown"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--corte", default=datetime.date.today().isoformat()); ap.add_argument("--plantilla", action="store_true"); ap.add_argument("--interesados")
    ap.add_argument("--checkin"); ap.add_argument("--valor"); ap.add_argument("--confianza"); ap.add_argument("--nota"); ap.add_argument("--autor"); ap.add_argument("--fecha"); ap.add_argument("--fuente")
    ap.add_argument("--propuesta-sync", choices=["tability", "perdoo"]); ap.add_argument("--marcar-publicado"); ap.add_argument("--destino", choices=["tability", "perdoo"]); ap.add_argument("--ref")
    a = ap.parse_args()
    if a.plantilla:
        with open(a.csv, "w", newline="", encoding="utf-8") as f: csv.writer(f).writerow(COLS + EXT)
        print(f"Plantilla escrita en {a.csv}"); return
    if not os.path.exists(a.csv): sys.exit(f"No existe {a.csv} (crear con --plantilla)")
    if a.checkin: cmd_checkin(a, leer_csv(a.csv)[0]); return
    if a.propuesta_sync: propuesta_sync(a.csv, a.propuesta_sync, a.json); return
    if a.marcar_publicado:
        if not a.destino: sys.exit("--marcar-publicado requiere --destino")
        marcar_publicado(a.csv, a.marcar_publicado, a.destino, a.ref); return
    umb = tuple(float(x) for x in a.umbrales.split(","))
    R = evaluar(a.csv, a.corte, umb, a.interesados); objs, avisos, color, ext = R["objs"], R["avisos"], R["color"], R["extendido"]
    fmt = lambda p: "-" if p is None else f"{p:.2f}"
    if a.json:
        print(json.dumps({"corte": a.corte, "objetivos": [{"id": o["id"], "enunciado": o["enunciado"], "puntuacion": o["puntuacion"], "semaforo": color(o["puntuacion"], o.get("compromiso", "")),
                          "padre_id": o.get("padre_id", ""), "nivel_cascada": niv, "compromiso": o.get("compromiso", "") or "aspiracional",
                          "krs": [{"id": k["id"], "puntuacion": k["puntuacion"], "semaforo": color(k["puntuacion"], k.get("compromiso") or o.get("compromiso", "")), "vinculo": k.get("vinculo"),
                                   "tipo_kr": k.get("tipo_kr") or "de-a", "actual": k["actual_usado"], "salud": k["salud"], "esperado": k["esperado"],
                                   "confianza": k["confianza_usada"], "confianza_semaforo": k["confianza_semaforo"], "responsable": k.get("responsable", ""), "historial": k["historial"]} for k in o["krs"]]}
                         for oid, niv in R["orden"] for o in [objs[oid]]], "avisos": avisos}, ensure_ascii=False, indent=2))
    else:
        for oid, niv in R["orden"]:
            o = objs[oid]; p = o["puntuacion"]; sang = "   " * niv + ("↳ " if niv else "")
            print(f"{sang}{o['id']} {o['enunciado']} → {fmt(p)} ({color(p, o.get('compromiso', ''))})" + (f" · {o.get('compromiso') or 'aspiracional'}" if ext else ""))
            for k in o["krs"]:
                q = k["puntuacion"]; extra = ""
                if ext:
                    extra = (f" · {k.get('tipo_kr') or 'de-a'}" + (f" · salud {k['salud']}" + (f" (esperado {k['esperado']:.2f})" if k["esperado"] is not None else "") if k["salud"] else "")
                             + (f" · confianza {k['confianza_usada']} ({k['confianza_semaforo']})" if k["confianza_semaforo"] else ""))
                print(f"{sang}   {k['id']} {k['enunciado']} [{k['actual_usado'] if (k.get('tipo_kr') == 'hito' and k['actual_usado']) else (k['actual_usado'] or '-') + '/' + (k.get('meta') or '') + ' ' + (k.get('unidad') or '')}] → {fmt(q)} ({color(q, k.get('compromiso') or o.get('compromiso', ''))}) · {k.get('vinculo','')} · {k.get('responsable','')}{extra}")
        for w in avisos: print("AVISO", w)
    if a.markdown:
        if ext:
            L = ["| Objetivo / KR | Tipo | Métrica | Base → Meta | Actual | Puntuación | Semáforo | Salud | Confianza | Vínculo | Responsable |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        else:
            L = ["| Objetivo / KR | Métrica | Base → Meta | Actual | Puntuación | Semáforo | Vínculo | Responsable |", "|---|---|---|---|---|---|---|---|"]
        for oid, niv in R["orden"]:
            o = objs[oid]; p = o["puntuacion"]; pre = "↳ " * niv
            if ext: L.append(f"| **{pre}{o['id']} {o['enunciado']}** | {o.get('compromiso') or 'aspiracional'} | | | | {fmt(p)} | {color(p, o.get('compromiso', ''))} | | | {o.get('vinculo','')} | {o.get('responsable','')} |")
            else: L.append(f"| **{o['id']} {o['enunciado']}** | | | | {fmt(p)} | {color(p)} | {o.get('vinculo','')} | {o.get('responsable','')} |")
            for k in o["krs"]:
                q = k["puntuacion"]; c = color(q, k.get("compromiso") or o.get("compromiso", ""))
                if ext:
                    L.append(f"| {k['id']} {k['enunciado']} | {k.get('tipo_kr') or 'de-a'} | {k.get('metrica','')} | {k.get('linea_base','')} → {k.get('meta','')} {k.get('unidad','')} | {k['actual_usado'] or '-'} | {fmt(q)} | {c} | {k['salud'] or '-'} | {k['confianza_usada'] or '-'} {('(' + k['confianza_semaforo'] + ')') if k['confianza_semaforo'] else ''} | {k.get('vinculo','')} | {k.get('responsable','')} |")
                else:
                    L.append(f"| {k['id']} {k['enunciado']} | {k.get('metrica','')} | {k.get('linea_base','')} → {k.get('meta','')} {k.get('unidad','')} | {k.get('actual','') or '-'} | {fmt(q)} | {c} | {k.get('vinculo','')} | {k.get('responsable','')} |")
        texto = "\n".join(L) + "\n\n" + "\n".join(f"- Aviso: {w}" for w in avisos) + "\n"
        con_hist = [(k, o) for o in objs.values() for k in o["krs"] if len(k["historial"]) >= 1]
        if con_hist:
            texto += "\n## Historial de check-ins\n\n| KR | Fecha | Valor | Confianza |\n|---|---|---|---|\n" + "".join(
                f"| {k['id']} | {c['fecha']} | {c['valor']} | {c['confianza'] or '-'} |\n" for k, _ in con_hist for c in k["historial"])
        open(a.markdown, "w", encoding="utf-8").write(texto); print(f"Tabla escrita en {a.markdown}")

if __name__ == "__main__":
    main()
