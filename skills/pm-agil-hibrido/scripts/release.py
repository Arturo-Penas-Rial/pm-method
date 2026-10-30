#!/usr/bin/env python3
"""Capacidad de cada release por MoSCoW contra la velocidad (release plan de pm-agil-hibrido).
Release capacity by MoSCoW against velocity (pm-agil-hibrido release plan).

Uso / Usage:
  release.py --proyecto G capacidad [--release R1] [--velocidad 8] [--must-max 60] [--json]
Lee 02-planificacion/backlog.csv (columnas de gobierno moscow, estimacion, iteracion, release) y la velocidad de
referencia de estado.json.agil (--velocidad la reemplaza, por ejemplo con la observada). Por release:
  capacidad = velocidad × iteraciones distintas del release; puntos Must, Should, Could y sin MoSCoW;
  regla del release plan: Σ Must + Should ≤ capacidad (si no, repriorizar; si ni los Must entran, excepción vía pm-director);
  holgura = capacidad − (Must + Should); Must / capacidad contra la regla práctica Must ≤ ~60 % (--must-max);
  historias de más puntos que la velocidad (no entran en una iteración: dividir), ítems sin MoSCoW o sin puntos y Won't
  con release asignado. No cuenta épicas ni ítems descartados o retirados en BMAD. Solo lectura: no escribe nada.
La misma función (capacidad) la usa impacto.py analizar --puntos --release (pm-issues-cambios) para medir un cambio.
"""
import argparse, csv, json, math, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-estado-proyecto", "scripts")))
import esquema as E

FUERA = {"descartado", "retirada-en-bmad"}


def moscow(f):
    """Valor MoSCoW normalizado: must, should, could, wont o '' (sin clasificar)."""
    v = re.sub(r"[^a-z]", "", (f.get("moscow") or "").strip().lower())
    return v if v in ("must", "should", "could", "wont") else ""


def puntos(f):
    try: return float(str(f.get("estimacion") or "0").replace(",", "."))
    except ValueError: return 0.0


def cuenta(f):
    return (f.get("tipo") or "").strip().lower() not in ("epica", "epic") and (f.get("estado") or "").strip().lower() not in FUERA


def orden_it(x):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", x)]


