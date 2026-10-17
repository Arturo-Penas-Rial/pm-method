# Catálogo de pm-method 2.0.0 · Agents and skills catalog

Referencia de los 6 agentes, las 37 skills (31 que el modelo puede activar solo y 6 comandos de uso humano) y los scripts del paquete. Todo lo que figura aquí sale de `SPEC.md`, de `agents/*.md` y del frontmatter y cuerpo de cada `skills/*/SKILL.md`. Si algo de este catálogo contradice esos archivos, mandan ellos.

## 1. Cómo leer este catálogo

**Reparto de capas (SPEC §0).** PRINCE2 7 define qué se hace, cuándo y quién decide: etapas de gestión, gestión por excepción, roles de la junta, procesos y productos de gestión. El PMBOK 8 aporta solo técnicas (el "cómo") y siempre se aplica dentro de una práctica, proceso o producto PRINCE2. BMAD, si el proyecto lo usa, es la capa de especificación del producto y pm-method la lee sin escribirla. Los MCP que conecte el usuario (Jira, Slack, Teams…) son fuentes y canales. La fuente de verdad del gobierno es la carpeta del proyecto (`estado.json`, Markdown y CSV).

**Abreviaturas de procesos PRINCE2.** SU = puesta en marcha (Starting up, etapa 0, pre-proyecto) · DP = dirección (Directing) · IP = iniciación (Initiating, etapa 1) · CS = control de etapa (Controlling a stage) · MP = entrega de productos (Managing product delivery) · SB = límite de etapa (Managing a stage boundary) · CP = cierre (Closing). Las etapas de entrega van de la 2 a la n.

**Prácticas PRINCE2** (tal como figuran en `metadata.pm-method.practicas_prince2`): business-case, organizing, plans, quality, risk, issues, progress.

**Invocación.** Toda skill es invocable como comando: `/pm-method:<skill>` dentro del plugin, `/<skill>` en instalación manual y en Hermes Agent. El orquestador también corre como agente de hilo principal: `claude --agent pm-method:pm-orquestador`.

**Rutas de scripts (SPEC §1.10.1).** `<pm-estado-proyecto>/scripts/x.py` es la carpeta instalada de esa skill: en el plugin, `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/scripts/`; en instalación manual, `~/.claude/skills/pm-estado-proyecto/scripts/`; en Hermes, `~/.hermes/skills/pm-estado-proyecto/scripts/`. Todos los scripts aceptan la carpeta del proyecto con `--proyecto <dir>` (o como argumento posicional en `wbs.py`, `cpm.py`, `okr.py` y `transcripcion.py`, que reciben un archivo).

**Fachada de especificación (SPEC §1.16).** Ninguna skill abre archivos de BMAD ni `requisitos.md` para sacar datos. Todas consultan `especificacion.py` (contrato `pm-spec-index/1`), que con BMAD delega en `bmad.py` y sin BMAD lee `requisitos.md`, `backlog.csv` y `wbs.csv`. En cada ficha, la línea "Lee de la fachada" indica qué consulta esa skill.

## 2. Comandos de uso humano

Los seis comandos llevan `disable-model-invocation: true`: el modelo no los activa por su cuenta y no ocupan presupuesto del listado de skills. Al recibir uno, el orquestador sigue su procedimiento con esa intención.

| Comando | Argumentos (`argument-hint`) | Qué hace | Agente y skills que usa | ¿Escribe? |
|---|---|---|---|---|
| `/pm-ayuda` | `[tema / topic]` | Muestra qué escribir en cada situación, la lista de skills y comandos, el ciclo de vida con sus puertas, las carpetas y la regla de fuente única. Si hay proyecto, agrega `estado.py siguiente`. | orquestador; lee pm-orquestador | No |
| `/pm-nuevo` | `"Nombre del proyecto" [carpeta] [es\|en] [predictivo\|agil\|hibrido]` | Crea la carpeta con `nuevo_proyecto.py`; si hay BMAD en la carpeta o en una superior, `bmad.py detectar` e `integracion especificacion=bmad`. No sobrescribe un proyecto existente. | orquestador; pm-estado-proyecto, pm-bmad-puente | Sí (carpeta nueva) |
| `/pm-estado` | `[carpeta del proyecto / project folder]` | `estado.py ver` y `siguiente`, `registro.py resumen`, `sanidad.py --rapido` y, con BMAD, `bmad.py avance`. Responde en tres líneas, una tabla corta y el siguiente paso con el rol que decide. | orquestador; pm-estado-proyecto, pm-sanidad, pm-bmad-puente | Solo la fila de `avance-bmad.csv` |
| `/pm-reporte` | `highlight\|checkpoint\|excepcion [carpeta]` | Produce el informe pedido. Antes corre `registro.py resumen`, `evm.py` con tolerancias, `bmad.py avance` y `verificar`, y `/pm-sync` si hay tracker. Una excepción se deriva a pm-director. | pm-control; pm-progreso-reportes, pm-issues-cambios | Sí, informe `en-revision` |
| `/pm-puerta` | `autorizar-inicio\|autorizar-proyecto\|autorizar-etapa\|autorizar-plan-excepcion\|autorizar-cierre\|decision-ad-hoc [carpeta]` | `sanidad.py --informe`, `paquete.py listar`, `especificacion.py resumen`, `bmad.py verificar` y traspasos pendientes; pm-director redacta la solicitud; el orquestador presenta opciones al humano. Solo tras una decisión explícita, pm-director registra. | pm-director; pm-direccion-decisiones, pm-exportar, pm-bmad-puente, pm-sanidad | Sí, solicitud `en-revision` |
| `/pm-sync` | `[bmad\|tracker\|okr\|todo] [carpeta]` | `especificacion.py resumen`; con BMAD, `bmad.py backlog`, `avance` y `verificar`; lista traspasos pendientes; instantáneas de tracker u OKR vía pm-integraciones; termina con `sanidad.py`. Propone cambios, no los aplica sin confirmación. | pm-control; pm-bmad-puente, pm-integraciones, pm-okr, pm-sanidad | Derivados e instantáneas |

## 3. Agentes

### 3.1 Resumen

| Agente | Tipo | Rol | Procesos PRINCE2 | Puertas que prepara |
|---|---|---|---|---|
| `pm-orquestador` | Hilo principal (`model: inherit`, sin `disallowedTools`) | Único que conversa con el usuario: lee el estado, clasifica la petición, delega, hace las preguntas y presenta las decisiones humanas. | SU, DP, IP, CS, MP, SB, CP (coordina) | Ninguna propia: presenta todas al humano |
| `pm-director` | Subagente (`disallowedTools: Agent`) | Representa el nivel de dirección: prepara solicitudes de decisión y es el **único agente que ejecuta `estado.py puerta` y `estado.py aprobar`**, siempre después de una decisión humana con nombre y rol. | DP (y SB, CP en lo que toca a la junta) | Compone la solicitud de todas; registra todas |
| `pm-inicio` | Subagente | Lleva el proyecto del mandato a quedar listo para autorizar. | SU, IP | `autorizar-inicio`; `autorizar-proyecto` + `autorizar-etapa` (etapa 2) |
| `pm-planificacion` | Subagente | Planificación basada en productos y técnicas de estimación, programación y costeo. | Plans; IP, SB | Insumos de `autorizar-inicio`, `autorizar-proyecto`, `autorizar-etapa`, `autorizar-plan-excepcion`; opciones para `decision-ad-hoc` |
| `pm-control` | Subagente | Mantiene la etapa dentro de tolerancias: paquetes, registros, informes, calidad, actas, sincronización; prepara excepciones. | CS, MP | Informe de excepción (insumo de `decision-ad-hoc`) |
| `pm-cierre` | Subagente | Cierre ordenado, planificado o prematuro. | CP | `autorizar-cierre` |

Ningún agente declara `tools`: heredan todas las herramientas de la sesión, incluidos los MCP que se conecten después. La organización puede restringir con `disallowedTools`. Los subagentes no pueden preguntar al usuario (Claude Code les quita `AskUserQuestion`) y no delegan en otros subagentes. Invocan skills por demanda; no las precargan.

### 3.2 Protocolo de retorno (obligatorio en los cinco subagentes)

