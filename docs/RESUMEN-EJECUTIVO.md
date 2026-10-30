# Resumen ejecutivo · pm-method 2.7.0

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
| El mismo comunicado para todos los interesados y una RACI que nadie vincula al plan | Mensajes que no llegan a quien decide; responsabilidades difusas sobre entregables y KR |
| Se invierte sobre supuestos sin validar y opciones que nadie comparó con números | Proyectos aprobados sobre hipótesis; el business case se descubre falso cuando ya se gastó |
| La primera respuesta a un riesgo se anota sin compararla, el impacto de un cambio se estima a ojo y lo acordado en una reunión depende de quién tomó notas | Reservas que no alcanzan, cambios aprobados por quien no tenía autoridad y compromisos que nadie recuerda |
| Las lecciones se escriben al cierre y nadie las vuelve a usar | Los mismos errores se repiten en el proyecto siguiente |
| Se elige entre alternativas sin reunir la evidencia, sin pesos explícitos y a veces por quien no tiene la autoridad; después nadie sabe qué decisión sigue vigente | Decisiones que se contradicen, se reabren sin rastro o no resisten una auditoría |
| La evidencia de lo decidido queda dispersa en registros, documentos con varias versiones, actas y transcripciones | Buscar «por qué se decidió esto» lleva horas y depende de la memoria de alguien |

## 3. Qué ofrece

