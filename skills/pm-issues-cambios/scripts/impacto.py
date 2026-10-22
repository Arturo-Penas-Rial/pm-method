#!/usr/bin/env python3
"""Análisis de impacto de una solicitud de cambio (C-###) y borrador de la solicitud con opciones y quién decide.
Change impact analysis for a change request (C-###) and draft change request with options and the deciding level.

Uso / Usage:
  impacto.py --proyecto G analizar C-001
      [--actividades ESCENARIO.csv [--actividades-base 02-planificacion/actividades.csv] [--inicio AAAA-MM-DD] [--pert PERT.csv [--confianza 2]]]
      [--flujos FLUJOS.csv --opcion "Con C-001" [--base "Línea base"] --tasa 0.10 [--variacion 0.10]]
      [--refs FR-13,E-2] [--paquetes 3.4] [--puntos 8 --release R2 [--liberar 2-3] [--etapa]] [--evm 03-control/reportes/evm-<corte>.json]
      [--costo 9000] [--cargo presupuesto-cambio] [--tol-dias 15] [--fecha AAAA-MM-DD] [--salida F.md] [--json]
Escenario (lo prepara la persona o el modelo; el script no inventa cifras):
  --actividades        CSV de cpm.py con el cambio incorporado (actividades nuevas o predecesoras cambiadas); se compara con
                       --actividades-base (por defecto 02-planificacion/actividades.csv): duración, fin, camino crítico y las
                       actividades que se corren (dependencias). --pert (el que escribe cpm.py --estimacion: id, optimista,
                       mas_probable, pesimista, distribucion) da la reserva de cronograma a kσ del camino crítico base
                       (σ = √Σσ² con la σ de la distribución declarada, beta-PERT si falta; --confianza k, por defecto 2) y
                       cuánto queda. Las actividades con tres valores toman tE con esa misma distribución.
  --flujos/--opcion    CSV de inversion.py con la opción base y la opción con el cambio: VAN, VAN incremental y cuánto puede
                       caer el beneficio principal antes de que el VAN llegue a 0, contra la tolerancia de beneficios.
  --refs/--paquetes    requisitos, épicas o historias (fachada especificacion.py) y paquetes de la WBS afectados: estado en la
                       especificación, líneas base vigentes, riesgos abiertos y actividades de calidad que los citan.
  --puntos/--release   capacidad del release en backlog.csv con la velocidad de estado.json.agil, con la misma regla que
                       release.py capacidad (pm-agil-hibrido; --liberar: historias que salen del release); --etapa: el
                       release cierra la etapa actual (el atraso se mide contra su tolerancia).
  --evm                corte guardado por evm.py (alcance que no entra, excepción prevista).
  costo y cargo salen de cambios.csv (o --costo/--cargo); la tolerancia de tiempo del proyecto, de estado.json
  ("±3 semanas" = 15 días laborables, "±10 %" de la duración base; --tol-dias la fija).
Quién decide: la regla de autoridad y presupuesto de cambio de registro.py (motivos_autoridad), las tolerancias de etapa y de
proyecto y la excepción prevista del EVM. Salida: tabla de impacto y borrador de solicitud de cambio
(03-control/reportes/<fecha>-solicitud-cambio-C-###.md, estado borrador) con opciones aprobar, rechazar, diferir y pedir
plan de excepción. No escribe registros: los comandos para dejar el análisis en cambios.csv se muestran para después de la
decisión humana.
"""
import argparse, csv, datetime, json, math, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.normpath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SK, "pm-estado-proyecto", "scripts"))
sys.path.insert(0, os.path.join(SK, "pm-caso-de-negocio", "scripts"))
sys.path.insert(0, os.path.join(SK, "pm-agil-hibrido", "scripts"))
import esquema as E
import registro as RG
import cpm as CPM
import inversion as INV
import release as REL

IDIOMA = "es"
PC = "[por confirmar]"
def t(es, en): return en if IDIOMA == "en" else es
def num(x, d=0):
    if x is None: return "—"
    s = f"{x:,.{d}f}"
    return s if IDIOMA == "en" else s.replace(",", "§").replace(".", ",").replace("§", ".")

def ruta(proyecto, r):
    if not r: return None
    for c in (r, os.path.join(proyecto, r)):
        if os.path.isfile(c): return c
    sys.exit(t(f"No existe el archivo: {r}", f"File not found: {r}"))

def tol_dias_proyecto(texto, base):
    """Días laborables de la tolerancia de tiempo del proyecto: "±N semanas" = 5·N; "±N días" = N; "±N %" de la duración base."""
    s = str(texto or "")
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", s)
    if m: return float(m.group(1).replace(",", ".")) * base / 100 if base else None
    m = re.search(r"(\d+)\s*(semana|week)", s, re.I)
    if m: return 5 * int(m.group(1))
    m = re.search(r"(\d+)\s*(d[ií]a|day)", s, re.I)
    return int(m.group(1)) if m else None

