---
tipo: informe-lecciones
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Informe de lecciones · Lessons report — {{proyecto}} — {{alcance_informe}}

> Borrador generado con apoyo de IA a partir de lecciones.csv, retrospectivas y registros; cada lección cita su origen. Una lección sin acción y responsable sigue en estado `registrada`. / AI-assisted draft from lecciones.csv, retrospectives and registers; every lesson cites its origin. A lesson without an owned action stays `registrada`.

## 1. Datos del informe / Report data

**Alcance / Scope:** {{alcance_informe}}
*Etapa n, iteraciones x–y, proyecto completo o paquete de trabajo.*

**Organización destinataria / Target organization:** {{destinatario}}
*Negocio, usuario, proveedor, PMO; puede haber un informe por destinatario.*

**Período cubierto / Period covered:** {{periodo}}
*Fechas.*

**Fuentes / Sources:** {{fuentes}}
*lecciones.csv, retrospectivas (rutas), riesgos.csv, issues.csv, cambios.csv, decisiones.csv, calidad.csv, auditorías, cierres de contrato.*

**Integrado en / Embedded in:** {{integrado_en}}
*Informe de fin de etapa, informe de fin de proyecto o emisión independiente.*

## 2. Resumen ejecutivo / Executive summary

{{resumen_ejecutivo}}
*Las tres a cinco lecciones más importantes, con su destinatario y acción, en pocas líneas.*

## 3. Análisis por área de desempeño / Performance area analysis

| Área / Area | Funcionó bien / What worked well | Puede mejorar / What can be improved | Lección (L-nnn) / Lesson |
|---|---|---|---|
| Requisitos / Requirements | {{req_bien}} | {{req_mejorar}} | {{req_l}} |
| Alcance / Scope | {{alc_bien}} | {{alc_mejorar}} | {{alc_l}} |
| Cronograma / Schedule | {{cro_bien}} | {{cro_mejorar}} | {{cro_l}} |
| Costos / Cost | {{cos_bien}} | {{cos_mejorar}} | {{cos_l}} |
| Calidad / Quality | {{cal_bien}} | {{cal_mejorar}} | {{cal_l}} |
| Recursos / Resources | {{rec_bien}} | {{rec_mejorar}} | {{rec_l}} |
| Equipo / Team | {{equ_bien}} | {{equ_mejorar}} | {{equ_l}} |
| Comunicaciones / Communications | {{com_bien}} | {{com_mejorar}} | {{com_l}} |
| Riesgos / Risk | {{rie_bien}} | {{rie_mejorar}} | {{rie_l}} |
| Adquisiciones / Procurement | {{adq_bien}} | {{adq_mejorar}} | {{adq_l}} |
| Interesados / Stakeholders | {{int_bien}} | {{int_mejorar}} | {{int_l}} |
| Procesos y método (etapas, cambios, enfoque híbrido) / Processes and method | {{pro_bien}} | {{pro_mejorar}} | {{pro_l}} |
| Producto / Product-specific | {{prd_bien}} | {{prd_mejorar}} | {{prd_l}} |

*Cada área con al menos una entrada o una justificación de omisión; redactar como recomendación, no como relato.*

## 4. Lecciones específicas / Specific lessons

| Id / Id | Situación o disparador / Trigger | Efecto / Effect | Causa / Cause | Alerta temprana / Early warning | Era riesgo previo (R-nnn) / Was a prior risk | Recomendación / Recommendation | Destinatario / Addressee | Acción · responsable · fecha / Action · owner · date | Estado / Status |
|---|---|---|---|---|---|---|---|---|---|
| {{l_id_1}} | {{l_sit_1}} | {{l_efecto_1}} | {{l_causa_1}} | {{l_alerta_1}} | {{l_riesgo_1}} | {{l_rec_1}} | {{l_dest_1}} | {{l_accion_1}} | {{l_estado_1}} |

