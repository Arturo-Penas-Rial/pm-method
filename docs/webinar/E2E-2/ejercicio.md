# Ejercicio · E2E-2 · La línea base de cambio y la tabla de impacto de tu proyecto

**Para qué:** aplicar el caso a un proyecto propio (real o reciente) sin herramientas: papel o una planilla alcanzan.
**Duración:** parte A, 10 minutos (cierre de la clase 1); parte B, 10 minutos (cierre de la clase 2). Si hacés el
ejercicio solo, calculá 20 minutos en total. **Referencia:** [Guía E2E-2](../../guias/E2E-2-alcance-roadmap.md), pasos 5,
7 y 10.

Elegí un proyecto con al menos un cambio de alcance en los últimos meses. No hace falta que los números sean exactos:
alcanza con el orden de magnitud.

---

## Parte A · La línea base de cambio (clase 1)

**A1. Tres números que fija la junta.** Completá lo que existe hoy en tu proyecto. Si no existe, escribí "no definido".

| Elemento | Valor en mi proyecto | ¿Está escrito y aprobado? (sí / no) | ¿Quién lo aprobó? |
|---|---|---|---|
| Tolerancia de tiempo del proyecto | | | |
| Tolerancia de costo del proyecto | | | |
| Límite por cambio de quien aprueba cambios | | | |
| Presupuesto de cambio (monto total para cambios) | | | |

**A2. El margen de alcance.** ¿Qué parte de tu alcance es Should/Could (lo que se puede retirar sin pedir permiso)?

| Total del alcance (puntos, horas o productos) | Must | Should + Could | Margen = (Should + Could) / total |
|---|---|---|---|
| | | | % |

**A3. Trazabilidad.** ¿Cuándo se actualizó por última vez la relación requisito → historia o tarea → paquete de trabajo?

- [ ] En la última semana · [ ] En el último mes · [ ] Al planificar · [ ] Nunca se armó

### Autoevaluación de la parte A

| Criterio | Cumple si… |
|---|---|
| Línea base de cambio completa | Los cuatro elementos de A1 tienen valor, están escritos y tienen quien los aprobó. |
| Autoridad delimitada | El límite por cambio es menor que el presupuesto de cambio (si no, un solo cambio lo agota). |
| Margen conocido | Sabés el porcentaje de A2 y quién decide retirar Should/Could. |
| Trazabilidad viva | A3 es "en la última semana" o se regenera en cada sincronización. |

---

## Parte B · La tabla de impacto de un cambio real (clase 2)

**B1. Elegí un cambio** que se haya aprobado en tu proyecto. Describilo en una línea:

> Cambio: ……………………………………………… · ¿Quién lo aprobó? …………………… · ¿Cuándo? ……………

**B2. Completá la tabla de impacto como si fuera antes de decidir.**

| Objetivo | Antes | Con el cambio | Contra qué se mide | Lectura (dentro / fuera / riesgo) |
|---|---|---|---|---|
| Tiempo (fecha de fin o camino crítico) | | | tolerancia de tiempo | |
| Reserva de cronograma | | | lo que quedaba antes del cambio | |
| Costo y presupuesto de cambio | | | presupuesto de cambio (saldo) | |
| Autoridad | | | límite por cambio | |
| Capacidad del equipo o del release | | | velocidad × iteraciones | |
| Business case (VAN o beneficio esperado) | | | VAN de la línea base o meta del beneficio | |

**B3. ¿Qué camino le correspondía?** Marcá uno y justificá en una línea.

- [ ] Intercambio del product owner (no toca Must, fecha ni costo)
- [ ] Autoridad de cambio (dentro del límite por cambio y del saldo del presupuesto)
- [ ] Excepción a la junta (supera el límite, el presupuesto o una tolerancia)

> Justificación: ……………………………………………………………………………………………

### Autoevaluación de la parte B

| Criterio | Cumple si… |
|---|---|
| Impacto completo | Completaste al menos tiempo, costo, autoridad, capacidad y business case (no solo el costo). |
| Antes de decidir | Las cifras de "Con el cambio" se podían conocer antes de aprobarlo. |
| Camino correcto | El camino de B3 coincide con quien aprobó en B1; si no coincide, encontraste un caso de autoridad excedida. |
| Riesgo derivado | Si la reserva quedó chica, registraste (o registrarías) un riesgo con disparador. |

---

## Solución de referencia (escenario del caso)

**Parte A** (Portal de autoservicio para socios, paso 5 de la guía):

| Elemento | Valor | ¿Escrito y aprobado? | ¿Quién? |
|---|---|---|---|
| Tolerancia de tiempo del proyecto | ±3 semanas (15 días laborables) | sí (`estado.py tolerancia`) | Laura Méndez, ejecutiva |
| Tolerancia de costo del proyecto | ±8 % | sí | Laura Méndez |
| Límite por cambio | 10.000 | sí (`estado.py presupuesto … limite_autoridad_cambio=10000`) | Laura Méndez, para Sofía Ramírez |
| Presupuesto de cambio | 12.000 | sí (`estado.py presupuesto cambio=12000`) | Laura Méndez |

Margen de alcance: 20 % Should/Could (el valor de `--pct-no-must 20` del EVM). Trazabilidad: se regenera en cada
sincronización con BMAD; en el paso 2 da 12 de 12 requisitos funcionales con historia y paquete, y en el paso 8, 13 de 13.

**Parte B, cambio C-001** (simulador de préstamo, paso 7): camino **autoridad de cambio**.

| Objetivo | Antes | Con C-001 | Contra qué se mide | Lectura |
|---|---|---|---|---|
| Tiempo | 110 días · fin 2027-05-03 | 121 días · fin 2027-05-18 | ±3 semanas = 15 días | dentro (11 de 15) |
| Reserva | 2σ = 13,0 días | 2,0 días | atraso posible | riesgo: R-001 |
| Costo y presupuesto | 0 de 12.000 | 9.000 de 12.000 (75 %) | saldo del presupuesto | dentro |
| Autoridad | — | 9.000 | límite 10.000 | dentro |
| Capacidad R2 | 21 pts de 24 | 29 pts de 24 | velocidad 8 × 3 sprints | +1 sprint (32 pts) |
| Business case | VAN 39.776 | VAN 45.939 (+6.163) | VAN a 5 años, tasa 10 % | a favor: se paga solo |

**Parte B, cambio C-002** (requisito regulatorio, paso 10): camino **excepción a la junta**. La autoridad de cambio lo
aprobó de palabra el 17/2, pero 15.000 supera su límite de 10.000 y el presupuesto quedaría en 24.000 de 12.000 (200 %):
`registro.py` rechaza registrar esa aprobación y C-002 queda `pendiente-decision`. Además, el R1 necesita 7 sprints en
lugar de 6 (+14 días corridos, más que la tolerancia de etapa de 9,8 días) y el corte de EVM del 19/2 deja fuera el
22,1 % del alcance, más que el 20 % de margen (sanidad: TOL-01). No suma beneficio propio: el VAN baja de 45.939 a
30.939, pero sigue positivo y B-01 puede caer 18 % antes de llegar a 0 (tolerancia −10 %). La junta pide un plan de
excepción con el business case actualizado, amplía el presupuesto a 32.000, aprueba C-002 con cargo a ese presupuesto y
aprueba `autorizar-plan-excepcion` el 26/2; ese día, REG-09 recuerda revisar R-001.
