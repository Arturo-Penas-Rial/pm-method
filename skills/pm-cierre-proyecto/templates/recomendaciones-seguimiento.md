---
tipo: recomendaciones-seguimiento
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Recomendaciones de acciones de seguimiento · Follow-on action recommendations — {{proyecto}}

> Borrador generado con apoyo de IA. Toda recomendación tiene destinatario, responsable propuesto y fecha; nada queda abierto sin dueño. / AI-assisted draft. Every recommendation has an addressee, a proposed owner and a date; nothing is left open without an owner.

## 1. Contexto / Context

**Tipo de cierre / Closure type:** {{tipo_cierre}}
*planificado · prematuro.*

**Fecha de corte / Cut-off date:** {{fecha_corte}}
*Estado de los registros a esta fecha.*

**Fuentes / Sources:** {{fuentes}}
*issues.csv, riesgos.csv, cambios.csv, product status account, cierres de contrato, enfoque de beneficios.*

**Audiencias / Audiences:** {{audiencias}}
*Operaciones, soporte, RR. HH., finanzas, proveedor, programa; puede emitirse una lista por audiencia.*

## 2. Trabajo incompleto y productos no aceptados / Incomplete work and unaccepted products

| Producto o trabajo / Product or work | Estado / State | Recomendación / Recommendation | Destinatario / Addressee | Responsable propuesto / Proposed owner | Fecha / Date |
|---|---|---|---|---|---|
| {{inc_1}} | {{inc_estado_1}} | {{inc_rec_1}} | {{inc_dest_1}} | {{inc_resp_1}} | {{inc_fecha_1}} |

*Qué completar, abandonar o transferir a otro proyecto; en cierre prematuro incluye lo que debe dejarse en estado seguro.*

## 3. Issues abiertos / Open issues

| Id (I-nnn) / Id | Descripción / Description | Recomendación / Recommendation | Destinatario / Addressee | Responsable propuesto / Proposed owner | Fecha / Date |
|---|---|---|---|---|---|
| {{iss_id_1}} | {{iss_desc_1}} | {{iss_rec_1}} | {{iss_dest_1}} | {{iss_resp_1}} | {{iss_fecha_1}} |

*Issues que no se resolvieron en el proyecto, incluidas solicitudes de cambio no implementadas y off-specifications con concesión.*

## 4. Riesgos residuales transferidos / Residual risks transferred

| Id (R-nnn) / Id | Riesgo / Risk | Exposición actual / Current exposure | Recomendación / Recommendation | Destinatario / Addressee | Fecha de revisión / Review date |
|---|---|---|---|---|---|
| {{rsk_id_1}} | {{rsk_desc_1}} | {{rsk_exp_1}} | {{rsk_rec_1}} | {{rsk_dest_1}} | {{rsk_fecha_1}} |

*Riesgos que siguen vivos en operación; en riesgos.csv se cierran (`estado=cerrado`) con `notas=transferido a <destinatario>`; "transferido" no es un estado válido de riesgos.*

## 5. Obligaciones contractuales y de proveedores / Contractual and vendor obligations

| Contrato / Contract | Obligación / Obligation | Vigencia / Term | Destinatario / Addressee | Responsable propuesto / Proposed owner |
|---|---|---|---|---|
| {{ctr_1}} | {{ctr_oblig_1}} | {{ctr_vig_1}} | {{ctr_dest_1}} | {{ctr_resp_1}} |

*Garantías, soporte, licencias, pagos diferidos, disputas no resueltas.*

## 6. Operación, mantenimiento y mejoras sugeridas / Operations, maintenance and suggested improvements

| Tema / Topic | Recomendación / Recommendation | Destinatario / Addressee | Responsable propuesto / Proposed owner | Fecha / Date |
|---|---|---|---|---|
| {{op_1}} | {{op_rec_1}} | {{op_dest_1}} | {{op_resp_1}} | {{op_fecha_1}} |

*Mejoras del producto no incluidas en el alcance, formación adicional, monitoreo recomendado, decisiones que el negocio debe tomar.*

## 7. Revisiones de beneficios post-proyecto / Post-project benefit reviews

| Beneficio / Benefit | Cómo se medirá / How it will be measured | Dueño del negocio / Business owner | Fecha de revisión / Review date |
|---|---|---|---|
| {{ben_1}} | {{ben_metodo_1}} | {{ben_dueno_1}} | {{ben_fecha_1}} |

*Copia del enfoque de gestión de beneficios; la ejecución corresponde al negocio o al programa.*

## 8. Forma de seguimiento / Follow-up mechanism

{{mecanismo_seguimiento}}
*Quién consolida estas recomendaciones tras el cierre (PMO, área de operaciones, programa), en qué herramienta y con qué frecuencia se revisan.*

## Lista de verificación / Checklist
- [ ] Cada recomendación con destinatario, responsable propuesto y fecha.
- [ ] Todos los issues abiertos y riesgos residuales del registro aparecen aquí o están cerrados.
- [ ] Productos no aceptados y trabajo incompleto declarados, no omitidos.
- [ ] Obligaciones contractuales posteriores con vigencia y dueño.
- [ ] Beneficios pendientes con método de medición, dueño del negocio y fecha.
- [ ] Mecanismo de seguimiento posterior identificado.
- [ ] Listas por audiencia emitidas en el formato que cada receptor necesita (según enfoque de comunicación).
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
