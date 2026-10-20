# Guía E2E-2 · Alcance y su cambio, estimación de esfuerzo, priorización y mapa de ruta

**Qué vas a probar:** cómo se define el alcance por productos, se traza a los requisitos de BMAD, se estima y se
programa, se prioriza contra la capacidad del equipo y se fija como línea base con tolerancias, una autoridad de
cambio con presupuesto propio y un business case con su VAN. Después, cómo se gestionan tres tipos de cambio: el
**intercambio** que decide el product owner, el **cambio de alcance** que decide la autoridad de cambio dentro de su
límite y el cambio que **excede la autoridad delegada**, que se gestiona por excepción.

**Skills y agentes:** pm-orquestador · pm-planificacion → `pm-planificacion-por-productos`,
`pm-cronograma-estimacion`, `pm-costos-presupuesto`, `pm-agil-hibrido`, `pm-enfoques-gestion`, `pm-plan-etapa-y-limites`
· pm-control → `pm-issues-cambios`, `pm-riesgos`, `pm-progreso-reportes`, `pm-calidad` · pm-inicio → `pm-caso-de-negocio` ·
`pm-bmad-puente` · `pm-visuales` · `pm-director` (`pm-direccion-decisiones`).

**Duración:** 10 pasos, 85–115 minutos de recorrido; en el webinar, dos clases de 90 minutos.
**Preparación:** [README de las guías](README.md#cómo-usar-las-guías) (copia del fixture en
`~/proyectos-prueba/portal-e2e-2`). **Evidencia de referencia:** [salida-g2.md](evidencia/salida-g2.md). **Material de
clase:** [guion](../webinar/E2E-2/guion-instructor.md) · [ejercicio](../webinar/E2E-2/ejercicio.md) ·
[diapositivas](../webinar/E2E-2/diapositivas.json). **Términos:** [TERMINOLOGIA.md](../TERMINOLOGIA.md).

---

## Por qué importa

En la mayoría de los proyectos el alcance se define bien una vez y se controla mal después. La matriz de trazabilidad
se arma en la planificación y se desactualiza con el primer cambio. Los cambios se aprueban "porque son razonables" u
"obligatorios", sin mirar qué le hacen al camino crítico, a la capacidad del equipo, al presupuesto ni al business case.
Y nadie suma lo que ya se comprometió: el desvío aparece al cerrar la etapa, cuando ya no quedan opciones baratas.

El escenario de esta guía lo muestra con cifras. Un cambio razonable (C-001, 9.000) corre 11 días la puesta en
producción y deja la reserva de cronograma en 2 días, aunque suma valor: el VAN pasa de 39.776 a 45.939. Un segundo
cambio "obligatorio" (C-002, 15.000) llega aprobado de palabra, sin análisis, por quien tenía un límite de 10.000:
llevaría el presupuesto de cambio al 200 % y resta 15.000 de VAN. Con pm-method esa aprobación **no se puede
registrar**: el cambio queda pendiente de la junta el mismo día, con el impacto calculado y una ruta de decisión.

## Qué vas a lograr

1. Un alcance por productos con criterios de calidad medibles, trazado a requisitos e historias, y una cobertura de
   trazabilidad que se **recalcula en cada sincronización** con BMAD.
2. Un cronograma con camino crítico y reserva calculados por script, y un backlog priorizado que entra en la capacidad.
3. Una línea base con tolerancias, autoridad de cambio, **presupuesto de cambio** y business case registrados, que
   sanidad vigila.
4. Un **análisis de impacto antes de cada decisión**: tiempo, reserva, costo, presupuesto, autoridad, capacidad y VAN.
5. Una **excepción completa**: detectada el mismo día, informada, replanificada con el business case actualizado y
   autorizada por la junta.

## Indicadores que vas a ver

![Tarjetas de indicadores del caso](img/g2-indicadores.png)
Resumen al 26/2: VAN de 30.939 con los dos cambios, puesta en producción el 18/5, 2 días de reserva, presupuesto de
cambio al 75 % tras la ampliación, 22,1 % del alcance en riesgo en el corte del 19/2 y 13 de 13 requisitos trazados.

![Consumo del presupuesto de cambio en tres cortes](img/g2-consumo-cambio.png)
El presupuesto de cambio queda en 75 % tras C-001; con C-002 llegaría al 200 %, por eso C-002 espera a la junta, que
amplía el presupuesto y lo aprueba: vuelve a 75 % (paso 10).

![Alcance que no entra frente al margen de Should/Could](img/g2-alcance-evm.png)
El 29/1 no entra el 10,3 % del alcance (ámbar, lo gestiona el PO); el 19/2 no entra el 22,1 %, más que el 20 % de
margen: los Must peligran y hay excepción (pasos 9 y 10).

![VAN del business case en cada escenario](img/g2-business-case.png)
C-001 suma 6.163 de VAN y C-002 resta 15.000; con los dos, el VAN sigue en 30.939 y el beneficio principal puede caer
18 % antes de llegar a 0 (pasos 5, 7 y 10).

## Clases

| Clase (90 min) | Pasos | Pregunta que responde |
|---|---|---|
| **1 · Del alcance a la línea base** | 1 a 5: alcance por productos, trazabilidad, PERT y camino crítico, MoSCoW y capacidad, presupuesto, business case, tolerancias y autoridad de cambio | ¿Contra qué vamos a medir cada cambio? |
| **2 · El cambio bajo control** | 6 a 10: intercambio del PO, cambio con análisis de impacto, nuevas líneas base y trazabilidad, EVM guardado, excepción | ¿Quién decide cada cambio y cómo nos enteramos a tiempo? |

Son dos clases porque la segunda solo tiene sentido con la línea base de la primera: sin presupuesto de cambio, límite
delegado, tolerancias y VAN registrados, no hay contra qué medir el impacto. El guion las detalla minuto a minuto.

## Del uso único al control continuo

| Actividad | Cómo se hace hoy | Con pm-method (frecuencia · control) | Indicador |
|---|---|---|---|
| Trazabilidad requisito → historia → paquete | Una matriz armada una vez, que se desactualiza con el primer cambio | Se recalcula en cada sincronización con BMAD (pasos 2 y 8) · `bmad.py trazabilidad`, ESP-03 | Cobertura: 13 de 13 requisitos con historia y paquete |
| Detectar cambios en la especificación | Se descubren en la demo o en la UAT | `bmad.py verificar` contra la línea base en cada sincronización · ESP-10 | FR-13 detectado como desvío (paso 7) |
| Análisis de impacto de un cambio | A ojo, o nunca si "es obligatorio" | Tabla de impacto antes de decidir: escenario de `cpm.py`, capacidad, presupuesto, autoridad y VAN (pasos 7 y 10) | +11 días de camino crítico; 200 % del presupuesto |
| Justificación del negocio | El VAN se calcula una vez, para aprobar el proyecto | VAN antes y después de cada cambio con `inversion.py`; la junta lo revisa en la puerta del plan de excepción (pasos 5, 7 y 10) | VAN 39.776 → 45.939 → 30.939 |
| Consumo del presupuesto de cambio | Nadie lo suma hasta el cierre de la etapa | Al registrar cada aprobación (`registro.py` no la acepta sin saldo) y en cada corrida de sanidad · CAM-03: INFO < 80 %, AVISO ≥ 80 %, ERROR > 100 % | 75 % → 75 % (con C-002 sería 200 %) → 75 % |
| Respetar la autoridad delegada | Se "aprueba lo razonable", sin tope escrito | Límite en `estado.json`: `registro.py` rechaza la aprobación de quien no tiene autoridad; CAM-04 vigila los datos anteriores al límite | C-002: 15.000 sobre un límite de 10.000, no registrado como aprobado |
| Cargar cada cambio a un presupuesto | Se paga "con la contingencia" | Monto y cargo obligatorios en `cambios.csv` · CAM-01 | Cambios aprobados sin cargo: 0 |
| Pronóstico contra tolerancia | EVM en una planilla, mirado al fin de la etapa | Corte guardado en cada período · TOL-03, TOL-02, TOL-01 | Alcance que no entra: 10,3 % → 22,1 % |
| Gestión por excepción | Se explica el desvío al cierre | Informe, plan de excepción y puerta; la puerta queda bloqueada mientras haya un ERROR · bloqueo por sanidad, X-01, X-02 | `autorizar-plan-excepcion` aprobada el 26/2 |
| Revisar los riesgos que deja un cambio | Se registran al aprobar y no se vuelven a mirar | Fecha de revisión de cada riesgo abierto comparada con el corte · REG-09 | R-001 con revisión vencida el 26/2, revisada ese día |
| Calidad de lo terminado | Se discute en la UAT | Sanidad a volumen sobre `backlog.csv` · QUA-01 | Historias terminadas sin revisión: 0 |
| Traspasos a BMAD | Se pierden en el correo | Aviso hasta que el equipo marca `aplicado` · ESP-13 | Traspaso de C-002 sin confirmar al 26/2 |

