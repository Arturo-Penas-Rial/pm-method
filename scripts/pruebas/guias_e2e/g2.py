"""Guía E2E-2 · Alcance y su cambio, estimación de esfuerzo, priorización y mapa de ruta (scripts reales)."""
from comun import *
import math
repo = proyecto("portal-socios"); print("REPO", repo)
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))
WBS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wbs.csv"), encoding="utf-8").read()
import visuales as V, io
OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
png = lambda nombre: os.path.join(OUT, f"g2-{nombre}.png")
num = lambda x, d=0: V.miles(x, d)                 # 12.000 · 6,51 (formato es-UY)
corta = lambda f: f"{int(f[8:10])}/{int(f[5:7])}/{f[:4]}"   # 2027-05-03 → 3/5/2027
TOL_DIAS = 15                                       # tolerancia de tiempo del proyecto: ±3 semanas = 15 días laborables


def cpm_tabla(salida):
    """Lee la tabla de texto de cpm.py (la misma que queda en la evidencia)."""
    filas = []
    for l in salida.split("\n"):
        m = re.match(r"^(A\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*?)\s*(\*)?$", l)
        if m:
            filas.append(dict(id=m[1], dur=int(m[2]), inicio=int(m[3]), fin=int(m[4]), holgura=int(m[7]),
                              nombre=m[9].replace(" [hito]", ""), hito="[hito]" in m[9], critica=bool(m[10])))
    total = int(re.search(r"Duración total \(días laborables\): (\d+)", salida)[1])
    fin = re.search(r"Fin previsto: (\S+)", salida)[1]
    camino = re.search(r"Camino crítico: (.*)", salida)[1].strip().split(" -> ")
    return {f["id"]: f for f in filas}, total, fin, camino


IMP = f"{RAIZ}/skills/pm-issues-cambios/scripts/impacto.py"
REL = f"{RAIZ}/skills/pm-agil-hibrido/scripts/release.py"


def impacto(repo, cid, args, fecha):
    """Análisis de impacto ANTES de decidir (pm-issues-cambios: impacto.py analizar). El texto y la sección 3 a 6 del borrador
    de la solicitud de cambio quedan en la evidencia; devuelve el --json para las cifras de la guía y los gráficos."""
    cmd = f'python3 {IMP} --proyecto {G} analizar {cid} {args} --fecha {fecha}'
    run(cmd, repo)
    r = json.loads(subprocess.run(cmd + " --json", shell=True, cwd=repo, capture_output=True, text=True, check=True).stdout)
    md = open(os.path.join(repo, r["salida"]), encoding="utf-8").read()
    LOG.append((f"(borrador {r['salida']}: §3 análisis de impacto a §6 autoridad y decisión)", md[md.index("## 3."):md.index("**Disposición")].strip()))
    return r


def cobertura(repo, con_backlog):
    """Cobertura de trazabilidad recalculada sobre matriz-trazabilidad-bmad.csv (bmad.py trazabilidad), backlog.csv y las
    descripciones de producto. Devuelve filas (etiqueta, cumplen, total, detalle)."""
    mz = list(csv.DictReader(open(os.path.join(repo, G, "02-planificacion/especificacion/matriz-trazabilidad-bmad.csv"), encoding="utf-8")))
    fr = [f for f in mz if f["requisito"].startswith("FR-")]
    nfr = [f for f in mz if f["requisito"].startswith("NFR-")]
    docs = "".join(open(os.path.join(repo, G, r), encoding="utf-8").read() for r in ("02-planificacion/descripcion-producto-proyecto.md", "02-planificacion/productos/3.1-acceso-seguro.md"))
    nfr_ok = [f["requisito"] for f in nfr if f["paquetes_wbs"] or re.search(rf"\b{f['requisito']}\b(?!\d)", docs)]
    filas = [("Requisitos (FR) con historia", sum(f["cubierto"] == "si" for f in fr), len(fr), "bmad.py trazabilidad"),
             ("Requisitos (FR) con paquete de la WBS", sum(bool(f["paquetes_wbs"]) for f in fr), len(fr), "columna ref de wbs.csv")]
    if con_backlog:  # etiquetas cortas: entran en el eje de los gráficos
        bl = list(csv.DictReader(open(os.path.join(repo, G, "02-planificacion/backlog.csv"), encoding="utf-8")))
        filas.append(("Historias con producto de la PBS", sum(bool(f["producto_pbs"]) for f in bl), len(bl), "columna producto_pbs"))
    filas += [("NFR con WBS o criterio de calidad", len(nfr_ok), len(nfr), "WBS o descripciones de producto"),
              ("Requisitos (FR) citados en su historia", sum(f["nivel_traza"] == "historia" for f in fr), len(fr), "el resto, solo a nivel de épica")]
    LOG.append(("(cobertura de trazabilidad recalculada en esta sincronización: matriz-trazabilidad-bmad.csv, backlog.csv y descripciones de producto)",
                "\n".join(f"{e}: {a} de {t} ({100 * a / t:.0f} %) · {d}" for e, a, t, d in filas)))
    return filas


def cam03(salida):
    m = re.search(r"Presupuesto de cambio(?: excedido)?: ([\d.]+) de ([\d.]+)", salida)
    return float(m[1].replace(".", "")), float(m[2].replace(".", ""))


# Business case: flujos anuales (t = 0 inversión; t = 1…5 los cinco años de operación) que da la usuaria sénior, dueña
# de los beneficios, con la tasa que fija finanzas. inversion.py calcula VAN, TIR, repago, sensibilidad y equilibrio.
INV = f"{RAIZ}/skills/pm-caso-de-negocio/scripts/inversion.py"
TASA, VARIACION = 0.10, 0.10            # tasa anual de la organización · sensibilidad ±10 % = tolerancia de beneficios
ANIOS = 5


def conceptos_base(bac):
    return [("Proyecto (BAC de la WBS)", "inversion", [-bac]),
            ("Operación y soporte", "costo", [0] + [-22000] * ANIOS),
            ("B-01 Desvío de consultas", "beneficio", [0, 30000] + [50000] * (ANIOS - 1)),
            ("B-03 Eficiencia de préstamos", "beneficio", [0] + [20000] * ANIOS)]


def flujos_csv(opciones):
    """opciones: [(nombre, [(concepto, tipo, flujos)])] → CSV de inversion.py (opcion,concepto,tipo,0…n)."""
    filas = ["opcion,concepto,tipo," + ",".join(str(t) for t in range(ANIOS + 1))]
    for op, conceptos in opciones:
        for c, tipo, fl in conceptos:
            fl = fl + [0] * (ANIOS + 1 - len(fl))
            filas.append(f"{op},{c},{tipo}," + ",".join(str(x) if x else "" for x in fl))
    return "\n".join(filas) + "\n"


