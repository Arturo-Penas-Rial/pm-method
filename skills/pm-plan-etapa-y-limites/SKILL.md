---
name: pm-plan-etapa-y-limites
description: "Planes de proyecto, etapa y excepción; fin de etapa. Usar: plan de etapa, fin de etapa, stage plan, end stage report. No: cronograma→pm-cronograma-estimacion; costos→pm-costos-presupuesto."
version: 2.4.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: planificacion
    agente: pm-planificacion
    procesos_prince2: [SU, IP, SB, DP]
    practicas_prince2: [plans, progress, business-case, risk]
    tecnicas_pmbok: [integración de planes subsidiarios, criterios de salida, análisis de variación y pronóstico]
    artefactos: [plan-etapa, plan-proyecto, informe-fin-etapa, plan-excepcion, lecciones]
    idiomas: [es, en]
---

# Plan de etapa y límites de etapa · Stage plan and stage boundaries

## Cuándo usar / When to use
- SU: plan de la etapa de iniciación (`plan-etapa-1.md`; la iniciación es la etapa 1) para `autorizar-inicio`.
- IP: plan de proyecto y plan de la primera etapa de entrega (etapa 2).
- Fin de cualquier etapa (SB): informe de fin de etapa, business case y plan de proyecto actualizados, plan siguiente, lecciones, solicitud de `autorizar-etapa`.
- Tras un informe de excepción, cuando la junta pide un plan de excepción (`autorizar-plan-excepcion`).
- EN: initiation, project, stage and exception plans; end stage report and the matching board gate.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. plantillas bilingües; equivalencias ES/EN en `references/guia.md` (inicio).

## Conocimiento
- `references/guia.md` (esta skill): §1 puertas y comandos, §2 SU, §3 composición del plan de proyecto, §4 criterios de etapas, §5 tolerancias, §6 composición del plan de etapa, §7 fin de etapa, §8 BMAD en SB, §9 plan de excepción, §10 mínima vs. completa, §11 reglas complementarias.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §5.1 SU, §5.3 IP act. 4–7, §5.6 SB, §4.5 (etapas y puertas), §6, §8.3.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §4.2.1–§4.2.4 (niveles de plan, etapas, tolerancias, reglas), §4.5.1, §4.8.
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §4.c.1–§4.c.2 (tolerancias, excepción), §4.c.7, §4.d (informes), §6.
- Con BMAD: `SPEC.md` §1.13, §1.16 y `pm-bmad-puente`.

## Entradas requeridas
- `estado.json`: `fase`, `proceso_actual`, `etapa_actual` (0 = SU; 1 = iniciación; 2…n = entrega), tolerancias, `roles`, `puertas`, `enfoque_entrega`, `excepcion_abierta`, `integraciones.especificacion`.
- SU: brief y business case esquemático. IP: descripción del producto del proyecto, `wbs.csv`/PBS, flujo, cronograma, presupuesto, riesgos, estrategia de adquisiciones y enfoques (en ágil, backlog y release plan, SPEC §1.10.12).
- Fin de etapa: plan vigente, últimos informes, registros, registro de productos, business case y plan de proyecto.
- **Especificación (fuente única, SPEC §1.16)**: historias y épicas de la etapa y cobertura solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar …` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: planes de proyecto, etapa y excepción e informe de fin de etapa, que citan ids.
- Plan de excepción: informe `X-###` y decisión de la junta que lo pide; si falta alguno, no se produce.

## Procedimiento
### A. Plan de la etapa de iniciación (SU)
1. Listar los productos de gestión de la iniciación con actividades, recursos, duración, costo y tolerancias (`references/guia.md` §2); completar `plan-etapa.md` como `02-planificacion/plan-etapa-1.md`; `estado.py --proyecto <dir> artefacto plan-etapa-1 --ruta 02-planificacion/plan-etapa-1.md --estado en-revision`. **Puerta** `autorizar-inicio`: decide la junta, registra `pm-director`.

### B. Plan de proyecto (IP)
2. Reunir las salidas de las skills de planificación; completar `plan-proyecto.md` (§3).
3. **Etapas**: proponer número y longitud (§4); sin solapes; confirmar con el usuario.
4. **Tolerancias**: proponer las siete por nivel (§5); las registra `pm-director` tras la decisión.
5. Cruzar con business case, mandato y enfoques. Si cronograma o presupuesto no entran ni con las opciones de `pm-cronograma-estimacion` / `pm-costos-presupuesto`, llevar la decisión a la junta vía `pm-director`. Registrar `plan-proyecto` en `en-revision`. **Puertas**: `autorizar-proyecto`, luego `autorizar-etapa` de la etapa 2 (parte C).

