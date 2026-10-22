---
name: pm-planificacion-por-productos
description: "Alcance por productos: descripción del producto, PBS, WBS/EDT (wbs.py), requisitos y RTM. Usar: alcance, PBS, WBS, EDT, scope, product description. No: requisitos con BMAD→pm-bmad-puente."
version: 2.4.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: planificacion
    agente: pm-planificacion
    procesos_prince2: [SU, IP, SB]
    practicas_prince2: [plans, quality]
    tecnicas_pmbok: [descomposición, regla del 100 %, planificación gradual, elicitación de requisitos, matriz de trazabilidad, MoSCoW]
    artefactos: [descripcion-producto-proyecto, pbs-wbs, wbs.csv, descripcion-producto-<id>, flujo-productos, enunciado-alcance, requisitos, matriz-trazabilidad, diccionario-wbs]
    idiomas: [es, en]
---

# Planificación basada en productos · Product-based planning

## Cuándo usar / When to use
- Definir **qué** entregará el proyecto: descripción del producto del proyecto, PBS, WBS/EDT, flujo, alcance, diccionario; requisitos y RTM solo **sin BMAD**.
- En la iniciación (IP) para el plan de proyecto y en cada límite de etapa (SB) para los productos de la etapa siguiente.
- EN: project product description, PBS→WBS, product descriptions, flow diagram, scope statement, WBS dictionary.
- EN: build and validate the WBS with `wbs.py`; requirements/RTM only without BMAD.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Plantillas bilingües. La primera vez, dar el nombre EN de cada artefacto (ver `references/guia.md` §2). Columnas de `wbs.csv` con su nombre EN: `references/guia.md` §4.

## Conocimiento
- `references/guia.md` (esta skill): §1 mínima vs. completa, §2 mapeo de nombres, §3 elicitación, §4 `wbs.py`, §5 detalle de pasos, §6 ágil/híbrido/BMAD, §7 reglas complementarias, §8 casos borde.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §4.1.2, §4.3.1 Pasos 1–2, §4.3.2 (MoSCoW), §5.3.4 y §5.5.1 (descripciones y criterios).
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §2–§5 (requisitos, RTM, alcance, diccionario), Parte V.
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.8 (descomposición, regla del 100 %) y §3.13 (épicas, historias).
- Con BMAD: `SPEC.md` §1.13 y §1.16 (`pm-bmad-puente`, dueño de la RTM).

## Entradas requeridas
- `estado.json` (`enfoque_entrega`, `etapa_actual`, `integraciones`). Si no existe → `pm-estado-proyecto`.
- Project brief o acta en `01-inicio/` y business case (al menos esquemático) en `00-direccion/`. Sin business case, preguntar si es modo exploratorio (todo borrador).
- `stakeholders.csv` (origen de requisitos); equipo y proveedores (responsables de paquetes).
- Plan de etapa: plan de proyecto vigente y productos de la etapa.
- **Especificación (fuente única, SPEC §1.16)**: requisitos y cobertura solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar requisitos` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md` para extraer datos). Escribe como dueña: PBS, descripciones de producto, `wbs.csv` (`ref` = ids) y, solo sin BMAD, `requisitos.md`.
- Datos faltantes como `[por confirmar]` / `[to be confirmed]`, con las preguntas al final; no inventar criterios ni cifras.

