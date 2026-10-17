---
tipo: enfoque-sostenibilidad
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enfoque de gestión de sostenibilidad · Sustainability management approach — {{proyecto}}

> Acciones, revisiones y controles para alcanzar las metas de sostenibilidad del proyecto, trazables a los compromisos del negocio. Parte del PID; lo elabora el gestor, lo aprueba el ejecutivo, lo acuerda el usuario sénior. / Actions, reviews and controls for the project's sustainability targets.

**Aplicabilidad / Applicability:** {{aplicabilidad}}
*`completo`, `minimo` (sección dentro del business case) o `no aplica` con la razón. En proyectos pequeños sin impacto relevante, una línea razonada basta.*

## 1. Alcance / Scope

**Metas de sostenibilidad gestionadas / Sustainability targets managed:** {{alcance_metas}}
*Qué metas cubre este enfoque: ambientales, sociales, de gobernanza, de desmantelamiento o reutilización. Enlaza con la sección 6 del business case.*

**Compromisos corporativos de referencia / Corporate commitments referenced:** {{compromisos}}
*Política ESG, objetivos de cero neto, ODS adoptados, códigos de compra ética. Nombrarlos; no inventarlos.*

## 2. Metas, medición y tolerancias / Targets, measurement and tolerances

| Id | Meta / Target | Medida / Measure | Línea base / Baseline | Objetivo / Goal | Tolerancia / Tolerance | Método y frecuencia / Method and frequency | Responsable / Owner |
|---|---|---|---|---|---|---|---|
| MS-01 | {{s1_meta}} | {{s1_medida}} | {{s1_base}} | {{s1_objetivo}} | {{s1_tolerancia}} | {{s1_metodo}} | {{s1_responsable}} |
| MS-02 | {{s2_meta}} | {{s2_medida}} | {{s2_base}} | {{s2_objetivo}} | {{s2_tolerancia}} | {{s2_metodo}} | {{s2_responsable}} |

*La tolerancia es el margen antes de escalar; se copia a `estado.json.tolerancias.sostenibilidad`. Las medidas deben ser verificables por un tercero.*

## 3. Sostenibilidad en las decisiones del proyecto / Sustainability in project decisions

**Criterio en el análisis de opciones / Criterion in options analysis:** {{criterio_opciones}}
*Cómo pesó (o pesará) la sostenibilidad al comparar opciones: por ejemplo, un presupuesto de emisiones como restricción.*

**Sostenibilidad en el enfoque del proyecto / Sustainability in the project approach:** {{criterio_enfoque}}
*Cómo el modelo de entrega, las compras y la tecnología elegida sostienen las metas.*

**Intercambios aceptados / Accepted trade-offs:** {{intercambios}}
*Qué se sacrificó en costo, tiempo o alcance por sostenibilidad, o al revés, y quién lo decidió.*

## 4. Procedimientos y controles / Procedures and controls

**Revisiones formales / Formal reviews:** {{revisiones}}
*Cuándo se revisan las metas: fin de cada etapa como mínimo; auditorías o certificaciones si aplican.*

**Vigilancia del entorno / Environmental scanning:** {{vigilancia}}
*Quién vigila cambios regulatorios o de compromisos corporativos que afecten las metas; se registra como responsabilidad formal.*

**Gestión tras el cierre / Post-closure management:** {{post_cierre}}
*Quién mide y responde por las metas cuando el producto esté en operación; desmantelamiento o fin de vida del producto si corresponde.*

## 5. Responsabilidades / Responsibilities

| Rol / Role | Responsabilidad / Responsibility |
|---|---|
| Ejecutivo / Executive | {{resp_ejecutivo}} |
| Usuario sénior / Senior user | {{resp_usuario_senior}} |
| Proveedor sénior / Senior supplier | {{resp_proveedor_senior}} |
| Gestor de proyecto / Project manager | {{resp_gestor}} |
| Gestores de equipo / Team managers | {{resp_gestores_equipo}} |
| Aseguramiento / Assurance | {{resp_aseguramiento}} |

*El ejecutivo responde por la alineación con los compromisos corporativos; las descripciones de rol incluyen estas responsabilidades.*

## 6. Recursos, herramientas y estándares / Resources, tools and standards

{{recursos_herramientas_estandares}}
*Calculadoras de huella, especialistas, normas de medición o reporte aplicables, datos necesarios y su origen.*

## 7. Referencias / References

{{referencias}}
*Business case (sección 6), política corporativa, enfoque comercial (compras éticas), descripciones de rol.*

## Lista de verificación / Checklist
- [ ] Aplicabilidad declarada (completo, mínimo o no aplica con razón).
- [ ] Cada meta trazable a un compromiso corporativo nombrado.
- [ ] Medidas verificables con línea base, objetivo, tolerancia, método y responsable.
- [ ] Tolerancias coherentes con el business case y copiadas a `estado.json`.
- [ ] Revisiones como mínimo en cada fin de etapa.
- [ ] Responsable de vigilar el entorno y responsable post-cierre nombrados.
- [ ] Intercambios con otros aspectos de desempeño documentados.
- [ ] Estado `borrador` hasta la aprobación del ejecutivo.
