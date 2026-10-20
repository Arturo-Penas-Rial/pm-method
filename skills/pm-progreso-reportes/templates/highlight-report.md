---
tipo: highlight-report
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Informe de destacados · Highlight report (≈ project status report)

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}} ({{etapa_inicio}} → {{etapa_fin_previsto}})

**Ejecutivo / Executive:** {{ejecutivo}} · **Gestor del proyecto / Project manager:** {{gestor}}

**Período / Period:** {{periodo_desde}} – {{periodo_hasta}} · **Nº de informe / Report no.:** {{numero}} · **Cadencia / Cadence:** {{cadencia}}
*Cadencia acordada por la junta y registrada en el PID.*

**Variante / Variant:** {{variante}}
*`minima` (una página: solo las secciones marcadas [mín]) o `completa` (las doce). Mínima para proyectos pequeños, perfil ágil mínimo o cadencia semanal; completa con EVM, proveedores, varias audiencias o algún ámbar/rojo.*

**Audiencia / Audience:** {{audiencia}}
*Junta del proyecto por defecto; las versiones para equipo o cliente se derivan de esta con las mismas cifras.*

**Fuentes / Sources:** plan de etapa {{ruta_plan_etapa}} · `progreso.csv` + `evm.py` ({{fecha_corte}}) · `registro.py resumen` · checkpoints {{checkpoints}}
*Toda cifra de este informe debe poder rastrearse a una de estas fuentes.*

## 1. Resumen ejecutivo / Executive summary [mín]
{{resumen_ejecutivo}}
*Tres a cinco frases: estado general, principal desvío, principal decisión que se pide a la junta.*

## 2. Semáforo por objetivo / RAG by objective [mín]

| Objetivo / Objective | Período anterior / Previous | Este período / Current | Cifra y umbral que lo justifican / Figure and threshold | Ruta hacia verde / Route to green |
|---|---|---|---|---|
| General / Overall | {{rag_general_prev}} | {{rag_general}} | {{just_general}} | {{ruta_general}} |
| Beneficios / Benefits | {{rag_ben_prev}} | {{rag_ben}} | {{just_ben}} | {{ruta_ben}} |
| Tiempo / Time | {{rag_tiempo_prev}} | {{rag_tiempo}} | {{just_tiempo}} | {{ruta_tiempo}} |
| Costo / Cost | {{rag_costo_prev}} | {{rag_costo}} | {{just_costo}} | {{ruta_costo}} |
| Calidad / Quality | {{rag_cal_prev}} | {{rag_cal}} | {{just_cal}} | {{ruta_cal}} |
| Alcance / Scope | {{rag_alc_prev}} | {{rag_alc}} | {{just_alc}} | {{ruta_alc}} |
| Sostenibilidad / Sustainability | {{rag_sost_prev}} | {{rag_sost}} | {{just_sost}} | {{ruta_sost}} |
| Riesgo / Risk | {{rag_riesgo_prev}} | {{rag_riesgo}} | {{just_riesgo}} | {{ruta_riesgo}} |

*`verde`, `ambar`, `rojo`. Cada color se justifica con el pronóstico comparado con la tolerancia: verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo fuera de tolerancia → excepción (tiempo y costo: `semaforo_cronograma` y `semaforo_costo` de `evm.py --tol-plazo/--tol-costo`; riesgo: rojo si `altos_abiertos` tiene alguno sin respuesta o sin propietario). Nunca por percepción.*

## 3. Seguimientos / Follow-ups
{{seguimientos}}
*Pendientes del informe anterior y decisiones que la junta tomó desde entonces (`D-###`).*

## 4. Este período / This period [mín]

**Productos completados y aprobados / Products completed and approved:** {{productos_completados}}
*Solo con calidad registrada; ids del PBS.*

**Paquetes de trabajo / Work packages:** en ejecución {{wp_en_curso}} · completados {{wp_completados}} · pendientes de autorizar {{wp_pendientes}}
*Con datos de órdenes de compra y facturación si los ejecutan proveedores externos.*

**Productos planificados no iniciados o no completados / Planned products not started or not finished:** {{productos_atrasados}}
*Alerta temprana de tiempo; causa raíz en una línea.*

**Acciones correctivas tomadas / Corrective actions taken:** {{acciones_tomadas}}
*Demuestran que el gestor actúa dentro de tolerancia; ids `A-###` de acciones.csv o del paquete.*

## 5. Próximo período / Next period [mín]

**Productos a completar / Products to complete:** {{prox_productos}}
**Paquetes a autorizar o completar / Work packages to authorize or complete:** {{prox_wp}}
**Acciones correctivas a completar / Corrective actions to complete:** {{prox_acciones}}
*Esto es lo que el próximo informe deberá contrastar con lo logrado.*

## 6. Decisiones que necesita la junta / Decisions required from the board [mín]

