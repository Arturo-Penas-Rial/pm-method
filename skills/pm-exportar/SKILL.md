---
name: pm-exportar
description: "Exportados Office, paquetes ZIP de puerta o cierre y expediente de auditoría. Usar: exportar a Word, Excel, PowerPoint, paquete de puerta, gate package, audit pack. No: tablero→pm-visuales; informe→pm-progreso-reportes."
version: 2.5.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [DP, IP, SB, CP]
    practicas_prince2: [progress, organizing]
    tecnicas_pmbok: [informes de desempeño, gestión de la información del proyecto]
    artefactos: [exportados docx, exportados xlsx, exportados pptx, paquete-puerta.zip, paquete-cierre.zip, expediente-auditoria.zip]
    idiomas: [es, en]
---

# Exportación a Office y paquetes · Office export and packages

**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro.

## Cuándo usar / When to use
- Un artefacto Markdown o un registro CSV debe entregarse como `.docx`, `.xlsx` o `.pptx` a la junta, al cliente, a un proveedor o a una PMO.
- Se prepara una **puerta** o el **cierre** y la junta quiere todo en un ZIP con la solicitud de decisión y un manifiesto.
- Se necesita un deck de puerta de etapa (stage-gate deck) con estado, productos, riesgos y decisiones requeridas.
- La PMO, una auditoría interna, una due diligence o un cliente piden el expediente: decisiones, aprobaciones, líneas base, cambios, riesgos, aceptaciones, comunicaciones y evidencia de puertas, con huellas verificables.
- EN: export to Word, Excel or PowerPoint; bundle the gate or closure package as a ZIP.
- EN: file a versioned, dated export under `exportados/`.

## Idioma
Los exportados conservan el idioma de la fuente (`estado.json.idioma`); nombres de archivo en kebab-case español con fecha ISO. Primera mención con el EN: paquete de puerta (gate package), paquete de cierre (closure package), deck de puerta de etapa (stage-gate deck).

## Conocimiento
- `references/formatos.md` (este skill): §1 Markdown → docx, §2 CSV → xlsx, §3 esquema del deck, §4 contenido de cada ZIP.
- `references/guia.md` (este skill): §1 vías por formato, §2 nombres y versionado, §3 contenido mínimo de paquetes (§3.1 expediente de auditoría y verificación), §4 revisión, §5 reglas extendidas.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` — `### 5.2` (qué revisa la junta en cada puerta) y `### 5.7` (productos del cierre).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` — `## 5.` (composición de los productos de gestión) y `### 7.5` (informe de destacados, base del deck).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` — `### 2.7` (nivel de detalle por audiencia) y `### 5.3` (guardarraíles de IA).

## Entradas requeridas
- Carpeta con `estado.json` y artefactos con frontmatter (`tipo`, `version`, `estado`, `aprobado_por`).
- Python 3 con `python-docx` y `openpyxl` para `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/exportar.py` (avisa si faltan); opcional `mmdc` para Mermaid como imagen.
- `estado.json.integraciones.export`: `scripts` (defecto) o `skills-office`: skills oficiales de Office, que en el listado aparecen como `docx`/`xlsx`/`pptx`, `document-skills:<x>` (plugin) o `anthropic-skills:<x>` (claude.ai); cualquiera vale (INS-03, guía §1.1). Sin `pptx`, guion Markdown del deck.
- Paquetes: artefactos registrados con su clave canónica (SPEC §1.10.3).
- Ningún conector es obligatorio; subir o enviar a un sistema externo va por `pm-integraciones` o `pm-comunicacion-stakeholders`, con confirmación.

