---
name: pm-mandato-y-brief
description: "Mandato, propuesta, project brief, canvas, visión y roadmap; enfoque de entrega. Usar: mandato, brief, arrancar, kick-off, canvas, visión, mandate, start up. No: business case→pm-caso-de-negocio."
version: 2.6.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-inicio
    procesos_prince2: [SU, IP]
    practicas_prince2: [business-case, organizing, plans]
    tecnicas_pmbok: [selección del enfoque de desarrollo, juicio de expertos, elicitación, taller facilitado]
    artefactos: [mandato, propuesta-proyecto, project-brief, canvas-arranque, declaracion-vision, roadmap, lecciones.csv]
    idiomas: [es, en]
---

# Mandato y brief del proyecto · Project mandate and brief

## Cuándo usar / When to use
- Una idea, correo o pedido debe convertirse en **mandato** (project mandate).
- Hay que decidir si vale la pena iniciar: **propuesta** (project proposal) y **project brief** para `autorizar-inicio`.
- Alinear con **canvas de arranque**, **declaración de visión** o un primer **roadmap** por etapas.
- Elegir el **enfoque de entrega** (predictivo, ágil, híbrido) y, con BMAD, la ruta de planificación BMAD.
- EN: turn a request into a mandate; draft proposal, project brief, canvas, vision or roadmap.
- EN: choose and record the delivery approach (and BMAD planning path); search previous lessons first.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Plantillas con etiquetas bilingües; artefactos con su nombre EN entre paréntesis la primera vez.

## Conocimiento
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §5.1 (SU) y §5.2 act. 1.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §2.2.1, §2.5.1 (brief), §3.3.2.
- `pm-knowledge/references/plantillas-inicio-y-planes.md` §2.1, §2.3, §2.4, §2.6, §2.7, §4.4, §6.5.
- `pm-knowledge/references/pmbok8-estandar-principios-ciclos.md` §4.3–4.4 (selección del enfoque).
- `references/guia.md`: perfiles (§1), ágil mínimo (§2), enfoque de entrega (§3), BMAD (§4), reglas extendidas (§5), ejemplo (§6), casos borde (§7), columnas de lecciones (§8), validar antes de invertir (§9).
- Con BMAD: `SPEC.md` §1.13 y `pm-bmad-puente/references/guia.md` §2.

## Entradas requeridas
- `estado.json` en `pre-proyecto` (SU, etapa 0) o `inicio`; si no existe, `pm-estado-proyecto` (`nuevo_proyecto.py --ruta <dir> --nombre ... --idioma ... --enfoque ...`).
- El disparador; si no hay texto, preguntar: problema, patrocinador, quién paga, restricciones, interesados evidentes.
- Lecciones previas (proyectos anteriores, auditorías, personas con experiencia).
- **Especificación (fuente única, SPEC §1.16)**: proveedor, brief de producto y visión se leen solo con `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> fuente|resumen|consultar <id>|listar …`, igual con o sin BMAD; nunca abrir archivos BMAD ni `requisitos.md` para extraer datos (ruta + sha del brief: `bmad.py inventario`). Escribe como dueña: mandato, propuesta, project brief (cita el brief de producto por ruta + sha, sin copiar texto), visión, roadmap.
- Si hay documentos o correo conectados, leer el disparador vía `pm-integraciones` (ningún conector es obligatorio).

