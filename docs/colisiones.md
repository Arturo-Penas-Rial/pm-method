# Dueños únicos, colisiones y enrutamiento · Owners, collisions and routing

Cada tema del paquete tiene una sola skill dueña; las demás la invocan o la nombran en su pista "No:". Este documento reúne la matriz de dueños, la pista de alcance de cada skill, los pares que más se confunden y la evaluación de enrutamiento con la forma de repetirla. `SPEC.md` §1.3 y §1.14 remiten aquí.

## 1. Por qué importa

Claude Code decide qué skill activar leyendo solo el `name` y la `description` de cada skill del listado. Ese listado ocupa presupuesto de contexto en todas las sesiones (≈ 1 % de la ventana). Por eso cada `description` sigue un formato fijo de una línea y hasta 240 caracteres (SPEC §1.3):

`<Objeto que produce o decide>. Usar: <4–7 disparadores ES/EN>. No: <tema vecino>→<skill dueña>.`

- El objeto va primero, sin procedimiento.
- "Usar:" lleva disparadores concretos en español y en inglés.
- "No:" es la pista de alcance (scope clue): nombra la colisión más probable y a qué skill corresponde.
- Los seis comandos (`pm-ayuda`, `pm-nuevo`, `pm-estado`, `pm-reporte`, `pm-puerta`, `pm-sync`) llevan `disable-model-invocation: true`: no compiten en el enrutamiento ni consumen presupuesto, y no tienen pista "No:".

**Presupuesto medido.** Las 31 descripciones invocables suman 6.160 caracteres (`validar_paquete.py`; el límite del paquete es 7.500, SPEC §3). Si conviven muchos plugins y el listado se recorta, se puede subir la fracción con `"skillListingBudgetFraction": 0.02` en `settings.json`. `skillOverrides` (`on | name-only | user-invocable-only | off`) no se aplica a skills de plugins.

## 2. Matriz de dueños

Basada en la matriz del refactor v2, con las filas de las skills nuevas (pm-bmad-puente, pm-integraciones, pm-okr, pm-reuniones, pm-sanidad) completadas según sus SKILL.md.

