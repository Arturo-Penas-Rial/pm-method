---
name: pm-visuales
description: "Diagramas y tablero de avance HTML. Usar: organigrama, mapa de stakeholders, diagrama de la WBS, roadmap visual, one-pager, tablero, dashboard, vista por actor. No: Gantt→pm-cronograma-estimacion; contenido del informe→pm-progreso-reportes."
version: 2.5.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [SU, IP, CS, SB, CP]
    practicas_prince2: [organizing, plans, progress, risk]
    tecnicas_pmbok: [estructuras jerárquicas (WBS, OBS), diagrama de Gantt, roadmap, mapa poder-interés, mapa de calor P×I, burn-up, controles visuales]
    artefactos: [organigrama, mapa-stakeholders, pbs-wbs, flujo-productos, gantt, roadmap, flujo-excepciones, canvas-arranque, tablero-avance]
    idiomas: [es, en]
---

# Visuales del método · Method visuals

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- Un artefacto se entiende mejor dibujado: organigrama, mapa poder/interés, PBS/WBS, flujo de productos, Gantt, roadmap, flujo de excepciones, canvas o one-pager visual.
- La junta, el patrocinador o el cliente piden "verlo en una página": tablero de avance con semáforo, hitos, riesgos, acciones y **vista por actor**.
- Otra skill (`pm-organizacion-roles`, `pm-planificacion-por-productos`, `pm-cronograma-estimacion`, `pm-progreso-reportes`) necesita incrustar un diagrama.
- EN: org chart, stakeholder map, WBS tree, roadmap, one-pager or progress dashboard.

## Idioma
Etiquetas en el idioma del proyecto (`estado.json.idioma`); los HTML con cabeceras bilingües (ES / EN). Términos EN la primera vez: product breakdown structure (PBS), product flow diagram, progress dashboard.

## Conocimiento
- `references/guia.md`: motores externos §1 (nombres, tipos, contrato, recetas), contenido y `wbs.py` §2, tablero §3, vista por actor §4, trackers §5, datos mínimos §6, elección §7, casos borde §8.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §3.1.5, §3.5.2 (equipo), §3.3.3 (RACI), planes (PBS, flujo).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §4.c.6 (highlight tipo tablero), §6 (flujo de excepciones), §4.a (tolerancias).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §2.4 (WBS, OBS), §2.6 (Gantt, roadmap), §3.3 (poder/interés), §5.2 regla 35 (visual según el dato).

