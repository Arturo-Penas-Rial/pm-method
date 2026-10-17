---
tipo: enfoque-beneficios
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enfoque de gestión de beneficios · Benefits management approach — {{proyecto}}

> Define las acciones y revisiones que asegurarán los resultados y confirmarán los beneficios. Parte del PID; lo crea el gestor, lo aprueba el ejecutivo, lo acuerda el usuario sénior; sobrevive al proyecto y se traspasa al negocio al cierre. / Defines how outcomes will be secured and benefits confirmed; outlives the project.

**Gestionado por / Managed by:** {{gestionado_por}}
*`proyecto` mientras dura; `negocio` (usuario sénior o área designada) después del cierre. Si el proyecto está en un programa, indicar que se integra en el plan de beneficios del programa.*

## 1. Alcance / Scope

**Beneficios gestionados y medidos / Benefits managed and measured:** {{alcance_beneficios}}
*Identificadores B-xx y D-xx del business case. Los que quedan fuera (por ejemplo, gestionados por el programa) se nombran con la razón.*

**Resultados que los habilitan / Enabling outcomes:** {{resultados}}
*Qué debe cambiar en la operación para que cada beneficio sea posible; enlaza con la cadena de valor del caso.*

## 2. Beneficios: medición y responsabilidad / Benefits: measurement and accountability

| Id | Beneficio / Benefit | Dueño (rinde cuentas) / Owner | Medida / Measure | Línea base y fecha / Baseline and date | Meta / Target | Fecha prevista / Expected date | Método de medición / Method | Frecuencia / Frequency | Tolerancia / Tolerance | Refs SM / KR |
|---|---|---|---|---|---|---|---|---|---|---|
| B-01 | {{b1_nombre}} | {{b1_dueno}} | {{b1_medida}} | {{b1_base}} | {{b1_meta}} | {{b1_fecha}} | {{b1_metodo}} | {{b1_frecuencia}} | {{b1_tolerancia}} | {{b1_refs}} |
| B-02 | {{b2_nombre}} | {{b2_dueno}} | {{b2_medida}} | {{b2_base}} | {{b2_meta}} | {{b2_fecha}} | {{b2_metodo}} | {{b2_frecuencia}} | {{b2_tolerancia}} | {{b2_refs}} |
| DB-01 | {{d1_nombre}} | {{d1_dueno}} | {{d1_medida}} | {{d1_base}} | {{d1_meta}} | {{d1_fecha}} | {{d1_metodo}} | {{d1_frecuencia}} | {{d1_tolerancia}} | {{d1_refs}} |

*Copiar de la sección 5 del business case: misma medida, misma línea base. Sin línea base no hay forma de demostrar el beneficio. Los des-beneficios también se miden.*

## 3. Procedimientos de realización / Realisation procedures

**Acciones durante el proyecto / Actions during the project:** {{acciones_proyecto}}
*Qué hará el proyecto para que los productos se usen: formación, comunicación, pilotos, transición a operación, retiro del sistema anterior.*

**Acciones del negocio tras el cierre / Business actions after closure:** {{acciones_post_cierre}}
*Qué hará el negocio cuando ya no exista la organización temporal; quién las ejecuta y con qué recursos.*

**Barreras a la adopción identificadas / Adoption barriers identified:** {{barreras}}
*Obstáculos para incorporar las nuevas capacidades al trabajo cotidiano; se registran como riesgos o issues y fijan expectativas realistas de fecha.*

## 4. Revisiones de beneficios / Benefits reviews

| Revisión / Review | Momento / When | Beneficios cubiertos / Benefits covered | Quién confirma / Confirmed by | Entrada / Input | Salida / Output |
|---|---|---|---|---|---|
| Intermedia 1 / Intermediate 1 | {{rev1_momento}} | {{rev1_beneficios}} | {{rev1_quien}} | {{rev1_entrada}} | {{rev1_salida}} |
| Fin de etapa / Stage boundary | cada fin de etapa | previsión de todos | usuario sénior | caso actualizado, mediciones | veredicto en informe de fin de etapa |
| Cierre / Closure | {{rev_cierre_momento}} | realizados hasta la fecha | usuario sénior | informe de fin de proyecto | traspaso al negocio |
| Post-proyecto 1 / Post-project 1 | {{post1_momento}} | {{post1_beneficios}} | {{post1_quien}} | mediciones en operación | acciones correctivas, lecciones |

*Con entregas iterativas, programar revisiones intermedias para los beneficios que llegan durante el proyecto. Las revisiones post-proyecto las encarga el negocio al usuario sénior.*

## 5. Desempeño del producto en operación / Product performance in operation

{{desempeno_producto}}
*Cómo se revisará que el producto funciona en operación (métricas de servicio, incidentes, uso real) para detectar efectos colaterales positivos o negativos.*

## 6. Responsabilidades / Responsibilities

| Rol / Role | Responsabilidad / Responsibility |
|---|---|
| Ejecutivo / Executive | {{resp_ejecutivo}} |
| Usuario sénior / Senior user | {{resp_usuario_senior}} |
| Gestor de proyecto / Project manager | {{resp_gestor}} |
| Aseguramiento / Assurance | {{resp_aseguramiento}} |
| Negocio tras el cierre / Business after closure | {{resp_negocio}} |

*El ejecutivo asegura que las revisiones se planifiquen; el usuario sénior rinde cuentas de que los beneficios se realicen; el gestor mantiene este enfoque hasta el cierre.*

## 7. Recursos y financiación / Resources and funding

**Durante el proyecto / During the project:** {{recursos_proyecto}}
*Personas, estudios, herramientas de medición.*

**Después del cierre / After closure:** {{recursos_post_cierre}}
*Quién paga y quién ejecuta las mediciones post-proyecto. Campo obligatorio: sin financiación, las revisiones no ocurren.*

## 8. Herramientas, técnicas y estándares / Tools, techniques and standards

{{herramientas_estandares}}
*Tableros, encuestas, simuladores, normas de medición aplicables (por ejemplo, definiciones contables para ahorros).*

## 9. Referencias / References

{{referencias}}
*Business case (versión y sección 5), enfoque de sostenibilidad, plan de beneficios del programa, políticas corporativas.*

## Lista de verificación / Checklist
- [ ] Cada beneficio tiene dueño, medida, línea base con fecha, meta, fecha prevista, método y tolerancia.
- [ ] Medidas y líneas base idénticas a las del business case.
- [ ] Revisiones intermedias programadas si hay beneficios durante el proyecto.
- [ ] Acciones del negocio tras el cierre con ejecutor nombrado.
- [ ] Financiación y recursos post-cierre definidos.
- [ ] Desempeño del producto en operación cubierto.
- [ ] Barreras a la adopción registradas como riesgos o issues.
- [ ] Aprobación del ejecutivo y acuerdo del usuario sénior previstos; estado `borrador` hasta la puerta.
