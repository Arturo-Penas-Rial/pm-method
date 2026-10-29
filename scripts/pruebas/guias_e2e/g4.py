"""Guía E2E-4 · Producto de la idea al producto con BMAD dentro de un proyecto PRINCE2 (evidencia con scripts).

El paso 1 (de la idea al proyecto autorizado) se ejecuta completo para que el recorrido funcione, aunque la guía lo
resume y remite a E2E-5. Gráficos (visuales.py) con los datos reales de la corrida: g4-calidad-entregas.png,
g4-burnup.png, g4-lecciones-ciclo.png, g4-cierre.png, g4-expediente.png (con la bitácora de escrituras) y g4-beneficios.png; capturas del tablero con su sección de mapas estratégicos
(g4-tablero.png y el recorte 16:9 g4-tablero-mapas-169.png) y del mapa de recorrido de UJ-1 (g4-recorrido.png).
"""
from comun import *
import yaml
import visuales as V
OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
repo = proyecto("portal-socios"); print("REPO", repo)
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))

def puerta4(tipo, por, fecha, extra="", decision="aprobado"):
    """Como comun.puerta, con la fecha de la junta también en la lista y en la confirmación (evidencia determinista)."""
    run(E(f'puertas.py --proyecto {G} verificar {tipo}'), repo, ok=(0, 1, 2))
    run(E(f'puertas.py --proyecto {G} lista {tipo} --fecha {fecha}'), repo, mostrar=False)
    run(E(f'puertas.py --proyecto {G} confirmar {tipo} --por "{por}" --fecha {fecha}'), repo)
    return run(E(f'estado.py --proyecto {G} puerta {tipo} --decision {decision} --por "{por}" --fecha {fecha} {extra}'), repo)

def sanidad(corte):
    return run(E(f'sanidad.py --proyecto {G} --rapido --corte {corte}'), repo, ok=(0, 1))

def fm(clave, texto, estado="en-revision", version=None):
    """Encabezado YAML como el de las plantillas: estado.py aprobar lo sincroniza y la copia congelada lo conserva."""
    return f"---\ntipo: {clave}\nversion: {version or '0.1'}\nestado: {estado}\n---\n{texto}"

def doc(clave, rel, texto, estado="en-revision", version=None, origen=""):
    """El contenido lo redacta la skill dueña desde su plantilla; aquí, una versión mínima con los datos del escenario."""
    art(repo, clave, rel, estado=estado, version=version, texto=fm(clave, texto, estado, version))
    LOG.append((f"({origen} → gestion/{rel})" if origen else f"(gestion/{rel})", texto.strip()))

P("Paso 1a · Proyecto y detección de BMAD")
run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez" --fecha 2026-10-20'), repo)
run(f'python3 {BMAD} --proyecto {G} detectar', repo)
run(E(f'estado.py --proyecto {G} integracion especificacion=bmad'), repo)

P("Paso 1b · Idea → brief de producto (BMAD) → mandato y project brief (pm-method)")
run(f'python3 {BMAD} --proyecto {G} inventario', repo)
run(E(f'especificacion.py --proyecto {G} fuente'), repo)
art(repo, "mandato", "00-direccion/mandato.md")
art(repo, "project-brief", "01-inicio/project-brief.md", texto="# Project brief\n\nProducto: ver brief de BMAD (_bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md, sha 58db1efac463).\n")
reg(repo, "decisiones", fecha="2026-10-20", decision="Enfoque híbrido: etapas PRINCE2; especificación con BMAD; sprints de 14 días como paquetes", decidido_por="Ejecutivo: Laura Méndez", nivel="junta")

P("Paso 1c · Junta, business case esquemático y puerta autorizar-inicio")
run(E(f'estado.py --proyecto {G} rol usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" product_owner="Sofía Ramírez" autoridad_cambio="Sofía Ramírez" aseguramiento="Andrea Costa" jefes_equipo="Lucía Benítez"'), repo)
run(E(f'estado.py --proyecto {G} agil cadencia_iteracion_dias=14 velocidad_referencia=8'), repo)
art(repo, "business-case-esquematico", "00-direccion/business-case-esquematico.md")
art(repo, "plan-etapa-1", "02-planificacion/plan-etapa-1.md")
puerta4("autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")

P("Paso 1d · PRD, UX y arquitectura (BMAD) → requisitos en la fachada")
run(f'python3 {BMAD} --proyecto {G} requisitos', repo)
run(E(f'especificacion.py --proyecto {G} resumen'), repo)
run(E(f'especificacion.py --proyecto {G} consultar FR-6'), repo)

P("Paso 1e · Épicas e historias (BMAD) → WBS por productos y trazabilidad")
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

P("Paso 1f · Backlog con columnas de gobierno, MoSCoW y release plan")
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

