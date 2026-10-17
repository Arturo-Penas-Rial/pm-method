---
name: pm-progreso-reportes
description: "Informes de avance PRINCE2 con EVM y semáforos. Usar: checkpoint, highlight report, status report, valor ganado, EVM, burn-up, pronóstico. No: tablero o gráficos→pm-visuales."
version: 2.0.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [CS, MP, DP]
    practicas_prince2: [progress, risk, issues, quality]
    tecnicas_pmbok: [valor ganado, análisis de variaciones, pronóstico EAC, burn-down, burn-up, velocidad, cronograma ganado]
    artefactos: [informe-avance-equipo, checkpoint-report, highlight-report, analisis-variaciones, analisis-valor-ganado, progreso.csv, avance-bmad.csv]
    idiomas: [es, en]
---

# Progreso e informes · Progress and reporting

## Cuándo usar / When to use
- Al cierre de cada período de informe del PID: recoger checkpoints, medir contra el plan de etapa y redactar el highlight report para la junta.
- Un miembro o gestor de equipo debe informar avance (checkpoint report).
- Valor ganado (`evm.py`), variaciones, pronóstico y semáforos; burn-up y velocidad en ágil (con BMAD, `avance-bmad.csv`).
- EN: close a reporting period: checkpoints, EVM or burn charts, highlight report with RAG against tolerances.
- EN: forecast completion and decide whether a deviation is a corrective action or an exception.

## Idioma
Responder en el idioma del usuario. Términos EN la primera vez: checkpoint report, highlight report, variance analysis, earned value (EV/PV/AC/EAC), burn-up chart. Siglas EVM en inglés en ambos idiomas; plantillas bilingües; `progreso.csv` con cabecera técnica.

## Conocimiento
- `references/guia.md` (esta skill): entradas §1, avance de equipo §2, EVM §3, ágil y burn-up §4, BMAD §5, trackers §6, variaciones y pronóstico §7, semáforos §8, highlight §9, adaptación por enfoque §10, reglas extendidas §11, fin de etapa §12.
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §4 (tolerancias, controles, cadena de informes, pronóstico, checkpoint, highlight); §7.2 A-14/A-15; §7.5 A-29 a A-35.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §27–§30 (avance, estado, variaciones, valor ganado); §49 reglas 21–22.
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.2, §3.3, §3.13 (EVM, burn charts, velocidad).

