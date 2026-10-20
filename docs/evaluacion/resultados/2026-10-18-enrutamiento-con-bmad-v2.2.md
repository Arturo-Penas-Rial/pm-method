# Pruebas en vivo · enrutamiento con BMAD instalado en el mismo proyecto · pm-method 2.2.0 · 2026-10-18

**Pregunta:** ¿los disparadores de pm-method siguen funcionando cuando en el mismo proyecto están instaladas las skills
de BMAD, que tratan temas vecinos (PRD, brief, sprint planning, retrospectiva, correct course, revisión, ayuda)?

**Instalación de BMAD:** `npx bmad-method@6.12.4 install --modules bmm --tools claude-code --yes` en una carpeta aparte;
dejó 29 skills en `.claude/skills/` (bmad-prd, bmad-product-brief, bmad-sprint-planning, bmad-retrospective,
bmad-correct-course, bmad-review, bmad-code-review, bmad-help, bmad-agent-pm, etc.), con 6.952 caracteres de
descripciones; pm-method suma 6.582. Se copiaron al proyecto base con la opción nueva `suite.py --skills-extra`.
Comprobación: el evento de inicio de Claude Code listó 104 skills disponibles (30 de BMAD, 38 de pm-method y las del
sistema), es decir, las skills de BMAD estaban cargadas.

**Selección:** 25 frases del lote con mayor riesgo de confusión con BMAD (especificación, backlog y sprints, brief,
retrospectiva, calidad y revisión, fin de etapa, "¿qué sigue?" frente a bmad-help).

**Resultado: 25/25** (Claude Code 2.1.302, modelo por defecto, una corrida).

| id | frase | esperada | elegida | veredicto |
|---|---|---|---|---|
| 9 | El proveedor entregó un módulo que no cumple la especificación | pm-issues-cambios | pm-issues-cambios | OK |
| 10 | El cliente pide agregar pagos en línea, ¿cómo lo tramito? | pm-issues-cambios | pm-issues-cambios | OK |
| 13 | Procesá la transcripción del comité de ayer y sacá las acciones | pm-reuniones | pm-reuniones | OK |
| 14 | Sincronizá el backlog con las historias de BMAD | pm-bmad-puente | pm-bmad-puente | OK |
| 15 | ¿Qué requisitos del PRD no tienen historias? | pm-bmad-puente | pm-bmad-puente | OK |
| 18 | ¿Qué sigue en mi proyecto? | pm-orquestador | pm-orquestador | OK |
| 22 | Hagamos el plan de la próxima etapa | pm-plan-etapa-y-limites | pm-plan-etapa-y-limites | OK |
| 27 | Armá el project brief y el canvas de arranque | pm-mandato-y-brief | pm-mandato-y-brief | OK |
| 28 | Necesito el PID completo para que lo firme el ejecutivo | pm-acta-constitucion | pm-acta-constitucion | OK |
| 30 | Priorizá el backlog con MoSCoW y armá el release plan | pm-agil-hibrido | pm-agil-hibrido | OK |
| 31 | Hagamos la retrospectiva del sprint 3 | pm-agil-hibrido | pm-agil-hibrido | OK |
| 32 | Recopilá las lecciones aprendidas de la etapa | pm-lecciones-aprendidas | pm-lecciones-aprendidas | OK |
| 35 | Definí los criterios de aceptación y el registro de calidad | pm-calidad | pm-calidad | OK |
| 37 | Estimá el esfuerzo con PERT de los paquetes | pm-cronograma-estimacion | pm-cronograma-estimacion | OK |
| 45 | Did the PRD change since the board approved it? | pm-bmad-puente | pm-bmad-puente | OK |
| 47 | Prepare the end stage report | pm-plan-etapa-y-limites | pm-plan-etapa-y-limites | OK |
| 53 | Revisá la sanidad del proyecto antes de la junta | pm-sanidad | pm-sanidad | OK |
| 54 | Run a consistency check between the PRD and our plan | pm-sanidad | pm-sanidad | OK |
| 55 | ¿Cómo venimos con el proyecto? | pm-orquestador | pm-orquestador | OK |
| 56 | How are we doing on the project? | pm-orquestador | pm-orquestador | OK |
| 57 | Set up the backlog and plan the next sprints from the BMAD stories | pm-agil-hibrido | pm-agil-hibrido | OK |
| 58 | Revisá la calidad del entregable de integración antes de aceptarlo | pm-calidad | pm-calidad | OK |
| 66 | Detectá riesgos candidatos en el brief de BMAD, las actas y los ticket | pm-riesgos | pm-riesgos | OK |
| 71 | Armá el resumen del proyecto a partir del mandato que nos mandó el dir | pm-mandato-y-brief | pm-mandato-y-brief | OK |
| 89 | Cerremos el límite de etapa y prepará el informe de fin de etapa | pm-plan-etapa-y-limites | pm-plan-etapa-y-limites | OK |

Observaciones:
- Ninguna frase de gobierno se desvió a una skill de BMAD, ni siquiera las más cercanas: "project brief" (27, frente a
  bmad-product-brief), "retrospectiva del sprint" (31, frente a bmad-retrospective), "¿qué sigue?" (18, frente a
  bmad-help), "plan de los próximos sprints desde las historias de BMAD" (57, frente a bmad-sprint-planning).
- No se observó recorte del listado de skills con esta combinación (≈13.500 caracteres de descripciones de pm-method y
  BMAD). Con más módulos o repositorios de skills el total crece (INSTALACION §7.4).
- Límites: una sola corrida por frase; modelo por defecto; no se probaron frases que **deberían** ir a BMAD (por
  ejemplo, "escribí el PRD"), que por diseño de pm-method son de BMAD.
