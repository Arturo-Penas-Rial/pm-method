---
status: final
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md
---

# Portal de autoservicio para socios - Desglose de épicas

## Overview

Este documento presenta el desglose completo de épicas e historias de *Portal de autoservicio para socios*, descomponiendo los requisitos del PRD y de la arquitectura en historias implementables. No existe documento de diseño UX; los requisitos de interfaz provienen del PRD (NFR-4) y de las convenciones de la arquitectura.

## Requirements Inventory

### Functional Requirements

FR1: El socio puede registrarse verificando su identidad (solo con registro de socio vigente en el núcleo operativo) y acceder con credenciales y segundo factor; tras 5 intentos fallidos consecutivos la cuenta se bloquea temporalmente y se notifica al socio.
FR2: El socio puede recuperar su acceso mediante verificación de identidad sin intervención de un operador; la recuperación invalida credenciales anteriores, se audita y se notifica por el contacto verificado.
FR3: El socio puede ver saldo y últimos movimientos de sus cuentas de ahorro, con fecha y hora de última actualización del núcleo operativo; si el núcleo no responde se informa la indisponibilidad sin mostrar datos desactualizados como vigentes.
FR4: El socio puede ver por préstamo sus cuotas, vencimientos, saldo pendiente y estado, incluida la próxima cuota; solo ve sus propios préstamos.
FR5: El socio puede generar y descargar constancias PDF (membresía, saldos, préstamo al día) con fecha/hora de emisión, nombre y código de verificación; la emisión se audita y no requiere aprobación de operador.
FR6: El socio puede completar y enviar una solicitud guiada de préstamo simple (producto habilitado, monto y plazo dentro de límites); el formulario valida antes del envío, se asigna número de solicitud, se envía confirmación por correo y la solicitud llega a la bandeja como "Recibida".
FR7: El socio puede ver el estado de sus solicitudes, leer comentarios del operador y adjuntar la información adicional pedida (formatos y tamaños limitados); cada cambio de estado se notifica por correo.
FR8: El socio puede solicitar el cambio de teléfono, correo o domicilio; teléfono y correo se verifican con código antes de ser vigentes; todo cambio genera una solicitud en la bandeja y se notifica al contacto anterior; el domicilio requiere aprobación de un operador.
FR9: El operador puede ver, filtrar, asignarse y ordenar solicitudes (préstamo y cambio de datos en una misma lista) por tipo, estado y antigüedad, con los datos completos del socio y del pedido.
FR10: El operador puede aprobar, rechazar o pedir información adicional con comentarios (obligatorios al rechazar o pedir información); cada acción actualiza el estado, notifica al socio y se audita.
FR11: El sistema distingue las capacidades de socio, operador y administrador de la consola; un socio no accede a la consola ni a datos ajenos; aprobar préstamos se limita a operadores habilitados.
FR12: El sistema notifica por correo (SMS opcional) confirmación de solicitud, cambio de estado, cambio de contacto y recuperación de acceso; un fallo de envío se registra y no bloquea la solicitud.

### NonFunctional Requirements

NFR1: Seguridad y privacidad: cumplimiento de la Ley 18.331; cifrado en tránsito y en reposo; sesiones con expiración por inactividad; revisar normativa del BCU.
NFR2: Disponibilidad de al menos 99,5 % mensual.
NFR3: Consultas de saldos y préstamos en menos de 3 segundos en p95 con conexión móvil estándar.
NFR4: Usabilidad y accesibilidad: fluido en celular y navegadores comunes, interfaz clara para socios con poca comodidad digital, objetivo WCAG 2.1 AA.
NFR5: Trazabilidad: registro de auditoría de accesos, constancias y toda acción sobre solicitudes, con retención según política de la cooperativa.
NFR6: Integración: saldos y préstamos se leen del núcleo operativo sin copias desfasadas; el portal no escribe saldos.

### Additional Requirements

