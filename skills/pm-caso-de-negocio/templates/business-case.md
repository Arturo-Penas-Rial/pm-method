---
tipo: business-case
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Caso de negocio · Business case — {{proyecto}}

> Producto de línea base que justifica la inversión y se mantiene vivo: esquemático en el arranque, completo en el inicio, actualizado en cada fin de etapa y confirmado al cierre. / Baseline product kept alive from outline to closure.

**Modo / Mode:** {{modo}} · **Versión que sustituye / Replaces version:** {{version_anterior}}
*`esquematico` (solo secciones marcadas ◇), `completo`, `verificado`, `mantenido`, `confirmado`. La versión anterior se guarda intacta en `00-direccion/historial/`.*

**Rinde cuentas / Accountable:** {{ejecutivo}} (ejecutivo) · **Beneficios / Benefits owner:** {{usuario_senior}} (usuario sénior) · **Costos y viabilidad / Costs and viability:** {{proveedor_senior}} (proveedor sénior) · **Elabora / Drafted by:** {{gestor}} (gestor)
*Quién responde por qué parte del caso. El ejecutivo nunca delega su rendición de cuentas.*

> **Versión de una página / One-page version (perfil ágil mínimo / minimal agile profile):** {{una_pagina}}
> *`sí`: completar solo este bloque y la sección 1; las secciones 3–13 se reemplazan por él y se marcan "no aplica (perfil ágil mínimo)". Se amplía a versión completa si el costo supera el umbral de la organización o la junta lo pide.*
>
> | Campo / Field | Contenido / Content |
> |---|---|
> | Problema y objetivo de negocio / Problem and business objective | {{p1_problema}} |
> | Opción elegida frente a "no hacer nada distinto" / Chosen option vs. do nothing | {{p1_opcion}} |
> | Beneficios como rango ligado al alcance entregado (solo Must / Must+Should) / Benefits as a range tied to delivered scope | {{p1_beneficios}} |
> | Costo fijo: iteraciones × costo por iteración + otros / Fixed cost: iterations × cost per iteration + other | {{p1_costo}} |
> | Retorno simple o payback, con supuestos / Simple return or payback, with assumptions | {{p1_retorno}} |
> | Tres riesgos principales (ids de `riesgos.csv`) / Top three risks | {{p1_riesgos}} |
> | Tolerancias: tiempo, costo, alcance en MoSCoW, beneficios / Tolerances | {{p1_tolerancias}} |
> | Dueño de beneficios (usuario sénior / product owner) y fecha de primera medición / Benefits owner and first measurement | {{p1_dueno}} |

## 1. Resumen ejecutivo ◇ / Executive summary

{{resumen_ejecutivo}}
*Se escribe al final: puntos clave, beneficios principales, retorno, opción recomendada y veredicto deseable / viable / alcanzable. Debe coincidir con las cifras del cuerpo.*

## 2. Razones ◇ / Reasons

**Problema u oportunidad / Problem or opportunity:** {{razones}}
*Por qué se emprende el proyecto, con el dato que lo evidencia y su fuente.*

**Objetivos de negocio a los que contribuye / Business objectives supported:** {{objetivos_negocio}}
*Nombrar el objetivo estratégico o compromiso ESG concreto; la contribución debe ser verificable.*

**Lecciones previas consideradas / Previous lessons considered:** {{lecciones}}
*Identificadores de `lecciones.csv` que cambiaron el enfoque o las cifras.*

## 3. Cadena de valor / Value chain

| Salida (producto) / Output | Capacidad / Capability | Resultado / Outcome | Beneficio o des-beneficio / Benefit or dis-benefit | Objetivo de negocio / Business objective | Habilitador / Enabler |
|---|---|---|---|---|---|
| {{salida_1}} | {{capacidad_1}} | {{resultado_1}} | {{beneficio_1}} | {{objetivo_1}} | {{habilitador_1}} |
| {{salida_2}} | {{capacidad_2}} | {{resultado_2}} | {{beneficio_2}} | {{objetivo_2}} | {{habilitador_2}} |

