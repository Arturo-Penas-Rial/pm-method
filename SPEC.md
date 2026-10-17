# pm-method · Especificación de construcción (para autores de skills)

Paquete bilingüe (ES/EN) de agentes y skills que implementan un método de gestión de proyectos
consolidado a partir de tres fuentes destiladas (en palabras propias, sin texto literal):
- PRINCE2 7 → **la metodología y el ciclo de vida** (manda siempre): etapas de gestión, gestión por excepción,
  roles de la junta, procesos SU/DP/IP/CS/MP/SB/CP, prácticas y productos de gestión. Define QUÉ se hace,
  CUÁNDO y QUIÉN decide.
- PMBOK 8 → **solo el CÓMO**: técnicas y herramientas (EVM, CPM, PERT, estimación, análisis de stakeholders,
  adquisiciones, gestión de recursos…) y relleno de vacíos de PRINCE2. Nunca aporta ciclo de vida, fases ni
  grupos de procesos; todo lo que se toma del PMBOK se aplica dentro de una práctica, proceso o producto PRINCE2.
- Libro de plantillas (Snyder Dionisio) → biblioteca de artefactos concretos (campos y checklists).
- BMAD (opcional) → capa de especificación de producto (brief, PRD, arquitectura, épicas e historias), tratada
  como productos especialistas dentro de los paquetes de trabajo (ver 1.13).

## 0. Arquitectura en capas
| Capa | Dueño | Qué aporta | Dónde vive |
|---|---|---|---|
| Gobierno | PRINCE2 (agentes y skills pm-*) | justificación, organización, planes, etapas, tolerancias, puertas, cambios, informes | carpeta del proyecto (`estado.json`, Markdown, CSV) |
| Técnicas | PMBOK, aplicado dentro de PRINCE2 | cómo estimar, programar, costear, medir, analizar | procedimientos de las skills y `pm-knowledge` |
| Especificación (opcional) | BMAD | qué debe hacer el producto: brief de producto, PRD (FR/NFR/UJ/SM), arquitectura (AD), UX, épicas, historias, estado del sprint | carpetas de BMAD (`_bmad-output/` o `docs/`), solo lectura para pm-method |
| Integración (opcional) | MCP que el usuario conecte | fuentes y canales: Jira, Confluence, Slack, Teams, correo, calendario, transcripciones, OKR | herramientas de la sesión; instantáneas fechadas en la carpeta del proyecto |
| Persistencia | pm-estado-proyecto | fuente de verdad del gobierno | carpeta del proyecto; `exportados/` solo copias |

Conocimiento destilado: `skills/pm-knowledge/references/*.md` (8 archivos). Toda skill DEBE citar
qué archivos de referencia consulta (sección "Conocimiento") y leerlos cuando necesite detalle.

## 1. Convenciones obligatorias

### 1.1 Estructura de una skill
```
skills/<nombre>/
  SKILL.md                 # obligatorio
  references/*.md          # opcional: detalle adicional propio de la skill
  templates/*.md|*.csv     # plantillas de artefactos que la skill produce
  scripts/*.py             # opcional: utilidades deterministas (stdlib + openpyxl/python-docx si export)
```
### 1.2 Frontmatter de SKILL.md (formato Agent Skills, compatible Claude Code / Cowork / Hermes / Codex)
```yaml
---
name: pm-<kebab-case>            # ≤ 64 caracteres, único
description: "<≤ 240 caracteres en una línea. Ver 1.3>"
version: 1.0.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio|planificacion|control|cierre|direccion|transversal
    agente: pm-inicio|pm-planificacion|pm-control|pm-cierre|pm-director|pm-orquestador
    procesos_prince2: [SU, IP, DP, CS, MP, SB, CP]      # los que aplican
    practicas_prince2: [business-case, organizing, plans, quality, risk, issues, progress]   # las que implementa
    tecnicas_pmbok: [lista de técnicas PMBOK que aplica como "cómo"]                       # nunca grupos de procesos
    artefactos: [lista de artefactos que produce o actualiza]
    idiomas: [es, en]
---
```
### 1.3 Regla de disparadores (description) — precisión, scope clues y no colisión
La `description` decide la activación y ocupa presupuesto de contexto en TODAS las sesiones (el listado de
skills de Claude Code tiene un presupuesto de ≈1 % de la ventana de contexto). Formato obligatorio, una línea,
≤ 240 caracteres:
`<Objeto que produce o decide>. Usar: <4–7 disparadores ES/EN>. No: <tema vecino>→<skill dueña>.`
- Empezar por el objeto (sustantivo) que la skill produce; nada de procedimiento.
- "Usar:" disparadores concretos en español e inglés (sin sinónimos redundantes).
- "No:" la pista de alcance (scope clue) que evita la colisión más probable, apuntando a la skill dueña.
- Las skills de comando (1.15) llevan `disable-model-invocation: true` y no consumen presupuesto.
Ejemplo: `Business case y beneficios PRINCE2. Usar: caso de negocio, business case, ROI, VAN, payback, beneficios. No: OKR→pm-okr; costo del plan→pm-costos-presupuesto.`

