---
name: pm-knowledge
description: "Conocimiento del método: PRINCE2 (método), PMBOK (técnicas), plantillas (campos). Usar: qué es, quién aprueba, qué campos, fórmula, glosario, what is. No: producir artefactos→pm-orquestador."
version: 2.0.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-orquestador
    procesos_prince2: [SU, DP, IP, CS, MP, SB, CP]
    practicas_prince2: [business-case, organizing, plans, quality, risk, issues, progress]
    tecnicas_pmbok: [catálogo de técnicas y fórmulas como referencia]
    artefactos: []
    idiomas: [es, en]
---

# Base de conocimiento del método · Method knowledge base

## Cuándo usar / When to use
- Una skill o agente necesita el detalle de un concepto, proceso, rol, producto de gestión, técnica o fórmula.
- El usuario pregunta "¿qué es…?", "¿quién aprueba…?", "¿qué campos lleva…?", "¿qué dice el método sobre…?".
- Resolver equivalencias entre PRINCE2, PMBOK y plantillas (p. ej. highlight report ≈ project status report).
- EN: look up definitions, process steps, roles, artifact composition, techniques or formulas.
- EN: answer "what is…", "who approves…", "which fields…" questions.

## Idioma
Responder en el idioma del usuario. Las referencias están en español con el término inglés entre paréntesis; traducir al vuelo si el usuario escribe en inglés y mantener el EN entre paréntesis la primera vez.

## Conocimiento
Ocho archivos en `references/` (150–240 KB cada uno). **Nunca leer uno entero**: localizar el encabezado con `grep` y leer solo esa sección (carga progresiva, SPEC §1.4).

### Precedencia de fuentes · Source precedence
1. **PRINCE2 7 = el método**: ciclo de vida por etapas de gestión, procesos SU/DP/IP/CS/MP/SB/CP, roles, tolerancias, puertas, decisiones y productos de gestión. Define QUÉ se hace, CUÁNDO y QUIÉN decide. Manda siempre.
2. **PMBOK 8 = solo el CÓMO o un vacío**: técnicas (EVM, CPM, PERT, estimación, análisis de interesados, adquisiciones…) y relleno de lo que PRINCE2 no detalla. Toda respuesta que use PMBOK la **mapea a una práctica, proceso o producto PRINCE2** (`[PMBOK→Plans/SB] PERT para el plan de etapa`). Nunca se usan sus fases, grupos de procesos ni dominios como ciclo de vida del proyecto.
3. **Plantillas = campos y formato** del artefacto (qué casillas lleva, checklist); no deciden proceso ni roles.
4. **Convenciones del paquete** (SPEC §1.10: esquema de registros de `<pm-estado-proyecto>/scripts/esquema.py`, numeración de etapas, fase `entrega`, umbrales de riesgo, BAC sin reserva de gestión, cinco tipos de issue) prevalecen sobre los esquemas y valores de ejemplo de las referencias, que son trasfondo.
5. Ante conflicto, se aplica el orden anterior y se deja constancia en la respuesta ("PRINCE2 manda; PMBOK aporta la técnica").

### Índice para carga progresiva · Section index
Cómo buscar: `grep -n '^## ' references/<archivo>.md` (secciones) o `grep -n '^### 5\.' references/<archivo>.md` (subsecciones de §5); luego leer desde esa línea hasta el siguiente encabezado del mismo nivel (Read con `offset`/`limit`, o `sed -n '/^## 5\./,/^## 6\./p'`). Para un término: `grep -n -i 'tolerancia' references/<archivo>.md | head`.

