---
tipo: hoja-costeo
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Hoja de costeo · Cost estimating worksheet

> Borrador generado con asistencia de IA; cada cifra cita cotización, tarifa o histórico. / AI-assisted draft; every figure cites its quote, rate or history.

**Nivel de plan / Plan level:** {{nivel_plan}}
*Proyecto, etapa N o excepción.*

**Moneda / Currency:** {{moneda}} · **Redondeo / Precision:** {{redondeo}} · **Clase de exactitud / Accuracy class:** {{clase_exactitud}}
*Orden de magnitud −25/+75 %, presupuestaria −10/+25 %, definitiva −5/+10 % (valores de referencia configurables); declarar la que aplica a esta versión.*

**Nivel de la contingencia / Contingency level:** {{nivel_contingencia}}
*Etapa (recomendado) o paquete, uno solo. BAC = Σ paquetes base + contingencia; la reserva de gestión queda fuera del BAC (SPEC del paquete §1.10.6).*

## 1. Tarifas / Rates
| Rol o persona / Role or person | Tarifa / Rate | Unidad / Unit | Vigencia / Valid until | Fuente / Source |
|---|---|---|---|---|
| {{rol}} | {{tarifa}} | h · día | {{vigencia}} | {{fuente}} |
*Tarifas internas o de contrato; indicar si incluyen cargas sociales e indirectos.*

## 2. Hoja ascendente por paquete / Bottom-up sheet per work package
| Paquete / Package | Recurso / Resource | Horas / Hours | Tarifa / Rate | Mano de obra / Labor | Materiales / Material | Suministros / Supplies | Equipos / Equipment | Viajes / Travel | Otros directos / Other direct | Indirectos / Indirect | Estimación base / Base estimate | Método / Method | Base / Basis | Confianza / Confidence | Contrato / Contract |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W-{{w}} | {{recurso}} | {{horas}} | {{tarifa}} | {{mo}} | {{mat}} | {{sum}} | {{eq}} | {{via}} | {{otros}} | {{ind}} | {{est}} | ascendente · parametrico · analogico · pert · juicio_experto | {{base}} | alta · media · baja | FFP · T&M · otro |
*Mano de obra = horas × tarifa; estimación base = mano de obra + materiales + suministros + equipos + viajes + otros directos + indirectos, sin reserva. Las horas provienen de la hoja de estimación; el riesgo se cubre una sola vez en la §5. En ágil, reemplazar esta tabla por la §2-bis.*

## 2-bis. Variante ágil: costo por iteración / Agile variant: cost per iteration
| Rol / Role | Personas / People | Dedicación / Allocation | Días por iteración / Days per iteration | Tarifa diaria / Daily rate | Costo por iteración / Cost per iteration |
|---|---|---|---|---|---|
| {{rol}} | {{personas}} | {{dedicacion}} | {{dias}} | {{tarifa}} | {{costo_iteracion}} |
**Iteraciones de la etapa / Iterations in stage:** {{n_iteraciones}} · **Puntos Must+Should / Must+Should points:** {{puntos}} · **Velocidad de referencia / Reference velocity:** {{velocidad}}
*Presupuesto de etapa = costo por iteración × iteraciones; iteraciones necesarias ≈ puntos / velocidad. Si las primeras iteraciones calibran la velocidad, declararlo como supuesto.*

## 3. Bloques alternativos / Alternative blocks
**Paramétrico / Parametric**
| Paquete / Package | Variable de costo / Cost driver | Costo unitario / Unit cost | Unidades / Units | Estimación / Estimate | Fuente / Source |
|---|---|---|---|---|---|
| W-{{w}} | {{variable}} | {{unitario}} | {{unidades}} | {{estimacion}} | {{fuente}} |
*Costo = unidades × costo unitario; usar solo dentro del rango de los datos históricos.*

**Analógico / Analogous**
| Paquete / Package | Referencia / Reference | Costo previo / Previous cost | Tamaño previo / Previous size | Tamaño actual / Current size | Multiplicador / Multiplier | Estimación / Estimate |
|---|---|---|---|---|---|---|
| W-{{w}} | {{referencia}} | {{costo_previo}} | {{tam_previo}} | {{tam_actual}} | {{multiplicador}} | {{estimacion}} |
*Multiplicador = tamaño actual / tamaño previo × ajuste (inflación, complejidad) declarado; estimación = costo previo × multiplicador.*

**Tres puntos / Three-point**
| Paquete / Package | O | M | P | Fórmula / Formula | cE | σ |
|---|---|---|---|---|---|---|
| W-{{w}} | {{o}} | {{m}} | {{p}} | PERT · triangular | {{ce}} | {{sigma}} |
*PERT: cE = (O + 4M + P) / 6, σ = (P − O) / 6; triangular: (O + M + P) / 3; P ≥ M ≥ O.*

**Verificación cruzada / Cross-check:** {{verificacion_cruzada}}
*Si para un mismo paquete la estimación ascendente y la analógica difieren más del 25 %, revisar supuestos antes de agregar.*

## 4. Agregación por cuenta de control / Control account aggregation
| Cuenta de control / Control account | Paquetes / Packages | Σ estimaciones base / Σ base estimates | Responsable / Owner |
|---|---|---|---|
| {{cuenta}} | {{paquetes}} | {{suma}} | {{responsable}} |
*Agregar de abajo hacia arriba siguiendo la WBS, solo con estimaciones base; la contingencia se suma una vez, en el nivel declarado (§5).*

## 5. Contingencia por riesgo / Risk-based contingency
| Riesgo / Risk | Probabilidad (1–5 → %) / Probability | Impacto monetario / Monetary impact | EMV | Costo de respuesta no incluido en paquetes / Response cost not in packages | Etapa o período / Stage or period |
|---|---|---|---|---|---|
| R-{{id}} | {{p}} | {{i}} | {{emv}} | {{respuesta}} | Etapa {{n}} · {{periodo}} |
| | | | **Σ = {{emv}}** | **Σ = {{respuestas}}** | |
*EMV = impacto monetario × probabilidad (1/2/3/4/5 → 10/30/50/70/90 %, configurable); contingencia = Σ EMV + Σ respuestas no incluidas ya en paquetes; sin datos, porcentaje justificado marcado como supuesto. Equivale al presupuesto de riesgo de PRINCE2 y forma parte del BAC.*

## 6. Supuestos, cotizaciones y pendientes / Assumptions, quotes and open points
- Supuestos / Assumptions: S-{{ids}}
- Cotizaciones / Quotes: {{cotizaciones}} (proveedor, fecha, validez)
- Pendientes / Open points: {{pendientes}} (`[por confirmar]` / `[to be confirmed]`)
*Todo supuesto va también al registro de supuestos.*

## Lista de verificación / Checklist
- [ ] Cada estimación muestra su cálculo, no solo el resultado.
- [ ] Horas coinciden con la hoja de estimación; tarifas con vigencia y fuente.
- [ ] Indirectos y tipo de contrato explícitos; ningún paquete lleva reserva dentro.
- [ ] P ≥ M ≥ O en tres puntos; multiplicadores ajustados y justificados.
- [ ] Verificación cruzada realizada cuando hay dos métodos.
- [ ] Contingencia vinculada a riesgos del registro, calculada una vez y en un solo nivel.
- [ ] Cotizaciones referenciadas con fecha y validez.
