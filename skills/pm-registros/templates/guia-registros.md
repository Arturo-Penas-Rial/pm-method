---
tipo: guia-registros
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Guía de registros · Registers guide

**Proyecto / Project:** {{proyecto}}
*Nombre del proyecto tal como figura en `estado.json`.*

**Cadencia de revisión / Review cadence:** {{cadencia_revision}}
*Con qué frecuencia se recorren los registros abiertos (por defecto, cada período de informe acordado en el PID; en ágil, en la revisión de iteración).*

**Autoridad de cambio / Change authority:** {{autoridad_cambio}}
*Rol o persona a quien la junta delegó decisiones de cambio; copiar de `estado.json.roles.autoridad_cambio`.*

Convenciones comunes a todos los CSV: codificación UTF-8, separador coma, fechas ISO `AAAA-MM-DD`, valores de enumeración en minúsculas sin acentos, `id` secuencial con prefijo fijo que nunca se reutiliza, `estado` nunca se borra (se cierra). Los valores se guardan en español; al registrar se aceptan alias en inglés (`threat`, `opportunity`, `open`, `closed`, `high`, `medium`, `low`, `avoid`, `reduce`, `change-request`, `off-specification`…) que `registro.py` convierte al valor canónico. / Values are stored in Spanish; English aliases are accepted on input. Los prefijos de id son: R (riesgos), I (issues), C (cambios), D (decisiones), S (supuestos), L (lecciones), ST (stakeholders), Q (calidad), A (acciones). `X-###` no es un registro: es el id de un informe de excepción (documento en `03-control/reportes/`).

**Fuente única del esquema / Single source of schema:** `<pm-estado-proyecto>/scripts/esquema.py`. Esta guía documenta exactamente las mismas columnas, en el mismo orden, y los mismos valores permitidos; si cambia una, cambian las dos. Para consultar el esquema vigente desde la consola: `python3 <pm-estado-proyecto>/scripts/registro.py --proyecto <dir> esquema <registro>`.

**Validación / Validation:** `registro.py agregar` y `actualizar` rechazan valores fuera de la lista "Valores permitidos" y, en riesgos, probabilidades e impactos que no sean enteros 1–5; también rechazan columnas inexistentes. `--forzar` registra igual, solo con motivo anotado en `notas`. Las columnas marcadas "libre" no se validan (los valores listados son sugerencias). Si un CSV de una versión anterior no tiene una columna nueva, el script la agrega al final sin perder filas.

**Estado inicial / Initial state** (lo pone `registro.py agregar` si no se indica): riesgos `abierto`, issues `abierto`, cambios `abierto`, supuestos `abierto`, lecciones `registrada`, calidad `planificada`, acciones `abierta`; decisiones y stakeholders no tienen columna `estado`.

**Estados "abiertos" / Open states** (los que cuentan `registro.py listar --abiertos` y `resumen`): riesgos `abierto|en-seguimiento|escalado`; issues `abierto|en-evaluacion|en-accion|escalado|pendiente-cambio`; cambios `abierto|en-evaluacion|pendiente-decision|aprobado|diferido`; supuestos `abierto`; lecciones `registrada|revisada`; calidad `planificada|en-curso`; acciones `abierta|en-curso`.