P("Paso 1g · Business case, enfoques de beneficios, calidad y sostenibilidad, PID adaptado, OKR y puerta autorizar-proyecto")
art(repo, "business-case", "00-direccion/business-case.md", texto=fm("business-case", "# Business case\n\nB-01 desvío de consultas (SM-2); B-02 adopción (SM-1); B-03 eficiencia de préstamos (SM-3).\n"))
art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
okr = """id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas
O-1,objetivo,,Los socios resuelven sus gestiones simples sin ir a la sucursal,,,,,,Ejecutivo: Laura Méndez,2027-12-31,OBJ-1,,
KR-1.1,kr,O-1,30 % de socios activos registrados,% socios registrados,0,30,0,%,Usuario sénior: Sofía Ramírez,2027-12-31,B-02; SM-1,6,
KR-1.2,kr,O-1,Bajar 30 % las consultas de saldo por canales tradicionales,consultas/mes,5000,3500,5000,consultas,Usuario sénior: Sofía Ramírez,2027-12-31,B-01; SM-2,5,
KR-1.3,kr,O-1,Responder préstamos simples en menos de 48 h hábiles,horas,96,48,96,horas,Usuario sénior: Sofía Ramírez,2027-12-31,B-03; SM-3,6,
"""
escribir(repo, "00-direccion/okr.csv", okr)
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2026-11-20', repo)
run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "calidad=NFR sin tolerancia; cada historia terminada con revisión aprobada" "beneficios=-10 %" "riesgo=ningún riesgo alto sin respuesta" "sostenibilidad=-10 % sobre las metas del enfoque de sostenibilidad"'), repo)
doc("pid", "00-direccion/pid.md", """# PID · Portal de autoservicio para socios
§1-§7: business case, organización, enfoques (calidad, beneficios, sostenibilidad, riesgo, cambios), plan de proyecto y controles.
## 8. Adaptación del método (tailoring)
- Ciclo de vida: etapas PRINCE2 (iniciación, Release 1, Release 2); dentro de cada etapa, sprints de 14 días como paquetes de trabajo.
- Especificación: BMAD es la fuente única (PRD, épicas, historias); pm-method la lee por la fachada y no la copia. Cambios a la línea base del PRD: solo por control de cambios y traspaso.
- Roles combinados: Sofía Ramírez es usuaria sénior, product owner y autoridad de cambio (hasta USD 8.000 por cambio y USD 15.000 en total, presupuesto de cambio de la junta).
- Informes: checkpoint por sprint (jefa de equipo), highlight quincenal (gestor), informe de fin de etapa por release.
- Calidad: una revisión registrada por historia (enfoque de calidad); los NFR con prueba propia.
- Productos de gestión fusionados: plan de proyecto dentro del PID; release plan en lugar de plan de equipo.""", origen="pm-acta-constitucion; §8 con la adaptación del método")
# primera verificación: hay B-n en el business case pero nadie definió cómo, cuándo y quién mide después del cierre (P-04)
run(E(f'puertas.py --proyecto {G} verificar autorizar-proyecto'), repo, ok=(0, 1, 2))
doc("enfoque-beneficios", "00-direccion/enfoque-beneficios.md", """# Enfoque de gestión de beneficios v1.0
Gestionado por: proyecto hasta el cierre; negocio (usuaria sénior Sofía Ramírez) después.
| Beneficio | Medida | Línea base | Meta | Dueño | Mediciones |
|---|---|---|---|---|---|
| B-01 desvío de consultas | SM-2 (KR-1.2) | 5.000 consultas/mes | 3.500 | Sofía Ramírez | 30/6/2027 y 31/12/2027 |
| B-02 adopción | SM-1 (KR-1.1) | 0 % | 30 % de socios activos | Sofía Ramírez | 30/6/2027 y 31/12/2027 |
| B-03 préstamos en < 48 h | SM-3 (KR-1.3) | 96 h | 48 h | Sofía Ramírez | 30/6/2027 y 31/12/2027 |
Tolerancia de beneficios: -10 %. Las revisiones posteriores al proyecto las ejecuta y financia el negocio.""", origen="pm-caso-de-negocio, templates/enfoque-beneficios.md")
doc("enfoque-calidad", "00-direccion/enfoque-calidad.md", """# Enfoque de gestión de la calidad v1.0
Criterios: cada historia se verifica contra sus criterios de aceptación de BMAD (epics.md); los NFR, con prueba específica (NFR-3: prueba de carga, p95 < 3 s).
Responsables: produce Lucía Benítez (equipo), revisa Andrea Costa (aseguramiento, independiente), aprueba Sofía Ramírez (usuaria sénior).
Registro: una revisión en calidad.csv por historia terminada, que la cite como "historia N-M"; se registra en lote al cierre de cada sprint o release.
Control permanente: sanidad QUA-01 (terminado sin revisión), QUA-02 (revisión vencida), QUA-03 (rechazo sin tratamiento).
Defectos fuera de especificación: issue (pm-issues-cambios).""", origen="pm-enfoques-gestion, templates/enfoque-calidad.md")
doc("enfoque-sostenibilidad", "00-direccion/enfoque-sostenibilidad.md", """# Enfoque de gestión de sostenibilidad v1.0
Aplicabilidad: mínimo (sin impacto ambiental relevante; se mide lo que el portal cambia).
| Meta | Indicador | Línea base | Meta | Dueño | Revisión |
|---|---|---|---|---|---|
| S-1 constancias sin papel | % de constancias emitidas en PDF | 0 % | 80 % a 12 meses | Sofía Ramírez | fin de cada etapa y revisión de beneficios |
| S-2 traslados evitados | consultas desviadas de sucursal (SM-2) | 5.000/mes | -30 % | Sofía Ramírez | ídem |
| S-3 alojamiento | proveedor de nube con energía renovable certificada | — | requisito de contrato | Diego Ferreira | fin de etapa 2 |
Tolerancia: -10 % sobre las metas (estado.json tolerancias.proyecto.sostenibilidad).""", origen="pm-caso-de-negocio, templates/enfoque-sostenibilidad.md")
run(E(f'estado.py --proyecto {G} presupuesto cambio=15000 limite_autoridad_cambio=8000 --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27'), repo)
sanidad("2026-11-27")
puerta4("autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
for c in ("business-case", "pid", "enfoque-beneficios", "enfoque-calidad", "enfoque-sostenibilidad"):
    run(E(f'estado.py --proyecto {G} aprobar {c} --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27'), repo)
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.0 --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27', repo)
run(E(f'estado.py --proyecto {G} resumen'), repo)

P("Paso 2 · Gate de preparación de BMAD y puerta autorizar-etapa (Release 1) con condición formal")
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado CONCERNS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26 --nota "NFR-3 sin prueba de carga planificada"'), repo)
art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md", texto="# Plan de la etapa 2 (Release 1)\n\nSprints 1 a 4 (historias del Release 1). Prueba de carga de NFR-3 planificada antes del fin de etapa (respuesta a la condición de la junta).\n")
run(E(f'estado.py --proyecto {G} tolerancia --nivel etapa "tiempo=±10 %" "costo=±10 %" "alcance=PO intercambia Should/Could"'), repo)
puerta4("autorizar-etapa", "Ejecutivo: Laura Méndez", "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05', decision="condicionado")
# la respuesta a la condición entra como revisión de calidad planificada, con fecha: si vence sin hacerse, QUA-02 la marca
qc = reg(repo, "calidad", producto="NFR-3 prueba de carga (consultas de saldos y préstamos)", metodo_verificacion="prueba", criterios="NFR-3 p95 menor a 3 s con conexión móvil estándar; condición de autorizar-etapa (CONCERNS de BMAD)", responsable_productor="Lucía Benítez", revisores="Diego Ferreira; Andrea Costa", aprobador="Sofía Ramírez", fecha_prevista="2027-02-19")
sanidad("2026-11-27")
run(f'python3 {BMAD} --proyecto {G} avance --corte 2026-11-27', repo)   # punto de partida del burn-up: 0 de 68 puntos

P("Paso 3 · Sprint 1 como paquete de trabajo; construcción con BMAD; checkpoint y aceptación del paquete")
art(repo, "WP-001", "03-control/paquetes-trabajo/WP-001-sprint-1.md", estado="aprobado", version="1.0",
    texto="# WP-001 · Sprint 1 (descripción de paquete de trabajo)\n\nAlcance por ids de la fachada: historias 1-1 y 1-2. Gestora de equipo: Lucía Benítez. Checkpoint al cierre del sprint.\n")
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
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
pb = os.path.join(repo, G, "02-planificacion/backlog.csv")
titulos = {f["id"][:3]: f["titulo"] for f in csv.DictReader(open(pb, encoding="utf-8"))}
def revision(k, rel, fecha, resultado="aprobado", notas=""):
    extra = {"notas": notas} if notas else {}
    return reg(repo, "calidad", producto=f"{rel} · historia {k} {titulos[k]}", metodo_verificacion="prueba", criterios=f"criterios de aceptación de la historia {k} (epics.md)", responsable_productor="Lucía Benítez", revisores="Andrea Costa", aprobador="Sofía Ramírez", fecha_prevista=fecha, fecha_real=fecha, resultado=resultado, estado="completada", **extra)
q_s1 = [revision("1-1", "Sprint 1", "2026-12-21", notas="incluye NFR-1 segundo factor"), revision("1-2", "Sprint 1", "2026-12-22")]
FOTOS = []
def productos_json(corte=None):
    d = json.loads(run(E(f'estado.py --proyecto {G} productos' + (f' --corte {corte}' if corte else '') + ' --json'), repo, mostrar=False)); LOG.pop()
    return d
def foto_calidad(etiqueta, corte):
    """Estado de productos del plugin (estado.py productos --json) al corte: historias terminadas en backlog.csv contra las
    que el plugin da por aprobadas o aceptadas (misma regla que QUA-01). Alimenta g4-calidad-entregas.png."""
    d = productos_json(corte)
    hechas = [p for p in d["productos"] if p["fisico"] == "terminado"]
    ok_ = [p for p in hechas if p["estado"] in ("aprobado", "aceptado", "con-concesion")]
    FOTOS.append((etiqueta, len(hechas), len(ok_)))
    LOG.append((f"(foto de calidad «{etiqueta}» para g4-calidad-entregas.png: estado.py productos --corte {corte} --json, historias terminadas contra aprobadas o aceptadas)",
                f"terminadas {len(hechas)} · con revisión aprobada {len(ok_)} · sin revisión aprobada {len(hechas) - len(ok_)}"))
doc_cp = f"""# Informe de punto de control · WP-001 (sprint 1) · 2026-12-23
Gestora de equipo: Lucía Benítez · Para: Martín Suárez (gestor) · Período: 2026-11-30 – 2026-12-23
1. Resumen: sprint 1 completo; semáforo verde (13 de 13 puntos comprometidos).
3. Productos completados (con calidad aprobada): historia 1-1 ({q_s1[0]}), historia 1-2 ({q_s1[1]}). En curso: historia 1-3 en review (sprint 2).
   Actividades de calidad: {q_s1[0]} y {q_s1[1]} aprobadas por Sofía Ramírez. Prevista: {qc} prueba de carga NFR-3 (19/2).
5. Tolerancias del paquete: tiempo y costo dentro; alcance completo; calidad: 2 de 2 historias con revisión.
6. Issues y riesgos: sin novedades. 7. Acciones correctivas: ninguna."""
escribir(repo, "03-control/reportes/2026-12-23-checkpoint-WP-001.md", doc_cp)
LOG.append(("(pm-progreso-reportes, templates/checkpoint-report.md → gestion/03-control/reportes/2026-12-23-checkpoint-WP-001.md)", doc_cp))
sanidad("2026-12-23")
foto_calidad("23/12 · Sprint 1", "2026-12-23")
reg(repo, "decisiones", fecha="2026-12-23", decision=f"WP-001 aceptado: checkpoint del 23/12; historias 1-1 y 1-2 terminadas con {q_s1[0]} y {q_s1[1]} aprobadas", decidido_por="Gestor: Martín Suárez", nivel="gestor", artefactos_afectados="03-control/reportes/2026-12-23-checkpoint-WP-001.md")
run(E(f'especificacion.py --proyecto {G} resumen'), repo)

P("Paso 4 · Valor ganado ágil (corte guardado) y highlight con puertas y condiciones")
run(E(f'evm.py --pv 41000 --ev 38000 --ac 40500 --bac 124000 --modo agil --pct-no-must 20 --proyecto {G} --guardar --corte 2027-01-08'), repo)
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)

P("Paso 5 · Cambio de rumbo: bmad-correct-course agrega FR-13 → verificar → issue → cambio con costo y cargo → traspaso → línea base 1.1")
prd = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(repo, "_bmad-output")) for f in fs if f == "prd.md"][0]
t = open(prd, encoding="utf-8").read()
t = t.replace("#### FR-11: Roles y permisos", "#### FR-13: Pago de cuotas de préstamo con débito en cuenta\n\nEl socio puede pagar una cuota vencida o próxima de su préstamo con débito de su cuenta de ahorro. Realiza UJ-2.\n\n#### FR-11: Roles y permisos", 1)
open(prd, "w", encoding="utf-8").write(t)
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
sanidad("2027-01-12")
i1 = reg(repo, "issues", fecha="2027-01-12", tipo="solicitud-cambio", titulo="FR-13 pago de cuotas agregado al PRD sin control de cambios", descripcion="bmad.py verificar detectó FR-13 nuevo contra la línea base PRD v1.0", prioridad="alta", severidad="mayor", responsable="Martín Suárez")
c1 = reg(repo, "cambios", fecha="2027-01-13", solicitante="Sofía Ramírez", titulo="Incorporar FR-13 pago de cuotas", descripcion=f"Origen {i1}", impacto_alcance="nueva historia 2-4 (8 puntos)", impacto_tiempo="+1 sprint en la etapa 3", impacto_costo="+USD 6.000 contra el presupuesto de cambio", impacto_beneficios="refuerza B-01", recomendacion="aprobar para la etapa 3; diferir FR-8 a Could", costo="6000", cargo="presupuesto-cambio")
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
titulos = {f["id"][:3]: f["titulo"] for f in filas}
LOG.append(("(el PO completa las columnas de gobierno de la historia nueva 2-4: Should, 8 pts, S7, R2)", ""))
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.1 --por "Ejecutivo: Laura Méndez" --fecha 2027-01-20', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.1 --por "Ejecutivo: Laura Méndez" --fecha 2027-01-20', repo)
import glob as _g
hd = _g.glob(os.path.join(repo, G, "02-planificacion/especificacion/handoff-bmad-*-C-001.md"))[0]
_t = open(hd, encoding="utf-8").read().replace("estado: emitido", "estado: aplicado", 1); open(hd, "w", encoding="utf-8").write(_t)
LOG.append(("(el equipo BMAD marca el traspaso como aplicado: estado: aplicado en " + re.sub(r"handoff-bmad-\d{4}-\d{2}-\d{2}-", "handoff-bmad-<fecha>-", os.path.relpath(hd, repo)) + ")", ""))
act(repo, "cambios", c1, estado="implementado")
act(repo, "issues", i1, estado="cerrado", fecha_cierre="2027-01-20")
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
sanidad("2027-01-20")
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-01-20', repo)   # el alcance pasa de 68 a 76 puntos por C-001

