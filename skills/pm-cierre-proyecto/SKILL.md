---
name: pm-cierre-proyecto
description: "Cierre planificado o prematuro: aceptación, handover, informe final. Usar: cerrar proyecto, cierre prematuro, closeout, end project report. No: lecciones→pm-lecciones-aprendidas."
version: 2.2.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: cierre
    agente: pm-cierre
    procesos_prince2: [CP, DP]
    practicas_prince2: [business-case, quality, risk, issues, progress]
    tecnicas_pmbok: [reseña posterior a la acción, análisis de variaciones, valor ganado, matriz de trazabilidad de requisitos]
    artefactos: [informe-fin-proyecto, recomendaciones-seguimiento, handover, notificacion-cierre, product-status-account-final, registro-aceptacion, plan-revision-beneficios, inventario-cierre-prematuro]
    idiomas: [es, en]
---

# Cierre del proyecto · Closing a project

## Cuándo usar / When to use
- Se acerca el fin de la etapa final y hay que preparar el cierre planificado.
- La junta ordenó un cierre prematuro y hay que cerrar en orden, rescatando valor y dejando los productos en estado seguro.
- EN: planned or premature closure: acceptance, handover, follow-on actions, end project report.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. primera mención con el término EN: informe de fin de proyecto (end project report), recomendaciones de seguimiento (follow-on action recommendations), plan de revisión de beneficios (benefits review plan). Faltante: `[por confirmar]`.

## Conocimiento
- `references/guia.md` (este skill): §1 flujo, §2 preparación, §3 inventario prematuro, §4 aceptación (§4.1 con BMAD), §5 handover y beneficios, §6 fórmulas, §7 informe, §8 cierre de registros, §9 reglas extendidas.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` — `### 5.7` (Closing a project) y `### 5.2` (autorizar el cierre).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` — `### 4.d` (informe de fin de proyecto y de lecciones) y `### 5.4` (cierre de registros).
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` — `## 2.` (beneficios y revisiones post-proyecto) y `## 5.` (aceptación de productos).
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` — `## 35.` (reporte de cierre).

