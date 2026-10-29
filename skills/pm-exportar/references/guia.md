# Guía de exportación y paquetes · Export and packages guide

Detalle de `pm-exportar`. El mapeo técnico de cada formato (Markdown → docx, CSV → xlsx, deck, contenido de los ZIP)
está en `references/formatos.md`; esta guía reúne las vías, la convención de nombres y las reglas extendidas.

## 1. Vías por formato
| Formato | Vía por defecto (`integraciones.export = scripts`) | Vía con skills oficiales (`skills-office`) | Qué no cubre el script |
|---|---|---|---|
| `.docx` | `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/exportar.py docx` | skill `docx` (plantilla `.dotx`, portada, índice, marca de agua en todas las páginas, imágenes, control de cambios) | cursiva, enlaces, imágenes `![]()`, metadatos en portada (Mermaid solo con `mmdc`) |
| `.xlsx` | `exportar.py xlsx` | skill `xlsx` (fórmulas, formato condicional, filtros, validación, gráficos, hoja Resumen/Notas) | fórmulas vivas y semáforos |
| `.pptx` | no disponible: guion Markdown del deck (`formatos.md` §3) | skill `pptx` con el esquema de `formatos.md` §3 | todo |
| `.zip` (paquetes) | `${CLAUDE_SKILL_DIR}/../pm-exportar/scripts/paquete.py` | n/a | conversión de formatos (se hace antes) |
| `.pdf` | no cubierto | skill `pdf`, a partir del `.docx` | todo |
| `.xml` MS Project | lo genera `cpm.py --mspdi` (`pm-cronograma-estimacion`); aquí solo se incluye en paquetes con `--extra` | — | — |

Detalle de comandos (vía `scripts`):
- `.docx`: `exportar.py docx --entrada <ruta.md> --salida exportados/<nombre>.docx` (encabezados, listas, tablas, negritas, banda de borrador; Mermaid como imagen con `mmdc`, si no como código con aviso; `formatos.md` §1).
- `.xlsx`: `exportar.py xlsx --proyecto <dir> --salida exportados/AAAA-MM-DD-registros-v<n>.xlsx` (todas las hojas, incluida `stakeholders`: quitarla o exportar aparte si la audiencia es externa) o `--entrada <csv> --salida <xlsx>` (`formatos.md` §2). **Solo lee CSV**: un artefacto Markdown con tablas (presupuesto, hoja de costeo) se exporta desde su CSV hermano (`02-planificacion/linea-base-costo.csv`, `wbs.csv`); si no existe, avisar y ofrecer el `.docx` del Markdown o la skill `xlsx`. No improvisar planillas a mano.
- `.pptx`: con la skill `pptx` siguiendo el esquema de deck de puerta (título, estado contra tolerancias, productos, riesgos, decisiones requeridas); sin ella, `exportados/<nombre>-deck.md` y avisar que falta la skill.

### 1.1 Skills oficiales de Office (`integraciones.export = skills-office`) — verificado en vivo, Claude Code 2.1, 2026-10-17
Origen: `anthropics/skills` (carpetas `skills/docx`, `skills/xlsx`, `skills/pptx`; licencia **propietaria** de Anthropic, "source-available", no MIT). Se ven con nombres distintos según cómo se instalaron, y **cualquiera vale**:

| Instalación | Nombre en el listado | Comando |
|---|---|---|
| Plugin del marketplace oficial | `document-skills:docx`, `:xlsx`, `:pptx` (y `:pdf`) | `/plugin marketplace add anthropics/skills` + `/plugin install document-skills@anthropic-agent-skills` |
| Copia como skills del proyecto o del usuario | `docx`, `xlsx`, `pptx` | `npx skills add anthropics/skills -a claude-code -s docx xlsx pptx -y` (agregar `-g` para el usuario) |
| Skills de claude.ai / Cowork sincronizadas | `anthropic-skills:docx`, `:xlsx`, `:pptx` | habilitarlas en claude.ai (Capacidades) |