### 1.4 Cuerpo de SKILL.md (orden fijo, encabezados exactos) y carga progresiva
Tres niveles de carga: (1) `name` + `description` siempre; (2) el cuerpo de SKILL.md solo al activarse;
(3) `references/`, `templates/` y `scripts/` solo cuando un paso lo pide. Límites del nivel 2: **≤ 12 000
caracteres y ≤ 200 líneas** (≈3,5 k tokens; Claude Code conserva hasta 5 k tokens por skill tras compactar).
El detalle (reglas extensas, ejemplos trabajados, tablas largas, variantes) va a `references/guia.md` de la
propia skill, citado por sección desde el paso que lo necesita. El conocimiento de las fuentes se consulta por
sección en `pm-knowledge/references/` (con `grep` del encabezado), nunca entero.
```
# <Nombre ES> · <Name EN>
## Cuándo usar / When to use        (viñetas ES; luego 2–4 viñetas EN)
## Idioma                            (regla: responder y generar artefactos en el idioma del usuario; etiquetas bilingües en plantillas)
## Conocimiento                      (archivos de references/ que consulta y para qué; secciones concretas)
## Entradas requeridas               (qué debe existir en la carpeta del proyecto; qué preguntar si falta)
## Procedimiento                     (pasos numerados; cada paso: acción, decisión, artefacto; incluir puertas de aprobación humana)
## Reglas del método                 (8–15 reglas clave; marcar [PRINCE2], [PMBOK→práctica], [Plantillas]; el resto en references/guia.md)
## Artefactos y plantillas           (tabla: artefacto · plantilla · ruta de salida en la carpeta del proyecto · estado en estado.json)
## Calidad                           (checklist de revisión antes de entregar)
## Escalamiento y excepciones        (cuándo derivar a pm-director u otro agente; qué registrar)
## Ejemplos de invocación            (2 ES + 2 EN, frases naturales; incluir 1 que NO debe activarla y a qué skill va)
## EN summary                        (3–6 líneas en inglés)
```
### 1.5 Carpeta del proyecto (fuente de verdad, Markdown + CSV)
```
<proyecto>/
  estado.json                      # ver 1.6
  00-direccion/                    # mandato, business case, PID, estructura y roles, tolerancias, enfoque de beneficios, okr.csv
    decisiones/                    # solicitudes de decisión, evaluaciones de excepción, actas de la junta
    historial/                     # versiones aprobadas congeladas (business-case-v1.0.md, pid-v1.0.md …)
  01-inicio/                       # propuesta, brief, canvas, visión, acta de constitución, análisis de stakeholders
  02-planificacion/                # plan de proyecto, planes de etapa y de excepción, PBS/WBS, estimaciones, cronograma, presupuesto, backlog, release plan
    enfoques/                      # enfoques de gestión y planes subsidiarios (PID)
    productos/                     # descripciones de producto
    adquisiciones/                 # estrategia, documentos de licitación, evaluación, contratos
    visuales/                      # diagramas y tableros de planificación
    especificacion/                # derivados del puente BMAD (inventario, requisitos, trazabilidad): no editar
  03-control/
    registros/                     # riesgos, issues, cambios, decisiones, supuestos, lecciones, stakeholders, calidad, acciones (.csv) + diario.md
    paquetes-trabajo/              # WP-###-<nombre>.md
    reportes/                      # checkpoint, highlight, excepción, fin de etapa, tablero, progreso.csv, avance-bmad.csv
    reuniones/                     # transcripciones normalizadas y actas
    fuentes/                       # instantáneas fechadas de sistemas externos (Jira, Slack, Teams…)
  04-cierre/                       # aceptación, handover, informe de fin de proyecto, lecciones, recomendaciones, plan de revisión de beneficios
  exportados/                      # .docx/.xlsx/.pptx/.zip generados bajo demanda (nunca fuente de verdad)
```
Nombres de archivo: `kebab-case`, prefijo numérico cuando hay secuencia (`2026-10-16-highlight-report.md`).
Encabezado de todo artefacto Markdown: frontmatter YAML con `tipo`, `proyecto`, `version`, `fecha`, `autor`, `estado` (borrador|en-revision|aprobado|obsoleto), `aprobado_por`, `idioma`.