## Entradas requeridas
- `estado.json` (idioma, etapa, tolerancias, roles, `enfoque_entrega`, `integraciones.diagramas`, `integraciones.cronograma`).
- Por visual: organigrama ← `roles` y `00-direccion/estructura-organizativa.md`; mapa ← `stakeholders.csv`; PBS/WBS ← `02-planificacion/pbs-wbs.md` o `wbs.csv`; flujo ← descripciones de producto; Gantt/roadmap ← `cpm.py --mermaid` o plan; canvas ← `01-inicio/canvas-arranque.md`.
- Tablero ← `estado.py periodo` (registros, `resumen --corte`, último corte de EVM, `avance-bmad.csv`, umbrales de `estado.json`) + juicio del gestor (JSON, guía de `pm-progreso-reportes` §14); instantáneas de `pm-integraciones` en `03-control/fuentes/`.
- **Especificación (fuente única, SPEC §1.16)**: requisitos, épicas e historias solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar … --json` (con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: visuales y tablero, que citan ids.
- Si falta la fuente: esqueleto con `[por confirmar]` y lista de lo que falta; nunca inventar nodos.

## Procedimiento
1. **Identificar el visual y su fuente**; leer `estado.json` y la fuente; listar faltantes antes de dibujar (datos mínimos en `references/guia.md` §6).
2. **Elegir el motor** según `integraciones.diagramas` (valor o lista por prioridad): `mermaid` por defecto (`templates/diagramas-mermaid.md`). Con `archify`, `diagram-design` o `visual-explainer` configurado e instalado (listado de skills, también con prefijo de plugin; INS-03) **delegar siempre**: Mermaid de respaldo, invocar la skill con la herramienta Skill y seguir guía §1.3–1.4 (ruta, ids, BORRADOR; sin preguntas bloqueantes). Ausente, sin el tipo o fallida: Mermaid y nota en `diario.md`.
3. **Tabla intermedia** (nodo, etiqueta, padre/dependencia, atributos) mostrada al usuario si hay más de ~15 elementos; es lo que se traduce al motor.
4. **Generar** con la plantilla o el script (contenido por visual en guía §2):
   - WBS: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/wbs.py 02-planificacion/wbs.csv --mermaid 02-planificacion/visuales/wbs.md` (árbol Mermaid validado; `--profundidad` para recortar).
   - Gantt: `cpm.py --mermaid`; roadmap con puertas como hitos; canvas con `templates/canvas-arranque.html`.
   - Tablero: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> periodo --desde … --corte … --juicio <json> --tablero` llena `templates/tablero-avance.html` (bloque `datos-tablero`, guía §3; mismas cifras que el highlight): semáforos por regla, hitos, decisiones, mapa de calor P×I, burn-up, acciones y **Vista por actor**. Con mapas en `02-planificacion/mapas/`, sección **Mapas estratégicos**: `${CLAUDE_SKILL_DIR}/../pm-mapas-estrategicos/scripts/mapas.py --proyecto <dir> tablero --insertar <tablero>` (guía §3).
5. **Vista por actor.** Selector sobre acciones abiertas (`D.acciones`), riesgos por propietario (`D.riesgos`) e issues por responsable (`D.issues`); abre filtrada con `?actor=<Nombre>` (guía §4).
6. **Datos de trackers.** El tablero puede alimentarse con instantáneas fechadas de `pm-integraciones` (avance de ítems, bloqueos), citadas en `fuentes`; riesgos, issues y acciones siguen saliendo de los registros (guía §5).
7. **Legibilidad**: título bilingüe, leyenda, fecha de corte, fuente; ≤ ~40 nodos (guía §7).
8. **Guardar** en `02-planificacion/visuales/` (planes) o `03-control/reportes/` (tablero con fecha) y registrar con `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> artefacto <nombre> --ruta ... --estado borrador`.
9. **PUERTA HUMANA.** El visual hereda el estado de su fuente (BORRADOR si no está aprobada); el gestor confirma antes de compartirlo, el ejecutivo antes de usarlo en una puerta. Publicar solo vía `pm-integraciones` con confirmación.
10. **Cerrar** con rutas, motor usado, fuentes y faltantes; si corre como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; el roadmap muestra siempre las puertas entre etapas, también en ágil o híbrido.
2. [PRINCE2] Un objetivo en rojo lleva la referencia a la excepción o issue escalado; nunca un verde cosmético.
3. [PRINCE2] Un visual no cambia el estado de nada: nada aprobado sin acto humano registrado.
4. [PRINCE2] La PBS contiene productos, no actividades; el flujo marca los externos; la WBS deriva de la PBS.
5. [PRINCE2] El organigrama muestra tres intereses en la junta, un ejecutivo y aseguramiento separado; si la fuente lo viola, se señala.
6. [PRINCE2] El tablero sigue la lógica del highlight: semáforo contra tolerancias de etapa y proyecto (50 %/100 %), hecho separado de pronóstico, decisiones visibles; mapa de calor con `estado.json.umbrales_riesgo` (por defecto alto ≥ 15, medio 6–12).
7. [PMBOK→Progress/CS] El tipo de visual sigue al tipo de dato; sin gráficos de vanidad. En ágil, burn-up con línea de alcance total y solo ítems terminados.
8. [PMBOK→Organizing/IP] El mapa poder/interés usa criterios explícitos y es de circulación restringida; la vista por actor muestra compromisos, no desempeño.
9. [Plantillas] HTML autocontenidos (sin red ni librerías, SVG en la página); datos solo por el bloque JSON, nunca editando celdas.
10. [Plantillas] Acciones por actor desde `acciones.csv` (A-###), no desde `issues.csv`.
11. Integraciones visuales opcionales (SPEC §1.10.14): si el motor está instalado se delega (no se imita su salida a mano); salida en `02-planificacion/visuales/` o `03-control/reportes/`, nunca fuera del proyecto ni en BMAD; Mermaid siempre como respaldo.
12. Datos externos solo como instantáneas fechadas de `pm-integraciones`; nunca reemplazan a los registros.
13. Transparencia de IA: fuente y fecha de corte en cada visual; `[por confirmar]` si falta; borrador hasta confirmación. Idioma del usuario.
14. Escrituras externas (portal, chat, correo, tracker) solo con confirmación explícita.

## Artefactos y plantillas
| Artefacto | Plantilla / motor | Ruta de salida | estado.json |
|---|---|---|---|
| Organigrama | `templates/diagramas-mermaid.md` §1 · archify · diagram-design · drawio | `02-planificacion/visuales/organigrama.md` | `organigrama` |
| Mapa poder/interés | §2 · diagram-design (quadrant) | `02-planificacion/visuales/mapa-stakeholders.md` (restringido) | `mapa-stakeholders` |
| PBS / WBS | §3 · `wbs.py --mermaid` · archify · diagram-design · drawio | `02-planificacion/visuales/wbs.md` | `pbs-wbs` (contenido: `pm-planificacion-por-productos`) |
| Flujo de productos | §4 · archify | `02-planificacion/visuales/flujo-productos.md` | `flujo-productos` |
| Gantt | §5 · `cpm.py --mermaid` | `02-planificacion/cronograma-gantt.md` | `cronograma` |
| Roadmap por etapas | §6 · diagram-design · visual-explainer | `02-planificacion/visuales/roadmap.md` | `roadmap` |
| Flujo de excepciones | §7 · diagram-design (swimlane) · archify | `02-planificacion/visuales/flujo-excepciones.md` | `flujo-excepciones` |
| Canvas de arranque (HTML) | `templates/canvas-arranque.html` | `01-inicio/canvas-arranque.html` | `canvas-arranque-html` |
| One-pager visual (brief, resumen) | visual-explainer; sin él, `templates/canvas-arranque.html` | `02-planificacion/visuales/one-pager-<fuente>.html` | `one-pager-<fuente>` |
| Tablero de avance | `templates/tablero-avance.html` | `03-control/reportes/AAAA-MM-DD-tablero-avance.html` | `tablero-avance` |

## Calidad
- [ ] Nodos con origen identificable; título bilingüe, leyenda, fecha de corte, fuente, BORRADOR si corresponde.
- [ ] Organigrama con tres intereses; PBS sin actividades; roadmap con puertas; Gantt con camino crítico si viene de `cpm.py`.
- [ ] Tablero: JSON válido; semáforo 50 %/100 %; umbrales en el pie; vencidas resaltadas; sección ágil si aplica; vista por actor completa; mapas si existen; instantáneas citadas.
- [ ] Salida externa verificada por su motor (guía §1.4), junto a su Mermaid; HTML interno sin conexión e imprimible en A4.
- [ ] Visuales con datos de personas marcados como restringidos.

## Escalamiento y excepciones
- Objetivo en rojo sin issue ni excepción → `pm-control` (`pm-progreso-reportes`, `pm-issues-cambios`) antes de publicar.
- Estructura que viola la separación de roles → señalar y derivar a `pm-organizacion-roles`.
- Cronograma con SS/FF, calendarios, nivelación → `pm-cronograma-estimacion`.
- Motor externo ausente, sin el tipo o fallido (tras dos reparaciones) → Mermaid/HTML interno y nota en `diario.md` con la causa.
- Visual nominativo para circulación amplia → rechazar; ofrecer versión agregada.
- Como subagente: la confirmación para compartir o publicar se devuelve como "decisión humana requerida" (SPEC §1.11).

## Ejemplos de invocación
- "Generá el tablero de avance de esta semana con mapa de calor, burn-up y la vista por actor para mandarle a cada uno su link."
- "Dibujá la EDT desde wbs.csv hasta el nivel 3 en Mermaid."
- EN: "Build a stage roadmap with the gates as milestones."
- "Hacé un one-pager visual del brief." (con `visual-explainer` configurado)
- No activa: "Redactá el highlight de la quincena con el EVM" → `pm-progreso-reportes`.

## EN summary
Turns artifacts and registers into diagrams (org chart, stakeholder map, WBS via `wbs.py --mermaid`, product flow, Gantt, roadmap with gates, exception flow, canvas, one-pager) and a self-contained HTML dashboard fed by one JSON block (RAG, milestones, P×I heat map, burn-up, "view by actor" `?actor=`).
Mermaid is the default and always-kept fallback; when archify, diagram-design or visual-explainer is configured and installed the skill must delegate to it (Skill tool, real skill name) and file the output in the project folder.
