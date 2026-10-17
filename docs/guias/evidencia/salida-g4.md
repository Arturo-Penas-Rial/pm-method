## Paso 1 · Proyecto y detección de BMAD
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
$ python3 $EST/estado.py --proyecto gestion integracion especificacion=bmad
ok
```

## Paso 2 · Idea → brief de producto (BMAD) → mandato y project brief (pm-method)
```
$ python3 $BMAD --proyecto gestion inventario
BMAD v6 (soportada) en <repo>
  brief              1 archivo(s) · estado=final · 2026-10-17T11:07 · sha 58db1efac463 · _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md
  prd                1 archivo(s) · estado=final · 2026-10-17T11:07 · sha bc048f7f59a3 · _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md
  arquitectura       1 archivo(s) · estado=final · 2026-10-17T11:07 · sha 9a0a63b20794 · _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md
  epicas             1 archivo(s) · estado=final · 2026-10-17T11:07 · sha 3ff846d6f8d9 · _bmad-output/planning-artifacts/epics.md
  estado-sprint      1 archivo(s) · estado=- · 2026-10-17T11:07 · sha 519bd23ac20a · _bmad-output/implementation-artifacts/sprint-status.yaml
  historias          1 archivo(s) · estado=ready-for-dev · 2026-10-17T11:07 · sha 16b91b8717ea · _bmad-output/implementation-artifacts/spec-1-1-alta-y-acceso-del-socio-con-segundo-factor.md
Inventario escrito en gestion/02-planificacion/especificacion/inventario-bmad.json
```

```
$ python3 $EST/especificacion.py --proyecto gestion fuente
Proveedor de especificación: bmad · índice reconstruido ahora (2026-10-17T18:51:34)
  dueño de requisitos, épicas, historias, estado de desarrollo: BMAD (solo lectura)
  dueño de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs): pm-method backlog.csv
  dueño de paquetes_wbs: pm-method wbs.csv (columna ref)
  BMAD v6 · soporte soportada · líneas base: ninguna
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
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-10-20" --campo "decision=Enfoque híbrido: etapas PRINCE2; especificación con BMAD; sprints de 14 días como paquetes" --campo "decidido_por=Ejecutivo: Laura Méndez" --campo "nivel=junta"
D-001
```

## Paso 3 · Junta, tolerancias, business case esquemático y puerta autorizar-inicio
```
$ python3 $EST/estado.py --proyecto gestion rol usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" product_owner="Sofía Ramírez" autoridad_cambio="Sofía Ramírez" aseguramiento="Andrea Costa" jefes_equipo="Lucía Benítez"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion agil cadencia_iteracion_dias=14 velocidad_referencia=8
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case-esquematico --ruta 00-direccion/business-case-esquematico.md --estado en-revision
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

## Paso 4 · PRD, UX y arquitectura (BMAD) → requisitos en la fachada
```
$ python3 $BMAD --proyecto gestion requisitos
42 identificadores · {'UJ': 3, 'FR': 12, 'NFR': 6, 'SM': 8, 'AD': 13} → gestion/02-planificacion/especificacion/requisitos-bmad.csv (derivado: no editar)
```

```
$ python3 $EST/especificacion.py --proyecto gestion resumen
requisitos: 42
historias: 10
por_estado: {'backlog': 9, 'ready-for-dev': 1, 'in-progress': 0, 'review': 0, 'done': 0}
```

```
$ python3 $EST/especificacion.py --proyecto gestion consultar FR-6
tipo_entidad: requisito
id: FR-6
tipo: FR
titulo: Solicitud guiada de préstamo simple
fuente: _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md
linea: 130
historias: ['2-1-solicitud-guiada-de-préstamo-simple', '2-2-seguimiento-de-solicitudes-y-respuesta-a-pedidos-de-informac', '2-3-actualización-de-datos-de-contacto-con-verificación']
nivel_traza: epica
epicas: ['E-2']
cobertura: planificado
```