- Monolito modular hexagonal en Next.js 16 / TypeScript / PostgreSQL / drizzle-orm (módulos `acceso`, `productos`, `constancias`, `solicitudes`, `notificaciones`, `auditoria`, más `shared` y `worker/`); no se especifica un starter template, por lo que la Historia 1.1 inicializa el esqueleto del repositorio.
- AD-1: solo `productos` accede al núcleo mediante `NucleoPort` (solo lectura, con timeout); no se cachean saldos; respuestas con `actualizadoEn`; error `NUCLEO_NO_DISPONIBLE`.
- AD-2: PostgreSQL solo para datos del portal; un módulo dueño por tabla.
- AD-3: entidad `Solicitud` única con máquina de estados única (Recibida → En revisión → Información adicional → Aprobada | Rechazada).
- AD-4 y AD-11: `socioId` siempre desde la sesión; `Actor` y enum cerrado de acciones; `autorizar(actor, accion, recurso)`; consola bajo `/consola` con sesión y segundo factor propios.
- AD-5: autenticación detrás de `IdentityPort`, cookie `httpOnly`/`Secure`/`SameSite=Lax`, expiración por inactividad.
- AD-6: auditoría append-only (sin UPDATE/DELETE) en la misma transacción de la acción.
- AD-7 y AD-10: outbox transaccional con contrato `OutboxMensaje`, worker con reintentos; destinatarios resueltos desde `acceso`.
- AD-8 y AD-13: constancias generadas al vuelo con `@react-pdf/renderer`; solo se registra la emisión, tras generar el PDF con éxito; cifrado en reposo.
- AD-9: `acceso` es dueño de `contactoVigente` y `verificacionContacto`.
- AD-12: `solicitudes` es dueña de adjunto, comentario y `asignadoA`; `responderInformacion` devuelve a "En revisión"; configuración única de formatos y tamaños de adjuntos.
- Convenciones: ids UUID v7, fechas UTC, montos enteros en centésimos + moneda, errores `{codigo, mensaje}`, logs JSON sin datos personales, textos en español de Uruguay centralizados, formulario compartido con el mismo esquema en cliente y servidor.
- Entornos dev/staging/prod con la misma imagen; al menos 2 instancias sin estado y respaldos con restauración probada.

### UX Design Requirements

No se encontró documento de diseño UX; no hay requisitos UX-DR. Los requisitos de interfaz se cubren con NFR4 y las convenciones de UI de la arquitectura.

### FR Coverage Map

FR1: Epic 1 - Alta y acceso del socio con segundo factor y bloqueo
FR2: Epic 1 - Recuperación de acceso
FR3: Epic 1 - Consulta de saldos de ahorro
FR4: Epic 1 - Consulta de préstamos
FR5: Epic 1 - Constancias PDF
FR6: Epic 2 - Solicitud guiada de préstamo
FR7: Epic 2 - Seguimiento y respuesta a pedidos de información
FR8: Epic 2 - Actualización de contacto con verificación
FR9: Epic 3 - Bandeja única del operador
FR10: Epic 3 - Resolución de solicitudes
FR11: Epic 1 (rol socio y autorización base) y Epic 3 (operador, administrador y permiso de aprobar)
FR12: Epic 1 (outbox y avisos de seguridad) y Epic 2 (avisos de solicitudes)

## Epic List

### Epic 1: Acceso seguro y consulta de mis productos
El socio se registra, accede de forma segura, recupera su acceso, consulta saldos y préstamos y descarga constancias sin ir a la sucursal. Incluye el esqueleto del proyecto, la auditoría y el outbox de notificaciones.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR11 (parcial), FR12 (parcial)

### Epic 2: Solicitudes del socio: préstamo y datos de contacto
El socio pide un préstamo simple, sigue su estado, responde pedidos de información y actualiza sus datos de contacto con verificación. Las solicitudes quedan persistidas con estado "Recibida".
**FRs covered:** FR6, FR7, FR8, FR12 (parcial)

### Epic 3: Consola de operador
El operador atiende en una bandeja única las solicitudes de préstamo y de contacto, las resuelve con comentarios y auditoría, y el administrador gestiona los roles de la consola.
**FRs covered:** FR9, FR10, FR11 (parcial)

## Epic 1: Acceso seguro y consulta de mis productos

