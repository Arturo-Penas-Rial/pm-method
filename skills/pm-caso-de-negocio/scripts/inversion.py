#!/usr/bin/env python3
"""Evaluación de la inversión por opción de negocio: VAN, TIR, repago, sensibilidad y punto de equilibrio.
Investment appraisal per business option: NPV, IRR, payback, sensitivity and break-even.

Entrada: CSV con una fila por concepto (o por opción) y una columna por período, en orden (t = 0, 1, 2, …):
    opcion,concepto,tipo,0,1,2,3
    1 · Mínimo,Inversión,inversion,-30000,,,
    1 · Mínimo,Turnos recuperados,beneficio,,48000,48000,48000
    1 · Mínimo,Operación,costo,,-18000,-18000,-18000
- `opcion` (obligatoria). `concepto` y `tipo` (inversion | costo | beneficio) son opcionales: sin `concepto`, cada fila
  es el flujo neto de la opción; sin `tipo`, se deduce del signo (negativo = costo, positivo = beneficio).
- Las columnas de período son las que quedan, en el orden del archivo; celdas vacías = 0. Montos con punto decimal y
  sin separador de miles (10000 o 10000.5). Los flujos van con su signo: egresos negativos, ingresos positivos.

Fórmulas (r = tasa de descuento por período, F_t = flujo neto del período t, t = 0…n):
- VAN (NPV) = Σ F_t / (1 + r)^t
- TIR (IRR) = r tal que VAN(r) = 0, por bisección en [-99 %, 1000 %]; si los flujos cambian de signo más de una vez
  puede haber varias TIR y se informa como ambigua (regla de los signos de Descartes).
- Repago simple = primer período en que el flujo acumulado llega a 0, interpolado dentro del período:
  (t − 1) + (−acumulado_{t−1}) / F_t. Repago descontado: igual con F_t / (1 + r)^t. "—" si no se recupera.
- Sensibilidad: VAN con cada concepto multiplicado por (1 − v) y (1 + v) (v = --variacion), ordenado por amplitud
  (tornado), y VAN con la tasa r ± --delta-tasa.
- Punto de equilibrio de un concepto: como el VAN es lineal en cada concepto, VAN(m) = VAN + (m − 1) · VAN_c, donde
  VAN_c es el valor actual del concepto; el VAN es 0 con m* = 1 − VAN / VAN_c (se informa como % del valor estimado).
  La TIR es el punto de equilibrio de la tasa.
- Comparación: VAN incremental de cada opción frente a la opción base (--base, por defecto la primera).

Uso / Usage:
  inversion.py flujos.csv --tasa 0.10 [--variacion 0.2] [--delta-tasa 0.02] [--base "0 · No hacer nada"] [--idioma es|en] [--json]
Solo biblioteca estándar. El resultado es un cálculo de apoyo: las cifras de origen y la tasa los provee la organización.
"""
import argparse, csv, json, os, sys

TIPOS = ("inversion", "costo", "beneficio")

def num(x, donde):
    x = (x or "").strip()
    if not x: return 0.0
    try: return float(x)
    except ValueError: sys.exit(f"{donde}: monto no numérico {x!r} (usar 10000 o 10000.5, sin separador de miles) / not a number")

def leer(ruta):
    if not os.path.isfile(ruta): sys.exit(f"No existe el archivo / file not found: {ruta}")
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        filas = list(csv.reader(f))
    if not filas: sys.exit(f"{ruta}: vacío / empty")
    cab = [c.strip() for c in filas[0]]
    if "opcion" not in cab: sys.exit(f"{ruta}: falta la columna 'opcion' / missing 'opcion' column")
    meta = {c: cab.index(c) for c in ("opcion", "concepto", "tipo") if c in cab}
    periodos = [i for i in range(len(cab)) if i not in meta.values()]
    if not periodos: sys.exit(f"{ruta}: sin columnas de período / no period columns")
    opciones = {}
    for k, fila in enumerate(filas[1:], 2):
        if not any(x.strip() for x in fila): continue
        fila = fila + [""] * (len(cab) - len(fila))
        op = fila[meta["opcion"]].strip()
        if not op: sys.exit(f"{ruta}:{k}: fila sin opción / row without option")
        flujos = [num(fila[i], f"{ruta}:{k}") for i in periodos]
        concepto = fila[meta["concepto"]].strip() if "concepto" in meta else ""
        tipo = fila[meta["tipo"]].strip().lower() if "tipo" in meta else ""
        if tipo and tipo not in TIPOS: sys.exit(f"{ruta}:{k}: tipo {tipo!r} (inversion | costo | beneficio)")
        if not tipo: tipo = "costo" if sum(flujos) < 0 else "beneficio"
        opciones.setdefault(op, []).append({"concepto": concepto or "flujo neto", "tipo": tipo, "flujos": flujos})
    return [cab[i] for i in periodos], opciones

