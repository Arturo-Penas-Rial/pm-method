# Ejercicio · E2E-1 · Opciones, plan de contingencia, presupuesto y revisión de riesgos de tu proyecto

## Cómo funciona este ejercicio

- **Para qué sirve:** llevar el caso a un proyecto tuyo. Vas a escribir las reglas de riesgo que fija la junta,
  comparar las opciones de respuesta de tu riesgo más alto, escribir su plan de contingencia, calcular un presupuesto de
  riesgo y revisar si tu registro sigue vivo.
- **Cuándo se hace:** la parte A, al cierre de la clase 1, después de la demostración (10 minutos); la parte B, al
  cierre de la clase 2, después de la demostración (10 minutos). Si lo hacés por tu cuenta, calculá 25 minutos. En la
  clase, A1 a A3 son el núcleo; si no llegás, A4 se completa después.
- **Qué hacés:** completás la hoja de trabajo con un proyecto propio, real o reciente, que tenga al menos un riesgo
  alto conocido. Alcanza con papel o una planilla, y con el orden de magnitud de los números. Si no tenés un proyecto,
  usá el escenario del caso: los datos de partida están en [Lo que necesitás saber](#lo-que-necesitás-saber).
- **Cómo te autoevaluás:** al final de cada parte hay una tabla de criterios. Marcá cuáles cumple tu hoja; un criterio
  sin cumplir es un hallazgo sobre tu proyecto, no un error del ejercicio.
- **Ejemplo resuelto:** al final está la hoja resuelta con el escenario del caso, y cada dato dice de qué paso de la
  guía sale. Miralo **después** de intentarlo, para comparar, no antes.

---

## Lo que necesitás saber

### El escenario del caso

Una cooperativa construye un portal de autoservicio para sus socios (WBS de 2.480 horas, USD 124.000). Laura Méndez es
la ejecutiva; Martín Suárez, el gestor; Sofía Ramírez, usuaria sénior, product owner y autoridad de cambio; Diego
Ferreira, proveedor sénior; Lucía Benítez, jefa de equipo. Se trabaja en sprints de 14 días. La clase 1 va del enfoque
de riesgo al presupuesto de riesgo; la clase 2 sigue la etapa de entrega hasta el 12/02, cuando la revisión de riesgos
lleva semanas sin hacerse y un disparador ya se alcanzó.

**Datos de partida para la parte A** (si usás el caso):

- Enfoque que el gestor lleva a la ejecutiva: apetito bajo en cumplimiento (Ley 18.331) y en seguridad del acceso,
  moderado en plazo y costo, abierto a oportunidades de reutilización; tolerancia: ningún riesgo alto sin respuesta y
  exposición de amenazas ≤ USD 60.000; el gestor compromete hasta USD 5.000 por respuesta aceptada y por encima decide
  la ejecutiva; revisión del registro en cada sprint y auditoría en cada fin de etapa.
- Riesgo alto para A2 y A3: **R-003**, el proveedor de SMS del segundo factor no cumple la disponibilidad y los socios
  no pueden ingresar. P3 × I5, impacto USD 25.000, EMV 12.500. Opciones que juntó el equipo:

| Opción | Qué es | Costo (USD) | Residual P × I | Impacto residual (USD) | Contingencia al disparo (USD) | EMV del secundario (USD) |
|---|---|---|---|---|---|---|
| evitar | app autenticadora (TOTP) en lugar de SMS | 7.000 | 1 × 3 | 6.000 | — | 4.000 (socios sin teléfono inteligente) |
| reducir | dos proveedores de SMS activos con conmutación | 9.000 | 1 × 4 | 25.000 | — | — |
| transferir | SLA de 99,9 % con penalidad de tope USD 2.000 por mes | 2.500 | 2 × 4 | 25.000 | — | 1.800 (la penalidad no cubre el atraso) |
| contingencia | acuerdo marco con un proveedor alternativo; activarlo si hay dos caídas en un mes | 0 | 3 × 3 | 8.000 | 12.000 | — |
| aceptar | sin acciones | 0 | 3 × 5 | 25.000 | — | — |

- Para A4: respuestas elegidas con costo USD 7.300 en total; EMV residual de las amenazas USD 32.500 (con la
  contingencia de R-003 ponderada); provisión para riesgos no identificados: 5 % del costo de la WBS (124.000), que va
  a la reserva de gestión.

**Datos de partida para la parte B** (al 12/02):

- La última revisión completa del registro fue el 15/12 y dejó la próxima para el 29/12, que no se hizo. R-007, un
  riesgo nuevo del 8/1, tenía la suya prevista para el 26/01. Riesgos abiertos: R-002, R-003, R-004, R-005 y R-007. La
  sanidad avisa con REG-09 en cada corrida desde el 12/01.
- La acción A-004 (entregar a la junta el análisis normativo; Martín Suárez) vencía el 05/02 y sigue abierta. La junta
  dejó una condición abierta sobre R-007 en su decisión del 12/01.
- El disparador de R-003 es «dos caídas del proveedor de SMS en un mes»; el proveedor cayó el 20/1 y el 3/2. Su plan de
  contingencia dice: activar el proveedor alternativo por USD 12.000 de la reserva de riesgo, con autorización de la
  ejecutiva.
- Usos de la reserva de riesgo (presupuesto de 39.800; reserva de gestión de 6.200 aparte, sin uso): C-001 respuestas planificadas, 7.300 · C-002 entorno de pruebas
  temporal para R-001, 8.000 · C-003 licencias de diseño sin riesgo citado, 3.000, rechazado el 18/12 · C-004 análisis
  normativo para R-007, 10.000 · C-005 activación del plan de contingencia de R-003, 12.000, el 15/02.
- EMV residual planificado de las amenazas abiertas al 15/02: R-002 4.500 · R-003 2.400 · R-004 3.600 · R-005 5.400 ·
  R-007 12.000.

### Conceptos mínimos

- **Apetito de riesgo:** cuánto riesgo acepta la organización en cada área (por ejemplo, poco en cumplimiento y más en
  plazo).
- **Tolerancia de riesgo:** el límite que, si se supera, obliga a escalar a la junta; en el caso, ningún riesgo alto sin
  respuesta y exposición ≤ USD 60.000.
- **P × I:** probabilidad e impacto, de 1 a 5; el producto da el nivel: alto ≥ 15, medio 6 a 12, bajo ≤ 5.
- **Probabilidad convertida:** P1 10 % · P2 30 % · P3 50 % · P4 70 % · P5 90 %.
- **EMV (valor monetario esperado):** impacto en dinero × probabilidad convertida. **Exposición:** la suma del EMV de
  las amenazas abiertas.
- **Opciones de respuesta** a una amenaza: evitar (cambiar el plan para que no ocurra), reducir (bajar probabilidad o
  impacto), transferir (pasar el impacto a un tercero), contingencia (preparar una acción que se activa con un
  disparador), aceptar; para una oportunidad, explotar. Se escala a la junta lo que excede la autoridad del gestor.
- **EMV residual:** probabilidad residual convertida × (impacto residual + contingencia por activar). Sin dato propio,
  el impacto residual es el original (no se rebaja).
- **Riesgo secundario:** el riesgo nuevo que crea una respuesta; su EMV se descuenta del valor de la opción.
- **Valor neto de una opción:** EMV antes − EMV residual − EMV del secundario − costo. La de mayor valor neto que deja
  el riesgo bajo la línea es la recomendada; elegir otra exige un motivo escrito (por ejemplo, el apetito).
- **Plan de contingencia:** disparador medible y alerta temprana, acciones con responsable, plazo y costo, monto y
  fuente (la reserva de riesgo), quién lo autoriza, cómo se registra la activación y qué hacer si falla.
- **Presupuesto de riesgo:** costo de las respuestas + EMV residual de las amenazas identificadas. Lo fija la
  ejecutiva. La provisión para riesgos no identificados va a la **reserva de gestión**, que solo libera la junta; el
  presupuesto de riesgo financia las respuestas y contingencias de los riesgos identificados.
- **Fecha de próxima revisión:** cuándo se vuelve a mirar cada riesgo; en pm-method, la sanidad avisa REG-09 cuando un
  riesgo abierto la pasa y CAM-03 cuando la reserva consumida llega al 80 %. El **radar** ordena lo pendiente en
  decidir, escalar, desbloquear y vigilar.

---

## Hoja de trabajo · parte A · Opciones, plan de contingencia y presupuesto de riesgo (clase 1)

**A1. Lo que decide la junta antes del taller.** Si no existe, escribí "no definido".

| Elemento | En mi proyecto | ¿Escrito y aprobado? (sí / no) | ¿Quién lo aprobó? |
|---|---|---|---|
| Apetito (dónde aceptamos poco riesgo y dónde más) | | | |
| Tolerancia de riesgo (regla y tope de exposición) | | | |
| Quién puede gastar la reserva y hasta qué monto | | | |
| Cada cuánto se revisa el registro | | | |

**A2. Opciones para tu riesgo más alto.** Riesgo: ……………………… P × I: …… Impacto (USD): ……… EMV antes: ………
Al menos tres opciones además de aceptar. Valor neto = EMV antes − EMV residual − EMV del secundario − costo.

| Opción | Costo | Residual P × I | EMV residual | EMV del secundario | Valor neto | ¿Queda bajo la línea? |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |
| aceptar | 0 | | | — | 0 | |

Elegida: ……… ¿Es la de mayor valor neto? Si no, motivo: ………………………………………………

**A3. Plan de contingencia** (de la opción contingencia de A2, aunque no la elijas).

| Disparador medible | Alerta temprana y quién la vigila | Acciones al disparo (quién, plazo) | Monto y fuente | Quién lo autoriza | Si falla |
|---|---|---|---|---|---|
| | | | | | |

**A4. Presupuesto de riesgo.**

| Costo de las respuestas | + EMV residual de las amenazas | = Presupuesto de riesgo | Aparte: reserva de gestión (provisión para no identificados, …… % del costo) |
|---|---|---|---|
| | | | |

### Autoevaluación de la parte A

| Criterio | Cumple si… |
|---|---|
| Reglas antes del taller | Los cuatro elementos de A1 tienen valor y alguien con autoridad los aprobó. |
| Opciones comparadas | A2 tiene al menos tres opciones además de aceptar, cada una con costo y residual, y el riesgo secundario descontado donde existe. |
| Elección justificada | La elegida es la de mayor valor neto bajo la línea, o tiene un motivo escrito. |
| Contingencia activable | A3 tiene un disparador que se puede observar (no "si las cosas empeoran"), un monto con fuente y una persona que la autoriza. |
| Presupuesto con fórmula | A4 suma los tres componentes; no es un porcentaje a ojo. |

---

## Hoja de trabajo · parte B · La revisión que se deja de hacer (clase 2)

**B1. Estado de tu registro hoy.**

| Pregunta | Respuesta |
|---|---|
| ¿Cuándo se revisó por última vez el registro completo? | |
| ¿Cuántos riesgos tienen una fecha de próxima revisión? ¿Cuántos la tienen vencida? | |
| ¿Quién o qué avisa cuando esa fecha pasa? ¿Desde cuándo está el aviso sin atender? | |
| ¿Cuántas acciones de respuesta están vencidas o hechas pero sin cerrar? | |
| ¿Algún disparador ya se alcanzó? ¿Hay un plan escrito para activar la contingencia? | |
| ¿Hay condiciones de la junta (o del comité) sin cumplir? | |
| De todo lo anterior, ¿qué es lo primero que hay que decidir hoy, y quién lo decide? | |

**B2. La reserva de riesgo.**

| Presupuesto de riesgo | Consumido | % | Remanente | EMV residual de las amenazas abiertas | ¿Algún gasto que no responde a un riesgo? |
|---|---|---|---|---|---|
| | | | | | |

**B3. Tu regla de revisión.** Completá en una línea: "Revisamos el registro cada ……… en ………………… (reunión), lo
dirige ………………, empezamos por ……………………, y avisamos a la junta cuando la reserva llega al …… %."

### Autoevaluación de la parte B

| Criterio | Cumple si… |
|---|---|
| Registro vivo | Ningún riesgo abierto tiene la revisión vencida por más de un ciclo (un sprint o un mes). |
| Acciones al día | Cero acciones vencidas sin replanificar ni cerrar. |
| Disparadores con dueño | Todo disparador alcanzado tiene su contingencia activada o una decisión escrita de no activarla. |
| Reserva con propósito | Cada gasto de la reserva cita el riesgo al que responde. |
| Alerta temprana | Hay un umbral de aviso (el caso usa 80 %) y una persona que decide qué hacer al cruzarlo. |

---

## Para ir más allá

- Si la reserva llega al 80 % a mitad de la etapa, ¿qué preferís: pedir a la junta que pase reserva de gestión al
  presupuesto de riesgo, concentrar la autoridad en la ejecutiva o pedir un plan de excepción? En el caso la ejecutiva
  eligió la segunda y dejó intacta la reserva de gestión, que es de la junta (guía, paso 13).
- En el caso, la junta eligió para R-007 una opción con valor neto negativo por el apetito bajo en cumplimiento (guía,
  paso 10). ¿En qué riesgo de tu proyecto pesaría más el apetito que el valor neto?
- ¿Qué urgencia de tu proyecto desplazaría hoy la revisión de riesgos, y quién se daría cuenta?

---

## Ejemplo resuelto (escenario del caso)

Cifras de la corrida de referencia ([salida-g1.md](../../guias/evidencia/salida-g1.md)); entre paréntesis, el paso de
la [guía E2E-1](../../guias/E2E-1-riesgos.md) de donde sale cada dato.

**A1.** Todo quedó escrito en el enfoque de riesgo v1.0, aprobado por Laura Méndez, ejecutiva, el 2026-10-28 (D-002)
(guía, paso 3).

| Elemento | En el caso | ¿Escrito y aprobado? | ¿Quién lo aprobó? |
|---|---|---|---|
| Apetito | bajo en cumplimiento (Ley 18.331) y en seguridad del acceso; moderado en plazo y costo; abierto a oportunidades de reutilización (paso 3) | sí | Laura Méndez, ejecutiva |
| Tolerancia de riesgo | ningún riesgo alto sin respuesta y exposición de amenazas ≤ USD 60.000 (pasos 1 y 3) | sí | Laura Méndez |
| Reserva | el gestor compromete hasta USD 5.000 por respuesta ya aceptada; por encima, o para un riesgo nuevo, decide la ejecutiva (paso 3) | sí | Laura Méndez |
| Revisión del registro | en cada sprint (14 días); reevaluación y auditoría en cada fin de etapa; vigilancia normativa mensual (paso 3) | sí | Laura Méndez |

**A2.** R-003, P3 × I5, impacto 25.000, EMV 12.500 (pasos 4 y 5); opciones calculadas por `riesgos.py opciones`
(paso 6a), USD:

| Opción | Costo | Residual P × I | EMV residual | EMV del secundario | Valor neto | ¿Bajo la línea? |
|---|---|---|---|---|---|---|
| contingencia ★ | 0 | 3 × 3 = 9 | 10.000 = 50 % × (8.000 + 12.000) | — | **2.500** | sí |
| reducir | 9.000 | 1 × 4 = 4 | 2.500 | — | 1.000 | sí |
| evitar | 7.000 | 1 × 3 = 3 | 600 | 4.000 | 900 | sí |
| transferir | 2.500 | 2 × 4 = 8 | 7.500 | 1.800 | 700 | sí |
| aceptar | 0 | 3 × 5 = 15 | 12.500 | — | 0 | no (sobre la línea) |

Elegida: contingencia, la recomendada; la registra Diego Ferreira, propietario, con `--elegir O4` (D-004) (paso 6a).
La respuesta más habitual para un proveedor que falla, el SLA con penalidad, es la de menor valor neto de las cuatro:
la penalidad no cubre el atraso.

**A3.** Plan de contingencia de R-003, aprobado por su propietario el 2026-11-04 (paso 6b):

| Disparador | Alerta temprana | Acciones | Monto y fuente | Autoriza | Si falla |
|---|---|---|---|---|---|
| dos caídas del proveedor de SMS en un mes | primera caída o disponibilidad mensual < 99,9 %; Lucía Benítez, en cada revisión del sprint | 1) Diego activa el proveedor alternativo en paralelo 6 meses (5 días hábiles); 2) Lucía conmuta el segundo factor y lo verifica (3 días hábiles más) | USD 12.000 de la reserva de riesgo | Laura Méndez, ejecutiva (supera los USD 5.000 del gestor) | correo como único segundo factor temporal y aviso a cumplimiento; excepción a la junta si el residual sigue sobre la línea |

