---
tipo: enfoque-issues-cambios
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enfoque de gestión de issues y control de cambios · Issue management and change control approach — {{proyecto}}

> Cómo se capturan y resuelven los issues y cómo se controlan los cambios a la línea base: líneas base, resolución, control de cambios, delegación de autoridad, presupuesto de cambio. Parte del PID; se prepara después de las descripciones de producto y de paquete de trabajo. Mapeo del paquete: ≈ plan de gestión de cambios (change management plan) + gestión de la configuración. / Issue capture and resolution, change control, delegated authority and change budget.

> Nota: aquí "cambio" es control de cambios del proyecto (líneas base y documentos), no gestión del cambio organizacional (adopción por las personas), que vive en su propio enfoque.

**Versión mínima / Minimal version:** {{version_minima}}
*`sí` (una página): una regla por tipo de cambio, quién aprueba, formulario sencillo y bitácora. En ágil (perfil mínimo): el backlog es el mecanismo de cambio; el product owner intercambia ítems dentro de la tolerancia de alcance de la etapa sin solicitud de cambio (decisión `nivel=product-owner` en `decisiones.csv`); fechas de release, presupuesto total y todo lo que desplace un Must pasan por solicitud de cambio.*

## 1. Alcance / Scope

{{alcance}}
*A qué productos, planes y documentos se aplica; cómo se integra con los procedimientos contractuales si hay proveedores externos.*

## 2. Líneas base / Baselines

| Producto o documento / Product or document | Nivel de línea base / Baseline level | Identificador y versión / Id and version | Bajo control desde / Controlled from | Vía (híbrido) / Track (hybrid) |
|---|---|---|---|---|
| {{lb_1}} | {{lb_1_nivel}} | {{lb_1_id}} | {{lb_1_desde}} | {{lb_1_via}} |
| {{lb_2}} | {{lb_2_nivel}} | {{lb_2_id}} | {{lb_2_desde}} | {{lb_2_via}} |
| PID, business case, plan de proyecto, planes de etapa | producto de gestión | versión y fecha de aprobación | puerta correspondiente | — |

*Línea base al nivel de componente independientemente liberable. Cada producto y versión con identificador único en el registro de productos. En híbrido: qué entregables siguen control formal y cuáles evolucionan vía backlog.*

## 3. Tipología y escalas de issues / Issue types and scales

| Tipo / Type (`issues.csv.tipo`) | Significado / Meaning | Decide por defecto / Default decider |
|---|---|---|
| solicitud-cambio / request for change | Propuesta de modificar una línea base | autoridad de cambio o junta según límite (swap dentro de tolerancia en ágil: product owner) |
| fuera-especificacion / off-specification | Producto que no cumple o no cumplirá su especificación | autoridad de cambio o junta (concesión) |
| problema-preocupacion / problem or concern | Situación o pregunta que requiere decisión, respuesta formal o apoyo del gestor | gestor |
| evento-externo / external event | Hecho fuera del proyecto (regulación, mercado, proveedor, organización) que lo afecta | gestor; junta si amenaza tolerancias |
| oportunidad-negocio / business opportunity | Posibilidad de obtener más valor que la prevista en el business case | junta (o capa de negocio si excede el proyecto) |

*Exactamente estos cinco tipos (los valida `registro.py`). Una tarea a cumplir por alguien no es un issue: va a `acciones.csv` (`A-###`). Una incertidumbre futura es un riesgo (`riesgos.csv`).*

**Severidad / Severity (`critica|mayor|menor|informativa`):** {{escala_severidad}}
*Definir cada valor por su efecto: `critica` = amenaza una tolerancia de proyecto o el business case; `mayor` = amenaza una tolerancia de etapa; `menor` = se resuelve dentro de la tolerancia del paquete de trabajo; `informativa` = sin efecto en tolerancias.*

**Prioridad / Priority (`urgente|alta|media|baja`):** {{escala_prioridad}}
*Plazo de atención por valor (p. ej. urgente < 1 día hábil, alta < 1 semana); cómo se combina con severidad para ordenar la cola.*

**Niveles de decisión / Decision levels (`decisiones.csv.nivel`):** `equipo`, `product-owner`, `gestor`, `autoridad-cambio`, `junta`, `capa-negocio`. *La columna `decidido_por` de `issues.csv` y `cambios.csv` nombra a la persona y su rol.*

*Escalas aprobadas por el ejecutivo y usadas tal cual en `issues.csv`. Todo issue se verifica antes para descartar que sea un riesgo (incertidumbre).*

## 4. Procedimiento de resolución de issues / Issue resolution procedure

