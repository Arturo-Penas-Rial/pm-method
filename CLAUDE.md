# CLAUDE.md · contexto para desarrollar pm-method

Este repositorio **es** el plugin pm-method (no un proyecto que lo usa). Leer esto antes de cambiar algo.

## Qué es
Plugin de Claude Code (también Cowork y Hermes) con 6 agentes, 39 skills y 3 hooks para gestión de proyectos (versión 2.7.0).
Jerarquía fija, no negociable:
1. **PRINCE2 7** = método y ciclo de vida; **siempre manda**.
2. **PMBOK 8** = solo el "cómo" (técnicas) o vacíos de PRINCE2.
3. **Plantillas** (libro de Snyder) = artefactos (campos, listas), destiladas en palabras propias, nunca texto literal.
4. **BMAD** = capa de especificación de **solo lectura**, fuente única por dato (`especificacion.py`, `bmad.py`).
Bilingüe ES/EN: responder en el idioma del usuario; artefactos en `estado.json.idioma`.

## Reglas del autor (obligatorias)
- Exactitud ante todo: no inventar fuentes, URLs, comandos, flags, funciones ni cifras; verificar con `--help`, el
  código o la fuente; marcar `[verificar]` lo no verificado; preguntar ante vacíos.
- Documentación en español (con resúmenes "EN:" donde ayude).
- Nunca agregar marca o logo de empresa alguna (los informes llevan espacio para el logo de IEEE).
- Nunca escribir credenciales en archivos, commits ni mensajes.

## Mapa del repositorio
- `.claude-plugin/` plugin.json y marketplace.json (versión: debe coincidir con `compatibilidad.json` y
  `skills/pm-estado-proyecto/scripts/esquema.py: VERSION_PAQUETE`; `validar_paquete.py` lo comprueba).
- `agents/` orquestador + pm-director + 4 subagentes de fase. Sin `tools` (heredan MCP), `disallowedTools: Agent`.
- `skills/<skill>/` SKILL.md (≤ 12.500 bytes y ≤ 200 líneas), `references/guia.md`, `templates/`, `scripts/`.
- `skills/pm-estado-proyecto/scripts/` núcleo: `esquema.py` (esquemas, valores, migración, bloqueo, escritura atómica y bitácora `.bitacora.jsonl`), `vigencia.py` (vigencia y contradicciones de decisiones: `reemplaza`, `conviven`, DEC-05/06), `texto.py` (normalización para buscar en español e inglés: lemas, fechas, cifras, ids), `estado.py` (también
  `contexto`, `radar` y `briefing` de incorporación, `periodo`: datos del período → tablero y highlight con la cadena de
  reporte verificada, y `productos`: estado de productos derivado de los registros), `registro.py` (con
  `motivos_autoridad`; `historial` y `reconocer` de la bitácora, BIT-01/02; propuestas con huella `proponer`,
  `propuestas`, `aprobar --por`, `rechazar` en `03-control/propuestas/`), `especificacion.py`, `sanidad.py`, `puertas.py` (verificación de puertas, también C-03 y C-07
  por id), `wbs.py`, `cpm.py` (también tres valores, `--estimacion` y reserva k·σ), `evm.py`, `exportar.py`,
  `nuevo_proyecto.py`, `tablero.py` (tablero `pm-tablero/1` en JSON o HTML con CSP por hash, también por actor
  `--actor`; `congelar`, `listar`, `comparar`; `estado.py puerta` y `cierre --prematuro` congelan el tablero previo a la
  decisión en `03-control/reportes/tableros/`; API pública `construir`, `actores`, `filtrar_actor` que usa pm-kb; SPEC
  §1.10.17).