## Entradas requeridas
- `estado.json`: `enfoque_entrega`, `tolerancias` (etapa y proyecto), `etapa_actual`, `roles`, `artefactos`, `integraciones`.
- Plan de etapa vigente (`02-planificacion/plan-etapa-<n>.md`) y paquetes con su frecuencia de checkpoint (`03-control/paquetes-trabajo/`).
- EVM: `linea-base-costo.csv`, presupuesto por producto, método de medición del EV, costos reales, BAC sin reserva de gestión (`references/guia.md` §1). Ágil: backlog con puntos, MoSCoW, velocidad, línea base del release plan.
- Checkpoints del período, `<pm-estado-proyecto>/scripts/registro.py --proyecto <dir> resumen --json`, highlight anterior, `progreso.csv`.
- **Especificación (fuente única, SPEC §1.16)**: estados de historias y épicas solo vía `python3 <pm-estado-proyecto>/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar …` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`); serie histórica en `avance-bmad.csv`. Escribe como dueña: informes, que citan ids. Tracker: instantánea en `03-control/fuentes/` (`pm-integraciones`).

## Procedimiento
1. **Situar.** `estado.json`, plan de etapa y highlight anterior (lo prometido, seguimientos, semáforos previos).
2. **Recoger avance por paquete** (`templates/informe-avance-equipo.md`, `templates/checkpoint-report.md`; en ágil, tablero en modo pull). Controles en `references/guia.md` §2. Actualizar el plan de etapa: completado solo si está aprobado en `calidad.csv`.
3. **Especificación y fuentes externas.** Estados por la fachada (`resumen`, `listar historias --estado …`). Con BMAD, cada período: `python3 <pm-bmad-puente>/scripts/bmad.py --proyecto <dir> verificar` (desvío no traspasado o Sprint Change Proposal → `pm-issues-cambios`) y `bmad.py avance` (fila en `avance-bmad.csv`, burn-up; guía §5). Tracker: solo instantáneas (guía §6).
4. **Medir desempeño.** Predictivo o híbrido con línea base: actualizar `progreso.csv` y correr `evm.py --tol-costo --tol-plazo` con tolerancias de etapa y de proyecto (comando y controles en guía §3). Ágil: velocidad, burn-down, burn-up y, opcional, `evm.py --modo agil --pct-no-must` (guía §4).
5. **Analizar variaciones** de tiempo, costo y desempeño técnico con causa raíz, respuesta, responsable y fecha; `templates/analisis-variaciones.md` si se supera el umbral de atención (guía §7).
6. **Pronosticar contra los siete objetivos** y comparar el pronóstico (no el acumulado) con las tolerancias de etapa y proyecto; semáforo por regla (guía §8).
7. **PUERTA HUMANA — Acción correctiva o excepción.** Dentro de tolerancia → acciones correctivas que el gestor confirma, en `acciones.csv` o enmienda del paquete. Problema de fondo que es un issue → `pm-issues-cambios`. Pronóstico fuera de tolerancia (`excepcion_prevista` o rojo en otra dimensión) → aviso temprano e **informe de excepción** con `pm-issues-cambios/templates/informe-excepcion.md` en `03-control/reportes/`, `en-revision`; pm-control lo entrega a `pm-director`, único que registra la decisión.
8. **Reunir registros.** `registro.py resumen --json [--corte <fecha>]` con sus campos tal cual (guía §9); riesgo alto sin respuesta o sin propietario → semáforo de riesgo rojo.
9. **Redactar el highlight** con `templates/highlight-report.md` → `03-control/reportes/<fecha>-highlight-report.md`, variante mínima o completa (guía §9). Cada cifra con fuente; cada semáforo con cifra y umbral. En ágil o híbrido, bloque burn-up (guía §4).
10. **Adaptar por audiencia** con `pm-comunicacion-stakeholders`: mismas cifras, distinta selección.
11. **Registrar.** `<pm-estado-proyecto>/scripts/estado.py --proyecto <dir> artefacto highlight-<fecha> --ruta ... --estado en-revision`; tras la revisión humana, `estado.py aprobar highlight-<fecha> --por "<rol: nombre>"`.
12. **Fin de etapa próximo** → proponer `estado.py limite-etapa` y derivar a `pm-plan-etapa-y-limites` (guía §12). Como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; en ágil o híbrido el progreso se mide por ítems terminados en cada iteración dentro de la etapa, sin eliminar el highlight ni las puertas.
2. [PRINCE2] Desviación prevista fuera de tolerancia → excepción a `pm-director` vía la plantilla de `pm-issues-cambios`; el highlight nunca suaviza un pronóstico de excepción.
3. [PRINCE2] Nada aprobado sin acto humano registrado: acciones confirmadas por el gestor, highlight confirmado por aseguramiento y revisado por la junta.
4. [PRINCE2] Pronosticar siempre: se compara el pronóstico, no el acumulado, contra tolerancias de etapa y proyecto.
5. [PRINCE2] El highlight cubre los siete objetivos, distingue hecho de pronóstico, lista RFC y fuera de especificación aunque sea "ninguna" y pide decisiones explícitas a la junta.
6. [PRINCE2] Una página; detalle en anexos; nunca contradecir los registros.
7. [PRINCE2] Sin tolerancias no hay gestión por excepción: declararlo y pedir a la junta que las fije.
8. [PMBOK→Progress/CS] Técnica según la pregunta (EVM, burn charts, camino crítico, cronograma ganado); declarar método del EV y EAC elegida; BAC sin reserva de gestión.
9. [PMBOK→Progress/CS] Semáforo por `evm.py --tol-costo/--tol-plazo`: verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo fuera.
10. [PMBOK→Progress/MP] EVM ágil con costo y fecha fijos: EAC > BAC = alcance que no entra; excepción solo si no entran los Must. Solo cuentan ítems terminados; con BMAD, solo `done`.
11. [PRINCE2] Con BMAD, `bmad.py verificar` cada período; los desvíos del PRD son solicitudes de cambio, no ajustes del informe.
12. [Plantillas] Validar la cadena de reporte (mismas cifras en highlight, variaciones y EVM); versión mínima o completa según riesgo.
13. Transparencia de IA: cada cifra con origen; `[por confirmar]` si falta; borrador hasta confirmación.
14. Datos externos solo como instantáneas fechadas; escrituras externas solo con confirmación explícita vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Avance de miembro / checkpoint | `templates/informe-avance-equipo.md`, `templates/checkpoint-report.md` | `03-control/reportes/<fecha>-checkpoint-WP-###.md` | — |
| Highlight report | `templates/highlight-report.md` | `03-control/reportes/<fecha>-highlight-report.md` | `highlight-<fecha>` |
| Variaciones / valor ganado | `templates/analisis-variaciones.md`, `templates/analisis-valor-ganado.md` | `03-control/reportes/<fecha>-analisis-*.md` | opcional |
| Serie EVM | `templates/progreso.csv` | `03-control/reportes/progreso.csv` | `progreso-csv` |
| Avance BMAD | `bmad.py avance` | `03-control/reportes/avance-bmad.csv` | — (derivado) |
| Acciones correctivas | `registro.py agregar acciones` | `03-control/registros/acciones.csv` | — |
| Informe de excepción | `pm-issues-cambios/templates/informe-excepcion.md` | `03-control/reportes/<fecha>-informe-excepcion-X-###.md` | `informe-excepcion-X-###` (puerta: solo `pm-director`) |

