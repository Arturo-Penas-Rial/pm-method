---
tipo: plan-proyecto
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de proyecto · Project plan

> Borrador generado con asistencia de IA. Línea base al aprobarse (autorizar-proyecto); se actualiza y vuelve a ser línea base en cada límite de etapa con aprobación de la junta. / AI-assisted draft; baselined at project authorization and re-baselined at stage boundaries.

**Proyecto / Project:** {{proyecto}} · **Gestor / Project manager:** {{gestor}} · **Ejecutivo / Executive:** {{ejecutivo}}
*Del brief y de estado.json.roles.*

**Enfoque de entrega / Delivery approach:** {{enfoque_entrega}}
*Predictivo, ágil o híbrido; el ciclo de vida por etapas se mantiene en todos los casos.*

**Versión que reemplaza / Supersedes version:** {{version_anterior}} · **Motivo / Reason:** {{motivo_version}}
*Inicio, fin de etapa N, plan de excepción aprobado.*

## 1. Alcance del plan / Plan scope
{{alcance}}
*Todo el ciclo de vida del proyecto; referencia a la descripción del producto del proyecto y al enunciado del alcance.*

## 2. Dependencias externas / External dependencies
| Dependencia / Dependency | Proyecto u organización / Project or organization | Fecha requerida / Needed by | Riesgo / Risk |
|---|---|---|---|
| {{dependencia}} | {{origen}} | {{fecha}} | R-{{id}} |
*Incluye dependencias hacia y desde otros proyectos del programa.*

## 3. Supuestos y prerrequisitos / Assumptions and prerequisites
- {{supuesto}} (S-{{id}})
*Base del plan; cada supuesto no validado es un riesgo.*

## 4. Lecciones incorporadas / Lessons incorporated
| Lección / Lesson | Origen / Source | Aplicación / Application |
|---|---|---|
| L-{{id}} | {{origen}} | {{aplicacion}} |
*De proyectos similares previos y, en versiones posteriores, de etapas anteriores.*

## 5. Productos a entregar / Products to be delivered
Referencias / References: `descripcion-producto-proyecto.md`, `pbs-wbs.md`, `flujo-productos.md`, `productos/`.
| Código / Code | Producto mayor / Major product | Etapa de entrega / Delivery stage | Criterio de aceptación principal / Main acceptance criterion |
|---|---|---|---|
| P-{{p}} | {{producto}} | {{etapa}} | {{criterio}} |
*Nivel de productos mayores; el detalle vive en las descripciones de producto.*

## 6. Trabajo a realizar / Work to be done
| Paquete de nivel superior / Top-level work package | Productos / Products | Equipo o proveedor / Team or supplier | Entrega / Delivery | Etapa / Stage |
|---|---|---|---|---|
| W-{{w}} | P-{{p}} | {{equipo}} | secuencial · iterativo | {{etapa}} |
*Nivel superior de la WBS; indicar si cada paquete se entrega de forma lineal o iterativa.*

## 7. Etapas y decisiones de la junta / Stages and board decisions
| Etapa / Stage | Nombre / Name | Inicio / Start | Fin / End | Productos clave / Key products | Puerta al final / Gate at end |
|---|---|---|---|---|---|
| 1 | Iniciación / Initiation | {{inicio_1}} | {{fin_1}} | PID, plan de proyecto, plan de la etapa 2 | autorizar-proyecto + autorizar-etapa |
| 2 | {{nombre_2}} | {{inicio_2}} | {{fin_2}} | {{productos}} | autorizar-etapa |
| {{n}} | {{nombre}} | {{inicio}} | {{fin}} | {{productos}} | autorizar-etapa · autorizar-cierre (última) |
*Numeración del paquete: 1 = iniciación; 2…n = entrega (el arranque SU es pre-proyecto, no es etapa). Las etapas no se solapan; su número y longitud se justifican por complejidad, riesgo, horizonte de planificación, decisiones clave y eventos externos. Justificación / Rationale: {{justificacion_etapas}}*

