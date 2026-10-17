---
tipo: plan-equipo
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de equipo · Team plan

> Borrador generado con asistencia de IA. Opcional según el método; un tablero Kanban puede sustituirlo. / AI-assisted draft; optional, a Kanban board may replace it.

**Paquete de trabajo / Work package:** W-{{codigo}} · {{nombre_paquete}}
*Código y nombre de la descripción de paquete de trabajo que este plan desarrolla.*

**Gestor de equipo / Team manager:** {{gestor_equipo}}
*Quien elabora el plan al aceptar el paquete y reporta puntos de control.*

**Acordado con / Agreed with:** {{gestor_proyecto}}
*Gestor de proyecto; el acuerdo queda en la descripción del paquete.*

**Productos a entregar / Products to deliver:** {{productos}}
*Códigos PBS con enlace a sus descripciones de producto; los criterios de calidad no se renegocian aquí.*

## 1. Alcance y dependencias / Scope and dependencies
{{alcance_dependencias}}
*Qué cubre el plan y de qué productos externos o de otros paquetes depende (del diagrama de flujo).*

## 2. Tareas y asignaciones / Tasks and assignments
| ID tarea / Task ID | Tarea / Task | Persona / Person | Esfuerzo (h) / Effort | Inicio / Start | Fin / End | Predecesora / Predecessor | Estado / Status |
|---|---|---|---|---|---|---|---|
| W-{{codigo}}.{{n}} | {{tarea}} | {{persona}} | {{esfuerzo}} | {{inicio}} | {{fin}} | {{pred}} | pendiente · en-curso · hecho |
*Nivel de detalle: tareas y personas por nombre; coherente con las fechas del cronograma de etapa.*

## 3. Cronograma del equipo / Team schedule
```mermaid
gantt
    dateFormat YYYY-MM-DD
    title Paquete W-{{codigo}}
    excludes weekends
    section {{persona_1}}
    {{tarea_1}} :{{id_1}}, {{inicio_1}}, {{fin_1}}
    section {{persona_2}}
    {{tarea_2}} :{{id_2}}, after {{id_1}}, {{duracion_2}}d
```
*Una sección por persona ayuda a ver sobreasignaciones; opcional si se usa Kanban.*

## 4. Actividades de calidad / Quality activities
| Producto / Product | Método / Method | Revisor / Reviewer | Fecha prevista / Planned date | Registro calidad / Quality register ID |
|---|---|---|---|---|
| P-{{p}} | {{metodo}} | {{revisor}} | {{fecha}} | Q-{{id}} |
*Tomadas de la descripción de producto; se registran en calidad.csv.*

## 5. Tolerancias del paquete / Work package tolerances
- Tiempo / Time: {{tol_tiempo}}
- Costo o esfuerzo / Cost or effort: {{tol_costo}}
- Alcance / Scope: {{tol_alcance}}
*Dentro de las tolerancias de la etapa; si se prevé excederlas, se plantea un issue al gestor de proyecto (no se absorbe).*

## 6. Puntos de control / Checkpoints
**Frecuencia / Frequency:** {{frecuencia}} · **Formato / Format:** {{formato}}
*Informe de punto de control (checkpoint report) o reunión diaria; lo fija la descripción del paquete.*

## 7. Riesgos y supuestos del paquete / Package risks and assumptions
{{riesgos_supuestos}}
*Referencias R-### y S-###; los nuevos se registran vía registro.py.*

## Lista de verificación / Checklist
- [ ] Todas las tareas trazan a un producto del paquete.
- [ ] Personas y fechas confirmadas con los asignados.
- [ ] Actividades de calidad incluidas y registradas.
- [ ] Tolerancias dentro de las de la etapa.
- [ ] Frecuencia de puntos de control acordada.
- [ ] Acordado entre gestor de equipo y gestor de proyecto (registrado en la descripción del paquete).
