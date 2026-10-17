# Resumen ejecutivo · pm-method 2.1.0

**Gestión de proyectos asistida por IA, con método, gobierno y trazabilidad.**
EN: *AI-assisted project management with a real method, real governance and end-to-end traceability.*

---

## 1. La propuesta en una frase

pm-method convierte a Claude Code (y a Cowork o Hermes) en un **equipo de gestión de proyectos que trabaja con
PRINCE2 7**, usa las técnicas de PMBOK 8 cuando hacen falta, produce los artefactos con plantillas profesionales y
gobierna el producto **sobre la especificación BMAD sin duplicarla**: el equipo de producto especifica, pm-method
gobierna, y cada decisión queda registrada y verificada.

## 2. El problema que resuelve

| Situación habitual | Consecuencia |
|---|---|
| Los asistentes generan documentos de gestión sueltos ("un plan", "un informe") sin ciclo de vida | No hay etapas, tolerancias ni puertas: nadie sabe qué está aprobado |
| La especificación (PRD, épicas, historias) vive en un lado y la gestión en otro | Requisitos sin historias, historias sin requisito, cambios de alcance invisibles |
| El modelo "decide" lo que debería decidir una persona | Riesgo de gobierno: aprobaciones que nadie dio |
| Archivos de estado y registros editados a mano | Datos inconsistentes, informes que no cuadran |
| Integraciones atadas a un proveedor o frágiles | Dependencia y mantenimiento costoso |

## 3. Qué ofrece

| Capacidad | Cómo lo hace | Beneficio |
|---|---|---|
| **Método único y dominante** | PRINCE2 7 define etapas, procesos (SU, DP, IP, CS, MP, SB, CP), gestión por excepción y tolerancias; PMBOK 8 solo aporta técnicas (EVM, CPM, PERT, P×I, EMV, VAN) | Coherencia: siempre se sabe en qué etapa está el proyecto y quién decide |
| **Orquestación con roles** | un orquestador en el hilo principal y cinco subagentes de fase; solo `pm-director` registra decisiones de la junta | El modelo prepara, la persona decide; la separación se hace cumplir con un hook |
| **Fuente única de especificación** | BMAD es la especificación; pm-method la lee por una fachada (`especificacion.py`), fija líneas base con sha256 y detecta desvíos | Trazabilidad requisito → historia → paquete → aceptación sin copias desincronizadas |
| **Guardarraíles permanentes** | `estado.json` y los registros solo cambian por scripts que validan; el hook bloquea ediciones directas por Edit y por Bash | Datos de gobierno íntegros y auditables |
| **Sanidad continua** | `sanidad.py` con familias INS, EST, ART, REG, ESP, INT al iniciar sesión y antes de cada puerta | Los problemas aparecen antes de la junta, no durante |
| **Informes listos para la junta** | highlight, checkpoint, excepción, fin de etapa con valor ganado; tablero por actor; exportación Word, Excel y PowerPoint | Menos tiempo armando informes, más tiempo decidiendo |
| **Visuales profesionales** | organigramas, WBS, roadmaps y one-pagers con archify, diagram-design o visual-explainer; respaldo Mermaid | Comunicación clara con interesados no técnicos |
| **Planificación seria** | WBS, camino crítico, exportación MSPDI a MS Project, presupuesto con reservas, release plan ágil | Planes que se pueden auditar y llevar a la herramienta corporativa |
| **OKR ligados a beneficios** | `pm-okr` vincula resultados clave a beneficios y métricas de éxito del PRD | La estrategia se mide con los mismos datos del proyecto |
| **Reuniones a registros** | actas desde transcripciones (VTT, SRT, texto o MCP) con acciones, riesgos y decisiones confirmadas | Lo que se acuerda en una reunión no se pierde |
| **Integraciones abiertas** | Jira, Confluence, Slack, Teams, transcripciones y Tability por MCP genérico; nada predefinido | Se adapta a las herramientas que ya usa la organización |
| **Bilingüe** | respuestas en el idioma del usuario; artefactos en el idioma del proyecto (ES/EN) | Equipos y clientes de distintos idiomas |

