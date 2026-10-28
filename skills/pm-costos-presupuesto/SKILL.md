---
name: pm-costos-presupuesto
description: "Costeo y presupuesto: reservas, BAC, línea base PV, curva S. Usar: costear, presupuesto, BAC, contingencia, reserva de gestión, budget, cost baseline. No: business case→pm-caso-de-negocio."
version: 2.5.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: planificacion
    agente: pm-planificacion
    procesos_prince2: [IP, SB]
    practicas_prince2: [plans, risk, progress, business-case]
    tecnicas_pmbok: [estimación ascendente, estimación paramétrica, estimación análoga, PERT, agregación de costos, análisis de reservas, EMV, curva S, conciliación del límite de financiación, valor ganado]
    artefactos: [hoja-costeo, presupuesto, linea-base-costo]
    idiomas: [es, en]
---

# Costos y presupuesto · Costs and budget

## Cuándo usar / When to use
- Ya existen paquetes de trabajo con esfuerzo (o, en ágil, backlog con puntos y velocidad) y hay que convertirlos en costos, reservas y línea base.
- Piden "costear", "presupuesto", "línea base de costo", "BAC", "curva S", "contingencia", "reserva de gestión", "flujo de caja", "presupuesto por etapa o iteración", "PV por período" o "exportar el presupuesto a Excel".
- Presupuesto del plan de proyecto (IP), de etapa o de excepción (SB), o sección de costos del business case.
- EN: bottom-up cost estimate, contingency and management reserve, BAC, time-phased baseline (S-curve), stage budgets.
- EN: planned value series for EVM, or budget export to .xlsx.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. plantillas bilingües. Equivalencias: hoja de costeo (cost estimating worksheet), línea base de costo (cost baseline), BAC (budget at completion), presupuesto autorizado (authorized budget), reserva de contingencia (contingency reserve), reserva de gestión (management reserve), presupuesto de cambio (change budget), valor planificado (planned value, PV). Columnas de `linea-base-costo.csv`: `references/guia.md` §6. Faltantes: `[por confirmar]` / `[to be confirmed]`.

## Conocimiento
- `references/guia.md` (esta skill): §1 convenciones, §2 fórmulas, §3 reservas, §4 consolidación con `wbs.py`, §5 ágil y BMAD, §6 `evm.py` y CSV, §7 opciones si no entra, §8 mínima vs. completa, §9 reglas complementarias.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §8–§9 (estimación y hoja de costeo), §5.3, §30.3 (EVM), Parte V.
- `pm-knowledge/references/plantillas-inicio-y-planes.md` §3.5 (plan de gestión de costos).
- `pm-knowledge/references/pmbok8-dominios-procesos-adaptacion.md` §2.4 (finanzas: reservas, financiación, ágil).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.7, §3.9, §3.2 (reservas, EMV) y bloque EVM.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §4.2.4 regla 15, §4.3.1 Paso 5, §4.2.3, §4.8.
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §4.c.1–§4.c.2 (tolerancias y excepción).