*Una salida sola rara vez basta: anotar qué conjunto de salidas forma cada capacidad. Marcar `sí` en habilitador cuando el producto no genera beneficio por sí mismo pero otros dependen de él.*

## 4. Opciones de negocio ◇ / Business options

| Opción / Option | Descripción / Description | Ventajas / Advantages | Desventajas, costos y límites / Disadvantages, costs and limits | Riesgos / Risks | Deseable · Viable · Alcanzable |
|---|---|---|---|---|---|
| 0. No hacer nada distinto / Do nothing different | {{op0_desc}} | {{op0_ventajas}} | {{op0_desventajas}} | {{op0_riesgos}} | {{op0_dva}} |
| 1. Hacer lo mínimo / Do the minimum | {{op1_desc}} | {{op1_ventajas}} | {{op1_desventajas}} | {{op1_riesgos}} | {{op1_dva}} |
| 2. Hacer más que lo mínimo / Do more | {{op2_desc}} | {{op2_ventajas}} | {{op2_desventajas}} | {{op2_riesgos}} | {{op2_dva}} |

**Opción recomendada y razones / Recommended option and reasons:** {{opcion_recomendada}}
*En términos de valor por dinero y alineación con la misión. La opción 0 es siempre la base de comparación, también en proyectos obligatorios.*

**Supuestos de las opciones / Option assumptions:** {{supuestos_opciones}}
*Todo lo que se dio por cierto al comparar; registrar en `supuestos.csv`.*

## 5. Beneficios y des-beneficios esperados ◇ / Expected benefits and dis-benefits

| Id | Beneficio o des-beneficio / Benefit or dis-benefit | Medida / Measure | Línea base / Baseline | Meta / Target | Fecha de realización / Realisation date | Dueño / Owner | Tolerancia / Tolerance | Fuente / Source | Refs SM / KR |
|---|---|---|---|---|---|---|---|---|---|
| B-01 | {{b1_nombre}} | {{b1_medida}} | {{b1_base}} | {{b1_meta}} | {{b1_fecha}} | {{b1_dueno}} | {{b1_tolerancia}} | {{b1_fuente}} | {{b1_refs}} |
| B-02 | {{b2_nombre}} | {{b2_medida}} | {{b2_base}} | {{b2_meta}} | {{b2_fecha}} | {{b2_dueno}} | {{b2_tolerancia}} | {{b2_fuente}} | {{b2_refs}} |
| DB-01 | {{d1_nombre}} | {{d1_medida}} | {{d1_base}} | {{d1_meta}} | {{d1_fecha}} | {{d1_dueno}} | {{d1_tolerancia}} | {{d1_fuente}} | {{d1_refs}} |

*Ids: `B-##` beneficio, `DB-##` des-beneficio (no confundir con `D-###` del registro de decisiones). Todo beneficio medible contra la situación previa. Un des-beneficio es un deterioro esperado, no un riesgo. En modo esquemático basta la lista con medida aproximada. Columna Refs: ids de métricas de éxito del PRD BMAD (`SM-n`) y de resultados clave OKR (`KR-…` de `okr.csv`, `pm-okr`) que miden o comparten este beneficio; se citan, no se copian sus definiciones. La meta y la tolerancia del beneficio son del business case.*

**Escenarios (ágil / híbrido) / Scenarios (agile / hybrid):** {{escenarios}}
*Si el alcance es flexible: beneficios en peor caso (solo imprescindibles), esperado (imprescindibles + deseables) y mejor caso. El peor caso debe seguir siendo viable.*

## 6. Metas de sostenibilidad / Sustainability targets

| Meta / Target | Medida / Measure | Línea base / Baseline | Objetivo / Goal | Tolerancia / Tolerance | Compromiso corporativo / Corporate commitment | Responsable / Owner |
|---|---|---|---|---|---|---|
| {{s1_meta}} | {{s1_medida}} | {{s1_base}} | {{s1_objetivo}} | {{s1_tolerancia}} | {{s1_compromiso}} | {{s1_responsable}} |

