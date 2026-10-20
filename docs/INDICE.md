# Índice de la documentación y las pruebas · pm-method 2.3.0

Mapa de todo lo que hay en el repositorio para entenderlo rápido. EN: *documentation and test map.*

## 1. Rutas de lectura por perfil

| Perfil | Leer en este orden | Tiempo aproximado |
|---|---|---|
| Decisor / patrocinador | [RESUMEN-EJECUTIVO](RESUMEN-EJECUTIVO.md) → diagramas del [README](../README.md) → [PRUEBAS §3.1](PRUEBAS.md) → [PILOTO](PILOTO.md) | 20 min |
| Gestor de proyectos (usuario) | [INSTALACION](INSTALACION.md) → [guías E2E](guias/README.md) (probar como usuario, por prompts) → [PRUEBAS §6](PRUEBAS.md) (aceptación) → [CASOS-DE-USO](CASOS-DE-USO.md) → [CASO-MAESTRO](CASO-MAESTRO.md) | 2–4 h |
| Equipo de producto con BMAD | [PUERTAS](PUERTAS.md) → [sincronizacion](sincronizacion.md) → [CASOS-DE-USO-INTEGRACIONES §7](CASOS-DE-USO-INTEGRACIONES.md) → [SANIDAD](SANIDAD.md) (familia ESP) | 45 min |
| Responsable de comunicación con interesados | [guía E2E-3](guias/E2E-3-interesados-okr-avance.md) (14 pasos: matriz, preferencias, RACI, OKR, envío por canales, cadencia de contacto STK-12) → [CATALOGO: pm-interesados](CATALOGO.md) → [colisiones](colisiones.md) (qué frase va a cada skill) → `skills/pm-interesados/references/guia.md` | 1 h |
| Quien integra herramientas | [DEPENDENCIAS](DEPENDENCIAS.md) → [INTEGRACIONES](INTEGRACIONES.md) → [CASOS-DE-USO-INTEGRACIONES](CASOS-DE-USO-INTEGRACIONES.md) → [INSTALACION §6](INSTALACION.md) | 1 h |
| Junta, PMO o aseguramiento (controles permanentes) | [SANIDAD §2.1](SANIDAD.md) (familias CAM, QUA, TOL y SUP, REG-09 y STK-12) → [PUERTAS §3.1](PUERTAS.md) (condiciones formales, G-01, P-11) → tablas "Del uso único al control continuo" de las [guías E2E](guias/README.md) → [CASOS-DE-USO caso 48](CASOS-DE-USO.md) | 45 min |
| Formador o facilitador | [guías E2E](guias/README.md) → [webinar](webinar/README.md) (guion, ejercicio y diapositivas por caso) → [TERMINOLOGIA](TERMINOLOGIA.md) | 1 h por caso |
| Quien mantiene el paquete | [CLAUDE.md](../CLAUDE.md) → [ARQUITECTURA](ARQUITECTURA.md) → [SPEC.md](../SPEC.md) → [colisiones](colisiones.md) → [PRUEBAS](PRUEBAS.md) | 2 h |

## 2. Documentos

