---
tipo: plan-gestion-recursos-adquisiciones
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de gestión de recursos y adquisiciones · Resource and procurement management plan — {{proyecto}}

> Cómo se estiman, obtienen, desarrollan y liberan las personas y los recursos físicos, y cómo se contratan y controlan los proveedores. Lo prepara el gestor con el proveedor sénior; lo aprueba el ejecutivo. / How people, physical resources and suppliers are planned and managed.

**Versión mínima / Minimal version:** {{version_minima}}
*`sí`: secciones 1, 2 y 5 con la lista de proveedores y tipo de contrato.*

## 1. Estimación y obtención del equipo / Team estimation and acquisition

{{obtencion_equipo}}
*Cómo se estiman perfiles y cantidades (desde la WBS y las estimaciones), de dónde salen (internos, contratados), quién los asigna, con qué anticipación.*

## 2. Roles, autoridad y responsabilidad / Roles, authority and responsibility

| Rol / Role | Autoridad / Authority | Responsabilidad / Responsibility | Competencias / Skills | Cantidad / Count |
|---|---|---|---|---|
| {{rol1}} | {{aut1}} | {{resp1}} | {{comp1}} | {{cant1}} |
| {{rol2}} | {{aut2}} | {{resp2}} | {{comp2}} | {{cant2}} |

*Coherente con la estructura organizativa y la RACI de `pm-organizacion-roles`.*

## 3. Desarrollo y liberación del equipo / Team development and release

{{desarrollo_equipo}}
*Formación necesaria, team charter, reconocimiento, evaluación del desempeño del equipo, cómo y cuándo se libera a las personas.*

## 4. Recursos físicos / Physical resources

{{recursos_fisicos}}
*Equipos, materiales, espacios, licencias: cómo se estiman, piden, controlan y devuelven.*

## 5. Adquisiciones / Procurement

| Qué se contrata / Item | Motivo (make-or-buy) / Rationale | Tipo de contrato / Contract type | Método de selección / Selection | Fecha requerida / Needed by | Responsable / Owner |
|---|---|---|---|---|---|
| {{adq1}} | {{mot1}} | {{tipo1}} | {{sel1}} | {{fecha1}} | {{dueno1}} |

*Detalle de estrategia, criterios y seguimiento en `pm-adquisiciones`.*

## 6. Integración de proveedores en el control / Supplier integration

{{integracion_proveedores}}
*Cómo encajan los proveedores en el método: sus entregables como paquetes de trabajo, sus checkpoints, sus riesgos en el registro del proyecto, sus cambios por el procedimiento de cambios, su calidad en el registro de calidad.*

## 7. Métricas / Metrics

{{metricas}}
*Utilización del equipo, rotación, cumplimiento de proveedores (plazo, calidad, costo), reclamaciones abiertas.*

## 8. Consideraciones legales / Legal considerations

{{legales}}
*Jurisdicción, moneda, normas de contratación pública si aplican, confidencialidad, propiedad intelectual.*

## Lista de verificación / Checklist
- [ ] Perfiles y cantidades derivados de la WBS y las estimaciones.
- [ ] Roles con autoridad y responsabilidad coherentes con la RACI.
- [ ] Cada adquisición con motivo, tipo de contrato y responsable.
- [ ] Proveedores integrados en paquetes de trabajo, riesgos, cambios y calidad.
- [ ] Aprobado por el ejecutivo.
