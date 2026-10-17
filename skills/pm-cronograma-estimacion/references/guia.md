# Guía de estimación y cronograma · Estimation and scheduling guide

## 1. Elección de técnica de estimación
| Situación | Técnica | Qué declarar |
|---|---|---|
| Hay un proyecto o actividad comparable con datos reales | Análoga (comparativa) | Referencia, tamaño previo y actual, multiplicador y ajustes |
| Hay una relación cantidad × productividad conocida | Paramétrica | Variable, unidad, productividad y rango válido de los datos |
| Trabajo nuevo o incierto, o en el camino crítico | Tres puntos (PERT o triangular) | O, M, P, fórmula, σ y quién dio cada valor |
| Detalle conocido y se necesita exactitud | Ascendente | Subtareas, esfuerzo por subtarea, estimador |
| Varios expertos con opiniones distintas | Delphi de banda ancha / juicio experto | Rondas, participantes, consenso |
| Enfoque ágil, tamaño relativo | Puntos de historia + planning poker | Escala, velocidad histórica, sin conversión a horas |
| Horizonte lejano | Planificación gradual (paquetes de planificación) | Qué se detalla ahora y cuándo el resto |

Quien ejecutará el trabajo valida o da la estimación; cada fila de `hoja-estimacion.md` lleva método, rango, confianza y estimador.

## 2. Fórmulas de referencia
```
Duración (paramétrica)   = Esfuerzo / (Recursos × % disponible × Factor de desempeño)
Duración (análoga)       = Duración previa × (Tamaño actual / Tamaño previo) × Ajuste
PERT                     tE = (O + 4M + P) / 6        σ = (P − O) / 6
Triangular               tE = (O + M + P) / 3
Rango de confianza       tE ± 1σ ≈ 68 %     tE ± 2σ ≈ 95 %
σ de un camino           σ_camino = √(Σ σ_i²)  (actividades del camino)
CPM (inicio en 0)        ES = máx(EF_pred + lag); EF = ES + dur; LF = mín(LS_suc − lag); LS = LF − dur
Holgura total            HT = LS − ES = LF − EF        Holgura libre  HL = mín(ES_suc − lag) − EF
Velocidad (ágil)         iteraciones ≈ ⌈puntos (Must+Should) / velocidad⌉; duración = iteraciones × cadencia
```
Verificar `P ≥ M ≥ O`; pesos alternativos solo con justificación escrita. Conversión `días = horas / 8` solo con recurso a tiempo completo; si no, fórmula paramétrica.

## 3. `actividades.csv` y `cpm.py`
Cabecera: `id,nombre,duracion,predecesoras,recurso[,wbs]` = activity id, name, duration, predecessors, resource, WBS code.
- `id`: admite guiones (`WP-1.1`, `A-01`); si el texto completo coincide con un id no se interpreta como lag.
- `duracion`: días laborables; decimales se redondean hacia arriba (2,3 → 3); `0` = hito.
- `predecesoras`: separadas por `;`; solo fin-a-comienzo; retraso/adelanto al final `id+N` / `id-N` (`WP-1.1+2`).
- `wbs` (opcional): código de `02-planificacion/wbs.csv` (1.2.3). Ordena las tareas por código y genera tareas resumen en el MSPDI; con `--wbs wbs.csv` las tareas resumen toman el nombre del paquete o producto.
- Toda actividad, salvo la primera y la última, tiene predecesora y sucesora; la red no admite ciclos.

