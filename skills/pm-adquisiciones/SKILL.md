---
name: pm-adquisiciones
description: "Adquisiciones y contratos: make-or-buy, estrategia, selección, contratistas, cierre. Usar: proveedor, licitación, RFP, contrato, procurement, vendor. No: costo del plan→pm-costos-presupuesto."
version: 2.1.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: planificacion
    agente: pm-planificacion
    procesos_prince2: [IP, CS, MP, SB, CP]
    practicas_prince2: [organizing, plans, quality, risk, issues]
    tecnicas_pmbok: [análisis de hacer o comprar, tipos de contrato, documentos de licitación, criterios de selección ponderados, conferencia de oferentes, administración de reclamaciones, resolución alternativa de disputas, auditoría de adquisiciones]
    artefactos: [estrategia-adquisiciones, criterios-seleccion, documentos-licitacion, informe-estado-contratista, auditoria-adquisiciones, cierre-contrato, registro-reclamaciones]
    idiomas: [es, en]
---

# Adquisiciones y gestión de proveedores · Procurement and supplier management

## Cuándo usar / When to use
- En la iniciación (IP) o en un plan de etapa (SB): decidir hacer o comprar y, si se compra, método de entrega, tipo de contrato, monto, garantías y fases. La estrategia se decide al planificar, no al empezar la entrega.
- Criterios de selección y RFI/RFP/RFQ; en las etapas de entrega, informes de contratistas, cambios y reclamaciones; auditoría y cierre de contratos.
- EN: make-or-buy and procurement strategy at initiation or stage planning; weighted selection criteria and bid skeletons.
- EN: contractor status reports, claims, procurement audit and contract closeout.

## Idioma
**Idioma · Language:** responder siempre en el idioma en que escribe el usuario (English request → English reply); los artefactos van en `estado.json.idioma` salvo que el usuario pida otro. plantillas bilingües. Nombrar la primera vez: estrategia de adquisiciones (procurement strategy), hacer o comprar (make-or-buy), informe de estado del contratista (contractor status report), reclamaciones (claims), cierre de contrato (contract closeout).

## Conocimiento
- `references/guia.md` (esta skill): §1 flujo, §2 hacer o comprar, §3 estrategia, §4 tipos de contrato, §5 selección y ética, §6 control del contrato, §7 cierre, §8 mínima vs. completa, §9 reglas complementarias.
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §4.3 (apéndice de adquisiciones) y §4.3.2; §3.12 Familia L; §2.8.
- `pm-knowledge/references/plantillas-documentos-registros-reportes.md` §14–§15, §32–§33, §38.
- `pm-knowledge/references/prince2-practicas-bc-organizacion-planes-calidad.md` §3.5.1 (gestión comercial), §5.4 (calidad comercial), §5.8.

## Entradas requeridas
- `estado.json`: fase, `etapa_actual` (1 = iniciación; 2…n = entrega), roles (ejecutivo, proveedor sénior, gestor), tolerancias, `enfoque_entrega`.
- Enfoque de gestión comercial del PID; si falta, la estrategia hace de equivalente para la adquisición y se propone registrarlo (`pm-enfoques-gestion`).
- Planificar: paquetes candidatos (`wbs.csv`/diccionario; en ágil, épicas del backlog), descripciones de producto o enunciado del trabajo (con BMAD, ids del PRD), cronograma y presupuesto de referencia, riesgos, políticas de compras.
- Seguir y cerrar: contrato o resumen, informes del contratista, aceptaciones, pagos, cambios y reclamaciones.
- Quiénes de compras y legal aprueban: preguntar.