## 1. riesgos.csv · Risk register

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador único | Unique id | `R-###` (automático) |
| fecha_identificacion | Fecha en que se detectó | Date identified | ISO (automático si se omite) |
| autor | Quién lo planteó | Raised by | nombre o rol |
| categoria | Fuente o área del riesgo | Risk category | vacío o `tecnico`, `externo`, `organizacional`, `gestion`, `comercial`, `sostenibilidad`, `otro` |
| causa | Situación que origina el riesgo | Cause | texto; no es el riesgo en sí |
| evento | Lo incierto que podría ocurrir | Event | texto; amenaza u oportunidad |
| efecto | Consecuencia sobre los objetivos | Effect | texto; en unidades del objetivo (días, moneda, métrica) |
| tipo | Sentido del riesgo | Risk type | `amenaza`, `oportunidad` |
| probabilidad | Chance de ocurrencia | Probability | entero 1–5 (escala del enfoque de riesgos) |
| impacto | Magnitud del efecto | Impact | entero 1–5 |
| puntuacion | probabilidad × impacto | Score | calculado por `registro.py` (1–25): alto ≥15, medio 6–12, bajo ≤5 |
| impacto_monetario | Efecto estimado en moneda si ocurre | Monetary impact | número sin separador de miles (moneda del presupuesto); vacío si no se cuantifica |
| valor_esperado | EMV = impacto monetario × probabilidad porcentual | Expected monetary value | calculado por `registro.py` con la convención 1→10 %, 2→30 %, 3→50 %, 4→70 %, 5→90 % |
| proximidad | Cuándo podría ocurrir | Proximity | vacío o `inminente`, `corto-plazo`, `mediano-plazo`, `largo-plazo` |
| disparador | Señal observable que anticipa el evento | Trigger | texto; condición que activa el plan de contingencia |
| respuesta | Estrategia elegida | Response strategy | vacío mientras se analiza; amenazas: `evitar`, `reducir`, `transferir`, `compartir`, `aceptar`, `contingencia`, `escalar`; oportunidades: `explotar`, `mejorar`, `compartir`, `aceptar`, `contingencia`, `escalar` |
| acciones | Tareas concretas con fecha | Actions | texto; separar con `;` |
| propietario | Quien gestiona el riesgo | Risk owner | nombre o rol (obligatorio) |
| ejecutor | Quien ejecuta las acciones | Risk actionee | nombre o rol (puede coincidir con propietario) |
| probabilidad_residual | Probabilidad prevista tras aplicar la respuesta | Residual probability | entero 1–5 |
| impacto_residual | Impacto previsto tras aplicar la respuesta | Residual impact | entero 1–5 |
| estado | Situación del riesgo | Status | `abierto`, `en-seguimiento`, `escalado`, `ocurrido`, `retirado`, `cerrado` |
| fecha_revision | Última revisión | Last review | ISO; vencida si supera la cadencia |
| notas | Riesgos secundarios, referencias cruzadas | Notes | texto; incluir `origen S-###` / `→ I-###` |

*Umbrales y EMV / Thresholds and EMV:* puntuación P×I alto ≥15, medio 6–12, bajo ≤5 (valores por defecto del paquete, configurables en el enfoque de gestión del riesgo; si se cambian, declararlo allí, cargarlos con `estado.py umbrales-riesgo alto=<n> medio=<n>` para que `registro.py resumen` los use, y mencionarlo en el informe). Línea de tolerancia por defecto: ningún riesgo alto abierto sin `respuesta` y sin `propietario`. El EMV es una aproximación: la escala ordinal 1–5 se convierte a 10/30/50/70/90 % por convención; `registro.py` recalcula la columna en cada alta o actualización con esa convención; si el enfoque de riesgo define otra tabla, el valor alternativo se informa en `notas` y en el informe de riesgos, no en la columna. Para oportunidades, el EMV se lee como beneficio esperado.

## 2. issues.csv · Issue register

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `I-###` |
| fecha | Fecha de planteo | Date raised | ISO (automático) |
| autor | Quién lo planteó | Raised by | nombre o rol |
| tipo | Uno de los cinco tipos del método | Issue type | `problema-preocupacion`, `evento-externo`, `oportunidad-negocio`, `solicitud-cambio`, `fuera-especificacion` |
| titulo | Resumen en una línea | Title | texto |
| descripcion | Qué ocurre y desde cuándo | Description | texto |
| prioridad | Urgencia de tratarlo | Priority | vacío o `urgente`, `alta`, `media`, `baja` |
| severidad | Gravedad del efecto | Severity | vacío o `critica`, `mayor`, `menor`, `informativa` |
| impacto | Efecto sobre objetivos y tolerancias | Impact | texto; cubrir los siete objetivos cuando es mayor |
| decision | Qué se resolvió | Decision | texto libre; para fuera de especificación: `concesion` o `corregir` + resumen |
| decidido_por | Quién resolvió y a qué nivel | Decided by | texto libre: rol + nombre (p. ej. `gestor: Ana`, `autoridad-cambio: J. Pérez`) |
| responsable | Quien lo resuelve | Owner | nombre o rol (obligatorio) |
| estado | Situación | Status | `abierto`, `en-evaluacion`, `en-accion`, `escalado`, `pendiente-cambio`, `resuelto`, `cerrado` |
| fecha_cierre | Cuándo se cerró | Closed on | ISO (obligatoria al cerrar) |
| notas | Referencias (`origen R-###`, `→ C-###`, informe de issue) | Notes | texto |

