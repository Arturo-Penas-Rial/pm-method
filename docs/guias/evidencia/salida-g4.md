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
Proveedor de especificación: bmad · índice reconstruido ahora (<fecha-hora>)
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

## Paso 7 · Business case, enfoques de beneficios, calidad y sostenibilidad, PID adaptado, OKR y puerta autorizar-proyecto
```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision
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
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "calidad=NFR sin tolerancia; cada historia terminada con revisión aprobada" "beneficios=-10 %" "riesgo=ningún riesgo alto sin respuesta" "sostenibilidad=-10 % sobre las metas del enfoque de sostenibilidad"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto pid --ruta 00-direccion/pid.md --estado en-revision
ok
```

```
$ (pm-acta-constitucion; §8 con la adaptación del método → gestion/00-direccion/pid.md)
# PID · Portal de autoservicio para socios
§1-§7: business case, organización, enfoques (calidad, beneficios, sostenibilidad, riesgo, cambios), plan de proyecto y controles.
## 8. Adaptación del método (tailoring)
- Ciclo de vida: etapas PRINCE2 (iniciación, Release 1, Release 2); dentro de cada etapa, sprints de 14 días como paquetes de trabajo.
- Especificación: BMAD es la fuente única (PRD, épicas, historias); pm-method la lee por la fachada y no la copia. Cambios a la línea base del PRD: solo por control de cambios y traspaso.
- Roles combinados: Sofía Ramírez es usuaria sénior, product owner y autoridad de cambio (hasta USD 8.000 por cambio y USD 15.000 en total, presupuesto de cambio de la junta).
- Informes: checkpoint por sprint (jefa de equipo), highlight quincenal (gestor), informe de fin de etapa por release.
- Calidad: una revisión registrada por historia (enfoque de calidad); los NFR con prueba propia.
- Productos de gestión fusionados: plan de proyecto dentro del PID; release plan en lugar de plan de equipo.
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 0 condición(es) · 3 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  aviso     sin enfoque de beneficios (cómo, cuándo y quién mide cada beneficio, incluso después del proyecto)
  aviso     registro de interesados vacío: sin matriz poder/interés (pm-interesados)
  aviso     sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-beneficios --ruta 00-direccion/enfoque-beneficios.md --estado en-revision
ok
```

```
$ (pm-caso-de-negocio, templates/enfoque-beneficios.md → gestion/00-direccion/enfoque-beneficios.md)
# Enfoque de gestión de beneficios v1.0
Gestionado por: proyecto hasta el cierre; negocio (usuaria sénior Sofía Ramírez) después.
| Beneficio | Medida | Línea base | Meta | Dueño | Mediciones |
|---|---|---|---|---|---|
| B-01 desvío de consultas | SM-2 (KR-1.2) | 5.000 consultas/mes | 3.500 | Sofía Ramírez | 30/6/2027 y 31/12/2027 |
| B-02 adopción | SM-1 (KR-1.1) | 0 % | 30 % de socios activos | Sofía Ramírez | 30/6/2027 y 31/12/2027 |
| B-03 préstamos en < 48 h | SM-3 (KR-1.3) | 96 h | 48 h | Sofía Ramírez | 30/6/2027 y 31/12/2027 |
Tolerancia de beneficios: -10 %. Las revisiones posteriores al proyecto las ejecuta y financia el negocio.
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-calidad --ruta 00-direccion/enfoque-calidad.md --estado en-revision
ok
```

```
$ (pm-enfoques-gestion, templates/enfoque-calidad.md → gestion/00-direccion/enfoque-calidad.md)
# Enfoque de gestión de la calidad v1.0
Criterios: cada historia se verifica contra sus criterios de aceptación de BMAD (epics.md); los NFR, con prueba específica (NFR-3: prueba de carga, p95 < 3 s).
Responsables: produce Lucía Benítez (equipo), revisa Andrea Costa (aseguramiento, independiente), aprueba Sofía Ramírez (usuaria sénior).
Registro: una revisión en calidad.csv por historia terminada, que la cite como "historia N-M"; se registra en lote al cierre de cada sprint o release.
Control permanente: sanidad QUA-01 (terminado sin revisión), QUA-02 (revisión vencida), QUA-03 (rechazo sin tratamiento).
Defectos fuera de especificación: issue (pm-issues-cambios).
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-sostenibilidad --ruta 00-direccion/enfoque-sostenibilidad.md --estado en-revision
ok
```

