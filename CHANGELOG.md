# Cambios · Changelog

## 2.7.0 · 2026-10-30 — portal unificado de pm-kb: tableros con historial, tarjetas-enlace, artefactos y enlaces compartidos

Capacidades nuevas según la definición del portal unificado aprobada el 2026-10-29: el tablero del proyecto pasa al
núcleo de pm-method, con su historial congelado en cada puerta, y pm-kb lo sirve junto con la búsqueda, los artefactos y
los enlaces para interesados. El portal no guarda datos de gestión propios ni escribe en la carpeta del proyecto. Sin
dependencias nuevas. Retrocompatible: los proyectos de 2.6.3 se abren sin migración (las instantáneas empiezan con la
primera puerta que se registre); el índice de pm-kb pasa al esquema 4 con `pm-kb base crear`, sin perder el índice ni
los tokens.

### Nuevo · núcleo de pm-method
- **`tablero.py`** (`skills/pm-estado-proyecto/scripts/`): `generar` (formato `pm-tablero/1` en JSON, o HTML de un solo
  archivo con CSP por hash, claro, oscuro y móvil), `congelar`, `listar` y `comparar`. Cada tarjeta es una
  **tarjeta-enlace**: nombre y descripción breves (sin montos, condiciones de la junta ni datos de interesados) y un id
  estable (`R-003`, clave de artefacto, `puerta:<tipo>:<etapa>`, id de producto) que no cambia si el archivo se mueve.
  Bloque de artefactos clave agrupados en generales, ciclo actual, cierre de etapas y decisiones de la junta (SPEC
  §1.10.17).
- **Historial congelado:** `estado.py puerta` guarda la instantánea del tablero tal como estaba antes de la decisión, con
  la decisión, en `03-control/reportes/tableros/` (JSON y HTML); también `cierre --prematuro`. Congelado manual con
  `tablero.py congelar --etiqueta`. Las instantáneas son inmutables, quedan en la bitácora con su huella y el guardián
  impide editarlas fuera de los scripts. Si el congelado falla, la puerta se registra igual con un aviso.
- **Tableros por actor:** `generar|congelar --actor "<nombre o rol>"` filtra por la matriz RACI (R, A, C o I) y por las
  filas que lo nombran; API en Python `actores()` y `filtrar_actor()`.
- **Lectura sin escrituras:** los comandos de lectura (`estado.py radar|productos|contexto|resumen`, `puertas.py
  estado`, `registro.py propuestas`, `tablero.py generar`) funcionan sobre una carpeta de solo lectura sin escribir
  nada: la sanidad sin `--reparar` ya no crea un registro que falta (lo informa REG-01) y la caché de la especificación
  de BMAD se usa en memoria si no se puede escribir.

### Nuevo · pm-kb (esquema 4)
- **Ubicaciones por id y movimientos:** cada fila, artefacto y documento tiene su ubicación vigente; si un archivo se
  mueve, el movimiento se detecta por huella sha256 o por clave de artefacto y el enlace sigue funcionando.
  `pm-kb enlaces` informa referencias rotas, la ruta sugerida y la acción. La ficha amplía ubicación, movimiento,
  versiones, relacionados por id e historia (también la de los artefactos).
- **Portal web:** cartera ordenada por lo que pide acción; por proyecto, las pestañas Tableros (actual en vivo,
  historial como línea de tiempo, comparar y vista por actor), Buscar, Artefactos (vigente y aprobada, con la marca de
  borrador; «Documentos» de visual-explainer, diagram-design y archify en `iframe` con `sandbox`, más descarga y SVG o
  PNG) y Preguntar. Botón «actualizar ahora» solo para tokens personales: regenera el tablero en el índice sin escribir
  en la carpeta, con origen validado y límite de uso. `pm-kb tablero` a demanda; `indexar` y `vigilar` publican el
  tablero y las instantáneas.
- **Compartir:** `pm-kb compartir crear|listar|revocar`: un enlace por tablero actual o instantánea, opcionalmente por
  actor, que vence (7 días por defecto, 90 como máximo), se puede revocar y registra su uso. El destinatario ve ese
  tablero y las fichas de sus tarjetas, de circulación de equipo (lo restringido solo con `--restringida`); no puede
  buscar, preguntar, usar el MCP ni ver otros proyectos. Las sesiones web llevan un identificador propio: la cookie
  nunca lleva el token.
- **`pm-kb vigilar`** reindexa ante cualquier cambio de los documentos indexables y publica el tablero; como servicio de
  usuario de systemd en WSL2 (`docs/servicios/pm-kb-vigilar@.service`) o como servicio `pm-kb-vigilar` del perfil `kb`
  en Docker. MCP con la herramienta `tablero` (9 herramientas).
- **Seguridad:** `pmkb.documento` y `pmkb.version` filtran también por circulación (antes, solo por proyecto).
- **Robustez:** la aplicación del esquema (`base crear`, `verificar`) y la carga de un índice o de un tablero (`indexar`,
  `vigilar`, `tablero`, `quitar`) se ordenan con un bloqueo consultivo de PostgreSQL, y la carga se repite entera ante un
  interbloqueo: antes, una indexación coincidente con `base crear` podía abortar (lo encontró la suite de variantes).

### Documentación y pruebas
- SPEC §1.10.17, PUERTAS, ARQUITECTURA §9.5 y §9.6, PM-KB §5 y §11.5 a §11.8, SEGURIDAD §14, RACI §5, guías de
  instalación §8.10 y §8.11; paso 15 del recorrido E2E-3 (historial, comparación, vista por actor, enlace compartido) y
  su diapositiva en el webinar; evidencia de las cinco guías regenerada (cada puerta imprime la instantánea congelada).
- Caso TB de `probar_paquete.py`; pruebas de pm-kb ampliadas (ubicaciones, migraciones 2 → 3 → 4, portal, compartir) y
  prueba de pantallas con Playwright (claro, oscuro y móvil, sin violaciones de CSP); unidad `kb-portal` de la suite de
  variantes (interacción con puertas, propuestas, BMAD, proyecto en inglés, carpeta de solo lectura y skills externas).
- Resultados del 2026-10-30 ([verificación 2.7.0](docs/evaluacion/resultados/2026-10-30-portal-v2.7.0.md)): regresión
  **558 OK · 0 FALLO** con Python 3.13 y **554** con 3.9; integración **123 OK en 40 eslabones**; guías E2E 5/5 (77
  pasos, 66 imágenes) con evidencia idéntica; suite de variantes `--nivel todo --repetir 2`: **592 OK · 0 FALLO · 0
  trazas** en cada corrida (31 unidades); pm-kb núcleo 39 OK, con base 116 OK, pantallas 68 OK, consultas de oro 14/15
  (MRR@5 0,75); 131 bloques Mermaid sin errores. Imagen Docker `pm-method:2.7.0`, dos corridas de la batería:
  regresión **561 OK · 0 FALLO** con Python 3.14, guías 5/5, integración 122 OK, variantes sin E2E **296 OK** y webinar
  5/5; perfil `kb` con el esquema 4, portal, enlace compartido (canje, sesión, revocación) y `pm-kb-vigilar`.
- No se repitió la batería en vivo con Claude Code (`suite.py`): las descripciones de las skills no cambiaron.

## 2.6.3 · 2026-10-30 — correcciones: idioma de los hallazgos, plan de excepción en el cierre prematuro y supuestos transferidos

Versión de corrección sobre 2.6.2: resuelve las tres limitaciones que dejó registradas la campaña de estabilización y
corrige el spot. Sin funciones nuevas de gestión ni dependencias nuevas. Retrocompatible: los proyectos de 2.6.2 se
abren sin migración y pm-kb no cambia su esquema.

### Corregido
- **Hallazgos en el idioma del proyecto.** En un proyecto en inglés, `sanidad.py` y `puertas.py verificar|estado|lista`
  daban sus mensajes en español. Ahora mensajes, correcciones, resumen, lista de control de la junta y etiquetas de
  `decisiones.csv` («— conditions:», «gate:») salen en el idioma de `estado.json`; los códigos, las severidades y las
  claves de `--json` son los mismos en los dos idiomas. El radar reconoce CAM-03 en inglés («risk reserve») y
  `riesgos.py` (REG-10) y `mapas.py` también son bilingües.
- **Plan de excepción durante un cierre prematuro.** `estado.py puerta autorizar-plan-excepcion` se admite en el cierre
  (CP) sin `--forzar` y sin volver a la entrega: sirve para rescatar productos o dejarlos en estado seguro. El plan queda
  en `cierre_prematuro.plan_excepcion`; **C-09** bloquea `autorizar-cierre` hasta que pm-director registra
  `estado.py cierre --plan-excepcion completado|cerrado --por "<rol: nombre>"` (el guardián reserva ese comando a
  pm-director). En un cierre planificado, el comportamiento no cambia.
- **Supuesto transferido sin destino.** `registro.py` rechaza `estado=transferido` si `notas` no cita el riesgo o issue
  que lo recibe (`→ R-###` o `→ I-###`) o si el destino no existe, también con `--forzar` y por propuesta. Para los datos
  que ya estaban así, la sanidad avisa **SUP-04**: 104 códigos en 15 familias.
- **Spot de LinkedIn:** la escena de estrategia decía que la integración con Jira, Slack y Teams estaba probada; ahora
  dice «integración probada con BMAD y lista para Jira, Slack y Teams». El cierre suma la línea «Iniciativa con el apoyo
  del PMI Capítulo Montevideo y de IEEE (Uruguay)». Las dos frases se locutaron de nuevo con el mismo modelo de voz
  (Kokoro-82M con `kokoro-onnx` 0.6.1); el video dura 56,5 s y los cuadros muestran las cifras de esta versión.
- **pm-kb:** `base crear` y `verificar` reintentan la aplicación del esquema hasta seis veces (antes, tres) ante un
  interbloqueo con el servicio respondiendo, con espera creciente y dispersa; con el equipo cargado, los tres intentos
  podían no alcanzar.
- **Suite de variantes:** la prueba del modelo que no responde a tiempo mide solo la espera del modelo; antes sumaba la
  búsqueda previa y fallaba con el equipo cargado aunque el plazo se respetara.

### Pruebas
- Caso nuevo **C3** de `probar_paquete.py` (23 comprobaciones): el mismo recorrido en español y en inglés, el plan de
  excepción en el cierre prematuro y el supuesto transferido. La suite de variantes comprueba además el idioma de los
  hallazgos en el ciclo completo.
- Resultados del 2026-10-29 y el 2026-10-30: regresión **531 OK · 0 FALLO** con Python 3.13 y **529** con 3.9 (omisiones DD, N y PE
  como en 2.6.2); integración **123 OK en 40 eslabones**; pm-kb núcleo 23 OK y con base 58 OK; consultas de oro 14/15
  (MRR@5 0,75); 131 bloques Mermaid sin errores; suite de variantes `--nivel todo --repetir 2`: **567 OK · 0 FALLO · 0 trazas** en cada corrida, con las mismas comprobaciones.
  Imagen Docker `pm-method:2.6.3`, dos corridas de la batería: regresión **534 OK · 0 FALLO** con Python 3.14 (caso DD
  completo), guías 5/5, integración 122 OK, variantes sin E2E **295 OK · 0 FALLO**, 131 bloques Mermaid y webinar 5/5;
  perfil `kb` con `verificar` 14 OK, indexación de E2E-1, token con vencimiento, ingreso por formulario y MCP desde el
  contenedor `pm`.
- No se repitió la batería en vivo con Claude Code (`suite.py`): las descripciones de las skills no cambiaron. El
  agente pm-director suma una línea sobre `cierre --plan-excepcion`, sin cambios de enrutamiento.

## 2.6.2 · 2026-10-29 — versión estable: robustez, caminos alternos, suite de variantes y opcionales verificados

Versión de estabilización, sin funciones nuevas de gestión: una campaña de pruebas sobre caminos alternos, excepciones,
dependencias, integraciones y los dos entornos (Claude Code y Hermes Agent) encontró y corrigió los defectos que se
detallan abajo; cada uno tiene su prueba de regresión. Incluye además las guías paso a paso de los opcionales y el
comparativo del resumen ejecutivo. Sin dependencias nuevas. Retrocompatible: los proyectos creados con 2.6.1 se abren
sin migración (lo prueba la suite de variantes); pm-kb no cambia su esquema.

### Corregido · datos y codificación
- **CSV con BOM** (el "CSV UTF-8" de Excel): `registro.py` duplicaba la columna `id` y repetía ids. Los CSV se leen con
  el BOM tolerado y los scripts los reescriben siempre en UTF-8 sin BOM y con CRLF.
- **Lectura fallida tomada como "ninguno"**: con un registro ilegible, `estado.py contexto`, `radar`, `periodo`,
  `briefing` y `productos` decían "Abiertos: ninguno" o mostraban un semáforo verde. Ahora terminan con el archivo y el
  motivo.
- **Trazas de Python con datos dañados**: un `estado.json` truncado o con tipos inválidos, o un CSV en otra codificación o
  mal formado, termina con un mensaje bilingüe (archivo, qué pasó, qué hacer), código 1, sin traza y sin reescribir nada
  (`esquema.DatosIlegibles`). La sanidad informa **DAT-01** (ERROR, familia nueva DAT: 103 códigos en 15 familias con CAM-06) y sigue con el resto; `puertas.py` cuenta una sanidad
  sin resultado como bloqueo y un C-07 que no se pudo verificar como condición.
- **CSV mal formado reescrito en silencio**: una fila con comilla sin cerrar, con más o menos campos que el encabezado o
  con columnas repetidas detiene el comando con el archivo y la línea (antes `registro.py agregar` la "normalizaba").
- **Hook de inicio silencioso** ante un proyecto roto: emite una línea de aviso y la sesión empieza igual.
- **Consolas que no son UTF-8** (Windows): los scripts y los hooks escriben su salida en UTF-8 y los subprocesos se leen
  con `encoding="utf-8"`. Con la consola cp1252, el guardián dejaba pasar una escritura de `estado.json` en una ruta con
  acentos: corregido.

### Corregido · caminos del ciclo
- **Cierre prematuro con puerta propia** (PRINCE2 7): `estado.py cierre --prematuro --decision D-### [--motivo] [--fecha]`
  desde la iniciación o la entrega (no desde la puesta en marcha, donde corresponde `autorizar-inicio` rechazado);
  `estado.json.cierre_prematuro` con fecha, decisión, motivo, origen y etapa (y la excepción abierta, si la había, que se
  cierra). En `autorizar-cierre` con cierre prematuro: **C-08** (bloqueo) exige el `inventario-cierre-prematuro`, C-07
  baja a aviso, C-04 sigue bloqueando y la lista de la junta suma V-07. `puertas.py estado`, el radar y `contexto` lo
  informan; EST-03 ya no da ERROR en un cierre desde la iniciación.
