---
tipo: solicitud-cambio
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Solicitud de cambio · Change request

**Identificador / Change id:** {{id_cambio}} · **Issue de origen / Source issue:** {{id_issue}}
*El id `C-###` de `cambios.csv` y el `I-###` de tipo `solicitud-cambio` que lo originó.*

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}}

**Fecha de presentación / Date submitted:** {{fecha_presentacion}}
*ISO.*

**Solicitante / Requestor:** {{solicitante}}
*Nombre y rol; cualquier interesado puede solicitar un cambio.*

**Categoría / Category:** {{categoria}}
*Aspecto principal afectado: alcance, calidad, requisitos, costo, cronograma, documentos, contrato. Puede marcarse más de uno.*

**Prioridad / Priority:** {{prioridad}} · **Obligatorio o discrecional / Mandatory or discretionary:** {{obligatoriedad}}
*Urgente, alta, media, baja. Obligatorio cuando es legal, de seguridad o contractual.*

**Fecha límite para decidir / Decision needed by:** {{fecha_limite_decision}}
*Si no hay plazo real, dejar vacío; no inventar urgencia.*

## 1. Descripción del cambio / Description of the change

**Situación actual (línea base) / Current baseline:** {{antes}}
*Qué dice hoy el producto, plan o documento aprobado, con su versión (`estado.json.artefactos`).*

**Situación propuesta / Proposed state:** {{despues}}
*Qué quedaría después; el lector debe poder reconstruir el antes y el después sin otro documento.*

**Productos y documentos afectados / Products and documents affected:** {{productos_afectados}}
*Ids del PBS/WBS, descripciones de producto, plan de etapa, PID, requisitos; indicar versión actual → versión propuesta.*

## 2. Justificación / Justification

**Origen / Origin:** {{origen}}
*Normativo, defecto, requerimiento del cliente, oportunidad, evento externo, lección aprendida.*

**Por qué es necesario / Why it is needed:** {{justificacion}}

**Consecuencia de no hacer el cambio / Implication of not changing:** {{consecuencia_no_cambio}}
*Qué ocurre si se rechaza: beneficios perdidos, incumplimiento, riesgo.*

## 3. Análisis de impacto / Impact analysis

| Objetivo / Objective | Impacto / Impact | Cuantificación / Quantification | Tolerancia vigente / Current tolerance | ¿Sale de tolerancia? / Breaches tolerance? |
|---|---|---|---|---|
| Alcance / Scope | {{imp_alcance}} | {{cuant_alcance}} | {{tol_alcance}} | {{br_alcance}} |
| Tiempo / Time | {{imp_tiempo}} | {{cuant_tiempo}} días; ruta crítica: {{ruta_critica}} | {{tol_tiempo}} | {{br_tiempo}} |
| Costo / Cost | {{imp_costo}} | {{cuant_costo}} {{moneda}} ({{variacion_costo_pct}} % del BAC) | {{tol_costo}} | {{br_costo}} |
| Calidad / Quality | {{imp_calidad}} | {{cuant_calidad}} | {{tol_calidad}} | {{br_calidad}} |
| Beneficios / Benefits | {{imp_beneficios}} | {{cuant_beneficios}} | {{tol_beneficios}} | {{br_beneficios}} |
| Sostenibilidad / Sustainability | {{imp_sostenibilidad}} | {{cuant_sostenibilidad}} | {{tol_sostenibilidad}} | {{br_sostenibilidad}} |
| Riesgo / Risk | {{imp_riesgo}} | riesgos nuevos o modificados: {{riesgos_ids}} | {{tol_riesgo}} | {{br_riesgo}} |

*Escribir "ninguno" cuando no hay impacto, nunca dejar vacío. Ruta crítica: `si`, `no`, `no-evaluado`. Variación relativa = costo del cambio / BAC vigente; días adicionales / duración planificada.*

**Impacto en el caso de negocio / Business case impact:** {{impacto_caso_negocio}}
*¿Sigue siendo viable y deseable el proyecto con y sin el cambio?*

