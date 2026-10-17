---
tipo: informe-fin-proyecto
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Informe de fin de proyecto · End project report — {{proyecto}}

> Borrador generado con apoyo de IA; cada cifra cita su fuente (registro, EVM, acta, contrato); datos sin fuente aparecen como `[por confirmar]`. Equivale al informe de cierre del proyecto (project closeout report). / AI-assisted draft; every figure cites its source. Equivalent to the project closeout report.

## 1. Cabecera / Header

**Gestor del proyecto / Project manager:** {{gestor_proyecto}}
*Quien prepara el informe.*

**Ejecutivo / Executive:** {{ejecutivo}}
*Quien recibe la recomendación de cierre y notifica a la capa de negocio.*

**Tipo de cierre / Closure type:** {{tipo_cierre}}
*planificado · prematuro (indicar la decisión D-nnn de la junta).*

**Versión del PID de referencia / Baseline PID version:** {{pid_linea_base}} → **Versión vigente / Current version:** {{pid_vigente}}
*El informe compara ambas; todo cambio entre ellas debe estar en cambios.csv.*

**Período del proyecto / Project period:** {{fecha_inicio}} — {{fecha_fin}}
*Fechas de autorización del proyecto y de solicitud de cierre.*

## 2. Resumen ejecutivo / Executive summary

{{resumen_ejecutivo}}
*Cinco a ocho líneas: qué se entregó, cómo quedó frente a tolerancias y business case, qué queda pendiente y qué se recomienda. Sin adjetivos sin evidencia.*

## 3. Descripción del proyecto / Project description

{{descripcion_proyecto}}
*Objetivo, productos principales y alcance acordado en el PID; enfoque de entrega y número de etapas.*

## 4. Revisión de desempeño / Performance review

### 4.1 Contra tolerancias de proyecto / Against project tolerances

| Dimensión / Dimension | Objetivo (PID línea base) / Target (baseline) | Objetivo vigente / Current target | Resultado final / Final result | Variación / Variance | Dentro de tolerancia / Within tolerance | Cambios que lo explican (C-nnn) / Explaining changes | Fuente / Source |
|---|---|---|---|---|---|---|---|
| Tiempo / Time | {{t_base}} | {{t_vigente}} | {{t_final}} | {{t_var}} | {{t_tol}} | {{t_cambios}} | {{t_fuente}} |
| Costo / Cost | {{c_base}} | {{c_vigente}} | {{c_final}} | {{c_var}} | {{c_tol}} | {{c_cambios}} | {{c_fuente}} |
| Alcance / Scope | {{a_base}} | {{a_vigente}} | {{a_final}} | {{a_var}} | {{a_tol}} | {{a_cambios}} | {{a_fuente}} |
| Calidad / Quality | {{q_base}} | {{q_vigente}} | {{q_final}} | {{q_var}} | {{q_tol}} | {{q_cambios}} | {{q_fuente}} |
| Beneficios / Benefits | {{b_base}} | {{b_vigente}} | {{b_final}} | {{b_var}} | {{b_tol}} | {{b_cambios}} | {{b_fuente}} |
| Riesgo / Risk | {{r_base}} | {{r_vigente}} | {{r_final}} | {{r_var}} | {{r_tol}} | {{r_cambios}} | {{r_fuente}} |
| Sostenibilidad / Sustainability | {{s_base}} | {{s_vigente}} | {{s_final}} | {{s_var}} | {{s_tol}} | {{s_cambios}} | {{s_fuente}} |

*Fórmulas declaradas: variación de tiempo % = (fecha real − fecha meta) / duración planificada × 100; variación de costo % = (costo real − BAC) / BAC × 100; CPI final = valor ganado final / costo real si hay EVM. Tolerancias tomadas de estado.json.*

### 4.2 Business case y objetivos / Business case and objectives

{{revision_business_case}}
*¿Sigue justificado el resultado? Costos y beneficios reales frente a los previstos; objetivos del PID alcanzados, alcanzados con cambios aprobados o no alcanzados; métrica del business case usada para juzgar la necesidad de negocio.*

### 4.3 Desempeño del equipo y del método / Team and method performance

{{revision_equipo_metodo}}
*Salud y bienestar del equipo, rotación, relaciones con proveedores; adaptaciones del método que funcionaron o no; fuentes: diario, lecciones, informes de fin de etapa.*

## 5. Revisión de productos / Products review

| Producto / Product | Estado final / Final status | Aceptado por · fecha / Accepted by · date | Concesión u off-specification (I-nnn) / Concession or off-spec | Entregado a / Handed over to |
|---|---|---|---|---|
| {{prod_1}} | {{prod_estado_1}} | {{prod_aceptado_1}} | {{prod_concesion_1}} | {{prod_entregado_1}} |

