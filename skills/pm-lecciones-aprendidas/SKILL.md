---
name: pm-lecciones-aprendidas
description: "Lecciones aprendidas: lecciones.csv, taller de etapa, informe de lecciones. Usar: lección aprendida, lessons learned, lessons report, retro de etapa. No: retro de sprint→pm-agil-hibrido."
version: 2.2.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-cierre
    procesos_prince2: [SU, IP, CS, MP, SB, CP]
    practicas_prince2: [progress, quality, risk, issues]
    tecnicas_pmbok: [retrospectiva, reseña posterior a la acción, autopsia en curso, votación por puntos]
    artefactos: [lecciones.csv, retrospectiva-etapa, informe-lecciones, propuesta-mejora-organizacion]
    idiomas: [es, en]
---

# Lecciones aprendidas · Lessons learned

## Cuándo usar / When to use
- Al arrancar o planificar una etapa: buscar lecciones previas y registrar cuáles se incorporan y con qué acción.
- Durante las etapas de entrega, cuando un riesgo se materializa, un issue se cierra, una revisión de calidad falla o algo sale muy bien: capturar la lección en el momento.
- En el límite de etapa y al cierre: taller de lecciones de etapa, informe de lecciones y conversión de cada lección en acción con dueño; propuestas de mejora a la organización.
- EN: search prior lessons, capture lessons continuously, run the stage lessons workshop.
- EN: consolidate stage or project lessons reports and raise improvement proposals to the PMO.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Primera mención con el término EN: registro de lecciones (lessons log), informe de lecciones (lessons report), reseña posterior a la acción (after-action review). Plantillas bilingües.

## Conocimiento
- `references/guia.md` (este skill): §1 lecciones previas, §2 captura, §3 taller de etapa, §4 informe, §5 propuesta organizacional, §6 ciclo, §7 estados, §8 columnas, §9 reglas extendidas.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` — `### 2.2` (aprender de la experiencia), `### 5.6` y `### 5.7` (informe de lecciones en SB y CP).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` — `### 4.d` (registro e informe de lecciones).
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` — `## 18.` (retrospectiva), `## 26.` (registro), `## 34.` (reporte de lecciones).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` — `### 3.6` y `### 3.13` (técnicas de equipo y ágiles).
- `pm-registros/templates/guia-registros.md` (columnas y estados válidos de `lecciones.csv`).

## Entradas requeridas
- `estado.json` (fase, etapa, enfoque, roles) y `03-control/registros/lecciones.csv`; se opera con `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> …`.
- Para capturar: qué pasó (etapa o paquete), efecto, causa si se conoce, ids relacionados (R-, I-, C-, Q-).
- Para el taller: etapa, participantes, facilitador, datos del período, acciones del taller anterior, retrospectivas de iteración y, si existen, actas o transcripciones normalizadas en `03-control/reuniones/` (`pm-reuniones`).
- Para el informe: `lecciones.csv`, retrospectivas, registros, auditorías y cierres de contrato.
- Lecciones previas: repositorio u otros informes; si no hay, preguntarlo y declararlo.
- Integraciones: si hay un tracker conectado, las acciones pueden crearse como ítems vía `pm-integraciones` solo con confirmación; por defecto van al registro.