*Insumo: `puertas.py --proyecto <dir> estado --markdown` (puertas registradas, condiciones abiertas, observaciones de la verificación y bloqueos de la próxima puerta).*

{{bloque_puertas}}


| Decisión / Decision | Contexto / Context | Opciones / Options | Recomendación / Recommendation | Fecha límite / Needed by |
|---|---|---|---|---|
| {{dec_1}} | {{ctx_1}} | {{opc_1}} | {{rec_1}} | {{fecha_1}} |
| {{dec_2}} | {{ctx_2}} | {{opc_2}} | {{rec_2}} | {{fecha_2}} |

*Cambios fuera de la autoridad delegada, concesiones, riesgos escalados, consejo solicitado. Escribir "ninguna" si no hay.*

## 7. Estado de tolerancias / Tolerance status

| Objetivo / Objective | Nivel / Level | Plan | Real a la fecha / Actual | Pronóstico / Forecast | Tolerancia / Tolerance | % consumido / Used |
|---|---|---|---|---|---|---|
| Tiempo / Time | etapa | {{t_plan_e}} | {{t_real_e}} | {{t_pron_e}} | {{t_tol_e}} | {{t_pct_e}} |
| Tiempo / Time | proyecto | {{t_plan_p}} | {{t_real_p}} | {{t_pron_p}} | {{t_tol_p}} | {{t_pct_p}} |
| Costo / Cost | etapa | {{c_plan_e}} | {{c_real_e}} | {{c_pron_e}} | {{c_tol_e}} | {{c_pct_e}} |
| Costo / Cost | proyecto | {{c_plan_p}} | {{c_real_p}} | {{c_pron_p}} | {{c_tol_p}} | {{c_pct_p}} |
| Alcance / Scope | etapa | {{a_plan_e}} | {{a_real_e}} | {{a_pron_e}} | {{a_tol_e}} | {{a_pct_e}} |

*Reportar contra tolerancias de etapa y de proyecto, no solo contra el plan de etapa. Pronóstico, no acumulado. `% consumido` = desvío previsto ÷ tolerancia; > 100 % → `excepcion_prevista`.*

### 7b. Avance ágil — burn-up / Agile progress — burn-up [mín en ágil e híbrido]

| Iteración / Iteration | Alcance total (pts) / Total scope | Terminado acumulado (pts) / Done to date | Velocidad / Velocity | Nota / Note |
|---|---|---|---|---|
| {{iter_1}} | {{alcance_1}} | {{hecho_1}} | {{vel_1}} | {{nota_1}} |
| {{iter_2}} | {{alcance_2}} | {{hecho_2}} | {{vel_2}} | {{nota_2}} |
| {{iter_3}} | {{alcance_3}} | {{hecho_3}} | {{vel_3}} | {{nota_3}} |

