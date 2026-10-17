# Guía del caso de negocio · Business case guide

## 1. Modos y versionado
| Modo | Proceso | Qué se hace | Versión |
|---|---|---|---|
| esquematico | SU | secciones marcadas "esquemático" del business case; resto `[en inicio]`; dentro del project brief o aparte | 0.x; al aprobarse en `autorizar-inicio` se congela como `00-direccion/historial/business-case-esquematico.md` (no es línea base) |
| completo | IP (etapa 1) | todas las secciones con tiempo y costo del plan de proyecto y riesgo agregado; enfoques de beneficios y sostenibilidad | 0.9 en revisión; **1.0** al aprobarse en `autorizar-proyecto` = línea base, congelada en `00-direccion/historial/business-case-v1.0.md` |
| verificar | DP (cada puerta) | deseable / viable / alcanzable con información nueva; veredicto continuar / cambiar / detener en tres líneas con evidencia | sin cambio de versión salvo que se actualice |
| mantener | SB (fin de etapa) | productos entregados, costos reales, beneficios realizados, previsiones; actualizar enfoques de beneficios y sostenibilidad | 1.1, 1.2…; la anterior queda intacta para comparar |
| confirmar | CP y post-proyecto | real vs. esquemático original; beneficios realizados; traspaso del enfoque de beneficios al usuario sénior con financiación de revisiones; lecciones sobre beneficios no logrados y efectos colaterales | versión final del proyecto |

Puerta humana: el ejecutivo revisa (rinde cuentas del caso); el usuario sénior confirma beneficios; el proveedor sénior confirma costos y viabilidad; aseguramiento verifica alineación con políticas. `pm-director` registra la puerta con `estado.py puerta ...` y, con aprobación explícita, `estado.py aprobar business-case --por "Ejecutivo: <nombre>" --version 1.0`.

## 2. Técnica de evaluación según la pregunta
| Pregunta de la junta | Técnica | Cuándo no alcanza |
|---|---|---|
| ¿En cuánto tiempo recuperamos lo invertido? | Payback simple | beneficios después del horizonte |
| ¿Crea valor considerando el tiempo del dinero? | NPV con tasa de la organización | tasa desconocida → `[por confirmar]` y rango de tasas |
| ¿Qué rendimiento tiene frente a otras inversiones? | IRR o ROI | flujos con cambios de signo (IRR ambigua) |
| ¿Depende todo de un supuesto? | Sensibilidad (tornado simple) | obligatoria si un beneficio aporta > 50 % del valor |
| ¿Es mandatorio o estratégico, sin retorno monetario claro? | Multi-caso (estratégico, económico, financiero, implementación/comercial) | — |
| ¿Cuánto valen los riesgos principales? | EMV = impacto monetario × probabilidad (1–5 → 10/30/50/70/90 %) | riesgos no cuantificables → descripción cualitativa |
| Alcance flexible (ágil/híbrido) | Escenarios mejor / esperado / peor | — |

En proyectos obligatorios se comparan igualmente maneras de cumplir. El EMV de riesgos se refleja como reserva de contingencia en `pm-costos-presupuesto` (dentro del BAC, no como reserva de gestión).

## 3. Business case de una página (perfil ágil mínimo, SPEC §1.10.12)
Cuando `enfoque_entrega=agil` y el proyecto no supera el umbral de inversión. Se completa el bloque "Versión de una página" de `templates/business-case.md` más el resumen ejecutivo:
- **Costo fijo, alcance variable**: costo = iteraciones × costo por iteración (equipo estable) + licencias e infraestructura; fecha y presupuesto fijos, el alcance se negocia.
- **Beneficios como rango** por escenario: "solo Must" (pesimista), "Must + Should" (esperado), "todo" (optimista). El caso sigue válido mientras los Must entren.
- **Justificación en puertas**: en cada `autorizar-etapa`, ¿los Must de la próxima release entran con el presupuesto restante? (lectura ágil del EAC, SPEC §1.10.7); si no, excepción.
- Sin enfoque de beneficios separado: la tabla nombra dueño y primera fecha de medición; el enfoque completo se escribe antes del cierre si hay beneficios post-proyecto.

## 4. Beneficios, métricas de éxito del PRD (SM-n) y OKR
**Principio**: un dato, un dueño (SPEC §1.13). El beneficio (qué mejora, meta, línea base, dueño, tolerancia) es del business case; la métrica de éxito del producto `SM-n` es del PRD BMAD; el resultado clave es de `okr.csv` (`pm-okr`). Se enlazan por id.

