# Guía de enfoques de gestión · Management approaches guide

## 1. Detalle por enfoque
### 1.1 Calidad
Alcance; procedimientos de planificación y control (incluida aceptación y delegaciones de la autoridad de aceptación); responsabilidades (aseguramiento por interés); recursos; herramientas; estándares (formato del registro de calidad); normas y objetivos de calidad por entregable con métrica y umbral; procedimiento de no conformidad (quién registra, quién analiza, en cuánto se cierra). En ágil: definición de "hecho" (DoD) y "listo" (DoR). Con BMAD: el code review de BMAD y el gate de preparación del sprint planning (PASS/CONCERNS/FAIL) figuran como métodos de verificación; la aceptación por requisito usa la matriz de trazabilidad derivada (`pm-bmad-puente`).

### 1.2 Riesgo
Procedimiento (identificar, evaluar, planificar, implementar, comunicar); escalas 1–5 de probabilidad e impacto por objetivo con definiciones operativas; matriz P×I y puntuación (la de `registro.py`: probabilidad × impacto; alto ≥ 15, medio 6–12, bajo ≤ 5); EMV = impacto monetario × probabilidad (1–5 → 10/30/50/70/90 %); riesgo residual (`probabilidad_residual` × `impacto_residual`) y disparador; línea de tolerancia (por defecto: ningún riesgo alto abierto sin respuesta y propietario); proximidad; categorías; apetito y tolerancia; presupuesto de riesgo y reservas (contingencia dentro del BAC vs. gestión fuera, la libera la junta) con autoridad de liberación; roles (dueño y ejecutor); cadencia. Con BMAD: decisiones AD con incertidumbre alimentan el registro citando el id.

### 1.3 Issues y control de cambios
Cinco bloques: líneas base, resolución de issues, control de cambios, delegación de autoridad, presupuesto de cambio. Tipología con exactamente los cinco tipos canónicos; severidad y prioridad con definiciones; niveles de decisión; acciones en `acciones.csv`, no como issues; procedimiento de cinco pasos con tiempos (capturar, evaluar, proponer, decidir, implementar); definiciones de cambio vs. revisión para cronograma, presupuesto, alcance y documentos; autoridad de cambio con límites; en ágil/híbrido, entregables bajo control formal vs. backlog y regla de swaps del PO. Con BMAD: sección 5.1 (ver §4).

### 1.4 Datos y tecnología digital
Tecnología para gestionar y para el trabajo especializado; fuente de verdad por tipo de dato (si dos herramientas tienen el mismo dato, cuál manda y cómo se sincronizan); siete preguntas de datos (origen, custodia, seguridad, privacidad, acceso, calidad, destino al cierre); audiencias de los tableros; uso de IA con guardarraíles (contenido marcado como borrador, datos sensibles, revisión humana); integraciones conectadas como capacidades (ver §5); quién puede conectar herramientas y gestionar tokens.

### 1.5 Planes subsidiarios combinados
- **Alcance y requisitos** (dueño único del CÓMO; el QUÉ —enunciado y PBS/WBS— es de `pm-planificacion-por-productos`): descomposición, cambio vs. elaboración progresiva, aceptación, elicitación, categorías, priorización con innegociables, trazabilidad hasta la prueba, backlog. Con BMAD: los requisitos viven en el PRD; la trazabilidad la genera `bmad.py trazabilidad`; el plan solo define el CÓMO.
- **Cronograma y costos**: metodología, herramienta, unidades, precisión y exactitud por momento, umbrales en tres zonas iguales para tiempo y costo, actualización y línea base, iteraciones y releases, reglas de EVM (`evm.py`, incluido `--modo agil`), vínculo con plan de cuentas, informe de costos, autoridad de compromiso de fondos.
- **Recursos y adquisiciones**: estimación y adquisición del equipo, roles con autoridad, formación, recursos físicos, contratistas, integración de adquisiciones en cinco dimensiones, calendario, métricas, jurisdicción y moneda.

### 1.6 Comunicación (último)
Recoge las comunicaciones que exigen los demás enfoques (informes de riesgo, decisiones de cambio, resultados de calidad, revisiones de beneficios, demos); políticas por audiencia; referencia al anexo `02-planificacion/matriz-comunicaciones.md` (lo mantiene `pm-comunicacion-stakeholders`); regla de comunicación extraordinaria (umbral); autorización de información confidencial; frecuencia de highlight y checkpoint; glosario; actualización; enlace con el plan de compromiso. Canales de chat o correo solo si están conectados (si no, el canal es "manual").

