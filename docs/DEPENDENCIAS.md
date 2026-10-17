# Dependencias · pm-method 2.1.0

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
| Conectores MCP (Jira, Slack, reuniones…) | el servidor MCP correspondiente, configurado en el cliente (§5) |

**Node.js: versión mínima efectiva.** Cada componente declara un mínimo distinto en su `package.json` (`engines`,
consultado con `npm view`): archify ≥ 18, `@drawio/mcp` ≥ 18, `minutes-mcp` ≥ 20, `bmad-method@6.12.4` ≥ 20.12.0,
`@mermaid-js/mermaid-cli@12.0.0` ≥ 22.13.0, `skills@1.7.0` y `@1.7.2` ≥ 22.20.0. Para cubrir todo, **Node.js ≥ 22.20**.
El entorno de pruebas usó Node 22.22.0 y npm 10.9.4.

---

## 1. Entorno de ejecución obligatorio

### 1.1 Cliente (al menos uno)

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| Claude Code (CLI) | ejecuta las 37 skills, los 6 agentes y los 3 hooks (plugin) | obligatoria (uno de los tres clientes) | 2.1.302 (`compatibilidad.json`, `INTEGRACIONES.md` §3.1) | propietaria: "© Anthropic PBC. All rights reserved", sujeta a los términos comerciales de Anthropic (`LICENSE.md` del repositorio) | https://github.com/anthropics/claude-code · npm `@anthropic-ai/claude-code`: https://registry.npmjs.org/@anthropic-ai%2fclaude-code | según su README: macOS/Linux `curl -fsSL https://claude.ai/install.sh \| bash`; Homebrew `brew install --cask claude-code`; Windows (PowerShell) `irm https://claude.ai/install.ps1 \| iex` o `winget install Anthropic.ClaudeCode`; npm (marcado como obsoleto) `npm install -g @anthropic-ai/claude-code` |
| Cowork | usa el formato de plugin (skills y agentes) | alternativa | no registrada | no verificada | URL a confirmar por el usuario | gestión de plugins de la aplicación **[verificar]** |
| Hermes Agent | usa las 37 skills como comandos `/skill`; los agentes como personas; sin hooks | alternativa | no registrada | MIT (`LICENSE` del repositorio) | https://github.com/NousResearch/hermes-agent | según su README: Linux/macOS `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash`; Windows (PowerShell) `iex (irm https://hermes-agent.nousresearch.com/install.ps1)` |

Documentación de instalación citada en esos README, no accesible desde el entorno de verificación **[verificar]**:
Claude Code `https://code.claude.com/docs/en/setup`; Hermes
`https://hermes-agent.nousresearch.com/docs/getting-started/installation`.

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
| `@mermaid-js/mermaid-cli` (`mmdc`) | `exportar.py` inserta los diagramas Mermaid como imagen en Word (`pm-exportar`); `scripts/validar_mermaid.py --render` (mantenimiento) | opcional | 11.16.0 (entorno de pruebas); la 12.0.0 exige Node ≥ 22.13.0 | MIT (npm) | https://github.com/mermaid-js/mermaid-cli · npm https://registry.npmjs.org/@mermaid-js%2fmermaid-cli | `npm install -g @mermaid-js/mermaid-cli` |
| Java (JRE/JDK) | solo para usar MPXJ | opcional | entorno de pruebas OpenJDK 21.0.12.1 | no verificada | URL a confirmar por el usuario | distribución de Java del sistema operativo **[verificar]** |
| MPXJ (paquete PyPI `mpxj`) + JPype (`jpype1`) | validar o convertir el MSPDI de `cpm.py --mspdi` y `.mpp` (`pm-cronograma-estimacion`); `cpm.py` no lo necesita | opcional | `mpxj` 16.10.0 (`INTEGRACIONES.md` §2); `jpype1` 1.7.1 (entorno de pruebas) | `mpxj`: LGPL-2.0-or-later; `jpype1`: Apache-2.0 (metadatos PyPI) | https://pypi.org/project/mpxj/ · fuente https://github.com/joniles/mpxj · https://pypi.org/project/jpype1/ · fuente https://github.com/jpype-project/jpype | `python3 -m pip install mpxj jpype1` (el paquete `mpxj` no declara JPype como dependencia; su documentación lo usa con `import jpype`) |
| Playwright (PyPI `playwright`) | PNG opcional de diagram-design | opcional | no registrada | no verificada | https://pypi.org/project/playwright/ · fuente https://github.com/microsoft/playwright | `python3 -m pip install playwright && playwright install chromium` (comando de `INSTALACION.md` §6.1) |
| `playwright-core` (npm) | `check.mjs` de visual-explainer (sin él no corre esa comprobación) | opcional | no registrada | Apache-2.0 (npm) | https://github.com/microsoft/playwright · npm https://registry.npmjs.org/playwright-core | **[verificar]** según la documentación de visual-explainer |
| `docx` y `pptxgenjs` (npm) | los usan las skills de Office de `anthropics/skills` para generar `.docx` y `.pptx` | opcional | no registrada | MIT ambos (npm) | https://github.com/dolanmiu/docx · https://github.com/gitbrent/PptxGenJS | `npm install docx pptxgenjs` en una carpeta de trabajo fuera del proyecto (`INSTALACION.md` §12) |
| Orca (stablyai/orca) | ver en una sola aplicación varias sesiones de Claude Code o Hermes (gestión y producto) en paralelo, con worktrees, terminales, tableros de GitHub/Linear y notificaciones; no la usan los scripts | opcional (sugerida) | no probada en este entorno **[verificar]** | MIT (README del repositorio) | https://github.com/stablyai/orca | Windows/macOS/Linux desde onorca.dev/download o *releases*; macOS `brew install --cask stablyai/orca/orca`; detalle en `INSTALACION.md` §0.8 |

