# Cambios · Changelog

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
