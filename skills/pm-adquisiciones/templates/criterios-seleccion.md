---
tipo: criterios-seleccion
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Criterios de selección de proveedores · Source selection criteria — {{id_adquisicion}} {{nombre_adquisicion}}

> Borrador generado con apoyo de IA. Una vez aprobada, esta planilla se congela antes de recibir ofertas y se conserva como evidencia de evaluación justa. / AI-assisted draft. Once approved, this sheet is frozen before offers arrive and kept as evidence of fair evaluation.

## 1. Marco de evaluación / Evaluation framework

**Método de selección publicado / Published selection method:** {{metodo_seleccion}}
*El mismo que figura en la estrategia y en los documentos de licitación.*

**Escala de calificación / Rating scale:** {{escala}}
*1–5 (habitual) o 1–10; cada nivel tiene descriptor observable por criterio.*

**Evaluadores / Evaluators:** {{evaluadores}}
*Nombres y roles; califican de forma independiente antes de consolidar; declaran conflictos de interés.*

**Regla de consolidación / Consolidation rule:** {{regla_consolidacion}}
*Promedio simple, mediana u otra; declarada antes de evaluar.*

**Regla de desempate / Tie-break rule:** {{regla_desempate}}
*P. ej. mayor puntaje en el criterio de mayor peso; luego menor costo del ciclo de vida.*

**Fecha de congelamiento / Freeze date:** {{fecha_congelamiento}}
*Fecha de aprobación; posterior a ella no se modifican criterios ni pesos.*

## 2. Criterios eliminatorios / Pass-fail criteria

| Requisito / Requirement | Evidencia exigida / Required evidence | Fuente del requisito / Source |
|---|---|---|
| {{eliminatorio_1}} | {{evidencia_elim_1}} | {{fuente_elim_1}} |

*Requisitos mínimos sin los cuales la propuesta no se evalúa (certificaciones, solvencia, cumplimiento legal). Se definen antes de abrir ofertas.*

## 3. Criterios ponderados y descriptores / Weighted criteria and rating descriptors

| Criterio / Criterion | Peso % / Weight % | Fuente (requisito o estrategia) / Source | Nivel 1 / Level 1 | Nivel 3 / Level 3 | Nivel 5 / Level 5 |
|---|---|---|---|---|---|
| {{criterio_1}} | {{peso_1}} | {{fuente_1}} | {{desc1_1}} | {{desc3_1}} | {{desc5_1}} |
| {{criterio_2}} | {{peso_2}} | {{fuente_2}} | {{desc1_2}} | {{desc3_2}} | {{desc5_2}} |
| {{criterio_3}} | {{peso_3}} | {{fuente_3}} | {{desc1_3}} | {{desc3_3}} | {{desc5_3}} |
| **Total / Total** | **100** | | | | |

*Catálogo orientativo: capacidad instalada, costo del producto y del ciclo de vida, fechas de entrega, pericia técnica, experiencia relevante, enfoque y plan de trabajo, equipo clave, estabilidad financiera, experiencia de gestión, transferencia de conocimiento, sostenibilidad, contenido local. Los niveles 2 y 4 se interpolan o se describen en anexo. A mayor riesgo, más peso a calidad.*

## 4. Evaluación de propuestas / Proposal evaluation

| Criterio / Criterion | Peso / Weight | {{candidato_a}} calif. / rating | {{candidato_a}} puntaje / score | {{candidato_b}} calif. / rating | {{candidato_b}} puntaje / score | {{candidato_c}} calif. / rating | {{candidato_c}} puntaje / score |
|---|---|---|---|---|---|---|---|
| {{criterio_1}} | {{peso_1}} | {{a_calif_1}} | {{a_punt_1}} | {{b_calif_1}} | {{b_punt_1}} | {{c_calif_1}} | {{c_punt_1}} |
| {{criterio_2}} | {{peso_2}} | {{a_calif_2}} | {{a_punt_2}} | {{b_calif_2}} | {{b_punt_2}} | {{c_calif_2}} | {{c_punt_2}} |
| **Total / Total** | 100 | | {{a_total}} | | {{b_total}} | | {{c_total}} |
| **Total normalizado % / Normalized %** | | | {{a_norm}} | | {{b_norm}} | | {{c_norm}} |

*Puntaje = peso/100 × calificación; total = suma de puntajes; total normalizado = total / calificación máxima × 100. Calificaciones consolidadas según la regla de la sección 1.*

**Justificación de calificaciones extremas / Rationale for extreme ratings:** {{justificacion_extremos}}
*Toda calificación 1 o 5 (o mínima/máxima) lleva una frase con la evidencia de la propuesta.*

**Propuestas descartadas por criterios eliminatorios / Proposals excluded by pass-fail:** {{descartadas}}
*Candidato y requisito incumplido.*

## 5. Resultado y recomendación / Result and recommendation

**Ranking / Ranking:** {{ranking}}
*Orden final con totales; aplicar la regla de desempate si corresponde.*

**Recomendación / Recommendation:** {{recomendacion}}
*Candidato recomendado y condiciones a negociar (precio, plazos, propiedad intelectual, equipo clave).*

**Decisión de adjudicación / Award decision:** {{decision_adjudicacion}}
*Quién decide (compras, ejecutivo, junta), fecha y D-nnn. La recomendación no es la adjudicación.*

## Lista de verificación / Checklist
- [ ] Pesos suman exactamente 100 %.
- [ ] Cada criterio con descriptor observable por nivel y fuente en requisitos o estrategia.
- [ ] Criterios eliminatorios definidos antes de abrir propuestas.
- [ ] Método de selección coincide con el publicado en los documentos de licitación.
- [ ] Evaluadores independientes, sin conflictos de interés declarados sin resolver.
- [ ] Planilla congelada antes de recibir ofertas (fecha registrada).
- [ ] Calificaciones extremas justificadas; descartes documentados.
- [ ] Adjudicación registrada como decisión humana con D-nnn.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
