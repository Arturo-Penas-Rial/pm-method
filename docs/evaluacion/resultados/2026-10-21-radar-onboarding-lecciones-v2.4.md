# Pruebas en vivo de enrutamiento · radar de atención, briefing de incorporación y lecciones entre proyectos · 2026-10-21

- **Qué se probó:** las 7 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 108–114) y 5 frases de control
  que podían cambiar con la línea de radar del hook de inicio y con las descripciones tocadas: 18 («¿Qué sigue?»), 55 y 56
  («¿Cómo venimos?» en español e inglés), 86 (informe de estado → `pm-progreso-reportes`) y 92 (registro de lecciones
  de la etapa → `pm-lecciones-aprendidas`).
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 108,109,110,111,112,113,114,18,55,56,86,92 --par 6`
  con Claude Code 2.1.306 real (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre el proyecto
  desechable de la suite (fixture BMAD 6.12.4, etapa de iniciación, un riesgo). Se compara la primera skill elegida; la
  sesión se corta apenas elige. El hook de inicio agregó la línea de radar del proyecto base: «pm-method · radar al
  2026-10-21: decidir 0 · escalar 0 · desbloquear 1 (R-001) · vigilar 0; detalle, responsables y siguiente paso:
  pm-orquestador (estado.py radar).»
- **Descripciones probadas** (listado total: 6.898 de 7.500 caracteres):
  - `pm-orquestador`: «… Usar: qué sigue, cómo venimos, qué decido hoy, radar, next step, how are we doing, gestionar el
    proyecto. …»
  - `pm-progreso-reportes`: «… Usar: checkpoint, highlight report, status report, valor ganado, EVM, burn-up, pronóstico,
    briefing de incorporación. …»
  - `pm-lecciones-aprendidas`: «… Usar: lección aprendida, lessons learned, lessons report, retro de etapa, lecciones de
    otros proyectos. …»
- **Resultado: 12/12 OK** en una corrida.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 108 | ¿Qué tengo que decidir, escalar y desbloquear hoy en el proyecto? | pm-orquestador | pm-orquestador | OK |
| 109 | Dame el radar del día: decisiones pendientes, excepciones y bloqueos | pm-orquestador | pm-orquestador | OK |
| 110 | What do I need to decide or unblock today on the project? | pm-orquestador | pm-orquestador | OK |
| 111 | Prepará un briefing de incorporación para la nueva integrante de la junta antes de la puerta | pm-progreso-reportes | pm-progreso-reportes | OK |
| 112 | Write an onboarding briefing for the new auditor joining before the stage gate | pm-progreso-reportes | pm-progreso-reportes | OK |
| 113 | ¿Qué lecciones de otros proyectos sobre integraciones deberíamos tener en cuenta al arrancar? | pm-lecciones-aprendidas (acepta pm-mandato-y-brief) | pm-lecciones-aprendidas | OK |
| 114 | Search our previous projects' lessons learned about integration delays and add the relevant ones | pm-lecciones-aprendidas | pm-lecciones-aprendidas | OK |
| 18 | ¿Qué sigue en mi proyecto? | pm-orquestador | pm-orquestador | OK |
| 55 | ¿Cómo venimos con el proyecto? | pm-orquestador | pm-orquestador | OK |
| 56 | How are we doing on the project? | pm-orquestador | pm-orquestador | OK |
| 86 | Mandame el informe de estado del proyecto | pm-progreso-reportes (acepta pm-reporte, pm-estado, pm-orquestador) | pm-progreso-reportes | OK |
| 92 | Hacé el registro de lecciones aprendidas de la etapa | pm-lecciones-aprendidas | pm-lecciones-aprendidas | OK |

Observaciones:
- Con la línea de radar en el contexto de inicio, el modelo no contestó «¿qué decido hoy?» de memoria: eligió
  `pm-orquestador`, que es quien corre `estado.py radar` y pregunta lo que decide la junta (la línea remite a él).
- La 112 no nombra ningún informe PRINCE2: «onboarding briefing» alcanza para `pm-progreso-reportes`, dueña de la
  plantilla `briefing-incorporacion.md`.
- La 113 llega a `pm-lecciones-aprendidas` aunque habla de arrancar (puesta en marcha, terreno de
  `pm-mandato-y-brief`); las lecciones previas del propio arranque siguen en `pm-mandato-y-brief`, que remite al buscador.
- Una sola corrida por frase: la variabilidad del modelo no está medida. Antes de publicar la versión, `suite.py todo`.
