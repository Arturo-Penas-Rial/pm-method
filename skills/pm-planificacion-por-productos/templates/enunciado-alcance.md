---
tipo: enunciado-alcance
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enunciado del alcance · Project scope statement

> Borrador generado con asistencia de IA. / AI-assisted draft.

**Proyecto / Project:** {{proyecto}}
*Título tal como figura en el acta o el brief.*

**Fecha de preparación / Date prepared:** {{fecha}}
*Fecha de esta versión; solo cambia ante un cambio de alcance aprobado.*

## 1. Descripción del alcance del proyecto y del producto / Project and product scope description
{{descripcion_alcance}}
*Narrativa que amplía el acta y los requisitos: qué se hará y qué características tendrá el producto; coherente con la descripción del producto del proyecto.*

## 2. Entregables / Deliverables
| Código PBS / PBS code | Entregable / Deliverable | Criterio de aceptación / Acceptance criterion | Método / Method | Acepta / Accepted by |
|---|---|---|---|---|
| P-1 | {{entregable}} | {{criterio}} | inspección · prueba · demostración · análisis | {{responsable}} |
*Exactamente los productos de nivel superior de la PBS (del proyecto y de gestión); al menos un criterio medible por entregable, tomado de su descripción de producto.*

## 3. Exclusiones / Exclusions
- {{exclusion}}
*Lo que explícitamente no forma parte del producto ni del proyecto; cubrir las zonas grises que ya generaron preguntas.*

## 4. Restricciones / Constraints
- {{restriccion}}
*Límites impuestos: fecha, presupuesto, normativa, tecnología, contratos.*

## 5. Supuestos / Assumptions
- {{supuesto}} (S-{{id}})
*Referencia al registro de supuestos; cada supuesto no validado es un riesgo potencial.*

## 6. Tolerancia de alcance / Scope tolerance
{{tolerancia_alcance}}
*Qué productos o criterios son opcionales (could/won't) y pueden sacrificarse sin escalar; coherente con estado.json.tolerancias.proyecto.alcance y .etapa.alcance.*

## 7. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Acta, brief, descripción del producto del proyecto, requisitos; puntos [por confirmar].*

## Lista de verificación / Checklist
- [ ] Coherente con el acta de constitución, el brief y la descripción del producto del proyecto.
- [ ] Cada entregable tiene al menos un criterio de aceptación medible.
- [ ] Entregables = nivel superior de la PBS.
- [ ] Exclusiones explícitas y suficientes.
- [ ] Tolerancia de alcance declarada.
- [ ] Aprobación del ejecutivo / patrocinador pendiente antes de construir la línea base.
