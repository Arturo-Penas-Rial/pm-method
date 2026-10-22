# Matriz RACI de pm-method 2.4.0 · Humans and agents

Quién hace qué a lo largo del ciclo de vida PRINCE2 cuando se trabaja con los agentes del paquete. La matriz cruza los roles humanos del método con los seis agentes y nombra las skills que ejecutan cada actividad. Está verificada contra `SPEC.md` (§1.10.4, §1.11, §1.13, §1.16), `agents/*.md` y los procedimientos de las skills; la sección 5 resume esa verificación y las tensiones encontradas.

## 1. Leyenda

**Letras**

| Letra | En una columna humana | En una columna de agente |
|---|---|---|
| **R** (Responsible) | Hace el trabajo o lo ejecuta en el mundo real (redacta, revisa, aplica, acepta un paquete). | Prepara, redacta o calcula el borrador; o ejecuta el script de registro **después** de la decisión humana. |
| **A** (Accountable) | Rinde cuentas y tiene la última palabra. Exactamente una por fila. | **Nunca.** Ningún agente es A. |
| **C** (Consulted) | Se le consulta antes de decidir; su opinión cambia el resultado. | Aporta datos o verificaciones (lectura de registros, `verificar`, justificación continua). |
| **I** (Informed) | Se le informa del resultado. | Recibe el resultado (bloque de retorno, `estado.json`). |
| A/R | Rinde cuentas y además hace el trabajo. | — |
| – | No interviene. | No interviene. |

**Columnas humanas.** CN = capa de negocio o patrocinador (en el ejemplo, el consejo directivo) · EJ = ejecutivo · US = usuario sénior · PS = proveedor sénior · GP = gestor del proyecto · JE/PO = jefe de equipo o product owner (en ágil e híbrido, el PO es el usuario sénior o su delegado con autoridad escrita) · AS = aseguramiento · SP = soporte del proyecto · BM = equipo BMAD o de especificación.

**Columnas de agentes.** orq = pm-orquestador (hilo principal) · dir = pm-director · ini = pm-inicio · pla = pm-planificacion · con = pm-control · cie = pm-cierre.

**Notas numeradas.**
- ¹ Autoridad de cambio: por defecto la junta, que decide el ejecutivo. Si se delega (`estado.json.roles.autoridad_cambio`), el delegado decide dentro de su umbral y su presupuesto de cambio; por encima, o si se consume reserva de gestión, vuelve a la junta. En el proyecto de muestra la autoridad de cambio delegada es la usuaria sénior.
- ² Si el pronóstico supera la tolerancia de **proyecto**, la A pasa a la capa de negocio y la decisión se registra con `nivel=capa-negocio`.
- ³ Un comunicado dirigido a la capa de negocio o al exterior lo confirma el ejecutivo; las notificaciones de inicio, autorización y cierre las firma el ejecutivo.
- ⁴ El acta de una reunión la confirma quien la presidió. El acta de la junta (`acta-junta-<fecha>`) es de pm-direccion-decisiones y la confirma el ejecutivo.
- ⁵ Cada riesgo tiene propietario (acepta la respuesta) y ejecutor (hace las acciones); pueden ser cualquiera de los roles. La escala P×I la aprueba el ejecutivo y el uso del presupuesto de riesgo lo autoriza quien diga el enfoque de riesgo (por defecto, el ejecutivo).

## 2. Reglas de la matriz

