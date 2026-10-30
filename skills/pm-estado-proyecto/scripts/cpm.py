#!/usr/bin/env python3
"""Camino crítico (CPM) desde un CSV de actividades y salida Gantt en Mermaid; estimación de tres valores y reserva.
Critical path (CPM) from an activities CSV, plus a Mermaid Gantt; three-point estimating and schedule reserve.

CSV de entrada (cabecera): id,nombre,duracion,predecesoras,recurso[,wbs][,optimista,mas_probable,pesimista]
  - wbs (opcional): código EDT/WBS del paquete (1.2.3); genera tareas resumen en MSPDI y ordena por código.
  - duracion en días laborables (decimales se redondean hacia arriba; 0 = hito);
  - optimista, mas_probable, pesimista (opcionales, O ≤ M ≤ P): estimación de tres valores; la duración es tE redondeada
    hacia arriba (la columna duracion puede quedar vacía). --distribucion elige la fórmula declarada en el enfoque:
      beta (por defecto, PERT): tE = (O + 4M + P)/6, σ = (P − O)/6 (práctica habitual; "no determinado en la fuente");
      triangular: tE = (O + M + P)/3 (la que cita la Guía PMBOK, pmbok8-artefactos-tecnicas-anexos.md §3.7 Familia G),
                  σ de la distribución triangular √((O² + M² + P² − OM − OP − MP)/18).
    σ del camino crítico = √Σσ²; reserva de cronograma = k·σ (--confianza k, por defecto 2: ≈ 95 %; 1: ≈ 68 %).
  - predecesoras separadas por ';' (solo fin-a-comienzo); lag/adelanto explícito al final: "WP-1.1+2", "WP-1.1-3".
    Los id pueden contener guiones (WP-1.1); si el texto completo coincide con un id, no se interpreta como lag.
Uso / Usage:
  python3 cpm.py actividades.csv [--inicio 2026-11-03] [--mermaid salida.md] [--json] [--mspdi cronograma.xml --titulo "Nombre"]
                 [--distribucion beta|triangular] [--confianza 2] [--estimacion 02-planificacion/estimacion-pert.csv]
Salida: ES, EF, LS, LF, holgura total y libre, camino crítico, carga por recurso (días asignados), Gantt Mermaid; con tres
valores, además tE y σ por actividad, σ del camino crítico, reserva y fin con reserva (--estimacion escribe el archivo que
lee impacto.py --pert: id,nombre,optimista,mas_probable,pesimista,tE,sigma,distribucion).
Limitación: sin nivelación de recursos; para FS/SS/FF/SF, calendarios y nivelación exportar MSPDI (--mspdi) y completar en MS Project o ProjectLibre (ver pm-cronograma-estimacion).
"""
import argparse, csv, json, os, sys, datetime, re, math

TRES = ("optimista", "mas_probable", "pesimista")
DISTRIBUCIONES = {"beta": "beta-PERT: tE = (O + 4M + P)/6, σ = (P − O)/6 (práctica habitual; la Guía PMBOK cita la triangular)",
                  "triangular": "triangular: tE = (O + M + P)/3 (Guía PMBOK), σ = √((O² + M² + P² − OM − OP − MP)/18)"}

def tres_valores(o, m, p, distribucion="beta"):
    """tE y σ de una estimación de tres valores (O ≤ M ≤ P) con la distribución declarada (ver el docstring del módulo).
    La comparten cpm.py e impacto.py (pm-issues-cambios)."""
    if distribucion == "triangular":
        return (o + m + p) / 3, math.sqrt(max(o * o + m * m + p * p - o * m - o * p - m * p, 0.0) / 18)
    return (o + 4 * m + p) / 6, (p - o) / 6

def sigma_camino(sigmas):
    """σ de un camino = √Σσ² de sus actividades (independientes)."""
    return math.sqrt(sum(x * x for x in sigmas))

def dias(x):
    """Días enteros de una duración decimal: hacia arriba (2,3 → 3), tolerando el error de coma flotante."""
    return int(math.ceil(round(x, 6)))

