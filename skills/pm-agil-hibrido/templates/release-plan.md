---
tipo: release-plan
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de release y cadencia · Release plan and cadence

> Borrador generado con asistencia de IA. Se aprueba con el plan de etapa; es dinámico entre iteraciones, fijo dentro de cada una. / AI-assisted draft; approved with the stage plan; dynamic between iterations, frozen within one.

**Etapa / Stage:** {{numero_etapa}} · {{nombre_etapa}} · **Enfoque / Approach:** {{enfoque_entrega}}
*Las releases e iteraciones de este plan viven dentro de la etapa; el fin de la última iteración es el límite de etapa.*

**Dueño del producto / Product owner:** {{dueno_producto}} (estado.json.roles.product_owner) · **Usuario sénior / Senior user:** {{usuario_senior}} · **Equipo / Team:** {{equipo}}
*Quién prioriza, quién acepta, quién entrega.*

## 1. Cadencia y capacidad / Cadence and capacity
- Duración de iteración / Iteration length: {{duracion_iteracion}} días (estado.json.agil.cadencia_iteracion_dias) · Iteraciones en la etapa / Iterations in stage: {{n_iteraciones}}
- Capacidad del equipo por iteración / Team capacity per iteration: {{capacidad}}
- Velocidad histórica (promedio últimas 3) / Historical velocity: {{velocidad}} puntos · Fuente / Source: {{fuente_velocidad}}
- Presupuesto por iteración / Budget per iteration: {{costo_iteracion}} (equipo × período)
*Si no hay velocidad histórica, declarar que las primeras 2–3 iteraciones calibran y usar un rango.*

## 2. Definición de hecho y de listo / Definition of done and ready
**Definición de hecho / Definition of done:**
- [ ] {{criterio_dod}}
*Qué debe cumplir todo ítem para contar como terminado (criterios de aceptación verificados, pruebas, revisión, documentación, desplegable); referenciada desde el enfoque de gestión de la calidad.*

**Definición de listo / Definition of ready:**
- [ ] {{criterio_dor}}
*Qué debe tener un ítem para entrar a una iteración (criterios, estimación, dependencias resueltas, dueño identificado).*

## 3. Releases / Releases
| Release | Objetivo (capacidad para el usuario) / Goal | Iteraciones / Iterations | Fecha objetivo / Target date | Ítems must / Must items | Ítems should-could / Should-could items | Σ puntos / Σ points | Capacidad (velocidad × iteraciones) / Capacity | Cabe / Fits |
|---|---|---|---|---|---|---|---|---|
| R{{n}} | {{objetivo}} | S{{a}}–S{{b}} | {{fecha}} | PB-{{ids}} | PB-{{ids}} | {{puntos}} | {{capacidad}} | sí · no (repriorizar) |
*Objetivo en términos de qué podrá hacer el usuario; los must son el compromiso de la etapa, el resto es tolerancia de alcance; si Σ puntos > capacidad, se repriorizan should/could, no se estira la iteración.*

## 4. Asignación por iteración / Iteration assignment
| Iteración / Iteration | Fechas / Dates | Objetivo / Goal | Ítems / Items | Puntos / Points | Dependencias / Dependencies | Paquete de trabajo / Work package |
|---|---|---|---|---|---|---|
| S{{n}} | {{inicio}} → {{fin}} | {{objetivo}} | PB-{{ids}} | {{puntos}} | {{dependencias}} | W-{{w}} |
*Solo se detalla la iteración próxima y la siguiente; la iteración en curso no se modifica; cada iteración se autoriza como paquete de trabajo en la planificación.*

## 5. Hoja de ruta / Roadmap
```mermaid
gantt
    dateFormat YYYY-MM-DD
    title Releases e iteraciones · etapa {{numero_etapa}}
    section {{equipo_1}}
    S1 {{objetivo_s1}} :s1, {{inicio_s1}}, {{dur}}d
    S2 {{objetivo_s2}} :s2, after s1, {{dur}}d
    section Releases
    R1 {{objetivo_r1}} :milestone, r1, after s2, 0d
    section Puertas / Gates
    Fin de etapa (SB) :milestone, sb, {{fin_etapa}}, 0d
```
*Una sección por equipo o flujo (carriles); releases y fin de etapa como hitos; en híbrido estos hitos se copian al cronograma maestro (cronograma.md).*