| Capacidad | Cómo lo hace | Beneficio |
|---|---|---|
| **Método único y dominante** | PRINCE2 7 define etapas, procesos (SU, DP, IP, CS, MP, SB, CP), gestión por excepción y tolerancias; PMBOK 8 solo aporta técnicas (EVM, CPM, PERT, P×I, EMV, VAN) | Coherencia: siempre se sabe en qué etapa está el proyecto y quién decide |
| **Orquestación con roles** | un orquestador en el hilo principal y cinco subagentes de fase; solo `pm-director` registra decisiones de la junta | El modelo prepara, la persona decide; la separación se hace cumplir con un hook |
| **Fuente única de especificación** | BMAD es la especificación; pm-method la lee por una fachada (`especificacion.py`), fija líneas base con sha256 y detecta desvíos | Trazabilidad requisito → historia → paquete → aceptación sin copias desincronizadas |
| **Guardarraíles permanentes** | `estado.json` y los registros solo cambian por scripts que validan; el hook bloquea ediciones directas por Edit y por Bash | Datos de gobierno íntegros y auditables |
| **Sanidad continua** | `sanidad.py`, 104 códigos en 15 familias (INS, EST, ART, REG, CAM, QUA, TOL, SUP, ESP, INT, STK, MAP, DEC, BIT, DAT) al iniciar sesión y antes de cada puerta; en cada inicio de sesión, un resumen derivado de los registros y el radar de lo que hay que decidir, escalar, desbloquear y vigilar | Los problemas aparecen antes de la junta, no durante |
| **Controles permanentes** | lo que en la práctica se controla a mano, tarde o nunca, se verifica en cada corrida: costo de cada cambio contra el presupuesto de cambio y la reserva de riesgo que fija la junta (excedido = bloqueo de puerta), cambios sobre el límite de la autoridad delegada, historias terminadas sin revisión de calidad, pronóstico de valor ganado contra las tolerancias, condiciones de la junta con seguimiento hasta cumplirse (bloquean el cierre), riesgos con la revisión vencida, riesgos altos sin opciones evaluadas o con una contingencia sin plan, supuestos críticos sin validar, lecciones sin acción o sin verificar, productos aceptados sin revisión y contacto con cada interesado en la frecuencia prometida | La gestión por excepción funciona sola: la junta se entera a tiempo y con el dato |
| **Informes listos para la junta** | highlight y tablero desde un solo cálculo del período, con la cadena de reporte verificada contra el valor ganado; checkpoint, excepción, fin de etapa; briefing de incorporación; tablero por actor; estado de productos derivado de los registros; expediente de auditoría con huellas verificables; exportación Word, Excel y PowerPoint | Menos tiempo armando informes, más tiempo decidiendo; el mismo número en el informe, el tablero y el correo |
| **Decidir con datos** | opciones de respuesta a los riesgos comparadas por valor neto con plan de contingencia; análisis de impacto de cada cambio (tiempo, reserva, capacidad, presupuesto, VAN) con quién decide; estimación de tres valores con reserva de cronograma y capacidad del release por MoSCoW; personas de usuario para priorizar | La decisión se toma con las opciones y el impacto a la vista, y la toma quien tiene la autoridad |
| **Decidir con contexto** | para cualquier elección entre alternativas (riesgo, negocio, planificación, OKR, cambio, adquisición): expediente con la evidencia aplicable y su fuente, matriz con pesos explícitos, eliminatorios y sensibilidad de cada peso, pregunta cerrada para la junta y elección registrada por una persona; la autoridad la fija PRINCE2 y la refleja la RACI; las decisiones vigentes, con su cadena de reemplazos y aviso de contradicciones; un componente de Wardley o un paso del recorrido se nombra en la decisión (hacer o comprar) | Decisiones defendibles: se sabe con qué evidencia, quién y con qué autoridad se tomó cada una, y cuál sigue vigente |
| **Control de las escrituras** | bitácora encadenada de toda escritura de los scripts, sin valores confidenciales, con aviso si algo cambió fuera de ellos; un agente propone cambios con la huella de lo que leyó y una persona distinta los aprueba | Auditoría sin reconstrucciones: qué cambió, quién, cuándo y con qué script |
| **Búsqueda citada (opcional)** | pm-kb, componente aparte del plugin: índice en PostgreSQL de las carpetas de los proyectos, búsqueda en español o inglés con versiones vigente y aprobada y relaciones por ids que siguen funcionando si un archivo se mueve; MCP de solo lectura; se instala sobre WSL2 o con Docker y se mantiene al día solo | La respuesta a «por qué se decidió esto» llega en segundos y con la cita de dónde sale |
| **Portal del proyecto (opcional)** | la web de pm-kb, con token por persona: cartera de proyectos con lo que pide acción primero, el tablero que genera pm-method con una instantánea por cada puerta decidida, artefactos clave y diagramas en un marco aislado, la ficha de cada tarjeta; enlaces de solo lectura que vencen y se revocan, también para un solo actor según la RACI | La junta y quien no usa Claude ven el estado y su historia en el navegador, sin pedir un informe; nada se escribe en la carpeta del proyecto |
| **Visuales profesionales** | organigramas, WBS, roadmaps y one-pagers con archify, diagram-design o visual-explainer; respaldo Mermaid | Comunicación clara con interesados no técnicos |
| **Planificación seria** | WBS, camino crítico, exportación MSPDI a MS Project, presupuesto con reservas, release plan ágil | Planes que se pueden auditar y llevar a la herramienta corporativa |
| **Validar antes de invertir** | supuestos críticos como hipótesis con experimento, criterio y fecha (SUP-01…03), puerta `autorizar-proyecto` con condición P-11, opciones evaluadas con VAN, TIR, repago, sensibilidad y punto de equilibrio (`inversion.py`) | La junta invierte sobre evidencia y sabe qué supuesto aceptó sin validar |
| **Mapas estratégicos** | mapas de Wardley (qué construir, comprar o tercerizar) y de recorrido del cliente con emoción, dolores y service blueprint, desde BMAD o el proyecto; cada inercia termina en un riesgo y cada dolor en un tratamiento con id | Decisiones de compra y de experiencia trazadas hasta el registro |
| **Maestro de interesados** | `pm-interesados`: matriz poder/interés con estrategia por cuadrante, RACI ligada a WBS, requisitos, historias y KR (un A por elemento), estereotipos y preferencias tomadas de entrevistas y actas que una persona confirma, perfil de comunicación por interesado y reporte HTML | Cada interesado recibe lo que necesita por el canal que prefiere, con responsabilidades claras y verificadas |
| **Capa de canales** | `envios.py` envía por correo SMTP, webhooks de Slack o Teams, archivos `.eml` o MCP conectados; simulación por defecto, solo mensajes aprobados, destinos desde el maestro y registro de cada envío | Comunicación personalizada y auditable sin perder el control humano |
| **OKR ligados a beneficios** | `pm-okr` vincula resultados clave a beneficios y métricas de éxito del PRD, con tipos de KR, aspiracional o comprometido, check-ins, salud contra el avance esperado y propuesta de sincronización con Tability o Perdoo | La estrategia se mide con los mismos datos del proyecto |
| **Reuniones a registros** | actas desde transcripciones (VTT, SRT, texto o MCP); decisiones con su nivel, compromisos con responsable y fecha, supuestos, riesgos y lecciones propuestos con cita y hora, que se registran solo cuando una persona los confirma | Lo que se acuerda en una reunión no se pierde |
| **Lecciones que se usan** | lecciones de otros proyectos al arrancar; en la retrospectiva, candidatas con cita; clasificación por impacto y proceso, acción, verificación e informe que alimenta el índice de la organización | Lo aprendido cambia la forma de trabajar y se comprueba que funcionó |
| **Integraciones abiertas** | Jira, Confluence, Slack, Teams, transcripciones, Tability y Perdoo por MCP genérico; nada predefinido | Se adapta a las herramientas que ya usa la organización |
| **Bilingüe** | respuestas en el idioma del usuario; artefactos en el idioma del proyecto (ES/EN) | Equipos y clientes de distintos idiomas |

