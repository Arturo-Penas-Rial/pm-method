---
name: pm-integraciones
description: "Integración con las herramientas MCP conectadas (Jira, Confluence, Slack, Teams, correo, calendario). Usar: sincronizar Jira, publicar en Slack/Teams, traer issues, sync. No: BMAD→pm-bmad-puente; transcripciones→pm-reuniones."
version: 2.0.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-control
    procesos_prince2: [CS, MP, SB, DP]
    practicas_prince2: [progress, issues, organizing]
    tecnicas_pmbok: [gestión de la información del proyecto, comunicaciones]
    artefactos: [instantáneas en 03-control/fuentes, estado.json.integraciones]
    idiomas: [es, en]
---

# Integraciones con herramientas · Tool integrations

## Cuándo usar / When to use
- Traer datos de un tracker (Jira, Linear, GitHub, Azure DevOps), de documentación (Confluence, Notion, SharePoint) o de calendario, para informes, registros o el tablero.
- Publicar un resumen (highlight, acta, recordatorio de acciones) en Slack, Teams o correo, o crear/actualizar tickets desde el backlog o las acciones.
- EN: pull tracker/docs data into the project folder; push summaries or tickets, always after confirmation.
- EN: decide which connected MCP tool fulfils each capability.

## Idioma
Responder en el idioma del usuario; los mensajes publicados usan el idioma de la audiencia (matriz de comunicaciones).

## Conocimiento
- `SPEC.md` §1.12 (reglas de integración) y §1.11 (decisiones humanas desde subagentes).
- `references/guia.md` (este skill): tabla de capacidades, detección de herramientas, mapeo de campos Jira↔backlog/acciones, formatos de instantánea, ejemplos de mensajes.

## Entradas requeridas
- `estado.json` (sección `integraciones`). Si una capacidad está en `ninguno`, ofrecer configurarla.
- Herramientas MCP conectadas en la sesión. El paquete no las trae ni las configura: el usuario las conecta (en Claude Code `claude mcp add …` o la gestión de conectores de la app; en Hermes, su configuración MCP), con las credenciales en el propio cliente.
- Para escribir: destino exacto (proyecto Jira, canal, lista de correo) confirmado por el usuario.

## Procedimiento
1. **Detectar capacidades**: revisar qué herramientas hay disponibles en la sesión (nombres `mcp__<servidor>__<herramienta>`, o las listadas por el cliente) y clasificarlas con la tabla de `references/guia.md` §1 (tracker, docs, chat, correo, calendario, reuniones, okr). No suponer nombres de herramientas: usar las que efectivamente existen y leer su descripción.
2. **Registrar** qué sistema cumple cada capacidad: `python3 <pm-estado-proyecto>/scripts/estado.py --proyecto <dir> integracion tracker=jira chat=teams`.
3. **Leer (sin confirmación)**: consultar lo necesario (p. ej. issues de un proyecto o sprint, páginas, eventos) y guardar una **instantánea fechada** en `03-control/fuentes/<sistema>-AAAA-MM-DD.csv|md|json` con columnas normalizadas (§3 de la guía). Citarla en informes como fuente.
4. **Conciliar**: comparar la instantánea con los registros de gobierno (backlog, acciones, issues). Las diferencias se proponen como cambios a los registros (`registro.py`), nunca se aplican en silencio; los cambios de alcance van a `pm-issues-cambios`.
5. **Escribir (con confirmación)**: preparar la vista previa exacta (destino, contenido, campos). En el hilo principal, pedir confirmación explícita; en un subagente, devolverla como "decisión humana requerida". Solo después ejecutar la herramienta y registrar el resultado (id externo) en `notas` del registro afectado o en `diario.md`.
6. **Errores**: si una herramienta falla dos veces o no tiene la operación, informar y ofrecer la alternativa local (CSV, Markdown, borrador de mensaje para copiar).

## Reglas del método
1. Fuente de verdad del gobierno = carpeta del proyecto; los sistemas externos son fuentes de datos o canales.
2. Escritura externa solo con vista previa y confirmación explícita, una vez por lote; nunca credenciales en archivos del proyecto.
3. No presuponer conectores: trabajar con los MCP presentes; si falta uno, sugerir conectarlo sin bloquear el trabajo.
4. [PRINCE2] Los datos de trackers alimentan checkpoints y highlights; las decisiones siguen las tolerancias y la autoridad PRINCE2, no el flujo del tracker.
5. Instantáneas fechadas e inmutables; una nueva lectura crea un archivo nuevo.
6. Privacidad: no exportar datos personales o confidenciales a canales no autorizados (enfoque de datos y tecnología digital).
7. Teams: el servidor MCP "Teams (preview)" de Microsoft está marcado como legado; preferir el que la organización tenga aprobado (p. ej. Work IQ) — verificar en la documentación vigente.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | estado.json |
|---|---|---|---|
| Instantánea de sistema externo | formato de `references/guia.md` §3 | `03-control/fuentes/<sistema>-AAAA-MM-DD.<ext>` | — |
| Mapa de integraciones | — | `estado.json.integraciones` | `integraciones` |

## Calidad
- [ ] Cada capacidad usada figura en `estado.json.integraciones`.
- [ ] Toda cifra externa cita su instantánea.
- [ ] Toda escritura externa tuvo vista previa y confirmación registrada.

## Escalamiento y excepciones
- Diferencias de alcance entre tracker y backlog → `pm-issues-cambios`.
- Conflicto entre lo que muestra el tracker y lo aprobado por la junta → informar a `pm-director`.

## Ejemplos de invocación
- "Traé los issues abiertos del sprint de Jira y actualizá el tablero."
- "Publicá el highlight de esta semana en el canal del proyecto en Teams."
- EN: "Create Jira tickets for the open actions assigned to the vendor."
- No activa: "Sincronizá con BMAD" → `pm-bmad-puente`; "procesá la grabación del comité" → `pm-reuniones`.

## EN summary
Tool-agnostic integration layer: detects which MCP tools are connected, maps them to capabilities (tracker, docs, chat, mail, calendar, meetings, OKR), stores dated snapshots in the project folder, reconciles them with governance registers, and performs external writes only after an explicit previewed confirmation. No connectors are predefined.
