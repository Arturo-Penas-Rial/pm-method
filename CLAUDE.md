# CLAUDE.md · contexto para desarrollar pm-method

Este repositorio **es** el plugin pm-method (no un proyecto que lo usa). Leer esto antes de cambiar algo.

## Qué es
Plugin de Claude Code (también Cowork y Hermes) con 6 agentes, 37 skills y 3 hooks para gestión de proyectos.
Jerarquía fija, no negociable:
1. **PRINCE2 7** = método y ciclo de vida; **siempre manda**.
2. **PMBOK 8** = solo el "cómo" (técnicas) o vacíos de PRINCE2.
3. **Plantillas** (libro de Snyder) = artefactos (campos, listas), destiladas en palabras propias, nunca texto literal.
4. **BMAD** = capa de especificación de **solo lectura**, fuente única por dato (`especificacion.py`, `bmad.py`).
Bilingüe ES/EN: responder en el idioma del usuario; artefactos en `estado.json.idioma`.

## Reglas del autor (obligatorias)
- Exactitud ante todo: no inventar fuentes, URLs, comandos, flags, funciones ni cifras; verificar con `--help`, el
  código o la fuente; marcar `[verificar]` lo no verificado; preguntar ante vacíos.
- Documentación en español (con resúmenes "EN:" donde ayude).
- Nunca agregar marca o logo de empresa alguna (los informes llevan espacio para el logo de IEEE).
- Nunca escribir credenciales en archivos, commits ni mensajes.

## Mapa del repositorio
- `.claude-plugin/` plugin.json y marketplace.json (versión: debe coincidir con `compatibilidad.json` y
  `skills/pm-estado-proyecto/scripts/esquema.py: VERSION_PAQUETE`; `validar_paquete.py` lo comprueba).
- `agents/` orquestador + pm-director + 4 subagentes de fase. Sin `tools` (heredan MCP), `disallowedTools: Agent`.
- `skills/<skill>/` SKILL.md (≤ 12.500 bytes y ≤ 200 líneas), `references/guia.md`, `templates/`, `scripts/`.
- `skills/pm-estado-proyecto/scripts/` núcleo: `esquema.py` (esquemas, valores, migración), `estado.py`,
  `registro.py`, `especificacion.py`, `sanidad.py`, `puertas.py` (verificación de puertas), `wbs.py`, `cpm.py`, `evm.py`, `exportar.py`, `nuevo_proyecto.py`.
- `skills/pm-bmad-puente/scripts/bmad.py` puente BMAD. `hooks/` guardian.py, inicio.py, idioma.py, py.sh, hooks.json.
- `scripts/validar_paquete.py`, `scripts/probar_paquete.py`, `scripts/validar_mermaid.py`, `scripts/pruebas/fixtures/`, `scripts/pruebas_vivo/`.
- `SPEC.md` convenciones canónicas (claves de artefactos, registros, niveles de decisión, presupuestos).

## Convenciones de código
- Python 3.9+, solo biblioteca estándar en el núcleo (pyyaml, python-docx, openpyxl opcionales con mensaje claro).
- Referencias a scripts: en SKILL.md y references `${CLAUDE_SKILL_DIR}/../pm-X/scripts/…`; en agentes y hooks
  `${CLAUDE_PLUGIN_ROOT}/skills/pm-X/scripts/…`. Ninguna variable se expande en archivos leídos con Read ni en Hermes.
- `estado.json` y registros CSV solo se escriben con `estado.py` / `registro.py` (el hook lo impone también en pruebas
  manuales). Nada escribe en `_bmad/`, `_bmad-output/` ni `.bmad-core/`.
- Descripciones de skills: formato "… Usar: … No: …→skill", ≤ 240 caracteres; listado total ≤ 7.500 caracteres.
- Mensajes de scripts bilingües con `E.t(idioma, es, en)` cuando el usuario los lee.

## Flujo de trabajo para cada cambio
1. Leer la sección relevante (`grep -n`), no archivos enteros.
2. Cambiar el código y, si cambia una conducta, agregar una prueba en `scripts/probar_paquete.py`.
3. `python3 scripts/validar_paquete.py` → OK; `python3 scripts/probar_paquete.py` → 0 FALLO; `claude plugin validate .`;
   si se tocó un diagrama: `python3 scripts/validar_mermaid.py --render` (y revisar legibilidad con `--png DIR`).
4. Si cambian descripciones, agentes, hooks o el texto de inicio: `python3 scripts/pruebas_vivo/suite.py enrutamiento
   --ids <afectados>` (consume tokens) y, antes de una versión, `suite.py todo`.
5. Actualizar `CHANGELOG.md`, la documentación afectada (`docs/INDICE.md` lista todo) y, si corresponde, la versión en
   los tres lugares.
6. Commit con mensaje descriptivo; una rama y PR por cambio grande.

## Probar como usuario
```bash
claude --plugin-dir . -p "/pm-method:pm-ayuda"                 # sin instalar
python3 scripts/pruebas_vivo/vivo.py --cwd /tmp/demo "¿qué sigue?"
```
Proyecto de prueba con BMAD real: copiar `scripts/pruebas/fixtures/bmad-v6.12-real` y correr
`skills/pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta gestion --nombre Demo` dentro de la copia.

## Pendientes conocidos
Ver la sección "Pendientes" de `docs/INDICE.md` y los ítems `[verificar]` de la documentación.
