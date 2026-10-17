# Guía ágil e híbrida · Agile and hybrid guide

## 1. Perfil ágil mínimo: qué sustituye a qué
| Artefacto predictivo | Equivalente en perfil ágil mínimo | Dónde |
|---|---|---|
| PBS / WBS completa | Árbol épica → historia del backlog | `backlog.csv` (`tipo`, `producto_pbs`) |
| Diccionario de la WBS | Historias con criterios de aceptación + DoD | `historias/`, `release-plan.md` |
| Flujo de productos | Dependencias entre historias y orden del release | `release-plan.md` §5 |
| Cronograma con CPM | Iteraciones de duración fija + hitos de release | `release-plan.md`, `cronograma.md` (híbrido) |
| Presupuesto por paquete | Presupuesto por iteración × iteraciones de la etapa | `presupuesto.md` |
| Plan de equipo | Tablero Kanban / backlog de iteración | tracker o `backlog.csv` |
| Highlight completo | Highlight corto con burn-up | `03-control/reportes/` (`pm-progreso-reportes`) |

Perfil mínimo (SPEC §1.10.12): brief ligero + visión, business case de una página, estructura con PO, enfoques en una página, backlog priorizado, release plan por etapas, DoD/DoR, presupuesto por iteración, highlight corto con burn-up. Perfil completo: historias detalladas, carriles por equipo, EVM adaptativo, RTM (sin BMAD). Las puertas de etapa existen siempre. En híbrido, `pbs-wbs.md`/`wbs.csv` solo para los paquetes predictivos; `producto_pbs` enlaza con ellos.

## 2. `backlog.csv`: columnas
Equivalencias: historia de usuario (user story), caja de tiempo (timebox), velocidad (velocity), definición de hecho/listo (DoD/DoR), dueño del producto (product owner, PO).

Cabecera: `id,tipo,titulo,descripcion,prioridad,moscow,estimacion,estado,iteracion,release,producto_pbs,criterios_aceptacion,origen,refs`.
| Columna | Valores / regla | Dueño con BMAD |
|---|---|---|
| `id` | `PB-###` sin BMAD; clave de historia BMAD (`1-2-slug`) o épica (`epic-1`) con BMAD | puente |
| `tipo` | `epica`, `historia`, `requisito`, `defecto`, `mejora_tecnica`, `accion_retro` | derivada |
| `titulo`, `descripcion` | "como / quiero / para" | derivada |
| `prioridad` | entero único (orden total) | **gobierno** |
| `moscow` | `must`, `should`, `could`, `wont` | **gobierno** |
| `estimacion` | puntos (planning poker, sin horas) | **gobierno** |
| `estado` | sin BMAD: `nuevo`, `refinado`, `listo`, `en_progreso`, `completado`, `descartado`; con BMAD: `backlog`, `ready-for-dev`, `in-progress`, `review`, `done`, `retirada-en-bmad` | derivada |
| `iteracion` | `S<k>` | **gobierno** |
| `release` | `R<k>` | **gobierno** |
| `producto_pbs` | código de la PBS/WBS o épica padre | **gobierno** |
| `criterios_aceptacion` | texto o referencia a la historia | derivada |
| `origen` | vacío / `bmad` / `tracker` | derivada |
| `refs` | ids del PRD (FR-3; NFR-1) | derivada |
Columnas opcionales al final (esquema Parte V): `rol_usuario`, `categoria`, `id_requisito`, fechas, `comentarios`. Si el archivo existe sin `origen` y `refs`, agregarlas antes de la primera sincronización BMAD (el puente conserva las columnas del archivo).

## 3. BMAD como fuente del backlog
Si `estado.json.integraciones.especificacion = bmad`:
- Las filas del backlog **las crea y actualiza** `python3 <pm-bmad-puente>/scripts/bmad.py --proyecto <dir> backlog` desde `epics.md` y `sprint-status.yaml`. Columnas derivadas (tipo, titulo, descripcion, estado, origen, refs, criterios_aceptacion) se sobrescriben en cada sincronización; columnas de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) son de esta skill y del PO, y el puente nunca las toca. No se escriben historias a mano para ítems de BMAD ni se copian requisitos.
- Historias nuevas en BMAD entran sin MoSCoW ni release: el PO las clasifica (decisión `nivel=product-owner` si caben en la tolerancia; si desplazan un Must, solicitud de cambio).
- Historias `retirada-en-bmad`: el PO decide quitarlas o reponerlas vía cambio.
- **Avance**: `bmad.py avance` agrega una fila a `03-control/reportes/avance-bmad.csv` (conteo por estado, épicas terminadas, % por puntos si hay `estimacion`). Velocidad, burn-up y EV salen de ahí (`done` = terminado; la DoD de BMAD incluye code review).
- **Sprint = paquete de trabajo**: cada sprint de BMAD se autoriza como paquete (MP) con `pm-paquetes-trabajo`: alcance = historias del sprint, tolerancias, DoD.
- **Gate de preparación del sprint planning de BMAD** (PASS/CONCERNS/FAIL): su resultado es insumo de `autorizar-etapa`; CONCERNS/FAIL se presentan como riesgo o condición al plan de etapa (`pm-plan-etapa-y-limites`).
- Desvíos del PRD o Sprint Change Proposals → `bmad.py verificar` → `pm-issues-cambios`.
- **Traspaso de prioridades** (SPEC §1.16): tras cambiar MoSCoW, release o iteración en `backlog.csv`, `python3 <pm-bmad-puente>/scripts/bmad.py --proyecto <dir> handoff` (sin `--cambio`) emite `handoff-bmad-<fecha>-prioridades.md` solo con las filas que cambiaron desde el último traspaso; es insumo del sprint planning de BMAD. Nunca se editan `epics.md` ni `sprint-status.yaml`.

