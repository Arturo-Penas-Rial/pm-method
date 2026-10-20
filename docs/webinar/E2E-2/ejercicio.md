# Ejercicio · E2E-2 · La línea base de cambio y la tabla de impacto de tu proyecto

## Cómo funciona este ejercicio

- **Para qué sirve:** llevar el caso a un proyecto tuyo. Vas a escribir contra qué se mide cada cambio (tolerancias,
  límite y presupuesto de cambio, margen de alcance) y a analizar un cambio real como si todavía no se hubiera decidido.
- **Cuándo se hace:** la parte A, al cierre de la clase 1, después de la demostración (10 minutos); la parte B, al
  cierre de la clase 2, después de la demostración (10 minutos). Si lo hacés por tu cuenta, calculá 20 minutos.
- **Qué hacés:** completás la hoja de trabajo con un proyecto propio, real o reciente, que haya tenido al menos un
  cambio de alcance en los últimos meses. Alcanza con papel o una planilla, y con el orden de magnitud de los números.
  Si no tenés un proyecto, usá el escenario del caso: los datos de partida están en
  [Lo que necesitás saber](#lo-que-necesitás-saber).
- **Cómo te autoevaluás:** al final de cada parte hay una tabla de criterios. Marcá cuáles cumple tu hoja; un criterio
  sin cumplir es un hallazgo sobre tu proyecto, no un error del ejercicio.
- **Ejemplo resuelto:** al final está la hoja resuelta con el escenario del caso, y cada dato dice de qué paso de la
  guía sale. Miralo **después** de intentarlo, para comparar, no antes.

---

## Lo que necesitás saber

### El escenario del caso

Una cooperativa construye un portal de autoservicio para sus socios: 10 historias en tres épicas, WBS de USD 124.000,
sprints de 14 días y una velocidad de referencia de 8 puntos. Laura Méndez es la ejecutiva; Sofía Ramírez, usuaria
sénior, product owner y autoridad de cambio; Martín Suárez, el gestor. La clase 1 fija la línea base contra la que se
mide todo cambio; en la clase 2 llega un cambio de alcance (el simulador de préstamo) y después uno "obligatorio" que
supera la autoridad delegada.

**Datos de partida para la parte A** (si usás el caso):

- La junta fija una tolerancia de tiempo de ±3 semanas (15 días laborables) y de costo de ±8 %. Sofía Ramírez decide
  cambios de hasta 10.000 cada uno, con un presupuesto de cambio de 12.000. Lo aprueba Laura Méndez, ejecutiva.
- Backlog en puntos: Must 1.1 (8), 1.2 (5), 1.3 (8), 2.1 (8), 3.1 (5), 3.2 (8) y 3.3 (8); Should 1.4 (5) y 2.2 (8);
  Could 2.3 (5).
- La matriz requisito → historia → paquete de la WBS la regenera pm-method en cada sincronización con BMAD.

**Datos de partida para la parte B** (cambio C-001, el simulador de préstamo):

- El PM de producto agregó FR-13 al PRD por pedido del Consejo, sin pasar por la autoridad de cambio. Cuesta 9.000, se
  estima en 8, 10 y 16 días (optimista, más probable y pesimista) después de los sprints de solicitudes, suma una
  historia de 8 puntos al Release 2 y agrega 4.000 por año al beneficio B-03.
- Antes del cambio: camino crítico de 110 días laborables (fin 2027-05-03) y reserva de cronograma de 13,0 días; el
  Release 2 tiene 21 puntos en 3 sprints; no se usó nada del presupuesto de cambio; VAN del business case 39.776.
- Con el cambio, el escenario de cronograma da 121 días (fin 2027-05-18) y el business case, un VAN de 45.939.

### Conceptos mínimos

- **Línea base:** la versión aprobada del alcance, el plan y el costo contra la que se mide todo cambio.
- **Tolerancia:** el desvío que cada nivel puede absorber sin escalar (por ejemplo, ±3 semanas en el proyecto).
- **Autoridad de cambio:** quien decide cambios dentro de un **límite por cambio** y de un **presupuesto de cambio**
  (el monto total para cambios) que fija la junta.
- **MoSCoW:** Must (sin eso no hay producto), Should, Could y Won't. Con costo y fecha fijos, Should y Could son el
  **margen de alcance** que el product owner puede mover sin pedir permiso.
- **Trazabilidad:** la relación requisito → historia o tarea → paquete de trabajo; sirve si se recalcula con cada
  cambio.
- **Camino crítico:** la cadena de actividades sin holgura; si una se atrasa, se atrasa el fin. La **reserva de
  cronograma** (en el caso, 2σ del camino crítico) cubre su incertidumbre.
- **Capacidad:** velocidad × sprints (en el caso, 8 puntos por sprint).
- **VAN (valor actual neto):** la suma de los flujos de cada año descontados a la tasa de la organización; si es
  positivo, el proyecto crea valor.
- **Tres caminos para un cambio:** el **intercambio** del product owner (no toca Must, fecha ni costo), la **autoridad
  de cambio** (dentro de su límite y del saldo del presupuesto) y la **excepción** a la junta (supera el límite, el
  presupuesto o una tolerancia).

---

## Hoja de trabajo · parte A · La línea base de cambio (clase 1)

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

## Hoja de trabajo · parte B · La tabla de impacto de un cambio real (clase 2)

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

## Para ir más allá

- ¿Qué cambio de tu proyecto llegó como "obligatorio" y se aprobó sin tabla de impacto? ¿Quién debió decidirlo?
- Si tu margen de Should/Could es menor que lo que ya no entra según el avance, ¿qué Must peligran y quién lo sabe hoy?

---

## Ejemplo resuelto (escenario del caso)

Cifras de la corrida de referencia ([salida-g2.md](../../guias/evidencia/salida-g2.md)); entre paréntesis, el paso de
la [guía E2E-2](../../guias/E2E-2-alcance-roadmap.md) de donde sale cada dato.

**A1.**

| Elemento | Valor | ¿Escrito y aprobado? | ¿Quién? |
|---|---|---|---|
| Tolerancia de tiempo del proyecto | ±3 semanas = 15 días laborables (pasos 3 y 5) | sí (`estado.py tolerancia`) | Laura Méndez, ejecutiva |
| Tolerancia de costo del proyecto | ±8 % (paso 5; el comando está en la evidencia) | sí | Laura Méndez |
| Límite por cambio | 10.000 (paso 5) | sí (`estado.py presupuesto … limite_autoridad_cambio=10000`) | Laura Méndez, para Sofía Ramírez |
| Presupuesto de cambio | 12.000 (paso 5) | sí (`estado.py presupuesto cambio=12000`) | Laura Méndez |

**A2.** Con los puntos del backlog (paso 4):

| Total | Must | Should + Could | Margen |
|---|---|---|---|
| 68 puntos | 50 | 18 (Should 13, Could 5) | 26,5 % |

El caso declara al valor ganado un margen de 20 % de Should/Could (paso 9, `--pct-no-must 20`), menor que el 26,5 %
que dan los puntos. Retirar Should/Could lo decide la product owner, Sofía Ramírez (pasos 4 y 6).

**A3.** En cada sincronización con BMAD: 12 de 12 requisitos funcionales con historia y paquete en el paso 2, y 13 de
13 después del cambio, en el paso 8.

**B1.** C-001, simulador de préstamo · aprobado por Sofía Ramírez, autoridad de cambio, con cargo al presupuesto de
cambio · 2027-01-18 (paso 7; la fecha de la decisión está en la evidencia).

**B2.** Tabla de impacto de C-001, armada antes de la decisión (paso 7; las cifras de "Antes" salen de los pasos 3, 4 y
5).

| Objetivo | Antes | Con C-001 | Contra qué se mide | Lectura |
|---|---|---|---|---|
| Tiempo | 110 días · fin 2027-05-03 | 121 días · fin 2027-05-18 | ±3 semanas = 15 días | dentro (11 de 15) |
| Reserva | 2σ = 13,0 días | 2,0 días | atraso posible | riesgo: R-001 |
| Costo y presupuesto | 0 de 12.000 | 9.000 de 12.000 (75 %) | saldo del presupuesto | dentro |
| Autoridad | — | 9.000 | límite 10.000 | dentro |
| Capacidad R2 | 21 pts de 24 | 29 pts de 24 | velocidad 8 × 3 sprints | +1 sprint (32 pts) |
| Business case | VAN 39.776 | VAN 45.939 (+6.163) | VAN a 5 años, tasa 10 % | a favor: se paga solo |

**B3.** Camino: **autoridad de cambio**. 9.000 está dentro del límite de 10.000 y del saldo de 12.000; el tiempo queda
dentro de la tolerancia. Como la reserva de cronograma queda en 2 días, se registra R-001 (P3 × I3, reducir,
disparador SPI < 0,90) (paso 7).

**Otro cambio del caso para comparar: C-002** (requisito regulatorio, paso 10). Camino: **excepción a la junta**. La
autoridad de cambio lo aprobó de palabra el 17/2, pero 15.000 supera su límite de 10.000 y el presupuesto quedaría en
24.000 de 12.000 (200 %): `registro.py` rechaza registrar esa aprobación y C-002 queda `pendiente-decision`. Además, el
R1 necesita 7 sprints en lugar de 6 (+14 días corridos, más que la tolerancia de etapa de 9,8 días) y el corte de EVM
del 19/2 deja fuera el 22,1 % del alcance, más que el 20 % de margen (sanidad: TOL-01). No suma beneficio propio: el
VAN baja de 45.939 a 30.939, pero sigue positivo y B-01 puede caer 18 % antes de llegar a 0 (tolerancia −10 %). La
junta pide un plan de excepción con el business case actualizado, amplía el presupuesto a 32.000, aprueba C-002 con
cargo a ese presupuesto y aprueba `autorizar-plan-excepcion` el 26/2; ese día, REG-09 recuerda revisar R-001.
