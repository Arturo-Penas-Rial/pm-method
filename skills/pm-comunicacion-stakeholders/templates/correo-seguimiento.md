---
tipo: correo-seguimiento
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
acta_origen: "{{ruta_acta}}"
---

# Correo de seguimiento · Follow-up email

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Texto listo para pegar o para enviar vía pm-integraciones, solo tras confirmar destinatarios y contenido. El envío se anota en `diario.md`.

**Acta de origen / Source minutes:** {{ruta_acta}}
*Ruta del acta confirmada (la produce pm-reuniones en 03-control/reuniones/) o del comunicado aprobado; sin acta confirmada no se envían correos de acciones.*

**Modalidad / Mode:** {{modalidad}}
*"general" (un correo con todas las acciones) o "por responsable" (un correo por persona con sus acciones).*

**Confirmación / Confirmation:** destinatarios revisados por {{confirma}} el {{fecha_confirmacion}}
*Vacío mientras sea borrador.*

---

**Para / To:** {{para}}
**CC:** {{cc}}
**Asunto / Subject:** {{asunto}}
*Formato sugerido: "[{{proyecto}}] Acciones de la reunión {{nombre_reunion}} ({{fecha_reunion}})".*

{{saludo}},
*Saludo adecuado al canal y a la relación.*

{{apertura}}
*Una o dos líneas: de qué reunión viene y cuál es el propósito del correo (recordar acciones, confirmar decisiones, pedir una respuesta).*

**Decisiones confirmadas / Confirmed decisions:**
- {{decision_1}} (decidido por {{decidido_1}})
*Solo las que ya están confirmadas en el acta; las pendientes de ratificación se indican como tales.*

**Acciones / Actions:**

| # | Acción / Action | Responsable / Owner | Fecha límite / Due | Id |
|---|---|---|---|---|
| A1 | {{accion_1}} | {{responsable_1}} | {{fecha_1}} | {{id_1}} |
| A2 | {{accion_2}} | {{responsable_2}} | {{fecha_2}} | {{id_2}} |

*En modalidad "por responsable", solo las filas de esa persona.*

**Lo que necesito de vos / What I need from you:** {{pedido}}
*Confirmar la fecha, responder a una pregunta abierta, aportar un dato marcado [por confirmar].*

**Próxima reunión / Next meeting:** {{proxima_reunion}}

{{cierre}}
*Despedida y firma: nombre, rol en el proyecto, canal de contacto.*

---

## Registro del envío / Send record

| Enviado a / Sent to | Canal / Channel | Fecha / Date | Anotado en diario.md |
|---|---|---|---|
| {{enviado_a}} | {{canal}} | {{fecha_envio}} | {{diario}} |

## Lista de verificación / Checklist
- [ ] Acta de origen confirmada por quien presidió.
- [ ] Cada acción con responsable, fecha e id `A-###` de `acciones.csv`.
- [ ] Decisiones pendientes de ratificación marcadas como tales, no como confirmadas.
- [ ] Pedido explícito al destinatario con fecha.
- [ ] Sin datos sensibles no autorizados para ese destinatario.
- [ ] Destinatarios y texto confirmados por el usuario antes de enviar; envío anotado en `diario.md`.
