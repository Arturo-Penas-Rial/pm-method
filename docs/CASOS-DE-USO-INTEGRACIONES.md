# Casos de uso de integraciones · pm-method 2.1.0

Casos trabajados para cada repositorio o integración externa que pm-method incorpora, con más detalle en diseño visual,
informes, planificación y OKR. Cada caso dice en qué momento del ciclo PRINCE2 se usa, qué skill y qué agente son
dueños, qué herramienta externa interviene, cuál es el respaldo interno cuando no está instalada, qué comandos se
ejecutan, qué queda en la carpeta del proyecto, qué controles aplican y qué límites tiene.

EN: worked examples for every external repository and integration (visual design, reports, planning, OKR, meetings,
trackers and BMAD), with the PRINCE2 moment, owner skill and agent, fallback, real commands, outputs, controls and limits.

Regla de evidencia de este documento. Las salidas de scripts que se muestran son reales y están recortadas: se
obtuvieron el 2026-10-17 corriendo los scripts del paquete sobre un proyecto temporal (ver "Proyecto de prueba"). Lo
que se dice de las skills externas en sesiones de Claude Code sale de `docs/INTEGRACIONES.md` §3.1 y de los registros
de esas sesiones (A0–G1). Lo que no se pudo verificar se marca **[sin verificar en vivo]**. Los nombres de personas y
la cooperativa son ficticios, igual que en `CASOS-DE-USO.md`.

Estados de verificación usados en todo el documento:
- **verificado en vivo**: una sesión real de Claude Code con el plugin invocó la integración y produjo la salida.
- **probado con scripts**: se corrieron los scripts (del paquete o del repositorio externo) y se revisó la salida, sin
  una sesión de Claude Code que decida la delegación.
- **documentado sin prueba en vivo**: el contrato está escrito en el paquete, pero no hubo herramienta conectada.

## Índice

