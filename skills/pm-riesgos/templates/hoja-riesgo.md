---
tipo: hoja-riesgo
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Hoja de datos de riesgo · Risk data sheet

**Identificador / Risk id:** {{id_riesgo}}
*El mismo `id` que en `riesgos.csv` (R-###). Esta hoja amplía la fila; no la reemplaza.*

**Título / Title:** {{titulo}}
*Una línea que identifique el riesgo en informes.*

**Tipo / Type:** {{tipo}}
*`amenaza` (threat) u `oportunidad` (opportunity).*

**Categoría / Category:** {{categoria}}
*Según la guía de registros: tecnico, externo, organizacional, gestion, comercial, sostenibilidad, otro.*

**Estado / Status:** {{estado}}
*`abierto`, `en-seguimiento`, `escalado`, `ocurrido`, `retirado`, `cerrado`; sincronizado con el CSV.*

**Fecha de identificación / Date identified:** {{fecha_identificacion}}
*ISO.*

**Última revisión / Last review:** {{fecha_revision}}
*ISO; vencida si supera la cadencia del enfoque de riesgos.*

## 1. Descripción / Description

**Causa / Cause:** {{causa}}
*La situación o factor que origina el riesgo (no es el riesgo en sí).*

**Evento / Event:** {{evento}}
*Lo incierto que podría ocurrir.*

**Efecto / Effect:** {{efecto}}
*La consecuencia sobre los objetivos, en sus unidades (días, moneda, productos, métrica).*

**Enunciado / Statement:** Si {{causa_corta}}, puede ocurrir {{evento_corto}}, lo que provocaría {{efecto_corto}}.
*Frase única derivada de los tres campos; es lo que aparece en informes.*

**Objetivos afectados / Objectives affected:** {{objetivos_afectados}}
*Entre beneficios, tiempo, costo, calidad, alcance, sostenibilidad, riesgo; indicar la tolerancia de cada uno.*

## 2. Evaluación actual / Current assessment

| Dimensión / Dimension | Valor / Value | Base de la estimación / Basis |
|---|---|---|
| Probabilidad / Probability (1–5) | {{probabilidad}} | {{base_probabilidad}} |
| Impacto tiempo / Time impact | {{impacto_tiempo}} | {{base_impacto_tiempo}} |
| Impacto costo / Cost impact | {{impacto_costo}} | {{base_impacto_costo}} |
| Impacto alcance-calidad / Scope-quality impact | {{impacto_alcance_calidad}} | {{base_impacto_alcance}} |
| Impacto beneficios-sostenibilidad / Benefits-sustainability impact | {{impacto_beneficios}} | {{base_impacto_beneficios}} |
| Impacto máximo (1–5) / Max impact | {{impacto}} | regla multi-objetivo del enfoque |
| Puntuación / Score | {{puntuacion}} | probabilidad × impacto |
| Calificación / Rating | {{calificacion}} | umbrales del enfoque; sobre la línea de tolerancia: {{sobre_linea}} |
| Proximidad / Proximity | {{proximidad}} | {{base_proximidad}} |
| Velocidad / Velocity | {{velocidad}} | con qué rapidez se sentiría el impacto |

*Citar datos de proyectos comparables o el juicio de quién estimó; no dejar la base vacía.*

**Valor monetario esperado / Expected monetary value:** EMV = {{probabilidad_fraccion}} × {{impacto_monetario}} = {{emv}} {{moneda}}
*Probabilidad convertida a % (por defecto 1–5 → 10/30/50/70/90 %) por impacto en moneda; coincide con `valor_esperado` de riesgos.csv si se carga `impacto_monetario`. Marcar `[por confirmar]` si el impacto monetario no está estimado.*

## 3. Respuesta planificada / Planned response

**Estrategia / Strategy:** {{estrategia}}
*Amenaza: evitar, reducir, transferir, compartir, aceptar, contingencia, escalar. Oportunidad: explotar, mejorar, compartir, aceptar, contingencia, escalar. Justificar por qué no las demás.*

**Descripción de la respuesta / Response description:** {{respuesta}}
*Qué se hará concretamente.*

| Acción / Action | Ejecutor / Actionee | Fecha límite / Due | Costo / Cost | Estado / Status |
|---|---|---|---|---|
| {{accion_1}} | {{ejecutor_1}} | {{fecha_1}} | {{costo_1}} | {{estado_1}} |
| {{accion_2}} | {{ejecutor_2}} | {{fecha_2}} | {{costo_2}} | {{estado_2}} |

*Cada acción debe estar en el plan de etapa o en un paquete de trabajo; si no, no tiene recursos.*

**Costo total de la respuesta / Total response cost:** {{costo_respuesta}} {{moneda}}
*Cargado al presupuesto de riesgo; autorizado por {{autorizado_por}}.*

**Propietario del riesgo / Risk owner:** {{propietario}}
*Responsable de gestionar el riesgo de principio a fin; acepta esta hoja.*

## 4. Evaluación residual esperada / Expected residual assessment

| Dimensión / Dimension | Antes / Before | Después / After |
|---|---|---|
| Probabilidad / Probability | {{probabilidad}} | {{probabilidad_residual}} |
| Impacto / Impact | {{impacto}} | {{impacto_residual}} |
| Puntuación / Score | {{puntuacion}} | {{puntuacion_residual}} |
| EMV | {{emv}} | {{emv_residual}} |

**Justificación económica / Economic justification:** beneficio = {{emv}} − {{emv_residual}} = {{beneficio_emv}}; costo de la respuesta = {{costo_respuesta}}; se justifica: {{se_justifica}}
*Si el costo supera el beneficio, indicar la justificación no económica (regulatoria, reputacional) o cambiar la respuesta.*

**Riesgos secundarios / Secondary risks:** {{riesgos_secundarios}}
*Nuevos riesgos que crea la respuesta; registrarlos en `riesgos.csv` con su propio id.*

**Riesgo residual aceptado / Accepted residual risk:** {{residual_aceptado}}
*Lo que queda aun con la respuesta; si sigue sobre la línea de tolerancia, combinar otra respuesta o escalar.*

## 5. Alerta temprana y contingencia / Early warning and contingency

**Indicador de alerta temprana / Early warning indicator:** {{indicador_alerta}}
*Señal observable de que el riesgo se está materializando; quién la vigila y con qué frecuencia.*

**Disparador / Trigger:** {{disparador}}
*Condición concreta que activa el plan de contingencia (fecha, umbral, evento); copiarla a la columna `disparador` de riesgos.csv.*

**Plan de contingencia / Contingency plan:** {{plan_contingencia}}
*Qué se hará si el riesgo ocurre; se planifica ahora, se ejecuta solo al disparo.*

**Plan de reserva / Fallback plan:** {{plan_reserva}}
*Qué hacer si la respuesta principal falla.*

**Reserva de fondos / Contingency funds:** {{fondos_contingencia}} {{moneda}} · **Reserva de tiempo / Contingency time:** {{tiempo_contingencia}} días
*Deben estar reflejadas en el presupuesto de riesgo y en el plan de etapa.*

## 6. Historial / History

| Fecha / Date | Cambio / Change | Por / By |
|---|---|---|
| {{hist_fecha}} | {{hist_cambio}} | {{hist_por}} |

*Reevaluaciones, cambios de estrategia, escalados, decisiones de la junta (D-###), materialización (→ I-###).*

**Registros asociados / Related records:** {{registros_asociados}}
*Ids de supuestos de origen (S-###), issues generados (I-###), cambios (C-###), decisiones (D-###), lecciones (L-###).*

## Lista de verificación / Checklist
- [ ] Causa, evento y efecto separados y enunciado derivado.
- [ ] Probabilidad e impactos con base de estimación y en las escalas del enfoque.
- [ ] Puntuación, calificación y posición respecto de la línea de tolerancia coherentes con `riesgos.csv`.
- [ ] Estrategia del catálogo justificada; acciones con ejecutor, fecha y costo; propietario que acepta.
- [ ] Residual, secundarios y justificación económica completos.
- [ ] Disparador explícito, plan de contingencia y reservas reflejadas en el presupuesto de riesgo.
- [ ] Fila de `riesgos.csv` sincronizada (`notas` referencia esta hoja).
- [ ] Cifras sin fuente marcadas `[por confirmar]`.
