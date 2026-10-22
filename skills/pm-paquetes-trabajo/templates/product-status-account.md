---
tipo: product-status-account
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Estado de productos · Product status account — {{proyecto}}

> Borrador generado con apoyo de IA a partir del plan de etapa, calidad.csv y las aprobaciones registradas; cada fila cita su fuente. / AI-assisted draft built from the stage plan, calidad.csv and recorded approvals; every row cites its source.
> Lo derivable de los registros (estados, conteos, revisiones, aceptaciones, diferencias, paquetes) lo llena `estado.py productos --markdown` (guía de pm-paquetes-trabajo §5). / Derivable content is filled by `estado.py productos --markdown`.

## 1. Alcance del informe / Report scope

**Fecha de corte / Cut-off date:** {{fecha_corte}}
*Momento al que corresponde la foto; todo lo posterior no se refleja.*

**Alcance / Scope:** {{alcance}}
*Etapa, paquete de trabajo, iteración o proyecto completo; indicar el plan del que salen los productos.*

**Motivo / Reason:** {{motivo}}
*Fin de etapa, recepción de paquete, excepción, auditoría, cierre o a demanda.*

**Fuentes / Sources:** {{fuentes}}
*Rutas del plan, de calidad.csv, de las descripciones de paquete y del tracker si se usó.*

## 2. Resumen / Summary

| Estado / Status | Cantidad / Count |
|---|---|
| No iniciado / Not started | {{n_no_iniciado}} |
| En desarrollo / In development | {{n_en_desarrollo}} |
| En revisión de calidad / In quality review | {{n_en_revision}} |
| Aprobado (pendiente de aceptación) / Approved (pending acceptance) | {{n_aprobado}} |
| Aceptado / Accepted | {{n_aceptado}} |
| Con concesión / Concession granted | {{n_concesion}} |
| Fuera de especificación abierto / Open off-specification | {{n_off_spec}} |

*Conteos calculados sobre la tabla de la sección 3; deben sumar el total de productos del plan.*

## 3. Detalle por producto / Product detail

| Id / Id | Producto / Product | Paquete / Work package | Versión / Version | Descripción aprobada el / Description approved on | Estado / Status | Actividad de calidad (Q-nnn) / Quality activity | Resultado / Result | Aprobado por · fecha / Approved by · date | Aceptado por · fecha / Accepted by · date | Observaciones / Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| {{id_1}} | {{producto_1}} | {{wp_1}} | {{version_1}} | {{fecha_desc_1}} | {{estado_1}} | {{q_1}} | {{resultado_1}} | {{aprobado_1}} | {{aceptado_1}} | {{notas_1}} |
| {{id_2}} | {{producto_2}} | {{wp_2}} | {{version_2}} | {{fecha_desc_2}} | {{estado_2}} | {{q_2}} | {{resultado_2}} | {{aprobado_2}} | {{aceptado_2}} | {{notas_2}} |

*Un renglón por producto del plan vigente. "Aprobado" es la aprobación de la autoridad nombrada en la descripción de producto; "aceptado" es la aceptación formal del usuario o de la junta. Dejar vacío lo que no ocurrió; no inferir.*

## 4. Desviaciones y pendientes / Deviations and open items

**Fuera de especificación / Off-specifications:** {{off_specs}}
*Ids de issues.csv con la decisión pendiente o tomada (completar o concesión).*

**Productos con actividades de calidad vencidas / Products with overdue quality activities:** {{calidad_vencida}}
*Q-nnn cuya fecha prevista pasó sin fecha real.*

**Productos sin descripción aprobada / Products without approved description:** {{sin_descripcion}}
*Deben resolverse antes de autorizar su paquete.*

**Discrepancias entre registro y estado físico / Register vs. physical state discrepancies:** {{discrepancias}}
*Lo que el registro dice y lo que se verificó realmente; relevante en auditorías y cierre prematuro.*

## 5. Estado de paquetes de trabajo / Work package status

| Paquete / Work package | Gestor de equipo / Team manager | Estado / Status | Pronóstico vs. tolerancias / Forecast vs. tolerances | Último checkpoint / Last checkpoint | Issues y riesgos abiertos / Open issues and risks |
|---|---|---|---|---|---|
| {{wp_a}} | {{gestor_a}} | {{estado_wp_a}} | {{pronostico_a}} | {{checkpoint_a}} | {{abiertos_a}} |

*Estados: autorizado, en ejecución, en verificación, completado, suspendido. El pronóstico cita el checkpoint del que sale.*

## 6. Conclusión y siguiente paso / Conclusion and next step

{{conclusion}}
*Qué habilita o bloquea este estado: cerrar la etapa, recibir el paquete, escalar una excepción, recomendar el cierre.*

## Lista de verificación / Checklist
- [ ] Todos los productos del plan vigente aparecen en la tabla, sin omisiones.
- [ ] Cada fila cita la actividad de calidad y la aprobación que la sustenta; vacíos reales, no inferidos.
- [ ] Los conteos del resumen coinciden con la tabla de detalle.
- [ ] Off-specifications con decisión o marcados como pendientes.
- [ ] Fecha de corte y fuentes declaradas.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