## Paso 5 · Épicas e historias (BMAD) → WBS por productos y trazabilidad
```
$ python3 $EST/wbs.py gestion/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --mermaid gestion/02-planificacion/visuales/wbs.md
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

## Paso 6 · Backlog con columnas de gobierno, MoSCoW y release plan
```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 10 nuevas, 0 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 10 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ (columnas de gobierno de backlog.csv completadas por pm-agil-hibrido: prioridad, moscow, estimacion, iteracion, release, producto_pbs)
1-1-alta-y-acceso-del-socio-con-segundo-   Must      8 pts  S1  R1  WBS 3.1
1-2-recuperación-de-acceso                 Must      5 pts  S1  R1  WBS 3.1
1-3-consulta-de-saldos-de-ahorro-y-prést   Must      8 pts  S2  R1  WBS 3.2
1-4-descarga-de-constancias-en-pdf         Should    5 pts  S2  R1  WBS 3.2
2-1-solicitud-guiada-de-préstamo-simple    Must      8 pts  S5  R2  WBS 3.3
2-2-seguimiento-de-solicitudes-y-respues   Should    8 pts  S6  R2  WBS 3.3
2-3-actualización-de-datos-de-contacto-c   Could     5 pts  S6  R2  WBS 3.3
3-1-acceso-y-roles-de-la-consola-de-oper   Must      5 pts  S3  R1  WBS 4.1
3-2-bandeja-única-de-solicitudes           Must      8 pts  S3  R1  WBS 4.1
3-3-resolución-de-solicitudes              Must      8 pts  S4  R1  WBS 4.1
```

## Paso 7 · Business case, OKR ligados a SM-n y puerta autorizar-proyecto con línea base del PRD
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
$ python3 $OKR gestion/00-direccion/okr.csv --corte 2026-11-20
O-1 Los socios resuelven sus gestiones simples sin ir a la sucursal → 0.00 (rojo)
   KR-1.1 30 % de socios activos registrados [0/30 %] → 0.00 (rojo) · B-02; SM-1 · Usuario sénior: Sofía Ramírez
   KR-1.2 Bajar 30 % las consultas de saldo por canales tradicionales [5000/3500 consultas] → 0.00 (rojo) · B-01; SM-2 · Usuario sénior: Sofía Ramírez
   KR-1.3 Responder préstamos simples en menos de 48 h hábiles [96/48 horas] → 0.00 (rojo) · B-03; SM-3 · Usuario sénior: Sofía Ramírez
```

```
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "beneficios=-10 %" "riesgo=ningún riesgo alto sin respuesta"
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido
Sanidad de 'Portal de autoservicio para socios' (inicio/IP): 0 ERROR · 0 AVISO · 1 INFO
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
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
$ python3 $EST/estado.py --proyecto gestion aprobar business-case --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27
Copia congelada / frozen copy: 00-direccion/historial/business-case-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar pid --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27
Copia congelada / frozen copy: 00-direccion/historial/pid-v1.0.md
ok
```

```
$ python3 $BMAD --proyecto gestion linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"
Línea base bmad-prd v1.0 registrada · sha bc048f7f59a3 · copia congelada en gestion/00-direccion/historial/bmad-prd-v1.0
```

```
$ python3 $BMAD --proyecto gestion linea-base epicas --version 1.0 --por "Ejecutivo: Laura Méndez"
Línea base bmad-epicas v1.0 registrada · sha 3ff846d6f8d9 · copia congelada en gestion/00-direccion/historial/bmad-epicas-v1.0
```

