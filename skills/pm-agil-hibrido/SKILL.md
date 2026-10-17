---
name: pm-agil-hibrido
description: "Ágil/híbrido en etapas: backlog MoSCoW, historias, release plan, velocidad, retro de iteración. Usar: backlog, sprint, user story, release plan, DoD, velocity. No: sync con BMAD→pm-bmad-puente."
version: 2.1.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: planificacion
    agente: pm-planificacion
    procesos_prince2: [IP, CS, MP, SB]
    practicas_prince2: [plans, progress, quality, issues]
    tecnicas_pmbok: [backlog priorizado, MoSCoW, planning poker, velocidad, release planning, burn-up, Kanban, DoD/DoR, EVM adaptativo, retrospectiva]
    artefactos: [backlog, historia-usuario, release-plan, retrospectiva]
    idiomas: [es, en]
---

# Adaptación ágil e híbrida · Agile and hybrid delivery

## Cuándo usar / When to use
- `enfoque_entrega` es `agil` o `hibrido` y la etapa se planifica o sigue en iteraciones: backlog, historias, release plan, cadencia, DoD y DoR.
- Piden "backlog", "historia de usuario", "épica", "sprint", "release plan", "MoSCoW", "velocidad", "MVP", "perfil ágil mínimo".
- EN: agile or hybrid work inside PRINCE2 stages: MoSCoW backlog, user stories, release plan baseline, cadence, DoD/DoR.
- EN: PO swaps within scope tolerance, agile EVM, iteration retrospective.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. plantillas bilingües. Equivalencias ES/EN y columnas de `backlog.csv`: `references/guia.md` §2.

## Conocimiento
- `references/guia.md` (esta skill): §1 perfil mínimo, §2 columnas del backlog, §3 BMAD, §4 ceremonias↔controles, §5 retro vs. lecciones, §6 fórmulas y EVM ágil, §7 comandos, §8 reglas complementarias, §9 casos borde.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §4.4, §4.8 "Proyecto ágil", §4.3.2, §5.4 (MVP, DoD, DoR).
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §5.3–§5.6 (adaptación ágil de IP, CS, MP, SB).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §4.c.5 y §4.c.2.
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.13 Familia M, §3.8, §3.7.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §17, §18, §20, Parte V.
- Con BMAD: `SPEC.md` §1.13, §1.16 y `pm-bmad-puente`.

