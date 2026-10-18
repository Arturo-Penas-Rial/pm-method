---
name: pm-issues-cambios
description: "Issues, control de cambios e informe de excepción. Usar: issue, solicitud de cambio, change request, off-spec, concesión, desvío del PRD. No: pronóstico o semáforo→pm-progreso-reportes."
version: 2.2.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [CS, MP, SB, DP]
    practicas_prince2: [issues, progress, quality, business-case]
    tecnicas_pmbok: [análisis de impacto, cinco porqués, causa-efecto, análisis de red, análisis multicriterio, gestión de configuración]
    artefactos: [issues.csv, cambios.csv, decisiones.csv, solicitud-cambio, informe-issue, informe-excepcion]
    idiomas: [es, en]
---

# Issues y control de cambios · Issues and change control

## Cuándo usar / When to use
- Alguien plantea un issue (problema, evento externo, oportunidad, solicitud de cambio, fuera de especificación) y hay que capturarlo, clasificarlo y evaluarlo.
- Analizar el impacto de un cambio sobre los siete objetivos, tolerancias y business case, y decidir en el nivel delegado o escalar.
- Redactar solicitud de cambio, informe de issue o informe de excepción; aplicar líneas base y control de configuración.
- Con BMAD: un desvío del PRD o una Sprint Change Proposal detectada por `bmad.py verificar`.
- EN: capture, assess and route an issue or change request; write exception reports; handle BMAD drift.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Términos EN la primera vez: `references/guia.md` (inicio). Valores de `issues.csv` y `cambios.csv` en minúsculas sin acentos (`pm-registros/templates/guia-registros.md`).

## Conocimiento
- `references/guia.md` (esta skill): cinco tipos §1, captura §2, impacto y opciones §3, tabla de autoridad §4, decisiones y sincronización §5, excepción §6, cambio ligero §7, BMAD §8, trackers §9, casos borde §10.
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §3 (tipos, procedimiento, autoridad, presupuesto de cambio, líneas base); §4.a, §4.c.2 y §4.d (excepción); §6 flujo de decisión.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §1 solicitud de cambio; §21; §23; §29.3; §49 regla 18.
- `SPEC.md` §1.13 y §1.16 (línea base, traspaso inverso).

## Entradas requeridas
- `estado.json`: `tolerancias`, `roles.autoridad_cambio`, `roles.ejecutivo`, `roles.product_owner`, `etapa_actual`, `artefactos` (líneas base con versión), `enfoque_entrega`, `integraciones`.
- Enfoque de issues y cambios (`02-planificacion/enfoques/enfoque-issues-cambios.md`): línea base, escalas, delegación por umbral, presupuesto de cambio. Si no existe, valores de referencia declarados.
- Plan de etapa y de proyecto; descripciones de producto afectadas.
- `03-control/registros/issues.csv`, `cambios.csv`, `riesgos.csv`, `decisiones.csv`, `acciones.csv`, `calidad.csv`; esquemas con `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> esquema issues|cambios|decisiones`.
- **Especificación (fuente única, SPEC §1.16)**: ids afectados e historias solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar …` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`); desvíos de `bmad.py verificar`. Escribe como dueña: `issues.csv`, `cambios.csv` (ids en `notas`) y el origen del traspaso. Tracker o chat: instantánea vía `pm-integraciones`.

