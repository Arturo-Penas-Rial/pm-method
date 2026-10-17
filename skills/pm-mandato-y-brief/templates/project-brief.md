---
tipo: project-brief
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Resumen del proyecto · Project brief — {{proyecto}}

> Base firme para autorizar la etapa 1 (iniciación). Lo prepara el gestor con el ejecutivo; lo aprueba la junta en la puerta `autorizar-inicio`. Se absorbe en el PID y no se mantiene después. / Firm basis for authorising the initiation stage; absorbed by the PID afterwards.

**Versión / Version:** {{version_doc}} · **Nivel de formalidad / Formality level:** {{nivel_formalidad}}
*Mínima (brief con business case esquemático fusionado), ágil mínima (brief ligero: secciones 1, 2 resumida, 4 y 5 en una o dos páginas; alcance por épicas; tolerancia de alcance con MoSCoW; product owner prospectivo; acompañado de la declaración de visión) o completa. Indicar qué secciones se omitieron y por qué.*

## 1. Definición del proyecto / Project definition

**Antecedentes / Background:** {{antecedentes}}
*Situación actual, trabajo previo y hecho que dispara el proyecto. Copiar de la propuesta si existe.*

**Brief de producto BMAD / BMAD product brief:** {{ref_brief_bmad}}
*Solo si `integraciones.especificacion = bmad`: ruta · sha corto · status (de `bmad.py inventario`). Problema, usuarios y visión del producto se leen allí; no copiarlos aquí. Si no aplica, "no aplica".*

**Objetivos / Objectives:** {{objetivos}}
*Objetivos medibles con criterio de éxito cada uno. Fuente única: nacen aquí (o en el business case) y se copian al PID y al acta.*

**Resultados deseados / Desired outcomes:** {{resultados}}
*Qué cambia en la organización cuando se usan los productos. Distinto de los entregables.*

**Alcance e inclusiones / Scope and inclusions:** {{alcance}}
*Productos y trabajo que entran.*

**Exclusiones / Exclusions:** {{exclusiones}}
*Al menos una. Lo que un lector podría suponer incluido y no lo está.*

**Restricciones / Constraints:** {{restricciones}}
*Límites impuestos: fechas, presupuesto, normativa, tecnología, contratos.*

**Supuestos / Assumptions:** {{supuestos}}
*Lo que se da por cierto sin verificar. Cada uno con responsable de validación; registrar en `supuestos.csv`.*

**Tolerancias de proyecto / Project tolerances:** {{tolerancias}}
*Tiempo, costo, alcance, calidad, beneficios, riesgo, sostenibilidad (tiempo y costo, mínimo obligatorio). Lo que la capa de negocio concede; se copian a `estado.json` con `estado.py tolerancia --nivel proyecto k=v`; `[por confirmar]` si aún no se fijó. En ágil, la tolerancia de alcance se expresa con MoSCoW.*

**Usuarios e interesados conocidos / Known users and stakeholders:** {{interesados}}
*Incluir siempre al usuario final y a quien operará el producto. Alimenta `stakeholders.csv`.*

**Interfaces y dependencias / Interfaces and dependencies:** {{interfaces}}
*Otros proyectos, sistemas o contratos de los que se depende o a los que se afecta.*

## 2. Caso de negocio esquemático / Outline business case

**Razones / Reasons:** {{razones}}
*Por qué el proyecto y a qué objetivo de negocio contribuye.*

**Opción de negocio elegida / Chosen business option:** {{opcion_elegida}}
*Frente a "no hacer nada distinto", "hacer lo mínimo" y "hacer más": cuál se recomienda y en una línea por qué.*

**Beneficios esperados (alto nivel) / Expected benefits (high level):** {{beneficios}}
*Medibles aunque sean aproximados; des-beneficios conocidos también.*

**Riesgos de viabilidad / Viability risks:** {{riesgos_viabilidad}}
*Los riesgos que podrían hacer que no valga la pena iniciar.*

**Referencia / Reference:** {{ref_business_case}}
*Ruta a `00-direccion/business-case.md` si se produjo aparte con `pm-caso-de-negocio`.*

## 3. Descripción del producto del proyecto / Project product description

**Propósito del producto / Product purpose:** {{proposito_producto}}
*Para qué sirve el producto final y quién lo usará.*

**Composición principal / Main composition:** {{composicion}}
*Productos mayores que lo forman; en ágil pueden expresarse como épicas.*