**Impacto en otros productos o paquetes de trabajo / Impact on other products or work packages:** {{impacto_otros}}

**Impacto en stakeholders / Stakeholder impact:** {{impacto_stakeholders}}
*Quién se ve afectado y cómo (recapacitación, comunicación, contrato).*

## 4. Opciones / Options

| Opción / Option | Descripción / Description | Ventaja / Benefit | Impacto de implementación / Implementation impact | Fuente de financiación / Funding source |
|---|---|---|---|---|
| A | {{opcion_a}} | {{ventaja_a}} | {{impacto_a}} | {{financiacion_a}} |
| B | {{opcion_b}} | {{ventaja_b}} | {{impacto_b}} | {{financiacion_b}} |
| Rechazar / Reject | no hacer el cambio | {{ventaja_rechazo}} | {{impacto_rechazo}} | — |

*Fuente de financiación: presupuesto de cambio, reducción de alcance en otra parte, fondos adicionales (requiere junta), reserva de riesgo (solo si el cambio responde a un riesgo).*

## 5. Recomendación / Recommendation

**Opción recomendada / Recommended option:** {{opcion_recomendada}}

**Razones / Rationale:** {{razones}}

**Consecuencias de aprobar / If approved:** {{consecuencias_aprobar}}
**Consecuencias de rechazar / If rejected:** {{consecuencias_rechazar}}

## 6. Autoridad y decisión / Authority and decision

**Nivel que decide / Deciding level:** {{nivel_decision}}
*Autoridad de cambio (dentro de umbral {{umbral_autoridad}} y presupuesto de cambio remanente {{presupuesto_cambio_remanente}}), junta del proyecto, o capa de negocio. Si el cambio saca la etapa de tolerancia, se acompaña de informe de excepción.*

**Disposición / Disposition:** {{disposicion}}
*`aprobado`, `rechazado`, `diferido`, `pedir-plan-excepcion`, `pedir-mas-informacion`. Vacío hasta la decisión humana.*

**Decidido por / Decided by:** {{decidido_por}} · **Fecha / Date:** {{fecha_decision}} · **Decisión / Decision log:** {{id_decision}}
*Nombre, rol y `D-###` en `decisiones.csv`; también en `cambios.csv.decidido_por`. Si decidió la junta, la puerta `decision-ad-hoc` y su fila las registra `pm-director`. Un intercambio del product owner dentro de la tolerancia no usa esta plantilla: es cambio ligero (`nivel=product-owner`).*

**Condiciones / Conditions:** {{condiciones}}

**Fecha de reevaluación (si diferido) / Re-evaluation date (if deferred):** {{fecha_reevaluacion}}

## 7. Implementación / Implementation

**Nueva versión de los artefactos / New artifact versions:** {{nuevas_versiones}}
*`estado.json.artefactos.<nombre>.version`; conservar la versión anterior.*

**Paquete de trabajo o acción / Work package or action:** {{paquete_accion}}

**Riesgos nuevos registrados / New risks registered:** {{riesgos_nuevos}}

**Lección / Lesson:** {{leccion}}

## Lista de verificación / Checklist
- [ ] Antes y después reconstruibles sin otro documento; productos y versiones afectados identificados.
- [ ] Justificación con origen y consecuencia de no cambiar.
- [ ] Impacto declarado para los siete objetivos (aunque sea "ninguno"), comparado con las tolerancias y con el caso de negocio; ruta crítica evaluada.
- [ ] Al menos dos opciones más "rechazar", cada una con ventaja, impacto y fuente de financiación.
- [ ] Nivel de autoridad verificado contra umbral y presupuesto de cambio.
- [ ] Disposición, decisor y fecha registrados; `cambios.csv`, `issues.csv` y `decisiones.csv` actualizados.
- [ ] Si se aprobó: líneas base versionadas, descripción de producto y plan actualizados, riesgos nuevos consultados.
- [ ] Si se difirió: fecha o evento de reevaluación.
- [ ] Cifras sin fuente marcadas `[por confirmar]`.