1. **Ningún agente de IA es Accountable.** La A está siempre en una columna humana. El agente prepara, redacta, calcula o registra; nunca aprueba, rechaza ni condiciona en nombre de una persona.
2. **Solo pm-director registra puertas y aprobaciones.** `estado.py puerta` y `estado.py aprobar` los ejecuta pm-director, y solo después de que el orquestador obtuvo una respuesta humana explícita con nombre y rol. Por eso pm-director figura como R en las filas de puertas y líneas base: registra, no decide.
3. **Solo el orquestador pregunta.** Los subagentes devuelven las preguntas en el bloque "Retorno al orquestador / Return". El orquestador es R cuando presenta una decisión al humano; en el resto de las filas está informado (I) porque recibe todos los retornos.
4. **Los agentes de fase dejan todo en `en-revision`.** pm-inicio, pm-planificacion, pm-control y pm-cierre son R de borradores y de registros operativos (filas de `registro.py`), no de aprobaciones.
5. **La especificación la escribe su dueño.** Con BMAD, el PRD, la arquitectura, las épicas y las historias son del equipo BMAD (R). pm-method solo lee a través de `especificacion.py` y `bmad.py`; las decisiones de gobierno vuelven a BMAD con un traspaso (`bmad.py handoff`). El hook `guardian.py` impide que los subagentes escriban en `_bmad/`, `_bmad-output/` o `.bmad-core/`.
6. **Escrituras externas solo con confirmación.** Publicar, enviar o crear tickets requiere vista previa y confirmación humana; desde un subagente se devuelve como decisión humana requerida.
7. **El PMBOK no cambia la matriz.** Las técnicas (EVM, CPM, PERT, análisis de interesados) son el cómo dentro de una actividad PRINCE2; no agregan roles ni decisiones.

## 3. Matriz principal

