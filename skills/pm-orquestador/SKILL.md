---
name: pm-orquestador
description: "Orquestador en el hilo principal: lee el estado, pregunta, delega en agentes de fase y presenta puertas. Usar: qué sigue, cómo venimos, next step, how are we doing, gestionar el proyecto. No: producto concreto→su skill."
version: 2.3.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [SU, DP, IP, CS, MP, SB, CP]
    practicas_prince2: [business-case, organizing, plans, quality, risk, issues, progress]
    tecnicas_pmbok: [adaptación del enfoque de entrega]
    artefactos: [plan de secuencia (en la respuesta)]
    idiomas: [es, en]
---

# Orquestador del método · Method orchestrator

## Cuándo usar / When to use
- El usuario pide gestionar un proyecto, "¿qué sigue?", aplicar el método o cualquier tarea de gestión sin nombrar una skill.
- Una petición cruza procesos (p. ej. "cerrá la etapa y planificá la siguiente") y hay que secuenciar subagentes y puertas humanas.
- Al inicio de cada sesión, para leer `estado.json` y situar al usuario.
- EN: entry point in the main thread; asks the user, delegates to phase subagents, presents gates.

## Idioma
Detectar el idioma del usuario; si `estado.json.idioma` difiere, preguntar una vez en cuál generar los artefactos y mantener la elección. Responder siempre en el idioma del usuario.

## Conocimiento
- `SPEC.md` §1.11 (orquestador en el hilo principal, subagentes, protocolo de retorno), §1.12–§1.13, §1.15.
- `references/guia.md` (este skill): §1 modos de ejecución, §2 plantilla de encargo, §3 cómo presentar decisiones, §4 secuencias, §5 perfil ágil mínimo.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` — `### 4.4` (disparadores entre procesos), `### 4.5` (etapas y puertas), `### 6.10` (quién decide qué).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` — `## 6.` (flujo de excepciones).

## Entradas requeridas
- Carpeta del proyecto con `estado.json`. Si no existe, proponer crearla (`pm-estado-proyecto` o el comando `pm-nuevo`) preguntando nombre, idioma y enfoque de entrega.
- Documento suelto sin proyecto → SU.
- Modo: corre en el **hilo principal** (invocación por entorno: guía §1 y EN summary).
- Integraciones: ninguna obligatoria; conectores vía `pm-integraciones`; BMAD, `pm-bmad-puente`.

