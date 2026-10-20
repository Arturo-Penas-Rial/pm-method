"""Guía E2E-1 · Ciclo completo de gestión de riesgos (producto, WBS, interesados) con scripts reales."""
from comun import *
repo = proyecto("portal-socios"); print("REPO", repo)
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))
WBS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wbs.csv"), encoding="utf-8").read()
EJ = "Ejecutiva: Laura Méndez"
PCT = {1: 0.1, 2: 0.3, 3: 0.5, 4: 0.7, 5: 0.9}          # conversión de la escala aprobada (paso 3)
usd = lambda n: f"{n:,.0f}".replace(",", ".")
def sanidad(repo, corte, etiqueta=None):
    out = run(E(f'sanidad.py --proyecto {G} --rapido --corte {corte}'), repo, ok=(0, 1, 2))
    if "REG-09" in out: REG09.append(corte)        # cortes en los que la sanidad avisa riesgos con la revisión vencida
    if etiqueta:                                   # consumo de la reserva tal como lo informa CAM-03 (para el gráfico)
        m = re.search(r"CAM-03 Reserva de riesgo[^\n]*?([\d.]+) de ([\d.]+)", out)
        if m: CAM.append((etiqueta, int(m.group(1).replace(".", "")), int(m.group(2).replace(".", ""))))
    return out

# ---- datos para los gráficos (visuales.py), siempre leídos de los registros reales del recorrido
import csv as _c
import visuales as V
OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
ABIERTOS = ("abierto", "en-seguimiento", "escalado")
CAM, TEND, REG09 = [], [], []
def filas_riesgos():
    return list(_c.DictReader(open(os.path.join(repo, G, "03-control/registros/riesgos.csv"), encoding="utf-8")))
def emv_resid(f):
    return float(f["impacto_monetario"] or 0) * PCT[int(f["probabilidad_residual"] or f["probabilidad"])]
def exposicion(etiqueta):
    """EMV actual y EMV residual planificado de las amenazas abiertas (riesgos.csv) en un corte."""
    am = [f for f in filas_riesgos() if f["tipo"] == "amenaza" and f["estado"] in ABIERTOS]
    actual = sum(float(f["valor_esperado"] or 0) for f in am)
    residual = sum(emv_resid(f) for f in am) if any(f["probabilidad_residual"] for f in am) else None
    TEND.append((etiqueta, actual, residual))
    LOG.append((f"(exposición de amenazas abiertas al {etiqueta}, desde riesgos.csv: suma de valor_esperado y del EMV residual planificado)",
                f"amenazas abiertas: {', '.join(f['id'] for f in am)}\nexposición actual (EMV): USD {usd(actual)}" + (f" · EMV residual planificado: USD {usd(residual)}" if residual is not None else " · sin respuestas todavía")))
    return actual, residual
def hallazgos(corte, codigo=None):
    """Hallazgos de la sanidad (sanidad.py --json) al corte, sin dejar rastro en la evidencia: para contar y graficar."""
    d = json.loads(run(E(f'sanidad.py --proyecto {G} --rapido --json --corte {corte}'), repo, mostrar=False, ok=(0, 1, 2))); LOG.pop()
    return [h for h in d["hallazgos"] if codigo is None or h["codigo"] == codigo]
def reg09(corte):
    """Lista completa de REG-09 (riesgo abierto con la revisión vencida) al corte: la salida de texto de la sanidad
    muestra cinco por código; la lista entera sale de sanidad.py --json. Días = corte − fecha de revisión prevista."""
    import datetime as _d
    v = []
    for h in hallazgos(corte, "REG-09"):
        m = re.search(r"Riesgo (R-\d{3}) abierto con la revisión vencida \((\d{4}-\d{2}-\d{2}); propietario: ([^)]*)\)", h["mensaje"])
        v.append((m.group(1), m.group(2), (_d.date.fromisoformat(corte) - _d.date.fromisoformat(m.group(2))).days, m.group(3)))
    LOG.append((f"(sanidad.py --rapido --json --corte {corte}: lista completa de REG-09, con los días desde la revisión prevista)",
                f"riesgos con la revisión vencida: {len(v)}\n" + "\n".join(f"{i}  revisión prevista {f} · {d} días · propietario {p}" for i, f, d, p in v)))
    return v