*Trazables a los compromisos ESG o de sostenibilidad del negocio. Si no aplica, declarar "no aplica" y por qué. Detalle en `enfoque-sostenibilidad.md`.*

## 7. Tiempo / Timescale

**Duración del proyecto / Project duration:** {{duracion_proyecto}}
*Desde el plan de proyecto; en modo esquemático, ventana aproximada.*

**Período de realización de beneficios / Benefits realisation period:** {{periodo_beneficios}}
*Cuándo empiezan y hasta cuándo se miden; define el horizonte de la evaluación.*

## 8. Costos / Costs

| Concepto / Item | Importe / Amount | Período / Period | Fuente / Source | Confianza / Confidence |
|---|---|---|---|---|
| Costo del proyecto (productos + gestión) / Project cost | {{costo_proyecto}} | {{costo_proyecto_periodo}} | {{costo_proyecto_fuente}} | {{costo_proyecto_confianza}} |
| Costo de transición / Transition cost | {{costo_transicion}} | {{costo_transicion_periodo}} | {{costo_transicion_fuente}} | {{costo_transicion_confianza}} |
| Costo de operación y mantenimiento / Operation and maintenance | {{costo_operacion}} | {{costo_operacion_periodo}} | {{costo_operacion_fuente}} | {{costo_operacion_confianza}} |
| Presupuesto de riesgo y de cambio / Risk and change budget | {{presupuesto_riesgo_cambio}} | — | plan de proyecto | — |

**Financiación / Funding arrangements:** {{financiacion}}
*Origen de los fondos, calendario de liberación, condiciones. Lo confirma el ejecutivo.*

## 9. Evaluación de la inversión / Investment appraisal

**Técnica(s) elegida(s) y por qué / Technique(s) and rationale:** {{tecnica}}
*Beneficios netos y payback para casos simples; NPV/IRR con beneficios diferidos; ROI para comunicación ejecutiva; multi-caso cuando lo financiero no basta.*

**Supuestos / Assumptions:** horizonte {{horizonte}} · tasa de descuento {{tasa}} · moneda {{moneda}} · base de comparación {{base_comparacion}}
*Valores de la política de inversiones de la organización; si son de referencia, marcarlos `[por confirmar]`.*

**Fórmulas / Formulas:** NPV = Σ (CF_t / (1 + r)^t) para t = 0..n; payback = primer t en que Σ CF acumulado ≥ 0; ROI = (beneficios netos − inversión) / inversión.
*Escribir la fórmula aplicada y los flujos usados, para que otro pueda rehacer el cálculo.*

| Indicador / Indicator | Opción 0 | Opción 1 | Opción 2 |
|---|---|---|---|
| Beneficios netos / Net benefits | {{nb_0}} | {{nb_1}} | {{nb_2}} |
| Payback | {{pb_0}} | {{pb_1}} | {{pb_2}} |
| NPV | {{npv_0}} | {{npv_1}} | {{npv_2}} |
| ROI | {{roi_0}} | {{roi_1}} | {{roi_2}} |

**Sensibilidad / Sensitivity:** {{sensibilidad}}
*Qué beneficio o costo, al variar, hace que la inversión deje de justificarse; punto de quiebre. Obligatorio si un beneficio sostiene más de la mitad del valor.*

**Modelo multi-caso / Multi-case view:** estratégico {{caso_estrategico}} · económico {{caso_economico}} · financiero {{caso_financiero}} · implementación y comercial {{caso_implementacion}}
*Una línea por perspectiva. Una inversión robusta satisface las cuatro.*

## 10. Riesgos principales ◇ / Major risks

| Id (`riesgos.csv`) | Amenaza u oportunidad / Threat or opportunity | Impacto en la justificación / Impact on justification | Respuesta / Response | Dueño / Owner |
|---|---|---|---|---|
| {{r1_id}} | {{r1_desc}} | {{r1_impacto}} | {{r1_respuesta}} | {{r1_dueno}} |
| {{r2_id}} | {{r2_desc}} | {{r2_impacto}} | {{r2_respuesta}} | {{r2_dueno}} |

