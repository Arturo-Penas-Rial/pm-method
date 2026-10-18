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

## Paso 2 · Identificar y valorar a los interesados (maestro único)
```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Laura Méndez" --campo "rol_organizacion=Gerenta de operaciones" --campo "rol_proyecto=Ejecutiva" --campo "poder=alto" --campo "interes=alto" --campo "actitud=lider" --campo "nivel_compromiso_actual=lider" --campo "nivel_compromiso_deseado=lider" --campo "canal=reunión 1:1" --campo "frecuencia=quincenal" --campo "responsable_relacion=Martín Suárez" --campo "confidencial=no" --campo "correo=laura.mendez@example.org" --campo "usuario_chat="
ST-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Consejo directivo" --campo "rol_organizacion=Órgano de gobierno de la cooperativa" --campo "rol_proyecto=Capa de negocio" --campo "poder=alto" --campo "interes=medio" --campo "actitud=partidario" --campo "nivel_compromiso_actual=partidario" --campo "nivel_compromiso_deseado=lider" --campo "canal=correo" --campo "frecuencia=trimestral" --campo "responsable_relacion=Laura Méndez" --campo "confidencial=no" --campo "correo=consejo@example.org" --campo "usuario_chat="
ST-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Sofía Ramírez" --campo "rol_organizacion=Jefa de atención al socio" --campo "rol_proyecto=Usuaria sénior y PO" --campo "poder=alto" --campo "interes=alto" --campo "actitud=lider" --campo "nivel_compromiso_actual=lider" --campo "nivel_compromiso_deseado=lider" --campo "canal=sprint review" --campo "frecuencia=quincenal" --campo "responsable_relacion=Martín Suárez" --campo "confidencial=no" --campo "correo=sofia.ramirez@example.org" --campo "usuario_chat=sofia.ramirez@example.org"
ST-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Sindicato de operadores" --campo "rol_organizacion=Representación de operadores de sucursal" --campo "rol_proyecto=Afectado" --campo "poder=medio" --campo "interes=alto" --campo "actitud=resistente" --campo "nivel_compromiso_actual=resistente" --campo "nivel_compromiso_deseado=neutral" --campo "canal=taller presencial" --campo "frecuencia=mensual" --campo "responsable_relacion=Sofía Ramírez" --campo "confidencial=si" --campo "correo=delegado.sindical@example.org" --campo "usuario_chat="
ST-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Socios usuarios piloto" --campo "rol_organizacion=Panel de 40 socios" --campo "rol_proyecto=Usuarios finales" --campo "poder=bajo" --campo "interes=alto" --campo "actitud=desconocedor" --campo "nivel_compromiso_actual=desconocedor" --campo "nivel_compromiso_deseado=partidario" --campo "canal=encuesta y boletín" --campo "frecuencia=mensual" --campo "responsable_relacion=Sofía Ramírez" --campo "confidencial=no" --campo "correo=panel.socios@example.org" --campo "usuario_chat="
ST-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Área de TI del núcleo operativo" --campo "rol_organizacion=Dueña del core y del padrón" --campo "rol_proyecto=Proveedor interno" --campo "poder=alto" --campo "interes=medio" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "canal=reunión técnica" --campo "frecuencia=semanal" --campo "responsable_relacion=Lucía Benítez" --campo "confidencial=no" --campo "correo=" --campo "usuario_chat="
ST-006
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Unidad de cumplimiento" --campo "rol_organizacion=Protección de datos" --campo "rol_proyecto=Asesor" --campo "poder=alto" --campo "interes=bajo" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "canal=correo y revisión" --campo "frecuencia=por hito" --campo "responsable_relacion=Andrea Costa" --campo "confidencial=no" --campo "correo=cumplimiento@example.org" --campo "usuario_chat="
ST-007
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Diego Ferreira" --campo "rol_organizacion=Gerente del proveedor" --campo "rol_proyecto=Proveedor sénior" --campo "poder=medio" --campo "interes=alto" --campo "actitud=partidario" --campo "nivel_compromiso_actual=partidario" --campo "nivel_compromiso_deseado=partidario" --campo "canal=reunión de junta" --campo "frecuencia=mensual" --campo "responsable_relacion=Martín Suárez" --campo "confidencial=no" --campo "correo=diego.ferreira@example.org" --campo "usuario_chat="
ST-008
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Martín Suárez" --campo "rol_organizacion=Gestor del proyecto" --campo "rol_proyecto=Gestor" --campo "poder=medio" --campo "interes=alto" --campo "actitud=lider" --campo "nivel_compromiso_actual=lider" --campo "nivel_compromiso_deseado=lider" --campo "canal=checkpoint" --campo "frecuencia=semanal" --campo "responsable_relacion=Laura Méndez" --campo "confidencial=no" --campo "correo=martin.suarez@example.org" --campo "usuario_chat=martin.suarez@example.org"
ST-009
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Lucía Benítez" --campo "rol_organizacion=Jefa de equipo del proveedor" --campo "rol_proyecto=Jefa de equipo" --campo "poder=bajo" --campo "interes=alto" --campo "actitud=partidario" --campo "nivel_compromiso_actual=partidario" --campo "nivel_compromiso_deseado=partidario" --campo "canal=daily" --campo "frecuencia=diaria" --campo "responsable_relacion=Martín Suárez" --campo "confidencial=no" --campo "correo=lucia.benitez@example.org" --campo "usuario_chat="
ST-010
```

