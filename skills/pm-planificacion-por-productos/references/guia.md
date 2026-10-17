# Guía de planificación por productos · Product-based planning guide

## 1. Versión mínima vs. completa
| Artefacto | Versión mínima (proyecto pequeño) | Versión completa (riesgo, costo, proveedores, regulación) |
|---|---|---|
| Descripción del producto del proyecto | Propósito, productos mayores, 3–7 criterios priorizados | Todos los campos, tolerancias de calidad, métodos de aceptación por criterio |
| PBS / WBS | Dos niveles, en una sola tabla; `wbs.csv` de dos niveles sin WBS separada | Árbol completo, estados de producto, WBS con paquetes y cuentas de control, `wbs.csv` completo |
| Descripciones de producto | Solo productos mayores; una página cada una | Todos los productos finales e intermedios; especificaciones funcionales y no funcionales |
| Flujo de productos | Lista ordenada o diagrama de 5–10 nodos | Diagrama completo coloreado por etapa, tabla de dependencias |
| Enunciado del alcance | Integrado en el acta de constitución | Documento propio con exclusiones, restricciones y tolerancia de alcance |
| Requisitos y RTM | Puede omitirse; el backlog o las descripciones cumplen la función | Tabla de requisitos, RTM con cobertura y matriz inter-requisitos (sin BMAD) |
| Diccionario de la WBS | Tabla de una línea por paquete: código, producto, responsable | Una entrada por paquete, con responsable, costos y referencias contractuales |

## 2. Correspondencia de nombres entre marcos (mapeo del paquete)
| PRINCE2 | PMBOK / plantillas | Uso en esta skill |
|---|---|---|
| Project product description | Scope statement + criterios de aceptación del acta | `descripcion-producto-proyecto.md` alimenta `enunciado-alcance.md` |
| Product breakdown structure | WBS orientada a entregables | `pbs-wbs.md` secciones 1–2 |
| Work package (descripción) | Paquete de la WBS + entrada del diccionario | `wbs.csv`, `pbs-wbs.md` sección 3 y `diccionario-wbs.md` |
| Product description | Documentación de requisitos + métricas de calidad | `productos/<id>.md`; sus criterios se reflejan en `requisitos.md` (o citan ids del PRD con BMAD) |
| Product flow diagram | Red del cronograma a nivel de entregables | `flujo-productos.md`; base de la secuenciación |
| Product register | Estado de entregables / estado de traza de la RTM | tabla final de `pbs-wbs.md` |
| Épica / historia (PRINCE2 Agile) | User story, ítem del backlog | `pm-agil-hibrido`, con `producto_pbs` |

## 3. Preguntas de elicitación recomendadas
- ¿Qué debe existir al final para que el usuario sénior acepte? ¿Cómo lo comprobará?
- ¿Qué productos dependen de terceros o de otros proyectos? ¿Quién responde por ellos?
- ¿Qué estados intermedios tienen calidad propia (diseño aprobado, prototipo validado)?
- ¿Qué queda explícitamente fuera? ¿Qué zonas grises ya generaron dudas?
- ¿Qué requisitos regulatorios, de transición u operación hay que incluir como productos?

