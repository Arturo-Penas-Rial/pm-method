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
| — (técnica PMBOK) | línea base de costo, reserva de contingencia | línea base de costos, cost baseline | pm-costos-presupuesto | 78 |
| — | plan de comunicación | plan de gestión de las comunicaciones (PMBOK) | pm-comunicacion-stakeholders | 2, 82 |
| — (técnica de estrategia) | mapa de Wardley | mapa de valor, mapa de evolución, Wardley map, qué construir y qué comprar según la evolución | pm-mapas-estrategicos | 95, 96, 100 |
| — (técnica de diseño de servicios) | mapa de recorrido del cliente | customer journey, customer journey map, CJM, mapa de experiencia, puntos de dolor (pain points) | pm-mapas-estrategicos | 97, 98, 101 |
| — (técnica de diseño de servicios) | carriles internos del recorrido (service blueprint) | service blueprint, plano del servicio, frontstage y backstage | pm-mapas-estrategicos | 99 |

## Control y seguimiento

| Concepto (PRINCE2 7) | pm-method | También se acepta | Skill | En vivo |
|---|---|---|---|---|
| highlight report | informe de aspectos destacados (highlight) | informe de estado, status report, reporte de avance | pm-progreso-reportes | 67, 86 |
| checkpoint report | informe de punto de control (checkpoint) | reporte del equipo, avance del paquete | pm-progreso-reportes | 68 |
| end stage report | informe de fin de etapa | cierre de fase | pm-plan-etapa-y-limites | 89 |
| work package / product status account | paquete de trabajo, estado de los productos | WP, sprint como paquete | pm-paquetes-trabajo | 90 |
| issue / issue register | issue, incidencia (`issues.csv`) | registro de incidencias, registro de incidentes (PMBOK), issue log, impedimento, bloqueo, alcance adicional, scope creep | pm-issues-cambios | 69, 70, 85, 91 |
| request for change | solicitud de cambio | change request | pm-issues-cambios | 83 |
| risk register | registro de riesgos | matriz de riesgos, matriz de probabilidad e impacto | pm-riesgos | 84 |
| daily log | diario del proyecto (`diario.md`) | registro diario | pm-registros | 75 |
| — (PMBOK) | registro de supuestos | assumption log, RAID | pm-registros | 88 |
| quality register | registro de calidad | revisión de calidad, aceptación del entregable | pm-calidad | — |
| lessons log / report | registro e informe de lecciones | lecciones aprendidas, registro de lecciones aprendidas (PMBOK) | pm-lecciones-aprendidas | 92 |
| — (PMBOK) | valor ganado (EVM) | gestión del valor ganado, semáforo | pm-progreso-reportes | — |
| minutes | acta | minuta | pm-reuniones | — |

## Cierre

| Concepto (PRINCE2 7) | pm-method | También se acepta | Skill | En vivo |
|---|---|---|---|---|
| closing a project / handover | cierre, traspaso (handover) | cierre del proyecto, closeout, entrega a operaciones | pm-cierre-proyecto | — |
| benefits review plan | plan de revisión de beneficios | medición de beneficios posterior | pm-cierre-proyecto · pm-caso-de-negocio | — |

## Cómo se verificó

Batería en vivo del 18/10/2026 (28 frases con términos de PRINCE2 en español, PMBOK en español y uso habitual, ids
67–94): **27/28** a la primera; la frase 70 ("registro de incidentes") quedó sin skill en esa corrida. Por eso la
descripción de `pm-issues-cambios` incluye "incidencia" y "registro de incidentes", y la tabla de enrutamiento del
orquestador, "incidencia" y "comité de dirección"; con esos términos, la 70 llegó bien en dos corridas (2/2). Detalle:
`docs/evaluacion/resultados/2026-10-18-terminologia-v2.2.md`.

Frases 95–102 (mapas estratégicos y una de control con "mapa de stakeholders"): **8/8** el 20/10/2026, en
`docs/evaluacion/resultados/2026-10-20-enrutamiento-mapas-v2.3.md`.