El socio se registra, accede de forma segura, recupera su acceso, consulta saldos y préstamos y descarga constancias sin ir a la sucursal. Incluye el esqueleto del proyecto, la auditoría y el outbox de notificaciones.

### Story 1.1: Alta y acceso del socio con segundo factor

As a socio,
I want registrarme verificando mi identidad y acceder con credenciales y un segundo factor,
So that pueda usar el portal con la seguridad de que solo yo veo mis datos.

**Acceptance Criteria:**

**Given** un repositorio vacío
**When** se completa esta historia
**Then** existe el esqueleto del monolito modular (`src/app`, `src/modules/{acceso,productos,constancias,solicitudes,notificaciones,auditoria}`, `src/shared`, `worker/`, `db/migrations/`) con TypeScript, Next.js, PostgreSQL y drizzle-orm
**And** la configuración se lee de variables de entorno validadas al arranque y existe un pipeline que ejecuta lint y pruebas.

**Given** una persona con registro de socio vigente en el núcleo operativo
**When** completa el alta verificando su identidad por `IdentityPort`
**Then** se crea su usuario en `acceso` y queda habilitada para acceder
**And** una persona sin registro vigente no puede completar el alta y recibe el error `{codigo, mensaje}` correspondiente.

**Given** un socio registrado
**When** ingresa credenciales válidas y el segundo factor
**Then** se crea una sesión con cookie `httpOnly`, `Secure` y `SameSite=Lax` que expira por inactividad
**And** el `socioId` se obtiene siempre de la sesión y `autorizar(actor, accion, recurso)` impide acceder a datos de otros socios.

**Given** un socio con 4 intentos fallidos consecutivos
**When** falla un quinto intento
**Then** la cuenta se bloquea temporalmente
**And** se inserta en el outbox un mensaje `OutboxMensaje` de bloqueo, procesado por el worker con reintentos, y el evento queda en el registro de auditoría append-only.

**Given** un acceso exitoso o fallido
**When** se registra el evento
**Then** `auditoria.registrar` guarda `actorId`, `rol`, `accion`, `recursoId` y `ts` UTC en la misma transacción, sin permitir `UPDATE` ni `DELETE`.

### Story 1.2: Recuperación de acceso

As a socio,
I want recuperar mi acceso verificando mi identidad,
So that pueda volver al portal sin ir a la sucursal si olvido mi contraseña.

**Acceptance Criteria:**

**Given** un socio que olvidó su contraseña
**When** inicia la recuperación y supera la verificación de identidad
**Then** puede definir nuevas credenciales sin intervención de un operador
**And** las credenciales y sesiones anteriores quedan invalidadas.

**Given** una recuperación completada
**When** se confirma el cambio
**Then** se notifica por el contacto verificado mediante el outbox
**And** el evento queda en el registro de auditoría.

**Given** una verificación fallida o expirada
**When** el socio intenta continuar
**Then** no se cambian las credenciales y se muestra un error claro
**And** tras completar el acceso el socio vuelve al punto del portal donde estaba.

### Story 1.3: Consulta de saldos de ahorro y préstamos

As a socio,
I want ver mis saldos, movimientos y préstamos,
So that conozca mi situación sin ir a la sucursal ni esperar un horario.

**Acceptance Criteria:**

**Given** un socio autenticado
**When** abre la vista de ahorros
**Then** ve el saldo y los últimos movimientos de sus cuentas, leídos del núcleo operativo por `NucleoPort`
**And** cada respuesta muestra la fecha y hora de `actualizadoEn`, y los montos se expresan con moneda (`UYU`, `USD`).

**Given** un socio autenticado con préstamos
**When** abre la vista de préstamos
**Then** ve por préstamo sus cuotas, vencimientos, saldo pendiente y estado, y destacada la próxima cuota con vencimiento y monto
**And** solo ve sus propios préstamos.

**Given** que el núcleo operativo no responde dentro del timeout
**When** el socio consulta saldos o préstamos
**Then** el portal informa la indisponibilidad con el error `NUCLEO_NO_DISPONIBLE`
**And** no muestra datos desactualizados como vigentes ni persiste saldos.

