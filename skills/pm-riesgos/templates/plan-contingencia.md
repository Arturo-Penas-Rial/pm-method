---
tipo: plan-contingencia
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Plan de contingencia · Contingency plan

**Riesgo / Risk:** {{id_riesgo}} · {{evento}}
*El mismo `id` de `riesgos.csv` (R-###). Este plan acompaña a la respuesta `aceptar` o `contingencia`, o sirve de plan de reserva (fallback) de otra respuesta que puede fallar; no reemplaza la fila del registro.*

**Respuesta elegida / Chosen response:** {{respuesta}} · opción {{opcion}} de `03-control/registros/opciones-riesgo/{{id_riesgo}}.csv` · decisión {{id_decision}}
*La que decidió el propietario con `riesgos.py opciones --elegir`; citar la decisión D-### y, si no fue la recomendada, su motivo.*

**Evaluación / Assessment:** P×I {{probabilidad}}×{{impacto}} = {{puntuacion}} · EMV {{emv}} · residual con el plan P×I {{probabilidad_residual}}×{{impacto_residual}} · EMV residual {{emv_residual}}
*Cifras de `riesgos.csv` y del archivo de opciones; sin cifra, `[por confirmar]`.*

## 1. Disparador / Trigger

**Condición medible / Measurable condition:** {{disparador}}
*Un hecho observable con umbral y fecha o frecuencia (p. ej. «dos caídas del proveedor en un mes», «spike sin datos al día 5»). Es el mismo texto de la columna `disparador` de `riesgos.csv`. «Si las cosas empeoran» no es un disparador.*

**Indicador de alerta temprana / Early warning:** {{indicador_alerta}} · **quién lo vigila y cada cuánto:** {{vigilancia}}
*La señal previa que permite prepararse antes del disparo; se revisa con la cadencia del enfoque de riesgo.*

## 2. Acciones al disparo / Actions when triggered

| # | Acción / Action | Ejecutor (actionee) / Actionee | Plazo desde el disparo / Lead time | Costo / Cost |
|---|---|---|---|---|
| 1 | {{accion_1}} | {{ejecutor_1}} | {{plazo_1}} | {{costo_1}} |
| 2 | {{accion_2}} | {{ejecutor_2}} | {{plazo_2}} | {{costo_2}} |

*Se planifican ahora y se ejecutan solo al disparo. Cada acción, al activarse, pasa a `acciones.csv` con `origen=R-###` y fecha.*

**Propietario del riesgo / Risk owner:** {{propietario}} · **Ejecutor principal / Main actionee:** {{ejecutor}}
*El propietario responde por el plan y lo acepta; el ejecutor tiene la autoridad y los medios para la acción.*

## 3. Monto y fuente / Amount and funding

**Monto de la contingencia / Contingency amount:** {{monto}} {{moneda}} · **tiempo / time:** {{tiempo}} días
*Lo que costaría activar el plan (el `monto_contingencia` de la opción); en la evaluación entra ponderado por la probabilidad.*

**Fuente / Source:** presupuesto de riesgo de la etapa (`estado.json.presupuestos.riesgo`: {{presupuesto_riesgo}}; comprometido {{comprometido}}; remanente {{remanente}})
*El presupuesto de riesgo financia respuestas y contingencias; no es reserva libre del gestor. Si el monto supera el remanente o la autoridad delegada, decide la junta (reserva de gestión o plan de excepción).*

## 4. Activación / Activation

**Quién la autoriza / Who authorizes:** {{autoriza}}
*La autoridad que fija el enfoque de riesgo sobre la reserva (por defecto, el ejecutivo); el agente nunca la activa.*

**Cómo se registra / How it is recorded:**
1. `riesgos.csv`: el disparador se alcanzó → nota con fecha; si el riesgo ya ocurrió, `estado=ocurrido` e issue en `pm-issues-cambios`.
2. `cambios.csv`: `costo={{monto}}`, `cargo=reserva-riesgo`, cita {{id_riesgo}} en descripción o justificación (sanidad CAM-02) y `decidido_por` la autoridad; el consumo contra el presupuesto lo vigila CAM-03.
3. `decisiones.csv`: la decisión de activar, con las opciones consideradas y `revisar_en`.
4. `acciones.csv`: las acciones de la sección 2 con responsable y fecha.

## 5. Plan alternativo si falla / Fallback plan

**Si el plan no da resultado / If the plan fails:** {{plan_reserva}}
*Qué hacer si la contingencia no alcanza o no puede ejecutarse; cuándo se considera fallida (señal y plazo).*

**Escalamiento / Escalation:** {{escalamiento}}
*Si el residual tras activar sigue sobre la línea de tolerancia, o el costo rompe una tolerancia de etapa: excepción a `pm-director`.*

## Lista de verificación / Checklist
- [ ] Disparador medible, idéntico al de `riesgos.csv`, con quién lo vigila y cada cuánto.
- [ ] Acciones con ejecutor, plazo desde el disparo y costo; propietario que acepta el plan.
- [ ] Monto y fuente (presupuesto de riesgo) con el remanente citado; autoridad de activación según el enfoque.
- [ ] Registro de la activación previsto: `cambios.csv` (reserva-riesgo + R-###), `decisiones.csv`, `acciones.csv`.
- [ ] Plan alternativo y criterio de escalamiento.
- [ ] `notas` de `riesgos.csv` cita este archivo; cifras sin fuente marcadas `[por confirmar]`.
