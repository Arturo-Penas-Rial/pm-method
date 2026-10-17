---
tipo: plan-excepcion
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de excepción · Exception plan

> Borrador generado con asistencia de IA. Solo existe porque la junta lo pidió tras un informe de excepción; al aprobarse reemplaza al plan vigente y crea un nuevo límite de etapa. / AI-assisted draft; produced only at the board's request after an exception report; on approval it replaces the current plan and creates a new stage boundary.

**Plan que reemplaza / Plan it replaces:** {{plan_vigente}} (etapa {{numero_etapa}} · versión {{version_vigente}})
*Plan de etapa o, si la excepción supera tolerancias de proyecto, plan de proyecto.*

**Informe de excepción / Exception report:** X-{{numero}} · `03-control/reportes/{{fecha_informe}}-informe-excepcion-X-{{numero}}.md` · **Decisión de la junta / Board decision:** D-{{id}} ({{fecha_decision}})
*Sin informe y decisión registrada no se produce este plan. Este archivo: `02-planificacion/plan-excepcion-X-{{numero}}.md`; proceso en SB (`estado.py limite-etapa --excepcion X-{{numero}}`).*

**Opción elegida por la junta / Option chosen by the board:** {{opcion}}
*Copiada del informe de excepción; el plan desarrolla exactamente esa opción.*

## 1. Causa y situación / Cause and situation
{{causa}}
*Qué provocó la desviación prevista, en qué dimensión y por cuánto; fuente: informe de excepción.*

## 2. Alcance del plan de excepción / Scope of the exception plan
{{alcance}}
*Desde la fecha de la excepción hasta el fin de la etapa revisada (o del proyecto); conviene alinear el nuevo fin con el original cuando sea posible.*

## 3. Qué cambia respecto del plan vigente / What changes vs the current plan
| Elemento / Element | Plan vigente / Current plan | Plan de excepción / Exception plan | Motivo / Reason |
|---|---|---|---|
| Productos / Products | {{antes}} | {{despues}} | {{motivo}} |
| Paquetes de trabajo / Work packages | {{antes}} | {{despues}} | {{motivo}} |
| Fechas e hitos / Dates and milestones | {{antes}} | {{despues}} | {{motivo}} |
| Presupuesto / Budget | {{antes}} | {{despues}} | {{motivo}} |
| Tolerancias / Tolerances | {{antes}} | {{despues}} | {{motivo}} |
| Equipo y recursos / Team and resources | {{antes}} | {{despues}} | {{motivo}} |
*Tabla de diferencias explícita para que la junta vea el impacto de un vistazo.*

## 4. Dependencias, supuestos y lecciones / Dependencies, assumptions and lessons
- Dependencias / Dependencies: {{dependencias}}
- Supuestos / Assumptions: S-{{ids}}
- Lecciones aplicadas / Lessons applied: L-{{ids}}
*Incluir la lección que deja la propia excepción.*

## 5. Productos a entregar / Products to be delivered
| Código / Code | Producto / Product | Descripción (versión) / Description (version) | Estado / Status | Fecha prevista / Planned date |
|---|---|---|---|---|
| P-{{p}} | {{producto}} | `productos/{{archivo}}.md` v{{v}} | nuevo · modificado · sin cambio · eliminado | {{fecha}} |
*Descripciones de producto creadas o actualizadas; registro de productos actualizado.*

## 6. Trabajo, cronograma y presupuesto / Work, schedule and budget
- Paquetes / Work packages: ver tabla 3 y `diccionario-wbs.md`.
- Cronograma revisado / Revised schedule: `{{ruta_cronograma}}` (camino crítico: {{camino_critico}})
- Presupuesto revisado / Revised budget: {{presupuesto}} (contingencia {{contingencia}}; variación vs vigente {{variacion}})
*Mismo nivel de detalle que el plan reemplazado; un diagrama de flujo de productos ayuda a mostrar la nueva secuencia.*

## 7. Metas y tolerancias revisadas / Revised targets and tolerances
| Dimensión / Dimension | Meta / Target | Tolerancia / Tolerance | Nivel que la fija / Set by |
|---|---|---|---|
| Tiempo · Costo · Alcance · Calidad · Beneficios · Riesgo · Sostenibilidad | {{meta}} | {{tol}} | junta · capa de negocio |
*Si la excepción supera las tolerancias de proyecto, las nuevas las fija la capa de negocio.*

## 8. Impacto en el business case y en los riesgos / Impact on business case and risks
{{impacto}}
*Costos, fechas y beneficios revisados; exposición agregada; referencia al business case actualizado.*

## 9. Monitoreo, control y reporte / Monitoring, control and reporting
{{controles}}
*Controles adicionales derivados de la excepción (p. ej. revisiones más frecuentes).*

## 10. Solicitud a la junta / Request to the board
- Aprobar este plan de excepción como nuevo plan de etapa / Approve this plan as the new stage plan.
- Aprobar actualizaciones de business case, plan de proyecto y PID si procede / Approve updates to business case, project plan and PID.
- Puerta / Gate: `autorizar-plan-excepcion` · decide: {{rol_decide}}
- Si se rechaza: la etapa continúa según dirección de la junta hasta aprobar una versión revisada / If rejected, the stage continues under board direction until a revised plan is approved.
*Solo pm-director registra la puerta (`estado.py puerta autorizar-plan-excepcion`, que limpia excepcion_abierta y escribe decisiones.csv); si se aprueba, estado.json.artefactos.plan-etapa-<n> apunta a este archivo.*

## 11. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Informe de excepción, registros, cálculos; cifras [por confirmar].*

## Lista de verificación / Checklist
- [ ] Informe de excepción y decisión de la junta referenciados.
- [ ] Opción elegida desarrollada sin añadir cambios no pedidos.
- [ ] Tabla de diferencias completa.
- [ ] Mismo nivel de detalle que el plan reemplazado; descripciones y registro de productos actualizados.
- [ ] Tolerancias revisadas y nivel que las fija identificado.
- [ ] Impacto en business case y riesgos evaluado.
- [ ] Lección de la excepción registrada.
- [ ] Solicitud de puerta autorizar-plan-excepcion preparada para pm-director.