def cargar(p, distribucion="beta"):
    if not os.path.isfile(p): sys.exit(f"No existe el archivo / file not found: {p}")
    filas = list(csv.DictReader(open(p, encoding="utf-8")))
    ids = {r["id"].strip() for r in filas}
    acts = {}
    for row in filas:
        preds = []
        for tk in (row.get("predecesoras") or "").split(";"):
            tk = tk.strip()
            if not tk: continue
            if tk in ids:                      # id exacto (admite guiones: WP-1.1, A-01)
                preds.append((tk, 0)); continue
            m = re.match(r"^(.+?)([+-]\d+)d?$", tk)   # lag/lead explícito al final: "WP-1.1+2", "A-01-3"
            if not m or m.group(1).strip() not in ids:
                sys.exit(f"Predecesora inexistente o mal escrita: '{tk}' (en {row['id']}). Lags: id+N / id-N")
            preds.append((m.group(1).strip(), int(m.group(2) or 0)))
        i = row["id"].strip(); tres = te = sg = None
        vals = [(row.get(k) or "").strip() for k in TRES]
        if any(vals):
            try: o, mp, pe = (float(v.replace(",", ".")) for v in vals)
            except ValueError: sys.exit(f"{i}: optimista, mas_probable y pesimista deben ser números / three-point values must be numbers: {vals}")
            if not 0 <= o <= mp <= pe: sys.exit(f"{i}: se requiere 0 ≤ O ≤ M ≤ P / three-point values must satisfy 0 ≤ O ≤ M ≤ P: {o}, {mp}, {pe}")
            tres = (o, mp, pe); te, sg = tres_valores(o, mp, pe, distribucion)
            d0 = (row.get("duracion") or "").strip()
            if d0 and dias(float(d0)) != dias(te):
                print(f"Aviso: {i} trae duracion {d0} y tres valores; se usa tE = {te:.2f} / {i}: duration replaced by tE", file=sys.stderr)
            dur = te
        else:
            dur = float(row["duracion"] or 0)
        acts[i] = {"id": i, "nombre": row.get("nombre", ""), "dur": dias(dur),
                   "dur_original": dur, "preds": preds, "recurso": row.get("recurso", ""),
                   "hito": dias(dur) == 0, "wbs": (row.get("wbs") or "").strip(), "tres": tres, "tE": te, "sigma": sg}
    return acts

def cpm(acts):
    orden = []; visit = {}
    def visitar(i):
        if visit.get(i) == 1: sys.exit(f"Ciclo detectado en {i}")
        if visit.get(i) == 2: return
        visit[i] = 1
        for p, _ in acts[i]["preds"]:
            if p not in acts: sys.exit(f"Predecesora inexistente: {p} (en {i})")
            visitar(p)
        visit[i] = 2; orden.append(i)
    for i in acts: visitar(i)
    for i in orden:
        a = acts[i]; a["ES"] = max([acts[p]["EF"] + lag for p, lag in a["preds"]] or [0]); a["EF"] = a["ES"] + a["dur"]
    fin = max(a["EF"] for a in acts.values())
    for i in reversed(orden):
        a = acts[i]
        sucesores = [(s, lag) for s in acts for p, lag in acts[s]["preds"] if p == i]
        a["LF"] = min([acts[s]["LS"] - lag for s, lag in sucesores] or [fin]); a["LS"] = a["LF"] - a["dur"]
        a["holgura"] = a["LS"] - a["ES"]; a["critica"] = a["holgura"] == 0
    for i in orden:   # holgura libre: cuánto puede retrasarse sin mover el inicio temprano de ninguna sucesora
        a = acts[i]
        suc = [acts[s]["ES"] - lag - a["EF"] for s in acts for p, lag in acts[s]["preds"] if p == i]
        a["holgura_libre"] = min(suc) if suc else fin - a["EF"]
    return orden, fin

def dias_laborables(inicio, offset):
    d = inicio; n = 0
    while n < offset:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5: n += 1
    return d

def _x(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))

