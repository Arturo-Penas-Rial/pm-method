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

## Paso 3 · Enfoque de gestión de riesgos y escala P×I (propuesta → aprobación de la ejecutiva)
```
$ python3 $EST/estado.py --proyecto gestion umbrales-riesgo alto=15 medio=6
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto evaluacion-probabilidad-impacto --ruta 02-planificacion/enfoques/evaluacion-probabilidad-impacto.md --estado en-revision --version 0.1
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar evaluacion-probabilidad-impacto --por "Ejecutiva: Laura Méndez" --version 1.0 --fecha 2026-10-28
Copia congelada / frozen copy: 00-direccion/historial/evaluacion-probabilidad-impacto-v1.0.md
ok
```

```
$ (pm-enfoques-gestion redacta el enfoque con templates/enfoque-riesgo.md, versión mínima → gestion/02-planificacion/enfoques/enfoque-riesgo.md)
# Enfoque de gestión de riesgos — Portal de autoservicio para socios

**Versión mínima:** sí (una página; escalas y matriz en evaluacion-probabilidad-impacto.md).

## 1. Alcance
Proyecto completo; los riesgos del proveedor (Diego Ferreira) entran al mismo registro (riesgos.csv).

## 2. Procedimiento
Identificar: candidatos citados de BMAD, transcripciones, Jira y artefactos (riesgos.py candidatos) y taller al inicio de cada etapa.
Evaluar: P×I 1–5 y EMV en riesgos.csv. Planificar: respuesta del catálogo, aceptada por su propietario y justificada
por costo de la respuesta < reducción de EMV (si no, justificación no económica explícita). Implementar: acciones en
acciones.csv y en el plan de etapa. Comunicar: sección de riesgos del highlight e informe de riesgos a la junta.

## 3-4. Escalas y matriz
Las de evaluacion-probabilidad-impacto.md v1.0: alto >= 15, medio 6-12, bajo <= 5; P1…P5 = 10/30/50/70/90 %.

## 6. Apetito y tolerancia
Apetito: bajo en cumplimiento (Ley 18.331) y seguridad del acceso; moderado en plazo y costo a cambio de adopción
temprana; abierto a oportunidades de reutilización.
Tolerancia del proyecto: ningún riesgo alto sin respuesta y propietario; exposición de amenazas (suma de EMV)
<= USD 60.000 (estado.json, tolerancias.proyecto.riesgo). Un riesgo que queda sobre la línea (>= 15) o que por sí solo
amenaza la tolerancia de tiempo o costo se escala a la junta, con su hoja de riesgo.

## 7. Presupuesto de riesgo y autoridad sobre la reserva
Presupuesto de riesgo = suma del costo de las respuestas + EMV residual de las amenazas + provisión para riesgos no
identificados (5 % del costo de la WBS). Lo fija la ejecutiva (estado.py presupuesto riesgo=<monto>).
El gestor compromete hasta USD 5.000 por respuesta ya aceptada; por encima, o para un riesgo nuevo, decide la ejecutiva.
Cada uso se registra en cambios.csv con cargo=reserva-riesgo y cita el R-### al que responde; lo que no responde a un
riesgo va al presupuesto de cambio o a la junta. La reserva de gestión la libera solo la junta.

## 8. Roles
Ejecutiva: aprueba este enfoque, fija y libera la reserva. Propietarios: aceptan la respuesta de su riesgo.
Ejecutores: acciones con fecha. Aseguramiento (Andrea Costa): revisa el registro en cada fin de etapa.

## 9. Cadencia
Revisión del registro en cada sprint (14 días); reevaluación completa y auditoría en cada fin de etapa; vigilancia
normativa mensual con cumplimiento.

## 10. Reportes
Highlight: altos, nuevos, ocurridos y consumo de la reserva (sanidad CAM-03). Informe de riesgos a pedido de la junta.
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-riesgo --ruta 02-planificacion/enfoques/enfoque-riesgo.md --estado en-revision --version 0.1
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-riesgo --por "Ejecutiva: Laura Méndez" --version 1.0 --fecha 2026-10-28
Copia congelada / frozen copy: 00-direccion/historial/enfoque-riesgo-v1.0.md
ok
```

## Paso 4 · Identificación desde varias fuentes (BMAD, entrevistas y reuniones, artefactos) y taller de riesgos
```
$ (transcripción de ejemplo: copiala a gestion/03-control/reuniones/2026-10-27-ronda-riesgos-original.vtt)
WEBVTT

00:00:01.000 --> 00:00:12.000
<v Martín Suárez>Hagamos la ronda de riesgos del portal antes del taller.

00:00:13.000 --> 00:00:30.000
<v Área de TI del núcleo operativo>Nos preocupa que el padrón no tenga entorno de pruebas; dependemos de otra área para habilitarlo.

00:00:31.000 --> 00:00:45.000
<v Sindicato de operadores>Los operadores temen perder tareas con la bandeja única.

00:00:46.000 --> 00:00:58.000
<v Lucía Benítez>Si no llega el contrato del proveedor de SMS, el segundo factor se atrasa. Además rotan desarrolladores entre clientes y eso nos puede atrasar.

00:00:59.000 --> 00:01:10.000
<v Unidad de cumplimiento>No está claro cómo interpreta la Ley 18.331 las constancias.

00:01:11.000 --> 00:01:20.000
<v Sofía Ramírez>Podríamos aprovechar el generador de PDF del sistema de cartera para las constancias.
```

```
$ python3 $PLUGIN/skills/pm-reuniones/scripts/transcripcion.py gestion/03-control/reuniones/2026-10-27-ronda-riesgos-original.vtt --salida gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md
6 intervenciones de 6 hablantes → gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md
```

