---
tipo: solicitud-{{tipo_puerta}}
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
puerta: "{{tipo_puerta}}"
---

# Solicitud de decisión de puerta · Gate decision request

*Ruta / Path: `00-direccion/decisiones/AAAA-MM-DD-solicitud-<puerta>.md` · clave en estado.json / key: `solicitud-<puerta>` (p. ej. `solicitud-autorizar-etapa`). No confundir con el ZIP que arma pm-exportar (`exportado-paquete-<puerta>`), que incluye este documento.*

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Nivel de intervención: asistencia. Requiere revisión del gestor del proyecto y decisión de una persona con rol en la junta. Ninguna cifra sin fuente.

**Proyecto / Project:** {{proyecto}}
*Nombre tal como figura en estado.json.*

**Puerta / Gate:** {{tipo_puerta}}
*Uno de: autorizar-inicio · autorizar-proyecto · autorizar-etapa · autorizar-plan-excepcion · autorizar-cierre · decision-ad-hoc.*

**Etapa que termina / Stage ending:** {{etapa_actual}} · **Etapa que se propone / Stage proposed:** {{etapa_siguiente}}
*Número y nombre según estado.json.etapa_actual. Numeración: 0 = puesta en marcha (pre-proyecto), 1 = iniciación, 2…n = etapas de entrega. En autorizar-inicio: "0 → 1 (iniciación)".*

**Decisión que se pide / Decision requested:** {{decision_solicitada}}
*Una frase, en primer lugar: qué se pide autorizar y a quién. Lo primero que lee el patrocinador.*

**Quién decide / Who decides:** {{quien_decide}}
*Ejecutivo con la junta; capa de negocio si la decisión excede tolerancias de proyecto. Nombre y rol, en el formato que usará `--por` ("Ejecutivo: C. Ruiz").*

**Fecha límite para decidir / Decision due:** {{fecha_limite}}
*Qué pasa si no se decide a tiempo (p. ej. el equipo queda sin paquetes de trabajo autorizados).*

## 1. Justificación continua / Continued business justification

| Pregunta / Question | Respuesta / Answer | Evidencia / Evidence |
|---|---|---|
| ¿Sigue siendo deseable? / Still desirable? | {{deseable}} | {{evidencia_deseable}} |
| ¿Sigue siendo viable? / Still viable? | {{viable}} | {{evidencia_viable}} |
| ¿Sigue siendo alcanzable? / Still achievable? | {{alcanzable}} | {{evidencia_alcanzable}} |

*Responder sí / no / por confirmar y citar ruta y versión del business case y de los registros usados. Si alguna respuesta es "no", la recomendación por defecto es no autorizar.*

**Cambios en el business case desde la última puerta / Changes since last gate:** {{cambios_bc}}
*Beneficios, costos, plazos y exposición agregada al riesgo: valor anterior → valor actual, con fuente.*

## 2. Productos requeridos / Required products

| Producto / Product | Ruta / Path | Versión / Version | Estado / Status | Aprobador / Approver | Bloqueante / Blocking |
|---|---|---|---|---|---|
| {{producto_1}} | {{ruta_1}} | {{version_1}} | {{estado_1}} | {{aprobador_1}} | {{bloqueante_1}} |
| {{producto_2}} | {{ruta_2}} | {{version_2}} | {{estado_2}} | {{aprobador_2}} | {{bloqueante_2}} |

*Una fila por producto exigido para esta puerta (ver tabla en SKILL.md). Estado según estado.json.artefactos. Los productos que esta puerta aprueba pueden venir `en-revision`; un obligatorio que falta o sigue en `borrador` es bloqueante.*

## 3. Desempeño contra tolerancias / Performance against tolerances

| Objetivo / Objective | Tolerancia de etapa / Stage tol. | Pronóstico / Forecast | Tolerancia de proyecto / Project tol. | Semáforo / RAG | Fuente / Source |
|---|---|---|---|---|---|
| Tiempo / Time | {{tol_tiempo}} | {{pron_tiempo}} | {{tol_proy_tiempo}} | {{rag_tiempo}} | {{fuente_tiempo}} |
| Costo / Cost | {{tol_costo}} | {{pron_costo}} | {{tol_proy_costo}} | {{rag_costo}} | {{fuente_costo}} |
| Alcance / Scope | {{tol_alcance}} | {{pron_alcance}} | {{tol_proy_alcance}} | {{rag_alcance}} | {{fuente_alcance}} |
| Calidad / Quality | {{tol_calidad}} | {{pron_calidad}} | {{tol_proy_calidad}} | {{rag_calidad}} | {{fuente_calidad}} |
| Beneficios / Benefits | {{tol_beneficios}} | {{pron_beneficios}} | {{tol_proy_beneficios}} | {{rag_beneficios}} | {{fuente_beneficios}} |
| Riesgo / Risk | {{tol_riesgo}} | {{pron_riesgo}} | {{tol_proy_riesgo}} | {{rag_riesgo}} | {{fuente_riesgo}} |
| Sostenibilidad / Sustainability | {{tol_sost}} | {{pron_sost}} | {{tol_proy_sost}} | {{rag_sost}} | {{fuente_sost}} |