| Paso / Step | Qué se hace / What is done | Quién / Who | Plazo / Timing |
|---|---|---|---|
| 1. Capturar / Capture | {{p1}} | {{p1_quien}} | {{p1_plazo}} |
| 2. Evaluar / Assess | {{p2}} | {{p2_quien}} | {{p2_plazo}} |
| 3. Recomendar opciones / Recommend | {{p3}} | {{p3_quien}} | {{p3_plazo}} |
| 4. Decidir / Decide | {{p4}} | {{p4_quien}} | {{p4_plazo}} |
| 5. Implementar y verificar / Implement and verify | {{p5}} | {{p5_quien}} | {{p5_plazo}} |

*Captura con mínima carga administrativa por cualquier canal; evaluación integrada sobre los siete aspectos de desempeño, el business case y otros productos; más de una opción cuando sea posible, con consecuencias de aprobar y de rechazar; rechazar es válido; decisiones y acciones en `issues.csv`; cambios aprobados reflejados en productos y en el registro de productos; un issue que llevará la etapa fuera de tolerancia se convierte en excepción (informe de issue → informe de excepción).*

## 5. Definiciones de cambio frente a revisión / Change vs. revision definitions

| Dimensión / Dimension | Es revisión o elaboración (no pasa por control) / Revision | Es cambio (pasa por control) / Change | Umbral / Threshold |
|---|---|---|---|
| Cronograma / Schedule | {{def_cron_rev}} | {{def_cron_cambio}} | {{def_cron_umbral}} |
| Presupuesto / Budget | {{def_pres_rev}} | {{def_pres_cambio}} | {{def_pres_umbral}} |
| Alcance / Scope | {{def_alc_rev}} | {{def_alc_cambio}} | {{def_alc_umbral}} |
| Documentos / Documents | {{def_doc_rev}} | {{def_doc_cambio}} | {{def_doc_umbral}} |

*Umbral concreto por dimensión (p. ej. mover un hito más de dos semanas; aumentar el total; añadir una función no prevista; modificar el acta). Igual a los umbrales del plan de cronograma y costos y del PID.*

### 5.1 Especificaciones BMAD: elaboración progresiva frente a cambio / BMAD specs: progressive elaboration vs. change
*Solo si `estado.json.integraciones.especificacion = bmad`; si no, "no aplica". Rige para artefactos BMAD con línea base (`bmad.py linea-base`); antes de la línea base todo es elaboración. `bmad.py verificar` detecta los desvíos; esta tabla dice cómo se clasifican.*

| Modificación en el artefacto BMAD / BMAD artefact change | Clasificación / Classification | Quién decide / Decided by |
|---|---|---|
| Detallar un FR/NFR existente sin cambiar su id ni su intención (criterios de aceptación, ejemplos, redacción) | {{bmad_elab_detalle}} | {{bmad_elab_detalle_quien}} |
| Descomponer una épica en historias o refinar historias dentro de la épica ya aprobada | {{bmad_elab_historias}} | {{bmad_elab_historias_quien}} |
| Arquitectura: precisar una decisión AD existente sin alterar sus consecuencias de costo, plazo o riesgo | {{bmad_elab_ad}} | {{bmad_elab_ad_quien}} |
| Agregar, retirar o fusionar ids FR/NFR/UJ/SM | {{bmad_cambio_ids}} | {{bmad_cambio_ids_quien}} |
| Cambiar la intención o la meta de un requisito o de una métrica SM-n | {{bmad_cambio_intencion}} | {{bmad_cambio_intencion_quien}} |
| Nueva o modificada decisión AD que afecta tolerancias o un producto aprobado | {{bmad_cambio_ad}} | {{bmad_cambio_ad_quien}} |
| Sprint Change Proposal (correct-course) | {{bmad_scp}} | {{bmad_scp_quien}} |

*Valores por defecto (configurables): las tres primeras filas = elaboración progresiva (registro como decisión `nivel=product-owner` o `equipo`, sin solicitud de cambio, nueva versión menor del artefacto); las cuatro últimas = `solicitud-cambio` en `issues.csv`, decide la autoridad de cambio o la junta según el impacto; el "sí" de BMAD no sustituye esa decisión. Tras aprobar un cambio, `pm-director` fija una nueva línea base con versión mayor. Si la elaboración acumulada mueve el tamaño estimado más allá del umbral de alcance de esta tabla, se trata como cambio.*

## 6. Delegación de autoridad y presupuesto de cambio / Delegated authority and change budget

