## Paso 1 · Proyecto y junta
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

## Paso 2 · Identificar y clasificar interesados (poder, interés, actitud, compromiso actual y deseado)
```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Laura Méndez" --campo "rol_organizacion=Gerenta de operaciones" --campo "rol_proyecto=Ejecutiva" --campo "poder=alto" --campo "interes=alto" --campo "actitud=lider" --campo "nivel_compromiso_actual=lider" --campo "nivel_compromiso_deseado=lider" --campo "canal=reunión 1:1" --campo "frecuencia=quincenal" --campo "responsable_relacion=Martín Suárez" --campo "confidencial=no"
ST-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Consejo directivo" --campo "rol_organizacion=Órgano de gobierno de la cooperativa" --campo "rol_proyecto=Capa de negocio" --campo "poder=alto" --campo "interes=medio" --campo "actitud=partidario" --campo "nivel_compromiso_actual=partidario" --campo "nivel_compromiso_deseado=lider" --campo "canal=informe ejecutivo" --campo "frecuencia=trimestral" --campo "responsable_relacion=Laura Méndez" --campo "confidencial=no"
ST-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Sofía Ramírez" --campo "rol_organizacion=Jefa de atención al socio" --campo "rol_proyecto=Usuaria sénior y PO" --campo "poder=alto" --campo "interes=alto" --campo "actitud=lider" --campo "nivel_compromiso_actual=lider" --campo "nivel_compromiso_deseado=lider" --campo "canal=sprint review" --campo "frecuencia=quincenal" --campo "responsable_relacion=Martín Suárez" --campo "confidencial=no"
ST-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Sindicato de operadores" --campo "rol_organizacion=Representación de operadores de sucursal" --campo "rol_proyecto=Afectado" --campo "poder=medio" --campo "interes=alto" --campo "actitud=resistente" --campo "nivel_compromiso_actual=resistente" --campo "nivel_compromiso_deseado=neutral" --campo "canal=taller presencial" --campo "frecuencia=mensual" --campo "responsable_relacion=Sofía Ramírez" --campo "confidencial=si"
ST-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Socios usuarios piloto" --campo "rol_organizacion=Panel de 40 socios" --campo "rol_proyecto=Usuarios finales" --campo "poder=bajo" --campo "interes=alto" --campo "actitud=desconocedor" --campo "nivel_compromiso_actual=desconocedor" --campo "nivel_compromiso_deseado=partidario" --campo "canal=encuesta y boletín" --campo "frecuencia=mensual" --campo "responsable_relacion=Sofía Ramírez" --campo "confidencial=no"
ST-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Área de TI del núcleo operativo" --campo "rol_organizacion=Dueña del core y del padrón" --campo "rol_proyecto=Proveedor interno" --campo "poder=alto" --campo "interes=medio" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "canal=reunión técnica" --campo "frecuencia=semanal" --campo "responsable_relacion=Lucía Benítez" --campo "confidencial=no"
ST-006
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Unidad de cumplimiento" --campo "rol_organizacion=Protección de datos" --campo "rol_proyecto=Asesor" --campo "poder=alto" --campo "interes=bajo" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "canal=correo y revisión" --campo "frecuencia=por hito" --campo "responsable_relacion=Andrea Costa" --campo "confidencial=no"
ST-007
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Diego Ferreira" --campo "rol_organizacion=Gerente del proveedor" --campo "rol_proyecto=Proveedor sénior" --campo "poder=medio" --campo "interes=alto" --campo "actitud=partidario" --campo "nivel_compromiso_actual=partidario" --campo "nivel_compromiso_deseado=partidario" --campo "canal=reunión de junta" --campo "frecuencia=mensual" --campo "responsable_relacion=Martín Suárez" --campo "confidencial=no"
ST-008
```

