# Guía del puente BMAD · BMAD bridge guide

## 1. Formatos que reconoce el script
| Elemento | v6.11–6.12 | v4 |
|---|---|---|
| Configuración | `_bmad/<módulo>/config.yaml`; capas TOML `_bmad/config.toml`, `config.user.toml`, `_bmad/custom/config*.toml` (mandan las personalizaciones). Versión: `_bmad/_config/manifest.yaml` (`installation.version` y una por módulo); respaldo: cabecera `# Version:` de `_bmad/<módulo>/config.yaml` | `.bmad-core/core-config.yaml` (`prdFile`, `prdSharded`, `prdShardedLocation`, `architectureFile`, `devStoryLocation`) |
| Salidas | `output_folder` (por defecto `_bmad-output`), `planning_artifacts`, `implementation_artifacts` | `docs/` |
| Brief de producto | `planning-artifacts/briefs/brief-<proyecto>-<fecha>/brief.md` | `docs/brief.md` o `docs/project-brief.md` |
| PRD | `planning-artifacts/prds/prd-<proyecto>-<fecha>/prd.md` (la carpeta más reciente es la vigente) | `docs/prd.md` o fragmentos en `docs/prd/` |
| Arquitectura | `planning-artifacts/architecture/architecture-<proyecto>-<fecha>/ARCHITECTURE-SPINE.md` | `docs/architecture.md` o `docs/architecture/` |
| UX | `planning-artifacts/ux-designs/ux-<proyecto>-<fecha>/DESIGN.md`, `EXPERIENCE.md` | `docs/front-end-spec.md` |
| Épicas | `planning-artifacts/epics.md` (`status: final`; `## Epic N:` / `### Story N.M:`). 6.12 declara la cobertura **por épica**: `### FR Coverage Map` con `FR1: Epic 1 - …` y `**FRs covered:** FR1, FR2` en la `## Epic List`; las historias no citan FR. Si el mapa nombra `Story N.M`, se traza a la historia | `docs/prd/epic-*.md` |
| Estado | `implementation-artifacts/sprint-status.yaml` → `development_status` (`epic-N`, `N-M-slug`, `epic-N-retrospective`). La clave conserva tildes y ñ, se corta a 60 caracteres y admite sufijo (`2-6a-…`); el puente usa esa clave tal cual. Historias: `spec-N-M-slug.md` de `bmad-build` (`status: draft·ready-for-dev·in-progress·in-review·done`) y `N-M-slug.md` heredados | archivos `docs/stories/N.M.story.md`, sección `Status` (Draft, Approved, InProgress, Review, Done) |
| Propuestas de cambio | `planning-artifacts/sprint-change-proposal-<fecha>.md` | — |
| Ids | `FR-n` o `FRn`, `NFR-n`, `UJ-n`, `SM-n`, `SM-Cn` (métricas de contrapeso), `AD-n`, `UX-DR-n` (se normalizan a `TIPO-n`) | `FRn:`, `NFRn:` |

Estados normalizados de historia: `backlog`, `ready-for-dev`, `in-progress`, `review`, `done` (v4: Draft→backlog, Approved→ready-for-dev, InProgress→in-progress, Review→review, Done→done; v6 heredados: drafted→ready-for-dev, contexted→in-progress; spec `in-review`→review).

Reglas de estado v6: manda `sprint-status.yaml`. Como `sprint_plan.py`, un archivo de historia aprobado (spec con `status` distinto de `draft`) sube una historia en `backlog` a `ready-for-dev`; nunca se toma `done` del spec (bmad-build lo marca `done` cuando sprint-status queda en `review`).

Trazabilidad por épica: si ninguna historia cita el id, el requisito se traza a todas las historias de las épicas que lo declaran (`nivel_traza=epica` en la matriz y en el índice; `epicas` lista cuáles). Cuenta como cubierto (planificado) y queda `terminado` solo cuando esas historias están `done`.