`sanidad.py` (INS-03) informa cuál está y con qué nombre invocarla. Requisitos: Node.js con el paquete npm `docx` (Word) o `pptxgenjs` (PowerPoint) resoluble por `require` (si falla: `npm install docx` / `npm install pptxgenjs` en una carpeta de trabajo fuera del proyecto); Python con `openpyxl` (Excel); LibreOffice para recalcular fórmulas (`scripts/recalc.py`) y para la vista previa en PDF; `pandoc` para leer `.docx`.

**Contrato de delegación** (obligatorio con `skills-office` y la skill presente):
1. pm-exportar resuelve qué exportar, el estado de la fuente y el **nombre final** (§2) antes de invocar.
2. Invocar la skill con la herramienta Skill por su nombre real y entregarle: el contenido limpio (Markdown sin frontmatter, o filas CSV / tablas Markdown), el bloque de metadatos de portada (`formatos.md` §1.3), la ruta exacta `exportados/AAAA-MM-DD-<tipo>-v<n>[-BORRADOR].<ext>`, la marca "BORRADOR / DRAFT" si la fuente no está aprobada (banda en portada y encabezado o marca de agua en todas las páginas), la declaración de asistencia de IA y la fecha de corte.
3. Excel: una hoja por tabla o registro, totales como **fórmulas** (`=SUM(...)`), hoja "Notas" con fuente de cada cifra; recalcular con `python <xlsx>/scripts/recalc.py <archivo>` y no entregar con `errors_found`. Word: respetar el orden de secciones de la fuente. Deck: esquema de `formatos.md` §3.
4. Los scripts temporales de la skill (`.js`, `.py`) van a una carpeta de trabajo fuera de la carpeta del proyecto; en `exportados/` solo queda el archivo final.
5. Verificar: el archivo abre (`python-docx` / `openpyxl` / `python-pptx`), contiene la marca BORRADOR cuando corresponde y las tablas completas; anotar en `diario.md` la vía usada.
6. Si la skill no está en el listado o falla dos veces: `exportar.py` (docx/xlsx) o guion Markdown (pptx), con nota inmediata en `diario.md` ("skill X no disponible/falló: <causa>; se usó exportar.py"), sin esperar la confirmación de envío.

## 2. Convención de nombres y versionado
- `exportados/AAAA-MM-DD-<tipo>-v<version>[-BORRADOR].<ext>`; `<tipo>` = `tipo` del frontmatter (`plan-etapa-2`, `informe-fin-etapa-2`, `registros`, `deck-autorizar-cierre`) o `paquete-<puerta>` para los ZIP.
- Clave en `estado.json`: `exportado-<tipo>` (p. ej. `exportado-paquete-autorizar-etapa`), nunca la clave de la fuente.
- `v<version>` copia la `version` del frontmatter; para paquetes y libros de registros, correlativo por puerta (`v1`, `v2`). No inventar versiones.
- `-BORRADOR` obligatorio si la fuente no está `aprobado`; en paquetes, si falta un obligatorio o un obligatorio sigue en `borrador` (`en-revision` se acepta). `paquete.py` lo añade solo.
- Ejemplos: `2026-10-16-plan-etapa-2-v1.0.docx` · `2026-10-16-registros-v3-BORRADOR.xlsx` · `2026-10-16-paquete-autorizar-etapa-v1.zip` · `2026-10-16-deck-autorizar-cierre-v0.2-BORRADOR.pptx`.
- Un exportado `aprobado` es inmutable; los reemplazados se mueven a `exportados/obsoletos/` solo a pedido del usuario.