```
$ python3 $EST/registro.py --proyecto gestion listar stakeholders
id=ST-001 | nombre=Laura Méndez | rol_organizacion=Gerenta de operaciones | rol_proyecto=Ejecutiva | poder=alto | interes=alto | actitud=lider | nivel_compromiso_actual=lider | nivel_compromiso_deseado=lider | canal=reunión 1:1 | frecuencia=quincenal | responsable_relacion=Martín Suárez | confidencial=no
id=ST-002 | nombre=Consejo directivo | rol_organizacion=Órgano de gobierno de la cooperativa | rol_proyecto=Capa de negocio | poder=alto | interes=medio | actitud=partidario | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=lider | canal=informe ejecutivo | frecuencia=trimestral | responsable_relacion=Laura Méndez | confidencial=no
id=ST-003 | nombre=Sofía Ramírez | rol_organizacion=Jefa de atención al socio | rol_proyecto=Usuaria sénior y PO | poder=alto | interes=alto | actitud=lider | nivel_compromiso_actual=lider | nivel_compromiso_deseado=lider | canal=sprint review | frecuencia=quincenal | responsable_relacion=Martín Suárez | confidencial=no
id=ST-004 | nombre=Sindicato de operadores | rol_organizacion=Representación de operadores de sucursal | rol_proyecto=Afectado | poder=medio | interes=alto | actitud=resistente | nivel_compromiso_actual=resistente | nivel_compromiso_deseado=neutral | canal=taller presencial | frecuencia=mensual | responsable_relacion=Sofía Ramírez | confidencial=si
id=ST-005 | nombre=Socios usuarios piloto | rol_organizacion=Panel de 40 socios | rol_proyecto=Usuarios finales | poder=bajo | interes=alto | actitud=desconocedor | nivel_compromiso_actual=desconocedor | nivel_compromiso_deseado=partidario | canal=encuesta y boletín | frecuencia=mensual | responsable_relacion=Sofía Ramírez | confidencial=no
id=ST-006 | nombre=Área de TI del núcleo operativo | rol_organizacion=Dueña del core y del padrón | rol_proyecto=Proveedor interno | poder=alto | interes=medio | actitud=neutral | nivel_compromiso_actual=neutral | nivel_compromiso_deseado=partidario | canal=reunión técnica | frecuencia=semanal | responsable_relacion=Lucía Benítez | confidencial=no
id=ST-007 | nombre=Unidad de cumplimiento | rol_organizacion=Protección de datos | rol_proyecto=Asesor | poder=alto | interes=bajo | actitud=neutral | nivel_compromiso_actual=neutral | nivel_compromiso_deseado=partidario | canal=correo y revisión | frecuencia=por hito | responsable_relacion=Andrea Costa | confidencial=no
id=ST-008 | nombre=Diego Ferreira | rol_organizacion=Gerente del proveedor | rol_proyecto=Proveedor sénior | poder=medio | interes=alto | actitud=partidario | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=partidario | canal=reunión de junta | frecuencia=mensual | responsable_relacion=Martín Suárez | confidencial=no
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto analisis-stakeholders --ruta 01-inicio/analisis-stakeholders.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto mapa-stakeholders --ruta 02-planificacion/visuales/mapa-stakeholders.md --estado en-revision
ok
```

## Paso 3 · Plan de compromiso, enfoque de comunicación y matriz de comunicaciones
```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-compromiso-stakeholders --ruta 02-planificacion/plan-compromiso-stakeholders.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-comunicacion --ruta 02-planificacion/enfoques/enfoque-comunicacion.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto matriz-comunicaciones --ruta 02-planificacion/matriz-comunicaciones.md --estado en-revision
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2026-11-02" --campo "origen=ST-004" --campo "descripcion=Taller de co-diseño de la bandeja con operadores y delegado sindical" --campo "responsable=Sofía Ramírez" --campo "fecha_compromiso=2026-11-20" --campo "prioridad=alta"
A-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2026-11-02" --campo "origen=ST-005" --campo "descripcion=Boletín 1 al panel de socios: qué es el portal y cómo participar del piloto" --campo "responsable=Sofía Ramírez" --campo "fecha_compromiso=2026-12-01" --campo "prioridad=media"
A-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2026-11-02" --campo "origen=ST-002" --campo "descripcion=Informe ejecutivo trimestral al Consejo con OKR y riesgos" --campo "responsable=Laura Méndez" --campo "fecha_compromiso=2027-01-15" --campo "prioridad=media"
A-003
```

