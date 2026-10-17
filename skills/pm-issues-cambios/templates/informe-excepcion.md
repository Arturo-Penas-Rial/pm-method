---
tipo: informe-excepcion
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Informe de excepción · Exception report

**Identificador / Exception id:** {{id_excepcion}}
*`X-###` correlativo (id del documento, no de un registro); clave `informe-excepcion-X-###` en estado.json; se referencia desde `issues.csv.notas` y `decisiones.csv`. Plantilla única del paquete: la usan pm-issues-cambios y pm-progreso-reportes (cuando `evm.py` marca `excepcion_prevista`).*

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}}

**Fecha de emisión / Date issued:** {{fecha_emision}} · **Aviso temprano dado el / Early warning given on:** {{fecha_aviso}} a {{aviso_a}}
*El método recomienda avisar a la junta en cuanto existe el pronóstico (verbal o mensaje breve) y formalizar después por escrito.*

**Emitido por / Issued by:** {{gestor}} · **Para / To:** {{destinatario}}
*Gestor del proyecto → junta del proyecto (o ejecutivo). Si se pronostica superar tolerancias de proyecto, la junta debe referir a la capa de negocio.*

**Issue de origen / Source issue(s):** {{ids_issues}} · **Informe de issue / Issue report:** {{ruta_informe_issue}}

**Nivel de tolerancia afectado / Tolerance level affected:** {{nivel_tolerancia}}
*`etapa` o `proyecto`. Determina quién tiene autoridad para decidir.*

## 1. Descripción de la excepción / Description
{{descripcion}}
*Qué se pronostica y por qué constituye excepción: desviación prevista más allá de la tolerancia acordada. Se emite al pronosticar, no al constatar.*

## 2. Causa / Cause
{{causa}}
*Qué provocó la desviación respecto del plan vigente (causa raíz, no síntoma); ids de issues y riesgos relacionados.*

## 3. Desviación pronosticada por objetivo / Forecast deviation by objective

| Objetivo / Objective | Plan vigente / Current plan | Tolerancia / Tolerance | Pronóstico / Forecast | Desviación / Deviation | Fuente / Source |
|---|---|---|---|---|---|
| Tiempo / Time | {{plan_tiempo}} | {{tol_tiempo}} | {{pron_tiempo}} | {{desv_tiempo}} | {{fuente_tiempo}} |
| Costo / Cost | {{plan_costo}} | {{tol_costo}} | {{pron_costo}} | {{desv_costo}} | {{fuente_costo}} |
| Alcance / Scope | {{plan_alcance}} | {{tol_alcance}} | {{pron_alcance}} | {{desv_alcance}} | {{fuente_alcance}} |
| Calidad / Quality | {{plan_calidad}} | {{tol_calidad}} | {{pron_calidad}} | {{desv_calidad}} | {{fuente_calidad}} |
| Beneficios / Benefits | {{plan_beneficios}} | {{tol_beneficios}} | {{pron_beneficios}} | {{desv_beneficios}} | {{fuente_beneficios}} |
| Sostenibilidad / Sustainability | {{plan_sostenibilidad}} | {{tol_sostenibilidad}} | {{pron_sostenibilidad}} | {{desv_sostenibilidad}} | {{fuente_sostenibilidad}} |
| Riesgo / Risk | {{plan_riesgo}} | {{tol_riesgo}} | {{pron_riesgo}} | {{desv_riesgo}} | {{fuente_riesgo}} |

*En unidades del objetivo (días, moneda, productos, métrica). Fuente: EVM (`evm.py`), plan de etapa, `riesgos.csv`, checkpoint. Marcar las filas sin impacto como "dentro de tolerancia".*

**Productos inacabados y qué pasaría si se continúa sin decisión / Unfinished products and consequence of continuing:** {{productos_inacabados}}

## 4. Consecuencias / Consequences

**Para el proyecto / For the project:** {{consecuencias_proyecto}}
*Efecto sobre el plan de etapa, el plan de proyecto y el perfil de riesgo si no se actúa.*

**Para la organización / For the organization:** {{consecuencias_organizacion}}
*Efecto sobre el caso de negocio, los beneficios, otros proyectos o programas, obligaciones contractuales o regulatorias.*

**Viabilidad del caso de negocio / Business case viability:** {{viabilidad}}

## 5. Opciones / Options

