---
name: pm-paquetes-trabajo
description: "Paquetes de trabajo (WP) y product status account. Usar: autorizar paquete, work package, plan de equipo, recibir paquete, sprint como paquete, team plan. No: plan de etapa→pm-plan-etapa-y-limites."
version: 2.5.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [CS, MP]
    practicas_prince2: [plans, quality, progress, organizing]
    tecnicas_pmbok: [porcentaje completado, burn-down, gestión del equipo, seguridad psicológica]
    artefactos: [descripcion-paquete-trabajo, plan-de-equipo, product-status-account, estado-paquetes, calidad.csv, decisiones.csv]
    idiomas: [es, en]
---

# Paquetes de trabajo y entrega de productos · Work packages and product delivery

## Cuándo usar / When to use
- El plan de etapa está aprobado y hay que asignar trabajo a un equipo: "autorizá el paquete de trabajo".
- Un gestor de equipo acepta, ejecuta e informa un paquete; el gestor del proyecto lo recibe y comprueba calidad y aprobaciones.
- Se pide el estado de productos (product status account) o de los paquetes en curso; una iteración o sprint se gestiona como paquete.
- EN: co-create, authorize, execute and receive a work package with a team manager.
- EN: produce a product status account; run a sprint as a work package inside a stage.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. plantillas con etiquetas bilingües. La primera vez, nombrar el equivalente EN (work package description, team plan, checkpoint report, product status account).

## Conocimiento
- `references/guia.md` (esta skill): contenido del WP §1, registro de actos §2, flujo §3, completitud §4, product status account §5, `calidad.csv` §6, ágil §7, BMAD §8, proveedores y casos borde §9.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §5.4 (CS: autorizar, evaluar, recibir), §5.5 (MP), §8.4 reglas 20–24, §8.7 regla 42.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §4.5.3 descripción de paquete; §5.5.1 descripción de producto; §5.5.4 registro de productos.
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §4.d checkpoint; §5.4 A13 y A15.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §27 y §32 (checkpoint de equipo y de contratista).

## Entradas requeridas
- `estado.json` con `fase = entrega`, `proceso_actual = CS` y `autorizar-etapa` (o `autorizar-plan-excepcion`) aprobada. Si falta, detenerse y derivar a `pm-director`.
- Plan de etapa aprobado con productos y descripciones de producto (propósito, especificaciones de calidad, productor, revisor, autoridad de aceptación); si faltan, `pm-planificacion-por-productos` o `pm-calidad`.
- Tolerancias de etapa en `estado.json.tolerancias`; gestor de equipo; si es proveedor, contrato (`pm-adquisiciones`).
- `enfoque_entrega` para elegir variante predictiva o iterativa.
- **Especificación (fuente única, SPEC §1.16)**: historias del sprint o épica del paquete y sus estados solo vía `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/especificacion.py --proyecto <dir> resumen|consultar <id>|listar historias --epica <E>` (igual con o sin BMAD; nunca abrir BMAD ni `requisitos.md`). Escribe como dueña: el paquete de trabajo (alcance = ids de historias, sin copiar texto).
- Opcional: tracker vía `pm-integraciones` (instantánea en `03-control/fuentes/`; escribir solo con confirmación).

