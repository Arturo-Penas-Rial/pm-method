# Ejercicio · E2E-4 · Del "done" al beneficio medido

Hoja de trabajo para aplicar el caso a un proyecto propio (o a uno que conozcas bien). La parte A va al final de la
clase 1 (10 minutos) y la parte B al final de la clase 2 (10 a 15 minutos; si el tiempo aprieta, B1 y B2 en clase y B3
después). No hace falta tener pm-method instalado: lo que se practica es el criterio. Al final está la solución de referencia con el escenario del caso
([guía E2E-4](../../guias/E2E-4-producto-bmad.md)).

## Parte A · Condiciones y presupuesto de cambio (clase 1, 10 min)

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

**Autoevaluación A** (marcá lo que se cumple):
- [ ] La condición tiene un verificador con rol, no "el equipo".
- [ ] La evidencia es un registro concreto (una revisión, una prueba, un documento), no "que esté bien".
- [ ] La condición bloquea algo concreto (la puerta siguiente o el cierre).
- [ ] El cambio tiene monto y cargo; sabés cuánto queda del presupuesto.

## Parte B · Calidad por entrega, recorrido y revisión de beneficios (clase 2, 10–15 min)

**B1. Calidad por entrega.** Elegí tu última entrega (sprint, release o hito).

| Entrega | Productos o historias terminadas | Con revisión aprobada registrada | Rechazadas | ¿Cada rechazo tiene un issue o acción que lo cite? |
|---|---|---|---|---|
| | | | | |

**B2. Un dolor del recorrido de tu cliente.** Pensá en la última entrega desde la persona que la usa: un paso donde se
traba, cómo lo sabés y qué lo trata.

| Paso del recorrido (una acción) | Emoción (−2 a +2) | Fuente (observación, métrica, entrevista o supuesto declarado) | Dolor | Tratamiento con id (requisito, historia, riesgo, issue, cambio, decisión, supuesto o revisión de calidad) | Dueño |
|---|---|---|---|---|---|
| | | | | | |

**B3. Plan de revisión de beneficios.** Elegí dos beneficios de tu business case.

| Beneficio | Medida | Línea base (fecha) | Meta (fecha) | Quién mide después del cierre | Criterio de desvío | A quién se informa |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

**Autoevaluación B**:
- [ ] Terminadas = con revisión aprobada antes de pasar la puerta (si no, ¿cuántas faltan?).
- [ ] Ningún rechazo queda sin un issue, acción o cambio que lo cite.
- [ ] El paso del recorrido es una sola acción y la emoción tiene una fuente, no una opinión.
- [ ] El dolor tiene un tratamiento con id y dueño; si no cambia el alcance, ¿amenaza algún beneficio (riesgo)?
- [ ] El dolor y su tratamiento se ven en el tablero que mira la junta, no solo en el taller (en pm-method, la sección
      «Mapas estratégicos» del tablero de avance, con `mapas.py tablero --insertar`).
- [ ] La línea base de cada beneficio se mide **al entrar en operación**, no al aprobar el proyecto.
- [ ] Quien mide es del negocio, no del equipo del proyecto.
- [ ] El criterio distingue la revisión intermedia (trayectoria) de la final (tolerancia).

## Solución de referencia (escenario del caso)

**A1.**

| Condición | Quién la verifica | Evidencia | Fecha límite | Qué bloquea |
|---|---|---|---|---|
| Gate de preparación de BMAD en CONCERNS: NFR-3 sin prueba de carga planificada (26/11) | Laura Méndez, ejecutiva (`cumplir-condiciones` el 5/3) | Q-001 prueba de carga aprobada el 2/3 (p95 2,4 s con 400 sesiones; meta menor a 3 s) y gate en PASS el 3/3 | 19/2 (`fecha_prevista` de Q-001; QUA-02 avisó al vencer) | condición en la puerta siguiente (G-01) y bloqueo de `autorizar-cierre` |

**A2.**

| Concepto | Valor |
|---|---|
| Presupuesto de cambio que fija la junta | USD 15.000 |
| Límite por cambio de la autoridad de cambio | USD 8.000 |
| Último cambio aprobado | C-001 (FR-13 pago de cuotas): USD 6.000, `cargo=presupuesto-cambio` |
| ¿Quién debió decidirlo? | Sofía Ramírez, autoridad de cambio (está bajo su límite); consumo 6.000 de 15.000 (40 %, CAM-03) |

**B1.**

| Entrega | Terminadas | Con revisión aprobada | Rechazadas | ¿Rechazo tratado? |
|---|---|---|---|---|
| Sprint 1 (23/12) | 2 | 2 (Q-002, Q-003) | 0 | — |
| Release 1 (26/2, antes del lote) | 7 | 2 → 7 después del lote (Q-004 a Q-008) | 0 | — |
| Release 2 (7/5) | 11 | 10 → 11 el 12/5 (Q-013) | 1 (Q-012, historia 2-4) | sí: I-002 lo cita; Q-013 aprobada el 11/5 |

**B2.** (recorrido UJ-1, revisión del Release 1 con seis socios el 25/2; mapa en `g4-recorrido.png` y, en el tablero
del Release 1, en `g4-tablero-mapas-169.png`: los dos dolores con su tratamiento y 0 avisos MAP)

| Paso | Emoción | Fuente | Dolor | Tratamiento | Dueño |
|---|---|---|---|---|---|
| P1 Ingresa con sus credenciales | −1 | observación: dos de seis socios pidieron ayuda en el primer ingreso | el primer ingreso con segundo factor la frena | R-001, riesgo para B-02 adopción (respuesta: alta asistida en sucursal y por teléfono los primeros 60 días) | Sofía Ramírez |
| P2 Ve el resumen de cuentas | −1 | observación: el resumen tarda y no hay indicador de carga | espera sin saber si cargó | NFR-3 (p95 menor a 3 s), verificado por Q-001 | Lucía Benítez (produce), Sofía Ramírez (aprueba) |

**B3.**

| Beneficio | Medida | Línea base | Meta | Quién mide | Criterio de desvío | A quién |
|---|---|---|---|---|---|---|
| B-02 adopción | KR-1.1 % de socios registrados (SM-1) | 0 % (15/5/2027) | 30 % (31/12/2027) | Sofía Ramírez, servicios al socio | 30/6: salud en-riesgo o desviado; 31/12: avance menor que 0,90 | Laura Méndez, ejecutiva |
| B-01 desvío de consultas | KR-1.2 consultas por mes (SM-2) | 5.000 (15/5/2027) | 3.500 (31/12/2027) | Sofía Ramírez | ídem | Laura Méndez |

Resultado en el caso: al 30/6, los tres KR "en camino" (esperado 0,20); al 31/12, B-02 llega a 0,83 (fuera de la
tolerancia de −10 %) y B-01 a 0,93 (dentro). Se informa a la ejecutiva (D-029), que empieza por R-001: el dolor del
primer ingreso que dejó el recorrido.