**Tolerancia de riesgo del proyecto / Project risk tolerance:** {{tolerancia_riesgo}}
*Nivel agregado de riesgo aceptable; por defecto del paquete: ningún riesgo alto (P×I ≥ 15) abierto sin respuesta y propietario, más un tope de valor esperado (EMV) agregado de las amenazas. Aquí se ancla y se copia con `estado.py tolerancia --nivel proyecto riesgo="..."`.*

## 11. Siete aspectos de desempeño / Seven performance aspects

| Aspecto / Aspect | Meta / Target | Tolerancia / Tolerance | ¿Cierra? / Within? |
|---|---|---|---|
| Beneficios / Benefits | {{pa_beneficios}} | {{pa_beneficios_tol}} | {{pa_beneficios_ok}} |
| Costo / Cost | {{pa_costo}} | {{pa_costo_tol}} | {{pa_costo_ok}} |
| Tiempo / Time | {{pa_tiempo}} | {{pa_tiempo_tol}} | {{pa_tiempo_ok}} |
| Calidad / Quality | {{pa_calidad}} | {{pa_calidad_tol}} | {{pa_calidad_ok}} |
| Alcance / Scope | {{pa_alcance}} | {{pa_alcance_tol}} | {{pa_alcance_ok}} |
| Riesgo / Risk | {{pa_riesgo}} | {{pa_riesgo_tol}} | {{pa_riesgo_ok}} |
| Sostenibilidad / Sustainability | {{pa_sostenibilidad}} | {{pa_sostenibilidad_tol}} | {{pa_sostenibilidad_ok}} |

*Si alguno no cierra, la justificación es cuestionable y el resumen ejecutivo lo dice.*

## 12. Verificación en puertas / Gate checks

| Fecha / Date | Puerta / Gate | Deseable / Desirable | Viable / Viable | Alcanzable / Achievable | Veredicto / Verdict | Decidido por / Decided by | Ref. `decisiones.csv` |
|---|---|---|---|---|---|---|---|
| {{v1_fecha}} | {{v1_puerta}} | {{v1_deseable}} | {{v1_viable}} | {{v1_alcanzable}} | {{v1_veredicto}} | {{v1_quien}} | {{v1_ref}} |

*Una fila por verificación: autorizar inicio, autorizar proyecto, fin de cada etapa, excepción, cierre. Veredicto: continuar / cambiar / detener.*

## 13. Actualización con datos reales / Update with actuals

{{actualizacion}}
*Solo en modos mantener y confirmar: productos entregados, costos reales, beneficios realizados, previsiones revisadas, diferencias contra la versión que autorizó el proyecto.*

## 14. Referencias / References

{{referencias}}
*Mandato, brief, plan de proyecto, enfoque de beneficios, enfoque de sostenibilidad, modelo financiero (anexo), política de inversiones.*

## Lista de verificación / Checklist
- [ ] Modo y versión declarados; versión anterior conservada en `historial/`.
- [ ] Cadena de valor completa con habilitadores y des-beneficios.
- [ ] Opción "no hacer nada distinto" presente y usada como base.
- [ ] Beneficios medibles con línea base, meta, fecha, dueño y tolerancia; fuente de cada cifra.
- [ ] Costos de proyecto, transición y operación; financiación confirmada o `[por confirmar]` por el ejecutivo.
- [ ] Técnica de evaluación justificada; supuestos y fórmulas escritos; sensibilidad cuando corresponde.
- [ ] Deseable / viable / alcanzable evaluados por separado.
- [ ] Siete aspectos dentro de tolerancia o cuestionamiento explícito.
- [ ] Metas de sostenibilidad con tolerancia y compromiso corporativo (o no aplicabilidad razonada).
- [ ] Riesgos principales enlazados a `riesgos.csv`; tolerancia de riesgo fijada.
- [ ] Resumen ejecutivo escrito al final y coherente con las tablas.
- [ ] Estado `borrador` o `en-revision` hasta la puerta; `aprobado_por` vacío hasta entonces.
