"""Guía E2E-3 · Interesados, comunicaciones, OKR y reporte de avance (scripts reales + tablero)."""
from comun import *
repo = proyecto("portal-socios"); print("REPO", repo)
OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))

P("Paso 1 · Proyecto y junta")
base_su(repo)

P("Paso 2 · Identificar y clasificar interesados (poder, interés, actitud, compromiso actual y deseado)")
ST = {}
for n, ro, rp, pod, inte, act_, des, canal, frec, resp, conf in [
  ("Laura Méndez", "Gerenta de operaciones", "Ejecutiva", "alto", "alto", "lider", "lider", "reunión 1:1", "quincenal", "Martín Suárez", "no"),
  ("Consejo directivo", "Órgano de gobierno de la cooperativa", "Capa de negocio", "alto", "medio", "partidario", "lider", "informe ejecutivo", "trimestral", "Laura Méndez", "no"),
  ("Sofía Ramírez", "Jefa de atención al socio", "Usuaria sénior y PO", "alto", "alto", "lider", "lider", "sprint review", "quincenal", "Martín Suárez", "no"),
  ("Sindicato de operadores", "Representación de operadores de sucursal", "Afectado", "medio", "alto", "resistente", "neutral", "taller presencial", "mensual", "Sofía Ramírez", "si"),
  ("Socios usuarios piloto", "Panel de 40 socios", "Usuarios finales", "bajo", "alto", "desconocedor", "partidario", "encuesta y boletín", "mensual", "Sofía Ramírez", "no"),
  ("Área de TI del núcleo operativo", "Dueña del core y del padrón", "Proveedor interno", "alto", "medio", "neutral", "partidario", "reunión técnica", "semanal", "Lucía Benítez", "no"),
  ("Unidad de cumplimiento", "Protección de datos", "Asesor", "alto", "bajo", "neutral", "partidario", "correo y revisión", "por hito", "Andrea Costa", "no"),
  ("Diego Ferreira", "Gerente del proveedor", "Proveedor sénior", "medio", "alto", "partidario", "partidario", "reunión de junta", "mensual", "Martín Suárez", "no")]:
    ST[n] = reg(repo, "stakeholders", nombre=n, rol_organizacion=ro, rol_proyecto=rp, poder=pod, interes=inte, actitud=act_, nivel_compromiso_actual=act_, nivel_compromiso_deseado=des, canal=canal, frecuencia=frec, responsable_relacion=resp, confidencial=conf)
run(E(f'registro.py --proyecto {G} listar stakeholders'), repo)
art(repo, "analisis-stakeholders", "01-inicio/analisis-stakeholders.md")
art(repo, "mapa-stakeholders", "02-planificacion/visuales/mapa-stakeholders.md")

P("Paso 3 · Plan de compromiso, enfoque de comunicación y matriz de comunicaciones")
art(repo, "plan-compromiso-stakeholders", "02-planificacion/plan-compromiso-stakeholders.md")
art(repo, "enfoque-comunicacion", "02-planificacion/enfoques/enfoque-comunicacion.md")
art(repo, "matriz-comunicaciones", "02-planificacion/matriz-comunicaciones.md")
A = {}
A["taller"] = reg(repo, "acciones", fecha="2026-11-02", origen=ST["Sindicato de operadores"], descripcion="Taller de co-diseño de la bandeja con operadores y delegado sindical", responsable="Sofía Ramírez", fecha_compromiso="2026-11-20", prioridad="alta")
A["boletin"] = reg(repo, "acciones", fecha="2026-11-02", origen=ST["Socios usuarios piloto"], descripcion="Boletín 1 al panel de socios: qué es el portal y cómo participar del piloto", responsable="Sofía Ramírez", fecha_compromiso="2026-12-01", prioridad="media")
A["consejo"] = reg(repo, "acciones", fecha="2026-11-02", origen=ST["Consejo directivo"], descripcion="Informe ejecutivo trimestral al Consejo con OKR y riesgos", responsable="Laura Méndez", fecha_compromiso="2027-01-15", prioridad="media")

P("Paso 4 · OKR ligados a beneficios (B-n) y métricas de éxito del PRD (SM-n)")
art(repo, "business-case", "00-direccion/business-case.md", texto="# Business case\n\nB-01 desvío de consultas a canales digitales (SM-2). B-02 adopción del portal (SM-1). B-03 respuesta de préstamos en menos de 48 h (SM-3).\n")
okr = """id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas
O-1,objetivo,,Los socios resuelven sus gestiones simples sin ir a la sucursal,,,,,,Ejecutivo: Laura Méndez,2027-12-31,OBJ-1,,
KR-1.1,kr,O-1,30 % de socios activos registrados en el portal,% socios registrados,0,30,0,%,Usuario sénior: Sofía Ramírez,2027-12-31,B-02; SM-1,6,
KR-1.2,kr,O-1,Bajar 30 % las consultas de saldo y constancias por canales tradicionales,consultas/mes,5000,3500,5000,consultas,Usuario sénior: Sofía Ramírez,2027-12-31,B-01; SM-2,5,
O-2,objetivo,,Los préstamos simples se resuelven rápido y sin papeles,,,,,,Ejecutivo: Laura Méndez,2027-12-31,OBJ-2,,
KR-2.1,kr,O-2,Respuesta a solicitudes simples en menos de 48 h hábiles,horas,96,48,96,horas,Usuario sénior: Sofía Ramírez,2027-12-31,B-03; SM-3,6,
KR-2.2,kr,O-2,Más del 90 % de las solicitudes llegan completas,% completas,60,90,60,%,Usuario sénior: Sofía Ramírez,2027-12-31,B-03; SM-3,7,
"""
escribir(repo, "00-direccion/okr.csv", okr)
art(repo, "okr", "00-direccion/okr.md")
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2026-11-20', repo)
run(E(f'sanidad.py --proyecto {G} --rapido'), repo, ok=(0, 1, 2))
hasta_etapa2(repo)

