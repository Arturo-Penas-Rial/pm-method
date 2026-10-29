---
tipo: evaluacion-excepcion
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
excepcion: "{{id_excepcion}}"
issue_origen: "{{id_issue}}"
informe_excepcion: "{{ruta_informe_excepcion}}"
---

# Evaluación de excepción para la junta · Exception assessment for the board

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Evalúa el informe de excepción del gestor y ordena las opciones de la junta. No decide: la decisión corresponde a la junta o, si se exceden tolerancias de proyecto, a la capa de negocio.

**Proyecto / Project:** {{proyecto}} · **Etapa / Stage:** {{etapa}}
*Según estado.json.*

**Excepción / Exception:** {{id_excepcion}} · **Issue de origen / Originating issue:** {{id_issue}} · **Informe de excepción / Exception report:** {{ruta_informe_excepcion}}
*X-### es el id del informe (no de un registro). Ruta: `03-control/reportes/<fecha>-informe-excepcion-X-###.md`, preparado por pm-control con la plantilla de pm-issues-cambios. Ruta de esta evaluación: `00-direccion/decisiones/AAAA-MM-DD-evaluacion-excepcion-X-###.md`.*

**Decisión que se pide / Decision requested:** {{decision_solicitada}}
*Una frase. Primero la decisión, después el contexto.*

**Urgencia / Urgency:** {{urgencia}}
*Fecha a partir de la cual la falta de decisión empeora el impacto. Si es urgente: comunicación verbal primero, escrita después.*

## 1. ¿Es realmente una excepción? / Is it really an exception?

| Nivel / Level | Tolerancia vigente / Current tolerance | Pronóstico / Forecast | ¿Superada? / Exceeded? | Fuente / Source |
|---|---|---|---|---|
| Paquete de trabajo / Work package | {{tol_wp}} | {{pron_wp}} | {{sup_wp}} | {{fuente_wp}} |
| Etapa / Stage | {{tol_etapa}} | {{pron_etapa}} | {{sup_etapa}} | {{fuente_etapa}} |
| Proyecto / Project | {{tol_proyecto}} | {{pron_proyecto}} | {{sup_proyecto}} | {{fuente_proyecto}} |

*Comparar pronóstico, no acumulado. Si solo se supera la de paquete, el gestor resuelve y no hay excepción de etapa: devolver con esa indicación. Si se supera la de proyecto, la junta debe escalar a la capa de negocio.*

**Conclusión / Conclusion:** {{conclusion_nivel}}
*"Excepción de etapa: decide la junta" · "Excepción de proyecto: decide la capa de negocio" · "No es excepción: devolver al gestor".*

## 2. Resumen del informe de excepción / Exception report summary

**Desviación / Deviation:** {{desviacion}}
*Qué objetivo(s) y cuánto, en unidades.*

**Causa / Cause:** {{causa}}
*Causa raíz verificada, no el síntoma.*

**Consecuencias de no actuar / Consequences of no action:** {{consecuencias}}
*Para el proyecto y para la organización.*

**Impacto sobre el business case / Impact on business case:** {{impacto_bc}}
*Beneficios, costos, plazos, exposición al riesgo: antes → después.*

**Recomendación del gestor / Project manager's recommendation:** {{recomendacion_gestor}}
*Copiar el enunciado del informe; no reinterpretarlo.*

## 3. Opciones de la junta / Board options

| Opción / Option | Efecto en tiempo / Time | Costo / Cost | Alcance / Scope | Beneficios / Benefits | Riesgo / Risk | Requiere plan de excepción / Needs exception plan | Autoridad / Authority |
|---|---|---|---|---|---|---|---|
| A. Reasignar tolerancias y aceptar la desviación / Reassign tolerances, accept deviation | {{a_t}} | {{a_c}} | {{a_a}} | {{a_b}} | {{a_r}} | No | {{a_aut}} |
| B. Repriorizar o reducir alcance / Reprioritize or reduce scope | {{b_t}} | {{b_c}} | {{b_a}} | {{b_b}} | {{b_r}} | Según magnitud | {{b_aut}} |
| C. Pedir plan de excepción / Request exception plan | {{c_t}} | {{c_c}} | {{c_a}} | {{c_b}} | {{c_r}} | Sí | {{c_aut}} |
| D. Pedir más tiempo para decidir / Defer decision | {{d_t}} | {{d_c}} | {{d_a}} | {{d_b}} | {{d_r}} | No | {{d_aut}} |
| E. Cierre prematuro / Premature closure | {{e_t}} | {{e_c}} | {{e_a}} | {{e_b}} | {{e_r}} | No (va a CP) | {{e_aut}} |

*Al menos una opción sin plan de excepción y una con él. Autoridad: junta · capa de negocio · autoridad de cambio. Cuantificar en unidades; "sin impacto" cuando corresponda para dejar constancia de que se consideró.*

**Técnica usada para comparar / Technique used:** {{tecnica}}
*Análisis de alternativas, multicriterio con pesos explícitos, árbol de decisión con EMV. Declarar pesos y fórmulas. Con matriz: pegar el bloque de `decision.py matriz <ID> --markdown` (tipo `cambio` o `planificacion`; hoja `03-control/decisiones/<ID>/`, guía §13) con la sensibilidad de los pesos.*

## 4. Recomendación / Recommendation

**Opción recomendada / Recommended option:** {{opcion_recomendada}} · **Grado de confianza / Confidence:** {{confianza}}
*Letra, enunciado y alta/media/baja.*

**Justificación / Rationale:** {{justificacion}}
*Por qué protege mejor la justificación continua.*

**Si se pide plan de excepción / If an exception plan is requested:** {{instrucciones_plan}}
*Flujo: pm-director registra `estado.py puerta decision-ad-hoc --decision aprobado --por ".."` (pedido de plan de excepción) y `estado.py limite-etapa --excepcion X-###` (CS → SB); pm-planificacion prepara `02-planificacion/plan-excepcion-X-###.md`, que reemplaza al plan vigente; la junta lo decide en `autorizar-plan-excepcion`. Intentar alinear el nuevo fin de etapa con el original.*

**Lección propuesta / Proposed lesson:** {{leccion}}
*Qué esperábamos, qué ocurrió, qué funcionó, qué no, qué cambiar. Va a lecciones.csv al cerrar la excepción.*

## 5. Decisión pendiente de aprobación humana / Decision pending human approval

> Requiere decisión de **{{quien_decide}}**. Tras la decisión, pm-director registra `estado.py puerta decision-ad-hoc ...` (escribe la fila en `decisiones.csv`, nivel `junta`; si decidió la capa de negocio, agregar con `registro.py` la fila de nivel `capa-negocio`), actualiza el issue {{id_issue}} y, si se pidió plan de excepción, ejecuta `estado.py limite-etapa --excepcion {{id_excepcion}}`. Si se elige cierre prematuro: `estado.py cierre --prematuro` y derivar a pm-cierre.

## Lista de verificación / Checklist
- [ ] Se verificó el nivel de tolerancia superado con pronóstico y fuente; conclusión explícita.
- [ ] Causa raíz y consecuencias de no actuar están escritas en unidades.
- [ ] Al menos cinco opciones, con una sin plan de excepción y una con él; autoridad indicada por opción.
- [ ] Impacto sobre el business case antes/después con fuente.
- [ ] Recomendación con grado de confianza; la del gestor se cita sin alterar.
- [ ] Lección propuesta para el cierre de la excepción.
- [ ] Bloque de decisión pendiente con el rol que decide.
