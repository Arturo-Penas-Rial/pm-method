---
name: pm-sanidad
description: "Sanidad y consistencia del ecosistema (estado, puertas, registros, BMAD↔PRINCE2, integraciones). Usar: sanidad, chequeo, consistencia, doctor, health check, antes de una puerta. No: cómo venimos→pm-orquestador; calidad→pm-calidad."
version: 2.1.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [DP, CS, SB, CP]
    practicas_prince2: [progress, quality, issues]
    tecnicas_pmbok: [auditoría de la información del proyecto]
    artefactos: [informe-sanidad]
    idiomas: [es, en]
---

# Sanidad del ecosistema · Ecosystem health check

## Cuándo usar / When to use
- Al abrir una sesión sobre un proyecto, antes de preparar cualquier puerta, después de sincronizar BMAD o un tracker, y al actualizar pm-method o BMAD.
- Cuando algo "no cuadra": cifras distintas entre informes, ids que no existen, puertas fuera de orden, cambios del PRD sin tramitar.
- EN: run before gates, after syncs or upgrades, or whenever data look inconsistent.
- EN: the same checks run automatically at session start (Claude Code hook) in quick mode.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. los códigos de hallazgo (EST-03, ESP-10…) no se traducen.

## Conocimiento
- `SPEC.md` §1.10 (convenciones), §1.13 y §1.16 (columna vertebral BMAD ↔ PRINCE2), §1.17 (controles permanentes).
- `references/guia.md` (este skill): catálogo de comprobaciones con causa típica y corrección.

## Entradas requeridas
- Carpeta del proyecto con `estado.json`. Con BMAD: `integraciones.especificacion = bmad` y raíz detectada.
- Script: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/sanidad.py --proyecto <dir> [--rapido] [--informe] [--reparar] [--json]`.

## Procedimiento
1. **Ejecutar** `sanidad.py --proyecto <dir> --informe` (completo) o `--rapido` (inicio de sesión). Familias: INS instalación e integraciones externas · EST estado, roles y puertas · ART artefactos · REG registros · ESP especificación y BMAD · INT integraciones MCP.
2. **Reparar lo seguro** con `--reparar` (solo agrega columnas de esquema faltantes y reconstruye el índice de especificación). Nada más se corrige automáticamente.
3. **Clasificar** cada ERROR por dueño (ver `references/guia.md` §2) y derivar: estado/puertas → pm-director; registros → pm-registros, pm-riesgos o pm-issues-cambios; especificación → pm-bmad-puente o pm-planificacion-por-productos; cambio no controlado (ESP-10) → pm-issues-cambios; integraciones → pm-integraciones; instalación → usuario.
4. **Regla de puerta**: con ERROR abierto no se presenta una puerta a la junta; si el humano decide seguir igual, queda como condición en la decisión (`--condiciones`) y en `decisiones.csv`.
5. **Registrar** el resultado: el informe queda en `03-control/reportes/<fecha>-sanidad.md`; los ERROR que requieren trabajo se convierten en acciones (`registro.py agregar acciones`) con responsable.
6. Si corre como subagente: devolver el bloque de retorno (SPEC §1.11) con los ERROR como "decisiones humanas requeridas" cuando haga falta decidir.

## Reglas del método
1. [PRINCE2] Gestión por excepción también para los datos: un ERROR de sanidad es una desviación del control del proyecto y se trata antes de decidir.
2. Fuente única: la sanidad nunca "arregla" datos de negocio copiando de un lado a otro; señala al dueño (SPEC §1.16).
3. Cambio no controlado (especificación distinta de su línea base sin issue que la cite) es siempre ERROR.
4. Derivados y copias congeladas no se editan; si difieren, se regeneran o se crea una versión nueva.
5. Los hallazgos de instalación (INS) no bloquean puertas, pero se informan al usuario.
6. [PMBOK→Progress] La sanidad es una auditoría de información del proyecto, no de calidad de productos (eso es pm-calidad).

## Artefactos y plantillas
| Artefacto | Origen | Ruta | estado.json |
|---|---|---|---|
| Informe de sanidad | `sanidad.py --informe` | `03-control/reportes/<fecha>-sanidad.md` | — |

## Calidad
- [ ] Ejecutada antes de cada puerta y tras cada sincronización.
- [ ] Ningún ERROR sin dueño ni acción.
- [ ] ESP-10 (cambio no controlado) en cero o tramitado.

## Escalamiento y excepciones
- ERROR de puertas o roles → pm-director. ERROR de especificación → pm-bmad-puente / pm-issues-cambios.
- Versión de BMAD no probada (ESP-07) → el mantenedor corre probar_paquete.py (carpeta de scripts en la raíz del paquete).

## Ejemplos de invocación
- "Revisá la sanidad del proyecto antes de la junta."
- "¿Está todo consistente entre el PRD y nuestro plan?"
- EN: "Run a health check on the project folder."
- No activa: "Auditá la calidad del módulo de pagos" → `pm-calidad`.

## EN summary
Runs sanidad.py over the project: state/gate coherence, roles, artefact registry vs documents, register schema and cross-references, specification coverage and id resolution, BMAD baselines vs current specs (uncontrolled change), pending handoffs and change proposals, integration snapshots, installation and skill-listing collisions. ERRORs block gate presentation unless the board accepts them as conditions.
