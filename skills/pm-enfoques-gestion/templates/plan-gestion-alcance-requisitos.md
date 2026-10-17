---
tipo: plan-gestion-alcance-requisitos
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de gestión del alcance y de requisitos · Scope and requirements management plan — {{proyecto}}

> Cómo se define, descompone, valida y controla el alcance, y cómo se obtienen, priorizan, rastrean y cambian los requisitos. Complementa el enfoque de issues y cambios. Predominante en enfoques predictivos e híbridos; en ágil, versión mínima centrada en el backlog. / How scope and requirements are defined, decomposed, validated and controlled.

**Enfoque de entrega / Delivery approach:** {{enfoque_entrega}}
**Versión mínima / Minimal version:** {{version_minima}}
*`sí`: secciones 1, 3, 5 y 7 con una línea cada una.*

## 1. Definición del alcance / Scope definition

{{definicion_alcance}}
*Dueños únicos: este plan dice CÓMO se gestiona el alcance; QUÉ entra (enunciado de alcance, PBS/WBS, diccionario) lo produce y mantiene `pm-planificacion-por-productos`. Aquí solo se referencia por ruta, sin copiar su contenido. En perfil ágil mínimo, el QUÉ es el backlog priorizado (épica → historia).*

## 2. Descomposición / Decomposition

{{descomposicion}}
*Cómo se construye la PBS y la WBS/EDT: niveles, criterio de paquete de trabajo (tamaño máximo en esfuerzo o duración), codificación, diccionario. En ágil: épicas → historias como productos.*

## 3. Elaboración progresiva vs cambio / Progressive elaboration vs change

{{elaboracion_vs_cambio}}
*Qué se considera detalle que se completa sin control formal y qué se considera cambio a la línea base que requiere solicitud de cambio.*

## 4. Obtención de requisitos / Requirements elicitation

{{elicitacion}}
*Técnicas (entrevistas, talleres, observación, prototipos), quiénes participan, cómo se documentan.*

## 5. Categorías y priorización / Categories and prioritization

| Categoría / Category | Ejemplos / Examples | Método de priorización / Prioritization |
|---|---|---|
| Negocio / Business | {{cat_negocio}} | {{prio_negocio}} |
| Interesados / Stakeholder | {{cat_stakeholder}} | {{prio_stakeholder}} |
| Solución (funcionales y no funcionales) / Solution | {{cat_solucion}} | {{prio_solucion}} |
| Transición / Transition | {{cat_transicion}} | {{prio_transicion}} |

*Indicar requisitos innegociables y método (MoSCoW, valor/costo, orden del backlog).*

## 6. Trazabilidad / Traceability

{{trazabilidad}}
*Qué se traza (objetivo de negocio → requisito → producto → prueba → aceptación), dónde (matriz de trazabilidad) y quién la mantiene.*

## 7. Validación y aceptación del alcance / Scope validation and acceptance

{{aceptacion}}
*Quién acepta cada producto (usuario sénior o su delegado), con qué criterios (descripción de producto) y cómo se registra (registro de calidad y de aceptación).*

## 8. Control del alcance / Scope control

{{control_alcance}}
*Cómo se detecta y trata la desviación de alcance: tolerancia de alcance, autoridad de cambio, presupuesto de cambio; en ágil, el product owner intercambia ítems del backlog dentro de la tolerancia de alcance de la etapa (decisión `nivel=product-owner`); desplazar un Must o exceder la tolerancia es solicitud de cambio.*

## 9. Gestión de requisitos en ágil o híbrido / Agile or hybrid requirements

{{agil}}
*Refinamiento del backlog, definición de listo y de hecho, quién prioriza (product owner ≈ usuario sénior delegado), cómo se reflejan los cambios de prioridad en los informes.*

## Lista de verificación / Checklist
- [ ] Criterio de paquete de trabajo definido.
- [ ] Frontera entre elaboración progresiva y cambio explícita.
- [ ] Método de priorización y requisitos innegociables declarados.
- [ ] Trazabilidad hasta prueba y aceptación.
- [ ] Responsables de aceptación por tipo de producto.
- [ ] Coherente con el enfoque de issues y cambios.
