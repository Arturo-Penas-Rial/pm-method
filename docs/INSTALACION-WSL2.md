# Instalación en Windows con WSL2 · pm-method 2.5.0

Guía paso a paso para dejar en una PC con Windows un entorno **estable, completo y verificado** para usar pm-method
dentro de WSL2 (Ubuntu), por uno de dos caminos: **A · Claude Code** (recomendado) o **B · Hermes Agent**. Pensada para
quien no programa: cada paso dice dónde se escribe, qué comando copiar y qué deberías ver.

Es uno de los **dos caminos de instalación** de pm-method: aquí instalás las herramientas directamente en Ubuntu. El
otro camino, independiente de este, es usar pm-method dentro de un **contenedor Docker** que ya trae todo:
[INSTALACION-DOCKER](INSTALACION-DOCKER.md). Cómo elegir: §0.

EN: *step-by-step guide to install pm-method on Windows through WSL2 + Ubuntu 24.04 LTS, either with Claude Code
(recommended: skills, agents and hooks) or with Hermes Agent (skills and scripts, no hooks or named subagents). Every
block ends with a check and its expected output; troubleshooting, uninstall and security at the end.*

> **Cómo leer esta guía**
> - Cada bloque indica dónde se escribe: **[Windows]** (PowerShell), **[Ubuntu]** (la terminal de WSL) o **[Claude]**
>   (dentro de una sesión de `claude`).
> - Copiá y pegá los comandos. En la terminal de Ubuntu se pega con **clic derecho** o **Ctrl+Shift+V**. Las líneas que
>   empiezan con `#` son comentarios: no hace falta escribirlas.
> - Debajo de cada bloque está **qué deberías ver**. Si ves otra cosa, **no sigas**: buscá el síntoma en §9. Todos los
>   pasos se pueden repetir sin romper nada, salvo los marcados como irreversibles en §10.
> - Lo que está entre `<…>` (por ejemplo `<tu-usuario>`) lo reemplazás por tu dato, sin los signos `<` y `>`.
> - **"Abrí una terminal nueva"** significa cerrar la ventana de Ubuntu y abrir otra (o abrir otra pestaña): así se
>   cargan los cambios de `~/.bashrc`.
> - **[verificar]** marca un dato que no se pudo comprobar en el entorno de prueba (pantallas de Windows, inicio de
>   sesión con tu cuenta, red de tu organización). Cada uno dice cómo comprobarlo vos.
> - Comandos de Ubuntu ejecutados tal cual están escritos aquí, en una Ubuntu 24.04 LTS limpia y como usuario sin
>   privilegios, el 2026-10-27 (detalle en §11). Lo del lado de Windows no se pudo ejecutar en ese entorno.

**Tiempo estimado:** 60–90 minutos la primera vez (la mitad son descargas). **Qué necesitás:** una cuenta de Windows con
permisos de administrador, conexión a internet y, para el camino A, una cuenta de Claude con Claude Code (Pro, Max,
Team, Enterprise o Console); para el camino B, una clave de algún proveedor de modelos.

---

## Mapa de la guía

| § | Paso | Camino A · Claude Code | Camino B · Hermes |
|---|---|---|---|
| 0 | Elegir el camino (y, antes, WSL2 o Docker) | leer | leer |
| 1 | Windows: requisitos, WSL2, Ubuntu 24.04, `.wslconfig` | sí | sí |
| 2 | Ubuntu: primeros ajustes (actualizar, systemd, archivos, git, hora e idioma) | sí | sí |
| 3 | Paquetes del sistema y Python en un entorno virtual | sí | sí |
| 4 | Navegador para capturas y diagramas, Node.js, Mermaid y pptxgenjs | recomendado | recomendado |
| 5 | Descargar pm-method y validarlo | sí | sí |
| 6 | Camino A: Claude Code, inicio de sesión, plugin, BMAD, primera conversación | sí | — |
| 7 | Camino B: Hermes Agent y las skills de pm-method | — | sí |
| 8 | Verificación final (lista de aceptación) | sí | sí |
| 9 | Solución de problemas | consulta | consulta |
| 10 | Actualizar, desinstalar o empezar de cero | consulta | consulta |
| 11 | Qué se verificó y qué queda por comprobar | consulta | consulta |
| 12 | Seguridad | leer | leer |

---

## 0. Elegir el camino

