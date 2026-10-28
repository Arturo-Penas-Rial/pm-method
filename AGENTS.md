# AGENTS.md · guía para agentes de código que trabajan en este repositorio

Este archivo sigue la convención AGENTS.md para agentes distintos de Claude Code. El contexto completo está en
[CLAUDE.md](CLAUDE.md); lo esencial:

- **Qué es:** el plugin pm-method 2.5.0 (6 agentes, 39 skills, 3 hooks). PRINCE2 7 manda; PMBOK 8 solo técnicas; BMAD es
  especificación de solo lectura.
- **Verificar siempre después de cambiar algo:**
  ```bash
  python3 scripts/validar_paquete.py      # estructura, tamaños, descripciones, versiones → OK
  python3 scripts/probar_paquete.py       # regresión → 355 OK · 0 FALLO (354 con Python 3.9; requiere pyyaml)
  python3 scripts/pruebas/integracion/correr.py   # integración cruzada → 99 OK · 0 FALLO en 34 eslabones
  python3 scripts/pruebas/guias_e2e/correr.py --salida /tmp/guias   # recorridos E2E → 5/5 OK
  python3 scripts/validar_mermaid.py --render   # si se tocó un diagrama → 128 bloques, 0 errores
  ```
- **No hacer:** editar `estado.json` o registros CSV de proyectos a mano (incluidos los opcionales `estereotipos`,
  `preferencias`, `raci`, `envios` y `personas`); escribir en carpetas de BMAD; inventar comandos, URLs o cifras; agregar marcas de
  empresas; incluir credenciales (la capa de canales `envios.py` las lee solo de variables de entorno).
- **Estilo:** documentación en español; mensajes de scripts bilingües; Python 3.9+ con biblioteca estándar en el
  núcleo.
- **Scripts principales:** núcleo en `skills/pm-estado-proyecto/scripts/` (`esquema.py`, `estado.py`, `registro.py`,
  `especificacion.py`, `sanidad.py`, `puertas.py`…); `pm-bmad-puente/scripts/bmad.py`; `pm-interesados/scripts/interesados.py`
  (maestro de interesados); `pm-integraciones/scripts/envios.py` (capa de canales); `pm-okr/scripts/okr.py`; `pm-caso-de-negocio/scripts/inversion.py`;
  `pm-mapas-estrategicos/scripts/mapas.py`; `pm-riesgos/scripts/riesgos.py`; `pm-reuniones/scripts/extraccion.py`;
  `pm-issues-cambios/scripts/impacto.py`; `pm-agil-hibrido/scripts/release.py`;
  `pm-lecciones-aprendidas/scripts/lecciones.py`; `pm-exportar/scripts/paquete.py`. Mapa completo en [CLAUDE.md](CLAUDE.md).
- **Instalación:** dos caminos separados, cada uno con su guía paso a paso: sobre WSL2 o Linux
  ([docs/INSTALACION-WSL2.md](docs/INSTALACION-WSL2.md)) o con Docker
  ([docs/INSTALACION-DOCKER.md](docs/INSTALACION-DOCKER.md)); guía general en [docs/INSTALACION.md](docs/INSTALACION.md).
- **Versionado:** la versión vive en `.claude-plugin/plugin.json`, `compatibilidad.json` y `esquema.py`
  (`VERSION_PAQUETE`); cambios en `CHANGELOG.md`.

## Uso de pm-method desde Hermes Agent
Instalar con `python3 scripts/instalar_hermes.py` (copia adaptada en `~/.hermes/skills/pm-method/`, rutas con
`${HERMES_SKILL_DIR}`); las skills se invocan como `/<skill>` y los agentes de `agents/` funcionan como personas. Hermes no ejecuta los hooks de Claude Code: la sanidad se hace con
`pm-sanidad` y en `pm-puerta`. Detalle: [docs/INSTALACION.md §3](docs/INSTALACION.md).
