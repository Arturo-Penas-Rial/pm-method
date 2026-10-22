# Ejercicio · E2E-5 · Los supuestos, el experimento y las reservas de tu proyecto

## Cómo funciona este ejercicio

- **Para qué sirve:** llevar el caso a una idea o un proyecto tuyo. Vas a separar lo que sabés de lo que suponés,
  diseñar un experimento barato antes de invertir, separar las reservas del presupuesto, decir para quién es cada
  requisito y dejar escrita la adaptación de la gestión.
- **Cuándo se hace:** la parte A, al cierre de la clase 1, después de la demostración (10 minutos); la parte B, al
  cierre de la clase 2, después de la demostración (10 minutos). Si lo hacés por tu cuenta, calculá 20 minutos.
- **Qué hacés:** completás la hoja de trabajo con una idea que alguien quiera aprobar en los próximos meses, o con un
  proyecto que se aprobó hace poco. Alcanza con papel o una planilla, y con el orden de magnitud de los números. Si no
  tenés uno, usá el escenario del caso: los datos de partida están en
  [Lo que necesitás saber](#lo-que-necesitás-saber).
- **Cómo te autoevaluás:** al final de cada parte hay una tabla de criterios. Marcá cuáles cumple tu hoja; un criterio
  sin cumplir es un hallazgo sobre tu proyecto, no un error del ejercicio.
- **Ejemplo resuelto:** al final está la hoja resuelta con el escenario del caso, y cada dato dice de qué paso de la
  guía sale. Miralo **después** de intentarlo, para comparar, no antes.

---

## Lo que necesitás saber

### El escenario del caso

La red de Policlínicas Altamar (6 policlínicas, 240.000 turnos por año, 70 % por teléfono, ausentismo del 18 %) quiere
que los pacientes saquen, confirmen y cancelen turnos sin llamar. Carmen Olivera es la ejecutiva; Pablo Rinaldi, el
gestor; Inés Ferrer, usuaria sénior, product owner y autoridad de cambio; Tomás Aguirre, proveedor sénior (jefe de TI).
La clase 1 decide si vale la pena autorizar la iniciación; la clase 2 diseña el proyecto hasta la puerta
`autorizar-proyecto` del 2027-01-15.

**Datos de partida para la parte A** (si usás el caso):

- Lo que el mandato y las lecciones dan por cierto: al menos el 40 % de los turnos se sacará en línea desde el segundo
  año (20 % el primero); un recordatorio con confirmación baja el ausentismo del 18 % al 10 %; la agenda clínica del
  proveedor permite reservar y cancelar en tiempo real desde otro sistema; la dirección médica libera las agendas con
  60 días de anticipación; la normativa permite enviar recordatorios con el consentimiento dado al pedir el turno; el
  costo por mensaje se mantiene en USD 0,02. Se mantienen el teléfono y el presencial (restricción, no supuesto).
- Lecciones previas (aprobadas en otros proyectos de la red): la app de resultados de 2024 tuvo 11 % de uso en mayores
  de 65; la integración con la agenda clínica de 2025 se estimó en 4 semanas y llevó 14; un piloto de recordatorios bajó
  el ausentismo, pero nadie midió la línea base.
- Para A5: el piloto de recordatorios en una policlínica dio 13,5 % de ausentismo (criterio: 12 % o menos). Con el 10 %
  del mandato, el VAN de la opción completa es 431.782; con el 13,5 % medido, 272.569.

**Datos de partida para la parte B:**

- WBS: USD 142.800. Riesgos: la agenda sin interfaz documentada (P3 × I4, USD 30.000), la adopción baja en mayores de
  65 (P3 × I3, USD 12.000; canal asistido por USD 4.000) y un dictamen legal que exija consentimiento explícito (P2 ×
  I3, USD 10.000). La reserva de gestión es el 5 % del BAC. La junta fija un presupuesto de cambio de 10.000 con tope
  de 3.000 por cambio.
- Enfoque de entrega con los nueve criterios: recordatorios 18 (híbrido), turnos en línea 23 (adaptativo), integración
  con la agenda 12 (predictivo). Proyecto mediano, con datos de salud y un solo equipo.
- El 2027-01-14, la prueba técnica de la agenda dio 50 de 50 reservas y cancelaciones (1,4 s). El dictamen legal sobre
  el consentimiento llega el 2027-01-29, después de la puerta del 15/1.
- Mapas: la agenda clínica del proveedor es un producto con inercia (sistema en uso en las 6 policlínicas, el
  proveedor controla la interfaz). En el recorrido del paciente, el paso «Intenta avisar que no va» (emoción −2) tiene
  un dolor: solo puede cancelar llamando en horario de atención.
- Personas: el paciente que agenda por teléfono, la recepcionista del call center y el paciente mayor de 65 que no usa
  aplicaciones. Requisitos Must: recordatorio 48 h antes (REQ-001), confirmar o cancelar desde el recordatorio y
  liberar el turno (REQ-003), sacar turno en línea (REQ-004) y reservar en la agenda en tiempo real (REQ-006).

### Conceptos mínimos

- **Supuesto:** algo que se da por cierto sin evidencia; una **restricción** es un límite que no se discute.
- **Familias:** deseabilidad (¿lo van a usar?), viabilidad (¿cierra económicamente?) y factibilidad (¿se puede
  construir y operar?).
- **Criticidad y certeza:** criticidad, cuánto cambia el caso si el supuesto es falso; certeza, cuánta evidencia hay
  hoy. Criticidad alta y certeza baja = hipótesis: se valida primero.
- **Experimento barato:** más barato que equivocarse, con fecha y con el criterio para seguir decidido **antes** del
  resultado.
- **VAN (valor actual neto):** la suma de los flujos de cada año descontados a la tasa de la organización; se compara
  siempre con la opción 0, "no hacer nada distinto".
- **Contingencia:** cubre los riesgos identificados (su EMV, valor monetario esperado, más el costo de las respuestas);
  EMV = impacto en dinero × probabilidad (P1 10 % · P2 30 % · P3 50 % · P4 70 % · P5 90 %).
- **BAC:** paquetes de la WBS + contingencia. **Reserva de gestión:** cubre lo no identificado y la libera solo la
  junta. **Presupuesto de cambio:** va aparte y lo administra la autoridad de cambio, con un tope por cambio.
- **Enfoque de entrega:** nueve criterios de 1 (favorece predictivo) a 3 (favorece adaptativo) por entregable: 13 o
  menos es predictivo, de 14 a 21 híbrido y 22 o más adaptativo.
- **Adaptación (tailoring):** decidir cuánta formalidad necesita cada parte de la gestión, y por qué; se aligeran los
  documentos, no las decisiones.
- **Aceptar un supuesto:** si un supuesto crítico no se valida antes de la puerta, la junta puede aceptarlo con una
  decisión escrita que lo cite y diga cómo se cubre; en pm-method, la puerta lo marca con P-11.
- **Persona de usuario:** el arquetipo de quien pide, usa o aprovecha una capacidad (no es un interesado, pero un
  interesado la representa). Un requisito Must sin persona es una señal: falta alguien o sobra la prioridad.
- **Inercia y dolor:** en un mapa de Wardley, la inercia es algo difícil de cambiar (un sistema en uso); en un recorrido
  del cliente, el dolor es dónde sufre la persona. Los dos necesitan un tratamiento con id.

---

## Hoja de trabajo · parte A · El mapa de supuestos y un experimento barato (clase 1)

**A1. La idea en una frase y la decisión que se espera.**

> Idea: ……………………………………………… · Decisión que se espera: ………………………… · ¿Para cuándo? ……………

**A2. Cinco supuestos.** Al menos uno de cada familia. Criticidad y certeza: alta / media / baja.

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

## Hoja de trabajo · parte B · Las reservas y la adaptación (clase 2)

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

**B6. Para quién es cada requisito.** Dos personas de usuario y los requisitos imprescindibles (Must) que cada una
pide, usa o aprovecha sin usarlos.

| Persona (quién es, en una línea) | De dónde sale (entrevista, observación, documento, supuesto) | Pide | Usa | Aprovecha | Interesado que la representa |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

> Must sin persona: ……………………………… · ¿Falta una persona o sobra la prioridad? ………………

### Autoevaluación de la parte B

| Criterio | Cumple si… |
|---|---|
| Bolsas separadas | Contingencia, reserva de gestión y presupuesto de cambio tienen monto y dueño distintos; nada se cuenta dos veces. |
| Autoridad delimitada | El tope por cambio es menor que el presupuesto de cambio. |
| Adaptación escrita | B3 dice qué se aligera y por qué, sin saltear ninguna decisión de la junta. |
| Hipótesis a la vista | B4 tiene una decisión escrita de quien puede aceptar el supuesto, una cobertura y una fecha. |
| Mapas con tratamiento | B5 nombra un id para la inercia y para el dolor; ninguno queda "para después". |
| Cada Must con su persona | En B6 todo requisito Must tiene al menos una persona que lo pide, lo usa o lo aprovecha, y cada persona dice de dónde sale. |

---

## Para ir más allá

- ¿Qué número del último caso de negocio que viste aprobar descansaba en un supuesto que nadie había probado?
- Si tu experimento sale mal, ¿la idea se ajusta o se abandona? ¿Quién lo decidió antes de ver el resultado?

---

## Ejemplo resuelto (escenario del caso)

Cifras de la corrida de referencia ([salida-g5.md](../../guias/evidencia/salida-g5.md)); entre paréntesis, el paso de
la [guía E2E-5](../../guias/E2E-5-idea-a-proyecto.md) de donde sale cada dato.

### Parte A · Turnos en línea, Policlínicas Altamar

**A1.** Idea: que los pacientes saquen, confirmen y cancelen turnos sin llamar (paso 1). Decisión: autorizar la
iniciación, en la puerta `autorizar-inicio` del 2026-12-11 (paso 6).

**A2.** Supuestos registrados el 2026-11-04 (paso 2; el texto y el origen de cada uno están en la evidencia).

| Id | Supuesto | Familia | Criticidad | Certeza | Evidencia al registrarlo |
|---|---|---|---|---|---|
| S-001 | Al menos el 40 % de los turnos se sacará en línea desde el segundo año (20 % el primero) | deseabilidad | alta | baja | mandato y lección L-001 (11 % de uso en mayores de 65) |
| S-002 | Un recordatorio con confirmación baja el ausentismo del 18 % al 10 % | viabilidad | alta | baja | mandato y L-003 (piloto sin línea base) |
| S-003 | La agenda clínica del proveedor permite reservar y cancelar en tiempo real desde otro sistema | factibilidad | alta | baja | mandato y L-002 (4 semanas estimadas, 14 reales) |
| S-004 | La dirección médica libera las agendas con 60 días de anticipación | viabilidad | media | media | sin cita en el registro |
| S-006 | La normativa permite enviar recordatorios con el consentimiento dado al pedir el turno | factibilidad | alta | media | sin cita en el registro |

**A3.** "Validar primero" (alta, baja): S-001, S-002 y S-003. Alta y media: S-006. Media y media: S-004 (paso 2).

**A4.** Experimentos del paso 3 (el caso da la duración, no el costo).

| Supuesto | Experimento | Criterio | Duración | Responsable | Fecha límite |
|---|---|---|---|---|---|
| S-001 | prueba de humo: botón en el sitio con registro de interés | ≥ 1.000 registros | 3 semanas | Inés Ferrer | 2026-11-27 |
| S-002 | piloto de recordatorio con confirmación en la Policlínica Centro (2.000 turnos) | ausentismo ≤ 12 % | 4 semanas | Inés Ferrer | 2026-12-04 |
| S-003 | prueba técnica: reservar y cancelar 50 turnos en el entorno del proveedor | 50 de 50 y < 2 s | 5 días | Tomás Aguirre | 2026-12-04, replanificada al 2027-01-14 |

**A5.** S-002 salió mal: 13,5 % contra un criterio de 12 % (paso 3). Cambia el beneficio de turnos recuperados (B-01) y
el VAN de las dos opciones baja 159.213; el de la opción 2, de 431.782 a 272.569 (paso 4). Decide la ejecutiva, Carmen
Olivera: ajustar, el caso usa 13,5 % (D-001, paso 3). La idea sigue: la opción 2 sigue siendo la mejor (paso 4).

### Parte B

**B1.** Presupuesto del paso 9 (D-007).

| Bolsa | Monto | Para qué se usa | Quién la libera | ¿Escrita y aprobada? |
|---|---|---|---|---|
| Contingencia | 28.000 = Σ EMV 24.000 (R-001 15.000, R-002 6.000, R-003 3.000) + respuestas 4.000 | los riesgos R-001, R-002 y R-003 | el caso no lo dice | sí: `estado.py presupuesto … riesgo=28000`, Carmen Olivera, 2027-01-12 |
| Reserva de gestión | 8.540 (5 % del BAC) | lo no identificado | la junta | sí, en la misma decisión |
| Presupuesto de cambio | 10.000 | los cambios aprobados | la autoridad de cambio, Inés Ferrer | sí |
| Tope por cambio | 3.000 | — | por encima, la junta | sí |

BAC 170.800 (paquetes 142.800 + contingencia); presupuesto autorizado 179.340 (BAC + reserva de gestión) (paso 9).

**B2.** Híbrido: integración predictiva (12), recordatorios híbridos (18) y portal adaptativo (23) (paso 5). Si fuera
regulado, pediría 16 artefactos y siete tolerancias; si fuera interno y pequeño, 7 artefactos y dos tolerancias (paso
12).

**B3.** Sección 8 del PID (paso 13; la tabla completa está en la evidencia).

| Qué se adapta | Cómo | Por qué |
|---|---|---|
| Enfoques de gestión | una página cada uno; datos digitales dentro de calidad | proyecto mediano, un solo equipo (D-008, paso 11) |
| Roles | Inés Ferrer: usuaria sénior, product owner y autoridad de cambio | una sola voz del negocio |
| Puerta de la etapa 3 | condicionada a la adopción medida en el release 1 | el VAN es sensible a la adopción: equilibrio en 11,6 % de adopción estable con el orden de magnitud y 12,6 % con el presupuesto (pasos 4 y 9) |

**B4.** (paso 13, salvo donde se indica).

| Supuesto | ¿Validar o aceptar? | Quién lo acepta | Cobertura | Fecha |
|---|---|---|---|---|
| S-003, interfaz de la agenda | validado el 2027-01-14 (50 de 50, 1,4 s) | — | — | — |
| S-006, consentimiento para recordatorios | aceptado sin validar | la junta, decisión D-009 del 2027-01-15 | riesgo R-003 y su contingencia; el dictamen es condición antes del release de recordatorios | 2027-01-29; al 2027-02-01 la sanidad avisa SUP-02 y REG-09, y el radar pone S-006 primero en «decidir», a cargo de Carmen Olivera (paso 14) |

**B5.** Tablero de mapas del proyecto autorizado (paso 14).

| Elemento del mapa | Qué muestra | Tratamiento | Dueño |
|---|---|---|---|
| Agenda clínica del proveedor (producto, con inercia) | el proveedor controla la interfaz y el adaptador depende de ella (paso 5b) | R-001, «La integración en tiempo real se atrasa», `en-seguimiento` (pasos 9 y 14) | Tomás Aguirre, propietario de R-001 (paso 9, en la evidencia) |
| P5 «Intenta avisar que no va» (−2) | solo puede cancelar llamando en horario de atención (paso 5b) | REQ-003 (confirmar o cancelar y liberar el turno) y REQ-005 (reprogramar) (paso 6) | Inés Ferrer, usuaria sénior y product owner: confirmó el recorrido (paso 5b) y acepta cada release (enfoque de calidad del paso 11, en la evidencia) |

**B6.** Personas de usuario del 2027-01-12 (paso 10b).

| Persona | De dónde sale | Pide | Usa | Aprovecha | Representa |
|---|---|---|---|---|---|
| PU-001 Paciente que agenda por teléfono | observación: la propone `personas candidatos` desde el recorrido del paciente y el mandato | — | REQ-001, REQ-003, REQ-004, REQ-005 | REQ-006 | ST-006, comisión de usuarios |
| PU-002 Recepcionista del call center | supuesto, a validar con entrevistas en recepción | REQ-003 | REQ-002 | REQ-004 | ST-005, recepción y call center |
| PU-003 Paciente mayor de 65 | documento: la lección L-001 (11 % de uso en mayores de 65) | REQ-007 | REQ-001, REQ-003 | — | ST-006 |

Must sin persona: REQ-006 (STK-13), hasta que se marca al paciente como quien lo aprovecha: nadie usa la integración,
pero el paciente ve turnos reales. Resultado: los 4 Must con persona y REQ-003 sirve a las tres (paso 10b). En la
variante con BMAD, las personas salen de los recorridos del PRD (Marta, Diego y Lucía) y los 12 FR quedan con persona
(paso 16b).
