# Pruebas en vivo de enrutamiento · skill pm-mapas-estrategicos · 2026-10-20

- **Qué se probó:** las 8 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 95–102): siete que deben
  llegar a `pm-mapas-estrategicos` (mapa de Wardley, evolución con construir o comprar, customer journey, puntos de dolor,
  service blueprint, dos en inglés) y una de control (102, "mapa de stakeholders con poder e interés") que debe seguir en
  `pm-interesados` y no ser captada por la skill nueva.
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 95,96,97,98,99,100,101,102` con Claude Code 2.1.304
  real (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el
  fixture BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripción probada:** "Mapas de Wardley y de recorrido del cliente (journey, service blueprint) desde el proyecto o
  BMAD, con controles. Usar: mapa de Wardley, evolución de componentes, customer journey, puntos de dolor. No: diagramas de
  gestión→pm-visuales." (listado total de descripciones: 6.817 de 7.500 caracteres).
- **Resultado: 8/8 OK** en una corrida.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 95 | Armá un mapa de Wardley de los componentes del portal | pm-mapas-estrategicos | pm-mapas-estrategicos | OK |
| 96 | Ubicá los componentes del producto según su evolución y decime qué conviene construir y qué comprar | pm-mapas-estrategicos (acepta pm-adquisiciones) | pm-mapas-estrategicos | OK |
| 97 | Hacé el customer journey del socio que pide un préstamo | pm-mapas-estrategicos | pm-mapas-estrategicos | OK |
| 98 | Mapeá los puntos de dolor del paciente al sacar y cancelar un turno | pm-mapas-estrategicos | pm-mapas-estrategicos | OK |
| 99 | Armemos un service blueprint del trámite con lo que pasa detrás del mostrador | pm-mapas-estrategicos | pm-mapas-estrategicos | OK |
| 100 | Draw a Wardley map of our platform showing inertia and build or buy decisions | pm-mapas-estrategicos | pm-mapas-estrategicos | OK |
| 101 | Create a customer journey map for UJ-2 with emotions and touchpoints | pm-mapas-estrategicos | pm-mapas-estrategicos | OK |
| 102 | Armá el mapa de stakeholders con poder e interés | pm-interesados (acepta pm-visuales) | pm-interesados | OK |

Observaciones:
- La frase 96 no nombra a Wardley: "evolución" y "construir y qué comprar" alcanzan para elegir la skill nueva. Un pedido
  de make-or-buy sin mapa ("¿hacemos o compramos el módulo de pagos?") sigue siendo de `pm-adquisiciones`; no se volvió a
  medir en esta corrida, que se limitó a los ids nuevos.
- La 102 confirma que "mapa" de interesados no se confunde con los mapas estratégicos.
- Una sola corrida por frase: la variabilidad del modelo no está medida. Antes de publicar una versión, correr
  `suite.py todo` (incluye las 102 frases).
