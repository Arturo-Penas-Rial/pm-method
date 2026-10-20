---
name: pm-registros
description: "Registros genéricos (supuestos, decisiones, acciones, diario) y clasificación. Usar: registrar, anotar, acción, supuesto, RAID, action log. No: riesgos→pm-riesgos; issues/cambios→pm-issues-cambios."
version: 2.3.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: control
    agente: pm-control
    procesos_prince2: [SU, IP, CS, MP, SB, CP]
    practicas_prince2: [risk, issues, progress, quality, organizing]
    tecnicas_pmbok: [análisis de supuestos, cinco porqués, registros y bitácoras, puntuación P×I]
    artefactos: [riesgos.csv, issues.csv, cambios.csv, decisiones.csv, supuestos.csv, lecciones.csv, stakeholders.csv, calidad.csv, acciones.csv, diario.md, guia-registros]
    # opcionales: estereotipos.csv, preferencias.csv y raci.csv (pm-interesados) y envios.csv (pm-integraciones) usan el mismo registro.py
    idiomas: [es, en]
---

# Registros del proyecto · Project registers

## Cuándo usar / When to use
- Alguien reporta algo que hay que anotar y no está claro si es riesgo, issue, cambio, decisión, supuesto, acción o lección.
- Agregar, actualizar, cerrar, listar o resumir filas de cualquiera de los nueve CSV o del diario; migrar una entrada entre registros sin perder trazabilidad.
- Revisión periódica de registros y resumen para el highlight o el informe de fin de etapa; compromisos con responsable y fecha (`A-###`).
- EN: capture and classify a reported fact into the right register; add, update, close or summarize rows.
- EN: run the periodic register review or build the register summary for a report.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. Archivos y cabeceras en español técnico (`snake_case`); enumeraciones en minúsculas sin acentos (se aceptan alias en inglés). Primera mención con el EN: riesgos (risk register), issues (issue register), cambios (change log), decisiones (decision log), supuestos (assumption log), lecciones (lessons log), stakeholders (stakeholder register), calidad (quality register), acciones (action log), diario (daily log). Traducción por columna: `templates/guia-registros.md`.

## Conocimiento
- `references/guia.md` (este skill): §1 clasificación, §2 redacción, §3 escritura, §4 cierre, §5 migraciones, §6 revisión periódica, §7 resumen, §8 reglas extendidas.
- `templates/guia-registros.md`: columnas, valores permitidos, estados iniciales y transiciones (= `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/esquema.py`).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` — `### 3.a` (tipos de issue y frontera con riesgo), `### 3.d` (registro de issues), `### 7.1` y `### 7.4` (clasificación y qué registrar).
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` — `# PARTE II` (fichas 19–26), `## 46.` (transiciones entre estados), `## 47.`–`## 52.` (reglas operativas).

## Entradas requeridas
- Carpeta con `estado.json` y `03-control/registros/*.csv` (creados por `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/nuevo_proyecto.py`); si no existen, `pm-estado-proyecto` primero.
- `estado.json`: enfoque, tolerancias, `roles.autoridad_cambio`, `etapa_actual` (para saber si algo excede la autoridad del gestor).
- Preguntar lo mínimo para clasificar: ¿ya ocurrió o podría ocurrir? ¿pide cambiar algo aprobado? ¿quién lo detectó y quién decide? Sin propietario, preguntarlo; no inventarlo.
- Integraciones opcionales: si hay un tracker conectado, se sincroniza vía `pm-integraciones` solo con confirmación; los CSV siguen siendo la fuente de verdad. Acciones de reuniones llegan de `pm-reuniones`.

