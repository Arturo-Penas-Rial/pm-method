# Formatos de exportación · Export formats

Referencia propia de `pm-exportar`. Describe cómo se traduce cada artefacto del método a Office y qué esquema sigue el deck de puerta de etapa. Los nombres de productos van en español con su equivalente EN entre paréntesis la primera vez.

## 1. Markdown → .docx

### 1.1 Qué hace `exportar.py docx`
Script `<pm-estado-proyecto>/scripts/exportar.py` (python-docx). Si el frontmatter no dice `estado: aprobado`, la primera línea del documento es una banda en negrita "BORRADOR / DRAFT — estado: <estado> · generado con asistencia de IA, requiere revisión humana". Luego procesa el archivo línea a línea:

| Elemento Markdown | Resultado en Word | Notas |
|---|---|---|
| Frontmatter YAML (`---` ... `---`) al inicio | Se elimina | Los metadatos (versión, estado, aprobador) se reinsertan a mano en la portada si hace falta (ver 1.3) |
| `#` … `######` | Títulos nivel 1–4 (los niveles 5–6 se aplanan a 4) | El título 1 debe ser el nombre del artefacto |
| Párrafo | Párrafo normal | `**negrita**` se conserva; cursiva, enlaces y código en línea no se interpretan (quedan como texto) |
| `- ` / `* ` | Lista con viñetas | Las casillas `- [ ]` se mantienen como texto `[ ]` dentro de la viñeta |
| `1. ` | Lista numerada | La numeración se reinicia por bloque |
| Tabla `| a | b |` | Tabla con estilo "Table Grid" | La fila separadora `|---|` se descarta; celdas con `**` conservan los asteriscos (limitación conocida) |
| Línea en blanco | Se ignora | No genera párrafos vacíos |
| Bloque ```` ```mermaid ```` | Imagen PNG (ancho 6,3") si `mmdc` (mermaid-cli) está instalado; si no, aviso en cursiva + código fuente en Courier | Instalar con `npm i -g @mermaid-js/mermaid-cli`; alternativa: imagen desde `pm-visuales` con la skill oficial `docx` |
| Otros bloques ```` ``` ```` (código) | Texto en Courier 8 pt | — |
| Imágenes `![]()` | No se insertan | Usar la skill oficial `docx` |

### 1.2 Cuándo usar la skill oficial `docx` en lugar del script
Portada y plantilla corporativa (`.dotx`), índice automático, encabezados y pies con versión, marca de agua "BORRADOR" en todas las páginas (el script solo pone la banda inicial), imágenes `![]()`, control de cambios o comentarios, estilos de tabla específicos. En esos casos el agente entrega a la skill el Markdown ya limpio (sin frontmatter) y el bloque de metadatos de 1.3.

### 1.3 Bloque de metadatos que se añade a la portada
Primera página del `.docx`, en una tabla de dos columnas:

| Campo / Field | Valor |
|---|---|
| Proyecto / Project | `estado.json.proyecto` |
| Tipo de documento / Document type | `tipo` del frontmatter y su nombre EN |
| Versión / Version | `version` |
| Fecha / Date | `fecha` |
| Estado / Status | `estado` (si no es `aprobado`, la portada lleva la banda "BORRADOR / DRAFT") |
| Aprobado por / Approved by | `aprobado_por` o "pendiente" |
| Autor / Author | `autor` |
| Generado con asistencia de IA / AI-assisted | sí; nivel de intervención |

### 1.4 Orden de secciones por tipo (se respeta el de la plantilla fuente)
- PID (project initiation documentation): definición del proyecto · enfoque · business case · estructura y roles · enfoques de gestión · plan de proyecto · controles · adaptación del método.
- Plan de etapa (stage plan): descripción · productos (PBS, descripciones) · cronograma · recursos y costos · tolerancias · controles · riesgos de la etapa.
- Informe de fin de etapa (end stage report): resumen · desempeño contra tolerancias · estado de productos y concesiones · riesgos e issues · lecciones · business case actualizado · recomendación.
- Informe de fin de proyecto (end project report): logro contra PID original · desempeño · productos aceptados · beneficios obtenidos y previstos · lecciones · recomendaciones de seguimiento.
- Solicitud de decisión de puerta (`solicitud-<puerta>`): según `pm-direccion-decisiones/templates/solicitud-puerta.md`.

## 2. CSV → .xlsx

