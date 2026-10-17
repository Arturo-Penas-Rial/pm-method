---
tipo: analisis-valor-ganado
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Análisis de valor ganado · Earned value analysis

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}} · **Nivel / Level:** {{nivel}}
*Proyecto, etapa o cuenta de control.*

**Fecha de corte / Cut-off date:** {{fecha_corte}} · **Período / Period:** {{periodo}}

**Línea base de costo / Cost baseline:** {{ruta_linea_base}} (versión {{version_linea_base}})
*Debe incluir los cambios aprobados hasta la fecha; el BAC es su total sin reserva de gestión.*

**Método de medición del EV por producto / EV measurement method:** {{metodo_ev}}
*0/100, 50/50, hitos ponderados, % físico completado, esfuerzo prorrateado, nivel de esfuerzo; declarar por producto o paquete si difieren.*

**Fuente de AC / Source of AC:** {{fuente_ac}}
*Costos devengados (compromisos incurridos), no solo facturas pagadas.*

**Comando ejecutado / Command run:** `python3 <pm-estado-proyecto>/scripts/evm.py --csv 03-control/reportes/progreso.csv --bac {{bac}} --tol-costo {{tol_costo_pct}} --tol-plazo {{tol_plazo_pct}} --eac {{eac_variante}} [--modo agil] --json` (o `--pv {{pv}} --ev {{ev}} --ac {{ac}} --bac {{bac}}`)
*Correr con tolerancias de etapa y luego de proyecto; copiar `semaforo_costo`, `semaforo_cronograma`, `base_semaforo` y `excepcion_prevista`.*
*Mostrar el cálculo; redondear solo en la presentación.*

## 1. Magnitudes / Base figures ({{moneda}})

| Magnitud / Figure | Período anterior acumulado / Previous cumulative | Este período / Current period | Acumulado actual / Current cumulative |
|---|---|---|---|
| BAC | {{bac}} | — | {{bac}} |
| PV | {{pv_prev}} | {{pv_per}} | {{pv}} |
| EV | {{ev_prev}} | {{ev_per}} | {{ev}} |
| AC | {{ac_prev}} | {{ac_per}} | {{ac}} |

*El acumulado anterior debe coincidir con el informe anterior. Verificar EV ≤ PV total del componente.*

## 2. Variaciones e índices / Variances and indices

| Indicador / Indicator | Fórmula / Formula | Valor / Value | Lectura / Reading | Semáforo / RAG |
|---|---|---|---|---|
| SV | EV − PV | {{sv}} | {{lect_sv}} | — |
| CV | EV − AC | {{cv}} | {{lect_cv}} | — |
| SPI | EV / PV | {{spi}} | {{lect_spi}} | {{rag_spi}} |
| CPI | EV / AC | {{cpi}} | {{lect_cpi}} | {{rag_cpi}} |
| % planificado / Percent planned | PV / BAC | {{pct_plan}} % | | |
| % ganado / Percent earned | EV / BAC | {{pct_ganado}} % | | |
| % gastado / Percent spent | AC / BAC | {{pct_gastado}} % | | |

*Convención: SV y CV negativos = atraso y sobrecosto. Umbrales de semáforo de referencia 0,95 / 0,85 (configurables; declarar los del PID). SPI tiende a 1 al final: complementar con camino crítico.*

**Causa raíz de la variación de cronograma / Root cause of schedule variance:** {{causa_sv}}
**Impacto en cronograma (hitos, ruta crítica) / Schedule impact:** {{impacto_sv}}
**Causa raíz de la variación de costo / Root cause of cost variance:** {{causa_cv}}
**Impacto en presupuesto, contingencia y reservas / Budget impact:** {{impacto_cv}}

## 3. Pronóstico de costo / Cost forecast

| Variante de EAC / EAC variant | Supuesto / Assumption | Fórmula / Formula | Valor / Value |
|---|---|---|---|
| Atípica / Atypical | la variación fue puntual; el resto se hará al ritmo presupuestado | AC + (BAC − EV) | {{eac_atipico}} |
| Tendencia / Typical | el CPI acumulado se mantendrá | BAC / CPI | {{eac_tendencia}} |
| Compuesta / Composite | costo y plazo seguirán afectando | AC + (BAC − EV) / (CPI × SPI) | {{eac_compuesto}} |
| Ascendente / Bottom-up | la línea base ya no sirve; se reestima el resto | AC + ETC reestimado | {{eac_ascendente}} |

**EAC seleccionada / Selected EAC:** {{eac_seleccionada}} ({{eac_variante}})
**Justificación / Justification:** {{justificacion_eac}}
*Explicar por qué ese supuesto describe la situación; presentar al menos dos variantes.*

