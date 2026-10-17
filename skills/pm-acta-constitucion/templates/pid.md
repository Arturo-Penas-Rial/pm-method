---
tipo: pid
proyecto: "{{proyecto}}"
version: 0.9
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: en-revision
aprobado_por: ""
idioma: "{{idioma}}"
---

# Documentación de inicio del proyecto · Project initiation documentation (PID) — {{proyecto}}

> Paquete que reúne qué, por qué, quién, cómo, dónde, cuándo y cuánto. Con el plan de etapa, es el "contrato" entre el gestor y la junta. La versión que autoriza el proyecto se congela como línea base; las posteriores se comparan contra ella. / The what, why, who, how, where, when and how much of the project; the authorising version is frozen as baseline.

**Formato / Format:** {{formato}} · **Versión mínima / Minimal version:** {{version_minima}}
*`indice` (cada componente es un documento independiente referenciado aquí), `documento` (texto resumido en cada sección) o `compacto` (perfil ágil mínimo: business case de una página, estructura con product owner, enfoques de una página, backlog priorizado y release plan por etapas en lugar de PBS/WBS completa; 3–5 páginas en total). Versión mínima: un documento breve; declarar qué componentes se omitieron o fusionaron y por qué.*

**Modo / Mode:** {{modo}}
*`ensamblar` (inicio), `relinea-base` (fin de etapa o excepción). En `relinea-base`, la versión 1.0 de `historial/` no se toca.*

## 0. Índice de componentes / Component index

| # | Componente / Component | Ruta / Path | Versión / Version | Estado / Status | Creador / Creator | Revisor / Reviewer | Aprobador / Approver | Skill dueña / Owning skill |
|---|---|---|---|---|---|---|---|---|
| 1 | Definición del proyecto / Project definition | {{c1_ruta}} | {{c1_version}} | {{c1_estado}} | gestor | aseguramiento | junta | pm-mandato-y-brief |
| 2 | Enfoque del proyecto / Project approach | {{c2_ruta}} | {{c2_version}} | {{c2_estado}} | gestor | aseguramiento | junta | pm-mandato-y-brief |
| 3 | Caso de negocio / Business case | {{c3_ruta}} | {{c3_version}} | {{c3_estado}} | gestor (por el ejecutivo) | aseguramiento | junta | pm-caso-de-negocio |
| 4 | Estructura del equipo de gestión / Management team structure | {{c4_ruta}} | {{c4_version}} | {{c4_estado}} | gestor | aseguramiento | ejecutivo | pm-organizacion-roles |
| 5 | Descripciones de rol / Role descriptions | {{c5_ruta}} | {{c5_version}} | {{c5_estado}} | gestor | aseguramiento | ejecutivo | pm-organizacion-roles |
| 6a | Enfoque de beneficios / Benefits approach | {{c6a_ruta}} | {{c6a_version}} | {{c6a_estado}} | gestor | aseguramiento | ejecutivo (acuerda usuario sénior) | pm-caso-de-negocio |
| 6b | Enfoque de sostenibilidad / Sustainability approach | {{c6b_ruta}} | {{c6b_version}} | {{c6b_estado}} | gestor | aseguramiento | ejecutivo | pm-caso-de-negocio |
| 6c | Enfoque de calidad / Quality approach | {{c6c_ruta}} | {{c6c_version}} | {{c6c_estado}} | gestor | aseguramiento | ejecutivo (acuerdan US y PS) | pm-enfoques-gestion |
| 6d | Enfoque de riesgo / Risk approach | {{c6d_ruta}} | {{c6d_version}} | {{c6d_estado}} | gestor | aseguramiento | ejecutivo (acuerdan US y PS) | pm-enfoques-gestion |
| 6e | Enfoque de issues y cambio / Issue and change approach | {{c6e_ruta}} | {{c6e_version}} | {{c6e_estado}} | gestor | aseguramiento | ejecutivo (acuerdan US y PS) | pm-enfoques-gestion |
| 6f | Enfoque de comunicación / Communication approach (+ anexo `02-planificacion/matriz-comunicaciones.md`, dueño `pm-comunicacion-stakeholders`) | {{c6f_ruta}} | {{c6f_version}} | {{c6f_estado}} | gestor | aseguramiento | ejecutivo (acuerdan US y PS) | pm-enfoques-gestion |
| 6g | Enfoque de datos y tecnología digital / Digital and data approach | {{c6g_ruta}} | {{c6g_version}} | {{c6g_estado}} | gestor | aseguramiento | ejecutivo (acuerdan US y PS) | pm-enfoques-gestion |
| 6h | Enfoque comercial / Commercial approach | {{c6h_ruta}} | {{c6h_version}} | {{c6h_estado}} | gestor | aseguramiento | ejecutivo | pm-adquisiciones |
| 6i | Enfoque de gestión del cambio organizacional / Organisational change approach | {{c6i_ruta}} | {{c6i_version}} | {{c6i_estado}} | gestor | aseguramiento | ejecutivo | pm-comunicacion-stakeholders |
| 6j | Planes de gestión: alcance y requisitos (CÓMO), cronograma y costos, recursos y adquisiciones / Management plans | {{c6j_ruta}} | {{c6j_version}} | {{c6j_estado}} | gestor | aseguramiento | ejecutivo | pm-enfoques-gestion |
| 7 | Plan de proyecto / Project plan (+ enunciado de alcance y PBS/WBS = QUÉ; en ágil, backlog y release plan) | {{c7_ruta}} | {{c7_version}} | {{c7_estado}} | gestor | aseguramiento | junta | pm-planificacion-por-productos |
| 8 | Controles del proyecto / Project controls | este documento §7 | — | — | gestor | aseguramiento | junta | pm-acta-constitucion |
| 9 | Adaptación de PRINCE2 / PRINCE2 tailoring | este documento §8 | — | — | gestor | aseguramiento | junta | pm-acta-constitucion |

