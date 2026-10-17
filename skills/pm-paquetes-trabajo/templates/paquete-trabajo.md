---
tipo: descripcion-paquete-trabajo
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
estado_paquete: "{{estado_paquete}}"
---

# Descripción de paquete de trabajo · Work package description — {{id_paquete}} {{nombre_paquete}}

> Borrador generado con apoyo de IA; cifras y nombres sin fuente aparecen como `[por confirmar]`. / AI-assisted draft; unsourced figures are marked `[por confirmar]`.

## 1. Identificación / Identification

**Identificador / Identifier:** {{id_paquete}}
*Código único, p. ej. WP-003; coincide con la clave `WP-003` en estado.json.artefactos.*

**Estado del paquete / Package status:** {{estado_paquete}}
*autorizado, en-ejecucion, en-verificacion, completado o suspendido. Vive aquí (y en el frontmatter), respaldado por las filas Q-nnn de calidad.csv; estado.json solo guarda el estado del documento (borrador, en-revision, aprobado, obsoleto).*

**Etapa y plan de referencia / Stage and parent plan:** {{etapa}} — {{ruta_plan_etapa}}
*Número y nombre de la etapa de gestión y enlace al plan de etapa (o plan de excepción) que autoriza este trabajo.*

**Gestor de equipo o persona autorizada / Team manager or authorized person:** {{gestor_equipo}}
*Quien responde por el paquete ante el gestor del proyecto; si es proveedor externo, indicar empresa y referencia de contrato.*

**Gestor del proyecto / Project manager:** {{gestor_proyecto}}
*Quien autoriza el paquete y recibe los checkpoints.*

**Enfoque de entrega / Delivery approach:** {{enfoque_entrega}}
*predictivo, ágil (iteración como paquete) o híbrido; condiciona las secciones 3, 7 y 8.*

## 2. Descripción del trabajo / Work description

**Enunciado del trabajo / Statement of work:**
{{enunciado_trabajo}}
*Qué se va a hacer y para qué, en dos o tres frases; sin repetir las descripciones de producto.*

**Fragmento de PBS/WBS cubierto / PBS/WBS fragment covered:**
{{fragmento_wbs}}
*Lista o diagrama de los nodos de la estructura de productos que este paquete produce; sin solapes con otros paquetes.*

## 3. Productos del paquete / Products in scope

| Id producto / Product id | Producto / Product | Descripción de producto (ruta) / Product description (path) | Criterios de aceptación clave / Key acceptance criteria | Autoridad de aceptación / Acceptance authority |
|---|---|---|---|---|
| {{id_producto_1}} | {{producto_1}} | {{ruta_descripcion_1}} | {{criterios_1}} | {{aprobador_1}} |
| {{id_producto_2}} | {{producto_2}} | {{ruta_descripcion_2}} | {{criterios_2}} | {{aprobador_2}} |

*Un renglón por producto o subproducto; los criterios se copian de la descripción de producto aprobada, no se inventan aquí. En ágil, cada ítem de backlog comprometido ocupa un renglón y su definición de hecho actúa como criterio.*

## 4. Técnicas, procedimientos y estándares / Techniques, procedures and standards

{{tecnicas_procedimientos}}
*Métodos de desarrollo obligatorios, estándares corporativos o regulatorios, herramientas, repositorios y convenciones que el equipo debe seguir.*

## 5. Interfaces y dependencias / Interfaces and dependencies

| Con quién / With whom | Qué recibe este paquete / Inputs received | Qué entrega / Outputs delivered | Fecha o hito / Date or milestone |
|---|---|---|---|
| {{interfaz_1}} | {{recibe_1}} | {{entrega_1}} | {{fecha_interfaz_1}} |

*Otros paquetes, equipos, proveedores u operaciones con los que hay que coordinar; incluir dependencias con trabajo fuera del alcance del proyecto y quién lo financia.*

## 6. Control de cambios y configuración / Change and configuration control

{{control_cambios}}
*Cómo se protegen las líneas base dentro del paquete: qué puede decidir el equipo por sí mismo, qué requiere solicitud de cambio, cómo se versionan los productos.*

## 7. Restricciones / Constraints

{{restricciones}}
*Horas o presupuesto autorizado, ventanas de trabajo, seguridad, acceso a instalaciones o datos, requisitos de sostenibilidad y de salud del equipo.*

## 8. Monitoreo, control y reporte / Monitoring, control and reporting

**Frecuencia del checkpoint / Checkpoint frequency:** {{frecuencia_checkpoint}}
*Semanal, quincenal o por iteración; en ágil puede ser consulta "pull" del tablero.*