## 4. Valor diferencial

1. **Gobierno real, no texto generado.** Cada puerta queda en `estado.json` y en `decisiones.csv` con quién decidió,
   cuándo y con qué condiciones. Los subagentes no pueden registrar decisiones de la junta.
2. **La especificación no se duplica.** pm-method no edita BMAD: lee, mide y devuelve decisiones con un documento de
   traspaso. Un requisito nuevo en el PRD sin cambio aprobado aparece como **ESP-10** y bloquea la puerta.
3. **Verificado, no solo diseñado.** 463 pruebas automáticas de regresión (incluida una instalación real de BMAD
   6.12.4 y envíos SMTP y por webhooks contra servidores locales), una suite de integración cruzada de 118 comprobaciones,
   cinco recorridos E2E reproducibles, validación del plugin con la CLI y pruebas en vivo con Claude Code real:
   enrutamiento, guardarraíles, idioma, robustez y skills externas.
4. **Degrada con elegancia.** Sin skills externas usa Mermaid y scripts propios; sin BMAD usa su propia especificación
   (`requisitos.md`, `backlog.csv`); sin MCP trabaja con archivos.
5. **Abierto y portable.** Licencia MIT; la fuente de verdad es una carpeta de Markdown, CSV y JSON que se versiona con
   git y se lee sin pm-method.

## 5. Para quién

| Perfil | Qué obtiene |
|---|---|
| Gestor de proyectos | planes, registros, informes y puertas preparados con método; comunicados por interesado enviados con aprobación; menos trabajo administrativo |
| Ejecutivo y junta | decisiones claras con opciones, tolerancias y excepciones a tiempo |
| Product owner / equipo ágil | backlog sincronizado con BMAD, MoSCoW, release plan, avance por puntos |
| PMO / CoE de IA | un estándar reproducible de gestión asistida, con trazabilidad y controles |

## 6. Evidencia (2026-10-29)