## 4. EDT/WBS con `wbs.py`
Script: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/wbs.py 02-planificacion/wbs.csv --titulo "<Proyecto>" --mermaid 02-planificacion/visuales/wbs.md --diccionario 02-planificacion/diccionario-wbs-esqueleto.md` (opciones `--json` para consumo por otra herramienta y `--profundidad N` para recortar el diagrama).

Columnas de `wbs.csv` (plantilla `templates/wbs.csv`). EN: `codigo`=code, `nombre`=name, `tipo`=type (producto|paquete|hito = product|work package|milestone), `responsable`=owner, `esfuerzo_h`=effort hours, `costo`=cost, `ref`=requirement/story ids (siempre ids leídos de la fachada `especificacion.py`, nunca texto copiado).
| Columna | Contenido | Regla |
|---|---|---|
| `codigo` | 1, 1.2, 1.2.3 | el padre de 1.2.3 es 1.2; el nivel 0 (proyecto) es implícito; sin huecos de padre |
| `nombre` | sustantivo (producto o paquete) | nunca un verbo en los niveles de producto |
| `tipo` | `producto`, `paquete` o `hito` | paquetes e hitos son hojas; una hoja de tipo `producto` genera aviso (descomponer o marcar como paquete) |
| `responsable` | persona o rol (jefe de equipo, proveedor) | obligatorio en cada paquete; sin él, aviso |
| `esfuerzo_h`, `costo` | solo en hojas | los niveles superiores se consolidan (regla del 100 %); valores en un padre se ignoran con aviso |
| `ref` | ids separados por `;` (FR-3; NFR-2; 1-2-login) o código de requisito propio (REQ-012) | trazabilidad: con BMAD la usa `bmad.py trazabilidad --wbs` |

Ejemplo:
```
codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref
1,Plataforma de reservas,producto,,,,
1.1,Módulo de pagos,producto,,,,
1.1.1,Integración pasarela,paquete,Jefe equipo backend,120,9600,FR-4;NFR-2
1.1.2,Pruebas de pagos,paquete,QA lead,40,2800,FR-4
1.2,Puesta en producción,hito,Gestor,0,0,
```
Lectura de la salida: total de elementos y hojas, esfuerzo y costo consolidados por nivel, y líneas `AVISO`. Los errores (código inválido o duplicado, padre faltante, valor no numérico) detienen el script: corregir el CSV y volver a correr. El diagrama Mermaid (hojas con responsable y cifras) se pega en `pbs-wbs.md` sección 4 o se deja en `visuales/`; el esqueleto de diccionario se completa con la plantilla `diccionario-wbs.md`.

Antes de la estimación, `esfuerzo_h` y `costo` pueden quedar vacíos (0); se completan con los resultados de `pm-cronograma-estimacion` y `pm-costos-presupuesto` y se vuelve a correr para verificar que la consolidación coincide con la hoja de estimación y el presupuesto (la diferencia se explica o se corrige). La columna `wbs` de `actividades.csv` (cronograma) usa los mismos códigos.

## 5. Detalle de pasos
- **Descripción del producto del proyecto**: propósito, productos mayores, derivación, expectativas de calidad del usuario, criterios de aceptación priorizados (MoSCoW), métodos y responsables de aceptación, tolerancias de calidad. Si viene del brief, refinarla, no reescribirla.
- **PBS**: incluir productos intermedios, externos (marcados) y estados de un mismo producto cuando cada estado tenga calidad propia. Códigos `P-1.2` en la PBS y `1.2` en `wbs.csv`; la tabla PBS ↔ WBS de `pbs-wbs.md` guarda la correspondencia.
- **Descripciones de producto** (`productos/<id>-<nombre>.md`): identificador, propósito, composición, formato, derivado de, especificaciones de calidad funcionales y no funcionales medibles, tolerancia de calidad, método de verificación (inspección, prueba, demostración, análisis), habilidades, productor, revisor independiente y autoridad de aceptación.
- **Flujo de productos**: nodos Inicio y Fin, todos los productos, flechas de dependencia, anotación por etapa; identificar paralelismo. Toda dependencia externa se propone como riesgo (`registro.py agregar riesgos`) con confirmación.
- **Enunciado del alcance**: entregables = productos de nivel superior de la PBS, criterios por entregable, exclusiones explícitas, restricciones y referencia a supuestos (`S-###`).
- **Requisitos y RTM (sin BMAD)**: una fila atómica y verificable por requisito (categoría, interesado origen, prioridad, criterio de aceptación, método de verificación, release/etapa); la RTM enlaza requisito → objetivo del business case → entregable de la EDT → métrica → técnica de validación. `cobertura = requisitos trazados / total`; listar huérfanos hacia adelante y hacia atrás.
- **Diccionario de la WBS**: responsable del paquete (único, acepta el paquete en MP), tipo de ejecución (interno · proveedor, enlazado a `pm-adquisiciones`), descripción del trabajo, productos, hitos, actividades, recursos, criterios de aceptación, referencias técnicas y contractuales. Horas y costos se completan desde estimación y costeo; hasta entonces `[por confirmar]`.