## Procedimiento
### A. Planificar
1. **Hacer o comprar** (IP para todo el plan; SB para la etapa siguiente) con costo total y riesgos de ambas opciones (`references/guia.md` §2); decisión registrada por quien corresponde; paquetes comprados marcados como proveedor externo.
2. **Estrategia** con `templates/estrategia-adquisiciones.md` → `02-planificacion/adquisiciones/estrategia-adquisiciones.md` (o `<id>-estrategia-adquisiciones.md`): contenido en §3, tipo de contrato según §4. Alertar ante precio fijo con alcance indefinido o reembolsable sin controles. Riesgos a `pm-riesgos`, hitos a `pm-cronograma-estimacion`, monto a `pm-costos-presupuesto`.
3. **Método y criterios** con `templates/criterios-seleccion.md` → `<id>-criterios-seleccion.md`: método fijado antes de licitar, pesos 100 %, descriptores, eliminatorios (§5).
4. **Documento de licitación** (RFI/RFP/RFQ según la pregunta) → `02-planificacion/adquisiciones/<id>-rfp.md` con el esqueleto de §5.
5. **PUERTA HUMANA — estrategia y criterios**: se aprueban con el plan (`autorizar-proyecto` / `autorizar-etapa`); si la política exige aprobación propia, tras la decisión humana `estado.py --proyecto <dir> aprobar estrategia-adquisiciones --por "<rol: nombre>"`. La planilla de criterios se congela antes de recibir ofertas.

### B. Seleccionar
6. Recibir propuestas; misma información para todos; eliminatorios; calificación independiente (§5).
7. **PUERTA HUMANA — adjudicación y firma**: ranking y recomendación; decide la autoridad de la organización. Registrar la decisión (`registro.py agregar decisiones`, o `pm-director` si es puerta de la junta) y alta en `03-control/registros/contratos.md`; legal antes de firmar.

### C. Controlar
8. **Paquete contractual** con `pm-paquetes-trabajo`, coherente con el contrato y las descripciones de producto (§6).
9. **Informe de estado del contratista** (`templates/informe-estado-contratista.md` → `03-control/reportes/AAAA-MM-DD-estado-contratista-<id>.md`): cuatro dimensiones, pronóstico, reclamaciones, acciones; riesgos e issues replicados en los registros; insumo del highlight.
10. **Cambios contractuales** siempre por `pm-issues-cambios` y el mecanismo del contrato; nunca informales.
11. **Reclamaciones** en `03-control/registros/reclamaciones.md` con fecha, hechos, cláusulas y cronología; negociación y mediación primero; legal antes de escalar (§6). Desvío que amenaza la tolerancia de etapa → `pm-progreso-reportes` y `pm-director`.
12. **Auditoría** con `templates/auditoria-adquisiciones.md` (bloques A–D) antes de cada cierre o periódicamente.

### D. Cerrar
13. Verificar las tres condiciones (disputas resueltas, aceptación formal, pagos finales) y garantías, retenciones, obligaciones pendientes y lecciones (§7).
14. Completar `templates/cierre-contrato.md` → `04-cierre/cierre-contrato-<id>.md`.
15. **PUERTA HUMANA — cierre**: firma la autoridad contractual; luego `estado.py aprobar cierre-contrato-<id> --por "<rol: nombre>"`; informar a `pm-cierre-proyecto`.
16. Cerrar la respuesta con ids creados, estado de cada contrato y próxima puerta con el rol que decide; como subagente, en el bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas de gestión por defecto; contratos alineados con las etapas (hitos de pago y puntos de salida en límites); la contratación ágil opera dentro de las etapas.
2. [PRINCE2] La estrategia se decide al planificar y forma parte del plan que aprueba la junta.
3. [PRINCE2] Una desviación de proveedor prevista fuera de tolerancia se escala como excepción a `pm-director`; nunca se absorbe.
4. [PRINCE2] Nada se aprueba (estrategia, adjudicación, cambio, cierre) sin acto humano registrado; la skill recomienda, no adjudica ni firma.
5. [PRINCE2] El paquete de un proveedor externo es instrucción formal conforme al contrato; criterios contractuales y descripciones de producto no se contradicen; la aceptación contractual precede a la del proyecto.
6. [PMBOK→Plans] Hacer o comprar con costos totales y riesgos antes de recomendar comprar.
7. [PMBOK→Risk] Tipo de contrato según definición del alcance y riesgo a asignar; alertar ante combinaciones peligrosas.
8. [PMBOK→Organizing] Método de selección publicado antes de licitar y nunca cambiado tras ver ofertas; matriz ponderada como evidencia; misma información para todos.
9. [PMBOK→Issues] Controversias con hechos y cronología; negociación y mediación antes de litigio; consulta legal.
10. [Plantillas] Un contrato no se cierra sin las tres condiciones verificadas.
11. [Plantillas] Compras simples: enunciado del trabajo en el contrato; versión completa para adquisiciones mayores.
12. Transparencia de IA: borrador; no inventar precios ni cláusulas (`[por confirmar]`); no sustituye asesoramiento legal.
13. Escrituras externas (portal de compras, correo al proveedor, tracker) solo con confirmación, vía `pm-integraciones`. Más reglas en §9.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Hacer o comprar + estrategia | `templates/estrategia-adquisiciones.md` | `02-planificacion/adquisiciones/estrategia-adquisiciones.md` (o `<id>-…`) | `estrategia-adquisiciones` (o `-<id>`) |
| Criterios de selección | `templates/criterios-seleccion.md` (+ CSV opcional) | `02-planificacion/adquisiciones/<id>-criterios-seleccion.md` | `criterios-seleccion-<id>` |
| Documento de licitación | esqueleto de `references/guia.md` §5 | `02-planificacion/adquisiciones/<id>-rfp.md` | `licitacion-<id>` |
| Informe de estado del contratista | `templates/informe-estado-contratista.md` | `03-control/reportes/AAAA-MM-DD-estado-contratista-<id>.md` | — |
| Auditoría de adquisiciones | `templates/auditoria-adquisiciones.md` | `03-control/reportes/AAAA-MM-DD-auditoria-adquisiciones-<id>.md` | `auditoria-adquisiciones-<id>` |
| Cierre de contrato | `templates/cierre-contrato.md` | `04-cierre/cierre-contrato-<id>.md` | `cierre-contrato-<id>` |
| Decisiones | `registro.py agregar decisiones` | `03-control/registros/decisiones.csv` | puerta de la junta solo por `pm-director` |

