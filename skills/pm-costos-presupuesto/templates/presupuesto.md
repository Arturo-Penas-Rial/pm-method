---
tipo: presupuesto
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Presupuesto y línea base de costo · Budget and cost baseline

> Borrador generado con asistencia de IA. Sin plan aprobado no hay línea base. / AI-assisted draft; no baseline until the plan is approved.

**Nivel de plan / Plan level:** {{nivel_plan}} · **Moneda / Currency:** {{moneda}}
*Proyecto o etapa N; cifras tomadas de la hoja de costeo.*

**Enfoque de entrega / Delivery approach:** {{enfoque_entrega}}
*Predictivo: costeo desde la WBS. Ágil: costo por iteración × iteraciones de la etapa, con el backlog como alcance.*

## 1. Resumen / Summary
| Componente / Component | Importe / Amount | Fuente / Source |
|---|---|---|
| Σ estimaciones base de paquetes (incl. gestión) / Σ base work package estimates (incl. management) | {{suma_paquetes}} | hoja-costeo §4 (sin reserva dentro de los paquetes) |
| Contingencia para riesgos identificados / Contingency reserve | {{contingencia}} | hoja-costeo §5 (EMV + respuestas; un solo nivel: {{nivel_contingencia}}) |
| **BAC (línea base de medición) / BAC (performance measurement baseline)** | **{{bac}}** | Σ paquetes base + contingencia; = último pv_acumulado |
| Reserva de gestión (propuesta, fuera del BAC) / Management reserve (proposed, outside BAC) | {{reserva_gestion}} | la libera solo la junta / capa de negocio |
| Presupuesto de cambio (opcional, fuera del BAC) / Change budget (optional) | {{presupuesto_cambio}} | autoridad de cambio |
| **Presupuesto autorizado / Authorized budget** | **{{presupuesto_autorizado}}** | BAC + reserva de gestión (+ presupuesto de cambio) |
| Restricción del mandato o techo del business case / Mandate constraint or business case ceiling | {{techo_bc}} | 00-direccion/ |
| Tolerancia de costo (proyecto / etapa) / Cost tolerance | {{tolerancia_costo}} | estado.json.tolerancias.proyecto.costo / .etapa.costo |
*Nunca se suma contingencia dentro de cada paquete y otra vez aquí. Si el BAC excede la restricción o la tolerancia, ver §8: opciones y decisión de la junta antes de aprobar.*

## 2. Presupuesto por etapa / Budget per stage
| Etapa / Stage | Paquetes o iteraciones / Packages or iterations | Estimación base / Base estimate | Contingencia / Contingency | BAC de etapa / Stage BAC | Tolerancia de costo / Cost tolerance | Puerta / Gate |
|---|---|---|---|---|---|---|
| {{n}} · {{nombre_etapa}} | {{paquetes}} | {{estimacion}} | {{contingencia}} | {{total}} | {{tolerancia}} | autorizar-etapa |
| **Total / Total** | | {{suma_est}} | {{suma_cont}} | {{suma_total}} | | |
*Etapa 1 = iniciación; etapas de entrega 2…n. La suma de BAC de etapa = BAC del proyecto; la tolerancia de etapa la fija la junta en cada autorizar-etapa (estado.py tolerancia --nivel etapa).*

## 3. Línea base por período / Time-phased baseline
| Período / Period | Etapa / Stage | PV del período / Period PV | PV acumulado / Cumulative PV | Método de distribución / Distribution method | Notas / Notes |
|---|---|---|---|---|---|
| {{periodo}} | {{etapa}} | {{pv_periodo}} | {{pv_acum}} | lineal · hitos ponderados · 0/100 · 50/50 | {{notas}} |
*Mismos valores que linea-base-costo.csv (columnas pv_periodo y pv_acumulado); el último PV acumulado = BAC, sin reserva de gestión. evm.py lee pv_acumulado junto con ev_acumulado y ac_acumulado, desde progreso.csv (pm-progreso-reportes) o desde las columnas ev_acumulado/ac_acumulado de este CSV completadas en cada corte (pasar solo las filas hasta el corte; las futuras vacías no se leen): `evm.py --csv <archivo> --bac {{bac}} --tol-costo <%> --tol-plazo <%>` (`--modo agil` en ágil).*