| Verificación | Resultado |
|---|---|
| Validación estructural (`validar_paquete.py`) | OK · 39 skills, listado de 6.966 caracteres (límite 7.500); sintaxis compatible con Python 3.9 |
| Regresión (`probar_paquete.py`) | 558 OK · 0 FALLO con Python 3.13 (554 con 3.9) |
| Integración cruzada (`scripts/pruebas/integracion/correr.py`) | 118 OK · 0 FALLO en 38 eslabones (cadenas 1–5); 122 OK en 40 eslabones con las seis cadenas, en la imagen Docker |
| Validación del plugin (`claude plugin validate .`) | aprobada (con el aviso esperado sobre `CLAUDE.md`) |
| Imagen Docker (`pm-pruebas`, sin red) | todas las pruebas OK sin red (dos corridas; regresión 561 OK con Python 3.14, con el caso DD y diagram-design; 5/5 recorridos E2E; 131 bloques Mermaid; webinar 5/5); imagen `pm-method:2.7.0` de 3,33 GB |
| Enrutamiento en vivo | 60/60 en la batería base; 27/28 con vocabulario de PRINCE2 y PMBOK en español; 25/25 con las skills de BMAD instaladas; 14/14 con el resumen de contexto del hook de inicio; 8/8 en mapas estratégicos; 28/28 en las frases de opciones, personas, radar, reuniones, impacto, auditoría, lecciones, productos, período y estimación; 11/11 en las frases de decisiones con sus frases de control (detalle en [PRUEBAS](PRUEBAS.md)) |
| Diagramas y recorridos | 131 bloques Mermaid, 0 errores; guías E2E 5/5 OK (E2E-1 16 pasos, E2E-2 10, E2E-3 15, E2E-4 16, E2E-5 20; 66 imágenes), con evidencia e imágenes idénticas en dos corridas |
| pm-kb (opcional) | núcleo 39 OK y 116 OK con la base (portal, enlaces compartidos y tableros por actor incluidos); pantallas del portal 68 OK en claro, oscuro y móvil; consultas de oro 14/15 (MRR@5 0,75); `pm-kb verificar` 14 OK en Ubuntu 24.04 limpio y en Docker |
| Material de formación | 5 mazos del webinar sin errores: 10 clases de 90 minutos, 199 diapositivas de contenido, 125 términos de glosario |
| Guardarraíles, idioma y robustez en vivo | guardarraíles 4/4; idioma 5/5; inyección en fuentes, datos desordenados, escala y varias sesiones: todos los chequeos OK; controles permanentes 7/7; integración con BMAD instalado 12/12 |
| Skills externas en vivo | archify, diagram-design, visual-explainer, docx/xlsx/pptx: delegadas y funcionando |

## 7. Límites conocidos (con honestidad)

- El enrutamiento en lenguaje natural es probabilístico: el orquestador y los comandos `/pm-method:…` son la vía
  determinista.
- `cpm.py` cubre dependencias fin-a-comienzo con desfases; relaciones SS/FF/SF, calendarios y nivelación se completan en
  MS Project o ProjectLibre sobre el MSPDI exportado.
- BMAD cambia en casi cada versión menor: el puente está probado con v4, 6.11 y 6.12 (6.12.4 real); fuera de ese rango
  trabaja en modo degradado y lo avisa.
- Los conectores MCP de terceros no se probaron en vivo en este entorno; los contratos están documentados. Los envíos
  SMTP y por webhooks se probaron contra servidores locales, no contra servicios reales.
- Los controles permanentes se probaron con scripts (regresión, integración y guías E2E) y en vivo en un escenario
  (presupuesto de cambio excedido y calidad a volumen); con el presupuesto agotado, `registro.py` no deja que la
  autoridad delegada registre la aprobación y el cambio queda pendiente de la junta.
- Los escenarios de robustez en vivo no se repitieron con las versiones 2.4.0 a 2.6.2; con 2.6.2 se corrió la batería en
  vivo `suite.py todo` (enrutamiento 130/134, guardarraíles e idioma OK); la imagen Docker se construyó y probó con
  2.7.0, pero no con una sesión de Claude Code con credenciales ni en arm64; lo del lado de Windows de las dos guías
  de instalación queda por comprobar.
