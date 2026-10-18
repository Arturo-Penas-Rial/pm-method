# Guía de comunicación con stakeholders · Stakeholder communication guide

## 1. Estereotipos de audiencia y mensaje por defecto
Estos seis estereotipos se cargan como catálogo editable con `interesados.py estereotipos --semilla` (`pm-interesados`, `estereotipos.csv`), donde además se combinan con la estrategia del cuadrante poder/interés y las preferencias confirmadas de cada persona (perfil resuelto: `interesados.py perfil`).

| Estereotipo | Quién suele estar | Qué le importa | Qué NO recibe por defecto | Canal típico |
|---|---|---|---|---|
| dirección-patrocinador | ejecutivo, junta, capa de negocio, PMO | decisiones pendientes, desvíos contra tolerancias, riesgos del business case, hitos de puerta | detalle operativo, listas de tareas | paquete de decisión, highlight, reunión de junta |
| equipo | gestores de equipo, miembros, soporte | bloqueos, prioridades, cambios aprobados, tolerancias de paquete, qué no cambia | deliberaciones de la junta no cerradas, cifras comerciales | checkpoint, tablero, chat del equipo |
| cliente-usuario | usuario sénior, usuarios finales, cliente externo | hitos y entregas, qué recibe y cuándo, riesgos que afectan su operación, qué se le pide | costos internos, asuntos de proveedores, valoraciones de interesados | reunión de seguimiento, correo, demo |
| proveedores | proveedor sénior, contratistas | dependencias, fechas de entrada, aceptaciones, hitos de pago, cambios contractuales | business case interno, información de otros proveedores | reunión contractual, correo formal |
| regulador-comunidad | autoridades, comunidad afectada | cumplimiento, impacto, hitos públicos | todo lo no autorizado por el ejecutivo | canal institucional, fase silenciosa si aplica |
| product owner y usuarios clave (ágil) | PO, usuario sénior delegado, usuarios de negocio | incremento terminado, retroalimentación, cambios del backlog, Must en riesgo | deliberaciones internas, costos internos | revisión de iteración / demo, tablero del backlog |

*Mapeo del paquete; se ajusta con la matriz aprobada.*

## 2. Construcción de la matriz
- Una fila por audiencia × mensaje: canal, frecuencia, emisor, idioma, retroalimentación (canal de escucha), regla de comunicación extraordinaria, quién autoriza información sensible.
- Prioridad por poder × interés: `alto/alto` gestionar de cerca; `alto/bajo|medio` mantener satisfecho; `bajo|medio/alto` mantener informado; resto monitorear.
- Cada interesado del registro en al menos una fila; la cadencia coincide con la del enfoque de comunicación (aquí no se redefinen políticas; ante conflicto prevalece el enfoque aprobado).
- En ágil o híbrido, la revisión de iteración figura como evento recurrente (cadencia `agil.cadencia_iteracion_dias`).
- Registro: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> artefacto matriz-comunicaciones --ruta 02-planificacion/matriz-comunicaciones.md --estado en-revision`; tras el acto del ejecutivo, `estado.py aprobar matriz-comunicaciones --por "Ejecutivo: <nombre>"`. Dentro del PID, lo registra `pm-director` con la puerta.
- Al aprobarse: `registro.py actualizar stakeholders ST-### --campo canal=... --campo frecuencia=...`.
- La matriz se revisa en cada límite de etapa y cuando cambian los influenciadores clave.

## 3. Comunicado por audiencia
- Hecho a comunicar con su fuente (id en `decisiones.csv`, `issues.csv`, `cambios.csv`, ruta del informe, acta de `pm-reuniones`).
- Ejecutivo: decisión o desvío primero, contexto después, una pantalla, decisiones pedidas con fecha límite (un comunicado sin pedido explícito se cuestiona); adaptado a la forma de trabajar del patrocinador.
- Equipo: qué cambia, bloqueos, prioridades, a quién preguntar.
- Cliente: hitos, qué recibe y cuándo, riesgos que le afectan, qué se le pide; sin costos internos no autorizados.
- Proveedores cuando la matriz lo exige.
- Las mismas cifras en todas las versiones; con el highlight, la selección por audiencia la define `pm-progreso-reportes`.
- Comunicaciones de puerta (inicio, autorización, cierre): a nombre de la junta, firma del ejecutivo.
- Excepción urgente: comunicación verbal inmediata y luego el informe escrito; el comunicado nunca sustituye al informe de excepción.

## 4. Seguimiento del plan de compromiso
- Fuente: `plan-compromiso-stakeholders` (de `pm-organizacion-roles`) y `stakeholders.csv` (`nivel_compromiso_actual` vs. `nivel_compromiso_deseado`).
- Cada período: brechas que persisten (p. ej. `resistente` → objetivo `partidario`), acciones de comunicación del plan cumplidas o vencidas (`acciones.csv`), señales de las actas (`pm-reuniones`), y ajuste de mensajes, canal o frecuencia en la matriz.
- Cambios de valoración de una persona: los propone esta skill, los decide quien es dueño de la relación y se registran en `stakeholders.csv` (filas `confidencial=si` de circulación restringida); el nuevo análisis completo es de `pm-organizacion-roles`.
- Interesados nuevos → `pm-organizacion-roles`.