```
$ (pm-caso-de-negocio, templates/enfoque-sostenibilidad.md → gestion/00-direccion/enfoque-sostenibilidad.md)
# Enfoque de gestión de sostenibilidad v1.0
Aplicabilidad: mínimo (sin impacto ambiental relevante; se mide lo que el portal cambia).
| Meta | Indicador | Línea base | Meta | Dueño | Revisión |
|---|---|---|---|---|---|
| S-1 constancias sin papel | % de constancias emitidas en PDF | 0 % | 80 % a 12 meses | Sofía Ramírez | fin de cada etapa y revisión de beneficios |
| S-2 traslados evitados | consultas desviadas de sucursal (SM-2) | 5.000/mes | -30 % | Sofía Ramírez | ídem |
| S-3 alojamiento | proveedor de nube con energía renovable certificada | — | requisito de contrato | Diego Ferreira | fin de etapa 2 |
Tolerancia: -10 % sobre las metas (estado.json tolerancias.proyecto.sostenibilidad).
```

```
$ python3 $EST/estado.py --proyecto gestion presupuesto cambio=15000 limite_autoridad_cambio=8000 --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-27
Sanidad de 'Portal de autoservicio para socios' (inicio/IP): 0 ERROR · 0 AVISO · 0 INFO
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 0 condición(es) · 2 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  aviso     registro de interesados vacío: sin matriz poder/interés (pm-interesados)
  aviso     sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
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
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-beneficios --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27
Copia congelada / frozen copy: 00-direccion/historial/enfoque-beneficios-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-calidad --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27
Copia congelada / frozen copy: 00-direccion/historial/enfoque-calidad-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-sostenibilidad --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-11-27
Copia congelada / frozen copy: 00-direccion/historial/enfoque-sostenibilidad-v1.0.md
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

```
$ python3 $EST/estado.py --proyecto gestion resumen
Portal de autoservicio para socios · inicio/IP · etapa 1 Iniciación (2026-10-30 → 2026-11-27) · enfoque hibrido · idioma es
Autorizado: sí
Roles: ejecutivo=Laura Méndez; usuario_senior=Sofía Ramírez; proveedor_senior=Diego Ferreira; gestor_proyecto=Martín Suárez; aseguramiento=Andrea Costa; autoridad_cambio=Sofía Ramírez; product_owner=Sofía Ramírez; jefes_equipo=Lucía Benítez
Tolerancias: proyecto: tiempo=±3 semanas, costo=±8 %, alcance=Must sin tolerancia, calidad=NFR sin tolerancia; cada historia terminada con revisión aprobada, beneficios=-10 %, riesgo=ningún riesgo alto sin respuesta, sostenibilidad=-10 % sobre las metas del enfoque de sostenibilidad | etapa: 
Presupuestos: cambio=15000, limite_autoridad_cambio=8000
Artefactos: 12 (7 aprobados)
Última puerta: autorizar-proyecto · aprobado · 2026-11-27 · Ejecutivo: Laura Méndez
Próxima puerta: autorizar-etapa · 3 bloqueo(s) · 0 condición(es) (detalle: puertas.py verificar autorizar-etapa)
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director). Proyecto ya autorizado: falta autorizar-etapa para la primera etapa de entrega.
```

## Paso 8 · Gate de preparación de BMAD y puerta autorizar-etapa (Release 1) con condición formal
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
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa --fecha 2026-11-27
Lista creada: 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md (1 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27
Lista 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision condicionado --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27 --etapa-nombre "Release 1" --fin 2027-03-05
Condiciones agregadas desde la verificación: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
Aviso: se conservan las tolerancias de etapa vigentes; si la junta fijó otras para esta etapa, pasarlas con --tol o 'tolerancia --nivel etapa'.
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
Condiciones abiertas: autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=NFR-3 prueba de carga (consultas de saldos y préstamos)" --campo "metodo_verificacion=prueba" --campo "criterios=NFR-3 p95 menor a 3 s con conexión móvil estándar; condición de autorizar-etapa (CONCERNS de BMAD)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Diego Ferreira; Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-02-19"
Q-001
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-27
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 1 INFO
  AVISO EST-12 Condiciones abiertas de autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada).
        → estado.py cumplir-condiciones <tipo> cuando se cumplan.
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

## Paso 9 · Sprint 1 como paquete de trabajo; construcción con BMAD; checkpoint y aceptación del paquete
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
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 10 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Sprint 1 · historia 1-1 Alta y acceso del socio con segundo factor" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 1-1 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2026-12-21" --campo "fecha_real=2026-12-21" --campo "resultado=aprobado" --campo "estado=completada" --campo "notas=incluye NFR-1 segundo factor"
Q-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Sprint 1 · historia 1-2 Recuperación de acceso" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 1-2 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2026-12-22" --campo "fecha_real=2026-12-22" --campo "resultado=aprobado" --campo "estado=completada"
Q-003
```

