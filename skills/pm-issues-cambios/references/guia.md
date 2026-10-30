# Guía de issues y control de cambios · Issues and change control guide

Términos EN la primera vez: request for change (RFC), off-specification, concession, change authority, change budget, baseline, exception report, exception plan.

## 1. Los cinco tipos de issue
| Tipo (valor en CSV) | Qué es | Tratamiento por defecto | Artefactos |
|---|---|---|---|
| `problema-preocupacion` | Impacto negativo inmediato (problema) o algo a evaluar (preocupación) | Resolver dentro de tolerancias si se puede; si no, escalar; muchos van al diario | `issues.csv`; informe de issue si requiere análisis |
| `evento-externo` | Hecho fuera del control del proyecto que podría afectarlo | Analizar impacto; puede derivar en cambio o excepción | `issues.csv`; posible `cambios.csv` o informe de excepción |
| `oportunidad-negocio` | Consecuencia positiva no prevista | Evaluar y pedir opinión a la junta (suele exceder al proyecto) | `issues.csv`; `decisiones.csv` nivel `junta` |
| `solicitud-cambio` | Propuesta de modificar la línea base | Siempre control de cambios: productos, justificación, financiación | `issues.csv` + `cambios.csv` + `solicitud-cambio.md` |
| `fuera-especificacion` | Producto que no cumple o no podrá cumplir su especificación | Siempre control de cambios: concesión o corrección | `issues.csv` (+ `cambios.csv` si concesión) + informe de issue; `calidad.csv` |

