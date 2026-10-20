# Prueba en vivo de integración cruzada con BMAD instalado y control del contexto · 2026-10-20

- **Qué se probó:** un pedido que cruza tres skills de pm-method sobre la especificación de BMAD, con las 29 skills de
  BMAD 6.12.4 instaladas en el mismo proyecto: «Con el PRD de BMAD armá el recorrido del cliente del préstamo (UJ-2),
  registrá los riesgos que surjan y decime el estado del proyecto. (carpeta ./gestion)».
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py integracion --skills-extra <proyecto con BMAD>/.claude/skills` con
  Claude Code 2.1.304 real (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto
  desechable creado desde el fixture BMAD 6.12.4 (iniciación aprobada, un riesgo). El escenario está en
  `scripts/pruebas_vivo/escenarios.py` (`integracion`) y verifica el estado resultante con comprobaciones deterministas.
- **Medición del contexto:** `vivo.py` registra, para cada llamada al modelo, los tokens de entrada que ocupa
  (`input_tokens + cache_creation_input_tokens + cache_read_input_tokens` del evento `assistant` del flujo
  `stream-json`), por separado para el hilo principal y para los subagentes.
- **Topes declarados** (constantes del escenario): primera llamada ≤ 50.000 tokens; cualquier llamada ≤ 120.000; ningún
  salto entre dos llamadas seguidas > 20.000 (una salida de herramienta o un archivo leído de una vez).
- **Resultado: 12/12** (segunda corrida, con el chequeo de skills corregido; ver la tabla de corridas). Costo total de las
  dos corridas: USD 0,57.

## Corridas

| Corrida | Llamadas al modelo | Contexto 1.ª llamada | Contexto máximo | Subagentes | USD | Duración | Resultado |
|---|---|---|---|---|---|---|---|
| 1 | 14 | 45.503 | 66.064 | ninguno | 0,30 | 81 s | 11/12: el chequeo exigía la skill `pm-riesgos`; el modelo registró los riesgos con `registro.py` dentro de `pm-mapas-estrategicos`, que es el paso «dolores → riesgos» de esa skill. Se corrigió el chequeo |
| 2 | 12 | 45.505 | 64.177 | ninguno | 0,26 | 67 s | 11/12 al correr; la expresión del chequeo corregido no abarcaba un comando de dos líneas (`S=…/registro.py; …` y en la línea siguiente `python3 $S $P agregar riesgos`). Corregida (`re.S`) y reevaluada sobre los comandos registrados: **12/12** |

Comprobaciones (corrida 2):

| Comprobación | Resultado |
|---|---|
| BMAD instalado en el proyecto (29 skills `bmad-*` en `.claude/skills`) | OK |
| Usa `pm-mapas-estrategicos`; los riesgos pasan por `registro.py`; ninguna skill de BMAD invocada | OK (tras la corrección del chequeo) |
| Recorrido UJ-2 creado desde BMAD en `02-planificacion/mapas/` | OK |
| Lee BMAD por el puente (`bmad.py recorridos`) y no abre `_bmad-output/` ni `spec-index.json` enteros | OK |
| Riesgos registrados (o presentados para confirmar) | OK: tres riesgos nuevos (R-002 a R-004) cuyas causas citan UJ-2, FR-7, SM-3, SM-C1 y el riesgo previo R-001 |
| Informa el estado (fase, etapa, próxima puerta) | OK: iniciación, `autorizar-proyecto` bloqueada y por qué |
| PRD y épicas de BMAD sin cambios | OK |
| Sin ERROR nuevo en sanidad | OK |
| Contexto: primera llamada ≤ 50.000 | OK (45.505) |
| Contexto: cada llamada ≤ 120.000 | OK (64.177) |
| Contexto: ningún salto > 20.000 entre llamadas seguidas | OK |
| Costo < USD 3 | OK (0,26) |

## Línea de base del contexto (mismo proyecto, pedido mínimo «Respondé solo: hola»)

| Configuración | Tokens de la primera llamada | Diferencia |
|---|---|---|
| Claude Code sin el plugin | 38.337 | — |
| Con pm-method (`--plugin-dir`): hooks de inicio e idioma, listado de 33 skills invocables y 6 agentes | 43.754 | +5.417 |
| Con pm-method y las 29 skills de BMAD 6.12.4 en `.claude/skills` | 45.437 | +1.683 por BMAD |

Lo que suma pm-method antes del primer pedido (≈ 5.400 tokens) es el 0,5 % de una ventana de 1 millón de tokens y el
2,7 % de una de 200.000. Durante la tarea el contexto creció de 45.500 a 64.200 tokens en 12 llamadas (≈ 1.560 por
llamada): las salidas de los scripts están acotadas (`docs/PRUEBAS.md` §2.2) y la especificación se leyó por el puente.

## Observaciones

- El modelo marcó como supuestos propios las emociones del recorrido (el PRD no trae fuente) y lo dijo en la respuesta,
  como pide la guía de la skill.
- Registró los riesgos sin pedir confirmación porque el pedido decía «registrá»; con un pedido de identificación sin esa
  orden, la regla de `pm-riesgos` es presentar candidatos y registrar después de la evaluación humana.
- Para conocer los valores admitidos de `tipo_causa` y `kano` buscó en `mapas.py` con `grep` en lugar de leer la guía
  (`references/guia.md` §4 los lista). Es una lectura acotada y no afectó el contexto, pero muestra que la consulta
  directa al script es una ruta que el modelo elige.
- `riesgos.csv` se leyó entero con `cat` (2 filas en el proyecto de prueba). Con registros grandes, el escenario
  `escala` comprueba que no se lean enteros.
