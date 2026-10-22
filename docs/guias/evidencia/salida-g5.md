## Paso 1 · Mandato y lecciones previas
```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Turnos en línea · Policlínicas Altamar" --idioma es --ejecutivo "Carmen Olivera" --gestor "Pablo Rinaldi" --fecha 2026-11-02
Proyecto creado en gestion · enfoque de entrega: predictivo · siguiente: estado.py siguiente
```

```
$ (pm-mandato-y-brief, templates/mandato.md → gestion/00-direccion/mandato.md)
# Mandato del proyecto · Turnos en línea · Policlínicas Altamar (ficticia)

## 1. Origen
Correo de la gerenta general, Carmen Olivera, del 2026-11-02 a la dirección de la red (6 policlínicas).

## 2. Qué se pide
"Que los pacientes saquen, confirmen y cancelen turnos sin llamar. El call center no da abasto y el ausentismo nos
cuesta caro." Restricción: el canal telefónico y el presencial se mantienen (decisión de la dirección).

## 3. Personas
Autoridad emisora y ejecutiva prospectiva: Carmen Olivera. Gestor propuesto: Pablo Rinaldi.

## 4. Contexto (datos de la red, 2026)
- 240.000 turnos por año; 70 % se agendan por teléfono.
- Ausentismo (el paciente no se presenta ni avisa): 18 %.
- Margen de un turno que se recupera: USD 5 (finanzas). Costo de una llamada atendida: USD 1,20 (finanzas).
- [supuesto] Buena parte de los pacientes sacaría el turno en línea si pudiera.
- [supuesto] Un recordatorio con confirmación baja mucho el ausentismo.
- [supuesto] El proveedor de la agenda clínica permite reservar y cancelar turnos desde otro sistema [por confirmar].

## 5. Anotaciones del gestor
Faltan: presupuesto disponible y fecha deseada [por confirmar con la ejecutiva].
```

```
$ (índice de lecciones de la red, exportado por la PMO con lecciones.py buscar --exportar → pmo-altamar/lecciones-indice.csv)
5 lecciones de 4 proyectos (una sin aprobar)
```

```
$ python3 $PLUGIN/skills/pm-lecciones-aprendidas/scripts/lecciones.py buscar --indice pmo-altamar/lecciones-indice.csv --texto "pacientes turnos agenda recordatorios"
Lecciones aprobadas que coinciden: 3 de 4 (omitidas: 1 sin aprobar, 0 copias).
- piloto-de-recordatorios-de-odontologia:L-002 · Piloto de recordatorios de odontología · 2025-09-15 · beneficios · #recordatorios;ausentismo;linea-base · alta · accionada-proyecto · coincide: recordatorios
    situación: Piloto de recordatorios por SMS en odontología (2025)
    recomendación: medir la línea base antes de cualquier piloto
- historia-clinica-electronica:L-007 · Historia clínica electrónica · 2025-06-30 · tecnica · #agenda-clinica;integracion;proveedor · alta · revisada · coincide: agenda
    situación: Historia clínica (2025): la integración con la agenda clínica se estimó en 4 semanas y llevó 14
    recomendación: validar la interfaz del proveedor con una prueba técnica antes de comprometer fechas
- app-de-resultados-de-laboratorio:L-004 · App de resultados de laboratorio · 2024-11-20 · adopcion · #pacientes;adopcion;canal-digital · alta · accionada-organizacion · coincide: pacientes
    situación: App de resultados de laboratorio (2024): 11 % de uso en pacientes mayores de 65
    recomendación: mantener un canal asistido y medir la adopción por franja de edad desde el día 1
Para proponerlas como lecciones previas: lecciones.py incorporar --proyecto <dir> … --ids <ref,ref> (vista previa; registra solo con --confirmar --por).
```

```
$ python3 $PLUGIN/skills/pm-lecciones-aprendidas/scripts/lecciones.py incorporar --proyecto gestion --indice pmo-altamar/lecciones-indice.csv --ids app-de-resultados-de-laboratorio:L-004,historia-clinica-electronica:L-007,piloto-de-recordatorios-de-odontologia:L-002
Vista previa: 3 lección(es) previa(s) para gestion/03-control/registros/lecciones.csv (no se registró nada):
- App de resultados de laboratorio · L-004 · 2024-11-20 · adopcion · #pacientes;adopcion;canal-digital · responsable Pablo Rinaldi
    recomendación: mantener un canal asistido y medir la adopción por franja de edad desde el día 1
- Historia clínica electrónica · L-007 · 2025-06-30 · tecnica · #agenda-clinica;integracion;proveedor · responsable Pablo Rinaldi
    recomendación: validar la interfaz del proveedor con una prueba técnica antes de comprometer fechas
- Piloto de recordatorios de odontología · L-002 · 2025-09-15 · beneficios · #recordatorios;ausentismo;linea-base · responsable Pablo Rinaldi
    recomendación: medir la línea base antes de cualquier piloto
Confirmar con la persona y repetir con --confirmar --por "Gestor: Nombre". Luego convertir cada una en un control temprano (riesgo con respuesta, acción o condición del plan) y marcarla accionada-proyecto con notas=incorporada: <artefacto>.
```

```
$ python3 $PLUGIN/skills/pm-lecciones-aprendidas/scripts/lecciones.py incorporar --proyecto gestion --indice pmo-altamar/lecciones-indice.csv --ids app-de-resultados-de-laboratorio:L-004,historia-clinica-electronica:L-007,piloto-de-recordatorios-de-odontologia:L-002 --confirmar --por "Gestor: Pablo Rinaldi" --fecha 2026-11-02
Lecciones previas registradas (estado registrada): L-001 ← App de resultados de laboratorio · L-004 · 2024-11-20; L-002 ← Historia clínica electrónica · L-007 · 2025-06-30; L-003 ← Piloto de recordatorios de odontología · L-002 · 2025-09-15
Siguiente: un control temprano por lección (pm-riesgos, acción en pm-registros o condición del plan de la etapa) y marcarla accionada-proyecto con notas=incorporada: <artefacto>.
```

```
$ python3 $EST/registro.py --proyecto gestion listar lecciones
id=L-001 | fecha=2026-11-02 | etapa=0 | categoria=adopcion | situacion=App de resultados de laboratorio (2024): 11 % de uso en pacientes mayores de 65 | efecto=la app no redujo las llamadas de ese grupo | recomendacion=mantener un canal asistido y medir la adopción por franja de edad desde el día 1 | prioridad=alta | responsable_seguimiento=Pablo Rinaldi | estado=registrada | notas=lección previa de otro proyecto; confirmada por Gestor: Pablo Rinaldi | origen=App de resultados de laboratorio · L-004 · 2024-11-20 | etiquetas=pacientes;adopcion;canal-digital
id=L-002 | fecha=2026-11-02 | etapa=0 | categoria=tecnica | situacion=Historia clínica (2025): la integración con la agenda clínica se estimó en 4 semanas y llevó 14 | efecto=el proveedor no tenía una interfaz documentada; atraso de 10 semanas | recomendacion=validar la interfaz del proveedor con una prueba técnica antes de comprometer fechas | prioridad=alta | responsable_seguimiento=Pablo Rinaldi | estado=registrada | notas=lección previa de otro proyecto; confirmada por Gestor: Pablo Rinaldi | origen=Historia clínica electrónica · L-007 · 2025-06-30 | etiquetas=agenda-clinica;integracion;proveedor
id=L-003 | fecha=2026-11-02 | etapa=0 | categoria=beneficios | situacion=Piloto de recordatorios por SMS en odontología (2025) | efecto=bajó el ausentismo pero nadie midió la línea base y no se pudo justificar la extensión | recomendacion=medir la línea base antes de cualquier piloto | prioridad=alta | responsable_seguimiento=Pablo Rinaldi | estado=registrada | notas=lección previa de otro proyecto; confirmada por Gestor: Pablo Rinaldi | origen=Piloto de recordatorios de odontología · L-002 · 2025-09-15 | etiquetas=recordatorios;ausentismo;linea-base
```

## Paso 2 · Mapa de supuestos: criticidad y certeza (deseabilidad, viabilidad, factibilidad)
```
$ python3 $PLUGIN/skills/pm-riesgos/scripts/riesgos.py --proyecto gestion candidatos --fuentes artefactos --fecha 2026-11-04
artefactos: 5 candidatos · 3 fuente(s) leída(s)
CR-01 [supuesto/amenaza] gestion/00-direccion/mandato.md:17 · [supuesto] Buena parte de los pacientes sacaría el turno en línea si pudiera.
CR-02 [supuesto/amenaza] gestion/00-direccion/mandato.md:18 · [supuesto] Un recordatorio con confirmación baja mucho el ausentismo.
CR-03 [supuesto/amenaza] gestion/00-direccion/mandato.md:19 · [supuesto] El proveedor de la agenda clínica permite reservar y cancelar turnos desde otro sistema [por confirmar].
CR-04 [supuesto/amenaza] gestion/00-direccion/mandato.md:22 · Faltan: presupuesto disponible y fecha deseada [por confirmar con la ejecutiva].
CR-05 [riesgo/amenaza] lecciones.csv L-002 · Historia clínica (2025): la integración con la agenda clínica se estimó en 4 semanas y llevó 14 → el proveedor no tenía una interfaz documen · refs L-002
→ gestion/03-control/reportes/2026-11-04-candidatos-riesgo.md (borrador). Son candidatos: pm-riesgos los formula, evalúa con el propietario y registra; lo ocurrido va a issues.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-11-04" --campo "autor=Pablo Rinaldi" --campo "supuesto_o_restriccion=Al menos el 40 % de los turnos se sacará en línea desde el segundo año (20 % el primero)" --campo "tipo=supuesto" --campo "categoria=deseabilidad" --campo "criticidad=alta" --campo "certeza=baja" --campo "validado=pendiente" --campo "responsable=Inés Ferrer" --campo "notas=sostiene B-02 (llamadas evitadas) · origen: mandato.md §4 y L-001"
S-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-11-04" --campo "autor=Pablo Rinaldi" --campo "supuesto_o_restriccion=Un recordatorio con confirmación baja el ausentismo del 18 % al 10 %" --campo "tipo=supuesto" --campo "categoria=viabilidad" --campo "criticidad=alta" --campo "certeza=baja" --campo "validado=pendiente" --campo "responsable=Inés Ferrer" --campo "notas=sostiene B-01 (turnos recuperados) · origen: mandato.md §4 y L-003"
S-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-11-04" --campo "autor=Pablo Rinaldi" --campo "supuesto_o_restriccion=La agenda clínica del proveedor permite reservar y cancelar turnos en tiempo real desde otro sistema" --campo "tipo=supuesto" --campo "categoria=factibilidad" --campo "criticidad=alta" --campo "certeza=baja" --campo "validado=pendiente" --campo "responsable=Tomás Aguirre" --campo "notas=sin esto no hay turnos en línea · origen: mandato.md §4 y L-002"
S-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-11-04" --campo "autor=Pablo Rinaldi" --campo "supuesto_o_restriccion=La dirección médica libera las agendas con 60 días de anticipación" --campo "tipo=supuesto" --campo "categoria=viabilidad" --campo "criticidad=media" --campo "certeza=media" --campo "validado=pendiente" --campo "responsable=Inés Ferrer" --campo "notas=condiciona la oferta de turnos en línea"
S-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-11-04" --campo "autor=Pablo Rinaldi" --campo "supuesto_o_restriccion=Se mantienen el canal telefónico y el presencial" --campo "tipo=restriccion" --campo "categoria=deseabilidad" --campo "criticidad=baja" --campo "certeza=alta" --campo "validado=pendiente" --campo "responsable=Carmen Olivera" --campo "notas=restricción de la dirección · origen: mandato.md §2"
S-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-11-04" --campo "autor=Pablo Rinaldi" --campo "supuesto_o_restriccion=La normativa de protección de datos permite enviar recordatorios por mensajería con el consentimiento dado al pedir el turno" --campo "tipo=supuesto" --campo "categoria=factibilidad" --campo "criticidad=alta" --campo "certeza=media" --campo "validado=pendiente" --campo "responsable=Carmen Olivera" --campo "notas=si no, el recordatorio pierde alcance"
S-006
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-11-04" --campo "autor=Pablo Rinaldi" --campo "supuesto_o_restriccion=El costo por mensaje se mantiene en USD 0,02" --campo "tipo=supuesto" --campo "categoria=viabilidad" --campo "criticidad=baja" --campo "certeza=media" --campo "validado=pendiente" --campo "responsable=Tomás Aguirre" --campo "notas=pesa poco en el caso"
S-007
```

```
$ python3 $EST/registro.py --proyecto gestion listar supuestos
id=S-001 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=Al menos el 40 % de los turnos se sacará en línea desde el segundo año (20 % el primero) | tipo=supuesto | categoria=deseabilidad | validado=pendiente | responsable=Inés Ferrer | estado=abierto | notas=sostiene B-02 (llamadas evitadas) · origen: mandato.md §4 y L-001 | criticidad=alta | certeza=baja
id=S-002 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=Un recordatorio con confirmación baja el ausentismo del 18 % al 10 % | tipo=supuesto | categoria=viabilidad | validado=pendiente | responsable=Inés Ferrer | estado=abierto | notas=sostiene B-01 (turnos recuperados) · origen: mandato.md §4 y L-003 | criticidad=alta | certeza=baja
id=S-003 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=La agenda clínica del proveedor permite reservar y cancelar turnos en tiempo real desde otro sistema | tipo=supuesto | categoria=factibilidad | validado=pendiente | responsable=Tomás Aguirre | estado=abierto | notas=sin esto no hay turnos en línea · origen: mandato.md §4 y L-002 | criticidad=alta | certeza=baja
id=S-004 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=La dirección médica libera las agendas con 60 días de anticipación | tipo=supuesto | categoria=viabilidad | validado=pendiente | responsable=Inés Ferrer | estado=abierto | notas=condiciona la oferta de turnos en línea | criticidad=media | certeza=media
id=S-005 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=Se mantienen el canal telefónico y el presencial | tipo=restriccion | categoria=deseabilidad | validado=pendiente | responsable=Carmen Olivera | estado=abierto | notas=restricción de la dirección · origen: mandato.md §2 | criticidad=baja | certeza=alta
id=S-006 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=La normativa de protección de datos permite enviar recordatorios por mensajería con el consentimiento dado al pedir el turno | tipo=supuesto | categoria=factibilidad | validado=pendiente | responsable=Carmen Olivera | estado=abierto | notas=si no, el recordatorio pierde alcance | criticidad=alta | certeza=media
id=S-007 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=El costo por mensaje se mantiene en USD 0,02 | tipo=supuesto | categoria=viabilidad | validado=pendiente | responsable=Tomás Aguirre | estado=abierto | notas=pesa poco en el caso | criticidad=baja | certeza=media
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-04
Sanidad de 'Turnos en línea · Policlínicas Altamar' (pre-proyecto/SU): 0 ERROR · 4 AVISO · 1 INFO
  AVISO SUP-01 Supuesto crítico S-001 sin experimento para validarlo: «Al menos el 40 % de los turnos se sacará en línea desde el segundo año».
  AVISO SUP-01 Supuesto crítico S-002 sin experimento para validarlo: «Un recordatorio con confirmación baja el ausentismo del 18 % al 10 %».
  AVISO SUP-01 Supuesto crítico S-003 sin experimento para validarlo: «La agenda clínica del proveedor permite reservar y cancelar turnos en ».
  AVISO SUP-01 Supuesto crítico S-006 sin experimento para validarlo: «La normativa de protección de datos permite enviar recordatorios por m».
        → Definir cómo se valida (experimento), el criterio para seguir y la fecha límite (registro.py actualizar supuestos S-…).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

## Paso 3 · Experimentos baratos con criterio decidido de antemano, resultados y controles SUP
```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-001 --campo "experimento=prueba de humo: botón «sacá tu turno en línea» en el sitio actual con registro de interés, 3 semanas" --campo "criterio=≥ 1.000 registros de interés en 3 semanas" --campo "fecha_limite=2026-11-27" --campo "responsable=Inés Ferrer"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-002 --campo "experimento=piloto de recordatorio con confirmación por mensajería en la Policlínica Centro, 4 semanas (2.000 turnos)" --campo "criterio=ausentismo del piloto ≤ 12 %" --campo "fecha_limite=2026-12-04" --campo "responsable=Inés Ferrer"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-003 --campo "experimento=prueba técnica de 5 días contra el entorno de pruebas del proveedor: reservar y cancelar 50 turnos" --campo "criterio=50 de 50 sin intervención manual y respuesta < 2 s" --campo "fecha_limite=2026-12-04" --campo "responsable=Tomás Aguirre"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-006 --campo "experimento=consulta formal a la asesoría legal sobre el consentimiento para recordatorios" --campo "criterio=dictamen favorable o condiciones de consentimiento por escrito" --campo "fecha_limite=2027-01-29" --campo "responsable=Carmen Olivera"
ok
```

```
$ (pm-mandato-y-brief, templates/hipotesis-y-experimentos.md → gestion/01-inicio/hipotesis-y-experimentos.md)
# Hipótesis y experimentos · Turnos en línea (v0.1)

