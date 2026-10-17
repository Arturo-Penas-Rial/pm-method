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
| okr | objetivos y KR | `tability` | leer objetivos y progreso |

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
CSV con cabecera y columnas normalizadas; primera línea comentada no permitida (para que lo lean los scripts). Nombre: `03-control/fuentes/<sistema>-AAAA-MM-DD.csv`. Columnas mínimas para tracker: `clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url`. Para mensajes o páginas: Markdown con front matter `fuente`, `fecha`, `consulta`.

## 4. Mensajes tipo (borradores, se envían solo con confirmación)
- **Highlight breve (chat)**: estado general en una línea; semáforos tiempo/costo/alcance; 3 logros; 3 riesgos/issues con id; decisiones pendientes de la junta; enlace al informe.
- **Recordatorio de acciones vencidas**: por responsable, lista de A-### con fecha; tono neutro; sin juicios sobre personas.
- **Convocatoria a puerta**: decisión requerida, documentos del paquete, fecha límite.