```
$ python3 $PLUGIN/skills/pm-riesgos/scripts/riesgos.py --proyecto gestion candidatos --fecha 2026-10-28
bmad: 42 candidatos · 3 fuente(s) leída(s)
transcripciones: 6 candidatos · 1 fuente(s) leída(s)
tracker: 0 candidatos · no disponible
artefactos: 0 candidatos · 2 fuente(s) leída(s)
CR-01 [supuesto/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:26 · `[SUPUESTO]` No se dispone de métricas actuales (volumen de consultas, tiempos, costo por gestión). Medirlas es una tarea previa.
CR-02 [supuesto/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:47 · **Integración con el núcleo operativo de la cooperativa**, con datos al día y no copias desfasadas. `[SUPUESTO]` Existe un sistema central c
CR-03 [supuesto/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:60 · `[SUPUESTO]` Metas orientativas, a calibrar con la línea base:
CR-04 [riesgo/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:89 · **Seguridad y privacidad:** el portal maneja datos financieros y personales. Aplica la Ley 18.331 de protección de datos personales de Urugu
CR-05 [riesgo/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:90 · **Autenticación de identidad:** no está definido el método (cédula con validación, factor adicional, identidad digital nacional). Es la deci
CR-06 [riesgo/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:91 · **Integración con el sistema central:** su calidad y capacidad condicionan plazos y alcance.
CR-07 [riesgo/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:92 · **Brecha digital:** parte de los socios, sobre todo los de mayor edad, no adoptará el portal. Los canales presenciales deben mantenerse.
CR-08 [riesgo/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:93 · **Reglas de préstamos simples:** montos, plazos, requisitos y quién aprueba deben ser definidos por la cooperativa.
CR-09 [riesgo/amenaza] _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md:94 · **Pendiente:** presupuesto, plazo y equipo disponibles; línea base de volumen de gestiones.
CR-10 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:13 · Este PRD define los requisitos de la primera versión del portal de autoservicio de una cooperativa de ahorro y crédito uruguaya (unos 40.000
CR-11 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:64 · **Núcleo operativo** — sistema central de la cooperativa, fuente de verdad de saldos y préstamos. `[SUPUESTO]` Ofrece una API o base de lect
CR-12 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:76 · **Descripción:** el socio se registra y accede con verificación de identidad y puede recuperar el acceso. Realiza UJ-1, UJ-2. `[SUPUESTO]` E · refs UJ-1, UJ-2
CR-13 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:124 · `[SUPUESTO]` Las constancias no requieren firma ni aprobación de un operador.
CR-14 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:128 · **Descripción:** el socio solicita un préstamo simple mediante un formulario guiado con montos y plazos acotados, y sigue su estado. La deci · refs UJ-2, UJ-3
CR-15 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:158 · `[SUPUESTO]` El cambio de domicilio requiere aprobación de un operador; teléfono y correo se aplican tras la verificación, sin aprobación.
CR-16 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:187 · Aprobar préstamos está limitado a operadores habilitados. `[SUPUESTO]` Una sola persona aprueba; la cooperativa puede exigir doble aprobació
CR-17 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:193 · El sistema notifica al socio por correo los eventos de sus solicitudes y los eventos de seguridad. `[SUPUESTO]` El SMS se incorpora solo si 
CR-18 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:201 · **NFR-1 Seguridad y privacidad:** cumplimiento de la Ley 18.331 de protección de datos personales de Uruguay; cifrado en tránsito y en repos · refs NFR-1
CR-19 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:203 · **NFR-3 Rendimiento:** las consultas de saldos y préstamos responden en menos de 3 segundos en el percentil 95 con conexión móvil estándar.  · refs NFR-3
CR-20 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:204 · **NFR-4 Usabilidad y accesibilidad:** uso fluido en celular y navegadores comunes; interfaz clara para socios con poca comodidad digital; ob · refs NFR-4
CR-21 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:231 · Metas orientativas `[SUPUESTO]`, a calibrar cuando exista línea base.
CR-22 [pregunta/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:249 · ¿Qué método de autenticación y verificación de identidad se usa? Es la decisión de mayor impacto en seguridad y adopción (bloquea arquitectu
CR-23 [pregunta/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:250 · ¿Qué interfaz ofrece el núcleo operativo, y con qué capacidad y latencia?
CR-24 [pregunta/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:251 · ¿Qué productos de préstamo simple se habilitan, con qué montos, plazos y requisitos, y quién aprueba?
CR-25 [pregunta/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:252 · ¿Qué exige la normativa del Banco Central del Uruguay para cooperativas de intermediación financiera? Responsable sugerido: cumplimiento.
CR-26 [pregunta/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:253 · ¿Presupuesto, plazo y equipo disponibles? ¿Cuál es la línea base de volumen de gestiones?
CR-27 [pregunta/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:254 · ¿Política de retención del registro de auditoría?
CR-28 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:258 · §0, §3 Núcleo operativo: existe una API o base de lectura utilizable.
CR-29 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:259 · §4.1 Autenticación con segundo factor; método exacto por definir.
CR-30 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:260 · §4.4 Productos, límites y requisitos de préstamo los define la cooperativa.
CR-31 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:261 · FR-5: las constancias no requieren aprobación de un operador. · refs FR-5
CR-32 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:262 · FR-8: domicilio con aprobación del operador; teléfono y correo tras verificación. · refs FR-8
CR-33 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:263 · FR-11: aprobación de préstamo por una sola persona. · refs FR-11
CR-34 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:264 · FR-12: SMS condicionado al costo. · refs FR-12
CR-35 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:265 · NFR-1, NFR-3, NFR-4: normativa BCU aplicable, latencia p95 y WCAG 2.1 AA. · refs NFR-1, NFR-3, NFR-4
CR-36 [supuesto/amenaza] _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:266 · §8: todas las metas son orientativas, sin línea base.
CR-37 [riesgo/amenaza] _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:173 · Proveedor y método de identidad (pregunta abierta 1): se decide con `IdentityPort` ya definido; no afecta el resto de la arquitectura.
CR-38 [riesgo/amenaza] _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:174 · Interfaz y capacidad reales del núcleo operativo (pregunta 2): el adaptador se escribe cuando se conozca; el puerto no cambia.
CR-39 [riesgo/amenaza] _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:175 · Productos y límites de préstamo, y doble aprobación (pregunta 3): son configuración del módulo `solicitudes`.
CR-40 [riesgo/amenaza] _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:176 · Normativa BCU, retención de auditoría y residencia de datos (preguntas 4 y 6): condicionan hosting y retención; la decisión es de cumplimien
CR-41 [riesgo/amenaza] _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:177 · Hosting, proveedor de correo/SMS y almacenamiento de adjuntos: dependen de presupuesto y residencia de datos.
CR-42 [riesgo/amenaza] _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:178 · Observabilidad, CI/CD y estrategia de pruebas: se definen al armar el repositorio.
CR-43 [riesgo/amenaza] gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md [00:00:13] · Área de TI del núcleo operativo: «Nos preocupa que el padrón no tenga entorno de pruebas; dependemos de otra área para habilitarlo.» · ST-003
CR-44 [riesgo/amenaza] gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md [00:00:31] · Sindicato de operadores: «Los operadores temen perder tareas con la bandeja única.» · ST-002
CR-45 [riesgo/amenaza] gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md [00:00:46] · Lucía Benítez: «Si no llega el contrato del proveedor de SMS, el segundo factor se atrasa.»
CR-46 [riesgo/amenaza] gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md [00:00:46] · Lucía Benítez: «Además rotan desarrolladores entre clientes y eso nos puede atrasar.»
CR-47 [riesgo/amenaza] gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md [00:00:59] · Unidad de cumplimiento: «No está claro cómo interpreta la Ley 18.331 las constancias.» · ST-004
CR-48 [riesgo/oportunidad] gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md [00:01:11] · Sofía Ramírez: «Podríamos aprovechar el generador de PDF del sistema de cartera para las constancias.»
→ gestion/03-control/reportes/2026-10-28-candidatos-riesgo.md (borrador). Son candidatos: pm-riesgos los formula, evalúa con el propietario y registra; lo ocurrido va a issues.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=externo" --campo "causa=El padrón del núcleo operativo no tiene entorno de pruebas (AD-1)" --campo "evento=La integración de consulta se prueba tarde" --campo "efecto=Atraso del Release 1 y defectos en FR-3/FR-4" --campo "tipo=amenaza" --campo "probabilidad=4" --campo "impacto=4" --campo "impacto_monetario=30000" --campo "proximidad=corto-plazo" --campo "propietario=Diego Ferreira" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 3.2 · producto Portal del socio · interesado ST-003 · origen: brief.md:91 (BMAD) y ronda 2026-10-27 [00:00:13]"
R-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=organizacional" --campo "causa=Los operadores temen perder tareas con la bandeja única (FR-9)" --campo "evento=Resistencia a usar la consola" --campo "efecto=Adopción baja de la consola y doble trabajo" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=4" --campo "impacto_monetario=15000" --campo "proximidad=mediano-plazo" --campo "propietario=Sofía Ramírez" --campo "ejecutor=Martín Suárez" --campo "notas=WBS 4.1 y 5.1 · producto Consola de operador · interesado ST-002 · origen: ronda 2026-10-27 [00:00:31]"
R-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=tecnico" --campo "causa=El segundo factor depende de un proveedor de SMS nuevo (AD-5)" --campo "evento=El proveedor de SMS no cumple la disponibilidad" --campo "efecto=Socios sin poder ingresar (FR-1, NFR-2)" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=5" --campo "impacto_monetario=25000" --campo "proximidad=mediano-plazo" --campo "propietario=Diego Ferreira" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 3.1 · producto Portal del socio · origen: prd.md:249 y ARCHITECTURE-SPINE.md:177 (BMAD) y ronda 2026-10-27 [00:00:46]"
R-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=externo" --campo "causa=La interpretación de la Ley 18.331 sobre constancias no está cerrada (NFR-1)" --campo "evento=Cumplimiento exige cambios en FR-5" --campo "efecto=Retrabajo de constancias y atraso" --campo "tipo=amenaza" --campo "probabilidad=2" --campo "impacto=4" --campo "impacto_monetario=12000" --campo "proximidad=mediano-plazo" --campo "propietario=Laura Méndez" --campo "ejecutor=Andrea Costa" --campo "notas=WBS 3.2 · interesado ST-004 · origen: brief.md:89 (BMAD) y ronda 2026-10-27 [00:00:59]"
R-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=gestion" --campo "causa=El proveedor rota desarrolladores entre clientes" --campo "evento=Pérdida de conocimiento en el equipo" --campo "efecto=Baja de velocidad" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=3" --campo "impacto_monetario=18000" --campo "proximidad=largo-plazo" --campo "propietario=Diego Ferreira" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 1.1 · origen: ronda 2026-10-27 [00:00:46]"
R-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "estado=abierto" --campo "categoria=comercial" --campo "causa=El generador de PDF del sistema de cartera ya existe" --campo "evento=Reutilizarlo para constancias (FR-5)" --campo "efecto=Ahorro de esfuerzo en WBS 3.2" --campo "tipo=oportunidad" --campo "probabilidad=3" --campo "impacto=3" --campo "impacto_monetario=8000" --campo "proximidad=corto-plazo" --campo "propietario=Sofía Ramírez" --campo "ejecutor=Lucía Benítez" --campo "notas=WBS 3.2 · producto Portal del socio · origen: ronda 2026-10-27 [00:01:11]"
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
    "total": 2
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
id=R-001 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=externo | causa=El padrón del núcleo operativo no tiene entorno de pruebas (AD-1) | evento=La integración de consulta se prueba tarde | efecto=Atraso del Release 1 y defectos en FR-3/FR-4 | tipo=amenaza | probabilidad=4 | impacto=4 | puntuacion=16 | impacto_monetario=30000 | valor_esperado=21000 | proximidad=corto-plazo | propietario=Diego Ferreira | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 3.2 · producto Portal del socio · interesado ST-003 · origen: brief.md:91 (BMAD) y ronda 2026-10-27 [00:00:13]
id=R-002 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=organizacional | causa=Los operadores temen perder tareas con la bandeja única (FR-9) | evento=Resistencia a usar la consola | efecto=Adopción baja de la consola y doble trabajo | tipo=amenaza | probabilidad=3 | impacto=4 | puntuacion=12 | impacto_monetario=15000 | valor_esperado=7500 | proximidad=mediano-plazo | propietario=Sofía Ramírez | ejecutor=Martín Suárez | estado=abierto | notas=WBS 4.1 y 5.1 · producto Consola de operador · interesado ST-002 · origen: ronda 2026-10-27 [00:00:31]
id=R-003 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=tecnico | causa=El segundo factor depende de un proveedor de SMS nuevo (AD-5) | evento=El proveedor de SMS no cumple la disponibilidad | efecto=Socios sin poder ingresar (FR-1, NFR-2) | tipo=amenaza | probabilidad=3 | impacto=5 | puntuacion=15 | impacto_monetario=25000 | valor_esperado=12500 | proximidad=mediano-plazo | propietario=Diego Ferreira | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 3.1 · producto Portal del socio · origen: prd.md:249 y ARCHITECTURE-SPINE.md:177 (BMAD) y ronda 2026-10-27 [00:00:46]
id=R-004 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=externo | causa=La interpretación de la Ley 18.331 sobre constancias no está cerrada (NFR-1) | evento=Cumplimiento exige cambios en FR-5 | efecto=Retrabajo de constancias y atraso | tipo=amenaza | probabilidad=2 | impacto=4 | puntuacion=8 | impacto_monetario=12000 | valor_esperado=3600 | proximidad=mediano-plazo | propietario=Laura Méndez | ejecutor=Andrea Costa | estado=abierto | notas=WBS 3.2 · interesado ST-004 · origen: brief.md:89 (BMAD) y ronda 2026-10-27 [00:00:59]
id=R-005 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=gestion | causa=El proveedor rota desarrolladores entre clientes | evento=Pérdida de conocimiento en el equipo | efecto=Baja de velocidad | tipo=amenaza | probabilidad=3 | impacto=3 | puntuacion=9 | impacto_monetario=18000 | valor_esperado=9000 | proximidad=largo-plazo | propietario=Diego Ferreira | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 1.1 · origen: ronda 2026-10-27 [00:00:46]
id=R-006 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=comercial | causa=El generador de PDF del sistema de cartera ya existe | evento=Reutilizarlo para constancias (FR-5) | efecto=Ahorro de esfuerzo en WBS 3.2 | tipo=oportunidad | probabilidad=3 | impacto=3 | puntuacion=9 | impacto_monetario=8000 | valor_esperado=4000 | proximidad=corto-plazo | propietario=Sofía Ramírez | ejecutor=Lucía Benítez | estado=abierto | notas=WBS 3.2 · producto Portal del socio · origen: ronda 2026-10-27 [00:01:11]
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-03
Sanidad de 'Portal de autoservicio para socios' (pre-proyecto/SU): 0 ERROR · 2 AVISO · 0 INFO
  AVISO REG-06 Riesgo alto R-001 sin respuesta o propietario.
  AVISO REG-06 Riesgo alto R-003 sin respuesta o propietario.
        → pm-riesgos.
```

