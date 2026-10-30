# Instalación con Docker · pm-method 2.7.0

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
>   ejecutaron tal cual están escritos aquí, como usuario sin privilegios, el 2026-10-27; los de pm-kb (§8.1 a §8.8), el
>   2026-10-28 (detalle en §14). Los procedimientos de los opcionales (§8.9, §8.10, §9.3 a §9.5 y §11.1) se comprobaron
>   en parte el 2026-10-29 y el 2026-10-30: cada uno dice qué se verificó y qué no. Lo del lado de Windows y la instalación de Docker Engine
>   no se pudieron ejecutar en ese entorno.
> - Detalle técnico de la imagen (qué incluye, versiones, endurecimiento, construcción en redes cerradas):
>   [DOCKER.md](DOCKER.md). Esta guía lo cita en lugar de repetirlo.

**Tiempo estimado:** 45–75 minutos la primera vez (la construcción de la imagen tarda 10–20 minutos y las pruebas,
unos 25). **Qué necesitás:** Windows 10 o 11 con permisos para instalar programas (o un Linux con Docker), unos 15 GB
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
| 8 | pm-kb: búsqueda citada en tus proyectos, con su base en un contenedor aparte (web y MCP), y sus modelos opcionales | opcional | opcional | opcional |
| 9 | Claude Code dentro del contenedor (inicio de sesión, plugin, primera conversación); opcionales: envío a interesados, skills externas, conectores MCP | sí | sí | sí |
| 10 | BMAD y git dentro del contenedor (opcional) | opcional | opcional | opcional |
| 11 | Actualizar a una versión nueva (también pm-kb) | consulta | consulta | consulta |
| 12 | Solución de problemas | consulta | consulta | consulta |
| 13 | Desinstalar | consulta | consulta | consulta |
| 14 | Lista de aceptación; qué se verificó y qué queda por comprobar | sí | sí | sí |
| 15 | Seguridad | leer | leer | leer |