| # | Actividad o producto | CN | EJ | US | PS | GP | JE/PO | AS | SP | BM | orq | dir | ini | pla | con | cie | Skills ejecutoras |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | **Puesta en marcha (SU)** | | | | | | | | | | | | | | | | |
| 1 | Mandato | A/R | C | I | I | C | – | – | – | – | I | – | R | – | – | – | pm-mandato-y-brief |
| 2 | Project brief y enfoque de entrega | I | A | C | C | R | – | C | – | C | I | – | R | – | – | – | pm-mandato-y-brief |
| 2b | Mapas de Wardley y de recorrido del cliente (evidencia para opciones, enfoque, hacer o comprar y riesgos) | – | A | C | C | R | – | C | – | C | I | – | R | C | – | – | pm-mapas-estrategicos |
| 3 | Business case (esquemático, completo, actualizado, final) | C | A | C | C | R | – | C | – | – | I | C | R | C | – | R | pm-caso-de-negocio |
| 4 | OKR del proyecto (incluidos check-ins y salud) | C | A | C | – | R | – | – | – | – | I | C | R | C | R | R | pm-okr |
| 5 | Tolerancias de proyecto | A | C | C | C | C | – | C | – | – | I | R | R | – | – | – | pm-caso-de-negocio, pm-enfoques-gestion, pm-direccion-decisiones, pm-estado-proyecto |
| 6 | Estructura de gestión, roles y nombramientos | C | A | C | C | R | I | C | I | I | I | – | R | – | – | – | pm-organizacion-roles |
| 7 | Análisis y registro de interesados (maestro, matriz poder/interés y estrategia, estereotipos) | – | C | C | C | A/R | – | I | – | – | I | – | R | – | – | – | pm-interesados |
| 7a | Preferencias de comunicación (propuestas desde entrevistas y actas; confirmar o rechazar) | – | – | – | – | A/R | – | – | – | – | I | – | R | – | R | – | pm-interesados (pm-reuniones paso 7b) |
| 7b | Matriz RACI ligada a WBS, requisitos, épicas, historias, KR y decisiones | – | C | C | C | A/R | C | C | – | I | I | – | R | C | R | – | pm-interesados |
| | **Iniciación (IP)** | | | | | | | | | | | | | | | | |
| 8 | Enfoques de gestión y planes subsidiarios | I | A | C | C | R | – | C | I | C | I | – | R | – | – | – | pm-enfoques-gestion |
| 9 | PID y acta de constitución | I | A | C | C | R | – | C | – | I | I | R | R | – | – | – | pm-acta-constitucion |
| 10 | Descripción del producto del proyecto y descripciones de producto | – | C | A | C | R | C | C | – | C | I | – | – | R | – | – | pm-planificacion-por-productos, pm-calidad |
| 11 | PBS/WBS | – | A | C | C | R | C | I | – | I | I | – | – | R | – | – | pm-planificacion-por-productos, pm-visuales |
| 12 | Requisitos sin BMAD (`requisitos.md`, RTM) | – | I | A | C | R | C | C | – | – | I | – | – | R | – | – | pm-planificacion-por-productos |
| 13 | PRD y especificación con BMAD | – | I | A | C | C | C | – | – | R | I | – | – | C | I | – | flujos de BMAD (pm-bmad-puente solo lee) |
| 14 | Estimación y cronograma | – | A | I | C | R | C | – | – | – | I | – | – | R | – | – | pm-cronograma-estimacion |
| 15 | Presupuesto (BAC, contingencia, reserva de gestión) | C | A | I | C | R | – | I | – | – | I | – | – | R | – | – | pm-costos-presupuesto |
| 16 | Plan de proyecto | I | A | C | C | R | – | C | – | – | I | C | – | R | – | – | pm-plan-etapa-y-limites |
| 17 | Plan de etapa (1 = iniciación; 2…n) | – | A | C | C | R | C | C | – | – | I | – | R | R | – | – | pm-plan-etapa-y-limites, pm-agil-hibrido |
| 18 | Tolerancias de etapa | I | A | C | C | R | – | C | – | – | I | R | – | R | – | – | pm-plan-etapa-y-limites, pm-direccion-decisiones, pm-estado-proyecto |
| 19 | Backlog, release plan y swaps del PO dentro de tolerancia | – | I | C | – | C | A | – | – | I | I | – | – | R | R | – | pm-agil-hibrido |
| 20 | Adquisiciones (estrategia, adjudicación, contratos) | C | A | C | C | R | – | C | – | – | I | – | R | R | R | R | pm-adquisiciones |
| | **Especificación BMAD ↔ gobierno** | | | | | | | | | | | | | | | | |
| 21 | Línea base de especificación BMAD | – | A | C | – | I | – | C | – | I | I | R | – | C | – | – | pm-bmad-puente (`linea-base`), pm-direccion-decisiones |
| 22 | Sincronización BMAD → gobierno (backlog, avance, verificar) | – | – | – | – | A | C | – | I | I | I | C | – | R | R | R | pm-bmad-puente, pm-sync |
| 23 | Traspaso gobierno → BMAD (handoff) y su aplicación | – | I | C | – | A | C | – | – | R | I | – | – | R | R | – | pm-bmad-puente, pm-issues-cambios, pm-agil-hibrido |
| | **Control de etapa y entrega (CS, MP)** | | | | | | | | | | | | | | | | |
| 24 | Paquetes de trabajo (autorizar, aceptar, recibir) | – | – | I | C | A | R | C | – | – | I | – | – | – | R | – | pm-paquetes-trabajo |
| 25 | Checkpoint report | – | – | – | – | I | A/R | – | – | – | – | – | – | – | R | – | pm-progreso-reportes, pm-paquetes-trabajo |
| 26 | Highlight report | – | I | I | I | A/R | C | C | – | – | I | I | – | – | R | – | pm-progreso-reportes, pm-reporte |
| 27 | Registros genéricos (supuestos, acciones, decisiones operativas, diario) | – | – | – | – | A | C | – | R | – | I | – | R | – | R | R | pm-registros |
| 28 | Riesgos (identificar, evaluar, responder, monitorear)⁵ | – | C | C | C | A | C | C | I | C | I | – | R | R | R | – | pm-riesgos |
| 29 | Issues (captura y evaluación) | – | I | C | C | A | C | I | I | – | I | – | – | – | R | – | pm-issues-cambios, pm-registros |
| 30 | Solicitudes de cambio y concesiones (decisión)¹ | I | A | C | C | R | C | C | – | C | R | R | – | – | R | – | pm-issues-cambios, pm-direccion-decisiones |
| 31 | Informe de excepción | I | I | I | I | A/R | – | C | – | – | I | C | – | – | R | – | pm-issues-cambios (plantilla), pm-progreso-reportes (detección) |
| 32 | Plan de excepción² | C | A | C | C | R | – | C | – | – | I | R | – | R | – | – | pm-plan-etapa-y-limites |
| 33 | Calidad (registro, revisiones, auditoría, DoD) | – | – | C | C | A | R | C | R | – | I | – | – | – | R | – | pm-calidad |
| 34 | Aceptación de productos (intermedios y final) | – | C | A | C | R | C | C | – | – | I | R | – | – | R | R | pm-calidad, pm-cierre-proyecto |
| 35 | Matriz de comunicaciones | – | A | C | C | R | – | C | I | – | I | – | R | – | R | – | pm-comunicacion-stakeholders |
| 36 | Comunicados y escrituras externas³ | I | C | I | I | A | I | – | – | – | R | R | R | R | R | R | pm-comunicacion-stakeholders, pm-integraciones |
| 36a | Envío personalizado por la capa de canales (plan de envío, aprobación del mensaje, envío, registro en `envios.csv`)³ | – | C | – | – | A | – | – | I | – | R | – | – | – | R | R | pm-comunicacion-stakeholders, pm-interesados (`plan-envio`), pm-integraciones (`envios.py`) |
| 37 | Reuniones, actas y cargas a registros⁴ | – | I | C | C | A | C | I | R | – | I | – | – | – | R | R | pm-reuniones |
| 38 | Tablero de avance y visuales | – | I | I | I | A | I | – | – | – | I | – | – | R | R | – | pm-visuales |
| 39 | Sanidad (sanity check) | – | – | – | – | A | – | C | R | – | R | R | – | – | R | – | pm-sanidad |
| | **Puertas (las decide la junta; registra pm-director)** | | | | | | | | | | | | | | | | |
| 40 | Puerta `autorizar-inicio` | I | A | C | C | R | – | C | I | I | R | R | R | C | – | – | pm-puerta, pm-direccion-decisiones, pm-exportar |
| 41 | Puerta `autorizar-proyecto` | I | A | C | C | R | – | C | I | C | R | R | R | R | – | – | pm-puerta, pm-direccion-decisiones, pm-exportar |
| 42 | Puerta `autorizar-etapa` | I | A | C | C | R | C | C | I | C | R | R | – | R | R | – | pm-puerta, pm-direccion-decisiones, pm-plan-etapa-y-limites |
| 43 | Puerta `autorizar-plan-excepcion`² | C | A | C | C | R | – | C | I | – | R | R | – | R | C | – | pm-puerta, pm-direccion-decisiones |
| 44 | Puerta `decision-ad-hoc` (excepción, cambio sobre autoridad delegada, consejo)² | C | A | C | C | R | – | C | I | I | R | R | – | – | R | – | pm-direccion-decisiones |
| 45 | Puerta `autorizar-cierre` | C | A | C | C | R | – | C | I | I | R | R | – | – | – | R | pm-puerta, pm-direccion-decisiones, pm-cierre-proyecto |
| | **Límite de etapa y cierre (SB, CP)** | | | | | | | | | | | | | | | | |
| 46 | Informe de fin de etapa | – | I | I | I | A/R | C | C | – | – | I | I | – | R | R | – | pm-plan-etapa-y-limites, pm-progreso-reportes |
| 47 | Lecciones (registro, taller de etapa, informe, propuesta a la organización) | I | C | C | C | A | C | C | I | – | I | – | R | – | R | R | pm-lecciones-aprendidas |
| 48 | Cierre: handover, recomendaciones, informe de fin de proyecto | I | C | C | C | A/R | – | C | I | – | I | – | – | – | – | R | pm-cierre-proyecto |
| 49 | Plan y revisiones de beneficios | R | A | R | – | R | – | C | – | – | I | C | – | – | – | R | pm-caso-de-negocio, pm-cierre-proyecto, pm-okr |

