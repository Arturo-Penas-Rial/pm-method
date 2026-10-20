# Cambios · Changelog

## 2.3.0 · 2026-10-20 — validar antes de invertir, mapas estratégicos, contexto controlado y material de formación

Versión que suma la validación de supuestos antes de invertir, la evaluación financiera de opciones, los mapas de
Wardley y de recorrido del cliente, un resumen de contexto derivado de los registros para cada sesión, la revisión de
seguridad del paquete, un entorno Docker opcional y el material de formación (cinco casos E2E con guion, ejercicio y
diapositivas). Retrocompatible: un proyecto creado con 2.2 se migra al leerse, sin dependencias nuevas en el núcleo y
sin escribir en BMAD.

En cifras: 39 skills (33 invocables por el modelo; listado de descripciones de 6.817 de 7.500 caracteres), 6 agentes,
3 hooks, 13 registros (9 base y 4 opcionales), 85 códigos de sanidad en 12 familias, 5 casos E2E (70 pasos, 10 clases
de 90 minutos, 42 imágenes) y 186 diapositivas de contenido en los mazos del webinar.

### Agregado
- **Validar antes de invertir.** `supuestos.csv` suma `criticidad`, `certeza`, `experimento`, `criterio`,
  `fecha_limite` y `evidencia`; guía de `pm-mandato-y-brief` §9 y plantilla `hipotesis-y-experimentos.md` (vista para la
  junta). Familia de sanidad **SUP**: SUP-01 supuesto crítico sin experimento o sin fecha límite, SUP-02 fecha límite
  vencida sin resultado, SUP-03 supuesto invalidado sin issue, cambio, riesgo o decisión que trate su efecto. Control
  **P-11** en `autorizar-proyecto`: condición si quedan supuestos críticos sin validar; aviso, con la D-### citada, si
  la junta los acepta con una decisión de nivel junta, ejecutivo o capa de negocio.
- **Evaluación de inversiones:** `pm-caso-de-negocio/scripts/inversion.py` calcula, desde un CSV de flujos por opción y
  concepto, VAN, TIR (con aviso de TIR ambigua), repago simple y descontado, VAN incremental contra la opción base,
  sensibilidad por concepto (±20 % por defecto) y de la tasa (±2 puntos) y punto de equilibrio por concepto; texto
  (ceros y enteros sin decimales, columna de concepto de hasta 60 caracteres) o `--json`.
- **Mapas estratégicos:** skill `pm-mapas-estrategicos` (agente pm-inicio, también en el límite de etapa de
  pm-planificacion) con mapas de Wardley (cadena de valor × evolución, construir, comprar, tercerizar o mercado,
  movimiento e inercia) y de recorrido del cliente (etapas, una acción por paso, puntos de contacto, emoción de −2 a +2
  con su fuente, dolores, oportunidades con clase Kano y carriles de service blueprint). `mapas.py`: `semilla` (desde la
  especificación BMAD, de solo lectura, o desde los artefactos del proyecto), `validar`, `render` (Mermaid
  `wardley-beta` y `journey`, texto OWM, HTML autocontenido y escapado, PNG con `mmdc`), `recorrido candidatos`,
  `vincular`, `controles`, `listar` y `tablero`. Si `mmdc` no puede iniciar el navegador, el aviso lo dice y da la
  solución (`TMPDIR` corto) en lugar de informar un error de sintaxis.
- **Tablero de mapas:** `mapas.py tablero [--mapas] [--insertar TABLERO.html] [--salida]` dibuja cada mapa válido en
  SVG propio, sin `mmdc` (Wardley con componentes coloreados por decisión, barra de inercia con su riesgo, movimientos
  y rótulos que no se pisan; recorrido con bandas por etapa, curva de emoción actual y esperada y el tratamiento de cada
  dolor), con los avisos MAP vigentes y la tabla «Vínculos citados» (dolor → requisito, riesgo, issue o supuesto;
  inercia → riesgo), ids enlazados y todo el texto escapado. Escribe `02-planificacion/visuales/tablero-mapas.html`
  (plantilla `tablero-mapas.html`) y, con `--insertar`, la sección opcional «Mapas estratégicos» del tablero de avance
  de `pm-visuales`, que reserva los marcadores `pm-mapas:inicio` y `pm-mapas:fin` y numera sus secciones según las
  que se muestran. `mapas.py controles` informa también el elemento de cada aviso.