## Paso 6 · Respuestas con costo justificado por EMV, residual, secundarios, disparadores y acciones
```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-001 --campo "respuesta=reducir" --campo "acciones=spike de integración con datos sintéticos en el sprint 1; pedir entorno de pruebas a TI · costo USD 2.000 · ΔEMV USD 12.000" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "disparador=spike sin datos del padrón al día 5" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-002 --campo "respuesta=reducir" --campo "acciones=taller con operadores y piloto de la bandeja en una sucursal · costo USD 1.500 · ΔEMV USD 3.000" --campo "probabilidad_residual=2" --campo "impacto_residual=3" --campo "disparador=menos del 50 % de operadores usa la consola en el piloto" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-003 --campo "respuesta=transferir" --campo "acciones=SLA de 99,9 % con penalidad en el contrato del proveedor de SMS; correo como factor alternativo · costo USD 2.500 · ΔEMV USD 5.000" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "disparador=dos caídas del proveedor en un mes" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-004 --campo "respuesta=aceptar" --campo "acciones=seguimiento mensual con cumplimiento; contingencia de 1 semana · costo USD 0 · ΔEMV USD 0" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "disparador=dictamen de cumplimiento" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-005 --campo "respuesta=reducir" --campo "acciones=cláusula de permanencia del equipo clave y documentación de decisiones · costo USD 3.000 · ΔEMV USD 3.600" --campo "probabilidad_residual=2" --campo "impacto_residual=3" --campo "disparador=salida de un desarrollador clave" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-006 --campo "respuesta=explotar" --campo "acciones=spike de reutilización del generador de PDF en el sprint 2 · costo USD 800 · ΔEMV USD 1.600" --campo "probabilidad_residual=4" --campo "impacto_residual=3" --campo "disparador=" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-11-04" --campo "autor=Martín Suárez" --campo "categoria=comercial" --campo "causa=La respuesta de R-003 transfiere el riesgo con una penalidad con tope de USD 2.000 por mes" --campo "evento=El proveedor de SMS falla y la penalidad cobrada no cubre el costo del atraso" --campo "efecto=Costo del atraso no recuperado (WBS 3.1)" --campo "tipo=amenaza" --campo "probabilidad=2" --campo "impacto=3" --campo "impacto_monetario=6000" --campo "proximidad=mediano-plazo" --campo "respuesta=aceptar" --campo "acciones=aceptar: el correo como factor alternativo (respuesta de R-003) limita el atraso · costo USD 0" --campo "probabilidad_residual=2" --campo "impacto_residual=3" --campo "disparador=primera caída con penalidad menor que el costo del atraso" --campo "propietario=Diego Ferreira" --campo "ejecutor=Lucía Benítez" --campo "estado=en-seguimiento" --campo "fecha_revision=2026-11-17" --campo "notas=WBS 3.1 · riesgo secundario de R-003 (respuesta transferir)"
R-007
```

