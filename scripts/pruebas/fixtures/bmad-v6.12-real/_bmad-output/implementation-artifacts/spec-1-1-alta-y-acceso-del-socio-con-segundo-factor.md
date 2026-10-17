---
title: 'Alta y acceso del socio con segundo factor (Historia 1.1)'
type: 'feature'
created: '2026-10-17'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** El repositorio está vacío y el socio no tiene forma de registrarse ni de acceder al portal; sin identidad, sesión, autorización, auditoría y outbox no pueden construirse el resto de la Épica 1 ni las Épicas 2 y 3.

**Approach:** Inicializar el monolito modular hexagonal y construir en `acceso` el alta (verificación contra el núcleo vía `IdentityPort`), el ingreso con credenciales más segundo factor, la sesión y `autorizar`, con bloqueo a los 5 fallos, `auditoria.registrar` append-only y outbox con worker para el aviso de bloqueo.

**Decisions (human):** (1) El segundo factor es TOTP con app autenticadora. (2) La identidad en el alta se verifica con la cédula más un código enviado al contacto que figura en el núcleo.

## Boundaries & Constraints

**Always:** Seguir la arquitectura: `socioId` solo desde la sesión; cookie `httpOnly`/`Secure`/`SameSite=Lax` con expiración por inactividad; auditoría en la misma transacción que la acción; productores del outbox sin direcciones (`OutboxMensaje {id, evento, socioId, plantilla, params}`); ids UUID v7, fechas UTC, errores `{codigo, mensaje}`, textos en español de Uruguay centralizados, logs JSON sin datos personales; configuración por variables de entorno validadas al arranque; módulos solo se llaman por casos de uso públicos.

**Never:** No implementar recuperación de acceso (1.2), saldos (1.3), constancias (1.4), consola ni sesión de operador (3.1). No escribir saldos ni guardar secretos o credenciales en claro. No acoplar el dominio a un proveedor de identidad: el adaptador real queda diferido y se usa uno simulado para dev/pruebas. No permitir `UPDATE` ni `DELETE` sobre auditoría.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Alta válida | Persona con socio vigente en el núcleo, identidad verificada | Se crea el usuario en `acceso`, habilitado para acceder; evento auditado | N/A |
| Alta sin vigencia | Persona sin registro vigente o con identidad no verificada | No se crea usuario | `{codigo: 'SOCIO_NO_VIGENTE', mensaje}` |
| Alta duplicada | Socio que ya tiene usuario | No se crea otro usuario | `{codigo: 'USUARIO_YA_REGISTRADO', mensaje}` |
| Ingreso válido | Credenciales y segundo factor correctos | Sesión con cookie segura; contador de fallos en 0; acceso auditado | N/A |
| Fallo de credencial o factor | Dato incorrecto, menos de 5 fallos consecutivos | Sin sesión; fallo auditado; contador +1 | `{codigo: 'CREDENCIALES_INVALIDAS', mensaje}` genérico |
| Quinto fallo | 4 fallos previos y falla otro | Cuenta bloqueada temporalmente; `OutboxMensaje` de bloqueo y auditoría en la misma transacción | `{codigo: 'CUENTA_BLOQUEADA', mensaje}` |
| Ingreso con cuenta bloqueada | Dentro de la ventana de bloqueo, incluso con datos correctos | Sin sesión; intento auditado | `{codigo: 'CUENTA_BLOQUEADA', mensaje}` |
| Sesión inactiva | Sesión sin actividad más allá del límite | Sesión inválida | `{codigo: 'SESION_EXPIRADA', mensaje}` |
| Acceso a datos ajenos | Actor socio A pide recurso del socio B | `autorizar` deniega | `{codigo: 'ACCESO_DENEGADO', mensaje}` |
| Fallo de envío | El worker no logra enviar el aviso | Reintenta y registra el fallo; el bloqueo no se revierte | Registro del fallo |

</frozen-after-approval>

## Code Map

Repositorio sin código de aplicación (solo `_bmad/`, `_bmad-output/`, `.claude/`); todo es nuevo. Node instalado: v22.22.0 (la arquitectura fija 24 LTS; usar `engines` y `.nvmrc` en 24 y no depender de nada exclusivo de 24 en esta historia).

