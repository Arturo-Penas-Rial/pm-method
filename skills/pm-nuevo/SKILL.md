---
name: pm-nuevo
description: "Crea la carpeta de un proyecto pm-method (estado.json, registros) y detecta BMAD si existe. Uso manual: /pm-nuevo \"Nombre\" [carpeta]. New project scaffold."
disable-model-invocation: true
argument-hint: "\"Nombre del proyecto\" [carpeta] [es|en] [predictivo|agil|hibrido]"
version: 2.6.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-orquestador
    procesos_prince2: [SU]
    practicas_prince2: [organizing, plans]
    tecnicas_pmbok: []
    artefactos: [estado.json, registros CSV]
    idiomas: [es, en]
---

# Nuevo proyecto · New project

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- El usuario escribe `/pm-nuevo` para arrancar un proyecto. EN: user-invoked project scaffold.

## Idioma
Idioma del argumento o del usuario; se guarda en `estado.json.idioma`.

## Conocimiento
`SPEC.md` §1.5–1.6; `pm-estado-proyecto` (scripts); `pm-bmad-puente` (detección).

## Entradas requeridas
Nombre (obligatorio), carpeta (por defecto `./<nombre-kebab>`), idioma, enfoque de entrega, ejecutivo y gestor si se conocen (si no, `[por confirmar]`). Preguntar solo el nombre si falta.

## Procedimiento
Scripts en `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/scripts/` y `${CLAUDE_PLUGIN_ROOT}/skills/pm-bmad-puente/scripts/` (manual/Hermes: `~/.claude/skills/<skill>/scripts/` o `~/.hermes/skills/<skill>/scripts/`).
1. Si la carpeta ya tiene `estado.json`, no sobrescribir: mostrar `estado.py --proyecto <dir> ver` y parar.
2. `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta <dir> --nombre "<nombre>" --idioma <es|en> --enfoque <predictivo|agil|hibrido> [--ejecutivo ".."] [--gestor ".."]`.
3. Si el repositorio tiene BMAD (`_bmad/`, `_bmad-output/` o `.bmad-core/` en la carpeta o en una superior): `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> detectar` y luego `estado.py --proyecto <dir> integracion especificacion=bmad`. La carpeta del proyecto debe quedar fuera de las carpetas de BMAD.
4. Mostrar la estructura creada, `estado.py --proyecto <dir> siguiente` y ofrecer seguir con `pm-mandato-y-brief` (mandato y brief, proceso SU).

## Reglas del método
1. [PRINCE2] El proyecto nace en SU (etapa 0, pre-proyecto); no hay etapa autorizada hasta `autorizar-inicio`.
2. No sobrescribir proyectos existentes. 3. No instalar BMAD ni escribir en sus carpetas.

## Artefactos y plantillas
| Artefacto | Ruta | estado.json |
|---|---|---|
| Estado y registros | `<dir>/estado.json`, `<dir>/03-control/registros/*.csv` | creado |

## Calidad
- [ ] `estado.json` creado con idioma y enfoque; BMAD detectado o declarado ausente.

## Escalamiento y excepciones
Error de script o carpeta inválida → informar y no reintentar a ciegas. Siguientes pasos → `pm-orquestador`.

## Ejemplos de invocación
- `/pm-nuevo "Portal de turnos" ./turnos es hibrido` · `/pm-nuevo "Faro"`
- EN: `/pm-nuevo "Data platform" ./dp en agil` · No aplica a "¿en qué etapa estamos?" → `/pm-estado`.

## EN summary
User-invoked scaffold: runs nuevo_proyecto.py to create the project folder, registers and estado.json, detects BMAD with bmad.py detectar when present, and points to the start-up (SU) next step. Never overwrites an existing project.
