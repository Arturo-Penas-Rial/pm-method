#!/usr/bin/env python3
"""Valor ganado (EVM) con semáforo contra tolerancias. Earned value with tolerance-based RAG status.

Uso / Usage:
  python3 evm.py --pv 120000 --ev 100000 --ac 110000 --bac 500000 [--tol-costo 10] [--tol-plazo 10] [--json]
  python3 evm.py --csv progreso.csv --bac 500000 [--tol-costo 10]
        columnas aceptadas (acumulados): periodo, pv|pv_acumulado, ev|ev_acumulado, ac|ac_acumulado
        (la línea base de pm-costos-presupuesto, linea-base-costo.csv, sirve si tiene ev/ac acumulados)
  python3 evm.py ... --eac tendencia|atipico|compuesto    # EAC que usan ETC, VAC, TCPI y el semáforo (defecto: tendencia)
  python3 evm.py ... --modo agil [--pct-no-must 30]   # costo y fecha fijos: el desvío se lee como % de alcance que no entra;
        excepción solo si supera el % de alcance Should/Could (los Must peligran). Semáforos de costo/plazo = n/a-agil.
  python3 evm.py ... --proyecto ./p   # idioma y tolerancias de etapa (% en estado.json) si no se pasan --tol-*

Definiciones del paquete:
  BAC = línea base de medición del desempeño (presupuesto de los paquetes + reserva de contingencia asignada),
        SIN la reserva de gestión. La reserva de gestión se informa aparte y solo la libera la junta.
  SV=EV-PV, CV=EV-AC, SPI=EV/PV, CPI=EV/AC,
  EAC tendencia=BAC/CPI, atípico=AC+(BAC-EV), compuesto=AC+(BAC-EV)/(CPI*SPI), ETC=EAC-AC, VAC=BAC-EAC,
  TCPI_bac=(BAC-EV)/(BAC-AC) (eficiencia necesaria para terminar en BAC),
  TCPI_eac=(BAC-EV)/(EAC-AC) (eficiencia necesaria para terminar en el EAC elegido; con EAC tendencia es igual al CPI).
Semáforo (si se dan tolerancias en %): verde = desvío previsto ≤ 50 % de la tolerancia; ámbar = 50–100 %;
  rojo = previsto fuera de tolerancia → informe de excepción. Sin tolerancias: SPI/CPI ≥0,95 verde, ≥0,85 ámbar
  (umbrales de referencia del paquete, configurables en el plan de gestión de cronograma y costos).
"""
import argparse, csv, json, os, re, sys

def col(row, *nombres):
    for n in nombres:
        if n in row and str(row[n]).strip() != "": return float(row[n])
    raise KeyError(nombres[0])