- **Cambios contradictorios**: `registro.py agregar|actualizar|proponer cambios` rechaza combinaciones contradictorias de
  `decision` y `estado` (tabla en la guía de registros §3), también con `--forzar`; la sanidad avisa **CAM-06** en datos
  existentes, y un cambio `rechazado` o `diferido` ya no consume presupuesto.
- `estado.py puerta --motivo` guarda el motivo en la puerta y en `decisiones.csv`; al rechazar una puerta, el aviso
  depende de la puerta y muestra la D-### anotada. La guía de `pm-direccion-decisiones` §6 recomendaba registrar un
  cierre prematuro con `--condiciones`, lo que dejaba una condición abierta que bloqueaba el cierre: usa `--motivo`.

### Corregido · integraciones y componentes
- **Hermes**: `instalar_hermes.py` convertía `${CLAUDE_PLUGIN_ROOT}/skills/x` en una ruta que no existe en la copia de
  Hermes y dejaba sin adaptar `~/.hermes/skills/<skill>`.
- `riesgos.py candidatos` terminaba con traza ante una instantánea de tracker que no estaba en UTF-8.
- `bmad.py` ignoraba en silencio `_bmad/custom/config*.toml` con Python anterior a 3.11: ahora avisa.
- `interesados.py plan-envio` avisaba "correo vacío" cuando el perfil no tenía canal aunque el correo existiera.
- La documentación de pm-mapas-estrategicos citaba `mapas.py render`, que no existe (`wardley render`, `recorrido render`).
- **pm-kb**: con el servidor de vectores caído o con error, `buscar` (CLI, MCP y web) y `indexar` terminaban con error;
  ahora siguen con búsqueda léxica (o indexan sin vectores) y avisan. Lo mismo con el re-ranqueo. Las propuestas
  pendientes se indexan (con las exclusiones de interesados). Las consultas de solo lectura y la aplicación del esquema
  se reintentan ante un interbloqueo de PostgreSQL. El extracto de una fila de registro empieza por su `estado` (un
  extracto recortado hacía parecer abierta una fila cerrada). pm-kb leía una clave inexistente de `estado.json`
  (`enfoque`) y su fixture usaba columnas que no están en el esquema.
- **Docker**: las variables de los canales de envío (SMTP, Slack, Teams) no llegaban al contenedor: el servicio `pm` las
  declara por nombre, sin valor. En el perfil `kb`, la clave del modelo de "Preguntar" va en `PMKB_CLAVE_MODELO` y llega
  solo a `pm-kb` (antes, `ANTHROPIC_API_KEY` llegaba también al contenedor `pm`), y `host.docker.internal` apunta al
  equipo.
- **CI**: el flujo de Docker no se disparaba con cambios en `pm-kb/**`, `SPEC.md` ni `compatibilidad.json` y fijaba una
  etiqueta vieja; `validar_paquete.py` controla las versiones del CI y de `docker/compose.yaml`.

### Documentación
- **Guías paso a paso de los opcionales** en los dos caminos: envío a interesados (`.eml`, SMTP, Slack, Teams), skills
  externas (diagram-design, visual-explainer, archify y Office), conectores MCP, modelos de pm-kb (API de Anthropic,
  Ollama, TEI), actualización de pm-kb en Docker y listas de aceptación; ejecutadas en contenedores descartables (ver
  Pruebas). Correcciones de pasos que no salían como decían (salidas de `pm-kb`, `apt autoremove`, `GIT_SSL_CAINFO` en
  redes que inspeccionan HTTPS, `read -rs` en zsh, `kit/render.mjs` de visual-explainer, dominios del instalador de
  Hermes).
- **Resumen ejecutivo**: comparativo honesto con PMI Infinity y con la gestión tradicional (dos diapositivas nuevas, 21 en
  total, y la §9 de `docs/RESUMEN-EJECUTIVO.md` con fuentes al 2026-10-29).
- `docs/PRUEBAS.md` §2.5 (suite de variantes), `docs/PUERTAS.md` (cierre prematuro), `docs/SANIDAD.md` (DAT-01, CAM-06),
  `SPEC.md`, `docs/ARQUITECTURA.md` §9.4 (datos ilegibles y codificación), guía de registros (decisión × estado),
  `docs/PM-KB.md` y las guías de las skills afectadas.
- Versión 2.6.2 en `plugin.json`, `compatibilidad.json`, `esquema.py`, pm-kb, las skills, `docker/`, el README y la
  documentación que cita la versión vigente. El material generado que no se regeneró (informe, webinar, `docs/ieee/`)
  conserva la versión con la que se hizo; el resumen ejecutivo se regeneró con 2.6.2.

### Pruebas
- **Suite de variantes** (`scripts/pruebas/variantes/correr.py --nivel …`): robustez y migración desde 2.6.1, caminos
  alternos, matriz pairwise (Python 3.9 y 3.13 × dependencias completas o mínimas × sin BMAD, v4, v6, 6.12.4, fuera de
  rango y con TOML × español e inglés × consola UTF-8 o cp1252 × rutas con espacios y acentos × cierre normal o
  prematuro), integraciones con fallas (SMTP y webhooks), contratos documentación ↔ comandos y esquema ↔ consumidores,
  Hermes (instalación, rutas y scripts desde la copia) y **opcionales** (pm-kb con simuladores de vectores, re-ranqueo y
  respuesta; skills externas sin red). Criterio de salida: 0 FALLO en dos corridas seguidas, sin trazas y con las
  omisiones del manifiesto.
- `probar_paquete.py`: casos **RB** (robustez de datos, 17) y **CP** (cierre prematuro y cambios, 25); cada caso aislado
  (un error cuenta como FALLO y la corrida sigue), `--casos`, `--json` y omisiones explícitas. Guías E2E con
  `--comparar` (evidencia normalizada), `--python` y limpieza de temporales. pm-kb: KB-53 a KB-58.
- Resultados (2026-10-29): `probar_paquete.py` **508 OK · 0 FALLO** con Python 3.13 (1 omisión: DD sin
  `PM_DIAGRAM_DESIGN`) y **506 OK · 0 FALLO** con 3.9.25 (3 omisiones); integración cruzada **123 OK · 0 FALLO en 40
  eslabones** (seis cadenas); suite de variantes `--nivel todo --repetir 2` **561 OK · 0 FALLO · 0 trazas · 0 omisiones
  fuera del manifiesto** en cada corrida, con las mismas comprobaciones (con pm-kb, Docker y las skills externas);
  guías E2E 5/5 en dos corridas con pm-kb, con evidencia idéntica entre corridas (cambia E2E-1 por los extractos de
  pm-kb); `pm-kb/pruebas/probar_kb.py` **23 OK** (núcleo, 3.13 y 3.9) y **58 OK** con base; consultas de oro **14/15, MRR@5
  0,75**; `validar_mermaid.py --render` **131 bloques · 0 errores**; `validar_paquete.py` OK (también con 3.9). Imagen
  Docker `pm-method:2.6.2` (`pm-pruebas`, sin red, dos corridas con el mismo resultado): **511 OK · 0 FALLO** en la regresión con Python 3.14 (caso
  DD completo), 5/5 recorridos, **122 OK en 40 eslabones**, variantes sin E2E **291 OK · 0 FALLO**, 131 bloques Mermaid y
  webinar 5/5; perfil `kb` con `pm-kb-db:2.6.2` (PostgreSQL 18.6, pgvector 0.8.1): `verificar` 14 OK, E2E-1 indexado en 444 unidades (399 vigentes), token con vencimiento, ingreso por el formulario (303) y MCP por HTTP con 8 herramientas desde el contenedor `pm`. En vivo con Claude Code (`suite.py todo`): enrutamiento
  **130/134** (variabilidad en cuatro frases ambiguas, sin cambios en las descripciones), guardarraíles y idioma OK; una
  sesión con el plugin, el MCP de pm-kb y diagram-design (USD 0,46). Informe de la campaña:
  `docs/evaluacion/resultados/2026-10-29-estabilizacion-v2.6.2.md`.

## 2.6.1 · 2026-10-29 — correcciones de pm-kb, del tablero HTML y de la verificación de puertas

Versión de corrección: seis problemas encontrados al evaluar un tablero del ciclo de vida para el portal de pm-kb y uno
más que apareció al verificarlos en Docker. No
cambia formatos de proyecto, registros ni comandos existentes del plugin; pm-kb agrega una opción (`token crear
--dias`) y actualiza su esquema de forma idempotente (`pm-kb base crear`, esquema 1 → 2). Sin dependencias nuevas; una
dependencia de pm-kb baja de versión (starlette).

### Corregido
- **pm-kb indexaba el resumen de `estado.json` con claves que no existen** (`nombre`, `proceso`, `etapa`): la ficha
  «Estado del proyecto» salía sin nombre, proceso ni etapa. `pmkb/fuentes.py` usa las claves de SPEC §1.10 (`proyecto`,
  `fase`, `proceso_actual`, `etapa_actual` con número y nombre, `enfoque`, `enfoque_entrega`, `idioma`), el título es
  «Estado del proyecto · <proyecto>» y esas claves ya no se indexan además como trozos sueltos; `indexador.preparar`
  toma el nombre de `proyecto`. El índice de un proyecto tiene unas pocas unidades menos (E2E-1: 444 unidades, 399
  vigentes). El fixture de pruebas y `pm-kb verificar` usan las claves reales.
- **Tablero HTML de pm-visuales con script en línea sin política propia**: `tablero-avance.html` sigue siendo un solo
  archivo autocontenido y trae ahora una CSP propia (`default-src 'none'`, sin red, formularios ni `<base>`) que solo
  autoriza su script de dibujo por el hash sha256; un script inyectado o alterado no corre. Un servicio que lo sirva
  (por ejemplo pm-kb) puede autorizarlo agregando ese mismo hash. Cómo recalcular el hash si se cambia el script:
  `pm-visuales/references/guia.md` §3.
- **Los tokens de pm-kb no vencían**: `pmkb.acceso.vence`; `pm-kb token crear --dias N` (1 a 365, 90 por defecto) muestra
  la fecha de vencimiento; `pmkb.identidad()` descarta los vencidos; `token listar` muestra el vencimiento y señala los
  tokens emitidos sin él (siguen válidos hasta revocarlos); el enlace de la sesión local de `pm-kb servir` vence a las
  24 horas; la caché de identidad del servicio nunca supera el vencimiento.
- **starlette 1.10.0 tenía cinco días de publicada**: pm-kb fija **starlette 1.7.0** (2026-09-23) en
  `pm-kb/requirements.txt`, regenerado con hashes; el resto de las versiones no cambia.
- **`pm-kb servir` rechazaba un puerto recién liberado** durante unos 60 s («Address already in use») por conexiones en
  TIME_WAIT: la verificación previa (`config.puerto_ocupado`) usa `SO_REUSEADDR`, como uvicorn; un proceso que escucha
  en el puerto sigue bloqueándolo con el mensaje de siempre.