- Las decisiones con contexto se probaron con scripts (regresión, integración y las cinco guías E2E) y en vivo en el
  enrutamiento, no en una sesión completa que arme y puntúe una hoja; en pm-kb no se probó la respuesta con modelo de
  «Preguntar» ni los modelos de vectores y re-ranqueo.
- El perfil de comunicación solo adapta mensajes: no infiere emociones, personalidad ni datos sensibles; la guía cita
  las normas consultadas, pero no es asesoramiento jurídico.
- PRINCE2® y PMBOK® son marcas de sus titulares; el contenido está destilado en palabras propias.

## 8. Cómo empezar

```bash
claude plugin marketplace add Arturo-Penas-Rial/pm-method
claude plugin install pm-method@pm-method
```

Luego, en una sesión: `/pm-method:pm-nuevo "Mi proyecto"` y "¿qué sigue?". Guía paso a paso según el camino elegido:
[INSTALACION-WSL2](INSTALACION-WSL2.md) (sobre WSL2 o Linux, con Claude Code o Hermes) o
[INSTALACION-DOCKER](INSTALACION-DOCKER.md) (contenedor Docker); guía general: [INSTALACION](INSTALACION.md). pm-kb, la
búsqueda citada en los proyectos, se suma en cualquiera de los dos caminos (§8 de cada guía; referencia en [PM-KB](PM-KB.md)).

Para probar las capacidades paso a paso, como usuario y con prompts: [guías de recorrido E2E](guias/README.md) (riesgos con
opciones y contingencia; alcance, cambio, impacto y mapa de ruta; interesados, OKR, radar y avance; producto de la idea
al producto con BMAD, con el ciclo de las lecciones y el expediente de auditoría; de la idea al proyecto diseñado). Cada guía tiene la tabla "Del uso único al control continuo" y su material de webinar en
[docs/webinar/](webinar/README.md).

## 9. Comparativo honesto: pm-method, PMI Infinity y la gestión tradicional

Consulta de las fuentes de terceros: **2026-10-29**. Comparativo propio, sin relación ni aval de PMI; PMI Infinity™,
PRINCE2® y PMBOK® son marcas de sus titulares y se nombran solo como texto.

**Son categorías distintas.** PMI Infinity es un asistente y coach de IA que responde con el contenido de PMI (web y
app móvil, para miembros de PMI). pm-method es un sistema que gestiona un proyecto concreto dentro de un agente de IA:
lleva el estado, los registros, las puertas y los controles en una carpeta propia. La gestión tradicional es la
práctica establecida: plantillas, planillas, herramientas de cronograma y una PMO. **Infinity responde con el contenido
de PMI; pm-method gestiona el proyecto con su método, sus datos y sus puertas.** No se excluyen: se pueden combinar.

### 9.1 Tabla completa

Leyenda: [n] = fuente de §9.5 (primaria o secundaria, según se indica allí); R = este repositorio; **[verificar]** = dato
no confirmado en una fuente primaria.