| Opción / Option | Descripción / Description | Efecto sobre el caso de negocio / Business case effect | Efecto sobre riesgos / Risk effect | Efecto sobre tolerancias / Tolerance effect | ¿Requiere plan de excepción? / Exception plan needed? | Decide / Authority |
|---|---|---|---|---|---|---|
| 1 | {{op1_desc}} | {{op1_bc}} | {{op1_riesgo}} | {{op1_tol}} | {{op1_plan}} | {{op1_decide}} |
| 2 | {{op2_desc}} | {{op2_bc}} | {{op2_riesgo}} | {{op2_tol}} | {{op2_plan}} | {{op2_decide}} |
| 3 | {{op3_desc}} | {{op3_bc}} | {{op3_riesgo}} | {{op3_tol}} | {{op3_plan}} | {{op3_decide}} |

*Opciones típicas de la junta: (a) reasignar tolerancias del proyecto para absorber la desviación de etapa; (b) repriorizar o reducir alcance para volver a tolerancia; (c) pedir más tiempo para decidir; (d) pedir un plan de excepción; (e) si excede tolerancias de proyecto, escalar a la capa de negocio (que puede ajustar tolerancias, pedir plan de excepción de proyecto o cerrar prematuramente). Incluir, cuando sea viable, al menos una opción que no requiera plan de excepción. Cuantificar cada opción en las unidades de los objetivos afectados.*

## 6. Recomendación / Recommendation

**Opción recomendada / Recommended option:** {{recomendacion}}

**Razones / Rationale:** {{razones}}
*Priorizando la justificación de negocio; indicar qué deja de ser posible con cada opción descartada.*

**Si se pide plan de excepción / If an exception plan is requested:** {{plan_excepcion_nota}}
*La etapa actual se detiene (`estado.py limite-etapa --excepcion X-###`), se elabora el plan de excepción en `02-planificacion/plan-excepcion-X-###.md` (y la PID se ajusta); conviene alinear el nuevo fin de etapa con el original. Deriva a `pm-plan-etapa-y-limites`; la puerta `autorizar-plan-excepcion` la registra `pm-director`.*

## 7. Lecciones / Lessons
{{lecciones}}
*Qué se aprende de esta excepción para este u otros proyectos: ¿qué esperábamos? ¿qué ocurrió? ¿qué funcionó? ¿qué no? ¿qué cambiar? Registrar `L-###`.*

## 8. Decisión de la junta / Board decision

**Decisión / Decision:** {{decision_junta}}
*Vacía hasta el acto humano. Opciones: reasignar tolerancias, repriorizar alcance, esperar, pedir plan de excepción, referir a la capa de negocio.*

**Decidido por / Decided by:** {{decidido_por}} · **Fecha / Date:** {{fecha_decision}} · **Registro / Decision log:** {{id_decision}} · **Puerta / Gate:** {{puerta}}
*Lo completa `pm-director` al registrar la puerta `decision-ad-hoc` con `estado.py puerta` (escribe la fila `D-###` en `decisiones.csv`, nivel `junta`; `capa-negocio` si la refiere); luego `autorizar-plan-excepcion` cuando se apruebe el plan. Quien prepara este informe no registra ninguna puerta.*

**Tolerancias ajustadas / Adjusted tolerances:** {{tolerancias_ajustadas}}
*Si la junta reasigna tolerancias, actualizar con `estado.py tolerancia --nivel etapa|proyecto dimension=valor`.*

**Acciones derivadas / Resulting actions:** {{acciones}}
*Paquetes de trabajo a enmendar o autorizar; registros a actualizar; comunicación a stakeholders; cada una con id `A-###` en acciones.csv.*

## Lista de verificación / Checklist
- [ ] Emitido al pronosticar, con aviso temprano previo registrado.
- [ ] Nivel de tolerancia afectado (etapa o proyecto) y autoridad decisora identificados.
- [ ] Causa raíz, no síntoma; issues y riesgos de origen enlazados.
- [ ] Desviación cuantificada por objetivo con fuente de cada cifra (EVM, plan, registros).
- [ ] Consecuencias para el proyecto y para la organización, con juicio sobre el caso de negocio.
- [ ] Al menos una opción sin plan de excepción (si es viable) y una con; cada opción con efecto sobre caso de negocio, riesgos y tolerancias, y quién la decide.
- [ ] Recomendación razonada y lección registrada.
- [ ] Decisión, decisor, fecha, `D-###` y puerta registrados; tolerancias actualizadas si corresponde.
- [ ] Cifras sin fuente marcadas `[por confirmar]`; documento en `borrador` hasta la decisión.