Equivalencia de columnas si se exporta `requisitos.csv` (esquema Parte V): `id, requisito, interesado, categoria, prioridad, criterios_aceptacion, metodo_verificacion, fase_release, id_padre, estado` = ID, requirement, stakeholder, category, priority, acceptance criteria, verification method, phase/release, parent, status.

## 6. Variantes ágil, híbrida y BMAD
- **Ágil puro** (perfil mínimo, SPEC §1.10.12): solo descripción del producto del proyecto (o visión con MVP) y, si se pide, el árbol épica → historia como PBS; el backlog de `pm-agil-hibrido` sustituye a WBS, diccionario y flujo como entrada de estimación y costeo.
- **Híbrido**: WBS, diccionario y flujo solo para los paquetes predictivos; los productos mayores se conservan como épicas con descripción breve; las historias son descripciones de grano fino con criterios y `producto_pbs` apuntando al código de la PBS.
- **BMAD** (`estado.json.integraciones.especificacion = bmad`): los requisitos FR/NFR, journeys y métricas viven en el PRD. Esta skill **no escribe** `requisitos.md` ni la RTM: las descripciones de producto, la PBS y la columna `ref` de `wbs.csv` citan ids; la matriz de trazabilidad la deriva `pm-bmad-puente` (`bmad.py requisitos` y `bmad.py trazabilidad --wbs 02-planificacion/wbs.csv`). Un requisito nuevo o retirado respecto de la línea base del PRD es solicitud de cambio (`pm-issues-cambios`). Si BMAD no está instalado pero hay documentos sueltos, se trabaja sin BMAD.

## 7. Reglas complementarias
1. [PRINCE2] La PBS y el PFD incluyen productos intermedios y externos; los externos generan una dependencia documentada en el paquete y, cuando corresponde, un riesgo.
2. [PRINCE2] Las especificaciones de calidad se escriben medibles (cuantitativas) o acotadas con contexto (cualitativas), separando funcionales de no funcionales, con tolerancia explícita.
3. [PMBOK→Plans] Elegir técnica según la pregunta (`pmbok8-artefactos-tecnicas-anexos.md` §5): entrevistas, talleres o prototipos para elicitar; descomposición para estructurar; MoSCoW/Kano para priorizar.
4. [PMBOK→Quality] Cobertura hacia adelante y hacia atrás en la RTM: todo requisito traza a un entregable y una verificación; todo entregable a un requisito.
5. [Plantillas] Un requisito por fila, verificable y con origen; sin método de verificación no entra en la línea base.
6. [Plantillas] El diccionario no duplica documentos técnicos: los referencia; los paquetes de proveedor remiten a su contrato.
7. Diagramas en Mermaid por defecto; si `integraciones.diagramas` declara otra herramienta, ofrecer la versión mejorada vía `pm-visuales` sin reemplazar la fuente Markdown/CSV.
8. La sincronización del backlog con un tracker se delega a `pm-agil-hibrido` / `pm-integraciones`, con confirmación.

## 8. Casos borde
- Criterios en conflicto entre usuario sénior y proveedor sénior → `pm-director` (decisión de la junta en `decisiones.csv`).
- Paquete sin responsable o producto externo sin dueño → riesgo con `pm-riesgos` y pedido a `pm-director` (proveedor sénior) de nombrar responsable.
- Paquete candidato a compra → `pm-adquisiciones` (make-or-buy) antes de costear.
- Ambigüedad entre plan de proyecto y de etapa → una sola pregunta de desambiguación.
- Business case inexistente → el método exige justificación antes de planificar en detalle; ofrecer `pm-caso-de-negocio`.
- `wbs.py` consolida un total distinto del presupuesto → revisar hojas sin costo, costos cargados en padres (se ignoran) o reservas que no van en la WBS (la contingencia y la reserva de gestión viven en el presupuesto).