## Calidad
- [ ] Hacer o comprar con costos totales y riesgos, registrado.
- [ ] Estrategia decidida al planificar, con monto y base, garantías, retenciones, seguros, plazo de garantía, fases y mecanismo de cambio.
- [ ] Método publicado antes de licitar; pesos 100 %; descriptores; eliminatorios; planilla congelada.
- [ ] Informes del contratista con cuatro dimensiones; riesgos e issues replicados; reclamaciones con cronología.
- [ ] Cierre con las tres condiciones, garantías y retenciones resueltas, lecciones y evaluación del proveedor.
- [ ] Compras y legal consultados según política.

## Escalamiento y excepciones
- Desvío de proveedor fuera de tolerancia de etapa → informe de excepción (plantilla de `pm-issues-cambios`) y `pm-director`.
- Monto que deja el presupuesto fuera de la restricción del mandato → `pm-costos-presupuesto` y, si sigue fuera, junta vía `pm-director`.
- Disputa sin acuerdo → protocolo del contrato, consulta legal e informe a la junta.
- Conflicto contrato ↔ descripción de producto → `pm-calidad` y `pm-director`; no aceptar hasta resolver.
- Presión para cambiar criterios tras ver ofertas o favorecer a un oferente → negarse, explicar y registrar issue.
- Como subagente: adjudicación, firma y cierre se devuelven como decisiones humanas en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "¿Conviene hacer el conector con la naviera internamente o contratarlo? Armá el análisis y la estrategia de adquisiciones."
- "Llegó el informe mensual del proveedor B: 4 días de atraso y un reclamo por cambio de alcance. Procesalo."
- EN: "Draft the RFP skeleton for the tracking vendor, fixed price with milestone payments and 10 % retention."
- EN: "Close out the contract with vendor C: acceptance is signed, final invoice pending."
- No activa: "¿Cuánta contingencia lleva el presupuesto de la etapa 3?" → `pm-costos-presupuesto`.

## EN summary
Procurement inside the PRINCE2 commercial context: make-or-buy, procurement strategy decided at initiation or stage planning, weighted selection criteria frozen before bids, RFI/RFP/RFQ skeletons, fair evaluation, contractual work packages, contractor status reports, controlled contract changes, claims handled by negotiation first, procurement audits, and closeout only when disputes, acceptance and final payment are settled. Award, signature and closeout are human decisions; supplier deviations beyond tolerance escalate to pm-director.
