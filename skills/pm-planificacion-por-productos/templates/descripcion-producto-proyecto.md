---
tipo: descripcion-producto-proyecto
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Descripción del producto del proyecto · Project product description

> Borrador generado con asistencia de IA. Fuente de cada campo indicada entre corchetes. / AI-assisted draft; sources noted in brackets.

**Proyecto / Project:** {{proyecto}}
*Nombre tal como figura en el mandato o el brief.*

**Nivel de plan / Plan level:** plan de proyecto
*Este artefacto solo existe para el plan de proyecto; los planes de etapa usan descripciones de producto individuales.*

## 1. Propósito / Purpose
{{proposito}}
*Qué lograrán los productos una vez entregados y quién los usará; una o dos frases en términos de resultado, no de tareas.*

## 2. Productos mayores / Major products
| Código PBS / PBS code | Producto / Product | Tipo / Type | Etapa prevista / Planned stage |
|---|---|---|---|
| {{codigo}} | {{producto}} | final · intermedio · externo | {{etapa}} |
*Un renglón por producto de primer nivel de la PBS; marcar los externos (los produce otro) y los intermedios (insumo de otro producto).*

## 3. Derivación / Derivation
{{derivacion}}
*De qué parte el producto: sistema a reemplazar, producto comercial, requisito de nueva capacidad, diseño existente, enunciado de beneficios.*

## 4. Expectativas de calidad del usuario / User quality expectations
{{expectativas_calidad}}
*Nivel de calidad que el usuario sénior espera y estándares o sistemas de gestión de calidad (del negocio, del usuario o del proveedor) que deben aplicarse.*

## 5. Criterios de aceptación priorizados / Prioritized acceptance criteria
| ID | Criterio / Criterion | Medida / Measure | Prioridad (MoSCoW) / Priority | Método de aceptación / Acceptance method | Responsable / Responsible |
|---|---|---|---|---|---|
| CA-01 | {{criterio}} | {{medida}} | must · should · could · won't | inspección · prueba · demostración · análisis | {{responsable}} |
*Criterios expresados como capacidades que el negocio tendrá al aceptar; medibles cuando sea posible; si son descriptivos, dejar constancia de que se traducirán a especificaciones precisas en las descripciones de producto. La prioridad fija la tolerancia de alcance.*

## 6. Tolerancias de calidad a nivel proyecto / Project-level quality tolerances
{{tolerancias_calidad}}
*Rangos dentro de los cuales los criterios de aceptación pueden variar y el producto seguir siendo aceptable; en unidades del criterio.*

## 7. Métodos y responsabilidades de aceptación / Acceptance methods and responsibilities
{{metodos_aceptacion}}
*Cómo se confirmará la aceptación (ronda de pruebas de usuario, inspección en entrega, piloto) y quién decide: usuario sénior acepta, ejecutivo confirma, proveedor sénior acuerda si corresponde.*

## 8. Versión ágil (si aplica) / Agile version (if applicable)
**Producto mínimo viable / Minimum viable product:** {{mvp}}
*Si el enfoque es ágil o híbrido: qué incluye la versión mínima usable que permite obtener retroalimentación; los criterios de la tabla 5 pueden expresarse como historias de usuario de alto nivel.*

## 9. Fuentes y pendientes / Sources and open points
- Fuentes consultadas / Sources: {{fuentes}}
- Pendientes `[por confirmar]` / Open points: {{pendientes}}
*Documentos de origen (brief, mandato, actas) y preguntas que faltan responder antes de la aprobación.*

## Lista de verificación / Checklist
- [ ] Todos los productos mayores identificados; ninguno sobra ni falta.
- [ ] Criterios de aceptación medibles o con compromiso explícito de precisión posterior.
- [ ] Prioridad asignada a cada criterio.
- [ ] Estándares y sistemas de calidad aplicables indicados.
- [ ] Método y responsable de aceptación por criterio.
- [ ] Tolerancias de calidad explícitas.
- [ ] Revisada por el usuario sénior; aprobación pendiente del ejecutivo (puerta registrada por pm-director).
