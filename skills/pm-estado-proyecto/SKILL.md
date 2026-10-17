---
name: pm-estado-proyecto
description: "Carpeta del proyecto, estado.json y scripts compartidos (estado, registro, wbs, cpm, evm). Usar: crear proyecto, estado, etapa, tolerancias, project state. No: decidir puertas→pm-direccion-decisiones."
version: 2.1.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [SU, DP, IP, CS, MP, SB, CP]
    practicas_prince2: [organizing, plans, risk, issues, progress]
    tecnicas_pmbok: [valor ganado, método del camino crítico, EDT/WBS, gestión de la información del proyecto]
    artefactos: [estado.json, registros CSV, diario, wbs, cronograma, cronograma MSPDI, exportados]
    idiomas: [es, en]
---

# Estado del proyecto y scripts · Project state and scripts

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- Crear la carpeta de un proyecto nuevo o consultar fase, proceso y etapa, qué tolerancias rigen y qué puertas o condiciones siguen abiertas.
- Ejecutar el registro mecánico de una puerta, una aprobación o una transición (CS→SB, →CP) que ya decidió una persona.
- Operar los scripts compartidos que usan las demás skills: `estado.py`, `registro.py`, `esquema.py`, `wbs.py`, `cpm.py`, `evm.py`, `exportar.py` y la fachada `especificacion.py`.
- EN: scaffold the project folder, read or update `estado.json`, record gates and approvals after a human decision.
- EN: run the shared scripts (registers, WBS, CPM/MSPDI, EVM, Office export) on behalf of other skills.

## Idioma
Carpetas y cabeceras CSV en español técnico (`snake_case`); los scripts responden en el idioma de `estado.json.idioma` y las respuestas al usuario van en su idioma. Equivalencias de registros en `references/guia.md` §7. Dato faltante: `[por confirmar]` / `[to be confirmed]`.

## Conocimiento
- `SPEC.md` §1.5 (carpeta), §1.6 (estado.json), §1.10 (convenciones canónicas), §1.12–§1.13 (integraciones, BMAD), §1.16 (fuente única).
- `references/guia.md` (este skill): §1 modelo de puertas, §2 migración, §3 carpetas v2, §4 integraciones, §5 opciones de scripts, §6 quién usa cada script.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` — buscar `### 4.5` (etapas y puertas) y `### 5.` (procesos SU…CP).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` — `### 3.8` (CPM) y `### 3.9` (EVM), fórmulas de `cpm.py` y `evm.py`.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` — `# PARTE V` (esquemas CSV de referencia); el esquema canónico es `scripts/esquema.py`.

## Entradas requeridas
- Ruta de la carpeta del proyecto. Si no existe: preguntar nombre, idioma (es/en), enfoque de entrega (predictivo/ágil/híbrido; las etapas PRINCE2 son siempre el marco) y, si se conocen, ejecutivo y gestor.
- Python 3; para exportar, `python-docx` y `openpyxl`; opcional `mmdc`.
- Rutas: `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/` = carpeta instalada de esta skill (plugin, manual o Hermes: guía §5).
- Integraciones: ninguna obligatoria; `estado.json.integraciones` declara qué sistema cumple cada capacidad (guía §4).

