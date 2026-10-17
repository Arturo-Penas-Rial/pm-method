---
tipo: acta-junta
proyecto: "{{proyecto}}"
version: "1.0"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
puerta: "{{tipo_puerta}}"
id_decision: "{{id_decision}}"
---

# Acta de decisión de la junta · Board decision record

> Este documento registra una decisión tomada por personas con rol en la junta. El agente lo redacta a partir de lo decidido; no decide. Pasa a `estado: aprobado` cuando `aprobado_por` lleva nombre y rol del ejecutivo.

**Proyecto / Project:** {{proyecto}} · **Puerta / Gate:** {{tipo_puerta}} · **Etapa / Stage:** {{etapa}}
*Según estado.json y el paquete de decisión asociado.*

**Fecha de la decisión / Decision date:** {{fecha_decision}} · **Modalidad / Format:** {{modalidad}}
*Reunión, correo, chat, acuerdo sin reunión con instrucción documentada del ejecutivo.*

**Solicitud evaluada / Decision request reviewed:** {{ruta_solicitud}}
*Ruta y versión de `00-direccion/decisiones/AAAA-MM-DD-solicitud-<puerta>.md` o de la evaluación de excepción. Ruta de esta acta: `00-direccion/decisiones/AAAA-MM-DD-acta-junta-<puerta>.md` (clave `acta-junta-<fecha>`).*

## 1. Participantes / Participants

| Nombre / Name | Rol en la junta / Board role | Presente / Present | Posición / Position |
|---|---|---|---|
| {{nombre_1}} | Ejecutivo / Executive | {{presente_1}} | {{posicion_1}} |
| {{nombre_2}} | Usuario sénior / Senior user | {{presente_2}} | {{posicion_2}} |
| {{nombre_3}} | Proveedor sénior / Senior supplier | {{presente_3}} | {{posicion_3}} |
| {{nombre_4}} | {{rol_4}} | {{presente_4}} | {{posicion_4}} |

*Posición: a favor / con condiciones / en contra / se abstiene. Si no hubo unanimidad, decide el ejecutivo y se deja constancia.*

## 2. Decisión / Decision

**Decisión / Decision:** {{decision}}
*aprobado · rechazado · condicionado · pendiente. Enunciado que no admita dos lecturas. `condicionado` avanza como aprobado y deja las condiciones abiertas hasta `estado.py cumplir-condiciones <puerta>`; `pendiente` (p. ej. se pidió más información) no cambia el estado.*

**Decidido por / Decided by:** {{decidido_por}}
*Nombre y rol de quien tiene la autoridad (ejecutivo; capa de negocio si excede tolerancias de proyecto).*

**Opciones consideradas / Options considered:** {{opciones_consideradas}}
*Las del paquete, con la letra; indicar cuál se eligió y por qué se descartaron las demás, en una línea cada una.*

**Contexto / Context:** {{contexto}}
*Puerta, etapa, excepción o issue de origen; estado de la justificación continua en el momento de decidir.*

## 3. Condiciones y acciones / Conditions and actions

| # | Condición o acción / Condition or action | Responsable / Owner | Fecha / Due | Id en acciones.csv |
|---|---|---|---|---|
| 1 | {{condicion_1}} | {{resp_1}} | {{fecha_1}} | {{accion_1}} |
| 2 | {{condicion_2}} | {{resp_2}} | {{fecha_2}} | {{accion_2}} |

*Solo si la decisión es condicionada o genera acciones. Cada fila se abre en `acciones.csv` (A-###, `origen=acta-junta-<fecha>`) con responsable y `fecha_compromiso`; una condición no es un issue. Cuando todas se cumplen: `estado.py cumplir-condiciones <puerta>`.*

## 4. Tolerancias y autoridad confirmadas / Confirmed tolerances and authority

**Tolerancias de la etapa autorizada / Tolerances of the authorized stage:** {{tolerancias}}
*Siete objetivos en unidades, o referencia a 00-direccion/tolerancias-y-autoridad.md. Se escriben con `estado.py tolerancia --nivel etapa ...` después de registrar la puerta (autorizar-etapa vacía las de la etapa anterior).*

**Autoridad delegada / Delegated authority:** {{autoridad_delegada}}
*Autoridad de cambio y presupuestos, si cambian con esta decisión.*

## 5. Artefactos afectados y comunicación / Affected artifacts and communication

**Artefactos afectados / Affected artifacts:** {{artefactos_afectados}}
*Qué pasa a aprobado (ruta y versión) y qué se vuelve obsoleto.*

**Comunicar a / Communicate to:** {{comunicar_a}}
*Audiencias según el enfoque de comunicación: capa de negocio (notificación de inicio/autorización/cierre), equipo, cliente, proveedores. Lo ejecuta pm-comunicacion-stakeholders con confirmación.*

**Revisar en / Review on:** {{revisar_en}}
*Próxima puerta o fecha en que se reevalúa la decisión.*

## 6. Registro / Record

- `estado.py puerta {{tipo_puerta}} --decision {{decision}} --por "{{decidido_por}}" [--condiciones ".."]` (solo pm-director) → ejecutado: {{registro_puerta}}
- Fila en `decisiones.csv` escrita por el propio script → id {{id_decision}} (ver `puertas[].decision_id`)
- Documentos aprobados con `estado.py aprobar <clave> --por "{{decidido_por}}"` → claves {{claves_aprobadas}}
- Condiciones en `acciones.csv` → ids {{ids_acciones}}

*Marcar sí/no con fecha. El acta no está completa hasta que los registros existen. No agregar a mano otra fila en decisiones.csv para la misma puerta.*

## Lista de verificación / Checklist
- [ ] Decisión enunciada sin ambigüedad y con valor permitido (aprobado/rechazado/condicionado/pendiente).
- [ ] Nombre y rol de quien decidió; coincide con la autoridad del método para esta puerta.
- [ ] Opciones consideradas y motivo de descarte registrados.
- [ ] Condiciones con responsable, fecha e id de acción (A-###).
- [ ] Tolerancias de la etapa autorizada confirmadas en los siete objetivos.
- [ ] Puerta en estado.json con `decision_id`, documentos aprobados con `aprobar` y acciones abiertas.
- [ ] `aprobado_por` completado y `estado: aprobado` solo tras confirmación del ejecutivo.