- `skills/pm-bmad-puente/scripts/bmad.py` puente BMAD. `skills/pm-interesados/scripts/interesados.py` maestro de
  interesados (matriz, estereotipos, preferencias, perfil, RACI, personas de usuario y capacidad × persona, integridad,
  reporte, plan de envío; `sanidad.py` lo usa para la familia STK). `skills/pm-integraciones/scripts/envios.py` capa de canales (SMTP, webhooks de Slack o Teams,
  `.eml`, MCP; credenciales solo por variables de entorno). `skills/pm-okr/scripts/okr.py` OKR y check-ins.
  `skills/pm-caso-de-negocio/scripts/inversion.py` VAN, TIR, repago, sensibilidad y equilibrio por opción.
  `skills/pm-mapas-estrategicos/scripts/mapas.py` mapas de Wardley y de recorrido (familia MAP de la sanidad).
  `skills/pm-riesgos/scripts/riesgos.py` riesgos candidatos desde BMAD, transcripciones, tracker y artefactos, y
  `opciones` (valor neto de las opciones de respuesta y elección del propietario con `--por`).
  `skills/pm-lecciones-aprendidas/scripts/lecciones.py` ciclo de las lecciones (clasificar, accionar, verificar; REG-11, REG-12, E-11), informe
  desde el registro con índice de la organización, y lecciones aprobadas de otros proyectos (solo lectura) e incorporación con `origen`.
  `skills/pm-reuniones/scripts/extraccion.py` candidatos de decisiones, compromisos, supuestos y riesgos de una transcripción
  y, en una retrospectiva, lecciones y acciones de mejora (registra solo lo confirmado). `skills/pm-issues-cambios/scripts/impacto.py` análisis de impacto de un C-### y borrador
  de la solicitud. `skills/pm-agil-hibrido/scripts/release.py` capacidad del release por MoSCoW (función compartida
  con `impacto.py`). `skills/pm-exportar/scripts/paquete.py` también arma el expediente de auditoría (`auditoria`, `verificar`).
  `skills/pm-direccion-decisiones/scripts/decision.py` decisiones con contexto para seis tipos (riesgo, negocio,
  planificación, OKR, cambio, adquisición): `expediente` (contexto aplicable con fuente, sin confidenciales, con tope),
  `matriz` de la hoja `03-control/decisiones/<ID>/` (suma ponderada, eliminatorios, dominadas, sensibilidad, empates;
  `--elegir … --por` registra con `registro.py` o `riesgos.py`; RACI ↔ autoridad: `--motivo` si no decide el A, borrador del
  aviso a los I con `plan-envio`) y `pregunta` tipada con `--validar`; `vigentes` (decisiones vigentes y su cadena de reemplazos; el expediente solo trae vigentes y `--tema` busca con `texto.py`); DEC-01…06 en sanidad. `esquema.nivel_autoridad`:
  nivel de decisión de una persona (roles de `estado.json` por nombre o palabras del rol).
- `hooks/` guardian.py, inicio.py, idioma.py, py.sh, hooks.json.
- `scripts/validar_paquete.py`, `scripts/probar_paquete.py`, `scripts/validar_mermaid.py`, `scripts/instalar_hermes.py`.
- `scripts/pruebas/fixtures/` (BMAD v6 sintético, 6.12.4 real, v4), `scripts/pruebas/guias_e2e/` (recorridos de
  `docs/guias/`: `g1.py`…`g5.py`, `comun.py`, `visuales.py` y `correr.py`, con `--comparar docs/guias/evidencia`,
  `--python` y `--conservar`), `scripts/pruebas/integracion/` (suite de integración cruzada, `correr.py`),
  `scripts/pruebas/variantes/` (suite de variantes, `docs/PRUEBAS.md` §2.5: `correr.py --nivel …`, `ciclo.py` recorrido
  paramétrico, `matriz.py` celdas pairwise y manifiesto de omisiones, `integraciones.py`, `contratos.py`, `hermes.py`,
  `migracion.py`, `opcionales.py` pm-kb con modelos simulados, `probar_kb.py`/`pantallas.py` y skills externas,
  `portal.py` el portal de pm-kb con pm-method (instantáneas, «actualizar ahora» en solo lectura, propuestas, enlaces
  compartidos, inglés, `pm-kb enlaces`), `simuladores.py` servidores que imitan TEI y las API de modelos,
  `sitio/sitecustomize.py` bloqueador de imports), `scripts/pruebas_vivo/` (Claude Code real;
  consume tokens).
- `scripts/webinar/` material del webinar: `generar.py` y `pptx.js` (diapositivas PPTX y HTML desde
  `docs/webinar/E2E-N/diapositivas.json`; con `--ficha`, la ficha promocional del taller desde `ficha.json`) y
  `documentos.py` (guía, guion y ejercicio con el ejemplo resuelto plegado, en HTML, e índice `docs/webinar/index.html`).
