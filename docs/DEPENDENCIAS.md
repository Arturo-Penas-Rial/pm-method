# Dependencias · pm-method 2.5.0

Lista completa de lo que pm-method necesita o puede usar, con la **URL de origen** de cada elemento, para qué lo usa el
paquete, si es obligatorio, la versión probada, la licencia y el comando de instalación. Cómo instalar y configurar
todo de punta a punta: [INSTALACION.md](INSTALACION.md). Decisiones y contratos de cada integración:
[INTEGRACIONES.md](INTEGRACIONES.md).

> Convenciones
> - **Nivel**: *obligatoria* (sin ella el paquete no funciona), *recomendada* (funciones habituales la necesitan; la
>   sanidad avisa si falta), *opcional* (solo para una integración o función puntual; siempre hay respaldo interno).
> - **Versión probada**: la registrada en `compatibilidad.json` o en `INTEGRACIONES.md` §3.1; si no hay registro, la del
>   entorno donde pasaron `validar_paquete.py` y `probar_paquete.py` el 2026-10-17 (se indica "entorno de pruebas").
> - **Licencia**: solo se informa si se comprobó en el archivo de licencia o en los metadatos del paquete; si no, "no
>   verificada".
> - **URL**: toda URL fue comprobada con el comando que figura en §7. Las que no se pudieron comprobar dicen
>   **"URL a confirmar por el usuario"** o llevan **[verificar]**.
> - El repositorio de cada tercero puede cambiar. Revisar cada skill o servidor antes de instalarlo: corre con los
>   permisos del agente.

---

## 0. Resumen: qué instalar según el uso

| Uso | Necesita |
|---|---|
| Núcleo (método, registros, sanidad, informes en Markdown/CSV) | un cliente (§1.1) + Python ≥ 3.9 |
| Instalar desde GitHub o actualizar | además `git` |
| Exportar Word/Excel, leer actas `.docx`, puente BMAD | además `pyyaml`, `python-docx`, `openpyxl` (§2) |
| BMAD como capa de especificación | además Node.js (≥ 20.12 para `bmad-method@6.12.4`) (§3, §4.1) |
| Skills externas de diagramas u Office instaladas con `npx skills` | además Node.js ≥ 22.20 (lo exige `skills@1.7.0`) (§3, §6) |
| Conectores MCP (Jira, Slack, reuniones, OKR…) | el servidor MCP correspondiente, configurado en el cliente (§5) |
| Enviar comunicaciones a interesados por correo SMTP, webhooks de Slack o Teams, o `.eml` (`envios.py`) | nada que instalar (biblioteca estándar de Python); solo las variables de entorno del modo elegido (§5, `INSTALACION.md` §0.7); `.eml` sin configuración |

**Node.js: versión mínima efectiva.** Cada componente declara un mínimo distinto en su `package.json` (`engines`,
consultado con `npm view`): archify ≥ 18, `@drawio/mcp` ≥ 18, `minutes-mcp` ≥ 20, `bmad-method@6.12.4` ≥ 20.12.0,
`@mermaid-js/mermaid-cli@12.0.0` ≥ 22.13.0, `skills@1.7.0` y `@1.7.2` ≥ 22.20.0. Para cubrir todo, **Node.js ≥ 22.20**.
El entorno de pruebas usó Node 22.22.0 y npm 10.9.4.

---

## 1. Entorno de ejecución obligatorio

### 1.1 Cliente (al menos uno)

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| Claude Code (CLI) | ejecuta las 39 skills, los 6 agentes y los 3 hooks (plugin) | obligatoria (uno de los tres clientes) | 2.1.302 (`compatibilidad.json`, `INTEGRACIONES.md` §3.1) | propietaria: "© Anthropic PBC. All rights reserved", sujeta a los términos comerciales de Anthropic (`LICENSE.md` del repositorio) | https://github.com/anthropics/claude-code · npm `@anthropic-ai/claude-code`: https://registry.npmjs.org/@anthropic-ai%2fclaude-code | según su README: macOS/Linux `curl -fsSL https://claude.ai/install.sh \| bash`; Homebrew `brew install --cask claude-code`; Windows (PowerShell) `irm https://claude.ai/install.ps1 \| iex` o `winget install Anthropic.ClaudeCode`; npm `npm install -g @anthropic-ai/claude-code` (opción avanzada; requiere Node.js 22 o posterior y no se usa con `sudo`); también repositorios apt, dnf y apk firmados (documentación oficial "Advanced setup", consultada el 2026-10-27) |
| Cowork | usa el formato de plugin (skills y agentes) | alternativa | no registrada | no verificada | URL a confirmar por el usuario | gestión de plugins de la aplicación **[verificar]** |
| Hermes Agent | usa las 39 skills como comandos `/skill`; los agentes como personas; sin hooks | alternativa | no registrada | MIT (`LICENSE` del repositorio) | https://github.com/NousResearch/hermes-agent | según su README: Linux/macOS `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash`; Windows (PowerShell) `iex (irm https://hermes-agent.nousresearch.com/install.ps1)` |