### 2.1 Qué hace `exportar.py xlsx`
- `--proyecto <dir> [--salida exportados/AAAA-MM-DD-registros-v<n>.xlsx]`: toma todos los `03-control/registros/*.csv` (incluido `acciones.csv` y **también `stakeholders.csv`**) y crea un libro con una hoja por registro (nombre de hoja = nombre del archivo, máximo 31 caracteres). Sin `--salida` escribe `exportados/registros.xlsx`: pasar siempre `--salida` con la convención de nombres.
- `--entrada <csv> --salida <xlsx>`: un solo registro.
- Cabecera en negrita con fondo, ancho de columna fijo (18), primera fila inmovilizada. Sin fórmulas ni formato condicional.

### 2.2 Mapeo de registros → hojas
Columnas exactamente como `<pm-estado-proyecto>/scripts/esquema.py` (fuente única; detalle y valores en `pm-registros/templates/guia-registros.md`).

| Registro CSV | Hoja | Columnas (cabecera snake_case del paquete) | Traducción EN de las columnas clave |
|---|---|---|---|
| `riesgos.csv` | riesgos | id, fecha_identificacion, autor, categoria, causa, evento, efecto, tipo, probabilidad, impacto, puntuacion, impacto_monetario, valor_esperado, proximidad, disparador, respuesta, acciones, propietario, ejecutor, probabilidad_residual, impacto_residual, estado, fecha_revision, notas | risk id, cause, event, effect, type, probability, impact, score (= P×I; alto ≥15, medio 6–12, bajo ≤5), monetary impact, expected monetary value (EMV), proximity, trigger, response, owner, actionee, residual probability/impact, status |
| `issues.csv` | issues | id, fecha, autor, tipo, titulo, descripcion, prioridad, severidad, impacto, decision, decidido_por, responsable, estado, fecha_cierre, notas | issue id, type (solo `solicitud-cambio`, `fuera-especificacion`, `problema-preocupacion`, `evento-externo`, `oportunidad-negocio`), priority, severity, decision, decided by, owner, status |
| `cambios.csv` | cambios | id, fecha, solicitante, titulo, descripcion, justificacion, impacto_alcance, impacto_tiempo, impacto_costo, impacto_calidad, impacto_riesgo, impacto_beneficios, recomendacion, decision, decidido_por, fecha_decision, estado, notas | change id, requester, impacts (scope, time, cost, quality, risk, benefits), recommendation, decision, decided by |
| `decisiones.csv` | decisiones | id, fecha, decision, contexto, opciones_consideradas, decidido_por, nivel, artefactos_afectados, revisar_en, notas | decision id, context, options considered, decided by, level (`equipo`, `product-owner`, `gestor`, `autoridad-cambio`, `junta`, `capa-negocio`), affected artifacts, review on |
| `supuestos.csv` | supuestos | id, fecha, autor, supuesto_o_restriccion, tipo, categoria, validado, fecha_validacion, responsable, estado, notas | assumption or constraint, type, validated, owner |
| `lecciones.csv` | lecciones | id, fecha, etapa, categoria, situacion, efecto, recomendacion, prioridad, responsable_seguimiento, estado, notas | lesson id, stage, situation, effect, recommendation, follow-up owner, status (`registrada` inicial) |
| `stakeholders.csv` | stakeholders | id, nombre, rol_organizacion, rol_proyecto, poder, interes, actitud, nivel_compromiso_actual, nivel_compromiso_deseado, expectativas, canal, frecuencia, responsable_relacion, confidencial, notas | name, org role, project role, power, interest, attitude, current/desired engagement, channel, frequency, relationship owner, confidential — **hoja de circulación restringida**; filas `confidencial=si` nunca a terceros |
| `calidad.csv` | calidad | id, producto, metodo_verificacion, criterios, responsable_productor, revisores, aprobador, fecha_prevista, fecha_real, resultado, estado, notas | product, verification method, criteria, producer, reviewers, approver, planned/actual date, result |
| `acciones.csv` | acciones | id, fecha, origen, descripcion, responsable, fecha_compromiso, prioridad, estado, fecha_cierre, notas | action id, source, description, owner, due date, priority, status, closed on |

