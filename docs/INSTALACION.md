# Instalación y configuración · pm-method 2.2.0

Guía para instalar, configurar, verificar, actualizar y desinstalar el paquete de agentes y skills **pm-method** en
Claude Code, Cowork y Hermes Agent, y para instalar y conectar de punta a punta sus dependencias: Python y sus paquetes,
BMAD, las skills externas de diagramas y Office, y los conectores MCP de la organización.

> Convenciones de este documento
> - `/ruta/a/pm-method` es la carpeta del paquete (la que contiene `SPEC.md` y `.claude-plugin/`): un clon del
>   repositorio o la copia que instala Claude Code (ver §7.1).
> - `<pm-estado-proyecto>` es la carpeta instalada de esa skill (ver §7.1).
> - `./gestion` es la carpeta del proyecto de gestión (la que contiene `estado.json`).
> - **[verificar]** marca un dato que no se probó en este entorno o que depende de la versión vigente del cliente.
> - Comandos comprobados el 2026-10-17 con Claude Code 2.1.302 (`--help` de cada subcomando y ejecución real con un
>   `HOME` aislado). La lista completa de dependencias, con la URL de origen de cada una, está en
>   **[DEPENDENCIAS.md](DEPENDENCIAS.md)**.

---

## Recorrido de punta a punta

| Paso | Qué | Sección |
|---|---|---|
| 1 | Revisar los requisitos previos según el sistema operativo | §1 |
| 2 | Instalar el plugin desde GitHub (o desde una carpeta local) | §0 (o §2) |
| 2b | Configurar la credencial del cliente (suscripción o clave de API) y, si se usan, los tokens MCP y las variables de la capa de canales (correo, Slack, Teams) | §0.7 |
| 3 | Instalar los paquetes Python recomendados | §5 |
| 4 | Crear la carpeta del proyecto de gestión | §7.2 |
| 5 | Si el producto usa BMAD: instalarlo en su repositorio y detectarlo desde pm-method | §4 |
| 6 | Si se quieren diagramas u Office externos: instalar las skills y declararlas | §6.1 |
| 7 | Si hay herramientas de la organización: conectar los MCP y declararlos | §6 |
| 8 | Verificar la instalación completa | §8 |
| 9 | (Opcional) Instalar Orca para ver varias sesiones y proyectos en paralelo | §0.8 |

---

## 0. Instalación desde GitHub (recomendada)

El paquete está publicado en **https://github.com/Arturo-Penas-Rial/pm-method** (licencia MIT, repositorio público).
La raíz del repositorio es a la vez el plugin (`.claude-plugin/plugin.json`) y su marketplace
(`.claude-plugin/marketplace.json`, nombre `pm-method`). Cada integrante del equipo lo instala desde allí y recibe las
actualizaciones con dos comandos.

### 0.1 Credenciales de GitHub

- **Nunca compartir en el chat** (con Claude ni con ningún asistente) la contraseña de GitHub, tokens de acceso
  personal, códigos de recuperación ni códigos de 2FA. Ninguno de los comandos de esta guía los necesita escritos en
  la línea de comandos ni en archivos del proyecto.
- Se recomienda tener activada la **verificación en dos pasos (2FA)** en la cuenta de GitHub.
- Instalar desde el repositorio público no requiere credenciales. Solo se necesitan para publicar cambios (§0.2):
  `gh auth login` inicia sesión en el navegador; sin la CLI `gh`, GitHub pide un token de acceso personal en lugar de
  la contraseña de la cuenta, que se ingresa solo en el aviso de `git`, nunca en un mensaje al asistente.

### 0.2 Publicar el repositorio (lo hace el responsable del paquete)
```bash
# en la carpeta del paquete
git init && git add . && git commit -m "pm-method 2.2.0"
gh auth login                       # inicia sesión en el navegador
gh repo create <usuario>/pm-method --public --source . --push
```
Sin la CLI `gh`: crear el repositorio vacío en github.com y hacer `git remote add origin https://github.com/<usuario>/pm-method.git`
y `git push -u origin main`. Para un repositorio privado (`--private`), cada integrante necesita acceso de lectura.
Antes de anunciar una versión, comprobar que `version` de `.claude-plugin/plugin.json` coincide con la publicada: es la
que muestra `claude plugin list` y la que usa `claude plugin update` para decidir si hay algo nuevo.

### 0.3 Claude Code (cada integrante)
```bash
claude plugin marketplace add Arturo-Penas-Rial/pm-method   # acepta owner/repo de GitHub; necesita git
claude plugin install pm-method@pm-method                   # alcance por defecto: user
claude plugin list                                          # pm-method@pm-method · Version: 2.2.0 · Status: enabled
```
- Dentro de una sesión: `/plugin marketplace add Arturo-Penas-Rial/pm-method` y `/plugin install pm-method@pm-method`.
- Alcances: `claude plugin marketplace add … --scope user|project|local` (por defecto `user`) y
  `claude plugin install … --scope user|project|local` (por defecto `user`). Con `--scope project` el marketplace queda
  declarado en `.claude/settings.json` del repositorio y lo comparten quienes confíen en la carpeta.
- Para todo un equipo con plan Team/Enterprise, el administrador puede declarar el marketplace y habilitar el plugin en
  la configuración gestionada (`extraKnownMarketplaces` + `enabledPlugins`) **[verificar en la documentación vigente de
  configuración gestionada]**.
- Instalar sin agregar antes el marketplace: `claude plugin install pm-method --marketplace Arturo-Penas-Rial/pm-method`
  (opción `--marketplace <source>` de `claude plugin install --help`).

### 0.4 Actualizar
```bash
claude plugin marketplace update pm-method        # refresca el catálogo desde GitHub
claude plugin update pm-method@pm-method          # instala la versión nueva; requiere reiniciar Claude Code
claude plugin list                                # confirmar la versión
```
Si `update` responde que ya está en la última versión, el repositorio publicado todavía no tiene una `version` mayor en
`plugin.json`. `claude plugin marketplace update` sin nombre actualiza todos los marketplaces. Después de actualizar:
§10 (migración de proyectos) y §8 (verificación).

### 0.5 Hermes Agent
```bash
git clone https://github.com/Arturo-Penas-Rial/pm-method.git ~/pm-method
python3 ~/pm-method/scripts/instalar_hermes.py        # → ~/.hermes/skills/pm-method/ (38 skills adaptadas)
hermes skills list | grep -c "pm-"                    # → 38
```
Dentro de Hermes: `/reload-skills` (o reiniciar) y probar `/pm-ayuda`. Detalle, agentes y límites: §3.
No usar `hermes skills tap add` ni `hermes skills install` con este repositorio: instalan las skills tal cual, con rutas
`${CLAUDE_SKILL_DIR}` que Hermes no expande (Hermes expande `${HERMES_SKILL_DIR}`), y los scripts no se encontrarían.

### 0.6 Verificar
Seguir §8.

### 0.7 Claves de API y credenciales: cuáles, dónde y cómo

**pm-method no necesita ninguna clave propia.** Sus scripts son Python local y no llaman a servicios externos, con una
sola excepción opcional: la **capa de canales** (`envios.py`, v2.2), que envía comunicaciones aprobadas por correo SMTP
o por webhooks de Slack o Teams **solo si definís sus variables de entorno** (ver "Capa de canales" más abajo); sin
ellas, genera archivos `.eml` o deja el envío a un conector MCP. Las credenciales las necesitan solo cuatro cosas: el
**cliente** que ejecuta el modelo (Claude Code o Hermes), los **servidores MCP** de la organización (Jira, Slack,
Tability, Perdoo, etc.), la **capa de canales** si se usa y, si se usa, **Orca** (§0.8), que reutiliza el inicio de
sesión de cada agente. BMAD se instala con `npx` y tampoco pide claves.