def calcular(pv, ev, ac, bac, metodo="tendencia", tol_costo=None, tol_plazo=None):
    r = {"PV": pv, "EV": ev, "AC": ac, "BAC": bac}
    r["SV"] = ev - pv; r["CV"] = ev - ac
    r["SPI"] = ev / pv if pv else None; r["CPI"] = ev / ac if ac else None
    r["pct_completado"] = ev / bac if bac else None
    r["pct_gastado"] = ac / bac if bac else None
    r["EAC_tendencia"] = bac / r["CPI"] if r["CPI"] else None
    r["EAC_atipico"] = ac + (bac - ev)
    r["EAC_compuesto"] = ac + (bac - ev) / (r["CPI"] * r["SPI"]) if r["CPI"] and r["SPI"] else None
    eac = r.get(f"EAC_{metodo}") or r["EAC_atipico"]
    r["EAC_usado"] = metodo; r["EAC"] = eac
    r["ETC"] = eac - ac; r["VAC"] = bac - eac
    r["VAC_pct"] = (bac - eac) / bac * 100 if bac else None          # mismo signo que VAC (negativo = sobrecosto)
    r["sobrecosto_pct"] = (eac - bac) / bac * 100 if bac else None   # desvío previsto contra BAC (positivo = sobrecosto)
    r["TCPI_bac"] = (bac - ev) / (bac - ac) if bac != ac else None
    r["TCPI_eac"] = (bac - ev) / (eac - ac) if eac != ac else None
    r["SV_pct_del_PV"] = (pv - ev) / pv * 100 if pv else None

    def por_indice(idx):
        if idx is None: return "sin-dato"
        return "verde" if idx >= 0.95 else ("ambar" if idx >= 0.85 else "rojo")
    def por_tolerancia(desvio_pct, tol):
        if desvio_pct is None: return "sin-dato"
        if desvio_pct <= 0.5 * tol: return "verde"
        return "ambar" if desvio_pct <= tol else "rojo"
    r["semaforo_costo"] = por_tolerancia(max(r["sobrecosto_pct"] or 0, 0), tol_costo) if tol_costo is not None else por_indice(r["CPI"])
    r["semaforo_cronograma"] = por_tolerancia(max(r["SV_pct_del_PV"] or 0, 0), tol_plazo) if tol_plazo is not None else por_indice(r["SPI"])
    r["base_semaforo"] = f"costo:{'tolerancia' if tol_costo is not None else 'indice-0.95-0.85'};cronograma:{'tolerancia' if tol_plazo is not None else 'indice-0.95-0.85'}"
    r["excepcion_prevista"] = "rojo" in (r["semaforo_costo"], r["semaforo_cronograma"])
    return r

def lectura_agil(r, pct_no_must):
    """Costo y fecha fijos: el desvío se expresa como alcance que no entra, no como sobrecosto."""
    eac = r["EAC"]; bac = r["BAC"]
    r["alcance_no_entregable_pct"] = max(0.0, (1 - bac / eac) * 100) if eac else None
    r["semaforo_costo"] = "n/a-agil"; r["semaforo_cronograma"] = "n/a-agil"
    if pct_no_must is None:
        r["semaforo_alcance"] = "sin-dato (indicar --pct-no-must)"; r["excepcion_prevista"] = False
    else:
        x = r["alcance_no_entregable_pct"] or 0
        r["semaforo_alcance"] = "verde" if x <= 0.5 * pct_no_must else ("ambar" if x <= pct_no_must else "rojo")
        r["excepcion_prevista"] = x > pct_no_must    # los Must no entran
    r["base_semaforo"] = "alcance-agil"
    return r