| Criterio | pm-method | PMI Infinity | Gestión tradicional |
|---|---|---|---|
| Qué es | sistema de gestión de un proyecto dentro de un agente de IA: Claude Code, también Cowork y Hermes (R) | "your AI that speaks project management": asistente y coach de IA "grounded in global standards from PMI" [1] | práctica con plantillas, planillas, herramientas de cronograma, trackers y una PMO |
| Método y ciclo de vida | PRINCE2 7 manda (etapas, tolerancias, gestión por excepción); PMBOK 8 solo aporta técnicas (R) | estándares de PMI [1]; contenido de PRINCE2 no documentado **[verificar]** | el que defina la organización; depende de la PMO |
| Puertas y autoridad | las decide una persona con nombre y rol; solo `pm-director` las registra y un hook lo impone; la autoridad delegada se controla con un script (R) | no descritas en las fuentes públicas consultadas; la beta para organizaciones habla de agentes que actúan "under your governance" [2] **[verificar]** | actas y firmas de la junta; control manual |
| Fuente de verdad y trazabilidad | `estado.json` y registros CSV que solo cambian scripts que validan; bitácora encadenada; trazabilidad requisito → historia → paquete con BMAD (R) | historial de chats, carpetas ("Folders") y proyectos ("Projects") en la app [9][10]; qué guarda "Projects" **[verificar]** | archivos y herramientas; la trazabilidad depende de la disciplina |
| Generación de artefactos | plantillas propias e informes desde un solo cálculo; exportación a Word, Excel, PowerPoint y MSPDI (R) | agentes para actas de constitución, RACI y planes de interesados y de riesgos; plantillas; creación y descarga de documentos [1][9][10] | manual, sobre plantillas |
| Datos propios del proyecto | trabaja sobre la carpeta del proyecto y BMAD; lee y escribe los registros (R) | carga de documentos para analizar [1][9]; la guía de uso pide no compartir datos confidenciales, sensibles o no públicos [7] | sin restricciones de IA |
| Controles continuos | sanidad con 104 códigos en 15 familias y radar en cada sesión; bloqueos antes de cada puerta (R, §3) | no descritos en las fuentes públicas consultadas | revisiones periódicas de la PMO |
| Integraciones | MCP genérico (Jira, Slack, Teams, etc.) documentado, sin prueba en vivo con servicios reales; envíos SMTP y por webhooks probados contra servidores locales (R, §7) | para organizaciones, las integraciones empresariales figuran como función futura de la beta [2]; una nota de un capítulo de PMI menciona Jira, Trello y MS Project [12] **[verificar]**; API pública no confirmada **[verificar]** | nativas entre las herramientas del mercado |
| Base de conocimiento | destilación propia de PRINCE2, PMBOK y plantillas; no es contenido oficial (R) | contenido oficial de PMI, con citas ("Infinity provides clear references and source visibility") [1]; al lanzarse, "more than 14,000 pieces" de contenido de PMI [8] | manuales, formación y experiencia |
| Privacidad y dónde viven los datos | archivos en la máquina o el repositorio del usuario; lo que el modelo lee va al proveedor del modelo según su política y el plan contratado (R) **[verificar la política de cada plan]** | modelos de OpenAI, Google y Cohere; "PMI does not train or fine-tune the models" y los proveedores no usan los datos para mejorar sus modelos [5]; las entradas se almacenan [7]; residencia y retención no publicadas **[verificar]** | donde la organización decida |
| Costo | plugin libre (MIT); requiere un plan pago de Claude (Pro: USD 20 por mes, o 17 por mes con pago anual; "Claude Code is included in all paid plans") o la API [16][17]; costo semanal en un proyecto real sin medir (R) | incluido en la membresía Professional de PMI, no en la cuenta gratuita; prueba de 30 días sin tarjeta [3][4]; el monto de la membresía no aparece en pmi.org (USD 154 + 10 de inscripción el primer año según un tercero [15]) **[verificar]**; para organizaciones, beta con lista de espera y sin precio publicado [2] | licencias de herramientas y horas de personas |
| Instalación y adopción | técnica: GitHub, terminal, WSL2 o Docker en Windows; Python (R) | ninguna: web y app móvil "PMI Official" [1][10][11] | conocida; requiere formación en el método |
| Idioma | español e inglés: responde en el idioma del usuario y escribe los artefactos en el del proyecto; idioma en vivo 5/5 (R, §6) | no declarado en las fuentes leídas; la app figura solo en inglés en el App Store [10]; si responde en español **[verificar]** | el de la organización |
| Madurez y evidencia | pruebas de laboratorio amplias (§6); **sin piloto en un proyecto real**: el plan existe ([PILOTO](PILOTO.md)) y no hay resultados (R) | en el mercado desde el 22 de enero de 2024 [8]; la app supera las 50.000 descargas en Google Play [11]; sin métricas de resultados publicadas **[verificar]** | décadas de uso y aceptación institucional |
| Soporte | un solo autor, código abierto, sin soporte comercial (R) | institución PMI | proveedores de herramientas y PMO |
| Exactitud | cálculos y validaciones con scripts deterministas; el texto del modelo requiere revisión humana (R) | "Output may not always be accurate" [6]; la guía deja la verificación a cargo de quien usa [7]; críticas de terceros sobre versiones de 2024 y 2025 [13][14] | depende de la persona |

