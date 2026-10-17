---
tipo: mandato
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Mandato del proyecto · Project mandate — {{proyecto}}

> Disparador externo del proyecto. No es un producto de gestión del método: se conserva tal como llegó y se anota qué añadió el gestor al transcribirlo. / External trigger of the project; kept faithful to the source, with the manager's additions clearly marked.

## 1. Origen / Origin

**Autoridad que emite el mandato / Issuing authority:** {{autoridad_emisora}}
*Quién encarga el proyecto: comité, gerencia, programa, portafolio o cliente. Sin autoridad reconocible no hay mandato.*

**Fecha y canal de recepción / Date and channel received:** {{fecha_recepcion}} · {{canal}}
*Cuándo llegó y por dónde (correo, acta, solicitud de propuesta, conversación). Sirve de trazabilidad.*

**Texto o referencia original / Original text or reference:** {{texto_original}}
*Pegar el pedido original o enlazar el documento fuente. Si fue verbal, transcribir en palabras propias y marcarlo como transcripción.*

## 2. Qué se pide / What is requested

**Problema u oportunidad / Problem or opportunity:** {{problema_oportunidad}}
*Qué duele o qué se quiere aprovechar, con al menos un dato verificable si existe.*

**Resultado esperado / Expected outcome:** {{resultado_esperado}}
*Qué cambia en el negocio cuando el proyecto termina, no la lista de entregables.*

**Salidas conocidas / Known outputs:** {{salidas_conocidas}}
*Productos que el mandato ya nombra. Puede estar vacío: al arrancar basta con que el problema esté claro.*

**Restricciones impuestas / Imposed constraints:** {{restricciones}}
*Plazos, presupuesto tope, normativa, proveedores obligatorios, tecnología fijada. Solo lo que el mandato impone, no lo que el gestor supone.*

**Tolerancias de proyecto declaradas / Declared project tolerances:** {{tolerancias}}
*Márgenes que la capa de negocio concede (tiempo, costo, alcance, calidad, beneficios, riesgo, sostenibilidad). Si no las declara, `[por confirmar]`.*

## 3. Personas / People

**Ejecutivo prospectivo / Prospective executive:** {{ejecutivo}}
*Quién responderá por el proyecto ante el negocio. Campo bloqueante: sin ejecutivo no se solicita el inicio.*

**Gestor de proyecto propuesto / Proposed project manager:** {{gestor}}
*Si el mandato lo nombra. Si no, lo nombra el ejecutivo en el arranque.*

**Interesados evidentes / Obvious stakeholders:** {{interesados}}
*Áreas, clientes, reguladores o proveedores que el mandato menciona o que es imposible no considerar.*

## 4. Contexto / Context

**Relación con estrategia, programa o portafolio / Link to strategy, programme or portfolio:** {{relacion_estrategia}}
*Objetivo de negocio al que contribuye. Si viene de un programa, indicar qué aporta el programa (brief, junta, enfoques).*

**Trabajo previo / Previous work:** {{trabajo_previo}}
*Estudios de viabilidad, pilotos, intentos anteriores y por qué terminaron como terminaron.*

**Lecciones previas identificadas / Previous lessons identified:** {{lecciones}}
*Referencia a las filas de `lecciones.csv` cargadas al arrancar, o declaración de que no se encontraron.*

## 5. Anotaciones del gestor / Manager's annotations

**Ambigüedades detectadas / Ambiguities found:** {{ambiguedades}}
*Qué del mandato no se entiende o se contradice; cada una con la pregunta que se hará y a quién.*

**Añadidos al transcribir / Additions made when transcribing:** {{anadidos}}
*Todo lo que el gestor o el agente agregó que no estaba en la fuente. Transparencia obligatoria.*

**Campos por confirmar / Fields to confirm:** {{por_confirmar}}
*Lista de `[por confirmar]` con el rol que debe confirmarlos y la fecha límite.*

## Lista de verificación / Checklist
- [ ] Autoridad emisora identificada y con capacidad de encargar el proyecto.
- [ ] Texto original conservado o transcripción marcada como tal.
- [ ] Problema u oportunidad formulado con al menos un dato verificable (o `[por confirmar]`).
- [ ] Ejecutivo prospectivo nombrado (campo bloqueante).
- [ ] Restricciones separadas de supuestos del gestor.
- [ ] Tolerancias declaradas o marcadas `[por confirmar]`.
- [ ] Lecciones previas referenciadas o ausencia declarada.
- [ ] Añadidos del agente listados en la sección 5.
- [ ] Frontmatter completo; estado `borrador`.
