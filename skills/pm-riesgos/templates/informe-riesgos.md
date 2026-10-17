---
tipo: informe-riesgos
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Informe de riesgos · Risk report

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}}
*Nombre y etapa según `estado.json.etapa_actual`.*

**Período / Period:** {{periodo_desde}} – {{periodo_hasta}}
*Mismo período que el highlight report al que acompaña.*

**Elaborado por / Prepared by:** {{gestor}} · **Revisado por / Reviewed by:** {{aseguramiento}}
*Gestor del proyecto redacta; aseguramiento confirma; la junta recibe.*

**Audiencia / Audience:** {{audiencia}}
*`junta`, `equipo` o `cliente`; el contenido se ajusta: la junta quiere exposición, escalados y presupuesto; el equipo acciones y disparadores; el cliente los riesgos que lo afectan.*

**Fuente de datos / Data source:** `03-control/registros/riesgos.csv` al {{fecha_corte}}; escala y umbrales de `{{ruta_evaluacion_pi}}`.
*Toda cifra de este informe debe poder reconstruirse desde el CSV.*

## 1. Resumen ejecutivo / Executive summary
{{resumen_ejecutivo}}
*Un párrafo: exposición global y tendencia, riesgos individuales principales, respuestas en curso, decisiones que se piden a la junta.*

## 2. Estado y tendencia del riesgo global / Overall risk status and trend

| Indicador / Indicator | Período anterior / Previous | Este período / Current | Tolerancia / Tolerance | Semáforo / RAG |
|---|---|---|---|---|
| Exposición agregada (suma de puntuaciones abiertas) | {{exp_prev}} | {{exp_actual}} | {{tolerancia_riesgo}} | {{rag_exposicion}} |
| Riesgos altos abiertos (P×I ≥ 15; `altos_abiertos`) | {{rojos_prev}} | {{rojos_actual}} | {{tol_rojos}} | {{rag_rojos}} |
| Altos sin respuesta / sin propietario (`sin_respuesta`, `sin_propietario`) | {{sin_resp_prev}} | {{sin_resp_actual}} | 0 | {{rag_sin_resp}} |
| Σ EMV amenazas − Σ EMV oportunidades | {{emv_prev}} | {{emv_actual}} | {{tol_emv}} | {{rag_emv}} |
| Riesgos sobre la línea de tolerancia sin decisión | {{sin_decision_prev}} | {{sin_decision_actual}} | 0 | {{rag_sin_decision}} |

*Tendencia = valor actual − anterior. Conteos de `registro.py resumen --json`; EMV de la columna `valor_esperado`. Umbrales: alto ≥ 15, medio 6–12, bajo ≤ 5. Un semáforo rojo en exposición, o un alto sin respuesta o propietario, equivale a pronóstico de excepción en la dimensión riesgo.*

**Impulsores principales / Main drivers:** {{impulsores}}
*Fuentes que explican la mayor parte de la exposición (proveedores, tecnología, regulación, recursos).*

**Respuestas al riesgo global / Overall risk responses:** {{respuestas_globales}}
*Acciones a nivel de proyecto (replanificar, cambiar alcance, reforzar aseguramiento) y quién las decide.*

## 3. Matriz del período / Period matrix

| P \ I | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | {{m_5_1}} | {{m_5_2}} | {{m_5_3}} | {{m_5_4}} | {{m_5_5}} |
| **4** | {{m_4_1}} | {{m_4_2}} | {{m_4_3}} | {{m_4_4}} | {{m_4_5}} |
| **3** | {{m_3_1}} | {{m_3_2}} | {{m_3_3}} | {{m_3_4}} | {{m_3_5}} |
| **2** | {{m_2_1}} | {{m_2_2}} | {{m_2_3}} | {{m_2_4}} | {{m_2_5}} |
| **1** | {{m_1_1}} | {{m_1_2}} | {{m_1_3}} | {{m_1_4}} | {{m_1_5}} |

*Ids de riesgos abiertos por celda (oportunidades con `+`). Línea de tolerancia: puntuación ≥ {{linea_tolerancia}}.*

**Movimientos respecto del período anterior / Movements since last period:** {{movimientos}}
*Riesgos que subieron o bajaron de celda, con id y motivo.*

## 4. Métricas / Metrics

| Métrica / Metric | Valor / Value |
|---|---|
| Riesgos abiertos (amenazas / oportunidades) | {{abiertos}} ({{amenazas}} / {{oportunidades}}) |
| Nuevos en el período | {{nuevos}} |
| Cerrados o retirados en el período | {{cerrados}} |
| Ocurridos en el período (→ issues) | {{ocurridos}} |
| Escalados a la junta | {{escalados}} |
| Por calificación alto / medio / bajo | {{n_alto}} / {{n_medio}} / {{n_bajo}} |
| Por objetivo principal afectado | {{por_objetivo}} |
| Acciones de respuesta vencidas | {{acciones_vencidas}} |
| Riesgos sin revisar desde el período anterior | {{sin_revisar}} |
| Tasa de cierre (cerrados / abiertos al inicio) | {{tasa_cierre}} |

