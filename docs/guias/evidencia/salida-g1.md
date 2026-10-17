## Paso 1 · Proyecto, junta y objetivos con tolerancias
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
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "beneficios=-10 %" "riesgo=ningún riesgo alto sin respuesta; exposición total ≤ USD 60.000"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Portal de autoservicio para socios · pre-proyecto/SU · etapa 0 pre-proyecto (2026-10-17 → ) · enfoque hibrido · idioma es
Autorizado: no
Roles: ejecutivo=Laura Méndez; usuario_senior=Sofía Ramírez; proveedor_senior=Diego Ferreira; gestor_proyecto=Martín Suárez; aseguramiento=Andrea Costa; autoridad_cambio=Sofía Ramírez; product_owner=Sofía Ramírez; jefes_equipo=Lucía Benítez
Tolerancias: proyecto: tiempo=±3 semanas, costo=±8 %, alcance=Must sin tolerancia, beneficios=-10 %, riesgo=ningún riesgo alto sin respuesta; exposición total ≤ USD 60.000 | etapa: 
Artefactos: 0 (0 aprobados)
Próxima puerta: autorizar-inicio · 2 bloqueo(s) · 1 condición(es) (detalle: puertas.py verificar autorizar-inicio)
Fase: pre-proyecto · Proceso: SU · Etapa 0: pre-proyecto · Enfoque: hibrido
Puesta en marcha (SU): mandato → lecciones previas → brief (con caso de negocio esquemático y enfoque del proyecto) → junta y roles → plan de la etapa de iniciación. Ágil/híbrido: brief ligero + visión y backlog inicial de épicas. Agentes: pm-inicio. Puerta: autorizar-inicio (pm-director).
```

## Paso 2 · Contexto del riesgo: productos y WBS, interesados y especificación
```
$ python3 $EST/wbs.py gestion/02-planificacion/wbs.csv --titulo "Portal de autoservicio para socios" --profundidad 1
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
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Laura Méndez" --campo "rol_organizacion=Ejecutiva" --campo "poder=alto" --campo "interes=alto" --campo "actitud=lider" --campo "nivel_compromiso_actual=lider" --campo "nivel_compromiso_deseado=lider" --campo "confidencial=no"
ST-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Sindicato de operadores" --campo "rol_organizacion=Representación de operadores de sucursal" --campo "poder=medio" --campo "interes=alto" --campo "actitud=resistente" --campo "nivel_compromiso_actual=resistente" --campo "nivel_compromiso_deseado=neutral" --campo "confidencial=no"
ST-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Área de TI del núcleo operativo" --campo "rol_organizacion=Dueña del core y del padrón" --campo "poder=alto" --campo "interes=medio" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "confidencial=no"
ST-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Unidad de cumplimiento" --campo "rol_organizacion=Protección de datos (Ley 18.331)" --campo "poder=alto" --campo "interes=medio" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "confidencial=no"
ST-004
```

```
$ python3 $EST/especificacion.py --proyecto gestion listar requisitos --limite 8
id=UJ-1 | tipo=UJ | titulo=Marta consulta su saldo y baja una constancia desde el celular. | paquetes_wbs=['2.1'] | cobertura=n/a
id=UJ-2 | tipo=UJ | titulo=Diego pide un préstamo simple y sigue su estado. | paquetes_wbs=['2.1'] | cobertura=n/a
id=UJ-3 | tipo=UJ | titulo=Lucía atiende la bandeja de solicitudes. | paquetes_wbs=['2.1'] | cobertura=n/a
id=FR-1 | tipo=FR | titulo=Alta y acceso del socio | historias=['1-1-alta-y-acceso-del-socio-con-segundo-factor', '1-2-recuperación-de-acceso', '1-3-consulta-de-saldos-de-ahorro-y-préstamos', '1-4-descarga-de-constancias-en-pdf'] | nivel_traza=epica | epicas=['E-1'] | paquetes_wbs=['3.1'] | cobertura=planificado
id=FR-2 | tipo=FR | titulo=Recuperación de acceso | historias=['1-1-alta-y-acceso-del-socio-con-segundo-factor', '1-2-recuperación-de-acceso', '1-3-consulta-de-saldos-de-ahorro-y-préstamos', '1-4-descarga-de-constancias-en-pdf'] | nivel_traza=epica | epicas=['E-1'] | paquetes_wbs=['3.1'] | cobertura=planificado
id=FR-3 | tipo=FR | titulo=Consulta de saldos de ahorro | historias=['1-1-alta-y-acceso-del-socio-con-segundo-factor', '1-2-recuperación-de-acceso', '1-3-consulta-de-saldos-de-ahorro-y-préstamos', '1-4-descarga-de-constancias-en-pdf'] | nivel_traza=epica | epicas=['E-1'] | paquetes_wbs=['3.2'] | cobertura=planificado
id=FR-4 | tipo=FR | titulo=Consulta de préstamos | historias=['1-1-alta-y-acceso-del-socio-con-segundo-factor', '1-2-recuperación-de-acceso', '1-3-consulta-de-saldos-de-ahorro-y-préstamos', '1-4-descarga-de-constancias-en-pdf'] | nivel_traza=epica | epicas=['E-1'] | paquetes_wbs=['3.2'] | cobertura=planificado
id=FR-5 | tipo=FR | titulo=Descarga de constancias en PDF | historias=['1-1-alta-y-acceso-del-socio-con-segundo-factor', '1-2-recuperación-de-acceso', '1-3-consulta-de-saldos-de-ahorro-y-préstamos', '1-4-descarga-de-constancias-en-pdf'] | nivel_traza=epica | epicas=['E-1'] | paquetes_wbs=['3.2'] | cobertura=planificado
… 34 de 42 más sin mostrar: filtrar con --estado/--epica/--cobertura o usar --limite 0 · 34 of 42 more not shown: filter or use --limite 0
```

```
$ python3 $EST/especificacion.py --proyecto gestion consultar AD-5
tipo_entidad: requisito
id: AD-5
tipo: AD
titulo: Autenticación detrás de `IdentityPort`; segundo factor obligatorio
fuente: _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md
linea: 62
cobertura: n/a
```

## Paso 3 · Escala de probabilidad e impacto (propuesta → aprobación del ejecutivo)
```
$ python3 $EST/estado.py --proyecto gestion umbrales-riesgo alto=15 medio=6
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto evaluacion-probabilidad-impacto --ruta 02-planificacion/enfoques/evaluacion-probabilidad-impacto.md --estado en-revision --version 0.1
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar evaluacion-probabilidad-impacto --por "Ejecutivo: Laura Méndez" --version 1.0 --fecha 2026-10-28
Copia congelada / frozen copy: 00-direccion/historial/evaluacion-probabilidad-impacto-v1.0.md
ok
```

## Paso 4 · Identificación: taller de riesgos (causa → evento → efecto) ligado a productos, WBS e interesados
```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=externo" --campo "causa=El padrón del núcleo operativo no tiene entorno de pruebas (AD-1)" --campo "evento=La integración de consulta se prueba tarde" --campo "efecto=Atraso del Release 1 y defectos en FR-3/FR-4" --campo "tipo=amenaza" --campo "probabilidad=4" --campo "impacto=4" --campo "impacto_monetario=30000" --campo "proximidad=corto-plazo" --campo "propietario=Diego Ferreira" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 3.2 · producto Portal del socio · interesado ST-003"
R-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=organizacional" --campo "causa=Los operadores temen perder tareas con la bandeja única (FR-9)" --campo "evento=Resistencia a usar la consola" --campo "efecto=Adopción baja de la consola y doble trabajo" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=4" --campo "impacto_monetario=15000" --campo "proximidad=mediano-plazo" --campo "propietario=Sofía Ramírez" --campo "ejecutor=Martín Suárez" --campo "notas=WBS 4.1 y 5.1 · producto Consola de operador · interesado ST-002"
R-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=tecnico" --campo "causa=El segundo factor depende de un proveedor de SMS nuevo (AD-5)" --campo "evento=El proveedor de SMS no cumple la disponibilidad" --campo "efecto=Socios sin poder ingresar (FR-1, NFR-2)" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=5" --campo "impacto_monetario=25000" --campo "proximidad=mediano-plazo" --campo "propietario=Diego Ferreira" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 3.1 · producto Portal del socio"
R-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=externo" --campo "causa=La interpretación de la Ley 18.331 sobre constancias no está cerrada (NFR-1)" --campo "evento=Cumplimiento exige cambios en FR-5" --campo "efecto=Retrabajo de constancias y atraso" --campo "tipo=amenaza" --campo "probabilidad=2" --campo "impacto=4" --campo "impacto_monetario=12000" --campo "proximidad=mediano-plazo" --campo "propietario=Laura Méndez" --campo "ejecutor=Andrea Costa" --campo "notas=WBS 3.2 · interesado ST-004"
R-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=gestion" --campo "causa=El proveedor rota desarrolladores entre clientes" --campo "evento=Pérdida de conocimiento en el equipo" --campo "efecto=Baja de velocidad" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=3" --campo "impacto_monetario=18000" --campo "proximidad=largo-plazo" --campo "propietario=Diego Ferreira" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 1.1"
R-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=comercial" --campo "causa=El generador de PDF del sistema de cartera ya existe" --campo "evento=Reutilizarlo para constancias (FR-5)" --campo "efecto=Ahorro de esfuerzo en WBS 3.2" --campo "tipo=oportunidad" --campo "probabilidad=3" --campo "impacto=3" --campo "impacto_monetario=8000" --campo "proximidad=corto-plazo" --campo "propietario=Sofía Ramírez" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 3.2 · producto Portal del socio"
R-006
```

## Paso 5 · Evaluación y perfil de riesgo (P×I, EMV, exposición)
```
$ python3 $EST/registro.py --proyecto gestion resumen --json --corte 2026-11-03
{
  "riesgos": {
    "total": 6,
    "por_estado": {
      "abierto": 6
    },
    "abiertos": 6,
    "altos_abiertos": 2,
    "umbrales": {
      "alto": 15.0,
      "medio": 6.0
    },
    "sin_respuesta": [
      "R-001",
      "R-002",
      "R-003",
      "R-004",
      "R-005",
      "R-006"
    ],
    "sin_propietario": [],
    "top": [
      "R-001 (16, alto) La integración de consulta se prueba tarde",
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-002 (12, medio) Resistencia a usar la consola",
      "R-005 (9, medio) Pérdida de conocimiento en el equipo",
      "R-006 (9, medio) Reutilizarlo para constancias (FR-5)"
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
    "total": 1
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
    "total": 4
  },
  "calidad": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "acciones": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0,
    "vencidas": [],
    "abiertas_por_responsable": {}
  },
  "fecha_corte": "2026-11-03"
}
```

```
$ python3 $EST/registro.py --proyecto gestion listar riesgos --abiertos
id=R-001 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=externo | causa=El padrón del núcleo operativo no tiene entorno de pruebas (AD-1) | evento=La integración de consulta se prueba tarde | efecto=Atraso del Release 1 y defectos en FR-3/FR-4 | tipo=amenaza | probabilidad=4 | impacto=4 | puntuacion=16 | impacto_monetario=30000 | valor_esperado=21000 | proximidad=corto-plazo | propietario=Diego Ferreira | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 3.2 · producto Portal del socio · interesado ST-003
id=R-002 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=organizacional | causa=Los operadores temen perder tareas con la bandeja única (FR-9) | evento=Resistencia a usar la consola | efecto=Adopción baja de la consola y doble trabajo | tipo=amenaza | probabilidad=3 | impacto=4 | puntuacion=12 | impacto_monetario=15000 | valor_esperado=7500 | proximidad=mediano-plazo | propietario=Sofía Ramírez | ejecutor=Martín Suárez | estado=abierto | notas=WBS 4.1 y 5.1 · producto Consola de operador · interesado ST-002
id=R-003 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=tecnico | causa=El segundo factor depende de un proveedor de SMS nuevo (AD-5) | evento=El proveedor de SMS no cumple la disponibilidad | efecto=Socios sin poder ingresar (FR-1, NFR-2) | tipo=amenaza | probabilidad=3 | impacto=5 | puntuacion=15 | impacto_monetario=25000 | valor_esperado=12500 | proximidad=mediano-plazo | propietario=Diego Ferreira | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 3.1 · producto Portal del socio
id=R-004 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=externo | causa=La interpretación de la Ley 18.331 sobre constancias no está cerrada (NFR-1) | evento=Cumplimiento exige cambios en FR-5 | efecto=Retrabajo de constancias y atraso | tipo=amenaza | probabilidad=2 | impacto=4 | puntuacion=8 | impacto_monetario=12000 | valor_esperado=3600 | proximidad=mediano-plazo | propietario=Laura Méndez | ejecutor=Andrea Costa | estado=abierto | notas=WBS 3.2 · interesado ST-004
id=R-005 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=gestion | causa=El proveedor rota desarrolladores entre clientes | evento=Pérdida de conocimiento en el equipo | efecto=Baja de velocidad | tipo=amenaza | probabilidad=3 | impacto=3 | puntuacion=9 | impacto_monetario=18000 | valor_esperado=9000 | proximidad=largo-plazo | propietario=Diego Ferreira | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 1.1
id=R-006 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=comercial | causa=El generador de PDF del sistema de cartera ya existe | evento=Reutilizarlo para constancias (FR-5) | efecto=Ahorro de esfuerzo en WBS 3.2 | tipo=oportunidad | probabilidad=3 | impacto=3 | puntuacion=9 | impacto_monetario=8000 | valor_esperado=4000 | proximidad=corto-plazo | propietario=Sofía Ramírez | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 3.2 · producto Portal del socio
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido
Sanidad de 'Portal de autoservicio para socios' (pre-proyecto/SU): 0 ERROR · 2 AVISO · 0 INFO
  AVISO REG-06 Riesgo alto R-001 sin respuesta o propietario.
  AVISO REG-06 Riesgo alto R-003 sin respuesta o propietario.
        → pm-riesgos.
