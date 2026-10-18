# Guía de visuales del método · Method visuals guide

## 1. Motores y contrato con skills externas
`integraciones.diagramas` admite un valor o una lista por prioridad (`estado.py --proyecto <dir> integracion diagramas=archify,visual-explainer`). Para cada visual se usa el primer motor de la lista que cubra su tipo (tabla 1.2); si ninguno lo cubre, Mermaid, sin que cuente como falla.

### 1.1 Nombres reales y cómo se reconocen (verificado en vivo, Claude Code 2.1, 2026-10-17)
| Valor | Skill a invocar (herramienta Skill) | Distribución · licencia | Requisitos | Instalación (detalle en `docs/INSTALACION.md` §6.1) |
|---|---|---|---|---|
| `archify` | `archify` | carpeta de skill (no es plugin) · MIT | Node ≥ 18 para ejecutarla (`npx skills add` requiere Node ≥ 22.20); Chrome/Chromium para `browser-check` (`ARCHIFY_CHROME=<ejecutable>` si no lo encuentra) | `npx skills add tt-a1i/archify -a claude-code -s archify -y` |
| `diagram-design` | `diagram-design` (copia) o `diagram-design:diagram-design` (plugin) | plugin con marketplace + carpeta `skills/diagram-design` · MIT | Python 3; Playwright + Chromium solo para PNG | `/plugin marketplace add cathrynlavery/diagram-design` + `/plugin install diagram-design@diagram-design`, o `npx skills add cathrynlavery/diagram-design -a claude-code -s diagram-design -y` |
| `visual-explainer` | `visual-explainer` (copia) o `visual-explainer:visual-explainer` (plugin) | plugin con marketplace (SKILL.md en la raíz del plugin) · MIT | Node ≥ 18; `playwright-core` opcional para `kit/check.mjs` | `/plugin marketplace add nicobailon/visual-explainer` + `/plugin install visual-explainer@visual-explainer-marketplace`, o `npx skills add nicobailon/visual-explainer -a claude-code -s visual-explainer -y` |
| `drawio` | herramientas `mcp__drawio…` | servidor MCP | el del servidor | `claude mcp add …` |

Está instalada si figura en el listado de skills de la sesión con cualquiera de esos nombres, o si `sanidad.py --proyecto <dir>` informa INS-03 "invocar como …". No basta con que exista la carpeta: se invoca la skill.

### 1.2 Tipo de cada visual por motor
| Visual | `archify` (tipo JSON) | `diagram-design` (tipo) | `visual-explainer` (página) |
|---|---|---|---|
| Organigrama | `tree` | org chart | — |
| PBS / WBS | `tree` | tree (importar el Mermaid de `wbs.py`) | — |
| Mapa poder/interés | — | quadrant | — |
| Flujo de productos | `workflow` | flowchart / dependency | — |
| Roadmap por etapas | `timeline` | timeline | roadmap comentado |
| Flujo de excepciones | `workflow` | swimlane | — |
| One-pager (brief, canvas, resumen de etapa) | — | — | "One diagram" / explicador de una página |

### 1.3 Contrato de delegación (obligatorio cuando el motor está configurado e instalado)
1. **Respaldo primero**: tabla intermedia (id, etiqueta, padre/dependencia, atributos, fuente) y Mermaid en `<carpeta>/<nombre>.md` (WBS con `wbs.py --mermaid`). Para el one-pager, la tabla de campos del brief.
2. **Invocar la skill** con la herramienta Skill por su nombre real (1.1) y seguir su procedimiento con estos parámetros fijados por pm-visuales: ruta de salida, idioma del proyecto, título bilingüe, ids de la fuente en cada nodo, "BORRADOR" si la fuente no está aprobada, fuente y fecha de corte en el pie. No improvisar el HTML a mano si la skill está disponible.
3. **Ruta**: `02-planificacion/visuales/<nombre>.html` (planes, one-pager `one-pager-<fuente>.html`) o `03-control/reportes/AAAA-MM-DD-<nombre>.html`. Los subproductos del motor quedan junto a la salida con el mismo prefijo; nunca en `~/.agent/diagrams/`, `.archify/` del cwd ni carpetas de BMAD.
4. **Sin preguntas bloqueantes**: si el motor pide confirmar estilo o plan y el usuario no está (subagente, `claude -p`), usar el estilo por defecto, seguir y anotar los supuestos en la respuesta.
5. **Verificar**: el archivo existe, pasó la comprobación del motor (1.4) y contiene los ids de la fuente sin nodos inventados; si no, se descarta.
6. **Registrar** `estado.py --proyecto <dir> artefacto <clave> --ruta <salida.html> --estado borrador` y cerrar con el motor usado, la salida y el respaldo `.md`.
7. **Falla o ausencia** (no figura en el listado, error del motor tras dos reparaciones, salida sin ids): queda el Mermaid, nota en `diario.md` ("motor X no disponible/falló: <causa>; se entrega Mermaid") y aviso al usuario.