def inversion(repo, rel, base=None):
    """Corre inversion.py (texto en la evidencia) y devuelve su --json para las tablas y los gráficos."""
    b = f' --base "{base}"' if base else ""
    cmd = f'python3 {INV} {G}/{rel} --tasa {TASA} --variacion {VARIACION}{b}'
    run(cmd, repo)
    r = subprocess.run(cmd + " --json", shell=True, cwd=repo, capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["opciones"]


def margen_b01(op):
    """Cuánto puede caer B-01 (el beneficio que sostiene el caso) antes de que el VAN llegue a 0, en %."""
    s = next(x for x in op["sensibilidad"] if x["concepto"].startswith("B-01"))
    return 100 * (1 - s["equilibrio"])


ROAD = lambda titulo, r2: f"""```mermaid
gantt
    title {titulo}
    dateFormat YYYY-MM-DD
    axisFormat %b
    todayMarker off
    section Gobierno
    SU puesta en marcha        :done, su, 2026-10-19, 2026-10-30
    IP iniciación              :done, ip, 2026-10-30, 2026-11-27
    autorizar-proyecto y etapa :milestone, m1, 2026-11-27, 0d
    section Etapa 2 · Release 1
    Sprints 1 a 6 (47 pts)     :r1, 2026-11-30, 2027-03-05
    Release 1                  :milestone, m2, 2027-03-05, 0d
    section Etapa 3 · Release 2
{r2}
```
"""
R2_BASE = """    Sprints 7 a 9 (21 pts)     :r2, 2027-03-08, 2027-04-16
    UAT y capacitación         :u, 2027-04-21, 2027-05-05
    Puesta en producción       :milestone, m3, 2027-05-05, 0d"""
R2_C001 = """    Sprints 7 a 9 (21 pts)     :r2, 2027-03-08, 2027-04-16
    Sprint 10 simulador (C-001) :crit, s10, 2027-04-21, 2027-05-05
    UAT y capacitación         :u, 2027-05-06, 2027-05-20
    Puesta en producción       :milestone, m3, 2027-05-20, 0d"""

# Documentos que redactan las skills dueñas a partir de sus plantillas (versión abreviada para el recorrido; las cifras
# salen de la WBS, del cronograma y de los registros de esta misma corrida).
FM = lambda tipo, fecha: f'---\ntipo: {tipo}\nproyecto: "Portal de autoservicio para socios"\nversion: "0.1"\nfecha: "{fecha}"\nautor: "Martín Suárez"\nestado: borrador\naprobado_por: ""\nidioma: "es"\n---\n\n'
DPP = FM("descripcion-producto-proyecto", "2026-11-13") + """# Descripción del producto del proyecto

**Nivel de plan:** plan de proyecto

## 1. Propósito
Que el socio resuelva por sí mismo consultas, constancias y solicitudes simples desde el celular, y que el operador las
atienda desde una bandeja única (UJ-1, UJ-2, UJ-3).

## 2. Productos mayores
| Código PBS | Producto | Tipo | Etapa prevista |
|---|---|---|---|
| 2 | Especificación del producto (PRD, UX, arquitectura en BMAD) | intermedio | 1 Iniciación |
| 3 | Portal del socio (acceso, consulta, solicitudes) | final | 2 Release 1 y 3 Release 2 |
| 4 | Consola de operador | final | 2 Release 1 |
| 5 | Transición (UAT, prueba de carga, capacitación, puesta en producción) | final | 3 Release 2 |

## 3. Derivación
PRD de BMAD (línea base 1.0), business case B-01 a B-03, núcleo operativo existente (NFR-6).

## 4. Expectativas de calidad del usuario
Seguro y simple para socios con poca comodidad digital: NFR-1 (Ley 18.331), NFR-3 (p95 < 3 s), NFR-4 (WCAG 2.1 AA).

## 5. Criterios de aceptación priorizados
| ID | Criterio | Medida | Prioridad | Método | Responsable |
|---|---|---|---|---|---|
| CA-01 | El socio entra con segundo factor y recupera el acceso solo | FR-1, FR-2 | must | demostración en UAT | Sofía Ramírez |
| CA-02 | Consultas de saldos y préstamos rápidas | p95 < 3 s (NFR-3) | must | prueba de carga | Sofía Ramírez |
| CA-03 | Disponibilidad del portal | ≥ 99,5 % mensual (NFR-2) | must | análisis del primer mes | Diego Ferreira |
| CA-04 | Accesible | WCAG 2.1 AA (NFR-4) | should | inspección con lista WCAG | Sofía Ramírez |

## 6. Tolerancias de calidad a nivel proyecto
p95 de 3 s sin tolerancia en consultas; WCAG: hasta 3 observaciones menores abiertas al aceptar.

## 7. Métodos y responsabilidades de aceptación
UAT por release; la usuaria sénior (Sofía Ramírez) acepta, la ejecutiva confirma, el proveedor sénior acuerda.

## 8. Versión ágil
Producto mínimo viable = Release 1 (acceso seguro, consulta, consola).
"""
DP31 = FM("descripcion-producto", "2026-11-13") + """# Descripción de producto · 3.1 Acceso seguro

**Identificador:** 3.1 · **Nombre:** Acceso seguro del socio · **Etapa:** 2 Release 1

## 1. Propósito
Que solo el socio titular entre al portal y pueda recuperar el acceso sin ir a la sucursal.

## 2. Composición
Alta con segundo factor (FR-1), recuperación de acceso (FR-2), roles y permisos (FR-11), expiración de sesión.

## 4. Derivado de
PRD de BMAD (línea base 1.0): FR-1, FR-2, FR-11, NFR-1, NFR-5.

## 5. Especificaciones de calidad
| ID | Especificación | Tipo | Medida | Tolerancia de calidad |
|---|---|---|---|---|
| EC-01 | Alta con segundo factor | funcional | 100 % de los criterios de aceptación de la historia 1-1 | ninguna |
| EC-02 | Recuperación de acceso sin intervención del operador | funcional | 100 % de los criterios de la historia 1-2 | ninguna |
| EC-03 | Sesión expira por inactividad (NFR-1) | no funcional | ≤ 10 min | ± 0 |
| EC-04 | Auditoría de accesos (NFR-5) | no funcional | 100 % de altas, ingresos y recuperaciones registrados | ninguna |
| EC-05 | Sin vulnerabilidades altas | no funcional | 0 hallazgos altos o críticos en la prueba de penetración | ninguna |

## 7. Métodos de calidad
| Método | Qué verifica | Habilidades | Momento |
|---|---|---|---|
| prueba automatizada | EC-01 a EC-04 | QA del proveedor | cada sprint (DoD) |
| prueba de penetración | EC-05 | especialista externo | antes de aceptar Release 1 |
| revisión de calidad | criterios de las historias 1-1 y 1-2 | usuaria sénior + aseguramiento | review del sprint 3 |

## 8. Responsabilidades
**Productor:** equipo del proveedor (Lucía Benítez) · **Revisor:** QA del proveedor, con Andrea Costa (aseguramiento) ·
**Autoridad de aceptación:** Sofía Ramírez (usuaria sénior)

## 10. Versión ágil
Historias 1-1 y 1-2 del backlog; sus criterios de aceptación refinan EC-01 y EC-02.
"""
TOLAUT = FM("tolerancias-y-autoridad", "2026-11-27") + """# Tolerancias y autoridad delegada

**Nivel:** proyecto (y etapa 2) · **Fija:** junta (Laura Méndez, ejecutiva) · **Propone:** Martín Suárez

## 1. Tolerancias por objetivo
| Objetivo | Meta | Tolerancia | Prioridad | Dónde vive |
|---|---|---|---|---|
| Tiempo | puesta en producción 2027-05-05 | ± 3 semanas (proyecto) · ± 10 % (etapa) | 2 | plan de proyecto / etapa |
| Costo | BAC 124.000 | ± 8 % (proyecto) · ± 10 % (etapa) | 1 | plan de proyecto / etapa |
| Alcance | Must del release plan | Must sin tolerancia; Should/Could los intercambia el PO | 3 | backlog / release plan |
| Calidad | criterios CA y EC | ver descripciones de producto | — | descripciones de producto |
| Beneficios | B-01 a B-03 | −10 % sobre cada meta | 4 | business case |
| Riesgo | sin riesgos altos sin respuesta | ninguno | — | enfoque de riesgo |
| Sostenibilidad | n/a | n/a (proyecto sin componente físico relevante) | — | — |

## 2. Autoridad delegada
| Elemento | Valor | Límite | Quién la ejerce | Decidido por |
|---|---|---|---|---|
| Autoridad de cambio | Sofía Ramírez | hasta 10.000 por cambio y dentro del saldo del presupuesto de cambio | Sofía Ramírez | junta |
| Presupuesto de cambio | 12.000 (≈ 10 % del BAC) | por encima: excepción a la junta | autoridad de cambio | junta |
| Presupuesto de riesgo | no se fija en esta guía (ver E2E-1) | — | gestor | junta |
| Concesiones | Sofía Ramírez | sin tocar Must ni NFR-1 | usuaria sénior | junta |

## 3. Reporte y escalado
Highlight quincenal a la junta; checkpoint semanal del equipo. Verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo =
excepción. Cadena: paquete → gestor (issue) → junta (informe de excepción) → capa de negocio.

## 4. Decisión
Confirmado por: Laura Méndez (ejecutiva), 2026-11-27 → `estado.py tolerancia`, `estado.py presupuesto` y fila en decisiones.csv.
"""
ENFBEN = FM("enfoque-beneficios", "2026-11-27") + """# Enfoque de gestión de beneficios

**Gestionado por:** proyecto hasta el cierre; después, el negocio (Sofía Ramírez, usuaria sénior).

## 2. Beneficios: medición y responsabilidad
| Id | Beneficio | Dueño | Medida | Línea base | Meta | Fecha prevista | Método | Frecuencia | Tolerancia | Refs |
|---|---|---|---|---|---|---|---|---|---|---|
| B-01 | Desvío de consultas | Sofía Ramírez | consultas de saldo y constancias por canales tradicionales | promedio 2026 [por confirmar] | −30 % | 12 meses tras la puesta en producción | informe del centro de contacto | trimestral | −10 % | SM-2 |
| B-02 | Adopción | Sofía Ramírez | socios activos registrados | 0 | 30 % a 6 meses · 50 % a 12 | 2027-11 / 2028-05 | reporte del portal | mensual | −10 % | SM-1 |
| B-03 | Eficiencia de préstamos | Sofía Ramírez | solicitudes simples respondidas en < 48 h hábiles | [por confirmar] | > 90 % | 6 meses tras la puesta en producción | consola de operador | mensual | −10 % | SM-3 |

## 4. Revisiones de beneficios
En cada fin de etapa (previsión), al cierre (realizados) y post-proyecto a los 6 y 12 meses (encargadas por el negocio a la usuaria sénior).
"""
INFEXC = FM("informe-excepcion", "2027-02-19") + """# Informe de excepción · X-001

**Etapa:** 2 Release 1 · **Emitido:** 2027-02-19 · **Aviso temprano:** 2027-02-19 a Laura Méndez (mensaje breve)
**Emitido por:** Martín Suárez · **Para:** junta del proyecto · **Issues de origen:** I-002 (C-002), I-003
**Nivel de tolerancia afectado:** etapa (presupuesto de cambio y alcance de la etapa 2)

## 1. Descripción
Dos señales el mismo día: (a) C-002, requisito regulatorio obligatorio de 15.000, supera el límite delegado de la
autoridad de cambio (10.000) y el saldo del presupuesto de cambio (llevaría el consumo a 24.000 de 12.000): su
aprobación no se pudo registrar y C-002 queda pendiente de la decisión de la junta; (b) el corte de EVM del 19/2
pronostica que no entra ≈ 22 % del alcance, más que el 20 % de Should/Could: los Must peligran.

## 2. Causa
Revisión normativa de NFR-1 (supuesto del PRD): el regulador exige consentimiento informado y consulta del registro de
accesos por el socio. Sumado al CPI de 0,78 de la etapa.

## 3. Desviación pronosticada
| Objetivo | Plan vigente | Tolerancia | Pronóstico | Fuente |
|---|---|---|---|---|
| Costo (presupuesto de cambio) | 12.000 | autoridad de cambio ≤ 10.000 por cambio | 24.000 si se aprueba C-002 | cambios.csv, registro.py (control de cambios), sanidad CAM-03 |
| Alcance | todos los Must | Must sin tolerancia | ≈ 22 % del alcance no entra (> 20 % Should/Could) | evm-2027-02-19.json, sanidad TOL-01 |
| Tiempo | fin de etapa 2027-03-05 | ± 10 % | +2 semanas si C-002 entra como Must en R1 | escenario del gestor |

## 4. Impacto en el business case
{BC}

## 5. Opciones
| Opción | Descripción | ¿Plan de excepción? | Decide |
|---|---|---|---|
| 1 | Rechazar C-002 | no | junta (inviable: es obligatorio) |
| 2 | Postergar C-002 a Release 2 | no | junta (riesgo regulatorio) |
| 3 | Incorporar C-002 como Must en R1, ampliar el presupuesto de cambio y retirar Could | sí | junta |

## 6. Recomendación
Opción 3, con plan de excepción para la etapa 2.

## 8. Decisión de la junta
(la completa pm-director al registrar la decisión)
"""
PLANEXC = FM("plan-excepcion", "2027-02-24") + """# Plan de excepción · X-001

**Plan que reemplaza:** plan-etapa-2 (Release 1) · **Informe de excepción:** X-001 · **Decisión de la junta:** pide plan de excepción (2027-02-22)
**Opción elegida:** 3 · incorporar C-002 como Must en R1, ampliar el presupuesto de cambio y retirar Could

## 3. Qué cambia respecto del plan vigente
| Elemento | Plan vigente | Plan de excepción | Motivo |
|---|---|---|---|
| Productos | 3.1, 3.2, 4.1 | + 3.5 Consentimiento y registro de accesos (C-002, Must) | requisito regulatorio |
| Fechas | fin de etapa 2027-03-05 | 2027-03-19 (+1 sprint) | C-002 |
| Presupuesto de cambio | 12.000 | 32.000 (12.000 + 15.000 de C-002 + 5.000 de reposición) | decisión de la junta |
| Alcance | 2-3 contacto (Could) en R1 | 2-3 sale de R1 | liberar capacidad para C-002 |
| Tolerancias | ± 10 % tiempo y costo | sin cambio | — |
| Business case | {BC0} | {BC1} | C-002 no suma beneficio propio: es condición para salir a producción |

## 9. Monitoreo
Corte de EVM guardado cada sprint (evm.py --guardar) y sanidad con --corte en cada highlight.

## 10. Solicitud a la junta
Puerta autorizar-plan-excepcion · decide: Laura Méndez (ejecutiva).
"""

P("Paso 1 · Proyecto, especificación y enunciado de alcance")
base_su(repo, "2026-10-20")
run(E(f'especificacion.py --proyecto {G} resumen'), repo)
run(E(f'especificacion.py --proyecto {G} listar epicas'), repo)
art(repo, "enunciado-alcance", "01-inicio/enunciado-alcance.md")
art(repo, "plan-gestion-alcance-requisitos", "02-planificacion/enfoques/plan-gestion-alcance-requisitos.md")

P("Paso 2 · Estructura de productos (PBS), descripciones de producto con criterios de calidad y WBS trazada a requisitos e historias")
escribir(repo, "02-planificacion/wbs.csv", WBS)
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/visuales/wbs.md --diccionario {G}/02-planificacion/diccionario-wbs.md'), repo)
run(f'python3 {BMAD} --proyecto {G} trazabilidad --wbs 02-planificacion/wbs.csv', repo)
run(E(f'especificacion.py --proyecto {G} listar requisitos --cobertura sin-cobertura'), repo)
art(repo, "descripcion-producto-proyecto", "02-planificacion/descripcion-producto-proyecto.md", texto=DPP)
art(repo, "descripcion-producto-3.1", "02-planificacion/productos/3.1-acceso-seguro.md", texto=DP31)
cob0 = cobertura(repo, con_backlog=False)
run(E(f'sanidad.py --proyecto {G} --rapido --corte 2026-11-13'), repo, ok=(0, 1, 2))

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
# actividades.csv con los tres valores que valida Lucía (la duración la deriva cpm.py: tE redondeada hacia arriba)
ACAB = "id,nombre,duracion,predecesoras,recurso,wbs,optimista,mas_probable,pesimista"
afila = lambda i, n, o, m, p, pre, rec, w: f"{i},{n},,{pre},{rec},{w},{o},{m},{p}"
escribir(repo, "02-planificacion/actividades.csv", "\n".join([ACAB] + [afila(*x) for x in acts]) + "\n")
CPM0 = f'cpm.py {G}/02-planificacion/actividades.csv --inicio 2026-11-30'
cp = run(E(f'{CPM0} --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/cronograma.md --mspdi {G}/02-planificacion/cronograma.xml --wbs {G}/02-planificacion/wbs.csv --estimacion {G}/02-planificacion/estimacion-pert.csv'), repo)
T0, DUR0, FIN0, CAM0 = cpm_tabla(cp)
EST0 = json.loads(subprocess.run(E(f'{CPM0} --json'), shell=True, cwd=repo, capture_output=True, text=True, check=True).stdout)["estimacion"]
SIG0, RES0, FINR0 = EST0["sigma_camino"], EST0["reserva"], EST0["fin_con_reserva"]   # σ del camino, reserva a 2σ (beta-PERT por defecto)
LOG.append(("(02-planificacion/estimacion-pert.csv que escribió cpm.py --estimacion; lo lee impacto.py --pert en los pasos 7 y 10)",
            open(os.path.join(repo, G, "02-planificacion", "estimacion-pert.csv"), encoding="utf-8").read().strip()))
# la fórmula la declara el enfoque: la misma red con la triangular (la que cita la Guía PMBOK), solo para comparar
TRI = json.loads(subprocess.run(E(f'{CPM0} --distribucion triangular --json'), shell=True, cwd=repo, capture_output=True, text=True, check=True).stdout)
LOG.append((f"python3 $EST/{CPM0} --distribucion triangular --json   (comparación; la línea base usa beta-PERT)",
            f"duracion_total: {TRI['duracion_total']} · sigma_camino: {num(TRI['estimacion']['sigma_camino'], 2)} · reserva a 2σ: {num(TRI['estimacion']['reserva'], 1)} días · "
            f"fin_con_reserva: {TRI['estimacion']['fin_con_reserva']}"))
V.gantt([t for t in T0.values() if not t["hito"]], png("gantt"),
        titulo=f"Camino crítico: {DUR0} días, fin el {corta(FIN0)}",
        subtitulo=f"Tres valores (beta-PERT) · reserva a 2σ: {num(RES0, 1)} días · fin con reserva {corta(FINR0)}",
        fuente="cpm.py --estimacion sobre actividades.csv (tres valores, beta-PERT) · corrida de referencia de la guía E2E-2")

P("Paso 4 · Priorización del backlog: MoSCoW, valor, esfuerzo en puntos y personas de usuario")
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
# capacidad del release plan (pm-agil-hibrido): velocidad de estado.json.agil × iteraciones; Σ Must + Should ≤ capacidad
run(f'python3 {REL} --proyecto {G} capacidad', repo)
CAP = json.loads(subprocess.run(f'python3 {REL} --proyecto {G} capacidad --json', shell=True, cwd=repo, capture_output=True, text=True, check=True).stdout)


def capacidad_png(cap, ruta):
    """Barras apiladas Must/Should/Could por release contra la capacidad (velocidad × iteraciones) de release.py --json."""
    if not V.OK: return None
    rs = cap["releases"]; fig = V._fig(f"El {rs[0]['release']} entra con {num(rs[0]['holgura'])} punto{'' if rs[0]['holgura'] == 1 else 's'} de holgura y {rs[0]['pct_must']:.0f} % de Must",
                                       f"Puntos por MoSCoW contra la capacidad = velocidad {num(cap['velocidad'])} × iteraciones · regla Must + Should ≤ capacidad")
    ax = fig.add_axes([0.13, 0.14, 0.52, 0.64]); V._ejes(ax, grilla_x=True, grilla_y=False)
    ys = list(range(len(rs)))[::-1]; mx = max(max(r["capacidad"], r["total"]) for r in rs)
    for y, r in zip(ys, rs):
        x0 = 0
        for k, (clave, nombre) in enumerate((("must", "Must"), ("should", "Should"), ("could", "Could"))):
            if r[clave]:
                ax.barh(y, r[clave], left=x0, height=0.5, color=V.SERIE[k], label=nombre if y == ys[0] or not any(rr[clave] for rr in rs[:rs.index(r)]) else None)
                ax.text(x0 + r[clave] / 2, y, num(r[clave]), va="center", ha="center", fontsize=12, color="white", fontweight="bold")
            x0 += r[clave]
        ax.plot([r["capacidad"]] * 2, [y - 0.36, y + 0.36], color=V.TINTA, linewidth=2)
        ax.text(mx * 1.08, y, f"{num(r['comprometido'])} de {num(r['capacidad'])} (M+S) · holgura {num(r['holgura'])}\nMust {r['pct_must']:.0f} % de la capacidad"
                + (" · ▲ vigilar" if r["vigilar_must"] else " · ✔ en rango"), va="center", fontsize=12, color=V.TINTA, linespacing=1.5)
    ax.set_yticks(ys); ax.set_yticklabels([f"{r['release']} · {r['n_iteraciones']} sprints" for r in rs], fontsize=13, color=V.TINTA)
    ax.set_xlim(0, mx * 1.04); ax.xaxis.set_major_locator(V.matplotlib.ticker.MaxNLocator(integer=True))
    h, l = ax.get_legend_handles_labels(); orden_l = [l.index(x) for x in ("Must", "Should", "Could") if x in l]
    fig.legend([h[i] for i in orden_l], [l[i] for i in orden_l], loc="lower left", bbox_to_anchor=(0.13, 0.79), frameon=False, fontsize=12, ncol=3)
    fig.text(0.96, 0.07, "Línea negra = capacidad del release · regla práctica: Must ≤ 60 %", fontsize=10.5, color=V.MUDA, ha="right")
    return V._guardar(fig, ruta, "release.py capacidad --json (backlog.csv y estado.json.agil)")


capacidad_png(CAP, png("capacidad-release"))
# Personas de usuario (pm-interesados): ¿cada Must sirve a alguien? Se proponen desde los recorridos UJ-n de BMAD (solo
# lectura) y la usuaria sénior confirma cada una; el nombre lleva el rol para no confundirla con una persona del equipo.
# Los dolores salen de la sección «Usuarios» del PRD.
run(f'python3 {IN} --proyecto {G} personas candidatos --desde bmad', repo)
cand = {c["origen"][0]: c for c in json.loads(subprocess.run(f'python3 {IN} --proyecto {G} personas candidatos --desde bmad --json', shell=True, cwd=repo,
                                                             capture_output=True, text=True, check=True).stdout)}
PU = {}
for uj, nombre, dolor in (("UJ-1", "Marta (socia que consulta)", "ir a la sucursal o esperar un horario para conseguir una constancia"),
                          ("UJ-2", "Diego (socio que pide un préstamo)", "no saber en qué estado está su préstamo"),
                          ("UJ-3", "Lucía (operadora de back-office)", "transcribir pedidos que llegan por varios canales")):
    c = cand[uj]
    PU[uj] = reg(repo, "personas", nombre=nombre, descripcion=c["descripcion"], objetivo=c["objetivo"], dolores=dolor, contexto_uso=c["contexto_uso"],
                 fuente="bmad-uj", evidencia=c["evidencia"], usa=c["usa"], notas="confirmada por Sofía Ramírez (usuaria sénior) el 2026-11-20")
pz = run(f'python3 {IN} --proyecto {G} personas priorizacion', repo)
# Must sin persona (STK-13): la usuaria sénior relee UJ-2 («autenticado, con contacto verificado» y «recibe … un correo de
# confirmación») y vincula FR-8 y FR-12 a Diego, en lugar de bajarles la prioridad.
if "Must sin persona: FR-8, FR-12" in pz:
    act(repo, "personas", PU["UJ-2"], usa="FR-6;FR-7;FR-8;FR-12", notas="confirmada por Sofía Ramírez (usuaria sénior) el 2026-11-20 · UJ-2: entra con contacto verificado (FR-8) y recibe la confirmación por correo (FR-12)")
    run(f'python3 {IN} --proyecto {G} personas priorizacion', repo)
art(repo, "backlog", "02-planificacion/backlog.csv"); art(repo, "release-plan", "02-planificacion/release-plan.md")

P("Paso 5 · Presupuesto desde la WBS, tolerancias y autoridad de cambio, línea base de alcance y puertas")
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --json --profundidad 1'), repo, corte=40)
for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
    art(repo, c, r)
puerta(repo, "autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")
BAC0 = sum(float(f["costo"] or 0) for f in csv.DictReader(io.StringIO(WBS)))
escribir(repo, "00-direccion/flujos-business-case.csv", flujos_csv([("Línea base", conceptos_base(BAC0))]))
INV0 = inversion(repo, "00-direccion/flujos-business-case.csv")["Línea base"]
art(repo, "business-case", "00-direccion/business-case.md", texto=f"# Business case\n\nB-01 desvío de consultas (SM-2); B-02 adopción (SM-1); B-03 eficiencia de préstamos (SM-3).\n\n"
    f"Evaluación de la inversión (flujos-business-case.csv, tasa {100 * TASA:.0f} % anual, {ANIOS} años): VAN {num(INV0['van'])} · TIR {num(100 * INV0['tir'], 1)} % · "
    f"repago {num(INV0['repago'], 2)} años. B-01 sostiene el caso: puede caer {num(margen_b01(INV0), 1)} % antes de que el VAN llegue a 0.\n")
art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia; Should/Could los intercambia el PO" "riesgo=ningún riesgo alto sin respuesta"'), repo)
art(repo, "tolerancias-y-autoridad", "00-direccion/tolerancias-y-autoridad.md", texto=TOLAUT)
run(E(f'estado.py --proyecto {G} presupuesto cambio=12000 limite_autoridad_cambio=10000 --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27'), repo)
art(repo, "enfoque-beneficios", "00-direccion/enfoque-beneficios.md", texto=ENFBEN)
puerta(repo, "autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.0 --por "Ejecutivo: Laura Méndez"', repo)
run(E(f'estado.py --proyecto {G} aprobar backlog --por "Product owner: Sofía Ramírez" --nivel product-owner --version 1.0 --fecha 2026-11-27'), repo)
art(repo, "roadmap", "02-planificacion/visuales/roadmap.md", texto="# Roadmap por etapas con puertas\n\n" + ROAD("Roadmap · línea base (antes de C-001)", R2_BASE))
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

P("Paso 7 · Cambio de alcance: nueva funcionalidad → análisis de impacto (impacto.py) → decisión contra el presupuesto de cambio")
prd = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(repo, "_bmad-output")) for f in fs if f == "prd.md"][0]
t = open(prd, encoding="utf-8").read().replace("#### FR-11: Roles y permisos", "#### FR-13: Simulador de préstamo\n\nEl socio puede simular cuota y costo total antes de solicitar un préstamo. Realiza UJ-2.\n\n#### FR-11: Roles y permisos", 1)
open(prd, "w", encoding="utf-8").write(t)
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
I1 = reg(repo, "issues", fecha="2027-01-15", tipo="solicitud-cambio", titulo="Agregar FR-13 simulador de préstamo", descripcion="Pedido del Consejo; detectado como desvío del PRD contra la línea base 1.0", prioridad="alta", severidad="mayor", responsable="Martín Suárez")
acts2 = acts[:7] + [("A10", "Sprint simulador de préstamo (FR-13)", 8, 10, 16, "A07", "Proveedor", "3.4")] + [("A08", "UAT prueba de carga y capacitación", 8, 10, 16, "A07;A10", "Usuario sénior", "5.1"), acts[8]]
escribir(repo, "02-planificacion/escenarios/actividades-C-001.csv", "\n".join([ACAB] + [afila(*x) for x in acts2]) + "\n")
cp1 = run(E(f'cpm.py {G}/02-planificacion/escenarios/actividades-C-001.csv --inicio 2026-11-30 --titulo "Escenario con FR-13"'), repo)
T1, DUR1, FIN1, CAM1 = cpm_tabla(cp1)
COSTO1 = 9000; PTS1 = 8; BEN1 = 4000          # monto de C-001 y beneficio anual que estima la usuaria sénior (B-03)
C001 = conceptos_base(BAC0) + [("C-001 Simulador de préstamo", "inversion", [-COSTO1]), ("B-03 Simulador (C-001)", "beneficio", [0] + [BEN1] * ANIOS)]
escribir(repo, "02-planificacion/escenarios/flujos-C-001.csv", flujos_csv([("Línea base", conceptos_base(BAC0)), ("Con C-001", C001)]))
INV1 = inversion(repo, "02-planificacion/escenarios/flujos-C-001.csv")["Con C-001"]
C1 = reg(repo, "cambios", fecha="2027-01-16", solicitante="Consejo directivo (vía Laura Méndez)", titulo="FR-13 simulador de préstamo", descripcion=f"Origen {I1}", justificacion="mejora la conversión de solicitudes (SM-3)", costo="9000", cargo="presupuesto-cambio")
# FR-13 realiza UJ-2: la usuaria sénior confirma que lo usa la persona de ese recorrido (personas afectadas por el cambio)
act(repo, "personas", PU["UJ-2"], usa="FR-6;FR-7;FR-8;FR-12;FR-13")
run(f'python3 {IN} --proyecto {G} personas mapa', repo)
IM1 = impacto(repo, C1, '--actividades 02-planificacion/escenarios/actividades-C-001.csv --inicio 2026-11-30 --pert 02-planificacion/estimacion-pert.csv '
              '--flujos 02-planificacion/escenarios/flujos-C-001.csv --opcion "Con C-001" --tasa 0.10 --refs FR-13 --paquetes 3.4 --puntos 8 --release R2', "2027-01-16")