```
## Retorno al orquestador / Return
- Hecho: <artefactos con ruta y estado; ids de registros>
- Decisiones humanas requeridas: <pregunta · opciones · quién decide (rol)>   (o "ninguna")
- Datos faltantes: <campo · a quién preguntar>                                  (o "ninguno")
- Siguiente paso sugerido: <agente/skill>
```

El orquestador verifica *Hecho* con `estado.py ver` (ninguna puerta registrada fuera de pm-director), pregunta los *Datos faltantes*, presenta las *Decisiones humanas requeridas* (pregunta, opciones con consecuencia, rol que decide; pide nombre y rol de quien responde) y, solo con la respuesta, invoca a pm-director para registrar. En pm-director, *Hecho* incluye además las puertas y decisiones registradas con su id.

### 3.3 Fichas

#### pm-orquestador
- **Invocación:** `/pm-method:pm-orquestador` (skill) · `claude --agent pm-method:pm-orquestador` o `"agent"` en `settings.json` · `/pm-orquestador` en manual y Hermes.
- **Cada turno:** (0) `sanidad.py --rapido` si el hook de inicio no lo hizo; (1) `estado.py ver` y `siguiente`; (2) resumen en tres líneas: fase/proceso y etapa, tolerancias y excepción abierta, puertas pendientes y condiciones; (3) clasificar con la tabla de enrutamiento de la skill y delegar; (4) pasar al subagente todo lo que necesita, porque no puede preguntar; (5) leer el retorno y presentar decisiones; (6) si la petición cruza fases, mostrar la secuencia y pedir conformidad; (7) cerrar con "Siguiente paso según el método" y el rol que decide.
- **Transiciones que secuencia:** SU → IP con `autorizar-inicio`; IP → CS con `autorizar-proyecto` + `autorizar-etapa`; CS → SB con `estado.py limite-etapa`; SB → CS con `autorizar-etapa`; excepción: pm-control → pm-director → pm-planificacion → `autorizar-plan-excepcion`; última etapa → CP con `estado.py cierre` → pm-cierre → `autorizar-cierre`. Con BMAD, `bmad.py verificar` antes de cada puerta.
- **Skills que usa en el hilo principal:** pm-orquestador, pm-sanidad, pm-knowledge y los seis comandos.
- **Reglas propias:** una pregunta de desambiguación por turno; no saltar puertas (si el usuario insiste, explicar el riesgo y registrarlo como decisión); escrituras externas solo tras vista previa y confirmación; OKR subordinados al business case; clima de equipo solo con consentimiento.
- **Hermes:** texto de persona del perfil `pm-orquestador`; ejecuta directamente las skills que en Claude Code delegaría.

#### pm-director
- **Skills, en orden:** pm-estado-proyecto → pm-exportar (`paquete.py listar`) → pm-caso-de-negocio (justificación continua) → pm-okr (lectura de beneficios) → pm-bmad-puente (`verificar` antes, `linea-base` después) → pm-direccion-decisiones → pm-comunicacion-stakeholders. Scripts: `estado.py`, `registro.py`, `paquete.py`, `bmad.py`, `okr.py`.
- **Modo A (preparar):** `sanidad.py --informe` (un ERROR abierto impide proponer la decisión salvo que el humano lo acepte como condición); `paquete.py listar`; `bmad.py verificar`; resumen de riesgos, issues y desempeño contra tolerancias; solicitud `00-direccion/decisiones/<fecha>-solicitud-<puerta>.md` en `en-revision` con opciones (aprobar, condicionar, rechazar, pedir información, cierre prematuro). No registra nada.
- **Modo B (registrar, con decisión explícita traída por el orquestador):** `estado.py puerta <tipo> --decision … --por "<rol: nombre>" [--condiciones ..] [--etapa-nombre ..] [--fin ..]`; `estado.py aprobar <clave> --por … --version 1.0` por documento; en `autorizar-proyecto`, congelar PID y business case en `00-direccion/historial/` y, con BMAD, `bmad.py linea-base prd|arquitectura|epicas …`; en `autorizar-etapa`, `estado.py tolerancia --nivel etapa` y una acción A-### por condición; acta `<fecha>-acta-junta-<puerta>.md`.
- **Excepciones:** confirma que el informe de pm-control supera la tolerancia (si no, lo devuelve como issue del gestor); si supera la de proyecto, prepara la escalada a la capa de negocio; evaluación `<fecha>-evaluacion-excepcion-X-###.md`; tras la decisión, `puerta decision-ad-hoc`, `estado.py limite-etapa --excepcion X-###`, encargo del plan a pm-planificacion y luego `autorizar-plan-excepcion`. Cierre prematuro: `estado.py cierre --prematuro`.
- **Hermes:** tarjetas Kanban "puerta" y "excepción" con aprobación humana obligatoria.

#### pm-inicio
- **SU:** pm-estado-proyecto (`nuevo_proyecto.py`, `siguiente`) → pm-bmad-puente (`detectar`, `inventario`) → pm-mandato-y-brief → pm-organizacion-roles → pm-caso-de-negocio (esquemático, OBJ-n y B-nn) → pm-riesgos (iniciales) → pm-plan-etapa-y-limites (`plan-etapa-1.md`).
- **IP:** pm-enfoques-gestion → pm-adquisiciones (si hay proveedores) → planes con pm-planificacion (lo coordina el orquestador) → pm-caso-de-negocio (completo y enfoque de beneficios) → pm-okr → pm-acta-constitucion (PID) → pm-comunicacion-stakeholders (matriz y kickoff) → pm-integraciones (`estado.py integracion …`).
- **Entrega a pm-director:** cada producto con `estado.py artefacto <clave> --ruta .. --estado en-revision` y la lista del paquete de puerta.
- **Perfil ágil mínimo:** brief ligero + visión, business case de una página, estructura con PO, enfoques en una página, backlog priorizado en lugar de PBS/WBS completa, release plan por etapas, DoD/DoR. Las puertas se mantienen.

#### pm-planificacion
- **Skills, en orden típico:** pm-estado-proyecto → pm-bmad-puente (`requisitos`, `trazabilidad --wbs`, `backlog`) → pm-planificacion-por-productos → pm-adquisiciones → pm-riesgos → pm-cronograma-estimacion → pm-costos-presupuesto → pm-agil-hibrido → pm-plan-etapa-y-limites → pm-visuales → pm-okr (solo lectura en límites de etapa). Scripts: `estado.py`, `wbs.py`, `cpm.py`, `evm.py`, `bmad.py`.
- **Entregas a pm-director:** fin de SU: `plan-etapa-1.md` (`autorizar-inicio`); fin de IP: plan de proyecto, cronograma, presupuesto, estrategia de adquisiciones, `plan-etapa-2.md` (`autorizar-proyecto` + `autorizar-etapa`); límite de etapa: informe de fin de etapa, `plan-etapa-<n+1>.md`, business case y plan de proyecto actualizados (`autorizar-etapa`); tras excepción: `plan-excepcion-X-###.md` (`autorizar-plan-excepcion`); plan que no entra: opciones cuantificadas (`decision-ad-hoc`).
- **Prohibido:** `estado.py puerta`, `aprobar` y `tolerancia`.

#### pm-control
- **Bucle por período de informe:** pm-estado-proyecto (`ver`, `registro.py resumen --json`) → pm-integraciones (instantánea y conciliación) → pm-bmad-puente (`backlog`, `avance`, `verificar`) → pm-reuniones → pm-paquetes-trabajo → pm-registros, pm-riesgos, pm-issues-cambios → pm-calidad → pm-progreso-reportes (`evm.py` con tolerancias de etapa y proyecto) → pm-agil-hibrido → pm-comunicacion-stakeholders, pm-visuales, pm-exportar → pm-plan-etapa-y-limites (proponer `limite-etapa`). Scripts: `estado.py`, `registro.py`, `evm.py`, `bmad.py`, `transcripcion.py`, `okr.py`.
- **Excepción:** aviso temprano como borrador (envío = decisión humana); informe con la plantilla de pm-issues-cambios en `03-control/reportes/<fecha>-informe-excepcion-X-###.md`, `estado.py artefacto informe-excepcion-X-### --estado en-revision`, issue de origen `escalado`; derivar a pm-director. No ejecuta `limite-etapa --excepcion`.
- **Hermes:** perfil natural para un cron diario (registros y acciones vencidas) y semanal (`/pm-sync`, `/pm-reporte highlight`, tablero).

