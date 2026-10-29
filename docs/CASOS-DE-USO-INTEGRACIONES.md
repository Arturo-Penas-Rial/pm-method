# Casos de uso de integraciones · pm-method 2.6.0

Casos trabajados para cada repositorio o integración externa que pm-method incorpora, con más detalle en diseño visual,
informes, planificación, OKR y canales de envío a interesados (correo, Teams, Slack, `.eml`). Cada caso dice en qué
momento del ciclo PRINCE2 se usa, qué skill y qué agente son dueños, qué herramienta externa interviene, cuál es el
respaldo interno cuando no está instalada, qué comandos se ejecutan, qué queda en la carpeta del proyecto, qué controles
aplican y qué límites tiene.

EN: worked examples for every external repository and integration (visual design, reports, planning, OKR, meetings,
trackers, BMAD and the delivery channels layer), with the PRINCE2 moment, owner skill and agent, fallback, real commands,
outputs, controls and limits.

Regla de evidencia de este documento. Las salidas de scripts que se muestran son reales y están recortadas: se
obtuvieron el 2026-10-17 corriendo los scripts del paquete sobre un proyecto temporal (ver "Proyecto de prueba"). Lo
que se dice de las skills externas en sesiones de Claude Code sale de `docs/INTEGRACIONES.md` §3.1 y de los registros
de esas sesiones (A0–G1). Los casos 8 y 9 usan la corrida de referencia de la guía E2E-3
(`docs/guias/evidencia/salida-g3.md`) y una corrida complementaria del mismo día sobre esa carpeta; el correo y los
webhooks se probaron contra servidores de prueba en 127.0.0.1, no contra servicios reales. Lo que no se pudo verificar
se marca **[sin verificar en vivo]** o **[verificar]**. Los nombres de personas y la cooperativa son ficticios, igual
que en `CASOS-DE-USO.md`.

Estados de verificación usados en todo el documento:
- **verificado en vivo**: una sesión real de Claude Code con el plugin invocó la integración y produjo la salida.
- **probado con scripts**: se corrieron los scripts (del paquete o del repositorio externo) y se revisó la salida, sin
  una sesión de Claude Code que decida la delegación.
- **documentado sin prueba en vivo**: el contrato está escrito en el paquete, pero no hubo herramienta conectada.

Cómo recorrer cada caso como usuario: cada caso (o subcaso) empieza por **Prompt del usuario**, el o los mensajes en
lenguaje natural que escribís en Claude Code, con el atajo `/pm-method:…` cuando existe; lo único que se teclea fuera
de la conversación va marcado "en tu terminal:" (instalaciones y `claude mcp add`). Sigue **Respuestas del usuario**
(qué contestar cuando el sistema pregunta o necesita una decisión humana) y **Entradas (qué aporta el usuario y
cómo)**: dato escrito en el prompt, respuesta a una pregunta del orquestador, archivo que dejás en una ruta concreta o
adjuntás en la sesión, dato traído por un conector MCP (queda como instantánea fechada en
`gestion/03-control/fuentes/<sistema>-AAAA-MM-DD.(csv|md|json)`, SPEC §1.12) o dato leído de BMAD por la fachada, en
solo lectura. Los bloques de comandos de "Pasos" los ejecuta el sistema; el usuario no los escribe. **Salidas (qué
queda y dónde verificarlo)** da la ruta (las rutas sin prefijo son relativas a la carpeta del proyecto `gestion/`), la
clave en `gestion/estado.json` y cómo comprobarlo: abrir el archivo, abrir el CSV de `gestion/03-control/registros/` en
un editor o Excel, buscar la fila en `decisiones.csv` o la nota en `diario.md` (misma carpeta), o pedir
`/pm-method:pm-estado`.

## Índice

