---
tipo: estrategia-adquisiciones
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Estrategia de adquisiciones · Procurement strategy — {{id_adquisicion}} {{nombre_adquisicion}}

> Borrador generado con apoyo de IA; no sustituye la revisión de compras ni de legal. / AI-assisted draft; it does not replace procurement or legal review.

**Momento de decisión / Decision point:** {{momento}}
*Iniciación (plan de proyecto) o plan de la etapa {{n}}; la estrategia se aprueba con ese plan, antes de ejecutar. Archivo en 02-planificacion/adquisiciones/.*

**Paquetes de trabajo afectados / Work packages concerned:** {{paquetes}}
*Códigos W-x.y (o épicas PB-### en ágil) que ejecutará el proveedor; su responsable en el diccionario de la WBS será el proveedor sénior o el contratista.*

**Monto estimado / Estimated amount:** {{monto_estimado}} {{moneda}} · **Base / Basis:** {{base_monto}}
*De la hoja de costeo o de una cotización/RFI con fecha; incluido en el BAC como estimación base del paquete. Sin fuente: [por confirmar] / [to be confirmed].*

## 1. Análisis de hacer o comprar / Make-or-buy analysis

**Alcance a adquirir / Scope to procure:** {{alcance}}
*Productos o servicios concretos, con referencia a sus descripciones de producto o enunciado del trabajo.*

| Factor / Factor | Hacer / Make | Comprar / Buy |
|---|---|---|
| Costo total (incluida gestión del contrato) / Total cost (incl. contract management) | {{costo_hacer}} | {{costo_comprar}} |
| Capacidad y habilidades disponibles / Available capacity and skills | {{capacidad_hacer}} | {{capacidad_comprar}} |
| Necesidad de experiencia especializada o independiente / Need for specialized or independent expertise | {{experiencia_hacer}} | {{experiencia_comprar}} |
| Impacto en plantilla permanente / Impact on permanent staff | {{plantilla_hacer}} | {{plantilla_comprar}} |
| Riesgos principales / Main risks | {{riesgos_hacer}} | {{riesgos_comprar}} |
| Plazo / Lead time | {{plazo_hacer}} | {{plazo_comprar}} |

*Comparar opciones completas, no precio de compra contra salario interno. Cifras sin fuente: `[por confirmar]`.*

**Técnica financiera aplicada y supuestos / Financial technique and assumptions:** {{tecnica_financiera}}
*Costo-beneficio, VAN, recuperación u otra; declarar tasa, horizonte y supuestos.*

**Decisión y justificación / Decision and rationale:** {{decision_make_or_buy}}
*Hacer, comprar o mixto; id D-nnn de decisiones.csv y quién decidió.*

## 2. Método de entrega / Delivery method

**Modalidad / Modality:** {{metodo_entrega}}
*Proveedor único sin subcontratación; con subcontratación permitida; sociedad conjunta; proveedor como representante; llave en mano, diseño-construcción u otra modalidad sectorial; entrega integrada.*

**Justificación / Rationale:** {{justificacion_metodo}}
*Por qué esta modalidad encaja con el alcance, el riesgo y la capacidad del comprador.*

## 3. Tipo de contrato y asignación de riesgo / Contract type and risk allocation

**Tipo / Type:** {{tipo_contrato}}
*Precio fijo cerrado, precio fijo con incentivo o con ajuste, costos reembolsables (honorario fijo, con incentivo, por premio), tiempo y materiales con tope, costo objetivo, híbrido, contratación ágil por iteración.*

**Quién asume el riesgo de costo / Who bears cost risk:** {{riesgo_costo}}
*Vendedor, comprador o compartido; coherente con el grado de definición del alcance.*

**Coherencia con la definición del alcance / Fit with scope definition:** {{coherencia_alcance}}
*Alcance claro → precio fijo; incierto → reembolsable o T&M con tope. Señalar aquí la alerta si se pide precio fijo con alcance indefinido.*

**Incentivos o premios / Incentives or awards:** {{incentivos}}
*Monto o fórmula.*

**Criterios del incentivo / Incentive criteria:** {{criterios_incentivo}}
*Condición medible y fecha de medición.*

**Visión del contratista / Contractor's view:** {{vision_contratista}}
*Qué gana y qué arriesga el proveedor con esta estructura; buscar ganar-ganar.*

## 4. Ciclo de vida de la adquisición / Procurement life cycle

| Fase / Phase | Criterios de entrada / Entry criteria | Entregables o hitos / Deliverables or milestones | Criterios de salida / Exit criteria | Transferencia de conocimiento / Knowledge transfer | Fecha prevista / Planned date |
|---|---|---|---|---|---|
| {{fase_1}} | {{entrada_1}} | {{hitos_1}} | {{salida_1}} | {{transferencia_1}} | {{fecha_fase_1}} |
| {{fase_2}} | {{entrada_2}} | {{hitos_2}} | {{salida_2}} | {{transferencia_2}} | {{fecha_fase_2}} |

*Fases de la adquisición (p. ej. licitación, diseño, construcción, transición) alineadas con las etapas de gestión; la transferencia de conocimiento se planifica desde el inicio.*

## 5. Proceso de licitación / Bidding process

**Documento de licitación / Bid document:** {{tipo_documento}}
*RFI (conocer el mercado), RFP (que el proveedor proponga la solución), RFQ (el precio decide).*

**Método de selección / Selection method:** {{metodo_seleccion}}
*Menor costo, solo calificaciones, mayor puntaje técnico, calidad y costo, fuente única justificada, presupuesto fijo. Se fija aquí y se publica en los documentos; no se cambia tras ver ofertas.*

**Calendario / Timeline:** {{calendario_licitacion}}
*Publicación, consultas, conferencia de oferentes, cierre, evaluación, adjudicación, firma.*

**Oferentes potenciales / Potential bidders:** {{oferentes}}
*Resultado de investigación de mercado o RFI; `[por confirmar]` si no se verificó.*

## 6. Control del contrato / Contract control

**Indicadores de desempeño / Performance indicators:** {{kpis}}
*Qué se mide por período (entregas, defectos, plazos, respuesta).*

**Hitos de pago / Payment milestones:** {{hitos_pago}}
*Vinculados a aceptaciones, no a fechas de calendario.*

**Mecanismo de cambio contractual / Contract change mechanism:** {{mecanismo_cambio}}
*Cómo se solicita, evalúa y aprueba un cambio; enlace con cambios.csv.*

**Frecuencia del informe de estado del contratista / Contractor status report frequency:** {{frecuencia_informe}}
*Período y formato.*

**Derechos de acceso, inspección y auditoría / Access, inspection and audit rights:** {{derechos_inspeccion}}
*Acceso a instalaciones, pruebas independientes, transparencia del control de calidad del proveedor.*

**Resolución de disputas / Dispute resolution:** {{resolucion_disputas}}
*Escalado contractual: negociación, mediación, arbitraje u otros; jurisdicción.*

## 7. Garantías, retenciones y seguros / Guarantees, retentions and insurance

| Instrumento / Instrument | Monto o % / Amount or % | Vigencia / Validity | Condición de liberación / Release condition |
|---|---|---|---|
| Garantía de mantenimiento de oferta / Bid bond | {{garantia_oferta}} | {{vigencia_oferta}} | Firma del contrato o descarte de la oferta |
| Garantía de fiel cumplimiento / Performance bond | {{garantia_cumplimiento}} | {{vigencia_cumplimiento}} | Aceptación contractual del producto |
| Garantía de anticipo / Advance payment bond | {{garantia_anticipo}} | {{vigencia_anticipo}} | Amortización total del anticipo |
| Retención sobre pagos / Retention on payments | {{retencion_pct}} % | {{vigencia_retencion}} | Fin del plazo de garantía sin defectos abiertos |
*Montos y porcentajes según la política de compras o la norma aplicable; "no aplica" si la adquisición es menor.*

**Seguros exigidos / Required insurance:** {{seguros}}
*Responsabilidad civil, riesgos profesionales, todo riesgo de construcción, ciberriesgo u otros; montos mínimos y beneficiario.*

**Plazo de garantía del producto / Product warranty period:** {{plazo_garantia}}
*Desde la aceptación; qué cubre, tiempo de respuesta y quién lo gestiona tras el cierre del proyecto (anotar en el handover).*

## 8. Riesgos y cumplimiento / Risks and compliance

**Riesgos contractuales (R-nnn) / Contract risks:** {{riesgos_contractuales}}
*Ids en riesgos.csv (con impacto monetario; los altos, P×I ≥ 15, con respuesta y propietario).*

**Políticas y regulación aplicables / Applicable policies and regulation:** {{politicas}}
*Umbrales de compras, normas públicas, contenido local, sostenibilidad, protección de datos.*

**Participación de compras y legal / Procurement and legal involvement:** {{compras_legal}}
*Quién revisa y en qué momento.*

## 9. Aprobación / Approval

| Rol / Role | Nombre / Name | Decisión / Decision | Fecha / Date | D-nnn |
|---|---|---|---|---|
| {{aprobador_rol}} | {{aprobador_nombre}} | {{decision_aprobacion}} | {{fecha_aprobacion}} | {{id_decision}} |

*Aprobador según la política de la organización (compras, ejecutivo, junta); se aprueba con el plan (autorizar-proyecto / autorizar-etapa, registrada por pm-director) o con `estado.py aprobar estrategia-adquisiciones --por "<rol: nombre>"`. Sin aprobación, el documento sigue en borrador.*

## Lista de verificación / Checklist
- [ ] Análisis de hacer o comprar con costos totales y riesgos de ambas opciones; decisión registrada.
- [ ] Tipo de contrato coherente con la definición del alcance; alertas declaradas.
- [ ] Incentivos con criterio medible y fecha.
- [ ] Fases con criterios de entrada y salida verificables; transferencia de conocimiento prevista.
- [ ] Método de selección fijado antes de los documentos.
- [ ] Monto estimado con base y fuente; incluido en el presupuesto.
- [ ] Garantías, retenciones, seguros y plazo de garantía definidos o marcados "no aplica".
- [ ] Indicadores, hitos de pago y mecanismo de cambio definidos y enlazados al cronograma y presupuesto.
- [ ] Decidida en iniciación o plan de etapa, antes de la ejecución.
- [ ] Derechos de acceso, inspección y auditoría incluidos.
- [ ] Riesgos contractuales en riesgos.csv; compras y legal consultados.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]` / `[to be confirmed]`.