Documentación de instalación citada en esos README: Claude Code https://code.claude.com/docs/en/setup (consultada el
2026-10-27: instalador nativo recomendado para macOS, Linux y WSL; requisitos Ubuntu 20.04+, 4 GB de RAM); Hermes
`https://hermes-agent.nousresearch.com/docs/getting-started/installation`, no accesible desde el entorno de verificación
(el mismo texto está en `website/docs/getting-started/installation.md` del repositorio de Hermes, leído el 2026-10-27).
Instalación en Windows con WSL2, paso a paso: [INSTALACION-WSL2.md](INSTALACION-WSL2.md).

### 1.2 Herramientas de base

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| Python ≥ 3.9 | todos los scripts deterministas (`estado.py`, `registro.py`, `sanidad.py`, `bmad.py`, `cpm.py`, `exportar.py`…) y los hooks (`guardian.py`, `inicio.py`, invocados como `python3`) | obligatoria | ≥ 3.9 declarada (`compatibilidad.json`); entorno de pruebas 3.13.16 | no verificada | código fuente: https://github.com/python/cpython · descargas: `https://www.python.org/downloads/` **[verificar]** | instalador oficial del sistema operativo o gestor de paquetes; ver notas por sistema en `INSTALACION.md` §1 |
| git | instalar y actualizar desde GitHub (`claude plugin marketplace add <owner>/<repo>` clona el repositorio), clonar para Hermes; en Windows, Git for Windows aporta Git Bash, que Claude Code usa para ejecutar los hooks | obligatoria para instalar desde GitHub; en Windows, necesaria para los hooks | entorno de pruebas 2.43.0 | no verificada | https://github.com/git/git · Git for Windows: https://github.com/git-for-windows/git (sitio `https://gitforwindows.org/` **[verificar]**) | Linux: gestor de paquetes; macOS: **[verificar]**; Windows: instalador de Git for Windows |

---

## 2. Paquetes Python recomendados

Ninguno es obligatorio (`compatibilidad.json`: `dependencias.obligatorias` vacío). La sanidad informa la falta de cada
uno como **INS-01** con el comando de instalación.

| Nombre (PyPI) | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| `pyyaml` (módulo `yaml`) | `pm-bmad-puente` (`bmad.py`: configuración de BMAD y `sprint-status.yaml`); `scripts/probar_paquete.py` lo exige | recomendada (imprescindible con BMAD) | 6.0.3 (entorno de pruebas) | MIT (metadatos PyPI) | https://pypi.org/project/pyyaml/ · fuente https://github.com/yaml/pyyaml | `python3 -m pip install pyyaml` |
| `python-docx` (módulo `docx`) | `pm-exportar` (`exportar.py docx`), `pm-reuniones` (`transcripcion.py` lee actas `.docx`) | recomendada | 1.2.0 (entorno de pruebas) | MIT (metadatos PyPI) | https://pypi.org/project/python-docx/ · fuente https://github.com/python-openxml/python-docx | `python3 -m pip install python-docx` |
| `openpyxl` | `pm-exportar` (`exportar.py xlsx`) | recomendada | 3.1.5 (entorno de pruebas) | MIT (metadatos PyPI) | https://pypi.org/project/openpyxl/ (fuente declarada en PyPI: `https://foss.heptapod.net/openpyxl/openpyxl` **[verificar]**) | `python3 -m pip install openpyxl` |

Las tres juntas: `python3 -m pip install pyyaml python-docx openpyxl`.

---

