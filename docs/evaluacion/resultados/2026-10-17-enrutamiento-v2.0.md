> Informe histórico de la prueba en vivo de **pm-method 2.0.0** (2026-10-17). Los defectos que describe se corrigieron en 2.1.0 (ver `CHANGELOG.md` y `docs/PRUEBAS.md`). Las rutas del entorno de prueba se reemplazaron por marcadores.

# Evaluación de enrutamiento EN VIVO · pm-method 2.0.0 (L1)

Fecha: 2026-10-17 · Claude Code 2.1.302 · modelo del hilo: `claude-sonnet-5-5` (por defecto) · plugin cargado con `--plugin-dir <repo>` (sin modificar).

## 1. Método

- **Arnés:** `scripts/pruebas_vivo/vivo.py` (función `analizar` y el mismo comando que `Sesion.turno`: `claude -p … --plugin-dir … --output-format stream-json --verbose --max-turns 4 --dangerously-skip-permissions`). Envoltorio propio `<entorno-de-prueba>/l1/correr.py`: lee el stream en línea, separa hilo principal de subagente y cortaría la corrida poco después de la primera llamada `Agent` (no ocurrió nunca). Puntuación: `<entorno-de-prueba>/l1/puntuar.py`.
- **Aislamiento:** por frase, copia nueva de `<entorno-de-prueba>/base.tgz` (fixture BMAD v6 + proyecto en `base/gestion`, fase inicio/IP, etapa 1), cwd = `base`. Un turno, `max_turns 4`. Lotes de 6 en paralelo.
- **Conjunto:** 54 frases de `docs/evaluacion/frases-enrutamiento.tsv` + 17 propias (`frases-extra.tsv`, ids 55–71; dueña según `docs/colisiones.md`, con columna de alternativas aceptables en casos ambiguos) + 4 de comandos (`slash.tsv`).
- **Veredicto:** OK = la 1.ª skill es la esperada; OK (aceptable) = alternativa documentada; OK (vía orquestador) = pm-orquestador y luego la esperada o un agente de fase dueño; PARCIAL = solo pm-orquestador sin llegar a la dueña; SIN SKILL = respondió directo o fue a Bash.
- **Seguimientos:** (a) repetición de los fallos (10 corridas); (b) los 8 casos de orquestador con `max_turns 14` para ver si delega; (c) **A/B** con una copia del plugin en `<entorno-de-prueba>/l1/variante/` donde solo cambia el texto del hook SessionStart (10 corridas).
- **Costo total:** 103 corridas, **USD 11,26** (principal 75 → 8,18; repetición 10 → 0,92; orquestador largo 8 → 1,03; A/B 10 → 1,12). Costos reales de `total_cost_usd` (ninguna corrida se cortó).

## 2. Resultados globales (71 frases en lenguaje natural)

| Medida | Resultado |
|---|---|
| Acierto (OK + aceptable + vía orquestador) | **58/71 = 81,7 %** |
| Acierto estricto (1.ª skill = esperada) | 56/71 = 78,9 % |
| Solo orquestador (método correcto, dueña no alcanzada) | 6/71 (8,5 %) |
| Contando "orquestador" como enrutamiento válido | 64/71 = 90,1 % |
| Conjunto original del TSV (1–54) | 45/54 = 83,3 % |
| Frases nuevas (55–71) | 13/17 = 76,5 % (estricto 11/17) |
| Frases en inglés (15) | 11/15 = 73 % |
| Corridas que invocaron alguna skill | 65/71 = 91,5 % |
| Corridas que usaron `Agent` (subagente) | **0/93** (ni con 14 turnos) |

### Por categoría (según la skill esperada)

| Categoría | n | OK | Estricto | Solo orq. |
|---|---|---|---|---|
| Control: registros/riesgos/issues | 9 | 9 | 8 | 0 |
| Inicio (SU/IP) | 10 | 9 | 9 | 1 |
| Planificación | 10 | 9 | 9 | 1 |
| Control: informes/visuales/calidad/ágil | 13 | 11 | 10 | 1 |
| Reuniones/integraciones/BMAD | 12 | 9 | 9 | 0 |
| Estado/dirección | 3 | 2 | 2 | 1 |
| Enrutamiento/conocimiento/sanidad | 9 | 6 | 6 | 0 |
| Cierre/exportar | 5 | 3 | 3 | 2 |

## 3. Desvíos (frase → obtenido → esperado) e hipótesis