## Calidad
- [ ] Lo planificado coincide con lo prometido en el informe anterior; completados solo si aprobados en `calidad.csv`.
- [ ] EVM: BAC vigente, método de EV, EV ≤ PV, acumulados coherentes, dos EAC con la elegida justificada, `base_semaforo` declarada.
- [ ] Ágil: solo ítems terminados; velocidad con ventana; burn-up con línea de alcance total. BMAD: `verificar` y `avance` del período corridos y citados.
- [ ] Variaciones con causa raíz, respuesta, responsable y fecha; pronóstico contra siete objetivos y ambas tolerancias.
- [ ] Decisiones para la junta y RFC listados; conteos = `registro.py resumen`.
- [ ] Pronóstico fuera de tolerancia → informe de excepción entregado a `pm-director`; ninguna puerta registrada aquí.

## Escalamiento y excepciones
- Pronóstico fuera de tolerancia en cualquiera de los siete objetivos → aviso temprano + informe de excepción → `pm-director` decide; el highlight lo señala en rojo con `X-###`.
- Fuera de tolerancia del paquete → issue (`pm-issues-cambios`).
- Tolerancias o periodicidad no definidas → `pm-director`; reportar sin semáforo y declararlo.
- Cifras discrepantes → corregir el registro antes de emitir. Sin línea base de costo → `pm-costos-presupuesto`.
- Como subagente (pm-control): confirmaciones del gestor y decisiones de la junta se devuelven en el bloque de retorno (SPEC §1.11), no se preguntan.

## Ejemplos de invocación
- "Armá el highlight report de la quincena con estos checkpoints y el resumen de registros."
- "Calculá el valor ganado al 30 de octubre: PV 180k, EV 150k, AC 170k, BAC 600k, y decime qué EAC usar."
- EN: "Build the burn-up for sprint 6 from the BMAD progress file and tell me whether any Must items fall outside the release date."
- EN: "Write the checkpoint report for WP-004: three products done, one blocked by the customs API."
- No activa: "Actualizá el tablero HTML con la vista por actor" → `pm-visuales`.

## EN summary
Runs the PRINCE2 progress practice per reporting period: collects checkpoints, updates the stage plan with approved products only, measures with `evm.py` (tolerance-based RAG) or burn charts, reads story status only via `especificacion.py`, and with BMAD runs `bmad.py verificar` and `avance` each period.
Forecast breaches of tolerance produce an exception report for pm-director.
Tracker data enters only as dated snapshots from pm-integraciones; every figure cites its source and the highlight stays a draft until assurance confirms it.