## Entradas requeridas
- `estado.json`: `enfoque_entrega`, `etapa_actual`, tolerancias de costo (proyecto y etapa), `integraciones.export`, `integraciones.especificacion`.
- **Predictivo/híbrido**: `hoja-estimacion.md`, `wbs.csv` y `diccionario-wbs.md` (paquetes, responsables), `cronograma.md` (fechas). Si faltan → `pm-cronograma-estimacion` / `pm-planificacion-por-productos`.
- **Ágil (perfil mínimo, SPEC §1.10.12)**: `backlog.csv` (puntos, MoSCoW, release), `release-plan.md` (cadencia, velocidad) y costo del equipo por iteración (§5).
- **Especificación (fuente única, SPEC §1.16)**: épicas e historias por release solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar epicas|historias` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: hoja de costeo, presupuesto y `linea-base-costo.csv`, que citan ids sin copiar texto.
- Restricción de costo del mandato o techo del business case; tarifas por rol, cotizaciones con fecha y validez, política de indirectos (si faltan, preguntar).
- `riesgos.csv` con `impacto_monetario` y `valor_esperado` (si faltan → `pm-riesgos`); límite de financiación por período si existe.

## Procedimiento
1. **Acordar convenciones**: moneda, unidad, redondeo, clase de exactitud (`references/guia.md` §1); versión mínima o completa (§8), con confirmación.
2. **Costear cada paquete (ascendente)** en `hoja-costeo.md`: `mano de obra = horas × tarifa` + directos con cotización + indirectos; **sin reserva dentro**. Método, base, supuestos, rango y confianza por fila; tipo de contrato de proveedores (`pm-adquisiciones`). La gestión es un paquete más (W-G).
3. **Variante ágil**: costo por iteración × iteraciones de la etapa; PV por iteración (§5).
4. **Bloques alternativos** sin detalle: paramétrico, análogo, tres puntos (§2). Ascendente vs. análoga > 25 % → revisar supuestos.
5. **Agregar siguiendo la WBS**: cargar la estimación base por paquete en `costo` (y horas en `esfuerzo_h`) de `wbs.csv` y correr `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/wbs.py 02-planificacion/wbs.csv`; el total consolidado = Σ paquetes base. Reservas fuera de la WBS (§4).
6. **Reservas sin doble conteo (SPEC §1.10.6)**: contingencia una vez y en un nivel (EMV + respuestas); `BAC = Σ paquetes base + contingencia`; reserva de gestión fuera del BAC; `presupuesto autorizado = BAC + reserva de gestión`; presupuesto de cambio aparte; los montos aprobados van a `estado.json` → `presupuestos` vía pm-director (§3).
7. **Distribuir en el tiempo** según la curva de consumo de cada paquete (lineal, hitos ponderados, 0/100, 50/50) → `linea-base-costo.csv` (`pv_periodo`, `pv_acumulado`; el último = BAC).
8. **Presupuesto**: en `presupuesto.md`, tabla por etapa (base, contingencia, BAC de etapa, tolerancia), curva S Mermaid, flujo de caja y conciliación con el límite de financiación; un exceso se reprograma con `pm-cronograma-estimacion`, nunca se oculta.
9. **Comparar** el BAC con la restricción del mandato ± `tolerancias.proyecto.costo`, y el BAC de etapa con la tolerancia propuesta.
10. **Si no entra**: opciones cuantificadas (MoSCoW, recursos, reprogramación, revisión de contingencia; §7). Si sigue fuera, el plan **no** se presenta como aprobable: decisión de la junta vía `pm-director`.
11. **Actualizar dependientes**: costos en el diccionario; sección de costos del business case (`pm-caso-de-negocio`); supuestos y riesgos de costo vía `registro.py`, con confirmación.
12. **Exportar** bajo demanda (`exportar.py xlsx` o skill xlsx; §9).
13. **Registrar y derivar**: `estado.py --proyecto <dir> artefacto presupuesto --ruta 02-planificacion/presupuesto.md --estado en-revision` (y `linea-base-costo`). **Puerta humana**: el presupuesto se aprueba con el plan (`autorizar-proyecto` / `autorizar-etapa`, registradas solo por `pm-director`); la reserva de gestión la aprueba la junta o la capa de negocio. Hasta entonces no hay línea base. Como subagente, cerrar con el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; el presupuesto por iteración vive dentro del de etapa, sin eliminar puertas.
2. [PRINCE2] Un sobrecosto previsto fuera de tolerancia se escala (excepción); nunca se consumen reservas en silencio.
3. [PRINCE2] Nada se aprueba sin acto humano registrado; solo `pm-director` registra puertas.
4. [PRINCE2] El presupuesto muestra por separado trabajo, gestión, contingencia, presupuesto de cambio y tolerancias.
5. [PRINCE2] Un plan cuyo costo excede la restricción del mandato o la tolerancia de proyecto va con opciones a la junta.
6. [PMBOK→Plans] Técnica elegida según la pregunta, con método, base, rango y confianza declarados.
7. [PMBOK→Plans] BAC = Σ paquetes base + contingencia; reserva de gestión fuera del BAC y del PV (SPEC §1.10.6).
8. [PMBOK→Risk] La contingencia se calcula una vez y en un nivel, vinculada a riesgos con EMV.
9. [PMBOK→Progress] Línea base distribuida en el tiempo; sin serie PV no hay EVM. En ágil, EAC > BAC = alcance que no entra (`evm.py --modo agil --pct-no-must`).
10. [Plantillas] Verificación cruzada ascendente vs. análoga (> 25 % revisar); WBS consolidada igual a la hoja de costeo.
11. [Plantillas] Versión mínima o completa según riesgo, costo y stakeholders.
12. Transparencia de IA: borrador; no inventar tarifas ni cotizaciones; citar la fuente de cada cifra.
13. Escrituras externas (ERP, hoja compartida, chat) solo con confirmación, vía `pm-integraciones`. Más reglas en §9.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Hoja de costeo | `templates/hoja-costeo.md` | `02-planificacion/hoja-costeo.md` (o `-etapa-<n>`) | `hoja-costeo` |
| Presupuesto (BAC, reservas, etapas, curva S, caja) | `templates/presupuesto.md` | `02-planificacion/presupuesto.md` | `presupuesto` |
| Línea base de costo (PV) | `templates/linea-base-costo.csv` | `02-planificacion/linea-base-costo.csv` | `linea-base-costo` |
| WBS con costo consolidado | `wbs.py` | `02-planificacion/wbs.csv` | en `pbs-wbs` |
| Export Excel (bajo demanda) | `exportar.py xlsx` o skill xlsx | `exportados/linea-base-costo.xlsx` | — |

## Calidad
- [ ] Cada fila de costeo con base, método, supuestos, rango y confianza; ningún paquete con reserva.
- [ ] Contingencia una sola vez, en un nivel declarado, vinculada a R-### con EMV.
- [ ] BAC = Σ paquetes base + contingencia; reserva de gestión fuera y marcada como propuesta.
- [ ] Total de `wbs.py` = Σ paquetes base de la hoja de costeo.
- [ ] Σ `pv_periodo` = BAC; etapa asignada a cada período.
- [ ] Comparación con mandato y tolerancias; opciones si no entra; caja conciliada con la financiación.
- [ ] Ágil: costo por iteración, iteraciones por etapa y velocidad declarados.
- [ ] Frontmatter completo; `borrador` o `en-revision` hasta la puerta.

## Escalamiento y excepciones
- BAC fuera de la restricción o tolerancia tras el paso 10 → `pm-director` antes de aprobar el plan.
- Pronóstico fuera de tolerancia con línea base → `pm-progreso-reportes` detecta, informe de excepción (plantilla de `pm-issues-cambios`), `pm-director` decide.
- Reserva de gestión o presupuesto de cambio: propuesta aquí; decisión de la junta, registrada por `pm-director`.
- Caja por encima del límite de financiación → `pm-cronograma-estimacion` y aviso a `pm-director`; riesgos sin impacto monetario → `pm-riesgos`.
- Como subagente: las decisiones humanas se devuelven en el bloque de retorno (SPEC §1.11), no se preguntan.

## Ejemplos de invocación
- "Costeá los paquetes de la etapa 2 y calculá la contingencia desde el registro de riesgos, sin duplicarla."
- "El mandato dice 180 mil y el presupuesto da 215 mil: ¿qué opciones tenemos antes de ir a la junta?"
- EN: "Build the bottom-up cost estimate and show BAC and management reserve separately."
- EN: "Produce the time-phased cost baseline so evm.py can read it."
- No activa: "Actualizá el ROI y el payback del caso de negocio" → `pm-caso-de-negocio`.

## EN summary
Costing and budgeting inside PRINCE2 plans. It turns package effort (or team cost per iteration) into bottom-up estimates without hidden reserves, rolls them up through `wbs.csv` with `wbs.py`, computes contingency once from the risk register, and sets BAC = base packages + contingency, with the management reserve outside the BAC and released only by the board. The baseline is time-phased into `linea-base-costo.csv` for `evm.py` (including agile mode). Costs outside the mandate constraint or tolerance go to the board with options, never absorbed.