```
$ python3 $EST/registro.py --proyecto gestion listar stakeholders
id=ST-001 | nombre=Laura Méndez | rol_organizacion=Gerenta de operaciones | rol_proyecto=Ejecutiva | poder=alto | interes=alto | actitud=lider | nivel_compromiso_actual=lider | nivel_compromiso_deseado=lider | canal=reunión 1:1 | frecuencia=quincenal | responsable_relacion=Martín Suárez | confidencial=no | correo=laura.mendez@example.org
id=ST-002 | nombre=Consejo directivo | rol_organizacion=Órgano de gobierno de la cooperativa | rol_proyecto=Capa de negocio | poder=alto | interes=medio | actitud=partidario | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=lider | canal=correo | frecuencia=trimestral | responsable_relacion=Laura Méndez | confidencial=no | correo=consejo@example.org
id=ST-003 | nombre=Sofía Ramírez | rol_organizacion=Jefa de atención al socio | rol_proyecto=Usuaria sénior y PO | poder=alto | interes=alto | actitud=lider | nivel_compromiso_actual=lider | nivel_compromiso_deseado=lider | canal=sprint review | frecuencia=quincenal | responsable_relacion=Martín Suárez | confidencial=no | correo=sofia.ramirez@example.org | usuario_chat=sofia.ramirez@example.org
id=ST-004 | nombre=Sindicato de operadores | rol_organizacion=Representación de operadores de sucursal | rol_proyecto=Afectado | poder=medio | interes=alto | actitud=resistente | nivel_compromiso_actual=resistente | nivel_compromiso_deseado=neutral | canal=taller presencial | frecuencia=mensual | responsable_relacion=Sofía Ramírez | confidencial=si | correo=delegado.sindical@example.org
id=ST-005 | nombre=Socios usuarios piloto | rol_organizacion=Panel de 40 socios | rol_proyecto=Usuarios finales | poder=bajo | interes=alto | actitud=desconocedor | nivel_compromiso_actual=desconocedor | nivel_compromiso_deseado=partidario | canal=encuesta y boletín | frecuencia=mensual | responsable_relacion=Sofía Ramírez | confidencial=no | correo=panel.socios@example.org
id=ST-006 | nombre=Área de TI del núcleo operativo | rol_organizacion=Dueña del core y del padrón | rol_proyecto=Proveedor interno | poder=alto | interes=medio | actitud=neutral | nivel_compromiso_actual=neutral | nivel_compromiso_deseado=partidario | canal=reunión técnica | frecuencia=semanal | responsable_relacion=Lucía Benítez | confidencial=no
id=ST-007 | nombre=Unidad de cumplimiento | rol_organizacion=Protección de datos | rol_proyecto=Asesor | poder=alto | interes=bajo | actitud=neutral | nivel_compromiso_actual=neutral | nivel_compromiso_deseado=partidario | canal=correo y revisión | frecuencia=por hito | responsable_relacion=Andrea Costa | confidencial=no | correo=cumplimiento@example.org
id=ST-008 | nombre=Diego Ferreira | rol_organizacion=Gerente del proveedor | rol_proyecto=Proveedor sénior | poder=medio | interes=alto | actitud=partidario | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=partidario | canal=reunión de junta | frecuencia=mensual | responsable_relacion=Martín Suárez | confidencial=no | correo=diego.ferreira@example.org
id=ST-009 | nombre=Martín Suárez | rol_organizacion=Gestor del proyecto | rol_proyecto=Gestor | poder=medio | interes=alto | actitud=lider | nivel_compromiso_actual=lider | nivel_compromiso_deseado=lider | canal=checkpoint | frecuencia=semanal | responsable_relacion=Laura Méndez | confidencial=no | correo=martin.suarez@example.org | usuario_chat=martin.suarez@example.org
id=ST-010 | nombre=Lucía Benítez | rol_organizacion=Jefa de equipo del proveedor | rol_proyecto=Jefa de equipo | poder=bajo | interes=alto | actitud=partidario | nivel_compromiso_actual=partidario | nivel_compromiso_deseado=partidario | canal=daily | frecuencia=diaria | responsable_relacion=Martín Suárez | confidencial=no | correo=lucia.benitez@example.org
```

## Paso 3 · Matriz poder/interés y estrategia por cuadrante
```
$ python3 $IN --proyecto gestion matriz
Gestionar de cerca (7): ST-001 Laura Méndez, ST-002 Consejo directivo ◇, ST-003 Sofía Ramírez, ST-004 Sindicato de operadores ◇, ST-006 Área de TI del núcleo operativo ◇, ST-008 Diego Ferreira ◇, ST-009 Martín Suárez ◇
   Los actores más críticos: comunicación constante, participación activa en las decisiones y máxima atención.
Mantener satisfecho (1): ST-007 Unidad de cumplimiento
   No abrumar con detalles; reportes ejecutivos de alto nivel sobre beneficios y avance.
Mantener informado (2): ST-005 Socios usuarios piloto, ST-010 Lucía Benítez
   Canales claros (boletines, reuniones informativas) y escucha activa de su retroalimentación: suelen ser aliados y fuente de información.
Monitorear (0): —
   Supervisar con el menor esfuerzo, sin gastar recursos innecesarios, salvo que cambien de posición en la matriz.
◇ = frontera ('medio' ubicado como alto)
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto analisis-stakeholders --ruta 01-inicio/analisis-stakeholders.md --estado en-revision
ok
```

## Paso 4 · Estereotipos y preferencias declaradas en una entrevista
```
$ python3 $IN --proyecto gestion estereotipos --semilla
6 estereotipos semilla creados (ET-001…ET-006); ajustarlos con registro.py actualizar estereotipos …
ET-001 direccion-patrocinador [activo] gestionar-de-cerca · reunion · conclusion-primero · ejecutivo · por-hito → —
ET-002 equipo [activo] mantener-informado ·  · lista · detallado · semanal → —
ET-003 cliente-usuario [activo] mantener-informado · correo · narrativa · resumen · quincenal → —
ET-004 proveedores [activo] mantener-satisfecho · correo · lista · resumen · por-hito → —
ET-005 regulador-comunidad [activo] mantener-satisfecho · correo · conclusion-primero · ejecutivo · por-hito → —
ET-006 product-owner-usuarios-clave [activo] gestionar-de-cerca · reunion · datos · detallado · semanal → —
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-001 --campo "estereotipo=ET-001"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-002 --campo "estereotipo=ET-001"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-003 --campo "estereotipo=ET-006"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-005 --campo "estereotipo=ET-003"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-007 --campo "estereotipo=ET-005"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-008 --campo "estereotipo=ET-004"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-009 --campo "estereotipo=ET-002"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-010 --campo "estereotipo=ET-002"
ok
```

```
$ python3 $IN --proyecto gestion estereotipos
ET-001 direccion-patrocinador [activo] gestionar-de-cerca · reunion · conclusion-primero · ejecutivo · por-hito → ST-001, ST-002
ET-002 equipo [activo] mantener-informado ·  · lista · detallado · semanal → ST-009, ST-010
ET-003 cliente-usuario [activo] mantener-informado · correo · narrativa · resumen · quincenal → ST-005
ET-004 proveedores [activo] mantener-satisfecho · correo · lista · resumen · por-hito → ST-008
ET-005 regulador-comunidad [activo] mantener-satisfecho · correo · conclusion-primero · ejecutivo · por-hito → ST-007
ET-006 product-owner-usuarios-clave [activo] gestionar-de-cerca · reunion · datos · detallado · semanal → ST-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar preferencias --campo "fecha=2026-11-03" --campo "stakeholder_id=ST-001" --campo "dimension=canal" --campo "valor=correo" --campo "procedencia=declarado" --campo "evidencia=«Prefiero que el avance me llegue por correo, no por chat.»" --campo "fuente=01-inicio/entrevistas/2026-11-03-laura-mendez.md" --campo "vigencia_hasta=2027-05-02"
PF-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar preferencias --campo "fecha=2026-11-03" --campo "stakeholder_id=ST-001" --campo "dimension=formato" --campo "valor=conclusion-primero" --campo "procedencia=declarado" --campo "evidencia=«Una página, con la conclusión y lo que tengo que decidir arriba.»" --campo "fuente=01-inicio/entrevistas/2026-11-03-laura-mendez.md" --campo "vigencia_hasta=2027-05-02"
PF-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar preferencias --campo "fecha=2026-11-03" --campo "stakeholder_id=ST-001" --campo "dimension=nivel_detalle" --campo "valor=ejecutivo" --campo "procedencia=declarado" --campo "evidencia=«Una página, con la conclusión y lo que tengo que decidir arriba.»" --campo "fuente=01-inicio/entrevistas/2026-11-03-laura-mendez.md" --campo "vigencia_hasta=2027-05-02"
PF-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar preferencias --campo "fecha=2026-11-03" --campo "stakeholder_id=ST-001" --campo "dimension=horario" --campo "valor=antes de las 9" --campo "procedencia=declarado" --campo "evidencia=«Los lunes antes de las 9 lo leo con calma.»" --campo "fuente=01-inicio/entrevistas/2026-11-03-laura-mendez.md" --campo "vigencia_hasta=2027-05-02"
PF-004
```

