---
tipo: evaluacion-probabilidad-impacto
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: "{{aprobado_por}}"
idioma: "{{idioma}}"
---

# Evaluación de probabilidad e impacto · Probability and impact assessment

**Proyecto / Project:** {{proyecto}}
*Nombre del proyecto según `estado.json`.*

**Aprobado por / Approved by:** {{ejecutivo}}
*El ejecutivo del proyecto fija las escalas y la línea de tolerancia; hasta su aprobación este documento es una propuesta.*

**Apetito de riesgo declarado / Stated risk appetite:** {{apetito}}
*Actitud cualitativa de la organización hacia el riesgo (por ejemplo: conservador en costo, abierto en alcance). Copiar del caso de negocio o del mandato.*

**Tolerancia de riesgo del proyecto / Project risk tolerance:** {{tolerancia_riesgo}}
*Umbral medible sobre la exposición agregada de amenazas (puntuación total, EMV total o cantidad de riesgos en zona roja). Copiar de `estado.json.tolerancias.riesgo`.*

**Tipo de puntuación / Scoring type:** {{tipo_puntuacion}}
*`lineal 1–5` (por defecto; `puntuacion = probabilidad × impacto`, rango 1–25) o `no lineal` (probabilidad 0,1–0,9 × impacto 0,05–0,80). Declarar cuál se usa.*

## 1. Escala de probabilidad / Probability scale

| Nivel / Level | Etiqueta ES | Label EN | Banda de referencia / Reference band | Descripción / Description |
|---|---|---|---|---|
| 1 | Muy baja | Very low | {{p1_banda}} | {{p1_desc}} |
| 2 | Baja | Low | {{p2_banda}} | {{p2_desc}} |
| 3 | Media | Medium | {{p3_banda}} | {{p3_desc}} |
| 4 | Alta | High | {{p4_banda}} | {{p4_desc}} |
| 5 | Muy alta | Very high | {{p5_banda}} | {{p5_desc}} |

*Bandas de referencia habituales: 1–20 %, 21–40 %, 41–60 %, 61–80 %, > 80 %. Deben ser excluyentes y cubrir 0–100 %; ajustarlas al proyecto.*

## 2. Escalas de impacto por objetivo / Impact scales by objective

| Nivel / Level | Tiempo / Time | Costo / Cost | Alcance / Scope | Calidad / Quality | Beneficios / Benefits | Sostenibilidad / Sustainability |
|---|---|---|---|---|---|---|
| 1 Muy bajo / Very low | {{i1_tiempo}} | {{i1_costo}} | {{i1_alcance}} | {{i1_calidad}} | {{i1_beneficios}} | {{i1_sostenibilidad}} |
| 2 Bajo / Low | {{i2_tiempo}} | {{i2_costo}} | {{i2_alcance}} | {{i2_calidad}} | {{i2_beneficios}} | {{i2_sostenibilidad}} |
| 3 Medio / Medium | {{i3_tiempo}} | {{i3_costo}} | {{i3_alcance}} | {{i3_calidad}} | {{i3_beneficios}} | {{i3_sostenibilidad}} |
| 4 Alto / High | {{i4_tiempo}} | {{i4_costo}} | {{i4_alcance}} | {{i4_calidad}} | {{i4_beneficios}} | {{i4_sostenibilidad}} |
| 5 Muy alto / Very high | {{i5_tiempo}} | {{i5_costo}} | {{i5_alcance}} | {{i5_calidad}} | {{i5_beneficios}} | {{i5_sostenibilidad}} |

*Expresar cada celda en las unidades del objetivo (días o % de duración; moneda o % del presupuesto; productos afectados; criterios de aceptación incumplidos; % de beneficio perdido; métrica de sostenibilidad). Valores de referencia para tiempo y costo: < holgura, 1–5 %, 5–10 %, 10–20 %, > 20 %. Las columnas que no apliquen se dejan vacías y se indica por qué.*

**Regla multi-objetivo / Multi-objective rule:** {{regla_multiobjetivo}}
*Cuando un riesgo afecta varios objetivos: tomar el impacto máximo (conservador, por defecto) o una suma ponderada por criticidad; declarar cuál.*

## 3. Escala de proximidad / Proximity scale

| Valor en CSV | Etiqueta ES | Label EN | Horizonte / Horizon |
|---|---|---|---|
| inminente | Inminente | Imminent | {{prox_inminente}} |
| corto-plazo | Corto plazo | Short term | {{prox_corto}} |
| mediano-plazo | Mediano plazo | Medium term | {{prox_mediano}} |
| largo-plazo | Largo plazo | Long term | {{prox_largo}} |

*Referencia: dentro del período de informe actual; dentro de la etapa; en la etapa siguiente; después. La proximidad se evalúa aparte del impacto para evitar el sesgo de cercanía.*

## 4. Matriz probabilidad × impacto / Probability × impact matrix

