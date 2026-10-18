---
name: pm-organizacion-roles
description: "Estructura de gestión, roles y team charter. Usar: junta, roles, descripción de rol, team charter, mapear roles ágiles o BMAD. No: interesados o RACI→pm-interesados; plan de comunicación→pm-comunicacion-stakeholders."
version: 2.2.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-inicio
    procesos_prince2: [SU, IP, SB]
    practicas_prince2: [organizing]
    tecnicas_pmbok: [diseño organizacional, acta del equipo]
    artefactos: [estructura-organizativa, descripcion-rol-<rol>, team-charter]
    idiomas: [es, en]
---

# Organización y roles · Organisation and roles

## Cuándo usar / When to use
- Diseñar la **estructura del equipo de gestión** (junta, gestor, equipos, aseguramiento, soporte, autoridad de cambio) y las **descripciones de rol**.
- Redactar el **team charter**. Interesados (matriz poder/interés, RACI, estereotipos, preferencias, plan de compromiso): **`pm-interesados`**.
- Revisar en cada fin de etapa (SB); mapear roles ágiles o BMAD a los del método.
- EN: design the board and team, role descriptions and team charter; map agile/BMAD roles (stakeholders and RACI: pm-interesados).

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. etiquetas bilingües; roles con nombre EN la primera vez. Interesados y sus columnas: `pm-interesados`.

## Conocimiento
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §3 (intereses, roles, diseño organizacional, RACI).
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §6 (responsabilidades base por rol) y §5.1 act. 1 y 4.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §10, §11, §16, §24; `plantillas-inicio-y-planes.md` §3.11.
- `pm-knowledge/references/pmbok8-dominios-procesos-adaptacion.md` §2.5 (interesados); `pmbok8-artefactos-tecnicas-anexos.md` §3.13 (roles ágiles).
- `references/guia.md`: diseño (§1), mapeo ágil y BMAD (§2), ágil mínimo (§3), traspaso a pm-interesados (§4), reglas extendidas (§5), ejemplo (§6), columnas CSV (§7), casos borde (§8).

## Entradas requeridas
- `estado.json` (fase SU o IP; `enfoque_entrega`; `roles` si existen).
- `00-direccion/mandato.md` (ejecutivo prospectivo) y `01-inicio/project-brief.md` o `canvas-arranque.md` (interesados, modelo de entrega).
- `03-control/registros/stakeholders.csv` (creado por `pm-estado-proyecto`; `registro.py esquema stakeholders` muestra columnas y valores).
- Organización permanente (estructura, proveedores, PMO); si falta, `[por confirmar]`.
- Si hay un directorio conectado, leer nombres vía `pm-integraciones` (nunca inventar personas).