## 2. Enfoques en una página (perfil ágil mínimo, SPEC §1.10.12)
| Enfoque | Qué cabe | Qué se omite |
|---|---|---|
| Calidad | DoD y DoR, quién acepta (PO por historia, junta por release), una métrica por release | plan de auditorías, matriz completa de métodos |
| Riesgo | escala 1–5, zonas por defecto, revisión en cada planificación de iteración, dueño, línea de tolerancia | categorías detalladas, RBS |
| Issues y cambios | cinco tipos, severidad y prioridad, swap del PO, qué es solicitud de cambio; con BMAD, la tabla 5.1 con valores por defecto | configuración formal, comité |
| Comunicación | highlight corto con burn-up, demo de fin de iteración, regla extraordinaria; matriz en anexo | glosario, archivo |
| Datos digitales | dónde vive el backlog y quién lo ve; datos personales sí/no; IA marcada; integraciones conectadas (o "ninguna") | inventario de datos completo |
Los planes de alcance, cronograma/costos y recursos/adquisiciones se reducen a un párrafo o "no aplica, con razón".

## 3. Escalas canónicas y columnas de registros (SPEC §1.10.8–9)
| Escala | Valores | Uso |
|---|---|---|
| Probabilidad / impacto | 1–5 (EMV: 10/30/50/70/90 %) | `riesgos.csv` |
| Puntuación P×I | alto ≥ 15 · medio 6–12 · bajo ≤ 5 (configurable con `estado.py umbrales-riesgo`) | zonas, tablero, línea de tolerancia |
| Tipo de issue | `solicitud-cambio`, `fuera-especificacion`, `problema-preocupacion`, `evento-externo`, `oportunidad-negocio` | `issues.csv` |
| Severidad / prioridad | `critica`, `mayor`, `menor`, `informativa` · `urgente`, `alta`, `media`, `baja` | `issues.csv` |
| Nivel de decisión | `equipo`, `product-owner`, `gestor`, `autoridad-cambio`, `junta`, `capa-negocio` | `decisiones.csv` |
| Semáforo de desvío | verde ≤ 50 % de la tolerancia · ámbar 50–100 % · rojo fuera | cronograma/costos, `evm.py` |
Si la organización exige otra escala, se documenta la equivalencia y se avisa a `pm-estado-proyecto`; nunca se escriben valores que `registro.py` rechaza.

Columnas relevantes (`registro.py esquema <registro>`): `riesgos.csv` (`probabilidad`, `impacto`, `puntuacion`, `impacto_monetario`, `valor_esperado`, `disparador`, `probabilidad_residual`, `impacto_residual`, `propietario`, `estado`); `issues.csv` (`tipo`, `severidad`, `prioridad`, `decision`, `decidido_por`); `cambios.csv` (`estado`: abierto | en-evaluacion | pendiente-decision | aprobado | rechazado | diferido | implementado | cerrado; `impacto_beneficios`); `decisiones.csv` (`nivel`); `acciones.csv` (`A-###`, compromisos por actor); `calidad.csv` (`producto`, `metodo_verificacion`, `criterios`, `responsable_productor`, `revisores`, `resultado`; estado inicial `planificada`).

## 4. BMAD: elaboración progresiva frente a cambio
Aplica si `estado.json.integraciones.especificacion = bmad`. Antes de la línea base (`bmad.py linea-base`, que fija `pm-director` tras la puerta) todo ajuste es elaboración. Después:
| Modificación | Por defecto | Registro | Decide |
|---|---|---|---|
| Detallar un FR/NFR sin cambiar id ni intención (criterios, ejemplos, redacción) | elaboración progresiva | `decisiones.csv` nivel `product-owner` | PO |
| Descomponer una épica aprobada en historias o refinarlas | elaboración progresiva | sincronización de backlog (`bmad.py backlog`) | PO / equipo |
| Precisar una AD sin alterar costo, plazo ni riesgo | elaboración progresiva | `decisiones.csv` nivel `equipo` | proveedor sénior o jefe técnico |
| Agregar, retirar o fusionar ids FR/NFR/UJ/SM | cambio | `issues.csv` `solicitud-cambio` | autoridad de cambio / junta según impacto |
| Cambiar intención o meta de un requisito o de una SM-n | cambio | ídem; si la SM-n mide un beneficio, evaluar impacto en el business case | ídem |
| AD nueva o modificada que afecta tolerancias o un producto aprobado | cambio | ídem | ídem |
| Sprint Change Proposal (correct-course) | cambio | ídem | ídem; el "sí" de BMAD no la sustituye |
Notas:
- `bmad.py verificar` detecta ids agregados/retirados y contenido distinto; el gestor clasifica con esta tabla. Un desvío de contenido sin cambio de ids se presume elaboración si cabe en las tres primeras filas; ante duda, es cambio.
- Umbral acumulado: si la elaboración en una etapa mueve la estimación más allá del umbral de alcance de la sección 5 del enfoque (p. ej. +10 % de puntos de la release), se trata como cambio aunque cada ajuste fuera menor.
- Un cambio aprobado se refleja en BMAD por el equipo (flujo de BMAD que corresponda) y `pm-director` fija nueva línea base con versión mayor.
- Los swaps del PO en el backlog siguen la regla ágil general (SPEC §1.10.12) y no requieren modificar el PRD.

