---
title: Portal de autoservicio para socios
status: final
created: 2026-10-17
updated: 2026-10-17
---

# PRD: Portal de autoservicio para socios
*Título de trabajo, a confirmar.*

## 0. Propósito del documento

Este PRD define los requisitos de la primera versión del portal de autoservicio de una cooperativa de ahorro y crédito uruguaya (unos 40.000 socios). Está dirigido a la gerencia, al PM y a quienes harán UX, arquitectura y épicas. Parte del brief `briefs/brief-portal-socios-2026-10-17/brief.md`. Los términos del Glosario se usan sin sinónimos. Los puntos inferidos se marcan `[SUPUESTO]` y se indexan al final.

## 1. Visión

Un portal web, adaptado a celular, donde el socio resuelve solo las gestiones más frecuentes: consultar saldos y préstamos, descargar constancias, pedir un préstamo simple y actualizar sus datos de contacto. Las solicitudes llegan estructuradas a una bandeja única donde el operador las atiende, en lugar de llegar por canales dispersos.

El socio gana autonomía y rapidez. La cooperativa libera capacidad del personal, mejora la calidad de sus datos de contacto y gana trazabilidad. El portal absorbe lo rutinario para que el personal dedique más tiempo a los casos que piden trato humano. No es un diferencial tecnológico sino una necesidad de servicio.

## 2. Usuarios objetivo

### 2.1 Trabajos a resolver (JTBD)

- **Socio:** "Quiero saber mi saldo o conseguir una constancia sin ir a la sucursal ni esperar un horario." "Quiero pedir un préstamo pequeño y saber en qué estado está." "Quiero confiar en que mis datos están seguros."
- **Operador:** "Quiero una cola clara con la información completa de cada solicitud, sin transcribir pedidos."
- **Cooperativa:** eficiencia, cumplimiento normativo y datos de contacto vigentes.

### 2.2 No usuarios (v1)

Personas que aún no son socias (altas de nuevos socios), y socios sin acceso digital, que siguen atendidos por los canales presenciales y telefónicos, que se mantienen.

### 2.3 Recorridos clave

- **UJ-1. Marta consulta su saldo y baja una constancia desde el celular.**
  - **Persona y contexto:** Marta, socia de 58 años, comerciante, usa el celular a diario pero evita los trámites digitales complejos. Necesita una constancia de saldos para un trámite bancario.
  - **Estado de entrada:** ya registrada, abre el portal desde el navegador del celular.
  - **Recorrido:** ingresa con sus credenciales, ve el resumen de cuentas de ahorro y préstamos, elige "Constancias" y selecciona "Constancia de saldos".
  - **Clímax:** el PDF se descarga en segundos con la fecha y los saldos vigentes.
  - **Resolución:** Marta adjunta el PDF a su trámite sin pisar la sucursal.
  - **Caso límite:** si olvidó su contraseña, usa la recuperación de acceso con verificación y vuelve al punto donde estaba.

- **UJ-2. Diego pide un préstamo simple y sigue su estado.**
  - **Persona y contexto:** Diego, socio de 34 años, necesita un préstamo pequeño para una reparación.
  - **Estado de entrada:** autenticado, con contacto verificado.
  - **Recorrido:** elige "Solicitar préstamo", completa el formulario guiado (producto, monto, plazo dentro de los límites), revisa el resumen y envía.
  - **Clímax:** recibe un número de solicitud y un correo de confirmación.
  - **Resolución:** días después ve el estado "En revisión". Una operadora le pide un documento y Diego lo adjunta desde el portal. Recibe la aprobación por correo.
  - **Caso límite:** si el monto excede el máximo del producto, el formulario lo indica antes de enviar.

- **UJ-3. Lucía atiende la bandeja de solicitudes.**
  - **Persona y contexto:** Lucía, operadora de back-office, hoy transcribe pedidos que llegan por varios canales.
  - **Estado de entrada:** autenticada en la consola de operador.
  - **Recorrido:** abre la bandeja, toma una solicitud de préstamo, revisa los datos completos, comenta que falta un documento y pasa la solicitud a "Información adicional". Cuando el socio responde, la aprueba.
  - **Clímax:** la solicitud queda resuelta con su registro de auditoría, sin transcribir nada.
  - **Resolución:** la bandeja muestra la siguiente solicitud pendiente por antigüedad.

