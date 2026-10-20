# Ejercicio · E2E-1 · El enfoque, el presupuesto y la revisión de riesgos de tu proyecto

**Para qué:** aplicar el caso a un proyecto propio (real o reciente) sin herramientas: papel o una planilla alcanzan.
**Duración:** parte A, 10 minutos (cierre de la clase 1); parte B, 10 minutos (cierre de la clase 2). Si hacés el
ejercicio solo, calculá 20 minutos en total. **Referencia:** [Guía E2E-1](../../guias/E2E-1-riesgos.md), pasos 3, 6, 7,
12 y 13.

Elegí un proyecto con al menos tres riesgos conocidos. No hace falta que los números sean exactos: alcanza con el orden
de magnitud. Conversión de probabilidad sugerida (la del caso): P1 10 % · P2 30 % · P3 50 % · P4 70 % · P5 90 %.

---

## Parte A · Enfoque y presupuesto de riesgo (clase 1)

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

## Parte B · La revisión que se deja de hacer (clase 2)

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

## Solución de referencia (escenario del caso)

Cifras de la corrida de referencia, `docs/guias/evidencia/salida-g1.md`.

**A1.** Apetito bajo en cumplimiento (Ley 18.331) y en seguridad del acceso, moderado en plazo y costo, abierto a
oportunidades de reutilización. Tolerancia: ningún riesgo alto sin respuesta y exposición de amenazas ≤ USD 60.000. El
gestor compromete hasta USD 5.000 por respuesta aceptada; por encima decide la ejecutiva. Revisión en cada sprint (14
días) y auditoría en cada fin de etapa. Aprobado por Laura Méndez, ejecutiva, el 2026-10-28 (D-002).

**A2.**

| Riesgo | P × I | Impacto (USD) | EMV antes | Respuesta | P residual | EMV residual | Costo | ¿Costo < ΔEMV? |
|---|---|---|---|---|---|---|---|---|
| R-001 sin entorno de pruebas del padrón | 4 × 4 | 30.000 | 21.000 | reducir (spike) | 2 | 9.000 | 2.000 | sí (12.000) |
| R-003 proveedor de SMS | 3 × 5 | 25.000 | 12.500 | transferir (SLA) | 2 | 7.500 | 2.500 | sí (5.000) |
| R-005 rotación del equipo | 3 × 3 | 18.000 | 9.000 | reducir (permanencia) | 2 | 5.400 | 3.000 | sí (3.600) |

Secundario: R-007, la penalidad del SLA de R-003 (tope de USD 2.000 por mes) no cubre el atraso: P2 × I3, EMV 1.800,
aceptar.

**A3.** 9.800 + 31.800 + 6.200 (5 % de 124.000) = **47.800**, fijado por la ejecutiva el 2026-11-27 (D-006).

**B1 al 12/02.** Última revisión completa: 15/12. Con fecha de próxima revisión: 6 de 6 abiertos, los 6 vencidos (45 días
R-002, R-003, R-004, R-005 y R-007; 17 días R-008). Aviso: la sanidad, con REG-09, en cada corrida desde el 12/01 (un
mes sin atender). Acciones vencidas: 1 (A-004). Disparador alcanzado: R-003 (caídas
del 20/1 y del 3/2). Condiciones abiertas: 1 (la de la `decision-ad-hoc` sobre R-008).

**B2 al 15/02.**

| Presupuesto | Consumido | % | Remanente | EMV residual de amenazas abiertas | Gastos sin riesgo citado |
|---|---|---|---|---|---|
| 47.800 | 38.800 | 81 % | 9.000 | 34.800 | 0 (C-003 se rechazó el 18/12) |

**B3.** "Revisamos el registro cada 14 días en la revisión del sprint, lo dirige Martín Suárez, y avisamos a la junta
cuando la reserva llega al 80 %" (CAM-03). Lección L-002: empezar cada revisión por los REG-09 de la sanidad y no
cerrarla con revisiones vencidas, aunque haya urgencias.