## Procedimiento
1. **Situar el plan**: leer `estado.json`; decidir proyecto (IP) o etapa (SB) y anotarlo en el frontmatter. Proponer versión mínima o completa (`references/guia.md` §1) y confirmar. Si `enfoque_entrega = agil`, aplicar el perfil mínimo (§6).
2. **Descripción del producto del proyecto** (solo plan de proyecto): propósito, productos mayores, criterios priorizados (MoSCoW), métodos y responsables de aceptación, tolerancias (§5). **Puerta**: la aprueban usuario sénior y ejecutivo; hasta entonces `borrador`.
3. **PBS** en `pbs-wbs.md`: productos hasta el nivel que se controla, con intermedios y externos; regla del 100 %.
4. **WBS/EDT en `wbs.csv`** (plantilla `templates/wbs.csv`, en `02-planificacion/wbs.csv`): por cada producto de nivel inferior, agrupar el trabajo en paquetes (`tipo=paquete`) e hitos; cada paquete con un **responsable**; `esfuerzo_h` y `costo` solo en hojas (vacíos hasta estimar); `ref` con ids de requisitos (PRD con BMAD, `REQ-###` sin BMAD). Correr `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/wbs.py 02-planificacion/wbs.csv --mermaid 02-planificacion/visuales/wbs.md --diccionario 02-planificacion/diccionario-wbs-esqueleto.md`; corregir errores y resolver cada `AVISO`. Detalle en §4.
5. **Descripciones de producto** (`productos/<id>-<nombre>.md`): especificaciones medibles, tolerancia, método de verificación, productor, revisor independiente y autoridad de aceptación (§5). Con BMAD, los criterios citan FR/NFR del PRD sin copiarlos.
6. **Flujo de productos** (`flujo-productos.md`): Inicio, Fin, dependencias y paralelismo; proponer cada dependencia externa como riesgo (`registro.py agregar riesgos`) con confirmación.
7. **Enunciado del alcance** (QUÉ; el CÓMO es de `pm-enfoques-gestion`): entregables = productos de nivel superior, criterios, exclusiones, restricciones, supuestos `S-###`.
8. **Requisitos y RTM**: *sin BMAD*, `requisitos.md` y `matriz-trazabilidad.md` con cobertura y huérfanos (§5). *Con BMAD*, **no se escriben aquí**: citar ids en `ref` y descripciones; RTM por `pm-bmad-puente` (`bmad.py trazabilidad --wbs 02-planificacion/wbs.csv`); FR sin paquete en la cobertura de la fachada → hallazgo de alcance (§6).
9. **Diccionario de la WBS**: completar el esqueleto generado con la plantilla `diccionario-wbs.md` (§5).
10. **Consolidar tras estimar**: cargar en `wbs.csv` las cifras por paquete de estimación y costeo y volver a correr `wbs.py`; el total debe coincidir con la estimación base (diferencias: §8).
11. **Revisión cruzada**: checklist de Calidad; PBS ↔ WBS ↔ PFD sin vacíos ni solapamientos.
12. **Registrar** con `estado.py --proyecto <dir> artefacto <clave> --ruta ... --estado borrador|en-revision --version 0.x` (`descripcion-producto-proyecto`, `pbs-wbs`, `diccionario-wbs`, `enunciado-alcance`). **Puerta humana**: las descripciones las aprueba el usuario sénior; el conjunto se aprueba con el plan (`autorizar-proyecto` / `autorizar-etapa`, registradas por `pm-director`). Nunca marcar `aprobado` desde aquí.
13. **Siguiente paso**: paquetes con responsables y `wbs.csv` → `pm-cronograma-estimacion` y `pm-costos-presupuesto`; candidatos a compra → `pm-adquisiciones`; dependencias externas → `pm-riesgos`. Como subagente, cerrar con el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido se aplica dentro de las etapas (épicas e historias como productos), sin eliminar puertas.
2. [PRINCE2] Alcance previsto fuera de tolerancia se escala a `pm-director` como excepción; nunca se recortan productos en silencio.
3. [PRINCE2] Nada se aprueba sin acto humano registrado (puerta en `estado.json` y fila en `decisiones.csv`).
4. [PRINCE2] Primero productos, después actividades: la WBS se deriva de la PBS, no al revés.
5. [PRINCE2] Lo que no está en una descripción de producto aprobada no está en el alcance; trabajo que no rastrea al plan es solicitud de cambio.
6. [PRINCE2] Cada descripción nombra productor, revisor independiente y autoridad de aceptación; cada paquete de la WBS, un único responsable.
7. [PRINCE2] Los criterios de aceptación se priorizan (MoSCoW); la priorización fija la tolerancia de alcance.
8. [PMBOK→Plans] Regla del 100 %; esfuerzo y costo en hojas, consolidados con `wbs.py`; planificación gradual.
9. [PMBOK→Quality] Trazabilidad requisito ↔ paquete por la columna `ref`; sin BMAD, RTM con cobertura hacia adelante y atrás.
10. Dueño único de requisitos: sin BMAD esta skill; con BMAD el PRD. Aquí solo se citan ids.
11. Dueños del alcance (SPEC §1.10.11): QUÉ aquí; CÓMO (`plan-gestion-alcance-requisitos`) en `pm-enfoques-gestion`.
12. [Plantillas] Versión mínima o completa según riesgo, costo, proveedores y stakeholders.
13. Transparencia de IA: todo borrador; `[por confirmar]` en vez de inventar; citar la fuente de cada cifra.
14. Escrituras externas (tracker, chat) solo con confirmación, vía `pm-integraciones`. Más reglas en `references/guia.md` §7.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Descripción del producto del proyecto | `templates/descripcion-producto-proyecto.md` | `02-planificacion/descripcion-producto-proyecto.md` | `descripcion-producto-proyecto` |
| PBS ↔ WBS y registro de productos | `templates/pbs-wbs.md` | `02-planificacion/pbs-wbs.md` (o `-etapa-<n>`) | `pbs-wbs` |
| WBS en CSV + diagrama | `templates/wbs.csv` + `wbs.py` | `02-planificacion/wbs.csv`, `visuales/wbs.md` | en `pbs-wbs` |
| Descripciones de producto | `templates/descripcion-producto.md` | `02-planificacion/productos/<id>-<nombre>.md` | `descripcion-producto-<id>` |
| Flujo de productos | `templates/flujo-productos.md` | `02-planificacion/flujo-productos.md` | `flujo-productos` |
| Enunciado del alcance | `templates/enunciado-alcance.md` | `02-planificacion/enunciado-alcance.md` | `enunciado-alcance` |
| Requisitos (solo sin BMAD) | `templates/requisitos.md` | `02-planificacion/requisitos.md` | `requisitos` |
| RTM (solo sin BMAD) | `templates/matriz-trazabilidad.md` | `02-planificacion/matriz-trazabilidad.md` | `matriz-trazabilidad` |
| Diccionario de la WBS | `templates/diccionario-wbs.md` | `02-planificacion/diccionario-wbs.md` | `diccionario-wbs` |

