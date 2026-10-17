---
name: pm-organizacion-roles
description: "Estructura de gestión, roles, RACI, análisis (poder/interés) y compromiso de interesados. Usar: junta, roles, RACI, interesados, stakeholders, engagement plan, team charter. No: plan de comunicación→pm-comunicacion-stakeholders."
version: 2.1.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-inicio
    procesos_prince2: [SU, IP, SB]
    practicas_prince2: [organizing]
    tecnicas_pmbok: [análisis de interesados, cuadrícula poder/interés, matriz RACI, acta del equipo, matriz de evaluación del compromiso]
    artefactos: [estructura-organizativa, descripcion-rol-<rol>, analisis-stakeholders, matriz-raci, team-charter, plan-compromiso-stakeholders, stakeholders.csv]
    idiomas: [es, en]
---

# Organización y roles · Organisation and roles

## Cuándo usar / When to use
- Diseñar la **estructura del equipo de gestión** (junta, gestor, equipos, aseguramiento, soporte, autoridad de cambio) y las **descripciones de rol**.
- Hacer el **análisis de interesados** (stakeholder analysis) y cargar `stakeholders.csv`; construir **RACI**, **team charter** y **plan de compromiso** (stakeholder engagement plan).
- Revisar en cada fin de etapa (SB); mapear roles ágiles o BMAD a los del método.
- EN: design the board and team, role descriptions, RACI, stakeholder analysis; map agile/BMAD roles.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. etiquetas bilingües; roles con nombre EN la primera vez. Columnas de `stakeholders.csv` en `snake_case` español (traducción en `references/guia.md` §7). Actitudes: circulación restringida.

## Conocimiento
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §3 (intereses, roles, diseño organizacional, RACI).
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §6 (responsabilidades base por rol) y §5.1 act. 1 y 4.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §10, §11, §16, §24; `plantillas-inicio-y-planes.md` §3.11.
- `pm-knowledge/references/pmbok8-dominios-procesos-adaptacion.md` §2.5 (interesados); `pmbok8-artefactos-tecnicas-anexos.md` §3.13 (roles ágiles).
- `references/guia.md`: diseño (§1), mapeo ágil y BMAD (§2), ágil mínimo (§3), interesados y RACI (§4), reglas extendidas (§5), ejemplo (§6), columnas CSV (§7), casos borde (§8).

## Entradas requeridas
- `estado.json` (fase SU o IP; `enfoque_entrega`; `roles` si existen).
- `00-direccion/mandato.md` (ejecutivo prospectivo) y `01-inicio/project-brief.md` o `canvas-arranque.md` (interesados, modelo de entrega).
- `03-control/registros/stakeholders.csv` (creado por `pm-estado-proyecto`; `registro.py esquema stakeholders` muestra columnas y valores).
- Organización permanente (estructura, proveedores, PMO); si falta, `[por confirmar]`.
- Para la RACI: PBS/WBS (`pm-planificacion-por-productos`) o, en SU, actividades de la etapa 1.
- Si hay un directorio conectado, leer nombres vía `pm-integraciones` (nunca inventar personas).

