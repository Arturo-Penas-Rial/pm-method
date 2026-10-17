---
tipo: plan-etapa
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de etapa · Stage plan

> Borrador generado con asistencia de IA. Línea base solo tras la puerta autorizar-etapa (o autorizar-inicio para la etapa de inicio). / AI-assisted draft; baseline only after the stage gate.

**Etapa / Stage:** {{numero_etapa}} · {{nombre_etapa}}
*Número y nombre: 1 = iniciación (archivo plan-etapa-1.md, puerta autorizar-inicio); 2…n = etapas de entrega (plan-etapa-<n>.md, puerta autorizar-etapa).*

**Inicio / Start:** {{fecha_inicio}} · **Fin previsto / Planned end:** {{fecha_fin}} · **Duración / Duration:** {{duracion}}
*Fechas del cronograma de etapa; coinciden con los hitos del plan de proyecto.*

**Gestor de proyecto / Project manager:** {{gestor}} · **Aprueba / Approved by:** junta de proyecto (ejecutivo)
*El ejecutivo fija las tolerancias de etapa y aprueba el plan.*

**Enfoque de entrega / Delivery approach:** {{enfoque_entrega}}
*Predictivo, ágil o híbrido; en ágil indicar número de iteraciones y backlog comprometido.*

## 1. Alcance de la etapa / Stage scope
{{alcance}}
*Qué productos e hitos del plan de proyecto cubre esta etapa y qué queda fuera; cada elemento rastrea a un elemento del plan de proyecto.*

## 2. Dependencias / Dependencies
| Dependencia / Dependency | Tipo / Type | Responsable / Owner | Fecha requerida / Needed by | Riesgo / Risk |
|---|---|---|---|---|
| {{dependencia}} | interna · externa | {{responsable}} | {{fecha}} | R-{{id}} |
*Del diagrama de flujo de productos; las externas van también al registro de riesgos.*

## 3. Supuestos y prerrequisitos / Assumptions and prerequisites
- {{supuesto}} (S-{{id}})
*Lo que debe mantenerse cierto para que el plan funcione; referenciar supuestos.csv.*

## 4. Lecciones incorporadas / Lessons incorporated
| Lección / Lesson | Origen / Source | Cómo se aplica en este plan / How it is applied |
|---|---|---|
| L-{{id}} | etapa anterior · proyecto previo · retrospectiva | {{aplicacion}} |
*Revisar lecciones.csv antes de planificar; indicar las que cambian el plan.*

## 5. Productos de la etapa / Stage products
| Código PBS / PBS code | Producto / Product | Descripción de producto / Product description | Productor / Producer | Aprobador / Approver | Fecha prevista / Planned date |
|---|---|---|---|---|---|
| P-{{p}} | {{producto}} | `productos/{{archivo}}.md` | {{productor}} | {{aprobador}} | {{fecha}} |
*Incluir intermedios y externos; PBS y flujo de la etapa en pbs-wbs-etapa-N.md y flujo-productos.md.*

## 6. Trabajo a realizar / Work to be done
| Paquete / Work package | Productos / Products | Equipo o proveedor / Team or supplier | Método / Method | Inicio / Start | Fin / End | Tolerancias del paquete / Package tolerances |
|---|---|---|---|---|---|---|
| W-{{w}} | P-{{p}} | {{equipo}} | secuencial · iterativo | {{inicio}} | {{fin}} | {{tolerancias_paquete}} |
*Todos los paquetes de la etapa, incluido el de gestión del proyecto; ninguno cruza el límite de etapa sin justificación.*

## 7. Cronograma / Schedule
Ver `02-planificacion/cronograma.md` (Gantt, camino crítico, hitos, reserva). Hitos clave / Key milestones:
| Hito / Milestone | Fecha / Date | Tipo / Type |
|---|---|---|
| {{hito}} | {{fecha}} | producto · puerta · compra |
*Nivel de detalle: días y personas por nombre.*

