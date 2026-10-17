---
tipo: matriz-trazabilidad
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Matriz de trazabilidad de requisitos · Requirements traceability matrix

> Borrador generado con asistencia de IA. / AI-assisted draft.

**Última solicitud de cambio incorporada / Last change request applied:** {{ultimo_cambio}}
*ID de cambios.csv; la matriz se actualiza en la misma operación que la documentación de requisitos.*

## 1. Matriz principal / Main matrix
| ID requisito / Requirement ID | Requisito (resumen) / Requirement | Fuente / Source | Prioridad / Priority | Categoría / Category | Objetivo / Objective | Entregable EDT / WBS deliverable | Verificación (métrica) / Verification | Validación (técnica) / Validation | Organización responsable / Accountable org | Release | Estado de traza / Trace status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REQ-001 | {{requisito}} | {{fuente}} | {{prioridad}} | {{categoria}} | OBJ-{{n}} | P-{{codigo}} / W-{{codigo}} | {{metrica}} | {{tecnica}} | {{organizacion}} | R{{n}} | completa · parcial · huerfano |
*El objetivo viene del acta o del business case; el entregable es el código PBS/WBS; verificación = cómo se mide; validación = cómo se confirma que satisface la necesidad (p. ej. prueba de aceptación de usuario).*

## 2. Matriz inter-requisitos / Inter-requirements matrix
| ID negocio / Business ID | Requisito de negocio / Business requirement | Prioridad / Priority | Fuente / Source | ID técnico / Technical ID | Requisito técnico / Technical requirement | Prioridad / Priority | Fuente / Source |
|---|---|---|---|---|---|---|---|
| BR-{{n}} | {{req_negocio}} | {{prioridad}} | {{fuente}} | TR-{{n}} | {{req_tecnico}} | {{prioridad}} | {{fuente}} |
*Opcional (versión completa): relaciona requisitos padre (negocio) con hijos (técnicos) para detectar requisitos técnicos sin justificación.*

## 3. Cobertura / Coverage
- Requisitos con entregable y verificación / Traced requirements: {{trazados}} de {{total}} → cobertura = {{cobertura_pct}} %
- Requisitos huérfanos (sin objetivo) / Orphans: {{huerfanos}}
- Entregables sin requisito (posible sobre-alcance) / Deliverables without requirement: {{entregables_sin_requisito}}
*cobertura = requisitos con entregable y verificación / total de requisitos. Un entregable sin requisito es sospecha de gold plating; un requisito sin objetivo es candidato a eliminación o a solicitud de cambio.*

## 4. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Documentación de requisitos, PBS/WBS, business case.*

## Lista de verificación / Checklist
- [ ] IDs idénticos a la documentación de requisitos (sin faltantes ni duplicados).
- [ ] Cada requisito tiene objetivo, entregable y verificación.
- [ ] Cada entregable de la EDT aparece al menos una vez.
- [ ] Prioridades coinciden con requisitos y backlog.
- [ ] Requisitos técnicos cuelgan de al menos un requisito de negocio.
- [ ] Cobertura calculada y huérfanos listados.
- [ ] Actualizada con la última solicitud de cambio aprobada.