## 1. Idea y decisión
Idea: que los pacientes saquen, confirmen y cancelen turnos sin llamar. Decisión esperada: autorizar la iniciación
(2026-12-11) y elegir una opción.

## 2. Supuestos que sostienen la idea (cuadrante crítico + certeza baja: S-001, S-002, S-003)
| Id | Supuesto | Tipo | Criticidad | Certeza |
|---|---|---|---|---|
| S-001 | Al menos el 40 % de los turnos se sacará en línea desde el segundo año (20 % el primero) | deseabilidad | alta | baja |
| S-002 | Un recordatorio con confirmación baja el ausentismo del 18 % al 10 % | viabilidad | alta | baja |
| S-003 | La agenda clínica del proveedor permite reservar y cancelar turnos en tiempo real desde otro sistema | factibilidad | alta | baja |
| S-004 | La dirección médica libera las agendas con 60 días de anticipación | viabilidad | media | media |
| S-005 | Se mantienen el canal telefónico y el presencial | deseabilidad | baja | alta |
| S-006 | La normativa de protección de datos permite enviar recordatorios por mensajería con el consentimiento dado al pedir el turno | factibilidad | alta | media |
| S-007 | El costo por mensaje se mantiene en USD 0,02 | viabilidad | baja | media |

## 3. Experimentos
| Supuesto | Experimento | Criterio para seguir | Fecha límite | Responsable |
|---|---|---|---|---|
| S-001 | prueba de humo: botón «sacá tu turno en línea» en el sitio actual con registro de interés, 3 semanas | ≥ 1.000 registros de interés en 3 semanas | 2026-11-27 | Inés Ferrer |
| S-002 | piloto de recordatorio con confirmación por mensajería en la Policlínica Centro, 4 semanas (2.000 turnos) | ausentismo del piloto ≤ 12 % | 2026-12-04 | Inés Ferrer |
| S-003 | prueba técnica de 5 días contra el entorno de pruebas del proveedor: reservar y cancelar 50 turnos | 50 de 50 sin intervención manual y respuesta < 2 s | 2026-12-04 | Tomás Aguirre |
| S-006 | consulta formal a la asesoría legal sobre el consentimiento para recordatorios | dictamen favorable o condiciones de consentimiento por escrito | 2027-01-29 | Carmen Olivera |
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-11-05
Sanidad de 'Turnos en línea · Policlínicas Altamar' (pre-proyecto/SU): 0 ERROR · 0 AVISO · 1 INFO
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-001 --campo "validado=si" --campo "estado=validado" --campo "certeza=alta" --campo "fecha_validacion=2026-11-27" --campo "evidencia=1.840 registros de interés en 3 semanas (criterio ≥ 1.000)"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-002 --campo "validado=no" --campo "estado=invalidado" --campo "certeza=alta" --campo "fecha_validacion=2026-12-04" --campo "evidencia=piloto Policlínica Centro: ausentismo del 18 % al 13,5 % en 2.000 turnos (criterio ≤ 12 %)"
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-12-07
Sanidad de 'Turnos en línea · Policlínicas Altamar' (pre-proyecto/SU): 0 ERROR · 2 AVISO · 1 INFO
  AVISO SUP-02 Supuesto S-003 con fecha límite 2026-12-04 vencida y sin validar.
        → Registrar la evidencia y el resultado (validado=si|no) o replanificar con la junta.
  AVISO SUP-03 Supuesto S-002 invalidado sin issue, cambio, riesgo o decisión que trate su efecto.
        → Revisar el business case y registrar la decisión (pm-caso-de-negocio, pm-direccion-decisiones).
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-12-07" --campo "decision=S-002 invalidado: el business case usa un ausentismo de 13,5 % (resultado del piloto) en lugar de 10 %; la idea sigue con el beneficio B-01 ajustado" --campo "decidido_por=Ejecutiva: Carmen Olivera" --campo "nivel=ejecutivo" --campo "artefactos_afectados=00-direccion/business-case-esquematico.md; 01-inicio/hipotesis-y-experimentos.md"
D-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-12-07" --campo "decision=Replanificar la prueba técnica de S-003 al 2027-01-14: el proveedor entrega las credenciales del entorno de pruebas el 2027-01-07" --campo "decidido_por=Ejecutiva: Carmen Olivera" --campo "nivel=ejecutivo" --campo "revisar_en=2027-01-14"
D-002
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-003 --campo "fecha_limite=2027-01-14" --campo "notas=sin esto no hay turnos en línea · origen: mandato.md §4 y L-002 · replanificado el 2026-12-07 (credenciales del proveedor el 2027-01-07)"
ok
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-12-07
Sanidad de 'Turnos en línea · Policlínicas Altamar' (pre-proyecto/SU): 0 ERROR · 0 AVISO · 1 INFO
  INFO  ESP-02 El índice de especificación está desactualizado (se reconstruye solo al consultarlo).
        → especificacion.py indice o sanidad.py --reparar.
```

```
$ python3 $EST/estado.py --proyecto gestion artefacto hipotesis-y-experimentos --ruta 01-inicio/hipotesis-y-experimentos.md --estado en-revision --version 0.2
ok
```

```
$ python3 $EST/registro.py --proyecto gestion listar supuestos
id=S-001 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=Al menos el 40 % de los turnos se sacará en línea desde el segundo año (20 % el primero) | tipo=supuesto | categoria=deseabilidad | validado=si | fecha_validacion=2026-11-27 | responsable=Inés Ferrer | estado=validado | notas=sostiene B-02 (llamadas evitadas) · origen: mandato.md §4 y L-001 | criticidad=alta | certeza=alta | experimento=prueba de humo: botón «sacá tu turno en línea» en el sitio actual con registro de interés, 3 semanas | criterio=≥ 1.000 registros de interés en 3 semanas | fecha_limite=2026-11-27 | evidencia=1.840 registros de interés en 3 semanas (criterio ≥ 1.000)
id=S-002 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=Un recordatorio con confirmación baja el ausentismo del 18 % al 10 % | tipo=supuesto | categoria=viabilidad | validado=no | fecha_validacion=2026-12-04 | responsable=Inés Ferrer | estado=invalidado | notas=sostiene B-01 (turnos recuperados) · origen: mandato.md §4 y L-003 | criticidad=alta | certeza=alta | experimento=piloto de recordatorio con confirmación por mensajería en la Policlínica Centro, 4 semanas (2.000 turnos) | criterio=ausentismo del piloto ≤ 12 % | fecha_limite=2026-12-04 | evidencia=piloto Policlínica Centro: ausentismo del 18 % al 13,5 % en 2.000 turnos (criterio ≤ 12 %)
id=S-003 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=La agenda clínica del proveedor permite reservar y cancelar turnos en tiempo real desde otro sistema | tipo=supuesto | categoria=factibilidad | validado=pendiente | responsable=Tomás Aguirre | estado=abierto | notas=sin esto no hay turnos en línea · origen: mandato.md §4 y L-002 · replanificado el 2026-12-07 (credenciales del proveedor el 2027-01-07) | criticidad=alta | certeza=baja | experimento=prueba técnica de 5 días contra el entorno de pruebas del proveedor: reservar y cancelar 50 turnos | criterio=50 de 50 sin intervención manual y respuesta < 2 s | fecha_limite=2027-01-14
id=S-004 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=La dirección médica libera las agendas con 60 días de anticipación | tipo=supuesto | categoria=viabilidad | validado=pendiente | responsable=Inés Ferrer | estado=abierto | notas=condiciona la oferta de turnos en línea | criticidad=media | certeza=media
id=S-005 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=Se mantienen el canal telefónico y el presencial | tipo=restriccion | categoria=deseabilidad | validado=pendiente | responsable=Carmen Olivera | estado=abierto | notas=restricción de la dirección · origen: mandato.md §2 | criticidad=baja | certeza=alta
id=S-006 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=La normativa de protección de datos permite enviar recordatorios por mensajería con el consentimiento dado al pedir el turno | tipo=supuesto | categoria=factibilidad | validado=pendiente | responsable=Carmen Olivera | estado=abierto | notas=si no, el recordatorio pierde alcance | criticidad=alta | certeza=media | experimento=consulta formal a la asesoría legal sobre el consentimiento para recordatorios | criterio=dictamen favorable o condiciones de consentimiento por escrito | fecha_limite=2027-01-29
id=S-007 | fecha=2026-11-04 | autor=Pablo Rinaldi | supuesto_o_restriccion=El costo por mensaje se mantiene en USD 0,02 | tipo=supuesto | categoria=viabilidad | validado=pendiente | responsable=Tomás Aguirre | estado=abierto | notas=pesa poco en el caso | criticidad=baja | certeza=media
```

## Paso 4 · Opciones de negocio 0/1/2 con VAN, TIR, repago y sensibilidad (antes y después de los experimentos)
```
$ (pm-caso-de-negocio: datos de las opciones, del mandato y de finanzas)
Base (opción 0): ausentismo 18 % de 240.000 turnos = 43.200 turnos perdidos por año = USD 216.000 de margen no realizado
B-01 turnos recuperados = 240.000 × (0,18 − ausentismo) × USD 5 · B-02 llamadas evitadas = 240.000 × adopción × USD 1,20 (adopción 20 % el año 1, 40 % después)
Opción 1: inversión 30.000, operación 18.000/año · Opción 2: inversión 180.000 (orden de magnitud −25/+75 %), operación 36.000/año · tasa 10 % (finanzas) · 5 años
Con los supuestos iniciales: ausentismo 10 % (S-002 sin validar) · después de los experimentos: 13,5 % (piloto de S-002)
```

```
$ (pm-caso-de-negocio → gestion/00-direccion/inversion/flujos-supuestos-iniciales.csv)
opcion,concepto,tipo,0,1,2,3,4,5
0 · No hacer nada distinto,Sin cambios,costo,,,,,,
1 · Mínimo: recordatorios,Inversión,inversion,-30000,,,,,
1 · Mínimo: recordatorios,Turnos recuperados (B-01),beneficio,,96000,96000,96000,96000,96000
1 · Mínimo: recordatorios,Operación,costo,,-18000,-18000,-18000,-18000,-18000
2 · Completo: turnos en línea,Inversión,inversion,-180000,,,,,
2 · Completo: turnos en línea,Turnos recuperados (B-01),beneficio,,96000,96000,96000,96000,96000
2 · Completo: turnos en línea,Llamadas evitadas (B-02),beneficio,,57600,115200,115200,115200,115200
2 · Completo: turnos en línea,Operación,costo,,-36000,-36000,-36000,-36000,-36000
```

```
$ python3 $PLUGIN/skills/pm-caso-de-negocio/scripts/inversion.py gestion/00-direccion/inversion/flujos-supuestos-iniciales.csv --tasa 0.10
Evaluación de la inversión · tasa 10,0 % por período · base: 0 · No hacer nada distinto
Fórmulas: VAN = Σ F_t/(1+r)^t, t = 0…n · TIR: VAN(TIR) = 0 · repago interpolado en el período en que el acumulado llega a 0

Opción                                      VAN       TIR   Repago Rep. desc.  VAN vs base
0 · No hacer nada distinto                    0         —        —          —            0
1 · Mínimo: recordatorios               265.681   259,6 %     0,38       0,42      265.681
2 · Completo: turnos en línea           431.782    77,9 %     1,36       1,50      431.782

0 · No hacer nada distinto · flujos netos: 0: 0 | 1: 0 | 2: 0 | 3: 0 | 4: 0 | 5: 0
  Sensibilidad a la tasa: VAN 0 con 8,0 % · 0 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Sin cambios               [costo] VAN 0 … 0 · —

1 · Mínimo: recordatorios · flujos netos: 0: -30.000 | 1: 78.000 | 2: 78.000 | 3: 78.000 | 4: 78.000 | 5: 78.000
  Sensibilidad a la tasa: VAN 281.431 con 8,0 % · 251.173 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Turnos recuperados (B-01) [beneficio] VAN 192.898 … 338.464 · 27,0 % del valor estimado
    Operación                 [costo] VAN 279.328 … 252.035 · 489,4 % del valor estimado
    Inversión                 [inversion] VAN 271.681 … 259.681 · 985,6 % del valor estimado

2 · Completo: turnos en línea · flujos netos: 0: -180.000 | 1: 117.600 | 2: 175.200 | 3: 175.200 | 4: 175.200 | 5: 175.200
  Sensibilidad a la tasa: VAN 466.189 con 8,0 % · 400.128 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Llamadas evitadas (B-02)  [beneficio] VAN 354.915 … 508.649 · ningún valor positivo del concepto lo lleva a 0
    Turnos recuperados (B-01) [beneficio] VAN 358.999 … 504.565 · ningún valor positivo del concepto lo lleva a 0
    Inversión                 [inversion] VAN 467.782 … 395.782 · 339,9 % del valor estimado
    Operación                 [costo] VAN 459.076 … 404.489 · 416,4 % del valor estimado
