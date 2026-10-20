# Ejercicio · E2E-1 · El enfoque, el presupuesto y la revisión de riesgos de tu proyecto

## Cómo funciona este ejercicio

- **Para qué sirve:** llevar el caso a un proyecto tuyo. Vas a escribir las reglas de riesgo que fija la junta, costear
  tres respuestas, calcular un presupuesto de riesgo y revisar si tu registro sigue vivo.
- **Cuándo se hace:** la parte A, al cierre de la clase 1, después de la demostración (10 minutos); la parte B, al
  cierre de la clase 2, después de la demostración (10 minutos). Si lo hacés por tu cuenta, calculá 20 minutos.
- **Qué hacés:** completás la hoja de trabajo con un proyecto propio, real o reciente, que tenga al menos tres riesgos
  conocidos. Alcanza con papel o una planilla, y con el orden de magnitud de los números. Si no tenés un proyecto,
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
lleva semanas sin hacerse.

**Datos de partida para la parte A** (si usás el caso):

- Enfoque que el gestor lleva a la ejecutiva: apetito bajo en cumplimiento (Ley 18.331) y en seguridad del acceso,
  moderado en plazo y costo, abierto a oportunidades de reutilización; tolerancia: ningún riesgo alto sin respuesta y
  exposición de amenazas ≤ USD 60.000; el gestor compromete hasta USD 5.000 por respuesta aceptada y por encima decide
  la ejecutiva; revisión del registro en cada sprint y auditoría en cada fin de etapa.
- Tres riesgos del taller con la respuesta propuesta:

| Riesgo | P × I | Impacto (USD) | Respuesta propuesta | P residual | Costo (USD) |
|---|---|---|---|---|---|
| R-001 el padrón no tiene entorno de pruebas | 4 × 4 | 30.000 | reducir: spike de integración con datos sintéticos | 2 | 2.000 |
| R-003 el proveedor de SMS no cumple la disponibilidad | 3 × 5 | 25.000 | transferir: SLA con penalidad, con tope de USD 2.000 por mes | 2 | 2.500 |
| R-005 el proveedor rota desarrolladores | 3 × 3 | 18.000 | reducir: cláusula de permanencia | 2 | 3.000 |

- Para A3, el resto del registro: R-002 (respuesta USD 1.500, EMV residual 4.500), R-004 (aceptar, sin costo, EMV
  residual 3.600) y R-006 (oportunidad, respuesta USD 800). La transferencia de R-003 no cubre el costo del atraso: si
  lo registrás como riesgo secundario, es P2 × I3 con un impacto de USD 6.000. La provisión para riesgos no
  identificados es el 5 % del costo de la WBS.

**Datos de partida para la parte B** (al 12/02):

- La última revisión completa del registro fue el 15/12 y dejó la próxima para el 29/12, que no se hizo. R-008, un
  riesgo nuevo del 8/1, tenía la suya prevista para el 26/01. Riesgos abiertos: R-002, R-003, R-004, R-005, R-007 y
  R-008. La sanidad avisa con REG-09 en cada corrida desde el 12/01.
- La acción A-004 (entregar a la junta el análisis normativo; Martín Suárez) vencía el 05/02 y sigue abierta. La junta
  dejó una condición abierta sobre R-008 en su decisión del 12/01.
- El disparador de R-003 es «dos caídas del proveedor en un mes»; el proveedor cayó el 20/1 y el 3/2.
- Usos de la reserva de riesgo (presupuesto de 47.800): C-001 respuestas planificadas, 9.800 · C-002 entorno de
  pruebas temporal para R-001, 8.000 · C-003 licencias de diseño sin riesgo citado, 3.000, rechazado el 18/12 · C-004
  análisis normativo para R-008, 10.000 · C-005 contingencia de R-003, 11.000, el 15/02.
- EMV residual planificado de las amenazas abiertas al 15/02: R-002 4.500 · R-003 7.500 · R-004 3.600 · R-005 5.400 ·
  R-007 1.800 · R-008 12.000.

### Conceptos mínimos

- **Apetito de riesgo:** cuánto riesgo acepta la organización en cada área (por ejemplo, poco en cumplimiento y más en
  plazo).
- **Tolerancia de riesgo:** el límite que, si se supera, obliga a escalar a la junta; en el caso, ningún riesgo alto sin
  respuesta y exposición ≤ USD 60.000.
