---
tipo: revision-calidad
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Revisión de calidad · Quality review — {{producto}} v{{version_producto}}

> Borrador generado con apoyo de IA; la estructura de roles y pasos es una propuesta del paquete compatible con el método. / AI-assisted draft; the role and step structure is a package proposal compatible with the method.

## 1. Identificación / Identification

**Producto y versión / Product and version:** {{producto}} v{{version_producto}}
*Nombre o id del producto tal como figura en el plan y en calidad.csv.*

**Actividad del registro de calidad / Quality register entry:** {{id_calidad}}
*Fila Q-nnn de calidad.csv que esta revisión ejecuta.*

**Descripción de producto / Product description:** {{ruta_descripcion}}
*Ruta de la descripción aprobada; los criterios de la sección 4 salen de ahí.*

**Paquete de trabajo / Work package:** {{id_paquete}}
*WP-nnn al que pertenece el producto.*

**Tipo de revisión / Review type:** {{tipo_revision}}
*Revisión de documento, de diseño, recorrido de código, revisión de iteración, inspección de entrega.*

## 2. Roles / Roles

| Rol / Role | Nombre / Name | Independiente del productor / Independent of producer |
|---|---|---|
| Presidente / Chair | {{presidente}} | {{indep_presidente}} |
| Presentador / Presenter | {{presentador}} | no aplica (productor o representante) |
| Revisor / Reviewer | {{revisor_1}} | {{indep_revisor_1}} |
| Revisor / Reviewer | {{revisor_2}} | {{indep_revisor_2}} |
| Administrador / Administrator | {{administrador}} | {{indep_administrador}} |

*El presidente conduce y decide el resultado; el presentador explica el producto; los revisores evalúan contra criterios y deben ser independientes del productor (al menos uno del lado del usuario cuando el producto lo usará el negocio); el administrador registra observaciones y acciones.*

## 3. Preparación / Preparation

**Fecha de distribución / Distribution date:** {{fecha_distribucion}}
*Cuándo se entregó el producto y su descripción a los revisores.*

**Fecha de la reunión / Meeting date:** {{fecha_reunion}}
*Dejar tiempo suficiente entre distribución y reunión para una lectura real.*

**Material distribuido / Material distributed:** {{material}}
*Producto, descripción de producto, estándares aplicables, lista de verificación si existe.*

**Observaciones previas recibidas / Pre-meeting observations received:** {{observaciones_previas}}
*Cantidad por revisor; si alguno no envió, anotarlo.*

## 4. Criterios evaluados / Criteria assessed

| N.º / No. | Criterio o especificación / Criterion or specification | Prioridad / Priority | Cumple / Met | Evidencia / Evidence |
|---|---|---|---|---|
| 1 | {{criterio_1}} | {{prioridad_1}} | {{cumple_1}} | {{evidencia_1}} |
| 2 | {{criterio_2}} | {{prioridad_2}} | {{cumple_2}} | {{evidencia_2}} |

*Copiar los criterios de la descripción de producto, con su prioridad; marcar sí / no / parcial y señalar dónde se verificó. No se agregan criterios nuevos aquí.*

## 5. Observaciones y acciones / Observations and actions

| Id / Id | Observación / Observation | Criterio / Criterion | Clase / Class | Acción acordada / Agreed action | Responsable / Owner | Fecha límite / Due date | Estado / Status |
|---|---|---|---|---|---|---|---|
| {{obs_id_1}} | {{obs_1}} | {{obs_criterio_1}} | {{obs_clase_1}} | {{obs_accion_1}} | {{obs_resp_1}} | {{obs_fecha_1}} | {{obs_estado_1}} |

*Clase: mayor (impide cumplir un criterio), menor (corrección sin impacto en el criterio), observación (sugerencia). Solo se registran observaciones referidas a criterios; las preferencias personales no cuentan.*

## 6. Resultado / Outcome

**Resultado / Result:** {{resultado}}
*`aprobado` · `aprobado-con-observaciones` (acciones menores) · `rechazado` (repetir): mismos valores que `calidad.csv.resultado`. Lo decide el presidente al cierre de la reunión.*

**Justificación / Rationale:** {{justificacion}}
*Qué criterios mayores no se cumplen, si los hay, y por qué el resultado es ese.*

**Fecha prevista de nueva revisión / Planned re-review date:** {{fecha_nueva_revision}}
*Solo si el resultado es `rechazado` y es razonable esperar que apruebe (nueva fila Q-nnn `planificada`); si no, derivar a issues como `fuera-especificacion`.*

**Off-specification planteado / Off-specification raised:** {{off_spec}}
*Id I-nnn si el producto no puede alcanzar su especificación dentro de la tolerancia de calidad.*

## 7. Seguimiento / Follow-up

**Acciones cerradas verificadas por / Actions closed verified by:** {{verifica_cierre}}
*El presidente (o quien delegue) confirma el cierre de todas las acciones mayores antes de pasar a aceptación.*

**Actualización de calidad.csv / Quality register update:** {{actualizacion_registro}}
*fecha_real, resultado, `estado=completada` y ruta de este acta en la fila Q-nnn; acciones con responsable y fecha en acciones.csv (`A-###`, origen Q-nnn).*

**Lecciones identificadas / Lessons identified:** {{lecciones}}
*Ids L-nnn de lecciones.csv (criterios ambiguos, defectos repetidos, carga de revisores).*

## Lista de verificación / Checklist
- [ ] Revisores independientes del productor; roles completos.
- [ ] Producto y descripción distribuidos con antelación; observaciones previas recogidas.
- [ ] Criterios tomados de la descripción de producto, sin criterios nuevos.
- [ ] Cada observación clasificada, con acción, responsable, fecha y estado.
- [ ] Resultado decidido por el presidente y justificado.
- [ ] Fila Q-nnn actualizada con fecha real, resultado y evidencia.
- [ ] Off-specification registrado en issues.csv si corresponde.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