## Procedimiento
1. **Lecciones previas** (SU, IP, inicio de etapa): buscar, registrar las aplicables y marcarlas `accionada-proyecto` con `notas=incorporada: <artefacto>` al aplicarlas; listarlas en "lecciones incorporadas" del plan (guía §1).
2. **Capturar** ante cada disparador con `registro.py agregar lecciones --campo situacion=.. --campo efecto=.. --campo recomendacion=.. --campo prioridad=.. --campo responsable_seguimiento=..`; recomendación accionable y transferible; aciertos también; `notas` con ids y `impacto_organizacional=si|no` (guía §2).
3. **Revisar** en cada checkpoint/highlight: `registro.py listar lecciones --abiertos`; completar las `registrada`; pasar a `revisada` las confirmadas.
4. **Taller de lecciones de etapa** con `templates/retrospectiva-etapa.md`: formato declarado (estrella de mar, 4L o reseña posterior a la acción), facilitador declarado, acciones anteriores revisadas, 1–3 acciones con dueño y fecha; volcado a plan, backlog o `acciones.csv` y a `lecciones.csv` (guía §3). Si piden "la retro del sprint", derivar a `pm-agil-hibrido` y recoger aquí solo lo transferible.
5. **Informe de lecciones** con `templates/informe-lecciones.md`: por área de desempeño, bloques de riesgos/issues, calidad, proveedores y desempeño excepcional; cada lección con destinatario, acción, responsable, fecha e ids de registro (guía §4).
6. **🔒 Puerta humana — revisión**: aseguramiento confirma responsables; la junta revisa. Tras la revisión: `estado.py aprobar informe-lecciones --por "<rol: nombre>"` (o `informe-lecciones-etapa-<n>`) y actualizar estados de `lecciones.csv` (guía §7).
7. **Propuesta de mejora** para lecciones con impacto organizacional (guía §5). **🔒 Puerta humana**: decide el ejecutivo; envío externo solo con confirmación; marcar `accionada-organizacion`.
8. **Cerrar** con ids L-nnn creados o actualizados, acciones con dueño y fecha, lecciones sin dueño y destino de cada una (o el bloque de retorno, SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; las retrospectivas de iteración (`pm-agil-hibrido`) operan dentro de las etapas y alimentan el taller y el informe del límite de etapa, sin sustituirlos.
2. [PRINCE2] Una desviación fuera de tolerancia que aflore en una lección se trata como issue y se escala a `pm-director`; nunca queda solo como "lección".
3. [PRINCE2] Nada se da por aprobado sin acto humano registrado: aseguramiento confirma, la junta revisa, el ejecutivo decide las propuestas a la organización.
4. [PRINCE2] Aprender de la experiencia: lecciones previas al arrancar y al planificar cada etapa, registradas con acción concreta.
5. [PRINCE2] Una lección sin acción ni responsable sigue `registrada` (abierta); convertirla en acción con dueño y fecha es obligación del gestor.
6. [PRINCE2] El informe de lecciones puede emitirse en cualquier momento; suele integrarse en el de fin de etapa o de proyecto y puede haber uno por organización destinataria.
7. [PMBOK→Progress/SB] Técnica según la pregunta (retrospectiva, reseña posterior a la acción, autopsia en curso), formato declarado y ambiente sin culpas; facilitador neutral o sesgo declarado (guía §9).
8. [PMBOK→Organizing] Las lecciones con impacto organizacional se elevan a la PMO; el proyecto no se queda con lo que sirve a otros.
9. [Plantillas] Lección como recomendación accionable y generalizable, con disparador que permita juzgar su aplicabilidad; se capturan buenas prácticas.
10. [Plantillas] Un taller produce 1–3 acciones con dueño y fecha y respeta su caja de tiempo; el informe cubre cada área o justifica la omisión.
11. Estados válidos: `registrada`, `revisada`, `accionada-proyecto`, `accionada-organizacion`, `descartada`; nunca se borra una fila.
12. Transparencia de IA: todo borrador; no inventar hechos ni causas; citar registro o sesión de origen.
13. Escrituras externas (tracker, repositorio de la PMO, correo) solo con confirmación explícita.

## Artefactos y plantillas
| Artefacto | Plantilla / herramienta | Ruta | estado.json |
|---|---|---|---|
| Registro de lecciones (lessons log) | `registro.py agregar/actualizar lecciones` | `03-control/registros/lecciones.csv` | — |
| Lecciones previas incorporadas | filas `accionada-proyecto` + sección del plan | `02-planificacion/plan-etapa-<n>.md` | `plan-etapa-<n>` |
| Taller de lecciones de etapa | `templates/retrospectiva-etapa.md` | `03-control/reportes/AAAA-MM-DD-retrospectiva-etapa-<n>.md` | `retrospectiva-etapa-<n>` |
| Informe de lecciones de etapa | `templates/informe-lecciones.md` | `03-control/reportes/AAAA-MM-DD-informe-lecciones-etapa-<n>.md` | `informe-lecciones-etapa-<n>` |
| Informe de lecciones de proyecto | `templates/informe-lecciones.md` | `04-cierre/informe-lecciones.md` | `informe-lecciones` |
| Propuesta de mejora a la organización | sección del informe o archivo propio | `04-cierre/propuesta-mejora-organizacion.md` | `propuesta-mejora-organizacion` |
| Acciones del taller | plan, backlog (`pm-agil-hibrido`) o `registro.py agregar acciones` | plan, `02-planificacion/backlog.csv` o `acciones.csv` | — |

Columnas de `lecciones.csv` y traducción: guía §8.

## Calidad
- [ ] Lecciones previas buscadas; incorporadas con acción y artefacto destino (o constancia de que no hay).
- [ ] Cada lección con situación, efecto, recomendación accionable, prioridad, responsable y estado válido.
- [ ] Aciertos capturados, no solo problemas.
- [ ] Taller con formato y facilitador declarados, acciones anteriores revisadas, 1–3 acciones con dueño y fecha.
- [ ] Informe con todas las áreas cubiertas o justificadas, citas a registros y lecciones organizacionales separadas.
- [ ] Revisión de la junta y decisiones del ejecutivo registradas.

## Escalamiento y excepciones
- Lección que revela desviación fuera de tolerancia o riesgo no gestionado → `pm-issues-cambios` / `pm-riesgos` y `pm-director`.
- Lección sin responsable posible en el proyecto → ejecutivo.
- Señales de falta de seguridad psicológica (silencio, culpas) → informar al gestor antes de atribuir mala conducta.
- Propuesta rechazada por la PMO → `descartada` con motivo.
- Como subagente (pm-cierre, pm-control): la revisión de la junta, la decisión de enviar a la PMO y las escrituras externas se devuelven en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Registrá una lección: la naviera no tenía entorno de pruebas y perdimos dos semanas."
- "Facilitá el taller de lecciones de la etapa 3 con estrella de mar; acá están las retros de los sprints 5 a 8."
- EN: "Before planning stage 3, which lessons from previous projects should we incorporate?"
- EN: "Consolidate the project lessons report for the closure package."
- No activa: "Hagamos la retro del sprint 7" → `pm-agil-hibrido`.

## EN summary
Applies the PRINCE2 principle of learning from experience. Searches prior lessons when starting or planning, captures lessons continuously in `lecciones.csv` as transferable recommendations with owner, runs the blame-free stage lessons workshop (iteration retros belong to pm-agil-hibrido), consolidates stage or project lessons reports reviewed by assurance and the board, and raises organizational improvement proposals sent only on the executive's decision. Detail in `references/guia.md`.