def van(fl, r): return sum(f / (1 + r) ** t for t, f in enumerate(fl))

def cambios_signo(fl):
    s = [f for f in fl if f]
    return sum(1 for a, b in zip(s, s[1:]) if (a < 0) != (b < 0))

def tir(fl):
    """(tir, ambigua). None si VAN no cambia de signo en el intervalo."""
    if not any(fl): return None, False
    lo, hi = -0.99, 10.0
    vlo, vhi = van(fl, lo), van(fl, hi)
    if vlo == 0: return lo, cambios_signo(fl) > 1
    if vlo * vhi > 0: return None, cambios_signo(fl) > 1
    for _ in range(200):
        m = (lo + hi) / 2; vm = van(fl, m)
        if (vm > 0) == (vlo > 0): lo, vlo = m, vm
        else: hi = m
    return (lo + hi) / 2, cambios_signo(fl) > 1

def repago(fl, r=None):
    f = [x / (1 + r) ** t for t, x in enumerate(fl)] if r is not None else list(fl)
    if not any(f): return None
    acc = f[0]
    if acc >= 0: return 0.0
    for t in range(1, len(f)):
        if acc + f[t] >= 0: return t - 1 + (-acc) / f[t]
        acc += f[t]
    return None

def neto(conceptos, n): return [sum(c["flujos"][t] for c in conceptos) for t in range(n)]

def evaluar(periodos, opciones, r, variacion, delta, base):
    n = len(periodos); res = {}
    for op, cs in opciones.items():
        fl = neto(cs, n); v = van(fl, r); i, amb = tir(fl)
        conceptos = []
        for c in cs:
            vc = van(c["flujos"], r)
            conceptos.append({"concepto": c["concepto"], "tipo": c["tipo"], "van_concepto": vc,
                              "van_menos": v - variacion * vc, "van_mas": v + variacion * vc,
                              "equilibrio": (1 - v / vc) if abs(vc) > 1e-9 else None})
        conceptos.sort(key=lambda c: -abs(c["van_mas"] - c["van_menos"]))
        res[op] = {"flujos": fl, "van": v, "tir": i, "tir_ambigua": amb, "repago": repago(fl), "repago_descontado": repago(fl, r),
                   "van_tasa_menos": van(fl, r - delta), "van_tasa_mas": van(fl, r + delta), "sensibilidad": conceptos}
    b = base if base in res else next(iter(res))
    for op in res: res[op]["van_incremental"] = res[op]["van"] - res[b]["van"]
    return b, res

