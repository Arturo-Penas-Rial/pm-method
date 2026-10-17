"""Guía E2E-1 · Ciclo completo de gestión de riesgos (producto, WBS, interesados) con scripts reales."""
from comun import *
repo = proyecto("portal-socios"); print("REPO", repo)
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))
WBS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wbs.csv"), encoding="utf-8").read()

P("Paso 1 · Proyecto, junta y objetivos con tolerancias")
base_su(repo)
run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "beneficios=-10 %" "riesgo=ningún riesgo alto sin respuesta; exposición total ≤ USD 60.000"'), repo)
run(E(f'estado.py --proyecto {G} resumen'), repo)

P("Paso 2 · Contexto del riesgo: productos y WBS, interesados y especificación")
escribir(repo, "02-planificacion/wbs.csv", WBS)
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --profundidad 1'), repo)
st = {}
for nombre, rol, pod, inte, act_, des in (("Laura Méndez", "Ejecutiva", "alto", "alto", "lider", "lider"),
                                         ("Sindicato de operadores", "Representación de operadores de sucursal", "medio", "alto", "resistente", "neutral"),
                                         ("Área de TI del núcleo operativo", "Dueña del core y del padrón", "alto", "medio", "neutral", "partidario"),
                                         ("Unidad de cumplimiento", "Protección de datos (Ley 18.331)", "alto", "medio", "neutral", "partidario")):
    st[nombre] = reg(repo, "stakeholders", nombre=nombre, rol_organizacion=rol, poder=pod, interes=inte, actitud=act_, nivel_compromiso_actual=act_, nivel_compromiso_deseado=des, confidencial="no")
run(E(f'especificacion.py --proyecto {G} listar requisitos --limite 8'), repo)
run(E(f'especificacion.py --proyecto {G} consultar AD-5'), repo)

P("Paso 3 · Escala de probabilidad e impacto (propuesta → aprobación del ejecutivo)")
run(E(f'estado.py --proyecto {G} umbrales-riesgo alto=15 medio=6'), repo)
art(repo, "evaluacion-probabilidad-impacto", "02-planificacion/enfoques/evaluacion-probabilidad-impacto.md", estado="en-revision", version="0.1")
run(E(f'estado.py --proyecto {G} aprobar evaluacion-probabilidad-impacto --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-10-28'), repo)

P("Paso 4 · Identificación: taller de riesgos (causa → evento → efecto) ligado a productos, WBS e interesados")
R = {}
riesgos = [
  ("R1", dict(categoria="externo", causa="El padrón del núcleo operativo no tiene entorno de pruebas (AD-1)", evento="La integración de consulta se prueba tarde", efecto="Atraso del Release 1 y defectos en FR-3/FR-4", tipo="amenaza", probabilidad=4, impacto=4, impacto_monetario=30000, proximidad="corto-plazo", propietario="Diego Ferreira", ejecutor="Lucía Benítez", notas=f"WBS 3.2 · producto Portal del socio · interesado {st['Área de TI del núcleo operativo']}")),
  ("R2", dict(categoria="organizacional", causa="Los operadores temen perder tareas con la bandeja única (FR-9)", evento="Resistencia a usar la consola", efecto="Adopción baja de la consola y doble trabajo", tipo="amenaza", probabilidad=3, impacto=4, impacto_monetario=15000, proximidad="mediano-plazo", propietario="Sofía Ramírez", ejecutor="Martín Suárez", notas=f"WBS 4.1 y 5.1 · producto Consola de operador · interesado {st['Sindicato de operadores']}")),
  ("R3", dict(categoria="tecnico", causa="El segundo factor depende de un proveedor de SMS nuevo (AD-5)", evento="El proveedor de SMS no cumple la disponibilidad", efecto="Socios sin poder ingresar (FR-1, NFR-2)", tipo="amenaza", probabilidad=3, impacto=5, impacto_monetario=25000, proximidad="mediano-plazo", propietario="Diego Ferreira", ejecutor="Lucía Benítez", notas="WBS 3.1 · producto Portal del socio")),
  ("R4", dict(categoria="externo", causa="La interpretación de la Ley 18.331 sobre constancias no está cerrada (NFR-1)", evento="Cumplimiento exige cambios en FR-5", efecto="Retrabajo de constancias y atraso", tipo="amenaza", probabilidad=2, impacto=4, impacto_monetario=12000, proximidad="mediano-plazo", propietario="Laura Méndez", ejecutor="Andrea Costa", notas=f"WBS 3.2 · interesado {st['Unidad de cumplimiento']}")),
  ("R5", dict(categoria="gestion", causa="El proveedor rota desarrolladores entre clientes", evento="Pérdida de conocimiento en el equipo", efecto="Baja de velocidad", tipo="amenaza", probabilidad=3, impacto=3, impacto_monetario=18000, proximidad="largo-plazo", propietario="Diego Ferreira", ejecutor="Lucía Benítez", notas="WBS 1.1")),
  ("R6", dict(categoria="comercial", causa="El generador de PDF del sistema de cartera ya existe", evento="Reutilizarlo para constancias (FR-5)", efecto="Ahorro de esfuerzo en WBS 3.2", tipo="oportunidad", probabilidad=3, impacto=3, impacto_monetario=8000, proximidad="corto-plazo", propietario="Sofía Ramírez", ejecutor="Lucía Benítez", notas="WBS 3.2 · producto Portal del socio")),
]
for k, c in riesgos:
    R[k] = reg(repo, "riesgos", fecha_identificacion="2026-10-29", autor="Martín Suárez", estado="abierto", **c)

