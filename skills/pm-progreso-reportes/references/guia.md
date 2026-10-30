# Guía de progreso e informes · Progress and reporting guide

## 1. Entradas detalladas
- **EVM**: línea base de costo `02-planificacion/linea-base-costo.csv` (de `pm-costos-presupuesto`; cabecera `periodo,pv_acumulado,etapa,notas`, puede traer `pv_periodo`) con PV acumulado por período; presupuesto por producto (plan de etapa o diccionario de la WBS); avance por producto con método de medición declarado (0/100, 50/50, hitos ponderados, % físico); costos reales del período (`[por confirmar]` si no hay fuente).
- **BAC** = línea base de medición del desempeño vigente (Σ paquetes + contingencia asignada, cambios aprobados incluidos) **sin** la reserva de gestión, que se informa aparte (SPEC §1.10.6). Tolerancias de tiempo y costo de etapa y proyecto convertibles a % para `--tol-costo` y `--tol-plazo`.
- **Ágil**: backlog con puntos o ítems planificados y terminados por iteración (definición de terminado), MoSCoW, velocidad histórica, `estado.json.agil` y la línea base del release plan (el release plan guarda solo la línea base; los burn charts se generan aquí).
- **Periodicidad**: la del PID; si no consta, proponer referencia (checkpoint semanal, highlight quincenal o mensual) y pedir a la junta vía `pm-director`.

