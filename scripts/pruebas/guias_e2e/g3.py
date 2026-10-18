"""Guía E2E-3 · Interesados (maestro, matriz poder/interés, estereotipos, preferencias, RACI), comunicaciones personalizadas
y su envío por la capa de canales, OKR con check-ins y salud, y reporte de avance (scripts reales + tablero)."""
from comun import *
import glob
repo = proyecto("portal-socios"); print("REPO", repo)
OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))
I = lambda sub: f'python3 {IN} --proyecto {G} {sub}'
V = lambda sub: f'python3 {EV} --proyecto {G} {sub}'

def puerta_f(repo, tipo, por, fecha, extra="", decision="aprobado"):
    """Como comun.puerta, con --fecha en la lista y su confirmación (archivo de verificación con la fecha del paso, no la de la corrida)."""
    run(E(f'puertas.py --proyecto {G} verificar {tipo}'), repo, ok=(0, 1, 2))
    run(E(f'puertas.py --proyecto {G} lista {tipo} --fecha {fecha}'), repo, mostrar=False)
    run(E(f'puertas.py --proyecto {G} confirmar {tipo} --por "{por}" --fecha {fecha}'), repo)
    return run(E(f'estado.py --proyecto {G} puerta {tipo} --decision {decision} --por "{por}" --fecha {fecha} {extra}'), repo)

