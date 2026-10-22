---
name: pm-acta-constitucion
description: "Acta de constitución y PID ensamblado (controles, adaptación, consistencia). Usar: acta de constitución, PID, project charter, autorizar proyecto. No: enfoques de gestión→pm-enfoques-gestion."
version: 2.4.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-inicio
    procesos_prince2: [IP, DP]
    practicas_prince2: [business-case, organizing, plans, progress]
    tecnicas_pmbok: [acta de constitución, matriz de alineación, adaptación (tailoring), análisis de consistencia]
    artefactos: [acta-constitucion, pid]
    idiomas: [es, en]
---

# Acta de constitución y PID · Project charter and PID

## Cuándo usar / When to use
- Con `autorizar-inicio` aprobada: **acta de constitución** (project charter) y/o **documentación de inicio del proyecto** (PID).
- **Ensamblar** el PID desde componentes de otras skills: definición, enfoque, business case, estructura y roles, enfoques de gestión, plan de proyecto, controles, adaptación.
- Elegir **versión mínima, compacta o completa** y ejecutar el **checklist de consistencia** antes de `autorizar-proyecto`.
- **Actualizar** y volver a fijar como línea base el PID al fin de etapa o tras una excepción, conservando la versión que autorizó.
- EN: draft the charter, assemble the PID, check consistency before `autorizar-proyecto`, re-baseline at stage boundaries.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. etiquetas bilingües. "Acta de constitución" = charter; "PID" = paquete PRINCE2; si se mezclan, aclarar el mapeo una vez.

## Conocimiento
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §1.4.1 (PID) y §1.5 (adaptación).
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §5.3 act. 1, 3, 6 y §5.2 act. 2; `prince2-practicas-riesgo-issues-progreso-productos.md` §5.4 A12, §5.3.
- `pm-knowledge/references/plantillas-inicio-y-planes.md` §2.5 (acta), §4.3, §4.4, §6.3; `plantillas-documentos-registros-reportes.md` §40.
- `pm-knowledge/references/pmbok8-dominios-procesos-adaptacion.md` §3.4–3.6 (adaptación).
- `references/guia.md`: formato (§1), PID compacto (§2), controles (§3), adaptación (§4), consistencia (§5), BMAD (§6), reglas extendidas (§7), casos borde (§8).

## Entradas requeridas
- `estado.json` con fase `inicio`, proceso `IP` y puerta `autorizar-inicio` aprobada; si falta, derivar a `pm-mandato-y-brief` / `pm-director`.
- Componentes: project brief, business case, estructura y roles, `02-planificacion/enfoques/*.md`, `plan-proyecto.md`, enfoques de beneficios y sostenibilidad, `estado.json.tolerancias` y `.roles` (dueñas al pie de la tabla de artefactos).
- Componente ausente: producirlo con su skill dueña o dejarlo `[por confirmar]` en el índice con la razón (decisión del usuario).
- Para el acta: presupuesto preaprobado y fuente, ejecutivo y gestor con su autoridad, hitos del roadmap, interesados clave.
- Si `integraciones.especificacion = bmad`: inventario y línea base prevista del PRD vía `pm-bmad-puente` (el PID referencia, no copia).

