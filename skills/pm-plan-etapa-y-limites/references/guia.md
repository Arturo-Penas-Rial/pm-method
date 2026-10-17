# Guía de planes y límites de etapa · Stage plans and boundaries guide

Equivalencias: límite de etapa (stage boundary, SB), informe de fin de etapa (end stage report), plan de excepción (exception plan), lecciones incorporadas (lessons incorporated), registro de productos (product register).

## 1. Puertas que prepara esta skill y quién decide
| Puerta (`estado.py puerta <tipo>`) | Momento | Paquete que se entrega a la junta | Decide | Efecto si se aprueba |
|---|---|---|---|---|
| `autorizar-inicio` | Fin de SU | Brief, business case esquemático, descripción del producto del proyecto, `plan-etapa-1.md` | Junta (ejecutivo) | Fase `inicio`, proceso `IP`, `etapa_actual = 1` (iniciación) |
| `autorizar-proyecto` | Fin de IP | PID (enfoques, controles, plan de proyecto, business case completo) | Junta / capa de negocio | `proyecto_autorizado = true`; línea base de la PID (y del PRD con BMAD, `bmad.py linea-base` por `pm-director`) |
| `autorizar-etapa` | Fin de IP (para la etapa 2) y de cada etapa (SB) | Informe de fin de etapa, plan de etapa siguiente, business case y plan de proyecto actualizados; con BMAD, resultado de `bmad.py verificar` y del gate de preparación del sprint planning | Junta (fija tolerancias de etapa) | Fase `entrega`, proceso `CS`, `etapa_actual` = n+1, tolerancias de etapa a registrar |
| `autorizar-plan-excepcion` | Tras informe de excepción y `limite-etapa --excepcion X-###` | `plan-excepcion-X-###.md`, PID actualizada, informe de fin de etapa opcional | Junta (etapa) o capa de negocio (proyecto) | Vuelve a CS (o IP), `excepcion_abierta` vacía, nueva línea base |
| `autorizar-cierre` | Última etapa (tras `estado.py cierre`) | Lo prepara `pm-cierre-proyecto` | Junta | Fase `cerrado` |

Transiciones sin puerta (las ejecuta `pm-control` o `pm-director`): `estado.py limite-etapa [--excepcion X-###]` (CS → SB) y `estado.py cierre [--prematuro]` (→ CP).

Comandos de referencia (puerta y tolerancia: solo `pm-director`, tras la decisión humana):
- `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> puerta autorizar-etapa --decision aprobado|condicionado|rechazado --por "<rol: nombre>" [--etapa-nombre "..."] [--fin AAAA-MM-DD] [--condiciones "..."]` — avanza `etapa_actual` y escribe `decisiones.csv`.
- `... tolerancia --nivel etapa tiempo="±10 días" costo="±8 %"`; `... tolerancia --nivel proyecto ...` (capa de negocio).
- `... limite-etapa [--excepcion X-###]`; `... aprobar plan-proyecto --por "<rol: nombre>"`.
- `estado.py etapa` queda solo para correcciones manuales: la puerta aprobada ya avanza la etapa.

## 2. Plan de la etapa de iniciación (SU) — detalle
Productos de gestión que producirá la iniciación: PID con enfoques y controles, plan de proyecto, business case completo, plan de la primera etapa de entrega. El plan lista sus actividades, recursos, duración, costo de la propia iniciación y tolerancias de la etapa 1. La versión mínima suele bastar.

## 3. Plan de proyecto (IP) — composición
Alcance, dependencias, supuestos y prerrequisitos, lecciones incorporadas, productos (referencia a PBS/PFD/descripciones; con BMAD, ids del PRD), trabajo (WBS en `wbs.csv`, paquetes y si cada uno es secuencial o iterativo), presupuesto (con riesgo y cambio), cronograma de alto nivel con etapas, metas y tolerancias de proyecto, controles (informes, umbrales, excepción), decisiones planificadas de la junta (puertas por etapa) y transición a operación. El plan referencia los planes subsidiarios y enfoques; no los duplica.

## 4. Criterios para definir etapas
- Más etapas = más control y más costo de gestión; un proyecto simple puede tener iniciación (1) + una etapa de entrega (2).
- Poner un límite donde haya una decisión clave (continuar tras prototipo, licitación, ciclo presupuestario, fin de tramo de programa).
- Etapas más cortas con muchas dependencias, alta incertidumbre o riesgo elevado; no tienen que ser uniformes.
- En ágil, una etapa agrupa N iteraciones o una release; con BMAD, releases por épica y cada sprint = paquete de trabajo. Con alta incertidumbre, etapas de un mes que redefinen alcance en cada límite.
- Evitar paquetes que crucen un límite; si es inevitable (compras de largo plazo), revisar su estado en SB.

## 5. Tolerancias
Siete dimensiones (tiempo, costo, alcance, calidad, beneficios, riesgo, sostenibilidad); tiempo y costo obligatorias. Proyecto: las fija la capa de negocio/ejecutivo. Etapa: la junta en cada `autorizar-etapa`. Paquete: en el documento del paquete. Las inferiores caben en las superiores; se estrechan a medida que mejora la información; cada plan declara qué restricción manda. Esta skill solo las **propone**.

## 6. Plan de etapa — composición
Alcance de la etapa, dependencias, supuestos, lecciones incorporadas (de `lecciones.csv` y de la etapa anterior), productos, paquetes de trabajo con equipo o proveedor, presupuesto y siete tolerancias de etapa, controles (frecuencia de checkpoint y highlight, umbrales, procedimiento de excepción), actividades de calidad planificadas (alta en `calidad.csv` con fechas objetivo), riesgos e issues de la etapa. En ágil/híbrido: iteraciones de la etapa, backlog comprometido (Must) y tolerancia de alcance amplia.

