---
name: pm-calidad
description: "Calidad y aceptación de productos. Usar: registro de calidad, revisar o auditar la calidad de un entregable, criterios de aceptación, aceptar producto, quality review, DoD. No: off-spec→pm-issues-cambios; consistencia→pm-sanidad."
version: 2.5.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [IP, CS, MP, SB, CP]
    practicas_prince2: [quality, plans, issues]
    tecnicas_pmbok: [inspección, pruebas, auditoría de calidad, costo de la calidad, gráficos de control, definición de hecho, matriz de trazabilidad]
    artefactos: [calidad.csv, revision-calidad, auditoria-calidad, registro-aceptacion, aceptacion-producto, criterios-calidad-producto, costo-calidad]
    idiomas: [es, en]
---

# Gestión de la calidad · Quality management

## Cuándo usar / When to use
- Planificar la calidad de una etapa o paquete: criterios y tolerancias por producto, métodos de verificación y alta en el registro de calidad.
- Preparar, conducir y cerrar una revisión de calidad; registrar la aceptación formal de un producto o por requisito.
- Conducir una auditoría de calidad; estimar el costo de la calidad; definir DoD y pruebas de aceptación en ágil.
- EN: plan quality criteria, methods and register entries for a stage or package.
- EN: run a quality review, record product acceptance, audit quality, define the definition of done.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Términos EN la primera vez: quality register, quality review, acceptance criteria, quality tolerance, quality audit, cost of quality, definition of done. Plantillas bilingües.

## Conocimiento
- `references/guia.md` (esta skill): planificación §1, métodos por madurez §2, costo de la calidad §3, revisión §4, aceptación §5, BMAD §6, auditoría §7, ágil §8, columnas §9, flujo y reglas extendidas §10.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §5 (conceptos, técnica de tres pasos, tipos de verificación, revisión, criterios, registro, contextos); §6.5.
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.10 Familia J Calidad.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §36 auditoría; §17 historia de usuario; Parte V `hallazgos_auditoria.csv`.