### 1.6 estado.json (lo mantiene pm-estado-proyecto; lo leen todas las skills)
```json
{
  "proyecto": "nombre", "idioma": "es|en", "metodo": "prince2-por-etapas",
  "enfoque_entrega": "predictivo|agil|hibrido",
  "fase": "pre-proyecto|inicio|entrega|cierre|cerrado",   // inicio = Initiating (IP); entrega = etapas de entrega (CS/MP/SB)
  "proceso_actual": "SU|IP|CS|SB|CP",
  "etapa_actual": {"numero": 0, "nombre": "", "inicio": "", "fin_previsto": ""},
  "proyecto_autorizado": false, "excepcion_abierta": "X-001|",
  "tolerancias": {"proyecto": {"tiempo": "", "costo": "", "alcance": "", "calidad": "", "beneficios": "", "riesgo": "", "sostenibilidad": ""},
                  "etapa":    {"...": "mismas siete dimensiones"}},
  "roles": {"ejecutivo": "", "usuario_senior": [], "proveedor_senior": [], "gestor_proyecto": "", "aseguramiento": [],
            "soporte": "", "autoridad_cambio": "", "product_owner": "", "jefes_equipo": []},
  "agil": {"cadencia_iteracion_dias": "", "velocidad_referencia": "", "tracker_backlog": ""},
  "artefactos": {"business-case": {"ruta": "", "estado": "borrador|en-revision|aprobado|obsoleto", "version": "1.0", "aprobado_por": ""}},
  "puertas": [{"tipo": "autorizar-inicio", "fecha": "", "decision": "aprobado|condicionado|rechazado|pendiente", "por": "", "condiciones": "", "etapa": 0, "decision_id": "D-001"}],
  "integraciones": {"tracker": "ninguno|jira|linear|github|azure-devops", "chat": "ninguno|slack|teams", "docs": "ninguno|confluence|notion|sharepoint", "reuniones": "manual|archivo|granola|fireflies|zoom|minutes", "okr": "archivo|tability", "diagramas": "mermaid|diagram-design|archify|visual-explainer|drawio", "cronograma": "cpm|mspdi", "export": "scripts|skills-office", "especificacion": "ninguna|bmad", "bmad": {"raiz": "", "layout": "v6|v4", "soporte": ""}}
}
```
Lo escribe solo `estado.py` (y `nuevo_proyecto.py`); los proyectos de versiones anteriores se migran solos al leerse.

### 1.7 Plantillas (templates/*.md)
- Etiquetas de campo bilingües: `**Objetivo / Objective:**`.
- Campos entre `{{llaves}}`; una línea de ayuda en cursiva debajo de cada campo (qué poner, en palabras propias).
- Checklist de calidad al final (`## Lista de verificación / Checklist`).
- Registros en CSV con la fila de cabecera bilingüe `id,titulo|title,...` NO: usar cabecera en inglés técnico simple en snake_case y documentar la traducción en el SKILL.md. Columnas según los esquemas CSV de `plantillas-documentos-registros-reportes.md` Parte V.

### 1.8 Reglas transversales que toda skill incluye en "Reglas del método"
1. [PRINCE2] El ciclo de vida por etapas de gestión es el modo por defecto; el enfoque ágil o híbrido se aplica dentro de las etapas (paquetes de trabajo iterativos), nunca eliminando las puertas de decisión.
2. [PRINCE2] Toda desviación prevista fuera de tolerancia se escala (excepción); el agente nunca "absorbe" una excepción en silencio.
3. [PRINCE2] Nada se da por aprobado sin un acto explícito de aprobación humana registrado (puerta en estado.json y decisiones.csv).
4. [PMBOK→práctica PRINCE2] El PMBOK solo aporta técnica o cubre un vacío, y la regla indica en qué práctica, proceso o producto PRINCE2 se aplica (p. ej. `[PMBOK→Plans/SB] PERT para la estimación del plan de etapa`). Elegir la técnica según la pregunta (pmbok8-artefactos-tecnicas-anexos.md §5) y declarar supuestos y fórmulas. Ante conflicto, manda PRINCE2.
5. [Plantillas] Versión mínima para proyectos pequeños; versión completa cuando el riesgo, el costo o la cantidad de stakeholders lo justifiquen.
6. Transparencia de IA: marcar todo contenido generado como borrador, no inventar datos (usar `[por confirmar]`), citar de qué registro o documento sale cada cifra.
7. Idioma: responder y generar en el idioma del usuario; mantener los nombres de artefactos con su equivalente EN entre paréntesis la primera vez.
8. Escrituras externas (tracker, correo, chat) solo con confirmación explícita.

### 1.9 Integraciones externas opcionales (declarar en "Entradas requeridas" si la skill las usa)
`estado.json.integraciones` define si están disponibles. Si no, la skill usa la alternativa interna (Mermaid, CSV, scripts).
- Diagramas: diagram-design / archify / drawio-mcp → alternativa Mermaid.
- Cronograma y camino crítico: `scripts/cpm.py` (CPM fin-a-comienzo con desfases, Mermaid Gantt y exportación MSPDI para MS Project/ProjectLibre, validada con MPXJ). utf8proj se evaluó y no se incorpora (inmaduro).
- Export Office: skill oficial xlsx/docx/pptx o `<pm-estado-proyecto>/scripts/exportar.py` (docx/xlsx) y `<pm-exportar>/scripts/paquete.py` (ZIP de puerta).
- Trackers: MCP Atlassian / Linear / GitHub / Notion → alternativa: registros CSV.
- Reuniones: minutes / transcript-to-actions / meeting-analyzer → alternativa: pegar transcripción.

