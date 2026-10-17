---
tipo: cronograma
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Cronograma · Schedule

> Borrador generado con asistencia de IA. Cálculo CPM: {{herramienta}} (cpm.py, cpm.py --mspdi o utf8proj). Export MS Project / MS Project export: {{ruta_mspdi}}. / AI-assisted draft; CPM computed with the tool named here.

**Nivel de plan / Plan level:** {{nivel_plan}}
*Proyecto, etapa N (1 = iniciación; 2…n entrega), excepción o equipo; los hitos de etapa coinciden con el plan de proyecto. En ágil, iteraciones y releases en lugar de actividades de la WBS.*

**Fecha de inicio / Start date:** {{fecha_inicio}} · **Fin previsto / Forecast end:** {{fecha_fin}} · **Duración / Duration:** {{duracion_total}} días laborables
*Salida del cálculo; comparar con la fecha objetivo y con la tolerancia de tiempo.*

**Calendario / Calendar:** {{calendario}}
*Días laborables, feriados excluidos, jornada; supuestos declarados en la hoja de estimación.*

**Tolerancia de tiempo del nivel / Time tolerance:** {{tolerancia_tiempo}} · **Holgura frente a la fecha objetivo / Slack vs target:** {{holgura_objetivo}}
*De estado.json.tolerancias.proyecto.tiempo o .etapa.tiempo y de la restricción del mandato; holgura negativa = evaluar compresión (§6) y, si no entra, decisión de la junta antes de aprobar.*

## 1. Diagrama de Gantt / Gantt chart
```mermaid
gantt
    dateFormat YYYY-MM-DD
    title {{titulo_gantt}}
    excludes weekends
    section {{paquete_1}}
    {{actividad_1}} :crit, {{id_1}}, {{inicio_1}}, {{fin_1}}
    {{actividad_2}} :{{id_2}}, after {{id_1}}, {{duracion_2}}d
    section Hitos / Milestones
    {{hito_1}} :milestone, {{id_hito}}, {{fecha_hito}}, 0d
    section Reserva / Reserve
    Reserva de contingencia :{{id_reserva}}, {{inicio_reserva}}, {{dias_reserva}}d
```
*Generado por cpm.py --mermaid o escrito a mano con el mismo formato; las actividades críticas llevan "crit"; los hitos duración 0; la reserva visible al final del camino. Con diagram-design/archify configurado, pm-visuales puede producir la versión gráfica.*

## 2. Tabla CPM / CPM table
| ID | Actividad / Activity | Paquete / Package | Duración / Duration | Predecesoras / Predecessors | ES | EF | LS | LF | Holgura total / Total float | Holgura libre / Free float | Crítica / Critical |
|---|---|---|---|---|---|---|---|---|---|---|---|
| {{id}} | {{actividad}} | W-{{w}} | {{dur}} | {{preds}} | {{es}} | {{ef}} | {{ls}} | {{lf}} | {{ht}} | {{hl}} | sí · no |
*ES = máx(EF predecesoras + lag); EF = ES + duración; LF = mín(LS sucesoras − lag); LS = LF − duración; HT = LS − ES; HL = mín(ES sucesoras − lag) − EF. Convención de inicio en 0 (cpm.py, que imprime HT y HL); duraciones decimales redondeadas hacia arriba; duración 0 = hito. Si se usa utf8proj, declararlo.*

**Camino crítico / Critical path:** {{camino_critico}}
*Secuencia con holgura total 0; listar también los caminos casi críticos (holgura ≤ {{umbral_casi_critico}} días).*

## 3. Dependencias y relaciones / Dependencies and relationships
| De / From | A / To | Relación / Relationship | Adelanto o retraso / Lead or lag | Tipo / Type | Justificación / Rationale |
|---|---|---|---|---|---|
| {{a}} | {{b}} | FS · SS · FF · SF | {{lag}} | obligatoria · discrecional · externa · interna | {{justificacion}} |
*El CSV de cpm.py solo admite FS con lag (`WP-1.1+2`) o adelanto (`WP-1.1-1`); SS/FF/SF, calendarios y nivelación requieren utf8proj. Las discrecionales se documentan; las externas generan riesgo.*

## 4. Carga por recurso / Resource load
| Recurso / Resource | Días asignados / Assigned days | Capacidad / Capacity | Sobreasignación / Over-allocation | Acción / Action |
|---|---|---|---|---|
| {{recurso}} | {{dias}} | {{capacidad}} | {{exceso}} | alisado · nivelación · recurso adicional · ninguna |
*Salida de cpm.py (carga_recursos); el alisado usa holgura y no mueve el fin; la nivelación puede mover el fin y cambiar el camino crítico.*

## 5. Hitos / Milestones
| Hito / Milestone | Tipo / Type | Fecha base / Baseline date | Producto o puerta / Product or gate | Responsable / Owner |
|---|---|---|---|---|
| {{hito}} | producto · puerta · compra · pago · externo | {{fecha}} | P-{{p}} / autorizar-etapa | {{responsable}} |
*Incluir descripción aprobada y producto aceptado por producto mayor, fin de etapa y hitos de compras alineados con las etapas.*

## 6. Reservas y compresión / Reserves and compression
- Reserva de contingencia / Contingency reserve: {{reserva}} (de la hoja de estimación, σ del camino = {{sigma}})
- Restricción de fecha del mandato / Mandate date constraint: {{restriccion_fecha}} · Brecha / Gap: {{brecha_dias}} días

| Opción / Option | Días ganados / Days gained | Costo o riesgo añadido / Added cost or risk | Decide / Decides |
|---|---|---|---|
| Ejecución rápida (fast-tracking) | {{dias_ft}} | riesgo de retrabajo R-{{id}} | gestor |
| Intensificación (crashing) | {{dias_crash}} | {{costo_crash}} → pm-costos-presupuesto | gestor · junta si excede tolerancia de costo |
| Reducción de alcance (MoSCoW Could/Should) | {{dias_alcance}} | beneficios diferidos {{efecto}} | product owner (dentro de tolerancia) · junta |
| Recursos (reasignar, subcontratar) | {{dias_recursos}} | {{costo_recursos}} | gestor · proveedor sénior |
*Solo sobre actividades críticas, recalculando el camino tras cada opción. Si ninguna combinación entra en la tolerancia: el plan no se aprueba; pm-director lleva la decisión a la junta.*

## 7. Supuestos, riesgos y pendientes / Assumptions, risks and open points
- Supuestos / Assumptions: S-{{ids}}
- Riesgos de cronograma / Schedule risks: R-{{ids}}
- Pendientes / Open points: {{pendientes}} (`[por confirmar]` / `[to be confirmed]`)
*Dependencias externas sin fecha comprometida y recursos no confirmados van aquí y al registro correspondiente.*

## Lista de verificación / Checklist
- [ ] Todos los paquetes de la etapa (incluido gestión) están en el cronograma.
- [ ] Red sin ciclos; actividades intermedias con predecesora y sucesora.
- [ ] Camino crítico y holguras visibles; casi críticos señalados.
- [ ] Carga por recurso revisada y acciones documentadas.
- [ ] Reserva separada y visible; comparación con la tolerancia de tiempo hecha.
- [ ] Hitos de producto, de puerta y de compras presentes.
- [ ] Gantt Mermaid renderiza; fechas ISO.
- [ ] Fin comparado con la restricción del mandato y la tolerancia; opciones de §6 evaluadas si no entra.
- [ ] Aprobación pendiente con el plan (autorizar-proyecto / autorizar-etapa, registrada por pm-director).