def exportar_mspdi(acts, orden, inicio, salida, titulo="Proyecto", nombres_wbs=None):
    """Escribe MS Project XML (MSPDI): calendario estándar L–V 8 h, tareas (con resumen por código WBS si existe),
    vínculos fin-a-comienzo con lag (LinkLag en décimas de minuto: 1 día = 8 h = 4800), recursos y asignaciones.
    Importable en MS Project y herramientas que leen MSPDI (p. ej. ProjectLibre, MPXJ)."""
    H = 8
    def ini(off): return dias_laborables(inicio, off).isoformat() + "T08:00:00"
    def fin(a):
        if a["hito"]: return ini(a["ES"])
        return dias_laborables(inicio, a["EF"] - 1).isoformat() + "T17:00:00"
    # orden por WBS si existe, si no por orden topológico
    hojas = sorted(acts.values(), key=lambda a: ([int(x) if x.isdigit() else x for x in a["wbs"].split(".")] if a["wbs"] else [], orden.index(a["id"])))
    filas, uid = [], 0
    resumen = {}
    if any(a["wbs"] for a in hojas):
        codigos = set()
        for a in hojas:
            partes = a["wbs"].split(".") if a["wbs"] else []
            for i in range(1, len(partes)): codigos.add(".".join(partes[:i]))
        for c in codigos:
            hijos = [a for a in hojas if a["wbs"].startswith(c + ".")]
            resumen[c] = {"wbs": c, "ES": min(h["ES"] for h in hijos), "EF": max(h["EF"] for h in hijos)}
    vistos = set(); uid_de = {}
    for a in hojas:
        partes = a["wbs"].split(".") if a["wbs"] else []
        for i in range(1, len(partes)):
            c = ".".join(partes[:i])
            if c in vistos: continue
            vistos.add(c); uid += 1; r = resumen[c]
            filas.append({"uid": uid, "nombre": (nombres_wbs or {}).get(c, c), "wbs": c, "nivel": i, "resumen": True, "hito": False,
                          "start": ini(r["ES"]), "finish": dias_laborables(inicio, max(r["EF"] - 1, r["ES"])).isoformat() + "T17:00:00",  # resumen solo de hitos: fin = inicio
                          "dur": r["EF"] - r["ES"], "preds": [], "recurso": ""})
        uid += 1; uid_de[a["id"]] = uid
        filas.append({"uid": uid, "nombre": a["nombre"] or a["id"], "wbs": a["wbs"] or a["id"], "nivel": max(len(partes), 1),
                      "resumen": False, "hito": a["hito"], "start": ini(a["ES"]), "finish": fin(a), "dur": a["dur"],
                      "preds": a["preds"], "recurso": a["recurso"], "id": a["id"], "critica": a["critica"], "holgura": a["holgura"]})
    recursos = sorted({f["recurso"] for f in filas if f["recurso"]})
    L = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
         '<Project xmlns="http://schemas.microsoft.com/project">',
         '  <SaveVersion>14</SaveVersion>', f'  <Name>{_x(titulo)}</Name>', f'  <Title>{_x(titulo)}</Title>',
         '  <ScheduleFromStart>1</ScheduleFromStart>', f'  <StartDate>{ini(0)}</StartDate>',
         '  <MinutesPerDay>480</MinutesPerDay>', '  <MinutesPerWeek>2400</MinutesPerWeek>', '  <DaysPerMonth>20</DaysPerMonth>',
         '  <CalendarUID>1</CalendarUID>',
         '  <Calendars>', '    <Calendar>', '      <UID>1</UID>', '      <Name>Estandar</Name>', '      <IsBaseCalendar>1</IsBaseCalendar>',
         '      <WeekDays>']
    for d in range(1, 8):   # 1 = domingo … 7 = sábado
        if d in (1, 7):
            L += ['        <WeekDay>', f'          <DayType>{d}</DayType>', '          <DayWorking>0</DayWorking>', '        </WeekDay>']
        else:
            L += ['        <WeekDay>', f'          <DayType>{d}</DayType>', '          <DayWorking>1</DayWorking>', '          <WorkingTimes>',
                  '            <WorkingTime><FromTime>08:00:00</FromTime><ToTime>12:00:00</ToTime></WorkingTime>',
                  '            <WorkingTime><FromTime>13:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime>',
                  '          </WorkingTimes>', '        </WeekDay>']
    L += ['      </WeekDays>', '    </Calendar>', '  </Calendars>', '  <Tasks>']
    for i, f in enumerate(filas, 1):
        L += ['    <Task>', f'      <UID>{f["uid"]}</UID>', f'      <ID>{i}</ID>', f'      <Name>{_x(f["nombre"])}</Name>',
              f'      <WBS>{_x(f["wbs"])}</WBS>', f'      <OutlineNumber>{_x(f["wbs"])}</OutlineNumber>', f'      <OutlineLevel>{f["nivel"]}</OutlineLevel>',
              f'      <Summary>{1 if f["resumen"] else 0}</Summary>', f'      <Milestone>{1 if f["hito"] else 0}</Milestone>',
              f'      <Start>{f["start"]}</Start>', f'      <Finish>{f["finish"]}</Finish>',
              f'      <Duration>PT{f["dur"] * H}H0M0S</Duration>', '      <DurationFormat>7</DurationFormat>',
              '      <ConstraintType>0</ConstraintType>', '      <CalendarUID>-1</CalendarUID>']
        if not f["resumen"]:
            L.append(f'      <Critical>{1 if f.get("critica") else 0}</Critical>')
            L.append(f'      <TotalSlack>{f.get("holgura", 0) * 480 * 10}</TotalSlack>')
        for p, lag in f["preds"]:
            L += ['      <PredecessorLink>', f'        <PredecessorUID>{uid_de[p]}</PredecessorUID>', '        <Type>1</Type>',
                  f'        <LinkLag>{lag * 4800}</LinkLag>', '        <LagFormat>7</LagFormat>', '      </PredecessorLink>']
        L.append('    </Task>')
    L += ['  </Tasks>', '  <Resources>']
    for j, r in enumerate(recursos, 1):
        L += ['    <Resource>', f'      <UID>{j}</UID>', f'      <ID>{j}</ID>', f'      <Name>{_x(r)}</Name>', '      <Type>1</Type>', '    </Resource>']
    L += ['  </Resources>', '  <Assignments>']
    k = 0
    for f in filas:
        if f["recurso"] and not f["resumen"]:
            k += 1
            L += ['    <Assignment>', f'      <UID>{k}</UID>', f'      <TaskUID>{f["uid"]}</TaskUID>',
                  f'      <ResourceUID>{recursos.index(f["recurso"]) + 1}</ResourceUID>', '      <Units>1</Units>',
                  f'      <Work>PT{f["dur"] * H}H0M0S</Work>', f'      <Start>{f["start"]}</Start>', f'      <Finish>{f["finish"]}</Finish>',
                  '    </Assignment>']
    L += ['  </Assignments>', '</Project>']
    open(salida, "w", encoding="utf-8").write("\n".join(L) + "\n")