| Tema | Dueña | Vecinas que NO deben activarse (→ dueña de lo vecino) |
|---|---|---|
| Estado del proyecto, registro mecánico de puertas, scripts compartidos | pm-estado-proyecto (ejecuta) / pm-direccion-decisiones (prepara la decisión) | decidir una puerta → pm-direccion-decisiones |
| Decisiones de la junta: puertas, tolerancias, excepciones | pm-direccion-decisiones | anotar riesgos o issues → pm-registros |
| Registros genéricos (supuestos, decisiones operativas, acciones, diario) y clasificación | pm-registros | riesgos → pm-riesgos; issues y cambios → pm-issues-cambios |
| Riesgos | pm-riesgos | issue ya ocurrido → pm-issues-cambios |
| Issues, cambios, concesiones e informe de excepción (plantilla única) | pm-issues-cambios | pronóstico o semáforo → pm-progreso-reportes |
| Informes de avance, EVM, semáforos, detección de excepción | pm-progreso-reportes | tablero o gráficos → pm-visuales |
| Tablero, diagramas, canvas, vista por actor | pm-visuales | contenido del informe → pm-progreso-reportes; Gantt → pm-cronograma-estimacion |
| Plan de proyecto, de etapa y de excepción; fin de etapa | pm-plan-etapa-y-limites | cálculo de cronograma → pm-cronograma-estimacion; costos → pm-costos-presupuesto |
| Estimación, cronograma, CPM, Gantt, MSPDI | pm-cronograma-estimacion | presupuesto → pm-costos-presupuesto |
| Costeo, presupuesto, reservas, BAC, línea base PV | pm-costos-presupuesto | business case → pm-caso-de-negocio |
| Alcance, PBS, WBS (`wbs.py`), descripciones de producto, requisitos y RTM sin BMAD | pm-planificacion-por-productos | requisitos con BMAD → pm-bmad-puente |
| Backlog, historias, release plan, velocidad, swaps del PO, retro de iteración | pm-agil-hibrido | sincronización con BMAD → pm-bmad-puente |
| Business case, beneficios, enfoques de beneficios y sostenibilidad | pm-caso-de-negocio | OKR → pm-okr; presupuesto → pm-costos-presupuesto |
| **OKR** ligados a beneficios (B-n) y métricas de éxito (SM-n), puntuación, Tability | pm-okr | beneficios o business case → pm-caso-de-negocio |
| Matriz de comunicaciones, mensajes por audiencia, seguimiento del compromiso | pm-comunicacion-stakeholders | actas → pm-reuniones; análisis o compromiso de interesados → pm-organizacion-roles |
| **Transcripciones, actas, acciones de reunión, clima agregado** | pm-reuniones | matriz de comunicación → pm-comunicacion-stakeholders |
| Estructura de gestión, roles, RACI, análisis y plan de compromiso de interesados | pm-organizacion-roles | plan de comunicación → pm-comunicacion-stakeholders |
| Enfoques de gestión del PID y planes subsidiarios | pm-enfoques-gestion | PID ensamblado → pm-acta-constitucion |
| Acta de constitución y PID ensamblado | pm-acta-constitucion | enfoques de gestión → pm-enfoques-gestion |
| Mandato, propuesta, brief, canvas, visión, roadmap, enfoque de entrega | pm-mandato-y-brief | business case → pm-caso-de-negocio |
| Paquetes de trabajo y product status account | pm-paquetes-trabajo | plan de etapa → pm-plan-etapa-y-limites |
| Calidad y aceptación de productos | pm-calidad | off-spec o concesión → pm-issues-cambios |
| Adquisiciones y contratos | pm-adquisiciones | costo del plan → pm-costos-presupuesto |
| Lecciones aprendidas, taller de etapa, informe de lecciones | pm-lecciones-aprendidas | retro de sprint → pm-agil-hibrido |
| Cierre planificado o prematuro | pm-cierre-proyecto | lecciones → pm-lecciones-aprendidas |
| Exportados Office y paquetes ZIP | pm-exportar | tablero → pm-visuales; informe → pm-progreso-reportes |
| **Integraciones MCP** (tracker, docs, chat, correo, calendario) | pm-integraciones | BMAD → pm-bmad-puente; transcripciones → pm-reuniones |
| **BMAD** (puente de solo lectura, trazabilidad, línea base, traspaso) | pm-bmad-puente | escribir el PRD → flujos de BMAD; requisitos sin BMAD → pm-planificacion-por-productos |
| **Sanidad y consistencia del ecosistema** | pm-sanidad | auditoría de calidad de productos → pm-calidad |
| Conocimiento del método | pm-knowledge | producir artefactos → pm-orquestador |
| Enrutamiento y conversación con el usuario | pm-orquestador | conceptos → pm-knowledge |

**Dueños únicos de documentos que suelen duplicarse (SPEC §1.10.11).** Comunicación: el enfoque es de pm-enfoques-gestion y la matriz operativa de pm-comunicacion-stakeholders. Alcance: el QUÉ (`enunciado-alcance`, PBS/WBS) es de pm-planificacion-por-productos y el CÓMO (`plan-gestion-alcance-requisitos`) de pm-enfoques-gestion. Informe de excepción: la plantilla es de pm-issues-cambios; pm-progreso-reportes detecta el pronóstico fuera de tolerancia y la usa. Retrospectiva de iteración: pm-agil-hibrido; taller de lecciones de etapa: pm-lecciones-aprendidas. Burn-down y burn-up: en los informes; el release plan guarda solo la línea base.

## 3. Pista "No:" de cada skill invocable

"Usar" y "No" copiados de la `description` vigente. La última columna es el ejemplo de invocación que, según la propia skill, **no** debe activarla.