d1 = DUR1 - DUR0; REM1 = RES0 - d1
# el gestor deja el análisis en cambios.csv y la autoridad de cambio decide (IM1["nivel"] == "autoridad-cambio")
act(repo, "cambios", C1, impacto_alcance="nuevo paquete WBS 3.4 · historia 2-4 · 8 pts en R2", impacto_tiempo=f"+{d1} días laborables en el camino crítico (fin {FIN0} → {FIN1}), dentro de la tolerancia de ±3 semanas",
    impacto_costo=f"+USD {num(COSTO1)}", impacto_riesgo=f"la reserva de cronograma a 2σ baja de {num(RES0, 1)} a {num(REM1, 1)} días laborables (riesgo nuevo)",
    impacto_beneficios=f"refuerza B-03 (SM-3): +{num(BEN1)} por año; VAN del business case {num(INV0['van'])} → {num(INV1['van'])}",
    recomendacion=f"{IM1['recomendacion']}: presupuesto de cambio ({num(COSTO1)} de 12.000, dentro del límite de 10.000 de la autoridad de cambio); FR-13 como Should en R2", estado="pendiente-decision")
act(repo, "cambios", C1, decision="aprobado", decidido_por="Autoridad de cambio: Sofía Ramírez", fecha_decision="2027-01-18", estado="aprobado")
act(repo, "issues", I1, estado="pendiente-cambio", decision=f"tramitado como {C1}", decidido_por="Autoridad de cambio: Sofía Ramírez")
R1 = reg(repo, "riesgos", fecha_identificacion="2027-01-18", autor="Martín Suárez", categoria="gestion", causa=f"{C1} suma {d1} días laborables al camino crítico y deja la reserva de cronograma a 2σ en ≈{num(REM1)} días", evento=f"un atraso adicional de más de {num(REM1)} días laborables en el camino crítico", efecto=f"la puesta en producción pasa del {FIN1} y consume la tolerancia de tiempo del proyecto (±3 semanas)", tipo="amenaza", probabilidad="3", impacto="3", proximidad="mediano-plazo", disparador="SPI de un sprint < 0,90 o atraso acumulado ≥ 2 días en el camino crítico", respuesta="reducir", acciones="vigilar SPI por sprint con evm.py --guardar; preparar con el PO qué Should/Could salen si se dispara", propietario="Martín Suárez", ejecutor="Lucía Benítez", fecha_revision="2027-02-19", notas=f"surge de {C1}")
escribir(repo, "02-planificacion/wbs.csv", WBS.replace("4,Consola de operador", "3.4,Simulador de préstamo (C-001),paquete,Lucía Benítez,180,9000,FR-13\n4,Consola de operador"))
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/visuales/wbs.md --profundidad 1'), repo)
run(f'python3 {BMAD} --proyecto {G} handoff --cambio {C1}', repo)
s18 = run(E(f'sanidad.py --proyecto {G} --rapido --corte 2027-01-18'), repo, ok=(0, 1, 2))
hitos = ["A09", "A08", "A07", "A06"]; corto = {"A06": "Release 1 aceptada", "A07": "Fin de solicitudes", "A08": "Fin de UAT", "A09": "Puesta en producción"}
V.barras_comparadas([f"{h} {corto[h]}" for h in hitos], [[T0[h]["fin"] for h in hitos], [T1[h]["fin"] for h in hitos]], png("roadmap-c001"),
                    titulo=f"{C1} no mueve el Release 1 y corre {d1} días la puesta en producción",
                    subtitulo=f"Fin de cada hito en días laborables desde el 30/11/2026 · {corta(FIN0)} → {corta(FIN1)}, dentro de la tolerancia de ±3 semanas ({TOL_DIAS} días)",
                    fuente=f"cpm.py: actividades.csv (línea base) y escenarios/actividades-{C1}.csv", unidad=" días", nombres=["Línea base", f"Con {C1}"])

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
cob1 = cobertura(repo, con_backlog=True)
V.estados([(e, 100 * a / n, "bien" if a == n else "atencion", f"{a} de {n} · " + ("✔ completo" if a == n else f"▲ {n - a} " + ("solo a nivel de épica" if "épica" in d else "sin cubrir"))) for e, a, n, d in cob1], png("trazabilidad"),
          titulo=f"Tras {C1}: {cob1[0][1]} de {cob1[0][2]} requisitos con historia y paquete",
          subtitulo="Cobertura recalculada en cada sincronización con BMAD (no una matriz que se arma una vez) · corte 2027-01-25",
          fuente="bmad.py trazabilidad → matriz-trazabilidad-bmad.csv · backlog.csv · descripciones de producto", maximo=100, decimales=0, sufijo=" %")
