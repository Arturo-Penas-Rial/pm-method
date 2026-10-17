---
tipo: auditoria-adquisiciones
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Auditoría de adquisiciones · Procurement audit — {{id_contrato}} {{proveedor}}

> Borrador generado con apoyo de IA; los hallazgos se cruzan con los informes de estado del contratista y los registros citados. / AI-assisted draft; findings are cross-checked against contractor status reports and the cited registers.

## 1. Datos generales / General data

**Auditor / Auditor:** {{auditor}}
*Persona o función independiente del equipo que gestionó el contrato, con participación de compras.*

**Fecha de la auditoría / Audit date:** {{fecha_auditoria}}
*Fecha o rango.*

**Contrato y proveedor / Contract and vendor:** {{id_contrato}} — {{proveedor}}
*Objeto, tipo de contrato, monto y período.*

**Alcance de la auditoría / Audit scope:** {{alcance}}
*Desempeño del proveedor, proceso de adquisición completo o una fase; motivo (periódica, previa al cierre, a demanda).*

**Evidencia revisada / Evidence reviewed:** {{evidencia}}
*Estrategia, criterios de selección, documentos de licitación, contrato, informes de estado, cambios.csv, reclamaciones, aceptaciones, pagos.*

## 2. Bloque A — Desempeño del proveedor / Block A — Vendor performance

| Dimensión / Dimension | Funcionó bien / What worked well | Puede mejorar / What can be improved | Evidencia / Evidence |
|---|---|---|---|
| Alcance / Scope | {{alcance_bien}} | {{alcance_mejorar}} | {{alcance_ev}} |
| Calidad / Quality | {{calidad_bien}} | {{calidad_mejorar}} | {{calidad_ev}} |
| Cronograma / Schedule | {{cronograma_bien}} | {{cronograma_mejorar}} | {{cronograma_ev}} |
| Costo / Cost | {{costo_bien}} | {{costo_mejorar}} | {{costo_ev}} |
| Otros (trato, respuesta, colaboración) / Other (ease of work, responsiveness, collaboration) | {{otros_bien}} | {{otros_mejorar}} | {{otros_ev}} |

*Cinco dimensiones, incluidas las cualitativas; citar informes de estado, Q-nnn, I-nnn.*

## 3. Bloque B — Cumplimiento del proceso de adquisición / Block B — Procurement process compliance

| Proceso / Process | Seguido / Followed | Herramientas y técnicas eficaces / Effective tools and techniques | Desvíos observados / Observed deviations |
|---|---|---|---|
| Planificar (hacer o comprar, estrategia, criterios) / Planning | {{plan_seguido}} | {{plan_tecnicas}} | {{plan_desvios}} |
| Conducir (licitación, evaluación, adjudicación, firma) / Conducting | {{conducir_seguido}} | {{conducir_tecnicas}} | {{conducir_desvios}} |
| Controlar (informes, cambios, reclamaciones, aceptación) / Controlling | {{controlar_seguido}} | {{controlar_tecnicas}} | {{controlar_desvios}} |
| Cerrar (condiciones de cierre, evaluación) / Closing | {{cerrar_seguido}} | {{cerrar_tecnicas}} | {{cerrar_desvios}} |

*Seguido: sí / parcial / no. Verificar en particular: método de selección fijado antes de licitar, planilla congelada, igualdad de información a oferentes, cambios por el mecanismo contractual.*

## 4. Bloque C — Buenas prácticas a compartir / Block C — Good practices to share

| Práctica / Practice | Dónde incorporarla (política, plantilla, proceso) / Where to embed | Lección (L-nnn) / Lesson |
|---|---|---|
| {{bp_1}} | {{bp_donde_1}} | {{bp_leccion_1}} |

*Prácticas que deberían pasar a políticas o plantillas de compras y al registro de lecciones.*

## 5. Bloque D — Áreas de mejora y hallazgos / Block D — Areas for improvement and findings

| Id / Id | Hallazgo / Finding | Severidad / Severity | Acción / Action | Responsable / Owner | Fecha límite / Due date | Estado / Status |
|---|---|---|---|---|---|---|
| {{h_id_1}} | {{h_desc_1}} | {{h_sev_1}} | {{h_accion_1}} | {{h_resp_1}} | {{h_fecha_1}} | {{h_estado_1}} |

*Severidad: mayor, menor, observación. Mejoras al proceso de compras, cambios a políticas, lecciones con responsable.*

## 6. Calificación global del proveedor / Overall vendor rating

| Alcance / Scope | Calidad / Quality | Cronograma / Schedule | Costo / Cost | Otros / Other | Promedio / Average |
|---|---|---|---|---|---|
| {{cal_alcance}} | {{cal_calidad}} | {{cal_cronograma}} | {{cal_costo}} | {{cal_otros}} | {{cal_promedio}} |

*Escala 1–5 para el repositorio de proveedores; coherente con el informe de cierre de contrato.*

## 7. Conclusión / Conclusion

**Valoración / Assessment:** {{valoracion}}
*Conforme, conforme con observaciones o no conforme; aptitud para cerrar el contrato o para futuras contrataciones.*

**Recomendaciones a compras / Recommendations to procurement:** {{recomendaciones}}
*Cambios de política, plantilla o proceso.*

**Destinatarios / Recipients:** {{destinatarios}}
*Gestor del proyecto, ejecutivo, proveedor sénior, compras, PMO.*

## Lista de verificación / Checklist
- [ ] Auditor independiente; compras participó.
- [ ] Proveedor evaluado en las cinco dimensiones, incluidas las cualitativas, con evidencia.
- [ ] Cumplimiento verificado de los procesos planificar, conducir, controlar y cerrar.
- [ ] Hallazgos cruzados con los informes de estado del contratista.
- [ ] Buenas prácticas y mejoras formuladas como cambios a políticas o plantillas.
- [ ] Lecciones registradas en lecciones.csv con responsable.
- [ ] Resultado enviado al informe de cierre de contrato.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
