"""Guía E2E-2 · Alcance y su cambio, estimación de esfuerzo, priorización y mapa de ruta (scripts reales)."""
from comun import *
import math
repo = proyecto("portal-socios"); print("REPO", repo)
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))
WBS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wbs.csv"), encoding="utf-8").read()

P("Paso 1 · Proyecto, especificación y enunciado de alcance")
base_su(repo)
run(E(f'especificacion.py --proyecto {G} resumen'), repo)
run(E(f'especificacion.py --proyecto {G} listar epicas'), repo)
art(repo, "enunciado-alcance", "01-inicio/enunciado-alcance.md")
art(repo, "plan-gestion-alcance-requisitos", "02-planificacion/enfoques/plan-gestion-alcance-requisitos.md")

P("Paso 2 · Estructura de productos (PBS) y WBS con diccionario, trazada a requisitos e historias")
escribir(repo, "02-planificacion/wbs.csv", WBS)
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/visuales/wbs.md --diccionario {G}/02-planificacion/diccionario-wbs.md'), repo)
run(f'python3 {BMAD} --proyecto {G} trazabilidad --wbs 02-planificacion/wbs.csv', repo)
run(E(f'especificacion.py --proyecto {G} listar requisitos --cobertura sin-cobertura'), repo)
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1, 2))

P("Paso 3 · Estimación de esfuerzo: PERT de tres puntos por actividad y reserva de cronograma")
acts = [  # id, nombre, O, M, P, predecesoras, recurso, wbs
 ("A01", "Brief PRD UX y arquitectura (BMAD)", 8, 10, 15, "", "PO + arquitecto", "2.1"),
 ("A02", "Spike de integración con el núcleo", 5, 8, 14, "", "Proveedor", "3.2"),
 ("A03", "Sprints acceso seguro", 20, 28, 40, "A01", "Proveedor", "3.1"),
 ("A04", "Sprints consulta y constancias", 18, 25, 38, "A02;A03", "Proveedor", "3.2"),
 ("A05", "Sprints consola de operador", 20, 28, 42, "A03", "Proveedor", "4.1"),
 ("A06", "Release 1 aceptada", 0, 0, 0, "A04;A05", "Usuario sénior", "3.2"),
 ("A07", "Sprints solicitudes del socio", 22, 30, 45, "A06", "Proveedor", "3.3"),
 ("A08", "UAT prueba de carga y capacitación", 8, 10, 16, "A07", "Usuario sénior", "5.1"),
 ("A09", "Puesta en producción", 0, 0, 0, "A08", "Usuario sénior", "5.2"),
]
lineas = ["id,nombre,optimista,mas_probable,pesimista,tE,sigma"]; acsv = ["id,nombre,duracion,predecesoras,recurso,wbs"]
for i, n, o, m, p, pre, rec, w in acts:
    te = (o + 4 * m + p) / 6; sg = (p - o) / 6
    lineas.append(f"{i},{n},{o},{m},{p},{te:.1f},{sg:.2f}"); acsv.append(f"{i},{n},{round(te)},{pre},{rec},{w}")
escribir(repo, "02-planificacion/estimacion-pert.csv", "\n".join(lineas) + "\n")
escribir(repo, "02-planificacion/actividades.csv", "\n".join(acsv) + "\n")
LOG.append(("(estimacion-pert.csv que calcula pm-cronograma-estimacion: tE=(O+4M+P)/6, σ=(P−O)/6)", "\n".join(lineas)))
cp = run(E(f'cpm.py {G}/02-planificacion/actividades.csv --inicio 2026-11-30 --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/cronograma.md --mspdi {G}/02-planificacion/cronograma.xml --wbs {G}/02-planificacion/wbs.csv'), repo)
crit = [l.split()[0] for l in cp.split("\n") if "crít" in l.lower() and l[:3].startswith("A")]
sig = {a[0]: (a[4] - a[2]) / 6 for a in acts}
LOG.append(("(σ del camino crítico = √Σσ² de las actividades críticas; reserva a 2σ)", ""))

