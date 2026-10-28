---
name: pm-estado
description: "Estado del proyecto: fase, etapa, tolerancias, puertas pendientes, registros abiertos, avance BMAD y siguiente paso. Uso manual: /pm-estado [carpeta]. Project status."
disable-model-invocation: true
argument-hint: "[carpeta del proyecto / project folder]"
version: 2.5.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [DP, CS, SB]
    practicas_prince2: [progress, risk, issues]
    tecnicas_pmbok: []
    artefactos: []
    idiomas: [es, en]
---

# Estado del proyecto · Project status

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- El usuario escribe `/pm-estado` para ver dónde está el proyecto y qué sigue. EN: user-invoked status check.

## Idioma
Idioma de `estado.json` o del usuario.

## Conocimiento
`pm-estado-proyecto` (scripts); `pm-bmad-puente` (avance); `SPEC.md` §1.10.

## Entradas requeridas
Carpeta con `estado.json` ("$ARGUMENTS" o el directorio actual; si no se encuentra, preguntar o sugerir `/pm-nuevo`).

## Procedimiento
Scripts en `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/` (manual/Hermes: `~/.claude/skills/<skill>/scripts/` o `~/.hermes/skills/<skill>/scripts/`).
1. `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> ver` y `… siguiente`.
2. `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> resumen`.
2b. `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/sanidad.py --proyecto <dir> --rapido` (`pm-sanidad`): contar ERROR/AVISO y mostrar los ERROR.
3. Si `integraciones.especificacion = bmad`: `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> avance` (solo lectura del avance; agrega una fila a `avance-bmad.csv`).
3b. Si piden «hoy», «radar» o qué decidir: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> radar` (solo lectura; decidir, escalar, desbloquear y vigilar con quién decide y el siguiente paso).
4. Responder: tres líneas (fase/proceso y etapa · tolerancias y excepción abierta · puertas pendientes y condiciones) + tabla corta (riesgos altos sin respuesta, issues abiertos, acciones vencidas por responsable, avance BMAD) + siguiente paso con agente/skill y rol que decide.

## Reglas del método
1. [PRINCE2] Un pronóstico fuera de tolerancia se señala como excepción para `pm-director`. 2. Cada cifra cita su script o registro. 3. Solo lectura (salvo la fila de avance BMAD).

## Artefactos y plantillas
Ninguno nuevo; `03-control/reportes/avance-bmad.csv` (fila) si hay BMAD.

## Calidad
- [ ] Datos de los scripts, sin inventar; siguiente paso con rol.

## Escalamiento y excepciones
Excepción abierta o prevista → `pm-director`; informe formal → `/pm-reporte`.

## Ejemplos de invocación
- `/pm-estado` · `/pm-estado ./turnos` · EN: `/pm-estado ./dp` · No aplica a "armá el highlight" → `/pm-reporte`.

## EN summary
User-invoked status: runs estado.py ver/siguiente, registro.py resumen and, with BMAD, bmad.py avance; answers in three lines plus a short register table and the method's next step.
