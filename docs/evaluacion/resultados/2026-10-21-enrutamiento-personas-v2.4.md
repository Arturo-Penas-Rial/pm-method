# Pruebas en vivo de enrutamiento · personas de usuario y mapa capacidad × persona (pm-interesados) · 2026-10-21

- **Qué se probó:** las 3 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 105 a 107), dos en español y
  una en inglés, que piden definir personas de usuario y mapearlas a requisitos y épicas, contar los Must por persona y
  derivar personas de los recorridos de usuario de BMAD; las tres deben llegar a `pm-interesados`.
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 105,106,107` con Claude Code 2.1.306 real
  (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture
  BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripción probada:** "Maestro de interesados: poder/interés, RACI (WBS, PRD, OKR), estereotipos, preferencias y personas de usuario × capacidades. Usar: interesados, stakeholders, RACI, preferencias, personas. No: enviar comunicados→pm-comunicacion-stakeholders."
  (listado total de descripciones: 6.898 de 7.500 caracteres al momento de la corrida).
- **Resultado: 3/3 OK** en una corrida.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 105 | Definí las personas de usuario del portal y mapeá qué requisitos pide, usa o aprovecha cada una | pm-interesados | pm-interesados | OK |
| 106 | ¿Cuántos requisitos Must tiene cada persona de usuario y qué beneficios se le vinculan? | pm-interesados | pm-interesados | OK |
| 107 | Create user personas from the BMAD user journeys and map them to the epics they use | pm-interesados | pm-interesados | OK |

Observaciones:
- La 107 nombra BMAD y los recorridos de usuario, que también podrían atraer a `pm-bmad-puente` o a
  `pm-mapas-estrategicos` (recorrido del cliente); eligió `pm-interesados`.
- La 106 menciona Must y beneficios, vocabulario de `pm-agil-hibrido` y `pm-caso-de-negocio`; eligió `pm-interesados`.
- Una sola corrida por frase: la variabilidad del modelo no está medida. Antes de publicar la versión, correr
  `suite.py todo` (incluye todas las frases).