| Skill | Usar | No | Ejemplo que no la activa → destino |
|---|---|---|---|
| pm-acta-constitucion | acta de constitución, PID, project charter, autorizar proyecto | enfoques de gestión→pm-enfoques-gestion | "Escribí el enfoque de gestión de riesgos" → pm-enfoques-gestion |
| pm-adquisiciones | proveedor, licitación, RFP, contrato, procurement, vendor | costo del plan→pm-costos-presupuesto | "¿Cuánta contingencia lleva el presupuesto de la etapa 3?" → pm-costos-presupuesto |
| pm-agil-hibrido | backlog, sprint, user story, release plan, DoD, velocity | sync con BMAD→pm-bmad-puente | "Sincronizá el backlog con las historias de BMAD" → pm-bmad-puente |
| pm-bmad-puente | BMAD, PRD, requisitos FR, trazabilidad, sprint-status, línea base del PRD | escribir el PRD→BMAD; requisitos sin BMAD→pm-planificacion-por-productos | "Escribí el PRD" → flujo de PRD de BMAD; "listá los requisitos" sin BMAD → pm-planificacion-por-productos |
| pm-calidad | registro de calidad, revisión de calidad, criterios de aceptación, aceptar producto, quality audit, DoD | off-spec o concesión→pm-issues-cambios | "El módulo no cumple el tiempo de respuesta; ¿lo aceptamos como concesión?" → pm-issues-cambios |
| pm-caso-de-negocio | caso de negocio, business case, ROI, VAN/NPV, payback, beneficios | OKR→pm-okr; presupuesto→pm-costos-presupuesto | "Definí los OKR del trimestre y sus resultados clave" → pm-okr |
| pm-cierre-proyecto | cerrar proyecto, cierre prematuro, closeout, end project report | lecciones→pm-lecciones-aprendidas | "Facilitá el taller de lecciones de la etapa 3" → pm-lecciones-aprendidas |
| pm-comunicacion-stakeholders | plan de comunicación, communication matrix, comunicado, status email, sprint review | actas→pm-reuniones; análisis o compromiso de interesados→pm-organizacion-roles | "Acá está la transcripción del comité de hoy; sacame el acta y las acciones" → pm-reuniones |
| pm-costos-presupuesto | costear, presupuesto, BAC, contingencia, reserva de gestión, budget, cost baseline | business case→pm-caso-de-negocio | "Actualizá el ROI y el payback del caso de negocio" → pm-caso-de-negocio |
| pm-cronograma-estimacion | estimar, cronograma, camino crítico, Gantt, schedule, critical path | presupuesto→pm-costos-presupuesto | "¿Cuánto cuesta la etapa 2 con reservas?" → pm-costos-presupuesto |
| pm-direccion-decisiones | aprobar etapa, autorizar proyecto, junta, excepción, board decision, stage gate | anotar riesgos o issues→pm-registros | "Anotá este riesgo del proveedor" → pm-registros (o pm-riesgos para analizarlo) |
| pm-enfoques-gestion | enfoque de riesgos, control de cambios, enfoque de calidad, management approach, subsidiary plan | PID ensamblado→pm-acta-constitucion | "Ensamblá el PID y revisá la consistencia" → pm-acta-constitucion |
| pm-estado-proyecto | crear proyecto, estado, etapa, tolerancias, project state | decidir puertas→pm-direccion-decisiones | "¿Apruebo la etapa 3 o pido más información?" → pm-direccion-decisiones |
| pm-exportar | exportar a Word, Excel, PowerPoint, paquete de puerta, gate package | tablero→pm-visuales; informe→pm-progreso-reportes | "Armá el tablero de avance con semáforos" → pm-visuales |
| pm-integraciones | sincronizar Jira, publicar en Slack/Teams, traer issues, sync | BMAD→pm-bmad-puente; transcripciones→pm-reuniones | "Sincronizá con BMAD" → pm-bmad-puente; "procesá la grabación del comité" → pm-reuniones |
| pm-issues-cambios | issue, solicitud de cambio, change request, off-spec, concesión, desvío del PRD | pronóstico o semáforo→pm-progreso-reportes | "¿Cómo viene el CPI de la etapa y qué semáforo le toca?" → pm-progreso-reportes |
| pm-knowledge | qué es, quién aprueba, qué campos, fórmula, glosario, what is | producir artefactos→pm-orquestador | "Armame el plan de la etapa 3" → pm-plan-etapa-y-limites (vía pm-orquestador) |
| pm-lecciones-aprendidas | lección aprendida, lessons learned, lessons report, retro de etapa | retro de sprint→pm-agil-hibrido | "Hagamos la retro del sprint 7" → pm-agil-hibrido |
| pm-mandato-y-brief | mandato, brief, arrancar, kick-off, canvas, visión, mandate, start up | business case→pm-caso-de-negocio | "Calculá NPV y payback de la opción elegida" → pm-caso-de-negocio |
| pm-okr | OKR, objetivos y resultados clave, key results, puntuar OKR, Tability | beneficios o business case→pm-caso-de-negocio | "Calculá el VAN y el payback del proyecto" → pm-caso-de-negocio |
| pm-organizacion-roles | junta, roles, RACI, interesados, stakeholders, engagement plan, team charter | plan de comunicación→pm-comunicacion-stakeholders | "Prepará el mensaje para el comité y la matriz de comunicaciones" → pm-comunicacion-stakeholders |
| pm-orquestador | gestionar proyecto, qué sigue, next step, PRINCE2 | conceptos→pm-knowledge | "¿Qué es un informe de destacados?" → pm-knowledge |
| pm-paquetes-trabajo | autorizar paquete, work package, plan de equipo, recibir paquete, sprint como paquete, team plan | plan de etapa→pm-plan-etapa-y-limites | "Armá el plan de la etapa 3 con sus tolerancias" → pm-plan-etapa-y-limites |
| pm-plan-etapa-y-limites | plan de etapa, fin de etapa, stage plan, end stage report | cronograma→pm-cronograma-estimacion; costos→pm-costos-presupuesto | "Calculá el camino crítico de la etapa 2" → pm-cronograma-estimacion |
| pm-planificacion-por-productos | alcance, PBS, WBS, EDT, scope, product description | requisitos con BMAD→pm-bmad-puente | "Trazá los FR del PRD de BMAD a los paquetes" → pm-bmad-puente |
| pm-progreso-reportes | checkpoint, highlight report, status report, valor ganado, EVM, burn-up, pronóstico | tablero o gráficos→pm-visuales | "Actualizá el tablero HTML con la vista por actor" → pm-visuales |
| pm-registros | registrar, anotar, acción, supuesto, RAID, action log | riesgos→pm-riesgos; issues/cambios→pm-issues-cambios | "Analizá la probabilidad e impacto de los riesgos y proponé respuestas" → pm-riesgos |
| pm-reuniones | acta, minuta, transcripción, minutes, meeting notes, clima del equipo | matriz de comunicación→pm-comunicacion-stakeholders | "Armá la matriz de comunicaciones para el cliente" → pm-comunicacion-stakeholders |
| pm-riesgos | riesgo, risk register, matriz P×I, EMV, respuesta al riesgo, oportunidad, informe o auditoría de riesgos | issue ya ocurrido→pm-issues-cambios | "Se cayó la API de aduanas ayer y frenó al equipo" → pm-issues-cambios |
| pm-sanidad | sanidad, chequeo, consistencia, doctor, health check, auditoría del proyecto | auditoría de calidad de productos→pm-calidad | "Auditá la calidad del módulo de pagos" → pm-calidad |
| pm-visuales | organigrama, mapa de stakeholders, diagrama de la WBS, roadmap visual, tablero, dashboard, vista por actor | Gantt→pm-cronograma-estimacion; contenido del informe→pm-progreso-reportes | "Redactá el highlight de la quincena con el EVM" → pm-progreso-reportes |