### 9.2 Dónde PMI Infinity o la gestión tradicional son mejores

- **PMI Infinity:** contenido oficial de PMI con citas; nada que instalar; web y móvil; apto para cualquier miembro sin
  perfil técnico; respaldo institucional y un programa de seguridad propio [2][5]; costo ya cubierto para quien es
  miembro; muy bueno para aprender, consultar el estándar y redactar un primer borrador.
- **Gestión tradicional:** madurez y aceptación institucional (auditores, juntas, contratos); cronogramas con
  calendarios, nivelación, relaciones SS/FF/SF y carteras; ningún proveedor de IA en el medio; datos sin restricción;
  sin riesgo de contenido generado inventado.

### 9.3 Cuándo conviene cada uno

| Situación | Conviene |
|---|---|
| Aprender o consultar el estándar de PMI y redactar un primer borrador de acta o RACI, también desde el móvil | PMI Infinity |
| PMO madura, cronogramas con calendarios y nivelación, carteras o auditorías que exigen herramientas establecidas | gestión tradicional (pm-method exporta a ella en MSPDI) |
| Proyecto con junta y tolerancias PRINCE2 que necesita trazabilidad requisito → entrega, decisiones auditables y controles que corran solos | pm-method, tras un piloto en paralelo |
| Equipo de producto que ya especifica con BMAD | pm-method |
| Datos confidenciales que no pueden salir de la organización | gestión tradicional; pm-method solo con un plan o proveedor de IA aprobado por la organización; PMI Infinity desaconseja cargarlos [7] |
| Personas sin perfil técnico y sin apoyo para instalar | PMI Infinity o gestión tradicional; pm-method necesita a alguien que lo instale |

Se combinan: PMI Infinity para consultar el estándar, pm-method para llevar el proyecto y la herramienta corporativa
para el cronograma detallado.

**Lo que pm-method no hace o no probó:** no es contenido oficial de PMI ni de PeopleCert ni está avalado por ellos; no
reemplaza a MS Project o Primavera en calendarios, nivelación o carteras; no tiene app móvil ni web propia (salvo el
portal opcional de pm-kb, para consultar y compartir en modo lectura); no tiene un piloto en un proyecto real, así que el ahorro de tiempo y la usabilidad con
líderes no técnicos están sin medir; depende de un proveedor de modelos (política de datos, precio y límites de uso);
exige instalación técnica, y Windows nativo, Cowork y arm64 tienen partes sin verificar; tiene un solo autor y no tiene
soporte comercial; el texto del modelo puede equivocarse y los borradores requieren revisión humana, como en cualquier
asistente.

### 9.4 Mensajes clave

1. **"Infinity responde; pm-method gestiona."** PMI Infinity es un asistente de consulta y redacción sobre el
   contenido de PMI; pm-method lleva el proyecto: estado, registros, puertas y controles en archivos propios.
2. **"La persona decide y queda escrito."** En pm-method las puertas las decide una persona con autoridad, un hook
   impide que las registre otro agente y cada escritura queda en una bitácora verificable.
3. **"Complementa, no reemplaza."** Convive con la PMO y sus herramientas (exporta a Word, Excel, PowerPoint y MS
   Project) y con PMI Infinity como fuente de consulta del estándar.
4. **"Probado en laboratorio, listo para piloto."** Pruebas reproducibles y recorridos E2E (§6); el ahorro de tiempo
   se mide en un piloto en paralelo de 4 semanas ([PILOTO](PILOTO.md)) antes de prometerlo.