```
$ (pm-progreso-reportes, templates/checkpoint-report.md → gestion/03-control/reportes/2026-12-23-checkpoint-WP-001.md)
# Informe de punto de control · WP-001 (sprint 1) · 2026-12-23
Gestora de equipo: Lucía Benítez · Para: Martín Suárez (gestor) · Período: 2026-11-30 – 2026-12-23
1. Resumen: sprint 1 completo; semáforo verde (13 de 13 puntos comprometidos).
3. Productos completados (con calidad aprobada): historia 1-1 (Q-002), historia 1-2 (Q-003). En curso: historia 1-3 en review (sprint 2).
   Actividades de calidad: Q-002 y Q-003 aprobadas por Sofía Ramírez. Prevista: Q-001 prueba de carga NFR-3 (19/2).
5. Tolerancias del paquete: tiempo y costo dentro; alcance completo; calidad: 2 de 2 historias con revisión.
6. Issues y riesgos: sin novedades. 7. Acciones correctivas: ninguna.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-12-23
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 2 INFO
  AVISO EST-12 Condiciones abiertas de autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada).
        → estado.py cumplir-condiciones <tipo> cuando se cumplan.
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-12-23" --campo "decision=WP-001 aceptado: checkpoint del 23/12; historias 1-1 y 1-2 terminadas con Q-002 y Q-003 aprobadas" --campo "decidido_por=Gestor: Martín Suárez" --campo "nivel=gestor" --campo "artefactos_afectados=03-control/reportes/2026-12-23-checkpoint-WP-001.md"
D-015
```

```
$ python3 $EST/especificacion.py --proyecto gestion resumen
requisitos: 42
historias: 10
por_estado: {'backlog': 7, 'ready-for-dev': 0, 'in-progress': 0, 'review': 1, 'done': 2}
```

## Paso 10 · Valor ganado ágil (corte guardado) y highlight con puertas y condiciones
```
$ python3 $EST/evm.py --pv 41000 --ev 38000 --ac 40500 --bac 124000 --modo agil --pct-no-must 20 --proyecto gestion --guardar --corte 2027-01-08
Guardado: 03-control/reportes/evm-2027-01-08.json
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
| autorizar-inicio | 2026-10-30 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md |
| autorizar-proyecto | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md |
| autorizar-etapa | 2026-11-27 | condicionado | Ejecutivo: Laura Méndez | gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada) (abiertas) | gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada) | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md |

**Próxima puerta / Next gate: autorizar-etapa** — 2 bloqueo(s), 3 condición(es), 0 aviso(s).
- bloqueo: falta el plan de la etapa a autorizar (plan-etapa-3)
- bloqueo: falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
- condición: condiciones abiertas de puertas anteriores: autorizar-etapa 2026-11-27 (verificarlas y registrar estado.py cumplir-condiciones, o traspasarlas como recomendación)
- condición: revisiones de calidad sin cerrar: Q-001
- condición: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
```