- **P × I:** probabilidad e impacto, de 1 a 5; el producto da el nivel: alto ≥ 15, medio 6 a 12, bajo ≤ 5.
- **Probabilidad convertida:** P1 10 % · P2 30 % · P3 50 % · P4 70 % · P5 90 %.
- **EMV (valor monetario esperado):** impacto en dinero × probabilidad convertida. **Exposición:** la suma del EMV de
  las amenazas abiertas.
- **Respuesta:** reducir, transferir, aceptar o escalar una amenaza; explotar una oportunidad. Se justifica por los
  números si cuesta menos que la reducción de EMV que logra (ΔEMV); si no, necesita una razón no económica escrita.
- **EMV residual:** impacto en dinero × probabilidad residual convertida, después de la respuesta (el impacto no se
  rebaja).
- **Riesgo secundario:** el riesgo nuevo que crea una respuesta.
- **Presupuesto de riesgo:** costo de las respuestas + EMV residual de las amenazas + provisión para riesgos no
  identificados. Lo fija la ejecutiva; es distinto de la reserva de gestión, que solo libera la junta.
- **Disparador:** el hecho observable que indica que el riesgo está ocurriendo y activa la contingencia.
- **Fecha de próxima revisión:** cuándo se vuelve a mirar cada riesgo; en pm-method, la sanidad avisa REG-09 cuando un
  riesgo abierto la pasa y CAM-03 cuando la reserva consumida llega al 80 %.

---

## Hoja de trabajo · parte A · Enfoque y presupuesto de riesgo (clase 1)

**A1. Lo que decide la junta antes del taller.** Si no existe, escribí "no definido".

| Elemento | En mi proyecto | ¿Escrito y aprobado? (sí / no) | ¿Quién lo aprobó? |
|---|---|---|---|
| Apetito (dónde aceptamos poco riesgo y dónde más) | | | |
| Tolerancia de riesgo (regla y tope de exposición) | | | |
| Quién puede gastar la reserva y hasta qué monto | | | |
| Cada cuánto se revisa el registro | | | |

**A2. Tres riesgos con su respuesta.** EMV = impacto en dinero × probabilidad convertida.

| Riesgo | P × I | Impacto (USD) | EMV antes | Respuesta | P residual | EMV residual | Costo de la respuesta | ¿Costo < reducción de EMV? |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |

¿Alguna respuesta crea un riesgo nuevo (secundario)? Anotalo: ……………………………………………

**A3. Presupuesto de riesgo.**

| Costo de las respuestas | + EMV residual de las amenazas | + Provisión para no identificados (…… % del costo) | = Presupuesto de riesgo |
|---|---|---|---|
| | | | |

### Autoevaluación de la parte A

| Criterio | Cumple si… |
|---|---|
| Reglas antes del taller | Los cuatro elementos de A1 tienen valor y alguien con autoridad los aprobó. |
| Respuestas justificadas | Cada respuesta cumple costo < reducción de EMV, o tiene una justificación no económica escrita (apetito, cumplimiento). |
| Secundarios a la vista | Revisaste si cada respuesta crea un riesgo nuevo y, si lo crea, está en la tabla. |
| Presupuesto con fórmula | A3 suma los tres componentes; no es un porcentaje a ojo. |

---

## Hoja de trabajo · parte B · La revisión que se deja de hacer (clase 2)

**B1. Estado de tu registro hoy.**

| Pregunta | Respuesta |
|---|---|
| ¿Cuándo se revisó por última vez el registro completo? | |
| ¿Cuántos riesgos tienen una fecha de próxima revisión? ¿Cuántos la tienen vencida? | |
| ¿Quién o qué avisa cuando esa fecha pasa? ¿Desde cuándo está el aviso sin atender? | |
| ¿Cuántas acciones de respuesta están vencidas o hechas pero sin cerrar? | |
| ¿Algún disparador ya se alcanzó y nadie activó la contingencia? | |
| ¿Hay condiciones de la junta (o del comité) sin cumplir? | |

**B2. La reserva de riesgo.**

| Presupuesto de riesgo | Consumido | % | Remanente | EMV residual de las amenazas abiertas | ¿Algún gasto que no responde a un riesgo? |
|---|---|---|---|---|---|
| | | | | | |

**B3. Tu regla de revisión.** Completá en una línea: "Revisamos el registro cada ……… en ………………… (reunión), lo
dirige ………………, y avisamos a la junta cuando la reserva llega al …… %."

