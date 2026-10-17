---
tipo: matriz-comunicaciones
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Matriz de comunicaciones · Communications matrix

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Anexo operativo del enfoque de gestión de la comunicación (communication management approach, `02-planificacion/enfoques/enfoque-comunicacion.md`, dueño pm-enfoques-gestion): aplica sus políticas, no las redefine. La propone el gestor del proyecto, la aprueba el ejecutivo y la acuerdan usuario y proveedor sénior. Se revisa en cada límite de etapa.

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}}
*Según estado.json.*

**Alcance de la comunicación gestionada / Scope of managed communication:** {{alcance}}
*Qué comunicaciones cubre esta matriz (gobernanza, equipo, cliente, proveedores, externos) y cuáles quedan fuera (p. ej. comunicación pública gestionada por otra área).*

**Fuente de audiencias / Audience source:** `03-control/registros/stakeholders.csv` versión del {{fecha_registro}}
*Toda audiencia debe existir en el registro de interesados (ids ST-###). Usar `poder` e `interes` (alto/medio/bajo) para priorizar; las valoraciones de filas `confidencial=si` no se copian aquí.*

## 1. Matriz audiencia × mensaje × canal × frecuencia / Audience × message × channel × frequency

| Audiencia / Audience | Estereotipo / Stereotype | Mensaje / Message | Canal / Channel | Frecuencia / Frequency | Emisor / Sender | Idioma / Language | Retroalimentación / Feedback path |
|---|---|---|---|---|---|---|---|
| {{audiencia_1}} | dirección-patrocinador | Decisiones pendientes y desvíos contra tolerancias / Decisions needed and deviations | {{canal_1}} | {{frecuencia_1}} | {{emisor_1}} | {{idioma_1}} | {{feedback_1}} |
| {{audiencia_2}} | dirección-patrocinador | Informe de destacados / Highlight report | {{canal_2}} | {{frecuencia_2}} | {{emisor_2}} | {{idioma_2}} | {{feedback_2}} |
| {{audiencia_3}} | equipo | Bloqueos, prioridades y cambios aprobados / Blockers, priorities, approved changes | {{canal_3}} | {{frecuencia_3}} | {{emisor_3}} | {{idioma_3}} | {{feedback_3}} |
| {{audiencia_4}} | cliente-usuario | Hitos, entregas y riesgos que le afectan / Milestones, deliveries, risks affecting them | {{canal_4}} | {{frecuencia_4}} | {{emisor_4}} | {{idioma_4}} | {{feedback_4}} |
| {{audiencia_5}} | proveedores | Dependencias, fechas, aceptaciones y pagos / Dependencies, dates, acceptances, payments | {{canal_5}} | {{frecuencia_5}} | {{emisor_5}} | {{idioma_5}} | {{feedback_5}} |
| {{audiencia_6}} | {{estereotipo_6}} | {{mensaje_6}} | {{canal_6}} | {{frecuencia_6}} | {{emisor_6}} | {{idioma_6}} | {{feedback_6}} |

*Una fila por combinación audiencia × mensaje. Estereotipos: dirección-patrocinador · equipo · cliente-usuario · proveedores · regulador-comunidad. Canal: reunión, correo, chat, tablero, repositorio. Frecuencia alineada con hitos e informes del plan. Retroalimentación: cómo esa audiencia devuelve preguntas o preocupaciones (la comunicación es bidireccional).*

## 2. Comunicaciones por evento / Event-driven communications

| Evento / Event | Audiencias / Audiences | Mensaje / Message | Plazo / Timing | Emisor / Sender | Autoriza / Authorized by |
|---|---|---|---|---|---|
| Autorización de inicio / Initiation authorized | {{aud_inicio}} | Notificación de inicio / Initiation notice | {{plazo_inicio}} | Junta / Board | Ejecutivo / Executive |
| Autorización del proyecto o etapa / Project or stage authorized | {{aud_etapa}} | Notificación de autorización, nuevas tolerancias / Authorization notice | {{plazo_etapa}} | Junta / Board | Ejecutivo / Executive |
| Excepción / Exception | {{aud_excepcion}} | Aviso temprano verbal + informe escrito / Early verbal warning + written report | Inmediato / Immediate | Gestor / PM | n/a (obligatorio) |
| Cambio aprobado / Change approved | {{aud_cambio}} | Qué cambia y desde cuándo / What changes and when | {{plazo_cambio}} | {{emisor_cambio}} | {{autoriza_cambio}} |
| Hito alcanzado / Milestone reached | {{aud_hito}} | Entrega y próximos pasos / Delivery and next steps | {{plazo_hito}} | {{emisor_hito}} | {{autoriza_hito}} |
| Revisión de iteración o demo (ágil/híbrido) / Sprint review or demo | {{aud_revision}} | Incremento terminado, burn-up, Must en riesgo, retroalimentación / Done increment, burn-up, Must at risk, feedback | Cada {{cadencia_iteracion}} días / Every iteration | Equipo + product owner / Team + PO | Product owner |
| Cierre / Closure | {{aud_cierre}} | Notificación de cierre, retiro de recursos, fecha límite de cargos / Closure notice | {{plazo_cierre}} | Junta / Board | Ejecutivo / Executive |

*Las comunicaciones de puerta las emite la junta; el agente redacta y el ejecutivo firma. Completar el resto según el proyecto.*

## 3. Reglas / Rules

**Comunicación extraordinaria / Extraordinary communication:** {{regla_extraordinaria}}
*Umbral que dispara una comunicación no programada (p. ej. pronóstico en ámbar en cualquier objetivo, riesgo nuevo por encima de la línea de tolerancia).*

**Información sensible / Sensitive information:** {{regla_sensible}}
*Quién autoriza divulgar cifras de costo, datos de clientes o asuntos comerciales a terceros; qué audiencias nunca reciben qué información.*

**Escucha e informalidad / Listening and informal channels:** {{regla_escucha}}
*Conversaciones periódicas con gestores de equipo e influenciadores; cómo se recogen preocupaciones fuera de los informes.*

**Equipos remotos o híbridos / Remote or hybrid teams:** {{regla_remoto}}
*Zona horaria, tiempo no estructurado, evitar grupos "dentro" y "fuera" por ubicación. "n/a" si todos están co-ubicados.*

**Fase silenciosa / Quiet phase:** {{fase_silenciosa}}
*Si aplica: hasta qué hito la comunicación amplia se restringe a un grupo de influenciadores, y quién lo decidió.*

**Revisión de la matriz / Matrix review:** {{revision}}
*En cada límite de etapa y cuando entran o salen interesados clave.*

## 4. Glosario del proyecto / Project glossary

| Término / Term | Significado / Meaning |
|---|---|
| {{termino_1}} | {{significado_1}} |

*Acrónimos y términos con sentido particular que aparecen en los informes.*

## Lista de verificación / Checklist
- [ ] Cada interesado de `stakeholders.csv` aparece en al menos una fila.
- [ ] Cada fila tiene audiencia, mensaje, canal, frecuencia y emisor; idioma si difiere del proyecto.
- [ ] Coherente con el enfoque de comunicación aprobado; en ágil/híbrido incluye la revisión de iteración o demo.
- [ ] Cada audiencia tiene una vía de retroalimentación.
- [ ] Las frecuencias coinciden con los hitos y la cadencia de informes del plan de etapa.
- [ ] Existe regla de comunicación extraordinaria y de información sensible.
- [ ] Las comunicaciones de puerta (inicio, autorización, cierre) tienen emisor junta y firma del ejecutivo.
- [ ] Aprobación del ejecutivo registrada antes de pasar a `estado: aprobado` y de copiar canal/frecuencia al registro.