## 3. Glosario

- **Socio** — persona asociada a la cooperativa, titular de cuentas de ahorro y/o préstamos. Usuario primario. Se usa "socio" y nunca "cliente".
- **Operador** — personal de back-office que atiende solicitudes en la consola.
- **Portal** — aplicación web del socio, adaptada a celular.
- **Consola de operador** — parte interna del portal donde trabaja el operador.
- **Núcleo operativo** — sistema central de la cooperativa, fuente de verdad de saldos y préstamos. `[SUPUESTO]` Ofrece una API o base de lectura utilizable.
- **Constancia** — documento PDF emitido por el portal que certifica un dato del socio (membresía, saldos, préstamo al día).
- **Solicitud** — pedido del socio que requiere decisión humana: de préstamo o de cambio de datos de contacto.
- **Bandeja** — lista única de solicitudes para el operador, con estado, asignación y comentarios.
- **Estado de solicitud** — Recibida, En revisión, Información adicional, Aprobada, Rechazada.
- **Dato de contacto** — teléfono, correo o domicilio del socio.
- **Registro de auditoría** — historial inmutable de quién hizo qué y cuándo sobre una solicitud o acceso.

## 4. Funcionalidades

### 4.1 Acceso seguro

**Descripción:** el socio se registra y accede con verificación de identidad y puede recuperar el acceso. Realiza UJ-1, UJ-2. `[SUPUESTO]` El método exacto de autenticación (cédula con validación, factor adicional, identidad digital nacional) no está definido; el PRD exige verificación de identidad y segundo factor, y se decide en arquitectura.

#### FR-1: Alta y acceso del socio

El socio puede registrarse en el portal verificando su identidad y acceder con credenciales y un segundo factor. Realiza UJ-1.

**Consecuencias (verificables):**
- Solo una persona con registro de socio vigente en el núcleo operativo puede completar el alta.
- El acceso exige un segundo factor.
- Tras 5 intentos fallidos consecutivos la cuenta se bloquea temporalmente y se notifica al socio.

#### FR-2: Recuperación de acceso

El socio puede recuperar su acceso mediante verificación de identidad, sin intervención de un operador en el caso común. Realiza UJ-1.

**Consecuencias (verificables):**
- La recuperación invalida las credenciales anteriores.
- Todo evento de recuperación queda en el registro de auditoría y se notifica por el contacto verificado.

### 4.2 Consulta de productos

**Descripción:** el socio ve el estado de sus cuentas de ahorro y préstamos con datos tomados del núcleo operativo. Realiza UJ-1.

#### FR-3: Consulta de saldos de ahorro

El socio puede ver el saldo y los últimos movimientos de sus cuentas de ahorro.

**Consecuencias (verificables):**
- Los datos mostrados provienen del núcleo operativo y muestran la fecha y hora de la última actualización.
- Si el núcleo operativo no responde, el portal informa la indisponibilidad y no muestra datos desactualizados como vigentes.

#### FR-4: Consulta de préstamos

El socio puede ver, por préstamo, sus cuotas, vencimientos, saldo pendiente y estado.

**Consecuencias (verificables):**
- Cada préstamo muestra la próxima cuota con su vencimiento y monto.
- Un socio solo ve sus propios préstamos.

### 4.3 Constancias

#### FR-5: Descarga de constancias en PDF

El socio puede generar y descargar constancias en PDF (membresía, saldos, préstamo al día). Realiza UJ-1.

**Consecuencias (verificables):**
- La constancia incluye fecha y hora de emisión, nombre del socio y un código de verificación.
- La emisión queda en el registro de auditoría.
- `[SUPUESTO]` Las constancias no requieren firma ni aprobación de un operador.

### 4.4 Solicitud de préstamo

**Descripción:** el socio solicita un préstamo simple mediante un formulario guiado con montos y plazos acotados, y sigue su estado. La decisión es siempre humana (sin scoring). Realiza UJ-2, UJ-3. `[SUPUESTO]` Los productos, límites y requisitos los define la cooperativa antes del desarrollo.

#### FR-6: Solicitud guiada de préstamo simple