## Procedimiento
1. **Leer el estado** (`python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> ver`). Fase `entrega` o posterior → el brief ya está en el PID; solo actualizar roadmap o visión.
2. **Mandato** → `templates/mandato.md` en `00-direccion/mandato.md`: pedido en palabras propias, autoridad emisora, ejecutivo prospectivo; faltantes `[por confirmar]`.
3. **Lecciones previas**: 3–10 aplicables en `lecciones.csv` (`registro.py agregar lecciones`) con recomendación; si no hay, el brief lo declara. De otros proyectos pm-method: `pm-lecciones-aprendidas` (`lecciones.py buscar --indice <índice> --para ideacion|descubrimiento`; `incorporar` las registra con `origen` tras confirmar con la persona).
4. **Nivel de formalidad** con la tabla de `references/guia.md` §1. 🔒 **Puerta humana 1**: el usuario confirma nivel y artefactos (`decisiones.csv`, nivel `gestor`); en perfiles mínimos se combina con la 2.
5. **Enfoque de entrega**: puntuar los criterios de selección (`references/guia.md` §3); entregables que puntúan distinto → híbrido. Con BMAD, proponer la **ruta de planificación BMAD** (`references/guia.md` §4.3). 🔒 **Puerta humana 2**: confirma el ejecutivo o el usuario; `estado.py set enfoque_entrega=...` y fila en `decisiones.csv`.
6. **Propuesta** → `templates/propuesta-proyecto.md` en `01-inicio/propuesta-proyecto.md` (resumen autónomo, dato verificable, orden de magnitud con confianza, petición de decisión).
7. **Visión** (si hay producto o servicio) → `templates/declaracion-vision.md` en `01-inicio/`; con BMAD, cita la visión del brief de producto. **Canvas** (opcional) → `templates/canvas-arranque.md` en `01-inicio/`.
8. **Project brief** → `templates/project-brief.md` en `01-inicio/project-brief.md`: definición, business case esquemático (`pm-caso-de-negocio`), descripción del producto del proyecto, enfoque (regla 10), estructura (`pm-organizacion-roles`), referencias; datos de fuente única copiados. **Con BMAD**: problema, usuarios y visión se **referencian** al brief de producto (ruta + sha corto), sin copiarlos (`references/guia.md` §4.2).
8b. **Validar antes de invertir** (idea con incertidumbre alta): supuestos críticos de deseabilidad, viabilidad y factibilidad en `supuestos.csv` con `criticidad`, `certeza`, `experimento`, `criterio`, `fecha_limite`; vista para la junta con `templates/hipotesis-y-experimentos.md` (`references/guia.md` §9). Sanidad SUP-01…03; puerta P-11.
9. **Roadmap** → `templates/roadmap.md` en `01-inicio/roadmap.md`: SU = etapa 0, etapa 1 = iniciación, entrega 2…n, puertas, releases; Mermaid. Con BMAD, en qué etapa se esperan PRD `final`, arquitectura y épicas (`references/guia.md` §4.4).
10. **Coherencia cruzada** de presupuesto, plazo, entregables, exclusiones e interesados; reportar discrepancias.
11. **Registrar** (`estado.py artefacto <clave> --ruta ... --estado borrador --version 0.1`) y listar `[por confirmar]` con su rol.
12. 🔒 **Puerta humana 3 (fuera de esta skill)**: brief, business case esquemático y `plan-etapa-1.md` quedan `en-revision` para `pm-director`, que registra `autorizar-inicio` y aprueba. Como subagente, cerrar con el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas, nunca sin puertas. SU es pre-proyecto (etapa 0); el primer plan es el de la etapa 1.
2. [PRINCE2] Desviación prevista fuera de tolerancia → se escala; nunca se absorbe.
3. [PRINCE2] Nada se aprueba sin acto humano registrado; esta skill deja todo `en-revision` y no registra puertas.
4. [PMBOK→Plans/SU] La puntuación del enfoque es orientativa; entregables con puntuación distinta → híbrido con vía por entregable; se revisa en cada puerta de etapa.
5. [Plantillas] Mínima (propuesta + brief, o brief con caso esquemático) en proyectos pequeños; completa según riesgo, costo e interesados; nunca los seis artefactos sin pedido.
6. Transparencia de IA: borrador, sin datos inventados (`[por confirmar]`), cifra con fuente.
7. Idioma del usuario; nombre EN la primera vez.
8. Escrituras externas solo con confirmación, vía `pm-integraciones`.
9. [PRINCE2] El mandato se conserva como llegó; sin ejecutivo prospectivo no hay proyecto (bloqueante).
10. [PRINCE2] El enfoque del proyecto responde: interno o contratado, construir o adaptar, estándar o a medida, método de entrega, sostenibilidad; con BMAD, la ruta de planificación elegida.
11. [PRINCE2] El brief alcanza para decidir la iniciación, no más; las lecciones se buscan antes.
12. [PRINCE2] Tolerancias de proyecto conocidas en el brief (tiempo y costo, obligatorias); a `estado.json` las lleva pm-director con `estado.py tolerancia --nivel proyecto` cuando el ejecutivo las fija.
13. [Plantillas] Todo artefacto de alcance tiene una exclusión; una discrepancia de datos de fuente única es un hallazgo.
14. BMAD (SPEC §1.13): el brief de producto es dueño de problema, usuarios y visión; el project brief lo referencia, nunca lo duplica ni escribe en carpetas BMAD.
Más reglas: `references/guia.md` §5.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | Clave |
|---|---|---|---|
| Mandato | `templates/mandato.md` | `00-direccion/mandato.md` | `mandato` |
| Propuesta | `templates/propuesta-proyecto.md` | `01-inicio/propuesta-proyecto.md` | `propuesta-proyecto` |
| Project brief | `templates/project-brief.md` | `01-inicio/project-brief.md` | `project-brief` |
| Canvas de arranque | `templates/canvas-arranque.md` | `01-inicio/canvas-arranque.md` | `canvas-arranque` |
| Declaración de visión | `templates/declaracion-vision.md` | `01-inicio/declaracion-vision.md` | `declaracion-vision` |
| Roadmap | `templates/roadmap.md` | `01-inicio/roadmap.md` | `roadmap` |
| Hipótesis y experimentos | `templates/hipotesis-y-experimentos.md` | `01-inicio/hipotesis-y-experimentos.md` | `hipotesis-y-experimentos` |
| Enfoque de entrega | brief + `estado.py set` | `estado.json.enfoque_entrega` | campo raíz |
| Lecciones previas | `registro.py agregar lecciones` | `03-control/registros/lecciones.csv` | registro |