## Entradas requeridas
- `estado.json`: `enfoque_entrega` (si es `predictivo`, preguntar y pedir a `pm-director` que registre el cambio), `etapa_actual`, `tolerancias.etapa` (alcance, tiempo, costo), `roles.product_owner`, `agil.*`, `integraciones.tracker`, `integraciones.especificacion`.
- **Perfil ágil mínimo (SPEC §1.10.12)**: el backlog priorizado sustituye a PBS/WBS, diccionario y flujo; basta la descripción del producto del proyecto o la visión con MVP. No pedir `pbs-wbs.md` para avanzar.
- Plan de etapa vigente o en preparación (`plan-etapa-<n>.md`); si no existe → `pm-plan-etapa-y-limites`.
- Equipo, capacidad y velocidad histórica (o calibración en las primeras 2–3 iteraciones).
- **Especificación (fuente única, SPEC §1.16)**: épicas, historias y estados solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar historias|epicas` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: columnas de gobierno de `backlog.csv` y `release-plan.md`.

## Procedimiento
1. **Cadencia**: confirmar duración de iteración, iteraciones por etapa, capacidad y, en híbrido, qué paquetes iteran. Proponer a `pm-director` registrar cadencia y PO (`references/guia.md` §7).
2. **Perfil**: mínimo o completo (§1); las puertas de etapa existen siempre.
3. **DoD y DoR** en `release-plan.md`, referenciadas desde el enfoque de calidad. **Puerta humana**: las acuerdan equipo y usuario sénior; decisión registrada.
4. **Backlog** (`02-planificacion/backlog.csv`, plantilla `templates/backlog.csv`):
   - *Sin BMAD*: épicas desde productos mayores o visión, historias desde requisitos; orden total, `moscow`, puntos, estado, `iteracion`, `release`, `producto_pbs`, criterios. Refinar solo lo próximo; incluir deuda técnica y acciones de retro.
   - *Con BMAD*: filas y columnas **derivadas** las refresca `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> backlog`; el PO completa solo las de **gobierno** (prioridad, moscow, estimacion, iteracion, release, producto_pbs). Nada de historias ni requisitos a mano (§3).
5. **Historias** (sin BMAD) con `historia-usuario.md`: como/quiero/para, dado-cuando-entonces, INVEST.
6. **Tolerancia de alcance**: Must = compromiso mínimo; Should/Could = tolerancia; Won't fuera. Must ≤ ~60 % de la capacidad (§6). Proponerla en el plan de etapa; la registra `pm-director` tras `autorizar-etapa`.
7. **Release plan**: objetivo por capacidad, iteraciones, historias, dependencias; en híbrido, releases = hitos del cronograma maestro. `Σ puntos Must+Should ≤ velocidad × iteraciones` o repriorizar. Solo **línea base**.
8. **Presupuesto y fecha**: costo por iteración a `pm-costos-presupuesto`, iteraciones a `pm-cronograma-estimacion`; si los Must no entran, opciones (primero alcance) y, si sigue fuera, junta vía `pm-director`.
9. **Ceremonias ↔ controles** (§4). **Cada sprint = paquete de trabajo** autorizado con `pm-paquetes-trabajo` (alcance = historias del sprint, tolerancias, DoD).
10. **Seguir la iteración**: velocidad = puntos terminados (DoD), promedio de 3. Estados por la fachada (`listar historias --estado …`); con BMAD, serie en `avance-bmad.csv` (`bmad.py avance`). Datos a `pm-progreso-reportes`, que dibuja burn charts en los informes.
11. **Swaps del PO**: cambiar Should/Could por un ítem equivalente sin tocar Must, fecha ni costo lo decide el PO (`decisiones.csv`, `nivel=product-owner`, §7). Lo que desplaza un Must o excede la tolerancia → `pm-issues-cambios`. Historias nuevas o `retirada-en-bmad`: mismo criterio. **Con BMAD**, todo cambio de MoSCoW, release o iteración llega a BMAD solo con `bmad.py handoff` (sin `--cambio`), insumo de su sprint planning; nunca editar BMAD.
12. **EVM ágil** con `evm.py --modo agil --pct-no-must` (§6): EAC > BAC = alcance que no entra; excepción solo si peligran los Must.
13. **Tolerancias**: si los Must no caben en tiempo o costo, es excepción → `pm-progreso-reportes` (informe con la plantilla de `pm-issues-cambios`) y `pm-director`. Recortar un Must nunca se decide aquí.
14. **Límite de etapa con BMAD**: el gate de preparación del sprint planning (PASS/CONCERNS/FAIL) va a `pm-plan-etapa-y-limites` para `autorizar-etapa`.
15. **Retrospectiva** (`retrospectiva.md`): 1–3 acciones con dueño y fecha (backlog como `accion_retro` o `acciones.csv`); lecciones candidatas a `lecciones.csv` con confirmación. El taller de etapa es de `pm-lecciones-aprendidas`.
16. **Registrar**: `estado.py --proyecto <dir> artefacto backlog --ruta 02-planificacion/backlog.csv --estado en-revision` (y `release-plan`). **Puerta humana**: backlog comprometido y release plan se aprueban con el plan de etapa (`autorizar-etapa`, registrada por `pm-director`); cada incremento lo acepta el usuario sénior o el PO en la review. Como subagente, cerrar con el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; iteraciones como paquetes de trabajo dentro de las etapas, sin eliminar puertas.
2. [PRINCE2] Si los Must no caben, se informa a la junta; nunca se estiran iteraciones ni se baja la DoD en silencio.
3. [PRINCE2] Nada se aprueba sin acto humano; solo `pm-director` registra puertas, tolerancias, cadencia y PO.
4. [PRINCE2] Tiempo y costo con tolerancia estrecha; alcance amplia vía MoSCoW; los Must no se negocian sin excepción.
5. [PRINCE2] El PO intercambia ítems dentro de la tolerancia sin solicitud de cambio (`nivel=product-owner`); lo demás es cambio.
6. [PRINCE2] Las ceremonias alimentan los controles, no los sustituyen; cada sprint es un paquete de trabajo.
7. [PRINCE2] En perfil mínimo, el backlog reemplaza a PBS/WBS/diccionario/flujo; la descripción del producto del proyecto se mantiene.
8. Dueño único con BMAD: historias y requisitos en BMAD; prioridad, MoSCoW, estimación, iteración y release en `backlog.csv`, y viajan a BMAD solo por `bmad.py handoff`. Nunca duplicar.
9. [PMBOK→Progress] Velocidad para pronóstico, burn charts para variación, EVM adaptativo solo con ítems terminados según DoD.
10. [PMBOK→Plans] Puntos sin conversión a horas; caja de tiempo respetada.
11. [Plantillas] El release plan guarda la línea base; los burn charts reales van a los informes. Versión mínima o completa según riesgo.
12. Transparencia de IA: borrador; no inventar velocidad; citar la fuente de cada cifra.
13. Escrituras externas (tracker, chat) solo con confirmación por operación, vía `pm-integraciones`; el CSV es la fuente. Más reglas en §8.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Backlog priorizado | `templates/backlog.csv` | `02-planificacion/backlog.csv` | `backlog` |
| Historias de usuario (sin BMAD) | `templates/historia-usuario.md` | `02-planificacion/historias/<id>-<slug>.md` | — |
| Release plan (cadencia, DoD/DoR, ceremonias, línea base) | `templates/release-plan.md` | `02-planificacion/release-plan.md` | `release-plan` |
| Retrospectiva de iteración | `templates/retrospectiva.md` | `03-control/reportes/<fecha>-retrospectiva-S<k>.md` | — |
| Avance BMAD (derivado) | `bmad.py avance` | `03-control/reportes/avance-bmad.csv` | — |
| Swaps del PO / acciones de retro | `registro.py agregar decisiones` / `acciones` | `03-control/registros/` | — |

## Calidad
- [ ] Enfoque ágil/híbrido registrado; PO y cadencia en `estado.json`; perfil declarado.
- [ ] Backlog con orden total, `moscow` y `release` en los ítems próximos, estado válido y criterios.
- [ ] Con BMAD: `bmad.py backlog` al día, columnas de gobierno completas, cambios de prioridad traspasados (`handoff`), nada copiado.
- [ ] Must dentro de la capacidad; tolerancia de alcance propuesta; release plan solo con línea base.
- [ ] Swaps registrados con `nivel=product-owner`; cambios mayores en `pm-issues-cambios`.
- [ ] EVM ágil con `--modo agil` e ítems terminados según DoD.
- [ ] Retro con 1–3 acciones con dueño y fecha; ninguna escritura externa sin confirmación.

## Escalamiento y excepciones
- Velocidad que no cubre los Must en la etapa → excepción vía `pm-progreso-reportes` y `pm-director`.
- Alcance que desplaza un Must o desvío del PRD → `pm-issues-cambios`.
- Gate de sprint planning de BMAD en CONCERNS/FAIL → `pm-plan-etapa-y-limites` como riesgo o condición de la puerta.
- Como subagente: decisiones humanas (DoD, swaps fuera de tolerancia) en el bloque de retorno (SPEC §1.11), no se preguntan.

## Ejemplos de invocación
- "Armá el backlog de la etapa 2 con MoSCoW y releases, y las historias de las dos primeras iteraciones."
- "El PO quiere cambiar la historia de exportar PDF por la de filtros: ¿hace falta solicitud de cambio?"
- EN: "Create the MoSCoW backlog using the minimal agile profile; we have no WBS."
- EN: "Run agile EVM for sprint 6: we are on budget but behind on points."
- No activa: "Sincronizá el backlog con las historias de BMAD" → `pm-bmad-puente`.

## EN summary
Agile and hybrid delivery inside PRINCE2 stages: cadence and PO (recorded by pm-director), DoD/DoR, one ordered MoSCoW backlog, release plan baseline, sprints as work packages, PO swaps within scope tolerance, agile EVM and iteration retrospectives. Specification data is read only through `especificacion.py`; with BMAD, rows come from `bmad.py backlog` (governance columns kept), priority changes reach BMAD only via `bmad.py handoff`, and the BMAD sprint-planning readiness result feeds `autorizar-etapa`. Must items not fitting is an exception for the board.