## Paso 8 · Gate de preparación de BMAD y puerta autorizar-etapa (Release 1)
```
$ python3 $EST/puertas.py --proyecto gestion preparacion-bmad --resultado CONCERNS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26 --nota "NFR-3 sin prueba de carga planificada"
Preparación BMAD registrada: CONCERNS
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-etapa-2 --ruta 02-planificacion/plan-etapa-2.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel etapa "tiempo=±10 %" "costo=±10 %" "alcance=PO intercambia Should/Could"
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-etapa
Puerta autorizar-etapa: 1 bloqueo(s) · 1 condición(es) · 0 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-etapa y confirmarla (puertas.py confirmar …)
  condición gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
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
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision condicionado --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27 --etapa-nombre "Release 1" --fin 2027-03-05
Aviso: se conservan las tolerancias de etapa vigentes; si la junta fijó otras para esta etapa, pasarlas con --tol o 'tolerancia --nivel etapa'.
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

## Paso 9 · Sprint 1 como paquete de trabajo; construcción con BMAD; avance
```
$ python3 $EST/estado.py --proyecto gestion artefacto WP-001 --ruta 03-control/paquetes-trabajo/WP-001-sprint-1.md --estado aprobado --version 1.0
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar WP-001 --por "Gestor: Martín Suárez" --nivel gestor --fecha 2026-11-30
Copia congelada / frozen copy: 00-direccion/historial/WP-001-v1.0.md
ok
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2026-12-23
Historias 10 · backlog 7 · ready-for-dev 0 · in-progress 0 · review 1 · done 2 · épicas terminadas 0/3 · 19.1 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ (cada corte agrega una fila a 03-control/reportes/avance-bmad.csv)

```

```
$ python3 $EST/especificacion.py --proyecto gestion resumen
requisitos: 42
historias: 10
por_estado: {'backlog': 7, 'ready-for-dev': 0, 'in-progress': 0, 'review': 1, 'done': 2}
```

## Paso 10 · Valor ganado ágil y highlight con puertas
```
$ python3 $EST/evm.py --pv 41000 --ev 38000 --ac 40500 --bac 124000 --modo agil --pct-no-must 20 --proyecto gestion
PV                     41,000.000
EV                     38,000.000
AC                     40,500.000
BAC                    124,000.000
SV                     -3,000.000
CV                     -2,500.000
SPI                    0.927
CPI                    0.938
pct_completado         0.306
pct_gastado            0.327
EAC_tendencia          132,157.895
EAC_atipico            126,500.000
EAC_compuesto          139,394.044
EAC_usado              tendencia
ETC                    91,657.895
VAC                    -8,157.895
VAC_pct                -6.579
sobrecosto_pct         6.579
TCPI_bac               1.030
TCPI_eac               0.938
semaforo_cronograma    n/a-agil
semaforo_costo         n/a-agil
base_semaforo          alcance-agil
alcance_no_entregable_pct 6.173
semaforo_alcance       verde
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
| autorizar-etapa | 2026-11-27 | condicionado | Ejecutivo: Laura Méndez | — | gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada) | 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md |

**Próxima puerta / Next gate: autorizar-etapa** — 2 bloqueo(s), 1 condición(es), 0 aviso(s).
- bloqueo: falta el plan de la etapa a autorizar (plan-etapa-3)
- bloqueo: falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
- condición: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
```

## Paso 11 · Cambio de rumbo: bmad-correct-course agrega FR-13 → verificar → issue → cambio → traspaso → línea base 1.1
```
$ python3 $BMAD --proyecto gestion verificar
- [desvio] bmad-prd: contenido distinto de la línea base aprobada → tratar como solicitud de cambio (pm-issues-cambios) salvo elaboración progresiva declarada · agregados ['FR-13'] · retirados []
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 2 ERROR · 2 AVISO · 1 INFO
  ERROR ESP-03 Requisitos sin cobertura (ni historia ni paquete de la WBS): FR-13.
        → Planificarlos (pm-planificacion-por-productos / pm-agil-hibrido) o retirarlos mediante control de cambios.
  ERROR ESP-10 Cambio no controlado: bmad-prd difiere de la línea base v1.0 (ids FR-13) y ningún issue/cambio abierto lo cita.
        → pm-issues-cambios: registrar solicitud-cambio (o declarar elaboración progresiva y fijar nueva línea base).
  AVISO ESP-14 requisitos-bmad.csv no coincide con el PRD vigente (desactualizado o editado).
        → bmad.py requisitos (es derivado: no se edita).
  AVISO ESP-15 backlog.csv 1-1-alta-y-acceso-del-socio-con-segundo-factor: estado 'ready-for-dev' ≠ BMAD 'done'.
        → bmad.py backlog (sincroniza las columnas derivadas).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2027-01-12" --campo "tipo=solicitud-cambio" --campo "titulo=FR-13 pago de cuotas agregado al PRD sin control de cambios" --campo "descripcion=bmad.py verificar detectó FR-13 nuevo contra la línea base PRD v1.0" --campo "prioridad=alta" --campo "severidad=mayor" --campo "responsable=Martín Suárez"