P("Paso 4 · Priorización del backlog: MoSCoW, valor y esfuerzo en puntos")
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
pb = os.path.join(repo, G, "02-planificacion/backlog.csv")
gob = {"1-1": ("Must", 9, 8, "S1", "R1", "3.1"), "1-2": ("Must", 6, 5, "S3", "R1", "3.1"), "1-3": ("Must", 10, 8, "S2", "R1", "3.2"),
       "1-4": ("Should", 7, 5, "S6", "R1", "3.2"), "3-1": ("Must", 6, 5, "S3", "R1", "4.1"), "3-2": ("Must", 8, 8, "S4", "R1", "4.1"),
       "3-3": ("Must", 8, 8, "S5", "R1", "4.1"), "2-1": ("Must", 9, 8, "S7", "R2", "3.3"), "2-2": ("Should", 6, 8, "S8", "R2", "3.3"),
       "2-3": ("Could", 4, 5, "S9", "R2", "3.3")}
filas = list(csv.DictReader(open(pb, encoding="utf-8"))); cab = list(filas[0].keys())
orden = sorted(filas, key=lambda f: ({"Must": 0, "Should": 1, "Could": 2}[gob[f["id"][:3]][0]], -gob[f["id"][:3]][1] / gob[f["id"][:3]][2]))
tabla = []
for n, f in enumerate(orden, 1):
    mo, val, pts, it, rel, pbs = gob[f["id"][:3]]
    f.update(prioridad=str(n), moscow=mo, estimacion=str(pts), iteracion=it, release=rel, producto_pbs=pbs)
    tabla.append(f"{n:>2} {f['id'][:44]:46s} {mo:6s} valor {val:>2} · {pts:>2} pts · valor/pts {val/pts:4.2f} · {it} {rel}")
escribir_csv(pb, cab, orden)
LOG.append(("(backlog.csv: columnas de gobierno completadas por el PO con pm-agil-hibrido; orden = MoSCoW y luego valor/puntos)", "\n".join(tabla)))
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
tot = {}
for f in orden: tot.setdefault((f["release"], f["moscow"]), 0); tot[(f["release"], f["moscow"])] += int(f["estimacion"])
LOG.append(("(capacidad del release plan: velocidad 8 × iteraciones; Σ Must+Should ≤ capacidad)", "\n".join(f"{k[0]} {k[1]:6s} {v:>3} pts" for k, v in sorted(tot.items())) + "\nR1: 6 sprints × 8 = 48 pts de capacidad (Must+Should = 47) · R2: 3 sprints × 8 = 24 pts (Must+Should = 16; con Could = 21)"))
art(repo, "backlog", "02-planificacion/backlog.csv"); art(repo, "release-plan", "02-planificacion/release-plan.md")

P("Paso 5 · Presupuesto desde la WBS, línea base de alcance y puerta autorizar-proyecto")
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --json --profundidad 1'), repo, corte=40)
for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
    art(repo, c, r)