## Paso 4 · OKR ligados a beneficios (B-n) y métricas de éxito del PRD (SM-n)
```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto okr --ruta 00-direccion/okr.md --estado en-revision
ok
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --corte 2026-11-20
O-1 Los socios resuelven sus gestiones simples sin ir a la sucursal → 0.00 (rojo)
   KR-1.1 30 % de socios activos registrados en el portal [0/30 %] → 0.00 (rojo) · B-02; SM-1 · Usuario sénior: Sofía Ramírez
   KR-1.2 Bajar 30 % las consultas de saldo y constancias por canales tradicionales [5000/3500 consultas] → 0.00 (rojo) · B-01; SM-2 · Usuario sénior: Sofía Ramírez
O-2 Los préstamos simples se resuelven rápido y sin papeles → 0.00 (rojo)
   KR-2.1 Respuesta a solicitudes simples en menos de 48 h hábiles [96/48 horas] → 0.00 (rojo) · B-03; SM-3 · Usuario sénior: Sofía Ramírez
   KR-2.2 Más del 90 % de las solicitudes llegan completas [60/90 %] → 0.00 (rojo) · B-03; SM-3 · Usuario sénior: Sofía Ramírez
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido
Sanidad de 'Portal de autoservicio para socios' (pre-proyecto/SU): 0 ERROR · 0 AVISO · 1 INFO
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
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
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "riesgo=ningún riesgo alto sin respuesta"
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
$ python3 $EST/puertas.py --proyecto gestion preparacion-bmad --resultado CONCERNS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26 --nota "NFR-3 sin prueba de carga planificada"
Preparación BMAD registrada: CONCERNS
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-etapa-2 --ruta 02-planificacion/plan-etapa-2.md --estado en-revision
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-etapa
Puerta autorizar-etapa: 2 bloqueo(s) · 1 condición(es) · 0 aviso(s)
  BLOQUEO   faltan tolerancias de la etapa (--tol o 'tolerancia --nivel etapa')
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-etapa y confirmarla (puertas.py confirmar …)
  condición gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa
Lista creada: 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md (2 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutivo: Laura Méndez"
Lista 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision condicionado --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27 --etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=+2 semanas" "costo=±10 %"
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

## Paso 5 · Comunicar durante la etapa: acta de reunión con interesados → acciones y decisiones
```
$ (transcripción de ejemplo: copiala a gestion/03-control/reuniones/2026-11-19-taller-bandeja-original.vtt)
WEBVTT

00:00:01.000 --> 00:00:09.000
<v Sofía Ramírez>Buen día, este es el taller de la bandeja única con operadores.

00:00:10.000 --> 00:00:21.000
<v Delegado sindical>Nos preocupa que la bandeja se use para medir productividad individual.

00:00:22.000 --> 00:00:34.000
<v Martín Suárez>Propongo que el tablero de la bandeja muestre solo métricas del equipo, no por persona. Lo registro como decisión del product owner si Sofía está de acuerdo.

00:00:35.000 --> 00:00:42.000
<v Sofía Ramírez>De acuerdo. Y Lucía prepara el prototipo con ese criterio para el 11 de diciembre.