| id | Frase | Obtenido | Esperado | Repetición | Hipótesis |
|---|---|---|---|---|---|
| 19 | ¿Qué es la gestión por excepción? | respuesta directa | pm-knowledge | 2/2 igual | El modelo sabe PRINCE2 y no ve valor en cargar la skill; la `description` no dice qué aporta (convenciones propias: etapa 1 = iniciación, quién registra puertas). |
| 39 | Who approves a stage plan in PRINCE2? | respuesta directa | pm-knowledge | 2/2 igual | Ídem. Contraste: la 64 ("¿Quién aprueba el plan de etapa?", sin "PRINCE2") sí cargó pm-knowledge. |
| 58 | Pasame las acciones de la reunión de hoy: «…» (transcripción pegada) | respuesta directa (tabla) | pm-reuniones | 2/2 igual | Con el contenido en el mensaje la tarea parece trivial y se resuelve inline; la `description` no menciona "acciones de la reunión"/"action items" ni el valor de cargarlas como A-### en registros. |
| 26 | Escribí el acta de la reunión con estas notas | Bash (busca notas), pide el texto | pm-reuniones | con notas: pm-reuniones 2/2 | **Defecto del conjunto**: la frase anuncia notas que no trae. Con notas reales (26b/44b) enruta bien. |
| 44 | Turn this meeting transcript into minutes… | Bash, pide el texto | pm-reuniones | con texto: OK | Ídem. |
| 71 | Auditá la calidad del módulo de pagos | Bash (grep de código) | pm-calidad | 2/2 igual | Colisión con el sentido de software ("auditar código"); la `description` dice "quality audit" pero no "auditar/revisar la calidad de un producto o entregable". |
| 65 | How are we doing on this project? | pm-sanidad | pm-orquestador | 2.ª: orquestador | "how are we doing" ≈ "health check"; el hook SessionStart nombra "pm-orquestador / pm-sanidad" juntos. |
| 21, 22, 28, 33, 48, 63 | fin de etapa / plan próxima etapa / PID completo / cerrar el proyecto ×2 / forecast fuera de tolerancia | pm-orquestador (sin llegar a la dueña) | direccion-decisiones, plan-etapa, acta-constitucion, cierre-proyecto, progreso-reportes | 21 en 2.ª corrida → direccion-decisiones | **Sobrecarga del orquestador inducida por el hook**: su texto dice "Antes de producir artefactos o preparar una puerta, usar pm-orquestador / pm-sanidad". "Cerramos el proyecto" contiene literal el disparador de pm-cierre-proyecto y aun así fue al orquestador. **A/B lo confirma** (sección 5). |
| 56* | Armame el informe para la junta del jueves | pm-direccion-decisiones (2.ª: orquestador) | pm-progreso-reportes | inestable | Colisión: "junta" es disparador de pm-direccion-decisiones. En IP, preparar a la junta puede ser la solicitud de `autorizar-proyecto`, así que se aceptó; con hook A/B fue a pm-progreso-reportes. |
| 67* | Anotá el riesgo de que se nos vaya el arquitecto principal | pm-riesgos | pm-registros | 2/2 igual | **Contradicción documental**: `colisiones.md` (fila pm-direccion-decisiones) dice "Anotá este riesgo → pm-registros", pero la `description` de pm-registros dice "No: riesgos→pm-riesgos". El modelo obedece a la descripción. |

\* contados como aceptables.

**Orquestador: nunca delega.** En los 8 casos re-ejecutados con 14 turnos, pm-orquestador corrió `estado.py ver/siguiente`, verificó precondiciones y terminó el turno con un resumen y una pregunta (p. ej. "cerrar en IP = cierre prematuro, decide la junta"). Es coherente con su procedimiento (pasos 2 y 4: preguntar antes de delegar) y metodológicamente correcto con el fixture en IP, pero en un turno nunca llega a cargar la skill dueña ni a llamar `Agent`. El camino subagente quedó sin ejercitar.

## 4. Comandos de barra

| Prueba | Resultado |
|---|---|
| `/pm-estado` (sin espacio de nombres) | Funciona: ejecutó `estado.py ver/siguiente` y respondió con el formato del comando (USD 0,105). |
| `/pm-method:pm-estado` | Funciona, mismo resultado. |
| `/pm-ayuda` y `/pm-method:pm-ayuda` | Ambos funcionan (tabla "Ayuda de pm-method"). |
| Control `/pm-inexistente` | "no está instalado en esta sesión": confirma que el nombre corto sí se resuelve al comando del plugin cuando no hay otro con ese nombre. |

El stream de `-p` no muestra la expansión como `Skill` (ni como mensaje `<command-name>`); se verificó por el comportamiento y el formato de salida.

## 5. A/B del texto del hook SessionStart (copia del plugin, sin tocar el original)

