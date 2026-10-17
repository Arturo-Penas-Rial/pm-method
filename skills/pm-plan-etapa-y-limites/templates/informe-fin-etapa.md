---
tipo: informe-fin-etapa
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Informe de fin de etapa · End stage report

> Borrador generado con asistencia de IA; cada cifra cita su registro o reporte de origen. Lo confirma aseguramiento y lo revisa la junta. / AI-assisted draft; figures cite their source; confirmed by assurance, reviewed by the board.

**Etapa / Stage:** {{numero_etapa}} · {{nombre_etapa}} · **Período / Period:** {{inicio}} → {{fin_real}}
*Fechas reales de la etapa (1 = iniciación; 2…n = entrega); si es por excepción, indicarlo. Archivo: `03-control/reportes/{{fecha}}-informe-fin-etapa-{{numero_etapa}}.md`.*

**Gestor de proyecto / Project manager:** {{gestor}} · **Confirmado por aseguramiento / Confirmed by assurance:** {{aseguramiento}}
*Nombres de estado.json.roles.*

## 1. Resumen del gestor / Project manager's summary
{{resumen}}
*Tres a cinco líneas: qué se logró, qué no, situación general y recomendación (continuar, replanificar, detener).*

## 2. Revisión de desempeño / Performance review
### 2.1 Business case
{{revision_business_case}}
*Sigue siendo deseable, viable y alcanzable; cambios en costos, beneficios, riesgos agregados; referencia a la versión actualizada.*

### 2.2 Objetivos del proyecto / Project objectives
| Dimensión / Dimension | Meta / Target | Real o pronóstico / Actual or forecast | Tolerancia / Tolerance | Estado / Status |
|---|---|---|---|---|
| Tiempo · Costo · Alcance · Calidad · Beneficios · Riesgo · Sostenibilidad | {{meta}} | {{real}} | {{tol}} | verde · ámbar · rojo |
*Fuente: plan de proyecto actualizado, EVM (evm.py), registros.*

### 2.3 Objetivos de la etapa / Stage objectives
| Dimensión / Dimension | Meta / Target | Real / Actual | Variación / Variance | Fuente / Source |
|---|---|---|---|---|
| Tiempo / Time | {{meta}} | {{real}} | {{var}} | cronograma.md |
| Costo / Cost | {{meta}} | {{real}} | {{var}} | presupuesto.md · evm.py |
| Alcance / Scope | {{meta}} | {{real}} | {{var}} | registro de productos |
*Comparar contra la línea base de la etapa y sus tolerancias.*

### 2.4 Desempeño del equipo / Team performance
{{desempeno_equipo}}
*Capacidad, salud y bienestar, rotación; entrada a lecciones.*

### 2.5 Actividades de calidad / Quality activities
| Producto / Product | Método / Method | Planificada / Planned | Real / Actual | Resultado / Result |
|---|---|---|---|---|
| P-{{p}} | {{metodo}} | {{fecha_plan}} | {{fecha_real}} | aprobado · no aprobado · pendiente |
*Fuente: calidad.csv; cobertura: todo producto de la etapa tiene al menos una actividad.*

### 2.6 Estado de productos / Product status
| Código / Code | Producto / Product | Estado / Status | Aceptado por / Accepted by | Fecha / Date | Concesión / Concession |
|---|---|---|---|---|---|
| P-{{p}} | {{producto}} | aceptado · en-revision · pendiente · trasladado | {{aprobador}} | {{fecha}} | ninguna · I-{{id}} |
*Fuente: registro de productos; las concesiones por fuera de especificación se listan explícitamente.*

### 2.7 Entregas escalonadas / Phased handovers
{{entregas_escalonadas}}
*Productos ya entregados a operación durante la etapa y acciones de seguimiento que requieren.*

### 2.8 Lecciones / Lessons
| ID | Lección / Lesson | Recomendación / Recommendation | Incorporada en / Incorporated in |
|---|---|---|---|
| L-{{id}} | {{leccion}} | {{recomendacion}} | plan de etapa {{n+1}} · otros proyectos |
*Fuente: lecciones.csv y retrospectivas.*

