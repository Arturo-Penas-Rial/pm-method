# Ejercicio · E2E-5 · Los supuestos, el experimento y las reservas de tu proyecto

**Para qué:** aplicar el caso a una idea o un proyecto propio (real o reciente) sin herramientas: papel o una planilla
alcanzan. **Duración:** parte A, 10 minutos (cierre de la clase 1); parte B, 10 minutos (cierre de la clase 2). Si hacés
el ejercicio solo, calculá 20 minutos en total. **Referencia:** [Guía E2E-5](../../guias/E2E-5-idea-a-proyecto.md),
pasos 2 a 5, 9 y 11 a 14.

Elegí una idea que alguien quiera aprobar en los próximos meses, o un proyecto que se aprobó hace poco. No hace falta que
los números sean exactos: alcanza con el orden de magnitud.

---

## Parte A · El mapa de supuestos y un experimento barato (clase 1)

**A1. La idea en una frase y la decisión que se espera.**

> Idea: ……………………………………………… · Decisión que se espera: ………………………… · ¿Para cuándo? ……………

**A2. Cinco supuestos.** Al menos uno de cada familia. Criticidad: si es falso, ¿cuánto cambia el caso? Certeza: ¿cuánta
evidencia hay hoy? (alta / media / baja).

| Id | Supuesto (si es falso, el caso cambia) | Familia (deseabilidad · viabilidad · factibilidad) | Criticidad | Certeza | Evidencia que tengo hoy |
|---|---|---|---|---|---|
| S-1 | | | | | |
| S-2 | | | | | |
| S-3 | | | | | |
| S-4 | | | | | |
| S-5 | | | | | |

**A3. Ubicalos en el mapa.** Escribí los ids en la celda que corresponde.

| Criticidad \ Certeza | baja | media | alta |
|---|---|---|---|
| **alta** | **(validar primero)** | | |
| **media** | | | |
| **baja** | | | |

**A4. Un experimento barato** para un supuesto de la celda "validar primero".

| Supuesto | Experimento (lo más barato que da evidencia) | Criterio para seguir, decidido hoy | Costo y duración | Responsable | Fecha límite |
|---|---|---|---|---|---|
| | | | | | |

**A5. Si el resultado sale mal**, ¿qué número del caso cambia y quién decide qué hacer?

> Cambia: ……………………………… · Decide: ……………………………… · Opciones: seguir / ajustar / abandonar

### Autoevaluación de la parte A

| Criterio | Cumple si… |
|---|---|
| Familias cubiertas | Hay al menos un supuesto de deseabilidad, uno de viabilidad y uno de factibilidad. |
| Prioridad clara | Hay al menos un supuesto en "validar primero" y sabés por qué está ahí. |
| Experimento bien diseñado | Es más barato que equivocarse, tiene fecha y el criterio está escrito **antes** del resultado. |
| Resultado con destino | A5 dice qué número del caso cambia y quién decide (lo que en pm-method vigila SUP-03). |

---

## Parte B · Las reservas y la adaptación (clase 2)

**B1. Las tres bolsas.** Completá con lo que existe hoy en tu proyecto. Si no existe, escribí "no definido".

| Bolsa | Monto | Para qué se usa | Quién la libera | ¿Está escrita y aprobada? |
|---|---|---|---|---|
| Contingencia (riesgos identificados) | | | | |
| Reserva de gestión (lo no identificado) | | | | |
| Presupuesto de cambio | | | | |
| Tope por cambio de quien aprueba cambios | | — | | |

**B2. ¿Qué diseño le corresponde?** Marcá el que más se parece a tu proyecto y anotá una cosa que harías distinto.

| Diseño | Se parece a mi proyecto | Qué haría distinto |
|---|---|---|
| Interno pequeño (perfil mínimo; acta y PID breve; un enfoque de una página) | [ ] | |
| Regulado (perfil completo; aseguramiento independiente; siete tolerancias) | [ ] | |
| Producto digital ágil (PID compacto; enfoques de una página; fecha fija y alcance en MoSCoW) | [ ] | |
| Híbrido (como el caso: cada entregable con su vía) | [ ] | |

**B3. Una decisión de adaptación** que dejarías escrita en el PID:

| Qué se adapta | Cómo | Por qué |
|---|---|---|
| | | |

**B4. Un supuesto crítico que seguiría sin validar** el día de la aprobación:

| Supuesto | ¿Se valida antes o la junta lo acepta? | Quién lo acepta (decisión escrita) | Cómo se cubre si sale mal | Fecha para revisarlo |
|---|---|---|---|---|
| | | | | |

**B5. Lo que el tablero de mapas mostraría a la junta.** Un componente con inercia y un dolor de la persona, cada uno
con lo que lo trata (en pm-method, `mapas.py tablero` los dibuja con su vínculo o con un aviso MAP).

| Elemento del mapa | Qué muestra | Tratamiento con id (riesgo, requisito, supuesto, decisión…) | Dueño |
|---|---|---|---|
| Componente con inercia | | | |
| Dolor del recorrido | | | |

### Autoevaluación de la parte B

