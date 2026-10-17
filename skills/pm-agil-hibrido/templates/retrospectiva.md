---
tipo: retrospectiva
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Retrospectiva de iteración · Iteration retrospective

> Borrador generado con asistencia de IA a partir de las notas de la sesión; ambiente sin culpas. / AI-assisted draft from session notes; blameless.

**Iteración / Iteration:** S{{iteracion}} · etapa {{numero_etapa}} · **Fecha / Date:** {{fecha}}
*Una por iteración, sobre la forma de trabajar del equipo. El taller de lecciones de la etapa (límite de etapa) no usa esta plantilla: lo conduce pm-lecciones-aprendidas con retrospectiva-etapa.md. Archivo: 03-control/reportes/{{fecha}}-retrospectiva-S{{iteracion}}.md.*

**Facilitador / Facilitator:** {{facilitador}} · **Participantes / Participants:** {{participantes}}
*Facilitador neutral cuando sea posible; si facilita el gestor o el scrum master, anotarlo como posible sesgo. Participan el equipo y el PO.*

**Caja de tiempo / Timebox:** {{duracion}} · **Formato / Format:** estrella de mar · 4 L · bien/mejorar/acciones
*Rotar formatos para evitar rutina.*

## 1. Métricas de la iteración / Iteration metrics
| Métrica / Metric | Valor / Value | Fuente / Source |
|---|---|---|
| Comprometido / Committed | {{comprometido}} puntos | backlog.csv |
| Terminado (DoD) / Done | {{terminado}} puntos | backlog.csv |
| Velocidad / Velocity | {{velocidad}} | release-plan.md |
| Impedimentos / Impediments | {{impedimentos}} | diario.md · issues.csv |
| Defectos abiertos / Open defects | {{defectos}} | backlog.csv (tipo defecto) |
*Datos, no opiniones; sirven para contextualizar la conversación.*

## 2. Seguimiento de acciones anteriores / Previous actions follow-up
| Acción / Action | Responsable / Owner | Estado / Status | Comentario / Comment |
|---|---|---|---|
| {{accion_previa}} | {{responsable}} | hecha · en curso · descartada | {{comentario}} |
*Revisar antes de generar acciones nuevas.*

## 3. Ítems por categoría / Items by category
**Estrella de mar / Starfish** (o adaptar al formato elegido)
| Empezar / Start | Dejar de hacer / Stop | Mantener / Keep | Más / More | Menos / Less |
|---|---|---|---|---|
| {{empezar}} | {{dejar}} | {{mantener}} | {{mas}} | {{menos}} |
*Alternativa 4 L: Gustó / Liked, Aprendió / Learned, Faltó / Lacked, Anheló / Longed for. Alternativa mínima: bien / mejorar / acciones.*

## 4. Acciones de mejora / Improvement actions
| Acción / Action | Responsable / Owner | Fecha / Due date | Registro / Record |
|---|---|---|---|
| {{accion}} | {{responsable}} | {{fecha}} | PB-{{id}} (tipo accion_retro) · A-{{id}} (acciones.csv) |
*Una a tres acciones concretas. Las del equipo entran al backlog (accion_retro) para competir por capacidad; los compromisos de alguien fuera del equipo van a acciones.csv (`registro.py agregar acciones`).*

## 5. Lecciones trasladables / Transferable lessons
| Lección / Lesson | Alcance / Scope | Registro / Register |
|---|---|---|
| {{leccion}} | equipo · proyecto · organización | L-{{id}} (lecciones.csv, estado registrada) |
*Lo que sirve más allá del equipo va al registro de lecciones (con confirmación); el taller de lecciones de etapa las consolida.*

## 6. Señales para el método / Signals for the method
- Riesgos nuevos / New risks: R-{{ids}}
- Issues que requieren al gestor de proyecto / Issues needing the project manager: I-{{ids}} (tipo problema-preocupacion u otro de los cinco canónicos)
- Indicios de excepción (velocidad vs must) / Exception signals: {{senal_excepcion}}
*La retrospectiva mira la forma de trabajar; lo que afecta tolerancias se escala por la vía del método.*

## Lista de verificación / Checklist
- [ ] Todo el equipo participó; ambiente sin culpas.
- [ ] Acciones de la retrospectiva anterior revisadas.
- [ ] 1–3 acciones con dueño y fecha, cargadas al backlog o a acciones.csv.
- [ ] Lecciones trasladables registradas en lecciones.csv.
- [ ] Riesgos e issues derivados registrados por su vía.
- [ ] Duró lo previsto.