## 6. Integración híbrida / Hybrid integration
| Paquete predictivo / Predictive package | Relación con el flujo iterativo / Link to iterative flow | Tipo de dependencia / Dependency type | Hito del cronograma maestro / Master schedule milestone |
|---|---|---|---|
| W-{{w}} | {{relacion}} | FS · SS · externa | {{hito}} |
*Solo en híbrido: dependencias entre camino crítico e iteraciones documentadas y vigiladas.*

## 7. Mapa de ceremonias a controles / Ceremonies to controls map
| Ceremonia / Ceremony | Frecuencia / Frequency | Control del método / Method control | Artefacto o registro / Artifact or register | Participa / Attends |
|---|---|---|---|---|
| Planificación de iteración / Iteration planning | inicio de S# | Autorizar paquete de trabajo (MP) | descripción de paquete, backlog de iteración | gestor de proyecto, equipo, dueño del producto |
| Reunión diaria / Daily | diaria | Punto de control (checkpoint) | tablero, checkpoint report | equipo |
| Revisión / Review | fin de S# | Aceptación de productos; insumo del highlight | registro de productos, calidad.csv, highlight report | usuario sénior, interesados |
| Retrospectiva de iteración / Iteration retrospective | fin de S# | Mejora del equipo; lecciones candidatas | retrospectiva, acciones en backlog o acciones.csv | equipo, PO, facilitador |
| Demo de etapa y taller de lecciones / Stage demo and lessons workshop | última S# de la etapa | Fin de etapa (SB, `limite-etapa`) | informe de fin de etapa, retrospectiva-etapa (pm-lecciones-aprendidas) | junta, equipo |
*Las ceremonias no reemplazan los controles: los alimentan.*

## 8. Línea base de seguimiento / Tracking baseline
**Burn-up planificado / Planned burn-up:**
| Iteración / Iteration | Puntos planificados acumulados / Planned cumulative points | Alcance Must / Must scope | Alcance total de la etapa / Total stage scope | PV acumulado / Cumulative PV |
|---|---|---|---|---|
| S{{k}} | {{puntos_plan_acum}} | {{puntos_must}} | {{puntos_total}} | {{pv_acum}} |
*Es la línea base contra la que se mide: velocidad de referencia × iteración. El PV coincide con linea-base-costo.csv (pm-costos-presupuesto).*

**Dónde se sigue / Where it is tracked:** velocidad real, burn-down de iteración y burn-up de release se dibujan en los informes (`03-control/reportes/`, highlight o tablero de pm-progreso-reportes), no en este documento.
*El release plan solo cambia por replanificación aprobada (nuevo plan de etapa o swap del PO dentro de la tolerancia, registrado con nivel=product-owner).*

**Regla de pronóstico / Forecast rule:** iteraciones restantes ≈ puntos restantes / velocidad promedio (últimas 3); EVM ágil con `evm.py --modo agil`.
*Si los Must no caben en el tiempo o costo de la etapa, es una excepción (informe de excepción → pm-director → junta). Si solo no entran Should/Could, se consume tolerancia de alcance.*

## 9. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Backlog, tablero, registros; cifras [por confirmar].*

## Lista de verificación / Checklist
- [ ] Cadencia, capacidad y número de iteraciones coherentes con el plan de etapa.
- [ ] DoD y DoR acordadas y referenciadas en el enfoque de calidad.
- [ ] Objetivos de release expresados como capacidad para el usuario.
- [ ] Σ puntos ≤ velocidad × iteraciones, o repriorización explícita de should/could.
- [ ] Iteración en curso sin cambios; prioridades iguales al backlog.
- [ ] Dependencias entre historias y con paquetes predictivos identificadas.
- [ ] Releases como hitos del cronograma maestro (híbrido).
- [ ] Mapa de ceremonias a controles completo.
- [ ] Solo línea base de burn-up; los burn charts reales quedan en 03-control/reportes/.
- [ ] Columnas moscow y release del backlog coherentes con este plan.
- [ ] Aprobación pendiente con el plan de etapa (autorizar-etapa).
