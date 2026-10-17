---
tipo: tolerancias-y-autoridad
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
nivel: "{{nivel}}"
---

# Tolerancias y autoridad delegada · Tolerances and delegated authority

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Las tolerancias de proyecto las acuerda la capa de negocio con la junta; las de etapa las fija la junta; las de paquete de trabajo, el gestor del proyecto. Requiere confirmación del ejecutivo antes de escribirse en estado.json.

**Proyecto / Project:** {{proyecto}}
*Nombre según estado.json.*

**Nivel / Level:** {{nivel}}
*proyecto · etapa N · paquete de trabajo WP-xxx. Un documento por nivel o una sección por nivel.*

**Quién fija / Set by:** {{quien_fija}} · **Quién propone / Proposed by:** {{quien_propone}}
*Proyecto: capa de negocio con la junta. Etapa: junta (el gestor propone en el plan de etapa). Paquete: gestor (el gestor de equipo acepta).*

**Vigencia / Valid from–to:** {{vigencia}}
*Fechas de inicio y fin previsto del nivel al que aplican.*

## 1. Tolerancias por objetivo / Tolerances by objective

| Objetivo / Objective | Meta / Target | Tolerancia / Tolerance | Unidad / Unit | Prioridad / Priority | Dónde vive / Lives in | Fuente / Source |
|---|---|---|---|---|---|---|
| Tiempo / Time | {{meta_tiempo}} | {{tol_tiempo}} | días / fecha | {{prio_tiempo}} | plan de {{nivel}} | {{fuente_tiempo}} |
| Costo / Cost | {{meta_costo}} | {{tol_costo}} | moneda o % | {{prio_costo}} | plan de {{nivel}} | {{fuente_costo}} |
| Alcance / Scope | {{meta_alcance}} | {{tol_alcance}} | productos opcionales (ref. PBS) | {{prio_alcance}} | plan de {{nivel}} | {{fuente_alcance}} |
| Calidad / Quality | {{meta_calidad}} | {{tol_calidad}} | rango por criterio | {{prio_calidad}} | descripciones de producto | {{fuente_calidad}} |
| Beneficios / Benefits | {{meta_beneficios}} | {{tol_beneficios}} | rango sobre beneficio | {{prio_beneficios}} | business case / plan de etapa | {{fuente_beneficios}} |
| Riesgo / Risk | {{meta_riesgo}} | {{tol_riesgo}} | exposición agregada | {{prio_riesgo}} | business case / plan de etapa | {{fuente_riesgo}} |
| Sostenibilidad / Sustainability | {{meta_sost}} | {{tol_sost}} | métrica acordada | {{prio_sost}} | business case / plan de etapa | {{fuente_sost}} |

*Expresar en las unidades del objetivo. Prioridad: 1 = la que menos desviación admite. La tolerancia de calidad no se resume por etapa: remitir a las descripciones de producto. "n/a" cuando el nivel no la define.*

**Coherencia hacia arriba / Upward consistency:** {{coherencia}}
*Confirmar que las tolerancias de este nivel caben dentro de las del nivel superior (etapa ⊂ proyecto; paquete ⊂ etapa). Citar los valores del nivel superior desde estado.json.*

## 2. Autoridad delegada / Delegated authority

| Elemento / Element | Valor / Value | Límite / Limit | Quién la ejerce / Exercised by | Decidido por / Decided by |
|---|---|---|---|---|
| Autoridad de cambio / Change authority | {{autoridad_cambio}} | {{limite_autoridad_cambio}} | {{quien_autoridad_cambio}} | {{decidido_autoridad_cambio}} |
| Presupuesto de cambio / Change budget | {{presupuesto_cambio}} | {{limite_presupuesto_cambio}} | {{quien_presupuesto_cambio}} | {{decidido_presupuesto_cambio}} |
| Presupuesto de riesgo / Risk budget | {{presupuesto_riesgo}} | {{limite_presupuesto_riesgo}} | {{quien_presupuesto_riesgo}} | {{decidido_presupuesto_riesgo}} |
| Concesiones (fuera de especificación) / Concessions | {{autoridad_concesiones}} | {{limite_concesiones}} | {{quien_concesiones}} | {{decidido_concesiones}} |

*Qué puede aprobar cada uno sin consultar a la junta y a partir de qué umbral se escala. Si no se delega, escribir "junta" en "quién la ejerce".*

## 3. Reporte y escalado / Reporting and escalation

**Formato y frecuencia de reporte / Report format and frequency:** {{reporte}}
*Highlight report a la junta (frecuencia), checkpoint del gestor de equipo al gestor (frecuencia). Acordados en el mismo acto que las tolerancias.*

**Umbral de alerta temprana / Early-warning threshold:** {{umbral_alerta}}
*Valor configurable; referencia del paquete: verde si el desvío previsto consume ≤ 50 % de la tolerancia, ámbar 50–100 % (se menciona en el próximo informe), rojo fuera de tolerancia (excepción).*

**Cadena de escalado / Escalation chain:** {{cadena}}
*Paquete → gestor del proyecto (issue); etapa → junta (issue report + exception report); proyecto → capa de negocio.*

## 4. Decisión pendiente de aprobación humana / Decision pending human approval

> Requiere confirmación de **{{quien_fija}}**. Tras la confirmación: `estado.py tolerancia --nivel proyecto|etapa ...` (las de paquete de trabajo van en el documento del paquete), `estado.py rol autoridad_cambio="..."` y fila en `decisiones.csv` con nivel `junta` (o `capa-negocio` si son tolerancias de proyecto).

**Confirmado por / Confirmed by:** {{confirmado_por}} · **Fecha / Date:** {{fecha_confirmacion}}
*Nombre y rol; vacío mientras el documento sea borrador.*

## Lista de verificación / Checklist
- [ ] Siete objetivos con tolerancia o "n/a" justificado; ninguno en blanco.
- [ ] Unidades explícitas y coherentes con el plan del nivel.
- [ ] Prioridad relativa definida (qué objetivo manda cuando hay que elegir).
- [ ] Coherencia hacia arriba verificada con los valores del nivel superior.
- [ ] Autoridad de cambio, presupuesto de cambio y de riesgo con límite y titular.
- [ ] Formato y frecuencia de reporte acordados en el mismo acto.
- [ ] Confirmación humana registrada antes de escribir estado.json.
