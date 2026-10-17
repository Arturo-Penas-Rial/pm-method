# Integraciones · pm-method 2.0.0

Qué necesita pm-method para funcionar, con qué herramientas externas puede integrarse, qué se decidió incorporar (y
qué no) y cómo agregar una integración nueva sin romper el ecosistema.

Principio rector: **el núcleo funciona sin nada externo.** Cada integración es un contrato de insumo/salida con un
**respaldo interno** (Mermaid, CSV, scripts propios). Si la herramienta externa no está o falla, la skill sigue con el
respaldo y lo anota.

---

## 1. Dependencias

Fuente: `compatibilidad.json`.

| Tipo | Dependencia | Uso | Si falta |
|---|---|---|---|
| Obligatoria | Python ≥ 3.9 | todos los scripts | no hay ejecución |
| Obligatoria | — (`dependencias.obligatorias` vacío) | el núcleo usa solo la biblioteca estándar | — |
| Recomendada | `pyyaml` | leer la configuración de BMAD y `sprint-status.yaml` | el puente BMAD no funciona; sanidad INS-01 |
| Recomendada | `python-docx` | exportar `.docx`, leer actas `.docx` | sin exportación Word; INS-01 |
| Recomendada | `openpyxl` | exportar `.xlsx` | sin exportación Excel; INS-01 |
| Opcional | `@mermaid-js/mermaid-cli` (`mmdc`) | Mermaid como imagen en Word | los diagramas quedan como código Mermaid |
| Opcional | Java + `mpxj` | validar o convertir MSPDI / `.mpp` | `cpm.py --mspdi` genera igual el XML |
| Opcional (marco) | BMAD Method (instalado por el equipo con `npx bmad-method install`) | capa de especificación | el proveedor de la especificación es pm-method (`requisitos.md`, `backlog.csv`, `wbs.csv`) |

---

## 2. Decisiones de integración

Los candidatos provienen de un informe previo de relevamiento; la valoración en estrellas es la de ese informe.

