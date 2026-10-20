---
tipo: hipotesis-y-experimentos
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Hipótesis y experimentos · Validar antes de invertir / Hypotheses and experiments

> Toda idea de proyecto descansa en supuestos. Los que más afectan al business case y menos evidencia tienen son
> **hipótesis**: antes de pedir la inversión completa se validan con experimentos baratos y con un criterio acordado
> para seguir, ajustar o abandonar. Es la justificación continua de PRINCE2 aplicada antes de gastar. El registro
> vivo es `supuestos.csv` (columnas `criticidad`, `certeza`, `experimento`, `criterio`, `fecha_limite`, `evidencia`);
> este documento es la vista para la junta.

## 1. Idea y decisión que se quiere tomar / Idea and decision
**Idea en una frase:** {{idea}}
**Decisión que espera la junta / Decision expected:** {{decision}} *(p. ej. autorizar la iniciación, elegir una opción, invertir en la etapa 2)*
**Fecha de la decisión / Decision date:** {{fecha_decision}}

## 2. Supuestos que sostienen la idea / Assumptions behind the idea
*Tres preguntas, una fila por supuesto. **Deseabilidad**: ¿alguien lo quiere y lo va a usar? **Viabilidad**: ¿cierra
económicamente y para la organización? **Factibilidad**: ¿se puede construir y operar con lo que tenemos?*

| Id | Supuesto (si es falso, el caso cambia) | Tipo | Criticidad | Certeza hoy | Evidencia actual |
|---|---|---|---|---|---|
| S-001 | {{supuesto_1}} | deseabilidad | alta | baja | {{evidencia_1}} |
| S-002 | {{supuesto_2}} | viabilidad | alta | media | {{evidencia_2}} |
| S-003 | {{supuesto_3}} | factibilidad | media | baja | {{evidencia_3}} |

*Criticidad = cuánto cambia el business case si el supuesto es falso. Certeza = cuánta evidencia hay hoy. El cuadrante
**criticidad alta + certeza baja** es donde se invierte primero en aprender.*

## 3. Experimentos / Experiments
| Supuesto | Experimento (lo más barato que da evidencia) | Métrica y criterio para seguir | Costo · duración | Responsable | Fecha límite |
|---|---|---|---|---|---|
| S-001 | {{experimento_1}} *(p. ej. 8 entrevistas, prototipo en papel, landing con registro)* | {{criterio_1}} *(p. ej. ≥ 6 de 8 lo usarían semanalmente)* | {{costo_1}} | {{resp_1}} | {{fecha_1}} |
| S-002 | {{experimento_2}} | {{criterio_2}} | {{costo_2}} | {{resp_2}} | {{fecha_2}} |

*Un buen experimento: se decide antes qué resultado haría cambiar la decisión; es más barato que equivocarse; tiene
fecha. Si un supuesto no se puede validar a tiempo, se trata como riesgo (pm-riesgos) y la junta lo acepta explícitamente.*

## 4. Resultados y decisión / Results and decision
| Supuesto | Resultado | Evidencia (fuente, fecha) | Efecto en el business case | Decisión |
|---|---|---|---|---|
| S-001 | {{validado_1}} *(sí / no / parcial)* | {{evidencia_res_1}} | {{efecto_1}} | {{decision_1}} *(seguir / ajustar / abandonar)* |

**Recomendación a la junta / Recommendation:** {{recomendacion}}

## Lista de verificación / Checklist
- [ ] Cada supuesto crítico tiene experimento, criterio y fecha (sanidad SUP-01).
- [ ] Los vencidos sin resultado están replanificados o escalados (SUP-02).
- [ ] Los invalidados tienen su efecto tratado en el business case, un riesgo, un issue o una decisión (SUP-03).
- [ ] La puerta `autorizar-proyecto` no recibe supuestos críticos sin validar sin que la junta lo decida (condición P-11).
