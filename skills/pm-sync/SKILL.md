---
name: pm-sync
description: "Sincroniza fuentes externas con el proyecto: BMAD (backlog, avance, desvíos) e instantáneas de tracker y OKR. Escribe afuera solo con confirmación. Uso manual: /pm-sync [bmad|tracker|okr]."
disable-model-invocation: true
argument-hint: "[bmad|tracker|okr|todo] [carpeta]"
version: 2.3.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [CS, MP]
    practicas_prince2: [progress, issues]
    tecnicas_pmbok: []
    artefactos: [backlog.csv, avance-bmad.csv, instantáneas en 03-control/fuentes]
    idiomas: [es, en]
---

# Sincronizar integraciones · Sync integrations

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- El usuario escribe `/pm-sync` para traer datos de BMAD, del tracker o de la herramienta OKR. EN: user-invoked sync.

## Idioma
Idioma de `estado.json` o del usuario.

## Conocimiento
`pm-bmad-puente`, `pm-integraciones`, `pm-okr`, `pm-estado-proyecto` (fachada); `SPEC.md` §1.12–1.13 y §1.16 (fuente única).

## Entradas requeridas
`estado.json.integraciones` (qué sistema cumple cada capacidad). Si una capacidad está en `ninguno`, ofrecer configurarla con `pm-integraciones`.

**Fuente única (SPEC §1.16)**: los datos de especificación se leen solo con `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar …`, con o sin BMAD; nunca abrir archivos de BMAD ni `requisitos.md`. Esta skill solo refresca derivados y propone; no escribe especificación.

## Procedimiento
Scripts en `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/` (manual/Hermes: `~/.claude/skills/…` o `~/.hermes/skills/…`).
0. Al final de la sincronización: `sanidad.py --proyecto <dir>` (`pm-sanidad`) para confirmar que la columna vertebral quedó consistente (sin ESP-10, ESP-04 ni ESP-14).
1. **Especificación**: `especificacion.py --proyecto <dir> resumen` (proveedor, cobertura, requisitos sin historia; reconstruye el índice si cambió la huella).
2. **BMAD** (si `especificacion = bmad`): `bmad.py --proyecto <dir> backlog`, `… avance`, `… verificar`. Desvío no traspasado o Sprint Change Proposal → proponer issue `solicitud-cambio` (`pm-issues-cambios`).
3. **Traspasos pendientes**: revisar `estado.json.integraciones.bmad.handoffs`; listar los no confirmados por el equipo BMAD y su antigüedad. Si `backlog.csv` tiene cambios de MoSCoW/release/iteración sin traspasar, proponer `bmad.py --proyecto <dir> handoff` (lo decide `pm-agil-hibrido`/PO); cambio aprobado sin traspaso → `handoff --cambio C-###` vía `pm-issues-cambios`.
4. **Tracker / docs / chat** (si están conectados): con `pm-integraciones`, leer y guardar instantánea `03-control/fuentes/<sistema>-AAAA-MM-DD.csv|md`; conciliar contra backlog, acciones e issues y **proponer** las diferencias.
5. **OKR** (si `okr = tability|perdoo`): instantánea en `03-control/fuentes/` y check-in por KR (`okr.py <csv> --checkin KR-… --valor … --fuente tability|perdoo`); puntuar con `okr.py`; los check-ins locales sin publicar se proponen con `okr.py --propuesta-sync` y se publican solo con confirmación.
6. Mostrar un resumen: qué se leyó, traspasos pendientes, qué cambió en archivos derivados, qué propuestas hay. Cambios a registros de gobierno y cualquier escritura externa (crear tickets, publicar) solo tras vista previa y confirmación explícita.

## Reglas del método
1. Fuente de verdad = carpeta del proyecto; instantáneas fechadas e inmutables. 2. [PRINCE2] Los desvíos de alcance son solicitudes de cambio que decide la autoridad de cambio. 3. Escrituras externas solo con confirmación. 4. Fuente única (SPEC §1.16): leer por `especificacion.py`; las decisiones viajan a BMAD solo por `bmad.py handoff`.

## Artefactos y plantillas
`02-planificacion/backlog.csv` (columnas derivadas), `03-control/reportes/avance-bmad.csv`, `03-control/fuentes/*`.

## Calidad
- [ ] `especificacion.py resumen` y `bmad.py verificar` corridos; traspasos pendientes listados.
- [ ] Cada lectura con instantánea; columnas de gobierno intactas; propuestas sin aplicar hasta confirmar.

## Escalamiento y excepciones
Diferencias de alcance → `pm-issues-cambios`; conflicto con lo aprobado por la junta → `pm-director`.

## Ejemplos de invocación
- `/pm-sync` · `/pm-sync bmad` · EN: `/pm-sync tracker` · No aplica a "escribí el PRD" → flujos de BMAD.

## EN summary
User-invoked sync: runs `especificacion.py resumen`, bmad.py backlog/avance/verificar, lists pending handoffs (`integraciones.bmad.handoffs`) and takes dated tracker or OKR snapshots via pm-integraciones; reconciles them with governance registers and writes externally only after an explicit confirmation.