| Candidato | Valoración | Decisión v2 | Dónde | Justificación |
|---|---|---|---|---|
| BMAD Method | — (marco) | **Integrado** como capa de especificación de solo lectura, con contrato por patrones y fachada | `pm-bmad-puente`, `especificacion.py` | Aporta lo que PRINCE2 no detalla (qué debe hacer el producto). Como sus formatos cambian en casi cada versión menor 6.x, se aísla detrás de un único lector (`bmad.py`) y una fachada (`pm-spec-index/1`): las demás skills no dependen de BMAD |
| archify | ★★★★★ | **Opcional** por contrato de insumo; respaldo Mermaid | `pm-visuales` | Buena calidad de diagramas, pero es una skill externa: pm-visuales prepara el insumo y conserva siempre el Mermaid |
| diagram-design | ★★★★★ | **Opcional**, igual que archify | `pm-visuales` | Ídem |
| visual-explainer | ★★★★ | **Opcional** (one-pagers), igual | `pm-visuales` | Ídem; útil para resúmenes de una página |
| drawio-mcp (oficial) | ★★★★ | **Opcional** vía MCP | `pm-visuales` / `pm-integraciones` | Diagramas editables por el usuario; entra como capacidad MCP, no como dependencia |
| Skills oficiales docx/xlsx/pptx | ★★★★ | **Opcional**; respaldo `exportar.py` | `pm-exportar` | Mejor acabado Office cuando están instaladas; sin ellas, `exportar.py` cubre `.docx`/`.xlsx` y, sin `pptx`, se entrega un guion Markdown del deck |
| Atlassian Rovo MCP, Slack MCP, Teams/Work IQ | ★★★★ | **Capacidades genéricas**, sin conector predefinido | `pm-integraciones` | Las organizaciones usan herramientas distintas; atar el paquete a un conector lo haría frágil. Se describen capacidades (tracker, docs, chat) y se resuelven con lo que haya en la sesión |
| Granola / Fireflies / Zoom / minutes (MCP) + transcripciones VTT/SRT | ★★★★ | **Fuente de transcripciones** vía MCP o archivo | `pm-reuniones` (`transcripcion.py`) | La transcripción es un insumo; el valor está en el acta y en los registros. Archivo local siempre disponible como respaldo. Zoom MCP: obtención de transcripciones **no confirmada** |
| meeting-analyzer | ★★★★ | **No incorporado** | `pm-reuniones` | Se aplican reglas de privacidad propias: clima del equipo solo agregado, con consentimiento y anonimizado; sin perfiles emocionales individuales |
| Tability MCP | ★★★ | **Opcional** para OKR | `pm-okr` | Lectura de progreso a instantánea; escritura solo con confirmación. No existe un formato estándar de OKR, por eso el registro propio es `okr.csv` |
| Operately / okr-writer | ★★★★ | **No incorporados** | `pm-okr` (`okr.py`) | Operately es una aplicación sin MCP; okr-writer, una skill externa. Se optó por OKR propio en CSV con vínculo a beneficios (B-n) y métricas de éxito (SM-n) |
| utf8proj + MPXJ | ★★★★ | utf8proj **descartado**; exportador MSPDI **propio**, validado con MPXJ; MPXJ **opcional** para `.mpp` | `pm-cronograma-estimacion` (`cpm.py --mspdi`) | utf8proj es inmaduro (v0.10.0, pre-1.0, 6 estrellas). MSPDI es un formato XML abierto (solo `UID` obligatorio en Task); el exportador propio evita la dependencia y se validó leyéndolo con MPXJ (PyPI `mpxj` 16.10.0, LGPL, requiere Java) |
| knowledge-work-plugins status-report / dashboards | ★★★★ | **No incorporado** | — | Duplica `pm-progreso-reportes` y `pm-visuales`, y generaría dos dueños para el mismo informe |
| cost-core / Monte Carlo | ★★★ | **No incorporado en v2** | — | Madurez insuficiente; candidato futuro para contingencia P50/P80 |
| gonzalezpazmonica/pm-workspace | — | **Excluido** | — | A pedido del usuario (pesado, riesgoso) |

Referencias consultadas al 2026-10-17 que condicionan las decisiones: el servidor "Teams (preview)" de Microsoft está
marcado como legado (se recomienda Work IQ); el Slack MCP oficial (`https://mcp.slack.com/mcp`) está restringido a apps
publicadas o internas; Atlassian Rovo MCP Server requiere obtener el `cloudId` con `getAccessibleAtlassianResources`
antes de usar herramientas como `searchJiraIssuesUsingJql` o `createJiraIssue`; Operately es Apache-2.0 sin MCP;
minutes es MIT (`minutes-mcp`); phuryn/pm-skills (MIT, brainstorm-okrs) se relevó como referencia.

---

## 3. Contrato de cada integración

Cada integración se declara en `estado.json.integraciones` (`estado.py integracion clave=valor`) y cumple tres reglas:
**insumo** preparado por la skill dueña, **salida** guardada en la carpeta del proyecto y **respaldo** interno.