## 7. Fin de etapa — detalle
- **Reales**: fechas, costos y productos aceptados (registro de productos y `calidad.csv`; con BMAD, `avance-bmad.csv`) en el plan de etapa vigente; previsiones de lo que resta en el plan de proyecto; diferencias contra la línea base marcadas.
- **Business case** (vía `pm-caso-de-negocio`): costos y fechas revisados, exposición agregada a riesgos contra la tolerancia de riesgo, beneficios obtenidos o previstos. Si deja de sostenerse, decirlo: parar bien no es fracaso.
- **Lecciones**: `lecciones.csv`, retrospectivas de iteración (`pm-agil-hibrido`) y diario; taller de etapa con `pm-lecciones-aprendidas` si hace falta; `registro.py agregar lecciones ...` con confirmación; marcar las que se incorporan al plan siguiente.
- **Informe de fin de etapa**: resumen del gestor; revisión de desempeño (business case, objetivos del proyecto y de la etapa, equipo, actividades de calidad, productos y entregas escalonadas, lecciones); acciones de seguimiento; issues y riesgos clave (solicitudes de cambio y fuera de especificación del período, concesiones); pronóstico contra objetivos y tolerancias. Aseguramiento lo confirma antes de la junta.
- **Revisión de la PID**: estructura del equipo, descripciones de rol y enfoques para la etapa siguiente (`pm-organizacion-roles`, `pm-enfoques-gestion`).
- **Envío a la junta**: lo delega `pm-director` / `pm-comunicacion-stakeholders`; escrituras externas con confirmación.

## 8. BMAD en el límite de etapa
Si `estado.json.integraciones.especificacion = bmad`, antes de pedir la puerta:
1. `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> verificar`: desvíos del PRD, arquitectura o épicas respecto de la línea base (ids agregados o retirados, contenido distinto) y Sprint Change Proposals nuevas. Cada desvío no tratado → issue `solicitud-cambio` en `pm-issues-cambios`; si hay solicitudes abiertas que afectan la etapa siguiente, se informan en el informe de fin de etapa y la junta decide (puede aprobar condicionado).
2. Reales y cobertura por la fachada (SPEC §1.16): `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen` y `listar requisitos --json` (FR de la etapa siguiente con historia y paquete). Ningún dato se extrae abriendo archivos de BMAD.
2b. Traspasos pendientes: cada entrada de `estado.json.integraciones.bmad.handoffs` sin confirmación del equipo BMAD se informa en el informe de fin de etapa; un traspaso aplicado exige `verificar` limpio antes de la nueva línea base.
3. Resultado del gate de preparación del sprint planning de BMAD (PASS/CONCERNS/FAIL): insumo de `autorizar-etapa`; CONCERNS o FAIL se presentan como riesgo o condición.
4. La nueva línea base del PRD (si cambió con aprobación) la fija `pm-director` tras la puerta (`bmad.py linea-base`).

## 9. Plan de excepción — detalle
Contenido: referencia al informe de excepción `X-###` y a la opción elegida por la junta, causa, alcance del plan (etapa o proyecto), qué cambia respecto del plan vigente (productos, paquetes, cronograma, presupuesto, tolerancias nuevas), impacto en business case y riesgos, y el resto de la composición de un plan, con el mismo nivel de detalle que el plan que reemplaza. Actualizar descripciones de producto, registro de productos y actividades de calidad. Si exige acciones fuera de la etapa, también cambia el plan de proyecto (y si supera tolerancias de proyecto, decide la capa de negocio). Opcionalmente, informe de fin de etapa de la etapa interrumpida. Si se aprueba, pasa a ser el plan de etapa vigente (`estado.py artefacto plan-etapa-<n> --ruta 02-planificacion/plan-excepcion-X-###.md --estado aprobado`, tras la puerta), con nuevo límite de etapa y nueva línea base; si se rechaza, la etapa sigue según la dirección de la junta hasta una versión revisada. No hay planes de excepción para planes de equipo.

## 10. Versión mínima vs. completa
| Elemento | Mínima (proyecto pequeño) | Completa |
|---|---|---|
| Planes | Un plan de proyecto que hace de plan de etapa; cronograma como lista de hitos | Plan de proyecto + plan detallado por etapa + planes de equipo opcionales |
| Tolerancias | Tiempo, costo y alcance; riesgo y cambio dentro de la tolerancia de costo | Siete dimensiones por nivel, presupuestos de riesgo y cambio separados |
| Informe de fin de etapa | Una página: productos aceptados, desviaciones, pronóstico, solicitud | Composición completa con revisión de desempeño y lecciones |
| Plan de excepción | Sección "qué cambia" + cronograma e hitos revisados | Mismo detalle que el plan reemplazado, PID actualizada |

## 11. Reglas complementarias
1. [PRINCE2] Siempre coexisten un plan de proyecto de alto nivel y un plan detallado de la etapa en curso; el de la siguiente se hace cerca del fin de la actual.
2. [PRINCE2] En cada límite se revisan los productos de línea base (business case, plan de proyecto, PID, equipo, enfoques).
3. [PRINCE2] El informe de fin de etapa se apoya en el registro de productos y el de calidad: entregados, aprobados, concesiones, pronóstico.
4. [PRINCE2] Las actividades de cierre se planifican dentro del plan de la etapa final.
5. [PMBOK→SB] Los criterios de salida de cada puerta se escriben como condiciones verificables.
6. Envío del paquete de fin de etapa a la junta por chat o correo solo con confirmación, vía `pm-integraciones`.
