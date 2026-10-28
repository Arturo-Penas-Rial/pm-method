---
name: pm-cronograma-estimacion
description: "Estimación y cronograma: PERT, puntos, CPM, Gantt, hitos, MS Project (MSPDI). Usar: estimar, cronograma, camino crítico, Gantt, schedule, critical path. No: presupuesto→pm-costos-presupuesto."
version: 2.5.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: planificacion
    agente: pm-planificacion
    procesos_prince2: [IP, SB, MP]
    practicas_prince2: [plans, progress]
    tecnicas_pmbok: [estimación análoga, estimación paramétrica, tres valores (triangular, beta-PERT), estimación ascendente, Delphi, puntos de historia, método del diagrama de precedencias, CPM, nivelación de recursos, compresión del cronograma, reservas de contingencia]
    artefactos: [hoja-estimacion, actividades, cronograma, cronograma-mspdi, plan-equipo]
    idiomas: [es, en]
---

# Estimación y cronograma · Estimation and schedule

## Cuándo usar / When to use
- Ya existen paquetes de trabajo (`pm-planificacion-por-productos`) o, en ágil, backlog con puntos (`pm-agil-hibrido`) y hay que estimar esfuerzo y duración.
- Piden "estimar", "cuánto tarda", "PERT", "planning poker", "dependencias", "camino crítico", "Gantt", "hitos", "nivelar recursos", "reserva de cronograma", "plan de equipo" o "pasarlo a MS Project".
- Cronograma del plan de proyecto (IP), de etapa o de excepción (SB) o plan de equipo de un paquete (MP).
- EN: estimate work packages (analogous, parametric, three-point, bottom-up, story points) and build a CPM schedule with Gantt and milestones.
- EN: export the schedule as MS Project XML (MSPDI) or plan sprints from velocity.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. plantillas bilingües. Equivalencias: esfuerzo (effort), camino crítico (critical path), holgura (float), hito (milestone), intensificación (crashing), ejecución rápida (fast tracking). Columnas de `actividades.csv`: ver `references/guia.md` §3.

## Conocimiento
- `references/guia.md` (esta skill): §1 técnica de estimación, §2 fórmulas, §3 `cpm.py` y CSV, §4 export MSPDI, §5 herramientas externas, §6 compresión, §7 reservas, hitos y plan de equipo, §8 mínima vs. completa, §9 reglas complementarias.
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.7 Familia G (estimación) y §3.8 Familia H (precedencias, CPM, compresión, nivelación, cadena crítica); §5.1 técnica por pregunta.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §4.2.3 (tolerancias y confianza), §4.2.4 reglas 12–17, §4.3.1 Pasos 3–4, §4.3.3–§4.3.4 (programación y estimación), §4.2.1 (plan de equipo).
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §6–§7, Parte V.