| P \ I | 1 Muy bajo | 2 Bajo | 3 Medio | 4 Alto | 5 Muy alto |
|---|---|---|---|---|---|
| **5 Muy alta** | 5 · {{z_5_1}} | 10 · {{z_5_2}} | 15 · {{z_5_3}} | 20 · {{z_5_4}} | 25 · {{z_5_5}} |
| **4 Alta** | 4 · {{z_4_1}} | 8 · {{z_4_2}} | 12 · {{z_4_3}} | 16 · {{z_4_4}} | 20 · {{z_4_5}} |
| **3 Media** | 3 · {{z_3_1}} | 6 · {{z_3_2}} | 9 · {{z_3_3}} | 12 · {{z_3_4}} | 15 · {{z_3_5}} |
| **2 Baja** | 2 · {{z_2_1}} | 4 · {{z_2_2}} | 6 · {{z_2_3}} | 8 · {{z_2_4}} | 10 · {{z_2_5}} |
| **1 Muy baja** | 1 · {{z_1_1}} | 2 · {{z_1_2}} | 3 · {{z_1_3}} | 4 · {{z_1_4}} | 5 · {{z_1_5}} |

*Cada celda muestra la puntuación y la zona (`verde`, `ambar`, `rojo`). Al usarla como fotografía del período, reemplazar la zona por los ids de los riesgos ubicados en la celda (amenazas con `R-###`, oportunidades con `R-###+`).*

## 5. Reglas de calificación y línea de tolerancia / Rating rules and tolerance line

| Calificación / Rating | Regla en escala 1–5 / Rule (1–5 scale) | Tratamiento / Treatment |
|---|---|---|
| Alto / High (rojo) | puntuación ≥ {{umbral_alto}} | {{trat_alto}} |
| Medio / Medium (ámbar) | {{umbral_medio_min}} ≤ puntuación < {{umbral_alto}} | {{trat_medio}} |
| Bajo / Low (verde) | puntuación < {{umbral_medio_min}} | {{trat_bajo}} |

*Valores por defecto del paquete (SPEC §1.10.9, configurables): alto ≥ 15, medio 6–12, bajo ≤ 5 (en escala 1–5 no existen puntuaciones 13 ni 14). Son los que usan `registro.py resumen` y el tablero; si se cambian, declararlo en cada informe. Tratamiento habitual: alto → respuesta activa con hoja de datos y revisión cada período; medio → respuesta y revisión cada período; bajo → aceptar y vigilar.*

**Línea de tolerancia de riesgo / Risk tolerance line:** {{linea_tolerancia}}
*Por defecto: ningún riesgo alto (≥ 15) abierto sin respuesta y sin propietario; el gestor refiere a la junta (escala) todo riesgo alto que no pueda cumplirlo, salvo decisión registrada. Puede endurecerse (p. ej. ningún riesgo ≥ 15 abierto) si el ejecutivo lo aprueba.*

**Matriz de oportunidades / Opportunity matrix:** {{matriz_oportunidades}}
*`misma matriz con marcador +` (por defecto) o `matriz espejo separada`. Las oportunidades sobre la línea también se llevan a la junta, como decisiones de explotar o mejorar.*

## 6. Exposición agregada / Aggregate exposure

**Indicador elegido / Chosen indicator:** {{indicador_exposicion}}
*`suma de puntuaciones de riesgos abiertos`, `conteo en zona roja` o `Σ EMV amenazas − Σ EMV oportunidades`. Debe ser comparable con `tolerancias.etapa.riesgo` y `tolerancias.proyecto.riesgo`.*

**Conversión de probabilidad / Probability mapping:** 1 → {{p1_pct}} · 2 → {{p2_pct}} · 3 → {{p3_pct}} · 4 → {{p4_pct}} · 5 → {{p5_pct}}
*Por defecto 10 / 30 / 50 / 70 / 90 %, la que usa `registro.py` para calcular `valor_esperado`; si se cambia, recalcular a mano y anotarlo.*

**Fórmula EMV / EMV formula:** EMV = probabilidad (fracción) × impacto monetario (columnas `impacto_monetario` → `valor_esperado`); EMV residual con `probabilidad_residual` e impacto monetario residual; beneficio de una respuesta = EMV_antes − EMV_después; se justifica si el costo de la respuesta es menor que ese beneficio.
*Convertir el nivel 1–5 a fracción con las bandas de la sección 1 (punto medio de la banda) y declararlo.*

## 7. Cadencia y responsabilidades / Cadence and responsibilities

| Actividad / Activity | Frecuencia / Frequency | Responsable / Owner |
|---|---|---|
| Revisión de riesgos abiertos | {{cad_revision}} | {{resp_revision}} |
| Actualización de la matriz y comparación con el período anterior | {{cad_matriz}} | {{resp_matriz}} |
| Revisión formal en límite de etapa | cada límite de etapa | gestor del proyecto + aseguramiento |
| Autorización de uso del presupuesto de riesgo | a demanda | {{resp_presupuesto}} |
| Auditoría de riesgos | {{cad_auditoria}} | {{resp_auditoria}} |

*En ágil o híbrido: revisión en la planificación y la retrospectiva de cada iteración; la matriz se actualiza al menos una vez por período de informe.*

## Lista de verificación / Checklist
- [ ] Bandas de probabilidad excluyentes y completas.
- [ ] Escalas de impacto definidas para cada objetivo relevante, en sus unidades.
- [ ] Regla multi-objetivo declarada.
- [ ] Tipo de puntuación declarado y coherente con `registro.py` (lineal 1–5 por defecto).
- [ ] Umbrales de calificación y línea de tolerancia coherentes con el apetito y con `tolerancias.riesgo`.
- [ ] Tratamiento de oportunidades definido.
- [ ] Cadencia compatible con el enfoque de entrega.
- [ ] Aprobación del ejecutivo registrada en `decisiones.csv` y en `estado.json.artefactos.evaluacion-probabilidad-impacto` (vía `estado.py aprobar`).