## Paso 11 · Cambio de rumbo: bmad-correct-course agrega FR-13 → verificar → issue → cambio con costo y cargo → traspaso → línea base 1.1
```
$ python3 $BMAD --proyecto gestion verificar
- [desvio] bmad-prd: contenido distinto de la línea base aprobada → tratar como solicitud de cambio (pm-issues-cambios) salvo elaboración progresiva declarada · agregados ['FR-13'] · retirados []
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-12
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 2 ERROR · 2 AVISO · 1 INFO
  ERROR ESP-03 Requisitos sin cobertura (ni historia ni paquete de la WBS): FR-13.
        → Planificarlos (pm-planificacion-por-productos / pm-agil-hibrido) o retirarlos mediante control de cambios.
  ERROR ESP-10 Cambio no controlado: bmad-prd difiere de la línea base v1.0 (ids FR-13) y ningún issue/cambio abierto lo cita.
        → pm-issues-cambios: registrar solicitud-cambio (o declarar elaboración progresiva y fijar nueva línea base).
  AVISO ESP-14 requisitos-bmad.csv no coincide con el PRD vigente (desactualizado o editado).
        → bmad.py requisitos (es derivado: no se edita).
  AVISO EST-12 Condiciones abiertas de autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada).
        → estado.py cumplir-condiciones <tipo> cuando se cumplan.
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2027-01-12" --campo "tipo=solicitud-cambio" --campo "titulo=FR-13 pago de cuotas agregado al PRD sin control de cambios" --campo "descripcion=bmad.py verificar detectó FR-13 nuevo contra la línea base PRD v1.0" --campo "prioridad=alta" --campo "severidad=mayor" --campo "responsable=Martín Suárez"
I-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2027-01-13" --campo "solicitante=Sofía Ramírez" --campo "titulo=Incorporar FR-13 pago de cuotas" --campo "descripcion=Origen I-001" --campo "impacto_alcance=nueva historia 2-4 (8 puntos)" --campo "impacto_tiempo=+1 sprint en la etapa 3" --campo "impacto_costo=+USD 6.000 contra el presupuesto de cambio" --campo "impacto_beneficios=refuerza B-01" --campo "recomendacion=aprobar para la etapa 3; diferir FR-8 a Could" --campo "costo=6000" --campo "cargo=presupuesto-cambio"
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
$ (el equipo BMAD marca el traspaso como aplicado: estado: aplicado en gestion/02-planificacion/especificacion/handoff-bmad-<fecha>-C-001.md)

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
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-20
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 2 INFO
  AVISO EST-12 Condiciones abiertas de autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada).
        → estado.py cumplir-condiciones <tipo> cuando se cumplan.
  INFO  CAM-03 Presupuesto de cambio: 6.000 de 15.000 (40 %).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

## Paso 12 · Calidad a volumen al acercarse el fin del Release 1: terminados sin revisión, registro en lote, retrospectiva y lecciones
```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 11 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-26
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 7 AVISO · 3 INFO
  AVISO EST-12 Condiciones abiertas de autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada).
        → estado.py cumplir-condiciones <tipo> cuando se cumplan.
  AVISO QUA-01 1-3-consulta-de-saldos-de-ahorro-y-préstamos: terminado sin revisión de calidad registrada.
  AVISO QUA-01 1-4-descarga-de-constancias-en-pdf: terminado sin revisión de calidad registrada.
  AVISO QUA-01 3-1-acceso-y-roles-de-la-consola-de-operador: terminado sin revisión de calidad registrada.
  AVISO QUA-01 3-2-bandeja-única-de-solicitudes: terminado sin revisión de calidad registrada.
  AVISO QUA-01 3-3-resolución-de-solicitudes: terminado sin revisión de calidad registrada.
        → pm-calidad: registrar la revisión (registro.py agregar calidad --campo producto="… historia N-M") o aplicar el criterio de aceptación por lote.
  AVISO QUA-02 Revisión de calidad vencida Q-001 (NFR-3 prueba de carga (consultas de saldos y préstamos), prevista 2027-02-19).
        → Realizarla o replanificarla.
  INFO  CAM-03 Presupuesto de cambio: 6.000 de 15.000 (40 %).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
  INFO  TOL-03 Último corte de EVM guardado el 2027-01-08 (más de 31 días).
        → evm.py … --guardar en cada período de informe.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 1 · historia 1-3 Consulta de saldos de ahorro y préstamos" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 1-3 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-02-25" --campo "fecha_real=2027-02-25" --campo "resultado=aprobado" --campo "estado=completada"
