# Guía de dirección y decisiones · Directing guide

Detalle de `pm-direccion-decisiones` (agente `pm-director`). El SKILL.md cita cada sección por número.
Scripts: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py` y `registro.py`, `${CLAUDE_SKILL_DIR}/../pm-exportar/scripts/paquete.py`,
`${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py`, siempre con `--proyecto <dir>`.

## 1. Productos requeridos por puerta
| Puerta | Productos que deben existir y estar aprobados o listos para aprobación |
|---|---|
| autorizar-inicio | brief, descripción del producto del proyecto, business case esquemático (puede vivir en el brief), estructura de roles, `plan-etapa-1.md` (iniciación) con tolerancias |
| autorizar-proyecto (+ primera etapa) | PID completa (enfoques, controles, plan de proyecto, business case detallado), `plan-etapa-2.md` (primera etapa de entrega), lecciones revisadas, riesgos revisados. Perfil ágil mínimo: PID compacta, backlog priorizado y release plan en lugar de PBS/WBS completa. Con BMAD: PRD `final`, arquitectura suficiente para estimar y épicas iniciales (ver §8) |
| autorizar-etapa | `informe-fin-etapa-<n>`, `plan-etapa-<n+1>`, business case y plan de proyecto actualizados, estado de productos y concesiones otorgadas. Con BMAD: épicas e historias de la etapa siguiente y resultado del gate de preparación del sprint planning (PASS/CONCERNS/FAIL) |
| autorizar-plan-excepcion | `informe-excepcion-X-###`, `plan-excepcion-X-###`, business case y PID ajustados, evaluación de excepción |
| autorizar-cierre | `registro-aceptacion`, `informe-fin-proyecto`, `informe-lecciones`, `recomendaciones-seguimiento`, `plan-revision-beneficios`, business case original (`historial/business-case-v1.0.md`) y actual, PID original (`historial/pid-v1.0.md`) y actual, registros |
| decision-ad-hoc | issue report o solicitud escrita, evaluación de impacto sobre los siete objetivos y el business case |

Un obligatorio que falta o sigue en `borrador` es bloqueante declarado; `en-revision` es aceptable para lo que la puerta
aprueba. `paquete.py --proyecto <dir> listar puerta <tipo>` (o `listar cierre`) da obligatorios y faltantes sin crear ZIP.

## 2. Registro de la decisión de puerta (paso a paso)
Solo pm-director y solo después de una respuesta explícita de una persona identificada con su rol.
a. `estado.py puerta <tipo> --decision aprobado|condicionado|rechazado|pendiente --por "<rol: nombre>" [--condiciones ".."] [--fecha ..] [--etapa-nombre ".."] [--fin AAAA-MM-DD]`. El script escribe la fila en `decisiones.csv` (nivel `junta`, `notas=puerta: <tipo>`) y guarda su id en `puertas[].decision_id`; no agregar otra a mano. Para detallar opciones: `registro.py actualizar decisiones D-### --campo opciones_consideradas=".." --campo revisar_en=".."`.
b. Por cada documento aprobado: `estado.py aprobar <clave> --por "<rol: nombre>" --version 1.0`.
c. En `autorizar-proyecto` aprobado: copiar PID y business case a `00-direccion/historial/pid-v1.0.md` y `business-case-v1.0.md` (línea base congelada, `aprobado`, no se edita; el cierre compara contra ellas).
d. **Con BMAD activo** (`estado.json.integraciones.especificacion = bmad`): fijar la línea base de cada especificación aprobada en la puerta con `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> linea-base prd --version 1.0 --por "<rol: nombre>"` (y `arquitectura`, `epicas`, `brief`, `ux` según lo aprobado). Guarda sha256, ids y copia congelada en `00-direccion/historial/bmad-<art>-v<ver>/`. Tras un cambio aprobado, nueva línea base con versión mayor.
e. En `autorizar-etapa`: fijar las tolerancias de la nueva etapa con `estado.py tolerancia --nivel etapa ...` (la puerta vacía las anteriores).
f. Redactar `templates/acta-decision-junta.md` en `00-direccion/decisiones/AAAA-MM-DD-acta-junta-<puerta>.md` (clave `acta-junta-<fecha>`).
g. Si es `condicionado`: una acción por condición (`registro.py agregar acciones --campo origen=acta-junta-<fecha> --campo responsable=.. --campo fecha_compromiso=..`); cuando todas se cumplen y alguien con rol lo verifica, `estado.py cumplir-condiciones <tipo> --fecha AAAA-MM-DD --por "<rol: nombre>" --nota "evidencia"` (queda en la puerta y en `decisiones.csv`; falla si no hay condiciones abiertas de ese tipo). Con `condicionado`, `estado.py` suma solos a las condiciones los hallazgos de tipo condición de la verificación (p. ej. CONCERNS del gate de BMAD, P-04, P-06); una decisión `aprobado` con `--condiciones` (p. ej. `decision-ad-hoc`) también queda abierta. Mientras estén abiertas: sanidad EST-12 y G-01 en la verificación de las puertas siguientes (bloqueo en `autorizar-cierre`; o se cumplen o se traspasan como recomendación de seguimiento).

Efecto de cada decisión: `aprobado` y `condicionado` avanzan el ciclo de vida (autorizar-inicio → IP, etapa 1;
autorizar-proyecto → proyecto autorizado; autorizar-etapa → CS y etapa n+1 en fase `entrega`; autorizar-plan-excepcion →
vuelve a CS; autorizar-cierre → `cerrado`). `pendiente` no cambia nada ni escribe fila; la próxima decisión del mismo tipo
la marca resuelta. `rechazado` no avanza: la junta pide replanificar o el cierre prematuro.

## 3. Tolerancias y autoridad delegada
1. Nivel y quién fija: capa de negocio acuerda las de proyecto con la junta; la junta fija las de etapa; el gestor las de paquete.
2. Para cada objetivo (tiempo, costo, alcance, calidad, beneficios, riesgo, sostenibilidad): objetivo, desviación aceptada sin consulta, prioridad relativa; en unidades del objetivo. Las de etapa caben en las de proyecto.
3. `templates/tolerancias-y-autoridad.md` → `00-direccion/tolerancias-y-autoridad.md` (incluye autoridad de cambio, presupuesto de cambio y de riesgo). Tras la confirmación del ejecutivo: `estado.py tolerancia --nivel proyecto|etapa ...`, `estado.py rol autoridad_cambio=".."` (en ágil/híbrido también `product_owner=".."`), `estado.py presupuesto cambio=.. riesgo=.. gestion=.. limite_autoridad_cambio=.. --por "<rol: nombre>" [--fecha ..]` (montos sin moneda ni separador de miles; `estado.json` → `presupuestos`, con fila en `decisiones.csv`; la sanidad vigila su consumo con CAM-01…05) y, si hace falta detallar, una fila con `registro.py agregar decisiones` (nivel `capa-negocio` o `junta`). Las de paquete no van a `estado.json`. Formato y frecuencia de reporte se acuerdan en el mismo acto.

## 4. Evaluación de un informe de excepción
1. Flujo de entrada: `pm-control` detecta el pronóstico fuera de tolerancia (`pm-progreso-reportes`), prepara `03-control/reportes/<fecha>-informe-excepcion-X-###.md` con la plantilla de `pm-issues-cambios` y lo deriva. Leer desviación, causa, consecuencias de no actuar, opciones con efecto sobre business case, riesgos y tolerancias, recomendación y lecciones.
2. ¿Es excepción? Si cabe en la tolerancia de etapa, se devuelve al gestor como issue dentro de su autoridad. Si supera la de proyecto, la junta no decide sola: escalada a la capa de negocio.
3. `templates/evaluacion-excepcion.md` → `00-direccion/decisiones/AAAA-MM-DD-evaluacion-excepcion-X-###.md`. Opciones mínimas: (a) reasignar tolerancias / aceptar la desviación, (b) repriorizar o reducir alcance, (c) pedir plan de excepción, (d) más tiempo para decidir, (e) cierre prematuro; cada una cuantificada y con indicación de si está dentro de la autoridad de la junta.
4. Tras la decisión humana: (a) siempre `estado.py puerta decision-ad-hoc --decision aprobado --por ".." --condiciones "<opción elegida>"`; (b) si se pide plan de excepción: `estado.py limite-etapa --excepcion X-###` y encargo de `02-planificacion/plan-excepcion-X-###.md` a pm-planificacion (`pm-plan-etapa-y-limites`); opcional `puerta autorizar-plan-excepcion --decision pendiente`; (c) con el plan `en-revision`, solicitud `solicitud-autorizar-plan-excepcion` y decisión `autorizar-plan-excepcion` (aprobado → reemplaza al plan vigente, vuelve a CS; pasar `--fin` y `--etapa-nombre` si cambian); (d) cierre prematuro: §6.
5. Al cerrar la excepción, al menos una lección en `lecciones.csv` (`pm-lecciones-aprendidas`).

## 5. Dirección ad hoc
1. Clasificar: consejo informal (`diario.md`), issue escalado (fuera de especificación → rechazo o concesión; solicitud de cambio → verificar autoridad de cambio y presupuesto; si la junta lo aprueba sin saldo, indica la fuente: `cargo=reserva-gestion`, `cargo=plan-excepcion` o ampliar antes el presupuesto con `estado.py presupuesto cambio=<monto> --por …`, porque `registro.py` rechaza `presupuesto-cambio` sin saldo también para la junta; guía de `pm-issues-cambios` §4.1), cambio del entorno o del mandato.
2. Cambio del mandato: dos vías, ambas cuantificadas: solicitud de cambio (replanificar con evaluación de impacto de `pm-issues-cambios`) o cerrar prematuramente y arrancar un proyecto nuevo.
3. Nota de decisión de una página (`templates/solicitud-puerta.md` versión mínima, `AAAA-MM-DD-solicitud-decision-ad-hoc.md`), decisión humana y registro con `estado.py puerta decision-ad-hoc` (junta) o `registro.py agregar decisiones --campo nivel=autoridad-cambio` (no es puerta).
4. Con BMAD: un desvío detectado por `bmad.py verificar` o una Sprint Change Proposal llega como issue `solicitud-cambio`; el "sí" dado dentro del flujo correct-course de BMAD no sustituye la decisión de la autoridad de cambio PRINCE2.

## 6. Cierre prematuro y cierre normal
- **Prematuro**: `estado.py puerta decision-ad-hoc --decision aprobado --por ".." --condiciones "cierre prematuro: <motivo>"` y `estado.py cierre --prematuro` (→ CP). Derivar a `pm-cierre` (rescatar productos, documentar lo incompleto); `autorizar-cierre` se decide igual al final.
- **Normal**: `pm-cierre` entra a CP con `estado.py cierre`, prepara los productos `en-revision` y deriva. pm-director verifica con `paquete.py listar cierre`, compone `solicitud-autorizar-cierre`, obtiene la decisión y registra `puerta autorizar-cierre` (→ `cerrado`) y `aprobar` por producto. La notificación la emite `pm-comunicacion-stakeholders`.

## 7. Mapa de puertas, disparadores y quién decide
| Puerta | Llega desde | Rol que decide | Salida hacia |
|---|---|---|---|
| autorizar-inicio | SU (solicitud de iniciación) | Ejecutivo | IP, etapa 1; notificación de inicio a la capa de negocio |
| autorizar-proyecto (+ autorizar-etapa para la etapa 2) | IP | Junta (ejecutivo A/R) | CS, etapa 2; notificación de autorización |
| autorizar-etapa / autorizar-plan-excepcion | SB | Junta | CS con la nueva línea base |
| decision-ad-hoc | CS (consejo, excepción, issue escalado) o capa de negocio | Junta o ejecutivo (la autoridad de cambio registra con `registro.py`) | CS; SB (`limite-etapa --excepcion`); CP (`cierre --prematuro`) |
| autorizar-cierre | CP | Junta, con refrendo de la capa de negocio si aplica | `cerrado`; notificación de cierre; disolución de la junta |

## 8. BMAD en las puertas (si `integraciones.especificacion = bmad`)
- Checklist previo a toda puerta: `bmad.py verificar` ejecutado en el período; resultado limpio, o cada desvío (ids agregados/retirados, contenido distinto, Sprint Change Proposal nueva) convertido en issue `solicitud-cambio` con decisión o tratamiento indicado en la solicitud de puerta.
- `autorizar-proyecto`: PRD con `status: final` (si no, aprobar a lo sumo `condicionado` con la condición "PRD final antes de <fecha>"); trazabilidad FR→historias→paquetes sin huecos críticos (`bmad.py trazabilidad`).
- `autorizar-etapa`: resultado del gate de preparación del sprint planning de BMAD (CONCERNS o FAIL = riesgo o condición); avance desde `03-control/reportes/avance-bmad.csv`.
- `autorizar-cierre`: aceptación por requisito con la matriz de trazabilidad (ver `pm-cierre-proyecto`).
- Tras la decisión: `bmad.py linea-base …` (§2.d). pm-method nunca escribe en las carpetas de BMAD.

## 9. Reglas extendidas
1. [PRINCE2] Si otro agente registró una puerta, se regulariza aquí y se anota.
2. [PRINCE2] Si el usuario dice "aprobalo vos", responder que no corresponde al método y pedir que una persona con rol lo haga.
3. [PRINCE2] Sin mandato identificable no se prepara `autorizar-inicio`.
4. [PRINCE2] Un plan de excepción rechazado no se ejecuta: la etapa sigue bajo dirección de la junta hasta un plan revisado.
5. [PRINCE2] Un fuera de especificación solo admite rechazo (se completa el producto) o concesión (se acepta incompleto y se actualiza la descripción de producto).
6. [PRINCE2] Las delegaciones (aseguramiento, autoridad de cambio) no trasladan la responsabilidad final de la junta; el gestor nunca ejerce decisiones del ejecutivo.
7. [PMBOK→DP/Business case] Comparar opciones con análisis de alternativas o multicriterio con pesos explícitos; con incertidumbre, árbol de decisión con EMV (`pmbok8-artefactos-tecnicas-anexos.md` `### 3.4`, `### 5.1`).
8. [PMBOK→DP] Guardarraíl de IA: toda salida que implique compromiso incluye el bloque "Decisión pendiente de aprobación humana — requiere decisión de [rol]"; intervención etiquetada como asistencia (`### 5.3`).
9. [PMBOK→DP] No inventar nombres, fechas ni cifras ("dato no disponible: solicitar a [fuente]"); no infundir urgencia ni sesgar hacia "continuar".
10. [PMBOK→Organizing/DP] Comunicación con el patrocinador: primero la decisión que se pide, luego el contexto; una página; detalle en anexos.
11. [Plantillas] Versión mínima: solicitud de una página y acta de cinco líneas; completa cuando riesgo, costo o stakeholders lo justifiquen.
12. [Plantillas] Una decisión reabierta no se borra: se marca reemplazada y se crea una fila nueva que la referencia.

## 10. Columnas de `decisiones.csv`
`id` (D-###) · `fecha` (date) · `decision` · `contexto` (puerta/excepción/ad hoc) · `opciones_consideradas` ·
`decidido_por` (nombre y rol) · `nivel` (`equipo` | `product-owner` | `gestor` | `autoridad-cambio` | `junta` |
`capa-negocio`; `product-owner` = intercambio de ítems del backlog dentro de la tolerancia de alcance de la etapa) ·
`artefactos_afectados` · `revisar_en` · `notas`.

## 11. Calidad ampliada
- Una página para la versión ejecutiva; anexos para el detalle.
- Solicitud `en-revision` hasta la decisión; acta `aprobado` solo con `aprobado_por` del ejecutivo.
- En excepciones: nivel de tolerancia superado verificado con pronóstico; al menos una opción sin plan de excepción y una con él.
- En tolerancias: siete objetivos, unidades, prioridad relativa y coherencia hacia arriba.
- Ninguna decisión del ejecutivo tomada por el gestor; si se detecta, se señala como incumplimiento del método.

## 12. Ejemplos adicionales
- "Fijá las tolerancias de la etapa 1: ±10 días, ±5 % de costo, alcance según PBS, y definí la autoridad de cambio."
- "The board approved stage 3 with conditions; record the decision and open the follow-up actions."
- "Set project-level tolerances with the business layer and delegate a change budget of 20k."
- "La junta aprobó el PRD en la puerta; fijá la línea base de la especificación."
