"""Guía E2E-4 · Producto de la idea al producto con BMAD dentro de un proyecto PRINCE2 (evidencia con scripts)."""
from comun import *
import yaml
repo = proyecto("portal-socios"); print("REPO", repo)
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))

P("Paso 1 · Proyecto y detección de BMAD")
run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez"'), repo)
run(f'python3 {BMAD} --proyecto {G} detectar', repo)
run(E(f'estado.py --proyecto {G} integracion especificacion=bmad'), repo)

P("Paso 2 · Idea → brief de producto (BMAD) → mandato y project brief (pm-method)")
run(f'python3 {BMAD} --proyecto {G} inventario', repo)
run(E(f'especificacion.py --proyecto {G} fuente'), repo)
art(repo, "mandato", "00-direccion/mandato.md")
art(repo, "project-brief", "01-inicio/project-brief.md", texto="# Project brief\n\nProducto: ver brief de BMAD (_bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md, sha 58db1efac463).\n")
reg(repo, "decisiones", fecha="2026-10-20", decision="Enfoque híbrido: etapas PRINCE2; especificación con BMAD; sprints de 14 días como paquetes", decidido_por="Ejecutivo: Laura Méndez", nivel="junta")

P("Paso 3 · Junta, tolerancias, business case esquemático y puerta autorizar-inicio")
run(E(f'estado.py --proyecto {G} rol usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" product_owner="Sofía Ramírez" autoridad_cambio="Sofía Ramírez" aseguramiento="Andrea Costa" jefes_equipo="Lucía Benítez"'), repo)
run(E(f'estado.py --proyecto {G} agil cadencia_iteracion_dias=14 velocidad_referencia=8'), repo)
art(repo, "business-case-esquematico", "00-direccion/business-case-esquematico.md")
art(repo, "plan-etapa-1", "02-planificacion/plan-etapa-1.md")
puerta(repo, "autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")

P("Paso 4 · PRD, UX y arquitectura (BMAD) → requisitos en la fachada")
run(f'python3 {BMAD} --proyecto {G} requisitos', repo)
run(E(f'especificacion.py --proyecto {G} resumen'), repo)
run(E(f'especificacion.py --proyecto {G} consultar FR-6'), repo)

P("Paso 5 · Épicas e historias (BMAD) → WBS por productos y trazabilidad")
wbs = """codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref
1,Gestión del proyecto,producto,Martín Suárez,,,
1.1,Gestión de etapas,paquete,Martín Suárez,400,20000,
2,Especificación del producto,producto,Sofía Ramírez,,,
2.1,Brief PRD UX y arquitectura (BMAD),paquete,Sofía Ramírez,240,12000,UJ-1; UJ-2; UJ-3
3,Portal del socio,producto,Lucía Benítez,,,
3.1,Acceso seguro,paquete,Lucía Benítez,420,21000,FR-1; FR-2; FR-11; 1-1-alta-y-acceso-del-socio-con-segundo-factor; 1-2-recuperación-de-acceso
3.2,Consulta y constancias,paquete,Lucía Benítez,380,19000,FR-3; FR-4; FR-5; 1-3-consulta-de-saldos-de-ahorro-y-préstamos; 1-4-descarga-de-constancias-en-pdf
3.3,Solicitudes del socio,paquete,Lucía Benítez,440,22000,FR-6; FR-7; FR-8; FR-12; 2-1-solicitud-guiada-de-préstamo-simple; 2-2-seguimiento-de-solicitudes-y-respuesta-a-pedidos-de-informac; 2-3-actualización-de-datos-de-contacto-con-verificación
4,Consola de operador,producto,Lucía Benítez,,,
4.1,Bandeja y resolución,paquete,Lucía Benítez,400,20000,FR-9; FR-10; 3-1-acceso-y-roles-de-la-consola-de-operador; 3-2-bandeja-única-de-solicitudes; 3-3-resolución-de-solicitudes
5,Transición,producto,Sofía Ramírez,,,
5.1,UAT prueba de carga y capacitación,paquete,Sofía Ramírez,200,10000,NFR-2; NFR-3
5.2,Puesta en producción,hito,Sofía Ramírez,,,
"""
escribir(repo, "02-planificacion/wbs.csv", wbs)
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/visuales/wbs.md'), repo)
run(f'python3 {BMAD} --proyecto {G} trazabilidad --wbs 02-planificacion/wbs.csv', repo)
run(E(f'especificacion.py --proyecto {G} listar requisitos --cobertura sin-cobertura'), repo)