art(repo, "roadmap", "02-planificacion/visuales/roadmap.md", texto="# Roadmap por etapas con puertas\n\n" + ROAD("Roadmap · línea base (antes de C-001)", R2_BASE) + "\n" + ROAD(f"Roadmap · con {C1} (simulador de préstamo)", R2_C001))
run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.1 --por "Ejecutivo: Laura Méndez"', repo)
run(f'python3 {BMAD} --proyecto {G} linea-base epicas --version 1.1 --por "Ejecutivo: Laura Méndez"', repo)
act(repo, "cambios", C1, estado="implementado"); act(repo, "issues", I1, estado="cerrado", fecha_cierre="2027-01-25")
run(f'python3 {BMAD} --proyecto {G} verificar', repo, ok=(0, 1, 2))
run(E(f'sanidad.py --proyecto {G} --rapido --corte 2027-01-25'), repo, ok=(0, 1, 2))

P("Paso 9 · Avance del alcance: EVM ágil (alcance no entregable) e informe")
ss_t = open(ss, encoding="utf-8").read()
for k in ["1-1-alta-y-acceso-del-socio-con-segundo-factor", "1-2-recuperación-de-acceso", "1-3-consulta-de-saldos-de-ahorro-y-préstamos", "3-1-acceso-y-roles-de-la-consola-de-operador"]:
    ss_t = re.sub(rf"(?m)^(\s*{re.escape(k)}:)\s*\S+", r"\1 done", ss_t)
