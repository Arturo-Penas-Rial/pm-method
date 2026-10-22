# Pruebas en vivo de enrutamiento · estado de productos y controles de cierre por id · 2026-10-22

- **Qué se probó:** las 2 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 125 y 126) para el estado de
  productos derivado (`estado.py productos`, `pm-paquetes-trabajo`) y los controles de cierre por id (C-03 y C-07 de
  `autorizar-cierre`, `pm-cierre-proyecto`). Las descripciones de las skills, los agentes y la tabla de enrutamiento
  del orquestador no cambiaron, por eso no se corrió regresión.
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 125,126` con Claude Code 2.1.308 real
  (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture
  BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Resultado: 2/2 OK** (una corrida cada una).

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 125 | ¿En qué estado está cada producto del Release 1? Armá el product status account y marcá lo que figura terminado o aceptado sin revisión de calidad | pm-paquetes-trabajo (o pm-calidad) | pm-paquetes-trabajo | OK |
| 126 | Antes de pedir la puerta de cierre: ¿qué requisitos Must quedan sin aceptar y qué riesgos o issues abiertos no tienen responsable en las recomendaciones de seguimiento? | pm-cierre-proyecto | pm-cierre-proyecto | OK |

Observaciones:
- **La 125 admite dos skills.** El estado de productos lo arma `pm-paquetes-trabajo` (paso 11, guía §5) y la pregunta
  por terminados o aceptados sin revisión es también de `pm-calidad` (QUA-01, QUA-04); las dos llegan a
  `estado.py productos`.
- **La 126 suma una frase propia a `pm-cierre-proyecto`**, que tenía una sola (33, «Vamos a cerrar el proyecto»).
