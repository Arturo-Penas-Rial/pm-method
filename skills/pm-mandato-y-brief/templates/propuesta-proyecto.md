---
tipo: propuesta-proyecto
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Propuesta de proyecto · Project proposal — {{proyecto}}

> Una o dos páginas para decidir si vale la pena profundizar. Equivalente PRINCE2: mandato + business case esquemático. / One to two pages so the decision-makers can judge whether to go deeper.

**Versión mínima / Minimal version:** {{version_minima}}
*Indicar `sí` si el proyecto es pequeño: entonces bastan resumen, problema, solución, cifra, equipo y petición; los demás campos se omiten declarándolo.*

## 1. Resumen ejecutivo / Executive summary

{{resumen_ejecutivo}}
*Un párrafo que se entienda solo: problema u oportunidad, cómo se ataca, objetivos y entregables principales. Quien lea solo esto debe poder opinar.*

## 2. Antecedentes / Background

**Contexto y hechos desencadenantes / Context and triggering facts:** {{antecedentes}}
*Historia, condiciones del mercado, normativa, eventos que hacen evidente la necesidad. Al menos un dato con cifra, fecha o hecho verificable.*

**Alineación estratégica / Strategic alignment:** {{alineacion_estrategica}}
*Objetivo de negocio o compromiso corporativo (incluidos ESG) al que contribuye.*

## 3. Solución y enfoque / Solution and approach

**Meta / Goal:** {{meta}}
*Qué se quiere lograr en términos de negocio, en una frase.*

**Alcance resumido / Scope summary:** {{alcance}}
*Qué entra. Tres a cinco viñetas como máximo.*

**Exclusiones / Exclusions:** {{exclusiones}}
*Al menos una. Lo que la gente podría suponer que entra y no entra.*

**Línea de tiempo esperada / Expected timeline:** {{linea_tiempo}}
*Duración aproximada y ventana de entrega; en etapas de gestión si ya se intuyen.*

**Enfoque de entrega / Delivery approach:** {{enfoque_entrega}}
*Predictivo, ágil o híbrido, con la puntuación resumida de los criterios de selección. El ciclo de vida por etapas es siempre el marco.*

**Nota híbrida / Hybrid note:** {{nota_hibrida}}
*Solo si es híbrido: qué entregables van por vía predictiva y cuáles por vía adaptativa, y cómo se integran.*

## 4. Información financiera / Financial information

**Orden de magnitud de la inversión / Order-of-magnitude investment:** {{inversion}}
*Cifra con moneda y nivel de confianza (orden de magnitud, estimación preliminar). Citar la fuente de la cifra.*

**Beneficio esperado / Expected benefit:** {{beneficio}}
*Ahorro, ingreso, cumplimiento o riesgo evitado, cuantificado si es posible; si no, describir cómo se medirá.*

**Métricas opcionales / Optional metrics:** {{metricas_financieras}}
*Payback, ROI o NPV solo si hay datos; declarar supuestos (horizonte, tasa).*

## 5. Recursos / Resources

**Perfil del equipo / Team profile:** {{equipo}}
*Roles, cantidad y nivel. Si aún no se sabe, `[por confirmar]` con quién lo estimará.*

**Recursos físicos / Physical resources:** {{recursos_fisicos}}
*Equipos, instalaciones, licencias, materiales. "Ninguno adicional" es una respuesta válida.*

**Modelo de entrega / Delivery model:** {{modelo_entrega}}
*Interno, externo o mixto; si externo, por producto o por mano de obra.*

## 6. Riesgos y restricciones principales / Key risks and constraints

{{riesgos_restricciones}}
*Tres a cinco amenazas u oportunidades de alto nivel y las restricciones duras (plazo regulatorio, presupuesto cerrado).*

## 7. Conclusión y decisión solicitada / Conclusion and requested decision

{{decision_solicitada}}
*Repaso en dos líneas y petición concreta: autorizar la elaboración del business case y del brief, nombrar al ejecutivo y al gestor, asignar recursos para la etapa de inicio.*

**Decide / Decided by:** {{decisor}} · **Plazo / By:** {{plazo_decision}}
*Rol o comité que decide y fecha en que se necesita la respuesta.*

## 8. Anexos / Appendices

{{anexos}}
*Estudios, encuestas, referencias de mercado. Opcional.*

## Lista de verificación / Checklist
- [ ] El resumen ejecutivo se entiende sin leer el resto y cabe en un párrafo.
- [ ] Hay al menos un dato verificable en los antecedentes.
- [ ] La solución responde al problema planteado, no a otro.
- [ ] Hay al menos una exclusión explícita.
- [ ] La cifra de inversión indica fuente y nivel de confianza.
- [ ] Recursos: perfiles y recursos físicos, o "ninguno adicional".
- [ ] Enfoque de entrega declarado; si híbrido, vías por entregable.
- [ ] La conclusión pide una decisión concreta a un decisor concreto.
- [ ] Cabe en una o dos páginas.
- [ ] Coherente con visión, canvas y brief si existen.
- [ ] Frontmatter completo; estado `borrador`.