## Procedimiento
1. **Situar el trabajo.** Leer `estado.json` y el plan de etapa: productos pendientes, dependencias y equipo. Granularidad: `references/guia.md` §1.
2. **Co-crear la descripción** con el gestor de equipo en `templates/paquete-trabajo.md` (campos en guía §1). Criterios de aceptación citados de la descripción de producto o por id de historia. Marcar borrador.
3. **Derivar tolerancias** del paquete dentro de las de la etapa y declarar el reparto; si no caben, ajustar el plan de etapa o escalar (guía §1).
4. **Revisar el plan de equipo** (o extracto de hitos; en ágil, backlog de la iteración). Si los productos no caben en las restricciones, renegociar alcance o escalar.
5. **Revisores de calidad.** Con aseguramiento, confirmar revisores independientes del productor y dar de alta las actividades en `calidad.csv` (`pm-calidad` o `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> agregar calidad`; columnas en guía §6).
6. **PUERTA HUMANA — Autorizar y aceptar.** El gestor del proyecto autoriza y el gestor de equipo acepta explícitamente. Registrar en el bloque **Acuerdo / Agreement** del WP, `estado.py artefacto/aprobar` y la fila de aceptación `nivel=equipo` (guía §2). `estado_paquete: autorizado`. Sin este acto el trabajo no comienza.
7. **Ejecutar y seguir.** El equipo produce según las descripciones, ejecuta las actividades de calidad y actualiza `calidad.csv`. Checkpoints a la frecuencia pactada vía `pm-progreso-reportes` (en ágil, tablero por "pull").
8. **Tratar desviaciones.** Dentro de tolerancia del paquete → acción correctiva anotada en el checkpoint. Fuera → issue al gestor del proyecto (`pm-issues-cambios`), que decide dentro de la tolerancia de etapa o escala como excepción. Producto que no alcanzará su especificación → off-specification: completar o concesión.
9. **Verificar antes de entregar.** Por producto: actividad de calidad `aprobado` en `calidad.csv`, aprobación fechada de la autoridad nombrada y estado actualizado en el product status account. Si falta algo, el paquete no está completo (criterios en guía §4).
10. **PUERTA HUMANA — Notificar y recibir.** El gestor de equipo notifica con desempeño contra lo acordado, issues, riesgos y lecciones. El gestor del proyecto comprueba, actualiza el plan de etapa y registra la recepción (`decisiones.csv`, `nivel=gestor`); `estado_paquete: completado` (estado operativo vs documental: guía §2).
11. **Product status account** cuando se pida (fin de etapa, cierre, excepción, auditoría): `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> productos [--corte] [--alcance WP-###] [--markdown]` deriva el estado de cada producto y las diferencias registrado/físico (guía §5); la persona completa lo que queda `[por confirmar]`.
12. **Variantes.** Ágil/híbrido: la iteración es el paquete, DoD = criterios de calidad, intercambios del PO dentro de tolerancia sin cambio (guía §7). Con BMAD: sprint = paquete, historias = productos (estado por la fachada), DoD y code review como métodos de calidad (guía §8). Proveedores: guía §9.
13. **Cerrar** con ids creados (WP-nnn, Q-, D-), estado de cada producto, próxima puerta y quién decide; como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas (iteraciones como paquetes), sin eliminar puertas.
2. [PRINCE2] Desviación prevista fuera de tolerancia del paquete → issue al gestor del proyecto; fuera de la de etapa → excepción a `pm-director`; nunca se absorbe.
3. [PRINCE2] Nada aprobado sin acto humano explícito registrado (autorización, aceptación, aprobación de cada producto) en `decisiones.csv` y `estado.json`.
4. [PRINCE2] Ningún paquete sin plan de etapa aprobado ni sin descripción co-creada y aceptada, con productos, criterios, aprobadores, tolerancias y frecuencia de informe.
5. [PRINCE2] Ningún paquete completo sin aprobación de la autoridad designada por producto y actividades de calidad en el registro de calidad.
6. [PRINCE2] Trabajo que no mapea a un producto con descripción se cuestiona o es solicitud de cambio.
7. [PRINCE2] Tolerancias del paquete dentro de las de etapa; el gestor de equipo actúa con autonomía dentro de ellas.
8. [PRINCE2] Off-specification: completar o concesión aprobada; nunca desaparece. Productor y revisor nunca son la misma persona.
9. [PRINCE2] Con proveedor externo, el paquete es instrucción conforme al contrato; la aceptación contractual precede a la del proyecto.
10. [PMBOK→Progress/CS] Métrica de avance según la pregunta (% por producto, burn-down, EVM con línea base); declarar supuestos y fórmulas.
11. [PMBOK→Plans/MP] Mapeo ágil: iteración↔paquete, ítem↔producto, DoD↔criterios de calidad, tablero↔checkpoint.
12. [Plantillas] Versión mínima (una página) o completa (plan de equipo, interfaces) si hay proveedores, riesgo o varios equipos.
13. Transparencia de IA: borrador, `[por confirmar]`, cada estado de producto cita su fila de `calidad.csv`.
14. Escrituras externas (tracker, correo, chat) solo con confirmación explícita, vía `pm-integraciones`.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Descripción de paquete de trabajo | `templates/paquete-trabajo.md` | `03-control/paquetes-trabajo/WP-nnn-<nombre>.md` | `artefactos["WP-nnn"]` (documental); avance en `estado_paquete` del WP |
| Plan de equipo o extracto de hitos | sección del WP o archivo propio | `03-control/paquetes-trabajo/WP-nnn-plan-equipo.md` | anexo del WP-nnn |
| Product status account | `templates/product-status-account.md` (`estado.py productos --markdown`) | `03-control/reportes/AAAA-MM-DD-product-status-account.md` | `product-status-account` |
| Estado de paquetes | tabla en la respuesta o al pie del anterior | `03-control/reportes/AAAA-MM-DD-estado-paquetes.md` | — |
| Actividades de calidad | `registro.py agregar calidad` | `03-control/registros/calidad.csv` | — |
| Autorización, aceptación, recepción | `registro.py agregar decisiones` / `estado.py aprobar` | `03-control/registros/decisiones.csv` | puertas de junta: solo `pm-director` |