## 3. cambios.csv · Change log

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `C-###` |
| fecha | Fecha de presentación | Date submitted | ISO |
| solicitante | Quién pide el cambio | Requestor | nombre o rol |
| titulo | Resumen | Title | texto |
| descripcion | Antes y después del cambio | Description | texto |
| justificacion | Por qué (origen: normativo, defecto, cliente, mejora) | Justification | texto |
| impacto_alcance | Efecto en productos | Scope impact | texto; `ninguno` si no hay |
| impacto_tiempo | Efecto en fechas e hitos; ruta crítica | Schedule impact | texto con días; indicar si toca ruta crítica |
| impacto_costo | Monto y fuente de financiación | Cost impact | número + moneda + `presupuesto-cambio` / `fondos-adicionales` |
| impacto_calidad | Efecto en criterios de calidad | Quality impact | texto |
| impacto_riesgo | Riesgos nuevos o modificados | Risk impact | texto; ids `R-###` |
| impacto_beneficios | Efecto en los beneficios del business case | Benefits impact | texto; `ninguno` si no hay; si afecta la viabilidad, escalar a la junta |
| recomendacion | Opción recomendada y por qué | Recommendation | texto |
| decision | Disposición | Disposition | vacío hasta decidir; `aprobado`, `rechazado`, `diferido`, `pedir-plan-excepcion`, `pedir-mas-informacion` |
| decidido_por | Autoridad que decidió | Decided by | texto libre: nivel (`product-owner`, `gestor`, `autoridad-cambio`, `junta`, `capa-negocio`) + nombre |
| fecha_decision | Cuándo | Decision date | ISO |
| estado | Situación | Status | `abierto`, `en-evaluacion`, `pendiente-decision`, `aprobado`, `rechazado`, `diferido`, `implementado`, `cerrado` |
| notas | `origen I-###`, versión nueva de línea base, fecha de reevaluación si diferido | Notes | texto |

## 4. decisiones.csv · Decision log

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `D-###` |
| fecha | Fecha de la decisión | Date | ISO |
| decision | Enunciado preciso | Decision | texto |
| contexto | Situación que la motivó | Context | texto; ids relacionados |
| opciones_consideradas | Alternativas descartadas | Options considered | texto; separar con `;` |
| decidido_por | Quién decidió | Decided by | nombre o rol |
| nivel | Nivel de autoridad | Authority level | `equipo`, `product-owner`, `gestor`, `autoridad-cambio`, `junta`, `capa-negocio` |
| artefactos_afectados | Qué se actualiza | Affected artifacts | rutas o ids (`C-###`, `02-planificacion/plan-etapa-2.md`) |
| revisar_en | Cuándo reevaluar | Review on | ISO o hito |
| notas | Condiciones, puerta asociada | Notes | texto; `puerta: autorizar-etapa` cuando aplica |

*Filas automáticas / Automatic rows:* `estado.py puerta` escribe por sí mismo la fila de cada decisión de puerta (nivel `junta`, `notas=puerta: <tipo>`) y `estado.py aprobar` la de cada aprobación de documento; no duplicarlas a mano. `nivel=product-owner` se usa para intercambios de ítems del backlog dentro de la tolerancia de alcance de la etapa (ágil/híbrido).

