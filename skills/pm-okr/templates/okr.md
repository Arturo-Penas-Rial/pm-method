---
tipo: okr
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
periodo: "{{periodo}}"
---

# OKR del proyecto · Project OKRs

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Los OKR ilustran el business case; no lo reemplazan. Los datos de beneficios se citan desde su documento dueño.

**Proyecto / Project:** {{proyecto}} · **Período / Period:** {{periodo}}
*Trimestre, semestre o el horizonte del business case.*

**Dueño de los objetivos / Objectives owner:** {{responsable_objetivos}}
*Ejecutivo o usuario sénior responsable de los beneficios (rol: nombre).*

**Fuentes / Sources:** {{fuentes}}
*Versión del business case, del enfoque de beneficios y, si aplica, del PRD (sha corto) de donde salen OBJ-n, B-nn y SM-n.*

## 1. Contexto / Context
{{contexto}}
*Dos o tres frases: a qué objetivos de negocio contribuye el proyecto y por qué se usan OKR (práctica de la organización, tablero de producto, etc.).*

## 2. Cadena de valor / Value chain

| Objetivo de negocio / Business objective (OBJ-n) | Objetivo / Objective (O-n) | Resultado clave / Key result (KR-n.m) | Vínculo / Link (B-nn · SM-n) | Producto que lo habilita / Enabling product |
|---|---|---|---|---|
| {{obj_1}} | {{o_1}} | {{kr_1_1}} | {{vinculo_1_1}} | {{producto_1_1}} |
| {{obj_1}} | {{o_1}} | {{kr_1_2}} | {{vinculo_1_2}} | {{producto_1_2}} |

*Una fila por KR. El detalle numérico (base, meta, actual, fecha) vive en `00-direccion/okr.csv`; aquí solo la lógica.*

## 3. Supuestos y dependencias / Assumptions and dependencies
- {{supuesto_1}}
*Qué tiene que ser cierto para que los productos produzcan el resultado (adopción, procesos, otros proyectos). Registrar los críticos en supuestos.csv.*

## 4. Puntuación y umbrales / Scoring and thresholds
**Umbrales / Thresholds:** {{umbrales}}
*Por defecto 0,7 / 0,4 (convención habitual de OKR, no regla de PRINCE2 ni PMBOK). Indicar si la organización usa otros.*

**Última puntuación / Latest score:** {{ultima_puntuacion}}
*Ruta de la tabla generada por `okr.py --markdown` (03-control/reportes/<fecha>-okr.md).*

## 5. Cadencia de revisión / Review cadence
| Momento / Moment | Quién / Who | Salida / Output |
|---|---|---|
| Límite de etapa {{n}} / Stage boundary | {{quien_sb}} | {{salida_sb}} |
| Revisión de beneficios / Benefits review ({{fecha_rb}}) | {{quien_rb}} | {{salida_rb}} |

*Mínimo: cada límite de etapa y las revisiones de beneficios del plan de revisión posterior al cierre.*

## 6. Cambios a metas aprobadas / Changes to approved targets
| Fecha / Date | KR | Antes / Before | Después / After | Decisión / Decision id |
|---|---|---|---|---|
| {{fecha_cambio}} | {{kr_cambio}} | {{antes}} | {{despues}} | {{id_decision}} |

*Toda modificación tras la aprobación lleva un D-### en decisiones.csv.*

## Lista de verificación / Checklist
- [ ] Cada objetivo cita un OBJ-n y tiene dueño con rol de junta.
- [ ] Cada KR cita un B-nn o SM-n existente; ningún beneficio inventado aquí.
- [ ] Base, meta y fecha en `okr.csv`; fuente anotada cuando repiten datos del business case.
- [ ] KR que miden resultados, no tareas ni entregables.
- [ ] Umbrales declarados como convención.
- [ ] Revisiones agendadas en límites de etapa y en el plan de revisión de beneficios.
