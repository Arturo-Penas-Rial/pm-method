# Entorno Docker opcional · pm-method 2.3.0

Un contenedor Linux aislado con todo lo necesario para **usar** pm-method con Claude Code sobre un proyecto montado y
para **correr las pruebas** del paquete: Claude Code CLI, Python 3 con los paquetes opcionales, Node.js con mermaid-cli
y pptxgenjs, el Chromium que usan los diagramas y las capturas, y git. Es una alternativa a la instalación manual de
[INSTALACION](INSTALACION.md), que **no cambia**: se elige una u otra.

EN: *optional Docker environment: an isolated, hardened Linux container with Claude Code CLI, Python 3, Node.js,
mermaid-cli, pptxgenjs, Playwright's Chromium headless shell and git, pinned and tested. Build with
`docker compose -f docker/compose.yaml build`, run `PROYECTO=/path docker compose -f docker/compose.yaml run --rm pm`,
test with `docker compose -f docker/compose.yaml run --rm pruebas`. The API key or login is passed at run time,
never baked into the image. Cowork does not run inside the container.*

> Convenciones: los comandos se ejecutan desde la raíz del repositorio clonado. **[verificar]** marca lo que no se
> probó. Construcción y pruebas verificadas el 2026-10-20 con Docker Engine 29.8.2 y Compose 5.5.1 en Linux x86_64
> (resultados en §10).

---

## 1. Cuándo conviene

| Situación | Recomendación |
|---|---|
| Uso diario en tu equipo con Claude Code ya instalado | instalación manual ([INSTALACION](INSTALACION.md)) |
| Probar pm-method sin instalar Python, Node, Chromium ni paquetes en tu equipo | **Docker** |
| Aislar lo que ejecuta el agente (comandos de Bash, scripts, `npx`) del resto del sistema | **Docker** |
| Correr las pruebas del paquete en un entorno reproducible (mantenimiento, CI) | **Docker** (`pruebas`) |
| Cowork o la aplicación de escritorio | instalación manual (Cowork no corre dentro del contenedor, §9) |
| Hermes Agent | instalación manual ([INSTALACION §3](INSTALACION.md)); la imagen no lo incluye |

## 2. Qué incluye

| Componente | Versión fijada | De dónde sale |
|---|---|---|
| Sistema base | Ubuntu 26.04 LTS, imagen oficial `ubuntu:26.04` fijada por digest `sha256:c098726d…fb944` | Docker Hub; digest tomado de `docker-library/repo-info` (`repos/ubuntu/remote/26.04.md`) el 2026-10-20 |
| Python | 3.14 (paquete `python3` de Ubuntu) | archivo de Ubuntu |
| Paquetes Python | `pyyaml` 6.0.3, `python-docx` 1.2.0, `openpyxl` 3.1.5, `matplotlib` 3.11.2, `playwright` 1.56.0 y sus transitivas | PyPI, con hash obligatorio (`docker/requirements.txt`) |
| Node.js | 22.22 (paquete `nodejs` de Ubuntu) | archivo de Ubuntu |
| Paquetes Node | `@anthropic-ai/claude-code` 2.1.304, `@mermaid-js/mermaid-cli` 11.16.0, `pptxgenjs` 4.0.1 (con `image-size` 2.0.3 por `overrides`) y `npm` 11.21.1, que aporta `npm` y `npx` para instalar BMAD o skills externas dentro del contenedor (§5.4) | npm, con `npm ci` y `docker/node/package-lock.json` (integridad sha512); `npm audit`: 0 críticos y 0 altos ([SEGURIDAD](SEGURIDAD.md) SEG-13) |
| Chromium | headless shell de Playwright, revisión 1194 (la de `playwright` 1.56.0); lo usan `mmdc` y las capturas de los recorridos E2E | CDN de Playwright (`playwright install --only-shell chromium`) |
| Otras | git, `tini` (proceso init), fuentes DejaVu, Liberation y Noto Color Emoji | archivo de Ubuntu |
| pm-method | el repositorio, en `/opt/pm-method` (solo lectura) | el contexto de construcción (filtrado por `.dockerignore`) |