| Integración | Clave y valor | Skill dueña | Insumo | Salida | Respaldo |
|---|---|---|---|---|---|
| BMAD | `especificacion=bmad` (+ `bmad.raiz`, `layout`, `soporte`) | `pm-bmad-puente` | artefactos de `_bmad-output/` o `docs/` (solo lectura) | derivados en `02-planificacion/especificacion/` (`inventario-bmad.json`, `requisitos-bmad.csv`, `matriz-trazabilidad-bmad.csv`, `spec-index.json`), columnas derivadas de `backlog.csv`, `03-control/reportes/avance-bmad.csv`, líneas base en `00-direccion/historial/bmad-<art>-v<ver>/`, traspasos `handoff-bmad-<fecha>-<…>.md` | `especificacion=ninguna`: `requisitos.md`, `backlog.csv`, `wbs.csv` con el mismo contrato `pm-spec-index/1` |
| Diagramas externos | `diagramas=archify\|diagram-design\|visual-explainer` | `pm-visuales` | insumo preparado desde registros, WBS, plan o resumen de la especificación | `02-planificacion/visuales/` o `03-control/reportes/` | Mermaid, siempre conservado; nota en `diario.md` si la externa falla |
| draw.io | `diagramas=drawio` | `pm-visuales` / `pm-integraciones` | igual que el anterior, por MCP | igual | Mermaid |
| Office | `export=skills-office` | `pm-exportar` | artefactos Markdown con frontmatter | `exportados/` (nunca fuente de verdad) | `export=scripts`: `exportar.py` (docx/xlsx), `paquete.py` (ZIP); sin `pptx`, guion Markdown |
| Cronograma MS Project | `cronograma=mspdi` | `pm-cronograma-estimacion` | `actividades.csv` (+ `wbs.csv`) | `02-planificacion/cronograma.xml` (MSPDI; copia en `exportados/`) | `cronograma=cpm`: CPM y Gantt Mermaid de `cpm.py` |
| Tracker | `tracker=jira\|linear\|github\|azure-devops` | `pm-integraciones` | consultas de lectura; vista previa para escrituras | instantánea `03-control/fuentes/<sistema>-AAAA-MM-DD.<ext>`; propuestas de cambio a registros | registros CSV (`backlog.csv`, `acciones.csv`) |
| Documentación | `docs=confluence\|notion\|sharepoint` | `pm-integraciones` | lectura de páginas; publicación con confirmación | instantánea o página publicada (id anotado) | Markdown local |
| Chat / correo | `chat=slack\|teams` | `pm-integraciones`, `pm-comunicacion-stakeholders` | mensaje con vista previa | id externo en `notas` o `diario.md` | borrador para copiar |
| Reuniones | `reuniones=manual\|archivo\|granola\|fireflies\|zoom\|minutes` | `pm-reuniones` | transcripción por MCP o archivo `.vtt`/`.srt`/`.txt`/`.docx` | `03-control/reuniones/` (transcripción normalizada y acta); registros solo tras confirmación de quien presidió | texto pegado o archivo |
| OKR | `okr=archivo\|tability` | `pm-okr` | progreso leído vía `pm-integraciones` | `03-control/fuentes/tability-AAAA-MM-DD.csv` → columna `actual` de `00-direccion/okr.csv` | `okr.csv` mantenido a mano con `okr.py` |

Reglas comunes:
- Lectura libre; **escritura externa solo con vista previa y confirmación explícita**, una vez por lote. En un
  subagente se devuelve como "decisión humana requerida".
- Instantáneas **fechadas e inmutables**; una nueva lectura crea un archivo nuevo. Se citan como fuente en los informes.
- Las diferencias entre una fuente externa y los registros se **proponen**, no se aplican en silencio; los cambios de
  alcance van a `pm-issues-cambios`.
- Nunca credenciales en la carpeta del proyecto ni en el paquete.

---

## 4. Control de consistencia

La sanidad (`sanidad.py`, skill `pm-sanidad`) vigila las integraciones; los hallazgos INS no bloquean puertas, pero se
informan.

| Código | Severidad | Qué controla |
|---|---|---|
| INS-01 | AVISO | módulos Python recomendados (`pyyaml`, `python-docx`, `openpyxl`) |
| INS-03 | AVISO / INFO | la skill externa declarada en `integraciones.diagramas` (archify, diagram-design, visual-explainer) está instalada; si no, propone volver a `mermaid` |
| INS-05 | AVISO | presupuesto del listado de skills, incluidas las de BMAD y otros repos (umbral ≈8.000 caracteres) |
| INS-06 | AVISO | posible colisión de activación entre una skill externa y una pm-* (tres o más disparadores compartidos) |
| INT-01 | AVISO | valores de `integraciones` conocidos para `tracker`, `chat`, `docs`, `reuniones`, `okr` y `especificacion` |
| INT-02 | AVISO | tracker declarado sin instantáneas en `03-control/fuentes/` durante la fase de entrega |
| INT-03 | AVISO | última instantánea del tracker con más de 14 días |
| INT-04 | AVISO | instantánea sin fecha en el nombre (`<sistema>-AAAA-MM-DD.<ext>`) |
| ESP-01…15 | ERROR / AVISO | especificación legible, cobertura, ids, versión de BMAD probada, carpeta fuera de BMAD, líneas base vs especificación (cambio no controlado), traspasos pendientes, derivados desactualizados |