En esta guía, sanidad corre con `--corte` en la fecha de cada paso, así el resultado es reproducible. En uso real,
pm-control la corre con la fecha de cada checkpoint y highlight, junto con el corte de EVM.

```mermaid
flowchart TB
    subgraph c1["Clase 1 · del alcance a la línea base"]
        a["1 · Proyecto y<br/>enunciado de alcance"] --> b["2 · PBS, WBS, descripciones<br/>de producto y trazabilidad"]
        b --> c["3 · PERT, camino crítico<br/>y reserva"] --> d["4 · MoSCoW, valor<br/>y capacidad"]
        d --> e["5 · Presupuesto, business case,<br/>tolerancias, autoridad y línea base"]
    end
    subgraph c2["Clase 2 · el cambio bajo control"]
        f["6 · Intercambio del PO<br/>sin solicitud de cambio"] --> g["7 · Cambio de alcance:<br/>impacto, VAN y decisión"]
        g --> h["8 · BMAD aplica, líneas base<br/>y trazabilidad recalculada"]
        h --> i["9 · EVM ágil guardado<br/>y calidad de lo terminado"]
        i --> j["10 · Excepción: impacto, informe,<br/>plan, business case y puerta"]
    end
    e --> f
```

---

## Paso 1 · Proyecto, especificación y enunciado de alcance

**Prompt**
```text
Creá el proyecto "Portal de autoservicio para socios" en ./gestion, español, híbrido. Ejecutiva Laura Méndez, gestor
Martín Suárez, usuaria sénior, PO y autoridad de cambio Sofía Ramírez, proveedor sénior Diego Ferreira, aseguramiento
Andrea Costa, jefa de equipo Lucía Benítez. Sprints de 14 días y velocidad de referencia de 8 puntos.
Mostrame qué especificó el equipo de producto en BMAD y armá el enunciado de alcance y el plan de gestión del alcance y
los requisitos.
```

**Si te pregunta:** nada; los roles y la cadencia están en el prompt.

**Qué hace el sistema:** `pm-nuevo` y `bmad.py detectar`; lee la especificación por la fachada (`especificacion.py
resumen`, `listar epicas`). `pm-planificacion-por-productos` redacta el enunciado de alcance (el **qué**) y
`pm-enfoques-gestion`, el plan de gestión del alcance y los requisitos (el **cómo**).

**Qué deberías ver:** "requisitos: 42 · historias: 10" y tres épicas: E-1 acceso seguro y consulta, E-2 solicitudes del
socio, E-3 consola de operador.

**Dónde verificar:** `gestion/01-inicio/enunciado-alcance.md` · `gestion/02-planificacion/enfoques/plan-gestion-alcance-requisitos.md`.

---

## Paso 2 · Productos (PBS), descripciones de producto y WBS trazada a requisitos e historias

La **PBS** (estructura de productos, *product breakdown structure*) descompone lo que se entrega; la **WBS** (estructura
de desglose del trabajo) le agrega el trabajo y el costo de cada paquete. Una **descripción de producto** (*product
description*) fija qué significa "terminado" para cada producto, con medidas y quién acepta.

**Prompt**
```text
Armá la WBS por productos con estos paquetes y su referencia a la especificación (USD 50 la hora):
1.1 Gestión de etapas 400 h · 2.1 Brief, PRD, UX y arquitectura (BMAD) 240 h (UJ-1, UJ-2, UJ-3)
· 3.1 Acceso seguro 420 h (FR-1, FR-2, FR-11, historias 1.1 y 1.2) · 3.2 Consulta y constancias 380 h (FR-3, FR-4, FR-5,
historias 1.3 y 1.4) · 3.3 Solicitudes del socio 440 h (FR-6, FR-7, FR-8, FR-12, historias 2.1 a 2.3)
· 4.1 Bandeja y resolución 400 h (FR-9, FR-10, historias 3.1 a 3.3) · 5.1 UAT, prueba de carga y capacitación 200 h
(NFR-2, NFR-3) · 5.2 Puesta en producción (hito).
Generá el diagrama, el diccionario y la matriz de trazabilidad, y decime si queda algún requisito sin cubrir.
Escribí también la descripción del producto del proyecto con los criterios de aceptación priorizados y la descripción
de producto del 3.1 Acceso seguro con sus especificaciones de calidad, métodos de calidad y quién acepta.
```

**Si te pregunta** por los criterios de calidad: Sofía Ramírez, usuaria sénior, responde: "consultas con p95 menor a
3 s (NFR-3), disponibilidad de 99,5 % (NFR-2), WCAG 2.1 AA (NFR-4); en el acceso, sesión que expira a los 10 minutos,
auditoría de todos los accesos (NFR-5) y cero vulnerabilidades altas en la prueba de penetración. Acepto yo".

**Qué hace el sistema:**
- `pm-planificacion-por-productos` escribe `wbs.csv` (columna `ref` con ids de BMAD) y corre `wbs.py … --mermaid …
  --diccionario …`.
- `pm-bmad-puente` corre `bmad.py trazabilidad --wbs 02-planificacion/wbs.csv` y `especificacion.py listar requisitos
  --cobertura sin-cobertura`.
- Redacta con sus plantillas la descripción del producto del proyecto (criterios CA-01 a CA-04 con prioridad, método y
  responsable) y la descripción de producto 3.1 (especificaciones EC-01 a EC-05 con medida y tolerancia de calidad).
  Las registra con `estado.py artefacto` en estado `en-revision`: las aprueba la usuaria sénior con el plan.
- Calcula la cobertura de trazabilidad y corre `sanidad.py --rapido --corte 2026-11-13`.

**Qué deberías ver:**
- "13 elementos, 8 hojas · esfuerzo 2480 h · costo 124,000".
- Trazabilidad: "Requisitos funcionales sin historia: ninguno · Historias sin requisito: ninguna · Referencias de la WBS a
  ids inexistentes: ninguna"; ningún requisito sin cobertura.
- Cobertura: 12 de 12 requisitos funcionales con historia y con paquete de la WBS; 6 de 6 NFR con paquete o criterio de
  calidad; 0 de 12 citados en su propia historia (BMAD los traza a nivel de épica).
- Sanidad "0 ERROR · 0 AVISO · 0 INFO".

> **Por qué importa.** Sin descripciones de producto, "terminado" significa lo que cada uno cree y la calidad se discute
> en la UAT. Con criterios medibles por producto, cada revisión de calidad (paso 9) se registra contra una
> especificación concreta, y sanidad la vigila a volumen (QUA-01).

**Dónde verificar:** `02-planificacion/wbs.csv` · `02-planificacion/visuales/wbs.md` (diagrama) ·
`02-planificacion/diccionario-wbs.md` · `02-planificacion/especificacion/matriz-trazabilidad-bmad.csv` ·
`02-planificacion/descripcion-producto-proyecto.md` · `02-planificacion/productos/3.1-acceso-seguro.md`.

---

## Paso 3 · Estimación de esfuerzo (PERT), camino crítico y reserva de cronograma

**PERT de tres puntos:** para cada actividad se estiman los días optimista (O), más probable (M) y pesimista (P); la
duración esperada es tE = (O + 4M + P)/6 y la desviación, σ = (P − O)/6. El **camino crítico** es la cadena de
actividades sin holgura: si una se atrasa, se atrasa el fin. La **reserva de cronograma** a 2σ cubre la incertidumbre de
ese camino.

**Prompt**
```text
Estimá con PERT de tres puntos las actividades y armá el cronograma con camino crítico desde el 30/11, con exportación a
MS Project. Lucía va a validar los valores. Calculá la reserva de cronograma a 2σ del camino crítico.
```

**Si te pregunta** por O, M y P (días): Lucía Benítez, jefa de equipo, responde:

