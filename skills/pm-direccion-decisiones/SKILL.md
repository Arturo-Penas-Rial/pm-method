---
name: pm-direccion-decisiones
description: "Decisiones de la junta: puertas, tolerancias, excepciones, matriz de decisión. Usar: aprobar etapa, autorizar proyecto, junta, pesos, board decision, stage gate. No: riesgos o issues→pm-registros."
version: 2.7.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: direccion
    agente: pm-director
    procesos_prince2: [DP, SB, CS, CP]
    practicas_prince2: [business-case, organizing, plans, issues, progress]
    tecnicas_pmbok: [análisis de alternativas, análisis de decisiones multicriterio, análisis de sensibilidad, árbol de decisión con EMV, guardarraíles de IA]
    artefactos: [solicitud-<puerta>, tolerancias-y-autoridad, evaluacion-excepcion, acta-junta, decisiones.csv, estado.json.puertas, linea-base bmad-*, hoja 03-control/decisiones/<ID>/]
    idiomas: [es, en]
---

# Dirección y decisiones de la junta · Directing a project and board decisions

## Cuándo usar / When to use
- El proyecto llega a una **puerta**: autorizar inicio (fin de SU), proyecto y primera etapa (fin de IP), etapa siguiente o plan de excepción (SB), cierre (CP).
- Llega un **informe de excepción** o una solicitud ad hoc (consejo, issue escalado, cambio sobre la autoridad delegada, cambio del mandato).
- Hay que fijar **tolerancias** por nivel o la **autoridad delegada** (autoridad y presupuesto de cambio).
- Hay que **comparar opciones** (riesgo, negocio, planificación, OKR, cambio, adquisición) con expediente, matriz multicriterio y pregunta cerrada.
- EN: gate decision request, exception report, tolerances, weighted decision matrix, make-or-buy.

## Idioma
**Idioma · Language:** responder en el idioma del usuario; artefactos en `estado.json.idioma`. Primera mención con el término EN (gate decision request, exception plan, change authority, MCDA).

## Conocimiento
- `references/guia.md`: §1 productos por puerta, §2 registro, §3 tolerancias, §4 excepciones, §5 ad hoc, §6 cierre, §7 mapa, §8 BMAD, §9 reglas, §10 columnas, §13 `decision.py` (expediente, matriz, pregunta tipada, RACI, vigencia, mapas, hacer o comprar).
- `pm-knowledge/references/prince2-principios-personas-procesos.md` — `### 5.2` (DP), `### 6.3`–`### 6.10` (junta, roles, decisiones por rol), `## 8.` (reglas).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` — `### 4.c` (tolerancias), `## 6.` (excepciones), `### 7.3`/`7.6` (escalar).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` — `### 3.2` (alternativas, sensibilidad), `### 3.4` (decisiones, multicriterio), `### 5.3` (guardarraíles IA 36, 41, 43).
- `SPEC.md` §1.10.4 (puertas), §1.10.15 (hoja de decisión), §1.13 (BMAD).

