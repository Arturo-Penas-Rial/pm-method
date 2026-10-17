---
tipo: analisis-variaciones
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Análisis de variaciones · Variance analysis report

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}} · **Período / Period:** {{periodo_desde}} – {{periodo_hasta}}

**Nivel de análisis / Level of analysis:** {{nivel}}
*Proyecto, etapa, cuenta de control, paquete de trabajo o producto. En proyectos pequeños, este análisis es una tabla de tres filas dentro del highlight.*

**Elaborado por / Prepared by:** {{autor_informe}} · **Para / For:** {{destinatario}}

**Convención de signos / Sign convention:** para tiempo y costo, positivo = peor (más plazo, más gasto); para avance físico, negativo = peor.
*Declararla siempre; evita lecturas opuestas entre informes.*

**Umbrales / Thresholds:** atención {{umbral_atencion}} % · escalamiento {{umbral_escalamiento}} %
*Tomados del PID o del plan de etapa. Si no existen: 5 % y 10 % como valores de referencia, declarados como tales. Las tolerancias de PRINCE2 cumplen la misma función; fijarlas una sola vez.*

**Fuentes / Sources:** {{fuentes}}
*Plan de etapa, checkpoints, `progreso.csv` y `evm.py`, `calidad.csv`, `issues.csv`.*

## 1. Variación de cronograma / Schedule variance

| Campo / Field | Valor / Value |
|---|---|
| Resultado planificado / Planned result | {{sch_plan}} |
| Resultado real / Actual result | {{sch_real}} |
| Variación absoluta / Absolute variance | {{sch_var_abs}} |
| Variación relativa / Relative variance | {{sch_var_pct}} % |
| Afecta ruta crítica / Affects critical path | {{sch_ruta_critica}} |
| Causa raíz / Root cause | {{sch_causa}} |
| Respuesta planificada (acción, responsable, fecha) / Planned response | {{sch_respuesta}} |
| Implicación si continúa / Implication if it continues | {{sch_implicacion}} |
| Comparación con umbral / Threshold check | {{sch_umbral}} |
| Requiere escalamiento / Escalate | {{sch_escalar}} |

*Ejemplo de planificado/real: productos completados a la fecha de corte; hitos alcanzados; SV y SPI si hay EVM. `si`, `no`, `no-evaluado` para ruta crítica. Umbral: `dentro-atencion`, `atencion`, `escalamiento`.*

## 2. Variación de costo / Cost variance

| Campo / Field | Valor / Value |
|---|---|
| Resultado planificado / Planned result | {{cost_plan}} |
| Resultado real / Actual result | {{cost_real}} |
| Variación absoluta / Absolute variance | {{cost_var_abs}} {{moneda}} |
| Variación relativa / Relative variance | {{cost_var_pct}} % |
| Causa raíz (mano de obra, materiales, base de estimación, supuestos) / Root cause | {{cost_causa}} |
| Impacto en contingencia y reservas / Impact on contingency and reserves | {{cost_reservas}} |
| Respuesta planificada / Planned response | {{cost_respuesta}} |
| Implicación si continúa (EAC) / Implication if it continues | {{cost_implicacion}} |
| Comparación con umbral / Threshold check | {{cost_umbral}} |
| Requiere escalamiento / Escalate | {{cost_escalar}} |

## 3. Variación técnica (alcance y calidad) / Technical variance (scope and quality)

| Campo / Field | Alcance / Scope | Calidad / Quality |
|---|---|---|
| Resultado planificado / Planned result | {{sc_plan}} | {{q_plan}} |
| Resultado real / Actual result | {{sc_real}} | {{q_real}} |
| Variación / Variance | {{sc_var}} | {{q_var}} |
| Causa raíz / Root cause | {{sc_causa}} | {{q_causa}} |
| Respuesta planificada / Planned response | {{sc_respuesta}} | {{q_respuesta}} |
| Implicación si continúa / Implication if it continues | {{sc_implicacion}} | {{q_implicacion}} |
| Comparación con umbral / Threshold check | {{sc_umbral}} | {{q_umbral}} |
| Requiere escalamiento / Escalate | {{sc_escalar}} | {{q_escalar}} |

*Alcance: productos previstos vs. entregados, cambios aprobados; calidad: criterios incumplidos, pruebas fallidas sin retestear, fuera de especificación (`I-###`).*

## 4. Otros objetivos / Other objectives

| Objetivo / Objective | Plan | Real / Actual | Variación / Variance | Causa / Cause | Respuesta / Response | Umbral / Threshold |
|---|---|---|---|---|---|---|
| Beneficios / Benefits | {{ben_plan}} | {{ben_real}} | {{ben_var}} | {{ben_causa}} | {{ben_resp}} | {{ben_umbral}} |
| Sostenibilidad / Sustainability | {{sost_plan}} | {{sost_real}} | {{sost_var}} | {{sost_causa}} | {{sost_resp}} | {{sost_umbral}} |
| Riesgo (exposición) / Risk exposure | {{rie_plan}} | {{rie_real}} | {{rie_var}} | {{rie_causa}} | {{rie_resp}} | {{rie_umbral}} |

*Incluir aunque la variación sea cero; el método pronostica contra los siete objetivos.*

## 5. Tendencia / Trend

| Período / Period | Var. cronograma % | Var. costo % | Var. técnica | Comentario / Comment |
|---|---|---|---|---|
| {{per_1}} | {{t_sch_1}} | {{t_cost_1}} | {{t_tec_1}} | {{t_com_1}} |
| {{per_2}} | {{t_sch_2}} | {{t_cost_2}} | {{t_tec_2}} | {{t_com_2}} |
| {{per_actual}} | {{t_sch_a}} | {{t_cost_a}} | {{t_tec_a}} | {{t_com_a}} |

*Tres últimos períodos como mínimo; una variación que crece es más grave que una grande pero estable.*

## 6. Conclusión y escalamiento / Conclusion and escalation
{{conclusion}}
*Qué variaciones superan el umbral de escalamiento o pronostican salir de tolerancia; si alguna lo hace, se prepara el informe de excepción (`X-###`) con la plantilla de `pm-issues-cambios`, se entrega a `pm-director` y se indica aquí.*

**Acciones registradas / Actions recorded:** {{acciones_ids}}
*Ids de acciones (`A-###` en acciones.csv), issues (`I-###`), paquetes de trabajo o decisiones (`D-###`).*

## Lista de verificación / Checklist
- [ ] Tres dimensiones cubiertas (cronograma, costo, técnica) más beneficios, sostenibilidad y riesgo aunque la variación sea cero.
- [ ] Variación en absoluto y relativo; convención de signos declarada.
- [ ] Causa raíz como origen, no síntoma.
- [ ] Respuesta concreta con responsable y fecha.
- [ ] Comparación con umbrales del plan (o de referencia, declarados) y marca de escalamiento.
- [ ] Implicación si continúa, con pronóstico.
- [ ] Cifras coherentes con `evm.py` y con el highlight del mismo período.
- [ ] Variaciones fuera de tolerancia derivadas a informe de excepción.