open(ss, "w", encoding="utf-8").write(ss_t)
run(f'python3 {BMAD} --proyecto {G} avance', repo)
run(f'python3 {BMAD} --proyecto {G} backlog', repo)
reg(repo, "calidad", producto="Release 1 parcial · historias 1-1, 1-2, 1-3 y 3-1 (productos 3.1, 3.2 y 4.1)", metodo_verificacion="revision", criterios="EC-01 a EC-04 de la descripción de producto 3.1 y criterios de aceptación de cada historia", responsable_productor="Lucía Benítez", revisores="QA del proveedor; Andrea Costa (aseguramiento)", aprobador="Sofía Ramírez", fecha_prevista="2027-01-28", fecha_real="2027-01-28", resultado="aprobado", estado="completada")
run(E(f'evm.py --pv 60000 --ev 52000 --ac 58000 --bac 133000 --modo agil --pct-no-must 20 --proyecto {G} --guardar --corte 2027-01-29'), repo)
ev29 = json.load(open(os.path.join(repo, G, "03-control/reportes/evm-2027-01-29.json"), encoding="utf-8"))
if ev29["SPI"] < 0.90:   # disparador de R-001 (SPI < 0,90): se ejecuta la respuesta registrada
    act(repo, "riesgos", R1, estado="en-seguimiento", notas=f"surge de {C1} · disparador activado el 2027-01-29 (SPI {num(ev29['SPI'], 3)} < 0,90): el PO prepara qué Should/Could salen si el atraso sigue")
