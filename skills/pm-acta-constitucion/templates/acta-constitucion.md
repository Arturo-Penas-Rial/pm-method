---
tipo: acta-constitucion
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Acta de constitución del proyecto · Project charter — {{proyecto}}

> Autoriza formalmente el proyecto, deja constancia de por qué se hace y nombra al gestor con su nivel de autoridad. Mapeo del paquete: resume el PID para firmas y comunicación; la autorización PRINCE2 es la aprobación del PID por la junta. / Formally authorises the project and names the project manager with defined authority.

**Versión / Version:** {{version_doc}} · **Formato / Format:** {{formato}}
*`minima` (una página fusionada con el enunciado del alcance) o `completa` (tres páginas con todas las secciones). Si se fusiona con la visión (híbrido), declararlo en el título.*

## 1. Identificación / Identification

**Patrocinador (ejecutivo) / Sponsor (executive):** {{patrocinador}} · **Gestor de proyecto / Project manager:** {{gestor}}
*Las dos personas clave. Un solo ejecutivo; nunca la misma persona que el gestor.*

**Fecha de preparación / Date prepared:** {{fecha_preparacion}} · **Originador / Originator:** {{originador}}
*Quién originó el pedido si no es el patrocinador (programa, cliente, comité).*

## 2. Propósito del proyecto / Project purpose

{{proposito}}
*La razón de ser, remitiendo a una fuente identificable: business case (ruta y versión), objetivo estratégico, norma, contrato.*

## 3. Descripción de alto nivel / High-level description

{{descripcion}}
*Qué se hará, en un párrafo. Copiar de la definición del proyecto del brief.*

## 4. Límites del proyecto / Project boundaries

**Inclusiones / Inclusions:** {{inclusiones}}
*Qué entra, en viñetas.*

**Exclusiones / Exclusions:** {{exclusiones}}
*Obligatorio: al menos una exclusión explícita.*

**Restricciones / Constraints:** {{restricciones}}
*Plazo, presupuesto, normativa, tecnología, contratos. Separadas de los supuestos.*

**Supuestos / Assumptions:** {{supuestos}}
*Lo que se da por cierto sin verificar; referenciar `supuestos.csv`.*

## 5. Entregables clave / Key deliverables

| Entregable / Deliverable | Descripción breve / Short description | Autoridad de aceptación / Acceptance authority | Vía de entrega / Delivery track |
|---|---|---|---|
| {{ent1}} | {{ent1_desc}} | {{ent1_acepta}} | {{ent1_via}} |
| {{ent2}} | {{ent2_desc}} | {{ent2_acepta}} | {{ent2_via}} |
| {{ent3}} | {{ent3_desc}} | {{ent3_acepta}} | {{ent3_via}} |

*Cada entregable debe poder aceptarse o rechazarse. Vía: predictiva o adaptativa (obligatorio en híbrido). Fuente única: brief/canvas.*

## 6. Requisitos de alto nivel / High-level requirements

{{requisitos}}
*Capacidades o condiciones imprescindibles para cumplir el propósito; se detallan después en la documentación de requisitos o en las descripciones de producto.*

## 7. Objetivos y criterios de éxito / Objectives and success criteria

| Dimensión / Dimension | Objetivo / Objective | Criterio de éxito / Success criterion | Fuente / Source |
|---|---|---|---|
| Alcance / Scope | {{obj_alcance}} | {{crit_alcance}} | {{src_alcance}} |
| Tiempo / Time | {{obj_tiempo}} | {{crit_tiempo}} | {{src_tiempo}} |
| Costo / Cost | {{obj_costo}} | {{crit_costo}} | {{src_costo}} |
| Calidad / Quality | {{obj_calidad}} | {{crit_calidad}} | {{src_calidad}} |
| Beneficios / Benefits | {{obj_beneficios}} | {{crit_beneficios}} | {{src_beneficios}} |
| Sostenibilidad / Sustainability | {{obj_sostenibilidad}} | {{crit_sostenibilidad}} | {{src_sostenibilidad}} |

*Al menos alcance, tiempo y costo con criterio medible. Copiar del business case y del brief; no reformular.*

## 8. Riesgo general del proyecto / Overall project risk

**Valoración / Rating:** {{riesgo_general}}
*Alto, medio o bajo, considerando volatilidad, incertidumbre, complejidad y ambigüedad del entorno y la exposición de los interesados.*

**Justificación / Rationale:** {{riesgo_justificacion}}
*Una o dos líneas; enlazar los riesgos mayores de `riesgos.csv`.*

## 9. Cronograma resumido de hitos / Summary milestone schedule

| Hito / Milestone | Fecha / Date | Tipo / Type |
|---|---|---|
| Autorización del proyecto / Project authorisation | {{hito_autorizacion}} | puerta |
| {{hito_1}} | {{hito_1_fecha}} | {{hito_1_tipo}} |
| {{hito_2}} | {{hito_2_fecha}} | {{hito_2_tipo}} |
| Aceptación y cierre / Acceptance and closure | {{hito_cierre}} | puerta |

