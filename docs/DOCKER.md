# Entorno Docker opcional · pm-method 2.7.0

Un contenedor Linux aislado con todo lo necesario para **usar** pm-method con Claude Code sobre un proyecto montado y
para **correr las pruebas** del paquete: Claude Code CLI, Python 3 con los paquetes opcionales, Node.js con mermaid-cli
y pptxgenjs, el Chromium que usan los diagramas y las capturas, y git. Es la **referencia técnica** del camino de
instalación con Docker; la guía paso a paso para usuarios (Docker Desktop con WSL2 o Docker Engine dentro de Ubuntu en
Windows, o Linux; obtener, construir, verificar, usar, actualizar y desinstalar) es
**[INSTALACION-DOCKER](INSTALACION-DOCKER.md)**. El otro camino, independiente, es la instalación sobre WSL2 o Linux
([INSTALACION-WSL2](INSTALACION-WSL2.md), [INSTALACION](INSTALACION.md)): se elige uno u otro.

EN: *optional Docker environment: an isolated, hardened Linux container with Claude Code CLI, Python 3, Node.js,
mermaid-cli, pptxgenjs, Playwright's Chromium headless shell and git, pinned and tested. Build with
`docker compose -f docker/compose.yaml build`, run `PROYECTO=/path docker compose -f docker/compose.yaml run --rm pm`,
test with `docker compose -f docker/compose.yaml run --rm pruebas`. The API key or login is passed at run time,
never baked into the image. Cowork does not run inside the container. Optional profile `kb`: pm-kb (cited search, web
UI and read-only MCP) with its PostgreSQL in a segregated `pm-kb-db` container on an internal network.*

> Convenciones: los comandos se ejecutan desde la raíz del repositorio clonado. **[verificar]** marca lo que no se
> probó. Construcción y pruebas verificadas el 2026-10-27 con Docker Engine 29.8.2 y Compose 5.5.1 en Linux x86_64 y,
> con la imagen `pm-method:2.7.0`, el 2026-10-29 (resultados en §10).

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
| Paquetes Node | `@anthropic-ai/claude-code` 2.1.304, `@mermaid-js/mermaid-cli` 11.16.0, `pptxgenjs` 4.0.1 (con `image-size` 2.0.3 por `overrides`) y `npm` 11.21.1, que aporta `npm` y `npx` para instalar BMAD o skills externas dentro del contenedor (§5.4) | npm, con `npm ci` y `docker/node/package-lock.json` (integridad sha512); `npm audit` al 2026-10-27: 0 críticos, 1 alto y 1 moderado dentro de `npm` (`undici` e `ip-address` empaquetados; ninguna versión publicada de `npm` los corrige todavía, aceptados temporalmente con su justificación en [SEGURIDAD](SEGURIDAD.md) SEG-13) y 5 bajos de la cadena de `mermaid-cli` (aceptados) |
| Chromium | headless shell de Playwright, revisión 1194 (la de `playwright` 1.56.0), compilación de Ubuntu 24.04 (`PLAYWRIGHT_HOST_PLATFORM_OVERRIDE`, porque Playwright 1.56 no publica descargas para Ubuntu 26.04; la etapa final verifica con `ldd` que no falten bibliotecas); lo usan `mmdc` y las capturas de los recorridos E2E | CDN de Playwright (`playwright install --only-shell chromium`) |
| Otras | git, `tini` (proceso init), fuentes DejaVu, Liberation y Noto Color Emoji | archivo de Ubuntu |
| diagram-design (skill externa, MIT) | commit `66fa2e7` (2.6.133): solo la carpeta `skills/diagram-design` con `LICENSE` y `THIRD_PARTY_LICENSES.md`, en `/opt/skills-externas/diagram-design`; `PM_DIAGRAM_DESIGN` apunta a ella. No se instala como skill de Claude Code: la usa el caso DD de `probar_paquete.py` para comprobar la compatibilidad (importación de los respaldos Mermaid y `self_check.py --offline`; resultado en §10) | GitHub (`git fetch --depth 1` del commit fijado, comprobado con `git rev-parse`) |
| pm-method | el repositorio, en `/opt/pm-method` (solo lectura) | el contexto de construcción (filtrado por `.dockerignore`) |
| pm-kb (componente opcional, [PM-KB](PM-KB.md)) | sus dependencias de Python (`psycopg` y `psycopg-binary` 3.3.6, `starlette` 1.7.0, `uvicorn` 0.54.0, `markitdown` 0.1.9 con sus extras y las transitivas) en el mismo entorno `/opt/venv`, y el comando `/usr/local/bin/pm-kb` (enlace al lanzador del repositorio, con `PMKB_VENV=/opt/venv`) | PyPI, con hash obligatorio (`pm-kb/requirements.txt`) |

