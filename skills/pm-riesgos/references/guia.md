# Guía de gestión de riesgos · Risk management guide

## 1. Escala P×I y enfoque de riesgo
- Escala por defecto 1–5 para probabilidad e impacto; umbrales del paquete (SPEC §1.10.9): **alto ≥ 15, medio 6–12, bajo ≤ 5** (los productos posibles saltan de 12 a 15).
- Línea de tolerancia por defecto: ningún riesgo alto abierto sin respuesta y propietario.
- Probabilidad 1–5 → 10/30/50/70/90 % para el EMV (configurable en el enfoque).
- El enfoque de riesgo (`02-planificacion/enfoques/enfoque-riesgo.md`, de `pm-enfoques-gestion`) fija escalas de probabilidad, impacto y proximidad, umbrales, línea de tolerancia, conversión a %, cadencia de revisión, quién autoriza el presupuesto de riesgo y el destino de la provisión para riesgos no identificados (§5).
- Sin enfoque aprobado: redactar `evaluacion-probabilidad-impacto.md` como anexo, registrar `estado.py --proyecto <dir> artefacto evaluacion-probabilidad-impacto --ruta ... --estado en-revision` y, tras el acto del ejecutivo, `estado.py aprobar evaluacion-probabilidad-impacto --por "Ejecutivo: <nombre>"` (escribe la fila en `decisiones.csv`).
- Umbrales distintos: `estado.py umbrales-riesgo alto=.. medio=..` (los usa `registro.py resumen`); declararlo en cada informe.

## 2. Identificar
- **Descubrimiento de candidatos** (`scripts/riesgos.py --proyecto <dir> candidatos [--fuentes …] [--transcripcion F] [--instantanea F] [--desde AAAA-MM-DD] [--json]`): cada candidato trae clase (riesgo, supuesto, pregunta abierta, issue), tipo (amenaza u oportunidad), origen (archivo y línea, hablante y marca de tiempo, o clave del ticket), ids citados, interesado del maestro, categoría sugerida y posible duplicado o relación con riesgos ya registrados. Salida: `03-control/reportes/<fecha>-candidatos-riesgo.md` (borrador). No registra nada.

| Fuente | Qué lee | Qué se destila |
|---|---|---|
| `bmad` (si `integraciones.especificacion = bmad`) | vía pm-bmad-puente, solo lectura: descubrimiento (brainstorming, PRFAQ, investigación), brief, PRD, arquitectura, UX | secciones de riesgos, restricciones, dependencias y preguntas abiertas; marcas `[SUPUESTO]`, `[por confirmar]`, `TBD`; decisiones diferidas de la arquitectura |
| `transcripciones` | `03-control/reuniones/*transcripcion*.md` (o `--transcripcion`), VTT, SRT, TXT | frases de preocupación, dependencia, incertidumbre, atraso u oportunidad, con hablante y marca de tiempo; sin inferir emociones |
| `tracker` | instantánea más reciente de `03-control/fuentes/<sistema>-AAAA-MM-DD.csv` (Jira vía pm-integraciones) | bug, incidente o impedimento, bloqueado o prioridad alta → **issue** (ya ocurrió) más el riesgo derivado; etiqueta `riesgo` → riesgo |
| `artefactos` | mandato, project brief, canvas, business case, requisitos, plan del proyecto, PID, enfoques, `supuestos.csv` sin validar, `lecciones.csv` | restricciones, riesgos conocidos, supuestos, preguntas abiertas, lecciones previas |
- Del candidato al riesgo: confirmar que afecta un objetivo medible, formular causa → evento → efecto con el propietario, evaluar P×I y registrar citando el origen en `notas` (`origen: brief.md:91 (BMAD) y ronda 2026-10-27 [00:00:13]`, `origen: jira:PS-102`). Un supuesto se valida en `supuestos.csv`; si no puede validarse, se registra el riesgo de que sea falso. Una pregunta abierta recibe dueño y fecha.
- Técnicas: listas por categoría, PESTLE/SWOT, pre-mortem, revisión de supuestos (`supuestos.csv`), lecciones previas, causa-efecto.
- Cada riesgo como causa → evento → efecto en campos separados; rechazar formulaciones que solo nombren causa o efecto; amenazas y oportunidades separadas aunque compartan causa.
- `registro.py --proyecto <dir> agregar riesgos --campo causa=... --campo evento=... --campo efecto=... --campo tipo=amenaza|oportunidad --campo categoria=... --campo propietario=... --campo autor=...` (valida valores; `--forzar` solo con motivo en `notas`).
- Primero los objetivos: no se registra una incertidumbre que no afecte a un objetivo medible.

