# Índice de la documentación y las pruebas · pm-method 2.1.0

Mapa de todo lo que hay en el repositorio para entenderlo rápido. EN: *documentation and test map.*

## 1. Rutas de lectura por perfil

| Perfil | Leer en este orden | Tiempo aproximado |
|---|---|---|
| Decisor / patrocinador | [RESUMEN-EJECUTIVO](RESUMEN-EJECUTIVO.md) → diagramas del [README](../README.md) → [PRUEBAS §3.1](PRUEBAS.md) → [PILOTO](PILOTO.md) | 20 min |
| Gestor de proyectos (usuario) | [INSTALACION](INSTALACION.md) → [PRUEBAS §6](PRUEBAS.md) (aceptación) → [CASOS-DE-USO](CASOS-DE-USO.md) → [CASO-MAESTRO](CASO-MAESTRO.md) | 1–2 h |
| Equipo de producto con BMAD | [PUERTAS](PUERTAS.md) → [sincronizacion](sincronizacion.md) → [CASOS-DE-USO-INTEGRACIONES §7](CASOS-DE-USO-INTEGRACIONES.md) → [SANIDAD](SANIDAD.md) (familia ESP) | 45 min |
| Quien integra herramientas | [DEPENDENCIAS](DEPENDENCIAS.md) → [INTEGRACIONES](INTEGRACIONES.md) → [CASOS-DE-USO-INTEGRACIONES](CASOS-DE-USO-INTEGRACIONES.md) → [INSTALACION §6](INSTALACION.md) | 1 h |
| Quien mantiene el paquete | [CLAUDE.md](../CLAUDE.md) → [ARQUITECTURA](ARQUITECTURA.md) → [SPEC.md](../SPEC.md) → [colisiones](colisiones.md) → [PRUEBAS](PRUEBAS.md) | 2 h |

## 2. Documentos