### 1.10 Convenciones canónicas (vinculantes para todas las skills y agentes)
1. **Rutas de scripts.** `<pm-estado-proyecto>/scripts/x.py` denota la carpeta instalada de esa skill: en el plugin `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/`, en instalación manual `~/.claude/skills/pm-estado-proyecto/`, en Hermes `~/.hermes/skills/pm-estado-proyecto/` (o la ruta que muestre el gestor de skills). Dentro de un SKILL.md, Claude Code expande `${CLAUDE_SKILL_DIR}` (carpeta de esa skill) y, en el plugin, `${CLAUDE_PLUGIN_ROOT}`; en Hermes se usa la ruta bajo `~/.hermes/skills/`. Los scripts se ejecutan desde cualquier carpeta con `--proyecto <dir>`.
2. **Numeración de etapas.** La puesta en marcha (SU) es pre-proyecto, `etapa_actual.numero = 0`, no es etapa de gestión. **Etapa 1 = iniciación**; las etapas de entrega son 2…n. Archivos: `02-planificacion/plan-etapa-<n>.md`, `03-control/reportes/<fecha>-informe-fin-etapa-<n>.md`, `03-control/reportes/<fecha>-informe-excepcion-X-###.md`, `02-planificacion/plan-excepcion-X-###.md`. `autorizar-etapa` aprobada avanza `etapa_actual` a n+1 automáticamente.
3. **Claves de artefactos** en `estado.json.artefactos` (= `tipo` del frontmatter, sin fecha): `mandato`, `propuesta-proyecto`, `project-brief`, `canvas-arranque`, `declaracion-vision`, `roadmap`, `business-case`, `enfoque-beneficios`, `enfoque-sostenibilidad`, `estructura-organizativa`, `descripcion-rol-<rol>`, `team-charter`, `matriz-raci`, `analisis-stakeholders`, `plan-compromiso-stakeholders`, `acta-constitucion`, `pid`, `enfoque-<tema>` y `plan-gestion-<tema>`, `descripcion-producto-proyecto`, `pbs-wbs`, `diccionario-wbs`, `enunciado-alcance`, `plan-proyecto`, `plan-etapa-<n>`, `cronograma`, `presupuesto`, `backlog`, `release-plan`, `matriz-comunicaciones`, `estrategia-adquisiciones`, `WP-###`, `highlight-<fecha>`, `informe-fin-etapa-<n>`, `informe-excepcion-X-###`, `evaluacion-excepcion-X-###`, `plan-excepcion-X-###`, `evaluacion-probabilidad-impacto`, `linea-base-costo`, `hoja-estimacion`, `hoja-costeo`, `business-case-esquematico`, `solicitud-<puerta>` (documento de pm-direccion-decisiones), `acta-junta-<fecha>`, `acta-reunion-<fecha>` (actas de pm-reuniones; varias el mismo día: `-2`, `-3`), `registro-aceptacion`, `handover`, `informe-fin-proyecto`, `informe-lecciones`, `recomendaciones-seguimiento`, `plan-revision-beneficios`, `notificacion-cierre`. Los ZIP generados se registran (si se desea) como `exportado-paquete-<puerta>` y nunca se reincluyen.
4. **Puertas y aprobaciones.** Solo `pm-director` registra puertas (`estado.py puerta`, que además escribe la fila en `decisiones.csv`). Los demás agentes preparan los productos, los dejan `en-revision` y derivan. Tras una aprobación humana de un documento: `estado.py aprobar <clave> --por "<rol: nombre>" --nivel <nivel>` (sincroniza frontmatter y `estado.json`): nivel junta o capa-negocio → solo pm-director; nivel gestor, product-owner o equipo → el agente de la fase, con la confirmación humana traída por el orquestador. Nombramientos (`estado.py rol`) → pm-director tras confirmación del ejecutivo. Transiciones: `estado.py limite-etapa [--excepcion X-###]` (CS→SB), `estado.py cierre [--prematuro]` (→CP). Excepción: pm-control prepara el informe de excepción y deriva; pm-director registra la decisión (`puerta decision-ad-hoc` pidiendo plan de excepción) y ejecuta `estado.py limite-etapa --excepcion X-###`; pm-planificacion prepara el plan de excepción; pm-director registra `autorizar-plan-excepcion`. `condicionado` avanza como aprobado y deja condiciones abiertas hasta `cumplir-condiciones`.
5. **Tolerancias** por nivel: `estado.json.tolerancias.proyecto` (fija la capa de negocio/ejecutivo) y `.etapa` (fija la junta en cada `autorizar-etapa`); las de paquete de trabajo viven en el documento del paquete. Tiempo y costo, mínimo obligatorio.
6. **Costos y EVM.** BAC = línea base de medición del desempeño = Σ paquetes de trabajo (estimación base) + reserva de contingencia asignada a riesgos identificados; **la reserva de gestión queda fuera del BAC** y solo la libera la junta. Presupuesto autorizado = BAC + reserva de gestión. No se agrega contingencia dentro de cada estimación de paquete y otra vez a nivel de etapa. Semáforo de `evm.py` contra tolerancias (`--tol-costo`, `--tol-plazo`): verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo = fuera → excepción.
7. **EVM ágil** con costo y fecha fijos: un EAC > BAC se lee como alcance pronosticado que no entra, contra la tolerancia de alcance (MoSCoW), no como sobrecosto; hay excepción solo si los Must no entran (`evm.py --modo agil`).
8. **Registros** (ver `pm-estado-proyecto/scripts/esquema.py` y `pm-registros/templates/guia-registros.md`, que coinciden): prefijos R, I, C, D, S, L, ST, Q, **A** (acciones: `acciones.csv`, compromisos por actor que alimentan el tablero; una acción no es un issue). Issues: exactamente cinco tipos `solicitud-cambio`, `fuera-especificacion`, `problema-preocupacion`, `evento-externo`, `oportunidad-negocio`; prioridad `urgente|alta|media|baja`; severidad `critica|mayor|menor|informativa`. Niveles de decisión: `equipo`, `product-owner`, `gestor`, `autoridad-cambio`, `ejecutivo` (decisiones del ejecutivo fuera de puerta), `junta`, `capa-negocio`. Las puertas, `rol`, `tolerancia`, `agil`, `umbrales-riesgo`, `cumplir-condiciones`, `limite-etapa --excepcion`, `set --forzar` y `aprobar` (que además crea la copia congelada en `00-direccion/historial/<clave>-v<versión>`) de nivel `autoridad-cambio`/`ejecutivo`/`junta`/`capa-negocio` los ejecuta solo pm-director; el hook `guardian.py` lo hace cumplir en el hilo principal y en los demás subagentes (los comandos que la persona escribe en su propia terminal no pasan por el hook). **Verificación de puertas (`puertas.py`, `docs/PUERTAS.md`):** toda puerta de la junta salvo `decision-ad-hoc` se verifica en tres capas — salud (`sanidad.py --rapido` sin ERROR), controles automáticos de PRINCE2 (artefactos, tolerancias, criterios de éxito, calidad, registros abiertos) y de BMAD (PRD y arquitectura `final`, línea base, gate de preparación PASS/CONCERNS/FAIL), y lista de control de la junta confirmada con `puertas.py confirmar --por`. `estado.py puerta --decision aprobado` se rechaza con bloqueos; `condicionado` los suma como condiciones; `--forzar` los anota; las condiciones de los controles quedan como observaciones en la puerta y en `decisiones.csv`.
9. **Riesgo.** Escala P e I 1–5; puntuación P×I: alto ≥15, medio 6–12, bajo ≤5 (configurable en el enfoque de riesgo y en `estado.py umbrales-riesgo alto=.. medio=..`, que usa `registro.py resumen`). Línea de tolerancia por defecto: ningún riesgo alto abierto sin respuesta y propietario. Valor esperado (EMV) = impacto monetario × probabilidad (1–5 → 10/30/50/70/90 % por convención del paquete, configurable).
10. **Stakeholders:** poder e interés `alto|medio|bajo`; actitud y compromiso `lider|partidario|neutral|resistente|desconocedor`; columna `confidencial=si` para valoraciones sensibles (circulación restringida).
11. **Dueños únicos.** Comunicación: `enfoque-comunicacion.md` (pm-enfoques-gestion: políticas, PID) + `matriz-comunicaciones.md` (pm-comunicacion-stakeholders: matriz operativa, anexo del enfoque). Alcance: `enunciado-alcance` y PBS/WBS (pm-planificacion-por-productos: QUÉ) vs `plan-gestion-alcance-requisitos` (pm-enfoques-gestion: CÓMO). Informe de excepción: plantilla en pm-issues-cambios; pm-progreso-reportes detecta el pronóstico fuera de tolerancia y la usa. Retrospectiva de iteración: pm-agil-hibrido (`retrospectiva.md`); taller de lecciones de etapa: pm-lecciones-aprendidas (`retrospectiva-etapa.md`). Burn-down/burn-up: en los informes (`03-control/reportes/`); el release plan guarda solo la línea base.
12. **Ágil dentro de etapas.** El product owner (usuario sénior delegado) intercambia ítems del backlog dentro de la tolerancia de alcance de la etapa sin solicitud de cambio (decisión `nivel=product-owner` en `decisiones.csv`); agregar alcance que desplaza un Must o excede la tolerancia es solicitud de cambio. **Perfil ágil mínimo**: brief ligero + visión, business case de una página, estructura con PO, enfoques en una página, backlog priorizado (MoSCoW, puntos, criterios de aceptación) en lugar de PBS/WBS completa (la PBS puede ser el árbol épica→historia), release plan por etapas, DoD/DoR, presupuesto por iteración, highlight corto con burn-up. Puertas de etapa siempre.
13. **Idioma.** Plantillas con `idioma: "{{idioma}}"` y etiquetas bilingües; datos faltantes como `[por confirmar]` (ES) o `[to be confirmed]` (EN). Los scripts responden en el idioma de `estado.json`.
14. **Integraciones visuales.** Por defecto Mermaid y las plantillas HTML de pm-visuales; si `integraciones.diagramas` declara `archify`, `visual-explainer` o `diagram-design`, pm-visuales prepara el insumo para esa skill y guarda el resultado en `02-planificacion/visuales/` o `03-control/reportes/`.

