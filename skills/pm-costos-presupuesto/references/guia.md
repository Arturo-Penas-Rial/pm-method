# Guía de costos y presupuesto · Costs and budget guide

## 1. Convenciones y clases de exactitud
- Moneda, unidad de esfuerzo, redondeo y fecha de las tarifas se acuerdan antes de costear y quedan en el frontmatter del presupuesto.
- Clases de exactitud orientativas (configurables en el enfoque o plan de gestión de costos): orden de magnitud −25/+75 % (mandato, SU), presupuestaria −10/+25 % (iniciación), definitiva −5/+10 % (plan de etapa con cotizaciones).
- La definición de BAC y reservas es la del paquete (SPEC §1.10.6); no se renegocia documento por documento.

## 2. Fórmulas de referencia
```
Mano de obra               = Horas × Tarifa
Paramétrica                Costo = Unidades × Costo unitario
Análoga                    Costo = Costo previo × (Tamaño actual / Tamaño previo) × Ajuste
Tres puntos (PERT)         cE = (O + 4M + P) / 6        σ = (P − O) / 6
Paquete (base)             = Mano de obra + Materiales + Suministros + Equipos + Viajes + Otros directos + Indirectos   (sin reserva)
Ágil, costo por iteración  = Σ personas × dedicación × días × tarifa diaria + fijos del período
Contingencia (un nivel)    = Σ EMV amenazas (impacto monetario × prob.) + Σ costo de respuestas no incluidas en paquetes
BAC                        = Σ paquetes base (incl. gestión) + Contingencia       (línea base de medición; total del PV)
Reserva de gestión         = provisión para riesgos no identificados (monto o % del enfoque de riesgo §7) [+ otra reserva que fije la junta]
Presupuesto autorizado     = BAC + Reserva de gestión  (+ presupuesto de cambio si se usa)
PV acumulado (t)           = Σ pv_periodo hasta t ;  PV acumulado (fin) = BAC
Verificación cruzada       |Ascendente − Analógica| / Analógica > 25 % → revisar supuestos
```
EMV con la convención del paquete: P 1–5 → 10/30/50/70/90 % (configurable). Sin datos de riesgo: porcentaje justificado marcado como supuesto.

