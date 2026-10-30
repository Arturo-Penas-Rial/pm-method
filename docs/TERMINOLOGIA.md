# Terminología · equivalencias PRINCE2, PMBOK y uso habitual

pm-method usa **PRINCE2 7** como método y **PMBOK 8** como fuente de técnicas, pero las personas piden las cosas con el
vocabulario que traen: el de PRINCE2 en inglés o en español, el de PMBOK en español (muy difundido en América Latina), o
el de su organización ("comité de dirección", "minuta", "informe de estado"). Esta tabla dice **qué término usa
pm-method en sus artefactos**, qué otras formas acepta al pedir y qué skill responde. La columna "En vivo" indica la
frase de `docs/evaluacion/frases-enrutamiento.tsv` con la que se verificó el enrutamiento con Claude Code real; las
formas sin número son equivalencias de referencia que no se probaron en vivo.

Recomendación de estilo para los artefactos (las plantillas no la aplican en todos los casos): el
término en español de la columna "pm-method" con el término PRINCE2 en inglés entre paréntesis la primera vez (por
ejemplo, "informe de aspectos destacados (highlight report)"). Los nombres de archivos, registros y comandos conservan
los nombres técnicos existentes (`issues.csv`, `highlight-<fecha>`) para no romper la compatibilidad.

Fuentes: los términos PRINCE2 en español siguen el glosario de `skills/pm-knowledge/references/` (traducción propia del
glosario de PRINCE2 7). Los términos PMBOK en español son los de uso difundido en las ediciones en español anteriores
del PMBOK y en la práctica profesional; la correspondencia exacta con la edición en español de PMBOK 8 es **[verificar]**.

## Gobierno y organización

