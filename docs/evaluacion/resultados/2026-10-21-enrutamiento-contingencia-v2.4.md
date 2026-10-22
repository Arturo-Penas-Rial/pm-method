# Pruebas en vivo de enrutamiento · opciones de respuesta y plan de contingencia (pm-riesgos) · 2026-10-21

- **Qué se probó:** las 2 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 103 y 104), una en español y
  una en inglés, que piden comparar opciones de respuesta de riesgos altos y redactar un plan de contingencia; las dos
  deben llegar a `pm-riesgos`.
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 103,104` con Claude Code 2.1.306 real
  (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture
  BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripción probada:** "Registro y respuestas de riesgo PRINCE2. Usar: riesgo, risk register, matriz P×I, EMV,
  respuesta al riesgo, plan de contingencia, oportunidad, informe o auditoría. No: issue ya ocurrido→pm-issues-cambios."
  (listado total de descripciones: 6.828 de 7.500 caracteres al momento de la corrida).
- **Resultado: 2/2 OK** en una corrida.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 103 | Para los riesgos altos compará evitar, reducir, transferir y aceptar con contingencia, y decime cuál conviene | pm-riesgos | pm-riesgos | OK |
| 104 | Write the contingency plan for R-003 with a measurable trigger and funding from the risk budget | pm-riesgos | pm-riesgos | OK |

Observaciones:
- La 104 menciona "risk budget" y "funding", que también podrían atraer a `pm-costos-presupuesto`; eligió `pm-riesgos`.
- Una sola corrida por frase: la variabilidad del modelo no está medida. Antes de publicar la versión, correr
  `suite.py todo` (incluye todas las frases).