## 4. Valor diferencial

1. **Gobierno real, no texto generado.** Cada puerta queda en `estado.json` y en `decisiones.csv` con quién decidió,
   cuándo y con qué condiciones. Los subagentes no pueden registrar decisiones de la junta.
2. **La especificación no se duplica.** pm-method no edita BMAD: lee, mide y devuelve decisiones con un documento de
   traspaso. Un requisito nuevo en el PRD sin cambio aprobado aparece como **ESP-10** y bloquea la puerta.
3. **Verificado, no solo diseñado.** 80 pruebas automáticas de regresión (incluida una instalación real de BMAD
   6.12.4), validación del plugin con la CLI y pruebas en vivo con Claude Code real: enrutamiento, guardarraíles,
   idioma y skills externas.
4. **Degrada con elegancia.** Sin skills externas usa Mermaid y scripts propios; sin BMAD usa su propia especificación
   (`requisitos.md`, `backlog.csv`); sin MCP trabaja con archivos.
5. **Abierto y portable.** Licencia MIT; la fuente de verdad es una carpeta de Markdown, CSV y JSON que se versiona con
   git y se lee sin pm-method.

## 5. Para quién

| Perfil | Qué obtiene |
|---|---|
| Gestor de proyectos | planes, registros, informes y puertas preparados con método; menos trabajo administrativo |
| Ejecutivo y junta | decisiones claras con opciones, tolerancias y excepciones a tiempo |
| Product owner / equipo ágil | backlog sincronizado con BMAD, MoSCoW, release plan, avance por puntos |
| PMO / CoE de IA | un estándar reproducible de gestión asistida, con trazabilidad y controles |

## 6. Evidencia (2026-10-17)

| Verificación | Resultado |
|---|---|
| Validación estructural (`validar_paquete.py`) | OK · 37 skills, listado de 6.289 caracteres (límite 7.500) |
| Regresión (`probar_paquete.py`) | 80 OK · 0 FALLO |
| Validación del plugin (`claude plugin validate .`) | aprobada |
| Enrutamiento en vivo | v2.0: 82 % en 75 frases → v2.1: 60/60 (detalle en [PRUEBAS](PRUEBAS.md)) |
| Guardarraíles, idioma y robustez en vivo | guardarraíles 4/4; idioma 5/5; inyección en fuentes, datos desordenados, escala y varias sesiones: todos los chequeos OK |
| Skills externas en vivo | archify, diagram-design, visual-explainer, docx/xlsx/pptx: delegadas y funcionando |

## 7. Límites conocidos (con honestidad)

- El enrutamiento en lenguaje natural es probabilístico: el orquestador y los comandos `/pm-method:…` son la vía
  determinista.
- `cpm.py` cubre dependencias fin-a-comienzo con desfases; relaciones SS/FF/SF, calendarios y nivelación se completan en
  MS Project o ProjectLibre sobre el MSPDI exportado.
- BMAD cambia en casi cada versión menor: el puente está probado con v4, 6.11 y 6.12 (6.12.4 real); fuera de ese rango
  trabaja en modo degradado y lo avisa.
- Los conectores MCP de terceros no se probaron en vivo en este entorno; los contratos están documentados.
- PRINCE2® y PMBOK® son marcas de sus titulares; el contenido está destilado en palabras propias.

## 8. Cómo empezar

```bash
claude plugin marketplace add Arturo-Penas-Rial/pm-method
claude plugin install pm-method@pm-method
```

Luego, en una sesión: `/pm-method:pm-nuevo "Mi proyecto"` y "¿qué sigue?". Guía completa: [INSTALACION](INSTALACION.md).

Para probar las capacidades paso a paso, como usuario y con prompts: [guías de recorrido E2E](guias/README.md) (riesgos; alcance, cambio y mapa de ruta; interesados, OKR y avance; producto de la idea al producto con BMAD).