**Cómo se leen algunas filas.**
- **Fila 3:** el ejecutivo rinde cuentas del business case; el usuario sénior aporta los beneficios y el proveedor sénior los costos. pm-director lo consulta en cada puerta (justificación continua) y pm-cierre produce la versión final.
- **Fila 5:** las tolerancias de proyecto las fija la capa de negocio. pm-inicio puede ejecutar `estado.py tolerancia --nivel proyecto` después de esa decisión (pm-caso-de-negocio paso 7, pm-enfoques-gestion paso 11); pm-planificacion tiene prohibido `tolerancia`.
- **Filas 7, 7a y 7b:** el gestor revisa las valoraciones de poder, interés y actitud, confirma o rechaza cada preferencia propuesta (`interesados.py confirmar|rechazar --por`) y responde por la RACI; pm-inicio la arma en SU e IP y pm-control la mantiene y propone preferencias desde las actas. Dentro de la RACI de un elemento, el A de una decisión de la junta es un rol de la junta (pm-interesados regla 3).
- **Fila 19:** el PO intercambia ítems dentro de la tolerancia de alcance sin solicitud de cambio (`decisiones.csv`, `nivel=product-owner`). Lo que desplaza un Must o excede la tolerancia pasa a la fila 30.
- **Fila 23:** el gestor rinde cuentas de que cada decisión aprobada llegue a BMAD como traspaso; el equipo BMAD lo aplica con sus propios flujos y lo confirma. Después, `verificar` limpio y nueva línea base (fila 21).
- **Fila 24:** el gestor autoriza el paquete y lo recibe; el jefe de equipo lo acepta, lo ejecuta y notifica. Sin el acto de autorización y aceptación, el trabajo no empieza.
- **Fila 30:** el orquestador presenta la decisión; pm-control registra la decisión de la autoridad delegada en `issues.csv`, `cambios.csv` y `decisiones.csv`; si decide la junta, pm-director registra `decision-ad-hoc`.
- **Fila 36a:** el gestor aprueba cada mensaje (`envios.py aprobar --por "Gestor: …"`) y el orquestador pide la confirmación del envío; el agente ejecuta `enviar --confirmar` (sin `--confirmar` solo simula) o, por MCP, `preparar-mcp` → envío tras vista previa → `registrar`. Los destinatarios salen siempre del maestro de interesados. Nota ³: si el destinatario es la capa de negocio o un tercero externo, confirma el ejecutivo.
- **Fila 49:** las revisiones de beneficios posteriores al cierre las ejecuta el negocio, no el proyecto; el usuario sénior rinde cuentas de la realización de beneficios también después del cierre, y el ejecutivo del plan.