00:00:43.000 --> 00:00:50.000
<v Lucía Benítez>Confirmado, prototipo el 11 de diciembre.
```

```
$ python3 $PLUGIN/skills/pm-reuniones/scripts/transcripcion.py gestion/03-control/reuniones/2026-11-19-taller-bandeja-original.vtt --salida gestion/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md
5 intervenciones de 4 hablantes → gestion/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-19" --campo "decision=El tablero de la bandeja muestra métricas del equipo, no individuales" --campo "contexto=taller con ST-004" --campo "decidido_por=Product owner: Sofía Ramírez" --campo "nivel=product-owner"
D-006
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2026-11-19" --campo "origen=acta-2026-11-19-taller-bandeja" --campo "descripcion=Prototipo de bandeja con métricas de equipo" --campo "responsable=Lucía Benítez" --campo "fecha_compromiso=2026-12-11" --campo "prioridad=alta"
A-004
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-001 --campo "estado=completada" --campo "fecha_cierre=2026-11-19"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-004 --campo "nivel_compromiso_actual=neutral" --campo "notas=taller 2026-11-19: acuerdo sobre métricas de equipo"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto comunicado-operadores --ruta 03-control/reportes/2026-11-21-comunicado-bandeja.md --estado en-revision
ok
```

## Paso 6 · Avance de la etapa: serie EVM, avance BMAD y registros a la fecha de corte
```
$ python3 $EST/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 124000 --tol-costo 10 --tol-plazo 10 --proyecto gestion
== 2026-12-11 ==
PV                     15,000.000
EV                     14,200.000
AC                     15,000.000
BAC                    124,000.000
SV                     -800.000
CV                     -800.000
SPI                    0.947
CPI                    0.947
pct_completado         0.115
pct_gastado            0.121
EAC_tendencia          130,985.915
EAC_atipico            124,800.000
EAC_compuesto          137,520.333
EAC_usado              tendencia
ETC                    115,985.915
VAC                    -6,985.915
VAC_pct                -5.634
sobrecosto_pct         5.634
TCPI_bac               1.007
TCPI_eac               0.947
semaforo_cronograma    ambar
semaforo_costo         ambar
base_semaforo          costo:tolerancia;cronograma:tolerancia
excepcion_prevista     False
== 2026-12-23 ==
PV                     30,000.000
EV                     28,000.000
AC                     29,600.000
BAC                    124,000.000
SV                     -2,000.000
CV                     -1,600.000
SPI                    0.933
CPI                    0.946
pct_completado         0.226
pct_gastado            0.239
EAC_tendencia          131,085.714
EAC_atipico            125,600.000
EAC_compuesto          138,334.694
EAC_usado              tendencia
ETC                    101,485.714
VAC                    -7,085.714
VAC_pct                -5.714
sobrecosto_pct         5.714
TCPI_bac               1.017
TCPI_eac               0.946
semaforo_cronograma    ambar
semaforo_costo         ambar
base_semaforo          costo:tolerancia;cronograma:tolerancia
excepcion_prevista     False
== 2027-01-08 ==
PV                     45,000.000
EV                     42,000.000
AC                     44,600.000
BAC                    124,000.000
SV                     -3,000.000
CV                     -2,600.000
SPI                    0.933
CPI                    0.942
pct_completado         0.339
pct_gastado            0.360
EAC_tendencia          131,676.190
EAC_atipico            126,600.000
EAC_compuesto          137,895.918
EAC_usado              tendencia
ETC                    87,076.190
VAC                    -7,676.190
VAC_pct                -6.190
sobrecosto_pct         6.190
TCPI_bac               1.033
TCPI_eac               0.942
semaforo_cronograma    ambar
semaforo_costo         ambar
base_semaforo          costo:tolerancia;cronograma:tolerancia
excepcion_prevista     False
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 10 nuevas, 0 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2026-12-11
Historias 10 · backlog 9 · ready-for-dev 0 · in-progress 0 · review 0 · done 1 · épicas terminadas 0/3 · 11.8 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2026-12-23
Historias 10 · backlog 7 · ready-for-dev 0 · in-progress 0 · review 0 · done 3 · épicas terminadas 0/3 · 26.5 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2027-01-08
Historias 10 · backlog 5 · ready-for-dev 0 · in-progress 1 · review 0 · done 4 · épicas terminadas 0/3 · 38.2 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-002 --campo "estado=completada" --campo "fecha_cierre=2026-11-28"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-12-20" --campo "autor=Martín Suárez" --campo "categoria=organizacional" --campo "causa=Baja respuesta del panel de socios a las encuestas" --campo "evento=No se puede medir la satisfacción (SM-5) en el piloto" --campo "efecto=KR sin línea base confiable" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=3" --campo "impacto_monetario=4000" --campo "respuesta=reducir" --campo "acciones=incentivo de participación y encuesta corta" --campo "propietario=Sofía Ramírez" --campo "ejecutor=Martín Suárez" --campo "estado=en-seguimiento" --campo "notas=interesado ST-005"
R-001
```

```
$ python3 $EST/registro.py --proyecto gestion resumen --corte 2027-01-08
{
  "riesgos": {
    "total": 1,
    "por_estado": {
      "en-seguimiento": 1
    },
    "abiertos": 1,
    "altos_abiertos": 0,
    "umbrales": {
      "alto": 15.0,
      "medio": 6.0
    },
    "sin_respuesta": [],
    "sin_propietario": [],
    "top": [
      "R-001 (9, medio) No se puede medir la satisfacción (SM-5) en el piloto"
    ]
  },
  "issues": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0,
    "sin_responsable": []
  },
  "cambios": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "decisiones": {
    "total": 6
  },
  "supuestos": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "lecciones": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "stakeholders": {
    "total": 8
  },
  "calidad": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "acciones": {
    "total": 4,
    "por_estado": {
      "completada": 2,
      "abierta": 2
    },
    "abiertos": 2,
    "vencidas": [
      "A-004 Lucía Benítez 2026-12-11"
    ],
    "abiertas_por_responsable": {
      "Laura Méndez": 1,
      "Lucía Benítez": 1
    }
  },
  "fecha_corte": "2027-01-08"
}
```

## Paso 7 · Highlight report con puertas, OKR al corte y tablero de avance con vista por actor
```
$ python3 $OKR gestion/00-direccion/okr.csv --corte 2027-01-08 --markdown gestion/03-control/reportes/2027-01-08-okr.md
O-1 Los socios resuelven sus gestiones simples sin ir a la sucursal → 0.05 (rojo)
   KR-1.1 30 % de socios activos registrados en el portal [3/30 %] → 0.10 (rojo) · B-02; SM-1 · Usuario sénior: Sofía Ramírez
   KR-1.2 Bajar 30 % las consultas de saldo y constancias por canales tradicionales [5000/3500 consultas] → 0.00 (rojo) · B-01; SM-2 · Usuario sénior: Sofía Ramírez
