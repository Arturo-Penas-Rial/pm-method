---
name: pm-reporte
description: "Genera el informe de avance pedido: highlight, checkpoint o excepción, vía pm-progreso-reportes. Uso manual: /pm-reporte highlight|checkpoint|excepcion [carpeta]. Progress report."
disable-model-invocation: true
argument-hint: "highlight|checkpoint|excepcion [carpeta]"
version: 2.3.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [CS, MP]
    practicas_prince2: [progress, issues]
    tecnicas_pmbok: [análisis del valor ganado, análisis de variación]
    artefactos: [highlight, checkpoint, informe-excepcion]
    idiomas: [es, en]
---

# Informe de avance · Progress report

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- El usuario escribe `/pm-reporte <tipo>`. EN: user-invoked highlight, checkpoint or exception report.

## Idioma
Idioma de `estado.json` o del usuario.

## Conocimiento
`pm-progreso-reportes` (dueña de informes y EVM), `pm-issues-cambios` (plantilla del informe de excepción), `pm-control` (agente).

## Entradas requeridas
Tipo (por defecto `highlight`), carpeta con `estado.json` en proceso CS, período de informe. Datos de avance en `03-control/reportes/progreso.csv` o del tracker.

## Procedimiento
1. Delegar en el agente `pm-control` (o seguir `pm-progreso-reportes` en el hilo principal) con el tipo pedido.
2. Antes del informe: `registro.py resumen`, `evm.py` con tolerancias si hay línea base, `bmad.py avance` y `verificar` si hay BMAD, y `/pm-sync` si hay tracker (instantánea fechada). Scripts en `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/` (manual/Hermes: `~/.claude/skills/…` o `~/.hermes/skills/…`).
3. `highlight` → `03-control/reportes/<fecha>-highlight-report.md`; `checkpoint` → por paquete de trabajo; `excepcion` → plantilla de `pm-issues-cambios`, `03-control/reportes/<fecha>-informe-excepcion-X-###.md`, y derivar a `pm-director`.
4. Dejar el informe `en-revision` y mostrar resumen, semáforos con su fuente y decisiones pedidas a la junta. Publicarlo en chat o correo solo con confirmación (`pm-integraciones`).

## Reglas del método
1. [PRINCE2] Gestión por excepción: si el pronóstico sale de tolerancia, el informe es de excepción, no un highlight ámbar. 2. Conteos idénticos a `registro.py resumen`. 3. Nada se envía sin confirmación.

## Artefactos y plantillas
Plantillas de `pm-progreso-reportes` y `pm-issues-cambios`; salida en `03-control/reportes/`.

## Calidad
- [ ] Tipo correcto; cifras con fuente; informe `en-revision`; excepción derivada.

## Escalamiento y excepciones
Excepción → `pm-director` (decide la junta). Gráficos y tablero → `pm-visuales`.

## Ejemplos de invocación
- `/pm-reporte highlight` · `/pm-reporte excepcion ./turnos` · EN: `/pm-reporte checkpoint` · No aplica a "dibujá el burn-up" → `pm-visuales`.

## EN summary
User-invoked report: runs pm-control/pm-progreso-reportes to produce a highlight, checkpoint or exception report from registers, EVM, BMAD progress and tracker snapshots; exceptions go to pm-director.