| Nivel / Level | Quién / Who | Puede aprobar / Can approve | Límite / Limit | Presupuesto de cambio asignado / Change budget allocated |
|---|---|---|---|---|
| Junta / Board | {{junta_quien}} | cualquier cambio; concesiones mayores | tolerancias de proyecto | {{junta_presupuesto}} |
| Autoridad de cambio / Change authority | {{ac_quien}} | {{ac_puede}} | {{ac_limite}} | {{ac_presupuesto}} |
| Gestor de proyecto / Project manager | {{gp_quien}} | {{gp_puede}} | {{gp_limite}} | {{gp_presupuesto}} |
| Gestor de equipo / Team manager | {{ge_quien}} | {{ge_puede}} | {{ge_limite}} | {{ge_presupuesto}} |

*Autoridad delegada sin presupuesto es inútil. El presupuesto puede ser dinero o un conjunto de restricciones dentro de las cuales se admiten intercambios. Asignación por etapa o paquete de trabajo: {{asignacion_etapa}}. Uso informado en el highlight report.*

## 7. Control de cambios y configuración / Change control and configuration management

**Solicitud / Request:** {{solicitud}}
*Quién puede presentar, formulario o campos mínimos (productos afectados, razón, financiación: presupuesto de cambio o fondos adicionales), quién recibe.*

**Seguimiento / Tracking:** `03-control/registros/cambios.csv` — estados `abierto` → `en-evaluacion` → `pendiente-decision` → `aprobado` | `rechazado` | `diferido` → `implementado` → `cerrado`; decisión `aprobado|rechazado|diferido|pedir-plan-excepcion|pedir-mas-informacion`; incluir `impacto_beneficios`.
*Cada solicitud con identificador, fecha, estado y decisión; vínculo al issue de origen.*

**Disposición y comunicación / Disposition and communication:** {{disposicion}}
*Plazo para comunicar la decisión al solicitante; qué se actualiza tras aprobar (líneas base, planes, registro de productos, PID si corresponde).*

**Fuera de especificación / Off-specification:** {{fuera_especificacion}}
*Aceptar = concesión (cambia la línea base); rechazar = corrección vía presupuesto de cambio, plan de excepción o remedio contractual.*

**Gestión de la configuración / Configuration management:** {{configuracion}}
*Nomenclatura y versionado, dónde vive cada producto, auditorías de configuración (fin de etapa y cierre) para verificar que el estado real coincide con el autorizado. Ningún sistema debe permitir cambios sin la aprobación requerida y sin pista de auditoría.*

## 8. Cadencia y actividades formales / Cadence and formal activities

{{cadencia}}
*Revisión de issues abiertos en todas las revisiones del proyecto (no opcional); sesiones de la autoridad de cambio; vigilancia del entorno externo (quién) si regulación o sostenibilidad son relevantes.*

## 9. Responsabilidades / Responsibilities

| Rol / Role | Responsabilidad / Responsibility |
|---|---|
| Ejecutivo / Executive | {{resp_ejecutivo}} |
| Junta / Board | {{resp_junta}} |
| Autoridad de cambio / Change authority | {{resp_autoridad_cambio}} |
| Gestor de proyecto / Project manager | {{resp_gestor}} |
| Gestores de equipo / Team managers | {{resp_gestores_equipo}} |
| Aseguramiento / Assurance | {{resp_aseguramiento}} |
| Soporte / Support | {{resp_soporte}} |

## 10. Herramientas, estándares y referencias / Tools, standards and references

{{herramientas_referencias}}
*Sistema de control de versiones, tracker (solo con confirmación para escrituras externas), formato de `issues.csv` y `cambios.csv`, procedimiento corporativo, cláusulas contractuales de cambio.*

## Lista de verificación / Checklist
- [ ] Líneas base definidas sin ambigüedad y a nivel liberable; híbrido: control formal vs. backlog.
- [ ] Los cinco tipos canónicos de issue; severidad `critica|mayor|menor|informativa` y prioridad `urgente|alta|media|baja` definidas y aprobadas por el ejecutivo.
- [ ] En ágil: regla de swap del product owner dentro de la tolerancia de alcance y frontera con la solicitud de cambio.
- [ ] Procedimiento de cinco pasos con responsables y plazos.
- [ ] Cuatro definiciones de cambio con umbral concreto, iguales a los de cronograma/costos y PID.
- [ ] Con BMAD: tabla 5.1 completa (qué es elaboración progresiva y qué es cambio en PRD, arquitectura y épicas).
- [ ] Autoridad delegada con límite por nivel y presupuesto de cambio asociado.
- [ ] Tres disposiciones (aprobar, diferir, rechazar) y qué se actualiza tras aprobar.
- [ ] Fuera de especificación: concesión vs. corrección definidas.
- [ ] Configuración: identificadores, versiones, auditorías, pista de auditoría.
- [ ] Coherente con procedimientos contractuales si hay proveedores externos.
- [ ] Estado `borrador` hasta la aprobación del ejecutivo.
