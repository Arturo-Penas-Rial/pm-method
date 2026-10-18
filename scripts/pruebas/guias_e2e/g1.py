"""Guía E2E-1 · Ciclo completo de gestión de riesgos (producto, WBS, interesados) con scripts reales."""
from comun import *
repo = proyecto("portal-socios"); print("REPO", repo)
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))
WBS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wbs.csv"), encoding="utf-8").read()
EJ = "Ejecutiva: Laura Méndez"
PCT = {1: 0.1, 2: 0.3, 3: 0.5, 4: 0.7, 5: 0.9}          # conversión de la escala aprobada (paso 3)
usd = lambda n: f"{n:,.0f}".replace(",", ".")
def puerta_f(repo, tipo, por, fecha, extra="", decision="aprobado"):
    """Como puerta() de comun.py, con la fecha del paso en la lista de control (corrida determinista)."""
    run(E(f'puertas.py --proyecto {G} verificar {tipo}'), repo, ok=(0, 1, 2))
    run(E(f'puertas.py --proyecto {G} lista {tipo} --fecha {fecha}'), repo, mostrar=False)
    run(E(f'puertas.py --proyecto {G} confirmar {tipo} --por "{por}" --fecha {fecha}'), repo)
    return run(E(f'estado.py --proyecto {G} puerta {tipo} --decision {decision} --por "{por}" --fecha {fecha} {extra}'), repo)
def sanidad(repo, corte):
    return run(E(f'sanidad.py --proyecto {G} --rapido --corte {corte}'), repo, ok=(0, 1, 2))

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

P("Paso 3 · Enfoque de gestión de riesgos y escala P×I (propuesta → aprobación de la ejecutiva)")
run(E(f'estado.py --proyecto {G} umbrales-riesgo alto=15 medio=6'), repo)
art(repo, "evaluacion-probabilidad-impacto", "02-planificacion/enfoques/evaluacion-probabilidad-impacto.md", estado="en-revision", version="0.1")
run(E(f'estado.py --proyecto {G} aprobar evaluacion-probabilidad-impacto --por "{EJ}" --version 1.0 --fecha 2026-10-28'), repo)
ENFOQUE = """---
tipo: enfoque-riesgo
proyecto: "Portal de autoservicio para socios"
version: 0.1
fecha: "2026-10-28"
autor: "Martín Suárez"
estado: en-revision
aprobado_por: ""
idioma: "es"
---

# Enfoque de gestión de riesgos — Portal de autoservicio para socios

**Versión mínima:** sí (una página; escalas y matriz en evaluacion-probabilidad-impacto.md).

## 1. Alcance
Proyecto completo; los riesgos del proveedor (Diego Ferreira) entran al mismo registro (riesgos.csv).

## 2. Procedimiento
Identificar: candidatos citados de BMAD, transcripciones, Jira y artefactos (riesgos.py candidatos) y taller al inicio de cada etapa.
Evaluar: P×I 1–5 y EMV en riesgos.csv. Planificar: respuesta del catálogo, aceptada por su propietario y justificada
por costo de la respuesta < reducción de EMV (si no, justificación no económica explícita). Implementar: acciones en
acciones.csv y en el plan de etapa. Comunicar: sección de riesgos del highlight e informe de riesgos a la junta.

## 3-4. Escalas y matriz
Las de evaluacion-probabilidad-impacto.md v1.0: alto >= 15, medio 6-12, bajo <= 5; P1…P5 = 10/30/50/70/90 %.

## 6. Apetito y tolerancia
Apetito: bajo en cumplimiento (Ley 18.331) y seguridad del acceso; moderado en plazo y costo a cambio de adopción
temprana; abierto a oportunidades de reutilización.
Tolerancia del proyecto: ningún riesgo alto sin respuesta y propietario; exposición de amenazas (suma de EMV)
<= USD 60.000 (estado.json, tolerancias.proyecto.riesgo). Un riesgo que queda sobre la línea (>= 15) o que por sí solo
amenaza la tolerancia de tiempo o costo se escala a la junta, con su hoja de riesgo.

## 7. Presupuesto de riesgo y autoridad sobre la reserva
Presupuesto de riesgo = suma del costo de las respuestas + EMV residual de las amenazas + provisión para riesgos no
identificados (5 % del costo de la WBS). Lo fija la ejecutiva (estado.py presupuesto riesgo=<monto>).
El gestor compromete hasta USD 5.000 por respuesta ya aceptada; por encima, o para un riesgo nuevo, decide la ejecutiva.
Cada uso se registra en cambios.csv con cargo=reserva-riesgo y cita el R-### al que responde; lo que no responde a un
riesgo va al presupuesto de cambio o a la junta. La reserva de gestión la libera solo la junta.

## 8. Roles
Ejecutiva: aprueba este enfoque, fija y libera la reserva. Propietarios: aceptan la respuesta de su riesgo.
Ejecutores: acciones con fecha. Aseguramiento (Andrea Costa): revisa el registro en cada fin de etapa.

## 9. Cadencia
Revisión del registro en cada sprint (14 días); reevaluación completa y auditoría en cada fin de etapa; vigilancia
normativa mensual con cumplimiento.

## 10. Reportes
Highlight: altos, nuevos, ocurridos y consumo de la reserva (sanidad CAM-03). Informe de riesgos a pedido de la junta.
"""
escribir(repo, "02-planificacion/enfoques/enfoque-riesgo.md", ENFOQUE)
LOG.append(("(pm-enfoques-gestion redacta el enfoque con templates/enfoque-riesgo.md, versión mínima → gestion/02-planificacion/enfoques/enfoque-riesgo.md)", ENFOQUE.split("---", 2)[2].strip()))
run(E(f'estado.py --proyecto {G} artefacto enfoque-riesgo --ruta 02-planificacion/enfoques/enfoque-riesgo.md --estado en-revision --version 0.1'), repo)
run(E(f'estado.py --proyecto {G} aprobar enfoque-riesgo --por "{EJ}" --version 1.0 --fecha 2026-10-28'), repo)

