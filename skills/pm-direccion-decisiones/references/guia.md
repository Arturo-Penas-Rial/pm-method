# Guía de dirección y decisiones · Directing guide

Detalle de `pm-direccion-decisiones` (agente `pm-director`). El SKILL.md cita cada sección por número.
Scripts: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py` y `registro.py`, `${CLAUDE_SKILL_DIR}/../pm-exportar/scripts/paquete.py`,
`${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py` y `${CLAUDE_SKILL_DIR}/scripts/decision.py` (§13), siempre con `--proyecto <dir>`.

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
- **Prematuro** (`docs/PUERTAS.md` §3.2): la decisión de la junta es el rechazo de la puerta (`puerta autorizar-proyecto|autorizar-etapa|autorizar-plan-excepcion --decision rechazado --por ".." [--motivo ".."]`; el aviso muestra la D-###) o, fuera de una puerta, `estado.py puerta decision-ad-hoc --decision aprobado --por ".." --motivo "cierre prematuro: <razón>"` (con `--motivo`, no con `--condiciones`: una condición abierta bloquearía `autorizar-cierre` por G-01). Luego `estado.py cierre --prematuro --decision D-###` (→ CP, desde la iniciación o la entrega; en el pre-proyecto no hay cierre: `autorizar-inicio` rechazado). Derivar a `pm-cierre` (inventario por estado, rescate, estado seguro, brechas); `autorizar-cierre` se decide igual al final, con C-08 (inventario) y C-07 como aviso.
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
7. [PMBOK→DP/Business case] Comparar opciones con análisis de alternativas o multicriterio con pesos explícitos (`decision.py matriz`, §13); con incertidumbre, árbol de decisión con EMV (`pmbok8-artefactos-tecnicas-anexos.md` `### 3.2`, `### 3.4`, `### 5.1`).
8. [PMBOK→DP] Guardarraíl de IA: toda salida que implique compromiso incluye el bloque "Decisión pendiente de aprobación humana — requiere decisión de [rol]"; intervención etiquetada como asistencia (`### 5.3`).
9. [PMBOK→DP] No inventar nombres, fechas ni cifras ("dato no disponible: solicitar a [fuente]"); no infundir urgencia ni sesgar hacia "continuar".
10. [PMBOK→Organizing/DP] Comunicación con el patrocinador: primero la decisión que se pide, luego el contexto; una página; detalle en anexos.
11. [Plantillas] Versión mínima: solicitud de una página y acta de cinco líneas; completa cuando riesgo, costo o stakeholders lo justifiquen.
12. [Plantillas] Una decisión reabierta no se borra: se marca reemplazada y se crea una fila nueva que la referencia
    (columna `reemplaza` de la fila nueva, con nivel igual o superior al de la reemplazada; §13.10). No hay deshacer: la
    bitácora de escrituras (`registro.py historial D-###`, SPEC §1.10.16) muestra quién escribió cada versión de la fila.

## 10. Columnas de `decisiones.csv`
`id` (D-###) · `fecha` (date) · `decision` · `contexto` (puerta/excepción/ad hoc) · `opciones_consideradas` ·
`decidido_por` (nombre y rol) · `nivel` (`equipo` | `product-owner` | `gestor` | `autoridad-cambio` | `junta` |
`capa-negocio`; `product-owner` = intercambio de ítems del backlog dentro de la tolerancia de alcance de la etapa) ·
`artefactos_afectados` · `revisar_en` (AAAA-MM-DD para que la sanidad la controle, DEC-06; o un hito en texto) · `notas` ·
`reemplaza` (D-### que esta decisión deja sin efecto, separados por `;`) · `conviven` (D-### que la persona decidió
mantener vigentes a la vez aunque parezcan contradecirse). "Reemplazada por" se deriva (§13.10).

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

## 13. Decisiones con contexto: expediente, matriz multicriterio y pregunta tipada (`decision.py`)

**Para qué.** Cualquier decisión que elige entre alternativas (la respuesta a un riesgo, la opción de negocio, qué entra
en un release, qué OKR se adopta, qué hacer con un cambio, a qué proveedor se adjudica) necesita tres cosas que en la
práctica faltan: el **contexto aplicable** reunido en un solo lugar y con su fuente, una **comparación con pesos
explícitos** que se pueda revisar (y que muestre cuánto depende de esos pesos) y una **pregunta cerrada** que el modelo o
la junta respondan sin salirse de las opciones. `decision.py` hace las tres sin modelo propio y sin decidir.

**Fundamento.** PRINCE2 7 manda: la junta decide y el gestor recomienda (`prince2-principios-personas-procesos.md`
`### 6.10`, matriz de decisiones por rol; `## 8.` reglas 25–28), y toda decisión queda registrada (registro del
proyecto: `prince2-practicas-bc-organizacion-planes-calidad.md` `#### 1.4.2`; aquí, `decisiones.csv`). El PMBOK 8 aporta
la técnica: análisis de decisiones multicriterio, "puntaje = Σ (peso × puntuación)", con la trampa de los "pesos
acomodados para que gane la opción deseada" (`pmbok8-artefactos-tecnicas-anexos.md` `### 3.4`); análisis de
alternativas sin omitir "no hacer nada" y análisis de sensibilidad (`### 3.2`); guardarraíles 36 (el agente no toma
decisiones de gobierno), 38 (dato no disponible), 41 (criterios y pesos explícitos) y 43 (la técnica más simple que
responde la pregunta) en `### 5.3`. De los modelos de decisión tipada (Laya, TypeSafe Jev) se toman tres ideas, no el
modelo: pregunta tipada, respuesta restringida a las opciones y abstención explícita.

### 13.1 Tipos de decisión y quién decide

| Tipo (`--tipo`) | Qué se compara | Criterios de la plantilla (`templates/criterios-por-tipo.csv`) | Cifras que entran sin recalcular | Nivel que propone el script |
|---|---|---|---|---|
| `riesgo` | respuestas a un riesgo, o qué riesgo atender primero | valor neto, apetito (eliminatorio < 2), riesgo secundario, factibilidad, plazo para actuar | `riesgos.py opciones --json` (valor neto, EMV residual, costo) | `gestor` (propietario del riesgo); `junta` si el riesgo está escalado; muestra el saldo del presupuesto de riesgo |
| `negocio` | opciones del business case | VAN, beneficios fuera del VAN, riesgo, ajuste estratégico | `inversion.py --json` (VAN, TIR, repago) | `ejecutivo` (dueño del business case, `#### 6.3.1`); en una puerta, la junta |
| `planificacion` | alcance de un release, secuencia, replanificación dentro de la etapa | valor, dependencias, capacidad (holgura), riesgo | `release.py capacidad --json` (holgura), último corte de `evm.py` | `gestor`; `junta` si los Must no entran o el EVM pronostica excepción; intercambios del backlog: product owner |
| `okr` | alternativas de objetivos y KR | alineación con beneficios (eliminatorio < 2), medibilidad (eliminatorio < 2), esfuerzo | `okr.py --json` (puntuación y salud) | `ejecutivo` (o el usuario sénior dueño del beneficio, `pm-okr` paso 12) |
| `cambio` | aprobar, rechazar, diferir, pedir plan de excepción | impacto, tolerancias, autoridad | `impacto.py analizar --json` (tabla de impacto, nivel y motivos) | el de `impacto.py`; sin él, la regla `motivos_autoridad` de `registro.py`: autoridad de cambio dentro del límite y del saldo, si no la junta |
| `adquisicion` | proveedores o modalidades; con `--criterios hacer-o-comprar`, hacer o comprar un componente (§13.11) | costo del ciclo de vida, riesgo, calidad (eliminatorio < 2), dependencia; hacer o comprar: diferenciación, costo total, tiempo hasta disponible, dependencia del proveedor, capacidad interna, riesgo de construir algo que va a volverse commodity | — (los puntajes salen de `pm-adquisiciones/templates/criterios-seleccion.md`, congelados antes de las ofertas; en hacer o comprar, del caso, cotizaciones, estimaciones y el mapa de Wardley) | `ejecutivo` (autoridad de la organización; la estrategia se aprueba con el plan) |

El nivel queda en `decision.json` (`nivel`, `quien`) y se puede corregir a mano; el expediente avisa si difiere de la regla.

### 13.2 Expediente: el contexto aplicable, con fuente y con tope

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/decision.py --proyecto <dir> expediente --tipo riesgo --ids R-007 \
    --pregunta "¿Qué respuesta damos a R-007?" [--tema "norma de biometría"] [--hoja ID] [--importar F.json …] \
    [--saltos 1|2] [--max-items 8] [--max 9000] [--corte AAAA-MM-DD] [--historia] [--salida RUTA] [--json]
```

Solo lectura. Arma, en este orden: (1) pregunta, tipo, forma y **nivel que decide** con sus motivos; (2) tolerancias de
proyecto y de etapa y presupuestos de la junta con su consumo en `cambios.csv` (misma regla que CAM-03); (3) líneas del
business case con beneficios `B-n`/`DB-n` (las citadas por los registros relacionados; todas en `negocio` y `okr`) y
líneas de **apetito** del enfoque de riesgo y del business case, cada una con `archivo:línea`; (4) **registros
relacionados** a `--saltos` de los ids de partida, en los dos sentidos: los ids que cita cada fila y las filas que lo
citan, más las columnas de referencia de `esquema.py` (`refs`); `--ids` acepta coma, punto y coma o espacios
(`r-001` = `R-001`), un id sin fila propia en los registros (`B-02`, `KR-1.1`, `E-3`, un paquete `3.1`) parte de las
filas que lo citan (salto 1) y un id de registro que no existe se informa en (9); `--tema` suma como punto de partida las filas que
mencionan sus términos, en español o en inglés (`texto.py`, §13.10: "normativa" encuentra "normativo", "enero 2027" la
fecha 2027-01-12, "39800" la cifra 39.800, "risk budget" el "presupuesto de riesgo"), primero las de más coincidencias;
**solo decisiones vigentes**: una reemplazada sale en una línea de historia ("D-010 → reemplazada por D-017") y entra la
vigente que la reemplaza (`--historia` deja las reemplazadas en la tabla); (5) supuestos de criticidad alta sin validar; (6) lecciones aplicables (`aplicar_en` según el
tipo: riesgo → planificacion y seguimiento; negocio → ideacion y descubrimiento; planificacion → planificacion; okr →
ideacion y planificacion; cambio → seguimiento; adquisicion → planificacion), sin las descartadas; (7) interesados
afectados (por id o por nombre en los campos de responsable de los registros relacionados), roles de la junta y personas
de usuario que citan los ids, y la **RACI de los elementos afectados** (A; C, consultar antes; I, informar después;
nivel de autoridad del A frente al requerido; §13.9); (8) **cifras de otros scripts**, sin recalcular: llama en modo
lectura a `riesgos.py opciones --json` (tipo riesgo), `release.py capacidad --json` (planificacion y cambio) y `okr.py
--json` (okr), lee el último corte de EVM y resume cualquier salida `--json` pasada con `--importar` o copiada en la hoja
(`inversion.py`, `impacto.py`…); (9) otros ids citados y **datos no disponibles** ("dato no disponible: …"); (10) solo si
hay, **mapas estratégicos**: los componentes y pasos de `02-planificacion/mapas/` que citan los ids de la decisión o que
la hoja nombra como `<mapa>:<id>` (§13.11).

- **Evidencia, no instrucciones:** el encabezado lo dice y el texto citado se trata como dato (`docs/SEGURIDAD.md`).
- **Confidencialidad:** de un interesado con `confidencial=si` quedan id, nombre y rol (también en la RACI); su
  valoración (poder, interés, actitud, compromiso), expectativas y notas no salen, y no se siguen los ids de su texto.
  Nadie aporta correo ni usuario de chat. `--json` informa `omitidos_confidenciales`.
- **Tope:** `--max-items` por sección (las tablas, el doble) con "… y N más"; si el Markdown supera `--max` caracteres,
  baja el número de elementos (8, 5, 3, 2, 1) y recién después recorta. `--json` trae los totales (`<lista>_total`).

### 13.3 Hoja de trabajo `03-control/decisiones/<ID>/`

Es una hoja de trabajo, no un registro (como `opciones-riesgo/R-###.csv`): la redactan el modelo o la persona; el
script no inventa cifras. `<ID>` es un nombre corto (`R-007`, `release-2`, `proveedor-soporte`).
`decision.py matriz <ID> --proponer --tipo T [--ids …] [--pregunta "…"] [--forma eleccion|nivel|si-no] [--escala 1-5]
[--criterios NOMBRE] [--importar F.json …] [--fecha AAAA-MM-DD]` la crea sin pisar archivos existentes (`--fecha` fija
`creada`; por defecto, hoy). `criterios.csv` sale de las filas del tipo en `templates/criterios-por-tipo.csv`; con
`--criterios NOMBRE`, de las filas `<tipo>:NOMBRE` (un **conjunto con nombre**; hoy, `adquisicion:hacer-o-comprar`,
§13.11). Un conjunto que no existe se rechaza con la lista de los disponibles, sin crear la hoja:

- `decision.json`: `id`, `tipo`, `pregunta`, `forma` (`eleccion` entre opciones, `nivel` en una escala, `si-no`),
  `escala`, `ids` (un componente o un paso de un mapa se nombra `<mapa>:<id>`, §13.11), `nivel` y `quien` (de §13.1),
  `creada`, `idioma`, `criterios` (el conjunto con nombre, si se usó); tras la decisión, `eleccion` (§13.5).
- `criterios.csv`: `criterio` (letras, dígitos y `_`), `descripcion`, `peso` (≥ 0; si no suman 100 se normalizan con
  aviso), `sentido` (`mayor` o `menor` es mejor), `escala` (`a-b`, p. ej. `1-5`, o `num` para cifras sin tope como el VAN
  o un costo), `eliminatorio` (umbral: con `mayor`, se elimina la opción con un valor menor; con `menor`, la de un valor
  mayor), `importar` (`campo` o `archivo.json:campo` de una salida importada), `fuente_peso` (de dónde sale el peso:
  enfoque, junta, taller…; `[por confirmar]` cuenta como sin fuente), `notas`.
- `opciones.csv`: `opcion` (O1, O2…), `descripcion`, `ref` (la opción en el JSON importado: `R-007/O2`, `1 · Mínimo`,
  `R2`…; vacía = `opcion`), y por criterio dos columnas: `<criterio>` (puntaje) y `<criterio>_fuente` (id, archivo o
  persona); `notas`. Números simples, con punto o coma decimal, sin moneda ni separador de miles (`2.500` es ambiguo y
  se rechaza).
- Salidas `--json` importadas: `--importar F.json` las copia en la hoja con su nombre de archivo (la evidencia queda
  con la decisión; en una llamada posterior, una copia con el mismo nombre se reemplaza con aviso; dos `--importar` con
  el mismo nombre en la misma llamada son un error: renombrar uno, p. ej. `release-a.json` y `release-b.json`). En `riesgo` con `--ids R-###`, `--proponer` corre `riesgos.py opciones
  --riesgo R-### --json`, guarda `riesgos-opciones-R-###.json` y crea una opción por respuesta con la misma numeración y
  `ref` `R-###/O#`; en `negocio`, toma las opciones del JSON de `inversion.py` importado.

Los JSON se indexan por `opcion`, `id`, `release` o `cambio` (y los objetos de un diccionario, por su clave). **Regla
con varias salidas importadas** (determinista): si la `ref` de la opción nombra el archivo (`release-b.json:R1`) o el
criterio lo nombra en `importar` (`release-b.json:holgura`), la cifra se busca solo ahí (si nombran archivos distintos,
es un error); si no, la `ref` con ese campo debe estar en un solo objeto de un solo archivo. Si está en dos archivos, o
dos veces en uno, no se toma ninguna (ni la primera ni la última): la opción queda inválida con un error que dice dónde
está y cómo calificarla (`archivo.json:ref`, o `R-001/O2` con su padre). Si la hoja trae también una cifra para un
criterio importado y difiere, se usa la importada con aviso.

### 13.4 Cálculo, eliminatorios, dominadas, sensibilidad y abstención

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/decision.py --proyecto <dir> matriz <ID> [--importar F.json] [--margen 2] \
    [--umbral-sensibilidad 5] [--max 12] [--markdown [RUTA]] [--json]
```

1. **Validación:** criterios con nombre, peso, sentido y escala válidos; puntajes numéricos y dentro de la escala; un
   valor inválido deja la opción `invalida` y el comando termina con código 1 (sin recomendación).
2. **Eliminatorios:** la opción que no pasa un umbral queda `eliminada` y fuera de la normalización.
3. **Huecos:** una opción no eliminada con un puntaje faltante queda `por-confirmar`; si hay alguna, o menos de dos
   evaluadas, la matriz **se abstiene**: `accion = pedir-informacion`, sin recomendada y con la lista de lo que falta
   (no se rankea con huecos).
4. **Normalización** de cada puntaje x a 0–1: escala `a-b` → (x − a)/(b − a); escala `num` → (x − mín)/(máx − mín) entre
   las opciones evaluadas (si todas son iguales, 1); sentido `menor` → 1 − valor. **Puntaje** = 100 × Σ (peso/Σ pesos) ×
   valor normalizado.
5. **Dominadas:** una opción es dominada si otra es igual o mejor en todos los criterios y mejor en al menos uno; se
   marca, no se elimina.
6. **Recomendada** (propuesta, no decisión): la de mayor puntaje; **empate** si otra queda a `--margen` puntos o menos.
7. **Sensibilidad de los pesos:** para cada criterio, el peso se mueve de 0 a 100 y los demás conservan sus proporciones;
   el puntaje de cada opción es lineal en ese peso, y el script informa el peso con el que otra opción pasa a primera,
   hacia abajo y hacia arriba ("estable" si ninguno la cambia; tocar 0 o 100 solo empata). **Sensibilidad baja** si
   algún peso cambia la primera moviéndose `--umbral-sensibilidad` puntos o menos. Ataca la trampa de los pesos
   acomodados: muestra cuánto habría que mover un peso para que gane otra.
8. **Avisos:** pesos que no suman 100, pesos o puntajes sin fuente, criterio importado sin datos en la hoja, menos de
   dos opciones y ninguna opción del tipo "no hacer nada" (`### 3.2`).

La tabla sale en el orden de la hoja (la recomendada se marca con ★ después del cálculo), para no inducir a elegir por
posición. `--markdown` escribe el bloque para la sección de opciones de `templates/solicitud-puerta.md` o
`templates/evaluacion-excepcion.md` (por defecto `<hoja>/matriz.md`).

**Ejemplo a mano** (caso DC de `probar_paquete.py`): costo (`num`, menor) peso 4, calidad (`1-5`, mayor) 4, riesgo
(`1-5`, menor) 2 → pesos 40/40/20 con aviso. Proveedor A (100, 4, 2), B (150, 5, 1), C (200, 3, 3). Normalizados: costo
A 1, B 0,5, C 0; calidad A 0,75, B 1, C 0,5; riesgo A 0,75, B 1, C 0,5. Puntajes: A = 100 × (0,4 × 1 + 0,4 × 0,75 + 0,2 ×
0,75) = 85; B = 80; C = 30 (dominada por A). Sensibilidad: si el peso del costo baja de 40 a 33,3, gana B; si el de
calidad sube a 50, también; la mínima es 6,7 puntos, así que no es "baja" con el umbral 5. Con calidad eliminatoria 4,
C sale y el costo se normaliza entre 100 y 150: A 85, B 60.

### 13.5 Elegir y registrar (puerta humana)

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/decision.py --proyecto <dir> matriz <ID> --elegir O# --por "<rol: nombre>" \
    [--motivo "…"] [--nivel equipo|product-owner|gestor|autoridad-cambio|ejecutivo] [--decision D-###] [--reemplaza D-###] \
    [--fecha AAAA-MM-DD] [--revision AAAA-MM-DD] [--sin-aviso]
```

- Sin `--por` no registra nada. `--motivo` es obligatorio si la elegida no es la recomendada, si hay empate, si la
  sensibilidad es baja o si la matriz se abstuvo. Una opción eliminada o inválida no se puede elegir (si el umbral no
  aplica, se corrige `criterios.csv`).
- **Nivel:** por defecto el de `decision.json`; `--nivel` no puede ser menor. Las decisiones de **junta** o **capa de
  negocio** las registra pm-director (`estado.py puerta decision-ad-hoc --decision … --por …`); después
  `--decision D-###` completa esa fila con la matriz (opciones consideradas si estaban vacías, la hoja en
  `artefactos_afectados`, la elección y el contexto en `notas`) sin crear otra. Con `--decision`, el nivel es el de esa
  fila (no se usa `--nivel`: si difiere, avisa) y no puede ser menor que el de la hoja.
- **Fila nueva** (`registro.py agregar decisiones`): `decision` = pregunta y opción; `contexto` = hoja, criterios con su
  peso normalizado, recomendada (y empate o sensibilidad baja si los hubo); `opciones_consideradas` = cada opción con su
  puntaje o su estado; `nivel`; `artefactos_afectados` = hoja e ids; `notas` = motivo.
- **Riesgos:** si la opción tiene `ref` `R-###/O#`, el registro lo hace `riesgos.py opciones --riesgo R-### --elegir O#`
  (misma regla, respuesta y residual en `riesgos.csv` y una sola decisión); si la matriz recomendó esa opción y
  `riesgos.py` recomendaba otra por valor neto, el motivo que recibe es "recomendada por la matriz multicriterio <ID>".
  `--revision AAAA-MM-DD` pasa a `riesgos.py --revision` la próxima revisión del riesgo (`fecha_revision`); en una hoja
  que no es de riesgo se rechaza: la revisión de esa decisión va en su columna `revisar_en`. Luego `decision.py` agrega
  la matriz a las notas de esa decisión.
- **Forma `nivel` o `si-no`:** `--elegir 4` (un valor de la escala) o `--elegir si|no`; registra la decisión sin matriz.
- **RACI** (§13.9): `--motivo` también es obligatorio si quien decide no es el A de un elemento afectado ni una
  autoridad superior; una incoherencia entre el A y el nivel requerido se avisa; tras registrar, recuerda a los C y
  prepara el borrador del aviso a los I (`--sin-aviso`: solo el comando).
- La elección queda en `decision.json` → `eleccion` (opción, recomendada, motivo, D-###, quién, nivel, fecha, puntajes,
  huella de la hoja; con RACI, `raci`: elementos, A, motivos por no ser el A, incoherencias y carpeta del aviso; con un
  elemento de un mapa en los ids, `mapas`: las citas `archivo#id` donde quedó la decisión, §13.11). Un
  segundo `--elegir` se rechaza: una decisión reabierta no se borra (§9, regla 12), se abre una hoja nueva que la cita
  y se elige con `--reemplaza D-###` (o `"reemplaza": "D-###"` en su `decision.json`): la autoridad se valida antes de
  registrar nada y la columna `reemplaza` queda en la fila (también con `--decision` o vía `riesgos.py`).

### 13.6 Pregunta tipada y validación de una respuesta

`decision.py pregunta <ID> [--max 9000] [--corte AAAA-MM-DD] [--json]` produce (con `--corte`, el expediente incluido
usa esa fecha, como `expediente --corte`), para el modelo o para la junta: la pregunta, el tipo, la forma
y quién decide; las opciones válidas en el orden de la hoja con su puntaje (las eliminadas no figuran entre las
respuestas posibles); el **formato cerrado** de la respuesta

```json
{"respuesta": "O1 | O2 | pedir-informacion", "evidencia": ["R-007", "inversion.json"], "confianza": "alta | media | baja", "faltan": [], "razon": "…"}
```

(en forma `nivel`, un valor de la escala; en `si-no`, `si` o `no`); las reglas (solo valores de la lista, al menos una
evidencia del expediente, `pedir-informacion` con lo que falta en lugar de suponer, no elegir por el orden); la matriz
y el expediente. `pregunta <ID> --validar RESPUESTA.json` (o `-` para la entrada estándar) comprueba: que sea JSON con
`respuesta`; que la respuesta sea una opción existente y evaluada (ni eliminada, ni por confirmar), un valor de la
escala o sí/no; que cada evidencia cite un id o un archivo que está en el expediente o en la hoja; que, si la hoja tiene
datos por confirmar, la única respuesta válida sea `pedir-informacion`; y que una abstención liste qué falta. Código 1
si no es válida; avisa si difiere de la recomendada. **No decide ni registra:** la respuesta validada es insumo para
quien decide.

### 13.7 Controles de sanidad (familia DEC, solo avisos)

Sobre las hojas con una decisión registrada (`decision.json` con `eleccion`): **DEC-01** si se eligió una opción distinta
de la que hoy recomienda la matriz sin motivo registrado (incluye el caso en que la hoja se modificó después de decidir:
cambia su huella) o si la decisión citada no existe en `decisiones.csv`; **DEC-02** si la decisión se tomó con pesos o
puntajes sin fuente. Las hojas sin decisión no se revisan: mientras se trabaja, los avisos los da `matriz`.

Con `raci.csv` (§13.9), sobre todas las hojas y sobre las decisiones D-### que son elementos de la RACI: **DEC-03** si
decidió quien no es el A de un elemento afectado ni una autoridad superior y no hay motivo (en la hoja, `eleccion.motivo`;
en una D-###, la columna `notas`; aparece, por ejemplo, si la RACI cambia de A después de decidir); **DEC-04** si el A
del elemento no tiene la autoridad del nivel requerido (`decision.json.nivel` o la columna `nivel` de la D-###), solo
cuando el nivel del A se puede determinar (objetivo). Un elemento sin A ya lo marca STK-02.

Sobre `decisiones.csv`, haya hojas o no (§13.10): **DEC-05** dos decisiones vigentes del mismo asunto que parecen
contradecirse sin `reemplaza` ni `conviven`; **DEC-06** `revisar_en` vencido sin una decisión posterior del mismo asunto y con el asunto todavía abierto.

### 13.8 Recetas por tipo

- **Riesgo:** `riesgos.py opciones --riesgo R-007 --proponer` y completar → `decision.py matriz R-007 --proponer --tipo
  riesgo --ids R-007` → puntuar apetito, factibilidad, plazo y secundario con su fuente → `matriz R-007` → `--elegir`.
  Para priorizar varios riesgos: una opción por riesgo con `ref` = su id e `importar` `puntuacion` o `emv_inherente`
  del JSON de `riesgos.py opciones --json`.
- **Negocio:** `inversion.py flujos.csv --tasa 0.10 --json > inversion.json` → `matriz opciones-bc --proponer --tipo
  negocio --importar inversion.json` (una opción por alternativa, VAN importado).
- **Planificación:** `release.py --proyecto <dir> capacidad --json > release.json` → `matriz release-2 --proponer --tipo
  planificacion --importar release.json`; cada opción con `ref` = el release (o un JSON por escenario).
- **OKR:** alternativas de KR u objetivos como opciones; `okr.py okr.csv --json` en el expediente; medibilidad y alineación
  con `B-n` como eliminatorios.
- **Cambio:** `impacto.py --proyecto <dir> analizar C-### … --json > impacto.json` → `expediente --tipo cambio --ids
  C-### --importar impacto.json` (quién decide sale del análisis) → matriz con aprobar, rechazar, diferir y plan de
  excepción.
- **Adquisición:** criterios y pesos de `pm-adquisiciones/templates/criterios-seleccion.md` (congelados antes de las
  ofertas) → `matriz proveedor-x --proponer --tipo adquisicion` → la adjudicación la decide la autoridad de la
  organización.
- **Hacer o comprar:** `matriz hacer-comprar-c2 --proponer --tipo adquisicion --criterios hacer-o-comprar --ids
  entregables:C2` → `expediente --hoja hacer-comprar-c2` (contexto del mapa) → puntajes con fuente → `--elegir` (§13.11).

### 13.9 RACI y autoridad: PRINCE2 manda, la RACI lo refleja

**Precedencia.** PRINCE2 7 define la autoridad: quién decide sale de los niveles de decisión (SPEC §1.10.8), de las
tolerancias y de la autoridad de cambio (`motivos_autoridad` de `registro.py`, §13.1); la junta decide y el gestor
recomienda (`prince2-principios-personas-procesos.md` `### 6.10`). La matriz RACI de `pm-interesados` (`raci.csv`, un
solo A por elemento, SPEC §1.10.10) es la vista de responsabilidades por elemento y debe **reflejar** esa autoridad; no
la reemplaza ni agrega reglas propias. `decision.py` usa la RACI solo para tres cosas: mostrar a quién consultar e
informar, pedir una justificación cuando decide otra persona y avisar cuando las dos fuentes no coinciden.

**Elementos afectados.** Los elementos de `raci.csv` (productos y paquetes de la WBS, actividades, requisitos, épicas e
historias, KR y objetivos, decisiones, entregables) que son ids de partida de la decisión (`--ids` o `decision.json.ids`)
o que aparecen en el texto de la pregunta, de las filas de partida o de las filas relacionadas a **1 salto** (las que
citan o son citadas por las de partida). Un elemento solo numérico (`2`, un producto raíz de la WBS) cuenta solo como id
de partida; los demás también por mención, con límites de palabra (`3.1` no es `13.1` ni `3.12`).

**Nivel de autoridad de una persona** (`esquema.nivel_autoridad`, el mismo criterio para `--por`, para el A de la RACI y
para `decidido_por`): (1) los roles de `estado.json` por nombre (sin acentos ni mayúsculas, palabra completa):
`ejecutivo`, `usuario_senior` y `proveedor_senior` → `junta` (la junta es un órgano colectivo; el ejecutivo tiene la
última palabra), `autoridad_cambio` → `autoridad-cambio`, `gestor_proyecto` → `gestor`, `product_owner` →
`product-owner`, `jefes_equipo`, `aseguramiento` y `soporte` → `equipo`; (2) si no, palabras del rol escrito (el prefijo
de `--por "Rol: Nombre"`, o `rol_proyecto` y `rol_organizacion` del maestro): capa de negocio o corporativo →
`capa-negocio`; ejecutivo, junta, usuario o proveedor sénior → `junta`; autoridad de cambio; gestor o jefe de proyecto
→ `gestor`; product owner o dueño de producto; jefe de equipo, equipo, analista, desarrollador → `equipo`. Si coinciden
varios, el más alto; si ninguno, **no determinado**. El orden es el de los niveles: equipo < product-owner < gestor <
autoridad-cambio < ejecutivo < junta < capa-negocio.

**Reglas al `--elegir`** (el nivel requerido es el de `decision.json`):

1. Quien decide (`--por`) es el A de cada elemento afectado (por id del maestro o por nombre completo) → sin cambios.
2. Si no lo es, es **autoridad superior** cuando su nivel alcanza el requerido y supera el del A (en `junta` o más
   arriba basta igualarlo); con el nivel del A sin determinar, basta el requerido. Si no → `--motivo` obligatorio, con
   un mensaje que nombra el elemento, el A, su nivel y el de quien decide. El motivo queda en `notas`.
3. Si el A tiene un nivel determinado **menor** que el requerido (p. ej. A en una jefa de equipo para una decisión del
   ejecutivo) → aviso de **incoherencia RACI ↔ autoridad**: el script no elige cuál vale; se corrige la RACI con
   `pm-interesados` o el nivel de la hoja. La decisión sigue la regla de autoridad de PRINCE2 (§13.5).
4. Después de registrar: recuerda a los **C** (dejar constancia de la consulta) y, si hay **I**, escribe la base
   `<hoja>/aviso-D-###.md` y prepara con `interesados.py plan-envio` (audiencia `raci:<elemento>:I`, sin quien decidió)
   el borrador en `03-control/comunicaciones/<fecha>-decision-d-###-…/`: un mensaje por destinatario según su perfil,
   estado `borrador`. **Nada se envía**: `envios.py aprobar … --por` y `enviar … --confirmar` siguen con confirmación
   humana (hook `guardian.py`). `--sin-aviso` solo muestra el comando.

**Ejemplo** (caso DR de `probar_paquete.py`): épica E-1 con A la usuaria sénior (junta), C una jefa de sucursal
confidencial e I el comité y la ejecutiva. Una hoja de planificación (nivel `gestor`) sobre E-1: la jefa de equipo y el
gestor necesitan `--motivo` (no son el A y su nivel no supera el de ella); la usuaria sénior decide sin motivo. En una
hoja de OKR (nivel `ejecutivo`) sobre KR-1.1, cuyo A es la jefa de equipo, se avisa la incoherencia y la ejecutiva
decide sin motivo (es autoridad superior); la sanidad da DEC-04 hasta que se corrija la RACI.

### 13.10 Vigencia y contradicciones de decisiones (regla 12 con soporte en los datos)

Una decisión no se borra ni se edita para "deshacerla": la decisión nueva **reemplaza** a la anterior y la anterior
queda como historia. La vigencia depende de la **autoridad**, no solo de la fecha: una decisión posterior de nivel
inferior no deja sin efecto la de la junta (PRINCE2: la junta decide y delega; niveles de SPEC §1.10.8).

```bash
python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> actualizar decisiones D-017 --campo reemplaza=D-010
python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> actualizar decisiones D-004 --campo conviven=D-018
python3 ${CLAUDE_SKILL_DIR}/scripts/decision.py --proyecto <dir> vigentes [--tema "…"] [--ids D-010,R-003] [--historia] [--corte AAAA-MM-DD] [--max 25] [--json]
```

- **Columnas** (al final de `decisiones.csv`; un archivo anterior las gana al primer uso): `reemplaza` y `conviven`
  (§10). `registro.py` valida que los D-### existan, que no se reemplace dos veces la misma ni se forme un ciclo, y que la
  reemplazada no sea posterior (esto se omite con `--forzar`); y la **autoridad**, que no se omite: el `nivel` de la
  nueva debe ser igual o superior al de la reemplazada y quien decide (`decidido_por`) debe tener esa autoridad
  (`esquema.nivel_autoridad`). Si no, la decisión va a quien tiene ese nivel (junta: pm-director, `estado.py puerta
  decision-ad-hoc`) y se marca `reemplaza` en la fila que registre.
- **Automático:** al aprobar una versión nueva del mismo artefacto (`estado.py aprobar`, `bmad.py linea-base`), al
  volver a fijar todas las claves de los presupuestos (`estado.py presupuesto`), al cambiar el enfoque de entrega
  (`estado.py set enfoque_entrega=… --por`) o al registrar un veredicto nuevo del gate de preparación de BMAD
  (`puertas.py preparacion-bmad`: `estado.json` guarda uno solo), la fila nueva reemplaza a la anterior si esta no tiene
  nivel mayor ni fecha posterior. Una actualización parcial de presupuestos (solo algunas claves) no reemplaza ni se
  toma como contradicción.
- **`vigentes`** (solo lectura): las decisiones vigentes con su cadena (D-010 → D-017), `conviven`, `revisar_en` (vencida
  si es anterior al corte) y las contradicciones probables; `--tema` busca en español e inglés; `--ids` filtra por la
  decisión, su cadena, un id que cita su texto (`decision`, `contexto`, `artefactos_afectados`) o un elemento de
  `artefactos_afectados` (un id como `KR-1.1`, un paquete como `3.1`, una ruta, o el ID de la hoja
  `03-control/decisiones/<ID>/`); `--historia` agrega las reemplazadas.
- **Asunto:** dos decisiones tratan el mismo asunto si comparten un id de registro citado en `decision` o
  `artefactos_afectados` (R, I, C, S, L, Q, A, PU); si ninguna cita ids, un artefacto (ruta con carpeta, sin los CSV de
  registros); si tampoco, un texto parecido. Citar ids distintos separa asuntos: "acepta el residual de R-005" y "… de
  R-004" no se comparan (el falso positivo que mostró la prueba del informe exxperts).
- **DEC-05 (contradicción probable):** mismo asunto, ambas vigentes, texto parecido (Jaccard ≥ 0,6 de los lemas de
  `texto.py`, al menos 2) y un valor distinto: versión (v1.0 → v1.1), cifra normalizada (39.800 → 45.000), fecha
  (15 de marzo → 30 de abril), negación (no, nunca, jamás, ni, tampoco, not, never; "sin" no cuenta) o una palabra
  cambiada (predictivo → híbrido). Se resuelve marcando `reemplaza` (si la nueva deja sin efecto a la anterior) o
  `conviven` (si deben valer las dos; no se vuelve a avisar). Es un aviso: el script no decide cuál vale.
- **DEC-06 (revisión vencida):** decisión vigente con `revisar_en` (AAAA-MM-DD) anterior al corte, sin una decisión
  posterior del mismo asunto y con algo de lo que cita todavía abierto (si todos los ids citados de registros con estado
  están cerrados o validados, por ejemplo el supuesto que se replanificó ya se validó, no avisa): reevaluarla con quien decidió y confirmarla (nueva `revisar_en`) o registrar la decisión
  nueva con `reemplaza`. Es "lo que hay que decidir hoy" de la revisión periódica.
- **Búsqueda en español e inglés** (`pm-estado-proyecto/scripts/texto.py`, común a `expediente --tema`, `vigentes --tema`
  y al futuro indexador): minúsculas sin tildes; palabras vacías es/en; lematizador ligero (plurales, género y vocal
  final, participios y gerundios, -ción: normativa = normativo = normative, aprobado = aprobación = approved,
  delegaciones = delegación); glosario corto inglés → español de gestión; fechas ISO, dd/mm/aaaa (día primero), "15 de
  marzo de 2027", "March 15, 2027", "enero 2027", trimestres T1/Q1 (una fecha de la fila vale también por su mes, año y
  trimestre, y "enero" solo por el mes); cifras con separadores (39.800 = 39,800 = 39800 = "39,8 mil"); versiones; ids
  (R-3 = R-003). Coinciden todos los términos de una consulta de hasta dos y el 60 % (al menos dos) desde tres. Límites:
  no une cambios de raíz (aprueba/aprobado) ni sinónimos fuera del glosario.

### 13.11 Mapas estratégicos: contexto de la decisión, hacer o comprar y cita en el componente

Los mapas de `pm-mapas-estrategicos` (`02-planificacion/mapas/*.json`, esquemas `pm-mapa-wardley/1` y `pm-recorrido/1`)
son evidencia para una decisión, no un criterio: la evolución de un componente lo describe a él, no distingue entre las
opciones de ese mismo componente (construirlo, comprarlo o tercerizarlo están todas en la misma etapa).

- **Nombrar un elemento:** en `--ids` (o en `decision.json.ids`), `<mapa>:<id>`, donde `<mapa>` es el slug
  (`entregables:C2`), el archivo sin extensión (`wardley-entregables:C2`) o con ella; vale para un componente de Wardley
  o un paso de un recorrido. Un elemento que no existe, un ancla o un mapa que no está se informan en (9) como dato
  faltante; no son "otros ids".
- **Expediente, sección 10** (solo si hay; `mapas.py`, función `contexto`, solo lectura): cada componente y cada paso que
  la decisión nombra o que cita en `refs` un id de partida (los de `--ids` y los de la pregunta), con su cita
  `archivo#id` y los campos tal como están en el mapa. De Wardley: etapa, evolución y visibilidad, decisión del mapa
  (`construir`, `comprar`, `tercerizar`, `mercado`), inercia, evidencia, lo que depende de él (los elementos con un
  enlace hacia él) y el movimiento previsto. Del recorrido: acción y etapa, emoción con su fuente, dolor y tipo de
  causa, oportunidad con su clase Kano, KPI del recorrido y persona (con `persona_id` si es una `PU-###`). `--json`
  trae `mapas` y `mapas_total`; `pregunta --validar` acepta como evidencia el elemento (`entregables:C2`) o su archivo.
- **Criterios de hacer o comprar** (`--criterios hacer-o-comprar`, tipo `adquisicion`): **diferenciación** que conserva la
  opción (1–5, mayor; 15), **costo total** de propiedad en el horizonte del caso (num, menor; 25), **tiempo hasta
  disponible** en semanas (num, menor; 20), **dependencia del proveedor** (1–5, menor; 15), **capacidad interna** para
  construir y mantener o administrar el producto o el contrato (1–5, mayor; 10) y **riesgo de construir algo que va a
  volverse commodity** (1–5, menor; 15). Los pesos son los de la plantilla hasta que los confirma quien decide
  (`fuente_peso`). La etapa y el movimiento del componente son la fuente del puntaje de riesgo commodity y de la
  diferenciación; el costo total puede salir de `inversion.py --json` si hay flujos por año. Para elegir proveedor (ya
  decidido comprar), los criterios del tipo sin conjunto. El aviso "ninguna opción parece no hacer nada" es esperable
  cuando la opción 0 ya se comparó en el caso de negocio: se explica en la solicitud.
- **Cita en el componente (cierre de MAP-01):** `matriz <ID> --elegir …`, después de registrar la decisión, llama a
  `mapas.py --proyecto <dir> vincular <mapa> <id> --refs D-###` por cada elemento nombrado en los ids de la hoja (no por
  los que solo citan un id): un componente en producto o commodity marcado `construir` deja de dar MAP-01 y un dolor
  queda tratado por la decisión (MAP-03). Imprime "Mapa · wardley-….json C2: refs = …" y, en un componente, su
  `decision` en el mapa. `mapas.py` no tiene una opción para cambiar esa columna y el script no la toca: si la opción
  elegida cambia el hacer o comprar, la persona la corrige en el JSON y regenera la vista (`mapas.py … wardley render`).
  Si `vincular` falla, la decisión queda registrada igual y el aviso muestra el comando para citarla a mano.

### 13.12 Opciones de tratamiento de un dolor del recorrido

Un dolor del recorrido no tiene matriz propia: lo que entra en un release lo deciden MoSCoW y `release.py capacidad`
(`pm-agil-hibrido`), con el contexto de la sección 10 del expediente. Cuando un dolor admite tratamientos distintos (un
requisito nuevo, un cambio de proceso, un supuesto que se valida antes, un riesgo que se acepta), se comparan en una
hoja del tipo que corresponda (`planificacion` si compite por capacidad; `cambio` si toca una línea base) con el paso
nombrado en los ids (`paciente:P5`), y se puntúa así:

- **Valor** según el paso y no según la preferencia: emoción actual frente a `emocion_objetivo`, clase Kano (un
  `obligatorio` sin tratar pesa más que un `atractivo`) y el KPI del recorrido que mueve, citando `archivo#id`.
- **Alcance del dolor:** cuántas personas (`personas.csv`) o pasos comparten la causa (`tipo_causa`); una causa
  `dependencia-externa` suele pedir un riesgo antes que un requisito.
- **Costo, capacidad y riesgo** con la fuente habitual (estimación, `release.py` importado, `riesgos.csv`).
- La emoción es un dato del mapa con su fuente: si es un supuesto declarado, la opción de validarlo primero entra como
  alternativa, no como un puntaje inventado. Al elegir, la decisión queda citada en el paso y cuenta como tratamiento.

