# Guía de organización y roles · Organisation and roles guide

## 1. Técnica de diseño organizacional (detalle)
1. **Ecosistema**: organizaciones participantes, quién retiene la gestión de personas, qué decisiones siguen gobernanza corporativa, políticas aplicables, cómo entran y salen las personas. Anotar acuerdos de interfaz en la estructura.
2. **Modelo de entrega** por bloque de trabajo: interno / externo / mixto; si externo, por producto o por mano de obra; grado de aseguramiento interno; riesgo asignado a quien mejor lo gestiona. Tabla en la estructura (y en el enfoque comercial de `pm-adquisiciones` si hay proveedores).
3. **Estructura**: organigrama Mermaid con líneas de autoridad (sólidas) y de aseguramiento/soporte (punteadas). Reglas duras: un solo ejecutivo; ejecutivo ≠ gestor; aseguramiento nunca en gestor, gestores de equipo, miembros ni soporte; soporte separado de aseguramiento; evitar usuario sénior = proveedor sénior. Estructuras distintas por etapa si cambian.
4. **Descripciones de rol**: una clave por archivo (`descripcion-rol-ejecutivo`…); en versión mínima no hay archivos propios y se registra solo `estructura-organizativa`.
5. **Revisión**: en cada fin de etapa y al cambiar personas.

## 2. Mapeo de roles ágiles y BMAD a la estructura del método
| Rol ágil | Rol del método | Qué decide | Dónde queda | Límite |
|---|---|---|---|---|
| Patrocinador / dueño del negocio | Ejecutivo | inversión, tolerancias de proyecto (con la capa de negocio) | `roles.ejecutivo` | rinde cuentas del business case |
| Product owner | Usuario sénior o su delegado | orden del backlog, aceptación de historias, swaps dentro de la tolerancia de alcance | `roles.product_owner` + descripción de rol | desplazar un Must o exceder la tolerancia → solicitud de cambio |
| Representante técnico del proveedor / arquitecto líder | Proveedor sénior | viabilidad técnica, recursos | `roles.proveedor_senior` | — |
| Scrum master / agile coach | Facilitación dentro del equipo; puede apoyar a soporte | nada de gobierno | descripción de rol | nunca aseguramiento |
| Equipo de desarrollo | Gestor de equipo colectivo con punto de contacto | cómo hacer el trabajo, cuánto entra en la iteración | `roles.jefes_equipo` | tolerancia del paquete de trabajo |
| Gestor del proyecto | Gestor del proyecto | coordina etapas, informa a la junta | `roles.gestor_proyecto` | no es el PO |

Roles de BMAD (orientativo; ver `pm-bmad-puente/references/guia.md` §3). Los "agentes" de BMAD son asistentes; el rol PRINCE2 lo ocupa la persona que los opera y aprueba su salida:
| Rol BMAD | Quién lo ejerce en PRINCE2 | Nota |
|---|---|---|
| Analyst (brief de producto, investigación) | trabajo especializado bajo el gestor, insumo del usuario sénior | el brief de producto es insumo del project brief |
| PM (PRD) | product owner / usuario sénior delegado | el PRD `final` lo aprueba quien la junta designe; no es el gestor del proyecto |
| Architect | proveedor sénior o jefe de equipo técnico | decisiones AD con impacto en tolerancias se escalan |
| UX Designer | equipo especialista | — |
| Scrum master BMAD (sprint planning, correct-course) | facilitación del equipo | su "sí" en correct-course no reemplaza a la autoridad de cambio |
| Dev / code review | equipo de entrega (MP) dentro del paquete de trabajo | — |

## 3. Perfil ágil mínimo (SPEC §1.10.12)
Estructura de una página: junta con tres intereses (puede ser de dos personas si el ejecutivo asume el interés usuario y el PO es su delegado), PO con autoridad escrita de una línea, equipo con punto de contacto, aseguramiento en alguien de la junta o un tercero. Sin descripciones de rol separadas; RACI por release o épica (5–8 filas); cuadrícula fusionada con el registro. El team charter se reemplaza por el acuerdo de trabajo (DoD/DoR y eventos) que mantiene `pm-agil-hibrido`.