I-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2027-01-13" --campo "solicitante=Sofía Ramírez" --campo "titulo=Incorporar FR-13 pago de cuotas" --campo "descripcion=Origen I-001" --campo "impacto_alcance=nueva historia 2-4 (8 puntos)" --campo "impacto_tiempo=+1 sprint en la etapa 3" --campo "impacto_costo=+USD 6.000 (contingencia)" --campo "impacto_beneficios=refuerza B-01" --campo "recomendacion=aprobar para la etapa 3; diferir FR-8 a Could"
C-001
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-001 --campo "decision=aprobado" --campo "decidido_por=Autoridad de cambio: Sofía Ramírez" --campo "fecha_decision=2027-01-14" --campo "estado=aprobado"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-001 --campo "estado=pendiente-cambio" --campo "decision=tramitado como C-001" --campo "decidido_por=Autoridad de cambio: Sofía Ramírez"
ok
```

```
$ python3 $BMAD --proyecto gestion handoff --cambio C-001
Traspaso emitido → gestion/02-planificacion/especificacion/handoff-bmad-2026-10-17-C-001.md (cambio C-001 · 10 prioridades cambiadas)
```

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
$ (el PO completa las columnas de gobierno de la historia nueva 2-4: Should, 8 pts, S7, R2)

```

```
$ python3 $BMAD --proyecto gestion linea-base prd --version 1.1 --por "Ejecutivo: Laura Méndez"
Línea base bmad-prd v1.1 registrada · sha 203d33cb9e51 · copia congelada en gestion/00-direccion/historial/bmad-prd-v1.1
```

```
$ python3 $BMAD --proyecto gestion linea-base epicas --version 1.1 --por "Ejecutivo: Laura Méndez"
Línea base bmad-epicas v1.1 registrada · sha 360c24ddcd9c · copia congelada en gestion/00-direccion/historial/bmad-epicas-v1.1
```

```
$ (el equipo BMAD marca el traspaso como aplicado: estado: aplicado en gestion/02-planificacion/especificacion/handoff-bmad-2026-10-17-C-001.md)

```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-001 --campo "estado=implementado"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-001 --campo "estado=cerrado" --campo "fecha_cierre=2027-01-20"
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

## Paso 12 · Calidad por requisito, retrospectiva y lecciones
```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=FR-1 alta y acceso (historia 1-1)" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 1-1 y NFR-1" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-01-20"
Q-001
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar calidad Q-001 --campo "resultado=aprobado" --campo "estado=completada" --campo "fecha_real=2027-01-20"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar lecciones --campo "etapa=2" --campo "categoria=especificacion" --campo "situacion=FR-13 entró al PRD por correct-course sin pasar por la autoridad de cambio" --campo "efecto=sanidad ESP-10 bloqueó la puerta hasta tramitar C-001" --campo "recomendacion=toda Sprint Change Proposal se presenta primero como issue" --campo "prioridad=alta" --campo "responsable_seguimiento=Martín Suárez"
L-001
```

## Paso 13 · Fin de la etapa 2 (Release 1), informe de fin de etapa y puerta autorizar-etapa (Release 2)
```
$ python3 $BMAD --proyecto gestion avance --corte 2027-03-05
Historias 11 · backlog 4 · ready-for-dev 0 · in-progress 0 · review 0 · done 7 · épicas terminadas 2/3 · 61.8 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 11 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto tablero-avance --ruta 03-control/reportes/2027-03-05-tablero-avance.html --estado en-revision
ok
```

