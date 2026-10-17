---
tipo: informe-avance-equipo
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Informe de avance de miembro de equipo · Team member progress report

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}}

**Miembro del equipo / Team member:** {{miembro}} · **Rol / Role:** {{rol}}
*Quien informa; va dirigido al gestor de equipo o directamente al gestor del proyecto si no hay gestor de equipo.*

**Paquete de trabajo / Work package:** {{paquete_trabajo}}
*Id y nombre del paquete al que pertenece el trabajo informado.*

**Período / Period:** {{periodo_desde}} – {{periodo_hasta}} · **Fecha de corte / Cut-off date:** {{fecha_corte}}
*Cadencia fijada en la descripción del paquete de trabajo (por defecto semanal).*

## 1. Seguimientos del informe anterior / Follow-ups from previous report
{{seguimientos}}
*Pendientes del informe anterior: completados o aún abiertos, con fecha.*

## 2. Este período / This period

| Actividad o producto planificado / Planned activity or product | Logrado / Accomplished | Causa raíz si no se logró / Root cause if not |
|---|---|---|
| {{plan_1}} | {{logrado_1}} | {{causa_1}} |
| {{plan_2}} | {{logrado_2}} | {{causa_2}} |
| {{plan_3}} | {{logrado_3}} | {{causa_3}} |

*La columna "planificado" debe coincidir con lo previsto en el informe anterior. `si`, `parcial`, `no`. La causa es un origen, no un síntoma.*

**Variación de actividades / Activity variance:** ({{planificadas}} − {{logradas}}) / {{planificadas}} × 100 = {{variacion_actividades}} %

**Actividades de calidad realizadas / Quality activities done:** {{calidad_realizada}}
*Revisiones, pruebas, aprobaciones obtenidas; ids `Q-###` de `calidad.csv`.*

## 3. Esfuerzo y costo / Effort and cost

| Concepto / Item | Planificado / Planned | Real / Actual | Variación / Variance |
|---|---|---|---|
| Horas / Hours | {{horas_plan}} | {{horas_real}} | {{horas_var}} |
| Costo / Cost ({{moneda}}) | {{costo_plan}} | {{costo_real}} | {{costo_var}} |

**Causa raíz de la variación de costo / Root cause of cost variance:** {{causa_costo}}
*Distinguir mano de obra de materiales; si falló la base de estimación o un supuesto.*

*Comparar con lo planificado del período, no con el acumulado. Positivo = sobrecosto.*

## 4. Variaciones de calidad / Quality variances
{{variaciones_calidad}}
*Desviaciones de desempeño o de criterios de aceptación detectadas; si un producto no cumplirá su especificación, es un fuera de especificación → issue.*

## 5. Acción correctiva o preventiva / Corrective or preventive action
{{accion_correctiva}}
*Cómo se recupera o se evita la desviación; responsable y fecha.*

## 6. Próximo período / Next period

| Actividad o producto / Activity or product | Fecha prevista / Due |
|---|---|
| {{prox_1}} | {{prox_fecha_1}} |
| {{prox_2}} | {{prox_fecha_2}} |

**Costo previsto / Planned cost:** {{costo_proximo}} {{moneda}}

## 7. Riesgos, issues y lecciones nuevos / New risks, issues and lessons

| Tipo / Type | Descripción / Description | Id asignado / Register id |
|---|---|---|
| riesgo / risk | {{riesgo_nuevo}} | {{riesgo_id}} |
| issue | {{issue_nuevo}} | {{issue_id}} |
| lección / lesson | {{leccion_nueva}} | {{leccion_id}} |

*Se cargan en los registros antes de emitir el informe; si el id está vacío, el gestor de equipo lo crea.*

## 8. Escalamientos y decisiones / Escalations and decisions
**Necesito que se decida o desbloquee / I need a decision or unblock on:** {{escalamientos}}
*Lo que supera la autoridad de quien informa.*

**Decisiones tomadas / Decisions made:** {{decisiones}}
*Con id `D-###` si son formales.*

**Comentarios / Comments:** {{comentarios}}

## Lista de verificación / Checklist
- [ ] Lo planificado coincide con lo previsto en el informe anterior.
- [ ] Toda actividad no lograda tiene causa raíz.
- [ ] Horas y costo comparados con el plan del período.
- [ ] Riesgos, issues y lecciones nuevos cargados en los registros con id.
- [ ] Acción correctiva para cada variación significativa, con responsable y fecha.
- [ ] Entregado en la fecha de corte.
