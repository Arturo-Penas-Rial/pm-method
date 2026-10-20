---
name: pm-enfoques-gestion
description: "Enfoques de gestión del PID y planes subsidiarios. Usar: enfoque de riesgos, control de cambios, enfoque de calidad, management approach, subsidiary plan. No: PID ensamblado→pm-acta-constitucion."
version: 2.3.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: inicio
    agente: pm-inicio
    procesos_prince2: [IP, SB]
    practicas_prince2: [quality, risk, issues, progress, plans, organizing]
    tecnicas_pmbok: [matriz de probabilidad e impacto, EMV, reservas, umbrales de variación, reglas de medición EVM, control de configuración]
    artefactos: [enfoque-calidad, enfoque-riesgo, enfoque-issues-cambios, enfoque-comunicacion, enfoque-datos-digitales, enfoque-sostenibilidad-gestion, plan-gestion-alcance-requisitos, plan-gestion-cronograma-costos, plan-gestion-recursos-adquisiciones]
    idiomas: [es, en]
---

# Enfoques de gestión y planes subsidiarios · Management approaches and subsidiary plans

## Cuándo usar / When to use
- En la iniciación (IP): escribir los **enfoques de gestión** del PID (calidad, riesgo, issues y cambios, comunicación, datos y tecnología digital, sostenibilidad); beneficios y comercial son de `pm-caso-de-negocio` y `pm-adquisiciones`.
- **Planes subsidiarios** con vocabulario PMBOK: los mismos documentos con doble nombre.
- Fijar escalas, umbrales en tres zonas, tolerancias por nivel y autoridad de cambio; con BMAD, qué es elaboración progresiva y qué es cambio.
- EN: PID management approaches and subsidiary plans; scales, thresholds, change authority, BMAD change rules, connected MCP capabilities.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. etiquetas bilingües; doble nombre la primera vez ("enfoque de gestión de riesgos (risk management approach ≈ risk management plan)"). Escalas con valores numéricos.

## Conocimiento
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §2.d, §3.b–3.d, §5.3–5.4, §7.2.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §5 (calidad), §3.3.5 (comunicación), §1.5 (adaptación).
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §5.3 act. 2–3, §2.4 (tolerancias).
- `pm-knowledge/references/plantillas-inicio-y-planes.md` §3.1–3.12, §4.3–4.4; `pmbok8-artefactos-tecnicas-anexos.md` §2.3, §3.11.
- `references/guia.md`: detalle por enfoque (§1), una página (§2), escalas y registros (§3), BMAD elaboración vs. cambio (§4), integraciones MCP (§5), reglas extendidas (§6), ejemplo (§7), casos borde (§8).
- `SPEC.md` §1.12 (integraciones) y §1.13 (BMAD).

## Entradas requeridas
- `estado.json` en `inicio`/IP (o SB): `enfoque_entrega`, `tolerancias`, `roles`, `integraciones`.
- `01-inicio/project-brief.md` (estándares, adaptación); descripciones de producto (si faltan, `[pendiente de PBS]`).
- `stakeholders.csv` y `plan-compromiso-stakeholders.md` para comunicación.
- Políticas corporativas; si faltan, `[por confirmar]`.
- Con BMAD: inventario vía `pm-bmad-puente`. Integraciones: las que reporte `pm-integraciones` (ninguna obligatoria).

