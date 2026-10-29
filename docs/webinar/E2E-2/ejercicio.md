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
- Las personas de usuario salen de los tres recorridos de BMAD: Marta (socia que consulta, épica 1), Diego (socio que
  pide un préstamo, épica 2) y Lucía (operadora de back-office, épica 3).

**Datos de partida para la parte B** (cambio C-001, el simulador de préstamo):

- El PM de producto agregó FR-13 al PRD por pedido del Consejo, sin pasar por la autoridad de cambio. Cuesta 9.000, se
  estima en 8, 10 y 16 días (optimista, más probable y pesimista) después de los sprints de solicitudes, suma una
  historia de 8 puntos al Release 2 y agrega 4.000 por año al beneficio B-03.
- Antes del cambio: camino crítico de 112 días laborables (fin 2027-05-05) y reserva de cronograma de 13,0 días; el
  Release 2 tiene 21 puntos en 3 sprints; no se usó nada del presupuesto de cambio; VAN del business case 39.776.
- Con el cambio, el escenario de cronograma da 123 días (fin 2027-05-20) y el business case, un VAN de 45.939.

### Conceptos mínimos

- **Línea base:** la versión aprobada del alcance, el plan y el costo contra la que se mide todo cambio.
- **Tolerancia:** el desvío que cada nivel puede absorber sin escalar (por ejemplo, ±3 semanas en el proyecto).
- **Autoridad de cambio:** quien decide cambios dentro de un **límite por cambio** y de un **presupuesto de cambio**
  (el monto total para cambios) que fija la junta.
- **MoSCoW:** Must (sin eso no hay producto), Should, Could y Won't. Con costo y fecha fijos, Should y Could son el
  **margen de alcance** que el product owner puede mover sin pedir permiso.
- **Trazabilidad:** la relación requisito → historia o tarea → paquete de trabajo; sirve si se recalcula con cada
  cambio.
- **Persona de usuario:** un arquetipo de quien usa el producto (objetivo, contexto, dolores). No es un interesado: es a
  quien sirve cada capacidad. Un Must sin persona es una pregunta: ¿falta la persona o sobra la prioridad?
- **Camino crítico:** la cadena de actividades sin holgura; si una se atrasa, se atrasa el fin. La **reserva de
  cronograma** (en el caso, 2σ del camino crítico) cubre su incertidumbre.
- **Capacidad:** velocidad × sprints (en el caso, 8 puntos por sprint).
- **VAN (valor actual neto):** la suma de los flujos de cada año descontados a la tasa de la organización; si es
  positivo, el proyecto crea valor.
- **Análisis de impacto:** el cambio medido contra cada objetivo antes de decidir; dice además qué nivel tiene que
  decidirlo.
- **Tres caminos para un cambio:** el **intercambio** del product owner (no toca Must, fecha ni costo), la **autoridad
  de cambio** (dentro de su límite y del saldo del presupuesto) y la **excepción** a la junta (supera el límite, el
  presupuesto o una tolerancia).
- **Matriz de decisión:** las alternativas comparadas con pesos explícitos (puntaje = Σ peso × valor de 0 a 1). Un
  criterio **eliminatorio** saca una opción que no lo cumple; una opción **dominada** es peor o igual que otra en todo;
  la **sensibilidad** dice cuánto habría que mover un peso para que gane otra. Incluí siempre rechazar o diferir.

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

**A4. ¿A quién sirve cada Must?** Elegí tres Must de tu alcance y escribí qué tipo de usuario los necesita.

| Must | Usuario (persona) que lo necesita | ¿De dónde sale? (entrevista, recorrido, supuesto) |
|---|---|---|
| | | |
| | | |
| | | |

### Autoevaluación de la parte A

| Criterio | Cumple si… |
|---|---|
| Línea base de cambio completa | Los cuatro elementos de A1 tienen valor, están escritos y tienen quien los aprobó. |
| Autoridad delimitada | El límite por cambio es menor que el presupuesto de cambio (si no, un solo cambio lo agota). |
| Margen conocido | Sabés el porcentaje de A2 y quién decide retirar Should/Could. |
| Trazabilidad viva | A3 es "en la última semana" o se regenera en cada sincronización. |
| Must con usuario | Cada Must de A4 tiene una persona y una fuente; uno sin persona es un hallazgo para revisar su prioridad. |

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
| Quién lo pide y a quién afecta | | | personas de usuario que lo usan o se benefician | |

**B3. ¿Qué camino le correspondía?** Marcá uno y justificá en una línea.

- [ ] Intercambio del product owner (no toca Must, fecha ni costo)
- [ ] Autoridad de cambio (dentro del límite por cambio y del saldo del presupuesto)
- [ ] Excepción a la junta (supera el límite, el presupuesto o una tolerancia)

> Justificación: ……………………………………………………………………………………………

**B4. Las alternativas.** ¿Qué otras opciones tenía quien decidió? Escribí al menos dos, una de ellas rechazar o
diferir.

| Opción | ¿Algún criterio la elimina? (por ejemplo, un requisito obligatorio) | ¿Por qué ganó, o por qué no? |
|---|---|---|
| | | |
| | | |

> ¿Qué tendría que pesar más para que ganara otra opción? ……………………………………………

### Autoevaluación de la parte B