Fuentes de los formatos: instalación real de `bmad-method@6.12.4` (`npx bmad-method@6.12.4 install --modules bmm --tools claude-code --yes`) con artefactos escritos por sus skills (fixture `scripts/pruebas/fixtures/bmad-v6.12-real/`) y v4.44 (relevados el 2026-10-17). No trazado: `bmad-spec` (`{output_folder}/specs/spec-<slug>/SPEC.md`, ids `CAP-n`, `stories.yaml`). BMAD cambia en casi cada versión menor; si el equipo actualiza BMAD, correr `inventario` y revisar antes de la siguiente puerta.

## 2. Mapeo a PRINCE2 (qué se espera en cada momento)
| Momento PRINCE2 | Artefacto BMAD esperado | Uso en pm-method |
|---|---|---|
| SU (pre-proyecto) | brief de producto (borrador) | insumo del project brief y de la descripción del producto del proyecto (`pm-mandato-y-brief`) |
| Etapa 1, iniciación (IP) | PRD `final`; arquitectura suficiente para estimar; épicas iniciales | PBS y descripciones de producto citan FR/NFR; estimación y plan del proyecto; riesgos desde AD; línea base del PRD en `autorizar-proyecto` |
| Límite de etapa (SB) | épicas e historias de la siguiente etapa; resultado del gate de preparación del sprint planning (PASS/CONCERNS/FAIL) | plan de etapa y release plan; el veredicto se registra con `puertas.py preparacion-bmad` (FAIL bloquea, CONCERNS es condición de `autorizar-etapa`; ver `docs/PUERTAS.md`) |
| Control de etapa (CS) / MP | `sprint-status.yaml`, historias | paquetes de trabajo = iteraciones; checkpoint y highlight con `avance-bmad.csv`; calidad por DoD y code review |
| Cambio | PRD/arquitectura modificados, Sprint Change Proposal | `verificar` → issue `solicitud-cambio` → autoridad de cambio → nueva línea base |
| CP (cierre) | estado final, retrospectivas de épica | aceptación por requisito (matriz de trazabilidad con `terminado=si`), lecciones |

## 3. Roles BMAD ↔ PRINCE2 (orientativo)
| BMAD | Equivalente en el proyecto PRINCE2 |
|---|---|
| Analyst (brief, investigación) | trabajo especializado de la etapa SU/IP, bajo el gestor; insumo del usuario sénior |
| PM (PRD) | product owner / usuario sénior delegado para el contenido; el PRD final lo aprueba quien la junta designe |
| Architect | proveedor sénior / jefe de equipo técnico |
| UX Designer | equipo especialista |
| Dev, code review | equipo de entrega (MP) dentro del paquete de trabajo |

## 4. Casos borde
- **Varios PRD fechados**: el vigente es la carpeta más reciente; las anteriores se listan como versiones previas y no se trazan.
- **PRD sin `status: final` en una puerta**: avisar; la junta puede aprobar condicionado (condición: PRD final antes de X).
- **Historias en el estado de sprint que no están en `epics.md`**: se agregan al backlog con el título deducido del slug.
- **Backlog creado con una versión anterior del puente** (claves sin tildes): esas filas quedan `retirada-en-bmad` y aparecen las claves reales; pasar a mano las columnas de gobierno y borrar las viejas.
- **Historia retirada en BMAD**: queda `retirada-en-bmad`; el PO decide quitarla (decisión `nivel=product-owner`) o reponerla vía cambio.
- **Elaboración progresiva vs cambio**: agregar detalle o criterios sin cambiar ids ni alcance es elaboración progresiva si el enfoque de issues y cambios lo declara; agregar/retirar ids es cambio de alcance.
- **BMAD no instalado pero hay documentos sueltos**: usar `pm-planificacion-por-productos`; el puente requiere `_bmad/` o `.bmad-core/`.