## Calidad
- [ ] Descripción del producto del proyecto con criterios priorizados y método/responsable de aceptación.
- [ ] PBS con regla del 100 %, externos e intermedios marcados, sin actividades.
- [ ] `wbs.py` corre sin errores; sin avisos pendientes; cada paquete con responsable; cada producto hoja con paquete.
- [ ] Descripciones medibles con productor, revisor y autoridad; PFD con Inicio/Fin y dependencias externas como riesgos.
- [ ] Enunciado = entregables de nivel superior de la PBS, con exclusiones explícitas.
- [ ] Sin BMAD: requisitos atómicos y RTM con cobertura; con BMAD: ningún requisito copiado, `ref` con ids válidos.
- [ ] Totales de `wbs.py` coherentes con estimación y presupuesto cuando existen.
- [ ] Frontmatter completo, `borrador` hasta la puerta; `[por confirmar]` listados.

## Escalamiento y excepciones
- Alcance fuera de tolerancia o criterios en conflicto entre usuario y proveedor sénior → `pm-director`.
- Requisito nuevo tras la línea base (o desvío del PRD con BMAD) → `pm-issues-cambios` como solicitud de cambio; esta skill no modifica la PBS aprobada.
- Paquete candidato a compra → `pm-adquisiciones` antes de costear. Más casos en `references/guia.md` §8.
- Como subagente: decisiones humanas (aprobar descripciones, criterios en conflicto) en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Armá la PBS y la WBS del proyecto Faro con responsables y el diagrama de wbs.py."
- "Escribí la descripción de producto del módulo de notificaciones con criterios de calidad medibles."
- EN: "Build the product breakdown structure and product flow diagram for the next stage."
- EN: "Create the WBS dictionary and roll up effort and cost per level."
- No activa: "Trazá los FR del PRD de BMAD a los paquetes" → `pm-bmad-puente`.

## EN summary
Product-based planning: project product description with prioritized acceptance criteria, PBS mapped one-to-one to work packages, product descriptions with measurable quality criteria and named producer/reviewer/acceptor, product flow diagram, scope statement and WBS dictionary. The WBS lives in `wbs.csv`; `wbs.py` validates it, rolls up effort/cost and draws a Mermaid tree. Without BMAD it also writes requirements and the RTM; with BMAD it only cites PRD ids in `ref`, and pm-bmad-puente derives the traceability matrix.