## 5. Revisión de iteración o demo como evento de comunicación
- Antes: invitar al PO, usuarios clave y, al cierre de release o etapa, al ejecutivo; agenda corta (objetivo de la iteración, incremento terminado según la DoD, burn-up de `pm-progreso-reportes` —con BMAD, desde `avance-bmad.csv`—, Must en riesgo, preguntas al usuario).
- Durante: solo lo terminado; la retroalimentación son ítems candidatos al backlog, no compromisos; lo aceptado por el usuario es evidencia de calidad (`metodo_verificacion=demostracion`, vía `pm-calidad`).
- Después: el acta, las acciones y las decisiones los produce `pm-reuniones` (tipo `revision-iteracion`); intercambios del PO → `decisiones.csv` `nivel=product-owner` (cambio ligero de `pm-issues-cambios`); desplazar un Must → solicitud de cambio. Esta skill emite el comunicado corto al patrocinador si cambió el pronóstico de Must.
- La retrospectiva no es evento de comunicación externa: `pm-agil-hibrido`.

## 6. Envíos externos (capa de canales)
- **Personalización**: `interesados.py plan-envio` resuelve el perfil de cada destinatario (cuadrante → estereotipo → matriz → preferencias confirmadas) y crea un borrador por persona (o por grupo con `--agrupar`) en `03-control/comunicaciones/<fecha>-<tema>/`. Para enviar un artefacto ya hecho (highlight, acta, decisión de puerta, OKR): `envios.py nuevo --origen <archivo> --audiencia … --asunto … --proposito informe|acta|puerta|okr|recordatorio|convocatoria`.
- **Aprobación**: `envios.py aprobar <carpeta> --por "Gestor: Nombre"`; rechaza borradores sin redactar o con destinatarios que ya no existen en el maestro.
- **Transportes** (`envios.py enviar <carpeta> --modo …`, simulación por defecto, `--confirmar` para enviar):

| Modo | Canal | Configuración (solo variables de entorno) | Qué hace |
|---|---|---|---|
| `smtp` | correo | `PM_SMTP_HOST`, `PM_SMTP_REMITENTE`, opcionales `PM_SMTP_PUERTO` (587), `PM_SMTP_TLS` (starttls, ssl, ninguno), `PM_SMTP_USUARIO`, `PM_SMTP_CLAVE` | un correo por destinatario, Message-ID como referencia |
| `eml` | correo | ninguna | genera `.eml` por destinatario para abrir y enviar desde el cliente de correo; luego `envios.py registrar --modo eml` |
| `slack-webhook` | slack | `PM_SLACK_WEBHOOK_URL` | publica en el canal del webhook y menciona a quienes tienen `usuario_chat` de Slack |
| `teams-webhook` | teams | `PM_TEAMS_WEBHOOK_URL` (Workflows de Teams) | publica una tarjeta adaptable (límite 28 KB) |
| conector MCP | correo, slack, teams | el conector conectado en la sesión | `envios.py preparar-mcp` → el agente envía con la herramienta tras la vista previa → `envios.py registrar --modo mcp --referencia …` |

- Canales no electrónicos (reunión, llamada, tablero): se entregan en el evento y se registran con `envios.py registrar --modo manual`.
- Cada envío queda en `03-control/registros/envios.csv` (EN-###, con propósito, destino y referencia) y en `diario.md`. Reintento: `enviar` de nuevo solo envía a quienes falta. Los destinos se toman siempre del maestro vigente.
- Correo de seguimiento de acciones (`templates/correo-seguimiento.md`): solo a partir de un acta confirmada (producida por `pm-reuniones`) o de un comunicado aprobado; acciones con su id `A-###` de `acciones.csv`.

## 7. Columnas de registros usadas
- `stakeholders.csv` (ST-###): `nombre`, `rol_proyecto`, `poder`, `interes` (alto/medio/bajo), `actitud`, `nivel_compromiso_actual`, `nivel_compromiso_deseado` (lider/partidario/neutral/resistente/desconocedor), `canal`, `frecuencia`, `responsable_relacion`, `confidencial` (si/no), `estereotipo`, `correo`, `usuario_chat`.
- `acciones.csv` (A-###): `fecha`, `origen`, `descripcion`, `responsable`, `fecha_compromiso`, `prioridad`, `estado` (abierta/en-curso/completada/cancelada), `fecha_cierre`, `notas`.
- Esquemas vigentes: `registro.py esquema stakeholders|acciones`.

## 8. Reglas extendidas y guardarraíles
- Comunicación bidireccional: cada comunicado define cómo se recibe la retroalimentación; la matriz incluye canales de escucha.
- Los informes periódicos tienen sesgo: la matriz prevé conversaciones informales con gestores de equipo e influenciadores; los focos de resistencia indican dónde comunicar más.
- Fase silenciosa en proyectos sensibles: comunicación amplia mínima hasta que la definición sea estable; se registra como decisión.
- Técnicas (PMBOK, dentro del enfoque de comunicación PRINCE2): análisis de requisitos de comunicación, matriz actual/deseado de involucramiento, métodos interactivo/empuje/atracción.
- Privacidad: no solicitar ni retener datos personales innecesarios; valoraciones de interesados solo en documentos de circulación restringida.
- Análisis de dinámica o clima de reuniones: no se hace aquí; es de `pm-reuniones` (agregado, con consentimiento). Esta skill solo recibe sus sugerencias de ajuste a la matriz.
- Versión mínima: matriz de cinco columnas y cuatro a seis filas; completa cuando el riesgo, el costo o la cantidad de stakeholders lo justifican.

## 9. Traspaso a pm-reuniones (v2)
Hasta v1 esta skill producía actas, decisiones y acciones desde reuniones o transcripciones, con su guardarraíl de análisis de reuniones. Desde v2 esa responsabilidad, la plantilla `acta-reunion.md` y el análisis agregado de clima son de `pm-reuniones` (`<pm-reuniones>/templates/acta-reunion.md`, `${CLAUDE_SKILL_DIR}/../pm-reuniones/scripts/transcripcion.py`). Pedidos de acta, minuta o transcripción se derivan allí; esta skill toma el acta confirmada como fuente de comunicados y correos de seguimiento.
