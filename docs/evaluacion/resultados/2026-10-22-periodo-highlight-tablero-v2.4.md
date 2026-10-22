# Pruebas en vivo de enrutamiento · datos del período, highlight y tablero desde el dato (pm-progreso-reportes) · 2026-10-22

- **Qué se probó:** las 2 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 127 y 128), una en español y
  una en inglés: armar el highlight y el tablero desde los datos marcando el juicio del gestor, y verificar las cifras
  del EVM de un informe antes de enviarlo. Las dos deben llegar a `pm-progreso-reportes` (la 127 admite `pm-visuales`).
  Como control, las frases 67 y 86 (highlight e informe de estado), que ya llegaban a `pm-progreso-reportes`.
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 127,128,67,86` con Claude Code 2.1.308 real
  (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture
  BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripciones:** sin cambios (`pm-progreso-reportes` y `pm-visuales`); cambió el cuerpo de sus SKILL.md (paso 9 y
  regla 12; paso 4 y entradas) y el agente pm-control (paso 8).
- **Resultado: 4/4 OK** en una corrida.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 67 | Prepará el informe de aspectos destacados de esta semana para la junta | pm-progreso-reportes | pm-progreso-reportes | OK |
| 86 | Mandame el informe de estado del proyecto | pm-progreso-reportes | pm-progreso-reportes | OK |
| 127 | Armá el highlight de la quincena desde los datos y el tablero con las mismas cifras; marcá qué semáforos son juicio mío | pm-progreso-reportes | pm-progreso-reportes | OK |
| 128 | Before I send the status report to the board, check that every SPI, CPI and EAC in it matches the saved earned value cut-off | pm-progreso-reportes | pm-progreso-reportes | OK |

Observaciones:
- La 127 nombra el tablero, que también atrae a `pm-visuales`; eligió `pm-progreso-reportes`, que es la dueña del cálculo
  del período (`estado.py periodo`) y del juicio del gestor.
- Una sola corrida por frase: la variabilidad del modelo no está medida. Antes de publicar la versión, correr
  `suite.py todo` (incluye todas las frases).