## 5. supuestos.csv · Assumption log

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `S-###` |
| fecha | Fecha de registro | Date | ISO |
| autor | Quién lo planteó | Raised by | nombre o rol |
| supuesto_o_restriccion | Enunciado falsable | Statement | texto |
| tipo | Naturaleza | Type | `supuesto`, `restriccion` |
| categoria | Área | Category | libre; sugeridos: `tecnico`, `recursos`, `cronograma`, `costo`, `externo`, `regulatorio`, `organizacional`, `otro` |
| validado | Resultado de la validación | Validated | vacío o `si`, `no`, `pendiente` |
| fecha_validacion | Fecha límite o real de validación | Validation date | ISO |
| responsable | Quien valida | Owner | nombre o rol |
| estado | Situación | Status | `abierto`, `validado`, `invalidado`, `transferido`, `cerrado` |
| notas | `→ R-###` / `→ I-###` si transferido; documento de origen | Notes | texto |

## 6. lecciones.csv · Lessons log

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `L-###` |
| fecha | Fecha | Date | ISO |
| etapa | Etapa en que surgió | Stage | número o nombre de `estado.json.etapa_actual` |
| categoria | Área | Category | libre; sugeridos: `proceso`, `tecnica`, `entorno`, `stakeholders`, `adquisiciones`, `calidad`, `riesgos`, `equipo`, `otro` |
| situacion | Qué esperábamos y qué ocurrió | Situation | texto |
| efecto | Consecuencia (incluido impacto financiero si lo hay) | Effect | texto |
| recomendacion | Qué repetir o cambiar | Recommendation | texto accionable |
| prioridad | Importancia | Priority | vacío o `alta`, `media`, `baja` |
| responsable_seguimiento | Quien acciona el aprendizaje | Follow-up owner | nombre o rol |
| estado | Situación | Status | inicial `registrada`; luego `revisada`, `accionada-proyecto`, `accionada-organizacion`, `descartada` |
| notas | Ids relacionados, si fue riesgo previo | Notes | texto |

## 7. stakeholders.csv · Stakeholder register

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `ST-###` |
| nombre | Persona, cargo u organización | Name | texto |
| rol_organizacion | Cargo en su organización | Organizational role | texto |
| rol_proyecto | Función en el proyecto | Project role | texto (p. ej. usuario senior) |
| poder | Capacidad de influir | Power | vacío o `alto`, `medio`, `bajo` |
| interes | Grado de interés | Interest | vacío o `alto`, `medio`, `bajo` |
| actitud | Postura | Attitude | vacío o `lider`, `partidario`, `neutral`, `resistente`, `desconocedor` |
| nivel_compromiso_actual | Involucramiento hoy | Current engagement | vacío o `lider`, `partidario`, `neutral`, `resistente`, `desconocedor` |
| nivel_compromiso_deseado | Involucramiento objetivo | Desired engagement | vacío o `lider`, `partidario`, `neutral`, `resistente`, `desconocedor` |
| expectativas | Qué espera del proyecto | Expectations | texto |
| canal | Medio de comunicación | Channel | texto |
| frecuencia | Cadencia de contacto | Frequency | texto |
| responsable_relacion | Quien gestiona la relación | Relationship owner | nombre o rol |
| confidencial | La fila contiene valoraciones sensibles | Confidential | vacío, `si`, `no`; `si` = circulación restringida (no se exporta en la versión pública) |
| notas | Observaciones | Notes | texto |

## 8. calidad.csv · Quality register

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `Q-###` |
| producto | Producto verificado | Product | nombre o id del PBS |
| metodo_verificacion | Cómo se verifica | Verification method | vacío o `revision`, `prueba`, `inspeccion`, `demostracion`, `auditoria` |
| criterios | Criterios de calidad aplicados | Criteria | texto o referencia a la descripción de producto |
| responsable_productor | Quien produce | Producer | nombre o rol |
| revisores | Quienes revisan | Reviewers | nombres separados con `;` |
| aprobador | Quien aprueba | Approver | nombre o rol |
| fecha_prevista | Fecha planificada | Planned date | ISO |
| fecha_real | Fecha real | Actual date | ISO |
| resultado | Resultado | Result | vacío o `aprobado`, `aprobado-con-observaciones`, `rechazado`, `pendiente` |
| estado | Situación | Status | inicial `planificada`; luego `en-curso`, `completada`, `cancelada` |
| notas | Observaciones, fuera de especificación generados (`I-###`) | Notes | texto |