*Todos los productos del PID; fuente: product status account final y registros de aceptación. En cierre prematuro, añadir columna o nota con la categoría del inventario (aprobado, en desarrollo, con concesión, no iniciado, a asegurar, útil para otros).*

**Aceptación del producto del proyecto / Project product acceptance:** {{aceptacion_producto_proyecto}}
*Usuario sénior, fecha, D-nnn, ruta del registro de aceptación; confirmación del ejecutivo.*

## 6. Riesgos e issues significativos / Significant risks and issues

| Id / Id | Descripción / Description | Respuesta o resolución / Response or resolution | Eficacia / Effectiveness | Estado al cierre / Status at closure |
|---|---|---|---|---|
| {{ri_id_1}} | {{ri_desc_1}} | {{ri_resp_1}} | {{ri_eficacia_1}} | {{ri_estado_1}} |

*Los que afectaron tolerancias o decisiones; riesgos residuales cerrados en riesgos.csv con `notas=transferido a <destinatario>`.*

## 7. Beneficios / Benefits

| Beneficio / Benefit | Previsto / Planned | Realizado a la fecha / Realized to date | Medición y fuente / Measure and source | Pendiente: dueño · fecha · método / Pending: owner · date · method |
|---|---|---|---|---|
| {{ben_1}} | {{ben_prev_1}} | {{ben_real_1}} | {{ben_medicion_1}} | {{ben_pendiente_1}} |

*Enlace al enfoque de gestión de beneficios actualizado; las revisiones post-proyecto son del negocio o del programa.*

## 8. Cierre de adquisiciones / Procurement closeout

| Contrato / Contract | Proveedor / Vendor | Estado / Status | Informe de cierre / Closeout report | Obligaciones posteriores / Post-closure obligations |
|---|---|---|---|---|
| {{contrato_1}} | {{proveedor_1}} | {{contrato_estado_1}} | {{contrato_ruta_1}} | {{contrato_obligaciones_1}} |

*Cerrado (tres condiciones) o en seguimiento con dueño.*

## 9. Lecciones / Lessons

{{resumen_lecciones}}
*Las tres a cinco lecciones prioritarias con destinatario; enlace al informe de lecciones.*

## 10. Recomendaciones de acciones de seguimiento / Follow-on action recommendations

{{resumen_recomendaciones}}
*Resumen por audiencia; enlace al documento completo.*

## 11. Cierre de registros y archivo / Register closure and archiving

| Registro / Register | Abiertos al cierre / Open at closure | Transferidos / Transferred | Cerrado el / Closed on |
|---|---|---|---|
| Riesgos / Risks | {{reg_riesgos_abiertos}} | {{reg_riesgos_transf}} | {{reg_riesgos_fecha}} |
| Issues | {{reg_issues_abiertos}} | {{reg_issues_transf}} | {{reg_issues_fecha}} |
| Cambios / Changes | {{reg_cambios_abiertos}} | {{reg_cambios_transf}} | {{reg_cambios_fecha}} |
| Calidad / Quality | {{reg_calidad_abiertos}} | {{reg_calidad_transf}} | {{reg_calidad_fecha}} |
| Lecciones / Lessons | {{reg_lecciones_abiertos}} | {{reg_lecciones_transf}} | {{reg_lecciones_fecha}} |

**Ubicación del archivo / Archive location:** {{archivo}}
*Dónde queda la carpeta del proyecto para auditoría futura, según el enfoque de datos.*

## 12. Recomendación de cierre / Closure recommendation

{{recomendacion_cierre}}
*Petición formal a la junta de autorizar el cierre, con los huecos declarados y la propuesta de reconocimiento al equipo.*

**Confirmado por aseguramiento / Confirmed by project assurance:** {{aseguramiento}}
*Nombre y fecha.*

**Decisión de la junta / Board decision:** {{decision_junta}}
*aprobado · rechazado · condicionado (condiciones y quién verifica); fecha. La registra solo pm-director con `estado.py puerta autorizar-cierre`; citar el `decision_id` (D-###). Este informe se entrega `en-revision`.*

## Lista de verificación / Checklist
- [ ] Compara la línea base congelada (`00-direccion/historial/pid-v1.0.md`, `business-case-v1.0.md`) con la vigente; cambios referenciados a cambios.csv.
- [ ] Variaciones con fórmula declarada y fuente por cifra.
- [ ] Todos los productos del PID con estado, aceptación y entrega; concesiones visibles.
- [ ] Aceptación del producto del proyecto registrada con D-nnn.
- [ ] Beneficios realizados con medición; pendientes en `04-cierre/plan-revision-beneficios.md` con dueño, fecha y método.
- [ ] Contratos cerrados o en seguimiento con dueño.
- [ ] Riesgos residuales e issues abiertos transferidos; registros cerrados sin borrar filas.
- [ ] Lecciones y recomendaciones de seguimiento enlazadas.
- [ ] Aseguramiento confirmó; decisión de la junta registrada.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