| Documento | Qué responde |
|---|---|
| [README](../README.md) | qué es, diagramas, instalación rápida, componentes, dependencias, calidad verificada |
| [RESUMEN-EJECUTIVO](RESUMEN-EJECUTIVO.md) | por qué usarlo: problema, capacidades, valor diferencial, evidencia, límites |
| [INSTALACION](INSTALACION.md) | cómo instalar y configurar todo (plugin, credenciales y API-KEY §0.7, Orca opcional §0.8, Python, BMAD, skills externas, MCP, Cowork, Hermes), verificar y resolver problemas |
| [DOCKER](DOCKER.md) | entorno Docker opcional (alternativa a la instalación manual): qué incluye, construir, usar con Claude Code sobre un proyecto montado, correr las pruebas sin red, actualizar, seguridad del contenedor, proxies, limitaciones y verificación registrada |
| [DEPENDENCIAS](DEPENDENCIAS.md) | cada dependencia con nivel, uso, versión probada, licencia, URL de origen y cómo se verificó |
| [ARQUITECTURA](ARQUITECTURA.md) | capas, precedencia PRINCE2/PMBOK, agentes vs subagentes, carga progresiva, presupuesto de descripciones |
| [INTEGRACIONES](INTEGRACIONES.md) | qué repositorio se integró y por qué, contratos, verificación en vivo, cómo agregar una integración |
| [sincronizacion](sincronizacion.md) | fuente única por dato, fachada `pm-spec-index/1`, líneas base, traspaso a BMAD |
| [SANIDAD](SANIDAD.md) | catálogo de las 85 comprobaciones en 12 familias: INS, EST, ART, REG (con REG-09, revisión de riesgos vencida), ESP, INT, STK (maestro de interesados), las de controles permanentes CAM (cambios contra presupuestos), QUA (calidad a volumen), TOL (pronóstico contra tolerancias) y SUP (supuestos críticos), y MAP (mapas de Wardley y de recorrido, solo avisos); `--corte` |
| [RACI](RACI.md) | quién decide, quién produce y quién registra, por rol humano, agente y skill |
| [CATALOGO](CATALOGO.md) | las 39 skills: disparadores, artefactos, agente, scripts |
| [TERMINOLOGIA](TERMINOLOGIA.md) | equivalencias PRINCE2 7 · PRINCE2 en español · PMBOK en español · uso habitual, skill que responde y frase verificada en vivo |
| [colisiones](colisiones.md) | dueños únicos de cada artefacto y pistas de alcance entre skills |
| [CASOS-DE-USO](CASOS-DE-USO.md) | un caso por skill a lo largo del ciclo de vida; parte 6 (casos 38 a 48): maestro de interesados, canales, OKR, riesgos desde cuatro fuentes y controles permanentes (caso 48) |
| [CASOS-DE-USO-INTEGRACIONES](CASOS-DE-USO-INTEGRACIONES.md) | un caso por repositorio integrado: diseño visual, reportes, planificación, OKR, reuniones, trackers, BMAD |
| [CASO-MAESTRO](CASO-MAESTRO.md) | proyecto completo con BMAD, con prompts del usuario, comandos y salidas reales |
| [guias/](guias/README.md) | cinco guías de punta a punta por prompts, con reporte y gráficos: [riesgos](guias/E2E-1-riesgos.md), [alcance, cambio, esfuerzo, priorización y roadmap](guias/E2E-2-alcance-roadmap.md), [interesados, comunicaciones, OKR y avance](guias/E2E-3-interesados-okr-avance.md), [producto de la idea al producto con BMAD](guias/E2E-4-producto-bmad.md), [de la idea al proyecto diseñado](guias/E2E-5-idea-a-proyecto.md); 70 pasos en total (15, 10, 14, 13 y 18), dos clases de 90 minutos por caso, cada guía con su tabla "Del uso único al control continuo"; evidencia reproducible en `guias/evidencia/` y 42 imágenes en `guias/img/` |
| [PRUEBAS](PRUEBAS.md) | niveles de prueba, qué cubre cada una (incluidas la integración cruzada, la compatibilidad con Python 3.9 y los presupuestos de contexto medidos en vivo), resultados registrados y lista de aceptación |
| [PUERTAS](PUERTAS.md) | qué se verifica en cada puerta (salud, controles PRINCE2 y BMAD, lista de control de la junta), cómo se registra la decisión y cómo se siguen sus condiciones hasta cumplirse (G-01, `cumplir-condiciones`); diagrama del ciclo de vida PRINCE2 + BMAD |
| [PILOTO](PILOTO.md) | plan de piloto en paralelo: fases, métricas, rúbrica de revisión experta, prueba de usabilidad, criterios de decisión |
| [SEGURIDAD](SEGURIDAD.md) | revisión de seguridad para quien instala: alcance, herramientas, modelo de amenazas, hallazgos con severidad y estado, buenas prácticas y cómo reportar una vulnerabilidad |
| [CHANGELOG](../CHANGELOG.md) | cambios por versión |
| [SPEC.md](../SPEC.md) | especificación de construcción y convenciones canónicas |
| [CLAUDE.md](../CLAUDE.md) · [AGENTS.md](../AGENTS.md) | cómo seguir desarrollando el paquete con agentes de código |
| [informe/](informe/README.md) | Informe 2 (HTML + PPTX) y su generador |
| [resumen-ejecutivo/](resumen-ejecutivo/README.md) | resumen ejecutivo comercial (PPTX + HTML): propuesta de valor, agentes y skills, arquitectura, ciclo de vida, controles permanentes, integraciones y un caso E2E por diapositiva; cifras extraídas del repositorio al regenerar (`fuente/extraer.py`) |
| [resumen-ejecutivo/spot/](resumen-ejecutivo/spot/README.md) | spot para LinkedIn (MP4 de 44 s, 4:5, en español): locución sintética, música original y subtítulos incrustados, versión sin voz, `.srt` y guion de locución con tiempos; generador reproducible en `fuente/` |
| [webinar/](webinar/README.md) | material del webinar por caso E2E (guion del instructor, ejercicio, diapositivas) y el generador de diapositivas PPTX + HTML con glosario (`scripts/webinar/generar.py`) |

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