P("Paso 6 · Backlog con columnas de gobierno, MoSCoW y release plan")
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
pb = os.path.join(repo, G, "02-planificacion/backlog.csv")
gob = {"1-1": ("1","Must",8,"S1","R1","3.1"), "1-2": ("2","Must",5,"S1","R1","3.1"), "1-3": ("3","Must",8,"S2","R1","3.2"),
       "1-4": ("4","Should",5,"S2","R1","3.2"), "3-1": ("5","Must",5,"S3","R1","4.1"), "3-2": ("6","Must",8,"S3","R1","4.1"),
       "3-3": ("7","Must",8,"S4","R1","4.1"), "2-1": ("8","Must",8,"S5","R2","3.3"), "2-2": ("9","Should",8,"S6","R2","3.3"),
       "2-3": ("10","Could",5,"S6","R2","3.3")}
filas = list(csv.DictReader(open(pb, encoding="utf-8"))); cab = list(filas[0].keys())
for f in filas:
    g = gob[f["id"][:3]]
    f["prioridad"], f["moscow"], f["estimacion"], f["iteracion"], f["release"], f["producto_pbs"] = map(str, g)
escribir_csv(pb, cab, filas)
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
LOG.append(("(columnas de gobierno de backlog.csv completadas por pm-agil-hibrido: prioridad, moscow, estimacion, iteracion, release, producto_pbs)", "\n".join(f"{f['id'][:40]:42s} {f['moscow']:7s} {f['estimacion']:>3s} pts  {f['iteracion']}  {f['release']}  WBS {f['producto_pbs']}" for f in filas)))