### 1.11 Agentes, subagentes y protocolo de retorno
- **Orquestador en el hilo principal.** `pm-orquestador` es skill (`/pm-method:pm-orquestador`, `/pm-orquestador` en
  instalación manual o Hermes) y también agente para hilo principal (`claude --agent pm-method:pm-orquestador`). Es el
  único que conversa con el usuario, hace las preguntas y presenta las puertas.
- **Agentes de fase = subagentes** (pm-director, pm-inicio, pm-planificacion, pm-control, pm-cierre): contexto aislado
  para producir artefactos sin llenar la conversación. No pueden preguntar al usuario (Claude Code les quita
  `AskUserQuestion`) y no delegan en otros subagentes (`disallowedTools: Agent`).
- **Herramientas.** Los agentes NO declaran `tools`: heredan todas las de la sesión, incluidos los MCP que el usuario
  conecte después (Jira, Slack, Teams…). La organización puede restringir con `disallowedTools`.
- **Skills.** Los subagentes invocan skills por demanda (no se precargan con `skills:`, para no gastar contexto).
- **Protocolo de retorno** (obligatorio al final de cada subagente):
  ```
  ## Retorno al orquestador / Return
  - Hecho: <artefactos con ruta y estado; ids de registros>
  - Decisiones humanas requeridas: <pregunta · opciones · quién decide (rol)>   (o "ninguna")
  - Datos faltantes: <campo · a quién preguntar>                                  (o "ninguno")
  - Siguiente paso sugerido: <agente/skill>
  ```