*Fuente única: roadmap y plan de proyecto. Incluir las puertas de fin de etapa.*

## 10. Recursos financieros preaprobados / Preapproved financial resources

**Presupuesto / Budget:** {{presupuesto}} · **Fuente de fondos / Funding source:** {{fuente_fondos}} · **Distribución por período / Per-period limits:** {{distribucion}}
*Misma cifra que el business case y el plan de proyecto. Indicar si incluye presupuesto de riesgo y de cambio.*

## 11. Interesados clave / Key stakeholders

| Interesado / Stakeholder | Rol en el proyecto / Role in the project | Id `stakeholders.csv` |
|---|---|---|
| {{stk1}} | {{stk1_rol}} | {{stk1_id}} |
| {{stk2}} | {{stk2_rol}} | {{stk2_id}} |
| {{stk3}} | {{stk3_rol}} | {{stk3_id}} |

*Incluir usuario final y operador del producto. Detalle en el registro de interesados.*

## 12. Criterios de salida del proyecto / Project exit criteria

{{criterios_salida}}
*Condiciones objetivas para dar por terminado el proyecto: aceptación firmada, ciclos en operación sin incidentes, traspaso a operación, enfoque de beneficios entregado al negocio.*

## 13. Nivel de autoridad del gestor / Project manager authority level

| Dimensión / Dimension | Autoridad / Authority | Límite / Limit |
|---|---|---|
| Personal / Staffing | {{aut_personal}} | {{aut_personal_limite}} |
| Presupuesto y variación / Budget and variance | {{aut_presupuesto}} | {{aut_presupuesto_limite}} |
| Decisiones técnicas / Technical decisions | {{aut_tecnica}} | {{aut_tecnica_limite}} |
| Resolución de conflictos / Conflict resolution | {{aut_conflictos}} | {{aut_conflictos_limite}} |

*Cuatro dimensiones con cifras o criterios: a quién puede asignar o rechazar, hasta cuánto aprueba, qué umbral obliga a escalar (coherente con `estado.json.tolerancias`), qué decide con quién, qué conflictos resuelve y cuáles escala.*

## 14. Autoridad del patrocinador / Sponsor authority

{{autoridad_patrocinador}}
*Qué puede hacer el patrocinador para el proyecto: aprobar cambios, fijar tolerancias, resolver conflictos entre proyectos, defender el proyecto ante la dirección. Complementaria a la del gestor, sin solapamiento.*

## 15. Enfoque de entrega / Delivery approach

{{enfoque_entrega}}
*Predictivo, ágil o híbrido según `estado.json.enfoque_entrega`; en híbrido, vía por entregable (ver tabla 5). El ciclo de vida por etapas de gestión es el marco. En ágil, nombrar al product owner y su margen: ordena e intercambia ítems del backlog dentro de la tolerancia de alcance de la etapa; agregar alcance que desplaza un Must es solicitud de cambio.*

## 16. Aprobaciones / Approvals

| Rol / Role | Nombre / Name | Firma o evidencia / Signature or evidence | Fecha / Date |
|---|---|---|---|
| Patrocinador u originador / Sponsor or originator | {{firma_patrocinador}} | {{firma_patrocinador_evidencia}} | {{firma_patrocinador_fecha}} |
| Gestor de proyecto / Project manager | {{firma_gestor}} | {{firma_gestor_evidencia}} | {{firma_gestor_fecha}} |

*La evidencia puede ser firma, correo o acta. La aprobación se registra como puerta `autorizar-proyecto` en `estado.json` por `pm-director`; hasta entonces el acta sigue en `borrador`.*

## Lista de verificación / Checklist
- [ ] Propósito remite a una fuente de justificación identificable.
- [ ] Objetivos con criterio de éxito medible al menos para alcance, tiempo y costo.
- [ ] Al menos una exclusión explícita; restricciones y supuestos separados.
- [ ] Cada entregable es aceptable o rechazable y tiene autoridad de aceptación; vía por entregable si híbrido.
- [ ] Autoridad del gestor en cuatro dimensiones con cifras; umbral de escalado coherente con las tolerancias.
- [ ] Autoridad del patrocinador complementaria, sin solapamiento.
- [ ] Hitos con fecha y coherentes con roadmap, plan y business case.
- [ ] Presupuesto idéntico al del business case y el plan; fuente de fondos declarada.
- [ ] Criterios de salida objetivos.
- [ ] Riesgo general justificado en una o dos líneas.
- [ ] Interesados incluyen usuario final y operador.
- [ ] Firmas o evidencia de aprobación previstas; estado `borrador` hasta la puerta.
- [ ] Coherente con business case, enunciado del alcance, cronograma de hitos, presupuesto, registro de interesados y registro de riesgos.
