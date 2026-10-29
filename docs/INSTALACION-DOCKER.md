# Instalación con Docker · pm-method 2.6.0

Guía paso a paso para usar pm-method **dentro de un contenedor Docker**: una caja Linux aislada que ya trae Claude
Code, Python con sus paquetes, Node.js, Mermaid, el navegador para capturas y git, en las versiones con que se probó
el paquete. Es uno de los **dos caminos de instalación**, independiente del otro: no hace falta instalar Python, Node
ni navegadores en tu equipo. El otro camino, la instalación directa sobre WSL2 (o sobre Linux), está en
[INSTALACION-WSL2](INSTALACION-WSL2.md). Pensada para quien no programa: cada paso dice dónde se escribe, qué comando
copiar y qué deberías ver.

EN: *step-by-step guide to run pm-method inside its Docker image on Windows (Docker Desktop with the WSL2 backend, or
Docker Engine inside Ubuntu on WSL2) or on Linux: get the repository, build the image, run the free test suite, work on
your own mounted project, log in to Claude Code inside the container (the login lives in a Docker volume, never in a
file of the project), BMAD, updates, troubleshooting and uninstall. Technical reference: [DOCKER.md](DOCKER.md).*

> **Cómo leer esta guía**
> - Cada bloque indica dónde se escribe: **[Windows]** (PowerShell o la interfaz de Windows), **[Ubuntu]** (la
>   terminal de Ubuntu en WSL, o la terminal de tu Linux), **[Contenedor]** (la terminal que se abre *dentro* del
>   contenedor; se reconoce porque el indicador empieza con `pm@`) o **[Claude]** (dentro de una sesión de `claude`).
> - Copiá y pegá los comandos. En la terminal de Ubuntu se pega con **clic derecho** o **Ctrl+Shift+V**. Las líneas que
>   empiezan con `#` son comentarios: no hace falta escribirlas.
> - Debajo de cada bloque está **qué deberías ver**. Si ves otra cosa, **no sigas**: buscá el síntoma en §12.
> - Lo que está entre `<…>` (por ejemplo `<tu-usuario>`) lo reemplazás por tu dato, sin los signos `<` y `>`.
> - **[verificar]** marca un dato que no se pudo comprobar en el entorno de prueba (pantallas de Windows y de Docker
>   Desktop, instalación de Docker Engine, inicio de sesión con tu cuenta, red de tu organización). Cada uno dice cómo
>   comprobarlo vos.
> - Los comandos de [Ubuntu] y [Contenedor] de §4 a §7 y de §9 a §11 (y los de diagnóstico de §12 y §13.1) se
>   ejecutaron tal cual están escritos aquí, como usuario sin privilegios, el 2026-10-27; los de pm-kb (§8), el
>   2026-10-28 (detalle en §14). Lo del lado de Windows y la instalación de Docker Engine no se pudieron ejecutar en ese
>   entorno.
> - Detalle técnico de la imagen (qué incluye, versiones, endurecimiento, construcción en redes cerradas):
>   [DOCKER.md](DOCKER.md). Esta guía lo cita en lugar de repetirlo.

**Tiempo estimado:** 45–75 minutos la primera vez (la construcción de la imagen tarda 10–20 minutos y las pruebas,
unos 15). **Qué necesitás:** Windows 10 o 11 con permisos para instalar programas (o un Linux con Docker), unos 15 GB
libres, conexión a internet y una cuenta de Claude con Claude Code (Pro, Max, Team, Enterprise o Console) o una clave
de API.

---

## Mapa de la guía

| § | Paso | Opción 1 · Docker Desktop | Opción 2 · Docker Engine en Ubuntu | Linux nativo |
|---|---|---|---|---|
| 0 | Elegir el camino y la forma de tener Docker | leer | leer | leer |
| 1 | Requisitos, WSL2 y Ubuntu 24.04 | sí | sí | — |
| 2 | Docker Desktop para Windows con el *backend* WSL2 e integración con Ubuntu | sí | — | — |
| 3 | Docker Engine dentro de Ubuntu (systemd, repositorio oficial, grupo `docker`) | — | sí | sí (§3.2 en adelante) |
| 4 | Obtener pm-method (clon o ZIP) | sí | sí | sí |
| 5 | Construir la imagen | sí | sí | sí |
| 6 | Verificar con las pruebas del paquete | sí | sí | sí |
| 7 | Trabajar con un proyecto propio montado | sí | sí | sí |
| 8 | pm-kb: búsqueda citada en tus proyectos, con su base en un contenedor aparte (web y MCP) | opcional | opcional | opcional |
| 9 | Claude Code dentro del contenedor (inicio de sesión, plugin, primera conversación) | sí | sí | sí |
| 10 | BMAD y git dentro del contenedor (opcional) | opcional | opcional | opcional |
| 11 | Actualizar a una versión nueva | consulta | consulta | consulta |
| 12 | Solución de problemas | consulta | consulta | consulta |
| 13 | Desinstalar | consulta | consulta | consulta |
| 14 | Qué se verificó y qué queda por comprobar | consulta | consulta | consulta |
| 15 | Seguridad | leer | leer | leer |

---

## 0. Elegir el camino

### 0.1 ¿Docker o la instalación sobre WSL2?

