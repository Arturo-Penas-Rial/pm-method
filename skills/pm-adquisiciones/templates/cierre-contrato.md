---
tipo: cierre-contrato
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Informe de cierre de contrato · Contract closeout report — {{id_contrato}} {{proveedor}}

> Borrador generado con apoyo de IA. El contrato no se considera cerrado hasta cumplir las tres condiciones de la sección 2 y contar con la firma de la sección 7. / AI-assisted draft. The contract is not closed until the three conditions in section 2 are met and section 7 is signed.

## 1. Cabecera / Header

**Contrato / Contract:** {{id_contrato}}
*Identificador, objeto y tipo de contrato.*

**Proveedor / Vendor:** {{proveedor}}
*Razón social y representante.*

**Gestor del proyecto / Project manager:** {{gestor_proyecto}}
*Quien prepara el informe.*

**Representante de compras o contratos / Procurement or contracts representative:** {{representante_compras}}
*Quien valida el cierre desde la organización.*

**Monto original y final / Original and final amount:** {{monto_original}} → {{monto_final}}
*Con fuente (contrato, cambios aprobados, facturas).*

**Período / Period:** {{fecha_inicio}} — {{fecha_fin}}
*Fechas contractuales de inicio y finalización.*

## 2. Condiciones de cierre / Closure conditions

| Condición / Condition | Cumplida / Met | Evidencia / Evidence |
|---|---|---|
| Todas las disputas resueltas / All disputes resolved | {{cond_disputas}} | {{ev_disputas}} |
| Producto o resultado formalmente aceptado (aceptación contractual) / Product formally accepted (contractual acceptance) | {{cond_aceptacion}} | {{ev_aceptacion}} |
| Pagos finales efectuados o contrato terminado formalmente / Final payments made or contract formally terminated | {{cond_pagos}} | {{ev_pagos}} |

*Las tres deben ser "sí" con evidencia (registro de aceptación, comprobante, acta). Si alguna es "no", el contrato sigue abierto y se registra en recomendaciones de seguimiento.*

## 3. Obligaciones posteriores / Post-closure obligations

| Obligación / Obligation | Vigencia / Term | Responsable / Owner | Dónde se transfiere / Transferred to |
|---|---|---|---|
| {{obligacion_1}} | {{vigencia_1}} | {{resp_oblig_1}} | {{transferencia_1}} |

*Garantías, soporte, licencias, confidencialidad, transferencia de conocimiento pendiente; se entregan a operaciones o al negocio con dueño.*

## 4. Desempeño del proveedor / Vendor performance

| Dimensión / Dimension | Funcionó bien / What worked well | Puede mejorar / What can be improved | Calificación 1–5 / Rating |
|---|---|---|---|
| Alcance / Scope | {{alcance_bien}} | {{alcance_mejorar}} | {{cal_alcance}} |
| Calidad / Quality | {{calidad_bien}} | {{calidad_mejorar}} | {{cal_calidad}} |
| Cronograma / Schedule | {{cronograma_bien}} | {{cronograma_mejorar}} | {{cal_cronograma}} |
| Costo / Cost | {{costo_bien}} | {{costo_mejorar}} | {{cal_costo}} |
| Otros / Other | {{otros_bien}} | {{otros_mejorar}} | {{cal_otros}} |

*Base para el repositorio de evaluación de proveedores; coherente con la auditoría de adquisiciones si la hubo.*

## 5. Historial de cambios del contrato / Record of contract changes

| Id (C-nnn) / Id | Descripción / Description | Impacto / Impact | Fecha de aprobación / Approval date | Aprobado por / Approved by |
|---|---|---|---|---|
| {{cambio_id_1}} | {{cambio_desc_1}} | {{cambio_impacto_1}} | {{cambio_fecha_1}} | {{cambio_por_1}} |

*Debe coincidir con cambios.csv filtrado por este contrato.*

## 6. Historial de disputas / Record of contract disputes

| Id / Id | Descripción / Description | Método de resolución / Resolution method | Resolución / Resolution | Fecha de resolución / Resolution date |
|---|---|---|---|---|
| {{disputa_id_1}} | {{disputa_desc_1}} | {{disputa_metodo_1}} | {{disputa_resolucion_1}} | {{disputa_fecha_1}} |

*Negociación, mediación, arbitraje u otro; toda disputa con resolución y fecha.*

## 7. Formalización / Formalization

| Campo / Field | Valor / Value |
|---|---|
| Fecha de finalización del contrato / Contract completion date | {{fecha_finalizacion}} |
| Fecha del pago final / Final payment date | {{fecha_pago_final}} |
| Firmado por / Signed off by | {{firmado_por}} |
| Rol / Role | {{rol_firmante}} |
| Fecha de firma / Sign-off date | {{fecha_firma}} |
| Decisión (D-nnn) / Decision log entry | {{id_decision}} |

*Autoridad contractual según la política (ejecutivo, compras, proveedor sénior). Sin firma, el informe sigue en borrador.*

## 8. Lecciones y destino de la información / Lessons and records disposition

**Lecciones registradas (L-nnn) / Lessons recorded:** {{lecciones}}
*Sobre el contrato, el proveedor y el proceso de compras.*

**Archivo de la documentación contractual / Contract documentation archive:** {{archivo}}
*Dónde queda el contrato, correspondencia, informes, aceptaciones y pagos para auditoría futura.*

**Repositorio de evaluación de proveedores / Vendor evaluation repository:** {{repositorio_proveedores}}
*Dónde consultará compras esta evaluación en futuras licitaciones.*

## Lista de verificación / Checklist
- [ ] Las tres condiciones de cierre cumplidas y con evidencia.
- [ ] Obligaciones posteriores (garantías, soporte, licencias) con vigencia y dueño.
- [ ] Desempeño del proveedor en las cinco dimensiones, con calificación.
- [ ] Cambios listados coinciden con cambios.csv; disputas con resolución y fecha.
- [ ] Fechas de finalización, pago final y firma completas; D-nnn registrada.
- [ ] Lecciones en lecciones.csv; evaluación guardada donde compras la consulte.
- [ ] Informado a pm-cierre-proyecto para el informe de fin de proyecto.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
