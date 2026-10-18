---
name: pm-riesgos
description: "Registro y respuestas de riesgo PRINCE2. Usar: riesgo, risk register, matriz P×I, EMV, respuesta al riesgo, oportunidad, informe o auditoría de riesgos. No: issue ya ocurrido→pm-issues-cambios."
version: 2.2.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [SU, IP, CS, MP, SB, CP]
    practicas_prince2: [risk, business-case, progress]
    tecnicas_pmbok: [matriz probabilidad-impacto, valor monetario esperado, árbol de decisiones, Monte Carlo, pre-mortem, auditoría de riesgos]
    artefactos: [candidatos-riesgo, riesgos.csv, evaluacion-probabilidad-impacto, hoja-riesgo, informe-riesgos, auditoria-riesgos]
    idiomas: [es, en]
---

# Gestión de riesgos · Risk management

## Cuándo usar / When to use
- Identificar amenazas u oportunidades (taller, pre-mortem, checkpoint, revisión de supuestos).
- Evaluar un riesgo (probabilidad, impacto, proximidad), ubicarlo en la matriz y decidir si se escala.
- Planificar respuestas con propietario y ejecutor; calcular EMV y controlar el presupuesto de riesgo frente al apetito y la tolerancia.
- Producir la escala P-I, una hoja de datos de riesgo, el informe de riesgos o una auditoría.
- EN: capture, assess and place a threat or opportunity on the P×I matrix.
- EN: plan, cost and assign responses (EMV, risk budget); risk report, data sheet or audit.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. EN la primera vez: risk owner, risk actionee, risk appetite, risk tolerance, risk budget, expected monetary value (EMV), residual risk. Plantillas bilingües; valores de `riesgos.csv` en minúsculas sin acentos.

## Conocimiento
- `references/guia.md` (esta skill): escala y enfoque §1, identificar §2, evaluar §3, respuestas y catálogo §4, monitoreo, presupuesto y escalado §5, comunicar y auditar §6, columnas §7, ágil/BMAD/trackers §8, sesgos §9.
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §2 (procedimiento de cinco pasos, matriz, EMV, respuestas, presupuesto); §7.2 A-09 a A-11; §7.3 A-19; §7.7 A-44.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §12, §13, §25, §31, §37.
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.2 (EMV, árbol, Monte Carlo); §3.3 (P×I); §3.11 familia K.

