# Índice de la documentación y las pruebas · pm-method 2.7.0

Mapa de todo lo que hay en el repositorio para entenderlo rápido. EN: *documentation and test map.*

## 1. Rutas de lectura por perfil

| Perfil | Leer en este orden | Tiempo aproximado |
|---|---|---|
| Decisor / patrocinador | [RESUMEN-EJECUTIVO](RESUMEN-EJECUTIVO.md) → diagramas del [README](../README.md) → [PRUEBAS §3.1](PRUEBAS.md) → [PILOTO](PILOTO.md) | 20 min |
| Gestor de proyectos (usuario) | [INSTALACION](INSTALACION.md) (en Windows, uno de los dos caminos: [INSTALACION-WSL2](INSTALACION-WSL2.md) o [INSTALACION-DOCKER](INSTALACION-DOCKER.md)) → [guías E2E](guias/README.md) (probar como usuario, por prompts) → [PRUEBAS §6](PRUEBAS.md) (aceptación) → [CASOS-DE-USO](CASOS-DE-USO.md) → [CASO-MAESTRO](CASO-MAESTRO.md) | 2–4 h |
| Equipo de producto con BMAD | [PUERTAS](PUERTAS.md) → [sincronizacion](sincronizacion.md) → [CASOS-DE-USO-INTEGRACIONES §7](CASOS-DE-USO-INTEGRACIONES.md) → [SANIDAD](SANIDAD.md) (familia ESP) | 45 min |
| Responsable de comunicación con interesados | [guía E2E-3](guias/E2E-3-interesados-okr-avance.md) (15 pasos: matriz, preferencias, RACI, OKR, envío por canales, cadencia de contacto STK-12) → [CATALOGO: pm-interesados](CATALOGO.md) → [colisiones](colisiones.md) (qué frase va a cada skill) → `skills/pm-interesados/references/guia.md` | 1 h |
| Quien integra herramientas | [DEPENDENCIAS](DEPENDENCIAS.md) → [INTEGRACIONES](INTEGRACIONES.md) → [CASOS-DE-USO-INTEGRACIONES](CASOS-DE-USO-INTEGRACIONES.md) → [INSTALACION §6](INSTALACION.md) | 1 h |
| Junta, PMO o aseguramiento (controles permanentes) | [SANIDAD §2.1](SANIDAD.md) (familias CAM, QUA, TOL y SUP, REG-09 a REG-12 y STK-12) → [PUERTAS §3](PUERTAS.md) (condiciones formales, G-01, P-11, E-11, C-03 y C-07) → radar del día (`estado.py radar`, [CASOS-DE-USO caso 52](CASOS-DE-USO.md)) → expediente de auditoría ([caso 59](CASOS-DE-USO.md)) → tablas "Del uso único al control continuo" de las [guías E2E](guias/README.md) → [CASOS-DE-USO caso 48](CASOS-DE-USO.md) | 45 min |
| Formador o facilitador | [guías E2E](guias/README.md) → [webinar](webinar/README.md) (guion, ejercicio, diapositivas y ficha promocional del taller por caso; `webinar/index.html` enlaza las versiones HTML para presentar, repartir o difundir) → [TERMINOLOGIA](TERMINOLOGIA.md) | 1 h por caso |
| Quien mantiene el paquete | [CLAUDE.md](../CLAUDE.md) → [ARQUITECTURA](ARQUITECTURA.md) → [SPEC.md](../SPEC.md) → [colisiones](colisiones.md) → [PRUEBAS](PRUEBAS.md) | 2 h |

## 2. Documentos