### 1.4 Receta por motor
- **archify**: escribir el candidato `<carpeta>/<nombre>.candidate.json` según el esquema del tipo (leer `schemas/<tipo>.schema.json` y el ejemplo que indica su SKILL.md), con `meta.output` = ruta de salida relativa al directorio de trabajo; luego, desde ese directorio, `node <archify>/bin/archify.mjs finalize <tipo> <nombre>.candidate.json <salida>.html --quality showcase --json` (rutas relativas al cwd). Éxito = `"ok": true` con `validate`, `deliver`, `check` y `browser-check` en `pass`. Si solo `browser-check` queda `skipped` por falta de Chrome, el HTML vale como "verificado sin navegador" (decirlo y anotarlo). Sin red: `ARCHIFY_UPDATE_CHECK_DISABLED=1`. El árbol `tree` es de un solo padre: aseguramiento y soporte se cuelgan de la junta o del gestor y se aclara en el pie.
- **diagram-design**: la primera vez exige revisar `references/style-guide.md`; sin marcador `.diagram-design` en el proyecto, preguntar una vez al usuario (personalizar o estilo por defecto); sin usuario, estilo por defecto (opción e). Para la WBS u otro Mermaid de respaldo, usar la vía de importación: `python3 <diagram-design>/scripts/mermaid_extract.py <respaldo>.md` y redibujar con detalle `faithful` (conserva todos los nodos; zonas sobre 9, dividir sobre 24). Copiar `assets/template.html`, cargar la referencia del tipo y comprobar con `python3 <diagram-design>/scripts/self_check.py <salida>.html` (debe imprimir `OK`). PNG opcional con `scripts/export_png.py` (Playwright). Las tipografías se cargan de Google Fonts; sin conexión, pedir fuentes del sistema (style-guide § Font source).
- **visual-explainer**: escribir la fuente `<carpeta>/<nombre>.src.html` (registro `data-register`, `<link rel="stylesheet" href="kit.css" data-ve-kit>`) y renderizar con `node <visual-explainer>/kit/render.mjs <nombre>.src.html` **sin `--open`** → `<nombre>.html` (debe imprimir `✓`). `kit/check.mjs` solo si `playwright-core` está instalado. Nunca escribir en `~/.agent/diagrams/`.
- **drawio**: servidor MCP oficial de draw.io (`jgraph/drawio-mcp`, npm `@drawio/mcp`) desde la tabla intermedia (nodo, padre, etiqueta); `.drawio` + PNG/SVG junto al `.md`.

`<archify>`, `<diagram-design>` y `<visual-explainer>` son la carpeta base que informa la herramienta Skill al invocarla (o la ruta de INS-03).

## 2. Contenido de cada visual
- **Organigrama**: tres intereses (negocio, usuario, proveedor) en la junta, un ejecutivo, gestor, aseguramiento separado, soporte, gestores de equipo; líneas de reporte; autoridad de cambio si existe. Si la fuente viola la separación, se señala.
- **Mapa poder/interés**: cuatro cuadrantes con criterios explícitos; actitud; estrategia por cuadrante; circulación restringida; nunca para evaluar personas del equipo.
- **Reporte de interesados (v2.2)**: es el visual del maestro de interesados y lo genera su dueña, `pm-interesados`: `python3 ${CLAUDE_SKILL_DIR}/../pm-interesados/scripts/interesados.py --proyecto <dir> reporte --html 03-control/reportes/<fecha>-interesados.html` (HTML autocontenido con la matriz poder/interés en SVG, RACI, perfiles y envíos; contenido y opciones en la guía de `pm-interesados` §8). pm-visuales no lo redibuja ni copia sus datos: lo enlaza o lo incluye en un tablero; un mapa poder/interés con motor externo (tabla 1.2) parte de `interesados.py matriz --json`.
- **PBS/WBS**: producto del proyecto en la raíz; externos marcados; sin actividades en la PBS; la WBS deriva de la PBS. Desde `wbs.csv`: `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/wbs.py 02-planificacion/wbs.csv --titulo "<Proyecto>" --mermaid 02-planificacion/visuales/wbs.md [--profundidad 3] [--diccionario 02-planificacion/diccionario-wbs-esqueleto.md]` (valida la EDT, consolida esfuerzo y costo y escribe el árbol Mermaid `flowchart TD`). El contenido de la EDT es de `pm-planificacion-por-productos`; aquí solo se dibuja.
- **Flujo de productos**: dependencias entre productos de un plan; externos como entradas; aristas sin confirmar en línea punteada.
- **Gantt y roadmap**: Gantt desde `cpm.py --mermaid` o el plan (camino crítico resaltado); roadmap por etapas de gestión con puertas como hitos.
- **Flujo de excepciones**: paquete → gestor; etapa → junta; proyecto → capa de negocio, con tolerancias y quién decide.
- **Canvas de arranque**: `templates/canvas-arranque.html` con los campos del brief (contenido en `01-inicio/canvas-arranque.md` de `pm-mandato-y-brief`).