- **Hermes**: no hay subagentes con nombre; los agentes se usan como personas (perfil/SOUL.md) y la lógica vive en las
  skills, que Hermes expone como comandos `/nombre-skill`.

### 1.12 Integraciones MCP genéricas (sin predefinir conectores)
- Las skills son agnósticas de herramienta: describen **capacidades** (leer issues, crear issue, publicar mensaje,
  leer transcripción, leer evento de calendario, leer/escribir página) y `pm-integraciones` las resuelve con los MCP que
  existan en la sesión. El paquete no trae `.mcp.json` ni credenciales.
- Lectura libre; **escritura externa solo con vista previa y confirmación explícita** del usuario (en subagentes: se
  devuelve como "decisión humana requerida").
- Los datos externos entran como **instantáneas fechadas** en `03-control/fuentes/<sistema>-AAAA-MM-DD.(csv|md|json)`
  y se citan en los informes; nunca reemplazan a los registros de gobierno.
- `estado.json.integraciones` registra qué sistema cumple cada capacidad (`estado.py integracion tracker=jira`).

### 1.13 BMAD como capa de especificación (contrato estable)
- **Separación**: PRINCE2 gobierna; BMAD especifica el producto. Los artefactos BMAD son **productos especialistas**
  creados en paquetes de trabajo (MP) y aprobados en las puertas PRINCE2. pm-method **nunca escribe en carpetas de BMAD**
  ni ejecuta skills de BMAD por su cuenta; solo lee mediante `pm-bmad-puente` (`scripts/bmad.py`).
- **Compatibilidad**: BMAD v6.11–v6.12 (salidas en carpetas fechadas bajo `planning-artifacts/`) y v4 (`docs/`,
  `.bmad-core/core-config.yaml`). Descubrimiento por configuración y patrones, nunca por nombre de skill BMAD. Fuera de
  rango: modo degradado con aviso.
- **Dueño único de cada dato** (sin duplicar):
  | Dato | Dueño | pm-method hace |
  |---|---|---|
  | Justificación, beneficios, costos totales, tolerancias | business case PRINCE2 | — |
  | Problema, usuarios, visión del producto | brief de producto BMAD | el project brief lo referencia |
  | Requisitos FR/NFR, journeys UJ, métricas de éxito SM | PRD BMAD | PBS/descripciones de producto citan ids; RTM derivada |
  | Decisiones de arquitectura AD | arquitectura BMAD | riesgos/calidad citan ids |
  | Épicas, historias, estado de desarrollo | `epics.md` y `sprint-status.yaml` BMAD | `backlog.csv`: columnas derivadas por sincronización |
  | Prioridad MoSCoW, release, etapa, estimación de gobierno | pm-method (`backlog.csv`) | el puente nunca las sobrescribe |
  | Beneficios ↔ métricas de éxito; OKR | business case / `okr.csv` citan SM-n | — |