| Qué | Credencial | Dónde se guarda | Cómo se configura |
|---|---|---|---|
| Claude Code con suscripción (Pro, Max, Team, Enterprise) — **recomendado** | inicio de sesión OAuth, sin clave | Linux/WSL: `~/.claude/.credentials.json` (permiso 0600) · macOS: Llavero · Windows: `%USERPROFILE%\.claude\.credentials.json` | ejecutar `claude` y seguir el navegador, o `/login` dentro de la sesión |
| Claude Code con clave de la Claude Console (facturación por API) | `ANTHROPIC_API_KEY` | variable de entorno del usuario (p. ej. `~/.bashrc` en Linux/WSL) | ver el bloque de abajo; al primer uso interactivo Claude Code pide aprobarla una vez |
| Claude Code con claves rotativas o de un gestor de secretos | salida de un script | `apiKeyHelper` en `~/.claude/settings.json` (el script devuelve la clave) | ver la referencia de settings de Claude Code |
| Claude Code en CI o scripts sin navegador | `CLAUDE_CODE_OAUTH_TOKEN` (token de un año) | variable de entorno del entorno de CI | `claude setup-token` lo imprime; no lo guarda solo |
| Claude Code vía Bedrock, Vertex o Foundry | credenciales del proveedor de nube | las del SDK del proveedor | `CLAUDE_CODE_USE_BEDROCK` / `CLAUDE_CODE_USE_VERTEX` / `CLAUDE_CODE_USE_FOUNDRY` + guía del proveedor |
| Hermes Agent | `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, etc. (según proveedor) | `~/.hermes/.env` | `hermes model` (selector) o `hermes setup` (asistente); o `hermes config set ANTHROPIC_API_KEY …` |
| Servidor MCP con token (stdio) | variable que pide el servidor | Claude Code: `~/.claude.json` (alcance `local` o `user`) | `claude mcp add <nombre> -e TOKEN=… -- <comando>` |
| Servidor MCP remoto (HTTP) | OAuth o cabecera | Claude Code: `~/.claude.json` | `claude mcp add --transport http <nombre> <url>` y luego `/mcp` para autenticar; o `-H "Authorization: Bearer …"` |
| Servidor MCP compartido por el equipo | nunca el valor: solo `${VARIABLE}` | `.mcp.json` en la raíz del proyecto (versionado) | `${VAR}` o `${VAR:-valor}` en `env`, `args`, `url` o `headers`; cada integrante define la variable en su entorno |
| MCP en Hermes | variable del servidor | bloque `env:` de `mcp_servers` en `~/.hermes/config.yaml` | ver la guía MCP de Hermes |
| Capa de canales: correo SMTP (`envios.py --modo smtp`) | `PM_SMTP_HOST`, `PM_SMTP_REMITENTE` (obligatorias); `PM_SMTP_PUERTO`, `PM_SMTP_TLS`, `PM_SMTP_USUARIO`, `PM_SMTP_CLAVE` (opcionales) | solo variables de entorno del usuario (nunca archivos del proyecto) | ver "Capa de canales" |
| Capa de canales: Slack (`--modo slack-webhook`) | `PM_SLACK_WEBHOOK_URL` (la URL del webhook entrante es en sí la credencial) | ídem | ver "Capa de canales" |
| Capa de canales: Teams (`--modo teams-webhook`) | `PM_TEAMS_WEBHOOK_URL` (URL del flujo de Workflows; también es la credencial) | ídem | ver "Capa de canales" |
| Capa de canales: `.eml` (`--modo eml`) | ninguna | — | sin configuración |

**Claude Code con clave de API, en Linux o WSL** (la clave se crea en la Claude Console, platform.claude.com):
```bash
# 1. Guardarla solo para tu usuario (no en la carpeta del proyecto ni en el repositorio)
echo 'export ANTHROPIC_API_KEY="<pegar aquí la clave>"' >> ~/.bashrc
chmod 600 ~/.bashrc
source ~/.bashrc
# 2. Abrir Claude Code: la primera vez pregunta si usar esa clave (la elección se recuerda;
#    se cambia luego en /config → "Use custom API key")
claude
# 3. Comprobar qué credencial está activa
/status
```
Windows PowerShell (persistente para el usuario): `[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY","<clave>","User")`
y abrir una terminal nueva. macOS: igual que Linux, en `~/.zshrc`.

**Orden de precedencia en Claude Code** (gana el primero presente; fuente: documentación oficial "Authentication",
comprobada el 2026-10-17): 1) proveedor de nube (`CLAUDE_CODE_USE_BEDROCK|VERTEX|FOUNDRY`) · 2) `ANTHROPIC_AUTH_TOKEN`
(pasarela o proxy) · 3) `ANTHROPIC_API_KEY` · 4) `apiKeyHelper` · 5) `CLAUDE_CODE_OAUTH_TOKEN` · 6) perfiles Anthropic
y federación · 7) inicio de sesión con suscripción (`/login`).

> **Atención:** si tenés suscripción **y** `ANTHROPIC_API_KEY` definida, Claude Code usa la clave una vez aprobada (y en
> modo `-p` la usa siempre), con cargo a la API. Para volver a la suscripción: `unset ANTHROPIC_API_KEY` (y quitarla de
> `~/.bashrc`), luego `/status`. Las pruebas en vivo de pm-method (`scripts/pruebas_vivo/`) usan `claude -p`, así que
> consumen la credencial que esté activa.

**WSL:** si después de iniciar sesión el navegador muestra un código en lugar de volver a la terminal, pegarlo en el
aviso `Paste code here if prompted` (pasa cuando el navegador de Windows no alcanza el servidor local de WSL).

**Hermes Agent** (en la máquina donde corre Hermes):
```bash
hermes model                                   # elegir proveedor y modelo; pide la clave y la guarda en ~/.hermes/.env
# o, sin asistente:
hermes config set ANTHROPIC_API_KEY "<clave>"  # las variables EN_MAYÚSCULAS van a ~/.hermes/.env, nunca a config.yaml
chmod 600 ~/.hermes/.env                       # recomendado
```
Proveedores con OAuth (por ejemplo `hermes auth add nous`) no usan clave escrita. La tabla completa de proveedores y
variables está en la documentación de Hermes (*Providers*).

#### Capa de canales: envío a interesados por correo, Slack o Teams (opcional, v2.2)

`skills/pm-integraciones/scripts/envios.py` envía comunicaciones **ya aprobadas** a los interesados del maestro
(`stakeholders.csv`). Usa solo la biblioteca estándar de Python y lee las credenciales **únicamente de variables de
entorno**: nunca de archivos, `estado.json` ni registros, y nunca las imprime. Sin `--confirmar` todo es simulación.
En los comandos, `<pm-integraciones>` es la carpeta instalada de esa skill, hermana de `<pm-estado-proyecto>` (§7.1).

| Variable | Modo | Obligatoria | Valor por defecto / valores |
|---|---|---|---|
| `PM_SMTP_HOST` | `smtp` | sí | nombre del servidor de correo, p. ej. `<tu-servidor>` |
| `PM_SMTP_REMITENTE` | `smtp` | sí | dirección del remitente, p. ej. `<tu-direccion>` |
| `PM_SMTP_PUERTO` | `smtp` | no | `587` |
| `PM_SMTP_TLS` | `smtp` | no | `starttls` (defecto), `ssl` o `ninguno` |
| `PM_SMTP_USUARIO`, `PM_SMTP_CLAVE` | `smtp` | no (solo si el servidor pide autenticación; se usan si están las dos) | — |
| `PM_SLACK_WEBHOOK_URL` | `slack-webhook` | sí | URL del webhook entrante de Slack |
| `PM_TEAMS_WEBHOOK_URL` | `teams-webhook` | sí | URL del flujo de Workflows de Teams |

**Dónde definirlas** (igual que `ANTHROPIC_API_KEY`; solo para tu usuario, nunca en la carpeta del proyecto ni en el
repositorio). Los valores de abajo son marcadores: reemplazarlos por los tuyos solo en tu terminal o en tu archivo de
perfil, nunca en el chat.

```bash
# Linux / WSL: en ~/.bashrc (macOS: igual, en ~/.zshrc)
echo 'export PM_SMTP_HOST="<tu-servidor>"'          >> ~/.bashrc
echo 'export PM_SMTP_REMITENTE="<tu-direccion>"'    >> ~/.bashrc
echo 'export PM_SMTP_USUARIO="<tu-usuario>"'        >> ~/.bashrc   # solo si el servidor pide autenticación
echo 'export PM_SMTP_CLAVE="<tu-clave>"'            >> ~/.bashrc   # ídem
echo 'export PM_SLACK_WEBHOOK_URL="<url-del-webhook-de-slack>"' >> ~/.bashrc
echo 'export PM_TEAMS_WEBHOOK_URL="<url-del-flujo-de-teams>"'   >> ~/.bashrc
chmod 600 ~/.bashrc
source ~/.bashrc
```
Windows PowerShell (persistente para el usuario; una línea por variable):
`[Environment]::SetEnvironmentVariable("PM_SMTP_HOST","<tu-servidor>","User")` y abrir una terminal nueva.
Para no dejar la clave SMTP escrita en un archivo de perfil, puede definirse solo en la terminal de la sesión
(`export PM_SMTP_CLAVE=…` en Linux/macOS/WSL, `$env:PM_SMTP_CLAVE = "…"` en PowerShell) antes de abrir Claude Code.
Claude Code hereda el entorno de la terminal desde la que se abre: después de definirlas, abrir una terminal nueva y
reiniciar la sesión. En Hermes y Cowork, cómo llegan las variables de entorno a los scripts no se probó **[verificar]**.

**Comprobar** (no usa la red: solo informa qué variables están definidas, sin mostrar sus valores; código de salida 1
si falta alguna obligatoria):
```bash
python3 <pm-integraciones>/scripts/envios.py --proyecto ./gestion verificar --modo smtp
python3 <pm-integraciones>/scripts/envios.py --proyecto ./gestion verificar --modo slack-webhook
python3 <pm-integraciones>/scripts/envios.py --proyecto ./gestion verificar --modo teams-webhook
```
`verificar` no prueba la conexión: la primera prueba real conviene hacerla con un mensaje aprobado dirigido a uno mismo
(`enviar … --modo smtp --confirmar --mensaje <archivo>`). El flujo completo (crear, aprobar, simular, enviar, registrar)
está en [INTEGRACIONES.md §3.2](INTEGRACIONES.md).

**Sin ninguna configuración: archivos `.eml`.** `envios.py --proyecto ./gestion enviar <carpeta> --modo eml --confirmar`
escribe un `.eml` por destinatario en `<carpeta>/eml/` (cabecera `X-Unsent: 1`, que Outlook abre como borrador; en
otros clientes de correo **[verificar]**) y lo registra como `pendiente` en `envios.csv`. Se abre, se revisa y se envía
desde el cliente de correo habitual; luego se deja constancia con
`envios.py --proyecto ./gestion registrar <carpeta> --mensaje <mensaje-NN-….md> --modo eml`. El modo `eml` no necesita
variables, servidor ni conector.