## Procedimiento
Todos los enfoques salen de `templates/<clave>.md` hacia `02-planificacion/enfoques/<clave>.md`.
1. **Leer el estado**: enfoques existentes; modo `crear` (IP) o `revisar` (SB/excepción).
2. **Nivel de formalidad** por enfoque (`references/guia.md` §2). 🔒 **Puerta humana 1**: el usuario confirma nivel y alcance; "no aplica, con razón" es válido. Fila en `decisiones.csv`.
3. **Entradas comunes**: tolerancias, estándares, roles, esquemas CSV (`registro.py esquema <registro>`); mismas escalas que los registros (`references/guia.md` §3).
4. **Calidad** (`templates/enfoque-calidad.md`): objetivos con métrica y umbral, autoridad de aceptación, no conformidad, DoD/DoR en ágil; con BMAD, code review y gate de preparación como métodos de verificación (§1.1 de la guía).
5. **Riesgo** (`templates/enfoque-riesgo.md`): escalas 1–5, P×I (alto ≥ 15, medio 6–12, bajo ≤ 5), EMV, residual, línea de tolerancia, contingencia vs. reserva de gestión (§1.2).
6. **Issues y cambios** (`templates/enfoque-issues-cambios.md`): cinco tipos canónicos, severidad, prioridad, niveles de decisión, cuatro definiciones de cambio con umbral, autoridad y presupuesto de cambio, swap del PO. **Con BMAD**: completar la sección 5.1 —qué es elaboración progresiva y qué es cambio en PRD, arquitectura, épicas y Sprint Change Proposals— con `references/guia.md` §4; `pm-bmad-puente` la aplica en `verificar`.
7. **Datos y tecnología digital** (`templates/enfoque-datos-digitales.md`): fuente de verdad, siete preguntas de datos, tableros, guardarraíles de IA. **Integraciones**: sección 1.1 con solo los MCP conectados, como capacidades (leer issues, publicar mensaje, leer transcripción…), escritura confirmada e instantáneas; sin conectores predefinidos (`references/guia.md` §5).
8. **Sostenibilidad** (`templates/enfoque-sostenibilidad-gestion.md`): controles para las metas de `00-direccion/enfoque-sostenibilidad.md`.
9. **Planes subsidiarios** (predictivo/híbrido; mínimos en ágil): `templates/plan-gestion-alcance-requisitos.md` (CÓMO; el QUÉ es de `pm-planificacion-por-productos`; con BMAD se citan ids del PRD), `templates/plan-gestion-cronograma-costos.md`, `templates/plan-gestion-recursos-adquisiciones.md` (§1.5).
10. **Comunicación, último** (`templates/enfoque-comunicacion.md`): lo que exigen los demás enfoques, políticas por audiencia, referencia (no copia) a `02-planificacion/matriz-comunicaciones.md` de `pm-comunicacion-stakeholders`, regla extraordinaria; canales solo si están conectados.
11. **Consolidar controles**: tolerancia de proyecto con `python3 ${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/estado.py --proyecto <dir> tolerancia --nivel proyecto tiempo=... costo=...`; etapa la fija la junta vía `pm-director`; paquete en `WP-###`. Umbrales, unidades, reservas y vía por entregable iguales entre documentos; reportar discrepancias.
12. **Registrar** (`estado.py artefacto <clave> --estado borrador`) con `[por confirmar]` y `[pendiente de PBS]`.
13. 🔒 **Puerta humana 2 (fuera de esta skill)**: el ejecutivo aprueba, usuario y proveedor sénior acuerdan; normalmente con el PID en `autorizar-proyecto`, registrada por `pm-director` (`estado.py aprobar enfoque-<tema> ...`); nunca sin acto humano.
14. **Revisar** (SB): escalas, umbrales, autoridades, cadencias e integraciones; versión 1.x.
15. **Cerrar** con estado, discrepancias, aprobador y siguiente paso (`pm-acta-constitucion`); como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; ágil o híbrido dentro de las etapas (DoD, backlog como mecanismo de cambio), nunca sin puertas.
2. [PRINCE2] Desviación prevista fuera de tolerancia → excepción; los umbrales de alerta la anticipan.
3. [PRINCE2] Nada se aprueba sin acto humano; el ejecutivo aprueba los enfoques.
4. [PMBOK→Risk/Progress] P×I, EMV para reservas, reglas EVM; umbrales en tres zonas con cifras iguales en cronograma/costos, cambios y PID.
5. [Plantillas] Mínima (una página) o completa según riesgo, costo e interesados; "no aplica, con razón" figura en el PID.
6. Transparencia de IA: borrador, sin datos inventados; umbrales de referencia configurables.
7. Idioma del usuario; nombre EN la primera vez.
8. Escrituras externas solo con vista previa y confirmación, vía `pm-integraciones`.
9. [PRINCE2] Espina común: alcance, procedimiento, responsabilidades, recursos, herramientas, estándares, referencias; desviaciones corporativas = adaptación.
10. [PRINCE2] Comunicación se completa último.
11. [PRINCE2] Escalas = las que aplican `registro.py` y los CSV; ninguna que los scripts rechacen.
12. [PRINCE2] Tolerancias por nivel con cifras, copiadas a `estado.json`; delegar cambios exige presupuesto de cambio.
13. [PRINCE2] Todo issue en uno de los cinco tipos; acciones en `acciones.csv`; swap del PO dentro de la tolerancia de alcance sin solicitud de cambio (`nivel=product-owner`).
14. BMAD (SPEC §1.13): sobre artefactos con línea base, agregar o retirar ids, cambiar la intención de un requisito o una SM-n, o una Sprint Change Proposal son `solicitud-cambio`; detallar sin cambiar ids es elaboración progresiva.
15. Integraciones (SPEC §1.12): capacidades de MCP conectados, sin conectores obligatorios; lectura libre, escritura confirmada, instantáneas que no reemplazan registros.
Más reglas: `references/guia.md` §6.