## 3. Herramientas opcionales

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| Node.js y `npx` | `npx bmad-method install` (BMAD), `npx skills add` (skills externas); en ejecución, archify, visual-explainer y las skills de Office | opcional (obligatoria para BMAD y skills externas) | entorno de pruebas Node 22.22.0, npm 10.9.4; mínimo efectivo ≥ 22.20 (§0) | no verificada | código fuente: https://github.com/nodejs/node · descargas: `https://nodejs.org/en/download` **[verificar]** | instalador oficial o gestor de paquetes **[verificar]**; `npx` viene con npm |
| `skills` (CLI de `npx skills add`) | instalar archify, diagram-design, visual-explainer y docx/xlsx/pptx como skills copiadas (§6.1 de `INSTALACION.md`) | opcional | 1.7.0 (`INSTALACION.md` §6.1); última en npm al 2026-10-17: 1.7.2 | MIT (npm) | https://github.com/vercel-labs/skills · npm https://registry.npmjs.org/skills | sin instalación: `npx skills add <owner>/<repo> -a claude-code -s <skill> -y` (requiere Node ≥ 22.20.0) |
| Chrome o Chromium | `browser-check` de archify (`pm-visuales` con `diagramas=archify`) | opcional | no registrada | no verificada | URL a confirmar por el usuario | instalar el navegador; si archify no lo encuentra, `ARCHIFY_CHROME=<ruta del ejecutable>` |
| `@mermaid-js/mermaid-cli` (`mmdc`) | `exportar.py` inserta los diagramas Mermaid como imagen en Word (`pm-exportar`); `mapas.py … render` genera el PNG de los mapas de Wardley y de recorrido (`pm-mapas-estrategicos`; `wardley-beta` exige Mermaid 11.14 o posterior y está en beta); `scripts/validar_mermaid.py --render` (mantenimiento) | opcional | 11.16.0 con Mermaid 11.16.1 (entorno de pruebas); la 12.0.0 exige Node ≥ 22.13.0 | MIT (npm) | https://github.com/mermaid-js/mermaid-cli · npm https://registry.npmjs.org/@mermaid-js%2fmermaid-cli | `npm install -g @mermaid-js/mermaid-cli` |
| Java (JRE/JDK) | solo para usar MPXJ | opcional | entorno de pruebas OpenJDK 21.0.12.1 | no verificada | URL a confirmar por el usuario | distribución de Java del sistema operativo **[verificar]** |
| MPXJ (paquete PyPI `mpxj`) + JPype (`jpype1`) | validar o convertir el MSPDI de `cpm.py --mspdi` y `.mpp` (`pm-cronograma-estimacion`); `cpm.py` no lo necesita | opcional | `mpxj` 16.10.0 (`INTEGRACIONES.md` §2); `jpype1` 1.7.1 (entorno de pruebas) | `mpxj`: LGPL-2.0-or-later; `jpype1`: Apache-2.0 (metadatos PyPI) | https://pypi.org/project/mpxj/ · fuente https://github.com/joniles/mpxj · https://pypi.org/project/jpype1/ · fuente https://github.com/jpype-project/jpype | `python3 -m pip install mpxj jpype1` (el paquete `mpxj` no declara JPype como dependencia; su documentación lo usa con `import jpype`) |
| Playwright (PyPI `playwright`) | PNG opcional de diagram-design; capturas de tableros, reportes y recorridos en los recorridos E2E (`scripts/pruebas/guias_e2e/`, mantenimiento) | opcional | 1.56.0 (entorno de pruebas e imagen Docker) | no verificada | https://pypi.org/project/playwright/ · fuente https://github.com/microsoft/playwright | `python3 -m pip install playwright && playwright install chromium` (comando de `INSTALACION.md` §6.1) |
| `playwright-core` (npm) | `check.mjs` de visual-explainer (sin él no corre esa comprobación) | opcional | no registrada | Apache-2.0 (npm) | https://github.com/microsoft/playwright · npm https://registry.npmjs.org/playwright-core | **[verificar]** según la documentación de visual-explainer |
| `docx` y `pptxgenjs` (npm) | los usan las skills de Office de `anthropics/skills` para generar `.docx` y `.pptx`; `pptxgenjs` 4.0.1 lo usa también el generador del webinar (`scripts/webinar/pptx.js`) y del Informe 2 | opcional | no registrada | MIT ambos (npm) | https://github.com/dolanmiu/docx · https://github.com/gitbrent/PptxGenJS | `npm install docx pptxgenjs` en una carpeta de trabajo fuera del proyecto (`INSTALACION.md` §12) |
| matplotlib (PyPI) | gráficos de 1600 × 900 de las guías E2E (`scripts/pruebas/guias_e2e/visuales.py`, mantenimiento); sin él, `probar_paquete.py` omite una comprobación | opcional | 3.11.2 (entorno de pruebas e imagen Docker) | no verificada | https://pypi.org/project/matplotlib/ | `python3 -m pip install matplotlib` |
| Orca (stablyai/orca) | ver en una sola aplicación varias sesiones de Claude Code o Hermes (gestión y producto) en paralelo, con worktrees, terminales, tableros de GitHub/Linear y notificaciones; no la usan los scripts | opcional (sugerida) | no probada en este entorno **[verificar]** | MIT (README del repositorio) | https://github.com/stablyai/orca | Windows/macOS/Linux desde onorca.dev/download o *releases*; macOS `brew install --cask stablyai/orca/orca`; detalle en `INSTALACION.md` §0.8 |

---

## 4. Repositorios externos integrados