**Crear el webhook de Teams (Workflows).** Según la página de Microsoft "Create an Incoming Webhook"
(https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook,
consultada el 2026-10-17), a alto nivel: en Teams, ir al equipo y canal que recibirán los mensajes → **More options
(…)** junto al canal → **Workflows** → buscar y elegir una plantilla como **Send webhook alerts to a channel** →
configurar los parámetros → **Save** → copiar el enlace del webhook que muestra el flujo. También puede crearse un flujo
desde cero con el disparador **When a Teams webhook request is received**. Los nombres de menús y plantillas pueden
cambiar y pueden variar según el idioma de Teams **[verificar en tu Teams]**. Esa misma página indica que los conectores
de Microsoft 365 (antes Office 365) están "nearing deprecation" y que el límite de mensaje es 28 KB (`envios.py`
rechaza mensajes más grandes). `envios.py` envía una tarjeta adaptable (`type: message` con `attachments`
`application/vnd.microsoft.card.adaptive`); se probó solo contra un servidor local, no contra un flujo real
**[verificar con tu flujo]**. La URL copiada va en `PM_TEAMS_WEBHOOK_URL`; quien la tenga puede publicar en el canal,
así que se trata como credencial.

**Crear el webhook entrante de Slack.** A alto nivel: en la administración de apps de Slack, crear (o reutilizar) una
app del espacio de trabajo, activar **Incoming Webhooks**, agregar un webhook nuevo eligiendo el canal y copiar su URL
**[verificar nombres y pasos en la documentación vigente de Slack; puede requerir aprobación de un administrador del
espacio de trabajo]**. Cada webhook publica en un solo canal. La URL va en `PM_SLACK_WEBHOOK_URL` y se trata como
credencial. `envios.py` menciona a la persona (`<@ID>`) solo si su `usuario_chat` en `stakeholders.csv` es un id de
usuario de Slack (empieza con `U` o `W`).

#### Conectores OKR: Tability y Perdoo (opcional, v2.2)

Ambos publican un servidor MCP remoto oficial (verificado el 2026-10-17 en su documentación). Se agregan como cualquier
MCP remoto (§6) y se autentican en una sesión con `/mcp`:

```bash
# Tability (servidor por defecto, nube de EE. UU.)
claude mcp add --transport http tability https://mcp.tability.app/mcp
#   espacios de trabajo en la nube de la UE: https://mcp-eu.tability.app/mcp · de Australia: https://mcp-au.tability.app/mcp
# Perdoo
claude mcp add --transport http perdoo https://mcp.perdoo.com
# luego, dentro de una sesión de Claude Code:
/mcp
```

| Conector | Autenticación | Requisitos | Herramienta para check-ins | Fuente |
|---|---|---|---|---|
| Tability | OAuth en el navegador (su guía indica que nunca se pide pegar un token) | "API Access Enabled" = Yes para tu usuario (Settings > Users; puede hacerlo el administrador del espacio de trabajo) | `tability_create_checkin` | https://guides.tability.io/docs/become-a-tability-power-user/integrations/tability-mcp-server |
| Perdoo | OAuth o clave de API (Personal settings > API tokens; se envía en la cabecera `Authorization: Bearer …`) | plan comercial requerido: no lo indica la página **[verificar]** | `update_goal_progress` | https://support.perdoo.com/en/articles/14470891-mcp-server (artículo del 15/09/2026) |

Preferir OAuth. Si se usa la clave de Perdoo: `claude mcp add --transport http perdoo https://mcp.perdoo.com -H
"Authorization: Bearer <tu-clave-de-api>"` (queda en `~/.claude.json`; nunca en `.mcp.json` versionado). Ninguna de las
dos guías muestra un comando de Claude Code: el comando es la forma general de `claude mcp add` ya documentada; no se
probó en vivo con pm-method **[verificar]**. Después: `estado.py --proyecto ./gestion integracion okr=tability` (o
`okr=perdoo`); la publicación de check-ins la propone `okr.py 00-direccion/okr.csv --propuesta-sync tability|perdoo` y
siempre requiere vista previa y confirmación.

**Reglas de seguridad** (las mismas que aplica el paquete):
- Nunca pegar claves, tokens ni contraseñas en el chat con Claude ni con ningún asistente, ni escribirlas en archivos de
  la carpeta del proyecto, en `estado.json`, en los registros ni en commits.
- En archivos versionados (`.mcp.json`, `.claude/settings.json`) solo referencias `${VARIABLE}`, nunca el valor.
- Si una clave se expuso: revocarla en su consola de origen (Claude Console, Jira, Slack…) y crear una nueva. Una URL de
  webhook expuesta se trata igual: eliminar el webhook (o el flujo de Teams) y crear otro.

### 0.8 Orca (opcional): varias sesiones de agentes y proyectos en un solo lugar