## Entradas requeridas
- `estado.json`: `tolerancias.*.riesgo` (si vacías, rige la línea por defecto), `tolerancias.*.costo` y `.tiempo`, `roles`, `enfoque_entrega`, `etapa_actual`, `integraciones`.
- Enfoque de riesgo aprobado (`02-planificacion/enfoques/enfoque-riesgo.md`); si no existe, proponer la evaluación P×I (paso 2).
- `03-control/registros/riesgos.csv`, `supuestos.csv`, `issues.csv`, `acciones.csv`, `lecciones.csv`; business case para la tolerancia del proyecto.
- Presupuesto de riesgo de la etapa (`[por confirmar]` si falta).
- **Especificación (fuente única, SPEC §1.16)**: AD-n, NFR y preguntas abiertas solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar requisitos` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: `riesgos.csv`, que cita ids sin copiar texto. Tracker: instantánea vía `pm-integraciones`.

## Procedimiento
1. **Objetivos.** Listar los siete objetivos en riesgo con unidades y tolerancias. Sin objetivos acordados no se registra ningún riesgo.
2. **Escala. PUERTA HUMANA.** Sin enfoque aprobado, redactar `templates/evaluacion-probabilidad-impacto.md` (1–5; alto ≥ 15, medio 6–12, bajo ≤ 5; P → 10/30/50/70/90 %); el ejecutivo la aprueba y se registra con `estado.py aprobar` (`references/guia.md` §1). Hasta entonces, puntuaciones como propuesta.
3. **Identificar** desde las fuentes, no de memoria: `python3 ${CLAUDE_SKILL_DIR}/../pm-riesgos/scripts/riesgos.py --proyecto <dir> candidatos` destila candidatos citados de BMAD (vía pm-bmad-puente), transcripciones, el tracker (Jira) y los artefactos del proyecto (sin BMAD); guía §2. En el taller, formular causa → evento → efecto y registrar con `registro.py agregar riesgos … --campo notas="origen: …"`; lo ocurrido va a `pm-issues-cambios`.
4. **Evaluar** P, I (en unidades del objetivo), proximidad e impacto monetario con `registro.py actualizar riesgos` (recalcula puntuación y EMV; guía §3). Altos sin respuesta o propietario → lista de escalado.
5. **Perfil agregado** con `registro.py resumen --json`; comparar exposición con `tolerancias.*.riesgo`. Si se supera → paso 10.
6. **Planificar respuestas** del catálogo (guía §4), justificadas por EMV antes − EMV residual; residual, secundarios, disparador y contingencia; `templates/hoja-riesgo.md` para riesgos sobre la línea. **PUERTA HUMANA:** el propietario acepta la respuesta y el ejecutor sus acciones; si no, `[por confirmar]`.
7. **Incorporar al plan.** Acción, responsable y fecha en el plan de etapa o paquete; costo al presupuesto de riesgo; cada acción en `acciones.csv` (`--campo origen=R-###`). Si cambia una línea base → `pm-issues-cambios`.
8. **Monitorear** cada período: acciones vencidas, reevaluación, movimientos, disparadores. Materializado → `estado=ocurrido` + issue en `pm-issues-cambios`; retirado con nota (guía §5).
9. **Presupuesto de riesgo:** total, comprometido, usado, remanente, cobertura; su uso lo autoriza quien diga el enfoque (por defecto el ejecutivo), nunca el agente.
10. **Escalar** a la junta vía `pm-director` (criterios en guía §5): `respuesta=escalar`, `estado=escalado`. Si la exposición pronostica superar la tolerancia de etapa, pm-control prepara el informe de excepción con la plantilla de `pm-issues-cambios`.
11. **Comunicar:** sección de riesgos del highlight para `pm-progreso-reportes`; `templates/informe-riesgos.md` cuando se pida (guía §6).
12. **Auditar** en límites de etapa o cierre con `templates/auditoria-riesgos.md`; conclusiones a `lecciones.csv`.
13. **Variante ágil/híbrida:** revisión en cada iteración; `riesgos.csv` sigue siendo la fuente; un riesgo sobre un Must es candidato a excepción (guía §8).
14. **Cerrar** con ids, exposición antes/después, riesgos sobre la línea y su escalado, presupuesto remanente y decisión pendiente con rol; como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; en ágil o híbrido la cadencia de riesgos sigue las iteraciones dentro de la etapa, con revisión en cada límite de etapa.
2. [PRINCE2] Exposición o respuesta que pronostique superar una tolerancia → excepción a `pm-director`; nunca se baja la puntuación para absorberla.
3. [PRINCE2] Nada aprobado sin acto humano registrado: escalas (ejecutivo), respuestas (propietario), presupuesto de riesgo (autoridad del enfoque), escalados (junta), en `decisiones.csv`.
4. [PRINCE2] Primero los objetivos; causa → evento → efecto; impacto en unidades del objetivo para compararlo con la tolerancia.
5. [PRINCE2] Sin incertidumbre no hay riesgo: lo ocurrido es un issue; revisión cruzada riesgos ↔ issues cada período.
6. [PRINCE2] Cada riesgo con propietario (el más capaz) y ejecutor; las respuestas viven en el plan del nivel correspondiente con fecha, responsable y recursos.
7. [PRINCE2] El presupuesto de riesgo financia respuestas y contingencias; no es reserva libre del gestor.
8. [PMBOK→Risk/IP-CS] Técnica según la pregunta: P×I para priorizar, EMV para justificar respuestas y reservas, Monte Carlo solo con datos; declarar escala, fórmula y supuestos.
9. [PMBOK→Risk/CS] EMV = impacto monetario × probabilidad convertida; residual y disparador registrados; contingencia ≠ reserva de gestión (fuera del BAC).
10. [PMBOK→Risk/CS] Oportunidades con procedimiento completo; su ausencia total es señal de sesgo.
11. [Plantillas] Umbrales del paquete alto ≥ 15, medio 6–12, bajo ≤ 5; línea por defecto: ningún alto abierto sin respuesta y propietario; configurables y declarados en cada informe.
12. [Plantillas] Versión mínima (registro + matriz + sección del highlight) para proyectos pequeños; hoja, informe y auditoría si el riesgo lo justifica.
13. Transparencia de IA: puntuaciones del agente como propuesta; montos sin fuente `[por confirmar]`; cada cifra cita `riesgos.csv` e id.
14. Escrituras externas (tracker, correo) solo con confirmación explícita, vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Registro de riesgos | `registro.py` + `pm-registros/templates/guia-registros.md` | `03-control/registros/riesgos.csv` | — (`registro.py resumen`) |
| Evaluación P×I / matriz 5×5 | `templates/evaluacion-probabilidad-impacto.md` | `02-planificacion/enfoques/evaluacion-probabilidad-impacto.md` | `evaluacion-probabilidad-impacto` |
| Hoja de datos de riesgo | `templates/hoja-riesgo.md` | `03-control/registros/R-###-hoja-riesgo.md` | — (referencia en `notas`) |
| Informe de riesgos | `templates/informe-riesgos.md` | `03-control/reportes/<fecha>-informe-riesgos.md` | `informe-riesgos-<fecha>` |
| Auditoría de riesgos | `templates/auditoria-riesgos.md` | `03-control/reportes/<fecha>-auditoria-riesgos.md` | `auditoria-riesgos-<fecha>` |
| Decisiones y acciones de respuesta | `registro.py agregar decisiones` / `agregar acciones` | `03-control/registros/decisiones.csv`, `acciones.csv` | puerta de junta: solo `pm-director` |

