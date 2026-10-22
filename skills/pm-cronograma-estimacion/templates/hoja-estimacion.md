---
tipo: hoja-estimacion
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Hoja de estimación de esfuerzo y duración · Effort and duration estimating worksheet

> Borrador generado con asistencia de IA; cada cifra cita su origen. / AI-assisted draft; every figure cites its source.

**Nivel de plan / Plan level:** {{nivel_plan}}
*Proyecto, etapa N o paquete de trabajo.*

**Unidades / Units:** esfuerzo en {{unidad_esfuerzo}}; duración en {{unidad_duracion}}
*Horas-persona o días-persona para esfuerzo; días laborables o semanas para duración; coherentes con el cronograma.*

**Calendario y supuestos globales / Calendar and global assumptions:**
- Jornada / Working day: {{horas_jornada}} h · Semana / Week: {{dias_semana}} días
- Disponibilidad por defecto / Default availability: {{pct_disponible}} (práctica habitual: 0,75)
- Convención del factor de desempeño / Performance factor convention: {{convencion_factor}} (1,0 recurso promedio; < 1 experto más rápido, aplicado como divisor)
*Declarar aquí lo que se asume para todas las filas; los supuestos específicos van en cada bloque y en supuestos.csv.*

## 1. Bloque paramétrico / Parametric block
| ID | Actividad / Activity | Esfuerzo (h) / Effort | Recursos / Resources | % disponible / Available | Factor / Factor | Duración (h) / Duration | Duración (días) / Days | Base / Basis |
|---|---|---|---|---|---|---|---|---|
| {{id}} | {{actividad}} | {{esfuerzo}} | {{cantidad}} | {{pct}} | {{factor}} | {{duracion_h}} | {{duracion_d}} | {{base}} |
*Duración = esfuerzo / (recursos × % disponible × factor); convertir a días con la jornada declarada. Ejemplo propio: 120 h, 2 personas, 0,75, factor 0,9 → 88,9 h ≈ 11 días.*

## 2. Bloque analógico / Analogous block
| ID | Actividad / Activity | Referencia histórica / Historical reference | Tamaño previo / Previous size | Duración previa / Previous duration | Tamaño actual / Current size | Multiplicador / Multiplier | Duración estimada / Estimated duration | Fuente / Source |
|---|---|---|---|---|---|---|---|---|
| {{id}} | {{actividad}} | {{referencia}} | {{tam_previo}} | {{dur_previa}} | {{tam_actual}} | {{multiplicador}} | {{duracion}} | {{fuente}} |
*Multiplicador = tamaño actual / tamaño previo (× ajuste por complejidad, declarado); duración = duración previa × multiplicador; citar el proyecto o la lección de la que sale el dato.*

## 3. Bloque de tres puntos / Three-point block
| ID | Actividad / Activity | O | M | P | Fórmula / Formula | tE | σ | Rango 68 % / 68 % range | Estimador / Estimator |
|---|---|---|---|---|---|---|---|---|---|
| {{id}} | {{actividad}} | {{o}} | {{m}} | {{p}} | beta-PERT · triangular · {{pesos}} | {{te}} | {{sigma}} | {{te}} ± {{sigma}} | {{estimador}} |
*Beta-PERT (práctica habitual, por defecto): tE = (O + 4M + P) / 6, σ = (P − O) / 6. Triangular (la que cita la Guía PMBOK): tE = (O + M + P) / 3, σ = √((O² + M² + P² − OM − OP − MP) / 18). La fórmula la declara el plan de gestión del cronograma; `cpm.py --estimacion` calcula tE, σ y la reserva desde las columnas optimista, mas_probable y pesimista de `actividades.csv`. Pesos alternativos (p. ej. (O + 3M + 2P) / 6) solo con justificación. Verificar P ≥ M ≥ O. Obligatorio para actividades del camino crítico.*

## 4. Bloque ascendente / Bottom-up block
| ID paquete / Package ID | Subtarea / Subtask | Esfuerzo (h) / Effort | Recurso / Resource | Duración / Duration | Estimador / Estimator |
|---|---|---|---|---|---|
| {{id}} | {{subtarea}} | {{esfuerzo}} | {{recurso}} | {{duracion}} | {{estimador}} |
| | **Total paquete / Package total** | {{total_esfuerzo}} | | {{total_duracion}} | |
*Sumar subtareas conocidas; vigilar optimismos u holguras ocultas; reflejar dependencias en el uso de recursos.*

## 5. Bloque ágil (puntos de historia) / Agile block (story points)
| ID historia / Story ID | Título / Title | Puntos / Points | Técnica / Technique | Iteración prevista / Planned iteration |
|---|---|---|---|---|
| PB-{{id}} | {{titulo}} | {{puntos}} | planning poker · tallas · comparación | S{{n}} |
*Tamaño relativo, no horas; velocidad histórica / Historical velocity: {{velocidad}} puntos por iteración; iteraciones restantes ≈ puntos restantes / velocidad.*

## 6. Consolidado por actividad / Consolidated per activity
| ID | Actividad / Activity | Paquete WBS / Work package | Producto PBS / Product | Método / Method | Esfuerzo / Effort | Duración / Duration | Reserva / Reserve | Confianza / Confidence | Supuestos / Assumptions |
|---|---|---|---|---|---|---|---|---|---|
| {{id}} | {{actividad}} | W-{{w}} | P-{{p}} | parametrico · analogico · pert · triangular · ascendente · juicio_experto · puntos | {{esfuerzo}} | {{duracion}} | {{reserva}} | alta · media · baja | S-{{id}} |
*Esta tabla alimenta actividades.csv (columna duracion) y la hoja de costeo (columna esfuerzo); la reserva se declara aparte del estimado base.*

## 7. Reserva de contingencia de cronograma / Schedule contingency reserve
- Actividades críticas con σ / Critical activities with σ: {{lista}}
- σ del camino / Path σ = √(Σ σ_i²) = {{sigma_camino}}
- Reserva propuesta / Proposed reserve: {{reserva}} (1σ ≈ 68 % · 2σ ≈ 95 %)
- Riesgos vinculados / Linked risks: R-{{ids}}
*Se añade al final del camino crítico o por etapa, visible en el Gantt; no se reparte escondida entre actividades.*

## 8. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Lecciones, históricos, personas consultadas; cifras [por confirmar].*

## Lista de verificación / Checklist
- [ ] Cada estimación indica bloque/método, cálculo y estimador.
- [ ] O/M/P provienen de quien conoce el trabajo; P ≥ M ≥ O.
- [ ] Convención del factor de desempeño declarada.
- [ ] Resultados convertidos a la unidad del cronograma.
- [ ] σ o rango acompaña a las actividades críticas.
- [ ] Reserva separada, justificada y vinculada a riesgos.
- [ ] Supuestos copiados a supuestos.csv.