- **Línea base y cambios**: al aprobar una puerta, pm-director fija la línea base (`bmad.py linea-base prd --version 1.0`:
  huella sha256 + copia congelada en `00-direccion/historial/`). `bmad.py verificar` detecta desvíos (ids agregados o
  retirados) y Sprint Change Proposals nuevas → issue `solicitud-cambio`; decide la autoridad de cambio PRINCE2. El
  "sí" dentro del flujo correct-course de BMAD no sustituye esa decisión.
- **Mapeo de ciclo de vida**: SU → brief de producto (insumo); etapa 1 (iniciación) → PRD `final` + arquitectura suficiente
  para estimar + épicas iniciales; etapas de entrega → releases por épica, cada sprint = paquete de trabajo; el gate de
  preparación de BMAD (sprint planning PASS/CONCERNS/FAIL) es insumo de `autorizar-etapa`.

### 1.14 Dueños únicos y colisiones entre skills
Cada tema tiene una sola skill dueña; las demás la invocan. Matriz completa en `docs/colisiones.md`. Pares sensibles:
registros genéricos (pm-registros) vs riesgos (pm-riesgos) vs issues/cambios (pm-issues-cambios); informes
(pm-progreso-reportes) vs visuales (pm-visuales); plan de etapa (pm-plan-etapa-y-limites) vs cronograma
(pm-cronograma-estimacion); comunicación (pm-comunicacion-stakeholders) vs reuniones (pm-reuniones); business case
(pm-caso-de-negocio) vs OKR (pm-okr); requisitos (pm-planificacion-por-productos, solo si no hay BMAD) vs PRD (pm-bmad-puente).

### 1.15 Comandos
Toda skill es invocable como comando (`/pm-method:<skill>` en el plugin; `/<skill>` en instalación manual y en Hermes).
Además hay skills-comando de uso humano (`disable-model-invocation: true`, sin costo de contexto): `pm-ayuda`, `pm-nuevo`,
`pm-estado`, `pm-reporte`, `pm-puerta`, `pm-sync`.

### 1.16 Sincronización con fuente única (especificación ↔ gobierno)
**Decisión**: cada dato tiene un solo dueño que lo escribe; todos los demás lo **leen a través de una fachada** y, en
sentido inverso, las decisiones de gobierno se **traspasan** al dueño para que él las aplique. No hay copias editables
ni sincronización bidireccional de archivos.

| Opción evaluada | Ventaja | Riesgo | Veredicto |
|---|---|---|---|
| Cada skill lee BMAD directamente | sin copias | ~30 skills acopladas a formatos BMAD que cambian en casi cada versión menor; lógica de lectura duplicada e inconsistente | descartada como acceso directo; adoptada **detrás de la fachada** |
| Sincronización bidireccional de archivos | ambos lados al día | dos escritores sobre el mismo dato: conflictos, ids reescritos, ambigüedad sobre quién manda | descartada |
| Exportar copias periódicas BMAD → pm | simple | duplicación y desfase silencioso | descartada (solo copias congeladas para líneas base) |
| **Fuente única + fachada de lectura + traspaso de decisiones** | un dueño por dato; skills independientes del formato de BMAD; cambios trazables | requiere disciplina de verificación (automatizada por huellas) | **adoptada** |

**Mecanismo**
1. **Lectura (BMAD → todas las skills)**: `<pm-estado-proyecto>/scripts/especificacion.py --proyecto <dir> fuente|resumen|consultar <id>|listar …`.
   Devuelve requisitos (FR/NFR/UJ/SM/AD/UX-DR o REQ-nnn), épicas e historias con su estado, cobertura, paquetes de la WBS
   y columnas de gobierno, desde el contrato `pm-spec-index/1` (`02-planificacion/especificacion/spec-index.json`). El índice
   es un caché: se reconstruye solo cuando cambia la huella de las fuentes. Ninguna skill abre archivos de BMAD ni
   `requisitos.md` para extraer datos.
2. **Mismo contrato sin BMAD**: con `integraciones.especificacion ≠ bmad`, el proveedor es pm-method (`requisitos.md`,
   `backlog.csv`, `wbs.csv`) y las skills no cambian.
3. **Escritura por dueño**: especificación → equipo BMAD con sus flujos; gobierno (prioridad, MoSCoW, release, iteración,
   estimación, paquete) → `backlog.csv`; vínculo a la WBS → columna `ref` de `wbs.csv`; beneficios → business case; OKR →
   `okr.csv`. `bmad.py backlog` solo refresca las columnas derivadas de `backlog.csv` (la única tabla que combina ambos lados).
4. **Sentido inverso (gobierno → BMAD)**: `bmad.py handoff [--cambio C-###]` emite `02-planificacion/especificacion/
   handoff-bmad-<fecha>-<…>.md` con el cambio aprobado (ids afectados) y las prioridades de gobierno que cambiaron. El equipo
   BMAD lo aplica (actualización del PRD con ids estables, corrección de rumbo, planificación del sprint) y confirma.
5. **Verificación y línea base**: `bmad.py verificar` (cada período y antes de cada puerta) compara huellas e ids con la
   línea base; un desvío no traspasado = cambio no controlado → issue. Tras aplicar un traspaso: `verificar` limpio y nueva
   línea base (`bmad.py linea-base … --version` mayor) por pm-director.
