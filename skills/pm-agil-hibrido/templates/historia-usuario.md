---
tipo: historia-usuario
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Historia de usuario · User story

> Borrador generado con asistencia de IA. Descripción de producto de grano fino: apunta a un producto de la PBS. / AI-assisted draft; a fine-grained product description linked to a PBS product.

**ID:** PB-{{id}} · **Título / Title:** {{titulo}}
*Mismo ID que en backlog.csv; título corto y orientado al resultado.*

**Producto PBS / PBS product:** P-{{codigo_pbs}} · **Épica / Epic:** PB-{{epica}}
*Trazabilidad al producto mayor y a la épica que descompone.*

**Requisito / Requirement:** REQ-{{req}} · **Objetivo / Objective:** OBJ-{{obj}}
*Enlace a la documentación de requisitos y al objetivo del business case; "ninguno" si es deuda técnica o acción de retro.*

## 1. Historia / Story
Como **{{rol}}**, quiero **{{necesidad}}** para **{{beneficio}}**.
*Rol concreto (no "usuario"); el beneficio explica el porqué y no repite la necesidad; cabe en una o dos oraciones.*

## 2. Criterios de aceptación / Acceptance criteria
| ID | Dado / Given | Cuando / When | Entonces / Then | Método de verificación / Verification |
|---|---|---|---|---|
| CA-1 | {{contexto}} | {{accion}} | {{resultado_observable}} | prueba · demostración · inspección · análisis |
*Condiciones verificables antes de entrar a la iteración; refinan las especificaciones de calidad del producto PBS; determinan si la historia está terminada junto con la definición de hecho.*

## 3. Prioridad y tamaño / Priority and size
- Prioridad (orden en backlog) / Priority: {{prioridad}} · MoSCoW: must · should · could · won't
- Puntos de historia / Story points: {{puntos}} (técnica: planning poker · tallas · comparación)
- Iteración prevista / Planned iteration: S{{iteracion}} · Release: R{{release}}
*Los puntos son tamaño relativo, no horas; must = compromiso de la etapa; should/could = tolerancia de alcance.*

## 4. Dependencias / Dependencies
- {{dependencia}} (PB-{{id}} · externa: {{externa}})
*Historias o productos externos que deben existir antes; si las hay, la historia no es independiente y se declara.*

## 5. Notas y supuestos / Notes and assumptions
{{notas}}
*Detalles de conversación, bocetos, restricciones no funcionales, supuestos (S-###).*

## 6. Definición de hecho aplicable / Applicable definition of done
{{dod_ref}}
*Referencia a la DoD de release-plan.md; excepciones a la DoD solo con acuerdo registrado.*

## 7. Responsable y aceptación / Owner and acceptance
- Equipo o responsable / Team or owner: {{responsable}}
- Acepta / Accepted by: {{aceptador}} (usuario sénior o delegado) · Fecha / Date: {{fecha_aceptacion}}
- Registro de calidad / Quality register: Q-{{id}}
*La aceptación en la review se registra en calidad.csv y en el registro de productos.*

## Lista de verificación / Checklist (INVEST)
- [ ] Independiente o con dependencias declaradas.
- [ ] Negociable: describe el qué, no la solución.
- [ ] Valiosa: beneficio explícito para un rol concreto.
- [ ] Estimable: puntos asignados por el equipo.
- [ ] Pequeña: cabe en una iteración.
- [ ] Testeable: criterios de aceptación verificables.
- [ ] Trazada a requisito, objetivo y producto PBS.