## 3. Acciones de seguimiento recomendadas / Follow-on action recommendations
- {{accion}} — responsable / owner: {{responsable}} — fecha / date: {{fecha}}
*Para la organización, derivadas de entregas escalonadas o issues abiertos.*

## 4. Issues y riesgos clave / Key issues and risks
| ID | Tipo / Type | Descripción / Description | Estado / Status | Decisión o respuesta / Decision or response |
|---|---|---|---|---|
| I-{{id}} | solicitud-cambio · fuera-especificacion · problema-preocupacion · evento-externo · oportunidad-negocio | {{descripcion}} | {{estado}} | {{decision}} |
| R-{{id}} | amenaza · oportunidad | {{descripcion}} | {{estado}} | {{respuesta}} |
*Fuente: issues.csv (solo los cinco tipos canónicos), cambios.csv, riesgos.csv; riesgos altos (P×I ≥ 15) abiertos: {{riesgos_altos}}; exposición agregada (Σ EMV): {{exposicion}} vs tolerancia {{tol_riesgo}}.*

## 5. Pronóstico / Forecast
### 5.1 Siguiente etapa / Next stage
{{pronostico_etapa}}
*Resumen del plan de la siguiente etapa: productos, fechas, costo, tolerancias propuestas, personas y recursos requeridos.*

### 5.2 Proyecto / Project
| Dimensión / Dimension | Línea base / Baseline | Pronóstico / Forecast | Tolerancia / Tolerance | Dentro / Within |
|---|---|---|---|---|
| Fin / End date | {{base}} | {{pronostico}} | {{tol}} | sí · no |
| Costo (EAC) / Cost | {{base}} | {{eac}} ({{metodo_eac}}) | {{tol}} | sí · no |
| Beneficios / Benefits | {{base}} | {{pronostico}} | {{tol}} | sí · no |
*Si algún pronóstico está fuera de tolerancia, esto es una excepción y se dice expresamente.*

## 6. Solicitud a la junta / Request to the board

*Verificación de la próxima puerta (`autorizar-etapa` o `autorizar-cierre`): `puertas.py --proyecto <dir> verificar <puerta>` y estado de puertas anteriores y sus condiciones (`puertas.py estado --markdown`).*

{{bloque_puertas}}

- Aprobar el informe de fin de etapa / Approve this report.
- Aprobar el plan de la etapa {{n+1}} (o el plan de excepción) / Approve the next stage or exception plan: `{{ruta_plan}}`.
- Aprobar business case y plan de proyecto actualizados / Approve the updated business case and project plan.
- Confirmar concesiones otorgadas / Confirm concessions granted.
- Autorizar personas y recursos / Authorize people and resources: {{recursos}}.
- Puerta / Gate: `autorizar-etapa` · decide: {{rol_decide}}
*Solo pm-director registra la puerta (`estado.py puerta autorizar-etapa`, que avanza etapa_actual a n+1 y escribe decisiones.csv); luego registra las tolerancias de la nueva etapa (`estado.py tolerancia --nivel etapa ...`).*

## 7. Fuentes / Sources
{{fuentes}}
*Reportes, registros y cálculos usados; cifras [por confirmar] señaladas.*

## Lista de verificación / Checklist
- [ ] Todos los productos de la etapa con estado y aprobador; concesiones listadas.
- [ ] Actividades de calidad reales vs planificadas con fuente.
- [ ] Objetivos de etapa y proyecto comparados con tolerancias.
- [ ] Business case y plan de proyecto actualizados o confirmados.
- [ ] Lecciones registradas e incorporación indicada.
- [ ] Pronóstico contra tolerancias; excepciones declaradas expresamente.
- [ ] Solicitud a la junta completa y rol que decide nombrado.
- [ ] Confirmado por aseguramiento antes de enviarse.