**Formato / Format:** {{formato_checkpoint}}
*Documento, correo, reunión diaria con el gestor del proyecto, tablero Kanban o burn-down.*

**Qué se informa / What is reported:** {{contenido_checkpoint}}
*Productos en curso y completados, actividades de calidad hechas, pronóstico contra tolerancias, issues, riesgos y lecciones.*

**Cómo se plantean issues y riesgos / How issues and risks are raised:** {{procedimiento_issues}}
*Canal y plazo para avisar al gestor del proyecto cuando se prevé salir de tolerancia o aparece un riesgo nuevo.*

## 9. Objetivos y tolerancias del paquete / Targets and tolerances

| Dimensión / Dimension | Objetivo / Target | Tolerancia / Tolerance | Derivada de la etapa / Derived from stage |
|---|---|---|---|
| Tiempo / Time | {{objetivo_tiempo}} | {{tolerancia_tiempo}} | {{tolerancia_etapa_tiempo}} |
| Costo o esfuerzo / Cost or effort | {{objetivo_costo}} | {{tolerancia_costo}} | {{tolerancia_etapa_costo}} |
| Alcance / Scope | {{objetivo_alcance}} | {{tolerancia_alcance}} | {{tolerancia_etapa_alcance}} |
| Calidad / Quality | {{objetivo_calidad}} | {{tolerancia_calidad}} | {{tolerancia_etapa_calidad}} |
| Riesgo / Risk | {{objetivo_riesgo}} | {{tolerancia_riesgo}} | {{tolerancia_etapa_riesgo}} |
| Sostenibilidad / Sustainability | {{objetivo_sostenibilidad}} | {{tolerancia_sostenibilidad}} | {{tolerancia_etapa_sostenibilidad}} |

*Las tolerancias del paquete caben dentro de las de la etapa; dejar la última columna para mostrar el reparto. En ágil: tiempo y costo fijos, alcance con tolerancia amplia (imprescindibles vs. deseables).*

## 10. Plan de equipo / Team plan

{{plan_equipo}}
*Cronograma o extracto de hitos, recursos, actividades de calidad y riesgos del paquete; en ágil, el backlog de la iteración; con proveedor externo, puede ser solo el extracto de hitos.*

## 11. Aprobación de productos / Product approval

{{procedimiento_aprobacion}}
*Quién aprueba cada producto terminado (según la descripción de producto), con qué evidencia y cómo se registra en el registro de productos y en calidad.csv.*

## 12. Referencias / References

{{referencias}}
*Plan de etapa, enfoques de gestión (calidad, cambios, comercial), contrato si aplica, descripciones de producto, lecciones previas incorporadas.*

## 13. Acuerdo / Agreement

| Acto / Act | Nombre / Name | Rol / Role | Fecha / Date | Evidencia / Evidence |
|---|---|---|---|---|
| Autorización / Authorization | {{autoriza_nombre}} | Gestor del proyecto | {{fecha_autorizacion}} | {{id_decision_autorizacion}} |
| Aceptación / Acceptance | {{acepta_nombre}} | Gestor de equipo | {{fecha_aceptacion}} | {{id_decision_aceptacion}} |
| Notificación de finalización / Completion notice | {{notifica_nombre}} | Gestor de equipo | {{fecha_finalizacion}} | {{ruta_checkpoint_final}} |
| Recepción del paquete / Package received | {{recibe_nombre}} | Gestor del proyecto | {{fecha_recepcion}} | {{id_decision_recepcion}} |

*Sin la primera y la segunda fila el trabajo no empieza; sin las dos últimas el paquete no está completo. Referenciar las filas D-nnn de decisiones.csv.*

## Lista de verificación / Checklist
- [ ] Plan de etapa aprobado y referenciado.
- [ ] Cada producto tiene descripción aprobada con productor, revisor independiente y autoridad de aceptación.
- [ ] Criterios de aceptación copiados de las descripciones de producto.
- [ ] Tolerancias del paquete contenidas en las de la etapa y reparto explicado.
- [ ] Interfaces y dependencias listadas; sin solape con otros paquetes.
- [ ] Frecuencia y formato de checkpoint fijados; procedimiento para plantear issues.
- [ ] Actividades de calidad dadas de alta en calidad.csv.
- [ ] Autorización y aceptación firmadas y registradas en decisiones.csv.
- [ ] `estado_paquete` actualizado en cada cambio de situación; `completado` solo con actividades de calidad `completada` y recepción registrada.
- [ ] Si hay proveedor externo: paquete coherente con el contrato.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