| Archivo | Encabezados principales (`## `) | Úsalo para |
|---|---|---|
| `prince2-principios-personas-procesos.md` | 1 Proyecto y gestión · 2 Siete principios (2.1–2.7) · 3 Personas · 4 Modelo de procesos (4.2 capas, 4.5 etapas y puertas) · 5 Los siete procesos (5.1 SU, 5.2 DP, 5.3 IP, 5.4 CS, 5.5 MP, 5.6 SB, 5.7 CP, 5.8 matriz) · 6 Roles (6.3 junta … 6.10 matriz de decisiones) · 7 Glosario · 8 Reglas para agentes · 9 Cobertura | ciclo de vida, quién decide, disparadores, puertas |
| `prince2-practicas-bc-organizacion-planes-calidad.md` | 1 Las prácticas · 2 Caso de negocio · 3 Organización · 4 Planes · 5 Calidad · 6 Reglas para agentes · 7 Glosario · 8 Cobertura | business case y beneficios, organización, planificación por productos, calidad y aceptación |
| `prince2-practicas-riesgo-issues-progreso-productos.md` | 1 Marco común (1.2 objetivos, 1.3 niveles) · 2 Riesgo (2.a–2.g) · 3 Issues (3.a–3.g) · 4 Progreso (4.a–4.g; 4.c tolerancias y excepciones; 4.d productos) · 5 Apéndice A: 16 productos de gestión · 6 Flujo de excepciones · 7 Reglas para agentes (7.5 highlight, 7.6 excepción) · 8 Glosario · 9 Cobertura | registros, tolerancias, excepciones, informes, composición de productos |
| `pmbok8-estandar-principios-ciclos.md` | 1 Términos · 2 Sistema de entrega de valor · 3 Seis principios · 4 Ciclos de vida y enfoques · 5 Cinco áreas de enfoque · 6 Correspondencia PMBOK 8 ↔ PRINCE2 7 · 7 Reglas para agentes · 8 Glosario · 9 Cobertura | elegir enfoque predictivo/ágil/híbrido dentro de etapas; mapeo entre marcos |
| `pmbok8-dominios-procesos-adaptacion.md` | 1 Marco general · 2 Siete dominios (2.1 gobernanza … 2.7 riesgo) · 3 Adaptación (3.6 diagnósticos) · 4 Matriz 40 procesos · 5 Reglas para agentes · 6 Glosario · 7 Cobertura | técnica o métrica para una práctica PRINCE2; cómo adaptar |
| `pmbok8-artefactos-tecnicas-anexos.md` | 1 Marco general · 2 Catálogo de artefactos (2.1–2.9 familias A–I) · 3 Técnicas (3.1 datos … 3.4 decisiones, 3.7 estimación, 3.8 programación, 3.9 financieras, 3.10 calidad, 3.11 riesgo, 3.12 adquisiciones, 3.13 ágiles) · 4 Anexos PMO, IA, adquisiciones · 5 Reglas (5.1 qué técnica para qué pregunta, 5.3 guardarraíles de IA) · 6 Glosario · 7 Cobertura | fórmulas (EVM, CPM, PERT, EMV, VAN), elección de técnica, IA responsable |
| `plantillas-inicio-y-planes.md` | 0 Cómo leer · 1 Marco general · 2 Artefactos de inicio (2.1 propuesta … 2.7 roadmap) · 3 Planes (3.1 alcance … 3.13 plan para la dirección) · 4 Dependencias · 5 Glosario · 6 Reglas para agentes (6.5 elicitación) · 7 Cobertura | campos de brief, charter, business case, planes y enfoques del PID |
| `plantillas-documentos-registros-reportes.md` | 0 Cómo usar · PARTE I documentos (1 solicitud de cambio … 18 retrospectiva) · PARTE II registros (19–26) · PARTE III reportes y auditorías (27–38; 30 EVM, 35 cierre) · PARTE IV combinadas (39–43) · PARTE V esquemas CSV (44.x) · PARTE VI flujo de control (45–46) · PARTE VII glosario · PARTE VIII reglas para agentes (47–52) · PARTE IX cobertura | campos de documentos, registros y reportes; reglas de transición entre estados |

En las plantillas de documentos, las partes son `# PARTE …` (nivel 1): `grep -n '^# PARTE' …`; las fichas son `## <n>.`.

## Entradas requeridas
Ninguna. Si la pregunta se refiere a un proyecto concreto, leer antes `estado.json` (fase, enfoque, tolerancias, `integraciones.especificacion`).