#### pm-cierre
- **Skills, en orden típico:** pm-estado-proyecto (`estado.py cierre` o `cierre --prematuro` si la junta lo decidió y aún no se ejecutó) → pm-cierre-proyecto → pm-bmad-puente (`avance` y `verificar` finales) → pm-adquisiciones (cierre de contratos) → pm-lecciones-aprendidas → pm-reuniones (taller o reunión de aceptación) → pm-caso-de-negocio (caso final y plan de revisión de beneficios) → pm-okr (puntuación final) → pm-comunicacion-stakeholders (notificación, envío = decisión humana) → pm-exportar (`paquete.py listar cierre`).
- **Puerta:** `autorizar-cierre` con `registro-aceptacion`, `informe-fin-proyecto`, `informe-lecciones`, `recomendaciones-seguimiento` y `plan-revision-beneficios` en `en-revision`.

## 4. Skills por agente y fase

Formato de cada ficha: **Produce** (artefactos y ruta), **PRINCE2** (procesos · prácticas), **PMBOK como cómo** (`tecnicas_pmbok`), **Plantillas** (`templates/` de la skill), **Scripts**, **Lee de la fachada** (consultas a `especificacion.py` u otras lecturas de la capa de especificación), **Usar / No** (disparadores de la `description`). La invocación es siempre `/pm-method:<skill>` y `/<skill>`.

### 4.1 Agente pm-orquestador (transversal)

#### pm-orquestador
- **Produce:** plan de secuencia en la respuesta; no escribe artefactos propios.
- **PRINCE2:** SU, DP, IP, CS, MP, SB, CP · las siete prácticas.
- **PMBOK como cómo:** adaptación del enfoque de entrega.
- **Plantillas / scripts:** ninguna plantilla; usa `estado.py ver|siguiente` y `sanidad.py --rapido`. Detalle en `references/guia.md` (§1 modos, §2 plantilla de encargo, §3 presentación de decisiones, §4 secuencias, §5 perfil ágil mínimo).
- **Lee de la fachada:** hace cumplir la regla de fuente única; no consulta datos por sí.
- **Usar:** gestionar proyecto, qué sigue, next step, PRINCE2. **No:** conceptos→pm-knowledge.

#### pm-estado-proyecto
- **Produce:** carpeta y `estado.json`; registro mecánico de puertas, aprobaciones, transiciones, tolerancias, roles e integraciones; registros CSV y diario; WBS validada, cronograma CPM y MSPDI, cálculo EVM, exportados; índice de especificación (caché).
- **PRINCE2:** SU, DP, IP, CS, MP, SB, CP · organizing, plans, risk, issues, progress.
- **PMBOK como cómo:** valor ganado, método del camino crítico, EDT/WBS, gestión de la información del proyecto.
- **Plantillas:** ninguna propia. **Scripts:** `nuevo_proyecto.py`, `estado.py`, `registro.py`, `esquema.py`, `especificacion.py`, `sanidad.py`, `wbs.py`, `cpm.py`, `evm.py`, `exportar.py` (ver §5).
- **Lee de la fachada:** es la dueña de `especificacion.py`.
- **Usar:** crear proyecto, estado, etapa, tolerancias, project state. **No:** decidir puertas→pm-direccion-decisiones.

#### pm-sanidad
- **Produce:** informe `03-control/reportes/<fecha>-sanidad.md`; acciones A-### para los ERROR que requieren trabajo.
- **PRINCE2:** DP, CS, SB, CP · progress, quality, issues.
- **PMBOK como cómo:** auditoría de la información del proyecto.
- **Plantillas:** ninguna. **Scripts:** `sanidad.py --proyecto <dir> [--rapido] [--informe] [--reparar] [--json]`. Familias de hallazgos: INS instalación, EST estado y puertas, ART artefactos, REG registros, ESP especificación y BMAD, INT integraciones. `--reparar` solo agrega columnas de esquema faltantes y reconstruye el índice.
- **Lee de la fachada:** comprueba ids entre capas, cobertura, líneas base contra especificación (ESP-10 = cambio no controlado) y traspasos pendientes.
- **Usar:** sanidad, chequeo, consistencia, doctor, health check, auditoría del proyecto. **No:** auditoría de calidad de productos→pm-calidad.

#### pm-knowledge
- **Produce:** respuestas con cita de archivo y encabezado; ningún artefacto.
- **PRINCE2:** los siete procesos y las siete prácticas.
- **PMBOK como cómo:** catálogo de técnicas y fórmulas como referencia.
- **Plantillas / scripts:** ninguno. Base: ocho archivos en `references/` que se consultan por sección con `grep`, nunca enteros. Precedencia: PRINCE2 (método) > PMBOK (técnica mapeada a PRINCE2) > plantillas (campos) > convenciones del paquete sobre los valores de ejemplo.
- **Lee de la fachada:** no; con BMAD, los requisitos se consultan vía pm-bmad-puente.
- **Usar:** qué es, quién aprueba, qué campos, fórmula, glosario, what is. **No:** producir artefactos→pm-orquestador.

#### pm-visuales
- **Produce:** organigrama, mapa poder/interés (restringido), PBS/WBS, flujo de productos, Gantt, roadmap por etapas, flujo de excepciones, canvas HTML y tablero de avance HTML con vista por actor (`?actor=<Nombre>`). Salidas en `02-planificacion/visuales/`, `01-inicio/canvas-arranque.html` y `03-control/reportes/AAAA-MM-DD-tablero-avance.html`.
- **PRINCE2:** SU, IP, CS, SB, CP · organizing, plans, progress, risk.
- **PMBOK como cómo:** estructuras jerárquicas (WBS, OBS), diagrama de Gantt, roadmap, mapa poder-interés, mapa de calor P×I, burn-up, controles visuales.
- **Plantillas:** `diagramas-mermaid.md`, `canvas-arranque.html`, `tablero-avance.html`. **Scripts:** `wbs.py --mermaid`, `cpm.py --mermaid`, `evm.py --json`, `registro.py listar|resumen`. Motores opcionales: diagram-design, archify, visual-explainer, drawio (siempre con Mermaid de respaldo).
- **Lee de la fachada:** resumen y estados de requisitos, épicas e historias (`… --json`).
- **Usar:** organigrama, mapa de stakeholders, diagrama de la WBS, roadmap visual, tablero, dashboard, vista por actor. **No:** Gantt→pm-cronograma-estimacion; contenido del informe→pm-progreso-reportes.

#### pm-exportar
- **Produce:** `.docx`, `.xlsx`, `.pptx` (o guion Markdown del deck) y ZIP de puerta o cierre con `MANIFIESTO.md`, en `exportados/AAAA-MM-DD-<tipo>-v<n>[-BORRADOR].<ext>`.
- **PRINCE2:** DP, IP, SB, CP · progress, organizing.
- **PMBOK como cómo:** informes de desempeño, gestión de la información del proyecto.
- **Plantillas:** ninguna (formatos en `references/formatos.md`). **Scripts:** `exportar.py docx|xlsx`, `paquete.py listar|puerta|cierre`; opcional skills oficiales docx/xlsx/pptx (`integraciones.export = skills-office`).
- **Lee de la fachada:** no; con BMAD agrega con `--extra` la matriz de trazabilidad y la línea base del PRD.
- **Usar:** exportar a Word, Excel, PowerPoint, paquete de puerta, gate package. **No:** tablero→pm-visuales; informe→pm-progreso-reportes.

#### Comandos asignados al orquestador: pm-ayuda, pm-nuevo, pm-estado
Ver §2. Metadatos: pm-ayuda (transversal, todos los procesos), pm-nuevo (inicio, SU; produce `estado.json` y registros), pm-estado (transversal; DP, CS, SB; solo lectura salvo `avance-bmad.csv`).

### 4.2 Agente pm-director (dirección)

