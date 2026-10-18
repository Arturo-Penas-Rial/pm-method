# Cambios · Changelog

## 2.2.0 · 2026-10-17 — maestro de interesados, capa de canales y OKR

Versión que convierte el registro de interesados en un maestro con matriz, RACI ligada al plan y perfil de
comunicación por persona, agrega una capa propia para enviar comunicados con aprobación y registro, y amplía OKR con
tipos de KR, check-ins y salud. Retrocompatible: los proyectos 2.1 siguen funcionando sin cambios (migración no
destructiva, sin dependencias nuevas, nada se escribe en BMAD).

### Interesados
- Skill nueva **`pm-interesados`** (agente `pm-inicio`): dueña de `stakeholders.csv`, `estereotipos.csv`,
  `preferencias.csv` y `raci.csv`, y de los artefactos `analisis-stakeholders`, `matriz-raci`,
  `plan-compromiso-stakeholders` (plantillas movidas desde `pm-organizacion-roles`) y `reporte-interesados`. Plantilla
  nueva `entrevista-interesado.md`; guía en `references/guia.md` §1–§12.
- `interesados.py --proyecto G [--medio alto|bajo]` con los subcomandos `matriz`, `estereotipos`, `proponer`,
  `confirmar`, `rechazar`, `perfil`, `raci`, `vinculos`, `integridad`, `reporte` y `plan-envio`.
- **Matriz poder/interés** con estrategia por cuadrante (gestionar de cerca, mantener satisfecho, mantener informado,
  monitorear) y valores de comunicación por defecto; "medio" se ubica del lado alto y se marca como frontera
  (`--medio bajo` lo invierte).
- **RACI** sobre elementos con fuente verificable: paquetes y actividades de la WBS, requisitos, épicas e historias por
  la fachada `especificacion.py` o el backlog, KR y objetivos de `okr.csv`, decisiones de `decisiones.csv`; un solo A
  por elemento.
- **Estereotipos** (6 semilla) y **preferencias** con procedencia (declarado, observado, inferido), estado (propuesta,
  confirmada, rechazada, vencida), cita, fuente y vigencia (defecto 180 días). `proponer` lee entrevistas, actas o
  transcripciones y solo analiza oraciones en primera persona; una persona confirma o rechaza cada propuesta.
- **Perfil de comunicación** resuelto con precedencia cuadrante → idioma del proyecto → estereotipo → matriz de
  comunicaciones → preferencias confirmadas y vigentes; aviso ante conflicto entre preferencia y matriz.
- **Reporte HTML** autocontenido (claro/oscuro, móvil): matriz SVG 2×2, estrategias, RACI, perfiles con procedencia,
  estereotipos, vínculos con OKR, especificación y WBS, envíos e integridad; valoraciones solo con `--restringido`.
- Privacidad: el perfil solo adapta comunicaciones; no se infieren emociones, personalidad, salud ni datos sensibles,
  no se analiza audio ni tono, no se usan tipologías propietarias. La guía §10 cita las normas consultadas (AI Act,
  RGPD, Ley 18.331) sin constituir asesoramiento jurídico.

### Capa de canales
- Nuevo `skills/pm-integraciones/scripts/envios.py` con `nuevo`, `estado`, `aprobar`, `enviar`, `preparar-mcp`,
  `registrar`, `historial` y `verificar`.
- Modos: `smtp`, `slack-webhook`, `teams-webhook` (flujo de Workflows con tarjeta adaptable, límite 28 KB), `eml`
  (archivos con `X-Unsent: 1`) y MCP conectados (`preparar-mcp` → vista previa y confirmación → `registrar --modo mcp`).
- Mensajes en `03-control/comunicaciones/<fecha>-<tema>/` con frontmatter y `plan-envio.csv`, generados desde
  `interesados.py plan-envio` con el perfil de cada destinatario.