Controles adicionales:
- **Hook `PreToolUse`** (plugin de Claude Code): impide editar a mano los derivados de la especificación y que los
  subagentes pm-* escriban en carpetas de BMAD.
- **`pm-puerta` / `pm-director`**: ninguna puerta con ERROR sin decisión humana registrada como condición.
- **`compatibilidad.json`**: declara versiones probadas de BMAD (4.x, 6.11, 6.12), integraciones externas opcionales y
  comportamiento por cliente.
- **`scripts/probar_paquete.py`**: regresión de punta a punta con BMAD v6, BMAD v4 y sin BMAD (35 pruebas).

Observación: INT-01 no valida hoy las claves `diagramas`, `cronograma` ni `export`; para `diagramas` actúa INS-03.

---

## 5. Cómo agregar una integración nueva

Lista de verificación para incorporar una herramienta sin romper el ecosistema:

**Decisión**
- [ ] La necesidad no está cubierta por una skill existente (revisar `docs/colisiones.md` y `docs/CATALOGO.md`); si
      duplicaría un dueño, no se incorpora.
- [ ] Madurez y licencia evaluadas y anotadas en la tabla de §2 con su justificación.
- [ ] Se define como **capacidad** (qué hace), no como conector concreto, salvo que sea un formato de archivo.

**Contrato**
- [ ] Una sola skill dueña de la integración; las demás la consumen a través de ella.
- [ ] Insumo, salida y **respaldo interno** definidos; el flujo funciona igual si la herramienta falta.
- [ ] Salidas en la carpeta del proyecto (`03-control/fuentes/` con nombre fechado si son datos externos); nunca
      reemplazan un registro de gobierno.
- [ ] Escrituras externas solo con vista previa y confirmación; en subagentes, como decisión humana requerida.
- [ ] Sin credenciales ni `.mcp.json` en el paquete.

**Estado y validación**
- [ ] Valor nuevo en `estado.json.integraciones` documentado en `SPEC.md` §1.6 y en la tabla de capacidades de
      `pm-integraciones/references/guia.md`.
- [ ] Valor agregado a la lista de conocidos de `sanidad.py` (INT-01) y, si es una skill externa, a la comprobación de
      instalación (como INS-03).
- [ ] Si genera archivos derivados, agregarlos a la protección de `hooks/guardian.py`.
- [ ] Entrada en `compatibilidad.json` (`integraciones_externas_opcionales`).

**Activación y contexto**
- [ ] La descripción de la skill dueña sigue el formato `Objeto. Usar: … No: …→…`, ≤ 240 caracteres, y el listado
      total del paquete sigue ≤ 7.500 caracteres.
- [ ] Si se agregan disparadores, actualizar `docs/colisiones.md` y repetir la evaluación de enrutamiento
      (`docs/evaluacion/frases-enrutamiento.tsv`) con frases nuevas.
- [ ] El cuerpo de `SKILL.md` sigue dentro de ≤ 12.000 caracteres y ≤ 200 líneas; el detalle va a `references/guia.md`.

**Pruebas**
- [ ] `python3 scripts/validar_paquete.py` termina en `OK`.
- [ ] `python3 scripts/probar_paquete.py` sin fallos; si la integración tiene lógica en scripts, agregar un caso.
- [ ] `sanidad.py --informe` sobre un proyecto de prueba sin ERROR nuevos.
- [ ] Documentación actualizada: este archivo, `INSTALACION.md` §6 y `README.md`.