P("Paso 6 · Calidad a volumen al acercarse el fin del Release 1: terminados sin revisión y registro en lote")
run(E(f'estado.py --proyecto {G} contexto --corte 2027-02-26'), repo)   # lo que el hook de inicio le muestra al gestor al retomar la sesión
run(E(f'estado.py --proyecto {G} radar --corte 2027-02-26 --linea'), repo)   # la línea de radar del mismo hook
run(E(f'estado.py --proyecto {G} radar --corte 2027-02-26'), repo)           # «¿qué tengo que decidir, escalar y desbloquear hoy?»
poner_estados({k: "done" for k in ["epic-1", "epic-3", "1-3-consulta-de-saldos-de-ahorro-y-préstamos", "1-4-descarga-de-constancias-en-pdf", "3-1-acceso-y-roles-de-la-consola-de-operador", "3-2-bandeja-única-de-solicitudes", "3-3-resolución-de-solicitudes"]})
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
sanidad("2027-02-26")
run(E(f'estado.py --proyecto {G} productos --corte 2027-02-26 --alcance R1'), repo)   # estado de productos del Release 1
foto_calidad("26/2 · antes del lote", "2027-02-26")
q_r1 = [revision(k, "Release 1", "2027-02-25") for k in ("1-3", "1-4", "3-1", "3-2")]
q_r1.append(revision("3-3", "Release 1", "2027-02-25", resultado="aprobado-con-observaciones", notas="observación menor de usabilidad en el filtro de la bandeja; va al backlog"))
sanidad("2027-02-26")
foto_calidad("26/2 · después del lote", "2027-02-26")

P("Paso 6b · El recorrido de la socia sobre lo entregado: mapa de UJ-1 desde BMAD, dolores con tratamiento (MAP-03)")
MAPAS = f"python3 {RAIZ}/skills/pm-mapas-estrategicos/scripts/mapas.py"
RMAP = os.path.join(repo, G, "02-planificacion", "mapas", "recorrido-uj-1.json")
run(f'python3 {BMAD} --proyecto {G} recorridos --id UJ-1', repo)
run(f'{MAPAS} --proyecto {G} recorrido semilla --uj UJ-1 --fecha 2027-02-26', repo)
OBS = "observación: revisión del Release 1 con seis socios (25/2)"
EMO = {  # paso: (emoción, fuente, dolor, causa, oportunidad, kano, refs, punto de contacto, frontstage, backstage, soporte)
    "P1": (-1, OBS + ": dos pidieron ayuda en el primer ingreso", "El primer ingreso con segundo factor la frena y pide ayuda", "usabilidad",
           "Alta asistida en sucursal y por teléfono al salir a producción", "desempeno", [], "Portal", "Usuario, contraseña y código por SMS", "", "Proveedor de identidad y SMS"),
    "P2": (-1, OBS + ": el resumen tarda en aparecer y no hay indicador de carga", "Espera el resumen sin saber si cargó", "rendimiento",
           "Respuesta en menos de 3 s con carga real (NFR-3)", "obligatorio", [], "Portal", "Resumen de ahorro y préstamos", "Lectura del núcleo operativo (AD-1)", ""),
    "P3": (0, OBS, "", "", "", "", ["FR-5"], "Portal", "Menú Constancias", "", ""),
    "P4": (1, OBS, "", "", "", "", ["FR-5"], "Portal", "Constancia de saldos", "", ""),
    "P5": (2, OBS + ": la constancia se descargó en el primer intento", "", "", "", "", ["FR-5"], "PDF", "Constancia con fecha y saldos", "PDF al vuelo con código de verificación (AD-8)", ""),
    "P6": (1, "supuesto declarado: lo confirma la revisión de beneficios (B-01, S-1)", "", "", "", "", [], "Trámite bancario", "", "", "")}
def completar(cambios, origen):
    d_ = json.load(open(RMAP, encoding="utf-8")); cambios(d_)
    open(RMAP, "w", encoding="utf-8").write(json.dumps(d_, ensure_ascii=False, indent=2) + "\n")
    filas_ = [f"{et['nombre']} · {p_['id']} {p_['accion']} · {format(p_['emocion'], '+d') if p_['emocion'] else '0'} ({p_['fuente_emocion']})"
              + (f" · dolor: {p_['dolor']} ({p_['tipo_causa']})" if p_.get("dolor") else "") + (f" → {p_['oportunidad']}" if p_.get("oportunidad") else "")
              + (f" · refs {', '.join(p_['refs'])}" if p_.get("refs") else "") for et in d_["etapas"] for p_ in et["pasos"]]
    LOG.append((f"({origen} → gestion/02-planificacion/mapas/recorrido-uj-1.json)", "\n".join(filas_)))
def prop(d_):
    for et in d_["etapas"]:
        for p_ in et["pasos"]:
            em, fu, do, ca, op, ka, rf, pc, fr, bk, so = EMO[p_["id"]]
            p_.update({"emocion": em, "fuente_emocion": fu, "dolor": do, "tipo_causa": ca, "oportunidad": op, "kano": ka, "refs": rf, "punto_contacto": pc, "canal": "" if p_["id"] == "P6" else "celular"})
            for k_, v_ in (("frontstage", fr), ("backstage", bk), ("soporte", so)):
                if v_: p_[k_] = v_
    d_.update({"titulo": "UJ-1 · Marta consulta su saldo y baja una constancia (Release 1)", "trabajo": "Conseguir una constancia de saldos para un trámite bancario sin ir a la sucursal",
               "escenario": "actual"})
completar(prop, "pm-mapas-estrategicos completa la semilla con lo observado en la revisión del Release 1; Sofía Ramírez (product owner) confirma")
run(f'{MAPAS} --proyecto {G} recorrido validar uj-1', repo)
run(f'{MAPAS} --proyecto {G} controles', repo)
run(f'{MAPAS} --proyecto {G} recorrido candidatos uj-1', repo)
# la persona decide: P2 ya tiene tratamiento (NFR-3, verificado por Q-001, la condición de la puerta); P1 no se trata con alcance
# nuevo a una etapa del cierre, sino como riesgo para el beneficio B-02 con una respuesta del negocio
r1 = reg(repo, "riesgos", fecha_identificacion="2027-02-26", autor="Martín Suárez", categoria="comercial",
         causa="El primer ingreso con segundo factor frena a socios que evitan los trámites digitales (recorrido UJ-1, paso P1)",
         evento="La adopción del portal queda por debajo de la meta", efecto="B-02 adopción (KR-1.1, 30 % de socios activos) fuera de la tolerancia de beneficios",
         tipo="amenaza", probabilidad=3, impacto=3, proximidad="mediano-plazo", respuesta="reducir",
         acciones="alta asistida en sucursal y por teléfono durante los primeros 60 días de operación (servicios al socio)", propietario="Sofía Ramírez", fecha_revision="2027-06-30")
run(f'{MAPAS} --proyecto {G} vincular uj-1 P1 --refs {r1}', repo)
run(f'{MAPAS} --proyecto {G} vincular uj-1 P2 --refs NFR-3,{qc}', repo)
run(f'{MAPAS} --proyecto {G} recorrido render uj-1 --png no', repo)
run(E(f'estado.py --proyecto {G} artefacto mapa-recorrido-uj-1 --ruta 02-planificacion/visuales/recorrido-uj-1.md --estado en-revision'), repo, mostrar=False); LOG.pop()
run(f'{MAPAS} --proyecto {G} controles', repo)
captura_html(os.path.join(repo, G, "02-planificacion", "visuales", "recorrido-uj-1.html"), os.path.join(OUT, "g4-recorrido.png"))