*Estado: `borrador`, `en-revision`, `aprobado`, `pendiente` (con razón en la sección correspondiente), `no-aplica` (con razón). US = usuario sénior; PS = proveedor sénior.*

## 1. Definición del proyecto / Project definition

{{definicion}}
*Contexto, objetivos con criterios de éxito, resultados deseados, alcance con inclusiones y exclusiones, restricciones y supuestos, usuarios e interesados, interfaces con otros proyectos o sistemas. En formato índice, resumen de cinco líneas y referencia al brief.*

## 2. Enfoque del proyecto / Project approach

{{enfoque}}
*Solución y método de entrega elegidos para la opción de negocio seleccionada, considerando el entorno operativo de destino: modelo de entrega (interno/externo), construir/adaptar/comprar, enfoque de entrega (`estado.json.enfoque_entrega`) y cómo convive con las etapas de gestión, sostenibilidad.*

## 3. Caso de negocio / Business case

{{business_case}}
*Resumen ejecutivo del caso completo: opción elegida, beneficios principales con tolerancia, costos, evaluación de inversión, veredicto deseable / viable / alcanzable. Referencia a `00-direccion/business-case.md` versión {{c3_version}}.*

## 4. Estructura del equipo de gestión / Management team structure

{{estructura}}
*Organigrama (Mermaid o referencia), tres intereses representados, un solo ejecutivo, aseguramiento separado del gestor y del soporte, cambios de estructura previstos por etapa. Referencia a `00-direccion/estructura-organizativa.md`.*

## 5. Descripciones de rol / Role descriptions

{{roles}}
*Lista de roles con persona, dedicación y ruta a cada descripción en `00-direccion/roles/`. Las autoridades delegadas deben coincidir con los controles de la sección 7.*

## 6. Enfoques de gestión / Management approaches

{{enfoques}}
*Una línea por enfoque: escala o umbral clave que define (por ejemplo, matriz de riesgo 5×5, severidad de issues, frecuencia del highlight report). El enfoque de comunicación se completa último porque recoge las comunicaciones que los demás requieren.*

## 7. Controles del proyecto / Project controls

**Etapas de gestión / Management stages:** {{etapas}}
*Número, nombre y límite de cada etapa; criterio por el que se cortaron (producto mayor, transición de capacidades, riesgo). Numeración canónica: etapa 1 = iniciación (esta), etapas de entrega 2…n; la puesta en marcha fue pre-proyecto.*