1. [Diseño visual](#caso-1--diseño-visual-pm-visuales): archify, diagram-design, visual-explainer, tablero HTML, drawio-mcp, Mermaid
2. [Reportes](#caso-2--reportes-checkpoint-highlight-excepción-fin-de-etapa-y-exportación): checkpoint, highlight con EVM, excepción, fin de etapa, exportación Office
3. [Planificación](#caso-3--planificación-wbs-camino-crítico-ms-project-presupuesto-y-release-plan): WBS, camino crítico, MS Project (MSPDI), presupuesto, release plan
4. [OKR](#caso-4--okr-ligados-a-beneficios-con-tability-opcional): `okr.py`, vínculo con beneficios y métricas, Tability
5. [Transcripciones y reuniones](#caso-5--transcripciones-y-actas-de-reunión): `transcripcion.py`, Granola, Fireflies, Zoom, minutes
6. [Trackers y canales](#caso-6--trackers-documentación-y-canales-jira-confluence-slack-teams): Jira, Confluence, Slack, Teams
7. [BMAD](#caso-7--bmad-como-capa-de-especificación-pm-bmad-puente): `bmad.py` sobre el fixture real 6.12.4
8. [Matriz de cierre](#matriz-de-cierre)

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
| 4 | Tability MCP | MCP | pm-okr (vía pm-integraciones) |
| 5 | Granola, Fireflies, Zoom, minutes (`minutes-mcp`) | MCP | pm-reuniones (vía pm-integraciones) |
| 6 | Atlassian Rovo MCP (Jira, Confluence), Slack MCP, Teams/Work IQ | MCP | pm-integraciones |
| 7 | BMAD Method (`bmad-method` 6.12.4 y v4) | marco, solo lectura | pm-bmad-puente |

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

Declarar el motor (uno o una lista por prioridad) y comprobar la instalación:

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

- **Objetivo:** organigrama y WBS en HTML interactivo validado por el propio motor, con los ids de la WBS en cada nodo.
- **Momento PRINCE2:** organigrama en SU (pm-organizacion-roles lo pide para `autorizar-inicio`); WBS en IP, como parte del plan que la junta aprueba en `autorizar-proyecto`. Decide la ejecutiva; el visual no se aprueba por separado.
- **Dueña y agente:** `pm-visuales`; la invoca el orquestador directamente o `pm-inicio` / `pm-planificacion` (paso 10 de su bucle). El contenido de la WBS es de `pm-planificacion-por-productos`.
- **Externa:** archify 3.1 (`tt-a1i/archify`, MIT). Tipos útiles: `tree` (organigrama, WBS), `workflow`, `timeline`. Instalación (INSTALACION §6.1): `npx skills add tt-a1i/archify -a claude-code -s archify -y`. Requiere Node ≥ 18 y Chrome/Chromium (o `ARCHIFY_CHROME=<ejecutable>`).
- **Respaldo:** `wbs.py --mermaid` para la WBS y `templates/diagramas-mermaid.md` §1 para el organigrama.
- **Frase:** "Hacé el organigrama del proyecto y el diagrama de la WBS" (la usada en la sesión en vivo). EN: "Draw the project org chart and the WBS diagram."
- **Pasos:**
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
- **Resultado:** `02-planificacion/visuales/wbs.html` (830.803 bytes, 16 nodos), `wbs.md` (Mermaid de respaldo) y, al lado, `wbs.candidate.json`, `wbs.finalize.json`, `wbs.finalize-summary.json`, `wbs.delivery.json`, `wbs.browser-check.json`. En la sesión en vivo (A1) los cuatro gates quedaron en `pass` y se generaron `organigrama.html` y `wbs.html` con sus `.md`.
- **Controles:** INS-03 (instalada / Chrome); guía §1.4: éxito = `"ok": true` con los cuatro gates en `pass`; con solo `browser-check` en `skipped` por falta de Chrome, vale como "verificado sin navegador" y se dice. `estado.py artefacto` registra el visual como borrador.
- **Límites:** el árbol `tree` es de un solo padre: aseguramiento y soporte se cuelgan de la junta o del gestor y se aclara en el pie (lo señaló la sesión A1). archify no cubre mapa poder/interés ni one-pager. Antes de los ajustes del contrato (sesión A0) se usó el binario de archify sin invocar la skill: la regla actual es invocarla siempre.

### 1.2 diagram-design: organigrama, flujo de excepciones y roadmap editoriales

- **Objetivo:** diagramas editoriales HTML/SVG (organigrama, mapa poder/interés tipo `quadrant`, flujo de excepciones tipo `swimlane`, roadmap por etapas tipo `timeline`) para la junta o el cliente.
- **Momento PRINCE2:** organigrama en SU; flujo de excepciones en IP (enfoque de control del PID); roadmap en SU/IP con las puertas como hitos y actualizado en cada SB. Decide quien aprueba la fuente (ejecutiva en las puertas).
- **Dueña y agente:** `pm-visuales`; desde `pm-inicio` o `pm-planificacion`.
- **Externa:** diagram-design 2.6 (`cathrynlavery/diagram-design`, MIT). Como plugin: `claude plugin marketplace add cathrynlavery/diagram-design` y `claude plugin install diagram-design@diagram-design` (con `--scope project` queda para todo el equipo); como skill copiada: `npx skills add cathrynlavery/diagram-design -a claude-code -s diagram-design -y`. Se invoca como `diagram-design:diagram-design` (plugin) o `diagram-design`.
- **Respaldo:** Mermaid de `templates/diagramas-mermaid.md` (§1 organigrama, §6 roadmap, §7 flujo de excepciones).
- **Frase:** "Hacé el organigrama del proyecto" (sesión en vivo B2). EN: "Build a stage roadmap with the gates as milestones." (ejemplo de la propia skill).
- **Pasos:** respaldo Mermaid; para la WBS u otro Mermaid, la vía de importación del motor y luego su chequeo:
  ```bash
  python3 <diagram-design>/scripts/mermaid_extract.py 02-planificacion/visuales/wbs.md
  python3 <diagram-design>/scripts/self_check.py 02-planificacion/visuales/<nombre>.html     # debe imprimir OK
  ```
  Salida real de `mermaid_extract.py` sobre la WBS del proyecto de prueba:
  ```text
  1 diagram(s): [0] flowchart (16n/15e)
  - budget: nodes OVER (max 9), edges OVER (max 12)
  - type candidates: architecture
  ```
- **Resultado:** `02-planificacion/visuales/organigrama.html` (o `roadmap.html`, `flujo-excepciones.html`) junto a su `.md`. En vivo: B1 (`--plugin-dir` con el clon) generó `organigrama.html` y `wbs.html`, con `self_check.py` → `OK …/organigrama.html` y `OK …/wbs.html`; B2 (plugin instalado) generó el organigrama con `OK organigrama.html` y nota en `diario.md`.
- **Controles:** INS-03 (no ve un plugin cargado solo con `--plugin-dir`: ahí emite AVISO y hay que ignorarlo); `self_check.py` = OK; regla de método: tres intereses en la junta y aseguramiento separado (la sesión B2 lo verificó y marcó `[por confirmar]` los roles vacíos).
- **Límites:** la primera vez pide elegir estilo; sin usuario (subagente o `claude -p`) usa el estilo por defecto y lo anota. Su tope sugerido es de 9 nodos: con la regla `faithful` se conservan todos (la WBS de 11 nodos de B1 se mantuvo completa). Carga tipografías de Google Fonts; sin red, pedir fuentes del sistema. El roadmap y el flujo de excepciones con este motor **[sin verificar en vivo]**: solo se probaron organigrama y WBS. Un flujo de control de cambios distinto del de excepciones no figura como visual del catálogo; se dibujaría como `flowchart` **[sin verificar en vivo]**.

### 1.3 visual-explainer: one-pager del brief (o de los OKR)

- **Objetivo:** una página HTML que explica el brief, un resumen de etapa o los OKR a la junta o al patrocinador.
- **Momento PRINCE2:** SU (one-pager del project brief antes de `autorizar-inicio`) o SB (resumen para la puerta de etapa). Decide la ejecutiva sobre la fuente; el one-pager es solo lectura.
- **Dueña y agente:** `pm-visuales`; desde `pm-inicio` (brief) o el orquestador.
- **Externa:** visual-explainer 0.12 (`nicobailon/visual-explainer`, MIT). Plugin: `claude plugin marketplace add nicobailon/visual-explainer` y `claude plugin install visual-explainer@visual-explainer-marketplace`; skill copiada: `npx skills add nicobailon/visual-explainer -a claude-code -s visual-explainer -y`. Node ≥ 18; `playwright-core` opcional.
- **Respaldo:** `templates/canvas-arranque.html`.
- **Frase:** "Hacé un one-pager visual del brief" (sesiones C2 y C3). EN: "Make a one-page visual summary of the project brief."
- **Pasos:** pm-visuales escribe la fuente `<nombre>.src.html` (con `data-register` y `<link rel="stylesheet" href="kit.css" data-ve-kit>`) y la renderiza **sin `--open`**. Prueba real con un one-pager de los OKR del caso 4:
  ```bash
  cd gestion/02-planificacion/visuales
  node ../../../.claude/skills/visual-explainer/kit/render.mjs one-pager-okr.src.html
  ```
  ```text
  ✓ <repo>/gestion/02-planificacion/visuales/one-pager-okr.html  kit inlined
    Page: 0 figures · 40 prose words outside figures
  ```
- **Resultado:** `02-planificacion/visuales/one-pager-<fuente>.html` + `.src.html`; registro `estado.py artefacto one-pager-<fuente> … --estado borrador`. En vivo, C2 y C3 dejaron `one-pager-project-brief.src.html` y `.html` en esa carpeta y nada en `~/.agent/diagrams/` (la ruta por defecto del motor, que el contrato prohíbe).
- **Controles:** INS-03; el render debe imprimir `✓`; `kit/check.mjs` solo con `playwright-core` (C3 no pudo correrlo y lo dijo). Las sesiones detectaron y reportaron incoherencias de la fuente (versión del brief en `estado.json` distinta de la del archivo) sin corregirlas.
- **Límites:** en una corrida (C1) la petición la tomó otra skill del entorno (`artifact-design`) y el archivo quedó fuera del proyecto; si el entorno tiene skills de diseño propias, pedirlo nombrando pm-visuales o pasar por el orquestador. visual-explainer no hace árboles ni organigramas (guía §1.2).

### 1.4 Tablero de avance con vista por actor (interno)

- **Objetivo:** HTML autocontenido con semáforo contra tolerancias, riesgos (mapa de calor P×I), acciones por actor y sección ágil; cada persona recibe su enlace filtrado `?actor=<Nombre>`.
- **Momento PRINCE2:** CS, en cada período de informe, junto al highlight. Lo confirma el gestor antes de compartirlo.
- **Dueña y agente:** `pm-visuales`, invocada por `pm-control` (paso 10 de su bucle).
- **Externa:** ninguna; puede tomar instantáneas de tracker de `03-control/fuentes/` (caso 6).
- **Frase:** "Mostrame un tablero con las acciones de cada persona" (frase #8 del conjunto de enrutamiento). EN: "Build this week's progress dashboard with a view per person."
- **Pasos:** se arma el bloque JSON `datos-tablero` con el script de la guía §3 (registros con `registro.py … --json`, `evm.py --json`, `avance-bmad.csv`) y se reemplaza en `templates/tablero-avance.html`. En la prueba: `riesgos` R-001 (16, alto) y R-002 (6, medio), acciones A-001 (vencida al corte) y A-002, issue I-001, objetivos tiempo y costo en `rojo` desde `evm.py --proyecto`.
  ```bash
  python3 $E/estado.py --proyecto gestion artefacto tablero-avance --ruta 03-control/reportes/2026-12-18-tablero-avance.html --estado borrador
  ```
- **Resultado:** `03-control/reportes/2026-12-18-tablero-avance.html` (35 KB, sin red). `paquete.py listar puerta autorizar-etapa` lo incluye como opcional.
- **Controles:** rojo sin issue o excepción → no se publica (regla 2 de pm-visuales); acciones desde `acciones.csv`, nunca desde `issues.csv`; publicación solo vía pm-integraciones con confirmación.
- **Límites:** la inyección del JSON se verificó; la vista por actor en navegador **[sin verificar en vivo]** (no había navegador en el entorno). El valor de `?actor=` debe coincidir exactamente con el del registro.

### 1.5 drawio-mcp: diagramas editables

- **Objetivo:** que el usuario pueda editar el organigrama o la WBS en draw.io.
- **Momento, dueña, agente:** igual que 1.1; capacidad `diagramas=drawio`, dueña `pm-visuales` (conexión vía `pm-integraciones`).
- **Externa:** drawio-mcp oficial, conectado con la gestión de conectores del cliente (`claude mcp add …`); herramientas con prefijo `mcp__drawio…` (guía §1.1). El paquete no trae `.mcp.json` ni credenciales.
- **Respaldo:** Mermaid.
- **Frase:** "Pasame el organigrama a draw.io para editarlo." EN: "Give me the org chart as an editable draw.io file."
- **Pasos:** tabla intermedia (nodo, padre, etiqueta) → herramienta del servidor → `.drawio` + PNG/SVG junto al `.md` (guía §1.4).
- **Resultado esperado:** `02-planificacion/visuales/organigrama.drawio` y su imagen **[sin verificar en vivo]**.
- **Controles:** INT-01 acepta `drawio` como valor conocido de `diagramas`; INS-03 **no** comprueba drawio (solo skills externas), así que si el servidor no está la sesión debe caer al Mermaid y anotarlo.
- **Límites:** documentado sin prueba en vivo; no se conocen ni se citan nombres de herramientas concretos del servidor.

### 1.6 Respaldo Mermaid (sin ninguna skill externa)

- **Objetivo:** que el flujo funcione igual sin nada instalado.
- **Pasos:** `wbs.py --mermaid` (WBS), `cpm.py --mermaid` (Gantt), plantillas Mermaid para organigrama, roadmap y flujos; `templates/canvas-arranque.html` para el one-pager.
- **Resultado:** `02-planificacion/visuales/wbs.md`, `organigrama.md`, `02-planificacion/gantt.md` (ejemplo real en `docs/ejemplos/integraciones/gantt-cpm.md`).
- **Evidencia en vivo:** con `HOME` aislado y `diagramas=archify` declarado pero no instalado (E1), pm-visuales entregó `organigrama.md` y `wbs.md` y anotó en `diario.md` que archify no estaba; con `visual-explainer` no instalado (G1), usó la plantilla interna y lo anotó.
- **Límites:** con `mmdc` instalado, `exportar.py docx` inserta el Mermaid como imagen; sin él queda como código con aviso.

---

## Caso 2 · Reportes: checkpoint, highlight, excepción, fin de etapa y exportación

El contenido de los informes es de `pm-progreso-reportes` (checkpoint, highlight), `pm-issues-cambios` (informe de
excepción) y `pm-plan-etapa-y-limites` (informe de fin de etapa); los formatos Office son de `pm-exportar`. Ningún
script redacta el informe: los scripts dan las cifras y la skill completa la plantilla.

### 2.1 Checkpoint y highlight con EVM

- **Objetivo:** informe quincenal a la junta con semáforo contra tolerancias de etapa y proyecto.
- **Momento PRINCE2:** CS (checkpoint del equipo al gestor en MP; highlight del gestor a la junta). Aseguramiento revisa; la aprobación del highlight la registra `pm-director` con la confirmación del gestor.
- **Dueña y agente:** `pm-progreso-reportes`, desde `pm-control`; comando `/pm-method:pm-reporte highlight|checkpoint|excepcion`.
- **Frase:** "Armá el highlight de la quincena con el EVM." EN: "Write this fortnight's highlight report with earned value."
- **Pasos reales** (corte 2026-12-18, BAC de la etapa 68.000 = Σ PV de `linea-base-costo.csv`):
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
- **Resultado:** `03-control/reportes/2026-12-18-highlight-report.md` desde `templates/highlight-report.md`, registrado con `estado.py artefacto highlight-2026-12-18 --estado borrador`; checkpoint en `templates/checkpoint-report.md`.
- **Controles:** conteos idénticos a `registro.py resumen`; ningún verde con un pronóstico en rojo; sanidad EST-06/07 exige tolerancias de tiempo y costo.
- **Límites:** desde v2.1 `VAC_pct` tiene el signo de VAC y el desvío previsto contra BAC va en `sobrecosto_pct`; `base_semaforo` declara la base de cada semáforo (`costo:tolerancia;cronograma:indice-0.95-0.85` si solo se pasa `--tol-costo`). Una tolerancia en semanas ("±2 semanas") no la lee `--proyecto`: el script avisa y hay que convertirla y pasarla con `--tol-plazo`. (Salida del bloque re-ejecutada con v2.1.)

### 2.2 Informe de excepción

- **Objetivo:** escalar a la junta un pronóstico fuera de tolerancia de etapa, con opciones.
- **Momento PRINCE2:** CS → DP. El gestor lo emite; la junta decide (pedir plan de excepción, aceptar, cerrar). `estado.py limite-etapa --excepcion` y la puerta `autorizar-plan-excepcion` son exclusivos de `pm-director`.
- **Dueña y agente:** `pm-issues-cambios` (plantilla única `templates/informe-excepcion.md`, también la usa pm-progreso-reportes cuando `evm.py` marca `excepcion_prevista`); `pm-control` la prepara y `pm-director` registra.
- **Frase:** "Con estos números nos vamos de la tolerancia de costo: prepará el informe de excepción." EN: "Prepare the exception report for the cost overrun."
- **Pasos reales** (en una copia del proyecto, como lo haría pm-director tras la decisión de la junta):
  ```bash
  python3 $E/estado.py --proyecto gestion limite-etapa --excepcion I-001
  python3 $E/sanidad.py --proyecto gestion --rapido
  ```
  ```text
  Fase: entrega · Proceso: SB · Etapa 2: Release 1 · Enfoque: hibrido
  Límite de etapa por excepción I-001: plan de excepción (reemplaza el plan vigente), actualizar plan de proyecto, business case y riesgos. Puerta: autorizar-plan-excepcion (pm-director).
  AVISO EST-14 Excepción abierta I-001 esperando plan de excepción.
  ```
- **Resultado:** informe con clave `informe-excepcion-X-###` en `estado.json`, referenciado desde `issues.csv.notas` y `decisiones.csv`.
- **Controles:** hook: un subagente pm-* que intente `estado.py puerta …` recibe "ese comando de estado.py está reservado a pm-director"; sanidad EST-14 hasta que se apruebe el plan de excepción.
- **Límites:** el informe lo redacta la skill sobre la plantilla; el script no lo genera.

### 2.3 Informe de fin de etapa

- **Objetivo:** cierre de la etapa con EVM, productos, lecciones y pronóstico, para la puerta `autorizar-etapa` siguiente.
- **Momento PRINCE2:** SB; decide la junta. Dueña `pm-plan-etapa-y-limites` (plantilla `informe-fin-etapa.md`, que pide costo desde `presupuesto.md · evm.py`), desde `pm-planificacion` + `pm-control`.
- **Frase:** "Cerremos la etapa 2: informe de fin de etapa y plan de la 3." EN: "Prepare the end stage report and the next stage plan."
- **Pasos reales:**
  ```bash
  python3 $E/estado.py --proyecto gestion limite-etapa
  python3 $X --proyecto gestion listar puerta autorizar-etapa
  ```
  ```text
  Límite de etapa (SB): informe de fin de etapa, plan de la siguiente etapa, actualizar plan de proyecto, business case, riesgos y lecciones. …
  **ESTADO DEL PAQUETE / PACKAGE STATUS:** BORRADOR / DRAFT — faltan: informe-fin-etapa-2, plan-etapa-3, business-case, plan-proyecto
  ```
- **Resultado:** `informe-fin-etapa-2` y `plan-etapa-3` registrados en `estado.json`; con ellos, el paquete deja de salir BORRADOR.
- **Controles:** faltante o borrador obligatorio → ZIP `-BORRADOR`; `pm-director` corre `bmad.py verificar` antes de la puerta (caso 7).

### 2.4 Exportación con las skills oficiales de Office (y respaldo `exportar.py`)

- **Objetivo:** entregar a la junta Word, Excel o PowerPoint con marca BORRADOR cuando la fuente no está aprobada.
- **Momento PRINCE2:** DP/SB (paquete de puerta) o CS (highlight). El usuario confirma antes de enviar; el envío es de `pm-comunicacion-stakeholders`.
- **Dueña y agente:** `pm-exportar`, desde el orquestador o `pm-director` (preparación de puerta).
- **Externa:** `anthropics/skills` (`docx`, `xlsx`, `pptx`; licencia propietaria). Plugin: `claude plugin marketplace add anthropics/skills` y `claude plugin install document-skills@anthropic-agent-skills`; copia: `npx skills add anthropics/skills -a claude-code -s docx xlsx pptx -y`. Se aceptan los nombres `docx`, `document-skills:docx` y `anthropic-skills:docx` (igual para xlsx y pptx). Se activa con `integracion export=skills-office`.
- **Respaldo:** `export=scripts`: `exportar.py` (docx desde Markdown; xlsx solo desde CSV), `paquete.py` (ZIP); sin `pptx`, guion `exportados/<nombre>-deck.md`.
- **Frases:** "Exportá el presupuesto a Excel y el highlight a Word"; "Exportá el highlight a PowerPoint" (sesiones D1, D2). EN: "Export the highlight report to Word and the budget to Excel."
- **Evidencia en vivo:** D1 invocó `xlsx` y `docx`: Excel con hojas Resumen, Por etapa, Línea base PV y Notas, fórmulas recalculadas sin errores; Word con encabezado BORRADOR. D2 siguió la skill `pptx` leyendo su `SKILL.md` (pptxgenjs, 5 diapositivas con BORRADOR). Todo en `exportados/`.
- **Pasos reales del respaldo:**
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
- **Resultado:** `exportados/AAAA-MM-DD-<tipo>-v<n>[-BORRADOR].<ext>`; nunca fuente de verdad.
- **Controles:** INS-03 informa con qué nombre invocar cada skill (en este entorno: `anthropic-skills:docx`, `:xlsx`, `:pptx`, sincronizadas de claude.ai); INS-01 si faltan `python-docx` u `openpyxl`; nota en `diario.md` cuando se usa el respaldo (F2 la dejó; F1 no, y lo ofreció como pendiente).
- **Límites:** `exportar.py xlsx` solo convierte CSV; el presupuesto en Markdown se exporta desde `linea-base-costo.csv`, sin las tablas de `presupuesto.md` (lo informaron F1 y F2). Si se le pasa un `.md`, desde v2.1 el script lo rechaza con un mensaje (antes creaba una hoja con el texto crudo). La hoja `stakeholders` va siempre en el libro de registros: quitarla si la audiencia es externa.

---

## Caso 3 · Planificación: WBS, camino crítico, MS Project, presupuesto y release plan

Todo en IP (plan de proyecto y plan de la primera etapa de entrega) y en cada SB; se aprueba con el plan en
`autorizar-proyecto` y `autorizar-etapa` (decide la junta; registra pm-director). Agente: `pm-planificacion`.

### 3.1 WBS con `wbs.py`

- **Dueña:** `pm-planificacion-por-productos` (contenido); `pm-visuales` solo dibuja (caso 1.1).
- **Frase:** "Armá la WBS con responsables y citá los FR del PRD." EN: "Build the WBS with owners and cite the PRD requirement ids."
- **Pasos reales** (`wbs.csv` con 6 productos, 8 paquetes y 1 hito; `ref` con FR del PRD real):
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
- **Controles:** sanidad ESP-04 si un `ref` de la WBS no existe en la especificación; `bmad.py trazabilidad --wbs` informó "Referencias de la WBS a ids inexistentes: ninguna".

### 3.2 Camino crítico y exportación a MS Project (MSPDI)

- **Dueña:** `pm-cronograma-estimacion`; capacidad `cronograma=cpm|mspdi`.
- **Externa:** ninguna obligatoria. MSPDI es XML abierto generado por `cpm.py`; MPXJ (PyPI `mpxj`, LGPL, Java) es opcional para validar o convertir a `.mpp`. utf8proj fue **descartado** (INTEGRACIONES §2).
- **Frase:** "Calculá el camino crítico y exportalo para abrirlo en MS Project." EN: "Compute the critical path and export it for MS Project."
- **Pasos reales:**
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
- **Resultado:** `02-planificacion/cronograma.xml` (copia en `exportados/` cuando se entrega), `gantt.md`; ejemplos reales en `docs/ejemplos/integraciones/`.
- **Límites:** solo fin-a-comienzo, calendario L–V 8 h sin feriados (el 25/12 y el 1/1 cuentan como laborables) y sin nivelación. El paquete 1.1 de la WBS no tiene actividad, así que no aparece en el MSPDI. Observado en la prueba con v2.0 y corregido en v2.1: una tarea resumen que solo contiene un hito salía con `Finish` anterior a `Start` (ahora `Finish` = `Start`; prueba de regresión en `probar_paquete.py`, caso F). El título del Gantt Mermaid toma `--titulo`.

### 3.3 Presupuesto y costeo

- **Dueña:** `pm-costos-presupuesto` (plantillas `presupuesto.md`, `hoja-costeo.md`, `linea-base-costo.csv`).
- **Frase:** "Costeá los paquetes y calculá la contingencia desde los riesgos, sin duplicarla." EN: "Cost the work packages and derive contingency from the risk register."
- **Pasos reales:** `wbs.py … --json` → `total_costo: 124000.0`; `registro.py listar riesgos --abiertos --json` → R-001 `valor_esperado` 8400 (impacto 12.000), R-002 sin monto. Base 124.000 + contingencia 8.400 = BAC 132.400 (cálculo de la skill, no de un script); la reserva de gestión va fuera del BAC y la aprueba la junta. PV por período en `linea-base-costo.csv` (etapa 2: 68.000).
- **Controles:** total de `wbs.py` = hoja de costeo; Σ PV = BAC; contingencia una sola vez.
- **Límites:** no hay script de presupuesto: la consolidación es de `wbs.py` y el EMV de `registro.py`. Excel con fórmulas solo con la skill `xlsx` (caso 2.4).

### 3.4 Release plan ágil dentro de la etapa

- **Dueña:** `pm-agil-hibrido` (plantilla `release-plan.md`); con BMAD, el backlog lo sincroniza `pm-bmad-puente` (caso 7).
- **Frase:** "Armá el release plan del R1 con MoSCoW y DoD." EN: "Draft the release 1 plan with MoSCoW and definition of done."
- **Pasos reales:** `bmad.py backlog` (10 historias) → la PO completa las columnas de gobierno (Must 8 + 3 + 8 = 19 puntos, Should 5) → `bmad.py backlog` las conserva → `bmad.py handoff` (4 prioridades para el equipo BMAD). Capacidad: Must + Should = 24 ≤ velocidad 30 × 2 iteraciones. EVM en modo ágil:
  ```text
  $ python3 $E/evm.py --pv 45000 --ev 39000 --ac 43500 --bac 68000 --modo agil --pct-no-must 30 --proyecto gestion
  semaforo_cronograma    n/a-agil
  semaforo_costo         n/a-agil
  alcance_no_entregable_pct 10.345
  semaforo_alcance       verde
  excepcion_prevista     False
  ```
- **Límites:** en modo ágil, EAC > BAC se lee como alcance que no entra; hay excepción solo si peligran los Must.

---

## Caso 4 · OKR ligados a beneficios, con Tability opcional

- **Objetivo:** OKR de la capa de negocio vinculados a objetivos (OBJ-n), beneficios del business case (B-nn) o métricas de éxito del PRD (SM-n), sin duplicar sus datos.
- **Momento PRINCE2:** SU/IP (redacción), SB (revisión en cada límite de etapa), CP y revisiones de beneficios posteriores. Acepta la ejecutiva (o el usuario sénior dueño del beneficio); `pm-director` ejecuta `estado.py aprobar okr --por "<rol: nombre>"`.
- **Dueña y agente:** `pm-okr` (metadato `agente: pm-director`); la usan `pm-inicio` (redacción), `pm-director` y `pm-cierre` (puntuación), `pm-planificacion` (solo lectura en SB).
- **Externa:** Tability MCP, opcional (`integracion okr=tability`): lectura a instantánea; escritura solo con vista previa y confirmación. Operately y okr-writer no se incorporaron.
- **Respaldo:** `okr=archivo`: `00-direccion/okr.csv` mantenido con `okr.py`.
- **Frases:** "Definamos los OKR del proyecto para el próximo semestre" (#12) y "Score our key results for Q4" (#46). Tability: "Pull progress from Tability and update the OKR table for the board."
- **Pasos reales:**
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
  `clave,tipo,titulo,actual,meta,actualizado,url` y pm-okr actualiza la columna `actual` (conciliando por título o por
  `notas=tability:<clave>`); `/pm-method:pm-sync okr` repite la lectura. **[sin verificar en vivo]**: no hubo servidor
  Tability; en la prueba solo se creó la instantánea a mano para verificar su nombre.
- **Resultado:** `00-direccion/okr.csv`, `00-direccion/okr.md` (narrativa), `03-control/reportes/<fecha>-okr.md` (ejemplo en `docs/ejemplos/integraciones/okr-puntuado.md`); visual opcional con visual-explainer (caso 1.3).
- **Controles:** la sanidad valida la existencia del vínculo: con un KR que cita `SM-99` salió `ERROR ESP-04 okr KR-1.4 cita SM-99, que no existe en la especificación vigente (bmad)`; un `B-n` ausente del business case da `AVISO ESP-05`. Un KR rojo que amenaza un beneficio pasa a riesgo o issue y, fuera de la tolerancia de beneficios, a excepción.
- **Límites:** los umbrales 0,7/0,4 son convención OKR, no PRINCE2 ni PMBOK; se declaran en el informe. `okr.py` solo comprueba el formato del vínculo, no su existencia (eso lo hace `sanidad.py`); desde v2.1 acepta `SM-C1` (métricas de contrapeso del PRD 6.12.4). Escritura en Tability nunca sin confirmación.

---

## Caso 5 · Transcripciones y actas de reunión

- **Objetivo:** acta con decisiones, acciones A-###, riesgos e issues propuestos a partir de una transcripción.
- **Momento PRINCE2:** CS/MP (checkpoints, dailies, reuniones con el cliente), DP (actas de junta, que firma pm-director), SB y CP (talleres). Quien presidió confirma el acta; nada entra a los registros antes.
- **Dueña y agente:** `pm-reuniones`, desde `pm-control` (o `pm-cierre` en CP).
- **Externa:** fuentes vía `pm-integraciones`, capacidad `reuniones` (indicios `granola`, `fireflies`, `zoom`, `minutes`, `teams`): listar reuniones de un rango, confirmar cuál y traer la transcripción completa, no solo el resumen automático. La obtención de transcripciones por Zoom MCP **no está confirmada**. minutes es MIT (`minutes-mcp`). meeting-analyzer no se incorporó.
- **Respaldo:** archivo `.vtt`, `.srt`, `.txt` ("Nombre: texto" o con marcas `[hh:mm:ss]`), `.docx` (requiere `python-docx`) o texto pegado, guardado primero como `<fecha>-<reunion>-original.txt`.
- **Frases:** "Procesá la transcripción del comité de ayer y sacá las acciones" (#13); "Turn this meeting transcript into minutes and action items: …" (#44).
- **Pasos reales:**
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
- **Resultado:** `03-control/reuniones/<fecha>-<reunion>-transcripcion.md` (ejemplo en `docs/ejemplos/integraciones/transcripcion-checkpoint.md`), `<fecha>-acta-<reunion>.md`; con herramienta conectada, instantánea `03-control/fuentes/<sistema>-AAAA-MM-DD.md` con front matter `fuente`, `fecha`, `consulta`.
- **Controles:** hook: `riesgos.csv` o `acciones.csv` editados a mano se bloquean ("se modifica con registro.py"); INT-01 valida el valor de `reuniones`. Registrar el acta solo después de escribirla: en la prueba se registró antes y la sanidad respondió `ERROR ART-01 Artefacto acta-reunion-2026-12-03 registrado pero no existe`.
- **Límites:** el script cuenta, no interpreta: no infiere emociones. El clima de equipo solo con consentimiento, `--anonimizar` y agregado. Una línea sin "Nombre:" que sigue a otra con hablante se agrega al turno anterior (no queda como `?`): revisar continuaciones mal atribuidas. Granola, Fireflies, Zoom y minutes: **documentado sin prueba en vivo**.

---

## Caso 6 · Trackers, documentación y canales (Jira, Confluence, Slack, Teams)

- **Objetivo:** leer el estado real del equipo en su tracker y publicar comunicaciones en sus canales, sin que el tracker reemplace a los registros de gobierno.
- **Momento PRINCE2:** CS/MP en cada período (`/pm-method:pm-sync tracker`); IP para registrar capacidades (`pm-inicio`, paso 15). El gestor confirma cada lote de escrituras externas.
- **Dueña y agente:** `pm-integraciones`, desde `pm-control` (paso 2 del bucle) o `pm-inicio`.
- **Externa:** capacidades genéricas, **sin conector predefinido** ni `.mcp.json` en el paquete. Notas relevadas al 2026-10-17 (INTEGRACIONES §2): Atlassian Rovo MCP Server requiere obtener el `cloudId` con `getAccessibleAtlassianResources` antes de herramientas como `searchJiraIssuesUsingJql` o `createJiraIssue`; el Slack MCP oficial (`https://mcp.slack.com/mcp`) está restringido a apps publicadas o internas; el servidor "Teams (preview)" de Microsoft figura como legado (se recomienda Work IQ). La skill siempre lee la descripción real de las herramientas presentes en la sesión.
- **Respaldo:** registros CSV (`backlog.csv`, `acciones.csv`), Markdown local y borradores de mensaje para copiar.
- **Frases:** "Traé los tickets abiertos de Jira del sprint actual" (#16); "Publicá el resumen semanal en el canal de Teams" (#17). EN: "Sync Jira and post the highlight to the project Slack channel."
- **Pasos:**
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
- **Resultado:** `03-control/fuentes/jira-2026-12-18.csv`, propuestas de cambio a registros y anotaciones de publicación en `diario.md`. El tablero (caso 1.4) cita la instantánea como fuente y usa su fecha de corte.
- **Controles:** INT-01…04; columnas de gobierno (`moscow`, `release`, `producto_pbs`, `prioridad`) solo de pm-method; en un subagente, toda escritura vuelve como "decisión humana requerida"; si una herramienta falla dos veces, alternativa local.
- **Límites:** **documentado sin prueba en vivo** (no hubo servidores conectados); la instantánea de la prueba se escribió a mano para verificar los controles. `estado.py integracion` guarda un valor desconocido pero avisa en el momento (y la sanidad lo marca, INT-01). Desde v2.1 el hook impide modificar una instantánea existente de `03-control/fuentes/` (se crea una nueva con fecha). INT-03 (más de 14 días) no avisa si la fecha del nombre es futura.

---

## Caso 7 · BMAD como capa de especificación (pm-bmad-puente)

- **Objetivo:** usar el PRD, la arquitectura, las épicas y el `sprint-status.yaml` de BMAD como especificación, sin escribir nunca en BMAD, y devolverle las decisiones de gobierno por traspaso.
- **Momento PRINCE2:** SU/IP (`detectar`, `inventario`, `requisitos`, `trazabilidad`, `backlog`), DP (`linea-base` tras `autorizar-proyecto`, por pm-director), CS (`backlog`, `avance`, `verificar` en cada período), SB (`verificar` antes de la puerta), cambios aprobados → `handoff`.
- **Dueña y agente:** `pm-bmad-puente` (metadato `agente: pm-planificacion`); también `pm-inicio`, `pm-control`, `pm-director` y `pm-cierre` en sus bucles. El resto de las skills lee solo por la fachada `especificacion.py` (contrato `pm-spec-index/1`).
- **Externa:** BMAD Method instalado por el equipo (`npx bmad-method@6.12.4 install …`, INSTALACION §4); versiones probadas 4.x, 6.11 y 6.12 (`compatibilidad.json`). Fixture real 6.12.4.
- **Respaldo:** `especificacion=ninguna`: `requisitos.md`, `backlog.csv` y `wbs.csv` con el mismo contrato.
- **Frases:** "Sincronizá el backlog con las historias de BMAD" (#14); "¿Qué requisitos del PRD no tienen historias?" (#15); "Did the PRD change since the board approved it?" (#45).
- **Pasos reales sobre el fixture:**
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
- **Resultado:** derivados en `02-planificacion/especificacion/` (`inventario-bmad.json`, `requisitos-bmad.csv`, `matriz-trazabilidad-bmad.csv`, `spec-index.json`, `handoff-bmad-<fecha>-<…>.md`), columnas derivadas de `backlog.csv`, `03-control/reportes/avance-bmad.csv`, línea base en `00-direccion/historial/bmad-prd-v1.0/`.
- **Controles:** hook: los derivados (`requisitos-bmad.csv`, `avance-bmad.csv`, …) no se editan ("es un derivado regenerable") y un subagente pm-* que escriba en `_bmad-output/` recibe "los agentes de gestión no escriben en carpetas de BMAD. Usar bmad.py handoff …"; el hilo principal sí puede (los flujos de BMAD escriben ahí). Sanidad ESP-01…15: `AVISO ESP-13 Traspaso a BMAD sin confirmar` hasta que el equipo BMAD marque `estado: aplicado`; ESP-10 si el PRD cambia sin solicitud de cambio (lo cubre `probar_paquete.py`, 80 OK en la corrida final).
- **Límites:** en el formato 6.12.4 las historias no citan el FR, así que la traza es por épica y la columna `refs` de cada historia trae todos los FR de su épica. Desde v2.1 la `descripcion` derivada del backlog es el primer párrafo completo de la historia ("As a socio, I want…, So that…"). `bmad-spec` (`specs/spec-<slug>/SPEC.md`) no se traza. Fuera del rango probado, modo degradado con aviso.

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
| Tability MCP | pm-okr (vía pm-integraciones) | pm-inicio · pm-director · pm-cierre | `okr.csv` con `okr.py` | INT-01 (`okr`), ESP-04/05 | `okr.py` probado con scripts · Tability documentado sin prueba en vivo |
| Granola / Fireflies / Zoom / minutes | pm-reuniones (vía pm-integraciones) | pm-control · pm-cierre | archivo VTT/SRT/TXT/DOCX o texto pegado | INT-01 (`reuniones`) | `transcripcion.py` probado con scripts · MCP documentado sin prueba en vivo (Zoom no confirmado) |
| Atlassian Rovo (Jira, Confluence) | pm-integraciones | pm-control · pm-inicio | CSV y Markdown locales | INT-01…04 | documentado sin prueba en vivo · controles INT probados con scripts |
| Slack MCP, Teams/Work IQ | pm-integraciones (y pm-comunicacion-stakeholders) | pm-control | borrador para copiar | INT-01 (`chat`) | documentado sin prueba en vivo |
| BMAD 6.12.4 / v4 | pm-bmad-puente | pm-planificacion · pm-control · pm-director | `requisitos.md`, `backlog.csv`, `wbs.csv` | ESP-01…15, hook | probado con scripts sobre artefactos reales de BMAD 6.12.4 (fixture) y en `probar_paquete.py` |

Controles transversales: el hook `guardian.py` (PreToolUse) bloquea ediciones directas de `estado.json`, registros CSV,
derivados de la especificación y `00-direccion/historial/`, las escrituras de subagentes pm-* en BMAD y los
subcomandos de `estado.py` reservados a pm-director; `sanidad.py` no bloquea puertas con INS o INT, pero los informa;
`pm-puerta` no deja pasar un ERROR sin decisión humana registrada.