## 4. Pruebas y evidencia

| Recurso | Qué es |
|---|---|
| `scripts/validar_paquete.py` | validación estructural del paquete |
| `scripts/pruebas/integracion/correr.py` | integración cruzada: seis cadenas sobre un mismo proyecto (BMAD → plan → EVM → OKR → puertas; actas, Jira y BMAD → riesgos → presupuestos → tablero; interesados ↔ RACI ↔ OKR ↔ envíos; mapas → inversión; exportación y paquete; recorridos E2E → webinar) con integridad referencial en cada eslabón ([PRUEBAS §2.3](PRUEBAS.md)) |
| `scripts/pruebas/guias_e2e/correr.py` | corre los cinco recorridos E2E de `docs/guias/` con los scripts reales (≈ 2 min, sin tokens) y guarda la evidencia y las 42 imágenes (gráficos de `visuales.py` y capturas) |
| `scripts/validar_mermaid.py` | lint de los bloques Mermaid (errores que GitHub no renderiza) y render con mmdc; `--png` para inspección visual (127 bloques, 0 errores) |
| `scripts/probar_paquete.py` | 216 pruebas de regresión con Python 3.13 y 215 con 3.9 (casos A–N, P, S, X e Y; el caso X corre la integración cruzada sin los recorridos; el caso Y, el `--help` de todos los scripts y los mensajes ante entradas faltantes; el caso H cubre interesados, capa de canales con SMTP y webhooks locales y OKR; el caso K, supuestos críticos y P-11; el caso L, el esquema de las diapositivas del webinar; el caso P, las salidas de los scripts para el usuario; el caso I, candidatos de riesgo desde cuatro fuentes; el caso J, controles permanentes; el caso J2, autoridad y presupuesto de cambio al registrar; el caso S, las correcciones de [SEGURIDAD](SEGURIDAD.md); el caso N, el endurecimiento de SEG-03 a SEG-10, los presupuestos de contexto de [PRUEBAS §2.2](PRUEBAS.md) e `inversion.py`; el caso M, los mapas estratégicos: semillas con y sin BMAD, validación, MAP-01…05, REG-09, HTML escapado, `wardley-beta` que renderiza y `bmad.py linea-base --fecha`) |
| `docker/` · `pm-pruebas` | entorno Docker opcional: `docker compose -f docker/compose.yaml run --rm pruebas` corre sin red todas las pruebas gratuitas dentro del contenedor ([DOCKER §5.5](DOCKER.md)); CI en `.github/workflows/docker.yml` |
| `scripts/pruebas/generar_bmad_grande.py` | genera un BMAD sintético grande para pruebas de escala |
| `scripts/pruebas/fixtures/` | BMAD v6 sintético, BMAD 6.12.4 real, BMAD v4 |
| `scripts/pruebas_vivo/vivo.py` · `suite.py` · `escenarios.py` | arnés, suite y escenarios de robustez con Claude Code real |
| `docs/evaluacion/frases-enrutamiento.tsv` | 102 frases con la skill esperada (y aceptables) |
| `docs/evaluacion/resultados/` | informes de las pruebas en vivo con Claude Code real; cada nombre lleva la fecha y la versión con que se corrió |
| `docs/ejemplos/` | salidas reales: traspaso a BMAD, informe de sanidad, WBS en Mermaid |
| `docs/ejemplos/integraciones/` | salidas reales de los casos de integración (MSPDI, Gantt, OKR, transcripción, avance BMAD, archify) |

## 5. Componentes del paquete