## Entradas requeridas
- `estado.json`: `enfoque_entrega`, `etapa_actual`, tolerancias de tiempo (proyecto y etapa), `agil.cadencia_iteracion_dias`, `agil.velocidad_referencia`, `integraciones.cronograma` (`cpm` por defecto o `mspdi`).
- **Predictivo/híbrido**: `02-planificacion/wbs.csv` (o `pbs-wbs.md`) y `diccionario-wbs.md` con paquetes y responsables; `flujo-productos.md` con dependencias. Si faltan → `pm-planificacion-por-productos`.
- **Ágil (perfil mínimo, SPEC §1.10.12)**: `02-planificacion/backlog.csv` (puntos, MoSCoW, release) y cadencia.
- **Especificación (fuente única, SPEC §1.16)**: épicas, historias, estados y estimación de gobierno solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar historias|epicas` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: `actividades.csv` y cronograma, que citan ids.
- Restricción de fecha del mandato; calendario y disponibilidad (si faltan, supuestos `[por confirmar]`, §9); históricos, lecciones, riesgos.
- Python 3 para `cpm.py`. MS Project, ProjectLibre o MPXJ: opcionales y externos.

## Procedimiento
1. **Situar y elegir nivel**: plan de proyecto (semanas, recursos por habilidad), etapa (días, personas) o equipo (tareas). Proponer versión mínima o completa (`references/guia.md` §8) y confirmar.
2. **Definir actividades** por paquete de la WBS, más las de gestión y calidad y los hitos (duración 0). Cada actividad lleva en la columna opcional `wbs` el código del paquete en `wbs.csv` (1.2.3).
3. **Estimar** eligiendo y declarando la técnica por actividad (§1); en `hoja-estimacion.md` cálculo, supuestos, confianza y estimador; tres valores siempre en lo crítico (columnas `optimista,mas_probable,pesimista` de `actividades.csv`). Quien hará el trabajo valida.
4. **Esfuerzo → duración**: `duración = esfuerzo / (recursos × % disponible × factor de desempeño)` (§2); la reserva nunca dentro del estimado base.
5. **Secuenciar**: predecesoras (FS; lags `id+N`/`id-N`), dependencias clasificadas, volcado a `actividades.csv` (`id,nombre,duracion,predecesoras,recurso,wbs`); reglas del CSV en §3.
6. **Camino crítico**: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/cpm.py 02-planificacion/actividades.csv --inicio AAAA-MM-DD --mermaid 02-planificacion/gantt.md`; llevar a `cronograma.md` ES/EF/LS/LF, HT, HL, camino crítico y carga por recurso. Con SS/FF/SF, feriados o nivelación automática, usar una herramienta externa (§5) y declararlo.
7. **Nivelar o alisar** sobreasignaciones (alisar no mueve el fin; nivelar puede moverlo) y documentar.
8. **Si el fin supera la restricción o la tolerancia de tiempo**: evaluar ejecución rápida, intensificación, MoSCoW y recursos, recalculando cada vez (§6). Si nada entra, el plan **no** se presenta como aprobable: decisión de la junta vía `pm-director`.
9. **Reservas**: `cpm.py … --estimacion 02-planificacion/estimacion-pert.csv [--distribucion triangular] [--confianza 1]` da σ del camino crítico, reserva kσ y fin con reserva (para `impacto.py --pert`); visible, ligada a riesgos (§3, §7).
10. **Hitos y etapas**: de producto, de puerta y de compras; ningún paquete cruza un límite de etapa sin nota (§7).
11. **Variante ágil**: `iteraciones = ⌈puntos Must+Should ÷ velocidad⌉`, `duración = iteraciones × cadencia`, rango con velocidad baja/alta; iteraciones como bloques fijos y releases como hitos. Con BMAD, cada sprint es un paquete de trabajo; el avance real sale de la fachada (`listar historias --estado …`). Si los Must no entran, paso 8 (primero alcance).
12. **Export MS Project** (si lo piden o `integraciones.cronograma = mspdi`): agregar `--mspdi 02-planificacion/cronograma.xml --titulo "<Proyecto>" --wbs 02-planificacion/wbs.csv`. Sin feriados ni calendarios por recurso: tras importar, comparar el fin; `.mpp` y límites en §4.
13. **Documentar** en `cronograma.md`: Gantt, tabla CPM, carga, reservas, supuestos, dependencias externas, confianza, ruta del MSPDI. Versión gráfica opcional con `pm-visuales`.
14. **Plan de equipo** (opcional): `plan-equipo.md` por paquete, o tablero de iteración en ágil.
15. **Registrar y derivar**: `estado.py --proyecto <dir> artefacto cronograma --ruta 02-planificacion/cronograma.md --estado en-revision`; horas a `wbs.csv`/diccionario; esfuerzos a `pm-costos-presupuesto`. **Puerta humana**: el cronograma se aprueba con el plan (`autorizar-proyecto` / `autorizar-etapa`, que registra solo `pm-director`). Como subagente, cerrar con el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; las iteraciones son bloques dentro del cronograma de etapa, sin eliminar puertas.
2. [PRINCE2] Un retraso previsto fuera de tolerancia se escala (excepción); nunca se mueven hitos en silencio.
3. [PRINCE2] Nada se aprueba sin acto humano registrado; el cronograma es borrador hasta aprobar el plan que lo contiene.
4. [PRINCE2] Toda estimación lleva nivel de confianza; tolerancias amplias al inicio y más estrechas etapa a etapa.
5. [PRINCE2] El cronograma de etapa incluye todos los paquetes (también gestión) y muestra la holgura.
6. [PMBOK→Plans] Técnica elegida según la pregunta, con método, rango (O/M/P), confianza y estimador declarados.
7. [PMBOK→Plans] Esfuerzo y duración aparte; tres valores con `P ≥ M ≥ O`: triangular `(O+M+P)/3` (la Guía, ref. §3.7) o beta-PERT `(O+4M+P)/6`, `σ=(P−O)/6` (práctica habitual, no en la fuente), declarada en el plan; por defecto beta.
8. [PMBOK→Plans] Compresión solo sobre el camino crítico, cuantificada en costo y riesgo; si nada entra, decide la junta.
9. [PMBOK→Plans/SB] En ágil, puntos ÷ velocidad; sin conversión a horas ni comparación entre equipos.
10. [Plantillas] Reserva de contingencia aparte del estimado base y visible; versión mínima o completa según riesgo y costo.
11. La fuente del cronograma es `actividades.csv`; Mermaid y MSPDI se regeneran, no se editan en paralelo. Ninguna herramienta externa es obligatoria.
12. Transparencia de IA: borrador; `[por confirmar]` en vez de inventar; citar histórico, registro o persona de cada estimación.
13. Escrituras externas (tracker, MS Project en la nube, chat) solo con confirmación, vía `pm-integraciones`. Más reglas en §9.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Hoja de estimación | `templates/hoja-estimacion.md` | `02-planificacion/hoja-estimacion.md` (o `-etapa-<n>`) | `hoja-estimacion` |
| Actividades secuenciadas | `templates/actividades.csv` | `02-planificacion/actividades.csv` | `actividades` |
| Cronograma (Gantt, CPM, reservas, hitos) | `templates/cronograma.md` (+ `gantt.md` de `cpm.py`) | `02-planificacion/cronograma.md` | `cronograma` |
| MS Project XML (MSPDI, opcional) | `cpm.py --mspdi` | `02-planificacion/cronograma.xml`; copia en `exportados/` | ruta adicional en `cronograma` |
| Plan de equipo | `templates/plan-equipo.md` | `03-control/paquetes-trabajo/plan-equipo-<paquete>.md` | `plan-equipo-<paquete>` |