P("Paso 5 · Evaluación y perfil de riesgo (P×I, EMV, exposición)")
run(E(f'registro.py --proyecto {G} resumen --json --corte 2026-11-03'), repo)
run(E(f'registro.py --proyecto {G} listar riesgos --abiertos'), repo)
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1, 2))

P("Paso 6 · Respuestas, riesgo residual, disparadores y acciones en el plan")
resp = {"R1": ("reducir", "spike de integración con datos sintéticos en el sprint 1; pedir entorno de pruebas a TI", 2, 4, "spike sin datos del padrón al día 5"),
        "R2": ("reducir", "taller con operadores y piloto de la bandeja en una sucursal", 2, 3, "menos del 50 % de operadores usa la consola en el piloto"),
        "R3": ("transferir", "SLA de 99,9 % con penalidad en el contrato del proveedor de SMS; correo como factor alternativo", 2, 4, "dos caídas del proveedor en un mes"),
        "R4": ("aceptar", "seguimiento mensual con cumplimiento; contingencia de 1 semana", 2, 4, "dictamen de cumplimiento"),
        "R5": ("reducir", "cláusula de permanencia del equipo clave y documentación de decisiones", 2, 3, "salida de un desarrollador clave"),
        "R6": ("explotar", "spike de reutilización del generador de PDF en el sprint 2", 4, 3, "")}
for k, (r, acc, pr, ir, disp) in resp.items():
    act(repo, "riesgos", R[k], respuesta=r, acciones=acc, probabilidad_residual=pr, impacto_residual=ir, disparador=disp, estado="en-seguimiento", fecha_revision="2026-11-17")
A1 = reg(repo, "acciones", fecha="2026-11-03", origen=R["R1"], descripcion="Spike de integración con el padrón usando datos sintéticos", responsable="Lucía Benítez", fecha_compromiso="2026-12-11", prioridad="alta")
A2 = reg(repo, "acciones", fecha="2026-11-03", origen=R["R2"], descripcion="Taller con operadores y delegado sindical sobre la bandeja única", responsable="Martín Suárez", fecha_compromiso="2026-11-20", prioridad="alta")
A3 = reg(repo, "acciones", fecha="2026-11-03", origen=R["R3"], descripcion="Negociar SLA con penalidad con el proveedor de SMS", responsable="Diego Ferreira", fecha_compromiso="2026-11-25", prioridad="media")
for k in ("R1", "R3", "R5"):
    reg(repo, "decisiones", fecha="2026-11-04", decision=f"El propietario acepta la respuesta de {R[k]}", decidido_por="Proveedor sénior: Diego Ferreira", nivel="gestor")