P("Paso 6c · Retrospectiva del sprint 4 (reunión propia): lecciones con cita, clasificadas por impacto y ámbito, y una acción para el sprint siguiente")
TRS = f"python3 {RAIZ}/skills/pm-reuniones/scripts/transcripcion.py"
XT = f"python3 {RAIZ}/skills/pm-reuniones/scripts/extraccion.py --proyecto {G}"
LECC = f"python3 {RAIZ}/skills/pm-lecciones-aprendidas/scripts/lecciones.py"
RETRO = """WEBVTT

00:00:05.000 --> 00:00:30.000
<v Andrea Costa>Arrancamos con las tres preguntas de siempre sobre el proceso del sprint 4 (qué anduvo, qué no y qué probamos), sin buscar culpables.

00:00:40.000 --> 00:01:20.000
<v Sofía Ramírez>La revisión con seis socios del 25/2 funcionó muy bien, aprendimos que mirar el recorrido con socios reales antes de cerrar un release encuentra dolores que las pruebas no ven.

00:01:30.000 --> 00:02:05.000
<v Lucía Benítez>No funcionó lo de siempre: otra vez llegaron historias a done sin la revisión registrada, cinco desde el sprint 2.

00:02:10.000 --> 00:02:55.000
<v Martín Suárez>Tampoco funcionó cómo entró FR-13: la Sprint Change Proposal llegó al PRD sin pasar por la autoridad de cambio y la sanidad marcó el cambio no controlado hasta tramitar C-001.

00:03:40.000 --> 00:04:15.000
<v Lucía Benítez>Probemos en el sprint 5 que ninguna historia pase a done sin su revisión registrada: yo actualizo la definición de terminado para el 3/3.

00:04:20.000 --> 00:04:50.000
<v Martín Suárez>Acordamos que toda Sprint Change Proposal entra primero como issue, yo armo la plantilla del issue para el 3/3.

00:05:00.000 --> 00:05:20.000
<v Andrea Costa>Las acciones de la retrospectiva del sprint 3 quedaron hechas; gracias a todos.
"""
escribir(repo, "03-control/reuniones/2027-02-26-retro-sprint-4-original.vtt", RETRO)
LOG.append(("(la reunión grabada por el equipo, facilitada por aseguramiento → gestion/03-control/reuniones/2027-02-26-retro-sprint-4-original.vtt)", RETRO.strip()))
TR_R = f"{G}/03-control/reuniones/2027-02-26-retro-sprint-4-transcripcion.md"
run(f"{TRS} {G}/03-control/reuniones/2027-02-26-retro-sprint-4-original.vtt --salida {TR_R}", repo)
run(f"{XT} candidatos --transcripcion {TR_R}", repo)
CJ = os.path.join(repo, G, "03-control", "reuniones", "2027-02-26-retro-sprint-4-candidatos.json")
CR = {c["id"]: c for c in json.load(open(CJ, encoding="utf-8"))["candidatos"]}
N_CL = sum(1 for c in CR.values() if c["clase"] == "leccion"); N_CM = sum(1 for c in CR.values() if c["clase"] == "mejora")
N_GOB = sum(1 for c in CR.values() if c["clase"] in ("decision", "accion"))
out_r = run(f'{XT} registrar --candidatos {G}/03-control/reuniones/2027-02-26-retro-sprint-4-candidatos.json --confirmar CL-01,CL-02,CL-03,CM-01,CM-02 --por "Gestor: Martín Suárez"'
            ' --campo "CL-01:efecto=dos dolores del recorrido UJ-1 que las pruebas no habían mostrado (R-001 y la espera del resumen)" --campo "CL-01:categoria=acierto" --campo "CL-01:responsable_seguimiento=Sofía Ramírez"'
            ' --campo "CL-02:efecto=QUA-01 marcó cinco historias el 26/2 y hubo que registrar las revisiones en lote" --campo "CL-02:recomendacion=la revisión registrada es parte de la definición de terminado: ninguna historia pasa a done sin ella"'
            ' --campo "CL-02:categoria=calidad" --campo "CL-02:responsable_seguimiento=Lucía Benítez"'
            ' --campo "CL-03:efecto=ESP-10 en la sanidad del 12/1: la puerta quedaba bloqueada hasta tramitar C-001 y una línea base nueva" --campo "CL-03:recomendacion=toda Sprint Change Proposal entra primero como issue y pasa por la autoridad de cambio antes de tocar el PRD"'
            ' --campo "CL-03:categoria=especificacion" --campo "CL-03:responsable_seguimiento=Martín Suárez"', repo)
IDR = dict(re.findall(r"^([A-Z]{2}-\d+) → ([A-Z]+-\d+)", out_r, re.M))
L_SOC, L_DOD, L_SCP, A_DOD, A_SCP = IDR["CL-01"], IDR["CL-02"], IDR["CL-03"], IDR["CM-01"], IDR["CM-02"]
CLAS = f'--por "Gestor: Martín Suárez" --fecha 2027-02-26'
run(f'{LECC} clasificar {L_SCP} --proyecto {G} --impacto alto --recurrencia media --aplicar-en planificacion,seguimiento {CLAS}', repo)
run(f'{LECC} clasificar {L_DOD} --proyecto {G} --impacto medio --recurrencia alta --aplicar-en seguimiento {CLAS}', repo)
run(f'{LECC} clasificar {L_SOC} --proyecto {G} --impacto medio --recurrencia baja --aplicar-en descubrimiento {CLAS}', repo)
run(f'{LECC} listar --proyecto {G} --corte 2027-02-26', repo)
sanidad("2027-02-26")
run(f'{LECC} accionar {L_DOD} --proyecto {G} --accion "{A_DOD}; definición de terminado del sprint 5" --verificar-en 2027-03-19 {CLAS}', repo)

P("Paso 7 · Fin de la etapa 2 (Release 1): prueba de carga NFR-3, gate en PASS que reemplaza al CONCERNS, condición cumplida, lecciones en el plan de la etapa 3, business case 1.1 y puerta autorizar-etapa (Release 2)")
act(repo, "acciones", A_DOD, estado="completada", fecha_cierre="2027-03-03", notas="definición de terminado actualizada: ninguna historia pasa a done sin su revisión registrada en calidad.csv")
act(repo, "acciones", A_SCP, estado="completada", fecha_cierre="2027-03-03", notas="plantilla del issue para toda Sprint Change Proposal (antes de tocar el PRD)")
act(repo, "calidad", qc, resultado="aprobado", estado="completada", fecha_real="2027-03-02", notas="p95 2,4 s con 400 sesiones concurrentes (meta menor a 3 s)")
run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2027-03-03'), repo)
# vigencia: el PASS reemplaza solo al CONCERNS del 26/11 (puertas.py completa reemplaza: mismo nivel, gestor, y fecha
# posterior), como las líneas base 1.1 a las 1.0
D_GATE = {f["decision"].split(" — ")[0]: f for f in csv.DictReader(open(os.path.join(repo, G, "03-control/registros/decisiones.csv"), encoding="utf-8")) if f["decision"].startswith("gate de preparación de BMAD")}
assert D_GATE["gate de preparación de BMAD: PASS"]["reemplaza"] == D_GATE["gate de preparación de BMAD: CONCERNS"]["id"], "el PASS del gate no reemplazó al CONCERNS"
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-03-05', repo)
run(E(f'estado.py --proyecto {G} limite-etapa'), repo)
run(E(f'evm.py --pv 82000 --ev 80000 --ac 83500 --bac 130000 --proyecto {G} --guardar --corte 2027-03-05'), repo)
art(repo, "informe-fin-etapa-2", "03-control/reportes/2027-03-05-informe-fin-etapa-2.md")
art(repo, "plan-etapa-3", "02-planificacion/plan-etapa-3.md", texto="# Plan de la etapa 3 (Release 2)\n\nSprints 5 a 7 (historias 2-1 a 2-4, con FR-13 de C-001).\n")
run(f'{LECC} listar --proyecto {G} --para planificacion --corte 2027-03-05', repo)
doc("business-case", "00-direccion/business-case.md", """# Business case v1.1 (modo mantener, fin de la etapa 2)
B-01 desvío de consultas (SM-2); B-02 adopción (SM-1); B-03 eficiencia de préstamos (SM-3).
Costos: AC 83.500 contra PV 82.000; EAC 135.688 contra BAC 130.000 (124.000 + 6.000 de C-001, cargado al presupuesto de cambio): +4,4 %, dentro de ±8 %.
Beneficios: sin medición todavía (primera revisión 30/6/2027 según el enfoque de beneficios); FR-13 (C-001) refuerza B-01.
Riesgos: sin riesgos altos abiertos; NFR-3 verificada con prueba de carga; R-001 (medio) amenaza B-02 adopción, con respuesta del negocio (alta asistida).
Veredicto: sigue deseable, viable y alcanzable → continuar con la etapa 3.""", version="1.1", origen="pm-caso-de-negocio, modo mantener")
run(E(f'puertas.py --proyecto {G} verificar autorizar-etapa'), repo, ok=(0, 1, 2))
PLAN3 = f"""# Plan de la etapa 3 (Release 2)
Sprints 5 a 7 (historias 2-1 a 2-4, con FR-13 de C-001).
## Lecciones incorporadas
| Lección | Qué cambia en este plan | Acción | Verificación |
|---|---|---|---|
| {L_SCP} (impacto alto) | toda Sprint Change Proposal de la etapa entra primero como issue y pasa por la autoridad de cambio antes de tocar el PRD | {A_SCP} plantilla del issue | 12/5, al cerrar el Release 2 |
| {L_DOD} (impacto medio) | la definición de terminado exige la revisión registrada (seguimiento en cada sprint) | {A_DOD} | 19/3, fin del sprint 5 |
"""
art(repo, "plan-etapa-3", "02-planificacion/plan-etapa-3.md", texto=PLAN3)
LOG.append(("(pm-plan-etapa-y-limites → gestion/02-planificacion/plan-etapa-3.md, sección «Lecciones incorporadas»)", PLAN3.strip()))
run(f'{LECC} accionar {L_SCP} --proyecto {G} --accion "{A_SCP}; plan-etapa-3" --verificar-en 2027-05-12 --por "Gestor: Martín Suárez" --fecha 2027-03-05', repo)
run(f'{LECC} informe --proyecto {G} --etapa 2 --corte 2027-03-05', repo)
run(E(f'estado.py --proyecto {G} artefacto informe-lecciones-etapa-2 --ruta 03-control/reportes/2027-03-05-informe-lecciones-etapa-2.md --estado en-revision'), repo, mostrar=False)
run(E(f'estado.py --proyecto {G} cumplir-condiciones autorizar-etapa --fecha 2027-03-05 --por "Ejecutivo: Laura Méndez" --nota "{qc} prueba de carga NFR-3 aprobada el 2027-03-02 (p95 2,4 s); gate de preparación de BMAD en PASS el 2027-03-03"'), repo)
sanidad("2027-03-05")
# antes de la puerta, la junta ve solo las decisiones vigentes sobre BMAD, cada una con su cadena de reemplazos
s_vig = run(f'python3 {RAIZ}/skills/pm-direccion-decisiones/scripts/decision.py --proyecto {G} vigentes --tema BMAD --corte 2027-03-05', repo)
av = [f for f in csv.DictReader(open(os.path.join(repo, G, "03-control/reportes/avance-bmad.csv"), encoding="utf-8")) if f["fecha"] in ("2026-12-23", "2027-03-05")]
it = [{"fecha": f["fecha"], "nombre": f["fecha"], "planificado": 16 if i == 0 else 34} for i, f in enumerate(av)]   # cierre de cada etapa: nombre y plan, del gestor
obj4 = [   # tiempo, costo, calidad y riesgo: semáforo por regla (estado.py periodo); aquí solo el juicio y las notas del gestor
        {"clave": "alcance", "pronostico": "Release 1 completa; FR-13 aprobado (C-001) para R2", "tol_etapa": "PO intercambia Should/Could", "tol_proyecto": "Must sin tolerancia", "rag": "verde"},
        {"clave": "calidad", "pronostico": "7 historias + NFR-3", "tol_proyecto": "cada historia con revisión"},
        {"clave": "beneficios", "pronostico": "se miden desde el 30/6/2027", "tol_etapa": "", "tol_proyecto": "-10 %", "rag": "na"},
        {"clave": "riesgo", "pronostico": "R-001 (medio) con respuesta"},
        {"clave": "sostenibilidad", "pronostico": "S-1 a S-3 sin desvíos previstos", "tol_etapa": "", "tol_proyecto": "-10 % sobre metas", "rag": "verde"}]