- `package.json`, `tsconfig.json`, `next.config.ts`, `drizzle.config.ts`, `eslint.config.mjs`, `vitest.config.ts` -- toolchain: Next.js 16.4.2, React 19.3.1, TypeScript 7.0.2, drizzle-orm 0.45.4, Vitest
- `src/shared/config.ts`, `src/shared/errors.ts`, `src/shared/ids.ts`, `src/shared/textos.ts`, `src/shared/logger.ts` -- entorno validado con zod, `AppError {codigo, mensaje}`, UUID v7, textos centralizados, logger JSON
- `src/modules/acceso/{domain,app,adapters}` -- `Usuario`, `Actor`, enum de acciones, `autorizar`, `IdentityPort`, casos de uso `registrarSocio` e `ingresar`, sesión; adaptador simulado de identidad y del núcleo para dev
- `src/modules/auditoria/` -- `registrar(evento)` y adaptador Postgres
- `src/modules/notificaciones/` -- contrato `OutboxMensaje`, tabla `outbox`, `NotificadorPort`
- `src/modules/{productos,constancias,solicitudes}/` -- solo carpetas con `README`/`index.ts` vacío; sin lógica
- `src/app/(portal)/{registro,ingreso}/` y `src/app/api/` -- páginas y rutas que solo delegan; mobile-first y accesibles (etiquetas, foco, errores asociados)
- `worker/index.ts` -- bucle del outbox con reintentos y registro de fallos
- `db/migrations/` -- usuarios, intentos/bloqueo, sesiones, auditoría con trigger y permisos que impiden UPDATE/DELETE, outbox
- `.github/workflows/ci.yml` -- lint y pruebas sobre Postgres de servicio

## Tasks & Acceptance

**Execution:**
- [ ] `package.json`, configs y estructura `src/`, `worker/`, `db/migrations/` -- crear el esqueleto con los seis módulos hexagonales -- AC del repositorio vacío
- [ ] `src/shared/config.ts` -- validar variables de entorno al arranque y fallar con mensaje claro; incluir ventana de bloqueo (default 15 min) e inactividad (default 30 min) como configuración -- evitar valores fijos
- [ ] `db/migrations/*` y esquemas drizzle por módulo -- tablas de `acceso`, `auditoria` (append-only con trigger y revocación de permisos) y `outbox`, un dueño por tabla -- AD-2 y AD-6
- [ ] `src/modules/auditoria` -- `registrar(evento)` que acepta la transacción del llamador -- misma transacción
- [ ] `src/modules/acceso` -- `IdentityPort` con adaptador simulado, `registrarSocio`, `ingresar`, contador de fallos y bloqueo, sesión por cookie, `Actor` y `autorizar` -- núcleo de la historia
- [ ] `src/modules/notificaciones` y `worker/index.ts` -- insertar `OutboxMensaje` de bloqueo en la transacción del quinto fallo; el worker resuelve destinatario desde `acceso`, reintenta y registra fallos -- AD-7 y AD-10
- [ ] `src/app/(portal)` -- pantallas de registro e ingreso con formulario compartido (mismo esquema en cliente y servidor) -- NFR-4
- [ ] `**/*.test.ts` -- pruebas unitarias de la matriz I/O y de integración con Postgres (auditoría inmutable, transacción con outbox) -- verificación
- [ ] `.github/workflows/ci.yml` -- pipeline de lint y pruebas -- AC del pipeline

**Acceptance Criteria:**
- Given un repositorio vacío, when se completa la historia, then existen el esqueleto indicado y la configuración falla al arrancar si falta una variable requerida
- Given un socio vigente, when completa el alta, then queda un usuario en `acceso`; y una persona sin vigencia recibe `{codigo, mensaje}` sin usuario creado
- Given un ingreso válido, when se crea la sesión, then la cookie es `httpOnly`, `Secure` y `SameSite=Lax`, expira por inactividad y ningún caso de uso acepta `socioId` por parámetro
- Given 4 fallos consecutivos, when ocurre el quinto, then la cuenta se bloquea, hay un `OutboxMensaje` y un evento auditado, y el worker lo procesa con reintentos
- Given cualquier acceso exitoso o fallido, when se registra, then `auditoria` guarda `actorId`, `rol`, `accion`, `recursoId` y `ts` UTC, y un UPDATE o DELETE sobre ella es rechazado por la base

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Decisiones propias (invisibles para el usuario, ajustables): contraseñas con argon2id; sesión con token opaco aleatorio guardado como hash en tabla y renovación de `ultimoUso` en cada petición (la expiración por inactividad se evalúa en servidor); mensaje de error genérico para credencial o factor inválido, para no revelar qué dato falló; npm como gestor de paquetes; Vitest; GitHub Actions como CI. El contador de fallos se reinicia con un ingreso exitoso y el bloqueo vence solo por tiempo.

## Verification

**Commands:**
- `npm run lint` -- expected: sin errores
- `npm test` -- expected: todas las pruebas pasan, incluida la inmutabilidad de auditoría
- `npm run build` -- expected: compila Next.js sin errores de tipos