## Procedimiento
1. **Situar.** Tolerancias, autoridad de cambio, umbral y presupuesto de cambio remanente.
2. **Capturar.** Prueba de certeza (incierto → `pm-riesgos`); exactamente uno de cinco tipos; formal/informal; prioridad y severidad; alta con `registro.py agregar issues` (`references/guia.md` §1–§2). Una tarea no es un issue → `acciones.csv`. Nunca rechazar sin evaluar.
3. **Entrada BMAD.** Cada desvío o Sprint Change Proposal de `bmad.py verificar` entra como `solicitud-cambio` citando ids y sha, salvo elaboración progresiva declarada (guía §8).
4. **Evaluar impacto integrado** sobre los siete objetivos, tolerancias, business case y otros productos; ruta crítica analizada; variación relativa; pronóstico vs. tolerancia (guía §3).
5. **Documentar** (rutas en la tabla de artefactos). Si requiere análisis: `templates/informe-issue.md`. Solicitud de cambio: `templates/solicitud-cambio.md` + fila en `cambios.csv` (`notas=origen I-###`, ids afectados, `costo` y `cargo`: guía §4.1); issue en `pendiente-cambio`.
6. **Recomendar** al menos dos opciones (incluida no hacer nada), con financiación del cambio o concesión/corrección del fuera de especificación (guía §3).
7. **PUERTA HUMANA — Autoridad.** Determinar quién decide con la tabla (guía §4). El agente nunca decide: pide la decisión al PO, gestor, autoridad de cambio o junta. Sin umbral o presupuesto suficiente, subir de nivel; si el pronóstico sale de tolerancia → paso 10.
8. **Registrar la decisión** en `issues.csv`/`cambios.csv` (`decidido_por`) y `decisiones.csv` con nivel; si decidió la junta, la puerta la registra `pm-director` y aquí se copia el `D-###` (guía §5).
9. **Implementar y sincronizar** en la misma operación: registro de cambios, nueva versión del artefacto (`estado.py artefacto` + `aprobar` tras el acto humano), descripción de producto, plan; riesgos nuevos a `pm-riesgos`; acción correctiva vía `pm-paquetes-trabajo`. **Si afecta la especificación**: con BMAD, traspaso inverso `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> handoff --cambio C-###` (sin BMAD, `requisitos.md` lo actualiza `pm-planificacion-por-productos`); tras la confirmación del equipo BMAD, `bmad.py verificar` limpio y pedir a `pm-director` la nueva línea base (versión mayor; guía §8).
10. **Excepción.** Pronóstico fuera de tolerancia sin corrección posible dentro de la autoridad del gestor: aviso temprano + `templates/informe-excepcion.md`, `en-revision`, issue `escalado`; entregar a `pm-director`. **Ninguna puerta se registra aquí** (guía §6).
11. **Tras la decisión de la junta:** tolerancias reasignadas o plan de excepción vía `pm-director` y `pm-plan-etapa-y-limites` (guía §6).
12. **Ágil/híbrido:** intercambios del PO como cambio ligero si cumplen las cuatro condiciones (guía §7); si no, solicitud formal.
13. **Cerrar** con id, tipo, impacto, opciones, nivel que decide y `[por confirmar]`; como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; en ágil o híbrido los cambios de características se absorben en el backlog dentro de la tolerancia de alcance, sin suprimir puertas.
2. [PRINCE2] Desviación prevista fuera de tolerancia → informe de excepción a `pm-director`; nunca se absorbe ni se fragmenta en cambios pequeños.
3. [PRINCE2] Nada aprobado sin acto humano registrado (decisor y nivel en `decisiones.csv`; puerta en `estado.json` si decide la junta).
4. [PRINCE2] Todo issue se captura y evalúa antes de juzgarse, y se clasifica en exactamente uno de cinco tipos.
5. [PRINCE2] Solicitud de cambio y fuera de especificación son siempre formales; la solicitud dice qué productos cambia, por qué y con qué dinero.
6. [PRINCE2] Concesión = cambio de línea base con descripción de producto actualizada; rechazada, se corrige.
7. [PRINCE2] Autoridad delegada exige umbral y presupuesto de cambio; escalado en dos pasos (aviso temprano, informe) respetando la cadena.
8. [PRINCE2] Con BMAD, los desvíos del PRD y las Sprint Change Proposals son solicitudes de cambio decididas por la autoridad PRINCE2; el "sí" de correct-course no aprueba; la nueva línea base la fija `pm-director`.
9. [PMBOK→Issues/CS] Técnica según la pregunta (cinco porqués, causa-efecto, análisis de red, multicriterio); variaciones relativas sobre BAC y duración declaradas.
10. [PMBOK→Issues/CS] Cambio aprobado reflejado en tres lugares en la misma operación: registro de cambios, versión del producto, plan; luego riesgos nuevos.
11. [Plantillas] Umbrales del plan o 5 %/10 % declarados; "diferir" con fecha; causa raíz, no síntoma.
12. Transparencia de IA: documentos en `borrador`; impactos no analizados `[por confirmar]`, nunca "sin impacto" por omisión.
13. Escrituras externas (tracker, correo, chat) solo con confirmación explícita, vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Registro de issues | `registro.py` + `pm-registros/templates/guia-registros.md` | `03-control/registros/issues.csv` | — |
| Registro de cambios | `registro.py` | `03-control/registros/cambios.csv` | versión de la línea base al implementar |
| Solicitud de cambio | `templates/solicitud-cambio.md` | `03-control/reportes/<fecha>-solicitud-cambio-C-###.md` | `solicitud-cambio-C-###` |
| Informe de issue | `templates/informe-issue.md` | `03-control/reportes/<fecha>-informe-issue-I-###.md` | `informe-issue-I-###` |
| Informe de excepción (plantilla única) | `templates/informe-excepcion.md` | `03-control/reportes/<fecha>-informe-excepcion-X-###.md` | `informe-excepcion-X-###` en `en-revision`; puerta solo `pm-director` |
| Decisiones y acciones | `registro.py agregar decisiones` / `agregar acciones` | `03-control/registros/decisiones.csv`, `acciones.csv` | `junta`/`capa-negocio` vía `pm-director` |
| Plan de excepción | vía `pm-plan-etapa-y-limites` | `02-planificacion/plan-excepcion-X-###.md` | `plan-excepcion-X-###` |

