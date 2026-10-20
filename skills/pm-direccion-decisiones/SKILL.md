---
name: pm-direccion-decisiones
description: "Decisiones de la junta: puertas, tolerancias, excepciones. Usar: aprobar etapa, autorizar proyecto, junta, excepción, board decision, stage gate. No: anotar riesgos o issues→pm-registros."
version: 2.3.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: direccion
    agente: pm-director
    procesos_prince2: [DP, SB, CS, CP]
    practicas_prince2: [business-case, organizing, plans, issues, progress]
    tecnicas_pmbok: [análisis de alternativas, análisis multicriterio, árbol de decisión con EMV, guardarraíles de IA]
    artefactos: [solicitud-<puerta>, tolerancias-y-autoridad, evaluacion-excepcion, acta-junta, decisiones.csv, estado.json.puertas, linea-base bmad-*]
    idiomas: [es, en]
---

# Dirección y decisiones de la junta · Directing a project and board decisions

## Cuándo usar / When to use
- El proyecto llega a una **puerta**: autorizar el inicio (fin de SU), el proyecto y su primera etapa (fin de IP), una etapa siguiente o un plan de excepción (SB), el cierre (CP).
- Llega un **informe de excepción** o una solicitud de dirección ad hoc (consejo, issue escalado, cambio sobre la autoridad delegada, cambio del mandato).
- Hay que fijar **tolerancias** por nivel o la **autoridad delegada** (autoridad y presupuesto de cambio).
- EN: prepare a gate decision request, assess an exception report, set tolerances and delegated authority.
- EN: record a board decision once a named board member has decided.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma`. Primera mención con el término EN: solicitud de decisión de puerta (gate decision request), plan de excepción (exception plan), autoridad de cambio (change authority). Plantillas bilingües.

## Conocimiento
- `references/guia.md`: §1 productos por puerta, §2 registro, §3 tolerancias, §4 excepciones, §5 ad hoc, §6 cierre, §7 mapa, §8 BMAD, §9 reglas, §10 columnas.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` — `### 5.2` (Directing a project), `### 6.3`–`### 6.10` (junta, roles, matriz de decisiones), `## 8.` (reglas de gobierno).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` — `### 4.c` (tolerancias y excepciones), `## 6.` (flujo de excepciones), `### 7.3`/`### 7.6` (escalado, informe de excepción).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` — `### 3.4` (decisiones), `### 5.3` (guardarraíles IA).
- `SPEC.md` §1.10.4 (puertas), §1.13 (BMAD).

## Entradas requeridas
- `estado.json` (fase, proceso, etapa, tolerancias, roles, puertas previas); si falta, `pm-estado-proyecto`.
- Productos de la puerta (guía §1). Faltante o en `borrador` = bloqueante declarado; `en-revision` es aceptable para lo que la puerta decide.
- Excepción: `03-control/reportes/<fecha>-informe-excepcion-X-###.md` de `pm-control` (si solo hay relato, registrar el issue y pedirlo).
- Registros vía `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py`; estado vía `estado.py` (SPEC §1.10.1), siempre con `--proyecto <dir>`.
- Ejecutivo nombrado en `estado.json.roles.ejecutivo`; si está vacío, preguntarlo (o devolverlo como dato faltante) antes de preparar nada.
- Con `integraciones.especificacion = bmad`: `${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py`. Ningún conector es obligatorio.

