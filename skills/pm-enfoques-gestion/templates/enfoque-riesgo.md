---
tipo: enfoque-riesgo
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enfoque de gestión de riesgos · Risk management approach — {{proyecto}}

> Procedimiento, técnicas, escalas, tolerancias, presupuesto y responsabilidades para gestionar amenazas y oportunidades. Parte del PID. Mapeo del paquete: ≈ plan de gestión de riesgos (risk management plan). Lo prepara el gestor; lo aprueba el ejecutivo; lo acuerdan usuario y proveedor sénior. / How threats and opportunities will be identified, assessed, planned, implemented and communicated.

**Versión mínima / Minimal version:** {{version_minima}}
*`sí` (una página): escala 1–5 con definiciones de una línea (la misma que usa `registro.py`; no se usa 3×3 para no romper los umbrales), zonas por defecto, categorías básicas, cadencia de revisión y dueño del registro; los riesgos se informan en el highlight report.*

## 1. Alcance / Scope

{{alcance}}
*A qué se aplica: proyecto completo, etapas, paquetes de trabajo de proveedores (y cómo se integran sus riesgos).*

## 2. Procedimiento / Procedure

| Paso / Step | Qué se hace / What is done | Quién / Who | Cuándo / When | Herramienta / Tool |
|---|---|---|---|---|
| Identificar / Identify | {{identificar}} | {{identificar_quien}} | {{identificar_cuando}} | {{identificar_herr}} |
| Evaluar / Assess | {{evaluar}} | {{evaluar_quien}} | {{evaluar_cuando}} | {{evaluar_herr}} |
| Planificar respuestas / Plan | {{planificar}} | {{planificar_quien}} | {{planificar_cuando}} | {{planificar_herr}} |
| Implementar / Implement | {{implementar}} | {{implementar_quien}} | {{implementar_cuando}} | {{implementar_herr}} |
| Comunicar / Communicate | {{comunicar}} | {{comunicar_quien}} | {{comunicar_cuando}} | {{comunicar_herr}} |

*Toda desviación del procedimiento corporativo de riesgos se señala y justifica como adaptación. En ágil, identificar y revisar también en la planificación de iteración y en la retrospectiva.*

## 3. Escalas de valoración / Rating scales

**Probabilidad / Probability (1–5):**

| Nivel / Level | Etiqueta / Label | Definición operativa / Operational definition |
|---|---|---|
| 1 | Muy baja / Very low | {{prob_1}} |
| 2 | Baja / Low | {{prob_2}} |
| 3 | Media / Medium | {{prob_3}} |
| 4 | Alta / High | {{prob_4}} |
| 5 | Muy alta / Very high | {{prob_5}} |

*Rangos porcentuales o de frecuencia definidos por la organización. Convención del paquete para el valor esperado: 1 → 10 %, 2 → 30 %, 3 → 50 %, 4 → 70 %, 5 → 90 % (configurable; si se cambia, decirlo aquí).*

**Impacto por objetivo / Impact by objective (1–5):**

| Nivel / Level | Tiempo / Time | Costo / Cost | Alcance / Scope | Calidad / Quality | Beneficios / Benefits | Sostenibilidad / Sustainability |
|---|---|---|---|---|---|---|
| 1 | {{imp1_tiempo}} | {{imp1_costo}} | {{imp1_alcance}} | {{imp1_calidad}} | {{imp1_beneficios}} | {{imp1_sost}} |
| 3 | {{imp3_tiempo}} | {{imp3_costo}} | {{imp3_alcance}} | {{imp3_calidad}} | {{imp3_beneficios}} | {{imp3_sost}} |
| 5 | {{imp5_tiempo}} | {{imp5_costo}} | {{imp5_alcance}} | {{imp5_calidad}} | {{imp5_beneficios}} | {{imp5_sost}} |

*Rangos con cifras (semanas de retraso en el camino crítico, porcentaje de sobrecosto, funciones afectadas). Niveles 2 y 4 por interpolación. Al menos tiempo y costo definidos.*

**Proximidad y velocidad / Proximity and velocity:** {{proximidad}}
*Cómo se usa la cercanía temporal (p. ej. riesgos a menos de un mes suben un nivel) y la rapidez con que el impacto se materializa.*

## 4. Matriz y puntuación / Matrix and scoring

**Puntuación / Score:** probabilidad × impacto (1–25), la misma que calcula `registro.py` en `riesgos.csv`.

| Zona / Zone | Rango de puntuación / Score range | Tratamiento / Treatment |
|---|---|---|
| Baja / Low | ≤ 5 (por defecto) {{zona_baja}} | {{zona_baja_trat}} |
| Media / Medium | 6–12 (por defecto) {{zona_media}} | {{zona_media_trat}} |
| Alta / High | ≥ 15 (por defecto) {{zona_alta}} | {{zona_alta_trat}} |

**Valor esperado / Expected monetary value (EMV):** `valor_esperado = impacto_monetario × probabilidad (%)`; oportunidades con signo positivo, amenazas negativo. Sirve para dimensionar la reserva de contingencia.

**Riesgo residual / Residual risk:** `probabilidad_residual` × `impacto_residual` tras la respuesta; un riesgo alto solo se considera tratado si su residual baja de 15 o la junta acepta el residual por escrito. **Disparador / Trigger:** señal observable que indica que el riesgo está por ocurrir (columna `disparador`).

