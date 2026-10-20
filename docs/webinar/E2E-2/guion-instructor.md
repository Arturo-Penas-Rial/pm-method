# Guion del instructor · E2E-2 · Alcance, cambio y mapa de ruta

**Caso:** [Guía E2E-2](../../guias/E2E-2-alcance-roadmap.md) · **Evidencia:** [salida-g2.md](../../guias/evidencia/salida-g2.md)
· **Ejercicio:** [ejercicio.md](ejercicio.md) · **Diapositivas:** [diapositivas.json](diapositivas.json) (las arma el
generador común) · **Público:** gestores de proyecto con algo de PMBOK o PRINCE2 y líderes de negocio.

**Formato:** dos clases de 90 minutos. La primera construye la línea base contra la que se mide todo cambio (pasos 1 a
5); la segunda gestiona tres cambios de distinto tamaño, hasta la excepción (pasos 6 a 10). Se dividió así porque la
clase 2 necesita lo que deja la 1: sin presupuesto de cambio, límite delegado y tolerancias registrados, el análisis de
impacto no tiene contra qué compararse. Una sola clase obligaría a saltear el análisis de impacto o la excepción, que
son el foco del caso.

Todas las cifras de este guion salen de la corrida de referencia (`docs/guias/evidencia/salida-g2.md`).

---

## Objetivos de aprendizaje

Al terminar las dos clases, cada asistente puede:

1. Explicar por qué el alcance se define por productos y se mide contra criterios de calidad, y leer una cobertura de
   trazabilidad requisito → historia → paquete.
2. Leer un camino crítico y calcular una reserva de cronograma a 2σ con PERT.
3. Distinguir los tres caminos de un cambio: intercambio del product owner, decisión de la autoridad de cambio y
   excepción a la junta, y decir quién decide cada uno.
4. Armar una tabla de impacto de un cambio **antes** de decidirlo (tiempo, reserva, costo, presupuesto, autoridad,
   capacidad y VAN del business case).
5. Reconocer las señales de una excepción (aprobación rechazada por `registro.py` fuera de la autoridad, TOL-01) y recorrer su ruta: informe, plan de excepción con
   el business case y los riesgos actualizados, y puerta de la junta.

## Requisitos previos

**Asistentes:** saber qué es una WBS, un backlog y un presupuesto; no hace falta saber programar. Conviene haber visto
E2E-1 (riesgos), pero no es obligatorio.