## 3. Contenido mínimo de cada paquete (coincide con `paquete.py`)
| Paquete | Obligatorios (clave canónica) | Opcionales |
|---|---|---|
| autorizar-inicio | `project-brief`, `estructura-organizativa`, `plan-etapa-1` (iniciación), `descripcion-producto-proyecto` | business case esquemático, `solicitud-autorizar-inicio`, canvas, mandato |
| autorizar-proyecto | `pid`, `business-case`, `plan-proyecto`, `plan-etapa-<n+1>` (primera de entrega = 2) | enfoques, `solicitud-autorizar-proyecto`, registros |
| autorizar-etapa | `informe-fin-etapa-<n>`, `plan-etapa-<n+1>`, `business-case`, `plan-proyecto` | `solicitud-autorizar-etapa`, registros `.xlsx`, tablero, deck |
| autorizar-plan-excepcion | `informe-excepcion-X-###`, `plan-excepcion-X-###`, `business-case` | plan de proyecto, evaluación de excepción, `solicitud-autorizar-plan-excepcion`, registros |
| cierre | `informe-fin-proyecto`, `registro-aceptacion`, `informe-lecciones`, `recomendaciones-seguimiento`, `plan-revision-beneficios`, business case original (`00-direccion/historial/business-case-v1.0.md`) y final, registros | PID original (`historial/pid-v1.0.md`), `solicitud-autorizar-cierre`, `handover`, cierres de contrato, `notificacion-cierre`, actas |

`paquete.py` busca cada producto por su clave en `estado.json.artefactos` y, si no está, por patrones de ruta; incluye
registros (el `.xlsx` de `exportados/` si existe, si no los CSV) y un `MANIFIESTO.md` (archivo, origen, versión, estado,
obligatorio/opcional, aprobador). Nunca reincluye un `exportado-*` ni un `.zip`. La solicitud de decisión figura como
opcional en el script, pero el método la exige: si falta, pedirla a `pm-director`.

Con BMAD (`integraciones.especificacion = bmad`), en `autorizar-proyecto`, `autorizar-etapa` y cierre conviene agregar con
`--extra` la matriz `02-planificacion/especificacion/matriz-trazabilidad-bmad.csv` y la línea base congelada
`00-direccion/historial/bmad-prd-v<ver>/`; nunca se copian archivos de las carpetas de BMAD.

### 3.1 Expediente de auditoría y verificación de integridad
Para la PMO, una auditoría interna, una due diligence o la entrega a un cliente, el expediente reúne bajo demanda la
evidencia que ya está en la carpeta del proyecto, sin reescribirla:
`python3 ${CLAUDE_SKILL_DIR}/../pm-exportar/scripts/paquete.py --proyecto <dir> auditoria [--desde AAAA-MM-DD] [--hasta AAAA-MM-DD] [--proposito "…"] [--externo] [--con-bitacora] [--salida …] [--extra …]`
→ `exportados/<hoy>-expediente-auditoria[-<desde>_<hasta>].zip`.