P("Paso 4 · Identificación desde varias fuentes (BMAD, entrevistas y reuniones, artefactos) y taller de riesgos")
RK = f"python3 {RAIZ}/skills/pm-riesgos/scripts/riesgos.py --proyecto {G}"
vtt_r = """WEBVTT

00:00:01.000 --> 00:00:12.000
<v Martín Suárez>Hagamos la ronda de riesgos del portal antes del taller.

00:00:13.000 --> 00:00:30.000
<v Área de TI del núcleo operativo>Nos preocupa que el padrón no tenga entorno de pruebas; dependemos de otra área para habilitarlo.

00:00:31.000 --> 00:00:45.000
<v Sindicato de operadores>Los operadores temen perder tareas con la bandeja única.

00:00:46.000 --> 00:00:58.000
<v Lucía Benítez>Si no llega el contrato del proveedor de SMS, el segundo factor se atrasa. Además rotan desarrolladores entre clientes y eso nos puede atrasar.

00:00:59.000 --> 00:01:10.000
<v Unidad de cumplimiento>No está claro cómo interpreta la Ley 18.331 las constancias.

00:01:11.000 --> 00:01:20.000
<v Sofía Ramírez>Podríamos aprovechar el generador de PDF del sistema de cartera para las constancias.
"""
escribir(repo, "03-control/reuniones/2026-10-27-ronda-riesgos-original.vtt", vtt_r)
LOG.append(("(transcripción de ejemplo: copiala a gestion/03-control/reuniones/2026-10-27-ronda-riesgos-original.vtt)", vtt_r.strip()))
run(f'python3 {RAIZ}/skills/pm-reuniones/scripts/transcripcion.py {G}/03-control/reuniones/2026-10-27-ronda-riesgos-original.vtt --salida {G}/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md', repo)
run(f'{RK} candidatos --fecha 2026-10-28', repo, corte=200)
R = {}
riesgos = [
  ("R1", dict(categoria="externo", causa="El padrón del núcleo operativo no tiene entorno de pruebas (AD-1)", evento="La integración de consulta se prueba tarde", efecto="Atraso del Release 1 y defectos en FR-3/FR-4", tipo="amenaza", probabilidad=4, impacto=4, impacto_monetario=30000, proximidad="corto-plazo", propietario="Diego Ferreira", ejecutor="Lucía Benítez", notas=f"WBS 3.2 · producto Portal del socio · interesado {st['Área de TI del núcleo operativo']} · origen: brief.md:91 (BMAD) y ronda 2026-10-27 [00:00:13]")),
  ("R2", dict(categoria="organizacional", causa="Los operadores temen perder tareas con la bandeja única (FR-9)", evento="Resistencia a usar la consola", efecto="Adopción baja de la consola y doble trabajo", tipo="amenaza", probabilidad=3, impacto=4, impacto_monetario=15000, proximidad="mediano-plazo", propietario="Sofía Ramírez", ejecutor="Martín Suárez", notas=f"WBS 4.1 y 5.1 · producto Consola de operador · interesado {st['Sindicato de operadores']} · origen: ronda 2026-10-27 [00:00:31]")),
  ("R3", dict(categoria="tecnico", causa="El segundo factor depende de un proveedor de SMS nuevo (AD-5)", evento="El proveedor de SMS no cumple la disponibilidad", efecto="Socios sin poder ingresar (FR-1, NFR-2)", tipo="amenaza", probabilidad=3, impacto=5, impacto_monetario=25000, proximidad="mediano-plazo", propietario="Diego Ferreira", ejecutor="Lucía Benítez", notas="WBS 3.1 · producto Portal del socio · origen: prd.md:249 y ARCHITECTURE-SPINE.md:177 (BMAD) y ronda 2026-10-27 [00:00:46]")),
  ("R4", dict(categoria="externo", causa="La interpretación de la Ley 18.331 sobre constancias no está cerrada (NFR-1)", evento="Cumplimiento exige cambios en FR-5", efecto="Retrabajo de constancias y atraso", tipo="amenaza", probabilidad=2, impacto=4, impacto_monetario=12000, proximidad="mediano-plazo", propietario="Laura Méndez", ejecutor="Andrea Costa", notas=f"WBS 3.2 · interesado {st['Unidad de cumplimiento']} · origen: brief.md:89 (BMAD) y ronda 2026-10-27 [00:00:59]")),
  ("R5", dict(categoria="gestion", causa="El proveedor rota desarrolladores entre clientes", evento="Pérdida de conocimiento en el equipo", efecto="Baja de velocidad", tipo="amenaza", probabilidad=3, impacto=3, impacto_monetario=18000, proximidad="largo-plazo", propietario="Diego Ferreira", ejecutor="Lucía Benítez", notas="WBS 1.1 · origen: ronda 2026-10-27 [00:00:46]")),
  ("R6", dict(categoria="comercial", causa="El generador de PDF del sistema de cartera ya existe", evento="Reutilizarlo para constancias (FR-5)", efecto="Ahorro de esfuerzo en WBS 3.2", tipo="oportunidad", probabilidad=3, impacto=3, impacto_monetario=8000, proximidad="corto-plazo", propietario="Sofía Ramírez", ejecutor="Lucía Benítez", notas="WBS 3.2 · producto Portal del socio · origen: ronda 2026-10-27 [00:01:11]")),
]
for k, c in riesgos:
    R[k] = reg(repo, "riesgos", fecha_identificacion="2026-10-29", autor="Martín Suárez", estado="abierto", **c)