## Procedimiento
1. **Crear proyecto**: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta <dir> --nombre "<nombre>" --idioma es|en --enfoque predictivo|agil|hibrido [--ejecutivo .. --gestor ..]`. Crea las carpetas de SPEC §1.5 (incluidas `02-planificacion/especificacion/` derivada, `03-control/reuniones/` y `03-control/fuentes/`; guía §3), los nueve CSV, el diario y `estado.json` en `pre-proyecto`/SU/etapa 0. No sobrescribe un `estado.json` existente.
2. **Consultar**: `estado.py --proyecto <dir> ver` y `siguiente` (qué toca, puertas pendientes, condiciones abiertas, tolerancias faltantes). Un `estado.json` antiguo se migra al leerse (`ejecucion` → `entrega`; guía §2).
3. **Artefactos**: `estado.py artefacto <clave> --ruta <ruta> --estado borrador|en-revision|aprobado|obsoleto --version x.y` con las claves canónicas de SPEC §1.10.3.
4. **Aprobar un documento** (solo tras aprobación humana explícita): `estado.py aprobar <clave> --por "<rol: nombre>" [--version 1.0] [--nivel ..]`; sincroniza frontmatter y `estado.json` y agrega la fila en `decisiones.csv`.
5. **Registrar una puerta** (solo `pm-director`, tras la decisión humana): `estado.py puerta <tipo> --decision aprobado|condicionado|rechazado|pendiente --por "<rol: nombre>" [--condiciones ..] [--forzar] (más opciones en guía §1)`. El script escribe la fila de `decisiones.csv` y su id en `puertas[].decision_id`. Efectos de cada puerta: guía §1. Condiciones: `cumplir-condiciones <tipo>`.
6. **Transiciones**: `estado.py limite-etapa [--excepcion X-###]` (CS→SB, solo en fase `entrega`) y `estado.py cierre [--prematuro]` (→CP). `set` y `etapa` solo para correcciones.
7. **Tolerancias, roles, ágil, integraciones**: `tolerancia --nivel proyecto|etapa tiempo=".." costo=".."` (siete dimensiones), `rol <clave>=".."`, `agil <clave>=..`, `integracion especificacion=bmad tracker=..`, `umbrales-riesgo` (sintaxis y claves en guía §4).
8. **Registros**: `registro.py --proyecto <dir> agregar|actualizar|listar|resumen [--corte AAAA-MM-DD]|esquema …`; valida contra `esquema.py`, alias EN (guía §5.1). Clasificación y redacción: `pm-registros`.
9. **EDT/WBS**: `wbs.py 02-planificacion/wbs.csv --mermaid 02-planificacion/visuales/wbs.md --diccionario 02-planificacion/diccionario-wbs-esqueleto.md` valida, consolida (regla del 100 %) y dibuja el árbol (guía §5.4). Contenido de la EDT: `pm-planificacion-por-productos`.
10. **CPM y MS Project**: `cpm.py actividades.csv --inicio AAAA-MM-DD --mermaid gantt.md [--mspdi cronograma.xml --wbs wbs.csv]` (holguras, camino crítico, carga; MSPDI por EDT; guía §5.3). Estimación y nivelación: `pm-cronograma-estimacion`.
11. **EVM**: `evm.py --csv progreso.csv | --pv --ev --ac --bac [--tol-costo --tol-plazo] [--modo agil …] [--json]` (opciones en guía §5.2). Interpretación e informe: `pm-progreso-reportes`.
12. **Exportar**: `exportar.py docx|xlsx …` (guía §5.5); paquetes ZIP: `pm-exportar`.
13. **Fachada de especificación** (SPEC §1.16; la usan todas las skills): `especificacion.py --proyecto <dir> fuente|resumen|consultar <id>|listar requisitos|historias|epicas [filtros]|indice [--json]`. Proveedor según `integraciones.especificacion`: `bmad` → `pm-bmad-puente/scripts/bmad.py` (solo lectura); otro → `requisitos.md`, `backlog.csv`, `wbs.csv`. Igual contrato `pm-spec-index/1` en `02-planificacion/especificacion/spec-index.json`: caché que se reconstruye solo cuando cambia la huella sha256 de las fuentes (`indice` lo fuerza). Nunca se edita ni se cita como fuente.
14. **Diario**: fila en `03-control/registros/diario.md` para lo informal.
15. **Cerrar** confirmando qué cambió (ruta, id, nueva fase/etapa); como subagente, con el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] `estado.json` es la única fuente del estado de gobierno; lo escriben solo `estado.py` y `nuevo_proyecto.py`, nunca una edición a mano.
2. [PRINCE2] Ciclo de vida por etapas: SU (etapa 0) → IP (etapa 1 = iniciación) → etapas de entrega 2…n (fase `entrega`, CS/MP/SB) → CP. Ágil o híbrido operan dentro de las etapas, sin quitar puertas.
3. [PRINCE2] Solo `pm-director` registra puertas, y solo tras la decisión humana; los demás agentes dejan los productos `en-revision` y derivan.
4. [PRINCE2] Tolerancias por nivel: `proyecto` (capa de negocio), `etapa` (junta en cada `autorizar-etapa`), paquete (en su documento). Tiempo y costo, mínimo obligatorio.
5. [PRINCE2] Cada decisión queda en `decisiones.csv` con su nivel (`equipo`, `product-owner`, `gestor`, `autoridad-cambio`, `junta`, `capa-negocio`); las de puerta y aprobación las escribe el script.
6. [PMBOK→Progress/CS] EVM: declarar variante de EAC y tolerancias; BAC sin reserva de gestión; en ágil con costo y fecha fijos, EAC > BAC = alcance que no entra.
7. [PMBOK→Plans] CPM y WBS: declarar supuestos (días laborables, fin-a-comienzo, sin nivelación); la EDT cumple la regla del 100 % sobre las hojas.
8. [Plantillas] `esquema.py` es la fuente única de columnas y valores; cambiarlo exige actualizar `pm-registros/templates/guia-registros.md` en el mismo acto.
9. Los scripts son compartidos (guía §6): no cambiar su interfaz sin revisar las skills que los usan.
10. Todo artefacto generado por IA queda `borrador` hasta una aprobación humana explícita; los scripts no borran filas.
11. Integraciones opcionales: si hay tracker o chat conectado, vía `pm-integraciones`; escrituras externas solo con confirmación explícita.
12. Fuente única (SPEC §1.16): ninguna skill abre BMAD ni `requisitos.md` para extraer datos; todas leen por `especificacion.py` y citan ids. Más reglas: guía §8.