```
$ (pm-visuales arma el tablero con la receta de references/guia.md §3 → gestion/03-control/reportes/2027-03-05-tablero-avance.html)
riesgos abiertos 0 · issues 0 · acciones 0 · iteraciones 2
```

```
$ python3 $EST/estado.py --proyecto gestion limite-etapa
ok
Fase: entrega · Proceso: SB · Etapa 2: Release 1 · Enfoque: hibrido
Límite de etapa (SB): informe de fin de etapa, plan de la siguiente etapa, actualizar plan de proyecto, business case, riesgos y lecciones. Puerta: autorizar-etapa (o si es la última etapa: estado.py cierre). Agentes: pm-planificacion + pm-control.
```

```
$ python3 $EST/evm.py --pv 82000 --ev 80000 --ac 83500 --bac 130000 --proyecto gestion
PV                     82,000.000
EV                     80,000.000
AC                     83,500.000
BAC                    130,000.000
SV                     -2,000.000
CV                     -3,500.000
SPI                    0.976
CPI                    0.958
pct_completado         0.615
pct_gastado            0.642
EAC_tendencia          135,687.500
EAC_atipico            133,500.000
EAC_compuesto          136,992.188
EAC_usado              tendencia
ETC                    52,187.500
VAC                    -5,687.500
VAC_pct                -4.375
sobrecosto_pct         4.375
TCPI_bac               1.075
TCPI_eac               0.958
semaforo_cronograma    verde
semaforo_costo         verde
base_semaforo          costo:tolerancia;cronograma:tolerancia
excepcion_prevista     False
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto informe-fin-etapa-2 --ruta 03-control/reportes/2027-03-05-informe-fin-etapa-2.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-etapa-3 --ruta 02-planificacion/plan-etapa-3.md --estado en-revision
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2027-03-03
Preparación BMAD registrada: PASS
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-etapa
Puerta autorizar-etapa: 0 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  → aprobado posible
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa
Lista creada: 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md (0 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutivo: Laura Méndez"
Lista 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-03-05 --etapa-nombre "Release 2" --fin 2027-05-14 --tol "tiempo=±10 %" "costo=±10 %"
ok
Fase: entrega · Proceso: CS · Etapa 3: Release 2 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

## Paso 14 · Release 2, aceptación, beneficios y puerta autorizar-cierre
```
$ python3 $BMAD --proyecto gestion avance --corte 2027-05-12
Historias 11 · backlog 0 · ready-for-dev 0 · in-progress 0 · review 0 · done 11 · épicas terminadas 3/3 · 100.0 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 11 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $EST/especificacion.py --proyecto gestion listar requisitos --cobertura sin-cobertura