### 4.1 El paquete y la capa de especificación

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| pm-method | el propio paquete (plugin y marketplace `pm-method`) | — | 2.5.0 (este documento) | MIT (`LICENSE` del repositorio publicado) | https://github.com/Arturo-Penas-Rial/pm-method | `claude plugin marketplace add Arturo-Penas-Rial/pm-method` y `claude plugin install pm-method@pm-method` |
| BMAD Method | capa de especificación de solo lectura: `pm-bmad-puente` (`bmad.py`), `especificacion.py`, `pm-nuevo` (detección) | opcional | 4.x, 6.11 y 6.12; relevado `bmad-method@6.12.4` (`compatibilidad.json`) | MIT (npm) | https://github.com/bmad-code-org/BMAD-METHOD · npm https://registry.npmjs.org/bmad-method | en la raíz del repositorio del producto: `npx bmad-method@6.12.4 install --modules bmm --tools claude-code --yes --user-name <nombre> --set core.project_name=<proyecto> --no-shims` (requiere Node ≥ 20.12.0) |

### 4.2 Skills externas (diagramas y Office)

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación (de `compatibilidad.json` / `INSTALACION.md` §6.1) |
|---|---|---|---|---|---|---|
| archify | `pm-visuales` con `diagramas=archify` (HTML interactivo validado por su `finalize`) | opcional | 3.1 (según su `SKILL.md`), commit `88d1ae4` | MIT (`LICENSE` y `SKILL.md`) | https://github.com/tt-a1i/archify | `npx skills add tt-a1i/archify -a claude-code -s archify -y` · requiere Node ≥ 18 (su `package.json`) y Chrome/Chromium para `browser-check` |
| diagram-design | `pm-visuales` con `diagramas=diagram-design` (organigrama, PBS/WBS, flujos, mapa poder/interés y roadmap editoriales, sin red); caso DD de `probar_paquete.py` con `PM_DIAGRAM_DESIGN` (imagen Docker) | opcional | 2.6.133 (su `plugin.json`), commit `66fa2e7`: delegación en vivo (organigrama con fuentes del sistema, `self_check.py --offline` OK) el 2026-10-27; antes 2.6.110 (`550fd66`) | MIT (`LICENSE` y `plugin.json`; terceros en su `THIRD_PARTY_LICENSES.md`: Tabler MIT, Simple Icons CC0, Devicon MIT, OFL) | https://github.com/cathrynlavery/diagram-design | plugin: `claude plugin marketplace add cathrynlavery/diagram-design` y `claude plugin install diagram-design@diagram-design`; o copia: `npx skills add cathrynlavery/diagram-design -a claude-code -s diagram-design -y` |
| visual-explainer | `pm-visuales` con `diagramas=visual-explainer` (one-pagers, roadmap comentado) | opcional | 0.12.0 (su `marketplace.json` y `package.json`), commit `5a1b3c4` | MIT (`LICENSE` y `package.json`) | https://github.com/nicobailon/visual-explainer | copia: `npx skills add nicobailon/visual-explainer -a claude-code -s visual-explainer -y`; o plugin: `claude plugin marketplace add nicobailon/visual-explainer` y `claude plugin install visual-explainer@visual-explainer-marketplace` |
| anthropics/skills (`docx`, `xlsx`, `pptx`) | `pm-exportar` con `export=skills-office` | opcional | commit `dbd4588` | **propietaria**: cada skill trae su `LICENSE.txt` ("© 2025 Anthropic, PBC. All rights reserved"; uso regido por el acuerdo del usuario con Anthropic). El repositorio no tiene `LICENSE` en la raíz | https://github.com/anthropics/skills | copia: `npx skills add anthropics/skills -a claude-code -s docx xlsx pptx -y`; o plugin: `claude plugin marketplace add anthropics/skills` y `claude plugin install document-skills@anthropic-agent-skills` (el plugin `document-skills` incluye también `pdf`) |

### 4.3 draw.io

`compatibilidad.json` nombra "drawio-mcp" e `INTEGRACIONES.md` §2 lo describe como oficial. Hay **dos** proyectos con
nombres parecidos; el de draw.io (jgraph) es el que publica el paquete `@drawio/mcp`:

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| drawio-mcp (jgraph, draw.io) | `diagramas=drawio` vía MCP (`pm-visuales` / `pm-integraciones`) | opcional | no probada en vivo con pm-method; npm `@drawio/mcp` 1.7.0 y plugin `drawio` 1.2.3 instalables al 2026-10-17 | Apache-2.0 (`LICENSE` y npm) | https://github.com/jgraph/drawio-mcp · npm https://registry.npmjs.org/@drawio%2fmcp | según su documentación: `claude mcp add drawio -- npx -y @drawio/mcp`; o plugin: `claude plugin marketplace add jgraph/drawio-mcp` y `claude plugin install drawio@drawio` |
| `drawio-mcp` (npm, otro autor) | no es el anterior: paquete npm `drawio-mcp` de `Sujimoshi/drawio-mcp` (ISC) | no usar sin revisar | — | ISC (npm) | https://github.com/Sujimoshi/drawio-mcp | — |