| Documento | Qué responde |
|---|---|
| [README](../README.md) | qué es, diagramas, instalación rápida, componentes, dependencias, calidad verificada |
| [RESUMEN-EJECUTIVO](RESUMEN-EJECUTIVO.md) | por qué usarlo: problema, capacidades, valor diferencial, evidencia, límites |
| [INSTALACION](INSTALACION.md) | cómo instalar y configurar todo (plugin, credenciales y API-KEY §0.7, Orca opcional §0.8, Python, BMAD, skills externas, MCP, Cowork, Hermes), verificar y resolver problemas |
| [DEPENDENCIAS](DEPENDENCIAS.md) | cada dependencia con nivel, uso, versión probada, licencia, URL de origen y cómo se verificó |
| [ARQUITECTURA](ARQUITECTURA.md) | capas, precedencia PRINCE2/PMBOK, agentes vs subagentes, carga progresiva, presupuesto de descripciones |
| [INTEGRACIONES](INTEGRACIONES.md) | qué repositorio se integró y por qué, contratos, verificación en vivo, cómo agregar una integración |
| [sincronizacion](sincronizacion.md) | fuente única por dato, fachada `pm-spec-index/1`, líneas base, traspaso a BMAD |
| [SANIDAD](SANIDAD.md) | catálogo de comprobaciones INS, EST, ART, REG, ESP, INT y controles permanentes |
| [RACI](RACI.md) | quién decide, quién produce y quién registra, por rol humano, agente y skill |
| [CATALOGO](CATALOGO.md) | las 37 skills: disparadores, artefactos, agente, scripts |
| [colisiones](colisiones.md) | dueños únicos de cada artefacto y pistas de alcance entre skills |
| [CASOS-DE-USO](CASOS-DE-USO.md) | un caso por skill a lo largo del ciclo de vida |
| [CASOS-DE-USO-INTEGRACIONES](CASOS-DE-USO-INTEGRACIONES.md) | un caso por repositorio integrado: diseño visual, reportes, planificación, OKR, reuniones, trackers, BMAD |
| [CASO-MAESTRO](CASO-MAESTRO.md) | proyecto completo con BMAD, con comandos y salidas reales |
| [PRUEBAS](PRUEBAS.md) | niveles de prueba, qué cubre cada una, resultados registrados y lista de aceptación |
| [PUERTAS](PUERTAS.md) | qué se verifica en cada puerta (salud, controles PRINCE2 y BMAD, lista de control de la junta) y cómo se registra la decisión; diagrama del ciclo de vida PRINCE2 + BMAD |
| [PILOTO](PILOTO.md) | plan de piloto en paralelo: fases, métricas, rúbrica de revisión experta, prueba de usabilidad, criterios de decisión |
| [CHANGELOG](../CHANGELOG.md) | cambios por versión |
| [SPEC.md](../SPEC.md) | especificación de construcción y convenciones canónicas |
| [CLAUDE.md](../CLAUDE.md) · [AGENTS.md](../AGENTS.md) | cómo seguir desarrollando el paquete con agentes de código |
| [informe/](informe/README.md) | Informe 2 (HTML + PPTX, 158 diapositivas) y su generador |

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
| `scripts/validar_mermaid.py` | lint de los bloques Mermaid (errores que GitHub no renderiza) y render con mmdc; `--png` para inspección visual |
| `scripts/probar_paquete.py` | 80 pruebas de regresión (casos A–F) |
| `scripts/pruebas/generar_bmad_grande.py` | genera un BMAD sintético grande para pruebas de escala |
| `scripts/pruebas/fixtures/` | BMAD v6 sintético, BMAD 6.12.4 real, BMAD v4 |
| `scripts/pruebas_vivo/vivo.py` · `suite.py` · `escenarios.py` | arnés, suite y escenarios de robustez con Claude Code real |
| `docs/evaluacion/frases-enrutamiento.tsv` | 60 frases con la skill esperada (y aceptables) |
| `docs/evaluacion/resultados/` | informes de las pruebas en vivo v2.0 y v2.1 |
| `docs/ejemplos/` | salidas reales: traspaso a BMAD, informe de sanidad, WBS en Mermaid |
| `docs/ejemplos/integraciones/` | salidas reales de los casos de integración (MSPDI, Gantt, OKR, transcripción, avance BMAD, archify) |

## 5. Componentes del paquete

| Carpeta | Contenido | Documento de referencia |
|---|---|---|
| `agents/` | 6 agentes | [ARQUITECTURA](ARQUITECTURA.md), [RACI](RACI.md) |
| `skills/` | 37 skills con `references/`, `templates/`, `scripts/` | [CATALOGO](CATALOGO.md) |
| `hooks/` | `guardian.py`, `inicio.py`, `idioma.py`, `py.sh`, `hooks.json` | [INSTALACION §9](INSTALACION.md), [SANIDAD](SANIDAD.md) |
| `skills/pm-estado-proyecto/scripts/` | núcleo de scripts | [CATALOGO](CATALOGO.md) |
| `skills/pm-bmad-puente/scripts/bmad.py` | puente BMAD | [sincronizacion](sincronizacion.md) |
| `compatibilidad.json` | versiones probadas y dependencias | [DEPENDENCIAS](DEPENDENCIAS.md) |

## 6. Pendientes y puntos abiertos

- Ítems marcados `[verificar]` en INSTALACION y DEPENDENCIAS (URLs de sitios no alcanzables desde el entorno de prueba,
  pasos de Cowork y Hermes).
- Conectores MCP de terceros (Jira, Slack, Teams, Granola, Fireflies, Zoom, Tability) documentados pero no probados en
  vivo; los hooks en Windows con `py.sh` no se probaron en una máquina Windows real.
- Mejoras candidatas: Monte Carlo de contingencia (P50/P80); calendarios y feriados en `cpm.py`; trazado de
  `bmad-spec` (`SPEC.md`, ids `CAP-n`).