```
$ (pm-riesgos: justificación económica de cada respuesta, desde riesgos.csv; EMV = impacto_monetario × probabilidad convertida)
id     respuesta   EMV antes  EMV residual  costo respuesta  ΔEMV    ¿costo < ΔEMV?
R-001  reducir        21.000         9.000            2.000  12.000  sí
R-002  reducir         7.500         4.500            1.500   3.000  sí
R-003  transferir     12.500         7.500            2.500   5.000  sí
R-004  aceptar         3.600         3.600                0       0  n/a (aceptar)
R-005  reducir         9.000         5.400            3.000   3.600  sí
R-006  explotar        4.000         5.600              800   1.600  sí
R-007  aceptar         1.800         1.800                0       0  n/a (aceptar)
Total costo de respuestas: USD 9.800 · EMV residual de amenazas: USD 31.800
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
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-04" --campo "decision=La persona propietaria acepta la respuesta, su costo y el residual de R-001, R-003, R-005, R-007" --campo "decidido_por=Proveedor sénior: Diego Ferreira" --campo "nivel=gestor"
D-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-04" --campo "decision=La persona propietaria acepta la respuesta, su costo y el residual de R-002, R-006" --campo "decidido_por=Usuaria sénior: Sofía Ramírez" --campo "nivel=gestor"
D-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-11-04" --campo "decision=La persona propietaria acepta la respuesta, su costo y el residual de R-004" --campo "decidido_por=Ejecutiva: Laura Méndez" --campo "nivel=ejecutivo"
D-005
```

```
$ python3 $EST/registro.py --proyecto gestion listar riesgos --abiertos
id=R-001 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=externo | causa=El padrón del núcleo operativo no tiene entorno de pruebas (AD-1) | evento=La integración de consulta se prueba tarde | efecto=Atraso del Release 1 y defectos en FR-3/FR-4 | tipo=amenaza | probabilidad=4 | impacto=4 | puntuacion=16 | impacto_monetario=30000 | valor_esperado=21000 | proximidad=corto-plazo | disparador=spike sin datos del padrón al día 5 | respuesta=reducir | acciones=spike de integración con datos sintéticos en el sprint 1; pedir entorno de pruebas a TI · costo USD 2.000 · ΔEMV USD 12.000 | propietario=Diego Ferreira | ejecutor=Lucía Benítez | probabilidad_residual=2 | impacto_residual=4 | estado=en-seguimiento | fecha_revision=2026-11-17 | notas=WBS 3.2 · producto Portal del socio · interesado ST-003 · origen: brief.md:91 (BMAD) y ronda 2026-10-27 [00:00:13]
id=R-002 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=organizacional | causa=Los operadores temen perder tareas con la bandeja única (FR-9) | evento=Resistencia a usar la consola | efecto=Adopción baja de la consola y doble trabajo | tipo=amenaza | probabilidad=3 | impacto=4 | puntuacion=12 | impacto_monetario=15000 | valor_esperado=7500 | proximidad=mediano-plazo | disparador=menos del 50 % de operadores usa la consola en el piloto | respuesta=reducir | acciones=taller con operadores y piloto de la bandeja en una sucursal · costo USD 1.500 · ΔEMV USD 3.000 | propietario=Sofía Ramírez | ejecutor=Martín Suárez | probabilidad_residual=2 | impacto_residual=3 | estado=en-seguimiento | fecha_revision=2026-11-17 | notas=WBS 4.1 y 5.1 · producto Consola de operador · interesado ST-002 · origen: ronda 2026-10-27 [00:00:31]
id=R-003 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=tecnico | causa=El segundo factor depende de un proveedor de SMS nuevo (AD-5) | evento=El proveedor de SMS no cumple la disponibilidad | efecto=Socios sin poder ingresar (FR-1, NFR-2) | tipo=amenaza | probabilidad=3 | impacto=5 | puntuacion=15 | impacto_monetario=25000 | valor_esperado=12500 | proximidad=mediano-plazo | disparador=dos caídas del proveedor en un mes | respuesta=transferir | acciones=SLA de 99,9 % con penalidad en el contrato del proveedor de SMS; correo como factor alternativo · costo USD 2.500 · ΔEMV USD 5.000 | propietario=Diego Ferreira | ejecutor=Lucía Benítez | probabilidad_residual=2 | impacto_residual=4 | estado=en-seguimiento | fecha_revision=2026-11-17 | notas=WBS 3.1 · producto Portal del socio · origen: prd.md:249 y ARCHITECTURE-SPINE.md:177 (BMAD) y ronda 2026-10-27 [00:00:46]
id=R-004 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=externo | causa=La interpretación de la Ley 18.331 sobre constancias no está cerrada (NFR-1) | evento=Cumplimiento exige cambios en FR-5 | efecto=Retrabajo de constancias y atraso | tipo=amenaza | probabilidad=2 | impacto=4 | puntuacion=8 | impacto_monetario=12000 | valor_esperado=3600 | proximidad=mediano-plazo | disparador=dictamen de cumplimiento | respuesta=aceptar | acciones=seguimiento mensual con cumplimiento; contingencia de 1 semana · costo USD 0 · ΔEMV USD 0 | propietario=Laura Méndez | ejecutor=Andrea Costa | probabilidad_residual=2 | impacto_residual=4 | estado=en-seguimiento | fecha_revision=2026-11-17 | notas=WBS 3.2 · interesado ST-004 · origen: brief.md:89 (BMAD) y ronda 2026-10-27 [00:00:59]
id=R-005 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=gestion | causa=El proveedor rota desarrolladores entre clientes | evento=Pérdida de conocimiento en el equipo | efecto=Baja de velocidad | tipo=amenaza | probabilidad=3 | impacto=3 | puntuacion=9 | impacto_monetario=18000 | valor_esperado=9000 | proximidad=largo-plazo | disparador=salida de un desarrollador clave | respuesta=reducir | acciones=cláusula de permanencia del equipo clave y documentación de decisiones · costo USD 3.000 · ΔEMV USD 3.600 | propietario=Diego Ferreira | ejecutor=Lucía Benítez | probabilidad_residual=2 | impacto_residual=3 | estado=en-seguimiento | fecha_revision=2026-11-17 | notas=WBS 1.1 · origen: ronda 2026-10-27 [00:00:46]
id=R-006 | fecha_identificacion=2026-10-29 | autor=Martín Suárez | categoria=comercial | causa=El generador de PDF del sistema de cartera ya existe | evento=Reutilizarlo para constancias (FR-5) | efecto=Ahorro de esfuerzo en WBS 3.2 | tipo=oportunidad | probabilidad=3 | impacto=3 | puntuacion=9 | impacto_monetario=8000 | valor_esperado=4000 | proximidad=corto-plazo | respuesta=explotar | acciones=spike de reutilización del generador de PDF en el sprint 2 · costo USD 800 · ΔEMV USD 1.600 | propietario=Sofía Ramírez | ejecutor=Lucía Benítez | probabilidad_residual=4 | impacto_residual=3 | estado=en-seguimiento | fecha_revision=2026-11-17 | notas=WBS 3.2 · producto Portal del socio · origen: ronda 2026-10-27 [00:01:11]
id=R-007 | fecha_identificacion=2026-11-04 | autor=Martín Suárez | categoria=comercial | causa=La respuesta de R-003 transfiere el riesgo con una penalidad con tope de USD 2.000 por mes | evento=El proveedor de SMS falla y la penalidad cobrada no cubre el costo del atraso | efecto=Costo del atraso no recuperado (WBS 3.1) | tipo=amenaza | probabilidad=2 | impacto=3 | puntuacion=6 | impacto_monetario=6000 | valor_esperado=1800 | proximidad=mediano-plazo | disparador=primera caída con penalidad menor que el costo del atraso | respuesta=aceptar | acciones=aceptar: el correo como factor alternativo (respuesta de R-003) limita el atraso · costo USD 0 | propietario=Diego Ferreira | ejecutor=Lucía Benítez | probabilidad_residual=2 | impacto_residual=3 | estado=en-seguimiento | fecha_revision=2026-11-17 | notas=WBS 3.1 · riesgo secundario de R-003 (respuesta transferir)
```

