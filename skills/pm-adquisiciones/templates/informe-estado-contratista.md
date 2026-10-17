---
tipo: informe-estado-contratista
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Informe de estado del contratista · Contractor status report — {{proveedor}} — {{periodo}}

> Equivale al informe de punto de control de un gestor de equipo externo, con el contenido y la frecuencia fijados en el contrato y en el paquete de trabajo. / Equivalent to a checkpoint report from an external team manager, as set in the contract and the work package.

## 1. Cabecera / Header

**Proveedor / Vendor:** {{proveedor}}
*Razón social y representante que informa.*

**Contrato / Contract:** {{id_contrato}}
*Identificador del contrato y del paquete de trabajo asociado (WP-nnn).*

**Período cubierto / Period covered:** {{periodo}}
*Fechas de inicio y fin del período de informe.*

**Fecha de entrega del informe / Report date:** {{fecha_informe}}
*Comparar con la fecha contractual; anotar retrasos en la entrega del informe.*

**Tipo de contrato / Contract type:** {{tipo_contrato}}
*Condiciona si se informa pronóstico de costo (no en precio fijo) y qué hitos de pago aplican.*

## 2. Seguimientos de informes anteriores / Follow-ups from previous reports

| Pendiente / Open item | Estado / Status | Comentario / Comment |
|---|---|---|
| {{pendiente_1}} | {{estado_pend_1}} | {{comentario_pend_1}} |

*Acciones y compromisos del período anterior: completados o aún abiertos.*

## 3. Desempeño del período / Performance this period

**Alcance / Scope:** {{desempeno_alcance}}
*Entregables contratados completados, en curso y no iniciados; referencia a los productos del paquete.*

**Calidad / Quality:** {{desempeno_calidad}}
*Actividades de calidad realizadas, defectos abiertos por severidad, resultados de aceptación; ids Q-nnn.*

**Cronograma / Schedule:** {{desempeno_cronograma}}
*En plazo, adelantado o atrasado, con causa y magnitud.*

**Costo / Cost:** {{desempeno_costo}}
*En presupuesto, por encima o por debajo, con causa; en precio fijo indicar solo hitos de pago alcanzados.*

**Hitos de pago / Payment milestones:** {{hitos_pago}}
*Alcanzados, facturados, pagados; próximos.*

## 4. Pronóstico / Forecast

**Fecha estimada de entrega final / Estimated final delivery date:** {{pronostico_fecha}}
*Coherente con el atraso reportado.*

**Costo final estimado / Estimated final cost:** {{pronostico_costo}}
*Omitir en precio fijo; en T&M o reembolsable, con supuestos.*

**Posición contra tolerancias del paquete / Position against package tolerances:** {{posicion_tolerancias}}
*Dentro, en riesgo o fuera (previsto); si está fuera, ya debe existir un issue I-nnn.*

## 5. Reclamaciones y disputas / Claims and disputes

| Id / Id | Descripción / Description | Fecha de apertura / Opened on | Estado / Status | Próximo paso / Next step | Responsable / Owner |
|---|---|---|---|---|---|
| {{reclamo_id_1}} | {{reclamo_desc_1}} | {{reclamo_fecha_1}} | {{reclamo_estado_1}} | {{reclamo_paso_1}} | {{reclamo_resp_1}} |

*Nuevas o resueltas en el período; toda reclamación se sigue hasta su resolución y alimenta el cierre del contrato.*

## 6. Solicitudes de cambio contractual / Contract change requests

| Id (C-nnn) / Id | Descripción / Description | Impacto (alcance, tiempo, costo) / Impact | Estado / Status |
|---|---|---|---|
| {{ccr_id_1}} | {{ccr_desc_1}} | {{ccr_impacto_1}} | {{ccr_estado_1}} |

*Presentadas o decididas en el período, con referencia a cambios.csv y al mecanismo del contrato.*

## 7. Riesgos e issues / Risks and issues

| Tipo / Type | Descripción / Description | Id en registros del proyecto / Project register id | Acción / Action |
|---|---|---|---|
| {{tipo_ri_1}} | {{desc_ri_1}} | {{id_ri_1}} | {{accion_ri_1}} |

*Riesgos e issues nuevos del contratista se replican en riesgos.csv e issues.csv con referencia al contrato.*

## 8. Acciones correctivas o preventivas / Corrective or preventive actions

| Acción / Action | Responsable (proveedor) / Owner (vendor) | Fecha / Date | Dimensión que recupera / Dimension recovered |
|---|---|---|---|
| {{accion_1}} | {{accion_resp_1}} | {{accion_fecha_1}} | {{accion_dim_1}} |

*Acciones concretas con responsable del lado del proveedor y fecha.*

## 9. Escalamientos y comentarios / Escalations and comments

**Escalamientos / Escalations:** {{escalamientos}}
*Temas que requieren decisión del gestor del proyecto, del proveedor sénior o de la junta.*

**Comentarios / Comments:** {{comentarios}}
*Contexto adicional del proveedor o del administrador del contrato.*

## 10. Próximo período / Next period

{{proximo_periodo}}
*Entregables previstos, actividades de calidad, hitos de pago y fechas.*

## Lista de verificación / Checklist
- [ ] Las cuatro dimensiones de desempeño cubiertas (alcance, calidad, cronograma, costo según tipo de contrato).
- [ ] Pronóstico de fecha coherente con el atraso reportado; posición contra tolerancias explícita.
- [ ] Reclamaciones con fecha de apertura, estado y próximo paso.
- [ ] Riesgos e issues replicados en los registros del proyecto con referencia al contrato.
- [ ] Acciones correctivas con responsable del proveedor y fecha.
- [ ] Solicitudes de cambio contractual referenciadas en cambios.csv.
- [ ] Informe recibido en la fecha contractual (o retraso anotado).
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
