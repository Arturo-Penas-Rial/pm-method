---
name: pm-okr
description: "OKR del proyecto ligados a beneficios (B-n) y métricas (SM-n): tipos de KR, check-ins, salud, cascada, Tability o Perdoo. Usar: OKR, key results, check-in, puntuar OKR. No: beneficios o business case→pm-caso-de-negocio."
version: 2.4.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-director
    procesos_prince2: [SU, IP, DP, SB, CP]
    practicas_prince2: [business-case, progress]
    tecnicas_pmbok: [indicadores clave de desempeño, medición de resultados, análisis de tendencias]
    artefactos: [okr.csv, okr.md]
    idiomas: [es, en]
---

# OKR del proyecto · Project OKRs

## Cuándo usar / When to use
- La organización gestiona por OKR y quiere ver cómo el proyecto contribuye a sus objetivos de negocio, sin crear un segundo business case.
- Hay que redactar, revisar o puntuar objetivos y resultados clave (KR) del proyecto o de un producto, o prepararlos para una puerta o una revisión de beneficios.
- El equipo de producto trabaja con métricas de éxito del PRD (SM-n) y la dirección pide leerlas como OKR.
- EN: write, link and score project OKRs against business-case benefits and PRD success metrics.
- EN: prepare the OKR view for a stage boundary or a post-project benefits review.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. La plantilla usa etiquetas bilingües y `idioma: "{{idioma}}"`. Cabecera de `okr.csv` en snake_case: `id` (id), `tipo` (type: objetivo|kr), `objetivo_id` (parent objective), `enunciado` (statement), `metrica` (metric), `linea_base` (baseline), `meta` (target), `actual` (current), `unidad` (unit), `responsable` (owner), `fecha_meta` (due date), `vinculo` (link: B-n, SM-n, OBJ-n), `confianza` (confidence 1–10), `notas` (notes). Opcionales: `tipo_kr` (de-a, mantener-sobre, mantener-bajo, binario, hito), `compromiso` (aspiracional, comprometido), `peso`, `padre_id` (cascada), `nivel`, `ciclo`, `fecha_inicio`, `estado`, `ref_externa`; `tipo=iniciativa` (IN-n) para el trabajo que mueve un KR. Check-ins en `okr_checkins.csv`.

## Conocimiento
- `references/guia.md` (este skill): §1 ubicación en PRINCE2, §2 redacción, §3 vínculos sin duplicar, §4 puntuación, §5 cadencia de revisión, §6 Tability, §7 BMAD, §8 casos borde.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` — buscar "Cadena de valor" (salidas → resultados → beneficios → objetivos de negocio) y "Enfoque de gestión de beneficios".
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` — técnicas de medición e indicadores (buscar "KPI" o "indicadores"), solo como cómo.
- `SPEC.md` §1.13 (dueño único: beneficios en el business case, SM-n en el PRD).

## Entradas requeridas
- `estado.json` y el business case (`business-case`) con objetivos de negocio numerados `OBJ-n` y beneficios `B-nn`. Si los objetivos no están numerados, proponer la numeración en el business case vía `pm-caso-de-negocio` (no en el OKR).
- Enfoque de gestión de beneficios (`enfoque-beneficios`) si existe: de ahí salen dueños, medidas y fechas de medición.
- **Especificación (fuente única, SPEC §1.16)**: métricas `SM-n` solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar requisitos` (igual con o sin BMAD; nunca abrir BMAD, `requisitos-bmad.csv` ni `requisitos.md`). Escribe como dueña: `00-direccion/okr.csv` y `okr.md`; los KR citan `B-nn`/`SM-n` por id, sin copiar texto.
- Responsables: id `ST-###` o nombre exacto del maestro de interesados (`pm-interesados`); `okr.py` avisa si no está.
- Opcional: herramienta OKR conectada (`integraciones.okr = tability|perdoo`, MCP oficiales) vía `pm-integraciones`.
- Si falta el responsable del objetivo, preguntar al orquestador quién es el ejecutivo o el usuario sénior que lo asume.