### 2.3 Cuándo usar la skill oficial `xlsx`
- Semáforos por formato condicional (p. ej. `puntuacion` ≥ umbral en rojo; el umbral se declara en una hoja "Notas").
- Fórmulas vivas: `puntuacion = probabilidad * impacto`, `valor_esperado = impacto_monetario * {1:10 %, 2:30 %, 3:50 %, 4:70 %, 5:90 %}[probabilidad]`; hoja EVM con SV, CV, SPI, CPI, EAC a partir de `03-control/reportes/progreso.csv` (las mismas fórmulas que `evm.py`; BAC sin reserva de gestión).
- Filtros automáticos, validación de datos en columnas enum (`estado`, `tipo`, `nivel`), gráficos (riesgos por categoría, issues por estado).
- Hoja "Resumen" con conteos por registro y estado (equivalente a `registro.py resumen`).
- Hoja "Notas" obligatoria cuando hay fórmulas: qué se calcula, con qué insumos, umbrales configurables y fecha de corte.

### 2.4 Reglas
- No renombrar ni reordenar columnas respecto al esquema; las traducciones van en una fila de comentario o en la hoja "Notas", no en la cabecera.
- La hoja `stakeholders` se omite del libro cuando la audiencia es externa o se exporta en un archivo aparte de circulación restringida.
- El nombre del libro lleva `-BORRADOR` si cualquier registro tiene filas sin `id`, `estado` o responsable (detectado por `registro.py` o por revisión).

## 3. Deck de puerta de etapa (.pptx) · Stage-gate deck

Esquema que el agente entrega a la skill oficial `pptx` (o como guion Markdown si no está instalada). Una idea por diapositiva; cifras con fuente; marca "BORRADOR" en todas las diapositivas si la fuente no está aprobada. Diez a doce diapositivas como máximo.

| # | Diapositiva / Slide | Contenido / Content | Fuente / Source |
|---|---|---|---|
| 1 | Título / Title | Proyecto, puerta (autorizar-etapa N / plan de excepción / cierre), fecha, quién presenta, estado del deck (borrador o aprobado) | `estado.json` |
| 2 | Decisión que se pide / Decision requested | Una frase; quién decide; fecha límite; qué pasa si no se decide | solicitud de decisión (`solicitud-<puerta>`), cabecera |
| 3 | Justificación continua / Business justification | Deseable · viable · alcanzable con evidencia; cambios del business case desde la última puerta (beneficios, costo, plazo, riesgo) | business case, solicitud §1 |
| 4 | Estado contra tolerancias / Status against tolerances | Siete objetivos con semáforo, pronóstico vs. tolerancia de etapa y de proyecto; criterio del semáforo (verde ≤50 % de la tolerancia, ámbar 50–100 %, rojo fuera) | highlight / end stage report, solicitud §3 |
| 5 | Productos / Products | Productos de la etapa: aprobados, con concesión, pendientes; productos requeridos para la puerta y su estado | registro de productos, `estado.json.artefactos`, solicitud §2 |
| 6 | Hitos / Milestones | Base vs. actual, variación, próximos hitos de la etapa que se propone | plan de etapa, Gantt |
| 7 | Riesgos e issues / Risks and issues | Los que necesitan atención de la junta, con propietario y respuesta; exposición agregada vs. tolerancia de riesgo | `riesgos.csv`, `issues.csv`, solicitud §4 |
| 8 | Plan propuesto / Proposed plan | Etapa siguiente o plan de excepción: productos, fechas, costo, tolerancias propuestas, recursos que se piden | plan de etapa / plan de excepción |
| 9 | Opciones y consecuencias / Options and consequences | Tabla de opciones (aprobar, condicionar, rechazar, más información, cierre prematuro) con consecuencias cuantificadas | solicitud §5 |
| 10 | Recomendación / Recommendation | Opción recomendada, grado de confianza, condiciones, supuestos | solicitud §6 |
| 11 | Decisiones requeridas / Decisions needed | Lista numerada: decisión, rol que decide, fecha límite; bloque "pendiente de aprobación humana" | solicitud §7 |
| 12 | Anexos / Annexes | Enlaces a PID, planes, registros, informe de excepción; lecciones del período | carpeta del proyecto |

Variantes:
- **autorizar-inicio**: diapositivas 1–3, 5 (brief, descripción del producto del proyecto, business case esquemático, roles, plan de la etapa 1 = iniciación), 7, 9–11.
- **autorizar-cierre**: sustituir 6 y 8 por "Logro contra la PID original" y "Beneficios obtenidos y previstos; transferencia al negocio; recomendaciones de seguimiento"; añadir "Lecciones" antes de los anexos.

Notas del orador: cada diapositiva lleva en notas la fuente exacta (ruta, versión, id de registro) y los supuestos adoptados.

## 4. Paquetes ZIP · ZIP packages