| Actividad | O | M | P | Predecesoras |
|---|---|---|---|---|
| A01 Brief, PRD, UX y arquitectura | 8 | 10 | 15 | — |
| A02 Spike de integración con el núcleo | 5 | 8 | 14 | — |
| A03 Sprints acceso seguro | 20 | 28 | 40 | A01 |
| A04 Sprints consulta y constancias | 18 | 25 | 38 | A02, A03 |
| A05 Sprints consola de operador | 20 | 28 | 42 | A03 |
| A06 Release 1 aceptada (hito) | 0 | 0 | 0 | A04, A05 |
| A07 Sprints solicitudes del socio | 22 | 30 | 45 | A06 |
| A08 UAT, prueba de carga y capacitación | 8 | 10 | 16 | A07 |
| A09 Puesta en producción (hito) | 0 | 0 | 0 | A08 |

**Qué hace el sistema:** `pm-cronograma-estimacion` calcula tE y σ en `estimacion-pert.csv`, escribe `actividades.csv`
con tE redondeado, corre `cpm.py … --inicio 2026-11-30 --mermaid … --mspdi cronograma.xml --wbs wbs.csv` y calcula la
reserva: σ del camino crítico = √Σσ² de sus actividades.

**Qué deberías ver:**
- "Duración total (días laborables): 110 · Fin previsto: 2027-05-03 · Camino crítico: A01 -> A03 -> A05 -> A06 -> A07 ->
  A08 -> A09"; A04 con 3 días de holgura y A02 con 34.
- "σ = √(1,17² + 3,33² + 3,67² + 3,83² + 1,33²) = 6,51 días · Reserva a 2σ = 13,0 días laborables", dentro de la
  tolerancia de ±3 semanas (15 días laborables) que la junta fija en el paso 5.

![Gantt de la línea base con el camino crítico](img/g2-gantt.png)
Cinco actividades sin holgura (naranja) fijan el fin del 3/5/2027; A04 y A02 pueden moverse sin atrasarlo.

**Dónde verificar:** `02-planificacion/estimacion-pert.csv` · `02-planificacion/cronograma.md` (Gantt) ·
`02-planificacion/cronograma.xml` (abrilo en MS Project o ProjectLibre).

---

## Paso 4 · Priorización del backlog: MoSCoW, valor y esfuerzo

**MoSCoW** clasifica cada historia en Must (sin ella no hay producto), Should, Could y Won't. En un proyecto de costo y
fecha fijos, Should y Could son el margen que el PO puede mover sin pedir permiso.

**Prompt**
```text
Sincronizá el backlog con BMAD y priorizalo con MoSCoW y valor/esfuerzo. Sofía, como PO, da el valor (1-10) y el equipo
los puntos. Ordená: primero MoSCoW y dentro de cada grupo por valor/puntos. Repartí en dos releases (R1: sprints 1-6;
R2: sprints 7-9) y verificá que los Must y Should entran en la capacidad.
```

**Si te pregunta** valores y puntos: Sofía Ramírez (PO) y Lucía Benítez (equipo) responden:

| Historia | MoSCoW | Valor | Puntos |
|---|---|---|---|
| 1.1 Alta y acceso con segundo factor | Must | 9 | 8 |
| 1.2 Recuperación de acceso | Must | 6 | 5 |
| 1.3 Consulta de saldos y préstamos | Must | 10 | 8 |
| 1.4 Constancias en PDF | Should | 7 | 5 |
| 2.1 Solicitud guiada de préstamo | Must | 9 | 8 |
| 2.2 Seguimiento de solicitudes | Should | 6 | 8 |
| 2.3 Actualización de contacto | Could | 4 | 5 |
| 3.1 Acceso y roles de la consola | Must | 6 | 5 |
| 3.2 Bandeja única | Must | 8 | 8 |
| 3.3 Resolución de solicitudes | Must | 8 | 8 |

**Qué hace el sistema:** `bmad.py backlog` crea `backlog.csv` con las columnas **derivadas** de BMAD; `pm-agil-hibrido`
completa solo las columnas de **gobierno** (`prioridad`, `moscow`, `estimacion`, `iteracion`, `release`, `producto_pbs`),
que el puente nunca sobrescribe; vuelve a correr `bmad.py backlog` ("0 nuevas, 10 actualizadas").

**Qué deberías ver:** orden 1.3 (1,25) · 1.2 (1,20) · 3.1 (1,20) · 1.1 (1,12) · 2.1 (1,12) · 3.2 (1,00) · 3.3 (1,00)
· 1.4 Should · 2.2 Should · 2.3 Could. Capacidad: **R1** 6 sprints × 8 = 48 puntos para Must 42 + Should 5 = 47;
**R2** 3 sprints × 8 = 24 para Must 8 + Should 8 + Could 5 = 21.

**Dónde verificar:** `02-planificacion/backlog.csv` (abrilo en Excel) · prompt: "Mostrame el backlog ordenado con
MoSCoW, puntos y release".

---

## Paso 5 · Presupuesto, business case, tolerancias, autoridad de cambio, roadmap y línea base

La **línea base** es la versión aprobada contra la que se mide todo cambio. La **tolerancia** (*tolerance*) es el
desvío que cada nivel puede absorber sin escalar. La **autoridad de cambio** (*change authority*) decide cambios
dentro de un **límite por cambio** y de un **presupuesto de cambio** (*change budget*) que fija la junta. El **business
case** justifica la inversión; su **VAN** (valor actual neto, *net present value*) suma los flujos de cada año
descontados a la tasa de la organización: si es positivo, el proyecto crea valor.

**Prompt**
```text
Calculá el presupuesto desde la WBS, armá el release plan y el roadmap por etapas con las puertas, y preparame las
puertas de inicio, proyecto y etapa 2. Antes de la de proyecto: documentá las tolerancias y la autoridad delegada
(Sofía decide cambios de hasta 10.000 cada uno, con un presupuesto de cambio de 12.000 que fija la junta), el enfoque
de beneficios (B-01 a B-03, quién los mide y cuándo) y el business case con su VAN a 5 años. En la de proyecto fijá la
línea base del PRD y de las épicas, y que Sofía apruebe el backlog como línea base.
```

**Si te pregunta:**
- Por los flujos del business case: Sofía Ramírez, dueña de los beneficios, y Laura Méndez, ejecutiva, responden con
  la tasa de 10 % anual que usa la cooperativa:

| Concepto | Año 0 | Años 1 a 5 |
|---|---|---|
| Proyecto (BAC de la WBS) | −124.000 | — |
| Operación y soporte | — | −22.000 por año |
| B-01 Desvío de consultas | — | 30.000 el año 1 y 50.000 por año del 2 al 5 |
| B-03 Eficiencia de préstamos | — | 20.000 por año |

- Por las decisiones: "Laura Méndez, ejecutiva: apruebo las tolerancias, el presupuesto de cambio de 12.000 y el
  límite de 10.000 por cambio para la autoridad de cambio; aprobado, confirmo las listas de control" · "Sofía Ramírez,
  PO: apruebo el backlog v1.0".

**Qué hace el sistema:**
- `pm-costos-presupuesto` calcula el BAC (presupuesto a la conclusión) con `wbs.py --json`: 124.000.
- `pm-caso-de-negocio` escribe `00-direccion/flujos-business-case.csv` y corre `inversion.py … --tasa 0.1 --variacion
  0.1` (VAN, TIR, repago y sensibilidad de ±10 %, la tolerancia de los beneficios); redacta el business case y el
  `enfoque-beneficios.md`.
- `pm-agil-hibrido` arma el release plan; `pm-visuales`, el roadmap por etapas (`02-planificacion/visuales/roadmap.md`).
- `pm-direccion-decisiones` redacta `00-direccion/tolerancias-y-autoridad.md` (siete objetivos con tolerancia y
  prioridad, autoridad de cambio, presupuesto de cambio y escalado).
- `pm-director`: `estado.py tolerancia --nivel proyecto …`; `estado.py presupuesto cambio=12000
  limite_autoridad_cambio=10000 --por "Ejecutiva: Laura Méndez"` (queda en `estado.json.presupuestos` y en
  `decisiones.csv`); puertas con `puertas.py`; `bmad.py linea-base prd|epicas --version 1.0`; `estado.py aprobar backlog
  --nivel product-owner`.