## Entradas requeridas
- `estado.json`: fase, `enfoque_entrega`, tolerancia de calidad (si vacía, proponer `[por confirmar]`), roles (usuario sénior, aseguramiento), `integraciones`.
- Descripción del producto del proyecto (`02-planificacion/descripcion-producto-proyecto.md`); si falta, `pm-planificacion-por-productos`.
- Enfoque de calidad (`02-planificacion/enfoques/enfoque-calidad.md`); si falta, versión mínima con `pm-enfoques-gestion`.
- Descripciones de producto (`02-planificacion/productos/<producto>.md`) y `03-control/registros/calidad.csv` (`${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> esquema calidad`).
- Revisión: producto, descripción y revisores. Auditoría: alcance y auditor independiente. Aceptación: evidencia de control y autoridad.
- **Especificación (fuente única, SPEC §1.16)**: criterios por historia, NFR y cobertura solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar requisitos|historias` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: `calidad.csv`, revisiones y registros de aceptación, que citan ids.

## Procedimiento
### A. Planificar
1. Listar los productos a controlar y verificar que cada descripción tenga especificaciones medibles, funcionales y no funcionales (`references/guia.md` §1). Lo que no está escrito y aprobado no es requisito.
2. Por producto, criterios, tolerancia y prioridad.
3. Elegir el método de verificación según madurez (guía §2) y codificarlo con uno de los cinco valores de `calidad.csv`; comprobar recursos en cronograma y presupuesto.
4. Nombrar productor, revisores independientes y autoridad de aceptación; productor ≠ revisor.
5. Alta de cada actividad con `registro.py agregar calidad` (estado `planificada`; guía §1).
6. Costo de la calidad cuando lo justifique el proyecto (guía §3).
7. **PUERTA HUMANA — Aprobar la planificación.** Usuario sénior (descripciones), ejecutivo (enfoque); `estado.py aprobar <clave> --por "<rol: nombre>"`; si es parte de una puerta de la junta, la registra `pm-director`. Hasta entonces, borrador.

### B. Controlar: revisión de calidad
8. **Preparar** con `templates/revision-calidad.md`: roles (presidente, presentador, revisores, administrador), material con antelación; estructura propuesta por el paquete, declarada como tal (guía §4).
9. **Reunir:** observaciones contra criterios (mayor, menor, observación), acciones con responsable y fecha; resultado `aprobado`, `aprobado-con-observaciones` o `rechazado`. Si se requiere acta formal de la reunión, `pm-reuniones`.
10. **Seguir:** actualizar la fila Q-nnn, correcciones a `acciones.csv` (`origen=Q-nnn`), cierre verificado antes de aceptar. Si no puede aprobar dentro de la tolerancia → off-specification vía `pm-issues-cambios`; nunca relajar la especificación.

### C. Aceptar
11. Reunir las dos evidencias (control + revisión independiente) y completar `templates/registro-aceptacion.md`; clave `aceptacion-<producto>` para intermedios, `registro-aceptacion` solo para el producto del proyecto (guía §5).
12. **Aceptación por requisito**: cobertura `terminado` en `listar requisitos` de la fachada (con BMAD, la RTM de `bmad.py trazabilidad` es anexo); DoD y code review como métodos de calidad registrados en `calidad.csv`; `done` en BMAD no sustituye la aceptación (guía §6); sanidad QUA-01…04 lo controla a volumen (guía §8.1).
13. **PUERTA HUMANA — Aceptación.** La autoridad nombrada acepta o rechaza explícitamente; `estado.py aprobar aceptacion-<producto> --por "<rol: nombre>" --nivel gestor|junta`; el estado de productos lo deriva `estado.py productos` (`pm-paquetes-trabajo`). Contractual antes que la del proyecto. El producto del proyecto lo conduce `pm-cierre-proyecto`.

### D. Auditar
14. Alcance, áreas y auditor independiente con `templates/auditoria-calidad.md`; comparar planificado vs. `calidad.csv`; hallazgos con acción, responsable, fecha y estado; seguimiento programado (guía §7).

### E. Ágil o híbrido y cierre
15. DoD y definición de listo en el enfoque, criterios por historia, una fila por incremento o historia significativa, demo como evidencia registrada (guía §8).
16. **Cerrar** con ids (Q-, I-, L-, D-), productos pendientes de aceptación y próxima puerta con su rol; si corre como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; DoD y pruebas por historia operan dentro de las etapas y no sustituyen la aceptación formal por la autoridad nombrada.
2. [PRINCE2] Producto que no alcanza su especificación dentro de la tolerancia → off-specification vía issues; nunca se ajusta la especificación en silencio.
3. [PRINCE2] Nada aprobado ni aceptado sin acto humano registrado (`decisiones.csv`, registro de aceptación, `estado.json`).
4. [PRINCE2] Solo es requisito lo escrito en un producto de gestión aprobado; con BMAD, el requisito vive en el PRD y se cita por id.
5. [PRINCE2] Productor, revisor independiente y autoridad de aceptación nombrados por producto; delegaciones en el enfoque.
6. [PRINCE2] El control empieza al aprobarse la descripción: alta inmediata en el registro con fechas previstas y reales, resultado y evidencia.
7. [PRINCE2] Aceptación con dos evidencias: control del proyecto y revisión independiente contra criterios.
8. [PMBOK→Quality/MP] Técnica según la pregunta: inspección, prueba, auditoría, gráfico de control, costo de la calidad; declarar supuestos.
9. [PMBOK→Quality/CS-CP] La cobertura `terminado` de la fachada es la evidencia por requisito; DoD y code review son métodos de calidad.
10. [PMBOK→Quality/CS] Auditoría como ayuda: busca buenas prácticas, no conformidades y confirma acciones previas.
11. [Plantillas] Versión mínima (inspección, una ronda de aceptación, registro en una hoja) o completa (producto nuevo, complejo, regulado o contratado).
12. Transparencia de IA: borrador; nunca inventar resultados ni fechas; `[por confirmar]`; citar la fila Q-nnn o el acta.
13. Escrituras externas (tracker de pruebas, correo, chat) solo con confirmación explícita, vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla / herramienta | Ruta de salida | estado.json |
|---|---|---|---|
| Registro de calidad | `registro.py agregar/actualizar calidad` | `03-control/registros/calidad.csv` | — |
| Criterios y tolerancias por producto | descripción de producto (`pm-planificacion-por-productos`) | `02-planificacion/productos/<producto>.md` | `descripcion-producto-<id>` |
| Acta de revisión de calidad | `templates/revision-calidad.md` | `03-control/reportes/AAAA-MM-DD-revision-calidad-<producto>.md` | `revision-calidad-<producto>` |
| Aceptación de producto | `templates/registro-aceptacion.md` | intermedio `03-control/reportes/AAAA-MM-DD-aceptacion-<producto>.md`; proyecto `04-cierre/registro-aceptacion.md` | `aceptacion-<producto>` / `registro-aceptacion` |
| Auditoría de calidad | `templates/auditoria-calidad.md` | `03-control/reportes/AAAA-MM-DD-auditoria-calidad.md` | `auditoria-calidad-AAAA-MM-DD` |
| Costo de la calidad | tabla | `02-planificacion/costo-calidad.md` | `costo-calidad` |
| DoD / definición de listo | sección del enfoque | `02-planificacion/enfoques/enfoque-calidad.md` | `enfoque-calidad` |

Columnas de `calidad.csv` y equivalentes EN: `references/guia.md` §9.

## Calidad
- [ ] Cada producto con descripción aprobada y especificaciones medibles; productor ≠ revisor; autoridad nombrada.
- [ ] Todo producto del plan con al menos una fila en `calidad.csv`; realizadas con fecha real y resultado.
- [ ] Revisión con roles, observaciones contra criterios, acciones y resultado registrados.
- [ ] Aceptación con dos evidencias, nombre, fecha y fila en `decisiones.csv`; claves correctas.
- [ ] Aceptación lista ids con cobertura `terminado` y pendientes (fachada), sin copiar el PRD.
- [ ] Off-specifications en `issues.csv`; auditoría independiente con seguimiento.
- [ ] En ágil: DoD y listo documentadas; criterios por historia.

## Escalamiento y excepciones
- Producto que no cumple su especificación → `pm-issues-cambios`; concesión solo por la junta o la autoridad de cambio; si afecta la tolerancia de etapa → `pm-director`.
- Conflicto entre contrato y descripciones → `pm-adquisiciones` y `pm-director`.
- Hallazgo mayor de auditoría → `pm-director` y aseguramiento.
- Como subagente (pm-control): aprobaciones y aceptaciones van como decisiones humanas en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Planificá la calidad de la etapa 2: estos son los productos; dame las actividades para el registro de calidad."
- "¿Qué FR del PRD ya podemos dar por aceptados en el release 1? Armá el registro de aceptación."
- EN: "Run a quality audit on stage 1: check the quality register coverage and the approved changes."
- EN: "Define the definition of done and acceptance tests for the next three sprints."
- No activa: "El módulo no cumple el tiempo de respuesta; ¿lo aceptamos como concesión?" → `pm-issues-cambios`.

## EN summary
PRINCE2 three-step quality technique (plan, control, accept) with PMBOK techniques: measurable criteria and tolerances per product, verification methods by maturity, independent reviewers and named acceptance authority, all in calidad.csv.
Quality reviews record results and actions; unrecoverable failures become off-specifications. Acceptance is a human gate with two evidences; contractual acceptance comes first.
Acceptance per requirement uses `terminado` coverage from `especificacion.py` and DoD/code review are quality methods. Also covers audits, cost of quality and agile DoD.