## 8. Cronograma de alto nivel / High-level schedule
```mermaid
gantt
    dateFormat YYYY-MM-DD
    title {{proyecto}} · etapas
    section Etapas / Stages
    Etapa 1 Iniciación :e1, {{inicio_1}}, {{fin_1}}
    Etapa 2 {{nombre_2}} :e2, after e1, {{dur_2}}d
    Etapa 3 {{nombre_3}} :e3, after e2, {{dur_3}}d
    section Puertas / Gates
    Autorizar proyecto y etapa 2 :milestone, g2, {{fin_1}}, 0d
    Autorizar etapa 3 :milestone, g3, after e2, 0d
```
*Semanas o meses; detalle en cronograma.md. Con integración de diagramas, pm-visuales puede producir la hoja de ruta gráfica.*

## 9. Presupuesto / Budget
| Componente / Component | Importe / Amount |
|---|---|
| Σ etapas (estimación + gestión) / Σ stages | {{suma_etapas}} |
| Presupuesto de riesgo / Risk budget | {{riesgo}} |
| Presupuesto de cambio / Change budget | {{cambio}} |
| **Línea base de costo / Cost baseline** | **{{linea_base}}** |
| Reserva de gestión / Management reserve | {{reserva_gestion}} |
| **Presupuesto total / Total budget** | **{{bac}}** |
*Detalle en presupuesto.md y linea-base-costo.csv; coincide con el business case o se explica la diferencia.*

## 10. Metas y tolerancias del proyecto / Project targets and tolerances
| Dimensión / Dimension | Meta / Target | Tolerancia de proyecto / Project tolerance | Fuente / Source |
|---|---|---|---|
| Tiempo / Time | {{meta}} | {{tol}} | mandato · capa de negocio |
| Costo / Cost | {{meta}} | {{tol}} | |
| Alcance / Scope | {{meta}} | {{tol}} | |
| Calidad / Quality | {{meta}} | {{tol}} | |
| Beneficios / Benefits | {{meta}} | {{tol}} | |
| Riesgo / Risk | {{meta}} | {{tol}} | |
| Sostenibilidad / Sustainability | {{meta}} | {{tol}} | |
*Las tolerancias de etapa se reparten dentro de estas; restricción dominante: {{restriccion_dominante}}.*

## 11. Monitoreo, control y reporte / Monitoring, control and reporting
{{controles}}
*Resumen de los controles del PID: frecuencias de highlight, umbrales, procedimiento de excepción, revisiones de fin de etapa, uso de EVM si aplica.*

## 12. Personas y recursos comprometidos / Committed people and resources
| Recurso / Resource | Tipo de habilidad / Skill type | Cantidad / Quantity | Período / Period | Comprometido por / Committed by |
|---|---|---|---|---|
| {{recurso}} | {{habilidad}} | {{cantidad}} | {{periodo}} | usuario sénior · proveedor sénior · ejecutivo |
*Nivel de tipo de habilidad; nombres en los planes de etapa.*

## 13. Transición a operación / Transition to operations
{{transicion}}
*Arreglos de soporte, acuerdos de servicio y formación para sostener los beneficios tras el cierre; incluir como productos si corresponde.*

## 14. Riesgos clave / Key risks
| ID | Riesgo / Risk | Respuesta / Response | Propietario / Owner |
|---|---|---|---|
| R-{{id}} | {{riesgo}} | {{respuesta}} | {{propietario}} |
*Los que afectan al plan en su conjunto; detalle en riesgos.csv.*

## 15. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Brief, business case, enfoques, registros; puntos [por confirmar].*

## Lista de verificación / Checklist
- [ ] Composición completa (alcance, dependencias, supuestos, lecciones, productos, trabajo, presupuesto, cronograma, tolerancias, controles).
- [ ] Etapas justificadas, sin solapamiento, con puerta al final de cada una.
- [ ] Tolerancias de proyecto en las siete dimensiones; restricción dominante declarada.
- [ ] Costos y fechas coherentes con el business case.
- [ ] Recursos comprometidos por los roles de la junta.
- [ ] Transición a operación considerada.
- [ ] Riesgos analizados; plan tratado como borrador hasta decidir respuestas.
- [ ] Solicitud de puerta autorizar-proyecto preparada para pm-director.
