# Prueba en vivo · pm-kb por MCP + diagram-design + scripts de pm-method · 2026-10-29 (2.6.2 en estabilización)

- **Qué se probó:** la interacción de tres opcionales en una sola sesión de Claude Code: el plugin (`--plugin-dir`), el
  MCP de pm-kb por stdio y la skill externa diagram-design. Pedido (un turno, en español): «Con el MCP pm-kb (proyecto
  portal-vivo), buscá los riesgos de mayor exposición del proyecto y citá cada uno con la cita que devuelve pm-kb.
  Después dibujá un diagrama de esos riesgos con la skill diagram-design (está configurada en
  integraciones.diagramas), siguiendo el contrato de pm-visuales: respaldo Mermaid primero, salida en
  gestion/02-planificacion/visuales/ y registro del artefacto. Sin red: fuentes del sistema. No me hagas preguntas: usá
  el estilo por defecto y anotá los supuestos.»
- **Cómo:** `scripts/pruebas_vivo/vivo.py` (`Sesion.turno`, `claude -p … --output-format stream-json`) con Claude Code
  2.1.312, modelo por defecto de la CLI (`claude-sonnet-5-5`; la CLI usó además `claude-haiku-5-5` para tareas
  internas), `--max-turns 60`, y `--mcp-config <archivo descartable> --strict-mcp-config` con un único servidor
  `pm-kb` (`pm-kb/pm-kb mcp`, `PMKB_PROYECTOS=portal-vivo`). Proyecto desechable: el de la guía E2E-1 (copia del fixture
  BMAD 6.12.4 real con `gestion/`), indexado como `portal-vivo` en una base de prueba (búsqueda léxica, sin modelos);
  diagram-design 2.6.136 (commit `0cf73c3`, la copia de la imagen `pm-method:2.6.1`) en `.claude/skills/` del
  proyecto y `estado.py integracion diagramas=diagram-design` (INS-03: «instalada: invocar como 'diagram-design'»). No
  se tocó la configuración global de Claude Code: el MCP y la skill vivían en archivos descartables de la prueba.
- **Resultado: OK con una observación de exactitud del modelo.** 19 turnos, 80,6 s, **USD 0,4621** (informado por la
  CLI en `total_cost_usd`).

| Comprobación | Resultado |
|---|---|
| Usa el MCP de pm-kb (no lee los CSV a mano para buscar) | `mcp__pm-kb__buscar` ×2 (con `registro: riesgos`) y `mcp__pm-kb__ficha` ×4 (R-001, R-002, R-003, R-007) |
| Usa las skills esperadas | `pm-method:pm-visuales` y después `diagram-design` (herramienta Skill) |
| Contrato de pm-visuales §1.3 | respaldo primero (`02-planificacion/visuales/riesgos-exposicion.md`: tabla intermedia con la cita de pm-kb de cada riesgo + `quadrantChart`); diagrama dibujado desde la tabla intermedia (diagram-design no importa `quadrantChart`, guía §1.2); salida `02-planificacion/visuales/riesgos-exposicion.html`; «BORRADOR», fecha de corte y fuente en el pie; fuentes del sistema |
| Verificación del motor | `self_check.py --offline` → `OK` (repetido por la prueba: `OK`; `export_png.py` en la imagen dibuja el cuadrante con los 4 riesgos) |
| Registro por los scripts | `estado.py --proyecto gestion artefacto riesgos-exposicion --ruta … --estado borrador`; `sanidad.py` después: 0 ERROR, sin ART-01 |
| Ninguna escritura fuera de los scripts | archivos cambiados: los dos de `visuales/` (Write), `estado.json` y `.bitacora.jsonl` (por `estado.py`); `registro.py historial` → «cadena íntegra (132 líneas) y cada archivo coincide con su última escritura anotada»; ningún Write/Edit sobre `estado.json` ni registros; ninguna negación del guardián |
| Sin red | ningún `<link>` a Google Fonts en la salida |

Observaciones:
- **Exactitud (modelo):** la tabla dice «amenazas abiertas» pero incluye R-005 con estado «abierto», cuando el registro
  dice `retirado`, y deja fuera R-002 y R-004 (`en-seguimiento`, puntuación 8); R-001 figura correctamente como
  `ocurrido`. Causa: para R-005 solo vio el extracto de `buscar`, que se centra en los términos encontrados y ese
  fragmento no traía `estado:`; no pidió su `ficha` (sí la de los otros tres). Propuesta para el autor (no aplicada:
  cambia los extractos que muestran las guías): en las filas de registro, anteponer siempre `estado:` (y el título) al
  extracto de `buscar`, o pedir en `pm-visuales`/`pm-kb` que un listado por estado salga de `registro.py listar` o de la
  `ficha` de cada id.
- Un `Bash` terminó con código 1 por un `tail -5 gestion/03-control/diario.md` del modelo (la ruta real es
  `03-control/registros/diario.md`); no afectó el resultado.
- R-007 y R-003 comparten la misma celda (P2 × I5): el diagrama los separa apenas y lo aclara en el pie.

Archivos de la corrida (fuera del repositorio, descartables): flujo `stream.jsonl`, resumen y el proyecto de trabajo.