O-2 Los préstamos simples se resuelven rápido y sin papeles → 0.20 (rojo)
   KR-2.1 Respuesta a solicitudes simples en menos de 48 h hábiles [96/48 horas] → 0.00 (rojo) · B-03; SM-3 · Usuario sénior: Sofía Ramírez
   KR-2.2 Más del 90 % de las solicitudes llegan completas [72/90 %] → 0.40 (ambar) · B-03; SM-3 · Usuario sénior: Sofía Ramírez
Tabla escrita en gestion/03-control/reportes/2027-01-08-okr.md
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

```
$ python3 $EST/estado.py --proyecto gestion artefacto highlight-2027-01-08 --ruta 03-control/reportes/2027-01-08-highlight-report.md --estado en-revision
ok
```

```
$ (columnas de avance-bmad.csv)
fecha, historias, backlog, ready-for-dev, in-progress, review, done, epicas, epicas_terminadas, puntos_total, puntos_terminados, pct_terminado, base_pct
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto tablero-avance --ruta 03-control/reportes/2027-01-08-tablero-avance.html --estado en-revision
ok
```

```
$ (pm-visuales arma el tablero con la receta de references/guia.md §3 → gestion/03-control/reportes/2027-01-08-tablero-avance.html)
riesgos abiertos 1 · issues 0 · acciones 4 · iteraciones 3
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto tablero-avance --ruta 03-control/reportes/2027-01-08-tablero-avance.html --estado en-revision
ok
```

```
$ (pm-visuales arma el tablero con la receta de references/guia.md §3 → gestion/03-control/reportes/2027-01-08-tablero-avance.html)
riesgos abiertos 1 · issues 0 · acciones 4 · iteraciones 3
```

