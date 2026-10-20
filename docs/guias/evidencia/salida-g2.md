## Paso 1 · Proyecto, especificación y enunciado de alcance
```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez" --fecha 2026-10-20
Proyecto creado en gestion · enfoque de entrega: hibrido · siguiente: estado.py siguiente
```

```
$ python3 $BMAD --proyecto gestion detectar
{
  "layout": "v6",
  "raiz": "<repo>",
  "salida": "<repo>/_bmad-output",
  "planning": "<repo>/_bmad-output/planning-artifacts",
  "implementation": "<repo>/_bmad-output/implementation-artifacts",
  "version": "6.12.4",
  "version_fuente": "_bmad/_config/manifest.yaml",
  "soporte": "soportada"
}
```

```
$ python3 $BMAD --proyecto gestion requisitos
42 identificadores · {'UJ': 3, 'FR': 12, 'NFR': 6, 'SM': 8, 'AD': 13} → gestion/02-planificacion/especificacion/requisitos-bmad.csv (derivado: no editar)
```

```
$ python3 $EST/estado.py --proyecto gestion rol usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" product_owner="Sofía Ramírez" autoridad_cambio="Sofía Ramírez" aseguramiento="Andrea Costa" jefes_equipo="Lucía Benítez"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion agil cadencia_iteracion_dias=14 velocidad_referencia=8
ok
```

```
$ python3 $EST/especificacion.py --proyecto gestion resumen
requisitos: 42
historias: 10
por_estado: {'backlog': 9, 'ready-for-dev': 1, 'in-progress': 0, 'review': 0, 'done': 0}
```

```
$ python3 $EST/especificacion.py --proyecto gestion listar epicas
id=E-1 | historias=['1-1-alta-y-acceso-del-socio-con-segundo-factor', '1-2-recuperación-de-acceso', '1-3-consulta-de-saldos-de-ahorro-y-préstamos', '1-4-descarga-de-constancias-en-pdf'] | titulo=Acceso seguro y consulta de mis productos | estado=backlog | refs=['FR-1', 'FR-11', 'FR-12', 'FR-2', 'FR-3', 'FR-4', 'FR-5']
id=E-2 | historias=['2-1-solicitud-guiada-de-préstamo-simple', '2-2-seguimiento-de-solicitudes-y-respuesta-a-pedidos-de-informac', '2-3-actualización-de-datos-de-contacto-con-verificación'] | titulo=Solicitudes del socio: préstamo y datos de contacto | estado=backlog | refs=['FR-12', 'FR-6', 'FR-7', 'FR-8']
id=E-3 | historias=['3-1-acceso-y-roles-de-la-consola-de-operador', '3-2-bandeja-única-de-solicitudes', '3-3-resolución-de-solicitudes'] | titulo=Consola de operador | estado=backlog | refs=['FR-10', 'FR-11', 'FR-9']
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enunciado-alcance --ruta 01-inicio/enunciado-alcance.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-gestion-alcance-requisitos --ruta 02-planificacion/enfoques/plan-gestion-alcance-requisitos.md --estado en-revision
ok
```

## Paso 2 · Estructura de productos (PBS), descripciones de producto con criterios de calidad y WBS trazada a requisitos e historias
```
$ python3 $EST/wbs.py gestion/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid gestion/02-planificacion/visuales/wbs.md --diccionario gestion/02-planificacion/diccionario-wbs.md
Portal de autoservicio para socios: 13 elementos, 8 hojas · esfuerzo 2480 h · costo 124,000
1 Gestión del proyecto [producto] 400 h · 20,000 · Martín Suárez
  1.1 Gestión de etapas [paquete] 400 h · 20,000 · Martín Suárez
2 Especificación del producto [producto] 240 h · 12,000 · Sofía Ramírez
  2.1 Brief PRD UX y arquitectura (BMAD) [paquete] 240 h · 12,000 · Sofía Ramírez
3 Portal del socio [producto] 1240 h · 62,000 · Lucía Benítez
  3.1 Acceso seguro [paquete] 420 h · 21,000 · Lucía Benítez
  3.2 Consulta y constancias [paquete] 380 h · 19,000 · Lucía Benítez
  3.3 Solicitudes del socio [paquete] 440 h · 22,000 · Lucía Benítez
4 Consola de operador [producto] 400 h · 20,000 · Lucía Benítez
  4.1 Bandeja y resolución [paquete] 400 h · 20,000 · Lucía Benítez
5 Transición [producto] 200 h · 10,000 · Sofía Ramírez
  5.1 UAT prueba de carga y capacitación [paquete] 200 h · 10,000 · Sofía Ramírez
  5.2 Puesta en producción [hito] 0 h · 0 · Sofía Ramírez
Mermaid escrito en gestion/02-planificacion/visuales/wbs.md
Diccionario escrito en gestion/02-planificacion/diccionario-wbs.md
```

```
$ python3 $BMAD --proyecto gestion trazabilidad --wbs 02-planificacion/wbs.csv
18 requisitos trazados → gestion/02-planificacion/especificacion/matriz-trazabilidad-bmad.csv
  Requisitos funcionales sin historia: ninguno
  Historias sin requisito: ninguna
  Trazados solo a nivel de épica (epics.md no cita el id en la historia): FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12
  Referencias de la WBS a ids inexistentes: ninguna
```

```
$ python3 $EST/especificacion.py --proyecto gestion listar requisitos --cobertura sin-cobertura

```

```
$ python3 $EST/estado.py --proyecto gestion artefacto descripcion-producto-proyecto --ruta 02-planificacion/descripcion-producto-proyecto.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto descripcion-producto-3.1 --ruta 02-planificacion/productos/3.1-acceso-seguro.md --estado en-revision
ok
```

```
$ (cobertura de trazabilidad recalculada en esta sincronización: matriz-trazabilidad-bmad.csv, backlog.csv y descripciones de producto)
Requisitos (FR) con historia: 12 de 12 (100 %) · bmad.py trazabilidad
Requisitos (FR) con paquete de la WBS: 12 de 12 (100 %) · columna ref de wbs.csv
NFR con WBS o criterio de calidad: 6 de 6 (100 %) · WBS o descripciones de producto
Requisitos (FR) citados en su historia: 0 de 12 (0 %) · el resto, solo a nivel de épica
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-13
Sanidad de 'Portal de autoservicio para socios' (pre-proyecto/SU): 0 ERROR · 0 AVISO · 0 INFO
```

## Paso 3 · Estimación de esfuerzo: PERT de tres puntos por actividad y reserva de cronograma
```
$ (estimacion-pert.csv que calcula pm-cronograma-estimacion: tE=(O+4M+P)/6, σ=(P−O)/6)
id,nombre,optimista,mas_probable,pesimista,tE,sigma
A01,Brief PRD UX y arquitectura (BMAD),8,10,15,10.5,1.17
A02,Spike de integración con el núcleo,5,8,14,8.5,1.50
A03,Sprints acceso seguro,20,28,40,28.7,3.33
A04,Sprints consulta y constancias,18,25,38,26.0,3.33
A05,Sprints consola de operador,20,28,42,29.0,3.67
A06,Release 1 aceptada,0,0,0,0.0,0.00
A07,Sprints solicitudes del socio,22,30,45,31.2,3.83
A08,UAT prueba de carga y capacitación,8,10,16,10.7,1.33
A09,Puesta en producción,0,0,0,0.0,0.00
```