### 4.4 Métodos y formatos de los mapas estratégicos (sin dependencia instalada)

`pm-mapas-estrategicos` no instala nada nuevo: usa Mermaid (si hay `mmdc`, para el PNG) y escribe texto. Los métodos se
citan por su autor y el contenido de la skill está redactado en palabras propias; no se copió texto ni código de
terceros.

| Fuente | Qué toma pm-method | Licencia o condición | URL |
|---|---|---|---|
| Mapas de Wardley (Simon Wardley) | el concepto y su vocabulario (ancla, cadena de valor, evolución, inercia) | el contenido del autor se publica bajo CC BY-SA 4.0 según su sitio [verificar versión]; se citan ideas, no texto | https://www.wardleymaps.com/faqs/is-wardley-mapping-free |
| Mermaid `wardley-beta` y `journey` | sintaxis de salida de `mapas.py render` | MIT (Mermaid); `wardley-beta` disponible desde 11.14 según la documentación y en beta | https://mermaid.js.org/syntax/wardley.html · https://mermaid.js.org/syntax/userJourney.html |
| Lenguaje de OnlineWardleyMaps (OWM) | formato del export `.owm` (`title`, `evolution`, `anchor`, `component … [v, e]`, `(build)`, `(buy)`, `(outsource)`, `(market)`, `inertia`, `evolve`, `note`), verificado contra su documentación el 2026-10-20 | MIT (repositorio de OWM); solo se escribe texto en ese formato | https://docs.onlinewardleymaps.com/docs/dsl-overview |

---

## 5. Conectores MCP opcionales

pm-method **no trae `.mcp.json` ni credenciales** y no predefine conectores: `pm-integraciones` resuelve capacidades
(`tracker`, `docs`, `chat`, `correo`, `reuniones`, `okr`, `diagramas`) con los servidores conectados en la sesión. El envío
a interesados tiene además una vía sin conector, la capa de canales (`envios.py`), que no agrega dependencias externas. Configuración
en `INSTALACION.md` §6.