**Given** una conexión móvil estándar
**When** se consultan saldos o préstamos
**Then** la respuesta toma menos de 3 segundos en el percentil 95
**And** la interfaz es utilizable en celular y cumple WCAG 2.1 AA.

### Story 1.4: Descarga de constancias en PDF

As a socio,
I want generar y descargar constancias en PDF,
So that pueda presentarlas sin pisar la sucursal.

**Acceptance Criteria:**

**Given** un socio autenticado
**When** elige una constancia (membresía, saldos o préstamo al día)
**Then** el servidor arma el PDF con los datos leídos en ese momento a través de `productos`
**And** el PDF incluye fecha y hora de emisión, nombre del socio y un código de verificación único.

**Given** un PDF generado con éxito
**When** se completa la emisión
**Then** en una sola transacción se registra `codigo`, tipo, socio y `ts` y se audita la emisión
**And** no se guarda el archivo PDF.

**Given** un fallo al generar el PDF o al leer el núcleo
**When** el socio solicita la constancia
**Then** no se registra ningún código ni auditoría de emisión
**And** se muestra un error claro.

**Given** un código de verificación
**When** se consulta el registro de constancias
**Then** se confirma si fue emitido, sin requerir aprobación de un operador.

## Epic 2: Solicitudes del socio: préstamo y datos de contacto

El socio pide un préstamo simple, sigue su estado, responde pedidos de información y actualiza sus datos de contacto con verificación. Las solicitudes quedan persistidas con estado "Recibida".

### Story 2.1: Solicitud guiada de préstamo simple

As a socio,
I want completar un formulario guiado para pedir un préstamo,
So that pueda solicitar un préstamo pequeño sin ir a la sucursal.

**Acceptance Criteria:**

**Given** un socio autenticado con contacto verificado
**When** elige "Solicitar préstamo", un producto habilitado, monto y plazo
**Then** el formulario valida campos obligatorios y límites del producto con el mismo esquema en cliente y servidor
**And** si el monto excede el máximo, lo indica antes de permitir el envío.

**Given** un formulario válido
**When** el socio revisa el resumen y envía
**Then** se crea una `Solicitud` de tipo `prestamo` en estado "Recibida" y se le asigna un número de solicitud
**And** los montos se guardan como entero en centésimos más moneda, y los productos y límites provienen de configuración del módulo `solicitudes`.

**Given** una solicitud creada
**When** se confirma la transacción
**Then** se inserta en el outbox la confirmación por correo y se registra la auditoría
**And** un fallo de envío se registra sin revertir ni bloquear la solicitud.

### Story 2.2: Seguimiento de solicitudes y respuesta a pedidos de información

As a socio,
I want ver el estado de mis solicitudes y adjuntar la información que me piden,
So that sepa en qué punto está mi trámite y pueda completarlo desde el portal.

**Acceptance Criteria:**

**Given** un socio con solicitudes
**When** abre "Mis solicitudes"
**Then** ve solo las suyas, con número, tipo, estado y los comentarios del operador.

**Given** una solicitud en "Información adicional"
**When** el socio adjunta un archivo de un formato y tamaño permitidos y responde
**Then** el adjunto queda asociado a la solicitud y se ejecuta `responderInformacion`, que la devuelve a "En revisión"
**And** formatos y tamaños se validan en servidor con la configuración compartida única, y el adjunto se cifra en reposo.

**Given** un adjunto de formato o tamaño no permitido
**When** el socio intenta subirlo
**Then** se rechaza con un error claro y la solicitud no cambia de estado.

**Given** cualquier cambio de estado de una solicitud
**When** se confirma la transición
**Then** se notifica al socio por correo mediante el outbox con el contrato `OutboxMensaje`.

### Story 2.3: Actualización de datos de contacto con verificación

As a socio,
I want actualizar mi teléfono, correo o domicilio,
So that la cooperativa tenga mis datos vigentes.

**Acceptance Criteria:**