```
$ python3 $EST/cpm.py gestion/02-planificacion/actividades.csv --inicio 2026-11-30 --titulo "Portal de autoservicio para socios" --mermaid gestion/02-planificacion/cronograma.md --mspdi gestion/02-planificacion/cronograma.xml --wbs gestion/02-planificacion/wbs.csv
Duración total (días laborables): 110  · Fin previsto: 2027-05-03
Camino crítico: A01 -> A03 -> A05 -> A06 -> A07 -> A08 -> A09
id      dur   ES   EF   LS   LF   HT   HL  nombre   (HT holgura total, HL libre, * crítica)
A01      10    0   10    0   10    0    0  Brief PRD UX y arquitectura (BMAD)  *
A02       8    0    8   34   42   34   31  Spike de integración con el núcleo
A03      29   10   39   10   39    0    0  Sprints acceso seguro  *
A04      26   39   65   42   68    3    3  Sprints consulta y constancias
A05      29   39   68   39   68    0    0  Sprints consola de operador  *
A06       0   68   68   68   68    0    0  Release 1 aceptada [hito]  *
A07      31   68   99   68   99    0    0  Sprints solicitudes del socio  *
A08      11   99  110   99  110    0    0  UAT prueba de carga y capacitación  *
A09       0  110  110  110  110    0    0  Puesta en producción [hito]  *
Carga por recurso (días): {'PO + arquitecto': 10, 'Proveedor': 123, 'Usuario sénior': 11}
Gantt escrito en gestion/02-planificacion/cronograma.md
MSPDI escrito en gestion/02-planificacion/cronograma.xml
```

```
$ (reserva de cronograma que calcula pm-cronograma-estimacion: σ del camino crítico = √Σσ² de sus actividades; reserva a 2σ)
Camino crítico: A01 → A03 → A05 → A06 → A07 → A08 → A09
σ = √(1,17² + 3,33² + 3,67² + 3,83² + 1,33²) = 6,51 días
Reserva a 2σ = 13,0 días laborables · tolerancia de tiempo del proyecto ±3 semanas = 15 días laborables (la fija la junta en el paso 5) → la reserva entra en la tolerancia
```

## Paso 4 · Priorización del backlog: MoSCoW, valor y esfuerzo en puntos
```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 10 nuevas, 0 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ (backlog.csv: columnas de gobierno completadas por el PO con pm-agil-hibrido; orden = MoSCoW y luego valor/puntos)
 1 1-3-consulta-de-saldos-de-ahorro-y-préstamos   Must   valor 10 ·  8 pts · valor/pts 1.25 · S2 R1
 2 1-2-recuperación-de-acceso                     Must   valor  6 ·  5 pts · valor/pts 1.20 · S3 R1
 3 3-1-acceso-y-roles-de-la-consola-de-operador   Must   valor  6 ·  5 pts · valor/pts 1.20 · S3 R1
 4 1-1-alta-y-acceso-del-socio-con-segundo-fact   Must   valor  9 ·  8 pts · valor/pts 1.12 · S1 R1
 5 2-1-solicitud-guiada-de-préstamo-simple        Must   valor  9 ·  8 pts · valor/pts 1.12 · S7 R2
 6 3-2-bandeja-única-de-solicitudes               Must   valor  8 ·  8 pts · valor/pts 1.00 · S4 R1
 7 3-3-resolución-de-solicitudes                  Must   valor  8 ·  8 pts · valor/pts 1.00 · S5 R1
 8 1-4-descarga-de-constancias-en-pdf             Should valor  7 ·  5 pts · valor/pts 1.40 · S6 R1
 9 2-2-seguimiento-de-solicitudes-y-respuesta-a   Should valor  6 ·  8 pts · valor/pts 0.75 · S8 R2
10 2-3-actualización-de-datos-de-contacto-con-v   Could  valor  4 ·  5 pts · valor/pts 0.80 · S9 R2
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 10 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ (capacidad del release plan: velocidad 8 × iteraciones; Σ Must+Should ≤ capacidad)
R1 Must    42 pts
R1 Should   5 pts
R2 Could    5 pts
R2 Must     8 pts
R2 Should   8 pts
R1: 6 sprints × 8 = 48 pts de capacidad (Must+Should = 47) · R2: 3 sprints × 8 = 24 pts (Must+Should = 16; con Could = 21)
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto backlog --ruta 02-planificacion/backlog.csv --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto release-plan --ruta 02-planificacion/release-plan.md --estado en-revision
ok
```

## Paso 5 · Presupuesto desde la WBS, tolerancias y autoridad de cambio, línea base de alcance y puertas
```
$ python3 $EST/wbs.py gestion/02-planificacion/wbs.csv --json --profundidad 1
{
  "total_esfuerzo_h": 2480.0,
  "total_costo": 124000.0,
  "hojas": 8,
  "avisos": [],
  "nodos": [
    {
      "codigo": "1",
      "nombre": "Gestión del proyecto",
      "tipo": "producto",
      "responsable": "Martín Suárez",
      "esfuerzo_h": 0.0,
      "costo": 0.0,
      "ref": "",
      "esfuerzo_tot": 400.0,
      "costo_tot": 20000.0
    },
    {
      "codigo": "1.1",
      "nombre": "Gestión de etapas",
      "tipo": "paquete",
      "responsable": "Martín Suárez",
      "esfuerzo_h": 400.0,
      "costo": 20000.0,
      "ref": "",
      "esfuerzo_tot": 400.0,
      "costo_tot": 20000.0
    },
    {
      "codigo": "2",
      "nombre": "Especificación del producto",
      "tipo": "producto",
      "responsable": "Sofía Ramírez",
      "esfuerzo_h": 0.0,
      "costo": 0.0,
      "ref": "",
      "esfuerzo_tot": 240.0,
      "costo_tot": 12000.0
    },
    {
… (111 líneas más)
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto mandato --ruta 00-direccion/mandato.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto project-brief --ruta 01-inicio/project-brief.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-etapa-1 --ruta 02-planificacion/plan-etapa-1.md --estado en-revision
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-inicio
Puerta autorizar-inicio: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-inicio y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-inicio --fecha 2026-10-30
Lista creada: 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md (0 hallazgos automáticos, 5 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-inicio --por "Ejecutivo: Laura Méndez" --fecha 2026-10-30
Lista 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-inicio --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2026-10-30 --fin 2026-11-27
ok
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director).
Aviso: faltan tolerancias de proyecto (tiempo, costo).
```

