# AGENTS.md · guía para agentes de código que trabajan en este repositorio

Este archivo sigue la convención AGENTS.md para agentes distintos de Claude Code. El contexto completo está en
[CLAUDE.md](CLAUDE.md); lo esencial:

- **Qué es:** el plugin pm-method 2.3.0 (6 agentes, 39 skills, 3 hooks). PRINCE2 7 manda; PMBOK 8 solo técnicas; BMAD es
  especificación de solo lectura.
- **Verificar siempre después de cambiar algo:**
  ```bash
  python3 scripts/validar_paquete.py      # estructura, tamaños, descripciones, versiones → OK
  python3 scripts/probar_paquete.py       # regresión → 223 OK · 0 FALLO (requiere pyyaml)
  python3 scripts/pruebas/integracion/correr.py   # integración cruzada → 61 OK · 0 FALLO
  python3 scripts/pruebas/guias_e2e/correr.py --salida /tmp/guias   # recorridos E2E → 5/5 OK
  python3 scripts/validar_mermaid.py --render   # si se tocó un diagrama → 0 errores
  ```
- **No hacer:** editar `estado.json` o registros CSV de proyectos a mano (incluidos los opcionales `estereotipos`,
  `preferencias`, `raci` y `envios`); escribir en carpetas de BMAD; inventar comandos, URLs o cifras; agregar marcas de
  empresas; incluir credenciales (la capa de canales `envios.py` las lee solo de variables de entorno).
- **Estilo:** documentación en español; mensajes de scripts bilingües; Python 3.9+ con biblioteca estándar en el
  núcleo.
- **Scripts principales:** núcleo en `skills/pm-estado-proyecto/scripts/` (`esquema.py`, `estado.py`, `registro.py`,
  `especificacion.py`, `sanidad.py`, `puertas.py`…); `pm-bmad-puente/scripts/bmad.py`; `pm-interesados/scripts/interesados.py`
  (maestro de interesados); `pm-integraciones/scripts/envios.py` (capa de canales); `pm-okr/scripts/okr.py`; `pm-caso-de-negocio/scripts/inversion.py`;
  `pm-mapas-estrategicos/scripts/mapas.py`. Mapa
  completo en [CLAUDE.md](CLAUDE.md).
- **Versionado:** la versión vive en `.claude-plugin/plugin.json`, `compatibilidad.json` y `esquema.py`
  (`VERSION_PAQUETE`); cambios en `CHANGELOG.md`.

## Uso de pm-method desde Hermes Agent
Instalar con `python3 scripts/instalar_hermes.py` (copia adaptada en `~/.hermes/skills/pm-method/`, rutas con
`${HERMES_SKILL_DIR}`); las skills se invocan como `/<skill>` y los agentes de `agents/` funcionan como personas. Hermes no ejecuta los hooks de Claude Code: la sanidad se hace con
`pm-sanidad` y en `pm-puerta`. Detalle: [docs/INSTALACION.md §3](docs/INSTALACION.md).