**A4.** 7.300 de respuestas + 32.500 de EMV residual de las amenazas (R-001 a R-005) = **39.800** de presupuesto de
riesgo; aparte, 6.200 de provisión (5 % de 124.000) como reserva de gestión. La ejecutiva fija los dos montos el
2026-11-27 (D-008, nivel junta) (pasos 6b y 7).

**B1, al 12/02** (paso 12, salvo donde se indica).

| Pregunta | En el caso |
|---|---|
| Última revisión completa | 15/12, en la revisión del sprint 2 (paso 8) |
| Con fecha de próxima revisión / vencidos | 5 de 5 abiertos, los 5 vencidos: R-002, R-003, R-004 y R-005 desde el 29/12 (45 días); R-007 desde el 26/01 (17 días) |
| Quién avisa y desde cuándo | la sanidad, con REG-09, en cada corrida desde el 12/01 (pasos 10 y 12): un mes sin atender |
| Acciones vencidas | 1: A-004 (Martín Suárez, 2027-02-05) |
| Disparador alcanzado | R-003: caídas del 20/1 y del 3/2; el plan del paso 6b dice quién autoriza, cuánto y cómo se registra |
| Condiciones de la junta sin cumplir | 1: la de la `decision-ad-hoc` del 12/01 sobre R-007 (paso 10) |
| Lo primero de hoy | el radar: «Hoy: decidir R-003» (contingencia por activar, inminente); después, la condición de la junta |

