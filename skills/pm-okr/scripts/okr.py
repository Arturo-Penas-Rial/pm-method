#!/usr/bin/env python3
"""OKR del proyecto: validación, puntuación y vínculo con beneficios (PRINCE2) y métricas de éxito (PRD).
Project OKRs: validation, scoring and links to benefits and PRD success metrics.

CSV 00-direccion/okr.csv (cabecera):
  id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas
  - tipo: objetivo | kr          id: O-1 / KR-1.1
  - vinculo (obligatorio en cada KR): B-n (beneficio del business case), SM-n (métrica de éxito del PRD), OBJ-n (objetivo de negocio)
  - confianza: 1–10 (opcional, autoevaluación del responsable)
Puntuación de un KR = (actual − línea base) / (meta − línea base), acotada a 0–1 (si la meta es reducir, funciona igual).
Objetivo = promedio de sus KR. Semáforo por defecto: ≥0,7 verde · 0,4–0,69 ámbar · <0,4 rojo (convención configurable con --umbrales).
Uso / Usage:
  python3 okr.py 00-direccion/okr.csv [--umbrales 0.7,0.4] [--markdown salida.md] [--json] [--corte 2026-12-31]
  python3 okr.py --plantilla 00-direccion/okr.csv       # crea el CSV vacío con la cabecera
"""
import argparse, csv, json, sys, datetime, re

COLS = ["id", "tipo", "objetivo_id", "enunciado", "metrica", "linea_base", "meta", "actual", "unidad", "responsable",
        "fecha_meta", "vinculo", "confianza", "notas"]

def num(v):
    v = (v or "").strip().replace(",", ".").rstrip("%")
    try: return float(v) if v else None
    except ValueError: return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--umbrales", default="0.7,0.4"); ap.add_argument("--markdown"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--corte", default=datetime.date.today().isoformat()); ap.add_argument("--plantilla", action="store_true")
    a = ap.parse_args()
    if a.plantilla:
        with open(a.csv, "w", newline="", encoding="utf-8") as f: csv.writer(f).writerow(COLS)
        print(f"Plantilla escrita en {a.csv}"); return
    verde, ambar = [float(x) for x in a.umbrales.split(",")]
    filas = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    objs = {f["id"]: {**f, "krs": []} for f in filas if f.get("tipo") == "objetivo"}
    avisos = []
    for f in filas:
        if f.get("tipo") != "kr": continue
        o = objs.get(f.get("objetivo_id"))
        if not o: avisos.append(f"{f['id']}: objetivo_id inexistente ({f.get('objetivo_id')})"); continue
        base, meta, act = num(f.get("linea_base")), num(f.get("meta")), num(f.get("actual"))
        if None in (base, meta): avisos.append(f"{f['id']}: falta línea base o meta numérica (un KR mide un resultado, no una tarea)"); score = None
        elif meta == base: avisos.append(f"{f['id']}: meta igual a la línea base"); score = None
        else: score = None if act is None else max(0.0, min(1.0, (act - base) / (meta - base)))
        # sin medición todavía: dejar 'actual' vacío (sin-dato), no copiar la línea base (daría rojo)
        if not re.search(r"\b(B|SM|OBJ)-?\d+", f.get("vinculo") or ""): avisos.append(f"{f['id']}: sin vínculo a beneficio (B-n), métrica de éxito (SM-n) u objetivo de negocio (OBJ-n)")
        if not f.get("responsable"): avisos.append(f"{f['id']}: sin responsable")
        if f.get("fecha_meta") and f["fecha_meta"] < a.corte and (score is None or score < 1): avisos.append(f"{f['id']}: fecha meta vencida sin cumplir")
        o["krs"].append({**f, "puntuacion": score})
    for o in objs.values():
        n = len(o["krs"])
        if n == 0: avisos.append(f"{o['id']}: objetivo sin resultados clave")
        if n > 5: avisos.append(f"{o['id']}: {n} resultados clave (recomendado 2–5)")
        ps = [k["puntuacion"] for k in o["krs"] if k["puntuacion"] is not None]
        o["puntuacion"] = sum(ps) / len(ps) if ps else None
    color = lambda p: "sin-dato" if p is None else ("verde" if p >= verde else ("ambar" if p >= ambar else "rojo"))
    if a.json:
        print(json.dumps({"corte": a.corte, "objetivos": [{"id": o["id"], "enunciado": o["enunciado"], "puntuacion": o["puntuacion"], "semaforo": color(o["puntuacion"]),
                          "krs": [{"id": k["id"], "puntuacion": k["puntuacion"], "semaforo": color(k["puntuacion"]), "vinculo": k.get("vinculo")} for k in o["krs"]]}
                         for o in objs.values()], "avisos": avisos}, ensure_ascii=False, indent=2))
    else:
        for o in objs.values():
            p = o["puntuacion"]; print(f"{o['id']} {o['enunciado']} → {'-' if p is None else f'{p:.2f}'} ({color(p)})")
            for k in o["krs"]:
                q = k["puntuacion"]; print(f"   {k['id']} {k['enunciado']} [{k.get('actual') or '-'}/{k.get('meta')} {k.get('unidad','')}] → {'-' if q is None else f'{q:.2f}'} ({color(q)}) · {k.get('vinculo','')} · {k.get('responsable','')}")
        for w in avisos: print("AVISO", w)
    if a.markdown:
        L = ["| Objetivo / KR | Métrica | Base → Meta | Actual | Puntuación | Semáforo | Vínculo | Responsable |", "|---|---|---|---|---|---|---|---|"]
        for o in objs.values():
            p = o["puntuacion"]; L.append(f"| **{o['id']} {o['enunciado']}** | | | | {'-' if p is None else f'{p:.2f}'} | {color(p)} | {o.get('vinculo','')} | {o.get('responsable','')} |")
            for k in o["krs"]:
                q = k["puntuacion"]
                L.append(f"| {k['id']} {k['enunciado']} | {k.get('metrica','')} | {k.get('linea_base','')} → {k.get('meta','')} {k.get('unidad','')} | {k.get('actual','') or '-'} | {'-' if q is None else f'{q:.2f}'} | {color(q)} | {k.get('vinculo','')} | {k.get('responsable','')} |")
        open(a.markdown, "w", encoding="utf-8").write("\n".join(L) + "\n\n" + "\n".join(f"- Aviso: {w}" for w in avisos) + "\n"); print(f"Tabla escrita en {a.markdown}")

if __name__ == "__main__":
    main()
