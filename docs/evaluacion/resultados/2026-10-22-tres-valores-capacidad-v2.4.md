# Pruebas en vivo de enrutamiento · estimación de tres valores y capacidad del release (pm-cronograma-estimacion, pm-agil-hibrido) · 2026-10-22

- **Qué se probó:** las 2 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 129 y 130): estimar con tres
  valores y la fórmula declarada (triangular) con la reserva a 1σ, que debe llegar a `pm-cronograma-estimacion`, y
  verificar si los Must y Should de un release entran en sus sprints, que debe llegar a `pm-agil-hibrido` (se acepta
  `pm-cronograma-estimacion` como alternativa, porque su variante ágil también calcula iteraciones por velocidad).
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 129,130` con Claude Code 2.1.308 real
  (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture
  BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripciones:** sin cambios (las capacidades se agregaron como pasos y comandos de las skills existentes).
- **Resultado: 2/2 OK** en una corrida.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 129 | Estimá con tres valores las actividades de la etapa 2 con la fórmula triangular que fija el plan y decime la reserva de cronograma a 1σ del camino crítico | pm-cronograma-estimacion | pm-cronograma-estimacion | OK |
| 130 | Con la velocidad de 20 puntos, ¿entran los Must y Should del release 2 en sus cuatro sprints o tengo que repriorizar? | pm-agil-hibrido | pm-agil-hibrido | OK |

Observaciones:
- La 130 eligió la skill esperada aunque la descripción de `pm-cronograma-estimacion` también cubre iteraciones por
  velocidad (ejemplo en inglés de su SKILL.md).
- Una sola corrida por frase: la variabilidad del modelo no está medida. Antes de publicar la versión, correr
  `suite.py todo` (incluye todas las frases).