- `docker/` entorno Docker opcional (`Dockerfile`, `compose.yaml`, `requirements.txt` y `node/` con versiones fijadas,
  `pm-pruebas.sh`; etapa `skills-externas` con diagram-design fijado por commit para el caso DD); documentado en
  `docs/DOCKER.md` (referencia técnica).
- `pm-kb/` componente **opcional** (no es skill ni agente; fuera del plugin), índice de conocimiento en PostgreSQL con
  búsqueda citada; referencia en `docs/PM-KB.md` (los docstrings citan sus §). Piezas:
  - `pm-kb` lanzador (entorno propio y `~/.config/pm-kb/pm-kb.env` sin secretos) · `pmkb/cli.py` subcomandos y `verificar`.
  - `pmkb/config.py` variables `PMKB_*` y conexión (inicia el clúster local si hace falta) · `pmkb/esquema.sql` esquema, RLS y roles.
  - `pmkb/fuentes.py` formatos, unidades, exclusiones (interesados, comunicaciones), circulación y confianza.
  - `pmkb/versiones.py` documentos, vigente/aprobada, duplicados y cambios · `pmkb/relaciones.py` aristas por ids.
  - `pmkb/enlaces.py` ids estables → ubicación vigente, movimientos, citas a rutas que no existen y la acción de
    pm-method sugerida (`pm-kb enlaces`).
  - `pmkb/indexador.py` carga en una transacción · `pmkb/busqueda.py` BM25 en SQL, sinónimos (`pmkb/sinonimos.py`), ids, RRF y re-ranqueo opcionales.
  - `pmkb/tablero.py` publica el tablero del núcleo (`tablero.py generar --json`, solo lectura) y sus instantáneas, poda
    por circulación, filtro por actor con la API del núcleo, resumen de la cartera · `pmkb/documentos.py` documentos HTML
    del proyecto (motor, SVG/PNG, ruta dentro de la carpeta, CSP aislada).
  - `pmkb/formato.py` salida con cita · `pmkb/modelos.py` clientes HTTP de modelos opcionales.
  - `pmkb/mcp.py` MCP propio de solo lectura (stdio y HTTP) · `pmkb/web.py` portal con token y enlaces compartidos ·
    `pmkb/estatico/` (`index.html` con `comun.js`, `app.js` y `tablero.js`; `compartido.html` y `compartido.js` para
    un enlace compartido; `ingresar.html`, `estilo.css`, Cytoscape.js 3.34.3).
  - `db/pg.sh` PostgreSQL de los dos caminos · `instalar-wsl.sh` · `requirements.txt` (hash) y `regenerar_requisitos.py`.
  - `pruebas/` `probar_kb.py [--con-base]`, `pantallas.py` (portal en Chromium), `consultas_oro.py`,
    `conformidad_mcp.py`, `fixture.py` y `proyecto_tablero.py` (proyectos de prueba), `esquema-2.sql` y `esquema-3.sql`
    (migraciones). Docker: `docker/pm-kb-db.Dockerfile`, `docker/kb-preparar.sh` y perfil `kb` de `docker/compose.yaml`
    (`pm-kb-db`, `pm-kb`, `pm-kb-vigilar`); WSL2: `docs/servicios/pm-kb-vigilar@.service` (`vigilar` como servicio de usuario).
- Guías de instalación, dos caminos separados: `docs/INSTALACION-WSL2.md` (Windows con WSL2 y Ubuntu, por Claude Code o
  Hermes) y `docs/INSTALACION-DOCKER.md` (Docker Desktop o Docker Engine sobre WSL2); `docs/INSTALACION.md` es la guía
  general (credenciales, BMAD, skills externas, MCP, verificación). Sus comandos se ejecutan tal cual y lo verificado
  queda en su sección de verificación (INSTALACION-WSL2 §12 e INSTALACION-DOCKER §14): si cambia un comando o una salida esperada, volver a ejecutarlos.
- `docs/guias/` cinco casos E2E con `evidencia/` e `img/` (salen de `guias_e2e/correr.py`; nunca dejar PNG ni carpetas
  temporales fuera de `img/`); `docs/webinar/E2E-N/` guion, ejercicio y diapositivas por caso;
  `docs/resumen-ejecutivo/` (con el spot), `docs/informe/` y `docs/ieee/` (versiones breves para público no especialista)
  presentaciones con su generador en `fuente/`; `docs/evaluacion/`
  frases de enrutamiento y resultados en vivo.
