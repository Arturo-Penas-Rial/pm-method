# Guía de integraciones · Integration guide

## 1. Capacidades y cómo reconocer la herramienta
| Capacidad | Qué se necesita | Indicios en los nombres de herramientas MCP | Ejemplos de operaciones (leer siempre la descripción real) |
|---|---|---|---|
| tracker | leer y crear/actualizar tickets | `jira`, `atlassian`, `rovo`, `linear`, `github`, `azure`, `devops` | buscar por consulta (JQL u otra), leer ticket, crear, editar, transicionar, comentar |
| docs | leer y publicar páginas | `confluence`, `notion`, `sharepoint`, `drive` | buscar, leer página, crear o actualizar página |
| chat | publicar y leer mensajes | `slack`, `teams`, `workiq` | enviar mensaje a canal, leer hilo |
| correo | redactar/enviar | `gmail`, `outlook`, `mail` | crear borrador, enviar |
| calendario | eventos y asistentes | `calendar`, `outlook` | listar eventos, crear evento |
| reuniones | transcripciones | `granola`, `fireflies`, `zoom`, `minutes`, `teams` | listar reuniones, obtener transcripción |
| okr | objetivos, KR y check-ins | `tability`, `perdoo` | leer objetivos y progreso; publicar check-ins (`tability_create_checkin`, `update_goal_progress`) con confirmación |

Notas verificadas al 2026-10-17 (revisar documentación vigente): el servidor remoto oficial de Atlassian (Rovo MCP Server) requiere obtener primero el `cloudId` con su herramienta de recursos accesibles; Slack tiene servidor oficial con restricciones por tipo de app; el servidor "Teams (preview)" de Microsoft está marcado como legado.

## 2. Mapeo de campos
### Jira (u otro tracker) ↔ backlog.csv
| backlog.csv | Tracker | Regla |
|---|---|---|
| id | clave del ticket (o `refs` si el id es de BMAD) | si el backlog es de BMAD, guardar la clave del tracker en `notas` como `jira:ABC-12` |
| titulo | resumen | lectura |
| estado | estado del flujo | lectura; no cambia la prioridad de gobierno |
| estimacion | story points | lectura si el equipo estima en el tracker |
| iteracion | sprint | lectura |
| moscow, release, producto_pbs, prioridad | — | solo pm-method |

### acciones.csv ↔ tracker
| acciones.csv | Tracker | Regla |
|---|---|---|
| descripcion, responsable, fecha_compromiso | resumen, asignado, vencimiento | crear ticket solo con confirmación; guardar la clave en `notas` |
| estado | estado | conciliar en cada período |

## 3. Formato de instantánea
CSV con cabecera y columnas normalizadas; primera línea comentada no permitida (para que lo lean los scripts). Nombre: `03-control/fuentes/<sistema>-AAAA-MM-DD.csv`. Columnas mínimas para tracker: `clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url`; opcionales que usa `pm-riesgos` (`riesgos.py candidatos --fuentes tracker`) para destilar issues y riesgos emergentes: `prioridad`, `etiquetas` (p. ej. `riesgo`), `vinculo` (épica o historia) y `descripcion`. Para mensajes o páginas: Markdown con front matter `fuente`, `fecha`, `consulta`.

## 4. Mensajes tipo (borradores, se envían solo con confirmación)
- **Highlight breve (chat)**: estado general en una línea; semáforos tiempo/costo/alcance; 3 logros; 3 riesgos/issues con id; decisiones pendientes de la junta; enlace al informe.
- **Recordatorio de acciones vencidas**: por responsable, lista de A-### con fecha; tono neutro; sin juicios sobre personas.
- **Convocatoria a puerta**: decisión requerida, documentos del paquete, fecha límite.

## 5. Capacidad `correo` y `okr`
- `estado.json.integraciones.correo`: `ninguno | smtp | gmail | outlook | eml` (`gmail`/`outlook` = conector MCP de la organización; `smtp` y `eml` = capa de canales sin conector). `integraciones.okr`: `archivo | tability | perdoo`.
- Tability y Perdoo tienen servidor MCP oficial (`https://mcp.tability.app/mcp`, `https://mcp.perdoo.com`); la sincronización la propone `okr.py --propuesta-sync` (ver `pm-okr` guía §6).

## 6. Capa de canales (`scripts/envios.py`)
Una sola vía de salida para **cualquier** comunicación a interesados: comunicados personalizados, informes (highlight, fin de etapa), actas y recordatorios de acciones, convocatorias, decisiones de puerta y check-ins de OKR.

| Paso | Comando | Regla |
|---|---|---|
| Crear | `interesados.py plan-envio --tema … --audiencia …` o `envios.py nuevo --origen <archivo> --audiencia … --asunto … --proposito …` | un `.md` por destinatario (o grupo) con el perfil en el frontmatter; audiencia inválida = nada se crea |
| Ver | `envios.py estado <carpeta>` | marca los mensajes sin redactar |
| Aprobar | `envios.py aprobar <carpeta> --por "Gestor: Nombre"` | acto humano; rechaza borradores sin redactar o con destinatarios inexistentes; el hook pide confirmación a la persona (Claude Code muestra el pedido de permiso) |
| Simular | `envios.py enviar <carpeta> --modo …` | por defecto; muestra destinatario, asunto y comienzo del texto; avisa variables faltantes |
| Enviar | `… --confirmar` | solo mensajes aprobados del canal del modo; el hook pide confirmación a la persona; registra `envios.csv` (EN-###) y `diario.md`; código de salida 2 si hubo fallos |
| MCP | `envios.py preparar-mcp <carpeta>` → herramienta conectada → `envios.py registrar <carpeta> --mensaje … --modo mcp --referencia …` | vista previa y confirmación antes de usar la herramienta |
| Historial | `envios.py historial [--stakeholder ST-…]` | — |

Modos y variables de entorno (credenciales nunca en archivos, commits ni chat; ver `docs/INSTALACION.md` §0.7). Las URL de webhook deben ser `https://` (`http://` solo hacia 127.0.0.1 o localhost, para pruebas):

| Modo | Variables | Notas |
|---|---|---|
| `smtp` | `PM_SMTP_HOST`, `PM_SMTP_REMITENTE` (obligatorias); `PM_SMTP_PUERTO` (587), `PM_SMTP_TLS` (`starttls` defecto, `ssl`, `ninguno`), `PM_SMTP_USUARIO`, `PM_SMTP_CLAVE` | un correo por destinatario; referencia = Message-ID; `ninguno` solo hacia bucle local o sin credenciales (con aviso) |
| `eml` | — | archivos `.eml` (cabecera `X-Unsent: 1`) para abrir y enviar desde el cliente; luego `registrar --modo eml` |
| `slack-webhook` | `PM_SLACK_WEBHOOK_URL` | JSON `{"text": …}`; menciona `<@ID>` si `usuario_chat` es un id de Slack (U…/W…); publica en el canal del webhook |
| `teams-webhook` | `PM_TEAMS_WEBHOOK_URL` | flujo de Workflows de Teams ("When a Teams webhook request is received"): mensaje con tarjeta adaptable (`type: message`, `attachments` con `contentType: application/vnd.microsoft.card.adaptive`); límite 28 KB según la documentación de Microsoft (https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook) |

Integridad: los destinos se toman del maestro en el momento de enviar (si alguien cambió de correo, se usa el vigente); un destinatario que ya no existe bloquea la aprobación y el envío de ese mensaje; un reenvío solo alcanza a quienes no tienen fila `enviado`.