P("Paso 5 · Evaluación y perfil de riesgo (P×I, EMV, exposición)")
run(E(f'registro.py --proyecto {G} resumen --json --corte 2026-11-03'), repo)
run(E(f'registro.py --proyecto {G} listar riesgos --abiertos'), repo)
sanidad(repo, "2026-11-03")

P("Paso 6 · Respuestas con costo justificado por EMV, residual, secundarios, disparadores y acciones")
resp = {"R1": ("reducir", "spike de integración con datos sintéticos en el sprint 1; pedir entorno de pruebas a TI", 2, 4, "spike sin datos del padrón al día 5", 2000),
        "R2": ("reducir", "taller con operadores y piloto de la bandeja en una sucursal", 2, 3, "menos del 50 % de operadores usa la consola en el piloto", 1500),
        "R3": ("transferir", "SLA de 99,9 % con penalidad en el contrato del proveedor de SMS; correo como factor alternativo", 2, 4, "dos caídas del proveedor en un mes", 2500),
        "R4": ("aceptar", "seguimiento mensual con cumplimiento; contingencia de 1 semana", 2, 4, "dictamen de cumplimiento", 0),
        "R5": ("reducir", "cláusula de permanencia del equipo clave y documentación de decisiones", 2, 3, "salida de un desarrollador clave", 3000),
        "R6": ("explotar", "spike de reutilización del generador de PDF en el sprint 2", 4, 3, "", 800)}
monto = {k: c["impacto_monetario"] for k, c in riesgos}; prob = {k: c["probabilidad"] for k, c in riesgos}
filas_j = []
for k, (r, acc, pr, ir, disp, costo) in resp.items():
    antes, despues = monto[k] * PCT[prob[k]], monto[k] * PCT[pr]
    delta = despues - antes if r == "explotar" else antes - despues
    filas_j.append((R[k], r, antes, despues, costo, delta))
    act(repo, "riesgos", R[k], respuesta=r, acciones=f"{acc} · costo USD {usd(costo)} · ΔEMV USD {usd(delta)}", probabilidad_residual=pr, impacto_residual=ir, disparador=disp, estado="en-seguimiento", fecha_revision="2026-11-17")
R["R7"] = reg(repo, "riesgos", fecha_identificacion="2026-11-04", autor="Martín Suárez", categoria="comercial", causa=f"La respuesta de {R['R3']} transfiere el riesgo con una penalidad con tope de USD 2.000 por mes",
              evento="El proveedor de SMS falla y la penalidad cobrada no cubre el costo del atraso", efecto="Costo del atraso no recuperado (WBS 3.1)", tipo="amenaza", probabilidad=2, impacto=3, impacto_monetario=6000,
              proximidad="mediano-plazo", respuesta="aceptar", acciones="aceptar: el correo como factor alternativo (respuesta de R-003) limita el atraso · costo USD 0", probabilidad_residual=2, impacto_residual=3,
              disparador="primera caída con penalidad menor que el costo del atraso", propietario="Diego Ferreira", ejecutor="Lucía Benítez", estado="en-seguimiento", fecha_revision="2026-11-17",
              notas=f"WBS 3.1 · riesgo secundario de {R['R3']} (respuesta transferir)")
filas_j.append((R["R7"], "aceptar", 1800, 1800, 0, 0))
LOG.append(("(pm-riesgos: justificación económica de cada respuesta, desde riesgos.csv; EMV = impacto_monetario × probabilidad convertida)",
            "id     respuesta   EMV antes  EMV residual  costo respuesta  ΔEMV    ¿costo < ΔEMV?\n" + "\n".join(
            f"{i}  {r:10s}  {usd(a):>9}  {usd(d):>12}  {usd(c):>15}  {usd(x):>6}  {'sí' if c < x else ('n/a (aceptar)' if r == 'aceptar' else 'no')}" for i, r, a, d, c, x in filas_j)
            + f"\nTotal costo de respuestas: USD {usd(sum(f[4] for f in filas_j))} · EMV residual de amenazas: USD {usd(sum(f[3] for f in filas_j if f[1] != 'explotar'))}"))
