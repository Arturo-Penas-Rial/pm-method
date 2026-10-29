---
name: pm-ayuda
description: "Ayuda de pm-method: qué escribir en cada situación, lista de skills y comandos, ciclo de vida y carpetas. Uso manual: /pm-ayuda [tema]. Help: commands, skills, life cycle."
disable-model-invocation: true
argument-hint: "[tema / topic]"
version: 2.6.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [SU, IP, DP, CS, MP, SB, CP]
    practicas_prince2: [business-case, organizing, plans, quality, risk, issues, progress]
    tecnicas_pmbok: []
    artefactos: []
    idiomas: [es, en]
---

# Ayuda de pm-method · pm-method help

## Cuándo usar / When to use
- El usuario escribe `/pm-ayuda` (con o sin tema) para saber qué pedir y dónde queda cada cosa. EN: user-invoked help.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. si el argumento "$ARGUMENTS" nombra un tema, mostrar solo esa parte.

## Conocimiento
`SPEC.md` §1.5 (carpetas), §1.10 (convenciones), §1.15 (comandos), §1.16 (fuente única); `pm-orquestador` (enrutamiento).

## Entradas requeridas
Ninguna. Si hay `estado.json`, agregar al final la salida de `estado.py siguiente` (`${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/scripts/estado.py`; en manual/Hermes, `~/.claude/skills/…` o `~/.hermes/skills/…`).

## Procedimiento
1. Mostrar **qué escribir** según la situación:
   | Situación | Escribir |
   |---|---|
   | Empezar un proyecto | `/pm-nuevo "Nombre"` |
   | ¿Dónde estoy? ¿Qué sigue? | `/pm-estado` |
   | Informe a la junta o al equipo | `/pm-reporte highlight` · `checkpoint` · `excepcion` |
   | Preparar una decisión de junta | `/pm-puerta autorizar-etapa` (u otra puerta) |
   | Traer datos de Jira/BMAD/Tability | `/pm-sync` |
   | Interesados, matriz poder/interés, RACI | pedirlo en lenguaje natural (`pm-interesados`) |
   | Enviar un comunicado o informe a interesados | pedirlo en lenguaje natural: borradores por perfil, aprobación y envío por correo, Slack, Teams o `.eml` (`pm-comunicacion-stakeholders` + `pm-integraciones`) |
   | Cualquier otra cosa | pedirlo en lenguaje natural o `/pm-orquestador` |
2. Formas de invocar: plugin `/pm-method:<skill>`; instalación manual y Hermes `/<skill>`. Agente de hilo principal: `claude --agent pm-method:pm-orquestador`.
3. **Skills** (todas invocables como comando):
   - Dirección: pm-orquestador, pm-direccion-decisiones, pm-estado-proyecto.
   - Inicio: pm-mandato-y-brief, pm-caso-de-negocio, pm-okr, pm-organizacion-roles, pm-interesados, pm-enfoques-gestion, pm-acta-constitucion.
   - Planificación: pm-planificacion-por-productos, pm-cronograma-estimacion, pm-costos-presupuesto, pm-plan-etapa-y-limites, pm-agil-hibrido, pm-adquisiciones.
   - Control: pm-paquetes-trabajo, pm-registros, pm-riesgos, pm-issues-cambios, pm-progreso-reportes, pm-calidad, pm-comunicacion-stakeholders, pm-reuniones, pm-visuales.
   - Cierre: pm-cierre-proyecto, pm-lecciones-aprendidas.
   - Transversales: pm-bmad-puente, pm-integraciones, pm-exportar, pm-knowledge.
   - Comandos: pm-ayuda, pm-nuevo, pm-estado, pm-reporte, pm-puerta, pm-sync.
4. **Ciclo de vida**: SU (etapa 0, pre-proyecto) → `autorizar-inicio` → IP (etapa 1) → `autorizar-proyecto` + `autorizar-etapa` → etapas de entrega 2…n (CS/MP; SB y `autorizar-etapa` en cada límite) → CP → `autorizar-cierre`. Excepción: informe → decisión de la junta → plan de excepción. Solo `pm-director` registra puertas.
5. **Carpetas**: `00-direccion/` (business case, PID, OKR, decisiones, historial) · `01-inicio/` · `02-planificacion/` (planes, WBS, backlog, especificacion BMAD) · `03-control/` (registros, paquetes, reportes, reuniones, fuentes) · `04-cierre/` · `exportados/` (copias, nunca fuente de verdad).
6. **Fuente única / Single source** (tema `especificacion`, `bmad`): cada dato tiene un solo dueño. Requisitos, épicas e historias los escribe BMAD (o, sin BMAD, `requisitos.md` y `backlog.csv`); todas las skills los leen solo con `especificacion.py resumen|consultar <id>|listar …` y citan ids, sin copiar texto. Las decisiones de gobierno (cambio aprobado, MoSCoW, release) vuelven a BMAD con `bmad.py handoff`; luego `verificar` y nueva línea base. EN: one owner per datum, one read façade, governance decisions handed back.

Sanidad: `/pm-method:pm-sanidad` (o `/pm-sanidad`) revisa estado, puertas, registros, coherencia BMAD↔PRINCE2 e integraciones; en Claude Code corre sola en modo rápido al abrir la sesión, y pm-puerta la exige antes de cada puerta.

## Reglas del método
1. [PRINCE2] Etapas y puertas siempre; nada aprobado sin decisión humana registrada.
2. Escrituras externas solo con confirmación. 3. Solo informa: no crea ni modifica archivos.

## Artefactos y plantillas
Ninguno (solo respuesta en pantalla).

## Calidad
- [ ] Respuesta de una pantalla; tema pedido primero; siguiente paso si hay proyecto.

## Escalamiento y excepciones
Si el usuario pide hacer algo, derivar a `pm-orquestador` o al comando correspondiente.

## Ejemplos de invocación
- `/pm-ayuda` · `/pm-ayuda puertas` · EN: `/pm-ayuda folders` · `/pm-ayuda commands`
- No aplica a "armá el highlight" → `/pm-reporte` o `pm-progreso-reportes`.

## EN summary
User-invoked help: what to type for each situation, every skill as `/pm-method:<skill>` or `/<skill>`, the PRINCE2 stage life cycle with its gates, and the project folder layout. Read-only.