Comando: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/cpm.py 02-planificacion/actividades.csv --inicio AAAA-MM-DD --mermaid 02-planificacion/gantt.md [--json] [--mspdi 02-planificacion/cronograma.xml --titulo "<Proyecto>" --wbs 02-planificacion/wbs.csv]`.
Salida: duración total y fin previsto, camino crítico, tabla ES/EF/LS/LF/HT/HL (`*` = crítica), carga por recurso en días; Gantt Mermaid con `crit` y `milestone`, `excludes weekends`.

## 4. Export a MS Project (MSPDI)
- `--mspdi <ruta.xml>` escribe MS Project XML (formato MSPDI): calendario estándar lunes–viernes de 8 h (08–12, 13–17), tareas con `WBS`/`OutlineNumber`/`OutlineLevel`, tareas resumen por código WBS, hitos, marca de crítica y holgura total, vínculos fin-a-comienzo con lag, recursos (uno por nombre de `recurso`) y asignaciones al 100 %.
- Se importa en MS Project (Archivo → Abrir → XML) y en herramientas que leen MSPDI (p. ej. ProjectLibre). El formato se validó leyendo el archivo con la biblioteca MPXJ.
- Limitaciones: sin feriados ni calendarios por recurso, una sola persona por actividad, solo FS. Tras importar, la herramienta destino recalcula con su propio calendario: revisar que el fin coincida con el de `cpm.py` y explicar diferencias (feriados agregados allí, por ejemplo).
- **`.mpp` binario**: no lo genera el paquete. Si alguien lo exige, MPXJ (Java, externo, opcional) puede convertir el XML; no es requisito del método y queda a cargo de quien tenga esa herramienta. El XML ya abre en MS Project.
- Registro: `estado.py integracion cronograma=mspdi` cuando el equipo trabaja con el XML; la fuente de verdad sigue siendo `actividades.csv` (el XML se regenera, no se edita a mano en paralelo). Las copias para enviar van en `exportados/`.

## 5. Herramientas externas opcionales
Exportar el MSPDI (`cpm.py --mspdi … --wbs …`) y completar la red en MS Project o ProjectLibre cuando haga falta: relaciones SS/FF/SF, calendarios por recurso o feriados, nivelación automática, varios recursos por actividad con dedicación parcial. Registrar el comando y guardar el archivo en `02-planificacion/`. Ninguna herramienta externa es obligatoria.

## 6. Compresión cuando el fin no entra
Evaluar y cuantificar, en este orden, recalculando el camino crítico tras cada opción (puede cambiar):
1. **Ejecución rápida**: solapar críticas con dependencia discrecional; sube el riesgo de retrabajo → riesgo registrado.
2. **Intensificación**: más recursos u horas en críticas de menor `costo de intensificar / días ahorrados`; costo a `pm-costos-presupuesto`.
3. **Reducción de alcance por MoSCoW**: diferir *Could*, luego *Should*; un *Must* solo con decisión de la junta. En ágil se empieza por aquí.
4. **Recursos**: reasignar, subcontratar (con `pm-adquisiciones`) o quitar cuellos de botella.
Si ninguna combinación entra en la tolerancia, el plan no se presenta como aprobable: decisión de la junta vía `pm-director` (informe de excepción con la plantilla de `pm-issues-cambios` si hay línea base; `decision-ad-hoc` en la iniciación).

## 7. Reservas, hitos y plan de equipo
- **Reserva de contingencia**: σ del camino crítico con PERT; proponer ≈1σ (68 %) o 2σ (95 %) según apetito de riesgo; aparte, visible y vinculada a riesgos. La reserva de gestión de tiempo, si existe, la maneja la junta como tolerancia.
- **Hitos**: de producto (descripción aprobada, producto aceptado), de puerta (fin de cada etapa: etapa 1 = iniciación, entrega 2…n) y de compras/pagos. Ningún paquete cruza un límite de etapa sin justificación.
- **Plan de equipo** (opcional, lo crea el gestor de equipo): tareas, asignaciones, fechas, puntos de control y tolerancias del paquete; un tablero Kanban o el backlog de iteración puede sustituirlo.

## 8. Versión mínima vs. completa
| Elemento | Mínima | Completa |
|---|---|---|
| Actividades | Paquetes de la WBS como actividades | Actividades por paquete con columna `wbs` |
| Estimación | Análoga o juicio experto; PERT solo en lo crítico | Hoja completa con bloques y σ por actividad |
| Red y CPM | Lista de hitos con fechas (ágil: iteraciones y releases) | `actividades.csv` + `cpm.py`, HT/HL y casi críticos; MSPDI si se pide |
| Recursos | Carga revisada a ojo | Nivelación o alisado documentados |
| Reservas | Dentro de la tolerancia de tiempo | Reserva calculada con σ del camino, visible en el Gantt |
| Plan de equipo | Omitido o Kanban | `plan-equipo.md` por paquete relevante |

## 9. Reglas complementarias
1. [PRINCE2] El cronograma de etapa incluye todos los paquetes, también el de gestión; holgura cero generalizada = alto riesgo de excepción y se informa.
2. [PRINCE2] El camino crítico ignora límites de recursos: con recursos compartidos, nivelar o usar cadena crítica y declararlo.
3. [PMBOK→Plans] Dependencias clasificadas (obligatoria/discrecional, interna/externa); las discrecionales crean holguras arbitrarias; las externas generan riesgo.
4. [PMBOK→Plans] Los lags no son duración; duplicar personas no divide el tiempo por dos.
5. [PMBOK→Plans] En ágil no se convierten puntos a horas ni se comparan velocidades entre equipos; sin velocidad histórica, rango y calibración en 2–3 iteraciones.
6. Gantt en Mermaid por defecto; con `integraciones.diagramas` configurado, versión elevada vía `pm-visuales` sin reemplazar el CSV.
7. Supuestos por defecto si faltan datos: 5 días/semana, 8 h/día, 75 % de disponibilidad, marcados `[por confirmar]`.