El socio puede completar y enviar una solicitud de préstamo para un producto habilitado, con monto y plazo dentro de los límites definidos. Realiza UJ-2.

**Consecuencias (verificables):**
- El formulario valida los límites y los campos obligatorios antes de permitir el envío.
- Al enviar se asigna un número de solicitud y se envía una confirmación por correo.
- La solicitud llega a la bandeja con estado "Recibida".

**Fuera de alcance:** evaluación crediticia automática; desembolso de dinero.

#### FR-7: Seguimiento de solicitud y respuesta a pedidos de información

El socio puede ver el estado de sus solicitudes, leer los comentarios del operador y adjuntar la información adicional pedida. Realiza UJ-2.

**Consecuencias (verificables):**
- Cada cambio de estado notifica al socio por correo.
- Los adjuntos se limitan a formatos y tamaños definidos y se asocian a la solicitud.

### 4.5 Datos de contacto

#### FR-8: Actualización de datos de contacto con verificación

El socio puede solicitar el cambio de su teléfono, correo o domicilio. El teléfono y el correo se verifican con un código enviado al nuevo dato antes de registrarse como vigentes.

**Consecuencias (verificables):**
- Un teléfono o correo no verificado no reemplaza al vigente.
- Todo cambio genera una solicitud en la bandeja y se notifica al contacto anterior.
- `[SUPUESTO]` El cambio de domicilio requiere aprobación de un operador; teléfono y correo se aplican tras la verificación, sin aprobación.

### 4.6 Consola de operador

**Descripción:** vista interna con la bandeja única de solicitudes. Realiza UJ-3.

#### FR-9: Bandeja única de solicitudes

El operador puede ver, filtrar, asignarse y ordenar las solicitudes por tipo, estado y antigüedad. Realiza UJ-3.

**Consecuencias (verificables):**
- La bandeja muestra solicitudes de préstamo y de cambio de datos en una misma lista.
- Cada solicitud muestra los datos completos del socio y del pedido, sin consultar otros sistemas.

#### FR-10: Resolución de solicitudes

El operador puede aprobar, rechazar o pedir información adicional en una solicitud, con comentarios. Realiza UJ-3.

**Consecuencias (verificables):**
- Rechazar o pedir información exige un comentario visible para el socio.
- Cada acción actualiza el estado y notifica al socio.
- Toda acción queda en el registro de auditoría con operador, fecha y hora.

#### FR-11: Roles y permisos

El sistema distingue las capacidades del socio, del operador y de un administrador de la consola.

**Consecuencias (verificables):**
- Un socio no accede a la consola ni a datos de otros socios.
- Aprobar préstamos está limitado a operadores habilitados. `[SUPUESTO]` Una sola persona aprueba; la cooperativa puede exigir doble aprobación.

### 4.7 Notificaciones

#### FR-12: Notificaciones por correo (y SMS opcional)

El sistema notifica al socio por correo los eventos de sus solicitudes y los eventos de seguridad. `[SUPUESTO]` El SMS se incorpora solo si el costo lo permite.

**Consecuencias (verificables):**
- Se notifican: confirmación de solicitud, cambio de estado, cambio de contacto y recuperación de acceso.
- Un fallo de envío queda registrado y no bloquea la solicitud.

## 5. Requisitos no funcionales transversales

- **NFR-1 Seguridad y privacidad:** cumplimiento de la Ley 18.331 de protección de datos personales de Uruguay; cifrado en tránsito y en reposo; sesiones con expiración por inactividad. Se debe revisar la normativa del Banco Central del Uruguay aplicable a cooperativas de intermediación financiera. `[SUPUESTO]`
- **NFR-2 Disponibilidad:** al menos 99,5 % mensual para el portal.
- **NFR-3 Rendimiento:** las consultas de saldos y préstamos responden en menos de 3 segundos en el percentil 95 con conexión móvil estándar. `[SUPUESTO]`
- **NFR-4 Usabilidad y accesibilidad:** uso fluido en celular y navegadores comunes; interfaz clara para socios con poca comodidad digital; objetivo WCAG 2.1 AA. `[SUPUESTO]`
- **NFR-5 Trazabilidad:** registro de auditoría de accesos, constancias y toda acción sobre solicitudes, conservado según la política de retención que defina la cooperativa.
- **NFR-6 Integración:** los saldos y préstamos se leen del núcleo operativo, sin copias desfasadas; el portal no escribe saldos.