---

## 4. Repositorios externos integrados

### 4.1 El paquete y la capa de especificación

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| pm-method | el propio paquete (plugin y marketplace `pm-method`) | — | 2.1.0 (este documento) | MIT (`LICENSE` del repositorio publicado) | https://github.com/Arturo-Penas-Rial/pm-method | `claude plugin marketplace add Arturo-Penas-Rial/pm-method` y `claude plugin install pm-method@pm-method` |
| BMAD Method | capa de especificación de solo lectura: `pm-bmad-puente` (`bmad.py`), `especificacion.py`, `pm-nuevo` (detección) | opcional | 4.x, 6.11 y 6.12; relevado `bmad-method@6.12.4` (`compatibilidad.json`) | MIT (npm) | https://github.com/bmad-code-org/BMAD-METHOD · npm https://registry.npmjs.org/bmad-method | en la raíz del repositorio del producto: `npx bmad-method@6.12.4 install --modules bmm --tools claude-code --yes --user-name <nombre> --set core.project_name=<proyecto> --no-shims` (requiere Node ≥ 20.12.0) |

### 4.2 Skills externas (diagramas y Office)

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación (de `compatibilidad.json` / `INSTALACION.md` §6.1) |
|---|---|---|---|---|---|---|
| archify | `pm-visuales` con `diagramas=archify` (HTML interactivo validado por su `finalize`) | opcional | 3.1 (según su `SKILL.md`), commit `88d1ae4` | MIT (`LICENSE` y `SKILL.md`) | https://github.com/tt-a1i/archify | `npx skills add tt-a1i/archify -a claude-code -s archify -y` · requiere Node ≥ 18 (su `package.json`) y Chrome/Chromium para `browser-check` |
| diagram-design | `pm-visuales` con `diagramas=diagram-design` | opcional | 2.6.110 (su `plugin.json`), commit `550fd66` | MIT (`LICENSE` y `plugin.json`) | https://github.com/cathrynlavery/diagram-design | plugin: `claude plugin marketplace add cathrynlavery/diagram-design` y `claude plugin install diagram-design@diagram-design`; o copia: `npx skills add cathrynlavery/diagram-design -a claude-code -s diagram-design -y` |
| visual-explainer | `pm-visuales` con `diagramas=visual-explainer` (one-pagers, roadmap comentado) | opcional | 0.12.0 (su `marketplace.json` y `package.json`), commit `5a1b3c4` | MIT (`LICENSE` y `package.json`) | https://github.com/nicobailon/visual-explainer | copia: `npx skills add nicobailon/visual-explainer -a claude-code -s visual-explainer -y`; o plugin: `claude plugin marketplace add nicobailon/visual-explainer` y `claude plugin install visual-explainer@visual-explainer-marketplace` |
| anthropics/skills (`docx`, `xlsx`, `pptx`) | `pm-exportar` con `export=skills-office` | opcional | commit `dbd4588` | **propietaria**: cada skill trae su `LICENSE.txt` ("© 2025 Anthropic, PBC. All rights reserved"; uso regido por el acuerdo del usuario con Anthropic). El repositorio no tiene `LICENSE` en la raíz | https://github.com/anthropics/skills | copia: `npx skills add anthropics/skills -a claude-code -s docx xlsx pptx -y`; o plugin: `claude plugin marketplace add anthropics/skills` y `claude plugin install document-skills@anthropic-agent-skills` (el plugin `document-skills` incluye también `pdf`) |