## 4. Matriz compacta skills × humanos: decisiones sensibles

Solo las decisiones que cambian líneas base, comprometen dinero, salen del proyecto o afectan a personas. En todas, el agente prepara y el humano decide; la última columna dice qué script deja la constancia y qué agente lo ejecuta **después** de la decisión.

| Decisión | Skill que la prepara | CN | EJ | US | PS | GP | JE/PO | AS | Registro tras la decisión (script · agente) |
|---|---|---|---|---|---|---|---|---|---|
| Nivel de formalidad del método | pm-mandato-y-brief, pm-orquestador | – | I | – | – | A | – | – | `registro.py agregar decisiones --campo nivel=gestor` · pm-inicio |
| Enfoque de entrega (predictivo, ágil, híbrido) | pm-mandato-y-brief | – | A | C | C | R | – | – | `estado.py set enfoque_entrega=…` + `decisiones.csv` · pm-inicio |
| Nombramientos de la junta y del equipo | pm-organizacion-roles | C | A | C | C | R | I | – | `estado.py rol …` + `decisiones.csv` (`nivel=junta`) · pm-inicio |
| Tolerancias de proyecto | pm-caso-de-negocio, pm-enfoques-gestion | A | C | C | C | C | – | C | `estado.py tolerancia --nivel proyecto` · pm-inicio o pm-director |
| Tolerancias de etapa | pm-plan-etapa-y-limites, pm-direccion-decisiones | I | A | C | C | R | – | C | `estado.py tolerancia --nivel etapa` · pm-director |
| Registrar cualquier puerta | pm-direccion-decisiones, pm-puerta | I/C² | A² | C | C | R | – | C | `estado.py puerta <tipo> --decision … --por "<rol: nombre>"` · pm-director |
| Aprobar un documento de gestión | skill dueña del documento | – | A* | C | C | R | – | C | `estado.py aprobar <clave> --por "<rol: nombre>"` · pm-director |
| Seguir con un ERROR de sanidad abierto | pm-sanidad, pm-puerta | – | A | C | C | R | – | C | `estado.py puerta … --condiciones "<ERROR aceptado>"` · pm-director |
| Saltar una puerta o forzar un registro | pm-orquestador, pm-direccion-decisiones | C | A | C | C | R | – | C | `--forzar` con motivo + `decisiones.csv` · pm-director |
| Línea base de PRD, arquitectura o épicas | pm-bmad-puente, pm-direccion-decisiones | – | A | C | – | I | – | C | `bmad.py linea-base <art> --version X.Y --por …` · pm-director |
| Solicitud de cambio o concesión¹ | pm-issues-cambios, pm-calidad | I | A¹ | C | C | R | C | C | `registro.py actualizar cambios\|issues` + `decisiones.csv` (`nivel=autoridad-cambio`) · pm-control; si decide la junta, `estado.py puerta decision-ad-hoc` · pm-director |
| Swap del PO dentro de la tolerancia de alcance | pm-agil-hibrido | – | I | C | – | I | A | – | `registro.py agregar decisiones --campo nivel=product-owner` · pm-planificacion o pm-control |
| Uso de la reserva de gestión | pm-costos-presupuesto, pm-issues-cambios | C² | A² | C | C | R | – | C | con la puerta o `decision-ad-hoc` · pm-director |
| Escala P×I y presupuesto de riesgo⁵ | pm-riesgos | – | A | C | C | R | – | C | `estado.py aprobar evaluacion-probabilidad-impacto` · pm-director; uso del presupuesto en `decisiones.csv` · pm-control |
| Qué hacer ante una excepción² | pm-progreso-reportes, pm-issues-cambios, pm-direccion-decisiones | C² | A² | C | C | R | – | C | `estado.py puerta decision-ad-hoc` y, si se pide plan, `estado.py limite-etapa --excepcion X-###` · pm-director |
| Autorizar y recibir un paquete de trabajo | pm-paquetes-trabajo | – | – | I | C | A | R | C | `registro.py agregar decisiones` (`nivel=equipo` al aceptar; `nivel=gestor` al recibir) · pm-control |
| Aceptación de un producto | pm-calidad | – | C | A | C | R | C | C | `estado.py aprobar aceptacion-<producto> --nivel …` · pm-director |
| Adjudicación, firma y cierre de un contrato | pm-adquisiciones | C | A | C | C | R | – | C | `registro.py agregar decisiones`; `estado.py aprobar cierre-contrato-<id>` · pm-director |
| Confirmar un acta y sus cargas a registros⁴ | pm-reuniones | – | – | C | C | A | C | I | `registro.py agregar acciones\|riesgos\|issues\|decisiones\|lecciones` · pm-control |
| Análisis de clima del equipo | pm-reuniones | – | – | – | – | A† | C | – | sin registro nominal; informe agregado y anonimizado · pm-control |
| Escritura externa (publicar, enviar, crear tickets)³ | pm-integraciones, pm-comunicacion-stakeholders | – | C³ | – | – | A | – | – | id externo en `notas` o `diario.md` · subagente de la fase |
| Aprobar y enviar un comunicado por la capa de canales³ | pm-comunicacion-stakeholders, pm-integraciones | – | C³ | – | – | A | – | – | `envios.py aprobar <carpeta> --por "<rol: nombre>"` y `enviar <carpeta> --modo … --confirmar` (o `registrar --modo mcp`) → `envios.csv` + `diario.md` · subagente de la fase |
| Confirmar o rechazar una preferencia de comunicación | pm-interesados | – | – | – | – | A | – | – | `interesados.py confirmar\|rechazar PF-… --por "<rol: nombre>"` · pm-inicio o pm-control |
| Compartir valoraciones de interesados fuera del equipo de gestión | pm-interesados | – | A | – | – | R | – | C | confirmación del ejecutivo antes de circular el análisis o un reporte `--restringido` (el único que incluye valoraciones) · pm-inicio o pm-control |
| Cambiar metas de OKR aprobadas | pm-okr | C | A | C | – | R | – | – | `registro.py agregar decisiones --campo nivel=junta` · pm-control o pm-director |
| Elevar lecciones a la organización | pm-lecciones-aprendidas | I | A | – | – | R | – | C | estado `accionada-organizacion` en `lecciones.csv` · pm-cierre o pm-control |
| Aceptación final del producto del proyecto | pm-cierre-proyecto | – | C | A | C | R | – | C | `estado.py aprobar registro-aceptacion --por "Usuario sénior: …; Ejecutivo: …"` · pm-director |
| Cierre del proyecto (planificado o prematuro) | pm-cierre-proyecto, pm-direccion-decisiones | C | A | C | C | R | – | C | `estado.py puerta autorizar-cierre`; prematuro: `estado.py cierre --prematuro` · pm-director |

