---
name: pm-mapas-estrategicos
description: "Mapas de Wardley y de recorrido del cliente (journey, service blueprint) desde el proyecto o BMAD, con controles. Usar: mapa de Wardley, evolución de componentes, customer journey, puntos de dolor. No: diagramas de gestión→pm-visuales."
version: 2.6.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-inicio
    procesos_prince2: [SU, IP, SB]
    practicas_prince2: [business-case, plans, risk, quality]
    tecnicas_pmbok: [análisis de hacer o comprar, pensamiento de diseño, análisis Kano, análisis de supuestos y restricciones]
    artefactos: [mapa-wardley-<slug>, mapa-recorrido-<slug>]
    idiomas: [es, en]
---

# Mapas estratégicos · Strategic maps

## Cuándo usar / When to use
- Antes de comprometer el enfoque de entrega o el hacer o comprar: ubicar cada componente del producto por **visibilidad** para el usuario y **evolución** (génesis → a medida → producto → commodity) y ver qué conviene construir, comprar o tercerizar, y dónde hay inercia (mapa de Wardley).
- Para entender la experiencia de quien usa el servicio: etapas, una acción por paso, puntos de contacto, emoción con su fuente, dolores y oportunidades, y lo que ocurre detrás (carriles de service blueprint).
- Para llevar los dolores del recorrido a requisitos, riesgos o supuestos registrados y vigilarlos con la sanidad (familia MAP).
- EN: Wardley map (build, buy, outsource, inertia) and customer journey map with blueprint lanes, from project artifacts or, read-only, from BMAD.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Las etapas salen en el idioma del proyecto; Mermaid rotula los ejes en inglés, por eso la vista lleva leyenda. Términos EN la primera vez: Wardley map, customer journey map, service blueprint, touchpoint, pain point.

## Conocimiento
- `references/guia.md`: §1 para qué, §2 Wardley (cadena de valor, etapas con evidencia, movimiento, inercia, decisiones), §3 lectura para la gestión, §4 recorrido (acciones, emociones con fuente, dolores, Kano), §5 carriles de service blueprint, §6 PRINCE2, §7 con y sin BMAD, §8 controles MAP, §9 formatos y tablero de mapas, §10 casos borde, §11 fuentes.
- `templates/wardley-ejemplo.json`, `recorrido-ejemplo.json` (esquemas comentados); `recorrido.html` y `tablero-mapas.html` (vistas autocontenidas).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.12 (hacer o comprar) y §3.4 (Kano), solo como técnica.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §2.3 (opciones y evaluación del caso), §4.5.2 (descripción del producto del proyecto); `prince2-practicas-riesgo-issues-progreso-productos.md` §2.c (riesgos).

## Entradas requeridas
- `estado.json` (idioma, `integraciones.especificacion`, `enfoque_entrega`).
- **Especificación (fuente única, SPEC §1.16)**: ids y existencia por `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar requisitos`. Con BMAD, el detalle de recorridos y del mapa de capacidades sale **solo** de `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> recorridos [--id UJ-n] [--json]` y `capacidades [--json]` (solo lectura); nunca abrir `_bmad-output/`.
- Sin BMAD: mandato, brief, business case esquemático (opciones), `requisitos.md` vía la fachada, `wbs.csv`, `supuestos.csv`, `riesgos.csv`, `decisiones.csv`, lecciones, interesados y transcripciones de `pm-reuniones`.
- La **pregunta estratégica** (qué decisión informa el mapa) y la **persona** del recorrido: si faltan, preguntarlas antes de dibujar.