Claude Code se instala con el paquete npm `@anthropic-ai/claude-code`, el método que la documentación oficial indica
para fijar la versión dentro de un contenedor (`npm install -g @anthropic-ai/claude-code@X.Y.Z` y
`DISABLE_AUTOUPDATER=1`; ver https://code.claude.com/docs/en/devcontainer y https://code.claude.com/docs/en/setup). Aquí
se instala con `npm ci` sobre un lockfile, que además verifica la integridad de cada paquete.

Imagen aparte del perfil `kb`, **`pm-kb-db:2.7.0`** (`docker/pm-kb-db.Dockerfile`): la misma base Ubuntu 26.04 fijada
por digest, `postgresql-common`, `tini`, `postgresql-<v>` y `postgresql-<v>-pgvector` del archivo de Ubuntu (18.6 y
0.8.1 al 2026-10-28; la versión la toma de `apt-cache policy postgresql`), sin el clúster `main` del sistema
(`create_main_cluster = false`), usuario `postgres`, punto de entrada `tini -- pm-kb-pg docker` (`pm-kb/db/pg.sh`) y
chequeo de salud `pg_isready` sobre el socket de `/tmp`.

Archivos:

| Archivo | Qué es |
|---|---|
| `docker/Dockerfile` | imagen multietapa: `base` (sistema), `herramientas-python`, `herramientas-node`, `navegadores`, `skills-externas` (diagram-design fijado por commit), `paquete` (permisos normalizados) y `final` |
| `docker/compose.yaml` | servicios `pm` (trabajo sobre un proyecto montado), `pm-sin-red` (lo mismo, sin red) y `pruebas` (sin red) con el endurecimiento de §7; perfil `kb`: `pm-kb-db` y `pm-kb` (§5.6) |
| `docker/pm-kb-db.Dockerfile` | imagen `pm-kb-db` (PostgreSQL y pgvector de Ubuntu para pm-kb) |
| `docker/kb-preparar.sh` | genera las dos contraseñas de la base de pm-kb como secretos en `docker/kb-secretos/` (carpeta 0700, archivos 0644; excluida de git y del contexto de construcción) y la carpeta vacía `docker/kb-sin-proyectos/` |
| `docker/requirements.txt` | dependencias Python con versión y hash |
| `docker/node/package.json` · `package-lock.json` | dependencias Node fijadas |
| `docker/puppeteer.json` · `docker/mmdc.sh` | configuración de Chromium para `mmdc` y el envoltorio que la aplica |
| `docker/pm-pruebas.sh` | comando `pm-pruebas` de la imagen: corre todas las pruebas gratuitas |
| `.dockerignore` | excluye `.git`, salidas regenerables del informe y cualquier archivo de credenciales |
| `.github/workflows/docker.yml` | CI: construye la imagen y corre `pruebas` sin red; no publica en registros |

## 3. Requisitos

- Docker Engine 23 o posterior con BuildKit (o Docker Desktop en macOS y Windows) y el plugin Compose v2. Se probó con
  Engine 29.8.2 y Compose 5.5.1. Los límites `deploy.resources` de `compose.yaml` los aplica `docker compose` sin Swarm.
- Disco: ≈ 3,3 GB para la imagen (≈ 840 MB comprimida) más hasta ≈ 3 GB de caché de construcción que se puede borrar
  (`docker builder prune`; medido el 2026-10-27). Memoria: 4 GB asignables a Docker (el servicio limita a 4 GB y
  2 CPU).
- Arquitectura: x86_64 probada. arm64 (Apple Silicon, Graviton) **[verificar]**: los lockfiles incluyen los binarios y
  ruedas de arm64, pero no se construyó la imagen en esa arquitectura.
- Red al construir: Docker Hub, `archive.ubuntu.com` y `security.ubuntu.com`, `pypi.org` y `files.pythonhosted.org`,
  `registry.npmjs.org` y la CDN de Playwright. Si alguna está bloqueada, ver §8.
- Red al usar: `api.anthropic.com` (y, para iniciar sesión, `claude.ai`) para Claude Code; las pruebas no necesitan red.
- Una cuenta de Claude con Claude Code (Pro, Max, Team, Enterprise o Console) o una clave de API.
- Cómo instalar Docker en Windows (Docker Desktop con el *backend* WSL2, o Docker Engine dentro de Ubuntu) o en Ubuntu,
  paso a paso y con las fuentes oficiales: [INSTALACION-DOCKER §1–§3](INSTALACION-DOCKER.md#1-requisitos-wsl2-y-ubuntu-2404--windows).

## 4. Construir

```bash
docker compose -f docker/compose.yaml build pm
# equivalente sin Compose:
docker build -f docker/Dockerfile -t pm-method:2.7.0 .
```

Argumentos opcionales (`--build-arg`):

| Argumento | Por defecto | Para qué |
|---|---|---|
| `UID` · `GID` | `1000` · `1000` | que el usuario `pm` del contenedor coincida con el dueño de la carpeta del proyecto en el host (`id -u`, `id -g`). Si se cambia, ajustar `uid`/`gid` del tmpfs de `/home/pm` en `compose.yaml` |
| `BASE_IMAGE` | `ubuntu:26.04@sha256:c098…` | otra imagen base compatible con Ubuntu 26.04 (por ejemplo, un espejo interno) |
| `VERSION` | `2.7.0` | etiqueta OCI `org.opencontainers.image.version` |

Comprobar la imagen: `docker run --rm pm-method:2.7.0 claude --version` → `2.1.304 (Claude Code)`.

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
| Clave de API | `read -rsp "Clave de API: " ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY` en la terminal del host (o desde un gestor de secretos) y luego `docker compose … run --rm pm` desde esa terminal; Compose la pasa porque `compose.yaml` la declara **sin valor** | solo en la memoria del proceso; la primera vez Claude Code pregunta si usarla |
| Token de larga duración | `claude setup-token` (en el host o en el contenedor) y `export CLAUDE_CODE_OAUTH_TOKEN=…` en el host | igual que la clave |

La capa de canales de pm-method (`envios.py`) recibe igual, por nombre y sin valor, `PM_SMTP_HOST`, `PM_SMTP_PUERTO`,
`PM_SMTP_TLS`, `PM_SMTP_USUARIO`, `PM_SMTP_CLAVE`, `PM_SMTP_REMITENTE`, `PM_SLACK_WEBHOOK_URL` y `PM_TEAMS_WEBHOOK_URL`
(servicios `pm` y `pm-sin-red`; [INSTALACION-DOCKER
§9.3](INSTALACION-DOCKER.md#93-enviar-comunicaciones-a-interesados-desde-el-contenedor-opcional--ubuntu-y-contenedor)).
`docker compose … config` muestra los valores de esas variables: no compartir su salida.
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

- BMAD (requiere red): `npx --yes bmad-method@6.12.4 install --modules bmm --tools claude-code --yes --user-name "<nombre>"
  --set core.project_name=<proyecto> --no-shims` en `/trabajo`, igual que en [INSTALACION §4](INSTALACION.md). `npx`
  descarga en `~/.npm`, que es temporal (tmpfs): se vuelve a descargar en cada ejecución. Si la red inspecciona HTTPS
  (`SELF_SIGNED_CERT_IN_CHAIN`), abrir el contenedor con el almacén de certificados del host y `NODE_EXTRA_CA_CERTS`
  ([INSTALACION-DOCKER §12.3](INSTALACION-DOCKER.md#123-red-corporativa-proxy-y-certificados), punto 3).
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
| documentos del webinar | `python3 /opt/pm-method/scripts/webinar/documentos.py --todos --salida <DIR>/webinar-documentos` (guía, guion y ejercicio en HTML, con los diagramas dibujados por el `mmdc` de la imagen) |

Cada comando también se puede correr suelto: `docker compose -f docker/compose.yaml run --rm pruebas python3
/opt/pm-method/scripts/validar_paquete.py`. `validar_mermaid.py --render` no necesita `--config`: el `mmdc` de la
imagen agrega `/etc/pm-method/puppeteer.json` (Chromium de la imagen y `--no-sandbox`, §7). Las pruebas en vivo
(`scripts/pruebas_vivo/`) consumen tokens y necesitan red y credenciales: se corren desde el servicio `pm`.

### 5.6 pm-kb (perfil `kb`)

Paso a paso: [INSTALACION-DOCKER §8](INSTALACION-DOCKER.md#8-pm-kb-en-docker-opcional); referencia: [PM-KB](PM-KB.md).

| Servicio | Imagen | Red | Datos y secretos | Endurecimiento y límites |
|---|---|---|---|---|
| `pm-kb-db` | `pm-kb-db:2.7.0` | solo `kb-interna` (`internal: true`: sin salida ni DNS externo); sin puertos publicados | volumen `pm-kb-datos` en `/var/lib/postgresql/data`; secretos `pmkb_admin_clave` y `pmkb_lector_clave` | raíz de solo lectura, `cap_drop: [ALL]`, `no-new-privileges`, usuario `postgres`; 2 CPU, 1 GB, 256 procesos; tmpfs `/tmp` (64 MB) y `/run/postgresql`; `restart: unless-stopped` |
| `pm-kb` | `pm-method:2.7.0` | `default` y `kb-interna`; publica solo `127.0.0.1:8765` | carpetas a indexar desde `${PROYECTOS}` en `/proyectos`, **solo lectura** (por defecto `docker/kb-sin-proyectos`); los mismos dos secretos | el endurecimiento de §7 (2 CPU, 4 GB); espera a que `pm-kb-db` esté sano; corre `pm-kb base crear` y `pm-kb servir --host 0.0.0.0 --puerto 8765`; chequeo de salud `GET /salud` |
| `pm-kb-vigilar` | `pm-method:2.7.0` | solo `kb-interna`; sin puertos publicados | `${PROYECTOS}` en `/proyectos`, **solo lectura**; solo el secreto `pmkb_admin_clave` (rol `pmkb`, dueño del índice: es el que indexa) | el endurecimiento de §7; espera a que `pm-kb-db` esté sano; corre `pm-kb base crear` y un `pm-kb vigilar --proyecto <p> --ruta /proyectos/<p> --cada <s>` por proyecto de `KB_VIGILAR` (`KB_VIGILAR_CADA`, 10 s por defecto); sale con código 1 si falta `KB_VIGILAR` o termina un `vigilar`; sin chequeo de salud (no hay puerto); `restart: unless-stopped` |

- **Por qué una base segregada**: el índice tiene datos de varios proyectos y tokens; en su propio contenedor y en una
  red interna, ni el contenedor `pm` (donde corre el agente) ni internet la alcanzan. Verificado: desde `pm`,
  `http://pm-kb:8765/salud` responde y `pm-kb-db` no se resuelve.
- **Contraseñas**: solo como secretos de Docker (`/run/secrets/…`); `pm-kb-db` las aplica a los roles `pmkb` (dueño del
  índice, sin superusuario) y `pmkb_lector` (solo lectura, con RLS) en cada arranque, así que se rotan cambiando el
  archivo y reiniciando ([INSTALACION-DOCKER §8.8](INSTALACION-DOCKER.md#88-respaldo-contraseñas-y-apagar--ubuntu)).
  `pg_hba.conf` admite por la red solo a esos dos roles sobre la base `pmkb` con `scram-sha-256`; el superusuario
  `postgres` entra solo por el socket dentro del contenedor.
- **Variables** del servicio `pm-kb`: `PMKB_DSN` y `PMKB_DSN_LECTOR` (`host=pm-kb-db dbname=pmkb user=…`), los archivos
  de las contraseñas, `PMKB_ORIGENES=http://localhost:8765,http://127.0.0.1:8765` (las direcciones desde las que el
  portal acepta «Actualizar ahora», `/mcp` con `Origin` y el canje de un enlace compartido; la primera arma la URL de
  `pm-kb compartir crear`: detrás de un proxy con TLS, poner primero su `https://…`) y, desde el host si existen,
  `PMKB_EMBED_URL`, `PMKB_EMBED_TIPO`, `PMKB_EMBED_MODELO`, `PMKB_RERANK_URL`, `PMKB_LLM_TIPO`, `PMKB_LLM_URL` y
  `PMKB_LLM_MODELO`; la clave del modelo, solo como `PMKB_CLAVE_MODELO` (declarada sin valor, con
  `PMKB_LLM_CLAVE_VAR=PMKB_CLAVE_MODELO` fijo), para que no llegue al servicio `pm`. `extra_hosts` define
  `host.docker.internal` (`host-gateway`) para un servidor de modelos en el equipo anfitrión ([PM-KB
  §8](PM-KB.md#8-configuración); [INSTALACION-DOCKER
  §8.9](INSTALACION-DOCKER.md#89-modelos-opcionales-respuesta-vectores-y-re-ranqueo--ubuntu)).
- **Vigilancia** (`pm-kb-vigilar`, [INSTALACION-DOCKER §8.10](INSTALACION-DOCKER.md#810-mantener-el-índice-al-día-servicio-pm-kb-vigilar--ubuntu)):
  se levanta aparte, `KB_VIGILAR="p1 p2" PROYECTOS=… docker compose -f docker/compose.yaml --profile kb up -d
  pm-kb-vigilar`; cada nombre es una carpeta de `/proyectos` y el nombre del proyecto en el índice. Recibe solo
  `PMKB_DSN`, el archivo de la contraseña del dueño y, si existen en el host, `PMKB_EMBED_URL`, `PMKB_EMBED_TIPO` y
  `PMKB_EMBED_MODELO` (para reutilizar los vectores calculados); ni la clave del modelo ni la red `default`, así que un
  servidor de vectores fuera de `kb-interna` no se alcanza desde este servicio.
- Comandos: `docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb …` (`verificar`, `indexar`, `token
  crear`, `buscar`, `tablero`, `enlaces`, `compartir crear|listar|revocar`…; portal y enlaces compartidos:
  [INSTALACION-DOCKER §8.11](INSTALACION-DOCKER.md#811-portal-tableros-y-enlaces-compartidos--ubuntu)). «Actualizar
  ahora» escribe el tablero solo en el índice, con la conexión del dueño (`PMKB_DSN`) que el servicio ya tiene: los
  proyectos siguen montados en solo lectura. `pm-kb db …` no aplica: la base la maneja Docker. `… --profile kb down` conserva el volumen; `down
  -v` borra todos los volúmenes del archivo, incluido `claude-config`.

## 6. Actualizar

| Qué | Cómo |
|---|---|
| pm-method | `git pull` en el clon y volver a construir (§4) |
| Claude Code | cambiar la versión en `docker/node/package.json`, regenerar el lockfile con `cd docker/node && PUPPETEER_SKIP_DOWNLOAD=1 npm install --package-lock-only --ignore-scripts` y reconstruir. Dentro del contenedor no se actualiza solo: la raíz es de solo lectura y `DISABLE_AUTOUPDATER=1` |
| mermaid-cli, pptxgenjs, npm | igual que Claude Code; después, `cd docker/node && npm audit --package-lock-only` debe quedar sin avisos críticos ni altos, salvo los aceptados con su justificación en [SEGURIDAD](SEGURIDAD.md) SEG-13 (hoy, `undici` empaquetado en `npm`; al subir `npm`, comprobar si una versión nueva los corrige con `npm view npm time` y el lockfile regenerado). Al cambiar `pptxgenjs`, revisar si el `overrides` de `image-size` sigue haciendo falta |
| Paquetes Python | cambiar las versiones y regenerar `docker/requirements.txt` con las ruedas `manylinux` (x86_64 y aarch64) cp314 o puras y sus hashes de `https://pypi.org/pypi/<paquete>/<versión>/json`; reconstruir. `pip install --require-hashes` rechaza cualquier archivo sin hash |
| Dependencias de pm-kb | `pm-kb/requirements.txt` se regenera con `python3 pm-kb/regenerar_requisitos.py congelado.txt > pm-kb/requirements.txt`, donde `congelado.txt` es la lista `paquete==versión` completa (el `pip freeze` de un entorno limpio con las directas instaladas y con las versiones comunes iguales a las de `docker/requirements.txt`); toma ruedas de CPython 3.12 y 3.14 en `manylinux` x86_64 y aarch64, o puras, y falla si falta alguna. Sirve a los dos caminos (WSL2 y la imagen); reconstruir y repetir `pm-kb verificar` |
| Imagen `pm-kb-db` | sigue a la base de la imagen principal: al cambiar el digest de `BASE_IMAGE` en el `Dockerfile`, cambiarlo también en `docker/pm-kb-db.Dockerfile`; PostgreSQL y pgvector salen de `apt` al construir. Si sube la versión mayor de PostgreSQL, el volumen `pm-kb-datos` no sirve: `--profile kb down`, `docker volume rm pm-method_pm-kb-datos`, levantar e indexar de nuevo ([PM-KB §14](PM-KB.md#14-operación)) |
| Chromium | lo fija la versión de `playwright`: al cambiarla cambia la revisión que descarga `playwright install` |
| diagram-design | cambiar `DIAGRAM_DESIGN_COMMIT` en el Dockerfile por el commit completo verificado (leer `LICENSE` y los scripts `mermaid_extract.py` y `self_check.py` antes), anotarlo en [DEPENDENCIAS](DEPENDENCIAS.md) §4.2 y reconstruir; el caso DD de `probar_paquete.py` debe seguir en 0 FALLO |
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
| Red | servicio `pm`: red por defecto de Docker; servicios `pruebas` y `pm-sin-red`: `network_mode: none`; perfil `kb`: `pm-kb-db` y `pm-kb-vigilar` solo en `kb-interna` (`internal: true`) | las pruebas se ejecutan sin red; la base de pm-kb no tiene salida y solo la alcanzan `pm-kb` y `pm-kb-vigilar`, que tampoco tiene salida |
| Secretos de pm-kb | `docker/kb-secretos/` (0700) montados con `secrets:`; excluidos por `.gitignore` y `.dockerignore` | las contraseñas no están en la imagen, en `compose.yaml`, en variables ni en git |
| Publicación de pm-kb | `127.0.0.1:8765` (no todas las interfaces); token por persona; proyectos montados en solo lectura | la web y el MCP no quedan expuestos a la red; el servicio no puede modificar los proyectos ([SEGURIDAD §14](SEGURIDAD.md#14-pm-kb-índice-de-conocimiento-2026-10-28)) |

Notas:

- **Chromium sin su sandbox interno** (`--no-sandbox` en `docker/puppeteer.json`; Playwright hace lo mismo por
  defecto): el perfil seccomp por defecto de Docker no permite el sandbox de Chromium a un usuario sin privilegios. El
  aislamiento lo dan el contenedor y las medidas de la tabla; Chromium solo abre archivos locales generados por los
  scripts (diagramas Mermaid y tableros HTML).
- **Desactivar la red** en el trabajo sobre un proyecto (correr scripts o revisar artefactos sin que nada salga):
  `PROYECTO=/ruta/al/proyecto docker compose -f docker/compose.yaml run --rm pm-sin-red` (mismo servicio que `pm` con
  `network_mode: none`; dentro solo existe la interfaz `lo`). `docker compose run` no tiene opción `--network`; con
  `docker run`: `docker run --rm -it --network none --read-only --tmpfs /tmp --tmpfs /home/pm:uid=1000,gid=1000,exec
  --cap-drop ALL --security-opt no-new-privileges:true -v "$PWD:/trabajo" pm-method:2.7.0`. El servicio `pruebas` ya
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

La imagen `pm-kb-db` acepta lo mismo (`BASE_IMAGE`, `--secret id=ca_proxy,…` y los argumentos de proxy): `docker build
-f docker/pm-kb-db.Dockerfile -t pm-kb-db:2.7.0 …` con las mismas opciones. Si la red no deja descargar la imagen base
ni los navegadores, ver §11.1 (la base local sirve para las dos imágenes).

## 9. Limitaciones

- **Cowork no corre dentro del contenedor**: es la aplicación de escritorio de Claude; pm-method se instala en ella
  como plugin del modo manual ([INSTALACION §2.3](INSTALACION.md)). Tampoco la extensión de VS Code ni la aplicación
  de escritorio se conectan solas a esta imagen (para eso existen los dev containers; esta imagen es para la terminal).
- **Hermes Agent** no está en la imagen.
- **Sin interfaz gráfica**: los HTML, PNG, DOCX, XLSX y PPTX que se generan en `/trabajo` se abren en el host.
- **`npx` y `~/.npm` son temporales** (tmpfs): BMAD o una skill externa se vuelven a descargar en cada ejecución.
- **Rutas de Windows**: con WSL2, el proyecto va en el sistema de archivos de Linux (`~`), no en `/mnt/c`: lo recomienda
  la documentación de Docker ("WSL 2 best practices") por rendimiento y para que se detecten los cambios de archivos.
  Con Docker Desktop, `PROYECTO` con una ruta `C:\…` desde PowerShell **[verificar]**.
- **arm64** sin probar (§3); tampoco `pm-kb-db` en arm64.
- **pm-kb**: la web y el MCP desde Windows o desde Ubuntu fuera de los contenedores (`127.0.0.1:8765`) y "Preguntar"
  con un modelo **[verificar]** ([PM-KB §15](PM-KB.md#15-limitaciones-y-verificar)).
- **Claude Code en vivo dentro del contenedor** **[verificar]**: se verificaron `claude --version`, `claude plugin
  validate /opt/pm-method`, `claude auth status` y `claude -p` sin credenciales (`Not logged in · Please run /login`),
  pero no una sesión con credenciales. Prueba de humo, con una clave o un token en el host:

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

2026-10-29, imagen `pm-method:2.7.0`, construida como en §11.1 (base Ubuntu 26.04 local `pm-method-base-local:26.04`;
Chromium headless shell con `--build-context navegadores`; Linux x86_64): **3,33 GB** descomprimida (**845 MB** de
contenido comprimido; etiqueta `org.opencontainers.image.version` = `2.7.0`). La etapa `skills-externas` comprueba con
`git rev-parse` que diagram-design quede en el commit `66fa2e7c36ff…`; sin esa coincidencia la construcción falla.
Capas principales (`docker history`): herramientas Node 849 MB (Claude Code, mermaid-cli con Mermaid, pptxgenjs y
npm), paquetes del sistema 521 MB, entorno Python 518 MB (con las dependencias de pm-kb), Chromium headless shell
338 MB, base 127 MB, pm-method 120 MB (con los informes, el resumen ejecutivo y los mazos y documentos del webinar de
`docs/`) y diagram-design 6 MB. Imagen de la base de pm-kb: `pm-kb-db:2.7.0`, **409 MB** (102 MB de contenido).

**Pruebas dentro del contenedor** (`docker compose -f docker/compose.yaml run --rm pruebas`, el bloque de
[INSTALACION-DOCKER](INSTALACION-DOCKER.md) §6.2: sin red, raíz de solo lectura, sin capacidades, límite de 2 CPU;
≈ 35 min): `Resultado: todas las pruebas OK` en **dos corridas seguidas** con el mismo resultado (tiempos de la primera y de la segunda).

| Paso de `pm-pruebas` | Resultado | Tiempo |
|---|---|---|
| `claude --version` | `2.1.304 (Claude Code)` | 0 s |
| `claude plugin validate /opt/pm-method` | pasa con el aviso esperado sobre `CLAUDE.md` | 0 s |
| `validar_paquete.py` | OK (39 skills, 33 invocables, listado de 6.966 caracteres; 6 agentes) | 2 s |
| compatibilidad con Python 3.9 | OK: 94 archivos `.py` sin f-strings incompatibles (análisis propio; la imagen no trae 3.9) | — |
| `probar_paquete.py` (todos los casos) | **561 OK · 0 FALLO · 0 omitidas** con el Python 3.14 de la imagen; incluye el **caso DD completo con `PM_DIAGRAM_DESIGN`** (las tres comprobaciones de compatibilidad que fuera de la imagen se omiten) | 762 s · 714 s |
| `guias_e2e/correr.py` | **5/5 OK**; el contenedor de pruebas no tiene pm-kb, así que sus pasos (E2E-1 paso 16, E2E-3 paso 15 en su parte de pm-kb, E2E-4 paso 9c) se omiten con «OMITIDO pm-kb» | 493 s · 516 s |
| `integracion/correr.py --e2e …` (seis cadenas, con las salidas de los recorridos) | **122 OK · 0 FALLO** en 40 eslabones | 113 s · 114 s |
| `variantes/correr.py` (niveles robustez, caminos, matriz, integraciones, contratos y hermes; sin Python 3.9 ni el ZIP de 2.6.1 en la imagen, omisiones declaradas) | **296 OK · 0 FALLO · 0 trazas · 0 omisiones fuera del manifiesto** | 367 s · 377 s |
| `validar_mermaid.py --render` | **OK · 131 bloques Mermaid · 0 error(es)** | 141 s · 149 s |
| `webinar/generar.py --todos --validar` y `--todos --salida …` | **5/5** sin errores; HTML y PPTX generados | 4 s |
| `webinar/documentos.py --todos --salida …` | **5/5** sin errores; 15 HTML e índice, con los diagramas dibujados por el `mmdc` de la imagen | 18 s · 19 s |

**Contenedor** (2026-10-30, `pm-method:2.7.0`): usuario `uid=1000(pm)`, `CapEff: 0000000000000000`, `NoNewPrivs: 1`,
solo la interfaz `lo`; escribir en `/` y en `/opt/pm-method` falla con "Read-only file system"; `npx --version` 11.21.1,
`node --version` v22.22.1, `python3 --version` 3.14.4, `mmdc --version` 11.16.0, `playwright --version` 1.56.0;
`PM_DIAGRAM_DESIGN` = `/opt/skills-externas/diagram-design/skills/diagram-design`. `npm ls npm image-size` en `/opt/node-tools`:
`npm@11.21.1` como dependencia directa e `image-size@2.0.3 overridden`. `npm audit --package-lock-only` sobre
`docker/node/` (2026-10-27): 0 críticos, **1 alto y 1 moderado** en `undici` 6.29.0 e `ip-address` 10.7.2, que `npm`
11.21.1 trae empaquetados, y los 5 bajos de la cadena de `mermaid-cli`. Ninguna versión publicada de `npm` los corrige
todavía (las últimas, 11.21.1 y 12.2.1, dan el mismo resultado con el lockfile regenerado): se mantiene `npm` 11.21.1 y
los dos avisos quedan aceptados temporalmente, con su justificación, en [SEGURIDAD](SEGURIDAD.md) SEG-13; `npm` solo se
usa dentro del contenedor para `npx` (BMAD y skills externas).

**Flujo de usuario**: los bloques de comandos de [INSTALACION-DOCKER](INSTALACION-DOCKER.md) se ejecutaron tal cual
como un usuario sin privilegios con UID 1000 en el grupo `docker` (detalle y versión de la imagen de cada paso en su §14): contenedor sobre una carpeta del
host (`/trabajo`, `uid=1000(pm)`), atajo `pm-docker`, proyecto creado con `nuevo_proyecto.py` (sanidad `0 ERROR · 0
AVISO · 1 INFO`; en el host, `estado.json` con el usuario del host como dueño), servicio `pm-sin-red` (solo `lo`),
`claude auth status` (`"loggedIn": false`, `"configDirectory": "/home/pm/.claude"`, volumen `pm-method_claude-config`),
clave de API ficticia cargada solo en memoria (llega al contenedor y no queda en ningún archivo del host ni del
volumen), `claude --plugin-dir /opt/pm-method -p "/pm-method:pm-ayuda"` sin credenciales (`Not logged in · Please run
/login`), BMAD 6.12.4 con `npx` dentro del contenedor (en la red de prueba, que inspecciona HTTPS, `npx` falla con
`SELF_SIGNED_CERT_IN_CHAIN` y funciona prestando el almacén de certificados del host con `NODE_EXTRA_CA_CERTS`:
`_bmad/`, 29 skills `bmad-*`, `detectar` → `v6`, `6.12.4`, `soportada`), `claude` interactivo (sin el certificado,
`Failed to connect to api.anthropic.com: SELF_SIGNED_CERT_IN_CHAIN`; con él, el error de certificado desaparece y la
red de prueba no resuelve `platform.claude.com`), `validar_mermaid.py --render` y la desinstalación. `docker compose … build pm` se detiene, en esta red, al resolver la imagen base en Docker Hub
(`Forbidden`), como se esperaba.

**pm-kb (perfil `kb`)**, 2026-10-30: imágenes `pm-kb-db:2.7.0` (409 MB; PostgreSQL 18.6, pgvector 0.8.1 y `tini` 0.19.0
de Ubuntu 26.04) y `pm-method:2.7.0` (con las dependencias de pm-kb), construidas sobre la base local de §11.1.
`docker compose -f docker/compose.yaml --profile kb up -d pm-kb` arranca `pm-kb-db`, espera a que esté sano y arranca
`pm-kb`; los dos quedan `(healthy)`. `… exec pm-kb pm-kb verificar`: 14 OK (módulos, PostgreSQL 18, pgvector, búsqueda
en español, relaciones, conexión de `pmkb_lector`, RLS por proyecto y circulación, el lector no lee tokens ni escribe).
`… exec pm-kb pm-kb indexar --proyecto portal-socios --ruta /proyectos/portal-socios` (caso E2E-1): 444 unidades (399
vigentes), 65 documentos, 511 relaciones, 115 entradas de historia; `token crear` (vence a los 90 días; `--dias 400` se
rechaza), ingreso por el formulario de la web en `http://127.0.0.1:8765` (303) y `/api/estado` con el token; `base
estado` informa el esquema 4 (migrado desde el volumen anterior al arrancar). Portal: `pm-kb tablero` y `enlaces`;
`compartir crear`, canje con el origen configurado (200; otro origen, 403), sesión compartida con el tablero (200) y sin
búsqueda (403), `compartir listar` con el uso y `revocar` que corta la sesión (401). `pm-kb-vigilar` (con
`KB_VIGILAR=portal-socios`): `uid=1000(pm)`, `/proyectos` de solo lectura, reindexa y publica el tablero al arrancar y
ante un archivo nuevo. Servicio `pm-kb`: `uid=1000(pm)`, `/proyectos` de solo lectura (`Read-only file system`). Desde el contenedor
`pm`: `http://pm-kb:8765/salud` → `ok`, `pm-kb-db` sin resolución de nombre y 9 herramientas MCP. Rotación (2026-10-29, imágenes 2.6.2): secreto del lector sobrescrito,
`restart pm-kb-db pm-kb` y `verificar` sin fallos. `--profile kb down` conserva el volumen `pm-method_pm-kb-datos`;
`down -v` (probado con otro nombre de proyecto de Compose) borra también el volumen de `claude-config`.

No verificado: una sesión de Claude Code con credenciales dentro del contenedor (§9), Docker Desktop y todo lo del lado
de Windows, la instalación de Docker Engine desde `download.docker.com` (bloqueado en la red de prueba),
`docker compose … build pm` con acceso a Docker Hub, arm64 (§3) y la descarga real de la etapa `descarga-navegadores`
con acceso a la CDN de Playwright.

## 11. Solución de problemas

| Síntoma | Causa y solución |
|---|---|
| `failed to resolve reference "docker.io/library/ubuntu…": Forbidden` o tiempo agotado | el registro está bloqueado: usar un espejo con `BASE_IMAGE` (§8) |
| `Could not load certificates from /run/secrets/ca_proxy` | el archivo del `--secret` no existe o no es PEM |
| `apt-get update` o `pip`: `certificate verify failed` con el `--secret` puesto | el proxy inspecciona solo algunos sitios y para el resto deja pasar el certificado real, que el archivo del secreto no cubre: pasar un archivo con la CA del proxy **más** las raíces públicas, por ejemplo `cat <ca del proxy> "$(python3 -c 'import certifi; print(certifi.where())')" > ca-combinada.pem` y `--secret id=ca_proxy,src=ca-combinada.pem` (verificado el 2026-10-29 en la red de prueba; requiere el paquete `certifi` de Python, o usar el almacén de certificados del sistema) |
| `apt-get update`: `does not have a Release file` detrás de un proxy | faltan los `--build-arg` de proxy o `--network host` (§8) |
| `playwright install` falla al descargar | sin acceso a la CDN de Playwright: `--build-context navegadores=…` (§8) |
| `playwright install` termina con error sin descargar nada | Playwright no reconoce la versión de Ubuntu de la imagen base y no tiene URL de descarga: el Dockerfile fija `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-<arq>`; si cambiás `BASE_IMAGE` o la versión de `playwright`, revisá ese valor (`playwright install --dry-run --only-shell chromium` muestra la URL que usaría) |
| `ERROR: no se encontró el Chromium headless shell de Playwright` | la carpeta pasada en `--build-context navegadores` no tiene `chromium_headless_shell-*/` en su raíz |
| `Permission denied` al escribir en `/trabajo` | el dueño de la carpeta del host no es el UID 1000: reconstruir con `--build-arg UID=$(id -u) --build-arg GID=$(id -g)` (y ajustar el tmpfs de `/home/pm`) |
| `Read-only file system` al instalar algo con `pip` o `npm -g` | es intencional: agregar la dependencia al `Dockerfile` o a los lockfiles y reconstruir |
| `mmdc`: `Failed to launch the browser process` | memoria compartida insuficiente o límite de procesos: subir `shm_size` o `pids` en `compose.yaml` |
| `claude` pide iniciar sesión en cada ejecución | no se está usando el volumen `claude-config` (con `docker run`, agregar `-v pm-method_claude-config:/home/pm/.claude`) |
| `git`: `detected dubious ownership` en otra ruta que no es `/trabajo` | montar el proyecto en `/trabajo` o `git config --global --add safe.directory <ruta>` |
| Compose: `can't set distinct values on 'pids_limit'…` | versión de Compose antigua o archivo editado: usar solo `deploy.resources.limits.pids` |
| pm-kb: `pm-kb-db: falta el secreto /run/secrets/pmkb_admin_clave …` (o Compose no encuentra `docker/kb-secretos/…`) | faltan las contraseñas: `bash docker/kb-preparar.sh` y volver a levantar el perfil `kb` |
| pm-kb: `pm-kb-db` no queda sano (chequeo `pg_isready -h /tmp -d pmkb`) y `pm-kb` no arranca | `docker compose -f docker/compose.yaml --profile kb logs pm-kb-db`: `initdb` o el arranque fallaron (por ejemplo, un volumen `pm-kb-datos` de otra versión mayor de PostgreSQL: §6) |
| pm-kb: el puerto `127.0.0.1:8765` ya está ocupado | otro `pm-kb servir` o programa en ese puerto: cerrarlo, o cambiar el puerto del host en `ports` del servicio `pm-kb` (`127.0.0.1:<otro>:8765`) y agregar `http://127.0.0.1:<otro>` a `PMKB_ORIGENES` |

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
   con `Components: main universe restricted multiverse` (la imagen necesita `universe` para `nodejs` y `npm`), quitar los
   paquetes que dejó `debootstrap` y las listas de `apt` (`rm -rf rootfs/var/cache/apt/archives/*.deb
   rootfs/var/lib/apt/lists/*`; la imagen oficial no los trae) e importarla: `tar -C rootfs -c . | docker import -c
   'CMD ["/bin/bash"]' - pm-method-base-local:26.04`. Es equivalente en paquetes a la imagen oficial, no idéntica byte a
   byte.
2. **Chromium**: una carpeta con `chromium_headless_shell-1194/` (la revisión de `playwright` 1.56.0) descargada en otra
   máquina con `PLAYWRIGHT_BROWSERS_PATH=<carpeta> playwright install --only-shell chromium`. Debe contener el binario
   original `chrome-linux/headless_shell`, no un envoltorio de shell.
3. **Construir** con el proxy, su certificado como secreto y las dos sustituciones:

   ```bash
   docker build --network host -f docker/Dockerfile -t pm-method:2.7.0 \
     --build-arg BASE_IMAGE=pm-method-base-local:26.04 \
     --build-context navegadores=<carpeta con chromium_headless_shell-1194> \
     --secret id=ca_proxy,src=<certificado de la CA del proxy> \
     --build-arg HTTPS_PROXY=$HTTPS_PROXY --build-arg https_proxy=$HTTPS_PROXY \
     --build-arg NO_PROXY=$NO_PROXY --build-arg no_proxy=$NO_PROXY .
   ```

   `--network host` hace falta cuando el proxy escucha en `127.0.0.1` del host. Si `apt-get` corta una descarga
   (`Connection reset by peer`), volver a ejecutar el mismo comando: las etapas ya construidas quedan en caché.