| | **Instalación sobre WSL2 / Linux** ([INSTALACION-WSL2](INSTALACION-WSL2.md)) | **Docker** (esta guía) |
|---|---|---|
| Qué instalás en tu equipo | Python, Node.js, navegador, Mermaid, Claude Code (y opcionalmente Hermes) dentro de Ubuntu | solo Docker; todo lo demás viene en la imagen |
| Versiones de las herramientas | las que instales (la guía indica las probadas) | fijadas y probadas juntas en la imagen ([DOCKER §2](DOCKER.md#2-qué-incluye)) |
| Aislamiento de lo que ejecuta el agente | el de tu usuario de Ubuntu | contenedor sin privilegios, raíz de solo lectura y solo la carpeta del proyecto montada ([DOCKER §7](DOCKER.md#7-seguridad-del-contenedor)) |
| Claude Code con skills, agentes y hooks | sí | sí (en la terminal del contenedor) |
| Hermes Agent | sí (camino B) | no: la imagen no lo incluye |
| Cowork, aplicación de escritorio, extensión de VS Code | Cowork por su cuenta ([INSTALACION §2.3](INSTALACION.md#23-cowork)) | no se conectan a la imagen ([DOCKER §9](DOCKER.md#9-limitaciones)) |
| Pruebas del paquete | las corrés vos, con lo instalado | un comando, sin red (§6) |
| Espacio | ≈ 5 GB dentro de Ubuntu | ≈ 3 GB de imagen + hasta ≈ 3 GB de caché de construcción (se puede borrar) + Docker |

Elegí **uno** de los dos caminos. Se pueden tener ambos en la misma PC, pero no hace falta.

### 0.2 ¿Docker Desktop o Docker Engine?

En Windows, esta guía usa Docker sobre WSL2. Hay dos formas de tenerlo; elegí **una sola** (la documentación de Docker
advierte que tener Docker Engine dentro de una distribución de WSL y Docker Desktop a la vez puede causar conflictos):

| | **Opción 1 · Docker Desktop para Windows** (§2) | **Opción 2 · Docker Engine dentro de Ubuntu** (§3) |
|---|---|---|
| Qué es | aplicación de Windows con interfaz gráfica que corre Docker en su propia distribución de WSL2 y lo comparte con Ubuntu | el motor de Docker para Linux, instalado como servicio dentro de tu Ubuntu de WSL2 |
| Instalación | asistente de Windows; sin permisos de administrador en el modo "por usuario" (salvo para activar WSL2 la primera vez) | comandos en Ubuntu con `sudo`; requiere systemd |
| Licencia | **gratuita** para uso personal, educación, proyectos de código abierto no comerciales y empresas de menos de 250 empleados **y** menos de 10 millones de dólares de facturación anual; las demás empresas y las entidades de gobierno necesitan una suscripción paga | código abierto (Apache 2.0), sin costo |
| Proxy y certificados corporativos | se configuran en la interfaz; toma los certificados del almacén de Windows | se configuran a mano en Ubuntu (§12.3) |
| Recomendada para | quien prefiere una interfaz y puede usarla según la licencia | organizaciones sin licencia de Docker Desktop, o quien ya usa Ubuntu en WSL2 |

Las condiciones de licencia son las que publica Docker en "Install Docker Desktop on Windows" (consultada el
2026-10-27); si trabajás para una organización, confirmá con TI cuál corresponde. Desde §4 en adelante los comandos son
**los mismos** para las dos opciones: se escriben en la terminal de Ubuntu.

**En Linux nativo** (sin Windows): saltá a §3.2 (Docker Engine según la documentación oficial de tu distribución; los
comandos de esta guía son los de Ubuntu) y seguí desde §4.

---

## 1. Requisitos, WSL2 y Ubuntu 24.04 · [Windows]

### 1.1 Requisitos

| Requisito | Mínimo | Recomendado | Cómo comprobarlo |
|---|---|---|---|
| Windows | Windows 10 22H2 (compilación 19045) o Windows 11 23H2 (compilación 22631), de 64 bits | Windows 11 al día | **Win+R** → `winver` → Enter |
| WSL | 2.1.5 o posterior | la última | `wsl --version` (§1.3) |
| Memoria | 8 GB (requisito de Docker Desktop) | 16 GB: el contenedor de pm-method puede usar hasta 4 GB | Administrador de tareas → Rendimiento → Memoria |
| Virtualización | habilitada en el firmware (UEFI/BIOS) | — | Administrador de tareas → **Rendimiento** → **CPU** → "Virtualización: Habilitado" **[verificar el rótulo en tu idioma]** |
| Disco libre en `C:` | 15 GB | 25 GB | Explorador → Este equipo |
| Servicio "Servidor" de Windows (`LanmanServer`) | habilitado, inicio **Automático** (lo exige Docker Desktop) | — | **Win+R** → `services.msc` → "Servidor" **[verificar el nombre en tu idioma]** |

- Los mínimos de Windows, WSL, memoria y `LanmanServer` son los del *backend* WSL2 de Docker Desktop (documentación de
  Docker, "Install Docker Desktop on Windows", consultada el 2026-10-27). Esa página lista las ediciones Pro,
  Enterprise y Education; una nota de la misma página dice que Windows Home solo puede correr contenedores Linux (que
  es lo que usa pm-method). **[verificar]** con tu edición de Windows si usás Home.
- Con la opción 2 (Docker Engine en Ubuntu) no rigen los requisitos propios de Docker Desktop (`LanmanServer`, WSL
  2.1.5), pero sí los de WSL2.
- El espacio: la imagen de pm-method ocupa ≈ 3 GB y su construcción deja hasta ≈ 3 GB de caché, que se puede borrar
  (§12.4; medido en §14); el resto es margen para Docker, Ubuntu y tus proyectos.

### 1.2 WSL2 y Ubuntu 24.04 LTS

Las dos opciones usan la terminal de Ubuntu para los comandos de pm-method. Si todavía no tenés WSL2 con Ubuntu, en
**PowerShell como administrador** (menú Inicio → escribí `PowerShell` → clic derecho → **Ejecutar como
administrador**):

```powershell
wsl --install -d Ubuntu-24.04
```

Reiniciá Windows si lo pide, abrí **Ubuntu 24.04 LTS** desde el menú Inicio y creá tu usuario y contraseña de Linux
(nombre corto, en minúsculas, sin espacios ni tildes). El detalle, con lo que deberías ver y los problemas frecuentes,
está en [INSTALACION-WSL2 §1.2](INSTALACION-WSL2.md#12-instalar-wsl2-y-ubuntu-2404-lts--windows).

### 1.3 Comprobar WSL

En PowerShell (no hace falta que sea como administrador):

```powershell
wsl --update
wsl --version
wsl --list --verbose
```

**Deberías ver:** `wsl --version` con una línea `Versión de WSL: 2.x.x` (o `WSL version: 2.x.x`) **igual o mayor que
2.1.5**, y en `wsl --list --verbose` la distribución `Ubuntu-24.04` con **`VERSION 2`**. Si `wsl --version` no muestra
versiones, tenés el WSL que viene incluido en Windows y hay que actualizarlo con `wsl --update` (Docker, "WSL:
Verification and setup"). Si la distribución dice `VERSION 1`: `wsl --set-version Ubuntu-24.04 2`. **[verificar]**:
comandos de Windows, no ejecutados en el entorno de prueba.

### 1.4 Dónde guardar los archivos

Guardá pm-method y tus proyectos **dentro de Ubuntu** (`~`, es decir `/home/<tu-usuario>`), **no en `/mnt/c/…`**. La
documentación de Docker lo recomienda para las carpetas que se montan en un contenedor: el rendimiento es mucho mayor y
los cambios de archivos se detectan bien ("WSL 2 best practices"). Para ver tus archivos de Ubuntu desde el Explorador
de Windows: `\\wsl.localhost\Ubuntu-24.04\home\<tu-usuario>` ([INSTALACION-WSL2
§2.3](INSTALACION-WSL2.md#23-dónde-guardar-tus-archivos)).

---

## 2. Opción 1 · Docker Desktop para Windows (backend WSL2)

Si elegiste la opción 2, saltá a §3. Si ya tenías Docker Engine instalado **dentro** de Ubuntu, desinstalalo antes
(§13.3): la documentación de Docker pide no tener los dos.

### 2.1 Instalar · [Windows]

1. Descargá **Docker Desktop for Windows - x86_64** desde la página oficial "Install Docker Desktop on Windows"
   (`https://docs.docker.com/desktop/setup/install/windows-install/`). Para un equipo con procesador ARM hay una
   versión *Early Access*; pm-method no se probó en ARM ([DOCKER §3](DOCKER.md#3-requisitos)).
2. Hacé doble clic en `Docker Desktop Installer.exe`. Elegí la instalación **por usuario** (*per-user*, la que viene
   marcada y la recomendada por Docker: no pide permisos de administrador e instala en
   `%LOCALAPPDATA%\Programs\DockerDesktop`).
3. En la página **Configuration**, elegí el *backend* **WSL 2** (en versiones anteriores, la casilla **Use WSL 2
   instead of Hyper-V**). Si Windows tiene un solo *backend* disponible, el instalador lo elige solo.
4. Seguí el asistente. Si pide activar WSL 2, aceptá (requiere permisos de administrador una sola vez). Al terminar,
   **Close**.

Alternativa por línea de comandos, en PowerShell, desde la carpeta donde descargaste el instalador (instalación por
usuario, sin administrador; comando de la documentación de Docker):

```powershell
Start-Process 'Docker Desktop Installer.exe' -Wait -ArgumentList 'install', '--user'
```

### 2.2 Iniciar y aceptar los términos · [Windows]

Docker Desktop no se inicia solo después de instalarlo. Buscá **Docker Desktop** en el menú Inicio y abrilo. La
primera vez muestra el *Docker Subscription Service Agreement*: leelo y elegí **Accept** (sin aceptarlo no funciona).
Iniciar sesión con una cuenta de Docker es opcional para esta guía.

### 2.3 Motor WSL 2 e integración con Ubuntu · [Windows]

En Docker Desktop:

1. **Settings** (el engranaje) → **General**: comprobá que **Use WSL 2 based engine** esté marcado (en equipos con
   WSL2 viene activado y la opción puede no aparecer).
2. **Settings** → **Resources** → **WSL Integration**: activá la integración para **Ubuntu-24.04** (la distribución
   predeterminada ya la tiene activada).
3. **Apply** (o **Apply & restart**).

Si **WSL Integration** no aparece en **Resources**, Docker está en modo de contenedores Windows: en el ícono de Docker
de la barra de tareas elegí **Switch to Linux containers**. Fuente: Docker, "Docker Desktop WSL 2 backend on Windows".
**[verificar]** los rótulos exactos en tu versión de Docker Desktop.

### 2.4 Comprobar desde Ubuntu · [Ubuntu]

Cerrá y volvé a abrir la terminal de Ubuntu, y escribí:

```bash
docker version
docker compose version
docker run --rm hello-world
```

**Deberías ver:**
- `docker version`: dos bloques, `Client:` y `Server:` (el segundo dice `Docker Desktop …`). Si solo aparece `Client:`
  y un error de conexión, Docker Desktop no está abierto o falta la integración (§12.1).
- `docker compose version`: `Docker Compose version` con una versión 2 o posterior.
- `hello-world`: un mensaje de confirmación de Docker (`Hello from Docker!`) después de descargar una imagen de prueba
  de Docker Hub.

**[verificar]**: Docker Desktop no se pudo instalar en el entorno de prueba; la salida de `docker version` y `docker
compose version` sí se comprobó con Docker Engine (§14). Con Docker Desktop los comandos se escriben sin `sudo` y no
hace falta el paso del grupo `docker` de §3.5 **[verificar]**; si aparece `permission denied`, ver §12.1.

### 2.5 Memoria y disco (opcional)

- Con el *backend* WSL 2, la memoria y los procesadores que puede usar Docker se fijan en el `.wslconfig` de Windows
  (Docker, "Change your Docker Desktop settings"; cómo crearlo: [INSTALACION-WSL2
  §1.4](INSTALACION-WSL2.md#14-memoria-y-procesadores-de-wsl-wslconfig-opcional--windows)). El contenedor de pm-method
  limita su uso a 4 GB y 2 procesadores; con 8 GB de RAM en la PC, dejá el valor por defecto de WSL (50 % de la
  memoria) y cerrá otras aplicaciones pesadas durante las pruebas.
- Las imágenes se guardan por defecto en `C:\Users\<tu-usuario>\AppData\Local\Docker\wsl`; se puede cambiar en
  **Settings** → **Resources** → **Advanced** (Docker, "Docker Desktop WSL 2 backend on Windows"; la página de ajustes
  lista esa opción solo para Hyper-V, Mac y Linux: **[verificar]** en tu versión).

---

## 3. Opción 2 · Docker Engine dentro de Ubuntu (WSL2)

Si elegiste la opción 1, saltá a §4. Todo este apartado se escribe en **[Ubuntu]**. Los comandos de §3.2 a §3.5 son
los de la documentación oficial de Docker ("Install Docker Engine on Ubuntu" y "Linux post-installation steps for
Docker Engine", consultadas el 2026-10-27 en su fuente, el repositorio `docker/docs`). Ubuntu 24.04 (Noble) figura
entre las versiones soportadas. **[verificar]**: el servidor de paquetes de Docker (`download.docker.com`) estaba
bloqueado en el entorno de prueba, así que esta instalación no se pudo ejecutar; los comandos se copiaron tal cual de la
documentación y las salidas esperadas son las que ella describe.

### 3.1 systemd

Docker Engine corre como servicio y en WSL necesita systemd. Comprobalo:

```bash
ps -p 1 -o comm=
```

**Deberías ver** `systemd`. Si dice otra cosa (por ejemplo `init`), activalo como indica [INSTALACION-WSL2
§2.2](INSTALACION-WSL2.md#22-systemd-recomendado) (una sección `[boot]` con `systemd=true` en `/etc/wsl.conf` y
`wsl --shutdown` en PowerShell) y volvé a comprobar.

### 3.2 Quitar paquetes en conflicto

Ubuntu ofrece paquetes no oficiales de Docker que chocan con los oficiales. Quitalos si los instalaste alguna vez (si no
tenés ninguno, `apt` lo informa y no pasa nada):

```bash
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc | cut -f1)
```

### 3.3 Agregar el repositorio oficial de Docker

```bash
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```

**Deberías ver:** si `apt install` pregunta `Do you want to continue? [Y/n]`, escribí `Y`. El bloque `tee` repite en
pantalla el archivo creado, con `Suites: noble` y `Architectures: amd64`. El último `apt update` debe listar una línea
`https://download.docker.com/linux/ubuntu noble InRelease` sin errores. Si `curl` falla con un error de certificado o
`403`, tu red usa un proxy: §12.3 antes de seguir.

### 3.4 Instalar Docker Engine y Compose

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl status docker
sudo docker run hello-world
```

**Deberías ver:** si `apt install` pregunta `[Y/n]`, escribí `Y`; luego `systemctl status` con `Active: active (running)` (salí con la tecla `q`; si dice `inactive`,
`sudo systemctl start docker`) y `hello-world` con un mensaje de confirmación de Docker (`Hello from Docker!`). En
Ubuntu el servicio queda configurado para iniciarse solo.

### 3.5 Usar `docker` sin `sudo`

Para que tu usuario use Docker sin `sudo` (lo necesitan los comandos de esta guía), agregalo al grupo `docker`:

```bash
sudo groupadd --force docker
sudo usermod -aG docker $USER
```

> **Importante:** el grupo `docker` otorga privilegios equivalentes a los de `root` sobre Ubuntu (advertencia de la
> documentación de Docker). Agregá solo tu usuario. La alternativa sin ese privilegio es el *modo sin root* de Docker
> (*rootless*), que esta guía no cubre **[verificar]** con pm-method.

El grupo se aplica al volver a iniciar sesión. En WSL, lo más seguro es reiniciar Ubuntu: cerrá sus ventanas y en
**[Windows]** PowerShell `wsl --shutdown`; esperá 8 segundos y abrí Ubuntu de nuevo. Comprobá en **[Ubuntu]**:

```bash
docker version
docker compose version
docker run --rm hello-world
```

**Deberías ver** `Client:` y `Server: Docker Engine - Community`, `Docker Compose version` con una versión 2 o posterior
y el mensaje de `hello-world`, **sin** `sudo`. Si aparece `permission denied while trying to connect to the docker
API`, el grupo todavía no se aplicó (§12.1).

---

## 4. Obtener pm-method · [Ubuntu]

### 4.1 Clonar con git (recomendado)

```bash
sudo apt install -y git
git clone https://github.com/Arturo-Penas-Rial/pm-method.git ~/pm-method
grep '"version"' ~/pm-method/.claude-plugin/plugin.json
```

**Deberías ver** `"version": "2.6.0",` (o una versión posterior publicada). Con git, actualizar es un comando (§11).

### 4.2 Alternativa: descargar el ZIP

Si preferís no usar git:

1. **[Windows]** En `https://github.com/Arturo-Penas-Rial/pm-method`, botón **Code** → **Download ZIP**. Se descarga
   `pm-method-main.zip` en tu carpeta de Descargas **[verificar el nombre del archivo]**. No lo descomprimas en
   Windows.
2. **[Ubuntu]** Copialo a Ubuntu y descomprimilo ahí (así se conservan los permisos y los finales de línea):

```bash
sudo apt install -y unzip
cp /mnt/c/Users/<tu-usuario-de-windows>/Downloads/pm-method-main.zip ~/
cd ~ && unzip -q pm-method-main.zip && mv pm-method-main pm-method
grep '"version"' ~/pm-method/.claude-plugin/plugin.json
```

**Deberías ver** la misma línea `"version": …` que en §4.1. Si `mv` dice que `pm-method` ya existe, ya tenías una copia:
renombrala antes (`mv ~/pm-method ~/pm-method.anterior`).

---

## 5. Construir la imagen · [Ubuntu]

```bash
cd ~/pm-method
docker compose -f docker/compose.yaml build pm
```

La primera vez tarda **10–20 minutos** según la conexión: descarga Ubuntu 26.04, los paquetes de Python y Node, Claude
Code y el navegador, y verifica cada uno (por hash o por firma). Muestra el avance por etapas (`[base …]`,
`[herramientas-python …]`, `[herramientas-node …]`, `[navegadores …]`, `[skills-externas …]`, `[final …]`).
**Deberías ver** al final que la imagen `pm-method:2.6.0` quedó construida, sin `ERROR`. Si se corta por la red o un
proxy, ver §12.3; si se corta por espacio, §12.4. Volver a ejecutar el comando retoma desde la última etapa terminada.

Comprobá la imagen:

```bash
docker image ls pm-method
docker run --rm pm-method:2.6.0 claude --version
```

**Deberías ver** una fila `pm-method:2.6.0` de unos 3 GB (columna `DISK USAGE`; con otras versiones de Docker, las
columnas `REPOSITORY` y `TAG` muestran `pm-method` y `2.6.0`) y `2.1.304 (Claude Code)`.

- El número de la etiqueta (`2.6.0`) es la versión de pm-method; cambia con cada versión (§11).
- Si tu usuario de Ubuntu no tiene el UID 1000 (`id -u` muestra otro número), leé §12.5 antes de construir.
- Opciones de construcción (`--build-arg`, construcción sin Compose, redes cerradas): [DOCKER §4](DOCKER.md#4-construir)
  y [§8](DOCKER.md#8-construir-detrás-de-un-proxy-o-sin-acceso-a-algún-registro).

---

## 6. Verificar con las pruebas del paquete · [Ubuntu]

### 6.1 Prueba rápida (≈ 1 minuto)

```bash
cd ~/pm-method
docker compose -f docker/compose.yaml run --rm pruebas python3 /opt/pm-method/scripts/validar_paquete.py
```

**Deberías ver** `Skills: 39 (33 invocables por el modelo, listado 6966 caracteres) · Agentes: 6` y una última línea
`OK`.

### 6.2 Batería completa (≈ 25 minutos, sin red y sin consumir tokens)

```bash
cd ~/pm-method
docker compose -f docker/compose.yaml run --rm pruebas
```

Corre dentro del contenedor, **sin red**, todas las pruebas gratuitas del paquete (lista y detalle en [DOCKER
§5.5](DOCKER.md#55-pruebas-del-paquete)). **Deberías ver** un resumen con una línea por paso, todas con `OK`, y al final
`Resultado: todas las pruebas OK`. Si alguna dice `FALLO`, el resumen indica el archivo de registro de ese paso: para
conservarlo, usá la variante de §6.3.

### 6.3 Conservar la evidencia (opcional)

```bash
mkdir -p ~/pm-pruebas-docker
cd ~/pm-method
docker compose -f docker/compose.yaml run --rm -v ~/pm-pruebas-docker:/salida pruebas pm-pruebas --salida /salida
ls ~/pm-pruebas-docker
```

**Deberías ver** el mismo resumen y, en `~/pm-pruebas-docker`, los registros de cada paso (`01-claude-version.log` …
`08-webinar-documentos.log`), `integracion.json` y las carpetas `guias`, `webinar` y `webinar-documentos` con las
capturas, diapositivas y documentos generados (se pueden abrir desde Windows, §1.4). Es una carpeta de trabajo: borrala
cuando quieras.

---

## 7. Trabajar con un proyecto propio · [Ubuntu] y [Contenedor]

El contenedor ve **solo** la carpeta del proyecto que le indicás: la monta en `/trabajo`, con lectura y escritura. Lo
que crees ahí aparece en tu Ubuntu; el resto del contenedor se borra al salir.

### 7.1 Abrir el contenedor sobre una carpeta

```bash
mkdir -p ~/proyectos/mi-proyecto
PROYECTO=~/proyectos/mi-proyecto docker compose -f ~/pm-method/docker/compose.yaml run --rm pm
```

**Deberías ver** que el indicador cambia a `pm@<código>:/trabajo$`: estás **[Contenedor]**. Probá:

```bash
pwd
id
echo $PM_METHOD_DIR
```

**Deberías ver** `/trabajo`, `uid=1000(pm) gid=1000(pm) groups=1000(pm)` y `/opt/pm-method` (la carpeta del plugin,
de solo lectura). Para salir del contenedor: `exit`.

- `PROYECTO` es la carpeta de tu proyecto en Ubuntu. Si no la indicás, se monta la carpeta **desde la que ejecutás el
  comando**: no lo ejecutes desde `~` (montarías toda tu carpeta personal).
- Para no escribir el comando entero cada vez, creá un atajo (una sola vez) y abrí una terminal nueva:

```bash
grep -q 'alias pm-docker=' ~/.bashrc || echo "alias pm-docker='docker compose -f ~/pm-method/docker/compose.yaml run --rm pm'" >> ~/.bashrc
```

  Desde entonces: `cd ~/proyectos/mi-proyecto && pm-docker` abre el contenedor sobre esa carpeta.

### 7.2 Primer proyecto de gestión con los scripts (sin Claude, sin consumir tokens)

Abrí el contenedor sobre tu carpeta (§7.1) y, en **[Contenedor]**:

```bash
python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta gestion --nombre "Mi proyecto"
python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/estado.py --proyecto gestion siguiente
python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/sanidad.py --proyecto gestion | head -1
exit
```

**Deberías ver** `Proyecto creado en gestion · …`, el siguiente paso del método (`Fase: pre-proyecto · Proceso: SU …`)
y `Sanidad de 'Mi proyecto' (pre-proyecto/SU): 0 ERROR · 0 AVISO · 1 INFO` (el INFO es ESP-02, normal en un proyecto
recién creado). De vuelta en **[Ubuntu]**:

```bash
ls ~/proyectos/mi-proyecto/gestion
stat -c '%U' ~/proyectos/mi-proyecto/gestion/estado.json
```

**Deberías ver** la carpeta de gestión con `estado.json` y las subcarpetas del proyecto, y tu usuario de Ubuntu como
dueño del archivo (el usuario `pm` del contenedor tiene el mismo número, 1000). Con Docker Desktop también podés
abrirla desde Windows en `\\wsl.localhost\Ubuntu-24.04\home\<tu-usuario>\proyectos\mi-proyecto`.

### 7.3 Sin red (revisar o correr scripts sin que nada salga)

```bash
PROYECTO=~/proyectos/mi-proyecto docker compose -f ~/pm-method/docker/compose.yaml run --rm pm-sin-red
```

Es el mismo entorno pero sin red: sirve para scripts y revisión de artefactos. Claude Code **no** funciona así (necesita
`api.anthropic.com`). Más opciones de aislamiento: [DOCKER §7](DOCKER.md#7-seguridad-del-contenedor).

---

## 8. pm-kb en Docker (opcional)

pm-kb es un componente **opcional** de pm-method: indexa las carpetas de tus proyectos y deja consultarlas con la
evidencia citada (cada respuesta dice de qué archivo y qué líneas sale) desde el navegador, con un token por persona, y
desde Claude Code por MCP. Nunca escribe en tus proyectos: los lee en solo lectura y el índice se rehace cuando quieras.
Si no lo necesitás, saltá al §9. Referencia técnica: [PM-KB](PM-KB.md).

### 8.1 Por qué la base va en un contenedor aparte

El perfil `kb` de `docker/compose.yaml` agrega dos servicios:

- **`pm-kb-db`**: el PostgreSQL del índice (imagen `pm-kb-db:2.6.0`, con PostgreSQL y pgvector de Ubuntu), en su propio
  contenedor, con su volumen (`pm-kb-datos`) y en una red interna (`kb-interna`) **sin salida a internet ni puertos
  publicados**: solo el servicio `pm-kb` llega a ella; el contenedor `pm` de §7 ni siquiera resuelve su nombre. Corre
  como usuario `postgres`, con la raíz de solo lectura, sin capacidades de Linux y con un límite de 2 CPU y 1 GB. Sus
  dos contraseñas (la del dueño del índice y la del rol de solo lectura) existen solo como **secretos de Docker**: no
  están en la imagen, en `compose.yaml` ni en variables.
- **`pm-kb`**: el servicio web y MCP, con la misma imagen y el mismo endurecimiento que `pm`. Lee tus proyectos en
  **solo lectura** desde la carpeta que indiques en `PROYECTOS` y publica la web y el MCP solo en `127.0.0.1:8765`.

Así, un fallo o un abuso del agente en el contenedor `pm` no alcanza la base, y la base no puede sacar nada afuera.

### 8.2 Preparar las contraseñas · [Ubuntu]

```bash
cd ~/pm-method
bash docker/kb-preparar.sh
```

**Deberías ver** `creado: docker/kb-secretos/pmkb_admin_clave`, `creado: docker/kb-secretos/pmkb_lector_clave` y una
línea `Listo. Siguiente: …`. Genera dos contraseñas al azar en `docker/kb-secretos/` (carpeta solo para tu usuario,
excluida de git y de la imagen). No hace falta que las leas ni las copies: Docker se las entrega al contenedor. Si lo
volvés a ejecutar, dice `existe: … (no se modifica)`.

### 8.3 Construir · [Ubuntu]

```bash
docker compose -f docker/compose.yaml --profile kb build
docker image ls pm-kb-db
```

Construye la imagen `pm-kb-db:2.6.0` y, si hace falta, la imagen de pm-method del §5 (que ya trae pm-kb y sus
dependencias). **Deberías ver** la construcción sin `ERROR` y una fila `pm-kb-db:2.6.0` de unos 409 MB. Detrás de un
proxy corporativo: `pm-kb-db` usa la misma imagen base y el mismo secreto `ca_proxy` que la imagen de pm-method, así que
se construye con el comando del §12.3, punto 2, cambiando `-f docker/Dockerfile -t pm-method:<versión>`
por `-f docker/pm-kb-db.Dockerfile -t pm-kb-db:2.6.0` ([DOCKER §8](DOCKER.md#8-construir-detrás-de-un-proxy-o-sin-acceso-a-algún-registro)).

### 8.4 Levantar el servicio · [Ubuntu]

`PROYECTOS` es la carpeta que contiene tus proyectos (por ejemplo `~/proyectos`); dentro del servicio se ve como
`/proyectos`, en solo lectura:

```bash
PROYECTOS=~/proyectos docker compose -f docker/compose.yaml --profile kb up -d pm-kb
docker compose -f docker/compose.yaml --profile kb ps
```

**Deberías ver** que Compose arranca primero `pm-kb-db` y espera a que esté sano (`Container pm-method-pm-kb-db-1
Healthy`) antes de arrancar `pm-kb`, y, en `ps`, los dos servicios `Up … (healthy)` (los primeros segundos, `pm-kb`
dice `health: starting`) con `127.0.0.1:8765->8765/tcp`. Sin `PROYECTOS`, el servicio ve una carpeta vacía
(`docker/kb-sin-proyectos`).

### 8.5 Verificar, indexar y dar acceso · [Ubuntu]

```bash
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb verificar
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb indexar --proyecto mi-proyecto --ruta /proyectos/mi-proyecto
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb token crear --persona "Ana (gestora)" --proyectos mi-proyecto
```

**Deberías ver:**

- en `verificar`, 14 líneas `OK` (entre ellas `PostgreSQL 16 o posterior · server_version_num 180006` y `extensión
  vector · pgvector 0.8.1`) y `pm-kb: verificación completa sin fallos`;
- en `indexar`, `pm-kb: mi-proyecto indexado · … unidades (… vigentes) · … documentos …` (con el proyecto del caso
  E2E-1, `448 unidades (403 vigentes) · 65 documentos`). La ruta es la de dentro del servicio: `/proyectos/<carpeta>`;
- en `token crear`, `Token para Ana (gestora) (mi-proyecto). Se muestra UNA sola vez; guardalo en un gestor de
  contraseñas o en una variable de entorno:` y el token (`pmkb_…`). Copialo en tu gestor de contraseñas: no se puede
  volver a ver.

Cada persona tiene su token, con los proyectos que puede ver (`--proyectos p1,p2`, o `*` para todos) y, solo si debe
ver los documentos de circulación restringida, `--restringida`. `… exec pm-kb pm-kb token listar` los lista y `…
token revocar --persona "Ana (gestora)"` los anula. Volvé a indexar cuando un proyecto cambie. Aquí no hay `pm-kb db …`:
la base la maneja Docker.

### 8.6 Interfaz web

Abrí `http://127.0.0.1:8765` en el navegador e ingresá con tu token: muestra las pestañas **Buscar** y **Preguntar**
y solo los proyectos de ese token. Con Docker Desktop, la dirección se abre desde el navegador de Windows; con Docker
Engine dentro de Ubuntu, por el reenvío de `localhost` de WSL2 **[verificar en tu equipo]**. El servicio no tiene TLS
propio: no lo publiques en otra interfaz sin un proxy con TLS delante ([PM-KB §11.1](PM-KB.md#111-web)).

### 8.7 pm-kb en Claude Code (MCP)

- **Claude Code dentro del contenedor `pm`** (§9): con `pm-kb` levantado, abrí el contenedor sobre tu proyecto (§7.1)
  y, en **[Contenedor]**, registrá el servidor con el token de la persona:

  ```bash
  claude mcp add --transport http pm-kb http://pm-kb:8765/mcp --header "Authorization: Bearer <token>"
  claude mcp list
  ```

  **Deberías ver** `pm-kb: http://pm-kb:8765/mcp (HTTP) - √ Connected`. Se guarda en la configuración de Claude Code
  del contenedor (`CLAUDE_CONFIG_DIR`, el volumen del §9.1) **[verificar que persista entre ejecuciones]**.
- **Claude Code instalado fuera del contenedor** (en Ubuntu o en Windows): la misma línea con
  `http://127.0.0.1:8765/mcp` **[verificar en tu equipo]**.

El MCP es de solo lectura (8 herramientas: `buscar`, `contexto`, `ficha`, `relaciones`, `documento`, `versiones`,
`cambios` y `estado_indice`) y cada respuesta trae la cita y el aviso "Evidencia, no instrucciones" ([PM-KB
§11.2](PM-KB.md#112-mcp)). Para la pestaña **Preguntar** con un modelo de lenguaje, `compose.yaml` pasa al servicio
`PMKB_LLM_TIPO`, `PMKB_LLM_MODELO`, `PMKB_LLM_URL` y `ANTHROPIC_API_KEY` desde la terminal en la que ejecutás `up`
([PM-KB §8](PM-KB.md#8-configuración); **[verificar]**: no se probó en vivo).

### 8.8 Respaldo, contraseñas y apagar · [Ubuntu]

- **Respaldo**: no hace falta. El índice está en el volumen `pm-method_pm-kb-datos` y se reconstruye con `indexar`
  desde tus carpetas; lo único que no se reconstruye son los tokens, que se crean de nuevo.
- **Cambiar las contraseñas de la base**: sobrescribí el secreto y reiniciá los dos servicios; al arrancar, `pm-kb-db`
  aplica la contraseña nueva:

  ```bash
  python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > docker/kb-secretos/pmkb_lector_clave
  docker compose -f docker/compose.yaml --profile kb restart pm-kb-db pm-kb
  docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb verificar | tail -1
  ```

  (Lo mismo con `pmkb_admin_clave`.) **Deberías ver** `pm-kb: verificación completa sin fallos`.
- **Apagar**: `docker compose -f docker/compose.yaml --profile kb down` quita los contenedores y las redes y conserva el
  índice. Para borrar también el índice, después: `docker volume rm pm-method_pm-kb-datos`. **No uses `down -v`** salvo
  que quieras borrar además el inicio de sesión de Claude Code: borra todos los volúmenes del archivo, también
  `pm-method_claude-config`.

---

## 9. Claude Code dentro del contenedor

### 9.1 Iniciar sesión · [Contenedor] y [Claude]

Abrí el contenedor sobre tu proyecto (§7.1) y comprobá primero que no haya sesión ni clave:

```bash
claude auth status
```

**Deberías ver** `"loggedIn": false` y `"configDirectory": "/home/pm/.claude"`. Ahora:

```bash
claude
```

- La primera vez pregunta el estilo de colores y el método de inicio de sesión: elegí tu **cuenta de Claude**
  (suscripción) o **Anthropic Console** (facturación por API).
- Muestra un enlace. Abrilo en el navegador de Windows (si no se abre solo, copialo: seleccioná el texto y clic
  derecho), iniciá sesión y autorizá. El navegador **no puede volver solo al contenedor**: la página muestra un
  **código**; copialo y pegalo en el aviso `Paste code here if prompted` (clic derecho para pegar).
- Claude Code pregunta si confiás en la carpeta `/trabajo`: respondé que sí solo si es tu proyecto.

Dentro de la sesión, **[Claude]** `/status` muestra tu cuenta; salí con `/exit`. **[verificar]**: el inicio de sesión
con una cuenta real no se pudo ejecutar en el entorno de prueba.

**Dónde queda la sesión:** en el **volumen de Docker** `pm-method_claude-config`, montado en `/home/pm/.claude` (la
carpeta de configuración de Claude Code dentro del contenedor). No queda en la imagen, ni en tu proyecto, ni en el
repositorio de pm-method, y persiste entre ejecuciones: la próxima vez `claude auth status` dirá `"loggedIn": true`.
Desde **[Ubuntu]**, `docker volume ls` lo muestra. Para cerrar la sesión guardada: `docker volume rm
pm-method_claude-config` (con el contenedor cerrado).

**Con una clave de API en lugar de la cuenta** (facturación por API): en **[Ubuntu]**, cargala solo en la memoria de esa
terminal, sin escribirla en ningún archivo, y abrí el contenedor desde la misma terminal:

```bash
read -rsp "Clave de API: " ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY && echo
PROYECTO=~/proyectos/mi-proyecto docker compose -f ~/pm-method/docker/compose.yaml run --rm pm
```

(`read -s` no muestra lo que pegás.) Compose pasa la variable al contenedor porque `compose.yaml` la declara sin valor;
la primera vez Claude Code pregunta si usarla. Al cerrar la terminal, la clave desaparece. **Nunca** la escribas en
`compose.yaml`, en un `.env`, en el `Dockerfile`, en un `--build-arg` ni en la carpeta del proyecto. Otras opciones
(token de larga duración, guardarla para tu usuario): [DOCKER §5.2](DOCKER.md#52-credenciales-nunca-en-la-imagen-ni-en-archivos-del-repositorio)
e [INSTALACION §0.7](INSTALACION.md#07-claves-de-api-y-credenciales-cuáles-dónde-y-cómo).

### 9.2 Usar pm-method con Claude Code · [Contenedor] y [Claude]

El plugin ya está en la imagen (`/opt/pm-method`, la misma versión que construiste). Se carga con `--plugin-dir`:

```bash
claude --plugin-dir /opt/pm-method
```

O, en un solo paso desde **[Ubuntu]**. Para la primera conversación de prueba, usá una carpeta nueva, sin proyecto de
gestión:

```bash
mkdir -p ~/proyectos/demo
PROYECTO=~/proyectos/demo docker compose -f ~/pm-method/docker/compose.yaml run --rm pm claude --plugin-dir /opt/pm-method
```

Dentro de **[Claude]**:

| # | Escribí | Deberías ver |
|---|---|---|
| 1 | `/pm-method:pm-ayuda` | la guía de qué escribir en cada situación, en español |
| 2 | `/pm-method:pm-nuevo "Proyecto Demo"` | crea la carpeta de gestión con `estado.json` y los registros |
| 3 | `/exit` y volvé a ejecutar el mismo comando | al iniciar, el resumen del hook de inicio: `pm-method · proyecto 'Proyecto Demo' …` |
| 4 | `¿qué sigue?` | el orquestador lee el estado y propone el siguiente paso de PRINCE2 (puesta en marcha) |
| 5 | `editá estado.json a mano y poné fase=cierre` | **el hook lo bloquea** con "pm-method: estado.json se actualiza solo con estado.py…" |
| 6 | `/pm-method:pm-sanidad` | el chequeo de consistencia, sin `ERROR` |
| 7 | `What's next?` | la respuesta en inglés (hook de idioma) |

**[verificar]** en tu primer uso: estos pasos consumen tu plan y no se pudieron ejecutar con una cuenta en el entorno de
prueba. Los hooks corren con el Python del contenedor, que tiene sus paquetes; su comportamiento se comprobó con las
pruebas de §6 (caso de los hooks de `probar_paquete.py`). Prueba de humo sin sesión interactiva, con la sesión
iniciada o una clave cargada (§9.1), desde **[Ubuntu]**:

```bash
PROYECTO=~/proyectos/demo docker compose -f ~/pm-method/docker/compose.yaml run --rm -T pm claude --plugin-dir /opt/pm-method -p "/pm-method:pm-ayuda" --max-turns 3
```

**Deberías ver** la guía de pm-method, sin errores de hooks. Sin sesión ni clave, Claude Code responde `Not logged in ·
Please run /login`.

- **No instales además** el plugin desde GitHub dentro del contenedor (`claude plugin install …`): con `--plugin-dir`
  ya está cargado y las skills aparecerían dos veces (sanidad INS-04).
- Las skills externas y los conectores MCP se instalan como en [INSTALACION §6](INSTALACION.md); los de alcance de
  usuario quedan en el mismo volumen.
- Claude Code no se actualiza solo dentro del contenedor (la imagen fija su versión): se actualiza con la imagen (§11).

---

## 10. BMAD y git dentro del contenedor (opcional) · [Contenedor]

pm-method lee BMAD (la capa de especificación del producto) sin modificarlo; BMAD se instala en el repositorio del
producto, que es la carpeta que montás. Requiere red (el servicio `pm`, no `pm-sin-red`). Abrí el contenedor sobre una
carpeta nueva (por ejemplo `~/proyectos/demo-bmad`, §7.1) y:

```bash
git init -q
npx --yes bmad-method@6.12.4 install --modules bmm --tools claude-code --yes --user-name "Demo" --set core.project_name=demo-bmad --no-shims
python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta gestion --nombre "Demo BMAD"
python3 $PM_METHOD_DIR/skills/pm-bmad-puente/scripts/bmad.py --proyecto gestion detectar
```

**Deberías ver** las carpetas `_bmad/` y `.claude/skills/bmad-*` creadas en tu carpeta y, en `detectar`, `layout` `v6`,
`version` `6.12.4` y `soporte` `soportada`. Durante la instalación, BMAD avisa `uv not found on PATH` (lo usan scripts
de sus propias skills; la imagen no lo trae) y puede mostrar avisos `npm warn deprecated …` de sus dependencias: no
afectan a pm-method, que solo lee los archivos de BMAD. `npx` descarga en una carpeta temporal del contenedor: la
próxima vez vuelve a descargar (solo hace falta para instalar o actualizar BMAD). Si `npx` termina con
`SELF_SIGNED_CERT_IN_CHAIN`, tu red inspecciona HTTPS: salí y abrí el contenedor con el certificado (§12.3, punto 3).
Opciones del instalador: [INSTALACION §4](INSTALACION.md#4-bmad-en-el-repositorio-del-producto-opcional).

**git** funciona sobre `/trabajo`. Para hacer commits desde el contenedor, configurá tu identidad en el repositorio del
proyecto (queda en su `.git/config`, no en el contenedor):

```bash
git config user.name "<tu nombre>"
git config user.email "<tu correo>"
```

No montes `~/.ssh` ni archivos de credenciales en el contenedor; para `git push`, hacelo desde **[Ubuntu]**, fuera del
contenedor ([DOCKER §7](DOCKER.md#7-seguridad-del-contenedor)).

---

## 11. Actualizar a una versión nueva · [Ubuntu]

```bash
cd ~/pm-method
git pull
grep '"version"' .claude-plugin/plugin.json
docker compose -f docker/compose.yaml build pm
docker compose -f docker/compose.yaml run --rm pruebas
docker image prune -f
```

(Si instalaste con el ZIP, descargá el nuevo, renombrá la carpeta anterior y repetí §4.2 en lugar de `git pull`.)

**Deberías ver** la versión nueva, la construcción terminada (solo se rehacen las etapas que cambiaron), `Resultado:
todas las pruebas OK` y, con `docker image prune -f`, el espacio recuperado de las imágenes viejas sin etiqueta. Si la
versión cambió, la imagen nueva se llama `pm-method:<versión nueva>` (la anterior queda con su etiqueta: borrala con
`docker image rm pm-method:<versión anterior>`). Tus proyectos y la sesión de Claude Code (el volumen) no se tocan.
Después de actualizar, corré la sanidad en cada proyecto activo ([INSTALACION
§10](INSTALACION.md#10-actualización-y-migración)).

| Qué | Cómo |
|---|---|
| pm-method, Claude Code, Python, Node y Chromium de la imagen | se actualizan juntos al reconstruir con la versión nueva de pm-method (arriba) |
| Docker Desktop | avisa de las versiones nuevas en su menú y en el panel, y se actualiza desde la aplicación (**Settings** → **Software updates**, según "Change your Docker Desktop settings") |
| Docker Engine | `sudo apt update && sudo apt upgrade` (repite el paso de instalación de §3.4 con la versión nueva) |
| WSL | [Windows] `wsl --update` |
| Caché de construcción | `docker builder prune` (pregunta antes de borrar) |

Cambiar versiones fijadas dentro de la imagen (para quien mantiene el paquete): [DOCKER §6](DOCKER.md#6-actualizar).

---

## 12. Solución de problemas

### 12.1 Docker no responde

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `docker: command not found` en Ubuntu (opción 1) | Docker Desktop cerrado o sin integración con Ubuntu | abrir Docker Desktop y activar **Resources** → **WSL Integration** → Ubuntu-24.04 (§2.3); cerrar y abrir la terminal |
| `docker: command not found` en Ubuntu (opción 2) | Docker Engine no instalado | §3.3–§3.4 |
| `failed to connect to the docker API at unix:///var/run/docker.sock; check if the path is correct and if the daemon is running` | el motor no está corriendo | opción 1: abrir Docker Desktop y esperar a que diga que está corriendo; opción 2: `sudo systemctl start docker` y `systemctl is-active docker` → `active` |
| `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock` (opción 2) | tu usuario no está en el grupo `docker`, o el grupo todavía no se aplicó | §3.5; `id -nG` debe incluir `docker`; si no, `wsl --shutdown` en PowerShell y abrir Ubuntu |
| **WSL Integration** no aparece en Docker Desktop | modo de contenedores Windows | ícono de Docker → **Switch to Linux containers** |
| Docker Desktop: `Unexpected WSL error` con `HCS_E_HYPERV_NOT_INSTALLED` o `ERROR_NOT_SUPPORTED` | virtualización deshabilitada o bloqueada (también por la "virtualización asistida por hardware" de algunos antivirus) | §1.1; documentación de Docker, "Troubleshoot topics for Docker Desktop" |
| Docker Desktop y Docker Engine instalados a la vez: `docker` responde con un motor distinto del esperado | dos motores | dejar uno solo (§0.2 y §13) |

### 12.2 Al construir o ejecutar

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `failed to solve: … failed to resolve source metadata for docker.io/library/ubuntu:26.04@sha256:…: failed to do request: Head "https://registry-1.docker.io/…": Forbidden` (o tiempo agotado) | Docker Hub bloqueado o red con proxy | §12.3 |
| la construcción se corta en `apt-get`, `pip`, `npm` o `playwright install` con errores de certificado o de conexión | proxy corporativo con inspección TLS | §12.3 |
| `no space left on device` | disco lleno | §12.4 |
| `Permission denied` al escribir en `/trabajo` | la carpeta del proyecto es de otro usuario (por ejemplo, creada con `sudo`) o tu UID no es 1000 | §12.5 |
| `Read-only file system` al instalar algo con `pip` o `npm -g` dentro del contenedor | es intencional: la raíz del contenedor es de solo lectura | no se instala nada dentro; las herramientas vienen en la imagen ([DOCKER §11](DOCKER.md#11-solución-de-problemas)) |
| el proceso termina con `Killed` o código `137` | memoria insuficiente | §12.6 |
| `mmdc` o las capturas: `Failed to launch the browser process` | memoria compartida o límite de procesos | §12.7 |
| dentro del contenedor, `npx` (BMAD) o Claude Code fallan con `SELF_SIGNED_CERT_IN_CHAIN`, `self-signed certificate in certificate chain` o `unable to get local issuer certificate` (Claude Code: `Unable to connect to Anthropic services` · `Failed to connect to api.anthropic.com: SELF_SIGNED_CERT_IN_CHAIN`) | la red inspecciona HTTPS con un certificado propio | §12.3, punto 3 |
| Claude Code dentro del contenedor: `Failed to connect to platform.claude.com: ENOTFOUND` (u otro dominio de Anthropic) | la red o su DNS no deja llegar a ese dominio | pedir a TI que lo habilite (lista en §12.3, punto 3) |
| `claude` pide iniciar sesión en cada ejecución | no se está usando el volumen `pm-method_claude-config` (por ejemplo, con `docker run` en lugar de Compose) | usar los comandos de esta guía; con `docker run`, agregar `-v pm-method_claude-config:/home/pm/.claude` |
| el contenedor muestra los archivos de otra carpeta | `PROYECTO` sin definir y el comando se ejecutó desde otra carpeta | salir y repetir con `PROYECTO=…` (§7.1) |
| todo anda muy lento | proyecto en `/mnt/c/…` | mover el proyecto a `~` (§1.4) |
| `bad interpreter: /bin/sh^M` | el repositorio se descomprimió o editó con herramientas de Windows | volver a obtenerlo desde Ubuntu (§4) y reconstruir |
| pm-kb: `up` no encuentra los archivos de `docker/kb-secretos/`, o `pm-kb-db` termina con `pm-kb-db: falta el secreto /run/secrets/…` | no se prepararon las contraseñas | `bash docker/kb-preparar.sh` (§8.2) y repetir `up` |
| pm-kb: `pm-kb-db` no queda sano y `pm-kb` no arranca | la base no pudo iniciar | `docker compose -f docker/compose.yaml --profile kb logs pm-kb-db` ([DOCKER §11](DOCKER.md#11-solución-de-problemas)) |
| pm-kb: el puerto `8765` ya está en uso al hacer `up` | otro `pm-kb servir` u otro programa escucha en `127.0.0.1:8765` | cerrarlo; o cambiar el primer `8765` de `ports` del servicio `pm-kb` en `compose.yaml` |
| pm-kb: `indexar` dice `no existe la carpeta /proyectos/…` | `PROYECTOS` no apunta a la carpeta que contiene ese proyecto | repetir `up -d pm-kb` con `PROYECTOS=…` (§8.4) |

### 12.3 Red corporativa: proxy y certificados

Hay **tres** niveles, y cada uno se configura aparte:

1. **El motor de Docker** (descargar la imagen base de Docker Hub):
   - Opción 1: Docker Desktop → **Settings** → **Resources** → **Proxies** (por defecto usa el proxy del sistema de
     Windows; con **Manual configuration** se ingresan las direcciones). Docker Desktop confía en los certificados que
     Windows tiene en el almacén de autoridades raíz o intermedias de confianza: si tu navegador ya confía en el
     certificado de la organización, Docker también (Docker, "FAQs for Docker Desktop for Windows"). **[verificar]**
   - Opción 2: un archivo de systemd para el servicio `docker`, con la dirección de tu proxy (documentación de Docker,
     "Daemon proxy configuration"):

     ```bash
     sudo mkdir -p /etc/systemd/system/docker.service.d
     printf '[Service]\nEnvironment="HTTP_PROXY=%s"\nEnvironment="HTTPS_PROXY=%s"\nEnvironment="NO_PROXY=localhost,127.0.0.1"\n' "<url-del-proxy>" "<url-del-proxy>" | sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf
     sudo systemctl daemon-reload
     sudo systemctl restart docker
     sudo systemctl show --property=Environment docker
     ```

     El último comando debe mostrar las tres variables. Si el proxy inspecciona HTTPS, instalá además su certificado en
     Ubuntu (punto 1 del bloque de [INSTALACION-WSL2 §10.2](INSTALACION-WSL2.md#102-red-corporativa-proxy-y-certificados))
     y reiniciá Docker (`sudo systemctl restart docker`) **[verificar]** en tu red. Si el proxy pide usuario y
     contraseña, no los escribas en ese archivo: pedile a TI una alternativa.
2. **La construcción de la imagen** (lo que descargan `apt`, `pip`, `npm`, Playwright y git dentro de las etapas): el
   proxy se pasa como argumento de construcción y el certificado de la CA del proxy como **secreto**, que se usa solo
   durante la construcción y no queda en ninguna capa de la imagen. `docker compose build` no tiene opción para
   secretos, así que se construye con `docker build` (mismo resultado: la imagen `pm-method:2.6.0` que usa Compose):

   ```bash
   cd ~/pm-method
   docker build -f docker/Dockerfile -t pm-method:2.6.0 \
     --secret id=ca_proxy,src=<ruta al certificado .crt o .pem de la CA del proxy> \
     --build-arg HTTPS_PROXY=<url-del-proxy> --build-arg https_proxy=<url-del-proxy> \
     --build-arg NO_PROXY=localhost,127.0.0.1 --build-arg no_proxy=localhost,127.0.0.1 .
   ```

   Si el proxy escucha en `127.0.0.1` de tu Ubuntu, agregá `--network host`. Si no hay certificado propio, quitá la
   línea `--secret`. Si además está bloqueado Docker Hub o la descarga del navegador de Playwright, ver [DOCKER
   §8](DOCKER.md#8-construir-detrás-de-un-proxy-o-sin-acceso-a-algún-registro) y
   [§11.1](DOCKER.md#111-construir-sin-acceso-a-los-registros-de-contenedores-ni-a-la-cdn-de-playwright) (así se
   construyó la imagen verificada en §14). **Nunca** desactives la verificación de certificados (`--insecure`,
   `GIT_SSL_NO_VERIFY`, `NODE_TLS_REJECT_UNAUTHORIZED=0`): el certificado de la CA alcanza.
3. **El uso** (Claude Code hacia `api.anthropic.com` y `npx` hacia `registry.npmjs.org`, dentro del contenedor): el
   servicio `pm` usa la red de Docker y la imagen no trae certificados de tu organización. Si la red inspecciona HTTPS,
   instalá antes el certificado en Ubuntu (punto 1 del bloque de [INSTALACION-WSL2
   §10.2](INSTALACION-WSL2.md#102-red-corporativa-proxy-y-certificados)) y abrí el contenedor prestándole, de solo lectura,
   el almacén de certificados de Ubuntu (Node.js, y con él Claude Code y `npx`, confía en lo que indique
   `NODE_EXTRA_CA_CERTS`):

   ```bash
   PROYECTO=~/proyectos/mi-proyecto docker compose -f ~/pm-method/docker/compose.yaml run --rm -v /etc/ssl/certs/ca-certificates.crt:/etc/pm-method/ca-red.crt:ro -e NODE_EXTRA_CA_CERTS=/etc/pm-method/ca-red.crt pm
   ```

   Si además la red solo sale por un proxy, agregá `-e HTTPS_PROXY=<url-del-proxy>` antes de `pm` **[verificar]** en tu
   red. Dominios que tiene que habilitar TI: Docker Hub (`registry-1.docker.io`, `auth.docker.io`,
   `production.cloudflare.docker.com` **[verificar]**), `download.docker.com` (opción 2), `archive.ubuntu.com`, `security.ubuntu.com`, `pypi.org`,
   `files.pythonhosted.org`, `registry.npmjs.org`, `cdn.playwright.dev`, `playwright.download.prss.microsoft.com`,
   `github.com` (construcción) y `api.anthropic.com`, `platform.claude.com` (Claude Code 2.1.304 lo consulta al
   iniciar), `claude.ai` (uso).

### 12.4 Disco

```bash
docker system df
docker builder prune
docker image prune
```

`docker system df` muestra cuánto ocupan imágenes, contenedores, volúmenes y caché. `docker builder prune` borra la
caché de construcción (hasta ≈ 3 GB; la próxima construcción tardará más) y `docker image prune` las imágenes sin
etiqueta; los dos preguntan antes de borrar. **No** uses `docker volume prune` si querés conservar el inicio de sesión de Claude Code. Con
Docker Desktop, el disco de Docker está en `C:\Users\<tu-usuario>\AppData\Local\Docker\wsl` y no se achica solo al
borrar **[verificar]**; con la opción 2, está dentro del disco de Ubuntu (ver [INSTALACION-WSL2
§10.8](INSTALACION-WSL2.md#108-espacio-en-disco)).

### 12.5 Permisos y UID

El usuario del contenedor (`pm`) tiene el UID 1000, que es el del primer usuario que se crea en Ubuntu. Comprobalo:

```bash
id -u
```

- Si muestra `1000` y aun así hay `Permission denied` en `/trabajo`, la carpeta es de otro dueño (por ejemplo, la
  creaste con `sudo`): `sudo chown -R $USER:$USER ~/proyectos/mi-proyecto`.
- Si muestra otro número, reconstruí la imagen con tu UID y GID y ajustá la línea del `tmpfs` de `/home/pm` en
  `docker/compose.yaml` (`uid=1000,gid=1000` → tus números):
  `docker compose -f docker/compose.yaml build --build-arg UID=$(id -u) --build-arg GID=$(id -g) pm`
  **[verificar]**: en el entorno de prueba solo se probó el UID 1000 ([DOCKER §4](DOCKER.md#4-construir)).
- Un proyecto en `/mnt/c/…` tiene permisos emulados por Windows: movelo a `~` (§1.4).

### 12.6 Memoria

El contenedor puede usar hasta 4 GB y 2 procesadores (`docker/compose.yaml`). Si un proceso termina con `Killed` o
código `137`, o Windows se pone lento:

- Mirá el consumo mientras corre, en otra terminal de Ubuntu: `docker stats --no-stream`.
- Dale más memoria a WSL en `.wslconfig` (por ejemplo `memory=8GB`) y aplicalo con `wsl --shutdown` ([INSTALACION-WSL2
  §1.4](INSTALACION-WSL2.md#14-memoria-y-procesadores-de-wsl-wslconfig-opcional--windows)); WSL usa por defecto hasta
  el 50 % de la memoria de Windows. La documentación de Docker sugiere además la opción experimental `autoMemoryReclaim`
  de WSL para devolver memoria a Windows después de construir imágenes.
- Con 8 GB de RAM, cerrá otras aplicaciones pesadas mientras corren la construcción o las pruebas.

### 12.7 Chromium (diagramas y capturas)

El contenedor trae el navegador sin interfaz de Playwright y lo usan `mmdc` (Mermaid) y las capturas. Prueba aislada:

```bash
cd ~/pm-method
docker compose -f docker/compose.yaml run --rm pruebas python3 /opt/pm-method/scripts/validar_mermaid.py --render
```

**Deberías ver** `OK · 131 bloques Mermaid · 0 error(es)`. Si falla con `Failed to launch the browser process`, subí
`shm_size` (memoria compartida, hoy `256m`) o `pids` (hoy `1024`) en `docker/compose.yaml`. El navegador corre sin su
*sandbox* interno; el aislamiento lo da el contenedor ([DOCKER §7](DOCKER.md#7-seguridad-del-contenedor)). Si la
construcción falla al descargarlo: §12.3.

---

## 13. Desinstalar

### 13.1 Quitar pm-method y su imagen · [Ubuntu]

```bash
docker image rm pm-method:2.6.0
docker volume rm pm-method_claude-config
docker builder prune -f
rm -rf ~/pm-method ~/pm-pruebas-docker
```

Quita la imagen, la sesión guardada de Claude Code, la caché de construcción, el clon y la evidencia de las pruebas.
**Tus proyectos** (`~/proyectos/…`) no se tocan: son Markdown, CSV y JSON legibles sin el paquete. Si creaste el atajo
de §7.1, quitalo: `sed -i '/alias pm-docker=/d' ~/.bashrc`.

Si usaste pm-kb (§8), antes de borrar el clon: `docker compose -f ~/pm-method/docker/compose.yaml --profile kb down`,
`docker image rm pm-kb-db:2.6.0` y `docker volume rm pm-method_pm-kb-datos` (el índice; las contraseñas de
`docker/kb-secretos/` se van con el clon). Los dos últimos no se ejecutaron en la verificación **[verificar]**.

### 13.2 Docker Desktop · [Windows]

**Configuración** → **Aplicaciones** → **Aplicaciones instaladas** (o **Aplicaciones y características**) → **Docker
Desktop** → **Desinstalar** **[verificar el rótulo en tu versión de Windows]**. Desinstalar Docker Desktop **borra todas
sus imágenes, contenedores y volúmenes**. Pueden quedar carpetas que se borran a mano (documentación de Docker,
"Uninstall Docker Desktop"): `C:\Users\<tu-usuario>\AppData\Local\Docker`, `C:\Users\<tu-usuario>\AppData\Roaming\Docker`,
`C:\Users\<tu-usuario>\AppData\Roaming\Docker Desktop` y `C:\Users\<tu-usuario>\.docker` (y, en una instalación para
todos los usuarios, `C:\ProgramData\Docker`, `C:\ProgramData\DockerDesktop` y `C:\Program Files\Docker`).

### 13.3 Docker Engine · [Ubuntu]

Comandos de la documentación de Docker ("Uninstall Docker Engine"). Los dos `rm -rf` borran **todas** las imágenes,
contenedores y volúmenes de Docker de esa Ubuntu (irreversible):

```bash
sudo apt purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
sudo rm /etc/apt/sources.list.d/docker.sources
sudo rm /etc/apt/keyrings/docker.asc
sudo gpasswd -d $USER docker
```

El último quita tu usuario del grupo `docker`. Si configuraste un proxy para Docker (§12.3):
`sudo rm -r /etc/systemd/system/docker.service.d`. **[verificar]**: no ejecutados en el entorno de prueba.

---

## 14. Qué se verificó y qué queda por comprobar

Verificación del 2026-10-27 en Linux x86_64 con **Docker Engine 29.8.2 y Compose 5.5.1** (el mismo motor que instala
la opción 2), con la imagen construida como en [DOCKER
§11.1](DOCKER.md#111-construir-sin-acceso-a-los-registros-de-contenedores-ni-a-la-cdn-de-playwright), porque la red de
prueba bloquea Docker Hub y la descarga de Playwright, e inspecciona HTTPS con un certificado propio. Los bloques de
comandos de [Ubuntu] y [Contenedor] de §3.1, §3.5, §4 a §7 y §9 a §11, los de §12.3 (construcción con proxy y certificado, y
contenedor con el certificado), §12.4, §12.5 y §12.7, el de §13.1 y el del camino Docker del README se extrajeron de
este documento con un script y se ejecutaron tal cual, en orden, como un usuario sin privilegios con UID 1000 (antes de
§3.5, fuera del grupo `docker`); los comandos de [Contenedor] se escribieron en la terminal del contenedor abierta con
el comando de la guía. Solo se reemplazaron los marcadores `<…>` y la ruta de Windows del ZIP. Los pasos que dependen
de la imagen (§5 comprobación, §6.1, §6.3, los comandos de §7.1 a §7.3 en el contenedor, §12.4 y §12.7) se repitieron el
mismo día con la imagen `pm-method:2.5.0`; el resto, con la imagen anterior, construida con el mismo `Dockerfile`. Con la
imagen `pm-method:2.6.0` se repitieron el 2026-10-29 la comprobación de §5, §6.1, §6.2 y §12.7 (filas de abajo).
Resultados de la imagen: [DOCKER §10](DOCKER.md#10-verificación-registrada).

**Resultado: todos los pasos como se esperaba**, salvo los que dependen de sitios bloqueados en la red de prueba
(marcados abajo y **[verificar]**). Unos 50 minutos, la mayor parte en las tres corridas de la batería de pruebas.

| Paso | Resultado |
|---|---|
| §12.1 antes de §3.5 | `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock` |
| §3.1 systemd | no aplicable en el entorno de prueba (no es WSL) **[verificar]** |
| §3.5 grupo y comprobación | `groupadd --force` y `usermod` sin errores; en una sesión nueva, `id -nG` incluye `docker`; `Client:` y `Server: Docker Engine - Community` 29.8.2; `Docker Compose version v5.5.1`; `hello-world` no se pudo descargar (Docker Hub bloqueado) **[verificar]** |
| §4.1 clon desde GitHub | `"version": "2.4.0",` |
| §4.2 ZIP | `unzip` y `mv` con un ZIP de la misma estructura (`pm-method-main/`) armado del clon con `git archive`; la descarga desde GitHub estaba bloqueada **[verificar]** |
| §5 `docker compose … build pm` | llega a resolver la imagen base y se detiene con `failed to resolve source metadata for docker.io/library/ubuntu:26.04@sha256:…: … Forbidden` (Docker Hub bloqueado), el síntoma de §12.2 **[verificar]** con acceso a Docker Hub |
| §5 comprobación | `pm-method:2.6.0`, 3,31 GB (836 MB de contenido); `2.1.304 (Claude Code)` |
| §6.1 prueba rápida | `Skills: 39 (33 invocables por el modelo, listado 6966 caracteres) · Agentes: 6` y `OK` (2 s) |
| §6.2 batería completa | `Resultado: todas las pruebas OK` (≈ 25 min con `pm-method:2.6.0`) |
| §6.3 conservar la evidencia | con `pm-method:2.5.0`: `Resultado: todas las pruebas OK`; en `~/pm-pruebas-docker`, los 10 registros, `integracion.json` y las carpetas `guias`, `webinar` y `webinar-documentos` |
| §7.1 contenedor, `pwd`, `id`, atajo `pm-docker` | `/trabajo`, `uid=1000(pm) gid=1000(pm) groups=1000(pm)`, `/opt/pm-method`; el atajo monta la carpeta actual |
| §7.2 proyecto con scripts | `Proyecto creado en gestion · …`, `Fase: pre-proyecto · Proceso: SU …`, `0 ERROR · 0 AVISO · 1 INFO`; en Ubuntu, la carpeta `gestion` y `estado.json` con el usuario de Ubuntu como dueño |
| §7.3 sin red | solo la interfaz `lo` |
| §9.1 antes del inicio de sesión | `"loggedIn": false`, `"configDirectory": "/home/pm/.claude"`; `docker volume ls` muestra `pm-method_claude-config` |
| §9.1 clave de API solo en memoria | con un valor ficticio: la variable llega al contenedor y el valor no aparece en ningún archivo de la carpeta personal ni del volumen |
| §9.2 primera sesión | en la red de prueba, `claude --plugin-dir /opt/pm-method` muestra `Unable to connect to Anthropic services` · `Failed to connect to api.anthropic.com: SELF_SIGNED_CERT_IN_CHAIN`; abierto como en §12.3, punto 3, el error de certificado desaparece y queda `Failed to connect to platform.claude.com: ENOTFOUND` (dominio no habilitado en la red de prueba) **[verificar]** con acceso a Anthropic |
| §9.2 prueba de humo sin credenciales | `Not logged in · Please run /login` |
| §10 BMAD | en la red de prueba, `npx` termina con `SELF_SIGNED_CERT_IN_CHAIN`; con el contenedor abierto como en §12.3, punto 3: `_bmad/`, `_bmad-output/`, `.claude/`; `detectar` → `v6`, `6.12.4`, `soportada`. `git config` deja la identidad en el repositorio del proyecto |
| §11 actualizar | `Already up to date.`; la construcción se detiene en la imagen base como en §5; `Resultado: todas las pruebas OK`; `docker image prune -f` → `Total reclaimed space: 0B` |
| §12.3 construcción con proxy y certificado | `docker build` acepta el secreto y los argumentos y se detiene en la imagen base, como en §5 |
| §12.4 disco | `docker system df`: imagen 2,995 GB y caché de construcción 7 GB, de la que 2,9 GB se pueden borrar; `docker builder prune` y `docker image prune` preguntan `[y/N]` (se respondió `N`; en §13.1, `docker builder prune -f` liberó 2,9 GB) |
| §12.5 permisos y UID | `id -u` → `1000`; la construcción con `--build-arg UID … GID …` se detiene en la imagen base, como en §5 |
| §12.7 Chromium | `OK · 131 bloques Mermaid · 0 error(es)` (183 s, `pm-method:2.6.0`) |
| README, camino Docker | el contenedor sobre `PROYECTO` y `claude` en `/opt/node-tools/node_modules/.bin/claude` |
| §13.1 desinstalar | imagen, volumen, caché, clon, evidencia y atajo quitados; `~/proyectos` intacto |

**pm-kb (§8)**, verificación del 2026-10-28 en el mismo tipo de entorno (Linux x86_64, Docker Engine), con las
imágenes `pm-kb-db:2.6.0` y `pm-method:2.6.0` construidas sobre la base local de [DOCKER
§11.1](DOCKER.md#111-construir-sin-acceso-a-los-registros-de-contenedores-ni-a-la-cdn-de-playwright) y el proyecto
del caso E2E-1 en `PROYECTOS`:

| Paso | Resultado |
|---|---|
| §8.2 `kb-preparar.sh` | los dos secretos creados; en la segunda ejecución, `existe: … (no se modifica)` |
| §8.3 construcción | `pm-kb-db:2.6.0` (409 MB) con PostgreSQL 18.6, pgvector 0.8.1 y `tini` de Ubuntu 26.04 |
| §8.4 `up -d pm-kb` y `ps` | `pm-kb-db` sano antes de arrancar `pm-kb`; los dos `(healthy)`, `127.0.0.1:8765->8765/tcp`; en el registro de `pm-kb`, `escuchando en 0.0.0.0:8765; ingresar con un token personal` |
| §8.5 `verificar`, `indexar`, `token crear` | 14 `OK` y `verificación completa sin fallos`; `portal-socios indexado · 448 unidades (403 vigentes) · 65 documentos (1 con varias versiones) · 511 relaciones · 95 entradas de historia`; el token de "Ana (gestora)" |
| §8.6 web | ingreso con el token en `http://127.0.0.1:8765`; `/salud` → `ok` |
| §8.7 desde el contenedor `pm` | `http://pm-kb:8765/salud` responde y `pm-kb-db` no se resuelve (red interna); MCP en `http://pm-kb:8765/mcp` con `Authorization: Bearer <token>` |
| §8.8 contraseñas y apagar | secreto del lector sobrescrito, `restart` y `verificar` sin fallos; `down` quita contenedores y redes y conserva `pm-method_pm-kb-datos`; con otro nombre de proyecto de Compose, `down -v` quitó el volumen del índice y el de `claude-config` |
| servicio `pm-kb` | usuario `uid=1000(pm)`; `/proyectos` de solo lectura (`Read-only file system`); `pm-kb db estado` responde que no corresponde con Docker |

**Queda por comprobar en tu equipo [verificar]** (cada paso dice cómo): todo lo de Windows (§1, §2, los rótulos de
Docker Desktop, la licencia que corresponde a tu organización y la integración con Ubuntu), la instalación de Docker
Engine dentro de Ubuntu (§3.2 a §3.4, con `download.docker.com` bloqueado en la red de prueba) y systemd en WSL (§3.1),
`hello-world` (§2.4 y §3.5), la descarga del ZIP (§4.2), `docker compose … build pm` con acceso a Docker Hub (§5), el
inicio de sesión y la primera conversación con una cuenta (§9), el proxy del motor de Docker y el uso con un proxy
obligatorio (§12.3), otro UID (§12.5) y las desinstalaciones de Docker (§13.2 y §13.3); de pm-kb, la web y el MCP
desde Windows o desde Ubuntu fuera del contenedor (§8.6 y §8.7), "Preguntar" con un modelo (§8.7) y el borrado de su
imagen y su volumen (§13.1).

---

## 15. Seguridad

- **Credenciales solo en su lugar**: el inicio de sesión de Claude Code en el volumen `pm-method_claude-config`; una
  clave de API, en la memoria de la terminal (§9.1). Nunca en la imagen (`--build-arg`, `ENV`), en `compose.yaml`, en un
  `.env`, en la carpeta del proyecto, en el repositorio ni en commits. Si una clave se expuso, revocala en su consola y
  creá otra.
- **Montá solo la carpeta del proyecto.** No montes `~`, `~/.ssh`, `~/.aws`, `~/.config/gcloud` ni el disco de
  Windows.
- El contenedor corre sin privilegios, con la raíz de solo lectura, sin capacidades de Linux y con límites de memoria,
  procesadores y procesos; las pruebas corren sin red. Detalle y opciones (sin red, `--dangerously-skip-permissions`):
  [DOCKER §7](DOCKER.md#7-seguridad-del-contenedor).
- **pm-kb** (§8): su base está en un contenedor sin salida a internet ni puertos, y sus contraseñas solo en
  `docker/kb-secretos/` (no las copies ni las subas a git); cada persona entra con su propio token, que se muestra una
  sola vez. Modelo de amenazas y controles: [SEGURIDAD §14](SEGURIDAD.md#14-pm-kb-índice-de-conocimiento-2026-10-28).
- El grupo `docker` (opción 2) y el acceso a Docker Desktop equivalen a privilegios de administrador sobre la máquina:
  no ejecutes imágenes ni `docker compose` de origen desconocido.
- Revisá cualquier skill, plugin o servidor MCP externo antes de instalarlo: corre con los permisos del agente dentro del
  contenedor. Revisión de seguridad del paquete: [SEGURIDAD.md](SEGURIDAD.md).