```
$ python3 $PLUGIN/skills/pm-caso-de-negocio/scripts/inversion.py gestion/00-direccion/flujos-business-case.csv --tasa 0.1 --variacion 0.1
Evaluación de la inversión · tasa 10,0 % por período · base: Línea base
Fórmulas: VAN = Σ F_t/(1+r)^t, t = 0…n · TIR: VAN(TIR) = 0 · repago interpolado en el período en que el acumulado llega a 0

Opción                                      VAN       TIR   Repago Rep. desc.  VAN vs base
Línea base                               39.776    21,0 %     3,00       3,70            0

Línea base · flujos netos: 0: -124.000 | 1: 28.000 | 2: 48.000 | 3: 48.000 | 4: 48.000 | 5: 48.000
  Sensibilidad a la tasa: VAN 49.132 con 8,0 % · 31.172 con 12,0 %
  Sensibilidad por concepto (±10 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    B-01 Desvío de consultas     [beneficio] VAN 22.640 … 56.912 · 76,8 % del valor estimado
    Proyecto (BAC de la WBS)     [inversion] VAN 52.176 … 27.376 · 132,1 % del valor estimado
    Operación y soporte          [costo] VAN 48.116 … 31.436 · 147,7 % del valor estimado
    B-03 Eficiencia de préstamos [beneficio] VAN 32.194 … 47.358 · 47,5 % del valor estimado
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto pid --ruta 00-direccion/pid.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-proyecto --ruta 02-planificacion/plan-proyecto.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia; Should/Could los intercambia el PO" "riesgo=ningún riesgo alto sin respuesta"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto tolerancias-y-autoridad --ruta 00-direccion/tolerancias-y-autoridad.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion presupuesto cambio=12000 limite_autoridad_cambio=10000 --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-beneficios --ruta 00-direccion/enfoque-beneficios.md --estado en-revision
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 0 condición(es) · 2 aviso(s)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  aviso     P-09 registro de interesados vacío: sin matriz poder/interés (pm-interesados)
  aviso     P-10 sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-proyecto --fecha 2026-11-27
Lista creada: 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md (2 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-proyecto --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27
Lista 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-proyecto --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27 
Aviso: registro de interesados vacío: sin matriz poder/interés (pm-interesados)
Aviso: sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
ok
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director). Proyecto ya autorizado: falta autorizar-etapa para la primera etapa de entrega.
```

```
$ python3 $BMAD --proyecto gestion linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"
Línea base bmad-prd v1.0 registrada · sha bc048f7f59a3 · copia congelada en gestion/00-direccion/historial/bmad-prd-v1.0
```

```
$ python3 $BMAD --proyecto gestion linea-base epicas --version 1.0 --por "Ejecutivo: Laura Méndez"
Línea base bmad-epicas v1.0 registrada · sha 3ff846d6f8d9 · copia congelada en gestion/00-direccion/historial/bmad-epicas-v1.0
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar backlog --por "Product owner: Sofía Ramírez" --nivel product-owner --version 1.0 --fecha 2026-11-27
Copia congelada / frozen copy: 00-direccion/historial/backlog-v1.0.csv
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto roadmap --ruta 02-planificacion/visuales/roadmap.md --estado en-revision
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26
Preparación BMAD registrada: PASS
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-etapa-2 --ruta 02-planificacion/plan-etapa-2.md --estado en-revision
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-etapa
Puerta autorizar-etapa: 2 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   E-02 faltan tolerancias de la etapa (--tol o 'tolerancia --nivel etapa')
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-etapa y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa --fecha 2026-11-27
Lista creada: 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md (1 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27
Lista 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27 --etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=±10 %" "costo=±10 %"
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

## Paso 6 · Cambio menor: intercambio de Should/Could por el PO (sin solicitud de cambio)
```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2027-01-08" --campo "decision=Intercambio: 1-4 constancias PDF (Should) pasa a R2 y 2-3 contacto (Could) a R1 por pedido de cumplimiento; sin tocar Must, fecha ni costo" --campo "decidido_por=Product owner: Sofía Ramírez" --campo "nivel=product-owner" --campo "artefactos_afectados=02-planificacion/backlog.csv"
D-009
```

```
$ python3 $BMAD --proyecto gestion handoff
Traspaso emitido → gestion/02-planificacion/especificacion/handoff-bmad-2026-10-20-prioridades.md (10 prioridades cambiadas)
```

## Paso 7 · Cambio de alcance: nueva funcionalidad → análisis de impacto (WBS, esfuerzo, cronograma, costo) → decisión contra el presupuesto de cambio
```
$ python3 $BMAD --proyecto gestion verificar
- [desvio] bmad-prd: contenido distinto de la línea base aprobada → tratar como solicitud de cambio (pm-issues-cambios) salvo elaboración progresiva declarada · agregados ['FR-13'] · retirados []
```

```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2027-01-15" --campo "tipo=solicitud-cambio" --campo "titulo=Agregar FR-13 simulador de préstamo" --campo "descripcion=Pedido del Consejo; detectado como desvío del PRD contra la línea base 1.0" --campo "prioridad=alta" --campo "severidad=mayor" --campo "responsable=Martín Suárez"
I-001
```

```
$ python3 $EST/cpm.py gestion/02-planificacion/escenarios/actividades-C-001.csv --inicio 2026-11-30 --titulo "Escenario con FR-13"
Duración total (días laborables): 121  · Fin previsto: 2027-05-18
Camino crítico: A01 -> A03 -> A05 -> A06 -> A07 -> A10 -> A08 -> A09
id      dur   ES   EF   LS   LF   HT   HL  nombre   (HT holgura total, HL libre, * crítica)
A01      10    0   10    0   10    0    0  Brief PRD UX y arquitectura (BMAD)  *
A02       8    0    8   34   42   34   31  Spike de integración con el núcleo
A03      29   10   39   10   39    0    0  Sprints acceso seguro  *
A04      26   39   65   42   68    3    3  Sprints consulta y constancias
A05      29   39   68   39   68    0    0  Sprints consola de operador  *
A06       0   68   68   68   68    0    0  Release 1 aceptada [hito]  *
A07      31   68   99   68   99    0    0  Sprints solicitudes del socio  *
A10      11   99  110   99  110    0    0  Sprint simulador de préstamo (FR-13)  *
A08      11  110  121  110  121    0    0  UAT prueba de carga y capacitación  *
A09       0  121  121  121  121    0    0  Puesta en producción [hito]  *
Carga por recurso (días): {'PO + arquitecto': 10, 'Proveedor': 134, 'Usuario sénior': 11}
```

```
$ python3 $PLUGIN/skills/pm-caso-de-negocio/scripts/inversion.py gestion/02-planificacion/escenarios/flujos-C-001.csv --tasa 0.1 --variacion 0.1
Evaluación de la inversión · tasa 10,0 % por período · base: Línea base
Fórmulas: VAN = Σ F_t/(1+r)^t, t = 0…n · TIR: VAN(TIR) = 0 · repago interpolado en el período en que el acumulado llega a 0

Opción                                      VAN       TIR   Repago Rep. desc.  VAN vs base
Línea base                               39.776    21,0 %     3,00       3,70            0
Con C-001                                45.939    21,8 %     2,94       3,62        6.163