## Procedimiento
1. **Situar la puerta**: `estado.py ver` y `siguiente`; tipo (`autorizar-inicio|proyecto|etapa|plan-excepcion|cierre`, `decision-ad-hoc`). Fase incoherente con los artefactos → regularizar primero.
2. **Justificación continua**: con el business case vigente (y `00-direccion/historial/business-case-v1.0.md`), responder con evidencia: ¿deseable?, ¿viable?, ¿alcanzable? Un "no" o `[por confirmar]` → recomendación por defecto: no autorizar y proponer replanteo o cierre prematuro ordenado.
3. **Productos requeridos** (guía §1): ruta, versión, estado, aprobador; `paquete.py --proyecto <dir> listar puerta <tipo>`.
4. **Checklist de la puerta**: desempeño contra tolerancias de etapa y proyecto (`registro.py resumen`, `listar … --abiertos`, último `evm.py`); condiciones previas cumplidas; **con BMAD, `bmad.py verificar` limpio o cada desvío tratado como `solicitud-cambio`** y PRD/épicas en el estado que exige la puerta (guía §8). Solo lo que requiere atención.
5. **Solicitud de decisión** (`templates/solicitud-puerta.md`): justificación · productos · desempeño · riesgos e issues · opciones (aprobar, condicionar, rechazar, pedir información; cierre prematuro) con consecuencias cuantificadas · recomendación con confianza · rol que decide. Guardar `en-revision` en `00-direccion/decisiones/AAAA-MM-DD-solicitud-<puerta>.md` y `estado.py artefacto solicitud-<puerta> …`. ZIP: `pm-exportar`.
6. **🔒 Puerta humana**: presentar al rol que decide (ejecutivo con la junta; capa de negocio si toca tolerancias de proyecto). Nada se registra sin respuesta explícita de una persona con nombre y rol. Como subagente, la pregunta va en "Decisiones humanas requeridas" del bloque de retorno; el orquestador la presenta y vuelve a invocar a pm-director con la respuesta.
7. **Registrar** (solo pm-director, tras el paso 6; guía §2): `estado.py puerta <tipo> --decision .. --por "<rol: nombre>" [--condiciones ..]` (escribe `decisiones.csv`); `estado.py aprobar <clave>` por documento; en `autorizar-proyecto`, congelar PID y business case v1.0; **con BMAD, `bmad.py --proyecto <dir> linea-base prd --version 1.0 --por "<rol: nombre>"`** (y demás especificaciones aprobadas); en `autorizar-etapa`, `tolerancia --nivel etapa`; acta (`templates/acta-decision-junta.md`); condiciones como acciones A-### y `cumplir-condiciones`.
8. **Tolerancias y autoridad** (guía §3): siete objetivos con unidades; `templates/tolerancias-y-autoridad.md`; 🔒 ejecutivo confirma; `estado.py tolerancia`, `rol autoridad_cambio=..`, `presupuesto cambio=.. riesgo=.. limite_autoridad_cambio=..` (sanidad CAM), fila en `decisiones.csv`.
9. **Excepción** (guía §4): verificar que supera la tolerancia de etapa (si supera la de proyecto, escalar a la capa de negocio); `templates/evaluacion-excepcion.md` con opciones cuantificadas; 🔒 decisión; `puerta decision-ad-hoc`; si se pide plan, `estado.py limite-etapa --excepcion X-###` y encargo a `pm-plan-etapa-y-limites`; luego `autorizar-plan-excepcion`.
10. **Ad hoc** (guía §5); **cierre** (guía §6). **Comunicar** vía `pm-comunicacion-stakeholders`; cerrar con el siguiente paso o el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas, nunca sin puertas.
2. [PRINCE2] Toda desviación prevista fuera de tolerancia se escala; nunca se absorbe en silencio.
3. [PRINCE2] Nada se da por aprobado sin acto humano explícito registrado (`estado.py puerta` + `decisiones.csv`; documentos con `estado.py aprobar`).
4. [PRINCE2] Solo pm-director registra puertas y fija líneas base (incluida la de BMAD con `bmad.py linea-base`), siempre después de la decisión humana.
5. [PRINCE2] El agente prepara, presenta y registra; nunca aprueba, rechaza ni condiciona en nombre de una persona.
6. [PRINCE2] Gestión por excepción: dentro de tolerancia no se piden informes extra; sin ejecutivo nombrado no hay puerta.
7. [PRINCE2] Cada puerta verifica primero la justificación continua; recomendar cierre prematuro es un resultado legítimo.
8. [PRINCE2] Escalada por niveles: paquete → gestor; etapa → junta; proyecto → capa de negocio.
9. [PRINCE2] Tolerancias explícitas (tiempo y costo como mínimo) antes de autorizar cualquier etapa; las de etapa caben en las de proyecto.
10. [PRINCE2] PID y business case v1.0 se congelan al autorizar el proyecto; el cierre compara contra ellos.
11. [PRINCE2] Con BMAD, un desvío del PRD con línea base es una solicitud de cambio que decide la autoridad de cambio PRINCE2; la aprobación dentro de BMAD no la sustituye.
12. [PMBOK→DP] Técnica según la pregunta (alternativas, multicriterio, árbol de decisión con EMV); toda recomendación con grado de confianza y fuente de cada cifra (`[por confirmar]` si falta).
13. [Plantillas] Versión mínima (una página) o completa según riesgo, costo y stakeholders; una decisión reabierta no se borra (guía §9).
14. Escrituras externas (tracker, correo, chat) solo con confirmación explícita, vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Solicitud de decisión de puerta | `templates/solicitud-puerta.md` | `00-direccion/decisiones/AAAA-MM-DD-solicitud-<puerta>.md` | `solicitud-<puerta>` |
| Tolerancias y autoridad delegada | `templates/tolerancias-y-autoridad.md` | `00-direccion/tolerancias-y-autoridad.md` | `tolerancias.*`, `roles.autoridad_cambio`, `tolerancias-y-autoridad` |
| Evaluación de excepción | `templates/evaluacion-excepcion.md` | `00-direccion/decisiones/AAAA-MM-DD-evaluacion-excepcion-X-###.md` | `evaluacion-excepcion-X-###` |
| Acta de decisión de la junta | `templates/acta-decision-junta.md` | `00-direccion/decisiones/AAAA-MM-DD-acta-junta-<puerta>.md` | `acta-junta-<fecha>`; `puertas[]` |
| Líneas base congeladas (PID, business case, BMAD) | copia / `bmad.py linea-base` | `00-direccion/historial/` | `aprobado`; `bmad-prd` … |
| Fila de decisión de puerta o aprobación | `estado.py puerta` / `aprobar` | `03-control/registros/decisiones.csv` | `puertas[].decision_id` |
| Condiciones | `registro.py agregar acciones` + `cumplir-condiciones` | `03-control/registros/acciones.csv` | `puertas[].condiciones_cumplidas` |