## 9. acciones.csv · Action log

| Columna | Significado ES | Meaning EN | Valores permitidos / formato |
|---|---|---|---|
| id | Identificador | Unique id | `A-###` |
| fecha | Fecha de alta | Date raised | ISO (automático) |
| origen | De dónde sale el compromiso | Source | texto: reunión, informe o id (`R-004`, `I-002`, `acta-junta-2026-11-03`) |
| descripcion | Qué hay que hacer, con resultado verificable | Description | texto |
| responsable | Quién se comprometió | Owner | nombre o rol (obligatorio) |
| fecha_compromiso | Fecha comprometida | Due date | ISO; vencida si es anterior a hoy y sigue abierta |
| prioridad | Importancia | Priority | vacío o `alta`, `media`, `baja` |
| estado | Situación | Status | inicial `abierta`; luego `en-curso`, `completada`, `cancelada` |
| fecha_cierre | Cuándo se completó o canceló | Closed on | ISO (automático al pasar a `completada`) |
| notas | Avance, motivo de cancelación | Notes | texto |

*Una acción no es un issue:* es un compromiso concreto de una persona (de una reunión, de la respuesta a un riesgo o de la resolución de un issue). `registro.py resumen` lista las vencidas y las abiertas por responsable, que alimentan el tablero de avance y el highlight report.

## 10. diario.md · Daily log
Tabla Markdown con columnas `fecha`, `entrada`, `responsable`, `seguimiento`. Guarda issues informales, acciones pequeñas y observaciones; durante la puesta en marcha (SU) también riesgos e issues hasta que existen los registros formales. Ver `diario.md`.

## 11. Transiciones entre registros · Register transitions

| Origen | Evento | Destino | En origen | En destino |
|---|---|---|---|---|
| supuesto `abierto` | vence o resulta falso | riesgo (incierto) o issue (ya afecta) | `estado=transferido`, `notas=→ R/I-###` | `notas=origen S-###` |
| riesgo `abierto` | se materializa | issue | `estado=ocurrido`, `notas=→ I-###` | `notas=origen R-###` |
| riesgo `abierto` | excede autoridad del gestor | decisión de junta | `respuesta=escalar`, `estado=escalado` | `decisiones.csv` nivel `junta` |
| issue `abierto` | requiere cambiar línea base | cambio | `estado=pendiente-cambio`, `notas=→ C-###` | `notas=origen I-###` |
| reunión, riesgo o issue | genera compromiso de una persona | acción | `notas=→ A-###` | `origen=<id o reunión>` |
| issue | se resuelve | decisión + lección | `estado=cerrado`, `decision`, `fecha_cierre` | `D-###` y `L-###` referencian `I-###` |
| cambio | aprobado | línea base | `decision=aprobado`, `estado=implementado` | `estado.json.artefactos.<x>.version` |
| cambio aprobado | genera incertidumbre | riesgo | — | `notas=origen C-###` |
| cualquier registro | período de informe | highlight report | — | nuevos, cerrados y críticos con ids |

## Lista de verificación / Checklist
- [ ] Todas las columnas usadas existen en el CSV real creado por `nuevo_proyecto.py` (el script rechaza columnas desconocidas).
- [ ] Valores de enumeración escritos en minúsculas y sin acentos, según esta guía.
- [ ] Prefijos de id, estados iniciales y valores coherentes con `esquema.py` (comprobar con `registro.py esquema <registro>`).
- [ ] Ningún riesgo alto (≥15) abierto sin respuesta ni propietario; EMV calculado cuando hay impacto monetario.
- [ ] Filas de stakeholders con valoraciones sensibles marcadas `confidencial=si`.
- [ ] Cadencia de revisión y autoridad de cambio completadas desde el PID y `estado.json`.
- [ ] Transiciones aplicadas con referencia cruzada en ambos extremos.
- [ ] Guía revisada por el gestor del proyecto y marcada `aprobado` en el frontmatter cuando el equipo la adopte.