tablero(repo, "2027-03-05", "2027-02-19", "2027-03-05", "2027-03-19", obj4,
        [{"hito": "Release 1 aceptada", "base": "2027-03-05", "actual": "2027-03-05", "var_dias": 0, "rag": "verde", "comentario": "épicas 1 y 3 terminadas"},
         {"hito": "Release 2 (incluye FR-13)", "base": "2027-05-14", "actual": "2027-05-14", "var_dias": 0, "rag": "verde", "comentario": "C-001 aprobado"}],
        [{"id": "autorizar-etapa", "texto": "autorizar la etapa 3 (Release 2) con el plan, el informe de fin de etapa y el business case 1.1", "fecha_limite": "2027-03-05"}], it,
        "Release 1 entregada; la condición de NFR-3 se cumplió con la prueba de carga; el cambio FR-13 entró por control de cambios.",
        "", salida_png=os.path.join(OUT, "g4-tablero.png"), fecha_fija="2027-05-14", fecha_pronostico="2027-05-14", moneda="USD",
        mapas=True, salida_mapas_png=os.path.join(OUT, "g4-tablero-mapas-169.png"))
puerta4("autorizar-etapa", "Ejecutivo: Laura Méndez", "2027-03-05", '--etapa-nombre "Release 2" --fin 2027-05-14 --tol "tiempo=±10 %" "costo=±10 %"')
run(E(f'estado.py --proyecto {G} aprobar business-case --por "Ejecutivo: Laura Méndez" --version 1.1 --fecha 2027-03-05'), repo)

P("Paso 8 · Release 2: la acción de la retro se verifica en el sprint 5 (REG-12), revisiones con un rechazo tratado: corregir o conceder con la matriz (QUA-01 y QUA-03), la lección de impacto alto verificada y valor ganado final")
PLANIF = """WEBVTT

00:00:05.000 --> 00:00:25.000
<v Sofía Ramírez>Para el sprint 5 tomamos la historia 2-1, la solicitud guiada de préstamo, con sus ocho puntos.

00:00:30.000 --> 00:00:55.000
<v Lucía Benítez>Me encargo de la 2-1 y la llevo a revisión el 19/3, con la definición de terminado nueva.

00:01:00.000 --> 00:01:20.000
<v Martín Suárez>Decidimos que la 2-2 queda para el sprint 6.
"""
escribir(repo, "03-control/reuniones/2027-03-08-planificacion-sprint-5-original.vtt", PLANIF)
LOG.append(("(la planificación del sprint 5, otra reunión → gestion/03-control/reuniones/2027-03-08-planificacion-sprint-5-original.vtt)", PLANIF.strip()))
TR_P = f"{G}/03-control/reuniones/2027-03-08-planificacion-sprint-5-transcripcion.md"
run(f"{TRS} {G}/03-control/reuniones/2027-03-08-planificacion-sprint-5-original.vtt --salida {TR_P}", repo)
run(f"{XT} candidatos --transcripcion {TR_P}", repo)
poner_estados({"epic-2": "in-progress", "2-1-solicitud-guiada-de-préstamo-simple": "done"})
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
q_s5 = revision("2-1", "Sprint 5", "2027-03-19", notas=f"revisión registrada el día del done (definición de terminado, {A_DOD})")
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-03-22', repo)
sanidad("2027-03-22")
run(E(f'estado.py --proyecto {G} radar --corte 2027-03-22'), repo)
run(f'{LECC} listar --proyecto {G} --para seguimiento --corte 2027-03-22', repo)
run(f'{LECC} verificar {L_DOD} --proyecto {G} --resultado efectiva --evidencia "sprint 5: la historia 2-1 pasó a done con {q_s5} registrada el mismo día (19/3); sanidad del 22/3 sin QUA-01" --por "Gestor: Martín Suárez" --fecha 2027-03-22', repo)
poner_estados({k: "done" for k in ["epic-2", "2-2-seguimiento-de-solicitudes-y-respuesta-a-pedidos-de-informac", "2-3-actualización-de-datos-de-contacto-con-verificación", "2-4-pago-de-cuotas-con-débito-en-cuenta"]})
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
q_r2 = [q_s5] + [revision(k, "Release 2", "2027-05-06") for k in ("2-2", "2-3")]
# BMAD la marcó done (code-review aprobado), pero la revisión contra los criterios de aceptación la rechaza
q_rech = revision("2-4", "Release 2", "2027-05-06", resultado="rechazado", notas="falta la notificación al socio después del débito (criterio de aceptación de FR-13)")
sanidad("2027-05-07")
foto_calidad("7/5 · Release 2, un rechazo", "2027-05-07")
i2 = reg(repo, "issues", fecha="2027-05-07", tipo="fuera-especificacion", titulo=f"Historia 2-4 rechazada en {q_rech}: falta la notificación del débito", descripcion=f"La revisión {q_rech} rechazó la historia 2-4 (FR-13): el débito se hace pero el socio no recibe la notificación", prioridad="alta", severidad="mayor", responsable="Lucía Benítez")
# fuera de especificación: PRINCE2 admite corregir o conceder; pm-direccion-decisiones compara las dos en una hoja con pesos
# y puntajes con fuente (los redacta el modelo con la autoridad de cambio; el script calcula) y Sofía elige
DEC = f"python3 {RAIZ}/skills/pm-direccion-decisiones/scripts/decision.py --proyecto {G}"
run(f'{DEC} matriz {i2} --proponer --tipo cambio --ids {i2},{q_rech} --pregunta "¿Corregir la historia 2-4 dentro del Release 2 o concederla sin la notificación?"', repo)
HOJA = f"03-control/decisiones/{i2}"
CRIT = """criterio,descripcion,peso,sentido,escala,eliminatorio,importar,fuente_peso,notas
impacto,Efecto sobre FR-13 y los beneficios B-01 y B-02 (1 = muy negativo; 5 = muy positivo),40,mayor,1-5,,,pesos de la plantilla de tipo cambio confirmados por la autoridad de cambio,
tolerancias,Margen dentro de las tolerancias de la etapa 3 (1 = fuera: excepción; 5 = holgado),35,mayor,1-5,,,pesos de la plantilla de tipo cambio confirmados por la autoridad de cambio,
autoridad,Dentro de la autoridad de cambio y sin costo (1 = no; 5 = sí),25,mayor,1-5,,,pesos de la plantilla de tipo cambio confirmados por la autoridad de cambio,
"""
OPC = f"""opcion,descripcion,ref,impacto,impacto_fuente,tolerancias,tolerancias_fuente,autoridad,autoridad_fuente,notas
O1,Corregir dentro del Release 2 y volver a revisar la historia,,4,{q_rech}: falta solo la notificación; FR-13 completo al salir a producción,4,4 días de los 7 que quedan hasta el fin de la etapa (14/5),5,sin costo ni cambio de alcance (PID §8),
O2,Conceder: aceptar la historia 2-4 sin la notificación y actualizar su descripción de producto,,2,el socio no sabe que se debitó su cuenta: reclamos en contra de B-01 y B-02,5,sin trabajo adicional en la etapa,4,concesión dentro de la autoridad de cambio (PID §8),
"""
escribir(repo, f"{HOJA}/criterios.csv", CRIT); escribir(repo, f"{HOJA}/opciones.csv", OPC)
LOG.append((f"(pm-direccion-decisiones completa la hoja con Sofía Ramírez, autoridad de cambio → gestion/{HOJA}/criterios.csv y opciones.csv)", CRIT.strip() + "\n\n" + OPC.strip()))
run(f'{DEC} matriz {i2}', repo)
out_d = run(f'{DEC} matriz {i2} --elegir O1 --por "Autoridad de cambio: Sofía Ramírez" --fecha 2027-05-07', repo)
d_off = re.search(r"decisión (D-\d+)", out_d).group(1)
act(repo, "issues", i2, estado="en-accion", decision=f"{d_off}: corregir dentro del Release 2, sin costo ni cambio de alcance (concesión descartada)", decidido_por="Autoridad de cambio: Sofía Ramírez")
q_re = revision("2-4", "Release 2", "2027-05-11", notas=f"nueva revisión después de corregir lo observado en {q_rech} ({i2}): notificación verificada")
act(repo, "issues", i2, estado="cerrado", fecha_cierre="2027-05-11", notas=f"corregido; {q_re} aprobada")
run(f'python3 {BMAD} --proyecto {G} avance --corte 2027-05-12', repo)
run(E(f'evm.py --pv 130000 --ev 130000 --ac 133000 --bac 130000 --tol-costo 8 --tol-plazo 10 --proyecto {G} --guardar --corte 2027-05-12'), repo)
sanidad("2027-05-12")
foto_calidad("12/5 · fin del Release 2", "2027-05-12")
run(f'{LECC} verificar {L_SCP} --proyecto {G} --resultado efectiva --evidencia "Release 2: el rechazo de la historia 2-4 entró como {i2} y se corrigió sin tocar la especificación; ninguna Sprint Change Proposal llegó al PRD sin issue (sanidades del 7/5 y del 12/5 sin ESP-10)" --por "Gestor: Martín Suárez" --fecha 2027-05-12', repo)