| Conector | Capacidad en `estado.json` | Skill dueña | Versión probada | Licencia | URL de origen / servidor | Configuración en Claude Code |
|---|---|---|---|---|---|---|
| Atlassian Rovo MCP Server (Jira, Confluence) | `tracker=jira`, `docs=confluence` | `pm-integraciones` | no probada en vivo con pm-method | Apache-2.0 (repositorio `atlassian/atlassian-mcp-server`; el servicio alojado tiene sus propios términos) | repositorio https://github.com/atlassian/atlassian-mcp-server · servidor `https://mcp.atlassian.com/v2/mcp` (tomado del README de ese repositorio; el endpoint no responde desde el entorno de verificación) | según ese README: `claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp` y luego `/mcp` en una sesión para autenticar |
| Slack MCP (oficial) | `chat=slack` | `pm-integraciones`, `pm-comunicacion-stakeholders` | no probada | no verificada | URL a confirmar por el usuario (`INTEGRACIONES.md` §2 cita `https://mcp.slack.com/mcp`; no se pudo comprobar) | `claude mcp add --transport http <nombre> <url>` con la URL que indique Slack |
| Microsoft Teams / Work IQ | `chat=teams`, `reuniones=teams` | `pm-integraciones`, `pm-reuniones` | no probada | no verificada | URL a confirmar por el usuario | según la documentación de Microsoft **[verificar]** |
| Granola | `reuniones=granola` | `pm-reuniones` | no probada | no verificada | URL a confirmar por el usuario | **[verificar]** |
| Fireflies | `reuniones=fireflies` | `pm-reuniones` | no probada | no verificada | URL a confirmar por el usuario | **[verificar]** |
| Zoom | `reuniones=zoom` (obtención de transcripciones **no confirmada**) | `pm-reuniones` | no probada | no verificada | URL a confirmar por el usuario | **[verificar]** |
| minutes (`minutes-mcp`) | `reuniones=minutes` | `pm-reuniones` | no probada en vivo; npm `minutes-mcp` 0.30.2 al 2026-10-17 | MIT (`LICENSE` y npm) | https://github.com/silverstein/minutes · npm https://registry.npmjs.org/minutes-mcp | según su README: `claude mcp add minutes -- npx -y minutes-mcp` (requiere Node ≥ 20) |
| Tability (MCP oficial) | `okr=tability` | `pm-okr` (vía `pm-integraciones`; publicación con `tability_create_checkin`) | no probada en vivo con pm-method | no verificada (servicio comercial con sus propios términos) | servidor `https://mcp.tability.app/mcp` (nube de EE. UU., por defecto); UE `https://mcp-eu.tability.app/mcp`; AU `https://mcp-au.tability.app/mcp` · guía https://guides.tability.io/docs/become-a-tability-power-user/integrations/tability-mcp-server | `claude mcp add --transport http tability https://mcp.tability.app/mcp` y luego `/mcp` (OAuth en el navegador; requiere "API Access Enabled" para el usuario). La guía no muestra un comando de Claude Code: es la forma general de `claude mcp add` (`INSTALACION.md` §0.7) |
| Perdoo (MCP oficial) | `okr=perdoo` | `pm-okr` (vía `pm-integraciones`; publicación con `update_goal_progress`) | no probada en vivo con pm-method | no verificada (servicio comercial); plan requerido **[verificar]** | servidor `https://mcp.perdoo.com` · artículo https://support.perdoo.com/en/articles/14470891-mcp-server (15/09/2026) | `claude mcp add --transport http perdoo https://mcp.perdoo.com` y luego `/mcp` (OAuth; o clave de API en la cabecera `Authorization: Bearer …`). El artículo no muestra un comando de Claude Code (forma general, `INSTALACION.md` §0.7) |
| Correo vía conector de la organización (Gmail, Outlook) | `correo=gmail` / `correo=outlook` | `pm-integraciones` (`envios.py preparar-mcp` → herramienta MCP → `envios.py registrar --modo mcp`) | no probada | no verificada | URL a confirmar por el usuario **[verificar]** (depende del conector que habilite cada organización) | según el proveedor del conector **[verificar]** |
| Capa de canales propia: SMTP y webhooks de Slack/Teams (`envios.py`) | `correo=smtp`, `correo=eml`; webhooks para `chat=slack`/`teams` | `pm-integraciones` | `probar_paquete.py` caso H, contra servidores locales en 127.0.0.1 (no contra servicios reales) | la del paquete (MIT) | no es un servidor MCP ni una dependencia: usa `smtplib`, `email` y `urllib` de la biblioteca estándar. Webhook de Teams según https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook | variables de entorno `PM_SMTP_*`, `PM_SLACK_WEBHOOK_URL`, `PM_TEAMS_WEBHOOK_URL` (`INSTALACION.md` §0.7); `--modo eml` sin configuración |
| draw.io | `diagramas=drawio` | `pm-visuales` | ver §4.3 | ver §4.3 | ver §4.3 | ver §4.3 |

---

## 6. Dónde se declara cada dependencia en el paquete

| Archivo | Qué declara |
|---|---|
| `compatibilidad.json` | Python ≥ 3.9; recomendadas y opcionales; versiones de BMAD probadas; skills externas probadas en vivo (repositorio, commit, versión, comando); MCP opcionales (incluidos Tability y Perdoo); `canales_sin_conector` (modos de `envios.py` y sus variables de entorno) |
| `skills/pm-estado-proyecto/scripts/sanidad.py` | INS-01 (módulos Python), INS-03 (skills externas, Node, Chrome), INT-01 (valores de `integraciones`, lista en `esquema.py: VALORES_INTEGRACION`, incluidos `correo` y `okr=perdoo`) |
| `skills/pm-integraciones/scripts/envios.py` | capa de canales: solo biblioteca estándar (`smtplib`, `email`, `urllib`); variables de entorno en su docstring y en `ENV` |
| `INTEGRACIONES.md` §1–§3 | uso de cada dependencia y respaldo interno si falta |
| `docker/Dockerfile` | versiones fijadas del entorno Docker opcional; etapa `skills-externas`: diagram-design por commit (`DIAGRAM_DESIGN_COMMIT`) para el caso DD de `probar_paquete.py` ([DOCKER](DOCKER.md) §2) |

---

## 7. Verificación

Comprobaciones hechas el **2026-10-17** desde el entorno de desarrollo del paquete (Linux; la navegación web a GitHub y a
la mayoría de los sitios de documentación está bloqueada por el proxy, por eso los repositorios se comprobaron con
`git ls-remote`).

### 7.1 Repositorios GitHub (`git ls-remote https://github.com/<owner>/<repo>.git HEAD`)