## Calidad
- [ ] Cada actividad con paquete (`wbs`), técnica, supuestos, estimador y confianza; `P ≥ M ≥ O`.
- [ ] Esfuerzo y duración en unidades declaradas, con disponibilidad y factor de desempeño.
- [ ] Red sin ciclos; dependencias clasificadas; camino crítico y holguras visibles; casi críticos señalados.
- [ ] Carga por recurso revisada; nivelación o alisado documentados.
- [ ] Reserva separada y ligada a riesgos; fin comparado con mandato y tolerancias; compresión documentada si no entra.
- [ ] Ágil: iteraciones = puntos ÷ velocidad con rango declarado.
- [ ] Hitos de producto, puerta y compras; Gantt Mermaid renderizable.
- [ ] MSPDI (si se pidió) regenerado desde el CSV vigente y fin verificado tras importar.
- [ ] Frontmatter completo y `borrador` hasta la puerta.

## Escalamiento y excepciones
- Fin fuera de la restricción o tolerancia tras el paso 8 → `pm-director` antes de aprobar el plan.
- Pronóstico fuera de tolerancia con línea base vigente → informe de excepción (plantilla de `pm-issues-cambios`) y `pm-director`.
- Conflicto de recursos sin holgura → `pm-director` (compromiso de recursos) y riesgo; dependencia externa sin fecha → `pm-riesgos`.
- Sin paquetes → `pm-planificacion-por-productos`.
- Como subagente: las decisiones humanas se devuelven en el bloque de retorno (SPEC §1.11), no se preguntan.

## Ejemplos de invocación
- "Estimá con tres puntos las actividades de la etapa 2 y calculá el camino crítico."
- "Armá el cronograma del proyecto Faro con Gantt e hitos y exportalo para abrirlo en MS Project."
- EN: "Estimate these work packages with PERT and give me the critical path and float."
- EN: "With 140 Must and Should points and velocity 25, how many two-week sprints does stage 3 need?"
- No activa: "¿Cuánto cuesta la etapa 2 con reservas?" → `pm-costos-presupuesto`.

## EN summary
Estimation and scheduling inside PRINCE2 plans. It picks and declares an estimation technique per activity, separates effort from duration, sequences activities (optional `wbs` column tied to `wbs.csv`), computes the critical path with `cpm.py` (Mermaid Gantt, float, resource load) and can export MS Project XML with `--mspdi` (importable by MS Project and other MSPDI readers). It levels resources, sizes schedule reserves from labelled three-point estimates (`cpm.py --estimacion`), and escalates any end date outside tolerance to the board instead of absorbing it.