## Calidad
- [ ] Justificación continua con evidencia citada (ruta y versión).
- [ ] Productos requeridos con estado y aprobador; faltantes declarados bloqueantes.
- [ ] Al menos tres opciones (incluida "no autorizar") con consecuencias cuantificadas.
- [ ] Recomendación con grado de confianza; ninguna cifra sin fuente.
- [ ] Rol que decide nombrado (ejecutivo/junta; capa de negocio si excede tolerancias de proyecto).
- [ ] Con BMAD: `bmad.py verificar` limpio o desvíos tratados; línea base fijada solo tras la decisión.
- [ ] Tras la decisión: puerta sin filas duplicadas, documentos aprobados, acta, condiciones como acciones, historial v1.0 (proyecto) y tolerancias de etapa (etapa).

## Escalamiento y excepciones
- Pronóstico fuera de tolerancia de **proyecto** → escalada a la capa de negocio; registrar con `nivel=capa-negocio`.
- Junta sin posición unificada → decide el ejecutivo; discrepancia en `notas`.
- Pedido de saltar una puerta → explicar el riesgo; si la persona con rol insiste, `--forzar` con motivo.
- `estado.py puerta` rechaza `aprobado` si `puertas.py` encuentra bloqueos (salud, controles PRINCE2 y BMAD, lista de control de la junta sin confirmar): corregir o registrar `condicionado` (los bloqueos pasan a condiciones); `--forzar` queda anotado. Criterios por puerta: `docs/PUERTAS.md`.
- Informe de excepción sin pasar por `pm-control` → completarlo con la plantilla de `pm-issues-cambios`.
- Plan de excepción → `pm-plan-etapa-y-limites`; business case en duda → `pm-caso-de-negocio`.
- Como subagente: las decisiones humanas se devuelven en el bloque de retorno (SPEC §1.11); nunca se preguntan desde el subagente ni se suponen.

## Ejemplos de invocación
- "Preparame la solicitud de decisión para autorizar la etapa 2 del proyecto Faro."
- "Llegó un informe de excepción: el proveedor se atrasa 6 semanas. ¿Qué opciones tiene la junta?"
- EN: "Prepare the closure authorization request for project Harbour MVP."
- EN: "The board approved the PRD at the gate; baseline it and record the decision."
- No activa: "Anotá este riesgo del proveedor" → `pm-registros` (o `pm-riesgos` para analizarlo).

## EN summary
Governance skill for PRINCE2 Directing a project, run by pm-director. It prepares gate decision requests (continued justification, required products, tolerance performance, with BMAD a clean `bmad.py verificar`), presents quantified options with a confidence-rated recommendation and, only after a named person decides, records the gate, approvals, frozen baselines (PID, business case, `bmad.py linea-base`), stage tolerances and conditions. It also sets tolerances and assesses exception reports.