*Los umbrales por defecto del paquete (alto ≥ 15, medio 6–12, bajo ≤ 5) son configurables aquí; si se cambian, avisar a `pm-estado-proyecto` porque `registro.py` y el tablero los usan. Riesgos en zona alta se informan a la junta en el highlight report; los que amenazan tolerancias disparan excepción.*

## 5. Categorías / Categories

{{categorias}}
*Técnicos, externos, organizacionales, de gestión, comerciales, de sostenibilidad… Deben permitir clasificar todos los riesgos sin que domine "otros". Base de una estructura de desglose de riesgos si se usa.*

## 6. Apetito y tolerancia de riesgo / Risk appetite and tolerance

**Apetito de la organización / Organisational appetite:** {{apetito}}
*Cuánta incertidumbre acepta el negocio a cambio de beneficio, por objetivo.*

**Tolerancia de riesgo del proyecto / Project risk tolerance:** {{tolerancia_proyecto}}
*Umbral agregado o por riesgo que, de superarse, se escala; copiado del business case y de `estado.json.tolerancias.proyecto.riesgo`. Línea de tolerancia por defecto: ningún riesgo alto (≥ 15) abierto sin respuesta y propietario; opcionalmente, tope de EMV agregado de amenazas.*

**Tolerancia por etapa / Stage tolerance:** {{tolerancia_etapa}}
*La fija la junta al autorizar cada etapa.*

## 7. Presupuesto de riesgo y reservas / Risk budget and reserves

| Reserva / Reserve | Monto o % / Amount or % | Para qué / Purpose | Quién libera / Released by | Cómo se informa / Reported how |
|---|---|---|---|---|
| Contingencia / Contingency | {{contingencia}} | riesgos identificados; respuestas planificadas (forma parte del BAC) | gestor dentro de tolerancia | {{contingencia_informe}} |
| Gestión / Management | {{reserva_gestion}} | imprevistos dentro del alcance (fuera del BAC) | junta | {{reserva_gestion_informe}} |

*Contingencia ≠ reserva de gestión; presupuesto autorizado = BAC + reserva de gestión. No sumar contingencia dentro de cada paquete y otra vez por etapa. Si se usa valor monetario esperado (EMV) para dimensionar, escribir la fórmula y los riesgos incluidos.*

## 8. Respuestas y roles / Responses and roles

**Tipos de respuesta / Response types:** {{tipos_respuesta}}
*Para amenazas: evitar, reducir, transferir, aceptar, preparar contingencia; para oportunidades: explotar, mejorar, compartir, aceptar. Declarar las que se usarán.*

| Rol / Role | Responsabilidad / Responsibility |
|---|---|
| Ejecutivo / Executive | {{resp_ejecutivo}} |
| Junta / Board | {{resp_junta}} |
| Gestor de proyecto / Project manager | {{resp_gestor}} |
| Dueño del riesgo / Risk owner | {{resp_dueno}} |
| Ejecutor de la respuesta / Action owner | {{resp_ejecutor}} |
| Gestores de equipo / Team managers | {{resp_gestores_equipo}} |
| Aseguramiento / Assurance | {{resp_aseguramiento}} |
| Soporte / Support | {{resp_soporte}} |

*Todo riesgo tiene dueño y ejecutor; nunca se cierra sin notas.*

## 9. Cadencia y actividades formales / Cadence and formal activities

{{cadencia}}
*Revisión del registro (p. ej. quincenal), reevaluación completa en cada fin de etapa, taller de identificación al inicio de etapa, auditoría del proceso de riesgos si aplica, vigilancia del entorno externo (quién).*

## 10. Registro de riesgos y reportes / Risk register and reporting

**Formato del registro / Register format:** `03-control/registros/riesgos.csv` — {{formato_registro}}
*Columnas según `pm-estado-proyecto`; valores de probabilidad e impacto 1–5; estados permitidos.*

**Reportes / Reporting:** {{reportes}}
*Qué va al highlight report (riesgos altos, nuevos, cambios de puntuación, uso de reservas), al informe de fin de etapa y al de excepción.*

## 11. Herramientas, técnicas y referencias / Tools, techniques and references

{{herramientas_referencias}}
*Talleres, listas de verificación, pre-mortem, análisis de sensibilidad, sistema corporativo de riesgos, procedimiento del proveedor.*

## Lista de verificación / Checklist
- [ ] Escalas con definiciones operativas (cifras o rangos), impacto al menos para tiempo y costo.
- [ ] Puntuación = probabilidad × impacto, igual a la del registro.
- [ ] Zonas de la matriz con tratamiento (por defecto alto ≥ 15, medio 6–12, bajo ≤ 5); EMV con la convención de probabilidades; residual y disparador definidos.
- [ ] Categorías que cubren todos los riesgos conocidos.
- [ ] Apetito y tolerancia por objetivo, coherentes con el business case y `estado.json`.
- [ ] Reservas con tamaño, criterio y autoridad de liberación; contingencia separada de gestión.
- [ ] Todo paso del procedimiento con rol; dueño y ejecutor por riesgo.
- [ ] Cadencia compatible con el enfoque de entrega; ágil: iteración y retrospectiva.
- [ ] Desviaciones del estándar corporativo justificadas.
- [ ] Estado `borrador` hasta la aprobación del ejecutivo.
