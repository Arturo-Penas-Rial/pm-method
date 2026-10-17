---
tipo: diccionario-wbs
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Diccionario de la WBS/EDT · WBS dictionary

> Borrador generado con asistencia de IA. Las horas y costos se completan desde pm-cronograma-estimacion y pm-costos-presupuesto. / AI-assisted draft; hours and costs come from the estimation and costing skills.

**Nivel de plan / Plan level:** {{nivel_plan}}
*Proyecto o etapa N; una entrada por paquete de trabajo de la WBS.*

**Moneda y unidad de esfuerzo / Currency and effort unit:** {{moneda}} · {{unidad_esfuerzo}}
*Coherentes con la hoja de estimación y la hoja de costeo.*

---

## Paquete {{codigo_wbs}} · {{nombre_paquete}}

**Responsable del paquete / Work package owner:** {{responsable_paquete}} · **Ejecución / Delivered by:** interno · proveedor externo ({{contrato}})
*Una persona o rol (jefe de equipo o contratista) que acepta el paquete y responde por él; si es proveedor, la estrategia y el contrato están en 02-planificacion/adquisiciones/.*

**Producto(s) que entrega / Product(s) delivered:** {{codigos_pbs}}
*Códigos PBS; cada paquete entrega al menos un producto final o intermedio.*

**Descripción del trabajo / Description of work:** {{descripcion_trabajo}}
*Qué incluye y qué no, de modo que alguien ajeno entienda el encargo.*

**Hitos y fechas / Milestones and due dates:**
| Hito / Milestone | Fecha prevista / Due date |
|---|---|
| {{hito}} | {{fecha_hito}} |
*Coinciden con el cronograma; en ágil, fin de iteración o release.*

**Actividades / Activities:**
| ID actividad / Activity ID | Actividad / Activity | Recurso / Team resource | Horas / Labor hours |
|---|---|---|---|
| {{codigo_wbs}}.1 | {{actividad}} | {{recurso}} | {{horas}} |
*Extensión de la numeración de la WBS; las horas provienen de la hoja de estimación.*

**Costo / Cost:**
| Mano de obra (horas × tarifa) / Labor | Materiales (unidades × unitario) / Material | Otros directos / Other direct | Costo total / Total cost |
|---|---|---|---|
| {{total_mano_obra}} | {{total_material}} | {{otros}} | {{costo_total}} |
*Total mano de obra = horas × tarifa; total material = unidades × costo unitario; costo total del paquete = mano de obra + material + otros directos; la cuenta de control suma sus paquetes.*

**Requisitos de calidad / Quality requirements:** {{requisitos_calidad}}
*Métricas o estándares aplicables, tomados de la descripción de producto.*

**Criterios de aceptación / Acceptance criteria:** {{criterios_aceptacion}}
*Los mismos del enunciado del alcance y de la descripción de producto.*

**Dependencias / Dependencies:** {{dependencias}}
*Del diagrama de flujo de productos; internas y externas.*

**Tolerancias del paquete / Work package tolerances:** {{tolerancias}}
*Tiempo, costo y alcance que el gestor de equipo puede manejar sin escalar; dentro de las de la etapa.*

**Información técnica / Technical information:** {{info_tecnica}}
*Referencias a especificaciones o documentos técnicos, sin copiarlos.*

**Información contractual / Contract information:** {{info_contractual}}
*Contrato o acuerdo que afecta el paquete cuando lo ejecuta un proveedor.*

---

## Resumen por cuenta de control / Control account summary
| Cuenta de control / Control account | Paquetes / Work packages | Costo total / Total cost | Responsable / Owner |
|---|---|---|---|
| {{cuenta}} | {{paquetes}} | {{costo}} | {{responsable}} |
*Costo de la cuenta de control = Σ costo total de sus paquetes.*

## Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Estimaciones, cronograma, contratos; campos [por confirmar] / [to be confirmed].*

## Lista de verificación / Checklist
- [ ] Una entrada por paquete de la WBS (regla del 100 %).
- [ ] Cada paquete tiene un responsable nombrado y su tipo de ejecución (interno o proveedor).
- [ ] Descripción comprensible para alguien ajeno al proyecto.
- [ ] Criterios de aceptación coinciden con enunciado del alcance y descripciones de producto.
- [ ] Horas y tarifas coinciden con las hojas de estimación y costeo.
- [ ] Hitos coinciden con el cronograma.
- [ ] Paquetes tercerizados referencian su contrato.
- [ ] Documentos externos referenciados, no duplicados.