## 2. Recoger el avance de equipo (paso 2)
Por cada paquete en curso: informe de avance de miembro (`templates/informe-avance-equipo.md`) o checkpoint (`templates/checkpoint-report.md`); en ágil, tablero o burn-down en modo pull. Verificar que lo "planificado este período" coincide con lo prometido en el checkpoint anterior; que cada no logrado tiene causa raíz; que riesgos e issues nuevos están en sus registros con id (si no, `pm-registros`/`pm-riesgos`/`pm-issues-cambios`) y que los compromisos están en `acciones.csv` (A-###). Un gestor de equipo que pronostica salir de la tolerancia del paquete plantea un issue, no un comentario. Actualizar el plan de etapa: completados solo si están aprobados en `calidad.csv`; productos no iniciados que debían haber empezado = alerta temprana de tiempo.

## 3. Medición predictiva o híbrida con EVM
- `03-control/reportes/progreso.csv` (periodo, pv, ev, ac acumulados, notas): `pv` = `pv_acumulado` del período en la línea base; `ev` = Σ presupuesto de cada producto × % de avance según el método declarado; `ac` = costo real devengado acumulado.
- `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/evm.py --csv <dir>/03-control/reportes/progreso.csv --bac <BAC> --tol-costo <%> --tol-plazo <%> --eac tendencia|atipico|compuesto --idioma <es|en> --json` (acepta también `pv_acumulado`, `ev_acumulado`, `ac_acumulado`; `--proyecto <dir>` toma datos de la carpeta).
- Devuelve SV, CV, SPI, CPI, % completado/gastado, tres EAC, ETC, VAC, TCPI, `semaforo_costo`, `semaforo_cronograma`, `excepcion_prevista`, `base_semaforo`.
- Correr una vez con tolerancias de etapa y otra con las de proyecto. Sin `--tol-*` usa índices de referencia (0,95/0,85) y lo declara en `base_semaforo`: decirlo en el informe.
- **Guardar el corte (control permanente):** en cada período, la corrida con las tolerancias de etapa se repite con `--proyecto <dir> --guardar --corte <fecha del informe>`; queda `03-control/reportes/evm-<corte>.json` y la sanidad vigila el pronóstico entre informes, sin esperar al fin de etapa: TOL-01 (AVISO) si el último corte pronostica excepción y no hay excepción abierta ni puerta `autorizar-plan-excepcion` posterior; TOL-02 (INFO) en ámbar; TOL-03 (INFO) etapa de entrega sin corte guardado o con el último de más de 31 días. Vale igual en ágil (`--modo agil --pct-no-must`). Correr `sanidad.py --corte` con la misma fecha.
- Controles: EV ≤ PV total del componente; acumulados del período anterior = informe anterior; BAC con cambios aprobados; al menos dos EAC con la elegida justificada (atípica, tendencia típica, CPI×SPI); ETC, VAC y TCPI recalculados; índices con la tendencia de los últimos períodos; SPI tiende a 1 al final → complementar con camino crítico o cronograma ganado.

## 4. Medición ágil y bloque burn-up
- Puntos planificados vs. terminados por iteración; velocidad promedio de las últimas iteraciones (ventana declarada); burn-down de iteración y burn-up de release con línea de alcance total; iteraciones restantes ≈ puntos restantes ÷ velocidad; qué Must/Should/Could entran en la fecha.
- EVM adaptativo opcional (PV y EV = puntos planificados/terminados valorizados, AC = costo del equipo): `evm.py ... --modo agil --pct-no-must <% puntos Should/Could>` → `semaforo_alcance`, `alcance_no_entregable_pct`; costo y plazo salen `n/a-agil`. Con costo y fecha fijos, EAC > BAC = alcance pronosticado que no entra, contra la tolerancia de alcance (MoSCoW); excepción solo si los Must no entran (SPEC §1.10.7).
- Solo cuentan ítems terminados según la definición de terminado; no reiniciar el burn-down al cambiar alcance sin anotarlo.
- **Bloque burn-up** (highlight y checkpoint, ágil o híbrido): iteración; alcance total y su variación desde la línea base del release plan; puntos terminados acumulados; velocidad de las últimas 3 iteraciones; iteraciones restantes; fecha pronosticada vs. fecha fija; Must en riesgo. Tabla y, con `pm-visuales`, gráfico en `tablero-avance.html` o Mermaid `xychart-beta`.

## 5. Variante BMAD (`integraciones.especificacion = bmad`)
- Cada período: `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> verificar` (desvíos del PRD o Sprint Change Proposals nuevas → `pm-issues-cambios`, tipo `solicitud-cambio`) y `bmad.py --proyecto <dir> avance` (agrega una fila a `03-control/reportes/avance-bmad.csv`).
- Columnas de `avance-bmad.csv`: `fecha, historias, backlog, ready-for-dev, in-progress, review, done, epicas, epicas_terminadas, puntos_total, puntos_terminados, pct_terminado, base_pct` (`puntos` si `backlog.csv` trae `estimacion`, si no `historias`).
- Uso: checkpoint del sprint-paquete = conteo por estado y historias bloqueadas; highlight = % terminado, épicas terminadas y serie para el burn-up (alcance total = `puntos_total`, terminado = `puntos_terminados`; un salto de `puntos_total` entre filas es cambio de alcance a explicar). Citar la fecha de la fila y el sha corto del artefacto BMAD.
- Solo `done` cuenta como terminado; `review` no. El "sí" de correct-course en BMAD no aprueba nada en PRINCE2.

## 6. Datos de trackers externos
Si hay un tracker conectado (Jira, Linear, GitHub, Azure DevOps), `pm-integraciones` deja una instantánea fechada en `03-control/fuentes/<sistema>-AAAA-MM-DD.(csv|json)`; el informe cita esa instantánea, nunca la herramienta en vivo, y los registros de gobierno siguen mandando. Publicar el informe en chat o correo: vía `pm-integraciones`, con vista previa y confirmación.

## 7. Variaciones y pronóstico
- Variaciones de tiempo, costo y desempeño técnico (alcance + calidad): planificado, real, variación absoluta y relativa, causa raíz (no síntoma), respuesta con responsable y fecha, implicación si continúa. Declarar convención de signos. Umbrales del plan o, si no hay, atención 5 % y escalamiento 10 % declarados como referencia. `templates/analisis-variaciones.md` cuando se supera el umbral de atención o la junta lo pide; en proyectos pequeños, tabla de tres filas en el highlight.
- Pronóstico contra los siete objetivos: fecha (SPI, cronograma ganado o camino crítico), costo final (EAC justificada), alcance (productos que no llegarán), calidad (pruebas fallidas sin retestear), beneficios, sostenibilidad, exposición al riesgo.
- Regla de semáforo para todas las dimensiones: desvío previsto ≤ 50 % de la tolerancia verde; 50–100 % ámbar (alerta temprana, acciones); fuera = rojo = excepción.
- Tendencias, no solo estado: cruzar issues abiertos, pruebas fallidas, productos no iniciados y movimientos en la matriz de riesgos.

## 8. Semáforos
| Color | Con tolerancias (preferida) | Sin tolerancias (referencia, declararlo) | Ágil (`--modo agil`) |
|---|---|---|---|
| Verde | desvío previsto ≤ 50 % de la tolerancia | SPI/CPI ≥ 0,95 | todos los Must y Should previstos entran |
| Ámbar | 50–100 % de la tolerancia; acciones con responsable | 0,85 ≤ SPI/CPI < 0,95 | caen Should/Could dentro de la tolerancia de alcance |
| Rojo | pronóstico fuera (`excepcion_prevista = true`) → informe de excepción | SPI/CPI < 0,85 | algún Must no entra → excepción |

Un rojo guardado con `--guardar` que no se trata aparece como TOL-01 en cada sanidad hasta que hay excepción abierta (`estado.py limite-etapa --excepcion X-###`, pm-director) o puerta `autorizar-plan-excepcion`. El highlight informa también el consumo del presupuesto de cambio y de la reserva de riesgo (sanidad CAM-03) y las condiciones de puertas abiertas o cumplidas (`puertas.py estado --markdown`).

Riesgos: un riesgo alto sin respuesta o sin propietario rompe la línea de tolerancia por defecto (SPEC §1.10.9) → rojo. Usar `registro.py resumen --corte <fecha del informe>` para que las acciones vencidas coincidan con el tablero.

## 9. Highlight: variantes, orden y resumen de registros
- `registro.py --proyecto <dir> resumen --json`: por registro `abiertos`, `por_estado`; riesgos `altos_abiertos` (P×I ≥ 15), `sin_respuesta`, `sin_propietario`, `top`; issues `sin_responsable`; acciones `vencidas`, `abiertas_por_responsable`. Usar los campos tal cual; las listas de ids traen a lo sumo 25 elementos y el conteo completo va en `<lista>_total` (`sin_respuesta_total`, `vencidas_total`…): para cantidades, usar siempre `_total`.
- **Mínima (una página)**: secciones `[mín]` — resumen, semáforo de los siete objetivos, logros y próximo período, decisiones pedidas, top riesgos/issues/acciones vencidas y, en ágil, bloque burn-up. Proyectos pequeños, perfil ágil mínimo o cadencia semanal.
- **Completa (doce secciones)**: con EVM, proveedores, varias audiencias o ámbar/rojo. Orden: identificación y período → semáforo de los siete objetivos (vs. anterior) → logros → previsto → decisiones pendientes de la junta → issues y riesgos críticos → comentario del gestor con "ruta hacia verde" → finanzas → hitos → lecciones. Anexar valor ganado y variaciones si se usan.
- Siempre: hecho vs. pronóstico; RFC y fuera de especificación del período aunque sea "ninguna"; nivel de logros y paquetes, no tareas; sostenibilidad integrada; no contradecir registros (corregir primero el registro).
- Acciones correctivas: `registro.py agregar acciones --campo origen=highlight-<fecha> --campo responsable=... --campo fecha_compromiso=...` o enmienda del paquete; los compromisos viven en `acciones.csv`, no en `issues.csv`.
- Audiencias (con `pm-comunicacion-stakeholders`): junta → decisiones, desvíos, finanzas, excepciones; equipo → bloqueos, prioridades, acciones; cliente/usuario sénior → hitos, productos entregados, riesgos que le afectan, cambios aprobados. Mismas cifras, distinta selección.


**Puertas como insumo del informe.** `puertas.py estado --markdown` aporta: cada puerta con su decisión, quién decidió, condiciones (abiertas o cumplidas), observaciones de la verificación (p. ej. gate de BMAD en CONCERNS) y si fue forzada; y la preparación de la próxima puerta (bloqueos, condiciones y avisos, cada uno con su código de control, los mismos de `puertas.py verificar`). En el highlight va en §6; una condición abierta vencida o una puerta forzada se informa como riesgo o issue; en el tablero y en "¿cómo venimos?" se muestra la línea de `estado.py resumen` (última y próxima puerta).
## 10. Adaptación según enfoque de entrega
| Aspecto | Predictivo | Ágil | Híbrido |
|---|---|---|---|
| Unidad de avance | productos aprobados y % físico | ítems terminados (DoD), puntos | productos aprobados; ítems dentro de cada paquete |
| Medición | EVM con `evm.py` sobre `progreso.csv` | velocidad, burn-down, burn-up (con BMAD: `avance-bmad.csv`) | EVM a nivel de etapa; burn charts por paquete |
| Pronóstico de fecha | EAC de tiempo, cronograma ganado, camino crítico | puntos restantes ÷ velocidad | ambos, conciliados |
| Checkpoint | documento o correo | modo pull: tablero, diaria, burn-down | según el paquete |
| Tolerancia de alcance | productos opcionales | intercambio de características en la etapa | por paquete |
| Highlight | mínimo o completo con EVM e hitos | mínimo con bloque burn-up | completo + burn-up por paquete |
| Cambios | solicitud formal | intercambio del PO dentro de tolerancia; solicitud si desplaza un Must | según nivel |
| EVM | `--tol-costo --tol-plazo` | opcional `--modo agil` | ambos |

## 11. Reglas extendidas
- Sin tolerancias no hay gestión por excepción: declararlo y pedir a la junta que las fije antes de asignar semáforos.
- Solo se controla al nivel de detalle del plan (highlight quincenal ⇒ productos por quincena en el plan de etapa).
- Monitorear es por tiempo, decidir por eventos, reportar ambas; cadena: checkpoint → highlight → excepción.
- Una excepción resuelta dentro de tolerancia de etapa no lleva informe de excepción, pero aparece en el siguiente highlight.
- La frecuencia la acuerda la junta (PID); con equipo nuevo o señales de riesgo, proponer aumentarla temporalmente.
- Validar la cadena de reporte: highlight, variaciones y EVM con las mismas cifras; si no, detener y señalar (`estado.py periodo --verificar`, §14).
- Señal de sesgo (todo verde con issues acumulándose, "va bien" sin evidencia) → pedir evidencia, revisión por pares o más frecuencia.
- Sin línea base de costo → EVM no es posible: avance por productos e hitos y derivar a `pm-costos-presupuesto`.

## 12. Transición de fin de etapa
Si el fin de etapa se acerca (último paquete en verificación, `fin_previsto` a menos de un período, productos completos), proponer CS→SB: con confirmación del gestor, `estado.py --proyecto <dir> limite-etapa` y derivar a `pm-plan-etapa-y-limites`. Con plan de excepción pedido por la junta (decisión registrada por `pm-director`): `estado.py limite-etapa --excepcion X-###`, plan en `02-planificacion/plan-excepcion-X-###.md`. Fin de proyecto → `estado.py cierre` y `pm-cierre-proyecto`. Ninguna puerta se registra desde aquí.

## 13. Briefing de incorporación
Para quien se suma antes de una puerta (integrante de la junta o del equipo, auditor, ejecutivo, agente): una lectura de 10
minutos que no reemplaza al PID ni al highlight, los cita. `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py
--proyecto <dir> briefing [--para ST-###] [--corte AAAA-MM-DD] [--salida RUTA|-] [--json]` llena
`templates/briefing-incorporacion.md` desde `estado.json`, los registros, el último corte de EVM guardado, `puertas.py` y el
radar de atención (`estado.py radar`; reglas y prioridad en `pm-estado-proyecto/references/guia.md` §9). Secciones:
contexto, rol y responsabilidades del interesado (`--para`: rol en el proyecto y en la junta, contacto acordado, RACI, lo que
tiene a cargo y sus ítems del radar), decisiones clave (nivel junta, ejecutivo o capa de negocio), riesgos altos, issues y
cambios pendientes con quién decide, desempeño contra tolerancias, artefactos aprobados con su copia congelada, próxima
puerta con bloqueos y condiciones, y próximos pasos. A lo sumo ≈ 2 páginas (6.500 caracteres); cada cifra con su id o su
archivo; nunca actitudes ni valoraciones de interesados.
- [PRINCE2] Definir roles y responsabilidades y comunicación bidireccional: quien entra a la junta debe saber qué decide y
  con qué tolerancias (`pm-knowledge/references/prince2-principios-personas-procesos.md` §2.3 y §3.4).
- [PMBOK→Organizing] Gestión del conocimiento: lo explícito (registros, artefactos aprobados) se entrega por escrito; lo
  tácito, en la conversación con el gestor que sigue a la lectura (`pmbok8-dominios-procesos-adaptacion.md` §2.1.b.6).
- [Plantillas] La incorporación de personas forma parte del plan de gestión de recursos (`plantillas-inicio-y-planes.md`
  §3.7: incorporación de personas y de contratistas externos).
El archivo queda `borrador` en `03-control/reportes/<corte>-briefing-incorporacion[-ST-###].md`; si se distribuye, el
gestor lo revisa y lo registra (`estado.py artefacto briefing-<fecha> --ruta … --estado en-revision`) y el envío va por
`pm-comunicacion-stakeholders`. Con `confidencial=si` en el interesado, el briefing omite también su poder e interés.

## 14. Datos del período, tablero y highlight desde el dato
Un solo cálculo alimenta el highlight, el tablero de `pm-visuales` y lo que leen pm-director y
`pm-comunicacion-stakeholders`: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir>
periodo --desde AAAA-MM-DD --corte AAAA-MM-DD [--proximo AAAA-MM-DD] [--juicio J.json] [--json] [--tablero [RUTA]]
[--highlight [RUTA] [--forzar]]`. Sin `--tablero` ni `--highlight` solo muestra los datos (texto acotado o `--json`).

**Semáforos por regla** (verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo fuera; §8):
| Objetivo | Regla | Fuente |
|---|---|---|
| Tiempo y costo | `semaforo_cronograma` y `semaforo_costo` del último corte de EVM con fecha dentro del período (uno anterior no se usa: aviso) | `evm-<corte>.json` |
| Alcance | `semaforo_alcance` del corte con `--modo agil`; si no, juicio del gestor, citado contra el burn-up | `evm-<corte>.json` · `avance-bmad.csv` |
| Riesgo | rojo si un riesgo abierto con P×I ≥ `estado.json.umbrales_riesgo.alto` no tiene respuesta o propietario; ámbar si hay altos abiertos; verde si no | `registro.py resumen` |
| Calidad | ámbar con QUA-01…03 o un fuera de especificación abierto; verde si no (sin revisiones registradas, juicio) | registros · sanidad QUA |
| Beneficios, sostenibilidad | juicio del gestor contra la tolerancia del proyecto | enfoque de beneficios |

Estado general = el peor de los siete. Productos aceptados del período = revisiones `completada` con resultado aprobado y
`fecha_real` en el período; también se listan los cambios y fuera de especificación del período, las acciones vencidas y
las que vencen hasta `--proximo`, y las decisiones (las del juicio o, si no hay, las de «decidir» del radar; las del radar
que el juicio deja afuera se avisan).

**Juicio del gestor** (`03-control/reportes/<corte>-juicio-gestor.json`, lo propone el modelo y lo confirma el gestor;
fuentes = datos): `objetivos` (`{clave: {rag, pronostico, detalle, tol_etapa, tol_proyecto}}`: en un objetivo con regla,
`pronostico` es una nota y `rag` solo puede empeorarlo; las tolerancias de `estado.json` mandan), `hitos`, `decisiones`
(`{id, texto, fecha_limite}`), `agil` (`iteraciones: [{fecha, nombre, planificado}]`, una por corte de
`avance-bmad.csv` que cierra una iteración; `fecha_fija`, `fecha_pronostico`, `must_en_riesgo`), `comentario`, `moneda`
y `fuentes` (se suman a las del script).

**Highlight.** `--highlight` escribe el borrador de la variante mínima (`03-control/reportes/<corte>-highlight-report.md`,
secciones [mín] de la plantilla) con las cifras, ids y puertas (`puertas.py estado`), y deja `[por redactar]` el
principal desvío, la decisión que se pide, el próximo período y la recomendación; no pisa un archivo existente sin
`--forzar` ni una versión aprobada. Tras redactar: `estado.py periodo --verificar <informe> [<otro> …]` (también
comunicados y borradores por audiencia) comprueba la **cadena de reporte**: cada cifra rotulada del EVM (SPI, CPI, EAC,
ETC, VAC, BAC, PV, EV, AC, SV, CV; «sobrecosto … %», «… % del PV») coincide con el corte guardado al redondeo citado
(«≈» o «~»: ±1 %) y ningún semáforo con regla es mejor que el derivado; código 1 si algo difiere. Recién entonces se
registra `highlight-<corte>` en revisión (paso 11).
- [PRINCE2] Cadena de informes y revisión del progreso contra los siete objetivos
  (`prince2-practicas-riesgo-issues-progreso-productos.md` §4.c.3 y §4.c.6); el gestor informa, la junta decide.
- [Plantillas] Validar la cadena de reporte y reconciliar números (`plantillas-documentos-registros-reportes.md` §49,
  reglas 21 y 22).

## 15. Tablero del proyecto junto al highlight o la junta
Para dejar la foto del ciclo que acompaña un highlight o una reunión de junta: `python3
${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/tablero.py --proyecto <dir> congelar --etiqueta "highlight <fecha>"
--por "<rol: nombre>"` (instantánea inmutable en `03-control/reportes/tableros/`, JSON y HTML). En cada puerta la foto
la congela `estado.py puerta` sin pedirlo. Qué cambió desde la última puerta, para la sección de avance del informe:
`tablero.py --proyecto <dir> comparar <id> actual` (ids con `tablero.py --proyecto <dir> listar`). El tablero no tiene
cifras propias: los números del informe siguen saliendo de `estado.py periodo` (§14) y del EVM.