Texto probado en `hooks/inicio.py` (copia): *"Si la petición nombra un producto o tema concreto (PID, cierre, plan de etapa, informe…), invocar directamente su skill dueña; pm-orquestador solo para '¿qué sigue?', '¿cómo venimos?' o pedidos que cruzan procesos; pm-sanidad antes de una puerta."*

| id | Original | Con hook nuevo | Esperado |
|---|---|---|---|
| 21 | orquestador | direccion-decisiones | direccion-decisiones |
| 22 | orquestador | plan-etapa-y-limites | plan-etapa-y-limites |
| 28 | orquestador | acta-constitucion | acta-constitucion |
| 33 | orquestador | cierre-proyecto | cierre-proyecto |
| 48 | orquestador | issues-cambios (aceptable) | progreso-reportes / issues-cambios |
| 63 | orquestador | cierre-proyecto | cierre-proyecto |
| 18 | orquestador | orquestador | orquestador |
| 55 | orquestador | orquestador | orquestador |
| 65 | sanidad / orquestador | orquestador | orquestador |
| 56 | direccion-decisiones / orquestador | progreso-reportes | progreso-reportes |

**10/10** con el hook nuevo frente a 3/10 con el original, y las preguntas vagas siguen yendo al orquestador. Extrapolado al conjunto completo: ≈ 64/71 (90 %).

## 6. Otros hallazgos

- **Ubicación de scripts:** 45 comandos `find / …` para hallar `estado.py`; **23 de 93 corridas ejecutaron scripts de otra copia del plugin (`<tmp>/chk/pm-method/…`)** encontrada por `find /`. Los cuerpos usan el marcador `<pm-estado-proyecto>/scripts/`, que el modelo no sabe resolver. Riesgo de versión cruzada y de costo.
- Hook guardián: 0 denegaciones (no hubo escrituras indebidas en 4 turnos).
- La pm-sanidad nueva enruta bien (53, 54, 70: 3/3).

## 7. Propuestas concretas

1. **Hook SessionStart (`hooks/inicio.py`)** — reemplazar "Antes de producir artefactos o preparar una puerta, usar pm-orquestador / pm-sanidad" por el texto del A/B (sección 5). Es la mejora de mayor impacto (+6 frases) y está medida. Además, imprimir la ruta absoluta de los scripts: `Scripts: <raiz>/skills/pm-estado-proyecto/scripts/` (el hook ya conoce `raiz`), lo que elimina los `find /` y el riesgo de usar otra copia.
2. **pm-reuniones** — agregar a "Usar:" `acciones de la reunión, action items, notas pegadas`; y al objeto: "…también si la transcripción viene pegada en el mensaje (carga acciones A-### tras confirmar)".
3. **pm-calidad** — agregar `auditar o revisar la calidad de un producto/entregable, quality review`; y "No: auditoría de código→fuera del paquete; información del proyecto→pm-sanidad".
4. **pm-knowledge** — explicitar el diferencial para que el modelo no responda de memoria: "Respuestas con las convenciones de pm-method (etapa 1 = iniciación, quién registra puertas, campos de estado.json); consultar antes de responder preguntas de PRINCE2/PMBOK". Alternativa: que el hook agregue "Preguntas de método → pm-knowledge".
5. **pm-orquestador** — sumar `cómo venimos, how are we doing, status` a "Usar:"; y en pm-sanidad, "No: ¿cómo venimos? / avance→pm-orquestador". En el procedimiento del orquestador: "si la petición es de una sola skill y las precondiciones se cumplen, invocar esa skill en el hilo principal; si no se cumplen, nombrar la skill dueña y la puerta que falta".
6. **docs/colisiones.md** — corregir el ejemplo "Anotá este riesgo… → pm-registros" a pm-riesgos (lo que dicen las descripciones y hace el modelo 2/2), o cambiar las descripciones si la intención es otra.
7. **Conjunto de prueba** — las frases 26 y 44 deben traer las notas o la transcripción; agregar 26b/44b/58 como casos con contenido pegado, 65/71 y los pares inglés del TSV. Agregar frases en inglés para pm-knowledge sin la palabra "PRINCE2".

## 8. Resultados por frase (corrida principal)