## Procedimiento
Script: `python3 ${CLAUDE_SKILL_DIR}/../pm-okr/scripts/okr.py <dir>/00-direccion/okr.csv ...` (en el plugin `${CLAUDE_PLUGIN_ROOT}/skills/pm-okr/scripts/okr.py`; en manual/Hermes, la carpeta instalada del skill).
1. **Encuadrar**: confirmar que se trata de un instrumento de la capa de negocio y no de un producto de gestión PRINCE2 (ver `references/guia.md` §1). Leer business case, enfoque de beneficios y los SM-n (fachada `especificacion.py`).
2. **Crear el registro**: si no existe, `okr.py --plantilla <dir>/00-direccion/okr.csv` (o copiar `templates/okr.csv`).
3. **Redactar objetivos** (O-n): cualitativos, uno a tres, cada uno con `vinculo=OBJ-n` y responsable = ejecutivo o usuario sénior. Criterios en `references/guia.md` §2.
4. **Redactar KR** (KR-n.m): dos a cinco por objetivo, medibles, con línea base y meta numéricas (o `tipo_kr` binario, hito o mantener), fecha, responsable del maestro, `compromiso` y `peso` si difieren del defecto; iniciativas `IN-n` ligadas al KR y a una épica, historia o paquete. **Cada KR cita un beneficio (`B-nn`) o una métrica de éxito (`SM-n`)**; si no hay ninguno que corresponda, falta un beneficio en el business case → derivar a `pm-caso-de-negocio`, no inventarlo aquí. Detalle en §3.
5. **No duplicar**: medida, línea base y fecha del beneficio viven en el business case; si el KR replica el mismo indicador, cópiese solo el valor de referencia y anótese la fuente en `notas` (§3).
6. **Narrativa**: completar `templates/okr.md` → `00-direccion/okr.md` (contexto, cadena OBJ→O→KR→B/SM, cadencia de revisión) y registrar `estado.py artefacto okr --ruta 00-direccion/okr.md --estado en-revision`.
7. **Check-in** periódico del responsable: `okr.py <csv> --checkin KR-n.m --valor <v> --confianza <1–10> --nota …` (solo se agrega; el historial alimenta la tendencia).
8. **Puntuar** en cada corte: `okr.py <csv> [--umbrales 0.7,0.4] [--corte AAAA-MM-DD] --markdown <dir>/03-control/reportes/<fecha>-okr.md`. Umbrales 0,7/0,4 (aspiracional) y 1,0/0,7 (comprometido): convención de la práctica OKR, **no** de PRINCE2 ni del PMBOK; declararlos. La **salud** compara la puntuación con el avance esperado entre `fecha_inicio` y `fecha_meta` (§4).
9. **Corregir avisos** del script (KR sin vínculo o sin línea base, verbo de actividad, responsable fuera del maestro, vencidos, más de cinco KR, todo en 1,0 al cierre): se resuelven con el responsable, no se ocultan.
10. **Revisar en los límites de etapa** (SB) y en las revisiones de beneficios posteriores al cierre (§5): la tabla puntuada se adjunta al informe de fin de etapa o al plan de revisión de beneficios. Un KR rojo que amenaza un beneficio se traslada como riesgo o issue y, si supera la tolerancia de beneficios, como excepción.
11. **Tability o Perdoo (opcional)**: `ref_externa` en cada KR; `okr.py <csv> --propuesta-sync tability|perdoo` lista los check-ins sin publicar con la herramienta MCP; publicar solo tras vista previa y confirmación y marcar con `--marcar-publicado KR@fecha --destino … --ref …`. Lectura: instantánea en `03-control/fuentes/` → check-in con `--fuente` (§6). Comunicar el resultado a los interesados con `envios.py nuevo --proposito okr`.
12. **Aprobación**: el objetivo y sus KR los acepta el ejecutivo (o el usuario sénior dueño del beneficio). Tras la decisión humana, `estado.py aprobar okr --por "<rol: nombre>"`. Si corre como subagente, devolver la aprobación como decisión humana requerida en el bloque de retorno.