P("Paso 7 · Business case, OKR ligados a SM-n y puerta autorizar-proyecto con línea base del PRD")
art(repo, "business-case", "00-direccion/business-case.md", texto="# Business case\n\nB-01 desvío de consultas (SM-2); B-02 adopción (SM-1); B-03 eficiencia de préstamos (SM-3).\n")
art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
okr = """id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas
O-1,objetivo,,Los socios resuelven sus gestiones simples sin ir a la sucursal,,,,,,Ejecutivo: Laura Méndez,2027-12-31,OBJ-1,,
KR-1.1,kr,O-1,30 % de socios activos registrados,% socios registrados,0,30,0,%,Usuario sénior: Sofía Ramírez,2027-12-31,B-02; SM-1,6,
KR-1.2,kr,O-1,Bajar 30 % las consultas de saldo por canales tradicionales,consultas/mes,5000,3500,5000,consultas,Usuario sénior: Sofía Ramírez,2027-12-31,B-01; SM-2,5,
KR-1.3,kr,O-1,Responder préstamos simples en menos de 48 h hábiles,horas,96,48,96,horas,Usuario sénior: Sofía Ramírez,2027-12-31,B-03; SM-3,6,
"""
escribir(repo, "00-direccion/okr.csv", okr)
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2026-11-20', repo)
run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "beneficios=-10 %" "riesgo=ningún riesgo alto sin respuesta"'), repo)
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1))
puerta(repo, "autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
run(E(f'estado.py --proyecto {G} aprobar business-case --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27'), repo)
run(E(f'estado.py --proyecto {G} aprobar pid --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27'), repo)
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.0 --por "Ejecutivo: Laura Méndez"', repo)

P("Paso 8 · Gate de preparación de BMAD y puerta autorizar-etapa (Release 1)")
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado CONCERNS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26 --nota "NFR-3 sin prueba de carga planificada"'), repo)
art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
run(E(f'estado.py --proyecto {G} tolerancia --nivel etapa "tiempo=±10 %" "costo=±10 %" "alcance=PO intercambia Should/Could"'), repo)
puerta(repo, "autorizar-etapa", "Ejecutivo: Laura Méndez", "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05', decision="condicionado")

P("Paso 9 · Sprint 1 como paquete de trabajo; construcción con BMAD; avance")
art(repo, "WP-001", "03-control/paquetes-trabajo/WP-001-sprint-1.md", estado="aprobado", version="1.0")
run(E(f'estado.py --proyecto {G} aprobar WP-001 --por "Gestor: Martín Suárez" --nivel gestor --fecha 2026-11-30'), repo)
ss = os.path.join(repo, "_bmad-output/implementation-artifacts/sprint-status.yaml")
def poner_estados(cambios):
    t = open(ss, encoding="utf-8").read()
    for k, v in cambios.items():
        t = re.sub(rf"(?m)^(\s*{re.escape(k)}:)\s*\S+", rf"\1 {v}", t)
    open(ss, "w", encoding="utf-8").write(t)
poner_estados({"epic-1": "in-progress", "1-1-alta-y-acceso-del-socio-con-segundo-factor": "done", "1-2-recuperación-de-acceso": "done", "1-3-consulta-de-saldos-de-ahorro-y-préstamos": "review"})
run(f'python3 {BMAD} --proyecto {G} avance --corte 2026-12-23', repo)
LOG.append(("(cada corte agrega una fila a 03-control/reportes/avance-bmad.csv)", ""))
run(E(f'especificacion.py --proyecto {G} resumen'), repo)

P("Paso 10 · Valor ganado ágil y highlight con puertas")
run(E(f'evm.py --pv 41000 --ev 38000 --ac 40500 --bac 124000 --modo agil --pct-no-must 20 --proyecto {G}'), repo)
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)

P("Paso 11 · Cambio de rumbo: bmad-correct-course agrega FR-13 → verificar → issue → cambio → traspaso → línea base 1.1")
prd = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(repo, "_bmad-output")) for f in fs if f == "prd.md"][0]
t = open(prd, encoding="utf-8").read()
t = t.replace("#### FR-11: Roles y permisos", "#### FR-13: Pago de cuotas de préstamo con débito en cuenta\n\nEl socio puede pagar una cuota vencida o próxima de su préstamo con débito de su cuenta de ahorro. Realiza UJ-2.\n\n#### FR-11: Roles y permisos", 1)
open(prd, "w", encoding="utf-8").write(t)
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1, 2))
i1 = reg(repo, "issues", fecha="2027-01-12", tipo="solicitud-cambio", titulo="FR-13 pago de cuotas agregado al PRD sin control de cambios", descripcion="bmad.py verificar detectó FR-13 nuevo contra la línea base PRD v1.0", prioridad="alta", severidad="mayor", responsable="Martín Suárez")
c1 = reg(repo, "cambios", fecha="2027-01-13", solicitante="Sofía Ramírez", titulo="Incorporar FR-13 pago de cuotas", descripcion=f"Origen {i1}", impacto_alcance="nueva historia 2-4 (8 puntos)", impacto_tiempo="+1 sprint en la etapa 3", impacto_costo="+USD 6.000 (contingencia)", impacto_beneficios="refuerza B-01", recomendacion="aprobar para la etapa 3; diferir FR-8 a Could")
act(repo, "cambios", c1, decision="aprobado", decidido_por="Autoridad de cambio: Sofía Ramírez", fecha_decision="2027-01-14", estado="aprobado")
act(repo, "issues", i1, estado="pendiente-cambio", decision=f"tramitado como {c1}", decidido_por="Autoridad de cambio: Sofía Ramírez")
run(f'python3 {BMAD} --proyecto {G} handoff --cambio {c1}', repo)
# el equipo BMAD aplica el traspaso con sus flujos (bmad-prd edit + bmad-create-epics-and-stories): historia 2.4 y FR13 en epics.md
ep = os.path.join(repo, "_bmad-output/planning-artifacts/epics.md"); t = open(ep, encoding="utf-8").read()
t = t.replace("FR12: El sistema notifica", "FR13: El socio puede pagar una cuota vencida o próxima de su préstamo con débito de su cuenta de ahorro.\nFR12: El sistema notifica", 1)
t = t.replace("## Epic 3: Consola de operador\n", "### Story 2.4: Pago de cuotas con débito en cuenta\n\nAs a socio,\nI want pagar una cuota de mi préstamo con débito de mi cuenta de ahorro,\nSo that no tenga que ir a la sucursal a pagar.\n\n**Acceptance Criteria:**\n\n**Given** un socio con una cuota vencida o próxima\n**When** confirma el pago\n**Then** se debita la cuenta y se notifica (FR-13).\n\n## Epic 3: Consola de operador\n", 1)
open(ep, "w", encoding="utf-8").write(t)
tt = open(ss, encoding="utf-8").read().replace("  2-3-actualización-de-datos-de-contacto-con-verificación: backlog", "  2-3-actualización-de-datos-de-contacto-con-verificación: backlog\n  2-4-pago-de-cuotas-con-débito-en-cuenta: backlog")
open(ss, "w", encoding="utf-8").write(tt)
pw = os.path.join(repo, G, "02-planificacion/wbs.csv"); tw = open(pw, encoding="utf-8").read()
tw = tw.replace("2-3-actualización-de-datos-de-contacto-con-verificación\n", "2-3-actualización-de-datos-de-contacto-con-verificación; FR-13; 2-4-pago-de-cuotas-con-débito-en-cuenta\n")
open(pw, "w", encoding="utf-8").write(tw)
run(f'python3 {BMAD} --proyecto {G} requisitos', repo)
run(f'python3 {BMAD} --proyecto {G} trazabilidad --wbs 02-planificacion/wbs.csv', repo)
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
filas = list(csv.DictReader(open(pb, encoding="utf-8"))); cab = list(filas[0].keys())
for f in filas:
    if f["id"].startswith("2-4"): f.update(prioridad="11", moscow="Should", estimacion="8", iteracion="S7", release="R2", producto_pbs="3.3")