6. **Ids estables**: el vínculo entre capas es siempre el id (FR-3, 1-2-slug, REQ-004, B-1, SM-1, WBS 1.2.3, WP-…); los
   textos nunca se copian entre documentos.

**Qué lee y qué escribe cada skill** (resumen; matriz completa en `docs/sincronizacion.md`):
| Skill | Lee de la especificación (fachada) | Escribe (dueña) |
|---|---|---|
| pm-mandato-y-brief | brief de producto (artefacto), visión | project brief (cita el brief BMAD) |
| pm-caso-de-negocio | SM-n | beneficios B-n (citan SM-n) |
| pm-okr | SM-n | `okr.csv` (KR citan B-n/SM-n) |
| pm-planificacion-por-productos | requisitos, cobertura | PBS, descripciones de producto, `wbs.csv` (`ref`) |
| pm-cronograma-estimacion | épicas, historias, estimación de gobierno | `actividades.csv`, cronograma |
| pm-costos-presupuesto | épicas/historias por release | presupuesto |
| pm-agil-hibrido | historias y estados | columnas de gobierno de `backlog.csv`, release plan |
| pm-plan-etapa-y-limites | historias/épicas de la etapa, cobertura | planes de etapa y excepción |
| pm-paquetes-trabajo | historias del sprint o épica del paquete | paquete de trabajo |
| pm-progreso-reportes | estados, `avance-bmad.csv` | informes |
| pm-riesgos | AD-n, NFR, preguntas abiertas del PRD | `riesgos.csv` (cita ids) |
| pm-calidad | criterios por historia, NFR, cobertura | `calidad.csv`, aceptación |
| pm-issues-cambios | desvíos (`verificar`) | `issues.csv`, `cambios.csv`, origen del traspaso |
| pm-cierre-proyecto | cobertura `terminado` por requisito | aceptación, informe final |
| pm-visuales | resumen y estados | tablero |

### 1.17 Controles permanentes de sanidad y consistencia
| Control | Cuándo actúa | Qué asegura | Cliente |
|---|---|---|---|
| `sanidad.py` (skill `pm-sanidad`) | inicio de sesión (rápido), antes de cada puerta, tras sincronizar, al actualizar pm-method o BMAD | coherencia de estado y puertas, roles, artefactos, registros, ids entre capas, cobertura, líneas base vs especificación (cambio no controlado), traspasos pendientes, integraciones, instalación y colisiones con skills de otros repos | todos |
| Hook `PreToolUse` (`hooks/guardian.py`) | cada Write/Edit/Bash | `estado.json` solo por script; registros solo por `registro.py`; derivados, copias congeladas e instantáneas de fuentes no editables; subagentes pm-* sin escritura en BMAD ni comandos reservados a pm-director | Claude Code (plugin) |
| Hook `SessionStart` (`hooks/inicio.py`) | al abrir, retomar, limpiar o compactar | contexto con fase, puertas y errores de sanidad | Claude Code (plugin) |
| Regla de puerta (`pm-puerta`, pm-director) | antes de presentar una puerta | ninguna puerta con ERROR sin decisión humana registrada como condición | todos |
| Esquemas versionados | al leer | `estado.json` y registros migran solos; contrato `pm-spec-index/1`; `compatibilidad.json` declara versiones probadas de BMAD | todos |
| `scripts/validar_paquete.py` | tras cualquier cambio del paquete | estructura, tamaños, descripciones (formato y presupuesto), referencias, agentes (herencia de herramientas, sin anidación), cobertura de orquestación, hooks | mantenedor |
| `scripts/probar_paquete.py` | tras cambios del paquete o de BMAD | regresión de punta a punta con BMAD v6, BMAD v4 y sin BMAD, incluida la sanidad (casos sanos y con defectos sembrados) | mantenedor |

## 2. Agentes (agents/*.md, formato de sub-agente de Claude Code)
Frontmatter: `name`, `description` (bilingüe, con disparadores), `model: inherit`, `disallowedTools: Agent` (agentes de fase). Sin `tools` (herencia, ver 1.11).
Cuerpo: rol, responsabilidades PRINCE2/PMBOK, skills que invoca y en qué orden, entradas/salidas, puertas que exige, reglas de escalamiento, estilo de salida, idioma. En Hermes se usan como texto de perfil/persona.

## 3. Calidad del paquete
- Ninguna frase copiada de las fuentes; ejemplos inventados.
- Cuerpo de SKILL.md ≤ 12 000 caracteres y ≤ 200 líneas; el detalle en `references/guia.md` (ver 1.4); procedimiento con puertas humanas; checklist de calidad.
- `description` ≤ 240 caracteres con formato "Usar: … No: …→…" (ver 1.3); total del listado del paquete ≤ 7 500 caracteres.
- Validación: `python3 scripts/validar_paquete.py` (frontmatter, longitud, encabezados).