## Procedimiento
1. **Leer estado y mandato**: sin ejecutivo prospectivo, detener (bloqueante del método).
2. **Ecosistema organizacional y modelo de entrega** por bloque de trabajo (interno/externo/mixto; producto o mano de obra; aseguramiento; riesgo a quien mejor lo gestiona); ver `references/guia.md` §1. Con proveedores, enlazar con `pm-adquisiciones`.
3. **Diseñar la estructura** → `templates/estructura-organizativa.md` en `00-direccion/estructura-organizativa.md`: organigrama Mermaid, junta con tres intereses, gestor, equipos (o equipo ágil con punto de contacto), aseguramiento por interés, soporte, autoridad de cambio. Verificar reglas 9–11; prever estructuras por etapa.
4. **Mapear roles ágiles y BMAD** (si `enfoque_entrega` es `agil`/`hibrido` o `integraciones.especificacion = bmad`) con la tabla de `references/guia.md` §2; registrar como adaptación para el PID. El nombramiento del PO lo confirma el ejecutivo y lo registra `pm-director` (`estado.py rol product_owner="<nombre>"`); la cadencia la acuerda el equipo y también la registra `pm-director` (`estado.py agil cadencia_iteracion_dias=<n>`), como dice `pm-agil-hibrido`.
5. **Descripciones de rol** → `templates/descripcion-rol.md`, una por rol en `00-direccion/roles/descripcion-rol-<rol>.md`: persona, autoridad y límite (coherente con tolerancias), responsabilidades (incl. sostenibilidad y bienestar), rendición de cuentas, dedicación, combinaciones. En versión mínima, unas líneas por rol dentro de la estructura.
6. 🔒 **Puerta humana 1**: el ejecutivo confirma diseño y nombramientos; fila en `decisiones.csv` (`nivel=junta`) y `estado.py rol ejecutivo=... gestor_proyecto=... usuario_senior="A;B" proveedor_senior=... aseguramiento=... soporte=... autoridad_cambio=... jefes_equipo="X;Y"`. Si acompaña una puerta, queda `en-revision` para `pm-director`.
7. **Interesados y RACI** → `pm-interesados`: registro y matriz poder/interés con estrategia por cuadrante, RACI validada (un A por elemento) sobre la estructura diseñada, estereotipos y preferencias. Esta skill le pasa la junta y los roles confirmados.
8. **Team charter** → `templates/team-charter.md` en `01-inicio/team-charter.md`: borrador para el taller del equipo.
9. **Revisión en fin de etapa** (modo `revisar`): capacidad vs. responsabilidades, cambios de personas, autoridades delegadas; lecciones sobre el ecosistema (cambios de interesados: `pm-interesados`).
10. **Registrar** (`estado.py artefacto <clave> --ruta ... --estado borrador`) y cerrar con `[por confirmar]`, rol que decide y siguiente paso; como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas (equipo autoorganizado = gestor de equipo colectivo), nunca eliminando puertas ni roles de la junta.
2. [PRINCE2] Desviación prevista fuera de tolerancia → excepción; una brecha de capacidad que amenaza una tolerancia es un riesgo registrado.
3. [PRINCE2] Nada se aprueba sin acto humano registrado; los nombramientos los confirma el ejecutivo; esta skill no registra puertas.
4. [PMBOK→Organizing/SU] El análisis de interesados (modelo, fuentes, estrategia) lo hace `pm-interesados` sobre la estructura de esta skill.
5. [Plantillas] Mínima (roles combinados permitidos, descripciones breves) para proyectos pequeños; completa cuando riesgo, costo o interesados lo justifiquen.
6. Transparencia de IA: borrador, sin datos inventados, fuente por valoración; nunca inventar nombres.
7. Idioma del usuario; artefactos y roles con nombre EN la primera vez.
8. Escrituras externas (invitar personas, publicar organigrama) solo con confirmación, vía `pm-integraciones`.
9. [PRINCE2] Todas las responsabilidades asignadas: los roles pueden combinarse, las responsabilidades no quedan huérfanas.
10. [PRINCE2] Un solo ejecutivo, nunca el gestor; separación gestor ↔ ejecutivo ↔ aseguramiento; aseguramiento nunca en gestor, equipos ni soporte.
11. [PRINCE2] Evitar usuario sénior = proveedor sénior; junta mínima con tres intereses; quien operará el producto representado desde el inicio.
12. [PRINCE2] Cada decisión tiene autorizado y tolerancia escritos; autoridades delegadas revisadas en cada fin de etapa; delegar cambios exige presupuesto de cambio.
14. [PRINCE2] En ágil, el product owner es el usuario sénior o su delegado con autoridad escrita: intercambia ítems dentro de la tolerancia de alcance (`nivel=product-owner`), nunca fija tolerancias ni aprueba etapas. Con BMAD, el rol PM de BMAD no es el gestor del proyecto.
Más reglas: `references/guia.md` §5.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta | Clave |
|---|---|---|---|
| Estructura del equipo de gestión | `templates/estructura-organizativa.md` | `00-direccion/estructura-organizativa.md` | `estructura-organizativa` |
| Descripciones de rol | `templates/descripcion-rol.md` | `00-direccion/roles/` | `descripcion-rol-<rol>` |
| Acta del equipo (team charter) | `templates/team-charter.md` | `01-inicio/team-charter.md` | `team-charter` |

## Calidad
- [ ] Ejecutivo y gestor distintos; tres intereses; aseguramiento separado; modelo de entrega por bloque.
- [ ] Sin responsabilidades huérfanas; descripciones con autoridad y límite.
- [ ] Roles ágiles/BMAD mapeados y registrados como adaptación; `roles.product_owner` y cadencia cargados.
- [ ] Team charter como propuesta; junta y roles entregados a `pm-interesados` para el mapa y la RACI.
- [ ] Mermaid válido; artefactos en `borrador`; cierre con la puerta y el rol que decide.

## Escalamiento y excepciones
- Sin ejecutivo prospectivo → `pm-director` para que la capa de negocio lo nombre.
- Pedido de combinar ejecutivo y gestor o dar aseguramiento al gestor → explicar, proponer alternativa; si insiste, excepción al método en `decisiones.csv` y riesgo.
- Brecha de capacidad o conflicto de representación con proveedores: `references/guia.md` §8. Interesado de alto poder resistente: `pm-interesados`.
- Como subagente: los nombramientos se devuelven como decisiones humanas en el bloque de retorno, no se preguntan desde el subagente.

## Ejemplos de invocación
- "Diseñá la junta: la gerenta de operaciones patrocina, el proveedor es externo y hay dos áreas usuarias."
- "Escribí las descripciones de rol del gestor y del aseguramiento de negocio con sus límites de autoridad."
- EN: "Draft the team charter for the kickoff workshop." (RACI or stakeholder map → `pm-interesados`)
- EN: "We use BMAD and Scrum: map the BMAD PM, architect and product owner onto PRINCE2 roles."
- No activa: "Prepará el mensaje para el comité y la matriz de comunicaciones" → `pm-comunicacion-stakeholders`.

## EN summary
PRINCE2 organising practice: confirm the executive (blocking), choose the delivery model, design the management team structure, map agile and BMAD roles as tailoring, write role descriptions with authority limits, get the executive to confirm appointments (human gate) and propose a team charter. Stakeholder analysis, the RACI and the engagement plan belong to pm-interesados. Hard rules: one executive, never the manager; assurance separate; no orphan responsibilities.