escribir_csv(pb, cab, filas)
LOG.append(("(el PO completa las columnas de gobierno de la historia nueva 2-4: Should, 8 pts, S7, R2)", ""))
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.1 --por "Ejecutivo: Laura Méndez"', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.1 --por "Ejecutivo: Laura Méndez"', repo)
import glob as _g
hd = _g.glob(os.path.join(repo, G, "02-planificacion/especificacion/handoff-bmad-*-C-001.md"))[0]
_t = open(hd, encoding="utf-8").read().replace("estado: emitido", "estado: aplicado", 1); open(hd, "w", encoding="utf-8").write(_t)
LOG.append(("(el equipo BMAD marca el traspaso como aplicado: estado: aplicado en " + os.path.relpath(hd, repo) + ")", ""))
act(repo, "cambios", c1, estado="implementado")
act(repo, "issues", i1, estado="cerrado", fecha_cierre="2027-01-20")
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1, 2))

P("Paso 12 · Calidad por requisito, retrospectiva y lecciones")
q1 = reg(repo, "calidad", producto="FR-1 alta y acceso (historia 1-1)", metodo_verificacion="prueba", criterios="criterios de aceptación de la historia 1-1 y NFR-1", responsable_productor="Lucía Benítez", revisores="Andrea Costa", aprobador="Sofía Ramírez", fecha_prevista="2027-01-20")
act(repo, "calidad", q1, resultado="aprobado", estado="completada", fecha_real="2027-01-20")
reg(repo, "lecciones", etapa="2", categoria="especificacion", situacion="FR-13 entró al PRD por correct-course sin pasar por la autoridad de cambio", efecto="sanidad ESP-10 bloqueó la puerta hasta tramitar C-001", recomendacion="toda Sprint Change Proposal se presenta primero como issue", prioridad="alta", responsable_seguimiento="Martín Suárez")

P("Paso 13 · Fin de la etapa 2 (Release 1), informe de fin de etapa y puerta autorizar-etapa (Release 2)")
poner_estados({k: "done" for k in ["epic-1", "epic-3", "1-3-consulta-de-saldos-de-ahorro-y-préstamos", "1-4-descarga-de-constancias-en-pdf", "3-1-acceso-y-roles-de-la-consola-de-operador", "3-2-bandeja-única-de-solicitudes", "3-3-resolución-de-solicitudes"]})
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-03-05', repo)
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
av = list(csv.DictReader(open(os.path.join(repo, G, "03-control/reportes/avance-bmad.csv"), encoding="utf-8")))
it = []; prev = 0
for f in av:
    t_ = float(f["puntos_terminados"] or 0); it.append({"nombre": f["fecha"], "planificado": 16 if not it else 34, "terminado": t_ - prev, "alcance_total": float(f["puntos_total"] or 0), "terminado_acumulado": t_}); prev = t_
obj4 = [{"clave": "tiempo", "pronostico": "SPI 0,98", "tol_etapa": "±10 %", "tol_proyecto": "±3 semanas", "rag": "verde"},
        {"clave": "costo", "pronostico": "CPI 0,96 · EAC ≈ USD 135.700", "tol_etapa": "±10 %", "tol_proyecto": "±8 %", "rag": "verde"},
        {"clave": "alcance", "pronostico": "Release 1 completa; FR-13 aprobado (C-001) para R2", "tol_etapa": "PO intercambia Should/Could", "tol_proyecto": "Must sin tolerancia", "rag": "verde"},
        {"clave": "calidad", "pronostico": "Q-001 aprobada", "tol_etapa": "", "tol_proyecto": "", "rag": "verde"},
        {"clave": "beneficios", "pronostico": "medición tras el lanzamiento", "tol_etapa": "", "tol_proyecto": "-10 %", "rag": "na"},
        {"clave": "riesgo", "pronostico": "sin riesgos altos abiertos", "tol_etapa": "", "tol_proyecto": "ningún alto sin respuesta", "rag": "verde"},
        {"clave": "sostenibilidad", "pronostico": "[por confirmar]", "tol_etapa": "", "tol_proyecto": "", "rag": "na"}]