def tol_dias_etapa(texto, dias_etapa):
    """Días corridos de la tolerancia de tiempo de la etapa: "±N %" de la duración de la etapa; semanas = 7·N; días = N."""
    s = str(texto or "")
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", s)
    if m: return float(m.group(1).replace(",", ".")) * dias_etapa / 100 if dias_etapa else None
    m = re.search(r"(\d+)\s*(semana|week)", s, re.I)
    if m: return 7 * int(m.group(1))
    m = re.search(r"(\d+)\s*(d[ií]a|day)", s, re.I)
    return int(m.group(1)) if m else None

def pct(texto):
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", str(texto or ""))
    return float(m.group(1).replace(",", ".")) if m else None

def correr_cpm(p, distribucion="beta"):
    acts = CPM.cargar(p, distribucion); orden, fin = CPM.cpm(acts)
    return acts, fin, [i for i in orden if acts[i]["critica"]]

def leer(proyecto, rel):
    p = os.path.join(proyecto, rel)
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []

def menciona(texto, claves):
    return [k for k in claves if k and re.search(rf"(?<![\w.-]){re.escape(k)}(?![\w-]|\.\d)", texto or "")]

def analizar(a, e):
    p = a.proyecto
    cambios = E.leer_csv(E.ruta_registro(p, "cambios"))[1] if os.path.exists(E.ruta_registro(p, "cambios")) else []
    fila = next((f for f in cambios if f.get("id") == a.cambio), None)
    if not fila: sys.exit(t(f"No existe {a.cambio} en cambios.csv: registrar antes la solicitud (issue solicitud-cambio → C-###).",
                            f"{a.cambio} not in cambios.csv: record the change request first."))
    costo = a.costo if a.costo is not None else (E.monto(fila.get("costo")) or 0.0)
    cargo = a.cargo or fila.get("cargo") or ""
    supuestos = []
    if costo > 0 and not cargo:
        cargo = "presupuesto-cambio"; supuestos.append(t("sin cargo declarado: se calcula contra el presupuesto de cambio (declararlo en cambios.csv, CAM-01)",
                                                      "no charge declared: computed against the change budget (declare it, CAM-01)"))
    tolp, tole = (e.get("tolerancias") or {}).get("proyecto", {}), (e.get("tolerancias") or {}).get("etapa", {})
    roles, pres, agil = e.get("roles") or {}, e.get("presupuestos") or {}, e.get("agil") or {}
    filas, fuera, notas = [], {"tiempo": False, "tiempo_etapa": False, "alcance": False, "costo": False, "beneficios": False}, []
    F = lambda obj, antes, con, contra, lectura: filas.append({"objetivo": obj, "antes": antes, "con": con, "contra": contra, "lectura": lectura})
    claves = [a.cambio] + [x.strip() for x in (a.refs or "").split(",") if x.strip()] + [x.strip() for x in (a.paquetes or "").split(",") if x.strip()]
    # ---------------- alcance y especificación
    refs = [x.strip() for x in (a.refs or "").split(",") if x.strip()]
    paquetes = [x.strip() for x in (a.paquetes or "").split(",") if x.strip()]
    espec = []
    if refs:
        import especificacion as ES
        idx, _ = ES.obtener(p)
        for r in refs:
            m = ES.REQ.match(r); q = ES.norm(m.group(1), m.group(2)) if m else r
            x = next((x for col in ("requisitos", "historias", "epicas") for x in idx.get(col, []) if x["id"] == q or x.get("numero") == q), None)
            espec.append({"id": r, "en_especificacion": bool(x), "titulo": (x or {}).get("titulo") or (x or {}).get("nombre", ""),
                          "estado": (x or {}).get("estado", ""), "cobertura": (x or {}).get("cobertura", "")})
    lineas = [f"{k} v{v.get('version')}" for k, v in (e.get("artefactos") or {}).items() if v.get("externo") == "bmad" and v.get("version")]
    nuevos = [x["id"] for x in espec if not x["en_especificacion"]]
    desc = "; ".join(filter(None, [(t("paquetes WBS ", "WBS packages ") + ", ".join(paquetes)) if paquetes else "",
                                   (f"+{num(a.puntos)} pts" + (f" {t('en', 'in')} {a.release}" if a.release else "")) if a.puntos else "",
                                   (t("requisitos ", "requirements ") + ", ".join(refs)) if refs else ""])) or PC
    F(t("Alcance y especificación", "Scope and specification"), t("línea base ", "baseline ") + (", ".join(lineas) or t("sin líneas base de la especificación", "no specification baselines")),
      desc, tolp.get("alcance") or PC,
      (t(f"{', '.join(nuevos)} no está en la especificación vigente: tras aprobar, traspaso (bmad.py handoff --cambio {a.cambio}) y nueva línea base (pm-director)",
         f"{', '.join(nuevos)} not in the current specification: after approval, handoff and a new baseline (pm-director)") if nuevos else
       t("afecta ids existentes: " + ", ".join(f"{x['id']} ({x['estado'] or x['cobertura'] or 'sin estado'})" for x in espec), "affects existing ids: " + ", ".join(x["id"] for x in espec)) if espec
       else t("sin requisitos ni épicas indicados (--refs)", "no requirements or epics given (--refs)")))
    # ---------------- tiempo, reserva y dependencias
    dur0 = None
    if a.actividades:
        base_p = ruta(p, a.actividades_base or os.path.join("02-planificacion", "actividades.csv"))
        pe = {r["id"].strip(): r for r in csv.DictReader(open(ruta(p, a.pert), encoding="utf-8"))} if a.pert else {}
        dist = next((r.get("distribucion", "").strip() for r in pe.values() if (r.get("distribucion") or "").strip()), "") or "beta"
        if dist not in CPM.DISTRIBUCIONES: sys.exit(t(f"distribución desconocida en {a.pert}: {dist}", f"unknown distribution in {a.pert}: {dist}"))
        acts0, dur0, cam0 = correr_cpm(base_p, dist); acts1, dur1, cam1 = correr_cpm(ruta(p, a.actividades), dist)
        d = dur1 - dur0
        ini = datetime.date.fromisoformat(a.inicio) if a.inicio else None
        fin = lambda n: CPM.dias_laborables(ini, n).isoformat() if ini else ""
        tol = a.tol_dias if a.tol_dias is not None else tol_dias_proyecto(tolp.get("tiempo"), dur0)
        fuera["tiempo"] = tol is not None and d > tol
        F(t("Tiempo (camino crítico)", "Time (critical path)"), f"{dur0} {t('días', 'days')}" + (f" · {t('fin', 'end')} {fin(dur0)}" if ini else ""),
          f"{dur1} {t('días', 'days')}" + (f" · {t('fin', 'end')} {fin(dur1)}" if ini else "") + f" ({'+' if d >= 0 else ''}{d})",
          (t(f"tolerancia del proyecto {tolp.get('tiempo')} = {num(tol)} días laborables", f"project tolerance {tolp.get('tiempo')} = {num(tol)} working days") if tol is not None
           else t(f"tolerancia del proyecto «{tolp.get('tiempo') or '—'}» no interpretable: indicar --tol-dias", "project tolerance not parseable: use --tol-dias")),
          (t("sin efecto en la fecha" if d <= 0 else (f"dentro: usa {d} de {num(tol)} ({100 * d / tol:.0f} %)" if not fuera["tiempo"] else f"fuera de tolerancia: {d} > {num(tol)} → excepción"),
             "no date impact" if d <= 0 else (f"within: uses {d} of {num(tol)}" if not fuera["tiempo"] else f"outside tolerance: {d} > {num(tol)} → exception"))
           if tol else t(f"{'+' if d >= 0 else ''}{d} días laborables", f"{'+' if d >= 0 else ''}{d} working days")))
        corridas = [i for i in acts1 if i in acts0 and acts1[i]["EF"] != acts0[i]["EF"]]
        nuevas = [i for i in acts1 if i not in acts0]
        F(t("Dependencias", "Dependencies"), t(f"camino crítico {' → '.join(cam0)}", f"critical path {' → '.join(cam0)}"),
          t(f"camino crítico {' → '.join(cam1)}", f"critical path {' → '.join(cam1)}"), "cpm.py",
          t((f"actividades nuevas: {', '.join(nuevas)}; " if nuevas else "") + (f"se corren: " + ", ".join(f"{i} (+{acts1[i]['EF'] - acts0[i]['EF']})" for i in corridas[:8])
             + (f" y {len(corridas) - 8} más" if len(corridas) > 8 else "") if corridas else "ninguna actividad existente se corre"),
            (f"new: {', '.join(nuevas)}; " if nuevas else "") + (f"shifted: " + ", ".join(f"{i} (+{acts1[i]['EF'] - acts0[i]['EF']})" for i in corridas[:8]) if corridas else "no existing activity shifts")))
        if a.pert:
            def sigma(r):
                o, pe_ = float(r["optimista"]), float(r["pesimista"])
                m = float(r["mas_probable"]) if (r.get("mas_probable") or "").strip() else None
                if m is None and dist != "beta": sys.exit(t(f"{a.pert}: falta mas_probable para la distribución {dist}", f"{a.pert}: mas_probable needed for {dist}"))
                return CPM.tres_valores(o, m if m is not None else o, pe_, dist)[1]
            sig = [sigma(pe[i]) for i in cam0 if i in pe and pe[i].get("pesimista") and pe[i].get("optimista")]
            k = a.confianza; ks = f"{k:g}".replace(".", "," if IDIOMA != "en" else ".") + "σ"
            res0 = k * CPM.sigma_camino(sig); res1 = res0 - max(d, 0)
            F(t("Reserva de cronograma", "Schedule reserve"), f"{ks} = {num(res0, 1)} {t('días', 'days')}", f"{num(res0, 1)} − {max(d, 0)} = {num(res1, 1)} {t('días', 'days')}",
              t(f"atraso posible del camino crítico (tres valores, {'beta-PERT' if dist == 'beta' else dist})", f"possible critical path delay (three-point, {'beta-PERT' if dist == 'beta' else dist})"),
              t("se agota: registrar riesgo" if res1 <= 0 else ("queda menos de la mitad: registrar riesgo" if res1 < res0 / 2 else "alcanza"),
                "exhausted: record a risk" if res1 <= 0 else ("less than half left: record a risk" if res1 < res0 / 2 else "enough")))
            if res1 < res0 / 2: notas.append(t(f"riesgo nuevo sugerido: la reserva de cronograma queda en {num(res1, 1)} días (pm-riesgos)", f"suggested new risk: schedule reserve down to {num(res1, 1)} days"))
    # ---------------- capacidad del release y tiempo de la etapa
    if a.puntos is not None and a.release:
        bl = leer(p, os.path.join("02-planificacion", "backlog.csv"))
        vel = float(agil.get("velocidad_referencia") or 0); cad = int(float(agil.get("cadencia_iteracion_dias") or 0))
        lib = [x.strip() for x in (a.liberar or "").split(",") if x.strip()]
        cp = REL.capacidad(bl, a.release, vel, liberar=lib, agregar=a.puntos)     # misma regla que release.py capacidad (pm-agil-hibrido)
        pts, spr, sale, nuevo = cp["total"], cp["n_iteraciones"], cp["sale"], cp["nuevo"]
        if vel:
            nec, extra = cp["necesarias"], cp["extra"]
            F(t(f"Capacidad del {a.release}", f"{a.release} capacity"), f"{num(pts)} pts {t('de', 'of')} {num(spr * vel)} ({spr} sprints)",
              f"{num(nuevo)} pts" + (t(f" (sin {', '.join(lib)}: −{num(sale)})", f" (without {', '.join(lib)}: −{num(sale)})") if lib else ""),
              t(f"velocidad {num(vel)} pts por sprint", f"velocity {num(vel)} pts per sprint"),
              t(f"entra en {spr} sprints" if not extra else f"{nec} sprints: +{extra} sprint ({extra * cad} días corridos)", f"fits in {spr} sprints" if not extra else f"{nec} sprints: +{extra} ({extra * cad} calendar days)"))
            if a.etapa and extra:
                et = e.get("etapa_actual") or {}
                try: dias = (datetime.date.fromisoformat(et["fin_previsto"]) - datetime.date.fromisoformat(et["inicio"])).days
                except (KeyError, ValueError, TypeError): dias = None
                te = tol_dias_etapa(tole.get("tiempo"), dias)
                nfin = (datetime.date.fromisoformat(et["fin_previsto"]) + datetime.timedelta(days=extra * cad)).isoformat() if dias else PC
                fuera["tiempo_etapa"] = te is not None and extra * cad > te
                F(t("Tiempo de la etapa", "Stage time"), t(f"fin {et.get('fin_previsto') or PC}", f"end {et.get('fin_previsto') or 'TBC'}"), f"{t('fin', 'end')} {nfin} (+{extra * cad})",
                  t(f"tolerancia de etapa {tole.get('tiempo') or '—'} = {num(te, 1)} días" if te is not None else "tolerancia de etapa no interpretable", f"stage tolerance = {num(te, 1)} days"),
                  t("fuera de tolerancia → excepción" if fuera["tiempo_etapa"] else "dentro", "outside tolerance → exception" if fuera["tiempo_etapa"] else "within"))
        else: notas.append(t("sin estado.json.agil.velocidad_referencia: no se mide la capacidad del release", "no reference velocity: release capacity not measured"))
    if a.evm:
        ev = json.load(open(ruta(p, a.evm), encoding="utf-8"))
        if ev.get("alcance_no_entregable_pct") is not None:
            fuera["alcance"] = bool(ev.get("excepcion_prevista"))
            F(t("Alcance (EVM)", "Scope (EVM)"), t(f"Should/Could = {num(ev.get('pct_no_must'))} % del alcance", f"Should/Could = {num(ev.get('pct_no_must'))} % of scope"),
              t(f"no entra {num(ev['alcance_no_entregable_pct'], 1)} %", f"{num(ev['alcance_no_entregable_pct'], 1)} % does not fit"), t("Must sin tolerancia", "Must has no tolerance"),
              t("los Must peligran → excepción" if fuera["alcance"] else "los Must no peligran", "Must items at risk → exception" if fuera["alcance"] else "Must items safe"))
        else:
            fuera["alcance"] = bool(ev.get("excepcion_prevista"))
            F("EVM", f"CPI {num(ev.get('CPI'), 2)} · SPI {num(ev.get('SPI'), 2)}", f"EAC {num(ev.get('EAC'))}", t("tolerancias de etapa", "stage tolerances"),
              t("excepción prevista" if fuera["alcance"] else "sin excepción prevista", "exception forecast" if fuera["alcance"] else "no exception forecast"))
    # ---------------- costo, presupuesto de cambio y autoridad (regla de registro.py)
    wbs = leer(p, os.path.join("02-planificacion", "wbs.csv"))
    paq = [f for f in wbs if (f.get("tipo") or "").strip() == "paquete"] or wbs
    bac = sum(E.monto(f.get("costo")) or 0 for f in paq)
    var = 100 * costo / bac if bac else None
    tcosto = pct(tolp.get("costo"))
    financia = cargo in ("presupuesto-cambio", "reserva-riesgo", "reserva-gestion", "plan-excepcion")
    fuera["costo"] = bool(var is not None and tcosto is not None and var > tcosto and not financia)
    F(t("Costo (BAC)", "Cost (BAC)"), num(bac) if bac else PC, (f"{num(bac + costo)} (+{num(costo)}" + (f", {num(var, 1)} %)" if var is not None else ")")) if bac else f"+{num(costo)}",
      t(f"tolerancia de costo {tolp.get('costo') or '—'}; cargo {cargo or 'sin costo'}", f"cost tolerance {tolp.get('costo') or '—'}; charge {cargo or 'none'}"),
      t(f"se financia con {cargo}, no con la tolerancia de costo" if financia and costo else ("sin costo" if not costo else ("fuera de la tolerancia de costo" if fuera["costo"] else "dentro de la tolerancia de costo")),
        f"funded by {cargo}, not the cost tolerance" if financia and costo else ("no cost" if not costo else ("outside cost tolerance" if fuera["costo"] else "within cost tolerance"))))
    RG.IDIOMA = IDIOMA
    hip = {**fila, "costo": str(costo), "cargo": cargo, "decision": "aprobado", "estado": "aprobado"}
    err_del, aviso = RG.motivos_autoridad(e, hip, cambios, junta=False)
    err_junta, _ = RG.motivos_autoridad(e, hip, cambios, junta=True)
    usado = E.consumo_cambios(cambios, excluir=a.cambio)
    if cargo == "presupuesto-cambio":
        tope = E.monto(pres.get("cambio"))
        F(t("Presupuesto de cambio", "Change budget"), f"{num(usado['presupuesto-cambio'])} {t('de', 'of')} {num(tope) if tope is not None else '—'}",
          f"{num(usado['presupuesto-cambio'] + costo)} {t('de', 'of')} {num(tope) if tope is not None else '—'}" + (f" ({100 * (usado['presupuesto-cambio'] + costo) / tope:.0f} %)" if tope else ""),
          t("saldo fijado por la junta (CAM-03: aviso desde 80 %, error sobre 100 %)", "balance set by the board (CAM-03)"),
          t("sin presupuesto fijado: lo fija la junta" if tope is None else ("dentro del saldo" if usado["presupuesto-cambio"] + costo <= tope else "no alcanza: otra fuente o ampliarlo"),
            "no budget set" if tope is None else ("within balance" if usado["presupuesto-cambio"] + costo <= tope else "not enough: another source or raise it")))
    lim = E.monto(pres.get("limite_autoridad_cambio"))
    F(t("Autoridad", "Authority"), t(f"límite {num(lim)} por cambio" if lim is not None else "sin límite fijado", f"limit {num(lim)} per change" if lim is not None else "no limit set"),
      f"{num(costo)} {t('en este cambio', 'in this change')}", "registro.py (motivos_autoridad) · CAM-04/CAM-05",
      t("excede la autoridad delegada" if err_del else "dentro de la autoridad delegada", "exceeds delegated authority" if err_del else "within delegated authority"))
    # ---------------- beneficios (business case)
    if a.flujos:
        if a.tasa is None: sys.exit(t("--flujos requiere --tasa (la fija finanzas)", "--flujos needs --tasa"))
        per, ops = INV.leer(ruta(p, a.flujos))
        if a.opcion not in ops: sys.exit(t(f"--opcion «{a.opcion}» no está en {a.flujos}: {list(ops)}", f"--opcion not found: {list(ops)}"))
        b, res = INV.evaluar(per, ops, a.tasa, a.variacion, 0.02, a.base)
        tb = pct(tolp.get("beneficios")) or 100 * a.variacion
        def margen(op):
            bs = [c for c in res[op]["sensibilidad"] if c["tipo"] == "beneficio" and c["van_concepto"] > 0]
            if not bs: return None, ""
            c = max(bs, key=lambda c: c["van_concepto"]); return 100 * res[op]["van"] / c["van_concepto"], c["concepto"]
        m0, c0 = margen(b); m1, c1 = margen(a.opcion)
        fuera["beneficios"] = res[a.opcion]["van"] <= 0 or (m1 is not None and m1 <= tb)
        F(t("Beneficios (VAN)", "Benefits (NPV)"), f"{num(res[b]['van'])}" + (t(f" · {c0} puede caer {num(m0)} %", f" · {c0} can fall {num(m0)} %") if m0 is not None else ""),
          f"{num(res[a.opcion]['van'])} ({'+' if res[a.opcion]['van_incremental'] >= 0 else ''}{num(res[a.opcion]['van_incremental'])})"
          + (t(f" · {c1} puede caer {num(m1)} %", f" · {c1} can fall {num(m1)} %") if m1 is not None else ""),
          t(f"inversion.py, tasa {100 * a.tasa:g} % · VAN > 0 · tolerancia de beneficios −{num(tb)} %", f"inversion.py, rate {100 * a.tasa:g} % · NPV > 0 · benefits tolerance −{num(tb)} %"),
          t("deja de estar justificado → excepción" if fuera["beneficios"] else ("a favor: el cambio suma valor" if res[a.opcion]["van_incremental"] > 0 else "sigue justificado, con menos margen"),
            "no longer justified → exception" if fuera["beneficios"] else ("in favour: adds value" if res[a.opcion]["van_incremental"] > 0 else "still justified, smaller margin")))
    # ---------------- riesgos y calidad que citan lo afectado
    rs = [r for r in leer(p, "03-control/registros/riesgos.csv") if r.get("estado") in E.REGISTROS["riesgos"]["abiertos"]
          and menciona(" ".join(r.get(k, "") for k in ("causa", "evento", "efecto", "notas", "acciones")), claves)]
    F(t("Riesgo", "Risk"), t(f"{len(rs)} riesgo(s) abierto(s) citan lo afectado", f"{len(rs)} open risk(s) cite the affected items") + (": " + ", ".join(r["id"] for r in rs[:8]) if rs else ""),
      "; ".join(notas) or t("sin riesgo nuevo calculado", "no new risk computed"), tolp.get("riesgo") or PC,
      t("revisar con pm-riesgos" if rs or notas else PC, "review with pm-riesgos" if rs or notas else "TBC"))
    qs = [q for q in leer(p, "03-control/registros/calidad.csv") if menciona(q.get("producto", ""), claves)]
    F(t("Calidad", "Quality"), t(f"{len(qs)} actividad(es) de calidad de lo afectado", f"{len(qs)} quality activit(ies)") + (": " + ", ".join(q["id"] for q in qs[:8]) if qs else ""),
      t("criterios de calidad del producto nuevo o cambiado", "quality criteria of the new or changed product"), tolp.get("calidad") or PC,
      t("planificar revisión o prueba (pm-calidad)" if not qs else "actualizar criterios y fechas (pm-calidad)", "plan a review or test (pm-calidad)" if not qs else "update criteria and dates"))
    # ---------------- quién decide (PRINCE2: issues 3.c.1 paso 4, 3.c.2; excepción 4.c.2)
    motivos = []
    if fuera["tiempo"] or fuera["beneficios"]:
        nivel = "capa-negocio" if fuera["tiempo"] else "junta"
    elif fuera["tiempo_etapa"] or fuera["alcance"] or fuera["costo"]:
        nivel = "junta"
    elif err_del:
        nivel = "junta"
    else:
        nivel = "autoridad-cambio"
    if fuera["tiempo"]: motivos.append(t("el pronóstico sale de la tolerancia de tiempo del proyecto: lo decide la capa de negocio vía la junta", "forecast outside the project time tolerance"))
    if fuera["tiempo_etapa"]: motivos.append(t("el pronóstico sale de la tolerancia de tiempo de la etapa: informe de excepción a la junta", "forecast outside the stage time tolerance"))
    if fuera["alcance"]: motivos.append(t("el EVM pronostica que los Must no entran: excepción", "EVM forecasts Must items do not fit"))
    if fuera["costo"]: motivos.append(t("la variación de costo sale de la tolerancia sin una fuente de financiación", "cost variance outside tolerance without funding"))
    if fuera["beneficios"]: motivos.append(t("el business case deja de estar justificado dentro de la tolerancia de beneficios", "business case no longer justified"))
    motivos += [m.split(": ", 1)[-1].rstrip(".") for m in err_del]
    excepcion = any(fuera[k] for k in ("tiempo", "tiempo_etapa", "alcance", "costo", "beneficios"))
    quien = {"autoridad-cambio": t(f"Autoridad de cambio: {roles.get('autoridad_cambio') or '[sin nombrar en estado.json.roles]'}", f"Change authority: {roles.get('autoridad_cambio') or '[not named]'}"),
             "junta": t(f"Junta (ejecutivo: {roles.get('ejecutivo') or PC}) vía pm-director", f"Board (executive: {roles.get('ejecutivo') or 'TBC'}) via pm-director"),
             "capa-negocio": t("Capa de negocio vía la junta y pm-director", "Business layer via the board and pm-director")}[nivel]
    opciones = [
        {"opcion": t("Aprobar", "Approve"), "aplica": not excepcion and not err_junta,
         "detalle": (t(f"cargo {cargo}" if costo else "sin costo", f"charge {cargo}" if costo else "no cost") + ("" if not err_del else t("; solo la junta o el ejecutivo", "; only the board or executive"))
                     + ("" if not err_junta else t("; la fuente no alcanza: indicar reserva-gestion, plan-excepcion o ampliar el presupuesto", "; source not enough")))},
        {"opcion": t("Rechazar", "Reject"), "aplica": True, "detalle": t("se mantiene la línea base; ¿sigue valiendo la justificación y los beneficios sin el cambio?", "baseline kept; are benefits still achieved?")},
        {"opcion": t("Diferir", "Defer"), "aplica": True, "detalle": t("con fecha o evento de reevaluación (obligatorio en notas)", "with a re-evaluation date or event")},
        {"opcion": t("Pedir plan de excepción", "Request an exception plan"), "aplica": excepcion or bool(err_junta),
         "detalle": t("el cambio saca el plan de tolerancia o no tiene fuente: informe de excepción y plan (pm-director)" if excepcion or err_junta else "no hace falta: el cambio entra en las tolerancias",
                      "the change breaches tolerance or lacks funding" if excepcion or err_junta else "not needed: within tolerances")}]
    rec = (t("pedir plan de excepción", "request an exception plan") if excepcion else t("escalar a la junta: aprobar indicando la fuente", "escalate to the board") if err_del or err_junta
           else t("aprobar con el cargo indicado", "approve with the stated charge"))
    issue = (re.search(r"\bI-\d{3,}\b", " ".join(fila.get(k, "") for k in ("descripcion", "notas"))) or [""])[0]
    return {"cambio": a.cambio, "titulo": fila.get("titulo", ""), "solicitante": fila.get("solicitante", ""), "issue": issue, "costo": costo, "cargo": cargo,
            "filas": filas, "fuera_de_tolerancia": fuera, "excepcion": excepcion, "nivel": nivel, "quien_decide": quien, "motivos": motivos, "opciones": opciones,
            "recomendacion": rec, "supuestos": supuestos, "aviso": aviso, "especificacion": espec, "riesgos": [r["id"] for r in rs], "calidad": [q["id"] for q in qs], "fila": fila}