puerta(repo, "autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")
art(repo, "business-case", "00-direccion/business-case.md", texto="# Business case\n\nB-01 desvío de consultas (SM-2); B-02 adopción (SM-1).\n")
art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia; Should/Could los intercambia el PO" "riesgo=ningún riesgo alto sin respuesta"'), repo)
puerta(repo, "autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.0 --por "Ejecutivo: Laura Méndez"', repo)
run(E(f'estado.py --proyecto {G} aprobar backlog --por "Product owner: Sofía Ramírez" --nivel product-owner --version 1.0 --fecha 2026-11-27'), repo)
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26'), repo, mostrar=False)
art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
puerta(repo, "autorizar-etapa", "Ejecutivo: Laura Méndez", "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=±10 %" "costo=±10 %"')

P("Paso 6 · Cambio menor: intercambio de Should/Could por el PO (sin solicitud de cambio)")
reg(repo, "decisiones", fecha="2027-01-08", decision="Intercambio: 1-4 constancias PDF (Should) pasa a R2 y 2-3 contacto (Could) a R1 por pedido de cumplimiento; sin tocar Must, fecha ni costo", decidido_por="Product owner: Sofía Ramírez", nivel="product-owner", artefactos_afectados="02-planificacion/backlog.csv")
filas = list(csv.DictReader(open(pb, encoding="utf-8")))
for f in filas:
    if f["id"].startswith("1-4"): f.update(release="R2", iteracion="S9")
    if f["id"].startswith("2-3"): f.update(release="R1", iteracion="S6")
escribir_csv(pb, cab, filas)
run(f'python3 {BMAD} --proyecto {G} handoff', repo)

P("Paso 7 · Cambio de alcance: nueva funcionalidad → análisis de impacto (WBS, esfuerzo, cronograma, costo) → decisión")
prd = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(repo, "_bmad-output")) for f in fs if f == "prd.md"][0]
t = open(prd, encoding="utf-8").read().replace("#### FR-11: Roles y permisos", "#### FR-13: Simulador de préstamo\n\nEl socio puede simular cuota y costo total antes de solicitar un préstamo. Realiza UJ-2.\n\n#### FR-11: Roles y permisos", 1)
open(prd, "w", encoding="utf-8").write(t)
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
I1 = reg(repo, "issues", fecha="2027-01-15", tipo="solicitud-cambio", titulo="Agregar FR-13 simulador de préstamo", descripcion="Pedido del Consejo; detectado como desvío del PRD contra la línea base 1.0", prioridad="alta", severidad="mayor", responsable="Martín Suárez")
acts2 = acts[:7] + [("A10", "Sprint simulador de préstamo (FR-13)", 8, 10, 16, "A07", "Proveedor", "3.4")] + [("A08", "UAT prueba de carga y capacitación", 8, 10, 16, "A07;A10", "Usuario sénior", "5.1"), acts[8]]
acsv2 = ["id,nombre,duracion,predecesoras,recurso,wbs"] + [f"{i},{n},{round((o+4*m+p)/6)},{pre},{rec},{w}" for i, n, o, m, p, pre, rec, w in acts2]
escribir(repo, "02-planificacion/escenarios/actividades-C-001.csv", "\n".join(acsv2) + "\n")
run(E(f'cpm.py {G}/02-planificacion/escenarios/actividades-C-001.csv --inicio 2026-11-30 --titulo "Escenario con FR-13"'), repo)
C1 = reg(repo, "cambios", fecha="2027-01-16", solicitante="Consejo directivo (vía Laura Méndez)", titulo="FR-13 simulador de préstamo", descripcion=f"Origen {I1}", justificacion="mejora la conversión de solicitudes (SM-3)", impacto_alcance="nuevo paquete WBS 3.4 · historia 2-4 · 8 pts", impacto_tiempo="+11 días laborables en el camino crítico (fin 2027-05-03 → 2027-05-18), dentro de la tolerancia de ±3 semanas", impacto_costo="+USD 9.000", impacto_riesgo="ninguno nuevo", impacto_beneficios="refuerza B-03 (SM-3)", recomendacion="aprobar; costo contra la contingencia; FR-13 como Should en R2")
act(repo, "cambios", C1, decision="aprobado", decidido_por="Autoridad de cambio: Sofía Ramírez", fecha_decision="2027-01-18", estado="aprobado")
act(repo, "issues", I1, estado="pendiente-cambio", decision=f"tramitado como {C1}", decidido_por="Autoridad de cambio: Sofía Ramírez")
escribir(repo, "02-planificacion/wbs.csv", WBS.replace("4,Consola de operador", "3.4,Simulador de préstamo (C-001),paquete,Lucía Benítez,180,9000,FR-13\n4,Consola de operador"))
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/visuales/wbs.md --profundidad 1'), repo)
run(f'python3 {BMAD} --proyecto {G} handoff --cambio {C1}', repo)