## Procedimiento
1. **Leer el estado** y confirmar `autorizar-inicio`. Listar componentes presentes y ausentes con ruta, versión y estado.
2. **Elegir formato** (acta sola, PID solo, ambos; mínimo, compacto o completo) con la tabla de `references/guia.md` §1. 🔒 **Puerta humana 1**: el usuario confirma; fila en `decisiones.csv`.
3. **Redactar el acta** → `templates/acta-constitucion.md` en `01-inicio/acta-constitucion.md`: copiar (no reescribir) objetivos, criterios de éxito y presupuesto del business case; entregables, exclusiones, hitos e interesados del brief; riesgo general en dos líneas con criterio declarado; autoridad del gestor en cuatro dimensiones con cifras y la del patrocinador complementaria; criterios de salida objetivos.
4. **Adaptación**: técnicas propias sustituidas, terminología, productos combinados u omitidos y por qué (`references/guia.md` §4).
5. **Controles** (si `pm-enfoques-gestion` no los consolidó): etapas (1 = iniciación; entrega 2…n), tolerancias por nivel, informes, escalado, autoridad delegada, presupuestos de riesgo y cambio; comprobar contra `estado.json.tolerancias` (`references/guia.md` §3).
6. **Ensamblar el PID** → `templates/pid.md` en `00-direccion/pid.md`: completo = índice con ruta, versión, estado, creador, revisor y aprobador por componente; mínimo = texto resumido; compacto = perfil ágil (`references/guia.md` §2). Con BMAD, la sección de enfoque y la de plan citan brief de producto, PRD y arquitectura por ruta y sha (`references/guia.md` §6).
7. **Checklist de consistencia** (`references/guia.md` §5): presupuesto, hitos, tolerancias, roles, escalas, descripciones de producto, adaptación. Reportar discrepancias con ambas rutas; no corregir en silencio.
8. **Precondiciones de `autorizar-proyecto`**: business case completo coherente con plan y riesgo; plan con PBS (o PRD citado), descripciones y etapas; enfoques; enfoque de beneficios; lecciones; riesgos con respuesta; plan de la etapa 2 (`pm-plan-etapa-y-limites`). Con BMAD: PRD `final` y `bmad.py verificar` sin desvíos. Lo que falte es bloqueante.
9. **Registrar**: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> artefacto acta-constitucion --ruta 01-inicio/acta-constitucion.md --estado en-revision` y `... artefacto pid --ruta 00-direccion/pid.md --estado en-revision --version 0.9`; copia en `00-direccion/historial/pid-v0.9.md`. El paquete de la puerta lo arma `pm-direccion-decisiones`.
10. 🔒 **Puerta humana 2 (fuera de esta skill)**: la junta decide `autorizar-proyecto` (normalmente con `autorizar-etapa` de la etapa 2); solo `pm-director` registra (`estado.py puerta autorizar-proyecto ...`), aprueba (`estado.py aprobar pid --por "Junta: <ejecutivo>" --version 1.0`) y, con BMAD, fija `bmad.py linea-base prd --version 1.0`. Luego se congela `00-direccion/historial/pid-v1.0.md`; si fue `condicionado`, listar condiciones hasta `estado.py cumplir-condiciones autorizar-proyecto`.
11. **Relínea base** (fin de etapa o excepción): incorporar solo cambios aprobados, nueva versión 1.x, nunca sobrescribir la 1.0; diferencias en "Historial de versiones".
12. **Cerrar** con estado del PID, discrepancias, bloqueantes, rol que decide y siguiente paso; como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas, documentado en el enfoque del proyecto y en los controles; nunca sin puertas.
2. [PRINCE2] Desviación prevista fuera de tolerancia → excepción; nunca absorbida.
3. [PRINCE2] El PID pasa a 1.0 solo con `autorizar-proyecto` registrada por `pm-director`; esta skill deja todo `en-revision` y nunca "firma".
4. [PMBOK→Organizing/IP] La autoridad del gestor se define en cuatro dimensiones (personal, presupuesto y umbral de escalado, decisiones técnicas, conflictos) con cifras; la del patrocinador es complementaria.
5. [Plantillas] Mínima (acta de una página fusionada con el enunciado del alcance; PID breve) para proyectos pequeños; completa (PID índice, acta de tres páginas) cuando riesgo, costo o interesados lo justifiquen; compacta en perfil ágil mínimo.
6. Transparencia de IA: borrador, sin datos inventados, cada cifra con fuente.
7. Idioma del usuario; artefactos con nombre EN la primera vez.
8. Escrituras externas (publicar el PID en una wiki conectada, enviarlo) solo con confirmación, vía `pm-integraciones`.
9. [PRINCE2] El PID con el plan de etapa es el "contrato" gestor–junta: tolerancias, autoridad delegada y escalado escritos con cifras.
10. [PRINCE2] El PID puede ser un índice de documentos; lo que no falta es la referencia cruzada entre componentes.
11. [PRINCE2] La versión que autorizó el proyecto se conserva intacta; las actualizaciones crean versiones comparables.
12. [PRINCE2] Sustituir una técnica propia del método es adaptación documentada; sustituir técnicas de apoyo (RACI, Gantt, NPV) no lo es.
13. [Plantillas] Los datos de fuente única se copian del artefacto donde nacen; una discrepancia es un hallazgo.
14. Dueño único (SPEC §1.13): con BMAD, el PID referencia brief de producto, PRD y arquitectura; nunca transcribe requisitos.
Más reglas: `references/guia.md` §7.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | Clave |
|---|---|---|---|
| Acta de constitución (project charter) | `templates/acta-constitucion.md` | `01-inicio/acta-constitucion.md` | `acta-constitucion` |
| PID | `templates/pid.md` | `00-direccion/pid.md` (+ `historial/pid-vX.Y.md`) | `pid` |
| Adaptación de PRINCE2 | sección del PID | `00-direccion/pid.md` §8 | `pid` |
| Controles del proyecto | sección del PID (tolerancias propuestas; las registra pm-director con `estado.py tolerancia` al aprobarse) | `00-direccion/pid.md` §7 y `estado.json.tolerancias` | `pid` |
| Consistencia entre componentes | sección "Consistencia" | `00-direccion/pid.md` §9 | `pid` |

Componentes y skill dueña: definición y enfoque (`pm-mandato-y-brief`), business case y enfoques de beneficios y sostenibilidad (`pm-caso-de-negocio`), estructura y roles (`pm-organizacion-roles`), enfoques de gestión (`pm-enfoques-gestion`), plan de proyecto (`pm-planificacion-por-productos`, `pm-cronograma-estimacion`, `pm-costos-presupuesto`), plan de etapa (`pm-plan-etapa-y-limites`), especificación BMAD (`pm-bmad-puente`).

## Calidad
- [ ] `autorizar-inicio` verificada; formato y versión acordados y registrados.
- [ ] Acta: objetivos con criterio de éxito, exclusiones, autoridad en cuatro dimensiones con cifras, hitos, presupuesto con fuente, criterios de salida objetivos.
- [ ] PID: ocho componentes presentes, referenciados o `[por confirmar]` con razón; cada uno con ruta, versión, estado, creador, revisor, aprobador.
- [ ] Controles coinciden con `estado.json`; tolerancias con notación canónica por nivel.
- [ ] Adaptación justificada; checklist de consistencia ejecutado con rutas.
- [ ] Con BMAD: artefactos citados por ruta y sha; ningún requisito transcrito; `verificar` limpio.
- [ ] Precondiciones de `autorizar-proyecto` y bloqueantes listados; copia en `historial/`; `aprobado_por` vacío.

## Escalamiento y excepciones
- Sin `autorizar-inicio` → no ensamblar; `pm-director` o `pm-mandato-y-brief`.
- Componente clave ausente que no se quiere producir → la junta no puede autorizar con un caso en esbozo; confirmación explícita y excepción al método registrada.
- Discrepancias no resueltas por sus dueños → issue `problema-preocupacion` + acción `A-###`; PID no apto para la puerta (detalle en `references/guia.md` §8).
- Pedido de "firmar" desde el agente → rechazar; aprueba la junta y registra `pm-director`.
- Como subagente: formato, discrepancias a decidir y bloqueantes se devuelven en el bloque de retorno, no se preguntan desde el subagente.

## Ejemplos de invocación
- "Ya tenemos brief, business case, roles y enfoques: armá el PID y decime qué falta para autorizar el proyecto."
- "Revisá que el PID sea consistente: el presupuesto del acta no coincide con el del business case."
- EN: "Assemble the PID as an index and fill the tailoring section: we use the corporate risk procedure."
- EN: "Small agile team: give me a compact PID with the backlog instead of a full WBS."
- No activa: "Escribí el enfoque de gestión de riesgos" → `pm-enfoques-gestion`.

## EN summary
Produces the authorisation package: the project charter and/or the PRINCE2 PID assembled from approved components, plus project controls and the tailoring section. Verifies `autorizar-inicio`, agrees the format (minimal, compact, full) at a human gate, copies single-source data, runs a cross-component consistency check, lists `autorizar-proyecto` blockers and leaves everything in review. With BMAD the PID cites the product brief, PRD and architecture by path and hash. pm-director records the gate and freezes version 1.0.