def capacidad(filas, release, velocidad, liberar=(), agregar=0.0):
    """Capacidad de un release: puntos por MoSCoW, iteraciones, capacidad = velocidad × iteraciones, holgura y, para un
    cambio, puntos con `agregar` y sin las historias de `liberar` (id o prefijo «id-») e iteraciones necesarias."""
    fr = [f for f in filas if (f.get("release") or "").strip() == release and cuenta(f)]
    por = {"must": 0.0, "should": 0.0, "could": 0.0, "wont": 0.0, "": 0.0}
    for f in fr: por[moscow(f)] += puntos(f)
    its = sorted({(f.get("iteracion") or "").strip() for f in fr} - {""}, key=orden_it)
    vel = float(velocidad or 0); cap = vel * len(its)
    total = sum(v for k, v in por.items() if k != "wont")
    sale = sum(puntos(f) for f in fr if any(f["id"] == x or f["id"].startswith(x + "-") for x in liberar))
    nuevo = total + agregar - sale
    nec = math.ceil(round(nuevo / vel, 6)) if vel else None
    return {"release": release, "iteraciones": its, "n_iteraciones": len(its), "velocidad": vel, "capacidad": cap,
            "must": por["must"], "should": por["should"], "could": por["could"], "wont": por["wont"], "sin_moscow": por[""],
            "total": total, "comprometido": por["must"] + por["should"], "holgura": cap - por["must"] - por["should"],
            "pct_must": 100 * por["must"] / cap if cap else None, "sale": sale, "nuevo": nuevo, "necesarias": nec,
            "extra": max(0, nec - len(its)) if nec is not None else None,
            "dividir": [f["id"] for f in fr if vel and puntos(f) > vel],
            "sin_estimar": [f["id"] for f in fr if not moscow(f) or not puntos(f)],
            "wont_con_release": [f["id"] for f in fr if moscow(f) == "wont"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("capacidad", help="capacidad de cada release por MoSCoW contra la velocidad")
    s.add_argument("--release"); s.add_argument("--velocidad", type=float); s.add_argument("--must-max", type=float, default=60.0, dest="must_max")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.proyecto, "estado.json")): sys.exit(f"{a.proyecto}: falta estado.json / not a project folder")
    e = E.cargar_estado(a.proyecto); idi = e.get("idioma", "es"); t = lambda es, en: E.t(idi, es, en)
    pb = os.path.join(a.proyecto, "02-planificacion", "backlog.csv")
    if not os.path.exists(pb): sys.exit(t(f"No existe {pb}: armar antes el backlog (pm-agil-hibrido; con BMAD, bmad.py backlog)", f"{pb} not found: build the backlog first"))
    filas = E.leer_filas(pb, idi)
    vel = a.velocidad if a.velocidad is not None else E.monto((e.get("agil") or {}).get("velocidad_referencia"))
    if not vel or vel <= 0:
        sys.exit(t("Sin velocidad: registrar estado.json.agil.velocidad_referencia (pm-director) o indicar --velocidad",
                   "No velocity: set estado.json.agil.velocidad_referencia or pass --velocidad"))
    rels = sorted({(f.get("release") or "").strip() for f in filas if cuenta(f)} - {""}, key=orden_it)
    if a.release:
        if a.release not in rels: sys.exit(t(f"{a.release} no figura en la columna release del backlog: {', '.join(rels) or 'ninguno'}", f"{a.release} not in backlog: {rels}"))
        rels = [a.release]
    res = [capacidad(filas, r, vel) for r in rels]
    for r in res:
        for k in ("sale", "nuevo", "necesarias", "extra"): r.pop(k)
        if r["must"] > r["capacidad"]: r["lectura"] = "must-no-entran"
        elif r["comprometido"] > r["capacidad"]: r["lectura"] = "repriorizar"
        elif r["total"] > r["capacidad"]: r["lectura"] = "could-no-entran"
        else: r["lectura"] = "entra"
        r["vigilar_must"] = r["lectura"] != "must-no-entran" and r["pct_must"] is not None and r["pct_must"] > a.must_max
    sin_rel = [f for f in filas if cuenta(f) and not (f.get("release") or "").strip()]
    fuente = "--velocidad" if a.velocidad is not None else "estado.json.agil.velocidad_referencia"
    if a.json:
        print(json.dumps({"velocidad": vel, "fuente_velocidad": fuente, "must_max": a.must_max, "releases": res,
                          "sin_release": {"items": len(sin_rel), "puntos": sum(puntos(f) for f in sin_rel)}}, ensure_ascii=False, indent=2)); return
    n = lambda x: (f"{x:.0f}" if float(x).is_integer() else f"{x:.1f}").replace(".", "," if idi != "en" else ".")
    print(t(f"Capacidad por release · velocidad {n(vel)} pts por iteración ({fuente}) · regla: Must + Should ≤ velocidad × iteraciones",
            f"Release capacity · velocity {n(vel)} pts per iteration ({fuente}) · rule: Must + Should ≤ velocity × iterations"))
    print(f"{'Release':8} {t('Iter.', 'Iter.'):>5} {t('Capac.', 'Capac.'):>6} {'Must':>5} {'Should':>6} {'Could':>5} {'M+S':>5} {t('Holgura', 'Slack'):>7} {t('Must/cap.', 'Must/cap.'):>9}")
    for r in res:
        pm = f"{r['pct_must']:.0f} %" if r["pct_must"] is not None else "—"
        print(f"{r['release']:8} {r['n_iteraciones']:>5} {n(r['capacidad']):>6} {n(r['must']):>5} {n(r['should']):>6} {n(r['could']):>5} {n(r['comprometido']):>5} {n(r['holgura']):>7} {pm:>9}")
    for r in res:
        R, cap = r["release"], n(r["capacidad"])
        base = {"must-no-entran": t(f"los Must no entran ({n(r['must'])} de {cap}): excepción vía pm-director; no estirar iteraciones ni bajar la DoD",
                                    f"Must items do not fit ({n(r['must'])} of {cap}): exception via pm-director"),
                "repriorizar": t(f"Must + Should no entran ({n(r['comprometido'])} de {cap}): repriorizar (el PO saca Should/Could del release)",
                                 f"Must + Should do not fit ({n(r['comprometido'])} of {cap}): reprioritise"),
                "could-no-entran": t(f"entran Must y Should ({n(r['comprometido'])} de {cap}); con los Could, {n(r['total'])}: no entran todos",
                                     f"Must and Should fit ({n(r['comprometido'])} of {cap}); with Could, {n(r['total'])}: not all fit"),
                "entra": t(f"entra todo ({n(r['total'])} de {cap}; Must + Should {n(r['comprometido'])}, holgura {n(r['holgura'])})",
                           f"everything fits ({n(r['total'])} of {cap}; Must + Should {n(r['comprometido'])}, slack {n(r['holgura'])})")}[r["lectura"]]
        print(f"- {R} ({', '.join(r['iteraciones'][:12])}{'…' if len(r['iteraciones']) > 12 else ''}): {base}")
        if r["vigilar_must"]:
            print(t(f"  vigilar: los Must son el {r['pct_must']:.0f} % de la capacidad (regla práctica ≤ {n(a.must_max)} %): poco margen MoSCoW para absorber atrasos o cambios sin tocar un Must",
                    f"  watch: Must is {r['pct_must']:.0f} % of capacity (rule of thumb ≤ {n(a.must_max)} %): little MoSCoW margin"))
        if r["dividir"]:
            print(t(f"  dividir (más puntos que la velocidad, no entran en una iteración): {', '.join(r['dividir'][:8])}" + (f" y {len(r['dividir']) - 8} más" if len(r['dividir']) > 8 else ""),
                    f"  split (more points than velocity): {', '.join(r['dividir'][:8])}"))
        if r["sin_estimar"]:
            print(t(f"  sin MoSCoW o sin puntos: {', '.join(r['sin_estimar'][:8])}" + (f" y {len(r['sin_estimar']) - 8} más" if len(r['sin_estimar']) > 8 else ""),
                    f"  missing MoSCoW or points: {', '.join(r['sin_estimar'][:8])}"))
        if r["wont_con_release"]:
            print(t(f"  Won't con release asignado (no cuenta): {', '.join(r['wont_con_release'][:8])}", f"  Won't items with a release (not counted): {', '.join(r['wont_con_release'][:8])}"))
    if sin_rel:
        print(t(f"Sin release: {len(sin_rel)} ítem(s), {n(sum(puntos(f) for f in sin_rel))} pts", f"No release: {len(sin_rel)} item(s), {n(sum(puntos(f) for f in sin_rel))} pts"))


if __name__ == "__main__":
    main()