**Qué deberías ver:**
- Business case (fila "Línea base" de `inversion.py`): VAN 39.776, TIR 21,0 %, repago en 3,00 años. B-01 sostiene el
  caso: su punto de equilibrio es "76,8 % del valor estimado", es decir, puede caer 23,2 % antes de que el VAN llegue
  a 0.
- Verificación de autorizar-proyecto: "1 bloqueo(s) · 0 condición(es) · 2 aviso(s)". El bloqueo es L-01, la lista de
  control (se genera y la confirma Laura); los avisos son P-09 (sin matriz poder/interés) y P-10 (sin RACI), que se
  trabajan en E2E-3.
- **No aparece P-04 "sin enfoque de beneficios"**, porque el enfoque quedó registrado.
- "Línea base bmad-prd v1.0 registrada · sha bc048f7f59a3"; "bmad-epicas v1.0 · sha 3ff846d6f8d9"; "Copia congelada …
  00-direccion/historial/backlog-v1.0.csv"; fase `entrega`, etapa 2 "Release 1".

> **Por qué importa.** En la práctica la autoridad de cambio "aprueba lo razonable" sin un tope escrito, nadie lleva
> la cuenta de cuánto se comprometió y el VAN se calcula una sola vez, para aprobar el proyecto. Con el límite y el
> presupuesto en `estado.json`, `registro.py` no deja registrar una aprobación de la autoridad de cambio que los supere
> y sanidad compara los cambios aprobados contra ellos de forma continua (CAM-03 y CAM-04, pasos 7 y 10); con los
> flujos en un CSV, cada cambio recalcula el VAN en segundos.

**Dónde verificar:** `00-direccion/tolerancias-y-autoridad.md` · `00-direccion/business-case.md` y
`00-direccion/flujos-business-case.csv` · `00-direccion/enfoque-beneficios.md` · `00-direccion/historial/` (copias
congeladas) · `02-planificacion/release-plan.md` · `02-planificacion/visuales/roadmap.md` · `decisiones.csv` · prompt:
"Mostrame el resumen del proyecto" (`estado.py resumen` lista los presupuestos).

---

## Paso 6 · Cambio menor: intercambio de Should/Could por el PO

**Prompt**
```text
Cumplimiento pide adelantar la actualización de contacto. Sofía decide: la 2.3 (Could) pasa a R1 y la 1.4 constancias
(Should) a R2, sin tocar Must, fecha ni costo. Registralo y avisale al equipo BMAD.
```

**Si te pregunta:** nada; la decisión es de la PO y está en el prompt.

**Qué hace el sistema:** `pm-agil-hibrido` verifica que es un intercambio permitido al PO (Should/Could equivalentes,
sin tocar Must, fecha ni costo) → `registro.py agregar decisiones --campo nivel=product-owner` (**no** hay solicitud
de cambio) → `bmad.py handoff` (sin `--cambio`: prioridades para el sprint planning de BMAD).

**Qué deberías ver:** **D-009**; "Traspaso emitido → …/handoff-bmad-<fecha>-prioridades.md". R1 queda con 47 puntos y R2
con 21.

**Dónde verificar:** `decisiones.csv` · `02-planificacion/especificacion/handoff-bmad-<fecha>-prioridades.md`.

---

## Paso 7 · Cambio de alcance: análisis de impacto antes de decidir

En BMAD, el PM de producto agrega **FR-13 "Simulador de préstamo"** al PRD por pedido del Consejo, sin pasar por la
autoridad de cambio. Para simularlo en tu copia, pedíselo a BMAD con `bmad-prd` en modo edición, o editá el PRD.

**Prompt**
```text
Verificá la especificación contra la línea base. Si hay algo nuevo, registralo como solicitud de cambio y analizá el
impacto antes de decidir: paquete de la WBS nuevo, esfuerzo, camino crítico, reserva de cronograma, costo, presupuesto
de cambio, autoridad, capacidad del release y business case. Estimá el simulador en O 8, M 10, P 16 días después de los
sprints de solicitudes; Sofía estima que suma 4.000 por año al beneficio B-03. Si la reserva de cronograma queda chica,
registralo como riesgo.
```

**Si te pregunta** la decisión: "Sofía Ramírez, autoridad de cambio: aprobado; se carga al presupuesto de cambio".