1. [Diseño visual](#caso-1--diseño-visual-pm-visuales): archify, diagram-design, visual-explainer, tablero HTML, drawio-mcp, Mermaid
2. [Reportes](#caso-2--reportes-checkpoint-highlight-excepción-fin-de-etapa-y-exportación): checkpoint, highlight con EVM, excepción, fin de etapa, exportación Office
3. [Planificación](#caso-3--planificación-wbs-camino-crítico-ms-project-presupuesto-y-release-plan): WBS, camino crítico, MS Project (MSPDI), presupuesto, release plan
4. [OKR](#caso-4--okr-ligados-a-beneficios-con-tability-opcional): `okr.py`, vínculo con beneficios y métricas, Tability
5. [Transcripciones y reuniones](#caso-5--transcripciones-y-actas-de-reunión): `transcripcion.py`, Granola, Fireflies, Zoom, minutes
6. [Trackers y canales](#caso-6--trackers-documentación-y-canales-jira-confluence-slack-teams): Jira, Confluence, Slack, Teams
7. [BMAD](#caso-7--bmad-como-capa-de-especificación-pm-bmad-puente): `bmad.py` sobre el fixture real 6.12.4
8. [Capa de canales](#caso-8--capa-de-canales-correo-smtp-conector-de-correo-teams-slack-y-eml): `envios.py` con correo SMTP propio, conector Gmail u Outlook, webhook de Teams (Workflows), webhook de Slack y `.eml` sin configuración
9. [OKR con Tability o Perdoo](#caso-9--okr-con-tability-o-perdoo-servidores-mcp-oficiales): `okr.py --propuesta-sync` y `--marcar-publicado`
10. [Matriz de cierre](#matriz-de-cierre)

### Qué repo cubre cada caso

| Caso | Repositorio o integración externa | Distribución · licencia | Skill pm-* dueña |
|---|---|---|---|
| 1.1 | `tt-a1i/archify` | carpeta de skill · MIT | pm-visuales |
| 1.2 | `cathrynlavery/diagram-design` | plugin con marketplace · MIT | pm-visuales |
| 1.3 | `nicobailon/visual-explainer` | plugin con marketplace · MIT | pm-visuales |
| 1.4 | ninguno (plantilla interna `tablero-avance.html`) | — | pm-visuales |
| 1.5 | drawio-mcp (servidor MCP) | MCP | pm-visuales / pm-integraciones |
| 1.6 | Mermaid (respaldo; `mmdc` opcional) | — | pm-visuales |
| 2.x | `anthropics/skills` (`docx`, `xlsx`, `pptx`) | propietaria, source-available · plugin `document-skills` | pm-exportar (contenido: pm-progreso-reportes) |
| 3.2 | MSPDI propio, validado con MPXJ (PyPI `mpxj`, LGPL, Java) | formato abierto | pm-cronograma-estimacion |
| 4 | Tability MCP (servidor oficial) | MCP | pm-okr (vía pm-integraciones) |
| 5 | Granola, Fireflies, Zoom, minutes (`minutes-mcp`) | MCP | pm-reuniones (vía pm-integraciones) |
| 6 | Atlassian Rovo MCP (Jira, Confluence), Slack MCP, Teams/Work IQ | MCP | pm-integraciones |
| 7 | BMAD Method (`bmad-method` 6.12.4 y v4) | marco, solo lectura | pm-bmad-puente |
| 8.1 | servidor SMTP de la organización | protocolo estándar (`smtplib`) | pm-integraciones (`envios.py`; contenido: pm-comunicacion-stakeholders) |
| 8.2 | conector de correo Gmail u Outlook | MCP o conector de la aplicación | pm-integraciones |
| 8.3 | Teams Workflows ("When a Teams webhook request is received") | webhook HTTP | pm-integraciones |
| 8.4 | webhook entrante de Slack | webhook HTTP | pm-integraciones |
| 8.5 | ninguno (archivo `.eml`) | — | pm-integraciones |
| 9.1 | Tability MCP (`https://mcp.tability.app/mcp`) | MCP oficial | pm-okr (vía pm-integraciones) |
| 9.2 | Perdoo MCP (`https://mcp.perdoo.com`) | MCP oficial | pm-okr (vía pm-integraciones) |

---

## Proyecto de prueba y convenciones

Se copió el fixture real `scripts/pruebas/fixtures/bmad-v6.12-real` (generado con `npx bmad-method@6.12.4 install` y
las skills de BMAD; ver su `README.md`) a una carpeta temporal `portal-socios/`, sin modificar el original, y se creó la
carpeta de gestión adentro. Las variables son las de `CASOS-DE-USO.md`:

```bash
PM="${CLAUDE_PLUGIN_ROOT}/skills"          # manual: ~/.claude/skills · Hermes: ~/.hermes/skills
E="$PM/pm-estado-proyecto/scripts"; B="$PM/pm-bmad-puente/scripts/bmad.py"
X="$PM/pm-exportar/scripts/paquete.py"; O="$PM/pm-okr/scripts/okr.py"; T="$PM/pm-reuniones/scripts/transcripcion.py"

cd portal-socios
python3 $E/nuevo_proyecto.py --ruta gestion --nombre "Portal de autoservicio para socios" --idioma es \
    --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez"
python3 $B --proyecto gestion detectar               # "version": "6.12.4", "version_fuente": "_bmad/_config/manifest.yaml", "soporte": "soportada"
python3 $E/estado.py --proyecto gestion integracion especificacion=bmad
python3 $E/estado.py --proyecto gestion rol ejecutivo="Laura Méndez" gestor_proyecto="Martín Suárez" \
    usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" aseguramiento="Andrea Costa" \
    autoridad_cambio="Sofía Ramírez" product_owner="Sofía Ramírez" jefes_equipo="Lucía Benítez"
python3 $E/estado.py --proyecto gestion tolerancia --nivel proyecto tiempo="±2 semanas" costo="±10 %"
python3 $E/estado.py --proyecto gestion tolerancia --nivel etapa tiempo="±10 %" costo="±5 %"
python3 $E/estado.py --proyecto gestion agil cadencia_iteracion_dias=14 velocidad_referencia=30
```

Las puertas (`estado.py puerta …`), `rol`, `tolerancia` y `agil` se corrieron a mano para preparar el escenario; en
operación normal los ejecuta solo `pm-director` tras la decisión humana (el hook `guardian.py` se lo impide a los demás
subagentes). Los registros se cargaron con `registro.py` (R-001, R-002, A-001, A-002, I-001), nunca editando los CSV.

Ejemplos reales guardados en `docs/ejemplos/integraciones/` (rutas absolutas reemplazadas por `<repo>`):

| Archivo | Producido por |
|---|---|
| `gantt-cpm.md`, `cronograma-mspdi.xml` | `cpm.py --mermaid --mspdi --wbs` (caso 3.2) |
| `archify-wbs-finalize-summary.json` | `archify.mjs finalize tree` sin Chrome (caso 1.1) |
| `okr-puntuado.md` | `okr.py --markdown` (caso 4) |
| `transcripcion-checkpoint.md` | `transcripcion.py` sobre un VTT (caso 5) |
| `handoff-bmad-prioridades.md`, `avance-bmad.csv` | `bmad.py handoff` y `bmad.py avance` (caso 7) |
| `sanidad-integraciones.md` | `sanidad.py --informe` con integraciones declaradas (casos 1, 2 y 6) |

---

## Caso 1 · Diseño visual (pm-visuales)

Contrato común (guía de pm-visuales §1.3): primero el respaldo (tabla intermedia y Mermaid en `<carpeta>/<nombre>.md`),
después se invoca la skill externa con la herramienta Skill por su nombre real, con ruta de salida, idioma, título
bilingüe, ids de la fuente, BORRADOR si la fuente no está aprobada, fuente y fecha de corte. La salida va a
`02-planificacion/visuales/<nombre>.html` (planes) o `03-control/reportes/AAAA-MM-DD-<nombre>.html` (tablero), con los
subproductos del motor al lado. Si el motor falta, no cubre el tipo o falla dos veces: queda el Mermaid y una nota en
`diario.md`. Un visual nunca cambia el estado de nada: hereda el de su fuente y lo comparte el gestor tras confirmarlo.

Declarar el motor (uno o una lista por prioridad) y comprobar la instalación. Los ejecuta el sistema cuando lo pedís por
prompt ("Usá archify y visual-explainer como motores de diagramas y revisá que estén instalados"); el usuario no los
escribe:

```bash
python3 $E/estado.py --proyecto gestion integracion diagramas=archify,visual-explainer export=skills-office
python3 $E/sanidad.py --proyecto gestion | grep INS-03
```

Salida real, primero sin las skills y después con ellas copiadas en `.claude/skills/` del repositorio (lo mismo que deja
`npx skills add` sin `-g`):

```text
AVISO INS-03 integraciones.diagramas = archify, pero no se encontró la skill 'archify' (ni '<plugin>:archify') en .claude/skills del proyecto, ~/.claude/skills ni en los plugins instalados.
      → Instalarla (docs/INSTALACION.md §6.1) o volver al respaldo (estado.py integracion diagramas=mermaid). Si se carga con --plugin-dir, ignorar este aviso.
...
INFO  INS-03 Skill externa 'archify' (archify) instalada: invocar como 'archify' · proyecto (<repo>/.claude/skills) · …/archify/SKILL.md
INFO  INS-03 archify: no se encontró Chrome/Chromium; su verificación en navegador (browser-check) quedará omitida.
INFO  INS-03 Skill externa 'visual-explainer' (visual-explainer) instalada: invocar como 'visual-explainer' · proyecto (<repo>/.claude/skills) · …
```

### 1.1 archify: organigrama y WBS como diagrama de árbol

- **Prompt del usuario:**
  1. En tu terminal (una sola vez): `npx skills add tt-a1i/archify -a claude-code -s archify -y` (ver Externa).
  2. "Usá archify como motor de diagramas del proyecto y revisá que esté instalada." (el sistema registra `integraciones.diagramas=archify` y corre la sanidad INS-03; atajo para el chequeo: `/pm-method:pm-sanidad`).
  3. "Hacé el organigrama del proyecto y el diagrama de la WBS."
- **Entradas (qué aporta el usuario y cómo):** el motor elegido, escrito en el prompt 2; los roles ya cargados en `gestion/estado.json` → `roles` (Laura Méndez, Martín Suárez, Sofía Ramírez, Diego Ferreira, Andrea Costa; un rol vacío sale `[por confirmar]`, guía de pm-visuales §6); la WBS de `gestion/02-planificacion/wbs.csv` (caso 3.1). No hace falta adjuntar nada. Si Chrome no está en la ruta habitual, el usuario define `ARCHIFY_CHROME=<ejecutable>` en su terminal antes de abrir Claude Code.
- **Objetivo:** organigrama y WBS en HTML interactivo validado por el propio motor, con los ids de la WBS en cada nodo.
- **Momento PRINCE2:** organigrama en SU (pm-organizacion-roles lo pide para `autorizar-inicio`); WBS en IP, como parte del plan que la junta aprueba en `autorizar-proyecto`. Decide la ejecutiva; el visual no se aprueba por separado.
- **Dueña y agente:** `pm-visuales`; la invoca el orquestador directamente o `pm-inicio` / `pm-planificacion` (paso 10 de su bucle). El contenido de la WBS es de `pm-planificacion-por-productos`.
- **Externa:** archify 3.1 (`tt-a1i/archify`, MIT). Tipos útiles: `tree` (organigrama, WBS), `workflow`, `timeline`. Instalación (INSTALACION §6.1): `npx skills add tt-a1i/archify -a claude-code -s archify -y`. Requiere Node ≥ 18 y Chrome/Chromium (o `ARCHIFY_CHROME=<ejecutable>`).
- **Respaldo:** `wbs.py --mermaid` para la WBS y `templates/diagramas-mermaid.md` §1 para el organigrama.
- **Frase:** "Hacé el organigrama del proyecto y el diagrama de la WBS" (la usada en la sesión en vivo). EN: "Draw the project org chart and the WBS diagram."
- **Pasos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  cd gestion
  python3 $E/wbs.py 02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" \
      --mermaid 02-planificacion/visuales/wbs.md --diccionario 02-planificacion/diccionario-wbs-esqueleto.md
  # pm-visuales escribe 02-planificacion/visuales/wbs.candidate.json (esquema schemas/tree.schema.json de archify,
  # un nodo por fila de wbs.csv, meta.output = 02-planificacion/visuales/wbs.html) y luego:
  ARCHIFY_UPDATE_CHECK_DISABLED=1 node ../.claude/skills/archify/bin/archify.mjs finalize tree \
      02-planificacion/visuales/wbs.candidate.json 02-planificacion/visuales/wbs.html --quality showcase --json
  python3 $E/estado.py --proyecto . artefacto pbs-wbs --ruta 02-planificacion/visuales/wbs.html --estado borrador
  ```
  Salida real de `finalize` en este entorno, que no tiene Chrome (completa en `docs/ejemplos/integraciones/archify-wbs-finalize-summary.json`):
  ```text
  "ok":false,"status":"skipped","type":"tree", … "gates":{"validate":"pass","deliver":"pass","check":"pass","browser-check":"skipped"},
  "failedStage":"browser-check","diagnostics":[{"code":"viewer/chrome-unavailable","severity":"warning", …
  ```
- **Salidas (qué queda y dónde verificarlo):** `02-planificacion/visuales/wbs.html` (830.803 bytes, 16 nodos), `wbs.md` (Mermaid de respaldo) y, al lado, `wbs.candidate.json`, `wbs.finalize.json`, `wbs.finalize-summary.json`, `wbs.delivery.json`, `wbs.browser-check.json`. En la sesión en vivo (A1) los cuatro gates quedaron en `pass` y se generaron `organigrama.html` y `wbs.html` con sus `.md`. Dónde verificarlo: abrí `gestion/02-planificacion/visuales/wbs.html` y `organigrama.html` en el navegador (cada nodo de la WBS lleva su código de `wbs.csv`); en `gestion/estado.json` → `artefactos`, las claves `pbs-wbs` y `organigrama` con estado `borrador`; si archify faltó o falló, la nota queda en `gestion/03-control/registros/diario.md` y se entrega el `.md`.
- **Controles:** INS-03 (instalada / Chrome); guía §1.4: éxito = `"ok": true` con los cuatro gates en `pass`; con solo `browser-check` en `skipped` por falta de Chrome, vale como "verificado sin navegador" y se dice. `estado.py artefacto` registra el visual como borrador.
- **Límites:** el árbol `tree` es de un solo padre: aseguramiento y soporte se cuelgan de la junta o del gestor y se aclara en el pie (lo señaló la sesión A1). archify no cubre mapa poder/interés ni one-pager. Antes de los ajustes del contrato (sesión A0) se usó el binario de archify sin invocar la skill: la regla actual es invocarla siempre.

### 1.2 diagram-design: organigrama, flujo de excepciones y roadmap editoriales

- **Prompt del usuario:**
  1. En tu terminal (una sola vez): `claude plugin marketplace add cathrynlavery/diagram-design` y `claude plugin install diagram-design@diagram-design` (o la copia con `npx skills add …`, ver Externa).
  2. "Usá diagram-design como motor de diagramas." (registra `integraciones.diagramas=diagram-design`).
  3. "Hacé el organigrama del proyecto." Variantes: "Armá el roadmap por etapas con las puertas como hitos." · "Dibujá el flujo de excepciones del PID."
- **Respuestas del usuario:** la primera vez diagram-design pregunta si personalizar el estilo o usar el estilo por defecto: "Usá el estilo por defecto." pm-visuales ya le pide fuentes del sistema (sin Google Fonts, sin red); para las tipografías web: "Usá las tipografías web de diagram-design."
- **Entradas (qué aporta el usuario y cómo):** el motor y el tipo de diagrama, en el prompt; roles de `gestion/estado.json` → `roles` (organigrama); etapas y puertas del plan de proyecto y de `estado.json` → `puertas` (roadmap); tolerancias y roles de `estado.json` (flujo de excepciones), según la guía de pm-visuales §6; para redibujar la WBS, el Mermaid `gestion/02-planificacion/visuales/wbs.md`. Nada se adjunta.
- **Objetivo:** diagramas editoriales HTML/SVG (organigrama, mapa poder/interés tipo `quadrant`, flujo de excepciones tipo `swimlane`, roadmap por etapas tipo `timeline`) para la junta o el cliente.
- **Momento PRINCE2:** organigrama en SU; flujo de excepciones en IP (enfoque de control del PID); roadmap en SU/IP con las puertas como hitos y actualizado en cada SB. Decide quien aprueba la fuente (ejecutiva en las puertas).
- **Dueña y agente:** `pm-visuales`; desde `pm-inicio` o `pm-planificacion`.
- **Externa:** diagram-design 2.6 (`cathrynlavery/diagram-design`, MIT; verificada 2.6.133, commit `66fa2e7`). Como plugin: `claude plugin marketplace add cathrynlavery/diagram-design` y `claude plugin install diagram-design@diagram-design` (con `--scope project` queda para todo el equipo); como skill copiada: `npx skills add cathrynlavery/diagram-design -a claude-code -s diagram-design -y`. Se invoca como `diagram-design:diagram-design` (plugin) o `diagram-design`.
- **Respaldo:** Mermaid de `templates/diagramas-mermaid.md` (§1 organigrama, §6 roadmap, §7 flujo de excepciones).
- **Frase:** "Hacé el organigrama del proyecto" (sesión en vivo B2). EN: "Build a stage roadmap with the gates as milestones." (ejemplo de la propia skill).
- **Pasos:** los ejecuta el sistema; el usuario no los escribe. Respaldo Mermaid; si es un `flowchart` (organigrama, WBS, flujo de productos, flujo de excepciones), la vía de importación del motor; el mapa poder/interés (`quadrantChart`) y el roadmap (`timeline`) se dibujan desde la tabla intermedia porque el importador los rechaza (código 2). Luego, el chequeo sin red:
  ```bash
  python3 <diagram-design>/scripts/mermaid_extract.py 02-planificacion/visuales/wbs.md
  python3 <diagram-design>/scripts/self_check.py --offline 02-planificacion/visuales/<nombre>.html     # debe imprimir OK
  ```
  Salida real de `mermaid_extract.py` sobre la WBS del proyecto de prueba:
  ```text
  1 diagram(s): [0] flowchart (16n/15e)
  - budget: nodes OVER (max 9), edges OVER (max 12)
  - type candidates: architecture
  ```
- **Salidas (qué queda y dónde verificarlo):** `02-planificacion/visuales/organigrama.html` (o `roadmap.html`, `flujo-excepciones.html`) junto a su `.md`. En vivo: B1 (`--plugin-dir` con el clon) generó `organigrama.html` y `wbs.html`, con `self_check.py` → `OK …/organigrama.html` y `OK …/wbs.html`; B2 (plugin instalado) generó el organigrama con `OK organigrama.html` y nota en `diario.md`. Dónde verificarlo: abrí `gestion/02-planificacion/visuales/organigrama.html` en el navegador (los roles vacíos se ven `[por confirmar]`); el sistema informa el `OK …` de `self_check.py`; por contrato (guía de pm-visuales §1.3, paso 6) queda en `gestion/estado.json` → `artefactos` (`organigrama`, `roadmap` o `flujo-excepciones`) como `borrador`; la nota de la sesión, en `gestion/03-control/registros/diario.md`.
- **Controles:** INS-03 (no ve un plugin cargado solo con `--plugin-dir`: ahí emite AVISO y hay que ignorarlo); `self_check.py` = OK; regla de método: tres intereses en la junta y aseguramiento separado (la sesión B2 lo verificó y marcó `[por confirmar]` los roles vacíos).
- **Límites:** la primera vez pide elegir estilo; sin usuario (subagente o `claude -p`) usa el estilo por defecto y lo anota. Su tope sugerido es de 9 nodos: con la regla `faithful` se conservan todos (la WBS de 11 nodos de B1 se mantuvo completa). Por defecto cargaría tipografías de Google Fonts: pm-visuales pide fuentes del sistema y verifica con `--offline` (reverificado en vivo el 2026-10-27 con 2.6.133: organigrama sin red, `OK`). El roadmap y el flujo de excepciones con este motor **[sin verificar en vivo]**: solo se probaron organigrama y WBS. Un flujo de control de cambios distinto del de excepciones no figura como visual del catálogo; se dibujaría como `flowchart` **[sin verificar en vivo]**.

### 1.3 visual-explainer: one-pager del brief (o de los OKR)

- **Prompt del usuario:**
  1. En tu terminal (una sola vez): `claude plugin marketplace add nicobailon/visual-explainer` y `claude plugin install visual-explainer@visual-explainer-marketplace` (o la copia con `npx skills add …`, ver Externa).
  2. "Usá visual-explainer para los one-pagers." (registra `integraciones.diagramas=visual-explainer` o la lista `archify,visual-explainer`).
  3. "Con pm-visuales, hacé un one-pager visual del brief." Variante: "Hacé un one-pager de los OKR para la junta." (nombrar pm-visuales evita que otra skill de diseño del entorno tome el pedido; ver Límites).
- **Entradas (qué aporta el usuario y cómo):** el pedido y la audiencia, en el prompt; el brief ya registrado (`gestion/01-inicio/project-brief.md`, clave `project-brief`) o los OKR de `gestion/00-direccion/okr.csv` (caso 4). Nada se adjunta.
- **Objetivo:** una página HTML que explica el brief, un resumen de etapa o los OKR a la junta o al patrocinador.
- **Momento PRINCE2:** SU (one-pager del project brief antes de `autorizar-inicio`) o SB (resumen para la puerta de etapa). Decide la ejecutiva sobre la fuente; el one-pager es solo lectura.
- **Dueña y agente:** `pm-visuales`; desde `pm-inicio` (brief) o el orquestador.
- **Externa:** visual-explainer 0.12 (`nicobailon/visual-explainer`, MIT). Plugin: `claude plugin marketplace add nicobailon/visual-explainer` y `claude plugin install visual-explainer@visual-explainer-marketplace`; skill copiada: `npx skills add nicobailon/visual-explainer -a claude-code -s visual-explainer -y`. Node ≥ 18; `playwright-core` opcional.
- **Respaldo:** `templates/canvas-arranque.html`.
- **Frase:** "Hacé un one-pager visual del brief" (sesiones C2 y C3). EN: "Make a one-page visual summary of the project brief."
- **Pasos:** los ejecuta el sistema; el usuario no los escribe. pm-visuales escribe la fuente `<nombre>.src.html` (con `data-register` y `<link rel="stylesheet" href="kit.css" data-ve-kit>`) y la renderiza **sin `--open`**. Prueba real con un one-pager de los OKR del caso 4:
  ```bash
  cd gestion/02-planificacion/visuales
  node ../../../.claude/skills/visual-explainer/kit/render.mjs one-pager-okr.src.html
  ```
  ```text
  ✓ <repo>/gestion/02-planificacion/visuales/one-pager-okr.html  kit inlined
    Page: 0 figures · 40 prose words outside figures
  ```
- **Salidas (qué queda y dónde verificarlo):** `02-planificacion/visuales/one-pager-<fuente>.html` + `.src.html`; registro `estado.py artefacto one-pager-<fuente> … --estado borrador`. En vivo, C2 y C3 dejaron `one-pager-project-brief.src.html` y `.html` en esa carpeta y nada en `~/.agent/diagrams/` (la ruta por defecto del motor, que el contrato prohíbe). Dónde verificarlo: abrí `gestion/02-planificacion/visuales/one-pager-project-brief.html` (u `one-pager-okr.html`) en el navegador; lleva BORRADOR si la fuente no está aprobada; la clave `one-pager-<fuente>` figura en `gestion/estado.json` → `artefactos` como `borrador`; no debe haber nada nuevo en `~/.agent/diagrams/`.
- **Controles:** INS-03; el render debe imprimir `✓`; `kit/check.mjs` solo con `playwright-core` (C3 no pudo correrlo y lo dijo). Las sesiones detectaron y reportaron incoherencias de la fuente (versión del brief en `estado.json` distinta de la del archivo) sin corregirlas.
- **Límites:** en una corrida (C1) la petición la tomó otra skill del entorno (`artifact-design`) y el archivo quedó fuera del proyecto; si el entorno tiene skills de diseño propias, pedirlo nombrando pm-visuales o pasar por el orquestador. visual-explainer no hace árboles ni organigramas (guía §1.2).

### 1.4 Tablero de avance con vista por actor (interno)

- **Prompt del usuario:** "Mostrame un tablero con las acciones de cada persona, con corte al 18/12/2026." Para cada persona: "Pasame el enlace del tablero filtrado para Lucía Benítez."
- **Respuestas del usuario:** antes de compartirlo, el gestor lo confirma: "Revisado, se puede compartir." Si hay un objetivo en rojo sin issue ni excepción, el sistema no lo publica y lo dice: "Registrá primero el issue y después armamos el tablero." Para publicarlo en un canal, confirmar destino y contenido en la vista previa (caso 6).
- **Entradas (qué aporta el usuario y cómo):** la fecha de corte, en el prompt; los registros ya cargados por el sistema con `registro.py` (`gestion/03-control/registros/riesgos.csv`, `acciones.csv`, `issues.csv`); la serie EVM de `gestion/03-control/reportes/progreso.csv` (caso 2.1); `avance-bmad.csv` (caso 7) y, si hay tracker, la instantánea de `gestion/03-control/fuentes/` traída por el conector (caso 6). El usuario no adjunta archivos.
- **Objetivo:** HTML autocontenido con semáforo contra tolerancias, riesgos (mapa de calor P×I), acciones por actor y sección ágil; cada persona recibe su enlace filtrado `?actor=<Nombre>`.
- **Momento PRINCE2:** CS, en cada período de informe, junto al highlight. Lo confirma el gestor antes de compartirlo.
- **Dueña y agente:** `pm-visuales`, invocada por `pm-control` (paso 10 de su bucle).
- **Externa:** ninguna; puede tomar instantáneas de tracker de `03-control/fuentes/` (caso 6).
- **Frase:** "Mostrame un tablero con las acciones de cada persona" (frase #8 del conjunto de enrutamiento). EN: "Build this week's progress dashboard with a view per person."
- **Pasos:** los ejecuta el sistema; el usuario no los escribe. Se arma el bloque JSON `datos-tablero` con el script de la guía §3 (registros con `registro.py … --json`, `evm.py --json`, `avance-bmad.csv`) y se reemplaza en `templates/tablero-avance.html`. En la prueba: `riesgos` R-001 (16, alto) y R-002 (6, medio), acciones A-001 (vencida al corte) y A-002, issue I-001, objetivos tiempo y costo en `rojo` desde `evm.py --proyecto`.
  ```bash
  python3 $E/estado.py --proyecto gestion artefacto tablero-avance --ruta 03-control/reportes/2026-12-18-tablero-avance.html --estado borrador
  ```
- **Salidas (qué queda y dónde verificarlo):** `03-control/reportes/2026-12-18-tablero-avance.html` (35 KB, sin red). `paquete.py listar puerta autorizar-etapa` lo incluye como opcional. Dónde verificarlo: abrí `gestion/03-control/reportes/2026-12-18-tablero-avance.html` en el navegador y compará las acciones con `gestion/03-control/registros/acciones.csv` abierto en Excel; la vista filtrada se abre agregando `?actor=Lucía Benítez` a la dirección **[sin verificar en vivo]**; la clave `tablero-avance` figura en `gestion/estado.json` → `artefactos` como `borrador`. Prompt de verificación: "Mostrame el tablero de avance".
- **Controles:** rojo sin issue o excepción → no se publica (regla 2 de pm-visuales); acciones desde `acciones.csv`, nunca desde `issues.csv`; publicación solo vía pm-integraciones con confirmación.
- **Límites:** la inyección del JSON se verificó; la vista por actor en navegador **[sin verificar en vivo]** (no había navegador en el entorno). El valor de `?actor=` debe coincidir exactamente con el del registro.

### 1.5 drawio-mcp: diagramas editables

- **Prompt del usuario:**
  1. En tu terminal: conectar el servidor drawio-mcp oficial con `claude mcp add …` (los argumentos los da el propio servidor **[verificar]**).
  2. "Usá draw.io como motor de diagramas." (registra `integraciones.diagramas=drawio`).
  3. "Pasame el organigrama a draw.io para editarlo."
- **Entradas (qué aporta el usuario y cómo):** la conexión MCP, hecha por el usuario en su cliente (credenciales fuera del proyecto); los roles de `gestion/estado.json` → `roles` o la WBS de `gestion/02-planificacion/wbs.csv`; la tabla intermedia (nodo, padre, etiqueta) la arma el sistema.
- **Objetivo:** que el usuario pueda editar el organigrama o la WBS en draw.io.
- **Momento, dueña, agente:** igual que 1.1; capacidad `diagramas=drawio`, dueña `pm-visuales` (conexión vía `pm-integraciones`).
- **Externa:** drawio-mcp oficial, conectado con la gestión de conectores del cliente (`claude mcp add …`); herramientas con prefijo `mcp__drawio…` (guía §1.1). El paquete no trae `.mcp.json` ni credenciales.
- **Respaldo:** Mermaid.
- **Frase:** "Pasame el organigrama a draw.io para editarlo." EN: "Give me the org chart as an editable draw.io file."
- **Pasos:** tabla intermedia (nodo, padre, etiqueta) → herramienta del servidor → `.drawio` + PNG/SVG junto al `.md` (guía §1.4).
- **Salidas (qué queda y dónde verificarlo):** `02-planificacion/visuales/organigrama.drawio` y su imagen **[sin verificar en vivo]**. Es la salida esperada. Dónde verificarlo: abrí `gestion/02-planificacion/visuales/organigrama.drawio` en draw.io; si el servidor no estaba, queda `organigrama.md` (Mermaid) y la nota en `gestion/03-control/registros/diario.md`.
- **Controles:** INT-01 acepta `drawio` como valor conocido de `diagramas`; INS-03 **no** comprueba drawio (solo skills externas), así que si el servidor no está la sesión debe caer al Mermaid y anotarlo.
- **Límites:** documentado sin prueba en vivo; no se conocen ni se citan nombres de herramientas concretos del servidor.

### 1.6 Respaldo Mermaid (sin ninguna skill externa)

- **Prompt del usuario:** "Hacé el organigrama y la WBS solo con Mermaid, sin skills externas." Si había un motor declarado: "Volvé al respaldo Mermaid para los diagramas." (el sistema corre `estado.py integracion diagramas=mermaid`, la salida que sugiere INS-03).
- **Entradas (qué aporta el usuario y cómo):** las mismas que 1.1 (roles en `gestion/estado.json`, WBS en `gestion/02-planificacion/wbs.csv`, actividades en `gestion/02-planificacion/actividades.csv` para el Gantt); nada que instalar ni adjuntar (`mmdc` es opcional).
- **Objetivo:** que el flujo funcione igual sin nada instalado.
- **Pasos:** los ejecuta el sistema; el usuario no los escribe. `wbs.py --mermaid` (WBS), `cpm.py --mermaid` (Gantt), plantillas Mermaid para organigrama, roadmap y flujos; `templates/canvas-arranque.html` para el one-pager.
- **Salidas (qué queda y dónde verificarlo):** `02-planificacion/visuales/wbs.md`, `organigrama.md`, `02-planificacion/gantt.md` (ejemplo real en `docs/ejemplos/integraciones/gantt-cpm.md`). Dónde verificarlo: abrí `gestion/02-planificacion/visuales/wbs.md`, `organigrama.md` y `gestion/02-planificacion/gantt.md` en un editor con vista previa de Mermaid; si un motor declarado no estaba, la nota está en `gestion/03-control/registros/diario.md`.
- **Evidencia en vivo:** con `HOME` aislado y `diagramas=archify` declarado pero no instalado (E1), pm-visuales entregó `organigrama.md` y `wbs.md` y anotó en `diario.md` que archify no estaba; con `visual-explainer` no instalado (G1), usó la plantilla interna y lo anotó.
- **Límites:** con `mmdc` instalado, `exportar.py docx` inserta el Mermaid como imagen; sin él queda como código con aviso.

---

## Caso 2 · Reportes: checkpoint, highlight, excepción, fin de etapa y exportación

El contenido de los informes es de `pm-progreso-reportes` (checkpoint, highlight), `pm-issues-cambios` (informe de
excepción) y `pm-plan-etapa-y-limites` (informe de fin de etapa); los formatos Office son de `pm-exportar`. Ningún
script redacta el informe: los scripts dan las cifras y la skill completa la plantilla.

### 2.1 Checkpoint y highlight con EVM

- **Prompt del usuario:**
  1. "Armá el highlight de la quincena con el EVM, corte 18/12/2026: valor ganado acumulado 39.000 y costo real 43.500." Atajo: `/pm-method:pm-reporte highlight`.
  2. "Compará también el costo contra la tolerancia del proyecto (±10 %)."
  3. Para el informe del equipo al gestor: `/pm-method:pm-reporte checkpoint`.
- **Respuestas del usuario:** si el sistema avisa que la tolerancia de plazo del proyecto ("±2 semanas") no se puede leer como porcentaje, contestá con el porcentaje que decida el gestor (p. ej. "Tomá ±10 % de plazo para el proyecto"). Con `excepcion_prevista True` propone el informe de excepción: "Sí, preparalo" (caso 2.2). Para cerrar: "Revisé el highlight, lo confirmo para la junta" (pm-director registra la aprobación).
- **Entradas (qué aporta el usuario y cómo):** EV y AC acumulados, escritos en el prompt (el sistema los pasa a `gestion/03-control/reportes/progreso.csv`, columnas `periodo,pv,ev,ac,notas`; el PV sale de `gestion/02-planificacion/linea-base-costo.csv`); los checkpoints del período; los registros de `gestion/03-control/registros/`; el avance de BMAD, leído en solo lectura por `bmad.py avance` (caso 7).
- **Objetivo:** informe quincenal a la junta con semáforo contra tolerancias de etapa y proyecto.
- **Momento PRINCE2:** CS (checkpoint del equipo al gestor en MP; highlight del gestor a la junta). Aseguramiento revisa; la aprobación del highlight la registra `pm-director` con la confirmación del gestor.
- **Dueña y agente:** `pm-progreso-reportes`, desde `pm-control`; comando `/pm-method:pm-reporte highlight|checkpoint|excepcion`.
- **Frase:** "Armá el highlight de la quincena con el EVM." EN: "Write this fortnight's highlight report with earned value."
- **Pasos reales** (corte 2026-12-18, BAC de la etapa 68.000 = Σ PV de `linea-base-costo.csv`): los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion resumen --corte 2026-12-18
  python3 $E/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 68000 --proyecto gestion
  python3 $B --proyecto gestion avance --corte 2026-12-10
  ```
  ```text
  "top": ["R-001 (16, alto) Integración de saldos se demora", "R-002 (6, medio) Notificaciones SMS no disponibles"]
  "vencidas": ["A-001 Lucía Benítez 2026-12-11"]
  == 2026-11-20 ==   SPI 0.929 · CPI 0.963 · semaforo_cronograma ambar · semaforo_costo ambar · excepcion_prevista False
  == 2026-12-18 ==
  SPI                    0.867
  CPI                    0.897
  EAC_tendencia          75,846.154
  VAC                    -7,846.154
  VAC_pct                -11.538
  sobrecosto_pct         11.538
  semaforo_cronograma    rojo
  semaforo_costo         rojo
  base_semaforo          costo:tolerancia;cronograma:tolerancia
  excepcion_prevista     True
  → Pronóstico fuera de tolerancia: preparar informe de excepción (pm-progreso-reportes) y escalar a pm-director.
  ```
  `--proyecto` toma las tolerancias **de etapa** en % de `estado.json` (±10 % tiempo, ±5 % costo). Contra el proyecto
  (BAC 132.400, ver 3.3) se pasa la tolerancia explícita: `evm.py --pv 45000 --ev 39000 --ac 43500 --bac 132400 --tol-costo 10`
  → EAC 147.677, `semaforo_costo rojo`, `semaforo_cronograma ambar`.
- **Salidas (qué queda y dónde verificarlo):** `03-control/reportes/2026-12-18-highlight-report.md` desde `templates/highlight-report.md`, registrado con `estado.py artefacto highlight-2026-12-18 --estado borrador`; checkpoint en `templates/checkpoint-report.md`. Dónde verificarlo: abrí `gestion/03-control/reportes/2026-12-18-highlight-report.md`; la clave `highlight-2026-12-18` figura en `gestion/estado.json` → `artefactos` (`borrador` hasta la confirmación; al aprobarse, una fila `aprobado highlight-2026-12-18 …` en `gestion/03-control/registros/decisiones.csv`); los conteos deben coincidir con `/pm-method:pm-estado` y la serie con `progreso.csv` abierto en Excel.
- **Controles:** conteos idénticos a `registro.py resumen`; ningún verde con un pronóstico en rojo; sanidad EST-06/07 exige tolerancias de tiempo y costo.
- **Límites:** `VAC_pct` tiene el signo de VAC y el desvío previsto contra BAC va en `sobrecosto_pct`; `base_semaforo` declara la base de cada semáforo (`costo:tolerancia;cronograma:indice-0.95-0.85` si solo se pasa `--tol-costo`). Una tolerancia en semanas ("±2 semanas") no la lee `--proyecto`: el script avisa y hay que convertirla y pasarla con `--tol-plazo`. (Salida del bloque re-ejecutada con la versión 2.1.0.)

### 2.2 Informe de excepción

- **Prompt del usuario:**
  1. "Con estos números nos vamos de la tolerancia de costo: prepará el informe de excepción." Atajo: `/pm-method:pm-reporte excepcion`.
  2. Después de la reunión de junta: "La junta decidió pedir un plan de excepción; lo decidió Laura Méndez, ejecutiva. Registralo."
  3. Con el plan de excepción listo: `/pm-method:pm-puerta autorizar-plan-excepcion`.
- **Respuestas del usuario:** el sistema pregunta qué decidió la junta y quién: una de las opciones del informe (pedir plan de excepción, aceptar el desvío o cerrar), con nombre y rol ("Ejecutivo: Laura Méndez").
- **Entradas (qué aporta el usuario y cómo):** las cifras del caso 2.1 (ya en `gestion/03-control/reportes/progreso.csv`); el issue I-001 de `gestion/03-control/registros/issues.csv`; la decisión de la junta, escrita en el prompt 2. Nada se adjunta.
- **Objetivo:** escalar a la junta un pronóstico fuera de tolerancia de etapa, con opciones.
- **Momento PRINCE2:** CS → DP. El gestor lo emite; la junta decide (pedir plan de excepción, aceptar, cerrar). `estado.py limite-etapa --excepcion` y la puerta `autorizar-plan-excepcion` son exclusivos de `pm-director`.
- **Dueña y agente:** `pm-issues-cambios` (plantilla única `templates/informe-excepcion.md`, también la usa pm-progreso-reportes cuando `evm.py` marca `excepcion_prevista`); `pm-control` la prepara y `pm-director` registra.
- **Frase:** "Con estos números nos vamos de la tolerancia de costo: prepará el informe de excepción." EN: "Prepare the exception report for the cost overrun."
- **Pasos reales** (en una copia del proyecto, como lo haría pm-director tras la decisión de la junta): los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion limite-etapa --excepcion I-001
  python3 $E/sanidad.py --proyecto gestion --rapido
  ```
  ```text
  Fase: entrega · Proceso: SB · Etapa 2: Release 1 · Enfoque: hibrido
  Límite de etapa por excepción I-001: plan de excepción (reemplaza el plan vigente), actualizar plan de proyecto, business case y riesgos. Puerta: autorizar-plan-excepcion (pm-director).
  AVISO EST-14 Excepción abierta I-001 esperando plan de excepción.
  ```
- **Salidas (qué queda y dónde verificarlo):** informe con clave `informe-excepcion-X-###` en `estado.json`, referenciado desde `issues.csv.notas` y `decisiones.csv`. Dónde verificarlo: el informe está en `gestion/03-control/reportes/<fecha>-informe-excepcion-X-###.md` (tabla de pm-issues-cambios) con estado `en-revision`; en `gestion/estado.json`, `excepcion_abierta` = `I-001` y `proceso_actual` = `SB`; la decisión de la junta es una fila en `gestion/03-control/registros/decisiones.csv`; `/pm-method:pm-estado` muestra la excepción abierta.
- **Controles:** hook: un subagente pm-* que intente `estado.py puerta …` recibe "ese comando de estado.py está reservado a pm-director"; sanidad EST-14 hasta que se apruebe el plan de excepción.
- **Límites:** el informe lo redacta la skill sobre la plantilla; el script no lo genera.

### 2.3 Informe de fin de etapa

- **Prompt del usuario:**
  1. "Cerremos la etapa 2: informe de fin de etapa y plan de la 3."
  2. "Prepará la puerta de la etapa 3 para la junta." Atajo: `/pm-method:pm-puerta autorizar-etapa`.
  3. Después de la junta: "La junta aprobó la etapa 3; decidió Laura Méndez, ejecutiva. Registralo."
- **Respuestas del usuario:** las lecciones de la etapa, si el sistema las pide; la confirmación de la lista de control de la junta; la decisión (aprobado, condicionado con sus condiciones, o rechazado) con nombre y rol de quien decidió.
- **Entradas (qué aporta el usuario y cómo):** lecciones y productos entregados, escritos en el prompt o ya en `gestion/03-control/registros/lecciones.csv`; cifras de `gestion/03-control/reportes/progreso.csv` y `gestion/02-planificacion/presupuesto.md` (casos 2.1 y 3.3); el avance de BMAD, por la fachada (caso 7); la decisión de la junta, en el prompt 3.
- **Objetivo:** cierre de la etapa con EVM, productos, lecciones y pronóstico, para la puerta `autorizar-etapa` siguiente.
- **Momento PRINCE2:** SB; decide la junta. Dueña `pm-plan-etapa-y-limites` (plantilla `informe-fin-etapa.md`, que pide costo desde `presupuesto.md · evm.py`), desde `pm-planificacion` + `pm-control`.
- **Frase:** "Cerremos la etapa 2: informe de fin de etapa y plan de la 3." EN: "Prepare the end stage report and the next stage plan."
- **Pasos reales:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion limite-etapa
  python3 $X --proyecto gestion listar puerta autorizar-etapa
  ```
  ```text
  Límite de etapa (SB): informe de fin de etapa, plan de la siguiente etapa, actualizar plan de proyecto, business case, riesgos y lecciones. …
  **ESTADO DEL PAQUETE / PACKAGE STATUS:** BORRADOR / DRAFT — faltan: informe-fin-etapa-2, plan-etapa-3, business-case, plan-proyecto
  ```
- **Salidas (qué queda y dónde verificarlo):** `informe-fin-etapa-2` y `plan-etapa-3` registrados en `estado.json`; con ellos, el paquete deja de salir BORRADOR. Dónde verificarlo: abrí `gestion/03-control/reportes/<fecha>-informe-fin-etapa-2.md` y `gestion/02-planificacion/plan-etapa-3.md` (rutas de pm-plan-etapa-y-limites); las claves figuran en `gestion/estado.json` → `artefactos`; al registrarse la puerta, `gestion/estado.json` → `puertas` y una fila `autorizar-etapa: aprobado` en `gestion/03-control/registros/decisiones.csv`; repetir `/pm-method:pm-puerta autorizar-etapa` muestra qué falta todavía.
- **Controles:** faltante o borrador obligatorio → ZIP `-BORRADOR`; `pm-director` corre `bmad.py verificar` antes de la puerta (caso 7).

### 2.4 Exportación con las skills oficiales de Office (y respaldo `exportar.py`)

- **Prompt del usuario:**
  1. En tu terminal (una sola vez): `claude plugin marketplace add anthropics/skills` y `claude plugin install document-skills@anthropic-agent-skills` (o la copia con `npx skills add …`, ver Externa).
  2. "Usá las skills de Office para exportar." (registra `integraciones.export=skills-office`).
  3. "Exportá el presupuesto a Excel y el highlight a Word." · "Exportá el highlight a PowerPoint." · Sin las skills: "Exportá los registros a Excel."
- **Respuestas del usuario:** antes de enviar, confirmar destinatarios y versión ("Sí, mandáselo a la junta"; el envío lo hace pm-comunicacion-stakeholders, con un conector o por la capa de canales del caso 8). Si el libro de registros va a una audiencia externa, pedí que se quite la hoja `stakeholders` (ver Límites; cómo la quita el sistema **[verificar]**).
- **Entradas (qué aporta el usuario y cómo):** formato y audiencia, en el prompt; los archivos fuente ya están en `gestion/` (`03-control/reportes/2026-12-18-highlight-report.md`, `02-planificacion/linea-base-costo.csv`, los CSV de `03-control/registros/`). Nada se adjunta.
- **Objetivo:** entregar a la junta Word, Excel o PowerPoint con marca BORRADOR cuando la fuente no está aprobada.
- **Momento PRINCE2:** DP/SB (paquete de puerta) o CS (highlight). El usuario confirma antes de enviar; el envío es de `pm-comunicacion-stakeholders`.
- **Dueña y agente:** `pm-exportar`, desde el orquestador o `pm-director` (preparación de puerta).
- **Externa:** `anthropics/skills` (`docx`, `xlsx`, `pptx`; licencia propietaria). Plugin: `claude plugin marketplace add anthropics/skills` y `claude plugin install document-skills@anthropic-agent-skills`; copia: `npx skills add anthropics/skills -a claude-code -s docx xlsx pptx -y`. Se aceptan los nombres `docx`, `document-skills:docx` y `anthropic-skills:docx` (igual para xlsx y pptx). Se activa con `integracion export=skills-office`.
- **Respaldo:** `export=scripts`: `exportar.py` (docx desde Markdown; xlsx solo desde CSV), `paquete.py` (ZIP); sin `pptx`, guion `exportados/<nombre>-deck.md`.
- **Frases:** "Exportá el presupuesto a Excel y el highlight a Word"; "Exportá el highlight a PowerPoint" (sesiones D1, D2). EN: "Export the highlight report to Word and the budget to Excel."
- **Evidencia en vivo:** D1 invocó `xlsx` y `docx`: Excel con hojas Resumen, Por etapa, Línea base PV y Notas, fórmulas recalculadas sin errores; Word con encabezado BORRADOR. D2 siguió la skill `pptx` leyendo su `SKILL.md` (pptxgenjs, 5 diapositivas con BORRADOR). Todo en `exportados/`.
- **Pasos reales del respaldo:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  cd gestion
  python3 $E/exportar.py docx --entrada 03-control/reportes/2026-12-18-highlight-report.md \
      --salida exportados/2026-12-18-highlight-report-v0.1-BORRADOR.docx
  python3 $E/exportar.py xlsx --entrada 02-planificacion/linea-base-costo.csv \
      --salida exportados/2026-12-18-linea-base-costo-v0.1-BORRADOR.xlsx
  python3 $E/exportar.py xlsx --proyecto . --salida exportados/2026-12-18-registros-v1.xlsx
  ```
  Revisado con `python-docx` y `openpyxl`: el `.docx` abre con el párrafo "BORRADOR / DRAFT — estado: borrador · generado
  con asistencia de IA, requiere revisión humana" y conserva la tabla; el `.xlsx` de línea base tiene una hoja
  (`linea-base-costo`, 5 filas × 7 columnas); el de registros, nueve hojas (acciones, calidad, cambios, decisiones,
  issues, lecciones, riesgos, stakeholders, supuestos).
- **Salidas (qué queda y dónde verificarlo):** `exportados/AAAA-MM-DD-<tipo>-v<n>[-BORRADOR].<ext>`; nunca fuente de verdad. Dónde verificarlo: abrí los archivos de `gestion/exportados/` en Word, Excel o PowerPoint (el encabezado "BORRADOR / DRAFT" aparece si la fuente no está aprobada); el exportado queda anotado en `gestion/03-control/registros/diario.md` y, si se registra, como `exportado-<tipo>` en `gestion/estado.json` (tabla de pm-exportar).
- **Controles:** INS-03 informa con qué nombre invocar cada skill (en este entorno: `anthropic-skills:docx`, `:xlsx`, `:pptx`, sincronizadas de claude.ai); INS-01 si faltan `python-docx` u `openpyxl`; nota en `diario.md` cuando se usa el respaldo (F2 la dejó; F1 no, y lo ofreció como pendiente).
- **Límites:** `exportar.py xlsx` solo convierte CSV; el presupuesto en Markdown se exporta desde `linea-base-costo.csv`, sin las tablas de `presupuesto.md` (lo informaron F1 y F2). Si se le pasa un `.md`, el script lo rechaza con un mensaje. La hoja `stakeholders` va siempre en el libro de registros: quitarla si la audiencia es externa.

---

## Caso 3 · Planificación: WBS, camino crítico, MS Project, presupuesto y release plan

Todo en IP (plan de proyecto y plan de la primera etapa de entrega) y en cada SB; se aprueba con el plan en
`autorizar-proyecto` y `autorizar-etapa` (decide la junta; registra pm-director). Agente: `pm-planificacion`.

### 3.1 WBS con `wbs.py`

- **Prompt del usuario:** "Armá la WBS con responsables y citá los FR del PRD." Con datos: "La 2.1 Alta y acceso con segundo factor la lleva Lucía Benítez, 400 horas; la puesta en producción es un hito de Martín Suárez."
- **Respuestas del usuario:** si falta un responsable, un esfuerzo o un costo, el sistema lo deja `[por confirmar]` y lo pide; contestá con el dato o con "dejalo por confirmar".
- **Entradas (qué aporta el usuario y cómo):** productos, paquetes, responsables, horas y costos, escritos en el prompt o en un CSV que dejás en `gestion/02-planificacion/wbs.csv` con las columnas de la plantilla (`codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref`); los ids FR del PRD, leídos de BMAD por la fachada `especificacion.py` en solo lectura.
- **Dueña:** `pm-planificacion-por-productos` (contenido); `pm-visuales` solo dibuja (caso 1.1).
- **Frase:** "Armá la WBS con responsables y citá los FR del PRD." EN: "Build the WBS with owners and cite the PRD requirement ids."
- **Pasos reales** (`wbs.csv` con 6 productos, 8 paquetes y 1 hito; `ref` con FR del PRD real): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $E/wbs.py 02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid 02-planificacion/visuales/wbs.md --diccionario 02-planificacion/diccionario-wbs-esqueleto.md
  Portal de autoservicio para socios: 15 elementos, 9 hojas · esfuerzo 2480 h · costo 124,000
  1 Gestión del proyecto [producto] 320 h · 16,000
  2 Acceso del socio [producto] 560 h · 28,000
    2.1 Alta y acceso con segundo factor [paquete] 400 h · 20,000 · Lucía Benítez
  …
  6 Transición [producto] 0 h · 0
    6.1 Puesta en producción [hito] 0 h · 0 · Martín Suárez
  ```
- **Salidas (qué queda y dónde verificarlo):** `gestion/02-planificacion/wbs.csv`, `gestion/02-planificacion/visuales/wbs.md` (Mermaid) y `gestion/02-planificacion/diccionario-wbs-esqueleto.md`; la WBS se registra dentro de la clave `pbs-wbs` de `gestion/estado.json` (tabla de pm-planificacion-por-productos). Dónde verificarlo: abrí `wbs.csv` en Excel (15 elementos, 2480 h, 124.000) y `wbs.md` con vista previa de Mermaid; `/pm-method:pm-sanidad` no debe mostrar ESP-04.
- **Controles:** sanidad ESP-04 si un `ref` de la WBS no existe en la especificación; `bmad.py trazabilidad --wbs` informó "Referencias de la WBS a ids inexistentes: ninguna".

### 3.2 Camino crítico y exportación a MS Project (MSPDI)

- **Prompt del usuario:** "Calculá el camino crítico desde el 9/11/2026 y exportalo para abrirlo en MS Project." Para dejarlo como formato del proyecto: "Registrá MSPDI como formato de cronograma." (registra `integraciones.cronograma=mspdi`).
- **Entradas (qué aporta el usuario y cómo):** la fecha de inicio, en el prompt; las actividades con duración, predecesoras, recurso y código WBS, dictadas en el prompt o en un CSV que dejás en `gestion/02-planificacion/actividades.csv` (columnas `id,nombre,duracion,predecesoras,recurso,wbs`); la WBS de `gestion/02-planificacion/wbs.csv` (caso 3.1).
- **Dueña:** `pm-cronograma-estimacion`; capacidad `cronograma=cpm|mspdi`.
- **Externa:** ninguna obligatoria. MSPDI es XML abierto generado por `cpm.py`; MPXJ (PyPI `mpxj`, LGPL, Java) es opcional para validar o convertir a `.mpp`. utf8proj fue **descartado** (INTEGRACIONES §2).
- **Frase:** "Calculá el camino crítico y exportalo para abrirlo en MS Project." EN: "Compute the critical path and export it for MS Project."
- **Pasos reales:** los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $E/cpm.py 02-planificacion/actividades.csv --inicio 2026-11-09 --mermaid 02-planificacion/gantt.md \
        --mspdi 02-planificacion/cronograma.xml --titulo "Portal de autoservicio para socios" --wbs 02-planificacion/wbs.csv
  Duración total (días laborables): 44  · Fin previsto: 2027-01-08
  Camino crítico: A01 -> A03 -> A07 -> A08
  A05       5    0    5   10   15   10    0  Roles y permisos
  A08       0   44   44   44   44    0    0  Puesta en producción [hito]  *
  Carga por recurso (días): {'Equipo proveedor': 71}
  MSPDI escrito en 02-planificacion/cronograma.xml
  ```
  Validación leyendo el XML con MPXJ 16.10 (`UniversalProjectReader`): `tareas: 13 formato: MSPDI`, tareas resumen por
  código WBS (2, 3, 4, 5, 6), críticas marcadas, vínculo A07→A08 con `LinkLag` 9600 (lag `+2` días).
- **Salidas (qué queda y dónde verificarlo):** `02-planificacion/cronograma.xml` (copia en `exportados/` cuando se entrega), `gantt.md`; ejemplos reales en `docs/ejemplos/integraciones/`. Dónde verificarlo: abrí `gestion/02-planificacion/cronograma.xml` en MS Project o ProjectLibre (13 tareas, críticas marcadas; en la prueba se leyó con MPXJ, la apertura en MS Project **[verificar]**) y `gestion/02-planificacion/gantt.md` con vista previa de Mermaid; la ruta queda en la clave `cronograma` de `gestion/estado.json`.
- **Límites:** solo fin-a-comienzo, calendario L–V 8 h sin feriados (el 25/12 y el 1/1 cuentan como laborables) y sin nivelación. El paquete 1.1 de la WBS no tiene actividad, así que no aparece en el MSPDI. Una tarea resumen que solo contiene un hito sale con `Finish` = `Start` (prueba de regresión en `probar_paquete.py`, caso F). El título del Gantt Mermaid toma `--titulo`.

### 3.3 Presupuesto y costeo

- **Prompt del usuario:** "Costeá los paquetes y calculá la contingencia desde los riesgos, sin duplicarla." Con datos: "La etapa 2 tiene un PV de 68.000."
- **Respuestas del usuario:** la reserva de gestión va fuera del BAC y la aprueba la junta; si el sistema pregunta su monto, contestá con la cifra o "dejala por confirmar hasta la junta".
- **Entradas (qué aporta el usuario y cómo):** costos de cada paquete en la columna `costo` de `gestion/02-planificacion/wbs.csv` (caso 3.1); riesgos con impacto económico ya cargados por el sistema en `gestion/03-control/registros/riesgos.csv` (R-001, impacto 12.000); la distribución del PV por período, escrita en el prompt.
- **Dueña:** `pm-costos-presupuesto` (plantillas `presupuesto.md`, `hoja-costeo.md`, `linea-base-costo.csv`).
- **Frase:** "Costeá los paquetes y calculá la contingencia desde los riesgos, sin duplicarla." EN: "Cost the work packages and derive contingency from the risk register."
- **Pasos reales:** los ejecuta el sistema; el usuario no los escribe. `wbs.py … --json` → `total_costo: 124000.0`; `registro.py listar riesgos --abiertos --json` → R-001 `valor_esperado` 8400 (impacto 12.000), R-002 sin monto. Base 124.000 + contingencia 8.400 = BAC 132.400 (cálculo de la skill, no de un script); la reserva de gestión va fuera del BAC y la aprueba la junta. PV por período en `linea-base-costo.csv` (etapa 2: 68.000).
- **Salidas (qué queda y dónde verificarlo):** `gestion/02-planificacion/presupuesto.md`, `gestion/02-planificacion/hoja-costeo.md` y `gestion/02-planificacion/linea-base-costo.csv`, con claves `presupuesto`, `hoja-costeo` y `linea-base-costo` en `gestion/estado.json` (tabla de pm-costos-presupuesto). Dónde verificarlo: abrí `linea-base-costo.csv` en Excel y comprobá Σ PV = BAC 132.400; en `presupuesto.md`, la contingencia de 8.400 aparece una sola vez.
- **Controles:** total de `wbs.py` = hoja de costeo; Σ PV = BAC; contingencia una sola vez.
- **Límites:** no hay script de presupuesto: la consolidación es de `wbs.py` y el EMV de `registro.py`. Excel con fórmulas solo con la skill `xlsx` (caso 2.4).

### 3.4 Release plan ágil dentro de la etapa

- **Prompt del usuario:**
  1. "Armá el release plan del R1 con MoSCoW y DoD."
  2. Con las prioridades de la PO (ejemplo ilustrativo; la prueba sumó Must 19 y Should 5 puntos): "Sofía Ramírez, como PO, prioriza el R1: Must 1.1 alta y acceso con segundo factor, 1.3 consulta de saldos y 1.4 constancias en PDF; Should 1.2 recuperación de acceso. Cargalo en el backlog."
  3. "Avisale al equipo BMAD las prioridades nuevas." Atajo para revisar traspasos pendientes: `/pm-method:pm-sync bmad`.
- **Respuestas del usuario:** la PO confirma estimaciones e iteraciones si el sistema las pide; el sistema propone el traspaso a BMAD y se confirma: "Sí, emití el traspaso."
- **Entradas (qué aporta el usuario y cómo):** MoSCoW, estimación, iteración y release, dictados en el prompt (el sistema completa esas columnas de gobierno en `gestion/02-planificacion/backlog.csv`) o cargados por la PO en ese CSV; las historias, leídas de BMAD en solo lectura por `bmad.py backlog`; cadencia (14 días) y velocidad (30) de `gestion/estado.json` → `agil`.
- **Dueña:** `pm-agil-hibrido` (plantilla `release-plan.md`); con BMAD, el backlog lo sincroniza `pm-bmad-puente` (caso 7).
- **Frase:** "Armá el release plan del R1 con MoSCoW y DoD." EN: "Draft the release 1 plan with MoSCoW and definition of done."
- **Pasos reales:** los ejecuta el sistema; el usuario no los escribe. `bmad.py backlog` (10 historias) → la PO completa las columnas de gobierno (Must 8 + 3 + 8 = 19 puntos, Should 5) → `bmad.py backlog` las conserva → `bmad.py handoff` (4 prioridades para el equipo BMAD). Capacidad: Must + Should = 24 ≤ velocidad 30 × 2 iteraciones. EVM en modo ágil:
  ```text
  $ python3 $E/evm.py --pv 45000 --ev 39000 --ac 43500 --bac 68000 --modo agil --pct-no-must 30 --proyecto gestion
  semaforo_cronograma    n/a-agil
  semaforo_costo         n/a-agil
  alcance_no_entregable_pct 10.345
  semaforo_alcance       verde
  excepcion_prevista     False
  ```
- **Salidas (qué queda y dónde verificarlo):** `gestion/02-planificacion/release-plan.md` (clave `release-plan`), las columnas de gobierno de `gestion/02-planificacion/backlog.csv` y el traspaso `gestion/02-planificacion/especificacion/handoff-bmad-<fecha>-prioridades.md`, anotado en `gestion/estado.json` → `integraciones.bmad.handoffs`. Dónde verificarlo: abrí `backlog.csv` en Excel (columnas `moscow`, `release`, `iteracion`, `estimacion`); `/pm-method:pm-sync bmad` lista los traspasos pendientes; los intercambios de la PO quedan como filas `nivel=product-owner` en `gestion/03-control/registros/decisiones.csv` (SPEC §1.10, regla 12).
- **Límites:** en modo ágil, EAC > BAC se lee como alcance que no entra; hay excepción solo si peligran los Must.

---

## Caso 4 · OKR ligados a beneficios, con Tability opcional

- **Prompt del usuario:**
  1. "Definamos los OKR del proyecto para el próximo semestre: que los socios resuelvan sus gestiones sin ir a la sucursal, medido con las métricas SM-1, SM-2 y SM-5 del PRD."
  2. "Al 18/12 tenemos 12 % de socios activos registrados y 9.200 consultas por canales tradicionales; la satisfacción todavía no se midió. Puntuá los OKR."
  3. Con Tability (opcional): en tu terminal, conectar el servidor MCP oficial con `claude mcp add --transport http tability https://mcp.tability.app/mcp` y autenticar con `/mcp` en una sesión (detalle en el caso 9.1); luego "Usá Tability para los OKR." (registra `integraciones.okr=tability`) y "Traé el avance de Tability y actualizá la tabla de OKR para la junta." Atajo: `/pm-method:pm-sync okr`.
- **Respuestas del usuario:** la aceptación: "Laura Méndez, ejecutiva, aprueba los OKR." (pm-director corre `estado.py aprobar okr --por "Ejecutivo: Laura Méndez"`). Si el sistema propone escribir en Tability, revisar la vista previa y contestar "Confirmo" o "No escribas en Tability".
- **Entradas (qué aporta el usuario y cómo):** objetivos, KR, metas y responsables, escritos en el prompt; las métricas SM-n, leídas del PRD de BMAD por la fachada (`especificacion.py consultar`, solo lectura) y los beneficios B-nn del business case; los valores `actual`, dictados en el prompt 2 o traídos por el conector MCP como instantánea `gestion/03-control/fuentes/tability-AAAA-MM-DD.csv`.
- **Objetivo:** OKR de la capa de negocio vinculados a objetivos (OBJ-n), beneficios del business case (B-nn) o métricas de éxito del PRD (SM-n), sin duplicar sus datos.
- **Momento PRINCE2:** SU/IP (redacción), SB (revisión en cada límite de etapa), CP y revisiones de beneficios posteriores. Acepta la ejecutiva (o el usuario sénior dueño del beneficio); `pm-director` ejecuta `estado.py aprobar okr --por "<rol: nombre>"`.
- **Dueña y agente:** `pm-okr` (metadato `agente: pm-director`); la usan `pm-inicio` (redacción), `pm-director` y `pm-cierre` (puntuación), `pm-planificacion` (solo lectura en SB).
- **Externa:** Tability MCP, opcional (`integracion okr=tability`): servidor oficial `https://mcp.tability.app/mcp` (verificado el 2026-10-17; detalle y Perdoo en el caso 9); lectura a instantánea; escritura solo con vista previa y confirmación. Operately y okr-writer no se incorporaron.
- **Respaldo:** `okr=archivo`: `00-direccion/okr.csv` mantenido con `okr.py`.
- **Frases:** "Definamos los OKR del proyecto para el próximo semestre" (#12) y "Score our key results for Q4" (#46). Tability: "Pull progress from Tability and update the OKR table for the board."
- **Pasos reales:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion consultar SM-1     # Adopción: 30 % de socios activos registrados a los 6 meses …
  python3 $O gestion/00-direccion/okr.csv --plantilla
  # O-1 → OBJ-1; KR-1.1 → SM-1; KR-1.2 → SM-2; KR-1.3 → SM-5 (sin medición todavía: 'actual' vacío)
  python3 $O gestion/00-direccion/okr.csv --corte 2026-12-18 --markdown gestion/03-control/reportes/2026-12-18-okr.md
  ```
  ```text
  O-1 Los socios resuelven sus gestiones habituales sin ir a la sucursal → 0.33 (rojo)
     KR-1.1 Socios activos registrados en el portal [12/30 %] → 0.40 (ambar) · SM-1 · Sofía Ramírez
     KR-1.2 Consultas de saldo y constancias por canales tradicionales [9200/7000 consultas] → 0.27 (rojo) · SM-2 · Sofía Ramírez
     KR-1.3 Satisfacción posterior a la gestión [-/4 puntos] → - (sin-dato) · SM-5 · Sofía Ramírez
  ```
  Con Tability conectado, pm-integraciones guarda `03-control/fuentes/tability-AAAA-MM-DD.csv` con columnas
  `clave,tipo,titulo,actual,meta,actualizado,url`; cada valor leído se registra como check-in
  (`okr.py … --checkin KR-… --valor … --fuente tability`) en lugar de sobrescribir `actual`, y el KR se vincula con su
  par por la columna `ref_externa` (`tability:<id>`). Publicar en Tability (escritura) va por `--propuesta-sync` y
  `--marcar-publicado` (caso 9.1). `/pm-method:pm-sync okr` repite la lectura. **[sin verificar en vivo]**: no hubo
  servidor Tability conectado; en la prueba solo se creó la instantánea a mano para verificar su nombre.
- **Salidas (qué queda y dónde verificarlo):** `00-direccion/okr.csv`, `00-direccion/okr.md` (narrativa), `03-control/reportes/<fecha>-okr.md` (ejemplo en `docs/ejemplos/integraciones/okr-puntuado.md`); visual opcional con visual-explainer (caso 1.3). Dónde verificarlo: abrí `gestion/00-direccion/okr.csv` en Excel (columna `vinculo` con OBJ-1, SM-1, SM-2, SM-5) y `gestion/03-control/reportes/2026-12-18-okr.md`; tras la aceptación, `okr` figura `aprobado` en `gestion/estado.json` → `artefactos` y hay una fila `aprobado okr …` en `gestion/03-control/registros/decisiones.csv`; `/pm-method:pm-sanidad` no debe mostrar ESP-04 ni ESP-05.
- **Controles:** la sanidad valida la existencia del vínculo: con un KR que cita `SM-99` salió `ERROR ESP-04 okr KR-1.4 cita SM-99, que no existe en la especificación vigente (bmad)`; un `B-n` ausente del business case da `AVISO ESP-05`. Un KR rojo que amenaza un beneficio pasa a riesgo o issue y, fuera de la tolerancia de beneficios, a excepción.
- **Límites:** los umbrales 0,7/0,4 son convención OKR, no PRINCE2 ni PMBOK; se declaran en el informe (los KR comprometidos usan 1,0/0,7). `okr.py` solo comprueba el formato del vínculo, no su existencia (eso lo hace `sanidad.py`); acepta `SM-C1` (métricas de contrapeso del PRD 6.12.4). Escritura en Tability nunca sin confirmación. El plan comercial de Tability que habilita el servidor MCP **[verificar]**.

---

## Caso 5 · Transcripciones y actas de reunión

- **Prompt del usuario:**
  1. Con archivo: "Procesá la transcripción del checkpoint del 3/12 y sacá las acciones; la dejé en `gestion/03-control/reuniones/2026-12-03-checkpoint-s1-original.vtt`."
  2. Con texto pegado: "Hacé el acta de esta reunión: <pegás la transcripción>."
  3. Con herramienta de reuniones (opcional): en tu terminal, conectar Granola, Fireflies, Zoom o minutes con `claude mcp add …` **[verificar]**; luego "Usá Fireflies como fuente de reuniones." (registra `integraciones.reuniones=fireflies`) y "Traé la transcripción del checkpoint del 3/12 y armá el acta."
- **Respuestas del usuario:** con herramienta conectada, el sistema lista las reuniones del rango: "La del checkpoint S1 del 3/12." Quien presidió confirma el acta antes de cargar nada: "Martín Suárez confirma el acta; cargá las acciones." Para el clima de equipo: "Hay consentimiento; anonimizalo" o "No analices el clima".
- **Entradas (qué aporta el usuario y cómo):** el archivo `.vtt`, `.srt`, `.txt` o `.docx`, que dejás en `gestion/03-control/reuniones/` o adjuntás en la sesión; el texto pegado, que el sistema guarda primero como `<fecha>-<reunion>-original.txt`; o la transcripción traída por el conector MCP (instantánea `gestion/03-control/fuentes/<sistema>-AAAA-MM-DD.md`); fecha, nombre de la reunión y quién presidió, en el prompt.
- **Objetivo:** acta con decisiones, acciones A-###, riesgos e issues propuestos a partir de una transcripción.
- **Momento PRINCE2:** CS/MP (checkpoints, dailies, reuniones con el cliente), DP (actas de junta, que firma pm-director), SB y CP (talleres). Quien presidió confirma el acta; nada entra a los registros antes.
- **Dueña y agente:** `pm-reuniones`, desde `pm-control` (o `pm-cierre` en CP).
- **Externa:** fuentes vía `pm-integraciones`, capacidad `reuniones` (indicios `granola`, `fireflies`, `zoom`, `minutes`, `teams`): listar reuniones de un rango, confirmar cuál y traer la transcripción completa, no solo el resumen automático. La obtención de transcripciones por Zoom MCP **no está confirmada**. minutes es MIT (`minutes-mcp`). meeting-analyzer no se incorporó.
- **Respaldo:** archivo `.vtt`, `.srt`, `.txt` ("Nombre: texto" o con marcas `[hh:mm:ss]`), `.docx` (requiere `python-docx`) o texto pegado, guardado primero como `<fecha>-<reunion>-original.txt`.
- **Frases:** "Procesá la transcripción del comité de ayer y sacá las acciones" (#13); "Turn this meeting transcript into minutes and action items: …" (#44).
- **Pasos reales:** los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $T gestion/03-control/reuniones/2026-12-03-checkpoint-s1-original.vtt \
        --salida gestion/03-control/reuniones/2026-12-03-checkpoint-s1-transcripcion.md
  5 intervenciones de 3 hablantes → …/2026-12-03-checkpoint-s1-transcripcion.md
  $ python3 $T gestion/03-control/reuniones/2026-12-03-checkpoint-s1-original.vtt --anonimizar --json
  "intervenciones": 5, "hablantes": 3, "duracion": "00:00:36",
  "participacion": {"P2": {"turnos": 1, "palabras": 27, "pct_palabras": 38.0}, "P1": {…}, "P3": {…}}, "anonimizado": true
  ```
  También se probaron un `.srt` y un `.txt` con marcas de tiempo (2 intervenciones de 2 hablantes cada uno). Tras la
  confirmación de quien presidió, las cargas van por script:
  ```bash
  python3 $E/registro.py --proyecto gestion agregar acciones --campo origen=acta-reunion-2026-12-03 \
      --campo descripcion="Pedir credenciales del entorno de pruebas del núcleo" --campo responsable="Lucía Benítez" \
      --campo fecha_compromiso=2026-12-11 --campo prioridad=alta          # → A-001
  python3 $E/estado.py --proyecto gestion artefacto acta-reunion-2026-12-03 --ruta 03-control/reuniones/2026-12-03-acta-checkpoint-s1.md --estado en-revision
  ```
- **Salidas (qué queda y dónde verificarlo):** `03-control/reuniones/<fecha>-<reunion>-transcripcion.md` (ejemplo en `docs/ejemplos/integraciones/transcripcion-checkpoint.md`), `<fecha>-acta-<reunion>.md`; con herramienta conectada, instantánea `03-control/fuentes/<sistema>-AAAA-MM-DD.md` con front matter `fuente`, `fecha`, `consulta`. Dónde verificarlo: abrí `gestion/03-control/reuniones/2026-12-03-acta-checkpoint-s1.md`; la acción A-001 es una fila de `gestion/03-control/registros/acciones.csv` (abrilo en Excel; `origen` = `acta-reunion-2026-12-03`); la clave `acta-reunion-2026-12-03` figura en `gestion/estado.json` → `artefactos` como `en-revision`; `/pm-method:pm-estado` muestra las acciones vencidas por responsable.
- **Controles:** hook: `riesgos.csv` o `acciones.csv` editados a mano se bloquean ("se modifica con registro.py"); INT-01 valida el valor de `reuniones`. Registrar el acta solo después de escribirla: en la prueba se registró antes y la sanidad respondió `ERROR ART-01 Artefacto acta-reunion-2026-12-03 registrado pero no existe`.
- **Límites:** el script cuenta, no interpreta: no infiere emociones. El clima de equipo solo con consentimiento, `--anonimizar` y agregado. Una línea sin "Nombre:" que sigue a otra con hablante se agrega al turno anterior (no queda como `?`): revisar continuaciones mal atribuidas. Granola, Fireflies, Zoom y minutes: **documentado sin prueba en vivo**.

---

## Caso 6 · Trackers, documentación y canales (Jira, Confluence, Slack, Teams)

- **Prompt del usuario:**
  1. En tu terminal: conectar Atlassian Rovo (Jira, Confluence), Slack o Teams/Work IQ con `claude mcp add …` (URL y autenticación según cada proveedor; ver Externa) **[verificar]**.
  2. "Registrá Jira como tracker, Confluence para documentación y Teams para el chat."
  3. "Traé los tickets abiertos de Jira del sprint actual." Atajo: `/pm-method:pm-sync tracker`.
  4. "Publicá el resumen semanal en el canal de Teams del proyecto."
- **Respuestas del usuario:** el sistema propone las diferencias entre la instantánea y los registros: "Aceptá la acción nueva de jira:ABC-12" o "Esa no". Si aparece alcance nuevo, "Abrí la solicitud de cambio" (pm-issues-cambios). Para publicar o crear tickets, revisar la vista previa (destino exacto, contenido) y contestar "Confirmo" o corregir el destino.
- **Entradas (qué aporta el usuario y cómo):** la conexión MCP, hecha por el usuario en su cliente (sin credenciales en el proyecto); el mapa de integraciones, en el prompt 2; los tickets, traídos por el conector y guardados como instantánea `gestion/03-control/fuentes/jira-AAAA-MM-DD.csv`; el canal de destino, confirmado por el usuario; el contenido a publicar, del highlight (caso 2.1).
- **Objetivo:** leer el estado real del equipo en su tracker y publicar comunicaciones en sus canales, sin que el tracker reemplace a los registros de gobierno.
- **Momento PRINCE2:** CS/MP en cada período (`/pm-method:pm-sync tracker`); IP para registrar capacidades (`pm-inicio`, paso 15). El gestor confirma cada lote de escrituras externas.
- **Dueña y agente:** `pm-integraciones`, desde `pm-control` (paso 2 del bucle) o `pm-inicio`.
- **Externa:** capacidades genéricas, **sin conector predefinido** ni `.mcp.json` en el paquete. Notas relevadas al 2026-10-17 (INTEGRACIONES §2): Atlassian Rovo MCP Server requiere obtener el `cloudId` con `getAccessibleAtlassianResources` antes de herramientas como `searchJiraIssuesUsingJql` o `createJiraIssue`; el Slack MCP oficial (`https://mcp.slack.com/mcp`) está restringido a apps publicadas o internas; el servidor "Teams (preview)" de Microsoft figura como legado (se recomienda Work IQ). La skill siempre lee la descripción real de las herramientas presentes en la sesión.
- **Respaldo:** registros CSV (`backlog.csv`, `acciones.csv`), Markdown local y borradores de mensaje para copiar. Para publicar en Teams o Slack sin servidor MCP, o para escribir a interesados del maestro, está la capa de canales (webhooks, correo o `.eml`; caso 8).
- **Frases:** "Traé los tickets abiertos de Jira del sprint actual" (#16); "Publicá el resumen semanal en el canal de Teams" (#17). EN: "Sync Jira and post the highlight to the project Slack channel."
- **Pasos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion integracion tracker=jira docs=confluence chat=teams
  # lectura (sin confirmación) → instantánea inmutable 03-control/fuentes/jira-AAAA-MM-DD.csv
  #   columnas: clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url
  # conciliación → propuestas a registros; alcance nuevo → pm-issues-cambios; clave en notas como jira:ABC-12
  # escritura (crear tickets, publicar) → vista previa → confirmación explícita → id externo en notas o diario.md
  ```
  Controles de sanidad reales sobre el proyecto de prueba:
  ```text
  AVISO INT-02 Tracker jira declarado sin instantáneas en 03-control/fuentes/.          (antes de la primera lectura)
  AVISO INT-04 Instantánea sin fecha en el nombre: jira-ultimo.csv.
  AVISO INT-01 integraciones.tracker = 'trello' no es un valor conocido (azure-devops, github, jira, linear, ninguno).
  ```
- **Salidas (qué queda y dónde verificarlo):** `03-control/fuentes/jira-2026-12-18.csv`, propuestas de cambio a registros y anotaciones de publicación en `diario.md`. El tablero (caso 1.4) cita la instantánea como fuente y usa su fecha de corte. Dónde verificarlo: abrí `gestion/03-control/fuentes/jira-2026-12-18.csv` en Excel (columnas `clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url`); en `gestion/estado.json` → `integraciones`: `tracker` = `jira`, `docs` = `confluence`, `chat` = `teams`; las propuestas aceptadas aparecen en `gestion/03-control/registros/acciones.csv` o `issues.csv` con `jira:<clave>` en `notas`; el id de cada publicación, en `gestion/03-control/registros/diario.md`; `/pm-method:pm-sanidad` sin INT-02.
- **Controles:** INT-01…04; columnas de gobierno (`moscow`, `release`, `producto_pbs`, `prioridad`) solo de pm-method; en un subagente, toda escritura vuelve como "decisión humana requerida"; si una herramienta falla dos veces, alternativa local.
- **Límites:** **documentado sin prueba en vivo** (no hubo servidores conectados); la instantánea de la prueba se escribió a mano para verificar los controles. `estado.py integracion` guarda un valor desconocido pero avisa en el momento (y la sanidad lo marca, INT-01). El hook impide modificar una instantánea existente de `03-control/fuentes/` (se crea una nueva con fecha). INT-03 (más de 14 días) no avisa si la fecha del nombre es futura.

### 6.1 De la instantánea de Jira a riesgos e issues

- **Prompt del usuario:** "Traé la instantánea de Jira del sprint y decime qué incidencias son riesgos o issues."
- **Objetivo:** que las incidencias emergentes alimenten la gestión de riesgos: lo ya ocurrido se trata como issue (con
  su riesgo derivado) y lo que todavía puede pasar, como riesgo candidato; sin que Jira escriba en los registros.
- **Momento PRINCE2:** CS/MP, en cada período de control (tema riesgo y progreso).
- **Dueñas y agente:** `pm-integraciones` trae la instantánea; `pm-riesgos` clasifica con `riesgos.py candidatos
  --fuentes tracker`; `pm-issues-cambios` registra los issues; agente `pm-control`.
- **Columnas:** las mínimas del caso 6 más, opcionales, `prioridad`, `etiquetas`, `vinculo` y `descripcion`
  (INTEGRACIONES §3 y guía de pm-integraciones §3).
- **Pasos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $PM/pm-riesgos/scripts/riesgos.py --proyecto gestion candidatos --fuentes tracker --fecha 2026-12-16
  python3 $E/registro.py --proyecto gestion actualizar riesgos R-001 --campo "estado=ocurrido" --campo "notas=… origen: jira:PS-102"
  python3 $E/registro.py --proyecto gestion agregar issues --campo "tipo=problema-preocupacion" … --campo "notas=origen: jira:PS-102"
  ```
- **Salida real (guía E2E-1, paso 9):**
  ```text
  tracker: 3 candidatos · 1 fuente(s) leída(s)
  CR-01 [issue/amenaza] jira:PS-101 … · La consulta de saldos devuelve timeout con el padrón de prueba · ¿relacionado con R-001?
  CR-02 [issue/amenaza] jira:PS-102 … · Sin entorno de pruebas del padrón: historias 1-3 y 1-4 bloqueadas · ¿relacionado con R-001?
  CR-03 [riesgo/amenaza] jira:PS-104 … · Evaluar un proveedor de SMS alternativo por la disponibilidad del segundo factor · ¿duplica R-003?
  ```
  Reglas: tipo bug, incidente o impedimento, o estado bloqueado → issue; etiqueta `riesgo` → riesgo; otro tipo con
  prioridad alta → riesgo candidato; historias, tareas y épicas sin esas marcas se ignoran. El gestor decide: R-001 pasa a `ocurrido`, se registran I-001 (PS-102) e
  I-002 fuera de especificación (PS-101), y R-003 anota el seguimiento de PS-104.
- **Dónde verificarlo:** `gestion/03-control/reportes/2026-12-16-candidatos-riesgo.md`, `riesgos.csv` e `issues.csv`
  (columna `notas` con `origen: jira:<clave>`).
- **Límites:** probado con scripts sobre una instantánea escrita a mano (guía E2E-1 y `probar_paquete.py` caso I); la
  lectura desde Atlassian Rovo sigue sin prueba en vivo. Los nombres de tipo, estado y prioridad dependen de la
  configuración de cada Jira: los reconocidos están en `riesgos.py` (`TIPOS_ISSUE`, `ESTADO_BLOQUEO`, `PRIORIDAD_ALTA`).

---

## Caso 7 · BMAD como capa de especificación (pm-bmad-puente)

- **Prompt del usuario:**
  1. Requisito previo, del equipo y en su terminal: BMAD instalado (`npx bmad-method@6.12.4 install …`, INSTALACION §4).
  2. "Usá BMAD como especificación del proyecto." (detecta la versión y registra `integraciones.especificacion=bmad`; `/pm-method:pm-nuevo` también lo detecta al crear el proyecto).
  3. "Sincronizá el backlog con las historias de BMAD." Atajo: `/pm-method:pm-sync bmad`.
  4. "¿Qué requisitos del PRD no tienen historias?" · "¿Cambió el PRD desde que lo aprobó la junta?"
  5. Tras `autorizar-proyecto`: "La junta aprobó el proyecto: registrá la línea base del PRD v1.0, aprobada por Laura Méndez, ejecutiva."
- **Respuestas del usuario:** ante un desvío del PRD sin solicitud de cambio, "Abrí la solicitud de cambio"; ante prioridades nuevas, "Sí, emití el traspaso"; cuando el equipo BMAD aplica el traspaso, marca `estado: aplicado` en el documento de traspaso y se lo decís al sistema ("El equipo BMAD aplicó el traspaso de prioridades").
- **Entradas (qué aporta el usuario y cómo):** los artefactos de BMAD (`_bmad-output/…`: brief, PRD, épicas, `sprint-status.yaml`), leídos por `bmad.py` y la fachada `especificacion.py` en solo lectura: el usuario no copia nada; las prioridades de gobierno de la PO (caso 3.4) y la aprobación de la junta con nombre y rol, en el prompt.
- **Objetivo:** usar el PRD, la arquitectura, las épicas y el `sprint-status.yaml` de BMAD como especificación, sin escribir nunca en BMAD, y devolverle las decisiones de gobierno por traspaso.
- **Momento PRINCE2:** SU/IP (`detectar`, `inventario`, `requisitos`, `trazabilidad`, `backlog`), DP (`linea-base` tras `autorizar-proyecto`, por pm-director), CS (`backlog`, `avance`, `verificar` en cada período), SB (`verificar` antes de la puerta), cambios aprobados → `handoff`.
- **Dueña y agente:** `pm-bmad-puente` (metadato `agente: pm-planificacion`); también `pm-inicio`, `pm-control`, `pm-director` y `pm-cierre` en sus bucles. El resto de las skills lee solo por la fachada `especificacion.py` (contrato `pm-spec-index/1`).
- **Externa:** BMAD Method instalado por el equipo (`npx bmad-method@6.12.4 install …`, INSTALACION §4); versiones probadas 4.x, 6.11 y 6.12 (`compatibilidad.json`). Fixture real 6.12.4.
- **Respaldo:** `especificacion=ninguna`: `requisitos.md`, `backlog.csv` y `wbs.csv` con el mismo contrato.
- **Frases:** "Sincronizá el backlog con las historias de BMAD" (#14); "¿Qué requisitos del PRD no tienen historias?" (#15); "Did the PRD change since the board approved it?" (#45).
- **Pasos reales sobre el fixture:** los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $B --proyecto gestion inventario
  BMAD v6 (soportada) en <repo>
    brief   1 archivo(s) · estado=final · … · sha 58db1efac463 · _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md
    prd     1 archivo(s) · estado=final · … · sha bc048f7f59a3 · _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md
    historias 1 archivo(s) · estado=ready-for-dev · … · _bmad-output/implementation-artifacts/spec-1-1-alta-y-acceso-del-socio-con-segundo-factor.md
  $ python3 $B --proyecto gestion requisitos
  42 identificadores · {'UJ': 3, 'FR': 12, 'NFR': 6, 'SM': 8, 'AD': 13} → gestion/02-planificacion/especificacion/requisitos-bmad.csv (derivado: no editar)
  $ python3 $B --proyecto gestion trazabilidad --wbs 02-planificacion/wbs.csv
  18 requisitos trazados → gestion/02-planificacion/especificacion/matriz-trazabilidad-bmad.csv
    Requisitos funcionales sin historia: ninguno
    Trazados solo a nivel de épica (epics.md no cita el id en la historia): FR-1, FR-2, … FR-12
    Referencias de la WBS a ids inexistentes: ninguna
  $ python3 $B --proyecto gestion backlog
  backlog.csv: 10 nuevas, 0 actualizadas, 0 retiradas en BMAD. … las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
  $ python3 $B --proyecto gestion linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"
  Línea base bmad-prd v1.0 registrada · sha bc048f7f59a3 · copia congelada en gestion/00-direccion/historial/bmad-prd-v1.0
  $ python3 $B --proyecto gestion handoff
  Traspaso emitido → gestion/02-planificacion/especificacion/handoff-bmad-2026-10-17-prioridades.md (4 prioridades cambiadas)
  $ python3 $B --proyecto gestion avance --corte 2026-12-10
  Historias 10 · backlog 9 · ready-for-dev 1 · … · épicas terminadas 0/3 · 0.0 % (historias) → gestion/03-control/reportes/avance-bmad.csv
  $ python3 $B --proyecto gestion verificar
  Sin desvíos: la especificación coincide con las líneas base registradas.
  ```
  Tras cargar las estimaciones de gobierno, `avance --json` pasó a `"puntos_total": 24.0`, `"base_pct": "puntos"` (una fila por fecha).
- **Salidas (qué queda y dónde verificarlo):** derivados en `02-planificacion/especificacion/` (`inventario-bmad.json`, `requisitos-bmad.csv`, `matriz-trazabilidad-bmad.csv`, `spec-index.json`, `handoff-bmad-<fecha>-<…>.md`), columnas derivadas de `backlog.csv`, `03-control/reportes/avance-bmad.csv`, línea base en `00-direccion/historial/bmad-prd-v1.0/`. Dónde verificarlo: abrí `gestion/02-planificacion/especificacion/matriz-trazabilidad-bmad.csv` y `gestion/02-planificacion/backlog.csv` en Excel (10 historias); la línea base es la clave `bmad-prd` de `gestion/estado.json` → `artefactos`, la carpeta `gestion/00-direccion/historial/bmad-prd-v1.0/` y una fila `línea base bmad-prd v1.0 …` en `gestion/03-control/registros/decisiones.csv`; `/pm-method:pm-estado` muestra el avance BMAD y `/pm-method:pm-sync bmad` corre `verificar` ("Sin desvíos…"); `_bmad-output/` no cambia.
- **Controles:** hook: los derivados (`requisitos-bmad.csv`, `avance-bmad.csv`, …) no se editan ("es un derivado regenerable") y un subagente pm-* que escriba en `_bmad-output/` recibe "los agentes de gestión no escriben en carpetas de BMAD. Usar bmad.py handoff …"; el hilo principal sí puede (los flujos de BMAD escriben ahí). Sanidad ESP-01…15: `AVISO ESP-13 Traspaso a BMAD sin confirmar` hasta que el equipo BMAD marque `estado: aplicado`; ESP-10 si el PRD cambia sin solicitud de cambio (lo cubre `probar_paquete.py`, caso A).
- **Límites:** en el formato 6.12.4 las historias no citan el FR, así que la traza es por épica y la columna `refs` de cada historia trae todos los FR de su épica. La `descripcion` derivada del backlog es el primer párrafo completo de la historia ("As a socio, I want…, So that…"). `bmad-spec` (`specs/spec-<slug>/SPEC.md`) no se traza. Fuera del rango probado, modo degradado con aviso.

---

## Caso 8 · Capa de canales: correo SMTP, conector de correo, Teams, Slack y .eml

Contrato común (guía de `pm-integraciones` §6 y de `pm-comunicacion-stakeholders` §6): una sola vía de salida
para cualquier comunicación a interesados del maestro (`stakeholders.csv`): comunicados personalizados, informes,
actas, recordatorios de acciones, convocatorias, decisiones de puerta y check-ins de OKR. Cada mensaje es un `.md` con
frontmatter (`para`, `canal`, `destino`, `formato`, `nivel_detalle`, `idioma`, `registro`, `horario`, `asunto`,
`estado`, `aprobado_por`, `proposito`) en `03-control/comunicaciones/<fecha>-<tema>/`, junto a `plan-envio.csv`. Lo
crean `interesados.py plan-envio` (con el perfil de cada destinatario) o `envios.py nuevo --origen <archivo>`. Nada sale
sin (1) mensaje aprobado con `aprobado_por` (acto humano) y (2) `--confirmar`; sin `--confirmar` todo es simulación.
Los destinos se toman del maestro en el momento de enviar (`correo` para correo, `usuario_chat` para Slack y Teams); un
reenvío solo alcanza a quien todavía no tiene fila `enviado`. Cada envío queda en `envios.csv` (EN-###, con
`proposito`, `destino`, `referencia` y `confirmado_por`) y en `diario.md`; si hubo fallos, el código de salida es 2 y
la integridad avisa STK-07. Credenciales **solo** por variables de entorno (INSTALACION §0.7, "Capa de canales");
nunca en archivos, commits ni chat. Sin dependencias nuevas: biblioteca estándar (`smtplib`, `email`, `urllib`).

Variables de los comandos (además de las del "Proyecto de prueba"):

```bash
I="$PM/pm-interesados/scripts/interesados.py"; V="$PM/pm-integraciones/scripts/envios.py"
```

| Modo de `envios.py enviar` | Canal del mensaje | Variables de entorno |
|---|---|---|
| `smtp` | correo | `PM_SMTP_HOST`, `PM_SMTP_REMITENTE` (obligatorias); `PM_SMTP_PUERTO` (587), `PM_SMTP_TLS` (`starttls` por defecto, `ssl`, `ninguno`), `PM_SMTP_USUARIO`, `PM_SMTP_CLAVE` |
| `eml` | correo | ninguna |
| `teams-webhook` | teams | `PM_TEAMS_WEBHOOK_URL` |
| `slack-webhook` | slack | `PM_SLACK_WEBHOOK_URL` |
| conector MCP (`preparar-mcp` + `registrar --modo mcp`) | correo, slack o teams | las del conector, en el cliente |

### 8.1 Correo con el servidor SMTP de la organización

- **Prompt del usuario:**
  1. En tu terminal (una sola vez): definir `PM_SMTP_HOST`, `PM_SMTP_REMITENTE` y, si el servidor pide autenticación, `PM_SMTP_USUARIO` y `PM_SMTP_CLAVE`, como variables de entorno de tu usuario (INSTALACION §0.7); abrir Claude Code desde esa terminal.
  2. "Verificá que el correo esté configurado y registrá SMTP como canal de correo." (corre `envios.py verificar --modo smtp` y `estado.py integracion correo=smtp`).
  3. "Prepará el comunicado del avance al 8/1 para «gestionar de cerca» y «mantener satisfecho», menos yo, adaptado a cada perfil; mostrame los borradores y, si los apruebo, mandalos por correo."
- **Respuestas del usuario:** "Sí, aprobados por Martín Suárez, gestor." Después de la simulación: "Sí, enviá."
- **Entradas (qué aporta el usuario y cómo):** las variables de entorno, definidas por el usuario en su terminal (nunca en el chat); la audiencia, en el prompt; los correos, de la columna `correo` de `gestion/03-control/registros/stakeholders.csv`; el contenido base, redactado por `pm-comunicacion-stakeholders`.
- **Objetivo:** que cada interesado reciba el comunicado por correo, adaptado a su perfil, con registro de quién aprobó y cuándo salió.
- **Momento PRINCE2:** CS (highlight, comunicados, recordatorios) y DP/SB (convocatorias y decisiones de puerta), según el enfoque de comunicación del PID. Aprueba el gestor (o quien fije la matriz); el envío lo confirma el usuario.
- **Dueña y agente:** contenido y plan de envío, `pm-comunicacion-stakeholders` con `pm-interesados`; envío, `pm-integraciones` (`envios.py`); desde `pm-control`.
- **Externa:** el servidor SMTP de la organización (protocolo estándar; un correo de texto por destinatario; referencia = Message-ID).
- **Respaldo:** modo `eml` (8.5) o conector de correo (8.2).
- **Frase:** "Mandá el comunicado aprobado por correo a los interesados." EN: "Email the approved update to the stakeholders."
- **Pasos reales** (corrida de referencia de la guía E2E-3, paso 11): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $V --proyecto gestion verificar --modo smtp          # corrida complementaria, sin variables definidas
     PM_SMTP_HOST: no definida
     PM_SMTP_REMITENTE: no definida
     …
  Faltan: PM_SMTP_HOST, PM_SMTP_REMITENTE
  $ python3 $I --proyecto gestion plan-envio --tema "Avance del portal al 8 de enero" --audiencia "cuadrante:gestionar-de-cerca,cuadrante:mantener-satisfecho,-ST-009" --proposito informe --base gestion/03-control/reportes/2027-01-15-comunicado-consejo.md --agrupar --fecha 2027-01-15
  Plan de envío → 03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero/ (7 destinatarios, 5 mensajes en borrador)
  $ python3 $V --proyecto gestion aprobar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --por "Gestor: Martín Suárez"
  5 mensaje(s) aprobados por Gestor: Martín Suárez
  $ python3 $V --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --modo smtp
  SIMULACIÓN mensaje-01-correo-st-001-st-002-st-007.md [smtp] → ST-001 <laura.mendez@example.org>, ST-002 <consejo@example.org>, ST-007 <cumplimiento@example.org> · «Avance del portal al 8 de enero»
     (faltan variables de entorno: PM_SMTP_HOST, PM_SMTP_REMITENTE)
  Resumen: 0 enviados, 0 fallidos, 3 simulados, 2 omitidos · simulación: agregar --confirmar para enviar
  $ python3 $V --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --modo smtp --confirmar --fecha 2027-01-15
  mensaje-01-correo-st-001-st-002-st-007.md: enviado · EN-001, EN-002, EN-003
  · mensaje-02-teams-st-003.md: canal teams no corresponde a --modo smtp
  mensaje-03-correo-st-004.md: enviado · EN-004
  · mensaje-04-reunion-st-006.md: canal reunion no corresponde a --modo smtp
  mensaje-05-correo-st-008.md: enviado · EN-005
  Resumen: 5 enviados, 0 fallidos, 0 simulados, 2 omitidos
  ```
  En la corrida, el envío con `--confirmar` fue contra un servidor SMTP de prueba en 127.0.0.1 que levanta el script de la guía (recibió los cinco `RCPT TO`); con las variables del usuario sale a su servidor.
- **Salidas (qué queda y dónde verificarlo):** borradores aprobados y `plan-envio.csv` en `gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero/` (cada `.md` pasa a `estado: enviado` con `fecha_envio`); EN-001…EN-005 en `gestion/03-control/registros/envios.csv` (modo `smtp`, referencia = Message-ID, `confirmado_por` = "Gestor: Martín Suárez"); una línea por envío en `diario.md`; `integraciones.correo` = `smtp` en `gestion/estado.json`. Dónde verificarlo: abrir `envios.csv` en Excel; prompt "¿Qué le enviamos al sindicato y cuándo?" (`envios.py historial --stakeholder ST-004`).
- **Controles:** `aprobar` rechaza borradores sin redactar y mensajes con destinatarios que ya no existen en el maestro (y avisa si quedó el título "Contenido base (adaptar…)"); con `--confirmar` y variables faltantes no se envía nada; un destinatario sin correo queda como fila `fallido` ("sin correo en stakeholders.csv"); reenvío sin duplicados; el hook `guardian.py` protege `envios.csv`.
- **Límites:** probado con scripts contra un servidor de prueba local; con un servidor real **[sin verificar en vivo]**. Texto plano, sin adjuntos. Un servidor que exige OAuth en lugar de usuario y clave no se cubre: usar el conector (8.2) o `.eml` (8.5).

### 8.2 Conector de correo Gmail u Outlook (MCP): `preparar-mcp` y `registrar`

- **Prompt del usuario:**
  1. Conectar el correo de la organización en el cliente (gestión de conectores de la aplicación, o `claude mcp add …` con el servidor que la organización tenga aprobado; URL y herramientas según el proveedor **[verificar]**).
  2. "Usá el conector de Gmail como canal de correo." (registra `integraciones.correo=gmail`; con Outlook, `correo=outlook`).
  3. "Mandale a Laura la decisión pendiente sobre la contingencia del panel, por el conector de correo."
- **Respuestas del usuario:** "Aprobado por Martín Suárez, gestor." Ante la vista previa (destinatario, asunto, texto): "Confirmo, envialo."
- **Entradas (qué aporta el usuario y cómo):** la conexión, hecha por el usuario en su cliente (las credenciales quedan ahí, no en el proyecto); el pedido, en el prompt; el destino, del maestro; el contenido, de `03-control/reportes/2027-01-15-comunicado-consejo.md`.
- **Objetivo:** enviar desde la cuenta de la organización y dejar el mismo registro que la capa de canales.
- **Momento PRINCE2, dueña y agente:** igual que 8.1; la herramienta del conector la usa el agente, nunca el script.
- **Externa:** conector de correo de la organización (Gmail u Outlook). Sus nombres de herramientas no se citan: la skill lee la descripción real de las herramientas presentes en la sesión.
- **Respaldo:** 8.1 o 8.5.
- **Frase:** "Mandale la decisión pendiente a Laura por el conector de correo." EN: "Send the pending decision to Laura through the mail connector."
- **Pasos reales** (corrida complementaria; el envío por el conector no se ejecutó): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $V --proyecto gestion nuevo --origen 03-control/reportes/2027-01-15-comunicado-consejo.md --audiencia ST-001 --asunto "Decisión pendiente: contingencia del panel" --proposito puerta --fecha 2027-01-17
  Comunicación «Decisión pendiente: contingencia del panel» (puerta) → 03-control/comunicaciones/2027-01-17-contingencia-del-panel/ · 1 destinatarios
     ST-001 Laura Méndez: correo · conclusion-primero · ejecutivo · mensaje-01-correo-st-001.md
  $ python3 $V --proyecto gestion aprobar gestion/03-control/comunicaciones/2027-01-17-contingencia-del-panel --por "Gestor: Martín Suárez"
  1 mensaje(s) aprobados por Gestor: Martín Suárez
  $ python3 $V --proyecto gestion preparar-mcp gestion/03-control/comunicaciones/2027-01-17-contingencia-del-panel --canal correo
  {"mensajes": [{"archivo": "mensaje-01-correo-st-001.md", "canal": "correo", "asunto": "Decisión pendiente: contingencia del panel", "proposito": "puerta",
    "destinatarios": [{"id": "ST-001", "nombre": "Laura Méndez", "destino": "laura.mendez@example.org"}], "errores": [], "cuerpo": "…",
    "registrar_despues": "envios.py --proyecto gestion registrar 03-control/comunicaciones/2027-01-17-contingencia-del-panel --mensaje mensaje-01-correo-st-001.md --modo mcp --referencia <id del mensaje>"}],
   "nota": "Enviar con la herramienta MCP conectada SOLO tras mostrar la vista previa y obtener confirmación explícita; luego registrar cada envío."}
  # vista previa → confirmación → el agente envía con la herramienta del conector → con el id que devuelve:
  $ python3 $V --proyecto gestion registrar gestion/03-control/comunicaciones/2027-01-17-contingencia-del-panel --mensaje mensaje-01-correo-st-001.md --modo mcp --referencia id-del-mensaje-ejemplo --fecha 2027-01-17
  EN-010
  ```
  (JSON recortado y en menos líneas.) Observación: el nombre de la carpeta se armó solo con la parte del asunto posterior a los dos puntos.
- **Salidas (qué queda y dónde verificarlo):** el borrador aprobado en `gestion/03-control/comunicaciones/2027-01-17-contingencia-del-panel/`; EN-010 en `envios.csv` (`correo/mcp`, referencia = id del mensaje que devolvió el conector) y la línea en `diario.md`. Dónde verificarlo: `envios.py historial --stakeholder ST-001` → `EN-010 2027-01-17 ST-001 correo/mcp «Decisión pendiente: contingencia del panel» [enviado] id-del-mensaje-ejemplo`; el mensaje en la carpeta de enviados de la cuenta.
- **Controles:** `preparar-mcp` solo lista mensajes aprobados y destinatarios pendientes; `registrar --estado enviado` se rechaza si el mensaje no está aprobado ("El mensaje no está aprobado: no se registra como enviado."); en un subagente, el envío vuelve como "decisión humana requerida".
- **Límites:** `preparar-mcp` y `registrar` probados con scripts; el envío con un conector Gmail u Outlook real **[sin verificar en vivo]**. Que el registro refleje la entrega depende de que el agente registre la referencia que devuelve la herramienta.

### 8.3 Webhook de Teams (Workflows)

- **Prompt del usuario:**
  1. En Teams (una sola vez, quien administre el canal): crear un flujo de Workflows con el desencadenador "When a Teams webhook request is received" que publique en el canal del proyecto, copiar la URL y definirla en tu terminal como `PM_TEAMS_WEBHOOK_URL` (la URL es en sí la credencial).
  2. "Verificá Teams y mandale a Sofía el comunicado por Teams."
- **Respuestas del usuario:** aprobación con nombre y rol; después de la simulación, "Sí, enviá".
- **Entradas (qué aporta el usuario y cómo):** la URL del flujo, solo como variable de entorno; el mensaje, del plan de envío (canal `teams` porque Sofía lo pidió: PF-005); el nombre del destinatario, del maestro.
- **Objetivo:** publicar en el canal de Teams del proyecto sin servidor MCP.
- **Momento PRINCE2, dueña y agente:** igual que 8.1.
- **Externa:** Teams Workflows. Mensaje `{"type":"message","attachments":[{"contentType":"application/vnd.microsoft.card.adaptive","content":{AdaptiveCard 1.0}}]}` con tres bloques (asunto, "Para: <nombres>", cuerpo); límite de 28 KB, según https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook (verificado el 2026-10-17; esa página indica además que los conectores de Office 365 están "nearing deprecation").
- **Respaldo:** conector MCP de Teams (8.2 con `--canal teams`) o correo (8.1).
- **Frase:** "Mandale a Sofía el comunicado por Teams." EN: "Post the update to Sofía on Teams."
- **Pasos reales** (guía E2E-3, paso 11): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $V --proyecto gestion verificar --modo teams-webhook          # corrida complementaria, sin la variable
     PM_TEAMS_WEBHOOK_URL: no definida
  Faltan: PM_TEAMS_WEBHOOK_URL
  $ python3 $V --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --modo teams-webhook --confirmar --fecha 2027-01-15
  · mensaje-01-correo-st-001-st-002-st-007.md: canal correo no corresponde a --modo teams-webhook
  mensaje-02-teams-st-003.md: enviado · EN-006
  …
  Resumen: 1 enviados, 0 fallidos, 0 simulados, 4 omitidos
  ```
  El receptor de prueba de 127.0.0.1 recibió la tarjeta con el asunto «Avance del portal al 8 de enero»; `historial` registra `EN-006 2027-01-15 ST-003 teams/teams-webhook «Avance del portal al 8 de enero» [enviado] teams-webhook HTTP 200`.
- **Salidas (qué queda y dónde verificarlo):** EN-006 en `envios.csv` (destino = `usuario_chat` de ST-003; referencia = código HTTP); `mensaje-02-teams-st-003.md` en `estado: enviado`; la línea en `diario.md`. Dónde verificarlo: la tarjeta en el canal de Teams; `envios.csv` en Excel.
- **Controles:** un mensaje de más de 28 KB no se envía (queda `fallido` con el motivo); respuesta HTTP distinta de 200 o 202 = `fallido`; solo se envían los mensajes de canal `teams`.
- **Límites:** el webhook publica en un único canal (el del flujo) y la tarjeta no menciona personas: el destinatario figura en el bloque "Para:". Probado contra un receptor local; con un flujo real **[sin verificar en vivo]**.

### 8.4 Webhook de Slack

- **Prompt del usuario:**
  1. En Slack (una sola vez, quien administre el espacio de trabajo): crear un webhook entrante para el canal del proyecto (procedimiento según la documentación de Slack **[verificar]**) y definir su URL en tu terminal como `PM_SLACK_WEBHOOK_URL`.
  2. En una daily, Lucía dijo «Los recordatorios de acciones prefiero que me lleguen por Slack»: "Proponé y confirmá esa preferencia; su usuario de Slack es U0LUCIA01."
  3. "Mandale a quien es R de la épica E-3 el recordatorio de acciones vencidas."
- **Respuestas del usuario:** "Confirmala como Martín Suárez, gestor." · "Aprobado por Martín Suárez, gestor." · "Sí, enviá."
- **Entradas (qué aporta el usuario y cómo):** la URL, solo como variable de entorno; el id de Slack, en el prompt (el sistema lo guarda en `usuario_chat`); la audiencia `raci:E-3:R`, resuelta contra `raci.csv`; el contenido base `03-control/reportes/2027-01-12-recordatorio-acciones.md`.
- **Objetivo:** recordatorios y avisos breves en el canal del equipo, con mención a la persona.
- **Momento PRINCE2, dueña y agente:** CS/MP (recordatorios de acciones desde actas confirmadas); igual que 8.1.
- **Externa:** webhook entrante de Slack: JSON `{"text": …}` con el asunto en negrita y `<@ID>` cuando `usuario_chat` es un id de Slack (U… o W…).
- **Respaldo:** conector MCP de Slack (8.2 con `--canal slack`), correo o `.eml`.
- **Frase:** "Mandale el recordatorio de acciones vencidas por Slack." EN: "Send the overdue actions reminder on Slack."
- **Pasos reales** (corrida complementaria sobre la carpeta de la guía E2E-3): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $I --proyecto gestion proponer --transcripcion gestion/03-control/reuniones/2027-01-12-daily-transcripcion.md --fecha 2027-01-12 --registrar
  PF-009 ST-010 canal=slack (declarado) "Los recordatorios de acciones prefiero que me lleguen por Slack." [00:00:01]
  …
  $ python3 $I --proyecto gestion confirmar PF-009 --por "Gestor: Martín Suárez"
  confirmar: PF-009
  $ python3 $E/registro.py --proyecto gestion actualizar stakeholders ST-010 --campo usuario_chat=U0LUCIA01
  ok
  $ python3 $I --proyecto gestion plan-envio --tema "Recordatorio de acciones vencidas" --audiencia raci:E-3:R --proposito recordatorio --base gestion/03-control/reportes/2027-01-12-recordatorio-acciones.md --fecha 2027-01-12
  Plan de envío → 03-control/comunicaciones/2027-01-12-recordatorio-de-acciones-vencidas/ (1 destinatarios, 1 mensajes en borrador)
     ST-010 Lucía Benítez: slack → U0LUCIA01 · lista · detallado · es · mensaje-01-slack-st-010.md
  $ python3 $V --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-12-recordatorio-de-acciones-vencidas --modo slack-webhook
  SIMULACIÓN mensaje-01-slack-st-010.md [slack-webhook] → ST-010 <U0LUCIA01> · «Recordatorio de acciones vencidas»
     (faltan variables de entorno: PM_SLACK_WEBHOOK_URL)
  $ python3 $V --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-12-recordatorio-de-acciones-vencidas --modo slack-webhook --confirmar --fecha 2027-01-12
  mensaje-01-slack-st-010.md: enviado · EN-008
  Resumen: 1 enviados, 0 fallidos, 0 simulados, 0 omitidos
  ```
  Lo que recibió el receptor de prueba de 127.0.0.1: `{"text": "*Recordatorio de acciones vencidas*\n<@U0LUCIA01>\n# Recordatorio de acciones vencidas\n\nA-004 Prototipo de bandeja con métricas de equipo (vencida el 2026-12-11)."}`. Repetir el envío responde "· mensaje-01-slack-st-010.md: ya enviado".
- **Salidas (qué queda y dónde verificarlo):** PF-009 `confirmada` en `preferencias.csv`; `usuario_chat=U0LUCIA01` en `stakeholders.csv`; EN-008 en `envios.csv` (`slack/slack-webhook`, referencia "slack-webhook HTTP 200"); la línea en `diario.md`. Dónde verificarlo: el mensaje en el canal de Slack; `envios.py historial --stakeholder ST-010`; `interesados.py vinculos ST-010` muestra PF-009 y EN-008.
- **Controles:** solo se envían mensajes de canal `slack`; respuesta distinta de HTTP 200 = `fallido`. El texto se envía tal como quedó el borrador: en la corrida conservó el encabezado Markdown `# …` del contenido base (cómo lo muestra Slack **[verificar]**); conviene que el modelo adapte el texto al canal antes de aprobar.
- **Límites:** el webhook publica en un único canal; la mención solo funciona con ids de Slack, no con correos. Probado contra un receptor local; con un webhook real **[sin verificar en vivo]**.

### 8.5 Archivos .eml sin configuración

- **Prompt del usuario:** "No tengo servidor de correo configurado: generá los .eml del highlight para cumplimiento y yo los mando desde mi correo." Después de enviarlo: "Ya lo mandé desde mi correo; registralo."
- **Respuestas del usuario:** "Aprobado por Martín Suárez, gestor."
- **Entradas (qué aporta el usuario y cómo):** el pedido, en el prompt; el informe de origen, `03-control/reportes/2027-01-08-highlight-report.md`; el correo del destinatario, del maestro. No hace falta ninguna variable de entorno.
- **Objetivo:** enviar desde el cliente de correo del usuario manteniendo el registro.
- **Momento PRINCE2, dueña y agente:** igual que 8.1 (`integraciones.correo=eml`).
- **Externa:** ninguna; el usuario abre el `.eml` en su cliente de correo.
- **Respaldo:** es en sí el respaldo de 8.1 y 8.2.
- **Frase:** "Generá los .eml del comunicado." EN: "Create .eml drafts for the update."
- **Pasos reales** (corrida complementaria): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $V --proyecto gestion nuevo --origen 03-control/reportes/2027-01-08-highlight-report.md --audiencia ST-007 --asunto "Highlight report al 8 de enero" --proposito informe --fecha 2027-01-16
  Comunicación «Highlight report al 8 de enero» (informe) → 03-control/comunicaciones/2027-01-16-highlight-report-al-8-de-enero/ · 1 destinatarios
     ST-007 Unidad de cumplimiento: correo · conclusion-primero · ejecutivo · mensaje-01-correo-st-007.md
  $ python3 $V --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-16-highlight-report-al-8-de-enero --modo eml --confirmar --fecha 2027-01-16
  mensaje-01-correo-st-007.md: eml-generado · EN-009
  $ python3 $I --proyecto gestion integridad --corte 2027-01-16
  AVISO STK-07: Envío EN-009 a ST-007 en estado pendiente (correo, Highlight report al 8 de enero)
  $ python3 $V --proyecto gestion registrar gestion/03-control/comunicaciones/2027-01-16-highlight-report-al-8-de-enero --mensaje mensaje-01-correo-st-007.md --modo eml --referencia "enviado desde el cliente de correo" --fecha 2027-01-16
  EN-009
  $ python3 $I --proyecto gestion integridad --corte 2027-01-16
  Integridad referencial y calidad del maestro: sin hallazgos.
  ```
  Cabeceras del archivo generado: `To: cumplimiento@example.org`, `Subject: Highlight report al 8 de enero`, `X-Unsent: 1`, `Content-Type: text/plain; charset="utf-8"`.
- **Salidas (qué queda y dónde verificarlo):** `gestion/03-control/comunicaciones/2027-01-16-highlight-report-al-8-de-enero/eml/mensaje-01-correo-st-007-st-007.eml`; EN-009 en `envios.csv`, primero `pendiente` y, tras `registrar`, `enviado` (`correo/eml`). Dónde verificarlo: abrir el `.eml` (con `X-Unsent: 1`, Outlook lo abre como borrador para enviar; otros clientes **[verificar]**); `envios.py historial --stakeholder ST-007`.
- **Controles:** mientras el `.eml` no se registre como enviado, la integridad avisa STK-07; `registrar` exige que el mensaje esté aprobado.
- **Límites:** el registro depende de que el usuario avise que lo envió; la cabecera `Date` del `.eml` es la de su generación, no la de `--fecha`.

---

## Caso 9 · OKR con Tability o Perdoo (servidores MCP oficiales)

Contrato común (guía de `pm-okr` §6): `okr.csv` y `00-direccion/okr_checkins.csv` siguen siendo la fuente; cada KR que
se sincroniza lleva en `ref_externa` su par en la herramienta (`tability:<id>` o `perdoo:<id>`). Publicar (escritura)
siempre es: `okr.py --propuesta-sync` (vista previa de los check-ins sin publicar, con la herramienta a usar) →
confirmación explícita → el agente publica con la herramienta del servidor MCP → `okr.py --marcar-publicado
KR@FECHA --destino … --ref <id>` (columna `publicado_en`). Leer: instantánea fechada en `03-control/fuentes/` y
registro como check-in con `--fuente`. Sin herramienta conectada, todo funciona igual. Viva Goals se retiró el
31/12/2025 (https://learn.microsoft.com/viva/goals/goals-retirement); Atlassian Goals y Asana Goals no se exponían por
sus MCP oficiales al 17/10/2026 **[verificar]**.

### 9.1 Tability

- **Prompt del usuario:**
  1. En tu terminal (una sola vez): `claude mcp add --transport http tability https://mcp.tability.app/mcp` (en Europa, `mcp-eu.tability.app/mcp`; en Australia, `mcp-au.tability.app/mcp`) y, en una sesión, `/mcp` para autenticar con OAuth. El usuario necesita tener habilitado "API access" en Tability.
  2. "Usá Tability para los OKR; KR-1.1 es kr-registro-portal en Tability." (registra `integraciones.okr=tability` y `ref_externa=tability:kr-registro-portal`).
  3. "Decime qué check-ins habría que publicar en Tability."
- **Respuestas del usuario:** con el conector: "Sí, publicá el del 8/1 de KR-1.1." Sin conector: "No, solo mostrame la propuesta."
- **Entradas (qué aporta el usuario y cómo):** la conexión MCP, hecha por el usuario en su cliente (OAuth; nada en el proyecto); el par de cada KR, en el prompt; los check-ins ya registrados en `okr_checkins.csv` (CASOS-DE-USO caso 45).
- **Objetivo:** que el tablero de OKR de la organización refleje los check-ins del proyecto sin cargarlos dos veces.
- **Momento PRINCE2:** CS (check-ins de cada período) y SB (puntuación en el límite de etapa); la aceptación de los OKR sigue siendo de la ejecutiva.
- **Dueña y agente:** `pm-okr` (propuesta y marca), publicación vía `pm-integraciones`; desde `pm-control` o `pm-director`.
- **Externa:** servidor MCP oficial de Tability (verificado el 2026-10-17: https://guides.tability.io/docs/become-a-tability-power-user/integrations/tability-mcp-server); escribe check-ins con `tability_create_checkin`. Plan comercial que lo habilita **[verificar]**.
- **Respaldo:** `okr=archivo` (`okr.csv` + `okr_checkins.csv`).
- **Frase:** "Decime qué check-ins habría que publicar en Tability." EN: "Which check-ins should we publish to Tability?"
- **Pasos reales** (guía E2E-3, paso 10): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $O gestion/00-direccion/okr.csv --propuesta-sync tability
  KR-1.1 2026-12-11 = 1 → tability:kr-registro-portal · tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp) · confidence green
  KR-1.1 2026-12-23 = 2 → tability:kr-registro-portal · tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp) · confidence green
  KR-1.1 2027-01-08 = 3 → tability:kr-registro-portal · tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp) · confidence green
  AVISO KR-1.2: sin ref_externa 'tability:…' (vincular el KR con su par en tability antes de publicar)
  AVISO KR-2.1: sin ref_externa 'tability:…' (vincular el KR con su par en tability antes de publicar)
  AVISO KR-2.2: sin ref_externa 'tability:…' (vincular el KR con su par en tability antes de publicar)
  $ python3 $O gestion/00-direccion/okr.csv --marcar-publicado KR-1.1@2027-01-08 --destino tability --ref checkin-ejemplo-1
  KR-1.1@2027-01-08 marcado como publicado en tability
  ```
  La confianza se traduce a los colores de Tability (rojo → red, ámbar → yellow, verde → green). Con `--json`, cada pendiente trae además el comando `marcar_despues` y la regla "Publicar solo tras mostrar esta vista previa y obtener confirmación explícita (pm-integraciones); okr.csv sigue siendo la fuente." En la corrida no hubo servidor Tability: `checkin-ejemplo-1` es una referencia de ejemplo.
- **Salidas (qué queda y dónde verificarlo):** columna `publicado_en` (`tability:<fecha>`) y `ref_externa` del check-in en `gestion/00-direccion/okr_checkins.csv`; el check-in publicado deja de aparecer en la propuesta siguiente. Dónde verificarlo: abrir `okr_checkins.csv` en Excel; el check-in en Tability.
- **Controles:** solo se proponen KR con `ref_externa` del destino; los demás salen como AVISO; `--marcar-publicado` falla si no existe el check-in ("No hay check-in KR-x del AAAA-MM-DD"); `integraciones.okr` acepta `archivo`, `tability` y `perdoo` (INT-01).
- **Límites:** propuesta y marca probadas con scripts; la publicación con el servidor real **[sin verificar en vivo]**.

### 9.2 Perdoo

- **Prompt del usuario:**
  1. En tu terminal (una sola vez): `claude mcp add --transport http perdoo https://mcp.perdoo.com` y autenticar con `/mcp` (OAuth) o con una API key de Perdoo (cómo se pasa, según la documentación de Perdoo **[verificar]**; siempre en el cliente, nunca en el proyecto).
  2. "Usá Perdoo para los OKR; KR-2.2 es goal-solicitudes-completas en Perdoo." (registra `integraciones.okr=perdoo` y `ref_externa=perdoo:goal-solicitudes-completas`).
  3. "Proponé qué publicar en Perdoo."
- **Respuestas del usuario:** "Publicá el del 8/1." o "Solo la propuesta."
- **Entradas (qué aporta el usuario y cómo):** la conexión MCP, en el cliente; el par del KR, en el prompt; los check-ins de `okr_checkins.csv`.
- **Objetivo, momento, dueña y agente:** igual que 9.1.
- **Externa:** servidor MCP oficial de Perdoo (https://support.perdoo.com/en/articles/14470891-mcp-server, artículo del 15/09/2026, verificado el 2026-10-17); registra progreso con `update_goal_progress` (valor, estado y nota). Plan comercial que lo habilita **[verificar]**.
- **Respaldo:** `okr=archivo`.
- **Frase:** "Proponé qué check-ins publicar en Perdoo." EN: "Propose which check-ins to push to Perdoo."
- **Pasos reales** (corrida complementaria, sobre una copia de `okr.csv` con `ref_externa=perdoo:goal-solicitudes-completas` en KR-2.2): los ejecuta el sistema; el usuario no los escribe.
  ```text
  $ python3 $O okr-perdoo/okr.csv --propuesta-sync perdoo
  KR-2.2 2026-12-11 = 64 → perdoo:goal-solicitudes-completas · update_goal_progress (MCP oficial de Perdoo: https://mcp.perdoo.com)
  KR-2.2 2026-12-23 = 68 → perdoo:goal-solicitudes-completas · update_goal_progress (MCP oficial de Perdoo: https://mcp.perdoo.com)
  KR-2.2 2027-01-08 = 72 → perdoo:goal-solicitudes-completas · update_goal_progress (MCP oficial de Perdoo: https://mcp.perdoo.com)
  AVISO KR-1.1: sin ref_externa 'perdoo:…' (vincular el KR con su par en perdoo antes de publicar)
  …
  $ python3 $O okr-perdoo/okr.csv --marcar-publicado KR-2.2@2027-01-08 --destino perdoo --ref progreso-ejemplo-1
  KR-2.2@2027-01-08 marcado como publicado en perdoo
  $ python3 $O okr-perdoo/okr.csv --checkin KR-2.2 --valor 75 --confianza 7 --fecha 2027-01-22 --autor "Usuaria sénior: Sofía Ramírez" --fuente perdoo
  Check-in KR-2.2 2027-01-22 = 75 → <repo>/okr-perdoo/okr_checkins.csv
  ```
  Con `--json`, cada pendiente trae un `status_sugerido` traducido de la confianza ("off track", "needs attention", "on track") marcado "[verificar nombres de estado en Perdoo]".
- **Salidas (qué queda y dónde verificarlo):** `publicado_en` = `perdoo:<fecha>` en `okr_checkins.csv`; el check-in leído de Perdoo queda con `fuente=perdoo`. Dónde verificarlo: abrir `okr_checkins.csv` en Excel; el progreso en Perdoo.
- **Controles:** los mismos que 9.1.
- **Límites:** los nombres de estado de Perdoo **[verificar]**; publicación con el servidor real **[sin verificar en vivo]**.

---

## Matriz de cierre

| Integración | Skill dueña | Agente | Respaldo | Control de sanidad | Estado de verificación |
|---|---|---|---|---|---|
| archify | pm-visuales | orquestador · pm-inicio · pm-planificacion | Mermaid (`wbs.py --mermaid`, plantillas) | INS-03 (instalada, Node, Chrome) | verificado en vivo (A1) · `finalize` probado con scripts sin Chrome |
| diagram-design | pm-visuales | ídem | Mermaid | INS-03 (no ve `--plugin-dir`) | verificado en vivo (B1, B2) para organigrama y WBS · `mermaid_extract.py` probado · roadmap y flujos sin verificar en vivo |
| visual-explainer | pm-visuales | ídem | `canvas-arranque.html` | INS-03 | verificado en vivo (C2, C3) · `render.mjs` probado con scripts |
| Tablero HTML (interno) | pm-visuales | pm-control | — (es interno) | regla rojo sin issue | probado con scripts (inyección JSON); vista por actor sin verificar en navegador |
| drawio-mcp | pm-visuales / pm-integraciones | ídem | Mermaid | INT-01 (valor conocido); sin INS | documentado sin prueba en vivo |
| Mermaid / `mmdc` | pm-visuales | ídem | código Mermaid sin imagen | — (`mmdc` es opcional y la sanidad no lo controla) | verificado en vivo como respaldo (E1, G1) · probado con scripts |
| Skills Office docx/xlsx/pptx | pm-exportar | orquestador · pm-director | `exportar.py`, `paquete.py`, guion de deck | INS-03, INS-01 | verificado en vivo (D1, D2; respaldo F1, F2) · `exportar.py` probado con scripts |
| MSPDI + MPXJ | pm-cronograma-estimacion | pm-planificacion | `cpm.py` (CPM y Gantt Mermaid) | INT-01 (`cronograma`) | probado con scripts (lectura con MPXJ 16.10) |
| EVM, WBS, CPM (`evm.py`, `wbs.py`, `cpm.py`) | pm-progreso-reportes · pm-planificacion-por-productos · pm-cronograma-estimacion | pm-control · pm-planificacion | — (internos) | EST-06/07, ESP-04 | probado con scripts |
| Tability MCP (oficial) | pm-okr (vía pm-integraciones) | pm-inicio · pm-control · pm-director · pm-cierre | `okr.csv` + `okr_checkins.csv` con `okr.py` | INT-01 (`okr`), ESP-04/05, STK-08 | `okr.py` (check-ins, `--propuesta-sync`, `--marcar-publicado`) probado con scripts · URL del servidor verificada el 2026-10-17 · publicación sin verificar en vivo |
| Perdoo MCP (oficial) | pm-okr (vía pm-integraciones) | ídem | ídem | ídem | `--propuesta-sync perdoo` probado con scripts · URL verificada el 2026-10-17 · nombres de estado y publicación sin verificar en vivo |
| Granola / Fireflies / Zoom / minutes | pm-reuniones (vía pm-integraciones) | pm-control · pm-cierre | archivo VTT/SRT/TXT/DOCX o texto pegado | INT-01 (`reuniones`) | `transcripcion.py` probado con scripts · MCP documentado sin prueba en vivo (Zoom no confirmado) |
| Atlassian Rovo (Jira, Confluence) | pm-integraciones (riesgos candidatos: pm-riesgos) | pm-control · pm-inicio | CSV y Markdown locales | INT-01…04 | documentado sin prueba en vivo · controles INT y clasificación de la instantánea en riesgos e issues (`riesgos.py`, caso 6.1) probados con scripts |
| Slack MCP, Teams/Work IQ | pm-integraciones (y pm-comunicacion-stakeholders) | pm-control | borrador para copiar o capa de canales (webhook, correo, `.eml`) | INT-01 (`chat`) | documentado sin prueba en vivo |
| Capa de canales: correo SMTP | pm-integraciones (`envios.py`; contenido: pm-comunicacion-stakeholders) | pm-control | `.eml` | INT-01 (`correo`), STK-07, hook sobre `envios.csv` | probado con scripts contra un servidor SMTP local (guía E2E-3 y `probar_paquete.py` caso H) · servidor real sin verificar en vivo |
| Capa de canales: conector Gmail u Outlook | pm-integraciones | pm-control | SMTP o `.eml` | INT-01 (`correo`), STK-07 | `preparar-mcp` y `registrar --modo mcp` probados con scripts · conector real sin verificar en vivo |
| Capa de canales: webhook de Teams (Workflows) | pm-integraciones | pm-control | conector MCP de Teams o correo | STK-07 | probado con scripts contra un receptor local (formato de la tarjeta según la documentación de Microsoft) · flujo real sin verificar en vivo |
| Capa de canales: webhook de Slack | pm-integraciones | pm-control | conector MCP de Slack, correo o `.eml` | STK-07 | probado con scripts contra un receptor local · webhook real sin verificar en vivo |
| Capa de canales: `.eml` | pm-integraciones | pm-control | — (es el respaldo) | STK-07 (pendiente hasta `registrar`) | probado con scripts |
| BMAD 6.12.4 / v4 | pm-bmad-puente | pm-planificacion · pm-control · pm-director | `requisitos.md`, `backlog.csv`, `wbs.csv` | ESP-01…15, hook | probado con scripts sobre artefactos reales de BMAD 6.12.4 (fixture) y en `probar_paquete.py` |

Controles transversales: el hook `guardian.py` (PreToolUse) bloquea ediciones directas de `estado.json`, registros CSV,
derivados de la especificación y `00-direccion/historial/`, las escrituras de subagentes pm-* en BMAD y los
subcomandos de `estado.py` reservados a pm-director; `sanidad.py` no bloquea puertas con INS o INT, pero los informa;
`pm-puerta` no deja pasar un ERROR sin decisión humana registrada.