*Los conteos deben coincidir con `registro.py resumen` y `registro.py listar riesgos`.*

## 5. Riesgos principales y respuestas / Top risks and responses

| Id | Enunciado / Statement | P×I | EMV | Residual P×I / Residual | Disparador / Trigger | Proximidad / Proximity | Estrategia / Strategy | Propietario / Owner | Próxima acción y fecha / Next action and due | Estado / Status |
|---|---|---|---|---|---|---|---|---|---|---|
| {{top1_id}} | {{top1_enunciado}} | {{top1_pi}} | {{top1_emv}} | {{top1_residual}} | {{top1_disparador}} | {{top1_prox}} | {{top1_estrategia}} | {{top1_prop}} | {{top1_accion}} | {{top1_estado}} |
| {{top2_id}} | {{top2_enunciado}} | {{top2_pi}} | {{top2_emv}} | {{top2_residual}} | {{top2_disparador}} | {{top2_prox}} | {{top2_estrategia}} | {{top2_prop}} | {{top2_accion}} | {{top2_estado}} |
| {{top3_id}} | {{top3_enunciado}} | {{top3_pi}} | {{top3_emv}} | {{top3_residual}} | {{top3_disparador}} | {{top3_prox}} | {{top3_estrategia}} | {{top3_prop}} | {{top3_accion}} | {{top3_estado}} |

*Entre tres y cinco; incluir al menos una oportunidad si existe. Para los que tienen hoja de datos, enlazar `03-control/registros/R-###-hoja-riesgo.md`. Las acciones con fecha llevan su id `A-###`.*

**Cambios en los riesgos principales / Changes to top risks:** {{cambios_top}}
*Entradas, salidas y re-puntuaciones de la lista desde el informe anterior.*

## 6. Presupuesto de riesgo / Risk budget

| Concepto / Item | Monto / Amount ({{moneda}}) |
|---|---|
| Presupuesto de riesgo de la etapa | {{pr_total}} |
| Comprometido en respuestas planificadas | {{pr_comprometido}} |
| Usado en el período | {{pr_usado_periodo}} |
| Usado acumulado | {{pr_usado_acum}} |
| Remanente | {{pr_remanente}} |
| Σ EMV de riesgos aceptados abiertos | {{emv_aceptados}} |
| Cobertura (remanente / Σ EMV aceptados) | {{cobertura}} |

**Reserva de tiempo / Schedule reserve:** total {{rt_total}} d · usada {{rt_usada}} d · remanente {{rt_remanente}} d
*Las cifras deben coincidir con el highlight report y el análisis de valor ganado.*

**Suficiencia / Adequacy:** {{suficiencia}}
*Argumentar con números si el remanente cubre la exposición pendiente; cobertura < 1 se informa como alerta.*

## 7. Análisis cuantitativo / Quantitative analysis
{{analisis_cuantitativo}}
*Solo si se hizo (Monte Carlo, árbol de decisión): probabilidad de cumplir fecha y costo, percentiles P50/P80, impulsores. Si no hubo análisis cuantitativo, eliminar esta sección en lugar de dejarla vacía.*

## 8. Escalados y decisiones solicitadas / Escalations and decisions requested

| Id | Motivo de escalado / Reason | Opciones / Options | Recomendación / Recommendation | Decide / Decided by |
|---|---|---|---|---|
| {{esc_id}} | {{esc_motivo}} | {{esc_opciones}} | {{esc_recomendacion}} | {{esc_decide}} |

*Riesgos sobre la línea de tolerancia, riesgos al caso de negocio, riesgos de programa, respuestas que romperían tolerancias, uso del presupuesto de riesgo fuera de autoridad. Si la exposición pronostica superar la tolerancia de etapa, indicar que se emite informe de excepción.*

## 9. Auditoría y lecciones / Audit and lessons
{{auditoria_lecciones}}
*Resumen de la última auditoría de riesgos si la hubo y lecciones registradas (L-###) en el período.*

## 10. Señales de sesgo revisadas / Bias checks
{{senales_sesgo}}
*Indicar explícitamente si se observó: todos los riesgos bajos, ninguna oportunidad, ningún escalado en varios períodos, un único propietario mayoritario; y la contramedida propuesta.*

## Lista de verificación / Checklist
- [ ] Conteos y matriz coinciden con `riesgos.csv` a la fecha de corte.
- [ ] Exposición comparada con `tolerancias.riesgo` y tendencia respecto del informe anterior.
- [ ] Riesgos principales con estrategia, propietario y próxima acción con fecha.
- [ ] Todo riesgo sobre la línea de tolerancia aparece en escalados o tiene decisión registrada (D-###).
- [ ] Presupuesto de riesgo y reservas coherentes con highlight report y EVM.
- [ ] Sección cuantitativa presente solo si hubo análisis.
- [ ] Oportunidades incluidas; señales de sesgo revisadas.
- [ ] Umbrales y línea de tolerancia declarados como valores configurables.
- [ ] Cifras sin fuente marcadas `[por confirmar]`; informe marcado como borrador hasta la revisión de aseguramiento.