**Antes: ¿esta guía o Docker?** Si preferís no instalar Python, Node.js ni navegadores en Ubuntu, o querés aislar lo
que ejecuta el agente, seguí en su lugar [INSTALACION-DOCKER](INSTALACION-DOCKER.md): Docker Desktop o Docker Engine
sobre WSL2 y una imagen con todo fijado y probado (Claude Code sí; Hermes no). La comparación está en su
[§0.1](INSTALACION-DOCKER.md#01-docker-o-la-instalación-sobre-wsl2). Esta guía sigue con la instalación directa.

| Capacidad | **A · Claude Code** (recomendado) | **B · Hermes Agent** |
|---|---|---|
| 39 skills y comandos | sí, como `/pm-method:<skill>` | sí, como `/<skill>` |
| Scripts deterministas (estado, registros, sanidad, BMAD, CPM, EVM…) | sí | sí (los mismos scripts Python) |
| Orquestador y subagentes de fase (`pm-orquestador`, `pm-director`, `pm-inicio`…) | sí, como agentes con nombre | no: los agentes se usan como persona o personalidad; las skills corren en el mismo hilo |
| Hooks: bloqueo de ediciones directas de `estado.json` y registros, resumen al abrir la sesión, regla de idioma | sí | **no**: Hermes no ejecuta hooks de Claude Code; la protección queda en las reglas de las skills y en la sanidad (`/pm-sanidad`, `/pm-puerta`) y el resumen se pide con `estado.py contexto` y `estado.py radar` |
| Bloqueos de puerta de `estado.py` | sí | sí (están en el script) |
| Instalación y actualización del paquete | `claude plugin install` / `update` desde GitHub | `scripts/instalar_hermes.py` desde un clon |
| Credencial | suscripción de Claude (inicio de sesión) o clave de API | clave o inicio de sesión del proveedor que elijas en `hermes model` |
| Estado de la verificación | completa, salvo la sesión con tu cuenta | skills instaladas y rutas comprobadas; conversación con un modelo **[verificar]** |

Fuente: [INSTALACION §3](INSTALACION.md#3-instalación-en-hermes-agent) y §9. Se pueden instalar los dos en la misma
Ubuntu; esta guía hace primero lo común (§1–§5) y después cada camino.

---

## 1. Windows: requisitos, WSL2 y Ubuntu 24.04 LTS

### 1.1 Requisitos

| Requisito | Mínimo | Recomendado | Cómo comprobarlo |
|---|---|---|---|
| Windows | Windows 10 versión 2004 (compilación 19041) o Windows 11 | Windows 11 al día | **Win+R** → `winver` → Enter |
| Virtualización | habilitada en el firmware (Intel VT-x o AMD-V/SVM) | — | Administrador de tareas (Ctrl+Shift+Esc) → **Rendimiento** → **CPU** → "Virtualización: Habilitado" **[verificar el rótulo en tu idioma de Windows]** |
| Memoria | 8 GB | 16 GB o más | Administrador de tareas → Rendimiento → Memoria |
| Disco libre en `C:` | 15 GB | 25 GB | Explorador → Este equipo |
| Permisos | administrador para instalar WSL | — | — |

- El mínimo de Windows y los comandos `wsl` son los de la documentación de Microsoft ("Install WSL", consultada el
  2026-10-27). Claude Code pide 4 GB de RAM o más y, en Linux, Ubuntu 20.04 o posterior (documentación oficial
  "Advanced setup").
- El espacio: lo que instala esta guía ocupa unos **5 GB** dentro de Ubuntu, además de la propia Ubuntu (medido en
  §11, con LibreOffice y sin el Chrome de Mermaid ni Hermes); el resto es margen para proyectos, BMAD y actualizaciones.
  El disco de WSL crece solo y no se achica solo (§9.8).
- Si la virtualización figura como deshabilitada, hay que activarla en la configuración UEFI/BIOS de la PC (el nombre
  de la opción depende del fabricante) **[verificar en el manual de tu equipo]**. En equipos corporativos puede
  requerir a TI.

### 1.2 Instalar WSL2 y Ubuntu 24.04 LTS · [Windows]

**Por qué Ubuntu 24.04 LTS:** es una versión de soporte extendido (cinco años de soporte estándar, hasta 2029), es la
que figura como "Ubuntu 24.04 LTS" en la lista de WSL y, a diferencia de Ubuntu 26.04 LTS, la soportan las herramientas
de esta guía en las versiones con que se probó pm-method: en particular Playwright 1.56.0, que instala el
navegador y sus bibliotecas para las capturas y los diagramas, no publica descargas para 26.04 (por eso el entorno
Docker de pm-method, que usa 26.04, necesita un ajuste especial: [DOCKER §2](DOCKER.md#2-qué-incluye)). Si ya tenés
Ubuntu 26.04 en WSL, los §2, §3, §5, §6 y §7 funcionan igual; el §4.1 necesitaría ese ajuste **[verificar]**.

1. Abrí **PowerShell como administrador**: menú Inicio → escribí `PowerShell` → clic derecho en "Windows PowerShell"
   → **Ejecutar como administrador**.
2. Mirá qué distribuciones ofrece WSL e instalá Ubuntu 24.04:

```powershell
wsl --list --online
wsl --install -d Ubuntu-24.04
```

**Deberías ver** en la lista una línea `Ubuntu-24.04    Ubuntu 24.04 LTS` y, después de la instalación, un aviso de que
hay que **reiniciar** si WSL no estaba habilitado. Reiniciá Windows.

- Si `wsl --install` muestra solo la ayuda, WSL ya estaba instalado: el comando `wsl --install -d Ubuntu-24.04`
  instala igual la distribución.
- Si la descarga se queda en 0,0 %: `wsl --install --web-download -d Ubuntu-24.04` (Microsoft, "Install WSL").

3. Al terminar (o al abrir **Ubuntu 24.04 LTS** desde el menú Inicio después del reinicio), Ubuntu pide crear un
   **usuario y una contraseña de Linux**. Usá un nombre corto, en minúsculas y sin espacios ni tildes (por ejemplo
   `ana`). Esa contraseña es la de `sudo` dentro de Ubuntu: no es la de Windows ni la de tu cuenta de Claude, y al
   escribirla no se ven caracteres (es normal).

### 1.3 Comprobar y actualizar WSL · [Windows]

En PowerShell (no hace falta que sea como administrador):

```powershell
wsl --update
wsl --version
wsl --list --verbose
wsl --set-default Ubuntu-24.04
```

**Deberías ver:**
- `wsl --version`: una línea `Versión de WSL: 2.x.x` (o `WSL version: 2.x.x`), además de las versiones del kernel y de
  Windows **[verificar el texto exacto en tu idioma]**.
- `wsl --list --verbose`: `Ubuntu-24.04` con `STATE Running` o `Stopped` y **`VERSION 2`**.

Si dice `VERSION 1`, convertila (tarda unos minutos): `wsl --set-version Ubuntu-24.04 2`. Con WSL 1 el ejecutable de
Claude Code falla con `cannot execute binary file: Exec format error` (documentación de Claude Code, "Troubleshoot
installation").

### 1.4 Memoria y procesadores de WSL (`.wslconfig`, opcional) · [Windows]

Por defecto WSL2 usa hasta el **50 % de la memoria** de Windows, **todos los procesadores** lógicos y un archivo de
intercambio del 25 % de la memoria (valores por defecto de la documentación de Microsoft, "Advanced settings
configuration in WSL"). Con 16 GB o más no hace falta tocar nada. Conviene ajustarlo solo si:

- Windows se pone lento mientras corren las pruebas o Claude Code: bajá `memory`.
- Tenés 8 GB de RAM: dejá el valor por defecto (4 GB) y evitá correr las pruebas largas (§5.3) con otras aplicaciones
  pesadas abiertas.

Para crearlo, en PowerShell:

```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

Si pregunta si querés crear el archivo, respondé **Sí**, pegá este contenido (ejemplo para una PC de 16 GB y 8
procesadores), guardá y cerrá:

```ini
[wsl2]
memory=8GB
processors=4
swap=4GB
```

Aplicalo cerrando WSL por completo (cierra todas las ventanas de Ubuntu):

```powershell
wsl --shutdown
```

Esperá unos 8 segundos y volvé a abrir Ubuntu. Comprobación en **[Ubuntu]**: `free -h` muestra en `Mem: total` un
valor cercano al de `memory` y `nproc` el de `processors`. **[verificar]**: estos pasos son del lado de Windows y no se
pudieron ejecutar en el entorno de prueba. No agregues claves que no conozcas: un error de sintaxis hace que WSL ignore
el archivo.

---

## 2. Ubuntu: primeros ajustes · [Ubuntu]

Abrí **Ubuntu 24.04 LTS** desde el menú Inicio (o escribí `wsl` en PowerShell). Todo lo marcado [Ubuntu] se escribe
ahí.

### 2.1 Dónde estás y actualizar el sistema

```bash
cd ~ && pwd
sudo apt update
sudo apt upgrade -y
```

**Deberías ver:** `pwd` → `/home/<tu-usuario>`; `apt update` termina con `Reading package lists... Done` (o
`Leyendo lista de paquetes... Hecho`) y `apt upgrade` sin errores. La primera vez `sudo` pide la contraseña de Ubuntu
(§1.2).

### 2.2 systemd (recomendado)

Con systemd, Ubuntu mantiene la hora sincronizada y pueden correr servicios (Docker Engine, el *gateway* de Hermes).
pm-method no lo necesita, pero da un entorno más estable. Comprobá si ya está activo:

```bash
ps -p 1 -o comm=
cat /etc/wsl.conf
```

**Deberías ver** `systemd` en la primera línea y, en `/etc/wsl.conf`, una sección `[boot]` con `systemd=true` (las
imágenes de Ubuntu para WSL suelen traerlo así **[verificar]**). Si la primera línea dice otra cosa (por ejemplo
`init`), activalo:

```bash
grep -q '^\[boot\]' /etc/wsl.conf 2>/dev/null || printf '\n[boot]\nsystemd=true\n' | sudo tee -a /etc/wsl.conf
cat /etc/wsl.conf
```

y en **[Windows]** PowerShell `wsl --shutdown`; esperá 8 segundos, abrí Ubuntu y repetí `ps -p 1 -o comm=`. Si
`/etc/wsl.conf` ya tenía una sección `[boot]` sin `systemd=true`, editalo a mano con `sudo nano /etc/wsl.conf`
(guardar: Ctrl+O, Enter; salir: Ctrl+X). Claves de `wsl.conf`: documentación de Microsoft, "Advanced settings
configuration in WSL".

### 2.3 Dónde guardar tus archivos

**Trabajá siempre dentro de tu carpeta de Linux (`~`, es decir `/home/<tu-usuario>`), nunca en `/mnt/c/…`** (el disco
de Windows visto desde Ubuntu):

| | En `~` (sistema de archivos de Linux) | En `/mnt/c/…` (disco de Windows) |
|---|---|---|
| Velocidad de git, Python y Node | normal | mucho más lenta: cada acceso cruza de la máquina virtual a Windows |
| Permisos de Linux (`chmod +x`) | correctos | emulados; los scripts pueden no ser ejecutables |
| Finales de línea | LF, los que esperan los scripts | riesgo de CRLF si los edita un programa de Windows |
| Vigilancia de cambios de archivos | fiable | poco fiable |

Para **ver tus archivos de Ubuntu desde Windows**, en el Explorador escribí en la barra de direcciones:

```text
\\wsl.localhost\Ubuntu-24.04\home\<tu-usuario>
```

(en algunas compilaciones de Windows 10: `\\wsl$\Ubuntu-24.04\home\<tu-usuario>` **[verificar]**). También podés abrir
la carpeta actual de Ubuntu en el Explorador con `explorer.exe .` (con el punto). Abrir o copiar archivos desde Windows
está bien; **no** uses programas de Windows (Git for Windows, editores que conviertan finales de línea) para hacer
commits o modificar en masa archivos de Ubuntu. Para llevar un archivo de Windows a Ubuntu:
`cp /mnt/c/Users/<tu-usuario-de-windows>/Downloads/<archivo> ~/`.

### 2.4 Git: identidad y finales de línea

```bash
sudo apt install -y git
git config --global user.name "<tu nombre>"
git config --global user.email "<el correo de tu cuenta de GitHub>"
git config --global init.defaultBranch main
git config --global core.autocrlf input
git config --global pull.ff only
git config --global --list
```

**Deberías ver** al final las cinco claves con tus valores (`user.name=…`, `user.email=…`, `init.defaultbranch=main`,
`core.autocrlf=input`, `pull.ff=only`).

- `core.autocrlf input`: si algún archivo llega con finales de línea de Windows (CRLF), git lo guarda con los de Linux
  (LF). Los scripts `.sh` y `.py` con CRLF fallan con `bad interpreter: /bin/sh^M` (§9.9). El repositorio de
  pm-method, además, fija LF para esos archivos en su `.gitattributes`.
- La identidad solo hace falta si vas a hacer commits. Nunca escribas contraseñas ni tokens de GitHub en estos
  comandos (§12).

### 2.5 Hora, zona horaria e idioma de la terminal

```bash
sudo apt install -y tzdata
date
locale | head -1
```

**Deberías ver:** `date` con tu hora local actual (WSL suele tomar la zona horaria de Windows **[verificar]**) y
`LANG=C.UTF-8` o `LANG=en_US.UTF-8` (lo importante es que termine en **UTF-8**, para que los acentos y la ñ de los
scripts se vean bien).

- Zona horaria incorrecta, con systemd (§2.2): `sudo timedatectl set-timezone America/Montevideo` (cambiá por tu zona;
  la lista sale con `timedatectl list-timezones`).
- Hora atrasada después de suspender la PC: §9.4.
- Si `LANG` está vacío, dice `POSIX` o no termina en UTF-8, fijalo para tu usuario (`C.UTF-8` viene siempre incluido en
  Ubuntu) y abrí una terminal nueva:

```bash
grep -qxF 'export LANG=C.UTF-8' ~/.bashrc || echo 'export LANG=C.UTF-8' >> ~/.bashrc
```

---

## 3. Paquetes del sistema y Python · [Ubuntu]

### 3.1 Paquetes del sistema

```bash
sudo apt install -y git curl ca-certificates unzip xz-utils python3 python3-venv python3-pip
git --version
python3 --version
```

**Deberías ver** `git version 2.43.0` (o posterior) y `Python 3.12.3` (o posterior; pm-method exige 3.9 o más).

| Paquete | Para qué |
|---|---|
| `git` | descargar y actualizar pm-method, instalar el plugin desde GitHub, BMAD y Hermes |
| `curl`, `ca-certificates` | instaladores de Claude Code, nvm y Hermes por HTTPS |
| `unzip`, `xz-utils` | descomprimir; nvm descarga Node.js en `.tar.xz` |
| `python3`, `python3-venv`, `python3-pip` | los scripts de pm-method y el entorno virtual del §3.2 |

### 3.2 Entorno virtual de Python con los paquetes de pm-method

Ubuntu 24.04 **no deja** instalar paquetes con `pip` en el Python del sistema: responde `error:
externally-managed-environment` (norma PEP 668, que protege las herramientas del sistema operativo). La forma correcta
es un **entorno virtual**: una carpeta con su propio Python y sus paquetes, que no toca el del sistema.

```bash
python3 -m venv ~/.venvs/pm-method
~/.venvs/pm-method/bin/python -m pip install pyyaml==6.0.3 python-docx==1.2.0 openpyxl==3.1.5 matplotlib==3.11.2 playwright==1.56.0
```

**Deberías ver** al final `Successfully installed …` con los cinco paquetes y sus dependencias. Son las versiones con
que se probó pm-method (las mismas de `docker/requirements.txt`):

| Paquete | Lo usa |
|---|---|
| `pyyaml` | puente BMAD (`bmad.py`) y `probar_paquete.py` (obligatorio para las pruebas) |
| `python-docx`, `openpyxl` | exportar a Word y Excel; leer actas `.docx` |
| `matplotlib` | gráficos de los recorridos E2E (`scripts/pruebas/guias_e2e/`) |
| `playwright` | capturas de tableros y recorridos E2E; descarga el navegador sin interfaz (§4.1) |

**Activar el entorno en cada terminal** (una sola vez): así `python3` y `pip` de tu usuario son siempre los del entorno,
y lo heredan Claude Code, sus hooks y Hermes cuando los abrís desde esa terminal.

```bash
grep -qxF 'source ~/.venvs/pm-method/bin/activate' ~/.bashrc || echo 'source ~/.venvs/pm-method/bin/activate' >> ~/.bashrc
tail -1 ~/.bashrc
```

**Abrí una terminal nueva** y comprobá:

```bash
which python3
python3 -c "import yaml, docx, openpyxl, matplotlib, playwright; print('paquetes OK')"
```

**Deberías ver** el indicador `(pm-method)` al comienzo de la línea de comandos,
`/home/<tu-usuario>/.venvs/pm-method/bin/python3` y `paquetes OK`.

- Para usar el Python del sistema en una terminal puntual: `deactivate` (vuelve en la próxima terminal).
- Nunca uses `sudo pip …` ni `--break-system-packages`: dañan el Python del sistema.

---

## 4. Navegador, Node.js, Mermaid y pptxgenjs · [Ubuntu]

Recomendado para los dos caminos: sin esto pm-method funciona, pero no se generan las capturas de los recorridos E2E,
los diagramas Mermaid como imagen (Word, mapas de Wardley, `validar_mermaid.py --render`) ni los PPTX del webinar.

### 4.1 Navegador sin interfaz para capturas (Playwright)

```bash
python3 -m playwright install --with-deps --only-shell chromium
```

Descarga la versión sin ventana de Chromium que usa Playwright 1.56.0 (*headless shell*, revisión 1194, unos 330 MB
en `~/.cache/ms-playwright/`) e instala con `apt` las bibliotecas y fuentes que necesita (por eso aparece
`Switching to root user to install dependencies...` y pide la contraseña de `sudo`; las bibliotecas suman unos 350 MB).
`--only-shell` evita bajar además el Chromium completo (unos 600 MB más), que pm-method no usa: sus capturas se hacen
sin ventana. **Deberías ver** los paquetes que instala `apt`, líneas `… downloaded to …` (o nada nuevo si el navegador
ya estaba) y ningún error.

Comprobación (abre el navegador sin ventana y saca una captura):

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.set_content('<h1>prueba</h1>'); pg.screenshot(path='/tmp/prueba.png'); b.close()
print('captura OK')"
ls -l /tmp/prueba.png
```

**Deberías ver** `captura OK` y el archivo `/tmp/prueba.png`.

### 4.2 Node.js con nvm

Node.js hace falta para BMAD, para las skills externas con `npx skills`, para Mermaid y para los PPTX. Se instala con
**nvm** (gestor de versiones de Node para tu usuario, sin `sudo`), porque el Node de Ubuntu 24.04 (18.19) es anterior al
mínimo:

| Componente | Node mínimo |
|---|---|
| BMAD (`bmad-method@6.12.4`) | 20.12.0 |
| Claude Code por npm (§6.1, alternativa) | 22 |
| `@mermaid-js/mermaid-cli` 11.16.0 y su `puppeteer` | 22.12 |
| skills externas con `npx skills` (1.7.x) | **22.20.0** |

Por eso se instala la **línea 22** (la versión con que se probó pm-method; recibe la última 22.x).

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
```

**Deberías ver** al final `=> Close and reopen your terminal to start using nvm`. **Abrí una terminal nueva** y:

```bash
nvm install 22
nvm alias default 22
node --version
npm --version
which node
```

**Deberías ver:** `node --version` → `v22.22.0` o una 22.x posterior (como mínimo `v22.20.0`); `npm --version` →
`10.9.4` o posterior; `which node` → `/home/<tu-usuario>/.nvm/versions/node/v22.…/bin/node`. Si `which node` muestra
una ruta que empieza con `/mnt/c/`, se está usando el Node de Windows: §9.6.

La versión de nvm (`v0.40.8`) es la vigente al 2026-10-27 en https://github.com/nvm-sh/nvm; una posterior también sirve.

### 4.3 Mermaid y pptxgenjs

```bash
npm install -g @mermaid-js/mermaid-cli@11.16.0 pptxgenjs@4.0.1
mmdc --version
```

**Deberías ver** `11.16.0`. Nunca uses `sudo npm …`: con nvm, los paquetes globales quedan en tu carpeta.

`npm install` descarga también un Chrome propio para Mermaid (en `~/.cache/puppeteer/`). Si la red lo bloquea, la
instalación **termina sin error** pero el render falla después: por eso se comprueba con un diagrama real:

```bash
printf 'flowchart LR\n  A[pm-method] --> B[WSL2]\n' > /tmp/prueba.mmd
mmdc -i /tmp/prueba.mmd -o /tmp/prueba-mermaid.png
ls -l /tmp/prueba-mermaid.png
```

**Deberías ver** el archivo `/tmp/prueba-mermaid.png`. Si dice `Could not find Chrome` o `Failed to launch the browser
process`: §9.5.

### 4.4 LibreOffice (opcional)

Solo hace falta para revisar o convertir los PPTX y DOCX dentro de Ubuntu (por ejemplo, con las skills de Office). Los
archivos generados se pueden abrir directamente con el Office de Windows desde `\\wsl.localhost\…` (§2.3), así que
podés saltear este paso.

```bash
sudo apt install -y libreoffice-impress libreoffice-writer libreoffice-calc
soffice --version
```

**Deberías ver** `LibreOffice 24.2…` (o posterior). `apt` informa unos 450 MB de espacio adicional.

---

## 5. Descargar pm-method y validarlo · [Ubuntu]

El clon del repositorio sirve en los dos caminos: para las validaciones de este paso, para Hermes (§7) y para probar
cambios con `--plugin-dir` (§6.4). En el camino A, el plugin que usa Claude Code se instala aparte desde GitHub (§6.3).

### 5.1 Clonar

```bash
git clone https://github.com/Arturo-Penas-Rial/pm-method.git ~/pm-method
grep '"version"' ~/pm-method/.claude-plugin/plugin.json
```

**Deberías ver** `"version": "2.5.0",` (o una versión posterior publicada).

### 5.2 Validación rápida y prueba de los hooks sin abrir Claude

```bash
cd ~/pm-method
python3 scripts/validar_paquete.py
sh hooks/py.sh -c "import sys, yaml, docx, openpyxl; print(sys.executable)"
```

**Deberías ver:**
- `Skills: 39 (33 invocables por el modelo, listado 6957 caracteres) · Agentes: 6` y una última línea `OK`.
- `/home/<tu-usuario>/.venvs/pm-method/bin/python3`: el lanzador de los hooks (`hooks/py.sh`) encuentra el Python del
  entorno, con sus paquetes. Si muestra `/usr/bin/python3` o un error de importación, el entorno no está activo en esa
  terminal (§3.2).

### 5.3 Pruebas completas del paquete (≈ 5–15 minutos, sin consumir tokens)

```bash
cd ~/pm-method
python3 scripts/probar_paquete.py 2>&1 | tail -1
python3 scripts/validar_mermaid.py --render | tail -1
python3 scripts/pruebas/guias_e2e/correr.py --salida ~/pm-pruebas/guias | grep -c '^OK'
python3 scripts/webinar/generar.py --todos --salida ~/pm-pruebas/webinar | tail -2
```

**Deberías ver:**

| Comando | Resultado esperado | Tiempo aproximado |
|---|---|---|
| `probar_paquete.py` | `Resultado: 355 OK · 0 FALLO` (el número total puede cambiar entre versiones; lo que importa es `0 FALLO`) | 2–8 min |
| `validar_mermaid.py --render` | `OK · 128 bloques Mermaid · 0 error(es)` | 1–3 min |
| `guias_e2e/correr.py` | `5`: los cinco recorridos E2E terminaron `OK`, con 51 capturas y gráficos en `~/pm-pruebas/guias` (sin `grep`, una línea `OK guía E2E-N …` por recorrido) | 2–6 min |
| `webinar/generar.py --todos` | `Resultado: 5/5 caso(s) sin errores`: diapositivas HTML y PPTX de los cinco casos en `~/pm-pruebas/webinar` | < 1 min |

`~/pm-pruebas` es una carpeta de trabajo: se puede borrar cuando quieras. No crees proyectos ni salidas dentro de
`~/pm-method` (ensuciarían el repositorio).

### 5.4 Proyecto de prueba con los scripts (sin abrir Claude ni Hermes)

Comprueba los scripts del núcleo sobre una carpeta de prueba, sin consumir tokens:

```bash
mkdir -p ~/proyectos/prueba-scripts && cd ~/proyectos/prueba-scripts
python3 ~/pm-method/skills/pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta gestion --nombre "Prueba de instalación"
python3 ~/pm-method/skills/pm-estado-proyecto/scripts/estado.py --proyecto gestion siguiente
python3 ~/pm-method/skills/pm-estado-proyecto/scripts/sanidad.py --proyecto gestion | head -1
```

**Deberías ver** `Proyecto creado en gestion · …`, el siguiente paso del método (`Fase: pre-proyecto · Proceso: SU …`) y
la primera línea de la sanidad: `Sanidad de 'Prueba de instalación' (pre-proyecto/SU): 0 ERROR · 0 AVISO · 1 INFO` (el
INFO es ESP-02, "índice de especificación desactualizado", normal en un proyecto recién creado: se reconstruye solo y
desaparece en la siguiente sanidad). Lo importante es **0 ERROR**.

Si repetís la sanidad desde `~/pm-method` **después** de instalar el plugin (§6.3), aparecen avisos **INS-04** ("la
skill … está instalada 2 veces"): la sanidad cuenta la carpeta desde la que se ejecuta el script además de la copia
instalada. Es esperable y no es una instalación doble ([INSTALACION §12](INSTALACION.md#12-solución-de-problemas)).

---

## 6. Camino A · Claude Code

### 6.1 Instalar Claude Code · [Ubuntu]

Con el **instalador nativo** (método recomendado por la documentación oficial de Claude Code, "Advanced setup",
consultada el 2026-10-27; se instala y se ejecuta **dentro de WSL**, no desde PowerShell):

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

El comando no muestra progreso mientras descarga. Instala `claude` en `~/.local/bin/claude` y se actualiza solo en
segundo plano. **Abrí una terminal nueva** y comprobá:

```bash
claude --version
claude doctor
```

**Deberías ver** `2.1.311 (Claude Code)` o una versión posterior, y `claude doctor` debe terminar con `No installation
issues found.` (antes de iniciar sesión también informa que no hay sesión de claude.ai: es normal). Si `claude doctor`
dice `Native installation exists but ~/.local/bin is not in your PATH` o la terminal dice `claude: command not found`:
§9.7.

**Alternativa si el instalador falla** con `curl: (22) The requested URL returned error: 403` (frecuente en redes
corporativas que bloquean `downloads.claude.ai`; si tu red usa proxy, primero §9.2): instalar el mismo programa con
npm, que descarga desde `registry.npmjs.org`. Requiere el Node del §4.2 y **nunca** `sudo`:

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

Instalado por npm, Claude Code se actualiza con `npm install -g @anthropic-ai/claude-code@latest` (§10.1). No combines
los dos métodos: si cambiás de uno a otro, desinstalá el anterior (§10.3).

### 6.2 Iniciar sesión · [Ubuntu] y [Claude]

Primero comprobá que no haya una clave de API definida (si la hay, Claude Code la usa en lugar de tu suscripción y el
consumo se cobra por API):

```bash
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+DEFINIDA}"
claude auth status
```

**Deberías ver** `ANTHROPIC_API_KEY:` sin nada después y, en `claude auth status`, `"loggedIn": false` (todavía no
iniciaste sesión). Ahora abrí Claude Code en tu carpeta personal:

```bash
cd ~ && claude
```

- La primera vez pregunta el estilo de colores y el método de inicio de sesión: elegí tu **cuenta de Claude**
  (suscripción) o **Anthropic Console** (facturación por API), según tu caso.
- Se abre el navegador de Windows. Iniciá sesión y autorizá. **En WSL es habitual** que el navegador muestre un
  **código** en lugar de volver solo a la terminal: copialo y pegalo en el aviso `Paste code here if prompted` (clic
  derecho para pegar). Si el navegador no se abre, presioná `c` para copiar la dirección y abrila vos en Windows
  (documentación de Claude Code, "OAuth login fails in WSL2, SSH, or containers").
- Claude Code pregunta si confiás en la carpeta: respondé que sí solo en carpetas tuyas.

Dentro de la sesión, escribí **[Claude]** `/status`. **Deberías ver** tu cuenta y el método de inicio de sesión. Salí
con `/exit`. De vuelta en la terminal, `claude auth status` debe mostrar `"loggedIn": true`. **[verificar]**: el inicio
de sesión con una cuenta real no se pudo ejecutar en el entorno de prueba.

Nunca pegues contraseñas, claves ni el código de inicio de sesión en un chat ni en archivos (§12). Todas las opciones de
credenciales (clave de API, token para CI, proveedores de nube): [INSTALACION
§0.7](INSTALACION.md#07-claves-de-api-y-credenciales-cuáles-dónde-y-cómo).

### 6.3 Instalar el plugin pm-method desde GitHub · [Ubuntu]

```bash
claude plugin marketplace add Arturo-Penas-Rial/pm-method
claude plugin install pm-method@pm-method
claude plugin list
```

**Deberías ver** al final `pm-method@pm-method`, `Version: 2.5.0` y `Status: ✔ enabled`. El plugin queda para tu usuario
en todas las carpetas (alcance `user`, el valor por defecto). Equivalente dentro de una sesión: `/plugin marketplace
add Arturo-Penas-Rial/pm-method` y `/plugin install pm-method@pm-method`.

Qué queda disponible: las 39 skills como `/pm-method:<skill>`, los 6 agentes (`pm-method:pm-orquestador` y los
subagentes de fase) y los 3 hooks ([INSTALACION §2.1](INSTALACION.md#21-como-plugin-desde-el-marketplace-local) y §9).

### 6.4 Alternativa: cargar el plugin desde tu clon (`--plugin-dir`)

Para probar una versión local o cambios propios sin instalarla: `claude --plugin-dir ~/pm-method`. Vale solo para esa
sesión. **No combines** las dos formas: con el plugin instalado (§6.3) y `--plugin-dir` a la vez, las skills aparecen
dos veces y la sanidad lo informa como **INS-04**. Antes de usar `--plugin-dir`, deshabilitá el instalado:

```bash
claude plugin disable pm-method@pm-method
claude plugin list
claude plugin enable pm-method@pm-method
```

(`disable` antes de la sesión con `--plugin-dir`; `enable` para volver a la instalación desde GitHub; `list` muestra
`Status: ✘ disabled` o `✔ enabled`. Ejecutados en tu carpeta personal, los mensajes dicen `scope: project` porque ahí
la configuración del proyecto y la del usuario son el mismo archivo, `~/.claude/settings.json`; el efecto es el mismo.)

### 6.5 Primera conversación de prueba · [Ubuntu] y [Claude]

```bash
mkdir -p ~/proyectos/demo && cd ~/proyectos/demo && claude
```

Dentro de Claude, en orden:

| # | Escribí | Deberías ver |
|---|---|---|
| 1 | `/pm-method:pm-ayuda` | la guía de qué escribir en cada situación, en español |
| 2 | `/pm-method:pm-nuevo "Proyecto Demo"` | crea la carpeta de gestión con `estado.json` y los registros |
| 3 | `/exit` y volvé a abrir `claude` en la misma carpeta | al iniciar, el resumen del hook de inicio: `pm-method · proyecto 'Proyecto Demo' …` y la ruta de los scripts |
| 4 | `¿qué sigue?` | el orquestador lee el estado y propone el siguiente paso de PRINCE2 (puesta en marcha) |
| 5 | `editá estado.json a mano y poné fase=cierre` | **el hook lo bloquea** con "pm-method: estado.json se actualiza solo con estado.py…" |
| 6 | `/pm-method:pm-sanidad` | el chequeo de consistencia, sin `ERROR` |
| 7 | `What's next?` | la respuesta en inglés (hook de idioma) |

**[verificar]** en tu primer uso: estos pasos consumen tu plan y no se pudieron ejecutar con una cuenta en el entorno de
prueba. El comportamiento de los hooks sí se comprobó (§5.2 y §11). Para una consulta sin sesión interactiva: `claude -p
"/pm-method:pm-ayuda"`. Prueba de aceptación completa: [PRUEBAS
§6](PRUEBAS.md#6-prueba-de-aceptación-antes-del-primer-proyecto-real). Siguientes pasos como usuario: las [guías
E2E](guias/README.md).

### 6.6 BMAD (opcional) · [Ubuntu]

pm-method lee BMAD (la capa de especificación del producto) sin modificarlo; BMAD se instala en el repositorio del
producto. Prueba en una carpeta nueva (requiere el Node del §4.2):

```bash
mkdir -p ~/proyectos/demo-bmad && cd ~/proyectos/demo-bmad && git init -q
npx --yes bmad-method@6.12.4 install --modules bmm --tools claude-code --yes --user-name "Demo" --set core.project_name=demo-bmad --no-shims
python3 ~/pm-method/skills/pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta gestion --nombre "Demo BMAD"
python3 ~/pm-method/skills/pm-bmad-puente/scripts/bmad.py --proyecto gestion detectar
```

**Deberías ver** las carpetas `_bmad/` y `.claude/skills/bmad-*` creadas y, en `detectar`, `layout` `v6`, `version`
`6.12.4` y `soporte` `soportada`. Un aviso `npm warn deprecated glob@…` durante la instalación es de una dependencia de
BMAD y no afecta. Opciones del instalador: [INSTALACION
§4](INSTALACION.md#4-bmad-en-el-repositorio-del-producto-opcional). Con BMAD instalado, el listado de skills crece: si
el modelo no activa la skill esperada, ver [INSTALACION §7.4](INSTALACION.md#74-settings-recomendados-en-claude-code)
(sanidad INS-05).

### 6.7 ¿Y Docker? Es otro camino

Usar pm-method dentro de un contenedor Docker (Docker Desktop con el *backend* WSL2 o Docker Engine dentro de Ubuntu) es
un **camino de instalación independiente** de esta guía, con sus propios pasos: [INSTALACION-DOCKER](INSTALACION-DOCKER.md).
No hace falta hacer nada de este apartado si seguiste esta guía.

---

## 7. Camino B · Hermes Agent

### 7.1 Instalar Hermes · [Ubuntu]

Según el README y la guía de instalación de Hermes Agent (repositorio `NousResearch/hermes-agent`, consultados el
2026-10-27), en Linux y WSL2:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

El instalador clona Hermes en `~/.hermes/hermes-agent/`, deja el comando `hermes` en `~/.local/bin/` y guarda tus datos
en `~/.hermes/`. Trae su propio Python (3.14), Node.js y demás herramientas (no usa el entorno del §3.2 ni el Node del
§4.2 para correr Hermes) y requiere `git`, `curl`, `tar` y `sha256sum` (§3.1). Si falta `libatomic1`, lo instala
pidiendo la contraseña de `sudo`. **Abrí una terminal nueva** y comprobá:

```bash
hermes --version
hermes doctor
```

**Deberías ver** la versión de Hermes y un diagnóstico sin problemas sin resolver (`hermes doctor` termina con código 0
cuando no quedan problemas). **[verificar]**: la descarga del instalador estaba bloqueada en la red del entorno de
prueba.

### 7.2 Elegir el proveedor de modelos · [Ubuntu]

```bash
hermes model
```

Elegí proveedor y modelo; si pide una clave, se guarda en `~/.hermes/.env` (nunca en `config.yaml` ni en carpetas de
proyecto). Para todo el asistente de configuración: `hermes setup`. Protegé el archivo: `chmod 600 ~/.hermes/.env`.
Detalle: [INSTALACION §0.7](INSTALACION.md#07-claves-de-api-y-credenciales-cuáles-dónde-y-cómo) (fila Hermes Agent).

### 7.3 Instalar las skills de pm-method en Hermes · [Ubuntu]

No uses `hermes skills install` ni `hermes skills tap add` con este repositorio: copiarían las skills con rutas
`${CLAUDE_SKILL_DIR}` que Hermes no expande. El script del repositorio hace una copia adaptada:

```bash
python3 ~/pm-method/scripts/instalar_hermes.py --verificar
python3 ~/pm-method/scripts/instalar_hermes.py
ls ~/.hermes/skills/pm-method | grep -c '^pm-'
```

**Deberías ver:** `pm-method → Hermes: 39 skills y 6 agentes en /home/<tu-usuario>/.hermes/skills/pm-method`, luego
`Listo: 39 skills (… archivos adaptados), agentes en …/_agentes.` y el conteo `39`.

Qué hace: copia `skills/` a `~/.hermes/skills/pm-method/` cambiando `${CLAUDE_SKILL_DIR}` por `${HERMES_SKILL_DIR}`
(la variable que Hermes reemplaza al cargar una skill), deja los agentes como texto de persona en `_agentes/` con rutas
absolutas y **no copia los hooks**. Volvé a correrlo después de cada `git pull` (§10.1); solo reemplaza su propia
copia (la marca con el archivo `.pm-method`).

En Hermes:

```bash
hermes skills list | grep -c "pm-"
```

**Deberías ver** `39` **[verificar]**. Dentro de una sesión (`hermes`), `/reload-skills` vuelve a leer las skills y
`/pm-ayuda` debe responder con la guía de pm-method **[verificar en el primer uso]**.

### 7.4 Qué funciona y qué no en Hermes

- Funcionan las 39 skills (como `/pm-ayuda`, `/pm-nuevo`, …) y los scripts. Los scripts los ejecuta la herramienta de
  terminal de Hermes con `python3`: abrí `hermes` desde una terminal con el entorno del §3.2 activo para que tengan
  `pyyaml`, `python-docx` y `openpyxl` **[verificar en el primer uso con `/pm-sanidad`: no debe aparecer INS-01]**.
- No hay hooks: nada impide que el modelo edite `estado.json` o un registro a mano. Pedí siempre los cambios a través
  de las skills y corré `/pm-sanidad` antes de cada puerta. El resumen que en Claude Code da el hook de inicio se pide
  así:

```bash
python3 ~/.hermes/skills/pm-method/pm-estado-proyecto/scripts/estado.py --proyecto ~/proyectos/prueba-scripts/gestion contexto
python3 ~/.hermes/skills/pm-method/pm-estado-proyecto/scripts/estado.py --proyecto ~/proyectos/prueba-scripts/gestion radar
```

- No hay subagentes con nombre: el orquestador se usa como persona (`_agentes/pm-orquestador.md` como `SOUL.md` de un
  perfil o como personalidad), según [INSTALACION §3.2](INSTALACION.md#32-agentes-como-personas).

---

## 8. Verificación final · lista de aceptación

| # | Dónde · comando | Resultado esperado | Camino |
|---|---|---|---|
| 1 | [Windows] `wsl --list --verbose` | `Ubuntu-24.04` con `VERSION 2` | A y B |
| 2 | [Ubuntu] `pwd` al abrir Ubuntu | `/home/<tu-usuario>` (no `/mnt/c/…`) | A y B |
| 3 | [Ubuntu] `which python3` | `/home/<tu-usuario>/.venvs/pm-method/bin/python3` | A y B |
| 4 | [Ubuntu] `python3 -c "import yaml, docx, openpyxl, matplotlib, playwright; print('paquetes OK')"` | `paquetes OK` | A y B |
| 5 | [Ubuntu] `node --version` y `which node` | `v22.20.0` o posterior, bajo `~/.nvm/` | A y B |
| 6 | [Ubuntu] `mmdc --version` | `11.16.0` | A y B |
| 7 | [Ubuntu] `cd ~/pm-method && python3 scripts/validar_paquete.py` | `OK` | A y B |
| 8 | [Ubuntu] `python3 scripts/probar_paquete.py 2>&1 \| tail -1` | `… 0 FALLO` | A y B |
| 9 | [Ubuntu] `python3 scripts/pruebas/guias_e2e/correr.py --salida ~/pm-pruebas/guias \| grep -c '^OK'` | `5` | A y B |
| 10 | [Ubuntu] `python3 scripts/validar_mermaid.py --render \| tail -1` | `OK · … 0 error(es)` | A y B |
| 11 | [Ubuntu] `claude --version` y `claude doctor` | la versión y `No installation issues found.` | A |
| 12 | [Ubuntu] `claude auth status` | `"loggedIn": true` | A |
| 13 | [Ubuntu] `claude plugin list` | `pm-method@pm-method` · `Version: 2.5.0` · `Status: ✔ enabled` | A |
| 14 | [Ubuntu] `cd ~/pm-method && claude plugin validate .` | `✔ Validation passed with warnings` (avisos esperados: `CLAUDE.md` de la raíz es para quien desarrolla el paquete y el plugin no tiene ícono) | A |
| 15 | [Claude] §6.5, pasos 1 a 7 | todo según la tabla | A |
| 16 | [Ubuntu] `hermes doctor` | sin problemas sin resolver | B |
| 17 | [Ubuntu] `hermes skills list \| grep -c "pm-"` | `39` | B |
| 18 | [Hermes] `/pm-ayuda` | la guía de pm-method | B |

Si todos los puntos de tu camino están bien, el entorno está completo.

---

## 9. Solución de problemas

### 9.1 Tabla de síntomas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `wsl --install` falla con un error de virtualización (por ejemplo `0x80370102`) | virtualización deshabilitada en el firmware | §1.1 **[verificar el código en tu equipo]** |
| `wsl --list --verbose` muestra `VERSION 1` | distribución en WSL 1 | `wsl --set-version Ubuntu-24.04 2` (§1.3) |
| `cannot execute binary file: Exec format error` al ejecutar `claude` | WSL 1 | ídem |
| `\\wsl.localhost\Ubuntu-24.04` no abre en el Explorador | nombre distinto o Windows 10 | usar el nombre que muestra `wsl --list --verbose`; probar `\\wsl$\<nombre>` |
| `sudo` no acepta la contraseña o la olvidaste | — | en [Windows] PowerShell: `wsl -d Ubuntu-24.04 -u root passwd <tu-usuario>` y escribí una nueva **[verificar]** |
| `apt update` falla con `Temporary failure resolving` | DNS de WSL (VPN o red corporativa) | §9.3 |
| `apt`, `curl`, `git`, `pip` o `npm` fallan con `certificate verify failed`, `SELF_SIGNED_CERT_IN_CHAIN`, `unable to get local issuer certificate` o `403` | proxy corporativo con inspección TLS o sitio bloqueado | §9.2 |
| `error: externally-managed-environment` al usar `pip` | Python del sistema protegido (PEP 668) | usar el entorno virtual (§3.2); el indicador `(pm-method)` debe verse en la terminal |
| `No module named yaml` (u otro paquete) al correr un script | entorno virtual no activo en esa terminal | `source ~/.venvs/pm-method/bin/activate`, y comprobar la línea en `~/.bashrc` (§3.2) |
| `nvm: command not found` | terminal abierta antes de instalar nvm | abrir una terminal nueva; si sigue, §9.6 |
| `node --version` muestra una versión vieja o `which node` empieza con `/mnt/c/` | Node de Ubuntu o de Windows antes que el de nvm | §9.6 |
| `claude: command not found` | `~/.local/bin` fuera del PATH, terminal vieja, o (con npm) nvm no cargado | §9.7 |
| El instalador de Claude Code muestra `syntax error near unexpected token '<'` o `403` | la red devuelve una página en lugar del script, o bloquea `downloads.claude.ai` | §9.2; o la alternativa con npm del §6.1 |
| El inicio de sesión no vuelve a la terminal | normal en WSL | pegar el código del navegador en `Paste code here if prompted`; si no pega, `claude auth login` (§6.2) |
| `/status` muestra clave de API en vez de suscripción | `ANTHROPIC_API_KEY` definida | quitar la línea `export ANTHROPIC_API_KEY=…` de `~/.bashrc`, `unset ANTHROPIC_API_KEY`, terminal nueva |
| "Token expired" o te pide iniciar sesión seguido | reloj de WSL atrasado | §9.4 |
| Las skills `pm-*` aparecen dos veces o la sanidad informa **INS-04** | plugin instalado y `--plugin-dir` a la vez, o plugin y copia manual | §6.4 (`claude plugin disable pm-method@pm-method`); no copiar skills a mano |
| INS-04 citando `~/.claude/plugins/marketplaces/pm-method/` y `~/.claude/plugins/cache/pm-method/…` | la sanidad cuenta también el clon del marketplace | no es una instalación doble ([INSTALACION §12](INSTALACION.md#12-solución-de-problemas)) |
| INS-04 al correr `sanidad.py` desde `~/pm-method` con el plugin instalado | la sanidad cuenta la carpeta del script que se ejecuta | usar los scripts de la copia instalada (ruta que imprime el hook de inicio) |
| `claude plugin list` muestra una versión anterior | catálogo sin refrescar | §10.1 |
| El hook no bloquea la edición de `estado.json` | Hermes (no tiene hooks) o copia manual de skills | usar el plugin (§6.3) o `--plugin-dir` |
| `mmdc` o las capturas fallan: `Could not find Chrome`, `Failed to launch the browser process`, `error while loading shared libraries` | navegador no descargado, bibliotecas faltantes o `TMPDIR` largo | §9.5 |
| `bad interpreter: /bin/sh^M` o `/usr/bin/env: 'python3\r'` | archivo con finales de línea de Windows (CRLF) | §9.9 |
| `Permission denied` en archivos bajo `/mnt/c` | permisos emulados del disco de Windows | trabajar en `~` (§2.3) |
| `git status` muestra todo modificado sin cambios visibles | finales de línea o permisos alterados por herramientas de Windows | §9.9 |
| Todo anda muy lento | proyectos en `/mnt/c`, antivirus o poca memoria | §2.3, §9.10 y §1.4 |
| `No space left on device` | disco de WSL o de Windows lleno | §9.8 |
| Hermes no encuentra los scripts | skills instaladas sin adaptar | repetir §7.3 con `instalar_hermes.py` |
| `hermes: command not found` | terminal abierta antes de instalar | abrir una terminal nueva (el instalador agrega `~/.local/bin` al PATH en `~/.bashrc`) |

### 9.2 Red corporativa: proxy y certificados

Si tu organización usa un **proxy** (y en especial uno que inspecciona HTTPS con un certificado propio), las
descargas fallan con errores de certificado o `403`. Pedile a TI la **dirección del proxy** (por ejemplo
`http://proxy.tuempresa:8080`) y el **certificado de su autoridad (CA)** en formato PEM (un archivo `.crt` que empieza
con `-----BEGIN CERTIFICATE-----`). Copiá el certificado a tu carpeta de descargas de Windows y, en [Ubuntu], **una
sola vez** (el punto 3 agrega líneas a `~/.bashrc`):

```bash
# 1. Certificado de la CA corporativa en el almacén del sistema (lo usan apt, curl, git y los instaladores)
sudo cp /mnt/c/Users/<tu-usuario-de-windows>/Downloads/<ca-corporativa>.crt /usr/local/share/ca-certificates/ca-corporativa.crt
sudo update-ca-certificates
# 2. Proxy para apt (apt no lee las variables de tu usuario cuando corre con sudo)
printf 'Acquire::http::Proxy "%s";\nAcquire::https::Proxy "%s";\n' "<url-del-proxy>" "<url-del-proxy>" | sudo tee /etc/apt/apt.conf.d/95proxy
# 3. Proxy y certificado para tu usuario: git, curl, nvm, npm, pip, Playwright, Claude Code y Hermes
cat >> ~/.bashrc <<'EOF'
export HTTPS_PROXY="<url-del-proxy>" HTTP_PROXY="<url-del-proxy>" NO_PROXY="localhost,127.0.0.1"
export https_proxy="$HTTPS_PROXY" http_proxy="$HTTP_PROXY" no_proxy="$NO_PROXY"
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
EOF
```

**Deberías ver:** `update-ca-certificates` → `1 added, 0 removed; done.`; luego, en una terminal nueva,
`curl -sS -o /dev/null -w '%{http_code}\n' https://pypi.org` → `200`. Si `curl` no está instalado:
`sudo apt install -y curl` (apt ya usa el proxy).

- `update-ca-certificates` agrega la CA a `/etc/ssl/certs/ca-certificates.crt`; `NODE_EXTRA_CA_CERTS` hace que Node,
  npm, Playwright y Claude Code confíen en ella (documentación de Claude Code, "TLS or SSL connection errors");
  `PIP_CERT` y `REQUESTS_CA_BUNDLE`, que lo haga `pip`.
- Si el proxy no necesita certificado propio, saltá el punto 1 y quitá las dos últimas líneas `export` del bloque.
- Si el proxy pide usuario y contraseña, **no** los escribas en `~/.bashrc`: pedile a TI una alternativa (proxy sin
  autenticación para la red interna o autenticación integrada).
- Si `env | grep -i proxy` ya muestra el proxy (WSL puede copiarlo de Windows con `autoProxy`, activo por defecto
  según Microsoft), no repitas el punto 3 salvo las líneas del certificado **[verificar en tu red]**.
- Si un sitio responde `403` aun con el proxy configurado, la política de la red lo bloquea: pedí a TI que habilite
  los dominios de la tabla siguiente; no intentes saltear el proxy.

| Dominio | Lo necesita |
|---|---|
| `archive.ubuntu.com`, `security.ubuntu.com` | `apt` |
| `pypi.org`, `files.pythonhosted.org` | paquetes de Python (§3.2) |
| `raw.githubusercontent.com`, `github.com` | nvm, clonar pm-method, plugin desde GitHub, Hermes |
| `nodejs.org` | Node.js con nvm (§4.2) |
| `registry.npmjs.org` | Mermaid, pptxgenjs, BMAD, Claude Code por npm |
| `cdn.playwright.dev`, `playwright.download.prss.microsoft.com` | navegador de Playwright (§4.1) |
| `storage.googleapis.com` | Chrome de Mermaid/puppeteer (§4.3) |
| `claude.ai`, `downloads.claude.ai`, `api.anthropic.com` | instalar Claude Code, iniciar sesión y usarlo |
| `hermes-agent.nousresearch.com` | instalador de Hermes |

### 9.3 DNS de WSL

Síntoma: `Temporary failure resolving 'archive.ubuntu.com'` o `Could not resolve host`, aunque Windows navega bien
(habitual con VPN). Primero probá cerrar WSL (**[Windows]** `wsl --shutdown`), esperar 8 segundos y volver a abrir.
Si sigue, fijá vos el servidor DNS (pedile a TI el de tu red; `1.1.1.1` es un servidor público):

```bash
printf '\n[network]\ngenerateResolvConf=false\n' | sudo tee -a /etc/wsl.conf
```

En **[Windows]** `wsl --shutdown`; al volver a abrir Ubuntu:

```bash
sudo rm -f /etc/resolv.conf
echo "nameserver <ip-del-dns>" | sudo tee /etc/resolv.conf
```

**[verificar]** en tu red. Para volver al comportamiento por defecto, borrá la sección `[network]` de `/etc/wsl.conf`
(`sudo nano /etc/wsl.conf`) y `wsl --shutdown`.

### 9.4 Reloj desfasado

Después de suspender o hibernar la PC, el reloj de WSL puede quedar atrasado y fallan el inicio de sesión, los tokens y
los certificados. Comparalo con Windows (`date`) y corregilo (comando que recomienda la guía de WSL de Hermes Agent
**[verificar]**):

```bash
sudo hwclock -s
date
```

Con systemd activo (§2.2) también sirve `sudo systemctl restart systemd-timesyncd`. Si nada lo corrige,
**[Windows]** `wsl --shutdown` y volvé a abrir Ubuntu **[verificar]**.

### 9.5 El navegador no inicia (capturas o Mermaid)

1. **Bibliotecas faltantes** (`error while loading shared libraries`, `Host system is missing dependencies`):
   `python3 -m playwright install-deps chromium` (pide `sudo`).
2. **Navegador no descargado** (`Executable doesn't exist`, `Could not find Chrome`): para Playwright,
   `python3 -m playwright install --only-shell chromium`; para Mermaid, con el `puppeteer` que trae mermaid-cli (así
   baja la versión de Chrome que ese `puppeteer` espera), `cd "$(npm root -g)/@mermaid-js/mermaid-cli" && npx puppeteer
   browsers install chrome-headless-shell` (en una red con proxy, después de §9.2). Si la red lo bloquea, termina con
   `Error: All providers failed for chrome-headless-shell …`.
3. **Ruta temporal larga**: Chromium no arranca si la ruta de su *socket* supera unos 107 caracteres, lo que pasa con
   un `TMPDIR` largo. Probá con `TMPDIR=/tmp` delante del comando (por ejemplo
   `TMPDIR=/tmp python3 scripts/validar_mermaid.py --render`).
4. Mientras tanto, `python3 scripts/validar_mermaid.py` (sin `--render`) hace el control estático y los bloques Mermaid
   de los `.md` siguen siendo válidos.

### 9.6 nvm o Node equivocados

```bash
grep -n NVM_DIR ~/.bashrc
which -a node npm
```

- Si `grep` no muestra nada, el instalador de nvm no escribió en `~/.bashrc`: agregá las líneas de carga que indica la
  documentación de Claude Code ("nvm version conflicts") y abrí una terminal nueva:

```bash
cat >> ~/.bashrc <<'EOF'
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
EOF
```

- Si `which -a node` lista primero `/usr/bin/node` (Node de Ubuntu) o una ruta `/mnt/c/…` (Node de Windows, que WSL
  agrega al PATH): `nvm use default` y `nvm alias default 22`; si persiste, quitá el Node de Ubuntu con
  `sudo apt remove nodejs`. No desactives la integración del PATH de Windows (`appendWindowsPath=false`): impide abrir
  programas de Windows desde Ubuntu (documentación de Claude Code).

### 9.7 `claude` no se encuentra

```bash
ls -la ~/.local/bin/claude
echo "$PATH" | tr ':' '\n' | grep -Fx "$HOME/.local/bin"
```

- Si el primer comando muestra el archivo y el segundo no imprime nada, falta `~/.local/bin` en el PATH (comando de la
  documentación oficial de Claude Code):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

- Si `~/.local/bin/claude` no existe: no hay instalación nativa; repetí §6.1 (o, si lo instalaste con npm, comprobá que
  nvm esté cargado: §9.6).
- Para ver todas las instalaciones: `which -a claude` y `npm -g ls @anthropic-ai/claude-code`. Dejá una sola (§10.3).

### 9.8 Espacio en disco

```bash
df -h ~
du -sh ~/.cache ~/.nvm ~/.venvs ~/.npm 2>/dev/null
```

Para liberar: `sudo apt clean`, `npm cache clean --force`, `python3 -m pip cache purge` y borrar `~/pm-pruebas`. El
disco virtual de WSL (un archivo `ext4.vhdx` en Windows) **no se achica solo** al borrar archivos. Para recuperar ese
espacio en Windows, con WSL cerrado (`wsl --shutdown`): `wsl --manage Ubuntu-24.04 --set-sparse true` **[verificar que
tu versión de WSL tenga la opción: `wsl --help`]**.

### 9.9 Finales de línea (CRLF)

Síntoma: `bad interpreter: /bin/sh^M` o `/usr/bin/env: 'python3\r': No such file or directory`. Pasa cuando un
archivo se editó o se clonó con herramientas de Windows. Lo más seguro es volver a clonar desde Ubuntu (§5.1, después
de `mv ~/pm-method ~/pm-method.anterior`). Para un archivo suelto:

```bash
sed -i 's/\r$//' <archivo>
```

Si `git status` muestra archivos modificados sin cambios reales: `git -C ~/pm-method diff --stat` y, si solo son finales
de línea o permisos, `git -C ~/pm-method config core.fileMode false` y `git -C ~/pm-method checkout -- .` (descarta
cambios locales: hacelo solo si no modificaste nada a propósito).

### 9.10 Antivirus y Microsoft Defender

- Dentro de Ubuntu los archivos están en un disco virtual; el antivirus de Windows los analiza sobre todo cuando se
  acceden desde Windows (`\\wsl.localhost\…`) o cuando trabajás en `/mnt/c`. Trabajar en `~` (§2.3) evita la mayor
  parte de la lentitud.
- Si el antivirus bloquea o pone en cuarentena algo durante la instalación, no lo desactives: anotá el archivo y el
  mensaje y consultá con TI. Excluir carpetas del análisis es una decisión de seguridad de tu organización.

---

## 10. Actualizar, desinstalar o empezar de cero

### 10.1 Actualizar · [Ubuntu]

| Qué | Cómo |
|---|---|
| Ubuntu | `sudo apt update && sudo apt upgrade -y` |
| WSL | [Windows] `wsl --update` |
| Claude Code (instalador nativo) | se actualiza solo; para forzarlo, `claude update` |
| Claude Code (npm) | `npm install -g @anthropic-ai/claude-code@latest` |
| Plugin pm-method | `claude plugin marketplace update pm-method` y `claude plugin update pm-method@pm-method`; reiniciá Claude Code y comprobá con `claude plugin list` |
| Clon de pm-method | `git -C ~/pm-method pull` |
| Hermes | `hermes update`; después, `python3 ~/pm-method/scripts/instalar_hermes.py` y `/reload-skills` |
| Paquetes de Python | `python3 -m pip install --upgrade <paquete>==<versión>` con el entorno activo; repetí §5.3 |
| Node.js | `nvm install 22` (trae la última 22.x) y `nvm alias default 22`; repetí §4.3, porque los paquetes globales son por versión de Node |

Después de actualizar pm-method: la sanidad completa en cada proyecto activo ([INSTALACION
§10](INSTALACION.md#10-actualización-y-migración)).

### 10.2 Desinstalar pm-method

```bash
claude plugin uninstall pm-method@pm-method
claude plugin marketplace remove pm-method
rm -rf ~/.hermes/skills/pm-method
```

Las carpetas de proyecto no se tocan: son Markdown, CSV y JSON legibles sin el paquete.

### 10.3 Desinstalar las herramientas

| Qué | Comando |
|---|---|
| Claude Code nativo | `rm -f ~/.local/bin/claude && rm -rf ~/.local/share/claude` |
| Claude Code por npm | `npm uninstall -g @anthropic-ai/claude-code` |
| Configuración e inicio de sesión de Claude Code (borra ajustes, MCP e historial) | `rm -rf ~/.claude && rm -f ~/.claude.json` |
| Hermes | `hermes uninstall` |
| Entorno de Python | `rm -rf ~/.venvs/pm-method` y quitar la línea de activación: `sed -i '\#source ~/.venvs/pm-method/bin/activate#d' ~/.bashrc` |
| Node.js y nvm | `rm -rf ~/.nvm` y quitar las líneas de carga de nvm: `sed -i '/NVM_DIR/d' ~/.bashrc` |
| Navegadores sin interfaz | `rm -rf ~/.cache/ms-playwright ~/.cache/puppeteer` |

Comandos de Claude Code tomados de su documentación oficial ("Uninstall Claude Code"); el de Hermes, de su referencia
de comandos.

### 10.4 Empezar de cero (irreversible)

Borra la Ubuntu entera con todo lo que tenga adentro (proyectos incluidos). Antes, guardá una copia. En
**[Windows]** PowerShell:

```powershell
wsl --shutdown
wsl --export Ubuntu-24.04 "$env:USERPROFILE\respaldo-ubuntu-24.04.tar"
wsl --unregister Ubuntu-24.04
```

Después, repetí desde §1.2. Para recuperar la copia en lugar de reinstalar:
`wsl --import Ubuntu-24.04 "$env:USERPROFILE\WSL\Ubuntu-24.04" "$env:USERPROFILE\respaldo-ubuntu-24.04.tar"`
**[verificar]**: comandos de la documentación de WSL (`wsl --help`), no ejecutados en el entorno de prueba.

---

## 11. Qué se verificó y qué queda por comprobar

Verificación del 2026-10-27 en una **Ubuntu 24.04 LTS limpia** (generada con `debootstrap` desde `archive.ubuntu.com`
con la firma del archivo verificada) dentro de un contenedor de Docker como sustituto de WSL2 (Linux x86_64, sin el
filtro seccomp, para que el navegador pueda usar su aislamiento como en WSL2), con un usuario sin privilegios (`sudo`
sin contraseña) y detrás de un proxy con inspección TLS configurado con el bloque del §9.2. Los bloques de comandos de
§2 a §7, el del §9.2, los de diagnóstico de §9.6 a §9.8 y los de §10.2 y §10.3 (y los comandos de [Ubuntu] de la tabla
del §8) se extrajeron de este documento con un script y se ejecutaron tal cual, cada uno en una terminal de inicio de
sesión nueva; solo se reemplazaron los marcadores `<…>`.

**Resultado: 45 de 45 comprobaciones como se esperaba** (incluidos los fallos esperados por la red de prueba, marcados
abajo), en unos 13 minutos de ejecución, más las desinstalaciones de §10.2 y §10.3.

| Paso | Resultado | Versión |
|---|---|---|
| §9.2 proxy y certificado de la CA | `1 added, 0 removed; done.`; `pypi.org` → `200` a través del proxy | — |
| §2.1 `apt update` y `apt upgrade` | sin errores | Ubuntu 24.04 LTS |
| §2.2 systemd | el bloque agrega `[boot]` `systemd=true` a `/etc/wsl.conf`; el efecto (`ps -p 1` → `systemd`) no se puede ver en un contenedor **[verificar]** | — |
| §2.4 git | las cinco claves, como se esperaba | git 2.43.0 |
| §2.5 hora e idioma | la imagen mínima no traía `LANG`: la línea del §2.5 lo dejó en `C.UTF-8` | tzdata 2026 |
| §3.1 paquetes | sin errores; `pip` fuera del entorno responde `error: externally-managed-environment` | Python 3.12.3 |
| §3.2 entorno virtual | `Successfully installed …`; `which python3` → el del entorno; `paquetes OK` | pyyaml 6.0.3 · python-docx 1.2.0 · openpyxl 3.1.5 · matplotlib 3.11.2 · playwright 1.56.0 |
| §4.1 navegador | `--with-deps` instaló 86 paquetes con `sudo`; `captura OK` | Chromium headless shell 1194 (¹) |
| §4.2 nvm y Node | `nvm install 22` con suma SHA-256 verificada; `which node` bajo `~/.nvm` | nvm 0.40.8 · Node 22.22.0 · npm 10.9.4 (²) |
| §4.3 Mermaid y pptxgenjs | `mmdc --version` → `11.16.0`; diagrama de prueba dibujado | mermaid-cli 11.16.0 (puppeteer 25.16.0) · pptxgenjs 4.0.1 (³) |
| §4.4 LibreOffice | `soffice --version` | LibreOffice 24.2.7.2 |
| §5.1–§5.2 clon, validación y lanzador de hooks | `"version": "2.4.0"`; `OK`; `hooks/py.sh` → Python del entorno | pm-method 2.4.0 (GitHub) |
| §5.3 pruebas del paquete | `Resultado: 353 OK · 0 FALLO`; `OK · 128 bloques Mermaid · 0 error(es)`; `5` recorridos E2E `OK` con 51 imágenes; `Resultado: 5/5 caso(s) sin errores` | 286 s en total |
| §5.4 proyecto con scripts | `0 ERROR · 0 AVISO · 1 INFO` (ESP-02) | — |
| §6.1 instalador nativo de Claude Code | `curl: (22) … 403`: `downloads.claude.ai` bloqueado en la red de prueba **[verificar]** | — |
| §6.1 alternativa npm | `2.1.311 (Claude Code)`; `claude doctor` → `No installation issues found.` | Claude Code 2.1.311 |
| §6.2 antes del inicio de sesión | `ANTHROPIC_API_KEY:` vacío; `"loggedIn": false` | — |
| §6.3 plugin desde GitHub | `pm-method@pm-method` · `Version: 2.4.0` · `Status: ✔ enabled` | — |
| §6.4 deshabilitar y habilitar | `✘ disabled` y luego `✔ enabled` | — |
| Hooks de la copia instalada (sin sesión) | `hooks/py.sh` usa el Python del entorno; `guardian.py` devuelve `deny` ante una escritura de `estado.json`; `inicio.py` imprime `pm-method · proyecto …` | — |
| §6.6 BMAD | `_bmad/`, 29 skills `bmad-*`; `detectar` → `v6`, `6.12.4`, `soportada` | bmad-method 6.12.4 |
| §7.1 instalador de Hermes | `curl: (22) … 403`: `hermes-agent.nousresearch.com` bloqueado en la red de prueba **[verificar]** | — |
| §7.3 `instalar_hermes.py` | `39 skills y 6 agentes`, `Listo: 39 skills (58 archivos adaptados)`, conteo `39` | — |
| §7.4 `estado.py contexto` y `radar` desde la copia para Hermes | resumen y radar del proyecto de §5.4 | — |
| §8 filas de [Ubuntu] 2 a 14 | todas como se esperaba, salvo la 12 (`"loggedIn": false`, sin cuenta) | — |
| §10.2 y §10.3 | plugin y catálogo quitados (`No plugins installed.`); Claude Code, entorno de Python, nvm y navegadores borrados; `~/.bashrc` sin las líneas del entorno ni de nvm | — |
| Espacio | unos 4,7 GB agregados a la Ubuntu mínima, con LibreOffice y la caché de `apt` (`~/.nvm` 1 GB, `~/.npm` 440 MB, `~/.cache` 420 MB, `~/.venvs` 340 MB, `~/.claude` 260 MB, `~/pm-method` 250 MB; paquetes del sistema: git y Python 450 MB, bibliotecas del navegador 350 MB, LibreOffice 450 MB) | — |

Lo que la red de prueba bloqueaba se reemplazó así, sin cambiar los comandos de la guía:
(¹) sin acceso a la descarga de Playwright, se copió en `~/.cache/ms-playwright/` la misma revisión 1194 antes del §4.1:
`playwright install` la reconoció como instalada e instaló igual las bibliotecas con `apt`; (²) sin acceso a
`nodejs.org`, nvm descargó Node 22.22.0 de un espejo local (`NVM_NODEJS_ORG_MIRROR`) armado con el binario oficial
publicado en npm (`node-linux-x64@22.22.0`); (³) sin acceso a `storage.googleapis.com`, `npm install` terminó sin error
pero sin el Chrome de puppeteer (lo que advierte el §4.3), y el render se probó con `PUPPETEER_EXECUTABLE_PATH`
apuntando al navegador del §4.1; el comando de recuperación del §9.5 se ejecutó hasta la descarga. Las fuentes de `apt`
usaron `https://`, porque el proxy de prueba solo admitía HTTPS; Ubuntu en WSL usa `http://archive.ubuntu.com`, cubierto
por la línea `Acquire::http::Proxy` del §9.2.

**Queda por comprobar en tu equipo [verificar]** (cada paso dice cómo): todo lo de Windows (§1, `.wslconfig`, la
actualización de WSL, el Explorador en `\\wsl.localhost\…`, `wsl --shutdown`, `wsl --export` y `--unregister`, `wsl -u
root`), el efecto de systemd (§2.2), el instalador nativo de Claude Code (§6.1), el inicio de sesión y la primera
conversación (§6.2 y §6.5), la instalación de Hermes, `hermes model`, `hermes
skills list` y una conversación en Hermes (§7), los arreglos de DNS y de reloj (§9.3 y §9.4), la descarga del Chrome de
Mermaid (§4.3) y `wsl --manage --set-sparse` (§9.8).

---

## 12. Seguridad

- **Credenciales solo en su lugar**: la sesión de Claude Code en `~/.claude/` (la crea el inicio de sesión); una clave
  de API, si la usás, como variable de entorno de tu usuario; las de Hermes en `~/.hermes/.env`; las de la capa de
  canales de pm-method (`PM_SMTP_*`, webhooks) como variables de entorno. Nunca en carpetas de proyecto, en
  `estado.json`, en los registros, en el repositorio ni en commits. Tabla completa: [INSTALACION
  §0.7](INSTALACION.md#07-claves-de-api-y-credenciales-cuáles-dónde-y-cómo).
- **Nunca pegues** contraseñas, claves de API, tokens, el código de inicio de sesión, códigos de verificación en dos
  pasos ni el contenido de `~/.claude/.credentials.json` o `~/.hermes/.env` en un chat (tampoco con Claude u otro
  asistente), en un correo ni en un *issue*. Si una clave se expuso: revocala en su consola de origen y creá otra.
- **No compartas** la carpeta `~/.claude`, `~/.claude.json`, `~/.hermes`, la copia de §10.4 ni capturas de pantalla
  de `/status` o `hermes config` con datos de cuenta.
- Instalá solo desde las fuentes de esta guía. Los instaladores por `curl … | bash` ejecutan código con tu usuario: si
  querés revisarlos antes, descargalos (`curl -fsSL <url> -o instalador.sh`), leelos y ejecutalos con `bash
  instalador.sh`.
- `sudo` solo donde la guía lo indica (paquetes del sistema). Nunca `sudo pip` ni `sudo npm`.
- Revisá cualquier skill, plugin o servidor MCP externo antes de instalarlo: corre con los permisos del agente.
  Revisión de seguridad del paquete: [SEGURIDAD.md](SEGURIDAD.md).
- Los hooks de pm-method protegen la integridad del método frente a errores del modelo; no son una frontera de
  seguridad (SEGURIDAD, SEG-09). Para aislar lo que ejecuta el agente, usá el camino Docker
  ([INSTALACION-DOCKER](INSTALACION-DOCKER.md)).