## 3. Tablero de avance: inyección de datos
HTML autocontenido (sin red ni librerías; SVG generado en la página). Todo el contenido variable vive en un único bloque `<script type="application/json" id="datos-tablero">`; no se editan celdas: se arma el JSON y se reemplaza el bloque.

```python
import json, re, subprocess, pathlib
P = "<dir>"; S = "<pm-estado-proyecto>/scripts"; T = "<pm-visuales>/templates/tablero-avance.html"
def reg(*a):
    r = subprocess.run(["python3", f"{S}/registro.py", "--proyecto", P, *a, "--json"], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)
e = json.load(open(f"{P}/estado.json", encoding="utf-8"))
datos = {"proyecto": e["proyecto"], "etapa": e["etapa_actual"]["nombre"], "enfoque_entrega": e["enfoque_entrega"],
         "idioma": e["idioma"], "estado": "borrador", "fecha_corte": "AAAA-MM-DD",
         "periodo_desde": "...", "periodo_hasta": "...", "proximo_hasta": "...",
         "riesgos": reg("listar", "riesgos", "--abiertos"), "issues": reg("listar", "issues", "--abiertos"),
         "acciones": reg("listar", "acciones"), "resumen_registros": reg("resumen", "--corte", "AAAA-MM-DD"),
         "umbrales_riesgo": {"alto": 15, "medio": 6},
         "objetivos": [...], "hitos": [...], "decisiones_pendientes": [...],   # del highlight y de evm.py --json
         "agil": {"iteraciones": [...], "ventana_velocidad": 3, "fecha_fija": "", "fecha_pronostico": "", "must_en_riesgo": []},
         "comentario_gestor": "...", "fuentes": "...", "fecha_generacion": "AAAA-MM-DD", "confirmado_por": ""}
html = pathlib.Path(T).read_text(encoding="utf-8")
bloque = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
html = re.sub(r'(<script type="application/json" id="datos-tablero">)(.*?)(</script>)',
              lambda m: m.group(1) + bloque + m.group(3), html, count=1, flags=re.S)
pathlib.Path(f"{P}/03-control/reportes/AAAA-MM-DD-tablero-avance.html").write_text(html, encoding="utf-8")
```

Campos:
- `objetivos[]` = `{clave: tiempo|costo|alcance|calidad|beneficios|riesgo|sostenibilidad, pronostico, tol_etapa, tol_proyecto, rag: verde|ambar|rojo|na}`. Tiempo y costo copian `semaforo_cronograma` y `semaforo_costo` de `evm.py`; con `--modo agil` salen `n/a-agil` → `rag: na` y `semaforo_alcance` en alcance.
- `hitos[]` = `{hito, base, actual, var_dias, rag, comentario}`.
- `decisiones_pendientes[]` = `{id, texto, fecha_limite}` (id del registro que origina la decisión, p. ej. R-001 o C-002).
- `agil.iteraciones[]` = `{nombre, planificado, terminado, alcance_total, terminado_acumulado}`; con BMAD, una iteración por fila de `03-control/reportes/avance-bmad.csv` (`alcance_total` = `puntos_total`, `terminado_acumulado` = `puntos_terminados`). La sección ágil se muestra con `enfoque_entrega` `agil`/`hibrido` o si hay iteraciones.
- `riesgos`, `issues`, `acciones`: filas de los CSV tal cual (las usan el mapa de calor, las tablas y la vista por actor).
- Acciones vencidas con la misma fecha de corte del tablero (`registro.py resumen --corte <fecha>`).
- `estado: "aprobado"` (quita la marca BORRADOR) solo tras la confirmación del gestor.