### 4.3 draw.io

`compatibilidad.json` nombra "drawio-mcp" e `INTEGRACIONES.md` §2 lo describe como oficial. Hay **dos** proyectos con
nombres parecidos; el de draw.io (jgraph) es el que publica el paquete `@drawio/mcp`:

| Nombre | Para qué lo usa pm-method | Nivel | Versión probada | Licencia | URL de origen | Instalación |
|---|---|---|---|---|---|---|
| drawio-mcp (jgraph, draw.io) | `diagramas=drawio` vía MCP (`pm-visuales` / `pm-integraciones`) | opcional | no probada en vivo con pm-method; npm `@drawio/mcp` 1.7.0 y plugin `drawio` 1.2.3 instalables al 2026-10-17 | Apache-2.0 (`LICENSE` y npm) | https://github.com/jgraph/drawio-mcp · npm https://registry.npmjs.org/@drawio%2fmcp | según su documentación: `claude mcp add drawio -- npx -y @drawio/mcp`; o plugin: `claude plugin marketplace add jgraph/drawio-mcp` y `claude plugin install drawio@drawio` |
| `drawio-mcp` (npm, otro autor) | no es el anterior: paquete npm `drawio-mcp` de `Sujimoshi/drawio-mcp` (ISC) | no usar sin revisar | — | ISC (npm) | https://github.com/Sujimoshi/drawio-mcp | — |

---

## 5. Conectores MCP opcionales

pm-method **no trae `.mcp.json` ni credenciales** y no predefine conectores: `pm-integraciones` resuelve capacidades
(`tracker`, `docs`, `chat`, `reuniones`, `okr`, `diagramas`) con los servidores conectados en la sesión. Configuración
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
| Tability | `okr=tability` | `pm-okr` (vía `pm-integraciones`) | no probada | no verificada | URL a confirmar por el usuario | **[verificar]** |
| draw.io | `diagramas=drawio` | `pm-visuales` | ver §4.3 | ver §4.3 | ver §4.3 | ver §4.3 |

---

## 6. Dónde se declara cada dependencia en el paquete

| Archivo | Qué declara |
|---|---|
| `compatibilidad.json` | Python ≥ 3.9; recomendadas y opcionales; versiones de BMAD probadas; skills externas probadas en vivo (repositorio, commit, versión, comando); MCP opcionales |
| `skills/pm-estado-proyecto/scripts/sanidad.py` | INS-01 (módulos Python), INS-03 (skills externas, Node, Chrome), INT-01 (valores de `integraciones`) |
| `INTEGRACIONES.md` §1–§3 | uso de cada dependencia y respaldo interno si falta |

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
| cathrynlavery/diagram-design | `550fd66` | clon local: `LICENSE` MIT, `plugin.json` 2.6.110; `claude plugin install diagram-design@diagram-design` correcto (`HOME` aislado) → INS-03 INFO |
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
- Servidores MCP de Slack, Teams/Work IQ, Granola, Fireflies, Zoom y Tability: sin fuente comprobable desde este
  entorno; la búsqueda en el registro de conectores no devolvió URLs. Figuran como "URL a confirmar por el usuario".
- Cowork: sin URL ni procedimiento comprobado.
- Licencias de Python, git, Node.js, Chrome/Chromium y Java: no leídas.
