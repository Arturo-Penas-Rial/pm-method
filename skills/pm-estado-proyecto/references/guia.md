# Guía de estado del proyecto y scripts · Project state and scripts guide

Detalle de `pm-estado-proyecto`. El SKILL.md cita cada sección por número. Todos los scripts viven en
`${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/` (SPEC §1.10.1) y se ejecutan desde cualquier carpeta con `--proyecto <dir>`
(salvo `cpm.py`, `wbs.py` y `evm.py` sin proyecto, que reciben archivos o cifras).

## 1. Modelo de puertas y transiciones · Gate and transition model
| Momento | Comando | Efecto en `estado.json` |
|---|---|---|
| Fin de SU | `puerta autorizar-inicio --decision aprobado` | fase `inicio`, proceso `IP`, **etapa 1 = iniciación** (la SU es etapa 0, pre-proyecto) |
| Fin de IP | `puerta autorizar-proyecto` | `proyecto_autorizado=true` (sigue en IP hasta autorizar la primera etapa de entrega) |
| Fin de IP o SB | `puerta autorizar-etapa --etapa-nombre ".." --fin ..` | fase `entrega`, proceso `CS`, `etapa_actual` avanza a n+1 (primera de entrega = 2); vacía las tolerancias de etapa para fijarlas con `tolerancia --nivel etapa` |
| Fin de etapa | `limite-etapa` | proceso `SB` (solo con fase `entrega`) |
| Excepción | `limite-etapa --excepcion X-001` → `puerta autorizar-plan-excepcion` | SB con `excepcion_abierta`; al aprobar vuelve a CS (o a IP si ocurrió en iniciación) y limpia la excepción |
| Última etapa o cierre anticipado | `cierre [--prematuro]` | fase `cierre`, proceso `CP`, `cierre_prematuro` (solo desde fase `entrega`, CS o SB) |
| Fin de CP | `puerta autorizar-cierre` | fase `cerrado` |
| Cualquier momento | `puerta decision-ad-hoc` | solo registra (p. ej. pedir un plan de excepción) |

- `condicionado` avanza igual que `aprobado` y deja las condiciones abiertas (las muestra `siguiente`) hasta `cumplir-condiciones <tipo>`.
- `pendiente` no cambia nada ni escribe en `decisiones.csv`; la siguiente decisión del mismo tipo la marca `resuelta`.
- `rechazado` de etapa o de plan de excepción no avanza; el script recuerda las opciones: replanificar o `cierre --prematuro`.
- Una puerta que no corresponde al estado actual se rechaza; `--forzar` la registra igual y queda marcada `forzada`.
- `etapa --numero n --nombre ..` y `set fase=..` quedan solo para correcciones; las transiciones normales las producen `puerta`, `limite-etapa` y `cierre`.

## 2. Migración automática de versiones anteriores
Al leer un `estado.json` antiguo, `esquema.py` lo actualiza en memoria y `estado.py` lo guarda en la siguiente escritura:
- tolerancias planas → niveles `proyecto` / `etapa`;
- agrega `product_owner`, bloque `agil`, `proyecto_autorizado`, `excepcion_abierta`;
- fase `planificacion` → `inicio`; **fase `ejecucion` → `entrega`** (v1 → v2, nombre PRINCE2 de las etapas de entrega);
- completa las claves de `integraciones` que falten con sus valores por defecto; `cronograma=mermaid|utf8proj` → `cpm`.
Los CSV antiguos reciben las columnas nuevas al primer uso de `registro.py`. `nuevo_proyecto.py` crea las carpetas de
v2 (`02-planificacion/especificacion/`, `03-control/reuniones/`, `03-control/fuentes/`); en un proyecto migrado no se crean
solas: las crea el script que escribe en ellas o se agregan a mano (vacías).