| Situación | Qué se hace |
|---|---|
| Una `SM-n` mide exactamente el beneficio | Columna "Refs SM / KR" = `SM-n`; la medida del beneficio dice "según SM-n (PRD)"; la meta y la tolerancia siguen en el caso |
| La `SM-n` es un indicador adelantado (uso, adopción) de un beneficio monetario | Citarla como habilitador o medida intermedia en la cadena de valor y en las revisiones intermedias del enfoque de beneficios |
| Un KR del trimestre contribuye al beneficio | Citar el id del KR; el OKR es alineación estratégica, no reemplaza a la medida del beneficio |
| Hay `SM-n` sin beneficio asociado | Normal (métricas de producto): no se agregan como beneficios salvo que el usuario sénior lo decida |
| Beneficio sin `SM-n` ni KR | Normal: se mide con el método del enfoque de beneficios |
| Meta del caso y meta de la `SM-n` o del KR difieren | Hallazgo: reportar ambas rutas; si el PRD tiene línea base, el cambio de `SM-n` es `solicitud-cambio` (`pm-issues-cambios`); el OKR lo ajusta su dueño con `pm-okr` |

Coherencia con `okr.csv`: cada KR ya declara en su columna `vinculo` el `B-n` o `SM-n` al que contribuye (lo valida `okr.py`). La columna "Refs SM / KR" del caso es la vista inversa: si un KR apunta a `B-01`, `B-01` debe citar ese KR; una diferencia es un hallazgo, no se corrige en silencio.

Obtención de ids: `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> requisitos` (filas tipo `SM` en `02-planificacion/especificacion/requisitos-bmad.csv`); KR desde `00-direccion/okr.csv` (o `okr.py` de `pm-okr`). Nunca copiar texto de definición; solo id y, si ayuda, un rótulo de cinco palabras.

En verificación de puerta y en confirmación de cierre, la última medición de la `SM-n` (informe de avance o fuente conectada vía `pm-integraciones`) o del KR se cita como evidencia del beneficio, con fecha y fuente.

## 5. Reglas extendidas
1. [PRINCE2] Empezar por un esbozo suficiente para decidir si vale la pena planificar; no autorizar el proyecto con un caso en esbozo.
2. [PRINCE2] Los costos incluyen producir los productos, gestionar el proyecto y operación y mantenimiento posteriores, según la política de la organización.
3. [PRINCE2] La cadena salidas → resultados → beneficios es visible a todo el equipo; los productos habilitadores se identifican.
4. [PRINCE2] Los beneficios se verifican al menos al fin de cada etapa; con entregas iterativas, revisiones intermedias.
5. [PRINCE2] El enfoque de beneficios dice quién financia las mediciones post-cierre.
6. [PRINCE2] Metas de sostenibilidad con tolerancias, trazables a compromisos ESG; si el beneficio llega en décadas, complementar el flujo descontado con multi-caso.
7. [PMBOK→Business case] Sensibilidad obligatoria cuando un beneficio sostiene más de la mitad del valor; ese beneficio se protege en planificación, control y riesgo.
8. [Plantillas] El resumen ejecutivo se escribe al final y se cruza contra las tablas.
9. [PMBOK→Business case/SB] Perfil ágil mínimo: costo y fecha fijos con alcance variable; la justificación se pierde solo si los Must dejan de entrar.

## 6. Ejemplo trabajado
Opción 2 "reemplazar el sistema de facturación": inversión 120 k en el año 0; ahorro neto 45 k/año durante 4 años; tasa 10 % `[por confirmar]`. NPV = −120 + 45/1,1 + 45/1,21 + 45/1,331 + 45/1,4641 ≈ −120 + 40,9 + 37,2 + 33,8 + 30,7 = **+22,6 k**; payback ≈ 2,7 años. Sensibilidad: con ahorro de 38 k/año el NPV ≈ 0 → tolerancia de beneficios −15 % e informe en cada highlight. R-004 (migración) impacto 30 k, probabilidad 3 → EMV = 15 k → contingencia en `pm-costos-presupuesto`.
Con BMAD y OKR: B-01 "reducir el tiempo de emisión de factura de 3 días a 4 h" cita `SM-2` (PRD: tiempo medio de emisión) y `KR-1.2` (OKR del trimestre: 80 % de facturas el mismo día). La meta (4 h) y la tolerancia (+2 h) quedan en el caso; si el PRD cambiara `SM-2` a "6 h", `bmad.py verificar` lo detecta y se trata como solicitud de cambio.

## 7. Casos borde
- Proyecto dentro de un programa → el caso cubre lo que el programa no; beneficios gestionados a nivel programa, documentado.
- Relación cliente–proveedor → casos separados; secciones confidenciales; el ejecutivo verifica compatibilidad.
- Intento de saltar la verificación en una puerta → explicar la justificación continua, pedir confirmación explícita y registrar la excepción al método en `decisiones.csv`.
- Datos financieros en un sistema conectado (ERP, hoja compartida) → leer vía `pm-integraciones`, guardar instantánea fechada en `03-control/fuentes/` y citarla.