**Línea base del release / Release baseline:** {{alcance_base}} pts · **Cambio de alcance / Scope change:** {{delta_alcance}}
*Del release plan (solo línea base); todo cambio de la línea de alcance se explica con un intercambio del product owner (D-###) o una solicitud de cambio (C-###).*

**Velocidad media (ventana de {{ventana}} iteraciones) / Average velocity:** {{velocidad_media}} · **Iteraciones restantes / Remaining iterations:** {{iter_restantes}} · **Fecha pronosticada vs. fija / Forecast vs. fixed date:** {{fecha_pronostico}} / {{fecha_fija}}

**Must en riesgo / Must items at risk:** {{must_en_riesgo}}
*Regla EVM ágil (`evm.py --modo agil`): con costo y fecha fijos, un EAC > BAC es alcance que no entra; se mide contra la tolerancia de alcance MoSCoW y solo es excepción si algún Must no entra. Omitir el bloque en predictivo puro.*

## 8. Finanzas / Finances

| Concepto / Item | Monto / Amount ({{moneda}}) |
|---|---|
| Presupuesto de la etapa (BAC etapa) / Stage budget | {{bac_etapa}} |
| Costo real acumulado (AC) / Actual cost to date | {{ac}} |
| Valor ganado (EV) / Earned value | {{ev}} |
| Valor planificado (PV) / Planned value | {{pv}} |
| SPI · CPI | {{spi}} · {{cpi}} |
| Pronóstico a la conclusión (EAC, variante {{eac_variante}}) / Forecast at completion | {{eac}} |
| Variación a la conclusión (VAC) / Variance at completion | {{vac}} |
| Presupuesto de cambio usado / remanente · Change budget used / remaining | {{pc_usado}} / {{pc_remanente}} |
| Presupuesto de riesgo usado / remanente · Risk budget used / remaining | {{pr_usado}} / {{pr_remanente}} |

**Comentario / Comment:** {{comentario_finanzas}}
*En ágil sin línea base de costo: reemplazar EV/PV por puntos terminados vs. planificados y velocidad; declarar que no hay EVM. Detalle en `analisis-valor-ganado.md`.*

## 9. Hitos / Milestones

| Hito / Milestone | Fecha base / Baseline | Fecha actual / Current | Variación (días) / Variance | Comentario / Comment |
|---|---|---|---|---|
| {{hito_1}} | {{base_1}} | {{actual_1}} | {{var_1}} | {{com_1}} |
| {{hito_2}} | {{base_2}} | {{actual_2}} | {{var_2}} | {{com_2}} |
| Fin de etapa / Stage end | {{base_fin}} | {{actual_fin}} | {{var_fin}} | {{com_fin}} |

*Positivo = retraso. Indicar si la ruta crítica cambió.*

## 10. Riesgos, issues y acciones clave / Key risks, issues and actions [mín: top 3]

| Tipo / Type | Id | Resumen / Summary | P×I o prioridad / P×I or priority | Propietario / Owner | Próxima acción / Next action | Estado / Status |
|---|---|---|---|---|---|---|
| riesgo | {{r_id_1}} | {{r_res_1}} | {{r_pi_1}} | {{r_prop_1}} | {{r_acc_1}} | {{r_est_1}} |
| issue | {{i_id_1}} | {{i_res_1}} | {{i_pri_1}} | {{i_prop_1}} | {{i_acc_1}} | {{i_est_1}} |

**Registros del período / Register movements:** riesgos nuevos {{r_nuevos}} · cerrados {{r_cerrados}} · ocurridos {{r_ocurridos}} · issues nuevos {{i_nuevos}} · cerrados {{i_cerrados}} · escalados {{i_escalados}}

**Resumen de registros / Register summary:** riesgos abiertos {{r_abiertos}} · altos abiertos (P×I ≥ 15) {{r_altos}} · sin respuesta {{r_sin_respuesta}} · sin propietario {{r_sin_propietario}} · issues abiertos {{i_abiertos}} · issues sin responsable {{i_sin_responsable}}

**Acciones / Actions:** abiertas {{a_abiertas}} · vencidas {{a_vencidas}} · abiertas por responsable / open by owner {{a_por_responsable}}
*Valores tal como los devuelve `registro.py resumen --json` (`abiertos`, `altos_abiertos`, `sin_respuesta`, `sin_propietario`, `sin_responsable`, `vencidas`, `abiertas_por_responsable`; cantidades desde `<lista>_total`); solo los críticos se listan en la tabla.*

**Solicitudes de cambio y fuera de especificación / RFCs and off-specs:** planteadas {{rfc_planteadas}} · decididas {{rfc_decididas}} · pendientes {{rfc_pendientes}}
*Listar ids (`C-###`, `I-###`) aunque sea "ninguna".*

**Excepciones / Exceptions:** {{excepciones}}
*Si hay pronóstico fuera de tolerancia: referencia al informe de excepción `X-###` (plantilla de pm-issues-cambios, entregado a pm-director) y su estado; si una desviación se resolvió dentro de tolerancia de etapa, describir la acción correctiva aquí.*

## 11. Comentario del gestor del proyecto / Project manager's commentary
{{comentario_gestor}}
*Evaluación crítica: tendencias (issues acumulados, pruebas sin retestear, movimientos de riesgos), viabilidad del caso de negocio, salud del equipo, qué le preocupa aunque esté en verde.*

## 12. Lecciones / Lessons
{{lecciones}}
*Qué fue bien, qué fue mal, recomendaciones; ids `L-###`. Omitir la sección si no hay lecciones en el período.*

**Próximo informe / Next report:** {{fecha_proximo}} · **Fin de etapa previsto / Expected stage end:** {{fin_etapa}} ({{aviso_sb}})
*Si el fin de etapa se acerca, indicar que se propone `estado.py limite-etapa` (CS → SB, Managing a stage boundary).*

## Lista de verificación / Checklist
- [ ] Variante declarada; la mínima cabe en una página con las secciones [mín]; detalle en anexos y enlaces a registros.
- [ ] En ágil/híbrido: bloque burn-up con línea de alcance total, velocidad con ventana y Must en riesgo.
- [ ] Siete objetivos con semáforo justificado por cifra y umbral, comparado con el período anterior.
- [ ] Hecho y pronóstico distinguidos; tolerancias de etapa y de proyecto reportadas.
- [ ] Lo "previsto" del informe anterior contrastado con lo logrado; seguimientos cerrados o explicados.
- [ ] Productos completados solo con calidad aprobada.
- [ ] Decisiones que necesita la junta listadas (o "ninguna"); RFC y fuera de especificación listados (o "ninguna").
- [ ] Riesgos, issues y acciones críticos con ids coherentes con los registros; conteos iguales a `registro.py resumen`.
- [ ] Finanzas e hitos coherentes con `evm.py` y el plan de etapa; variante de EAC declarada.
- [ ] Toda excepción pronosticada referenciada a su informe de excepción.
- [ ] Cifras con fuente; faltantes `[por confirmar]`; confirmado por aseguramiento antes de enviar a la junta.