def hasta_etapa2_f(repo):
    """Como comun.hasta_etapa2, sin reescribir el business case (el del paso 6, con B-01…B-03) y con fechas deterministas."""
    for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"),
                 ("business-case-esquematico", "00-direccion/business-case-esquematico.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
        art(repo, c, r)
    puerta_f(repo, "autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")
    art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
    run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "riesgo=ningún riesgo alto sin respuesta" "beneficios=-10 %"'), repo, mostrar=False)
    puerta_f(repo, "autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
    run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"', repo, mostrar=False)
    run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado CONCERNS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26 --nota "NFR-3 sin prueba de carga planificada"'), repo, mostrar=False)
    art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
    puerta_f(repo, "autorizar-etapa", "Ejecutivo: Laura Méndez", "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=+2 semanas" "costo=±10 %"', decision="condicionado")

P("Paso 1 · Proyecto y junta")
base_su(repo)

P("Paso 2 · Identificar y valorar a los interesados (maestro único)")
ST = {}
for n, ro, rp, pod, inte, act_, des, canal, frec, resp, conf, correo, chat in [
  ("Laura Méndez", "Gerenta de operaciones", "Ejecutiva", "alto", "alto", "lider", "lider", "reunión 1:1", "quincenal", "Martín Suárez", "no", "laura.mendez@example.org", ""),
  ("Consejo directivo", "Órgano de gobierno de la cooperativa", "Capa de negocio", "alto", "medio", "partidario", "lider", "correo", "trimestral", "Laura Méndez", "no", "consejo@example.org", ""),
  ("Sofía Ramírez", "Jefa de atención al socio", "Usuaria sénior y PO", "alto", "alto", "lider", "lider", "sprint review", "quincenal", "Martín Suárez", "no", "sofia.ramirez@example.org", "sofia.ramirez@example.org"),
  ("Sindicato de operadores", "Representación de operadores de sucursal", "Afectado", "medio", "alto", "resistente", "neutral", "taller presencial", "mensual", "Sofía Ramírez", "si", "delegado.sindical@example.org", ""),
  ("Socios usuarios piloto", "Panel de 40 socios", "Usuarios finales", "bajo", "alto", "desconocedor", "partidario", "encuesta y boletín", "mensual", "Sofía Ramírez", "no", "panel.socios@example.org", ""),
  ("Área de TI del núcleo operativo", "Dueña del core y del padrón", "Proveedor interno", "alto", "medio", "neutral", "partidario", "reunión técnica", "semanal", "Lucía Benítez", "no", "", ""),
  ("Unidad de cumplimiento", "Protección de datos", "Asesor", "alto", "bajo", "neutral", "partidario", "correo y revisión", "por hito", "Andrea Costa", "no", "cumplimiento@example.org", ""),
  ("Diego Ferreira", "Gerente del proveedor", "Proveedor sénior", "medio", "alto", "partidario", "partidario", "reunión de junta", "mensual", "Martín Suárez", "no", "diego.ferreira@example.org", ""),
  ("Martín Suárez", "Gestor del proyecto", "Gestor", "medio", "alto", "lider", "lider", "checkpoint", "semanal", "Laura Méndez", "no", "martin.suarez@example.org", "martin.suarez@example.org"),
  ("Lucía Benítez", "Jefa de equipo del proveedor", "Jefa de equipo", "bajo", "alto", "partidario", "partidario", "daily", "diaria", "Martín Suárez", "no", "lucia.benitez@example.org", "")]:
    ST[n] = reg(repo, "stakeholders", nombre=n, rol_organizacion=ro, rol_proyecto=rp, poder=pod, interes=inte, actitud=act_, nivel_compromiso_actual=act_,
                nivel_compromiso_deseado=des, canal=canal, frecuencia=frec, responsable_relacion=resp, confidencial=conf, correo=correo, usuario_chat=chat)
run(E(f'registro.py --proyecto {G} listar stakeholders'), repo)

P("Paso 3 · Matriz poder/interés y estrategia por cuadrante")
run(I("matriz"), repo)
art(repo, "analisis-stakeholders", "01-inicio/analisis-stakeholders.md")

P("Paso 4 · Estereotipos y preferencias declaradas en una entrevista")
run(I("estereotipos --semilla"), repo)
for n, et in (("Laura Méndez", "ET-001"), ("Consejo directivo", "ET-001"), ("Sofía Ramírez", "ET-006"), ("Socios usuarios piloto", "ET-003"),
              ("Unidad de cumplimiento", "ET-005"), ("Diego Ferreira", "ET-004"), ("Martín Suárez", "ET-002"), ("Lucía Benítez", "ET-002")):
    act(repo, "stakeholders", ST[n], estereotipo=et)
run(I("estereotipos"), repo)
escribir(repo, "01-inicio/entrevistas/2026-11-03-laura-mendez.md", "---\ntipo: entrevista-interesado\nestado: borrador\nconfidencial: si\ninteresado: ST-001\n---\n\n"
         "# Entrevista de interesado · ST-001 Laura Méndez\n\nAcepta que se registren sus preferencias: si\n\n"
         "- canal: «Prefiero que el avance me llegue por correo, no por chat.» → correo\n"
         "- formato y nivel: «Una página, con la conclusión y lo que tengo que decidir arriba.» → conclusion-primero · ejecutivo\n"
         "- horario: «Los lunes antes de las 9 lo leo con calma.» → antes de las 9\n")
PF = {}
for dim, val, cita in (("canal", "correo", "«Prefiero que el avance me llegue por correo, no por chat.»"),
                       ("formato", "conclusion-primero", "«Una página, con la conclusión y lo que tengo que decidir arriba.»"),
                       ("nivel_detalle", "ejecutivo", "«Una página, con la conclusión y lo que tengo que decidir arriba.»"),
                       ("horario", "antes de las 9", "«Los lunes antes de las 9 lo leo con calma.»")):
    PF[dim] = reg(repo, "preferencias", fecha="2026-11-03", stakeholder_id=ST["Laura Méndez"], dimension=dim, valor=val, procedencia="declarado",
                  evidencia=cita, fuente="01-inicio/entrevistas/2026-11-03-laura-mendez.md", vigencia_hasta="2027-05-02")
run(I(f'confirmar {" ".join(PF.values())} --por "Gestor: Martín Suárez"'), repo)
run(I(f'perfil {ST["Laura Méndez"]} --corte 2026-11-03'), repo)

P("Paso 5 · Plan de compromiso, enfoque de comunicación y matriz de comunicaciones")
art(repo, "plan-compromiso-stakeholders", "02-planificacion/plan-compromiso-stakeholders.md")
art(repo, "enfoque-comunicacion", "02-planificacion/enfoques/enfoque-comunicacion.md")
art(repo, "matriz-comunicaciones", "02-planificacion/matriz-comunicaciones.md")
A = {}
A["taller"] = reg(repo, "acciones", fecha="2026-11-02", origen=ST["Sindicato de operadores"], descripcion="Taller de co-diseño de la bandeja con operadores y delegado sindical", responsable="Sofía Ramírez", fecha_compromiso="2026-11-20", prioridad="alta")
A["boletin"] = reg(repo, "acciones", fecha="2026-11-02", origen=ST["Socios usuarios piloto"], descripcion="Boletín 1 al panel de socios: qué es el portal y cómo participar del piloto", responsable="Sofía Ramírez", fecha_compromiso="2026-12-01", prioridad="media")
A["consejo"] = reg(repo, "acciones", fecha="2026-11-02", origen=ST["Consejo directivo"], descripcion="Informe ejecutivo trimestral al Consejo con OKR y riesgos", responsable="Laura Méndez", fecha_compromiso="2027-01-15", prioridad="media")

P("Paso 6 · Beneficios del business case, enfoque de beneficios y OKR ligados (B-n, SM-n), con tipos de KR, compromiso, peso e iniciativas")
art(repo, "business-case", "00-direccion/business-case.md", texto="# Business case\n\n## 5. Beneficios esperados\n\n"
    "- B-01 desvío de consultas a canales digitales (SM-2): de 5.000 a 4.000 consultas/mes de saldo y constancias por canales tradicionales (−20 %) al 2027-12-31.\n"
    "- B-02 adopción del portal (SM-1): 25 % de socios activos registrados al 2027-12-31.\n"
    "- B-03 respuesta de préstamos simples en menos de 48 h hábiles (SM-3): de 96 h a 48 h al 2027-06-30.\n\nTolerancia de beneficios: −10 % sobre cada beneficio.\n")
escribir(repo, "00-direccion/enfoque-beneficios.md", """---
tipo: enfoque-beneficios
proyecto: "Portal de autoservicio para socios"
version: 0.1
fecha: "2026-11-20"
autor: "Martín Suárez"
estado: en-revision
aprobado_por: ""
idioma: "es"
---

# Enfoque de gestión de beneficios — Portal de autoservicio para socios

**Gestionado por:** proyecto hasta el cierre; después, el área de atención al socio (Sofía Ramírez, usuaria sénior).

## 1. Alcance
**Beneficios gestionados y medidos:** B-01, B-02 y B-03 del business case (sección 5).
**Resultados que los habilitan:** socios que se registran y consultan en el portal (R1); operadores que resuelven en la bandeja única (R1).

## 2. Beneficios: medición y responsabilidad

| Id | Beneficio | Dueño | Medida | Línea base y fecha | Meta | Fecha prevista | Método | Frecuencia | Tolerancia | Refs SM / KR |
|---|---|---|---|---|---|---|---|---|---|---|
| B-01 | Desvío de consultas a canales digitales | Sofía Ramírez | consultas/mes de saldo y constancias por canales tradicionales | 5.000 (2026-11) | 4.000 (−20 %) | 2027-12-31 | conteo del sistema de atención | mensual desde R1 | −10 % (≥ 900 desviadas) | SM-2 · KR-1.2 (aspiracional: 3.500) |
| B-02 | Adopción del portal | Sofía Ramírez | % de socios activos registrados | 0 % (2026-11) | 25 % | 2027-12-31 | padrón y registro del portal | mensual desde R1 | −10 % (≥ 22,5 %) | SM-1 · KR-1.1 (aspiracional: 30 %) |
| B-03 | Préstamos simples respondidos en menos de 48 h | Sofía Ramírez | horas hábiles promedio de respuesta | 96 h (2026-11) | 48 h | 2027-06-30 | tiempo ingreso → respuesta en la bandeja | mensual desde la bandeja | −10 % (≤ 52,8 h) | SM-3 · KR-2.1, KR-2.2, KR-2.3 |

Los OKR complementan, no reemplazan, estos beneficios: los KR fijan metas de ciclo (aspiracionales o comprometidas) y se
revisan con check-ins; los B-n son el compromiso del business case, con tolerancia de la junta y revisiones que siguen
después del cierre.

## 3. Procedimientos de realización
**Durante el proyecto:** piloto con el panel de socios, boletines, taller con operadores, formación en la bandeja.
**Tras el cierre:** medición mensual de B-01…B-03 por atención al socio; retiro gradual de la constancia en papel.
**Barreras:** baja respuesta del panel (riesgo a registrar), resistencia sindical a la medición individual.

## 4. Revisiones de beneficios

| Revisión | Momento | Beneficios | Quién confirma | Entrada | Salida |
|---|---|---|---|---|---|
| Highlight | cada highlight report | pronóstico de B-01…B-03 contra la tolerancia | gestor | OKR, avance, cronograma | fila Beneficios del highlight |
| Fin de etapa | cada fin de etapa | previsión de todos | usuaria sénior | caso actualizado, mediciones | veredicto en el informe de fin de etapa |
| Cierre | autorizar-cierre | realizados hasta la fecha | usuaria sénior | informe de fin de proyecto | traspaso al negocio |
| Post-proyecto 1 | 2027-12-31 | B-01, B-02, B-03 | usuaria sénior | mediciones en operación | acciones correctivas, lecciones |

## 6. Responsabilidades
Ejecutiva (Laura Méndez): asegura que las revisiones se planifiquen. Usuaria sénior (Sofía Ramírez): rinde cuentas de la
realización. Gestor (Martín Suárez): mantiene este enfoque hasta el cierre.

## 7. Recursos y financiación
Durante el proyecto: tablero del portal y reportes del sistema de atención. Después del cierre: presupuesto operativo de atención al socio.
""")
art(repo, "enfoque-beneficios", "00-direccion/enfoque-beneficios.md")
okr = """id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas,tipo_kr,compromiso,peso,padre_id,nivel,ciclo,fecha_inicio,estado,ref_externa
O-1,objetivo,,Los socios resuelven sus gestiones simples sin ir a la sucursal,,,,,,ST-001,2027-12-31,OBJ-1,,,,aspiracional,,,proyecto,2027,2026-11-02,activo,
KR-1.1,kr,O-1,30 % de socios activos registrados en el portal,% socios registrados,0,30,0,%,ST-003,2027-12-31,B-02; SM-1,6,,de-a,,2,,,,,activo,tability:kr-registro-portal
KR-1.2,kr,O-1,Bajar 30 % las consultas de saldo y constancias por canales tradicionales,consultas/mes,5000,3500,5000,consultas,ST-003,2027-12-31,B-01; SM-2,5,,de-a,,1,,,,,activo,
O-2,objetivo,,Los préstamos simples se resuelven rápido y sin papeles,,,,,,ST-001,2027-12-31,OBJ-2,,,,comprometido,,,proyecto,2027,2026-11-02,activo,
KR-2.1,kr,O-2,Respuesta a solicitudes simples en menos de 48 h hábiles,horas,96,48,96,horas,ST-003,2027-12-31,B-03; SM-3,6,,mantener-bajo,,1,,,,,activo,
KR-2.2,kr,O-2,Más del 90 % de las solicitudes llegan completas,% completas,60,90,60,%,ST-003,2027-12-31,B-03; SM-3,7,,de-a,,1,,,,,activo,
KR-2.3,kr,O-2,Bandeja única de solicitudes en producción para los operadores,hito,,,,,ST-003,2027-03-12,B-03; SM-3,,,hito,,1,,,,,activo,
IN-1,iniciativa,KR-2.3,Acceso y roles de la consola de operador,,,,,,ST-010,,3-1-acceso-y-roles-de-la-consola-de-operador,,,,,1,,,,,activo,
IN-2,iniciativa,KR-2.3,Bandeja única de solicitudes,,,,,,ST-010,,3-2-bandeja-única-de-solicitudes,,,,,1,,,,,activo,
IN-3,iniciativa,KR-2.3,Resolución de solicitudes,,,,,,ST-010,,3-3-resolución-de-solicitudes,,,,,1,,,,,activo,
"""
escribir(repo, "00-direccion/okr.csv", okr)
art(repo, "okr", "00-direccion/okr.md")
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2026-11-20', repo)
run(E(f'sanidad.py --proyecto {G} --rapido --corte 2026-11-20'), repo, ok=(0, 1, 2))

P("Paso 7 · RACI sobre la WBS, la especificación (épicas y requisitos) y los KR; integridad del maestro")
escribir(repo, "02-planificacion/wbs.csv", open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wbs.csv"), encoding="utf-8").read())
for el, filas in (("E-1", (("Sofía Ramírez", "A"), ("Lucía Benítez", "R"), ("Área de TI del núcleo operativo", "C"), ("Laura Méndez", "I"))),
                  ("E-3", (("Sofía Ramírez", "A"), ("Lucía Benítez", "R"), ("Sindicato de operadores", "C"), ("Diego Ferreira", "C"))),
                  ("NFR-1", (("Unidad de cumplimiento", "A"), ("Lucía Benítez", "R"), ("Sofía Ramírez", "C"))),
                  ("3.1", (("Martín Suárez", "A"), ("Lucía Benítez", "R"), ("Sofía Ramírez", "I"))),
                  ("KR-1.1", (("Laura Méndez", "A"), ("Sofía Ramírez", "R"), ("Socios usuarios piloto", "C"), ("Consejo directivo", "I"))),
                  ("KR-2.2", (("Laura Méndez", "A"), ("Sofía Ramírez", "R"), ("Consejo directivo", "I")))):
    for n, rol in filas: reg(repo, "raci", elemento=el, stakeholder_id=ST[n], rol=rol)
r = subprocess.run(f'python3 {EST}/registro.py --proyecto {G} agregar raci --campo elemento=E-1 --campo stakeholder_id={ST["Laura Méndez"]} --campo rol=A', shell=True, cwd=repo, capture_output=True, text=True)
LOG.append((f'$EST/registro.py --proyecto {G} agregar raci --campo elemento=E-1 --campo stakeholder_id={ST["Laura Méndez"]} --campo rol=A   # segundo A: se rechaza', (r.stdout + r.stderr).strip()))
run(I("raci --markdown gestion/02-planificacion/matriz-raci.md"), repo)
art(repo, "matriz-raci", "02-planificacion/matriz-raci.md")
run(I("raci --elemento E-3"), repo)
run(I("integridad"), repo)
hasta_etapa2_f(repo)

P("Paso 8 · Taller con interesados → acta, decisiones, acciones y preferencias declaradas")
vtt = """WEBVTT

00:00:01.000 --> 00:00:09.000
<v Sofía Ramírez>Buen día, este es el taller de la bandeja única con operadores. A mí mandame las novedades del proyecto por Teams.

00:00:10.000 --> 00:00:21.000
<v Delegado sindical>Nos preocupa que la bandeja se use para medir productividad individual. Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas.

00:00:22.000 --> 00:00:34.000
<v Martín Suárez>Propongo que el tablero de la bandeja muestre solo métricas del equipo, no por persona. Lo registro como decisión del product owner si Sofía está de acuerdo.

00:00:35.000 --> 00:00:42.000
<v Sofía Ramírez>De acuerdo. Y Lucía prepara el prototipo con ese criterio para el 11 de diciembre.

00:00:43.000 --> 00:00:50.000
<v Lucía Benítez>Confirmado, prototipo el 11 de diciembre.
"""
escribir(repo, "03-control/reuniones/2026-11-19-taller-bandeja-original.vtt", vtt)
LOG.append(("(transcripción de ejemplo: copiala a gestion/03-control/reuniones/2026-11-19-taller-bandeja-original.vtt)", vtt.strip()))
run(f'python3 {RAIZ}/skills/pm-reuniones/scripts/transcripcion.py {G}/03-control/reuniones/2026-11-19-taller-bandeja-original.vtt --salida {G}/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md', repo)
reg(repo, "decisiones", fecha="2026-11-19", decision="El tablero de la bandeja muestra métricas del equipo, no individuales", contexto=f"taller con {ST['Sindicato de operadores']}", decidido_por="Product owner: Sofía Ramírez", nivel="product-owner")
A["proto"] = reg(repo, "acciones", fecha="2026-11-19", origen="acta-2026-11-19-taller-bandeja", descripcion="Prototipo de bandeja con métricas de equipo", responsable="Lucía Benítez", fecha_compromiso="2026-12-11", prioridad="alta")
act(repo, "acciones", A["taller"], estado="completada", fecha_cierre="2026-11-19")
act(repo, "stakeholders", ST["Sindicato de operadores"], nivel_compromiso_actual="neutral", notas="taller 2026-11-19: acuerdo sobre métricas de equipo")
run(I(f'proponer --transcripcion {G}/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md --mapa "Delegado sindical={ST["Sindicato de operadores"]}" --fecha 2026-11-19 --registrar'), repo)
props = [f for f in csv.DictReader(open(os.path.join(repo, G, "03-control/registros/preferencias.csv"), encoding="utf-8")) if f["estado"] == "propuesta"]
run(I(f'confirmar {" ".join(f["id"] for f in props)} --por "Gestor: Martín Suárez"'), repo)
run(I(f'perfil {ST["Sindicato de operadores"]} --corte 2026-11-19'), repo)
act(repo, "stakeholders", ST["Sindicato de operadores"], frecuencia="quincenal")
art(repo, "comunicado-operadores", "03-control/reportes/2026-11-21-comunicado-bandeja.md")

P("Paso 9 · Avance de la etapa: serie EVM, avance BMAD, check-ins de OKR y registros a la fecha de corte")
escribir(repo, "03-control/reportes/progreso.csv", "periodo,pv,ev,ac,notas\n2026-12-11,15000,14200,15000,sprint 1\n2026-12-23,30000,28000,29600,sprint 2\n2027-01-08,45000,42000,44600,sprint 3\n")
run(E(f'evm.py --csv {G}/03-control/reportes/progreso.csv --bac 124000 --tol-costo 10 --tol-plazo 10 --proyecto {G} --guardar --corte 2027-01-08'), repo)
run(f'python3 {BMAD} --proyecto {G} backlog', repo, mostrar=False)
pb = os.path.join(repo, G, "02-planificacion/backlog.csv")
gob = {"1-1": ("1","Must",8,"S1","R1","3.1"), "1-2": ("2","Must",5,"S1","R1","3.1"), "1-3": ("3","Must",8,"S2","R1","3.2"),
       "1-4": ("4","Should",5,"S2","R1","3.2"), "3-1": ("5","Must",5,"S2","R1","4.1"), "3-2": ("6","Must",8,"S3","R1","4.1"),
       "3-3": ("7","Must",8,"S4","R1","4.1"), "2-1": ("8","Must",8,"S5","R2","3.3"), "2-2": ("9","Should",8,"S6","R2","3.3"),
       "2-3": ("10","Could",5,"S6","R2","3.3")}
filas = list(csv.DictReader(open(pb, encoding="utf-8"))); cab = list(filas[0].keys())
for f in filas:
    f["prioridad"], f["moscow"], f["estimacion"], f["iteracion"], f["release"], f["producto_pbs"] = map(str, gob[f["id"][:3]])
escribir_csv(pb, cab, filas)
ss = os.path.join(repo, "_bmad-output/implementation-artifacts/sprint-status.yaml")
def estados(ch):
    t = open(ss, encoding="utf-8").read()
    for k, v in ch.items(): t = re.sub(rf"(?m)^(\s*{re.escape(k)}:)\s*\S+", rf"\1 {v}", t)
    open(ss, "w", encoding="utf-8").write(t)
po = f"{G}/00-direccion/okr.csv"
def checkins(fecha, valores):
    for kr, v, cf in valores: run(f'python3 {OKR} {po} --checkin {kr} --valor {v} --confianza {cf} --fecha {fecha} --autor "Usuaria sénior: Sofía Ramírez"', repo)
def review(n, fecha, historias):   # aceptación de la PO en la sprint review: revisión de calidad que cita cada historia terminada
    return reg(repo, "calidad", producto=f"Sprint review {n}: historia {historias}", metodo_verificacion="demostracion", criterios="criterios de aceptación de cada historia y definición de terminado",
               responsable_productor="Lucía Benítez", revisores="Sofía Ramírez", aprobador="Product owner: Sofía Ramírez", fecha_prevista=fecha, fecha_real=fecha, resultado="aprobado", estado="completada")
estados({"1-1-alta-y-acceso-del-socio-con-segundo-factor": "done"})
review(1, "2026-12-11", "1-1")
run(f'python3 {BMAD} --proyecto {G} avance --corte 2026-12-11', repo)
checkins("2026-12-11", (("KR-1.1", 1, 7), ("KR-1.2", 4950, 6), ("KR-2.1", 92, 4), ("KR-2.2", 64, 6)))
estados({"1-2-recuperación-de-acceso": "done", "3-1-acceso-y-roles-de-la-consola-de-operador": "done"})
review(2, "2026-12-23", "1-2 e historia 3-1")
run(f'python3 {BMAD} --proyecto {G} avance --corte 2026-12-23', repo)
escribir(repo, "00-direccion/okr.csv", open(os.path.join(repo, po), encoding="utf-8").read().replace("3-1-acceso-y-roles-de-la-consola-de-operador,,,,,1,,,,,activo,", "3-1-acceso-y-roles-de-la-consola-de-operador,,,,,1,,,,,completada,"))
checkins("2026-12-23", (("KR-1.1", 2, 7), ("KR-1.2", 4900, 6), ("KR-2.1", 88, 4), ("KR-2.2", 68, 6)))
estados({"1-3-consulta-de-saldos-de-ahorro-y-préstamos": "done", "3-2-bandeja-única-de-solicitudes": "in-progress"})
review(3, "2027-01-08", "1-3")
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-01-08', repo)
checkins("2027-01-08", (("KR-1.1", 3, 7), ("KR-1.2", 4800, 6), ("KR-2.1", 80, 5), ("KR-2.2", 72, 6)))
print(open(os.path.join(repo, G, "03-control/reportes/avance-bmad.csv"), encoding="utf-8").read())
act(repo, "acciones", A["boletin"], estado="completada", fecha_cierre="2026-11-28")
R1 = reg(repo, "riesgos", fecha_identificacion="2026-12-20", autor="Martín Suárez", categoria="organizacional", causa="Baja respuesta del panel de socios a las encuestas", evento="No se puede medir la satisfacción (SM-5) en el piloto", efecto="KR sin línea base confiable", tipo="amenaza", probabilidad=3, impacto=3, impacto_monetario=4000, respuesta="reducir", acciones="incentivo de participación y encuesta corta", propietario="Sofía Ramírez", ejecutor="Martín Suárez", estado="en-seguimiento", notas=f"interesado {ST['Socios usuarios piloto']}")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-01-08'), repo)

P("Paso 10 · Highlight report con puertas, OKR al corte (salud y check-ins), sincronización con Tability y tablero por actor")
run(f'python3 {OKR} {po} --corte 2027-01-08 --markdown {G}/03-control/reportes/2027-01-08-okr.md', repo)
run(f'python3 {OKR} {po} --propuesta-sync tability', repo)
run(f'python3 {OKR} {po} --marcar-publicado KR-1.1@2027-01-08 --destino tability --ref checkin-ejemplo-1', repo)
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)
BEN = "B-01 4.000 y B-02 25 % en meta (R1 +1 semana, antes de medir); B-03 48 h solo con la bandeja (KR-2.3 en riesgo; hoy 80 h sin bandeja)"
escribir(repo, "03-control/reportes/2027-01-08-highlight-report.md", "# Highlight report · 2027-01-08\n\n| Objetivo | Pronóstico | Tolerancia | Estado |\n|---|---|---|---|\n"
         f"| Beneficios | {BEN} | −10 % por beneficio (B-03 ≤ 52,8 h), enfoque de beneficios | ámbar |\n\n"
         "OKR (complementan los beneficios): O-1 0,11 · O-2 0,24.\n")
art(repo, "highlight-2027-01-08", "03-control/reportes/2027-01-08-highlight-report.md")
av = list(csv.DictReader(open(os.path.join(repo, G, "03-control/reportes/avance-bmad.csv"), encoding="utf-8")))
LOG.append(("(columnas de avance-bmad.csv)", ", ".join(av[0].keys())))
it = []
for i, f in enumerate(av, 1):
    it.append({"nombre": f"Sprint {i}", "planificado": 8, "terminado": 0, "alcance_total": float(f.get("puntos_total") or 0), "terminado_acumulado": float(f.get("puntos_terminados") or 0)})
for i in range(len(it)):
    it[i]["terminado"] = it[i]["terminado_acumulado"] - (it[i-1]["terminado_acumulado"] if i else 0)
obj = [{"clave": "tiempo", "pronostico": "SPI 0,93: ~1 semana de atraso", "tol_etapa": "±10 %", "tol_proyecto": "±3 semanas", "rag": "ambar"},
       {"clave": "costo", "pronostico": "CPI 0,94: EAC ≈ USD 131.700 (+6,2 %)", "tol_etapa": "±10 %", "tol_proyecto": "±8 %", "rag": "ambar"},
       {"clave": "alcance", "pronostico": "Must completos en R1", "tol_etapa": "PO intercambia Should/Could", "tol_proyecto": "Must sin tolerancia", "rag": "verde"},
       {"clave": "calidad", "pronostico": "sin defectos críticos", "tol_etapa": "", "tol_proyecto": "", "rag": "verde"},
       {"clave": "beneficios", "pronostico": "B-01 y B-02 en meta; B-03 sujeto a la bandeja", "tol_etapa": "", "tol_proyecto": "−10 % por beneficio", "rag": "ambar"},
       {"clave": "riesgo", "pronostico": "sin riesgos altos abiertos", "tol_etapa": "", "tol_proyecto": "ningún alto sin respuesta", "rag": "verde"},
       {"clave": "sostenibilidad", "pronostico": "[por confirmar]", "tol_etapa": "", "tol_proyecto": "", "rag": "na"}]
hit = [{"hito": "Release 1 aceptada", "base": "2027-03-05", "actual": "2027-03-12", "var_dias": 7, "rag": "ambar", "comentario": "bandeja en curso"}]
tablero(repo, "2027-01-08", "2026-12-24", "2027-01-08", "2027-01-22", obj, hit,
        [{"id": "R-001", "texto": "aprobar USD 4.000 de contingencia para el incentivo del panel de socios", "fecha_limite": "2027-01-22"}], it,
        "Avance dentro de tolerancia; costo en ámbar por el sprint 3. El sindicato pasó de resistente a neutral tras el taller.",
        "estado.json; progreso.csv; avance-bmad.csv; registros al 2027-01-08; okr.csv; okr_checkins.csv",
        salida_png=os.path.join(OUT, "g3-tablero.png"), fecha_fija="2027-03-05", fecha_pronostico="2027-03-12")
tablero(repo, "2027-01-08", "2026-12-24", "2027-01-08", "2027-01-22", obj, hit, [], it, "Vista por actor", "idem",
        salida_png=os.path.join(OUT, "g3-tablero-actor.png"), actor="Sofía Ramírez")
# La junta revisa la condición de autorizar-etapa (CONCERNS de BMAD): la prueba de carga de NFR-3 ya está planificada → condición cumplida (EST-12 / G-01).
run(E(f'estado.py --proyecto {G} cumplir-condiciones autorizar-etapa --fecha 2027-01-08 --por "Ejecutiva: Laura Méndez" --nota "prueba de carga de NFR-3 planificada en el sprint 5 (plan de la etapa 2, Lucía Benítez)"'), repo)

P("Paso 11 · Comunicación personalizada por perfil y envío por la capa de canales")
escribir(repo, "03-control/reportes/2027-01-15-comunicado-consejo.md", "# Avance del Portal de autoservicio al 8 de enero\n\n"
         "**Decisión que se pide:** aprobar USD 4.000 de contingencia para el incentivo del panel de socios (R-001), antes del 22/1.\n\n"
         "Estado general ámbar: costo +6,2 % (dentro de la tolerancia de etapa de 10 %), 26 de 68 puntos terminados, Release 1 prevista el 12/3 "
         "(una semana después de la línea base). OKR: O-1 0,11 y O-2 0,24, esperables antes del lanzamiento; la bandeja (KR-2.3) está en riesgo.\n")
art(repo, "comunicado-consejo", "03-control/reportes/2027-01-15-comunicado-consejo.md")
run(I(f'plan-envio --tema "Avance del portal al 8 de enero" --audiencia "cuadrante:gestionar-de-cerca,cuadrante:mantener-satisfecho,-{ST["Martín Suárez"]}" '
      f'--proposito informe --base {G}/03-control/reportes/2027-01-15-comunicado-consejo.md --agrupar --fecha 2027-01-15'), repo)
C = f"{G}/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero"
run(V(f"estado {C}"), repo)
textos = {  # lo que redacta el modelo según el perfil (aquí, textos de ejemplo)
  "ejecutivo": "Decisión que se pide: aprobar USD 4.000 de contingencia para el incentivo del panel de socios (R-001) antes del 22/1.\n\n"
               "Estado: ámbar y dentro de tolerancia. Costo +6,2 % (tolerancia 10 %), Release 1 prevista el 12/3 (+1 semana). OKR O-1 0,11 y O-2 0,24: esperable antes del lanzamiento.",
  "lista":     "- Hitos: Release 1 el 12/3 (+1 semana); su aceptación técnica sigue el 5/3 para la bandeja.\n- Dependencias: ambiente de prueba de carga (NFR-3) antes del sprint 5.\n- Pedido: confirmar la capacidad del equipo para los sprints 4 y 5.",
  "datos":     "SPI 0,933 · CPI 0,942 · EAC USD 131.676 · 26/68 puntos (38,2 %). KR-1.1 0,10 · KR-1.2 0,13 · KR-2.2 0,40 · KR-2.3 0,33 (en riesgo: bandeja en curso). Acción vencida A-004 (prototipo).",
  "sindicato": "Resumen del avance: la bandeja muestra solo métricas del equipo, como se acordó en el taller (D-006). El prototipo se presentará a los operadores antes del sprint 4.",
  "reunion":   "Puntos para la reunión técnica: integración con el núcleo (NFR-6) y prueba de carga (NFR-3).",
}
for m in sorted(glob.glob(os.path.join(repo, C, "mensaje-*.md"))):
    t = open(m, encoding="utf-8").read(); cuerpo = t.split("-->", 1)[1]
    clave = ("sindicato" if f"para: {ST['Sindicato de operadores']}" in t else "reunion" if "canal: reunion" in t else
             "datos" if "formato: datos" in t else "lista" if "formato: lista" in t else "ejecutivo")
    open(m, "w", encoding="utf-8").write(t.split("-->", 1)[0] + "-->\n\n" + textos[clave] + "\n")
run(V(f'aprobar {C} --por "Gestor: Martín Suárez"'), repo)
run(V(f"enviar {C} --modo smtp"), repo)
s1, s2, rec, envp = servidores_prueba()
run_env(V(f"enviar {C} --modo smtp --confirmar --fecha 2027-01-15"), repo, envp)
run_env(V(f"enviar {C} --modo teams-webhook --confirmar --fecha 2027-01-15"), repo, envp)
reu = [os.path.basename(x) for x in glob.glob(os.path.join(repo, C, "mensaje-*-reunion-*.md"))]
for x in reu: run(V(f'registrar {C} --mensaje {x} --modo manual --referencia "reunión técnica del 2027-01-18" --fecha 2027-01-18'), repo)
LOG.append(("(lo que recibieron los servidores de prueba de 127.0.0.1)", json.dumps({"correos": [m["rcpt"] for m in rec["smtp"]], "teams": [h["cuerpo"]["attachments"][0]["content"]["body"][0]["text"] for h in rec["http"] if h["ruta"] == "/teams"]}, ensure_ascii=False, indent=1)))
for x in (s1, s2): x.shutdown()
run(V("historial"), repo)
act(repo, "acciones", A["consejo"], estado="completada", fecha_cierre="2027-01-15")
act(repo, "acciones", A["proto"], estado="completada", fecha_cierre="2027-01-14", notas="prototipo con métricas de equipo presentado a los operadores (vencida desde el 11/12, informada en el highlight)")
act(repo, "stakeholders", ST["Socios usuarios piloto"], nivel_compromiso_actual="partidario", notas="78 % de respuesta al boletín 2")
run(E(f'registro.py --proyecto {G} listar acciones'), repo)

P("Paso 12 · Reporte de interesados, vínculos en el ecosistema e integridad")
run(I(f"reporte --html {G}/03-control/reportes/2027-01-15-interesados.html --markdown {G}/03-control/reportes/2027-01-15-interesados.md --corte 2027-01-15"), repo)
art(repo, "reporte-interesados", "03-control/reportes/2027-01-15-interesados.html", estado="borrador")
captura_html(os.path.join(repo, G, "03-control/reportes/2027-01-15-interesados.html"), os.path.join(OUT, "g3-interesados.png"))
run(I(f'perfil todos --corte 2027-01-15'), repo)
run(I(f'vinculos {ST["Sofía Ramírez"]}'), repo)
run(I("integridad --corte 2027-01-15"), repo)
run(f'python3 {BMAD} --proyecto {G} backlog', repo, mostrar=False)
run(E(f'sanidad.py --proyecto {G} --rapido --corte 2027-01-15'), repo, ok=(0, 1, 2))
run(E(f'exportar.py xlsx --proyecto {G} --salida {G}/exportados/2027-01-15-registros.xlsx'), repo, ok=(0, 1))
P("Paso 13 · Compromiso sostenido: cadencia de contacto (STK-12), acción correctiva y reevaluación del compromiso")
CO = "2027-02-05"
run(I(f"integridad --corte {CO}"), repo)
run(E(f'sanidad.py --proyecto {G} --rapido --corte {CO}'), repo, ok=(0, 1, 2))
# Acción correctiva 1: la reunión técnica con TI se retoma y se registra como envío manual, con la retroalimentación.
reg(repo, "envios", fecha=CO, stakeholder_id=ST["Área de TI del núcleo operativo"], canal="reunion", modo="manual", estado="enviado", proposito="otro",
    asunto="Reunión técnica: integración con el núcleo (NFR-6) y prueba de carga (NFR-3)", referencia="acta 2027-02-05 reunión técnica", confirmado_por="Jefa de equipo: Lucía Benítez",
    notas="retroalimentación: TI se enteró por terceros del cambio en la consulta al padrón; sin la reunión semanal no pudo planificar el ambiente de carga. Pide retomar la reunión semanal con acta el mismo día.")
A["ti"] = reg(repo, "acciones", fecha=CO, origen=ST["Área de TI del núcleo operativo"], descripcion="Reunión técnica semanal con TI y acta enviada el mismo día; aviso previo de cambios que toquen el padrón",
              responsable="Lucía Benítez", fecha_compromiso="2027-02-12", prioridad="alta")
# Acción correctiva 2: la frecuencia de Lucía era la daily (ceremonia del equipo), no un compromiso de contacto → se revisa a semanal (checkpoint)
# y el checkpoint del 5/2 queda registrado como contacto de Lucía y de Martín.
act(repo, "stakeholders", ST["Lucía Benítez"], canal="checkpoint", frecuencia="semanal", notas="2027-02-05: la daily es ceremonia del equipo; el compromiso de contacto es el checkpoint semanal")
for n in ("Martín Suárez", "Lucía Benítez"):
    reg(repo, "envios", fecha=CO, stakeholder_id=ST[n], canal="reunion", modo="manual", estado="enviado", proposito="informe",
        asunto="Checkpoint semanal del 2027-02-05 (Lucía Benítez → Martín Suárez)", referencia="checkpoint-report 2027-02-05", confirmado_por="Gestor: Martín Suárez")
# Reevaluación del compromiso actual frente al deseado con la retroalimentación recibida.
act(repo, "stakeholders", ST["Área de TI del núcleo operativo"], nivel_compromiso_actual="resistente",
    notas=f"2027-02-05: molestia por falta de contacto (STK-12, 18 días sin reunión); ver {A['ti']}")
act(repo, "stakeholders", ST["Sindicato de operadores"], notas="2027-02-05: sin objeciones al comunicado del 15/1 (métricas de equipo, D-006); se mantiene neutral = deseado")
NIV = ["desconocedor", "resistente", "neutral", "partidario", "lider"]
sts = reg_json(repo, "listar", "stakeholders")
filas = ["| Interesado | " + " | ".join(NIV) + " | Brecha |", "|---|" + "---|" * (len(NIV) + 1)]
for x in sts:
    a_, d_ = x.get("nivel_compromiso_actual", ""), x.get("nivel_compromiso_deseado", "")
    celdas = [("A=D" if (n == a_ and n == d_) else "A" if n == a_ else "D" if n == d_ else "") for n in NIV]
    br = NIV.index(d_) - NIV.index(a_) if a_ in NIV and d_ in NIV else 0
    filas.append(f"| {x['id']} {x['nombre']} | " + " | ".join(celdas) + f" | {'+' + str(br) if br > 0 else '—'} |")
LOG.append((f"(matriz de evaluación del compromiso al {CO}, leída de stakeholders.csv: A = actual, D = deseado)", "\n".join(filas)))
run(I(f"integridad --corte {CO}"), repo)
run(E(f'sanidad.py --proyecto {G} --rapido --corte {CO}'), repo, ok=(0, 1, 2))
run(I(f'vinculos {ST["Área de TI del núcleo operativo"]}'), repo)
with open(sys.argv[1] if len(sys.argv) > 1 else "salida-g3.md", "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