```
$ python3 $IN --proyecto gestion confirmar PF-001 PF-002 PF-003 PF-004 --por "Gestor: Martín Suárez"
confirmar: PF-001, PF-002, PF-003, PF-004
```

```
$ python3 $IN --proyecto gestion perfil ST-001 --corte 2026-11-03
ST-001 Laura Méndez · gestionar-de-cerca · estereotipo ET-001 · destino laura.mendez@example.org
   canal: correo  (PF-001 (declarado, 2026-11-03))
   formato: conclusion-primero  (PF-002 (declarado, 2026-11-03))
   nivel_detalle: ejecutivo  (PF-003 (declarado, 2026-11-03))
   frecuencia: quincenal  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: formal  (estereotipo:ET-001)
   horario: antes de las 9  (PF-004 (declarado, 2026-11-03))
   estilo_decision: datos  (estereotipo:ET-001)
```

## Paso 5 · Plan de compromiso, enfoque de comunicación y matriz de comunicaciones
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

## Paso 6 · Beneficios del business case, enfoque de beneficios y OKR ligados (B-n, SM-n), con tipos de KR, compromiso, peso e iniciativas
```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-beneficios --ruta 00-direccion/enfoque-beneficios.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto okr --ruta 00-direccion/okr.md --estado en-revision
ok
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --corte 2026-11-20
O-1 Los socios resuelven sus gestiones simples sin ir a la sucursal → 0.00 (rojo) · aspiracional
   KR-1.1 30 % de socios activos registrados en el portal [0/30 %] → 0.00 (rojo) · B-02; SM-1 · ST-003 · de-a · salud en-camino (esperado 0.04) · confianza 6 (ambar)
   KR-1.2 Bajar 30 % las consultas de saldo y constancias por canales tradicionales [5000/3500 consultas] → 0.00 (rojo) · B-01; SM-2 · ST-003 · de-a · salud en-camino (esperado 0.04) · confianza 5 (ambar)
O-2 Los préstamos simples se resuelven rápido y sin papeles → 0.00 (rojo) · comprometido
   KR-2.1 Respuesta a solicitudes simples en menos de 48 h hábiles [96/48 horas] → 0.00 (rojo) · B-03; SM-3 · ST-003 · mantener-bajo · salud en-riesgo (esperado 0.04) · confianza 6 (ambar)
   KR-2.2 Más del 90 % de las solicitudes llegan completas [60/90 %] → 0.00 (rojo) · B-03; SM-3 · ST-003 · de-a · salud en-camino (esperado 0.04) · confianza 7 (verde)
   KR-2.3 Bandeja única de solicitudes en producción para los operadores [0/3 iniciativas] → 0.00 (rojo) · B-03; SM-3 · ST-003 · hito · salud en-riesgo (esperado 0.14)
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-20
Sanidad de 'Portal de autoservicio para socios' (pre-proyecto/SU): 0 ERROR · 0 AVISO · 1 INFO
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

## Paso 7 · RACI sobre la WBS, la especificación (épicas y requisitos) y los KR; integridad del maestro
```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-1" --campo "stakeholder_id=ST-003" --campo "rol=A"
RC-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-1" --campo "stakeholder_id=ST-010" --campo "rol=R"
RC-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-1" --campo "stakeholder_id=ST-006" --campo "rol=C"
RC-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-1" --campo "stakeholder_id=ST-001" --campo "rol=I"
RC-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-3" --campo "stakeholder_id=ST-003" --campo "rol=A"
RC-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-3" --campo "stakeholder_id=ST-010" --campo "rol=R"
RC-006
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-3" --campo "stakeholder_id=ST-004" --campo "rol=C"
RC-007
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=E-3" --campo "stakeholder_id=ST-008" --campo "rol=C"
RC-008
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=NFR-1" --campo "stakeholder_id=ST-007" --campo "rol=A"
RC-009
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=NFR-1" --campo "stakeholder_id=ST-010" --campo "rol=R"
RC-010
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=NFR-1" --campo "stakeholder_id=ST-003" --campo "rol=C"
RC-011
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=3.1" --campo "stakeholder_id=ST-009" --campo "rol=A"
RC-012
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=3.1" --campo "stakeholder_id=ST-010" --campo "rol=R"
RC-013
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=3.1" --campo "stakeholder_id=ST-003" --campo "rol=I"
RC-014
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=KR-1.1" --campo "stakeholder_id=ST-001" --campo "rol=A"
RC-015
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=KR-1.1" --campo "stakeholder_id=ST-003" --campo "rol=R"
RC-016
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=KR-1.1" --campo "stakeholder_id=ST-005" --campo "rol=C"
RC-017
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=KR-1.1" --campo "stakeholder_id=ST-002" --campo "rol=I"
RC-018
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=KR-2.2" --campo "stakeholder_id=ST-001" --campo "rol=A"
RC-019
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=KR-2.2" --campo "stakeholder_id=ST-003" --campo "rol=R"
RC-020
```

```
$ python3 $EST/registro.py --proyecto gestion agregar raci --campo "elemento=KR-2.2" --campo "stakeholder_id=ST-002" --campo "rol=I"
RC-021
```

```
$ $EST/registro.py --proyecto gestion agregar raci --campo elemento=E-1 --campo stakeholder_id=ST-001 --campo rol=A   # segundo A: se rechaza
Integridad referencial:
  - duplicado elemento=E-1 + stakeholder_id=ST-001 (una fila por combinación: actualizar la existente)
  - elemento E-1 ya tiene un 'A' (exactamente uno: cambiar primero la otra fila)
```

```
$ python3 $IN --proyecto gestion raci --markdown gestion/02-planificacion/matriz-raci.md
| Elemento | Descripción | ST-001 Laura Méndez | ST-002 Consejo… | ST-003 Sofía Ramírez | ST-004 Sindicato de… | ST-005 Socios usuarios… | ST-006 Área de TI del… | ST-007 Unidad de… | ST-008 Diego Ferreira | ST-009 Martín Suárez | ST-010 Lucía Benítez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E-1 | Acceso seguro y consulta de mis productos | I |  | A |  |  | C |  |  |  | R |
| E-3 | Consola de operador |  |  | A | C |  |  |  | C |  | R |
| NFR-1 | Seguridad y privacidad: cumplimiento de la Ley 18.331 de protección de datos personales d… |  |  | C |  |  |  | A |  |  | R |
| 3.1 | Acceso seguro |  |  | I |  |  |  |  |  | A | R |
| KR-1.1 | 30 % de socios activos registrados en el portal | A | I | R |  | C |  |  |  |  |  |
| KR-2.2 | Más del 90 % de las solicitudes llegan completas | A | I | R |  |  |  |  |  |  |  |