## 4. Traspaso a pm-interesados
Desde v2.2 el análisis de interesados (matriz poder/interés con estrategia por cuadrante), la RACI (`raci.csv`, un A por
elemento), los estereotipos, las preferencias de comunicación y el plan de compromiso son de **`pm-interesados`**
(plantillas `analisis-stakeholders`, `matriz-raci`, `plan-compromiso-stakeholders` y `entrevista-interesado` en esa skill).
Esta skill le entrega la junta y los roles confirmados para que cada rol figure en el maestro y en la RACI. El usuario
sénior asesora sobre los influenciadores de su comunidad; el proveedor sénior, sobre el lado proveedor.

## 5. Reglas extendidas
1. [PRINCE2] Si hay trabajo compartido de puesto, la descripción de rol explica cómo se mantiene el punto único de rendición de cuentas.
2. [PRINCE2] No mezclar personal interno y externo en un mismo paquete de trabajo; con más de tres o cuatro proveedores, representación agregada en la junta; si el gestor es del proveedor, reforzar el aseguramiento del cliente.
3. [PRINCE2] Sostenibilidad, seguridad y bienestar en las descripciones de rol, incluida la gestión post-cierre.
4. [PRINCE2] Prever en el inicio los cambios de estructura por etapa (de equipo de diseño a equipo de entrega) y sus recursos.
5. [PMBOK→Organizing] El análisis de interesados no se exporta a versiones públicas sin filtrar las filas `confidencial=si`.
6. [Plantillas] RACI con alertas de concentración y sobre-consulta.
7. [Plantillas] El team charter lo escribe el equipo (incluidos contratistas clave); el agente solo propone y nunca lo da por aprobado.
8. Visuales: organigrama y cuadrícula en Mermaid; si `integraciones.diagramas` declara otra herramienta, ofrecer a `pm-visuales` la versión mejorada sin cambiar el contenido.

## 6. Ejemplo trabajado
"App de órdenes de campo", ágil: ejecutivo = gerenta de operaciones; usuario sénior = jefe de técnicos, que delega como PO a una supervisora con autoridad para reordenar el backlog y aceptar historias; proveedor sénior = líder de la fábrica de software externa; aseguramiento usuario = analista de calidad; aseguramiento negocio = controller; soporte = PMO. `estado.py rol ejecutivo="G. Ríos" usuario_senior="J. Paz" product_owner="M. Sosa" proveedor_senior="L. Vera" aseguramiento="A. Gil;C. Mora" soporte="PMO"`. El sindicato de técnicos entra como `ST-004` (poder `medio`, interés `alto`, actitud `resistente`, `confidencial=si`); brecha resistente → neutral con acción "demo temprana con delegados" (PO, antes de la primera release).
Con BMAD: la supervisora (PO) opera el flujo de PRD de BMAD y lo presenta; el líder del proveedor ejerce de Architect; el PRD `final` lo aprueba el usuario sénior por delegación de la junta, anotado en su descripción de rol.

## 7. Columnas de `stakeholders.csv` (id `ST-###`)
`id`; `nombre` (name); `rol_organizacion` (role in the organisation); `rol_proyecto` (role in the project); `poder` (power); `interes` (interest); `actitud` (attitude); `nivel_compromiso_actual` (current engagement); `nivel_compromiso_deseado` (desired engagement); `expectativas` (expectations); `canal` (channel); `frecuencia` (frequency); `responsable_relacion` (relationship owner); `confidencial` (confidential: si/no; `si` restringe la circulación y excluye la fila de exportaciones públicas); `notas` (notes); v2.2: `estereotipo` (stereotype ET-###), `correo` (e-mail), `usuario_chat` (Slack/Teams user). Dueña del registro: `pm-interesados` (guía §11).

## 8. Casos borde
- Interesado de alto poder y actitud resistente sin acción → riesgo y acción propuesta al ejecutivo.
- Brecha de capacidad (rol sin persona con habilidades) → riesgo en `riesgos.csv`; opciones contratar, prestar, formar; decide el ejecutivo.
- Conflicto de representación con varios proveedores o entre juntas de cliente y proveedor → `pm-director` y `pm-adquisiciones`.
- El usuario propone combinar ejecutivo y gestor → alternativa (aseguramiento por un miembro de la junta o un tercero); si insiste, excepción registrada y riesgo.