### C. Plan de etapa (SB, o desde IP para la etapa 2)
6. Productos e hitos de la etapa vía `pm-planificacion-por-productos`, `pm-cronograma-estimacion`, `pm-costos-presupuesto` y, en ágil, `pm-agil-hibrido` (con BMAD, sprint = paquete de trabajo).
7. Completar `plan-etapa.md` → `02-planificacion/plan-etapa-<n>.md` (composición en §6), con actividades de calidad en `calidad.csv`.
8. Verificar trazabilidad al plan de proyecto; lo que no rastrea es posible deslizamiento → `pm-issues-cambios`. Registrar `plan-etapa-<n>` en `en-revision`; la puerta aprobada avanza `etapa_actual`.

### D. Fin de etapa (SB)
9. **Entrar en SB**: `pm-control` o `pm-director` ejecuta `estado.py limite-etapa` (o `--excepcion X-###`).
10. **Reales y pronósticos** en el plan de etapa y el plan de proyecto, con diferencias marcadas (§7).
11. **Business case** actualizado vía `pm-caso-de-negocio`; si deja de sostenerse, decirlo con claridad.
12. **Lecciones** de la etapa registradas y marcadas para el plan siguiente (§7): `lecciones.py listar --para planificacion` (pm-lecciones-aprendidas) y cada una citada en «lecciones incorporadas» con `accionar`; E-11 avisa las abiertas sin acción; informe con `lecciones.py informe --etapa <n>`.
13. **Especificación antes de la puerta** (§8): `especificacion.py resumen` (cobertura y estados); con BMAD, `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> verificar` y traspasos pendientes (`estado.json.integraciones.bmad.handoffs` sin confirmar). Desvío no traspasado o Sprint Change Proposal nueva → `solicitud-cambio` (`pm-issues-cambios`). El gate de sprint planning (PASS/CONCERNS/FAIL) es insumo de `autorizar-etapa`.
14. **Informe de fin de etapa** (`templates/informe-fin-etapa.md` → `03-control/reportes/<fecha>-informe-fin-etapa-<n>.md`) con cifras citadas y pronóstico contra tolerancias; aseguramiento lo confirma.
15. **Plan siguiente** con la parte C; revisar PID, equipo, roles y enfoques.
16. **Solicitar** `autorizar-etapa` a `pm-director` (arma la solicitud con `pm-direccion-decisiones`) con todo en `en-revision`. Al aprobarse, `etapa_actual` = n+1, proceso CS, fase `entrega`, y `pm-director` registra las nuevas tolerancias. Última etapa → `pm-cierre-proyecto`.