```

```
$ python3 $EST/especificacion.py --proyecto gestion resumen
requisitos: 43
historias: 11
por_estado: {'backlog': 0, 'ready-for-dev': 0, 'in-progress': 0, 'review': 0, 'done': 11}
```

```
$ python3 $EST/evm.py --pv 130000 --ev 130000 --ac 133000 --bac 130000 --tol-costo 8 --tol-plazo 10
PV                     130,000.000
EV                     130,000.000
AC                     133,000.000
BAC                    130,000.000
SV                     0.000
CV                     -3,000.000
SPI                    1.000
CPI                    0.977
pct_completado         1.000
pct_gastado            1.023
EAC_tendencia          133,000.000
EAC_atipico            133,000.000
EAC_compuesto          133,000.000
EAC_usado              tendencia
ETC                    0.000
VAC                    -3,000.000
VAC_pct                -2.308
sobrecosto_pct         2.308
TCPI_bac               -0.000
TCPI_eac               None
semaforo_cronograma    verde
semaforo_costo         verde
base_semaforo          costo:tolerancia;cronograma:tolerancia
excepcion_prevista     False
```

```
$ python3 $EST/estado.py --proyecto gestion cierre
ok
Fase: cierre · Proceso: CP · Etapa 3: Release 2 · Enfoque: hibrido
Cierre (CP): confirmar aceptación de productos, traspaso a operaciones, evaluar el proyecto contra el PID original, lecciones, plan de revisión de beneficios, informe de fin de proyecto y recomendación de cierre. Agente: pm-cierre. Puerta: autorizar-cierre (pm-director).
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto registro-aceptacion --ruta 04-cierre/registro-aceptacion.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar registro-aceptacion --por "Usuario sénior: Sofía Ramírez; Ejecutivo: Laura Méndez" --version 1.0 --fecha 2027-05-12
Copia congelada / frozen copy: 00-direccion/historial/registro-aceptacion-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto informe-fin-proyecto --ruta 04-cierre/informe-fin-proyecto.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto informe-lecciones --ruta 04-cierre/informe-lecciones.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-revision-beneficios --ruta 04-cierre/plan-revision-beneficios.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto recomendaciones-seguimiento --ruta 04-cierre/recomendaciones-seguimiento.md --estado en-revision
ok
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --corte 2027-06-30 --markdown gestion/03-control/reportes/2027-06-30-okr.md
O-1 Los socios resuelven sus gestiones simples sin ir a la sucursal → 0.37 (rojo)
   KR-1.1 30 % de socios activos registrados [9/30 %] → 0.30 (rojo) · B-02; SM-1 · Usuario sénior: Sofía Ramírez
   KR-1.2 Bajar 30 % las consultas de saldo por canales tradicionales [4600/3500 consultas] → 0.27 (rojo) · B-01; SM-2 · Usuario sénior: Sofía Ramírez
   KR-1.3 Responder préstamos simples en menos de 48 h hábiles [70/48 horas] → 0.54 (ambar) · B-03; SM-3 · Usuario sénior: Sofía Ramírez
Tabla escrita en gestion/03-control/reportes/2027-06-30-okr.md
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-cierre
Puerta autorizar-cierre: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-cierre y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-cierre
Lista creada: 00-direccion/decisiones/2026-10-17-verificacion-autorizar-cierre.md (0 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-cierre --por "Ejecutivo: Laura Méndez"
Lista 00-direccion/decisiones/2026-10-17-verificacion-autorizar-cierre.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-cierre --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-05-14 
ok
Fase: cerrado · Proceso: CP · Etapa 3: Release 2 · Enfoque: hibrido
Proyecto cerrado. Pendiente fuera del proyecto: revisiones de beneficios según el plan (responsable: usuario sénior / capa de negocio).
```

```
$ python3 $PAQ --proyecto gestion cierre
Escrito gestion/exportados/2026-10-17-paquete-cierre-v1-BORRADOR.zip
En borrador: business-case-original (sin-estado)
```

```
$ python3 $EST/exportar.py xlsx --proyecto gestion
Escrito gestion/exportados/2026-10-17-registros.xlsx
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Portal de autoservicio para socios · cerrado/CP · etapa 3 Release 2 (2027-03-05 → 2027-05-14) · enfoque hibrido · idioma es
Autorizado: sí
Roles: ejecutivo=Laura Méndez; usuario_senior=Sofía Ramírez; proveedor_senior=Diego Ferreira; gestor_proyecto=Martín Suárez; aseguramiento=Andrea Costa; autoridad_cambio=Sofía Ramírez; product_owner=Sofía Ramírez; jefes_equipo=Lucía Benítez
Tolerancias: proyecto: tiempo=±3 semanas, costo=±8 %, alcance=Must sin tolerancia, beneficios=-10 %, riesgo=ningún riesgo alto sin respuesta | etapa: tiempo=±10 %, costo=±10 %
Artefactos: 19 (6 aprobados)
Última puerta: autorizar-cierre · aprobado · 2027-05-14 · Ejecutivo: Laura Méndez
Fase: cerrado · Proceso: CP · Etapa 3: Release 2 · Enfoque: hibrido
Proyecto cerrado. Pendiente fuera del proyecto: revisiones de beneficios según el plan (responsable: usuario sénior / capa de negocio).
```

