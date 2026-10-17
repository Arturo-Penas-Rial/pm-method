---
tipo: requisitos
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Documentación de requisitos · Requirements documentation

> Borrador generado con asistencia de IA. / AI-assisted draft.

**Escala de prioridad / Priority scale:** {{escala_prioridad}}
*imprescindible / deseable / opcional (MoSCoW) o nivel 1–3; la misma que usa el backlog y la matriz de trazabilidad.*

**Enfoque / Approach:** {{enfoque_entrega}}
*En ágil esta tabla puede fundirse con el backlog e indicar iteración o release por requisito.*

## 1. Requisitos / Requirements
| ID | Requisito / Requirement | Interesado / Stakeholder | Categoría / Category | Prioridad / Priority | Criterio de aceptación / Acceptance criterion | Verificación / Verification | Fase o release / Phase or release | Padre / Parent | Estado / Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-001 | {{requisito}} | {{interesado}} | negocio · interesado · solucion_funcional · solucion_no_funcional · transicion · proyecto · calidad | {{prioridad}} | {{criterio}} | inspeccion · prueba · demostracion · analisis | {{fase}} | {{padre}} | propuesto · aprobado · implementado · verificado · descartado |
*Un requisito atómico por fila, redactado de forma verificable; el interesado es el origen (usar el cargo si no hay nombre); el criterio debe ser compatible con el método de verificación; "padre" enlaza requisito de negocio → técnico.*

## 2. Supuestos y restricciones asociados / Linked assumptions and constraints
| ID requisito / Requirement ID | Supuesto o restricción / Assumption or constraint | Registro / Register |
|---|---|---|
| REQ-001 | {{supuesto}} | S-{{id}} |
*Cada supuesto va también al registro de supuestos.*

## 3. Resumen / Summary
- Total de requisitos / Total: {{total}}
- Por categoría / By category: {{por_categoria}}
- Por prioridad / By priority: {{por_prioridad}}
- Sin método de verificación / Without verification: {{sin_verificacion}} (no entran en la línea base)
*Conteos automáticos para el highlight report y para la RTM.*

## 4. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Entrevistas, talleres, documentos; requisitos [por confirmar] con el interesado.*

## Lista de verificación / Checklist
- [ ] Una fila = un requisito atómico y verificable.
- [ ] Origen identificado en todas las filas.
- [ ] Prioridad según la escala declarada.
- [ ] Criterio de aceptación compatible con el método de verificación.
- [ ] Requisitos de transición y de calidad presentes, no solo funcionales.
- [ ] IDs únicos, estables y referenciados en la matriz de trazabilidad.
- [ ] Supuestos registrados en supuestos.csv.