| Carpeta | Contenido | Documento de referencia |
|---|---|---|
| `agents/` | 6 agentes | [ARQUITECTURA](ARQUITECTURA.md), [RACI](RACI.md) |
| `skills/` | 39 skills con `references/`, `templates/`, `scripts/` | [CATALOGO](CATALOGO.md) |
| `hooks/` | `guardian.py`, `inicio.py`, `idioma.py`, `py.sh`, `hooks.json` | [INSTALACION §9](INSTALACION.md), [SANIDAD](SANIDAD.md) |
| `skills/pm-estado-proyecto/scripts/` | núcleo de scripts | [CATALOGO](CATALOGO.md) |
| `skills/pm-bmad-puente/scripts/bmad.py` | puente BMAD | [sincronizacion](sincronizacion.md) |
| `skills/pm-interesados/` | maestro de interesados: `interesados.py` (matriz, estereotipos, preferencias, perfil, RACI, integridad, reporte, plan de envío), guía §1–§12 y plantillas (análisis, RACI, plan de compromiso, entrevista) | [CATALOGO](CATALOGO.md), [SPEC §1.10.10](../SPEC.md) |
| `skills/pm-integraciones/scripts/envios.py` | capa de canales: correo SMTP, webhooks de Slack o Teams, `.eml` y MCP, con aprobación y registro en `envios.csv` | [CATALOGO](CATALOGO.md), [SPEC §1.12](../SPEC.md) |
| `skills/pm-okr/scripts/okr.py` | OKR: tipos de KR, check-ins (`okr_checkins.csv`), salud, propuesta de sincronización con Tability o Perdoo | [CATALOGO](CATALOGO.md) |
| `skills/pm-caso-de-negocio/scripts/inversion.py` | evaluación de la inversión por opción desde un CSV de flujos: VAN, TIR, repago simple y descontado, sensibilidad y punto de equilibrio (fórmulas en `--help`) | [guía de pm-caso-de-negocio §2](../skills/pm-caso-de-negocio/references/guia.md) |
| `skills/pm-riesgos/scripts/riesgos.py` | riesgos candidatos desde BMAD, transcripciones, la instantánea del tracker y los artefactos del proyecto (borrador; no escribe registros) | [CATALOGO](CATALOGO.md), [guía E2E-1](guias/E2E-1-riesgos.md) |
| `skills/pm-mapas-estrategicos/scripts/mapas.py` | mapas de Wardley y de recorrido del cliente: semilla (BMAD de solo lectura o artefactos), validación, vistas Mermaid, OWM, HTML y PNG, candidatos, vínculos y controles MAP | [CATALOGO](CATALOGO.md), [guía E2E-5](guias/E2E-5-idea-a-proyecto.md) |
| `compatibilidad.json` | versiones probadas y dependencias | [DEPENDENCIAS](DEPENDENCIAS.md) |

## 6. Pendientes y puntos abiertos

- **Pruebas en vivo completas:** los escenarios de robustez `inyeccion`, `desorden`, `multisesion` y `escala` se
  corrieron el 2026-10-17 y no se repitieron con los cambios posteriores; la batería completa `suite.py todo` (consume
  tokens) no se corrió con la versión 2.3.0. Las pruebas en vivo de 2.3.0 son las de enrutamiento (14/14 y 8/8), la
  integración con BMAD instalado (12/12) y `controles` (7/7) del 2026-10-20 ([PRUEBAS §3](PRUEBAS.md)).
- **Docker:** una sesión de Claude Code con credenciales dentro del contenedor (`claude -p`) y la arquitectura arm64
  quedan [verificar] ([DOCKER §9](DOCKER.md)).
- **Render de `wardley-beta` en GitHub** [verificar]: es un tipo de diagrama de Mermaid en beta (11.14 o posterior) y no
  todos los visores de Markdown lo dibujan; por eso `mapas.py render` deja también el PNG y el texto OWM.
- Ítems marcados `[verificar]` en INSTALACION y DEPENDENCIAS (URLs de sitios no alcanzables desde el entorno de prueba,
  pasos de Cowork y Hermes); plan comercial que exigen los MCP de Tability y Perdoo; exclusión de texto escrito del art.
  5(1)(f) del AI Act (solo fuentes secundarias).
- Conectores MCP de terceros (Jira, Slack, Teams, Granola, Fireflies, Zoom, Tability, Perdoo) documentados pero no
  probados en vivo; la capa de canales se probó contra servidores SMTP y webhooks locales, no contra servicios reales;
  los hooks en Windows con `py.sh` no se probaron en una máquina Windows real.
- Mejoras candidatas: Monte Carlo de contingencia (P50/P80); calendarios y feriados en `cpm.py`; trazado de
  `bmad-spec` (`SPEC.md`, ids `CAP-n`).