**B2, al 15/02** (paso 13).

| Presupuesto | Consumido | % | Remanente | EMV residual de las amenazas abiertas | Gastos sin riesgo citado |
|---|---|---|---|---|---|
| 39.800 | 37.300 | 94 % | 2.500 | 27.900 | 0: C-003 se rechazó el 18/12 (paso 9) |

Consumido = 7.300 + 8.000 + 10.000 + 12.000 (C-001, C-002, C-004 y C-005; pasos 7, 9, 10 y 13). La activación del plan
de R-003 lleva la reserva al 94 %; la sanidad pasa CAM-03 a aviso y la ejecutiva decide mantener el presupuesto,
suspender la delegación de USD 5.000 al gestor hasta el límite de etapa y llevar a la junta lo que supere el remanente
(D-019, paso 13). La reserva de gestión (6.200) sigue sin uso: la libera solo la junta.

**B3.** "Revisamos el registro cada 14 días en la revisión del sprint, lo dirige el gestor, Martín Suárez, empezamos por
los REG-09 de la sanidad y el radar del día, y avisamos a la junta cuando la reserva llega al 80 %" (pasos 1, 3, 12 y
13). La lección L-002 del límite de etapa lo resume: «empezar cada revisión de sprint por los REG-09 de la sanidad del
día y no cerrarla con riesgos de revisión vencida, aunque haya urgencias» (paso 14).