## 4. Vista por actor
Sección 5b del tablero ("Vista por actor / View by actor"): un selector (`<select id="sel-actor">`) lista todas las personas o roles que tienen compromisos abiertos y filtra una tabla única con:
- acciones abiertas de `D.acciones` (por `responsable`, fecha `fecha_compromiso`; vencidas marcadas ⚠ contra `fecha_corte`);
- riesgos de `D.riesgos` en estado abierto, en-seguimiento o escalado (por `propietario`, fecha `fecha_revision`);
- issues de `D.issues` en estado abierto, en-evaluacion, en-accion, escalado o pendiente-cambio (por `responsable`).
Sin responsable aparece como "sin-responsable / unassigned" (señal para `pm-registros`). Se abre ya filtrada con `?actor=<Nombre>` en la URL (debe coincidir exactamente con el valor del registro), útil para enviar a cada persona su enlace. No requiere campos nuevos en el JSON. Es una vista de compromisos, no de desempeño: no se usa para evaluar personas.

## 5. Tableros alimentados por trackers externos
Si hay un tracker conectado (Jira, Linear, GitHub, Azure DevOps), `pm-integraciones` deja una instantánea fechada en `03-control/fuentes/<sistema>-AAAA-MM-DD.(csv|json)`. El tablero puede tomar de ella el avance de ítems (iteraciones, terminado, alcance) o los bloqueos, siempre:
- citando la instantánea en `fuentes` y usando su fecha como fecha de corte (no se lee la herramienta en vivo);
- sin reemplazar a los registros de gobierno: riesgos, issues y acciones salen de los CSV del proyecto; si el tracker muestra algo que no está en los registros, se avisa a `pm-control` para registrarlo;
- publicar el tablero en un portal, chat o correo solo vía `pm-integraciones`, con vista previa y confirmación.

## 6. Datos mínimos por visual
| Visual | Datos mínimos | Fuente | Si falta |
|---|---|---|---|
| Organigrama | ejecutivo, usuario sénior, proveedor sénior, gestor | `estado.json.roles` | nodo `[por confirmar]`; avisar a `pm-organizacion-roles` |
| Mapa de stakeholders | nombre o grupo, poder, interés | `stakeholders.csv` (vía `interesados.py matriz --json`) | no ubicar; listar aparte |
| Reporte de interesados | maestro con poder e interés | `interesados.py reporte --html` (`pm-interesados`) | lo informa su sección de integridad; avisar a `pm-interesados` |
| PBS / WBS | producto del proyecto y primer nivel | `pbs-wbs.md` o `wbs.csv` | solo raíz; pedir `pm-planificacion-por-productos` |
| Flujo de productos | productos y dependencias | descripciones de producto | aristas punteadas `[por confirmar]` |
| Gantt | actividades, duración, predecesoras, inicio | `actividades.csv` + `cpm.py` | no generar; pedir el cronograma |
| Roadmap | etapas con fechas y puertas | plan de proyecto, `estado.json.puertas` | etapas "por planificar" |
| Flujo de excepciones | tolerancias por nivel y roles | `estado.json.tolerancias`, `roles` | flujo genérico con `[por confirmar]` |
| Canvas | mandato, objetivos, producto, roles, riesgos | brief | bloques vacíos con ayuda |
| Tablero | semáforo, hitos, riesgos, acciones por actor; iteraciones en ágil | highlight, `evm.py`, registros, burn-up, instantáneas | la sección muestra "Sin datos / No data — [por confirmar]" |

## 7. Elegir el visual
- Jerarquía → árbol (organigrama, PBS/WBS). Dependencia o secuencia → flujo. Tiempo → Gantt (detalle) o roadmap (proyecto con puertas). Dos dimensiones → cuadrante. Estado para decidir → tablero, decisiones primero. Un número o una tabla corta → texto, sin visual.
- Legibilidad: títulos bilingües, leyenda, fecha de corte y fuente en el pie; ≤ ~40 nodos (si no, dividir por etapa o nivel); tabla intermedia visible al usuario si hay más de ~15 elementos.
- Sin gráficos de vanidad. HTML legible en pantalla e impresión A4.
- Versión mínima (canvas, roadmap, tablero de media página) en proyectos pequeños; completa cuando el riesgo o los stakeholders lo justifiquen.

## 8. Casos borde
- Cronograma con dependencias SS/FF, calendarios o nivelación → `pm-cronograma-estimacion` (MSPDI con `cpm.py --mspdi`, completado en MS Project o ProjectLibre); `cpm.py` solo cubre fin-a-comienzo.
- Objetivo en rojo sin issue ni excepción registrada → avisar a `pm-control` antes de publicar; nunca un verde cosmético.
- Visual con datos de personas para circulación amplia → rechazar; ofrecer versión agregada o restringida.