## Procedimiento
1. **Leer estado y mandato**: sin ejecutivo prospectivo, detener (bloqueante del método).
2. **Ecosistema organizacional y modelo de entrega** por bloque de trabajo (interno/externo/mixto; producto o mano de obra; aseguramiento; riesgo a quien mejor lo gestiona); ver `references/guia.md` §1. Con proveedores, enlazar con `pm-adquisiciones`.
3. **Diseñar la estructura** → `templates/estructura-organizativa.md` en `00-direccion/estructura-organizativa.md`: organigrama Mermaid, junta con tres intereses, gestor, equipos (o equipo ágil con punto de contacto), aseguramiento por interés, soporte, autoridad de cambio. Verificar reglas 9–11; prever estructuras por etapa.
4. **Mapear roles ágiles y BMAD** (si `enfoque_entrega` es `agil`/`hibrido` o `integraciones.especificacion = bmad`) con la tabla de `references/guia.md` §2; registrar como adaptación para el PID. El nombramiento del PO lo confirma el ejecutivo y lo registra `pm-director` (`estado.py rol product_owner="<nombre>"`); la cadencia la acuerda el equipo y también la registra `pm-director` (`estado.py agil cadencia_iteracion_dias=<n>`), como dice `pm-agil-hibrido`.
5. **Descripciones de rol** → `templates/descripcion-rol.md`, una por rol en `00-direccion/roles/descripcion-rol-<rol>.md`: persona, autoridad y límite (coherente con tolerancias), responsabilidades (incl. sostenibilidad y bienestar), rendición de cuentas, dedicación, combinaciones. En versión mínima, unas líneas por rol dentro de la estructura.
6. 🔒 **Puerta humana 1**: el ejecutivo confirma diseño y nombramientos; fila en `decisiones.csv` (`nivel=junta`) y `estado.py rol ejecutivo=... gestor_proyecto=... usuario_senior="A;B" proveedor_senior=... aseguramiento=... soporte=... autoridad_cambio=... jefes_equipo="X;Y"`. Si acompaña una puerta, queda `en-revision` para `pm-director`.
7. **Analizar interesados** → `templates/analisis-stakeholders.md` en `01-inicio/analisis-stakeholders.md` (restringido): lista amplia (internos, externos, reguladores, comunidad, operación), poder/interés con estrategia, actitud evaluada aparte, fuente por valoración, cuadrícula Mermaid (`references/guia.md` §4).
8. **Registro de interesados**: `registro.py agregar stakeholders --campo nombre=... --campo poder=... --campo interes=... --campo actitud=... --campo confidencial=si|no` (valores en `references/guia.md` §4). 🔒 **Puerta humana 2**: el usuario revisa las actitudes antes de guardarlas.
9. **RACI** → `templates/matriz-raci.md` en `02-planificacion/matriz-raci.md`: una A y ≥ 1 R por fila, sin columnas vacías, alertas de concentración (> 40 % de A en un rol) y sobre-consulta (> 3 C por fila).
10. **Team charter** → `templates/team-charter.md` en `01-inicio/team-charter.md`: borrador para el taller del equipo.
11. **Plan de compromiso** → `templates/plan-compromiso-stakeholders.md` en `02-planificacion/plan-compromiso-stakeholders.md`: actual/deseado, acción con responsable y fecha por brecha, demos en ágil/híbrido. Alimenta el enfoque de comunicación (`pm-enfoques-gestion`) y la matriz operativa (`pm-comunicacion-stakeholders`).
12. **Revisión en fin de etapa** (modo `revisar`): capacidad vs. responsabilidades, cambios de personas, autoridades delegadas, actitudes; lecciones sobre el ecosistema.
13. **Registrar** (`estado.py artefacto <clave> --ruta ... --estado borrador`) y cerrar con `[por confirmar]`, rol que decide y siguiente paso; como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas (equipo autoorganizado = gestor de equipo colectivo), nunca eliminando puertas ni roles de la junta.
2. [PRINCE2] Desviación prevista fuera de tolerancia → excepción; una brecha de capacidad que amenaza una tolerancia es un riesgo registrado.
3. [PRINCE2] Nada se aprueba sin acto humano registrado; los nombramientos los confirma el ejecutivo; esta skill no registra puertas.
4. [PMBOK→Organizing/SU] Técnica de análisis según la pregunta: cuadrícula poder/interés para pocos interesados, modelos multidimensionales para muchos; declarar el modelo.
5. [Plantillas] Mínima (roles combinados permitidos, descripciones breves, RACI por entregable, cuadrícula fusionada con el registro) para proyectos pequeños; completa cuando riesgo, costo o interesados lo justifiquen.
6. Transparencia de IA: borrador, sin datos inventados, fuente por valoración; nunca inventar nombres.
7. Idioma del usuario; artefactos y roles con nombre EN la primera vez.
8. Escrituras externas (invitar personas, publicar organigrama) solo con confirmación, vía `pm-integraciones`.
9. [PRINCE2] Todas las responsabilidades asignadas: los roles pueden combinarse, las responsabilidades no quedan huérfanas.
10. [PRINCE2] Un solo ejecutivo, nunca el gestor; separación gestor ↔ ejecutivo ↔ aseguramiento; aseguramiento nunca en gestor, equipos ni soporte.
11. [PRINCE2] Evitar usuario sénior = proveedor sénior; junta mínima con tres intereses; quien operará el producto representado desde el inicio.
12. [PRINCE2] Cada decisión tiene autorizado y tolerancia escritos; autoridades delegadas revisadas en cada fin de etapa; delegar cambios exige presupuesto de cambio.
13. [PMBOK→Organizing] Actitud e interés se evalúan por separado, con fuente; información sensible con `confidencial=si`.
14. [PRINCE2] En ágil, el product owner es el usuario sénior o su delegado con autoridad escrita: intercambia ítems dentro de la tolerancia de alcance (`nivel=product-owner`), nunca fija tolerancias ni aprueba etapas. Con BMAD, el rol PM de BMAD no es el gestor del proyecto.
Más reglas: `references/guia.md` §5.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | Clave |
|---|---|---|---|
| Estructura del equipo de gestión | `templates/estructura-organizativa.md` | `00-direccion/estructura-organizativa.md` | `estructura-organizativa` |
| Descripciones de rol | `templates/descripcion-rol.md` | `00-direccion/roles/` | `descripcion-rol-<rol>` |
| Análisis de interesados | `templates/analisis-stakeholders.md` | `01-inicio/analisis-stakeholders.md` (restringido) | `analisis-stakeholders` |
| Registro de interesados | `registro.py agregar stakeholders` | `03-control/registros/stakeholders.csv` | registro |
| Matriz RACI / RAM | `templates/matriz-raci.md` | `02-planificacion/matriz-raci.md` | `matriz-raci` |
| Acta del equipo (team charter) | `templates/team-charter.md` | `01-inicio/team-charter.md` | `team-charter` |
| Plan de compromiso | `templates/plan-compromiso-stakeholders.md` | `02-planificacion/` | `plan-compromiso-stakeholders` |