```

```
$ (pm-caso-de-negocio → gestion/00-direccion/inversion/flujos-opciones.csv)
opcion,concepto,tipo,0,1,2,3,4,5
0 · No hacer nada distinto,Sin cambios,costo,,,,,,
1 · Mínimo: recordatorios,Inversión,inversion,-30000,,,,,
1 · Mínimo: recordatorios,Turnos recuperados (B-01),beneficio,,54000,54000,54000,54000,54000
1 · Mínimo: recordatorios,Operación,costo,,-18000,-18000,-18000,-18000,-18000
2 · Completo: turnos en línea,Inversión,inversion,-180000,,,,,
2 · Completo: turnos en línea,Turnos recuperados (B-01),beneficio,,54000,54000,54000,54000,54000
2 · Completo: turnos en línea,Llamadas evitadas (B-02),beneficio,,57600,115200,115200,115200,115200
2 · Completo: turnos en línea,Operación,costo,,-36000,-36000,-36000,-36000,-36000
```

```
$ python3 $PLUGIN/skills/pm-caso-de-negocio/scripts/inversion.py gestion/00-direccion/inversion/flujos-opciones.csv --tasa 0.10
Evaluación de la inversión · tasa 10,0 % por período · base: 0 · No hacer nada distinto
Fórmulas: VAN = Σ F_t/(1+r)^t, t = 0…n · TIR: VAN(TIR) = 0 · repago interpolado en el período en que el acumulado llega a 0

Opción                                      VAN       TIR   Repago Rep. desc.  VAN vs base
0 · No hacer nada distinto                    0         —        —          —            0
1 · Mínimo: recordatorios               106.468   117,5 %     0,83       0,92      106.468
2 · Completo: turnos en línea           272.569    54,3 %     1,78       2,01      272.569

0 · No hacer nada distinto · flujos netos: 0: 0 | 1: 0 | 2: 0 | 3: 0 | 4: 0 | 5: 0
  Sensibilidad a la tasa: VAN 0 con 8,0 % · 0 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Sin cambios               [costo] VAN 0 … 0 · —

1 · Mínimo: recordatorios · flujos netos: 0: -30.000 | 1: 36.000 | 2: 36.000 | 3: 36.000 | 4: 36.000 | 5: 36.000
  Sensibilidad a la tasa: VAN 113.738 con 8,0 % · 99.772 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Turnos recuperados (B-01) [beneficio] VAN 65.528 … 147.409 · 48,0 % del valor estimado
    Operación                 [costo] VAN 120.115 … 92.821 · 256,0 % del valor estimado
    Inversión                 [inversion] VAN 112.468 … 100.468 · 454,9 % del valor estimado

2 · Completo: turnos en línea · flujos netos: 0: -180.000 | 1: 75.600 | 2: 133.200 | 3: 133.200 | 4: 133.200 | 5: 133.200
  Sensibilidad a la tasa: VAN 298.496 con 8,0 % · 248.728 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Llamadas evitadas (B-02)  [beneficio] VAN 195.702 … 349.436 · 29,1 % del valor estimado
    Turnos recuperados (B-01) [beneficio] VAN 231.629 … 313.510 · ningún valor positivo del concepto lo lleva a 0
    Inversión                 [inversion] VAN 308.569 … 236.569 · 251,4 % del valor estimado
    Operación                 [costo] VAN 299.863 … 245.275 · 299,7 % del valor estimado
```

```
$ (lectura de pm-caso-de-negocio, de inversion.py --json)
El supuesto de S-002 (10 %) inflaba el VAN de cada opción en USD 159.213: opción 2 de 431.782 a 272.569; opción 1 de 265.681 a 106.468.
B-02 aporta el 65 % del valor actual de los beneficios de la opción 2 (más del 50 %: la sensibilidad es obligatoria).
Punto de equilibrio de B-02: 29,1 % de lo estimado = adopción estable de 11,6 % (VAN = 0).
VAN incremental de la opción 2 sobre la 1: USD 166.101 por USD 150.000 más de inversión.
```

```
$ (pm-caso-de-negocio, modo esquemático → gestion/00-direccion/business-case-esquematico.md)
# Business case esquemático · Turnos en línea (v0.1)

## 2. Razones
Ausentismo del 18 %: 43.200 turnos perdidos por año (USD 216.000 de margen). El call center atiende el 70 % de los turnos.

## 4. Opciones de negocio (después de los experimentos; VAN a 5 años, r = 10 %; inversion.py con 00-direccion/inversion/flujos-opciones.csv)
| Opción | Inversión | Beneficio neto año 2 | VAN | TIR | Repago |
|---|---|---|---|---|---|
| 0 · No hacer nada distinto | 0 | 0 | 0 (base) | — | — |
| 1 · Mínimo: recordatorios | 30.000 | 36.000 | 106.468 | 117,5 % | 0,83 años |
| 2 · Completo: turnos en línea | 180.000 | 133.200 | 272.569 | 54,3 % | 1,78 años |

Recomendación: opción 2 en dos releases. El primero entrega el valor de la opción 1 (recordatorios); el segundo, turnos en
línea, solo si S-003 está validado. Sensibilidad: B-02 aporta el 65 % del valor de los beneficios; el VAN de la
opción 2 llega a 0 con una adopción estable de 11,6 % (29,1 % de lo estimado).

