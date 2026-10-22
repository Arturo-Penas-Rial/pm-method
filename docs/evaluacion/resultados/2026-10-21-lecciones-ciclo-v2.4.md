# Pruebas en vivo de enrutamiento · ciclo completo de las lecciones aprendidas · 2026-10-21

- **Qué se probó:** las 4 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 121–124) para el ciclo de las
  lecciones de la 2.4.0: candidatas desde la transcripción de una retrospectiva (`pm-reuniones`, `extraccion.py
  --tipo retrospectiva`), clasificación por impacto y uso en el plan de la etapa, verificación de las acciones y
  informe de lecciones con exportación al índice de la organización (`pm-lecciones-aprendidas`, `lecciones.py`). Como
  cambió la descripción de `pm-lecciones-aprendidas` y la fila de reuniones de la tabla de enrutamiento del
  orquestador, se volvieron a correr las frases existentes de esas skills y de la retro de sprint (13, 26, 31, 32, 44,
  52, 92, 113, 114 y 115).
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids …` con Claude Code 2.1.307 real
  (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture
  BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripción probada:**
  - `pm-lecciones-aprendidas`: "Lecciones: captura, impacto, acción, verificación, informe e índice. Usar: lección
    aprendida, lessons learned, lessons report, lecciones de la retro, verificar lección, lecciones de otros proyectos.
    No: facilitar la retro→pm-agil-hibrido."
  - `pm-reuniones` y `pm-agil-hibrido`: sin cambios.
- **Resultado: 4/4 frases nuevas OK y 10/10 de regresión OK** (una corrida cada una).

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 121 | Tengo la transcripción de la retrospectiva del sprint 4: proponeme las lecciones y las acciones de mejora con su cita antes de registrar nada | pm-reuniones (o pm-lecciones-aprendidas) | pm-lecciones-aprendidas | OK (alternativa aceptada) |
| 122 | Clasificá por impacto las lecciones de la retro y decime cuáles tiene que considerar el plan de la etapa 3 | pm-lecciones-aprendidas (o pm-plan-etapa-y-limites) | pm-lecciones-aprendidas | OK |
| 123 | Which lessons did we act on but never verify, and did the high-impact one about change control actually work? | pm-lecciones-aprendidas | pm-lecciones-aprendidas | OK |
| 124 | Generá el informe de lecciones de la etapa 2 desde el registro y exportalo al índice de lecciones de la organización | pm-lecciones-aprendidas | pm-lecciones-aprendidas | OK |

Regresión: 31 ("Hagamos la retrospectiva del sprint 3") → `pm-agil-hibrido`; 32, 92, 113 y 114 →
`pm-lecciones-aprendidas`; 13, 26, 44, 52 y 115 → `pm-reuniones`: 10/10 OK.

Observaciones:
- **La 121 admite dos skills.** Pedir candidatas desde una transcripción es trabajo de `pm-reuniones` (dueña de
  `extraccion.py`), pero cuando la transcripción es de una retrospectiva el modelo eligió `pm-lecciones-aprendidas`,
  cuyo paso 2 deriva a `extraccion.py candidatos --tipo retrospectiva`. Ambas llegan al mismo comando; la frase lleva
  las dos en el TSV.
- **Facilitar la retro sigue en `pm-agil-hibrido`** (frase 31): la descripción de `pm-lecciones-aprendidas` cambió su
  "No:" a "facilitar la retro→pm-agil-hibrido", y las lecciones que salen de ella vuelven a esta skill.
