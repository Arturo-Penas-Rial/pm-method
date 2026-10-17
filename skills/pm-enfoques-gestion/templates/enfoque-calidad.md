---
tipo: enfoque-calidad
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enfoque de gestión de la calidad · Quality management approach — {{proyecto}}

> Técnicas, estándares y responsabilidades para alcanzar las especificaciones y los criterios de aceptación. Parte del PID. Mapeo del paquete: ≈ plan de gestión de la calidad (quality management plan). Lo prepara el gestor; lo aprueba el ejecutivo; lo acuerdan usuario y proveedor sénior; aseguramiento verifica. / How quality will be planned, controlled, assured and reported.

**Versión mínima / Minimal version:** {{version_minima}}
*`sí`: tabla de entregables con criterio de aceptación y quién lo verifica, más una línea sobre cómo se tratan los defectos.*

## 1. Alcance / Scope

{{alcance}}
*Qué productos y qué trabajo cubre este enfoque; qué queda regido por el sistema de calidad del proveedor o del negocio.*

## 2. Normas y estándares aplicables / Applicable standards

| Norma o política / Standard or policy | Aplica a / Applies to | Verificable mediante / Verified by |
|---|---|---|
| {{norma_1}} | {{norma_1_aplica}} | {{norma_1_verif}} |
| {{norma_2}} | {{norma_2_aplica}} | {{norma_2_verif}} |

*Normas del sector, regulación, políticas internas, sistemas de calidad del proveedor. Específicas y verificables, no genéricas.*

## 3. Objetivos de calidad por entregable / Quality objectives per deliverable

| Producto / Product | Métrica o especificación / Metric or specification | Umbral / Threshold | Tolerancia de calidad / Quality tolerance | Método de medición / Measurement method | Momento / When |
|---|---|---|---|---|---|
| {{prod_1}} | {{prod_1_metrica}} | {{prod_1_umbral}} | {{prod_1_tolerancia}} | {{prod_1_metodo}} | {{prod_1_momento}} |
| {{prod_2}} | {{prod_2_metrica}} | {{prod_2_umbral}} | {{prod_2_tolerancia}} | {{prod_2_metodo}} | {{prod_2_momento}} |

*Copiar de las descripciones de producto cuando existan; si no, `[pendiente de PBS]`. Cada objetivo con métrica, umbral y método. Coherente con `estado.json.tolerancias.calidad`.*

## 4. Procedimientos de gestión de la calidad / Quality management procedures

**Planificación de la calidad / Quality planning:** {{planificacion}}
*Cómo se capturan expectativas y criterios de aceptación en la descripción del producto del proyecto y cómo se derivan especificaciones en cada descripción de producto; quién participa.*

**Control de calidad / Quality control:** {{control}}
*Métodos por tipo de producto (inspección, prueba, revisión, demostración, prototipo), cómo se registran en `calidad.csv`, qué pasa si un producto no pasa.*

**Aseguramiento / Assurance:** {{aseguramiento}}
*Cómo cada miembro de la junta asegura su interés (negocio, usuario, proveedor); auditorías de proceso; independencia del gestor.*

**Aceptación y delegaciones / Acceptance and delegations:** {{aceptacion}}
*La autoridad de aceptación es la junta salvo delegación: tabla de producto → quién acepta → evidencia requerida. Toda delegación queda aquí.*

**No conformidad y retrabajo / Non-conformance and rework:** {{no_conformidad}}
*Quién registra, quién analiza la causa, en cuánto tiempo se cierra, cuándo se convierte en issue fuera de especificación.*

**Desviaciones del estándar corporativo / Deviations from corporate standards:** {{desviaciones}}
*Cualquier diferencia con el sistema de calidad de la organización, destacada y justificada (es adaptación).*

## 5. Definición de "hecho" y "listo" (ágil / híbrido) / Definition of done and ready (agile / hybrid)

**Listo / Ready:** {{definicion_listo}}
*Condiciones para que un elemento entre en una iteración.*

**Hecho / Done:** {{definicion_hecho}}
*Condiciones para considerar un incremento terminado y aceptable; incluye pruebas, documentación y revisión.*

## 6. Responsabilidades / Responsibilities

| Rol / Role | Planificación / Planning | Control / Control | Aseguramiento / Assurance | Aceptación / Acceptance |
|---|---|---|---|---|
| Ejecutivo / Executive | {{resp_ex_plan}} | {{resp_ex_ctrl}} | {{resp_ex_aseg}} | {{resp_ex_acep}} |
| Usuario sénior / Senior user | {{resp_us_plan}} | {{resp_us_ctrl}} | {{resp_us_aseg}} | {{resp_us_acep}} |
| Proveedor sénior / Senior supplier | {{resp_ps_plan}} | {{resp_ps_ctrl}} | {{resp_ps_aseg}} | {{resp_ps_acep}} |
| Gestor de proyecto / Project manager | {{resp_gp_plan}} | {{resp_gp_ctrl}} | — | {{resp_gp_acep}} |
| Gestor de equipo / Team manager | {{resp_ge_plan}} | {{resp_ge_ctrl}} | — | — |
| Soporte / Support | {{resp_sop_plan}} | {{resp_sop_ctrl}} | — | — |

*Aseguramiento nunca en gestor, gestores de equipo ni soporte.*

## 7. Recursos, herramientas y técnicas / Resources, tools and techniques

{{recursos_herramientas}}
*Entornos de prueba, laboratorios, expertos, herramientas de pruebas automatizadas, listas de verificación, revisiones estructuradas.*

## 8. Registro de calidad y reportes / Quality register and reporting

**Formato del registro / Register format:** `03-control/registros/calidad.csv` — {{formato_registro}}
*Columnas y valores permitidos; una entrada por actividad de calidad planificada; se alimenta al aprobar cada descripción de producto.*

**Reportes / Reporting:** {{reportes}}
*Qué información de calidad va al checkpoint, al highlight y al informe de fin de etapa.*

## 9. Referencias / References

{{referencias}}
*Descripción del producto del proyecto, descripciones de producto, sistemas de calidad del negocio y del proveedor, contrato.*

## Lista de verificación / Checklist
- [ ] Cada objetivo de calidad con métrica, umbral y método de medición.
- [ ] Entregables sujetos a revisión coinciden con los productos del plan.
- [ ] Al menos un proceso (no solo productos) sujeto a verificación.
- [ ] Autoridad de aceptación y delegaciones explícitas.
- [ ] Aseguramiento por interés, nunca en gestor, equipos ni soporte.
- [ ] No conformidad con quién registra, quién analiza y plazo de cierre.
- [ ] "Hecho" y "listo" definidos en ágil/híbrido.
- [ ] Formato del registro de calidad acorde al esquema CSV.
- [ ] Desviaciones del estándar corporativo justificadas.
- [ ] Coherente con acta, plan de alcance y requisitos, recursos y adquisiciones; estado `borrador` hasta la aprobación del ejecutivo.