## 5. Beneficios
B-01 turnos recuperados (ausentismo 18 % → 13,5 %) · B-02 llamadas evitadas (adopción 40 %) · DB-01 des-beneficio:
dos puestos del call center se reasignan a recepción.
```

## Paso 5 · Enfoque de entrega: nueve criterios por entregable (1 = predictivo, 3 = adaptativo)
```
$ (pm-mandato-y-brief, references/guia.md §3: tabla de nueve criterios de pm-knowledge/references/pmbok8-estandar-principios-ciclos.md §4.4.4; suma ≤ 13 predictivo, 14–21 híbrido, ≥ 22 adaptativo)
criterio                                    Recordatorios y confir  Turnos en línea (porta  Integración con la age
Certeza de requisitos                                            1                       3                       1
Estabilidad del alcance                                          1                       3                       1
Costo del cambio en el entregable                                2                       3                       1
Regulación / seguridad                                           2                       2                       2
Valor de la retroalimentación frecuente                          2                       3                       1
Disponibilidad de interesados                                    2                       2                       1
Cultura organizativa                                             2                       2                       2
Tamaño del equipo                                                3                       3                       2
Presión por entrega temprana de valor                            3                       2                       1
suma · lectura                                        18 · híbrido         23 · adaptativo         12 · predictivo
Entregables con lecturas distintas → proyecto híbrido por construcción (cada entregable con su vía); se revisa en cada puerta de etapa.
```

```
$ python3 $EST/estado.py --proyecto gestion set enfoque_entrega=hibrido --por "Ejecutiva: Carmen Olivera" --nivel ejecutivo --fecha 2026-12-09
Decisión anotada: D-003
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar decisiones D-003 --campo "opciones_consideradas=predictivo; ágil; híbrido (nueve criterios: integración con la agenda 12, recordatorios 18, turnos en línea 23)" --campo "revisar_en=cada puerta de etapa" --campo "notas=estado.py set · etapas PRINCE2 con sprints de 14 días dentro"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion listar decisiones
id=D-001 | fecha=2026-12-07 | decision=S-002 invalidado: el business case usa un ausentismo de 13,5 % (resultado del piloto) en lugar de 10 %; la idea sigue con el beneficio B-01 ajustado | decidido_por=Ejecutiva: Carmen Olivera | nivel=ejecutivo | artefactos_afectados=00-direccion/business-case-esquematico.md; 01-inicio/hipotesis-y-experimentos.md
id=D-002 | fecha=2026-12-07 | decision=Replanificar la prueba técnica de S-003 al 2027-01-14: el proveedor entrega las credenciales del entorno de pruebas el 2027-01-07 | decidido_por=Ejecutiva: Carmen Olivera | nivel=ejecutivo | revisar_en=2027-01-14
id=D-003 | fecha=2026-12-09 | decision=enfoque de entrega: predictivo → hibrido | contexto=pre-proyecto/SU | opciones_consideradas=predictivo; ágil; híbrido (nueve criterios: integración con la agenda 12, recordatorios 18, turnos en línea 23) | decidido_por=Ejecutiva: Carmen Olivera | nivel=ejecutivo | revisar_en=cada puerta de etapa | notas=estado.py set · etapas PRINCE2 con sprints de 14 días dentro
```

## Paso 5b · Mapa de valor de los entregables y recorrido del paciente (pm-mapas-estrategicos)
```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion wardley semilla --slug entregables --titulo "Turnos en línea · qué construir y qué comprar" --pregunta "¿Qué parte del servicio construimos, cuál compramos y con qué enfoque se entrega cada una?" --anclas "Paciente" --componentes "Turnos en línea (portal y app); Recordatorios y confirmación; Mensajería SMS y correo; Adaptador de la agenda clínica; Agenda clínica del proveedor; Hosting" --fecha 2026-12-09
Semilla 02-planificacion/mapas/wardley-entregables.json desde artefactos: 1 ancla(s), 6 componente(s), 0 enlace(s); posiciones y evidencia [por confirmar].
Siguiente: completar con evidencia, 'validar' y 'render'. El modelo propone; la persona confirma.
```

```
$ (pm-mapas-estrategicos propone ubicación, decisión y evidencia de cada componente; Pablo Rinaldi y Tomás Aguirre confirman → gestion/02-planificacion/mapas/wardley-entregables.json)
C1 Turnos en línea (portal y app) · a-medida (0,35) · visibilidad 0,80 · construir · diferencia a la red; S-001 validado (1.840 registros de interés); 23 puntos en los nueve criterios · refs S-001
C2 Recordatorios y confirmación · producto (0,62) · visibilidad 0,70 · comprar · hay plataformas de recordatorio en el mercado; el piloto de S-002 usó una existente (L-003 midió sin línea base) · refs S-002, L-003
C3 Mensajería SMS y correo · commodity (0,88) · visibilidad 0,45 · tercerizar · servicio por mensaje con varios proveedores; USD 0,02 por mensaje (S-007) · refs S-007
C4 Adaptador de la agenda clínica · a-medida (0,30) · visibilidad 0,50 · construir · no hay conector del proveedor: se escribe a medida; L-002: 4 semanas estimadas, 14 reales · refs S-003, L-002
C5 Agenda clínica del proveedor · producto (0,60) · visibilidad 0,30 · sin decisión · inercia · sistema comprado en uso en las 6 policlínicas; reemplazarlo está fuera de alcance; el proveedor controla la interfaz (S-003) · refs S-003
C6 Hosting · commodity (0,90) · visibilidad 0,12 · comprar · servicio estándar de nube ya contratado por TI (Tomás Aguirre)
7 enlaces · 1 nota
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion wardley validar entregables
wardley-entregables.json: 0 error(es) · 0 aviso(s)
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion wardley render entregables --png no
Vistas: 02-planificacion/visuales/wardley-entregables.md, 02-planificacion/visuales/wardley-entregables.owm
Registrar (si es nuevo): estado.py --proyecto gestion artefacto mapa-wardley-entregables --ruta 02-planificacion/visuales/wardley-entregables.md --estado borrador
```

```
$ (lectura sugerida de gestion/02-planificacion/visuales/wardley-entregables.md, contrastada con los nueve criterios del paso 5)
C1 Turnos en línea (portal y app): adaptativo o híbrido; construir si diferencia
C2 Recordatorios y confirmación: híbrido; preferir comprar o configurar
C3 Mensajería SMS y correo: predictivo; comprar, tercerizar o usar como servicio
C4 Adaptador de la agenda clínica: predictivo con hitos de validación: depende de un componente con inercia (C5)
C5 Agenda clínica del proveedor: riesgo de inercia: registrarlo y planificar la transición
C6 Hosting: predictivo; comprar, tercerizar o usar como servicio
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion recorrido semilla --slug paciente --titulo "Paciente que saca y cancela un turno (hoy)" --persona "Paciente que agenda por teléfono" --etapas "Pedir el turno; Esperar el día; Cancelar o asistir" --fecha 2026-12-09
Semilla 02-planificacion/mapas/recorrido-paciente.json desde artefactos: 3 etapa(s), 3 paso(s); emociones y fuentes [por confirmar]
Siguiente: completar con evidencia, 'validar' y 'render'. El modelo propone; la persona confirma.
```

```
$ (pm-mapas-estrategicos propone el recorrido actual con la fuente de cada emoción; Inés Ferrer confirma → gestion/02-planificacion/mapas/recorrido-paciente.json)
Pedir el turno · P1 Llama al call center · -1 (mandato §2: «el call center no da abasto»; 70 % de los turnos por teléfono) · dolor: Espera en línea en las horas pico → Sacar el turno en línea 24 × 7 · refs S-001
Pedir el turno · P2 Acuerda fecha y hora con la operadora · 0 (supuesto declarado: sin datos de satisfacción del call center)
Esperar el día · P3 Anota el turno · 0 (supuesto declarado)
Esperar el día · P4 Olvida el turno · -2 (métrica: ausentismo del 18 % (mandato §4); el piloto con recordatorio lo bajó al 13,5 % (S-002)) · dolor: Nadie le recuerda el turno → Recordatorio 48 h antes con confirmación · refs S-002
Cancelar o asistir · P5 Intenta avisar que no va · -2 (supuesto declarado: solo se cancela llamando en horario de atención (mandato §2)) · dolor: Solo puede cancelar llamando en horario de atención → Cancelar desde el recordatorio y liberar el turno
Cancelar o asistir · P6 Se atiende en la policlínica · +1 (supuesto declarado)
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion recorrido validar paciente
recorrido-paciente.json: 0 error(es) · 0 aviso(s)
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion recorrido render paciente --png no
Vistas: 02-planificacion/visuales/recorrido-paciente.md, 02-planificacion/visuales/recorrido-paciente.html
Registrar (si es nuevo): estado.py --proyecto gestion artefacto mapa-recorrido-paciente --ruta 02-planificacion/visuales/recorrido-paciente.md --estado borrador
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion recorrido candidatos paciente
P5 [requisito] Cancelar desde el recordatorio y liberar el turno · 02-planificacion/mapas/recorrido-paciente.json#P5
1 candidato(s); se registran solo tras la evaluación humana.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-12-09
Sanidad de 'Turnos en línea · Policlínicas Altamar' (pre-proyecto/SU): 0 ERROR · 2 AVISO · 0 INFO
  AVISO MAP-02 wardley-entregables.json C5 Agenda clínica del proveedor: inercia sin riesgo abierto registrado
        → Registrar el riesgo de la inercia con pm-riesgos (registro.py agregar riesgos) y citarlo: mapas.py vincular <mapa> <id> --refs R-…
  AVISO MAP-03 recorrido-paciente.json P5 «Intenta avisar que no va»: dolor sin tratamiento (requisito, historia, riesgo, issue, cambio, decisión, supuesto o revisión de calidad)
        → Tratar el dolor con un requisito, historia del backlog, riesgo, issue, cambio, decisión, supuesto o revisión de calidad (Q-###) y citarlo con mapas.py vincular (candidatos: mapas.py recorrido candidatos).
```

## Paso 6 · Project brief, requisitos, roadmap y canvas → puerta autorizar-inicio
```
$ (pm-planificacion-por-productos, templates/requisitos.md → gestion/02-planificacion/requisitos.md; sin BMAD, pm-method es la fuente de la especificación)
7 requisitos REQ-001…REQ-007 (5 Must, 2 Should)
```

```
$ python3 $EST/especificacion.py --proyecto gestion fuente
Proveedor de especificación: pm-method · índice reconstruido ahora (<fecha-hora>)
  dueño de requisitos: pm-method requisitos.md (pm-planificacion-por-productos)
  dueño de backlog y gobierno: pm-method backlog.csv
  dueño de paquetes_wbs: pm-method wbs.csv (columna ref)
```

```
$ python3 $EST/especificacion.py --proyecto gestion resumen
requisitos: 7
sin_cobertura: ['REQ-001', 'REQ-002', 'REQ-003', 'REQ-004', 'REQ-005', 'REQ-006', 'REQ-007']
historias: 0
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion vincular paciente P5 --refs REQ-003,REQ-005
recorrido-paciente.json P5: refs = REQ-003, REQ-005
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion controles
AVISO MAP-02 wardley-entregables.json C5 Agenda clínica del proveedor: inercia sin riesgo abierto registrado
1 aviso(s) de la familia MAP
```

```
$ (pm-mandato-y-brief, templates/project-brief.md → gestion/01-inicio/project-brief.md)
# Project brief · Turnos en línea · Policlínicas Altamar (v0.1)

## 1. Definición
Objetivo: bajar el ausentismo y las llamadas para agendar. Alcance: recordatorios con confirmación, turnos en línea,
integración con la agenda clínica, capacitación. Exclusión: telemedicina y pagos en línea.
## 2. Caso de negocio esquemático
Ver 00-direccion/business-case-esquematico.md: opción 2 en dos releases (VAN USD 272.569, repago 1,78 años).
## 3. Producto del proyecto
Servicio de turnos sin llamada: recordatorios (REQ-001…003), turnos en línea (REQ-004, 005, 007), integración (REQ-006).
## 4. Enfoque del proyecto
Interno con el proveedor de la agenda; adaptar su interfaz, no reemplazarla; híbrido (decisión del 2026-12-09):
integración predictiva, recordatorios incrementales, portal adaptativo. Sostenibilidad: menos traslados por turnos perdidos.
## 5. Estructura
Ejecutiva Carmen Olivera; gestor Pablo Rinaldi; usuaria sénior y proveedor sénior a designar en la iniciación.
## 6. Hitos y etapas
Etapa 1 iniciación (hasta 2027-01-15) · etapa 2 recordatorios · etapa 3 turnos en línea (puerta condicionada a S-003).
## 7. Lecciones aplicadas
L-001 canal asistido · L-002 prueba técnica antes de fechas · L-003 línea base medida (ausentismo 18 %).
## 8. Tolerancias del proyecto (las fija la ejecutiva)
tiempo ±4 semanas · costo ±10 % · alcance: Must sin tolerancia · beneficios −15 % · riesgo: ningún riesgo alto sin respuesta.
```

```
$ (pm-mandato-y-brief, templates/roadmap.md → gestion/01-inicio/roadmap.md)
# Hoja de ruta inicial · Turnos en línea
| Etapa | Contenido | Puerta de salida |
|---|---|---|
| 0 · Puesta en marcha | mandato, supuestos, experimentos, brief | autorizar-inicio (2026-12-11) |
| 1 · Iniciación | business case, PBS, presupuesto, enfoques, PID | autorizar-proyecto y autorizar-etapa (2027-01-15) |
| 2 · Release 1: recordatorios | REQ-001…003 en 6 policlínicas | autorizar-etapa (adopción y ausentismo medidos) |
| 3 · Release 2: turnos en línea | REQ-004…007 con la integración | autorizar-cierre |
Revisión del enfoque de entrega en cada puerta de etapa.
```

```
$ (pm-mandato-y-brief, templates/canvas-arranque.md → gestion/01-inicio/canvas-arranque.md)
# Lienzo de arranque · Turnos en línea
Problema: 18 % de ausentismo y call center saturado · Pacientes: 240.000 turnos/año · Propuesta: sacar, confirmar y cancelar sin llamar ·
Supuestos críticos: S-001, S-002, S-003 · Experimentos: prueba de humo, piloto, prueba técnica · Métricas: ausentismo, % de turnos en línea ·
Costos: 180.000 (orden de magnitud) · Restricción: se mantienen teléfono y presencial.
```

```
$ (pm-plan-etapa-y-limites → gestion/02-planificacion/plan-etapa-1.md)
# Plan de la etapa 1 (iniciación) · 2026-12-11 a 2027-01-15

Business case completo, PBS y WBS, presupuesto, enfoques, PID; prueba técnica de S-003 (2027-01-14).
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar lecciones L-001 --campo "estado=accionada-proyecto" --campo "notas=incorporada: project-brief §7, canal asistido"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar lecciones L-002 --campo "estado=accionada-proyecto" --campo "notas=incorporada: project-brief §7 y plan-etapa-1, prueba técnica de S-003 antes de fechas"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar lecciones L-003 --campo "estado=accionada-proyecto" --campo "notas=incorporada: S-002, línea base medida antes del piloto (ausentismo 18 %)"
ok
```

```
$ python3 $EST/estado.py --proyecto gestion tolerancia --nivel proyecto "tiempo=±4 semanas" "costo=±10 %" "alcance=Must sin tolerancia" "beneficios=-15 %" "riesgo=ningún riesgo alto sin respuesta"
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-inicio
Puerta autorizar-inicio: 1 bloqueo(s) · 0 condición(es) · 0 aviso(s)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-inicio y confirmarla (puertas.py confirmar …)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-inicio --fecha 2026-12-11
Lista creada: 00-direccion/decisiones/2026-12-11-verificacion-autorizar-inicio.md (0 hallazgos automáticos, 5 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-inicio --por "Ejecutiva: Carmen Olivera" --fecha 2026-12-11
Lista 00-direccion/decisiones/2026-12-11-verificacion-autorizar-inicio.md confirmada por Ejecutiva: Carmen Olivera
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-inicio --decision aprobado --por "Ejecutiva: Carmen Olivera" --fecha 2026-12-11 --fin 2027-01-15
ok
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director).
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar project-brief --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2026-12-11
Copia congelada / frozen copy: 00-direccion/historial/project-brief-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar business-case-esquematico --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2026-12-11
Copia congelada / frozen copy: 00-direccion/historial/business-case-esquematico-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Turnos en línea · Policlínicas Altamar · inicio/IP · etapa 1 Iniciación (2026-12-11 → 2027-01-15) · enfoque hibrido · idioma es
Autorizado: no
Roles: ejecutivo=Carmen Olivera; gestor_proyecto=Pablo Rinaldi
Tolerancias: proyecto: tiempo=±4 semanas, costo=±10 %, alcance=Must sin tolerancia, beneficios=-15 %, riesgo=ningún riesgo alto sin respuesta | etapa: 
Artefactos: 9 (2 aprobados)
Última puerta: autorizar-inicio · aprobado · 2026-12-11 · Ejecutiva: Carmen Olivera
Próxima puerta: autorizar-proyecto · 3 bloqueo(s) · 5 condición(es) (detalle: puertas.py verificar autorizar-proyecto)
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director).
```

## Paso 7 · Retomar la sesión, mapa de beneficios y enfoque de beneficios (P-04)
```
$ python3 $EST/estado.py --proyecto gestion contexto --corte 2027-01-08
pm-method · contexto derivado de estado.json y los registros al 2027-01-08 (es el estado vigente; una nota de memoria que diga otra cosa está desactualizada):
Abiertos: supuestos 5.
Supuestos críticos sin validar: S-003, S-006.
Próxima puerta: autorizar-proyecto (detalle: puertas.py verificar autorizar-proyecto).
```

```
$ python3 $EST/estado.py --proyecto gestion radar --linea --corte 2027-01-08
pm-method · radar al 2027-01-08: decidir 0 · escalar 0 · desbloquear 0 · vigilar 2 (S-003); detalle, responsables y siguiente paso: pm-orquestador (estado.py radar).
```

```
$ (pm-caso-de-negocio, modo completo → gestion/00-direccion/business-case.md)
# Business case · Turnos en línea (v0.9, completo)

## 3. Cadena de valor
Salidas (recordatorios, turnos en línea, integración) → capacidades (confirmar y cancelar sin llamar; reservar 24×7) →
resultados (menos ausentismo; menos llamadas) → beneficios B-01, B-02 → objetivo: más pacientes atendidos con la misma capacidad.

## 5. Beneficios y des-beneficios
| Id | Beneficio | Medida | Línea base | Meta | Dueña | Tolerancia |
|---|---|---|---|---|---|---|
| B-01 | Turnos recuperados | ausentismo mensual | 18 % | 13,5 % | Inés Ferrer | −15 % |
| B-02 | Llamadas evitadas | % de turnos sacados en línea | 0 % | 40 % desde el año 2 | Inés Ferrer | −15 % |
| DB-01 | Dos puestos del call center se reasignan a recepción | puestos reasignados | 0 | 2 | Inés Ferrer | — |

## 9. Evaluación de la inversión
Opción 2: VAN USD 272.569, TIR 54,3 %, repago 1,78 años (r = 10 %, 5 años; inversion.py). Se recalcula con el presupuesto de la iniciación (paso 9).
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 2 bloqueo(s) · 4 condición(es) · 3 aviso(s)
  BLOQUEO   P-01 falta el artefacto pid (o su archivo)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  condición P-05 junta incompleta: falta usuario_senior
  condición P-05 junta incompleta: falta proveedor_senior
  condición P-06 sin plan de proyecto registrado (o incluido en el PID)
  condición P-11 supuestos críticos sin validar: S-003, S-006 (la junta invierte sobre hipótesis; acordar experimento, criterio y fecha o aceptarlos explícitamente con una decisión de la junta)
  aviso     P-04 sin enfoque de beneficios (cómo, cuándo y quién mide cada beneficio, incluso después del proyecto)
  aviso     P-09 registro de interesados vacío: sin matriz poder/interés (pm-interesados)
  aviso     P-10 sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ (pm-caso-de-negocio, templates/enfoque-beneficios.md → gestion/00-direccion/enfoque-beneficios.md)
# Enfoque de gestión de beneficios (v0.9)
| Beneficio | Medida | Línea base | Meta | Dueña | Mediciones |
|---|---|---|---|---|---|
| B-01 turnos recuperados | ausentismo mensual (agenda clínica) | 18 % | 13,5 % | Inés Ferrer | fin de la etapa 2; 6 y 12 meses después del cierre |
| B-02 llamadas evitadas | % de turnos sacados en línea; llamadas atendidas | 0 % | 40 % desde el año 2 | Inés Ferrer | fin de la etapa 3; 6 y 12 meses después del cierre |
| DB-01 reasignación | puestos reasignados | 0 | 2 | Inés Ferrer | al cierre |
Indicador adelantado: adopción por franja de edad (lección L-001). Las revisiones posteriores al cierre las ejecuta y
financia la red (usuaria sénior). Tolerancia: −15 % sobre la meta.
```

## Paso 8 · Descripción del producto del proyecto y PBS/WBS por productos
```
$ (pm-planificacion-por-productos, templates/descripcion-producto-proyecto.md → gestion/02-planificacion/descripcion-producto-proyecto.md)
# Descripción del producto del proyecto · Servicio de turnos sin llamada (v0.9)
1. Propósito: que el paciente saque, confirme y cancele turnos sin llamar, y que la red recupere los turnos que hoy se pierden.
2. Productos mayores: recordatorios y confirmación · turnos en línea · integración con la agenda clínica · capacitación de recepción y call center.
4. Expectativas de calidad: el turno se libera al cancelar; nadie queda sin canal (teléfono y presencial se mantienen).
5. Criterios de aceptación priorizados: Must REQ-001, 003, 004, 006 · Should REQ-002, 005, 007.
6. Tolerancias de calidad: REQ-006 respuesta < 2 s; accesibilidad WCAG 2.1 AA sin fallas graves.
7. Aceptación: usuaria sénior Inés Ferrer por release; aseguramiento Valeria Santos revisa la evidencia.
```

```
$ python3 $EST/wbs.py gestion/02-planificacion/wbs.csv --titulo "Turnos en línea" --mermaid gestion/02-planificacion/visuales/wbs.md
Turnos en línea: 12 elementos, 7 hojas · esfuerzo 2180 h · costo 142,800
1 Gestión del proyecto [producto] 320 h · 19,200 · Pablo Rinaldi
  1.1 Gestión de etapas [paquete] 320 h · 19,200 · Pablo Rinaldi
2 Recordatorios y confirmación [producto] 360 h · 21,600 · Inés Ferrer
  2.1 Plataforma de mensajería y plantillas [paquete] 160 h · 9,600 · Nicolás Pereyra
  2.2 Confirmación y liberación de turnos [paquete] 200 h · 12,000 · Nicolás Pereyra
3 Turnos en línea [producto] 900 h · 66,000 · Inés Ferrer
  3.1 Portal web y app de turnos (incluye diseño UX externo 12.000) [paquete] 900 h · 66,000 · Nicolás Pereyra
4 Integración con la agenda clínica [producto] 480 h · 28,800 · Tomás Aguirre
  4.1 Adaptador de la interfaz de la agenda [paquete] 480 h · 28,800 · Tomás Aguirre
5 Transición [producto] 120 h · 7,200 · Inés Ferrer
  5.1 Capacitación de recepción y call center [paquete] 120 h · 7,200 · Inés Ferrer
  5.2 Puesta en producción [hito] 0 h · 0 · Inés Ferrer
Mermaid escrito en gestion/02-planificacion/visuales/wbs.md
```

## Paso 9 · Riesgos con EMV, presupuesto con reservas (sin doble conteo) y presupuestos de la junta
```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2027-01-11" --campo "autor=Pablo Rinaldi" --campo "estado=en-seguimiento" --campo "fecha_revision=2027-01-29" --campo "categoria=externo" --campo "causa=La agenda clínica del proveedor no tiene interfaz documentada (L-002, S-003)" --campo "evento=La integración en tiempo real se atrasa" --campo "efecto=Atraso del release de turnos en línea (WBS 4.1 y 3.1)" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=4" --campo "impacto_monetario=30000" --campo "proximidad=corto-plazo" --campo "respuesta=reducir" --campo "acciones=prueba técnica en el entorno del proveedor (S-003) y adaptador detrás de una interfaz propia · costo USD 0 (dentro de la etapa 1)" --campo "probabilidad_residual=2" --campo "impacto_residual=4" --campo "propietario=Tomás Aguirre" --campo "ejecutor=Nicolás Pereyra" --campo "disparador=prueba técnica sin 50 de 50 reservas"
R-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2027-01-11" --campo "autor=Pablo Rinaldi" --campo "estado=en-seguimiento" --campo "fecha_revision=2027-01-29" --campo "categoria=organizacional" --campo "causa=Pacientes mayores de 65 con poca comodidad digital (L-001)" --campo "evento=La adopción en línea queda bajo el 40 % (S-001)" --campo "efecto=B-02 menor que lo previsto" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=3" --campo "impacto_monetario=12000" --campo "proximidad=mediano-plazo" --campo "respuesta=reducir" --campo "acciones=canal asistido en recepción y llamada de confirmación para mayores de 65 · costo USD 4.000" --campo "probabilidad_residual=2" --campo "impacto_residual=3" --campo "propietario=Inés Ferrer" --campo "ejecutor=Marta Gil" --campo "disparador=adopción por franja de edad < 15 % al mes 3 del release 2"
R-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2027-01-11" --campo "autor=Pablo Rinaldi" --campo "estado=en-seguimiento" --campo "fecha_revision=2027-01-29" --campo "categoria=externo" --campo "causa=No hay dictamen legal sobre el consentimiento para recordatorios por mensajería (S-006)" --campo "evento=La asesoría legal exige un consentimiento explícito separado" --campo "efecto=Rediseño del alta del turno y menos pacientes con recordatorio (WBS 2.1)" --campo "tipo=amenaza" --campo "probabilidad=2" --campo "impacto=3" --campo "impacto_monetario=10000" --campo "proximidad=corto-plazo" --campo "respuesta=contingencia" --campo "acciones=si el dictamen lo exige: consentimiento explícito al pedir el turno y recordatorio por correo para quien no consienta · costo USD 0" --campo "probabilidad_residual=2" --campo "impacto_residual=2" --campo "propietario=Carmen Olivera" --campo "ejecutor=Pablo Rinaldi" --campo "disparador=dictamen de la asesoría legal (2027-01-29)"
R-003
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion vincular entregables C5 --refs R-001
wardley-entregables.json C5: refs = S-003, R-001
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion controles
0 aviso(s) de la familia MAP
```

```
$ (pm-costos-presupuesto: reservas sin doble conteo, SPEC §1.10.6 y references/guia.md §3)
Paquetes base (Σ WBS, wbs.py)                           142.800
Contingencia = Σ EMV (15.000 + 6.000 + 3.000 = 24.000) + respuestas (4.000)      28.000
BAC = paquetes base + contingencia                       170.800
Reserva de gestión = 5 % del BAC (la libera solo la junta)       8.540
Presupuesto autorizado = BAC + reserva de gestión        179.340
Presupuesto de cambio (aparte; autoridad de cambio, tope 3.000 por cambio)      10.000
Clase de exactitud: presupuestaria (−10/+25 %). El orden de magnitud de la puesta en marcha (180.000, −25/+75 % = 135.000–315.000) contiene a 189.340.
```

```
$ (pm-costos-presupuesto, templates/presupuesto.md → gestion/02-planificacion/presupuesto.md)
# Presupuesto · Turnos en línea (v0.9)
| Componente | USD | Criterio |
|---|---|---|
| Paquetes base | 142.800 | Σ WBS (wbs.py), tarifa USD 60/h; UX externo 12.000 en 3.1 |
| Contingencia | 28.000 | Σ EMV de R-001, R-002, R-003 (24.000) + costo de respuestas (4.000) |
| **BAC** | **170.800** | paquetes base + contingencia |
| Reserva de gestión | 8.540 | 5 % del BAC; fuera del BAC; la libera la junta |
| **Presupuesto autorizado** | **179.340** | BAC + reserva de gestión |
| Presupuesto de cambio | 10.000 | aparte; autoridad de cambio con tope de 3.000 por cambio |
```

```
$ python3 $EST/estado.py --proyecto gestion presupuesto cambio=10000 riesgo=28000 gestion=8540 limite_autoridad_cambio=3000 --por "Ejecutiva: Carmen Olivera" --fecha 2027-01-12
ok
```

```
$ (pm-caso-de-negocio → gestion/00-direccion/inversion/flujos-opcion-2-presupuesto.csv)
opcion,concepto,tipo,0,1,2,3,4,5
2 · Con el orden de magnitud,Inversión,inversion,-180000,,,,,
2 · Con el orden de magnitud,Turnos recuperados (B-01),beneficio,,54000,54000,54000,54000,54000
2 · Con el orden de magnitud,Llamadas evitadas (B-02),beneficio,,57600,115200,115200,115200,115200
2 · Con el orden de magnitud,Operación,costo,,-36000,-36000,-36000,-36000,-36000
2 · Con el presupuesto,Inversión,inversion,-189340,,,,,
2 · Con el presupuesto,Turnos recuperados (B-01),beneficio,,54000,54000,54000,54000,54000
2 · Con el presupuesto,Llamadas evitadas (B-02),beneficio,,57600,115200,115200,115200,115200
2 · Con el presupuesto,Operación,costo,,-36000,-36000,-36000,-36000,-36000
```

```
$ python3 $PLUGIN/skills/pm-caso-de-negocio/scripts/inversion.py gestion/00-direccion/inversion/flujos-opcion-2-presupuesto.csv --tasa 0.10
Evaluación de la inversión · tasa 10,0 % por período · base: 2 · Con el orden de magnitud
Fórmulas: VAN = Σ F_t/(1+r)^t, t = 0…n · TIR: VAN(TIR) = 0 · repago interpolado en el período en que el acumulado llega a 0

Opción                                      VAN       TIR   Repago Rep. desc.  VAN vs base
2 · Con el orden de magnitud            272.569    54,3 %     1,78       2,01            0
2 · Con el presupuesto                  263.229    51,1 %     1,85       2,11       -9.340

2 · Con el orden de magnitud · flujos netos: 0: -180.000 | 1: 75.600 | 2: 133.200 | 3: 133.200 | 4: 133.200 | 5: 133.200
  Sensibilidad a la tasa: VAN 298.496 con 8,0 % · 248.728 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Llamadas evitadas (B-02)  [beneficio] VAN 195.702 … 349.436 · 29,1 % del valor estimado
    Turnos recuperados (B-01) [beneficio] VAN 231.629 … 313.510 · ningún valor positivo del concepto lo lleva a 0
    Inversión                 [inversion] VAN 308.569 … 236.569 · 251,4 % del valor estimado
    Operación                 [costo] VAN 299.863 … 245.275 · 299,7 % del valor estimado

2 · Con el presupuesto · flujos netos: 0: -189.340 | 1: 75.600 | 2: 133.200 | 3: 133.200 | 4: 133.200 | 5: 133.200
  Sensibilidad a la tasa: VAN 289.156 con 8,0 % · 239.388 con 12,0 %
  Sensibilidad por concepto (±20 %), de mayor a menor impacto · punto de equilibrio (VAN = 0):
    Llamadas evitadas (B-02)  [beneficio] VAN 186.362 … 340.096 · 31,5 % del valor estimado
    Turnos recuperados (B-01) [beneficio] VAN 222.289 … 304.170 · ningún valor positivo del concepto lo lleva a 0
    Inversión                 [inversion] VAN 301.097 … 225.361 · 239,0 % del valor estimado
    Operación                 [costo] VAN 290.523 … 235.935 · 292,9 % del valor estimado
```

```
$ (lectura de pm-caso-de-negocio, de inversion.py --json)
Inversión 189.340 = presupuesto autorizado 179.340 + presupuesto de cambio 10.000 (orden de magnitud: 180.000) · VAN USD 263.229 (-9.340) · TIR 51,1 % · repago 1,85 años · adopción estable de equilibrio 12,6 % (con el orden de magnitud: 11,6 %)
```

## Paso 10 · Organización, interesados y RACI (breve)
```
$ python3 $EST/estado.py --proyecto gestion rol usuario_senior="Inés Ferrer" proveedor_senior="Tomás Aguirre" product_owner="Inés Ferrer" autoridad_cambio="Inés Ferrer" aseguramiento="Valeria Santos" jefes_equipo="Nicolás Pereyra"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Carmen Olivera" --campo "rol_organizacion=Gerenta general · ejecutiva" --campo "poder=alto" --campo "interes=alto" --campo "actitud=lider" --campo "nivel_compromiso_actual=lider" --campo "nivel_compromiso_deseado=lider" --campo "confidencial=no"
ST-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Inés Ferrer" --campo "rol_organizacion=Jefa de atención al paciente · usuaria sénior" --campo "poder=alto" --campo "interes=alto" --campo "actitud=partidario" --campo "nivel_compromiso_actual=partidario" --campo "nivel_compromiso_deseado=lider" --campo "confidencial=no"
ST-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Tomás Aguirre" --campo "rol_organizacion=Jefe de TI · proveedor sénior" --campo "poder=alto" --campo "interes=medio" --campo "actitud=partidario" --campo "nivel_compromiso_actual=partidario" --campo "nivel_compromiso_deseado=partidario" --campo "confidencial=no"
ST-003
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Dirección médica" --campo "rol_organizacion=Libera las agendas (S-004)" --campo "poder=alto" --campo "interes=medio" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "confidencial=no"
ST-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Recepción y call center" --campo "rol_organizacion=Supervisa Marta Gil" --campo "poder=medio" --campo "interes=alto" --campo "actitud=resistente" --campo "nivel_compromiso_actual=resistente" --campo "nivel_compromiso_deseado=partidario" --campo "confidencial=no"
ST-005
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Comisión de usuarios" --campo "rol_organizacion=Representa a los pacientes" --campo "poder=medio" --campo "interes=alto" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "confidencial=no"
ST-006
```

```
$ python3 $EST/registro.py --proyecto gestion agregar stakeholders --campo "nombre=Proveedor de la agenda clínica" --campo "rol_organizacion=Dueño de la interfaz (S-003)" --campo "poder=alto" --campo "interes=medio" --campo "actitud=neutral" --campo "nivel_compromiso_actual=neutral" --campo "nivel_compromiso_deseado=partidario" --campo "confidencial=no"
ST-007
```

```
$ (pm-interesados registra la matriz RACI en raci.csv con registro.py agregar raci --campo elemento=<código WBS o id de requisito> …: 18 filas en 4 elementos, una A por elemento)

```

```
$ python3 $IN --proyecto gestion --medio bajo matriz
Gestionar de cerca (2): ST-001 Carmen Olivera, ST-002 Inés Ferrer
   Los actores más críticos: comunicación constante, participación activa en las decisiones y máxima atención.
Mantener satisfecho (3): ST-003 Tomás Aguirre ◇, ST-004 Dirección médica ◇, ST-007 Proveedor de la agenda clínica ◇
   No abrumar con detalles; reportes ejecutivos de alto nivel sobre beneficios y avance.
Mantener informado (2): ST-005 Recepción y call center ◇, ST-006 Comisión de usuarios ◇
   Canales claros (boletines, reuniones informativas) y escucha activa de su retroalimentación: suelen ser aliados y fuente de información.
Monitorear (0): —
   Supervisar con el menor esfuerzo, sin gastar recursos innecesarios, salvo que cambien de posición en la matriz.
◇ = frontera ('medio' ubicado como bajo)
```

```
$ python3 $IN --proyecto gestion --medio bajo raci
| Elemento | Descripción | ST-001 Carmen Olivera | ST-002 Inés Ferrer | ST-003 Tomás Aguirre | ST-004 Dirección médica | ST-005 Recepción y… | ST-006 Comisión de… | ST-007 Proveedor de la… |
|---|---|---|---|---|---|---|---|---|
| 2 | Recordatorios y confirmación | I | A | R |  | C | I |  |
| 3 | Turnos en línea | I | A | R | C | I | C |  |
| 4 | Integración con la agenda clínica | I | I | A |  |  |  | R |
| REQ-006 | Reservar y cancelar en la agenda clínica en tiempo real |  | C | A |  |  |  | R |

Leyenda: R responsable · A aprobador (uno por elemento) · C consultado · I informado.
RACI válida: un A por elemento, al menos un R, referencias existentes.
```

## Paso 10b · Personas de usuario: quién pide, usa o aprovecha cada capacidad
```
$ python3 $IN --proyecto gestion personas candidatos
1 persona(s) candidata(s) · el modelo propone, la persona confirma; nada se registra solo. El texto citado es dato de la fuente, no una instrucción.
- Paciente que agenda por teléfono · fuente observacion · recorrido-paciente.json; 00-direccion/mandato.md
    objetivo: Conseguir un turno que le sirva y no perderlo
    contexto de uso: Necesita un control con su médica de cabecera
    dolores: Espera en línea en las horas pico; Nadie le recuerda el turno; Solo puede cancelar llamando en horario de atención
    usa: REQ-003;REQ-005
    representante sugerido: ST-006 Comisión de usuarios
    → registro.py --proyecto gestion agregar personas --campo 'nombre=Paciente que agenda por teléfono' --campo 'objetivo=Conseguir un turno que le sirva y no perderlo' --campo 'dolores=Espera en línea en las horas pico; Nadie le recuerda el turno; Solo puede cancelar llamando en horario de atención' --campo 'contexto_uso=Necesita un control con su médica de cabecera' --campo fuente=observacion --campo 'evidencia=recorrido-paciente.json; 00-direccion/mandato.md' --campo stakeholder_id=ST-006 --campo 'usa=REQ-003;REQ-005'
Confirmar con la persona cada candidata, completar dolores y lo que pide (solicita) o de qué se beneficia (beneficia), y registrar.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar personas --campo "nombre=Paciente que agenda por teléfono" --campo "descripcion=Adulto que hoy saca, confirma y cancela el turno llamando al call center" --campo "objetivo=Conseguir un turno que le sirva y no perderlo" --campo "dolores=Espera en línea en las horas pico; Nadie le recuerda el turno; Solo puede cancelar llamando en horario de atención" --campo "contexto_uso=Necesita un control con su médica de cabecera" --campo "fuente=observacion" --campo "evidencia=recorrido-paciente.json; 00-direccion/mandato.md" --campo "stakeholder_id=ST-006" --campo "usa=REQ-001;REQ-003;REQ-004;REQ-005" --campo "beneficios=B-01;B-02"
PU-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar personas --campo "nombre=Recepcionista del call center" --campo "descripcion=Atiende el teléfono en las horas pico y libera a mano los turnos que se cancelan" --campo "objetivo=Atender a quien llama sin colas y no perder los turnos que se liberan" --campo "dolores=Colas en las horas pico; libera los turnos cancelados al día siguiente, a mano" --campo "contexto_uso=Puesto de recepción y call center, en horario de atención" --campo "fuente=supuesto" --campo "evidencia=backstage de P1 y P5 en recorrido-paciente.json; a validar con entrevistas en recepción" --campo "stakeholder_id=ST-005" --campo "solicita=REQ-003" --campo "usa=REQ-002" --campo "beneficia=REQ-004" --campo "beneficios=B-02;DB-01"
PU-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar personas --campo "nombre=Paciente mayor de 65" --campo "descripcion=Prefiere el teléfono; usa el celular para mensajes, no para aplicaciones" --campo "objetivo=No perder el turno sin tener que usar una aplicación" --campo "dolores=No usa aplicaciones; necesita que alguien lo atienda" --campo "contexto_uso=Recibe mensajes en el celular; agenda por teléfono o en recepción" --campo "fuente=documento" --campo "evidencia=L-001 (App de resultados de laboratorio, 2024: 11 % de uso en mayores de 65)" --campo "stakeholder_id=ST-006" --campo "solicita=REQ-007" --campo "usa=REQ-001;REQ-003" --campo "beneficios=B-01"
PU-003
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-12
Sanidad de 'Turnos en línea · Policlínicas Altamar' (inicio/IP): 0 ERROR · 1 AVISO · 0 INFO
  AVISO STK-13 REQ-006 (requisito Must) sin persona que lo pida, lo use o se beneficie: Reservar y cancelar en la agenda clínica en tiempo real
        → Vincular el requisito o la épica Must a la persona que lo pide, lo usa o se beneficia (registro.py actualizar personas PU-… --campo usa=…) o revisar su prioridad.
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar personas PU-001 --campo "beneficia=REQ-006"
ok
```

```
$ python3 $IN --proyecto gestion personas mapa
| Capacidad | Título | MoSCoW | PU-001 Paciente que… | PU-002 Recepcionista… | PU-003 Paciente mayor… |
|---|---|---|---|---|---|
| REQ-001 | Enviar un recordatorio 48 h antes del turno por m… | Must | U |  | U |
| REQ-003 | Confirmar o cancelar desde el recordatorio y libe… | Must | U | S | U |
| REQ-004 | Sacar turno en línea por especialidad y policlíni… | Must | U | B |  |
| REQ-006 | Reservar y cancelar en la agenda clínica en tiemp… | Must | B |  |  |
| REQ-002 | Plantillas de recordatorio por especialidad | Should |  | U |  |
| REQ-005 | Reprogramar o cancelar en línea | Should | U |  |  |
| REQ-007 | Uso accesible para pacientes mayores de 65 (WCAG… | Should |  |  | S |
S solicitante · U usuario · B beneficiario
```

```
$ python3 $IN --proyecto gestion personas priorizacion
| Persona | Representante | Must | Should | Could | Won't | Sin prioridad | S | U | B | Beneficios |
|---|---|---|---|---|---|---|---|---|---|---|
| PU-001 Paciente que agenda por… | ST-006 | 4 | 1 | 0 | 0 | 0 | 0 | 4 | 1 | B-01, B-02 |
| PU-002 Recepcionista del call… | ST-005 | 2 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | B-02, DB-01 |
| PU-003 Paciente mayor de 65 | ST-006 | 2 | 1 | 0 | 0 | 0 | 1 | 2 | 0 | B-01 |
7 capacidad(es) mapeadas · Must sin persona: ninguno
```

## Paso 11 · Enfoques de gestión adaptados al contexto (tailoring)
```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2027-01-12" --campo "decision=Nivel de formalidad de los enfoques: una página cada uno (riesgo, calidad, issues y cambios, comunicación); datos digitales dentro de calidad (datos de salud); sostenibilidad dentro del business case" --campo "decidido_por=Gestor: Pablo Rinaldi" --campo "nivel=gestor"
D-008
```

```
$ (pm-enfoques-gestion, versión de una página → gestion/02-planificacion/enfoques/enfoque-riesgo.md)
# Enfoque de riesgos (una página)
Escala 1–5, alto ≥ 15. Revisión en cada planificación de sprint. Contingencia 28.000 (EMV + respuestas); la reserva de gestión (8.540) la libera solo la junta. Supuestos que no se validan a tiempo pasan a riesgo (S-006 → R-003).
```

```
$ (pm-enfoques-gestion, versión de una página → gestion/02-planificacion/enfoques/enfoque-calidad.md)
# Enfoque de calidad (una página)
DoD por historia; aceptación por release (Inés Ferrer); aseguramiento independiente (Valeria Santos). Datos de salud: mínimo necesario, consentimiento registrado, sin datos clínicos en los mensajes. REQ-006 con prueba de respuesta; REQ-007 con auditoría WCAG 2.1 AA.
```

```
$ (pm-enfoques-gestion, versión de una página → gestion/02-planificacion/enfoques/enfoque-issues-cambios.md)
# Enfoque de issues y cambios (una página)
Cinco tipos de issue. Autoridad de cambio: Inés Ferrer, hasta USD 3.000 por cambio y 10.000 en total (presupuesto de cambio); por encima, la junta. El PO intercambia Should/Could dentro de la tolerancia de alcance sin solicitud de cambio.
```

```
$ (pm-enfoques-gestion, versión de una página → gestion/02-planificacion/enfoques/enfoque-comunicacion.md)
# Enfoque de comunicación (una página)
Highlight quincenal a la junta con ausentismo y adopción; demo al final de cada sprint con recepción y la comisión de usuarios; regla extraordinaria: todo pronóstico fuera de tolerancia se informa en 48 h.
```

## Paso 12 · Bloque C: el mismo proyecto, tres diseños (interno pequeño, regulado, producto digital ágil)
```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Turnos en línea · diseño Interno pequeño" --idioma es --enfoque predictivo --ejecutivo "Carmen Olivera" --gestor "Pablo Rinaldi" --fecha 2027-01-12
Proyecto creado en gestion · enfoque de entrega: predictivo · siguiente: estado.py siguiente
```

```
$ (diseño 1 · Interno pequeño: 7 artefactos registrados con estado.py artefacto y 2 tolerancias de proyecto)
perfil mínimo; brief con business case fusionado; acta + PID breve; un enfoque de una página (riesgos, issues y cambios); highlight mensual
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Turnos en línea · diseño Interno pequeño · pre-proyecto/SU · etapa 0 pre-proyecto (2027-01-12 → ) · enfoque predictivo · idioma es
Autorizado: no
Roles: ejecutivo=Carmen Olivera; gestor_proyecto=Pablo Rinaldi
Tolerancias: proyecto: tiempo=±2 semanas, costo=±15 % | etapa: 
Artefactos: 7 (0 aprobados)
Próxima puerta: autorizar-inicio · 1 bloqueo(s) · 0 condición(es) (detalle: puertas.py verificar autorizar-inicio)
Fase: pre-proyecto · Proceso: SU · Etapa 0: pre-proyecto · Enfoque: predictivo
Puesta en marcha (SU): mandato → lecciones previas → brief (con caso de negocio esquemático y enfoque del proyecto) → junta y roles → plan de la etapa de iniciación. Agentes: pm-inicio. Puerta: autorizar-inicio (pm-director).
```

```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Turnos en línea · diseño Regulado (datos de salud)" --idioma es --enfoque predictivo --ejecutivo "Carmen Olivera" --gestor "Pablo Rinaldi" --fecha 2027-01-12
Proyecto creado en gestion · enfoque de entrega: predictivo · siguiente: estado.py siguiente
```

```
$ (diseño 2 · Regulado (datos de salud): 16 artefactos registrados con estado.py artefacto y 7 tolerancias de proyecto)
perfil completo; PID índice; aseguramiento independiente; auditoría de privacidad como revisión de calidad; highlight quincenal; cambios solo con la junta
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Turnos en línea · diseño Regulado (datos de salud) · pre-proyecto/SU · etapa 0 pre-proyecto (2027-01-12 → ) · enfoque predictivo · idioma es
Autorizado: no
Roles: ejecutivo=Carmen Olivera; gestor_proyecto=Pablo Rinaldi
Tolerancias: proyecto: tiempo=±2 semanas, costo=±5 %, alcance=sin tolerancia, calidad=cero no conformidades de privacidad, beneficios=-10 %, riesgo=ningún riesgo alto sin respuesta, sostenibilidad=-10 % | etapa: 
Artefactos: 16 (0 aprobados)
Próxima puerta: autorizar-inicio · 1 bloqueo(s) · 0 condición(es) (detalle: puertas.py verificar autorizar-inicio)
Fase: pre-proyecto · Proceso: SU · Etapa 0: pre-proyecto · Enfoque: predictivo
Puesta en marcha (SU): mandato → lecciones previas → brief (con caso de negocio esquemático y enfoque del proyecto) → junta y roles → plan de la etapa de iniciación. Agentes: pm-inicio. Puerta: autorizar-inicio (pm-director).
```

```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Turnos en línea · diseño Producto digital ágil" --idioma es --enfoque agil --ejecutivo "Carmen Olivera" --gestor "Pablo Rinaldi" --fecha 2027-01-12
Proyecto creado en gestion · enfoque de entrega: agil · siguiente: estado.py siguiente
```

```
$ (diseño 3 · Producto digital ágil: 12 artefactos registrados con estado.py artefacto y 3 tolerancias de proyecto)
perfil ágil mínimo; PID compacto; enfoques de una página con DoD/DoR; el PO intercambia alcance; demo y burn-up por sprint
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Turnos en línea · diseño Producto digital ágil · pre-proyecto/SU · etapa 0 pre-proyecto (2027-01-12 → ) · enfoque agil · idioma es
Autorizado: no
Roles: ejecutivo=Carmen Olivera; gestor_proyecto=Pablo Rinaldi
Tolerancias: proyecto: tiempo=fecha fija (0 semanas), costo=±5 %, alcance=Must intocables; Could negociables | etapa: 
Artefactos: 12 (0 aprobados)
Próxima puerta: autorizar-inicio · 1 bloqueo(s) · 0 condición(es) (detalle: puertas.py verificar autorizar-inicio)
Fase: pre-proyecto · Proceso: SU · Etapa 0: pre-proyecto · Enfoque: agil
Puesta en marcha (SU): mandato → lecciones previas → brief (con caso de negocio esquemático y enfoque del proyecto) → junta y roles → plan de la etapa de iniciación. Ágil/híbrido: brief ligero + visión y backlog inicial de épicas. Agentes: pm-inicio. Puerta: autorizar-inicio (pm-director).
```

```
$ (bloque C: medidas leídas de los tres estado.json)
diseño                       artefactos  enfoques  etapas  tolerancias  enfoque de entrega
Interno pequeño                       7         1       2            2  predictivo
Regulado (datos de salud)            16         7       4            7  predictivo
Producto digital ágil                12         5       3            3  agil
```

## Paso 13 · PID con adaptación, sanidad y puerta autorizar-proyecto: P-11 y su resolución
```
$ (pm-acta-constitucion, templates/pid.md (§8 adaptación) → gestion/00-direccion/pid.md)
# PID · Turnos en línea · Policlínicas Altamar (v0.9)
§1–§6: definición, enfoque híbrido, business case v0.9, estructura (ejecutiva Carmen Olivera; usuaria sénior Inés Ferrer;
proveedor sénior Tomás Aguirre; aseguramiento Valeria Santos), enfoques de una página.
## 7. Controles
Etapas: 1 iniciación · 2 recordatorios · 3 turnos en línea. Tolerancias de proyecto: tiempo ±4 semanas, costo ±10 %,
alcance Must sin tolerancia, beneficios −15 %. Presupuesto autorizado 179.340 (BAC 170.800 + reserva de gestión 8.540);
presupuesto de cambio 10.000 con tope de 3.000 por cambio. Highlight quincenal; sanidad en cada highlight.
## 8. Adaptación (tailoring)
| Qué | Cómo se adaptó | Por qué |
|---|---|---|
| Ciclo de vida | etapas PRINCE2; sprints de 14 días como paquetes de trabajo en las etapas 2 y 3 | entregables con vías distintas (paso 5) |
| Enfoques | una página cada uno; datos digitales dentro de calidad | proyecto mediano, un solo equipo |
| Plan de proyecto | dentro del PID (roadmap + WBS + presupuesto) | evitar duplicar |
| Roles | Inés Ferrer: usuaria sénior, product owner y autoridad de cambio | una sola voz del negocio |
| Validación | supuestos críticos con experimento, criterio y fecha (supuestos.csv); SUP-01…03 y P-11 | idea con incertidumbre alta |
| Puerta de la etapa 3 | condicionada a la adopción medida en el release 1 | VAN sensible a la adopción |
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-14
Sanidad de 'Turnos en línea · Policlínicas Altamar' (inicio/IP): 0 ERROR · 0 AVISO · 0 INFO
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 1 condición(es) · 0 aviso(s)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  condición P-11 supuestos críticos sin validar: S-003, S-006 (la junta invierte sobre hipótesis; acordar experimento, criterio y fecha o aceptarlos explícitamente con una decisión de la junta)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-003 --campo "validado=si" --campo "estado=validado" --campo "certeza=alta" --campo "fecha_validacion=2027-01-14" --campo "evidencia=prueba técnica: 50 de 50 reservas y cancelaciones sin intervención; respuesta media 1,4 s"
ok
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2027-01-15" --campo "decision=La junta acepta S-006 sin validar: invierte sin el dictamen legal y cubre su efecto con el riesgo R-003 y su contingencia; el dictamen sigue como experimento y es condición antes del release de recordatorios" --campo "decidido_por=Ejecutiva: Carmen Olivera" --campo "nivel=junta" --campo "revisar_en=2027-01-29" --campo "artefactos_afectados=03-control/registros/supuestos.csv; 03-control/registros/riesgos.csv"
D-009
```

```
$ python3 $EST/registro.py --proyecto gestion actualizar supuestos S-006 --campo "notas=aceptado sin validar por la junta el 2027-01-15 (D-009); efecto cubierto por R-003; el dictamen del 2027-01-29 lo valida o lo invalida"
ok
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 1 bloqueo(s) · 0 condición(es) · 1 aviso(s)
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  aviso     P-11 supuestos críticos sin validar aceptados por decisión de la junta: S-006 (D-009) (seguir su validación; la sanidad SUP sigue mostrándolos)
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

```
$ python3 $EST/puertas.py --proyecto gestion lista autorizar-proyecto --fecha 2027-01-15
Lista creada: 00-direccion/decisiones/2027-01-15-verificacion-autorizar-proyecto.md (1 hallazgos automáticos, 6 ítems para la junta)
```

```
$ python3 $EST/puertas.py --proyecto gestion confirmar autorizar-proyecto --por "Ejecutiva: Carmen Olivera" --fecha 2027-01-15
Lista 00-direccion/decisiones/2027-01-15-verificacion-autorizar-proyecto.md confirmada por Ejecutiva: Carmen Olivera
```

```
$ python3 $EST/estado.py --proyecto gestion puerta autorizar-proyecto --decision aprobado --por "Ejecutiva: Carmen Olivera" --fecha 2027-01-15 
Aviso: supuestos críticos sin validar aceptados por decisión de la junta: S-006 (D-009) (seguir su validación; la sanidad SUP sigue mostrándolos)
ok
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director). Proyecto ya autorizado: falta autorizar-etapa para la primera etapa de entrega.
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar business-case --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/business-case-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-beneficios --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/enfoque-beneficios-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar pid --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/pid-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar presupuesto --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/presupuesto-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar descripcion-producto-proyecto --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/descripcion-producto-proyecto-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-riesgo --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/enfoque-riesgo-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-calidad --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/enfoque-calidad-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-issues-cambios --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/enfoque-issues-cambios-v1.0.md
ok
```

```
$ python3 $EST/estado.py --proyecto gestion aprobar enfoque-comunicacion --por "Ejecutiva: Carmen Olivera" --version 1.0 --fecha 2027-01-15
Copia congelada / frozen copy: 00-direccion/historial/enfoque-comunicacion-v1.0.md
ok
```

```
$ (pm-director aprueba con estado.py aprobar … --version 1.0 --fecha 2027-01-15: business case, enfoque de beneficios, PID, presupuesto, descripción del producto y los 4 enfoques)
9 copias congeladas en 00-direccion/historial/ (…-v1.0.md)
```

```
$ python3 $EST/estado.py --proyecto gestion resumen
Turnos en línea · Policlínicas Altamar · inicio/IP · etapa 1 Iniciación (2026-12-11 → 2027-01-15) · enfoque hibrido · idioma es
Autorizado: sí
Roles: ejecutivo=Carmen Olivera; usuario_senior=Inés Ferrer; proveedor_senior=Tomás Aguirre; gestor_proyecto=Pablo Rinaldi; aseguramiento=Valeria Santos; autoridad_cambio=Inés Ferrer; product_owner=Inés Ferrer; jefes_equipo=Nicolás Pereyra
Tolerancias: proyecto: tiempo=±4 semanas, costo=±10 %, alcance=Must sin tolerancia, beneficios=-15 %, riesgo=ningún riesgo alto sin respuesta | etapa: 
Presupuestos: cambio=10000, riesgo=28000, gestion=8540, limite_autoridad_cambio=3000
Artefactos: 21 (11 aprobados)
Última puerta: autorizar-proyecto · aprobado · 2027-01-15 · Ejecutiva: Carmen Olivera
Próxima puerta: autorizar-etapa · 2 bloqueo(s) · 0 condición(es) (detalle: puertas.py verificar autorizar-etapa)
Fase: inicio · Proceso: IP · Etapa 1: Iniciación · Enfoque: hibrido
Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. Híbrido: definir qué productos van con paquetes iterativos y su release plan. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director). Proyecto ya autorizado: falta autorizar-etapa para la primera etapa de entrega.
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-01-15
Sanidad de 'Turnos en línea · Policlínicas Altamar' (inicio/IP): 0 ERROR · 0 AVISO · 0 INFO
```

## Paso 14 · Tablero de una página y seguimiento después de la puerta
```
$ (puertas.py verificar autorizar-proyecto --json → hallazgos con id P-11)
aviso P-11 supuestos críticos sin validar aceptados por decisión de la junta: S-006 (D-009) (seguir su validación; la sanidad SUP sigue mostrándolos)
```

```
$ (insumos del tablero: supuestos.csv, estado.json, la verificación con --json y los cálculos de los pasos 5 y 9)
supuestos críticos 4: validados S-001, S-003 · invalidado y ajustado S-002 · aceptados por la junta S-006 (D-009) · puerta autorizar-proyecto aprobado 2027-01-15 · VAN 263.229 · TIR 51,1 % · repago 1,85 · autorizado 179.340
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion tablero
Tablero de mapas: 2 mapa(s) dibujado(s) (wardley-entregables.json, recorrido-paciente.json) · 0 aviso(s) MAP · 9 vínculo(s) citado(s)
Escrito: 02-planificacion/visuales/tablero-mapas.html
```

```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2027-02-01
Sanidad de 'Turnos en línea · Policlínicas Altamar' (inicio/IP): 0 ERROR · 4 AVISO · 0 INFO
  AVISO REG-09 Riesgo R-001 abierto con la revisión vencida (2027-01-29; propietario: Tomás Aguirre).
  AVISO REG-09 Riesgo R-002 abierto con la revisión vencida (2027-01-29; propietario: Inés Ferrer).
  AVISO REG-09 Riesgo R-003 abierto con la revisión vencida (2027-01-29; propietario: Carmen Olivera).
        → Revisarlo con el propietario (pm-riesgos) y actualizar estado, evaluación y fecha_revision (registro.py actualizar riesgos R-… --campo fecha_revision=…).
  AVISO SUP-02 Supuesto S-006 con fecha límite 2027-01-29 vencida y sin validar.
        → Registrar la evidencia y el resultado (validado=si|no) o replanificar con la junta.
```

```
$ python3 $EST/estado.py --proyecto gestion radar --corte 2027-02-01
Radar de atención · Turnos en línea · Policlínicas Altamar (inicio/IP, etapa 1) al 2027-02-01: 1 decidir · 0 escalar · 0 desbloquear · 4 vigilar
Hoy: decidir S-006 · escalar — · desbloquear —.
DECIDIR (1)
  P1 [SUP-02] S-006 · 2027-01-29 · Carmen Olivera — fecha límite vencida sin resultado: seguir, cambiar o detener · «La normativa de protección de datos permite enviar recordat…»
      → pm-mandato-y-brief (experimento y resultado) o pm-caso-de-negocio (efecto en el caso); la junta decide si se acepta sin validar
ESCALAR: nada.
DESBLOQUEAR: nada.
VIGILAR (4)
  P3 [REG-09] R-001 · 2027-01-29 · Tomás Aguirre — revisión del riesgo vencida
      → pm-riesgos: revisarlo con el propietario y actualizar fecha_revision
  P3 [REG-09] R-002 · 2027-01-29 · Inés Ferrer — revisión del riesgo vencida
      → pm-riesgos: revisarlo con el propietario y actualizar fecha_revision
  P3 [REG-09] R-003 · 2027-01-29 · Carmen Olivera — revisión del riesgo vencida
      → pm-riesgos: revisarlo con el propietario y actualizar fecha_revision
  P3 [RAD-07] autorizar-etapa · Pablo Rinaldi — 2 bloqueo(s) de la próxima puerta: E-02, L-01
      → pm-puerta: puertas.py verificar autorizar-etapa
Opciones: generar el highlight del período (pm-progreso-reportes) · escalar una excepción no corresponde: ningún pronóstico fuera de tolerancia ni presupuesto agotado.
Prioridad: 1 hoy (vencido, fuera de tolerancia o presupuesto agotado) · 2 espera una decisión o bloquea · 3 pendiente · 4 vigilar; orden: prioridad, fecha, id.
```

## Paso 15 · Variante a) con BMAD: supuestos, preguntas y requisitos desde los artefactos de descubrimiento
```
$ python3 $EST/nuevo_proyecto.py --ruta gestion --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez" --fecha 2026-10-27
Proyecto creado en gestion · enfoque de entrega: hibrido · siguiente: estado.py siguiente
```

```
$ python3 $BMAD --proyecto gestion inventario
BMAD v6 (soportada) en <repo>
  brief              1 archivo(s) · estado=final · <fecha-hora> · sha 58db1efac463 · _bmad-output/planning-artifacts/briefs/brief-portal-socios-2026-10-17/brief.md
  prd                1 archivo(s) · estado=final · <fecha-hora> · sha bc048f7f59a3 · _bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md
  arquitectura       1 archivo(s) · estado=final · <fecha-hora> · sha 9a0a63b20794 · _bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md
  epicas             1 archivo(s) · estado=final · <fecha-hora> · sha 3ff846d6f8d9 · _bmad-output/planning-artifacts/epics.md
  estado-sprint      1 archivo(s) · estado=- · <fecha-hora> · sha 519bd23ac20a · _bmad-output/implementation-artifacts/sprint-status.yaml
  historias          1 archivo(s) · estado=ready-for-dev · <fecha-hora> · sha 16b91b8717ea · _bmad-output/implementation-artifacts/spec-1-1-alta-y-acceso-del-socio-con-segundo-factor.md
Inventario escrito en gestion/02-planificacion/especificacion/inventario-bmad.json
```

```
$ python3 $BMAD --proyecto gestion requisitos
42 identificadores · {'UJ': 3, 'FR': 12, 'NFR': 6, 'SM': 8, 'AD': 13} → gestion/02-planificacion/especificacion/requisitos-bmad.csv (derivado: no editar)
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
$ python3 $EST/especificacion.py --proyecto gestion resumen
requisitos: 42
historias: 10
por_estado: {'backlog': 9, 'ready-for-dev': 1, 'in-progress': 0, 'review': 0, 'done': 0}
```

```
$ python3 $PLUGIN/skills/pm-riesgos/scripts/riesgos.py --proyecto gestion candidatos --fuentes bmad --fecha 2026-10-28
bmad: 42 candidatos · 3 fuente(s) leída(s)
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
… (32 líneas más)
```

```
$ (candidatos por clase, de riesgos.py candidatos --json)
pregunta: 6 · riesgo: 12 · supuesto: 24 · total 42
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-10-28" --campo "autor=Martín Suárez" --campo "supuesto_o_restriccion=Hay métricas actuales del volumen de consultas y del costo por gestión para fijar la línea base" --campo "tipo=supuesto" --campo "categoria=viabilidad" --campo "criticidad=alta" --campo "certeza=baja" --campo "validado=pendiente" --campo "responsable=Martín Suárez" --campo "notas=origen: BMAD brief.md:26 (CR-01) (riesgos.py candidatos)"
S-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-10-28" --campo "autor=Martín Suárez" --campo "supuesto_o_restriccion=El núcleo operativo ofrece una API o base de lectura utilizable para saldos y préstamos" --campo "tipo=supuesto" --campo "categoria=factibilidad" --campo "criticidad=alta" --campo "certeza=baja" --campo "validado=pendiente" --campo "responsable=Martín Suárez" --campo "notas=origen: BMAD prd.md:64 y prd.md:258 (riesgos.py candidatos)"
S-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-10-28" --campo "autor=Martín Suárez" --campo "supuesto_o_restriccion=El método de autenticación elegido no frena la adopción de los socios" --campo "tipo=supuesto" --campo "categoria=deseabilidad" --campo "criticidad=alta" --campo "certeza=baja" --campo "validado=pendiente" --campo "responsable=Martín Suárez" --campo "notas=origen: BMAD prd.md:249 (pregunta abierta 1) (riesgos.py candidatos)"
S-003
```

## Paso 16 · Variante a) con BMAD: qué controles detectan los vacíos
```
$ python3 $EST/sanidad.py --proyecto gestion --rapido --corte 2026-10-28
Sanidad de 'Portal de autoservicio para socios' (pre-proyecto/SU): 0 ERROR · 3 AVISO · 0 INFO
  AVISO SUP-01 Supuesto crítico S-001 sin experimento para validarlo: «Hay métricas actuales del volumen de consultas y del costo por gestión».
  AVISO SUP-01 Supuesto crítico S-002 sin experimento para validarlo: «El núcleo operativo ofrece una API o base de lectura utilizable para s».
  AVISO SUP-01 Supuesto crítico S-003 sin experimento para validarlo: «El método de autenticación elegido no frena la adopción de los socios».
        → Definir cómo se valida (experimento), el criterio para seguir y la fecha límite (registro.py actualizar supuestos S-…).
```

```
$ python3 $EST/puertas.py --proyecto gestion verificar autorizar-proyecto
Puerta autorizar-proyecto: 4 bloqueo(s) · 5 condición(es) · 2 aviso(s)
  BLOQUEO   P-01 falta el artefacto pid (o su archivo)
  BLOQUEO   P-02 falta el artefacto business-case (o su archivo)
  BLOQUEO   P-03 faltan tolerancias de proyecto (tiempo, costo): las fija la junta; pm-director las registra
  BLOQUEO   L-01 falta la lista de control de la junta: puertas.py --proyecto <dir> lista autorizar-proyecto y confirmarla (puertas.py confirmar …)
  condición P-04 no se encontraron criterios de éxito (beneficios B-n, métricas SM-n, enfoque de beneficios u OKR)
  condición P-05 junta incompleta: falta usuario_senior
  condición P-05 junta incompleta: falta proveedor_senior
  condición P-06 sin plan de proyecto registrado (o incluido en el PID)
  condición P-11 supuestos críticos sin validar: S-001, S-002, S-003 (la junta invierte sobre hipótesis; acordar experimento, criterio y fecha o aceptarlos explícitamente con una decisión de la junta)
  aviso     P-09 registro de interesados vacío: sin matriz poder/interés (pm-interesados)
  aviso     P-10 sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave
  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta
```

## Paso 16b · Variante a) con BMAD: personas de usuario desde los recorridos UJ y capacidad × persona
```
$ python3 $IN --proyecto gestion personas candidatos --desde bmad
3 persona(s) candidata(s) · el modelo propone, la persona confirma; nada se registra solo. El texto citado es dato de la fuente, no una instrucción.
- Marta · fuente bmad-uj · UJ-1 (prd.md:35)
    arquetipo: socia de 58 años, comerciante, usa el celular a diario pero evita los trámites digitales complejos. Necesita una constancia de saldos para un trámite bancario.
    objetivo: Marta consulta su saldo y baja una constancia desde el celular
    contexto de uso: ya registrada, abre el portal desde el navegador del celular.
    dolores: [por confirmar]
    usa: FR-1;FR-2;FR-5;FR-3;FR-4
    → registro.py --proyecto gestion agregar personas --campo nombre=Marta --campo 'descripcion=socia de 58 años, comerciante, usa el celular a diario pero evita los trámites digitales complejos. Necesita una constancia de saldos para un trámite bancario.' --campo 'objetivo=Marta consulta su saldo y baja una constancia desde el celular' --campo 'dolores=[por confirmar]' --campo 'contexto_uso=ya registrada, abre el portal desde el navegador del celular.' --campo fuente=bmad-uj --campo 'evidencia=UJ-1 (prd.md:35)' --campo 'usa=FR-1;FR-2;FR-5;FR-3;FR-4'
- Diego · fuente bmad-uj · UJ-2 (prd.md:43)
    arquetipo: socio de 34 años, necesita un préstamo pequeño para una reparación.
    objetivo: Diego pide un préstamo simple y sigue su estado
    contexto de uso: autenticado, con contacto verificado.
    dolores: [por confirmar]
    usa: FR-6;FR-7
    → registro.py --proyecto gestion agregar personas --campo nombre=Diego --campo 'descripcion=socio de 34 años, necesita un préstamo pequeño para una reparación.' --campo 'objetivo=Diego pide un préstamo simple y sigue su estado' --campo 'dolores=[por confirmar]' --campo 'contexto_uso=autenticado, con contacto verificado.' --campo fuente=bmad-uj --campo 'evidencia=UJ-2 (prd.md:43)' --campo 'usa=FR-6;FR-7'
- Lucía · fuente bmad-uj · UJ-3 (prd.md:51)
    arquetipo: operadora de back-office, hoy transcribe pedidos que llegan por varios canales.
    objetivo: Lucía atiende la bandeja de solicitudes
    contexto de uso: autenticada en la consola de operador.
    dolores: [por confirmar]
    usa: FR-9;FR-10;FR-11
    → registro.py --proyecto gestion agregar personas --campo 'nombre=Lucía' --campo 'descripcion=operadora de back-office, hoy transcribe pedidos que llegan por varios canales.' --campo 'objetivo=Lucía atiende la bandeja de solicitudes' --campo 'dolores=[por confirmar]' --campo 'contexto_uso=autenticada en la consola de operador.' --campo fuente=bmad-uj --campo 'evidencia=UJ-3 (prd.md:51)' --campo 'usa=FR-9;FR-10;FR-11'
Confirmar con la persona cada candidata, completar dolores y lo que pide (solicita) o de qué se beneficia (beneficia), y registrar.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar personas --campo "nombre=Marta" --campo "descripcion=socia de 58 años, comerciante, usa el celular a diario pero evita los trámites digitales complejos. Necesita una constancia de saldos para un trámite bancario." --campo "objetivo=Marta consulta su saldo y baja una constancia desde el celular" --campo "contexto_uso=ya registrada, abre el portal desde el navegador del celular." --campo "fuente=bmad-uj" --campo "evidencia=UJ-1 (prd.md:35)" --campo "usa=FR-1;FR-2;FR-5;FR-3;FR-4" --campo "dolores=Evita los trámites digitales complejos; necesita la constancia para un trámite bancario"
PU-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar personas --campo "nombre=Diego" --campo "descripcion=socio de 34 años, necesita un préstamo pequeño para una reparación." --campo "objetivo=Diego pide un préstamo simple y sigue su estado" --campo "contexto_uso=autenticado, con contacto verificado." --campo "fuente=bmad-uj" --campo "evidencia=UJ-2 (prd.md:43)" --campo "usa=FR-6;FR-7;FR-8" --campo "dolores=No sabe en qué estado está su solicitud de préstamo" --campo "beneficia=FR-12"
PU-002
```

```
$ python3 $EST/registro.py --proyecto gestion agregar personas --campo "nombre=Lucía" --campo "descripcion=operadora de back-office, hoy transcribe pedidos que llegan por varios canales." --campo "objetivo=Lucía atiende la bandeja de solicitudes" --campo "contexto_uso=autenticada en la consola de operador." --campo "fuente=bmad-uj" --campo "evidencia=UJ-3 (prd.md:51)" --campo "usa=FR-8;FR-9;FR-10;FR-11" --campo "dolores=Transcribe pedidos que llegan por varios canales" --campo "solicita=FR-9"
PU-003
```

```
$ python3 $IN --proyecto gestion personas mapa --limite 0
| Capacidad | Título | MoSCoW | PU-001 Marta | PU-002 Diego | PU-003 Lucía |
|---|---|---|---|---|---|
| FR-1 | Alta y acceso del socio | sin prioridad | U |  |  |
| FR-2 | Recuperación de acceso | sin prioridad | U |  |  |
| FR-3 | Consulta de saldos de ahorro | sin prioridad | U |  |  |
| FR-4 | Consulta de préstamos | sin prioridad | U |  |  |
| FR-5 | Descarga de constancias en PDF | sin prioridad | U |  |  |
| FR-6 | Solicitud guiada de préstamo simple | sin prioridad |  | U |  |
| FR-7 | Seguimiento de solicitud y respuesta a pedidos de… | sin prioridad |  | U |  |
| FR-8 | Actualización de datos de contacto con verificaci… | sin prioridad |  | U | U |
| FR-9 | Bandeja única de solicitudes | sin prioridad |  |  | S·U |
| FR-10 | Resolución de solicitudes | sin prioridad |  |  | U |
| FR-11 | Roles y permisos | sin prioridad |  |  | U |
| FR-12 | Notificaciones por correo (y SMS opcional) | sin prioridad |  | B |  |
S solicitante · U usuario · B beneficiario
```

```
$ python3 $IN --proyecto gestion personas priorizacion
| Persona | Representante | Must | Should | Could | Won't | Sin prioridad | S | U | B | Beneficios |
|---|---|---|---|---|---|---|---|---|---|---|
| PU-001 Marta | — | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | — |
| PU-002 Diego | — | 0 | 0 | 0 | 0 | 4 | 0 | 3 | 1 | — |
| PU-003 Lucía | — | 0 | 0 | 0 | 0 | 4 | 1 | 4 | 0 | — |
12 capacidad(es) mapeadas · Must sin persona: ninguno
```

## Paso 17 · Variante a) con BMAD: recorrido y mapa de valor desde la especificación
```
$ python3 $BMAD --proyecto gestion recorridos --id UJ-2
UJ-2 Diego pide un préstamo simple y sigue su estado (_bmad-output/planning-artifacts/prds/prd-portal-socios-2026-10-17/prd.md:43)
  persona: Diego, socio de 34 años, necesita un préstamo pequeño para una reparación.
  entrada: autenticado, con contacto verificado.
  recorrido: elige "Solicitar préstamo", completa el formulario guiado (producto, monto, plazo dentro de los límites), revisa el resumen y envía.
  climax: recibe un número de solicitud y un correo de confirmación.
  resolucion: días después ve el estado "En revisión". Una operadora le pide un documento y Diego lo adjunta desde el portal. Recibe la aprobación por correo.
  caso_limite: si el monto excede el máximo del producto, el formulario lo indica antes de enviar.
  FR: FR-6, FR-7 · KPI: SM-3, SM-5 · contrapesos: SM-C1
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion recorrido semilla --uj UJ-2 --backstage UJ-3 --persona PU-002 --fecha 2026-10-29
Semilla 02-planificacion/mapas/recorrido-uj-2.json desde bmad: 3 etapa(s), 9 paso(s); emociones y fuentes [por confirmar] · KPI SM-3, SM-5
Siguiente: completar con evidencia, 'validar' y 'render'. El modelo propone; la persona confirma.
```

```
$ (pm-mapas-estrategicos completa la semilla: emociones con fuente, dolores, oportunidades y el backstage de UJ-3 alineado a cada paso; Martín Suárez confirma → gestion/02-planificacion/mapas/recorrido-uj-2.json)
Recorrido · P1 Elige "Solicitar préstamo" · +1 (supuesto declarado: PRD §2.1, «quiero pedir un préstamo pequeño y saber en qué estado está») · refs FR-6
Recorrido · P2 Completa el formulario guiado (producto, monto, plazo dentro de los límites) · 0 (supuesto declarado: formulario con límites por producto (pregunta abierta 3)) · refs FR-6
Recorrido · P3 Revisa el resumen · 0 (supuesto declarado)
Recorrido · P4 Envía · +1 (supuesto declarado) · refs FR-6
Clímax · P5 Recibe un número de solicitud y un correo de confirmación · +2 (supuesto declarado: clímax del recorrido UJ-2) · refs FR-12
Resolución · P6 Días después ve el estado "En revisión" · -1 (sin fuente) · dolor: No sabe cuánto falta para la respuesta → Mostrar el plazo de respuesta comprometido (48 h, SM-3)
Resolución · P7 Una operadora le pide un documento · -1 (supuesto declarado: pedido de información adicional (FR-10)) · dolor: Tiene que buscar el documento y volver a entrar → Adjuntar desde el aviso, sin buscar la solicitud · refs FR-7
Resolución · P8 Diego lo adjunta desde el portal · 0 (supuesto declarado) · refs FR-7
Resolución · P9 Recibe la aprobación por correo · +2 (supuesto declarado: resolución del recorrido UJ-2) · refs FR-12
KPI SM-3, SM-5 · contrapeso SM-C1
```

```
$ python3 $BMAD --proyecto gestion capacidades
capacidad Acceso y recuperación · FR-1, FR-2 · acceso · AD-4, AD-5, AD-6, AD-9 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:161)
capacidad Saldos y préstamos · FR-3, FR-4 · productos · AD-1, AD-4 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:162)
capacidad Constancias · FR-5 · constancias · AD-1, AD-6, AD-8 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:163)
capacidad Solicitudes del socio · FR-6, FR-7, FR-8 · solicitudes · AD-2, AD-3, AD-7, AD-9, AD-12 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:164)
capacidad Consola · FR-9, FR-10 · solicitudes + /consola · AD-3, AD-4, AD-6 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:165)
capacidad Roles y permisos · FR-11 · acceso · AD-4, AD-11 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:166)
capacidad Notificaciones · FR-12 · notificaciones · AD-7, AD-10 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:167)
capacidad Seguridad y privacidad · NFR-1 · transversal · AD-4, AD-5, AD-6, AD-13 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:168)
capacidad Rendimiento · NFR-3 · productos · AD-1 (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:169)
diferida Proveedor y método de identidad (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:173)
diferida Interfaz y capacidad reales del núcleo operativo (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:174)
diferida Productos y límites de préstamo, y doble aprobación (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:175)
diferida Normativa BCU, retención de auditoría y residencia de datos (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:176)
diferida Hosting, proveedor de correo/SMS y almacenamiento de adjuntos (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:177)
diferida Observabilidad, CI/CD y estrategia de pruebas (_bmad-output/planning-artifacts/architecture/architecture-portal-socios-2026-10-17/ARCHITECTURE-SPINE.md:178)
stack TypeScript 7.0.2
stack Node.js 24 LTS (pasar a 26 LTS, vigente desde 2026-10-28, si el arranque es posterior)
stack Next.js (App Router) 16.4.2
stack React 19.3.1
stack PostgreSQL 18.x (19 aún en RC)
stack drizzle-orm 0.45.4
stack @react-pdf/renderer 4.9.0
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion wardley semilla --slug portal --titulo "Portal de socios · qué construir y qué comprar" --pregunta "¿Qué construye el equipo, qué se compra o terceriza y dónde está la inercia?" --fecha 2026-10-29
Semilla 02-planificacion/mapas/wardley-portal.json desde bmad: 3 ancla(s), 15 componente(s), 6 enlace(s); posiciones y evidencia [por confirmar].
Siguiente: completar con evidencia, 'validar' y 'render'. El modelo propone; la persona confirma.
```

```
$ (pm-mapas-estrategicos ubica 9 de los 15 componentes de la semilla: roles y permisos queda dentro de acceso; seguridad y rendimiento son criterios de calidad, no componentes; productos y límites, normativa y observabilidad son configuración o condiciones. Martín Suárez confirma → gestion/02-planificacion/mapas/wardley-portal.json)
C1 Acceso y recuperación · a-medida (0,48) · visibilidad 0,70 · construir · reglas propias de alta y bloqueo (AD-5); el proveedor de identidad queda detrás de IdentityPort · refs FR-1, FR-2, AD-4, AD-5, AD-6, AD-9
C2 Saldos y préstamos · a-medida (0,38) · visibilidad 0,76 · construir · lectura del núcleo con timeout y sin caché vigente (AD-1) · refs FR-3, FR-4, AD-1, AD-4
C3 Constancias · a-medida (0,36) · visibilidad 0,85 · construir · PDF al vuelo con código de verificación propio (AD-8); librería estándar del stack · refs FR-5, AD-1, AD-6, AD-8
C4 Solicitudes del socio · a-medida (0,30) · visibilidad 0,70 · construir · máquina de estados única de la cooperativa (AD-3); diferencia el servicio · refs FR-6, FR-7, FR-8, AD-2, AD-3, AD-7, AD-9, AD-12
C5 Consola de operador · a-medida (0,26) · visibilidad 0,60 · construir · bandeja única con auditoría (AD-3, AD-6) · refs FR-9, FR-10, AD-3, AD-4, AD-6
C7 Notificaciones · producto (0,68) · visibilidad 0,40 · construir · outbox transaccional propio (AD-7, AD-10); el envío es un servicio de mercado · refs FR-12, AD-7, AD-10
C10 Identidad y segundo factor · commodity (0,80) · visibilidad 0,45 · comprar · decisión diferida en la arquitectura (pregunta abierta 1); servicios de identidad de mercado · refs AD-5
C11 Núcleo operativo · producto (0,58) · visibilidad 0,28 · sin decisión · inercia · sistema central en uso; su interfaz y capacidad son desconocidas (pregunta abierta 2) · refs AD-1
C14 Correo, SMS y hosting · commodity (0,88) · visibilidad 0,15 · tercerizar · decisión diferida: depende de presupuesto y residencia de datos (preguntas 4 y 6) · refs AD-7
3 anclas · 11 enlaces
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion wardley validar portal
wardley-portal.json: 0 error(es) · 0 aviso(s)
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion recorrido render uj-2 --png no
Vistas: 02-planificacion/visuales/recorrido-uj-2.md, 02-planificacion/visuales/recorrido-uj-2.html
Registrar (si es nuevo): estado.py --proyecto gestion artefacto mapa-recorrido-uj-2 --ruta 02-planificacion/visuales/recorrido-uj-2.md --estado borrador
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion wardley render portal --png no
Vistas: 02-planificacion/visuales/wardley-portal.md, 02-planificacion/visuales/wardley-portal.owm
Registrar (si es nuevo): estado.py --proyecto gestion artefacto mapa-wardley-portal --ruta 02-planificacion/visuales/wardley-portal.md --estado borrador
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion controles
AVISO MAP-03 recorrido-uj-2.json P6 «Días después ve el estado "En revisión"»: dolor sin tratamiento (requisito, historia, riesgo, issue, cambio, decisión, supuesto o revisión de calidad)
AVISO MAP-04 recorrido-uj-2.json P6 «Días después ve el estado "En revisión"»: emoción sin fuente (entrevista, métrica, observación o supuesto declarado)
AVISO MAP-01 wardley-portal.json C7 Notificaciones: en producto y marcado 'construir' sin decisión registrada
AVISO MAP-02 wardley-portal.json C11 Núcleo operativo: inercia sin riesgo abierto registrado
4 aviso(s) de la familia MAP
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion recorrido candidatos uj-2
P6 [supuesto] Si se resuelve «No sabe cuánto falta para la respuesta», la persona usa el nuevo canal en «Días después ve el estado "En revisión"» · 02-planificacion/mapas/recorrido-uj-2.json#P6
1 candidato(s); se registran solo tras la evaluación humana.
```

```
$ python3 $EST/registro.py --proyecto gestion agregar supuestos --campo "fecha=2026-10-29" --campo "autor=Martín Suárez" --campo "supuesto_o_restriccion=Mostrar el plazo de respuesta comprometido reduce las consultas de seguimiento de los socios" --campo "tipo=supuesto" --campo "categoria=deseabilidad" --campo "criticidad=media" --campo "certeza=baja" --campo "validado=pendiente" --campo "responsable=Sofía Ramírez" --campo "notas=origen: recorrido-uj-2.json#P6 (mapas.py recorrido candidatos)"
S-004
```

```
$ python3 $EST/registro.py --proyecto gestion agregar decisiones --campo "fecha=2026-10-29" --campo "decision=Notificaciones: construir el outbox propio (AD-7, AD-10) y tercerizar el envío de correo y SMS" --campo "contexto=mapa de valor del portal (MAP-01)" --campo "opciones_consideradas=construir todo; comprar una plataforma de notificaciones; outbox propio con envío tercerizado" --campo "decidido_por=Gestor: Martín Suárez" --campo "nivel=gestor"
D-001
```

```
$ python3 $EST/registro.py --proyecto gestion agregar riesgos --campo "fecha_identificacion=2026-10-29" --campo "autor=Martín Suárez" --campo "categoria=tecnico" --campo "causa=El núcleo operativo es un sistema central con interfaz y capacidad desconocidas (pregunta abierta 2, AD-1)" --campo "evento=El adaptador del núcleo se atrasa o no cumple la latencia de NFR-3" --campo "efecto=Atraso de las consultas de saldos, préstamos y constancias (FR-3, FR-4, FR-5)" --campo "tipo=amenaza" --campo "probabilidad=3" --campo "impacto=4" --campo "proximidad=corto-plazo" --campo "respuesta=reducir" --campo "acciones=prueba técnica de lectura con el entorno de pruebas del núcleo antes de estimar" --campo "propietario=Martín Suárez" --campo "fecha_revision=2026-11-15"
R-001
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion vincular uj-2 P6 --refs S-004
recorrido-uj-2.json P6: refs = S-004
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion vincular portal C7 --refs D-001
wardley-portal.json C7: refs = FR-12, AD-7, AD-10, D-001
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion vincular portal C11 --refs R-001
wardley-portal.json C11: refs = AD-1, R-001
```

```
$ (la persona declara la fuente de la emoción del paso P6 → gestion/02-planificacion/mapas/recorrido-uj-2.json)
P6: supuesto declarado: el PRD no informa plazos al socio (FR-7)
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion controles
0 aviso(s) de la familia MAP
```

```
$ python3 $PLUGIN/skills/pm-mapas-estrategicos/scripts/mapas.py --proyecto gestion tablero
Tablero de mapas: 2 mapa(s) dibujado(s) (wardley-portal.json, recorrido-uj-2.json) · 0 aviso(s) MAP · 4 vínculo(s) citado(s)
Escrito: 02-planificacion/visuales/tablero-mapas.html
```