| Repositorio | HEAD devuelto (abreviado) | Comprobación adicional |
|---|---|---|
| Arturo-Penas-Rial/pm-method | `39e5e3f` | clonado; `LICENSE` MIT; `claude plugin validate` correcto; `claude plugin marketplace add` + `install` + `marketplace update` + `update` correctos con un `HOME` aislado (versión publicada en ese momento: 2.0.0) |
| anthropics/claude-code | `c017428` | clonado; README (métodos de instalación) y `LICENSE.md`; `CHANGELOG.md` (notas de Windows) |
| NousResearch/hermes-agent | `26f1b27` | clonado; README (instalación), `LICENSE` MIT, referencia de CLI (`hermes skills tap add`, `hermes skills install`, `hermes mcp add`, `/reload-skills`, `skills.external_dirs`) |
| python/cpython | `e5ef47e` | — |
| git/git | `c514088` | — |
| git-for-windows/git | `5cf10d7` | — |
| nodejs/node | `269cab6` | — |
| yaml/pyyaml | `f5e4504` | — |
| python-openxml/python-docx | `e454546` | — |
| mermaid-js/mermaid-cli | `f416ac5` | — |
| joniles/mpxj | `71304af` | — |
| jpype-project/jpype | `3d70d42` | — |
| microsoft/playwright | `b335271` | — |
| vercel-labs/skills | `13e4063` | `npx -y skills@1.7.0 add --help` (opciones `-a`, `-s`, `-y`, `-g`, `--copy`) |
| bmad-code-org/BMAD-METHOD | `cfba3ff` | `npx -y bmad-method@6.12.4 install --help`, `--list-options core`, `--list-tools`; instalación real en un repositorio de prueba y `bmad.py detectar` → `version 6.12.4`, `soporte: soportada` |
| tt-a1i/archify | `88d1ae4` | clon local: `LICENSE` MIT, `SKILL.md` (versión 3.1), `package.json` (`engines.node >=18`); `npx skills add tt-a1i/archify -a claude-code -s archify -y` en un repositorio de prueba → sanidad INS-03 INFO "instalada" |
| cathrynlavery/diagram-design | `66fa2e7` (antes `550fd66`) | clon local: `LICENSE` MIT, `plugin.json` 2.6.133; `mermaid_extract.py` importa los respaldos `flowchart` y rechaza `quadrantChart`, `gantt` y `timeline` (código 2); `self_check.py --offline` rechaza Google Fonts; sesión en vivo con `--plugin-dir` (Claude Code 2.1.311): Skill `diagram-design:diagram-design`, organigrama sin red. Con `550fd66`: `claude plugin install diagram-design@diagram-design` correcto (`HOME` aislado) → INS-03 INFO |
| nicobailon/visual-explainer | `5a1b3c4` | clon local: `LICENSE` MIT, `marketplace.json` 0.12.0 (`visual-explainer-marketplace`); plugin instalado (`HOME` aislado) → INS-03 INFO |
| anthropics/skills | `dbd4588` | clon local: `skills/{docx,xlsx,pptx}/LICENSE.txt` propietarias; sin `LICENSE` en la raíz; marketplace `anthropic-agent-skills`, plugin `document-skills` (xlsx, docx, pptx, pdf) instalado (`HOME` aislado) → INS-03 INFO |
| jgraph/drawio-mcp | `a06f00a` | clonado: `LICENSE` Apache-2.0; README (`npx @drawio/mcp`, plugin `drawio@drawio`) y `mcp-tool-server/README.md` (`claude mcp add drawio -- npx -y @drawio/mcp`); plugin instalado (`HOME` aislado) |
| Sujimoshi/drawio-mcp | `76dd5c2` | identificado por `npm view drawio-mcp repository.url` |
| atlassian/atlassian-mcp-server | `b74220d` | clonado: `LICENSE` Apache-2.0; README (servidor `https://mcp.atlassian.com/v2/mcp`, comando para Claude Code) |
| silverstein/minutes | `a8270a9` | clonado: `LICENSE` MIT; README (`claude mcp add minutes -- npx -y minutes-mcp`) |

### 7.2 Paquetes npm (`npm view <paquete> version repository.url license engines`)

