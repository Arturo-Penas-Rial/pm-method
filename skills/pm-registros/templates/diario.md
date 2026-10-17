---
tipo: diario
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Diario del proyecto · Daily log

**Proyecto / Project:** {{proyecto}}
*Nombre del proyecto según `estado.json`.*

**Titular del diario / Log keeper:** {{titular}}
*Gestor del proyecto o gestor de equipo que lleva este diario; cada gestor de equipo puede tener el suyo para su paquete de trabajo.*

**Período cubierto / Period covered:** {{periodo}}
*Desde–hasta; se puede llevar un único archivo continuo o uno por etapa.*

**Qué va aquí / What belongs here:** issues informales, acciones pequeñas, eventos significativos que ningún otro registro captura, observaciones y conversaciones que podrían convertirse en riesgo o issue. Durante la puesta en marcha (SU), también riesgos e issues hasta que se abran los registros formales.
*No anotar aquí solicitudes de cambio ni fuera de especificación: son siempre formales y van a issues.csv.*

## Entradas / Entries

| fecha / date | entrada / entry | responsable / owner | seguimiento / follow-up |
|---|---|---|---|
| {{fecha_entrada}} | {{entrada}} | {{responsable}} | {{seguimiento}} |

*fecha: ISO AAAA-MM-DD. entrada: qué pasó o qué se observó, en una o dos frases. responsable: quien debe actuar o vigilar. seguimiento: `pendiente`, `hecho AAAA-MM-DD`, `promovido a R-###/I-###/L-###` o `descartado`.*

## Revisión del período / Period review

**Fecha de revisión / Review date:** {{fecha_revision}}
*Se hace al cierre de cada período de informe, antes del highlight report.*

**Patrones detectados / Patterns found:** {{patrones}}
*Tres o más anotaciones sobre el mismo tema sugieren un issue o riesgo no declarado; listar el tema y las fechas.*

**Entradas promovidas / Entries promoted:** {{promovidas}}
*Ids creados en los registros formales a partir de este diario (R-###, I-###, S-###, L-###).*

**Acciones vencidas / Overdue actions:** {{vencidas}}
*Entradas con seguimiento `pendiente` cuya fecha comprometida pasó.*

## Lista de verificación / Checklist
- [ ] Cada entrada tiene fecha ISO, responsable y estado de seguimiento.
- [ ] Ninguna solicitud de cambio ni fuera de especificación quedó en el diario.
- [ ] Las entradas con impacto material fueron promovidas a su registro formal con id.
- [ ] Las acciones completadas tienen fecha de cierre; las vencidas aparecen en la revisión.
- [ ] La revisión del período se hizo antes de redactar el highlight report.