P("Paso 1 · Proyecto, junta y objetivos con tolerancias")
base_su(repo, "2026-10-20")
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
exposicion("03-nov")

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
    act(repo, "riesgos", R[k], respuesta=r, acciones=f"{acc} · costo USD {usd(costo)} · ΔEMV USD {usd(delta)}", probabilidad_residual=pr, impacto_residual=ir, disparador=disp, estado="en-seguimiento", fecha_revision="2026-12-15")
R["R7"] = reg(repo, "riesgos", fecha_identificacion="2026-11-04", autor="Martín Suárez", categoria="comercial", causa=f"La respuesta de {R['R3']} transfiere el riesgo con una penalidad con tope de USD 2.000 por mes",
              evento="El proveedor de SMS falla y la penalidad cobrada no cubre el costo del atraso", efecto="Costo del atraso no recuperado (WBS 3.1)", tipo="amenaza", probabilidad=2, impacto=3, impacto_monetario=6000,
              proximidad="mediano-plazo", respuesta="aceptar", acciones="aceptar: el correo como factor alternativo (respuesta de R-003) limita el atraso · costo USD 0", probabilidad_residual=2, impacto_residual=3,
              disparador="primera caída con penalidad menor que el costo del atraso", propietario="Diego Ferreira", ejecutor="Lucía Benítez", estado="en-seguimiento", fecha_revision="2026-12-15",
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
exposicion("04-nov")
am6 = [f for f in filas_riesgos() if f["tipo"] == "amenaza"]
inh = [dict(f, probabilidad="" if f["id"] == R["R7"] else f["probabilidad"]) for f in am6]   # el secundario nace con la respuesta
alt_i = sum(1 for f in am6 if f["id"] != R["R7"] and int(f["puntuacion"]) >= 15)
alt_r = sum(1 for f in am6 if int(f["probabilidad_residual"]) * int(f["impacto_residual"]) >= 15)
V.mapa_calor(inh, os.path.join(OUT, "g1-mapa-inherente-residual.png"),
             "Después de las respuestas, ninguna amenaza queda en zona alta" if alt_r == 0 else f"Después de las respuestas quedan {alt_r} amenazas en zona alta",
             f"Amenazas al 04/11 · inherente (taller del 29/10) frente a residual planificado · {R['R7']} es el secundario que crea la respuesta de {R['R3']}",
             "riesgos.csv (probabilidad, impacto, probabilidad_residual, impacto_residual)", residual_titulo="Residual")
ant = {f[0]: (0 if f[0] == R["R7"] else f[2]) for f in filas_j if f[1] != "explotar"}
res_ = {f[0]: f[3] for f in filas_j if f[1] != "explotar"}
ids6 = sorted(ant, key=lambda i: (-ant[i], i))
c_resp6 = sum(f[4] for f in filas_j)
V.barras_comparadas([f"{i} {'(secundario)' if i == R['R7'] else ''}".strip() for i in ids6], [[ant[i] for i in ids6], [res_[i] for i in ids6]],
                    os.path.join(OUT, "g1-exposicion-respuestas.png"),
                    f"Con USD {V.miles(c_resp6)} en respuestas, la exposición baja de {V.miles(sum(ant.values()))} a {V.miles(sum(res_.values()))}",
                    f"EMV por amenaza (USD) antes de responder y residual planificado · {R['R7']} no existía antes: lo crea la transferencia de {R['R3']}",
                    "riesgos.csv · justificación de respuestas del paso 6", nombres=["EMV antes de responder", "EMV residual planificado"])
LOG.append(("(gráficos del paso 6 → g1-mapa-inherente-residual.png y g1-exposicion-respuestas.png; datos)",
            f"zona alta inherente: {alt_i} · zona alta residual: {alt_r}\n" + "\n".join(f"{i}  antes {usd(ant[i]):>6}  residual {usd(res_[i]):>6}" for i in ids6)
            + f"\ntotal antes {usd(sum(ant.values()))} · total residual {usd(sum(res_.values()))} · costo de respuestas {usd(c_resp6)}"))

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
sanidad(repo, "2026-11-27", "27-nov · C-001 respuestas")
run(E(f'estado.py --proyecto {G} resumen'), repo)
for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
    art(repo, c, r)
puerta(repo, "autorizar-inicio", EJ, "2026-10-30", "--fin 2026-11-27")
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
puerta(repo, "autorizar-proyecto", EJ, "2026-11-27")
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "{EJ}"', repo, mostrar=False)
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26'), repo, mostrar=False)
art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
puerta(repo, "autorizar-etapa", EJ, "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=±10 %" "costo=±10 %"')

P("Paso 8 · Seguimiento en la etapa: revisión de riesgos del sprint (reevaluar, cerrar acciones, detectar vencidas)")
act(repo, "acciones", A2, estado="completada", fecha_cierre="2026-11-19")
act(repo, "acciones", A3, estado="completada", fecha_cierre="2026-11-24")
act(repo, "riesgos", R["R2"], probabilidad=2, notas=f"WBS 4.1 y 5.1 · producto Consola de operador · interesado {st['Sindicato de operadores']} · taller {A2} realizado: actitud mejoró", fecha_revision="2026-12-29")
act(repo, "riesgos", R["R6"], estado="cerrado", notas="WBS 3.2 · oportunidad aprovechada: generador reutilizado, ahorro 60 h", fecha_revision="2026-12-15")
for k in ("R1", "R3", "R4", "R5", "R7"):        # revisados en el sprint: próxima revisión en el sprint siguiente (cadencia de 14 días)
    act(repo, "riesgos", R[k], fecha_revision="2026-12-29")
run(E(f'registro.py --proyecto {G} resumen --corte 2026-12-15'), repo)
sanidad(repo, "2026-12-15")
exposicion("15-dic")

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
sanidad(repo, "2026-12-18", "18-dic · C-002 y C-003 sin R-###")
act(repo, "cambios", C3, decision="rechazado", estado="rechazado", decidido_por="Autoridad de cambio: Sofía Ramírez", fecha_decision="2026-12-18",
    notas="no responde a ningún riesgo: la reserva de riesgo no es una bolsa general; si hace falta, va como solicitud de cambio contra el presupuesto de cambio cuando la junta lo fije")
sanidad(repo, "2026-12-18", "18-dic · C-003 rechazado")

P("Paso 10 · Riesgo nuevo sobre la línea: hoja de riesgo, escalamiento a la junta y revisión del business case")
R8 = reg(repo, "riesgos", fecha_identificacion="2027-01-08", autor="Martín Suárez", categoria="externo", causa="El regulador anunció nueva norma de autenticación para servicios financieros", evento="La norma exige biometría para operaciones de préstamo (FR-6)", efecto="Rediseño del acceso y atraso del Release 2", tipo="amenaza", probabilidad=3, impacto=5, impacto_monetario=40000, proximidad="mediano-plazo", respuesta="escalar", propietario="Laura Méndez", ejecutor="Martín Suárez", estado="escalado", fecha_revision="2027-01-12", notas=f"WBS 3.1 y 3.3 · interesado {st['Unidad de cumplimiento']} · afecta el business case: decide la junta")
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
act(repo, "riesgos", R8, respuesta="reducir", acciones=f"análisis normativo con asesoría externa ({C4}); diseño de autenticación reforzada detrás de IdentityPort (AD-5) · costo USD 10.000 · ΔEMV USD 8.000", probabilidad_residual=2, impacto_residual=4, estado="en-seguimiento", fecha_revision="2027-01-26",
    notas=f"WBS 3.1 y 3.3 · interesado {st['Unidad de cumplimiento']} · hoja: 03-control/registros/{R8}-hoja-riesgo.md · decisión de la junta del 2027-01-12")
A4 = reg(repo, "acciones", fecha="2027-01-12", origen=R8, descripcion=f"Entregar a la junta el análisis normativo de la asesoría externa ({C4})", responsable="Martín Suárez", fecha_compromiso="2027-02-05", prioridad="alta")
art(repo, "business-case", "00-direccion/business-case.md", version="1.1", texto=f"""# Business case

B-01 desvío de consultas (SM-2); B-02 adopción (SM-1).

## Revisión 2027-01-12 por {R8} (norma de biometría)
- Escenario adverso: costo adicional de hasta USD 40.000 y atraso del Release 2; B-02 (adopción) podría demorarse un trimestre.
- Con la respuesta aprobada (análisis normativo, {C4}, USD 10.000 de la reserva de riesgo) el caso sigue siendo viable:
  la junta mantiene el proyecto y vuelve a revisar {R8} y este caso en la próxima reunión.
""")
run(E(f'estado.py --proyecto {G} aprobar business-case --por "{EJ}" --version 1.1 --fecha 2027-01-12'), repo)
sanidad(repo, "2027-01-12", "12-ene · C-004 análisis normativo")
exposicion("12-ene")

P("Paso 11 · Informe de riesgos e insumo para el highlight")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-01-15'), repo)
sanidad(repo, "2027-01-15")
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)
art(repo, "informe-riesgos-2027-01-15", "03-control/reportes/2027-01-15-informe-riesgos.md")

P("Paso 12 · Revisión periódica del registro: riesgos sin revisar, una respuesta vencida y un disparador alcanzado")
run(E(f'estado.py --proyecto {G} contexto --corte 2027-02-12'), repo)   # lo que el hook de inicio pone en la sesión
sanidad(repo, "2027-02-12")                      # lo que encuentra la revisión cuando el registro quedó quieto un mes
venc12 = reg09("2027-02-12")
abiertos12 = [f for f in filas_riesgos() if f["estado"] in ABIERTOS]
corto = {R[k]: n for k, n in (("R1", "padrón sin entorno de pruebas"), ("R2", "resistencia a la consola"), ("R3", "disponibilidad del SMS"),
                                ("R4", "Ley 18.331 y constancias"), ("R5", "rotación del equipo"), ("R6", "reutilizar el PDF"),
                                ("R7", "secundario de la penalidad del SMS"))}; corto[R8] = "norma de biometría"
dias = [d for _, _, d, _ in venc12]
sprints = lambda d: f"más de {d // 14} sprint{'s' if d // 14 > 1 else ''} de 14 días" if d >= 14 else "menos de un sprint"
V.estados([(f"{i} · {corto[i]}", d, "critico" if d > 28 else "serio" if d > 14 else "atencion", sprints(d))
           for i, _, d, _ in sorted(venc12, key=lambda v: (-v[2], v[0]))],
          os.path.join(OUT, "g1-revisiones-vencidas.png"),
          (f"Al 12/02, los {len(venc12)} riesgos abiertos llevan entre {min(dias)} y {max(dias)} días sin revisar" if len(venc12) == len(abiertos12)
           else f"Al 12/02, {len(venc12)} de {len(abiertos12)} riesgos abiertos tienen la revisión vencida"),
          f"Días entre la revisión prevista (fecha_revision) y el corte · la sanidad lo avisa con REG-09 desde el {REG09[0][8:]}/{REG09[0][5:7]}",
          "sanidad.py --json --corte 2027-02-12 (REG-09) · riesgos.csv", maximo=15 * (max(dias) // 15 + 1), decimales=0, sufijo=" días")
act(repo, "issues", I1, estado="resuelto", fecha_cierre="2027-02-10", decision="entorno de pruebas habilitado el 2027-02-08")
act(repo, "acciones", A4, fecha_compromiso="2027-02-26", notas="replanificada en la revisión del 2027-02-12: la asesoría externa pidió dos semanas más; la junta revisa R-008 el 2027-03-01")
act(repo, "riesgos", R["R3"], probabilidad=4, fecha_revision="2027-02-26", notas="WBS 3.1 · producto Portal del socio · origen: prd.md:249 y ARCHITECTURE-SPINE.md:177 (BMAD) y ronda 2026-10-27 [00:00:46] · seguimiento: jira:PS-104 (proveedor alternativo) · disparador alcanzado: caídas del proveedor de SMS el 2027-01-20 y el 2027-02-03")
for k in ("R2", "R4", "R5", "R7"):
    act(repo, "riesgos", R[k], fecha_revision="2027-02-26")
act(repo, "riesgos", R8, fecha_revision="2027-02-26")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-02-12'), repo)
sanidad(repo, "2027-02-12")
exposicion("12-feb")

P("Paso 13 · La reserva como presupuesto vivo: contingencia de R-003, alerta al 80 % y decisión de la ejecutiva")
C5 = reg(repo, "cambios", fecha="2027-02-15", solicitante="Martín Suárez", titulo=f"Proveedor de SMS alternativo en paralelo durante 6 meses (contingencia de {R['R3']}, disparador alcanzado)",
         descripcion="contrato con el proveedor evaluado en jira:PS-104 como respaldo activo del segundo factor, con conmutación ante caídas",
         justificacion=f"disparador de {R['R3']} alcanzado (dos caídas en un mes): sin respaldo queda en P4 × I5 = 20", impacto_costo="11.000", impacto_riesgo=f"responde a {R['R3']} (residual P2 I3)",
         decision="aprobado", decidido_por=EJ, fecha_decision="2027-02-15", estado="aprobado", costo=11000, cargo="reserva-riesgo",
         notas="supera los USD 5.000 que el enfoque de riesgo delega en el gestor: decide la ejecutiva")
act(repo, "riesgos", R["R3"], acciones=f"SLA de 99,9 % con penalidad y correo como factor alternativo · costo USD 2.500 · contingencia activada ({C5}): proveedor de SMS alternativo en paralelo · costo USD 11.000", probabilidad_residual=2, impacto_residual=3)
sanidad(repo, "2027-02-15", "15-feb · C-005 contingencia R-003")
usado13, tope13 = CAM[-1][1], CAM[-1][2]
am13 = [f for f in filas_riesgos() if f["tipo"] == "amenaza" and f["estado"] in ABIERTOS]
LOG.append(("(pm-riesgos: remanente de la reserva frente al EMV residual planificado de las amenazas abiertas, desde estado.json, cambios.csv y riesgos.csv)",
            f"presupuesto {usd(tope13)} · consumido {usd(usado13)} ({100 * usado13 / tope13:.0f} %) · remanente {usd(tope13 - usado13)}\n"
            + "\n".join(f"{f['id']}  EMV residual {usd(emv_resid(f)):>6}" for f in am13) + f"\nEMV residual planificado de las amenazas abiertas: {usd(sum(emv_resid(f) for f in am13))}"))
reg(repo, "decisiones", fecha="2027-02-15", decision=f"Mantener el presupuesto de riesgo en {usd(tope13)}; hasta el límite de etapa todo nuevo uso de la reserva lo decide la ejecutiva (se suspende la delegación de USD 5.000 al gestor)",
    contexto=f"AVISO CAM-03: reserva de riesgo al {100 * usado13 / tope13:.0f} % tras {C5}; remanente {usd(tope13 - usado13)} frente a un EMV residual de {usd(sum(emv_resid(f) for f in am13))}",
    opciones_consideradas="ampliar el presupuesto de riesgo con reserva de gestión · mantenerlo y concentrar la autoridad · pedir plan de excepción",
    decidido_por=EJ, nivel="ejecutivo", revisar_en="2027-03-01", artefactos_afectados="02-planificacion/enfoques/enfoque-riesgo.md §7")
run(E(f'estado.py --proyecto {G} resumen'), repo)

P("Paso 14 · Límite de etapa: auditoría de riesgos, lecciones y cierre de riesgos")
run(E(f'estado.py --proyecto {G} limite-etapa'), repo)
act(repo, "acciones", A4, estado="completada", fecha_cierre="2027-02-26")
act(repo, "riesgos", R["R5"], estado="retirado", notas="WBS 1.1 · equipo estable durante la etapa", fecha_revision="2027-03-01")
act(repo, "riesgos", R["R3"], probabilidad=2, fecha_revision="2027-03-15")
act(repo, "riesgos", R8, probabilidad=2, fecha_revision="2027-03-15", notas=f"WBS 3.1 y 3.3 · interesado {st['Unidad de cumplimiento']} · hoja: 03-control/registros/{R8}-hoja-riesgo.md · decisión de la junta del 2027-01-12 · análisis normativo ({A4}): la biometría se exigiría desde 2028, después del Release 2")
for k in ("R2", "R4", "R7"):
    act(repo, "riesgos", R[k], fecha_revision="2027-03-15")
reg(repo, "lecciones", fecha="2027-03-01", etapa="2", categoria="riesgo", situacion=f"{R['R1']} se materializó: el entorno de pruebas del núcleo dependía de otra área", efecto=f"USD 8.000 de la reserva de riesgo ({C2}) y 3 días de atraso en WBS 3.2 (sin el entorno temporal, 2 semanas)", recomendacion="exigir el entorno de pruebas como condición de la puerta autorizar-etapa", prioridad="alta", responsable_seguimiento="Martín Suárez")
reg(repo, "lecciones", fecha="2027-03-01", etapa="2", categoria="riesgo", situacion=f"La revisión de riesgos del 2026-12-29 no se hizo; la sanidad lo avisó con REG-09 desde el {REG09[0]} y la revisión se postergó hasta el 2027-02-12 porque la junta y el issue de {R['R1']} ocuparon las revisiones del sprint", efecto=f"el disparador de {R['R3']} se alcanzó sin que nadie lo mirara y la acción {A4} venció sin replanificar; la contingencia ({C5}) llevó la reserva al {100 * usado13 / tope13:.0f} %", recomendacion="empezar cada revisión de sprint por los REG-09 de la sanidad del día y no cerrarla con riesgos de revisión vencida, aunque haya urgencias", prioridad="alta", responsable_seguimiento="Martín Suárez")
art(repo, "auditoria-riesgos-2027-03-01", "03-control/reportes/2027-03-01-auditoria-riesgos.md")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-03-01'), repo)
run(E(f'estado.py --proyecto {G} cumplir-condiciones decision-ad-hoc --fecha 2027-03-01 --por "{EJ}" --nota "{R8} revisado en la junta; análisis normativo entregado ({C4})"'), repo)
run(E(f'puertas.py --proyecto {G} verificar autorizar-etapa'), repo, ok=(0, 1, 2))
run(E(f'exportar.py xlsx --proyecto {G}'), repo, ok=(0, 1))
fin = sanidad(repo, "2027-03-01", "01-mar · fin de etapa")
venc = hallazgos("2027-03-01", "REG-09")
exp_fin, _ = exposicion("01-mar")
rs = json.loads(run(E(f'registro.py --proyecto {G} resumen --json --corte 2027-03-01'), repo, mostrar=False)); LOG.pop()   # solo para las tarjetas
filas = list(_c.DictReader(open(os.path.join(repo, G, "03-control/registros/riesgos.csv"), encoding="utf-8")))
LOG.append(("(riesgos.csv al cierre de la etapa: id, tipo, P×I, residual, EMV, respuesta, estado)", "\n".join(f"{f['id']} {f['tipo'][:4]} P{f['probabilidad']}×I{f['impacto']}={f['puntuacion']:>3} res P{f['probabilidad_residual']}×I{f['impacto_residual']} EMV {f['valor_esperado']:>7} {f['respuesta']:10s} {f['estado']}" for f in filas)))
# gráficos de la etapa (datos de la corrida: CAM-03 de cada sanidad, exposición por corte, sanidad y resumen del 01/03)
cam_g = [c for c in CAM if not c[0].startswith("01-mar")]
V.consumo(cam_g, os.path.join(OUT, "g1-consumo-reserva.png"),
          f"La reserva llegó al {100 * cam_g[-1][1] / cam_g[-1][2]:.0f} % y la sanidad avisó antes de agotarse",
          f"Consumo acumulado de la reserva de riesgo (USD) en cada corrida de la sanidad · tope fijado por la ejecutiva: {V.miles(cam_g[-1][2])}",
          "sanidad CAM-03 · cambios.csv (cargo=reserva-riesgo) · estado.json presupuestos.riesgo")
V.lineas([t[0] for t in TEND], [[t[1] for t in TEND], [t[2] for t in TEND]], os.path.join(OUT, "g1-exposicion-tendencia.png"),
         "La exposición rozó la tolerancia en febrero" if max(t[1] for t in TEND) >= 0.9 * 60000 else "La exposición se mantuvo lejos de la tolerancia",
         f"Amenazas abiertas (USD) en cada revisión · cerró la etapa en {V.miles(exp_fin)}",
         "riesgos.csv en cada corte (valor_esperado, probabilidad_residual)", nombres=["EMV actual", "EMV residual planificado"],
         referencia=(60000, "Tolerancia 60.000"))
h_fin = hallazgos("2027-03-01"); reg06 = sum(h["codigo"] == "REG-06" for h in h_fin); est12 = sum(h["codigo"] == "EST-12" for h in h_fin); venc_acc = len(rs["acciones"]["vencidas"])
pct_fin = 100 * CAM[-1][1] / CAM[-1][2]
V.tarjetas([(V.miles(exp_fin), "Exposición de amenazas", "tolerancia USD 60.000", "bien" if exp_fin < 0.8 * 60000 else "atencion"),
            (f"{pct_fin:.0f} %", "Reserva de riesgo consumida", f"{V.miles(CAM[-1][1])} de {V.miles(CAM[-1][2])}", "atencion" if pct_fin >= 80 else "bien"),
            (str(rs["riesgos"]["altos_abiertos"]), "Riesgos altos abiertos", f"REG-06: {reg06} sin respuesta", "bien" if reg06 == 0 else "critico"),
            (str(venc_acc), "Acciones vencidas", "REG-07 al corte", "bien" if venc_acc == 0 else "serio"),
            (str(len(venc)), "Riesgos con la revisión vencida", "REG-09 al corte", "bien" if not venc else "serio"),
            (str(est12), "Condiciones de la junta abiertas", "EST-12", "bien" if est12 == 0 else "serio")],
           os.path.join(OUT, "g1-tarjetas-etapa.png"), "Fin de la etapa 2: exposición bajo la tolerancia y reserva bajo vigilancia",
           "Indicadores de riesgo al 01/03/2027, límite de la etapa 2 \"Release 1\"", "sanidad --corte 2027-03-01 · registro.py resumen · riesgos.csv")
LOG.append(("(gráficos de la etapa → g1-consumo-reserva.png, g1-exposicion-tendencia.png y g1-tarjetas-etapa.png; datos)",
            "consumo de la reserva (CAM-03):\n" + "\n".join(f"  {e}: {usd(u)} de {usd(t)} ({100 * u / t:.0f} %)" for e, u, t in CAM)
            + "\nexposición por corte (actual · residual planificado):\n" + "\n".join(f"  {e}: {usd(a)} · {usd(r) if r is not None else '—'}" for e, a, r in TEND)
            + f"\ntarjetas: exposición {usd(exp_fin)} · reserva {pct_fin:.0f} % · altos abiertos {rs['riesgos']['altos_abiertos']} (sin respuesta {reg06}) · acciones vencidas {venc_acc} · revisiones vencidas {len(venc)} · condiciones abiertas {est12}"))
P("Paso 15 · Variante sin BMAD: destilar riesgos de los artefactos del proyecto")
base2 = os.path.join(os.path.dirname(repo), "portal-sin-bmad"); os.makedirs(base2)
run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Portal de socios (sin BMAD)" --ejecutivo "Laura Méndez" --gestor "Martín Suárez" --fecha 2026-10-28'), base2)
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