P("Paso 9 · Aceptación, traspaso a operación, business case confirmado y puerta autorizar-cierre")
run(E(f'especificacion.py --proyecto {G} listar requisitos --cobertura sin-cobertura'), repo)
run(E(f'especificacion.py --proyecto {G} resumen'), repo)
run(E(f'estado.py --proyecto {G} cierre'), repo)
run(E(f'puertas.py --proyecto {G} verificar autorizar-cierre'), repo, ok=(0, 1, 2))   # qué falta para la puerta, por id (C-03, C-07)
art(repo, "registro-aceptacion", "04-cierre/registro-aceptacion.md")
run(E(f'estado.py --proyecto {G} aprobar registro-aceptacion --por "Usuario sénior: Sofía Ramírez; Ejecutivo: Laura Méndez" --version 1.0 --fecha 2027-05-12'), repo)
run(E(f'estado.py --proyecto {G} productos --corte 2027-05-12 --markdown {G}/04-cierre/product-status-account-final.md'), repo)
art(repo, "product-status-account-final", "04-cierre/product-status-account-final.md")
psa = open(os.path.join(repo, G, "04-cierre/product-status-account-final.md"), encoding="utf-8").read()
LOG.append(("(estado.py productos --markdown → gestion/04-cierre/product-status-account-final.md: resumen y desviaciones)",
            "\n".join(l for l in psa.splitlines() if l.startswith(("| No iniciado", "| En revisión", "| Aprobado", "| Aceptado", "| Fuera de", "| **Total", "**Fuera de", "**Discrepancias", "Must sin")))))
qs_ = list(csv.DictReader(open(os.path.join(repo, G, "03-control/registros/calidad.csv"), encoding="utf-8")))
n_apr = sum(1 for q in qs_ if q["resultado"] in ("aprobado", "aprobado-con-observaciones")); n_rech = sum(1 for q in qs_ if q["resultado"] == "rechazado")
doc("handover", "04-cierre/handover.md", f"""# Transferencia a operación y mantenimiento v1.0
Productos: portal del socio y consola de operador (13 FR, 11 historias; líneas base PRD y épicas 1.1), aceptados en registro-aceptacion v1.0.
Propietario receptor: usuaria sénior Sofía Ramírez (servicios al socio); mantenimiento: equipo de Lucía Benítez durante 90 días de garantía.
Evidencia de calidad: {len(qs_)} revisiones en calidad.csv: {n_apr} aprobadas (una por historia y la prueba de carga NFR-3) y {n_rech} rechazada ({q_rech}, tratada en {i2} y aprobada en {q_re}).
Pendientes: observación menor de {q_r1[-1]} en el backlog de mantenimiento. Costos de operación: desde el 15/5/2027, a cargo del negocio.
5. Confirmación del receptor: Sofía Ramírez, 2027-05-12.""", origen="pm-cierre-proyecto, templates/handover.md")
run(E(f'estado.py --proyecto {G} aprobar handover --por "Usuario sénior: Sofía Ramírez" --version 1.0 --fecha 2027-05-12'), repo)
art(repo, "informe-fin-proyecto", "04-cierre/informe-fin-proyecto.md")
run(f'{LECC} accionar {L_SOC} --proyecto {G} --accion "propuesta a la PMO: revisar el recorrido con usuarios reales antes de cerrar cada release" --destino organizacion --por "Ejecutivo: Laura Méndez" --fecha 2027-05-12', repo)
INF = run(f'{LECC} informe --proyecto {G} --corte 2027-05-12 --exportar pmo/lecciones-indice.csv --por "Ejecutivo: Laura Méndez"', repo)
LOG.append(("(lecciones.py informe → gestion/04-cierre/informe-lecciones.md)", open(os.path.join(repo, G, "04-cierre", "informe-lecciones.md"), encoding="utf-8").read().strip()))
run(E(f'estado.py --proyecto {G} artefacto informe-lecciones --ruta 04-cierre/informe-lecciones.md --estado en-revision'), repo, mostrar=False)
B_IX = run(f'{LECC} buscar --indice pmo/lecciones-indice.csv --para descubrimiento', repo)
doc("recomendaciones-seguimiento", "04-cierre/recomendaciones-seguimiento.md", f"""# Recomendaciones de acciones de seguimiento v1.0
| Origen | Recomendación | Responsable | Cuándo |
|---|---|---|---|
| {r1} adopción (recorrido UJ-1, P1) | sostener la alta asistida en sucursal y por teléfono; revisar el riesgo con los datos de adopción | Sofía Ramírez (servicios al socio) | revisión de beneficios del 30/6/2027 |
| {q_r1[-1]} observación menor | filtro de la bandeja de la consola: ajustar en el backlog de mantenimiento | Lucía Benítez (garantía de 90 días) | antes del 15/8/2027 |""", origen="pm-cierre-proyecto, templates/recomendaciones-seguimiento.md")
doc("plan-revision-beneficios", "04-cierre/plan-revision-beneficios.md", """# Plan de revisión de beneficios v1.0
Responsable de las revisiones: el negocio (usuaria sénior Sofía Ramírez), con financiación de servicios al socio; el proyecto no las ejecuta.
Línea base de las mediciones: check-in del 2027-05-15 (entrada en operación) en okr_checkins.csv.
| Revisión | Fecha | Qué se mide | Criterio | Fuente |
|---|---|---|---|---|
| 1 (intermedia) | 2027-06-30 | B-01, B-02, B-03 y S-1 | salud contra la trayectoria (okr.py): en-riesgo o desviado → informe | okr_checkins.csv (KR-1.1 a KR-1.3) y SM-1 a SM-3 del PRD |
| 2 (final) | 2027-12-31 | metas finales y contramétricas SM-C1, SM-C2 | avance hacia la meta (puntuación de okr.py) menor que 0,90 = fuera de la tolerancia de beneficios (-10 %) → informe | ídem |
Informe de desvío: a la ejecutiva (Laura Méndez), que decide con el negocio la acción correctiva.""", origen="pm-cierre-proyecto, templates/plan-revision-beneficios.md")
doc("business-case", "00-direccion/business-case.md", """# Business case v1.2 (modo confirmar, cierre)
Real contra la línea base: AC 133.000 contra BAC 130.000 (+2,3 %, dentro de ±8 %); 13 FR y 11 historias (C-001); fin 2027-05-14 sin desvío.
Beneficios B-01 a B-03: todavía no realizados (el portal entra en operación el 15/5/2027); se confirman en las revisiones del plan de revisión de beneficios.
Traspaso: el enfoque de beneficios pasa al negocio (Sofía Ramírez), que ejecuta y financia las revisiones.
Veredicto: el proyecto entregó lo autorizado; la justificación depende ahora de la adopción (B-02).""", version="1.2", origen="pm-caso-de-negocio, modo confirmar")
doc("enfoque-beneficios", "00-direccion/enfoque-beneficios.md", """# Enfoque de gestión de beneficios v1.1
Gestionado por: negocio (usuaria sénior Sofía Ramírez) desde el 2027-05-14; revisiones según 04-cierre/plan-revision-beneficios.md.
Beneficios, medidas, líneas base, metas y tolerancia sin cambios respecto de la v1.0.""", version="1.1", origen="pm-caso-de-negocio, traspaso del enfoque de beneficios")
doc("notificacion-cierre", "04-cierre/notificacion-cierre.md", """# Notificación de cierre del proyecto (borrador)
Emisor: Laura Méndez, ejecutiva, en nombre de la junta. Destinatarios: Consejo, servicios al socio, operaciones y proveedores.
Contenido: el proyecto cierra el 2027-05-14; el portal queda a cargo de servicios al socio; las revisiones de beneficios las hace el negocio (30/6 y 31/12/2027).
Se emite solo después de la puerta autorizar-cierre.""", estado="borrador", origen="pm-cierre-proyecto, templates/notificacion-cierre.md")
puerta4("autorizar-cierre", "Ejecutivo: Laura Méndez", "2027-05-14")
run(E(f'estado.py --proyecto {G} aprobar business-case --por "Ejecutivo: Laura Méndez" --version 1.2 --fecha 2027-05-14'), repo)
run(E(f'estado.py --proyecto {G} aprobar enfoque-beneficios --por "Ejecutivo: Laura Méndez; Usuario sénior: Sofía Ramírez" --version 1.1 --fecha 2027-05-14'), repo)
reg(repo, "decisiones", fecha="2027-05-14", decision="Responsabilidad de los beneficios traspasada al negocio: Sofía Ramírez ejecuta y financia las revisiones del plan de revisión de beneficios (30/6 y 31/12/2027)", decidido_por="Ejecutivo: Laura Méndez", nivel="junta", artefactos_afectados="00-direccion/enfoque-beneficios.md; 04-cierre/plan-revision-beneficios.md")
run(E(f'estado.py --proyecto {G} aprobar notificacion-cierre --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2027-05-14'), repo)
PRD_VIVO = os.path.relpath(prd, repo); PRD_LB = f"{G}/00-direccion/historial/bmad-prd-v1.1/prd.md"
run(f'python3 {PAQ} --proyecto {G} cierre --extra {PRD_LB} {PRD_VIVO}', repo, ok=(0, 1))
import zipfile
zp = _g.glob(os.path.join(repo, G, "exportados", "*-paquete-cierre-*.zip"))[0]
man = zipfile.ZipFile(zp).read("MANIFIESTO.md").decode("utf-8").splitlines()
LOG.append(("(MANIFIESTO.md dentro del ZIP: estado del paquete, filas de --extra y nota de excluidos)",
            "\n".join(l for l in man if l.startswith(("**ESTADO", "| prd.md", "| (extra)", "> **Excluidos")))))