- Familia de sanidad **MAP** (solo AVISO): MAP-00 mapa inválido, MAP-01 producto o commodity marcado construir sin
  decisión, MAP-02 inercia sin riesgo abierto, MAP-03 dolor sin tratamiento (requisito, historia del backlog, riesgo,
  issue, cambio, decisión, supuesto o revisión de calidad Q-###), MAP-04 posición o emoción sin evidencia, MAP-05 id
  roto.
- `bmad.py recorridos [--id UJ-n] [--json]` (campos del recorrido, FR que lo realizan, KPI SM-n y contrapesos) y
  `bmad.py capacidades [--json]` (capacidades → módulo → AD-n, decisiones diferidas y stack), de solo lectura.
- **Resumen de contexto derivado:** `estado.py contexto [--max 2000] [--corte] [--json]` resume `estado.json` y los
  registros con ids y sin texto libre: conteos abiertos (sin los registros de catálogo, como los estereotipos; las
  preferencias se cuentan como «por confirmar»), riesgos altos sin respuesta, riesgos con la revisión vencida (REG-09),
  issues abiertos, acciones vencidas, supuestos críticos sin validar, condiciones abiertas de puertas y próxima puerta,
  con "… y N más" para no pasar del tope. El hook de inicio lo agrega en cada inicio, reanudación, `/clear` y
  compactación, y declara que `estado.json` y los registros prevalecen sobre cualquier nota de memoria del cliente.
- **REG-09:** riesgo abierto con `fecha_revision` anterior al corte.
- **Autoridad y presupuesto de cambio al registrar** (PRINCE2; `registro.py`, no se omite con `--forzar`). Cuando una
  escritura deja aprobado un cambio con `costo` > 0 (`decision=aprobado` o `estado` aprobado, implementado o cerrado), o
  cambia `costo`, `cargo` o `decidido_por` de uno aprobado: si `decidido_por` no es la junta ni el ejecutivo (mismo
  criterio que CAM-04/CAM-05), se rechaza el cambio que supera `limite_autoridad_cambio`, el que carga
  `presupuesto-cambio` más allá de `presupuestos.cambio` (lo ya cargado + `costo`) y el que usa `reserva-gestion` o
  `plan-excepcion`, con mensaje bilingüe: dejar `estado=pendiente-decision` y escalar a pm-director. La junta o el
  ejecutivo aprueban sobre el límite por cambio, pero con `presupuesto-cambio` sin saldo deben indicar la fuente
  (`reserva-gestion`, `plan-excepcion`) o ampliar antes el presupuesto con `estado.py presupuesto cambio=… --por …`. Sin
  presupuesto de cambio fijado se registra con aviso. Consumo y reconocimiento de la junta salen de `esquema.py`
  (`consumo_cambios`, `es_junta`), los mismos que usa la sanidad CAM. Resuelve la decisión abierta de 2.2 (la prueba en
  vivo `controles` del 2026-10-18 había registrado `aprobado` con advertencia).
- Fechas explícitas para reproducir decisiones: `nuevo_proyecto.py --fecha`, `bmad.py linea-base --fecha` (valida el
  formato) y `estado.py set enfoque_entrega=… --por … [--nivel] [--fecha]`, que anota la decisión en `decisiones.csv`
  (sin `--por`, aviso). La guía de `pm-mandato-y-brief` §3 usa la escala 1–3 de la tabla de nueve criterios de
  `pm-knowledge` §4.4.4 (umbrales 13 y 22).
- **Generador del webinar** `scripts/webinar/generar.py` (con `pptx.js` y `pptxgenjs@4.0.1`): valida
  `docs/webinar/E2E-N/diapositivas.json` (tipos, imágenes citadas y su proporción, puntos, tablas, diapositivas por clase
  y términos del glosario) y escribe `E2E-N-diapositivas.pptx` (notas del orador, una sección por clase) y
  `E2E-N-diapositivas.html` (autocontenido, navegación por clase y diapositiva, claro/oscuro, notas plegables,
  imprimible, glosario con anclas). Portada del caso, portada de cada clase con objetivos y glosario; sin marca de
  empresa (recuadro «Logo IEEE» o `--logo`).
- **Documentos del webinar en HTML** `scripts/webinar/documentos.py` (biblioteca estándar; los diagramas con `mmdc`):
  convierte por caso la guía (`docs/guias/E2E-N-*.md`), el guion y el ejercicio en HTML autocontenido con la estética
  de las diapositivas y los escribe en `docs/webinar/E2E-N/`: `E2E-N-guia.html`, `E2E-N-guion-instructor.html` y
  `E2E-N-ejercicio.html`, una sola versión para asistentes e instructor que exige empezar por «Cómo funciona este
  ejercicio» y deja el «Ejemplo resuelto» en un bloque plegable rotulado «Ver el ejemplo resuelto (después de
  intentarlo)», que se despliega al imprimir y al seguir un enlace a un encabezado que está dentro; con `--todos`, además
  `docs/webinar/index.html` con todo el material de los cinco casos y para quién es cada archivo. Conversor de Markdown
  propio (encabezados con anclas como GitHub, listas anidadas y de tareas, tablas, código con botón «Copiar», citas,
  imágenes como data URI, `<details>`; el resto del HTML se escapa), Mermaid dibujado en SVG en línea con el código
  plegable (semilla fija: dos corridas dan archivos idénticos; `TMPDIR` corto para Chromium), enlaces relativos
  llevados al `.html` convertido o a GitHub, índice lateral, claro/oscuro, A4 imprimible y 390 px sin desplazamiento
  horizontal. Valida imágenes, enlaces y anclas, las secciones del ejercicio y los diagramas (error claro; con errores no
  escribe el caso). `--salida` arma una carpeta para repartir con las diapositivas copiadas; `docker/pm-pruebas.sh`
  suma el paso.
- **Entorno Docker opcional** (`docker/`): `Dockerfile` multietapa sobre `ubuntu:26.04` fijada por digest, usuario sin
  privilegios, Claude Code CLI 2.1.304 (`DISABLE_AUTOUPDATER=1`), Python 3.14 con dependencias fijadas por hash, Node 22
  con mermaid-cli 11.16.0, pptxgenjs 4.0.1 y npm 11.21.1 por lockfile, Chromium headless shell de Playwright, git,
  `tini`, etiquetas OCI y `HEALTHCHECK`; sin credenciales en capas. `compose.yaml` con los servicios `pm`, `pm-sin-red`
  y `pruebas` (raíz de solo lectura, `cap_drop: [ALL]`, `no-new-privileges`, límites de CPU, memoria y procesos) y
  comando `pm-pruebas` (validación del plugin, `validar_paquete`, `probar_paquete`, integración cruzada, compatibilidad
  con Python 3.9, recorridos E2E, `validar_mermaid --render` y mazos del webinar). Workflow
  `.github/workflows/docker.yml` que construye y prueba la imagen sin publicarla. Verificada el 2026-10-20 dentro del
  contenedor sin red, sin fallos (`probar_paquete.py` 216 OK con Python 3.14, recorridos 5/5, integración 60 OK con
  las salidas de los recorridos, Mermaid y mazos sin errores, flujo de usuario con proyecto montado); imagen de
  2,93 GB (726 MB comprimida).
- **Resumen ejecutivo comercial** (`docs/resumen-ejecutivo/`): PPTX y HTML autocontenido (claro/oscuro, imprimible,
  glosario con anclas) con arquitectura, componentes, ciclo de vida, controles permanentes y un caso E2E por
  diapositiva; `fuente/extraer.py` cuenta skills, agentes, hooks, registros, códigos de control y casos y corre las
  pruebas al regenerar.
- **Spot para LinkedIn** (`docs/resumen-ejecutivo/spot/`): MP4 de 54 s en 4:5 para directivos y PMO (la
  estrategia se ejecuta con proyectos; un control real del caso E2E-2; cierre con invitación a consultar, oferta de
  capacitación y transferencia y la mención de apoyo de PMI e IEEE Uruguay provista por el autor, solo como texto) con locución sintética (Kokoro-82M, Apache 2.0), música original sintetizada y subtítulos
  incrustados, versión sin voz, `.srt` y guion con tiempos.

### Cambiado
- `puertas.py verificar` muestra el código de cada control (`condición P-11 …`) y `--json` agrega `hallazgos`
  (`{severidad, id, mensaje}`) sin cambiar las listas existentes; la lista de control usa L-01…L-03. `puertas.py estado
  --markdown` muestra la preparación de la próxima puerta con los mismos códigos (bloqueos, condiciones y avisos) y
  `--json` agrega `hallazgos`.
- Control del contexto: `registro.py resumen` recorta cada lista de ids a 25 (`--max`) y agrega `<lista>_total`; el
  tablero de avance usa esos totales; salidas acotadas con muchos registros (presupuestos medidos en `docs/PRUEBAS.md`
  §2.2). `sanidad.py` agrupa en pantalla más de cinco hallazgos del mismo código («… y 1 hallazgo más», «… y N
  hallazgos más»).
- `sanidad.py` comprueba los módulos opcionales con `importlib.util.find_spec` y ya no carga `openpyxl` ni
  `python-docx` en cada corrida (ni en el hook de inicio).
- `paquete.py`: una copia congelada de `00-direccion/historial/` sin front matter toma su estado, versión y aprobador de
  `estado.json` (`copia_congelada`) o de la decisión «aprobado <clave> v<versión>» de `decisiones.csv`.
- `interesados.py reporte`: tabla de perfiles de comunicación en seis columnas (entra en 1.280 px) y «· N interesados»
  con su espacio.
- Mensaje claro («No existe el archivo / file not found») en `inversion.py`, `cpm.py`, `wbs.py`, `evm.py --csv`,
  `exportar.py` y `transcripcion.py` ante una entrada faltante; `probar_paquete.py --help` y `validar_paquete.py
  --help` muestran el uso en lugar de correr.
- `validar_paquete.py` analiza la sintaxis con un intérprete Python 3.9 si hay uno y, si no, busca las f-strings que solo
  compilan desde 3.12.
- `validar_mermaid.py`: lint de `wardley-beta` (nombres sin comillas con tildes, eñe o que empiezan por dígito; título
  y notas entre comillas; coordenadas fuera de 0–1) y de `journey` (puntaje entero de 1 a 5); el render detecta el SVG
  de "Syntax error" que `mmdc` produce sin terminar en error.
- Gráficos de las guías (`scripts/pruebas/guias_e2e/visuales.py`, matplotlib): `mapa_calor`, `barras_comparadas`,
  `consumo`, `lineas`, `gantt`, `estados`, `tarjetas` y `mapa_supuestos`, PNG de 1600 × 900, ejes de enteros cuando
  todos los valores lo son y leyenda que no se superpone con el título.
- Orquestador y agentes: `pm-mapas-estrategicos` en la tabla de enrutamiento (SU, IP) y en `pm-inicio` (paso 5b) y
  `pm-planificacion` (límite de etapa); `pm-adquisiciones` usa el mapa de Wardley si existe.
- `pm-caso-de-negocio` usa `inversion.py`; `pm-estado-proyecto` documenta `contexto`; `pm-sanidad` agrega SUP, MAP y
  REG-09.
- `pm-issues-cambios` (paso 7, escalamiento y guía §4–§4.1), `pm-direccion-decisiones` (guía, decisión ad hoc) y
  `pm-director` describen el control al registrar y el orden de la junta: ampliar el presupuesto y después aprobar el
  cambio. Guía E2E-2, paso 10: la aprobación de C-002 por la autoridad de cambio (15.000, sobre su límite de 10.000 y
  sin saldo) se rechaza al registrar y queda `pendiente-decision`; la sanidad del 19/2 da `0 ERROR · 1 AVISO · 1 INFO`
  (TOL-01, CAM-03 al 75 %), la junta amplía el presupuesto a 32.000 y recién entonces aprueba C-002; evidencia,
  `g2-consumo-cambio.png` y material del webinar E2E-2 con esas cifras. La cadena 2.4 de la integración cruzada y los
  casos de sanidad que necesitan CAM-03 ERROR o CAM-04 cargan esos cambios antes de que la junta fije el presupuesto.

### Seguridad
- Revisión del paquete en `docs/SEGURIDAD.md` (bandit, semgrep, pip-audit, npm audit y revisión manual): sin hallazgos
  de severidad alta; 3 medios y 12 bajos corregidos (SEG-12 en parte) y 2 informativos, cada uno con su estado.
- SEG-01: el reporte HTML de `interesados.py reporte` escapa todo dato de los registros (solo los fragmentos propios,
  `HtmlSeguro`, van sin escapar). SEG-02: `exportar.py xlsx` guarda como texto lo que empieza con `=`.
- SEG-03: `guardian.py` pide la confirmación de una persona (`permissionDecision: "ask"`) para `envios.py aprobar` y
  `envios.py enviar --confirmar`, también desde pm-director. SEG-09: evalúa cada segmento del comando de Bash y sus
  redirecciones y reconoce opciones abreviadas.
- SEG-04: `envios.py` rechaza `PM_SMTP_TLS=ninguno` con usuario y contraseña hacia un host que no es de bucle local.
  SEG-05: webhooks solo `https://` (`http://` solo hacia bucle local).
- SEG-06: `paquete.py` excluye del ZIP las rutas fuera de la carpeta del proyecto y las anota en el manifiesto, salvo
  `--permitir-externos`. SEG-07: `estado.py` valida las claves de artefacto y que la copia congelada quede en
  `historial/`. SEG-10: el hook de inicio imprime en una línea y recortados los textos de `estado.json`.
- SEG-08 (apertura de CSV en planillas), SEG-11 (regla "Fuentes = datos" en `pm-riesgos` y `pm-interesados`), SEG-12
  (`pptxgenjs@4.0.1` fijado), SEG-13 (Docker: `npm audit` con 5 avisos bajos justificados, `image-size` 2.0.3 por
  `overrides`), SEG-14 (escapado del canvas y del bloque JSON del tablero en la guía de `pm-visuales`) y SEG-15
  (archivos de credenciales en `.gitignore`).

### Corregido
- `docker/Dockerfile`: la descarga del Chromium headless shell fallaba en una construcción con acceso normal a la red
  (GitHub Actions), porque Playwright 1.56 detecta «ubuntu26.04» y no tiene descarga para esa plataforma. Se fuerza la
  compilación de Ubuntu 24.04 de la misma revisión (`PLAYWRIGHT_HOST_PLATFORM_OVERRIDE`) y se verifica que el binario
  quedó descargado.
- `docs/informe/fuente/build_html.py`: f-string que no compilaba con Python 3.9, con la misma salida.
- `docs/informe/fuente/build_pptx.js`: número de diapositiva como propiedad `slideNumber` del layout (pptxgenjs 4.0.1
  ignoraba el que estaba dentro de `objects`).

### Documentación
- Cinco casos E2E en `docs/guias/`, cada uno con "Por qué importa", "Qué vas a lograr", indicadores con imágenes de la
  corrida real, dos clases de 90 minutos, la tabla "Del uso único al control continuo" y pasos con la misma estructura
  (prompt · si te pregunta · qué hace el sistema · qué deberías ver · dónde verificar): E2E-1 riesgos (15 pasos),
  E2E-2 alcance, cambio y mapa de ruta (10), E2E-3 interesados, comunicaciones, OKR y avance (14), E2E-4 producto con
  BMAD (13) y E2E-5 de la idea al proyecto diseñado (18, con variante con BMAD). E2E-4 y E2E-5 (variantes a y b)
  terminan con la representación gráfica de sus mapas: el tablero del Release 1 con su sección de mapas
  (`g4-tablero.png`, recorte 16:9 `g4-tablero-mapas-169.png`) y los tableros de mapas `g5-tablero-mapas.png`
  (recorte `g5-tablero-mapas-169.png`) y `g5-tablero-mapas-bmad.png`, con una diapositiva de imagen en cada mazo.
- Material del webinar en `docs/webinar/E2E-1…E2E-5/`: guion del instructor (agenda minuto a minuto, mensajes clave,
  preguntas con respuesta esperada, plan B y cómo conducir el ejercicio), ejercicio y contenido de diapositivas: 186
  diapositivas de contenido y 124 términos de glosario en los cinco mazos. El ejercicio es una sola hoja que se hace
  sin abrir la guía: «Cómo funciona este ejercicio» (para qué sirve, cuándo se hace, qué se completa con un proyecto
  propio o con el escenario del caso, cómo se autoevalúa), «Lo que necesitás saber» (escenario, datos de partida y
  conceptos mínimos), la hoja de trabajo con sus criterios, preguntas para ir más allá y un ejemplo resuelto con el
  escenario del caso en el que cada dato cita el paso de la guía de donde sale.
- `docs/SEGURIDAD.md`, `docs/DOCKER.md`, `docs/PRUEBAS.md` §2.2 (presupuestos de contexto con y
  sin pm-method y con BMAD instalado), `docs/INSTALACION.md` §9.1 (contexto y memoria) y la solución de problemas de
  `mmdc` con un `TMPDIR` largo.
- Cifras actualizadas y sin historia de construcción en README, índice, arquitectura, catálogo, sanidad, puertas,
  pruebas y guías.
- Informe 2 en `docs/informe/` (`informe-2-ecosistema-pm-method-v2.3.html` y `.pptx`, reemplazan a los de 2.2):
  sección «Capacidades de gestión» (supuestos y P-11, `inversion.py`, mapas estratégicos, contexto de sesión), seguridad,
  Docker, integración cruzada, Python 3.9, guías E2E con sus indicadores, material de formación, pruebas en vivo del
  2026-10-20 e historial de versiones como sección aparte; las cifras del texto propio las cuenta `fuente/extraer.py` en
  el repositorio (marcadores `{{clave}}`); HTML con tema claro u oscuro; recuadro «Logo IEEE» en lugar de marca.

### Pruebas
- `probar_paquete.py`: **223 OK · 0 FALLO** con Python 3.13; **222 OK · 0 FALLO** con Python 3.9 (sin `matplotlib` se
  omite una comprobación de visuales). Casos nuevos: J2 (autoridad y presupuesto de cambio al registrar), K (supuestos y P-11), L (esquema de las diapositivas del webinar), L2 (documentos del webinar en HTML: Markdown completo, escapado, ejercicio en una sola versión con el ejemplo resuelto plegable y errores de imagen, enlace y Mermaid),
  M (mapas, tablero de mapas, REG-09 y `linea-base --fecha`), N (endurecimiento SEG-03…SEG-10 y control del contexto), P (salidas de los
  scripts: contexto, sanidad, puertas, paquete, mapas, inversión y reporte de interesados), S (SEG-01 y SEG-02),
  X (integración cruzada) e Y (`--help` de 30 scripts y 17 entradas faltantes sin traza de Python).
- Suite de integración cruzada `scripts/pruebas/integracion/correr.py`: seis cadenas sobre un mismo proyecto (BMAD →
  especificación → backlog → WBS → CPM → EVM → OKR → sanidad → puertas; acta, Jira y BMAD → riesgos → presupuestos y
  cambios → tablero; interesados ↔ RACI ↔ OKR ↔ envíos; mapas → vínculos → MAP → inversión; exportación y paquete;
  recorridos E2E → webinar), donde cada eslabón toma el dato de la salida del anterior: **61 OK · 0 FALLO en 24
  eslabones**.
- Recorridos E2E (`guias_e2e/correr.py`): 5/5 con los scripts reales, evidencia idéntica en dos corridas seguidas (la
  creación del proyecto también lleva fecha fija: `comun.base_su(repo, fecha)`).
- `validar_mermaid.py --render`: 127 bloques, 0 errores. `generar.py --todos --validar`: 5/5 mazos sin errores.
- En vivo con Claude Code real (2026-10-20): enrutamiento tras el cambio del hook de inicio 14/14
  (`docs/evaluacion/resultados/2026-10-20-enrutamiento-contexto-v2.3.md`); frases 95–102 de la skill de mapas 8/8
  (`…/2026-10-20-enrutamiento-mapas-v2.3.md`); escenario `suite.py integracion` con las 29 skills de BMAD 6.12.4
  instaladas 12/12, primera llamada de 45.505 tokens de entrada y máximo de 64.177
  (`…/2026-10-20-integracion-contexto-v2.3.md`); escenario `suite.py controles` 7/7: `registro.py` rechazó la
  aprobación de la autoridad de cambio sin saldo y el modelo dejó el cambio `pendiente-decision` y pidió la decisión a
  la junta (`…/2026-10-20-controles-v2.3.md`). `vivo.py` mide los tokens de entrada de cada llamada.
- 102 frases en `docs/evaluacion/frases-enrutamiento.tsv`.

## 2.2.0 · 2026-10-17 — maestro de interesados, capa de canales y OKR

Versión que convierte el registro de interesados en un maestro con matriz, RACI ligada al plan y perfil de
comunicación por persona, agrega una capa propia para enviar comunicados con aprobación y registro, y amplía OKR con
tipos de KR, check-ins y salud. Retrocompatible: los proyectos 2.1 siguen funcionando sin cambios (migración no
destructiva, sin dependencias nuevas, nada se escribe en BMAD).

### Interesados
- Skill nueva **`pm-interesados`** (agente `pm-inicio`): dueña de `stakeholders.csv`, `estereotipos.csv`,
  `preferencias.csv` y `raci.csv`, y de los artefactos `analisis-stakeholders`, `matriz-raci`,
  `plan-compromiso-stakeholders` (plantillas movidas desde `pm-organizacion-roles`) y `reporte-interesados`. Plantilla
  nueva `entrevista-interesado.md`; guía en `references/guia.md` §1–§12.
- `interesados.py --proyecto G [--medio alto|bajo]` con los subcomandos `matriz`, `estereotipos`, `proponer`,
  `confirmar`, `rechazar`, `perfil`, `raci`, `vinculos`, `integridad`, `reporte` y `plan-envio`.
- **Matriz poder/interés** con estrategia por cuadrante (gestionar de cerca, mantener satisfecho, mantener informado,
  monitorear) y valores de comunicación por defecto; "medio" se ubica del lado alto y se marca como frontera
  (`--medio bajo` lo invierte).
- **RACI** sobre elementos con fuente verificable: paquetes y actividades de la WBS, requisitos, épicas e historias por
  la fachada `especificacion.py` o el backlog, KR y objetivos de `okr.csv`, decisiones de `decisiones.csv`; un solo A
  por elemento.
- **Estereotipos** (6 semilla) y **preferencias** con procedencia (declarado, observado, inferido), estado (propuesta,
  confirmada, rechazada, vencida), cita, fuente y vigencia (defecto 180 días). `proponer` lee entrevistas, actas o
  transcripciones y solo analiza oraciones en primera persona; una persona confirma o rechaza cada propuesta.
- **Perfil de comunicación** resuelto con precedencia cuadrante → idioma del proyecto → estereotipo → matriz de
  comunicaciones → preferencias confirmadas y vigentes; aviso ante conflicto entre preferencia y matriz.
- **Reporte HTML** autocontenido (claro/oscuro, móvil): matriz SVG 2×2, estrategias, RACI, perfiles con procedencia,
  estereotipos, vínculos con OKR, especificación y WBS, envíos e integridad; valoraciones solo con `--restringido`.
- Privacidad: el perfil solo adapta comunicaciones; no se infieren emociones, personalidad, salud ni datos sensibles,
  no se analiza audio ni tono, no se usan tipologías propietarias. La guía §10 cita las normas consultadas (AI Act,
  RGPD, Ley 18.331) sin constituir asesoramiento jurídico.

### Capa de canales
- Nuevo `skills/pm-integraciones/scripts/envios.py` con `nuevo`, `estado`, `aprobar`, `enviar`, `preparar-mcp`,
  `registrar`, `historial` y `verificar`.
- Modos: `smtp`, `slack-webhook`, `teams-webhook` (flujo de Workflows con tarjeta adaptable, límite 28 KB), `eml`
  (archivos con `X-Unsent: 1`) y MCP conectados (`preparar-mcp` → vista previa y confirmación → `registrar --modo mcp`).
- Mensajes en `03-control/comunicaciones/<fecha>-<tema>/` con frontmatter y `plan-envio.csv`, generados desde
  `interesados.py plan-envio` con el perfil de cada destinatario.
- Reglas: sin `--confirmar` es simulación; solo se envían mensajes aprobados (`aprobar --por`); los destinos se leen
  siempre del maestro al enviar; el reenvío solo va a quien falta; cada envío queda en `envios.csv` (EN-###) y en
  `diario.md`; código de salida 2 si hubo fallos.
- Configuración solo por variables de entorno (`PM_SMTP_*`, `PM_SLACK_WEBHOOK_URL`, `PM_TEAMS_WEBHOOK_URL`), nunca en
  archivos. Solo biblioteca estándar (`smtplib`, `email`, `urllib`).
- `estado.json.integraciones.correo` (`ninguno|smtp|gmail|outlook|eml`).

### OKR
- `okr.py` v2.2, retrocompatible (con un `okr.csv` de 2.1 la salida es idéntica). Columnas opcionales `tipo_kr`
  (`de-a`, `mantener-sobre`, `mantener-bajo`, `binario`, `hito`), `compromiso` (aspiracional o comprometido), `peso`,
  `padre_id`, `nivel`, `ciclo`, `fecha_inicio`, `estado`, `ref_externa`; iniciativas `IN-n` ligadas a un KR y a una
  épica, historia o paquete.
- Puntuación por tipo, objetivo como promedio ponderado; semáforo aspiracional 0,7/0,4 y comprometido 1,0/0,7; salud
  (en camino, en riesgo, desviado) contra el avance esperado lineal; confianza 1–10 en tres bandas.
- **Check-ins** en `00-direccion/okr_checkins.csv` (solo se agregan): `--checkin KR --valor V [--confianza N] [--nota]
  [--autor] [--fecha] [--fuente]`; el valor actual es el último check-in hasta el corte.
- Sincronización: `--propuesta-sync tability|perdoo` y `--marcar-publicado KR@FECHA --destino … --ref …`;
  `estado.json.integraciones.okr` admite `perdoo`. Servidores MCP oficiales de Tability y Perdoo verificados el
  17/10/2026; plan comercial requerido: [verificar].
- Avisos nuevos: verbo de actividad en un KR, responsable fuera del maestro, tipo/compromiso/peso inválidos,
  iniciativa sin KR o sin vínculo, KR de hito sin iniciativas, check-in de KR inexistente, todos los aspiracionales en
  1,0 al cierre. Limitación: las iniciativas no guardan historia.

### Identificación de riesgos desde cuatro fuentes
- Nuevo `skills/pm-riesgos/scripts/riesgos.py candidatos [--fuentes bmad,transcripciones,tracker,artefactos]
  [--transcripcion F…] [--instantanea F] [--desde] [--salida] [--json] [--fecha]`: destila **riesgos candidatos** (con
  clase riesgo, supuesto, pregunta o issue, amenaza u oportunidad, cita y ubicación) de BMAD (descubrimiento, brief, PRD,
  arquitectura, UX; solo lectura vía `pm-bmad-puente`), de transcripciones y actas, de una instantánea fechada de Jira u
  otro tracker (lo ocurrido se propone como issue con su riesgo derivado) y, sin BMAD, de los artefactos del proyecto
  (mandato, brief, requisitos, `supuestos.csv` abiertos, `lecciones.csv`). Marca posibles duplicados o relaciones con
  riesgos ya registrados. Escribe solo el borrador `03-control/reportes/<fecha>-candidatos-riesgo.md`: nada entra al
  registro sin formularse y evaluarse.
- `bmad.py inventario` (v6) suma la clave `descubrimiento` (brainstorming, PRFAQ, investigación) [verificar por versión].
- `pm-riesgos` paso 3 y guía §2 (tabla de fuentes) y §8; `pm-integraciones` guía §3: columnas opcionales del tracker
  `prioridad`, `etiquetas`, `vinculo`, `descripcion`.
- `interesados.py proponer` ignora menciones negadas («por Slack, no por correo» propone solo Slack).

### Integridad y sanidad
- `esquema.py`: 4 registros opcionales que se crean al primer uso (estereotipos ET-, preferencias PF-, raci RC-,
  envios EN-; 13 registros en total), claves foráneas (`refs`), unicidad (`unico`: elemento + stakeholder_id en raci)
  y `uno_por` (un solo A por elemento). `stakeholders.csv` suma al final `estereotipo`, `correo` y `usuario_chat`.
- `registro.py agregar|actualizar` valida esas reglas (`--forzar` registra igual y sanidad lo detecta).
- `sanidad.py`: familia nueva **STK-00…STK-11** (ejecuta `interesados.py integridad` cuando existe alguno de los
  registros nuevos); REG-08 incluye los prefijos ET, PF, RC y EN.
- `puertas.py` en `autorizar-proyecto`: avisos P-09 (interesados vacío o sin poder/interés) y P-10 (sin `raci.csv` ni
  artefacto `matriz-raci`); no bloquean.
- `hooks/guardian.py` protege `estereotipos.csv`, `preferencias.csv`, `raci.csv` y `envios.csv`; `interesados.py` y
  `envios.py` figuran entre los scripts permitidos.

### Controles permanentes
Controles que antes se hacían a mano, tarde o nunca (por falta de estándar, por trabajo manual o por volumen) y que
ahora detectan `sanidad.py` y `puertas.py` en cada corrida. Todos son AVISO o INFO salvo donde se indica.
- **Presupuestos de la junta** en `estado.json` → `presupuestos` (`cambio`, `riesgo`, `gestion`,
  `limite_autoridad_cambio`; montos numéricos sin moneda ni separador de miles: `10.000` se rechaza): `estado.py presupuesto clave=monto …
  [--por "Rol: Nombre"] [--fecha AAAA-MM-DD]`; con `--por` queda en `decisiones.csv`; `estado.py resumen` los muestra.
  Reservado a pm-director (`hooks/guardian.py`).
- `cambios.csv` suma las columnas **`costo`** (numérica) y **`cargo`** (`presupuesto-cambio`, `reserva-riesgo`,
  `reserva-gestion`, `plan-excepcion`, `sin-costo`).
- Familia **CAM** (cambios aprobados, implementados o cerrados, o con `decision=aprobado`): CAM-01 impacto de costo sin
  `costo` ni `cargo`, o costo sin cargo · CAM-02 cargo a la reserva de riesgo sin citar un R-### · CAM-03 consumo del
  presupuesto de cambio y de la reserva de riesgo (INFO < 80 %, AVISO ≥ 80 %, **ERROR > 100 %**, que bloquea puertas;
  AVISO si se cargó sin presupuesto fijado) · CAM-04 costo sobre `limite_autoridad_cambio` no decidido por la junta o el
  ejecutivo · CAM-05 reserva de gestión no liberada por la junta.
- Familia **QUA** (calidad a volumen): QUA-01 elemento terminado de `02-planificacion/backlog.csv` sin revisión
  completada y aprobada en `calidad.csv` que lo cite (id completo o clave corta `N-M`) · QUA-02 revisión planificada o en
  curso con `fecha_prevista` vencida al corte · QUA-03 revisión rechazada sin issue, acción o cambio que cite su Q-###.
- **EVM vigilado**: `evm.py … --proyecto G --guardar [--corte AAAA-MM-DD]` guarda `03-control/reportes/evm-<corte>.json`.
  Familia **TOL**: TOL-01 (AVISO) el último corte pronostica excepción y no hay excepción abierta ni puerta
  `autorizar-plan-excepcion` posterior · TOL-02 (INFO) semáforo en ámbar · TOL-03 (INFO) etapa de entrega sin corte
  guardado o con el último de más de 31 días.
- **STK-12** (compromiso sostenido; `interesados.py integridad --corte` y sanidad): para los cuadrantes gestionar de
  cerca, mantener satisfecho y mantener informado, compara el último envío `enviado` de cada interesado en
  `envios.csv` (reuniones y llamadas se registran como envío manual) con la frecuencia de su perfil; tolerancia 1,5 ×
  el período. Frecuencia nueva **`trimestral`** (92 días), también reconocida por `interesados.py proponer`.
- **Condiciones formales de puertas**: con `--decision condicionado`, los hallazgos de tipo condición de la verificación
  (p. ej. CONCERNS del gate de preparación de BMAD, P-04, P-06) pasan a condiciones de la puerta. Las condiciones abiertas
  cuentan también para decisiones `aprobado` con `--condiciones` (p. ej. `decision-ad-hoc`) en EST-12, `puertas.py
  estado` y `estado.py resumen`. Control nuevo **G-01** en `puertas.py verificar` de `autorizar-proyecto`,
  `autorizar-etapa` y `autorizar-plan-excepcion` (condición) y de `autorizar-cierre` (**bloqueo**) mientras haya
  condiciones abiertas de puertas anteriores. `estado.py cumplir-condiciones <tipo> [--fecha] [--por] [--nota]` las cierra,
  guarda quién verificó y la nota, lo anota en `decisiones.csv` (con `--por`) y falla si no hay condiciones abiertas.
- **P-04** (`autorizar-proyecto`): condición si los criterios de éxito están solo en OKR (el business case no menciona
  beneficios —B-n, SM-n o la palabra «beneficio»— y no hay artefacto `enfoque-beneficios*`); aviso "sin enfoque de
  beneficios" si el business case los menciona pero no hay enfoque.
- `sanidad.py --corte AAAA-MM-DD`: fecha de corte de los controles con vencimiento (REG-07, QUA-02, TOL, STK-12), para
  informes reproducibles.
- `puertas.py preparacion-bmad --fecha` fecha también la decisión anotada en `decisiones.csv`.
- `riesgos.py candidatos` excluye de la fuente "artefactos" el enfoque de riesgo y la evaluación de probabilidad e
  impacto (son método, no riesgos).
- `SPEC.md` §1.10.3 lista las claves `descripcion-producto-<id>` y `tolerancias-y-autoridad`.

### Skills y agentes
- Descripciones nuevas o cambiadas: `pm-interesados` (nueva), `pm-organizacion-roles` (ahora solo estructura de
  gestión, roles y team charter), `pm-comunicacion-stakeholders` (matriz, mensajes por audiencia y envío),
  `pm-integraciones` (capa de canales) y `pm-okr` (tipos de KR, check-ins, salud, Tability o Perdoo).
- `pm-reuniones`: paso 7, distribución del acta por la capa de canales; paso 7b, preferencias declaradas con
  `interesados.py proponer`.
- `pm-orquestador`: fila de enrutamiento para interesados, matriz, RACI, estereotipos y preferencias; "enviar a
  interesados" en la fila de comunicación; `pm-interesados` en SU.
- Agentes: rutas de `interesados.py` y `envios.py`; `pm-inicio` pasos 4b y 13b; `pm-control` pasos 4 (preferencias) y
  10 (check-ins de OKR, comunicación personalizada y envío).
- `pm-registros/templates/guia-registros.md`: secciones 7.1–7.4 de los registros nuevos.
- Controles permanentes en skills y agentes (sin cambiar descripciones ni frontmatter): `pm-sanidad` (familias CAM, QUA,
  TOL y STK-12, `--corte`, dueños), `pm-issues-cambios` guía §4.1 (presupuesto de cambio, `costo` y `cargo`),
  `pm-calidad` guía §8.1 (calidad a volumen), `pm-progreso-reportes` guía §3 y §8 (`evm.py --guardar`, TOL),
  `pm-costos-presupuesto` guía §3 (presupuestos en `estado.json`), `pm-interesados` guía §7 (STK-12),
  `pm-direccion-decisiones` guía (presupuestos y condiciones), `guia-registros.md` (columnas `costo` y `cargo`);
  `pm-control` paso 8 (corte de EVM guardado y sanidad con `--corte`) y `pm-director` modo B paso 6 (`presupuesto`,
  `cumplir-condiciones`).
- 38 skills (32 invocables por el modelo; listado de 6.582 caracteres), 6 agentes, 3 hooks; versión 2.2.0 en
  `plugin.json`, `compatibilidad.json`, `esquema.py` y todos los SKILL.md.

### Pruebas y guías
- `probar_paquete.py`: 80 → **138** pruebas. Caso H (33 comprobaciones): maestro de interesados (matriz, RACI,
  estereotipos, preferencias), capa de canales con SMTP y webhooks de Slack y Teams contra servidores locales en
  127.0.0.1, y OKR v2.2. Caso I (9): candidatos de riesgo desde las cuatro fuentes, la negación en `proponer`, el enfoque
  de riesgo excluido como fuente y la frecuencia trimestral. Caso J nuevo (16): controles permanentes (presupuestos y
  hook, `costo` numérico, CAM-01…04, bloqueo de puerta por CAM-03, P-04, condiciones formales, G-01 y
  `cumplir-condiciones`, QUA-01…03, `evm.py --guardar` y TOL-01, STK-12).
- Las cuatro guías E2E muestran los controles permanentes, cada una con la sección "Controles permanentes que muestra
  esta guía" (problema habitual · control · código · paso):
  - **E2E-1** (13 pasos, 90–115 min): candidatos de BMAD, de la transcripción y de Jira; paso 13 sin BMAD; presupuesto de
    riesgo fijado por la junta y consumo de la reserva vigilado (CAM-02, CAM-03), P-04.
  - **E2E-2** (10 pasos, 80–110 min): autoridad de cambio con presupuesto y límite, cambio de alcance con costo y cargo,
    EVM ágil guardado, calidad de lo terminado (QUA-01) y paso 10 nuevo de gestión por excepción (CAM-03 ERROR, CAM-04,
    TOL-01, informe y plan de excepción, condición de la junta cumplida).
  - **E2E-3** (13 pasos, 100–130 min): maestro de interesados, preferencias, RACI, enfoque de beneficios con OKR que lo
    complementan, envío por canales y paso 13 nuevo de compromiso sostenido (STK-12, acción correctiva y reevaluación).
  - **E2E-4** (15 pasos, 3–4 h): condición formal desde el CONCERNS de BMAD (EST-12, G-01, `cumplir-condiciones`),
    cambio con presupuesto, calidad a volumen (QUA-01, QUA-02), cierre con traspaso y paso 15 posterior al proyecto
    (primera revisión de beneficios).
  - Imágenes `g3-interesados-matriz.png` y `g3-interesados-raci-perfiles.png`; `guias_e2e/correr.py` 4/4 OK; `base.py`
    sanea la marca de tiempo del índice en la evidencia.
- `validar_mermaid.py --render`: 127 bloques, 0 errores; `validar_paquete.py`: OK; `claude plugin validate .`: pasa.

### Pendientes
- Pruebas en vivo de enrutamiento con Claude Code real (18/10/2026): **14/14** en las frases de las skills cuya
  descripción cambió (`docs/evaluacion/resultados/2026-10-18-enrutamiento-v2.2.md`); guardarraíles 4/4, idioma 3/3 y
  escenario nuevo `controles` 6/6 (`…/2026-10-18-suite-v2.2.md`, USD 0,97). Decisión abierta: con el presupuesto de
  cambio agotado, el modelo registra `aprobado` si el usuario lo pide (advirtiendo y anotando la ratificación pendiente)
  en lugar de `pendiente-decision`.
- Terminología: batería en vivo de 28 frases con vocabulario de PRINCE2 en español, PMBOK en español y uso habitual
  (ids 67–94 de `frases-enrutamiento.tsv`): 27/28; se agregaron "incidencia" y "registro de incidentes" a la
  descripción de `pm-issues-cambios` y "incidencia" y "comité de dirección" a la tabla del orquestador; documento nuevo
  `docs/TERMINOLOGIA.md` (`…/2026-10-18-terminologia-v2.2.md`).
- Convivencia con BMAD: con las 29 skills de BMAD 6.12.4 (módulo bmm) instaladas en el mismo proyecto, 25/25 frases
  vecinas llegaron a la skill de pm-method (`…/2026-10-18-enrutamiento-con-bmad-v2.2.md`); `suite.py --skills-extra`
  copia las skills de otra instalación al proyecto de prueba.
- `scripts/pruebas_vivo/escenarios.py`: escenario `controles` (presupuesto de cambio excedido y calidad a volumen en
  una conversación real); `suite.py controles` y dentro del grupo `robustez`.
- Plan comercial que exigen los servidores MCP de Tability y Perdoo: [verificar].
- Exposición de objetivos por los MCP oficiales de otras herramientas de OKR: [verificar].
- Alcance exacto de la exclusión de texto escrito en el art. 5(1)(f) del AI Act (solo fuentes secundarias): [verificar].

## 2.1.0 · 2026-10-17 — madurez para uso real

Versión surgida de pruebas en vivo con Claude Code real (enrutamiento de 75 frases y siete escenarios de orquestación)
y de una revisión de cada script contra una instalación real de BMAD 6.12.4.

### Guías de prueba para el usuario
- `docs/guias/`: cuatro recorridos de punta a punta escritos como prompts del usuario, con respuestas a las preguntas
  del sistema, resultado esperado, dónde verificar, reporte de ejemplo y gráficos (Mermaid y capturas del tablero):
  E2E-1 riesgos, E2E-2 alcance/cambio/esfuerzo/priorización/roadmap, E2E-3 interesados/comunicaciones/OKR/avance,
  E2E-4 producto de la idea al producto con BMAD.
- `scripts/pruebas/guias_e2e/`: los recorridos con los scripts reales sobre el fixture BMAD 6.12.4 (≈ 1 min, sin
  tokens); evidencia en `docs/guias/evidencia/`.
- `CASOS-DE-USO`, `CASO-MAESTRO` y `CASOS-DE-USO-INTEGRACIONES`: cada caso con el prompt del usuario, sus respuestas,
  entradas (qué aporta el usuario y cómo) y salidas (qué queda y dónde verificarlo); los comandos quedan como
  referencia de lo que ejecuta el sistema.
- `pm-visuales` guía §3: documentado el formato de `decisiones_pendientes` del tablero (`{id, texto, fecha_limite}`).

### Diagramas
- Corregidos los bloques Mermaid que GitHub no renderizaba (`;` en mensajes de secuencia, paréntesis en etiquetas de
  arista sin comillas, marcadores `{{…}}` en fechas de gantt, números de xychart/quadrant e ids de nodo: ahora valores
  de ejemplo con un comentario `%%` que indica qué marcador reemplazan).
- Legibilidad: diagramas de arquitectura (README, ARQUITECTURA), sincronización, verificación y orquestación de puertas,
  flujo de orquestación y mapa del caso maestro rediseñados verticales (≤ 900 px de ancho natural: letra más grande en
  GitHub) y sin etiquetas superpuestas ni texto cortado.
- README reorganizado: justificación, beneficios por perfil con evidencia, y arquitectura, ciclo de vida, ciclo
  integrado PRINCE2 + BMAD y verificación de puertas como diagramas al comienzo.
- `INSTALACION.md` §0.7 nueva: dónde y cómo configurar las credenciales (suscripción o `ANTHROPIC_API_KEY` en Claude
  Code, `~/.hermes/.env` en Hermes, tokens de MCP), precedencia y reglas de seguridad. §0.8 nueva: Orca (opcional).
- Nuevo `scripts/validar_mermaid.py`: lint estático de esos errores + render real con mmdc (122 bloques, 0 errores).

### Guardarraíles y roles
- `hooks/guardian.py` reescrito: además de Write/Edit, bloquea escrituras directas por **Bash** (`sed -i`, `>`/`>>`,
  `tee`, `cp`/`mv`/`rm` hacia destinos protegidos, `open(...,'w')`, `json.dump`, `to_csv`) sobre `estado.json`,
  registros CSV, derivados de la especificación, `00-direccion/historial/` e instantáneas existentes de
  `03-control/fuentes/`. Ya no da falso positivo con `2>&1`.
- Separación de roles en el hook: desde subagentes pm-* (salvo pm-director) se niegan `estado.py puerta|rol|tolerancia|
  agil|umbrales-riesgo|cumplir-condiciones`, `limite-etapa --excepcion`, `set --forzar` y `aprobar` sin
  `--nivel gestor|product-owner|equipo`. El subcomando se identifica por análisis del comando, no por palabras sueltas.
- `estado.py set` ya no cambia `fase` ni `proceso_actual` (salvo `--forzar --por`, que queda en `decisiones.csv`).
- Nuevo nivel de decisión `ejecutivo`.
- Agentes: bloque "Reglas operativas comunes (v2.1)" (rutas de scripts, escrituras solo por script, idioma, lectura
  por secciones, no ofrecer desactivar hooks) y "Reservado a pm-director" en los agentes de fase.
- `pm-director` congela PID y business case v1.0 también cuando `autorizar-proyecto` es condicionado.

### Enrutamiento e idioma
- Hook `SessionStart`: ya no envía todo al orquestador; nombra la skill dueña cuando el pedido nombra un producto,
  imprime la ruta absoluta de los scripts, la regla de idioma y la regla de no esquivar hooks.
- Descripciones ajustadas (pm-reuniones, pm-calidad, pm-knowledge, pm-orquestador, pm-sanidad, pm-bmad-puente).
- Regla de idioma unificada en las 37 skills: responder en el idioma del usuario; artefactos en `estado.json.idioma`.
- Resultado en vivo: enrutamiento 59/60 (antes 82 %); idioma 3/3; guardarraíles 4/4.

### Scripts
- Rutas de scripts expandibles: `${CLAUDE_SKILL_DIR}/../pm-X/scripts/` en skills y `${CLAUDE_PLUGIN_ROOT}/skills/…` en
  agentes (antes un marcador que obligaba a buscar con `find`).
- `estado.py`: `resumen`; `puerta autorizar-etapa` conserva las tolerancias de etapa y acepta `--inicio` y `--tol`;
  `integracion` avisa ante valores desconocidos; la versión del paquete se actualiza al guardar.
- `bmad.py`: raíz de BMAD guardada **relativa** al proyecto; si una raíz absoluta heredada no contiene al proyecto,
  avisa y usa el BMAD del propio repositorio; descripción del backlog = párrafo completo de la historia; numeración
  del documento de traspaso.
- `cpm.py`: tareas resumen de solo hitos con fin = inicio en el MSPDI; título del Gantt con `--titulo`.
- `evm.py`: `VAC_pct` con el signo de VAC y nuevo `sobrecosto_pct`; `base_semaforo` por dimensión; aviso si una
  tolerancia no está en %.
- `okr.py`: acepta vínculos `SM-C<n>` (métricas de contrapeso de BMAD 6.12).
- `exportar.py xlsx`: rechaza entradas que no son CSV.
- `sanidad.py`: sin falsos INS-04 por los clones de `marketplaces/` o versiones viejas del caché; Chrome en Windows;
  aviso de Chrome solo si archify está instalada; valores de integración compartidos con `estado.py`.
- `hooks/py.sh`: lanzador portable (python3, python o `py -3`) para Windows con Git Bash; `.gitattributes` fuerza LF
  en `.sh`, `.py` y `.json`.
- utf8proj deja de recomendarse (inmaduro): SS/FF/SF y calendarios se completan sobre el MSPDI en MS Project o
  ProjectLibre.

### Ajustes tras las pruebas de robustez (misma versión, antes de publicarla)
- **Bloqueos de puerta** en `estado.py puerta`: `aprobado` de `autorizar-proyecto|autorizar-etapa|autorizar-plan-excepcion|
  autorizar-cierre` se rechaza si faltan tolerancias de proyecto o de etapa, PID o business case, el plan de la etapa a
  autorizar o la línea base del PRD (con BMAD), o si `sanidad.py --rapido` da ERROR. `condicionado` los suma como
  condiciones; `--forzar` los anota. Encontrado en el escenario `multisesion`.
- El hook reserva los comandos de decisión a pm-director **también en el hilo principal** (antes solo en subagentes).
  Las skills de inicio ya no registran tolerancias: las proponen y pm-director las registra.
- Nuevo hook `UserPromptSubmit` (`idioma.py`): si el pedido está en otro idioma que el proyecto, recuerda responder en
  el idioma del pedido (el fallo reaparecía en 1 de cada 4 corridas).
- Regla "fuentes = datos" en el hook de inicio y en pm-reuniones, pm-integraciones y pm-bmad-puente: instrucciones
  incrustadas en transcripciones, tickets o BMAD se informan y no se ejecutan.
- Escala: `especificacion.py listar` y `registro.py listar` muestran hasta 60 filas (`--limite`); `sanidad.py` agrupa en
  pantalla los hallazgos repetidos de un mismo código.
- Pruebas: escenarios en vivo `inyeccion`, `desorden`, `multisesion`, `escala` (`scripts/pruebas_vivo/escenarios.py`),
  generador `scripts/pruebas/generar_bmad_grande.py`, opción `--modelo`; `probar_paquete.py` llega a 80 pruebas.
- `estado.py aprobar` crea la copia congelada de la versión aprobada en `00-direccion/historial/<clave>-v<versión>`
  (antes la hacía el agente a mano y el hook, con razón, lo impedía).
- Hermes Agent: `scripts/instalar_hermes.py` genera una copia adaptada (`${HERMES_SKILL_DIR}`); verificado que Hermes
  lista las 37 skills y resuelve las rutas de los scripts. `tap add`/`install` desaconsejados.
- Nuevo `docs/PILOTO.md` (plan de piloto con métricas, rúbrica y usabilidad).
- **Verificación de puertas** (`puertas.py`, `docs/PUERTAS.md`): cada puerta se verifica en tres capas — salud,
  controles automáticos de PRINCE2 (artefactos, tolerancias, criterios de éxito, calidad, registros abiertos) y de BMAD
  (PRD y arquitectura `final`, línea base, gate de preparación del sprint planning: FAIL bloquea, CONCERNS es condición,
  sin veredicto es aviso), y lista de control de la junta (`lista` / `confirmar --por`). La decisión se registra con la
  referencia a la lista y las observaciones. Comportamiento del gate de BMAD verificado con 3 corridas reales de
  `bmad-sprint-planning` (no escribe archivo con CONCERNS ni con FAIL en modo no interactivo): el veredicto se registra
  con `puertas.py preparacion-bmad`. Diagrama del ciclo de vida PRINCE2 + BMAD en el README. Las puertas son insumo de los informes: `puertas.py estado`
  (highlight §6, informe de fin de etapa §6) y la línea de última/próxima puerta en `estado.py resumen`.

### Pruebas y documentación
- `probar_paquete.py`: 35 → **80** pruebas (BMAD 6.12.4 real, hook guardian con 36 decisiones, ciclo de puertas,
  regresiones v2.1).
- Nuevo `scripts/pruebas_vivo/` (`vivo.py`, `suite.py`) y `docs/evaluacion/resultados/`.
- Nuevos documentos: `RESUMEN-EJECUTIVO`, `INDICE`, `DEPENDENCIAS`, `PRUEBAS`, `CASOS-DE-USO-INTEGRACIONES`,
  `CLAUDE.md`, `AGENTS.md`; README con diagramas Mermaid; `INSTALACION` con requisitos por sistema operativo, BMAD,
  skills externas, MCP y verificación de 12 pasos.
- Clave canónica `acta-reunion-<fecha>`; ejemplo de colisión corregido (riesgos → pm-riesgos); drawio identificado
  como `jgraph/drawio-mcp` (npm `@drawio/mcp`).

## 2.0.0 · 2026-10-14

Orquestador en el hilo principal y cinco subagentes de fase; comandos como skills; puente BMAD de solo lectura con
fachada de especificación (`pm-spec-index/1`) y traspaso; integraciones MCP genéricas; OKR; actas desde
transcripciones; MSPDI; sanidad del ecosistema y hooks; migración automática desde v1.

## 1.0.0

Primera versión: agentes y skills PRINCE2 7 + PMBOK 8 + plantillas, ES/EN.