## 3. Evaluar y perfil agregado
- `registro.py actualizar riesgos R-### --campo probabilidad=N --campo impacto=M --campo proximidad=inminente|corto-plazo|mediano-plazo|largo-plazo --campo impacto_monetario=<monto>`: recalcula `puntuacion` = P×I y `valor_esperado` = impacto monetario × % de P.
- Impacto en unidades del objetivo afectado; si afecta varios, el máximo, anotado en `notas`.
- Exposición: suma de puntuaciones abiertas, conteo por zona, Σ EMV amenazas − Σ EMV oportunidades. Conteos de `registro.py resumen --json` (`altos_abiertos`, `sin_respuesta`, `sin_propietario`, `top`).
- Comparar con `tolerancias.etapa.riesgo` y `.proyecto.riesgo`; si se supera, es pronóstico de excepción en la dimensión riesgo.

## 4. Respuestas
- Justificación: `beneficio = EMV_antes − EMV_despues`; si el costo lo supera, pedir justificación no económica o alternativa.
- Residual (`probabilidad_residual`, `impacto_residual`; EMV residual), riesgos secundarios como filas nuevas, `disparador` observable y plan de contingencia para riesgos significativos; `hoja-riesgo.md` para los que superan la línea.
- Respuesta con costo o esfuerzo → plan de etapa o paquete (acción, responsable, fecha), costo al presupuesto de riesgo; cada acción con fecha también en `acciones.csv` (`--campo origen=R-###`). Si modifica una línea base → solicitud de cambio (`pm-issues-cambios`).
- Una respuesta sin fecha, responsable y recursos no existe; las no ejecutadas son la falla más común.

**Descubrimiento de opciones** (`scripts/riesgos.py --proyecto <dir> opciones [--riesgo R-###] [--umbral N] [--proponer] [--max N] [--json]`). PRINCE2 pide elegir y evaluar respuestas (procedimiento, paso 3; R-10, R-14, R-15) y PMBOK justificar la estrategia frente a las demás (§3.11). Para los riesgos abiertos con P×I ≥ umbral (por defecto `estado.json.umbrales_riesgo.alto`, que fija el enfoque con `estado.py umbrales-riesgo`; 15 sin enfoque) lee `03-control/registros/opciones-riesgo/R-###.csv`, una fila por opción, que redactan el modelo o la persona:

| Columna | Contenido |
|---|---|
| `opcion` | id corto dentro del archivo (O1, O2…) |
| `estrategia` | amenaza: evitar, reducir, transferir, compartir, aceptar, contingencia, escalar; oportunidad: explotar, mejorar, compartir, aceptar, contingencia, escalar |
| `descripcion` | qué se hará; sin `[por confirmar]` para que cuente como evaluada |
| `costo` | costo de la respuesta ahora (número simple ≥ 0) |
| `probabilidad_residual`, `impacto_residual` | 1–5 de la escala aprobada |
| `impacto_monetario_residual` | opcional; vacío = el `impacto_monetario` del riesgo (criterio conservador). Transferir: lo que no cubre el tercero; evitar: 0 si desaparece la causa |
| `monto_contingencia` | opcional; lo que cuesta activar el plan si ocurre (entra ponderado por la probabilidad) |
| `disparador` | obligatorio en `contingencia`; pasa a `riesgos.csv` al elegirla |
| `riesgo_secundario`, `emv_secundario` | el riesgo que crea la respuesta y su EMV (opcional, se descuenta) |
| `notas` | supuestos y fuentes de las cifras |