*Las cinco preguntas por lección; causa solo si está probada, si no `[por confirmar]`. Estado según lecciones.csv: `registrada`, `revisada`, `accionada-proyecto`, `accionada-organizacion`, `descartada`.*

## 5. Bloques temáticos / Thematic blocks

### 5.1 Riesgos e issues relevantes / Relevant risks and issues

| Id / Id | Descripción / Description | Respuesta / Response | Eficacia / Effectiveness | Lección / Lesson |
|---|---|---|---|---|
| {{ri_id_1}} | {{ri_desc_1}} | {{ri_resp_1}} | {{ri_ef_1}} | {{ri_l_1}} |

### 5.2 Defectos de calidad / Quality defects

| Defecto (Q-nnn / I-nnn) / Defect | Resolución / Resolution | Lección / Lesson |
|---|---|---|
| {{def_1}} | {{def_res_1}} | {{def_l_1}} |

### 5.3 Proveedores / Vendors

| Proveedor · contrato / Vendor · contract | Incidente, reclamo o disputa / Incident, claim or dispute | Resolución / Resolution | Lección / Lesson |
|---|---|---|---|
| {{ven_1}} | {{ven_inc_1}} | {{ven_res_1}} | {{ven_l_1}} |

### 5.4 Desempeño excepcional y áreas de mejora / Exceptional performance and areas for improvement

**Desempeño excepcional / Exceptional performance:** {{excepcional}}
*Qué merece repetirse y reconocerse.*

**Áreas de mejora / Areas for improvement:** {{mejora}}
*Qué debe cambiar en el próximo período o proyecto.*

## 6. Propuestas de mejora a la organización / Organizational improvement proposals

| Lección (L-nnn) / Lesson | Qué cambiar (política, plantilla, proceso) / What to change | Evidencia / Evidence | Beneficio esperado / Expected benefit | Esfuerzo / Effort | Destinatario / Addressee | Próxima oportunidad / Next opportunity | Decisión del ejecutivo (D-nnn) / Executive decision |
|---|---|---|---|---|---|---|---|
| {{org_l_1}} | {{org_cambio_1}} | {{org_ev_1}} | {{org_ben_1}} | {{org_esf_1}} | {{org_dest_1}} | {{org_opp_1}} | {{org_dec_1}} |

*Solo lecciones marcadas con impacto organizacional; el envío a la PMO o al negocio requiere decisión del ejecutivo y confirmación explícita.*

## 7. Lecciones incorporadas al siguiente plan / Lessons incorporated into the next plan

{{lecciones_incorporadas}}
*Ids L-nnn y en qué artefacto se reflejan (plan de etapa, enfoque, descripción de producto, contrato).*

## 8. Confirmación y revisión / Confirmation and review

| Rol / Role | Nombre / Name | Acción / Action | Fecha / Date | D-nnn |
|---|---|---|---|---|
| Aseguramiento del proyecto / Project assurance | {{aseg_nombre}} | Confirma que lecciones y acciones tienen responsable / Confirms owners assigned | {{aseg_fecha}} | {{aseg_dec}} |
| Junta del proyecto / Project board | {{junta_nombre}} | Revisa el informe / Reviews the report | {{junta_fecha}} | {{junta_dec}} |

*Sin estas filas el informe sigue en borrador.*

## Lista de verificación / Checklist
- [ ] Cada área con entrada o justificación de omisión; lecciones redactadas como recomendaciones.
- [ ] Aciertos incluidos, no solo problemas.
- [ ] Cada lección específica responde las cinco preguntas y cita sus registros.
- [ ] Cada lección con destinatario, acción, responsable, fecha y estado.
- [ ] Lecciones organizacionales separadas con evidencia, beneficio, esfuerzo y destinatario.
- [ ] Lecciones incorporadas al plan siguiente identificadas.
- [ ] Aseguramiento confirmó; junta revisó; decisiones registradas.
- [ ] lecciones.csv actualizado con los estados finales.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