## 2. Captura
- Prueba de certeza: incierto → `pm-riesgos`.
- Formal/informal: tres preguntas (¿impacto material?, ¿modifica línea base?, ¿decide otro?). Solicitud de cambio y fuera de especificación siempre formales.
- Prioridad `urgente|alta|media|baja`; severidad `critica|mayor|menor|informativa`, con las escalas del enfoque de issues.
- `registro.py --proyecto <dir> agregar issues --campo tipo=... --campo titulo=... --campo prioridad=... --campo severidad=... --campo responsable=...` (rechaza tipos fuera de los cinco). Informales: diario.
- Una tarea o compromiso no es un issue ("enviar la minuta", "pedir cotización" → `acciones.csv`, A-###).
- Qué preguntar si falta: quién lo plantea y cuándo; qué producto o línea base afecta; fecha límite para decidir; de dónde saldría el dinero.

## 3. Evaluación de impacto y opciones
- Efecto sobre los siete objetivos (aunque sea "sin impacto"), tolerancias de etapa y proyecto, business case, perfil de riesgo y otros productos o paquetes.
- Técnicas: cinco porqués o causa-efecto; análisis de red para la ruta crítica (nunca inferir "sin impacto en fecha" sin análisis); multicriterio para elegir opción.
- Variación relativa: costo del cambio ÷ BAC vigente; días adicionales ÷ duración planificada. Umbrales del plan o, si no hay, 5 % (atención) y 10 % (escalamiento) declarados.
- Comparar siempre el pronóstico con la tolerancia.
- Al menos dos opciones, incluida "rechazar y no hacer nada"; para cada una, ventaja frente a impacto de implementación; consecuencias de aprobar y de rechazar.
- Solicitud de cambio: fuente de financiación (presupuesto de cambio, reducción de alcance en otra parte, fondos adicionales). Fuera de especificación: concesión (aceptar y actualizar línea base; descripción de producto actualizada obligatoria) o corrección (presupuesto de cambio, plan de excepción o remedio contractual).
- Causa raíz, no síntoma: "retraso" o "falta de tiempo" no son causas.
- Es legítimo pedir consejo a la junta antes de completar la evaluación.

### 3.1 Análisis de impacto con impacto.py
`python3 ${CLAUDE_SKILL_DIR}/../pm-issues-cambios/scripts/impacto.py --proyecto <dir> analizar C-### [escenario]` arma la
tabla de impacto antes de pedir la decisión y el borrador de la solicitud de cambio
(`03-control/reportes/<fecha>-solicitud-cambio-C-###.md`, `borrador`, secciones de `templates/solicitud-cambio.md`). No
escribe registros: los comandos para dejar el análisis en `cambios.csv` se muestran para después de la decisión.

El escenario lo prepara la persona o el modelo (el script no inventa cifras) y cada parte es opcional:

| Entrada | Qué calcula | Contra qué |
|---|---|---|
| `--actividades <csv con el cambio>` (`--actividades-base`, por defecto `02-planificacion/actividades.csv`; `--inicio`) | duración y fin con `cpm.py`, camino crítico antes y después, actividades nuevas y las que se corren (dependencias) | tolerancia de tiempo del proyecto ("±N semanas" = 5·N días laborables; "±N %" de la duración base; `--tol-dias` la fija) |
| `--pert <estimacion-pert.csv> [--confianza k]` | reserva de cronograma a kσ (por defecto 2σ) del camino crítico base con la distribución del archivo que escribe `cpm.py --estimacion` (beta-PERT si falta: σ = (P − O)/6) y lo que queda | menos de la mitad → riesgo sugerido para `pm-riesgos` |
| `--puntos N --release R [--liberar ids] [--etapa]` | capacidad del release en `backlog.csv` con `agil.velocidad_referencia` (misma función que `pm-agil-hibrido/scripts/release.py capacidad`); sprints extra × `cadencia_iteracion_dias` | con `--etapa`, tolerancia de tiempo de la etapa ("±N %" de su duración en días corridos) |
| `--evm <evm-AAAA-MM-DD.json>` | alcance que no entra (modo ágil) o excepción prevista | Must sin tolerancia |
| costo y cargo de `cambios.csv` (o `--costo`, `--cargo`) | BAC de `wbs.csv` (paquetes) y variación relativa; consumo del presupuesto de cambio con la regla de CAM-03 | tolerancia de costo; saldo y límite de la autoridad de cambio con `registro.py` (`motivos_autoridad`, §4.1) |
| `--flujos <csv> --opcion "Con C-###" [--base] --tasa` | VAN de la base y con el cambio (`inversion.py`), VAN incremental y cuánto puede caer el beneficio principal | VAN > 0 y tolerancia de beneficios ("−N %" o `--variacion`) |
| `--refs FR-13,E-2 --paquetes 3.4` | estado en la especificación (fachada; un id nuevo pide traspaso y nueva línea base), riesgos abiertos y actividades de calidad que los citan | tolerancias de riesgo y calidad |

Quién decide (tabla §4): fuera de la tolerancia de tiempo del proyecto → capa de negocio vía la junta; fuera de la de la
etapa, Must en peligro (EVM), costo sin fuente o business case que deja de justificarse → junta con informe de excepción
(§6); costo sobre el límite delegado o sin saldo → junta (la autoridad de cambio no puede aprobarlo: `registro.py` lo
rechazaría con los mismos motivos); si no, la autoridad de cambio de `estado.json.roles`. Opciones del borrador: aprobar
(con la fuente), rechazar, diferir (con fecha) y pedir plan de excepción, cada una marcada si aplica; la recomendación es un
borrador que firma el gestor. Respaldo: PRINCE2 7 issues, pasos Evaluar, Recomendar y Decidir, autoridad y presupuesto de
cambio (`pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §3.c.1–§3.c.3) y gestión por
excepción (§4.c.2); PMBOK 8 "Evaluar e implementar cambios" (`pmbok8-dominios-procesos-adaptacion.md` §2.1.b.8: aprobar,
rechazar, diferir o pedir más información; impacto sobre alcance, cronograma, finanzas y riesgo).

## 4. Tabla de autoridad (referencia configurable en el enfoque de issues)
| Situación | Decide | Registro |
|---|---|---|
| Acción correctiva dentro de tolerancias de paquete | Gestor de equipo | checkpoint; `acciones.csv`; `issues.csv` si es formal |
| Intercambio de ítems de igual tamaño dentro de la tolerancia de alcance (cambio ligero) | Product owner | `decisiones.csv` nivel `product-owner`; backlog |
| Acción correctiva dentro de tolerancias de etapa, sin tocar línea base | Gestor del proyecto | `issues.csv` + `decisiones.csv` nivel `gestor`; highlight |
| Cambio dentro del umbral y presupuesto de cambio delegados | Autoridad de cambio | `cambios.csv` + `decisiones.csv` nivel `autoridad-cambio` |
| Cambio fuera del umbral o sin presupuesto, o concesión relevante | Junta (con la fuente: reserva de gestión, plan de excepción o presupuesto ampliado) | `cambios.csv` en `pendiente-decision` hasta la decisión; `pm-director`: puerta `decision-ad-hoc` (nivel `junta`) |
| Pronóstico fuera de tolerancia de etapa | Junta (informe de excepción) | `pm-director`: `decision-ad-hoc`; luego `autorizar-plan-excepcion` |
| Pronóstico fuera de tolerancia de proyecto | Capa de negocio vía la junta | `pm-director`, nivel `capa-negocio` |

Autoridad delegada sin presupuesto de cambio es inútil: verificar ambos. La mayoría de los cambios nace en paquetes y debe poder decidirse cerca de ellos.

### 4.1 Presupuesto de cambio, costo y cargo (control permanente)
- La junta fija los montos y pm-director los registra en `estado.json` → `presupuestos`: `estado.py presupuesto cambio=15000 riesgo=20000 gestion=10000 limite_autoridad_cambio=5000 --por "Ejecutiva: …" [--fecha …]` (números sin moneda ni separador de miles; con `--por` queda en `decisiones.csv`). Este skill no ejecuta ese comando: lo pide.
- Cada cambio declara cuánto consume y contra qué: `registro.py agregar|actualizar cambios … --campo costo=9000 --campo cargo=presupuesto-cambio|reserva-riesgo|reserva-gestion|plan-excepcion|sin-costo`. `costo` es numérico (`USD 9.000` se rechaza); el texto de `impacto_costo` sigue siendo la explicación.
- Lo que en la práctica se revisa a mano y tarde (cuánto queda del presupuesto, quién aprobó qué) lo vigila la sanidad sobre los cambios aprobados, implementados o cerrados: CAM-01 impacto de costo sin `costo`/`cargo`; CAM-02 cargo a la reserva de riesgo sin citar el R-### que responde (la reserva de riesgo solo financia respuestas a riesgos); CAM-03 consumo contra el presupuesto (INFO < 80 %, AVISO ≥ 80 %, ERROR > 100 % que bloquea puertas); CAM-04 costo sobre el límite de la autoridad de cambio sin decisión de la junta o el ejecutivo (se reconoce en `decidido_por`); CAM-05 reserva de gestión sin la junta.
- Antes de pedir la decisión, comparar el costo con el remanente (presupuesto − consumo) y con `limite_autoridad_cambio`: si no entra, sube a la junta (fila "fuera del umbral" de la tabla).
- **Control al registrar (`registro.py`, no se omite con `--forzar`).** Cuando la escritura deja un cambio aprobado (`decision=aprobado` o `estado` aprobado, implementado o cerrado) con `costo` > 0, o cambia `costo`, `cargo` o `decidido_por` de uno aprobado:
  - `decidido_por` que no es la junta ni el ejecutivo (se reconoce como en CAM-04/CAM-05: "ejecutiv", "junta", "board", "executive" o el nombre del ejecutivo de `estado.json.roles`) → **rechazo** si `costo` > `limite_autoridad_cambio`, si `cargo=presupuesto-cambio` y lo ya cargado + `costo` > `presupuestos.cambio`, o si `cargo` es `reserva-gestion` o `plan-excepcion` (fuentes que solo libera la junta). Qué hacer: dejar `estado=pendiente-decision` (sin `decision=aprobado`), anotar en `notas` lo que decidió quien no tenía autoridad, issue en `escalado` y escalar a `pm-director`.
  - La junta o el ejecutivo pueden aprobar sobre el límite por cambio (el límite es de la autoridad delegada), pero con `cargo=presupuesto-cambio` sin saldo se **rechaza** hasta que indiquen la fuente: `cargo=reserva-gestion`, `cargo=plan-excepcion` o `presupuesto-cambio` habiendo ampliado antes el presupuesto (`estado.py presupuesto cambio=<monto> --por "<rol: nombre>"`, que deja la decisión en `decisiones.csv`; lo ejecuta `pm-director`).
  - Sin `presupuestos.cambio` fijado se registra como siempre, con un aviso (CAM-03 lo recuerda). Actualizar otros campos de un cambio ya aprobado (estado `implementado`, `notas`) no vuelve a controlarlo.
- Un CAM-03 ERROR o un CAM-04 que aparezca igual (cambios aprobados antes de que la junta fijara el presupuesto o el límite, o un presupuesto reducido después) se escala como excepción (§6): la junta amplía el presupuesto o indica otra fuente y vuelve a registrar el cambio con `decidido_por` de la junta o el ejecutivo.

## 5. Registro de decisiones y sincronización
- Issues: `registro.py actualizar issues I-### --campo decision="..." --campo decidido_por="<rol: nombre>" --campo estado=en-accion|resuelto`.
- Cambios: `--campo decision=aprobado|rechazado|diferido|pedir-plan-excepcion|pedir-mas-informacion --campo decidido_por=... --campo fecha_decision=...` (diferido exige fecha o evento de reevaluación en `notas`). `decision` y `estado` deben ser coherentes (p. ej. `decision=diferido` con `estado=diferido`, nunca con `aprobado` o `implementado`): una combinación contradictoria se rechaza también con `--forzar` (tabla en la guía de registros §3; las heredadas, CAM-06). Un cambio rechazado o diferido no consume presupuesto.
- Fila en `decisiones.csv` con `nivel` (`equipo`, `product-owner`, `gestor`, `autoridad-cambio`) y `artefactos_afectados`. Junta o capa de negocio: la fila y la puerta las registra `pm-director` (`estado.py puerta`); aquí solo se copia el `D-###`.
- Concesión: `issues.csv.decision=concesion: ...`. Acciones de seguimiento → `acciones.csv` con `origen=I-###` o `C-###`.
- Cambio aprobado, en la misma operación: registro de cambios; nueva versión del artefacto (`estado.py artefacto <clave> --version x.y --estado en-revision` y, tras el acto humano, `estado.py aprobar <clave> --por "<rol: nombre>" --nivel autoridad-cambio|gestor`; si aprobó la junta, `aprobar` lo hace `pm-director`); descripción de producto; plan de etapa; consulta de riesgos nuevos (`pm-riesgos`). Conservar la versión anterior. Cerrar el issue con `fecha_cierre`.
- Líneas base al nivel de componente liberable; identificador único por producto y versión; ningún cambio sin aprobación ni pista de auditoría; en cada límite de etapa, verificar que el estado real coincide con el registrado.

## 6. Excepción y después de la decisión
- Dos pasos: aviso temprano inmediato a la junta + `templates/informe-excepcion.md` → `03-control/reportes/<fecha>-informe-excepcion-X-###.md` (causa, consecuencias, opciones cuantificadas por objetivo —al menos una sin plan de excepción si es viable—, recomendación, lecciones). `X-###` correlativo; `estado.py artefacto informe-excepcion-X-### --ruta ... --estado en-revision`; `issues.csv.estado=escalado`. No se registra puerta (ni `pendiente`).
- Plantilla única del paquete: `pm-progreso-reportes` la usa cuando `evm.py` marca `excepcion_prevista`.
- No fragmentar un cambio en partes pequeñas para evitar el escalado.
- Si la junta pide un plan de excepción con `decision-ad-hoc` y `--condiciones`, la condición queda abierta (sanidad EST-12) hasta que pm-director registra `estado.py cumplir-condiciones decision-ad-hoc --fecha … --por … --nota …`.
- Tras `decision-ad-hoc` (registrada por `pm-director`): reasignar tolerancias → `estado.py tolerancia --nivel etapa tiempo=... costo=...`; plan de excepción → `pm-director` ejecuta `estado.py limite-etapa --excepcion X-###` (CS→SB) y `pm-plan-etapa-y-limites` produce `02-planificacion/plan-excepcion-X-###.md`, aprobado con `autorizar-plan-excepcion`; se intenta alinear el nuevo fin de etapa con el original. Fuera de tolerancia de proyecto → capa de negocio.
- Una excepción resuelta dentro de tolerancia de etapa no lleva informe, pero aparece en el siguiente highlight. Al cerrar una excepción, al menos una lección (cinco preguntas). La repetición de un tipo de issue señala una falla de gestión en otra parte.

## 7. Cambio ligero (intercambio) en ágil e híbrido
Sin solicitud de cambio completa si se cumplen **todas**: (1) ítems de tamaño equivalente (± tolerancia de alcance de la etapa); (2) no se desplaza ningún Must ni se cambia el objetivo de la iteración sin acuerdo del equipo; (3) no cambia presupuesto, fecha, contrato ni producto de gestión; (4) decide el product owner. Pasos: actualizar backlog; `registro.py agregar decisiones --campo decision="intercambio: entra <ítem>, sale <ítem>" --campo decidido_por="PO: <nombre>" --campo nivel=product-owner --campo artefactos_afectados=backlog`; mencionarlo en el highlight. Si falla una condición → `solicitud-cambio`. En predictivo, el equivalente es el intercambio entre productos opcionales previsto en la tolerancia de alcance (`nivel=gestor`).

## 8. Variante BMAD (`integraciones.especificacion = bmad`)
- Entradas: `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> verificar` informa desvíos respecto de la línea base (ids FR/NFR/UJ/AD agregados o retirados, contenido distinto) y Sprint Change Proposals nuevas (`planning-artifacts/sprint-change-proposal-<fecha>.md`).
- Cada hallazgo entra como issue `solicitud-cambio` (uno por propuesta o por grupo coherente de ids), con fila en `cambios.csv`, citando ids, ruta y sha corto; nunca se copia el texto del PRD.
- Excepción: si el enfoque de issues y cambios declara la elaboración progresiva (detalle o criterios sin cambiar ids ni alcance), se registra como informativa y no requiere decisión.
- Evaluación de impacto como cualquier cambio: historias y paquetes afectados leídos por la fachada (`especificacion.py consultar <id>` / `listar historias`; SPEC §1.16), puntos, fecha, costo, Must desplazados.
- Decide la autoridad de cambio PRINCE2 según la tabla §4. El "sí" del flujo correct-course de BMAD no sustituye esa decisión.
- **Traspaso inverso** (aprobado y afecta la especificación): `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> handoff --cambio C-###` emite `02-planificacion/especificacion/handoff-bmad-<fecha>-C-###.md` y lo anota en `estado.json.integraciones.bmad.handoffs`. Solo acepta cambios con `decision=aprobado`; los ids afectados se toman de `notas` de `cambios.csv`. El equipo BMAD lo aplica con sus flujos (PRD con ids estables, corrección de rumbo, sprint planning) y confirma en la sección 3 del documento. pm-method nunca edita BMAD.
- Tras la confirmación, `bmad.py verificar` debe salir limpio (solo los ids traspasados cambiaron) y `pm-director` fija la nueva línea base: `bmad.py linea-base prd --version <mayor> --por "<rol: nombre>"` (o `arquitectura`, `epicas`…). Esta skill no ejecuta `linea-base`; deja la acción en el bloque de retorno o en `acciones.csv`.
- Rechazado: el equipo revierte en BMAD por su flujo; `verificar` debe volver a salir limpio.
- Historia `retirada-en-bmad` en el backlog: decisión del PO (`nivel=product-owner`) si cabe en la tolerancia; si no, solicitud de cambio.

## 9. Trackers y canales externos
- Issues planteados en un tracker o chat conectado se traen vía `pm-integraciones` como instantánea en `03-control/fuentes/` y se registran en `issues.csv` (el tracker no reemplaza al registro de gobierno).
- Crear tickets, notificar decisiones o publicar el informe solo vía `pm-integraciones`, con vista previa y confirmación explícita.

## 10. Variantes de plantilla y casos borde
- Mínima (solicitante, descripción, justificación, impacto global, disposición) en proyectos pequeños; completa con impactos por dimensión, ítems de configuración y consecuencia de no cambiar cuando el riesgo, el costo o la regulación lo justifiquen.
- Oportunidad de negocio con efectos fuera del proyecto → orientación de la junta antes de evaluar a fondo.
- Issue contractual con proveedor → `pm-adquisiciones`. Fuera de especificación detectado en revisión → `pm-calidad` lo anota en `calidad.csv` y aquí se trata.
- Pedido de aprobar "sobre la marcha" sin registro → explicar la pista de auditoría y registrar antes de implementar.
- Sin enfoque de issues aprobado → valores de referencia declarados y propuesta al ejecutivo.