A1 = reg(repo, "acciones", fecha="2026-11-03", origen=R["R1"], descripcion="Spike de integración con el padrón usando datos sintéticos", responsable="Lucía Benítez", fecha_compromiso="2026-12-11", prioridad="alta")
A2 = reg(repo, "acciones", fecha="2026-11-03", origen=R["R2"], descripcion="Taller con operadores y delegado sindical sobre la bandeja única", responsable="Martín Suárez", fecha_compromiso="2026-11-20", prioridad="alta")
A3 = reg(repo, "acciones", fecha="2026-11-03", origen=R["R3"], descripcion="Negociar SLA con penalidad con el proveedor de SMS", responsable="Diego Ferreira", fecha_compromiso="2026-11-25", prioridad="media")
for ks, quien, nivel in ((("R1", "R3", "R5", "R7"), "Proveedor sénior: Diego Ferreira", "gestor"), (("R2", "R6"), "Usuaria sénior: Sofía Ramírez", "gestor"), (("R4",), EJ, "ejecutivo")):
    reg(repo, "decisiones", fecha="2026-11-04", decision=f"La persona propietaria acepta la respuesta, su costo y el residual de {', '.join(R[k] for k in ks)}", decidido_por=quien, nivel=nivel)
run(E(f'registro.py --proyecto {G} listar riesgos --abiertos'), repo, corte=12)

P("Paso 7 · Presupuesto de riesgo (respuestas + EMV residual + no identificados), control de la reserva y puertas")
run(E(f'registro.py --proyecto {G} resumen --json --corte 2026-11-20'), repo)
c_resp = sum(f[4] for f in filas_j); emv_res = sum(f[3] for f in filas_j if f[1] != "explotar"); prov = 0.05 * 124000
PRES = f"""# Presupuesto de riesgo (contingencia) · etapa 2 y proyecto

| Componente | USD | Criterio |
|---|---|---|
| Costo de las respuestas planificadas | {usd(c_resp)} | R-001 2.000 · R-002 1.500 · R-003 2.500 · R-005 3.000 · R-006 800 (cada una < su reducción de EMV) |
| EMV residual de las amenazas | {usd(emv_res)} | R-001 9.000 · R-002 4.500 · R-003 7.500 · R-004 3.600 · R-005 5.400 · R-007 1.800 |
| Provisión para riesgos no identificados | {usd(prov)} | 5 % del costo de la WBS (124.000), según el enfoque de riesgo §7 |
| **Presupuesto de riesgo** | **{usd(c_resp + emv_res + prov)}** | aparte del costo de los paquetes; lo fija la ejecutiva |

La transferencia de R-003 no descuenta su EMV residual: la penalidad del SLA no cubre el atraso (riesgo secundario R-007).
"""
escribir(repo, "02-planificacion/presupuesto.md", PRES)
LOG.append(("(pm-riesgos calcula el presupuesto de riesgo con la fórmula del enfoque §7 → gestion/02-planificacion/presupuesto.md)", PRES.strip()))
run(E(f'estado.py --proyecto {G} artefacto presupuesto --ruta 02-planificacion/presupuesto.md --estado en-revision'), repo, mostrar=False)
run(E(f'estado.py --proyecto {G} presupuesto riesgo={c_resp + emv_res + prov:.0f} --por "{EJ}" --fecha 2026-11-27'), repo)
C1 = reg(repo, "cambios", fecha="2026-11-27", solicitante="Martín Suárez", titulo="Financiar las respuestas planificadas de R-001, R-002, R-003, R-005 y R-006",
         descripcion="spike del padrón (R-001) 2.000; taller y piloto (R-002) 1.500; sobreprecio del SLA y correo alternativo (R-003) 2.500; bono de permanencia (R-005) 3.000; spike de reutilización (R-006) 800",
         justificacion="cada costo es menor que la reducción de EMV que logra (enfoque de riesgo §7)", impacto_costo="9.800 de la reserva de riesgo",
         decision="aprobado", decidido_por=EJ, fecha_decision="2026-11-27", estado="aprobado", costo=c_resp, cargo="reserva-riesgo")
sanidad(repo, "2026-11-27")
run(E(f'estado.py --proyecto {G} resumen'), repo)
for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
    art(repo, c, r)