P("Paso 5 · Comunicar durante la etapa: acta de reunión con interesados → acciones y decisiones")
vtt = """WEBVTT

00:00:01.000 --> 00:00:09.000
<v Sofía Ramírez>Buen día, este es el taller de la bandeja única con operadores.

00:00:10.000 --> 00:00:21.000
<v Delegado sindical>Nos preocupa que la bandeja se use para medir productividad individual.

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
art(repo, "comunicado-operadores", "03-control/reportes/2026-11-21-comunicado-bandeja.md")

P("Paso 6 · Avance de la etapa: serie EVM, avance BMAD y registros a la fecha de corte")
escribir(repo, "03-control/reportes/progreso.csv", "periodo,pv,ev,ac,notas\n2026-12-11,15000,14200,15000,sprint 1\n2026-12-23,30000,28000,29600,sprint 2\n2027-01-08,45000,42000,44600,sprint 3\n")
run(E(f'evm.py --csv {G}/03-control/reportes/progreso.csv --bac 124000 --tol-costo 10 --tol-plazo 10 --proyecto {G}'), repo)
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
estados({"1-1-alta-y-acceso-del-socio-con-segundo-factor": "done"})
run(f'python3 {BMAD} --proyecto {G} avance --corte 2026-12-11', repo)
estados({"1-2-recuperación-de-acceso": "done", "3-1-acceso-y-roles-de-la-consola-de-operador": "done"})
run(f'python3 {BMAD} --proyecto {G} avance --corte 2026-12-23', repo)
estados({"1-3-consulta-de-saldos-de-ahorro-y-préstamos": "done", "3-2-bandeja-única-de-solicitudes": "in-progress"})
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-01-08', repo)
print(open(os.path.join(repo, G, "03-control/reportes/avance-bmad.csv"), encoding="utf-8").read())
act(repo, "acciones", A["boletin"], estado="completada", fecha_cierre="2026-11-28")
R1 = reg(repo, "riesgos", fecha_identificacion="2026-12-20", autor="Martín Suárez", categoria="organizacional", causa="Baja respuesta del panel de socios a las encuestas", evento="No se puede medir la satisfacción (SM-5) en el piloto", efecto="KR sin línea base confiable", tipo="amenaza", probabilidad=3, impacto=3, impacto_monetario=4000, respuesta="reducir", acciones="incentivo de participación y encuesta corta", propietario="Sofía Ramírez", ejecutor="Martín Suárez", estado="en-seguimiento", notas=f"interesado {ST['Socios usuarios piloto']}")
run(E(f'registro.py --proyecto {G} resumen --corte 2027-01-08'), repo)

P("Paso 7 · Highlight report con puertas, OKR al corte y tablero de avance con vista por actor")
okr2 = okr.replace(",30,0,%,Usuario", ",30,3,%,Usuario").replace(",60,90,60,%", ",60,90,72,%")
escribir(repo, "00-direccion/okr.csv", okr2)
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2027-01-08 --markdown {G}/03-control/reportes/2027-01-08-okr.md', repo)
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)
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
       {"clave": "beneficios", "pronostico": "KR-2.2 72 % (meta 90 %)", "tol_etapa": "", "tol_proyecto": "-10 %", "rag": "ambar"},
       {"clave": "riesgo", "pronostico": "sin riesgos altos abiertos", "tol_etapa": "", "tol_proyecto": "ningún alto sin respuesta", "rag": "verde"},
       {"clave": "sostenibilidad", "pronostico": "[por confirmar]", "tol_etapa": "", "tol_proyecto": "", "rag": "na"}]
hit = [{"hito": "Release 1 aceptada", "base": "2027-03-05", "actual": "2027-03-12", "var_dias": 7, "rag": "ambar", "comentario": "bandeja en curso"}]
tablero(repo, "2027-01-08", "2026-12-24", "2027-01-08", "2027-01-22", obj, hit,
        [{"id": "R-001", "texto": "aprobar USD 4.000 de contingencia para el incentivo del panel de socios", "fecha_limite": "2027-01-22"}], it,
        "Avance dentro de tolerancia; costo en ámbar por el sprint 3. El sindicato pasó de resistente a neutral tras el taller.",
        "estado.json; progreso.csv; avance-bmad.csv; registros al 2027-01-08; okr.csv",
        salida_png=os.path.join(OUT, "g3-tablero.png"), fecha_fija="2027-03-05", fecha_pronostico="2027-03-12")
tablero(repo, "2027-01-08", "2026-12-24", "2027-01-08", "2027-01-22", obj, hit, [], it, "Vista por actor", "idem",
        salida_png=os.path.join(OUT, "g3-tablero-actor.png"), actor="Sofía Ramírez")

P("Paso 8 · Comunicación del avance por audiencia y seguimiento de compromisos")
art(repo, "comunicado-consejo", "03-control/reportes/2027-01-15-comunicado-consejo.md")
act(repo, "acciones", A["consejo"], estado="completada", fecha_cierre="2027-01-15")
act(repo, "stakeholders", ST["Socios usuarios piloto"], nivel_compromiso_actual="partidario", notas="78 % de respuesta al boletín 2")
run(E(f'registro.py --proyecto {G} listar acciones'), repo)
run(E(f'registro.py --proyecto {G} listar stakeholders'), repo)
run(E(f'exportar.py xlsx --proyecto {G}'), repo, ok=(0, 1))
with open(sys.argv[1] if len(sys.argv) > 1 else "salida-g3.md", "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