## Paso 7 · Presupuesto de riesgo (respuestas + EMV residual + no identificados), control de la reserva y puertas
```
$ python3 $EST/registro.py --proyecto gestion resumen --json --corte 2026-11-20
{
  "riesgos": {
    "total": 7,
    "por_estado": {
      "en-seguimiento": 7
    },
    "abiertos": 7,
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
    "total": 5
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
$ (pm-riesgos calcula el presupuesto de riesgo con la fórmula del enfoque §7 → gestion/02-planificacion/presupuesto.md)
# Presupuesto de riesgo (contingencia) · etapa 2 y proyecto

| Componente | USD | Criterio |
|---|---|---|
| Costo de las respuestas planificadas | 9.800 | R-001 2.000 · R-002 1.500 · R-003 2.500 · R-005 3.000 · R-006 800 (cada una < su reducción de EMV) |
| EMV residual de las amenazas | 31.800 | R-001 9.000 · R-002 4.500 · R-003 7.500 · R-004 3.600 · R-005 5.400 · R-007 1.800 |
| Provisión para riesgos no identificados | 6.200 | 5 % del costo de la WBS (124.000), según el enfoque de riesgo §7 |
| **Presupuesto de riesgo** | **47.800** | aparte del costo de los paquetes; lo fija la ejecutiva |

La transferencia de R-003 no descuenta su EMV residual: la penalidad del SLA no cubre el atraso (riesgo secundario R-007).
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto presupuesto --ruta 02-planificacion/presupuesto.md --estado en-revision
ok
```

```
$ python3 $EST/estado.py --proyecto gestion presupuesto riesgo=47800 --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2026-11-27" --campo "solicitante=Martín Suárez" --campo "titulo=Financiar las respuestas planificadas de R-001, R-002, R-003, R-005 y R-006" --campo "descripcion=spike del padrón (R-001) 2.000; taller y piloto (R-002) 1.500; sobreprecio del SLA y correo alternativo (R-003) 2.500; bono de permanencia (R-005) 3.000; spike de reutilización (R-006) 800" --campo "justificacion=cada costo es menor que la reducción de EMV que logra (enfoque de riesgo §7)" --campo "impacto_costo=9.800 de la reserva de riesgo" --campo "decision=aprobado" --campo "decidido_por=Ejecutiva: Laura Méndez" --campo "fecha_decision=2026-11-27" --campo "estado=aprobado" --campo "costo=9800" --campo "cargo=reserva-riesgo"
C-001
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-27
Sanidad de 'Portal de autoservicio para socios' (pre-proyecto/SU): 0 ERROR · 2 AVISO · 1 INFO
  AVISO REG-07 Acción vencida A-002 (Martín Suárez, 2026-11-20).
  AVISO REG-07 Acción vencida A-003 (Diego Ferreira, 2026-11-25).
        → Recordatorio o replanificación.
  INFO  CAM-03 Reserva de riesgo: 9.800 de 47.800 (21 %).
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Portal de autoservicio para socios · pre-proyecto/SU · etapa 0 pre-proyecto (2026-10-17 → ) · enfoque hibrido · idioma es
Autorizado: no
Roles: ejecutivo=Laura Méndez; usuario_senior=Sofía Ramírez; proveedor_senior=Diego Ferreira; gestor_proyecto=Martín Suárez; aseguramiento=Andrea Costa; autoridad_cambio=Sofía Ramírez; product_owner=Sofía Ramírez; jefes_equipo=Lucía Benítez
Tolerancias: proyecto: tiempo=±3 semanas, costo=±8 %, alcance=Must sin tolerancia, beneficios=-10 %, riesgo=ningún riesgo alto sin respuesta; exposición total ≤ USD 60.000 | etapa: 
Presupuestos: riesgo=47800
Artefactos: 3 (2 aprobados)
Próxima puerta: autorizar-inicio · 2 bloqueo(s) · 1 condición(es) (detalle: puertas.py verificar autorizar-inicio)
Fase: pre-proyecto · Proceso: SU · Etapa 0: pre-proyecto · Enfoque: hibrido
Puesta en marcha (SU): mandato → lecciones previas → brief (con caso de negocio esquemático y enfoque del proyecto) → junta y roles → plan de la etapa de iniciación. Ágil/híbrido: brief ligero + visión y backlog inicial de épicas. Agentes: pm-inicio. Puerta: autorizar-inicio (pm-director).
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
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-inicio --fecha 2026-10-30
Lista creada: 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md (0 hallazgos automáticos, 5 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-inicio --por "Ejecutiva: Laura Méndez" --fecha 2026-10-30
Lista 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md confirmada por Ejecutiva: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-inicio --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2026-10-30 --fin 2026-11-27
ok
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director).
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision --version 1.0
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto enfoque-beneficios --ruta 00-direccion/enfoque-beneficios.md --estado en-revision
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
$ python3 $EST/estado.py --proyecto gestion aprobar business-case --por "Ejecutiva: Laura Méndez" --version 1.0 --fecha 2026-11-27
Copia congelada / frozen copy: 00-direccion/historial/business-case-v1.0.md
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 0 condición(es) · 1 aviso(s)
  BLOQUEO   falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  aviso     sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-proyecto --fecha 2026-11-27
Lista creada: 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md (1 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-proyecto --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27
Lista 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md confirmada por Ejecutiva: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-proyecto --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27 
Aviso: sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
ok
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director). Proyecto ya autorizado: falta autorizar-etapa para la primera etapa de entrega.
```