run(E(f'sanidad.py --proyecto {G} --rapido --corte 2027-01-29'), repo, ok=(0, 1, 2))
run(E(f'puertas.py --proyecto {G} estado --markdown'), repo)

P("Paso 10 · Excepción: un requisito regulatorio supera la autoridad y el presupuesto de cambio, y el EVM pronostica salir de la tolerancia")
I2 = reg(repo, "issues", fecha="2027-02-15", autor="Martín Suárez", tipo="solicitud-cambio", titulo="Requisito regulatorio: consentimiento informado y consulta del registro de accesos por el socio", descripcion="Resultado de la revisión normativa supuesta en NFR-1 (Ley 18.331); pedido del Consejo directivo", prioridad="urgente", severidad="mayor", responsable="Martín Suárez")
C2 = reg(repo, "cambios", fecha="2027-02-16", solicitante="Consejo directivo (requisito regulatorio, vía Laura Méndez)", titulo="Consentimiento informado y registro de accesos consultable por el socio", descripcion=f"Origen {I2}; refuerza NFR-1 y NFR-5", justificacion="obligatorio por regulación", impacto_alcance="nuevo paquete WBS 3.5 · 13 pts Must en R1", impacto_tiempo="+1 sprint en la etapa 2 (fin 2027-03-05 → 2027-03-19)", impacto_costo="+USD 15.000", impacto_riesgo="sin él, riesgo regulatorio de no poder salir a producción", impacto_beneficios="condición para salir a producción y para B-02 (adopción); sin beneficio propio", recomendacion="aprobar: es obligatorio; Must en R1", costo="15000", cargo="presupuesto-cambio")
# Sofía (autoridad de cambio) lo aprobó el 17/2 "porque es obligatorio": registro.py no deja registrarlo como aprobado
# (supera su límite por cambio y el saldo del presupuesto de cambio). Queda pendiente-decision y se escala a la junta.
RECH = run(E(f'registro.py --proyecto {G} actualizar cambios {C2} --campo "decision=aprobado" --campo "estado=aprobado" --campo "decidido_por=Autoridad de cambio: Sofía Ramírez" --campo "fecha_decision=2027-02-17"'), repo, ok=(1,))
act(repo, "cambios", C2, estado="pendiente-decision", notas="la autoridad de cambio quiso aprobarlo el 2027-02-17; supera su límite de 10.000 y el saldo del presupuesto de cambio (registro.py lo rechazó): decide la junta")
run(E(f'evm.py --pv 75000 --ev 60000 --ac 77000 --bac 133000 --modo agil --pct-no-must 20 --proyecto {G} --guardar --corte 2027-02-19'), repo)
s19 = run(E(f'sanidad.py --proyecto {G} --rapido --corte 2027-02-19'), repo, ok=(0, 1, 2))
COSTO2 = 15000
ev19 = json.load(open(os.path.join(repo, G, "03-control/reportes/evm-2027-02-19.json"), encoding="utf-8"))
C002 = C001 + [("C-002 Consentimiento y registro", "inversion", [-COSTO2])]
escribir(repo, "02-planificacion/escenarios/flujos-C-002.csv", flujos_csv([("Línea base", conceptos_base(BAC0)), ("Con C-001", C001), ("Con C-001 y C-002", C002)]))
INV2 = inversion(repo, "02-planificacion/escenarios/flujos-C-002.csv", base="Con C-001")["Con C-001 y C-002"]
# 13 pts Must en R1; sale la 2-3 (Could) para liberar capacidad; el R1 cierra la etapa 2; corte de EVM del 19/2
IM2 = impacto(repo, C2, '--refs NFR-1,NFR-5 --paquetes 3.5 --flujos 02-planificacion/escenarios/flujos-C-002.csv --opcion "Con C-001 y C-002" --base "Con C-001" --tasa 0.10 '
              '--puntos 13 --release R1 --liberar 2-3 --etapa --evm 03-control/reportes/evm-2027-02-19.json', "2027-02-19")