P("Paso 7 · Presupuesto de riesgo (contingencia) y puerta autorizar-proyecto")
run(E(f'registro.py --proyecto {G} resumen --json --corte 2026-11-20'), repo)
reg(repo, "decisiones", fecha="2026-11-27", decision="Presupuesto de riesgo de USD 23.000 dentro del BAC (EMV residual 30.000 menos 7.500 de R-003 transferido al proveedor); su uso lo autoriza el ejecutivo", decidido_por="Ejecutivo: Laura Méndez", nivel="ejecutivo", artefactos_afectados="02-planificacion/presupuesto.md")
for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
    art(repo, c, r)
puerta(repo, "autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")
art(repo, "business-case", "00-direccion/business-case.md", texto="# Business case\n\nB-01 desvío de consultas (SM-2); B-02 adopción (SM-1).\n")
art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
puerta(repo, "autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"', repo, mostrar=False)
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26'), repo, mostrar=False)
art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
puerta(repo, "autorizar-etapa", "Ejecutivo: Laura Méndez", "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=±10 %" "costo=±10 %"')

P("Paso 8 · Seguimiento en la etapa: revisión de riesgos del sprint (reevaluar, cerrar acciones, detectar vencidas)")
act(repo, "acciones", A2, estado="completada", fecha_cierre="2026-11-19")
act(repo, "acciones", A3, estado="completada", fecha_cierre="2026-11-24")
act(repo, "riesgos", R["R2"], probabilidad=2, notas=f"WBS 4.1 y 5.1 · producto Consola de operador · interesado {st['Sindicato de operadores']} · taller {A2} realizado: actitud mejoró", fecha_revision="2026-12-15")
act(repo, "riesgos", R["R6"], estado="cerrado", notas="WBS 3.2 · oportunidad aprovechada: generador reutilizado, ahorro 60 h", fecha_revision="2026-12-15")
run(E(f'registro.py --proyecto {G} resumen --corte 2026-12-15'), repo)
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1, 2))

OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
obj1 = [{"clave": "tiempo", "pronostico": "en plan", "tol_etapa": "±10 %", "tol_proyecto": "±3 semanas", "rag": "verde"},
        {"clave": "costo", "pronostico": "en plan", "tol_etapa": "±10 %", "tol_proyecto": "±8 %", "rag": "verde"},
        {"clave": "alcance", "pronostico": "Must en R1", "tol_etapa": "", "tol_proyecto": "Must sin tolerancia", "rag": "verde"},
        {"clave": "calidad", "pronostico": "sin defectos críticos", "tol_etapa": "", "tol_proyecto": "", "rag": "verde"},
        {"clave": "beneficios", "pronostico": "sin cambios", "tol_etapa": "", "tol_proyecto": "-10 %", "rag": "verde"},
        {"clave": "riesgo", "pronostico": "2 altos con respuesta (R-001, R-003); exposición en baja", "tol_etapa": "", "tol_proyecto": "ningún alto sin respuesta · ≤ USD 60.000", "rag": "ambar"},
        {"clave": "sostenibilidad", "pronostico": "[por confirmar]", "tol_etapa": "", "tol_proyecto": "", "rag": "na"}]
tablero(repo, "2026-12-15", "2026-12-01", "2026-12-15", "2026-12-29", obj1, [], [{"id": R["R1"], "texto": "si el spike confirma que no hay entorno de pruebas: aceptar 2 semanas de atraso o pagar entorno temporal", "fecha_limite": "2026-12-18"}], [],
        "Revisión de riesgos del sprint 2: R-002 bajó a 8 tras el taller; la oportunidad R-006 se aprovechó; A-001 (spike) vence sin cerrar.",
        "riesgos.csv, acciones.csv, issues.csv al 2026-12-15", salida_png=os.path.join(OUT, "g1-tablero.png"))