```
$ python3 $BMAD --proyecto gestion linea-base prd --version 1.0 --por "Ejecutiva: Laura Méndez"
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
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-etapa --fecha 2026-11-27
Lista creada: 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md (1 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-etapa --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27
Lista 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md confirmada por Ejecutiva: Laura Méndez
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-etapa --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27 --etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=±10 %" "costo=±10 %"
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
    "total": 7,
    "por_estado": {
      "en-seguimiento": 6,
      "cerrado": 1
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
    "total": 1,
    "por_estado": {
      "aprobado": 1
    },
    "abiertos": 1
  },
  "decisiones": {
    "total": 12
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
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-12-15
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 2 INFO
  AVISO REG-07 Acción vencida A-001 (Lucía Benítez, 2026-12-11).
        → Recordatorio o replanificación.
  INFO  CAM-03 Reserva de riesgo: 9.800 de 47.800 (21 %).
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto tablero-avance --ruta 03-control/reportes/2026-12-15-tablero-avance.html --estado en-revision
ok
```

```
$ (pm-visuales arma el tablero con la receta de references/guia.md §3 → gestion/03-control/reportes/2026-12-15-tablero-avance.html)
riesgos abiertos 6 · issues 0 · acciones 3 · iteraciones 0
```

## Paso 9 · Incidencias emergentes desde Jira: riesgo → issue, defecto fuera de especificación y control del consumo de la reserva de riesgo
```
$ (instantánea de Jira de ejemplo: la deja pm-integraciones en gestion/03-control/fuentes/jira-2026-12-16.csv)
clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url,prioridad,etiquetas,vinculo
PS-101,Bug,La consulta de saldos devuelve timeout con el padrón de prueba,En curso,Lucía Benítez,Sprint 2,,2026-12-16,https://jira.example.org/browse/PS-101,Highest,,1-3-consulta-de-saldos-de-ahorro-y-préstamos
PS-102,Impedimento,Sin entorno de pruebas del padrón: historias 1-3 y 1-4 bloqueadas,Bloqueado,Martín Suárez,Sprint 2,,2026-12-16,https://jira.example.org/browse/PS-102,High,,
PS-103,Historia,Descarga de constancias en PDF,En curso,Lucía Benítez,Sprint 2,5,2026-12-15,https://jira.example.org/browse/PS-103,Medium,,1-4-descarga-de-constancias-en-pdf
PS-104,Tarea,Evaluar un proveedor de SMS alternativo por la disponibilidad del segundo factor,Por hacer,Diego Ferreira,Sprint 3,,2026-12-14,https://jira.example.org/browse/PS-104,Medium,riesgo,
```

```
$ python3 $PLUGIN/skills/pm-riesgos/scripts/riesgos.py --proyecto gestion candidatos --fuentes tracker --fecha 2026-12-16
tracker: 3 candidatos · 1 fuente(s) leída(s)
CR-01 [issue/amenaza] jira:PS-101 (gestion/03-control/fuentes/jira-2026-12-16.csv) · La consulta de saldos devuelve timeout con el padrón de prueba · refs 1-3-consulta-de-saldos-de-ahorro-y-préstamos · ¿relacionado con R-001?
CR-02 [issue/amenaza] jira:PS-102 (gestion/03-control/fuentes/jira-2026-12-16.csv) · Sin entorno de pruebas del padrón: historias 1-3 y 1-4 bloqueadas · ¿relacionado con R-001?
CR-03 [riesgo/amenaza] jira:PS-104 (gestion/03-control/fuentes/jira-2026-12-16.csv) · Evaluar un proveedor de SMS alternativo por la disponibilidad del segundo factor · ¿duplica R-003?
→ gestion/03-control/reportes/2026-12-16-candidatos-riesgo.md (borrador). Son candidatos: pm-riesgos los formula, evalúa con el propietario y registra; lo ocurrido va a issues.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-001 --campo "estado=ocurrido" --campo "fecha_revision=2026-12-16" --campo "notas=WBS 3.2 · el spike A-001 confirmó que TI no da entorno de pruebas hasta febrero · origen: jira:PS-102"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2026-12-16" --campo "tipo=problema-preocupacion" --campo "titulo=Sin entorno de pruebas del padrón hasta febrero (materializa R-001)" --campo "descripcion=Las historias 1-3 y 1-4 no pueden probarse contra el núcleo operativo" --campo "prioridad=alta" --campo "severidad=mayor" --campo "impacto=2 semanas de atraso en WBS 3.2" --campo "responsable=Martín Suárez" --campo "notas=origen: jira:PS-102"
I-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar issues --campo "fecha=2026-12-16" --campo "tipo=fuera-especificacion" --campo "titulo=Timeout en la consulta de saldos con el padrón de prueba (NFR-3)" --campo "descripcion=Defecto de la historia 1-3: la respuesta supera los 3 s del NFR-3" --campo "prioridad=alta" --campo "severidad=mayor" --campo "impacto=la historia 1-3 no cumple NFR-3" --campo "responsable=Lucía Benítez" --campo "notas=origen: jira:PS-101"
I-002
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-003 --campo "notas=WBS 3.1 · producto Portal del socio · origen: prd.md:249 y ARCHITECTURE-SPINE.md:177 (BMAD) y ronda 2026-10-27 [00:00:46] · seguimiento: jira:PS-104 (proveedor alternativo)"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar issues I-002 --campo "estado=resuelto" --campo "fecha_cierre=2026-12-20" --campo "decision=índice en la consulta del adaptador; p95 = 1,8 s" --campo "decidido_por=Jefa de equipo: Lucía Benítez"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar acciones A-001 --campo "estado=completada" --campo "fecha_cierre=2026-12-11"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion listar issues --abiertos
id=I-001 | fecha=2026-12-16 | tipo=problema-preocupacion | titulo=Sin entorno de pruebas del padrón hasta febrero (materializa R-001) | descripcion=Las historias 1-3 y 1-4 no pueden probarse contra el núcleo operativo | prioridad=alta | severidad=mayor | impacto=2 semanas de atraso en WBS 3.2 | responsable=Martín Suárez | estado=abierto | notas=origen: jira:PS-102
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2026-12-17" --campo "solicitante=Martín Suárez" --campo "titulo=Entorno de pruebas temporal del padrón (contingencia de R-001 materializado, I-001)" --campo "descripcion=entorno en la nube con una copia anonimizada del padrón durante 8 semanas, hasta que TI habilite el suyo en febrero" --campo "justificacion=contingencia prevista para R-001 en el tablero del 15/12: baja el atraso de WBS 3.2 de 2 semanas a 3 días" --campo "impacto_tiempo=3 días en lugar de 2 semanas" --campo "impacto_costo=8.000" --campo "impacto_riesgo=responde a R-001 (ocurrido) e I-001" --campo "decision=aprobado" --campo "decidido_por=Ejecutiva: Laura Méndez" --campo "fecha_decision=2026-12-17" --campo "estado=aprobado" --campo "costo=8000" --campo "cargo=reserva-riesgo" --campo "notas=supera los USD 5.000 que el enfoque de riesgo delega en el gestor: decide la ejecutiva"
C-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2026-12-18" --campo "solicitante=Lucía Benítez" --campo "titulo=Licencias adicionales de la herramienta de diseño para el equipo UX" --campo "descripcion=dos licencias anuales porque el equipo de diseño creció" --campo "justificacion=productividad del equipo de diseño" --campo "impacto_costo=3.000" --campo "decision=aprobado" --campo "decidido_por=Gestor: Martín Suárez" --campo "fecha_decision=2026-12-18" --campo "estado=aprobado" --campo "costo=3000" --campo "cargo=reserva-riesgo"
C-003
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-12-18
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 2 INFO
  AVISO CAM-02 Cambio C-003 cargado a la reserva de riesgo sin citar el riesgo R-### que responde.
        → La reserva de riesgo solo financia respuestas a riesgos; si no, presupuesto de cambio o junta.
  INFO  CAM-03 Reserva de riesgo: 20.800 de 47.800 (44 %).
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar cambios C-003 --campo "decision=rechazado" --campo "estado=rechazado" --campo "decidido_por=Autoridad de cambio: Sofía Ramírez" --campo "fecha_decision=2026-12-18" --campo "notas=no responde a ningún riesgo: la reserva de riesgo no es una bolsa general; si hace falta, va como solicitud de cambio contra el presupuesto de cambio cuando la junta lo fije"
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-12-18
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 0 AVISO · 2 INFO
  INFO  CAM-03 Reserva de riesgo: 17.800 de 47.800 (37 %).
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

## Paso 10 · Riesgo nuevo sobre la línea: hoja de riesgo, escalamiento a la junta y revisión del business case
```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2027-01-08" --campo "autor=Martín Suárez" --campo "categoria=externo" --campo "causa=El regulador anunció nueva norma de autenticación para servicios financieros" --campo "evento=La norma exige biometría para operaciones de préstamo (FR-6)" --campo "efecto=Rediseño del acceso y atraso del Release 2" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=5" --campo "impacto_monetario=40000" --campo "proximidad=mediano-plazo" --campo "respuesta=escalar" --campo "propietario=Laura Méndez" --campo "ejecutor=Martín Suárez" --campo "estado=escalado" --campo "notas=WBS 3.1 y 3.3 · interesado ST-004 · afecta el business case: decide la junta"
R-008
```

```
$ (pm-riesgos redacta la hoja de riesgo con templates/hoja-riesgo.md → gestion/03-control/registros/R-008-hoja-riesgo.md)
# Hoja de datos de riesgo · R-008