NOTA_AGIL = {
    "es": "Modo ágil (costo y fecha fijos): un EAC > BAC significa que, al ritmo actual, no se entregará todo el alcance con el presupuesto; leerlo como alcance pronosticado (ítems Must/Should que no entran) y comparar contra la tolerancia de ALCANCE, no como sobrecosto. Hay excepción si los ítems Must no entran.",
    "en": "Agile mode (fixed cost and date): EAC > BAC means not all scope will be delivered within budget at the current pace; read it as forecast scope (Must/Should items that will not fit) against the SCOPE tolerance, not as overspend. It is an exception only if Must items do not fit.",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pv", type=float); ap.add_argument("--ev", type=float); ap.add_argument("--ac", type=float)
    ap.add_argument("--bac", type=float, required=True); ap.add_argument("--csv"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--eac", choices=["tendencia", "atipico", "compuesto"], default="tendencia")
    ap.add_argument("--tol-costo", type=float, dest="tol_costo", help="tolerancia de costo en %% (p. ej. 10)")
    ap.add_argument("--tol-plazo", type=float, dest="tol_plazo", help="tolerancia de plazo en %% del PV")
    ap.add_argument("--modo", choices=["predictivo", "agil"], default="predictivo"); ap.add_argument("--idioma", choices=["es", "en"])
    ap.add_argument("--pct-no-must", type=float, dest="pct_no_must", help="modo ágil: %% del alcance (puntos) que es Should/Could; si no entra más que eso, los Must peligran → excepción")
    ap.add_argument("--proyecto", help="carpeta del proyecto: toma idioma y, si faltan, tolerancias de etapa en %% de estado.json")
    a = ap.parse_args()
    if a.proyecto and os.path.exists(os.path.join(a.proyecto, "estado.json")):
        est = json.load(open(os.path.join(a.proyecto, "estado.json"), encoding="utf-8"))
        a.idioma = a.idioma or est.get("idioma")
        tol = est.get("tolerancias", {}); tol = tol.get("etapa", tol) if isinstance(tol.get("etapa"), dict) else tol
        def pct(v):
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", str(v or "")); return float(m.group(1).replace(",", ".")) if m else None
        if a.tol_costo is None: a.tol_costo = pct(tol.get("costo"))
        if a.tol_plazo is None: a.tol_plazo = pct(tol.get("tiempo"))
        for k, v in (("costo", a.tol_costo), ("tiempo", a.tol_plazo)):
            if v is None and tol.get(k):
                print(f"AVISO: la tolerancia de {k} '{tol.get(k)}' no está en %; convertirla y pasarla con --tol-{'costo' if k == 'costo' else 'plazo'} (se usan índices).", file=sys.stderr)
    a.idioma = a.idioma or "es"
    filas = []
    if a.csv:
        for row in csv.DictReader(open(a.csv, encoding="utf-8")):
            tiene = lambda *ns: any(n in row for n in ns)
            if not (tiene("pv", "pv_acumulado") and tiene("ev", "ev_acumulado") and tiene("ac", "ac_acumulado")):
                sys.exit(f"Faltan columnas en {a.csv}. Se aceptan: pv|pv_acumulado, ev|ev_acumulado, ac|ac_acumulado (acumulados).")
            try:
                pv = col(row, "pv", "pv_acumulado"); ev = col(row, "ev", "ev_acumulado"); ac = col(row, "ac", "ac_acumulado")
            except KeyError:
                continue   # período futuro o sin datos reales: se omite
            r = calcular(pv, ev, ac, a.bac, a.eac, a.tol_costo, a.tol_plazo); r["periodo"] = row.get("periodo", "")
            if a.modo == "agil": lectura_agil(r, a.pct_no_must)
            filas.append(r)
        if not filas: sys.exit("El CSV no tiene períodos con valores reales (ev y ac).")
    else:
        if None in (a.pv, a.ev, a.ac): sys.exit("Indicar --pv --ev --ac o --csv")
        r = calcular(a.pv, a.ev, a.ac, a.bac, a.eac, a.tol_costo, a.tol_plazo)
        if a.modo == "agil": lectura_agil(r, a.pct_no_must)
        filas.append(r)
    if a.json: print(json.dumps(filas, ensure_ascii=False, indent=2)); return
    for r in filas:
        if r.get("periodo"): print(f"== {r['periodo']} ==")
        for k in ["PV", "EV", "AC", "BAC", "SV", "CV", "SPI", "CPI", "pct_completado", "pct_gastado", "EAC_tendencia", "EAC_atipico",
                  "EAC_compuesto", "EAC_usado", "ETC", "VAC", "VAC_pct", "sobrecosto_pct", "TCPI_bac", "TCPI_eac", "semaforo_cronograma", "semaforo_costo",
                  "base_semaforo", "alcance_no_entregable_pct", "semaforo_alcance", "excepcion_prevista"]:
            if k not in r: continue
            v = r[k]; print(f"{k:22s} {v:,.3f}" if isinstance(v, float) else f"{k:22s} {v}")
    if a.modo == "agil": print(NOTA_AGIL[a.idioma])
    if any(r["excepcion_prevista"] for r in filas[-1:]):
        print("→ Pronóstico fuera de tolerancia: preparar informe de excepción (pm-progreso-reportes) y escalar a pm-director."
              if a.idioma == "es" else "→ Forecast outside tolerance: prepare an exception report (pm-progreso-reportes) and escalate to pm-director.")

if __name__ == "__main__":
    main()