```

## Paso 6 · Respuestas, riesgo residual, disparadores y acciones en el plan
```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-001 --campo "respuesta=reducir" --campo "acciones=spike de integración con datos sintéticos en el sprint 1; pedir entorno de pruebas a TI" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "disparador=spike sin datos del padrón al día 5" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-002 --campo "respuesta=reducir" --campo "acciones=taller con operadores y piloto de la bandeja en una sucursal" --campo "probabilidad_residual=2" --campo "impacto_residual=3" --campo "disparador=menos del 50 % de operadores usa la consola en el piloto" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-003 --campo "respuesta=transferir" --campo "acciones=SLA de 99,9 % con penalidad en el contrato del proveedor de SMS; correo como factor alternativo" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "disparador=dos caídas del proveedor en un mes" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-004 --campo "respuesta=aceptar" --campo "acciones=seguimiento mensual con cumplimiento; contingencia de 1 semana" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "disparador=dictamen de cumplimiento" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-005 --campo "respuesta=reducir" --campo "acciones=cláusula de permanencia del equipo clave y documentación de decisiones" --campo "probabilidad_residual=2" --campo "impacto_residual=3" --campo "disparador=salida de un desarrollador clave" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-006 --campo "respuesta=explotar" --campo "acciones=spike de reutilización del generador de PDF en el sprint 2" --campo "probabilidad_residual=4" --campo "impacto_residual=3" --campo "disparador=" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2026-11-03" --campo "origen=R-001" --campo "descripcion=Spike de integración con el padrón usando datos sintéticos" --campo "responsable=Lucía Benítez" --campo "fecha_compromiso=2026-12-11" --campo "prioridad=alta"
A-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2026-11-03" --campo "origen=R-002" --campo "descripcion=Taller con operadores y delegado sindical sobre la bandeja única" --campo "responsable=Martín Suárez" --campo "fecha_compromiso=2026-11-20" --campo "prioridad=alta"
A-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2026-11-03" --campo "origen=R-003" --campo "descripcion=Negociar SLA con penalidad con el proveedor de SMS" --campo "responsable=Diego Ferreira" --campo "fecha_compromiso=2026-11-25" --campo "prioridad=media"
A-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-04" --campo "decision=El propietario acepta la respuesta de R-001" --campo "decidido_por=Proveedor sénior: Diego Ferreira" --campo "nivel=gestor"
D-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-04" --campo "decision=El propietario acepta la respuesta de R-003" --campo "decidido_por=Proveedor sénior: Diego Ferreira" --campo "nivel=gestor"
D-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-04" --campo "decision=El propietario acepta la respuesta de R-005" --campo "decidido_por=Proveedor sénior: Diego Ferreira" --campo "nivel=gestor"
D-004
```

## Paso 7 · Presupuesto de riesgo (contingencia) y puerta autorizar-proyecto
```
$ python3 $EST/registro.py --proyecto gestion resumen --json --corte 2026-11-20
{
  "riesgos": {
    "total": 6,
    "por_estado": {
      "en-seguimiento": 6
    },
    "abiertos": 6,
    "altos_abiertos": 2,
    "umbrales": {
      "alto": 15.0,
      "medio": 6.0
    },
    "sin_respuesta": [],
    "sin_propietario": [],
    "top": [
      "R-001 (16, alto) La integración de consulta se prueba tarde",
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-002 (12, medio) Resistencia a usar la consola",
      "R-005 (9, medio) Pérdida de conocimiento en el equipo",
      "R-006 (9, medio) Reutilizarlo para constancias (FR-5)"
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
    "total": 4
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
    "total": 4
  },
  "calidad": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "acciones": {
    "total": 3,
    "por_estado": {
      "abierta": 3
    },
    "abiertos": 3,
    "vencidas": [],
    "abiertas_por_responsable": {
      "Lucía Benítez": 1,
      "Martín Suárez": 1,
      "Diego Ferreira": 1
    }
  },
  "fecha_corte": "2026-11-20"
}
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-27" --campo "decision=Presupuesto de riesgo de USD 23.000 dentro del BAC (EMV residual 30.000 menos 7.500 de R-003 transferido al proveedor); su uso lo autoriza el ejecutivo" --campo "decidido_por=Ejecutivo: Laura Méndez" --campo "nivel=ejecutivo" --campo "artefactos_afectados=02-planificacion/presupuesto.md"
D-005
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

## Paso 8 · Seguimiento en la etapa: revisión de riesgos del sprint (reevaluar, cerrar acciones, detectar vencidas)
```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-002 --campo "estado=completada" --campo "fecha_cierre=2026-11-19"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-003 --campo "estado=completada" --campo "fecha_cierre=2026-11-24"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-002 --campo "probabilidad=2" --campo "notas=WBS 4.1 y 5.1 · producto Consola de operador · interesado ST-002 · taller A-002 realizado: actitud mejoró" --campo "fecha_revision=2026-12-15"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-006 --campo "estado=cerrado" --campo "notas=WBS 3.2 · oportunidad aprovechada: generador reutilizado, ahorro 60 h" --campo "fecha_revision=2026-12-15"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion resumen --corte 2026-12-15
{
  "riesgos": {
    "total": 6,
    "por_estado": {
      "en-seguimiento": 5,
      "cerrado": 1
    },
    "abiertos": 5,
    "altos_abiertos": 2,
    "umbrales": {
      "alto": 15.0,
      "medio": 6.0
    },
    "sin_respuesta": [],
    "sin_propietario": [],
    "top": [
      "R-001 (16, alto) La integración de consulta se prueba tarde",
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-005 (9, medio) Pérdida de conocimiento en el equipo",
      "R-002 (8, medio) Resistencia a usar la consola",
      "R-004 (8, medio) Cumplimiento exige cambios en FR-5"
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
    "total": 10
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
    "total": 4
  },
  "calidad": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "acciones": {
    "total": 3,
    "por_estado": {
      "abierta": 1,
      "completada": 2
    },
    "abiertos": 1,
    "vencidas": [
      "A-001 Lucía Benítez 2026-12-11"
    ],
    "abiertas_por_responsable": {
      "Lucía Benítez": 1
    }
  },
  "fecha_corte": "2026-12-15"
}
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 0 INFO
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto tablero-avance --ruta 03-control/reportes/2026-12-15-tablero-avance.html --estado en-revision
ok
```

```
$ (pm-visuales arma el tablero con la receta de references/guia.md §3 → gestion/03-control/reportes/2026-12-15-tablero-avance.html)
riesgos abiertos 5 · issues 0 · acciones 3 · iteraciones 0
```

## Paso 9 · Un riesgo se materializa: de riesgo a issue
```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-001 --campo "estado=ocurrido" --campo "fecha_revision=2026-12-16" --campo "notas=WBS 3.2 · el spike A-001 confirmó que TI no da entorno de pruebas hasta febrero"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2026-12-16" --campo "tipo=problema-preocupacion" --campo "titulo=Sin entorno de pruebas del padrón hasta febrero (materializa R-001)" --campo "descripcion=Las historias 1-3 y 1-4 no pueden probarse contra el núcleo operativo" --campo "prioridad=alta" --campo "severidad=mayor" --campo "impacto=2 semanas de atraso en WBS 3.2" --campo "responsable=Martín Suárez"
I-001
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-001 --campo "estado=completada" --campo "fecha_cierre=2026-12-11"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion listar issues --abiertos
id=I-001 | fecha=2026-12-16 | tipo=problema-preocupacion | titulo=Sin entorno de pruebas del padrón hasta febrero (materializa R-001) | descripcion=Las historias 1-3 y 1-4 no pueden probarse contra el núcleo operativo | prioridad=alta | severidad=mayor | impacto=2 semanas de atraso en WBS 3.2 | responsable=Martín Suárez | estado=abierto
```

## Paso 10 · Riesgo nuevo sobre la línea: escalamiento a la junta
```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2027-01-08" --campo "autor=Martín Suárez" --campo "categoria=externo" --campo "causa=El regulador anunció nueva norma de autenticación para servicios financieros" --campo "evento=La norma exige biometría para operaciones de préstamo (FR-6)" --campo "efecto=Rediseño del acceso y atraso del Release 2" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=5" --campo "impacto_monetario=40000" --campo "proximidad=mediano-plazo" --campo "respuesta=escalar" --campo "propietario=Laura Méndez" --campo "ejecutor=Martín Suárez" --campo "estado=escalado" --campo "notas=WBS 3.1 y 3.3 · interesado ST-004 · afecta el business case: decide la junta"
R-007
```

```
$ python3 $EST/registro.py --proyecto gestion resumen --json --corte 2027-01-08
{
  "riesgos": {
    "total": 7,
    "por_estado": {
      "ocurrido": 1,
      "en-seguimiento": 4,
      "cerrado": 1,
      "escalado": 1
    },
    "abiertos": 5,
    "altos_abiertos": 2,
    "umbrales": {
      "alto": 15.0,
      "medio": 6.0
    },
    "sin_respuesta": [],
    "sin_propietario": [],
    "top": [
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-007 (15, alto) La norma exige biometría para operaciones de préstamo (FR-6)",
      "R-005 (9, medio) Pérdida de conocimiento en el equipo",
      "R-002 (8, medio) Resistencia a usar la consola",
      "R-004 (8, medio) Cumplimiento exige cambios en FR-5"
    ]
  },
  "issues": {
    "total": 1,
    "por_estado": {
      "abierto": 1
    },
    "abiertos": 1,
    "sin_responsable": []
  },
  "cambios": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "decisiones": {
    "total": 10
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
    "total": 4
  },
  "calidad": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "acciones": {
    "total": 3,
    "por_estado": {
      "completada": 3
    },
    "abiertos": 0,
    "vencidas": [],
    "abiertas_por_responsable": {}
  },
  "fecha_corte": "2027-01-08"
}
```

```
$ python3 $EST/estado.py --proyecto gestion puerta decision-ad-hoc --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-01-12 --condiciones "usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar R-007 en la próxima junta"
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-007 --campo "respuesta=reducir" --campo "acciones=análisis normativo con asesoría externa; diseño de autenticación reforzada detrás de IdentityPort (AD-5)" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "estado=en-seguimiento"
ok
```

## Paso 11 · Informe de riesgos e insumo para el highlight
```
$ python3 $EST/registro.py --proyecto gestion resumen --corte 2027-01-15
{
  "riesgos": {
    "total": 7,
    "por_estado": {
      "ocurrido": 1,
      "en-seguimiento": 5,
      "cerrado": 1
    },
    "abiertos": 5,
    "altos_abiertos": 2,
    "umbrales": {
      "alto": 15.0,
      "medio": 6.0
    },
    "sin_respuesta": [],
    "sin_propietario": [],
    "top": [
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-007 (15, alto) La norma exige biometría para operaciones de préstamo (FR-6)",
      "R-005 (9, medio) Pérdida de conocimiento en el equipo",
      "R-002 (8, medio) Resistencia a usar la consola",
      "R-004 (8, medio) Cumplimiento exige cambios en FR-5"
    ]
  },
  "issues": {
    "total": 1,
    "por_estado": {
      "abierto": 1
    },
    "abiertos": 1,
    "sin_responsable": []
  },
  "cambios": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "decisiones": {
    "total": 11
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
    "total": 4
  },
  "calidad": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "acciones": {
    "total": 3,
    "por_estado": {
      "completada": 3
    },
    "abiertos": 0,
    "vencidas": [],
    "abiertas_por_responsable": {}
  },
  "fecha_corte": "2027-01-15"
}
```

```
$ python3 $EST/puertas.py --proyecto gestion estado --markdown
### Puertas y verificación / Gates and verification

| Puerta | Fecha | Decisión | Por | Condiciones (estado) | Observaciones de la verificación | Lista |
|---|---|---|---|---|---|---|
| autorizar-inicio | 2026-10-30 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-17-verificacion-autorizar-inicio.md |
| autorizar-proyecto | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-17-verificacion-autorizar-proyecto.md |
| autorizar-etapa | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md |
| decision-ad-hoc | 2027-01-12 | aprobado | Ejecutivo: Laura Méndez | usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar R-007 en la próxima junta (abiertas) | — | — |

**Próxima puerta / Next gate: autorizar-etapa** — 2 bloqueo(s), 0 condición(es), 0 aviso(s).
- bloqueo: falta el plan de la etapa a autorizar (plan-etapa-3)
- bloqueo: falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto informe-riesgos-2027-01-15 --ruta 03-control/reportes/2027-01-15-informe-riesgos.md --estado en-revision
ok
```

## Paso 12 · Límite de etapa: auditoría de riesgos, lecciones y cierre de riesgos
```
$ python3 $EST/estado.py --proyecto gestion limite-etapa
ok
Fase: entrega · Proceso: SB · Etapa 2: Release 1 · Enfoque: hibrido
Límite de etapa (SB): informe de fin de etapa, plan de la siguiente etapa, actualizar plan de proyecto, business case, riesgos y lecciones. Puerta: autorizar-etapa (o si es la última etapa: estado.py cierre). Agentes: pm-planificacion + pm-control.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-001 --campo "estado=resuelto" --campo "fecha_cierre=2027-02-10" --campo "decision=entorno de pruebas habilitado el 2027-02-08"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-005 --campo "estado=retirado" --campo "notas=WBS 1.1 · equipo estable durante la etapa" --campo "fecha_revision=2027-03-01"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar lecciones --campo "etapa=2" --campo "categoria=riesgo" --campo "situacion=R-001 se materializó: el entorno de pruebas del núcleo dependía de otra área" --campo "efecto=2 semanas de atraso en WBS 3.2" --campo "recomendacion=exigir el entorno de pruebas como condición de la puerta autorizar-etapa" --campo "prioridad=alta" --campo "responsable_seguimiento=Martín Suárez"
L-001
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto auditoria-riesgos-2027-03-01 --ruta 03-control/reportes/2027-03-01-auditoria-riesgos.md --estado en-revision
ok
```

```
$ python3 $EST/registro.py --proyecto gestion resumen --corte 2027-03-01
{
  "riesgos": {
    "total": 7,
    "por_estado": {
      "ocurrido": 1,
      "en-seguimiento": 4,
      "retirado": 1,
      "cerrado": 1
    },
    "abiertos": 4,
    "altos_abiertos": 2,
    "umbrales": {
      "alto": 15.0,
      "medio": 6.0
    },
    "sin_respuesta": [],
    "sin_propietario": [],
    "top": [
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-007 (15, alto) La norma exige biometría para operaciones de préstamo (FR-6)",
      "R-002 (8, medio) Resistencia a usar la consola",
      "R-004 (8, medio) Cumplimiento exige cambios en FR-5"
    ]
  },
  "issues": {
    "total": 1,
    "por_estado": {
      "resuelto": 1
    },
    "abiertos": 0,
    "sin_responsable": []
  },
  "cambios": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "decisiones": {
    "total": 11
  },
  "supuestos": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "lecciones": {
    "total": 1,
    "por_estado": {
      "registrada": 1
    },
    "abiertos": 1
  },
  "stakeholders": {
    "total": 4
  },
  "calidad": {
    "total": 0,
    "por_estado": {},
    "abiertos": 0
  },
  "acciones": {
    "total": 3,
    "por_estado": {
      "completada": 3
    },
    "abiertos": 0,
    "vencidas": [],
    "abiertas_por_responsable": {}
  },
  "fecha_corte": "2027-03-01"
}
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-etapa
Puerta autorizar-etapa: 2 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   falta el plan de la etapa a autorizar (plan-etapa-3)
  BLOQUEO   falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/exportar.py xlsx --proyecto gestion
Escrito gestion/exportados/2026-10-17-registros.xlsx
```

```
$ (riesgos.csv al cierre de la etapa: id, tipo, P×I, residual, EMV, respuesta, estado)
R-001 amen P4×I4= 16 res P2×I4 EMV   21000 reducir    ocurrido
R-002 amen P2×I4=  8 res P2×I3 EMV    4500 reducir    en-seguimiento
R-003 amen P3×I5= 15 res P2×I4 EMV   12500 transferir en-seguimiento
R-004 amen P2×I4=  8 res P2×I4 EMV    3600 aceptar    en-seguimiento
R-005 amen P3×I3=  9 res P2×I3 EMV    9000 reducir    retirado
R-006 opor P3×I3=  9 res P4×I3 EMV    4000 explotar   cerrado
R-007 amen P3×I5= 15 res P2×I4 EMV   20000 reducir    en-seguimiento
```

