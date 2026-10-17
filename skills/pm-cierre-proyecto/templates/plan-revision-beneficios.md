---
tipo: plan-revision-beneficios
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Plan de revisión de beneficios · Benefits review plan — {{proyecto}}

> Borrador generado con apoyo de IA. Se prepara en el cierre (CP) y se entrega `en-revision` a la junta junto con el informe de fin de proyecto; las revisiones las ejecuta el negocio (o el programa) después del cierre, no el proyecto. Datos faltantes: `[por confirmar]` / `[to be confirmed]`. / AI-assisted draft prepared at closing; reviews are carried out by the business after closure.

**Ruta / Path:** `04-cierre/plan-revision-beneficios.md` · **Clave / Key:** `plan-revision-beneficios`
*Se registra con `estado.py artefacto plan-revision-beneficios --ruta 04-cierre/plan-revision-beneficios.md --estado en-revision`.*

## 1. Vínculos / Links

**Business case de referencia / Reference business case:** {{ruta_business_case}} (v{{version_bc}}) · **Original / Original:** `00-direccion/historial/business-case-v1.0.md`
*Versión final actualizada con reales y versión original congelada al autorizar el proyecto; las metas de este plan deben salir de ahí.*

**Enfoque de gestión de beneficios / Benefits management approach:** {{ruta_enfoque_beneficios}}
*Normalmente `00-direccion/enfoque-beneficios.md`. Este plan lo concreta para el período posterior al cierre; si lo contradice, gana el enfoque aprobado y se anota la diferencia.*

**Responsable global de beneficios / Overall benefits owner:** {{responsable_global}}
*Usualmente el usuario sénior o quien designe la capa de negocio; si el proyecto es parte de un programa, el responsable del programa.*

**Tipo de cierre / Closure type:** {{tipo_cierre}}
*planificado · prematuro. En cierre prematuro, indicar qué beneficios se pierden, cuáles se conservan parcialmente y con qué meta revisada.*

## 2. Beneficios a revisar / Benefits to review

| # | Beneficio / Benefit | Métrica / Metric | Línea de base / Baseline | Meta / Target | Realizado al cierre / Realized at closure | Fecha de medición / Measurement date | Frecuencia / Frequency | Dueño tras el cierre / Owner after closure | Fuente de datos / Data source |
|---|---|---|---|---|---|---|---|---|---|
| B1 | {{beneficio_1}} | {{metrica_1}} | {{base_1}} | {{meta_1}} | {{realizado_1}} | {{fecha_1}} | {{frecuencia_1}} | {{dueno_1}} | {{fuente_1}} |
| B2 | {{beneficio_2}} | {{metrica_2}} | {{base_2}} | {{meta_2}} | {{realizado_2}} | {{fecha_2}} | {{frecuencia_2}} | {{dueno_2}} | {{fuente_2}} |

*Un beneficio por fila, medible (unidad y período). Línea de base con fecha y fuente; meta igual a la del business case salvo cambio aprobado (citar C-### o D-###). Dueño con nombre y área en la organización receptora: un beneficio sin dueño no se transfiere y se escala al ejecutivo.*

## 3. Perjuicios a vigilar / Dis-benefits to monitor

| # | Perjuicio / Dis-benefit | Métrica / Metric | Umbral aceptable / Acceptable threshold | Dueño / Owner | Acción si se supera / Action if exceeded |
|---|---|---|---|---|---|
| P1 | {{perjuicio_1}} | {{metrica_p1}} | {{umbral_p1}} | {{dueno_p1}} | {{accion_p1}} |

*Efectos negativos que alguien percibe como pérdida (p. ej. más carga administrativa en un área). "Ninguno identificado" si no hay, para dejar constancia de que se consideró.*

## 4. Método de revisión / Review method

**Cómo se revisará / How it will be reviewed:** {{metodo_revision}}
*Medición directa del sistema, encuesta, auditoría, comparación con grupo de control, reseña posterior a la acción. Indicar quién recopila, quién analiza y a quién se informa.*

**Calendario de revisiones / Review schedule:** {{calendario}}
*Fechas o hitos de cada revisión (p. ej. +3, +6 y +12 meses desde el traspaso) y cuándo termina el seguimiento.*

**Criterio de éxito / Success criterion:** {{criterio_exito}}
*Qué resultado se considera beneficio logrado, parcialmente logrado o no logrado; qué se hace en cada caso.*

**Informe a / Report to:** {{destinatario_informe}}
*Capa de negocio, comité, programa o patrocinador que recibe los resultados después del cierre.*

## 5. Recursos y financiamiento / Resources and funding

**Esfuerzo estimado / Estimated effort:** {{esfuerzo}}
*Horas o jornadas por revisión y roles necesarios.*

**Financiamiento / Funding:** {{financiamiento}}
*Centro de costos o presupuesto operativo que paga las revisiones; el presupuesto del proyecto se cierra y no las cubre.*

**Supuestos y dependencias / Assumptions and dependencies:** {{supuestos}}
*Datos que deben seguir disponibles, sistemas que deben medirse, personas que deben seguir en sus roles. Proponer para supuestos.csv si aún está abierto.*

## 6. Aprobación / Approval

**Revisado por / Reviewed by:** {{revisores}}
*Aseguramiento del negocio y responsable global de beneficios.*

**Decisión / Decision:** {{decision}}
*La junta lo aprueba junto con la autorización del cierre; pm-director registra la puerta `autorizar-cierre` y `estado.py aprobar plan-revision-beneficios --por "<rol: nombre>"`.*

## Lista de verificación / Checklist
- [ ] Cada beneficio pendiente del business case aparece con métrica, línea de base, meta, fecha, frecuencia, dueño y fuente de datos.
- [ ] Metas coherentes con el business case final; diferencias con el original explicadas con su cambio o decisión.
- [ ] Perjuicios considerados (o "ninguno identificado").
- [ ] Método, calendario, criterio de éxito y destinatario del informe definidos.
- [ ] Financiamiento fuera del presupuesto del proyecto identificado.
- [ ] Ningún beneficio sin dueño; los huérfanos escalados al ejecutivo.
- [ ] En cierre prematuro: beneficios perdidos y conservados declarados.
- [ ] Vínculos a business case y enfoque de beneficios verificados; documento `en-revision` hasta la decisión de la junta.