puerta_f(repo, "autorizar-inicio", EJ, "2026-10-30", "--fin 2026-11-27")
art(repo, "business-case", "00-direccion/business-case.md", version="1.0", texto="# Business case\n\nB-01 desvío de consultas (SM-2); B-02 adopción (SM-1).\n")
BEN = """# Enfoque de gestión de beneficios (mínimo)

| Id | Beneficio | Dueña | Medida | Cuándo se mide |
|---|---|---|---|---|
| B-01 | Desvío de consultas de sucursal al portal (SM-2) | Sofía Ramírez | % de consultas resueltas en el portal | mensual desde la puesta en producción; revisión a los 6 meses (después del proyecto, a cargo del negocio) |
| B-02 | Adopción del portal por los socios (SM-1) | Sofía Ramírez | socios activos por mes | mensual; revisión a los 3 y 6 meses |
"""
art(repo, "enfoque-beneficios", "00-direccion/enfoque-beneficios.md", texto=BEN)
art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
run(E(f'estado.py --proyecto {G} aprobar business-case --por "{EJ}" --version 1.0 --fecha 2026-11-27'), repo)
puerta_f(repo, "autorizar-proyecto", EJ, "2026-11-27")
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "{EJ}"', repo, mostrar=False)
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26'), repo, mostrar=False)
art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
puerta_f(repo, "autorizar-etapa", EJ, "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=±10 %" "costo=±10 %"')

P("Paso 8 · Seguimiento en la etapa: revisión de riesgos del sprint (reevaluar, cerrar acciones, detectar vencidas)")
act(repo, "acciones", A2, estado="completada", fecha_cierre="2026-11-19")
act(repo, "acciones", A3, estado="completada", fecha_cierre="2026-11-24")
act(repo, "riesgos", R["R2"], probabilidad=2, notas=f"WBS 4.1 y 5.1 · producto Consola de operador · interesado {st['Sindicato de operadores']} · taller {A2} realizado: actitud mejoró", fecha_revision="2026-12-15")
act(repo, "riesgos", R["R6"], estado="cerrado", notas="WBS 3.2 · oportunidad aprovechada: generador reutilizado, ahorro 60 h", fecha_revision="2026-12-15")
run(E(f'registro.py --proyecto {G} resumen --corte 2026-12-15'), repo)
sanidad(repo, "2026-12-15")

OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
obj1 = [{"clave": "tiempo", "pronostico": "en plan", "tol_etapa": "±10 %", "tol_proyecto": "±3 semanas", "rag": "verde"},
        {"clave": "costo", "pronostico": "en plan", "tol_etapa": "±10 %", "tol_proyecto": "±8 %", "rag": "verde"},
        {"clave": "alcance", "pronostico": "Must en R1", "tol_etapa": "", "tol_proyecto": "Must sin tolerancia", "rag": "verde"},
        {"clave": "calidad", "pronostico": "sin defectos críticos", "tol_etapa": "", "tol_proyecto": "", "rag": "verde"},
        {"clave": "beneficios", "pronostico": "sin cambios", "tol_etapa": "", "tol_proyecto": "-10 %", "rag": "verde"},
        {"clave": "riesgo", "pronostico": "2 altos con respuesta (R-001, R-003); exposición en baja; reserva al 21 %", "tol_etapa": "", "tol_proyecto": "ningún alto sin respuesta · ≤ USD 60.000", "rag": "ambar"},
        {"clave": "sostenibilidad", "pronostico": "[por confirmar]", "tol_etapa": "", "tol_proyecto": "", "rag": "na"}]
tablero(repo, "2026-12-15", "2026-12-01", "2026-12-15", "2026-12-29", obj1, [], [{"id": R["R1"], "texto": "si el spike confirma que no hay entorno de pruebas: aceptar 2 semanas de atraso o pagar entorno temporal", "fecha_limite": "2026-12-18"}], [],
        "Revisión de riesgos del sprint 2: R-002 bajó a 8 tras el taller; la oportunidad R-006 se aprovechó; A-001 (spike) vence sin cerrar.",
        "riesgos.csv, acciones.csv, issues.csv al 2026-12-15", salida_png=os.path.join(OUT, "g1-tablero.png"))
P("Paso 9 · Incidencias emergentes desde Jira: riesgo → issue, defecto fuera de especificación y control del consumo de la reserva de riesgo")
escribir(repo, "03-control/fuentes/jira-2026-12-16.csv", "clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url,prioridad,etiquetas,vinculo\n"
         "PS-101,Bug,La consulta de saldos devuelve timeout con el padrón de prueba,En curso,Lucía Benítez,Sprint 2,,2026-12-16,https://jira.example.org/browse/PS-101,Highest,,1-3-consulta-de-saldos-de-ahorro-y-préstamos\n"
         "PS-102,Impedimento,Sin entorno de pruebas del padrón: historias 1-3 y 1-4 bloqueadas,Bloqueado,Martín Suárez,Sprint 2,,2026-12-16,https://jira.example.org/browse/PS-102,High,,\n"
         "PS-103,Historia,Descarga de constancias en PDF,En curso,Lucía Benítez,Sprint 2,5,2026-12-15,https://jira.example.org/browse/PS-103,Medium,,1-4-descarga-de-constancias-en-pdf\n"
         "PS-104,Tarea,Evaluar un proveedor de SMS alternativo por la disponibilidad del segundo factor,Por hacer,Diego Ferreira,Sprint 3,,2026-12-14,https://jira.example.org/browse/PS-104,Medium,riesgo,\n")
LOG.append(("(instantánea de Jira de ejemplo: la deja pm-integraciones en gestion/03-control/fuentes/jira-2026-12-16.csv)", open(os.path.join(repo, G, "03-control/fuentes/jira-2026-12-16.csv"), encoding="utf-8").read().strip()))
run(f'{RK} candidatos --fuentes tracker --fecha 2026-12-16', repo)
act(repo, "riesgos", R["R1"], estado="ocurrido", fecha_revision="2026-12-16", notas=f"WBS 3.2 · el spike {A1} confirmó que TI no da entorno de pruebas hasta febrero · origen: jira:PS-102")
I1 = reg(repo, "issues", fecha="2026-12-16", tipo="problema-preocupacion", titulo=f"Sin entorno de pruebas del padrón hasta febrero (materializa {R['R1']})", descripcion="Las historias 1-3 y 1-4 no pueden probarse contra el núcleo operativo", prioridad="alta", severidad="mayor", impacto="2 semanas de atraso en WBS 3.2", responsable="Martín Suárez", notas="origen: jira:PS-102")
I2 = reg(repo, "issues", fecha="2026-12-16", tipo="fuera-especificacion", titulo="Timeout en la consulta de saldos con el padrón de prueba (NFR-3)", descripcion="Defecto de la historia 1-3: la respuesta supera los 3 s del NFR-3", prioridad="alta", severidad="mayor", impacto="la historia 1-3 no cumple NFR-3", responsable="Lucía Benítez", notas="origen: jira:PS-101")
act(repo, "riesgos", R["R3"], notas="WBS 3.1 · producto Portal del socio · origen: prd.md:249 y ARCHITECTURE-SPINE.md:177 (BMAD) y ronda 2026-10-27 [00:00:46] · seguimiento: jira:PS-104 (proveedor alternativo)")
act(repo, "issues", I2, estado="resuelto", fecha_cierre="2026-12-20", decision="índice en la consulta del adaptador; p95 = 1,8 s", decidido_por="Jefa de equipo: Lucía Benítez")
act(repo, "acciones", A1, estado="completada", fecha_cierre="2026-12-11")
run(E(f'registro.py --proyecto {G} listar issues --abiertos'), repo)
C2 = reg(repo, "cambios", fecha="2026-12-17", solicitante="Martín Suárez", titulo=f"Entorno de pruebas temporal del padrón (contingencia de {R['R1']} materializado, {I1})",
         descripcion="entorno en la nube con una copia anonimizada del padrón durante 8 semanas, hasta que TI habilite el suyo en febrero",
         justificacion=f"contingencia prevista para {R['R1']} en el tablero del 15/12: baja el atraso de WBS 3.2 de 2 semanas a 3 días", impacto_tiempo="3 días en lugar de 2 semanas",
         impacto_costo="8.000", impacto_riesgo=f"responde a {R['R1']} (ocurrido) e {I1}", decision="aprobado", decidido_por=EJ, fecha_decision="2026-12-17", estado="aprobado", costo=8000, cargo="reserva-riesgo",
         notas="supera los USD 5.000 que el enfoque de riesgo delega en el gestor: decide la ejecutiva")
C3 = reg(repo, "cambios", fecha="2026-12-18", solicitante="Lucía Benítez", titulo="Licencias adicionales de la herramienta de diseño para el equipo UX",
         descripcion="dos licencias anuales porque el equipo de diseño creció", justificacion="productividad del equipo de diseño", impacto_costo="3.000",
         decision="aprobado", decidido_por="Gestor: Martín Suárez", fecha_decision="2026-12-18", estado="aprobado", costo=3000, cargo="reserva-riesgo")
sanidad(repo, "2026-12-18")
act(repo, "cambios", C3, decision="rechazado", estado="rechazado", decidido_por="Autoridad de cambio: Sofía Ramírez", fecha_decision="2026-12-18",
    notas="no responde a ningún riesgo: la reserva de riesgo no es una bolsa general; si hace falta, va como solicitud de cambio contra el presupuesto de cambio cuando la junta lo fije")
sanidad(repo, "2026-12-18")

P("Paso 10 · Riesgo nuevo sobre la línea: hoja de riesgo, escalamiento a la junta y revisión del business case")
R8 = reg(repo, "riesgos", fecha_identificacion="2027-01-08", autor="Martín Suárez", categoria="externo", causa="El regulador anunció nueva norma de autenticación para servicios financieros", evento="La norma exige biometría para operaciones de préstamo (FR-6)", efecto="Rediseño del acceso y atraso del Release 2", tipo="amenaza", probabilidad=3, impacto=5, impacto_monetario=40000, proximidad="mediano-plazo", respuesta="escalar", propietario="Laura Méndez", ejecutor="Martín Suárez", estado="escalado", notas=f"WBS 3.1 y 3.3 · interesado {st['Unidad de cumplimiento']} · afecta el business case: decide la junta")
HOJA = f"""---
tipo: hoja-riesgo
proyecto: "Portal de autoservicio para socios"
version: "0.1"
fecha: "2027-01-08"
autor: "Martín Suárez"
estado: borrador
aprobado_por: ""
idioma: "es"
---

# Hoja de datos de riesgo · {R8}

**Título:** norma de biometría para operaciones de préstamo · **Tipo:** amenaza · **Categoría:** externo · **Estado:** escalado

**Enunciado:** Si el regulador aprueba la nueva norma de autenticación, puede exigirse biometría para préstamos (FR-6),
lo que provocaría rediseñar el acceso (WBS 3.1 y 3.3) y atrasar el Release 2.
**Objetivos afectados:** tiempo (±3 semanas), costo (±8 %), beneficios (B-02 adopción, -10 %), cumplimiento (apetito bajo).

## Evaluación actual
P3 × I5 = 15 (alto, sobre la línea) · impacto monetario USD 40.000 · EMV = 50 % × 40.000 = USD 20.000 · proximidad: mediano plazo.

## Respuesta propuesta
Reducir: análisis normativo con asesoría externa y diseño de autenticación reforzada detrás de IdentityPort (AD-5).
Costo de la respuesta: USD 10.000 (reserva de riesgo; supera la autoridad del gestor: decide la ejecutiva).

## Evaluación residual y justificación
P2 × I4 = 8 · EMV residual = 30 % × 40.000 = USD 12.000 · reducción de EMV = USD 8.000.
Costo (10.000) mayor que la reducción de EMV (8.000): la respuesta **no se justifica solo por EMV**. Justificación no
económica: cumplimiento regulatorio, con apetito bajo según el enfoque de riesgo §6. Por eso decide la junta.
Riesgos secundarios: ninguno identificado. Residual aceptado: P2 × I4, revisión en la próxima junta.

## Alerta temprana y contingencia
Disparador: publicación de la norma en el Diario Oficial. Contingencia: autenticación biométrica para préstamos en el
Release 2 detrás de IdentityPort, con solicitud de cambio.
"""
escribir(repo, f"03-control/registros/{R8}-hoja-riesgo.md", HOJA)
LOG.append((f"(pm-riesgos redacta la hoja de riesgo con templates/hoja-riesgo.md → gestion/03-control/registros/{R8}-hoja-riesgo.md)", HOJA.split("---", 2)[2].strip()))
run(E(f'registro.py --proyecto {G} resumen --json --corte 2027-01-08'), repo)
run(E(f'estado.py --proyecto {G} puerta decision-ad-hoc --decision aprobado --por "{EJ}" --fecha 2027-01-12 --condiciones "usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar {R8} en la próxima junta"'), repo)
C4 = reg(repo, "cambios", fecha="2027-01-12", solicitante="Martín Suárez", titulo=f"Análisis normativo con asesoría externa (respuesta a {R8})",
         descripcion="asesoría externa sobre la norma de autenticación y diseño de autenticación reforzada detrás de IdentityPort (AD-5)",
         justificacion=f"hoja de riesgo de {R8}: justificación regulatoria (costo 10.000 mayor que la reducción de EMV 8.000)", impacto_costo="10.000", impacto_riesgo=f"responde a {R8}",
         decision="aprobado", decidido_por=EJ, fecha_decision="2027-01-12", estado="aprobado", costo=10000, cargo="reserva-riesgo", notas="decision-ad-hoc de la junta del 2027-01-12")
act(repo, "riesgos", R8, respuesta="reducir", acciones=f"análisis normativo con asesoría externa ({C4}); diseño de autenticación reforzada detrás de IdentityPort (AD-5) · costo USD 10.000 · ΔEMV USD 8.000", probabilidad_residual=2, impacto_residual=4, estado="en-seguimiento",
    notas=f"WBS 3.1 y 3.3 · interesado {st['Unidad de cumplimiento']} · hoja: 03-control/registros/{R8}-hoja-riesgo.md · decisión de la junta del 2027-01-12")
art(repo, "business-case", "00-direccion/business-case.md", version="1.1", texto=f"""# Business case

B-01 desvío de consultas (SM-2); B-02 adopción (SM-1).

## Revisión 2027-01-12 por {R8} (norma de biometría)
- Escenario adverso: costo adicional de hasta USD 40.000 y atraso del Release 2; B-02 (adopción) podría demorarse un trimestre.
- Con la respuesta aprobada (análisis normativo, {C4}, USD 10.000 de la reserva de riesgo) el caso sigue siendo viable:
  la junta mantiene el proyecto y vuelve a revisar {R8} y este caso en la próxima reunión.
""")
run(E(f'estado.py --proyecto {G} aprobar business-case --por "{EJ}" --version 1.1 --fecha 2027-01-12'), repo)
sanidad(repo, "2027-01-12")

P("Paso 11 · Informe de riesgos e insumo para el highlight")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-01-15'), repo)
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)
art(repo, "informe-riesgos-2027-01-15", "03-control/reportes/2027-01-15-informe-riesgos.md")