- Reglas: sin `--confirmar` es simulación; solo se envían mensajes aprobados (`aprobar --por`); los destinos se leen
  siempre del maestro al enviar; el reenvío solo va a quien falta; cada envío queda en `envios.csv` (EN-###) y en
  `diario.md`; código de salida 2 si hubo fallos.
- Configuración solo por variables de entorno (`PM_SMTP_*`, `PM_SLACK_WEBHOOK_URL`, `PM_TEAMS_WEBHOOK_URL`), nunca en
  archivos. Solo biblioteca estándar (`smtplib`, `email`, `urllib`).
- `estado.json.integraciones.correo` (`ninguno|smtp|gmail|outlook|eml`).

### OKR
- `okr.py` v2.2, retrocompatible (con un `okr.csv` de 2.1 la salida es idéntica). Columnas opcionales `tipo_kr`
  (`de-a`, `mantener-sobre`, `mantener-bajo`, `binario`, `hito`), `compromiso` (aspiracional o comprometido), `peso`,
  `padre_id`, `nivel`, `ciclo`, `fecha_inicio`, `estado`, `ref_externa`; iniciativas `IN-n` ligadas a un KR y a una
  épica, historia o paquete.
- Puntuación por tipo, objetivo como promedio ponderado; semáforo aspiracional 0,7/0,4 y comprometido 1,0/0,7; salud
  (en camino, en riesgo, desviado) contra el avance esperado lineal; confianza 1–10 en tres bandas.
- **Check-ins** en `00-direccion/okr_checkins.csv` (solo se agregan): `--checkin KR --valor V [--confianza N] [--nota]
  [--autor] [--fecha] [--fuente]`; el valor actual es el último check-in hasta el corte.
- Sincronización: `--propuesta-sync tability|perdoo` y `--marcar-publicado KR@FECHA --destino … --ref …`;
  `estado.json.integraciones.okr` admite `perdoo`. Servidores MCP oficiales de Tability y Perdoo verificados el
  17/10/2026; plan comercial requerido: [verificar].
- Avisos nuevos: verbo de actividad en un KR, responsable fuera del maestro, tipo/compromiso/peso inválidos,
  iniciativa sin KR o sin vínculo, KR de hito sin iniciativas, check-in de KR inexistente, todos los aspiracionales en
  1,0 al cierre. Limitación: las iniciativas no guardan historia.

### Identificación de riesgos desde cuatro fuentes
- Nuevo `skills/pm-riesgos/scripts/riesgos.py candidatos [--fuentes bmad,transcripciones,tracker,artefactos]
  [--transcripcion F…] [--instantanea F] [--desde] [--salida] [--json] [--fecha]`: destila **riesgos candidatos** (con
  clase riesgo, supuesto, pregunta o issue, amenaza u oportunidad, cita y ubicación) de BMAD (descubrimiento, brief, PRD,
  arquitectura, UX; solo lectura vía `pm-bmad-puente`), de transcripciones y actas, de una instantánea fechada de Jira u
  otro tracker (lo ocurrido se propone como issue con su riesgo derivado) y, sin BMAD, de los artefactos del proyecto
  (mandato, brief, requisitos, `supuestos.csv` abiertos, `lecciones.csv`). Marca posibles duplicados o relaciones con
  riesgos ya registrados. Escribe solo el borrador `03-control/reportes/<fecha>-candidatos-riesgo.md`: nada entra al
  registro sin formularse y evaluarse.
- `bmad.py inventario` (v6) suma la clave `descubrimiento` (brainstorming, PRFAQ, investigación) [verificar por versión].
- `pm-riesgos` paso 3 y guía §2 (tabla de fuentes) y §8; `pm-integraciones` guía §3: columnas opcionales del tracker
  `prioridad`, `etiquetas`, `vinculo`, `descripcion`.
- `interesados.py proponer` ignora menciones negadas («por Slack, no por correo» propone solo Slack).

### Integridad y sanidad
- `esquema.py`: 4 registros opcionales que se crean al primer uso (estereotipos ET-, preferencias PF-, raci RC-,
  envios EN-; 13 registros en total), claves foráneas (`refs`), unicidad (`unico`: elemento + stakeholder_id en raci)
  y `uno_por` (un solo A por elemento). `stakeholders.csv` suma al final `estereotipo`, `correo` y `usuario_chat`.
- `registro.py agregar|actualizar` valida esas reglas (`--forzar` registra igual y sanidad lo detecta).
- `sanidad.py`: familia nueva **STK-00…STK-11** (ejecuta `interesados.py integridad` cuando existe alguno de los
  registros nuevos); REG-08 incluye los prefijos ET, PF, RC y EN.
- `puertas.py` en `autorizar-proyecto`: avisos P-09 (interesados vacío o sin poder/interés) y P-10 (sin `raci.csv` ni
  artefacto `matriz-raci`); no bloquean.
- `hooks/guardian.py` protege `estereotipos.csv`, `preferencias.csv`, `raci.csv` y `envios.csv`; `interesados.py` y
  `envios.py` figuran entre los scripts permitidos.

### Controles permanentes
Controles que antes se hacían a mano, tarde o nunca (por falta de estándar, por trabajo manual o por volumen) y que
ahora detectan `sanidad.py` y `puertas.py` en cada corrida. Todos son AVISO o INFO salvo donde se indica.
- **Presupuestos de la junta** en `estado.json` → `presupuestos` (`cambio`, `riesgo`, `gestion`,
  `limite_autoridad_cambio`; montos numéricos sin moneda ni separador de miles: `10.000` se rechaza): `estado.py presupuesto clave=monto …
  [--por "Rol: Nombre"] [--fecha AAAA-MM-DD]`; con `--por` queda en `decisiones.csv`; `estado.py resumen` los muestra.
  Reservado a pm-director (`hooks/guardian.py`).
- `cambios.csv` suma las columnas **`costo`** (numérica) y **`cargo`** (`presupuesto-cambio`, `reserva-riesgo`,
  `reserva-gestion`, `plan-excepcion`, `sin-costo`).
- Familia **CAM** (cambios aprobados, implementados o cerrados, o con `decision=aprobado`): CAM-01 impacto de costo sin
  `costo` ni `cargo`, o costo sin cargo · CAM-02 cargo a la reserva de riesgo sin citar un R-### · CAM-03 consumo del
  presupuesto de cambio y de la reserva de riesgo (INFO < 80 %, AVISO ≥ 80 %, **ERROR > 100 %**, que bloquea puertas;
  AVISO si se cargó sin presupuesto fijado) · CAM-04 costo sobre `limite_autoridad_cambio` no decidido por la junta o el
  ejecutivo · CAM-05 reserva de gestión no liberada por la junta.
- Familia **QUA** (calidad a volumen): QUA-01 elemento terminado de `02-planificacion/backlog.csv` sin revisión
  completada y aprobada en `calidad.csv` que lo cite (id completo o clave corta `N-M`) · QUA-02 revisión planificada o en
  curso con `fecha_prevista` vencida al corte · QUA-03 revisión rechazada sin issue, acción o cambio que cite su Q-###.
- **EVM vigilado**: `evm.py … --proyecto G --guardar [--corte AAAA-MM-DD]` guarda `03-control/reportes/evm-<corte>.json`.
  Familia **TOL**: TOL-01 (AVISO) el último corte pronostica excepción y no hay excepción abierta ni puerta
  `autorizar-plan-excepcion` posterior · TOL-02 (INFO) semáforo en ámbar · TOL-03 (INFO) etapa de entrega sin corte
  guardado o con el último de más de 31 días.
- **STK-12** (compromiso sostenido; `interesados.py integridad --corte` y sanidad): para los cuadrantes gestionar de
  cerca, mantener satisfecho y mantener informado, compara el último envío `enviado` de cada interesado en
  `envios.csv` (reuniones y llamadas se registran como envío manual) con la frecuencia de su perfil; tolerancia 1,5 ×
  el período. Frecuencia nueva **`trimestral`** (92 días), también reconocida por `interesados.py proponer`.
- **Condiciones formales de puertas**: con `--decision condicionado`, los hallazgos de tipo condición de la verificación
  (p. ej. CONCERNS del gate de preparación de BMAD, P-04, P-06) pasan a condiciones de la puerta. Las condiciones abiertas
  cuentan también para decisiones `aprobado` con `--condiciones` (p. ej. `decision-ad-hoc`) en EST-12, `puertas.py
  estado` y `estado.py resumen`. Control nuevo **G-01** en `puertas.py verificar` de `autorizar-proyecto`,
  `autorizar-etapa` y `autorizar-plan-excepcion` (condición) y de `autorizar-cierre` (**bloqueo**) mientras haya
  condiciones abiertas de puertas anteriores. `estado.py cumplir-condiciones <tipo> [--fecha] [--por] [--nota]` las cierra,
  guarda quién verificó y la nota, lo anota en `decisiones.csv` (con `--por`) y falla si no hay condiciones abiertas.
- **P-04** (`autorizar-proyecto`): condición si los criterios de éxito están solo en OKR (el business case no menciona
  beneficios —B-n, SM-n o la palabra «beneficio»— y no hay artefacto `enfoque-beneficios*`); aviso "sin enfoque de
  beneficios" si el business case los menciona pero no hay enfoque.
- `sanidad.py --corte AAAA-MM-DD`: fecha de corte de los controles con vencimiento (REG-07, QUA-02, TOL, STK-12), para
  informes reproducibles.
- `puertas.py preparacion-bmad --fecha` fecha también la decisión anotada en `decisiones.csv`.
- `riesgos.py candidatos` excluye de la fuente "artefactos" el enfoque de riesgo y la evaluación de probabilidad e
  impacto (son método, no riesgos).
- `SPEC.md` §1.10.3 lista las claves `descripcion-producto-<id>` y `tolerancias-y-autoridad`.

### Skills y agentes
- Descripciones nuevas o cambiadas: `pm-interesados` (nueva), `pm-organizacion-roles` (ahora solo estructura de
  gestión, roles y team charter), `pm-comunicacion-stakeholders` (matriz, mensajes por audiencia y envío),
  `pm-integraciones` (capa de canales) y `pm-okr` (tipos de KR, check-ins, salud, Tability o Perdoo).
- `pm-reuniones`: paso 7, distribución del acta por la capa de canales; paso 7b, preferencias declaradas con
  `interesados.py proponer`.
- `pm-orquestador`: fila de enrutamiento para interesados, matriz, RACI, estereotipos y preferencias; "enviar a
  interesados" en la fila de comunicación; `pm-interesados` en SU.
- Agentes: rutas de `interesados.py` y `envios.py`; `pm-inicio` pasos 4b y 13b; `pm-control` pasos 4 (preferencias) y
  10 (check-ins de OKR, comunicación personalizada y envío).
- `pm-registros/templates/guia-registros.md`: secciones 7.1–7.4 de los registros nuevos.
- Controles permanentes en skills y agentes (sin cambiar descripciones ni frontmatter): `pm-sanidad` (familias CAM, QUA,
  TOL y STK-12, `--corte`, dueños), `pm-issues-cambios` guía §4.1 (presupuesto de cambio, `costo` y `cargo`),
  `pm-calidad` guía §8.1 (calidad a volumen), `pm-progreso-reportes` guía §3 y §8 (`evm.py --guardar`, TOL),
  `pm-costos-presupuesto` guía §3 (presupuestos en `estado.json`), `pm-interesados` guía §7 (STK-12),
  `pm-direccion-decisiones` guía (presupuestos y condiciones), `guia-registros.md` (columnas `costo` y `cargo`);
  `pm-control` paso 8 (corte de EVM guardado y sanidad con `--corte`) y `pm-director` modo B paso 6 (`presupuesto`,
  `cumplir-condiciones`).
- 38 skills (32 invocables por el modelo; listado de 6.546 caracteres), 6 agentes, 3 hooks; versión 2.2.0 en
  `plugin.json`, `compatibilidad.json`, `esquema.py` y todos los SKILL.md.

### Pruebas y guías
- `probar_paquete.py`: 80 → **138** pruebas. Caso H (33 comprobaciones): maestro de interesados (matriz, RACI,
  estereotipos, preferencias), capa de canales con SMTP y webhooks de Slack y Teams contra servidores locales en
  127.0.0.1, y OKR v2.2. Caso I (9): candidatos de riesgo desde las cuatro fuentes, la negación en `proponer`, el enfoque
  de riesgo excluido como fuente y la frecuencia trimestral. Caso J nuevo (16): controles permanentes (presupuestos y
  hook, `costo` numérico, CAM-01…04, bloqueo de puerta por CAM-03, P-04, condiciones formales, G-01 y
  `cumplir-condiciones`, QUA-01…03, `evm.py --guardar` y TOL-01, STK-12).
- Las cuatro guías E2E muestran los controles permanentes, cada una con la sección "Controles permanentes que muestra
  esta guía" (problema habitual · control · código · paso):
  - **E2E-1** (13 pasos, 90–115 min): candidatos de BMAD, de la transcripción y de Jira; paso 13 sin BMAD; presupuesto de
    riesgo fijado por la junta y consumo de la reserva vigilado (CAM-02, CAM-03), P-04.
  - **E2E-2** (10 pasos, 80–110 min): autoridad de cambio con presupuesto y límite, cambio de alcance con costo y cargo,
    EVM ágil guardado, calidad de lo terminado (QUA-01) y paso 10 nuevo de gestión por excepción (CAM-03 ERROR, CAM-04,
    TOL-01, informe y plan de excepción, condición de la junta cumplida).
  - **E2E-3** (13 pasos, 100–130 min): maestro de interesados, preferencias, RACI, enfoque de beneficios con OKR que lo
    complementan, envío por canales y paso 13 nuevo de compromiso sostenido (STK-12, acción correctiva y reevaluación).
  - **E2E-4** (15 pasos, 3–4 h): condición formal desde el CONCERNS de BMAD (EST-12, G-01, `cumplir-condiciones`),
    cambio con presupuesto, calidad a volumen (QUA-01, QUA-02), cierre con traspaso y paso 15 posterior al proyecto
    (primera revisión de beneficios).
  - Imágenes `g3-interesados-matriz.png` y `g3-interesados-raci-perfiles.png`; `guias_e2e/correr.py` 4/4 OK; `base.py`
    sanea la marca de tiempo del índice en la evidencia.
- `validar_mermaid.py --render`: 127 bloques, 0 errores; `validar_paquete.py`: OK; `claude plugin validate .`: pasa.

### Pendientes
- **Pruebas en vivo de enrutamiento** con Claude Code real: no se corrieron para 2.2 y cambiaron cinco descripciones.
  Recomendado: `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids <afectados>` (consume tokens) y, antes de
  publicar, `suite.py todo`.
- Controles permanentes (CAM, QUA, TOL, STK-12, G-01): probados con scripts (caso J y guías E2E); no se probaron en vivo
  con Claude Code real.
- Plan comercial que exigen los servidores MCP de Tability y Perdoo: [verificar].
- Exposición de objetivos por los MCP oficiales de otras herramientas de OKR: [verificar].
- Alcance exacto de la exclusión de texto escrito en el art. 5(1)(f) del AI Act (solo fuentes secundarias): [verificar].

## 2.1.0 · 2026-10-17 — madurez para uso real

Versión surgida de pruebas en vivo con Claude Code real (enrutamiento de 75 frases y siete escenarios de orquestación)
y de una revisión de cada script contra una instalación real de BMAD 6.12.4.

### Guías de prueba para el usuario
- `docs/guias/`: cuatro recorridos de punta a punta escritos como prompts del usuario, con respuestas a las preguntas
  del sistema, resultado esperado, dónde verificar, reporte de ejemplo y gráficos (Mermaid y capturas del tablero):
  E2E-1 riesgos, E2E-2 alcance/cambio/esfuerzo/priorización/roadmap, E2E-3 interesados/comunicaciones/OKR/avance,
  E2E-4 producto de la idea al producto con BMAD.
- `scripts/pruebas/guias_e2e/`: los recorridos con los scripts reales sobre el fixture BMAD 6.12.4 (≈ 1 min, sin
  tokens); evidencia en `docs/guias/evidencia/`.
- `CASOS-DE-USO`, `CASO-MAESTRO` y `CASOS-DE-USO-INTEGRACIONES`: cada caso con el prompt del usuario, sus respuestas,
  entradas (qué aporta el usuario y cómo) y salidas (qué queda y dónde verificarlo); los comandos quedan como
  referencia de lo que ejecuta el sistema.
- `pm-visuales` guía §3: documentado el formato de `decisiones_pendientes` del tablero (`{id, texto, fecha_limite}`).

### Diagramas
- Corregidos los bloques Mermaid que GitHub no renderizaba (`;` en mensajes de secuencia, paréntesis en etiquetas de
  arista sin comillas, marcadores `{{…}}` en fechas de gantt, números de xychart/quadrant e ids de nodo: ahora valores
  de ejemplo con un comentario `%%` que indica qué marcador reemplazan).
- Legibilidad: diagramas de arquitectura (README, ARQUITECTURA), sincronización, verificación y orquestación de puertas,
  flujo de orquestación y mapa del caso maestro rediseñados verticales (≤ 900 px de ancho natural: letra más grande en
  GitHub) y sin etiquetas superpuestas ni texto cortado.
- README reorganizado: justificación, beneficios por perfil con evidencia, y arquitectura, ciclo de vida, ciclo
  integrado PRINCE2 + BMAD y verificación de puertas como diagramas al comienzo.
- `INSTALACION.md` §0.7 nueva: dónde y cómo configurar las credenciales (suscripción o `ANTHROPIC_API_KEY` en Claude
  Code, `~/.hermes/.env` en Hermes, tokens de MCP), precedencia y reglas de seguridad. §0.8 nueva: Orca (opcional).
- Nuevo `scripts/validar_mermaid.py`: lint estático de esos errores + render real con mmdc (122 bloques, 0 errores).

### Guardarraíles y roles
- `hooks/guardian.py` reescrito: además de Write/Edit, bloquea escrituras directas por **Bash** (`sed -i`, `>`/`>>`,
  `tee`, `cp`/`mv`/`rm` hacia destinos protegidos, `open(...,'w')`, `json.dump`, `to_csv`) sobre `estado.json`,
  registros CSV, derivados de la especificación, `00-direccion/historial/` e instantáneas existentes de
  `03-control/fuentes/`. Ya no da falso positivo con `2>&1`.
- Separación de roles en el hook: desde subagentes pm-* (salvo pm-director) se niegan `estado.py puerta|rol|tolerancia|
  agil|umbrales-riesgo|cumplir-condiciones`, `limite-etapa --excepcion`, `set --forzar` y `aprobar` sin
  `--nivel gestor|product-owner|equipo`. El subcomando se identifica por análisis del comando, no por palabras sueltas.
- `estado.py set` ya no cambia `fase` ni `proceso_actual` (salvo `--forzar --por`, que queda en `decisiones.csv`).
- Nuevo nivel de decisión `ejecutivo`.
- Agentes: bloque "Reglas operativas comunes (v2.1)" (rutas de scripts, escrituras solo por script, idioma, lectura
  por secciones, no ofrecer desactivar hooks) y "Reservado a pm-director" en los agentes de fase.
- `pm-director` congela PID y business case v1.0 también cuando `autorizar-proyecto` es condicionado.

### Enrutamiento e idioma
- Hook `SessionStart`: ya no envía todo al orquestador; nombra la skill dueña cuando el pedido nombra un producto,
  imprime la ruta absoluta de los scripts, la regla de idioma y la regla de no esquivar hooks.
- Descripciones ajustadas (pm-reuniones, pm-calidad, pm-knowledge, pm-orquestador, pm-sanidad, pm-bmad-puente).
- Regla de idioma unificada en las 37 skills: responder en el idioma del usuario; artefactos en `estado.json.idioma`.
- Resultado en vivo: enrutamiento 59/60 (antes 82 %); idioma 3/3; guardarraíles 4/4.

### Scripts
- Rutas de scripts expandibles: `${CLAUDE_SKILL_DIR}/../pm-X/scripts/` en skills y `${CLAUDE_PLUGIN_ROOT}/skills/…` en
  agentes (antes un marcador que obligaba a buscar con `find`).
- `estado.py`: `resumen`; `puerta autorizar-etapa` conserva las tolerancias de etapa y acepta `--inicio` y `--tol`;
  `integracion` avisa ante valores desconocidos; la versión del paquete se actualiza al guardar.
- `bmad.py`: raíz de BMAD guardada **relativa** al proyecto; si una raíz absoluta heredada no contiene al proyecto,
  avisa y usa el BMAD del propio repositorio; descripción del backlog = párrafo completo de la historia; numeración
  del documento de traspaso.
- `cpm.py`: tareas resumen de solo hitos con fin = inicio en el MSPDI; título del Gantt con `--titulo`.
- `evm.py`: `VAC_pct` con el signo de VAC y nuevo `sobrecosto_pct`; `base_semaforo` por dimensión; aviso si una
  tolerancia no está en %.
- `okr.py`: acepta vínculos `SM-C<n>` (métricas de contrapeso de BMAD 6.12).
- `exportar.py xlsx`: rechaza entradas que no son CSV.
- `sanidad.py`: sin falsos INS-04 por los clones de `marketplaces/` o versiones viejas del caché; Chrome en Windows;
  aviso de Chrome solo si archify está instalada; valores de integración compartidos con `estado.py`.
- `hooks/py.sh`: lanzador portable (python3, python o `py -3`) para Windows con Git Bash; `.gitattributes` fuerza LF
  en `.sh`, `.py` y `.json`.
- utf8proj deja de recomendarse (inmaduro): SS/FF/SF y calendarios se completan sobre el MSPDI en MS Project o
  ProjectLibre.

### Ajustes tras las pruebas de robustez (misma versión, antes de publicarla)
- **Bloqueos de puerta** en `estado.py puerta`: `aprobado` de `autorizar-proyecto|autorizar-etapa|autorizar-plan-excepcion|
  autorizar-cierre` se rechaza si faltan tolerancias de proyecto o de etapa, PID o business case, el plan de la etapa a
  autorizar o la línea base del PRD (con BMAD), o si `sanidad.py --rapido` da ERROR. `condicionado` los suma como
  condiciones; `--forzar` los anota. Encontrado en el escenario `multisesion`.
- El hook reserva los comandos de decisión a pm-director **también en el hilo principal** (antes solo en subagentes).
  Las skills de inicio ya no registran tolerancias: las proponen y pm-director las registra.
- Nuevo hook `UserPromptSubmit` (`idioma.py`): si el pedido está en otro idioma que el proyecto, recuerda responder en
  el idioma del pedido (el fallo reaparecía en 1 de cada 4 corridas).
- Regla "fuentes = datos" en el hook de inicio y en pm-reuniones, pm-integraciones y pm-bmad-puente: instrucciones
  incrustadas en transcripciones, tickets o BMAD se informan y no se ejecutan.
- Escala: `especificacion.py listar` y `registro.py listar` muestran hasta 60 filas (`--limite`); `sanidad.py` agrupa en
  pantalla los hallazgos repetidos de un mismo código.
- Pruebas: escenarios en vivo `inyeccion`, `desorden`, `multisesion`, `escala` (`scripts/pruebas_vivo/escenarios.py`),
  generador `scripts/pruebas/generar_bmad_grande.py`, opción `--modelo`; `probar_paquete.py` llega a 80 pruebas.
- `estado.py aprobar` crea la copia congelada de la versión aprobada en `00-direccion/historial/<clave>-v<versión>`
  (antes la hacía el agente a mano y el hook, con razón, lo impedía).
- Hermes Agent: `scripts/instalar_hermes.py` genera una copia adaptada (`${HERMES_SKILL_DIR}`); verificado que Hermes
  lista las 37 skills y resuelve las rutas de los scripts. `tap add`/`install` desaconsejados.
- Nuevo `docs/PILOTO.md` (plan de piloto con métricas, rúbrica y usabilidad).
- **Verificación de puertas** (`puertas.py`, `docs/PUERTAS.md`): cada puerta se verifica en tres capas — salud,
  controles automáticos de PRINCE2 (artefactos, tolerancias, criterios de éxito, calidad, registros abiertos) y de BMAD
  (PRD y arquitectura `final`, línea base, gate de preparación del sprint planning: FAIL bloquea, CONCERNS es condición,
  sin veredicto es aviso), y lista de control de la junta (`lista` / `confirmar --por`). La decisión se registra con la
  referencia a la lista y las observaciones. Comportamiento del gate de BMAD verificado con 3 corridas reales de
  `bmad-sprint-planning` (no escribe archivo con CONCERNS ni con FAIL en modo no interactivo): el veredicto se registra
  con `puertas.py preparacion-bmad`. Diagrama del ciclo de vida PRINCE2 + BMAD en el README. Las puertas son insumo de los informes: `puertas.py estado`
  (highlight §6, informe de fin de etapa §6) y la línea de última/próxima puerta en `estado.py resumen`.

### Pruebas y documentación
- `probar_paquete.py`: 35 → **80** pruebas (BMAD 6.12.4 real, hook guardian con 36 decisiones, ciclo de puertas,
  regresiones v2.1).
- Nuevo `scripts/pruebas_vivo/` (`vivo.py`, `suite.py`) y `docs/evaluacion/resultados/`.
- Nuevos documentos: `RESUMEN-EJECUTIVO`, `INDICE`, `DEPENDENCIAS`, `PRUEBAS`, `CASOS-DE-USO-INTEGRACIONES`,
  `CLAUDE.md`, `AGENTS.md`; README con diagramas Mermaid; `INSTALACION` con requisitos por sistema operativo, BMAD,
  skills externas, MCP y verificación de 12 pasos.
- Clave canónica `acta-reunion-<fecha>`; ejemplo de colisión corregido (riesgos → pm-riesgos); drawio identificado
  como `jgraph/drawio-mcp` (npm `@drawio/mcp`).

## 2.0.0 · 2026-10-14

Orquestador en el hilo principal y cinco subagentes de fase; comandos como skills; puente BMAD de solo lectura con
fachada de especificación (`pm-spec-index/1`) y traspaso; integraciones MCP genéricas; OKR; actas desde
transcripciones; MSPDI; sanidad del ecosistema y hooks; migración automática desde v1.

## 1.0.0

Primera versión: agentes y skills PRINCE2 7 + PMBOK 8 + plantillas, ES/EN.
