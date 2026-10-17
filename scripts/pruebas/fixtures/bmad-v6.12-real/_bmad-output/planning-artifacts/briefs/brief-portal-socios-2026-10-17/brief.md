---
title: "Brief de producto: Portal de autoservicio para socios"
status: final
created: 2026-10-17
updated: 2026-10-17
---

# Brief de producto: Portal de autoservicio para socios

> Los puntos marcados `[SUPUESTO]` fueron inferidos al elaborar el brief sin intervención del usuario. Deben validarse antes de pasar a PRD.

## Resumen ejecutivo

Una cooperativa de ahorro y crédito uruguaya, con unos 40.000 socios, necesita que sus socios resuelvan por sí mismos las gestiones más frecuentes: consultar saldos y préstamos, descargar constancias, pedir un préstamo simple y actualizar sus datos de contacto. Hoy esas gestiones pasan por atención presencial, telefónica o por mensajes, y cada una consume tiempo del personal.

El portal de autoservicio web mueve esas gestiones a un canal disponible las 24 horas. Las solicitudes entran estructuradas a una bandeja de trabajo para los operadores de back-office, que dejan de transcribir pedidos y de responder consultas repetitivas.

El beneficio es doble. El socio gana autonomía y rapidez. La cooperativa libera capacidad operativa y mejora la trazabilidad de las solicitudes, sin perder el vínculo cercano que la distingue de un banco.

## El problema

- **Socios:** consultas simples, como el saldo o una constancia para un trámite, exigen ir a una sucursal, llamar o escribir, y esperar dentro de un horario limitado. Pedir un préstamo pequeño implica un trámite con pocas ventanas de contacto.
- **Operadores:** una parte importante de su jornada se dedica a consultas repetitivas, emisión manual de constancias y carga de cambios de datos. Los pedidos llegan por canales dispersos y sin estado visible.
- **Cooperativa:** los datos de contacto desactualizados dificultan la comunicación y el cobro. Hay poca visibilidad sobre los tiempos de atención y la demanda real.

`[SUPUESTO]` No se dispone de métricas actuales (volumen de consultas, tiempos, costo por gestión). Medirlas es una tarea previa.

## La solución

Un portal web, de uso adaptado a celular, con acceso autenticado para el socio y una consola interna para operadores.

**Socio:**
- Consulta de saldos de cuentas de ahorro y estado de préstamos (cuotas, vencimientos, saldo pendiente).
- Descarga de constancias en PDF (socio, saldos, préstamo al día, etc.).
- Solicitud de préstamos simples mediante un formulario guiado, con seguimiento del estado.
- Actualización de datos de contacto (teléfono, correo, domicilio) con verificación.

**Operador de back-office:**
- Bandeja única de solicitudes (préstamos y cambios de datos) con estados, asignación y comentarios.
- Aprobación, rechazo o pedido de información adicional, con registro de auditoría.

## Qué lo hace diferente

No se pretende una ventaja tecnológica: el portal es una necesidad de servicio, no un diferencial de mercado. La diferencia está en el contexto:

- **Hecho a medida de la lógica cooperativa:** el socio, no el cliente, es el centro; los productos y reglas de crédito son los propios.
- **Integración con el núcleo operativo de la cooperativa**, con datos al día y no copias desfasadas. `[SUPUESTO]` Existe un sistema central con interfaz utilizable (API o base de datos de lectura).
- **Cercanía preservada:** el autoservicio absorbe lo rutinario para que el personal dedique más tiempo a los casos que requieren trato humano.

## A quién sirve

**Socio (usuario primario).** Persona de perfil muy variado, con distintos niveles de comodidad digital, que usa sobre todo el celular. Necesita resolver rápido, sin ir a la sucursal, y confiar en que sus datos están seguros. Éxito: completa su gestión en minutos sin ayuda.

**Operador de back-office (usuario secundario).** Atiende solicitudes y excepciones. Necesita una cola clara, información completa en cada solicitud y menos tareas manuales.

**Cooperativa (patrocinador).** Gerencia y comité buscan eficiencia, cumplimiento y mejor experiencia del socio.

## Criterios de éxito

`[SUPUESTO]` Metas orientativas, a calibrar con la línea base:

- **Adopción:** al menos 30 % de los socios activos registrados a los 6 meses y 50 % a los 12 meses.
- **Desvío de carga:** reducción de al menos 30 % de las consultas de saldo y constancias atendidas por canales tradicionales.
- **Eficiencia de préstamos:** tiempo de respuesta a solicitudes simples menor a 48 horas hábiles; más del 90 % de las solicitudes llegan completas.
- **Calidad de datos:** aumento de la proporción de socios con contacto verificado y vigente.
- **Satisfacción:** puntuación de satisfacción del socio de al menos 4 sobre 5 en la encuesta posterior a la gestión.
- **Confiabilidad:** disponibilidad de al menos 99,5 % y cero incidentes de acceso indebido a datos de socios.

## Alcance

**Primera versión (dentro):**
- Alta y acceso seguro del socio, con verificación de identidad y recuperación de acceso.
- Consulta de saldos y préstamos.
- Constancias en PDF.
- Solicitud de préstamo simple (un producto o pocos, con monto y plazo acotados) y seguimiento.
- Actualización de datos de contacto con verificación.
- Consola de operador: bandeja, estados, comentarios, auditoría.
- Notificaciones por correo (y SMS si el costo lo permite).

**Fuera de la primera versión:**
- Transferencias, pagos y movimientos de dinero.
- Evaluación crediticia automática (scoring); la decisión sigue siendo humana.
- Aplicación móvil nativa.
- Apertura de nuevas cuentas o productos de ahorro, y altas de nuevos socios.
- Chat o asistente conversacional.

## Riesgos, restricciones y preguntas abiertas

- **Seguridad y privacidad:** el portal maneja datos financieros y personales. Aplica la Ley 18.331 de protección de datos personales de Uruguay. Debe revisarse además la normativa del Banco Central del Uruguay para cooperativas de intermediación financiera. `[SUPUESTO]`
- **Autenticación de identidad:** no está definido el método (cédula con validación, factor adicional, identidad digital nacional). Es la decisión con mayor impacto en seguridad y adopción.
- **Integración con el sistema central:** su calidad y capacidad condicionan plazos y alcance.
- **Brecha digital:** parte de los socios, sobre todo los de mayor edad, no adoptará el portal. Los canales presenciales deben mantenerse.
- **Reglas de préstamos simples:** montos, plazos, requisitos y quién aprueba deben ser definidos por la cooperativa.
- **Pendiente:** presupuesto, plazo y equipo disponibles; línea base de volumen de gestiones.

## Visión

Si el portal funciona, se convierte en el canal principal de relación entre el socio y su cooperativa. En dos o tres años puede sumar pagos de cuotas, simulador de préstamos, aplicación móvil, preaprobación con reglas transparentes, comunicaciones y beneficios segmentados, y la participación del socio en la vida cooperativa (asambleas, votaciones). Todo ello sin perder el trato humano que caracteriza al cooperativismo.
