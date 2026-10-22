# Guion del instructor · E2E-1 · Ciclo completo de gestión de riesgos

**Caso:** [Guía E2E-1](../../guias/E2E-1-riesgos.md) · **Evidencia:** [salida-g1.md](../../guias/evidencia/salida-g1.md)
· **Ejercicio:** [ejercicio.md](ejercicio.md) · **Diapositivas:** [diapositivas.json](diapositivas.json) (las arma el
generador común) · **Público:** gestores de proyecto con algo de PMBOK o PRINCE2 y líderes de negocio.

**Formato:** dos clases de 90 minutos. La primera lleva el registro desde el enfoque de riesgo hasta el presupuesto de
riesgo fijado por la junta (pasos 1 a 7, con la variante sin BMAD del paso 15 junto a la identificación). La segunda
muestra el control continuo durante la etapa (pasos 8 a 14). Se dividió así por dos motivos. El caso tiene 15 pasos y
cuatro demostraciones de peso (identificación, opciones de respuesta con su plan de contingencia, reserva, revisión
periódica): en una sola clase habría que saltear la revisión periódica o la reserva, que son justamente lo que en la
práctica no se hace. Además, la clase 2 se apoya en lo que deja la 1: sin apetito, presupuesto de riesgo, plan de
contingencia y fecha de revisión registrados, los controles de la etapa no tienen contra qué comparar. El hilo que une
las dos clases es R-003: en la clase 1 se elige su contingencia entre cinco opciones y se escribe su plan; en la clase 2
el disparador llega y el plan se activa tal como está escrito.

Todas las cifras de este guion salen de la corrida de referencia (`docs/guias/evidencia/salida-g1.md`).

---

## Objetivos de aprendizaje

Al terminar las dos clases, cada asistente puede:

1. Explicar qué decide la junta antes del taller de riesgos: apetito, tolerancia, presupuesto de riesgo y quién puede
   gastar la reserva.
2. Identificar riesgos desde fuentes existentes (especificación, reuniones, tracker, artefactos) con cita de origen, y
   distinguir un riesgo de un issue.
3. Comparar las opciones de respuesta de un riesgo alto (evitar, reducir, transferir, contingencia, aceptar) por su
   valor neto, con el riesgo secundario en la cuenta, y justificar por escrito una elección distinta de la recomendada.
4. Escribir un plan de contingencia que se active sin improvisar: disparador, acciones, monto, fuente y quién lo autoriza.
5. Calcular un presupuesto de riesgo con fórmula (respuestas + EMV residual), separar la provisión para lo no
   identificado en la reserva de gestión y leer su consumo.
6. Reconocer las señales de un registro que se dejó de mirar (revisión vencida, acción vencida, disparador alcanzado,
   reserva sobre el 80 %), ordenar con el radar qué decidir primero y decir quién decide en cada caso.

## Requisitos previos

**Asistentes:** saber qué es un riesgo, una WBS y un presupuesto. No hace falta saber programar ni conocer BMAD.

