# Guion del instructor · E2E-5 · De la idea al proyecto diseñado

**Caso:** [Guía E2E-5](../../guias/E2E-5-idea-a-proyecto.md) · **Evidencia:** [salida-g5.md](../../guias/evidencia/salida-g5.md)
· **Ejercicio:** [ejercicio.md](ejercicio.md) · **Diapositivas:** [diapositivas.json](diapositivas.json) (las arma el
generador común) · **Público:** gestores de proyecto con algo de PMBOK o PRINCE2 y líderes de negocio.

**Formato:** dos clases de 90 minutos. La primera responde "¿vale la pena?" (puesta en marcha, pasos 1 a 6, con el
contraste de la variante con BMAD, pasos 15 a 17). La segunda diseña el proyecto hasta su autorización (iniciación,
pasos 7 a 14, con el bloque C). La clase 2 usa lo que deja la 1: supuestos tratados, una opción elegida con números y un
enfoque decidido. Sin eso, el presupuesto y las tolerancias de la clase 2 se apoyarían en supuestos que nadie verificó,
que es justo lo que el caso quiere evitar.

Todas las cifras de este guion salen de la corrida de referencia (`docs/guias/evidencia/salida-g5.md`). El escenario
(Policlínicas Altamar) es ficticio. No uses estadísticas de la industria en el gancho: preguntale a la audiencia y usá
los datos del caso.

---

## Objetivos de aprendizaje

Al terminar las dos clases, cada asistente puede:

1. Armar un **mapa de supuestos** (criticidad × certeza) y elegir dónde invertir primero en aprender.
2. Diseñar un **experimento barato** con el criterio de decisión fijado antes de ver el resultado, y llevar un
   resultado negativo al caso de negocio.
3. Comparar **opciones de negocio** contra "no hacer nada distinto" con VAN, TIR, repago y el punto de equilibrio del
   beneficio que más pesa.
4. Elegir el **enfoque de entrega por entregable** con criterios explícitos, explicar por qué un proyecto resulta
   híbrido y contrastarlo con un **mapa de Wardley** (qué construir, qué comprar, dónde hay inercia) y con el
   **recorrido del cliente**.
5. Separar **contingencia, reserva de gestión y presupuesto de cambio**, decir quién libera cada uno, **adaptar** la
   formalidad de la gestión al contexto y llevar a la junta los supuestos sin validar para que los **valide o los
   acepte por escrito**.

## Requisitos previos

**Asistentes:** saber qué es un caso de negocio y un presupuesto; no hace falta saber programar ni calcular VAN a mano.
Conviene haber visto otro caso E2E, pero no es obligatorio: este es el primero en el ciclo de vida.