## Procedimiento
1. **Clasificar** la pregunta: método/gobierno (PRINCE2), técnica (PMBOK, mapeada a PRINCE2), campos/formato (plantillas) o equivalencia entre marcos.
2. **Ubicar** el archivo en el índice y la sección con `grep -n '^## '` / `'^### '`; leer solo esa sección (y la contigua si hace falta).
3. **Responder** con definición en palabras propias, regla aplicable, roles, artefacto asociado y ruta en la carpeta del proyecto (SPEC §1.5); si se usó PMBOK, decir en qué práctica, proceso o producto PRINCE2 se aplica.
4. **Si implica producir un artefacto**, derivar a la skill de fase (tabla de `pm-orquestador`). Con BMAD, los requisitos se consultan en el PRD vía `pm-bmad-puente`, no aquí.
5. **Si la fuente no lo determina**, decirlo ("no determinado en la fuente") y ofrecer la práctica habitual etiquetada como tal.

## Reglas del método
1. [PRINCE2] El método por defecto es el ciclo de vida por etapas con gestión por excepción; toda respuesta sobre "cómo se hace" parte de ahí.
2. [PRINCE2] Un producto de gestión tiene propósito, composición, creador, revisor y aprobador; no describir uno sin los cinco.
3. [PRINCE2] Las etapas son de gestión (SU, iniciación, entrega 2…n, cierre); nunca se responden "fases de ejecución" ni grupos de procesos del PMBOK como ciclo de vida.
4. [PMBOK→práctica PRINCE2] Toda técnica se presenta con para qué sirve, cuándo usarla, pasos o fórmula, trampas y la práctica o proceso PRINCE2 donde se aplica.
5. [Plantillas] Un campo se explica por su propósito, no por su etiqueta.
6. Nunca reproducir texto literal de las fuentes; el destilado es original.
7. Equivalencias entre marcos = "mapeo del paquete", no afirmación de las fuentes.
8. Cifra o umbral que no está en las fuentes (p. ej. "±10 %") = valor de referencia configurable.
9. Carga progresiva: citar archivo y encabezado; no cargar archivos completos.
10. Responder en el idioma del usuario con glosario ES/EN coherente.

## Artefactos y plantillas
Esta skill no produce artefactos; devuelve conocimiento con cita de archivo y sección. Para producir, derivar a la skill de fase.

## Calidad
- [ ] Cita el archivo y el encabezado usados; no se cargó un archivo entero.
- [ ] Aplica la precedencia: PRINCE2 para método y decisiones; PMBOK solo como técnica mapeada; plantillas para campos.
- [ ] Distingue regla del método, práctica habitual y mapeo del paquete.
- [ ] Nombra roles y artefacto asociado cuando aplica; idioma correcto.

## Escalamiento y excepciones
- Decisión de gobierno del proyecto (aprobar, escalar, cerrar) → `pm-director` (`pm-direccion-decisiones`).
- Tarea operativa de una fase → agente de fase vía `pm-orquestador`.
- Como subagente o consulta de otra skill: devolver la cita y la respuesta; no preguntar al usuario.

## Ejemplos de invocación
- "¿Qué diferencia hay entre un issue y un riesgo según el método?"
- "¿Quién aprueba el plan de etapa y qué pasa si se excede la tolerancia?"
- EN: "What is a product description and who writes it?"
- EN: "Which EVM formula should I use for EAC if performance will continue as is, and where does it fit in PRINCE2?"
- No activa: "Armame el plan de la etapa 3" → `pm-plan-etapa-y-limites` (vía `pm-orquestador`).

## EN summary
Read-only knowledge skill over eight distilled reference files (PRINCE2 7, PMBOK 8, templates). Explicit precedence: PRINCE2 defines method, life cycle, roles and decisions; PMBOK only supplies techniques or fills gaps, always mapped to a PRINCE2 practice, process or product; templates supply fields. A section index lists each file's main headings so callers grep the heading and read only that section. Answers cite file and heading, label package mappings, never quote sources and route artifact production to phase skills.