## 3. Reservas sin doble conteo
- **Contingencia**: para riesgos identificados; se calcula una vez y en un solo nivel (por etapa, recomendado; si se hace por paquete, no se repite en la etapa). Se asigna al período o etapa donde se espera el riesgo y se vincula a ids `R-###`.
- **BAC** = Σ estimaciones base de paquetes (incluido el de gestión, W-G) + contingencia. Es la línea base de medición del desempeño y el total de la serie PV.
- **Reserva de gestión**: fuera del BAC y del PV, para lo no identificado; la propone esta skill y solo la libera la junta (o la capa de negocio).
- **Provisión para riesgos no identificados** (regla por defecto del paquete): la provisión para riesgos no identificados va a la **reserva de gestión**, que solo libera la junta; el presupuesto de riesgo financia las respuestas y contingencias de los riesgos identificados. Por eso la contingencia (o presupuesto de riesgo) no lleva un margen para lo no identificado y la provisión se propone como `gestion=`; su uso es un cambio con `cargo=reserva-gestion` que decide la junta (CAM-05). El enfoque de riesgo §7 puede declarar el otro destino (`presupuesto-riesgo`, sugerencia de PRINCE2): entonces la provisión es un renglón propio de la contingencia, dentro del BAC, y no se repite en la reserva de gestión. Respaldo: PRINCE2 7, presupuesto de riesgo con provisión sugerida y control fijado por el enfoque (`pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §2.b R-18 y §2.c.6); PMBOK 8, reserva de contingencia para riesgos identificados y reserva de gestión para lo desconocido-desconocido, sin mezclarlas en una cifra (`pmbok8-dominios-procesos-adaptacion.md` §2.4.a y §5.3 punto 19; `pmbok8-artefactos-tecnicas-anexos.md` §3.2 "Análisis de reservas").
- **Presupuesto de cambio** (PRINCE2, opcional): fuera del BAC, declarado aparte, lo administra la autoridad de cambio.
- Nunca se quita contingencia sin cambiar la respuesta al riesgo que la sustenta.
- **Registro en `estado.json` (control permanente):** cuando la junta aprueba los montos, pm-director los registra en
  `presupuestos`: `estado.py presupuesto cambio=<presupuesto de cambio> riesgo=<reserva de riesgo> gestion=<reserva de gestión> limite_autoridad_cambio=<tope por cambio> --por "Ejecutiva: …" [--fecha …]`
  (números sin moneda ni separador de miles; queda en `decisiones.csv`; `estado.py resumen` los muestra). Esta skill
  propone los montos en `presupuesto.md`, no ejecuta el comando. Desde ahí la sanidad suma el consumo con el `costo` y
  el `cargo` de cada cambio de `cambios.csv` (CAM-03: INFO < 80 %, AVISO ≥ 80 %, ERROR > 100 %, que bloquea puertas;
  AVISO si se carga a un presupuesto no fijado), exige que lo cargado a la reserva de riesgo cite el R-### (CAM-02) y
  que la reserva de gestión la libere la junta (CAM-05). Lo que a mano se mira recién al fin de etapa, se ve en cada
  sanidad.

## 4. Consolidación con `wbs.py`
Cuando la hoja de costeo está lista, cargar la estimación base de cada paquete en la columna `costo` (y las horas en `esfuerzo_h`) de `02-planificacion/wbs.csv` y correr `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/wbs.py 02-planificacion/wbs.csv --mermaid 02-planificacion/visuales/wbs.md`. El total consolidado debe ser igual a Σ paquetes base de `hoja-costeo.md`; la contingencia y la reserva de gestión **no** se cargan en la WBS (viven en el presupuesto). Diferencias típicas: paquetes sin costo, costos cargados en un nodo padre (el script los ignora), paquete de gestión ausente de la WBS. El diagrama resultante (paquete, responsable, horas y costo) sirve como anexo del presupuesto.

## 5. Variante ágil y BMAD
- `iteraciones necesarias ≈ puntos Must+Should del release / velocidad`; `presupuesto de etapa = costo por iteración × iteraciones de la etapa`; PV por iteración (S1, S2…) o como proporción de puntos planificados × BAC.
- Con BMAD (`integraciones.especificacion = bmad`), el tamaño sale de la columna de gobierno `estimacion` de `backlog.csv` (sincronizado por `pm-bmad-puente`); el avance para EV, de `avance-bmad.csv` (`bmad.py avance`). Cada sprint es un paquete de trabajo con su costo de iteración.
- EVM ágil (SPEC §1.10.7): `evm.py --modo agil --pct-no-must <% Should/Could>`; un EAC > BAC es alcance que no entra, contra la tolerancia de alcance; excepción solo si los Must peligran.

## 6. Cómo consume `evm.py` la línea base
- `evm.py --csv <archivo> --bac <BAC>` lee columnas acumuladas `pv|pv_acumulado`, `ev|ev_acumulado`, `ac|ac_acumulado` (última fila con datos).
- Opción recomendada: `03-control/reportes/progreso.csv` (de `pm-progreso-reportes`) copia `periodo,pv_acumulado` de la línea base y suma `ev_acumulado,ac_acumulado` en cada corte.
- Alternativa: completar `ev_acumulado` y `ac_acumulado` en `linea-base-costo.csv`; las filas futuras vacías se omiten.
- `--bac` es siempre sin reserva de gestión. Semáforo con `--tol-costo`/`--tol-plazo` (%) o `--proyecto <dir>` (toma tolerancias de etapa e idioma de `estado.json`): verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo fuera → excepción. `--eac tendencia|atipico|compuesto` elige el EAC.

Cabecera de `linea-base-costo.csv`: `periodo,etapa,pv_periodo,pv_acumulado,ev_acumulado,ac_acumulado,notas` = period (AAAA-MM o S#), stage (1 = iniciación, 2…n entrega), planned value of the period, cumulative PV (sin reserva de gestión; el último = BAC), cumulative EV, cumulative AC (vacías hasta cada corte), notes (método de distribución, riesgos de la contingencia).

## 7. Opciones cuando el costo no entra
En orden de preferencia, cuantificando el efecto en tiempo, riesgo y beneficios:
1. Reducción de alcance por MoSCoW: retirar *Could*, luego *Should* (un *Must* solo con decisión de la junta); en ágil, menos iteraciones con el mismo equipo.
2. Cambio de recursos o de mezcla (tarifas, perfiles, make-or-buy con `pm-adquisiciones`) sin bajar la calidad declarada.
3. Reprogramar para eliminar horas extra o recargos; revisar si una intensificación previa encarece y se puede deshacer.
4. Revisar la contingencia contra los riesgos que la sustentan.
Si el BAC sigue fuera de la restricción del mandato o de la tolerancia de proyecto, el plan no se aprueba: decisión de la junta vía `pm-director` (informe de excepción con la plantilla de `pm-issues-cambios` si hay línea base; `decision-ad-hoc` en la iniciación).

## 8. Versión mínima vs. completa
| Elemento | Mínima | Completa |
|---|---|---|
| Hoja de costeo | Mano de obra + otros por paquete principal (o costo por iteración) | Cuatro bloques, indirectos, contratos, verificación cruzada |
| Contingencia | Porcentaje justificado por etapa | EMV por riesgo + respuestas, asignada a etapa o período |
| Presupuesto | Tabla por etapa con BAC, reserva de gestión y tolerancia | Por etapa y período, curva S, flujo de caja, conciliación |
| Línea base PV | Por etapa o iteración | Por período, lista para `evm.py` |
| Consolidación WBS | Opcional | `wbs.py` con costo por paquete y diagrama anexo |
| Export | No | xlsx con una hoja por tabla |

## 9. Reglas complementarias
1. [PRINCE2] Tolerancias por nivel: proyecto (capa de negocio), etapa (junta en cada `autorizar-etapa`), paquete (documento del paquete); las inferiores caben en la superior.
2. [PRINCE2] El business case se actualiza con los costos revisados en cada límite de etapa; cifras del business case y del plan coinciden o se explican.
3. [PMBOK→Plans] Conciliación con el límite de financiación: un período que excede los fondos se reprograma, no se maquilla.
4. [PMBOK→Business case] Costo del ciclo de vida: recortes que encarecen la operación se señalan al business case.
5. [Plantillas] Cotizaciones con fecha y validez; horas iguales a la hoja de estimación.
6. Curva S en Mermaid (`xychart-beta`) por defecto; con integración de diagramas, versión elevada vía `pm-visuales` sin reemplazar el CSV.
7. Exportación local: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/exportar.py xlsx --entrada 02-planificacion/linea-base-costo.csv --salida exportados/linea-base-costo.xlsx`, o la skill oficial xlsx si `integraciones.export` lo indica.