Claude Code se instala con el paquete npm `@anthropic-ai/claude-code`, el método que la documentación oficial indica
para fijar la versión dentro de un contenedor (`npm install -g @anthropic-ai/claude-code@X.Y.Z` y
`DISABLE_AUTOUPDATER=1`; ver https://code.claude.com/docs/en/devcontainer y https://code.claude.com/docs/en/setup). Aquí
se instala con `npm ci` sobre un lockfile, que además verifica la integridad de cada paquete.

Archivos:

| Archivo | Qué es |
|---|---|
| `docker/Dockerfile` | imagen multietapa: `base` (sistema), `herramientas-python`, `herramientas-node`, `navegadores`, `paquete` (permisos normalizados) y `final` |
| `docker/compose.yaml` | servicios `pm` (trabajo sobre un proyecto montado), `pm-sin-red` (lo mismo, sin red) y `pruebas` (sin red) con el endurecimiento de §7 |
| `docker/requirements.txt` | dependencias Python con versión y hash |
| `docker/node/package.json` · `package-lock.json` | dependencias Node fijadas |
| `docker/puppeteer.json` · `docker/mmdc.sh` | configuración de Chromium para `mmdc` y el envoltorio que la aplica |
| `docker/pm-pruebas.sh` | comando `pm-pruebas` de la imagen: corre todas las pruebas gratuitas |
| `.dockerignore` | excluye `.git`, salidas regenerables del informe y cualquier archivo de credenciales |
| `.github/workflows/docker.yml` | CI: construye la imagen y corre `pruebas` sin red; no publica en registros |

## 3. Requisitos

- Docker Engine 23 o posterior con BuildKit (o Docker Desktop en macOS y Windows) y el plugin Compose v2. Se probó con
  Engine 29.8.2 y Compose 5.5.1. Los límites `deploy.resources` de `compose.yaml` los aplica `docker compose` sin Swarm.
- Disco: ≈ 3 GB para la imagen (≈ 730 MB comprimida) más ≈ 1 GB de caché de construcción. Memoria: 4 GB asignables a
  Docker (el servicio limita a 4 GB y 2 CPU).
- Arquitectura: x86_64 probada. arm64 (Apple Silicon, Graviton) **[verificar]**: los lockfiles incluyen los binarios y
  ruedas de arm64, pero no se construyó la imagen en esa arquitectura.
- Red al construir: Docker Hub, `archive.ubuntu.com` y `security.ubuntu.com`, `pypi.org` y `files.pythonhosted.org`,
  `registry.npmjs.org` y la CDN de Playwright. Si alguna está bloqueada, ver §8.
- Red al usar: `api.anthropic.com` (y, para iniciar sesión, `claude.ai`) para Claude Code; las pruebas no necesitan red.
- Una cuenta de Claude con Claude Code (Pro, Max, Team, Enterprise o Console) o una clave de API.

## 4. Construir

```bash
docker compose -f docker/compose.yaml build pm
# equivalente sin Compose:
docker build -f docker/Dockerfile -t pm-method:2.3.0 .
```

Argumentos opcionales (`--build-arg`):

| Argumento | Por defecto | Para qué |
|---|---|---|
| `UID` · `GID` | `1000` · `1000` | que el usuario `pm` del contenedor coincida con el dueño de la carpeta del proyecto en el host (`id -u`, `id -g`). Si se cambia, ajustar `uid`/`gid` del tmpfs de `/home/pm` en `compose.yaml` |
| `BASE_IMAGE` | `ubuntu:26.04@sha256:c098…` | otra imagen base compatible con Ubuntu 26.04 (por ejemplo, un espejo interno) |
| `VERSION` | `2.3.0` | etiqueta OCI `org.opencontainers.image.version` |

Comprobar la imagen: `docker run --rm pm-method:2.3.0 claude --version` → `2.1.304 (Claude Code)`.

## 5. Usar

### 5.1 Abrir una shell sobre un proyecto

```bash
# Linux, macOS o WSL: el proyecto es la carpeta indicada en PROYECTO (por defecto, la carpeta actual)
PROYECTO=/ruta/al/proyecto docker compose -f /ruta/a/pm-method/docker/compose.yaml run --rm pm
# Windows PowerShell
$env:PROYECTO="C:\ruta\al\proyecto"; docker compose -f C:\ruta\a\pm-method\docker\compose.yaml run --rm pm
```

Dentro: la carpeta del proyecto está en `/trabajo` (lectura y escritura, los cambios se ven en el host), el plugin en
`/opt/pm-method` (solo lectura) y la variable `PM_METHOD_DIR` apunta a él.

### 5.2 Credenciales (nunca en la imagen ni en archivos del repositorio)

Elegir una:

| Opción | Cómo | Dónde queda |
|---|---|---|
| Iniciar sesión con la cuenta | dentro del contenedor, `claude` y seguir el enlace; si el navegador no puede volver al contenedor, copiar el código que muestra y pegarlo en `Paste code here if prompted` | volumen `pm-method_claude-config` (`/home/pm/.claude`, que es `CLAUDE_CONFIG_DIR`); persiste entre ejecuciones |
| Clave de API | `export ANTHROPIC_API_KEY=…` en el host (en `~/.bashrc` o el gestor de secretos) y luego `docker compose … run --rm pm`; Compose la pasa porque `compose.yaml` la declara **sin valor** | solo en la memoria del proceso; la primera vez Claude Code pregunta si usarla |
| Token de larga duración | `claude setup-token` (en el host o en el contenedor) y `export CLAUDE_CODE_OAUTH_TOKEN=…` en el host | igual que la clave |

Con `docker run` en lugar de Compose: `-e ANTHROPIC_API_KEY` (sin `=valor`, toma la del host). Nunca usar
`--build-arg` ni `ENV` para credenciales: quedarían en la imagen. Borrar el inicio de sesión guardado:
`docker volume rm pm-method_claude-config`. Detalle de cada credencial: [INSTALACION §0.7](INSTALACION.md).

### 5.3 Claude Code con pm-method sobre el proyecto montado

```bash
# dentro del contenedor (en /trabajo)
claude --plugin-dir /opt/pm-method                               # sesión interactiva con el plugin
claude --plugin-dir /opt/pm-method -p "/pm-method:pm-ayuda"      # una consulta
# o en un solo paso desde el host
PROYECTO=/ruta/al/proyecto docker compose -f docker/compose.yaml run --rm pm claude --plugin-dir /opt/pm-method
```

Los hooks de pm-method se ejecutan con el Python del contenedor (`/opt/venv`, que tiene `pyyaml`, `python-docx` y
`openpyxl`). Los scripts de las skills también:

```bash
python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta gestion --nombre Demo
```

### 5.4 BMAD, skills externas y git dentro del contenedor

- BMAD (requiere red): `npx bmad-method@6.12.4 install --modules bmm --tools claude-code --yes --user-name "<nombre>"
  --set core.project_name=<proyecto> --no-shims` en `/trabajo`, igual que en [INSTALACION §4](INSTALACION.md). `npx`
  descarga en `~/.npm`, que es temporal (tmpfs): se vuelve a descargar en cada ejecución.
- `git` funciona sobre `/trabajo` (declarado como `safe.directory`). Identidad: pasar `-e GIT_AUTHOR_NAME -e
  GIT_AUTHOR_EMAIL -e GIT_COMMITTER_NAME -e GIT_COMMITTER_EMAIL` o configurarla en el repositorio
  (`git config user.name …`). No montar `~/.ssh` ni archivos de credenciales del host (§7).
- Skills externas y conectores MCP se instalan como en [INSTALACION §6](INSTALACION.md); con `CLAUDE_CONFIG_DIR` en el
  volumen, las de alcance de usuario persisten.

### 5.5 Pruebas del paquete

```bash
docker compose -f docker/compose.yaml run --rm pruebas            # todas, sin red, salida en /tmp del contenedor
# conservar la evidencia en el host (la carpeta debe ser escribible por el UID 1000):
mkdir -p pruebas-docker && docker compose -f docker/compose.yaml run --rm -v "$PWD/pruebas-docker:/salida" pruebas pm-pruebas --salida /salida
```

`pm-pruebas` corre, en orden, y termina con código 1 si alguna falla:

| Paso | Comando dentro del contenedor |
|---|---|
| versión del CLI | `claude --version` |
| manifiestos del plugin | `claude plugin validate /opt/pm-method` (aviso esperado sobre `CLAUDE.md`, ver [PRUEBAS](PRUEBAS.md)) |
| estructura y compatibilidad con Python 3.9 | `python3 /opt/pm-method/scripts/validar_paquete.py` (la imagen no trae Python 3.9: usa el análisis de f-strings de [PRUEBAS §2.4](PRUEBAS.md)); el resumen lo muestra como un paso aparte |
| regresión (incluye la integración cruzada sin recorridos, caso X) | `python3 /opt/pm-method/scripts/probar_paquete.py` |
| recorridos E2E | `python3 /opt/pm-method/scripts/pruebas/guias_e2e/correr.py --salida <DIR>/guias` (con capturas PNG de Playwright) |
| integración cruzada completa | `python3 /opt/pm-method/scripts/pruebas/integracion/correr.py --e2e <DIR>/guias --json <DIR>/integracion.json` (las seis cadenas de [PRUEBAS §2.3](PRUEBAS.md); la sexta usa las imágenes de los recorridos del paso anterior) |
| diagramas | `python3 /opt/pm-method/scripts/validar_mermaid.py --render` |
| diapositivas | `python3 /opt/pm-method/scripts/webinar/generar.py --todos --validar` y `--todos --salida <DIR>/webinar` (HTML y PPTX reales) |
| documentos del webinar | `python3 /opt/pm-method/scripts/webinar/documentos.py --todos --salida <DIR>/webinar-documentos` (guía, guion y ejercicio en HTML, con los diagramas dibujados por el `mmdc` de la imagen; agregado después de la verificación de la imagen del 2026-10-20, todavía sin correr dentro del contenedor `[verificar]`) |

Cada comando también se puede correr suelto: `docker compose -f docker/compose.yaml run --rm pruebas python3
/opt/pm-method/scripts/validar_paquete.py`. `validar_mermaid.py --render` no necesita `--config`: el `mmdc` de la
imagen agrega `/etc/pm-method/puppeteer.json` (Chromium de la imagen y `--no-sandbox`, §7). Las pruebas en vivo
(`scripts/pruebas_vivo/`) consumen tokens y necesitan red y credenciales: se corren desde el servicio `pm`.

## 6. Actualizar

| Qué | Cómo |
|---|---|
| pm-method | `git pull` en el clon y volver a construir (§4) |
| Claude Code | cambiar la versión en `docker/node/package.json`, regenerar el lockfile con `cd docker/node && PUPPETEER_SKIP_DOWNLOAD=1 npm install --package-lock-only --ignore-scripts` y reconstruir. Dentro del contenedor no se actualiza solo: la raíz es de solo lectura y `DISABLE_AUTOUPDATER=1` |
| mermaid-cli, pptxgenjs, npm | igual que Claude Code; después, `cd docker/node && npm audit --package-lock-only` debe quedar sin avisos críticos ni altos ([SEGURIDAD](SEGURIDAD.md) SEG-13). Al cambiar `pptxgenjs`, revisar si el `overrides` de `image-size` sigue haciendo falta |
| Paquetes Python | cambiar las versiones y regenerar `docker/requirements.txt` con las ruedas `manylinux` (x86_64 y aarch64) cp314 o puras y sus hashes de `https://pypi.org/pypi/<paquete>/<versión>/json`; reconstruir. `pip install --require-hashes` rechaza cualquier archivo sin hash |
| Chromium | lo fija la versión de `playwright`: al cambiarla cambia la revisión que descarga `playwright install` |
| Imagen base | tomar el nuevo digest de `ubuntu:26.04` (`docker buildx imagetools inspect ubuntu:26.04` o `docker-library/repo-info`) y actualizar `BASE_IMAGE` en el Dockerfile |
| Limpiar | `docker image prune` (imágenes sin etiqueta) y `docker builder prune` (caché de construcción) |

## 7. Seguridad del contenedor

| Medida | Dónde | Efecto |
|---|---|---|
| Usuario sin privilegios `pm` (UID 1000) | Dockerfile `USER pm` | nada corre como root; además, Claude Code rechaza `--dangerously-skip-permissions` como root |
| Raíz de solo lectura | `read_only: true` | ni el agente ni un script pueden modificar el sistema, el plugin (`/opt/pm-method`) ni las herramientas; solo se escribe en `/trabajo`, en `/tmp` y en `/home/pm` (tmpfs, se borran al salir) y en el volumen de configuración |
| Sin capacidades de Linux | `cap_drop: [ALL]` | sin `chown`, `net_raw`, montajes, etc. |
| Sin escalada de privilegios | `security_opt: no-new-privileges:true` | los binarios setuid no elevan privilegios |
| Límites | `deploy.resources.limits`: 2 CPU, 4 GB, 1024 procesos; `/tmp` 1 GB y `/home/pm` 512 MB | un proceso descontrolado no agota el host |
| Proceso init | `tini` como `ENTRYPOINT` | reenvía señales y recoge procesos huérfanos (Chromium, Node) |
| Sin secretos en capas | credenciales solo al ejecutar (§5.2); el certificado de un proxy, si hace falta al construir, con `--secret` (§8) | `docker history` no muestra ninguno |
| Dependencias verificadas | digest de la imagen base, `pip --require-hashes`, `npm ci` con lockfile, firmas del archivo de Ubuntu | una dependencia alterada hace fallar la construcción |
| `HEALTHCHECK` | `claude --version` y las importaciones de Python | detecta una imagen rota en contenedores de larga duración |
| Red | servicio `pm`: red por defecto de Docker; servicios `pruebas` y `pm-sin-red`: `network_mode: none` | las pruebas se ejecutan sin red |

Notas:

- **Chromium sin su sandbox interno** (`--no-sandbox` en `docker/puppeteer.json`; Playwright hace lo mismo por
  defecto): el perfil seccomp por defecto de Docker no permite el sandbox de Chromium a un usuario sin privilegios. El
  aislamiento lo dan el contenedor y las medidas de la tabla; Chromium solo abre archivos locales generados por los
  scripts (diagramas Mermaid y tableros HTML).
- **Desactivar la red** en el trabajo sobre un proyecto (correr scripts o revisar artefactos sin que nada salga):
  `PROYECTO=/ruta/al/proyecto docker compose -f docker/compose.yaml run --rm pm-sin-red` (mismo servicio que `pm` con
  `network_mode: none`; dentro solo existe la interfaz `lo`). `docker compose run` no tiene opción `--network`; con
  `docker run`: `docker run --rm -it --network none --read-only --tmpfs /tmp --tmpfs /home/pm:uid=1000,gid=1000,exec
  --cap-drop ALL --security-opt no-new-privileges:true -v "$PWD:/trabajo" pm-method:2.3.0`. El servicio `pruebas` ya
  corre sin red. Claude Code no funciona sin red (necesita `api.anthropic.com`).
- **Restringir la salida a dominios concretos** (en lugar de cortarla): el contenedor de referencia de Anthropic usa un
  cortafuegos (`init-firewall.sh`) que requiere las capacidades `NET_ADMIN` y `NET_RAW`; esta imagen no lo incluye para
  mantener `cap_drop: [ALL]`. Usar los controles de red del host o del proxy corporativo
  (https://code.claude.com/docs/en/devcontainer).
- **`--dangerously-skip-permissions`**: posible porque el usuario no es root, pero el agente podría modificar todo
  `/trabajo` y alcanzar la red permitida; la documentación oficial advierte que no impide exfiltrar lo que haya en el
  contenedor, incluidas las credenciales de `~/.claude`. Usarlo solo con repositorios de confianza, nunca con datos de
  proyecto sensibles.
- **No montar** `~/.ssh`, `~/.aws`, `~/.config/gcloud` ni la carpeta de inicio del host. Montar solo la carpeta del
  proyecto.
- Docker Desktop, Podman sin root u otros motores con espacios de nombres de usuario ofrecen aislamiento adicional
  **[verificar]** en cada uno.

## 8. Construir detrás de un proxy o sin acceso a algún registro

El `Dockerfile` admite, sin cambios, tres ajustes para redes corporativas:

| Necesidad | Cómo |
|---|---|
| Proxy HTTP(S) | `--build-arg HTTPS_PROXY=… --build-arg https_proxy=… --build-arg NO_PROXY=… --build-arg no_proxy=…` (argumentos predefinidos de Docker: no quedan en la imagen). Si el proxy escucha en `127.0.0.1` del host, agregar `--network host` |
| Proxy con inspección TLS (certificado propio) | `--secret id=ca_proxy,src=/ruta/al/ca.pem`: `apt`, `pip`, `npm` y la descarga de Playwright confían en él **solo durante la construcción**; no queda en ninguna capa |
| Espejo interno de la imagen base | `--build-arg BASE_IMAGE=<espejo>/ubuntu:26.04@sha256:…` |
| Sin acceso a la CDN de Playwright | `--build-context navegadores=<carpeta>`: reemplaza la etapa `navegadores` por una carpeta que contenga `chromium_headless_shell-1194/` (la **misma revisión** que usa `playwright` 1.56.0, descargada en otra máquina con `PLAYWRIGHT_BROWSERS_PATH=<carpeta> playwright install --only-shell chromium`) |

Si la red no deja descargar la imagen base ni los navegadores, ver §11.1.

## 9. Limitaciones

- **Cowork no corre dentro del contenedor**: es la aplicación de escritorio de Claude; pm-method se instala en ella
  como plugin del modo manual ([INSTALACION §2.3](INSTALACION.md)). Tampoco la extensión de VS Code ni la aplicación
  de escritorio se conectan solas a esta imagen (para eso existen los dev containers; esta imagen es para la terminal).
- **Hermes Agent** no está en la imagen.
- **Sin interfaz gráfica**: los HTML, PNG, DOCX, XLSX y PPTX que se generan en `/trabajo` se abren en el host.
- **`npx` y `~/.npm` son temporales** (tmpfs): BMAD o una skill externa se vuelven a descargar en cada ejecución.
- **Rutas de Windows**: con Docker Desktop, `PROYECTO` acepta `C:\…`; con WSL conviene trabajar dentro del sistema de
  archivos de WSL por rendimiento **[verificar]**.
- **arm64** sin probar (§3).
- **Claude Code en vivo dentro del contenedor** **[verificar]**: se verificaron `claude --version` y `claude plugin
  validate /opt/pm-method`, pero no una sesión con credenciales. Prueba de humo, con una clave o un token en el host:

  ```bash
  export ANTHROPIC_API_KEY=…            # o CLAUDE_CODE_OAUTH_TOKEN=… (claude setup-token)
  mkdir -p /tmp/pm-humo && PROYECTO=/tmp/pm-humo docker compose -f docker/compose.yaml run --rm -T pm \
    claude --plugin-dir /opt/pm-method -p "/pm-method:pm-ayuda" --max-turns 3
  ```

  Resultado esperado: la guía de pm-method en el idioma del pedido, sin errores de hooks. Para una sesión con proyecto,
  crear antes la carpeta con `nuevo_proyecto.py` (§5.3) y preguntar «¿qué sigue?».
- Al iniciar sesión desde el contenedor el navegador no puede volver al `localhost` del contenedor: usar el código
  que muestra la página (§5.2).
- El servicio `pm` usa `${PWD}` como proyecto por defecto; en shells que no definen `PWD` (PowerShell), definir
  `PROYECTO`.

## 10. Verificación registrada

2026-10-20, imagen `pm-method:2.3.0` construida como en §11.1 (Linux x86_64, Docker Engine 29.8.2, Compose 5.5.1):
**2,93 GB** descomprimida (**726 MB** de contenido comprimido). Capas principales: herramientas Node 849 MB (Claude Code,
mermaid-cli con Mermaid, pptxgenjs y npm), paquetes del sistema 521 MB, Chromium headless shell 338 MB, entorno Python
301 MB, pm-method 65 MB (con los informes, el resumen ejecutivo y los mazos del webinar de `docs/`).

**Pruebas dentro del contenedor** (`docker compose -f docker/compose.yaml run --rm pruebas`: sin red, raíz de solo
lectura, sin capacidades, límite de 2 CPU; ≈ 12 min):

| Paso de `pm-pruebas` | Resultado | Tiempo |
|---|---|---|
| `claude --version` | `2.1.304 (Claude Code)` | 0 s |
| `claude plugin validate /opt/pm-method` | pasa con el aviso esperado sobre `CLAUDE.md` | 1 s |
| `validar_paquete.py` | OK (39 skills, 33 invocables, listado de 6.817 caracteres; 6 agentes) | 1 s |
| compatibilidad con Python 3.9 | OK: 53 archivos `.py` sin f-strings incompatibles (análisis propio; la imagen no trae 3.9) | — |
| `probar_paquete.py` (casos A–N, J2, P, S, X e Y) | **216 OK · 0 FALLO** con el Python 3.14 de la imagen | 215 s |
| `guias_e2e/correr.py` | **5/5 OK** (42 gráficos y capturas con Playwright; evidencia igual a la del repositorio salvo la hora local de los archivos de BMAD en E2E-4, porque el contenedor usa UTC) | 353 s |
| `integracion/correr.py --e2e …` (seis cadenas, con las salidas de los recorridos) | **60 OK · 0 FALLO** en 24 eslabones | 46 s |
| `validar_mermaid.py --render` | **OK · 127 bloques Mermaid · 0 error(es)** | 114 s |
| `webinar/generar.py --todos --validar` y `--todos --salida …` | **5/5** sin errores; HTML y PPTX generados | 4 s |

**Contenedor**: usuario `uid=1000(pm)`, `CapEff: 0000000000000000`, `NoNewPrivs: 1`; escribir en `/` y en
`/opt/pm-method` falla con "Read-only file system"; `npx --version` 11.21.1, `node --version` v22.22.1,
`python3 --version` 3.14.4, `mmdc --version` 11.16.0. `npm ls npm` y `npm ls image-size` dentro de la imagen:
`npm@11.21.1` solo como dependencia directa e `image-size@2.0.3 overridden`. `npm audit --package-lock-only` sobre
`docker/node/`: 0 críticos, 0 altos, 0 moderados y 5 bajos ([SEGURIDAD](SEGURIDAD.md) SEG-13).

**Flujo de usuario** (servicio `pm-sin-red` con una carpeta vacía del host montada en `/trabajo`, como `uid=1000(pm)`):
`nuevo_proyecto.py --ruta gestion --nombre "Demo Docker" …`, un riesgo con `registro.py`, presupuesto de cambio de
10.000 y límite delegado de 5.000 con `estado.py presupuesto … --por`, un cambio de 6.000 «aprobado» por la autoridad de
cambio que `registro.py` rechaza («supera el límite de la autoridad de cambio (5.000)», código 1) y que se registra como
`pendiente-decision`, `sanidad.py --informe` (0 ERROR, 1 AVISO REG-06 por el riesgo alto sin respuesta, 1 INFO) y el
informe capturado a PNG con el Chromium de la imagen. En el host, `gestion/`, el informe y el PNG quedaron con dueño
`1000:1000`, el UID del usuario `pm`.

No verificado: una sesión de Claude Code con credenciales dentro del contenedor (§9) y arm64 (§3).

## 11. Solución de problemas

| Síntoma | Causa y solución |
|---|---|
| `failed to resolve reference "docker.io/library/ubuntu…": Forbidden` o tiempo agotado | el registro está bloqueado: usar un espejo con `BASE_IMAGE` (§8) |
| `Could not load certificates from /run/secrets/ca_proxy` | el archivo del `--secret` no existe o no es PEM |
| `apt-get update`: `does not have a Release file` detrás de un proxy | faltan los `--build-arg` de proxy o `--network host` (§8) |
| `playwright install` falla al descargar | sin acceso a la CDN de Playwright: `--build-context navegadores=…` (§8) |
| `ERROR: no se encontró el Chromium headless shell de Playwright` | la carpeta pasada en `--build-context navegadores` no tiene `chromium_headless_shell-*/` en su raíz |
| `Permission denied` al escribir en `/trabajo` | el dueño de la carpeta del host no es el UID 1000: reconstruir con `--build-arg UID=$(id -u) --build-arg GID=$(id -g)` (y ajustar el tmpfs de `/home/pm`) |
| `Read-only file system` al instalar algo con `pip` o `npm -g` | es intencional: agregar la dependencia al `Dockerfile` o a los lockfiles y reconstruir |
| `mmdc`: `Failed to launch the browser process` | memoria compartida insuficiente o límite de procesos: subir `shm_size` o `pids` en `compose.yaml` |
| `claude` pide iniciar sesión en cada ejecución | no se está usando el volumen `claude-config` (con `docker run`, agregar `-v pm-method_claude-config:/home/pm/.claude`) |
| `git`: `detected dubious ownership` en otra ruta que no es `/trabajo` | montar el proyecto en `/trabajo` o `git config --global --add safe.directory <ruta>` |
| Compose: `can't set distinct values on 'pids_limit'…` | versión de Compose antigua o archivo editado: usar solo `deploy.resources.limits.pids` |

### 11.1 Construir sin acceso a los registros de contenedores ni a la CDN de Playwright

Con un proxy que bloquea Docker Hub (y cualquier otro registro) y la CDN de Playwright, pero deja pasar
`archive.ubuntu.com`, `security.ubuntu.com`, `pypi.org`, `files.pythonhosted.org` y `registry.npmjs.org`, la imagen se
construye con una base generada localmente desde el archivo oficial de Ubuntu y con una copia del Chromium:

1. **Base Ubuntu 26.04 con `debootstrap`** (como root, en un Linux con `gpgv` y el llavero `ubuntu-archive-keyring.gpg`):

   ```bash
   curl -fsS https://archive.ubuntu.com/ubuntu/dists/resolute/InRelease -o InRelease
   gpgv --keyring /usr/share/keyrings/ubuntu-archive-keyring.gpg InRelease     # firma del archivo de Ubuntu
   curl -fsS https://archive.ubuntu.com/ubuntu/dists/resolute/main/binary-amd64/Packages.gz -o Packages.gz
   grep " main/binary-amd64/Packages.gz$" InRelease; sha256sum Packages.gz      # el sha256 debe figurar en InRelease
   zcat Packages.gz | awk '/^Package: debootstrap$/{p=1} p&&/^(Filename|SHA256):/{print} p&&/^$/{exit}'
   curl -fsS https://archive.ubuntu.com/ubuntu/<Filename> -o debootstrap.deb && sha256sum debootstrap.deb   # contra el SHA256 anterior
   dpkg-deb -x debootstrap.deb dbs
   DEBOOTSTRAP_DIR=$PWD/dbs/usr/share/debootstrap dbs/usr/sbin/debootstrap --variant=minbase \
     --keyring=/usr/share/keyrings/ubuntu-archive-keyring.gpg resolute rootfs https://archive.ubuntu.com/ubuntu
   ```

   Agregar a `rootfs/etc/apt/sources.list.d/ubuntu.sources` las suites `resolute`, `resolute-updates` y
   `resolute-backports` (`https://archive.ubuntu.com/ubuntu`) y `resolute-security` (`https://security.ubuntu.com/ubuntu`)
   con `Components: main universe restricted multiverse` (la imagen necesita `universe` para `nodejs` y `npm`) e
   importarla: `tar -C rootfs -c . | docker import -c 'CMD ["/bin/bash"]' - pm-method-base-local:26.04`. Es equivalente en
   paquetes a la imagen oficial, no idéntica byte a byte.
2. **Chromium**: una carpeta con `chromium_headless_shell-1194/` (la revisión de `playwright` 1.56.0) descargada en otra
   máquina con `PLAYWRIGHT_BROWSERS_PATH=<carpeta> playwright install --only-shell chromium`. Debe contener el binario
   original `chrome-linux/headless_shell`, no un envoltorio de shell.
3. **Construir** con el proxy, su certificado como secreto y las dos sustituciones:

   ```bash
   docker build --network host -f docker/Dockerfile -t pm-method:2.3.0 \
     --build-arg BASE_IMAGE=pm-method-base-local:26.04 \
     --build-context navegadores=<carpeta con chromium_headless_shell-1194> \
     --secret id=ca_proxy,src=<certificado de la CA del proxy> \
     --build-arg HTTPS_PROXY=$HTTPS_PROXY --build-arg https_proxy=$HTTPS_PROXY \
     --build-arg NO_PROXY=$NO_PROXY --build-arg no_proxy=$NO_PROXY .
   ```

   `--network host` hace falta cuando el proxy escucha en `127.0.0.1` del host. Si `apt-get` corta una descarga
   (`Connection reset by peer`), volver a ejecutar el mismo comando: las etapas ya construidas quedan en caché.
