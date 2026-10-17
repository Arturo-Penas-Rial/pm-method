---
tipo: diagramas-mermaid
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Diagramas Mermaid del método · Mermaid diagram snippets

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Cada bloque es un esqueleto: reemplazar `{{placeholders}}`, añadir o quitar nodos según la fuente citada en cada sección, y conservar el pie con fuente y fecha de corte. Mermaid es el respaldo versionable aunque se use un motor externo.

**Proyecto / Project:** {{proyecto}} · **Fecha de corte / Cut-off:** {{fecha_corte}}
*Los nodos salen de registros y documentos; lo que falte se escribe `[por confirmar]`.*

## 1. Organigrama del equipo de gestión / Project management team org chart
*Fuente: estado.json.roles y 00-direccion/estructura-organizativa.md. Tres intereses en la junta, un solo ejecutivo, aseguramiento separado del gestor.*

```mermaid
flowchart TB
  NEG["Capa de negocio / Business layer<br/>{{negocio}}"]
  subgraph JUNTA["Junta del proyecto / Project board"]
    EJ["Ejecutivo / Executive<br/>{{ejecutivo}}"]
    US["Usuario sénior / Senior user<br/>{{usuario_senior}}"]
    PS["Proveedor sénior / Senior supplier<br/>{{proveedor_senior}}"]
  end
  ASEG["Aseguramiento / Project assurance<br/>{{aseguramiento}}"]
  AC["Autoridad de cambio / Change authority<br/>{{autoridad_cambio}}"]
  GP["Gestor del proyecto / Project manager<br/>{{gestor}}"]
  SOP["Soporte / Project support<br/>{{soporte}}"]
  GE1["Gestor de equipo / Team manager<br/>{{equipo_1}}"]
  GE2["Gestor de equipo / Team manager<br/>{{equipo_2}}"]
  NEG --> EJ
  EJ --> GP
  US -.-> GP
  PS -.-> GP
  JUNTA -.->|delega / delegates| ASEG
  JUNTA -.->|delega / delegates| AC
  GP --> GE1
  GP --> GE2
  GP --- SOP
```
*Línea continua: reporte. Punteada: delegación o acuerdo. Si una persona ocupa dos roles, repetir el nombre en ambos nodos y añadir nota.*

## 2. Mapa de stakeholders poder/interés / Power–interest stakeholder map
*Fuente: stakeholders.csv (poder, interes, actitud). Documento de circulación restringida; sin valoraciones personales. Escala 0–1 derivada de la escala del registro (declararla).*

```mermaid
quadrantChart
  title Mapa de interesados / Stakeholder map — {{proyecto}}
  x-axis Bajo interés / Low interest --> Alto interés / High interest
  y-axis Bajo poder / Low power --> Alto poder / High power
  quadrant-1 Gestionar de cerca / Manage closely
  quadrant-2 Mantener satisfecho / Keep satisfied
  quadrant-3 Monitorear / Monitor
  quadrant-4 Mantener informado / Keep informed
  %% Reemplazar los valores de ejemplo (0 a 1): [0.85, 0.90] = [{{interes_1}}, {{poder_1}}] · [0.30, 0.80] = [{{interes_2}}, {{poder_2}}] · [0.70, 0.25] = [{{interes_3}}, {{poder_3}}]
  "{{st_1}}": [0.85, 0.90]
  "{{st_2}}": [0.30, 0.80]
  "{{st_3}}": [0.70, 0.25]
```
*Estrategia por cuadrante en la matriz de comunicaciones. La actitud (a favor / neutral / en contra) se indica en una tabla aparte, no en el gráfico compartido.*

## 3. Estructura de desglose de productos / Product breakdown structure (PBS)
*Fuente: 02-planificacion/pbs-wbs.md. Solo productos (sustantivos), nunca actividades. Productos externos entre corchetes.*

```mermaid
flowchart TB
  P0["{{producto_proyecto}}"]
  P1["{{producto_1}}"]
  P2["{{producto_2}}"]
  P11["{{producto_1_1}}"]
  P12["{{producto_1_2}}"]
  PX[/"[Externo / External] {{producto_externo}}"/]
  P0 --> P1
  P0 --> P2
  P1 --> P11
  P1 --> P12
  P0 --> PX
```
*Para una WBS derivada, usar el mismo árbol con paquetes de trabajo como hojas y referencia al id de PBS.*

## 4. Diagrama de flujo de productos / Product flow diagram
*Fuente: PBS y descripciones de producto del plan de etapa. Flechas = dependencia "necesario para". Externos como entradas.*

```mermaid
flowchart LR
  EXT[/"[Externo] {{producto_externo}}"/]
  A["{{producto_a}}"]
  B["{{producto_b}}"]
  C["{{producto_c}}"]
  FIN(("{{producto_final}}"))
  EXT --> A
  A --> B
  A --> C
  B --> FIN
  C --> FIN
```
*Si el diagrama supera ~40 nodos, dividir por etapa de gestión.*

## 5. Gantt del plan de etapa / Stage plan Gantt
*Fuente: cpm.py --mermaid o el cronograma del plan. Marcar las actividades críticas con `crit`; hitos con `milestone`.*