| Documento | Qué responde |
|---|---|
| [README](../README.md) | qué es, diagramas, instalación rápida, componentes, dependencias, calidad verificada |
| [RESUMEN-EJECUTIVO](RESUMEN-EJECUTIVO.md) | por qué usarlo: problema, capacidades, valor diferencial, evidencia, límites |
| [INSTALACION](INSTALACION.md) | cómo instalar y configurar todo (plugin, credenciales y API-KEY §0.7, Orca opcional §0.8, Python, BMAD, skills externas, MCP, Cowork, Hermes), verificar y resolver problemas |
| [INSTALACION-WSL2](INSTALACION-WSL2.md) | Windows con WSL2 paso a paso, para quien no programa: requisitos de Windows, Ubuntu 24.04 LTS, `.wslconfig` y `wsl.conf`, git, Python en un entorno virtual, navegador para capturas, Node con nvm, Mermaid y pptxgenjs, y luego Claude Code (plugin, inicio de sesión, BMAD) o Hermes; opcionales paso a paso (envío a interesados por `.eml`, correo, Slack o Teams; skills externas de visuales y Office; conectores MCP; pm-kb y sus modelos); comprobación con la salida esperada en cada paso, lista de aceptación, solución de problemas (proxy y certificados, DNS, reloj, PATH, CRLF, disco), desinstalación y verificación registrada |
| [INSTALACION-DOCKER](INSTALACION-DOCKER.md) | el camino Docker paso a paso, separado de la instalación sobre WSL2, para quien no programa: elegir entre Docker Desktop (backend WSL2 e integración con Ubuntu) y Docker Engine dentro de Ubuntu (systemd, repositorio oficial, grupo `docker`), obtener pm-method (clon o ZIP), construir la imagen, verificar con las pruebas, trabajar con un proyecto montado, Claude Code dentro del contenedor (inicio de sesión en un volumen, plugin con `--plugin-dir`), BMAD, opcionales paso a paso (pm-kb y sus modelos, envío a interesados, skills externas, conectores MCP), actualizar (también pm-kb), solución de problemas (proxy y certificados, disco, UID, memoria, Chromium), desinstalar, lista de aceptación y verificación registrada |
| [DOCKER](DOCKER.md) | referencia técnica del entorno Docker: qué incluye y con qué versiones, construir (argumentos, redes cerradas), servicios y credenciales, pruebas sin red, actualizar las versiones fijadas, seguridad del contenedor, limitaciones y verificación registrada de la imagen |
| [PM-KB](PM-KB.md) | pm-kb, el índice de conocimiento opcional: qué indexa y qué excluye, versiones de documentos, relaciones por ids, PostgreSQL (esquema, extensiones, RLS y roles), instalación en los dos caminos, configuración y credenciales, búsqueda (BM25, sinónimos, híbrida opcional), línea de comandos, web, MCP para Claude Code y Hermes, "Preguntar", pruebas y medición, seguridad, operación y limitaciones |
| [DEPENDENCIAS](DEPENDENCIAS.md) | cada dependencia con nivel, uso, versión probada, licencia, URL de origen y cómo se verificó |
| [ARQUITECTURA](ARQUITECTURA.md) | capas, precedencia PRINCE2/PMBOK, agentes vs subagentes, carga progresiva, presupuesto de descripciones, escrituras concurrentes (§9.1), tablero del proyecto y lecturas sin escritura (§9.5), portal de pm-kb (§9.6) |
| [INTEGRACIONES](INTEGRACIONES.md) | qué repositorio se integró y por qué, contratos, verificación en vivo, cómo agregar una integración |
| [sincronizacion](sincronizacion.md) | fuente única por dato, fachada `pm-spec-index/1`, líneas base, traspaso a BMAD |
| [SANIDAD](SANIDAD.md) | catálogo de los 104 códigos en 15 familias: INS, EST, ART, REG (con REG-09, revisión de riesgos vencida; REG-10, opciones y plan de contingencia; REG-11 y REG-12, lecciones sin acción o sin verificar), ESP, INT, STK (maestro de interesados y personas de usuario), las de controles permanentes CAM (cambios contra presupuestos), QUA (calidad a volumen, con QUA-04 sobre la WBS), TOL (pronóstico contra tolerancias) y SUP (supuestos críticos), MAP (mapas de Wardley y de recorrido, solo avisos), DEC (hojas de decisión, RACI y vigencia de decisiones, solo avisos) y BIT (bitácora de escrituras, solo avisos); `--corte` |
| [RACI](RACI.md) | quién decide, quién produce y quién registra, por rol humano, agente y skill |
| [CATALOGO](CATALOGO.md) | las 39 skills: disparadores, artefactos, agente, scripts |
| [TERMINOLOGIA](TERMINOLOGIA.md) | equivalencias PRINCE2 7 · PRINCE2 en español · PMBOK en español · uso habitual, skill que responde y frase verificada en vivo |
| [colisiones](colisiones.md) | dueños únicos de cada artefacto y pistas de alcance entre skills |
| [CASOS-DE-USO](CASOS-DE-USO.md) | un caso por skill a lo largo del ciclo de vida; parte 6 (casos 38 a 49): maestro de interesados, canales, OKR, riesgos desde cuatro fuentes, controles permanentes (caso 48) y mapas (caso 49); parte 7 (casos 50 a 59): opciones de respuesta, personas, radar, reuniones, impacto, tres valores, datos del período, estado de productos, ciclo de las lecciones y expediente de auditoría, cada uno con su paso en las guías E2E |
| [CASOS-DE-USO-INTEGRACIONES](CASOS-DE-USO-INTEGRACIONES.md) | un caso por repositorio integrado: diseño visual, reportes, planificación, OKR, reuniones, trackers, BMAD |
| [CASO-MAESTRO](CASO-MAESTRO.md) | proyecto completo con BMAD, con prompts del usuario, comandos y salidas reales |
| [guias/](guias/README.md) | cinco guías de punta a punta por prompts, con reporte y gráficos: [riesgos](guias/E2E-1-riesgos.md), [alcance, cambio, esfuerzo, priorización y roadmap](guias/E2E-2-alcance-roadmap.md), [interesados, comunicaciones, OKR y avance](guias/E2E-3-interesados-okr-avance.md), [producto de la idea al producto con BMAD](guias/E2E-4-producto-bmad.md), [de la idea al proyecto diseñado](guias/E2E-5-idea-a-proyecto.md); 74 pasos en total (15, 10, 14, 15 y 20), dos clases de 90 minutos por caso, cada guía con su tabla "Del uso único al control continuo"; evidencia reproducible en `guias/evidencia/` y 57 imágenes en `guias/img/` |
| [PRUEBAS](PRUEBAS.md) | niveles de prueba, qué cubre cada una (incluidas la integración cruzada, la compatibilidad con Python 3.9 y los presupuestos de contexto medidos en vivo), resultados registrados y lista de aceptación |
| [PUERTAS](PUERTAS.md) | qué se verifica en cada puerta (salud, controles PRINCE2 y BMAD, lista de control de la junta), cómo se registra la decisión y cómo se siguen sus condiciones hasta cumplirse (G-01, `cumplir-condiciones`); tablero congelado en cada puerta (§2.1); diagrama del ciclo de vida PRINCE2 + BMAD |
| [PILOTO](PILOTO.md) | plan de piloto en paralelo: fases, métricas, rúbrica de revisión experta, prueba de usabilidad, criterios de decisión |
| [SEGURIDAD](SEGURIDAD.md) | revisión de seguridad para quien instala: alcance, herramientas, modelo de amenazas, hallazgos con severidad y estado, buenas prácticas y cómo reportar una vulnerabilidad |
| [CHANGELOG](../CHANGELOG.md) | cambios por versión |
| [SPEC.md](../SPEC.md) | especificación de construcción y convenciones canónicas |
| [CLAUDE.md](../CLAUDE.md) · [AGENTS.md](../AGENTS.md) | cómo seguir desarrollando el paquete con agentes de código |
| [ieee/](ieee/README.md) | presentaciones light para miembros de IEEE sin jerga de gestión de proyectos (PPTX + HTML, con notas del orador): resumen de 5 diapositivas (qué resuelve, cómo trabaja, ventajas, programa de formación propuesto de 14 sesiones de 90 min y piloto de 4 a 6 sesiones) y resumen del Informe 2 en 10 diapositivas (con decidir con evidencia y buscar con la fuente citada); generador en `fuente/` que verifica el programa contra el material del webinar |
| [informe/](informe/README.md) | Informe 2 v2.6 (HTML + PPTX, 346 diapositivas): el ecosistema completo, con los dos caminos de instalación (WSL2 o Docker), con una diapositiva por capacidad (incluidas las decisiones con contexto, la bitácora y pm-kb), la figura de su guía E2E y la salida real de la evidencia; generador en `fuente/` (cifras extraídas del repositorio) |
| [resumen-ejecutivo/](resumen-ejecutivo/README.md) | resumen ejecutivo comercial (PPTX + HTML): propuesta de valor, agentes y skills, arquitectura, ciclo de vida, controles permanentes, decisiones con contexto y búsqueda citada (pm-kb), integraciones y un caso E2E por diapositiva (19 diapositivas; «Cómo empezar» con los dos caminos de instalación); cifras extraídas del repositorio al regenerar (`fuente/extraer.py`) |
| [resumen-ejecutivo/spot/](resumen-ejecutivo/spot/README.md) | spot para LinkedIn (MP4 de 56,5 s, 4:5, en español): locución sintética, música original y subtítulos incrustados, versión sin voz, `.srt` y guion de locución con tiempos; generador reproducible en `fuente/` |
| [webinar/](webinar/README.md) | material del webinar por caso E2E (guion del instructor, ejercicio, diapositivas, ficha promocional del taller), el generador de diapositivas PPTX + HTML con glosario (`scripts/webinar/generar.py`; con `--ficha`, la ficha del taller desde `E2E-N/ficha.json`: `E2E-N-ficha.pptx` de 2 diapositivas con notas y `E2E-N-ficha.html`, volante A4) y los documentos en HTML autocontenido para presentar, repartir o imprimir (`scripts/webinar/documentos.py`): por caso `E2E-N-guia.html`, `E2E-N-guion-instructor.html` y `E2E-N-ejercicio.html` (una sola versión: la mecánica al comienzo y el ejemplo resuelto con el escenario del caso plegado al final), más `webinar/index.html` con todo el material |