run(E(f'exportar.py xlsx --proyecto {G}'), repo, ok=(0, 1))
run(E(f'estado.py --proyecto {G} resumen'), repo)

P("Paso 9b · Expediente de auditoría para la auditoría externa, verificación de integridad y bitácora de escrituras")
import io
# HOME vacío solo en este comando: la sanidad completa que el expediente incluye no suma avisos de instalación (INS) que
# dependen de las skills de usuario del equipo donde corre el driver (las demás sanidades del recorrido usan --rapido)
def sin_hora(texto):
    """La bitácora anota la fecha y hora reales de cada escritura y huellas sha256 que dependen de ellas: en la evidencia se
    enmascaran para que dos corridas den lo mismo (el número de línea, el script, la operación, --por y los cambios quedan)."""
    texto = re.sub(r"#(\d+) \d{4}-\d{2}-\d{2} \d{2}:\d{2}", r"#\1 <fecha y hora de la escritura>", texto)
    return re.sub(r"sha256 (?:[0-9a-f]{12}|—) → [0-9a-f]{12}", "sha256 <antes> → <después>", texto)
def run_bit(cmd, **kw):
    out = run(cmd, repo, **kw); c_, o_ = LOG[-1]; LOG[-1] = (c_, sin_hora(o_)); return out
s_aud = run(f'HOME="$(mktemp -d)" python3 {PAQ} --proyecto {G} auditoria --hasta 2027-05-14 --proposito "auditoría externa" --externo --con-bitacora', repo)
za = _g.glob(os.path.join(repo, G, "exportados", "*-expediente-auditoria-*.zip"))[0]; za_rel = os.path.relpath(za, repo)
s_ver = run(f'python3 {PAQ} --proyecto {G} verificar {za_rel}', repo)
zz = zipfile.ZipFile(za)
n_bit = zz.read("bitacora.jsonl").count(b"\n")
crono = list(csv.DictReader(io.StringIO(zz.read("cronologia.csv").decode("utf-8"))))
indice = zz.read("INDICE.md").decode("utf-8")
LOG.append(("(INDICE.md dentro del ZIP: propósito, conteo de la cronología, registros omitidos por destinatario externo y hallazgos de sanidad al corte)",
            re.sub(r"generado: \d{4}-\d{2}-\d{2}", "generado: <fecha de la corrida>",
                   "\n".join(l for l in indice.splitlines() if l.startswith(("Proyecto:", "Copia de los registros", "bitacora.jsonl:", "ERROR ", "| ERROR", "| AVISO", "| INFO")) or " eventos (también" in l))))
# la copia que recibe la auditoría: alguien cambia «condicionado» por «aprobado» en la fila de la puerta D-013
COPIA = os.path.join(repo, "copia-auditoria", "expediente-recibido.zip"); os.makedirs(os.path.dirname(COPIA), exist_ok=True)
with zipfile.ZipFile(COPIA, "w", zipfile.ZIP_DEFLATED) as zc:
    for n_ in zz.namelist():
        b_ = zz.read(n_)
        if n_ == "03-control/registros/decisiones.csv":
            b_ = b_.replace("autorizar-etapa: condicionado".encode("utf-8"), "autorizar-etapa: aprobado".encode("utf-8"), 1)
        zc.writestr(n_, b_)
LOG.append(("(copia del expediente que llega a la auditoría: una sola edición en decisiones.csv; el resto, idéntico)",
            "03-control/registros/decisiones.csv, fila D-013: «autorizar-etapa: condicionado — condiciones: …» → «autorizar-etapa: aprobado — condiciones: …»"))
s_alt = run_bit(f'python3 {PAQ} --proyecto {G} verificar copia-auditoria/expediente-recibido.zip', ok=(1,))
# ¿la fila D-013 dijo alguna vez «aprobado»? Aseguramiento consulta en el proyecto qué escribieron los scripts sobre D-013
s_his = run_bit(E(f'registro.py --proyecto {G} historial D-013'))
n_d013 = len(re.findall(r"^#\d+ ", s_his, re.M))

# ---------------------------------------------------------------- gráficos de ejecución y cierre (datos reales de la corrida)
MES = {"01": "ene", "02": "feb", "03": "mar", "04": "abr", "05": "may", "06": "jun", "07": "jul", "08": "ago", "09": "sep", "10": "oct", "11": "nov", "12": "dic"}
fcorta = lambda d: f"{int(d[8:10])}-{MES[d[5:7]]}"
LX_ = {f["id"]: f for f in csv.DictReader(open(os.path.join(repo, G, "03-control/registros/lecciones.csv"), encoding="utf-8"))}
IX_ = list(csv.DictReader(open(os.path.join(repo, "pmo", "lecciones-indice.csv"), encoding="utf-8")))
ver_ = [i for i, f in LX_.items() if f["estado"] == "verificada"]; acc_p = [i for i, f in LX_.items() if f["accion"] and "accionada-organizacion" != f["estado"]]
imp_ = {k: sum(1 for f in LX_.values() if f["impacto"] == k) for k in ("alto", "medio", "bajo")}
d_dod = LX_[L_DOD]["verificacion"].split(" · ")[0]; d_scp = LX_[L_SCP]["verificacion"].split(" · ")[0]
dm = lambda d: f"{int(d[8:10])}/{int(d[5:7])}"
V.tarjetas([(str(N_CL), "lecciones de la retrospectiva", f"sprint 4 (26/2): {N_CL} con cita, {N_CM} acciones de mejora, {N_GOB} decisiones", None),
            (f"{imp_['alto']} alto", f"impacto: {imp_['medio']} medio, {imp_['bajo']} bajo", " · ".join(f"{i} {LX_[i]['aplicar_en'].split(';')[0].replace('planificacion', 'planificación')}" for i in (L_SCP, L_DOD, L_SOC)), None),
            (A_DOD, f"acción de {L_DOD} (sprint 5)", f"REG-12 al vencer; verificada efectiva el {dm(d_dod)}", None),
            ("plan-etapa-3", f"cambia por {L_SCP} (alto)", f"E-11 el 5/3; {A_SCP} verificada el {dm(d_scp)}", None),
            (f"{len(ver_)} de {len(acc_p)}", "acciones verificadas", "efectivas; REG-11 y REG-12 en cero al cierre", "bien" if len(ver_) == len(acc_p) else "critico"),
            (str(len(IX_)), "lecciones en el índice", f"--para descubrimiento devuelve {L_SOC} (PMO)", None)],
           os.path.join(OUT, "g4-lecciones-ciclo.png"), "De la retrospectiva al índice: cada acción en el proyecto se verificó",
           "Ciclo de las lecciones del sprint 4 al cierre (14/5/2027): captura, impacto, acción, verificación e índice",
           "2027-02-26-retro-sprint-4-candidatos.json · lecciones.csv · pmo/lecciones-indice.csv")
sin_rev = [(e, n - k) for e, n, k in FOTOS if n > k]
V.barras_comparadas([f"{e} ({k} de {n})" for e, n, k in FOTOS], [[n for _, n, _ in FOTOS], [k for _, _, k in FOTOS]], os.path.join(OUT, "g4-calidad-entregas.png"),
                    "Ninguna entrega pasó la puerta con historias sin revisión aprobada",
                    "QUA-01 marcó historias sin revisión aprobada: " + " y ".join(f"{d} el {e.split(' · ')[0]}" for e, d in sin_rev) + ("; las dos brechas se cerraron" if len(sin_rev) == 2 else "; se cerraron") + " antes de la puerta siguiente",
                    "estado.py productos --corte <fecha> --json (backlog.csv done; calidad.csv: revisión aprobada que cita «historia N-M»)", nombres=["Historias terminadas (done)", "Con revisión aprobada"], leyenda="arriba")
av_all = list(csv.DictReader(open(os.path.join(repo, G, "03-control/reportes/avance-bmad.csv"), encoding="utf-8")))
tot = [float(f["puntos_total"]) for f in av_all]; hech = [float(f["puntos_terminados"]) for f in av_all]
V.lineas([fcorta(f["fecha"]) for f in av_all], [tot, hech], os.path.join(OUT, "g4-burnup.png"),
         f"C-001 sumó {V.miles(tot[-1] - tot[0])} puntos y aun así se terminó a tiempo",
         "Puntos por corte (bmad.py avance) · C-001 entra el 20/1 · fin previsto y real: 14/5",
         "03-control/reportes/avance-bmad.csv", nombres=["Alcance", "Terminado"], unidad=" pts")