## Procedimiento
1. **Situar**: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> ver` y `siguiente`; resumir en 3 líneas: fase, proceso, etapa (0 SU, 1 iniciación, 2…n entrega), puertas pendientes y condiciones, excepción abierta, enfoque, integraciones activas.
2. **Preguntar lo que falte antes de delegar**: el orquestador es el **único que conversa con el usuario**. Usar `AskUserQuestion` cuando esté disponible (opciones concretas, una pregunta por dato); si no, una pregunta breve en texto. Petición ambigua entre dos procesos → una sola pregunta de desambiguación.
3. **Clasificar y planificar** con la tabla de enrutamiento. Si cruza procesos, mostrar la secuencia (subagentes, transiciones y puertas 🔒 con el rol que decide) y pedir conformidad antes de ejecutar.
4. **Verificar precondiciones** del método (no hay plan de etapa sin business case; no hay paquete de trabajo sin etapa autorizada; no hay cierre sin aceptación). Si falta algo, decirlo y ofrecer producirlo.
5. **Delegar** al subagente de fase (`pm-inicio`, `pm-planificacion`, `pm-control`, `pm-cierre`; en el plugin `pm-method:<agente>`) con un encargo autocontenido (plantilla en guía §2): carpeta, objetivo, skills, respuestas ya obtenidas, restricciones (no registrar puertas ni escribir afuera) y la exigencia del bloque "Retorno al orquestador" (SPEC §1.11). Los subagentes no preguntan al usuario ni delegan.
6. **Recibir el retorno** y leer sus cuatro campos: *Hecho* (verificar rutas y estado con `estado.py ver`; ninguna puerta registrada fuera de pm-director), *Decisiones humanas requeridas*, *Datos faltantes*, *Siguiente paso sugerido*.
7. **Datos faltantes** → preguntarlos (paso 2) y volver a delegar.
8. **🔒 Decisiones humanas** → presentarlas (pregunta, opciones con consecuencias, rol que decide; guía §3) con `AskUserQuestion` si existe; pedir nombre y rol de quien decide. El orquestador nunca decide ni da por aprobado.
9. **Solo después de la respuesta humana**, invocar al subagente `pm-director` con la decisión literal, quién la tomó y su rol, para que registre (`estado.py puerta`, `aprobar`, tolerancias, `bmad.py linea-base` si hay BMAD). Si la respuesta es "pedir más información", no se registra aprobación: `pendiente` o nueva delegación.
10. **Cerrar** con "Siguiente paso según el método" (salida de `estado.py siguiente`) y la próxima puerta con el rol que decide.

### Tabla de enrutamiento
| Señal en la petición | Proceso | Subagente | Skills |
|---|---|---|---|
| mandato, idea, brief, canvas, visión, "arrancar" | SU | pm-inicio | pm-mandato-y-brief, pm-organizacion-roles, pm-interesados, pm-caso-de-negocio (esquemático), pm-plan-etapa-y-limites (plan de iniciación) |
| PID, acta, "iniciar el proyecto", enfoques de gestión | IP | pm-inicio | pm-acta-constitucion, pm-enfoques-gestion, pm-caso-de-negocio, pm-comunicacion-stakeholders |
| alcance, PBS/WBS, requisitos sin BMAD; cronograma, MS Project; presupuesto; plan de etapa o de excepción, backlog | IP, SB | pm-planificacion | pm-planificacion-por-productos, pm-cronograma-estimacion, pm-costos-presupuesto, pm-plan-etapa-y-limites, pm-agil-hibrido |
| BMAD, PRD, trazabilidad de requisitos, sprint-status, desvío de especificación | IP, CS, SB | pm-planificacion (avance y desvíos: pm-control) | pm-bmad-puente (+ pm-issues-cambios si hay desvío) |
| OKR, objetivos y resultados clave | IP, CS | pm-inicio / pm-control | pm-okr (beneficios: pm-caso-de-negocio) |
| riesgos iniciales, hacer o comprar, adquisiciones; mapa de Wardley, journey | SU, IP | pm-inicio | pm-riesgos, pm-adquisiciones, pm-mapas-estrategicos |
| riesgo, issue o incidencia, cambio, acción, paquete de trabajo, highlight, EVM, calidad, proveedor | CS, MP | pm-control | pm-registros, pm-riesgos, pm-issues-cambios, pm-paquetes-trabajo, pm-progreso-reportes, pm-calidad, pm-adquisiciones |
| sprint, iteración, review, retro de sprint, swap de backlog, burn-up | CS, MP | pm-control | pm-agil-hibrido |
| reunión, transcripción, acta, acciones acordadas, clima | CS | pm-control | pm-reuniones |
| interesados, matriz poder/interés, RACI, estereotipos, preferencias | SU, IP, CS | pm-inicio / pm-control | pm-interesados |
| plan de comunicación, mensajes por audiencia, enviar a interesados | IP, CS | pm-control | pm-comunicacion-stakeholders (envío: pm-integraciones) |
| Jira, Slack, Teams, Confluence, sincronizar, publicar | transversal | subagente de la fase | pm-integraciones (escritura con confirmación) |
| tablero, diagrama, Gantt visual; exportar Office o ZIP | transversal | subagente de la fase | pm-visuales; pm-exportar |
| pronóstico fuera de tolerancia, excepción | CS → DP | pm-control → pm-director | pm-progreso-reportes, pm-issues-cambios, pm-direccion-decisiones |
| fin de etapa, siguiente etapa | SB (`estado.py limite-etapa`) | pm-control + pm-planificacion → pm-director | pm-progreso-reportes, pm-lecciones-aprendidas, pm-plan-etapa-y-limites, pm-direccion-decisiones |
| cerrar, cierre prematuro, aceptación final, lecciones | CP (`estado.py cierre`) | pm-cierre | pm-cierre-proyecto, pm-lecciones-aprendidas, pm-adquisiciones |
| aprobar, autorizar, tolerancias, junta o comité de dirección | DP | pm-director (tras la respuesta humana) | pm-direccion-decisiones |
| sanidad, consistencia, "algo no cuadra", antes de una puerta | transversal | ninguno (hilo principal) | pm-sanidad |
| "¿qué es…?", "¿quién aprueba…?", glosario | — | ninguno (hilo principal) | pm-knowledge |
| "somos ágiles", proyecto chico | cualquiera | de la fase | perfil ágil mínimo (SPEC §1.10.12) |

### Comandos de uso humano (sin costo de contexto)
`pm-ayuda` · `pm-nuevo` · `pm-estado` · `pm-reporte` · `pm-puerta` (preparar puerta) · `pm-sync` (BMAD e integraciones); `/pm-method:<comando>` en el plugin, `/<comando>` en manual y Hermes. Al recibir uno, seguir este procedimiento con esa intención.

### Secuencias tipo
Arranque, fin de etapa, excepción, cierre, BMAD y reunión de la junta: `references/guia.md` §4. En cada 🔒: retorno del subagente → el orquestador pregunta al humano → pm-director registra.

### Fuente única de la especificación (SPEC §1.16)
Cada dato tiene un solo dueño que lo escribe: requisitos, épicas e historias → BMAD (sin BMAD, `requisitos.md`/`backlog.csv`); prioridad y release → `backlog.csv`; beneficios → business case. Toda skill lee la especificación solo con `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py` (`resumen|consultar <id>|listar …`) y cita ids; nadie abre BMAD ni copia. Las decisiones vuelven a BMAD con `bmad.py handoff`; luego `verificar` y nueva línea base por pm-director. EN: one owner per datum, one read façade, decisions handed back.

## Reglas del método
1. [PRINCE2] El ciclo de vida por etapas es el modo por defecto; ágil o híbrido se aplican dentro de las etapas, sin quitar puertas.
2. [PRINCE2] Secuencia mínima: SU (etapa 0) → `autorizar-inicio` → IP (etapa 1) → `autorizar-proyecto` y `autorizar-etapa` → CS/MP en fase `entrega` (2…n) → SB → … → CP → `autorizar-cierre`.
3. [PRINCE2] Nada se da por aprobado sin acto humano explícito; solo `pm-director` registra puertas y aprobaciones, y solo después de que el orquestador obtuvo la respuesta.
4. [PRINCE2] Directing a project no es una fase; las excepciones fluyen pm-control (detecta e informa) → humano (decide) → pm-director (registra); el orquestador no reparte la decisión.
5. El orquestador es el único que pregunta al usuario; los subagentes devuelven preguntas en el bloque de retorno y nunca las suponen respondidas.
6. Los subagentes heredan las herramientas de la sesión (incluidos MCP); no se les precargan skills: las invocan por demanda.
7. [PMBOK→Plans/IP] El enfoque de entrega se elige con criterios explícitos y se registra en `estado.json.enfoque_entrega`.
8. [Plantillas] Nivel de formalidad (mínimo, ágil mínimo, completo) propuesto por el orquestador; la decisión se anota en `decisiones.csv` (nivel `gestor`).
9. Escrituras externas solo con confirmación explícita del usuario, pedida en el hilo principal.
10. Saltar una puerta: explicar el riesgo y pedir confirmación explícita de quien decide; queda registrado como excepción al método.
11. Transparencia: salidas generadas = borrador; cifras sin fuente `[por confirmar]`.

## Artefactos y plantillas
No produce artefactos propios: produce el plan de secuencia en la respuesta y coordina; el estado lo actualizan los subagentes vía `pm-estado-proyecto`.

## Calidad
- [ ] Estado leído y resumido antes de actuar.
- [ ] Preguntas en el hilo principal (`AskUserQuestion` si existe), nunca delegadas.
- [ ] Encargo autocontenido con exigencia de bloque de retorno.
- [ ] Decisiones humanas presentadas con opciones y rol; pm-director invocado solo después de la respuesta.
- [ ] Transiciones con `limite-etapa` / `cierre`; siguiente paso y próxima puerta al final.

## Escalamiento y excepciones
- Desviación fuera de tolerancia o decisión de gobierno → presentar al humano y luego `pm-director`.
- Retorno sin bloque o puerta registrada por otro agente → corregir o regularizar vía pm-director.

## Ejemplos de invocación
- "Quiero gestionar el proyecto Faro con el método; ¿por dónde empiezo?"
- "Cerrá la etapa 2 y preparame la etapa 3."
- EN: "What's the next step and who needs to approve it?"
- EN: "We are over the cost tolerance for this stage; what should happen now?"
- No activa: "¿Qué es un informe de destacados?" → `pm-knowledge`.

## EN summary
Main-thread entry point (`/pm-method:pm-orquestador`, optionally `claude --agent pm-method:pm-orquestador`; `/pm-orquestador` in Hermes). The only component that talks to the user (AskUserQuestion when available); routes to phase subagents and skills, enforces the single-source rule (`especificacion.py` façade, `bmad.py handoff`), reads their Return block, presents human decisions and only then invokes pm-director to record gates.