\* El aprobador depende del documento: el ejecutivo para la mayoría de los productos de gestión (business case, PID, enfoques, matriz de comunicaciones, OKR); el usuario sénior para las descripciones de producto; el gestor para el highlight tras la confirmación de aseguramiento.
† El análisis de clima exige además el consentimiento explícito de los participantes; sin él, no se ejecuta. Nunca se perfilan personas.

## 5. Verificación de consistencia con agentes y skills

| Comprobación | Resultado | Fuente |
|---|---|---|
| Solo pm-director ejecuta `estado.py puerta` | Consistente. SPEC lo fija; los cuatro agentes de fase dicen "Nunca `estado.py puerta` ni `aprobar`"; pm-estado-proyecto regla 3; pm-puerta paso 5. | SPEC §1.10.4; `agents/*.md`; skills citadas |
| Las puertas se registran después de la decisión humana | Consistente. pm-director modo B exige la decisión explícita con rol y nombre que trae el orquestador; pm-orquestador pasos 8–9; pm-direccion-decisiones paso 6. | `agents/pm-director.md`; pm-orquestador; pm-direccion-decisiones |
| Ningún agente aprueba | Consistente en reglas. pm-direccion-decisiones regla 5: "nunca aprueba, rechaza ni condiciona en nombre de una persona". | pm-direccion-decisiones |
| Transiciones | `limite-etapa` lo ejecuta pm-control o pm-director; con `--excepcion`, solo pm-director. `cierre` lo ejecuta pm-cierre (o pm-director si es prematuro). Consistente. | SPEC §1.10.4; `agents/pm-control.md`; `agents/pm-cierre.md`; pm-plan-etapa-y-limites paso 9 |
| Tolerancias | Proyecto: la decide la capa de negocio; la registra pm-inicio o pm-director. Etapa: solo pm-director tras `autorizar-etapa`. pm-planificacion tiene prohibido `tolerancia`. Consistente. | SPEC §1.10.5; `agents/pm-planificacion.md`; pm-caso-de-negocio paso 7 |
| BMAD solo lectura | Consistente: pm-bmad-puente regla 3, SPEC §1.13 y el hook `guardian.py`, que niega escrituras de subagentes pm-* en carpetas de BMAD. | SPEC §1.13; `hooks/guardian.py` |
| Escrituras externas | Consistente: todas las skills las condicionan a vista previa y confirmación; desde un subagente se devuelven como decisión humana. La capa de canales lo impone en el script: sin `--confirmar` simula y solo envía mensajes aprobados con `aprobar --por`. | SPEC §1.12; pm-integraciones regla 2; `envios.py` |
| Interesados y preferencias | Consistente: valoraciones, preferencias y estereotipos sugeridos son borradores hasta que el gestor los confirma; las propuestas y vencidas no se aplican al perfil; la RACI exige un A por elemento (validado por `registro.py` y la sanidad STK-02). | pm-interesados reglas 2–3; SPEC §1.10.8 y §1.10.10 |

**Reglas de registro** (SPEC §1.10.4).
1. **`estado.py aprobar`**: nivel junta o capa de negocio → solo pm-director; nivel gestor, product owner o equipo (aceptación de paquetes de trabajo, revisiones de calidad, informes del gestor) → el agente de la fase, con `--nivel`, después de la confirmación humana que trae el orquestador. En el hilo principal o en Hermes lo ejecuta quien corre la skill, siempre tras la aprobación humana explícita.
2. **Nombramientos y cadencia ágil**: el ejecutivo confirma; pm-director registra `estado.py rol …` (incluido `product_owner`) y `estado.py agil cadencia_iteracion_dias=…`. pm-organizacion-roles y pm-agil-hibrido dicen lo mismo.
3. **`metadata.agente`** indica el dueño habitual de la skill, no el único invocador; la matriz refleja quién la invoca realmente.
