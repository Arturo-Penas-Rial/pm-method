# Guía operativa de registros · Registers operating guide

Detalle de `pm-registros`. El SKILL.md cita cada sección por número. Columnas, valores y traducción ES/EN:
`templates/guia-registros.md` (idéntica al esquema de `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/esquema.py`).

## 1. Tabla de clasificación (en orden de preguntas)
| Pregunta | Si la respuesta es… | Registro destino |
|---|---|---|
| ¿Se da por cierto sin evidencia, o es una limitación impuesta? | Sí | `supuestos.csv` (tipo `supuesto` o `restriccion`) |
| ¿Podría ocurrir pero aún no ocurrió (incertidumbre)? | Sí | `riesgos.csv` (`amenaza` u `oportunidad`) → análisis en `pm-riesgos` |
| ¿Ya ocurrió o es seguro y requiere atención de la gestión? | Sí, sin pedir cambiar una línea base | `issues.csv` (`problema-preocupacion`, `evento-externo`, `oportunidad-negocio`) |
| ¿Pide modificar un producto aprobado o una línea base? | Sí | `issues.csv` tipo `solicitud-cambio` + fila en `cambios.csv` → `pm-issues-cambios` |
| ¿Un producto no cumple o no cumplirá su especificación? | Sí | `issues.csv` tipo `fuera-especificacion` (+ `cambios.csv` si se propone concesión) |
| ¿Alguien con autoridad ya resolvió algo? | Sí | `decisiones.csv` (nivel `equipo`, `product-owner`, `gestor`, `autoridad-cambio`, `junta`, `capa-negocio`) |
| ¿Es un compromiso concreto de una persona con fecha? | Sí | `acciones.csv` (una acción no es un issue) |
| ¿Es aprendizaje reutilizable (bueno o malo)? | Sí | `lecciones.csv` → `pm-lecciones-aprendidas` |
| ¿Es una persona o grupo que afecta o es afectado? | Sí | `stakeholders.csv` |
| ¿Es una actividad de verificación de un producto? | Sí | `calidad.csv` → `pm-calidad` |
| ¿Nada de lo anterior tiene impacto material? | — | `diario.md` |

Con BMAD (`integraciones.especificacion = bmad`): un desvío del PRD o de la arquitectura con línea base, o una Sprint
Change Proposal, es `solicitud-cambio`; en `notas` se citan los ids (FR-n, AD-n) y el sha corto, sin copiar requisitos.

## 2. Redacción de filas con calidad
- **Riesgo**: causa → evento → efecto en campos separados; propietario y ejecutor; en moneda: `impacto_monetario` (el script calcula `valor_esperado`), `disparador` y, con respuesta definida, `probabilidad_residual` e `impacto_residual`.
- **Issue**: uno de los cinco tipos, qué ocurre y desde cuándo, prioridad y severidad, responsable.
- **Cambio**: título, justificación, impactos por dimensión (aunque sea "ninguno").
- **Decisión**: enunciado preciso, contexto, opciones consideradas, quién decidió y a qué nivel.
- **Supuesto**: enunciado falsable, responsable de validar, categoría.
- **Lección**: situación → efecto → recomendación accionable.
- **Stakeholder**: rol, poder, interés, actitud, compromiso actual y deseado; `confidencial=si` si la valoración es sensible.
- **Calidad**: producto, método, criterios, revisores, aprobador.
- **Acción**: qué, quién, para cuándo y de dónde sale (`origen`: acta, riesgo, issue, reunión).

## 3. Escritura con `registro.py`
`python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> agregar <registro> --campo clave=valor …`. Asigna `id`,
fecha y estado inicial (`abierto` en riesgos, issues, cambios y supuestos; `registrada` en lecciones; `planificada` en
calidad; `abierta` en acciones); en riesgos calcula `puntuacion = probabilidad × impacto` y, con `impacto_monetario`,
`valor_esperado` (EMV, 1–5 → 10/30/50/70/90 %). Ante dudas: `registro.py esquema <registro>`. Valida columnas, valores y
P/I 1–5; acepta alias en inglés (`threat`, `high`, `open`, `change-request`…) y guarda el canónico. `--forzar` solo con
motivo en `notas`. Mostrar el id creado y la fila resumida; marcar `[por confirmar]` lo que el usuario no dio.

### 3.1 Bitácora y propuestas (2.6.0)
Cada escritura de un script queda en `<proyecto>/.bitacora.jsonl` (solo anexado, con huellas sha256 encadenadas; SPEC
§1.10.16): `registro.py historial R-003` (o `riesgos`, `estado`, `P-001`) muestra fecha y hora reales, script, operación,
`--por` y los campos antes → después, y verifica la cadena. Si un registro cambió fuera de los scripts (merge de git,
edición revisada), la sanidad avisa BIT-02 hasta que una persona lo asienta: `registro.py reconocer riesgos --por
"<rol: nombre>" --motivo "…"`. No hay deshacer: un error se corrige con otra escritura (y una decisión, con `reemplaza`).
Cuando un agente propone un cambio para que una persona lo revise después: `registro.py proponer <registro> [id]
--campo … --por "agente: <nombre>" --motivo "…"` (valida como agregar/actualizar y guarda `03-control/propuestas/P-###.json`
con la huella del registro y los valores base, sin escribir el registro); `registro.py propuestas` muestra qué pasaría
al aprobar hoy; la persona decide con `registro.py aprobar P-### --por "<rol: nombre>"` (no puede ser quien propuso; el
guardián pide confirmación) o `rechazar P-### --por … --motivo …`. Al aprobar: sin cambios en el registro se aplica; si
cambiaron otras filas u otros campos de la fila, se reaplica sobre la versión actual; si cambió un campo que la propuesta
toca, queda en `conflicto` con la base, el valor de hoy y el propuesto: volver a proponer. Las reglas de `registro.py`
(valores, integridad, control de cambios, vigencia) se aplican al aprobar; si no pasan, la propuesta sigue pendiente.