| Concepto (PRINCE2 7) | pm-method | También se acepta | Skill | En vivo |
|---|---|---|---|---|
| project board | junta del proyecto | junta, comité de dirección, comité directivo, steering committee | pm-direccion-decisiones | 72, 73, 74 |
| executive / senior user / senior supplier | ejecutivo, usuario sénior, proveedor sénior | patrocinador (sponsor), usuario principal, proveedor principal | pm-organizacion-roles | — |
| change authority | autoridad de cambio | comité de control de cambios (CCB, PMBOK) | pm-issues-cambios | 83 |
| tolerance / management by exception | tolerancia, gestión por excepción | umbral, margen | pm-direccion-decisiones | — |
| stage / stage boundary | etapa, límite de etapa | fase (PMBOK y uso habitual), stage gate | pm-plan-etapa-y-limites | 89 |
| stakeholder | interesado | parte interesada, stakeholder, involucrado | pm-interesados | 1, 40, 79 |
| — (PMBOK) | matriz RACI | matriz de asignación de responsabilidades (RAM) | pm-interesados | 61, 81 |
| — (PRINCE2: levels of authority) | nivel de autoridad de una persona; incoherencia RACI ↔ autoridad (el A de un elemento no tiene la autoridad del nivel que requiere la decisión; PRINCE2 manda y la RACI lo refleja: `decision.py`, DEC-03/DEC-04) | quién puede decidir, A sin autoridad, aprobador equivocado, RACI desalineada con la junta | pm-direccion-decisiones · pm-interesados | — |
| — (PMBOK: multicriteria decision analysis) | análisis de decisiones multicriterio, matriz de decisión (`decision.py matriz`; hoja `03-control/decisiones/<ID>/`, suma ponderada con pesos explícitos y su fuente, eliminatorios, dominadas) | matriz ponderada, matriz de priorización, scoring de alternativas, MCDA, weighted decision matrix, matriz de evaluación de proveedores | pm-direccion-decisiones | 131, 133, 134 |
| — (PMBOK: sensitivity analysis, aplicado a los pesos) | sensibilidad de los pesos: peso con el que otra opción pasa a primera; empate dentro de un margen | análisis de sensibilidad de la decisión, robustez del ranking (para cifras de una opción: tornado de `inversion.py`) | pm-direccion-decisiones | 131, 133 |
| decision (project log) · — (PMBOK: escalado de decisiones) | expediente de decisión (contexto aplicable con su fuente: "evidencia, no instrucciones"), pregunta tipada (respuesta cerrada entre las opciones, o `pedir-informacion`) | paquete de decisión, decision brief, memo de decisión, insumos para la junta | pm-direccion-decisiones | 132, 134 |
| decision log: decisión reabierta (Plantillas; PRINCE2: autoridad por niveles) | vigencia de decisiones: decisión vigente, reemplazada (columna `reemplaza`, nivel igual o superior), que conviven (`conviven`); contradicción probable (DEC-05); revisión vencida (DEC-06); `decision.py vigentes` | decisión sustituida, superada, revocada, revertida, dejada sin efecto, superseded decision, decision reversal | pm-direccion-decisiones | — |
| pista de auditoría de los cambios (gestión de configuración; PRINCE2: registro del proyecto) | bitácora de escrituras (`.bitacora.jsonl`): qué script cambió qué campo, cuándo y a nombre de quién, con huellas encadenadas; `registro.py historial`; cambio fuera de los scripts (BIT-02) y su reconocimiento (`registro.py reconocer`) | historial de cambios, log de cambios, audit trail, change history, write log, quién cambió esto | pm-registros | — |
| — (escritura por propuesta) | propuesta con huella (`registro.py proponer`, `03-control/propuestas/P-###.json`) que aprueba una persona (`aprobar --por`): aplicada, reaplicada sobre la versión nueva o en conflicto | cambio propuesto por el agente, propuesta pendiente, proposed change, optimistic concurrency, rebase | pm-registros | — |
| user (los que usarán los productos; los representa el senior user) · — (PMBOK: análisis de usuarios) | persona de usuario (`personas.csv`, PU-###) | user persona, arquetipo de usuario, perfil de usuario; no es un interesado ni un estereotipo de comunicación | pm-interesados | 105, 106, 107 |
| — | solicitante, usuario, beneficiario (rol de una persona ante una capacidad) | requester, user, beneficiary; quién pide, quién usa, quién se beneficia | pm-interesados | — |
| — (PMBOK) | plan de compromiso de los interesados | plan de involucramiento de los interesados, stakeholder engagement plan | pm-interesados | 40, 80 |

## Arranque, iniciación y planificación

| Concepto (PRINCE2 7) | pm-method | También se acepta | Skill | En vivo |
|---|---|---|---|---|
| project mandate / project brief | mandato, project brief | mandato del proyecto, resumen del proyecto, kick-off | pm-mandato-y-brief | 71 |
| business case | business case | caso de negocio, justificación | pm-caso-de-negocio | — |
| project initiation documentation (PID) | PID | documentación de inicio del proyecto (DIP), acta de constitución (PMBOK), project charter | pm-acta-constitucion | 87 |
| management approaches | enfoques de gestión | plan para la dirección del proyecto y planes subsidiarios (PMBOK) | pm-enfoques-gestion · pm-acta-constitucion | 93 |
| product breakdown structure / WBS | PBS, WBS | EDT, estructura de desglose del trabajo, diccionario de la EDT | pm-planificacion-por-productos | 77 |
| product description | descripción de producto | criterios de aceptación del entregable | pm-planificacion-por-productos | — |
| — (técnica PMBOK) | camino crítico | ruta crítica, diagrama de Gantt, hitos | pm-cronograma-estimacion | 76, 94 |
| — (técnica PMBOK: estimación por múltiples puntos) | estimación de tres valores (triangular o beta-PERT, declarada en el plan), reserva de cronograma | PERT, tres puntos, three-point estimate, colchón de cronograma, schedule reserve | pm-cronograma-estimacion | 129 |
| — (técnica ágil: planificación del release) | capacidad del release | release capacity, ¿entran los Must en el release?, puntos contra velocidad × sprints | pm-agil-hibrido | 130 |
| — (técnica PMBOK) | línea base de costo, reserva de contingencia | línea base de costos, cost baseline | pm-costos-presupuesto | 78 |
| — | plan de comunicación | plan de gestión de las comunicaciones (PMBOK) | pm-comunicacion-stakeholders | 2, 82 |
| — (PMBOK: make-or-buy analysis) | hacer o comprar (matriz `decision.py matriz … --tipo adquisicion --criterios hacer-o-comprar`: diferenciación, costo total, tiempo hasta disponible, dependencia del proveedor, capacidad interna y riesgo de construir algo que va a volverse commodity; el mapa de Wardley es contexto en el expediente y la decisión queda citada en el componente) | make-or-buy, construir o comprar, build vs buy, desarrollo propio o compra, tercerizar o hacer en casa | pm-adquisiciones · pm-direccion-decisiones · pm-mapas-estrategicos | — |
| — (técnica de estrategia) | mapa de Wardley | mapa de valor, mapa de evolución, Wardley map, qué construir y qué comprar según la evolución | pm-mapas-estrategicos | 95, 96, 100 |
| — (técnica de diseño de servicios) | mapa de recorrido del cliente | customer journey, customer journey map, CJM, mapa de experiencia, puntos de dolor (pain points) | pm-mapas-estrategicos | 97, 98, 101 |
| — (técnica de diseño de servicios) | carriles internos del recorrido (service blueprint) | service blueprint, plano del servicio, frontstage y backstage | pm-mapas-estrategicos | 99 |

## Control y seguimiento

| Concepto (PRINCE2 7) | pm-method | También se acepta | Skill | En vivo |
|---|---|---|---|---|
| highlight report | informe de aspectos destacados (highlight) | informe de estado, status report, reporte de avance | pm-progreso-reportes | 67, 86 |
| checkpoint report | informe de punto de control (checkpoint) | reporte del equipo, avance del paquete | pm-progreso-reportes | 68 |
| end stage report | informe de fin de etapa | cierre de fase | pm-plan-etapa-y-limites | 89 |
| work package / product status account · product register | paquete de trabajo, estado de los productos (`estado.py productos`; registro de productos derivado, sin registro propio) | WP, sprint como paquete, estado de los entregables, entregables pendientes de aceptación, registro de productos | pm-paquetes-trabajo | 90, 125 |
| issue / issue register | issue, incidencia (`issues.csv`) | registro de incidencias, registro de incidentes (PMBOK), issue log, impedimento, bloqueo, alcance adicional, scope creep | pm-issues-cambios | 69, 70, 85, 91 |
| request for change | solicitud de cambio | change request | pm-issues-cambios | 83 |
| risk register | registro de riesgos | matriz de riesgos, matriz de probabilidad e impacto | pm-riesgos | 84 |
| risk response (options) | opciones de respuesta, valor neto de la respuesta | alternativas de respuesta, estrategias de respuesta, análisis costo-beneficio de la respuesta, mitigar (= reducir) | pm-riesgos | 103 |
| risk budget / management reserve | presupuesto de riesgo (respuestas y contingencias de riesgos identificados), reserva de gestión (provisión para riesgos no identificados; la libera solo la junta) | reserva de contingencia, contingencia, colchón para imprevistos, desconocidos desconocidos (PMBOK) | pm-riesgos · pm-costos-presupuesto | — |
| contingent plan / fallback plan | plan de contingencia, plan alternativo | plan de reserva, fallback, aceptación activa (PMBOK), contingencia | pm-riesgos | 104 |
| daily log | diario del proyecto (`diario.md`) | registro diario | pm-registros | 75 |
| — (PMBOK) | registro de supuestos | assumption log, RAID | pm-registros | 88 |
| quality register | registro de calidad | revisión de calidad, aceptación del entregable | pm-calidad | — |
| lessons log / report | registro e informe de lecciones (el informe se arma desde el registro: `lecciones.py informe`) | lecciones aprendidas, registro de lecciones aprendidas (PMBOK), lessons learned report | pm-lecciones-aprendidas | 92, 124 |
| lesson (learn from experience) | lección aprendida: identificada (`registrada`) → clasificada por impacto y proceso (`revisada`) → accionada → verificada | aprendizaje, buena práctica, lesson learned | pm-lecciones-aprendidas | 122, 123 |
| retrospective · after-action review | retrospectiva: reunión propia, distinta de la planificación y del seguimiento (qué funcionó, qué no, qué probamos; sin culpables) | retro, retro de sprint, reseña posterior a la acción, revisión post-acción | pm-agil-hibrido (facilitar la de iteración) · pm-lecciones-aprendidas (taller de etapa) · pm-reuniones (candidatas desde la transcripción) | 31, 121 |
| — (organizational knowledge) | índice de lecciones de la organización | base de conocimiento de lecciones, repositorio de lecciones de la PMO | pm-lecciones-aprendidas | 124 |
| previous lessons (learn from experience) | lecciones previas de otros proyectos (filas con `origen`) | lecciones de proyectos anteriores, aprendizaje organizacional, lessons learned de otros proyectos | pm-lecciones-aprendidas | 113, 114 |
| evaluate stage status · escalate issues and risks | radar de atención (`estado.py radar`: decidir, escalar, desbloquear, vigilar) | resumen operativo diario, «¿qué decido hoy?», bandeja de decisiones, daily brief | pm-orquestador | 108, 109, 110 |
| — | briefing de incorporación | onboarding, inducción, briefing para un integrante nuevo de la junta, un auditor o un agente | pm-progreso-reportes | 111, 112 |
| — (progress review: reporting period) | datos del período → highlight y tablero desde el dato (`estado.py periodo`); juicio del gestor marcado como tal | status report automático, tablero desde los datos, dashboard del período | pm-progreso-reportes · pm-visuales | 127 |
| review of progress: chain of reports | cadena de reporte verificada (`estado.py periodo --verificar`) | reconciliar o cuadrar cifras, consistency check, mismas cifras en informe, tablero y comunicado | pm-progreso-reportes | 128 |
| — (PMBOK) | valor ganado (EVM) | gestión del valor ganado, semáforo | pm-progreso-reportes | — |
| minutes | acta | minuta | pm-reuniones | — |
| — (PMBOK: reuniones; registro de decisiones) | candidatos de la reunión: decisiones (con nivel), compromisos, supuestos y riesgos con cita y hora (`extraccion.py`) | acuerdos, compromisos, action items, decisiones de la reunión, meeting decisions, dueños y fechas | pm-reuniones | 115, 116 |
| assess (issue and change control) | análisis de impacto (`impacto.py`) | evaluación de impacto, impact assessment, análisis integrado de cambios (PMBOK: control integrado de cambios) | pm-issues-cambios | 117, 118 |
| baselines and configuration management (audit trail) | expediente de auditoría (`paquete.py auditoria`, `verificar`) | audit pack, audit trail, paquete de evidencia, data room, due diligence | pm-exportar | 119, 120 |

## Cierre

| Concepto (PRINCE2 7) | pm-method | También se acepta | Skill | En vivo |
|---|---|---|---|---|
| closing a project / handover | cierre, traspaso (handover) | cierre del proyecto, closeout, entrega a operaciones | pm-cierre-proyecto | 126 |
| follow-on action recommendations | recomendaciones de seguimiento (cada issue y riesgo abierto por id, con responsable: C-03) | acciones de seguimiento, pendientes que pasan a operación, riesgos residuales transferidos | pm-cierre-proyecto | 126 |
| benefits review plan | plan de revisión de beneficios | medición de beneficios posterior | pm-cierre-proyecto · pm-caso-de-negocio | — |

## Búsqueda en los proyectos (pm-kb)

Términos de [PM-KB](PM-KB.md), el índice de conocimiento opcional; no son de PRINCE2 ni de PMBOK y no enrutan a una
skill.

| Término | Qué significa en pm-method | También se dice | Dónde |
|---|---|---|---|
| unidad citada | el fragmento mínimo que se busca y se cita: una fila de un registro, una sección de un documento, una diapositiva o una ventana de una transcripción, con su cita `proyecto@commit:archivo:líneas` | fragmento, *chunk* | PM-KB §3 |
| versión vigente | la última versión de cada documento, aunque esté en revisión; es lo que devuelve la búsqueda por defecto, con aviso si hay una aprobada anterior | versión actual, última versión | PM-KB §4 |
| versión aprobada | la última versión con estado `aprobado` (decisión y quién aprobó); `--aprobado` busca solo en ella, para consultas de gobierno | línea base, versión de gobierno | PM-KB §4 |
| circulación | quién puede ver una unidad: `equipo` (todo token del proyecto) o `restringida` (solo un token con `--restringida`) | confidencialidad, nivel de acceso | PM-KB §3.3 |
| BM25 | fórmula de relevancia por palabras que pondera cuántas veces aparece un término y qué tan raro es en el proyecto; la búsqueda por defecto de pm-kb | búsqueda léxica, por palabras clave | PM-KB §9 |
| RRF | fusión por rango recíproco: combina el orden por palabras y el orden por significado (vectores) sumando 1/(60 + puesto) | búsqueda híbrida | PM-KB §9 |
| RLS | seguridad por fila de PostgreSQL: la base solo devuelve las filas de los proyectos y la circulación que permite el token | permisos por fila, *row-level security* | PM-KB §6.3 |
| MCP | protocolo con el que un agente (Claude Code, Hermes) usa herramientas externas; pm-kb expone 9 herramientas de solo lectura | servidor MCP, conector | PM-KB §11.2 |
| portal | la web de pm-kb (`pm-kb servir`): cartera de proyectos y, por proyecto, las pestañas Tableros, Buscar, Artefactos y Preguntar, con la ficha de cada elemento; lee el índice y nunca escribe en la carpeta del proyecto («actualizar ahora» escribe solo en el índice) | interfaz web, tablero web | PM-KB §11.1 |
| tarjeta-enlace | tarjeta del tablero con nombre y una descripción corta cuyo detalle está en la ficha de la fuente, enlazada por id estable (`ficha/<ref>`: R-003, una clave de artefacto, `puerta:<tipo>:<etapa>`, un producto), nunca por ruta; si el archivo se mueve, el enlace sigue funcionando | tarjeta, *card* | PM-KB §5.1 y §11.5; SPEC §1.10.17 |
| instantánea congelada | foto del tablero (`pm-tablero/1`) en un momento del ciclo, guardada por pm-method en `03-control/reportes/tableros/` (JSON y HTML) e inmutable: se congela sola antes de cada decisión de puerta (con la decisión anotada) o con `tablero.py congelar`; el portal las muestra como línea de tiempo y las compara | snapshot, foto del tablero, historial | PM-KB §11.5; SPEC §1.10.17 |
| enlace compartido | dirección de solo lectura a un tablero (el actual o una instantánea, opcionalmente de un actor) para alguien sin token: vence (7 días por defecto, 90 como máximo), se revoca y registra sus usos; el token va después de `#` y se canjea por una sesión | enlace de solo lectura, *share link* | PM-KB §11.7 (`pm-kb compartir`) |
| tablero por actor | el tablero filtrado para una persona: sus elementos R, A, C o I de `raci.csv` y lo que tiene a cargo, pidió o decidió en los registros; el ciclo y las puertas son comunes | vista por persona, tablero personal | PM-KB §11.8; `tablero.py generar --actor` |

## Cómo se verificó

Batería en vivo del 18/10/2026 (28 frases con términos de PRINCE2 en español, PMBOK en español y uso habitual, ids
67–94): **27/28** a la primera; la frase 70 ("registro de incidentes") quedó sin skill en esa corrida. Por eso la
descripción de `pm-issues-cambios` incluye "incidencia" y "registro de incidentes", y la tabla de enrutamiento del
orquestador, "incidencia" y "comité de dirección"; con esos términos, la 70 llegó bien en dos corridas (2/2). Detalle:
`docs/evaluacion/resultados/2026-10-18-terminologia-v2.2.md`.

Frases 95–102 (mapas estratégicos y una de control con "mapa de stakeholders"): **8/8** el 20/10/2026, en
`docs/evaluacion/resultados/2026-10-20-enrutamiento-mapas-v2.3.md`.

Frases 103–130 (opciones de respuesta y plan de contingencia, personas de usuario, radar y briefing, lecciones de
otros proyectos y su ciclo, acuerdos de reunión, análisis de impacto, expediente de auditoría, estado de productos,
datos del período y tres valores con capacidad del release): **28/28** el 21 y el 22/10/2026, con las frases de
control de las skills vecinas; un informe por grupo en `docs/evaluacion/resultados/2026-10-21-*-v2.4.md` y
`docs/evaluacion/resultados/2026-10-22-*-v2.4.md`.

Frases 131–134 (matriz de decisión con pesos y sensibilidad, expediente para la junta, evaluación ponderada de
proveedores y criterios no monetarios sobre opciones con VAN): **4/4** el 28/10/2026 en dos corridas, con 7 frases de
control de las skills vecinas (11/11 en cada una), en `docs/evaluacion/resultados/2026-10-28-decisiones-v2.6.md`.