## Calidad
- [ ] Plan de etapa aprobado y puerta registrada antes de autorizar.
- [ ] Cada producto con descripción medible, productor, revisor independiente y autoridad de aceptación.
- [ ] Tolerancias del paquete declaradas y contenidas en las de etapa; frecuencia de checkpoint e interfaces fijadas; sin solapes entre paquetes.
- [ ] Actividades de calidad en `calidad.csv` al autorizar.
- [ ] Autorización, aceptación y recepción registradas con fecha y nombres; `estado_paquete` actualizado.
- [ ] Al recibir: todas las actividades con resultado, aprobaciones fechadas, off-specifications con decisión.
- [ ] Historias y requisitos leídos por la fachada y citados por id, no copiados.

## Escalamiento y excepciones
- Fuera de tolerancia del paquete → `pm-issues-cambios`; fuera de la de etapa → informe de excepción a `pm-director`.
- Off-specification → `issues.csv`; concesión solo por la junta o la autoridad de cambio.
- Conflicto de criterios entre contrato y descripción de producto → `pm-adquisiciones` y `pm-director`.
- Como subagente (pm-control): autorizaciones y recepciones humanas van en el bloque de retorno (SPEC §1.11) con id, decisión, quién y fecha.

## Ejemplos de invocación
- "Autorizá el paquete de trabajo del conector con la naviera B para el equipo de integración; la etapa 2 ya está aprobada."
- "El proveedor dice que terminó el módulo de facturación; ¿puedo recibir el paquete? Revisá calidad y aprobaciones."
- EN: "Set up sprint 4 as a work package: these are the committed backlog items and the definition of done."
- EN: "The team manager forecasts a 6-day slip on WP-003; the package tolerance is 4 days. What do we do?"
- No activa: "Armá el plan de la etapa 3 con sus tolerancias" → `pm-plan-etapa-y-limites`.

## EN summary
Implements the Controlling a stage ↔ Managing product delivery link: the project manager co-creates a work package with the team manager (products, interfaces, checkpoint cadence, tolerances nested in stage tolerances, acceptance criteria and approvers).
Two human gates — authorize/accept and notify/receive — are recorded in decisiones.csv and estado.json; a package is complete only when every product passed its quality activities and was approved.
Also produces the product status account. In agile/hybrid and BMAD delivery the sprint is the work package, stories map to products and DoD/code review are quality methods.
