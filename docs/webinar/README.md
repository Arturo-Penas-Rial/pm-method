# Webinar pm-method · material por caso y generador de diapositivas

Material del webinar de pm-method: dos clases de 90 minutos por caso E2E, para un público mixto (gestores
de proyecto con algo de PMBOK o PRINCE2 y líderes de negocio). Cada caso se apoya en su guía de punta a punta
(`docs/guias/E2E-N-*.md`) y en la evidencia real de su corrida (`docs/guias/evidencia/`).

EN: Webinar material per E2E case (instructor script, attendee exercise, slide content) and the generator that turns
`diapositivas.json` into a PPTX deck and a self-contained HTML deck with glossary.

## Estructura de carpetas

```text
docs/webinar/
├── README.md                          este archivo
└── E2E-N/                             un caso (N = 1..5)
    ├── guion-instructor.md            agenda minuto a minuto, mensajes clave, preguntas, plan B
    ├── ejercicio.md                   hoja de trabajo para asistentes y solución de referencia
    ├── diapositivas.json              contenido de las diapositivas (esquema abajo)
    ├── E2E-N-diapositivas.pptx        generado: PowerPoint con notas del orador
    └── E2E-N-diapositivas.html        generado: HTML autocontenido con glosario
scripts/webinar/
├── generar.py                         validación, HTML y orquestación (Python 3.9+, biblioteca estándar)
└── pptx.js                            armado del PPTX con pptxgenjs (lo llama generar.py)
```

Las imágenes que citan las diapositivas viven en `docs/guias/img/` (los PNG 16:9 de
`scripts/pruebas/guias_e2e/visuales.py` y las capturas de los tableros).

## Cómo regenerar

Desde la raíz del repositorio:

```bash
python3 scripts/webinar/generar.py --caso docs/webinar/E2E-1             # un caso → PPTX + HTML en su carpeta
python3 scripts/webinar/generar.py --todos                               # todos los docs/webinar/E2E-*/diapositivas.json
python3 scripts/webinar/generar.py --caso docs/webinar/E2E-1 --validar   # solo valida; no escribe nada
python3 scripts/webinar/generar.py --caso docs/webinar/E2E-1 --salida /tmp/mazo   # escribir en otra carpeta
python3 scripts/webinar/generar.py --todos --logo logo-ieee.png          # usar el logo de IEEE en lugar del recuadro
```

| Opción | Qué hace |
|---|---|
| `--caso DIR` | carpeta del caso que contiene `diapositivas.json` |
| `--todos` | recorre `docs/webinar/E2E-*/diapositivas.json` en orden |
| `--salida DIR` | carpeta de salida (por defecto, la del caso) |
| `--logo PNG` | logo de IEEE para la portada y la esquina; sin él queda un recuadro rotulado «Logo IEEE» |
| `--validar` | valida el JSON y muestra errores y avisos sin generar archivos |

Código de salida: `0` sin errores (puede haber avisos), `1` con errores de validación o de generación, `2` uso
incorrecto. Requisitos: Python 3.9+ y, para el PPTX, Node.js con `pptxgenjs` (`npm install -g pptxgenjs`; el script
agrega `npm root -g` al `NODE_PATH`). Si falta Node.js o `pptxgenjs`, el HTML se genera igual y el error lo indica.

## Qué agrega el generador

- **Portada del caso**: título, subtítulo y las clases con su duración.
- **Portada de cada clase**: título, duración y objetivos (hasta 6). En el HTML, además, el índice de sus diapositivas.
- **Glosario** al final, ordenado alfabéticamente: en el PPTX, tablas término/definición en dos columnas, paginadas si
  no entran; en el HTML, una tabla con ancla por término (`#g-<término>`) y por letra (`#g-letra-X`). En el HTML, la
  primera aparición de cada término en una diapositiva enlaza a su definición.
- **Notas del orador**: el campo `nota` va a las notas del PPTX y a un bloque plegable bajo cada diapositiva del HTML.
- **Pie**: `pm-method <versión> · Webinar <caso> · Clase N` (la versión se lee de `.claude-plugin/plugin.json`) y el
  número de diapositiva.
- **Sin marca ni logo de empresa**: recuadro punteado rotulado «Logo IEEE» en la portada y en la esquina de cada
  diapositiva, o la imagen pasada con `--logo`.

El PPTX usa la estética del Informe 2 (`docs/informe/fuente/build_pptx.js`): Arial, azul marino, azul y naranja,
16:9 de 13,33″ × 7,5″, layouts con marcadores de título, una sección por clase y el tema aplicado. El HTML es un solo
archivo (CSS en línea, imágenes como data URI): navegación por clase (barra superior) y por diapositiva (selector,
botones ◀ ▶ y teclas ← →), tecla N para mostrar u ocultar todas las notas, tema claro, oscuro o automático, imágenes
ampliables con un clic, botón para copiar el prompt exacto de las demostraciones (en pantalla, los saltos de línea simples
del prompt, que vienen del ajuste de la guía, se muestran como espacios; en el PPTX también) y versión para imprimir (una diapositiva por
página apaisada; con las notas visibles, cada nota se imprime en la página siguiente a su diapositiva).

## Esquema de `diapositivas.json` (resumen)

