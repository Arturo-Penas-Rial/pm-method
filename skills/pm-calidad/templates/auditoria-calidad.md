---
tipo: auditoria-calidad
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Auditoría de calidad · Quality audit — {{proyecto}} — {{fecha_auditoria}}

> Borrador generado con apoyo de IA; los hallazgos se basan en la evidencia citada. La auditoría busca mejorar, no sancionar. / AI-assisted draft; findings rest on the cited evidence. The audit aims to improve, not to punish.

## 1. Datos generales / General data

**Auditor / Auditor:** {{auditor}}
*Persona o función independiente del trabajo auditado (aseguramiento, PMO, auditor externo).*

**Fecha de la auditoría / Audit date:** {{fecha_auditoria}}
*Fecha o rango de fechas en que se revisó la evidencia.*

**Fecha de preparación del informe / Report date:** {{fecha_informe}}
*Cuándo se emitió este documento.*

**Alcance / Scope:** {{alcance}}
*Etapa, paquetes, productos o procesos cubiertos; qué queda fuera.*

**Destinatarios / Recipients:** {{destinatarios}}
*Gestor del proyecto, junta, aseguramiento, PMO; según el enfoque de comunicación.*

## 2. Áreas auditadas / Areas audited

| Área / Area | Auditada / Audited | Evidencia revisada / Evidence reviewed |
|---|---|---|
| Procesos del proyecto / Project processes | {{area_procesos}} | {{ev_procesos}} |
| Documentos del proyecto / Project documents | {{area_documentos}} | {{ev_documentos}} |
| Requisitos del producto / Product requirements | {{area_requisitos}} | {{ev_requisitos}} |
| Documentación del producto / Product documentation | {{area_doc_producto}} | {{ev_doc_producto}} |
| Reparación de defectos / Defect repair | {{area_defectos}} | {{ev_defectos}} |
| Cumplimiento de políticas y procedimientos / Policy and procedure compliance | {{area_politicas}} | {{ev_politicas}} |
| Cumplimiento del enfoque de gestión de la calidad / Quality management approach compliance | {{area_enfoque}} | {{ev_enfoque}} |

*Marcar sí / no por área y citar rutas (calidad.csv, descripciones, actas de revisión, issues.csv).*

## 3. Cobertura del registro de calidad / Quality register coverage

**Productos del plan / Products in plan:** {{n_productos}}
*Total de productos del plan vigente.*

**Productos con al menos una actividad planificada / Products with at least one planned activity:** {{n_con_actividad}}
*Cobertura esperada: 100 %; explicar brechas.*

**Actividades vencidas sin fecha real / Overdue activities without actual date:** {{n_vencidas}}
*Ids Q-nnn.*

**Fallos sin acción asociada / Failures without associated action:** {{n_fallos_sin_accion}}
*Ids Q-nnn con resultado `rechazado` y sin issue ni repetición planificada.*

**Cambios aprobados y acciones correctivas previas verificadas / Approved changes and previous corrective actions verified:** {{cambios_verificados}}
*Ids C-nnn e I-nnn cuya implementación se comprobó.*

## 4. Buenas prácticas detectadas / Good practices identified

| Práctica / Practice | Dónde se observó / Where observed | Recomendación de difusión / Sharing recommendation | Lección (L-nnn) / Lesson |
|---|---|---|---|
| {{bp_1}} | {{bp_donde_1}} | {{bp_recomendacion_1}} | {{bp_leccion_1}} |

*Prácticas que merecen repetirse en otras etapas o proyectos; se vuelcan a lecciones.csv.*

## 5. Áreas de mejora / Areas for improvement

| Área / Area | Situación actual / Current state | Medida objetivo / Target measure | Responsable / Owner | Fecha / Date |
|---|---|---|---|---|
| {{mejora_area_1}} | {{mejora_actual_1}} | {{mejora_objetivo_1}} | {{mejora_resp_1}} | {{mejora_fecha_1}} |

*Cada mejora lleva una medida verificable (p. ej. cobertura de pruebas del 55 % al 80 %).*

## 6. Hallazgos: deficiencias o defectos / Findings: deficiencies or defects

| Id / Id | Hallazgo / Finding | Área / Area | Severidad / Severity | Acción / Action | Responsable / Owner | Fecha límite / Due date | Estado / Status | Issue (I-nnn) |
|---|---|---|---|---|---|---|---|---|
| {{h_id_1}} | {{h_desc_1}} | {{h_area_1}} | {{h_sev_1}} | {{h_accion_1}} | {{h_resp_1}} | {{h_fecha_1}} | {{h_estado_1}} | {{h_issue_1}} |

*Severidad: mayor (incumple el enfoque o pone en riesgo la aceptación), menor, observación. Estado: abierto, en progreso, cerrado, verificado. Las deficiencias se siguen como issues.*

## 7. Conclusión / Conclusion

**Valoración global / Overall assessment:** {{valoracion}}
*Conforme · conforme con observaciones · no conforme; en una o dos frases con los hallazgos mayores.*

**Riesgos para la aceptación o la etapa / Risks to acceptance or stage:** {{riesgos_derivados}}
*Ids R-nnn si se registraron riesgos nuevos.*

**Auditoría de seguimiento / Follow-up audit:** {{fecha_seguimiento}}
*Fecha prevista y alcance (verificar cierre de hallazgos mayores).*

## Lista de verificación / Checklist
- [ ] Auditor independiente del trabajo auditado.
- [ ] Áreas auditadas marcadas con evidencia citada.
- [ ] Cobertura del registro de calidad calculada y brechas explicadas.
- [ ] Cada deficiencia con severidad, acción, responsable, fecha límite y estado.
- [ ] Áreas de mejora con medida objetivo.
- [ ] Buenas prácticas volcadas a lecciones.csv; deficiencias a issues.csv.
- [ ] Implementación de cambios aprobados y acciones previas verificada.
- [ ] Auditoría de seguimiento programada.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
