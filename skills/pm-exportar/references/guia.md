# Guía de exportación y paquetes · Export and packages guide

Detalle de `pm-exportar`. El mapeo técnico de cada formato (Markdown → docx, CSV → xlsx, deck, contenido de los ZIP)
está en `references/formatos.md`; esta guía reúne las vías, la convención de nombres y las reglas extendidas.

## 1. Vías por formato
| Formato | Vía por defecto (`integraciones.export = scripts`) | Vía con skills oficiales (`skills-office`) | Qué no cubre el script |
|---|---|---|---|
| `.docx` | `<pm-estado-proyecto>/scripts/exportar.py docx` | skill `docx` (plantilla `.dotx`, portada, índice, marca de agua en todas las páginas, imágenes, control de cambios) | cursiva, enlaces, imágenes `![]()`, metadatos en portada (Mermaid solo con `mmdc`) |
| `.xlsx` | `exportar.py xlsx` | skill `xlsx` (fórmulas, formato condicional, filtros, validación, gráficos, hoja Resumen/Notas) | fórmulas vivas y semáforos |
| `.pptx` | no disponible: guion Markdown del deck (`formatos.md` §3) | skill `pptx` con el esquema de `formatos.md` §3 | todo |
| `.zip` (paquetes) | `<pm-exportar>/scripts/paquete.py` | n/a | conversión de formatos (se hace antes) |
| `.pdf` | no cubierto | skill `pdf`, a partir del `.docx` | todo |
| `.xml` MS Project | lo genera `cpm.py --mspdi` (`pm-cronograma-estimacion`); aquí solo se incluye en paquetes con `--extra` | — | — |

Detalle de comandos:
- `.docx`: `exportar.py docx --entrada <ruta.md> --salida exportados/<nombre>.docx` (encabezados, listas, tablas, negritas, banda de borrador; Mermaid como imagen con `mmdc`, si no como código con aviso; `formatos.md` §1).
- `.xlsx`: `exportar.py xlsx --proyecto <dir> --salida exportados/AAAA-MM-DD-registros-v<n>.xlsx` (todas las hojas, incluida `stakeholders`: quitarla o exportar aparte si la audiencia es externa) o `--entrada <csv> --salida <xlsx>` (`formatos.md` §2).
- `.pptx`: con la skill `pptx` siguiendo el esquema de deck de puerta (título, estado contra tolerancias, productos, riesgos, decisiones requeridas); sin ella, `exportados/<nombre>-deck.md` y avisar que falta la skill.

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