| Paquete | Versión | Licencia | `engines.node` | Registro (HTTP 200 con `curl`) |
|---|---|---|---|---|
| `bmad-method@6.12.4` | 6.12.4 | MIT | ≥ 20.12.0 | https://registry.npmjs.org/bmad-method |
| `skills@1.7.0` / última | 1.7.0 / 1.7.2 | MIT | ≥ 22.20.0 | https://registry.npmjs.org/skills |
| `@mermaid-js/mermaid-cli` | 12.0.0 (11.16.0 instalada en pruebas: `^18.19 \|\| >=20.0`) | MIT | ≥ 22.13.0 | https://registry.npmjs.org/@mermaid-js%2fmermaid-cli |
| `@drawio/mcp` | 1.7.0 | Apache-2.0 | ≥ 18.0.0 | https://registry.npmjs.org/@drawio%2fmcp |
| `minutes-mcp` | 0.30.2 | MIT | ≥ 20 | https://registry.npmjs.org/minutes-mcp |
| `@anthropic-ai/claude-code` | 2.1.302 | "SEE LICENSE IN README.md" | — | https://registry.npmjs.org/@anthropic-ai%2fclaude-code |
| `docx` · `pptxgenjs` · `playwright-core` | 9.12.0 · 4.0.1 · 1.64.1 | MIT · MIT · Apache-2.0 | — | — |
| `drawio-mcp` | 1.6.0 | ISC | — | — |

### 7.3 Paquetes PyPI (`pip index versions <paquete>`, `pip download --no-deps` y lectura de `METADATA`)

| Paquete | Última versión | Licencia (`METADATA`) | Página (HTTP 200 con `curl`) |
|---|---|---|---|
| `pyyaml` | 6.0.3 | MIT | https://pypi.org/project/pyyaml/ |
| `python-docx` | 1.2.0 | MIT | https://pypi.org/project/python-docx/ |
| `openpyxl` | 3.1.5 | MIT | https://pypi.org/project/openpyxl/ |
| `mpxj` | 16.10.0 | LGPL-2.0-or-later | https://pypi.org/project/mpxj/ |
| `jpype1` | 1.7.1 | Apache-2.0 | https://pypi.org/project/jpype1/ (`JPype1` redirige aquí) |
| `playwright` | 1.64.0 | no leída | https://pypi.org/project/playwright/ |

### 7.4 No verificadas

- Sitios de documentación y descarga (python.org, nodejs.org, gitforwindows.org, code.claude.com,
  hermes-agent.nousresearch.com): el proxy del entorno no los alcanza (`curl` → 000). Se citan como figuran en los
  README de origen y con **[verificar]**.
- Servidores MCP de Slack, Teams/Work IQ, Granola, Fireflies y Zoom, y conectores de correo (Gmail, Outlook) de la
  organización: sin fuente comprobable desde este entorno; la búsqueda en el registro de conectores no devolvió URLs.
  Figuran como "URL a confirmar por el usuario". Tability está verificado en §7.5.
- Tability y Perdoo: si exigen un plan comercial concreto para usar el MCP (sus páginas no lo dicen). Webhooks de Slack
  y Teams: los pasos de interfaz para crearlos y el envío contra un servicio real (solo se probó contra servidores
  locales).
- Cowork: sin URL ni procedimiento comprobado.
- Licencias de Python, git, Node.js, Chrome/Chromium y Java: no leídas.

### 7.5 Documentación de servicios consultada el 2026-10-17

Leída con la herramienta de lectura web del entorno de desarrollo; los servidores MCP no se conectaron en vivo con
pm-method.

| Fuente | URL | Qué se tomó |
|---|---|---|
| Guía del servidor MCP de Tability | https://guides.tability.io/docs/become-a-tability-power-user/integrations/tability-mcp-server | servidores `https://mcp.tability.app/mcp` (EE. UU., defecto), `https://mcp-eu.tability.app/mcp` (UE), `https://mcp-au.tability.app/mcp` (AU); OAuth en el navegador; requisito "API Access Enabled" por usuario; herramienta de verificación `tability_whoami`; no menciona plan ni comando de Claude Code |
| Artículo de soporte del servidor MCP de Perdoo (15/09/2026) | https://support.perdoo.com/en/articles/14470891-mcp-server | servidor `https://mcp.perdoo.com`; OAuth o clave de API (cabecera `Authorization: Bearer …`); herramienta `update_goal_progress`; no menciona plan ni comando de Claude Code |
| Microsoft Learn, "Create an Incoming Webhook" | https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook | flujo de Workflows (plantilla "Send webhook alerts to a channel" o disparador "When a Teams webhook request is received"); límite de 28 KB; tarjeta adaptable en `attachments`; conectores de Microsoft 365 "nearing deprecation" |
| Retiro de Viva Goals | https://learn.microsoft.com/viva/goals/goals-retirement | retirado el 31/12/2025 (no se ofrece como conector OKR) |
| Google re:Work, OKR | https://rework.withgoogle.com/en/guides/set-goals-with-okrs | escala 0,0–1,0 y "punto óptimo" en 60–70 %, base del umbral 0,7 aspiracional de `okr.py`; el semáforo comprometido 1,0/0,7 es convención de la práctica OKR, no figura en esa página |

Atlassian Goals y Asana Goals no estaban expuestos por sus MCP oficiales al 2026-10-17 **[verificar]**.
