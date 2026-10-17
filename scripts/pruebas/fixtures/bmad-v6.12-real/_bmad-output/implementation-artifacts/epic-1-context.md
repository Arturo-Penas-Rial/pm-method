# Epic 1 Context: Acceso seguro y consulta de mis productos

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

El socio de una cooperativa de ahorro y crédito uruguaya (unos 40.000 socios) se registra, accede de forma segura, recupera su acceso, consulta saldos y préstamos y descarga constancias desde el celular, sin ir a la sucursal. La épica incluye el esqueleto del repositorio (no hay starter template), la auditoría y el outbox de notificaciones. No existe documento UX; la interfaz se rige por la accesibilidad y las convenciones de UI.

## Stories

- Story 1.1: Alta y acceso del socio con segundo factor
- Story 1.2: Recuperación de acceso
- Story 1.3: Consulta de saldos de ahorro y préstamos
- Story 1.4: Descarga de constancias en PDF

## Requirements & Constraints

- Solo quien tiene registro de socio vigente en el núcleo operativo completa el alta; el acceso exige segundo factor; 5 fallos consecutivos bloquean temporalmente la cuenta y se notifica al socio.
- La recuperación invalida credenciales y sesiones previas, se audita y se notifica por contacto verificado.
- Saldos y préstamos vienen siempre del núcleo, con fecha/hora de actualización; si no responde se informa indisponibilidad, nunca datos viejos. El portal no escribe saldos.
- Un socio solo ve sus propios datos.
- Constancias PDF con fecha/hora, nombre y código de verificación; emisión auditada, sin aprobación de operador.
- Seguridad: Ley 18.331, cifrado en tránsito y reposo, sesiones con expiración por inactividad. Consultas p95 < 3 s. Móvil primero, WCAG 2.1 AA. Auditoría de accesos y constancias. Un fallo de envío de correo no bloquea la acción.

## Technical Decisions

- Monolito modular hexagonal: Next.js 16 (App Router) / React 19 / TypeScript / Node 24 LTS / PostgreSQL 18 / drizzle-orm. Módulos `acceso`, `productos`, `constancias`, `solicitudes`, `notificaciones`, `auditoria` con capas `domain`, `app`, `adapters`; `src/app` solo delega a casos de uso; `src/shared`, `worker/`, `db/migrations/`. Los módulos se llaman solo vía casos de uso públicos.
- Un módulo dueño por tabla. Mutación solo vía casos de uso, una transacción por caso de uso.
- `socioId` siempre sale de la sesión. `acceso` define `Actor {id, rol, permisos[]}`, roles `socio|operador|admin`, enum cerrado de acciones y `autorizar(actor, accion, recurso)`. La consola vive en `/consola` con cookie y segundo factor propios.
- Autenticación detrás de `IdentityPort` (proveedor aún no decidido); cookie `httpOnly`, `Secure`, `SameSite=Lax`.
- Solo `productos` accede al núcleo por `NucleoPort` (solo lectura, timeout, sin caché); error `NUCLEO_NO_DISPONIBLE`; respuestas con `actualizadoEn`.
- Auditoría append-only (`registrar(evento)`, sin UPDATE/DELETE por permisos y trigger) en la misma transacción; evento con `actorId`, `rol`, `accion`, `recursoId`, `ts` UTC.
- Outbox transaccional: `OutboxMensaje {id, evento, socioId, plantilla, params}`; los productores no escriben direcciones; `notificaciones` resuelve el destinatario desde `acceso`; worker con reintentos vía `NotificadorPort`.
- Constancias: `@react-pdf/renderer`, al vuelo; se registra solo la emisión, tras generar el PDF con éxito, en una transacción. Cifrado en reposo.
- Convenciones: ids UUID v7; fechas UTC (se muestran en `America/Montevideo`); montos en centésimos + moneda; errores `{codigo, mensaje}` con códigos estables en mayúsculas; logs JSON con `requestId` sin datos personales; configuración por variables de entorno validadas al arranque; textos en español de Uruguay centralizados; formulario compartido con el mismo esquema en cliente y servidor; dominio/tablas en español, infraestructura en inglés, puertos `XxxPort`.

## Cross-Story Dependencies

- 1.1 crea el esqueleto, `acceso`, `auditoria` y el outbox que reutilizan 1.2 a 1.4 y las épicas 2 y 3.
- 1.3 y 1.4 dependen de la sesión y de `autorizar` de 1.1; 1.4 depende de `productos` (1.3).
- La interfaz real del núcleo y el proveedor de identidad están por definir: se usan adaptadores simulados detrás de los puertos.