| Derivado / Derived | Fórmula / Formula | Valor / Value | Lectura / Reading |
|---|---|---|---|
| ETC | EAC − AC | {{etc}} | {{lect_etc}} |
| VAC | BAC − EAC | {{vac}} | {{lect_vac}} |
| TCPI (BAC) | (BAC − EV) / (BAC − AC) | {{tcpi_bac}} | {{lect_tcpi_bac}} |
| TCPI (EAC) | (BAC − EV) / (EAC − AC) | {{tcpi_eac}} | {{lect_tcpi_eac}} |

*TCPI(BAC) > 1,10 con CPI < 0,90 sugiere que terminar en BAC es poco realista y conviene revisar la línea base vía control de cambios.*

## 4. Pronóstico de fecha / Schedule forecast

| Método / Method | Fórmula / Formula | Valor / Value |
|---|---|---|
| Por SPI (aproximación) / By SPI | duración planificada / SPI | {{dur_spi}} |
| Cronograma ganado / Earned schedule | ES = t tal que PV(t) = EV; SPI(t) = ES / AT; duración / SPI(t) | {{dur_es}} |
| Camino crítico / Critical path | fecha de fin según red actualizada (`cpm.py` o utf8proj) | {{fecha_cpm}} |

**Fecha de fin pronosticada / Forecast finish:** {{fecha_fin_pron}} vs. base {{fecha_fin_base}} → variación {{var_fecha}} días
*Elegir el método y decirlo; el camino crítico prevalece cuando existe.*

## 5. Comparación con tolerancias / Tolerance check

| Objetivo / Objective | Pronóstico / Forecast | Tolerancia de etapa / Stage tolerance | Tolerancia de proyecto / Project tolerance | % consumido / Used | Estado / Status |
|---|---|---|---|---|---|
| Costo / Cost | {{eac_seleccionada}} | {{tol_costo_e}} | {{tol_costo_p}} | {{pct_tol_costo}} | {{estado_costo}} |
| Tiempo / Time | {{fecha_fin_pron}} | {{tol_tiempo_e}} | {{tol_tiempo_p}} | {{pct_tol_tiempo}} | {{estado_tiempo}} |

*`verde` (≤ 50 % de la tolerancia), `ambar` (50–100 %), `rojo` (fuera de tolerancia: `excepcion_prevista = true` → informe de excepción con la plantilla de `pm-issues-cambios`, entregado a `pm-director`). Valores tomados de `evm.py --tol-costo/--tol-plazo`.*

## 6. Tendencia / Trend

| Período / Period | SPI | CPI | EAC seleccionada | Comentario / Comment |
|---|---|---|---|---|
| {{per_1}} | {{spi_1}} | {{cpi_1}} | {{eac_1}} | {{com_1}} |
| {{per_2}} | {{spi_2}} | {{cpi_2}} | {{eac_2}} | {{com_2}} |
| {{per_actual}} | {{spi}} | {{cpi}} | {{eac_seleccionada}} | {{com_actual}} |

*De `progreso.csv`; graficar curva S (PV, EV, AC) con `pm-visuales` cuando ayude.*

## 7. EVM adaptativo (si aplica) / Adaptive EVM (if applicable)

| Iteración / Iteration | Puntos planificados (PV) | Puntos terminados (EV) | Costo del equipo (AC) | SPI | CPI | Velocidad / Velocity |
|---|---|---|---|---|---|---|
| {{it_1}} | {{it_pv_1}} | {{it_ev_1}} | {{it_ac_1}} | {{it_spi_1}} | {{it_cpi_1}} | {{vel_1}} |

**Iteraciones restantes ≈ puntos restantes / velocidad promedio / Remaining iterations:** {{iter_restantes}}
*Solo cuentan ítems terminados según la definición de terminado; omitir la sección en entregas puramente predictivas. Con costo y fecha fijos (`evm.py --modo agil`), un EAC > BAC se interpreta como alcance pronosticado que no entra, contra la tolerancia de alcance MoSCoW, no como sobrecosto; es excepción solo si algún Must no entra.*

**Must que no entran / Must items that do not fit:** {{must_fuera}}

## 8. Conclusión y acciones / Conclusion and actions
{{conclusion}}
*Qué dicen los índices, qué se recomienda (acción correctiva dentro de tolerancia, cambio de línea base, excepción), con ids de acciones (`A-###`), issues o decisiones.*

## Lista de verificación / Checklist
- [ ] BAC = línea base vigente con cambios aprobados; reserva de gestión fuera.
- [ ] Método de EV declarado; EV ≤ PV del componente; AC devengado.
- [ ] Acumulados del período anterior coinciden con el informe anterior.
- [ ] Al menos dos EAC presentadas y la elegida justificada; ETC, VAC y TCPI recalculados con ella.
- [ ] Convención de signos y umbrales de semáforo declarados.
- [ ] Causas raíz de SV y CV vinculadas a issues o riesgos con id.
- [ ] Pronóstico comparado con tolerancias de etapa y proyecto; excepción derivada si corresponde.
- [ ] Cifras idénticas a las del highlight y del análisis de variaciones del mismo período.
- [ ] Cálculo mostrado (fórmula con valores); redondeo solo en presentación.