- **E-10 repetía una condición ya cumplida**: si el veredicto CONCERNS del gate de preparación de BMAD ya fue condición
  de una puerta posterior a él y esa condición se registró como cumplida, `puertas.py` lo informa como **aviso** E-10
  (cita la puerta y su D-### e indica registrar un veredicto nuevo con `puertas.py preparacion-bmad` si el plan cambió);
  con la condición abierta sigue siendo condición. En E2E-3, después de `cumplir-condiciones`, E-10 pasa de condición a
  aviso.
- **El formulario de ingreso de la web de pm-kb respondía 500** (encontrado al repetir la verificación en Docker): pegar
  el token en la pantalla de ingreso (`POST /ingresar`) fallaba porque `Request.form()` de Starlette exige el paquete
  python-multipart, que pm-kb no instala; el enlace `/ingresar?token=…` sí funcionaba. El formulario se lee con la
  biblioteca estándar (`urllib.parse`), sin dependencias nuevas.

### Documentación
- `docs/PM-KB.md` (§10, §12, §13, §14 y solución de problemas), `docs/SEGURIDAD.md`, `docs/PUERTAS.md` (E-10),
  `docs/DEPENDENCIAS.md` y `docs/DOCKER.md` (starlette 1.7.0), guías de instalación (token con vencimiento y esquema
  pm-kb 2), `docs/PRUEBAS.md`, `docs/INDICE.md`, `docs/CATALOGO.md`, `docs/RESUMEN-EJECUTIVO.md`, `README.md`,
  `pm-visuales/references/guia.md` §3 y la guía E2E-3 (E-10). Evidencia de E2E-1, E2E-3 y E2E-4 y la captura
  `g1-kb-ficha.png` regeneradas.
- Versión 2.6.1 en `plugin.json`, `compatibilidad.json`, `esquema.py`, pm-kb, las skills, `docker/`, el README y la
  documentación que cita la versión vigente. Los registros fechados que no se repitieron y el material generado
  (informe, resumen ejecutivo, webinar, `docs/ieee/`) conservan la versión con la que se hicieron.

### Pruebas
- `probar_paquete.py`: CSP del tablero (hash declarado = script de dibujo; el tablero abre en Chromium sin violaciones
  ni errores, si Playwright está instalado) y E-10 con la condición abierta y cumplida.
- `pm-kb/pruebas/probar_kb.py`: KB-47 (resumen de `estado.json`), KB-48 (vencimiento por defecto y rango), KB-49 (token
  vencido sin identidad), KB-50 (la web responde 401 a un token vencido) y KB-51 (puerto en TIME_WAIT frente a un
  proceso escuchando) y KB-52 (ingreso por el formulario de la web con un token válido y uno falso; con el código
  anterior responde 500).
- Resultados (2026-10-29): `probar_paquete.py` **466 OK · 0 FALLO** con Python 3.13 y **464 OK · 0 FALLO** con 3.9.25;
  integración cruzada **118 OK · 0 FALLO en 38 eslabones** (`--sin-e2e`); `pm-kb/pruebas/probar_kb.py` **21 OK** (núcleo,
  3.13 y 3.9) y **52 OK · 0 FALLO** con `--con-base` (starlette 1.7.0, PostgreSQL 16.15); `pm-kb verificar` 14 OK;
  guías E2E 5/5 en dos corridas con pm-kb, con evidencia idéntica entre corridas; `validar_paquete.py` OK (también con el
  intérprete 3.9); `claude plugin validate .` pasa con los avisos de siempre. Imagen Docker `pm-method:2.6.1` (`pm-pruebas`,
  sin red): **469 OK · 0 FALLO** en la regresión con Python 3.14, 5/5 recorridos, **122 OK en 40 eslabones**, **131
  bloques Mermaid** sin error y webinar 5/5; perfil `kb` con `pm-kb-db:2.6.1` (PostgreSQL 18.6, pgvector 0.8.1):
  `verificar` 14 OK, E2E-1 indexado en 444 unidades (399 vigentes), token con vencimiento y `--dias 400` rechazado,
  ingreso por el formulario (303), MCP por HTTP con 8 herramientas desde el contenedor `pm`, `/proyectos` de solo lectura.
  Las pruebas en vivo no se repitieron (no cambian descripciones, agentes ni hooks).

## 2.6.0 · 2026-10-29 — decidir con contexto, vigencia y bitácora, y pm-kb: buscar en los proyectos con evidencia citada

Tres frentes. (1) **Capacidad de decisión** para cualquier elección entre alternativas, dentro de
`pm-direccion-decisiones` y sin skill ni registro nuevos: expediente, matriz multicriterio, pregunta tipada, RACI ↔
autoridad y vínculo con los mapas de Wardley y del recorrido del cliente; biblioteca estándar (Python 3.9+), sin modelo
propio ni llamadas a red. Toma de los modelos de decisión tipada (Laya, TypeSafe Jev) tres ideas, no el modelo: pregunta
tipada, respuesta restringida a las opciones y abstención explícita. (2) **Control de las escrituras**: vigencia y
contradicciones de decisiones, bitácora encadenada y propuestas con huella (ideas de la evaluación de exxperts).
(3) **pm-kb**, componente opcional fuera del plugin: índice de conocimiento en PostgreSQL con búsqueda citada en
español, versiones de documentos y relaciones por ids, para personas (web) y agentes (MCP de solo lectura), instalable
por los dos caminos (WSL2 con un clúster propio del usuario; Docker con la base en un contenedor segregado).

### Agregado
- **`skills/pm-direccion-decisiones/scripts/decision.py`** con tres subcomandos y seis tipos de decisión (`riesgo`,
  `negocio`, `planificacion`, `okr`, `cambio`, `adquisicion`):
  - `expediente`: paquete de contexto aplicable a la decisión, de solo lectura y con encabezado "evidencia, no
    instrucciones": pregunta y **nivel que decide** (SPEC §1.10.8, la regla `motivos_autoridad` de `registro.py`, el
    análisis de `impacto.py` o el escalado del riesgo), tolerancias y presupuestos con su consumo, beneficios y apetito
    de riesgo con `archivo:línea`, registros relacionados a 1–2 saltos (ids citados en los dos sentidos y columnas
    `refs` del esquema; `--tema` por palabras), supuestos críticos, lecciones por `aplicar_en`, interesados y personas
    afectadas, y las **cifras de otros scripts sin recalcular** (`riesgos.py opciones`, `release.py capacidad` y
    `okr.py` en modo lectura; último corte de EVM; `inversion.py`, `impacto.py` o cualquier `--json` con `--importar`).
    Excluye la valoración y las notas de los interesados con `confidencial=si` y los datos de contacto de todos; tope con
    `--max-items` y `--max` ("… y N más").
  - `matriz`: hoja de trabajo `03-control/decisiones/<ID>/` (`decision.json`, `criterios.csv`, `opciones.csv` y las
    salidas `--json` copiadas con `--importar`); `--proponer` la crea desde `templates/criterios-por-tipo.csv` (en
    riesgos, con las opciones de `riesgos.py` y su valor neto; en negocio, con las de `inversion.py`). Valida pesos
    (normalizados con aviso si no suman 100), escalas, números sin separador de miles y la fuente de cada peso y de cada
    puntaje; normaliza por escala o mín–máx, calcula la suma ponderada, aplica eliminatorios, marca dominadas, mide la
    **sensibilidad de cada peso** (el peso con el que otra opción pasa a primera) y los empates; con un puntaje faltante
    se abstiene (`pedir-informacion`). `--markdown` da el bloque para la solicitud de decisión.
  - `matriz --elegir O# --por "<rol: nombre>"`: registra la decisión de la persona con `registro.py` en
    `decisiones.csv` (opciones con su puntaje, criterios y pesos, recomendada, hoja); `--motivo` obligatorio si difiere
    de la recomendada, con empate, con sensibilidad baja o si la matriz se abstuvo; respeta el nivel de la hoja; las de
    la junta las registra pm-director y se citan con `--decision D-###`; en riesgos (`ref` `R-###/O#`) llama a
    `riesgos.py opciones --elegir`, sin duplicar la decisión; un segundo `--elegir` se rechaza.
  - `pregunta`: pregunta cerrada para el modelo y la junta (una opción O#, un nivel de la escala o sí/no, o
    `pedir-informacion`) con la matriz y el expediente; `--validar` comprueba una respuesta propuesta (opción existente
    y no eliminada, evidencia citada que esté en el expediente, abstención con lo que falta cuando la hoja tiene huecos).
    No decide ni registra.
- **`templates/criterios-por-tipo.csv`**: criterios, pesos, sentido, escala, eliminatorios e importación por tipo.
- **Sanidad DEC-01 y DEC-02** (avisos, solo hojas ya decididas): elegida distinta de la que hoy recomienda la matriz sin
  motivo (también si la hoja cambió después de decidir) o D-### inexistente; pesos o puntajes sin fuente.
- **Capacidad de decisión alineada con la matriz RACI** (`raci.csv`, sin reglas duplicadas): PRINCE2 define la autoridad
  (niveles de decisión, tolerancias, `motivos_autoridad`, límite de la autoridad de cambio) y la RACI debe reflejarla.
  - `esquema.nivel_autoridad(e, texto, nombre)`: nivel de decisión de una persona, el mismo criterio para `--por`, para
    el A de la RACI y para `decidido_por`: roles de `estado.json` por nombre (ejecutivo, usuario y proveedor sénior →
    `junta`; autoridad de cambio; gestor; product owner; jefes de equipo, aseguramiento y soporte → `equipo`) y, si no,
    palabras del rol escrito; si no, no determinado.
  - `decision.py expediente`: dentro de §7, la RACI de los elementos afectados (ids de partida y relaciones a 1 salto):
    A, C (consultar antes) e I (informar después) con nombre y rol de `stakeholders.csv`, sin valoraciones ni contacto
    (también con `confidencial=si`), y si el A tiene la autoridad del nivel requerido; `--json` con `raci`.
  - `decision.py matriz --elegir`: `--motivo` obligatorio si quien decide no es el A de un elemento afectado ni una
    autoridad superior (alcanza el nivel requerido y supera el del A; en la junta basta igualarlo); aviso de
    **incoherencia RACI ↔ autoridad** si el A no alcanza el nivel requerido, sin elegir cuál vale; recordatorio de los C;
    borrador del aviso a los I con `interesados.py plan-envio` (base `<hoja>/aviso-D-###.md`, mensajes en estado
    `borrador`; nada se envía, `envios.py` sigue con confirmación humana). `--sin-aviso` solo muestra el comando.
    `decision.json` → `eleccion.raci`.
  - **Sanidad DEC-03** (decidió quien no es el A ni una autoridad superior, sin motivo) y **DEC-04** (el A no tiene la
    autoridad del nivel requerido, solo si su nivel se puede determinar), sobre las hojas y sobre las decisiones D-###
    que son elementos de la RACI.
- **Vigencia y contradicciones de decisiones** (idea 1 de la evaluación de exxperts; regla 12 de
  `pm-direccion-decisiones`, "una decisión reabierta se marca reemplazada", con soporte en los datos):
  - `decisiones.csv` agrega al final `reemplaza` (D-### que la decisión deja sin efecto) y `conviven` (D-### que la
    persona decidió mantener vigentes a la vez); migración transparente al primer uso. "Reemplazada por" se deriva.
  - `registro.py agregar|actualizar decisiones`: ids existentes, sin reemplazos dobles ni ciclos ni reemplazo de una
    posterior (se omite con `--forzar`) y **autoridad**, que no se omite: nivel igual o superior al de la reemplazada y
    quien decide con esa autoridad (`esquema.nivel_autoridad`). Corrige la regla "la fecha más nueva decide" de exxperts:
    una decisión posterior de nivel inferior no deja sin efecto la de la junta.
  - `esquema.anotar_decision` completa `reemplaza` al aprobar una versión nueva del mismo artefacto (`estado.py
    aprobar`, `bmad.py linea-base`), al volver a fijar todas las claves de los presupuestos o al cambiar el enfoque de
    entrega (si la anterior no tiene nivel mayor ni fecha posterior).
  - Módulo nuevo `skills/pm-estado-proyecto/scripts/vigencia.py` (funciones puras; `vigencia.py --proyecto <dir>`):
    vigentes, cadenas, asunto por ids citados (luego artefactos, luego texto), contradicciones probables y revisiones
    vencidas.
  - `decision.py vigentes [--tema] [--ids] [--historia] [--corte] [--max] [--json]`: decisiones vigentes con su cadena
    (D-010 → D-017), `conviven`, `revisar_en` vencido y contradicciones probables. `expediente` trae solo vigentes y
    menciona las reemplazadas como historia (`--historia` las deja en la tabla); `resumen_fila` muestra `reemplaza`.
    `matriz --elegir … --reemplaza D-###` (o `reemplaza` en `decision.json`, hoja reabierta) valida la autoridad antes
    de registrar y escribe la columna (fila nueva, `--decision` o vía `riesgos.py`).
  - **Sanidad DEC-05** (dos vigentes del mismo asunto, texto parecido y valor distinto —versión, cifra normalizada,
    fecha, negación es/en o una palabra cambiada— sin `reemplaza` ni `conviven`; agrupa por ids citados antes de
    comparar, así "residual de R-005" y "… de R-004" no se comparan) y **DEC-06** (`revisar_en` vencido sin decisión
    posterior del mismo asunto y con lo que cita todavía abierto). Solo avisos; corren siempre que haya decisiones.
- **Búsqueda que entiende español e inglés** (idea 4): módulo nuevo `skills/pm-estado-proyecto/scripts/texto.py`
  (biblioteca estándar, determinista; `texto.py "<texto>"`): minúsculas sin tildes, palabras vacías es/en, lematizador
  ligero documentado (plurales, género y vocal final, participios, gerundios, -ción: normativa = normativo =
  normative), glosario corto inglés → español de gestión, fechas y meses ("enero 2027" ↔ 2027-01, "15 de marzo de 2027"
  = "March 15, 2027" = 15/03/2027, T1/Q1; una fecha de la fila vale también por su mes, año y trimestre), cifras con
  separadores (39.800 = 39,800 = "39,8 mil"), versiones e ids (R-3 = R-003). Lo usan `decision.py expediente --tema`
  (antes, subcadenas de 4 letras; ahora términos normalizados, de más a menos coincidencias), `vigentes --tema` y
  DEC-05; queda listo para el futuro indexador.