## Procedimiento
Script: `python3 ${CLAUDE_SKILL_DIR}/../pm-mapas-estrategicos/scripts/mapas.py --proyecto <dir> …` (en el plugin `${CLAUDE_PLUGIN_ROOT}/skills/pm-mapas-estrategicos/scripts/mapas.py`).
1. **Encuadrar**: pregunta estratégica, alcance, persona y fecha de corte. Sin decisión que informar, el mapa es decoración (guía §1).
2. **Semilla**: `mapas.py --proyecto <dir> wardley semilla --slug <s> --titulo … --pregunta … [--anclas "…"] [--componentes "…; …"] --fecha AAAA-MM-DD` y `recorrido semilla [--uj UJ-n --backstage UJ-m] | [--persona … --etapas "…; …"] --fecha …`. Con BMAD toma UJ-n, sus FR, SM-n, capacidades → AD-n y decisiones diferidas; sin BMAD, productos de la WBS o requisitos e insumos para citar (supuestos, riesgos, decisiones, lecciones). Posiciones y emociones quedan `[por confirmar]`.
3. **Proponer con evidencia** (guía §2 y §4): cada posición con etapa y evidencia citada (id o archivo:línea); cada emoción entera −2…+2 con su fuente (entrevista, métrica, observación o supuesto declarado); una acción por paso; dolores con tipo de causa; oportunidades con clase Kano. Lo que no tiene fuente queda como supuesto explícito. El modelo propone; **la persona confirma** (puerta humana 1).
4. **Validar**: `mapas.py … wardley|recorrido validar <slug>`; los errores (rangos, ids, ciclos, etapa incoherente, emoción, más de una acción por paso; guía §8) impiden generar la vista.
5. **Generar las vistas**: `mapas.py … wardley|recorrido render <slug>` → `02-planificacion/visuales/`: Markdown con Mermaid (`wardley-beta`, `journey`) y tabla; `.owm` (Wardley); `.html` con carriles y curva de emoción (recorrido); `.png` si hay `mmdc`. **Tablero gráfico** (guía §9): `mapas.py … tablero` dibuja los mapas en SVG (sin `mmdc`) con avisos MAP y vínculos en `visuales/tablero-mapas.html`; `--insertar <tablero-avance.html>` llena su sección «Mapas estratégicos». Registrar la primera vez: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> artefacto mapa-wardley-<slug>|mapa-recorrido-<slug> --ruta 02-planificacion/visuales/<…>.md --estado borrador`.
6. **Leer el mapa para la gestión** (guía §3): contrastar con los nueve criterios del enfoque (`pm-mandato-y-brief`), hacer o comprar a `pm-adquisiciones` (matriz `--criterios hacer-o-comprar` de `pm-direccion-decisiones`: lee el mapa y cita la decisión en el componente), inercias como riesgos a `pm-riesgos`, dolores como requisitos (`pm-planificacion-por-productos` o traspaso a BMAD) o supuestos.
7. **Candidatos del recorrido**: `mapas.py … recorrido candidatos <slug> [--salida F.md]` propone, con cita, el tratamiento de cada dolor sin tratar. Se registran con `registro.py` **solo tras la evaluación humana** y se citan con `mapas.py … vincular <slug> <id> --refs R-…,REQ-…`.
8. **Controles**: `mapas.py … controles` (lo usa `sanidad.py`, familia MAP, solo avisos): MAP-01 construir en producto o commodity sin decisión, MAP-02 inercia sin riesgo, MAP-03 dolor sin tratamiento, MAP-04 sin evidencia, MAP-05 id roto.
9. **Revisar** en cada límite de etapa y tras un cambio de la especificación (MAP-05: ids retirados): los componentes se mueven.
10. **Aprobar**: BORRADOR hasta que lo confirma el dueño de la decisión (ejecutivo o usuario sénior); luego `estado.py aprobar mapa-…` con el nivel que corresponda. Si corre como subagente, devolver la aprobación como decisión humana requerida (SPEC §1.11).

## Reglas del método
1. [PRINCE2] El mapa no es un producto de gestión obligatorio: es evidencia para el business case (opciones), el enfoque del proyecto y los riesgos. Decide la junta con los productos PRINCE2, no con el dibujo.
2. [PRINCE2] Toda inercia o dependencia crítica se registra como riesgo con propietario; todo dolor relevante termina en un requisito, historia, riesgo, issue, cambio, decisión, supuesto o revisión de calidad con id.
3. [PMBOK→Plans/Commercial] La decisión de hacer o comprar sigue el análisis de `pm-adquisiciones` (costos totales y riesgos); el mapa la orienta, no la reemplaza.
4. Evolución no es cronograma: el eje horizontal describe cuán estandarizado está un componente en el mercado, no cuándo se entrega.
5. Sin evidencia no hay posición ni emoción: se marca supuesto explícito o `[por confirmar]`; la sanidad avisa (MAP-04).
6. Mapear primero lo que existe (recorrido actual) y después el futuro; nunca el producto imaginado como si fuera el actual.
7. Una unidad de tiempo, una acción por paso; ≤ 15 componentes o pasos por mapa (si no, submapas).
8. Fuente única: los mapas citan ids (UJ, FR, AD, SM, REQ, R, S, D, I) y nunca copian textos de BMAD; BMAD solo se lee por `bmad.py` y `especificacion.py`.
9. Las etapas se dibujan en cuartos iguales del eje (0,25 · 0,50 · 0,75), como Mermaid; es una convención del paquete para ubicar, no una medición.
10. Transparencia de IA: lo propuesto por el modelo es borrador hasta que la persona confirma; las vistas generadas no se editan a mano (se regeneran).
11. Emociones y dolores salen de fuentes del proyecto; nunca se infieren rasgos de personas reales.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | estado.json |
|---|---|---|---|
| Mapa de Wardley (fuente) | `templates/wardley-ejemplo.json` | `02-planificacion/mapas/wardley-<slug>.json` | — (fuente de la vista) |
| Vista del mapa de Wardley | `mapas.py render` | `02-planificacion/visuales/wardley-<slug>.md` (+ `.owm`, `.png`) | `mapa-wardley-<slug>` |
| Recorrido del cliente (fuente) | `templates/recorrido-ejemplo.json` | `02-planificacion/mapas/recorrido-<slug>.json` | — (fuente de la vista) |
| Vista del recorrido | `templates/recorrido.html` vía `mapas.py render` | `02-planificacion/visuales/recorrido-<slug>.md` (+ `.html`, `.png`) | `mapa-recorrido-<slug>` |
| Tablero de mapas (vista derivada) | `templates/tablero-mapas.html` vía `mapas.py tablero` | `02-planificacion/visuales/tablero-mapas.html`; sección del tablero de avance | — |
| Candidatos del recorrido | `mapas.py recorrido candidatos --salida` | `03-control/reportes/<fecha>-candidatos-recorrido-<slug>.md` | — |

## Calidad
- [ ] Pregunta estratégica y persona explícitas; fecha de corte.
- [ ] Cada posición con etapa y evidencia citada; cada emoción con fuente; supuestos marcados como tales.
- [ ] `validar` sin errores y avisos revisados (huérfanos, solapamientos, más de 15 elementos).
- [ ] Inercias con riesgo abierto; componentes en producto o commodity marcados construir con decisión registrada; dolores con tratamiento.
- [ ] `mapas.py controles` sin avisos (o explicados); vistas regeneradas tras cada cambio.
- [ ] Vista registrada como BORRADOR hasta la confirmación del dueño de la decisión.

## Escalamiento y excepciones
- Decisión de hacer o comprar o de contratación → `pm-adquisiciones`; opciones y beneficios → `pm-caso-de-negocio`.
- Enfoque de entrega por entregable (nueve criterios) → `pm-mandato-y-brief`; riesgos de inercia o dependencia → `pm-riesgos`.
- Requisitos nuevos: sin BMAD → `pm-planificacion-por-productos`; con BMAD → traspaso al equipo de producto (`pm-bmad-puente`, `bmad.py handoff`).
- Render con archify, diagram-design o visual-explainer declarados en `integraciones.diagramas` → `pm-visuales` (motor externo), con el Mermaid como respaldo.
- En subagente: aprobaciones y decisiones de construir o comprar se devuelven como "decisiones humanas requeridas" (SPEC §1.11).

## Ejemplos de invocación
- "Armá un mapa de Wardley de los entregables: qué construimos, qué compramos y dónde hay inercia."
- "Hacé el journey del paciente que saca y cancela un turno, con los dolores enlazados a requisitos y riesgos."
- EN: "Build a customer journey map for UJ-2 with the operator as backstage lane."
- "Llevá el Wardley y el recorrido al tablero de avance."
- No activa: "Dibujame el organigrama del proyecto" → `pm-visuales`.

## EN summary
Wardley maps (value chain × evolution, with build/buy/outsource marks, movement and inertia) and customer journey maps (stages, one action per step, touchpoints, sourced emotions, pain points, opportunities with Kano class, blueprint lanes), seeded from project artifacts or read-only from BMAD. `mapas.py` validates maps, renders Mermaid, OWM, escaped HTML lanes and optional PNG, draws a maps board in its own SVG, proposes candidates for untreated pain points and feeds the MAP checks (warnings only). Maps inform business case options, delivery approach, make-or-buy (decision.py cites the choice) and risks; they stay drafts until the decision owner confirms.
