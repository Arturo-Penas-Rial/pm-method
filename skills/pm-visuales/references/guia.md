# Guía de visuales del método · Method visuals guide

## 1. Motores y contrato con skills externas
| Valor de `integraciones.diagramas` | Cuándo conviene | Cómo invocarlo |
|---|---|---|
| `mermaid` (defecto) | Incrustar en Markdown, versionable, sin dependencias | Snippets de `templates/diagramas-mermaid.md`; guardar en `02-planificacion/visuales/<nombre>.md` |
| `diagram-design` | Tipos editoriales: timeline/roadmap, swimlane del flujo de excepciones, organigrama, cuadrante poder/interés | Tipo (`timeline`, `swimlane`, `org chart`, `quadrant`), nodos/eventos con etiquetas bilingües, idioma y título; pedir SVG o PNG |
| `archify` | Flujos y arquitecturas interactivas: flujo de productos navegable, modelo de procesos con disparadores | Nodos (id, etiqueta, tipo: producto, proceso, externo) y aristas (origen, destino, etiqueta); pedir HTML autocontenido |
| `visual-explainer` | Páginas o decks explicativos para la junta o el cliente (canvas narrado, roadmap comentado) | Artefacto Markdown aprobado + audiencia; si la fuente es borrador, banda "BORRADOR" en cada pantalla |
| `drawio` (opcional, fuera del esquema) | Versión editable por el equipo | `drawio-mcp` desde la tabla intermedia (nodo, padre, etiqueta); `.drawio` + PNG/SVG |

Las cuatro externas son **opcionales**: ninguna se exige. Contrato: (a) pm-visuales **prepara el insumo** (tabla intermedia con nodos, aristas, etiquetas bilingües, fuente y fecha de corte; tipo, idioma, marca BORRADOR); (b) invoca la skill; (c) guarda la salida en `02-planificacion/visuales/<nombre>.<ext>` (planificación) o `03-control/reportes/AAAA-MM-DD-<nombre>.<ext>` (control); (d) guarda junto a ella el `.md` con el Mermaid de respaldo y la tabla intermedia; (e) registra el artefacto. Si la salida pierde los ids de la fuente o agrega nodos inventados, se descarta y se usa Mermaid. Si la skill no está instalada o falla: Mermaid/HTML interno y nota en `diario.md`. Cambiar el motor: `<pm-estado-proyecto>/scripts/estado.py --proyecto <dir> integracion diagramas=<valor>`. Los nombres de skill son mapeo del paquete; ajustar al nombre real instalado.

## 2. Contenido de cada visual
- **Organigrama**: tres intereses (negocio, usuario, proveedor) en la junta, un ejecutivo, gestor, aseguramiento separado, soporte, gestores de equipo; líneas de reporte; autoridad de cambio si existe. Si la fuente viola la separación, se señala.
- **Mapa poder/interés**: cuatro cuadrantes con criterios explícitos; actitud; estrategia por cuadrante; circulación restringida; nunca para evaluar personas del equipo.
- **PBS/WBS**: producto del proyecto en la raíz; externos marcados; sin actividades en la PBS; la WBS deriva de la PBS. Desde `wbs.csv`: `python3 <pm-estado-proyecto>/scripts/wbs.py 02-planificacion/wbs.csv --titulo "<Proyecto>" --mermaid 02-planificacion/visuales/wbs.md [--profundidad 3] [--diccionario 02-planificacion/diccionario-wbs-esqueleto.md]` (valida la EDT, consolida esfuerzo y costo y escribe el árbol Mermaid `flowchart TD`). El contenido de la EDT es de `pm-planificacion-por-productos`; aquí solo se dibuja.
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
| Mapa de stakeholders | nombre o grupo, poder, interés | `stakeholders.csv` | no ubicar; listar aparte |
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
- Cronograma con dependencias SS/FF, calendarios o nivelación → `pm-cronograma-estimacion` (MSPDI/utf8proj); `cpm.py` solo cubre fin-a-comienzo.
- Objetivo en rojo sin issue ni excepción registrada → avisar a `pm-control` antes de publicar; nunca un verde cosmético.
- Visual con datos de personas para circulación amplia → rechazar; ofrecer versión agregada o restringida.
