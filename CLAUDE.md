# CLAUDE.md · contexto para desarrollar pm-method

Este repositorio **es** el plugin pm-method (no un proyecto que lo usa). Leer esto antes de cambiar algo.

## Qué es
Plugin de Claude Code (también Cowork y Hermes) con 6 agentes, 39 skills y 3 hooks para gestión de proyectos (versión 2.4.0).
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
- `skills/pm-estado-proyecto/scripts/` núcleo: `esquema.py` (esquemas, valores, migración), `estado.py` (también
  `contexto`, `radar` y `briefing` de incorporación, `periodo`: datos del período → tablero y highlight con la cadena de
  reporte verificada, y `productos`: estado de productos derivado de los registros), `registro.py` (con
  `motivos_autoridad`), `especificacion.py`, `sanidad.py`, `puertas.py` (verificación de puertas, también C-03 y C-07
  por id), `wbs.py`, `cpm.py` (también tres valores, `--estimacion` y reserva k·σ), `evm.py`, `exportar.py`,
  `nuevo_proyecto.py`.
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
- `hooks/` guardian.py, inicio.py, idioma.py, py.sh, hooks.json.
- `scripts/validar_paquete.py`, `scripts/probar_paquete.py`, `scripts/validar_mermaid.py`, `scripts/instalar_hermes.py`.
- `scripts/pruebas/fixtures/` (BMAD v6 sintético, 6.12.4 real, v4), `scripts/pruebas/guias_e2e/` (recorridos de
  `docs/guias/`: `g1.py`…`g5.py`, `comun.py`, `visuales.py` y `correr.py`), `scripts/pruebas/integracion/` (suite de
  integración cruzada, `correr.py`), `scripts/pruebas_vivo/` (Claude Code real; consume tokens).
- `scripts/webinar/` material del webinar: `generar.py` y `pptx.js` (diapositivas PPTX y HTML desde
  `docs/webinar/E2E-N/diapositivas.json`; con `--ficha`, la ficha promocional del taller desde `ficha.json`) y
  `documentos.py` (guía, guion y ejercicio con el ejemplo resuelto plegado, en HTML, e índice `docs/webinar/index.html`).
- `docker/` entorno Docker opcional (`Dockerfile`, `compose.yaml`, `requirements.txt` y `node/` con versiones fijadas,
  `pm-pruebas.sh`); documentado en `docs/DOCKER.md`.
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
  manuales). Nada escribe en `_bmad/`, `_bmad-output/` ni `.bmad-core/`.
- Descripciones de skills: formato "… Usar: … No: …→skill", ≤ 240 caracteres; listado total ≤ 7.500 caracteres.
- Mensajes de scripts bilingües con `E.t(idioma, es, en)` cuando el usuario los lee.

## Flujo de trabajo para cada cambio
1. Leer la sección relevante (`grep -n`), no archivos enteros.
2. Cambiar el código y, si cambia una conducta, agregar una prueba en `scripts/probar_paquete.py`.
3. `python3 scripts/validar_paquete.py` → OK; `python3 scripts/probar_paquete.py` → 0 FALLO (también con Python 3.9,
   `docs/PRUEBAS.md` §2.4); `python3 scripts/pruebas/integracion/correr.py`; `claude plugin validate .`;
   si se tocó un diagrama: `python3 scripts/validar_mermaid.py --render` (y revisar legibilidad con `--png DIR`); si
   cambió una salida que muestran las guías: `scripts/pruebas/guias_e2e/correr.py --salida <tmp>` dos veces, y copiar la
   evidencia y las imágenes que cambien a `docs/guias/` (y las cifras a guías y `docs/webinar/`).
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