| En el ZIP | De dónde sale |
|---|---|
| `INDICE.md` e `INDICE.html` (escapado, con enlaces) | alcance (propósito, período, corte, fase y etapa), cronología, líneas base, registros, evidencia de puertas, comunicaciones, sanidad y manifiesto |
| `cronologia.csv` | puertas de `estado.json` (con su D-### y la lista de control confirmada), `decisiones.csv` (aprobaciones `aprobado <clave> v<ver>`, presupuestos, decisiones de la reunión), cambios decididos, riesgos aceptados (`respuesta=aceptar`), productos aceptados (`calidad.csv`) y envíos realizados (`envios.csv`, por id de interesado) |
| `estado.json` y `03-control/registros/*.csv` | copia byte a byte; con período, las filas cuya fecha cae en él y las que no tienen fecha |
| `00-direccion/historial/**` | líneas base congeladas (aprobaciones de `estado.py aprobar` y de `bmad.py linea-base`) |
| `00-direccion/decisiones/**` | listas de verificación de puertas, solicitudes y actas de junta |
| `03-control/reuniones/*acta*`, `03-control/reportes/*` (incluidos los cortes `evm-*.json`), `03-control/comunicaciones/**`, `04-cierre/*aceptacion*` | comunicaciones, informes y aceptaciones (con período, se omiten los fechados fuera de él) |
| `sanidad-<corte>.json` | `sanidad.py --json --corte <hasta o hoy>` (solo lectura) |
| `bitacora.jsonl` (solo con `--con-bitacora`) | `<proyecto>/.bitacora.jsonl` completa aunque haya período (cadena de huellas: qué script escribió qué campo, cuándo y a nombre de quién; sin valores de interesados ni confidenciales; SPEC §1.10.16) |
| `MANIFIESTO.md` y `SHA256SUMS` | sha256 de cada archivo |

Los paquetes de puerta ya generados (`exportados/*.zip`) se citan en el índice con su huella y no se reincluyen; una ruta
de `--extra` fuera del proyecto se excluye y se anota. `--externo` (cliente, proveedor, due diligence) deja fuera el
registro de interesados y sus valoraciones (`stakeholders`, `estereotipos`, `preferencias`, regla 12) y el destino de
los envíos. El expediente no aprueba ni dictamina.

**Verificar:** `paquete.py --proyecto <dir> verificar <zip>` recalcula el sha256 de cada archivo y lo compara con
`SHA256SUMS`: informa alterados, faltantes y agregados (código 1) o `INTEGRIDAD: OK`. Si el expediente lleva la
bitácora, para cada `estado.json` o registro alterado muestra su última escritura anotada (línea, fecha, script,
operación, `--por`, ids) y si esa escritura dejó la versión del expediente: entonces la diferencia de la copia recibida no
salió de los scripts. Respaldo: PRINCE2 7, líneas base y
gestión de configuración (pista de auditoría de todos los cambios, archivo de versiones anteriores:
`pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §3.c.4), registro del proyecto (§5.4 A13)
y enfoque de gestión de datos (integridad y auditorías de datos, §4.d); PMBOK 8, auditorías
(`pmbok8-artefactos-tecnicas-anexos.md`, fila "Auditorías": confirmar la implementación de cambios aprobados).

## 4. Revisión del resultado
Abrir o listar el archivo generado: tablas íntegras, frontmatter no visible, marca BORRADOR cuando corresponde, orden de
secciones igual a la fuente, manifiesto coincidente con el contenido.

## 5. Reglas extendidas
1. [PRINCE2] El contenido mínimo de cada paquete sigue lo que la junta revisa en Directing a project (§3).
2. [PRINCE2] Un paquete de puerta con un informe de excepción pendiente lo declara en el manifiesto y en el deck.
3. [PMBOK→Progress] En los `.xlsx`, las fórmulas (puntuación de riesgo, EVM) se exportan como fórmulas o se documentan en una hoja "Notas", nunca como cifras sin origen.
4. [PMBOK→Progress/DP] Guardarraíl de IA: el exportado declara en portada o en "Notas" que se generó con asistencia de IA, el nivel de intervención (automatización: conversión de formato) y la fecha de corte de los datos.
5. [PMBOK→Organizing] Recordar la política de la organización antes de exportar documentos con datos de clientes, contratos o nóminas.
6. [Plantillas] Versión mínima: un `.docx` con brief + business case y un `.xlsx` con los registros; completa: ZIP con manifiesto y deck.
7. [Plantillas] El orden de secciones del `.docx` respeta el de la plantilla fuente; no se reordena ni se resume.
8. El manifiesto lista cada archivo con ruta de origen, versión, estado y aprobador; sin manifiesto el paquete no está completo.

## 6. Ejemplos adicionales
- "Prepará el paquete de cierre del proyecto Faro con el informe final, la aceptación y las lecciones."
- "Build the stage-gate deck for the board: status, products, risks and decisions needed."
- "Export all registers to one Excel workbook with a sheet per register."
