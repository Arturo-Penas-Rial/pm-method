---
tipo: handover
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Transferencia a operación y mantenimiento · Handover — {{proyecto}}

> Borrador generado con apoyo de IA. La transferencia es válida cuando el propietario receptor la confirma en la sección 5. / AI-assisted draft. The handover is valid once the receiving owner confirms it in section 5.

## 1. Alcance de la transferencia / Handover scope

**Productos transferidos / Products handed over:** {{productos}}
*Lista de productos (o el producto del proyecto completo) con versión aceptada; fuente: product status account y registros de aceptación.*

**Modalidad / Mode:** {{modalidad}}
*Entrega única al cierre · entregas por fases (indicar releases previas y sus fechas) · transferencia parcial por cierre prematuro.*

**Cómo se previó en el PID / As planned in the PID:** {{prevision_pid}}
*Referencia al enfoque de cambio o al plan de proyecto donde se definió la entrega a operaciones.*

**Fecha límite de cargo de costos al proyecto / Cost cut-off date:** {{fecha_corte_costos}}
*A partir de esta fecha ningún costo se imputa al proyecto.*

## 2. Detalle por producto / Product detail

| Producto / Product | Versión / Version | Aceptado por · fecha / Accepted by · date | Propietario de operación / Operations owner | Propietario de mantenimiento / Maintenance owner | Fecha de transferencia / Handover date | Estado / Status |
|---|---|---|---|---|---|---|
| {{p_1}} | {{p_ver_1}} | {{p_acept_1}} | {{p_op_1}} | {{p_mant_1}} | {{p_fecha_1}} | {{p_estado_1}} |

*Propietarios confirmados por nombre y área; estado: transferido · pendiente · con condiciones.*

## 3. Elementos entregados / Items delivered

| Elemento / Item | Descripción / Description | Ubicación / Location | Entregado / Delivered |
|---|---|---|---|
| Producto o sistema / Product or system | {{el_producto}} | {{el_producto_ubic}} | {{el_producto_ok}} |
| Documentación de usuario y operación / User and operations documentation | {{el_doc}} | {{el_doc_ubic}} | {{el_doc_ok}} |
| Documentación técnica y de configuración / Technical and configuration documentation | {{el_tec}} | {{el_tec_ubic}} | {{el_tec_ok}} |
| Accesos, credenciales y licencias / Access, credentials and licenses | {{el_acc}} | {{el_acc_ubic}} | {{el_acc_ok}} |
| Datos y migraciones / Data and migrations | {{el_datos}} | {{el_datos_ubic}} | {{el_datos_ok}} |
| Garantías y contratos de soporte / Warranties and support contracts | {{el_garantias}} | {{el_garantias_ubic}} | {{el_garantias_ok}} |
| Formación realizada / Training delivered | {{el_formacion}} | {{el_formacion_ubic}} | {{el_formacion_ok}} |

*Marcar sí / no / parcial; lo parcial pasa a recomendaciones de seguimiento.*

## 4. Soporte posterior / Post-handover support

**Período de garantía o soporte del proyecto / Warranty or project support period:** {{periodo_soporte}}
*Si el equipo del proyecto o el proveedor da soporte tras la transferencia: duración, alcance y a cargo de quién.*

**Canal de incidencias en operación / Operational incident channel:** {{canal_incidencias}}
*Dónde reporta el usuario a partir de ahora.*

**Riesgos residuales entregados (R-nnn) / Residual risks handed over:** {{riesgos_residuales}}
*Ids y destinatario.*

**Acciones pendientes entregadas / Pending actions handed over:** {{acciones_pendientes}}
*Referencia a las recomendaciones de seguimiento.*

## 5. Confirmación de la transferencia / Handover confirmation

| Rol / Role | Nombre / Name | Decisión / Decision | Fecha / Date | D-nnn |
|---|---|---|---|---|
| Entrega (gestor del proyecto) / Delivers (project manager) | {{entrega_nombre}} | {{entrega_decision}} | {{entrega_fecha}} | {{entrega_decision_id}} |
| Recibe (propietario de operación) / Receives (operations owner) | {{recibe_nombre}} | {{recibe_decision}} | {{recibe_fecha}} | {{recibe_decision_id}} |
| Usuario sénior / Senior user | {{us_nombre}} | {{us_decision}} | {{us_fecha}} | {{us_decision_id}} |

*Sin la confirmación del receptor la responsabilidad sigue en el proyecto. Decisión: confirmado · confirmado con condiciones · rechazado.*

## Lista de verificación / Checklist
- [ ] Todos los productos aceptados aparecen con propietario de operación y de mantenimiento confirmados.
- [ ] Entregas por fases previas verificadas como completas.
- [ ] Elementos entregados marcados; lo parcial en recomendaciones de seguimiento.
- [ ] Fecha límite de cargo de costos fijada.
- [ ] Soporte posterior, canal de incidencias y riesgos residuales definidos.
- [ ] Confirmación del receptor registrada con D-nnn.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