## Calidad
- [ ] Ejecutivo y gestor distintos; tres intereses; aseguramiento separado; modelo de entrega por bloque.
- [ ] Sin responsabilidades huérfanas; descripciones con autoridad y límite.
- [ ] Roles ágiles/BMAD mapeados y registrados como adaptación; `roles.product_owner` y cadencia cargados.
- [ ] Interesados amplios, actitud separada, fuente por valoración, `confidencial` completado; revisión humana hecha.
- [ ] RACI validada con leyenda; team charter como propuesta; brechas de compromiso con acción, responsable y fecha.
- [ ] Mermaid válido; artefactos en `borrador`; cierre con la puerta y el rol que decide.

## Escalamiento y excepciones
- Sin ejecutivo prospectivo → `pm-director` para que la capa de negocio lo nombre.
- Pedido de combinar ejecutivo y gestor o dar aseguramiento al gestor → explicar, proponer alternativa; si insiste, excepción al método en `decisiones.csv` y riesgo.
- Interesado de alto poder resistente sin acción, brecha de capacidad, conflicto de representación con proveedores: `references/guia.md` §8.
- Pedido de compartir actitudes fuera del equipo de gestión → advertir sensibilidad y pedir confirmación.
- Como subagente: nombramientos y revisión de actitudes se devuelven como decisiones humanas en el bloque de retorno, no se preguntan desde el subagente.

## Ejemplos de invocación
- "Diseñá la junta: la gerenta de operaciones patrocina, el proveedor es externo y hay dos áreas usuarias."
- "Hacé el análisis de interesados con poder, interés y actitud y cargalos al registro; incluí al regulador."
- EN: "Build the RACI for the twelve work packages and flag any row without a single accountable."
- EN: "We use BMAD and Scrum: map the BMAD PM, architect and product owner onto PRINCE2 roles."
- No activa: "Prepará el mensaje para el comité y la matriz de comunicaciones" → `pm-comunicacion-stakeholders`.

## EN summary
PRINCE2 organising practice plus PMBOK stakeholder techniques: confirm the executive (blocking), choose the delivery model, design the management team structure, map agile and BMAD roles as tailoring, write role descriptions with authority limits, get the executive to confirm appointments (human gate), analyse and register stakeholders after a sensitive-data review (human gate), validate the RACI, propose a team charter and draft the engagement plan. Hard rules: one executive, never the manager; assurance separate; no orphan responsibilities.