### Autoevaluación de la parte B

| Criterio | Cumple si… |
|---|---|
| Registro vivo | Ningún riesgo abierto tiene la revisión vencida por más de un ciclo (un sprint o un mes). |
| Acciones al día | Cero acciones vencidas sin replanificar ni cerrar. |
| Reserva con propósito | Cada gasto de la reserva cita el riesgo al que responde. |
| Alerta temprana | Hay un umbral de aviso (el caso usa 80 %) y una persona que decide qué hacer al cruzarlo. |

---

## Para ir más allá

- Si la reserva llega al 80 % a mitad de la etapa, ¿qué preferís: ampliarla con reserva de gestión, concentrar la
  autoridad en la ejecutiva o pedir un plan de excepción? En el caso la ejecutiva eligió la segunda (guía, paso 13).
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

**A2.** P × I e impacto del taller (pasos 4 y 5); respuesta, residual, costo y ΔEMV (paso 6).

| Riesgo | P × I | Impacto (USD) | EMV antes | Respuesta | P residual | EMV residual | Costo | ¿Costo < ΔEMV? |
|---|---|---|---|---|---|---|---|---|
| R-001 sin entorno de pruebas del padrón | 4 × 4 | 30.000 | 21.000 | reducir (spike) | 2 | 9.000 | 2.000 | sí (12.000) |
| R-003 proveedor de SMS | 3 × 5 | 25.000 | 12.500 | transferir (SLA) | 2 | 7.500 | 2.500 | sí (5.000) |
| R-005 rotación del equipo | 3 × 3 | 18.000 | 9.000 | reducir (permanencia) | 2 | 5.400 | 3.000 | sí (3.600) |

Secundario: R-007, porque la penalidad del SLA de R-003 (tope de USD 2.000 por mes) no cubre el costo del atraso: P2 ×
I3, impacto 6.000, EMV 1.800, aceptar (paso 6).

**A3.** 9.800 de respuestas + 31.800 de EMV residual de las amenazas (R-001 a R-005 y R-007) + 6.200 de provisión (5 %
de 124.000) = **47.800**, que la ejecutiva fija el 2026-11-27 (D-006) (pasos 6 y 7).

**B1, al 12/02** (paso 12, salvo donde se indica).

| Pregunta | En el caso |
|---|---|
| Última revisión completa | 15/12, en la revisión del sprint 2 (paso 8) |
| Con fecha de próxima revisión / vencidos | 6 de 6 abiertos, los 6 vencidos: R-002, R-003, R-004, R-005 y R-007 desde el 29/12 (45 días); R-008 desde el 26/01 (17 días) |
| Quién avisa y desde cuándo | la sanidad, con REG-09, en cada corrida desde el 12/01 (pasos 10 y 12): un mes sin atender |
| Acciones vencidas | 1: A-004 (Martín Suárez, 2027-02-05) |
| Disparador alcanzado sin contingencia | R-003: caídas del 20/1 y del 3/2 |
| Condiciones de la junta sin cumplir | 1: la de la `decision-ad-hoc` del 12/01 sobre R-008 (paso 10) |

**B2, al 15/02** (paso 13).

| Presupuesto | Consumido | % | Remanente | EMV residual de las amenazas abiertas | Gastos sin riesgo citado |
|---|---|---|---|---|---|
| 47.800 | 38.800 | 81 % | 9.000 | 34.800 | 0: C-003 se rechazó el 18/12 (paso 9) |

Consumido = 9.800 + 8.000 + 10.000 + 11.000 (C-001, C-002, C-004 y C-005; pasos 7, 9, 10 y 13). Al cruzar el 80 %, la
sanidad pasa CAM-03 a aviso y la ejecutiva decide mantener el presupuesto y suspender la delegación de USD 5.000 al
gestor hasta el límite de etapa (D-015, paso 13).

**B3.** "Revisamos el registro cada 14 días en la revisión del sprint, lo dirige el gestor, Martín Suárez, y avisamos a
la junta cuando la reserva llega al 80 %" (pasos 1, 3, 12 y 13). La lección L-002 del límite de etapa lo resume:
«empezar cada revisión de sprint por los REG-09 de la sanidad del día y no cerrarla con riesgos de revisión vencida,
aunque haya urgencias» (paso 14).
