## Paso 1 · Proyecto, especificación y enunciado de alcance
```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez"
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

## Paso 2 · Estructura de productos (PBS) y WBS con diccionario, trazada a requisitos e historias
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
$ python3 $EST/sanidad.py --proyecto gestion --rapido
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
$ (σ del camino crítico = √Σσ² de las actividades críticas; reserva a 2σ)

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

## Paso 5 · Presupuesto desde la WBS, línea base de alcance y puerta autorizar-proyecto
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
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-inicio y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-inicio
Lista creada: 00-direccion/decisiones/2026-10-17-verificacion-autorizar-inicio.md (0 hallazgos automáticos, 5 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-inicio --por "Ejecutivo: Laura Méndez"
Lista 00-direccion/decisiones/2026-10-17-verificacion-autorizar-inicio.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-inicio --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2026-10-30 --fin 2026-11-27
ok
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director).
Aviso: faltan tolerancias de proyecto (tiempo, costo).
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
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-proyecto
Lista creada: 00-direccion/decisiones/2026-10-17-verificacion-autorizar-proyecto.md (0 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-proyecto --por "Ejecutivo: Laura Méndez"
Lista 00-direccion/decisiones/2026-10-17-verificacion-autorizar-proyecto.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-proyecto --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27 
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
  BLOQUEO   faltan tolerancias de la etapa (--tol o 'tolerancia --nivel etapa')
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-etapa y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa
Lista creada: 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md (1 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutivo: Laura Méndez"
Lista 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md confirmada por Ejecutivo: Laura Méndez
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
D-008
```

```
$ python3 $BMAD --proyecto gestion handoff
Traspaso emitido → gestion/02-planificacion/especificacion/handoff-bmad-2026-10-17-prioridades.md (10 prioridades cambiadas)
```

## Paso 7 · Cambio de alcance: nueva funcionalidad → análisis de impacto (WBS, esfuerzo, cronograma, costo) → decisión
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
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2027-01-16" --campo "solicitante=Consejo directivo (vía Laura Méndez)" --campo "titulo=FR-13 simulador de préstamo" --campo "descripcion=Origen I-001" --campo "justificacion=mejora la conversión de solicitudes (SM-3)" --campo "impacto_alcance=nuevo paquete WBS 3.4 · historia 2-4 · 8 pts" --campo "impacto_tiempo=+11 días laborables en el camino crítico (fin 2027-05-03 → 2027-05-18), dentro de la tolerancia de ±3 semanas" --campo "impacto_costo=+USD 9.000" --campo "impacto_riesgo=ninguno nuevo" --campo "impacto_beneficios=refuerza B-03 (SM-3)" --campo "recomendacion=aprobar; costo contra la contingencia; FR-13 como Should en R2"
C-001
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
Traspaso emitido → gestion/02-planificacion/especificacion/handoff-bmad-2026-10-17-C-001.md (cambio C-001)
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
$ python3 $EST/sanidad.py --proyecto gestion --rapido
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 1 INFO
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

## Paso 9 · Avance del alcance: EVM ágil (alcance no entregable) e informe
```
$ python3 $BMAD --proyecto gestion avance
Historias 11 · backlog 7 · ready-for-dev 0 · in-progress 0 · review 0 · done 4 · épicas terminadas 0/3 · 34.2 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $EST/evm.py --pv 60000 --ev 52000 --ac 58000 --bac 133000 --modo agil --pct-no-must 20 --proyecto gestion
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
$ python3 $EST/puertas.py --proyecto gestion estado --markdown
### Puertas y verificación / Gates and verification

| Puerta | Fecha | Decisión | Por | Condiciones (estado) | Observaciones de la verificación | Lista |
|---|---|---|---|---|---|---|
| autorizar-inicio | 2026-10-30 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-17-verificacion-autorizar-inicio.md |
| autorizar-proyecto | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-17-verificacion-autorizar-proyecto.md |
| autorizar-etapa | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md |

**Próxima puerta / Next gate: autorizar-etapa** — 2 bloqueo(s), 0 condición(es), 0 aviso(s).
- bloqueo: falta el plan de la etapa a autorizar (plan-etapa-3)
- bloqueo: falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
```

