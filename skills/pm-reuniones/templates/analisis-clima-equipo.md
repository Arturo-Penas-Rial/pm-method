---
tipo: analisis-clima-equipo
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
equipo: "{{equipo}}"
anonimizado: si
---

# Señales agregadas de clima del equipo · Aggregated team climate signals

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Lectura agregada y anonimizada de la dinámica de reuniones, a nivel de equipo. No contiene evaluaciones de personas ni inferencias emocionales individuales y no debe usarse para evaluar desempeño.

**Equipo / Team:** {{equipo}} · **Período / Period:** {{periodo}}
*Equipo o conjunto de roles analizado; nunca una persona sola.*

**Reuniones analizadas / Meetings analyzed:** {{reuniones}}
*Lista de transcripciones normalizadas con `--anonimizar` (rutas en 03-control/reuniones/).*

## 1. Consentimiento / Consent
**Confirmado por / Confirmed by:** {{consentimiento_por}} · **Fecha / Date:** {{consentimiento_fecha}} · **Forma / How:** {{consentimiento_forma}}
*Quién confirmó que los participantes aceptaron el análisis y cómo (acuerdo en reunión, mensaje, acta del equipo). Sin este dato, el documento no se produce.*

## 2. Participación / Participation
| Indicador / Indicator | Valor / Value | Tendencia / Trend |
|---|---|---|
| Concentración: % de palabras de los 2 hablantes principales / Top-2 share | {{concentracion}} | {{tendencia_concentracion}} |
| Participación por rol (agregada) / Share by role | {{por_rol}} | {{tendencia_rol}} |
| Turnos por reunión / Turns per meeting | {{turnos}} | {{tendencia_turnos}} |

*Datos del resumen de `transcripcion.py --json`. Roles con una sola persona se agregan con otro rol.*

## 3. Señales de la conversación / Conversation signals
- **Temas sin cierre / Unresolved topics:** {{temas_sin_cierre}}
*Temas que volvieron en varias reuniones sin decisión.*
- **Preguntas sin respuesta / Unanswered questions:** {{preguntas}}
- **Acciones sin responsable o vencidas (por equipo) / Unowned or overdue actions (team level):** {{acciones}}
- **Lo que el equipo dijo sobre su forma de trabajar / What the team said about its way of working:** {{citas}}
*Citas breves sin atribución.*

## 4. Ajustes propuestos / Proposed adjustments
| Ajuste / Adjustment | Para qué / Purpose | Quién lo decide / Decided by |
|---|---|---|
| {{ajuste_1}} | {{proposito_1}} | {{decide_1}} |

*Formato de reunión, facilitación, agenda, canal o frecuencia. Cambios a la matriz de comunicaciones van a pm-comunicacion-stakeholders.*

## 5. Límites del análisis / Limits
{{limites}}
*Qué no se puede concluir (p. ej. hablar menos no implica desacuerdo; transcripciones incompletas).*

## Lista de verificación / Checklist
- [ ] Consentimiento registrado (quién, cuándo, cómo).
- [ ] Fuentes anonimizadas; ningún nombre ni alias que permita identificar a una persona.
- [ ] Solo indicadores observables y agregados por equipo o rol.
- [ ] Ninguna inferencia de emociones, actitudes o desempeño individual.
- [ ] Sin valoraciones personales almacenadas; intermedios nominativos eliminados.
- [ ] Ajustes orientados a la forma de trabajar, con quién decide.