## 6. No objetivos

- No es una aplicación bancaria: sin transferencias, pagos ni movimientos de dinero.
- No decide créditos: sin scoring; la decisión es humana.
- No reemplaza los canales presenciales y telefónicos, que se mantienen.
- No es un chat ni un asistente conversacional.

## 7. Alcance del MVP

### 7.1 Dentro

Alta y acceso seguro, recuperación de acceso, consulta de saldos y préstamos, constancias en PDF, solicitud y seguimiento de préstamo simple, actualización de contacto con verificación, consola de operador (bandeja, estados, comentarios, auditoría) y notificaciones por correo.

### 7.2 Fuera del MVP

- Pagos de cuotas y simulador de préstamos (visión a 2-3 años).
- Aplicación móvil nativa.
- Apertura de cuentas o productos de ahorro y altas de nuevos socios.
- Votaciones y participación en asambleas (visión a largo plazo).
- Preaprobación con reglas transparentes.

## 8. Métricas de éxito

Metas orientativas `[SUPUESTO]`, a calibrar cuando exista línea base.

**Primarias**
- **SM-1 Adopción:** 30 % de socios activos registrados a los 6 meses y 50 % a los 12. Valida FR-1.
- **SM-2 Desvío de carga:** reducción de al menos 30 % de consultas de saldo y constancias atendidas por canales tradicionales. Valida FR-3, FR-4, FR-5.
- **SM-3 Eficiencia de préstamos:** respuesta a solicitudes simples en menos de 48 horas hábiles; más del 90 % de las solicitudes llegan completas. Valida FR-6, FR-7, FR-9, FR-10.

**Secundarias**
- **SM-4 Calidad de datos:** aumento de la proporción de socios con contacto verificado y vigente. Valida FR-8.
- **SM-5 Satisfacción:** al menos 4 sobre 5 en la encuesta posterior a la gestión. Valida FR-1 a FR-8.
- **SM-6 Confiabilidad y seguridad:** disponibilidad de al menos 99,5 % y cero incidentes de acceso indebido a datos de socios. Valida FR-1, FR-2, FR-11, NFR-1, NFR-2.

**Contramétricas (no optimizar)**
- **SM-C1 Contrapeso a SM-3:** tasa de aprobación de préstamos y morosidad posterior. No se debe acelerar la respuesta aprobando de forma indiscriminada.
- **SM-C2 Contrapeso a SM-1 y SM-2:** satisfacción y acceso de los socios que siguen en canales presenciales. No se debe empujar al socio hacia el portal degradando la atención presencial.

## 9. Preguntas abiertas

1. ¿Qué método de autenticación y verificación de identidad se usa? Es la decisión de mayor impacto en seguridad y adopción (bloquea arquitectura).
2. ¿Qué interfaz ofrece el núcleo operativo, y con qué capacidad y latencia?
3. ¿Qué productos de préstamo simple se habilitan, con qué montos, plazos y requisitos, y quién aprueba?
4. ¿Qué exige la normativa del Banco Central del Uruguay para cooperativas de intermediación financiera? Responsable sugerido: cumplimiento.
5. ¿Presupuesto, plazo y equipo disponibles? ¿Cuál es la línea base de volumen de gestiones?
6. ¿Política de retención del registro de auditoría?

## 10. Índice de supuestos

- §0, §3 Núcleo operativo: existe una API o base de lectura utilizable.
- §4.1 Autenticación con segundo factor; método exacto por definir.
- §4.4 Productos, límites y requisitos de préstamo los define la cooperativa.
- FR-5: las constancias no requieren aprobación de un operador.
- FR-8: domicilio con aprobación del operador; teléfono y correo tras verificación.
- FR-11: aprobación de préstamo por una sola persona.
- FR-12: SMS condicionado al costo.
- NFR-1, NFR-3, NFR-4: normativa BCU aplicable, latencia p95 y WCAG 2.1 AA.
- §8: todas las metas son orientativas, sin línea base.