art(repo, "informe-excepcion-X-001", "03-control/reportes/2027-02-19-informe-excepcion-X-001.md",
    texto=INFEXC.replace("{BC}", f"VAN a {ANIOS} años: {num(INV1['van'])} con {C1} → {num(INV2['van'])} con {C2} (inversion.py, escenarios/flujos-C-002.csv). "
                                 f"Sigue positivo; B-01 puede caer {num(margen_b01(INV2), 1)} % antes de que el VAN llegue a 0 (tolerancia de beneficios −{100 * VARIACION:.0f} %)."))
I3 = reg(repo, "issues", fecha="2027-02-19", autor="Martín Suárez", tipo="problema-preocupacion", titulo="Excepción X-001: cambio fuera de la autoridad delegada y pronóstico fuera de tolerancia de alcance", descripcion=f"{C2} supera el límite de la autoridad de cambio y el saldo del presupuesto de cambio (pendiente-decision); EVM del 2027-02-19 con excepcion_prevista", prioridad="urgente", severidad="critica", responsable="Martín Suárez", estado="escalado", notas="informe 03-control/reportes/2027-02-19-informe-excepcion-X-001.md")
act(repo, "issues", I2, estado="escalado", decision=f"{C2} escalado a la junta (excepción X-001)")
run(E(f'estado.py --proyecto {G} puerta decision-ad-hoc --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2027-02-22 --condiciones "X-001: la junta pide plan de excepción para la etapa 2; {C2} queda sujeto a ese plan"'), repo)
run(E(f'estado.py --proyecto {G} limite-etapa --excepcion X-001'), repo)
art(repo, "plan-excepcion-X-001", "02-planificacion/plan-excepcion-X-001.md",
    texto=PLANEXC.replace("{BC0}", f"VAN {num(INV1['van'])}").replace("{BC1}", f"VAN {num(INV2['van'])} (sigue positivo)"))
art(repo, "business-case", "00-direccion/business-case.md", texto=open(os.path.join(repo, G, "00-direccion/business-case.md"), encoding="utf-8").read()
    + f"\n## Actualización con el plan de excepción X-001 (2027-02-24)\nCon {C1} y {C2} (escenarios/flujos-C-002.csv): inversión {num(BAC0 + COSTO1 + COSTO2)} · VAN {num(INV2['van'])} · TIR {num(100 * INV2['tir'], 1)} % · "
    f"repago {num(INV2['repago'], 2)} años. B-01 puede caer {num(margen_b01(INV2), 1)} % antes de que el VAN llegue a 0: el proyecto sigue justificado.\n")
run(E(f'estado.py --proyecto {G} cumplir-condiciones decision-ad-hoc --fecha 2027-02-24 --por "Ejecutiva: Laura Méndez" --nota "plan de excepción X-001 y business case actualizado presentados; {C2} se decide con ellos"'), repo)
run(E(f'puertas.py --proyecto {G} verificar autorizar-plan-excepcion'), repo, ok=(0, 1, 2))
run(E(f'estado.py --proyecto {G} presupuesto cambio=32000 --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26'), repo)
act(repo, "cambios", C2, decision="aprobado", estado="aprobado", decidido_por="Junta: Laura Méndez (ejecutiva) · plan de excepción X-001", fecha_decision="2027-02-26", notas="la autoridad de cambio no podía aprobarlo (límite de 10.000 y saldo del presupuesto de cambio); lo aprueba la junta con el presupuesto de cambio ampliado a 32.000 (plan de excepción X-001)")
run(E(f'puertas.py --proyecto {G} verificar autorizar-plan-excepcion'), repo, ok=(0, 1, 2))
run(E(f'puertas.py --proyecto {G} lista autorizar-plan-excepcion --fecha 2027-02-26'), repo, mostrar=False)
run(E(f'puertas.py --proyecto {G} confirmar autorizar-plan-excepcion --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26'), repo)
run(E(f'estado.py --proyecto {G} puerta autorizar-plan-excepcion --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26 --fin 2027-03-19'), repo)
act(repo, "issues", I3, estado="cerrado", fecha_cierre="2027-02-26", decision="plan de excepción X-001 autorizado", decidido_por="Ejecutiva: Laura Méndez")
act(repo, "issues", I2, estado="pendiente-cambio", decision=f"tramitado como {C2} (aprobado por la junta)", decidido_por="Ejecutiva: Laura Méndez")
escribir(repo, "02-planificacion/wbs.csv", open(os.path.join(repo, G, "02-planificacion/wbs.csv"), encoding="utf-8").read().replace("4,Consola de operador", f"3.5,Consentimiento y registro de accesos ({C2}),paquete,Lucía Benítez,300,15000,NFR-1; NFR-5\n4,Consola de operador", 1))
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid {G}/02-planificacion/visuales/wbs.md --profundidad 1'), repo)
run(f'python3 {BMAD} --proyecto {G} handoff --cambio {C2}', repo)
s26a = run(E(f'sanidad.py --proyecto {G} --rapido --corte 2027-02-26'), repo, ok=(0, 1, 2))
if "REG-09" in s26a:     # revisión vencida de R-001: pm-riesgos la revisa con el propietario y fija la próxima
    act(repo, "riesgos", R1, probabilidad="4", fecha_revision="2027-03-19",
        notas=f"surge de {C1} · disparador activado el 2027-01-29 (SPI {num(ev29['SPI'], 3)}) · revisado el 2027-02-26: SPI {num(ev19['SPI'], 2)} al 19/2 y {C2} suma un sprint a la etapa 2; probabilidad 3 → 4; próxima revisión al fin de la etapa (plan de excepción X-001)")