Línea base · flujos netos: 0: -124.000 | 1: 28.000 | 2: 48.000 | 3: 48.000 | 4: 48.000 | 5: 48.000
  Sensibilidad a la tasa: VAN 49.132 con 8,0 % · 31.172 con 12,0 %
  Sensibilidad por concepto (±10 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    B-01 Desvío de consultas     [beneficio] VAN 22.640 … 56.912 · 76,8 % del valor estimado
    Proyecto (BAC de la WBS)     [inversion] VAN 52.176 … 27.376 · 132,1 % del valor estimado
    Operación y soporte          [costo] VAN 48.116 … 31.436 · 147,7 % del valor estimado
    B-03 Eficiencia de préstamos [beneficio] VAN 32.194 … 47.358 · 47,5 % del valor estimado

Con C-001 · flujos netos: 0: -133.000 | 1: 32.000 | 2: 52.000 | 3: 52.000 | 4: 52.000 | 5: 52.000
  Sensibilidad a la tasa: VAN 56.102 con 8,0 % · 36.591 con 12,0 %
  Sensibilidad por concepto (±10 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    B-01 Desvío de consultas     [beneficio] VAN 28.803 … 63.075 · 73,2 % del valor estimado
    Proyecto (BAC de la WBS)     [inversion] VAN 58.339 … 33.539 · 137,0 % del valor estimado
    Operación y soporte          [costo] VAN 54.279 … 37.599 · 155,1 % del valor estimado
    B-03 Eficiencia de préstamos [beneficio] VAN 38.358 … 53.521 · 39,4 % del valor estimado
    B-03 Simulador (C-001)       [beneficio] VAN 44.423 … 47.455 · ningún valor positivo del concepto lo lleva a 0
    C-001 Simulador de préstamo  [inversion] VAN 46.839 … 45.039 · 610,4 % del valor estimado
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2027-01-16" --campo "solicitante=Consejo directivo (vía Laura Méndez)" --campo "titulo=FR-13 simulador de préstamo" --campo "descripcion=Origen I-001" --campo "justificacion=mejora la conversión de solicitudes (SM-3)" --campo "impacto_alcance=nuevo paquete WBS 3.4 · historia 2-4 · 8 pts" --campo "impacto_tiempo=+11 días laborables en el camino crítico (fin 2027-05-03 → 2027-05-18), dentro de la tolerancia de ±3 semanas" --campo "impacto_costo=+USD 9.000" --campo "impacto_riesgo=la reserva de cronograma a 2σ baja de ≈13 a ≈2 días laborables (riesgo nuevo)" --campo "impacto_beneficios=refuerza B-03 (SM-3): +4.000 por año; VAN del business case 39.776 → 45.939" --campo "recomendacion=aprobar; cargo al presupuesto de cambio (9.000 de 12.000, dentro del límite de 10.000 de la autoridad de cambio); FR-13 como Should en R2" --campo "costo=9000" --campo "cargo=presupuesto-cambio"
C-001
```

```
$ (análisis de impacto de C-001 antes de decidir: pm-issues-cambios con cpm.py, wbs.py, inversion.py, backlog.csv y estado.json)
Objetivo | Antes | Con C-001 | Contra qué se mide | Lectura
Tiempo (camino crítico) | 110 días · fin 2027-05-03 | 121 días · fin 2027-05-18 (+11) | tolerancia del proyecto ±3 semanas = 15 días | dentro: usa 11 de 15 (73 %)
Reserva de cronograma | 2σ = 13,0 días | 13,0 − 11 = 2,0 días | atraso posible del camino crítico | queda casi agotada: registrar riesgo
Costo (BAC) | 124.000 | 133.000 (+9.000) | presupuesto de cambio, no la tolerancia de costo | se paga con el presupuesto de cambio
Presupuesto de cambio | 0 de 12.000 | 9.000 de 12.000 (75 %) | CAM-03: aviso desde 80 %, error sobre 100 % | dentro del saldo
Autoridad | — | 9.000 en un cambio | límite de la autoridad de cambio 10.000 | lo decide la autoridad de cambio
Capacidad del R2 | 21 pts de 24 (3 sprints) | 29 pts de 24 | velocidad 8 pts por sprint | hace falta 1 sprint más (4 sprints = 32 pts)
Business case (VAN a 5 años) | 39.776 | 45.939 (+6.163) | inversion.py, tasa 10 % | a favor: el simulador se paga solo
Lectura: 9.000 ≤ 10.000 y 9.000 ≤ 12.000: está dentro de la autoridad delegada y lo decide Sofía Ramírez (autoridad de cambio). Antes de aprobar, registrar el riesgo de reserva y agregar el sprint 10.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-001 --campo "decision=aprobado" --campo "decidido_por=Autoridad de cambio: Sofía Ramírez" --campo "fecha_decision=2027-01-18" --campo "estado=aprobado"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-001 --campo "estado=pendiente-cambio" --campo "decision=tramitado como C-001" --campo "decidido_por=Autoridad de cambio: Sofía Ramírez"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2027-01-18" --campo "autor=Martín Suárez" --campo "categoria=gestion" --campo "causa=C-001 suma 11 días laborables al camino crítico y deja la reserva de cronograma a 2σ en ≈2 días" --campo "evento=un atraso adicional de más de 2 días laborables en el camino crítico" --campo "efecto=la puesta en producción pasa del 2027-05-18 y consume la tolerancia de tiempo del proyecto (±3 semanas)" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=3" --campo "proximidad=mediano-plazo" --campo "disparador=SPI de un sprint < 0,90 o atraso acumulado ≥ 2 días en el camino crítico" --campo "respuesta=reducir" --campo "acciones=vigilar SPI por sprint con evm.py --guardar; preparar con el PO qué Should/Could salen si se dispara" --campo "propietario=Martín Suárez" --campo "ejecutor=Lucía Benítez" --campo "fecha_revision=2027-02-19" --campo "notas=surge de C-001"
R-001
```

```
$ python3 $EST/wbs.py gestion/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid gestion/02-planificacion/visuales/wbs.md --profundidad 1
Portal de autoservicio para socios: 14 elementos, 9 hojas · esfuerzo 2660 h · costo 133,000
1 Gestión del proyecto [producto] 400 h · 20,000 · Martín Suárez
  1.1 Gestión de etapas [paquete] 400 h · 20,000 · Martín Suárez
2 Especificación del producto [producto] 240 h · 12,000 · Sofía Ramírez
  2.1 Brief PRD UX y arquitectura (BMAD) [paquete] 240 h · 12,000 · Sofía Ramírez
3 Portal del socio [producto] 1420 h · 71,000 · Lucía Benítez
  3.1 Acceso seguro [paquete] 420 h · 21,000 · Lucía Benítez
  3.2 Consulta y constancias [paquete] 380 h · 19,000 · Lucía Benítez
  3.3 Solicitudes del socio [paquete] 440 h · 22,000 · Lucía Benítez
  3.4 Simulador de préstamo (C-001) [paquete] 180 h · 9,000 · Lucía Benítez
4 Consola de operador [producto] 400 h · 20,000 · Lucía Benítez
  4.1 Bandeja y resolución [paquete] 400 h · 20,000 · Lucía Benítez
5 Transición [producto] 200 h · 10,000 · Sofía Ramírez
  5.1 UAT prueba de carga y capacitación [paquete] 200 h · 10,000 · Sofía Ramírez
  5.2 Puesta en producción [hito] 0 h · 0 · Sofía Ramírez
Mermaid escrito en gestion/02-planificacion/visuales/wbs.md
```

```
$ python3 $BMAD --proyecto gestion handoff --cambio C-001
Traspaso emitido → gestion/02-planificacion/especificacion/handoff-bmad-2026-10-20-C-001.md (cambio C-001)
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-18
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 4 AVISO · 3 INFO
  AVISO ESP-10 bmad-prd difiere de su línea base v1.0 y hay un issue/cambio abierto que lo trata.
        → Al aprobarse: bmad.py linea-base con versión mayor.
  AVISO ESP-13 Traspaso a BMAD sin confirmar: 02-planificacion/especificacion/handoff-bmad-2026-10-20-prioridades.md.
  AVISO ESP-13 Traspaso a BMAD sin confirmar: 02-planificacion/especificacion/handoff-bmad-2026-10-20-C-001.md.
        → Cuando el equipo BMAD lo aplique: marcar estado: aplicado en el documento, bmad.py verificar y nueva línea base.
  AVISO ESP-14 requisitos-bmad.csv no coincide con el PRD vigente (desactualizado o editado).
        → bmad.py requisitos (es derivado: no se edita).
  INFO  CAM-03 Presupuesto de cambio: 9.000 de 12.000 (75 %).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

## Paso 8 · El equipo BMAD aplica el cambio → nuevas líneas base → roadmap actualizado
```
$ python3 $BMAD --proyecto gestion requisitos
43 identificadores · {'UJ': 3, 'FR': 13, 'NFR': 6, 'SM': 8, 'AD': 13} → gestion/02-planificacion/especificacion/requisitos-bmad.csv (derivado: no editar)
```

```
$ python3 $BMAD --proyecto gestion trazabilidad --wbs 02-planificacion/wbs.csv
19 requisitos trazados → gestion/02-planificacion/especificacion/matriz-trazabilidad-bmad.csv
  Requisitos funcionales sin historia: ninguno
  Historias sin requisito: ninguna
  Trazados solo a nivel de épica (epics.md no cita el id en la historia): FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12
  Referencias de la WBS a ids inexistentes: ninguna
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 1 nuevas, 10 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ (cobertura de trazabilidad recalculada en esta sincronización: matriz-trazabilidad-bmad.csv, backlog.csv y descripciones de producto)
Requisitos (FR) con historia: 13 de 13 (100 %) · bmad.py trazabilidad
Requisitos (FR) con paquete de la WBS: 13 de 13 (100 %) · columna ref de wbs.csv
Historias con producto de la PBS: 11 de 11 (100 %) · columna producto_pbs
NFR con WBS o criterio de calidad: 6 de 6 (100 %) · WBS o descripciones de producto
Requisitos (FR) citados en su historia: 1 de 13 (8 %) · el resto, solo a nivel de épica
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto roadmap --ruta 02-planificacion/visuales/roadmap.md --estado en-revision
ok
```

```
$ python3 $BMAD --proyecto gestion linea-base prd --version 1.1 --por "Ejecutivo: Laura Méndez"
Línea base bmad-prd v1.1 registrada · sha 089472ba0219 · copia congelada en gestion/00-direccion/historial/bmad-prd-v1.1
```

```
$ python3 $BMAD --proyecto gestion linea-base epicas --version 1.1 --por "Ejecutivo: Laura Méndez"
Línea base bmad-epicas v1.1 registrada · sha acca7ef6e6b2 · copia congelada en gestion/00-direccion/historial/bmad-epicas-v1.1
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-001 --campo "estado=implementado"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-001 --campo "estado=cerrado" --campo "fecha_cierre=2027-01-25"
ok
```

```
$ python3 $BMAD --proyecto gestion verificar
Sin desvíos: la especificación coincide con las líneas base registradas.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-25
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 3 INFO
  INFO  CAM-03 Presupuesto de cambio: 9.000 de 12.000 (75 %).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

## Paso 9 · Avance del alcance: EVM ágil (alcance no entregable) e informe
```
$ python3 $BMAD --proyecto gestion avance
Historias 11 · backlog 7 · ready-for-dev 0 · in-progress 0 · review 0 · done 4 · épicas terminadas 0/3 · 34.2 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 11 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 1 parcial · historias 1-1, 1-2, 1-3 y 3-1 (productos 3.1, 3.2 y 4.1)" --campo "metodo_verificacion=revision" --campo "criterios=EC-01 a EC-04 de la descripción de producto 3.1 y criterios de aceptación de cada historia" --campo "responsable_productor=Lucía Benítez" --campo "revisores=QA del proveedor; Andrea Costa (aseguramiento)" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-01-28" --campo "fecha_real=2027-01-28" --campo "resultado=aprobado" --campo "estado=completada"
Q-001
```

```
$ python3 $EST/evm.py --pv 60000 --ev 52000 --ac 58000 --bac 133000 --modo agil --pct-no-must 20 --proyecto gestion --guardar --corte 2027-01-29
Guardado: 03-control/reportes/evm-2027-01-29.json
PV                     60,000.000
EV                     52,000.000
AC                     58,000.000
BAC                    133,000.000
SV                     -8,000.000
CV                     -6,000.000
SPI                    0.867
CPI                    0.897
pct_completado         0.391
pct_gastado            0.436
EAC_tendencia          148,346.154
EAC_atipico            139,000.000
EAC_compuesto          162,245.562
EAC_usado              tendencia
ETC                    90,346.154
VAC                    -15,346.154
VAC_pct                -11.538
sobrecosto_pct         11.538
TCPI_bac               1.080
TCPI_eac               0.897
semaforo_cronograma    n/a-agil
semaforo_costo         n/a-agil
base_semaforo          alcance-agil
alcance_no_entregable_pct 10.345
semaforo_alcance       ambar
excepcion_prevista     False
Modo ágil (costo y fecha fijos): un EAC > BAC significa que, al ritmo actual, no se entregará todo el alcance con el presupuesto; leerlo como alcance pronosticado (ítems Must/Should que no entran) y comparar contra la tolerancia de ALCANCE, no como sobrecosto. Hay excepción si los ítems Must no entran.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-001 --campo "estado=en-seguimiento" --campo "notas=surge de C-001 · disparador activado el 2027-01-29 (SPI 0,867 < 0,90): el PO prepara qué Should/Could salen si el atraso sigue"
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-29
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 3 INFO
  INFO  CAM-03 Presupuesto de cambio: 9.000 de 12.000 (75 %).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
  INFO  TOL-02 El EVM del 2027-01-29 está en ámbar (costo=n/a-agil, cronograma=n/a-agil, alcance=ambar): 50–100 % de la tolerancia.
        → Anticipar acciones correctivas y reportarlo en el highlight.
```

```
$ python3 $EST/puertas.py --proyecto gestion estado --markdown
### Puertas y verificación / Gates and verification

| Puerta | Fecha | Decisión | Por | Condiciones (estado) | Observaciones de la verificación | Lista |
|---|---|---|---|---|---|---|
| autorizar-inicio | 2026-10-30 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md |
| autorizar-proyecto | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md |
| autorizar-etapa | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md |

**Próxima puerta / Next gate: autorizar-etapa** — 2 bloqueo(s), 0 condición(es), 0 aviso(s).
- bloqueo: E-01 falta el plan de la etapa a autorizar (plan-etapa-3)
- bloqueo: E-04 falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
```

## Paso 10 · Excepción: un requisito regulatorio supera la autoridad y el presupuesto de cambio, y el EVM pronostica salir de la tolerancia
```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2027-02-15" --campo "autor=Martín Suárez" --campo "tipo=solicitud-cambio" --campo "titulo=Requisito regulatorio: consentimiento informado y consulta del registro de accesos por el socio" --campo "descripcion=Resultado de la revisión normativa supuesta en NFR-1 (Ley 18.331); pedido del Consejo directivo" --campo "prioridad=urgente" --campo "severidad=mayor" --campo "responsable=Martín Suárez"
I-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2027-02-16" --campo "solicitante=Consejo directivo (requisito regulatorio, vía Laura Méndez)" --campo "titulo=Consentimiento informado y registro de accesos consultable por el socio" --campo "descripcion=Origen I-002; refuerza NFR-1 y NFR-5" --campo "justificacion=obligatorio por regulación" --campo "impacto_alcance=nuevo paquete WBS 3.5 · 13 pts Must en R1" --campo "impacto_tiempo=+1 sprint en la etapa 2 (fin 2027-03-05 → 2027-03-19)" --campo "impacto_costo=+USD 15.000" --campo "impacto_riesgo=sin él, riesgo regulatorio de no poder salir a producción" --campo "impacto_beneficios=condición para salir a producción y para B-02 (adopción); sin beneficio propio" --campo "recomendacion=aprobar: es obligatorio; Must en R1" --campo "costo=15000" --campo "cargo=presupuesto-cambio"
C-002
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-002 --campo "decision=aprobado" --campo "estado=aprobado" --campo "decidido_por=Autoridad de cambio: Sofía Ramírez" --campo "fecha_decision=2027-02-17"

Control de cambios (PRINCE2, autoridad y presupuesto de cambio; no se omite con --forzar):
  - C-002: costo 15.000 supera el límite de la autoridad de cambio (10.000).
  - C-002: el presupuesto de cambio no alcanza: 9.000 ya cargados + 15.000 = 24.000 de 12.000 fijados por la junta.
  → 'Autoridad de cambio: Sofía Ramírez' no es la junta ni el ejecutivo. Dejar estado=pendiente-decision (sin decision=aprobado) y escalar a pm-director: decide la junta o el ejecutivo.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-002 --campo "estado=pendiente-decision" --campo "notas=la autoridad de cambio quiso aprobarlo el 2027-02-17; supera su límite de 10.000 y el saldo del presupuesto de cambio (registro.py lo rechazó): decide la junta"
ok
```

```
$ python3 $EST/evm.py --pv 75000 --ev 60000 --ac 77000 --bac 133000 --modo agil --pct-no-must 20 --proyecto gestion --guardar --corte 2027-02-19
Guardado: 03-control/reportes/evm-2027-02-19.json
PV                     75,000.000
EV                     60,000.000
AC                     77,000.000
BAC                    133,000.000
SV                     -15,000.000
CV                     -17,000.000
SPI                    0.800
CPI                    0.779
pct_completado         0.451
pct_gastado            0.579
EAC_tendencia          170,683.333
EAC_atipico            150,000.000
EAC_compuesto          194,104.167
EAC_usado              tendencia
ETC                    93,683.333
VAC                    -37,683.333
VAC_pct                -28.333
sobrecosto_pct         28.333
TCPI_bac               1.304
TCPI_eac               0.779
semaforo_cronograma    n/a-agil
semaforo_costo         n/a-agil
base_semaforo          alcance-agil
alcance_no_entregable_pct 22.078
semaforo_alcance       rojo
excepcion_prevista     True
Modo ágil (costo y fecha fijos): un EAC > BAC significa que, al ritmo actual, no se entregará todo el alcance con el presupuesto; leerlo como alcance pronosticado (ítems Must/Should que no entran) y comparar contra la tolerancia de ALCANCE, no como sobrecosto. Hay excepción si los ítems Must no entran.
→ Pronóstico fuera de tolerancia: preparar informe de excepción (pm-progreso-reportes) y escalar a pm-director.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-19
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 1 INFO
  AVISO TOL-01 El EVM del 2027-02-19 pronostica salir de la tolerancia (costo=n/a-agil, cronograma=n/a-agil, alcance=rojo) y no hay excepción abierta.
        → pm-progreso-reportes: informe de excepción; pm-director: estado.py limite-etapa --excepcion X-### y puerta autorizar-plan-excepcion.
  INFO  CAM-03 Presupuesto de cambio: 9.000 de 12.000 (75 %).
```

```
$ python3 $PLUGIN/skills/pm-caso-de-negocio/scripts/inversion.py gestion/02-planificacion/escenarios/flujos-C-002.csv --tasa 0.1 --variacion 0.1 --base "Con C-001"
Evaluación de la inversión · tasa 10,0 % por período · base: Con C-001
Fórmulas: VAN = Σ F_t/(1+r)^t, t = 0…n · TIR: VAN(TIR) = 0 · repago interpolado en el período en que el acumulado llega a 0

Opción                                      VAN       TIR   Repago Rep. desc.  VAN vs base
Línea base                               39.776    21,0 %     3,00       3,70       -6.163
Con C-001                                45.939    21,8 %     2,94       3,62            0
Con C-001 y C-002                        30.939    17,3 %     3,23       4,04      -15.000

Línea base · flujos netos: 0: -124.000 | 1: 28.000 | 2: 48.000 | 3: 48.000 | 4: 48.000 | 5: 48.000
  Sensibilidad a la tasa: VAN 49.132 con 8,0 % · 31.172 con 12,0 %
  Sensibilidad por concepto (±10 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    B-01 Desvío de consultas        [beneficio] VAN 22.640 … 56.912 · 76,8 % del valor estimado
    Proyecto (BAC de la WBS)        [inversion] VAN 52.176 … 27.376 · 132,1 % del valor estimado
    Operación y soporte             [costo] VAN 48.116 … 31.436 · 147,7 % del valor estimado
    B-03 Eficiencia de préstamos    [beneficio] VAN 32.194 … 47.358 · 47,5 % del valor estimado

Con C-001 · flujos netos: 0: -133.000 | 1: 32.000 | 2: 52.000 | 3: 52.000 | 4: 52.000 | 5: 52.000
  Sensibilidad a la tasa: VAN 56.102 con 8,0 % · 36.591 con 12,0 %
  Sensibilidad por concepto (±10 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    B-01 Desvío de consultas        [beneficio] VAN 28.803 … 63.075 · 73,2 % del valor estimado
    Proyecto (BAC de la WBS)        [inversion] VAN 58.339 … 33.539 · 137,0 % del valor estimado
    Operación y soporte             [costo] VAN 54.279 … 37.599 · 155,1 % del valor estimado
    B-03 Eficiencia de préstamos    [beneficio] VAN 38.358 … 53.521 · 39,4 % del valor estimado
    B-03 Simulador (C-001)          [beneficio] VAN 44.423 … 47.455 · ningún valor positivo del concepto lo lleva a 0
    C-001 Simulador de préstamo     [inversion] VAN 46.839 … 45.039 · 610,4 % del valor estimado

Con C-001 y C-002 · flujos netos: 0: -148.000 | 1: 32.000 | 2: 52.000 | 3: 52.000 | 4: 52.000 | 5: 52.000
  Sensibilidad a la tasa: VAN 41.102 con 8,0 % · 21.591 con 12,0 %
  Sensibilidad por concepto (±10 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    B-01 Desvío de consultas        [beneficio] VAN 13.803 … 48.075 · 81,9 % del valor estimado
    Proyecto (BAC de la WBS)        [inversion] VAN 43.339 … 18.539 · 125,0 % del valor estimado
    Operación y soporte             [costo] VAN 39.279 … 22.599 · 137,1 % del valor estimado
    B-03 Eficiencia de préstamos    [beneficio] VAN 23.358 … 38.521 · 59,2 % del valor estimado
    B-03 Simulador (C-001)          [beneficio] VAN 29.423 … 32.455 · ningún valor positivo del concepto lo lleva a 0
    C-002 Consentimiento y registro [inversion] VAN 32.439 … 29.439 · 306,3 % del valor estimado
    C-001 Simulador de préstamo     [inversion] VAN 31.839 … 30.039 · 443,8 % del valor estimado
```

```
$ (análisis de impacto de C-002 antes de decidir: pm-issues-cambios con backlog.csv, evm-2027-02-19.json, inversion.py y estado.json)
Objetivo | Antes | Con C-002 | Contra qué se mide | Lectura
Presupuesto de cambio | 9.000 de 12.000 (75 %) | 24.000 de 12.000 (200 %) | saldo fijado por la junta (registro.py; CAM-03) | no alcanza: hace falta otra fuente o ampliarlo
Autoridad | límite 10.000 por cambio | 15.000 en un cambio | límite delegado a la autoridad de cambio | excedida: registro.py rechazó su aprobación
Capacidad del R1 | 47 pts de 48 (6 sprints) | 60 pts; sin la 2-3 (Could, 5): 55 pts | velocidad 8 pts por sprint | 7 sprints: +1 sprint (14 días corridos)
Tiempo de la etapa 2 | fin 2027-03-05 (98 días corridos desde 2026-11-27) | fin 2027-03-19 (+14) | tolerancia de etapa ±10 % = 9,8 días | fuera de tolerancia
Alcance (EVM del 19/2) | Should/Could = 20 % del alcance | no entra 22,1 % | Must sin tolerancia | los Must peligran
Business case (VAN a 5 años) | 45.939 · B-01 puede caer 27 % | 30.939 · B-01 puede caer 18 % | VAN > 0 · tolerancia de beneficios −10 % | sigue justificado, con menos margen
Fin del proyecto | 2027-05-18 (con C-001) | lo recalcula el plan de proyecto con el plan de excepción | ±3 semanas | no se recalcula en esta corrida
Lectura: supera el límite delegado, el saldo del presupuesto de cambio y la tolerancia de tiempo de la etapa: no le corresponde a la autoridad de cambio (queda pendiente-decision). Se gestiona por excepción: informe a la junta.
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto informe-excepcion-X-001 --ruta 03-control/reportes/2027-02-19-informe-excepcion-X-001.md --estado en-revision
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2027-02-19" --campo "autor=Martín Suárez" --campo "tipo=problema-preocupacion" --campo "titulo=Excepción X-001: cambio fuera de la autoridad delegada y pronóstico fuera de tolerancia de alcance" --campo "descripcion=C-002 supera el límite de la autoridad de cambio y el saldo del presupuesto de cambio (pendiente-decision); EVM del 2027-02-19 con excepcion_prevista" --campo "prioridad=urgente" --campo "severidad=critica" --campo "responsable=Martín Suárez" --campo "estado=escalado" --campo "notas=informe 03-control/reportes/2027-02-19-informe-excepcion-X-001.md"
I-003
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-002 --campo "estado=escalado" --campo "decision=C-002 escalado a la junta (excepción X-001)"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion puerta decision-ad-hoc --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2027-02-22 --condiciones "X-001: la junta pide plan de excepción para la etapa 2; C-002 queda sujeto a ese plan"
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
Condiciones abiertas: decision-ad-hoc: X-001: la junta pide plan de excepción para la etapa 2; C-002 queda sujeto a ese plan
```

```
$ python3 $EST/estado.py --proyecto gestion limite-etapa --excepcion X-001
ok
Fase: entrega · Proceso: SB · Etapa 2: Release 1 · Enfoque: hibrido
Límite de etapa por excepción X-001: plan de excepción (reemplaza el plan vigente), actualizar plan de proyecto, business case y riesgos. Puerta: autorizar-plan-excepcion (pm-director).
Condiciones abiertas: decision-ad-hoc: X-001: la junta pide plan de excepción para la etapa 2; C-002 queda sujeto a ese plan
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-excepcion-X-001 --ruta 02-planificacion/plan-excepcion-X-001.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion cumplir-condiciones decision-ad-hoc --fecha 2027-02-24 --por "Ejecutiva: Laura Méndez" --nota "plan de excepción X-001 y business case actualizado presentados; C-002 se decide con ellos"
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-plan-excepcion
Puerta autorizar-plan-excepcion: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-plan-excepcion y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/estado.py --proyecto gestion presupuesto cambio=32000 --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-002 --campo "decision=aprobado" --campo "estado=aprobado" --campo "decidido_por=Junta: Laura Méndez (ejecutiva) · plan de excepción X-001" --campo "fecha_decision=2027-02-26" --campo "notas=la autoridad de cambio no podía aprobarlo (límite de 10.000 y saldo del presupuesto de cambio); lo aprueba la junta con el presupuesto de cambio ampliado a 32.000 (plan de excepción X-001)"
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-plan-excepcion
Puerta autorizar-plan-excepcion: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-plan-excepcion y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-plan-excepcion --fecha 2027-02-26
Lista creada: 00-direccion/decisiones/2027-02-26-verificacion-autorizar-plan-excepcion.md (0 hallazgos automáticos, 3 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-plan-excepcion --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26
Lista 00-direccion/decisiones/2027-02-26-verificacion-autorizar-plan-excepcion.md confirmada por Ejecutiva: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-plan-excepcion --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26 --fin 2027-03-19
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-003 --campo "estado=cerrado" --campo "fecha_cierre=2027-02-26" --campo "decision=plan de excepción X-001 autorizado" --campo "decidido_por=Ejecutiva: Laura Méndez"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-002 --campo "estado=pendiente-cambio" --campo "decision=tramitado como C-002 (aprobado por la junta)" --campo "decidido_por=Ejecutiva: Laura Méndez"
ok
```

```
$ python3 $EST/wbs.py gestion/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid gestion/02-planificacion/visuales/wbs.md --profundidad 1
Portal de autoservicio para socios: 15 elementos, 10 hojas · esfuerzo 2960 h · costo 148,000
1 Gestión del proyecto [producto] 400 h · 20,000 · Martín Suárez
  1.1 Gestión de etapas [paquete] 400 h · 20,000 · Martín Suárez
2 Especificación del producto [producto] 240 h · 12,000 · Sofía Ramírez
  2.1 Brief PRD UX y arquitectura (BMAD) [paquete] 240 h · 12,000 · Sofía Ramírez
3 Portal del socio [producto] 1720 h · 86,000 · Lucía Benítez
  3.1 Acceso seguro [paquete] 420 h · 21,000 · Lucía Benítez
  3.2 Consulta y constancias [paquete] 380 h · 19,000 · Lucía Benítez
  3.3 Solicitudes del socio [paquete] 440 h · 22,000 · Lucía Benítez
  3.4 Simulador de préstamo (C-001) [paquete] 180 h · 9,000 · Lucía Benítez
  3.5 Consentimiento y registro de accesos (C-002) [paquete] 300 h · 15,000 · Lucía Benítez
4 Consola de operador [producto] 400 h · 20,000 · Lucía Benítez
  4.1 Bandeja y resolución [paquete] 400 h · 20,000 · Lucía Benítez
5 Transición [producto] 200 h · 10,000 · Sofía Ramírez
  5.1 UAT prueba de carga y capacitación [paquete] 200 h · 10,000 · Sofía Ramírez
  5.2 Puesta en producción [hito] 0 h · 0 · Sofía Ramírez
Mermaid escrito en gestion/02-planificacion/visuales/wbs.md
```

```
$ python3 $BMAD --proyecto gestion handoff --cambio C-002
Traspaso emitido → gestion/02-planificacion/especificacion/handoff-bmad-2026-10-20-C-002.md (cambio C-002 · 1 prioridades cambiadas)
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-26
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 2 AVISO · 2 INFO
  AVISO ESP-13 Traspaso a BMAD sin confirmar: 02-planificacion/especificacion/handoff-bmad-2026-10-20-C-002.md.
        → Cuando el equipo BMAD lo aplique: marcar estado: aplicado en el documento, bmad.py verificar y nueva línea base.
  AVISO REG-09 Riesgo R-001 abierto con la revisión vencida (2027-02-19; propietario: Martín Suárez).
        → Revisarlo con el propietario (pm-riesgos) y actualizar estado, evaluación y fecha_revision (registro.py actualizar riesgos R-… --campo fecha_revision=…).
  INFO  CAM-03 Presupuesto de cambio: 24.000 de 32.000 (75 %).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-001 --campo "probabilidad=4" --campo "fecha_revision=2027-03-19" --campo "notas=surge de C-001 · disparador activado el 2027-01-29 (SPI 0,867) · revisado el 2027-02-26: SPI 0,80 al 19/2 y C-002 suma un sprint a la etapa 2; probabilidad 3 → 4; próxima revisión al fin de la etapa (plan de excepción X-001)"
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-26
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 1 INFO
  AVISO ESP-13 Traspaso a BMAD sin confirmar: 02-planificacion/especificacion/handoff-bmad-2026-10-20-C-002.md.
        → Cuando el equipo BMAD lo aplique: marcar estado: aplicado en el documento, bmad.py verificar y nueva línea base.
  INFO  CAM-03 Presupuesto de cambio: 24.000 de 32.000 (75 %).
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Portal de autoservicio para socios · entrega/CS · etapa 2 Release 1 (2026-11-27 → 2027-03-19) · enfoque hibrido · idioma es
Autorizado: sí
Roles: ejecutivo=Laura Méndez; usuario_senior=Sofía Ramírez; proveedor_senior=Diego Ferreira; gestor_proyecto=Martín Suárez; aseguramiento=Andrea Costa; autoridad_cambio=Sofía Ramírez; product_owner=Sofía Ramírez; jefes_equipo=Lucía Benítez
Tolerancias: proyecto: tiempo=±3 semanas, costo=±8 %, alcance=Must sin tolerancia; Should/Could los intercambia el PO, riesgo=ningún riesgo alto sin respuesta | etapa: tiempo=±10 %, costo=±10 %
Presupuestos: cambio=32000, limite_autoridad_cambio=10000
Artefactos: 20 (3 aprobados)
Última puerta: autorizar-plan-excepcion · aprobado · 2027-02-26 · Ejecutiva: Laura Méndez
Próxima puerta: autorizar-etapa · 2 bloqueo(s) · 0 condición(es) (detalle: puertas.py verificar autorizar-etapa)
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

```
$ python3 $EST/registro.py --proyecto gestion listar cambios
id=C-001 | fecha=2027-01-16 | solicitante=Consejo directivo (vía Laura Méndez) | titulo=FR-13 simulador de préstamo | descripcion=Origen I-001 | justificacion=mejora la conversión de solicitudes (SM-3) | impacto_alcance=nuevo paquete WBS 3.4 · historia 2-4 · 8 pts | impacto_tiempo=+11 días laborables en el camino crítico (fin 2027-05-03 → 2027-05-18), dentro de la tolerancia de ±3 semanas | impacto_costo=+USD 9.000 | impacto_riesgo=la reserva de cronograma a 2σ baja de ≈13 a ≈2 días laborables (riesgo nuevo) | impacto_beneficios=refuerza B-03 (SM-3): +4.000 por año; VAN del business case 39.776 → 45.939 | recomendacion=aprobar; cargo al presupuesto de cambio (9.000 de 12.000, dentro del límite de 10.000 de la autoridad de cambio); FR-13 como Should en R2 | decision=aprobado | decidido_por=Autoridad de cambio: Sofía Ramírez | fecha_decision=2027-01-18 | estado=implementado | costo=9000 | cargo=presupuesto-cambio
id=C-002 | fecha=2027-02-16 | solicitante=Consejo directivo (requisito regulatorio, vía Laura Méndez) | titulo=Consentimiento informado y registro de accesos consultable por el socio | descripcion=Origen I-002; refuerza NFR-1 y NFR-5 | justificacion=obligatorio por regulación | impacto_alcance=nuevo paquete WBS 3.5 · 13 pts Must en R1 | impacto_tiempo=+1 sprint en la etapa 2 (fin 2027-03-05 → 2027-03-19) | impacto_costo=+USD 15.000 | impacto_riesgo=sin él, riesgo regulatorio de no poder salir a producción | impacto_beneficios=condición para salir a producción y para B-02 (adopción); sin beneficio propio | recomendacion=aprobar: es obligatorio; Must en R1 | decision=aprobado | decidido_por=Junta: Laura Méndez (ejecutiva) · plan de excepción X-001 | fecha_decision=2027-02-26 | estado=aprobado | notas=la autoridad de cambio no podía aprobarlo (límite de 10.000 y saldo del presupuesto de cambio); lo aprueba la junta con el presupuesto de cambio ampliado a 32.000 (plan de excepción X-001) | costo=15000 | cargo=presupuesto-cambio
```