P("Paso 9 · Un riesgo se materializa: de riesgo a issue")
act(repo, "riesgos", R["R1"], estado="ocurrido", fecha_revision="2026-12-16", notas=f"WBS 3.2 · el spike {A1} confirmó que TI no da entorno de pruebas hasta febrero")
I1 = reg(repo, "issues", fecha="2026-12-16", tipo="problema-preocupacion", titulo=f"Sin entorno de pruebas del padrón hasta febrero (materializa {R['R1']})", descripcion="Las historias 1-3 y 1-4 no pueden probarse contra el núcleo operativo", prioridad="alta", severidad="mayor", impacto="2 semanas de atraso en WBS 3.2", responsable="Martín Suárez")
act(repo, "acciones", A1, estado="completada", fecha_cierre="2026-12-11")
run(E(f'registro.py --proyecto {G} listar issues --abiertos'), repo)

P("Paso 10 · Riesgo nuevo sobre la línea: escalamiento a la junta")
R7 = reg(repo, "riesgos", fecha_identificacion="2027-01-08", autor="Martín Suárez", categoria="externo", causa="El regulador anunció nueva norma de autenticación para servicios financieros", evento="La norma exige biometría para operaciones de préstamo (FR-6)", efecto="Rediseño del acceso y atraso del Release 2", tipo="amenaza", probabilidad=3, impacto=5, impacto_monetario=40000, proximidad="mediano-plazo", respuesta="escalar", propietario="Laura Méndez", ejecutor="Martín Suárez", estado="escalado", notas=f"WBS 3.1 y 3.3 · interesado {st['Unidad de cumplimiento']} · afecta el business case: decide la junta")
run(E(f'registro.py --proyecto {G} resumen --json --corte 2027-01-08'), repo)
run(E(f'estado.py --proyecto {G} puerta decision-ad-hoc --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-01-12 --condiciones "usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar {R7} en la próxima junta"'), repo)
act(repo, "riesgos", R7, respuesta="reducir", acciones="análisis normativo con asesoría externa; diseño de autenticación reforzada detrás de IdentityPort (AD-5)", probabilidad_residual=2, impacto_residual=4, estado="en-seguimiento")

P("Paso 11 · Informe de riesgos e insumo para el highlight")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-01-15'), repo)
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)
art(repo, "informe-riesgos-2027-01-15", "03-control/reportes/2027-01-15-informe-riesgos.md")

P("Paso 12 · Límite de etapa: auditoría de riesgos, lecciones y cierre de riesgos")
run(E(f'estado.py --proyecto {G} limite-etapa'), repo)
act(repo, "issues", I1, estado="resuelto", fecha_cierre="2027-02-10", decision="entorno de pruebas habilitado el 2027-02-08")
act(repo, "riesgos", R["R5"], estado="retirado", notas="WBS 1.1 · equipo estable durante la etapa", fecha_revision="2027-03-01")
reg(repo, "lecciones", etapa="2", categoria="riesgo", situacion=f"{R['R1']} se materializó: el entorno de pruebas del núcleo dependía de otra área", efecto="2 semanas de atraso en WBS 3.2", recomendacion="exigir el entorno de pruebas como condición de la puerta autorizar-etapa", prioridad="alta", responsable_seguimiento="Martín Suárez")
art(repo, "auditoria-riesgos-2027-03-01", "03-control/reportes/2027-03-01-auditoria-riesgos.md")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-03-01'), repo)
run(E(f'puertas.py --proyecto {G} verificar autorizar-etapa'), repo, ok=(0, 1, 2))
run(E(f'exportar.py xlsx --proyecto {G}'), repo, ok=(0, 1))
import csv as _c
filas = list(_c.DictReader(open(os.path.join(repo, G, "03-control/registros/riesgos.csv"), encoding="utf-8")))
LOG.append(("(riesgos.csv al cierre de la etapa: id, tipo, P×I, residual, EMV, respuesta, estado)", "\n".join(f"{f['id']} {f['tipo'][:4]} P{f['probabilidad']}×I{f['impacto']}={f['puntuacion']:>3} res P{f['probabilidad_residual']}×I{f['impacto_residual']} EMV {f['valor_esperado']:>7} {f['respuesta']:10s} {f['estado']}" for f in filas)))
with open(sys.argv[1] if len(sys.argv) > 1 else "salida-g1.md", "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