## 5. Integraciones conectadas en el enfoque de datos
- Fuente: lo que `pm-integraciones` detecta en la sesión y `estado.json.integraciones` (`estado.py integracion tracker=... chat=...`). No se predefinen ni recomiendan productos; se describen capacidades.
- Por capacidad: sistema conectado, lectura, escritura (siempre con vista previa y confirmación; en subagentes, como decisión humana requerida), carpeta de instantáneas (`03-control/fuentes/<sistema>-AAAA-MM-DD.*`), dueño.
- Capacidades típicas: leer/crear issues, leer/escribir páginas, publicar mensajes, leer transcripciones, leer eventos de calendario, leer OKR.
- Los datos externos nunca reemplazan los registros de gobierno; se citan en los informes con fecha.
- Sin integraciones: "ninguna; alternativa interna (CSV, Mermaid, scripts)".
- Revisión en cada fin de etapa: integraciones nuevas o retiradas actualizan la tabla y `estado.json`.

## 6. Reglas extendidas
1. [PRINCE2] Líneas base al nivel de componente liberable; todo producto y versión con identificador; un cambio aprobado genera versión nueva trazable.
2. [PRINCE2] Rechazar un issue es válido; un issue que lleva la etapa fuera de tolerancia se convierte en excepción; nunca tipos sueltos como "consulta" o "acción".
3. [PRINCE2] Calidad: la autoridad de aceptación es la junta salvo delegación documentada; aseguramiento es de cada miembro de la junta por su interés, nunca del gestor.
4. [PRINCE2] La mayoría de los cambios nacen en el paquete de trabajo: la delegación llega hasta ahí con límites.
5. [PMBOK→Plans] Separar precisión de exactitud, contingencia de reserva de gestión, cambio de revisión o elaboración progresiva.
6. [PMBOK→Plans] Unidades de medida definidas una vez y copiadas a cronograma, costos y recursos.
7. [Plantillas] Cuatro definiciones de cambio con umbral; autoridad con límite por miembro; tres disposiciones (aprobar, diferir, rechazar) en `cambios.csv`.
8. [Plantillas] En híbrido, cada entregable tiene su vía y los planes de alcance, cronograma y cambios tienen sección de integración; en ágil, el plan de recursos se limita a recursos físicos.
9. [Plantillas] Toda métrica de calidad con umbral y método; cada interesado aparece en al menos una fila de la matriz de comunicación.
10. Dueños únicos: comunicación = políticas aquí + matriz en `pm-comunicacion-stakeholders`; alcance = CÓMO aquí + QUÉ en `pm-planificacion-por-productos` (o PRD con BMAD).

## 7. Ejemplo: issues y cambios en una página (ágil con BMAD)
"El PO (M. Sosa) reordena el backlog y cambia historias Should/Could por otras de igual tamaño mientras los Must de la release entren en la etapa (`nivel=product-owner`). Cambiar o quitar un Must, mover la fecha de una release o usar más de 2 iteraciones extra es `solicitud-cambio`: decide la autoridad de cambio (ejecutivo) con presupuesto de 8 k; por encima, la junta. En el PRD con línea base: agregar criterios de aceptación a FR-7 es elaboración; agregar FR-15 o cambiar la meta de SM-2 es solicitud de cambio, igual que cualquier Sprint Change Proposal. Un defecto que impide aceptar una historia es `fuera-especificacion`. Una norma municipal nueva es `evento-externo`. Las tareas de la demo van a `acciones.csv`."
Enfoque de datos del mismo proyecto, sección 1.1: "Tracker conectado — leer y crear issues — escritura solo con confirmación — instantánea semanal en `03-control/fuentes/tracker-AAAA-MM-DD.csv` — dueño: PMO. Chat conectado — publicar highlight — con confirmación — dueño: gestor."

## 8. Casos borde
- Escala no soportada (p. ej. 7×7) → equivalencia a 1–5 o derivar a `pm-estado-proyecto` antes de adoptarla.
- Delegación de cambio sin presupuesto → advertir que es ineficaz; el ejecutivo fija presupuesto o retira la delegación.
- Sin descripciones de producto → enfoques en borrador con `[pendiente de PBS]`, coordinando con `pm-planificacion-por-productos` (o `pm-bmad-puente` si hay PRD).
- Discrepancias de umbrales entre dueños → issue `problema-preocupacion` (severidad `mayor`) con acción `A-###` por dueño; PID no apto para la puerta.
- Integración desconectada a mitad de etapa → el enfoque declara la alternativa interna; los informes citan la última instantánea con su fecha.