## Reglas del método
1. [PRINCE2] Los OKR no son un producto de gestión PRINCE2 ni reemplazan al business case: lo leen y lo ilustran. La justificación continua se decide sobre el business case.
2. [PRINCE2] Cada objetivo O-n se ancla a un objetivo de negocio `OBJ-n`; cada KR, a un beneficio `B-nn` o a una métrica de éxito `SM-n`. Sin vínculo no hay KR.
3. [PRINCE2] Dueño: el ejecutivo (o el usuario sénior responsable del beneficio). El gestor del proyecto mantiene el registro, no fija las metas.
4. [PRINCE2] Revisión en cada límite de etapa y en las revisiones de beneficios tras el cierre; sin informes extra si todo está dentro de tolerancia (gestión por excepción).
5. [PRINCE2] Una caída de KR que pronostica salir de la tolerancia de beneficios es excepción: se escala a `pm-director`, no se reescribe la meta en silencio.
6. Dueño único del dato (SPEC §1.13): beneficios y su medición en el business case; SM-n en el PRD; `okr.csv` solo los cita.
7. [PMBOK→Progress/DP] La puntuación lineal (actual − base)/(meta − base) es una técnica de medición de resultados aplicada a la información de progreso para la junta; declarar fórmula y umbrales.
8. Un KR mide un resultado (outcome), no una tarea ni un entregable: "publicar el portal" es un producto del plan, no un KR.
9. Metas cambiadas tras la aprobación se registran como decisión (`registro.py agregar decisiones --campo nivel=junta`) con la versión anterior en `notas`.
10. [Plantillas] Versión mínima: un objetivo, dos o tres KR, sin narrativa extensa; completa si hay varios beneficios o varias unidades de negocio.
11. Transparencia de IA: el contenido generado es borrador; valores faltantes como `[por confirmar]`; cada `actual` cita su fuente.
12. Integraciones: Tability o Perdoo solo si están conectadas; `okr.csv` y los check-ins siguen siendo la fuente; escrituras externas solo con confirmación.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | estado.json |
|---|---|---|---|
| Registro de OKR | `templates/okr.csv` | `00-direccion/okr.csv` | — (registro) |
| Narrativa OKR | `templates/okr.md` | `00-direccion/okr.md` | `okr` |
| Check-ins (historial) | `okr.py --checkin` | `00-direccion/okr_checkins.csv` | — |
| Tabla puntuada por corte | `okr.py --markdown` | `03-control/reportes/<fecha>-okr.md` | — |
| Instantánea de Tability | `pm-integraciones` | `03-control/fuentes/tability-AAAA-MM-DD.csv` | — |

## Calidad
- [ ] Cada O-n tiene `OBJ-n` y responsable con rol de junta.
- [ ] Cada KR con tipo, línea base y meta (o hito/binario), fecha, responsable del maestro y vínculo B-nn o SM-n existente; check-ins al día.
- [ ] Ningún dato de beneficio duplicado sin citar su fuente.
- [ ] `okr.py` sin avisos pendientes o con cada aviso explicado.
- [ ] Umbrales declarados como convención y no como regla del método.
- [ ] Revisión agendada en el próximo límite de etapa y en el plan de revisión de beneficios.

## Escalamiento y excepciones
- KR sin beneficio o SM que lo respalde → `pm-caso-de-negocio` (agregar o ajustar beneficio) o `pm-bmad-puente` (SM).
- Pronóstico fuera de la tolerancia de beneficios → `pm-progreso-reportes` / `pm-issues-cambios` (informe de excepción) → `pm-director`.
- Cambio de metas aprobadas → decisión de la junta vía `pm-direccion-decisiones`.
- En subagente: aprobaciones y cambios de meta se devuelven como "decisiones humanas requeridas" (SPEC §1.11).

## Ejemplos de invocación
- "Armame los OKR del proyecto a partir de los beneficios del business case."
- "Puntuá los OKR al cierre de la etapa 2 con semáforo 0,8/0,5."
- EN: "Link our key results to the PRD success metrics and score them."
- EN: "Pull progress from Tability and update the OKR table for the board."
- No activa: "Calculá el VAN y el payback del proyecto" → `pm-caso-de-negocio`.

## EN summary
Business-layer OKR tool, not a PRINCE2 management product. Objectives link to business objectives (OBJ-n); every key result links to a business-case benefit (B-nn) or a PRD success metric (SM-n) without duplicating their data. Owned by the executive or senior user, reviewed at stage boundaries and in post-project benefits reviews. `okr.py` validates links and owners against the stakeholder master, scores KRs by type (from-to, stay above/below, binary, milestone with initiatives), weights, cascades objectives, keeps an append-only check-in history, computes health against expected progress and proposes check-ins to publish in Tability or Perdoo through their official MCP servers after confirmation.