P("Paso 8 · El equipo BMAD aplica el cambio → nuevas líneas base → roadmap actualizado")
ep = os.path.join(repo, "_bmad-output/planning-artifacts/epics.md"); t = open(ep, encoding="utf-8").read()
t = t.replace("FR12: El sistema notifica", "FR13: El socio puede simular cuota y costo total antes de solicitar un préstamo.\nFR12: El sistema notifica", 1)
t = t.replace("## Epic 3: Consola de operador\n", "### Story 2.4: Simulador de préstamo\n\nAs a socio,\nI want simular cuota y costo total,\nSo that decida antes de solicitar.\n\n**Acceptance Criteria:**\n\n**Given** un producto habilitado\n**When** ingreso monto y plazo\n**Then** veo cuota y costo total (FR-13).\n\n## Epic 3: Consola de operador\n", 1)
open(ep, "w", encoding="utf-8").write(t)
ss = os.path.join(repo, "_bmad-output/implementation-artifacts/sprint-status.yaml")
tt = open(ss, encoding="utf-8").read().replace("  2-3-actualización-de-datos-de-contacto-con-verificación: backlog", "  2-3-actualización-de-datos-de-contacto-con-verificación: backlog\n  2-4-simulador-de-préstamo: backlog"); open(ss, "w", encoding="utf-8").write(tt)
pw = os.path.join(repo, G, "02-planificacion/wbs.csv"); tw = open(pw, encoding="utf-8").read().replace("C-001),paquete,Lucía Benítez,180,9000,FR-13", "C-001),paquete,Lucía Benítez,180,9000,FR-13; 2-4-simulador-de-préstamo"); open(pw, "w", encoding="utf-8").write(tw)
import glob as _g
for hd in _g.glob(os.path.join(repo, G, "02-planificacion/especificacion/handoff-bmad-*.md")):
    _t = open(hd, encoding="utf-8").read().replace("estado: emitido", "estado: aplicado", 1); open(hd, "w", encoding="utf-8").write(_t)
run(f'python3 {BMAD} --proyecto {G} requisitos', repo)
run(f'python3 {BMAD} --proyecto {G} trazabilidad --wbs 02-planificacion/wbs.csv', repo)
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
filas = list(csv.DictReader(open(pb, encoding="utf-8")))
for f in filas:
    if f["id"].startswith("2-4"): f.update(prioridad="11", moscow="Should", estimacion="8", iteracion="S10", release="R2", producto_pbs="3.4")
escribir_csv(pb, cab, filas)
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.1 --por "Ejecutivo: Laura Méndez"', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.1 --por "Ejecutivo: Laura Méndez"', repo)
act(repo, "cambios", C1, estado="implementado"); act(repo, "issues", I1, estado="cerrado", fecha_cierre="2027-01-25")
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1, 2))

P("Paso 9 · Avance del alcance: EVM ágil (alcance no entregable) e informe")
ss_t = open(ss, encoding="utf-8").read()
for k in ["1-1-alta-y-acceso-del-socio-con-segundo-factor", "1-2-recuperación-de-acceso", "1-3-consulta-de-saldos-de-ahorro-y-préstamos", "3-1-acceso-y-roles-de-la-consola-de-operador"]:
    ss_t = re.sub(rf"(?m)^(\s*{re.escape(k)}:)\s*\S+", r"\1 done", ss_t)
open(ss, "w", encoding="utf-8").write(ss_t)
run(f'python3 {BMAD} --proyecto {G} avance', repo)
run(E(f'evm.py --pv 60000 --ev 52000 --ac 58000 --bac 133000 --modo agil --pct-no-must 20 --proyecto {G}'), repo)
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)
with open(sys.argv[1] if len(sys.argv) > 1 else "salida-g2.md", "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