## 3. Carpetas de la v2 y su dueño
| Carpeta | Contenido | Quién escribe |
|---|---|---|
| `02-planificacion/especificacion/` | derivados del puente BMAD: `inventario-bmad.json`, `requisitos-bmad.csv`, `matriz-trazabilidad-bmad.csv` | solo `pm-bmad-puente` (`bmad.py`); no editar a mano |
| `03-control/reuniones/` | transcripciones normalizadas y actas | `pm-reuniones` (`transcripcion.py`) |
| `03-control/fuentes/` | instantáneas fechadas `<sistema>-AAAA-MM-DD.(csv\|md\|json)` de Jira, Slack, Teams… | `pm-integraciones` |
| `00-direccion/historial/` | versiones aprobadas congeladas (PID, business case, `bmad-<art>-v<ver>/`) | `pm-director` |
El resto de la estructura está en SPEC §1.5.

## 4. Claves de `estado.json.integraciones`
Comandos de configuración (ejemplos): `estado.py tolerancia --nivel proyecto|etapa tiempo=".." costo=".." …` (siete dimensiones); `rol gestor_proyecto=".." product_owner=".." autoridad_cambio=".."` (listas con `;`); `agil cadencia_iteracion_dias=14 velocidad_referencia=30`; `integracion tracker=jira chat=teams especificacion=bmad cronograma=mspdi`; `umbrales-riesgo alto=.. medio=..`.

| Clave | Valores | Uso |
|---|---|---|
| `tracker` | `ninguno` · `jira` · `linear` · `github` · `azure-devops` | backlog, acciones, issues vía `pm-integraciones` |
| `chat` | `ninguno` · `slack` · `teams` | publicación de resúmenes (con confirmación) |
| `docs` | `ninguno` · `confluence` · `notion` · `sharepoint` | lectura/publicación de páginas |
| `reuniones` | `manual` · `archivo` · `granola` · `fireflies` · `zoom` · `minutes` | origen de transcripciones (`pm-reuniones`) |
| `okr` | `archivo` · `tability` | `okr.csv` (`pm-okr`) |
| `diagramas` | `mermaid` · `diagram-design` · `archify` · `visual-explainer` · `drawio` | `pm-visuales` |
| `cronograma` | `cpm` · `mspdi` | `cpm.py` solo, o además `--mspdi` para MS Project |
| `export` | `scripts` · `skills-office` | vía de `pm-exportar` |
| `especificacion` | `ninguna` · `bmad` | con `bmad`, requisitos en el PRD y puente `pm-bmad-puente` |
| `bmad` | `{raiz, layout: v6\|v4, soporte}` | lo completa `bmad.py detectar` |
Se escriben con `estado.py integracion clave=valor …`. Ninguna integración es obligatoria: sin ellas se usan CSV,
Markdown, Mermaid y scripts.