## 4. Actualizar y cerrar
`registro.py actualizar <registro> <id> --campo estado=.. --campo notas=".."`. Cerrar = cambiar `estado` y anotar qué se
decidió, quién y cuándo: `decision` + `decidido_por` + `fecha_cierre` en issues; `fecha_cierre` en acciones (automática al
completar); `fecha_decision` en cambios; `fecha_revision` en riesgos; `fecha_validacion` en supuestos. Una fila sin
propietario, decisión o fecha no se cierra. Pedido de borrar: ofrecer `estado=retirado` con nota.

## 5. Migraciones con referencia cruzada
| Origen → destino | Origen | Destino |
|---|---|---|
| Supuesto invalidado → riesgo o issue | `estado=transferido`, `notas=→ R-00X` | `notas=origen S-00X` |
| Riesgo materializado → issue | `estado=ocurrido` | `notas=origen R-00X` |
| Issue que pide cambiar línea base → cambio | `estado=pendiente-cambio` | `notas=origen I-00X` |
| Cambio aprobado que genera incertidumbre → riesgo | — | `notas=origen C-00X` |
Toda decisión resultante va a `decisiones.csv` con `artefactos_afectados` apuntando a los ids. Al aprobar un cambio,
sincronizar en la misma operación: `cambios.csv`, `decisiones.csv`, nueva versión del artefacto de línea base en
`estado.json.artefactos` y pregunta por riesgos nuevos (con BMAD, además nueva línea base vía pm-director).

## 6. Revisión periódica: qué buscar
| Registro | Señal de alerta | Acción propuesta |
|---|---|---|
| riesgos | `fecha_revision` anterior al período; acciones vencidas; sin propietario; alto (≥15) sin respuesta | marcar revisión vencida; listar en highlight; pedir propietario |
| issues | `responsable` vacío; `en-evaluacion` más de un período; `escalado` sin informe enlazado | asignar; pedir decisión; enlazar informe de issue |
| cambios | `pendiente-decision` sin fecha límite; `diferido` sin fecha de reevaluación | pedir decisión a la autoridad; fijar fecha |
| decisiones | `revisar_en` vencido (DEC-06); dos vigentes del mismo asunto que se contradicen sin `reemplaza` ni `conviven` (DEC-05); decisión de junta sin puerta en `estado.json` | reevaluar con quien decidió; marcar `reemplaza` (nivel igual o superior) o `conviven`; pedir a `pm-director` que regularice |
| supuestos | `fecha_validacion` vencida con `validado=pendiente` | validar o transferir a riesgo/issue |
| lecciones | `responsable_seguimiento` vacío; `registrada` varios períodos | asignar; llevar al informe de fin de etapa |
| stakeholders | compromiso actual ≠ deseado sin acción | derivar a `pm-comunicacion-stakeholders` |
| acciones | `fecha_compromiso` vencida con `abierta`/`en-curso`; responsable con muchas abiertas | pedir avance o replanificar; llevar al tablero |
| calidad | `fecha_prevista` pasada con `resultado=pendiente`; `rechazado` sin issue | reprogramar; abrir fuera de especificación |
| diario | tres o más entradas del mismo tema; pendientes vencidos | promover a registro formal; cerrar o reasignar |
Revisión cruzada: ningún hecho cierto en riesgos, ninguna incertidumbre en issues. Si hay instantáneas de un tracker en
`03-control/fuentes/` (`pm-integraciones`), comparar y proponer cambios a los registros; nunca aplicarlos en silencio.

## 7. Resumen para informes
`registro.py resumen [--corte AAAA-MM-DD] [--json]` (corte = fecha del informe o tablero): conteos por registro y estado,
top 5 de riesgos por puntuación, riesgos altos sin respuesta o propietario, acciones vencidas por responsable, issues sin
responsable. Completar con nuevos y cerrados del período, issues `escalado` o prioridad alta, cambios pendientes y
supuestos vencidos, siempre con ids. Entregar a `pm-progreso-reportes` o `pm-riesgos`.

## 8. Reglas extendidas
1. [PRINCE2] La acumulación de issues de un mismo tipo es señal de un problema de gestión y se anota como lección.
2. [PRINCE2] Solicitud de cambio y fuera de especificación son siempre formales, aunque estén dentro de la autoridad del gestor.
3. [PRINCE2] Las entradas sin revisar hace más de un período se marcan revisión vencida y se listan en el siguiente highlight.
4. [PMBOK→Issues] Cinco porqués para causa raíz; análisis de supuestos para poblar el registro; declarar `puntuacion = probabilidad × impacto`.
5. [PMBOK→Risk] El EMV es aproximado y se declara la convención; línea de tolerancia por defecto: ningún riesgo alto abierto sin respuesta y propietario.
6. [Plantillas] Un ítem por fila: riesgos, issues, lecciones y supuestos atómicos; causa raíz y no síntoma ("retraso" no es causa).
7. [Plantillas] Stakeholders con `confidencial=si` circulan solo entre quienes indique el gestor; al exportar, versión restringida y versión pública.
8. Señales de sesgo a nombrar: todos los riesgos "bajos", ninguna oportunidad, un único propietario para casi todo, ningún issue escalado en varios períodos.
9. Toda fila creada por el agente lleva en `autor` o `notas` que es propuesta del asistente.

## 9. Ejemplos adicionales
- "Pasame una revisión de todos los registros abiertos y decime qué está vencido."
- "The risk R-007 just happened. Convert it into an issue and link both."
- "Give me the register summary for this week's highlight report, with ids of anything critical."
