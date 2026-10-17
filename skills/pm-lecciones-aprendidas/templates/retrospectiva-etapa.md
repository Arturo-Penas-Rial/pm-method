---
tipo: retrospectiva-etapa
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Taller de lecciones de etapa · Stage lessons workshop — {{iteracion_o_etapa}}

*Para la retrospectiva de cada iteración (sprint) usar `pm-agil-hibrido/templates/retrospectiva.md`; este taller se hace en el límite de etapa (o en un hito o al cierre), consolida lo aprendido en la etapa, incluidas las retrospectivas de iteración, y alimenta el informe de lecciones y el informe de fin de etapa. Ruta: `03-control/reportes/AAAA-MM-DD-retrospectiva-etapa-<n>.md`.*

> Borrador generado con apoyo de IA a partir de la sesión; el acuerdo del equipo sobre las acciones es lo que lo valida. Ambiente sin culpas. / AI-assisted draft from the session; the team's agreement on actions is what validates it. Blame-free setting.

## 1. Datos de la sesión / Session data

**Etapa o hito / Stage or milestone:** {{iteracion_o_etapa}}
*Número y nombre de la etapa de gestión (1 = iniciación; 2…n = entrega) o hito revisado. En ágil/híbrido, indicar qué iteraciones abarca y enlazar sus retrospectivas.*

**Fecha / Date:** {{fecha_sesion}}
*Fecha de la sesión.*

**Facilitador / Facilitator:** {{facilitador}}
*Quien conduce. Preferible una persona neutral (aseguramiento, PMO, facilitador de otro equipo). Si facilita el gestor del proyecto (o el scrum master que además es gestor), dejarlo dicho aquí y en la sección 8, y pedir a otra persona que recoja los ítems sobre la gestión, porque el sesgo es probable al evaluar su propio control.*

**Participantes / Participants:** {{participantes}}
*Todo el equipo; en etapa, gestores de equipo y, si corresponde, aseguramiento o proveedor.*

**Formato / Format:** {{formato}}
*estrella de mar · 4L · reseña posterior a la acción · tres columnas (mínimo). Declarar cuál se usó.*

**Caja de tiempo / Timebox:** {{caja_tiempo}}
*Duración prevista y real.*

## 2. Datos del período / Period data

| Métrica / Metric | Valor / Value | Fuente / Source |
|---|---|---|
| {{metrica_1}} | {{valor_1}} | {{fuente_1}} |
| {{metrica_2}} | {{valor_2}} | {{fuente_2}} |

*Velocidad, ítems completados vs. comprometidos, bloqueos, incidentes, resultados de calidad (Q-nnn), desvíos contra tolerancias; sin cifras inventadas.*

## 3. Seguimiento de acciones anteriores / Previous actions follow-up

| Acción anterior / Previous action | Responsable / Owner | Hecha / Done | Resultado o motivo / Result or reason |
|---|---|---|---|
| {{accion_prev_1}} | {{resp_prev_1}} | {{hecha_prev_1}} | {{resultado_prev_1}} |

*Se revisa primero; acciones no hechas se re-deciden o se descartan con motivo.*

## 4. Ítems por categoría / Items by category

### Formato estrella de mar / Starfish format

| Empezar / Start | Dejar de hacer / Stop | Mantener / Keep | Más / More | Menos / Less |
|---|---|---|---|---|
| {{start_1}} | {{stop_1}} | {{keep_1}} | {{more_1}} | {{less_1}} |

*Usar esta tabla si el formato es estrella de mar; eliminar la otra.*

### Formato 4L / 4L format

| Gustó / Liked | Aprendió / Learned | Faltó / Lacked | Anheló / Longed for |
|---|---|---|---|
| {{liked_1}} | {{learned_1}} | {{lacked_1}} | {{longed_1}} |

*Usar esta tabla si el formato es 4L; eliminar la otra.*

### Reseña posterior a la acción / After-action review (opcional)

**Qué debía ocurrir / What was supposed to happen:** {{aar_esperado}}
**Qué ocurrió / What happened:** {{aar_real}}
**Por qué hubo diferencias / Why the differences:** {{aar_causas}}
**Qué aprendemos / What we learn:** {{aar_aprendizaje}}
*Útil para hitos y cierre; sin búsqueda de culpables.*

## 5. Temas priorizados / Prioritized themes

| Tema / Theme | Votos / Votes | Comentario / Comment |
|---|---|---|
| {{tema_1}} | {{votos_1}} | {{comentario_tema_1}} |

*Agrupar ítems similares y priorizar por voto; de aquí salen las acciones.*

## 6. Acciones acordadas / Agreed actions

| Acción / Action | Responsable / Owner | Fecha / Date | Destino (plan de etapa, backlog, acciones.csv) / Destination | Id destino / Destination id |
|---|---|---|---|---|
| {{accion_1}} | {{resp_1}} | {{fecha_accion_1}} | {{destino_1}} | {{id_destino_1}} |
| {{accion_2}} | {{resp_2}} | {{fecha_accion_2}} | {{destino_2}} | {{id_destino_2}} |

*Una a tres acciones concretas; más de tres rara vez se cumplen. Las que no van a un plan o al backlog se registran en `acciones.csv` (A-###, `origen=retrospectiva-etapa-<n>`). En tracker solo con confirmación explícita.*

## 7. Lecciones transferibles / Transferable lessons

| Lección (recomendación) / Lesson (recommendation) | Categoría / Category | Impacto organizacional / Organizational impact | Id en lecciones.csv / Lessons log id |
|---|---|---|---|
| {{leccion_1}} | {{cat_leccion_1}} | {{org_leccion_1}} | {{id_leccion_1}} |

*Lo que sirve a otras etapas, equipos o proyectos; se vuelca a lecciones.csv con responsable (entra en estado `registrada`).*

## 8. Clima y seguridad psicológica / Climate and psychological safety

{{clima}}
*Observación breve del facilitador: participación, silencios, tensiones; señales que el gestor debe conocer. Si el facilitador fue el gestor, declarar el posible sesgo y cómo se mitigó.*

## Lista de verificación / Checklist
- [ ] Participó todo el equipo y se garantizó un ambiente sin culpas; facilitador declarado (si fue el gestor, sesgo anotado).
- [ ] Retrospectivas de iteración de la etapa (pm-agil-hibrido) revisadas e incorporadas.
- [ ] Formato declarado; datos del período con fuente.
- [ ] Acciones de la retrospectiva anterior revisadas.
- [ ] Una a tres acciones con responsable, fecha y destino.
- [ ] Lecciones transferibles registradas en lecciones.csv con id.
- [ ] Caja de tiempo respetada.
- [ ] Escrituras en tracker solo con confirmación explícita.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