**Instructor (antes de cada clase):**
- Claude Code con el plugin pm-method 2.3.0. Para la variante b, una carpeta vacía
  (`~/proyectos-prueba/turnos-e2e-5`); para la variante a, una copia del fixture en `~/proyectos-prueba/portal-e2e-5a`,
  según el [README de las guías](../../guias/README.md#cómo-usar-las-guías).
- La evidencia y las imágenes abiertas en pestañas: `salida-g5.md` y `docs/guias/img/g5-*.png` (plan B).
- Para la clase 2: un proyecto ya avanzado hasta el paso 6, preparado antes con los prompts de los pasos 1 a 6. Para
  mostrar archivos del recorrido completo sirve la carpeta que deja el driver:
  `cd scripts/pruebas/guias_e2e && GUIAS_SALIDA=<dir> TMPDIR=<dir> python3 g5.py <dir>/salida-g5.md` (la ruta aparece al
  final como "Carpeta del recorrido"; los tres diseños del bloque C quedan al lado, en `diseno-1` a `diseno-3`).
- Probar el micrófono y el tamaño de letra de la terminal (mínimo 18 pt).

## El ejercicio

La hoja es una sola para asistentes e instructor: [ejercicio.md](ejercicio.md) (en HTML, `E2E-5-ejercicio.html`). Se
basta sola: empieza por «Cómo funciona este ejercicio», resume el escenario y los conceptos que hacen falta, trae la
hoja de trabajo con sus criterios de autoevaluación y termina con un **ejemplo resuelto** con el escenario del caso,
plegado, donde cada dato cita el paso de la guía de donde sale.

- **Cuándo:** la parte A en el minuto 75 de la clase 1 y la parte B en el minuto 75 de la clase 2, siempre después de
  la demostración; 10 minutos cada una.
- **Cómo se presenta:** proyectá la diapositiva del ejercicio y leé en voz alta «Cómo funciona este ejercicio» (un
  minuto). Quien no tenga un proyecto propio trabaja con los datos de partida del caso, que están en «Lo que necesitás
  saber».
- **Mientras trabajan:** pedí que escriban el criterio del experimento antes de imaginar el resultado. En la parte B,
  si alguien no tiene reserva de gestión, que lo anote: es un hallazgo, no un error del ejercicio.
- **Ejemplo resuelto:** pedí que no lo abran antes de intentar. Mostralo recién en los dos últimos minutos del bloque:
  desplegalo en pantalla y comparalo con la hoja de uno o dos voluntarios. Al imprimir, sale desplegado al final de la
  hoja.
- **Autoevaluación:** cada asistente marca los criterios de su parte; un criterio sin cumplir es un hallazgo sobre su
  proyecto, no un error del ejercicio.

---

## Clase 1 · ¿Vale la pena?

**Pregunta de la clase:** ¿qué tendría que ser cierto para que esta idea valga la pena, y cómo lo sabemos barato?

### Agenda minuto a minuto

| Minuto | Bloque | Qué pasa | Material |
|---|---|---|---|
| 0–10 | Gancho | Pregunta a mano alzada: "¿Cuántos de ustedes vieron aprobar un proyecto con un supuesto que nadie verificó?". Después, el dato del caso: un solo supuesto inflaba el VAN de cada opción en USD 159.213. | Diapositivas de gancho y pregunta |
| 10–25 | Concepto | Mandato y lecciones; supuesto e hipótesis; criticidad × certeza; experimento con criterio previo; opciones contra "no hacer nada"; VAN, TIR, repago y punto de equilibrio; nueve criterios del enfoque; mapa de Wardley y recorrido del cliente. | Diapositivas de concepto |
| 25–65 | Demostración | Pasos 1 a 6 (detalle abajo). | Terminal + evidencia |
| 65–75 | Pregunta y discusión | "¿Qué harían con S-002: abandonar, ajustar o seguir?" y contraste con la variante a (pasos 15 a 17, con evidencia). | Diapositivas de pregunta y tabla a/b |
| 75–85 | Ejercicio | Parte A: mapa de supuestos y un experimento barato de un proyecto propio; ejemplo resuelto al cerrar el bloque. | [ejercicio.md](ejercicio.md) · [cómo conducirlo](#el-ejercicio) |
| 85–90 | Cierre | Tres mensajes clave y anticipo de la clase 2. | Diapositiva de cierre |

### Demostración (40 minutos)

| Min | Paso | En vivo o con evidencia | Qué mostrar | Qué decir |
|---|---|---|---|---|
| 25–29 | 1 | Evidencia | "enfoque de entrega: predictivo" (por defecto) y L-001 a L-003 | "Todavía no elegimos enfoque: lo vamos a decidir con criterios, no por costumbre." |
| 29–38 | 2 | **En vivo** (prompt del paso 2) | "artefactos: 5 candidatos"; S-001 a S-007; sanidad con 4 SUP-01; `g5-mapa-supuestos.png` | "Tres supuestos sostienen todo el caso y ninguno tiene evidencia. Ahí va la primera plata." |
| 38–48 | 3 | **En vivo** (primer prompt del paso 3); resultados con evidencia | Sanidad al 2026-11-05 en 0 AVISO; al 2026-12-07, SUP-02 (S-003) y SUP-03 (S-002); D-001 y D-002 | "El experimento malo es el que no cambia nada. Este cambió el caso." |
| 48–55 | 4 | **En vivo** (prompt del paso 4) o evidencia | Los dos CSV de flujos y la salida de `inversion.py`: 265.681 → 106.468 y 431.782 → 272.569; TIR 54,3 %; repago 1,78 años; B-02 en equilibrio al 29,1 % (adopción 11,6 %); `g5-van-opciones.png` | "El VAN bajó en las dos opciones por igual: 159.213. La 2 sigue ganando, y sabemos cuánto puede fallar la adopción antes de que deje de convenir." |
| 55–59 | 5 | **En vivo** (prompt del paso 5) | Sumas 18, 23 y 12; `estado.py set enfoque_entrega=hibrido --por …` con "Decisión anotada: D-003"; `g5-enfoque-entrega.png` | "No elegimos híbrido porque está de moda: salió así porque cada entregable puntúa distinto. Y quedó escrito quién lo decidió." |
| 59–63 | 5b | Evidencia | `g5-wardley.png`: construir el portal, comprar los recordatorios, adaptador atado a la agenda con inercia; `g5-recorrido.png`: dos pasos en −2; sanidad con MAP-02 y MAP-03 | "El mapa dice lo mismo que los criterios, desde el mercado. Y la sanidad no deja olvidar la inercia ni el dolor sin tratar." |
| 63–65 | 6 | Evidencia | Puerta `autorizar-inicio` (D-004), "Artefactos: 9 (2 aprobados)"; MAP-03 resuelto con REQ-003 y REQ-005 | "La junta autoriza gastar en diseñar, no en construir." |

**Prompts exactos:** los de los pasos 2, 3, 4 y 5 de la guía, copiados tal cual. Si Claude pregunta, responder con el
texto de "Si te pregunta" de cada paso.

### Mensajes clave

1. Todo caso de negocio descansa en supuestos. Los **críticos y sin evidencia** son hipótesis: se validan antes de
   invertir, con un criterio decidido de antemano.
2. Un resultado negativo **no mata la idea**: la ajusta. Lo grave es que quede archivado (SUP-03).
3. Las opciones se comparan **contra no hacer nada**, con la fórmula a la vista y el punto de equilibrio del beneficio
   que más pesa; el enfoque se elige **por entregable** con criterios, y el mapa de Wardley convierte la inercia en un
   riesgo registrado.

### Preguntas para la audiencia (con respuesta esperada)

| Pregunta | Respuesta esperada |
|---|---|
| ¿Cuántos vieron aprobar un proyecto con un supuesto que nadie verificó? | Muchas manos. Pedir un ejemplo breve: suele ser la adopción o una integración con un tercero. |
| El piloto bajó el ausentismo al 13,5 % y el criterio era 12 %. ¿Abandonamos, ajustamos o seguimos? | Ajustar: el supuesto (10 %) es falso, pero la idea sigue siendo valiosa con el dato real (D-001). |
| ¿Por qué la opción 0 tiene VAN 0? | Porque es la base de comparación: las otras miden cuánto mejoran respecto de seguir igual (43.200 turnos perdidos por año). |
| ¿Cuánto puede caer la adopción antes de que la opción 2 deje de convenir? | Hasta una adopción estable del 11,6 % (el 29,1 % de lo estimado). Como B-02 aporta el 65 % del valor de los beneficios, esa sensibilidad es obligatoria. |
| En la variante con BMAD, ¿de dónde sale la línea base para el VAN? | De ningún lado todavía: el brief declara que no hay métricas (`brief.md:26`). Primero hay que medir. |

### Dudas frecuentes

- **"¿Esto no es trabajo de la iniciación?"** Los experimentos baratos pueden hacerse en la puesta en marcha o como
  paquetes cortos de la etapa 1 (`pm-mandato-y-brief`, references/guia.md §9). Lo importante es que lleguen antes de
  comprometer la inversión completa.
- **"¿Tengo que saber calcular el VAN?"** No. `pm-caso-de-negocio` escribe los flujos en un CSV (una fila por concepto
  y año) y corre `inversion.py`, que imprime las fórmulas, el VAN, la TIR, el repago simple y descontado, la
  sensibilidad y el punto de equilibrio. Las cifras de origen y la tasa las pone la organización.
- **"¿El sistema decide por mí?"** No: los supuestos, los experimentos, el enfoque y la puerta los confirma una persona
  con rol (Carmen Olivera en el caso). El sistema registra quién y cuándo: `estado.py set enfoque_entrega … --por`
  anota la decisión en `decisiones.csv`.

### Plan B si la demo falla

Seguí con la evidencia: `salida-g5.md` tiene cada comando con su salida, paso por paso. Mostrá `g5-mapa-supuestos.png`
en el paso 2, la sección de sanidad del paso 3, la salida de `inversion.py` y `g5-van-opciones.png` en el paso 4. Decí:
"esto es lo que el sistema produjo en la corrida de referencia; los números son los mismos que verían en vivo".

### Conexión con la clase 2

"Hoy decidimos que vale la pena y cómo vamos a entregar. La próxima clase diseñamos el proyecto: beneficios con dueño,
presupuesto con reservas que no se cuentan dos veces, la gestión adaptada al contexto, y la puerta de la junta. Y vamos a
ver qué pasa con S-003 y S-006, que todavía no tienen resultado."

---

## Clase 2 · Diseñar el proyecto

**Pregunta de la clase:** ¿cómo dejamos el proyecto listo para que la junta delegue con cifras?

### Agenda minuto a minuto

| Minuto | Bloque | Qué pasa | Material |
|---|---|---|---|
| 0–10 | Gancho | Pregunta: "En tu proyecto, ¿quién puede gastar la reserva? ¿Está escrito?". Dato del caso: el mismo proyecto pide 7 artefactos de gestión si es interno y pequeño, y 16 si es regulado. | Diapositivas de gancho y `g5-tres-disenos.png` |
| 10–25 | Concepto | Contexto de sesión; mapa y enfoque de beneficios; descripción del producto del proyecto; contingencia, BAC, reserva de gestión y presupuesto de cambio; adaptación (tailoring); P-11: validar o aceptar. | Diapositivas de concepto |
| 25–65 | Demostración | Pasos 7 a 14 (detalle abajo). | Terminal + evidencia |
| 65–75 | Pregunta y discusión | "¿Qué diseño le corresponde a tu proyecto: pequeño, regulado o ágil?" | Tabla del bloque C |
| 75–85 | Ejercicio | Parte B: las reservas y la adaptación de un proyecto propio; ejemplo resuelto al cerrar el bloque. | [ejercicio.md](ejercicio.md) · [cómo conducirlo](#el-ejercicio) |
| 85–90 | Cierre | Tablero de una página, tablero de mapas, mensajes clave y conexión con E2E-1 y E2E-4. | `g5-tablero.png`, `g5-tablero-mapas-169.png` |

### Demostración (40 minutos)

| Min | Paso | En vivo o con evidencia | Qué mostrar | Qué decir |
|---|---|---|---|---|
| 25–31 | 7 | **En vivo** (prompt del paso 7) | El contexto al 2027-01-08 ("Supuestos críticos sin validar: S-003, S-006"); la verificación temprana con códigos: P-01 y L-01, P-05, P-06, P-11, P-04 (aviso), P-09, P-10; luego el enfoque de beneficios | "Un mes después, la sesión arranca con lo que dicen los registros, no con lo que recordamos. Y verificar la puerta antes de tiempo da la lista de trabajo de la iniciación." |
| 31–34 | 8 | Evidencia | "12 elementos, 7 hojas · esfuerzo 2180 h · costo 142,800" | "Producto antes que tarea: cada paquete cita sus REQ." |
| 34–42 | 9 | **En vivo** (prompt del paso 9) | R-001 a R-003 con EMV; R-001 cubre la inercia del mapa (MAP-02 resuelto); la tabla 142.800 → 28.000 → 170.800 → 8.540 → 179.340 y 10.000 aparte; D-007; `inversion.py` con la opción 2 dos veces: VAN 263.229, −9.340 | "Tres bolsas, tres dueños. La reserva de gestión no está en el BAC y solo la libera la junta." |
| 42–45 | 10 | Evidencia | Matriz: 2 de cerca, 3 satisfechos, 2 informados; "RACI válida" | "Lo mínimo que pide la puerta; E2E-3 lo desarrolla." |
| 45–48 | 11 | Evidencia | D-008 y los cuatro enfoques de una página | "Adaptar es decidir cuánta formalidad, por qué, y dejarlo escrito." |
| 48–53 | 12 | Evidencia | Tabla de los tres diseños y `g5-tres-disenos.png` | "El ágil no tiene menos puertas: tiene documentos más cortos." |
| 53–60 | 13 | **En vivo** (los dos prompts del paso 13) | "condición P-11 … S-003, S-006"; S-003 validado; D-009 "La junta acepta S-006 sin validar…"; "aviso P-11 … S-006 (D-009)"; puerta D-010; "Autorizado: sí" | "P-11 no bloquea: avisa que la junta invierte sobre hipótesis. Acá validamos una y la junta aceptó la otra por escrito." |
| 60–65 | 14 | Evidencia | `g5-tablero.png`; el tablero de mapas (`g5-tablero-mapas-169.png`): "Avisos MAP vigentes: 0", la agenda con "inercia → R-001" y cada dolor del paciente con su tratamiento (S-001, S-002, REQ-003 y REQ-005); la sanidad al 2027-02-01: REG-09 para R-001 a R-003 y SUP-02 para S-006 | "Los mapas del paso 5b terminan en un tablero: cada inercia con su riesgo y cada dolor con su tratamiento, a la vista de la junta. Y aceptar no es olvidar: si el dictamen no llega y nadie revisa los riesgos, la sanidad lo dice el primer día." |

**Prompts exactos:** los de los pasos 7, 9 y 13 de la guía, copiados tal cual.

### Mensajes clave

1. Un beneficio sin dueño, línea base y fecha de medición no es un criterio de éxito (P-04).
2. **Contingencia, reserva de gestión y presupuesto de cambio** son bolsas distintas, con dueños distintos; ninguna se
   cuenta dos veces.
3. Adaptar no es saltearse pasos: se aligeran los documentos, no las decisiones. Y nadie invierte sobre una hipótesis
   sin saberlo: se valida o la junta la acepta por escrito, y queda vigilada (P-11, SUP-02, REG-09).

### Preguntas para la audiencia (con respuesta esperada)

| Pregunta | Respuesta esperada |
|---|---|
| ¿Quién puede gastar la reserva de gestión? | Solo la junta (en el caso, Carmen Olivera). La contingencia financia las respuestas a R-001, R-002 y R-003; el presupuesto de cambio lo administra la autoridad de cambio, con un tope de 3.000 por cambio. |
| ¿Por qué el VAN bajó de 272.569 a 263.229? | Porque la inversión pasó del orden de magnitud (180.000) al presupuesto real (179.340 autorizado + 10.000 de cambio = 189.340). |
| ¿Qué diseño necesita más artefactos y por qué? | El regulado: 16 y siete tolerancias, por la auditoría de privacidad y el aseguramiento independiente. |
| La junta quiere aprobar sin el dictamen legal (S-006). ¿Se puede? | Sí, si lo decide expresamente: una decisión de la junta que cita S-006 y dice que lo acepta (D-009). P-11 pasa a aviso, el supuesto sigue abierto con su fecha y el riesgo R-003 cubre el efecto. |

### Dudas frecuentes

- **"¿Por qué P-11 es condición y no bloqueo?"** Porque la junta puede decidir invertir con un supuesto abierto; lo que
  no puede es hacerlo sin saberlo. Si aprueba con `condicionado`, P-11 pasa a ser una condición formal con seguimiento.
- **"¿Qué cuenta como aceptación?"** Una decisión de nivel junta, ejecutivo o capa de negocio en `decisiones.csv` que
  cite el id del supuesto y use el verbo "aceptar" ("aceptación" no cuenta). La verificación muestra el aviso con la
  D-### que lo aceptó (`docs/PUERTAS.md`).
- **"¿Qué ve el gestor al abrir una sesión nueva?"** El hook de inicio agrega el contexto de `estado.py contexto`:
  abiertos, supuestos críticos sin validar, condiciones de puertas y próxima puerta, con ids. Si una nota de memoria
  dice otra cosa, mandan los registros.
- **"¿El bloque C son tres proyectos?"** Para comparar, sí: tres carpetas con su `estado.json`. En la vida real se
  elige un diseño (en el caso, el híbrido de los pasos 1 a 13).
- **"¿Hace falta autorizar la etapa 2 hoy?"** El caso termina en `autorizar-proyecto`. La puerta `autorizar-etapa` de la
  primera etapa de entrega se muestra en E2E-2 y E2E-4.

### Plan B si la demo falla

Usá la evidencia de los pasos 7, 9, 13 y 14: cada verificación de puerta muestra sus hallazgos con código, y la salida
de `inversion.py` y de la sanidad al 2027-02-01 están copiadas en `salida-g5.md`. Imágenes: `g5-presupuesto.png`,
`g5-tres-disenos.png`, `g5-tablero.png` y `g5-tablero-mapas.png` (variante con BMAD: `g5-tablero-mapas-bmad.png`).

### Conexión con el caso siguiente

"El proyecto quedó autorizado con presupuestos, tolerancias y autoridad delegada escritos, y con lo aceptado bajo
vigilancia. Lo que sigue es ejecutarlo: en E2E-1 vemos cómo se gestionan sus riesgos etapa por etapa y en E2E-4, la
ejecución con BMAD, la calidad y el cierre."