## 4. Curva S / S-curve
```mermaid
xychart-beta
    title "Curva S · PV acumulado ({{moneda}})"
    x-axis [{{periodos}}]
    y-axis "PV acumulado" 0 --> {{bac}}
    line [{{pv_acumulados}}]
```
*Lista de períodos entre corchetes y valores acumulados en el mismo orden. Con integración de gráficos configurada, pm-visuales puede producir la versión gráfica.*

## 5. Flujo de caja / Cash flow
| Período / Period | Salidas previstas / Planned outflows | Entradas o financiación / Inflows or funding | Saldo acumulado / Cumulative balance | Límite de financiación / Funding limit | Exceso / Excess |
|---|---|---|---|---|---|
| {{periodo}} | {{salidas}} | {{entradas}} | {{saldo}} | {{limite}} | {{exceso}} |
*Conciliación del límite de financiación: si hay exceso en un período, reprogramar trabajo (pm-cronograma-estimacion) y señalarlo a la junta; no maquillar.*

## 6. Criterio de medición y reglas de desempeño / Cost measurement and performance rules
- Momento de registro del costo / Cost recognition: {{criterio_medicion}} (compromiso · orden · recepción · devengo)
- Método de avance para EV / EV method: {{metodo_ev}}
- Nivel de reporte / Reporting level: {{nivel_reporte}} (cuenta de control · paquete)
- Umbrales de control / Control thresholds: {{umbrales}} (semáforo de evm.py contra la tolerancia: verde ≤ 50 %, ámbar 50–100 %, rojo = fuera de tolerancia → excepción)
*Alineado con los controles del PID o el plan de gestión de costos.*

## 7. Supuestos, riesgos y pendientes / Assumptions, risks and open points
- Supuestos / Assumptions: S-{{ids}}
- Riesgos de costo que sustentan la contingencia / Cost risks behind contingency: R-{{ids}}
- Pendientes / Open points: {{pendientes}}
*Tarifas, cotizaciones o límites de financiación sin fuente: [por confirmar] / [to be confirmed].*

## 8. Ajuste a la restricción / Fit to the constraint
| Opción / Option | Ahorro / Saving | Efecto en tiempo, riesgo y beneficios / Effect on time, risk and benefits | Decide / Decides |
|---|---|---|---|
| Reducir alcance Could/Should (MoSCoW) / Scope reduction | {{ahorro}} | {{efecto}} | product owner (dentro de tolerancia) · junta |
| Cambiar recursos o make-or-buy / Resources or make-or-buy | {{ahorro}} | {{efecto}} | gestor · junta |
| Reprogramar, quitar recargos o compresión / Re-sequence, remove premiums | {{ahorro}} | {{efecto}} | gestor |
*Solo si el BAC excede la restricción o la tolerancia. Si después de las opciones sigue fuera: no se aprueba el plan; pm-director lleva la decisión a la junta (o a la capa de negocio si supera la tolerancia de proyecto).*

## Lista de verificación / Checklist
- [ ] BAC = Σ paquetes base + contingencia; reserva de gestión fuera del BAC; presupuesto autorizado = BAC + reserva de gestión.
- [ ] Contingencia calculada una sola vez y en un nivel declarado, justificada con riesgos (EMV).
- [ ] Presupuesto por etapa (iniciación = etapa 1) con BAC de etapa y tolerancias que caben en la de proyecto.
- [ ] pv_periodo suma el BAC y coincide con el cronograma o el release plan.
- [ ] Curva S renderiza y termina en el BAC.
- [ ] Flujo de caja conciliado con el límite de financiación.
- [ ] Comparación con la restricción del mandato hecha; §8 completa si no entra.
- [ ] Aprobación pendiente con el plan (autorizar-proyecto / autorizar-etapa, registrada por pm-director).