| Nivel / Level | Tiempo / Time | Costo / Cost | Alcance / Scope | Calidad / Quality | Beneficios / Benefits | Riesgo / Risk | Sostenibilidad / Sustainability | Fija / Set by |
|---|---|---|---|---|---|---|---|---|
| Proyecto / Project | {{tol_p_tiempo}} | {{tol_p_costo}} | {{tol_p_alcance}} | {{tol_p_calidad}} | {{tol_p_beneficios}} | {{tol_p_riesgo}} | {{tol_p_sostenibilidad}} | capa de negocio |
| Etapa / Stage | {{tol_e_tiempo}} | {{tol_e_costo}} | {{tol_e_alcance}} | {{tol_e_calidad}} | {{tol_e_beneficios}} | {{tol_e_riesgo}} | {{tol_e_sostenibilidad}} | junta |
| Paquete de trabajo / Work package | {{tol_w_tiempo}} | {{tol_w_costo}} | {{tol_w_alcance}} | {{tol_w_calidad}} | — | {{tol_w_riesgo}} | {{tol_w_sostenibilidad}} | gestor |

*Mismos valores que `estado.json.tolerancias` y que los enfoques. Proyecto: `estado.py tolerancia --nivel proyecto k=v`; etapa: la fija la junta en cada `autorizar-etapa` (`--nivel etapa`, vía `pm-director`); paquete de trabajo: vive en el documento `WP-###`. Tiempo y costo, mínimo obligatorio. En ágil, alcance como MoSCoW: el product owner intercambia ítems del backlog dentro de la tolerancia de alcance de la etapa (decisión `nivel=product-owner`); desplazar un Must o exceder la tolerancia es solicitud de cambio. Una tolerancia sin cifra o criterio no es tolerancia.*

**Autoridad delegada / Delegated authority:** {{autoridad_delegada}}
*Qué decide la junta, qué la autoridad de cambio (con presupuesto de cambio), qué el gestor, qué los gestores de equipo; cómo se monitoriza.*

**Informes y frecuencia / Reports and frequency:** {{informes}}
*Highlight report (gestor → junta), checkpoint report (gestor de equipo → gestor), informe de fin de etapa, informe de excepción; frecuencia y formato; en ágil, tableros en modo "pull" si la junta lo acepta.*

**Procedimiento de escalado / Escalation procedure:** {{escalado}}
*Gestor de equipo → gestor → junta → capa de negocio; qué dispara cada escalón (previsión de salir de tolerancia); plazo de respuesta.*

**Presupuestos de riesgo y de cambio / Risk and change budgets:** {{presupuestos_riesgo_cambio}}
*Montos, quién los libera, cómo se informa su consumo.*

**Puntos de decisión / Decision points:** {{puntos_decision}}
*Fin de cada etapa, excepciones, revisiones de beneficios intermedias; copiar del roadmap.*

## 8. Adaptación de PRINCE2 / PRINCE2 tailoring

| Elemento del método / Method element | Adaptación / Tailoring | Razón / Reason | Aprobada por / Approved by |
|---|---|---|---|
| {{ad1_elemento}} | {{ad1_adaptacion}} | {{ad1_razon}} | {{ad1_aprobada}} |
| {{ad2_elemento}} | {{ad2_adaptacion}} | {{ad2_razon}} | {{ad2_aprobada}} |

*Documentar: técnicas propias sustituidas (gestión del caso de negocio, diseño organizacional, planificación basada en productos, gestión de la calidad), cambios de terminología (product owner ≈ usuario sénior), productos combinados u omitidos, roles compartidos (y cómo se mantiene el punto único de rendición de cuentas), procesos no aplicados en la etapa de inicio. Sustituir técnicas de apoyo (RACI, Gantt, NPV) no es adaptación.*

## 9. Consistencia entre componentes / Cross-component consistency