evm_f = json.load(open(os.path.join(repo, G, "03-control/reportes/evm-2027-05-12.json"), encoding="utf-8"))
est_f = json.load(open(os.path.join(repo, G, "estado.json"), encoding="utf-8"))
cam = list(csv.DictReader(open(os.path.join(repo, G, "03-control/registros/cambios.csv"), encoding="utf-8")))
usado = sum(float(c["costo"] or 0) for c in cam if c["cargo"] == "presupuesto-cambio"); tope = float(est_f["presupuestos"]["cambio"])
abiertas = sum(1 for pz in est_f["puertas"] if pz.get("condiciones") and not pz.get("condiciones_cumplidas"))
pf_ = productos_json("2027-05-14")   # estado de productos al cierre (el mismo que lee C-07)
n_acc = pf_["conteos"]["aceptado"]; n_must = len(pf_["must"]["requisitos"]) + len(pf_["must"]["productos"])
V.tarjetas([(f"{n_acc} de {pf_['total']}", "productos aceptados", f"{n_must} Must sin aceptar (C-07); el rechazo de la 2-4 se trató en {i2}", "bien" if n_acc == pf_["total"] and not n_must else "critico"),
            (f"CPI {V.miles(evm_f['CPI'], 3)}", "costo final", f"+{V.miles(evm_f['sobrecosto_pct'], 1)} % contra BAC {V.miles(evm_f['BAC'])}; tolerancia ±8 %", "bien" if not evm_f["excepcion_prevista"] else "critico"),
            (f"{100 * usado / tope:.0f} %", "presupuesto de cambio usado", f"USD {V.miles(usado)} de {V.miles(tope)} (C-001)", "bien"),
            (str(abiertas), "condiciones abiertas al cierre", "la de NFR-3 (CONCERNS de BMAD) se cumplió el 5/3", "bien" if abiertas == 0 else "critico"),
            (f"{V.miles(hech[-1])} de {V.miles(tot[-1])}", "puntos terminados", f"{V.miles(tot[0])} de línea base + {V.miles(tot[-1] - tot[0])} por control de cambios", "bien"),
            ("2", "revisiones de beneficios", "a cargo del negocio: 30/6 y 31/12/2027", None)],
           os.path.join(OUT, "g4-cierre.png"), "El proyecto cierra sin condiciones abiertas y con cada producto aceptado",
           "Tablero de una página para la puerta autorizar-cierre (14/5/2027)", "estado.py productos · calidad.csv · evm-2027-05-12.json · cambios.csv · estado.json · avance-bmad.csv")
m_aud = re.search(r"(\d+) archivos · (\d+) eventos en la cronología · registros (\d+)", s_aud)
m_lb = re.search(r"lineas-base (\d+)", s_aud); m_ok = re.search(r"INTEGRIDAD: OK · (\d+) archivos", s_ver)
m_alt = re.search(r"INTEGRIDAD: FALLA · (\d+) problema", s_alt); alterado = re.search(r"alterado: (\S+)", s_alt).group(1)
tipos = {}
for e_ in crono: tipos[e_["tipo"]] = tipos.get(e_["tipo"], 0) + 1
V.tarjetas([(m_aud.group(2), "eventos en la cronología", f"{tipos.get('puerta', 0)} puertas · {tipos.get('cambio', 0)} cambio · {tipos.get('aceptacion-producto', 0)} productos aceptados · {tipos.get('decision', 0) + tipos.get('aprobacion', 0)} decisiones", None),
            (m_lb.group(1), "copias congeladas (líneas base)", "PRD y épicas 1.0 y 1.1, business case, PID, enfoques, WP-001 y cierre", None),
            (m_aud.group(3), "registros copiados", "sin stakeholders.csv: destinatario externo (--externo)", None),
            (str(n_bit), "escrituras en la bitácora", f"cadena íntegra; D-013: {n_d013} escritura{'s' if n_d013 != 1 else ''}, «condicionado»", None),
            ("OK", "integridad del expediente", f"los {m_ok.group(1)} archivos coinciden con SHA256SUMS", "bien"),
            (m_alt.group(1), f"archivo alterado: {alterado.split('/')[-1]}", "D-013 dice «aprobado»; no salió de los scripts", "critico")],
           os.path.join(OUT, "g4-expediente.png"), "Una edición en la copia: la verificación la delata y la bitácora la explica",
           "Expediente de auditoría al 14/5/2027 para la auditoría externa (paquete.py auditoria --externo --con-bitacora) y su verificación",
           "cronologia.csv, SHA256SUMS y bitacora.jsonl del expediente · paquete.py verificar · registro.py historial D-013")

P("Paso 9c · Versiones y auditoría con pm-kb: qué cambió en el business case y la historia de una fila")
# pm-kb es opcional: sin el lanzador o sin su base, el paso se omite y el recorrido sigue. Solo lee la carpeta: no
# escribe en el proyecto ni en la bitácora.
if not kb_disponible():
    kb_omitido("paso 9c (versiones del business case e historia de D-013)")
else:
    KP = "--proyecto producto-bmad"
    kb(f'indexar {KP} --ruta .', repo)
    kb(f'versiones business-case {KP}', repo)
    kb(f'cambios business-case {KP}', repo)
    for filtro in ("", " --aprobado", " --historia"):    # la vigente, la última aprobada y todas las versiones
        kb(f'buscar "veredicto del business case al fin de la etapa 2" {KP}{filtro} --k 2', repo)
    kb(f'ficha D-013 --historia {KP}', repo)
    kb(f'quitar {KP}', repo)

P("Paso 10 · Después del proyecto: primera revisión de beneficios del negocio (30/6/2027)")
CK = f'python3 {OKR} {G}/00-direccion/okr.csv --checkin'
for kr, v in (("KR-1.1", "0"), ("KR-1.2", "5000"), ("KR-1.3", "96")):
    run(f'{CK} {kr} --valor {v} --fecha 2027-05-15 --autor "Usuario sénior: Sofía Ramírez" --nota "línea base al entrar en operación"', repo)
for kr, v in (("KR-1.1", "9"), ("KR-1.2", "4600"), ("KR-1.3", "70")):
    run(f'{CK} {kr} --valor {v} --fecha 2027-06-30 --confianza 6 --autor "Usuario sénior: Sofía Ramírez" --nota "revisión 1 del plan de revisión de beneficios"', repo)
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2027-06-30 --markdown {G}/03-control/reportes/2027-06-30-okr.md', repo)

P("Paso 11 · Después del proyecto: revisión final de beneficios (31/12/2027) y desvío fuera de tolerancia")
for kr, v in (("KR-1.1", "25"), ("KR-1.2", "3600"), ("KR-1.3", "50")):
    run(f'{CK} {kr} --valor {v} --fecha 2027-12-31 --confianza 7 --autor "Usuario sénior: Sofía Ramírez" --nota "revisión 2 (final) del plan de revisión de beneficios"', repo)
run(f'python3 {OKR} {G}/00-direccion/okr.csv --corte 2027-12-31 --markdown {G}/03-control/reportes/2027-12-31-okr.md', repo)
def okr_json(corte):
    r = subprocess.run(["python3", OKR, f"{G}/00-direccion/okr.csv", "--corte", corte, "--json"], cwd=repo, capture_output=True, text=True, check=True)
    return {k["id"]: k for o in json.loads(r.stdout)["objetivos"] for k in o["krs"]}
k1, k2 = okr_json("2027-06-30"), okr_json("2027-12-31")
fuera = [k for k in ("KR-1.1", "KR-1.2", "KR-1.3") if k2[k]["puntuacion"] < 0.9]
reg(repo, "decisiones", fecha="2028-01-10", decision="Revisión final de beneficios: " + "; ".join(f"{k} {V.miles(100 * k2[k]['puntuacion'])} % de avance hacia la meta" for k in ("KR-1.1", "KR-1.2", "KR-1.3")) + f". Fuera de la tolerancia de beneficios (-10 %): {', '.join(fuera) or 'ninguno'}. Causa a investigar primero: {r1} (primer ingreso con segundo factor, recorrido UJ-1 P1). Se informa a la ejecutiva Laura Méndez, que decide con el negocio la acción correctiva", decidido_por="Usuario sénior: Sofía Ramírez", nivel="capa-negocio", artefactos_afectados="04-cierre/plan-revision-beneficios.md; 03-control/reportes/2027-12-31-okr.md")
nom = {"KR-1.1": "B-02 adopción", "KR-1.2": "B-01 desvío de consultas", "KR-1.3": "B-03 préstamos en < 48 h"}
V.estados([(f"{nom[k]} (30/6: {V.miles(100 * k1[k]['puntuacion'])} %)", 100 * k2[k]["puntuacion"], "critico" if k in fuera else "bien",
            "✖ fuera de tolerancia (< 90 %)" if k in fuera else "✔ dentro de tolerancia") for k in ("KR-1.1", "KR-1.2", "KR-1.3")],
          os.path.join(OUT, "g4-beneficios.png"),
          (f"Revisión final: {', '.join(nom[k] for k in fuera)} queda fuera de la tolerancia" if fuera else "Revisión final: los tres beneficios dentro de la tolerancia"),
          f"Avance hacia la meta al 31/12/2027 (puntuación de okr.py × 100). Entre paréntesis, la revisión del 30/6 (esperado {V.miles(100 * k1['KR-1.1']['esperado'])} %)",
          "okr.csv y okr_checkins.csv (check-ins del negocio)", maximo=100, decimales=0, sufijo=" %")

LOG_path = sys.argv[1] if len(sys.argv) > 1 else "salida-g4.md"
with open(LOG_path, "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