| id | Frase | Esperada | 1.ª skill | Orq. | Veredicto | USD |
|---|---|---|---|---|---|---|
| 1 | Armemos el análisis de interesados con poder e interés | organizacion-roles | organizacion-roles | no | OK | 0.115 |
| 2 | Quiero un plan de comunicación para la junta y los usuarios | comunicacion-stakeholders | comunicacion-stakeholders | no | OK | 0.141 |
| 3 | Identificá los riesgos del proyecto y su matriz probabilidad impacto | riesgos | riesgos | no | OK | 0.101 |
| 4 | Hacé la EDT del proyecto con responsables y costos | planificacion-por-productos | planificacion-por-productos | no | OK | 0.123 |
| 5 | Calculá el camino crítico y exportalo a MS Project | cronograma-estimacion | cronograma-estimacion | no | OK | 0.111 |
| 6 | Necesito el presupuesto con reserva de contingencia y de gestión | costos-presupuesto | costos-presupuesto | no | OK | 0.137 |
| 7 | Prepará el highlight report de esta semana con valor ganado | progreso-reportes | progreso-reportes | no | OK | 0.111 |
| 8 | Mostrame un tablero con las acciones de cada persona | visuales | visuales | no | OK | 0.108 |
| 9 | El proveedor entregó un módulo que no cumple la especificación | issues-cambios | issues-cambios | no | OK | 0.118 |
| 10 | El cliente pide agregar pagos en línea, ¿cómo lo tramito? | issues-cambios | issues-cambios | no | OK | 0.118 |
| 11 | Escribí el business case con VAN y payback | caso-de-negocio | caso-de-negocio | no | OK | 0.118 |
| 12 | Definamos los OKR del proyecto para el próximo semestre | okr | okr | no | OK | 0.110 |
| 13 | Procesá la transcripción del comité de ayer y sacá las acciones | reuniones | reuniones | no | OK | 0.102 |
| 14 | Sincronizá el backlog con las historias de BMAD | bmad-puente | bmad-puente | no | OK | 0.102 |
| 15 | ¿Qué requisitos del PRD no tienen historias? | bmad-puente | bmad-puente | no | OK | 0.115 |
| 16 | Traé los tickets abiertos de Jira del sprint actual | integraciones | integraciones | no | OK | 0.108 |
| 17 | Publicá el resumen semanal en el canal de Teams | integraciones | integraciones | no | OK | 0.108 |
| 18 | ¿Qué sigue en mi proyecto? | orquestador | orquestador | sí | OK | 0.115 |
| 19 | ¿Qué es la gestión por excepción? | knowledge | — | no | SIN SKILL (respuesta directa) | 0.013 |
| 20 | Creá la carpeta para un proyecto nuevo | estado-proyecto | estado-proyecto | no | OK | 0.089 |
| 21 | La junta tiene que aprobar el fin de etapa, prepará la decisión | direccion-decisiones | orquestador | sí | PARCIAL (solo orquestador) | 0.111 |
| 22 | Hagamos el plan de la próxima etapa | plan-etapa-y-limites | orquestador | sí | PARCIAL (solo orquestador) | 0.107 |
| 23 | Autorizá un paquete de trabajo para el equipo de infraestructura | paquetes-trabajo | paquetes-trabajo | no | OK | 0.112 |
| 24 | Registrá un supuesto: el padrón de socios estará disponible en marzo | registros | registros | no | OK | 0.099 |
| 25 | Anotá que Ana debe enviar la minuta el viernes | registros | registros | no | OK | 0.100 |
| 26 | Escribí el acta de la reunión con estas notas | reuniones | — | no | SIN SKILL (Bash directo) | 0.075 |
| 27 | Armá el project brief y el canvas de arranque | mandato-y-brief | mandato-y-brief | no | OK | 0.113 |
| 28 | Necesito el PID completo para que lo firme el ejecutivo | acta-constitucion | orquestador | sí | PARCIAL (solo orquestador) | 0.112 |
| 29 | Definí el enfoque de gestión de riesgos y de cambios | enfoques-gestion | enfoques-gestion | no | OK | 0.144 |
| 30 | Priorizá el backlog con MoSCoW y armá el release plan | agil-hibrido | agil-hibrido | no | OK | 0.117 |
| 31 | Hagamos la retrospectiva del sprint 3 | agil-hibrido | agil-hibrido | no | OK | 0.120 |
| 32 | Recopilá las lecciones aprendidas de la etapa | lecciones-aprendidas | lecciones-aprendidas | no | OK | 0.124 |
| 33 | Vamos a cerrar el proyecto | cierre-proyecto | orquestador | sí | PARCIAL (solo orquestador) | 0.112 |
| 34 | Exportá los registros a Excel y armá el ZIP para la junta | exportar | exportar | no | OK | 0.106 |
| 35 | Definí los criterios de aceptación y el registro de calidad | calidad | calidad | no | OK | 0.113 |
| 36 | Necesitamos licitar el desarrollo con tres proveedores | adquisiciones | adquisiciones | no | OK | 0.158 |
| 37 | Estimá el esfuerzo con PERT de los paquetes | cronograma-estimacion | cronograma-estimacion | no | OK | 0.109 |
| 38 | Dibujá el organigrama del proyecto | visuales | visuales | no | OK | 0.115 |
| 39 | Who approves a stage plan in PRINCE2? | knowledge | — | no | SIN SKILL (respuesta directa) | 0.062 |
| 40 | Draft the stakeholder engagement plan | organizacion-roles | organizacion-roles | no | OK | 0.121 |
| 41 | Build the risk register for the mobile app | riesgos | riesgos | no | OK | 0.107 |
| 42 | Create the work breakdown structure | planificacion-por-productos | planificacion-por-productos | no | OK | 0.116 |
| 43 | Write this week's status report with burn-up | progreso-reportes | progreso-reportes | no | OK | 0.145 |
| 44 | Turn this meeting transcript into minutes and action items | reuniones | — | no | SIN SKILL (Bash directo) | 0.085 |
| 45 | Did the PRD change since the board approved it? | bmad-puente | bmad-puente | no | OK | 0.101 |
| 46 | Score our key results for Q4 | okr | okr | no | OK | 0.101 |
| 47 | Prepare the end stage report | plan-etapa-y-limites | plan-etapa-y-limites | no | OK | 0.124 |
| 48 | The forecast says we will exceed the cost tolerance | progreso-reportes | orquestador | sí | PARCIAL (solo orquestador) | 0.113 |
| 49 | Fijá las tolerancias de la etapa en estado.json | estado-proyecto | estado-proyecto | no | OK | 0.107 |
| 50 | Hacé el diagrama de Gantt del cronograma | cronograma-estimacion | cronograma-estimacion | no | OK | 0.107 |
| 51 | Mandale un correo a los stakeholders con el estado | comunicacion-stakeholders | comunicacion-stakeholders | no | OK | 0.142 |
| 52 | ¿Cuál es el clima del equipo según las últimas reuniones? | reuniones | reuniones | no | OK | 0.101 |
| 53 | Revisá la sanidad del proyecto antes de la junta | sanidad | sanidad | no | OK | 0.093 |
| 54 | Run a consistency check between the PRD and our plan | sanidad | sanidad | no | OK | 0.098 |
| 55 | ¿Cómo venimos? | orquestador | orquestador | sí | OK | 0.118 |
| 56 | Armame el informe para la junta del jueves | progreso-reportes | direccion-decisiones | no | OK (aceptable) | 0.141 |
| 57 | El proveedor se atrasó dos semanas con la entrega del módulo de pagos | issues-cambios | issues-cambios | no | OK | 0.123 |
| 58 | Pasame las acciones de la reunión de hoy: «Marta: el padrón llega e… | reuniones | — | no | SIN SKILL (respuesta directa) | 0.064 |
| 59 | ¿Qué requisitos del PRD no están en el plan? | bmad-puente | bmad-puente | no | OK | 0.128 |
| 60 | Subí el highlight a Teams | integraciones | integraciones | no | OK | 0.096 |
| 61 | Necesito el Gantt | cronograma-estimacion | cronograma-estimacion | no | OK | 0.108 |
| 62 | Hagamos la retro del sprint | agil-hibrido | agil-hibrido | no | OK | 0.131 |
| 63 | Cerramos el proyecto | cierre-proyecto | orquestador | sí | PARCIAL (solo orquestador) | 0.118 |
| 64 | ¿Quién aprueba el plan de etapa? | knowledge | knowledge | no | OK | 0.116 |
| 65 | How are we doing on this project? | orquestador | sanidad | no | FALLO | 0.104 |
| 66 | The client wants SSO login added, log it as a change request | issues-cambios | issues-cambios | no | OK | 0.108 |
| 67 | Anotá el riesgo de que se nos vaya el arquitecto principal | registros | riesgos | no | OK (aceptable) | 0.108 |
| 68 | Exportame el plan de etapa a Word | exportar | exportar | no | OK | 0.101 |
| 69 | Make a dashboard of where we stand for the steering committee | visuales | visuales | no | OK | 0.120 |
| 70 | Run a health check on the project folder | sanidad | sanidad | no | OK | 0.091 |
| 71 | Auditá la calidad del módulo de pagos | calidad | — | no | SIN SKILL (Bash directo) | 0.091 |

Archivos: `resultados.jsonl` (crudo principal), `repeticion.jsonl`, `orquestador-largo.jsonl`, `ab-hook.jsonl`, `evaluacion.json`, `runs/<id>/out.jsonl` (stream completo por corrida), `frases-extra.tsv`, `slash.tsv`, `repetir.tsv`, `orq.tsv`, `ab.tsv`.
