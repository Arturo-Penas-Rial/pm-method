---
tipo: plan-compromiso-stakeholders
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
confidencial: si
---

# Plan de compromiso de interesados · Stakeholder engagement plan — {{proyecto}}

> Dónde invertir el esfuerzo de relación: a quién mover de resistente a neutral, a quién mantener como líder y con qué acciones. Plan vivo, de circulación restringida; alimenta el enfoque de comunicación (que se completa último). Mapeo del paquete: parte del enfoque de gestión de la comunicación. / Living, restricted plan of engagement actions per stakeholder; feeds the communication approach.

**Versión mínima / Minimal version:** {{version_minima}}
*`sí`: se omite como documento aparte y se añaden al enfoque de comunicación dos columnas (nivel actual / deseado y acción).*

**Frecuencia de revisión / Review frequency:** {{frecuencia_revision}} · **Última revisión / Last review:** {{ultima_revision}}
*Como mínimo en cada fin de etapa y cuando entran o salen interesados.*

## 1. Matriz de evaluación del compromiso / Engagement assessment matrix

| Id | Interesado / Stakeholder | Desconocedor / Unaware | Resistente / Resistant | Neutral / Neutral | Partidario / Supportive | Líder / Leading |
|---|---|---|---|---|---|---|
| ST-001 | {{s1_nombre}} | {{s1_u}} | {{s1_r}} | {{s1_n}} | {{s1_s}} | {{s1_l}} |
| ST-002 | {{s2_nombre}} | {{s2_u}} | {{s2_r}} | {{s2_n}} | {{s2_s}} | {{s2_l}} |
| ST-003 | {{s3_nombre}} | {{s3_u}} | {{s3_r}} | {{s3_n}} | {{s3_s}} | {{s3_l}} |

*Marcar `A` (actual) y `D` (deseado) en la columna correspondiente; `A/D` si coinciden. Datos tomados de `stakeholders.csv` (`nivel_compromiso_actual`, `nivel_compromiso_deseado`). El nivel deseado es realista: no todos deben ser líderes.*

## 2. Enfoque por interesado / Approach per stakeholder

| Id | Brecha / Gap | Acción / Action | Responsable / Owner | Fecha / Date | Canal / Channel | Indicador de avance / Progress indicator | Reflejado en / Reflected in |
|---|---|---|---|---|---|---|---|
| ST-001 | {{s1_brecha}} | {{s1_accion}} | {{s1_responsable}} | {{s1_fecha}} | {{s1_canal}} | {{s1_indicador}} | {{s1_reflejo}} |
| ST-002 | {{s2_brecha}} | {{s2_accion}} | {{s2_responsable}} | {{s2_fecha}} | {{s2_canal}} | {{s2_indicador}} | {{s2_reflejo}} |

*Una acción como mínimo por brecha: reunión individual, participación en diseño, demo, visibilidad de beneficios para su área, formación. "Reflejado en": enfoque de comunicación y cronograma (las acciones consumen tiempo).*

## 3. Involucramiento mediante demostraciones (ágil / híbrido) / Engagement through demos (agile / hybrid)

{{demos}}
*Quién asiste a cada demo o revisión de incremento, con qué frecuencia, qué se espera de ellos (retroalimentación al backlog, aceptación). Obligatorio si `enfoque_entrega` es ágil o híbrido.*

## 4. Cambios pendientes de interesados / Pending stakeholder changes

| Cambio / Change | Fecha prevista / Expected date | Impacto / Impact | Acción preventiva / Preventive action |
|---|---|---|---|
| {{cambio_1}} | {{cambio_1_fecha}} | {{cambio_1_impacto}} | {{cambio_1_accion}} |

*Altas, bajas o relevos en roles clave; riesgo de reabrir acuerdos.*

## 5. Interrelaciones y mapa de relaciones / Interrelationships and relationship map

{{interrelaciones}}
*Relaciones y solapamientos entre interesados que condicionan las acciones (misma jefatura, influencia informal, dependencia contractual). Opcional salvo con muchos interesados.*

```mermaid
flowchart LR
    {{s1_id}}["{{s1_nombre_corto}}"] -->|{{rel_1}}| {{s2_id}}["{{s2_nombre_corto}}"]
    {{s2_id}} -->|{{rel_2}}| {{s3_id}}["{{s3_nombre_corto}}"]
```
*Grafo de influencia; solo cuando hay relaciones múltiples. `pm-visuales` puede mejorarlo si las integraciones lo permiten.*

## 6. Responsabilidades / Responsibilities

{{responsabilidades}}
*Gestor: mantiene el plan. Usuario sénior: asesora sobre influenciadores de su comunidad y logra adhesión de los usuarios. Proveedor sénior: lado proveedor. Ejecutivo: relaciones con la capa de negocio y con interesados de alto poder. Soporte: asiste en análisis y seguimiento.*

## 7. Medición del compromiso / Engagement measurement

{{medicion}}
*Cómo se sabrá que el compromiso mejora: asistencia a demos, respuestas a consultas, cambios de actitud observados con fuente, encuestas breves. Se informa en el highlight report cuando hay brechas críticas.*

## 8. Riesgos y lecciones / Risks and lessons

{{riesgos_lecciones}}
*Riesgos de compromiso registrados en `riesgos.csv`; lecciones sobre qué acciones funcionaron.*

## Lista de verificación / Checklist
- [ ] Todos los interesados clave del registro aparecen en la matriz.
- [ ] Cada brecha tiene al menos una acción con responsable, fecha y canal.
- [ ] Nivel deseado realista.
- [ ] Acciones reflejadas en el enfoque de comunicación y en el cronograma.
- [ ] Demos como mecanismo en ágil/híbrido.
- [ ] Cambios pendientes con impacto evaluado y acción preventiva.
- [ ] Indicadores de avance definidos.
- [ ] Frecuencia de revisión y última revisión fechadas.
- [ ] Marcado como confidencial; circulación restringida; estado `borrador`.