P("Paso 12 · Límite de etapa: auditoría de riesgos, lecciones y cierre de riesgos")
run(E(f'estado.py --proyecto {G} limite-etapa'), repo)
act(repo, "issues", I1, estado="resuelto", fecha_cierre="2027-02-10", decision="entorno de pruebas habilitado el 2027-02-08")
act(repo, "riesgos", R["R5"], estado="retirado", notas="WBS 1.1 · equipo estable durante la etapa", fecha_revision="2027-03-01")
reg(repo, "lecciones", etapa="2", categoria="riesgo", situacion=f"{R['R1']} se materializó: el entorno de pruebas del núcleo dependía de otra área", efecto=f"USD 8.000 de la reserva de riesgo ({C2}) y 3 días de atraso en WBS 3.2 (sin el entorno temporal, 2 semanas)", recomendacion="exigir el entorno de pruebas como condición de la puerta autorizar-etapa", prioridad="alta", responsable_seguimiento="Martín Suárez")
art(repo, "auditoria-riesgos-2027-03-01", "03-control/reportes/2027-03-01-auditoria-riesgos.md")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-03-01'), repo)
run(E(f'estado.py --proyecto {G} cumplir-condiciones decision-ad-hoc --fecha 2027-03-01 --por "{EJ}" --nota "{R8} revisado en la junta; análisis normativo entregado ({C4})"'), repo)
run(E(f'puertas.py --proyecto {G} verificar autorizar-etapa'), repo, ok=(0, 1, 2))
run(E(f'exportar.py xlsx --proyecto {G}'), repo, ok=(0, 1))
import csv as _c
filas = list(_c.DictReader(open(os.path.join(repo, G, "03-control/registros/riesgos.csv"), encoding="utf-8")))
LOG.append(("(riesgos.csv al cierre de la etapa: id, tipo, P×I, residual, EMV, respuesta, estado)", "\n".join(f"{f['id']} {f['tipo'][:4]} P{f['probabilidad']}×I{f['impacto']}={f['puntuacion']:>3} res P{f['probabilidad_residual']}×I{f['impacto_residual']} EMV {f['valor_esperado']:>7} {f['respuesta']:10s} {f['estado']}" for f in filas)))
P("Paso 13 · Variante sin BMAD: destilar riesgos de los artefactos del proyecto")
base2 = os.path.join(os.path.dirname(repo), "portal-sin-bmad"); os.makedirs(base2)
run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Portal de socios (sin BMAD)" --ejecutivo "Laura Méndez" --gestor "Martín Suárez"'), base2)
for rel_, txt in (("00-direccion/mandato.md", "# Mandato\n\n## Contexto\nPortal de autoservicio para socios.\n\n## Restricciones y riesgos conocidos\n- La salida en producción debe ocurrir antes del cierre del ejercicio (31/12/2027).\n- El núcleo operativo es de un proveedor externo con ventanas de cambio trimestrales.\n\n## Lecciones de proyectos anteriores\n- El proyecto de banca telefónica se atrasó 6 semanas porque el proveedor del núcleo no tenía entorno de pruebas.\n"),
                  ("01-inicio/project-brief.md", "# Project brief\n\n## Enfoque\nEquipo interno con apoyo de un proveedor. [supuesto] El área de TI asigna dos personas a tiempo completo.\n\n## Preguntas abiertas\n- ¿Quién aprueba los préstamos simples en el canal digital?\n"),
                  ("02-planificacion/requisitos.md", "# Requisitos\n\n| Id | Requisito | Prioridad | Fuente | Criterio |\n|---|---|---|---|---|\n| REQ-001 | Consultar saldos | Must | brief | p95 < 3 s |\n\n## Supuestos y dependencias\n- Los saldos se leen del núcleo operativo por una API de lectura [por confirmar].\n")):
    p_ = os.path.join(base2, G, rel_); os.makedirs(os.path.dirname(p_), exist_ok=True); open(p_, "w", encoding="utf-8").write(txt)
run(E(f'registro.py --proyecto {G} agregar supuestos --campo "supuesto_o_restriccion=El proveedor del núcleo publica la API de lectura antes de marzo" --campo tipo=supuesto --campo validado=pendiente --campo responsable="Área de TI"'), base2)
run(f'python3 {RAIZ}/skills/pm-riesgos/scripts/riesgos.py --proyecto {G} candidatos --fecha 2026-10-28', base2)
reg(base2, "riesgos", fecha_identificacion="2026-10-28", autor="Martín Suárez", categoria="externo", causa="El proveedor del núcleo cambia solo en ventanas trimestrales y no publicó la API de lectura (S-001)",
    evento="La API de lectura no está disponible en marzo", efecto="Atraso de la consulta de saldos (REQ-001) y del lanzamiento", tipo="amenaza", probabilidad=3, impacto=4, impacto_monetario=20000,
    propietario="Laura Méndez", ejecutor="Martín Suárez", notas="origen: mandato.md (restricciones y lecciones), requisitos.md (supuestos) y supuestos.csv S-001")
run(E(f'registro.py --proyecto {G} listar riesgos'), base2)

with open(sys.argv[1] if len(sys.argv) > 1 else "salida-g1.md", "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
