---
tipo: checkpoint-report
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Informe de punto de control · Checkpoint report

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}}

**Paquete de trabajo / Work package:** {{paquete_trabajo}}
*Id y nombre; la frecuencia de este informe la fija la descripción del paquete de trabajo.*

**Gestor de equipo / Team manager:** {{gestor_equipo}} · **Para / To:** {{gestor_proyecto}}

**Período / Period:** {{periodo_desde}} – {{periodo_hasta}} · **Fecha / Date:** {{fecha_corte}}

**Formato / Format:** {{formato}}
*Documento, correo, entrada en herramienta, tablero Kanban o reunión diaria en modo pull (ágil). El método no prescribe formato; sí contenido y frecuencia.*

## 1. Resumen del gestor de equipo / Team manager's summary
{{resumen}}
*Dos o tres frases: estado del paquete, principal desvío, principal bloqueo.*

**Semáforo del paquete / Work package RAG:** {{rag_paquete}}
*Justificado con el pronóstico contra las tolerancias del paquete (sección 5), no con percepción.*

## 2. Seguimientos / Follow-ups
{{seguimientos}}
*Pendientes de informes anteriores: completados o sin resolver.*

## 3. Este período / This period

**Productos completados / Products completed:** {{productos_completados}}
*Solo los que superaron sus actividades de calidad y tienen aprobación registrada (`Q-###`, registro de productos).*

**Productos en desarrollo / Products in progress:** {{productos_en_curso}}
*Con % de avance según el método de medición declarado (0/100, 50/50, hitos ponderados, % físico) o ítems terminados del timebox en ágil.*

**Productos planificados no iniciados / Planned products not started:** {{productos_no_iniciados}}
*Alerta temprana de desvío de tiempo.*

**Actividades de calidad realizadas / Quality activities done:** {{calidad_realizada}}

**Lecciones identificadas / Lessons identified:** {{lecciones}}

## 4. Próximo período / Next period

**Productos a completar / Products to complete:** {{prox_completar}}
**Productos a desarrollar / Products to develop:** {{prox_desarrollar}}
**Actividades de calidad previstas / Planned quality activities:** {{prox_calidad}}

## 5. Estado de tolerancias del paquete / Work package tolerance status

| Objetivo / Objective | Plan / Plan | Real a la fecha / Actual to date | Pronóstico al fin del paquete / Forecast at completion | Tolerancia / Tolerance | Dentro / Within |
|---|---|---|---|---|---|
| Tiempo / Time | {{t_plan}} | {{t_real}} | {{t_pron}} | {{t_tol}} | {{t_dentro}} |
| Costo o esfuerzo / Cost or effort | {{c_plan}} | {{c_real}} | {{c_pron}} | {{c_tol}} | {{c_dentro}} |
| Alcance / Scope | {{a_plan}} | {{a_real}} | {{a_pron}} | {{a_tol}} | {{a_dentro}} |
| Calidad / Quality | {{q_plan}} | {{q_real}} | {{q_pron}} | {{q_tol}} | {{q_dentro}} |
| Sostenibilidad / Sustainability | {{s_plan}} | {{s_real}} | {{s_pron}} | {{s_tol}} | {{s_dentro}} |

*Se compara el pronóstico, no el acumulado. `si` (≤ 50 % de la tolerancia consumida), `alerta` (50–100 %), `no` (fuera de tolerancia); misma regla que `evm.py --tol-*`. Si alguna fila es `no`, ya debe existir un issue planteado al gestor del proyecto (sección 6); el gestor de equipo no decide fuera de su tolerancia.*

**Burn-down del timebox (ágil) / Timebox burn-down (agile):** {{burndown}}
*Ítems o puntos comprometidos, terminados, restantes y pronóstico de cierre; en modo pull basta enlazar el tablero.*

**Burn-up del paquete o release (ágil/híbrido) / Package or release burn-up:**

| Iteración / Iteration | Alcance total (pts) / Total scope | Terminado acumulado (pts) / Done to date | Velocidad / Velocity |
|---|---|---|---|
| {{bu_iter_1}} | {{bu_alcance_1}} | {{bu_hecho_1}} | {{bu_vel_1}} |
| {{bu_iter_2}} | {{bu_alcance_2}} | {{bu_hecho_2}} | {{bu_vel_2}} |

*Solo ítems terminados según la definición de terminado. Cambios de la línea de alcance explicados (intercambio del product owner D-### o solicitud de cambio C-###). Si un Must no entra en el timebox, plantear issue al gestor del proyecto.*

## 6. Issues y riesgos del paquete / Work package issues and risks

| Tipo / Type | Id | Descripción / Description | Estado / Status | ¿Planteado al gestor? / Raised to PM? |
|---|---|---|---|---|
| {{ir_tipo_1}} | {{ir_id_1}} | {{ir_desc_1}} | {{ir_estado_1}} | {{ir_planteado_1}} |
| {{ir_tipo_2}} | {{ir_id_2}} | {{ir_desc_2}} | {{ir_estado_2}} | {{ir_planteado_2}} |

*Novedades del período: nuevos, agravados, cerrados. Un pronóstico fuera de tolerancia del paquete se plantea como issue formal (I-###).*

## 7. Acciones correctivas dentro de la tolerancia del paquete / Corrective actions within work package tolerance
{{acciones_correctivas}}
*Qué hizo o hará el gestor de equipo dentro de su autoridad; responsable y fecha. Los compromisos que deben seguirse se cargan en acciones.csv (`A-###`, origen = este checkpoint).*

## Lista de verificación / Checklist
- [ ] Emitido en la frecuencia fijada en la descripción del paquete.
- [ ] Productos completados solo con calidad aprobada y registrada.
- [ ] Pronóstico explícito contra cada tolerancia del paquete; semáforo justificado.
- [ ] Todo pronóstico fuera de tolerancia ya planteado como issue al gestor del proyecto.
- [ ] Riesgos, issues y lecciones nuevos con id en los registros.
- [ ] Lo "previsto para este período" coincide con el checkpoint anterior.
- [ ] Datos sin fuente marcados `[por confirmar]`.
