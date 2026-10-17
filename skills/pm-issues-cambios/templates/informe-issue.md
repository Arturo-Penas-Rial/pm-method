---
tipo: informe-issue
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Informe de issue · Issue report

**Identificador / Issue id:** {{id_issue}}
*El mismo `I-###` de `issues.csv`; solo los issues que requieren análisis detallado o decisión formal tienen informe.*

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}} · **Paquete de trabajo / Work package:** {{paquete_trabajo}}

**Fecha de planteo / Date raised:** {{fecha_planteo}} · **Planteado por / Raised by:** {{autor_issue}}

**Tipo / Type:** {{tipo}}
*Uno de: problema-preocupacion, evento-externo, oportunidad-negocio, solicitud-cambio, fuera-especificacion. Verificado que no es un riesgo (ya ocurrió o es seguro).*

**Prioridad / Priority:** {{prioridad}} · **Severidad / Severity:** {{severidad}}
*Escalas del enfoque de gestión de issues; pueden revisarse tras el análisis o confirmarse con la junta.*

**Responsable del issue / Issue owner:** {{responsable}}

**Productos afectados / Products affected:** {{productos_afectados}}
*Ids del PBS/WBS y versión de línea base.*

## 1. Descripción / Description

**Qué ocurre y desde cuándo / What is happening and since when:** {{descripcion}}

**Origen y causa raíz / Origin and root cause:** {{causa_raiz}}
*Usar cinco porqués o causa-efecto; "retraso" o "falta de tiempo" son síntomas, no causas.*

**Evidencia / Evidence:** {{evidencia}}
*Checkpoint, registro de calidad (Q-###), correo, medición.*

## 2. Análisis de impacto / Impact analysis

| Objetivo / Objective | Impacto / Impact | Cuantificación / Quantification | Tolerancia de etapa / Stage tolerance | Pronóstico vs. tolerancia / Forecast vs. tolerance |
|---|---|---|---|---|
| Beneficios / Benefits | {{imp_beneficios}} | {{cuant_beneficios}} | {{tol_beneficios}} | {{pron_beneficios}} |
| Tiempo / Time | {{imp_tiempo}} | {{cuant_tiempo}} | {{tol_tiempo}} | {{pron_tiempo}} |
| Costo / Cost | {{imp_costo}} | {{cuant_costo}} | {{tol_costo}} | {{pron_costo}} |
| Calidad / Quality | {{imp_calidad}} | {{cuant_calidad}} | {{tol_calidad}} | {{pron_calidad}} |
| Alcance / Scope | {{imp_alcance}} | {{cuant_alcance}} | {{tol_alcance}} | {{pron_alcance}} |
| Sostenibilidad / Sustainability | {{imp_sostenibilidad}} | {{cuant_sostenibilidad}} | {{tol_sostenibilidad}} | {{pron_sostenibilidad}} |
| Riesgo / Risk | {{imp_riesgo}} | {{cuant_riesgo}} | {{tol_riesgo}} | {{pron_riesgo}} |

*"Sin impacto" se escribe explícitamente. Pronóstico: `dentro`, `en-alerta` (consume más del 50 % de la tolerancia, regla del paquete), `fuera`. Si alguna fila queda `fuera`, este informe se acompaña de un informe de excepción.*

**Impacto sobre el caso de negocio / Business case impact:** {{impacto_caso_negocio}}

**Impacto sobre otros productos y paquetes / Impact on other products and work packages:** {{impacto_otros}}

**Impacto sobre el perfil de riesgo / Risk profile impact:** {{impacto_riesgos}}
*Riesgos nuevos, agravados o retirados (R-###).*

**Impacto sobre tolerancias de proyecto / Project tolerance impact:** {{impacto_tolerancias_proyecto}}

## 3. Opciones / Options

| Opción / Option | Descripción / Description | Ventaja / Benefit | Impacto de implementación (costo, duración, riesgo) / Implementation impact | Dentro de autoridad de / Within authority of |
|---|---|---|---|---|
| A | {{opcion_a}} | {{ventaja_a}} | {{impacto_a}} | {{autoridad_a}} |
| B | {{opcion_b}} | {{ventaja_b}} | {{impacto_b}} | {{autoridad_b}} |
| No hacer nada / Do nothing | {{opcion_nada}} | {{ventaja_nada}} | {{impacto_nada}} | {{autoridad_nada}} |

*Para fuera de especificación: una opción de concesión (aceptar y actualizar la línea base) y una de corrección (presupuesto de cambio, plan de excepción o remedio contractual). Para solicitud de cambio: enlazar la solicitud `C-###`.*

## 4. Recomendación / Recommendation

**Opción recomendada / Recommended option:** {{recomendacion}}

**Razones / Rationale:** {{razones}}

**Consecuencias de aprobar / If approved:** {{consecuencias_aprobar}}
**Consecuencias de rechazar / If rejected:** {{consecuencias_rechazar}}

**Consejo solicitado a la junta / Advice requested from the board:** {{consejo_junta}}
*Opcional: confirmar prioridad o severidad antes de completar las opciones.*

## 5. Decisión / Decision

**Nivel que decide / Deciding level:** {{nivel_decision}}
*Gestor del proyecto (acción correctiva dentro de tolerancia), autoridad de cambio, junta, capa de negocio.*

**Decisión / Decision:** {{decision}}
*Para fuera de especificación aceptado: "concesión" y resumen de lo aceptado. Vacía hasta el acto humano.*

**Decidido por / Decided by:** {{decidido_por}} · **Fecha / Date:** {{fecha_decision}} · **Registro / Decision log:** {{id_decision}}

**Acción correctiva y responsable / Corrective action and owner:** {{accion_correctiva}}
*Paquete de trabajo nuevo o enmendado; fecha comprometida.*

**Registros a actualizar / Records to update:** {{registros_actualizar}}
*`issues.csv` (decision, estado, fecha_cierre), `cambios.csv` si aplica, versión del producto, descripción de producto (obligatoria en concesión), plan de etapa, `riesgos.csv`, `lecciones.csv`.*

**Informe de excepción asociado / Linked exception report:** {{id_excepcion}}
*Solo si el pronóstico sale de tolerancia de etapa o proyecto.*

## Lista de verificación / Checklist
- [ ] Tipo único verificado y prueba de certeza superada.
- [ ] Causa raíz identificada (no síntoma) con evidencia.
- [ ] Impacto sobre los siete objetivos, caso de negocio, otros productos y perfil de riesgo; pronóstico comparado con tolerancias.
- [ ] Más de una opción, incluida "no hacer nada", con ventaja, impacto y nivel de autoridad.
- [ ] Recomendación con consecuencias de aprobar y de rechazar; concesión o corrección explícita en fuera de especificación.
- [ ] Decisión, decisor, fecha y `D-###` registrados; acción correctiva con responsable y fecha.
- [ ] Si alguna dimensión sale de tolerancia: informe de excepción enlazado.
- [ ] Cifras sin fuente marcadas `[por confirmar]`.
