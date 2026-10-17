---
tipo: notificacion-cierre
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Notificación de cierre del proyecto · Project closure notification — {{proyecto}}

> Borrador preparado por el gestor del proyecto para revisión de la junta. Se emite únicamente después de la puerta autorizar-cierre y la firma el ejecutivo; el envío externo requiere confirmación explícita. / Draft prepared by the project manager for board review. Issued only after the closure gate is approved and signed by the executive; external sending requires explicit confirmation.

## 1. Datos de la notificación / Notification data

**Emisor / Issuer:** {{ejecutivo}}
*Ejecutivo del proyecto, en nombre de la junta.*

**Destinatarios / Recipients:** {{destinatarios}}
*Capa de negocio, usuarios, proveedores, áreas de soporte, programa; tomados del enfoque de comunicación.*

**Fecha de autorización del cierre / Closure authorization date:** {{fecha_autorizacion}}
*Fecha de la puerta autorizar-cierre y D-nnn.*

**Fecha efectiva de cierre / Effective closure date:** {{fecha_cierre}}
*A partir de la cual se disuelve la organización temporal del proyecto.*

**Tipo de cierre / Closure type:** {{tipo_cierre}}
*planificado · prematuro (con la razón en una frase).*

## 2. Mensaje / Message

{{mensaje}}
*Tres a seis párrafos en el idioma del proyecto: qué se entregó y a quién, estado de aceptación, resultados principales contra el business case, qué queda pendiente y quién lo sigue, agradecimiento y reconocimiento al equipo. Sin cifras sin fuente.*

## 3. Hechos que se comunican / Facts communicated

| Hecho / Fact | Detalle / Detail | Fuente / Source |
|---|---|---|
| Productos entregados y aceptados / Products delivered and accepted | {{hecho_productos}} | {{fuente_productos}} |
| Propietarios de operación y mantenimiento / Operations and maintenance owners | {{hecho_propietarios}} | {{fuente_propietarios}} |
| Fecha límite de cargo de costos / Cost cut-off date | {{hecho_costos}} | {{fuente_costos}} |
| Liberación de recursos y personas / Release of resources and people | {{hecho_recursos}} | {{fuente_recursos}} |
| Acciones de seguimiento y quién las lleva / Follow-on actions and owners | {{hecho_seguimiento}} | {{fuente_seguimiento}} |
| Revisiones de beneficios previstas / Planned benefit reviews | {{hecho_beneficios}} | {{fuente_beneficios}} |
| Ubicación del archivo del proyecto / Project archive location | {{hecho_archivo}} | {{fuente_archivo}} |

*Lo que cada destinatario necesita saber para actuar; coherente con el informe de fin de proyecto.*

## 4. Canales y formato por audiencia / Channels and format per audience

| Audiencia / Audience | Canal / Channel | Formato / Format | Responsable del envío / Sender | Fecha / Date |
|---|---|---|---|---|
| {{aud_1}} | {{canal_1}} | {{formato_1}} | {{sender_1}} | {{fecha_env_1}} |

*Correo, reunión, entrada en herramienta, comunicado; oportunidades de relaciones públicas si el enfoque las prevé.*

## 5. Reconocimiento / Recognition

{{reconocimiento}}
*Propuesta de la junta para reconocer al equipo y a los colaboradores; forma y fecha.*

## 6. Firma / Sign-off

| Campo / Field | Valor / Value |
|---|---|
| Firmado por / Signed by | {{firmado_por}} |
| Rol / Role | Ejecutivo del proyecto / Project executive |
| Fecha / Date | {{fecha_firma}} |
| Puerta en estado.json / Gate in estado.json | autorizar-cierre — {{decision_puerta}} |

*Sin esta firma y sin la puerta aprobada, el documento es solo un borrador para revisión.*

## Lista de verificación / Checklist
- [ ] Puerta autorizar-cierre aprobada y registrada antes de emitir.
- [ ] Destinatarios tomados del enfoque de comunicación; ninguno relevante omitido.
- [ ] Hechos coherentes con el informe de fin de proyecto y con fuente.
- [ ] Fecha de cierre, fecha límite de costos y liberación de recursos explícitas.
- [ ] Acciones de seguimiento y beneficios pendientes con dueño mencionados.
- [ ] Reconocimiento al equipo incluido.
- [ ] Envío externo solo con confirmación explícita del ejecutivo o del usuario.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