## 8. Presupuesto / Budget
| Componente / Component | Importe / Amount |
|---|---|
| Estimación de paquetes / Package estimates | {{estimacion}} |
| Costos de gestión / Management costs | {{gestion}} |
| Presupuesto de riesgo (contingencia) / Risk budget | {{riesgo}} |
| Presupuesto de cambio / Change budget | {{cambio}} |
| **Total etapa / Stage total** | **{{total}}** |
*Detalle en presupuesto.md; la tolerancia de costo se declara en la sección 9.*

## 9. Metas y tolerancias de la etapa / Stage targets and tolerances
| Dimensión / Dimension | Meta / Target | Tolerancia / Tolerance | Restricción dominante / Driving constraint |
|---|---|---|---|
| Tiempo / Time | {{meta_tiempo}} | {{tol_tiempo}} | sí · no |
| Costo / Cost | {{meta_costo}} | {{tol_costo}} | sí · no |
| Alcance / Scope | {{meta_alcance}} | {{tol_alcance}} (productos could/won't) | sí · no |
| Calidad / Quality | {{meta_calidad}} | {{tol_calidad}} | sí · no |
| Beneficios / Benefits | {{meta_beneficios}} | {{tol_beneficios}} | sí · no |
| Riesgo / Risk | {{meta_riesgo}} | {{tol_riesgo}} | sí · no |
| Sostenibilidad / Sustainability | {{meta_sost}} | {{tol_sost}} | sí · no |
*En unidades del objetivo; caben dentro de las tolerancias de proyecto; tras la aprobación, pm-director las registra con `estado.py tolerancia --nivel etapa ...` (autorizar-etapa vacía las de la etapa anterior).*

## 10. Monitoreo, control y reporte / Monitoring, control and reporting
- Informes de punto de control / Checkpoint reports: {{frecuencia_checkpoint}}
- Informes de destacados / Highlight reports: {{frecuencia_highlight}}
- Umbrales y procedimiento de excepción / Thresholds and exception procedure: {{procedimiento_excepcion}}
- Actividades de calidad planificadas / Planned quality activities: ver calidad.csv (Q-{{ids}})
- Revisiones de la junta / Board reviews: {{revisiones}}
*Cómo se vigila la etapa y quién recibe qué; coherente con los controles del PID.*

## 11. Riesgos e issues de la etapa / Stage risks and issues
| ID | Descripción / Description | Respuesta o decisión / Response or decision | Propietario / Owner |
|---|---|---|---|
| R-{{id}} / I-{{id}} | {{descripcion}} | {{respuesta}} | {{propietario}} |
*El plan sigue siendo borrador hasta decidir cómo se tratan los riesgos que contiene.*

## 12. Versión ágil (si aplica) / Agile version (if applicable)
- Iteraciones en la etapa / Iterations in the stage: {{n_iteraciones}} de {{duracion_iteracion}}
- Backlog comprometido / Committed backlog: PB-{{ids}} (Must de la etapa; Should/Could = tolerancia de alcance; ver backlog.csv y release-plan.md)
- Product owner / Product owner: {{product_owner}} (intercambia ítems dentro de la tolerancia de alcance; decisión nivel=product-owner)
- Definición de hecho / Definition of done: {{dod}}
*Las iteraciones son bloques del cronograma de etapa; la tolerancia de alcance es amplia y la de tiempo y costo, estrecha.*

## 13. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Documentos y registros consultados; puntos [por confirmar].*

## Lista de verificación / Checklist
- [ ] Todo producto y actividad rastrea al plan de proyecto.
- [ ] PBS, flujo y paquetes de la etapa sin vacíos ni solapamientos.
- [ ] Estimaciones con nivel de confianza; riesgos analizados y tratados.
- [ ] Siete tolerancias explícitas y dentro de las de proyecto.
- [ ] Dependencias externas identificadas y registradas.
- [ ] Lecciones incorporadas con ID.
- [ ] Controles y frecuencias de reporte definidos.
- [ ] Costo y fecha dentro de la tolerancia propuesta, o decisión de la junta preparada con opciones.
- [ ] Solicitud de puerta preparada para pm-director (autorizar-inicio para la etapa 1; autorizar-etapa para 2…n).
