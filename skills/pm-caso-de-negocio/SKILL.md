---
name: pm-caso-de-negocio
description: "Business case PRINCE2 y enfoques de beneficios y sostenibilidad. Usar: caso de negocio, business case, ROI, VAN/NPV, payback, beneficios. No: OKR→pm-okr; presupuesto→pm-costos-presupuesto."
version: 2.2.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-inicio
    procesos_prince2: [SU, IP, DP, SB, CP]
    practicas_prince2: [business-case, progress]
    tecnicas_pmbok: [NPV, IRR, payback, ROI, análisis de sensibilidad, análisis de alternativas, EMV, modelo multi-caso]
    artefactos: [business-case, business-case-esquematico, enfoque-beneficios, enfoque-sostenibilidad]
    idiomas: [es, en]
---

# Caso de negocio y beneficios · Business case and benefits

## Cuándo usar / When to use
- Arranque (SU): **business case esquemático** (outline business case) dentro del project brief, para autorizar la iniciación.
- Iniciación (IP, etapa 1): **business case completo** con tiempo y costo del plan, **enfoque de beneficios** (benefits management approach) y **enfoque de sostenibilidad** (sustainability management approach).
- En cada puerta (fin de etapa, excepción, cierre): **verificar** si sigue deseable, viable y alcanzable y **actualizar** con reales y previsiones.
- EN: outline or full business case, benefits and sustainability approaches; continued justification at gates.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Etiquetas bilingües en plantillas; términos EN entre paréntesis la primera vez ("des-beneficio (dis-benefit)"). Fórmulas con variables en inglés técnico (`NPV`, `CF_t`, `r`).

## Conocimiento
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §2 (cadena de valor, tres atributos, técnica de cuatro pasos, multi-caso, sostenibilidad).
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §2.1 (justificación continua), §5.2, §5.6, §5.7; `prince2-practicas-riesgo-issues-progreso-productos.md` §5.4 A1.
- `pm-knowledge/references/plantillas-inicio-y-planes.md` §2.2 (ficha del business case).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.9, §3.2, §3.11, §5.1 (técnica por pregunta).
- `references/guia.md`: modos y versionado (§1), técnicas (§2), una página (§3), SM-n y KR (§4), reglas extendidas (§5), ejemplo (§6), casos borde (§7).

## Entradas requeridas
- `estado.json` (fase y proceso definen el modo); si no existe, `pm-estado-proyecto`.
- Esquemático: mandato, propuesta o brief, `lecciones.csv`. Completo: esquemático aprobado, `02-planificacion/plan-proyecto.md`, `riesgos.csv`, roles (usuario sénior = dueño de beneficios). Verificar/mantener: versión anterior, `03-control/reportes/`, reales.
- Datos de la organización: tasa de descuento, horizonte, moneda, política de inversiones, compromisos ESG; si faltan, preguntar una vez y marcar `[por confirmar]`.
- **Especificación (fuente única, SPEC §1.16)**: métricas `SM-n` solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar requisitos` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: beneficios `B-##` que citan ids, sin copiar texto. KR: `00-direccion/okr.csv` (`pm-okr`), si existe.