- Cálculo: EMV residual = % de la probabilidad residual × (impacto monetario residual + monto de contingencia); **valor neto = EMV inherente − EMV residual − EMV secundario − costo** (oportunidad: aumento de EMV − EMV secundario − costo). Una amenaza con residual P×I ≥ umbral queda **sobre la línea** (aceptar o combinar respuestas no alcanza: escalar).
- Validación: estrategia que no aplica al tipo, cifras con moneda o separador de miles, P o I fuera de 1–5 → `invalida` (código de salida 1); faltan descripción, costo, residual o el disparador de una contingencia → `sin-evaluar`; aviso si el residual supera al inherente o si el costo supera la reducción. Faltan estrategias mínimas (amenaza: evitar, reducir, transferir, contingencia; oportunidad: explotar, mejorar, aceptar) → se informa; compartir solo si aplica.
- Orden y recomendación: primero las que quedan bajo la línea, luego mayor valor neto, menor EMV residual y menor costo; con dos o más evaluadas se marca la **recomendada** (★). Es una propuesta: no decide.
- `--proponer` crea la plantilla de los que no la tienen (estrategias mínimas, compartir y aceptar pasivo como referencia de valor neto 0); nunca pisa un archivo existente ni registra nada.
- **PUERTA HUMANA** `opciones --riesgo R-### --elegir O# --por "<rol: nombre>" [--motivo …] [--nivel gestor] [--decision D-###] [--revision AAAA-MM-DD] [--fecha …]`: sin `--por` no registra; si la elegida no es la recomendada exige `--motivo`. Con `registro.py` escribe en `riesgos.csv` `respuesta`, residual, `disparador`, `acciones` («descripción · costo · ΔEMV · valor neto · contingencia · O# (archivo) · D-###») y `estado=en-seguimiento`, y en `decisiones.csv` la decisión con las opciones consideradas (o cita `--decision` si la aceptación ya está registrada; el nivel informado es entonces el de esa fila, no `--nivel`). `--revision` fija `fecha_revision`. Las de la junta las registra `pm-director`.

**Plan de contingencia** (`templates/plan-contingencia.md` → `03-control/registros/R-###-plan-contingencia.md`, citado en `notas`): para la respuesta `aceptar` o `contingencia` de un riesgo significativo (R-12) y como plan de reserva de otra respuesta que puede fallar. Contiene disparador medible (el mismo de `riesgos.csv`), acciones con ejecutor y plazo, propietario, monto y fuente (presupuesto de riesgo, 2.c.6), quién lo activa (la autoridad del enfoque) y cómo se registra la activación: `cambios.csv` con `cargo=reserva-riesgo` y el R-### (CAM-02; consumo en CAM-03), `decisiones.csv` y `acciones.csv`; y el plan alternativo si falla. Sanidad **REG-10** avisa una amenaza alta con respuesta y menos de dos opciones evaluadas, o aceptada sin disparador o sin plan.

| Respuesta | Aplica a | Elegirla cuando… | Trampa habitual |
|---|---|---|---|
| Evitar / Avoid | amenaza | se elimina la causa replanificando, a costo justificado | "evitar" recortando alcance sin control de cambios |
| Reducir / Reduce | amenaza | una acción baja P o I y cuesta menos que la reducción de EMV | mitigar por reflejo sin evaluar el residual |
| Transferir / Transfer | amenaza | un tercero absorbe el impacto financiero (seguro, cláusula) | creer que también se transfiere el retraso o la reputación |
| Compartir / Share | ambas | varias partes reparten pérdidas y ganancias con fórmula acordada | compartir sin contrato |
| Aceptar / Accept | ambas | exposición dentro de tolerancia y actuar cuesta más | usar "aceptar" como ignorar |
| Preparar contingencia | ambas | conviene planificar sin gastar hasta el disparador | sin disparador ni reserva |
| Explotar / Exploit | oportunidad | se puede hacer cierta introduciendo el factor que la provoca | no registrarla por aversión a la pérdida |
| Mejorar / Enhance | oportunidad | una acción sube P o I positivos | acciones sin responsable ni fecha |
| Escalar / Escalate | ambas | excede al equipo, afecta el caso de negocio o rompe tolerancias | seguir tratándolo como propio sin aceptación de la junta |

## 5. Monitorear, presupuesto y escalado
- Cada período: acciones ejecutadas vs. vencidas (por nombre), reevaluar P e I, movimientos de la matriz, disparadores.
- Materializado → `estado=ocurrido` + issue vinculado (`pm-issues-cambios`; `problema-preocupacion` o `evento-externo`). Disparador alcanzado → contingencia con la autorización prevista. Causa desaparecida → `estado=retirado` con nota.
- Presupuesto de riesgo: total de la etapa, comprometido, usado, remanente; cobertura = remanente ÷ Σ EMV aceptados (deseable ≥ 1). No es reserva libre del gestor. Contingencia (identificados, dentro de la línea base) ≠ reserva de gestión (fuera del BAC).
- **Provisión para riesgos no identificados (regla por defecto del paquete):** la provisión para riesgos no identificados va a la **reserva de gestión**, que solo libera la junta; el presupuesto de riesgo financia las respuestas y contingencias de los riesgos identificados. Fórmula: presupuesto de riesgo = Σ costo de las respuestas + Σ EMV residual de las amenazas identificadas (con la contingencia ponderada, `riesgos.py opciones`); la provisión (monto o % que fija el enfoque §7) se propone como `gestion=` en `estado.py presupuesto … --por` (pm-director, nivel junta) y su uso es un cambio con `cargo=reserva-gestion` decidido por la junta (CAM-05). Configurable en el enfoque de riesgo §7 (`destino`: `reserva-gestion` por defecto o `presupuesto-riesgo`); con `presupuesto-riesgo` la provisión es un renglón propio del presupuesto de riesgo y entra en CAM-03. Nunca en los dos.
  - Respaldo: PRINCE2 7 deja al enfoque de gestión de riesgos el acceso y control del presupuesto de riesgo y sugiere una provisión para lo no identificado (`pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §2.b R-18 y §2.c.6); PMBOK 8 asigna lo desconocido-desconocido a la reserva de gestión, fuera de la línea base y liberada por la dirección, y pide no mezclar las dos reservas en una cifra (`pmbok8-dominios-procesos-adaptacion.md` §2.4.a "Reserva", §2.7.a "Clasificación del conocimiento", §5.3 punto 19; `pmbok8-artefactos-tecnicas-anexos.md` §3.2 "Análisis de reservas"). El paquete toma la técnica del PMBOK como regla por defecto porque deja lo identificado bajo la autoridad que fija el enfoque y lo no identificado bajo la junta, que en PRINCE2 retiene la tolerancia de costo (mapeo de `pmbok8-dominios-procesos-adaptacion.md` §2.4.f).
- Escalar a la junta vía `pm-director` cuando excede la influencia del equipo, afecta materialmente el caso de negocio, es riesgo de programa o la respuesta rompería tolerancias: `respuesta=escalar`, `estado=escalado`. Escalar temprano da más opciones.

## 6. Comunicar y auditar
- Sección de riesgos del highlight (para `pm-progreso-reportes`): top 3–5 con respuesta y propietario, movimientos, nuevos, cerrados, ocurridos. Junta: exposición, escalados, presupuesto; equipo: acciones y disparadores; cliente: riesgos que lo afectan.
- `informe-riesgos.md` completo cuando el PID lo pide o el proyecto es grande; omitir la sección cuantitativa si no hubo análisis cuantitativo.
- `auditoria-riesgos.md` en límites de etapa, cierre o a pedido de aseguramiento: eventos ocurridos (¿previsibles?), eficacia de respuestas, cumplimiento, mejoras; indicadores de materialización, sorpresa, eficacia y puntualidad. Conclusiones a `lecciones.csv`.

## 7. Columnas de `riesgos.csv`
`id`, `fecha_identificacion`, `autor`, `categoria`, `causa`, `evento`, `efecto`, `tipo` (amenaza/oportunidad), `probabilidad`, `impacto`, `puntuacion` (calculada), `impacto_monetario`, `valor_esperado` (EMV, calculado), `proximidad`, `disparador`, `respuesta`, `acciones`, `propietario`, `ejecutor`, `probabilidad_residual`, `impacto_residual`, `estado` (abierto, en-seguimiento, escalado, ocurrido, retirado, cerrado), `fecha_revision`, `notas`. Esquema vigente: `registro.py esquema riesgos`.

## 8. Variantes de entrega
- **Ágil/híbrido**: revisión de riesgos en la planificación y la retrospectiva de cada iteración; tablero opcional, pero `riesgos.csv` es la fuente de verdad; la tolerancia de alcance absorbe riesgos por intercambio de ítems que decide el PO (`nivel=product-owner`); un riesgo que amenaza un Must es candidato a excepción.
- **BMAD** (`integraciones.especificacion = bmad`): los artefactos de descubrimiento (brainstorming, PRFAQ, investigación), el brief (riesgos, restricciones, preguntas abiertas), las decisiones de arquitectura (AD-n) y los NFR y supuestos del PRD son fuente de riesgos (`riesgos.py candidatos --fuentes bmad`); se citan por id en `notas` o `causa`, sin copiar el texto. Un gate de preparación del sprint planning con CONCERNS/FAIL se registra como riesgo (o condición de `autorizar-etapa`). Ids nuevos o retirados detectados por `bmad.py verificar` no son riesgos sino solicitudes de cambio (`pm-issues-cambios`).
- **Trackers**: si hay un tracker conectado, riesgos, bugs o bloqueos se leen vía `pm-integraciones` como instantánea en `03-control/fuentes/`; `riesgos.py candidatos --fuentes tracker` los clasifica (issue o riesgo, relación con riesgos existentes) y se incorporan a `issues.csv` o `riesgos.csv` tras revisión; crear tickets de acciones de respuesta solo con confirmación.

## 9. Sesgos y reglas extendidas
- Señales: todos los riesgos "bajos", ninguna oportunidad, ningún escalado en varios períodos, un único propietario → proponer pre-mortem, revisión por pares o redistribución.
- Propietario = la persona más capaz, no la más disponible; evitar concentrar riesgos en una persona.
- Si no hay incertidumbre no hay riesgo: un hecho ocurrido es un issue; revisión cruzada riesgos ↔ issues cada período.
- El perfil combinado alimenta la revisión de la justificación de negocio en cada límite de etapa.
- Monte Carlo solo con datos suficientes; declarar escala, fórmula y supuestos.