```mermaid
gantt
  title {{proyecto}} — Etapa {{etapa}} / Stage {{etapa}}
  dateFormat YYYY-MM-DD
  axisFormat %d-%m
  section {{seccion_1}}
    %% Reemplazar los valores de ejemplo: 2026-01-05 y 10d = {{inicio_1}} y {{duracion_1}}d · 5d, 8d = {{duracion_2}}d, {{duracion_3}}d · 2026-01-23 = {{fecha_hito_1}}
    {{actividad_1}} :crit, a1, 2026-01-05, 10d
    {{actividad_2}} :a2, after a1, 5d
  section {{seccion_2}}
    {{actividad_3}} :crit, a3, after a1, 8d
    Hito / Milestone {{hito_1}} :milestone, m1, 2026-01-23, 0d
```
*Supuestos: días laborables, sin nivelación de recursos (cpm.py). Para SS/FF/SF o calendarios, MSPDI (`cpm.py --mspdi`) completado en MS Project o ProjectLibre, desde pm-cronograma-estimacion.*

## 6. Roadmap por etapas con puertas / Stage roadmap with gates
*Fuente: plan de proyecto (etapas) y estado.json.puertas. Las puertas aparecen siempre entre etapas.*

```mermaid
timeline
  title Roadmap — {{proyecto}}
  section Pre-proyecto / Pre-project
    {{fecha_su}} : Starting up (SU) : Puerta: autorizar-inicio ({{estado_puerta_inicio}})
  section Inicio / Initiation
    {{fecha_ip}} : Initiating (IP) · PID : Puerta: autorizar-proyecto + autorizar-etapa ({{estado_puerta_proyecto}})
  section Etapa 1 / Stage 1 — {{nombre_etapa_1}}
    {{fecha_e1}} : {{productos_etapa_1}} : Puerta: autorizar-etapa 2 ({{estado_puerta_e2}})
  section Etapa 2 / Stage 2 — {{nombre_etapa_2}}
    {{fecha_e2}} : {{productos_etapa_2}} : Puerta: autorizar-cierre ({{estado_puerta_cierre}})
  section Cierre / Closure
    {{fecha_cp}} : Closing (CP) : Notificación de cierre / Closure notice
```
*Alternativa con fechas exactas: usar el Gantt de la sección 5 con una sección por etapa y las puertas como hitos.*

## 7. Flujo de excepciones por nivel / Exception flow by level
*Fuente: tolerancias en estado.json y 00-direccion/tolerancias-y-autoridad.md. Quién decide en cada nivel.*

```mermaid
flowchart TD
  D([Pronóstico de desviación / Forecast deviation]) --> Q1{"¿Dentro de tolerancia del paquete?<br/>Within work package tolerance?<br/>{{tol_wp}}"}
  Q1 -- Sí / Yes --> T1[Gestor de equipo corrige<br/>Team manager corrects<br/>→ checkpoint]
  Q1 -- No --> I1[Issue al gestor del proyecto<br/>Issue to project manager]
  I1 --> Q2{"¿Dentro de tolerancia de etapa?<br/>Within stage tolerance?<br/>{{tol_etapa}}"}
  Q2 -- Sí / Yes --> T2[Gestor corrige<br/>PM corrects<br/>→ highlight report]
  Q2 -- No --> E1[Informe de excepción a la junta<br/>Exception report to board]
  E1 --> Q3{"¿Dentro de tolerancia de proyecto?<br/>Within project tolerance?<br/>{{tol_proyecto}}"}
  Q3 -- Sí / Yes --> J["Junta decide / Board decides:<br/>reasignar tolerancias · repriorizar · plan de excepción · esperar · cierre prematuro<br/>{{ejecutivo}}"]
  Q3 -- No --> N["Capa de negocio decide<br/>Business layer decides<br/>{{negocio}}"]
  N --> J
  J -->|plan de excepción / exception plan| SB[Límite de etapa · plan de excepción<br/>Stage boundary · exception plan] --> P([Puerta autorizar-plan-excepcion])
  T1 --> R([Registrar / Record])
  T2 --> R
  P --> R
```
*Para una versión swimlane por nivel (equipo · gestor · junta · negocio), usar diagram-design con estos mismos nodos.*

## 8. Línea de hitos simple / Simple milestone line
*Fuente: plan de etapa. Útil para el comunicado al cliente.*

```mermaid
timeline
  title Hitos / Milestones — {{proyecto}}
  {{fecha_h1}} : {{hito_1}} ({{estado_h1}})
  {{fecha_h2}} : {{hito_2}} ({{estado_h2}})
  {{fecha_h3}} : {{hito_3}} ({{estado_h3}})
```

## Pie obligatorio para cada diagrama / Mandatory footer for each diagram
`Fuente / Source: {{fuente}} · Corte / Cut-off: {{fecha_corte}} · Estado / Status: borrador · Generado con asistencia de IA`

## Lista de verificación / Checklist
- [ ] Cada diagrama cita su fuente y fecha de corte en el pie.
- [ ] Organigrama: tres intereses, un ejecutivo, aseguramiento separado del gestor.
- [ ] Mapa de stakeholders: escala declarada, sin valoraciones personales, circulación restringida.
- [ ] PBS sin actividades; externos marcados; flujo de productos con externos como entradas.
- [ ] Gantt con críticas marcadas y supuestos declarados; roadmap con puertas entre etapas.
- [ ] Flujo de excepciones con tolerancias y decisor por nivel.
- [ ] Ningún nodo inventado; faltantes como `[por confirmar]`.
- [ ] Menos de ~40 nodos por diagrama; dividir si hace falta.