| Verificación / Check | Documentos comparados / Documents compared | Resultado / Result | Acción / Action |
|---|---|---|---|
| Presupuesto igual en acta, business case y plan | {{chk_presupuesto_docs}} | {{chk_presupuesto}} | {{chk_presupuesto_accion}} |
| Hitos iguales en acta, roadmap y plan | {{chk_hitos_docs}} | {{chk_hitos}} | {{chk_hitos_accion}} |
| Tolerancias iguales en PID, `estado.json` y enfoques | {{chk_tolerancias_docs}} | {{chk_tolerancias}} | {{chk_tolerancias_accion}} |
| Un solo ejecutivo; separación gestor / ejecutivo / aseguramiento | {{chk_roles_docs}} | {{chk_roles}} | {{chk_roles_accion}} |
| Escalas de los enfoques coinciden con los registros CSV | {{chk_escalas_docs}} | {{chk_escalas}} | {{chk_escalas_accion}} |
| Cada producto mayor tiene descripción y vía de entrega (híbrido) | {{chk_productos_docs}} | {{chk_productos}} | {{chk_productos_accion}} |
| Beneficios del caso = beneficios del enfoque de beneficios | {{chk_beneficios_docs}} | {{chk_beneficios}} | {{chk_beneficios_accion}} |
| Autoridad del gestor (acta) = autoridad delegada (controles) | {{chk_autoridad_docs}} | {{chk_autoridad}} | {{chk_autoridad_accion}} |
| Cada adaptación justificada | este documento §8 | {{chk_adaptacion}} | {{chk_adaptacion_accion}} |

*Resultado: `ok`, `discrepancia` (describir) o `pendiente`. Las discrepancias se reportan a los dueños de los documentos; el PID no es apto para la puerta hasta resolverlas o aceptarlas explícitamente.*

## 10. Precondiciones de la puerta autorizar-proyecto / Preconditions for the authorise-project gate

- [ ] Business case completo coherente con el plan y el riesgo agregado.
- [ ] Plan de proyecto con PBS, descripciones de producto, diagrama de flujo y etapas (perfil ágil mínimo: backlog priorizado con MoSCoW, puntos y criterios de aceptación, release plan por etapas, DoD/DoR).
- [ ] Descripción del producto del proyecto presente (la exige el paquete de puerta).
- [ ] Enfoques aprobados o presentados para aprobación conjunta.
- [ ] Enfoque de beneficios y enfoque de sostenibilidad presentes.
- [ ] Lecciones revisadas; riesgos con respuestas adecuadas.
- [ ] Plan de la primera etapa de entrega preparado: `02-planificacion/plan-etapa-2.md` (`pm-plan-etapa-y-limites`).
- [ ] Tolerancias de proyecto de tiempo y costo cargadas en `estado.json`.
- [ ] Registros de productos, calidad, riesgos e issues creados.

**Bloqueantes / Blockers:** {{bloqueantes}}
*Lo que falta, quién lo produce y cuándo.*

## 11. Historial de versiones / Version history

| Versión / Version | Fecha / Date | Motivo / Reason | Cambios principales / Main changes | Aprobada por / Approved by | Ruta en historial / Path in history |
|---|---|---|---|---|---|
| {{hv1_version}} | {{hv1_fecha}} | {{hv1_motivo}} | {{hv1_cambios}} | {{hv1_aprobada}} | {{hv1_ruta}} |

*La versión 1.0 (la que autorizó el proyecto) se congela en `00-direccion/historial/pid-v1.0.md` y nunca se edita: el paquete de la puerta `autorizar-cierre` la compara con la versión vigente.*

*1.0 = versión de autorización, intacta. 1.x = re-líneas base en fin de etapa o excepción, con cambios aprobados por control de cambios.*

## 12. Referencias / References

{{referencias}}
*Brief, acta, roadmap, registros, contratos, políticas corporativas, documentos del programa.*

## Lista de verificación / Checklist
- [ ] Los ocho componentes presentes, referenciados o declarados `pendiente` / `no-aplica` con razón.
- [ ] Cada componente con ruta, versión, estado, creador, revisor y aprobador.
- [ ] Controles: etapas, tolerancias por nivel con cifras, autoridad delegada, informes, escalado, presupuestos de riesgo y cambio.
- [ ] Tolerancias idénticas a `estado.json`.
- [ ] Adaptación: cada desviación justificada y con aprobador.
- [ ] Consistencia ejecutada; discrepancias con acción y dueño.
- [ ] Precondiciones de la puerta verificadas; bloqueantes listados.
- [ ] Sirve a los tres usos del PID (base para la decisión, punto de comparación, referencia para quien se incorpora).
- [ ] Copia en `historial/`; estado `en-revision`; `aprobado_por` vacío hasta la puerta.