## Artefactos y plantillas
| Artefacto | Herramienta | Ruta | estado.json |
|---|---|---|---|
| Carpetas y estado inicial | `scripts/nuevo_proyecto.py` | `<dir>/` | crea `estado.json` |
| Estado, puertas, aprobaciones, transiciones, integraciones | `scripts/estado.py` | `estado.json` | todas las claves |
| Esquema de registros | `scripts/esquema.py` | — | — |
| Registros CSV (9) y diario | `scripts/registro.py` | `03-control/registros/` | — |
| EDT validada, diagrama y esqueleto de diccionario | `scripts/wbs.py` | `02-planificacion/wbs.csv`, `visuales/wbs.md`, `diccionario-wbs-esqueleto.md` | `pbs-wbs`, `diccionario-wbs` |
| Cronograma CPM + Gantt; MS Project XML | `scripts/cpm.py` (`--mspdi`, `--wbs`) | `02-planificacion/cronograma.md`, `cronograma.xml` | `cronograma` |
| Cálculo EVM | `scripts/evm.py` | consola o JSON para el informe | — |
| Exportados Office | `scripts/exportar.py` | `exportados/` | — (nunca fuente de verdad) |
| Índice de especificación (caché) | `scripts/especificacion.py` | `02-planificacion/especificacion/spec-index.json` | — (derivado) |

## Calidad
- [ ] `estado.json` coherente: fase ↔ proceso ↔ última puerta; `siguiente` sin avisos inesperados; ninguna mención a la fase `ejecucion`.
- [ ] Toda puerta con `decision_id` y su fila en `decisiones.csv`, sin duplicados a mano.
- [ ] Condiciones de puertas `condicionado` cumplidas o con responsable y fecha.
- [ ] Tolerancias de proyecto y de la etapa vigente con al menos tiempo y costo.
- [ ] Registros dentro del esquema; `wbs.py` sin errores antes de usar la EDT en un plan.
- [ ] Exportados sin errores; los no aprobados con banner de borrador.

## Escalamiento y excepciones
- Fase declarada incoherente con los artefactos → informar y pedir a `pm-director` que regularice; no corregir en silencio con `set` o `etapa`.
- `evm.py` marca `excepcion_prevista` → `pm-control` (informe de excepción) → `pm-director`.
- `--forzar` (en `puerta` o `registro.py`) solo con motivo explícito del usuario, anotado.
- Como subagente: decisiones humanas (aprobar, forzar, elegir integración) en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Creá la carpeta del proyecto Faro en español, enfoque híbrido."
- "¿En qué etapa está el proyecto y qué puerta falta?"
- EN: "Generate the MS Project XML from our activities and WBS files."
- EN: "Set the tracker integration to Jira and the spec layer to BMAD."
- No activa: "¿Apruebo la etapa 3 o pido más información?" → `pm-direccion-decisiones` (decide la junta; esta skill solo registra).

## EN summary
Operational backbone and shared script library of the pack. `nuevo_proyecto.py` scaffolds the folder; `estado.py` reads state and records gates (pm-director only, after a human decision), approvals, transitions, tolerances, roles and integrations. Phases are `pre-proyecto`, `inicio`, `entrega`, `cierre`, `cerrado` (old `ejecucion` migrates to `entrega`). `registro.py`, `wbs.py`, `cpm.py` (with `--mspdi`/`--wbs`), `evm.py` and `exportar.py` are used by many other skills; `especificacion.py` is the single specification façade (contract pm-spec-index/1, hash-invalidated cache) with or without BMAD.