tablero(repo, "2027-03-05", "2027-02-19", "2027-03-05", "2027-03-19", obj4,
        [{"hito": "Release 1 aceptada", "base": "2027-03-05", "actual": "2027-03-05", "var_dias": 0, "rag": "verde", "comentario": "épicas 1 y 3 terminadas"},
         {"hito": "Release 2 (incluye FR-13)", "base": "2027-05-14", "actual": "2027-05-14", "var_dias": 0, "rag": "verde", "comentario": "C-001 aprobado"}],
        [{"id": "autorizar-etapa", "texto": "autorizar la etapa 3 (Release 2) con el plan y el informe de fin de etapa", "fecha_limite": "2027-03-05"}], it,
        "Release 1 entregada; el cambio FR-13 entró por control de cambios y se traspasó al equipo BMAD.",
        "estado.json; avance-bmad.csv; registros al 2027-03-05", salida_png=os.path.join(OUT, "g4-tablero.png"), fecha_fija="2027-05-14", fecha_pronostico="2027-05-14")
run(E(f'estado.py --proyecto {G} limite-etapa'), repo)
run(E(f'evm.py --pv 82000 --ev 80000 --ac 83500 --bac 130000 --proyecto {G}'), repo)
art(repo, "informe-fin-etapa-2", "03-control/reportes/2027-03-05-informe-fin-etapa-2.md")
art(repo, "plan-etapa-3", "02-planificacion/plan-etapa-3.md")
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2027-03-03'), repo)
puerta(repo, "autorizar-etapa", "Ejecutivo: Laura Méndez", "2027-03-05", '--etapa-nombre "Release 2" --fin 2027-05-14 --tol "tiempo=±10 %" "costo=±10 %"')

P("Paso 14 · Release 2, aceptación, beneficios y puerta autorizar-cierre")
poner_estados({k: "done" for k in ["epic-2", "2-1-solicitud-guiada-de-préstamo-simple", "2-2-seguimiento-de-solicitudes-y-respuesta-a-pedidos-de-informac", "2-3-actualización-de-datos-de-contacto-con-verificación", "2-4-pago-de-cuotas-con-débito-en-cuenta"]})
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-05-12', repo)
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
run(E(f'especificacion.py --proyecto {G} listar requisitos --cobertura sin-cobertura'), repo)
run(E(f'especificacion.py --proyecto {G} resumen'), repo)
run(E(f'evm.py --pv 130000 --ev 130000 --ac 133000 --bac 130000 --tol-costo 8 --tol-plazo 10'), repo)
run(E(f'estado.py --proyecto {G} cierre'), repo)
art(repo, "registro-aceptacion", "04-cierre/registro-aceptacion.md")
run(E(f'estado.py --proyecto {G} aprobar registro-aceptacion --por "Usuario sénior: Sofía Ramírez; Ejecutivo: Laura Méndez" --version 1.0 --fecha 2027-05-12'), repo)
art(repo, "informe-fin-proyecto", "04-cierre/informe-fin-proyecto.md"); art(repo, "informe-lecciones", "04-cierre/informe-lecciones.md")
art(repo, "plan-revision-beneficios", "04-cierre/plan-revision-beneficios.md")
art(repo, "recomendaciones-seguimiento", "04-cierre/recomendaciones-seguimiento.md")
okr2 = okr.replace(",30,0,%", ",30,9,%").replace(",3500,5000,", ",3500,4600,").replace(",48,96,", ",48,70,")
escribir(repo, "00-direccion/okr.csv", okr2)
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2027-06-30 --markdown {G}/03-control/reportes/2027-06-30-okr.md', repo)
puerta(repo, "autorizar-cierre", "Ejecutivo: Laura Méndez", "2027-05-14")
run(f'python3 {PAQ} --proyecto {G} cierre', repo, ok=(0, 1))
run(E(f'exportar.py xlsx --proyecto {G}'), repo, ok=(0, 1))
run(E(f'estado.py --proyecto {G} resumen'), repo)
LOG_path = sys.argv[1] if len(sys.argv) > 1 else "salida-g4.md"
with open(LOG_path, "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