Leyenda: R responsable · A aprobador (uno por elemento) · C consultado · I informado.
RACI válida: un A por elemento, al menos un R, referencias existentes.
→ gestion/02-planificacion/matriz-raci.md
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto matriz-raci --ruta 02-planificacion/matriz-raci.md --estado en-revision
ok
```

```
$ python3 $IN --proyecto gestion raci --elemento E-3
E-3 (epica) Consola de operador
   A  ST-003 Sofía Ramírez
   R  ST-010 Lucía Benítez
   C  ST-004 Sindicato de operadores
   C  ST-008 Diego Ferreira
```

```
$ python3 $IN --proyecto gestion integridad
Integridad referencial y calidad del maestro: sin hallazgos.
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
$ python3 $EST/estado.py --proyecto gestion artefacto pid --ruta 00-direccion/pid.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto plan-proyecto --ruta 02-planificacion/plan-proyecto.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "riesgo=ningún riesgo alto sin respuesta" "beneficios=-10 %"
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-proyecto --fecha 2026-11-27
Lista creada: 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md (0 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-proyecto --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27
Lista 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md confirmada por Ejecutivo: Laura Méndez
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
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa --fecha 2026-11-27
Lista creada: 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md (2 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27
Lista 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md confirmada por Ejecutivo: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision condicionado --por "Ejecutivo: Laura Méndez" --fecha 2026-11-27 --etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=+2 semanas" "costo=±10 %"
Condiciones agregadas desde la verificación: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
Condiciones abiertas: autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)
```

## Paso 8 · Taller con interesados → acta, decisiones, acciones y preferencias declaradas
```
$ (transcripción de ejemplo: copiala a gestion/03-control/reuniones/2026-11-19-taller-bandeja-original.vtt)
WEBVTT

00:00:01.000 --> 00:00:09.000
<v Sofía Ramírez>Buen día, este es el taller de la bandeja única con operadores. A mí mandame las novedades del proyecto por Teams.

00:00:10.000 --> 00:00:21.000
<v Delegado sindical>Nos preocupa que la bandeja se use para medir productividad individual. Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas.

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
$ python3 $IN --proyecto gestion proponer --transcripcion gestion/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md --mapa "Delegado sindical=ST-004" --fecha 2026-11-19 --registrar
PF-005 ST-003 canal=teams (declarado) "A mí mandame las novedades del proyecto por Teams." [00:00:01]
PF-006 ST-004 canal=correo (declarado) "Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas." [00:00:10]
PF-007 ST-004 nivel_detalle=ejecutivo (declarado) "Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas." [00:00:10]
PF-008 ST-004 frecuencia=quincenal (declarado) "Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas." [00:00:10]
Estado: propuesta. Nada se aplica hasta que el gestor confirme con la persona: interesados.py confirmar PF-… --por "Rol: Nombre".
```

```
$ python3 $IN --proyecto gestion confirmar PF-005 PF-006 PF-007 PF-008 --por "Gestor: Martín Suárez"
confirmar: PF-005, PF-006, PF-007, PF-008
```

```
$ python3 $IN --proyecto gestion perfil ST-004 --corte 2026-11-19
ST-004 Sindicato de operadores · gestionar-de-cerca ◇ · estereotipo — · destino delegado.sindical@example.org
   canal: correo  (PF-006 (declarado, 2026-11-19))
   formato: conclusion-primero  (cuadrante:gestionar-de-cerca)
   nivel_detalle: ejecutivo  (PF-007 (declarado, 2026-11-19))
   frecuencia: quincenal  (PF-008 (declarado, 2026-11-19))
   idioma: es  (idioma del proyecto)
   AVISO frecuencia: la preferencia confirmada PF-008 (quincenal) difiere de la matriz aprobada (mensual); actualizar la matriz (pm-comunicacion-stakeholders)
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-004 --campo "frecuencia=quincenal"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto comunicado-operadores --ruta 03-control/reportes/2026-11-21-comunicado-bandeja.md --estado en-revision
ok
```

## Paso 9 · Avance de la etapa: serie EVM, avance BMAD, check-ins de OKR y registros a la fecha de corte
```
$ python3 $EST/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 124000 --tol-costo 10 --tol-plazo 10 --proyecto gestion --guardar --corte 2027-01-08
Guardado: 03-control/reportes/evm-2027-01-08.json
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
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Sprint review 1: historia 1-1" --campo "metodo_verificacion=demostracion" --campo "criterios=criterios de aceptación de cada historia y definición de terminado" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Sofía Ramírez" --campo "aprobador=Product owner: Sofía Ramírez" --campo "fecha_prevista=2026-12-11" --campo "fecha_real=2026-12-11" --campo "resultado=aprobado" --campo "estado=completada"
Q-001
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2026-12-11
Historias 10 · backlog 9 · ready-for-dev 0 · in-progress 0 · review 0 · done 1 · épicas terminadas 0/3 · 11.8 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-1.1 --valor 1 --confianza 7 --fecha 2026-12-11 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-1.1 2026-12-11 = 1 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-1.2 --valor 4950 --confianza 6 --fecha 2026-12-11 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-1.2 2026-12-11 = 4950 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-2.1 --valor 92 --confianza 4 --fecha 2026-12-11 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-2.1 2026-12-11 = 92 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-2.2 --valor 64 --confianza 6 --fecha 2026-12-11 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-2.2 2026-12-11 = 64 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Sprint review 2: historia 1-2 e historia 3-1" --campo "metodo_verificacion=demostracion" --campo "criterios=criterios de aceptación de cada historia y definición de terminado" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Sofía Ramírez" --campo "aprobador=Product owner: Sofía Ramírez" --campo "fecha_prevista=2026-12-23" --campo "fecha_real=2026-12-23" --campo "resultado=aprobado" --campo "estado=completada"
Q-002
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2026-12-23
Historias 10 · backlog 7 · ready-for-dev 0 · in-progress 0 · review 0 · done 3 · épicas terminadas 0/3 · 26.5 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-1.1 --valor 2 --confianza 7 --fecha 2026-12-23 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-1.1 2026-12-23 = 2 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-1.2 --valor 4900 --confianza 6 --fecha 2026-12-23 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-1.2 2026-12-23 = 4900 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-2.1 --valor 88 --confianza 4 --fecha 2026-12-23 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-2.1 2026-12-23 = 88 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-2.2 --valor 68 --confianza 6 --fecha 2026-12-23 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-2.2 2026-12-23 = 68 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $EST/registro.py --proyecto gestion agregar calidad --campo "producto=Sprint review 3: historia 1-3" --campo "metodo_verificacion=demostracion" --campo "criterios=criterios de aceptación de cada historia y definición de terminado" --campo "responsable_productor=Lucía Benítez" --campo "revisores=Sofía Ramírez" --campo "aprobador=Product owner: Sofía Ramírez" --campo "fecha_prevista=2027-01-08" --campo "fecha_real=2027-01-08" --campo "resultado=aprobado" --campo "estado=completada"
Q-003
```

```
$ python3 $BMAD --proyecto gestion avance --corte 2027-01-08
Historias 10 · backlog 5 · ready-for-dev 0 · in-progress 1 · review 0 · done 4 · épicas terminadas 0/3 · 38.2 % (puntos) → gestion/03-control/reportes/avance-bmad.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-1.1 --valor 3 --confianza 7 --fecha 2027-01-08 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-1.1 2027-01-08 = 3 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-1.2 --valor 4800 --confianza 6 --fecha 2027-01-08 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-1.2 2027-01-08 = 4800 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-2.1 --valor 80 --confianza 5 --fecha 2027-01-08 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-2.1 2027-01-08 = 80 → <repo>/gestion/00-direccion/okr_checkins.csv
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --checkin KR-2.2 --valor 72 --confianza 6 --fecha 2027-01-08 --autor "Usuaria sénior: Sofía Ramírez"
Check-in KR-2.2 2027-01-08 = 72 → <repo>/gestion/00-direccion/okr_checkins.csv
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
    "total": 10
  },
  "estereotipos": {
    "total": 6,
    "por_estado": {
      "activo": 6
    },
    "abiertos": 6
  },
  "preferencias": {
    "total": 8,
    "por_estado": {
      "confirmada": 8
    },
    "abiertos": 0
  },
  "raci": {
    "total": 21
  },
  "calidad": {
    "total": 3,
    "por_estado": {
      "completada": 3
    },
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

## Paso 10 · Highlight report con puertas, OKR al corte (salud y check-ins), sincronización con Tability y tablero por actor
```
$ python3 $OKR gestion/00-direccion/okr.csv --corte 2027-01-08 --markdown gestion/03-control/reportes/2027-01-08-okr.md
O-1 Los socios resuelven sus gestiones simples sin ir a la sucursal → 0.11 (rojo) · aspiracional
   KR-1.1 30 % de socios activos registrados en el portal [3/30 %] → 0.10 (rojo) · B-02; SM-1 · ST-003 · de-a · salud en-camino (esperado 0.16) · confianza 7 (verde)
   KR-1.2 Bajar 30 % las consultas de saldo y constancias por canales tradicionales [4800/3500 consultas] → 0.13 (rojo) · B-01; SM-2 · ST-003 · de-a · salud en-camino (esperado 0.16) · confianza 6 (ambar)
O-2 Los préstamos simples se resuelven rápido y sin papeles → 0.24 (rojo) · comprometido
   KR-2.1 Respuesta a solicitudes simples en menos de 48 h hábiles [80/48 horas] → 0.00 (rojo) · B-03; SM-3 · ST-003 · mantener-bajo · salud en-riesgo (esperado 0.16) · confianza 5 (ambar)
   KR-2.2 Más del 90 % de las solicitudes llegan completas [72/90 %] → 0.40 (rojo) · B-03; SM-3 · ST-003 · de-a · salud en-camino (esperado 0.16) · confianza 6 (ambar)
   KR-2.3 Bandeja única de solicitudes en producción para los operadores [1/3 iniciativas] → 0.33 (rojo) · B-03; SM-3 · ST-003 · hito · salud en-riesgo (esperado 0.52)
Tabla escrita en gestion/03-control/reportes/2027-01-08-okr.md
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --propuesta-sync tability
KR-1.1 2026-12-11 = 1 → tability:kr-registro-portal · tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp) · confidence green
KR-1.1 2026-12-23 = 2 → tability:kr-registro-portal · tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp) · confidence green
KR-1.1 2027-01-08 = 3 → tability:kr-registro-portal · tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp) · confidence green
AVISO KR-1.2: sin ref_externa 'tability:…' (vincular el KR con su par en tability antes de publicar)
AVISO KR-2.1: sin ref_externa 'tability:…' (vincular el KR con su par en tability antes de publicar)
AVISO KR-2.2: sin ref_externa 'tability:…' (vincular el KR con su par en tability antes de publicar)
```

```
$ python3 $OKR gestion/00-direccion/okr.csv --marcar-publicado KR-1.1@2027-01-08 --destino tability --ref checkin-ejemplo-1
KR-1.1@2027-01-08 marcado como publicado en tability
```

```
$ python3 $EST/puertas.py --proyecto gestion estado --markdown
### Puertas y verificación / Gates and verification

| Puerta | Fecha | Decisión | Por | Condiciones (estado) | Observaciones de la verificación | Lista |
|---|---|---|---|---|---|---|
| autorizar-inicio | 2026-10-30 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md |
| autorizar-proyecto | 2026-11-27 | aprobado | Ejecutivo: Laura Méndez | — | — | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md |
| autorizar-etapa | 2026-11-27 | condicionado | Ejecutivo: Laura Méndez | gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada) (abiertas) | gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada) | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md |

**Próxima puerta / Next gate: autorizar-etapa** — 2 bloqueo(s), 2 condición(es), 0 aviso(s).
- bloqueo: falta el plan de la etapa a autorizar (plan-etapa-3)
- bloqueo: falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
- condición: condiciones abiertas de puertas anteriores: autorizar-etapa 2026-11-27 (verificarlas y registrar estado.py cumplir-condiciones, o traspasarlas como recomendación)
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

```
$ python3 $EST/estado.py --proyecto gestion cumplir-condiciones autorizar-etapa --fecha 2027-01-08 --por "Ejecutiva: Laura Méndez" --nota "prueba de carga de NFR-3 planificada en el sprint 5 (plan de la etapa 2, Lucía Benítez)"
ok
```

## Paso 11 · Comunicación personalizada por perfil y envío por la capa de canales
```
$ python3 $EST/estado.py --proyecto gestion artefacto comunicado-consejo --ruta 03-control/reportes/2027-01-15-comunicado-consejo.md --estado en-revision
ok
```

```
$ python3 $IN --proyecto gestion plan-envio --tema "Avance del portal al 8 de enero" --audiencia "cuadrante:gestionar-de-cerca,cuadrante:mantener-satisfecho,-ST-009" --proposito informe --base gestion/03-control/reportes/2027-01-15-comunicado-consejo.md --agrupar --fecha 2027-01-15
Plan de envío → 03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero/ (7 destinatarios, 5 mensajes en borrador)
   ST-001 Laura Méndez: correo → laura.mendez@example.org · conclusion-primero · ejecutivo · es · mensaje-01-correo-st-001-st-002-st-007.md
   ST-002 Consejo directivo: correo → consejo@example.org · conclusion-primero · ejecutivo · es · mensaje-01-correo-st-001-st-002-st-007.md
   ST-003 Sofía Ramírez: teams → sofia.ramirez@example.org · datos · detallado · es · mensaje-02-teams-st-003.md
   ST-004 Sindicato de operadores: correo → delegado.sindical@example.org · conclusion-primero · ejecutivo · es · mensaje-03-correo-st-004.md
   ST-006 Área de TI del núcleo operativo: reunion → — · conclusion-primero · resumen · es · mensaje-04-reunion-st-006.md
   ST-008 Diego Ferreira: correo → diego.ferreira@example.org · lista · resumen · es · mensaje-05-correo-st-008.md
   ST-007 Unidad de cumplimiento: correo → cumplimiento@example.org · conclusion-primero · ejecutivo · es · mensaje-01-correo-st-001-st-002-st-007.md
AVISO ST-006 Área de TI del núcleo operativo: canal preferido «reunion» no es electrónico: entregarlo por esa vía y registrarlo con envios.py registrar --modo manual
Siguiente: redactar cada mensaje según su perfil, aprobar con envios.py aprobar y enviar con envios.py enviar (simulación por defecto).
```

```
$ python3 $EV --proyecto gestion estado gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero
mensaje-01-correo-st-001-st-002-st-007.md: correo → ST-001;ST-002;ST-007 · borrador
mensaje-02-teams-st-003.md: teams → ST-003 · borrador
mensaje-03-correo-st-004.md: correo → ST-004 · borrador
mensaje-04-reunion-st-006.md: reunion → ST-006 · borrador
mensaje-05-correo-st-008.md: correo → ST-008 · borrador
```

```
$ python3 $EV --proyecto gestion aprobar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --por "Gestor: Martín Suárez"
5 mensaje(s) aprobados por Gestor: Martín Suárez
```

```
$ python3 $EV --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --modo smtp
SIMULACIÓN mensaje-01-correo-st-001-st-002-st-007.md [smtp] → ST-001 <laura.mendez@example.org>, ST-002 <consejo@example.org>, ST-007 <cumplimiento@example.org> · «Avance del portal al 8 de enero»
   Decisión que se pide: aprobar USD 4.000 de contingencia para el incentivo del panel de socios (R-001) antes del 22/1.  Estado: ámbar y dentro de tolerancia. Costo +6,2 % (tolerancia 10 %), Release 1 prevista el 12/3 (+1 semana). OKR O-1 0,1…
   (faltan variables de entorno: PM_SMTP_HOST, PM_SMTP_REMITENTE)
· mensaje-02-teams-st-003.md: canal teams no corresponde a --modo smtp
SIMULACIÓN mensaje-03-correo-st-004.md [smtp] → ST-004 <delegado.sindical@example.org> · «Avance del portal al 8 de enero»
   Resumen del avance: la bandeja muestra solo métricas del equipo, como se acordó en el taller (D-006). El prototipo se presentará a los operadores antes del sprint 4.
   (faltan variables de entorno: PM_SMTP_HOST, PM_SMTP_REMITENTE)
· mensaje-04-reunion-st-006.md: canal reunion no corresponde a --modo smtp
SIMULACIÓN mensaje-05-correo-st-008.md [smtp] → ST-008 <diego.ferreira@example.org> · «Avance del portal al 8 de enero»
   - Hitos: Release 1 el 12/3 (+1 semana); su aceptación técnica sigue el 5/3 para la bandeja. - Dependencias: ambiente de prueba de carga (NFR-3) antes del sprint 5. - Pedido: confirmar la capacidad del equipo para los sprints 4 y 5.
   (faltan variables de entorno: PM_SMTP_HOST, PM_SMTP_REMITENTE)
Resumen: 0 enviados, 0 fallidos, 3 simulados, 2 omitidos · simulación: agregar --confirmar para enviar
```

```
$ python3 $EV --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --modo smtp --confirmar --fecha 2027-01-15
mensaje-01-correo-st-001-st-002-st-007.md: enviado · EN-001, EN-002, EN-003
· mensaje-02-teams-st-003.md: canal teams no corresponde a --modo smtp
mensaje-03-correo-st-004.md: enviado · EN-004
· mensaje-04-reunion-st-006.md: canal reunion no corresponde a --modo smtp
mensaje-05-correo-st-008.md: enviado · EN-005
Resumen: 5 enviados, 0 fallidos, 0 simulados, 2 omitidos
```

```
$ python3 $EV --proyecto gestion enviar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --modo teams-webhook --confirmar --fecha 2027-01-15
· mensaje-01-correo-st-001-st-002-st-007.md: canal correo no corresponde a --modo teams-webhook
mensaje-02-teams-st-003.md: enviado · EN-006
· mensaje-03-correo-st-004.md: canal correo no corresponde a --modo teams-webhook
· mensaje-04-reunion-st-006.md: canal reunion no corresponde a --modo teams-webhook
· mensaje-05-correo-st-008.md: canal correo no corresponde a --modo teams-webhook
Resumen: 1 enviados, 0 fallidos, 0 simulados, 4 omitidos
```

```
$ python3 $EV --proyecto gestion registrar gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero --mensaje mensaje-04-reunion-st-006.md --modo manual --referencia "reunión técnica del 2027-01-18" --fecha 2027-01-18
EN-007
```

```
$ (lo que recibieron los servidores de prueba de 127.0.0.1)
{
 "correos": [
  [
   "rcpt to:<laura.mendez@example.org>"
  ],
  [
   "rcpt to:<consejo@example.org>"
  ],
  [
   "rcpt to:<cumplimiento@example.org>"
  ],
  [
   "rcpt to:<delegado.sindical@example.org>"
  ],
  [
   "rcpt to:<diego.ferreira@example.org>"
  ]
 ],
 "teams": [
  "Avance del portal al 8 de enero"
 ]
}
```

```
$ python3 $EV --proyecto gestion historial
EN-001 2027-01-15 ST-001 correo/smtp «Avance del portal al 8 de enero» [enviado] <message-id>
EN-002 2027-01-15 ST-002 correo/smtp «Avance del portal al 8 de enero» [enviado] <message-id>
EN-003 2027-01-15 ST-007 correo/smtp «Avance del portal al 8 de enero» [enviado] <message-id>
EN-004 2027-01-15 ST-004 correo/smtp «Avance del portal al 8 de enero» [enviado] <message-id>
EN-005 2027-01-15 ST-008 correo/smtp «Avance del portal al 8 de enero» [enviado] <message-id>
EN-006 2027-01-15 ST-003 teams/teams-webhook «Avance del portal al 8 de enero» [enviado] teams-webhook HTTP 200
EN-007 2027-01-18 ST-006 reunion/manual «Avance del portal al 8 de enero» [enviado] reunión técnica del 2027-01-18
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-003 --campo "estado=completada" --campo "fecha_cierre=2027-01-15"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-004 --campo "estado=completada" --campo "fecha_cierre=2027-01-14" --campo "notas=prototipo con métricas de equipo presentado a los operadores (vencida desde el 11/12, informada en el highlight)"
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
id=A-004 | fecha=2026-11-19 | origen=acta-2026-11-19-taller-bandeja | descripcion=Prototipo de bandeja con métricas de equipo | responsable=Lucía Benítez | fecha_compromiso=2026-12-11 | prioridad=alta | estado=completada | fecha_cierre=2027-01-14 | notas=prototipo con métricas de equipo presentado a los operadores (vencida desde el 11/12, informada en el highlight)
```

## Paso 12 · Reporte de interesados, vínculos en el ecosistema e integridad
```
$ python3 $IN --proyecto gestion reporte --html gestion/03-control/reportes/2027-01-15-interesados.html --markdown gestion/03-control/reportes/2027-01-15-interesados.md --corte 2027-01-15
Reporte de interesados → gestion/03-control/reportes/2027-01-15-interesados.html gestion/03-control/reportes/2027-01-15-interesados.md · 10 ubicados, 6 elementos RACI, 0 hallazgos
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto reporte-interesados --ruta 03-control/reportes/2027-01-15-interesados.html --estado borrador
ok
```

```
$ python3 $IN --proyecto gestion perfil todos --corte 2027-01-15
ST-001 Laura Méndez · gestionar-de-cerca · estereotipo ET-001 · destino laura.mendez@example.org
   canal: correo  (PF-001 (declarado, 2026-11-03))
   formato: conclusion-primero  (PF-002 (declarado, 2026-11-03))
   nivel_detalle: ejecutivo  (PF-003 (declarado, 2026-11-03))
   frecuencia: quincenal  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: formal  (estereotipo:ET-001)
   horario: antes de las 9  (PF-004 (declarado, 2026-11-03))
   estilo_decision: datos  (estereotipo:ET-001)
ST-002 Consejo directivo · gestionar-de-cerca ◇ · estereotipo ET-001 · destino consejo@example.org
   canal: correo  (matriz de comunicaciones)
   formato: conclusion-primero  (estereotipo:ET-001)
   nivel_detalle: ejecutivo  (estereotipo:ET-001)
   frecuencia: trimestral  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: formal  (estereotipo:ET-001)
   estilo_decision: datos  (estereotipo:ET-001)
ST-003 Sofía Ramírez · gestionar-de-cerca · estereotipo ET-006 · destino sofia.ramirez@example.org
   canal: teams  (PF-005 (declarado, 2026-11-19))
   formato: datos  (estereotipo:ET-006)
   nivel_detalle: detallado  (estereotipo:ET-006)
   frecuencia: quincenal  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: neutral  (estereotipo:ET-006)
   estilo_decision: datos  (estereotipo:ET-006)
ST-004 Sindicato de operadores · gestionar-de-cerca ◇ · estereotipo — · destino delegado.sindical@example.org
   canal: correo  (PF-006 (declarado, 2026-11-19))
   formato: conclusion-primero  (cuadrante:gestionar-de-cerca)
   nivel_detalle: ejecutivo  (PF-007 (declarado, 2026-11-19))
   frecuencia: quincenal  (PF-008 (declarado, 2026-11-19))
   idioma: es  (idioma del proyecto)
ST-005 Socios usuarios piloto · mantener-informado · estereotipo ET-003 · destino panel.socios@example.org
   canal: correo  (estereotipo:ET-003)
   formato: narrativa  (estereotipo:ET-003)
   nivel_detalle: resumen  (estereotipo:ET-003)
   frecuencia: mensual  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: neutral  (estereotipo:ET-003)
ST-006 Área de TI del núcleo operativo · gestionar-de-cerca ◇ · estereotipo — · destino —
   canal: reunion  (cuadrante:gestionar-de-cerca)
   formato: conclusion-primero  (cuadrante:gestionar-de-cerca)
   nivel_detalle: resumen  (cuadrante:gestionar-de-cerca)
   frecuencia: semanal  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
ST-007 Unidad de cumplimiento · mantener-satisfecho · estereotipo ET-005 · destino cumplimiento@example.org
   canal: correo  (estereotipo:ET-005)
   formato: conclusion-primero  (estereotipo:ET-005)
   nivel_detalle: ejecutivo  (estereotipo:ET-005)
   frecuencia: por-hito  (estereotipo:ET-005)
   idioma: es  (idioma del proyecto)
   registro: formal  (estereotipo:ET-005)
ST-008 Diego Ferreira · gestionar-de-cerca ◇ · estereotipo ET-004 · destino diego.ferreira@example.org
   canal: correo  (estereotipo:ET-004)
   formato: lista  (estereotipo:ET-004)
   nivel_detalle: resumen  (estereotipo:ET-004)
   frecuencia: mensual  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: formal  (estereotipo:ET-004)
ST-009 Martín Suárez · gestionar-de-cerca ◇ · estereotipo ET-002 · destino —
   canal: reunion  (cuadrante:gestionar-de-cerca)
   formato: lista  (estereotipo:ET-002)
   nivel_detalle: detallado  (estereotipo:ET-002)
   frecuencia: semanal  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: cercano  (estereotipo:ET-002)
ST-010 Lucía Benítez · mantener-informado · estereotipo ET-002 · destino lucia.benitez@example.org
   canal: correo  (cuadrante:mantener-informado)
   formato: lista  (estereotipo:ET-002)
   nivel_detalle: detallado  (estereotipo:ET-002)
   frecuencia: diaria  (matriz de comunicaciones)
   idioma: es  (idioma del proyecto)
   registro: cercano  (estereotipo:ET-002)
```

```
$ python3 $IN --proyecto gestion vinculos ST-003
ST-003 Sofía Ramírez · Usuaria sénior y PO · gestionar-de-cerca · estereotipo ET-006
   RACI A en E-1 (epica) Acceso seguro y consulta de mis productos
   RACI A en E-3 (epica) Consola de operador
   RACI C en NFR-1 (requisito) Seguridad y privacidad: cumplimiento de la Ley 18.331 de protección de datos personales d…
   RACI I en 3.1 (paquete) Acceso seguro
   RACI R en KR-1.1 (kr) 30 % de socios activos registrados en el portal
   RACI R en KR-2.2 (kr) Más del 90 % de las solicitudes llegan completas
   OKR KR-1.1 (kr) 30 % de socios activos registrados en el portal
   OKR KR-1.2 (kr) Bajar 30 % las consultas de saldo y constancias por canales tradicionales
   OKR KR-2.1 (kr) Respuesta a solicitudes simples en menos de 48 h hábiles
   OKR KR-2.2 (kr) Más del 90 % de las solicitudes llegan completas
   OKR KR-2.3 (kr) Bandeja única de solicitudes en producción para los operadores
   riesgos R-001 (propietario, en-seguimiento)
   acciones A-001 (responsable, completada)
   acciones A-002 (responsable, completada)
   calidad Q-001 (revisores, completada)
   calidad Q-002 (revisores, completada)
   calidad Q-003 (revisores, completada)
   decisiones D-006 (decidido_por, )
   PF-005 canal=teams [confirmada]
   EN-006 2027-01-15 teams «Avance del portal al 8 de enero» [enviado]
```

```
$ python3 $IN --proyecto gestion integridad --corte 2027-01-15
Integridad referencial y calidad del maestro: sin hallazgos.
```

```
$ python3 $BMAD --proyecto gestion backlog
backlog.csv: 0 nuevas, 10 actualizadas, 0 retiradas en BMAD. Columnas derivadas (criterios_aceptacion, descripcion, estado, origen, refs, tipo, titulo) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-15
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 2 INFO
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
  INFO  TOL-02 El EVM del 2027-01-08 está en ámbar (costo=ambar, cronograma=ambar): 50–100 % de la tolerancia.
        → Anticipar acciones correctivas y reportarlo en el highlight.
```

```
$ python3 $EST/exportar.py xlsx --proyecto gestion --salida gestion/exportados/2027-01-15-registros.xlsx
Escrito gestion/exportados/2027-01-15-registros.xlsx
```

## Paso 13 · Compromiso sostenido: cadencia de contacto (STK-12), acción correctiva y reevaluación del compromiso
```
$ python3 $IN --proyecto gestion integridad --corte 2027-02-05
AVISO STK-12: ST-006 Área de TI del núcleo operativo (gestionar-de-cerca, frecuencia semanal): último contacto registrado el 2027-01-18, hace 18 días (máximo 10)
AVISO STK-12: ST-009 Martín Suárez (gestionar-de-cerca, frecuencia semanal): sin contacto registrado desde 2027-01-15 (21 días; máximo 10)
AVISO STK-12: ST-010 Lucía Benítez (mantener-informado, frecuencia diaria): sin contacto registrado desde 2027-01-15 (21 días; máximo 2)
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-05
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 3 AVISO · 1 INFO
  AVISO STK-12 ST-006 Área de TI del núcleo operativo (gestionar-de-cerca, frecuencia semanal): último contacto registrado el 2027-01-18, hace 18 días (máximo 10)
  AVISO STK-12 ST-009 Martín Suárez (gestionar-de-cerca, frecuencia semanal): sin contacto registrado desde 2027-01-15 (21 días; máximo 10)
  AVISO STK-12 ST-010 Lucía Benítez (mantener-informado, frecuencia diaria): sin contacto registrado desde 2027-01-15 (21 días; máximo 2)
        → Contactarlo según su perfil (envios.py o registrar la reunión o llamada: registro.py agregar envios --campo canal=reunion --campo modo=manual --campo estado=enviado …) o revisar la frecuencia acordada.
  INFO  TOL-02 El EVM del 2027-01-08 está en ámbar (costo=ambar, cronograma=ambar): 50–100 % de la tolerancia.
        → Anticipar acciones correctivas y reportarlo en el highlight.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar envios --campo "fecha=2027-02-05" --campo "stakeholder_id=ST-006" --campo "canal=reunion" --campo "modo=manual" --campo "estado=enviado" --campo "proposito=otro" --campo "asunto=Reunión técnica: integración con el núcleo (NFR-6) y prueba de carga (NFR-3)" --campo "referencia=acta 2027-02-05 reunión técnica" --campo "confirmado_por=Jefa de equipo: Lucía Benítez" --campo "notas=retroalimentación: TI se enteró por terceros del cambio en la consulta al padrón; sin la reunión semanal no pudo planificar el ambiente de carga. Pide retomar la reunión semanal con acta el mismo día."
EN-008
```

```
$ python3 $EST/registro.py --proyecto gestion agregar acciones --campo "fecha=2027-02-05" --campo "origen=ST-006" --campo "descripcion=Reunión técnica semanal con TI y acta enviada el mismo día; aviso previo de cambios que toquen el padrón" --campo "responsable=Lucía Benítez" --campo "fecha_compromiso=2027-02-12" --campo "prioridad=alta"
A-005
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-010 --campo "canal=checkpoint" --campo "frecuencia=semanal" --campo "notas=2027-02-05: la daily es ceremonia del equipo; el compromiso de contacto es el checkpoint semanal"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar envios --campo "fecha=2027-02-05" --campo "stakeholder_id=ST-009" --campo "canal=reunion" --campo "modo=manual" --campo "estado=enviado" --campo "proposito=informe" --campo "asunto=Checkpoint semanal del 2027-02-05 (Lucía Benítez → Martín Suárez)" --campo "referencia=checkpoint-report 2027-02-05" --campo "confirmado_por=Gestor: Martín Suárez"
EN-009
```

```
$ python3 $EST/registro.py --proyecto gestion agregar envios --campo "fecha=2027-02-05" --campo "stakeholder_id=ST-010" --campo "canal=reunion" --campo "modo=manual" --campo "estado=enviado" --campo "proposito=informe" --campo "asunto=Checkpoint semanal del 2027-02-05 (Lucía Benítez → Martín Suárez)" --campo "referencia=checkpoint-report 2027-02-05" --campo "confirmado_por=Gestor: Martín Suárez"
EN-010
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-006 --campo "nivel_compromiso_actual=resistente" --campo "notas=2027-02-05: molestia por falta de contacto (STK-12, 18 días sin reunión); ver A-005"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar stakeholders ST-004 --campo "notas=2027-02-05: sin objeciones al comunicado del 15/1 (métricas de equipo, D-006); se mantiene neutral = deseado"
ok
```

```
$ (matriz de evaluación del compromiso al 2027-02-05, leída de stakeholders.csv: A = actual, D = deseado)
| Interesado | desconocedor | resistente | neutral | partidario | lider | Brecha |
|---|---|---|---|---|---|---|
| ST-001 Laura Méndez |  |  |  |  | A=D | — |
| ST-002 Consejo directivo |  |  |  | A | D | +1 |
| ST-003 Sofía Ramírez |  |  |  |  | A=D | — |
| ST-004 Sindicato de operadores |  |  | A=D |  |  | — |
| ST-005 Socios usuarios piloto |  |  |  | A=D |  | — |
| ST-006 Área de TI del núcleo operativo |  | A |  | D |  | +2 |
| ST-007 Unidad de cumplimiento |  |  | A | D |  | +1 |
| ST-008 Diego Ferreira |  |  |  | A=D |  | — |
| ST-009 Martín Suárez |  |  |  |  | A=D | — |
| ST-010 Lucía Benítez |  |  |  | A=D |  | — |
```

```
$ python3 $IN --proyecto gestion integridad --corte 2027-02-05
Integridad referencial y calidad del maestro: sin hallazgos.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-05
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 1 INFO
  INFO  TOL-02 El EVM del 2027-01-08 está en ámbar (costo=ambar, cronograma=ambar): 50–100 % de la tolerancia.
        → Anticipar acciones correctivas y reportarlo en el highlight.
```

```
$ python3 $IN --proyecto gestion vinculos ST-006
ST-006 Área de TI del núcleo operativo · Proveedor interno · gestionar-de-cerca · estereotipo —
   RACI C en E-1 (epica) Acceso seguro y consulta de mis productos
   EN-007 2027-01-18 reunion «Avance del portal al 8 de enero» [enviado]
   EN-008 2027-02-05 reunion «Reunión técnica: integración con el núcleo (NFR-6) y prueba de carga (NFR-3)» [enviado]
```