#### pm-direccion-decisiones
- **Produce:** solicitud de decisión `00-direccion/decisiones/AAAA-MM-DD-solicitud-<puerta>.md`; `00-direccion/tolerancias-y-autoridad.md`; evaluación de excepción `…-evaluacion-excepcion-X-###.md`; acta `…-acta-junta-<puerta>.md`; líneas base congeladas en `00-direccion/historial/`; filas en `decisiones.csv` y `puertas[]` de `estado.json` (vía `estado.py`); condiciones como acciones A-###.
- **PRINCE2:** DP, SB, CS, CP · business-case, organizing, plans, issues, progress.
- **PMBOK como cómo:** análisis de alternativas, análisis multicriterio, árbol de decisión con EMV, guardarraíles de IA.
- **Plantillas:** `solicitud-puerta.md`, `tolerancias-y-autoridad.md`, `evaluacion-excepcion.md`, `acta-decision-junta.md`.
- **Scripts:** `estado.py puerta|aprobar|tolerancia|rol|limite-etapa|cierre|cumplir-condiciones`, `registro.py`, `paquete.py listar`, `bmad.py verificar|linea-base`.
- **Lee de la fachada:** con BMAD, `bmad.py verificar` antes de la puerta (desvío = `solicitud-cambio`) y estado del PRD y épicas que exige la puerta.
- **Usar:** aprobar etapa, autorizar proyecto, junta, excepción, board decision, stage gate. **No:** anotar riesgos o issues→pm-registros.

#### pm-okr
- **Produce:** `00-direccion/okr.csv` (O-n ligados a OBJ-n; KR-n.m ligados a B-nn o SM-n), `00-direccion/okr.md`, tabla puntuada `03-control/reportes/<fecha>-okr.md`, instantánea `03-control/fuentes/tability-AAAA-MM-DD.csv` si hay Tability.
- **PRINCE2:** SU, IP, DP, SB, CP · business-case, progress. No es un producto de gestión PRINCE2: lee e ilustra el business case.
- **PMBOK como cómo:** indicadores clave de desempeño, medición de resultados, análisis de tendencias.
- **Plantillas:** `okr.csv`, `okr.md`. **Scripts:** `okr.py <csv> [--plantilla] [--umbrales 0.7,0.4] [--corte AAAA-MM-DD] [--markdown <ruta>] [--json]`. Los umbrales son convención de la práctica OKR, no de PRINCE2 ni del PMBOK.
- **Lee de la fachada:** métricas de éxito SM-n.
- **Invocada también por:** pm-inicio (IP), pm-control (cortes), pm-planificacion (lectura en SB), pm-cierre (puntuación final).
- **Usar:** OKR, objetivos y resultados clave, key results, puntuar OKR, Tability. **No:** beneficios o business case→pm-caso-de-negocio.

#### pm-comunicacion-stakeholders
- **Produce:** matriz `02-planificacion/matriz-comunicaciones.md` (anexo operativo del enfoque de comunicación), comunicados `03-control/reportes/AAAA-MM-DD-comunicado-<tema>.md`, correos de seguimiento, canal y frecuencia en `stakeholders.csv`, envíos anotados en `diario.md`.
- **PRINCE2:** IP, DP, CS, SB, CP · organizing, progress.
- **PMBOK como cómo:** análisis de requisitos de comunicación, matriz de involucramiento actual/deseado, métodos interactivo/empuje/atracción, poder-interés.
- **Plantillas:** `matriz-comunicaciones.md`, `comunicado-por-audiencia.md`, `correo-seguimiento.md`.
- **Scripts:** `registro.py actualizar stakeholders`, `estado.py artefacto`.
- **Lee de la fachada:** no. Fuentes: `decisiones.csv`, informes y actas confirmadas de pm-reuniones.
- **Invocada también por:** pm-inicio (matriz y kickoff), pm-control (versiones por audiencia), pm-cierre (notificación).
- **Usar:** plan de comunicación, communication matrix, comunicado, status email, sprint review. **No:** actas→pm-reuniones; análisis o compromiso de interesados→pm-organizacion-roles.

#### Comando asignado a pm-director: pm-puerta
Ver §2. Metadatos: dirección; DP, SB, CP; business-case, plans, progress; produce `solicitud-<puerta>`.

### 4.3 Agente pm-inicio (SU e IP)

#### pm-mandato-y-brief
- **Produce:** `00-direccion/mandato.md`, `01-inicio/propuesta-proyecto.md`, `01-inicio/project-brief.md`, `01-inicio/canvas-arranque.md`, `01-inicio/declaracion-vision.md`, `01-inicio/roadmap.md`; enfoque de entrega en `estado.json.enfoque_entrega`; lecciones previas en `lecciones.csv`.
- **PRINCE2:** SU, IP · business-case, organizing, plans.
- **PMBOK como cómo:** selección del enfoque de desarrollo, juicio de expertos, elicitación, taller facilitado.
- **Plantillas:** `mandato.md`, `propuesta-proyecto.md`, `project-brief.md`, `canvas-arranque.md`, `declaracion-vision.md`, `roadmap.md`.
- **Scripts:** `estado.py ver|set|artefacto|tolerancia`, `registro.py agregar lecciones`, `especificacion.py`, `bmad.py inventario` (ruta y sha del brief de producto).
- **Lee de la fachada:** proveedor, brief de producto y visión. El project brief cita el brief de producto BMAD por ruta y sha corto, sin copiarlo.
- **Puertas humanas internas:** nivel de formalidad (nivel `gestor`) y enfoque de entrega (ejecutivo o usuario); en perfiles mínimos se combinan.
- **Usar:** mandato, brief, arrancar, kick-off, canvas, visión, mandate, start up. **No:** business case→pm-caso-de-negocio.

#### pm-caso-de-negocio
- **Produce:** `00-direccion/business-case.md` (esquemático en SU, completo en IP, nueva versión en cada fin de etapa; copias en `historial/`), `00-direccion/enfoque-beneficios.md`, `00-direccion/enfoque-sostenibilidad.md`; tolerancias de beneficios y sostenibilidad a nivel proyecto.
- **PRINCE2:** SU, IP, DP, SB, CP · business-case, progress.
- **PMBOK como cómo:** NPV, IRR, payback, ROI, análisis de sensibilidad, análisis de alternativas, EMV, modelo multi-caso.
- **Plantillas:** `business-case.md`, `enfoque-beneficios.md`, `enfoque-sostenibilidad.md`.
- **Scripts:** `estado.py tolerancia --nivel proyecto`, `estado.py artefacto`.
- **Lee de la fachada:** SM-n. Los beneficios B-## citan SM-n y KR por id en la columna "Refs SM / KR".
- **Modos:** `esquematico` (SU), `completo` (IP), `verificar` (puerta), `mantener` (fin de etapa), `confirmar` (cierre).
- **Usar:** caso de negocio, business case, ROI, VAN/NPV, payback, beneficios. **No:** OKR→pm-okr; presupuesto→pm-costos-presupuesto.

#### pm-organizacion-roles
- **Produce:** `00-direccion/estructura-organizativa.md`, `00-direccion/roles/descripcion-rol-<rol>.md`, `01-inicio/analisis-stakeholders.md` (restringido), `stakeholders.csv`, `02-planificacion/matriz-raci.md`, `01-inicio/team-charter.md`, `02-planificacion/plan-compromiso-stakeholders.md`.
- **PRINCE2:** SU, IP, SB · organizing.
- **PMBOK como cómo:** análisis de interesados, cuadrícula poder/interés, matriz RACI, acta del equipo, matriz de evaluación del compromiso.
- **Plantillas:** `estructura-organizativa.md`, `descripcion-rol.md`, `analisis-stakeholders.md`, `matriz-raci.md`, `team-charter.md`, `plan-compromiso-stakeholders.md`.
- **Scripts:** `estado.py rol …`, `estado.py agil cadencia_iteracion_dias=<n>`, `registro.py agregar stakeholders`.
- **Lee de la fachada:** no. Mapea roles ágiles y de BMAD a los del método (el PM de BMAD no es el gestor del proyecto).
- **Puertas humanas internas:** el ejecutivo confirma diseño y nombramientos; el usuario revisa las actitudes antes de guardarlas.
- **Usar:** junta, roles, RACI, interesados, stakeholders, engagement plan, team charter. **No:** plan de comunicación→pm-comunicacion-stakeholders.

