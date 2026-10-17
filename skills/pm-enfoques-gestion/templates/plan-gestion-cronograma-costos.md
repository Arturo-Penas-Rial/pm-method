---
tipo: plan-gestion-cronograma-costos
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de gestión del cronograma y de los costos · Schedule and cost management plan — {{proyecto}}

> Reglas para construir, medir y controlar el cronograma y el presupuesto: metodología, unidades, precisión, umbrales, línea base y reglas de valor ganado. Lo prepara el gestor; lo aprueba el ejecutivo. / Rules for building, measuring and controlling schedule and budget.

**Enfoque de entrega / Delivery approach:** {{enfoque_entrega}}
**Versión mínima / Minimal version:** {{version_minima}}
*`sí`: secciones 1, 3, 4 y 6.*

## 1. Metodología y herramienta / Methodology and tool

{{metodologia}}
*Método de programación (camino crítico, cadena crítica, cadencia ágil por iteraciones, flujo kanban) y herramienta (`cpm.py`, utf8proj, MS Project, tracker). Ver `pm-cronograma-estimacion`.*

## 2. Unidades y precisión / Units and precision

| Concepto / Item | Regla / Rule |
|---|---|
| Unidad de duración / Duration unit | {{unidad_duracion}} |
| Unidad de esfuerzo / Effort unit | {{unidad_esfuerzo}} |
| Moneda / Currency | {{moneda}} |
| Redondeo / Rounding | {{redondeo}} |
| Rango de precisión por fase (orden de magnitud → definitivo) / Accuracy by phase | {{precision_fase}} |

## 3. Umbrales de control / Control thresholds

| Indicador / Indicator | Verde / Green | Ámbar / Amber | Rojo / Red |
|---|---|---|---|
| Desvío de cronograma (SV % o días) / Schedule variance | {{sv_verde}} | {{sv_ambar}} | {{sv_rojo}} |
| Desvío de costo (CV %) / Cost variance | {{cv_verde}} | {{cv_ambar}} | {{cv_rojo}} |
| SPI | {{spi_verde}} | {{spi_ambar}} | {{spi_rojo}} |
| CPI | {{cpi_verde}} | {{cpi_ambar}} | {{cpi_rojo}} |

*Semáforo por defecto del paquete contra las tolerancias (el mismo que aplica `evm.py --tol-costo --tol-plazo`): verde = desvío ≤ 50 % de la tolerancia; ámbar = 50–100 %; rojo = fuera de tolerancia → informe de excepción (plantilla de `pm-issues-cambios`) a `pm-director`. En ágil con costo y fecha fijos (`evm.py --modo agil`), un EAC > BAC se lee como alcance que no entra, contra la tolerancia de alcance MoSCoW; hay excepción solo si los Must no entran.*

## 4. Línea base y actualización / Baseline and updates

{{linea_base}}
*Cuándo se fija la línea base (al autorizar la etapa), qué cambios la modifican (solo cambios aprobados), frecuencia de actualización del avance real, quién la mantiene.*

## 5. Reglas de valor ganado / Earned value rules

| Regla / Rule | Definición / Definition |
|---|---|
| Técnica de medición del avance (0/100, 50/50, % físico, hitos ponderados) / Progress measurement | {{evm_medicion}} |
| Nivel de las cuentas de control / Control account level | {{evm_cuentas}} |
| Fórmula de EAC preferida / Preferred EAC | {{evm_eac}} |
| Periodicidad / Frequency | {{evm_periodicidad}} |

*Si el enfoque es ágil, reemplazar por burn-up de alcance y costo por iteración; ver `pm-progreso-reportes`.*

## 6. Reservas y contingencias / Reserves and contingencies

{{reservas}}
*Reserva de contingencia (por riesgos identificados, dentro del BAC, la libera el gestor) y reserva de gestión (fuera del BAC, la libera solo la junta); presupuesto autorizado = BAC + reserva de gestión; sin doble conteo de contingencia por paquete y por etapa.*

## 7. Vínculo financiero / Financial link

{{vinculo_financiero}}
*Relación con el plan de cuentas de la organización, autoridad de compromiso de fondos, flujo de caja, cómo se informan los costos reales.*

## 8. Iteraciones y releases (si aplica) / Iterations and releases

{{iteraciones}}
*Duración de iteración, calendario de releases, cómo se presupuesta por iteración y cómo se mapea a las etapas de gestión.*

## Lista de verificación / Checklist
- [ ] Metodología y herramienta coherentes con el enfoque de entrega.
- [ ] Umbrales definidos y alineados con las tolerancias de etapa en `estado.json`.
- [ ] Reglas de línea base y de EVM (o burn charts) explícitas.
- [ ] Autoridad de liberación de reservas definida.
- [ ] Aprobado por el ejecutivo.
