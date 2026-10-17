---
tipo: auditoria-riesgos
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Auditoría de riesgos · Risk audit

**Proyecto / Project:** {{proyecto}} · **Etapa auditada / Stage audited:** {{etapa}}
*Normalmente al límite de etapa, al cierre del proyecto o a pedido de aseguramiento o del ejecutivo.*

**Auditor / Auditor:** {{auditor}}
*Persona independiente del equipo de gestión (aseguramiento del proyecto o revisor externo); si lo hace el gestor, declararlo como autoevaluación.*

**Período auditado / Period audited:** {{periodo_desde}} – {{periodo_hasta}}

**Fuentes revisadas / Sources reviewed:** {{fuentes}}
*`riesgos.csv`, hojas de datos, informes de riesgos, `issues.csv` (riesgos ocurridos y issues sin riesgo previo), enfoque de riesgos, `decisiones.csv`, `lecciones.csv`.*

**Alcance / Scope:** {{alcance}}
*Bloques incluidos: A eventos, B respuestas, C proceso, D buenas prácticas, E mejoras. Versión mínima: A y B.*

## A. Auditoría de eventos ocurridos / Risk event audit

| Id | Evento ocurrido / Event | Causa registrada / Recorded cause | Respuesta aplicada / Response applied | ¿Era previsible? / Foreseeable? | ¿Hubo alerta temprana? / Early warning? | Comentario / Comment |
|---|---|---|---|---|---|---|
| {{ev_id}} | {{ev_evento}} | {{ev_causa}} | {{ev_respuesta}} | {{ev_previsible}} | {{ev_alerta}} | {{ev_comentario}} |

*Un renglón por riesgo con `estado=ocurrido` y por issue del período sin `origen R-###` (sorpresa). Juzgar si pudo identificarse antes y si la respuesta llegó a tiempo.*

## B. Auditoría de respuestas / Risk response audit

| Id | Estrategia / Strategy | Acciones ejecutadas / Actions done | Residual previsto vs. real / Planned vs. actual residual | Costo previsto vs. real / Planned vs. actual cost | Exitosa / Successful | Mejora / Improvement |
|---|---|---|---|---|---|---|
| {{rs_id}} | {{rs_estrategia}} | {{rs_acciones}} | {{rs_residual}} | {{rs_costo}} | {{rs_exitosa}} | {{rs_mejora}} |

*`si`, `no`, `parcial`. Incluir oportunidades explotadas o mejoradas, no solo amenazas.*

## C. Auditoría del proceso / Process audit

| Paso del procedimiento / Procedure step | Cumplido / Followed | Evidencia / Evidence | Técnicas usadas / Techniques used | Observación / Observation |
|---|---|---|---|---|
| Definir contexto y objetivos en riesgo | {{c1_cumplido}} | {{c1_evidencia}} | {{c1_tecnicas}} | {{c1_obs}} |
| Identificar amenazas y oportunidades | {{c2_cumplido}} | {{c2_evidencia}} | {{c2_tecnicas}} | {{c2_obs}} |
| Evaluar (P×I, proximidad, perfil agregado) | {{c3_cumplido}} | {{c3_evidencia}} | {{c3_tecnicas}} | {{c3_obs}} |
| Planificar respuestas (justificación, residual, secundarios) | {{c4_cumplido}} | {{c4_evidencia}} | {{c4_tecnicas}} | {{c4_obs}} |
| Implementar (propietarios, ejecutores, acciones en plan) | {{c5_cumplido}} | {{c5_evidencia}} | {{c5_tecnicas}} | {{c5_obs}} |
| Comunicar (informes, escalados, decisiones) | {{c6_cumplido}} | {{c6_evidencia}} | {{c6_tecnicas}} | {{c6_obs}} |
| Presupuesto de riesgo (autorización y control) | {{c7_cumplido}} | {{c7_evidencia}} | {{c7_tecnicas}} | {{c7_obs}} |
| Cumplimiento del enfoque de riesgos y políticas corporativas | {{c8_cumplido}} | {{c8_evidencia}} | {{c8_tecnicas}} | {{c8_obs}} |

*`si`, `parcial`, `no`. Evidencia: ids, fechas, documentos.*

## D. Indicadores / Indicators

| Indicador / Indicator | Fórmula / Formula | Valor / Value | Lectura / Reading |
|---|---|---|---|
| Tasa de materialización / Materialization rate | riesgos ocurridos / riesgos identificados | {{tasa_materializacion}} | {{lect_materializacion}} |
| Tasa de sorpresa / Surprise rate | issues sin riesgo previo / total de issues | {{tasa_sorpresa}} | {{lect_sorpresa}} |
| Eficacia de respuestas / Response effectiveness | respuestas exitosas / respuestas implementadas | {{eficacia}} | {{lect_eficacia}} |
| Puntualidad / Timeliness | respuestas ejecutadas antes del disparador / respuestas planificadas | {{puntualidad}} | {{lect_puntualidad}} |
| Revisión al día / Review currency | riesgos revisados en cadencia / riesgos abiertos | {{revision_al_dia}} | {{lect_revision}} |
| Cobertura del presupuesto de riesgo / Risk budget coverage | remanente / Σ EMV aceptados | {{cobertura}} | {{lect_cobertura}} |

*Una tasa de sorpresa alta indica identificación deficiente; eficacia baja indica respuestas mal dimensionadas o no ejecutadas.*

## E. Buenas prácticas a compartir / Good practices to share
{{buenas_practicas}}
*Prácticas repetibles, plantillas o técnicas que funcionaron; destinatario (equipo, proyecto, organización).*

## F. Áreas de mejora / Areas for improvement

| Mejora / Improvement | Acción / Action | Responsable / Owner | Fecha / Due | Lección (L-###) |
|---|---|---|---|---|
| {{mej_1}} | {{acc_1}} | {{resp_1}} | {{fecha_1}} | {{lec_1}} |
| {{mej_2}} | {{acc_2}} | {{resp_2}} | {{fecha_2}} | {{lec_2}} |

*Cada mejora genera una fila en `lecciones.csv` con responsable de seguimiento; las que cambian el enfoque de riesgos se proponen como actualización del PID en el límite de etapa.*

## G. Señales de sesgo / Bias signals
{{senales_sesgo}}
*Todos los riesgos bajos, ausencia de oportunidades, sin escalados en varios períodos, propietario único mayoritario; contramedida sugerida.*

## H. Conclusión / Conclusion
{{conclusion}}
*Juicio global sobre la eficacia de la gestión de riesgos en el período y recomendación a la junta (mantener, reforzar, reducir formalidad).*

## Lista de verificación / Checklist
- [ ] Bloques A y B completos para todos los riesgos ocurridos y respuestas implementadas del período.
- [ ] Cada evento ocurrido tiene juicio de previsibilidad y de alerta temprana.
- [ ] Eficacia de respuestas evaluada con evidencia (residual y costo reales).
- [ ] Proceso comparado con el enfoque de riesgos aprobado.
- [ ] Indicadores calculados con cifras de `riesgos.csv` e `issues.csv`.
- [ ] Oportunidades incluidas.
- [ ] Mejoras con responsable, fecha y lección registrada.
- [ ] Resumen incorporado al informe de riesgos o al informe de fin de etapa.