#### pm-enfoques-gestion
- **Produce:** en `02-planificacion/enfoques/`: enfoques de calidad, riesgo, issues y cambios, comunicación, datos y tecnología digital, controles de sostenibilidad, y planes subsidiarios de alcance y requisitos, cronograma y costos, recursos y adquisiciones.
- **PRINCE2:** IP, SB · quality, risk, issues, progress, plans, organizing.
- **PMBOK como cómo:** matriz de probabilidad e impacto, EMV, reservas, umbrales de variación, reglas de medición EVM, control de configuración.
- **Plantillas:** `enfoque-calidad.md`, `enfoque-riesgo.md`, `enfoque-issues-cambios.md`, `enfoque-comunicacion.md`, `enfoque-datos-digitales.md`, `enfoque-sostenibilidad-gestion.md`, `plan-gestion-alcance-requisitos.md`, `plan-gestion-cronograma-costos.md`, `plan-gestion-recursos-adquisiciones.md`.
- **Scripts:** `estado.py tolerancia --nivel proyecto`, `registro.py esquema <registro>`, `estado.py artefacto`.
- **Lee de la fachada:** con BMAD, inventario vía pm-bmad-puente; la sección 5.1 del enfoque de cambios fija qué es elaboración progresiva y qué es solicitud de cambio.
- **Usar:** enfoque de riesgos, control de cambios, enfoque de calidad, management approach, subsidiary plan. **No:** PID ensamblado→pm-acta-constitucion.

#### pm-acta-constitucion
- **Produce:** `01-inicio/acta-constitucion.md`; `00-direccion/pid.md` (con copias `historial/pid-vX.Y.md`), con secciones de controles (§7), adaptación (§8) y consistencia (§9).
- **PRINCE2:** IP, DP · business-case, organizing, plans, progress.
- **PMBOK como cómo:** acta de constitución, matriz de alineación, adaptación (tailoring), análisis de consistencia.
- **Plantillas:** `acta-constitucion.md`, `pid.md`.
- **Scripts:** `estado.py artefacto acta-constitucion|pid`, `estado.py tolerancia --nivel proyecto`.
- **Lee de la fachada:** con BMAD, inventario y línea base prevista del PRD vía pm-bmad-puente; el PID cita brief de producto, PRD y arquitectura por ruta y sha.
- **Usar:** acta de constitución, PID, project charter, autorizar proyecto. **No:** enfoques de gestión→pm-enfoques-gestion.

### 4.4 Agente pm-planificacion (Plans, IP, SB)