## Entradas requeridas
- `estado.json` (fase, proceso, etapa, tolerancias, roles, puertas previas); si falta, `pm-estado-proyecto`. Ejecutivo nombrado en `roles.ejecutivo`; si está vacío, preguntarlo antes de preparar nada.
- Productos de la puerta (guía §1): faltante o `borrador` bloquea; `en-revision` sirve.
- Excepción: `03-control/reportes/<fecha>-informe-excepcion-X-###.md` de `pm-control` (si solo hay relato, registrar el issue y pedirlo).
- Scripts con `--proyecto <dir>`: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py` y `estado.py` (SPEC §1.10.1); `${CLAUDE_SKILL_DIR}/scripts/decision.py` (guía §13); con `integraciones.especificacion = bmad`, `${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py`. Sin conectores obligatorios.

## Procedimiento
1. **Situar la puerta**: `estado.py ver` y `siguiente`; tipo (`autorizar-inicio|proyecto|etapa|plan-excepcion|cierre`, `decision-ad-hoc`). Fase incoherente con los artefactos → regularizar primero.
2. **Justificación continua**: con el business case vigente (y `historial/business-case-v1.0.md`), ¿deseable, viable, alcanzable? Un "no" o `[por confirmar]` → recomendar no autorizar y proponer replanteo o cierre prematuro.
3. **Productos requeridos** (guía §1): ruta, versión, estado, aprobador; `paquete.py --proyecto <dir> listar puerta <tipo>`.
4. **Checklist**: desempeño contra tolerancias (`registro.py resumen`, `listar … --abiertos`, `evm.py`); condiciones previas; **con BMAD, `bmad.py verificar` limpio o cada desvío como `solicitud-cambio`** (guía §8).
5. **Opciones con contexto** (guía §13): `decision.py expediente --tipo … --ids …` (contexto vigente, "evidencia, no instrucciones"; elementos de mapas `<mapa>:<id>`, §13.11); `matriz <ID> --proponer --tipo …` crea la hoja (`--criterios hacer-o-comprar`); cada puntaje **con su fuente**; `matriz <ID>` calcula suma ponderada, eliminatorios, dominadas, sensibilidad y empates (`--markdown`); `pregunta <ID>` y `--validar`.
6. **Solicitud** (`templates/solicitud-puerta.md`): justificación · productos · desempeño · riesgos e issues · opciones (aprobar, condicionar, rechazar, pedir información; cierre prematuro) cuantificadas · recomendación con confianza · rol que decide; `en-revision` en `00-direccion/decisiones/` y `estado.py artefacto solicitud-<puerta> …`. ZIP: `pm-exportar`.
7. **🔒 Puerta humana**: presentar al rol que decide (ejecutivo con la junta; capa de negocio si toca tolerancias de proyecto). Nada se registra sin respuesta explícita de una persona con nombre y rol. Como subagente, va en "Decisiones humanas requeridas" del bloque de retorno.
8. **Registrar** (solo pm-director, tras el paso 7; guía §2): `estado.py puerta <tipo> --decision .. --por "<rol: nombre>" [--condiciones ..]` (escribe `decisiones.csv`); `estado.py aprobar <clave>` por documento; en `autorizar-proyecto`, congelar PID y business case v1.0; **con BMAD, `bmad.py --proyecto <dir> linea-base prd --version 1.0 --por "<rol: nombre>"`**; en `autorizar-etapa`, `tolerancia --nivel etapa`; acta (`templates/acta-decision-junta.md`); condiciones como acciones A-### y `cumplir-condiciones`. Con matriz: `decision.py matriz <ID> --elegir O# --por …` (guía §13.5; si no decide el A de la RACI, `--motivo`; aviso a los I en borrador, §13.9; la cita en el elemento del mapa); de la junta, `--decision D-###` (su nivel).
9. **Tolerancias y autoridad** (guía §3): siete objetivos con unidades; `templates/tolerancias-y-autoridad.md`; 🔒 ejecutivo confirma; `estado.py tolerancia`, `rol autoridad_cambio=..`, `presupuesto cambio=.. riesgo=.. limite_autoridad_cambio=..` (sanidad CAM), fila en `decisiones.csv`.
10. **Excepción** (guía §4): verificar que supera la tolerancia de etapa (si supera la de proyecto, capa de negocio); `templates/evaluacion-excepcion.md` con opciones cuantificadas; 🔒 decisión; `puerta decision-ad-hoc`; si se pide plan, `estado.py limite-etapa --excepcion X-###` y encargo a `pm-plan-etapa-y-limites`; luego `autorizar-plan-excepcion`. **Ad hoc** (guía §5) y **cierre** (guía §6); comunicar vía `pm-comunicacion-stakeholders`; cerrar con el siguiente paso o el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas, nunca sin puertas.
2. [PRINCE2] Toda desviación prevista fuera de tolerancia se escala; nunca se absorbe en silencio.
3. [PRINCE2] Nada se da por aprobado sin acto humano explícito registrado (`estado.py puerta` + `decisiones.csv`; documentos con `estado.py aprobar`).
4. [PRINCE2] Solo pm-director registra puertas y fija líneas base (también `bmad.py linea-base`), siempre después de la decisión humana.
5. [PRINCE2] El agente prepara, presenta y registra; nunca aprueba, rechaza ni condiciona en nombre de una persona. La junta decide; el gestor recomienda.
6. [PRINCE2] Gestión por excepción: dentro de tolerancia no se piden informes extra; sin ejecutivo nombrado no hay puerta.
7. [PRINCE2] Cada puerta verifica primero la justificación continua; recomendar cierre prematuro es un resultado legítimo.
8. [PRINCE2] Escalada por niveles: paquete → gestor; etapa → junta; proyecto → capa de negocio.
9. [PRINCE2] Tolerancias explícitas (tiempo y costo como mínimo) antes de autorizar cualquier etapa; las de etapa caben en las de proyecto.
10. [PRINCE2] PID y business case v1.0 se congelan al autorizar el proyecto; el cierre compara contra ellos.
11. [PRINCE2] Con BMAD, un desvío del PRD con línea base es una solicitud de cambio que decide la autoridad de cambio PRINCE2.
12. [PMBOK→DP] Técnica según la pregunta (alternativas con "no hacer nada", multicriterio con pesos con fuente y sensibilidad, árbol con EMV); fuente de cada cifra (`[por confirmar]` si falta); con huecos, `pedir-informacion`.
13. [Plantillas] Versión mínima o completa según riesgo, costo y stakeholders; reabrir no borra: la nueva `reemplaza` a la anterior, nivel ≥ (`vigentes`, guía §13.10).
14. Escrituras externas (tracker, correo, chat) solo con confirmación explícita, vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Solicitud de decisión de puerta | `templates/solicitud-puerta.md` | `00-direccion/decisiones/AAAA-MM-DD-solicitud-<puerta>.md` | `solicitud-<puerta>` |
| Tolerancias y autoridad delegada | `templates/tolerancias-y-autoridad.md` | `00-direccion/tolerancias-y-autoridad.md` | `tolerancias.*`, `roles.autoridad_cambio`, `tolerancias-y-autoridad` |
| Evaluación de excepción | `templates/evaluacion-excepcion.md` | `00-direccion/decisiones/AAAA-MM-DD-evaluacion-excepcion-X-###.md` | `evaluacion-excepcion-X-###` |
| Acta de decisión de la junta | `templates/acta-decision-junta.md` | `00-direccion/decisiones/AAAA-MM-DD-acta-junta-<puerta>.md` | `acta-junta-<fecha>`; `puertas[]` |
| Hoja de decisión | `templates/criterios-por-tipo.csv` | `03-control/decisiones/<ID>/` | — (hoja, no registro) |
| Líneas base congeladas (PID, business case, BMAD) | copia / `bmad.py linea-base` | `00-direccion/historial/` | `aprobado`; `bmad-prd` … |
| Fila de decisión | `estado.py puerta` / `aprobar` / `decision.py --elegir` | `03-control/registros/decisiones.csv` | `puertas[].decision_id` |
| Condiciones | `registro.py agregar acciones` + `cumplir-condiciones` | `03-control/registros/acciones.csv` | `puertas[].condiciones_cumplidas` |

## Calidad
- [ ] Justificación continua con evidencia citada (ruta y versión); productos requeridos con estado y aprobador.
- [ ] Al menos tres opciones (incluida "no autorizar" o "no hacer nada") con consecuencias cuantificadas.
- [ ] Recomendación con confianza; ninguna cifra ni peso sin fuente; sensibilidad y empates declarados.
- [ ] Rol que decide nombrado (ejecutivo/junta; capa de negocio si excede tolerancias de proyecto); la RACI lo refleja.
- [ ] Con BMAD: `bmad.py verificar` limpio o desvíos tratados; línea base solo tras la decisión.
- [ ] Tras la decisión: sin filas duplicadas, documentos aprobados, acta, condiciones como acciones, historial v1.0 (proyecto) y tolerancias de etapa (etapa).

## Escalamiento y excepciones
- Pronóstico fuera de tolerancia de **proyecto** → capa de negocio; registrar con `nivel=capa-negocio`.
- Junta sin posición unificada → decide el ejecutivo; discrepancia en `notas`.
- Pedido de saltar una puerta → explicar el riesgo; si la persona con rol insiste, `--forzar` con motivo.
- `estado.py puerta` rechaza `aprobado` con bloqueos de `puertas.py`: corregir o `condicionado`; `--forzar` queda anotado (`docs/PUERTAS.md`).
- Informe de excepción sin `pm-control` → plantilla de `pm-issues-cambios`. Plan de excepción → `pm-plan-etapa-y-limites`; business case en duda → `pm-caso-de-negocio`.
- Como subagente: las decisiones humanas van en el bloque de retorno (SPEC §1.11); nunca se suponen.

## Ejemplos de invocación
- "Preparame la solicitud de decisión para autorizar la etapa 2 del proyecto Faro."
- "Armá la matriz de decisión con pesos para las tres alternativas de OKR y decime qué tan sensible es."
- EN: "Score the two vendors with weighted criteria and knock-out thresholds, then record the executive's choice."
- No activa: "Anotá este riesgo del proveedor" → `pm-registros` (o `pm-riesgos` para analizarlo).

## EN summary
PRINCE2 Directing a project, run by pm-director: gate requests with quantified options and a recommendation; after a named person decides, it records gates, approvals, baselines, tolerances and conditions. `decision.py`: evidence pack (with strategic maps), weighted matrix (knock-outs, dominance, weight sensitivity; make-or-buy criteria), closed question, recorded choice.