Opcionales y dónde están: pm-kb §8, sus modelos §8.9, la vigilancia del índice §8.10 y el portal con enlaces compartidos §8.11 · envío a interesados (capa de canales) §9.3 · skills externas
§9.4 · conectores MCP §9.5 · BMAD §10. Vienen ya en la imagen (nada que instalar): los paquetes de Python, Node.js,
Mermaid, `pptxgenjs` y el navegador para capturas ([DOCKER §2](DOCKER.md#2-qué-incluye)). **No** vienen ni se cubren
aquí: LibreOffice, `pandoc` y el paquete npm `docx` (requisitos de las skills de Office, §9.4), Java con MPXJ, Orca y
Hermes.

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

**Deberías ver** `"version": "2.7.0",` (o una versión posterior publicada). Con git, actualizar es un comando (§11).

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
**Deberías ver** al final que la imagen `pm-method:2.7.0` quedó construida, sin `ERROR`. Si se corta por la red o un
proxy, ver §12.3; si se corta por espacio, §12.4. Volver a ejecutar el comando retoma desde la última etapa terminada.

Comprobá la imagen:

```bash
docker image ls pm-method
docker run --rm pm-method:2.7.0 claude --version
```

**Deberías ver** una fila `pm-method:2.7.0` de unos 3 GB (columna `DISK USAGE`; con otras versiones de Docker, las
columnas `REPOSITORY` y `TAG` muestran `pm-method` y `2.7.0`) y `2.1.304 (Claude Code)`.

- El número de la etiqueta (`2.7.0`) es la versión de pm-method; cambia con cada versión (§11).
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

El perfil `kb` de `docker/compose.yaml` agrega tres servicios:

- **`pm-kb-db`**: el PostgreSQL del índice (imagen `pm-kb-db:2.7.0`, con PostgreSQL y pgvector de Ubuntu), en su propio
  contenedor, con su volumen (`pm-kb-datos`) y en una red interna (`kb-interna`) **sin salida a internet ni puertos
  publicados**: solo los servicios `pm-kb` y `pm-kb-vigilar` llegan a ella; el contenedor `pm` de §7 ni siquiera resuelve su nombre. Corre
  como usuario `postgres`, con la raíz de solo lectura, sin capacidades de Linux y con un límite de 2 CPU y 1 GB. Sus
  dos contraseñas (la del dueño del índice y la del rol de solo lectura) existen solo como **secretos de Docker**: no
  están en la imagen, en `compose.yaml` ni en variables.
- **`pm-kb`**: el servicio web y MCP, con la misma imagen y el mismo endurecimiento que `pm`. Lee tus proyectos en
  **solo lectura** desde la carpeta que indiques en `PROYECTOS` y publica la web y el MCP solo en `127.0.0.1:8765`.
- **`pm-kb-vigilar`** (opcional, §8.10): reindexa los proyectos que le indiques cada vez que cambia un documento. Misma
  imagen y endurecimiento, proyectos en solo lectura, solo la red interna hacia la base y ningún puerto.

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

Construye la imagen `pm-kb-db:2.7.0` y, si hace falta, la imagen de pm-method del §5 (que ya trae pm-kb y sus
dependencias). **Deberías ver** la construcción sin `ERROR` y una fila `pm-kb-db:2.7.0` de unos 409 MB. Detrás de un
proxy corporativo: `pm-kb-db` usa la misma imagen base y el mismo secreto `ca_proxy` que la imagen de pm-method, así que
se construye con el comando del §12.3, punto 2, cambiando `-f docker/Dockerfile -t pm-method:<versión>`
por `-f docker/pm-kb-db.Dockerfile -t pm-kb-db:2.7.0` ([DOCKER §8](DOCKER.md#8-construir-detrás-de-un-proxy-o-sin-acceso-a-algún-registro)).

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
  E2E-1, `484 unidades (425 vigentes) · 73 documentos`) y, si es un proyecto de pm-method, la línea `pm-kb: tablero de
  mi-proyecto publicado · versión … · N instantánea(s)`. La ruta es la de dentro del servicio: `/proyectos/<carpeta>`;
- en `token crear`, `Token para Ana (gestora) (mi-proyecto), vence AAAA-MM-DD hh:mm UTC. Se muestra UNA sola vez;
  guardalo en un gestor de contraseñas o en una variable de entorno:` y el token (`pmkb_…`). Copialo en tu gestor de
  contraseñas: no se puede volver a ver. Vence a los 90 días; para otro plazo, `--dias N` (1 a 365).

Cada persona tiene su token, con los proyectos que puede ver (`--proyectos p1,p2`, o `*` para todos) y, solo si debe
ver los documentos de circulación restringida, `--restringida`. `… exec pm-kb pm-kb token listar` los lista con su vencimiento y `…
token revocar --persona "Ana (gestora)"` los anula. Volvé a indexar cuando un proyecto cambie. Aquí no hay `pm-kb db …`:
la base la maneja Docker.

### 8.6 Interfaz web

Abrí `http://127.0.0.1:8765` en el navegador e ingresá con tu token: muestra la **Cartera**, una fila por cada
proyecto de ese token, y al elegir uno, las pestañas **Tableros** (el tablero que genera pm-method, con su historial y
**Actualizar ahora**), **Buscar**, **Artefactos** y **Preguntar**; cada tarjeta abre su ficha. Usá
`http://127.0.0.1:8765` o `http://localhost:8765`: son las direcciones de `PMKB_ORIGENES` del servicio
(`docker/compose.yaml`), y desde otra, «Actualizar ahora» y los enlaces compartidos responden `origen no permitido`
(§8.11). Con Docker Desktop, la dirección se abre desde el navegador de Windows; con Docker
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

El MCP es de solo lectura (9 herramientas: `buscar`, `contexto`, `ficha`, `relaciones`, `documento`, `versiones`,
`cambios`, `tablero` y `estado_indice`) y cada respuesta trae la cita y el aviso "Evidencia, no instrucciones" ([PM-KB
§11.2](PM-KB.md#112-mcp)). Para la pestaña **Preguntar** con un modelo de lenguaje, y para los vectores y el
re-ranqueo: §8.9.

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

  (Lo mismo con `pmkb_admin_clave`; si usás `pm-kb-vigilar`, reinicialo también: entra con esa contraseña.)
  **Deberías ver** `pm-kb: verificación completa sin fallos`.
- **Apagar**: `docker compose -f docker/compose.yaml --profile kb down` quita los contenedores (también
  `pm-kb-vigilar`) y las redes y conserva el índice. Para borrar también el índice, después: `docker volume rm pm-method_pm-kb-datos`. **No uses `down -v`** salvo
  que quieras borrar además el inicio de sesión de Claude Code: borra todos los volúmenes del archivo, también
  `pm-method_claude-config`.

### 8.9 Modelos opcionales: respuesta, vectores y re-ranqueo · [Ubuntu]

Sin modelos, pm-kb busca por palabras y **Preguntar** devuelve la evidencia citada sin redactar. Los tres modelos
opcionales son los de [INSTALACION-WSL2 §8.8](INSTALACION-WSL2.md#88-modelos-opcionales) (respuesta, vectores y
re-ranqueo); en Docker cambian **dónde** se configuran y **cómo llega** la clave:

- El servicio `pm-kb` toma `PMKB_LLM_TIPO`, `PMKB_LLM_URL`, `PMKB_LLM_MODELO`, `PMKB_EMBED_URL`, `PMKB_EMBED_TIPO`,
  `PMKB_EMBED_MODELO` y `PMKB_RERANK_URL` de la terminal de Ubuntu desde la que ejecutás `up` (`docker/compose.yaml`;
  si no están, quedan vacías).
- La clave del modelo, si hace falta, va **siempre** en la variable `PMKB_CLAVE_MODELO`: `compose.yaml` fija
  `PMKB_LLM_CLAVE_VAR=PMKB_CLAVE_MODELO` y la declara sin valor, así que llega solo al servicio `pm-kb`, no queda
  escrita en ningún archivo tuyo ni del repositorio y **no** llega al contenedor `pm` (donde Claude Code tomaría una
  `ANTHROPIC_API_KEY` en lugar de tu suscripción, §9.1). Otro nombre de variable, como en WSL2, no llega al servicio.
  Docker sí la guarda en la configuración del contenedor `pm-kb` mientras ese contenedor exista (la ve quien pueda
  usar `docker`, por ejemplo con `docker inspect`, y queda en los datos del motor): al dejar de usarla, recreá el
  servicio sin ella ("Desactivar", abajo).
- `localhost` dentro del servicio es el propio contenedor, no tu Ubuntu: un servidor de modelos se alcanza por su
  **nombre** en la red de Compose (opción recomendada, abajo) o, si corre en el equipo anfitrión, como
  `host.docker.internal` (sección "Servidor fuera de Docker").

**Aplicar cualquier cambio de estas variables:** recreá solo el servicio `pm-kb` desde la terminal que las tiene (la
base y el índice no se tocan):

```bash
cd ~/pm-method
PROYECTOS=~/proyectos docker compose -f docker/compose.yaml --profile kb up -d --force-recreate --no-deps pm-kb
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb verificar | grep -E 'vectores|AVISO|verificación'
```

**Deberías ver** que Compose recrea `pm-kb`, y en `verificar` las líneas de los modelos que configuraste (abajo) y
`pm-kb: verificación completa sin fallos`. **No compartas** la salida de `docker compose … config`: muestra los
valores de las variables, también la clave.

#### Respuesta con la API de Anthropic

```bash
read -rsp "Clave del modelo: " PMKB_CLAVE_MODELO && export PMKB_CLAVE_MODELO && echo
export PMKB_LLM_TIPO=anthropic PMKB_LLM_MODELO="<nombre exacto del modelo>"
```

y aplicá con el bloque de arriba **en la misma terminal**. **Deberías ver** `Container pm-method-pm-kb-1 Started`,
`AVISO respuesta con modelo configurada (anthropic, <modelo>); no se prueba para no consumir tokens` y `pm-kb:
verificación completa sin fallos`; `… exec pm-kb pm-kb estado | tail -1` → `re-ranqueo: no · respuesta con modelo:
sí`. Usá una terminal **dedicada** a esto: si en ella cargás también `ANTHROPIC_API_KEY`, no abras ahí el contenedor
`pm`.

**Prueba con tu clave, paso a paso** (consume la API): el nombre exacto del modelo, de la lista de modelos de la
documentación de Anthropic; el bloque de arriba y "Aplicar" en una terminal nueva; en la web (§8.6), pestaña
**Preguntar**, `¿en qué fase está el proyecto?` con un proyecto indexado. **Deberías ver** una respuesta breve con
citas numeradas (`[1]`) que coinciden con la evidencia, y el modo `respuesta citada (<modelo>)`; los errores posibles
y su causa son los de INSTALACION-WSL2 §8.8.1. Al terminar: "Desactivar o quitar" (abajo), que recrea `pm-kb` sin la
clave, y cerrá la terminal (o `unset PMKB_CLAVE_MODELO`). Comprobá que no quedó: `docker inspect pm-method-pm-kb-1 |
grep -c PMKB_CLAVE_MODELO=` → `0`.

#### Modelos locales en contenedores de la red de Compose (recomendado)

Los servidores de modelos corren como contenedores propios, conectados a la red `pm-method_default` (la que Compose crea
para `pm` y `pm-kb` al levantar el perfil `kb`, §8.4) **sin publicar puertos**: `pm-kb` los alcanza por su nombre y
desde fuera de Docker no se ven. Los comandos adaptan los ejemplos oficiales (Ollama: imagen `ollama/ollama`, "CPU
only", que publica `-p 11434:11434`; TEI: imagen CPU `ghcr.io/huggingface/text-embeddings-inference:cpu-1.9`, que
escucha en el puerto 80) cambiando la publicación de puertos por `--network pm-method_default`:

```bash
# Ollama: respuesta y vectores (API compatible con OpenAI, sin clave)
docker run -d --name ollama --network pm-method_default -v ollama:/root/.ollama ollama/ollama
docker exec ollama ollama pull <modelo de respuesta>
docker exec ollama ollama pull bge-m3
export PMKB_LLM_TIPO=openai PMKB_LLM_URL=http://ollama:11434/v1 PMKB_LLM_MODELO="<modelo de respuesta>"
export PMKB_EMBED_TIPO=openai PMKB_EMBED_URL=http://ollama:11434/v1 PMKB_EMBED_MODELO=bge-m3
# TEI: re-ranqueo (y, si preferís, vectores con TEI en lugar de Ollama)
docker run -d --name pmkb-reranqueo --network pm-method_default -v pmkb-modelos:/data ghcr.io/huggingface/text-embeddings-inference:cpu-1.9 --model-id BAAI/bge-reranker-v2-m3
export PMKB_RERANK_URL=http://pmkb-reranqueo
```

Aplicá con el bloque de "Aplicar" y reindexá cada proyecto para calcular los vectores:

```bash
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb indexar --proyecto mi-proyecto --ruta /proyectos/mi-proyecto
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb estado
```

**Deberías ver** en `verificar` `OK    modelo de vectores · http://ollama:11434/v1 · dimensión <n>` y el `AVISO respuesta
con modelo configurada (openai, …)`; al indexar, `pm-kb: calculando … vectores con bge-m3 …`; en `estado`, `vectores:
bge-m3` y `re-ranqueo: sí · respuesta con modelo: sí`. Vectores con TEI en lugar de Ollama: otro contenedor
`--name pmkb-vectores … --model-id BAAI/bge-m3`, con `PMKB_EMBED_TIPO=tei` y `PMKB_EMBED_URL=http://pmkb-vectores`.

- **[verificar]**: las imágenes de Ollama y TEI no se pudieron descargar en el entorno de prueba; `bge-m3` como nombre
  en la biblioteca de Ollama y `BAAI/bge-reranker-v2-m3` en TEI (su lista de modelos admitidos nombra
  `bge-reranker-large` y `-base`, de la misma arquitectura) no están comprobados. Fijá una etiqueta de versión de
  `ollama/ollama` en lugar de la última.
- Esos contenedores están en la misma red que `pm`: el agente también los alcanza. No tienen el endurecimiento de los
  servicios de `compose.yaml` (raíz de solo lectura, límites): agregá `--memory`, `--cpus` y `--read-only` si tu
  organización lo exige **[verificar con cada imagen]**.
- `--profile kb down` borra la red `pm-method_default`, y no puede hacerlo con estos contenedores conectados
  **[verificar el mensaje]**: antes de `down`, quitalos con `docker rm -f ollama pmkb-reranqueo` (los modelos quedan
  en los volúmenes `ollama` y `pmkb-modelos`) y, después de `up`, repetí sus `docker run` (sin los `pull`).
- Detrás de un proxy, las descargas de modelos (Ollama y `huggingface.co` para TEI) necesitan `-e HTTPS_PROXY=…` en
  `docker run` y el certificado de la CA (§12.3) **[verificar]**.

#### Servidor fuera de Docker (en tu Ubuntu o en Windows)

Si el servidor de modelos ya corre en el equipo anfitrión, el servicio lo alcanza como `host.docker.internal`
(`PMKB_LLM_URL=http://host.docker.internal:11434/v1`, por ejemplo). Docker Desktop define ese nombre (documentación de
Docker, "Explore networking how-tos on Docker Desktop"); con Docker Engine lo agrega `compose.yaml` con el valor
especial `host-gateway` (referencia de `docker run`, opción `--add-host`), que apunta a la dirección del puente de
Docker. El servidor tiene que escuchar en una dirección que no sea solo `127.0.0.1` (Ollama escucha en
`127.0.0.1:11434` por defecto y se cambia con `OLLAMA_HOST`, según su FAQ), lo que lo expone a más que pm-kb: por eso
se recomienda la opción anterior. **[verificar]** en tu equipo, en especial con Docker Desktop y un servidor dentro de
la Ubuntu de WSL.

**Desactivar o quitar:** `unset PMKB_LLM_TIPO PMKB_LLM_URL PMKB_LLM_MODELO PMKB_EMBED_URL PMKB_EMBED_TIPO
PMKB_EMBED_MODELO PMKB_RERANK_URL PMKB_CLAVE_MODELO` y el bloque de "Aplicar" (sin vectores, reindexá);
`docker rm -f ollama pmkb-reranqueo` y `docker volume rm ollama pmkb-modelos` para borrar los servidores y los modelos
descargados.

**Verificado y no verificado** (§14): `docker compose … config` con valores ficticios (la clave llega solo a `pm-kb`,
nunca a `pm`; `host.docker.internal` queda definido), el cliente de pm-kb contra servidores locales de prueba, y el 2026-10-29
"Aplicar", "Respuesta con la API de Anthropic" y "Desactivar" con las imágenes de la versión 2.6.2 y un servidor que
imita la API de Anthropic como contenedor de la red de Compose, sí; Ollama, TEI y la API de Anthropic reales, no
**[verificar]**.


### 8.10 Mantener el índice al día: servicio `pm-kb-vigilar` · [Ubuntu]

`pm-kb-vigilar` corre `pm-kb vigilar` para cada proyecto que nombres en `KB_VIGILAR` (separados por espacios): compara
la huella de `/proyectos/<nombre>` cada 10 segundos y, si cambió un documento indexable, reindexa ese proyecto (el
nombre del proyecto en el índice es el de su carpeta). Usa la misma imagen y el mismo endurecimiento que `pm-kb`, lee
`PROYECTOS` en solo lectura, entra a la base como dueño del índice (`pmkb`, el rol que indexa) con el secreto
`pmkb_admin_clave`, está solo en la red interna `kb-interna` y no publica puertos. Como los demás servicios del perfil,
vuelve a arrancar con Docker (`restart: unless-stopped`).

1. Levantalo con la carpeta de tus proyectos y los nombres a vigilar (en la misma terminal, las dos variables):

   ```bash
   KB_VIGILAR="mi-proyecto" PROYECTOS=~/proyectos docker compose -f docker/compose.yaml --profile kb up -d pm-kb-vigilar
   docker compose -f docker/compose.yaml --profile kb ps pm-kb-vigilar
   docker compose -f docker/compose.yaml --profile kb logs --tail 5 pm-kb-vigilar
   ```

   **Deberías ver** que Compose espera a que `pm-kb-db` esté sano (`Healthy`) y arranca `Container
   pm-method-pm-kb-vigilar-1 Started`; en `ps`, `Up …` y la columna de puertos vacía; en el registro, `pm-kb: esquema
   listo …`, `pm-kb: vigilando /proyectos/mi-proyecto cada 10 s para mi-proyecto (Ctrl+C para terminar)`, `pm-kb:
   cambio detectado (huella …) · mi-proyecto reindexado · … unidades (… vigentes) · … documentos · … movimientos` y
   `pm-kb: tablero de mi-proyecto publicado …`.

2. Comprobá que reindexa ante un cambio (la nota se crea en tu carpeta, del lado de Ubuntu):

   ```bash
   echo "Nota para probar la vigilancia." > ~/proyectos/mi-proyecto/gestion/nota-vigilancia.md
   sleep 15
   docker compose -f docker/compose.yaml --profile kb logs --since 30s pm-kb-vigilar
   rm ~/proyectos/mi-proyecto/gestion/nota-vigilancia.md
   ```

   **Deberías ver** una línea nueva `pm-kb: cambio detectado (huella …) · mi-proyecto reindexado …` (al borrar la nota,
   otra más). Si tu proyecto no tiene `gestion/`, creá la nota en cualquier carpeta del proyecto.

- **Varios proyectos**: `KB_VIGILAR="mi-proyecto otro-proyecto"`; cada uno en `/proyectos/<nombre>`, con un nombre en
  minúsculas, sin espacios. **Cada cuánto**: `KB_VIGILAR_CADA=30` (segundos; 10 si no la definís). Las dos se toman de
  la terminal que ejecuta `up`: para cambiarlas, repetí el paso 1 con los valores nuevos (Compose recrea el servicio).
- **Si falla**: con `KB_VIGILAR` vacía, el registro dice `pm-kb-vigilar: falta KB_VIGILAR …`; con una carpeta que no
  está en `PROYECTOS`, `pm-kb: no existe la carpeta /proyectos/…`. En los dos casos el contenedor termina con código 1 y
  Docker lo reinicia (`ps` muestra `Restarting (1)`): corregí las variables y repetí el paso 1. Un error pasajero (la
  base reiniciándose, un archivo a medio escribir) no lo detiene: `vigilar` lo informa y reintenta en la vuelta
  siguiente. Levantá los servicios del perfil **por su nombre** (`up -d pm-kb`, `up -d pm-kb-vigilar`): `up -d` sin
  nombres arrancaría también `pm-kb-vigilar`, que sin `KB_VIGILAR` queda reiniciándose.
- **Vectores** (§8.9): si los configuraste, levantá `pm-kb-vigilar` desde una terminal con las mismas variables
  `PMKB_EMBED_*` que `pm-kb`. Los vectores ya calculados se reutilizan; los de un texto nuevo necesitan el servidor de
  vectores, y este servicio solo alcanza los contenedores de la red interna: con un servidor fuera de ella, el proyecto
  que cambió queda con búsqueda por palabras (el registro lo avisa) hasta que lo reindexes desde `pm-kb` (§8.5).
- **Detener o quitar**: `docker compose -f docker/compose.yaml --profile kb stop pm-kb-vigilar` lo detiene hasta el
  próximo `up`; `docker compose -f docker/compose.yaml --profile kb rm -s -f pm-kb-vigilar` lo quita. El índice queda
  como estaba.

### 8.11 Portal: tableros y enlaces compartidos · [Ubuntu]

La pestaña **Tableros** (§8.6) muestra el tablero que genera pm-method y las instantáneas que congela al decidir cada
puerta; `pm-kb` lo publica al indexar, con `pm-kb-vigilar` (§8.10) y con **Actualizar ahora**, sin escribir en tus
proyectos. Para que alguien lo vea sin token, `pm-kb compartir` crea un **enlace de solo lectura** a un tablero que
vence y se puede revocar. Referencia: [PM-KB §11.5 a §11.8](PM-KB.md#115-tablero-publicación-historial-y-actualizar-ahora).
Con un proyecto de pm-method indexado (§8.5; uno sin `estado.json` no tiene tablero). Verificado dentro del servicio
`pm-kb` con la imagen de esta versión (§14); la vista compartida, con `curl` y no con un navegador **[verificar]**:

1. Creá un enlace de un día al tablero actual:

   ```bash
   docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb compartir crear --proyecto mi-proyecto --dias 1 --para "prueba"
   ```

   **Deberías ver** `Enlace e-… de solo lectura al tablero actual (en vivo) de mi-proyecto, para prueba; vence
   AAAA-MM-DD hh:mm UTC. Se muestra UNA sola vez (la base guarda solo su huella); para cortarlo antes: pm-kb compartir
   revocar --id e-…` y la dirección `http://localhost:8765/v#pmkb_…`. El servicio arma la dirección con la primera de
   `PMKB_ORIGENES` (`docker/compose.yaml`, servicio `pm-kb`), y el enlace solo se abre desde una de esas direcciones.
   Para compartir con alguien de otra computadora hace falta publicar el servicio detrás de un proxy con TLS y poner
   esa dirección `https://…` primera en `PMKB_ORIGENES` ([PM-KB §8](PM-KB.md#8-configuración); sin TLS, no lo publiques
   fuera de `127.0.0.1`). Es una credencial: mandala solo a quien la tiene que ver.

2. Abrí esa dirección completa en una **ventana privada** del navegador (en la ventana normal reemplazaría tu sesión
   del §8.6). **Deberías ver** una página sin pestañas con «solo lectura · vence …», «tablero actual» y el tablero; la
   dirección queda en `…/v`, sin el token. Cada tarjeta abre su ficha; buscar, preguntar y los demás proyectos no
   están disponibles.

3. Revisá el uso y cortá el enlace:

   ```bash
   docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb compartir listar --proyecto mi-proyecto
   docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb compartir revocar --id e-…
   ```

   **Deberías ver** una línea `e-… · mi-proyecto · actual · para prueba · vigente · creado … · vence … · 1 uso(s),
   último …` y `pm-kb: 1 enlace(s) revocado(s): e-… · las sesiones abiertas con ellos se cortan en la petición
   siguiente`. Al recargar la ventana privada: «Sin sesión: abrí el enlace completo que recibiste …».

Otras formas: `--instantanea <id>` (una instantánea congelada; los ids salen en el historial de **Tableros**, o con
`tablero.py --proyecto gestion listar` en el contenedor `pm`), `--actor "<nombre o rol>"` (solo lo de esa persona según
la RACI), `--dias` de 1 a 90 (7 si no lo indicás) y `--restringida` (incluye lo de circulación restringida). Antes de
compartir fuera de la organización: [SEGURIDAD §14](SEGURIDAD.md#14-pm-kb-índice-de-conocimiento-2026-10-28)
(«Compartir fuera de la organización»).
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
- Las skills externas (§9.4) y los conectores MCP (§9.5) son opcionales; el envío a interesados por correo, Slack o
  Teams, §9.3.
- Claude Code no se actualiza solo dentro del contenedor (la imagen fija su versión): se actualiza con la imagen (§11).

### 9.3 Enviar comunicaciones a interesados desde el contenedor (opcional) · [Ubuntu] y [Contenedor]

**Para qué sirve.** La capa de canales (`envios.py`) envía a los interesados las comunicaciones aprobadas por `.eml`,
correo SMTP o webhooks de Slack o Teams y las registra en `envios.csv`. El procedimiento completo (agregar un
interesado, crear, aprobar, simular, enviar y registrar, con lo que deberías ver en cada paso) es el de
[INSTALACION-WSL2 §5.5](INSTALACION-WSL2.md#55-enviar-comunicaciones-a-interesados-eml-correo-slack-o-teams-opcional),
con dos diferencias: los comandos se escriben en **[Contenedor]**, con `$PM_METHOD_DIR` en lugar de `~/pm-method`, y
las credenciales se cargan **antes de abrir el contenedor**, en la terminal de Ubuntu.

**Por qué en Ubuntu.** `docker/compose.yaml` declara en el servicio `pm` las variables que lee `envios.py`
(`PM_SMTP_HOST`, `PM_SMTP_PUERTO`, `PM_SMTP_TLS`, `PM_SMTP_USUARIO`, `PM_SMTP_CLAVE`, `PM_SMTP_REMITENTE`,
`PM_SLACK_WEBHOOK_URL` y `PM_TEAMS_WEBHOOK_URL`) **por nombre, sin valor**: Compose copia al contenedor las que existan
en la terminal desde la que lo abrís y no crea las demás. Así ninguna credencial queda escrita en `compose.yaml`, en
un `.env`, en la imagen ni en el proyecto, y desaparece al cerrar esa terminal. Lo que exportes **dentro** del
contenedor también sirve, pero se pierde al salir.

**Paso 1 · Sin configuración: `.eml`.** No necesita variables. En **[Contenedor]**, sobre tu proyecto (§7.2):

```bash
EV=$PM_METHOD_DIR/skills/pm-integraciones/scripts/envios.py
python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/registro.py --proyecto gestion agregar stakeholders --campo "nombre=<tu nombre>" --campo poder=bajo --campo interes=alto --campo "correo=<tu dirección de correo>"
printf 'Prueba de envío de pm-method.\n' > aviso.md
python3 $EV --proyecto gestion nuevo --origen aviso.md --audiencia ST-001 --asunto "Prueba de canales"
C=gestion/03-control/comunicaciones/$(date +%F)-prueba-de-canales
sed -i '/^## Contenido base/d' $C/mensaje-01-correo-st-001.md
python3 $EV --proyecto gestion aprobar $C --por "Gestor: <tu nombre>"
python3 $EV --proyecto gestion enviar $C --modo eml --confirmar
ls $C/eml
```

**Deberías ver** lo mismo que en INSTALACION-WSL2 §5.5, paso 1 (`ST-001`, `… · 1 destinatarios`, `1 mensaje(s)
aprobados …`, `… eml-generado · EN-001` y el archivo `.eml`). El `.eml` queda en tu proyecto (`/trabajo`), así que lo
abrís desde Ubuntu o Windows (§7.2). La carpeta lleva la fecha del contenedor (la imagen no fija zona horaria, así que
es la de UTC): si no la encuentra, usá la ruta que mostró `nuevo`.

**Paso 2 · SMTP o webhooks.** En **[Ubuntu]**, cargá solo lo que vas a usar y abrí el contenedor **desde la misma
terminal**:

```bash
export PM_SMTP_HOST="<servidor SMTP>" PM_SMTP_REMITENTE="<tu dirección de correo>" PM_SMTP_PUERTO=587 PM_SMTP_TLS=starttls
read -rp "Usuario SMTP: " PM_SMTP_USUARIO && export PM_SMTP_USUARIO
read -rsp "Clave SMTP: " PM_SMTP_CLAVE && export PM_SMTP_CLAVE && echo
read -rsp "URL del webhook de Slack: " PM_SLACK_WEBHOOK_URL && export PM_SLACK_WEBHOOK_URL && echo
PROYECTO=~/proyectos/mi-proyecto docker compose -f ~/pm-method/docker/compose.yaml run --rm pm
```

y en **[Contenedor]**:

```bash
python3 $PM_METHOD_DIR/skills/pm-integraciones/scripts/envios.py --proyecto gestion verificar --modo smtp
python3 $PM_METHOD_DIR/skills/pm-integraciones/scripts/envios.py --proyecto gestion verificar --modo slack-webhook
```

**Deberías ver** `   PM_SMTP_HOST: definida` … y `Listo para enviar.` en cada modo cargado (`verificar` nunca muestra
los valores). Si dice `no definida` para todas, abriste el contenedor desde otra terminal. Los envíos reales siguen los
pasos 2 y 3 de INSTALACION-WSL2 §5.5 (con `$PM_METHOD_DIR`). Para el webhook de Teams, la variable es
`PM_TEAMS_WEBHOOK_URL`. Con el atajo `pm-docker` de §7.1 funciona igual (es el mismo comando).

**Si falla:** además de la tabla de INSTALACION-WSL2 §5.5:

| Síntoma | Qué hacer |
|---|---|
| `verificar` dice `no definida` aunque las cargaste | se cargaron en otra terminal o después de abrir el contenedor: salí (`exit`), cargalas y abrilo de nuevo |
| `certificate verify failed` hacia el servidor SMTP o el webhook | la red inspecciona HTTPS y la imagen no trae tu CA: abrí el contenedor como en §12.3, punto 3, agregando `-e SSL_CERT_FILE=/etc/pm-method/ca-red.crt` (Python usa ese archivo; `NODE_EXTRA_CA_CERTS` es solo para Node) **[verificar en tu red]** |
| tiempo agotado hacia el servidor SMTP | la red de Docker sale por la de tu equipo: si el puerto SMTP está bloqueado, consultá a TI (el proxy HTTP no se usa para SMTP) |
| `pm-sin-red` | recibe las mismas variables, pero sin red solo sirve `verificar` y `--modo eml` |

**Desactivar:** salí del contenedor y `unset PM_SMTP_HOST PM_SMTP_REMITENTE PM_SMTP_PUERTO PM_SMTP_TLS PM_SMTP_USUARIO
PM_SMTP_CLAVE PM_SLACK_WEBHOOK_URL PM_TEAMS_WEBHOOK_URL` en Ubuntu (o cerrá la terminal); borrá los webhooks que ya no
uses.

**Verificado y no verificado** (§14): que Compose pase esas variables al servicio `pm` (y a `pm-sin-red`) solo cuando
existen en el host, con `docker compose … config` y valores ficticios; el paso 1 y los envíos contra servidores
locales, con el mismo `envios.py` fuera del contenedor. Dentro del contenedor no se ejecutaron en esta verificación, ni
con servidores reales **[verificar]**.

### 9.4 Skills externas para visuales y Office (opcional) · [Contenedor]

Qué son, requisitos y comandos: [INSTALACION-WSL2 §6.8](INSTALACION-WSL2.md#68-skills-externas-para-visuales-y-office-opcional--ubuntu)
e [INSTALACION §6.1](INSTALACION.md#61-skills-externas-opcionales-diagramas-y-office). Se instalan **dentro del
contenedor**, con los mismos comandos (`claude plugin marketplace add …` y `claude plugin install …`, o `npx skills
add … -y` en `/trabajo`), y se declaran con `python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/estado.py
--proyecto gestion integracion diagramas=…`. Lo propio del contenedor:

| Tema | En el contenedor |
|---|---|
| Dónde quedan | plugins y copias de usuario (`-g`), en `~/.claude` = el volumen `pm-method_claude-config` (`CLAUDE_CONFIG_DIR`): persisten (en una ejecución nueva del contenedor, `claude plugin list` sigue mostrando el plugin); copias sin `-g`, en `/trabajo/.claude/skills/` (tu proyecto): persisten. La sanidad (INS-03) mira los dos lugares |
| Node | el de la imagen (22.22), suficiente para `npx skills` |
| `npx` | descarga en `~/.npm`, que es temporal: cada `npx skills …` vuelve a descargar |
| diagram-design | la copia de `/opt/skills-externas/diagram-design` es solo para las pruebas del paquete: para usarla en Claude Code, instalala igual |
| archify | `export ARCHIFY_CHROME=/usr/local/bin/chromium-headless-shell ARCHIFY_CHROME_NO_SANDBOX=1` antes de `claude` (el navegador de la imagen; la segunda variable, opción de archify, lo abre con `--no-sandbox`, porque el contenedor no le permite su aislamiento). Sin ella, su `finalize` falla en `browser-check` con `viewer/browser-check-runtime: browser-check could not complete its Chrome inspection.`; con las dos, `validate`, `deliver`, `check` y `browser-check` en `pass`. Con `ARCHIFY_CHROME` definida, la sanidad ya no avisa que falta Chrome |
| diagram-design | su PNG opcional (`scripts/export_png.py`) funciona con el Playwright y el navegador de la imagen |
| visual-explainer | la imagen no trae `playwright-core`: su `kit/render.mjs` escribe la página y omite la comprobación visual (`Visual check skipped: playwright-core is not installed`) |
| Office | la imagen **no** trae LibreOffice, `pandoc` ni el paquete npm `docx`, y su raíz es de solo lectura: las skills de Office no tienen todo lo que piden. En Docker, usá `export=scripts` (`exportar.py`) |
| Red corporativa | `npx` y `claude plugin marketplace add` necesitan el certificado de §12.3, punto 3, **y además** `-e GIT_SSL_CAINFO=/etc/pm-method/ca-red.crt` al abrir el contenedor: los dos clonan el repositorio con git, que no usa `NODE_EXTRA_CA_CERTS`. Sin esa variable, `claude plugin marketplace add` termina con `✘ Failed to add marketplace: … SSL certificate verification failed: certificate signer not trusted.` y `npx skills add` con `Installation failed` |

**Deberías ver** la misma salida de INS-03 que en INSTALACION-WSL2 §6.8, paso 2. **Desinstalar:** `claude plugin
uninstall …` o `npx skills remove …` dentro del contenedor, y volver a `diagramas=mermaid`. Borrar el volumen
`pm-method_claude-config` (§13.1) quita también los plugins. Verificado el 2026-10-29 con `pm-method:2.6.2` (§14.2):
instalación, persistencia, INS-03, archify con el navegador de la imagen, PNG de diagram-design y desinstalación; el uso
en Claude, **[verificar]**.

### 9.5 Conectores MCP de la organización (opcional) · [Contenedor] y [Claude]

Qué son, comandos y cómo declarar la capacidad: [INSTALACION-WSL2
§6.9](INSTALACION-WSL2.md#69-conectores-mcp-de-la-organización-jira-confluence-okr-y-otros-opcional--ubuntu-y-claude).
Se agregan dentro del contenedor con los mismos `claude mcp add …`. Lo propio del contenedor:

- **Dónde quedan:** Claude Code guarda los servidores (y sus credenciales OAuth o de cabecera) en `.claude.json`, que
  con `CLAUDE_CONFIG_DIR` queda dentro de esa carpeta: el volumen `pm-method_claude-config`. Comprobado con Claude Code
  2.1.312 fuera del contenedor (`File modified: <CLAUDE_CONFIG_DIR>/.claude.json [project: …]`); dentro, con la 2.1.304
  de la imagen, **[verificar]** que persista entre ejecuciones.
- **Autenticar por OAuth** (`/mcp`): el navegador de Windows no puede volver al `localhost` del contenedor, igual que
  en el inicio de sesión (§9.1) **[verificar si `/mcp` ofrece pegar un código]**. Si el proveedor admite un token
  personal: `claude mcp add --transport http <nombre> <url> --header "Authorization: Bearer <token>"` (queda en el
  volumen, no en el proyecto).
- **Servidores por `npx`** (stdio): se vuelven a descargar en cada ejecución (`~/.npm` temporal) y necesitan red.
- **Servidores que corren en tu equipo** (fuera de Docker): `localhost` dentro del contenedor no es tu equipo
  **[verificar `host.docker.internal` desde el servicio `pm`]**.
- **Red corporativa:** abrí el contenedor como en §12.3, punto 3.

**Quitar:** `claude mcp remove <nombre>` dentro del contenedor (o borrar el volumen, que quita todo). **[verificar]**:
ningún conector de terceros se probó en vivo.

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

### 11.1 pm-kb (perfil `kb`)

Si usás pm-kb (§8), después del `git pull` reconstruí también la imagen de la base y recreá los dos servicios; el
índice y los tokens se conservan en el volumen `pm-method_pm-kb-datos`:

```bash
cd ~/pm-method
docker compose -f docker/compose.yaml --profile kb build
PROYECTOS=~/proyectos docker compose -f docker/compose.yaml --profile kb up -d pm-kb
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb verificar | tail -1
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb indexar --proyecto mi-proyecto --ruta /proyectos/mi-proyecto
docker image ls pm-kb-db
```

**Deberías ver** la construcción de `pm-kb-db:<versión nueva>` y de `pm-method:<versión nueva>` sin `ERROR`, que `up`
recrea `pm-kb-db` y `pm-kb` con las imágenes nuevas, `pm-kb: verificación completa sin fallos` y el proyecto indexado
de nuevo (reindexá cada proyecto: la versión nueva puede indexar distinto). Borrá la imagen anterior con `docker image
rm pm-kb-db:<versión anterior>`. Si cargaste modelos (§8.9), ejecutá `up` desde una terminal con sus variables.

**Si cambia la versión mayor de PostgreSQL** de la imagen (por ejemplo, de 18 a 19), los datos del volumen no sirven y
`pm-kb-db` no queda sano (`docker compose -f docker/compose.yaml --profile kb logs pm-kb-db` muestra el error de
PostgreSQL **[verificar el mensaje]**). El índice no se migra: se rehace ([PM-KB
§14](PM-KB.md#14-operación)):

```bash
docker compose -f docker/compose.yaml --profile kb down
docker volume rm pm-method_pm-kb-datos
PROYECTOS=~/proyectos docker compose -f docker/compose.yaml --profile kb up -d pm-kb
docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb indexar --proyecto mi-proyecto --ruta /proyectos/mi-proyecto
```

y creá de nuevo los tokens de cada persona (§8.5): se borraron con el volumen. **No uses `down -v`**: borraría también
el inicio de sesión de Claude Code. **[verificar]**: la actualización de pm-kb entre dos versiones y el cambio de
versión mayor de PostgreSQL no se ejecutaron en el entorno de prueba.

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
   secretos, así que se construye con `docker build` (mismo resultado: la imagen `pm-method:2.7.0` que usa Compose):

   ```bash
   cd ~/pm-method
   docker build -f docker/Dockerfile -t pm-method:2.7.0 \
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

   Lo que clona con git dentro del contenedor (marketplaces de plugins, `npx skills add`, §9.4) necesita además `-e
   GIT_SSL_CAINFO=/etc/pm-method/ca-red.crt` antes de `pm`: git no usa `NODE_EXTRA_CA_CERTS` (comprobado en §14.2).
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
docker image rm pm-method:2.7.0
docker volume rm pm-method_claude-config
docker builder prune -f
rm -rf ~/pm-method ~/pm-pruebas-docker
```

Quita la imagen, la sesión guardada de Claude Code, la caché de construcción, el clon y la evidencia de las pruebas.
**Tus proyectos** (`~/proyectos/…`) no se tocan: son Markdown, CSV y JSON legibles sin el paquete. Si creaste el atajo
de §7.1, quitalo: `sed -i '/alias pm-docker=/d' ~/.bashrc`.

Si usaste pm-kb (§8), antes de borrar el clon: `docker compose -f ~/pm-method/docker/compose.yaml --profile kb down`,
`docker image rm pm-kb-db:2.7.0` y `docker volume rm pm-method_pm-kb-datos` (el índice; las contraseñas de
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

### 14.1 Lista de aceptación en tu equipo

Al terminar, comprobá en orden. Las filas "opcional" corresponden solo a lo que instalaste.

| # | Dónde · comando | Resultado esperado |
|---|---|---|
| 1 | [Ubuntu] `docker version` y `docker compose version` | `Client:` y `Server:`; Compose 2 o posterior (§2.4 o §3.5) |
| 2 | [Ubuntu] `docker image ls pm-method` y `docker run --rm pm-method:2.7.0 claude --version` | la imagen de la versión que construiste; `2.1.304 (Claude Code)` (§5) |
| 3 | [Ubuntu] `cd ~/pm-method && docker compose -f docker/compose.yaml run --rm pruebas python3 /opt/pm-method/scripts/validar_paquete.py` | `OK` (§6.1) |
| 4 | [Ubuntu] `docker compose -f docker/compose.yaml run --rm pruebas` | `Resultado: todas las pruebas OK` (§6.2) |
| 5 | [Contenedor] `id` y `echo $PM_METHOD_DIR` | `uid=1000(pm) …` y `/opt/pm-method` (§7.1) |
| 6 | [Contenedor] `claude auth status` | `"loggedIn": true` (§9.1) |
| 7 | [Ubuntu] la prueba de humo de §9.2 | la guía de pm-method, sin errores de hooks |
| 8 | (opcional, §8) [Ubuntu] `docker compose -f docker/compose.yaml --profile kb ps` y `… exec pm-kb pm-kb verificar \| tail -1` | los dos servicios `(healthy)`; `pm-kb: verificación completa sin fallos` |
| 9 | (opcional, §8.7) [Contenedor] `claude mcp list` | `pm-kb: http://pm-kb:8765/mcp (HTTP) - √ Connected` |
| 10 | (opcional, §8.9) [Ubuntu] `docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb estado \| tail -1` | `re-ranqueo: sí\|no · respuesta con modelo: sí\|no`, según lo que configuraste |
| 11 | (opcional, §8.10) [Ubuntu] `docker compose -f docker/compose.yaml --profile kb ps pm-kb-vigilar` | `Up …`, sin puertos |
| 12 | (opcional, §9.3) [Contenedor] `python3 $PM_METHOD_DIR/skills/pm-integraciones/scripts/envios.py --proyecto gestion verificar --modo smtp` (o `slack-webhook`, `teams-webhook`) | `Listo para enviar.` |
| 13 | (opcional, §9.4) [Contenedor] `python3 $PM_METHOD_DIR/skills/pm-estado-proyecto/scripts/sanidad.py --proyecto gestion \| grep INS-03` | `INFO  INS-03 … instalada: invocar como …` por skill declarada |
| 14 | (opcional, §9.5) [Contenedor] `claude mcp list` | cada conector agregado, autenticado y `√ Connected` |
| 15 | (opcional, §10) [Contenedor] `python3 $PM_METHOD_DIR/skills/pm-bmad-puente/scripts/bmad.py --proyecto gestion detectar` | `v6`, `6.12.4`, `soportada` |
| 16 | (opcional, §8.11) [Ubuntu] `docker compose -f docker/compose.yaml --profile kb exec pm-kb pm-kb compartir listar` | tus enlaces con su estado (`vigente`, `vencido` o `revocado`), vencimiento y usos; ninguno `vigente` que ya no haga falta |

Si todas las filas de lo que instalaste están bien, el entorno está completo.

### 14.2 Verificación registrada

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
imagen `pm-method:2.7.0` se repitieron el 2026-10-30 la comprobación de §5, §6.1, §6.2 y §12.7 (filas de abajo).
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
| §5 comprobación | `pm-method:2.7.0`, 3,33 GB (845 MB de contenido); `2.1.304 (Claude Code)` |
| §6.1 prueba rápida | `Skills: 39 (33 invocables por el modelo, listado 6966 caracteres) · Agentes: 6` y `OK` (2 s) |
| §6.2 batería completa | `Resultado: todas las pruebas OK` en dos corridas seguidas (≈ 35 min cada una con `pm-method:2.7.0`, que incluye la suite de variantes) |
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
| §12.7 Chromium | `OK · 131 bloques Mermaid · 0 error(es)` (141 s dentro de la batería del §6.2, `pm-method:2.7.0`) |
| README, camino Docker | el contenedor sobre `PROYECTO` y `claude` en `/opt/node-tools/node_modules/.bin/claude` |
| §13.1 desinstalar | imagen, volumen, caché, clon, evidencia y atajo quitados; `~/proyectos` intacto |

**pm-kb (§8)**, verificación del 2026-10-28, repetida el 2026-10-30 con las imágenes 2.7.0 de §8.3 a §8.7 (§8.8, el 2026-10-29 con las imágenes 2.6.2), en el mismo tipo de entorno (Linux x86_64, Docker Engine), con las
imágenes `pm-kb-db:2.7.0` y `pm-method:2.7.0` construidas sobre la base local de [DOCKER
§11.1](DOCKER.md#111-construir-sin-acceso-a-los-registros-de-contenedores-ni-a-la-cdn-de-playwright) y el proyecto
del caso E2E-1 en `PROYECTOS`:

| Paso | Resultado |
|---|---|
| §8.2 `kb-preparar.sh` | los dos secretos creados; en la segunda ejecución, `existe: … (no se modifica)` |
| §8.3 construcción | `pm-kb-db:2.7.0` (409 MB) con PostgreSQL 18.6, pgvector 0.8.1 y `tini` de Ubuntu 26.04 |
| §8.4 `up -d pm-kb` y `ps` | `pm-kb-db` sano antes de arrancar `pm-kb`; los dos `(healthy)`, `127.0.0.1:8765->8765/tcp`; en el registro de `pm-kb`, `escuchando en 0.0.0.0:8765; ingresar con un token personal` |
| §8.5 `verificar`, `indexar`, `token crear` | 14 `OK` y `verificación completa sin fallos`; `portal-socios indexado · 444 unidades (399 vigentes) · 65 documentos (1 con varias versiones) · 511 relaciones · 115 entradas de historia` (la evidencia de E2E-1 de la versión 2.7.0 da 444 unidades y 399 vigentes, [PM-KB §12](PM-KB.md#12-pruebas-y-medición); esta corrida en Docker no se repitió con ella); el token de "Ana (gestora)" |
| §8.6 web | ingreso con el token por el formulario de `http://127.0.0.1:8765` (303 y cookie); `/salud` → `ok` |
| §8.7 desde el contenedor `pm` | `http://pm-kb:8765/salud` responde y `pm-kb-db` no se resuelve (red interna); MCP en `http://pm-kb:8765/mcp` con `Authorization: Bearer <token>` |
| §8.8 contraseñas y apagar | secreto del lector sobrescrito, `restart` y `verificar` sin fallos; `down` quita contenedores y redes y conserva `pm-method_pm-kb-datos`; con otro nombre de proyecto de Compose, `down -v` quitó el volumen del índice y el de `claude-config` |
| servicio `pm-kb` | usuario `uid=1000(pm)`; `/proyectos` de solo lectura (`Read-only file system`); `pm-kb db estado` responde que no corresponde con Docker |
| §8.11 portal y enlaces | `pm-kb tablero` publica el tablero (`versión 1`, corte, fase, etapa, atención y próxima puerta); `pm-kb enlaces` lista una cita a una ruta movida con la acción; `compartir crear --dias 1 --para "prueba"` → `Enlace e-… de solo lectura al tablero actual (en vivo) …` y la URL `http://localhost:8765/v#…`; el canje por POST con `Origin` de `PMKB_ORIGENES` → 200 (otro origen → 403) y la cookie no contiene el token; con esa sesión, `/api/tablero` 200 y `/api/buscar` 403; `compartir listar` con `1 uso(s), último …`; `compartir revocar --id e-…` → la misma sesión responde 401; MCP desde el contenedor `pm`: 9 herramientas |

**Vigilancia del índice (§8.10)**, comprobación del 2026-10-30 con Docker Engine 29.8.2 y una copia del proyecto de
E2E-1 en `PROYECTOS`, en dos tiempos: primero con otro nombre de proyecto de Compose (`-p`) y el código de `pm-kb/` y de
`skills/` montado en solo lectura sobre las imágenes anteriores (filas de abajo); después, con las imágenes
`pm-method:2.7.0` y `pm-kb-db:2.7.0` construidas con esta versión: `up -d pm-kb-vigilar` con `KB_VIGILAR=portal-socios`
y `KB_VIGILAR_CADA=5` → `Up`, `uid=1000(pm)`, `/proyectos` de solo lectura, `cambio detectado … · portal-socios
reindexado` al arrancar y de nuevo al agregar una nota en la carpeta (445 unidades), cada vez con `tablero de
portal-socios publicado`.

| Paso | Resultado |
|---|---|
| `config` con el perfil `kb` | válido; `pm-kb-vigilar` con `read_only`, `cap_drop: [ALL]`, `no-new-privileges`, solo `kb-interna`, sin `ports`, secreto `pmkb_admin_clave` y `/proyectos` de solo lectura |
| paso 1 | `pm-kb-db` `Healthy` antes de arrancar `pm-kb-vigilar`; `Up`, sin puertos; `pm-kb: esquema listo …`, `pm-kb: vigilando /proyectos/portal-socios cada 3 s …` (con `KB_VIGILAR_CADA=3`) y `portal-socios reindexado · 444 unidades (399 vigentes) · 65 documentos · 0 movimientos` |
| paso 2 | una línea del README cambiada en la copia → `cambio detectado (huella …) · portal-socios reindexado` en la vuelta siguiente |
| aislamiento | usuario `uid=1000(pm)`; `/proyectos` de solo lectura (`Read-only file system`); sin `PMKB_CLAVE_MODELO` ni el secreto del lector; sin salida a internet (`Temporary failure in name resolution`); red `internal=true` |
| dos proyectos | `KB_VIGILAR="portal-socios portal-dos"`: un `vigilando` por proyecto y solo `portal-dos` reindexado al cambiar su carpeta |
| si falla | `KB_VIGILAR` vacía → `pm-kb-vigilar: falta KB_VIGILAR …` y código 1; carpeta inexistente → `pm-kb: no existe la carpeta /proyectos/no-existe` y código 1 |
| detener | `stop` en menos de un segundo; `down -v` con el nombre de proyecto de la prueba quitó sus contenedores, su red y su volumen |

**Opcionales (§8.9, §9.3 a §9.5 y §11.1)**, comprobación del 2026-10-29 con Docker Engine 29.8.2 y Compose 5.5.1, sin
levantar contenedores (el motor estaba reservado para otras pruebas) ni instalar nada:

| Paso | Resultado |
|---|---|
| `docker/compose.yaml` | `docker compose -f docker/compose.yaml config --quiet`, también con `--profile kb --profile sin-red`: sin errores |
| §9.3 variables de la capa de canales | `config` con valores ficticios en el host: `pm` y `pm-sin-red` reciben solo las `PM_*` definidas (las demás quedan declaradas sin valor), `pm-kb` y `pruebas` ninguna. Es el mecanismo que la fila "§9.1 clave de API solo en memoria" comprobó dentro del contenedor |
| §9.3 pasos 1 y 2 | el bloque del paso 1 y los dos `verificar`, fuera del contenedor con `PM_METHOD_DIR` apuntando al clon: las salidas de INSTALACION-WSL2 §5.5 (`eml-generado · EN-001`, `Listo para enviar.`) |
| §8.9 variables de los modelos | `config` con valores ficticios: `PMKB_CLAVE_MODELO` llega solo a `pm-kb`, nunca a `pm`; `PMKB_LLM_CLAVE_VAR: PMKB_CLAVE_MODELO`; `extra_hosts: host.docker.internal=host-gateway`; la red de Compose se llama `pm-method_default` |
| §8.9 cliente de los modelos | el de pm-kb contra servidores locales de prueba (INSTALACION-WSL2 §12, fila §8.8) |
| §9.5 dónde quedan los MCP | con `CLAUDE_CONFIG_DIR` en una carpeta de prueba y Claude Code 2.1.312, fuera del contenedor: `claude mcp add` escribe en `<CLAUDE_CONFIG_DIR>/.claude.json` |

**Opcionales dentro de los contenedores (§8.9 y §9.4)**, ejecución del 2026-10-29 con Docker Engine 29.8.2, las
imágenes `pm-method:2.6.2` y `pm-kb-db:2.6.2` y un usuario con UID 1000 dueño de la carpeta del proyecto. Para no
tocar los volúmenes de otras pruebas, Compose corrió con otro nombre de proyecto (`-p`), por eso la red y los
contenedores se llamaron distinto; el contenedor `pm` usó la red del anfitrión (un archivo de Compose adicional), porque
el proxy de prueba escucha en `127.0.0.1`, y se abrió como en §12.3, punto 3, con `-e HTTPS_PROXY`. Los comandos de
[Contenedor] de §9.4 (los de INSTALACION-WSL2 §6.8 con `$PM_METHOD_DIR`) y los bloques de §8.9 "Aplicar", "Respuesta con
la API de Anthropic" y "Desactivar o quitar" se ejecutaron tal cual; la clave fue un valor ficticio leído con `read -rsp`
y `PMKB_LLM_URL` apuntó a un servidor que imita `POST /v1/messages`, como contenedor de la red de Compose.

| Paso | Resultado |
|---|---|
| §9.4 sin `GIT_SSL_CAINFO` | `✘ Failed to add marketplace: … SSL certificate verification failed: certificate signer not trusted.` y `npx skills add` → `Installation failed` (fila "Red corporativa" corregida) |
| §9.4 con `-e GIT_SSL_CAINFO=/etc/pm-method/ca-red.crt` | `Successfully added marketplace`, `Successfully installed plugin: diagram-design@diagram-design (scope: user)`, visual-explainer y archify copiadas en `/trabajo/.claude/skills/` |
| §9.4 persistencia | en una ejecución nueva del contenedor, `claude plugin list` muestra `diagram-design@diagram-design` · `Version: 2.6.136` · `✔ enabled`; las copias siguen en el proyecto; INS-03 con las tres skills |
| §9.4 archify | con `ARCHIFY_CHROME=/usr/local/bin/chromium-headless-shell`: sin el aviso de Chrome en la sanidad; `finalize` de un ejemplo de archify falla en `browser-check` (`viewer/browser-check-runtime`) y, con `ARCHIFY_CHROME_NO_SANDBOX=1`, pasa las cuatro puertas (fila corregida) |
| §9.4 diagram-design y visual-explainer | `export_png.py` produce el PNG con el Playwright de la imagen; `kit/render.mjs` escribe la página y omite la comprobación visual sin `playwright-core` |
| §9.4 desinstalar | `Successfully uninstalled plugin`, `Successfully removed marketplace`, `npx skills remove … -y` → `Done!`; `/trabajo/.claude/skills` vacía |
| §8.4 y §8.5 | `pm-kb-db` y `pm-kb` `(healthy)`; 14 `OK` (PostgreSQL 18.6 `server_version_num 180006`, pgvector 0.8.1); proyecto del §7.2 indexado; token creado |
| §8.9 Anthropic y "Aplicar" | `Started`; `AVISO respuesta con modelo configurada (anthropic, modelo-de-prueba)`; `estado` → `respuesta con modelo: sí`; la clave llega a `pm-kb` y no a `pm`; "Preguntar" por la web → `respuesta citada (modelo-de-prueba)`, con `[cita inválida]` en lugar de una cita inexistente; el servidor recibió `x-api-key` y `anthropic-version: 2023-06-01`; la clave no quedó en el repositorio ni en la carpeta de proyectos, pero sí en `docker inspect` del contenedor `pm-kb` (texto de §8.9 corregido) |
| §8.9 "Desactivar o quitar" | `Started`; sin `AVISO`, `respuesta con modelo: no`; "Preguntar" → `evidencia (sin modelo configurado)`; `docker inspect … \| grep -c PMKB_CLAVE_MODELO=` → `0` |

**Queda por comprobar en tu equipo [verificar]** (cada paso dice cómo): todo lo de Windows (§1, §2, los rótulos de
Docker Desktop, la licencia que corresponde a tu organización y la integración con Ubuntu), la instalación de Docker
Engine dentro de Ubuntu (§3.2 a §3.4, con `download.docker.com` bloqueado en la red de prueba) y systemd en WSL (§3.1),
`hello-world` (§2.4 y §3.5), la descarga del ZIP (§4.2), `docker compose … build pm` con acceso a Docker Hub (§5), el
inicio de sesión y la primera conversación con una cuenta (§9), el proxy del motor de Docker y el uso con un proxy
obligatorio (§12.3), otro UID (§12.5) y las desinstalaciones de Docker (§13.2 y §13.3); de pm-kb, la web y el MCP
desde Windows o desde Ubuntu fuera del contenedor (§8.6 y §8.7), los modelos opcionales con Ollama, TEI o la API real de
Anthropic (§8.9), la actualización entre versiones y el cambio de versión mayor de PostgreSQL
(§11.1) y el borrado de su imagen y su volumen (§13.1); de los opcionales del contenedor, el envío y `verificar` dentro
del contenedor y con servidores reales (§9.3), el uso de las skills externas en Claude (§9.4), y los conectores MCP
con autenticación real (§9.5).

---

## 15. Seguridad

- **Credenciales solo en su lugar**: el inicio de sesión de Claude Code y las credenciales de los conectores MCP en el
  volumen `pm-method_claude-config` (§9.5); una clave de API (§9.1), las de la capa de canales (§9.3) y la del modelo
  de pm-kb (`PMKB_CLAVE_MODELO`, §8.9), en la memoria de la terminal de Ubuntu, cargadas con `read -rsp`: `compose.yaml`
  las declara por nombre, sin valor. No compartas la salida de `docker compose … config`, que muestra esos valores. El
  motor de Docker guarda las variables de cada contenedor mientras exista (`docker inspect`): `pm` se borra al salir
  (`run --rm`); `pm-kb` sigue en marcha, así que al dejar de usar la clave del modelo recreálo sin ella (§8.9).
  Nunca en la imagen (`--build-arg`, `ENV`), en `compose.yaml`, en un
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