## Calidad
- [ ] Mandato con autoridad emisora y ejecutivo (o bloqueante declarado); lecciones registradas o ausencia declarada.
- [ ] Nivel y enfoque confirmados y registrados (una sola confirmación en perfiles mínimos); con BMAD, ruta elegida.
- [ ] Brief: definición, cinco preguntas del enfoque, tolerancias, usuario final, referencias a caso y roles.
- [ ] Con BMAD: brief de producto citado por ruta y sha; nada de problema/usuarios/visión duplicado.
- [ ] Roadmap con numeración canónica y puertas; coherencia cruzada; `[por confirmar]` con rol.

## Escalamiento y excepciones
- Mandato sin ejecutivo o sin problema de negocio → `pm-director`; no avanzar.
- Pedido de saltar el brief → excepción al método en `decisiones.csv` si se confirma.
- Brief de producto BMAD ausente o contrario al mandato → issue `problema-preocupacion`; recomendar el flujo de brief de BMAD (rol Analyst), sin escribirlo.
- Otros casos: `references/guia.md` §7. Como subagente, las decisiones humanas van en el bloque de retorno, no se preguntan.

## Ejemplos de invocación
- "Convertí este correo del gerente en mandato y armá el brief."
- "¿Predictivo, ágil o híbrido? Ya hay un brief de producto de BMAD; usalo sin copiarlo."
- EN: "Turn this idea into a project mandate and a startup canvas for a workshop."
- EN: "Small agile app, fixed date: minimal profile, ask me only once."
- No activa: "Calculá NPV y payback de la opción elegida" → `pm-caso-de-negocio`.

## EN summary
PRINCE2 Starting up a project: capture the mandate, search lessons, agree formality and delivery approach (human gates, merged in minimal profiles), draft proposal, vision, canvas, project brief and roadmap. With BMAD, the project brief references the BMAD product brief (path + hash) without duplicating it, and the project approach records the BMAD planning path. pm-director records `autorizar-inicio`. Detail in `references/guia.md`.