## Procedimiento
1. **Qué y para quién**: artefacto(s), formato, audiencia (junta, cliente, proveedor, PMO), borrador o aprobado. Audiencia externa → regla de información sensible de la matriz de comunicaciones.
2. **Estado de la fuente** (frontmatter y `estado.json.artefactos`): si no es `aprobado`, `exportar.py docx` pone la banda "BORRADOR / DRAFT" y el nombre lleva `-BORRADOR`. Nunca un borrador sin marca.
3. **Elegir la vía** (guía §1). Con `skills-office` y la skill del formato en el listado, **delegar siempre**: invocarla con la herramienta Skill y entregarle contenido limpio, metadatos de portada, ruta final, marca BORRADOR y fecha de corte; Excel con fórmulas y `recalc.py` (guía §1.1). Si no está o falla: `exportar.py docx --entrada <md> --salida exportados/<nombre>.docx`; `exportar.py xlsx --proyecto <dir> --salida exportados/AAAA-MM-DD-registros-v<n>.xlsx` o `--entrada <csv>` (solo CSV: un Markdown con tablas sale de su CSV hermano, p. ej. `linea-base-costo.csv`); deck: guion `exportados/<nombre>-deck.md`; anotar ya en `diario.md` la vía de respaldo y su causa (no espera la confirmación del paso 8).
4. **Nombrar y versionar**: `exportados/AAAA-MM-DD-<tipo>-v<version>[-BORRADOR].<ext>`; versión del frontmatter; un aprobado nunca se sobrescribe (guía §2).
5. **Paquete de puerta**: `python3 ${CLAUDE_SKILL_DIR}/../pm-exportar/scripts/paquete.py --proyecto <dir> listar puerta <tipo>` (obligatorios, opcionales y faltantes, sin crear nada) y luego `paquete.py --proyecto <dir> puerta <tipo> [--salida ..] [--extra <ruta> …]`. Incluye los productos obligatorios de la puerta, registros y `MANIFIESTO.md`, más la `solicitud-<puerta>` de `pm-direccion-decisiones` si existe (es opcional en `listar`); faltante o borrador obligatorio → ZIP `-BORRADOR` (guía §3). Con BMAD, agregar con `--extra` la matriz de trazabilidad y la línea base del PRD.
6. **Paquete de cierre**: `paquete.py --proyecto <dir> listar cierre` y `paquete.py --proyecto <dir> cierre`; incluye el business case original congelado y el final (guía §3).
6b. **Expediente de auditoría** (a pedido): `paquete.py --proyecto <dir> auditoria [--desde ..] [--hasta ..] [--proposito ..] [--externo]` → índice MD y HTML, cronología, líneas base, registros, comunicaciones, sanidad al corte, manifiesto y `SHA256SUMS`; quien lo recibe lo comprueba con `paquete.py --proyecto <dir> verificar <zip>` (guía §3.1).
7. **Revisar el resultado**: tablas íntegras, frontmatter oculto, marca BORRADOR cuando corresponde, manifiesto coincidente (guía §4).
8. **🔒 Puerta humana**: el usuario confirma antes de enviar o subir a cualquier sistema externo; el envío lo hace `pm-comunicacion-stakeholders`. Anotar en `diario.md`; opcional `estado.py artefacto exportado-<tipo> --ruta exportados/… --estado <estado-de-la-fuente> --version <v>` (para un ZIP, `exportado-paquete-<puerta>`).
9. **Cerrar** con rutas generadas, faltantes y confirmación pendiente (o el bloque de retorno, SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; hay un paquete de puerta para cada puerta, también en ágil o híbrido.
2. [PRINCE2] Exportar no cambia el estado de un documento; el exportado hereda el de la fuente. Aprobar es `estado.py aprobar` tras decisión humana.
3. [PRINCE2] El contenido mínimo de cada paquete es lo que la junta revisa en esa puerta y coincide con `paquete.py` (guía §3).
4. [PRINCE2] El paquete de cierre lleva el business case original congelado y el final (y el PID original si existe).
5. [PRINCE2] Un paquete con un informe de excepción pendiente lo declara en el manifiesto y en el deck.
6. [PMBOK→Progress] Detalle según la audiencia: la junta recibe el resumen con decisiones requeridas; anexos y registros completos en archivos separados.
7. [PMBOK→Progress] Fórmulas exportadas como fórmulas o documentadas en una hoja "Notas"; declarar asistencia de IA y fecha de corte (guía §5).
8. [Plantillas] Versión mínima (un `.docx` y un `.xlsx`) o completa (ZIP con manifiesto y deck); el orden de secciones de la fuente se respeta.
9. Nunca un borrador sin "BORRADOR" en nombre y contenido; en paquetes, la marca depende solo de los obligatorios.
10. Un exportado aprobado no se sobrescribe; los obsoletos se mueven a `exportados/obsoletos/` a pedido, nunca se borran.
11. El ZIP de puerta incluye siempre `solicitud-<puerta>`; la solicitud y el ZIP (`exportado-paquete-<puerta>`) son artefactos distintos.
12. La hoja `stakeholders` y las valoraciones de interesados se exportan aparte y nunca en paquetes para cliente o proveedor.
13. Transparencia de IA: no inventar datos; citar la fuente de cada cifra.
14. Escrituras externas (subir, enviar, publicar) solo con confirmación explícita.

## Artefactos y plantillas
| Artefacto | Herramienta | Ruta | estado.json |
|---|---|---|---|
| Word desde Markdown | `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/exportar.py docx` · skill `docx` | `exportados/AAAA-MM-DD-<tipo>-v<n>[-BORRADOR].docx` | `exportado-<tipo>` |
| Excel de registros | `exportar.py xlsx` · skill `xlsx` | `exportados/AAAA-MM-DD-registros-v<n>[-BORRADOR].xlsx` | `exportado-registros` |
| Deck de puerta | skill `pptx` + `references/formatos.md` §3; sin ella, guion `.md` | `exportados/AAAA-MM-DD-deck-<puerta>-v<n>[-BORRADOR].pptx` | `exportado-deck-<puerta>` |
| Paquete de puerta / cierre | `scripts/paquete.py puerta <tipo>` / `cierre` | `exportados/AAAA-MM-DD-paquete-<tipo>-v<n>[-BORRADOR].zip` | `exportado-paquete-<tipo>` (opcional) |
| Manifiesto | generado por `paquete.py` | `MANIFIESTO.md` dentro del ZIP | — |
| Expediente de auditoría | `scripts/paquete.py auditoria` / `verificar` | `exportados/AAAA-MM-DD-expediente-auditoria[-<desde>_<hasta>].zip` | — |
| Registro del exportado | fila en `diario.md` | `03-control/registros/diario.md` | — |

Esta skill no tiene `templates/`.

## Calidad
- [ ] Fuente con ruta, versión y estado; nombre con fecha, tipo, versión y `-BORRADOR` si corresponde.
- [ ] Marca BORRADOR visible dentro del documento cuando la fuente no está aprobada; Mermaid renderizado o con aviso.
- [ ] `.xlsx` con una hoja por registro y columnas del esquema; fórmulas o notas de cálculo.
- [ ] Deck con diapositiva de decisiones requeridas (rol y fecha límite) y estado contra tolerancias con fuente.
- [ ] Paquete: `listar` ejecutado antes; manifiesto coincidente; obligatorios presentes o declarados; solicitud incluida.
- [ ] Sin información sensible para la audiencia destino; confirmación antes de enviar; anotación en el diario.

## Escalamiento y excepciones
- Falta un obligatorio del paquete → `pm-director`: la puerta no está lista; ZIP solo como BORRADOR si el usuario insiste.
- Piden exportar "limpio" un borrador → aprobar primero (decisión humana + `estado.py aprobar`) o exportar con marca.
- Faltan `python-docx`/`openpyxl` y no hay skills oficiales → entregar Markdown/CSV e instrucciones de instalación.
- `skills-office` declarado pero la skill no figura o falla dos veces → `exportar.py` y nota en `diario.md` con la causa.
- Destinatario externo sin regla de información sensible → ejecutivo vía `pm-comunicacion-stakeholders`.
- Discrepancia entre artefacto y registros → corregir la fuente con `pm-control`, no el exportado.
- Como subagente: la confirmación de envío se devuelve en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Exportá el plan de etapa 2 a Word y los registros a Excel para la junta del jueves."
- "Armá el paquete de puerta para autorizar la etapa 3 con la solicitud de decisión."
- EN: "Export the highlight report to .docx marked as draft; it is not approved yet."
- EN: "Build the closure package ZIP with the manifest."
- "Armá el expediente de auditoría del último trimestre para la PMO y verificá las huellas."
- No activa: "Armá el tablero de avance con semáforos" → `pm-visuales`.

## EN summary
Export skill: converts Markdown artifacts to .docx (draft banner unless approved) and CSV registers to .xlsx with `exportar.py`, delegates to the official docx/xlsx/pptx skills (any installed name) when `export=skills-office` (otherwise a Markdown deck outline), and assembles gate and closure ZIP packages with `paquete.py` (canonical keys, decision request, manifest, BORRADOR only when a mandatory item is missing or draft), plus an on-demand audit file (timeline, baselines, registers, health findings, SHA256SUMS) that `paquete.py verificar` re-hashes. Exports inherit the source status, are never overwritten when approved and are sent externally only after explicit confirmation. Detail in `references/guia.md` and `references/formatos.md`.
