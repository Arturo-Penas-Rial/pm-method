# Cambios · Changelog

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
