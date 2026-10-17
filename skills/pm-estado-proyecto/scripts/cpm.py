#!/usr/bin/env python3
"""Camino crítico (CPM) desde un CSV de actividades y salida Gantt en Mermaid.
Critical path (CPM) from an activities CSV, plus a Mermaid Gantt.

CSV de entrada (cabecera): id,nombre,duracion,predecesoras,recurso[,wbs]
  - wbs (opcional): código EDT/WBS del paquete (1.2.3); genera tareas resumen en MSPDI y ordena por código.
  - duracion en días laborables (decimales se redondean hacia arriba; 0 = hito);
  - predecesoras separadas por ';' (solo fin-a-comienzo); lag/adelanto explícito al final: "WP-1.1+2", "WP-1.1-3".
    Los id pueden contener guiones (WP-1.1); si el texto completo coincide con un id, no se interpreta como lag.
Uso / Usage:
  python3 cpm.py actividades.csv [--inicio 2026-11-03] [--mermaid salida.md] [--json] [--mspdi cronograma.xml --titulo "Nombre"]
Salida: ES, EF, LS, LF, holgura total y libre, camino crítico, carga por recurso (días asignados), Gantt Mermaid.
Limitación: sin nivelación de recursos; para FS/SS/FF/SF, calendarios y nivelación exportar MSPDI (--mspdi) y completar en MS Project o ProjectLibre (ver pm-cronograma-estimacion).
"""
import argparse, csv, json, sys, datetime, re, math

def cargar(p):
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
        dur = float(row["duracion"] or 0)
        acts[row["id"].strip()] = {"id": row["id"].strip(), "nombre": row.get("nombre", ""), "dur": int(math.ceil(dur)),
                                   "dur_original": dur, "preds": preds, "recurso": row.get("recurso", ""),
                                   "hito": dur == 0, "wbs": (row.get("wbs") or "").strip()}
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--inicio", default=datetime.date.today().isoformat())
    ap.add_argument("--mermaid"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--mspdi", help="exportar MS Project XML (MSPDI) a esta ruta"); ap.add_argument("--titulo", default="Proyecto")
    ap.add_argument("--wbs", help="wbs.csv (codigo,nombre,…) para nombrar las tareas resumen del MSPDI")
    a = ap.parse_args()
    acts = cargar(a.csv); orden, fin = cpm(acts)
    inicio = datetime.date.fromisoformat(a.inicio)
    carga = {}
    for x in acts.values():
        if x["recurso"]: carga[x["recurso"]] = carga.get(x["recurso"], 0) + x["dur"]
    criticas = [i for i in orden if acts[i]["critica"]]
    if a.json:
        print(json.dumps({"duracion_total": fin, "camino_critico": criticas, "actividades": list(acts.values()), "carga_recursos": carga}, ensure_ascii=False, indent=2))
    else:
        print(f"Duración total (días laborables): {fin}  · Fin previsto: {dias_laborables(inicio, fin).isoformat()}")
        print(f"Camino crítico: {' -> '.join(criticas)}")
        w = max(6, max(len(i) for i in orden))
        print(f"{'id':{w}} {'dur':>4} {'ES':>4} {'EF':>4} {'LS':>4} {'LF':>4} {'HT':>4} {'HL':>4}  nombre   (HT holgura total, HL libre, * crítica)")
        for i in orden:
            x = acts[i]; print(f"{i:{w}} {x['dur']:4} {x['ES']:4} {x['EF']:4} {x['LS']:4} {x['LF']:4} {x['holgura']:4} {x['holgura_libre']:4}  {x['nombre']}{' [hito]' if x['hito'] else ''}{'  *' if x['critica'] else ''}")
        print("Carga por recurso (días):", carga)
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
        lines.append("```")
        open(a.mermaid, "w", encoding="utf-8").write("\n".join(lines) + "\n"); print(f"Gantt escrito en {a.mermaid}")
    if a.mspdi:
        nombres = {r["codigo"].strip(): r["nombre"].strip() for r in csv.DictReader(open(a.wbs, encoding="utf-8"))} if a.wbs else None
        exportar_mspdi(acts, orden, inicio, a.mspdi, a.titulo, nombres); print(f"MSPDI escrito en {a.mspdi}")

if __name__ == "__main__":
    main()