5. **"Abierto y portable, con un costo de entrada técnico."** Licencia MIT y datos en Markdown, CSV y JSON; requiere
   Claude Code (u Hermes) con una cuenta paga y alguien que lo instale.

Sin cifras de ahorro: no hay en las fuentes consultadas un dato confiable del tiempo administrativo de un gestor, y el
de pm-method sale del piloto.

### 9.5 Fuentes (consultadas el 2026-10-29)

| # | Fuente | Tipo | Fecha del contenido |
|---|---|---|---|
| 1 | https://www.pmi.org/infinity | primaria | sin fecha |
| 2 | https://www.pmi.org/business-solutions/commercial-partners/pmi-infinity-for-organizations | primaria | beta 2026 |
| 3 | https://www.pmi.org/membership | primaria | sin fecha (sin precios) |
| 4 | https://www.pmi.org/Free-Trial | primaria | sin fecha |
| 5 | https://www.pmi.org/trust-center | primaria | sin fecha |
| 6 | https://www.pmi.org/infinity-terms-of-use | primaria | sin fecha |
| 7 | https://www.pmi.org/-/media/pmi/documents/public/pdf/membership/user_guidelines_and_disclaimer_pmi_infinity_1.pdf | primaria (guía de uso) | sin fecha |
| 8 | https://www.pmi.org/about/press-media/2024/pmi-introduces-pmi-infinity-the-all-new-ai-powered-resource-for-project-professionals | primaria (comunicado) | 22-01-2024 |
| 9 | https://www.projectmanagement.com/blog-post/80673/accomplish-more-with-ai-powered-pmi-infinity- | primaria (sitio de PMI) | 31-08-2026 |
| 10 | https://apps.apple.com/us/app/pmi-official/id6744980359 | primaria (ficha del editor) | versiones de 2025 y 2026 **[verificar el año de las últimas]** |
| 11 | https://play.google.com/store/apps/details?id=org.pmi.mobileapp&hl=en_US | primaria (ficha del editor) | actualizada el 14-10-2026 |
| 12 | https://pmi-gc.de/en/news-eng/1283-pmi-infinity-2-0---the-ultimate-ai-powered-project-management-coach | secundaria (capítulo de PMI) | sin fecha visible |
| 13 | https://www.projectmanagement.com/discussion-topic/197400/pmi-infinity-launches-today--thoughts-on-the-new-ai-powered-tool-/?pageNum=5 | secundaria (foro) | enero de 2024 |
| 14 | https://www.scottgraffius.com/blog/files/pmi-infinity-ai-gets-the-basics-of-team-development-alarmingly-and-repeatedly-wrong---by-scott-m-graffius.html | secundaria (opinión) | 17-06-2025 |
| 15 | https://pmstudycircle.com/pmi-membership-fee/ | secundaria | 04-04-2026 |
| 16 | https://claude.com/pricing | primaria (proveedor del modelo) | vigente al 2026-10-29 |
| 17 | https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan | primaria (proveedor del modelo) | vigente al 2026-10-29 |
| R | este repositorio: §3, §6 y §7 de este documento, [PILOTO](PILOTO.md), [PRUEBAS](PRUEBAS.md), [INSTALACION](INSTALACION.md) | repositorio | 2026-10-29 |

**Por verificar:** precio vigente de la membresía de PMI en pmi.org; si PMI Infinity responde en español; qué guarda
la función "Projects" de la app; integraciones y API de PMI Infinity (la página de PMI las presenta como futuras y un
capítulo menciona Jira, Trello y MS Project); precio y disponibilidad general de Infinity for Organizations; residencia
y retención de datos de PMI Infinity; si incluye contenido de PRINCE2; año de las versiones recientes de la app;
política de datos del proveedor del modelo según el plan con que se use pm-method; y, del lado de pm-method, resultados
del piloto, Windows nativo, Cowork, Docker Desktop, arm64 y conectores MCP de terceros en vivo.
