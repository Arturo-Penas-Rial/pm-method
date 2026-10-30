---
name: pm-puerta
description: "Prepara una puerta de decisión de la junta: productos requeridos, verificación BMAD y solicitud de decisión. Uso manual: /pm-puerta <tipo> [carpeta]. Prepare a gate."
disable-model-invocation: true
argument-hint: "autorizar-inicio|autorizar-proyecto|autorizar-etapa|autorizar-plan-excepcion|autorizar-cierre|decision-ad-hoc [carpeta]"
version: 2.7.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: direccion
    agente: pm-director
    procesos_prince2: [DP, SB, CP]
    practicas_prince2: [business-case, plans, progress]
    tecnicas_pmbok: []
    artefactos: [solicitud-<puerta>]
    idiomas: [es, en]
---

# Preparar puerta · Prepare a gate

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- El usuario escribe `/pm-puerta <tipo>` antes de una reunión de junta. EN: user-invoked gate preparation.

## Idioma
Idioma de `estado.json` o del usuario.

## Conocimiento
`pm-direccion-decisiones` (solicitud de decisión), `pm-exportar` (paquete), `pm-bmad-puente` (verificar, traspasos), `pm-estado-proyecto` (fachada `especificacion.py`), `SPEC.md` §1.10.4 y §1.16.

## Entradas requeridas
Tipo de puerta (si falta, deducirlo de `estado.py siguiente`); carpeta con `estado.json`. Datos de especificación solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar …` (fuente única, con o sin BMAD; nunca abrir BMAD ni `requisitos.md`).

## Procedimiento
Scripts en `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/` (manual/Hermes: `~/.claude/skills/…` o `~/.hermes/skills/…`).
0. **Sanidad**: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/sanidad.py --proyecto <dir> --informe` (`pm-sanidad`). Con algún ERROR no se presenta la puerta, salvo que el humano decida seguir: entonces el ERROR queda como condición (`--condiciones`) y en `decisiones.csv`.
1. `python3 ${CLAUDE_SKILL_DIR}/../pm-exportar/scripts/paquete.py --proyecto <dir> listar puerta <tipo>` (o `listar cierre`): obligatorios presentes, en `aprobado` o `en-revision`; faltantes o en borrador = bloqueantes. **Verificación:** `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/puertas.py --proyecto <dir> verificar <tipo>` (bloqueos, condiciones, avisos) y `puertas.py lista <tipo>` (lista de control de la junta; la confirma una persona, vía pm-director).
2. **Especificación**: `especificacion.py --proyecto <dir> resumen` (cobertura y requisitos sin historia para la etapa que se autoriza). Si hay BMAD: `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> verificar` y el gate de preparación del sprint planning como insumo; desvío no traspasado → issue `solicitud-cambio`.
   **Traspasos pendientes** (`estado.json.integraciones.bmad.handoffs` sin confirmar): se informan en la solicitud; con alguno pendiente no se propone nueva línea base de la especificación.
3. Delegar en `pm-director` la solicitud de decisión (`00-direccion/decisiones/<fecha>-solicitud-<tipo>.md`, `en-revision`): justificación continua, estado de productos, riesgos e issues clave, desempeño contra tolerancias, opciones y recomendación.
4. **Presentar la decisión al humano** con opciones (aprobar, condicionar, rechazar, pedir información, cierre prematuro) y quién decide. Sin respuesta explícita, no se registra nada.
5. Tras la decisión: solo `pm-director` ejecuta `estado.py puerta <tipo> --decision … --por "<rol: nombre>" [--motivo ".."]` y `estado.py aprobar`, y fija la línea base BMAD si corresponde. `estado.py puerta` congela antes el tablero (estado previo a la decisión) en `03-control/reportes/tableros/`; si falla, la puerta se registra igual con un aviso. Para la junta: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/tablero.py --proyecto <dir> generar --html <ruta>` (tablero estático) y `tablero.py --proyecto <dir> comparar <id> actual` (qué cambió desde la puerta anterior; ids con `tablero.py --proyecto <dir> listar`). ZIP opcional con `paquete.py puerta <tipo>`.
6. **Cierre prematuro** (la junta no autoriza el proyecto, rechaza una etapa o un plan de excepción, u ordena cerrar): `estado.py cierre --prematuro --decision D-###` con la D-### del rechazo o de la `decision-ad-hoc` (desde la iniciación o la entrega; en el pre-proyecto, `autorizar-inicio` rechazado). En `autorizar-cierre`, C-08 exige `inventario-cierre-prematuro` y C-07 es aviso (`docs/PUERTAS.md` §3.2). Un plan de excepción para rescatar productos o dejarlos en estado seguro se autoriza en CP con `autorizar-plan-excepcion` (el proyecto sigue en CP); C-09 bloquea `autorizar-cierre` hasta `estado.py cierre --plan-excepcion completado|cerrado --por "<rol: nombre>"` (pm-director).

## Reglas del método
1. [PRINCE2] La junta decide; el agente prepara. 2. Solo `pm-director` registra puertas. 3. Un obligatorio faltante bloquea la puerta. 4. Cada puerta se verifica en tres capas: salud, controles automáticos (PRINCE2 y BMAD) y lista de control confirmada por la junta (`docs/PUERTAS.md`).

## Artefactos y plantillas
`solicitud-<puerta>` (plantilla de `pm-direccion-decisiones`); ZIP en `exportados/` si se pide.

## Calidad
- [ ] Lista de obligatorios sin faltantes; opciones con consecuencias; decisor identificado.
- [ ] `especificacion.py resumen` citado; `bmad.py verificar` limpio o desvíos como issues; traspasos pendientes informados.

## Escalamiento y excepciones
Productos faltantes → agente de fase que los produce. Business case insostenible → recomendar parar o replantear.

## Ejemplos de invocación
- `/pm-puerta autorizar-etapa` · `/pm-puerta autorizar-cierre ./turnos` · EN: `/pm-puerta autorizar-proyecto` · No aplica a "¿qué sigue?" → `/pm-estado`.

## EN summary
User-invoked gate preparation: checks required products with paquete.py listar, runs `especificacion.py resumen` and `bmad.py verificar`, reports pending handoffs, has pm-director draft the decision request and presents options to the human; only pm-director records the gate after an explicit decision.