## Artefactos y plantillas
| Artefacto (≈ plan PMBOK) | Plantilla → salida en `02-planificacion/enfoques/` | Clave |
|---|---|---|
| Enfoque de calidad (≈ quality plan) | `templates/enfoque-calidad.md` | `enfoque-calidad` |
| Enfoque de riesgos (≈ risk plan) | `templates/enfoque-riesgo.md` | `enfoque-riesgo` |
| Enfoque de issues y cambios (≈ change plan) | `templates/enfoque-issues-cambios.md` | `enfoque-issues-cambios` |
| Enfoque de comunicación (≈ communications plan) | `templates/enfoque-comunicacion.md` | `enfoque-comunicacion` |
| Enfoque de datos y tecnología digital | `templates/enfoque-datos-digitales.md` | `enfoque-datos-digitales` |
| Sostenibilidad: controles | `templates/enfoque-sostenibilidad-gestion.md` | `enfoque-sostenibilidad-gestion` |
| Plan de alcance y requisitos | `templates/plan-gestion-alcance-requisitos.md` | `plan-gestion-alcance-requisitos` |
| Plan de cronograma y costos | `templates/plan-gestion-cronograma-costos.md` | `plan-gestion-cronograma-costos` |
| Plan de recursos y adquisiciones | `templates/plan-gestion-recursos-adquisiciones.md` | `plan-gestion-recursos-adquisiciones` |
Tolerancias: `estado.json.tolerancias`. La matriz de comunicaciones (anexo) es de `pm-comunicacion-stakeholders`.

## Calidad
- [ ] Nivel por enfoque acordado; "no aplica" con razón; espina común completa.
- [ ] Escalas canónicas que acepta `registro.py` en riesgo, issues y cambios.
- [ ] Con BMAD: sección 5.1 completa y coherente con `bmad.py verificar`.
- [ ] Datos: siete preguntas, guardarraíles de IA, integraciones conectadas como capacidades (o "ninguna").
- [ ] Planes con umbrales en tres zonas, unidades únicas, vía por entregable en híbrido.
- [ ] Comunicación último, con referencia a la matriz; perfil ágil mínimo en una página.
- [ ] Tolerancias, umbrales y reservas iguales entre documentos y `estado.json`; estado `borrador`.

## Escalamiento y excepciones
- Tolerancias de proyecto no fijadas → referencia `[por confirmar]` y `pm-director` antes de `autorizar-proyecto`.
- Estándar corporativo que contradice una técnica propia → aplicarlo como adaptación (PID §8), con confirmación.
- Equipo BMAD que quiere tratar como elaboración algo que la tabla 5.1 clasifica como cambio → decide el ejecutivo (enmienda del enfoque).
- Escala no soportada, delegación sin presupuesto, discrepancias entre dueños: `references/guia.md` §8.
- Como subagente: niveles, umbrales y aprobaciones van como decisiones humanas en el bloque de retorno.

## Ejemplos de invocación
- "Escribí los enfoques del PID en versión mínima; proyecto chico, un proveedor."
- "Usamos BMAD: ¿cuándo un ajuste al PRD es elaboración y cuándo solicitud de cambio? Dejalo en el enfoque."
- EN: "Draft the digital and data approach listing the integrations we connected as capabilities."
- EN: "Write the schedule and cost management plan with three-zone thresholds and EVM rules."
- No activa: "Ensamblá el PID y revisá la consistencia" → `pm-acta-constitucion`.

## EN summary
Produces the PID management approaches and the PMBOK subsidiary plans as the same documents, using the canonical scales the registers enforce. With BMAD, the change approach states which edits to baselined specs are progressive elaboration and which are change requests; the digital/data approach lists only connected MCP integrations, as capabilities. The executive approves; pm-director records the gate.