def fmt(x, dec=None):
    """Número con separador de miles en punto y coma decimal; sin decimales desde 100 en valor absoluto o si es entero."""
    if x is None: return "—"
    if dec is None: dec = 0 if abs(x) >= 100 or float(x).is_integer() else 2   # enteros (y el cero) sin decimales: 0, 36
    if abs(x) < 0.5 * 10 ** -dec: x = 0.0
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("csv"); ap.add_argument("--tasa", type=float, required=True, help="tasa de descuento por período, en tanto por uno (0.10 = 10 %%)")
    ap.add_argument("--variacion", type=float, default=0.2, help="variación de cada concepto para la sensibilidad (0.2 = ±20 %%)")
    ap.add_argument("--delta-tasa", type=float, default=0.02, dest="delta", help="variación de la tasa para la sensibilidad (0.02 = ±2 puntos)")
    ap.add_argument("--base", help="opción base de comparación (por defecto, la primera del archivo)")
    ap.add_argument("--idioma", choices=["es", "en"], default="es"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.tasa <= -1: sys.exit("--tasa debe ser mayor que -1 / must be > -1")
    periodos, opciones = leer(a.csv)
    base, res = evaluar(periodos, opciones, a.tasa, a.variacion, a.delta, a.base)
    if a.json:
        print(json.dumps({"tasa": a.tasa, "variacion": a.variacion, "delta_tasa": a.delta, "periodos": periodos, "base": base, "opciones": res},
                         ensure_ascii=False, indent=2)); return
    t = (lambda es, en: en) if a.idioma == "en" else (lambda es, en: es)
    pct = lambda x: "—" if x is None else fmt(100 * x, 1) + " %"
    anios = lambda x: "—" if x is None else fmt(x, 2)
    print(t(f"Evaluación de la inversión · tasa {pct(a.tasa)} por período · base: {base}", f"Investment appraisal · rate {pct(a.tasa)} per period · base: {base}"))
    print(t("Fórmulas: VAN = Σ F_t/(1+r)^t, t = 0…n · TIR: VAN(TIR) = 0 · repago interpolado en el período en que el acumulado llega a 0",
            "Formulas: NPV = Σ F_t/(1+r)^t, t = 0…n · IRR: NPV(IRR) = 0 · payback interpolated in the period where the cumulative reaches 0"))
    print()
    print(f"{t('Opción', 'Option'):34s} {t('VAN', 'NPV'):>12s} {t('TIR', 'IRR'):>9s} {t('Repago', 'Payback'):>8s} {t('Rep. desc.', 'Disc. pb'):>10s} {t('VAN vs base', 'NPV vs base'):>12s}")
    for op, x in res.items():
        print(f"{op[:34]:34s} {fmt(x['van']):>12s} {pct(x['tir']) + ('*' if x['tir_ambigua'] else ''):>9s} {anios(x['repago']):>8s} {anios(x['repago_descontado']):>10s} {fmt(x['van_incremental']):>12s}")
    if any(x["tir_ambigua"] for x in res.values()):
        print(t("* flujos con más de un cambio de signo: puede haber varias TIR; decidir con el VAN.", "* more than one sign change: several IRRs may exist; decide on NPV."))
    ancho = max([24] + [min(60, len(c["concepto"])) for x in res.values() for c in x["sensibilidad"]])   # columna de concepto: hasta 60 caracteres
    for op, x in res.items():
        print()
        print(t(f"{op} · flujos netos: ", f"{op} · net cash flows: ") + " | ".join(f"{p}: {fmt(f)}" for p, f in zip(periodos, x["flujos"])))
        print(t(f"  Sensibilidad a la tasa: VAN {fmt(x['van_tasa_menos'])} con {pct(a.tasa - a.delta)} · {fmt(x['van_tasa_mas'])} con {pct(a.tasa + a.delta)}",
                f"  Rate sensitivity: NPV {fmt(x['van_tasa_menos'])} at {pct(a.tasa - a.delta)} · {fmt(x['van_tasa_mas'])} at {pct(a.tasa + a.delta)}"))
        print(t(f"  Sensibilidad por concepto (±{fmt(100 * a.variacion, 0)} %), de mayor a menor impacto · punto de equilibrio (VAN = 0):",
                f"  Sensitivity per item (±{fmt(100 * a.variacion, 0)} %), largest first · break-even (NPV = 0):"))
        for c in x["sensibilidad"]:
            eq = c["equilibrio"]
            nom = c["concepto"] if len(c["concepto"]) <= ancho else c["concepto"][:ancho - 1] + "…"
            eq_txt = "—" if eq is None else (t(f"{fmt(100 * eq, 1)} % del valor estimado", f"{fmt(100 * eq, 1)} % of the estimate") if eq >= 0
                                             else t("ningún valor positivo del concepto lo lleva a 0", "no positive value brings it to 0"))
            print(f"    {nom:{ancho}s} [{c['tipo']}] {t('VAN', 'NPV')} {fmt(c['van_menos'])} … {fmt(c['van_mas'])} · {eq_txt}")

if __name__ == "__main__":
    main()