## Paso 8 · Comunicación del avance por audiencia y seguimiento de compromisos
```
$ python3 $EST/estado.py --proyecto gestion artefacto comunicado-consejo --ruta 03-control/reportes/2027-01-15-comunicado-consejo.md --estado en-revision
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-003 --campo "estado=completada" --campo "fecha_cierre=2027-01-15"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-005 --campo "nivel_compromiso_actual=partidario" --campo "notas=78 % de respuesta al boletín 2"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion listar acciones
id=A-001 | fecha=2026-11-02 | origen=ST-004 | descripcion=Taller de co-diseño de la bandeja con operadores y delegado sindical | responsable=Sofía Ramírez | fecha_compromiso=2026-11-20 | prioridad=alta | estado=completada | fecha_cierre=2026-11-19
id=A-002 | fecha=2026-11-02 | origen=ST-005 | descripcion=Boletín 1 al panel de socios: qué es el portal y cómo participar del piloto | responsable=Sofía Ramírez | fecha_compromiso=2026-12-01 | prioridad=media | estado=completada | fecha_cierre=2026-11-28
id=A-003 | fecha=2026-11-02 | origen=ST-002 | descripcion=Informe ejecutivo trimestral al Consejo con OKR y riesgos | responsable=Laura Méndez | fecha_compromiso=2027-01-15 | prioridad=media | estado=completada | fecha_cierre=2027-01-15
id=A-004 | fecha=2026-11-19 | origen=acta-2026-11-19-taller-bandeja | descripcion=Prototipo de bandeja con métricas de equipo | responsable=Lucía Benítez | fecha_compromiso=2026-12-11 | prioridad=alta | estado=abierta
```

```
$ python3 $EST/registro.py --proyecto gestion listar stakeholders
id=ST-001 | nombre=Laura Méndez | rol_organizacion=Gerenta de operaciones | rol_proyecto=Ejecutiva | poder=alto | interes=alto | actitud=lider | nivel_compromiso_actual=lider | nivel_compromiso_deseado=lider | canal=reunión 1:1 | frecuencia=quincenal | responsable_relacion=Martín Suárez | confidencial=no
id=ST-002 | nombre=Consejo directivo | rol_organizacion=Órgano de gobierno de la cooperativa | rol_proyecto=Capa de negocio | poder=alto | interes=medio | actitud=partidario | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=lider | canal=informe ejecutivo | frecuencia=trimestral | responsable_relacion=Laura Méndez | confidencial=no
id=ST-003 | nombre=Sofía Ramírez | rol_organizacion=Jefa de atención al socio | rol_proyecto=Usuaria sénior y PO | poder=alto | interes=alto | actitud=lider | nivel_compromiso_actual=lider | nivel_compromiso_deseado=lider | canal=sprint review | frecuencia=quincenal | responsable_relacion=Martín Suárez | confidencial=no
id=ST-004 | nombre=Sindicato de operadores | rol_organizacion=Representación de operadores de sucursal | rol_proyecto=Afectado | poder=medio | interes=alto | actitud=resistente | nivel_compromiso_actual=neutral | nivel_compromiso_deseado=neutral | canal=taller presencial | frecuencia=mensual | responsable_relacion=Sofía Ramírez | confidencial=si | notas=taller 2026-11-19: acuerdo sobre métricas de equipo
id=ST-005 | nombre=Socios usuarios piloto | rol_organizacion=Panel de 40 socios | rol_proyecto=Usuarios finales | poder=bajo | interes=alto | actitud=desconocedor | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=partidario | canal=encuesta y boletín | frecuencia=mensual | responsable_relacion=Sofía Ramírez | confidencial=no | notas=78 % de respuesta al boletín 2
id=ST-006 | nombre=Área de TI del núcleo operativo | rol_organizacion=Dueña del core y del padrón | rol_proyecto=Proveedor interno | poder=alto | interes=medio | actitud=neutral | nivel_compromiso_actual=neutral | nivel_compromiso_deseado=partidario | canal=reunión técnica | frecuencia=semanal | responsable_relacion=Lucía Benítez | confidencial=no
id=ST-007 | nombre=Unidad de cumplimiento | rol_organizacion=Protección de datos | rol_proyecto=Asesor | poder=alto | interes=bajo | actitud=neutral | nivel_compromiso_actual=neutral | nivel_compromiso_deseado=partidario | canal=correo y revisión | frecuencia=por hito | responsable_relacion=Andrea Costa | confidencial=no
id=ST-008 | nombre=Diego Ferreira | rol_organizacion=Gerente del proveedor | rol_proyecto=Proveedor sénior | poder=medio | interes=alto | actitud=partidario | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=partidario | canal=reunión de junta | frecuencia=mensual | responsable_relacion=Martín Suárez | confidencial=no
```

```
$ python3 $EST/exportar.py xlsx --proyecto gestion
Escrito gestion/exportados/2026-10-17-registros.xlsx
```