## Procedimiento
1. **Leer el estado** y fijar el modo: `esquematico` (SU), `completo` (IP), `verificar` (puerta), `mantener` (fin de etapa), `confirmar` (cierre). Anunciar modo y versión (ver `references/guia.md` §1).
2. **Reunir y citar fuentes**: cada cifra con origen; lo demás `[por confirmar]` con su rol (costos: proveedor sénior; beneficios: usuario sénior; financiación: ejecutivo).
3. **Cadena de valor**: salida → capacidad → resultado → beneficio → objetivo de negocio, con habilitadores y des-beneficios. Beneficio no medible → reformular o excluir de la evaluación.
4. **Vincular métricas sin duplicar** (si existen): cada beneficio `B-##` cita en la columna "Refs SM / KR" los `SM-n` del PRD y los KR de `okr.csv` que lo miden; meta, línea base, dueño y tolerancia siguen siendo del business case. Reglas y casos en `references/guia.md` §4.
5. **Opciones de negocio**: "no hacer nada distinto" (base), "hacer lo mínimo", "hacer más"; tabla de ventajas, desventajas, costo y riesgo; recomendación razonada.
6. **Evaluar la inversión** con la técnica que pide la pregunta (`references/guia.md` §2); supuestos y fórmulas en el documento; sensibilidad si un beneficio sostiene > 50 % del valor.
7. **Tolerancias** de beneficios y sostenibilidad: proponerlas; tras confirmación de la capa de negocio, `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> tolerancia --nivel proyecto beneficios="-10 %" sostenibilidad="..."`. Las de etapa las fija la junta vía `pm-director`.
8. **Redactar el business case** → `templates/business-case.md` en `00-direccion/business-case.md` (esquemático: secciones marcadas; resto `[en inicio]`). Perfil ágil mínimo: versión de una página (`references/guia.md` §3).
9. **Enfoque de beneficios** (completo) → `templates/enfoque-beneficios.md` en `00-direccion/enfoque-beneficios.md`: dueño, medida, línea base, fecha, método, revisiones intermedias, financiación post-cierre, Refs SM / KR.
10. **Enfoque de sostenibilidad** (completo; en mínima, sección del caso) → `templates/enfoque-sostenibilidad.md` en `00-direccion/enfoque-sostenibilidad.md`.
11. **Siete aspectos de desempeño** (beneficios, costo, tiempo, calidad, alcance, riesgo, sostenibilidad): si no cierran en tolerancia, la justificación es cuestionable y el resumen ejecutivo lo dice.
12. 🔒 **Puerta humana**: dejar `en-revision` (`estado.py artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision --version 0.9`) y derivar a `pm-director`; la junta decide en `autorizar-inicio` (esquemático) o `autorizar-proyecto` (completo, versión 1.0 = línea base). Solo `pm-director` registra la puerta y ejecuta `estado.py aprobar business-case ...`. Copias congeladas en `00-direccion/historial/`.
13. **Verificar (puerta)**: deseable / viable / alcanzable con la información nueva; veredicto continuar / cambiar / detener; previsión fuera de tolerancia → datos para informe de excepción (`pm-issues-cambios`) y `pm-director`. Si se usan SM-n o KR, citar su última medición como evidencia.
14. **Mantener (fin de etapa)** y **confirmar (cierre)**: ver `references/guia.md` §1.
15. **Cerrar** con estado, `[por confirmar]` con rol y siguiente puerta; como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas, nunca sin puertas. En ágil, beneficios como rango ligado al alcance entregado.
2. [PRINCE2] Previsión fuera de tolerancia (incluidos beneficios y sostenibilidad) → excepción; nunca ajustar supuestos para que el caso cierre.
3. [PRINCE2] Nada se aprueba sin acto humano registrado; el caso pasa a 1.0 solo tras `autorizar-proyecto`; esta skill nunca ejecuta `estado.py puerta`.
4. [PMBOK→Business case/IP] Técnica según la pregunta (`pmbok8-artefactos-tecnicas-anexos.md` §5); supuestos y fórmulas declarados (tasa, horizonte, moneda, base). Tasas no provistas por la organización, `[por confirmar]`.
5. [Plantillas] Versión mínima (dos opciones, beneficios netos, payback) para proyectos pequeños; completa (multi-caso, tabla por opción, anexos) cuando riesgo, costo o interesados lo justifiquen.
6. Transparencia de IA: borrador, sin datos inventados, cada cifra con fuente. Idioma del usuario.
7. Escrituras externas solo con confirmación explícita, vía `pm-integraciones`.
8. [PRINCE2] Deseable, viable y alcanzable se responden por separado.
9. [PRINCE2] "No hacer nada distinto" es siempre la primera opción y la base de comparación.
10. [PRINCE2] Todo beneficio es medible, con línea base, dueño, fecha y tolerancia; los des-beneficios son consecuencias esperadas (no riesgos) y se restan.
11. [PRINCE2] El ejecutivo rinde cuentas del caso; el usuario sénior, de la realización de beneficios, también tras el cierre.
12. [PRINCE2] La versión que autorizó el proyecto se conserva intacta; cada fin de etapa produce otra comparable.
13. Dueño único (SPEC §1.13, §1.16): beneficios, metas y tolerancias viven aquí; `SM-n` y KR de `pm-okr` se **citan** como medida, nunca se copian ni redefinen.
14. [Plantillas] Ids propios `B-##`, `DB-##`, `MS-##`; nunca prefijos de registros (R, I, C, D, S, L, ST, Q, A).
Más reglas: `references/guia.md` §5.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | Clave |
|---|---|---|---|
| Business case | `templates/business-case.md` | `00-direccion/business-case.md` (+ `historial/`) | `business-case`, `business-case-esquematico` |
| Enfoque de beneficios | `templates/enfoque-beneficios.md` | `00-direccion/enfoque-beneficios.md` | `enfoque-beneficios` |
| Enfoque de sostenibilidad | `templates/enfoque-sostenibilidad.md` | `00-direccion/enfoque-sostenibilidad.md` | `enfoque-sostenibilidad` |
| Tolerancias de beneficios y sostenibilidad | propuestas en el caso; las registra pm-director (`estado.py tolerancia --nivel proyecto`) al aprobarse | `estado.json.tolerancias.proyecto` | campo raíz |
| Veredicto de justificación continua | sección "Verificación" + fila en `decisiones.csv` | `00-direccion/business-case.md` | `business-case` (nueva versión) |