```json
{"caso": "E2E-N", "titulo": "…", "subtitulo": "…",
 "clases": [{"numero": 1, "titulo": "…", "duracion_min": 90, "objetivos": ["…"],
   "diapositivas": [
     {"tipo": "seccion|gancho|contenido|imagen|indicadores|demo|pregunta|ejercicio|tabla|cierre",
      "titulo": "…", "subtitulo": "… (opcional)", "puntos": ["… (máx. 5, cortos)"],
      "imagen": "docs/guias/img/gN-….png (solo imagen o indicadores)",
      "tabla": {"cab": ["…"], "filas": [["…"]]},
      "pregunta": "… (tipo pregunta)", "prompt": "… (tipo demo: el prompt exacto)",
      "nota": "notas del orador: qué decir, 2–4 frases"}]}],
 "glosario": [{"termino": "…", "definicion": "…"}]}
```

La portada y el glosario los agrega el generador: no se ponen en `diapositivas`. En los textos se admite `` `código` ``
y `**negrita**`.

| Tipo | Campos que usa | Cómo se ve |
|---|---|---|
| `seccion` | titulo, subtitulo, puntos | fondo azul, «Clase N», título grande |
| `gancho` | titulo, subtitulo (frase grande), puntos (tarjetas) | frase destacada y hasta 5 tarjetas |
| `contenido` | titulo, subtitulo, puntos | filas numeradas |
| `imagen` | titulo, subtitulo (lectura), **imagen**, puntos | imagen grande; con puntos, columna «Para mirar» |
| `indicadores` | titulo, subtitulo, imagen (opcional), puntos | imagen + columna «Cómo leerlo»; sin imagen, tarjetas de indicador (`**valor** texto` → valor grande) |
| `demo` | titulo, subtitulo, **prompt**, puntos | prompt en bloque de código y «Qué deberías ver» |
| `pregunta` | titulo, subtitulo, **pregunta**, puntos (opciones) | fondo oscuro, pregunta grande, opciones |
| `ejercicio` | titulo, subtitulo, puntos (pasos) | tarjetas numeradas |
| `tabla` | titulo, subtitulo, **tabla** | tabla con cabecera azul marino |
| `cierre` | titulo, subtitulo, puntos | fondo oscuro, mensajes con ✓ |

## Validaciones

| Situación | Resultado |
|---|---|
| JSON inválido, falta `caso`, `titulo` o `clases`, clase sin `numero`, `titulo`, `duracion_min` o `diapositivas` | error |
| tipo desconocido; diapositiva sin `titulo` | error |
| más de 5 puntos | error |
| imagen citada inexistente (se busca desde la raíz del repositorio) o que no es PNG/JPEG; tipo `imagen` sin imagen | error |
| tabla de más de 6 filas o 4 columnas, o filas con distinta cantidad de celdas que la cabecera | error |
| `demo` sin `prompt`; `pregunta` sin `pregunta`; entrada del glosario sin término o definición | error |
| clase con menos de 12 o más de 20 diapositivas | aviso |
| glosario fuera de 10–25 términos; término repetido | aviso |
| clave desconocida (por ejemplo, un error de tipeo), `imagen` o `tabla` en un tipo que no las usa, diapositiva sin `nota` | aviso |
| imagen muy alta (más de 1,3 veces su ancho): se verá chica en la diapositiva | aviso |
| texto que no entra ni con el tamaño mínimo (14 pt; 12 pt en tablas) | aviso del PPTX con la diapositiva |
| `caso` distinto del nombre de la carpeta | aviso |

Con errores no se genera nada. Los avisos no detienen la generación.

## Casos

| Caso | Tema | Guía | Clases (90 min cada una) | Diapositivas de contenido | Glosario |
|---|---|---|---|---|---|
| E2E-1 | riesgos | [E2E-1-riesgos](../guias/E2E-1-riesgos.md) | 1 · Del taller al plan de respuesta · 2 · El control continuo | 37 (18 + 19) | 24 términos |
| E2E-2 | alcance, cambio, esfuerzo, priorización y mapa de ruta | [E2E-2-alcance-roadmap](../guias/E2E-2-alcance-roadmap.md) | 1 · Del alcance a la línea base · 2 · El cambio bajo control | 35 (16 + 19) | 25 términos |
| E2E-3 | interesados, comunicaciones, OKR y avance | [E2E-3-interesados-okr-avance](../guias/E2E-3-interesados-okr-avance.md) | 1 · Del mapa de interesados al plan de compromiso · 2 · Del dato al reporte y al compromiso sostenido | 38 (18 + 20) | 25 términos |
| E2E-4 | producto de la idea al producto con BMAD | [E2E-4-producto-bmad](../guias/E2E-4-producto-bmad.md) | 1 · Gobernar la construcción con BMAD · 2 · Calidad a volumen, recorrido, cierre y beneficios | 36 (16 + 20) | 25 términos |
| E2E-5 | de la idea al proyecto diseñado | [E2E-5-idea-a-proyecto](../guias/E2E-5-idea-a-proyecto.md) | 1 · ¿Vale la pena? · 2 · Diseñar el proyecto | 40 (20 + 20) | 25 términos |
| **Total** | | | **10 clases** | **186** | **124 términos** |

Las cifras de la tabla salen de `python3 scripts/webinar/generar.py --todos --validar` (línea «válido: …» de cada caso: 5/5 sin errores ni avisos). A las diapositivas de contenido el generador suma la portada del caso, la de cada clase y el glosario.

## Control de calidad

Después de regenerar, revisar el PPTX como imágenes (LibreOffice → PDF → PNG) y el HTML en el navegador, en claro,
oscuro y ancho de teléfono: textos cortados o superpuestos, imágenes legibles, avisos del generador resueltos. Las
imágenes muy altas (capturas completas de tableros) se ven chicas en la diapositiva: conviene citar un PNG 16:9 de
`visuales.py` o un recorte.