Q-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 1 · historia 1-4 Descarga de constancias en PDF" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 1-4 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-02-25" --campo "fecha_real=2027-02-25" --campo "resultado=aprobado" --campo "estado=completada"
Q-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 1 · historia 3-1 Acceso y roles de la consola de operador" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 3-1 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-02-25" --campo "fecha_real=2027-02-25" --campo "resultado=aprobado" --campo "estado=completada"
Q-006
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 1 · historia 3-2 Bandeja única de solicitudes" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 3-2 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-02-25" --campo "fecha_real=2027-02-25" --campo "resultado=aprobado" --campo "estado=completada"
Q-007
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 1 · historia 3-3 Resolución de solicitudes" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 3-3 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-02-25" --campo "fecha_real=2027-02-25" --campo "resultado=aprobado-con-observaciones" --campo "estado=completada" --campo "notas=observación menor de usabilidad en el filtro de la bandeja; va al backlog"
Q-008
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-26
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 2 AVISO · 2 INFO
  AVISO EST-12 Condiciones abiertas de autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada).
        → estado.py cumplir-condiciones <tipo> cuando se cumplan.
  AVISO QUA-02 Revisión de calidad vencida Q-001 (NFR-3 prueba de carga (consultas de saldos y préstamos), prevista 2027-02-19).
        → Realizarla o replanificarla.
  INFO  CAM-03 Presupuesto de cambio: 6.000 de 15.000 (40 %).
  INFO  TOL-03 Último corte de EVM guardado el 2027-01-08 (más de 31 días).
        → evm.py … --guardar en cada período de informe.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar lecciones --campo "etapa=2" --campo "categoria=especificacion" --campo "situacion=FR-13 entró al PRD por correct-course sin pasar por la autoridad de cambio" --campo "efecto=sanidad ESP-10 bloqueó la puerta hasta tramitar C-001" --campo "recomendacion=toda Sprint Change Proposal se presenta primero como issue" --campo "prioridad=alta" --campo "responsable_seguimiento=Martín Suárez"
L-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar lecciones --campo "etapa=2" --campo "categoria=calidad" --campo "situacion=cinco historias del Release 1 llegaron a done sin revisión de calidad registrada" --campo "efecto=sanidad QUA-01 lo detectó antes del fin de etapa y se registraron en lote" --campo "recomendacion=la revisión registrada es parte de la definición de terminado; sanidad con --corte en cada checkpoint" --campo "prioridad=media" --campo "responsable_seguimiento=Lucía Benítez"
L-002
```

## Paso 13 · Fin de la etapa 2 (Release 1): prueba de carga NFR-3, condición cumplida, business case 1.1 y puerta autorizar-etapa (Release 2)
```
$ python3 $EST/registro.py --proyecto gestion actualizar calidad Q-001 --campo "resultado=aprobado" --campo "estado=completada" --campo "fecha_real=2027-03-02" --campo "notas=p95 2,4 s con 400 sesiones concurrentes (meta menor a 3 s)"
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion preparacion-bmad --resultado PASS --por "Arquitecto: Diego Ferreira" --fecha 2027-03-03
Preparación BMAD registrada: PASS
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2027-03-05
Historias 11 · backlog 4 · ready-for-dev 0 · in-progress 0 · review 0 · done 7 · épicas terminadas 2/3 · 61.8 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $EST/estado.py --proyecto gestion limite-etapa
ok
Fase: entrega · Proceso: SB · Etapa 2: Release 1 · Enfoque: hibrido
Límite de etapa (SB): informe de fin de etapa, plan de la siguiente etapa, actualizar plan de proyecto, business case, riesgos y lecciones. Puerta: autorizar-etapa (o si es la última etapa: estado.py cierre). Agentes: pm-planificacion + pm-control.
Condiciones abiertas: autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
```

```
$ python3 $EST/evm.py --pv 82000 --ev 80000 --ac 83500 --bac 130000 --proyecto gestion --guardar --corte 2027-03-05
Guardado: 03-control/reportes/evm-2027-03-05.json
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
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision --version 1.1
ok
```

```
$ (pm-caso-de-negocio, modo mantener → gestion/00-direccion/business-case.md)
# Business case v1.1 (modo mantener, fin de la etapa 2)
B-01 desvío de consultas (SM-2); B-02 adopción (SM-1); B-03 eficiencia de préstamos (SM-3).
Costos: AC 83.500 contra PV 82.000; EAC 135.688 contra BAC 130.000 (124.000 + 6.000 de C-001, cargado al presupuesto de cambio): +4,4 %, dentro de ±8 %.
Beneficios: sin medición todavía (primera revisión 30/6/2027 según el enfoque de beneficios); FR-13 (C-001) refuerza B-01.
Riesgos: sin riesgos altos abiertos; NFR-3 verificada con prueba de carga.
Veredicto: sigue deseable, viable y alcanzable → continuar con la etapa 3.
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-etapa
Puerta autorizar-etapa: 0 bloqueo(s) · 1 condición(es) · 0 aviso(s)
  condición condiciones abiertas de puertas anteriores: autorizar-etapa 2026-11-27 (verificarlas y registrar estado.py cumplir-condiciones, o traspasarlas como recomendación)
  → aprobado posible