## Calidad
- [ ] Modo y versión coherentes con `estado.json`.
- [ ] Cadena de valor completa; habilitadores y des-beneficios señalados.
- [ ] ≥ 3 opciones incluida "no hacer nada distinto"; recomendación razonada.
- [ ] Beneficios con línea base, dueño, fecha y tolerancia; Refs SM / KR citadas si existen, sin definiciones copiadas.
- [ ] Costos con operación y mantenimiento; técnica por pregunta con fórmulas; sensibilidad y EMV cuando corresponde.
- [ ] Deseable / viable / alcanzable por separado; siete aspectos en tolerancia o cuestionamiento explícito.
- [ ] Sostenibilidad con metas y tolerancias trazables a ESG (o no aplicabilidad declarada).
- [ ] Toda cifra con fuente; resumen ejecutivo cruzado contra tablas; versión anterior en `historial/`.
- [ ] Solo tolerancias de nivel proyecto (ninguna de etapa).

## Escalamiento y excepciones
- Previsión fuera de tolerancia → datos para informe de excepción y `pm-director`.
- Caso que no cierra en los siete aspectos → pedir decisión de la junta (cambiar opción, redefinir alcance o detener).
- Usuario sénior no identificado → `pm-organizacion-roles` y `pm-director` antes de completar.
- `SM-n` o KR que contradicen la meta de un beneficio → hallazgo; con PRD en línea base, posible `solicitud-cambio` (`pm-issues-cambios`); no alinear en silencio.
- Programa, cliente–proveedor, saltar la verificación: `references/guia.md` §7.
- Como subagente: decisiones humanas (opción, tolerancias, veredicto) en el bloque de retorno, no preguntadas desde el subagente.

## Ejemplos de invocación
- "Armá el business case esquemático a partir del mandato; todavía no tenemos costos firmes."
- "Cerramos la etapa 2: actualizá el caso con reales y vinculá los beneficios a las métricas SM del PRD."
- EN: "Compare 'do nothing', 'minimum fix' and 'full replacement' for billing and recommend one."
- EN: "We're agile with a fixed budget: one-page business case with benefits per MoSCoW scenario."
- No activa: "Definí los OKR del trimestre y sus resultados clave" → `pm-okr`.

## EN summary
PRINCE2 business case as a living product: outline (SU), full (IP), check at every gate, maintain at stage boundaries, confirm at closure. Builds the value chain, compares options starting with "do nothing different", picks the appraisal technique by the question and writes assumptions. Benefits are measurable with baseline, owner, date and tolerance; they may cite PRD success metrics (SM-n) and OKR key results (pm-okr) as measures without duplicating them. pm-director records the approval gate.