`python3 <pm-exportar>/scripts/paquete.py --proyecto <dir> puerta <tipo> | cierre | listar puerta <tipo> | listar cierre`. Busca cada producto primero por su clave canónica en `estado.json.artefactos` (SPEC §1.10.3; si hay varias numeradas, la más alta) y, si no está registrada, por patrones de ruta. `{n}` = `etapa_actual.numero`, `{n+1}` = la siguiente (en iniciación, n = 1 → `plan-etapa-2`).

**Solicitud vs. ZIP.** El documento de solicitud de decisión que redacta `pm-direccion-decisiones` es `00-direccion/decisiones/AAAA-MM-DD-solicitud-<puerta>.md` (clave `solicitud-<puerta>`; el script también reconoce nombres antiguos `*paquete-<puerta>*.md`). El ZIP que arma este script es otra cosa: si se registra, va como `exportado-paquete-<puerta>` y el script nunca lo reincluye en otro paquete.

### 4.1 Contenido del paquete de puerta (`paquete.py puerta <tipo>`)
| Tipo de puerta | Obligatorios (clave) | Opcionales (clave) |
|---|---|---|
| autorizar-inicio | `project-brief`, `estructura-organizativa`, `plan-etapa-1`, `descripcion-producto-proyecto` | `business-case` (esquemático; suele vivir en el brief), `solicitud-autorizar-inicio`, `canvas-arranque`, `mandato` |
| autorizar-proyecto | `pid`, `business-case`, `plan-proyecto`, `plan-etapa-{n+1}` | `enfoques` (`02-planificacion/enfoques/*.md`), `solicitud-autorizar-proyecto`, registros |
| autorizar-etapa | `informe-fin-etapa-{n}`, `plan-etapa-{n+1}`, `business-case`, `plan-proyecto` | `solicitud-autorizar-etapa`, registros (xlsx de `exportados/` o CSV), `tablero-avance` |
| autorizar-plan-excepcion | `informe-excepcion` (X-###), `plan-excepcion` (X-###), `business-case` | `plan-proyecto`, `evaluacion-excepcion`, `solicitud-autorizar-plan-excepcion`, registros |

### 4.2 Contenido del paquete de cierre (`paquete.py cierre`)
Obligatorios: `informe-fin-proyecto`, `registro-aceptacion`, `informe-lecciones`, `recomendaciones-seguimiento`, `plan-revision-beneficios` (si falta, toma `00-direccion/enfoque-beneficios.md`), `business-case-original` (`00-direccion/historial/business-case-v1.0.md`), `business-case` (final), registros. Opcionales: `pid-original` (`00-direccion/historial/pid-v1.0.md`), `solicitud-autorizar-cierre`, `handover`, cierres de contrato (`04-cierre/cierre-contrato-*.md`), `notificacion-cierre`, actas de la junta.

### 4.3 Regla BORRADOR y estados aceptados
- El ZIP lleva `-BORRADOR` **solo** si falta un obligatorio o si un obligatorio no está en un estado aceptable. Estados aceptables: `aprobado`, `en-revision` (lo que la puerta va a decidir llega en revisión) y, para CSV/XLSX, `registro`. Un opcional en borrador no marca el paquete; figura con su estado en el manifiesto.
- La solicitud de decisión es opcional para el script, pero el método la exige (sin ella la junta no sabe qué se le pide): si `listar` la muestra como "no incluido", pedirla a `pm-director` antes de enviar.

### 4.4 Manifiesto (`MANIFIESTO.md` dentro del ZIP)
Tabla con: archivo en el ZIP · ruta de origen · tipo · versión · estado · obligatorio/opcional · aprobado por. Cabecera con proyecto, paquete, fecha de generación, "generado con asistencia de IA" y la línea "ESTADO DEL PAQUETE: BORRADOR (faltan…; en borrador…) | COMPLETO PARA LA PUERTA". Pie: el paquete no constituye aprobación; la decisión la registra pm-director con `estado.py puerta`.

### 4.5 Convención de nombres
`exportados/AAAA-MM-DD-<tipo>-v<version>[-BORRADOR].<ext>`; `<tipo>` en kebab-case español (`plan-etapa-2`, `registros`, `paquete-autorizar-etapa`, `deck-autorizar-cierre`); versión de la fuente (o del paquete: número correlativo por puerta). Nombre por defecto del ZIP: `AAAA-MM-DD-paquete-<tipo>-v1[-BORRADOR].zip`. Los aprobados no se sobrescriben.