#### pm-planificacion-por-productos
- **Produce:** `02-planificacion/descripcion-producto-proyecto.md`, `pbs-wbs.md`, `wbs.csv` + `visuales/wbs.md`, `productos/<id>-<nombre>.md`, `flujo-productos.md`, `enunciado-alcance.md`, `diccionario-wbs.md`; solo sin BMAD: `requisitos.md` y `matriz-trazabilidad.md`.
- **PRINCE2:** SU, IP, SB · plans, quality.
- **PMBOK como cómo:** descomposición, regla del 100 %, planificación gradual, elicitación de requisitos, matriz de trazabilidad, MoSCoW.
- **Plantillas:** `descripcion-producto-proyecto.md`, `pbs-wbs.md`, `wbs.csv`, `descripcion-producto.md`, `flujo-productos.md`, `enunciado-alcance.md`, `requisitos.md`, `matriz-trazabilidad.md`, `diccionario-wbs.md`.
- **Scripts:** `wbs.py 02-planificacion/wbs.csv --mermaid 02-planificacion/visuales/wbs.md --diccionario 02-planificacion/diccionario-wbs-esqueleto.md`; `registro.py agregar riesgos` (dependencias externas, con confirmación).
- **Lee de la fachada:** requisitos y cobertura. La columna `ref` de `wbs.csv` lleva ids (FR-n con BMAD, REQ-### sin BMAD).
- **Usar:** alcance, PBS, WBS, EDT, scope, product description. **No:** requisitos con BMAD→pm-bmad-puente.

#### pm-cronograma-estimacion
- **Produce:** `02-planificacion/hoja-estimacion.md`, `actividades.csv`, `cronograma.md` (+ `gantt.md`), `cronograma.xml` (MSPDI, opcional), `03-control/paquetes-trabajo/plan-equipo-<paquete>.md`.
- **PRINCE2:** IP, SB, MP · plans, progress.
- **PMBOK como cómo:** estimación análoga, paramétrica, PERT, ascendente, Delphi, puntos de historia, método del diagrama de precedencias, CPM, nivelación de recursos, compresión del cronograma, reservas de contingencia.
- **Plantillas:** `hoja-estimacion.md`, `actividades.csv`, `cronograma.md`, `plan-equipo.md`.
- **Scripts:** `cpm.py 02-planificacion/actividades.csv --inicio AAAA-MM-DD --mermaid 02-planificacion/gantt.md [--mspdi 02-planificacion/cronograma.xml --titulo "<Proyecto>" --wbs 02-planificacion/wbs.csv]`.
- **Lee de la fachada:** épicas, historias, estados y estimación de gobierno (`listar historias --estado …`).
- **Usar:** estimar, cronograma, camino crítico, Gantt, schedule, critical path. **No:** presupuesto→pm-costos-presupuesto.

#### pm-costos-presupuesto
- **Produce:** `02-planificacion/hoja-costeo.md`, `presupuesto.md` (BAC, reservas por etapa, curva S, caja), `linea-base-costo.csv` (PV); export `exportados/linea-base-costo.xlsx` bajo demanda.
- **PRINCE2:** IP, SB · plans, risk, progress, business-case.
- **PMBOK como cómo:** estimación ascendente, paramétrica, análoga, PERT, agregación de costos, análisis de reservas, EMV, curva S, conciliación del límite de financiación, valor ganado.
- **Plantillas:** `hoja-costeo.md`, `presupuesto.md`, `linea-base-costo.csv`.
- **Scripts:** `wbs.py 02-planificacion/wbs.csv` (consolidación), `exportar.py xlsx`, `evm.py --modo agil --pct-no-must` (lectura ágil).
- **Regla de reservas (SPEC §1.10.6):** BAC = Σ paquetes base + contingencia; reserva de gestión fuera del BAC; presupuesto autorizado = BAC + reserva de gestión.
- **Lee de la fachada:** épicas e historias por release.
- **Usar:** costear, presupuesto, BAC, contingencia, reserva de gestión, budget, cost baseline. **No:** business case→pm-caso-de-negocio.

#### pm-plan-etapa-y-limites
- **Produce:** `02-planificacion/plan-etapa-1.md` (iniciación), `plan-proyecto.md`, `plan-etapa-<n>.md`, `03-control/reportes/<fecha>-informe-fin-etapa-<n>.md`, `02-planificacion/plan-excepcion-X-###.md`; lecciones de la etapa; business case y plan de proyecto actualizados (vía sus dueñas).
- **PRINCE2:** SU, IP, SB, DP · plans, progress, business-case, risk.
- **PMBOK como cómo:** integración de planes subsidiarios, criterios de salida, análisis de variación y pronóstico.
- **Plantillas:** `plan-etapa.md`, `plan-proyecto.md`, `informe-fin-etapa.md`, `plan-excepcion.md`.
- **Scripts:** `estado.py artefacto|limite-etapa`, `especificacion.py resumen`, `bmad.py verificar`, `registro.py agregar lecciones`.
- **Lee de la fachada:** historias y épicas de la etapa y cobertura; con BMAD, el gate de sprint planning (PASS/CONCERNS/FAIL) es insumo de `autorizar-etapa`.
- **Usar:** plan de etapa, fin de etapa, stage plan, end stage report. **No:** cronograma→pm-cronograma-estimacion; costos→pm-costos-presupuesto.

#### pm-agil-hibrido
- **Produce:** `02-planificacion/backlog.csv` (columnas de gobierno), `02-planificacion/historias/<id>-<slug>.md` (sin BMAD), `02-planificacion/release-plan.md` (cadencia, DoD/DoR, ceremonias, línea base), `03-control/reportes/<fecha>-retrospectiva-S<k>.md`; swaps del PO y acciones de retro en registros.
- **PRINCE2:** IP, CS, MP, SB · plans, progress, quality, issues.
- **PMBOK como cómo:** backlog priorizado, MoSCoW, planning poker, velocidad, release planning, burn-up, Kanban, DoD/DoR, EVM adaptativo, retrospectiva.
- **Plantillas:** `backlog.csv`, `historia-usuario.md`, `release-plan.md`, `retrospectiva.md`.
- **Scripts:** `bmad.py backlog`, `bmad.py handoff` (sin `--cambio`, para prioridades), `bmad.py avance`, `evm.py --modo agil --pct-no-must`, `registro.py agregar decisiones --campo nivel=product-owner`.
- **Lee de la fachada:** épicas, historias y estados.
- **Usar:** backlog, sprint, user story, release plan, DoD, velocity. **No:** sync con BMAD→pm-bmad-puente.

#### pm-adquisiciones
- **Produce:** en `02-planificacion/adquisiciones/`: estrategia (incluye hacer o comprar), `<id>-criterios-seleccion.md`, `<id>-rfp.md`; `03-control/reportes/AAAA-MM-DD-estado-contratista-<id>.md`, `…-auditoria-adquisiciones-<id>.md`; `03-control/registros/contratos.md`, `reclamaciones.md`; `04-cierre/cierre-contrato-<id>.md`.
- **PRINCE2:** IP, CS, MP, SB, CP · organizing, plans, quality, risk, issues.
- **PMBOK como cómo:** análisis de hacer o comprar, tipos de contrato, documentos de licitación, criterios de selección ponderados, conferencia de oferentes, administración de reclamaciones, resolución alternativa de disputas, auditoría de adquisiciones.
- **Plantillas:** `estrategia-adquisiciones.md`, `criterios-seleccion.md`, `informe-estado-contratista.md`, `auditoria-adquisiciones.md`, `cierre-contrato.md`.
- **Scripts:** `estado.py aprobar estrategia-adquisiciones|cierre-contrato-<id>` (tras decisión humana), `registro.py agregar decisiones`.
- **Lee de la fachada:** con BMAD, el enunciado del trabajo cita ids del PRD.
- **Usar:** proveedor, licitación, RFP, contrato, procurement, vendor. **No:** costo del plan→pm-costos-presupuesto.

#### pm-bmad-puente
- **Produce (todo derivado o de gobierno, nunca en BMAD):** `02-planificacion/especificacion/inventario-bmad.json`, `requisitos-bmad.csv`, `matriz-trazabilidad-bmad.csv`, `spec-index.json`, `handoff-bmad-<fecha>-<…>.md`; columnas derivadas de `backlog.csv`; `03-control/reportes/avance-bmad.csv`; líneas base `00-direccion/historial/bmad-<art>-v<ver>/` (las fija pm-director).
- **PRINCE2:** IP, CS, MP, SB, DP · plans, quality, issues, progress.
- **PMBOK como cómo:** matriz de trazabilidad de requisitos, control de alcance, burn-up.
- **Plantillas:** ninguna. **Scripts:** `bmad.py --proyecto <dir> [--raiz <repo>] detectar|inventario|requisitos|trazabilidad [--wbs …]|backlog|avance|linea-base …|verificar [--marcar-vistas]|indice|handoff [--cambio C-###]`.
- **Lee de la fachada:** es el proveedor de la fachada cuando `integraciones.especificacion = bmad`; el único componente que lee BMAD. Compatibilidad declarada: BMAD v4 y v6.11–v6.12.
- **Usar:** BMAD, PRD, requisitos FR, trazabilidad, sprint-status, línea base del PRD. **No:** escribir el PRD→BMAD; requisitos sin BMAD→pm-planificacion-por-productos.

### 4.5 Agente pm-control (CS y MP)

#### pm-paquetes-trabajo
- **Produce:** `03-control/paquetes-trabajo/WP-nnn-<nombre>.md` (con bloque Acuerdo / Agreement), `WP-nnn-plan-equipo.md`, `03-control/reportes/AAAA-MM-DD-product-status-account.md`, `…-estado-paquetes.md`; actividades en `calidad.csv`; autorización, aceptación y recepción en `decisiones.csv`.
- **PRINCE2:** CS, MP · plans, quality, progress, organizing.
- **PMBOK como cómo:** porcentaje completado, burn-down, gestión del equipo, seguridad psicológica.
- **Plantillas:** `paquete-trabajo.md`, `product-status-account.md`.
- **Scripts:** `registro.py agregar calidad|decisiones`, `estado.py artefacto`.
- **Lee de la fachada:** historias del sprint o épica del paquete (`listar historias --epica <E>`); el alcance del WP son ids, sin copiar texto.
- **Usar:** autorizar paquete, work package, plan de equipo, recibir paquete, sprint como paquete, team plan. **No:** plan de etapa→pm-plan-etapa-y-limites.

#### pm-registros
- **Produce:** filas en los nueve CSV de `03-control/registros/` (riesgos, issues, cambios, decisiones, supuestos, lecciones, stakeholders, calidad, acciones) y `diario.md`; resumen del período con ids.
- **PRINCE2:** SU, IP, CS, MP, SB, CP · risk, issues, progress, quality, organizing.
- **PMBOK como cómo:** análisis de supuestos, cinco porqués, registros y bitácoras, puntuación P×I.
- **Plantillas:** `diario.md`, `guia-registros.md` (columnas y valores; coincide con `esquema.py`).
- **Scripts:** `registro.py --proyecto <dir> agregar|actualizar|listar [--abiertos]|resumen [--corte AAAA-MM-DD]|esquema <registro>`.
- **Lee de la fachada:** no; un desvío del PRD se registra como `solicitud-cambio` citando ids.
- **Usar:** registrar, anotar, acción, supuesto, RAID, action log. **No:** riesgos→pm-riesgos; issues/cambios→pm-issues-cambios.

#### pm-riesgos
- **Produce:** `riesgos.csv`; `02-planificacion/enfoques/evaluacion-probabilidad-impacto.md`; `03-control/registros/R-###-hoja-riesgo.md`; `03-control/reportes/<fecha>-informe-riesgos.md` y `…-auditoria-riesgos.md`; acciones de respuesta en `acciones.csv`.
- **PRINCE2:** SU, IP, CS, MP, SB, CP · risk, business-case, progress.
- **PMBOK como cómo:** matriz probabilidad-impacto, valor monetario esperado, árbol de decisiones, Monte Carlo, pre-mortem, auditoría de riesgos.
- **Plantillas:** `evaluacion-probabilidad-impacto.md`, `hoja-riesgo.md`, `informe-riesgos.md`, `auditoria-riesgos.md`.
- **Scripts:** `registro.py agregar|actualizar riesgos` (recalcula P×I y EMV), `registro.py resumen --json`.
- **Lee de la fachada:** AD-n, NFR y preguntas abiertas del PRD, citados por id como fuente de riesgo.
- **Usar:** riesgo, risk register, matriz P×I, EMV, respuesta al riesgo, oportunidad, informe o auditoría de riesgos. **No:** issue ya ocurrido→pm-issues-cambios.

#### pm-issues-cambios
- **Produce:** `issues.csv`, `cambios.csv`; `03-control/reportes/<fecha>-solicitud-cambio-C-###.md`, `…-informe-issue-I-###.md`, `…-informe-excepcion-X-###.md` (plantilla única del paquete); origen del traspaso a BMAD.
- **PRINCE2:** CS, MP, SB, DP · issues, progress, quality, business-case.
- **PMBOK como cómo:** análisis de impacto, cinco porqués, causa-efecto, análisis de red, análisis multicriterio, gestión de configuración.
- **Plantillas:** `solicitud-cambio.md`, `informe-issue.md`, `informe-excepcion.md`.
- **Scripts:** `registro.py agregar|actualizar issues|cambios|decisiones`, `bmad.py handoff --cambio C-###`, `bmad.py verificar`.
- **Lee de la fachada:** ids afectados e historias; desvíos que informa `bmad.py verificar`.
- **Usar:** issue, solicitud de cambio, change request, off-spec, concesión, desvío del PRD. **No:** pronóstico o semáforo→pm-progreso-reportes.

#### pm-progreso-reportes
- **Produce:** `03-control/reportes/<fecha>-checkpoint-WP-###.md`, `<fecha>-highlight-report.md`, `<fecha>-analisis-*.md`, `progreso.csv`; usa `avance-bmad.csv`; acciones correctivas en `acciones.csv`; detecta la excepción y usa la plantilla de pm-issues-cambios.
- **PRINCE2:** CS, MP, DP · progress, risk, issues, quality.
- **PMBOK como cómo:** valor ganado, análisis de variaciones, pronóstico EAC, burn-down, burn-up, velocidad, cronograma ganado.
- **Plantillas:** `informe-avance-equipo.md`, `checkpoint-report.md`, `highlight-report.md`, `analisis-variaciones.md`, `analisis-valor-ganado.md`, `progreso.csv`.
- **Scripts:** `evm.py --csv progreso.csv --bac … --tol-costo … --tol-plazo … [--proyecto <dir>] [--modo agil --pct-no-must …]`, `registro.py resumen --json --corte …`, `bmad.py verificar|avance`.
- **Semáforo:** verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo fuera (excepción).
- **Lee de la fachada:** estados de historias y épicas; serie histórica en `avance-bmad.csv`.
- **Usar:** checkpoint, highlight report, status report, valor ganado, EVM, burn-up, pronóstico. **No:** tablero o gráficos→pm-visuales.

#### pm-calidad
- **Produce:** `calidad.csv`; `03-control/reportes/AAAA-MM-DD-revision-calidad-<producto>.md`; aceptación intermedia `…-aceptacion-<producto>.md` y del proyecto `04-cierre/registro-aceptacion.md`; `…-auditoria-calidad.md`; `02-planificacion/costo-calidad.md`; DoD/DoR en el enfoque de calidad.
- **PRINCE2:** IP, CS, MP, SB, CP · quality, plans, issues.
- **PMBOK como cómo:** inspección, pruebas, auditoría de calidad, costo de la calidad, gráficos de control, definición de hecho, matriz de trazabilidad.
- **Plantillas:** `revision-calidad.md`, `registro-aceptacion.md`, `auditoria-calidad.md`.
- **Scripts:** `registro.py agregar|actualizar calidad`, `estado.py aprobar aceptacion-<producto> --nivel gestor|junta` (tras decisión humana).
- **Lee de la fachada:** criterios por historia, NFR y cobertura (`listar requisitos|historias`); la cobertura `terminado` es la evidencia por requisito; `done` en BMAD no sustituye la aceptación.
- **Usar:** registro de calidad, revisión de calidad, criterios de aceptación, aceptar producto, quality audit, DoD. **No:** off-spec o concesión→pm-issues-cambios.

#### pm-reuniones
- **Produce:** `03-control/reuniones/<fecha>-<reunion>-transcripcion.md`, `<fecha>-acta-<reunion>.md`, `<fecha>-clima-<equipo>.md` (solo agregado, con consentimiento); filas en registros tras confirmar el acta; instantánea `03-control/fuentes/<sistema>-AAAA-MM-DD.md` si la transcripción viene de una herramienta conectada.
- **PRINCE2:** DP, CS, MP, SB, CP · progress, issues, risk, organizing.
- **PMBOK como cómo:** reuniones, gestión de la información del proyecto, habilidades interpersonales y de equipo.
- **Plantillas:** `acta-reunion.md`, `analisis-clima-equipo.md`.
- **Scripts:** `transcripcion.py <fuente .vtt|.srt|.txt|.docx> --salida <ruta> [--anonimizar] [--json] [--idioma es|en]`, `registro.py agregar acciones|riesgos|issues|decisiones|lecciones`.
- **Lee de la fachada:** no.
- **Usar:** acta, minuta, transcripción, minutes, meeting notes, clima del equipo. **No:** matriz de comunicación→pm-comunicacion-stakeholders.

#### pm-integraciones
- **Produce:** instantáneas fechadas `03-control/fuentes/<sistema>-AAAA-MM-DD.<csv|md|json>`; mapa de capacidades en `estado.json.integraciones`; ids externos en `notas` o `diario.md` tras una escritura confirmada.
- **PRINCE2:** CS, MP, SB, DP · progress, issues, organizing.
- **PMBOK como cómo:** gestión de la información del proyecto, comunicaciones.
- **Plantillas:** ninguna (formatos en `references/guia.md` §3). **Scripts:** `estado.py integracion tracker=… chat=… docs=… reuniones=… okr=…`.
- **Capacidades:** tracker, docs, chat, correo, calendario, reuniones, okr. No trae conectores ni credenciales; trabaja con los MCP presentes en la sesión.
- **Lee de la fachada:** no.
- **Usar:** sincronizar Jira, publicar en Slack/Teams, traer issues, sync. **No:** BMAD→pm-bmad-puente; transcripciones→pm-reuniones.

#### Comandos asignados a pm-control: pm-reporte, pm-sync
Ver §2. Metadatos: pm-reporte (control; CS, MP; progress, issues; técnicas: análisis del valor ganado, análisis de variación), pm-sync (control; CS, MP; progress, issues; produce `backlog.csv`, `avance-bmad.csv` e instantáneas).

### 4.6 Agente pm-cierre (CP)

#### pm-cierre-proyecto
- **Produce:** en `04-cierre/`: `registro-aceptacion.md` (por requisito), `handover.md`, `recomendaciones-seguimiento.md`, `plan-revision-beneficios.md`, `informe-fin-proyecto.md`, `notificacion-cierre.md`, product status account final e inventario de cierre prematuro.
- **PRINCE2:** CP, DP · business-case, quality, risk, issues, progress.
- **PMBOK como cómo:** reseña posterior a la acción, análisis de variaciones, valor ganado, matriz de trazabilidad de requisitos.
- **Plantillas:** `handover.md`, `informe-fin-proyecto.md`, `notificacion-cierre.md`, `plan-revision-beneficios.md`, `recomendaciones-seguimiento.md` (usa también `registro-aceptacion.md` de pm-calidad y `product-status-account.md` de pm-paquetes-trabajo).
- **Scripts:** `estado.py cierre [--prematuro]`, `registro.py resumen|listar|actualizar`, `paquete.py listar cierre`, `bmad.py verificar`.
- **Lee de la fachada:** cobertura `terminado` por requisito (`listar requisitos`).
- **Usar:** cerrar proyecto, cierre prematuro, closeout, end project report. **No:** lecciones→pm-lecciones-aprendidas.

#### pm-lecciones-aprendidas
- **Produce:** `lecciones.csv`; `03-control/reportes/AAAA-MM-DD-retrospectiva-etapa-<n>.md`; `…-informe-lecciones-etapa-<n>.md`; `04-cierre/informe-lecciones.md`; `04-cierre/propuesta-mejora-organizacion.md`.
- **PRINCE2:** SU, IP, CS, MP, SB, CP · progress, quality, risk, issues.
- **PMBOK como cómo:** retrospectiva, reseña posterior a la acción, autopsia en curso, votación por puntos.
- **Plantillas:** `retrospectiva-etapa.md`, `informe-lecciones.md`.
- **Scripts:** `registro.py agregar|actualizar|listar lecciones`, `estado.py aprobar informe-lecciones` (tras la revisión).
- **Estados válidos de una lección:** `registrada`, `revisada`, `accionada-proyecto`, `accionada-organizacion`, `descartada`.
- **Lee de la fachada:** no.
- **Usar:** lección aprendida, lessons learned, lessons report, retro de etapa. **No:** retro de sprint→pm-agil-hibrido.

### 4.7 Reparto por agente (control de totales)

| Agente (`metadata.agente`) | Skills | Total |
|---|---|---|
| pm-orquestador | pm-orquestador, pm-estado-proyecto, pm-sanidad, pm-knowledge, pm-visuales, pm-exportar · comandos pm-ayuda, pm-nuevo, pm-estado | 9 |
| pm-director | pm-direccion-decisiones, pm-okr, pm-comunicacion-stakeholders · comando pm-puerta | 4 |
| pm-inicio | pm-mandato-y-brief, pm-caso-de-negocio, pm-organizacion-roles, pm-enfoques-gestion, pm-acta-constitucion | 5 |
| pm-planificacion | pm-planificacion-por-productos, pm-cronograma-estimacion, pm-costos-presupuesto, pm-plan-etapa-y-limites, pm-agil-hibrido, pm-adquisiciones, pm-bmad-puente | 7 |
| pm-control | pm-paquetes-trabajo, pm-registros, pm-riesgos, pm-issues-cambios, pm-progreso-reportes, pm-calidad, pm-reuniones, pm-integraciones · comandos pm-reporte, pm-sync | 10 |
| pm-cierre | pm-cierre-proyecto, pm-lecciones-aprendidas | 2 |
| **Total** | 31 invocables por el modelo + 6 comandos | **37** |

`metadata.agente` indica el agente dueño habitual. Varias skills se invocan desde más de un agente (por ejemplo, pm-okr desde pm-inicio, pm-control, pm-planificacion y pm-cierre; pm-comunicacion-stakeholders desde los cuatro agentes de fase; pm-riesgos desde pm-inicio y pm-planificacion). Las fichas de agentes de §3.3 dan el orden real.

## 5. Scripts

### 5.1 Scripts compartidos (`<pm-estado-proyecto>/scripts/`)

| Script | Para qué | Comandos (sintaxis real de `--help`) |
|---|---|---|
| `nuevo_proyecto.py` | Crea la carpeta de SPEC §1.5, los nueve CSV, el diario y `estado.json` en `pre-proyecto`/SU/etapa 0. No sobrescribe. | `nuevo_proyecto.py --ruta <dir> --nombre "<nombre>" [--idioma es\|en] [--enfoque predictivo\|agil\|hibrido] [--ejecutivo ".."] [--gestor ".."]` |
| `estado.py` | Única vía de escritura de `estado.json`. | `estado.py --proyecto <dir> ver` · `siguiente` · `set clave=valor …` · `tolerancia [--nivel proyecto\|etapa] tiempo=".." costo=".." …` · `rol clave=".." …` · `agil clave=..` · `umbrales-riesgo alto=.. medio=..` · `integracion especificacion=bmad tracker=.. …` · `etapa --numero N --nombre ".." [--inicio ..] [--fin ..]` · `artefacto <clave> --ruta <ruta> [--estado borrador\|en-revision\|aprobado\|obsoleto] [--version x.y]` · `aprobar <clave> --por "<rol: nombre>" [--version ..] [--fecha ..] [--nivel equipo\|product-owner\|gestor\|autoridad-cambio\|junta\|capa-negocio]` · `puerta <autorizar-inicio\|autorizar-proyecto\|autorizar-etapa\|autorizar-plan-excepcion\|autorizar-cierre\|decision-ad-hoc> --decision aprobado\|condicionado\|rechazado\|pendiente --por "<rol: nombre>" [--condiciones ..] [--fecha ..] [--etapa-nombre ..] [--fin ..] [--forzar]` · `cumplir-condiciones <tipo>` · `limite-etapa [--excepcion X-###]` · `cierre [--prematuro]` |
| `registro.py` | Alta, actualización, listado y resumen de los nueve registros, validados contra `esquema.py`; acepta alias en inglés. No borra filas. | `registro.py --proyecto <dir> agregar <registro> --campo k=v … [--forzar]` · `actualizar <registro> <id> --campo k=v …` · `listar <registro> [--estado ..] [--abiertos] [--json]` · `resumen [--json] [--corte AAAA-MM-DD]` · `esquema <registro>` |
| `esquema.py` | Fuente única de columnas, valores y prefijos de registros (R, I, C, D, S, L, ST, Q, A). | Módulo usado por `registro.py` y `sanidad.py` |
| `especificacion.py` | Fachada única de especificación (contrato `pm-spec-index/1`, caché invalidada por huella sha256). | `especificacion.py --proyecto <dir> fuente` · `resumen [--json]` · `consultar FR-3\|REQ-004\|1-2-login\|E-2 [--json]` · `listar requisitos\|historias\|epicas [--estado done] [--epica E-1] [--cobertura sin-cobertura\|planificado\|en-curso\|terminado] [--json]` · `indice` |
| `sanidad.py` | Controles de consistencia (INS, EST, ART, REG, ESP, INT). Código de salida 1 si hay ERROR. | `sanidad.py --proyecto <dir> [--rapido] [--informe] [--reparar] [--json]` |
| `wbs.py` | Valida la EDT (regla del 100 %), consolida esfuerzo y costo y dibuja el árbol Mermaid. | `wbs.py 02-planificacion/wbs.csv [--titulo ..] [--mermaid 02-planificacion/visuales/wbs.md] [--diccionario 02-planificacion/diccionario-wbs-esqueleto.md] [--json] [--profundidad N] [--idioma es\|en]` |
| `cpm.py` | Camino crítico, holguras, carga por recurso, Gantt Mermaid y MS Project XML (MSPDI, validado leyéndolo con MPXJ). | `cpm.py 02-planificacion/actividades.csv [--inicio AAAA-MM-DD] [--mermaid <ruta>] [--json] [--mspdi 02-planificacion/cronograma.xml] [--titulo ".."] [--wbs 02-planificacion/wbs.csv]` |
| `evm.py` | Valor ganado con semáforo contra tolerancias y modo ágil. | `evm.py --bac N [--pv N --ev N --ac N \| --csv progreso.csv] [--eac tendencia\|atipico\|compuesto] [--tol-costo %] [--tol-plazo %] [--modo predictivo\|agil] [--pct-no-must %] [--idioma es\|en] [--proyecto <dir>] [--json]` |
| `exportar.py` | Markdown → `.docx` (banda BORRADOR si no está aprobado) y CSV → `.xlsx`. | `exportar.py docx --entrada <md> --salida exportados/<nombre>.docx` · `exportar.py xlsx --proyecto <dir> --salida exportados/AAAA-MM-DD-registros-v<n>.xlsx` (o `--entrada <csv>`) |

### 5.2 Scripts de otras skills

| Script | Para qué | Comandos |
|---|---|---|
| `<pm-bmad-puente>/scripts/bmad.py` | Puente de solo lectura con BMAD (v4 y v6.11–v6.12); proveedor de la fachada. | `bmad.py --proyecto <dir> [--raiz <repo>] detectar` · `inventario [--json]` · `requisitos` · `trazabilidad [--wbs 02-planificacion/wbs.csv]` · `backlog` · `avance [--json]` · `linea-base prd\|arquitectura\|epicas\|brief\|ux --version X.Y --por "<rol: nombre>"` · `verificar [--json] [--marcar-vistas]` · `indice` · `handoff [--cambio C-###]` |
| `<pm-okr>/scripts/okr.py` | Valida vínculos de KR y los puntúa. | `okr.py <dir>/00-direccion/okr.csv [--plantilla] [--umbrales 0.7,0.4] [--corte AAAA-MM-DD] [--markdown <ruta>] [--json]` |
| `<pm-reuniones>/scripts/transcripcion.py` | Normaliza transcripciones VTT, SRT, TXT o DOCX. | `transcripcion.py <entrada> [--salida <ruta>] [--anonimizar] [--json] [--idioma es\|en]` |
| `<pm-exportar>/scripts/paquete.py` | Lista obligatorios y arma ZIP de puerta o cierre con manifiesto. | `paquete.py --proyecto <dir> listar puerta <tipo>` · `listar cierre` · `puerta autorizar-inicio\|autorizar-proyecto\|autorizar-etapa\|autorizar-plan-excepcion [--salida ..] [--extra <ruta> …]` · `cierre [--salida ..] [--extra <ruta> …]` |

### 5.3 Scripts del mantenedor y hooks

| Componente | Cuándo | Qué hace |
|---|---|---|
| `scripts/validar_paquete.py` | Tras cualquier cambio del paquete | Estructura, tamaños, formato y presupuesto de descripciones, referencias, agentes (herencia de herramientas, sin anidación), cobertura de orquestación y hooks. Última corrida: `Skills: 37 (31 invocables por el modelo, listado 6160 caracteres) · Agentes: 6 · OK`. |
| `scripts/probar_paquete.py [--conservar]` | Tras cambios del paquete o de BMAD | Regresión de punta a punta con BMAD v6, BMAD v4 y sin BMAD, incluida la sanidad con defectos sembrados (35 pruebas OK). Requiere PyYAML. Fixtures en `scripts/pruebas/fixtures/`. |
| `hooks/guardian.py` (PreToolUse sobre Write, Edit, MultiEdit, NotebookEdit y Bash) | Cada escritura | Niega editar a mano `estado.json`, los registros CSV, los derivados de `02-planificacion/especificacion/` y las copias congeladas de `00-direccion/historial/`; impide a los subagentes pm-* escribir en `_bmad/`, `_bmad-output/` o `.bmad-core/`. |
| `hooks/inicio.py` (SessionStart: startup, resume, clear, compact) | Al abrir, retomar, limpiar o compactar | Agrega al contexto la fase, las puertas y los ERROR de la sanidad rápida. |

Los hooks solo corren en Claude Code con el plugin instalado; en Hermes no hay equivalente documentado.
