# AGENTS.md · guía para agentes de código que trabajan en este repositorio

Este archivo sigue la convención AGENTS.md para agentes distintos de Claude Code. El contexto completo está en
[CLAUDE.md](CLAUDE.md); lo esencial:

- **Qué es:** el plugin pm-method (6 agentes, 37 skills, 3 hooks). PRINCE2 7 manda; PMBOK 8 solo técnicas; BMAD es
  especificación de solo lectura.
- **Verificar siempre después de cambiar algo:**
  ```bash
  python3 scripts/validar_paquete.py      # estructura, tamaños, descripciones, versiones → OK
  python3 scripts/probar_paquete.py       # regresión → 0 FALLO (requiere pyyaml)
  ```
- **No hacer:** editar `estado.json` o registros CSV de proyectos a mano; escribir en carpetas de BMAD; inventar
  comandos, URLs o cifras; agregar marcas de empresas; incluir credenciales.
- **Estilo:** documentación en español; mensajes de scripts bilingües; Python 3.9+ con biblioteca estándar en el
  núcleo.
- **Versionado:** la versión vive en `.claude-plugin/plugin.json`, `compatibilidad.json` y `esquema.py`
  (`VERSION_PAQUETE`); cambios en `CHANGELOG.md`.

## Uso de pm-method desde Hermes Agent
Instalar con `python3 scripts/instalar_hermes.py` (copia adaptada en `~/.hermes/skills/pm-method/`, rutas con
`${HERMES_SKILL_DIR}`); las skills se invocan como `/<skill>` y los agentes de `agents/` funcionan como personas. Hermes no ejecuta los hooks de Claude Code: la sanidad se hace con
`pm-sanidad` y en `pm-puerta`. Detalle: [docs/INSTALACION.md §3](docs/INSTALACION.md).