### E. Plan de excepción
17. Verificar informe `X-###`, decisión de la junta y proceso en SB.
18. Completar `plan-excepcion.md` → `02-planificacion/plan-excepcion-X-###.md` con el mismo detalle que el plan que reemplaza (§9).
19. Pedir `autorizar-plan-excepcion` a `pm-director`; tras la decisión, registrar el artefacto y, si reemplaza al plan de etapa, apuntar `plan-etapa-<n>` al plan de excepción. Como subagente, cerrar con el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; un plan de etapa agrupa N iteraciones o releases y fija cuánto backlog se compromete, sin eliminar puertas.
2. [PRINCE2] Desviación prevista fuera de tolerancia → informe de excepción y junta; el plan de excepción solo a pedido explícito de la junta.
3. [PRINCE2] Nada se aprueba sin acto humano; solo `pm-director` registra puertas y tolerancias; esta skill deja todo `en-revision`.
4. [PRINCE2] Todo elemento del plan de etapa rastrea al plan de proyecto; lo demás es control de cambios.
5. [PRINCE2] Etapas sin solape, delimitadas por decisiones parar/seguir; 1 = iniciación, 2…n = entrega.
6. [PRINCE2] Siete tolerancias por plan (tiempo y costo mínimo), anidadas y más estrechas a medida que mejora la información.
7. [PRINCE2] El plan de excepción reemplaza al vigente con igual detalle y crea nuevo límite y línea base.
8. [PRINCE2] Lecciones de la etapa registradas e incorporadas explícitamente al plan siguiente; un cierre bien fundado no es fracaso.
9. [PRINCE2] Con BMAD, `bmad.py verificar` antes de cada puerta; el "sí" de BMAD no reemplaza a la autoridad de cambio.
10. [PMBOK→Plans] El plan de proyecto integra y referencia los planes subsidiarios; no los duplica.
11. [Plantillas] Versión mínima (un plan que hace de plan de etapa, hitos, informe de una página) o completa según riesgo y costo (§10).
12. Transparencia de IA: borrador; `[por confirmar]` en vez de inventar; citar la fuente de cada cifra.
13. Escrituras externas (correo a la junta, chat, tracker) solo con confirmación, vía `pm-integraciones`. Más reglas en §11.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Plan de la etapa de iniciación | `templates/plan-etapa.md` | `02-planificacion/plan-etapa-1.md` | `plan-etapa-1`; puerta `autorizar-inicio` |
| Plan de proyecto | `templates/plan-proyecto.md` | `02-planificacion/plan-proyecto.md` | `plan-proyecto`; puerta `autorizar-proyecto` |
| Plan de etapa n ≥ 2 | `templates/plan-etapa.md` | `02-planificacion/plan-etapa-<n>.md` | `plan-etapa-<n>`; puerta `autorizar-etapa` |
| Informe de fin de etapa | `templates/informe-fin-etapa.md` | `03-control/reportes/<fecha>-informe-fin-etapa-<n>.md` | `informe-fin-etapa-<n>` |
| Plan de excepción | `templates/plan-excepcion.md` | `02-planificacion/plan-excepcion-X-###.md` | `plan-excepcion-X-###`; puerta `autorizar-plan-excepcion` |
| Lecciones de la etapa | `registro.py agregar lecciones` | `03-control/registros/lecciones.csv` | — |
| Business case y plan de proyecto actualizados | vía `pm-caso-de-negocio` y `plan-proyecto.md` | `00-direccion/business-case.md`, `02-planificacion/plan-proyecto.md` | nueva versión |

## Calidad
- [ ] Plan con su composición completa (§3, §6) y lecciones incorporadas con ID.
- [ ] Trazabilidad al nivel superior; ningún paquete cruza un límite sin nota.
- [ ] Siete tolerancias explícitas, anidadas, con la restricción dominante declarada.
- [ ] Informe de fin de etapa con cifras citadas y pronóstico contra tolerancias.
- [ ] Con BMAD: `verificar` limpio o desvíos como issues; traspasos pendientes y gate de sprint planning informados.
- [ ] Plan de excepción con referencia al informe y a la decisión; diferencias explícitas.
- [ ] Rutas canónicas; puerta pedida a `pm-director` con el rol que decide; nada `aprobado` desde aquí.

## Escalamiento y excepciones
- Pronóstico fuera de tolerancia al preparar el fin de etapa → informe de excepción (`pm-issues-cambios`) y `pm-director`.
- Plan que no entra en tolerancia ni con compresión → decisión de la junta antes de pedir la puerta; si supera tolerancias de proyecto, decide la capa de negocio.
- Business case inviable → recomendación de cierre prematuro (`pm-director`, `pm-cierre-proyecto`).
- Como subagente: decisiones humanas (número de etapas, tolerancias, aprobación) en el bloque de retorno (SPEC §1.11), no se preguntan.

## Ejemplos de invocación
- "Preparame el plan de la etapa 2 con tolerancias y controles a partir del plan de proyecto."
- "Cerrá la etapa 1: informe de fin de etapa, lecciones, business case y verificá si cambió el PRD de BMAD."
- EN: "Draft the initiation stage plan to go with the project brief."
- EN: "The board asked for an exception plan after yesterday's exception report; replace the stage 3 plan."
- No activa: "Calculá el camino crítico de la etapa 2" → `pm-cronograma-estimacion`.

## EN summary
Stage planning and stage boundaries: initiation stage plan (stage 1), project plan with stages, seven tolerances and planned board decisions, detailed stage plans, end stage reports with cited figures and forecasts, stage lessons, and exception plans only at the board's request. With BMAD it runs `bmad.py verificar` before each stage gate and feeds the sprint-planning readiness result into `autorizar-etapa`. Gates are recorded only by pm-director.