[Orca](https://github.com/stablyai/orca) (licencia MIT) es una aplicación de escritorio para trabajar con **varios agentes
de código en paralelo** (Claude Code, Hermes Agent, Codex y otros), cada uno en su propio *git worktree*, con terminales
divididas y persistentes, tableros de GitHub y Linear, anotación de diffs, notificaciones cuando un agente termina o
necesita atención, y una app móvil compañera. Usa la suscripción o el inicio de sesión de cada agente (por eso conviene
completar §0.7 antes).

**Para qué sirve con pm-method** (sugerencia de uso; no es requisito):
- Tener a la vista, en una sola ventana, la sesión de gestión (`claude --agent pm-method:pm-orquestador` en la carpeta
  `gestion/`) y las sesiones del equipo de producto que trabajan sobre BMAD en el repositorio del producto.
- Varios proyectos de gestión abiertos a la vez, cada uno en su terminal o worktree, con aviso cuando un agente espera
  una decisión (por ejemplo, la confirmación de una lista de control de puerta).
- Seguir el avance desde el teléfono con la app compañera.

**Importante — TUI:** según su documentación, Orca es una aplicación **gráfica** que contiene terminales; su CLI `orca`
controla la aplicación en ejecución (worktrees, terminales, archivos) y **no es una interfaz de texto (TUI)
independiente**. La interfaz de texto de pm-method sigue siendo la del propio Claude Code o Hermes, que corren dentro
de las terminales de Orca.

**Instalación** (comandos tal como figuran en el repositorio de Orca, consultado el 2026-10-17):

| Sistema | Cómo |
|---|---|
| Windows | instalador `.exe` desde onorca.dev/download o desde las *releases* de GitHub |
| macOS | `brew install --cask stablyai/orca/orca` (o la descarga para macOS de onorca.dev/download) |
| Linux (escritorio) | AppImage desde `https://github.com/stablyai/orca/releases/latest` |
| Arch Linux | `yay -S stably-orca-bin` |
| Linux sin pantalla (servidor) | `orca-linux.AppImage serve --port 6768 --pairing-address <IP>`; requiere Xvfb y librerías de Electron (guía *headless-linux-server* del repositorio) y se empareja desde el escritorio o el móvil con la URL `orca://pair?code=…` |

**WSL:** la documentación de Orca no trae una guía para WSL **[verificar]**. La opción más directa es instalar la
versión de Windows y abrir desde ella terminales que ejecuten `wsl` para lanzar `claude` dentro de Ubuntu; confirmar en
la propia aplicación que las terminales y los worktrees sobre rutas de WSL funcionan como se espera.

**CLI y skill para los agentes** (opcional): activar la CLI en *Settings → General → Orca CLI*, comprobar con
`command -v orca` y `orca status --json`, e instalar la skill que enseña a los agentes a usarla:
```bash
npx skills add https://github.com/stablyai/orca --skill orca-cli
# sin interfaz de configuración:
orca skills install --skill orca-cli
```
Privacidad: Orca envía datos de uso anónimos que se pueden desactivar (ver su página de telemetría).

---

## 1. Requisitos previos

### 1.1 Lista de comprobación

| Requisito | Necesario para | Comprobar con | Esperado |
|---|---|---|---|
| Cliente: Claude Code, Cowork o Hermes Agent | todo | `claude --version` (Claude Code) | probado con `2.1.302 (Claude Code)` |
| Python ≥ 3.9 | todos los scripts y los hooks | `python3 --version` | `Python 3.9` o superior |
| git | instalar y actualizar desde GitHub; en Windows, Git Bash para los hooks | `git --version` | cualquier versión vigente |
| `pyyaml`, `python-docx`, `openpyxl` (recomendados) | BMAD, exportar Word/Excel, actas `.docx` | `python3 -c "import yaml, docx, openpyxl; print('ok')"` | `ok` |
| Node.js y `npx` (opcional) | BMAD (`≥ 20.12`); skills externas con `npx skills` (`≥ 22.20`) | `node --version` y `npx --version` | `v22.20.0` o superior para cubrir todo |
| Chrome o Chromium (opcional) | `browser-check` de archify | — | instalado, o `ARCHIFY_CHROME` definido |
| `mmdc`, Java + MPXJ (opcionales) | Mermaid como imagen en Word; validar MSPDI | `mmdc --version`, `java -version` | §6.2 |

Origen, licencia y versión probada de cada uno: [DEPENDENCIAS.md](DEPENDENCIAS.md).

### 1.2 Windows (Git for Windows + PowerShell)

- **Claude Code**: según el README de su repositorio, `irm https://claude.ai/install.ps1 | iex` en PowerShell o
  `winget install Anthropic.ClaudeCode`.
- **Git for Windows es necesario para los hooks de pm-method.** Claude Code ejecuta en Windows los hooks con Git Bash
  (CHANGELOG de Claude Code 2.1.47) y, desde 2.1.299, un hook `PreToolUse` sin shell declarado que falla porque no hay
  Git for Windows **bloquea** la llamada. Los hooks de pm-method no declaran shell: sin Git for Windows, las ediciones y
  comandos que vigila `guardian.py` quedarían bloqueados. Sin Git Bash, Claude Code usa PowerShell como herramienta de
  shell (CHANGELOG 2.1.120), pero eso no cubre los hooks del plugin.
- **Python debe responder dentro de Git Bash**: desde 2.1.0 los hooks se lanzan con `sh "${CLAUDE_PLUGIN_ROOT}/hooks/py.sh" …`,
  que prueba `python3`, luego `python` y luego `py -3`, y descarta el alias de Microsoft Store (que no ejecuta código).
  Abrir Git Bash y ejecutar `python --version` o `py -3 --version`: alguno debe mostrar 3.9 o superior. Si no hay
  Python, `py.sh` avisa por la salida de error y **no bloquea** (los hooks quedan sin efecto). El lanzador no se probó
  todavía en una máquina Windows real **[verificar]**. El repositorio fuerza finales de línea LF en `.sh` y `.py`
  (`.gitattributes`), necesarios para Git Bash.
- En PowerShell, los comandos `python3 …` de esta guía pueden requerir `python …` o `py -3 …` según cómo se instaló
  Python **[verificar]**. Para los paquetes: `python -m pip install pyyaml python-docx openpyxl` (o `py -3 -m pip …`).
- Rutas: la carpeta de configuración de Claude Code es `%USERPROFILE%\.claude` **[verificar]**; Hermes nativo instala en
  `%LOCALAPPDATA%\hermes` (en WSL2, `~/.hermes`), según su README.
- Chrome para archify: archify busca `chrome.exe` en `Program Files`, `Program Files (x86)` y `%LOCALAPPDATA%` (código de
  `bin/visual-check.mjs`), pero la sanidad de pm-method solo mira el `PATH` y `ARCHIFY_CHROME`. Para que coincidan,
  definir `ARCHIFY_CHROME` con la ruta completa de `chrome.exe`.
- `npx skills add` crea enlaces simbólicos o copias según el caso (con un solo agente, `-a claude-code`, copió los
  archivos en la prueba); si fallan los enlaces en Windows, agregar `--copy` (opción de `npx skills add --help`).

### 1.3 macOS

- Claude Code: `curl -fsSL https://claude.ai/install.sh | bash` o `brew install --cask claude-code` (README de Claude
  Code).
- git y Python 3: comprobar con `git --version` y `python3 --version`; si faltan, instalarlos con el método habitual del
  equipo **[verificar]**.
- Chrome: la sanidad reconoce `/Applications/Google Chrome.app` y `/Applications/Chromium.app`.

### 1.4 Linux

- Claude Code: `curl -fsSL https://claude.ai/install.sh | bash` (README de Claude Code).
- git, Python 3 y Node.js desde el gestor de paquetes de la distribución; comprobar que Node cumpla la versión mínima
  (§1.1), porque las distribuciones suelen traer versiones anteriores.
- En sistemas con Python gestionado por el sistema operativo, `pip install` puede rechazarse: usar un entorno virtual
  (§5).

---

## 2. Instalación en Claude Code desde una carpeta local

### 2.1 Como plugin desde el marketplace local

Alternativa a §0 cuando se trabaja con una copia local (por ejemplo, el mantenedor). La carpeta del paquete es a la vez
un plugin (`.claude-plugin/plugin.json`, nombre `pm-method`, versión 2.2.0) y un marketplace local
(`.claude-plugin/marketplace.json`, nombre `pm-method`). Junto con §0, es la única modalidad que activa los **hooks** de
protección y de sanidad (§9).

```bash
claude plugin marketplace add /ruta/a/pm-method
claude plugin install pm-method@pm-method
claude plugin list                       # pm-method debe figurar instalado y habilitado
```

O dentro de una sesión de Claude Code:

```
/plugin marketplace add /ruta/a/pm-method
/plugin install pm-method@pm-method
```

Qué queda disponible:
- 38 skills, invocables como `/pm-method:<skill>` (32 que el modelo puede activar solo y 6 comandos de uso humano).
- 6 agentes: `pm-method:pm-orquestador` (para el hilo principal) y los subagentes de fase `pm-method:pm-director`,
  `pm-method:pm-inicio`, `pm-method:pm-planificacion`, `pm-method:pm-control`, `pm-method:pm-cierre`.
- Hooks `PreToolUse` (`hooks/guardian.py`) y `SessionStart` (`hooks/inicio.py`), declarados en `hooks/hooks.json`.

Para probar el paquete sin instalarlo: `claude --plugin-dir /ruta/a/pm-method`. No hay carpeta `commands/`: es un formato
heredado y en v2 los comandos son skills.

### 2.2 Copia manual (sin plugin)

```bash
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r /ruta/a/pm-method/skills/* ~/.claude/skills/
cp /ruta/a/pm-method/agents/*.md ~/.claude/agents/
```

- Para un solo repositorio, copiar a `.claude/skills/` y `.claude/agents/` de ese repositorio.
- Las skills se invocan como `/<skill>` (sin prefijo) y los subagentes como `pm-inicio`, `pm-control`, etc.
- Los scripts quedan en `~/.claude/skills/<skill>/scripts/`.
- **Diferencia importante:** la copia manual **no registra los hooks** (dependen de `hooks/hooks.json` del plugin). La
  sanidad sigue disponible a demanda (`/pm-sanidad`) y la exigen `pm-puerta` y `pm-orquestador`, pero no hay bloqueo
  automático de ediciones sobre `estado.json` ni sobre los registros.
- No combinar plugin y copia manual: la sanidad lo detecta como **INS-04** (skill instalada más de una vez).

### 2.3 Cowork

Cowork usa el formato de plugin: instalar `pm-method` desde la gestión de plugins de la aplicación, apuntando al mismo
paquete. **[verificar]** el recorrido exacto de pantallas en la versión vigente de la aplicación. Las skills personales
de `~/.claude/skills/` no son una vía de instalación para Cowork.

---

## 3. Instalación en Hermes Agent

**Compatibilidad (verificada el 2026-10-17 con Hermes Agent `8ce2a4f`, 2026.9.24):** Hermes lee skills `SKILL.md` y
las ofrece como comandos `/nombre`; la instalación con `scripts/instalar_hermes.py` dejó visibles las 37 skills de la versión 2.1.0 en
`hermes skills list` (la 2.2.0 agrega `pm-interesados`: 38; el script copia todas las carpetas de `skills/`, pero esa
cifra no se volvió a comprobar dentro de Hermes **[verificar]**), y la sustitución de `${HERMES_SKILL_DIR}` de Hermes resolvió las rutas de los scripts a archivos
existentes. **No se probó una conversación completa con un modelo dentro de Hermes** (no había proveedor configurado en el
entorno de prueba) **[verificar en el primer uso]**.

| Capacidad | Claude Code (plugin) | Hermes |
|---|---|---|
| 38 skills y comandos `/…` | sí (`/pm-method:<skill>`) | sí (`/<skill>`) |
| Scripts (estado, registros, BMAD, sanidad, EVM, CPM…) | sí | sí (mismos scripts Python) |
| Subagentes de fase y orquestador como agente | sí | no: los agentes se usan como persona/personalidad; las skills corren en el mismo hilo |
| Hooks (guardian, inicio, idioma) | sí | no: la protección de `estado.json` y registros queda en las reglas de las skills y en la sanidad (`/pm-sanidad`, `/pm-puerta`) |
| Bloqueos de puerta en `estado.py` | sí | sí (están en el script) |

### 3.1 Instalar
```bash
git clone https://github.com/Arturo-Penas-Rial/pm-method.git ~/pm-method
python3 ~/pm-method/scripts/instalar_hermes.py --verificar   # muestra qué hará
python3 ~/pm-method/scripts/instalar_hermes.py               # copia adaptada en ~/.hermes/skills/pm-method/
pip install pyyaml python-docx openpyxl                      # en el Python con que Hermes ejecuta comandos (§5)
```
El script copia `skills/` reemplazando `${CLAUDE_SKILL_DIR}` por `${HERMES_SKILL_DIR}`, deja los agentes en
`~/.hermes/skills/pm-method/_agentes/` con rutas absolutas y no copia los hooks. Si se prefiere una carpeta propia:
`--destino ~/pm-hermes` y agregarla en `~/.hermes/config.yaml`:
```yaml
skills:
  external_dirs:
    - ~/pm-hermes
```
Precedencia de Hermes ante nombres repetidos: proyecto → `~/.hermes/skills/` → `skills.create_dir` → `external_dirs`.
Los directorios externos **no** están protegidos contra escritura: el agente de Hermes puede modificar skills donde las
encuentre (documentación de Hermes, "External Skill Directories").

### 3.2 Agentes como personas
Hermes no tiene subagentes con nombre. Usar `_agentes/pm-orquestador.md` como persona: crear un perfil
(`hermes profile create pm`) y copiar el cuerpo del archivo como `SOUL.md` del perfil, o declararlo como personalidad en
`config.yaml` y activarlo con `/personality` **[verificar la sintaxis vigente de perfiles y personalidades en la
documentación de Hermes]**. La lógica de cada fase vive en las skills, que el orquestador ejecuta en el mismo hilo.

### 3.3 Actualizar y desinstalar
`git -C ~/pm-method pull` y volver a correr `instalar_hermes.py` (reemplaza solo su propia copia, marcada con el archivo
`.pm-method`); luego `/reload-skills`. Desinstalar: borrar `~/.hermes/skills/pm-method/` (o la carpeta de `--destino` y
su entrada en `external_dirs`).

En Windows nativo Hermes instala bajo `%LOCALAPPDATA%\hermes` (README de Hermes); las rutas `~/.hermes/…` son de Linux,
macOS y WSL2 **[verificar la ruta en Windows nativo]**. En WSL2 todo funciona como en Linux.

---

## 4. BMAD en el repositorio del producto (opcional)

pm-method **no instala ni actualiza BMAD**; lo instala el equipo del producto en la raíz de su repositorio. Requiere
Node.js ≥ 20.12.0 (`engines` de `bmad-method@6.12.4`).

### 4.1 Instalar BMAD (versión probada)

```bash
cd /ruta/al/repositorio
npx bmad-method@6.12.4 install --modules bmm --tools claude-code --yes \
    --user-name "<nombre>" --set core.project_name=<proyecto> --no-shims
```

Opciones (comprobadas con `npx bmad-method@6.12.4 install --help`, `--list-options core` y `--list-tools`, y con una
instalación real el 2026-10-17):

| Opción | Efecto |
|---|---|
| `--modules bmm` | módulo de métodos (PRD, arquitectura, épicas, sprint) |
| `--tools claude-code` | instala las skills en `.claude/skills/`; obligatoria con `--yes` en una instalación nueva |
| `--yes` | acepta los valores por defecto sin preguntar |
| `--user-name <nombre>` | nombre con el que los agentes se dirigen al usuario |
| `--set core.project_name=<proyecto>` | nombre del proyecto (por defecto, el de la carpeta) |
| `--no-shims` | no instala las skills de compatibilidad obsoletas |
| `--communication-language <idioma>` / `--document-output-language <idioma>` | opcionales; por defecto, English |

Resultado: carpetas `_bmad/` y `_bmad-output/` y skills `bmad-*` en `.claude/skills/` (`bmad-prd`, `bmad-architecture`,
`bmad-create-epics-and-stories`, `bmad-sprint-planning`, `bmad-build`, `bmad-correct-course`, `bmad-help`, entre
otras). Las salidas van a `_bmad-output/planning-artifacts/` (carpetas fechadas para brief, PRD, arquitectura y UX;
`epics.md` fijo) e `_bmad-output/implementation-artifacts/sprint-status.yaml`. En v4 usa `docs/` y
`.bmad-core/core-config.yaml`.

### 4.2 Detectar BMAD desde pm-method

La carpeta del proyecto de gestión debe quedar **fuera** de `_bmad/`, `_bmad-output/` y `.bmad-core/` (por ejemplo,
`repositorio/gestion/`, creada con §7.2 o con `/pm-method:pm-nuevo`):

```bash
python3 <pm-bmad-puente>/scripts/bmad.py --proyecto ./gestion detectar
```

`detectar` registra en `estado.json.integraciones` `especificacion=bmad` y el bloque `bmad` con el layout (`v6` | `v4`),
las rutas (relativas a `--proyecto`), la versión y su fuente (`_bmad/_config/manifest.yaml`) y el soporte (`soportada`,
`v4`, `version-no-visible`, `no-probada`). En la prueba del 2026-10-17 devolvió `version 6.12.4` y
`soporte: soportada`. Si BMAD no está en un directorio superior, agregar `--raiz <repo>` **antes** del subcomando
(`bmad.py --proyecto ./gestion --raiz .. detectar`). El comando `/pm-nuevo` hace esta detección al crear el proyecto.
Para declararlo a mano: `estado.py --proyecto ./gestion integracion especificacion=bmad`.

Con BMAD instalado, las descripciones de sus skills se suman al listado de Claude Code: la sanidad avisa **INS-05**
(ver §7.4).

### 4.3 Compatibilidad y actualización de BMAD

Compatibilidad declarada (`compatibilidad.json`): probado con BMAD 4.x, 6.11 y 6.12; relevado `bmad-method@6.12.4`.
BMAD introduce cambios incompatibles en casi cada versión menor 6.x; fuera de rango el puente trabaja en **modo
degradado con aviso** (sanidad ESP-07) y conviene correr `scripts/probar_paquete.py` antes de la siguiente puerta.
Para actualizar una instalación existente, `install` acepta `--action update` o `--action quick-update` (según
`--help`) **[verificar el comportamiento antes de usarlo en un repositorio real]**; después, repetir `bmad.py detectar`.
El instalador 6.12.4 anuncia una vista previa de BMAD v7 (`npx skills add bmad-code-org/BMAD-METHOD`): **no está
probada** con pm-method.

---

## 5. Dependencias Python

```bash
python3 -m pip install pyyaml python-docx openpyxl
```

- Con Python gestionado por el sistema operativo (frecuente en Linux), usar un entorno virtual:
  `python3 -m venv ~/.venvs/pm-method` y luego `~/.venvs/pm-method/bin/python -m pip install pyyaml python-docx openpyxl`;
  en ese caso, los scripts y los hooks deben ejecutarse con un `python3` que vea esos paquetes **[verificar]**. La
  alternativa `--break-system-packages` instala en el Python del sistema.
- Windows: ver §1.2.
- La sanidad informa la falta de cada módulo como **INS-01** con el comando de instalación.

| Paquete | Lo usa |
|---|---|
| `pyyaml` | `bmad.py` (configuración de BMAD, `sprint-status.yaml`) y `scripts/probar_paquete.py` |
| `python-docx` | `exportar.py docx` (pm-exportar) y `transcripcion.py` (actas `.docx`, pm-reuniones) |
| `openpyxl` | `exportar.py xlsx` (pm-exportar) |

---

## 6. Conexión de herramientas MCP

El paquete **no trae `.mcp.json` ni credenciales** y no predefine conectores. Las skills describen capacidades y
`pm-integraciones` las resuelve con los MCP presentes en la sesión.

### Paso 1: conectar el servidor en el cliente

En Claude Code (sintaxis de `claude mcp add --help`):

```bash
# servidor remoto (HTTP)
claude mcp add --transport http <nombre> <url-del-servidor>
# servidor local (stdio): todo lo que sigue a -- es el comando que lo arranca
claude mcp add <nombre> -- <comando> [argumentos]
# alcance: -s local (por defecto) | user | project
claude mcp add -s user --transport http <nombre> <url-del-servidor>

claude mcp list                # servidores configurados y su estado
claude mcp get <nombre>        # detalle de uno
claude mcp login <nombre>      # autenticar por OAuth (o /mcp dentro de una sesión)
claude mcp remove <nombre>
```

- Con `-s project` el servidor queda declarado para el repositorio (archivo `.mcp.json`, que cada persona aprueba);
  nunca poner tokens en ese archivo ni en la carpeta del proyecto de gestión. Preferir OAuth (`claude mcp login` o
  `/mcp`) a encabezados con tokens (`-H "Authorization: …"`).
- No hay URLs de servidor predefinidas en pm-method: usar la que publique cada proveedor. Las comprobadas están en
  [DEPENDENCIAS.md §5](DEPENDENCIAS.md); las demás figuran como "URL a confirmar por el usuario".
- Ejemplos tomados de la documentación de cada proyecto (no probados en vivo con pm-method):

  | Conector | Comando |
  |---|---|
  | Atlassian Rovo (Jira, Confluence) | `claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp` y luego `/mcp` en una sesión para autenticar (README de `atlassian/atlassian-mcp-server`) |
  | minutes | `claude mcp add minutes -- npx -y minutes-mcp` (README de `silverstein/minutes`) |
  | draw.io | `claude mcp add drawio -- npx -y @drawio/mcp` (README de `jgraph/drawio-mcp`); o el plugin: `claude plugin marketplace add jgraph/drawio-mcp` y `claude plugin install drawio@drawio` |
  | Tability (OKR) | `claude mcp add --transport http tability https://mcp.tability.app/mcp` (UE: `mcp-eu.tability.app/mcp`; AU: `mcp-au.tability.app/mcp`) y luego `/mcp`; URL de su guía oficial, detalle en §0.7 |
  | Perdoo (OKR) | `claude mcp add --transport http perdoo https://mcp.perdoo.com` y luego `/mcp`; URL de su artículo de soporte, detalle en §0.7 |

- Conectores de la aplicación (claude.ai / Cowork): se conectan desde su gestión de conectores; las credenciales quedan
  en el cliente.
- Hermes: `hermes mcp add <nombre>` con `--url` o `--command` (referencia de CLI de Hermes) **[verificar opciones]**.

### Paso 2: declarar la capacidad en el proyecto

Pedir a pm-method que detecte y registre las capacidades (`pm-integraciones` o `/pm-method:pm-sync`), o registrarlas a
mano (varias claves en un mismo comando):
```bash
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion integracion tracker=jira docs=confluence chat=teams
```

Valores reconocidos por la sanidad (lista de **INT-01** en `sanidad.py`; valores por defecto en `esquema.py`):

| Capacidad (`estado.json.integraciones`) | Valores reconocidos | Por defecto | Ejemplos de servidor |
|---|---|---|---|
| `tracker` | `ninguno`, `jira`, `linear`, `github`, `azure-devops` | `ninguno` | Atlassian Rovo MCP Server |
| `docs` | `ninguno`, `confluence`, `notion`, `sharepoint` | `ninguno` | Atlassian Rovo (Confluence) |
| `chat` | `ninguno`, `slack`, `teams` | `ninguno` | Slack MCP oficial; Teams/Work IQ |
| `correo` (v2.2) | `ninguno`, `smtp`, `gmail`, `outlook`, `eml` | `ninguno` | `gmail`/`outlook`: conector de la organización **[verificar]**; `smtp`/`eml`: capa de canales sin conector (§0.7) |
| `reuniones` | `manual`, `archivo`, `granola`, `fireflies`, `zoom`, `minutes`, `teams` | `manual` | Granola, Fireflies, Zoom, minutes-mcp |
| `okr` | `archivo`, `tability`, `perdoo` | `archivo` | Tability MCP, Perdoo MCP (§0.7) |
| `especificacion` | `ninguna`, `bmad` | `ninguna` | — (lo fija `bmad.py detectar`, §4.2) |
| `diagramas` | `mermaid`, `diagram-design`, `archify`, `visual-explainer`, `drawio` (o lista por prioridad, `archify,visual-explainer`) | `mermaid` | drawio-mcp; skills externas (§6.1) |
| `cronograma` | `cpm`, `mspdi` | `cpm` | — (interno) |
| `export` | `scripts`, `skills-office` | `scripts` | skills docx/xlsx/pptx (§6.1) |

Un valor fuera de la lista se guarda igual, pero la sanidad lo informa como **INT-01** (AVISO). Con un tracker declarado,
**INT-02/03/04** vigilan las instantáneas de `03-control/fuentes/` durante la entrega.

Reglas que aplica el paquete: lectura libre; **escritura externa solo con vista previa y confirmación explícita**; los
datos externos entran como instantáneas fechadas en `03-control/fuentes/`. Detalle y justificación en
`INTEGRACIONES.md`. Notas de proveedores relevadas al 2026-10-17: el servidor "Teams (preview)" de Microsoft está
marcado como legado (se recomienda Work IQ); el Slack MCP oficial está restringido a apps publicadas o internas; la
obtención de transcripciones por Zoom MCP **no está confirmada**.


### 6.1 Skills externas opcionales (diagramas y Office)

Son skills de terceros, no MCP. pm-method no las trae: el usuario las instala y luego declara el motor en
`estado.json`. Comandos verificados el 2026-10-17 con Claude Code 2.1.302 (clonado público de GitHub; `npx skills`
1.7.0, que exige **Node.js ≥ 22.20.0**). Revisar cada skill antes de instalarla: corre con los permisos del agente.

| Integración | Repositorio · licencia · distribución | Instalar como plugin (Claude Code) | Instalar como skill copiada (proyecto; `-g` = usuario) | Nombre en el listado | Requisitos |
|---|---|---|---|---|---|
| `diagramas=archify` | `tt-a1i/archify` · MIT · carpeta de skill `archify/` (sin plugin) | — | `npx skills add tt-a1i/archify -a claude-code -s archify -y` | `archify` | Node ≥ 18; Chrome/Chromium (o `ARCHIFY_CHROME=<ejecutable>`) para su verificación en navegador |
| `diagramas=diagram-design` | `cathrynlavery/diagram-design` · MIT · plugin + marketplace | `claude plugin marketplace add cathrynlavery/diagram-design` y `claude plugin install diagram-design@diagram-design` | `npx skills add cathrynlavery/diagram-design -a claude-code -s diagram-design -y` | `diagram-design:diagram-design` (plugin) o `diagram-design` | Python 3; PNG opcional con `pip install playwright && playwright install chromium` |
| `diagramas=visual-explainer` | `nicobailon/visual-explainer` · MIT · plugin + marketplace | `claude plugin marketplace add nicobailon/visual-explainer` y `claude plugin install visual-explainer@visual-explainer-marketplace` | `npx skills add nicobailon/visual-explainer -a claude-code -s visual-explainer -y` | `visual-explainer:visual-explainer` o `visual-explainer` | Node ≥ 18; `playwright-core` opcional |
| `export=skills-office` | `anthropics/skills` (`skills/docx`, `xlsx`, `pptx`) · **propietaria** (source-available; `LICENSE.txt` en cada skill) · plugin `document-skills` | `claude plugin marketplace add anthropics/skills` y `claude plugin install document-skills@anthropic-agent-skills` | `npx skills add anthropics/skills -a claude-code -s docx xlsx pptx -y` | `document-skills:docx` …, `docx` …, o `anthropic-skills:docx` … (claude.ai/Cowork) | Node + npm `docx` / `pptxgenjs`; `openpyxl`; LibreOffice (recálculo y vista previa); `pandoc` |

Notas:
- Dentro de una sesión interactiva los comandos de plugin equivalen a `/plugin marketplace add …` y `/plugin install …`.
  Con `--scope project` quedan declarados en `.claude/settings.json` del repositorio para todo el equipo.
- `npx skills add` sin `-g` instala en `.claude/skills/` del directorio actual: ejecutarlo en la raíz donde se abre
  Claude Code (la que contiene la carpeta del proyecto de gestión). Sin `-s` instala todas las skills del repositorio
  (archify trae además skills internas de mantenimiento; anthropics/skills trae 20). El plugin `document-skills`
  incluye también `pdf`.
- Para probar un plugin sin instalarlo: `claude --plugin-dir <clon>` (la sanidad no puede verlo y emite INS-03 AVISO).
- Actualizar: skills copiadas con `npx skills update` (`-g` usuario, `-p` proyecto, `-y` sin preguntar); plugins con
  `claude plugin marketplace update <marketplace>` y `claude plugin update <plugin>@<marketplace>` (marketplaces:
  `diagram-design`, `visual-explainer-marketplace`, `anthropic-agent-skills`).

Declarar y comprobar:
```bash
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion integracion diagramas=archify          # o diagram-design, visual-explainer
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion integracion diagramas=archify,visual-explainer  # lista por prioridad
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion integracion export=skills-office
python3 <pm-estado-proyecto>/scripts/sanidad.py --proyecto ./gestion | grep INS-03   # "invocar como …" o AVISO si falta
```
Resultado esperado: una línea `INFO INS-03 Skill externa '<skill>' (<valor>) instalada: invocar como '<nombre>' · <origen> · <ruta>`
por skill (comprobado el 2026-10-17 con archify copiada y con diagram-design, visual-explainer y `document-skills`
instalados como plugin). Sin la skill, o si falla, pm-visuales entrega Mermaid y pm-exportar usa `exportar.py`, con nota
en `diario.md`. Volver al respaldo: `integracion diagramas=mermaid` / `integracion export=scripts`.

### 6.2 Herramientas opcionales del sistema

| Herramienta | Para qué | Instalar | Comprobar |
|---|---|---|---|
| `@mermaid-js/mermaid-cli` (`mmdc`) | `exportar.py` inserta los diagramas Mermaid como imagen en Word | `npm install -g @mermaid-js/mermaid-cli` (la 12.0.0 exige Node ≥ 22.13.0) | `mmdc --version` |
| Java + MPXJ | validar o convertir el MSPDI de `cpm.py --mspdi` y `.mpp`; `cpm.py` no lo necesita | Java del sistema y `python3 -m pip install mpxj jpype1` | `java -version`; `python3 -c "import jpype, mpxj"` |
| Chrome o Chromium | `browser-check` de archify | navegador del sistema; si no se encuentra, `ARCHIFY_CHROME=<ruta>` | sanidad INS-03 (sin INFO "no se encontró Chrome") |

---

## 7. Configuración

### 7.1 Ubicación de los scripts

| Instalación | `<pm-estado-proyecto>` |
|---|---|
| Plugin de Claude Code / Cowork | `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/`; instalado desde GitHub queda en `~/.claude/plugins/cache/pm-method/pm-method/<versión>/skills/pm-estado-proyecto/` (observado con Claude Code 2.1.302) |
| Copia manual | `~/.claude/skills/pm-estado-proyecto/` (o `.claude/skills/…` del repositorio) |
| Hermes | `~/.hermes/skills/pm-method/pm-estado-proyecto/` (o `<--destino>/pm-estado-proyecto/`); en las skills, `${HERMES_SKILL_DIR}/../pm-estado-proyecto/` |

`<pm-bmad-puente>` sigue el mismo patrón con `pm-bmad-puente`. Cómo las referencia el paquete:
- **Skills**: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/` (`${CLAUDE_SKILL_DIR}` es la carpeta de cada skill).
- **Agentes**: `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/scripts/` (`${CLAUDE_PLUGIN_ROOT}` es la raíz del plugin).
- **Hook de inicio**: al abrir una sesión en una carpeta con un proyecto (`estado.json` a ≤ 2 niveles), imprime la
  **ruta absoluta** de los scripts (`pm-method · scripts (usar esta ruta, no buscar con find): …/skills/pm-estado-proyecto/scripts/`)
  y la de `bmad.py`. En copia manual o Hermes, donde las variables no se expanden, esa es la ruta a usar.

Todos los scripts aceptan `--proyecto <dir>` y pueden ejecutarse desde cualquier carpeta.

### 7.2 Crear un proyecto e idioma

```bash
python3 <pm-estado-proyecto>/scripts/nuevo_proyecto.py --ruta ./gestion --nombre "Proyecto Faro" \
    --idioma es --enfoque hibrido --ejecutivo "Nombre" --gestor "Nombre"
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion set idioma=en     # cambiar idioma después
```

`--idioma` acepta `es` | `en` y `--enfoque` `predictivo` | `agil` | `hibrido`. El idioma de `estado.json` rige las
respuestas de los scripts; las skills responden en el idioma del usuario. En una sesión, `/pm-method:pm-nuevo` hace lo
mismo y además detecta BMAD.

### 7.3 Umbrales de riesgo y tolerancias

```bash
# Umbrales P×I (por defecto: alto ≥ 15, medio 6–12, bajo ≤ 5)
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion umbrales-riesgo alto=15 medio=6

# Tolerancias por nivel (dimensiones: tiempo, costo, alcance, calidad, beneficios, riesgo, sostenibilidad)
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion tolerancia --nivel proyecto tiempo="±2 semanas" costo="±10 %"
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion tolerancia --nivel etapa costo="±5 %"
```

Las tolerancias son decisiones de gobierno: las de proyecto las fija la capa de negocio/ejecutivo y las de etapa la
junta en cada `autorizar-etapa`. En operación normal las registra `pm-director` tras la decisión humana; el comando
directo sirve para la carga inicial o una corrección. Tiempo y costo son el mínimo obligatorio (sanidad EST-06/07).

### 7.4 Settings recomendados en Claude Code

El listado de descripciones de skills de Claude Code tiene un presupuesto de ≈1 % de la ventana de contexto. Las 32
skills de pm-method que el modelo puede activar suman ≈6.500 caracteres (6.546 según `validar_paquete.py` en la
versión 2.2.0); con BMAD u otros repositorios de skills en la misma sesión el total puede superar el presupuesto (en la
prueba con BMAD 6.12.4 instalado, ≈23.000 caracteres) y el listado se recorta. En ese caso, en `settings.json`:

```json
{
  "skillListingBudgetFraction": 0.02
}
```

La sanidad avisa con **INS-05** cuando las descripciones visibles superan ≈8.000 caracteres. `skillOverrides`
(`on` | `name-only` | `user-invocable-only` | `off`) permite reducir skills de otros orígenes, pero **no aplica a
skills de plugins**.

### 7.5 Orquestador en el hilo principal

El orquestador es el único componente que conversa con el usuario. Dos formas de usarlo:
- Como skill, dentro de cualquier sesión: `/pm-method:pm-orquestador` (`/pm-orquestador` en copia manual o Hermes).
- Como agente principal de toda la sesión:
  ```bash
  claude --agent pm-method:pm-orquestador
  ```
  También puede fijarse con la clave `"agent"` de `settings.json` **[verificar el formato del valor en la documentación
  vigente]**.

---

## 8. Verificación de la instalación

Secuencia final, en este orden. `<raíz>` es la carpeta del paquete: un clon del repositorio o la copia instalada
(`~/.claude/plugins/cache/pm-method/pm-method/<versión>/`, que incluye `scripts/`).

| # | Paso | Comando | Resultado esperado |
|---|---|---|---|
| 1 | Plugin instalado y versión | `claude plugin list` | `pm-method@pm-method` · `Version: 2.2.0` · `Status: enabled` |
| 2 | Manifiestos | `claude plugin validate <raíz>` | `Validation passed` |
| 3 | Python y paquetes | `python3 --version` y `python3 -c "import yaml, docx, openpyxl; print('ok')"` | 3.9 o superior; `ok` |
| 4 | Estructura del paquete | `python3 <raíz>/scripts/validar_paquete.py` | `Skills: 38 (32 invocables por el modelo, listado <n> caracteres) · Agentes: 6` y `OK` |
| 5 | Regresión de punta a punta (requiere PyYAML; trabaja en una carpeta temporal) | `python3 <raíz>/scripts/probar_paquete.py` | `Resultado: <n> OK · 0 FALLO` (138 OK en la corrida del 2026-10-17, versión 2.2.0) |
| 6 | Skills visibles | `/pm-method:pm-ayuda` en una sesión | tabla "qué escribir", catálogo de skills y comandos |
| 7 | Proyecto de prueba | `nuevo_proyecto.py --ruta <tmp>/prueba --nombre "Prueba"` y `estado.py --proyecto <tmp>/prueba siguiente` | carpeta creada y siguiente paso del método |
| 8 | BMAD (si se instaló) | `bmad.py --proyecto ./gestion detectar` | layout `v6`, `version` 6.12.x, `soporte: soportada` |
| 9 | Integraciones declaradas | `estado.py --proyecto ./gestion ver` | bloque `integraciones` con los valores de §6 |
| 10 | Sanidad completa | `/pm-method:pm-sanidad` o `sanidad.py --proyecto ./gestion --informe` | informe en `03-control/reportes/<fecha>-sanidad.md`; 0 ERROR en un proyecto nuevo (código de salida 1 si hay ERROR); AVISO/INFO de instalación según la tabla siguiente |
| 11 | Hook de inicio | abrir una sesión en una carpeta que contenga el proyecto | líneas "pm-method · proyecto '…': fase …; sanidad rápida …" y "pm-method · scripts (usar esta ruta …): <ruta absoluta>" |
| 12 | Hook de protección | pedir en la sesión que edite `estado.json` a mano | rechazo con "pm-method: estado.json se actualiza solo con estado.py…" |

Hallazgos de instalación esperables (familia INS de `sanidad.py`; con `--rapido`, el modo del hook de inicio, solo se
evalúan INS-01 e INS-02):

| Código | Qué controla | Esperado tras una instalación completa |
|---|---|---|
| INS-01 | módulos `yaml`, `docx`, `openpyxl` | ninguno; AVISO con `pip install …` por cada módulo que falte |
| INS-02 | versión de pm-method con la que se creó el proyecto vs la instalada | ninguno en un proyecto nuevo; AVISO en proyectos creados con otra versión (`estado.json` se migra al leerse) |
| INS-03 | skills externas declaradas (`diagramas`, `export=skills-office`), Node y Chrome | INFO "instalada: invocar como …" por skill; AVISO si falta la skill o Node; INFO si archify no encuentra Chrome (en Windows, ver §1.2) |
| INS-04 | skills `pm-*` instaladas más de una vez | ninguno; ver §12 si aparece con la instalación desde GitHub |
| INS-05 | presupuesto del listado de skills (umbral ≈8.000 caracteres) | AVISO habitual con BMAD instalado: aplicar §7.4 |
| INS-06 | posible colisión de disparadores entre una skill externa y una `pm-*` | ninguno o AVISO a revisar (`docs/colisiones.md`) |

---

## 9. Hooks (solo plugin de Claude Code)

| Hook | Disparo | Qué hace |
|---|---|---|
| `PreToolUse` → `hooks/guardian.py` | cada `Write`, `Edit`, `MultiEdit`, `NotebookEdit` y `Bash` | niega (`permissionDecision: "deny"`) con el motivo: modificar `estado.json` sin `estado.py`, `nuevo_proyecto.py` o `bmad.py`; los registros CSV de `03-control/registros/` (los 9 base y, desde 2.2, `estereotipos.csv`, `preferencias.csv`, `raci.csv` y `envios.csv`) sin `registro.py` (o `interesados.py` / `envios.py`, que también figuran entre los scripts permitidos); los derivados de especificación (`spec-index.json`, `requisitos-bmad.csv`, `matriz-trazabilidad-bmad.csv`, `inventario-bmad.json`, `avance-bmad.csv`), las copias congeladas de `00-direccion/historial/` o una instantánea existente de `03-control/fuentes/` — tanto con Write/Edit como con Bash (`sed -i`, `>`/`>>`, `tee`, `cp`/`mv`/`rm`, Python en línea); que un subagente `pm-*` escriba en `_bmad/`, `_bmad-output/` o `.bmad-core/`; y que el hilo principal o un subagente distinto de pm-director ejecute `estado.py puerta|rol|tolerancia|agil|umbrales-riesgo|cumplir-condiciones`, `limite-etapa --excepcion`, `set --forzar` o `aprobar` de nivel superior a gestor |
| `SessionStart` → `hooks/inicio.py` | `startup`, `resume`, `clear`, `compact` | si hay un `estado.json` a ≤ 2 niveles de la carpeta de trabajo (hasta 3 proyectos), agrega al contexto fase, proceso, etapa, el resultado de `sanidad.py --rapido` con los primeros ERROR, una guía de enrutamiento y la ruta absoluta de los scripts |
| `UserPromptSubmit` → `hooks/idioma.py` | cada pedido del usuario | si hay proyecto pm-method y el pedido está en otro idioma que `estado.json.idioma` (español/inglés), agrega al contexto la instrucción de responder en el idioma del pedido; no bloquea nada |

Comportamiento relevante:
- Se ejecutan como `sh "${CLAUDE_PLUGIN_ROOT}/hooks/py.sh" "${CLAUDE_PLUGIN_ROOT}/hooks/…"`; `py.sh` usa el primer
  Python 3.9+ disponible (`python3`, `python`, `py -3`) del shell de los hooks (en Windows, Git Bash: §1.2).
- Protegen rutas con nombres propios de pm-method (`estado.json`, `03-control/registros/*.csv`, derivados,
  `00-direccion/historial/`, `03-control/fuentes/`); en otros repositorios solo intervienen si existen archivos con
  esos nombres o si un subagente `pm-*` intenta un comando reservado.
- El hilo principal **sí** puede escribir en carpetas de BMAD (los flujos propios de BMAD lo necesitan); la
  restricción aplica a los subagentes de pm-method, identificados por `agent_type` en la entrada del hook.
- Ante un error propio, el hook termina sin decidir (no bloquea por fallas internas).

**Cómo prescindir de los hooks.** El paquete no ofrece una opción para desactivarlos por separado. Las vías son:
- deshabilitar el plugin: `claude plugin disable pm-method` (y `claude plugin enable pm-method` para volver);
- o usar la copia manual (§2.2), que no registra hooks.

En ambos casos se pierde la protección automática; la disciplina de escribir solo por scripts queda a cargo de las
skills y de la sanidad.

---

## 10. Actualización y migración

1. Plugin desde GitHub: §0.4. Plugin desde carpeta local: actualizar la carpeta (por ejemplo, `git pull`) y luego
   ```bash
   claude plugin marketplace update pm-method
   claude plugin update pm-method@pm-method       # requiere reiniciar Claude Code
   ```
   En este entorno se probó la actualización de 1.0.0 a 2.0.0 con resultado correcto.
2. Copia manual: volver a copiar `skills/` y `agents/`. Hermes: `git pull` y volver a correr
   `scripts/instalar_hermes.py` (§3.3); luego `/reload-skills`.
3. **Proyectos existentes:** `estado.json` y los registros migran solos al leerse (esquema `estado.json` v2 desde v1;
   `esquema.py` v2 con 9 registros; desde 2.2, 4 registros opcionales más del maestro de interesados que se crean al primer uso, sin migración destructiva). La sanidad avisa la diferencia de versión como **INS-02**.
4. Skills externas y BMAD: §6.1 (actualizar skills y plugins externos) y §4.3 (BMAD).
5. Después de actualizar pm-method o BMAD: correr la sanidad completa en cada proyecto activo y, si BMAD cambió de
   versión, `probar_paquete.py`.

Cambio visible de v1 a v2: desaparece la carpeta `commands/`; los comandos son las skills `pm-ayuda`, `pm-nuevo`,
`pm-estado`, `pm-reporte`, `pm-puerta` y `pm-sync`.

---

## 11. Desinstalación

```bash
claude plugin uninstall pm-method@pm-method
claude plugin marketplace remove pm-method
```

- Copia manual: borrar las carpetas `pm-*` de `~/.claude/skills/` (o `.claude/skills/`) y los seis `pm-*.md` de
  `~/.claude/agents/`.
- Hermes: borrar `~/.hermes/skills/pm-method/` (o la carpeta de `--destino` y su entrada en `external_dirs`); retirar el
  perfil o las personalidades creadas.
- Skills externas: `npx skills remove <skill>` (copias) o `claude plugin uninstall <plugin>@<marketplace>` (plugins).
  Conectores MCP: `claude mcp remove <nombre>`.
- Las carpetas de proyecto no se tocan: son Markdown, CSV y JSON legibles sin el paquete.

---

## 12. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `/pm-method:…` no aparece | plugin no instalado o deshabilitado | `claude plugin list`; `claude plugin enable pm-method`; reiniciar la sesión |
| `claude plugin list` muestra una versión anterior a 2.2.0 | catálogo sin refrescar o versión aún no publicada | §0.4; si persiste, el repositorio publicado no tiene la versión nueva |
| El modelo no activa la skill esperada | listado recortado por presupuesto (BMAD u otros repos) | `"skillListingBudgetFraction": 0.02` (§7.4); sanidad INS-05; invocar la skill por comando |
| Responde una skill de otro repositorio | colisión de disparadores | sanidad INS-06; ajustar la descripción local u ocultar la externa con `skillOverrides`; ver `docs/colisiones.md` |
| Windows: las ediciones o comandos quedan bloqueados por un hook, o no aparece el resumen de inicio | falta Git for Windows, no hay Python 3.9+ en Git Bash (`py.sh` lo avisa) o el clon tiene finales de línea CRLF en `hooks/py.sh` (volver a clonar con el `.gitattributes` vigente) | §1.2 |
| "pm-method: estado.json se actualiza solo con estado.py…" | hook `PreToolUse` | es el comportamiento esperado: usar `estado.py` |
| "… se modifica con registro.py" | edición directa de un registro CSV | `registro.py --proyecto <dir> agregar|actualizar …` |
| "… es un derivado regenerable" | edición de un archivo de `02-planificacion/especificacion/` | regenerar con `bmad.py` o `especificacion.py` |
| "los agentes de gestión no escriben en carpetas de BMAD" | un subagente intentó escribir en BMAD | emitir `bmad.py handoff` y que el equipo BMAD aplique el cambio |
| `bmad.py detectar` no encuentra BMAD | proyecto fuera del árbol del repositorio | `--raiz <repo>` antes del subcomando |
| `npx bmad-method … install` falla al empezar | Node anterior a 20.12.0 | actualizar Node (§1.1) |
| Aviso de versión de BMAD no probada (ESP-07) | BMAD fuera de 4.x / 6.11–6.12 | revisar inventario con el equipo; `probar_paquete.py`; modo degradado |
| ESP-08: carpeta del proyecto dentro de BMAD | proyecto creado en `_bmad-output/` u otra carpeta BMAD | mover la carpeta del proyecto fuera |
| INS-01: falta un módulo | dependencia no instalada | `python3 -m pip install pyyaml python-docx openpyxl` (§5) |
| INS-04: skill duplicada | plugin y copia manual a la vez | dejar una sola instalación |
| INS-04 con la instalación desde GitHub, citando `~/.claude/plugins/marketplaces/pm-method/` y `~/.claude/plugins/cache/pm-method/pm-method/<versión>/` | la sanidad cuenta también el clon del marketplace (comprobado el 2026-10-17 con un `HOME` aislado) | no es una instalación doble: puede ignorarse si esas son las dos únicas rutas **[verificar corrección en una versión posterior de `sanidad.py`]** |
| INS-04 al correr `sanidad.py` desde un clon con el plugin instalado | la sanidad cuenta la carpeta del script que se ejecuta | usar los scripts de la copia instalada (ruta que imprime el hook de inicio, §7.1) |
| No aparece el resumen al abrir la sesión | copia manual, Hermes, o `estado.json` a más de 2 niveles | abrir la sesión cerca del proyecto o correr `/pm-sanidad` |
| Hermes no encuentra los scripts | skills instaladas sin adaptar (`tap add`/`install` o copia directa de `skills/`) | reinstalar con `scripts/instalar_hermes.py` (§3.1) |
| Un subagente "pregunta" en su respuesta | diseño: los subagentes no pueden preguntar | el orquestador presenta las preguntas del bloque de retorno |
| Exportar `.docx`/`.xlsx` falla | faltan `python-docx` u `openpyxl` | instalarlos o usar `integraciones.export=skills-office` |
| `npx skills add` falla al arrancar | Node anterior a 22.20.0 (exigido por `skills@1.7.0`) | actualizar Node (§1.1) |
| INS-03 AVISO: skill externa no encontrada | no instalada, otro nombre o cargada con `--plugin-dir` | instalarla (§6.1); con `--plugin-dir` ignorar el aviso; o volver a `diagramas=mermaid` / `export=scripts` |
| INS-03 INFO "no se encontró Chrome/Chromium" en Windows con Chrome instalado | la sanidad no busca en `Program Files` | definir `ARCHIFY_CHROME` con la ruta de `chrome.exe` (§1.2) |
| archify termina con `browser-check: skipped` | no encuentra Chrome/Chromium | instalar Chrome o `export ARCHIFY_CHROME=<ejecutable>`; el HTML vale como "verificado sin navegador" |
| diagram-design pregunta por la guía de estilo | primera vez, estilo por defecto | responder (personalizar o mantener); sin usuario usa el estilo por defecto |
| La skill de Office no encuentra `docx`/`pptxgenjs` | paquete npm no resoluble por `require` | `npm install docx pptxgenjs` en una carpeta de trabajo fuera del proyecto |
| Un conector MCP no aparece en la sesión | no configurado, no aprobado (`.mcp.json`) o sin autenticar | `claude mcp list`; `claude mcp login <nombre>` o `/mcp`; luego `pm-integraciones` |
| `envios.py enviar … --confirmar` responde "Faltan variables de entorno" y no envía nada | variables de la capa de canales no definidas en el entorno de la sesión | §0.7 (definirlas, abrir terminal nueva, reiniciar la sesión); `envios.py --proyecto ./gestion verificar --modo …`; sin configuración: `--modo eml` |
| `envios.py enviar` termina con código 2 | algún destinatario falló (servidor, webhook o falta de correo en `stakeholders.csv`) | revisar `envios.csv` (estado `fallido`, columna `notas`) y la sanidad STK-07; reintentar: solo se reenvía a quien falta |