**Comandos (sin pista "No:").** Sus SKILL.md traen igual un ejemplo que no aplica: `/pm-ayuda` no arma informes ("armá el highlight" → `/pm-reporte` o pm-progreso-reportes); `/pm-nuevo` no informa el estado ("¿en qué etapa estamos?" → `/pm-estado`); `/pm-estado` no produce informes ("armá el highlight" → `/pm-reporte`); `/pm-reporte` no dibuja ("dibujá el burn-up" → pm-visuales); `/pm-puerta` no responde "¿qué sigue?" (→ `/pm-estado`); `/pm-sync` no escribe el PRD (→ flujos de BMAD).

## 4. Pares sensibles y criterio para separarlos

| Par | Criterio |
|---|---|
| pm-registros · pm-riesgos · pm-issues-cambios | Prueba de certeza: incierto → riesgo; ocurrido o pedido → issue (cinco tipos). Una tarea con responsable es una acción (A-###) de pm-registros. pm-registros solo anota la fila; el análisis es de pm-riesgos y la decisión de pm-issues-cambios. |
| pm-progreso-reportes · pm-visuales | El contenido (cifras, semáforos, pronóstico, decisiones pedidas) es del informe; el dibujo (tablero HTML, burn-up, mapa de calor) es de pm-visuales, que toma las cifras del informe y de los registros. |
| pm-progreso-reportes · pm-issues-cambios | pm-progreso-reportes detecta que el pronóstico sale de tolerancia; el informe de excepción se escribe con la plantilla de pm-issues-cambios. |
| pm-plan-etapa-y-limites · pm-cronograma-estimacion · pm-costos-presupuesto | El plan integra; el cálculo de fechas (CPM, PERT, Gantt, MSPDI) y el de costos (BAC, reservas, PV) los hacen sus skills. |
| pm-comunicacion-stakeholders · pm-reuniones · pm-organizacion-roles | Matriz y mensajes por audiencia → comunicación; transcripciones, actas y clima → reuniones; análisis, actitudes y plan de compromiso → organización. |
| pm-caso-de-negocio · pm-okr | El business case manda: beneficios, metas y tolerancias viven ahí. Los OKR solo los citan (KR → B-nn o SM-n) y se puntúan; no reemplazan la justificación continua. |
| pm-planificacion-por-productos · pm-bmad-puente | Sin BMAD, los requisitos y la RTM son de pm-planificacion-por-productos. Con BMAD, viven en el PRD; pm-bmad-puente deriva la matriz y pm-planificacion-por-productos solo cita ids en `ref`. |
| pm-agil-hibrido · pm-bmad-puente | Las columnas de gobierno de `backlog.csv` (prioridad, moscow, estimacion, iteracion, release, producto_pbs) son de pm-agil-hibrido; las derivadas las refresca `bmad.py backlog`. |
| pm-integraciones · pm-bmad-puente · pm-reuniones | BMAD no es un MCP: es la capa de especificación (pm-bmad-puente). Una transcripción, venga de archivo o de una herramienta conectada, la procesa pm-reuniones; pm-integraciones solo la trae. |
| pm-sanidad · pm-calidad | La sanidad audita la información del proyecto (estado, puertas, registros, ids, líneas base); la calidad audita productos contra sus criterios. |
| pm-estado-proyecto · pm-direccion-decisiones | La segunda prepara la decisión de la junta; la primera solo registra mecánicamente lo que una persona ya decidió (y lo ejecuta pm-director). |
| pm-knowledge · pm-orquestador | Preguntar ("¿qué es…?", "¿quién aprueba…?") → pm-knowledge; hacer algo → pm-orquestador, que enruta a la skill de fase. |

## 5. Evaluación de enrutamiento

### 5.1 Método
- **Conjunto de prueba:** `docs/evaluacion/frases-enrutamiento.tsv`, 52 frases con tres columnas sin cabecera: `id`, frase tal como la escribiría un usuario, skill esperada. Frases 1–38 y 49–52 en español rioplatense (42); frases 39–48 en inglés (10).
- **Cobertura:** 30 de las 31 skills invocables tienen al menos una frase. Más frases en los temas con vecinos fuertes: pm-reuniones 4; pm-progreso-reportes, pm-cronograma-estimacion y pm-bmad-puente 3 cada una; la mayoría del resto 2 o 1. **pm-sanidad no tiene frases** (se agregó después de armar el conjunto).
- **Evaluación ciega:** el modelo evaluador recibe solo el listado `- <name>: <description>` de las skills invocables (lo mismo que ve Claude Code para decidir) y las frases sin la columna esperada. Para cada frase debe nombrar una única skill. Las respuestas se comparan con la tercera columna.
- **Qué mide y qué no:** mide si las descripciones bastan para separar vecinos. No mide el efecto del contexto de la conversación, de skills de otros plugins ni del recorte del listado si se agota el presupuesto.

### 5.2 Resultados

| Ronda | Modelo | Aciertos |
|---|---|---|
| 1 (descripciones iniciales v2) | Haiku | 49/52 |
| 1 (descripciones iniciales v2) | Sonnet | 49/52 |
| 2 (tras ajustar descripciones) | Haiku | 51/52 |

Después de la ronda 1 se ajustaron descripciones del paquete y se repitió con Haiku. El registro de hechos de la evaluación no detalla qué frases fallaron en cada ronda ni incluye una segunda corrida con Sonnet; repetirla con el procedimiento de 5.3 da ambos datos.

### 5.3 Cómo repetirla

Desde la raíz del paquete:

```bash
cd pm-method
D=$(mktemp -d)

# 1) Listado actual de skills invocables (nombre: descripción), igual al que ve Claude Code
python3 - > "$D/listado.txt" <<'EOF'
import glob, re
for f in sorted(glob.glob("skills/*/SKILL.md")):
    t = open(f, encoding="utf-8").read()
    if "disable-model-invocation: true" in t:
        continue
    n = re.search(r"^name: (.+)$", t, re.M).group(1)
    d = re.search(r'^description: "(.+)"$', t, re.M).group(1)
    print(f"- {n}: {d}")
EOF

# 2) Frases sin la respuesta esperada
cut -f1,2 docs/evaluacion/frases-enrutamiento.tsv > "$D/frases-ciegas.tsv"

# 3) Instrucción para el evaluador
{
  printf '%s\n\n' "Sos el selector de skills de Claude Code. Estas son las skills disponibles (nombre: descripción):"
  cat "$D/listado.txt"
  printf '\n%s\n\n' "Para cada frase, respondé una línea con el id, un tabulador y el nombre de la única skill que debería activarse (o 'ninguna'). Sin otro texto."
  cat "$D/frases-ciegas.tsv"
} > "$D/prompt.txt"

# 4) Correr con cada modelo (alias o nombre completo del modelo)
claude -p --model sonnet "$(cat "$D/prompt.txt")" > "$D/respuestas-sonnet.tsv"

# 5) Puntuar e imprimir los fallos
awk -F'\t' 'NR==FNR{esp[$1]=$3; fr[$1]=$2; next}
  {tot++; if ($2==esp[$1]) ok++; else printf "FALLO %s\t%s\tesperado=%s\tobtenido=%s\n", $1, fr[$1], esp[$1], $2}
  END{printf "Aciertos: %d/%d\n", ok, tot}' docs/evaluacion/frases-enrutamiento.tsv "$D/respuestas-sonnet.tsv"
```

Repetir el paso 4 con el modelo Haiku disponible para comparar. Si la salida del modelo trae líneas extra, filtrarlas antes de puntuar (`grep -P '^\d+\t'`).

**Cuándo repetirla:** cada vez que cambie una `description`, cuando se agregue una skill y cuando se instale el paquete junto a otros plugins con temas parecidos.

**Mejoras pendientes al conjunto de prueba:**
1. Agregar frases para pm-sanidad, por ejemplo "Revisá la sanidad del proyecto antes de la junta" y "Run a health check on the project folder", y su vecina "Auditá la calidad del módulo de pagos" (→ pm-calidad).
2. Agregar frases en inglés para los pares sensibles que hoy solo se prueban en español (registros/riesgos/issues, comunicación/reuniones).
3. Guardar las respuestas de cada corrida junto al TSV, con fecha y modelo, para poder comparar rondas.

### 5.4 Colisiones con skills de otros repositorios

El listado de Claude Code mezcla las skills de todos los plugins y carpetas instaladas. La familia INS de `sanidad.py` revisa la instalación, incluidas las colisiones con skills de otros repositorios (SPEC §1.17); esos hallazgos no bloquean puertas, pero se informan. Ante una colisión real: (a) invocar la skill por su nombre completo (`/pm-method:<skill>`), (b) usar los comandos de uso humano, que no dependen del enrutamiento, o (c) desactivar o acotar la skill ajena en su propio plugin. Las descripciones del paquete no se reescriben para ganarle a una skill de terceros sin repetir la evaluación de 5.3.