**Título:** norma de biometría para operaciones de préstamo · **Tipo:** amenaza · **Categoría:** externo · **Estado:** escalado

**Enunciado:** Si el regulador aprueba la nueva norma de autenticación, puede exigirse biometría para préstamos (FR-6),
lo que provocaría rediseñar el acceso (WBS 3.1 y 3.3) y atrasar el Release 2.
**Objetivos afectados:** tiempo (±3 semanas), costo (±8 %), beneficios (B-02 adopción, -10 %), cumplimiento (apetito bajo).

## Evaluación actual
P3 × I5 = 15 (alto, sobre la línea) · impacto monetario USD 40.000 · EMV = 50 % × 40.000 = USD 20.000 · proximidad: mediano plazo.

## Respuesta propuesta
Reducir: análisis normativo con asesoría externa y diseño de autenticación reforzada detrás de IdentityPort (AD-5).
Costo de la respuesta: USD 10.000 (reserva de riesgo; supera la autoridad del gestor: decide la ejecutiva).

## Evaluación residual y justificación
P2 × I4 = 8 · EMV residual = 30 % × 40.000 = USD 12.000 · reducción de EMV = USD 8.000.
Costo (10.000) mayor que la reducción de EMV (8.000): la respuesta **no se justifica solo por EMV**. Justificación no
económica: cumplimiento regulatorio, con apetito bajo según el enfoque de riesgo §6. Por eso decide la junta.
Riesgos secundarios: ninguno identificado. Residual aceptado: P2 × I4, revisión en la próxima junta.