## 4. Mapa de ceremonias a controles
| Ceremonia | Control PRINCE2 | Registro |
|---|---|---|
| Planificación de iteración | Autorización del paquete de trabajo de la iteración (MP) | `WP-###` vía `pm-paquetes-trabajo` |
| Daily / tablero | Checkpoint | tablero o `avance-bmad.csv` |
| Review / demo | Aceptación de productos e insumo del highlight | `calidad.csv` |
| Retrospectiva de iteración | Mejora del equipo, lecciones candidatas | `retrospectiva.md`, `acciones.csv` |
| Última iteración de la etapa | Límite de etapa (SB, `limite-etapa`) | `pm-plan-etapa-y-limites` |

## 5. Retrospectiva de iteración vs. taller de lecciones de etapa
| | Retrospectiva de iteración (esta skill) | Taller de lecciones de etapa (`pm-lecciones-aprendidas`) |
|---|---|---|
| Cuándo | Al final de cada iteración | En cada límite de etapa y al cierre |
| Quién | Equipo, PO, facilitador | Gestor, equipo, aseguramiento; a veces junta |
| Foco | Forma de trabajar del equipo | Método, gobierno, estimaciones, proveedores |
| Salida | 1–3 acciones al backlog o a `acciones.csv` | Lecciones en `lecciones.csv`, informe |
| Plantilla | `templates/retrospectiva.md` | `retrospectiva-etapa.md` de esa skill |

## 6. Fórmulas y EVM ágil
- Velocidad = puntos terminados según DoD (promedio de las últimas 3). `iteraciones restantes ≈ puntos restantes / velocidad`.
- Capacidad del release: `Σ puntos Must+Should ≤ velocidad × iteraciones`; si no, repriorizar, no estirar la iteración. Regla práctica: Must ≤ ~60 % de la capacidad (configurable).
- EVM ágil (SPEC §1.10.7): PV = proporción de puntos planificados a la fecha × BAC; EV = proporción de puntos terminados × BAC; AC = costo real del equipo. `python3 <pm-estado-proyecto>/scripts/evm.py --pv .. --ev .. --ac .. --bac .. --modo agil --pct-no-must <% del alcance que es Should/Could> --proyecto <dir>`. EAC > BAC = alcance pronosticado que no entra; excepción solo si supera la porción Should/Could (los Must peligran).

## 7. Comandos de registro (los de `estado.json` los ejecuta `pm-director` tras confirmación)
- `estado.py --proyecto <dir> agil cadencia_iteracion_dias=14 velocidad_referencia=30`; `estado.py rol product_owner="<nombre>"`.
- `estado.py tolerancia --nivel etapa alcance="Must PB-001..PB-014; Should/Could flexibles"`.
- Swap del PO: `registro.py --proyecto <dir> agregar decisiones --campo decision="Swap PB-021 por PB-034 (5 pts)" --campo nivel=product-owner --campo decidido_por="PO: <nombre>"`.
- Acciones de retro fuera del equipo: `registro.py agregar acciones ...`.

## 8. Reglas complementarias
1. [PRINCE2] Un tablero Kanban o el backlog de iteración puede sustituir al plan de equipo; la descripción del paquete de la iteración sigue existiendo.
2. [PMBOK→Plans] Un solo backlog por producto con orden total; ítems próximos cumplen la DoR; no comparar velocidades entre equipos.
3. [PMBOK→Plans] En híbrido, releases = hitos del cronograma maestro e iteraciones = bloques fijos; dependencias con paquetes predictivos documentadas.
4. [Plantillas] Backlog, requisitos/PRD y RTM coinciden en prioridad; el contenido de una iteración iniciada no cambia.
5. [Plantillas] El release plan guarda la línea base; los burn charts reales viven en `03-control/reportes/`.
6. Tracker: el CSV local es la fuente del método; si el tracker tiene ítems que el CSV no, informar la diferencia y proponer reconciliación (vía `pm-integraciones`) antes de reportar.

## 9. Casos borde
- Pedido de alargar una iteración, bajar la DoD o pasar un Must a Should para "cumplir" → explicar el riesgo y pedir decisión registrada de la junta.
- Sin velocidad histórica → rango declarado; las primeras 2–3 iteraciones calibran.
- Con BMAD y tracker a la vez → BMAD manda en las columnas derivadas; el tracker solo en la clave guardada en notas (ver `pm-integraciones`).
