# Ejercicio · E2E-4 · Del "done" al beneficio medido

## Cómo funciona este ejercicio

- **Para qué sirve:** llevar el caso a un proyecto tuyo. Vas a seguir una aprobación "con condiciones" hasta su
  evidencia, ubicar un cambio en el presupuesto de cambio, comprobar la calidad de una entrega, darle tratamiento a un
  dolor del recorrido de tu cliente, llevar una lección de tu última retrospectiva hasta un cambio que se pueda verificar
  y planificar quién mide los beneficios después del cierre.
- **Cuándo se hace:** la parte A, al cierre de la clase 1, después de la demostración (10 minutos; si el tiempo aprieta,
  A1 y A3 en clase y A2 después); la parte B, al
  cierre de la clase 2, después de la demostración (10 a 15 minutos; si el tiempo aprieta, B1 y B2 en clase y B3
  después). Si lo hacés por tu cuenta, calculá 25 minutos.
- **Qué hacés:** completás la hoja de trabajo con un proyecto propio o uno que conozcas bien. No hace falta tener
  pm-method instalado: lo que se practica es el criterio. Si no tenés un proyecto, usá el escenario del caso: los datos
  de partida están en [Lo que necesitás saber](#lo-que-necesitás-saber).
- **Cómo te autoevaluás:** al final de cada parte hay una lista de criterios. Marcá cuáles cumple tu hoja; un criterio
  sin cumplir es un hallazgo sobre tu proyecto, no un error del ejercicio.
- **Ejemplo resuelto:** al final está la hoja resuelta con el escenario del caso, y cada dato dice de qué paso de la
  guía sale. Miralo **después** de intentarlo, para comparar, no antes.

---

## Lo que necesitás saber

### El escenario del caso

Una cooperativa construye con BMAD un portal de autoservicio para sus socios (consulta de saldos, constancias,
solicitudes de préstamo y una consola para las operadoras), gobernado con PRINCE2. Laura Méndez es la ejecutiva; Sofía
Ramírez, usuaria sénior, product owner y autoridad de cambio; Martín Suárez, el gestor; Lucía Benítez, jefa de equipo;
Andrea Costa, aseguramiento. Hay dos releases: el 1 termina el 5/3 y el 2 el 12/5; el proyecto cierra el 14/5 y el
negocio mide los beneficios el 30/6 y el 31/12/2027.

**Datos de partida para la parte A** (si usás el caso):

- El 26/11, el gate de preparación de BMAD da CONCERNS: NFR-3 (consultas en menos de 3 segundos, p95) no tiene prueba
  de carga planificada. Laura autoriza la etapa 2 con esa condición, y la prueba de carga se planifica como revisión de
  calidad Q-001 para el 19/2. La prueba se hace el 2/3 (p95 2,4 s con 400 sesiones concurrentes) y el gate da PASS el
  3/3.
- La junta fija un presupuesto de cambio de USD 15.000 y un límite de USD 8.000 por cambio para la autoridad de cambio.
  El único cambio del caso, C-001 (FR-13, pago de cuotas con débito en cuenta), cuesta USD 6.000 y se carga al
  presupuesto de cambio.

- Entregas: sprint 1 al 23/12 con las historias 1.1 y 1.2; Release 1 al 26/2 con siete historias terminadas (1.1 a 1.4
  y 3.1 a 3.3), de las que solo 1.1 y 1.2 tienen revisión; Release 2 al 7/5 con once terminadas: la 2.1 se revisó el
  19/3, el día que pasó a done; en las revisiones del 6/5, 2.2 y 2.3 se aprueban y 2.4 se rechaza porque falta la
  notificación al socio después del débito.

**Datos de partida para la parte B:**

- Recorrido UJ-1 del PRD: "Marta consulta su saldo y baja una constancia desde el celular". En la revisión del Release
  1 con seis socios (25/2), dos pidieron ayuda en el primer ingreso con segundo factor, el resumen de cuentas tarda en
  aparecer y no tiene indicador de carga, y la constancia se descargó en el primer intento. A una etapa del cierre no se
  quiere sumar alcance.
- Retrospectiva del sprint 4 (26/2), facilitada por aseguramiento: "la revisión con seis socios funcionó muy bien;
  aprendimos que mirar el recorrido con socios reales antes de cerrar un release encuentra dolores que las pruebas no
  ven"; "otra vez llegaron historias a done sin la revisión registrada, cinco desde el sprint 2"; "la Sprint Change
  Proposal de FR-13 llegó al PRD sin pasar por la autoridad de cambio y la sanidad marcó el cambio no controlado";
  "probemos que ninguna historia pase a done sin su revisión registrada" (Lucía, para el 3/3); "toda Sprint Change
  Proposal entra primero como issue" (Martín arma la plantilla para el 3/3). El Release 2 cierra el 12/5.
- Beneficios y sus KR: B-01 desvío de consultas (KR-1.2, de 5.000 a 3.500 consultas por mes), B-02 adopción (KR-1.1, 30
  % de socios registrados) y B-03 préstamos en menos de 48 horas (KR-1.3, de 96 a 48 horas). Sofía Ramírez, de
  servicios al socio, mide el 30/6 y el 31/12/2027. El producto entra en operación el 15/5.

### Conceptos mínimos

- **Condición formal de una puerta:** lo que la junta exige para que su aprobación valga; tiene quien la verifica,
  evidencia y fecha, y bloquea la puerta siguiente hasta que alguien con rol la da por cumplida.
- **Expediente de auditoría:** la evidencia del proyecto armada desde los registros (cronología de puertas, decisiones
  y cambios, copias congeladas) con una huella por archivo; si alguien edita una copia, la verificación lo detecta.
- **Gate de preparación de BMAD:** el control de BMAD antes de construir; responde PASS, CONCERNS o FAIL.
- **Revisión de calidad:** la comprobación registrada de un producto o una historia contra sus criterios de aceptación;
  "terminado" sin revisión aprobada no cuenta como completado.
- **Presupuesto de cambio y límite por cambio:** el monto total para cambios que fija la junta y el máximo que la
  autoridad de cambio puede aprobar en un solo cambio; por encima decide la junta.
- **Rechazo tratado:** una revisión rechazada queda citada por un issue, una acción o un cambio hasta que una nueva
  revisión la aprueba.
- **Mapa de recorrido del cliente:** las acciones de la persona en fila, con su emoción en cada paso (de −2 a +2) y la
  fuente que la respalda; todo **dolor** necesita un **tratamiento con id** (requisito, historia, riesgo, issue,
  cambio, decisión, supuesto o revisión de calidad) y un dueño.
- **Retrospectiva:** reunión propia, distinta de la planificación del sprint siguiente y del seguimiento: mira el proceso
  con hechos, sin culpables (qué funcionó, qué no, qué probamos). Produce lecciones y acciones de mejora, no tareas del
  plan ni decisiones de la junta.
- **Lección aprendida:** una recomendación transferible con **impacto** (alto si afecta o puede afectar una tolerancia,
  un beneficio o un riesgo alto, o bloqueó una puerta; medio si consumió margen o retrabajo sin salir de tolerancia;
  bajo si fue local), **ámbito** donde se usa (ideación, descubrimiento, planificación, seguimiento), una **acción** y
  una **fecha para verificar** que la acción funcionó. Sin acción verificada, la lección solo está identificada.
- **Plan de revisión de beneficios:** quién mide cada beneficio después del cierre, contra qué línea base (medida al
  entrar en operación), con qué meta y qué criterio de desvío, y a quién informa.
- **Trayectoria y tolerancia:** en una revisión intermedia se compara el avance con el esperado a esa fecha (salud); en
  la final, con la tolerancia (en el caso, avance menor que 0,90 = fuera de la tolerancia de −10 %).

---

## Hoja de trabajo · parte A · Condiciones, presupuesto de cambio y calidad por entrega (clase 1)

**A1. Una aprobación "con condiciones" de tu proyecto.** Escribí la última que recuerdes (o una plausible).

| Condición | Quién la verifica (rol y nombre) | Evidencia que prueba que se cumplió | Fecha límite | Qué bloquea si no se cumple |
|---|---|---|---|---|
| | | | | |

**A2. Presupuesto de cambio.** Completá con montos de tu proyecto.

| Concepto | Valor |
|---|---|
| Presupuesto de cambio que fija la junta | |
| Límite por cambio de la autoridad de cambio delegada | |
| Último cambio aprobado: costo y a qué se cargó | |
| ¿Quién debió decidirlo según el límite? | |

**A3. Calidad por entrega.** Elegí tu última entrega (sprint, release o hito).

| Entrega | Productos o historias terminadas | Con revisión aprobada registrada | Rechazadas | ¿Cada rechazo tiene un issue o acción que lo cite? |
|---|---|---|---|---|
| | | | | |

### Autoevaluación de la parte A

- [ ] La condición tiene un verificador con rol, no "el equipo".
- [ ] La evidencia es un registro concreto (una revisión, una prueba, un documento), no "que esté bien".
- [ ] La condición bloquea algo concreto (la puerta siguiente o el cierre).
- [ ] La condición y su cumplimiento quedan en un registro fechado, con quién lo verificó, que una auditoría puede
      revisar y comprobar que no se editó.
- [ ] El cambio tiene monto y cargo; sabés cuánto queda del presupuesto.
- [ ] Terminadas = con revisión aprobada antes de pasar la puerta (si no, ¿cuántas faltan?).
- [ ] Distinguís aprobadas (revisión de calidad) de aceptadas (acto de la autoridad de aceptación).
- [ ] Ningún rechazo queda sin un issue, acción o cambio que lo cite.

---

## Hoja de trabajo · parte B · Recorrido, lecciones y revisión de beneficios (clase 2)

**B1. Un dolor del recorrido de tu cliente.** Pensá en la última entrega desde la persona que la usa: un paso donde se
traba, cómo lo sabés y qué lo trata.

| Paso del recorrido (una acción) | Emoción (−2 a +2) | Fuente (observación, métrica, entrevista o supuesto declarado) | Dolor | Tratamiento con id (requisito, historia, riesgo, issue, cambio, decisión, supuesto o revisión de calidad) | Dueño |
|---|---|---|---|---|---|
| | | | | | |

**B2. Una lección de tu última retrospectiva.** Elegí una que se haya dicho más de una vez.

| Qué se dijo (cita) | Impacto (alto, medio, bajo) y por qué | Recurrencia | Ámbito donde se usa | Acción (id o artefacto) y dueño | Fecha para verificar | Evidencia de que funcionó |
|---|---|---|---|---|---|---|
| | | | | | | |

**B3. Plan de revisión de beneficios.** Elegí dos beneficios de tu business case.

| Beneficio | Medida | Línea base (fecha) | Meta (fecha) | Quién mide después del cierre | Criterio de desvío | A quién se informa |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

### Autoevaluación de la parte B

- [ ] El paso del recorrido es una sola acción y la emoción tiene una fuente, no una opinión.
- [ ] El dolor tiene un tratamiento con id y dueño; si no cambia el alcance, ¿amenaza algún beneficio (riesgo)?
- [ ] El dolor y su tratamiento se ven en el tablero que mira la junta, no solo en el taller (en pm-method, la sección
      «Mapas estratégicos» del tablero de avance, con `mapas.py tablero --insertar`).
- [ ] La lección sale de una cita de la retrospectiva, no de la memoria al cierre; la retro no se mezcló con la
      planificación.
- [ ] El impacto se justifica por su efecto en tiempo, costo, alcance, calidad, beneficios o riesgo.
- [ ] La acción vive en un lugar que se revisa (backlog, acciones, plan de la etapa), con dueño y fecha de verificación;
      si es de impacto alto y aplica a planificación, el plan siguiente la cita.
- [ ] La evidencia de efectividad es observable (un registro, una sanidad, una métrica), no "mejoró".
- [ ] La línea base de cada beneficio se mide **al entrar en operación**, no al aprobar el proyecto.
- [ ] Quien mide es del negocio, no del equipo del proyecto.
- [ ] El criterio distingue la revisión intermedia (trayectoria) de la final (tolerancia).

---

## Para ir más allá

- ¿Qué condición de una puerta de tu proyecto se aprobó y nadie volvió a mirar? ¿Qué la habría hecho reaparecer?
- ¿Dónde busca tu organización las lecciones de proyectos anteriores al arrancar uno nuevo? ¿Alguien las consulta?
- Si un objetivo sale en verde pero uno de sus beneficios queda fuera de tolerancia, ¿quién lo nota en tu organización?

---

## Ejemplo resuelto (escenario del caso)

Cifras de la corrida de referencia ([salida-g4.md](../../guias/evidencia/salida-g4.md)); entre paréntesis, el paso de
la [guía E2E-4](../../guias/E2E-4-producto-bmad.md) de donde sale cada dato.

**A1.**

| Condición | Quién la verifica | Evidencia | Fecha límite | Qué bloquea |
|---|---|---|---|---|
| Gate de preparación de BMAD en CONCERNS: NFR-3 sin prueba de carga planificada (26/11) (paso 2) | Laura Méndez, ejecutiva, que la da por cumplida con `cumplir-condiciones` el 5/3 (paso 7) | Q-001, prueba de carga aprobada el 2/3 (p95 2,4 s con 400 sesiones; meta menor a 3 s), y gate en PASS el 3/3 (paso 7) | 19/2, la `fecha_prevista` de Q-001; QUA-02 avisa al vencer (pasos 2 y 6) | la puerta siguiente, como condición G-01 (paso 7), y `autorizar-cierre`, que bloquea con G-01 (paso 9) |

La traza queda en el expediente para la auditoría externa: la puerta condicionada (D-013, 27/11) y la condición
cumplida (D-019, 5/3) en la cronología, con "INTEGRIDAD: OK" en la verificación. En la copia donde alguien cambió
«condicionado» por «aprobado» en D-013, la verificación falla en `decisiones.csv` (paso 9b).

**A2.**

| Concepto | Valor |
|---|---|
| Presupuesto de cambio que fija la junta | USD 15.000 (paso 1, sub-paso 1g) |
| Límite por cambio de la autoridad de cambio | USD 8.000 (paso 1, sub-paso 1g) |
| Último cambio aprobado | C-001 (FR-13, pago de cuotas): USD 6.000, `cargo=presupuesto-cambio` (paso 5) |
| ¿Quién debió decidirlo? | Sofía Ramírez, autoridad de cambio, porque está bajo su límite; consumo 6.000 de 15.000 (40 %, CAM-03) (paso 5) |

**A3.**

| Entrega | Terminadas | Con revisión aprobada | Rechazadas | ¿Rechazo tratado? |
|---|---|---|---|---|
| Sprint 1 (23/12) (paso 3) | 2 | 2 (Q-002 y Q-003) | 0 | — |
| Release 1 (26/2) (paso 6) | 7 | 2; 7 después del lote del 25/2 (Q-004 a Q-008) | 0 | — |
| Release 2 (7/5) (paso 8) | 11 | 10 (la 2.1 con Q-009 el 19/3); 11 al 12/5 (Q-013) | 1 (Q-012, historia 2-4) | sí: I-002 lo cita y Q-013 lo aprueba el 11/5 |

El conteo no se arma a mano: el estado de productos (`estado.py productos --corte 2027-02-26 --alcance R1`, paso 6) da
"en revisión 5 · aprobado 2 · aceptado 0" antes del lote, con una diferencia QUA-01 por historia. Aprobado no es
aceptado: los 11 productos quedan aceptados recién con el registro de aceptación del 12/5, y la puerta de cierre no
muestra ningún Must sin aceptar (C-07) (paso 9).

**B1.** Recorrido UJ-1 con lo observado en la revisión del Release 1 con seis socios el 25/2 (paso 6b). En el tablero
del Release 1, la sección «Mapas estratégicos» muestra los dos dolores con su tratamiento y 0 avisos MAP (paso 7).

| Paso | Emoción | Fuente | Dolor | Tratamiento | Dueño |
|---|---|---|---|---|---|
| P1 Ingresa con sus credenciales | −1 | observación: dos de seis socios pidieron ayuda en el primer ingreso | el primer ingreso con segundo factor la frena y pide ayuda | R-001, riesgo para B-02 adopción; respuesta del negocio: alta asistida en sucursal y por teléfono los primeros 60 días de operación | Sofía Ramírez |
| P2 Ve el resumen de cuentas de ahorro y préstamos | −1 | observación: el resumen tarda en aparecer y no hay indicador de carga | espera el resumen sin saber si cargó | NFR-3 (p95 menor a 3 s), verificado por Q-001 | Lucía Benítez produce, Sofía Ramírez aprueba (enfoque de calidad, paso 1, sub-paso 1g) |

P1 va como riesgo y no como requisito porque, a una etapa del cierre, el dolor no justifica alcance nuevo pero sí
amenaza un beneficio (paso 6b).

**B2.** Retrospectiva del sprint 4, 26/2 (paso 6c); la cita sale de la transcripción con su hora.

| Qué se dijo | Impacto | Recurrencia | Ámbito | Acción y dueño | Verificar | Evidencia |
|---|---|---|---|---|---|---|
| «Tampoco funcionó cómo entró FR-13: la Sprint Change Proposal llegó al PRD sin pasar por la autoridad de cambio…» (Martín Suárez, [00:02:10]) → L-003 (paso 6c) | alto: ESP-10 bloqueaba la puerta hasta tramitar C-001 (pasos 5 y 6c) | media | planificación y seguimiento | A-002, plantilla del issue (Martín Suárez), citada en «Lecciones incorporadas» del plan de la etapa 3; E-11 avisó hasta incorporarla (paso 7) | 12/5, al cerrar el Release 2 (paso 7) | el rechazo de la 2-4 entró como I-002 sin tocar la especificación; sanidades del 7/5 y del 12/5 sin ESP-10 → verificada efectiva (paso 8) |
| «No funcionó lo de siempre: otra vez llegaron historias a done sin la revisión registrada…» (Lucía Benítez, [00:01:30]) → L-002 (paso 6c) | medio: obligó a registrar cinco revisiones en lote, sin salir de tolerancia (paso 6) | alta | seguimiento | A-001, definición de terminado (Lucía Benítez) (paso 6c) | 19/3, fin del sprint 5; REG-12 avisó el 22/3 (paso 8) | la 2.1 pasó a done con Q-009 el mismo día; sanidad del 22/3 sin QUA-01 → verificada efectiva (paso 8) |

La tercera lección (L-001, la revisión con socios, impacto medio, descubrimiento) va a la PMO y, con las otras dos, al
índice de la organización que exporta el informe de lecciones del cierre (paso 9).

**B3.** Plan de revisión de beneficios del cierre (paso 9), con la línea base al entrar en operación (paso 10).

| Beneficio | Medida | Línea base | Meta | Quién mide | Criterio de desvío | A quién |
|---|---|---|---|---|---|---|
| B-02 adopción | KR-1.1 % de socios registrados | 0 % (15/5/2027) | 30 % (31/12/2027) | Sofía Ramírez, servicios al socio | 30/6: escala si la salud es en-riesgo o desviado; 31/12: avance menor que 0,90 | Laura Méndez, ejecutiva |
| B-01 desvío de consultas | KR-1.2 consultas por mes | 5.000 (15/5/2027) | 3.500 (31/12/2027) | Sofía Ramírez | ídem | Laura Méndez |

Lo que pasó: al 30/6, los tres KR van «en camino» (esperado 0,20) y no hay informe a la ejecutiva (paso 10). Al
31/12, el objetivo sale en verde (0,91), pero B-02 llega a 0,83, fuera de la tolerancia, y B-01 a 0,93, dentro. Se
informa a la ejecutiva con D-029, que empieza a buscar la causa por R-001: el dolor del primer ingreso que dejó el
recorrido (paso 11).