## Calidad
- [ ] Tipo (uno de cinco), prioridad, severidad, responsable; prueba de certeza superada.
- [ ] Impacto sobre siete objetivos, tolerancias, business case y otros productos; ruta crítica evaluada.
- [ ] Dos opciones o más con consecuencias de aprobar y rechazar; financiación o concesión/corrección.
- [ ] Nivel de autoridad verificado contra umbral y presupuesto; decisión pedida al rol correcto.
- [ ] Decisión en `issues.csv`/`cambios.csv` y `decisiones.csv`; ninguna puerta registrada aquí.
- [ ] Cambio aprobado sincronizado (versión, descripción de producto, plan); riesgos consultados. Con BMAD: ids citados, traspaso emitido, `verificar` limpio y línea base pedida a `pm-director`.
- [ ] Excepción emitida al pronosticar; lección al cerrar.

## Escalamiento y excepciones
- Pronóstico fuera de tolerancia de etapa → aviso temprano + `X-###` → `pm-director`; de proyecto → capa de negocio vía `pm-director`.
- Cambio fuera del umbral o presupuesto de la autoridad de cambio → `cambios.csv.estado=pendiente-decision` → `pm-director`.
- Issue contractual → `pm-adquisiciones`.
- Desvío BMAD rechazado → el equipo BMAD revierte (`verificar` limpio); aprobado → paso 9.
- Como subagente (pm-control): decisiones de autoridad en el bloque de retorno (SPEC §1.11), no se preguntan.

## Ejemplos de invocación
- "El cliente pide agregar un informe de trazabilidad al portal; armá la solicitud de cambio y decime quién la aprueba."
- "`bmad.py verificar` dice que el PRD tiene dos FR nuevos desde la línea base; ¿qué hacemos?"
- EN: "Raise an issue: the customs broker changed its API contract yesterday and two work packages are blocked."
- EN: "We forecast an 18 % cost overrun against a 10 % stage tolerance. Draft the exception report with options."
- No activa: "¿Cómo viene el CPI de la etapa y qué semáforo le toca?" → `pm-progreso-reportes`.

## EN summary
PRINCE2 issue and change control: certainty test, five issue types, integrated impact across seven objectives, at least two options, and routing to the delegated authority — the agent never decides.
Approved changes are synchronized in one operation; forecast tolerance breaches produce the package's single exception report (X-###) for pm-director, who records gates.
With BMAD, PRD drift and Sprint Change Proposals from `bmad.py verificar` enter as change requests; approved spec changes go back via `bmad.py handoff --cambio C-###`, then `verificar` and a new baseline by pm-director.