## Procedimiento
1. **Situar**: `estado.py ver` (fase, etapa, tolerancias, autoridad de cambio). En `pre-proyecto` sin registros abiertos, anotar en `diario.md` y promover en IP.
2. **Clasificar antes de registrar** con la tabla de la guía §1: un único registro destino; nunca el mismo hecho en dos registros sin referencia cruzada. Riesgos y issues/cambios se registran aquí solo como fila; su análisis y decisión son de `pm-riesgos` y `pm-issues-cambios`.
3. **Formal vs. informal**: ¿impacto material? ¿modifica una línea base? ¿decide alguien distinto de quien lo detectó? Un "sí" → registro formal; tres "no" → `diario.md`. Solicitud de cambio y fuera de especificación, siempre formales.
4. **Redactar la fila** con los campos de calidad de cada registro (guía §2).
5. **Escribir** con `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/registro.py --proyecto <dir> agregar <registro> --campo k=v …`; ante dudas, `registro.py esquema <registro>`. Corregir valores rechazados en lugar de `--forzar` (guía §3). Mostrar el id y marcar `[por confirmar]` lo no aportado.
6. **Actualizar, nunca borrar**: `registro.py actualizar <registro> <id> --campo estado=.. --campo notas=..`; cerrar solo con decisión, decisor y fecha (guía §4).
7. **Migrar** con referencia cruzada en ambos extremos y estado de origen actualizado (guía §5). Con BMAD, un desvío del PRD es `solicitud-cambio` citando ids, sin duplicar requisitos.
8. **🔒 Puerta humana** para cierres y decisiones relevantes: el agente propone; el gestor, la autoridad de cambio o la junta confirman antes de escribir `estado=cerrado`, `decision=..` o filas de `decisiones.csv` de nivel `junta` o `autoridad-cambio`. Si excede la autoridad del gestor, dejar `escalado` o `pendiente-decision` y derivar. Las decisiones de puerta y aprobaciones las escribe `estado.py puerta|aprobar` (solo pm-director); no duplicarlas.
9. **Revisión periódica** (cada período de informe): `registro.py listar <registro> --abiertos` y las señales de la guía §6; revisión cruzada y patrones del diario.
10. **Resumen para informes**: `registro.py resumen --corte <fecha del informe>` más críticos con ids (guía §7) → `pm-progreso-reportes` o `pm-riesgos`.
11. **Cerrar** con ids creados o actualizados, migraciones, `[por confirmar]` pendientes y decisión humana pendiente con su rol (o el bloque de retorno, SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; en ágil o híbrido los registros se revisan en las ceremonias existentes dentro de la etapa, sin suprimir puertas.
2. [PRINCE2] Una desviación prevista fuera de tolerancia detectada al revisar registros se escala a `pm-director`; no se reclasifica para evitar el escalado.
3. [PRINCE2] Una decisión existe cuando está en `decisiones.csv` con `decidido_por` y `nivel`; si es puerta, también en `estado.json.puertas`.
4. [PRINCE2] Prueba de certeza: incierto → riesgo; ocurrido o seguro → issue. Un riesgo materializado se cierra `ocurrido` y se abre el issue vinculado.
5. [PRINCE2] Todo issue tiene exactamente uno de cinco tipos (`problema-preocupacion`, `evento-externo`, `oportunidad-negocio`, `solicitud-cambio`, `fuera-especificacion`).
6. [PRINCE2] Riesgo con propietario y ejecutor; issue con responsable; lección con responsable de seguimiento; decisión con decisor y nivel. Sin esos campos, `[por confirmar]` y no se cierra.
7. [PRINCE2] Las acciones (`A-###`) son compromisos con responsable, fecha y `origen`; nunca issues.
8. [PRINCE2] El diario guarda lo informal y se revisa cada período buscando patrones a promover.
9. [PMBOK→Issues] Toda migración deja id de destino en el origen e id de origen en el destino, y cambia el estado del origen.
10. [PMBOK→Risk] P e I 1–5; alto ≥15, medio 6–12, bajo ≤5 (configurable); EMV aproximado con convención declarada.
11. [Plantillas] Un ítem por fila, causa raíz y no síntoma; no se agregan columnas ni valores sin cambiar a la vez `esquema.py` y `guia-registros.md`.
12. [Plantillas] Stakeholders con `confidencial=si` tienen circulación restringida.
13. Transparencia de IA: filas del agente marcadas como propuesta; cifras no aportadas `[por confirmar]`; cada resumen cita registro e id.
14. Escrituras externas (tracker, correo, chat) solo con confirmación explícita; los CSV son la fuente de verdad.

## Artefactos y plantillas
| Artefacto | Herramienta | Ruta | estado.json |
|---|---|---|---|
| Riesgos, issues, cambios, supuestos, lecciones, stakeholders, calidad | `registro.py agregar <registro>` | `03-control/registros/<registro>.csv` | — (`registro.py resumen`) |
| Cambios aprobados | `registro.py` + nueva versión del artefacto | `03-control/registros/cambios.csv` | `artefactos.<linea-base>.version` |
| Decisiones | `registro.py agregar decisiones`; puertas y aprobaciones vía `estado.py` | `03-control/registros/decisiones.csv` | `puertas[].decision_id` |
| Acciones (action log) | `registro.py agregar acciones` | `03-control/registros/acciones.csv` | — (vencidas en `resumen`) |
| Diario (daily log) | `templates/diario.md` | `03-control/registros/diario.md` | — |
| Guía de registros | `templates/guia-registros.md` | copia opcional en `03-control/registros/` | `guia-registros` (opcional) |
| Resumen del período | `registro.py resumen` + críticos con ids | dentro del highlight en `03-control/reportes/` | — |

## Calidad
- [ ] Cada entrada pasó la prueba de certeza y las tres preguntas formal/informal.
- [ ] Ninguna fila sin `id`, `estado` ni responsable; valores dentro de `esquema.py`; ningún `--forzar` sin motivo.
- [ ] Ningún riesgo alto (≥15) sin respuesta y propietario; acciones con responsable y `fecha_compromiso`.
- [ ] Ninguna fila cerrada sin decisión, decisor y fecha; migraciones con referencia en ambos extremos.
- [ ] Revisión cruzada hecha y diario revisado.
- [ ] Resumen con ids y conteos que coinciden con `registro.py resumen`.

## Escalamiento y excepciones
- Issue o riesgo cuyo tratamiento supera tolerancias de etapa → `pm-issues-cambios` (informe de issue/excepción) → `pm-director`; fila en `escalado`.
- Riesgo que excede la autoridad del gestor → `pm-riesgos` + `pm-director` (`respuesta=escalar`).
- Cambio fuera de la autoridad de cambio o sin presupuesto → `pm-issues-cambios` → `pm-director` (`pendiente-decision`).
- Incoherencia entre registros y `estado.json` → pedir a `pm-director` que regularice; no corregir en silencio.
- Como subagente: confirmaciones de cierre, decisiones de nivel junta y escrituras externas se devuelven en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "El proveedor avisó que puede atrasarse dos semanas; ¿lo anoto como riesgo o como issue?"
- "Cerrá la acción A-012: Marta entregó el informe el viernes."
- EN: "Log a new assumption: the customs API will be available in staging by November 10, owner Diego."
- EN: "What actions are overdue per person after the board meeting?"
- No activa: "Analizá la probabilidad e impacto de los riesgos y proponé respuestas" → `pm-riesgos`.

## EN summary
Owner of the generic registers (assumptions, decisions, actions, stakeholders, quality, daily log) and of classification across all nine CSV registers. Every item passes a certainty test and a formal-versus-informal test, is written and validated with `registro.py` (auto ids, initial states, P×I, EMV, English aliases), updated but never deleted, migrated with cross-references, reviewed each period and summarized with ids for reports. Risk analysis goes to pm-riesgos and issue/change decisions to pm-issues-cambios. Detail in `references/guia.md`.