## 5. Opciones de los scripts
Ruta `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/` según instalación: plugin `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/`, manual `~/.claude/skills/pm-estado-proyecto/`, Hermes `~/.hermes/skills/pm-estado-proyecto/`.
### 5.1 `registro.py`
`agregar <registro> --campo k=v …` (id, fecha y estado inicial automáticos; riesgos: puntuación P×I y EMV) ·
`actualizar <registro> <id> --campo …` · `listar <registro> [--abiertos | --estado x] [--json]` ·
`resumen [--corte AAAA-MM-DD] [--json]` (corte = fecha del informe o tablero; conteos, riesgos altos y sin
respuesta/propietario, top 5, acciones vencidas y por responsable, issues sin responsable) · `esquema <registro>`.
Acepta alias en inglés (`threat`, `high`, `open`, `change-request`…) y guarda el valor canónico; mensajes en el idioma
del proyecto. `--forzar` solo con motivo en `notas`. Umbrales de riesgo propios: `estado.py umbrales-riesgo alto=.. medio=..`.
En `decisiones`, `reemplaza` y `conviven` (D-### separados por `;`) se validan con `vigencia.py`: ids existentes, sin
ciclos ni reemplazos dobles (`--forzar` lo omite) y autoridad, que no se omite: nivel igual o superior al de la
reemplazada y quien decide con esa autoridad (`pm-direccion-decisiones` guía §13.10).
**Bitácora y propuestas (2.6.0, SPEC §1.10.16):** `historial [id|registro|estado|P-###] [--desde AAAA-MM-DD] [--max N]
[--json]` (escrituras anotadas en `<proyecto>/.bitacora.jsonl` y verificación de la cadena) · `reconocer <registro|estado>
--por … --motivo …` (asienta un cambio hecho fuera de los scripts; cierra BIT-02) · `proponer <registro> [id] --campo …
--por … [--motivo …]` · `propuestas [--estado pendiente|aplicada|reaplicada|conflicto|rechazada|todas] [--json]` ·
`aprobar P-### --por …` · `rechazar P-### --por … --motivo …` (pm-registros guía §3.1). La bitácora la escribe
`esquema.escribir_atomico` (el mecanismo común de 2.5.1), así que cubre `estado.py`, `puertas.py`, `interesados.py`,
`envios.py`, `bmad.py` y todo lo que llama a `registro.py`, bajo el mismo bloqueo: el script no tiene que hacer nada;
`esquema.contexto_bitacora(operacion=…, por=…)` precisa lo que no sale de la línea de comandos.

### 5.2 `evm.py`
`--pv --ev --ac --bac` o `--csv progreso.csv` (columnas `pv|pv_acumulado`, `ev|ev_acumulado`, `ac|ac_acumulado`) ·
`--tol-costo 10 --tol-plazo 10` (verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo fuera → `excepcion_prevista`) ·
`--eac tendencia|atipico|compuesto` · `--modo agil [--pct-no-must N]` (semáforos de costo/plazo `n/a-agil`; calcula
`alcance_no_entregable_pct` y `semaforo_alcance`; excepción solo si supera el % Should/Could) · `--proyecto <dir>`
(idioma y tolerancias de etapa en % desde `estado.json` si no se pasan `--tol-*`) · `--idioma es|en` · `--json`.
BAC sin reserva de gestión (SPEC §1.10.6).

### 5.3 `cpm.py`
CSV `id,nombre,duracion,predecesoras,recurso[,wbs]`. `cpm.py actividades.csv --inicio AAAA-MM-DD --mermaid gantt.md [--json]
[--mspdi cronograma.xml --titulo "Nombre" --wbs wbs.csv]`. Ids con guiones (`WP-1.1`), lag explícito `id+N` / `id-N`,
duraciones decimales hacia arriba, 0 = hito; imprime ES/EF/LS/LF, holgura total (HT) y libre (HL), camino crítico y
carga por recurso. `--mspdi` escribe MS Project XML (calendario estándar, tareas resumen por código EDT de la columna
`wbs`, nombradas con `--wbs wbs.csv`); importable en MS Project, ProjectLibre y herramientas basadas en MPXJ (validado con
MPXJ). Solo fin-a-comienzo y sin nivelación: SS/FF/SF, calendarios y nivelación → `pm-cronograma-estimacion`.

### 5.4 `wbs.py`
CSV `codigo,nombre,tipo,responsable,esfuerzo_h,costo[,ref]` (`tipo`: producto | paquete | hito; esfuerzo y costo solo en
hojas; `ref` = ids FR-n o claves de historia para trazabilidad). `wbs.py 02-planificacion/wbs.csv [--titulo ".."]
[--mermaid 02-planificacion/visuales/wbs.md] [--diccionario 02-planificacion/diccionario-wbs-esqueleto.md] [--json]
[--profundidad 3]`. Valida códigos, duplicados y padres faltantes (errores), avisa de valores en nodos con hijos y de hojas
de tipo producto, consolida esfuerzo y costo por nivel (regla del 100 %), dibuja el árbol y genera el esqueleto del
diccionario. Lo usa sobre todo `pm-planificacion-por-productos`; `bmad.py trazabilidad --wbs` lee su columna `ref`.

### 5.5 `exportar.py`
`docx --entrada <md> --salida exportados/<nombre>.docx` (banda "BORRADOR / DRAFT" si el frontmatter no dice `aprobado`;
Mermaid como imagen si `mmdc` está instalado) · `xlsx --proyecto <dir>` (una hoja por registro) o `--entrada <csv>
--salida <xlsx>`. ZIP de puerta: `pm-exportar` (`paquete.py`).

## 6. Scripts compartidos: quién los usa
| Script | Skills que lo usan habitualmente (además de esta) |
|---|---|
| `nuevo_proyecto.py` | pm-mandato-y-brief, pm-orquestador / `pm-nuevo` |
| `estado.py` | todas las skills de fase; `puerta` solo pm-director (pm-direccion-decisiones); `productos`: pm-paquetes-trabajo, pm-calidad, pm-cierre-proyecto, `sanidad.py` (QUA-04) y `puertas.py` (C-07); `periodo` (datos del período → tablero y borrador del highlight, `--verificar` = cadena de reporte): pm-progreso-reportes (guía §14) y pm-visuales (guía §3) |
| `registro.py` | pm-registros, pm-riesgos, pm-issues-cambios, pm-calidad, pm-lecciones-aprendidas, pm-paquetes-trabajo, pm-progreso-reportes, pm-comunicacion-stakeholders, pm-reuniones, pm-cierre-proyecto, pm-direccion-decisiones |
| `esquema.py` | importado por los demás scripts; documentado en `pm-registros/templates/guia-registros.md`; bloqueo, escritura atómica y bitácora de escrituras (`anotar_bitacora`, `verificar_bitacora`, `reconocer_bitacora`: `registro.py historial`, `sanidad.py` BIT, `paquete.py auditoria --con-bitacora`) |
| `vigencia.py` | `registro.py` (validación de `reemplaza`/`conviven`), `esquema.anotar_decision` (reemplazo automático de aprobaciones, presupuestos, enfoque y veredicto del gate de preparación de BMAD), `sanidad.py` (DEC-05, DEC-06) y `pm-direccion-decisiones/scripts/decision.py` (`vigentes`, expediente solo con vigentes) |
| `texto.py` | normalización para buscar en español e inglés (lemas, fechas, cifras, ids): `decision.py expediente --tema` y `vigentes --tema`, `vigencia.py`; lista para el futuro indexador (SPEC §1.10.15) |
| `evm.py` | pm-progreso-reportes, pm-agil-hibrido, pm-costos-presupuesto, pm-cierre-proyecto |
| `cpm.py` | pm-cronograma-estimacion, pm-plan-etapa-y-limites |
| `wbs.py` | pm-planificacion-por-productos, pm-costos-presupuesto, pm-bmad-puente (trazabilidad) |
| `exportar.py` | pm-exportar, pm-costos-presupuesto |
| `especificacion.py` | todas las que leen requisitos, épicas o historias (SPEC §1.16): pm-mandato-y-brief, pm-caso-de-negocio, pm-okr, pm-planificacion-por-productos, pm-cronograma-estimacion, pm-costos-presupuesto, pm-agil-hibrido, pm-plan-etapa-y-limites, pm-paquetes-trabajo, pm-progreso-reportes, pm-riesgos, pm-calidad, pm-issues-cambios, pm-cierre-proyecto, pm-visuales, pm-sync, pm-puerta; importa `pm-bmad-puente/scripts/bmad.py` como proveedor cuando `integraciones.especificacion = bmad` |
Un cambio de interfaz en un script obliga a revisar esas skills; agregar columnas exige cambiar a la vez `esquema.py`
y `guia-registros.md`.

## 7. Equivalencias de nombres de registros
riesgos = risk register · issues = issue register · cambios = change log · decisiones = decision log · supuestos =
assumption log · lecciones = lessons log · stakeholders = stakeholder register · calidad = quality register · acciones =
action log · diario = daily log.

## 8. Reglas complementarias que los scripts hacen cumplir
- [PRINCE2] Issues: cinco tipos exactos, con `decision` y `decidido_por` antes de cerrarse; una acción va a `acciones.csv`.
- [PMBOK→Risk] P e I 1–5; alto ≥15, medio 6–12, bajo ≤5; EMV con 10/30/50/70/90 % (configurable con `umbrales-riesgo`).
- Toda escritura de `estado.json`, de un registro o de una propuesta queda en la bitácora con huellas; una propuesta se
  aplica solo con la aprobación de una persona distinta de quien propuso y sin conflicto en los campos que toca.

## 9. Radar de atención y briefing de incorporación
`estado.py --proyecto <dir> radar [--corte AAAA-MM-DD] [--max 5] [--json | --linea]` responde, sin escribir nada, qué hay
que **decidir**, **escalar**, **desbloquear** y **vigilar** al corte. Cada ítem trae regla, id, fecha, responsable (o quién
decide), qué pasa y el siguiente paso con su skill o script. Es la actividad de control de etapa «evaluar el estado de la
etapa» con «capturar» y «escalar issues y riesgos» (`pm-knowledge/references/prince2-principios-personas-procesos.md`
§5.4) y la gestión por excepción (`prince2-practicas-riesgo-issues-progreso-productos.md` §4.c.2 y §7.3, A-16 a A-20).
Reutiliza `estado.py contexto` (conteos y próxima puerta), los controles de `sanidad.py` (CAM, TOL, SUP, QUA), el último
corte de EVM guardado, `puertas.py` (bloqueos de la próxima puerta) y los presupuestos y tolerancias de `estado.json`.

| Grupo | Regla | Cuándo aparece | Prioridad | Responsable o quien decide |
|---|---|---|---|---|
| Decidir | EST-14 | excepción abierta esperando el plan de excepción | 1 | junta |
| Decidir | SUP-02 | supuesto crítico con la fecha límite vencida sin resultado | 1 | responsable del supuesto |
| Decidir | RAD-03 | contingencia por activar: riesgo con respuesta `contingencia` que ocurrió o es `inminente`, sin cambio vigente con cargo `reserva-riesgo` que lo cite | 1 | propietario del riesgo |
| Decidir | RAD-01 | cambio `pendiente-decision` | 2 | autoridad de cambio; la junta si no hay autoridad delegada, si el costo supera `limite_autoridad_cambio`, si agota el presupuesto de cambio o si el cargo es `reserva-gestion` o `plan-excepcion` (A-20) |
| Decidir | RAD-02 | issue o riesgo `escalado` | 2 | junta |
| Decidir | EST-11, EST-12 | puerta pendiente; condiciones abiertas de una puerta | 2 | junta (registra pm-director) |
| Decidir | SUP-03 · SUP-01 | supuesto invalidado sin tratar · crítico sin experimento o fecha límite | 2 · 3 | responsable del supuesto |
| Decidir | REG-11 | lección de impacto alto sin acción ni decisión | 3 | responsable de seguimiento de la lección |
| Escalar | TOL-01 | el último EVM pronostica salir de la tolerancia y no hay excepción abierta | 1 | gestor → junta |
| Escalar | CAM-03 | presupuesto de cambio o reserva de riesgo excedido (ERROR de sanidad) | 1 | gestor → junta |
| Escalar | RAD-04 · CAM-04 · CAM-05 | riesgo con respuesta `escalar` sin escalar (A-19) · cambio sobre el límite delegado · reserva de gestión sin la junta | 2 | gestor o junta |
| Desbloquear | REG-07 | acción vencida | 1 | responsable de la acción |
| Desbloquear | RAD-05 | issue abierto sin responsable | 1 urgente · 2 alta · 3 resto | gestor (asigna) |
| Desbloquear | REG-06 | riesgo alto sin respuesta o sin propietario | 2 | gestor |
| Desbloquear | RAD-06 · QUA-02 · QUA-03 | dependencia (issue o acción abierta que cita otro issue, cambio, acción o revisión abierta) · revisión de calidad vencida · rechazada sin tratar | 3 | responsable del ítem |
| Vigilar | REG-09 · RAD-07 · CAM-03 | revisión de riesgo vencida · bloqueos de la próxima puerta · presupuesto al 80 % o más | 3 | propietario o gestor |
| Vigilar | REG-12 | lección accionada sin verificar su efecto a la fecha prevista | 3 | responsable de seguimiento de la lección |
| Vigilar | TOL-02 · TOL-03 · RAD-08 | EVM en ámbar · sin corte reciente · supuesto crítico en validación con fecha futura | 4 | gestor o responsable |

**Regla de prioridad:** 1 = hoy (vencido, fuera de tolerancia o presupuesto agotado), 2 = espera una decisión o bloquea, 3 =
pendiente sin bloqueo inmediato, 4 = vigilar. Dentro de cada grupo se ordena por prioridad, fecha (las vacías al final) e
id; con los mismos registros y el mismo `--corte`, la salida es la misma. «Hoy» muestra el primer ítem de decidir, escalar y
desbloquear. Las opciones finales son generar el highlight (`pm-progreso-reportes`) y, solo si hay TOL-01 o CAM-03,
escalar una excepción (informe de excepción → pm-director); dentro de tolerancia, la desviación se trata con acción
correctiva y se informa en el highlight (A-18). Salida acotada: `--max` ítems por grupo con «… y N más» y a lo sumo 3.500
caracteres; `--json` da totales, «hoy» e ítems por grupo; `--linea` es la línea del hook de inicio (totales y primer id
por grupo, sin texto libre de los registros ni la verificación de la puerta).

`estado.py --proyecto <dir> briefing [--para ST-###] [--corte AAAA-MM-DD] [--salida RUTA|-] [--json]` llena
`pm-progreso-reportes/templates/briefing-incorporacion.md` con el mismo motor: contexto (fase, etapa, junta, tolerancias,
presupuestos, abiertos), rol del interesado (`--para`: rol, contacto, RACI, lo que tiene a cargo y sus ítems del radar),
decisiones de nivel junta, ejecutivo o capa de negocio, riesgos altos, issues y cambios pendientes, último EVM, artefactos
aprobados (con su copia congelada), próxima puerta con sus bloqueos y condiciones (`puertas.py`) y los cinco primeros pasos
del radar. Cada cifra cita su id o su archivo; a lo sumo 6.500 caracteres (≈ 2 páginas: las tablas se recortan con «… y N
más»); el texto de los registros va en una línea, sin `|` ni etiquetas HTML. Escribe
`03-control/reportes/<corte>-briefing-incorporacion[-ST-###].md` como borrador (`-` lo muestra en pantalla) y no lo
registra: si se distribuye, `estado.py artefacto briefing-<fecha> --ruta … --estado en-revision`. Nunca muestra actitudes ni
valoraciones de interesados. Para un agente, `--json` da los totales y el resumen; el Markdown es la lectura completa.

## 10. Estado de productos (product status account)
`estado.py --proyecto <dir> productos [--corte AAAA-MM-DD] [--fuente auto|backlog|wbs] [--alcance proyecto|WP-###|<release o iteración>|<código WBS>] [--max 40] [--json | --markdown [RUTA]]`,
de solo lectura: el registro de productos de PRINCE2 (A13) derivado de `backlog.csv` o `wbs.csv`, `calidad.csv`, `issues.csv`,
las aceptaciones de `estado.json` y los paquetes de trabajo (descripción y recepción), sin registro propio. Regla de
estados, convención de citas, corte y Must sin aceptar: guía de `pm-paquetes-trabajo` §5 (fuente única). La misma
función alimenta QUA-04 de la sanidad (productos de la WBS) y C-07 de `autorizar-cierre` (`docs/PUERTAS.md` §3).