def celda(x): return str(x if x is not None else "").replace("|", "/").replace("\n", " ")

def markdown(r, e, fecha):
    f = r["fila"]; filas = r["filas"]
    L = ["---", "tipo: solicitud-cambio", f"proyecto: \"{e.get('proyecto', '')}\"", "version: \"0.1\"", f"fecha: \"{fecha}\"", "autor: \"\"", "estado: borrador",
         "aprobado_por: \"\"", f"idioma: \"{e.get('idioma', 'es')}\"", "---", "",
         t(f"# Solicitud de cambio · {r['cambio']} {r['titulo']}", f"# Change request · {r['cambio']} {r['titulo']}"), "",
         f"**{t('Identificador', 'Change id')}:** {r['cambio']} · **{t('Issue de origen', 'Source issue')}:** {r['issue'] or PC} · **{t('Solicitante', 'Requestor')}:** {f.get('solicitante') or PC}", "",
         t("> Borrador generado con impacto.py (análisis de impacto con cpm.py, inversion.py, backlog, presupuestos y la regla de autoridad de registro.py). "
           "No es una decisión: decide el nivel indicado en §6; las cifras sin fuente van [por confirmar].",
           "> Draft from impacto.py. Not a decision: the level in §6 decides."), "",
         t("## 1. Descripción del cambio", "## 1. Description"), "", f"{f.get('descripcion') or PC}", "",
         t("## 2. Justificación", "## 2. Justification"), "", f"{f.get('justificacion') or PC}", "",
         t("## 3. Análisis de impacto", "## 3. Impact analysis"), "",
         "| " + " | ".join([t("Objetivo", "Objective"), t("Antes", "Before"), f"{t('Con', 'With')} {r['cambio']}", t("Contra qué se mide", "Measured against"), t("Lectura", "Reading")]) + " |", "|---|---|---|---|---|"]
    L += ["| " + " | ".join(celda(x[k]) for k in ("objetivo", "antes", "con", "contra", "lectura")) + " |" for x in filas]
    tol = (e.get("tolerancias") or {}).get("proyecto", {})
    L += ["", t(f"Sostenibilidad: {tol.get('sostenibilidad') or PC} (no la calcula el script).", f"Sustainability: {tol.get('sostenibilidad') or 'TBC'} (not computed)")]
    if r["supuestos"]: L += ["", t("Supuestos del cálculo: ", "Calculation assumptions: ") + "; ".join(r["supuestos"])]
    L += ["", t("## 4. Opciones", "## 4. Options"), "", "| " + " | ".join([t("Opción", "Option"), t("¿Aplica?", "Applies?"), t("Detalle", "Detail")]) + " |", "|---|---|---|"]
    L += [f"| {o['opcion']} | {t('sí', 'yes') if o['aplica'] else 'no'} | {celda(o['detalle'])} |" for o in r["opciones"]]
    L += ["", t("## 5. Recomendación (borrador)", "## 5. Recommendation (draft)"), "", f"{r['recomendacion']}. " + t("La redacta y firma el gestor del proyecto.", "The project manager writes and signs it."), "",
          t("## 6. Autoridad y decisión", "## 6. Authority and decision"), "", f"**{t('Nivel que decide', 'Deciding level')}:** {r['nivel']} — {r['quien_decide']}", ""]
    L += [f"- {m}" for m in r["motivos"]] or [t("- dentro del límite delegado, del saldo del presupuesto de cambio y de las tolerancias", "- within the delegated limit, the change budget and the tolerances")]
    L += ["", f"**{t('Disposición', 'Disposition')}:** {t('(vacío hasta la decisión humana)', '(empty until the human decision)')}", "",
          t("Tras la decisión, dejar el análisis en `cambios.csv` (lo ejecuta pm-control; si decide la junta, pm-director registra la puerta):",
            "After the decision, record the analysis in cambios.csv:"), "", "```",
          f"registro.py --proyecto <dir> actualizar cambios {r['cambio']} --campo \"impacto_tiempo={celda(next((x['con'] + ' · ' + x['lectura'] for x in filas if x['objetivo'].startswith(('Tiempo', 'Time'))), PC))}\" "
          f"--campo \"recomendacion={r['recomendacion']}\" --campo estado=pendiente-decision", "```", ""]
    return "\n".join(L)

