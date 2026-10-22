# Pruebas en vivo de enrutamiento · reuniones, impacto de cambios y expediente de auditoría · 2026-10-21

- **Qué se probó:** las 6 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 115–120) para las tres
  capacidades de la 2.4.0: candidatos de decisiones y compromisos desde una transcripción (`pm-reuniones`,
  `extraccion.py`), análisis de impacto de un cambio (`pm-issues-cambios`, `impacto.py`) y expediente de auditoría
  (`pm-exportar`, `paquete.py auditoria`). Como cambiaron las descripciones de `pm-reuniones` y `pm-exportar`, se volvieron
  a correr las frases existentes de esas skills (13, 26, 34, 44, 52) y las de control que podían captar "auditoría"
  (35 y 58 de `pm-calidad`; 112, "auditor", de `pm-progreso-reportes`).
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids …` con Claude Code 2.1.306 real
  (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture
  BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripciones probadas:**
  - `pm-reuniones`: "Actas desde transcripciones o notas: decisiones, compromisos A-###, riesgos, lecciones, clima. Usar:
    acta, minuta, transcripción, acuerdos, action items, minutes, meeting decisions. No: matriz de
    comunicación→pm-comunicacion-stakeholders."
  - `pm-exportar`: "Exportados Office, paquetes ZIP de puerta o cierre y expediente de auditoría. Usar: exportar a Word,
    Excel, PowerPoint, paquete de puerta, gate package, audit pack. No: tablero→pm-visuales; informe→pm-progreso-reportes."
  - `pm-issues-cambios`: sin cambios.
- **Resultado final: 6/6 frases nuevas OK y 8/8 de regresión OK**, con la frase 116 reformulada (ver abajo). La 115 corrió
  una vez con la descripción anterior de `pm-reuniones` y otra con la nueva.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 115 | Pasame las decisiones y compromisos de la transcripción del comité de ayer, con responsable y fecha, y preguntame antes de registrarlos | pm-reuniones | pm-reuniones | OK (2/2 corridas) |
| 116 | Process yesterday's steering committee transcript and propose the decisions, owners and due dates for me to confirm before you log anything | pm-reuniones | pm-reuniones | OK (3/3 corridas) |
| 117 | Analizá el impacto del cambio C-004 en el camino crítico, el presupuesto de cambio y el VAN, y decime quién lo decide | pm-issues-cambios | pm-issues-cambios | OK |
| 118 | What is the impact of change request C-002 on the schedule, the change budget and the business case, and who has to approve it? | pm-issues-cambios | pm-issues-cambios | OK |
| 119 | Armá el expediente de auditoría del proyecto para la PMO con decisiones, líneas base, aprobaciones y evidencia de las puertas | pm-exportar | pm-exportar | OK (2/2 corridas) |
| 120 | Prepare a due diligence audit pack with the decision log, baselines and gate evidence, with hashes we can verify | pm-exportar | pm-exportar | OK (2/2 corridas) |

Regresión tras cambiar las descripciones (una corrida): 13, 26, 44 y 52 → `pm-reuniones`; 34 → `pm-exportar`; 35 y 58 →
`pm-calidad`; 112 → `pm-progreso-reportes`: 8/8 OK más 115, 119 y 120 repetidas.

Observaciones:
- **La 116 se reformuló dos veces.** Primera versión, "From this meeting transcript, pull the decisions, owners and due
  dates and ask me before logging them" (sin transcripción): SIN SKILL (el modelo pidió la transcripción). Segunda, con
  dos líneas de transcripción pegadas: 2 OK y 2 SIN SKILL en 4 corridas; en las fallidas el modelo extrajo él mismo la
  decisión y la acción de un texto de dos líneas y preguntó antes de registrar, sin cargar la skill (no registró nada).
  La versión final, que nombra la transcripción del comité como un pedido de trabajo, salió 3/3 OK. Lectura: un texto
  pegado muy corto puede resolverse sin la skill; con una transcripción real (archivo o reunión) la skill se elige.
- El "audit pack" en inglés y el "expediente de auditoría" no los captó `pm-calidad` (auditoría de calidad) ni
  `pm-progreso-reportes` (112, "auditor").
- Pocas corridas por frase: la variabilidad del modelo no está medida. Antes de publicar la versión, correr
  `suite.py todo`.
