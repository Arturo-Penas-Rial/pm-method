# Guía del puente BMAD · BMAD bridge guide

## 1. Formatos que reconoce el script
| Elemento | v6.11–6.12 | v4 |
|---|---|---|
| Configuración | `_bmad/<módulo>/config.yaml`; capas TOML `_bmad/config.toml`, `config.user.toml`, `_bmad/custom/config*.toml` (mandan las personalizaciones) | `.bmad-core/core-config.yaml` (`prdFile`, `prdSharded`, `prdShardedLocation`, `architectureFile`, `devStoryLocation`) |
| Salidas | `output_folder` (por defecto `_bmad-output`), `planning_artifacts`, `implementation_artifacts` | `docs/` |
| Brief de producto | `planning-artifacts/briefs/brief-<proyecto>-<fecha>/brief.md` | `docs/brief.md` o `docs/project-brief.md` |
| PRD | `planning-artifacts/prds/prd-<proyecto>-<fecha>/prd.md` (la carpeta más reciente es la vigente) | `docs/prd.md` o fragmentos en `docs/prd/` |
| Arquitectura | `planning-artifacts/architecture/architecture-<proyecto>-<fecha>/ARCHITECTURE-SPINE.md` | `docs/architecture.md` o `docs/architecture/` |
| UX | `planning-artifacts/ux-designs/ux-<proyecto>-<fecha>/DESIGN.md`, `EXPERIENCE.md` | `docs/front-end-spec.md` |
| Épicas | `planning-artifacts/epics.md` (`## Epic N:` / `### Story N.M:`, mapa de cobertura `FR1: Epic 1 (Story 1.1)`) | `docs/prd/epic-*.md` |
| Estado | `implementation-artifacts/sprint-status.yaml` → `development_status` (`epic-N`, `N-M-slug`, `epic-N-retrospective`) | archivos `docs/stories/N.M.story.md`, sección `Status` (Draft, Approved, InProgress, Review, Done) |
| Propuestas de cambio | `planning-artifacts/sprint-change-proposal-<fecha>.md` | — |
| Ids | `FR-n` o `FRn`, `NFR-n`, `UJ-n`, `SM-n`, `AD-n`, `UX-DR-n` (se normalizan a `TIPO-n`) | `FRn:`, `NFRn:` |

Estados normalizados de historia: `backlog`, `ready-for-dev`, `in-progress`, `review`, `done` (v4: Draft→backlog, Approved→ready-for-dev, InProgress→in-progress, Review→review, Done→done).

Fuentes de los formatos: paquete npm `bmad-method@6.12.4` y v4.44 (relevados el 2026-10-17). BMAD cambia en casi cada versión menor; si el equipo actualiza BMAD, correr `inventario` y revisar antes de la siguiente puerta.

## 2. Mapeo a PRINCE2 (qué se espera en cada momento)
| Momento PRINCE2 | Artefacto BMAD esperado | Uso en pm-method |
|---|---|---|
| SU (pre-proyecto) | brief de producto (borrador) | insumo del project brief y de la descripción del producto del proyecto (`pm-mandato-y-brief`) |
| Etapa 1, iniciación (IP) | PRD `final`; arquitectura suficiente para estimar; épicas iniciales | PBS y descripciones de producto citan FR/NFR; estimación y plan del proyecto; riesgos desde AD; línea base del PRD en `autorizar-proyecto` |
| Límite de etapa (SB) | épicas e historias de la siguiente etapa; resultado del gate de preparación del sprint planning (PASS/CONCERNS/FAIL) | plan de etapa y release plan; CONCERNS/FAIL = riesgo o condición de `autorizar-etapa` |
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
- **Historia retirada en BMAD**: queda `retirada-en-bmad`; el PO decide quitarla (decisión `nivel=product-owner`) o reponerla vía cambio.
- **Elaboración progresiva vs cambio**: agregar detalle o criterios sin cambiar ids ni alcance es elaboración progresiva si el enfoque de issues y cambios lo declara; agregar/retirar ids es cambio de alcance.
- **BMAD no instalado pero hay documentos sueltos**: usar `pm-planificacion-por-productos`; el puente requiere `_bmad/` o `.bmad-core/`.