def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("analizar"); s.add_argument("cambio")
    s.add_argument("--actividades"); s.add_argument("--actividades-base", dest="actividades_base"); s.add_argument("--inicio"); s.add_argument("--pert")
    s.add_argument("--confianza", type=float, default=2.0, help="k de la reserva de cronograma (k·σ del camino crítico; por defecto 2, como cpm.py)")
    s.add_argument("--flujos"); s.add_argument("--opcion"); s.add_argument("--base"); s.add_argument("--tasa", type=float); s.add_argument("--variacion", type=float, default=0.10)
    s.add_argument("--refs"); s.add_argument("--paquetes"); s.add_argument("--puntos", type=float); s.add_argument("--release"); s.add_argument("--liberar")
    s.add_argument("--etapa", action="store_true", help="el release cierra la etapa actual: el atraso se mide contra la tolerancia de tiempo de la etapa")
    s.add_argument("--evm"); s.add_argument("--costo", type=float); s.add_argument("--cargo", choices=[x for x in E.REGISTROS["cambios"]["valores"]["cargo"] if x])
    s.add_argument("--tol-dias", type=float, dest="tol_dias"); s.add_argument("--fecha"); s.add_argument("--salida"); s.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.proyecto, "estado.json")): sys.exit(f"{a.proyecto}: falta estado.json / not a project folder")
    e = E.cargar_estado(a.proyecto); IDIOMA = e.get("idioma", "es")
    if a.flujos and not a.opcion: sys.exit(t("--flujos requiere --opcion (la opción con el cambio)", "--flujos needs --opcion"))
    if (a.puntos is None) != (a.release is None): sys.exit(t("--puntos y --release van juntos", "--puntos and --release go together"))
    r = analizar(a, e)
    fecha = a.fecha or datetime.date.today().isoformat()
    salida = a.salida or os.path.join(a.proyecto, "03-control", "reportes", f"{fecha}-solicitud-cambio-{a.cambio}.md")
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True); open(salida, "w", encoding="utf-8").write(markdown(r, e, fecha))
    r.pop("fila")
    if a.json: print(json.dumps({**r, "salida": salida}, ensure_ascii=False, indent=2)); return
    w = max(len(x["objetivo"]) for x in r["filas"])
    for x in r["filas"]: print(f"{x['objetivo']:{w}}  {x['antes']}  →  {x['con']}  ·  {x['lectura']}")
    print(t("Decide: ", "Decides: ") + f"{r['quien_decide']} ({r['nivel']})" + (" · " + "; ".join(r["motivos"]) if r["motivos"] else ""))
    print(t("Opciones: ", "Options: ") + ", ".join(o["opcion"] + ("" if o["aplica"] else t(" (no aplica)", " (n/a)")) for o in r["opciones"]) + t(f" · recomendación: {r['recomendacion']}", f" · recommendation: {r['recomendacion']}"))
    if r["aviso"]: print(r["aviso"])
    print(t(f"→ {salida} (borrador: la decisión la toma una persona; nada registrado)", f"→ {salida} (draft; nothing recorded)"))

if __name__ == "__main__":
    main()