| Criterio | Cumple si… |
|---|---|
| Impacto completo | Completaste al menos tiempo, costo, autoridad, capacidad y business case (no solo el costo). |
| Antes de decidir | Las cifras de "Con el cambio" se podían conocer antes de aprobarlo. |
| Camino correcto | El camino de B3 coincide con quien aprobó en B1; si no coincide, encontraste un caso de autoridad excedida. |
| Riesgo derivado | Si la reserva quedó chica, registraste (o registrarías) un riesgo con disparador. |
| Alternativas explícitas | B4 tiene al menos dos opciones, una de ellas rechazar o diferir, y escribiste qué haría ganar a otra. |

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

**A4.** Con las personas propuestas desde los recorridos de BMAD y confirmadas por Sofía Ramírez (paso 4):

| Must | Persona | Fuente |
|---|---|---|
| 1.3 Consulta de saldos y préstamos (FR-3, FR-4) | Marta, socia que consulta (PU-001) | recorrido UJ-1 |
| 2.1 Solicitud guiada de préstamo (FR-6) | Diego, socio que pide un préstamo (PU-002) | recorrido UJ-2 |
| 3.2 Bandeja única (FR-9) | Lucía, operadora de back-office (PU-003) | recorrido UJ-3 |

La primera priorización por persona avisó "Must sin persona: FR-8, FR-12". No sobraba la prioridad: UJ-2 dice que
Diego entra con el contacto verificado y recibe la confirmación por correo, así que se vincularon a él y quedó "Must
sin persona: ninguno" (Marta 5 Must, Diego 4, Lucía 3).

**B1.** C-001, simulador de préstamo · aprobado por Sofía Ramírez, autoridad de cambio, con cargo al presupuesto de
cambio · 2027-01-18 (paso 7; la fecha de la decisión está en la evidencia).

**B2.** Tabla de impacto de C-001, calculada con `impacto.py analizar C-001` antes de la decisión (paso 7; las cifras
de "Antes" salen de los pasos 3, 4 y 5). Resumida:

| Objetivo | Antes | Con C-001 | Contra qué se mide | Lectura |
|---|---|---|---|---|
| Tiempo | 112 días · fin 2027-05-05 | 123 días · fin 2027-05-20 (+11) | ±3 semanas = 15 días laborables | dentro: usa 11 de 15 (73 %) |
| Reserva | 2σ = 13,0 días | 13,0 − 11 = 2,0 días | atraso posible del camino crítico | registrar riesgo: R-001 |
| Costo y presupuesto | 0 de 12.000 | 9.000 de 12.000 (75 %) | saldo del presupuesto de cambio | dentro del saldo |
| Autoridad | límite 10.000 por cambio | 9.000 en este cambio | límite por cambio | dentro de la autoridad delegada |
| Capacidad R2 | 21 pts de 24 (3 sprints) | 29 pts | velocidad 8 pts por sprint | 4 sprints: +1 sprint |
| Business case | VAN 39.776 | VAN 45.939 (+6.163) | VAN a 5 años, tasa 10 % | a favor: el cambio suma valor |
| Quién lo pide y a quién afecta | — | lo pide el Consejo directivo; lo usa Diego (PU-002) | personas de usuario | sirve a una persona registrada |

**B3.** Camino: **autoridad de cambio**, el mismo que da el análisis ("Decide: Autoridad de cambio: Sofía Ramírez").
9.000 está dentro del límite de 10.000 y del saldo de 12.000; el tiempo queda dentro de la tolerancia. Como la reserva de cronograma queda en 2 días, se registra R-001 (P3 × I3, reducir,
disparador SPI < 0,90) (paso 7).

**Otro cambio del caso para comparar: C-002** (requisito regulatorio, paso 10). Camino: **excepción a la junta**. La
autoridad de cambio lo aprobó de palabra el 17/2, pero 15.000 supera su límite de 10.000 y el presupuesto quedaría en
24.000 de 12.000 (200 %): `registro.py` rechaza registrar esa aprobación y C-002 queda `pendiente-decision`. Además, el
R1 necesita 7 sprints en lugar de 6 (+14 días corridos, más que la tolerancia de etapa de 9,8 días) y el corte de EVM
del 19/2 deja fuera el 22,1 % del alcance, más que el 20 % de margen (sanidad: TOL-01). No suma beneficio propio: el
VAN baja de 45.939 a 30.939, pero sigue positivo y B-01 puede caer 18 % antes de llegar a 0 (tolerancia −10 %). El
análisis de impacto lo resume: "Decide: Junta", con cuatro motivos, y recomienda pedir un plan de excepción. La
junta pide un plan de excepción con el business case actualizado, amplía el presupuesto a 32.000, aprueba C-002 con
cargo a ese presupuesto y aprueba `autorizar-plan-excepcion` el 26/2; ese día, REG-09 recuerda revisar R-001.

**B4.** Con C-002, las alternativas que recibió la junta en la matriz `03-control/decisiones/C-002/` (paso 10):

| Opción | ¿Algún criterio la elimina? | ¿Por qué ganó, o por qué no? |
|---|---|---|
| Rechazar C-002 | sí: impacto 1, menor que el eliminatorio 2 (es obligatorio por la Ley 18.331) | eliminada |
| Diferir C-002 al R2 | no (impacto 2) | 10,0 y dominada: el mismo análisis aplicado a diferir da 2 sprints más en el R2 (28 días corridos) y excede igual la autoridad y el presupuesto |
| Pedir plan de excepción | no (impacto 4) | 30,0, recomendada; la junta la elige el 22/2 y queda en D-013 con la matriz |

Ningún peso de 0 a 100 cambia la primera: la recomendación es estable. Para comparar, la decisión del R1 (paso 5) sí
tiene un peso que la cambia: la consola gana 56,2 contra 47,5, y ganarían las solicitudes si la capacidad pesara 31 en
lugar de 25.