Columnas de `riesgos.csv`: `references/guia.md` §7.

## Calidad
- [ ] Objetivos con unidades y tolerancias antes de identificar; escala aprobada o marcada como propuesta.
- [ ] Cada riesgo con causa, evento, efecto, tipo, categoría, propietario y ejecutor.
- [ ] `puntuacion = P × I` y nivel correcto; impacto en unidades del objetivo; proximidad.
- [ ] EMV cuando hay cifra; residual y `disparador` en riesgos con respuesta o contingencia.
- [ ] `sin_respuesta` y `sin_propietario` vacíos para altos, o escalados.
- [ ] Respuestas con acciones fechadas, residual y secundarios evaluados, justificación económica.
- [ ] Exposición comparada con `tolerancias.riesgo`; presupuesto de riesgo con cifras citadas.
- [ ] Ninguna acción vencida sin mención; informe coherente con `riesgos.csv`; oportunidades incluidas; sesgos revisados.

## Escalamiento y excepciones
- Riesgo sobre la línea, que afecta el business case, de programa o cuya respuesta rompería tolerancias → `estado=escalado`, decisión a `pm-director` (junta).
- Exposición que pronostica superar la tolerancia de etapa → informe de excepción (plantilla de `pm-issues-cambios`) con opciones para `pm-director`.
- Respuesta que modifica una línea base → solicitud de cambio vía `pm-issues-cambios`.
- Uso del presupuesto de riesgo sobre la autoridad delegada → autorización del ejecutivo, en `decisiones.csv`.
- Como subagente (pm-control): escala, aceptación de respuestas y escalados van como decisiones humanas en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Hagamos un taller de riesgos para la etapa 2: estos son los objetivos y el plan."
- "Evaluá el riesgo R-012 con probabilidad 4 e impacto 5 y decime si hay que escalarlo."
- EN: "Propose responses for the top three threats and tell me if the mitigation cost is justified by the EMV reduction."
- EN: "Run a risk audit for stage 1: which risks happened and did the responses work?"
- No activa: "Se cayó la API de aduanas ayer y frenó al equipo" → `pm-issues-cambios` (ya ocurrió).

## EN summary
Implements the PRINCE2 five-step risk procedure on `riesgos.csv`: cause → event → effect, threat or opportunity, P×I on an executive-approved scale (high ≥ 15, medium 6–12, low ≤ 5), EMV with 10/30/50/70/90 % mapping, residual and trigger.
Responses come from the full catalogue, are justified by EMV reduction, owned and funded from a risk budget authorized per the risk approach.
Each period it checks overdue actions and matrix movements, turns materialized risks into issues and feeds the highlight; AD/NFR ids read through `especificacion.py` are cited as risk sources.
Breaches go to pm-director; details in references/guia.md.