**Instructor (antes de cada clase):**
- Claude Code con el plugin pm-method instalado y una copia del fixture en `~/proyectos-prueba/portal-e2e-2`, según el
  [README de las guías](../../guias/README.md#cómo-usar-las-guías).
- La evidencia y las imágenes abiertas en pestañas: `salida-g2.md` y `docs/guias/img/g2-*.png` (plan B).
- Para la clase 2: un proyecto ya avanzado hasta el paso 5, preparado antes de la clase con los prompts de los pasos 1
  a 5 en una copia nueva del fixture. Para mostrar archivos del recorrido completo, sirve la carpeta que deja el driver:
  `cd scripts/pruebas/guias_e2e && GUIAS_SALIDA=<dir> TMPDIR=<dir> python3 g2.py <dir>/salida-g2.md` (la ruta aparece al
  final como "Carpeta del recorrido").
- Probar el micrófono y el tamaño de letra de la terminal (mínimo 18 pt).

---

## Clase 1 · Del alcance a la línea base

**Pregunta de la clase:** ¿contra qué vamos a medir cada cambio?

### Agenda minuto a minuto

| Minuto | Bloque | Qué pasa | Material |
|---|---|---|---|
| 0–10 | Gancho | La historia de C-002 contada al revés: "el 19/2 llegó aprobado de palabra un cambio que llevaba el presupuesto de cambio al 200 %". Pregunta a mano alzada (ver abajo). | Diapositiva de gancho (el gráfico `g2-consumo-cambio.png` se reserva para la clase 2) |
| 10–25 | Concepto | Producto antes que tarea (PBS/WBS y descripción de producto); trazabilidad viva; PERT y camino crítico; MoSCoW como margen; línea base, tolerancia, autoridad de cambio, presupuesto de cambio y VAN del business case. | Diapositivas de concepto |
| 25–65 | Demostración | Pasos 1 a 5 (detalle abajo). | Terminal + evidencia |
| 65–75 | Pregunta y discusión | "¿Quién aprueba un cambio de 9.000? ¿Y uno de 15.000?" | Diapositiva de pregunta |
| 75–85 | Ejercicio | Parte A del ejercicio: la línea base de cambio de un proyecto propio. | [ejercicio.md](ejercicio.md) |
| 85–90 | Cierre | Tres mensajes clave y anticipo de la clase 2. | Diapositiva de cierre |

### Demostración (40 minutos)

| Min | Paso | En vivo o con evidencia | Qué mostrar | Qué decir |
|---|---|---|---|---|
| 25–29 | 1 | Evidencia | "requisitos: 42 · historias: 10", tres épicas | "pm-method no reescribe la especificación: la lee de BMAD." |
| 29–40 | 2 | **En vivo** (prompt del paso 2) | "13 elementos, 8 hojas · esfuerzo 2480 h · costo 124,000"; trazabilidad sin huecos; la cobertura (12 de 12) | Abrir `descripcion-producto-proyecto.md` y señalar CA-02 "p95 < 3 s". "Esto es lo que significa terminado." |
| 40–50 | 3 | **En vivo** (prompt del paso 3) | "Duración total (días laborables): 110 · Fin previsto: 2027-05-03"; σ = 6,51; reserva 13,0 días | Mostrar `g2-gantt.png`: "cinco barras naranjas mandan; A04 tiene 3 días de holgura". |
| 50–55 | 4 | Evidencia | Orden por valor/puntos; R1 47 de 48, R2 21 de 24 | "Should y Could son el margen del PO, no un premio consuelo." |
| 55–65 | 5 | **En vivo** (prompt del paso 5) | `estado.py presupuesto cambio=12000 limite_autoridad_cambio=10000`; business case con VAN 39.776 y B-01 con equilibrio en 76,8 %; verificación de autorizar-proyecto "1 bloqueo(s) · 0 condición(es) · 2 aviso(s)" (L-01, P-09, P-10); líneas base con sha | "Desde acá, cada cambio aprobado se compara solo contra estos números, y cada cambio recalcula el VAN." |

**Prompts exactos:** los de los pasos 2, 3 y 5 de la guía, copiados tal cual. Si Claude pregunta, responder con el texto
de "Si te pregunta" de cada paso.

### Mensajes clave

1. El alcance es una lista de **productos con criterios de aceptación**, no de tareas. Sin criterio, "terminado" se
   discute en la UAT.
2. La trazabilidad sirve si se **recalcula**: 12 de 12 hoy no garantiza nada mañana.
3. La línea base de cambio son **tres números** que fija la junta: tolerancias, límite por cambio y presupuesto de cambio.
   Al lado, el VAN del business case: la vara para saber si un cambio crea o destruye valor.

### Preguntas para la audiencia

| Pregunta | Respuesta esperada |
|---|---|
| "¿Cuántos tienen hoy una matriz de trazabilidad actualizada?" (gancho, mano alzada) | Pocas manos. Se arma una vez y se abandona; es el problema que resuelve el paso 8. |
| "La reserva a 2σ es de 13 días y la tolerancia de tiempo es de 15. ¿Cuánto puede absorber un cambio?" | La tolerancia admite hasta 15 días, pero la reserva cubre la incertidumbre de las estimaciones: un cambio que consume 11 días deja solo 2 de reserva. No es excepción, pero sí un riesgo. |
| "¿Quién aprueba un cambio de 9.000? ¿Y uno de 15.000?" | 9.000: la autoridad de cambio, si queda saldo en el presupuesto de cambio. 15.000: supera el límite de 10.000, así que decide la junta. |
| "¿Por qué la junta fija un presupuesto de cambio aparte de la reserva de riesgo?" | La reserva de riesgo paga respuestas a riesgos; los cambios de alcance tienen su propio presupuesto. Mezclarlos oculta cuánto se gastó en cada cosa. |
| "El VAN es 39.776. ¿Cuánto puede fallar el beneficio principal antes de que el proyecto deje de valer la pena?" | B-01 tiene su punto de equilibrio en 76,8 % de lo estimado: puede caer 23,2 %. Es más que su tolerancia de −10 %, así que el caso es robusto, pero depende sobre todo de ese beneficio. |

### Dudas frecuentes

- **"¿Tengo que usar BMAD?"** En este caso la especificación viene de BMAD y pm-method la lee sin escribirla. Las
  demás guías muestran el resto del ecosistema.
- **"¿Puedo exportar el cronograma a MS Project?"** Sí: `cpm.py … --mspdi cronograma.xml` (paso 3), que se abre en MS
  Project o ProjectLibre.
- **"¿De dónde salen los flujos del business case?"** Los montos los da la dueña de los beneficios y la tasa, la
  organización; `inversion.py` solo calcula VAN, TIR, repago, sensibilidad y punto de equilibrio. Si falta un dato,
  queda `[por confirmar]`.
- **"¿Quién escribe la WBS?"** La redacta la skill con lo que dice el equipo; los cálculos (horas, costo, BAC) los hace
  `wbs.py`.
- **"¿Por qué hay avisos P-09 y P-10 en la puerta de proyecto?"** Faltan la matriz poder/interés y la RACI; se trabajan
  en E2E-3.

### Plan B si la demo en vivo falla

Seguir con la evidencia: abrir `salida-g2.md` en el bloque del paso y leer la línea de "Qué deberías ver" de la guía.
Mostrar `g2-gantt.png` para el paso 3 y `g2-indicadores.png` para cerrar. Nunca improvisar cifras: si una no está en
la evidencia, decir "lo verificamos después".

---

## Clase 2 · El cambio bajo control

**Pregunta de la clase:** ¿quién decide cada cambio, y cómo nos enteramos a tiempo?

### Agenda minuto a minuto

| Minuto | Bloque | Qué pasa | Material |
|---|---|---|---|
| 0–10 | Gancho | Mostrar `g2-consumo-cambio.png` sin título: "una barra roja al 200 %. ¿Quién lo quiso aprobar? ¿Por qué no llegó a consumirse?" Repaso en un minuto de los tres números de la clase 1. | Diapositivas de gancho |
| 10–25 | Concepto | Tres caminos de un cambio; tabla de impacto en todos los objetivos, incluido el VAN; EVM ágil (alcance que no entra, no sobrecosto); gestión por excepción. | Diapositivas de concepto |
| 25–65 | Demostración | Pasos 6 a 10 (detalle abajo). | Terminal + evidencia |
| 65–75 | Pregunta y discusión | "Sofía aprobó C-002 porque era obligatorio. ¿Estuvo mal?" | Diapositiva de pregunta |
| 75–85 | Ejercicio | Parte B del ejercicio: la tabla de impacto de un cambio real. | [ejercicio.md](ejercicio.md) |
| 85–90 | Cierre | Mensajes clave y puente a E2E-3. | Diapositiva de cierre |

### Demostración (40 minutos)

| Min | Paso | En vivo o con evidencia | Qué mostrar | Qué decir |
|---|---|---|---|---|
| 25–29 | 6 | Evidencia | **D-009**, nivel `product-owner`, sin solicitud de cambio | "Primer camino: lo decide el PO porque no toca Must, fecha ni costo." |
| 29–42 | 7 | **En vivo** (prompt del paso 7) | "agregados ['FR-13']"; escenario "121 · 2027-05-18"; VAN 39.776 → 45.939; la tabla de impacto; "INFO CAM-03 Presupuesto de cambio: 9.000 de 12.000 (75 %)" | Recorrer la tabla fila por fila. Mostrar `g2-roadmap-c001.png`: "el Release 1 no se mueve; la puesta en producción, 11 días; y el simulador se paga solo". |
| 42–47 | 8 | Evidencia | "Sin desvíos"; líneas base 1.1; cobertura 13 de 13 | Mostrar `g2-trazabilidad.png`: "la matriz se rehízo sola tras el cambio". |
| 47–52 | 9 | Evidencia | `alcance_no_entregable_pct 10.345`, ámbar; TOL-02; SPI 0,867 activa el disparador de R-001; Q-001 sin QUA-01 | "Ámbar: el PO saca Should/Could, que es justo la respuesta prevista en R-001; nadie escala todavía." |
| 52–65 | 10 | **En vivo** el prompt 1; evidencia para los prompts 2 y 3 | `registro.py` rechaza la aprobación de Sofía ("supera el límite de la autoridad de cambio (10.000)", "24.000 de 12.000 fijados por la junta") y C-002 queda `pendiente-decision`; sanidad "0 ERROR · 1 AVISO · 1 INFO" (TOL-01, CAM-03 al 75 %); tabla de impacto de C-002 con VAN 30.939; puerta "1 bloqueo(s)" (L-01); la junta amplía el presupuesto a 32.000 y recién entonces aprueba C-002; REG-09 de R-001 el 26/2 y su revisión; sanidad final "24.000 de 32.000 (75 %)" | Mostrar `g2-alcance-evm.png`, `g2-consumo-cambio.png` y `g2-business-case.png`. "La aprobación fuera de la autoridad se frenó el mismo día, el cambio esperó a la junta, y la junta decidió sabiendo que el proyecto sigue valiendo la pena." |

**Prompts exactos:** los de los pasos 7 y 10 (prompt 1) de la guía. Los prompts 2 y 3 del paso 10 se leen en voz alta y
se muestra su resultado en la evidencia, para no depender de dos rondas más en vivo.

### Mensajes clave

1. Un cambio tiene **tres caminos** y cada uno tiene dueño: PO (intercambio), autoridad de cambio (dentro del límite y
   del saldo) y junta (excepción).
2. El impacto se calcula **antes** de decidir y en **todos** los objetivos, no solo en el costo: también en el VAN.
3. "Obligatorio" responde si hay que hacerlo, no quién lo decide.
4. La excepción no es un fracaso: es la ruta prevista, y con pm-method empieza el mismo día del desvío. Llega a la
   junta con el business case recalculado y, si un riesgo queda sin revisar, REG-09 lo recuerda.

### Preguntas para la audiencia

| Pregunta | Respuesta esperada |
|---|---|
| "C-001 corre 11 días la puesta en producción. ¿Es una excepción?" | No: 11 de 15 días de tolerancia (73 %). Pero deja la reserva en 2,0 días, y por eso se registra R-001 antes de aprobar. |
| "Sofía aprobó C-002 porque era obligatorio. ¿Estuvo mal?" | La necesidad no se discute; la autoridad sí. 15.000 supera su límite de 10.000 y el presupuesto quedaría al 200 %: debía escalar a la junta. Por eso `registro.py` no registra su aprobación y C-002 queda `pendiente-decision`. |
| "¿Por qué el EVM ágil habla de alcance y no de sobrecosto?" | Con costo y fecha fijos, un EAC mayor que el BAC significa que no entra todo el alcance. Si lo que no entra cabe en Should/Could (10,3 % < 20 %), decide el PO; si no (22,1 %), los Must peligran y hay excepción. |
| "C-002 resta 15.000 de VAN y no suma beneficio. ¿Sigue valiendo la pena el proyecto?" | Sí: el VAN queda en 30.939 y B-01 puede caer 18 % antes de llegar a 0, más que su tolerancia de −10 %. Con menos margen: la junta lo sabe antes de aprobar el plan de excepción. |
| "Tras C-002, ¿qué pasa con la fecha de fin del proyecto?" | La recalcula el plan de proyecto junto con el plan de excepción (lo pide `limite-etapa`). La guía no la recalcula. Si quedara fuera de ±3 semanas, la junta tampoco podría aprobarla sola. |

### Dudas frecuentes

- **"¿El intercambio del PO no debería ser una solicitud de cambio?"** No, si cambia Should/Could equivalentes sin tocar
  Must, fecha ni costo: queda como decisión de nivel `product-owner` (D-009) y se avisa a BMAD.
- **"¿Puedo pagar un cambio con la reserva de riesgo?"** Solo si responde a un riesgo registrado; si no cita un R-###,
  sanidad avisa con CAM-02.
- **"¿Y si la junta necesita aprobar igual una puerta con un ERROR?"** La verificación lo indica: "corregir, o decisión
  'condicionado' (o --forzar) de la junta". En el caso, la junta corrige (amplía el presupuesto) y después aprueba.
- **"¿Por qué aparece REG-09 al final si todo se aprobó?"** `limite-etapa` pide actualizar plan, business case y
  riesgos. El business case se actualizó; R-001, con revisión prevista el 19/2, quedó sin mirar en medio de la
  excepción. Sanidad lo marca el 26/2 y el gestor lo revisa ese día (probabilidad 3 → 4, próxima revisión el 19/3).
- **"¿Qué pasa si BMAD cambia el PRD sin avisar?"** `bmad.py verificar` lo detecta como desvío contra la línea base. Sin un
  issue que lo cite, sanidad lo marca como ERROR ESP-10 ("Cambio no controlado"), que bloquea las puertas; con el issue
  baja a aviso hasta la nueva línea base.

### Plan B si la demo en vivo falla

Usar la evidencia: los bloques "análisis de impacto de C-001" y "análisis de impacto de C-002" de `salida-g2.md`, y la
salida de sanidad del 19/2. Las imágenes `g2-roadmap-c001.png`, `g2-trazabilidad.png`, `g2-alcance-evm.png`,
`g2-consumo-cambio.png` y `g2-business-case.png` cuentan la clase completa sin terminal.

---

## Conexión con el caso siguiente

Al cerrar la clase 2: "Todo lo que vimos lo decidieron la junta, la PO y el equipo. Falta el resto: socios,
operadores, cumplimiento, el Consejo. En E2E-3 vamos a ver quiénes son, qué quieren saber, cómo se les cuenta el avance
y cómo se verifica que el contacto prometido se cumple." Enlace: [E2E-3 · Interesados, comunicaciones, OKR y reporte de
avance](../../guias/E2E-3-interesados-okr-avance.md).