## 3. Diagramas

Fuentes Mermaid y SVG en [`docs/diagramas/`](diagramas/) (los mismos del README):

| Diagrama | Archivos |
|---|---|
| Arquitectura por capas | `arquitectura.mmd` · `arquitectura.svg` |
| Orquestación de una puerta | `orquestacion-puerta.mmd` · `orquestacion-puerta.svg` |
| Agentes y skills | `agentes-skills.mmd` · `agentes-skills.svg` |
| Ciclo de vida PRINCE2 y puertas | `ciclo-de-vida.mmd` · `ciclo-de-vida.svg` |
| Sincronización con BMAD | `sincronizacion-bmad.mmd` · `sincronizacion-bmad.svg` |
| Ciclo de vida PRINCE2 + BMAD y demás componentes | `ciclo-prince2-bmad.mmd` · `ciclo-prince2-bmad.svg` |
| Verificación de una puerta | `verificacion-puertas.mmd` · `verificacion-puertas.svg` |
| pm-kb: índice derivado y de solo lectura, escrituras por propuesta | `pm-kb.mmd` · `pm-kb.svg` |

## 4. Pruebas y evidencia

| Recurso | Qué es |
|---|---|
| `scripts/validar_paquete.py` | validación estructural del paquete |
| `scripts/pruebas/integracion/correr.py` | integración cruzada: seis cadenas sobre un mismo proyecto (BMAD → plan → EVM → OKR → puertas; actas, Jira y BMAD → riesgos → opciones y contingencia → presupuestos → tablero y highlight, y comité → acuerdos registrados; interesados ↔ RACI ↔ OKR ↔ envíos; mapas → inversión, personas, impacto de un cambio, tres valores y capacidad, decisiones con contexto, RACI ↔ autoridad, vigencia y hacer o comprar; exportación, paquete, expediente de auditoría, radar y briefing, lecciones, estado de productos, bitácora y propuestas; recorridos E2E → webinar) con integridad referencial en cada eslabón ([PRUEBAS §2.3](PRUEBAS.md)) |
| `scripts/pruebas/guias_e2e/correr.py` | corre los cinco recorridos E2E de `docs/guias/` con los scripts reales (≈ 2 min, sin tokens) y guarda la evidencia y las 66 imágenes (gráficos de `visuales.py` y capturas); sin pm-kb, sus pasos se omiten con aviso; `--comparar docs/guias/evidencia` compara la evidencia normalizada, `--python` elige el intérprete y `--conservar` deja los temporales |
| `scripts/pruebas/variantes/correr.py` | suite de variantes ([PRUEBAS §2.5](PRUEBAS.md)): robustez y migración desde 2.6.1, caminos alternos, matriz de entorno pairwise (Python × dependencias × BMAD × idioma × codificación × ruta) con manifiesto de omisiones, fallas de SMTP y webhooks, contratos documentación ↔ CLI (scripts y `pm-kb`) y esquema ↔ consumidores, entorno Hermes, E2E comparados y opcionales (`opcionales.py`: pm-kb con modelos simulados por `simuladores.py` e interacción con pm-method, BMAD y el MCP, `probar_kb.py` y `pantallas.py`; `portal.py`: el portal con pm-method, instantáneas de las puertas, «actualizar ahora» en solo lectura, propuestas, enlaces compartidos, inglés y `pm-kb enlaces`; skills externas de diagramas en un contenedor sin red y sus salidas en el portal); `--repetir 2` para el criterio de una versión |
| `scripts/validar_mermaid.py` | lint de los bloques Mermaid (errores que GitHub no renderiza) y render con mmdc; `--png` para inspección visual (131 bloques, 0 errores) |
| `scripts/probar_paquete.py` | 558 pruebas de regresión con Python 3.13 y 554 con 3.9 (casos A–N, P, S, X e Y y los de las capacidades de decisión y control: DC decisiones con contexto, DR decisiones y RACI, DK correcciones de decisiones, MD decisiones y mapas, BU búsqueda en español e inglés, VG vigencia de decisiones, BT bitácora de escrituras, PR propuestas con huella, CC escrituras concurrentes, I2 opciones y contingencia, PU personas, RA radar y briefing, PE datos del período, LX y LC lecciones entre proyectos y su ciclo, RD reuniones, IM impacto, TV tres valores y capacidad, AU expediente de auditoría PS estado de productos y cierre C3 correcciones 2.6.3 (idioma de los hallazgos, plan de excepción en el cierre prematuro, supuesto transferido) y TB tablero del proyecto (`tablero.py`, congelado en cada puerta, solo lectura); KB, el núcleo de pm-kb sin base; DD, el contrato con diagram-design, completo con `PM_DIAGRAM_DESIGN` (5 OK; la imagen Docker la define); el caso X corre la integración cruzada sin los recorridos; el caso Y, el `--help` de los 39 scripts y los mensajes ante entradas faltantes; el caso H cubre interesados, capa de canales con SMTP y webhooks locales y OKR; el caso K, supuestos críticos y P-11; el caso L, el esquema de las diapositivas del webinar; el caso L3, la ficha promocional del taller; el caso L2, los documentos del webinar en HTML; el caso P, las salidas de los scripts para el usuario; el caso I, candidatos de riesgo desde cuatro fuentes; el caso J, controles permanentes; el caso J2, autoridad y presupuesto de cambio al registrar; el caso S, las correcciones de [SEGURIDAD](SEGURIDAD.md); el caso N, el endurecimiento de SEG-03 a SEG-10, los presupuestos de contexto de [PRUEBAS §2.2](PRUEBAS.md) e `inversion.py`; el caso M, los mapas estratégicos) |
| `docker/` · `pm-pruebas` | entorno Docker opcional: `docker compose -f docker/compose.yaml run --rm pruebas` corre sin red todas las pruebas gratuitas dentro del contenedor ([DOCKER §5.5](DOCKER.md)); CI en `.github/workflows/docker.yml` |
| `pm-kb/pruebas/` | pruebas de pm-kb: `probar_kb.py` (39 de núcleo sin base; 116 con `--con-base`), `pantallas.py` (portal en Chromium con Playwright, claro, oscuro y móvil; 68), `consultas_oro.py` (aciertos@5 y MRR@5 sobre el proyecto de E2E-1), `conformidad_mcp.py` (SDK oficial de MCP, stdio y HTTP), los proyectos de prueba `fixture.py` y `proyecto_tablero.py` (armado con los scripts del núcleo: puertas decididas e instantáneas) y `esquema-2.sql` y `esquema-3.sql` (esquemas anteriores para probar la migración) ([PRUEBAS §7](PRUEBAS.md#7-pm-kb-componente-opcional)) |
| `scripts/pruebas/generar_bmad_grande.py` | genera un BMAD sintético grande para pruebas de escala |
| `scripts/pruebas/fixtures/` | BMAD v6 sintético, BMAD 6.12.4 real, BMAD v4 |
| `scripts/pruebas_vivo/vivo.py` · `suite.py` · `escenarios.py` | arnés, suite y escenarios de robustez con Claude Code real |
| `docs/evaluacion/frases-enrutamiento.tsv` | 134 frases con la skill esperada (y aceptables) |
| `docs/evaluacion/resultados/` | informes de las pruebas en vivo con Claude Code real y de las campañas de verificación (por ejemplo, [portal 2.7.0](evaluacion/resultados/2026-10-30-portal-v2.7.0.md)); cada nombre lleva la fecha y la versión con que se corrió |
| `docs/ejemplos/` | salidas reales: traspaso a BMAD, informe de sanidad, WBS en Mermaid |
| `docs/ejemplos/integraciones/` | salidas reales de los casos de integración (MSPDI, Gantt, OKR, transcripción, avance BMAD, archify) |

## 5. Componentes del paquete

| Carpeta | Contenido | Documento de referencia |
|---|---|---|
| `agents/` | 6 agentes | [ARQUITECTURA](ARQUITECTURA.md), [RACI](RACI.md) |
| `skills/` | 39 skills con `references/`, `templates/`, `scripts/` | [CATALOGO](CATALOGO.md) |
| `hooks/` | `guardian.py`, `inicio.py`, `idioma.py`, `py.sh`, `hooks.json` | [INSTALACION §9](INSTALACION.md), [SANIDAD](SANIDAD.md) |
| `skills/pm-estado-proyecto/scripts/` | núcleo de scripts | [CATALOGO](CATALOGO.md) |
| `skills/pm-estado-proyecto/scripts/tablero.py` | tablero del proyecto (`pm-tablero/1`, JSON o HTML autocontenido; también por actor) e instantáneas congeladas en cada puerta en `03-control/reportes/tableros/`; lo publica el portal de pm-kb | [CATALOGO §5.1](CATALOGO.md), [ARQUITECTURA §9.5](ARQUITECTURA.md), SPEC §1.10.17 |
| `skills/pm-bmad-puente/scripts/bmad.py` | puente BMAD | [sincronizacion](sincronizacion.md) |
| `skills/pm-interesados/` | maestro de interesados: `interesados.py` (matriz, estereotipos, preferencias, perfil, RACI, personas de usuario y capacidad × persona, integridad, reporte, plan de envío), guía §1–§13 y plantillas (análisis, RACI, plan de compromiso, entrevista) | [CATALOGO](CATALOGO.md), [SPEC §1.10.10](../SPEC.md) |
| `skills/pm-integraciones/scripts/envios.py` | capa de canales: correo SMTP, webhooks de Slack o Teams, `.eml` y MCP, con aprobación y registro en `envios.csv` | [CATALOGO](CATALOGO.md), [SPEC §1.12](../SPEC.md) |
| `skills/pm-okr/scripts/okr.py` | OKR: tipos de KR, check-ins (`okr_checkins.csv`), salud, propuesta de sincronización con Tability o Perdoo | [CATALOGO](CATALOGO.md) |
| `skills/pm-caso-de-negocio/scripts/inversion.py` | evaluación de la inversión por opción desde un CSV de flujos: VAN, TIR, repago simple y descontado, sensibilidad y punto de equilibrio (fórmulas en `--help`) | [guía de pm-caso-de-negocio §2](../skills/pm-caso-de-negocio/references/guia.md) |
| `skills/pm-riesgos/scripts/riesgos.py` | riesgos candidatos desde BMAD, transcripciones, la instantánea del tracker y los artefactos del proyecto (borrador; no escribe registros) y `opciones`: valor neto de las opciones de respuesta de los riesgos altos y elección del propietario con `--por` | [CATALOGO](CATALOGO.md), [guía E2E-1](guias/E2E-1-riesgos.md) |
| `skills/pm-reuniones/scripts/extraccion.py` | candidatos de decisiones (con nivel), compromisos, supuestos y riesgos desde una transcripción, con cita y hora, y en una retrospectiva lecciones y acciones de mejora; registra solo los ids confirmados | [guía de pm-reuniones §3.1](../skills/pm-reuniones/references/guia.md) |
| `skills/pm-issues-cambios/scripts/impacto.py` | análisis de impacto de un C-### (CPM, reserva, costo y presupuesto de cambio, autoridad, capacidad, VAN, EVM, riesgos y calidad) y borrador de la solicitud con opciones y quién decide | [guía de pm-issues-cambios §3.1](../skills/pm-issues-cambios/references/guia.md) |
| `skills/pm-agil-hibrido/scripts/release.py` | capacidad de cada release por MoSCoW contra velocidad × iteraciones (holgura, Must / capacidad, historias a dividir); la misma función usa `impacto.py` | [guía de pm-agil-hibrido §6](../skills/pm-agil-hibrido/references/guia.md) |
| `skills/pm-direccion-decisiones/scripts/decision.py` | decisiones con contexto para seis tipos (riesgo, negocio, planificación, OKR, cambio, adquisición): expediente de solo lectura con la evidencia aplicable y su fuente, matriz multicriterio de la hoja `03-control/decisiones/<ID>/` (suma ponderada, eliminatorios, dominadas, sensibilidad de pesos, empates, abstención), pregunta tipada con validación y elección registrada con `--por` | [guía de pm-direccion-decisiones §13](../skills/pm-direccion-decisiones/references/guia.md), [SPEC §1.10.15](../SPEC.md) |
| `skills/pm-lecciones-aprendidas/scripts/lecciones.py` | ciclo de las lecciones (clasificar por impacto y proceso, accionar, verificar, descartar), informe desde el registro con exportación al índice de la organización y búsqueda e incorporación de lecciones aprobadas de otros proyectos | [guía de pm-lecciones-aprendidas](../skills/pm-lecciones-aprendidas/references/guia.md) |
| `skills/pm-exportar/scripts/paquete.py` | paquete de puerta o de cierre y expediente de auditoría (`auditoria`, `verificar`) con cronología, líneas base, evidencia y `SHA256SUMS` | [guía de pm-exportar §3.1](../skills/pm-exportar/references/guia.md) |
| `skills/pm-mapas-estrategicos/scripts/mapas.py` | mapas de Wardley y de recorrido del cliente: semilla (BMAD de solo lectura o artefactos), validación, vistas Mermaid, OWM, HTML y PNG, candidatos, vínculos y controles MAP | [CATALOGO](CATALOGO.md), [guía E2E-5](guias/E2E-5-idea-a-proyecto.md) |
| `compatibilidad.json` | versiones probadas y dependencias | [DEPENDENCIAS](DEPENDENCIAS.md) |
| `pm-kb/` | componente opcional (no es skill ni agente): índice de conocimiento en PostgreSQL con búsqueda citada, línea de comandos (también `vigilar`, `tablero`, `enlaces` y `compartir`), portal web (cartera, tableros con su historial, artefactos y documentos en marco aislado, fichas por id, enlaces compartidos) y MCP de solo lectura; instalador para WSL2, `db/pg.sh`, dependencias fijadas por hash y pruebas | [PM-KB](PM-KB.md), [INSTALACION-WSL2 §8](INSTALACION-WSL2.md#8-pm-kb-buscar-en-tus-proyectos-opcional--ubuntu), [INSTALACION-DOCKER §8](INSTALACION-DOCKER.md#8-pm-kb-en-docker-opcional) |
| `docs/servicios/pm-kb-vigilar@.service` | unidad de usuario de systemd para `pm-kb vigilar` en WSL2 (una instancia por proyecto; en Docker, el servicio `pm-kb-vigilar` del perfil `kb`) | [INSTALACION-WSL2 §8.10](INSTALACION-WSL2.md#810-mantener-el-índice-al-día-pm-kb-vigilar-como-servicio--ubuntu), [INSTALACION-DOCKER §8.10](INSTALACION-DOCKER.md#810-mantener-el-índice-al-día-servicio-pm-kb-vigilar--ubuntu) |

## 6. Pendientes y puntos abiertos

- **Decisiones con contexto:** `decision.py` (guía de `pm-direccion-decisiones` §13) se recorre en las cinco guías E2E
  y en el webinar, pero todavía no tiene un caso propio en [CASOS-DE-USO](CASOS-DE-USO.md); el expediente de auditoría
  (`paquete.py auditoria`) no incluye las hojas `03-control/decisiones/<ID>/`; la prueba en vivo cubrió el enrutamiento
  (frases 131–134), no una sesión completa que arme la hoja, la puntúe con fuentes y registre la elección.
- **pm-kb:** la respuesta con modelo de «Preguntar» y los modelos de vectores y re-ranqueo se probaron con simuladores
  que hablan el mismo protocolo (nivel `opcionales` de la suite de variantes), no con los modelos reales (bge-m3 en TEI,
  el re-ranqueador y la API de Anthropic) [verificar con la guía: INSTALACION-WSL2 §8.8 e INSTALACION-DOCKER §8.9]
  ([PRUEBAS §7](PRUEBAS.md#7-pm-kb-componente-opcional)).
- **Hermes Agent:** instalación de las skills, rutas y scripts desde la copia de Hermes verificados (nivel `hermes`); el
  comando `hermes` no se pudo instalar en la red de prueba (`nodejs.org` bloqueado), así que `hermes skills list` y una
  conversación quedan por comprobar [verificar: INSTALACION-WSL2 §7].
- **Idioma de los hallazgos:** las traducciones al inglés de los mensajes de `sanidad.py` y `puertas.py` (2.6.3) no las
  revisó una persona de habla inglesa [verificar]; el marco del hook de inicio (texto para el modelo) y las etiquetas de
  la cronología del expediente de auditoría (`paquete.py auditoria`: «— condiciones:», «(FORZADA)», «lista confirmada
  por») siguen en español, con los hallazgos que citan en el idioma del proyecto.
- **Windows nativo:** la salida en UTF-8 y los hooks con la consola cp1252 se probaron emulándola en Linux [verificar en
  Windows real].

- **Pruebas en vivo completas:** los escenarios de robustez `inyeccion`, `desorden`, `multisesion` y `escala` se
  corrieron el 2026-10-17 y no se repitieron con los cambios posteriores; la batería completa `suite.py todo` (consume
  tokens) se corrió con 2.6.2 (2026-10-29: enrutamiento 130/134 con variabilidad en cuatro frases ambiguas,
  guardarraíles e idioma OK; [estabilización 2.6.2](evaluacion/resultados/2026-10-29-estabilizacion-v2.6.2.md) §4), junto
  con una sesión con el plugin, el MCP de pm-kb y diagram-design. Las pruebas en vivo de 2.6.0 son las de enrutamiento de
  las frases 131 a 134 con sus frases de control (2026-10-28, 11/11 en dos corridas) y las sesiones de Claude Code con el
  MCP de pm-kb por stdio y por HTTP; las de 2.4.0, enrutamiento de las frases 103 a 130 con sus frases de control
  (2026-10-21 y 2026-10-22, todas OK); las de 2.3.0, enrutamiento (14/14 y 8/8), integración con BMAD instalado (12/12)
  y `controles` (7/7) del 2026-10-20 ([PRUEBAS §3.1](PRUEBAS.md)).
- **Docker:** la imagen `pm-method:2.7.0` (con diagram-design y las dependencias de pm-kb) y la de la base de pm-kb se
  construyeron y probaron el 2026-10-29 ([DOCKER §10](DOCKER.md)); los comandos de [INSTALACION-DOCKER](INSTALACION-DOCKER.md)
  se ejecutaron en Linux (§14; con la imagen 2.7.0, la comprobación de la imagen, la prueba rápida, la batería completa
  dos veces, el render de Mermaid y el perfil `kb`). Los procedimientos de los opcionales (modelos de pm-kb, envío a interesados, skills externas
  y conectores MCP, en INSTALACION-WSL2 e INSTALACION-DOCKER) se comprobaron en parte, sin instalar servidores ni
  conectores reales [verificar]. Quedan [verificar]: Docker
  Desktop y todo lo de Windows, la instalación de Docker Engine (repositorio de Docker bloqueado en la red de prueba),
  una sesión de Claude Code con credenciales dentro del contenedor y la arquitectura arm64 ([DOCKER §9](DOCKER.md)).
- **Render de `wardley-beta` en GitHub** [verificar]: es un tipo de diagrama de Mermaid en beta (11.14 o posterior) y no
  todos los visores de Markdown lo dibujan; por eso `mapas.py render` deja también el PNG y el texto OWM.
- Ítems marcados `[verificar]` en INSTALACION y DEPENDENCIAS (URLs de sitios no alcanzables desde el entorno de prueba,
  pasos de Cowork y Hermes); plan comercial que exigen los MCP de Tability y Perdoo; exclusión de texto escrito del art.
  5(1)(f) del AI Act (solo fuentes secundarias).
- Conectores MCP de terceros (Jira, Slack, Teams, Granola, Fireflies, Zoom, Tability, Perdoo) documentados pero no
  probados en vivo; la capa de canales se probó contra servidores SMTP y webhooks locales, no contra servicios reales;
  los hooks en Windows con `py.sh` no se probaron en una máquina Windows real.
- **`npm` de la imagen Docker:** 1 aviso alto y 1 moderado en `undici` e `ip-address` empaquetados en `npm` 11.21.1, sin
  versión publicada de `npm` que los corrija al 2026-10-27; aceptados temporalmente ([SEGURIDAD](SEGURIDAD.md) SEG-13).
  Subir `npm` cuando se publique la corrección.
- **pm-kb** [verificar] ([PM-KB §15](PM-KB.md#15-limitaciones-y-verificar)): vectores, re-ranqueo y la respuesta con
  modelo de "Preguntar" (no probados en vivo; los modelos recomendados no se pudieron descargar en el entorno de
  prueba); el instalador en Ubuntu 26.04 sobre WSL y en aarch64; la web desde el navegador de Windows (reenvío de
  `localhost` de WSL2) y el MCP en `127.0.0.1:8765` desde fuera de los contenedores; Hermes con un modelo y el prefijo
  exacto de sus herramientas MCP; LibreChat y Cowork; la desinstalación de sus paquetes de Ubuntu y el borrado de su
  imagen y su volumen; `vigilar` como servicio con el apagado automático de WSL; un enlace compartido abierto desde
  otra computadora detrás de un proxy con TLS. Limitaciones aceptadas: estadísticas de BM25 que incluyen lo restringido
  (SEG-18), hasta 60 s para que un servicio en marcha deje de aceptar un token revocado (SEG-19) y la ficha de una
  tarjeta nueva, que responde 404 hasta la indexación siguiente cuando el tablero se regeneró sin reindexar.
- Mejoras candidatas: Monte Carlo de contingencia (P50/P80), con los tres valores de `actividades.csv` como entrada; calendarios y feriados en `cpm.py`; trazado de
  `bmad-spec` (`SPEC.md`, ids `CAP-n`).