- `SPEC.md` convenciones canónicas (claves de artefactos, registros, niveles de decisión, presupuestos).
- Registros: 9 base y 5 **opcionales** que se crean al primer uso (`estereotipos` ET, `preferencias` PF, `raci` RC,
  `envios` EN, `personas` PU), con claves foráneas, unicidad y "uno por" declarados en `esquema.py` (`opcional`, `refs`, `unico`,
  `uno_por`) y validados por `registro.py`. Un registro nuevo debe sumarse también a `hooks/guardian.py`,
  `pm-registros/templates/guia-registros.md` y `SPEC.md` §1.10.8.

## Convenciones de código
- Python 3.9+, solo biblioteca estándar en el núcleo (pyyaml, python-docx, openpyxl opcionales con mensaje claro).
- Referencias a scripts: en SKILL.md y references `${CLAUDE_SKILL_DIR}/../pm-X/scripts/…`; en agentes y hooks
  `${CLAUDE_PLUGIN_ROOT}/skills/pm-X/scripts/…`. Ninguna variable se expande en archivos leídos con Read ni en Hermes.
- `estado.json` y registros CSV solo se escriben con `estado.py` / `registro.py` (el hook lo impone también en pruebas
  manuales); toda escritura nueva pasa por `esquema.escribir_csv|escribir_json|escribir_atomico` para quedar en la
  bitácora (SPEC §1.10.16). Nada escribe en `_bmad/`, `_bmad-output/` ni `.bmad-core/`.
- Descripciones de skills: formato "… Usar: … No: …→skill", ≤ 240 caracteres; listado total ≤ 7.500 caracteres.
- Mensajes de scripts bilingües con `E.t(idioma, es, en)` cuando el usuario los lee.

## Flujo de trabajo para cada cambio
1. Leer la sección relevante (`grep -n`), no archivos enteros.
2. Cambiar el código y, si cambia una conducta, agregar una prueba en `scripts/probar_paquete.py`.
3. `python3 scripts/validar_paquete.py` → OK; `python3 scripts/probar_paquete.py` → 0 FALLO (también con Python 3.9,
   `docs/PRUEBAS.md` §2.4; `--casos A,E` para repetir solo lo afectado); `python3 scripts/pruebas/integracion/correr.py`;
   `python3 scripts/pruebas/variantes/correr.py --nivel todo` → 0 FALLO, sin trazas y omisiones = manifiesto (antes de una
   versión, `--repetir 2`; `docs/PRUEBAS.md` §2.5); `claude plugin validate .`;
   si se tocó un diagrama: `python3 scripts/validar_mermaid.py --render` (y revisar legibilidad con `--png DIR`); si
   cambió una salida que muestran las guías: `scripts/pruebas/guias_e2e/correr.py --salida <tmp> --comparar docs/guias/evidencia`
   (muestra el diff normalizado) dos veces, y copiar la evidencia y las imágenes que cambien a `docs/guias/` (y las cifras a
   guías y `docs/webinar/`).
4. Si cambian descripciones, agentes, hooks o el texto de inicio: `python3 scripts/pruebas_vivo/suite.py enrutamiento
   --ids <afectados>` (consume tokens) y, antes de una versión, `suite.py todo`.
5. Actualizar `CHANGELOG.md`, la documentación afectada (`docs/INDICE.md` lista todo) y, si corresponde, la versión en
   los tres lugares.
6. Commit con mensaje descriptivo; una rama y PR por cambio grande.

## Probar como usuario
```bash
claude --plugin-dir . -p "/pm-method:pm-ayuda"                 # sin instalar
python3 scripts/pruebas_vivo/vivo.py --cwd /tmp/demo "¿qué sigue?"
```
Proyecto de prueba con BMAD real: copiar `scripts/pruebas/fixtures/bmad-v6.12-real` y correr
`skills/pm-estado-proyecto/scripts/nuevo_proyecto.py --ruta gestion --nombre Demo` dentro de la copia.

## Pendientes conocidos
Ver la sección "Pendientes" de `docs/INDICE.md` y los ítems `[verificar]` de la documentación.