def coma(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")

def estimacion(acts, criticas, inicio, fin, distribucion, k):
    """Bloque de tres valores: tE y σ por actividad, σ del camino crítico, reserva k·σ y fin con reserva (None sin tres valores)."""
    tv = [a for a in acts.values() if a["tres"]]
    if not tv: return None
    sig = [acts[i]["sigma"] for i in criticas if acts[i]["sigma"]]
    sc = sigma_camino(sig); res = k * sc
    rd = dias(round(res, 1))      # la reserva entra al cronograma en días enteros, desde su valor con un decimal
    sin = [i for i in criticas if not acts[i]["tres"] and not acts[i]["hito"]]
    return {"distribucion": distribucion, "formula": DISTRIBUCIONES[distribucion], "confianza": k, "sigmas_camino": sig,
            "sigma_camino": sc, "reserva": res, "reserva_dias": rd, "fin_con_reserva": dias_laborables(inicio, fin + rd).isoformat(),
            "criticas_sin_tres_valores": sin,
            "actividades": [{"id": a["id"], "nombre": a["nombre"], "optimista": a["tres"][0], "mas_probable": a["tres"][1], "pesimista": a["tres"][2],
                             "tE": a["tE"], "sigma": a["sigma"], "critica": a["critica"]} for a in tv]}

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("csv"); ap.add_argument("--inicio", default=datetime.date.today().isoformat())
    ap.add_argument("--mermaid"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--mspdi", help="exportar MS Project XML (MSPDI) a esta ruta"); ap.add_argument("--titulo", default="Proyecto")
    ap.add_argument("--wbs", help="wbs.csv (codigo,nombre,…) para nombrar las tareas resumen del MSPDI")
    ap.add_argument("--distribucion", choices=list(DISTRIBUCIONES), default="beta", help="fórmula de tres valores declarada en el enfoque (por defecto beta-PERT)")
    ap.add_argument("--confianza", type=float, default=2.0, help="k de la reserva de cronograma k·σ del camino crítico (por defecto 2)")
    ap.add_argument("--estimacion", help="escribir tE y σ por actividad en este CSV (el que lee impacto.py --pert)")
    a = ap.parse_args()
    if a.confianza <= 0: sys.exit("--confianza debe ser mayor que 0 / must be > 0")
    acts = cargar(a.csv, a.distribucion); orden, fin = cpm(acts)
    inicio = datetime.date.fromisoformat(a.inicio)
    carga = {}
    for x in acts.values():
        if x["recurso"]: carga[x["recurso"]] = carga.get(x["recurso"], 0) + x["dur"]
    criticas = [i for i in orden if acts[i]["critica"]]
    est = estimacion(acts, criticas, inicio, fin, a.distribucion, a.confianza)
    if a.estimacion and not est: sys.exit("--estimacion requiere columnas optimista, mas_probable y pesimista en el CSV / needs three-point columns")
    k = f"{a.confianza:g}".replace(".", ",") + "σ"
    if a.json:
        print(json.dumps({"duracion_total": fin, "camino_critico": criticas, "actividades": list(acts.values()), "carga_recursos": carga,
                          **({"estimacion": est} if est else {})}, ensure_ascii=False, indent=2))
    else:
        print(f"Duración total (días laborables): {fin}  · Fin previsto: {dias_laborables(inicio, fin).isoformat()}")
        print(f"Camino crítico: {' -> '.join(criticas)}")
        w = max(6, max(len(i) for i in orden))
        print(f"{'id':{w}} {'dur':>4} {'ES':>4} {'EF':>4} {'LS':>4} {'LF':>4} {'HT':>4} {'HL':>4}  nombre   (HT holgura total, HL libre, * crítica)")
        for i in orden:
            x = acts[i]; print(f"{i:{w}} {x['dur']:4} {x['ES']:4} {x['EF']:4} {x['LS']:4} {x['LF']:4} {x['holgura']:4} {x['holgura_libre']:4}  {x['nombre']}{' [hito]' if x['hito'] else ''}{'  *' if x['critica'] else ''}")
        print("Carga por recurso (días):", carga)
        if est:
            print(f"Tres valores · {est['formula']}; duración = tE redondeada hacia arriba")
            print(f"{'id':{w}} {'O':>5} {'M':>5} {'P':>5} {'tE':>6} {'σ':>5}")
            for x in est["actividades"][:40]:
                print(f"{x['id']:{w}} {x['optimista']:5g} {x['mas_probable']:5g} {x['pesimista']:5g} {coma(x['tE']):>6} {coma(x['sigma']):>5}{'  *' if x['critica'] else ''}")
            if len(est["actividades"]) > 40: print(f"… y {len(est['actividades']) - 40} más (ver --json o --estimacion)")
            print(f"σ del camino crítico = √({' + '.join(coma(x) + '²' for x in est['sigmas_camino']) or '0'}) = {coma(est['sigma_camino'])} días")
            conf = {1.0: " (≈ 68 %)", 2.0: " (≈ 95 %)"}.get(a.confianza, "")
            print(f"Reserva de cronograma a {k} = {coma(est['reserva'], 1)} días laborables{conf} · fin con reserva {est['fin_con_reserva']} (+{est['reserva_dias']})")
            if est["criticas_sin_tres_valores"]:
                print(f"Aviso: actividades críticas sin tres valores (σ = 0): {', '.join(est['criticas_sin_tres_valores'][:8])}")
    if a.estimacion:
        os.makedirs(os.path.dirname(os.path.abspath(a.estimacion)), exist_ok=True)
        with open(a.estimacion, "w", encoding="utf-8", newline="") as fh:
            wr = csv.writer(fh, lineterminator="\n"); wr.writerow(["id", "nombre", "optimista", "mas_probable", "pesimista", "tE", "sigma", "distribucion"])
            for x in est["actividades"]:
                wr.writerow([x["id"], x["nombre"], f"{x['optimista']:g}", f"{x['mas_probable']:g}", f"{x['pesimista']:g}", f"{x['tE']:.2f}", f"{x['sigma']:.2f}", a.distribucion])
        if not a.json: print(f"Estimación escrita en {a.estimacion} (la lee impacto.py --pert)")
    if a.mermaid:
        lines = ["```mermaid", "gantt", "    dateFormat YYYY-MM-DD", f"    title {a.titulo if a.titulo != 'Proyecto' else 'Cronograma (CPM)'}", "    excludes weekends"]
        for i in orden:
            x = acts[i]; s = dias_laborables(inicio, x["ES"])
            nombre = re.sub(r"[:;#]", " ", x["nombre"] or i).strip()
            mid = re.sub(r"[^A-Za-z0-9_]", "_", i)
            tags = (["milestone"] if x["hito"] else []) + (["crit"] if x["critica"] else [])
            tag = ", ".join(tags) + ", " if tags else ""
            dur = "0d" if x["hito"] else f"{x['dur']}d"
            lines.append(f"    {nombre} :{tag}{mid}, {s.isoformat()}, {dur}")
        if est and est["reserva_dias"]:
            lines += ["    section Reserva", f"    Reserva de cronograma {k} :reserva_cronograma, {dias_laborables(inicio, fin).isoformat()}, {est['reserva_dias']}d"]
        lines.append("```")
        open(a.mermaid, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        if not a.json: print(f"Gantt escrito en {a.mermaid}")
    if a.mspdi:
        nombres = {r["codigo"].strip(): r["nombre"].strip() for r in csv.DictReader(open(a.wbs, encoding="utf-8"))} if a.wbs else None
        exportar_mspdi(acts, orden, inicio, a.mspdi, a.titulo, nombres)
        if not a.json: print(f"MSPDI escrito en {a.mspdi}")

if __name__ == "__main__":
    try: import esquema; esquema.salida_utf8()        # salida UTF-8 en consolas cp1252 (docs/ARQUITECTURA.md §9.4)
    except ImportError: pass
    main()