- **Bitácora de escrituras** (idea 2 de la evaluación de exxperts; SPEC §1.10.16): toda escritura de `estado.json`, de
  un registro o de una propuesta por el mecanismo común de 2.5.1 (`esquema.escribir_atomico`, es decir `registro.py`,
  `estado.py`, `puertas.py`, `interesados.py`, `envios.py`, `bmad.py` y lo que llama a `registro.py`) agrega bajo el
  mismo bloqueo una línea a `<proyecto>/.bitacora.jsonl` (solo anexado): número, fecha y hora reales, script,
  operación, archivo, ids, altas, bajas, campos cambiados antes → después (sin valores de interesados ni de filas
  `confidencial=si`), claves de `estado.json`, `--por`, sha256 del archivo antes y después y de la línea anterior
  (cadena). Una reescritura sin cambios no se anota; sin deshacer (una decisión se corrige con `reemplaza`).
  - `registro.py historial [ID|registro|estado|P-###] [--desde] [--max] [--json]`: qué escribió cada script y la
    verificación de la cadena y de la continuidad de cada archivo.
  - `registro.py reconocer <registro|estado> --por … --motivo …`: una persona deja asentado un cambio hecho fuera de
    los scripts (merge de git, corrección revisada), sin restaurar nada.
  - **Sanidad BIT-01** (cadena rota) y **BIT-02** (cambio fuera de los scripts no reconocido), solo avisos; familia
    nueva BIT.
  - `paquete.py auditoria --con-bitacora` incluye la bitácora entera (`bitacora.jsonl`) y `paquete.py verificar` la usa
    para explicar un registro alterado ("la última escritura anotada dejó la versión del expediente: el cambio no salió
    de los scripts"). Sin la opción, el expediente no cambia.
- **Propuestas con huella y reaplicación al aprobar** (idea 3; SPEC §1.10.16), primitiva de la escritura por propuesta
  de una base compartida: `registro.py proponer <registro> [ID] --campo … --por "<agente>" [--motivo]` valida como
  `agregar`/`actualizar` y guarda `03-control/propuestas/P-###.json` con la huella del registro, la de la fila y los
  valores base de los campos tocados, sin tocar el registro; `aprobar P-### --por "<rol: nombre>"` (una persona
  distinta de quien propuso) aplica con las reglas de `registro.py` si nada cambió, **reaplica** sobre la versión
  actual si cambiaron otras filas u otros campos (un alta toma el id siguiente) o deja la propuesta en **conflicto**
  con la explicación (campo, base, hoy, propuesto); si no pasa las validaciones (por ejemplo, el control de cambios),
  sigue pendiente. `rechazar` y `propuestas [--estado …]` (qué pasaría al aprobar hoy). Todo queda en la bitácora
  (`propuesta`, `propuesto_por`, `por`).
- `hooks/guardian.py`: niega escribir `.bitacora.jsonl` y `03-control/propuestas/P-###.json` con Write/Edit o Bash y
  pide confirmación de una persona ("ask") para `registro.py aprobar` y `registro.py reconocer`.
- **pm-kb** (`pm-kb/`, referencia `docs/PM-KB.md`), componente opcional (no es skill ni agente):
  - Indexador (`pmkb/fuentes.py`, `versiones.py`, `relaciones.py`, `indexador.py`): unidades citables (fila de registro
    con su id, sección de Markdown, diapositiva, hoja, ventana de transcripción, objeto JSON con `id`) desde Markdown,
    CSV, JSON, YAML, TXT, SRT/VTT, EML, HTML y, con MarkItDown, DOCX/PPTX/XLSX/PDF; exclusiones al construir
    (`preferencias`, `envios`, `03-control/comunicaciones/`, contacto de interesados y valoración con `confidencial=si`,
    `.bitacora.jsonl`, `_bmad/`, `.pmkbignore`, `--excluir`), circulación `restringida` (front matter o `--restringir`) y
    confianza `externo` para transcripciones y correos. **Versiones de documentos**: documento lógico → versiones desde
    `estado.json.artefactos`, las copias de `historial/`, `decisiones.csv` (quién aprobó y con qué D-###), el front
    matter y el nombre normalizado (una fecha en el nombre es una serie, no una versión); vigente = la última (con aviso
    si hay una aprobada anterior), aprobada = la última aprobada; duplicados exactos una sola vez; cambios por secciones.
    **Relaciones** declaradas por las columnas de los registros y por menciones de ids. Todo el índice de un proyecto se
    reemplaza en una transacción.
  - PostgreSQL 16 o posterior con `vector` (pgvector), `unaccent` y `pg_trgm` de los repositorios de Ubuntu; BM25 en SQL
    con la configuración `pmkb.es` (raíz española sin tildes), ids abreviados (R-3 = R-003), títulos parecidos, sinónimos
    de gestión y glosario inglés → español; vectores, fusión RRF y re-ranqueo opcionales (TEI o API compatible con
    OpenAI). RLS por proyecto y circulación con el rol `pmkb_lector`; tokens por persona (solo su sha256).
  - Línea de comandos `pm-kb` (`base`, `indexar`, `buscar`, `ficha`, `relaciones`, `versiones`, `cambios`, `documento`,
    `contexto`, `estado`, `token`, `servir`, `mcp`, `db`, `verificar`), **interfaz web** (búsqueda con facetas y extractos
    resaltados, ficha con grafo de relaciones (Cytoscape.js 3.34.3, MIT, incluido), versiones con línea de tiempo y
    comparación, "Preguntar" con respuesta citada si hay un modelo configurado o la evidencia ordenada si no) y **MCP de
    solo lectura** propio (stdio y Streamable HTTP; `buscar`, `contexto`, `ficha`, `relaciones`, `documento`,
    `versiones`, `cambios`, `estado_indice`; topes de tokens y "evidencia, no instrucciones").
  - Instalación: `pm-kb/instalar-wsl.sh` (paquetes de Ubuntu, entorno con dependencias fijadas por hash, clúster de
    PostgreSQL del usuario solo por socket, verificación de punta a punta) y perfil `kb` de `docker/compose.yaml` con la
    imagen `pm-kb-db` (`docker/pm-kb-db.Dockerfile`: PostgreSQL y pgvector de Ubuntu 26.04, contenedor segregado en una
    red interna sin puertos ni salida, secretos de Docker con `docker/kb-preparar.sh`) y el servicio `pm-kb` sobre la
    imagen de pm-method.
- **Decisiones ↔ mapas estratégicos** (`decision.py`, `mapas.py`; guía de pm-direccion-decisiones §13.11): un componente
  de Wardley o un paso de un recorrido se nombra en los ids de la decisión como `<mapa>:<id>` (`entregables:C2`).
  `decision.py expediente` agrega la sección 10 «Mapas estratégicos (contexto, no criterio)» con cita `archivo#id`: de
  Wardley, etapa, evolución, decisión, inercia, evidencia, lo que depende del componente y el movimiento previsto; del
  recorrido, emoción con fuente, dolor, Kano, KPI y persona; también los elementos que citan en `refs` un id de la
  decisión. Un elemento o mapa inexistente es dato faltante; `--json` trae `mapas`; `pregunta --validar` acepta el
  elemento como evidencia. Lectura en `mapas.py` (`contexto`, solo lectura).
- **Criterios de hacer o comprar**: `decision.py matriz <ID> --proponer --tipo adquisicion --criterios hacer-o-comprar`
  (filas `adquisicion:hacer-o-comprar` de `templates/criterios-por-tipo.csv`): diferenciación, costo total, tiempo hasta
  disponible, dependencia del proveedor, capacidad interna y riesgo de construir algo que va a volverse commodity. La
  evolución del mapa es la fuente de los puntajes, no un criterio. `--criterios` elige cualquier conjunto con nombre;
  uno inexistente se rechaza con la lista de los disponibles.
- **Cierre de MAP-01 al elegir**: `matriz --elegir … --por …` cita la decisión registrada en cada elemento nombrado con
  `mapas.py vincular` (en un paso con dolor, cuenta como tratamiento: MAP-03) y lo anota en `eleccion.mapas`; la
  columna `decision` del componente no se cambia (se avisa en la salida).
- Guía de pm-direccion-decisiones §13.12: cómo puntuar opciones de tratamiento de un dolor del recorrido (sin matriz
  propia: MoSCoW y `release.py`, con el contexto del expediente).
- **Casos E2E**: E2E-1 paso 16 «La pregunta de la junta» (pm-kb: indexar, búsqueda citada con C-003 y su motivo, ficha
  de R-003 con relaciones por ids, versiones y cambios del business case v1.0 → v1.1, `--aprobado`, contexto para
  agentes y registro del MCP en Claude Code y Hermes; capturas `g1-kb-busqueda`, `g1-kb-ficha` y `g1-kb-versiones`);
  E2E-4 paso 9c (tres versiones del business case, cambios 1.1 → 1.2, búsqueda vigente, aprobada y con historia, y
  `ficha D-013 --historia` desde la bitácora); E2E-5 paso 5b con hacer o comprar de C2 (comprar 78,8 · tercerizar 52,3 ·
  construir 28,7), el expediente con el contexto de los mapas, D-004 citada en C2 e imagen `g5-hacer-comprar-c2.png`, y
  KPI en el recorrido del paciente. Webinar de los tres casos actualizado (20 diapositivas por clase). pm-kb es opcional
  en los recorridos (`comun.kb_disponible`): sin él, «OMITIDO pm-kb» y el recorrido termina OK; con él, evidencia
  reproducible (fecha del indexado, puerto, token y fechas de la bitácora enmascarados).

### Cambiado
- Agente `pm-orquestador`: si está conectado el MCP de pm-kb, usa `buscar` o `contexto` para ubicar la evidencia citada
  antes de abrir archivos completos (la carpeta sigue siendo la fuente de verdad y toda escritura pasa por los scripts).
- Imagen Docker `pm-method:2.6.0`: incluye las dependencias de pm-kb (`pip install -r docker/requirements.txt -r
  pm-kb/requirements.txt`, por hash) y el comando `pm-kb`; `compose.yaml` suma el perfil `kb` (servicios `pm-kb-db` y
  `pm-kb`, red `kb-interna`, volumen `pm-kb-datos`, secretos `pmkb_admin_clave` y `pmkb_lector_clave`); `.gitignore` y
  `.dockerignore` excluyen `docker/kb-secretos/`. El resto de los servicios no cambia.
- Descripción de `pm-direccion-decisiones`: suma "matriz de decisión" y "pesos" y se acorta en lo demás (196
  caracteres; listado de descripciones: 6.966 de 7.500), para que el total de las skills visibles siga bajo el umbral
  de INS-05 (≈ 8.000) en los recorridos E2E. SKILL.md condensado (12.425 bytes) con el paso 5 "Opciones con contexto".
- Una línea que remite a `decision.py` en `pm-riesgos`, `pm-issues-cambios`, `pm-caso-de-negocio`, `pm-agil-hibrido`,
  `pm-okr` y `pm-adquisiciones` (y `pm-sanidad` con la familia DEC); plantillas `solicitud-puerta.md` y
  `evaluacion-excepcion.md` con el bloque de la matriz.
- `hooks/guardian.py` pide confirmación de una persona ("ask") ante `decision.py matriz … --elegir` y
  `riesgos.py opciones … --elegir` (también abreviado y desde pm-director), como con `registro.py aprobar`: los dos
  registran en `decisiones.csv` la decisión de quien figura en `--por`.
- `puertas.py preparacion-bmad`: un veredicto nuevo del gate de preparación de BMAD completa `reemplaza` con el
  anterior (`vigencia.reemplazo_automatico`, prefijo "gate de preparación de BMAD:"), como el enfoque de entrega: el
  `estado.json` guarda un solo veredicto y el anterior queda como historia. El recorrido E2E-4 deja de marcarlo a mano.
- `decision.py`: `matriz --proponer --fecha AAAA-MM-DD` fija `creada` (recorridos reproducibles); `pregunta --corte`
  con la misma semántica que en `expediente`; `matriz --elegir --revision AAAA-MM-DD` pasa la próxima revisión a
  `riesgos.py opciones --revision` en una hoja de riesgo (en otra hoja se rechaza y remite a `revisar_en`); `--fecha`,
  `--corte` y `--revision` se validan como AAAA-MM-DD. El recorrido E2E-1 usa `--revision` en lugar de actualizar
  `fecha_revision` aparte.
- `decision.py` con varias salidas importadas, regla determinista: la `ref` de la opción (`archivo.json:ref`) o el
  criterio (`archivo.json:campo`) nombran el archivo; una ref sin calificar que aparece en más de un archivo u objeto es
  un error que dice dónde está (no se toma ni la primera ni la última); dos `--importar` con el mismo nombre de archivo
  en una llamada son un error (antes, la segunda pisaba a la primera en la hoja).
- Portada de clase del HTML del webinar (`scripts/webinar/generar.py`): desde cuatro objetivos, en dos columnas; con
  cinco objetivos (E2E-3) o con un título u objetivos de dos líneas (E2E-5, clase 1) la lista llegaba al pie. El PPTX
  ya ajustaba el alto de cada fila y no cambia.

### Corregido
- `decision.py expediente --ids`: solo se tomaban los ids con fila en los registros y separados por coma, en
  mayúsculas; con `KR-1.1,B-02`, `r-001` o `R-001;R-002` mostraba "ids de partida: —", dejaba vacía la sección 4 y
  pedía "ids o tema". Los ids se separan por coma, punto y coma o espacios, el prefijo pasa a mayúsculas, un id sin
  fila propia (B-02, KR-1.1, E-3) es id de partida y trae a salto 1 las filas que lo citan, y un id de registro que no
  existe se informa como dato faltante.
- `decision.py expediente`, sección 4: el "Ninguno: indicar ids…" dependía de la historia de decisiones reemplazadas y
  no de la tabla, así que aparecía debajo de una tabla con filas y faltaba cuando no había ninguna. La sección muestra
  la tabla, o "Ninguno" (con el motivo según haya ids o tema), y la historia aparte.
- `decision.py vigentes --ids` no encontraba las decisiones vinculadas solo por `artefactos_afectados` (un KR, un
  paquete 3.1, la hoja `03-control/decisiones/<ID>/`) ni ids que no fueran de registro: compara cada elemento de esa
  columna (id, ruta o final de ruta) y los ids de forma X-n citados en el texto, con límites de palabra.
- `mapas.py vincular` acepta el nombre del archivo del mapa (`wardley-x.json`) aunque no esté en la carpeta actual, y
  escribe el JSON de forma atómica bajo el bloqueo del proyecto (`esquema.escribir_atomico`, `esquema.bloqueo`).
- `decision.py matriz --elegir --decision D-###` informaba el nivel por defecto (`gestor`, o el de `--nivel`) aunque la
  decisión citada fuera de la junta: el nivel sale de la fila citada (con aviso si `--nivel` difiere) y no puede ser
  menor que el de la hoja; en una hoja de riesgo, `riesgos.py opciones --elegir --decision` informa y registra el nivel
  de esa fila.

### Documentación
- Guía de `pm-direccion-decisiones` §13 (tipos y quién decide, expediente, hoja, cálculo con un ejemplo a mano,
  elegir, pregunta tipada, sanidad, recetas por tipo; PRINCE2 7 `### 6.10` y `## 8.`, PMBOK 8 `### 3.2`, `### 3.4` y
  `### 5.3`). `SPEC.md` §1.5 (carpeta `03-control/decisiones/`) y §1.10.15 (hojas de decisión). `docs/CATALOGO.md`,
  `docs/TERMINOLOGIA.md` (análisis de decisiones multicriterio, matriz de decisión, sensibilidad de los pesos,
  expediente y pregunta tipada), `docs/SANIDAD.md`, `docs/colisiones.md`, `docs/ARQUITECTURA.md`, `docs/INDICE.md`,
  `docs/PRUEBAS.md`, `docs/SEGURIDAD.md` §12, `CLAUDE.md`, `AGENTS.md` y `README.md`.
- RACI y autoridad: guía de `pm-direccion-decisiones` §13.9 (precedencia, elementos afectados, nivel de una persona,
  reglas al elegir, ejemplo) y menciones en §13.2, §13.5 y §13.7; guía de `pm-interesados` §2 (la RACI refleja la
  autoridad; uso en decisiones); `SPEC.md` §1.10.10 y §1.10.15; `docs/SANIDAD.md` (DEC-03, DEC-04, caso DR) y guía de
  `pm-sanidad`; `docs/CATALOGO.md`, `docs/TERMINOLOGIA.md` (nivel de autoridad, incoherencia RACI ↔ autoridad),
  `docs/PRUEBAS.md` y `CLAUDE.md`. SKILL.md de `pm-direccion-decisiones` (12.498 bytes) con una línea en el paso 8 y en
  Calidad; sin cambios en las descripciones de las skills.
- Vigencia y búsqueda: guía de `pm-direccion-decisiones` §13.10 (nueva) y menciones en §9 regla 12, §10, §13.2, §13.5
  y §13.7; SKILL.md (regla 13 y paso 5; 12.494 bytes); `SPEC.md` §1.10.8 (columnas, validación, reemplazo automático)
  y §1.10.15 (vigencia, asunto, DEC-05/06, búsqueda); guía de `pm-estado-proyecto` §5.1 y §6 (`vigencia.py`,
  `texto.py`); `pm-registros` (guía §6 y `guia-registros.md` §4 con las columnas); `pm-exportar/references/formatos.md`;
  guía de `pm-sanidad`; `docs/SANIDAD.md` (DEC-05, DEC-06, casos BU y VG), `docs/CATALOGO.md`, `docs/TERMINOLOGIA.md`
  (vigencia de decisiones) y `CLAUDE.md`.
- Bitácora y propuestas: `SPEC.md` §1.5 (`.bitacora.jsonl`, `03-control/propuestas/`), §1.10.16 (nuevo) y §1.17;
  guía de `pm-estado-proyecto` (bitácora), guía de `pm-registros` y `guia-registros.md` (historial, reconocer y
  propuestas), guía de `pm-direccion-decisiones` (regla 12: sin deshacer), guía de `pm-exportar`
  (`--con-bitacora`), guía de `pm-sanidad`; `docs/SANIDAD.md` (familia BIT, guardián, casos BT y PR),
  `docs/SEGURIDAD.md`, `docs/CATALOGO.md`, `docs/TERMINOLOGIA.md` (bitácora de escrituras, propuesta con huella,
  reaplicación), `docs/ARQUITECTURA.md`, `docs/DEPENDENCIAS.md` (atribución de las ideas de exxperts), `docs/PRUEBAS.md`
  y `CLAUDE.md`.
- Correcciones de `decision.py`: guía de `pm-direccion-decisiones` §13.2 (ids de partida), §13.3 (regla con varias salidas
  importadas y `--fecha`), §13.5 (`--decision` con el nivel de su fila, `--revision`), §13.6 (`--corte`) y §13.10
  (`vigentes --ids` por `artefactos_afectados`; gate de BMAD en el reemplazo automático); SKILL.md (12.487 bytes); guía
  de `pm-riesgos` (nivel con `--decision`); `SPEC.md` §1.10.8; `docs/SEGURIDAD.md` §12; `docs/CATALOGO.md`;
  `docs/guias/README.md` (tabla de casos con los pasos, skills y gráficos actuales, incluidas matriz, vigencia,
  bitácora y propuestas) y el total de imágenes (61) en `correr.py`, `docs/PRUEBAS.md`, `docs/INDICE.md`,
  `docs/CATALOGO.md` y `docs/RESUMEN-EJECUTIVO.md`.
- **`docs/PM-KB.md`** (nueva): referencia técnica de pm-kb (qué es, arquitectura con los dos despliegues, qué se indexa y
  qué no, versiones, relaciones por ids, PostgreSQL con extensiones elegidas y descartadas, RLS y roles, instalación,
  configuración y credenciales, búsqueda, línea de comandos, web, MCP para Claude Code y Hermes, "Preguntar", pruebas y
  medición, seguridad, operación y limitaciones); diagrama `docs/diagramas/pm-kb.mmd`.
- **Guías de instalación con pm-kb**: `INSTALACION-WSL2` §8 (instalador, verificación, indexar, web, MCP en Claude Code y
  Hermes, modelos opcionales y proxy para pip en §8.9) e `INSTALACION-DOCKER` §8 (base segregada `pm-kb-db`, secretos,
  `up -d pm-kb`, tokens, web, MCP desde el contenedor `pm`, rotación de contraseñas, `down` y aviso sobre `down -v`);
  secciones siguientes renumeradas (WSL2 §9–§13, Docker §9–§15) y referencias corregidas en INSTALACION, DOCKER, INDICE,
  CLAUDE.md y el generador del Informe 2.
- pm-kb en el resto del paquete: DOCKER (perfil `kb`, imagen `pm-kb-db`, actualizar, seguridad, verificación y
  problemas), INSTALACION (credenciales de pm-kb), SEGURIDAD §14 con SEG-18 (estadísticas de BM25 que incluyen lo
  restringido) y SEG-19 (revocación con hasta 60 s de demora), DEPENDENCIAS §3.1 y §7.6 (licencias verificadas en PyPI y
  en los paquetes de Ubuntu), ARQUITECTURA §9.3, TERMINOLOGIA (BM25, RRF, RLS, unidad citada, versión vigente y aprobada,
  circulación, MCP), CATALOGO §5.4, PRUEBAS §7, INDICE, README, CLAUDE.md y AGENTS.md.
- Decisiones ↔ mapas: guías y SKILL.md de `pm-direccion-decisiones` (§13.1–13.3, 13.5, 13.8, 13.11 y 13.12) y de
  `pm-mapas-estrategicos`, guía y plantilla de estrategia de `pm-adquisiciones`, `SPEC.md` §1.10.15, `docs/SANIDAD.md`
  (MAP-01, caso MD), CATALOGO y TERMINOLOGIA (hacer o comprar).
- Frases de enrutamiento 131–134 y su prueba en vivo
  (`docs/evaluacion/resultados/2026-10-28-decisiones-v2.6.md`).

### Pruebas
- **Caso DC de `probar_paquete.py`** (16 comprobaciones): cálculo a mano (85/80/30, dominada), sensibilidad exacta de
  cada peso, umbral y margen, eliminatorio, errores de formato, abstención, pregunta tipada y respuestas inválidas o sin
  evidencia, `--elegir` con y sin motivo, nivel menor rechazado, sin duplicados, nivel de junta con `--decision`,
  expediente sin confidenciales y con tope, matriz de riesgo con el valor neto importado y `--elegir` vía `riesgos.py`,
  DEC-01 y DEC-02 y forma `nivel`. Caso Y: 37 scripts y 18 entradas faltantes.
- **Eslabón 4.7 de la integración cruzada**: riesgo decidido en 2.6, `inversion.py` de 4.3 e `impacto.py` de 4.5 →
  `decision.py expediente` con las cifras sin recalcular y el nivel de `impacto.py` → matriz con el VAN importado →
  `--elegir` de la ejecutiva → `decisiones.csv`, sanidad sin DEC.
- **Caso DR de `probar_paquete.py`** (9 comprobaciones): nivel de autoridad por roles y por palabras, RACI del
  expediente (1 salto, límites de palabra, confidencial sin valoración), `--motivo` exigido a quien no es el A ni
  autoridad superior, el A sin motivo, borrador del aviso a los I y `--sin-aviso`, incoherencia avisada, DEC-03 y DEC-04
  (hojas y D-###).
- **Eslabón 4.8 de la integración cruzada**: RACI de la cadena 3 → expediente con A, I y nivel → `--elegir` del gestor
  con `--motivo` → borrador del aviso a la I (`envios.py estado`, sin envíos) → sanidad sin DEC-03/DEC-04.
- **Caso BU de `probar_paquete.py`** (6 comprobaciones): lematizador, fechas y meses, cifras, ids, glosario inglés →
  español y las consultas de la prueba del informe exxperts ("enero 2027", "2027-01", "normativa", "39800",
  "delegaciones suspendidas", "business case").
- **Caso VG de `probar_paquete.py`** (12 comprobaciones): migración de columnas, `reemplaza` automático al aprobar
  v1.1, DEC-05 en las cinco reversiones del informe y sin sus falsos positivos, DEC-06 al corte (no con el asunto cerrado), autoridad (ni con
  `--forzar`), reemplazo doble, ciclo e id inexistente, `conviven`, `decision.py vigentes`, expediente con historia y
  `matriz --elegir --reemplaza`.
- **Eslabón 4.9 de la integración cruzada**: la decisión de negocio de 4.7 se reabre en una hoja nueva → el gestor no
  puede reemplazarla (rechazado antes de registrar) → la ejecutiva elige con `--reemplaza` → `decision.py vigentes` con
  la cadena → `expediente --tema` en inglés sobre filas en español trae la vigente y la otra como historia → sanidad sin
  DEC-05 ni DEC-06.
- **Caso BT de `probar_paquete.py`** (12 comprobaciones): líneas de `registro.py` y `estado.py` con altas, antes →
  después, claves y `--por`; stakeholders sin valores; cadena y continuidad; reescritura sin cambios; `historial`;
  BIT-02 (cambio fuera de los scripts y hueco entre líneas) y `reconocer`; 15 altas simultáneas encadenadas; BIT-01
  con una línea editada; `auditoria --con-bitacora` y `verificar` que explica el archivo alterado; guardián.
- **Caso PR de `probar_paquete.py`** (11 comprobaciones): proponer (huella, valores base, alias resuelto, registro
  intacto), propuesta inválida, autoaprobación rechazada, aplicar, listar con lo que pasaría hoy, reaplicar con la fila
  cambiada en otro campo, conflicto en un campo tocado, alta reaplicada con el id de hoy, rechazar, control de cambios
  que deja la propuesta pendiente e `historial P-###`.
- **Eslabón 5.10 de la integración cruzada**: bitácora de todas las escrituras de las cadenas 1–5 íntegra y sin cambios
  fuera de los scripts → el alta de cada decisión en `historial` → propuesta de un agente sobre un riesgo de 2.3
  reaplicada tras un cambio de la persona en la misma fila → `auditoria --con-bitacora` → `verificar`.
- **Caso DK de `probar_paquete.py`** (12 comprobaciones): ids del expediente en minúsculas, con punto y coma, sin fila
  propia e inexistentes; sección 4 con tabla, historia o "Ninguno"; `vigentes --ids` por `artefactos_afectados`;
  `--proponer --fecha` y fecha inválida; `pregunta --corte`; `--elegir --decision` de la junta con nivel junta en
  `riesgos.py` y en la hoja, `--revision` en `riesgos.csv`; `--decision` de nivel menor y `--revision` fuera de una hoja
  de riesgo rechazados; importados con nombre repetido, ref ambigua, ref calificada y criterio en conflicto; "ask" del
  guardián; gate de BMAD que reemplaza al anterior.
- **Caso MD de `probar_paquete.py`** (7 comprobaciones): ids `<mapa>:<id>`, sección 10 del expediente con Wardley y
  recorrido, faltantes, conjunto de criterios con nombre, `--criterios` inválido y cierre de MAP-01 y MAP-03 al elegir.
  **Eslabón 4.10 de la integración cruzada**: mapa con un componente "construir" en producto (MAP-01) → hoja de hacer o
  comprar → `--elegir` → la decisión queda citada y la sanidad sin MAP-01.
- **pm-kb**: `pm-kb/pruebas/probar_kb.py` (19 comprobaciones del núcleo sin base, con Python 3.9 o posterior, también
  como caso KB de `probar_paquete.py`; 46 con `--con-base`: BM25 en español, ids abreviados, vigente con aviso de la
  aprobada, `--aprobado`, historia, versiones y cambios, ficha con bitácora, tope de tokens, RLS por proyecto y
  circulación, tokens, MCP JSON-RPC y servicio web con CSP, origen y "Preguntar" sin modelo), `consultas_oro.py` (15
  consultas sobre el proyecto de E2E-1: 14/15 aciertos@5, MRR@5 0,75) y `conformidad_mcp.py` (SDK oficial `mcp` 2.3.0, el
  que fija Hermes Agent: protocolo 2025-11-25 por stdio y por HTTP). `pm-kb verificar` (14 comprobaciones de punta a
  punta) pasa en un Ubuntu 24.04 limpio con el instalador (PostgreSQL 16, pgvector 0.6.0; dos ejecuciones idénticas) y en
  el perfil `kb` de Docker (PostgreSQL 18.6, pgvector 0.8.1). Sesiones reales de Claude Code con el MCP por stdio y por
  HTTP responden con la cita correcta.
- Resultados del 2026-10-29 (`docs/PRUEBAS.md`): `probar_paquete.py` 463 OK · 0 FALLO con Python 3.13 y 462 OK con 3.9;
  integración cruzada 118 OK en 38 eslabones; los cinco recorridos E2E 5/5 OK (76 pasos, 61 imágenes) y deterministas
  en dos corridas con pm-kb (salvo la fecha del día en los nombres de los archivos exportados); 131 bloques Mermaid sin
  errores; `claude plugin validate .` sin errores.

## 2.5.1 · 2026-10-28 — escrituras concurrentes seguras

Versión de corrección: varias sesiones que escriben a la vez sobre la misma carpeta de proyecto (dos personas, un
gateway de Hermes con varios usuarios, un agente y un hook) ya no pierden filas ni repiten ids. No cambia formatos de
archivo, comandos, opciones ni salidas; sin dependencias nuevas (biblioteca estándar, Python 3.9+). Retrocompatible: un
proyecto creado con 2.5.0 se usa sin migración (la carpeta `.pm-bloqueo/` se crea en la primera escritura).

### Corregido
- **Pérdida de datos con escrituras simultáneas.** `registro.py agregar` leía el CSV, calculaba el siguiente id y
  reescribía el archivo entero sin coordinación ni reemplazo atómico (lo mismo `estado.json` con `estado.py`). Prueba de
  concepto del informe de base de conocimiento compartida, repetida antes del cambio: con **20 altas simultáneas** de
  `registro.py` sobre un proyecto nuevo, 17 a 20 procesos informaron éxito, solo 4 o 5 ids distintos, hasta 3 fallaron leyendo
  un archivo truncado y el CSV quedó con **2 o 3 filas**; con 3 altas simultáneas, una de tres corridas perdió una fila.
  Después: 20 de 20 (tres corridas), 3 de 3 (tres corridas) y 50 de 50, con ids únicos y consecutivos.
  - **Bloqueo por proyecto** (`esquema.bloqueo`): exclusivo, sobre `<proyecto>/.pm-bloqueo/bloqueo`, con `fcntl.flock`
    en POSIX (Linux, WSL2, Docker, macOS) y `msvcrt.locking` en Windows nativo; la carpeta lleva un `.gitignore` con `*`.
    Espera como máximo `PM_BLOQUEO_ESPERA` segundos (30 por defecto) y, si no lo obtiene, termina con código 1, un
    mensaje en español e inglés y nada modificado. Reentrante en el mismo proceso y heredado por los subprocesos que el
    titular espera (`puertas.py` → `sanidad.py`).
  - **Id dentro del bloqueo**: el registro se relee ya bloqueado antes de calcular el siguiente id.
  - **Escritura atómica** (`esquema.escribir_atomico`, `escribir_csv`, `escribir_json`): temporal oculto en la misma
    carpeta, `flush` + `fsync` y `os.replace`; mismos bytes que antes (codificación, CRLF de los CSV, `indent=2` sin
    salto final, orden de columnas) y mismos permisos. Si el proceso se interrumpe, el archivo anterior queda intacto.
  - Pasan por el mecanismo común todos los scripts que reescribían archivos de gobierno por su cuenta: `registro.py`
    (`agregar`, `actualizar`), `estado.py` (todo comando que modifica), `nuevo_proyecto.py`, `puertas.py` (`lista`,
    `confirmar` y `preparacion-bmad`, que escribía `estado.json` directamente), `bmad.py` (`estado.json`, `backlog.csv`,
    `avance-bmad.csv` y derivados de `especificacion/`), `interesados.py` (altas, `estereotipos --semilla`,
    `confirmar`, `rechazar`), `envios.py` (registro de envíos), `esquema.asegurar_registro` y `anotar_decision`;
    `especificacion.py` regenera `spec-index.json` de forma atómica. `lecciones.py`, `riesgos.py` y `extraccion.py` ya
    escribían a través de `registro.py`. El guardián no cambia: no protege ni confunde `.pm-bloqueo/` ni los temporales.
  - Qué no garantiza (`docs/ARQUITECTURA.md` §9.1): dos ramas o clones de git pueden seguir generando el mismo id;
    montajes de red sin `flock` coherente (aviso y escritura atómica sin exclusión); ediciones fuera de los scripts.

### Documentación
- `docs/ARQUITECTURA.md` §9.1 (nueva): escrituras concurrentes, scripts cubiertos, qué garantiza y qué no. `SPEC.md`
  §1.5 (carpeta `.pm-bloqueo/`) y §1.6 (regla de escritura para scripts nuevos). `docs/PRUEBAS.md`: caso CC y eslabón 5.9.
- Versión 2.5.1 en `plugin.json`, `compatibilidad.json`, `esquema.py`, las skills, `docker/`, el flujo de CI, el README y
  la documentación que cita la versión vigente. Los registros fechados (imagen Docker, pruebas en vivo, verificaciones de
  las guías de instalación) y el material generado (informe, resumen ejecutivo, webinar, `docs/ieee/`) conservan la
  versión con la que se hicieron.

### Pruebas
- **Caso CC de `probar_paquete.py`** (16 comprobaciones): 20 y 50 altas simultáneas en procesos separados, 30
  actualizaciones simultáneas de filas distintas, 12 escrituras simultáneas de `estado.json` (`presupuesto`, `set`,
  `tolerancia`, `rol`, `agil`, `integracion`, `umbrales-riesgo`), tiempo de espera agotado, interrupción entre el
  temporal y el reemplazo, reentrada, permisos, herencia hacia `sanidad.py`, `.pm-bloqueo/` fuera de git y guardián.
  Contra el código de 2.5.0, 10 de las 16 fallan.
- **Eslabón 5.9 de la integración cruzada**: 12 altas de riesgos, 6 de decisiones, `estado.py presupuesto` y `set` y
  `bmad.py avance` a la vez sobre una copia del proyecto integrado; ids únicos, `estado.json` sin pérdidas, sanidad sin
  ERROR nuevos.
- Resultados (2026-10-28): `probar_paquete.py` **372 OK · 0 FALLO** con Python 3.13 y **371 OK · 0 FALLO** con 3.9.25 (sin
  `matplotlib`); integración cruzada **105 OK · 0 FALLO en 35 eslabones** (100 en 33 con `--sin-e2e`); guías E2E 5/5 con
  evidencia idéntica a `docs/guias/evidencia/` salvo la fecha del día en los nombres de los archivos exportados y de
  traspaso, y 51 de 51 imágenes idénticas byte a byte; `validar_paquete.py` OK (también con el intérprete 3.9);
  `claude plugin validate .` pasa (avisos esperados sobre `CLAUDE.md` y el ícono). Las pruebas en vivo no se repitieron
  (no cambian descripciones, agentes ni hooks).

## 2.5.0 · 2026-10-27 — dos caminos de instalación (WSL2 y Docker) y diagram-design como motor opcional verificado

Versión que ordena cómo se instala y se verifica pm-method: dos caminos independientes, cada uno con su guía paso a paso
y sus comandos ejecutados tal cual (sobre WSL2 o Linux, con Claude Code o Hermes, o dentro de un contenedor Docker), y
diagram-design como motor opcional de diagramas reverificado, con una prueba de contrato que corre también dentro de la
imagen Docker. No cambia esquemas, registros, scripts del núcleo, descripciones de skills, agentes ni hooks (las skills
solo cambian el número de versión y la guía de pm-visuales, en la delegación a diagram-design). Retrocompatible: un
proyecto creado con 2.4.0 se lee sin migración, sin dependencias nuevas en el núcleo y sin escribir en BMAD.

En cifras: 39 skills (33 invocables por el modelo; listado de descripciones de 6.957 de 7.500 caracteres), 6 agentes,
3 hooks, 14 registros (9 base y 5 opcionales), 93 códigos de sanidad en 12 familias, 39 controles de puerta, 5 casos
E2E (74 pasos, 10 clases de 90 minutos, 51 imágenes), 195 diapositivas de contenido en los mazos del webinar y tres
guías de instalación (general, WSL2 y Docker).

### Agregado
- **Docker: etapa `skills-externas`** con diagram-design fijado por commit (solo la carpeta de la skill y sus
  licencias) y la variable `PM_DIAGRAM_DESIGN`, para que `pm-pruebas` corra el caso DD completo (ver «Pruebas»). El
  `git fetch` de diagram-design funciona detrás de un proxy con los `--build-arg` y el certificado como `--secret`, sin
  desactivar TLS.

### Cambiado
- **diagram-design reevaluado** (pm-visuales, guía §1.2 y §1.4). Se evaluaron diagram-design
  (`cathrynlavery/diagram-design`, MIT), su sitio `diagramdesign.dev` y ShowAI (`Renaissance-Mind/ShowAI`, MIT).
  diagram-design sigue como motor opcional que complementa a Mermaid: no sustituye a los generadores deterministas.
  ShowAI no se incorpora (ver `docs/INTEGRACIONES.md` §2). Cambios en la delegación a diagram-design:
  - La salida queda sin red, igual que las vistas internas: fuentes del sistema (sin Google Fonts) y verificación con
    `self_check.py --offline`, salvo que el usuario pida las tipografías web.
  - Versión verificada: 2.6.133, commit `66fa2e7` (antes 2.6.110, `550fd66`). Se reverificó en vivo con Claude Code
    2.1.311: organigrama delegado sin enlaces externos y `self_check.py --offline` OK.
- **Dos caminos de instalación separados**: instalación sobre WSL2 / Linux, o Docker. El README (instalación rápida,
  con un bloque por camino), `docs/INSTALACION.md` §1 y `docs/INDICE.md` presentan las dos vías con su guía; las dos
  guías se remiten entre sí y explican cuándo elegir cada camino (`INSTALACION-WSL2` §0 y §6.7, `INSTALACION-DOCKER`
  §0.1). `docs/DOCKER.md` queda como referencia técnica de la imagen y enlaza la guía de Docker.

### Corregido
- **Contrato con diagram-design** (guía de pm-visuales): la guía decía que se podía importar "la WBS u otro Mermaid".
  Solo se importan los respaldos `flowchart` (organigrama, PBS/WBS, flujo de productos y flujo de excepciones): el
  importador de diagram-design rechaza `quadrantChart`, `timeline` y `gantt` con código 2, así que el mapa
  poder/interés y el roadmap se dibujan desde la tabla intermedia.
- **Documentación de instalación**: el Python del README e INSTALACION §3.1 usa `python3 -m pip` con nota de PEP 668;
  INSTALACION §5 explica cómo activar el entorno virtual para scripts y hooks (antes [verificar]); DEPENDENCIAS ya no
  marca como obsoleta la instalación de Claude Code por npm.

### Seguridad
- **SEG-13 revisado** (`docs/SEGURIDAD.md`): `npm audit --package-lock-only` sobre `docker/node/` muestra desde el
  2026-10-27 **1 aviso alto y 1 moderado** en dependencias que `npm` 11.21.1 trae empaquetadas: `undici` 6.29.0
  (GHSA-2m5v-pch6-74hx, GHSA-xjj6-f33q-929c y GHSA-qrxm-fqhp-jwvm, altos; GHSA-4qv8-2p9j-2685 y GHSA-9fm3-97px-rjf6,
  moderados; corregidos en 6.29.1) e `ip-address` 10.7.2 (GHSA-rxp7-6hxx-x8q5, moderado; corregido en 10.7.4). **Ninguna
  versión publicada de `npm` los corrige todavía**: se regeneró el lockfile con 12.0.0, 12.1.0, 12.2.0 y 12.2.1 (la más
  reciente, del 2026-10-15, igual que 11.21.1) y todas traen `undici` ≤ 6.29.0 e `ip-address` ≤ 10.7.2; la serie 12
  exige además Node.js ^22.22.2 y la imagen tiene el 22.22.1 de Ubuntu 26.04. Se mantiene `npm` 11.21.1 y los dos avisos
  quedan **aceptados temporalmente** con su justificación: `undici` solo lo usa `node-gyp` para descargar las cabeceras
  de Node al compilar un complemento nativo (la imagen no trae compilador de C/C++) e `ip-address` solo se usa con un
  proxy `socks://`; `npm` solo sirve dentro del contenedor para `npx` (BMAD y skills externas). Se subirá `npm` cuando
  una versión publicada los corrija. Comprobado otra vez al cerrar la versión (2026-10-27): `npm view npm time` no
  muestra versiones posteriores a 11.21.1 y 12.2.1, y el lockfile regenerado con cada una da el mismo resultado de
  `npm audit` (1 alto, 1 moderado y 5 bajos). `docs/DOCKER.md` §2 y §10 dejan de marcarlo [verificar].

### Documentación
- **`docs/INSTALACION-DOCKER.md`** (nueva): el camino Docker paso a paso, para quien no programa. Opción 1, Docker
  Desktop para Windows con el *backend* WSL2 y la integración con Ubuntu; opción 2, Docker Engine dentro de Ubuntu en
  WSL2 con systemd. Los comandos de Docker se tomaron de la documentación oficial (fuente `docker/docs`, consultada el
  2026-10-27). Cubre obtener pm-method (clon o ZIP), construir la imagen, verificar con las pruebas y trabajar con un
  proyecto montado. También Claude Code dentro del contenedor: el inicio de sesión queda en el volumen
  `pm-method_claude-config` y la clave de API solo en la memoria de la terminal. Incluye BMAD, actualizar, solución de
  problemas (proxy y certificados en tres niveles, disco, UID, memoria, Chromium), desinstalar y verificación
  registrada. Sus comandos de Linux se ejecutaron tal cual, extraídos con un script, como usuario sin privilegios
  (§13). Quedan [verificar] Windows, Docker Desktop y la instalación de Docker Engine.
- **`docs/INSTALACION-WSL2.md`** (nueva): instalación en Windows con WSL2 y Ubuntu 24.04 LTS paso a paso, por Claude
  Code o Hermes, con la salida esperada de cada comando, lista de aceptación, solución de problemas y desinstalación;
  sus comandos se ejecutaron tal cual en una Ubuntu 24.04 limpia (§11).
- **Pendientes** (`docs/INDICE.md` §6): base de conocimiento del proyecto, recomendación evaluada (índice SQLite
  derivado de los registros, exportación opcional a Obsidian y, más adelante, un MCP propio de solo lectura), sin
  implementar por decisión del autor.
- **Informe 2 v2.5** (`docs/informe/informe-2-ecosistema-pm-method-v2.5.{html,pptx}`, reemplaza a la v2.4):
  314 diapositivas (307 en la v2.4). Diapositiva nueva «Instalación: WSL2 o Docker» (los dos caminos con su guía,
  cuándo elegir cada uno y lo verificado) y, en la sección de integraciones, diagram-design verificado (2.6.133) y ShowAI evaluado y no
  incorporado; el historial de versiones suma la 2.5.0 y conserva la tabla de la 2.4.0 tal como se publicó.
- **Resumen ejecutivo** regenerado: «Cómo empezar» presenta los dos caminos con su guía
  (`INSTALACION-WSL2` e `INSTALACION-DOCKER`) y las pruebas en vivo citan la serie con la que se hicieron (2.4). Spot:
  rótulo de versión y mosaico de cifras actualizados (sin regenerar la voz). Material del webinar regenerado (pies con
  la versión 2.5.0; el contenido no cambia) y presentaciones light de `docs/ieee/` (versión y cifras de calidad).
- Versión 2.5.0 en el README, la documentación que cita la versión vigente, `docker/` y el flujo de CI. Los registros
  fechados y los resultados en vivo conservan la versión con la que se hicieron.

### Pruebas
- **Caso DD de `probar_paquete.py`** (contrato con diagram-design). Comprueba siempre que lo que la guía declara
  importable tenga un respaldo de gramática soportada y que la receta use fuentes del sistema y `--offline`. Con
  `PM_DIAGRAM_DESIGN=<carpeta skills/diagram-design>` comprueba además la versión instalada: importación de la WBS de
  `wbs.py` y de los 8 bloques de la plantilla Mermaid, y `self_check.py --offline` con y sin Google Fonts.
- **Imagen Docker `pm-method:2.5.0` reconstruida y verificada** (`docs/DOCKER.md` §10, 2026-10-27): construida desde
  cero como en §11.1 (base Ubuntu 26.04 con `debootstrap`, proxy como `--build-arg`, certificado como `--secret` y Chromium con
  `--build-context`), **2,99 GB** (752 MB de contenido comprimido); `pm-pruebas` sin red, como usuario sin privilegios:
  `Resultado: todas las pruebas OK` en 15 min, con `probar_paquete.py` **358 OK · 0 FALLO** (Python 3.14, caso DD
  completo con diagram-design `66fa2e7`), recorridos E2E 5/5, integración cruzada 98 OK en 34 eslabones, 128 bloques
  Mermaid y webinar 5/5. Los pasos de `docs/INSTALACION-DOCKER.md` que dependen de la imagen se repitieron con ella
  (§13). §11.1 indica además quitar de la base los paquetes y las listas de `apt` que deja `debootstrap`.
- Resultados de la versión (2026-10-27): `probar_paquete.py` **355 OK · 0 FALLO** con Python 3.13 y **354 OK · 0 FALLO**
  con 3.9.25 (sin `matplotlib`); caso DD con `PM_DIAGRAM_DESIGN` (diagram-design `66fa2e7`) **5 OK** con 3.13 y con 3.9;
  integración cruzada **99 OK · 0 FALLO** en 34 eslabones (94 en 32 con `--sin-e2e`); `validar_mermaid.py --render`:
  **128** bloques, 0 errores; guías E2E **5/5 OK** dos veces, con evidencia e imágenes idénticas a las de `docs/guias/`
  (salvo la fecha del día en los nombres de los archivos exportados y de traspaso); `webinar/generar.py --todos
  --validar` 5/5 sin errores (195 diapositivas de contenido, 125 términos) y `documentos.py --todos` 5/5 (15 HTML, 18
  diagramas Mermaid); `claude plugin validate .` pasa con Claude Code 2.1.312 (aviso esperado sobre `CLAUDE.md`). Las
  pruebas en vivo no se repitieron (las últimas son de la 2.4.0, 21 y 22/10/2026; esta versión no cambia descripciones,
  agentes ni hooks).

## 2.4.0 · 2026-10-22 — decidir con opciones, impacto antes del cambio, radar diario y ciclo completo de las lecciones

Versión que convierte en controles repetibles actividades que en la práctica se hacen a mano o una sola vez: comparar
opciones de respuesta a los riesgos y dejar listo el plan de contingencia, medir el impacto de un cambio antes de
decidirlo, saber cada día qué hay que decidir, escalar, desbloquear y vigilar, armar el highlight y el tablero desde un
solo cálculo del período, derivar el estado de los productos de los registros, extraer de las reuniones lo acordado con
cita, aprender de otros proyectos y cerrar el ciclo de las lecciones, estimar con tres valores y priorizar contra la
capacidad del release y las personas de usuario. Retrocompatible: un proyecto creado con 2.3 se migra al leerse (las
columnas nuevas de `lecciones.csv` se agregan al final con la primera escritura y `personas.csv` se crea al primer
uso), sin dependencias nuevas en el núcleo y sin escribir en BMAD.

En cifras: 39 skills (33 invocables por el modelo; listado de descripciones de 6.957 de 7.500 caracteres), 6 agentes,
3 hooks, 14 registros (9 base y 5 opcionales), 93 códigos de sanidad en 12 familias, 39 controles de puerta, 5 casos
E2E (74 pasos, 10 clases de 90 minutos, 51 imágenes) y 195 diapositivas de contenido en los mazos del webinar.

### Agregado
- **Opciones de respuesta y plan de contingencia** (pm-riesgos). `riesgos.py opciones`: para los riesgos abiertos con
  P×I ≥ umbral alto (`estado.json.umbrales_riesgo.alto`; `--umbral N`, `--riesgo R-###`) lee la hoja de opciones
  `03-control/registros/opciones-riesgo/R-###.csv` (evitar, reducir, transferir, compartir si aplica, contingencia y
  aceptar), valida montos y la escala 1–5, calcula el EMV residual (con la contingencia ponderada por la probabilidad) y
  el valor neto = EMV inherente − EMV residual − EMV secundario − costo, ordena (bajo la línea primero) y marca la
  recomendada sin decidir; `--proponer` crea la plantilla sin pisar una existente; salida de texto acotada (`--max`) y
  `--json`. PUERTA HUMANA `opciones --riesgo R-### --elegir O# --por "<rol: nombre>"`: sin `--por` no registra; si no es
  la recomendada exige `--motivo`; con `registro.py` escribe respuesta, residual, disparador y acciones en `riesgos.csv`
  y la decisión con las opciones consideradas en `decisiones.csv` (o cita `--decision D-###`). Plantilla
  `templates/plan-contingencia.md` (`03-control/registros/R-###-plan-contingencia.md`): disparador medible, acciones,
  propietario y ejecutor, monto y fuente (presupuesto de riesgo), quién lo activa, registro de la activación
  (`cambios.csv` con `cargo=reserva-riesgo` y el R-###: CAM-02, CAM-03) y plan alternativo. Sanidad **REG-10** (aviso):
  amenaza alta con respuesta y menos de dos opciones evaluadas, o con respuesta `aceptar`/`contingencia` sin disparador
  o sin plan de contingencia. PRINCE2 2.c.4, R-10, R-12, R-14 y R-15; PMBOK 8 §3.11.
- **Personas de usuario y mapa capacidad × persona** (pm-interesados). Registro opcional `personas.csv` (prefijo
  **PU**, se crea al primer uso): arquetipo (`nombre`, `descripcion`), `objetivo`, `dolores`, `contexto_uso`, `fuente`
  (`entrevista`, `bmad-uj`, `encuesta`, `observacion`, `documento`, `supuesto`), `evidencia`, `stakeholder_id`
  (interesado que la representa, validado), las capacidades en `solicita`, `usa` y `beneficia` (ids de requisitos,
  épicas, historias o productos de la WBS) y `beneficios` (`B-##`/`DB-##`); estado `activa|retirada`; alias
  `interview`, `survey`, `observation`, `active`, `retired`. No es un interesado ni un estereotipo de comunicación.
  `interesados.py personas candidatos [--desde auto|bmad|artefactos] [--limite 40] [--json]` propone personas desde los
  recorridos UJ-n de BMAD (solo lectura: persona, objetivo, contexto, FR que realizan el UJ, B-## cuyos KPI SM-n
  coinciden), desde los recorridos de `pm-mapas-estrategicos` y desde las historias «Como <rol>, quiero…» del backlog;
  sugiere el representante y el comando `registro.py` para registrar o completar cada una, sin registrar nada solo.
  `personas mapa [--json]` (capacidad × persona con S solicitante, U usuario, B beneficiario y la prioridad MoSCoW) y
  `personas priorizacion [--json]` (por persona: capacidades por prioridad, rol, representante y beneficios; JSON listo
  para barras apiladas); la prioridad sale de `requisitos.md` o de `backlog.csv`, y un requisito o una épica sin
  prioridad propia toma la más alta de sus historias. Sanidad, familia STK (solo si existe `personas.csv`; aviso):
  **STK-13** requisito o épica Must sin persona que lo pida, use o aproveche, **STK-14** persona sin capacidades,
  **STK-15** persona sin fuente o con fuente distinta de `supuesto` y sin evidencia, **STK-16** recorrido cuya persona no
  está registrada; STK-09 y STK-03 cubren también los ids y el representante que cita una persona. `mapas.py …
  recorrido semilla --persona PU-###` toma nombre, descripción, objetivo y contexto de la persona y deja `persona_id` en
  el mapa. PRINCE2 §3.1.3, §3.2.1, §4.5.2 y §4.3.2; PMBOK 8 §2.2.b.2.
- **Radar de atención y briefing de incorporación** (pm-estado-proyecto, pm-orquestador, pm-progreso-reportes).
  `estado.py radar [--corte] [--max 5] [--json | --linea]`, de solo lectura, agrupa lo pendiente en **decidir**
  (cambios `pendiente-decision` con quién decide según el límite y el presupuesto delegados, puertas pendientes,
  condiciones abiertas, excepción abierta, issues y riesgos escalados, supuestos críticos SUP-01…03, contingencias por
  activar), **escalar** (TOL-01, CAM-03 agotado, CAM-04, CAM-05, riesgos con respuesta `escalar` sin escalar),
  **desbloquear** (acciones vencidas, issues sin responsable, riesgos altos sin respuesta o propietario, dependencias,
  QUA-02/03) y **vigilar** (REG-09, bloqueos de la próxima puerta, presupuesto al 80 %, EVM en ámbar o sin corte
  reciente, supuestos en validación); cada ítem con regla (RAD-01…RAD-08), id, fecha, responsable, siguiente paso y
  prioridad 1–4, orden reproducible y línea «Hoy». Reutiliza `estado.py contexto`, los controles de `sanidad.py`, el
  último EVM guardado, `puertas.py` y los presupuestos y tolerancias de `estado.json`. `estado.py briefing [--para
  ST-###] [--corte] [--salida RUTA|-] [--json]` llena `pm-progreso-reportes/templates/briefing-incorporacion.md`
  (≤ 6.500 caracteres): contexto, rol y RACI del interesado con sus ítems del radar, decisiones de nivel junta, riesgos
  altos, issues y cambios pendientes con quién decide, último EVM, artefactos aprobados, próxima puerta y próximos
  pasos, cada cifra con su id o archivo y sin poder ni interés de un interesado confidencial. PRINCE2 §5.4, §4.c.2 y §7.3.
- **Datos del período → tablero y highlight desde el dato** (pm-progreso-reportes, pm-visuales, pm-estado-proyecto).
  `estado.py periodo --desde AAAA-MM-DD [--corte] [--proximo] [--juicio J.json] [--json] [--tablero [RUTA]]
  [--highlight [RUTA] [--forzar]]`: un solo cálculo del período para el highlight y el tablero. Siete objetivos con
  semáforo por regla (tiempo y costo del último corte de EVM del período; riesgo con `estado.json.umbrales_riesgo`;
  calidad con QUA-01…03 o un fuera de especificación abierto; alcance con el EVM ágil) o por juicio marcado del gestor
  (alcance predictivo, beneficios, sostenibilidad), estado general = el peor; productos aceptados, cambios, fuera de
  especificación, acciones vencidas y próximas, decisiones e iteraciones del período. El juicio puede empeorar un
  semáforo derivado, nunca mejorarlo. `--tablero` escribe `03-control/reportes/<corte>-tablero-avance.html` con un
  escape único del bloque de datos (todo `<` como `<`) y lo registra `tablero-avance`; `--highlight` escribe el
  borrador de la variante mínima con cifras, ids y `puertas.py estado` y deja `[por redactar]` la narrativa, sin pisar
  uno existente ni uno aprobado. `periodo --verificar INFORME`: cada cifra rotulada del EVM coincide con el corte
  guardado al redondeo citado y ningún semáforo con regla es mejor que el derivado; código 1 si algo difiere. PRINCE2
  §4.c.3 y §4.c.6.
- **Estado de productos derivado y controles de cierre por id** (pm-paquetes-trabajo, pm-calidad, pm-cierre-proyecto).
  `estado.py productos [--corte] [--fuente auto|backlog|wbs] [--alcance …] [--max 40] [--json | --markdown [RUTA]]`, de
  solo lectura: el registro de productos de PRINCE2 7 (A13) derivado de `backlog.csv` o de `wbs.csv`, `calidad.csv`,
  `issues.csv`, las aceptaciones de `estado.json` y los paquetes de trabajo, sin registro nuevo; estado por producto en
  un orden documentado con su Q-### y su aceptación, conteos que suman el total, diferencias entre lo registrado y lo
  físico con el control que las vigila (QUA-01…04) y Must sin aceptar; `--markdown` escribe el borrador del product
  status account sin pisar uno aprobado. Sanidad **QUA-04** (aviso, con `wbs.csv`): elemento de la WBS aceptado o con
  su paquete recibido sin revisión aprobada que lo cite. `puertas.py`, `autorizar-cierre`: **C-03** comprueba cada
  issue y riesgo abierto por id en `recomendaciones-seguimiento` (con responsable) y lista los faltantes; **C-07**
  (condición) lista los requisitos e historias Must cuyo estado derivado no es aceptado ni con concesión.
- **Inteligencia de reuniones** (pm-reuniones). `extraccion.py candidatos --transcripcion F [--reunion] [--fecha]
  [--tipo retrospectiva|planificacion|seguimiento|otra] [--max 20] [--json]`: desde la transcripción (normalizada, VTT,
  SRT o TXT) propone, oración por oración y con cita, hablante y `[hh:mm:ss]`, decisiones tomadas y pendientes (CD) con
  su nivel de decisión, compromisos (CA) con responsable y fecha, supuestos (CS), riesgos (CR, vía `riesgos.py`) e
  instrucciones incrustadas (IN, que se informan y nunca se registran); en una retrospectiva, lecciones candidatas (CL)
  y acciones de mejora (CM). Frases marcadoras deterministas en español e inglés; borrador
  `03-control/reuniones/<fecha>-<reunion>-candidatos.md` y `.json`. PUERTA HUMANA `extraccion.py registrar --candidatos
  J --confirmar <ids> --por "<rol: nombre>" [--campo ID:col=valor] [--simular]`: sin opción «todos»; valida todo antes
  de escribir con `registro.py` (las decisiones de nivel junta, ejecutivo o capa de negocio las registra pm-director);
  un candidato ya registrado se omite y una transcripción cambiada pide volver a proponer. PRINCE2 §3.c.1, §4.d y A13.
- **Análisis de impacto de cambios** (pm-issues-cambios). `impacto.py analizar C-### [--actividades … --pert]
  [--flujos …] [--puntos --release …] [--evm] [--costo --cargo] [--tol-dias] [--json]`: tabla de impacto (alcance y
  especificación, tiempo y camino crítico con `cpm.py`, reserva de cronograma, capacidad del release, tiempo de la
  etapa, alcance del EVM ágil, costo y BAC, presupuesto de cambio con la regla de CAM-03, autoridad, VAN y margen del
  beneficio principal con `inversion.py`, persona afectada, riesgos y calidad que citan lo afectado) y borrador
  `03-control/reportes/<fecha>-solicitud-cambio-C-###.md` con opciones aprobar, rechazar, diferir o pedir plan de
  excepción y quién decide. No escribe registros. PRINCE2 §3.c.1–§3.c.3 y §4.c.2; PMBOK 8 §2.1.b.8.
- **Expediente de auditoría** (pm-exportar). `paquete.py auditoria [--desde] [--hasta] [--proposito] [--externo]
  [--salida] [--extra]`: `INDICE.md` e `INDICE.html` (escapado), `cronologia.csv` (puertas con su D-### y la lista
  confirmada, decisiones, cambios decididos, riesgos aceptados, productos aceptados y envíos), `estado.json`, registros,
  líneas base congeladas, evidencia de puertas, actas, informes, cortes de EVM, comunicaciones, hallazgos de sanidad al
  corte, `MANIFIESTO.md` y `SHA256SUMS`; rutas externas excluidas; `--externo` sin el registro de interesados ni los
  destinos de envíos. `paquete.py verificar <zip>` recalcula cada sha256 (alterados, faltantes, agregados; código 1).
  PRINCE2 §3.c.4, §4.d y A13.
- **Lecciones entre proyectos y ciclo completo de las lecciones** (pm-lecciones-aprendidas, pm-reuniones,
  pm-agil-hibrido). `lecciones.py buscar (--en DIR … | --indice CSV …) [--texto] [--categoria] [--etiqueta] [--para
  <proceso>] [--max] [--json] [--exportar CSV]`, de solo lectura, devuelve las lecciones aprobadas de otros proyectos o
  de un índice exportado con su referencia `<proyecto>:L-###`; `incorporar --proyecto … --ids …` muestra la vista previa
  y solo con `--confirmar --por "Rol: Nombre"` las registra como lecciones previas con `origen`. Ciclo con `--por`:
  `clasificar` (impacto alto, medio o bajo y proceso en `aplicar_en`), `accionar` (en el proyecto exige
  `--verificar-en`), `verificar --resultado efectiva|no-efectiva --evidencia` y `descartar --motivo`; `listar --para
  <proceso>`; `informe --proyecto … [--etapa N] [--corte] [--exportar INDICE.csv --por …]` escribe el informe de
  lecciones desde el registro y alimenta el índice de la organización que consulta `buscar --indice`. Retrospectiva
  como reunión propia en `extraccion.py` (lecciones CL y acciones de mejora CM) y plantilla de retrospectiva qué
  funcionó · qué no funcionó · qué probamos. Controles: **E-11** (aviso en `autorizar-etapa`: lecciones de
  `planificacion` abiertas sin acción), **REG-11** (lección de impacto alto sin acción ni decisión) y **REG-12**
  (accionada con `verificar_en` vencida o de impacto alto sin fecha). PRINCE2 §2.2, §4.d, §5.6 y §5.7; PMBOK 8
  §2.1.b.6 y §3.13.
- **Estimación de tres valores y capacidad del release** (pm-cronograma-estimacion, pm-agil-hibrido). `cpm.py`:
  `actividades.csv` acepta al final `optimista`, `mas_probable` y `pesimista` (0 ≤ O ≤ M ≤ P); con ellas la duración es
  tE redondeada hacia arriba y `duracion` puede quedar vacía; `--distribucion beta|triangular` (por defecto beta-PERT)
  con las dos fórmulas rotuladas según la referencia del paquete (triangular = fórmula de la Guía; beta-PERT = práctica
  habitual), `--confianza k` (reserva k·σ, por defecto 2) y `--estimacion RUTA`, que escribe el archivo que lee
  `impacto.py --pert`; la salida muestra tE y σ por actividad, σ del camino crítico, reserva y fin con reserva, y el
  Gantt Mermaid la reserva como sección. `release.py capacidad [--release R] [--velocidad N] [--must-max 60] [--json]`
  (solo lectura): por release, capacidad = velocidad × iteraciones, puntos Must, Should y Could, holgura, Must /
  capacidad contra la regla práctica de ≤ 60 %, lectura (excepción, repriorizar, entran Must y Should, entra todo),
  historias para dividir, ítems sin MoSCoW o sin puntos y Won't con release; `impacto.py --puntos --release` usa la
  misma función.
- **Ficha promocional del taller** por caso E2E: `python3 scripts/webinar/generar.py --todos --ficha` lee
  `docs/webinar/E2E-N/ficha.json` (título centrado en el problema, destinatarios, 3–5 objetivos con verbo observable,
  qué hace el agente, qué decide la persona y el control humano, beneficios para la persona y la organización sin
  promesas de ROI, temas por clase, requisitos, modalidad, convocatoria opcional, una imagen real de `docs/guias/img/` y
  notas del orador) y escribe `E2E-N-ficha.pptx` (2 diapositivas con notas, modo `--ficha` de `pptx.js`) y
  `E2E-N-ficha.html` (volante autocontenido, claro/oscuro, una página A4 al imprimir), con el recuadro «Logo IEEE» o
  `--logo`. El título y la duración de cada clase salen de `diapositivas.json`; la validación da errores claros por campo
  faltante, cantidad o largo fuera de rango, clase que no coincide e imagen inexistente, y avisos por verbos no
  observables o promesas de ROI. `documentos.py` enlaza las fichas en `docs/webinar/index.html` («Para difundir») y
  las copia con `--salida`. Prueba: caso L3 de `probar_paquete.py`.

### Cambiado
- `lecciones.csv` suma al final `origen`, `etiquetas`, `impacto`, `recurrencia`, `aplicar_en` (multivalor que
  `registro.py` normaliza, con alias en inglés, y REG-05 valida), `accion`, `verificar_en` y `verificacion`, y el estado
  `verificada`; REG-08 no revisa las filas con `origen` (citan ids de su proyecto). REG-08 incluye el prefijo PU,
  REG-01 trata `personas.csv` como opcional y el guardián y la guía de registros (§7.5) suman el registro nuevo.
- Regla por defecto del paquete: la provisión para riesgos no identificados va a la reserva de gestión, que solo libera
  la junta (`estado.py presupuesto … gestion=<monto> --por …`; su uso es un cambio con `cargo=reserva-gestion`, CAM-05),
  y el presupuesto de riesgo financia las respuestas y contingencias de los riesgos identificados (respuestas + EMV
  residual). Configurable en el enfoque de riesgo §7 («Provisión para riesgos no identificados · Destino»:
  `reserva-gestion` por defecto o `presupuesto-riesgo`, nunca los dos). PRINCE2 7 §2.b R-18 y §2.c.6; PMBOK 8 §2.4.a y
  §2.7.a.
- El hook de inicio agrega una línea de radar por proyecto (totales y primer id de cada grupo, sin texto libre de los
  registros) que remite a `pm-orquestador`; la tabla de enrutamiento del orquestador y su secuencia «Radar del día» lo
  usan ante «¿qué decido hoy?» o al retomar la sesión.
- `registro.py`: la regla de autoridad y presupuesto de cambio queda en la función `motivos_autoridad` (misma conducta y
  mensajes), que `impacto.py` usa para decir quién decide antes de pedir la decisión.
- Fachada sin BMAD (`especificacion.py`): en `requisitos.md`, Interesado, Categoría, Prioridad y Estado se leen por el
  encabezado de la tabla; sin encabezado reconocible, por la posición de la plantilla. El índice expone `interesado`.
- `cpm.py --json` escribe solo el JSON (los avisos de Gantt y MSPDI escritos se omiten) y suma `estimacion`.
  `impacto.py --pert` toma la σ de la distribución declarada en el archivo y `--confianza k`, y aplica la misma
  distribución a las actividades con tres valores de los escenarios.
- `release.capacidad` no cuenta épicas ni ítems descartados o retirados en BMAD.
- QUA-01 y el estado de productos aceptan la clave corta seguida de punto («historia 1-2.»).
- El tablero de avance sale de `estado.py periodo --tablero` en lugar de la receta que el modelo reescribía (guía de
  `pm-visuales` §3), con los umbrales de riesgo de `estado.json`; `guias_e2e/comun.py: tablero()` llama al script con el
  juicio de cada caso.
- Descripciones de skills: `pm-riesgos` con «plan de contingencia», `pm-interesados` con las personas de usuario,
  `pm-orquestador` con «qué decido hoy, radar», `pm-progreso-reportes` con «briefing de incorporación», `pm-reuniones`
  con «compromisos, acuerdos, meeting decisions», `pm-exportar` con «expediente de auditoría, audit pack» y
  `pm-lecciones-aprendidas` con «lecciones de otros proyectos»; agentes pm-inicio, pm-planificacion, pm-control y
  pm-cierre con los pasos nuevos.

### Corregido
- `pm-cronograma-estimacion`, regla 7: la beta-PERT figuraba como fórmula de la Guía PMBOK; queda rotulada como práctica
  habitual (la Guía cita la triangular).
- Guía E2E-2: el driver redondeaba tE con `round()` de Python (al par: 10,5 → 10 y 8,5 → 8), distinto de la regla de
  `cpm.py` (decimales hacia arriba). Con `cpm.py --estimacion` como única fuente, la línea base es de 112 días (fin
  2027-05-05) y C-001 la lleva a 123 (fin 2027-05-20); sin cambio en el camino crítico, la reserva a 2σ (13,0 días), los
  +11 días de C-001, los 2,0 días de reserva remanente ni las capacidades (R1 47 de 48, R2 21 de 24).
- `docs/PUERTAS.md` §3 documenta el control B-00 (BMAD declarado y no legible) y `docs/SANIDAD.md` lista `personas` entre
  los registros opcionales de REG-01.

### Documentación
- `docs/ieee/`: dos presentaciones light para miembros de IEEE (PPTX y HTML autocontenido, claro u oscuro, imprimible): resumen
  de 5 diapositivas con el programa de formación propuesto (14 sesiones de 90 min = 21 h; piloto de 4 a 6 sesiones) y
  resumen del Informe 2 en 9 diapositivas; siglas explicadas en un recuadro, imágenes reales de las guías E2E y
  generador reproducible (`fuente/preparar.py` verifica el programa contra `docs/webinar/`).
- SKILL.md y guías de las skills involucradas: `pm-riesgos` (paso 6, regla 7, guía §1, §4 y §5), `pm-interesados`
  (paso 4b, regla 2b, guía §13), `pm-mapas-estrategicos` y `pm-planificacion-por-productos` (personas),
  `pm-estado-proyecto` (§6, §9 y §10), `pm-orquestador` (§4), `pm-progreso-reportes` (§11, §13 y §14, regla 12),
  `pm-visuales` (§3), `pm-paquetes-trabajo` (§5 y plantilla del product status account), `pm-calidad` (§5 y §8.1),
  `pm-cierre-proyecto` (§4 y §5), `pm-reuniones` (§3.1, §5 y §7), `pm-issues-cambios` (§3.1 y plantilla de solicitud de
  cambio), `pm-exportar` (§3.1), `pm-lecciones-aprendidas` (§1, §4, §6–§8, §11 y §12), `pm-agil-hibrido` (§5, §6 y
  plantilla de retrospectiva), `pm-cronograma-estimacion` (§1–§3, §7 y §8; plantillas `actividades.csv` y
  `hoja-estimacion.md`), `pm-enfoques-gestion` (enfoque de riesgo §7, plan de cronograma y costos §2),
  `pm-costos-presupuesto` (§2 y §3), `pm-mandato-y-brief`, `pm-plan-etapa-y-limites` y `pm-sanidad`.
- SPEC §1.5, §1.9, §1.10.3, §1.10.6, §1.10.8, §1.10.9, §1.10.11, §1.16 y §1.17; `docs/SANIDAD.md`, `docs/PUERTAS.md`,
  `docs/CATALOGO.md`, `docs/TERMINOLOGIA.md`, `docs/PRUEBAS.md`, `docs/INSTALACION.md` §9, `docs/INDICE.md`, README,
  CLAUDE.md, AGENTS.md y el resto de `docs/` con las cifras de esta versión.
- Casos E2E (guía, evidencia, imágenes y material del webinar): **E2E-1** opciones de respuesta por valor neto y
  decisión del propietario (paso 6a, `g1-opciones-valor-neto.png`), plan de contingencia (paso 6b) activado en el
  paso 13, presupuesto de riesgo de 39.800 (respuestas 7.300 + EMV residual 32.500) con la provisión de 6.200 como
  reserva de gestión de la junta, intacta al cierre de la etapa con la reserva de riesgo al 94 %, y radar en la
  revisión periódica (paso 12); **E2E-2** tres valores y reserva con `cpm.py --estimacion` (paso 3), capacidad del
  release y personas de usuario con STK-13 (paso 4, `g2-capacidad-release.png`) y análisis de impacto de C-001 y C-002
  con `impacto.py` (pasos 7 y 10, `g2-impacto-c002.png`); **E2E-3** candidatos del taller con cita y confirmación
  (paso 8, `g3-candidatos-reunion.png`), radar y briefing al retomar (paso 10a, `g3-radar.png`) y highlight y tablero
  desde `estado.py periodo` con la cadena de reporte verificada (paso 10b); **E2E-4** radar al retomar la sesión,
  estado de productos derivado (paso 6), retrospectiva y ciclo de las lecciones (pasos 6c a 9,
  `g4-lecciones-ciclo.png`), cierre verificado por id con C-03 y C-07 (paso 9, `g4-cierre.png`) y expediente de
  auditoría verificado (paso 9b, `g4-expediente.png`); **E2E-5** lecciones previas del índice de la red (paso 1),
  línea del radar al retomar y radar después de la puerta (pasos 7 y 14) y personas de usuario con capacidad × persona
  en las dos variantes (pasos 10b y 16b, `g5-personas-mapa.png`, `g5-personas-mapa-bmad.png`). Tablas de los casos en
  `docs/guias/README.md` y `docs/webinar/README.md`; mazos, guías, guiones y ejercicios en HTML regenerados.
- Fichas promocionales del taller de los cinco casos (`docs/webinar/E2E-N/ficha.json` y sus PPTX y HTML generados):
  E2E-1 «Que el registro de riesgos no muera después del taller», E2E-2 «Cada cambio, con su impacto medido antes de
  decidir», E2E-3 «Que lo prometido a cada interesado se cumpla, y se note a tiempo», E2E-4 “Del «done» al beneficio
  medido: gobernar un producto hecho con BMAD” y E2E-5 «¿Vale la pena? Validar la idea antes de invertir y diseñar el
  proyecto»; esquema, validaciones y criterios en `docs/webinar/README.md` («Ficha promocional del taller») y
  `docs/INDICE.md`.
- Frases de enrutamiento 103 a 130 en `docs/evaluacion/frases-enrutamiento.tsv` (130 en total).
- `docs/CASOS-DE-USO.md` parte 7 (casos 50 a 59): cada capacidad con su frase verificada en vivo, la skill y el script,
  la decisión humana y el paso de la guía E2E donde se recorre. `docs/SEGURIDAD.md` §11: revisión de los scripts que
  leen fuentes externas (sin hallazgos nuevos de severidad alta ni media). Mazo de E2E-3: la RACI resuelta como tabla
  en lugar de la captura alta del reporte de interesados.
- Informe 2 en `docs/informe/` (`informe-2-ecosistema-pm-method-v2.4.html` y `.pptx`, 307 diapositivas; reemplazan a los
  de 2.3): en la sección 2, una diapositiva por capacidad nueva con la figura de su guía E2E y, para opciones, radar,
  cadena de reporte, estado de productos y cierre, reuniones e impacto, la salida real de la evidencia; controles
  REG-10, REG-11, REG-12, E-11, STK-13…16, QUA-04, C-03 y C-07 en la tabla de controles permanentes; parte 7 de los
  casos de uso; pruebas en vivo de 2.4.0; glosario y tabla «antes y después» de 2.4.0 (la de 2.3.0 queda como se
  publicó). `extraer.py` cuenta los pasos como `docs/guias/README.md` y se detiene si no coinciden, toma las figuras de
  cualquier paso de las guías y las salidas de `docs/guias/evidencia/`.
- Resumen ejecutivo (`docs/resumen-ejecutivo/`, 18 diapositivas) regenerado con las cifras de 2.4.0: opciones de
  respuesta (REG-10), cierre por id (C-07) y ciclo de las lecciones (REG-11, REG-12) en la tabla del problema, y los
  casos E2E con las capacidades de 2.4.0 y sus imágenes (opciones por valor neto, impacto de C-002, highlight desde el
  dato, cierre y expediente de auditoría, personas de usuario). Spot (`docs/resumen-ejecutivo/spot/`): rótulo v2.4.0 y
  mosaico de cifras actualizados, sin regenerar la locución.

### Pruebas
- `probar_paquete.py`: **353 OK · 0 FALLO** con Python 3.13; **352 OK · 0 FALLO** con Python 3.9 (sin `matplotlib` se
  omite una comprobación de visuales). Casos nuevos: I2 (opciones y plan de contingencia, 7 comprobaciones), PU
  (personas, 9), RD (reuniones, 13), IM (impacto, 7), TV (tres valores y capacidad, 9), AU (expediente de auditoría, 7),
  RA (radar y briefing, 15), LX (lecciones entre proyectos, 9), LC (ciclo de las lecciones, 16), PE (datos del período,
  tablero y highlight, 8) y PS (estado de productos y cierre por id, 13); el caso Y cubre el `--help` de 34 scripts.
- Integración cruzada (`scripts/pruebas/integracion/correr.py`): eslabones nuevos 2.5 (tablero, highlight y
  `--verificar` sobre el EVM), 2.7 (comité → candidatos → registro), 4.4 (personas desde los UJ de BMAD y STK-13), 4.5
  (cambio + CPM, presupuestos y opciones → impacto), 4.6 (tres valores → `impacto.py --pert`; backlog → capacidad del
  release), 5.4 (expediente y verificación), 5.5 (radar y briefing), 5.6 (lecciones entre proyectos), 5.7 (ciclo de las
  lecciones) y 5.8 (estado de productos, QUA-04 y C-07): **99 OK · 0 FALLO en 34 eslabones** de las seis
  cadenas (94 OK en 32 eslabones sin la cadena de los recorridos E2E, también con Python 3.9).
- Recorridos E2E (`guias_e2e/correr.py`): 5/5 con los scripts reales, evidencia e imágenes idénticas en dos corridas
  seguidas. `validar_mermaid.py --render`: **128** bloques, 0 errores. `generar.py --todos --validar` y
  `documentos.py --todos --validar`: 5/5 sin errores.
- Imagen Docker `pm-method:2.4.0` reconstruida y verificada el 2026-10-22 (`docs/DOCKER.md` §10, construida como en
  §11.1): 2,99 GB (748 MB comprimida); dentro del contenedor, sin red, `pm-pruebas` completo en ≈ 14 min con todo OK
  (`probar_paquete.py` 346 OK · 0 FALLO con Python 3.14, recorridos E2E 5/5, integración 98 OK · 0 FALLO en 34
  eslabones con `--e2e`, 128 bloques Mermaid, `generar.py` y `documentos.py` 5/5), `claude plugin validate` y el flujo
  de usuario (proyecto nuevo, sanidad, `estado.py radar` y tablero) con archivos del host de dueño `1000:1000`.
- En vivo con Claude Code real (2026-10-21 y 2026-10-22): opciones y contingencia 2/2
  (`docs/evaluacion/resultados/2026-10-21-enrutamiento-contingencia-v2.4.md`); personas 3/3
  (`…/2026-10-21-enrutamiento-personas-v2.4.md`); radar, briefing y lecciones entre proyectos 12/12
  (`…/2026-10-21-radar-onboarding-lecciones-v2.4.md`); reuniones, impacto y auditoría 6/6 y 8/8 de regresión
  (`…/2026-10-21-reuniones-impacto-auditoria-v2.4.md`); ciclo de las lecciones 4/4 y 10/10 de regresión
  (`…/2026-10-21-lecciones-ciclo-v2.4.md`); estado de productos y cierre 2/2
  (`…/2026-10-22-estado-productos-cierre-v2.4.md`); período, highlight y tablero 4/4
  (`…/2026-10-22-periodo-highlight-tablero-v2.4.md`); tres valores y capacidad 2/2
  (`…/2026-10-22-tres-valores-capacidad-v2.4.md`).

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