**Given** un socio autenticado
**When** solicita cambiar su teléfono o correo
**Then** `acceso` envía un código de verificación al nuevo dato, con TTL e intentos máximos
**And** mientras no se verifique, el dato vigente no se reemplaza.

**Given** un código correcto
**When** el socio lo ingresa
**Then** `acceso.aplicarContacto()` actualiza el contacto vigente y se crea una `Solicitud` de tipo `contacto` ya resuelta, en la misma transacción
**And** se notifica al contacto anterior y se audita el cambio.

**Given** un código incorrecto, expirado o con intentos agotados
**When** el socio intenta verificar
**Then** no se registra ninguna solicitud ni cambio de contacto.

**Given** un socio que solicita un cambio de domicilio
**When** envía el pedido
**Then** se crea una `Solicitud` de tipo `contacto` en estado "Recibida", pendiente de operador, que llega a la bandeja
**And** el domicilio vigente no cambia hasta su aprobación.

## Epic 3: Consola de operador

El operador atiende en una bandeja única las solicitudes de préstamo y de contacto, las resuelve con comentarios y auditoría, y el administrador gestiona los roles de la consola.

### Story 3.1: Acceso y roles de la consola de operador

As a administrador de la consola,
I want gestionar operadores con sus permisos y segundo factor,
So that solo personal autorizado atienda solicitudes y aprobe préstamos.

**Acceptance Criteria:**

**Given** un administrador autenticado
**When** crea o habilita a un operador, con o sin el permiso `solicitud.aprobar`
**Then** `acceso` registra su identidad y permisos con segundo factor obligatorio
**And** la acción se audita.

**Given** un operador
**When** accede a `/consola`
**Then** usa una sesión y un segundo factor propios, que nunca comparten cookie con la sesión del socio
**And** el `Actor {id, rol, permisos[]}` se resuelve en el servidor.

**Given** un socio autenticado
**When** intenta abrir `/consola` o pedir datos de otro socio
**Then** `autorizar` deniega el acceso con un error `{codigo, mensaje}`
**And** un operador sin el permiso de aprobar no puede ejecutar `solicitud.aprobar`.

### Story 3.2: Bandeja única de solicitudes

As a operador,
I want ver, filtrar, asignarme y ordenar las solicitudes en una sola lista,
So that atienda los pedidos sin transcribir información de otros canales.

**Acceptance Criteria:**

**Given** un operador autenticado
**When** abre la bandeja
**Then** ve en una misma lista las solicitudes de préstamo y de contacto
**And** puede filtrar por tipo y estado y ordenar por antigüedad, y la siguiente pendiente aparece por antigüedad.

**Given** una solicitud sin asignar
**When** el operador se la asigna
**Then** se guarda `asignadoA` y se audita la acción.

**Given** una solicitud de la bandeja
**When** el operador la abre
**Then** ve los datos completos del socio y del pedido, con adjuntos y comentarios, sin consultar otros sistemas
**And** la solicitud pasa a "En revisión" al tomarla mediante el caso de uso de `solicitudes`.

### Story 3.3: Resolución de solicitudes

As a operador,
I want aprobar, rechazar o pedir información adicional con comentarios,
So that cada solicitud quede resuelta con su registro de auditoría.

**Acceptance Criteria:**

**Given** una solicitud en revisión
**When** el operador pide información adicional o rechaza
**Then** el comentario es obligatorio y visible para el socio
**And** el estado cambia a "Información adicional" o "Rechazada" mediante la máquina de estados de `Solicitud`, que valida el estado previo.

**Given** una solicitud en revisión y un operador con el permiso de aprobar
**When** aprueba
**Then** el estado pasa a "Aprobada"
**And** si es un cambio de domicilio, se llama a `acceso.aplicarContacto()` en la misma transacción.

**Given** cualquier acción de resolución
**When** se confirma
**Then** se notifica al socio por correo vía outbox y se registra auditoría con operador, fecha y hora en la misma transacción
**And** un operador sin permiso de aprobar recibe un error al intentar aprobar.

**Given** un comentario faltante al rechazar o pedir información
**When** el operador confirma
**Then** la acción se rechaza y el estado no cambia.