## Entradas requeridas
- `estado.json` con `fase = entrega` (CS o SB de la etapa final) o `fase = cierre` (CP), roles y tolerancias de proyecto. Cierre prematuro: decisión de la junta ya registrada por `pm-director`; si no existe, derivar antes de actuar.
- PID y business case v1.0 (`00-direccion/historial/`) y vigentes; plan con reales; enfoques de beneficios y comunicación.
- Registros (`${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py`), product status account, aceptaciones (`pm-calidad`), informes de fin de etapa, cierres de contrato.
- **Especificación (fuente única, SPEC §1.16)**: cobertura `terminado` por requisito solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar requisitos` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: aceptación e informe final, que citan ids.
- Si falta algo, declararlo; no inventar aceptaciones ni cifras.

## Procedimiento
1. **Situar y elegir ruta**: fin de la etapa final (planificado) o decisión de la junta (prematuro). Entrar a CP con `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> cierre` o `cierre --prematuro` (si pm-director no lo ejecutó); si `fase` ya es `cierre`, no repetir. Resumir con `registro.py resumen` y `listar <registro> --abiertos`.
2. **Preparar** el cierre planificado o el prematuro (inventario por estado y rescate; guía §2–§3).
3. **Confirmar la aceptación**: cruzar product status account, `calidad.csv` y registros de aceptación (guía §4). Aceptación **por requisito** con la cobertura de la fachada (`listar requisitos`); con BMAD, además `bmad.py verificar` limpio y sin traspasos pendientes: cada FR/NFR aceptado, no aceptado o con concesión, citando ids (guía §4.1).
4. **🔒 Puerta humana — aceptación**: el usuario sénior acepta contra los criterios de la descripción del producto del proyecto (dos evidencias); el ejecutivo confirma. `04-cierre/registro-aceptacion.md` `en-revision` y, con ambas confirmaciones escritas, `estado.py aprobar registro-aceptacion --por "Usuario sénior: ..; Ejecutivo: .."`. Como subagente, la confirmación se pide en el bloque de retorno.
5. **Handover, seguimiento y beneficios** (guía §5): `templates/handover.md` (propietario de operación, entregables, límite de cargo de costos); `templates/recomendaciones-seguimiento.md` (cada ítem con destinatario, responsable y fecha); con `pm-caso-de-negocio`, beneficios realizados con fuente y pendientes en `templates/plan-revision-beneficios.md`.
6. **Evaluar** línea base v1.0 vs vigente: tolerancias, variaciones con fórmulas declaradas, concesiones, equipo y método (guía §6).
7. **Contratos y lecciones**: cada contrato con sus tres condiciones de cierre o en seguimiento (`pm-adquisiciones`); retrospectiva final e informe de lecciones (`pm-lecciones-aprendidas`).
8. **Informe de fin de proyecto** con `templates/informe-fin-proyecto.md`, cada cifra con fuente, terminando en la recomendación de cierre (guía §7).
9. **Cerrar registros** con `registro.py actualizar` y estados finales válidos, sin borrar filas (guía §8).
10. **Dejar `en-revision`** (`estado.py artefacto <clave> … --estado en-revision`): `registro-aceptacion`, `handover`, `recomendaciones-seguimiento`, `informe-lecciones`, `plan-revision-beneficios`, `informe-fin-proyecto`, `notificacion-cierre` (borrador). Faltantes: `python3 ${CLAUDE_SKILL_DIR}/../pm-exportar/scripts/paquete.py --proyecto <dir> listar cierre`.
11. **🔒 Puerta humana — autorizar el cierre (la registra `pm-director`)**: derivar a `pm-direccion-decisiones`, que presenta la solicitud y, tras la decisión, registra `puerta autorizar-cierre` (→ `cerrado`). Esta skill no la registra. `condicionado` → completar condiciones; `rechazado` → volver al paso indicado. El ejecutivo notifica (`pm-comunicacion-stakeholders`, con confirmación).
12. **Cerrar la respuesta** con artefactos y estado, huecos declarados, puerta pendiente y rol que decide (o el bloque de retorno, SPEC §1.11); ZIP de cierre con `pm-exportar` si se pide.

## Reglas del método
1. [PRINCE2] Etapas por defecto; en ágil o por fases el cierre confirma los traspasos previos, sin quitar la puerta.
2. [PRINCE2] Desviación fuera de tolerancia → `pm-director`; productos sin aceptación formal → hueco declarado; nada se disimula.
3. [PRINCE2] Nada se da por aprobado sin acto humano registrado: aceptación (usuario sénior + ejecutivo, `estado.py aprobar registro-aceptacion`) y autorización del cierre (`estado.py puerta autorizar-cierre`, solo pm-director).
4. [PRINCE2] Al cerrar se transfiere al negocio, con dueño: riesgos residuales, seguimiento, revisiones de beneficios y datos; el informe compara la línea base original del PID con la vigente.
5. [PRINCE2] En cierre prematuro: inventariar, rescatar valor, dejar en estado seguro (puede requerir plan de excepción), elevar brechas y pedir liberar recursos; el proceso de cierre se ejecuta igual.
6. [PRINCE2] Las revisiones de beneficios post-proyecto se planifican con dueño del negocio y fecha; ejecutarlas no es actividad del proyecto.
7. [PRINCE2] El gestor prepara y recomienda; la junta autoriza y el ejecutivo notifica. Entrada a CP: `estado.py cierre [--prematuro]`; salida: la puerta de pm-director.
8. [PRINCE2] La aceptación cubre cada requisito en línea base según la cobertura de la fachada; un requisito no terminado es concesión o seguimiento, nunca "aceptado".
9. [PMBOK→CP/Progress] Variaciones finales con fórmulas declaradas (tiempo, costo, CPI) y referencia a los cambios que las explican; reseña posterior a la acción sin culpables (guía §6, §9).
10. [Plantillas] Versión mínima de una página o completa según tamaño, contratos o programa; un contrato abierto bloquea el cierre o pasa a seguimiento (guía §9).
11. Transparencia de IA: todo borrador; no inventar aceptaciones, fechas ni cifras; cada cifra cita su fuente.
12. Escrituras externas (notificación, correo, tracker, archivo corporativo) solo con confirmación explícita; si hay chat o tracker conectado, vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla / herramienta | Ruta | estado.json |
|---|---|---|---|
| Product status account final; inventario prematuro | `pm-paquetes-trabajo/templates/product-status-account.md`; guía §3 | `04-cierre/` | `product-status-account-final`, `inventario-cierre-prematuro` |
| Registro de aceptación (por requisito) | `pm-calidad/templates/registro-aceptacion.md` + `especificacion.py` | `04-cierre/registro-aceptacion.md` | `registro-aceptacion` |
| Handover · recomendaciones · plan de revisión de beneficios · informe de fin de proyecto · notificación | `templates/` (`handover.md`, `recomendaciones-seguimiento.md`, `plan-revision-beneficios.md`, `informe-fin-proyecto.md`, `notificacion-cierre.md`) | `04-cierre/<clave>.md` | misma clave |
| Informe de lecciones | `pm-lecciones-aprendidas/templates/informe-lecciones.md` | `04-cierre/informe-lecciones.md` | `informe-lecciones` |
| Cierres de contrato | `pm-adquisiciones/templates/cierre-contrato.md` | `04-cierre/cierre-contrato-<id>.md` | `cierre-contrato-<id>` |
| Entrada a CP / puerta de cierre | `estado.py cierre` / `puerta autorizar-cierre` (pm-director) | `estado.json`, `decisiones.csv` | `cierre`/CP → `cerrado` |

## Calidad
- [ ] Cada producto del PID (y cada FR/NFR, con BMAD) con aceptación, autoridad y fecha, o hueco declarado.
- [ ] Aceptación del usuario sénior con dos evidencias, confirmada por el ejecutivo y registrada.
- [ ] Handover con propietario de operación y fecha límite de cargo de costos.
- [ ] Recomendaciones con destinatario, responsable y fecha; riesgos residuales transferidos.
- [ ] Beneficios pendientes con métrica, línea de base, meta, dueño, fecha y método.
- [ ] Informe con línea base vs vigente, variaciones con fórmula y fuente de cada cifra.
- [ ] Contratos y lecciones cerrados o con dueño; registros cerrados sin borrar filas; puerta derivada a `pm-director`.

## Escalamiento y excepciones
- Producto que no será aceptado o costo/plazo final fuera de tolerancia de proyecto → informe de excepción a `pm-director` antes de recomendar el cierre.
- Cierre prematuro con trabajo de aseguramiento → plan de excepción (`pm-plan-etapa-y-limites`) y `autorizar-plan-excepcion`.
- Usuario sénior que no acepta o condiciona → issue, negociar condiciones, escalar al ejecutivo; no cerrar hasta decidir.
- Contrato en disputa → `pm-adquisiciones`; beneficio sin dueño → ejecutivo.
- Como subagente: aceptación, autorización y envíos se devuelven como "decisiones humanas requeridas" en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Estamos terminando la última etapa del proyecto Faro; prepará el cierre y decime qué falta aceptar."
- "La junta canceló el proyecto. Armá el cierre prematuro con el inventario de productos."
- EN: "Draft the handover and follow-on action recommendations for operations; three issues remain open."
- EN: "We used BMAD: build the requirement-by-requirement acceptance from the traceability matrix."
- No activa: "Facilitá el taller de lecciones de la etapa 3" → `pm-lecciones-aprendidas`.

## EN summary
PRINCE2 Closing a project (planned or premature). Enters CP with `estado.py cierre`, confirms acceptance (per requirement via `especificacion.py` coverage), prepares handover, follow-on actions and benefits review plan, evaluates against the frozen PID and business case, writes the end project report, closes registers and hands the closure recommendation to pm-director, who records `autorizar-cierre` after the board decides.