## Alerta temprana y contingencia
Disparador: publicación de la norma en el Diario Oficial. Contingencia: autenticación biométrica para préstamos en el
Release 2 detrás de IdentityPort, con solicitud de cambio.
```

```
$ python3 $EST/registro.py --proyecto gestion resumen --json --corte 2027-01-08
{
  "riesgos": {
    "total": 8,
    "por_estado": {
      "ocurrido": 1,
      "en-seguimiento": 5,
      "cerrado": 1,
      "escalado": 1
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
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-008 (15, alto) La norma exige biometría para operaciones de préstamo (FR-6)",
      "R-005 (9, medio) Pérdida de conocimiento en el equipo",
      "R-002 (8, medio) Resistencia a usar la consola",
      "R-004 (8, medio) Cumplimiento exige cambios en FR-5"
    ]
  },
  "issues": {
    "total": 2,
    "por_estado": {
      "abierto": 1,
      "resuelto": 1
    },
    "abiertos": 1,
    "sin_responsable": []
  },
  "cambios": {
    "total": 3,
    "por_estado": {
      "aprobado": 2,
      "rechazado": 1
    },
    "abiertos": 2
  },
  "decisiones": {
    "total": 12
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
$ python3 $EST/estado.py --proyecto gestion puerta decision-ad-hoc --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2027-01-12 --condiciones "usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar R-008 en la próxima junta"
ok
Fase: entrega · Proceso: CS · Etapa 2: Release 1 · Enfoque: hibrido
Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, iteraciones con review/retro, revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.
Condiciones abiertas: decision-ad-hoc: usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar R-008 en la próxima junta
```

```
$ python3 $EST/registro.py --proyecto gestion agregar cambios --campo "fecha=2027-01-12" --campo "solicitante=Martín Suárez" --campo "titulo=Análisis normativo con asesoría externa (respuesta a R-008)" --campo "descripcion=asesoría externa sobre la norma de autenticación y diseño de autenticación reforzada detrás de IdentityPort (AD-5)" --campo "justificacion=hoja de riesgo de R-008: justificación regulatoria (costo 10.000 mayor que la reducción de EMV 8.000)" --campo "impacto_costo=10.000" --campo "impacto_riesgo=responde a R-008" --campo "decision=aprobado" --campo "decidido_por=Ejecutiva: Laura Méndez" --campo "fecha_decision=2027-01-12" --campo "estado=aprobado" --campo "costo=10000" --campo "cargo=reserva-riesgo" --campo "notas=decision-ad-hoc de la junta del 2027-01-12"
C-004
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar riesgos R-008 --campo "respuesta=reducir" --campo "acciones=análisis normativo con asesoría externa (C-004); diseño de autenticación reforzada detrás de IdentityPort (AD-5) · costo USD 10.000 · ΔEMV USD 8.000" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "estado=en-seguimiento" --campo "notas=WBS 3.1 y 3.3 · interesado ST-004 · hoja: 03-control/registros/R-008-hoja-riesgo.md · decisión de la junta del 2027-01-12"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision --version 1.1
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar business-case --por "Ejecutiva: Laura Méndez" --version 1.1 --fecha 2027-01-12
Copia congelada / frozen copy: 00-direccion/historial/business-case-v1.1.md
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-12
Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 2 INFO
  AVISO EST-12 Condiciones abiertas de decision-ad-hoc: usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar R-008 en la próxima junta.
        → estado.py cumplir-condiciones <tipo> cuando se cumplan.
  INFO  CAM-03 Reserva de riesgo: 27.800 de 47.800 (58 %).
  INFO  TOL-03 Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.
        → evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.
```

## Paso 11 · Informe de riesgos e insumo para el highlight
```
$ python3 $EST/registro.py --proyecto gestion resumen --corte 2027-01-15
{
  "riesgos": {
    "total": 8,
    "por_estado": {
      "ocurrido": 1,
      "en-seguimiento": 6,
      "cerrado": 1
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
      "R-003 (15, alto) El proveedor de SMS no cumple la disponibilidad",
      "R-008 (15, alto) La norma exige biometría para operaciones de préstamo (FR-6)",
      "R-005 (9, medio) Pérdida de conocimiento en el equipo",
      "R-002 (8, medio) Resistencia a usar la consola",
      "R-004 (8, medio) Cumplimiento exige cambios en FR-5"
    ]
  },
  "issues": {
    "total": 2,
    "por_estado": {
      "abierto": 1,
      "resuelto": 1
    },
    "abiertos": 1,
    "sin_responsable": []
  },
  "cambios": {
    "total": 4,
    "por_estado": {
      "aprobado": 3,
      "rechazado": 1
    },
    "abiertos": 3
  },
  "decisiones": {
    "total": 14
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
| autorizar-inicio | 2026-10-30 | aprobado | Ejecutiva: Laura Méndez | — | — | 00-direccion/decisiones/2026-10-30-verificacion-autorizar-inicio.md |
| autorizar-proyecto | 2026-11-27 | aprobado | Ejecutiva: Laura Méndez | — | — | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-proyecto.md |
| autorizar-etapa | 2026-11-27 | aprobado | Ejecutiva: Laura Méndez | — | — | 00-direccion/decisiones/2026-11-27-verificacion-autorizar-etapa.md |
| decision-ad-hoc | 2027-01-12 | aprobado | Ejecutiva: Laura Méndez | usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar R-008 en la próxima junta (abiertas) | — | — |

**Próxima puerta / Next gate: autorizar-etapa** — 2 bloqueo(s), 1 condición(es), 0 aviso(s).
- bloqueo: falta el plan de la etapa a autorizar (plan-etapa-3)
- bloqueo: falta el informe de fin de la etapa 2 (informe-fin-etapa-2)
- condición: condiciones abiertas de puertas anteriores: decision-ad-hoc 2027-01-12 (verificarlas y registrar estado.py cumplir-condiciones, o traspasarlas como recomendación)
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
Condiciones abiertas: decision-ad-hoc: usar USD 10.000 del presupuesto de riesgo para un análisis normativo; revisar R-008 en la próxima junta
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
$ python3 $EST/registro.py --proyecto gestion agregar lecciones --campo "etapa=2" --campo "categoria=riesgo" --campo "situacion=R-001 se materializó: el entorno de pruebas del núcleo dependía de otra área" --campo "efecto=USD 8.000 de la reserva de riesgo (C-002) y 3 días de atraso en WBS 3.2 (sin el entorno temporal, 2 semanas)" --campo "recomendacion=exigir el entorno de pruebas como condición de la puerta autorizar-etapa" --campo "prioridad=alta" --campo "responsable_seguimiento=Martín Suárez"
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
    "total": 8,
    "por_estado": {
      "ocurrido": 1,
      "en-seguimiento": 5,
      "retirado": 1,
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
      "R-008 (15, alto) La norma exige biometría para operaciones de préstamo (FR-6)",
      "R-002 (8, medio) Resistencia a usar la consola",
      "R-004 (8, medio) Cumplimiento exige cambios en FR-5",
      "R-007 (6, medio) El proveedor de SMS falla y la penalidad cobrada no cubre el costo del atraso"
    ]
  },
  "issues": {
    "total": 2,
    "por_estado": {
      "resuelto": 2
    },
    "abiertos": 0,
    "sin_responsable": []
  },
  "cambios": {
    "total": 4,
    "por_estado": {
      "aprobado": 3,
      "rechazado": 1
    },
    "abiertos": 3
  },
  "decisiones": {
    "total": 14
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
$ python3 $EST/estado.py --proyecto gestion cumplir-condiciones decision-ad-hoc --fecha 2027-03-01 --por "Ejecutiva: Laura Méndez" --nota "R-008 revisado en la junta; análisis normativo entregado (C-004)"
ok
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
R-007 amen P2×I3=  6 res P2×I3 EMV    1800 aceptar    en-seguimiento
R-008 amen P3×I5= 15 res P2×I4 EMV   20000 reducir    en-seguimiento
```

## Paso 13 · Variante sin BMAD: destilar riesgos de los artefactos del proyecto
```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Portal de socios (sin BMAD)" --ejecutivo "Laura Méndez" --gestor "Martín Suárez"
Proyecto creado en gestion · enfoque de entrega: predictivo · siguiente: estado.py siguiente
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "supuesto_o_restriccion=El proveedor del núcleo publica la API de lectura antes de marzo" --campo tipo=supuesto --campo validado=pendiente --campo responsable="Área de TI"
S-001
```

```
$ python3 $PLUGIN/skills/pm-riesgos/scripts/riesgos.py --proyecto gestion candidatos --fecha 2026-10-28
bmad: no aplica (el proyecto no usa BMAD: los riesgos salen de los artefactos del proyecto)
transcripciones: 0 candidatos · no disponible
tracker: 0 candidatos · no disponible
artefactos: 7 candidatos · 5 fuente(s) leída(s)
CR-01 [riesgo/amenaza] gestion/00-direccion/mandato.md:7 · La salida en producción debe ocurrir antes del cierre del ejercicio (31/12/2027).
CR-02 [riesgo/amenaza] gestion/00-direccion/mandato.md:8 · El núcleo operativo es de un proveedor externo con ventanas de cambio trimestrales.
CR-03 [riesgo/amenaza] gestion/00-direccion/mandato.md:11 · El proyecto de banca telefónica se atrasó 6 semanas porque el proveedor del núcleo no tenía entorno de pruebas.
CR-04 [supuesto/amenaza] gestion/01-inicio/project-brief.md:4 · Equipo interno con apoyo de un proveedor. [supuesto] El área de TI asigna dos personas a tiempo completo.
CR-05 [pregunta/amenaza] gestion/01-inicio/project-brief.md:7 · ¿Quién aprueba los préstamos simples en el canal digital?
CR-06 [riesgo/amenaza] gestion/02-planificacion/requisitos.md:8 · Los saldos se leen del núcleo operativo por una API de lectura [por confirmar].
CR-07 [supuesto/amenaza] supuestos.csv S-001 · El proveedor del núcleo publica la API de lectura antes de marzo · refs S-001 · Área de TI
→ gestion/03-control/reportes/2026-10-28-candidatos-riesgo.md (borrador). Son candidatos: pm-riesgos los formula, evalúa con el propietario y registra; lo ocurrido va a issues.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-28" --campo "autor=Martín Suárez" --campo "categoria=externo" --campo "causa=El proveedor del núcleo cambia solo en ventanas trimestrales y no publicó la API de lectura (S-001)" --campo "evento=La API de lectura no está disponible en marzo" --campo "efecto=Atraso de la consulta de saldos (REQ-001) y del lanzamiento" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=4" --campo "impacto_monetario=20000" --campo "propietario=Laura Méndez" --campo "ejecutor=Martín Suárez" --campo "notas=origen: mandato.md (restricciones y lecciones), requisitos.md (supuestos) y supuestos.csv S-001"
R-001
```

```
$ python3 $EST/registro.py --proyecto gestion listar riesgos
id=R-001 | fecha_identificacion=2026-10-28 | autor=Martín Suárez | categoria=externo | causa=El proveedor del núcleo cambia solo en ventanas trimestrales y no publicó la API de lectura (S-001) | evento=La API de lectura no está disponible en marzo | efecto=Atraso de la consulta de saldos (REQ-001) y del lanzamiento | tipo=amenaza | probabilidad=3 | impacto=4 | puntuacion=12 | impacto_monetario=20000 | valor_esperado=10000 | propietario=Laura Méndez | ejecutor=Martín Suárez | estado=abierto | notas=origen: mandato.md (restricciones y lecciones), requisitos.md (supuestos) y supuestos.csv S-001
```