**Instructor (antes de cada clase):**
- Claude Code con el plugin pm-method y una copia del fixture en `~/proyectos-prueba/portal-e2e-1`, según el
  [README de las guías](../../guias/README.md#cómo-usar-las-guías).
- La evidencia y las imágenes abiertas en pestañas: `salida-g1.md` y `docs/guias/img/g1-*.png` (plan B).
- Para la clase 1: el proyecto ya creado con los pasos 1 y 2 (se muestran con evidencia) y la transcripción de la ronda
  copiada en `gestion/03-control/reuniones/2026-10-27-ronda-riesgos-original.vtt`.
- Para la clase 2: un proyecto ya avanzado hasta el paso 11, preparado antes con los prompts de la guía en una copia
  nueva del fixture. Para mostrar archivos del recorrido completo, sirve la carpeta que deja el driver:
  `cd scripts/pruebas/guias_e2e && GUIAS_SALIDA=<dir> TMPDIR=<dir> python3 g1.py <dir>/salida-g1.md` (la ruta aparece al
  final como "Carpeta del recorrido").
- Probar el micrófono y el tamaño de letra de la terminal (mínimo 18 pt).

## El ejercicio

La hoja es una sola para asistentes e instructor: [ejercicio.md](ejercicio.md) (en HTML, `E2E-1-ejercicio.html`). Se
basta sola: empieza por «Cómo funciona este ejercicio», resume el escenario y los conceptos que hacen falta, trae la
hoja de trabajo con sus criterios de autoevaluación y termina con un **ejemplo resuelto** con el escenario del caso,
plegado, donde cada dato cita el paso de la guía de donde sale.

- **Cuándo:** la parte A en el minuto 75 de la clase 1 y la parte B en el minuto 75 de la clase 2, siempre después de
  la demostración; 10 minutos cada una.
- **Cómo se presenta:** proyectá la diapositiva del ejercicio y leé en voz alta «Cómo funciona este ejercicio» (un
  minuto). Quien no tenga un proyecto propio trabaja con los datos de partida del caso, que están en «Lo que necesitás
  saber».
- **Mientras trabajan:** pedí órdenes de magnitud, no precisión. Si alguien no tiene reserva de riesgo formal, que
  anote cuánto se gastó en respuestas a riesgos y de qué partida salió.
- **Ejemplo resuelto:** pedí que no lo abran antes de intentar. Mostralo recién en los dos últimos minutos del bloque:
  desplegalo en pantalla y comparalo con la hoja de uno o dos voluntarios. Al imprimir, sale desplegado al final de la
  hoja.
- **Autoevaluación:** cada asistente marca los criterios de su parte; un criterio sin cumplir es un hallazgo sobre su
  proyecto, no un error del ejercicio.

---

## Clase 1 · Del taller al plan de respuesta

**Pregunta de la clase:** ¿qué tiene que estar decidido para que un registro de riesgos sirva después del taller?

### Agenda minuto a minuto

| Minuto | Bloque | Qué pasa | Material |
|---|---|---|---|
| 0–10 | Gancho | "Para un proveedor que falla, la respuesta de manual es un SLA con penalidad. En este caso es la de menor valor neto de las cuatro." Pregunta a mano alzada (ver abajo). | Diapositivas de gancho |
| 10–25 | Concepto | Enfoque de riesgo: apetito, tolerancia, autoridad sobre la reserva y cadencia; P×I y EMV; riesgo frente a issue; opciones de respuesta y valor neto; plan de contingencia; presupuesto de riesgo y reserva de gestión. | Diapositivas de concepto |
| 25–65 | Demostración | Pasos 3, 4, 15, 5, 6a, 6b y 7 (detalle abajo). | Terminal + evidencia |
| 65–75 | Pregunta y discusión | "Para R-001, evitar deja el residual más bajo. ¿Por qué no es la recomendada?" | Diapositiva de pregunta |
| 75–85 | Ejercicio | Parte A: el enfoque y el presupuesto de riesgo de un proyecto propio; ejemplo resuelto al cerrar el bloque. | [ejercicio.md](ejercicio.md) · [cómo conducirlo](#el-ejercicio) |
| 85–90 | Cierre | Tres mensajes clave y anticipo de la clase 2. | Diapositiva de cierre |

### Demostración (40 minutos)

| Min | Paso | En vivo o con evidencia | Qué mostrar | Qué decir |
|---|---|---|---|---|
| 25–27 | 1–2 | Evidencia | Tolerancia `riesgo=ningún riesgo alto sin respuesta; exposición total ≤ USD 60.000`; "13 elementos, 8 hojas · esfuerzo 2480 h · costo 124,000" | "Los riesgos se identifican contra objetivos y productos, no en el vacío." |
| 27–33 | 3 | **En vivo** (prompt del paso 3) | Enfoque en `en-revision` v0.1; tras la respuesta, copias congeladas v1.0 y D-001, D-002 | "La ejecutiva decide antes del taller cuánto riesgo acepta y quién gasta la reserva." |
| 33–41 | 4 | **En vivo** el prompt de descubrimiento; evidencia para el taller | `bmad: 42 candidatos · 3 fuente(s)`, `transcripciones: 6 candidatos`; la cita «Nos preocupa que el padrón no tenga entorno de pruebas…» [00:00:13] | "Cada candidato trae de dónde sale. Ninguno entra al registro sin formularse." |
| 41–43 | 15 | Evidencia | `bmad: no aplica`; `artefactos: 7 candidatos · 5 fuente(s) leída(s)` | "Sin BMAD, las fuentes son el mandato, el brief, los requisitos y los supuestos." |
| 43–46 | 5 | Evidencia | Tabla P×I; `AVISO REG-06` para R-001 y R-003; exposición 53.600 | "Bajo la tolerancia de 60.000, pero dos altos sin respuesta ya incumplen la regla." |
| 46–55 | 6a | **En vivo** (prompt del paso 6a con la tabla de datos pegada debajo) | Plantillas de opciones; tabla con ★ O2 reducir (10.000) para R-001 y ★ O4 contingencia (2.500) para R-003; transferir de R-003 en 700; `g1-opciones-valor-neto.png`; `--elegir` con D-003 y D-004; `AVISO REG-10` | "El script hace la cuenta y marca la recomendada; decide el propietario. Y si elige contingencia, sin plan no hay contingencia." |
| 55–61 | 6b | **En vivo** el prompt del plan; evidencia para las demás respuestas | Plan de R-003 (disparador, acciones, USD 12.000, autoriza Laura); sanidad `0 ERROR · 0 AVISO`; costo 7.300 y EMV residual 32.500; `g1-mapa-inherente-residual.png` y `g1-exposicion-respuestas.png` | "El plan se escribe en frío para que el día del disparo nadie improvise." |
| 61–65 | 7 | Evidencia | 7.300 + 32.500 = 39.800 de presupuesto de riesgo y 6.200 de reserva de gestión aparte (`riesgo=39800 gestion=6200`); `INFO  CAM-03 Reserva de riesgo: 7.300 de 39.800 (18 %).`; `AVISO REG-07` A-002 y A-003 | "La reserva ya tiene dueño y tope, y la contingencia de R-003 ya está adentro, ponderada. Lo que nadie identificó no se mezcla: es de la junta." |

**Prompts exactos:** los de los pasos 3, 4 (descubrimiento), 6a (con la tabla «Datos de las opciones») y 6b (plan de
contingencia) de la guía, copiados tal cual. Si Claude pregunta, responder con el texto de "Si te pregunta" de cada paso.

### Mensajes clave

1. El **enfoque de riesgo** se aprueba antes del taller: sin apetito ni autoridad sobre la reserva, el registro no
   tiene reglas.
2. Una respuesta se **elige entre opciones**: el valor neto (reducción de EMV − costo − riesgo secundario) muestra cuál
   conviene; el script marca la recomendada y decide el propietario, por escrito.
3. Una contingencia **es un plan**, no una palabra: disparador, acciones, monto, fuente y quién la autoriza.
4. El **presupuesto de riesgo** sale de una fórmula y lo fija la junta; no es un porcentaje a ojo.

### Preguntas para la audiencia

| Pregunta | Respuesta esperada |
|---|---|
| "¿Cuántos tienen un registro de riesgos que se actualizó en las últimas dos semanas?" (gancho, mano alzada) | Pocas manos. El registro nace en el taller y se congela; es el problema de la clase 2. |
| "¿Quién decide cuánto riesgo acepta el proyecto?" | La junta, a través de la ejecutiva (apetito y tolerancia en el enfoque). El gestor propone. |
| "Para R-001, evitar deja el residual más bajo (P×I 3). ¿Por qué no es la recomendada?" | Cuesta USD 6.000 y crea un riesgo secundario sobre B-01 (EMV 6.000): valor neto 7.800 frente a 10.000 de reducir. El residual más bajo no es la mejor respuesta si cuesta más de lo que ahorra. |
| "Para R-003, el SLA con penalidad cuesta solo 2.500. ¿Por qué queda último?" | Baja la probabilidad, pero no el impacto: la penalidad (tope de USD 2.000 por mes) no cubre el atraso, y ese riesgo secundario (EMV 1.800) se descuenta. Valor neto 700. |
| "La contingencia de R-003 no cuesta nada hoy. ¿Por qué entra en el presupuesto de riesgo?" | Porque si el disparador llega se paga con la reserva: su EMV residual incluye la contingencia ponderada, 50 % × (8.000 + 12.000) = 10.000. |
| "R-006 explotar sube el EMV de 4.000 a 5.600. ¿Es un error?" | No: es una oportunidad; subir su valor esperado es el objetivo. |

### Dudas frecuentes

- **"¿El modelo calcula P×I y EMV?"** No: los calcula `registro.py` al registrar, y el valor neto de cada opción
  `riesgos.py opciones`; el modelo redacta y propone.
- **"¿El script elige la respuesta?"** No: marca la recomendada. Solo `--elegir` con `--por "<rol: nombre>"` registra la
  decisión (puerta humana), y si la elegida no es la recomendada exige `--motivo`.
- **"¿Hace falta evaluar opciones para todos los riesgos?"** Para los altos (P×I ≥ 15); la sanidad avisa con REG-10 si
  uno tiene menos de dos opciones evaluadas o una contingencia sin plan. Los demás se justifican con costo < ΔEMV.
- **"¿Necesito BMAD?"** No. El paso 15 muestra la identificación desde los artefactos del propio proyecto.
- **"¿Qué diferencia hay entre reserva de riesgo y reserva de gestión?"** La reserva de riesgo paga respuestas y
  contingencias de riesgos identificados; la provisión para riesgos no identificados va a la reserva de gestión, que solo
  libera la junta (paso 7: 39.800 y 6.200).
- **"¿Por qué aparece REG-07 en el paso 7 si las acciones ya se hicieron?"** Porque nadie las cerró: la sanidad mira el
  registro, no la memoria del equipo.

### Plan B si la demo en vivo falla

Seguir con la evidencia: abrir `salida-g1.md` en el bloque del paso y leer la línea de "Qué deberías ver" de la guía.
Para el paso 6a, la salida de `riesgos.py opciones` y `g1-opciones-valor-neto.png`; para el 6b, el texto del plan, el
bloque "justificación económica de cada respuesta" y las imágenes `g1-mapa-inherente-residual.png` y
`g1-exposicion-respuestas.png` cuentan el resultado completo. Nunca improvisar cifras: si una no está en la evidencia,
decir "lo verificamos después".

---

## Clase 2 · El control continuo

**Pregunta de la clase:** ¿qué pasa con el registro cuando el proyecto se pone difícil, y cómo nos enteramos a tiempo?

### Agenda minuto a minuto

| Minuto | Bloque | Qué pasa | Material |
|---|---|---|---|
| 0–10 | Gancho | "El 12/02, los 5 riesgos abiertos llevaban entre 17 y 45 días sin revisar. La sanidad lo avisaba desde el 12/01." Repaso en un minuto del presupuesto de 39.800 (con la reserva de gestión de 6.200 aparte) y del plan de contingencia de R-003. | Diapositivas de gancho y `g1-revisiones-vencidas.png` |
| 10–25 | Concepto | Revisión periódica, fecha de revisión y REG-09; el resumen y la línea de radar que pm-method muestra al abrir la sesión; disparador y plan de contingencia; riesgo que ocurre → issue; la reserva como presupuesto vivo (CAM-02, CAM-03); condiciones de la junta (EST-12). | Diapositivas de concepto |
| 25–65 | Demostración | Pasos 8 a 14 (detalle abajo). | Terminal + evidencia |
| 65–75 | Pregunta y discusión | "Con la reserva al 94 %, ¿qué harías en lugar de Laura?" | Diapositiva de pregunta |
| 75–85 | Ejercicio | Parte B: la revisión de riesgos de un proyecto propio; ejemplo resuelto al cerrar el bloque. | [ejercicio.md](ejercicio.md) · [cómo conducirlo](#el-ejercicio) |
| 85–90 | Cierre | Mensajes clave y puente a E2E-2. | Diapositiva de cierre |

### Demostración (40 minutos)

| Min | Paso | En vivo o con evidencia | Qué mostrar | Qué decir |
|---|---|---|---|---|
| 25–28 | 8 | Evidencia | R-002 de 12 a 8; `AVISO REG-07 Acción vencida A-001`; exposición 50.600; tablero `g1-tablero.png` con la revisión prevista 2026-12-29 | "La revisión deja fijado cuándo se vuelve a mirar cada riesgo; si esa fecha pasa, la sanidad lo marca (REG-09)." |
| 28–36 | 9 | **En vivo** el prompt de la reserva; evidencia para Jira | PS-101 y PS-102 como issues relacionados con R-001; C-002 es la opción O4 que se había evaluado; `AVISO CAM-02 … C-003`; 46 % → 38 % tras el rechazo | "Las licencias estaban dentro de la autoridad del gestor: el control mira el propósito, no el monto." |
| 36–43 | 10–11 | Evidencia | Opciones de R-007: ★ O3 contingencia (3.000) y O2 reducir (−2.000); `--elegir O2` sin `--motivo` no registra; con el motivo de Laura, D-016; hoja de riesgo; `AVISO EST-12`; los cuatro `AVISO REG-09` (revisión del 29/12 sin hacer); 64 %; informe al 15/01 | "La recomendación es una propuesta: la junta elige otra por apetito, y el sistema le pide que lo deje escrito." |
| 43–54 | 12 | Evidencia para el resumen y la línea de radar; **en vivo** el prompt "antes de tocar nada" y el del radar; evidencia para la revisión | Resumen al abrir la sesión (cinco riesgos con la revisión vencida, A-004 vencida, condición de la junta, próxima puerta) y radar `decidir 1 · escalar 0 · desbloquear 1 · vigilar 6`; `0 ERROR · 7 AVISO`; cinco REG-09 (45 y 17 días); R-003 sube a 20; exposición 54.600; radar después de la revisión: «Hoy: decidir R-003»; `g1-revisiones-vencidas.png` y `g1-exposicion-tendencia.png` | "El aviso estuvo un mes en pantalla y nadie miró R-003. Con la revisión hecha, el radar pone su contingencia primera." |
| 54–61 | 13 | **En vivo** (prompt del paso 13) | C-005 (12.000, como dice el plan), D-018 y A-005; `AVISO CAM-03 Reserva de riesgo al 94 % (37.300 de 39.800).`; remanente 2.500 frente a 27.900; reserva de gestión 6.200 sin uso; D-019; `g1-consumo-reserva.png` | "Nadie improvisa: monto, quién autoriza y cómo se registra estaban escritos desde el 4/11. Quedan 2.500 en la caja de riesgo; lo que pase de ahí va a la junta, dueña de la reserva de gestión." |
| 61–65 | 14 | Evidencia | Exposición 27.600; L-001 y L-002; D-020; puerta con 2 bloqueos y 0 condiciones; `g1-tarjetas-etapa.png` | "Seis indicadores para la junta: cinco en rango y la reserva en atención." |

**Prompts exactos:** el prompt de la reserva del paso 9, el primer prompt y el del radar del paso 12, y el del paso 13.
El prompt de revisión del paso 12 se lee en voz alta y se muestra su resultado en la evidencia, para no depender de una
ronda más en vivo.

### Mensajes clave

1. Un registro de riesgos vale lo que su **última revisión**: cada riesgo lleva la fecha en que se vuelve a mirar, y la
   sanidad avisa (REG-09) cuando pasa. El aviso sirve si la revisión del sprint empieza por él.
2. La reserva de riesgo es un **presupuesto vivo** de la junta: cada uso cita su riesgo (CAM-02) y el consumo avisa al
   80 % (CAM-03) antes de agotarse.
3. Un **plan de contingencia** convierte el disparador en una decisión de minutos; el **radar** dice que es lo primero.
4. Lo ocurrido es un **issue**, no un riesgo; lo que no se justifica por números lo decide la junta, con el motivo
   escrito. Sus condiciones **no dependen de la memoria**: la sanidad las recuerda hasta que se cumplen (EST-12).

### Preguntas para la audiencia

| Pregunta | Respuesta esperada |
|---|---|
| "El 12/02, ¿qué control avisó que nadie revisaba el registro? ¿Desde cuándo?" | REG-09, en cada sanidad desde el 12/01 (cuatro riesgos con la revisión del 29/12 vencida; el 12/02 eran cinco). El control funcionó; lo que faltó fue actuar. Por eso la lección L-002 pide empezar cada revisión de sprint por los REG-09. |
| "Martín aprobó las licencias dentro de su límite de USD 5.000. ¿Por qué estuvo mal?" | Porque no responden a ningún riesgo: la reserva de riesgo no es una bolsa general. Van al presupuesto de cambio. |
| "La junta eligió para R-007 una opción con valor neto negativo. ¿Estuvo mal?" | No necesariamente: el valor neto es solo económico, y el apetito en cumplimiento es bajo. Lo que importa es que el motivo quedó escrito (D-016): sin `--motivo`, el script no lo registraba. |
| "Con la reserva al 94 %, ¿qué harías en lugar de Laura?" | No hay una única respuesta. Laura mantuvo el tope, concentró la autoridad y lleva a la junta lo que supere el remanente (D-019); las alternativas registradas eran pedir a la junta que pase reserva de gestión al presupuesto de riesgo o pedir un plan de excepción. Lo importante es que la decisión quede escrita con sus opciones. |
| "¿Qué pasaría si un cambio más llevara la reserva al 105 %?" | CAM-03 pasaría a ERROR y la verificación de puertas lo trataría como bloqueo: la junta tendría que decidir antes de autorizar nada. |

### Dudas frecuentes

- **"¿La sanidad detecta un riesgo sin revisar?"** Sí: REG-09 marca cada riesgo abierto (`abierto`, `en-seguimiento`,
  `escalado`) cuya `fecha_revision` es anterior al corte. REG-07 hace lo mismo con las acciones vencidas.
- **"¿Qué ve Claude al abrir la sesión?"** El hook de inicio agrega el conteo de la sanidad rápida y un resumen derivado
  de `estado.json` y los registros (`estado.py contexto`): abiertos, riesgos con la revisión vencida (REG-09), issues,
  acciones vencidas, condiciones de la junta y próxima puerta, más una línea de radar con los totales de decidir,
  escalar, desbloquear y vigilar. Si una nota de memoria dice otra cosa, mandan los registros.
- **"¿El radar reemplaza a la sanidad?"** No: la reutiliza (junto con el resumen, las puertas y los presupuestos) y la
  ordena por prioridad, con responsable y siguiente paso. Es de solo lectura: no registra nada.
- **"¿Por qué R-001 sale de la exposición en el paso 9?"** Porque ocurrió: pasa a `ocurrido` y su efecto se gestiona como
  issue (I-001), pagado con la reserva (C-002).
- **"¿Qué es TOL-03 en la sanidad?"** Un INFO: la etapa de entrega no tiene corte de EVM guardado. Esta guía no vigila
  el EVM; lo hacen E2E-2 y E2E-3.
- **"¿Quién cierra la condición de la junta?"** La ejecutiva, con `estado.py cumplir-condiciones … --por … --fecha`
  (D-020). Hasta entonces aparece EST-12 en cada sanidad.

### Plan B si la demo en vivo falla

Usar la evidencia: los bloques de sanidad de los pasos 9, 10, 12 y 13 de `salida-g1.md`, las opciones de R-007 del
paso 10, el resumen `estado.py contexto`, el radar y el bloque "lista completa de REG-09" del paso 12, el plan de
contingencia del paso 6b y el bloque "gráficos de la etapa … datos". Las imágenes
`g1-revisiones-vencidas.png`, `g1-exposicion-tendencia.png`, `g1-consumo-reserva.png` y `g1-tarjetas-etapa.png` cuentan
la clase completa sin terminal.

---

## Conexión con el caso siguiente

Al cerrar la clase 2: "Las licencias de diseño no eran un riesgo, eran un cambio. En E2E-2 vamos a ver qué pasa con los
cambios: quién decide cada uno, contra qué presupuesto se cobran y qué ocurre cuando uno excede la autoridad delegada."
Enlace: [E2E-2 · Alcance y su cambio, estimación, priorización y mapa de ruta](../../guias/E2E-2-alcance-roadmap.md).