| Criterio | Cumple si… |
|---|---|
| Bolsas separadas | Contingencia, reserva de gestión y presupuesto de cambio tienen monto y dueño distintos; nada se cuenta dos veces. |
| Autoridad delimitada | El tope por cambio es menor que el presupuesto de cambio. |
| Adaptación escrita | B3 dice qué se aligera y por qué, sin saltear ninguna decisión de la junta. |
| Hipótesis a la vista | B4 tiene una decisión escrita de quien puede aceptar el supuesto, una cobertura y una fecha. |
| Mapas con tratamiento | B5 nombra un id para la inercia y para el dolor; ninguno queda "para después". |

---

## Solución de referencia (escenario del caso)

### Parte A · Turnos en línea, Policlínicas Altamar

**A1.** Idea: que los pacientes saquen, confirmen y cancelen turnos sin llamar. Decisión: autorizar la iniciación
(2026-12-11).

**A2 y A3.**

| Id | Supuesto | Familia | Criticidad | Certeza |
|---|---|---|---|---|
| S-001 | Al menos el 40 % de los turnos se sacará en línea desde el segundo año | deseabilidad | alta | baja |
| S-002 | Un recordatorio con confirmación baja el ausentismo del 18 % al 10 % | viabilidad | alta | baja |
| S-003 | La agenda clínica permite reservar y cancelar en tiempo real desde otro sistema | factibilidad | alta | baja |
| S-004 | La dirección médica libera las agendas con 60 días | viabilidad | media | media |
| S-006 | La normativa permite recordatorios con el consentimiento dado al pedir el turno | factibilidad | alta | media |

"Validar primero": S-001, S-002 y S-003 (la imagen `g5-mapa-supuestos.png`).

**A4.**

| Supuesto | Experimento | Criterio | Fecha límite | Responsable |
|---|---|---|---|---|
| S-001 | Prueba de humo: botón en el sitio con registro de interés, 3 semanas | ≥ 1.000 registros | 2026-11-27 | Inés Ferrer |
| S-002 | Piloto de recordatorio en una policlínica, 4 semanas (2.000 turnos) | ausentismo ≤ 12 % | 2026-12-04 | Inés Ferrer |
| S-003 | Prueba técnica de 5 días: reservar y cancelar 50 turnos | 50 de 50 y < 2 s | 2026-12-04 (replanificada al 2027-01-14) | Tomás Aguirre |

**A5.** S-002 salió mal (13,5 %, criterio 12 %): cambia B-01 y el VAN de las dos opciones baja 159.213 (opción 2: de
431.782 a 272.569, según `inversion.py`). Decide la ejecutiva, Carmen Olivera: ajustar (D-001). La idea sigue.

### Parte B

**B1.**

| Bolsa | Monto | Quién la libera |
|---|---|---|
| Contingencia (Σ EMV 24.000 + respuestas 4.000) | 28.000 | solo para R-001, R-002 y R-003 (enfoque de riesgos) |
| Reserva de gestión (5 % del BAC) | 8.540 | la junta |
| Presupuesto de cambio | 10.000 | la autoridad de cambio (Inés Ferrer) |
| Tope por cambio | 3.000 | por encima, la junta |

BAC 170.800 (paquetes 142.800 + contingencia); presupuesto autorizado 179.340. Registrado con `estado.py presupuesto`
(D-007).

**B2.** El caso es híbrido: integración predictiva (12), recordatorios híbridos (18) y portal adaptativo (23). Si fuera
regulado, pediría 16 artefactos y siete tolerancias; si fuera interno y pequeño, 7 y dos.

**B3.**

| Qué se adapta | Cómo | Por qué |
|---|---|---|
| Enfoques de gestión | una página cada uno; datos digitales dentro de calidad | proyecto mediano, un solo equipo (D-008) |
| Roles | Inés Ferrer: usuaria sénior, product owner y autoridad de cambio | una sola voz del negocio |
| Puerta de la etapa 3 | condicionada a la adopción medida en el release 1 | el VAN es sensible a la adopción (equilibrio en 11,6 % con el orden de magnitud, 12,6 % con el presupuesto) |

**B4.**

| Supuesto | ¿Validar o aceptar? | Quién lo acepta | Cobertura | Fecha |
|---|---|---|---|---|
| S-003 · interfaz de la agenda | validado el 2027-01-14 (50 de 50, 1,4 s) | — | — | — |
| S-006 · consentimiento para recordatorios | aceptado sin validar | la junta, decisión D-009 del 2027-01-15 | riesgo R-003 y su contingencia; el dictamen es condición antes del release de recordatorios | 2027-01-29 (al 2027-02-01 la sanidad avisa SUP-02 y REG-09) |

**B5.** (tablero de mapas del caso, `g5-tablero-mapas.png`)

| Elemento del mapa | Qué muestra | Tratamiento | Dueño |
|---|---|---|---|
| Agenda clínica del proveedor (producto, con inercia) | el proveedor controla la interfaz; el adaptador depende de ella | R-001, "La integración en tiempo real se atrasa" (`en-seguimiento`) | Tomás Aguirre |
| P5 «Intenta avisar que no va» (−2) | solo puede cancelar llamando en horario de atención | REQ-003 (confirmar o cancelar desde el recordatorio) y REQ-005 (reprogramar o cancelar en línea) | Inés Ferrer (usuaria sénior y product owner) |