**Qué hace el sistema:**
1. `bmad.py verificar` → desvío. Sin un issue que lo cite, sanidad lo marcaría **ERROR ESP-10** ("Cambio no
   controlado"); con I-001 baja a AVISO hasta que se fije la nueva línea base (paso 8).
2. `pm-issues-cambios` registra **I-001** `solicitud-cambio`.
3. `pm-cronograma-estimacion` corre `cpm.py` sobre un **escenario** (`02-planificacion/escenarios/actividades-C-001.csv`)
   y `pm-caso-de-negocio` corre `inversion.py` sobre otro (`escenarios/flujos-C-001.csv`), sin tocar las líneas base.
4. `pm-issues-cambios` registra **C-001** con el impacto en los objetivos, el monto y su cargo (`--campo costo=9000
   --campo cargo=presupuesto-cambio`) y arma la **tabla de impacto** (abajo) **antes** de la decisión.
5. Decide la autoridad de cambio; `pm-riesgos` registra **R-001** (probabilidad 3 × impacto 3, respuesta reducir,
   disparador SPI < 0,90, revisión el 19/2); `wbs.py` suma el paquete **3.4**; `bmad.py handoff --cambio C-001`;
   `sanidad.py --rapido --corte 2027-01-18`.

**Qué deberías ver:**
- "agregados ['FR-13']"; escenario: "Duración total (días laborables): 121 · Fin previsto: 2027-05-18"; en el business
  case, la fila "Con C-001" da VAN 45.939, TIR 21,8 % y 6.163 más que la línea base.
- La tabla de impacto de C-001 (en la evidencia, tal cual):

| Objetivo | Antes | Con C-001 | Contra qué se mide | Lectura |
|---|---|---|---|---|
| Tiempo (camino crítico) | 110 días · fin 2027-05-03 | 121 días · fin 2027-05-18 (+11) | tolerancia del proyecto ±3 semanas = 15 días | dentro: usa 11 de 15 (73 %) |
| Reserva de cronograma | 2σ = 13,0 días | 13,0 − 11 = 2,0 días | atraso posible del camino crítico | queda casi agotada: registrar riesgo |
| Costo (BAC) | 124.000 | 133.000 (+9.000) | presupuesto de cambio, no la tolerancia de costo | se paga con el presupuesto de cambio |
| Presupuesto de cambio | 0 de 12.000 | 9.000 de 12.000 (75 %) | CAM-03: aviso desde 80 %, error sobre 100 % | dentro del saldo |
| Autoridad | — | 9.000 en un cambio | límite de la autoridad de cambio 10.000 | lo decide la autoridad de cambio |
| Capacidad del R2 | 21 pts de 24 (3 sprints) | 29 pts de 24 | velocidad 8 pts por sprint | hace falta 1 sprint más (4 sprints = 32 pts) |
| Business case (VAN a 5 años) | 39.776 | 45.939 (+6.163) | inversion.py, tasa 10 % | a favor: el simulador se paga solo |

- C-001 aprobado; R-001; WBS "14 elementos, 9 hojas · esfuerzo 2660 h · costo 133,000"; el traspaso
  `handoff-bmad-<fecha>-C-001.md`.
- Sanidad "0 ERROR · 4 AVISO · 3 INFO" con **"INFO CAM-03 Presupuesto de cambio: 9.000 de 12.000 (75 %)"**. Los avisos son
  el seguimiento del cambio en curso, que se resuelve en el paso 8: ESP-10 (el PRD difiere de su línea base y hay un
  issue que lo trata), dos ESP-13 (traspasos a BMAD sin confirmar) y ESP-14 (`requisitos-bmad.csv` sin resincronizar).

![Fin de cada hito antes y después de C-001](img/g2-roadmap-c001.png)
El Release 1 sigue en el día 68; UAT y puesta en producción se corren 11 días, dentro de la tolerancia de 15.

> **Más desarrollo: el impacto se mira antes, y en todos los objetivos.** La pregunta habitual es "¿cuánto cuesta?".
> La tabla agrega las que se olvidan: qué le hace al camino crítico, cuánto queda de reserva, si entra en la capacidad
> del release, si está dentro del límite de quien decide, cuánto queda del presupuesto y si el cambio crea valor. Con
> esa tabla, la decisión de Sofía es informada y queda registrada con sus condiciones (riesgo R-001 y sprint 10).

> **Por qué no "contra la contingencia".** Este proyecto no tiene contingencia definida, y la reserva de riesgo solo
> financia respuestas a riesgos. Un cambio aprobado se paga con el **presupuesto de cambio** del paso 5: por eso el BAC
> pasa de 124.000 a 133.000 y el saldo baja a 3.000. Sin monto ni cargo, sanidad lo marcaría CAM-01.

**Dónde verificar:** `issues.csv` · `cambios.csv` (columnas `impacto_*`, `decision`, `decidido_por`, `costo`, `cargo`)
· `riesgos.csv` · `02-planificacion/escenarios/` (cronograma y flujos de C-001) · la tabla de impacto en la evidencia ·
prompt: "¿Qué impacto tiene C-001 en fecha, costo, capacidad y VAN, y cuánto queda del presupuesto de cambio?".

---

## Paso 8 · BMAD aplica el cambio, nuevas líneas base y trazabilidad recalculada

El equipo BMAD aplica el traspaso con sus flujos (`bmad-prd`, `bmad-create-epics-and-stories`) y agrega la historia 2.4.

**Prompt**
```text
El equipo BMAD aplicó el traspaso de C-001 (historia 2.4 Simulador). Resincronizá requisitos, trazabilidad y backlog,
poné la 2.4 como Should de 8 puntos en el sprint 10 del R2, mostrame la cobertura de trazabilidad, fijá las nuevas
líneas base y actualizá el roadmap.
```

**Si te pregunta:** "Laura Méndez, ejecutiva: apruebo las líneas base 1.1".

**Qué hace el sistema:** `bmad.py requisitos` · `trazabilidad` · `backlog` · `pm-agil-hibrido` completa el gobierno de
la 2.4 · recalcula la cobertura · `pm-visuales` actualiza el roadmap · `pm-director`: `bmad.py linea-base prd|epicas
--version 1.1` · C-001 `implementado` e I-001 `cerrado` · `bmad.py verificar` · `sanidad.py --rapido --corte 2027-01-25`.

**Qué deberías ver:**
- "43 identificadores"; "backlog.csv: 1 nuevas, 10 actualizadas"; "bmad-prd v1.1 · sha 089472ba0219"; "bmad-epicas v1.1 ·
  sha acca7ef6e6b2"; "Sin desvíos: la especificación coincide con las líneas base registradas".
- Cobertura: 13 de 13 requisitos funcionales con historia y con paquete; 11 de 11 historias con producto de la PBS;
  6 de 6 NFR con paquete o criterio de calidad; 1 de 13 requisitos citados en su propia historia (FR-13).
- Sanidad "0 ERROR · 0 AVISO · 3 INFO": CAM-03 (9.000 de 12.000, 75 %), ESP-02 (índice de especificación que se
  reconstruye solo) y **TOL-03** ("Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se
  vigila"), que se corrige en el paso 9.
- R2 pasa a 29 puntos: se agrega el sprint 10 y la capacidad sube a 32. El roadmap cambia de fin 2027-05-03 a 2027-05-18.

![Cobertura de trazabilidad tras C-001](img/g2-trazabilidad.png)
Tras el cambio, la cobertura sigue completa. La única barra en ámbar señala que BMAD traza 12 requisitos a nivel de
épica: es una mejora para el equipo de producto, no un hueco de alcance.

> **Más desarrollo: trazabilidad continua.** La matriz no se arma una vez: se regenera en cada sincronización, y la
> cobertura se compara contra la anterior (12 de 12 en el paso 2, 13 de 13 tras el cambio). Si el traspaso no se
> hubiera aplicado, FR-13 quedaría sin historia y `bmad.py trazabilidad` lo listaría como "Requisitos funcionales sin
> historia".

**Dónde verificar:** `00-direccion/historial/bmad-prd-v1.1` · `backlog.csv` ·
`02-planificacion/especificacion/matriz-trazabilidad-bmad.csv` · `02-planificacion/visuales/roadmap.md` · prompt:
`/pm-method:pm-sync bmad`.

---

## Paso 9 · Avance del alcance (EVM ágil guardado) y calidad de lo terminado

El **valor ganado** (EVM, *earned value management*) compara lo planificado (PV), lo ganado (EV) y lo gastado (AC). En
modo ágil, con costo y fecha fijos, un EAC (costo estimado a la conclusión) mayor que el BAC no se lee como sobrecosto
sino como **alcance que no va a entrar**.

**Prompt**
```text
Corte del 29/1: ¿cuánto alcance llevamos y entra todo con el presupuesto? PV 60.000, EV 52.000, AC 58.000, BAC 133.000.
Leelo como ágil: costo y fecha fijos, el 20 % del alcance es Should/Could. Guardá el corte para que quede vigilado.
Registrá la revisión de calidad del 28/1 de las historias 1-1, 1-2, 1-3 y 3-1: Sofía la aprobó contra la descripción
de producto 3.1 y los criterios de aceptación.
```

**Si te pregunta:** nada; las cifras del corte y la revisión están en el prompt.

**Qué hace el sistema:** `bmad.py avance` (estados de BMAD → `avance-bmad.csv`) y `bmad.py backlog` (el estado `done`
llega a `backlog.csv`); `pm-calidad` registra **Q-001** (revisión completada y aprobada, cita las cuatro historias y
EC-01 a EC-04); `pm-progreso-reportes` → `evm.py --pv 60000 --ev 52000 --ac 58000 --bac 133000 --modo agil
--pct-no-must 20 --proyecto gestion --guardar --corte 2027-01-29`; como el SPI quedó debajo de 0,90, `pm-riesgos` anota
que se activó el disparador de R-001 y lo pasa a `en-seguimiento`; `sanidad.py --rapido --corte 2027-01-29`;
`puertas.py estado --markdown` para el highlight.

**Qué deberías ver:**
- "Historias 11 · … done 4 · … 34.2 % (puntos)"; "Guardado: 03-control/reportes/evm-2027-01-29.json".
- SPI 0,867 · CPI 0,897 · EAC 148.346 → `alcance_no_entregable_pct 10.345` · `semaforo_alcance ambar` ·
  `excepcion_prevista False`: no entra ≈ 10 % del alcance, menos que el 20 % de Should/Could. **Los Must no peligran**
  y el PO decide qué Should/Could salen, que es la respuesta prevista en R-001 ("disparador activado el 2027-01-29 (SPI
  0,867 < 0,90)").
- Sanidad "0 ERROR · 0 AVISO · 3 INFO" con **TOL-02** ("El EVM del 2027-01-29 está en ámbar … alcance=ambar: 50–100 % de
  la tolerancia") y CAM-03 al 75 %.
- No hay **QUA-01**: las cuatro historias terminadas tienen una revisión aprobada que las cita. Sin Q-001, sanidad daría
  un aviso por cada una ("terminado sin revisión de calidad registrada").

**Dónde verificar:** `03-control/reportes/avance-bmad.csv` · `03-control/reportes/evm-2027-01-29.json` · `calidad.csv`
· `riesgos.csv` (R-001: `estado`, `notas`) · la tabla de puertas de `puertas.py estado --markdown` (en la evidencia).

---

## Paso 10 · Excepción: el cambio excede la autoridad delegada y el pronóstico sale de la tolerancia

**El problema real.** Un pedido "obligatorio" se aprueba en el momento por quien está más cerca, nadie suma lo que ya
se comprometió y el pronóstico de EVM vive en una planilla que se mira al cerrar la etapa. Acá se frena **el mismo
día**: `registro.py` no deja registrar como aprobado un cambio que supera el límite de quien lo decide o el saldo del
presupuesto de cambio (queda `pendiente-decision` y se escala a la junta), sanidad cruza cada corte guardado con la
tolerancia (TOL-01) y la verificación de puertas no deja aprobar nada mientras haya un ERROR.

**Gestión por excepción** (*management by exception*): cada nivel decide dentro de su tolerancia y, si un pronóstico la
supera, escala al nivel de arriba con un **informe de excepción**; la junta puede pedir un **plan de excepción** que
reemplaza el plan vigente y llega con el business case y los riesgos actualizados.

La revisión normativa que el PRD dejaba como supuesto (NFR-1, Ley 18.331) concluye que el socio debe dar
consentimiento informado y poder consultar el registro de sus accesos. El Consejo lo pide como obligatorio.

**Prompt 1 (19/2, gestor)**
```text
Registrá el requisito regulatorio como solicitud de cambio: paquete nuevo 3.5, 13 puntos Must en R1, +1 sprint en la
etapa 2, USD 15.000, sin beneficio propio. Sofía lo aprobó el 17/2 porque es obligatorio: registralo. Guardá el corte de EVM del
19/2 (PV 75.000, EV 60.000, AC 77.000, BAC 133.000, ágil, 20 % Should/Could), corré sanidad al 19/2 y armá la tabla de
impacto de C-002 con su efecto en el business case. Si hay excepción, prepará el informe de excepción para la junta y
registrá el issue.
```
**Prompt 2 (22/2, junta)**
```text
Laura Méndez, ejecutiva: leí el informe X-001; la junta pide un plan de excepción para la etapa 2. Prepará el plan:
C-002 entra como Must en R1, la etapa termina el 19/3, sale la 2.3 de R1 y se pide ampliar el presupuesto de cambio.
```
**Prompt 3 (26/2, junta)**
```text
Laura Méndez, ejecutiva: la junta amplía el presupuesto de cambio a 32.000 (12.000 originales + 15.000 de C-002 + 5.000
de reposición), aprueba C-002 con cargo a ese presupuesto y aprueba el plan de excepción con fin de etapa el 19/3.
Confirmo la lista de control.
```

**Si te pregunta:** las decisiones de la junta están en los prompts 2 y 3 (Laura Méndez, ejecutiva). Si al cierre te
pide revisar R-001: "Martín Suárez, gestor: sube a probabilidad 4 (SPI 0,80 al 19/2 y un sprint más en la etapa 2);
próxima revisión el 19/3, al fin de la etapa".

**Qué hace el sistema:**
- **Con el prompt 1 (19/2):**
  1. `pm-issues-cambios` registra **I-002** `solicitud-cambio` y **C-002** con `costo=15000` y
     `cargo=presupuesto-cambio`. Al registrar la aprobación de Sofía (`decision=aprobado`, `decidido_por=Autoridad de
     cambio: Sofía Ramírez`), **`registro.py` la rechaza**: supera su límite de 10.000 y el saldo del presupuesto de
     cambio (9.000 + 15.000 = 24.000 de 12.000). C-002 queda `pendiente-decision`, con la aprobación de Sofía anotada
     en `notas`, y se escala a `pm-director`.
  2. `pm-progreso-reportes`: `evm.py … --proyecto gestion --guardar --corte 2027-02-19` → `evm-2027-02-19.json`.
  3. `sanidad.py --rapido --corte 2027-02-19` detecta la excepción prevista del EVM (TOL-01); el presupuesto de cambio
     sigue en 75 % porque C-002 no se aprobó (ver abajo).
  4. `pm-caso-de-negocio` corre `inversion.py` sobre `escenarios/flujos-C-002.csv` con el plan vigente como base
     (`--base "Con C-001"`), y `pm-issues-cambios` arma la **tabla de impacto de C-002**, que muestra lo que la
     aprobación de palabra del 17/2 no miró.
  5. `pm-progreso-reportes` redacta el **informe de excepción X-001** (plantilla `informe-excepcion.md`, con el impacto
     en el business case) y lo registra como `informe-excepcion-X-001`; `pm-issues-cambios` registra **I-003**
     `problema-preocupacion` (severidad crítica, `escalado`) e I-002 pasa a `escalado`.
- **Con el prompt 2 (22/2):**
  6. `pm-director`: `estado.py puerta decision-ad-hoc --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha
     2027-02-22 --condiciones "X-001: la junta pide plan de excepción …"` y `estado.py limite-etapa --excepcion X-001`
     (la etapa pasa a SB, límite de etapa). La condición queda abierta y a la vista (EST-12 en sanidad, G-01 en la
     próxima verificación) hasta que alguien la dé por cumplida.
  7. `pm-plan-etapa-y-limites` redacta el **plan de excepción** (plantilla `plan-excepcion.md`) y lo registra como
     `plan-excepcion-X-001`; `pm-caso-de-negocio` actualiza el business case con el escenario de C-002; `pm-director`
     cierra la condición con `estado.py cumplir-condiciones decision-ad-hoc --fecha 2027-02-24 --por "Ejecutiva: Laura
     Méndez" --nota "…"`.
- **Con el prompt 3 (26/2):**
  8. `pm-director`: `puertas.py verificar autorizar-plan-excepcion` → bloqueada solo por la lista de control (L-01).
     La junta decide: primero `estado.py presupuesto cambio=32000 --por "Ejecutiva: Laura Méndez"` (queda en
     `decisiones.csv`) y después C-002 `aprobado` con `decidido_por=Junta: Laura Méndez (ejecutiva) · plan de excepción
     X-001` y `cargo=presupuesto-cambio`, que ahora tiene saldo (24.000 de 32.000). Sin la ampliación, `registro.py`
     también rechazaría la aprobación de la junta y pediría la fuente: `reserva-gestion`, `plan-excepcion` o ampliar el
     presupuesto. Después: `verificar`, `puertas.py lista … --fecha 2027-02-26`, `confirmar … --fecha 2027-02-26` y
     `estado.py puerta autorizar-plan-excepcion --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26
     --fin 2027-03-19`.
  9. I-003 `cerrado`, I-002 `pendiente-cambio`; `wbs.py` suma el paquete **3.5**; `bmad.py handoff --cambio C-002`;
     `sanidad.py --rapido --corte 2027-02-26` → **REG-09**; `pm-riesgos` revisa R-001 con su propietario
     (`registro.py actualizar riesgos R-001 --campo probabilidad=4 --campo fecha_revision=2027-03-19 …`); sanidad otra
     vez; `estado.py resumen`; `registro.py listar cambios`.

**Qué deberías ver:**
- EVM del 19/2: SPI 0,800 · CPI 0,779 · EAC 170.683 · `alcance_no_entregable_pct 22.078` · `semaforo_alcance rojo` ·
  `excepcion_prevista True` · "→ Pronóstico fuera de tolerancia: preparar informe de excepción (pm-progreso-reportes) y
  escalar a pm-director". No entra ≈ 22 % del alcance, más que el 20 % de Should/Could: **los Must peligran**.
- Rechazo de la aprobación de Sofía: "Control de cambios (PRINCE2, autoridad y presupuesto de cambio; no se omite con
  --forzar)" con "C-002: costo 15.000 supera el límite de la autoridad de cambio (10.000)", "C-002: el presupuesto de
  cambio no alcanza: 9.000 ya cargados + 15.000 = 24.000 de 12.000 fijados por la junta" y "→ 'Autoridad de cambio:
  Sofía Ramírez' no es la junta ni el ejecutivo. Dejar estado=pendiente-decision (sin decision=aprobado) y escalar a
  pm-director: decide la junta o el ejecutivo".
- Sanidad del 19/2: "0 ERROR · 1 AVISO · 1 INFO":
  - **AVISO TOL-01** "El EVM del 2027-02-19 pronostica salir de la tolerancia (… alcance=rojo) y no hay excepción
    abierta".
  - **INFO CAM-03** "Presupuesto de cambio: 9.000 de 12.000 (75 %)": C-002 no consume presupuesto mientras esté
    pendiente, y sin CAM-04 porque ninguna aprobación quedó fuera de la autoridad.
- Business case (fila "Con C-001 y C-002"): VAN 30.939, TIR 17,3 %, repago en 3,23 años y 15.000 menos que el plan
  vigente; el punto de equilibrio de B-01 sube a "81,9 % del valor estimado".
- La tabla de impacto de C-002 (en la evidencia, tal cual):

| Objetivo | Antes | Con C-002 | Contra qué se mide | Lectura |
|---|---|---|---|---|
| Presupuesto de cambio | 9.000 de 12.000 (75 %) | 24.000 de 12.000 (200 %) | saldo fijado por la junta (registro.py; CAM-03) | no alcanza: hace falta otra fuente o ampliarlo |
| Autoridad | límite 10.000 por cambio | 15.000 en un cambio | límite delegado a la autoridad de cambio | excedida: registro.py rechazó su aprobación |
| Capacidad del R1 | 47 pts de 48 (6 sprints) | 60 pts; sin la 2-3 (Could, 5): 55 pts | velocidad 8 pts por sprint | 7 sprints: +1 sprint (14 días corridos) |
| Tiempo de la etapa 2 | fin 2027-03-05 (98 días corridos desde 2026-11-27) | fin 2027-03-19 (+14) | tolerancia de etapa ±10 % = 9,8 días | fuera de tolerancia |
| Alcance (EVM del 19/2) | Should/Could = 20 % del alcance | no entra 22,1 % | Must sin tolerancia | los Must peligran |
| Business case (VAN a 5 años) | 45.939 · B-01 puede caer 27 % | 30.939 · B-01 puede caer 18 % | VAN > 0 · tolerancia de beneficios −10 % | sigue justificado, con menos margen |
| Fin del proyecto | 2027-05-18 (con C-001) | lo recalcula el plan de proyecto con el plan de excepción | ±3 semanas | no se recalcula en esta corrida |

- `limite-etapa`: "Proceso: SB" y "Límite de etapa por excepción X-001: plan de excepción (reemplaza el plan vigente),
  actualizar plan de proyecto, business case y riesgos. Puerta: autorizar-plan-excepcion".
- Primera verificación: "Puerta autorizar-plan-excepcion: 1 bloqueo(s)", solo L-01, la lista de control: como C-002 no
  se registró aprobado contra un presupuesto agotado, no hay ERROR CAM-03 que bloquee (si lo hubiera, por datos
  cargados antes de que la junta fijara el presupuesto, la verificación lo convertiría en bloqueo S-CAM-03).
- Tras la decisión de la junta: "1 bloqueo(s)" (L-01 hasta confirmar la lista); "Lista creada:
  00-direccion/decisiones/2027-02-26-verificacion-autorizar-plan-excepcion.md (0 hallazgos automáticos, 3 ítems para la
  junta)"; la puerta queda aprobada y vuelve a "Proceso: CS". La WBS queda en "15 elementos, 10 hojas · esfuerzo 2960 h
  · costo 148,000".
- Sanidad del 26/2: "0 ERROR · 2 AVISO · 2 INFO" con **"AVISO REG-09 Riesgo R-001 abierto con la revisión vencida
  (2027-02-19; propietario: Martín Suárez)"**. `limite-etapa` pedía actualizar el business case y los riesgos: el
  business case se actualizó, R-001 no. Tras la revisión, sanidad final: "0 ERROR · 1 AVISO · 1 INFO": **"INFO CAM-03
  Presupuesto de cambio: 24.000 de 32.000 (75 %)"**, sin CAM-04 (la decisión es de la junta), sin TOL-01 (la puerta del
  26/2 es posterior al corte del 19/2) y sin REG-09. El aviso que queda es ESP-13: el traspaso de C-002 todavía no lo
  aplicó el equipo BMAD.
- `estado.py resumen`: "etapa 2 Release 1 (2026-11-27 → 2027-03-19)" · "Presupuestos: cambio=32000,
  limite_autoridad_cambio=10000" · "Última puerta: autorizar-plan-excepcion · aprobado · 2027-02-26 · Ejecutiva: Laura
  Méndez".

![Consumo del presupuesto de cambio](img/g2-consumo-cambio.png)
75 % tras C-001 (sanidad del 18/1); el 19/2, el 200 % que habría sumado C-002 según `registro.py` al rechazar su
aprobación (el consumo real siguió en 75 %); y 75 % con el tope que amplió la junta (sanidad del 26/2).

![Alcance que no entra frente al margen](img/g2-alcance-evm.png)
El mismo indicador, guardado por corte, pasa de ámbar (10,3 %) a rojo (22,1 %): el segundo corte supera el margen de
Should/Could y dispara TOL-01.

![VAN del business case en cada escenario](img/g2-business-case.png)
C-002 no suma beneficio propio y resta 15.000 de VAN, pero el caso sigue justificado: B-01 puede caer 18 % antes de que
el VAN llegue a 0, más que su tolerancia de −10 %.

> **Más desarrollo: excepción con impacto calculado.** La tabla de C-002 da a la junta lo que necesita para decidir:
> tres límites superados (autoridad, saldo del presupuesto y tolerancia de tiempo de la etapa), uno en riesgo (los Must) y la
> respuesta a la pregunta que PRINCE2 hace en cada puerta, ¿sigue valiendo la pena el proyecto? Con VAN de 30.939, sí,
> con menos margen. El fin del proyecto no se recalcula en esta guía: lo debe actualizar el plan de proyecto junto con
> el plan de excepción, como pide `limite-etapa`. Si quedara fuera de ±3 semanas, la junta tampoco podría aprobarlo
> sola.

**Dónde verificar:** `03-control/reportes/evm-2027-02-19.json` · `03-control/reportes/2027-02-19-informe-excepcion-X-001.md`
· `02-planificacion/plan-excepcion-X-001.md` · `00-direccion/business-case.md` · `02-planificacion/escenarios/flujos-C-002.csv`
· `00-direccion/decisiones/2027-02-26-verificacion-autorizar-plan-excepcion.md` · `cambios.csv` (C-002:
`decidido_por`, `notas`, `costo`, `cargo`) · `issues.csv` (I-002, I-003) · `riesgos.csv` (R-001) · `decisiones.csv` ·
prompt: "¿Cuánto queda del presupuesto de cambio, qué decidió la junta sobre X-001 y sigue justificado el proyecto?".

---

## Reporte: informe de alcance y cambio (ejemplo para el highlight)

> Cifras de la corrida de referencia; el texto lo redacta el modelo.

| Tema | Línea base (27/11) | Corte 29/1 | Tras la excepción (26/2) |
|---|---|---|---|
| Alcance | 10 historias · 68 puntos · 12 FR · WBS 124.000 | 11 historias · 76 puntos · 13 FR (C-001) · WBS 133.000 | + C-002 regulatorio (Must, 13 puntos) aprobado por la junta · WBS 148.000; traspaso a BMAD pendiente |
| Releases | R1 47 pts / 48 · R2 21 pts / 24 | R1 47 pts (intercambio D-009) · R2 29 pts / 32 (sprint 10 agregado) | plan de excepción X-001: C-002 en R1, sale la 2.3 |
| Cronograma | fin 2027-05-03 · reserva 2σ = 13,0 días | fin 2027-05-18 (+11 días) · reserva remanente 2,0 días (R-001, disparador activado) | fin de etapa 2: 2027-03-05 → 2027-03-19 · R-001 revisado (probabilidad 4) |
| Avance | — | 34,2 % de puntos · SPI 0,87 · CPI 0,90 · alcance que no entra 10,3 % (ámbar) | corte 19/2: SPI 0,80 · CPI 0,78 · 22,1 % que no entra (rojo) |
| Presupuesto de cambio | 12.000 · límite 10.000 por cambio | 9.000 usados (75 %) | 24.000 de 32.000 (75 %) tras la ampliación |
| Business case | VAN 39.776 · TIR 21,0 % | VAN 45.939 con C-001 | VAN 30.939 con C-001 y C-002 · B-01 puede caer 18 % |
| Trazabilidad | 12 de 12 FR con historia y paquete | 13 de 13 FR con historia y paquete | — |

**Decisión que se pidió a la junta:** en el corte del 29/1, ninguna (ámbar en alcance, gestionable por el PO; R-001
registrado por la reserva de cronograma y en seguimiento). El 19/2, la excepción X-001: la junta pidió un plan de
excepción, amplió el presupuesto de cambio, verificó que el business case sigue justificado y lo autorizó el 26/2.

## Representaciones gráficas

Los PNG de esta guía (`img/g2-*.png`) los genera el driver `scripts/pruebas/guias_e2e/g2.py` con los datos de la
corrida, con `visuales.py`. Los diagramas que genera el sistema están en `02-planificacion/visuales/wbs.md` (WBS),
`02-planificacion/cronograma.md` (Gantt con el camino crítico) y `02-planificacion/visuales/roadmap.md` (roadmap antes y
después de C-001).

**Valor contra esfuerzo** (izquierda 5 puntos, derecha 8 puntos; altura según el valor de 1 a 10, con un pequeño
desplazamiento para que no se superpongan las etiquetas):
```mermaid
quadrantChart
    title Priorización del backlog
    x-axis Menor esfuerzo --> Mayor esfuerzo
    y-axis Menor valor --> Mayor valor
    quadrant-1 Grandes apuestas
    quadrant-2 Ganancias rápidas
    quadrant-3 Relleno
    quadrant-4 Evitar o partir
    1.3 saldos: [0.62, 0.84]
    1.1 alta: [0.86, 0.76]
    2.1 préstamo: [0.62, 0.70]
    3.2 bandeja: [0.86, 0.63]
    3.3 resolución: [0.62, 0.57]
    2.2 seguimiento: [0.86, 0.40]
    1.4 constancias: [0.24, 0.72]
    1.2 recuperación: [0.12, 0.58]
    3.1 roles: [0.36, 0.52]
    2.3 contacto: [0.24, 0.26]
```

**Mapa de ruta por etapas con puertas: antes y después de C-001**
```mermaid
gantt
    title Roadmap · línea base (antes de C-001)
    dateFormat YYYY-MM-DD
    axisFormat %b
    todayMarker off
    section Gobierno
    SU puesta en marcha        :done, su, 2026-10-19, 2026-10-30
    IP iniciación              :done, ip, 2026-10-30, 2026-11-27
    autorizar-proyecto y etapa :milestone, m1, 2026-11-27, 0d
    section Etapa 2 · Release 1
    Sprints 1 a 6 (47 pts)     :r1, 2026-11-30, 2027-03-05
    Release 1                  :milestone, m2, 2027-03-05, 0d
    section Etapa 3 · Release 2
    Sprints 7 a 9 (21 pts)     :r2, 2027-03-08, 2027-04-16
    UAT y capacitación         :u, 2027-04-19, 2027-05-03
    Puesta en producción       :milestone, m3, 2027-05-03, 0d
```
```mermaid
gantt
    title Roadmap · con C-001 (simulador de préstamo)
    dateFormat YYYY-MM-DD
    axisFormat %b
    todayMarker off
    section Gobierno
    SU puesta en marcha        :done, su, 2026-10-19, 2026-10-30
    IP iniciación              :done, ip, 2026-10-30, 2026-11-27
    autorizar-proyecto y etapa :milestone, m1, 2026-11-27, 0d
    section Etapa 2 · Release 1
    Sprints 1 a 6 (47 pts)     :r1, 2026-11-30, 2027-03-05
    Release 1                  :milestone, m2, 2027-03-05, 0d
    section Etapa 3 · Release 2
    Sprints 7 a 9 (21 pts)     :r2, 2027-03-08, 2027-04-16
    Sprint 10 simulador (C-001) :crit, s10, 2027-04-19, 2027-05-03
    UAT y capacitación         :u, 2027-05-04, 2027-05-18
    Puesta en producción       :milestone, m3, 2027-05-18, 0d
```

**Trazabilidad del cambio:**
```mermaid
flowchart TB
    i1["I-001 · solicitud de cambio<br/>(desvío FR-13 detectado)"] --> c1["C-001 · tabla de impacto<br/>tiempo, reserva, costo, capacidad, VAN"]
    c1 --> dec{"Autoridad de cambio<br/>Sofía Ramírez"}
    dec -->|"aprobado · 9.000 de 12.000"| w34["WBS 3.4<br/>Simulador · USD 9.000"]
    dec --> h["bmad.py handoff<br/>--cambio C-001"]
    dec --> r1["R-001 · reserva<br/>de 2,0 días"]
    h --> bm["Equipo BMAD:<br/>historia 2.4"]
    bm --> lb["Líneas base<br/>PRD y épicas 1.1"]
    bm --> tz["Trazabilidad recalculada<br/>13 de 13 FR"]
    w34 --> rm["Roadmap: fin<br/>2027-05-18"]
```

**Gestión por excepción (paso 10):**
```mermaid
flowchart TB
    c2["C-002 · requisito regulatorio<br/>15.000, aprobado de palabra por Sofía"] --> rg{"registro.py<br/>límite y saldo"}
    rg -->|"rechaza<br/>pendiente-decision"| ti["Tabla de impacto de C-002<br/>con VAN 30.939"]
    ev["evm.py --guardar<br/>corte 19/2 · alcance rojo"] --> s1{"sanidad<br/>corte 19/2"}
    s1 -->|"TOL-01<br/>CAM-03 al 75 %"| ti
    ti --> x["Informe de excepción<br/>X-001 e issue I-003"]
    x --> j1{"Junta 22/2<br/>decision-ad-hoc"}
    j1 --> le["limite-etapa<br/>--excepcion X-001"]
    le --> pe["Plan de excepción X-001<br/>y business case actualizado"]
    pe --> v1["verificar · bloqueo<br/>lista de control L-01"]
    v1 --> j2{"Junta 26/2"}
    j2 --> pr["presupuesto cambio=32000<br/>y luego C-002 aprobado"]
    pr --> ap["autorizar-plan-excepcion<br/>fin de etapa 2027-03-19"]
    ap --> s2["sanidad 26/2<br/>REG-09: revisar R-001"]
    s2 --> s3["sanidad final<br/>CAM-03 INFO 75 %"]
```

## Lista de comprobación de capacidades

- [ ] WBS por productos con `ref` a FR, historias y UJ; trazabilidad sin huecos ni ids inexistentes.
- [ ] Descripción del producto del proyecto y descripción de producto 3.1 con especificaciones de calidad, métodos y
      autoridad de aceptación, registradas como artefactos.
- [ ] PERT de tres puntos, camino crítico y reserva a 2σ calculados por script; exportación MSPDI; Gantt `g2-gantt.png`.
- [ ] Backlog con columnas derivadas de BMAD y de gobierno separadas; MoSCoW y valor/esfuerzo; capacidad verificada.
- [ ] Business case con flujos en CSV y VAN, TIR, repago y sensibilidad de `inversion.py`.
- [ ] Tolerancias y autoridad delegada documentadas; presupuesto de cambio y límite de la autoridad de cambio en
      `estado.json` con la decisión en `decisiones.csv`; enfoque de beneficios registrado (sin aviso P-04).
- [ ] Línea base de PRD, épicas y backlog con copia congelada; roadmap registrado.
- [ ] Intercambio Should/Could decidido por el PO sin solicitud de cambio, traspasado a BMAD.
- [ ] Cambio de alcance detectado por `bmad.py verificar`, con escenarios de cronograma y de flujos y **tabla de
      impacto antes de decidir**, monto cargado al presupuesto de cambio (CAM-03 INFO), riesgo derivado, decisión de la
      autoridad de cambio, traspaso, nuevas líneas base y roadmap actualizado (`g2-roadmap-c001.png`).
- [ ] Cobertura de trazabilidad recalculada en los pasos 2 y 8 (`g2-trazabilidad.png`).
- [ ] EVM ágil guardado por corte que separa alcance que no entra de sobrecosto (TOL-02 en ámbar) y disparador de R-001
      anotado.
- [ ] Revisión de calidad que cubre las historias terminadas (sin QUA-01).
- [ ] Excepción completa: aprobación de C-002 fuera de la autoridad rechazada por `registro.py` (queda
      `pendiente-decision`) y TOL-01 detectado el mismo día; tabla de impacto de C-002 con su VAN; informe e issue de
      la excepción; `limite-etapa --excepcion`; plan de excepción y business case actualizado; ampliación del
      presupuesto antes de que la junta apruebe C-002; `autorizar-plan-excepcion` aprobada; REG-09 resuelto con la
      revisión de R-001; sanidad final sin CAM-03 ERROR, CAM-04, TOL-01 ni REG-09 (`g2-consumo-cambio.png`,
      `g2-alcance-evm.png`, `g2-business-case.png`).
- [ ] Todas las llamadas a sanidad con `--corte` de la fecha del paso; dos corridas seguidas del driver con evidencia
      idéntica.

## Siguiente caso

Esta guía deja el alcance, el cronograma, el presupuesto y el business case bajo control, pero con una sola voz: la de
la junta y el equipo. El caso siguiente agrega a todos los demás: quiénes son los interesados, qué quieren saber, cómo
se les cuenta el avance y cómo se verifica que el contacto prometido se cumple. Seguí con
**[E2E-3 · Interesados, comunicaciones, OKR y reporte de avance](E2E-3-interesados-okr-avance.md)**.