**Expectativas de calidad del usuario / User quality expectations:** {{expectativas_calidad}}
*Lo que el usuario sénior espera en términos de desempeño, usabilidad, cumplimiento.*

**Criterios de aceptación / Acceptance criteria:** {{criterios_aceptacion}}
*Medibles o al menos descriptivos, con compromiso de precisarlos en el inicio. Quién acepta.*

**Estándares aplicables / Applicable standards:** {{estandares}}
*Normas del sector, políticas internas, regulación.*

## 4. Enfoque del proyecto / Project approach

**Modelo de entrega / Delivery model:** {{modelo_entrega}}
*Interno, contratado o mixto; por producto o por mano de obra.*

**Construir, adaptar o comprar / Build, adapt or buy:** {{construir_adaptar_comprar}}
*Desde cero, modificar algo existente o producto estándar (COTS).*

**Método de entrega / Delivery method:** {{metodo_entrega}}
*Predictivo, ágil o híbrido, con la puntuación de los criterios PMBOK y la vía por entregable si es híbrido. El marco sigue siendo el ciclo de vida por etapas.*

**Ruta de planificación BMAD / BMAD planning path:** {{ruta_bmad}}
*Solo con BMAD: rápida, estándar (PRD + arquitectura + UX) o empresarial, con una línea de justificación y qué artefactos BMAD se esperan antes de `autorizar-proyecto`. Si no aplica, "no aplica".*

**Sostenibilidad / Sustainability:** {{sostenibilidad}}
*Cómo el enfoque sostiene los compromisos ESG o de sostenibilidad del negocio.*

**Estándares y prácticas de usuario y proveedor / User and supplier standards and practices:** {{practicas}}
*Lo que ya existe y debe respetarse (metodologías, herramientas, procesos de calidad).*

**Requisitos de adaptación conocidos / Known tailoring needs:** {{adaptacion}}
*Qué del método se adaptará y por qué; se detalla en el PID.*

## 5. Estructura del equipo de gestión y roles / Management team structure and roles

**Ejecutivo / Executive:** {{ejecutivo}} · **Gestor / Project manager:** {{gestor}}
**Usuario(s) sénior / Senior user(s):** {{usuario_senior}} · **Proveedor(es) sénior / Senior supplier(s):** {{proveedor_senior}}
**Aseguramiento / Assurance:** {{aseguramiento}} · **Soporte / Support:** {{soporte}}
*Nombres y dedicación. Referencia a `00-direccion/estructura-organizativa.md` producida por `pm-organizacion-roles`.*

**Prácticas de trabajo para el inicio / Working practices for initiation:** {{practicas_trabajo}}
*Frecuencia de contacto gestor–ejecutivo, canal, co-ubicación o remoto.*

## 6. Hitos y etapas conocidas / Known milestones and stages

{{hitos}}
*Hitos impuestos o evidentes y la propuesta inicial de etapas de gestión. Fuente única: se copian al roadmap.*

## 7. Lecciones previas aplicadas / Previous lessons applied

{{lecciones}}
*Identificadores de `lecciones.csv` y cómo cambiaron este brief. Si no hubo fuentes, declararlo.*

## 8. Referencias / References

{{referencias}}
*Mandato, propuesta, canvas, visión, roadmap, documentos del programa, contratos.*

## Lista de verificación / Checklist
- [ ] Suficiente para decidir si vale la pena invertir en la etapa de inicio (ni más ni menos).
- [ ] Coherente con el mandato; cada añadido del gestor está identificado.
- [ ] Objetivos medibles con criterio de éxito; resultados distintos de entregables.
- [ ] Al menos una exclusión; restricciones y supuestos separados.
- [ ] Tolerancias de proyecto anotadas o `[por confirmar]` con quién las fija.
- [ ] Opción de negocio explícita frente a "no hacer nada distinto".
- [ ] Criterios de aceptación al menos descriptivos y con autoridad de aceptación.
- [ ] Enfoque del proyecto responde las cinco preguntas (modelo, construir/comprar, método, sostenibilidad, estándares).
- [ ] Ejecutivo y gestor nombrados; los tres intereses representados.
- [ ] Usuario final y operador del producto entre los interesados.
- [ ] Lecciones previas referenciadas o ausencia declarada.
- [ ] Datos de fuente única iguales a propuesta, canvas, visión y roadmap.
- [ ] Con BMAD: brief de producto referenciado (no duplicado) y ruta de planificación BMAD declarada.
- [ ] Frontmatter completo; estado `borrador` hasta la puerta `autorizar-inicio`.
