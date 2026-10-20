# Pruebas en vivo de enrutamiento tras el cambio del hook de inicio · pm-method 2.3.0 · 2026-10-20

- **Qué cambió:** `hooks/inicio.py` agrega el resumen de contexto derivado de los registros (`estado.py contexto`) y la
  precedencia de `estado.json` y los registros sobre la memoria del cliente; `hooks/guardian.py` pide confirmación para
  `envios.py aprobar` y `enviar --confirmar` y evalúa los comandos por segmento. Como el texto de inicio cambia, se
  repite el enrutamiento.
- **Qué se probó:** 14 frases variadas de `docs/evaluacion/frases-enrutamiento.tsv`: las tres del orquestador
  ("¿qué sigue?", "¿cómo venimos?" en español e inglés), dos preguntas de método (`pm-knowledge`, español e inglés),
  la sanidad antes de la junta, la decisión de la junta, el envío de comunicaciones y productos concretos (riesgos,
  highlight, issue, business case, brief, exportar).
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 18,55,56,19,39,11,3,53,21,64,34,9,27,7` con
  Claude Code 2.1.304 real (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre el proyecto
  desechable de la suite (fixture BMAD 6.12.4, gestión en iniciación con un riesgo registrado). Se compara la primera
  skill elegida; la sesión se corta apenas elige.
- **Resultado: 14/14 OK** (32 s en total, en paralelo).

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 3 | Identificá los riesgos del proyecto y su matriz probabilidad impacto | pm-riesgos | pm-riesgos | OK |
| 7 | Prepará el highlight report de esta semana con valor ganado | pm-progreso-reportes | pm-progreso-reportes | OK |
| 9 | El proveedor entregó un módulo que no cumple la especificación | pm-issues-cambios | pm-issues-cambios | OK |
| 11 | Escribí el business case con VAN y payback | pm-caso-de-negocio | pm-caso-de-negocio | OK |
| 18 | ¿Qué sigue en mi proyecto? | pm-orquestador | pm-orquestador | OK |
| 19 | ¿Qué es la gestión por excepción? | pm-knowledge | pm-knowledge | OK |
| 21 | La junta tiene que aprobar el fin de etapa, prepará la decisión | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 27 | Armá el project brief y el canvas de arranque | pm-mandato-y-brief | pm-mandato-y-brief | OK |
| 34 | Exportá los registros a Excel y armá el ZIP para la junta | pm-exportar | pm-exportar | OK |
| 39 | Who approves a stage plan in PRINCE2? | pm-knowledge | pm-knowledge | OK |
| 53 | Revisá la sanidad del proyecto antes de la junta | pm-sanidad | pm-sanidad | OK |
| 55 | ¿Cómo venimos con el proyecto? | pm-orquestador | pm-orquestador | OK |
| 56 | How are we doing on the project? | pm-orquestador | pm-orquestador | OK |
| 64 | Send the approved status update to the steering committee by email | pm-comunicacion-stakeholders | pm-comunicacion-stakeholders | OK |

Comprobaciones adicionales con Claude Code 2.1.304:
- **El resumen derivado llega al modelo como contexto:** en una sesión sobre el mismo proyecto (modelo `haiku`), el
  pedido de copiar las líneas "Abiertos:" y "Próxima puerta" del contexto de pm-method devolvió `Abiertos: riesgos 1.` y
  `Próxima puerta: autorizar-proyecto (…)`, sin que el texto se tratara como instrucción sospechosa.
- **`permissionDecision: "ask"` de un hook `PreToolUse`** (plugin mínimo de prueba que pedía confirmación para un
  `echo`): con `-p` y `--allowedTools Bash` el comando se denegó (`permission_denials`); con
  `--dangerously-skip-permissions` (`bypassPermissions`) no hubo pedido y el comando corrió. En una sesión interactiva
  la documentación indica que se muestra el pedido de permiso habitual. Por eso la suite en vivo, que corre con
  `--dangerously-skip-permissions`, no se ve afectada por el nuevo pedido de confirmación de `envios.py`.

Sin repetir en esta corrida: guardarraíles, idioma y los escenarios de robustez (`suite.py todo` y `robustez`, antes
de publicar una versión).
