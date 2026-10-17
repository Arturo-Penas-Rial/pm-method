---
tipo: acta-reunion
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
reunion: "{{nombre_reunion}}"
fuente: "{{fuente}}"
---

# Acta de reunión · Meeting minutes

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT** a partir de {{fuente}}. Cada punto remite a la fuente; lo no dicho explícitamente está marcado `[por confirmar]`. La confirma quien presidió la reunión antes de distribuirla.

**Reunión / Meeting:** {{nombre_reunion}} · **Tipo / Type:** {{tipo_reunion}}
*Junta, checkpoint, revisión de etapa, reunión con cliente, retrospectiva, otra.*

**Fecha y hora / Date and time:** {{fecha_hora}} · **Duración / Duration:** {{duracion}} · **Modalidad / Format:** {{modalidad}}
*Presencial, remota, híbrida.*

**Preside / Chair:** {{preside}} · **Redacta / Minutes by:** {{redacta}}
*Quien preside confirma el acta.*

**Fuente / Source:** {{fuente}}
*Transcripción normalizada (ruta en 03-control/reuniones/), notas, instantánea de una herramienta de reuniones conectada (03-control/fuentes/); o "reconstruida de memoria" si no hay registro.*

## 1. Asistentes / Attendees

| Nombre / Name | Rol en el proyecto / Project role | Organización / Organization | Asistió / Attended |
|---|---|---|---|
| {{asistente_1}} | {{rol_1}} | {{org_1}} | {{asistio_1}} |
| {{asistente_2}} | {{rol_2}} | {{org_2}} | {{asistio_2}} |

*Incluir ausentes convocados. Solo nombre, rol y organización: ningún otro dato personal.*

## 2. Agenda y temas tratados / Agenda and topics

| # | Tema / Topic | Resumen / Summary | Referencia / Reference |
|---|---|---|---|
| 1 | {{tema_1}} | {{resumen_1}} | {{ref_1}} |
| 2 | {{tema_2}} | {{resumen_2}} | {{ref_2}} |

*Tres a cinco líneas por tema; referencia a minuto o párrafo de la fuente.*

## 3. Decisiones / Decisions

| # | Decisión / Decision | Decidido por / Decided by | Autoridad / Authority | Opciones consideradas / Options considered | Id en decisiones.csv |
|---|---|---|---|---|---|
| D1 | {{decision_1}} | {{decidido_1}} | {{autoridad_1}} | {{opciones_1}} | {{id_dec_1}} |

*Solo decisiones enunciadas por alguien con autoridad para tomarlas (gestor, autoridad de cambio, ejecutivo/junta). Si una decisión corresponde a la junta y la tomó otro, marcar "[por confirmar: requiere ratificación del ejecutivo]". Las decisiones sobre cambios van a cambios.csv.*

## 4. Acciones acordadas / Agreed actions

| # | Acción / Action | Responsable / Owner | Fecha límite / Due | Criterio de hecho / Done when | Id en acciones.csv / Action id (A-###) |
|---|---|---|---|---|---|
| A1 | {{accion_1}} | {{responsable_1}} | {{fecha_limite_1}} | {{hecho_1}} | {{id_accion_1}} |
| A2 | {{accion_2}} | {{responsable_2}} | {{fecha_limite_2}} | {{hecho_2}} | {{id_accion_2}} |

*Verbo en infinitivo, una persona responsable, fecha concreta. Sin responsable o sin fecha no es acción: va a "Preguntas abiertas". Tras confirmar el acta se cargan con `registro.py agregar acciones --campo origen=acta-{{fecha}}-...` (una acción no es un issue).*

## 5. Riesgos, issues y excepciones mencionados / Risks, issues and exceptions raised

| Tipo / Type | Descripción / Description | Propietario propuesto / Proposed owner | Registro destino / Target register | Id |
|---|---|---|---|---|
| {{tipo_r_1}} | {{desc_r_1}} | {{prop_r_1}} | {{registro_r_1}} | {{id_r_1}} |

*Tipo: riesgo (podría ocurrir) · issue (ocurrió; uno de los cinco tipos) · excepción (pronóstico fuera de tolerancia: escalar a pm-director, no absorber). Riesgos con estructura causa → evento → efecto.*

## 6. Preguntas abiertas / Open questions

- {{pregunta_1}} — quién responde: {{quien_1}}, para cuándo: {{cuando_1}}
*Todo lo que quedó sin dueño o sin fecha.*

## 7. Lecciones / Lessons

- {{leccion_1}}
*Qué esperábamos, qué ocurrió, qué funcionó, qué no, qué cambiar. Va a lecciones.csv si se confirma.*

## 8. Señales agregadas de dinámica (opcional, con consentimiento) / Aggregated dynamics signals (optional, with consent)

**Consentimiento declarado por / Consent declared by:** {{consentimiento}}
*Nombre de quien confirmó que los participantes aceptaron el análisis. Si está vacío, esta sección se elimina. Para un análisis de varias reuniones usar `analisis-clima-equipo.md`.*

**Señales / Signals:** {{senales}}
*Calculadas sobre la transcripción con `--anonimizar`. Solo agregadas por rol o por equipo: distribución del tiempo de palabra por rol, temas con más idas y vueltas, acciones vencidas por equipo, ausencia de menciones a riesgos. Nunca por persona, nunca juicios individuales.*

**Ajuste de comunicación propuesto / Proposed communication adjustment:** {{ajuste}}
*Qué cambiar en la próxima reunión o en la matriz.*

## 9. Próxima reunión / Next meeting

**Fecha / Date:** {{proxima_fecha}} · **Temas / Topics:** {{proximos_temas}}

## Lista de verificación / Checklist
- [ ] Asistentes con rol; ausentes convocados indicados.
- [ ] Cada decisión tiene quién y con qué autoridad; las que exceden la autoridad están marcadas para ratificación.
- [ ] Cada acción tiene responsable, fecha y criterio de hecho; ids `A-###` de `acciones.csv` anotados tras confirmación.
- [ ] Decisiones de junta (o puertas) marcadas para que las registre `pm-director`; no se registran desde el acta.
- [ ] Pronósticos fuera de tolerancia marcados como excepción y derivados a `pm-director`.
- [ ] Nada inferido: lo tácito lleva `[por confirmar]`.
- [ ] Sección 8 presente solo con consentimiento, anonimizada y sin datos nominativos ni juicios individuales.
- [ ] Cargas a registros hechas solo después de confirmar el acta.
- [ ] Confirmada por quien presidió antes de distribuir; distribución según la matriz y con confirmación.