*Comparar el pronóstico, no el valor acumulado. Semáforo del paquete: verde si el desvío previsto consume ≤ 50 % de la tolerancia; ámbar 50–100 %; rojo si la supera (= excepción). Para tiempo y costo, citar la salida de `evm.py --tol-costo --tol-plazo`.*

**Concesiones otorgadas en la etapa / Concessions granted:** {{concesiones}}
*Productos aceptados incompletos, con id de issue y quién lo decidió. "Ninguna" si no hay.*

## 4. Riesgos e issues que necesitan atención / Risks and issues needing attention

| Id | Descripción breve / Short description | Impacto sobre la decisión / Impact on decision | Propietario / Owner |
|---|---|---|---|
| {{id_riesgo_1}} | {{riesgo_1}} | {{impacto_riesgo_1}} | {{prop_riesgo_1}} |
| {{id_issue_1}} | {{issue_1}} | {{impacto_issue_1}} | {{prop_issue_1}} |

*Solo lo que la junta necesita para decidir (gestión por excepción). El resto se consulta en los registros.*

## 5. Opciones y consecuencias / Options and consequences

| Opción / Option | Consecuencias (tiempo, costo, alcance, beneficios, riesgo) / Consequences | Dentro de la autoridad de la junta / Within board authority |
|---|---|---|
| A. Aprobar / Approve | {{cons_aprobar}} | {{aut_aprobar}} |
| B. Aprobar con condiciones / Approve with conditions: {{condiciones_propuestas}} | {{cons_condicionado}} | {{aut_condicionado}} |
| C. Rechazar y pedir replanificación / Reject and request re-planning | {{cons_rechazar}} | {{aut_rechazar}} |
| D. Pedir más información / Request more information: {{informacion_faltante}} | {{cons_mas_info}} | {{aut_mas_info}} |
| E. Cerrar prematuramente / Close prematurely | {{cons_cierre}} | {{aut_cierre}} |

*Cuantificar en unidades del objetivo. Incluir siempre la opción de no autorizar. Eliminar E solo si la puerta es autorizar-inicio (rechazar el inicio no requiere cierre). Pedir más información se registra como `pendiente`. En autorizar-cierre, E se reemplaza por "Cierre con salvedades" si la junta acepta productos incompletos mediante concesión.*

## 6. Recomendación / Recommendation

**Opción recomendada / Recommended option:** {{opcion_recomendada}}
*Letra y enunciado.*

**Justificación / Rationale:** {{justificacion}}
*Tres a cinco líneas que conectan la opción con la justificación continua y las tolerancias.*

**Grado de confianza / Confidence level:** {{confianza}} · **Condiciones / Conditions:** {{condiciones_recomendacion}}
*alta / media / baja, y qué tendría que ser cierto para sostener la recomendación.*

**Supuestos adoptados / Assumptions made:** {{supuestos}}
*Listar y proponer para supuestos.csv.*

## 7. Decisión pendiente de aprobación humana / Decision pending human approval

> Requiere decisión de **{{quien_decide}}**. Este documento no constituye aprobación. Una vez decidido, solo pm-director registra: `estado.py puerta {{tipo_puerta}} --decision aprobado|condicionado|rechazado|pendiente --por "<rol: nombre>" [--condiciones ".."]` (el script escribe la fila de `decisiones.csv`; no duplicarla), `estado.py aprobar <clave> --por ..` por cada documento aprobado, y acta de decisión.

## Lista de verificación / Checklist
- [ ] La decisión que se pide está en la primera línea y cabe en una frase.
- [ ] Las tres preguntas de justificación tienen respuesta y evidencia con ruta y versión.
- [ ] Cada producto requerido tiene estado y aprobador; los bloqueantes están marcados.
- [ ] Pronóstico (no acumulado) contra tolerancias de etapa y de proyecto, con fuente por fila.
- [ ] Al menos tres opciones, incluida no autorizar, con consecuencias cuantificadas.
- [ ] Recomendación con grado de confianza, condiciones y supuestos.
- [ ] Ninguna cifra sin fuente; faltantes marcados `[por confirmar]` con quién la aporta.
- [ ] Versión ejecutiva en una página; detalle en anexos o enlaces a registros.