s26 = run(E(f'sanidad.py --proyecto {G} --rapido --corte 2027-02-26'), repo, ok=(0, 1, 2))
run(E(f'estado.py --proyecto {G} resumen'), repo)
run(E(f'registro.py --proyecto {G} listar cambios'), repo)

# ---------------------------------------------------------------- gráficos del cierre del recorrido (datos de esta corrida)
c18, c19, c26 = cam03(s18), cam03(s19), cam03(s26)
m = re.search(r"= ([\d.]+) de ([\d.]+) fijados por la junta", RECH)       # lo que registro.py calculó al rechazar la aprobación de C-002
p19 = (float(m[1].replace(".", "")), float(m[2].replace(".", "")))
V.consumo([(f"18/1 · tras {C1}", *c18), (f"19/2 · con {C2} (no aprobado)", *p19), ("26/2 · tope ampliado por la junta", *c26)], png("consumo-cambio"),
          titulo=f"Sin saldo para {C2} ({100 * p19[0] / p19[1]:.0f} %): quedó pendiente y decidió la junta",
          subtitulo=f"Consumo contra el presupuesto de cambio (CAM-03); el 19/2, con {C2}, que no se aprobó (real: {100 * c19[0] / c19[1]:.0f} %)",
          fuente="sanidad.py --corte 2027-01-18 y 2027-02-26 (CAM-03) · registro.py (rechazo de la aprobación de C-002) · estado.json presupuestos")
fi = {x["objetivo"]: x for x in IM2["filas"]}                # cifras de la tabla de impacto de C-002 (impacto.py --json)
nu = lambda t: float(t.replace(".", "").replace(",", "."))
lim2 = [("Presupuesto de cambio", *[nu(x) for x in re.search(r"([\d.]+) de ([\d.]+)", fi["Presupuesto de cambio"]["con"]).groups()], ""),
        ("Límite de la autoridad de cambio", nu(re.search(r"([\d.]+) en este cambio", fi["Autoridad"]["con"])[1]), nu(re.search(r"límite ([\d.]+)", fi["Autoridad"]["antes"])[1]), ""),
        ("Tiempo de la etapa 2 (días corridos)", nu(re.search(r"\(\+(\d+)\)", fi["Tiempo de la etapa"]["con"])[1]), nu(re.search(r"= ([\d,]+) días", fi["Tiempo de la etapa"]["contra"])[1]), "+"),
        ("Capacidad del R1 (puntos)", nu(re.search(r"^(\d+) pts", fi["Capacidad del R1"]["con"])[1]), nu(re.search(r"de (\d+)", fi["Capacidad del R1"]["antes"])[1]), ""),
        ("Alcance que no entra (EVM 19/2)", nu(re.search(r"no entra ([\d,]+) %", fi["Alcance (EVM)"]["con"])[1]), nu(re.search(r"= ([\d,]+) %", fi["Alcance (EVM)"]["antes"])[1]), "%")]
V.estados([(e, 100 * u / t, "critico" if u > t else "bien", f"{'✖' if u > t else '✔'} {s if s == '+' else ''}{num(u, 0 if u == int(u) else 1)}{' %' if s == '%' else ''} de "
            f"{'±' if s == '+' else ''}{num(t, 0 if t == int(t) else 1)}{' %' if s == '%' else ''}") for e, u, t, s in sorted(lim2, key=lambda x: -x[1] / x[2])], png("impacto-c002"),
          titulo=f"{C2} supera los cinco límites del análisis: decide la junta",
          subtitulo=f"Cada barra: cuánto del límite usaría {C2} (100 % = el límite) · el business case sigue justificado: VAN {num(INV2['van'])}",
          fuente=f"impacto.py analizar {C2} --fecha 2027-02-19 (tabla de impacto y borrador de la solicitud de cambio)", maximo=200, decimales=0, sufijo=" %")
V.estados([("Margen Should/Could (tolerancia)", ev29["pct_no_must"], "tope", "lo que el PO puede retirar"),
           ("Corte 29/1 · alcance que no entra", ev29["alcance_no_entregable_pct"], "atencion", f"ámbar: los Must no peligran"),
           ("Corte 19/2 · alcance que no entra", ev19["alcance_no_entregable_pct"], "critico", f"rojo: los Must peligran")], png("alcance-evm"),
          titulo=f"El 19/2 no entra el {num(ev19['alcance_no_entregable_pct'], 0)} % del alcance, más que el {ev19['pct_no_must']:.0f} % de margen",
          subtitulo=f"EVM ágil guardado por corte (costo y fecha fijos) · CPI {num(ev29['CPI'], 2)} → {num(ev19['CPI'], 2)} · SPI {num(ev29['SPI'], 2)} → {num(ev19['SPI'], 2)}",
          fuente="evm.py --modo agil --pct-no-must 20 --guardar → evm-2027-01-29.json y evm-2027-02-19.json", maximo=40, decimales=1, sufijo=" %")
V.barras_comparadas(["Línea base", f"Con {C1}", f"Con {C1} y {C2}"], [[INV0["van"], INV1["van"], INV2["van"]]], png("business-case"),
                    titulo=f"Con los dos cambios el business case sigue justificado: VAN {num(INV2['van'])}",
                    subtitulo=f"VAN a {ANIOS} años con tasa {100 * TASA:.0f} % · B-01 puede caer {num(margen_b01(INV0), 0)} %, {num(margen_b01(INV1), 0)} % y "
                              f"{num(margen_b01(INV2), 0)} % antes de que el VAN llegue a 0 (tolerancia: −{100 * VARIACION:.0f} %)",
                    fuente="inversion.py --tasa 0.1 --variacion 0.1 · flujos-business-case.csv, escenarios/flujos-C-001.csv y flujos-C-002.csv",
                    nombres=["VAN"], leyenda=None)
V.tarjetas([(num(INV2["van"]), "VAN del business case", f"inversión {num(BAC0 + COSTO1 + COSTO2)} con {C1} y {C2} · B-01 puede caer {num(margen_b01(INV2), 0)} %", "bien"),
            (corta(FIN1)[:-5], "Puesta en producción", f"línea base {corta(FIN0)[:-5]} · +{d1} días de {TOL_DIAS} de tolerancia", "atencion"),
            (f"{num(REM1, 0)} días", "Reserva de cronograma que queda", f"2σ = {num(RES0, 1)} − {d1} de {C1} · riesgo R-001", "serio"),
            (f"{100 * c26[0] / c26[1]:.0f} %", "Presupuesto de cambio usado", f"{num(c26[0])} de {num(c26[1])} tras la ampliación del 26/2", "bien"),
            (f"{num(ev19['alcance_no_entregable_pct'], 1)} %", "Alcance que no entra (19/2)", "más que el 20 % de Should/Could · excepción X-001", "critico"),
            (f"{cob1[0][1]} de {cob1[0][2]}", "Requisitos funcionales trazados", "con historia y paquete de la WBS tras cada cambio", "bien")], png("indicadores"),
           titulo="Al 26/2 cada cambio quedó medido; la reserva casi se agotó",
           subtitulo="Indicadores de la corrida de referencia de la guía E2E-2", fuente="inversion.py · cpm.py · sanidad CAM-03 · evm.py · bmad.py trazabilidad")

with open(sys.argv[1] if len(sys.argv) > 1 else "salida-g2.md", "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