```

```
$ python3 $EST/estado.py --proyecto gestion cumplir-condiciones autorizar-etapa --fecha 2027-03-05 --por "Ejecutivo: Laura Méndez" --nota "Q-001 prueba de carga NFR-3 aprobada el 2027-03-02 (p95 2,4 s); gate de preparación de BMAD en PASS el 2027-03-03"
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-03-05
Sanidad de 'Portal de autoservicio para socios' (entrega/SB): 0 ERROR · 0 AVISO · 1 INFO
  INFO  CAM-03 Presupuesto de cambio: 6.000 de 15.000 (40 %).
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
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-etapa
Puerta autorizar-etapa: 0 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  → aprobado posible
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa --fecha 2027-03-05
Lista creada: 00-direccion/decisiones/2027-03-05-verificacion-autorizar-etapa.md (0 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutivo: Laura Méndez" --fecha 2027-03-05
Lista 00-direccion/decisiones/2027-03-05-verificacion-autorizar-etapa.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-03-05 --etapa-nombre "Release 2" --fin 2027-05-14 --tol "tiempo=±10 %" "costo=±10 %"
ok
Fase: entrega · Proceso: CS · Etapa 3: Release 2 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar business-case --por "Ejecutivo: Laura Méndez" --version 1.1 --fecha 2027-03-05
Copia congelada / frozen copy: 00-direccion/historial/business-case-v1.1.md
ok
```

## Paso 14 · Release 2, aceptación, traspaso a operación, business case confirmado y puerta autorizar-cierre
```
$ python3 $BMAD --proyecto gestion avance --corte 2027-05-12
Historias 11 · backlog 0 · ready-for-dev 0 · in-progress 0 · review 0 · done 11 · épicas terminadas 3/3 · 100.0 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 11 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 2 · historia 2-1 Solicitud guiada de préstamo simple" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 2-1 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-05-11" --campo "fecha_real=2027-05-11" --campo "resultado=aprobado" --campo "estado=completada"
Q-009
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 2 · historia 2-2 Seguimiento de solicitudes y respuesta a pedidos de información" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 2-2 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-05-11" --campo "fecha_real=2027-05-11" --campo "resultado=aprobado" --campo "estado=completada"
Q-010
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 2 · historia 2-3 Actualización de datos de contacto con verificación" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 2-3 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-05-11" --campo "fecha_real=2027-05-11" --campo "resultado=aprobado" --campo "estado=completada"
Q-011
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Release 2 · historia 2-4 Pago de cuotas con débito en cuenta" --campo "metodo_verificacion=prueba" --campo "criterios=criterios de aceptación de la historia 2-4 (epics.md)" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Andrea Costa" --campo "aprobador=Sofía Ramírez" --campo "fecha_prevista=2027-05-11" --campo "fecha_real=2027-05-11" --campo "resultado=aprobado" --campo "estado=completada"
Q-012
```

```
$ python3 $EST/evm.py --pv 130000 --ev 130000 --ac 133000 --bac 130000 --tol-costo 8 --tol-plazo 10 --proyecto gestion --guardar --corte 2027-05-12
Guardado: 03-control/reportes/evm-2027-05-12.json
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
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-05-12
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 2 INFO
  INFO  CAM-03 Presupuesto de cambio: 6.000 de 15.000 (40 %).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
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
$ python3 $EST/estado.py --proyecto gestion artefacto handover --ruta 04-cierre/handover.md --estado en-revision
ok
```

```
$ (pm-cierre-proyecto, templates/handover.md → gestion/04-cierre/handover.md)
# Transferencia a operación y mantenimiento v1.0
Productos: portal del socio y consola de operador (13 FR, 11 historias; líneas base PRD y épicas 1.1), aceptados en registro-aceptacion v1.0.
Propietario receptor: usuaria sénior Sofía Ramírez (servicios al socio); mantenimiento: equipo de Lucía Benítez durante 90 días de garantía.
Evidencia de calidad: 12 revisiones aprobadas en calidad.csv (una por historia y la prueba de carga NFR-3).
Pendientes: observación menor de Q-008 en el backlog de mantenimiento. Costos de operación: desde el 15/5/2027, a cargo del negocio.
5. Confirmación del receptor: Sofía Ramírez, 2027-05-12.
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar handover --por "Usuario sénior: Sofía Ramírez" --version 1.0 --fecha 2027-05-12
Copia congelada / frozen copy: 00-direccion/historial/handover-v1.0.md
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
$ python3 $EST/estado.py --proyecto gestion artefacto recomendaciones-seguimiento --ruta 04-cierre/recomendaciones-seguimiento.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-revision-beneficios --ruta 04-cierre/plan-revision-beneficios.md --estado en-revision
ok
```

```
$ (pm-cierre-proyecto, templates/plan-revision-beneficios.md → gestion/04-cierre/plan-revision-beneficios.md)
# Plan de revisión de beneficios v1.0
Responsable de las revisiones: el negocio (usuaria sénior Sofía Ramírez), con financiación de servicios al socio; el proyecto no las ejecuta.
| Revisión | Fecha | Qué se mide | Fuente |
|---|---|---|---|
| 1 | 2027-06-30 | B-01, B-02, B-03 y S-1 contra línea base | okr.csv (KR-1.1 a KR-1.3) y SM-1 a SM-3 del PRD |
| 2 | 2027-12-31 | metas finales y contramétricas SM-C1, SM-C2 | ídem |
Desvío mayor que la tolerancia de beneficios (-10 % sobre la trayectoria) → informe a la ejecutiva (Laura Méndez).
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision --version 1.2
ok
```

```
$ (pm-caso-de-negocio, modo confirmar → gestion/00-direccion/business-case.md)
# Business case v1.2 (modo confirmar, cierre)
Real contra la línea base: AC 133.000 contra BAC 130.000 (+2,3 %, dentro de ±8 %); 13 FR y 11 historias (C-001); fin 2027-05-14 sin desvío.
Beneficios B-01 a B-03: todavía no realizados (el portal entra en operación el 15/5/2027); se confirman en las revisiones del plan de revisión de beneficios.
Traspaso: el enfoque de beneficios pasa al negocio (Sofía Ramírez), que ejecuta y financia las revisiones.
Veredicto: el proyecto entregó lo autorizado; la justificación depende ahora de la adopción (B-02).
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-beneficios --ruta 00-direccion/enfoque-beneficios.md --estado en-revision --version 1.1
ok
```

```
$ (pm-caso-de-negocio, traspaso del enfoque de beneficios → gestion/00-direccion/enfoque-beneficios.md)
# Enfoque de gestión de beneficios v1.1
Gestionado por: negocio (usuaria sénior Sofía Ramírez) desde el 2027-05-14; revisiones según 04-cierre/plan-revision-beneficios.md.
Beneficios, medidas, líneas base, metas y tolerancia sin cambios respecto de la v1.0.
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto notificacion-cierre --ruta 04-cierre/notificacion-cierre.md --estado borrador
ok
```

```
$ (pm-cierre-proyecto, templates/notificacion-cierre.md → gestion/04-cierre/notificacion-cierre.md)
# Notificación de cierre del proyecto (borrador)
Emisor: Laura Méndez, ejecutiva, en nombre de la junta. Destinatarios: Consejo, servicios al socio, operaciones y proveedores.
Contenido: el proyecto cierra el 2027-05-14; el portal queda a cargo de servicios al socio; las revisiones de beneficios las hace el negocio (30/6 y 31/12/2027).
Se emite solo después de la puerta autorizar-cierre.
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-cierre
Puerta autorizar-cierre: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-cierre y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-cierre --fecha 2027-05-14
Lista creada: 00-direccion/decisiones/2027-05-14-verificacion-autorizar-cierre.md (0 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-cierre --por "Ejecutivo: Laura Méndez" --fecha 2027-05-14
Lista 00-direccion/decisiones/2027-05-14-verificacion-autorizar-cierre.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-cierre --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-05-14 
ok
Fase: cerrado · Proceso: CP · Etapa 3: Release 2 · Enfoque: hibrido
Proyecto cerrado. Pendiente fuera del proyecto: revisiones de beneficios según el plan (responsable: usuario sénior / capa de negocio).
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar business-case --por "Ejecutivo: Laura Méndez" --version 1.2 --fecha 2027-05-14
Copia congelada / frozen copy: 00-direccion/historial/business-case-v1.2.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-beneficios --por "Ejecutivo: Laura Méndez; Usuario sénior: Sofía Ramírez" --version 1.1 --fecha 2027-05-14
Copia congelada / frozen copy: 00-direccion/historial/enfoque-beneficios-v1.1.md
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2027-05-14" --campo "decision=Responsabilidad de los beneficios traspasada al negocio: Sofía Ramírez ejecuta y financia las revisiones del plan de revisión de beneficios (30/6 y 31/12/2027)" --campo "decidido_por=Ejecutivo: Laura Méndez" --campo "nivel=junta" --campo "artefactos_afectados=00-direccion/enfoque-beneficios.md; 04-cierre/plan-revision-beneficios.md"
D-027
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar notificacion-cierre --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2027-05-14
Copia congelada / frozen copy: 00-direccion/historial/notificacion-cierre-v1.0.md
ok
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
Tolerancias: proyecto: tiempo=±3 semanas, costo=±8 %, alcance=Must sin tolerancia, calidad=NFR sin tolerancia; cada historia terminada con revisión aprobada, beneficios=-10 %, riesgo=ningún riesgo alto sin respuesta, sostenibilidad=-10 % sobre las metas del enfoque de sostenibilidad | etapa: tiempo=±10 %, costo=±10 %
Presupuestos: cambio=15000, limite_autoridad_cambio=8000
Artefactos: 24 (11 aprobados)
Última puerta: autorizar-cierre · aprobado · 2027-05-14 · Ejecutivo: Laura Méndez
Fase: cerrado · Proceso: CP · Etapa 3: Release 2 · Enfoque: hibrido
Proyecto cerrado. Pendiente fuera del proyecto: revisiones de beneficios según el plan (responsable: usuario sénior / capa de negocio).
```

## Paso 15 · Después del proyecto: primera revisión de beneficios del negocio (30/6/2027)
```
$ (Sofía Ramírez, por el negocio, carga las mediciones del 30/6 en okr.csv: KR-1.1 9 %, KR-1.2 4.600 consultas, KR-1.3 70 horas)

```

```
$ python3 $OKR gestion/00-direccion/okr.csv --corte 2027-06-30 --markdown gestion/03-control/reportes/2027-06-30-okr.md
O-1 Los socios resuelven sus gestiones simples sin ir a la sucursal → 0.37 (rojo)
   KR-1.1 30 % de socios activos registrados [9/30 %] → 0.30 (rojo) · B-02; SM-1 · Usuario sénior: Sofía Ramírez
   KR-1.2 Bajar 30 % las consultas de saldo por canales tradicionales [4600/3500 consultas] → 0.27 (rojo) · B-01; SM-2 · Usuario sénior: Sofía Ramírez
   KR-1.3 Responder préstamos simples en menos de 48 h hábiles [70/48 horas] → 0.54 (ambar) · B-03; SM-3 · Usuario sénior: Sofía Ramírez
Tabla escrita en gestion/03-control/reportes/2027-06-30-okr.md
```

