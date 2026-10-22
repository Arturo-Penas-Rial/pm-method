# Casos de uso de pm-method 2.4.0 · Worked examples

Un ejemplo trabajado por cada una de las 39 skills, incluidos los seis comandos, sobre un mismo proyecto de muestra para que los casos se encadenen de principio a fin. La parte 6 (casos 38 a 49) reúne las capacidades transversales: el maestro de interesados (`pm-interesados`), la comunicación personalizada enviada por la capa de canales, los OKR con check-ins, los riesgos candidatos desde cuatro fuentes, los controles permanentes (caso 48) y los mapas de Wardley y de recorrido del cliente (caso 49). La parte 7 (casos 50 a 59) remite, para cada capacidad de decisión y control continuo (opciones de respuesta, personas de usuario, radar, reuniones, impacto de cambios, tres valores y capacidad, datos del período, estado de productos, ciclo de las lecciones y expediente de auditoría), al paso de la guía E2E donde se recorre con salidas reales. Al final hay tres variantes cortas: predictivo sin BMAD, ágil en inglés y un proyecto con Jira y Teams conectados.

Los datos del proyecto de muestra (personas, montos, fechas, ids) siguen el caso de punta a punta con el que se probó la versión 2: las cifras de los ejemplos coinciden con lo que devolvieron los scripts en esa prueba. Los casos de la parte 6 usan, en cambio, la corrida de referencia de la guía [E2E-3](guias/E2E-3-interesados-okr-avance.md) (mismo portal y mismas personas, con diez interesados ST-001…ST-010): sus ids y cifras salen de [salida-g3.md](guias/evidencia/salida-g3.md) y no continúan la numeración de las partes 1 a 5 (el caso 48 toma además salidas de las guías E2E-2 y E2E-4, y el caso 49, de la variante con BMAD de la guía E2E-5, cada una con su propia carpeta y numeración). Las personas y la cooperativa son ficticias. Las respuestas humanas son simuladas.

## Proyecto de muestra

| Dato | Valor |
|---|---|
| Proyecto | Portal de autoservicio para socios de una cooperativa de ahorro y crédito |
| Mandato | 7 meses (oct-2026 → may-2027), USD 180.000, desarrollo con proveedor externo |
| Enfoque de entrega | híbrido: etapas PRINCE2 con sprints de 14 días dentro de las etapas de entrega |
| Especificación | BMAD v6 en el mismo repositorio (`_bmad/`, `_bmad-output/`): brief de producto, PRD con FR-1…FR-4, NFR-1, UJ-1, SM-1, arquitectura con AD-1 y AD-2, épicas e historias |
| Etapas | 0 = SU (pre-proyecto) · 1 = Iniciación · 2 = "Release 1" · 3 = "Release 2 y transición" |
| Capa de negocio | Consejo directivo de la cooperativa |
| Ejecutivo | Laura Méndez (gerenta de operaciones) |
| Usuario sénior, product owner y autoridad de cambio | Sofía Ramírez |
| Proveedor sénior | Diego Ferreira (proveedor de desarrollo) |
| Gestor del proyecto | Martín Suárez |
| Jefa de equipo | Lucía Benítez (equipo del proveedor) |
| Aseguramiento | Andrea Costa |
| Equipo BMAD | analista y PM de producto del proveedor (corren los flujos de BMAD) |

**Convenciones de los comandos.** Se trabaja desde la raíz del repositorio `portal-socios/`, con la carpeta del proyecto en `portal-socios/gestion/` (fuera de las carpetas de BMAD). En el plugin las rutas de scripts parten de `${CLAUDE_PLUGIN_ROOT}/skills`; para abreviar:

```bash
PM="${CLAUDE_PLUGIN_ROOT}/skills"          # manual: ~/.claude/skills · Hermes: ~/.hermes/skills
E="$PM/pm-estado-proyecto/scripts"         # estado.py, registro.py, especificacion.py, sanidad.py, wbs.py, cpm.py, evm.py, exportar.py
B="$PM/pm-bmad-puente/scripts/bmad.py"
X="$PM/pm-exportar/scripts/paquete.py"
O="$PM/pm-okr/scripts/okr.py"
T="$PM/pm-reuniones/scripts/transcripcion.py"
I="$PM/pm-interesados/scripts/interesados.py"   # maestro de interesados
V="$PM/pm-integraciones/scripts/envios.py"      # capa de canales
R="$PM/pm-riesgos/scripts/riesgos.py"           # riesgos candidatos desde cuatro fuentes
```

Los scripts que reciben la carpeta (incluidos `interesados.py` y `envios.py`) usan `--proyecto gestion` y resuelven las rutas internas contra ella. Los que reciben un archivo (`wbs.py`, `cpm.py`, `okr.py`, `transcripcion.py`) llevan la ruta desde la raíz del repositorio.

**Cómo leer cada caso.** *Prompt del usuario*: el mensaje o los mensajes, en lenguaje natural, que escribe la persona; cuando hay un comando de barra equivalente, figura como "Atajo". *Respuestas del usuario*: lo que contesta la persona a las preguntas del orquestador, con nombre y rol cuando es una decisión (solo aparece si el sistema pregunta). *Quién*: la cadena orquestador → subagente → skill. *Qué pregunta o verifica*: lo que la skill comprueba antes de producir y lo que pregunta (siempre a través del orquestador, porque los subagentes no preguntan). *Comandos*: los ejecuta el sistema por detrás; el usuario no los escribe. *Entradas*: qué información o archivos aporta el usuario y cómo llegan (en el prompt, respondiendo al orquestador, un archivo en una ruta de la carpeta del proyecto o adjunto en la sesión, BMAD leído por la fachada en solo lectura, o un conector MCP). *Salidas*: qué queda, con su ruta dentro de `gestion/`, su id y su estado, y cómo lo verifica el usuario (abrir el archivo, abrir el CSV en un editor o Excel, mirar un campo de `estado.json` o escribir un prompt de verificación). *Decisión humana*: quién decide y quién registra después.

Para probar un caso como usuario: abrí `claude` en la raíz del repositorio del producto y escribí los prompts en orden; los comandos son la referencia de lo que el sistema ejecuta por detrás.

Regla que atraviesa todos los casos: cuando un subagente necesita una decisión, la devuelve en su bloque "Retorno al orquestador / Return"; el orquestador se la presenta a la persona con el rol que decide; con la respuesta explícita (nombre y rol), el orquestador invoca a `pm-director`, que es el único agente que ejecuta `estado.py puerta` y `estado.py aprobar`.

---

## Parte 1 · Puesta en marcha (SU, etapa 0)

### 1. `/pm-ayuda` — orientarse antes de empezar
- **Prompt del usuario:** "Explicame cómo funcionan las puertas de decisión del método."
  Atajo: `/pm-method:pm-ayuda puertas`
- **Quién:** orquestador en el hilo principal ejecuta la skill-comando `pm-ayuda`. Sin subagente.
- **Qué pregunta o verifica:** filtra la ayuda al tema pedido (`$ARGUMENTS` = `puertas`). Busca `estado.json`; como todavía no hay proyecto, no agrega el siguiente paso.
- **Comandos:** ninguno (con proyecto, agregaría `python3 $E/estado.py --proyecto gestion siguiente`).
- **Entradas (qué aporta el usuario y cómo):** ninguna más allá del tema, escrito en el prompt. Como todavía no hay proyecto, no lee `estado.json`.
- **Salidas (qué queda y dónde verificarlo):** ninguna: no queda nada escrito. Respuesta en pantalla con el ciclo SU → `autorizar-inicio` → IP → `autorizar-proyecto` + `autorizar-etapa` → etapas 2…n → `autorizar-cierre`, y la aclaración de que solo pm-director registra puertas. Se verifica leyendo la respuesta en la conversación.
- **Decisión humana:** ninguna.

### 2. `/pm-nuevo` — crear la carpeta del proyecto
- **Prompt del usuario:** "Creá el proyecto “Portal de autoservicio para socios” en la carpeta ./gestion, en español y con enfoque híbrido. La ejecutiva es Laura Méndez y el gestor Martín Suárez."
  Atajo: `/pm-method:pm-nuevo "Portal de autoservicio para socios" ./gestion es hibrido`, con la ejecutiva y el gestor en el mismo mensaje.
- **Quién:** orquestador → skill-comando `pm-nuevo`, que usa los scripts de pm-estado-proyecto y pm-bmad-puente.
- **Qué pregunta o verifica:** que `gestion/` no tenga ya un `estado.json` (no sobrescribe); que haya BMAD en la carpeta o en una superior (`_bmad/`, `_bmad-output/` o `.bmad-core/`); que la carpeta del proyecto quede fuera de las de BMAD.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/nuevo_proyecto.py --ruta gestion --nombre "Portal de autoservicio para socios" \
      --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez"
  python3 $B --proyecto gestion detectar
  python3 $E/estado.py --proyecto gestion integracion especificacion=bmad
  python3 $E/estado.py --proyecto gestion siguiente
  ```
- **Entradas (qué aporta el usuario y cómo):** nombre, carpeta, idioma, enfoque, ejecutiva y gestor, escritos en el prompt. Las carpetas de BMAD del repositorio (`_bmad/`, `_bmad-output/`) las detecta el puente en solo lectura; el usuario no las mueve ni las copia.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/estado.json`: `fase` = `pre-proyecto`, `proceso_actual` = `SU`, `etapa_actual.numero` = 0, `roles.ejecutivo` y `roles.gestor_proyecto` cargados, `integraciones.especificacion` = `bmad` e `integraciones.bmad` con layout v6. En la prueba el soporte salió `version-no-visible`: el script avisa que trabaja por patrones.
  - Los nueve CSV de `gestion/03-control/registros/` (riesgos, issues, cambios, decisiones, supuestos, lecciones, stakeholders, calidad, acciones), vacíos, y `gestion/03-control/registros/diario.md`.
  - Cómo verificarlo: abrir `gestion/estado.json`; listar `gestion/03-control/registros/`; o escribir "¿Dónde estamos?" (atajo `/pm-method:pm-estado`), que debe mostrar SU, etapa 0.
- **Decisión humana:** ninguna. El comando ofrece seguir con pm-mandato-y-brief.

### 3. `pm-orquestador` — "¿por dónde empiezo?"
- **Prompt del usuario:** "Quiero gestionar el portal de socios con el método; ¿por dónde empiezo?"
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Sí, tengo el correo del consejo; te lo paso en el próximo mensaje."
  2. Martín Suárez, gestor: "Estoy de acuerdo con la secuencia; arrancá por el mandato y el brief."
- **Quién:** orquestador (hilo principal; también `claude --agent pm-method:pm-orquestador`).
- **Qué pregunta o verifica:** corre la sanidad rápida, lee el estado y resume en tres líneas: SU, etapa 0, sin tolerancias ni puertas; enfoque híbrido; especificación BMAD. Clasifica la petición como SU y muestra la secuencia: pm-inicio con pm-mandato-y-brief, pm-organizacion-roles, pm-interesados, pm-caso-de-negocio, pm-riesgos y pm-plan-etapa-y-limites → 🔒 `autorizar-inicio` (decide la ejecutiva). Hace una sola pregunta: "¿Tenés el correo o el acta del consejo con el pedido?".
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/sanidad.py --proyecto gestion --rapido
  python3 $E/estado.py --proyecto gestion ver
  python3 $E/estado.py --proyecto gestion siguiente
  ```
- **Entradas (qué aporta el usuario y cómo):** solo el prompt. El correo o el acta del consejo que pide el orquestador llega en el caso 4 (pegado en el mensaje o adjunto en la sesión).
- **Salidas (qué queda y dónde verificarlo):** ninguna en disco: el plan de secuencia queda en la respuesta. Al delegar usa la plantilla de encargo (guía §2): carpeta, objetivo, skills, datos confirmados, restricciones (no registrar puertas, no escribir afuera, BMAD solo lectura) y exigencia del bloque de retorno. Se verifica en la conversación; el estado no cambia (`/pm-method:pm-estado` sigue mostrando SU, etapa 0).
- **Decisión humana:** conformidad del gestor con la secuencia antes de ejecutarla.

### 4. `pm-mandato-y-brief` — mandato y project brief
- **Prompt del usuario:** "Convertí este correo del consejo en mandato y armá el brief. El brief de producto ya está en BMAD: usalo sin copiarlo." (con el texto del correo pegado debajo, o el archivo adjunto en la sesión)
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Formalidad mínima."
  2. Laura Méndez, ejecutiva: "Confirmo el enfoque híbrido."
- **Quién:** orquestador → `pm-inicio` → `pm-mandato-y-brief`.
- **Qué pregunta o verifica:** fase `pre-proyecto`; ejecutivo prospectivo presente (sin él el proyecto no sigue); lecciones previas (busca en proyectos anteriores); nivel de formalidad con la tabla de la guía §1; enfoque de entrega puntuando criterios (los entregables puntúan distinto → híbrido) y ruta de planificación BMAD. Lee el brief de producto solo por la fachada y toma ruta y sha con el inventario.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion ver
  python3 $E/especificacion.py --proyecto gestion fuente
  python3 $B --proyecto gestion inventario          # brief final, sha 42fc69b23dbb
  python3 $E/registro.py --proyecto gestion agregar lecciones \
      --campo situacion="Portal anterior sin entorno de pruebas del core bancario" \
      --campo efecto="Dos semanas de atraso en integración" \
      --campo recomendacion="Exigir entorno de pruebas del core antes del primer sprint" \
      --campo prioridad=alta --campo responsable_seguimiento="Martín Suárez"
  # tras las dos puertas humanas (segunda delegación):
  python3 $E/registro.py --proyecto gestion agregar decisiones --campo decision="Formalidad mínima" \
      --campo decidido_por="Gestor: Martín Suárez" --campo nivel=gestor
  python3 $E/estado.py --proyecto gestion set enfoque_entrega=hibrido
  python3 $E/estado.py --proyecto gestion artefacto mandato --ruta 00-direccion/mandato.md --estado borrador --version 0.1
  python3 $E/estado.py --proyecto gestion artefacto project-brief --ruta 01-inicio/project-brief.md --estado borrador --version 0.1
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Correo del consejo: pegado en el mismo prompt o adjunto en la sesión. Si hubiera correo o documentos conectados, se lee vía pm-integraciones (ningún conector es obligatorio).
  - Brief de producto: leído de BMAD por la fachada (solo lectura); ruta y sha (42fc69b23dbb) salen del inventario del puente.
  - Lección previa del portal anterior: la skill la busca en proyectos anteriores; si no está registrada en ningún lado, el usuario la cuenta en el chat.
  - Nivel de formalidad y enfoque de entrega: respuestas del gestor y de la ejecutiva a las preguntas del orquestador.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/00-direccion/mandato.md` (`borrador`, v0.1; clave `artefactos.mandato` en `gestion/estado.json`).
  - `gestion/01-inicio/project-brief.md` (`borrador`, v0.1; `artefactos.project-brief`): problema, usuarios y visión referenciados al brief de producto por ruta y sha corto.
  - L-001 en `gestion/03-control/registros/lecciones.csv`.
  - D-001 (formalidad, nivel `gestor`) y D-002 (enfoque, nivel `junta`) en `gestion/03-control/registros/decisiones.csv`; `enfoque_entrega` = `hibrido` en `gestion/estado.json`.
  - Cómo verificarlo: abrir los dos Markdown; abrir `decisiones.csv` y `lecciones.csv` en un editor o Excel (solo para leer: los cambios van siempre por el sistema); o escribir "Mostrame las decisiones registradas".
- **Decisión humana:** el primer retorno trae dos preguntas: nivel de formalidad (decide el gestor) y enfoque de entrega (decide la ejecutiva). El orquestador las presenta, Martín elige "mínimo" y Laura confirma "híbrido", y se vuelve a delegar con las respuestas.

### 5. `pm-organizacion-roles` — junta y roles (los interesados, con pm-interesados)
- **Prompt del usuario:** "Diseñá la junta: Laura patrocina, Sofía representa a los socios y será la PO, el desarrollo lo hace un proveedor con Diego como proveedor sénior, Andrea hace aseguramiento y Lucía lidera el equipo del proveedor." Y, para los interesados: "Registrá a los interesados con su poder, interés y actitud."
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva: "Confirmo el diseño de la junta y los nombramientos."
  2. Martín Suárez, gestor: "Revisé las actitudes de los interesados; guardalas así."
- **Quién:** orquestador → `pm-inicio` → `pm-organizacion-roles` (junta, roles, descripciones de rol, team charter). Los interesados y la RACI son de `pm-interesados` (maestro de interesados), que el mismo subagente invoca a continuación (casos 38 a 43).
- **Qué pregunta o verifica:** un solo ejecutivo distinto del gestor; los tres intereses en la junta; aseguramiento fuera del gestor, los equipos y el soporte; sin responsabilidades huérfanas. Mapea roles ágiles y BMAD (el PM de BMAD no es el gestor del proyecto; la PO es la usuaria sénior). Detecta que el rol de soporte no tiene titular y lo deja `[por confirmar]`. Para los interesados, `pm-interesados` pide poder e interés de cada uno (sin ellos no se ubican en la matriz: aviso STK-01) y deja las valoraciones como de circulación restringida.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe. Se corren después de la confirmación de la ejecutiva.
  ```bash
  python3 $E/estado.py --proyecto gestion rol ejecutivo="Laura Méndez" gestor_proyecto="Martín Suárez" \
      usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" aseguramiento="Andrea Costa" \
      autoridad_cambio="Sofía Ramírez" product_owner="Sofía Ramírez" jefes_equipo="Lucía Benítez"
  python3 $E/estado.py --proyecto gestion agil cadencia_iteracion_dias=14 velocidad_referencia=30
  # pm-interesados (maestro de interesados):
  python3 $E/registro.py --proyecto gestion agregar stakeholders --campo nombre="Consejo directivo" \
      --campo poder=alto --campo interes=medio --campo actitud=partidario --campo confidencial=no
  python3 $I --proyecto gestion matriz
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Personas y roles: escritos en el prompt.
  - Actitudes de los interesados: las revisa el gestor antes de guardarlas (respuesta al orquestador).
  - Cadencia de 14 días: dato del proyecto (sprints de 14 días). Velocidad de referencia 30: no figura en el prompt; el usuario la informa al orquestador **[verificar]** (el caso no dice de dónde sale).
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/00-direccion/estructura-organizativa.md` (organigrama Mermaid), de `pm-organizacion-roles`.
  - `gestion/01-inicio/analisis-stakeholders.md` (circulación restringida) y `gestion/02-planificacion/plan-compromiso-stakeholders.md` (cuatro brechas con acción): sus plantillas son de `pm-interesados`.
  - `gestion/03-control/registros/stakeholders.csv` con seis interesados (ST-004 con `confidencial=si`); `interesados.py matriz` muestra en la respuesta el cuadrante de cada uno con su estrategia (ejemplo completo en el caso 38).
  - `gestion/estado.json`: `roles` con los nombramientos (el rol de soporte queda `[por confirmar]`) y `agil.cadencia_iteracion_dias` = 14, `agil.velocidad_referencia` = 30; la decisión de la ejecutiva, nivel `junta`, en `gestion/03-control/registros/decisiones.csv`.
  - Cómo verificarlo: abrir los tres Markdown (el análisis es de circulación restringida); abrir `stakeholders.csv` en un editor o Excel; o escribir "Mostrame la junta y los roles registrados".
- **Decisión humana:** dos puertas internas: Laura confirma diseño y nombramientos (decisión nivel `junta`) y Martín revisa las actitudes antes de guardarlas.

### 6. `pm-estado-proyecto` — tolerancias de proyecto
- **Prompt del usuario:** "Fijá las tolerancias de proyecto que aprobó el consejo: más o menos 3 semanas, más o menos 8 % de costo y hasta 10 % menos de beneficios. ¿Qué falta para la puerta?"
- **Quién:** orquestador → `pm-inicio` → `pm-estado-proyecto`.
- **Qué pregunta o verifica:** que la decisión venga de la capa de negocio (el usuario cita el acta del consejo); que tiempo y costo estén presentes (mínimo obligatorio); que sean de nivel proyecto (las de etapa las fija la junta en cada `autorizar-etapa`).
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion tolerancia --nivel proyecto tiempo="±3 semanas" costo="±8 %" beneficios="-10 %"
  python3 $E/estado.py --proyecto gestion siguiente
  ```
- **Entradas (qué aporta el usuario y cómo):** las tres tolerancias, escritas en el prompt citando el acta del consejo (capa de negocio); el acta puede adjuntarse en la sesión. Sin acta, el subagente la devuelve como dato faltante.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/estado.json` → `tolerancias.proyecto`: `tiempo` = "±3 semanas", `costo` = "±8 %", `beneficios` = "-10 %".
  - `siguiente` lista en la respuesta lo que falta para `autorizar-inicio` (no se escribe en disco).
  - Cómo verificarlo: abrir `gestion/estado.json`; o escribir "¿Qué tolerancias tiene el proyecto?" (atajo `/pm-method:pm-estado`).
- **Decisión humana:** ya tomada por el consejo (capa de negocio); el script solo la registra. Si no hubiera acta, el subagente la devolvería como dato faltante.

### 7. `pm-caso-de-negocio` — business case esquemático
- **Prompt del usuario:** "Armá el business case de una página a partir del mandato; todavía no tenemos costos firmes del proveedor."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "No tenemos tasa de descuento de la organización; dejala por confirmar a cargo de Laura."
- **Quién:** orquestador → `pm-inicio` → `pm-caso-de-negocio` (modo `esquematico`).
- **Qué pregunta o verifica:** cadena de valor (salida → capacidad → resultado → beneficio → objetivo de negocio); tres opciones empezando por "no hacer nada distinto"; cada beneficio medible con línea base, dueño, fecha y tolerancia. La tasa de descuento no la dio la organización: queda `[por confirmar]` a cargo de la ejecutiva. Lee SM-1 por la fachada y lo cita sin copiarlo.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion consultar SM-1
  python3 $E/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision --version 0.9
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Mandato: ya está en `gestion/00-direccion/mandato.md` (caso 4).
  - SM-1: leído de BMAD por la fachada, citado sin copiar.
  - Tasa de descuento: la pregunta el orquestador una vez; sin dato, queda `[por confirmar]`.
  - Falta de costos firmes del proveedor: dicho en el prompt.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/00-direccion/business-case.md` (`en-revision`, v0.9; `artefactos.business-case`): OBJ-1; B-01 (porcentaje de trámites por el portal, de 0 a 40 %, Refs SM-1 · KR-1.1), B-02 (NPS de 22 a 35, Refs KR-1.2), des-beneficio DB-01; payback ≈ 1,9 años con supuestos declarados; tasa de descuento `[por confirmar]`.
  - Cómo verificarlo: abrir el archivo; mirar `artefactos.business-case` en `gestion/estado.json`; o escribir "Mostrame los beneficios del business case".
- **Decisión humana:** la junta lo decide en `autorizar-inicio` (versión esquemática) y en `autorizar-proyecto` (versión 1.0); registra pm-director.

### 8. `pm-okr` — OKR ligados a beneficios
- **Prompt del usuario:** "El consejo trabaja con OKR: armá los del proyecto a partir de los beneficios."
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva: "Acepto el objetivo O-1 y los tres KR."
- **Quién:** orquestador → `pm-inicio` → `pm-okr`.
- **Qué pregunta o verifica:** que el business case tenga OBJ-n y B-nn numerados (si no, propone la numeración en el business case, no en el OKR); que cada KR cite un B-nn o un SM-n existente; que ningún KR sea una tarea.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion consultar SM-1
  python3 $O gestion/00-direccion/okr.csv --plantilla
  python3 $O gestion/00-direccion/okr.csv --corte 2026-10-17 --markdown gestion/03-control/reportes/2026-10-17-okr.md
  python3 $E/estado.py --proyecto gestion artefacto okr --ruta 00-direccion/okr.md --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Business case con OBJ-1, B-01 y B-02 numerados, ya en `gestion/00-direccion/business-case.md`.
  - SM-1: leído de BMAD por la fachada.
  - Mediciones: no hay todavía; nada que aportar.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/00-direccion/okr.csv` (O-1 → OBJ-1; KR-1.1 → B-01 + SM-1; KR-1.2 → B-02; KR-1.3 → B-01).
  - `gestion/00-direccion/okr.md` (`en-revision`; `artefactos.okr`, que pasa a `aprobado` con `aprobado_por` "Ejecutivo: Laura Méndez" tras la aceptación).
  - `gestion/03-control/reportes/2026-10-17-okr.md`: tabla puntuada. Sin avisos de vínculo; los tres KR salen en rojo porque todavía no hay medición, y el informe lo aclara.
  - Cómo verificarlo: abrir `okr.csv` en un editor o Excel y la tabla puntuada; mirar `artefactos.okr` en `gestion/estado.json`.
  - Este `okr.csv` mínimo es válido tal cual; los tipos de KR, el compromiso, el peso, las iniciativas, los check-ins y la salud son opcionales (caso 45).
- **Decisión humana:** la ejecutiva acepta objetivo y KR; con su respuesta, pm-director ejecuta `estado.py aprobar okr --por "Ejecutivo: Laura Méndez"`.

### 9. `pm-riesgos` — riesgos iniciales
- **Prompt del usuario:** "Hagamos los riesgos iniciales: el proveedor es nuevo para nosotros, el padrón de socios está desactualizado y dependemos de la API del core bancario."
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva: "Apruebo la escala de probabilidad e impacto propuesta."
  2. Diego Ferreira, proveedor sénior: "Acepto la respuesta de reducir para R-001; la ejecuta Lucía Benítez." (cada propietario confirma la suya del mismo modo)
- **Quién:** orquestador → `pm-inicio` → `pm-riesgos`.
- **Qué pregunta o verifica:** objetivos con unidades y tolerancias antes de identificar; escala P×I aprobada (todavía no hay enfoque de riesgo, así que redacta la evaluación P×I y deja las puntuaciones como propuesta); causa → evento → efecto; propietario y ejecutor por riesgo; AD-n y NFR del PRD como fuentes.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar requisitos      # AD-1, AD-2, NFR-1
  python3 $E/registro.py --proyecto gestion agregar riesgos --campo categoria=externo \
      --campo causa="La API del core bancario no tiene entorno de pruebas (AD-2)" \
      --campo evento="La integración se prueba tarde" --campo efecto="Atraso del release 1" \
      --campo tipo=amenaza --campo probabilidad=4 --campo impacto=4 --campo impacto_monetario=30000 \
      --campo propietario="Diego Ferreira" --campo ejecutor="Lucía Benítez" --campo respuesta=reducir
  python3 $E/registro.py --proyecto gestion resumen --json
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Las tres fuentes de riesgo: escritas en el prompt.
  - AD-1, AD-2 y NFR-1: leídos de BMAD por la fachada.
  - Impacto monetario, propietario y ejecutor de cada riesgo: si faltan, los pregunta el orquestador y el usuario los responde en el chat.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/03-control/registros/riesgos.csv` con R-001…R-005: R-001 puntuación 16 (alto) EMV 21.000; R-002 9, EMV 9.000; R-003 12, EMV 20.000; R-004 9, EMV 5.000; R-005 oportunidad 6, EMV 2.400. Resumen: un riesgo alto, ninguno sin respuesta ni propietario.
  - `gestion/02-planificacion/enfoques/evaluacion-probabilidad-impacto.md` como propuesta; tras la aprobación de la ejecutiva, `artefactos.evaluacion-probabilidad-impacto` en `aprobado`.
  - Cómo verificarlo: abrir `riesgos.csv` en un editor o Excel; o escribir "Mostrame el registro de riesgos abiertos".
- **Decisión humana:** la ejecutiva aprueba la escala (luego pm-director `estado.py aprobar evaluacion-probabilidad-impacto`); cada propietario acepta su respuesta.

### 10. `pm-registros` — supuesto y clasificación
- **Prompt del usuario:** "Registrá un supuesto: el padrón de socios estará disponible en marzo."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "La responsable es Sofía Ramírez."
- **Quién:** orquestador → `pm-control` (o directamente en el hilo principal en SU) → `pm-registros`.
- **Qué pregunta o verifica:** prueba de certeza (no ocurrió, no es riesgo todavía: es un supuesto); formal o informal (afecta el plan del release 2 → formal); responsable, que no se inventa: lo pide.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion esquema supuestos
  python3 $E/registro.py --proyecto gestion agregar supuestos \
      --campo supuesto_o_restriccion="El padrón de socios depurado estará disponible en marzo de 2027" \
      --campo tipo=supuesto --campo validado=pendiente --campo responsable="Sofía Ramírez"
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - El supuesto: escrito en el prompt.
  - Responsable: no se inventa; lo pregunta el orquestador y el usuario lo responde.
- **Salidas (qué queda y dónde verificarlo):**
  - Fila S-002 en `gestion/03-control/registros/supuestos.csv` (`tipo=supuesto`, `validado=pendiente`, estado `abierto`, responsable Sofía Ramírez). Si se hubiera usado una columna inexistente, `registro.py` la rechaza y lista las válidas; se corrige en lugar de forzar.
  - Cómo verificarlo: abrir `supuestos.csv` en un editor o Excel; o escribir "Mostrame los supuestos abiertos".
- **Decisión humana:** ninguna para el alta. Cerrar el supuesto (validado o invalidado) exige confirmación del gestor.

### 11. `/pm-puerta autorizar-inicio` — primera puerta
- **Prompt del usuario:** "Prepará la puerta para autorizar el inicio del proyecto."
  Atajo: `/pm-method:pm-puerta autorizar-inicio`
- **Respuestas del usuario:**
  1. Sofía Ramírez, autoridad de cambio: "Diferí “notificaciones” como Could."
  2. Laura Méndez, ejecutiva: "Apruebo autorizar el inicio; la iniciación termina el 6 de noviembre."
- **Quién:** orquestador → `pm-director` (modo A) → `pm-direccion-decisiones`, `pm-exportar`, `pm-bmad-puente`, `pm-sanidad`; luego orquestador → humano → `pm-director` (modo B).
- **Qué pregunta o verifica:** sanidad completa sin ERROR; obligatorios de la puerta presentes en `aprobado` o `en-revision`; cobertura de la especificación; desvíos de BMAD; traspasos pendientes. En la prueba, `verificar` encontró una Sprint Change Proposal previa: se registró como issue I-001 (`solicitud-cambio`), la autoridad de cambio difirió "notificaciones" como Could (D-003, nivel `autoridad-cambio`) y `verificar --marcar-vistas` dejó el desvío visto.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/sanidad.py --proyecto gestion --informe
  python3 $X --proyecto gestion listar puerta autorizar-inicio
  python3 $E/especificacion.py --proyecto gestion resumen
  python3 $B --proyecto gestion verificar
  # tras la decisión de la ejecutiva (pm-director, modo B):
  python3 $E/estado.py --proyecto gestion puerta autorizar-inicio --decision aprobado \
      --por "Ejecutivo: Laura Méndez" --fin 2026-11-06
  python3 $E/estado.py --proyecto gestion aprobar project-brief --por "Ejecutivo: Laura Méndez"
  python3 $E/estado.py --proyecto gestion aprobar plan-etapa-1 --por "Ejecutivo: Laura Méndez"
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: lee el estado del proyecto, los productos de la puerta y BMAD por el puente (solo lectura; ahí encuentra la Sprint Change Proposal previa). La decisión llega como respuesta de la ejecutiva, con nombre y rol.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/00-direccion/decisiones/2026-10-17-solicitud-autorizar-inicio.md` (`en-revision`).
  - I-001 (`solicitud-cambio`) en `gestion/03-control/registros/issues.csv` y D-003 (nivel `autoridad-cambio`) en `gestion/03-control/registros/decisiones.csv`.
  - Tras la decisión: D-004 en `decisiones.csv`; en `gestion/estado.json`, la puerta `autorizar-inicio` en `puertas[]`, `fase` = `inicio`, `proceso_actual` = `IP`, `etapa_actual` = 1 "Iniciación" con fin 2026-11-06, y `artefactos.project-brief` y `artefactos.plan-etapa-1` en `aprobado`.
  - Cómo verificarlo: abrir la solicitud; abrir `decisiones.csv` y `issues.csv`; o escribir "¿Dónde estamos?" (atajo `/pm-method:pm-estado`).
- **Decisión humana:** el orquestador presenta las opciones (aprobar, condicionar, rechazar, pedir información, cierre prematuro) y pide nombre y rol. Laura Méndez aprueba. Sin esa respuesta no se registra nada.

---

## Parte 2 · Iniciación (IP, etapa 1)

### 12. `pm-enfoques-gestion` — enfoques del PID
- **Prompt del usuario:** "Escribí los enfoques del PID en una página. Usamos BMAD: dejá claro cuándo un ajuste al PRD es elaboración y cuándo es solicitud de cambio."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Versión de una página para todos los enfoques."
- **Quién:** orquestador → `pm-inicio` → `pm-enfoques-gestion`.
- **Qué pregunta o verifica:** nivel de formalidad por enfoque; escalas iguales a las que acepta `registro.py`; tolerancias iguales a las de `estado.json`; integraciones conectadas (ninguna). En el enfoque de issues y cambios completa la sección 5.1: detallar un requisito sin cambiar ids es elaboración progresiva; agregar o retirar ids, cambiar la intención de un FR o de una SM-n o una Sprint Change Proposal es `solicitud-cambio`. Comunicación se escribe al final.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion esquema issues
  python3 $E/estado.py --proyecto gestion artefacto enfoque-issues-cambios \
      --ruta 02-planificacion/enfoques/enfoque-issues-cambios.md --estado borrador
  ```
- **Entradas (qué aporta el usuario y cómo):** el pedido, escrito en el prompt; el resto lo lee de la carpeta (`gestion/estado.json`, `gestion/01-inicio/project-brief.md`, escalas de `registro.py`). El nivel por enfoque lo confirma el gestor.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/enfoques/` con calidad (`enfoque-calidad.md`: DoD/DoR, code review y gate de preparación de BMAD como métodos de verificación), riesgo (`enfoque-riesgo.md`), issues y cambios (`enfoque-issues-cambios.md`, `borrador`, `artefactos.enfoque-issues-cambios`, con la sección 5.1), comunicación (`enfoque-comunicacion.md`), datos y tecnología digital (`enfoque-datos-digitales.md`), en versión de una página.
  - Cómo verificarlo: abrir los archivos de la carpeta; mirar `artefactos` en `gestion/estado.json`.
- **Decisión humana:** el gestor confirma el nivel por enfoque; la ejecutiva los aprueba con el PID en `autorizar-proyecto` (registra pm-director).

### 13. `pm-planificacion-por-productos` — PBS y WBS
- **Prompt del usuario:** "Armá la PBS y la WBS con responsables; los requisitos están en el PRD, citá los ids."
- **Respuestas del usuario:**
  1. Sofía Ramírez, usuaria sénior: "Apruebo las descripciones de producto."
- **Quién:** orquestador → `pm-planificacion` → `pm-planificacion-por-productos`.
- **Qué pregunta o verifica:** productos antes que actividades; regla del 100 %; un responsable por paquete; `ref` con ids que existen en la fachada; con BMAD no escribe requisitos. La descripción del producto del proyecto ya se había producido para `autorizar-inicio` y cita FR, NFR, UJ y AD.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar requisitos
  python3 $E/wbs.py gestion/02-planificacion/wbs.csv --mermaid gestion/02-planificacion/visuales/wbs.md \
      --diccionario gestion/02-planificacion/diccionario-wbs-esqueleto.md
  python3 $E/estado.py --proyecto gestion artefacto pbs-wbs --ruta 02-planificacion/pbs-wbs.md --estado en-revision --version 0.9
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Requisitos (FR, NFR, UJ, AD): leídos de BMAD por la fachada.
  - Responsables por paquete: las personas ya registradas en `gestion/estado.json` (`roles`); si falta alguno, lo pregunta el orquestador.
  - Estimación y costo por paquete: llegan después (casos 15 y 16).
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/wbs.csv` (15 elementos, 11 hojas), `gestion/02-planificacion/visuales/wbs.md`, esqueleto `gestion/02-planificacion/diccionario-wbs-esqueleto.md` y `diccionario-wbs.md`; `gestion/02-planificacion/pbs-wbs.md` (`en-revision`, v0.9; `artefactos.pbs-wbs`). Tras cargar estimación y costo, `wbs.py` consolida 2.760 h y USD 138.000.
  - Cómo verificarlo: abrir `wbs.csv` en un editor o Excel; abrir `visuales/wbs.md` en un visor de Markdown con Mermaid.
- **Decisión humana:** la usuaria sénior aprueba las descripciones de producto; el conjunto se aprueba con el plan en `autorizar-proyecto`.

### 14. `pm-bmad-puente` — requisitos y trazabilidad
- **Prompt del usuario:** "Trazá los FR del PRD a los paquetes de la WBS y decime qué requisitos no tienen historia."
- **Quién:** orquestador → `pm-planificacion` → `pm-bmad-puente`.
- **Qué pregunta o verifica:** que la carpeta del proyecto esté fuera de las de BMAD; versión de BMAD soportada; que los derivados se regeneren y no se editen.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $B --proyecto gestion requisitos
  python3 $B --proyecto gestion trazabilidad --wbs 02-planificacion/wbs.csv
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna del usuario: el PRD y las historias se leen de BMAD por el puente (solo lectura) y la WBS de `gestion/02-planificacion/wbs.csv`.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/especificacion/requisitos-bmad.csv` (9 ids: 4 FR, 1 NFR, 1 UJ, 1 SM, 2 AD) y `gestion/02-planificacion/especificacion/matriz-trazabilidad-bmad.csv`: FR-1 → paquetes 2.1, 3.1 y 3.2; FR-4 sin historia; la historia `1-2-recuperar-contrasena` sin requisito; cero referencias rotas. Son derivados: se regeneran, no se editan.
  - Cómo verificarlo: abrir los dos CSV en un editor o Excel; o escribir "¿Qué requisitos no tienen historia?".
- **Decisión humana:** ninguna directa. FR-4 sin historia va a la PO (pm-agil-hibrido) para planificarla; la historia sin requisito va a pm-calidad o a pm-issues-cambios si es alcance nuevo.

### 15. `pm-cronograma-estimacion` — camino crítico y MS Project
- **Prompt del usuario:** "Estimá con PERT las actividades críticas, calculá el camino crítico y exportalo para abrirlo en MS Project."
- **Quién:** orquestador → `pm-planificacion` → `pm-cronograma-estimacion`.
- **Qué pregunta o verifica:** cada actividad con paquete (`wbs`), técnica, supuestos, estimador y confianza; `P ≥ M ≥ O`; fin contra el mandato y la tolerancia de tiempo; reserva fuera del estimado base.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/cpm.py gestion/02-planificacion/actividades.csv --inicio 2026-11-09 \
      --mermaid gestion/02-planificacion/gantt.md \
      --mspdi gestion/02-planificacion/cronograma.xml --titulo "Portal de autoservicio" \
      --wbs gestion/02-planificacion/wbs.csv
  python3 $E/estado.py --proyecto gestion artefacto cronograma --ruta 02-planificacion/cronograma.md --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Estimaciones optimista, más probable y pesimista, con estimador y confianza: las aporta el equipo respondiendo al orquestador (o en un archivo adjunto en la sesión); el sistema las vuelca a `gestion/02-planificacion/actividades.csv` con predecesoras y paquete (`wbs`).
  - Fecha de inicio (2026-11-09): si no está en el plan, la pregunta el orquestador.
  - `gestion/02-planificacion/wbs.csv`: ya en la carpeta.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/cronograma.md` (`en-revision`; `artefactos.cronograma`): 120 días laborables, fin 2027-04-26, camino crítico A00→A02→A04→A05→A07→A08→A10.
  - `gestion/02-planificacion/gantt.md` y `gestion/02-planificacion/cronograma.xml` (MSPDI con tareas resumen por paquete de la WBS).
  - Cómo verificarlo: abrir `cronograma.xml` en MS Project o ProjectLibre; abrir `gantt.md` en un visor de Markdown con Mermaid.
- **Decisión humana:** ninguna en este paso; el cronograma se aprueba con el plan. Si el fin no entrara, pasaría opciones a la junta vía pm-director.

### 16. `pm-costos-presupuesto` — BAC y reservas
- **Prompt del usuario:** "Costeá los paquetes y calculá la contingencia desde el registro de riesgos, sin duplicarla. El mandato dice 180 mil."
- **Respuestas del usuario:**
  1. Diego Ferreira, proveedor sénior: "Te adjunto la cotización del proveedor por paquete, con fecha y validez."
- **Quién:** orquestador → `pm-planificacion` → `pm-costos-presupuesto`.
- **Qué pregunta o verifica:** tarifas y cotizaciones con fuente (las del proveedor se piden a Diego); ningún paquete con reserva adentro; contingencia una sola vez, ligada a riesgos con EMV; total de `wbs.py` igual a la hoja de costeo; Σ PV = BAC.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/wbs.py gestion/02-planificacion/wbs.csv
  python3 $E/registro.py --proyecto gestion listar riesgos --abiertos --json
  python3 $E/estado.py --proyecto gestion artefacto presupuesto --ruta 02-planificacion/presupuesto.md --estado en-revision
  python3 $E/estado.py --proyecto gestion artefacto linea-base-costo --ruta 02-planificacion/linea-base-costo.csv --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Techo de 180.000: escrito en el prompt (coincide con el mandato).
  - Tarifas y cotización del proveedor: las pide el orquestador a Diego; llegan como archivo adjunto en la sesión o escritas en el chat.
  - Riesgos con EMV: de `gestion/03-control/registros/riesgos.csv`; paquetes: de `gestion/02-planificacion/wbs.csv`.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/presupuesto.md` (`en-revision`; `artefactos.presupuesto`): base 138.000 + contingencia 27.000 (EMV de R-001 y R-002 menos la oportunidad R-005) = BAC 165.000; reserva de gestión 15.000 fuera del BAC; presupuesto autorizado 180.000, igual al mandato.
  - `gestion/02-planificacion/linea-base-costo.csv` (`en-revision`; `artefactos.linea-base-costo`) con PV por período.
  - Cómo verificarlo: abrir el presupuesto; abrir `linea-base-costo.csv` en un editor o Excel.
- **Decisión humana:** la reserva de gestión es una propuesta: la aprueba la junta en `autorizar-proyecto`.

### 17. `pm-adquisiciones` — estrategia con el proveedor
- **Prompt del usuario:** "El desarrollo lo hace un proveedor externo: armá el hacer o comprar y la estrategia, precio fijo por release con retención del 10 %."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Adjudicación y firma las aprueba Laura Méndez junto con el área legal de la cooperativa."
- **Quién:** orquestador → `pm-inicio` (en IP) → `pm-adquisiciones`.
- **Qué pregunta o verifica:** costo total y riesgos de ambas opciones; tipo de contrato contra la definición del alcance (precio fijo exige alcance definido: el enunciado del trabajo cita los FR del PRD); hitos de pago en los límites de etapa; quién de compras y legal aprueba (lo pregunta).
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion artefacto estrategia-adquisiciones \
      --ruta 02-planificacion/adquisiciones/estrategia-adquisiciones.md --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Tipo de contrato (precio fijo por release) y retención del 10 %: escritos en el prompt.
  - FR del PRD para el enunciado del trabajo: leídos de BMAD por la fachada.
  - Quién de compras y legal aprueba: lo pregunta el orquestador.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/adquisiciones/estrategia-adquisiciones.md` (`en-revision`; `artefactos.estrategia-adquisiciones`).
  - Propuestas en el retorno (todavía no son filas): riesgos contractuales para pm-riesgos, hitos para pm-cronograma-estimacion, monto para pm-costos-presupuesto.
  - Cómo verificarlo: abrir el archivo; mirar `artefactos.estrategia-adquisiciones` en `gestion/estado.json`.
- **Decisión humana:** la estrategia se aprueba con el plan en `autorizar-proyecto`; adjudicación y firma son decisión de la autoridad de la cooperativa (Laura) con legal, y se devuelven como decisión humana requerida.

### 18. `pm-agil-hibrido` — backlog, release plan y DoD
- **Prompt del usuario:** "Armá el backlog con MoSCoW y releases a partir de las historias de BMAD, y el release plan con DoD."
- **Respuestas del usuario:**
  1. Sofía Ramírez, product owner: "Te paso prioridad, MoSCoW, estimación, iteración y release de cada historia; agregá PM-001 como Could por I-001."
  2. Lucía Benítez, jefa de equipo, y Sofía Ramírez, usuaria sénior: "Acordamos la DoD y la DoR del borrador."
- **Quién:** orquestador → `pm-planificacion` → `pm-agil-hibrido` (usa pm-bmad-puente para las columnas derivadas).
- **Qué pregunta o verifica:** cadencia de 14 días y PO registrados; Must ≤ ~60 % de la capacidad; `Σ puntos Must+Should ≤ velocidad × iteraciones`; con BMAD, nada de historias a mano: el puente refresca las derivadas y la PO completa solo las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs).
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $B --proyecto gestion backlog            # primera sincronización: 4 historias nuevas
  # la PO completa las columnas de gobierno y agrega PM-001 (Could, por I-001)
  python3 $B --proyecto gestion backlog            # segunda: gobierno intacto, PM-001 se conserva
  python3 $B --proyecto gestion handoff            # prioridades de gobierno → documento para el equipo BMAD
  python3 $E/estado.py --proyecto gestion artefacto backlog --ruta 02-planificacion/backlog.csv --estado en-revision
  python3 $E/estado.py --proyecto gestion artefacto release-plan --ruta 02-planificacion/release-plan.md --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Historias de BMAD: leídas por el puente (solo lectura); nada se escribe a mano.
  - Columnas de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs): las dicta la PO en el chat, respondiendo al orquestador.
  - Cadencia y PO: ya en `gestion/estado.json`.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/backlog.csv` (`en-revision`; `artefactos.backlog`).
  - `gestion/02-planificacion/release-plan.md` (`en-revision`; `artefactos.release-plan`): cadencia, DoD/DoR, ceremonias, línea base.
  - `gestion/02-planificacion/especificacion/handoff-bmad-<fecha>-prioridades.md` para el equipo BMAD (pendiente en `estado.json.integraciones.bmad.handoffs`).
  - Cómo verificarlo: abrir `backlog.csv` en un editor o Excel; abrir el release plan y el traspaso.
- **Decisión humana:** DoD y DoR las acuerdan el equipo y la usuaria sénior; backlog comprometido y release plan se aprueban con el plan de etapa en `autorizar-etapa`.

### 19. `pm-comunicacion-stakeholders` — matriz de comunicaciones
- **Prompt del usuario:** "Armá la matriz de comunicaciones con el consejo, la junta, el equipo del proveedor y los socios piloto."
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva: "Apruebo la matriz de comunicaciones."
- **Quién:** orquestador → `pm-inicio` → `pm-comunicacion-stakeholders`.
- **Qué pregunta o verifica:** que exista el enfoque de comunicación (dueño pm-enfoques-gestion) y que la matriz lo respete; que todo `stakeholders.csv` quede cubierto; que las filas con `confidencial=si` no entren en comunicados amplios; idioma por audiencia. Desde la versión 2.2 parte de la estrategia de cada cuadrante de la matriz poder/interés, de los estereotipos y de las preferencias confirmadas del maestro (casos 38 a 41); si una preferencia confirmada contradice la matriz, el perfil lo avisa y la matriz se actualiza.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion listar stakeholders --json
  python3 $E/estado.py --proyecto gestion artefacto matriz-comunicaciones \
      --ruta 02-planificacion/matriz-comunicaciones.md --estado en-revision
  # tras la aprobación:
  python3 $E/registro.py --proyecto gestion actualizar stakeholders ST-001 --campo canal=correo --campo frecuencia=mensual
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Audiencias: escritas en el prompt.
  - Interesados: de `gestion/03-control/registros/stakeholders.csv`; políticas: de `gestion/02-planificacion/enfoques/enfoque-comunicacion.md`.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/matriz-comunicaciones.md` (`en-revision`, `aprobado` tras la decisión; `artefactos.matriz-comunicaciones`) con la sprint review como evento recurrente.
  - Tras la aprobación: ST-001 con `canal=correo` y `frecuencia=mensual` en `gestion/03-control/registros/stakeholders.csv`.
  - Cómo verificarlo: abrir la matriz; abrir `stakeholders.csv` en un editor o Excel.
  - Los mensajes que salen de la matriz se pueden enviar por la capa de canales (correo, Slack, Teams o `.eml`), siempre con aprobación y confirmación explícita (caso 44).
- **Decisión humana:** la ejecutiva aprueba la matriz dentro del PID (pm-director `estado.py aprobar matriz-comunicaciones`).

### 20. `pm-acta-constitucion` — PID por referencia
- **Prompt del usuario:** "Ya tenemos brief, business case, roles, enfoques y planes: armá el PID por referencia y decime qué falta para autorizar el proyecto."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "PID índice, versión mínima."
- **Quién:** orquestador → `pm-inicio` → `pm-acta-constitucion`.
- **Qué pregunta o verifica:** `autorizar-inicio` aprobada; formato (PID índice, versión mínima); componentes con ruta, versión, estado, creador, revisor y aprobador; consistencia (presupuesto 180.000 en mandato, business case y presupuesto; tolerancias iguales a `estado.json`); con BMAD, PRD en `final` y `verificar` sin desvíos; plan de la etapa 2 presente.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $B --proyecto gestion verificar
  python3 $E/estado.py --proyecto gestion artefacto pid --ruta 00-direccion/pid.md --estado en-revision --version 0.9
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: los componentes ya están en la carpeta y el PRD y la arquitectura se leen de BMAD por el puente. El formato lo confirma el gestor.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/00-direccion/pid.md` (`en-revision`, v0.9; `artefactos.pid`): cita brief de producto, PRD y arquitectura por ruta y sha.
  - Copia `gestion/00-direccion/historial/pid-v0.9.md`.
  - Lista de bloqueantes (ninguno) en la respuesta.
  - Cómo verificarlo: abrir el PID; o escribir "¿Qué falta para autorizar el proyecto?".
- **Decisión humana:** el gestor confirma el formato; la junta decide `autorizar-proyecto`.

### 21. `pm-direccion-decisiones` — autorizar el proyecto y la etapa 2
- **Prompt del usuario:** "La junta del 6 de noviembre tiene que autorizar el proyecto y la primera etapa de entrega: prepará la decisión."
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva, por la junta (con Sofía Ramírez y Diego Ferreira): "Aprobamos autorizar el proyecto y la etapa 2 “Release 1” hasta el 15 de febrero de 2027, con tolerancias de etapa de +2 semanas y ±10 % de costo."
- **Quién:** orquestador → `pm-director` → `pm-direccion-decisiones` (modo A); orquestador → junta; orquestador → `pm-director` (modo B).
- **Qué pregunta o verifica:** justificación continua (deseable, viable, alcanzable) con el business case; productos requeridos; desempeño contra tolerancias; `verificar` limpio; ejecutivo nombrado. Redacta dos solicitudes con al menos tres opciones y recomendación con grado de confianza.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $X --proyecto gestion listar puerta autorizar-proyecto
  python3 $B --proyecto gestion verificar
  # tras la decisión de la junta (modo B):
  python3 $E/estado.py --proyecto gestion puerta autorizar-proyecto --decision aprobado \
      --por "Ejecutivo: Laura Méndez" --fecha 2026-11-06
  python3 $E/estado.py --proyecto gestion aprobar pid --por "Ejecutivo: Laura Méndez" --version 1.0
  python3 $E/estado.py --proyecto gestion aprobar business-case --por "Ejecutivo: Laura Méndez" --version 1.0
  python3 $B --proyecto gestion linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"
  python3 $B --proyecto gestion linea-base arquitectura --version 1.0 --por "Ejecutivo: Laura Méndez"
  python3 $B --proyecto gestion linea-base epicas --version 1.0 --por "Ejecutivo: Laura Méndez"
  python3 $E/estado.py --proyecto gestion puerta autorizar-etapa --decision aprobado \
      --por "Ejecutivo: Laura Méndez" --etapa-nombre "Release 1" --fin 2027-02-15
  python3 $E/estado.py --proyecto gestion tolerancia --nivel etapa tiempo="+2 semanas" costo="±10 %"
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: lee los productos de la puerta de la carpeta y BMAD por el puente. La decisión llega como respuesta literal de la junta, con nombre y rol.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/00-direccion/decisiones/2026-11-06-solicitud-autorizar-proyecto.md` y `…-solicitud-autorizar-etapa.md`; acta `gestion/00-direccion/decisiones/2026-11-06-acta-junta-autorizar-proyecto.md`.
  - PID y business case v1.0 en `gestion/00-direccion/historial/`; líneas base `bmad-prd-v1.0/` (sha ea90ca87952b), `bmad-arquitectura-v1.0/`, `bmad-epicas-v1.0/` en la misma carpeta.
  - `gestion/estado.json`: las dos puertas en `puertas[]`, `fase` = `entrega`, `proceso_actual` = `CS`, etapa 2, `tolerancias.etapa`; una fila por puerta en `gestion/03-control/registros/decisiones.csv`.
  - Cómo verificarlo: abrir solicitudes y acta; abrir `decisiones.csv`; o escribir "¿Dónde estamos?" (atajo `/pm-method:pm-estado`).
- **Decisión humana:** la junta (Laura decide; Sofía y Diego participan) aprueba ambas puertas. pm-director registra solo después de que el orquestador trae la respuesta literal con nombre y rol.

---

## Parte 3 · Etapa de entrega 2 (CS y MP)

### 22. `pm-integraciones` — proyecto sin conectores
- **Prompt del usuario:** "No conectamos Jira ni Teams; las transcripciones las bajamos como archivo. ¿Cómo quedan las integraciones?"
- **Quién:** orquestador → `pm-control` → `pm-integraciones`.
- **Qué pregunta o verifica:** qué herramientas MCP hay en la sesión (ninguna de tracker, chat ni docs); qué capacidad queda cubierta por alternativa local.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion integracion tracker=ninguno chat=ninguno docs=ninguno reuniones=archivo okr=archivo
  ```
- **Entradas (qué aporta el usuario y cómo):** lo que dice el prompt (sin tracker ni chat; transcripciones por archivo) y las herramientas MCP presentes en la sesión (ninguna de tracker, chat ni docs).
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/estado.json` → `integraciones`: `tracker` = `ninguno`, `chat` = `ninguno`, `docs` = `ninguno`, `reuniones` = `archivo`, `okr` = `archivo`.
  - Una nota en `gestion/03-control/registros/diario.md`. Las alternativas son el `backlog.csv`, la transcripción por archivo, borradores de mensajes para copiar y `okr.csv`. Sin ningún conector igual se puede enviar a los interesados por la capa de canales: correo SMTP propio, webhooks de Slack o Teams, o archivos `.eml` sin configuración (caso 44 y [CASOS-DE-USO-INTEGRACIONES caso 8](CASOS-DE-USO-INTEGRACIONES.md)).
  - Cómo verificarlo: abrir `gestion/estado.json` y `diario.md`; o escribir "¿Qué integraciones tiene el proyecto?".
- **Decisión humana:** ninguna. La skill sugiere conectar un tracker si el equipo lo usa, sin bloquear el trabajo (ver variante C).

### 23. `pm-paquetes-trabajo` — el sprint 3 como paquete
- **Prompt del usuario:** "Autorizá el sprint 3 como paquete de trabajo para el equipo de Lucía; la etapa 2 ya está aprobada."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Autorizo el WP-003."
  2. Lucía Benítez, jefa de equipo: "Acepto el WP-003."
- **Quién:** orquestador → `pm-control` → `pm-paquetes-trabajo`.
- **Qué pregunta o verifica:** fase `entrega`, proceso CS y `autorizar-etapa` aprobada; descripciones de producto con revisor independiente y autoridad de aceptación; tolerancias del paquete dentro de las de la etapa; frecuencia de checkpoint; con proveedor, coherencia con el contrato. Alcance = ids de historias, sin copiar texto.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar historias --epica E-1
  python3 $E/registro.py --proyecto gestion agregar calidad --campo producto="1-1-login-de-socio" \
      --campo metodo_verificacion=prueba --campo criterios="Criterios de la historia y NFR-1" \
      --campo responsable_productor="Lucía Benítez" --campo revisores="Andrea Costa" --campo aprobador="Sofía Ramírez"
  # tras el acuerdo:
  python3 $E/registro.py --proyecto gestion agregar decisiones --campo decision="WP-003 autorizado y aceptado" \
      --campo decidido_por="Gestor: Martín Suárez; Jefa de equipo: Lucía Benítez" --campo nivel=equipo
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: las historias de la épica E-1 se leen por la fachada y las descripciones de producto, tolerancias y contrato ya están en la carpeta. La autorización y la aceptación llegan como respuestas.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/03-control/paquetes-trabajo/WP-003-sprint-3.md` (`estado_paquete: autorizado` tras el acuerdo).
  - Filas Q-### en `gestion/03-control/registros/calidad.csv` (la del login, `1-1-login-de-socio`, es la Q-001 del caso 25).
  - Fila "WP-003 autorizado y aceptado", nivel `equipo`, en `gestion/03-control/registros/decisiones.csv`.
  - Cómo verificarlo: abrir el paquete; abrir `calidad.csv` y `decisiones.csv` en un editor o Excel.
- **Decisión humana:** dos actos: el gestor autoriza y la jefa de equipo acepta. pm-control los devuelve como decisión humana; con las respuestas, escribe la fila de aceptación. Si además se quiere marcar el documento WP-003 como aprobado con `estado.py aprobar`, lo ejecuta pm-director.

### 24. `pm-reuniones` — acta del checkpoint
- **Prompt del usuario:** "Te paso el VTT del checkpoint del sprint 3: armá el acta y proponé las acciones." (con el archivo adjunto en la sesión, o guardado antes en `gestion/03-control/reuniones/2026-12-03-checkpoint-sprint3-original.vtt`)
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Fue el checkpoint del sprint 3, el 3 de diciembre de 2026, y lo presidí yo."
  2. Martín Suárez, gestor: "No hay consentimiento para análisis de clima."
  3. Martín Suárez, gestor: "Confirmo el acta y la lista de cargas."
- **Quién:** orquestador → `pm-control` → `pm-reuniones`.
- **Qué pregunta o verifica:** nombre, tipo, fecha y quién presidió (Martín); hablantes `?` o nombres partidos tras normalizar; clasificación de cada hallazgo (acción ≠ issue; riesgo = incierto); decisiones de junta marcadas para pm-director. No hay consentimiento para análisis de clima, así que ese paso no corre.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $T gestion/03-control/reuniones/2026-12-03-checkpoint-sprint3-original.vtt \
      --salida gestion/03-control/reuniones/2026-12-03-checkpoint-sprint3-transcripcion.md
  # tras la confirmación del acta:
  python3 $E/registro.py --proyecto gestion agregar acciones --campo origen=acta-2026-12-03-checkpoint-sprint3 \
      --campo descripcion="Pedir al core bancario credenciales de pruebas" --campo responsable="Lucía Benítez" \
      --campo fecha_compromiso=2026-12-11 --campo prioridad=alta
  python3 $E/registro.py --proyecto gestion agregar decisiones --campo decision="Notificación por SMS en lugar de correo" \
      --campo decidido_por="PO: Sofía Ramírez" --campo nivel=product-owner
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Transcripción: archivo `.vtt` en `gestion/03-control/reuniones/2026-12-03-checkpoint-sprint3-original.vtt` (lo deja el usuario ahí o lo adjunta y el sistema lo guarda). También sirven `.srt`, `.txt`, `.docx` o texto pegado.
  - Nombre, tipo, fecha y quién presidió; consentimiento para clima: respuestas al orquestador.
- **Salidas (qué queda y dónde verificarlo):**
  - Transcripción normalizada `gestion/03-control/reuniones/2026-12-03-checkpoint-sprint3-transcripcion.md` (9 intervenciones, 3 hablantes).
  - Acta `gestion/03-control/reuniones/2026-12-03-acta-checkpoint-sprint3.md`.
  - Tras confirmar: D-026 en `gestion/03-control/registros/decisiones.csv`; A-001 (Lucía, 2026-12-11) y A-002 (Sofía, 2026-12-09) en `gestion/03-control/registros/acciones.csv`; R-006 (P4 × I3 = 12, EMV 8.400) en `gestion/03-control/registros/riesgos.csv`; I-002 (`problema-preocupacion`) en `gestion/03-control/registros/issues.csv`.
  - Opcional: distribuir el acta confirmada a los participantes por la capa de canales (`envios.py nuevo --origen <acta> --proposito acta`, con aprobación y `--confirmar`; caso 44) y proponer las preferencias de comunicación que alguien declaró en primera persona durante la reunión (`interesados.py proponer`; caso 41).
  - Cómo verificarlo: abrir el acta; abrir los CSV en un editor o Excel; o escribir "Mostrame las acciones abiertas".
- **Decisión humana:** Martín, que presidió, confirma el acta y la lista de cargas. Nada entra a los registros antes.

### 25. `pm-calidad` — aceptación por requisito del login
- **Prompt del usuario:** "¿Qué FR del release 1 ya podemos dar por aceptados? Armá la aceptación del login."
- **Respuestas del usuario:**
  1. Sofía Ramírez, usuaria sénior: "Acepto el login de socio."
- **Quién:** orquestador → `pm-control` → `pm-calidad`.
- **Qué pregunta o verifica:** dos evidencias (control del proyecto y revisión independiente); fila Q-### con resultado `aprobado`; cobertura `terminado` de la fachada; `done` en BMAD no alcanza por sí solo.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar requisitos --cobertura terminado
  python3 $E/registro.py --proyecto gestion actualizar calidad Q-001 --campo resultado=aprobado \
      --campo estado=completada --campo fecha_real=2026-12-09
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Resultado de la revisión independiente (Andrea Costa, 2026-12-09): lo informa el usuario en el chat para cargarlo en Q-001 de `gestion/03-control/registros/calidad.csv`.
  - Cobertura `terminado`: leída por la fachada.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/03-control/reportes/2026-12-10-aceptacion-login.md` (clave `aceptacion-login`, `aprobado` tras la aceptación de Sofía).
  - Q-001 en `gestion/03-control/registros/calidad.csv` con `resultado=aprobado`, `estado=completada`, `fecha_real=2026-12-09`. Se actualiza el product status account.
  - Cómo verificarlo: abrir el informe; abrir `calidad.csv`; mirar `artefactos.aceptacion-login` en `gestion/estado.json`.
- **Decisión humana:** Sofía acepta como autoridad nombrada; con su respuesta, pm-director ejecuta `estado.py aprobar aceptacion-login --por "Usuario sénior: Sofía Ramírez" --nivel junta` y se actualiza el product status account.

### 26. `/pm-reporte highlight` — informe de la quincena
- **Prompt del usuario:** "Armá el highlight report de esta quincena."
  Atajo: `/pm-method:pm-reporte highlight`
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "La fecha de corte es el 10 de diciembre de 2026."
  2. Andrea Costa, aseguramiento: "Revisé el informe; está conforme."
  3. Martín Suárez, gestor: "Revisado; aprobalo."
- **Quién:** orquestador → `pm-control` → `pm-progreso-reportes`.
- **Qué pregunta o verifica:** período y fecha de corte (2026-12-10); conteos idénticos a `registro.py resumen`; semáforo contra tolerancias de etapa; desvíos de BMAD del período.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion resumen --json --corte 2026-12-10
  python3 $E/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 95000 --tol-costo 10 --tol-plazo 14 --proyecto gestion
  python3 $B --proyecto gestion avance
  python3 $B --proyecto gestion verificar
  python3 $E/estado.py --proyecto gestion artefacto highlight-2026-12-10 \
      --ruta 03-control/reportes/2026-12-10-highlight-report.md --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Serie EVM `gestion/03-control/reportes/progreso.csv` actualizada al corte: el costo real acumulado lo informa el usuario en el chat y el sistema lo vuelca en la fila del período.
  - Registros, tolerancias de etapa y avance BMAD: ya en la carpeta o leídos por el puente.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/03-control/reportes/2026-12-10-highlight-report.md` (`en-revision` → `aprobado`; `artefactos.highlight-2026-12-10`): PV 52.000, EV 47.000, AC 50.000, SPI 0,90, CPI 0,94, EAC 101.064, costo y plazo en ámbar, sin excepción; avance BMAD 13/21 puntos (61,9 %); 6 riesgos abiertos (1 alto), 1 issue abierto, A-002 vencida.
  - Una fila nueva en `gestion/03-control/reportes/avance-bmad.csv`.
  - Cómo verificarlo: abrir el informe; mirar `artefactos.highlight-2026-12-10` en `gestion/estado.json`.
- **Decisión humana:** aseguramiento (Andrea) confirma; con la revisión del gestor, pm-director ejecuta `estado.py aprobar highlight-2026-12-10 --por "Gestor: Martín Suárez"`. Publicarlo en un canal requiere confirmación aparte: con un conector MCP (pm-integraciones) o por la capa de canales (`envios.py nuevo --origen 03-control/reportes/2026-12-10-highlight-report.md --proposito informe`, aprobación del gestor y `enviar … --confirmar`; caso 44).

### 27. `pm-progreso-reportes` — ¿estamos cerca de la tolerancia de proyecto?
- **Prompt del usuario:** "La junta pregunta qué tan cerca estamos de la tolerancia de costo del proyecto. Calculalo y decime qué EAC usar."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Confirmo las acciones correctivas propuestas."
- **Quién:** orquestador → `pm-control` → `pm-progreso-reportes`.
- **Qué pregunta o verifica:** BAC vigente sin reserva de gestión (165.000); método del EV declarado; dos EAC y la elegida justificada; se compara el pronóstico, no el acumulado. Corre además una prueba de sensibilidad.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 165000 --tol-costo 8 --proyecto gestion
  python3 $E/evm.py --pv 52000 --ev 47000 --ac 51000 --bac 165000 --tol-costo 8 --json     # sensibilidad
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: usa `gestion/03-control/reportes/progreso.csv`, el BAC vigente (165.000) y la tolerancia de costo del proyecto de `gestion/estado.json`.
- **Salidas (qué queda y dónde verificarlo):**
  - Respuesta con EAC 175.532 (−6,4 %, ámbar). Con AC 51.000, VAC −8,5 % supera el 8 %: el script marca `excepcion_prevista` y avisa que hay que preparar el informe de excepción.
  - Si se pide, `gestion/03-control/reportes/2026-12-10-analisis-valor-ganado.md`.
  - Acciones correctivas confirmadas en `gestion/03-control/registros/acciones.csv`.
  - Cómo verificarlo: leer la respuesta; abrir `acciones.csv`; o escribir "Mostrame las acciones abiertas".
- **Decisión humana:** dentro de tolerancia, el gestor confirma acciones correctivas (van a `acciones.csv`). Si el pronóstico real saliera de tolerancia, pm-control emitiría el informe de excepción con la plantilla de pm-issues-cambios y lo derivaría a pm-director.

### 28. `pm-visuales` — tablero con vista por actor
- **Prompt del usuario:** "Generá el tablero de esta semana con la vista por actor para mandarle a cada uno su link."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Confirmado, podés compartirlo."
- **Quién:** orquestador → `pm-control` → `pm-visuales`.
- **Qué pregunta o verifica:** fuentes del tablero (highlight vigente, `evm.py --json`, registros, `avance-bmad.csv`); que los objetivos en rojo tengan issue o excepción; que las acciones salgan de `acciones.csv` y no de `issues.csv`; legibilidad y fecha de corte.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 95000 --tol-costo 10 --tol-plazo 14 --json
  python3 $E/registro.py --proyecto gestion listar acciones --abiertos --json
  python3 $E/registro.py --proyecto gestion listar riesgos --abiertos --json
  python3 $E/especificacion.py --proyecto gestion resumen --json
  python3 $E/estado.py --proyecto gestion artefacto tablero-avance \
      --ruta 03-control/reportes/2026-12-10-tablero-avance.html --estado borrador
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: highlight vigente, `progreso.csv`, registros y `avance-bmad.csv` ya están en la carpeta.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/03-control/reportes/2026-12-10-tablero-avance.html` (`borrador`; `artefactos.tablero-avance`): 2 acciones, 6 riesgos, 1 issue. Con `?actor=Sofía Ramírez` muestra A-002 vencida y los riesgos R-003, R-004 y R-006 de los que es propietaria.
  - Sin chat conectado, el texto con los enlaces para pegar queda en la respuesta.
  - Cómo verificarlo: abrir el HTML en el navegador, con y sin `?actor=…` al final de la dirección.
- **Decisión humana:** el gestor confirma antes de compartirlo. Sin chat conectado, se entrega el texto con los enlaces para pegar; también puede salir por la capa de canales (webhook de Slack o Teams, o correo) con aprobación del gestor y `--confirmar` (caso 44).

### 29. `/pm-estado` — dónde estamos
- **Prompt del usuario:** "¿Dónde estamos y qué sigue?"
  Atajo: `/pm-method:pm-estado`
- **Quién:** orquestador → skill-comando `pm-estado` (scripts de pm-estado-proyecto, pm-sanidad y pm-bmad-puente).
- **Qué pregunta o verifica:** fase, proceso y etapa; tolerancias y excepción abierta; puertas pendientes; ERROR de sanidad; avance BMAD.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion ver
  python3 $E/estado.py --proyecto gestion siguiente
  python3 $E/registro.py --proyecto gestion resumen
  python3 $E/sanidad.py --proyecto gestion --rapido
  python3 $B --proyecto gestion avance
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna: lee el estado del proyecto, los registros y el avance de BMAD por el puente.
- **Salidas (qué queda y dónde verificarlo):**
  - Ninguna nueva salvo una fila en `gestion/03-control/reportes/avance-bmad.csv` (una por fecha de corte). El resumen y el siguiente paso, con el rol que decide, quedan en la respuesta.
  - Cómo verificarlo: leer la respuesta; abrir `avance-bmad.csv` en un editor o Excel.
- **Decisión humana:** ninguna. El siguiente paso se muestra con el rol que decide.

### 30. `/pm-sync bmad` — el PRD cambió
- **Prompt del usuario:** "El equipo BMAD corrió una corrección de rumbo y agregó FR-5 al PRD: sincronizá con BMAD."
  Atajo: `/pm-method:pm-sync bmad`
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Sí, registrá el issue de solicitud de cambio."
- **Quién:** orquestador → `pm-control` → `pm-bmad-puente`, `pm-sanidad`.
- **Qué pregunta o verifica:** cobertura y requisitos sin historia; desvíos contra la línea base; Sprint Change Proposals nuevas; traspasos pendientes en `estado.json.integraciones.bmad.handoffs`; columnas de gobierno intactas.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/especificacion.py --proyecto gestion resumen
  python3 $B --proyecto gestion backlog
  python3 $B --proyecto gestion avance
  python3 $B --proyecto gestion verificar --json
  python3 $E/sanidad.py --proyecto gestion
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna del usuario: el PRD modificado y la Sprint Change Proposal se leen de BMAD por el puente (solo lectura).
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/02-planificacion/backlog.csv` con las columnas derivadas refrescadas (las de gobierno, intactas) y una fila nueva en `gestion/03-control/reportes/avance-bmad.csv`.
  - En la respuesta, `verificar` informa `desvio bmad-prd v1.0 · agregados ['FR-5']` y `sprint-change-proposal-2027-01-12.md`. La skill propone un issue `solicitud-cambio`; no lo crea sola: con la confirmación queda como I-003 en `gestion/03-control/registros/issues.csv` (caso 32).
  - Cómo verificarlo: leer la respuesta; abrir `issues.csv`; o escribir "Mostrame los issues abiertos".
- **Decisión humana:** el gestor confirma que se registre el issue. El "sí" del flujo de corrección de rumbo de BMAD no aprueba nada en PRINCE2.

### 31. `pm-sanidad` — "algo no cuadra"
- **Prompt del usuario:** "Algo no cuadra: el tablero muestra cuatro historias y el equipo dice que hay un requisito nuevo. Revisá la sanidad."
- **Quién:** orquestador en el hilo principal → `pm-sanidad` (sin subagente; la tabla de enrutamiento la deja en el hilo principal).
- **Qué pregunta o verifica:** las seis familias de controles. Encuentra ESP-10: la especificación difiere de su línea base y ningún issue la cita (cambio no controlado), que siempre es ERROR.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/sanidad.py --proyecto gestion --informe
  python3 $E/registro.py --proyecto gestion agregar acciones --campo origen=sanidad-2027-01-13 \
      --campo descripcion="Tramitar FR-5 como solicitud de cambio" --campo responsable="Martín Suárez" \
      --campo fecha_compromiso=2027-01-14
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna: lee el estado del proyecto, los registros y la especificación.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/03-control/reportes/2027-01-13-sanidad.md` y una acción con responsable (Martín Suárez, 2027-01-14) en `gestion/03-control/registros/acciones.csv`. El ERROR se deriva a pm-issues-cambios. Mientras siga abierto, no se presenta ninguna puerta, salvo que el humano decida seguir y quede como condición.
  - Cómo verificarlo: abrir el informe de sanidad; abrir `acciones.csv`; o escribir "Revisá la sanidad rápida" (la corre también `/pm-method:pm-estado`).
- **Decisión humana:** ninguna para el informe. `--reparar` no se usa: solo agregaría columnas faltantes o reconstruiría el índice, y no corrige datos de negocio.

### 32. `pm-issues-cambios` — solicitud de cambio por FR-5
- **Prompt del usuario:**
  1. "`bmad.py verificar` dice que el PRD tiene un FR nuevo desde la línea base: armá la solicitud de cambio y decime quién la aprueba."
  2. (cuando el equipo BMAD confirma) "El equipo BMAD ya aplicó el traspaso de C-001: verificá y fijá la nueva línea base."
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva, por la junta: "Aprobamos C-001, financiado con la reserva de gestión."
- **Quién:** orquestador → `pm-control` → `pm-issues-cambios`; luego `pm-director`.
- **Qué pregunta o verifica:** tipo (uno de cinco: `solicitud-cambio`); impacto sobre los siete objetivos (+5 puntos, +USD 4.500 = 2,7 % del BAC, 0 días en el camino crítico); al menos dos opciones; autoridad: la autoridad de cambio delegada no tiene presupuesto de cambio suficiente y el cambio consume reserva de gestión, así que decide la junta.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion agregar issues --campo tipo=solicitud-cambio \
      --campo titulo="FR-5 agregado al PRD por corrección de rumbo" --campo prioridad=alta \
      --campo severidad=mayor --campo responsable="Martín Suárez"
  python3 $E/registro.py --proyecto gestion actualizar issues I-003 --campo estado=pendiente-cambio
  python3 $E/registro.py --proyecto gestion agregar cambios --campo titulo="Incorporar FR-5" \
      --campo impacto_costo="+4.500 USD" --campo impacto_tiempo="0 días en camino crítico" \
      --campo notas="origen I-003; ids: FR-5" --campo estado=pendiente-decision
  # tras la decisión de la junta (pm-director):
  python3 $E/estado.py --proyecto gestion puerta decision-ad-hoc --decision aprobado \
      --por "Ejecutivo: Laura Méndez" --fecha 2027-01-15 --condiciones "Financiar con reserva de gestión"
  # pm-control copia la decisión al registro de cambios y emite el traspaso:
  python3 $E/registro.py --proyecto gestion actualizar cambios C-001 --campo decision=aprobado \
      --campo decidido_por="Junta: Laura Méndez" --campo fecha_decision=2027-01-15 --campo estado=aprobado
  python3 $B --proyecto gestion handoff --cambio C-001
  # el equipo BMAD aplica el traspaso y lo confirma; luego:
  python3 $B --proyecto gestion verificar --marcar-vistas
  # pm-director fija la nueva línea base:
  python3 $B --proyecto gestion linea-base prd --version 1.1 --por "Ejecutivo: Laura Méndez"
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Desvío del PRD (FR-5): leído de BMAD por el puente.
  - Estimación del cambio (+5 puntos, +USD 4.500): la aporta el equipo respondiendo al orquestador **[verificar]** (el caso no dice de dónde sale).
  - Decisión de la junta y confirmación del equipo BMAD: respuestas y segundo prompt.
- **Salidas (qué queda y dónde verificarlo):**
  - I-003 en `gestion/03-control/registros/issues.csv` (`pendiente-cambio`) y C-001 en `gestion/03-control/registros/cambios.csv` (`aprobado`, decidido por "Junta: Laura Méndez" el 2027-01-15).
  - `gestion/03-control/reportes/2027-01-13-solicitud-cambio-C-001.md`; D-028 en `gestion/03-control/registros/decisiones.csv`.
  - `gestion/02-planificacion/especificacion/handoff-bmad-<fecha>-C-001.md` y `gestion/00-direccion/historial/bmad-prd-v1.1/` (sha 661eccce6457). Luego pm-planificacion agrega el paquete 3.7 a la WBS: base 142.500, BAC 169.500, reserva remanente 10.500.
  - Cómo verificarlo: abrir `issues.csv`, `cambios.csv` y `decisiones.csv` en un editor o Excel; abrir la solicitud y el traspaso; o escribir "Mostrame los cambios aprobados".
- **Decisión humana:** la junta aprueba C-001 con Laura como decisora. El agente nunca decide un cambio.

### 33. `pm-knowledge` — una pregunta de método
- **Prompt del usuario:** "¿Quién puede aprobar un cambio que consume reserva de gestión, y para qué está la autoridad de cambio?"
- **Quién:** orquestador en el hilo principal → `pm-knowledge`.
- **Qué pregunta o verifica:** clasifica la pregunta (método PRINCE2 con una convención del paquete); localiza la sección con `grep` y lee solo esa.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  grep -n '^### 3\.' "$PM/pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md"
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna: la pregunta va en el prompt y la respuesta sale de las referencias del paquete.
- **Salidas (qué queda y dónde verificarlo):** ninguna: no queda nada escrito. Respuesta en palabras propias: la autoridad de cambio decide dentro de su umbral y presupuesto de cambio; por encima, o si se toca la reserva de gestión, decide la junta (SPEC §1.10.6: la reserva de gestión queda fuera del BAC y solo la libera la junta). Cita archivo y encabezado, que el usuario puede abrir en `skills/pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md`.
- **Decisión humana:** ninguna. Si el usuario pidiera "entonces aprobalo", la petición pasa a pm-director vía el orquestador.

---

## Parte 4 · Límite de etapa (SB)

### 34. `pm-lecciones-aprendidas` — taller de la etapa 2
- **Prompt del usuario:** "Facilitá el taller de lecciones de la etapa 2 con estrella de mar y registrá que el proveedor no tenía entorno de pruebas del core."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Formato estrella de mar; facilita Andrea Costa."
  2. Andrea Costa, aseguramiento: "Confirmo los responsables de las acciones."
  3. Laura Méndez, ejecutiva: "Apruebo el informe de lecciones de la etapa 2 y elevo L-002 a la organización."
- **Quién:** orquestador → `pm-control` (en SB) → `pm-lecciones-aprendidas`.
- **Qué pregunta o verifica:** acciones del taller anterior; formato y facilitador declarados (ambiente sin culpas); 1–3 acciones con dueño y fecha; aciertos además de problemas; si alguien pide "la retro del sprint", eso es de pm-agil-hibrido.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion agregar lecciones --campo etapa=2 \
      --campo situacion="El proveedor no tenía entorno de pruebas del core bancario" \
      --campo efecto="R-001 se materializó parcialmente; cinco días de atraso" \
      --campo recomendacion="Incluir el entorno de pruebas como condición contractual del primer hito" \
      --campo prioridad=alta --campo responsable_seguimiento="Martín Suárez" --campo notas="R-001; impacto_organizacional=si"
  python3 $E/registro.py --proyecto gestion listar lecciones --abiertos
  ```
- **Entradas (qué aporta el usuario y cómo):**
  - Formato, facilitador y aportes del taller: el usuario los escribe en el chat (o llegan como acta de pm-reuniones en `gestion/03-control/reuniones/`).
  - La lección del entorno de pruebas: escrita en el prompt.
- **Salidas (qué queda y dónde verificarlo):**
  - L-002 en `gestion/03-control/registros/lecciones.csv`.
  - `gestion/03-control/reportes/2027-02-12-retrospectiva-etapa-2.md` y `gestion/03-control/reportes/2027-02-12-informe-lecciones-etapa-2.md` (`artefactos.informe-lecciones-etapa-2`, `aprobado` tras la decisión).
  - Cómo verificarlo: abrir los dos informes; abrir `lecciones.csv`; o escribir "Mostrame las lecciones abiertas".
- **Decisión humana:** aseguramiento confirma responsables y la junta revisa; luego pm-director ejecuta `estado.py aprobar informe-lecciones-etapa-2 --por "Ejecutivo: Laura Méndez"`. Elevar L-002 a la organización lo decide la ejecutiva.

### 35. `pm-plan-etapa-y-limites` — cerrar la etapa 2 y planificar la 3
- **Prompt del usuario:** "Cerrá la etapa 2: informe de fin de etapa, plan de la etapa 3, y verificá si cambió el PRD."
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva, por la junta: "Aprobamos la etapa 3 “Release 2 y transición” hasta el 26 de abril de 2027, con las tolerancias de etapa del plan."
- **Quién:** orquestador → `pm-control` (`limite-etapa`) + `pm-planificacion` → `pm-plan-etapa-y-limites`; luego `pm-director`.
- **Qué pregunta o verifica:** reales y pronósticos contra tolerancias; business case actualizado (vía pm-caso-de-negocio); lecciones incorporadas al plan siguiente; especificación antes de la puerta; traspasos pendientes; gate de sprint planning de BMAD como insumo.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion limite-etapa                     # CS → SB (pm-control)
  python3 $E/especificacion.py --proyecto gestion resumen
  python3 $B --proyecto gestion verificar
  python3 $B --proyecto gestion avance
  python3 $O gestion/00-direccion/okr.csv --corte 2027-02-12 --markdown gestion/03-control/reportes/2027-02-12-okr.md
  python3 $E/estado.py --proyecto gestion artefacto informe-fin-etapa-2 \
      --ruta 03-control/reportes/2027-02-12-informe-fin-etapa-2.md --estado en-revision
  python3 $E/estado.py --proyecto gestion artefacto plan-etapa-3 --ruta 02-planificacion/plan-etapa-3.md --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: reales, registros, lecciones y OKR ya están en la carpeta; el PRD y el gate de sprint planning se leen de BMAD por el puente. La decisión llega como respuesta de la junta.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/estado.json`: `proceso_actual` = `SB` tras `limite-etapa`; tras la puerta, `CS`, etapa 3, con la puerta en `puertas[]` y `tolerancias.etapa` nuevas.
  - `gestion/03-control/reportes/2027-02-12-informe-fin-etapa-2.md` (`en-revision`; avance 16/21 puntos = 76,2 %, épicas 1/2, sin desvíos), `gestion/02-planificacion/plan-etapa-3.md` (`en-revision`; BAC de etapa 74.500), `gestion/03-control/reportes/2027-02-12-okr.md`, solicitud `gestion/00-direccion/decisiones/2027-02-12-solicitud-autorizar-etapa.md`.
  - Cómo verificarlo: abrir el informe, el plan y la solicitud; o escribir "¿Dónde estamos?" (atajo `/pm-method:pm-estado`).
- **Decisión humana:** la junta decide `autorizar-etapa`; pm-director registra `estado.py puerta autorizar-etapa --decision aprobado --por "Ejecutivo: Laura Méndez" --etapa-nombre "Release 2 y transición" --fin 2027-04-26` y las tolerancias de la etapa 3. Pasa a CS, etapa 3.

### 36. `pm-exportar` — paquete de puerta y Excel
- **Prompt del usuario:** "Armá el paquete de puerta para autorizar la etapa 3 y exportá los registros a Excel para la junta del jueves."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Confirmo; mandale el paquete y el Excel a la junta."
- **Quién:** orquestador → `pm-director` (preparación de puerta) → `pm-exportar`.
- **Qué pregunta o verifica:** obligatorios de la puerta (faltante o borrador = ZIP `-BORRADOR`); solicitud incluida; estado de cada fuente; que la hoja de stakeholders con valoraciones no vaya en paquetes para terceros.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $X --proyecto gestion listar puerta autorizar-etapa
  python3 $X --proyecto gestion puerta autorizar-etapa \
      --extra 02-planificacion/especificacion/matriz-trazabilidad-bmad.csv 00-direccion/historial/bmad-prd-v1.1/prd.md
  python3 $E/exportar.py xlsx --proyecto gestion --salida gestion/exportados/2027-02-12-registros-v1.xlsx
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: los artefactos de la puerta y los registros ya están en la carpeta; los extras (`matriz-trazabilidad-bmad.csv` y la línea base del PRD) los suma el sistema.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/exportados/2027-02-12-paquete-autorizar-etapa-v1.zip` con `MANIFIESTO.md` (con un obligatorio faltante o en borrador saldría con sufijo `-BORRADOR`).
  - `gestion/exportados/2027-02-12-registros-v1.xlsx` (una hoja por registro).
  - Nota en `gestion/03-control/registros/diario.md`.
  - Cómo verificarlo: abrir el ZIP y leer el `MANIFIESTO.md`; abrir el Excel. Son copias: la fuente de verdad sigue en la carpeta.
- **Decisión humana:** el usuario confirma antes de enviar o subir los archivos; el envío lo hace pm-comunicacion-stakeholders, con un conector o por la capa de canales (`envios.py`, con aprobación y `--confirmar`; caso 44).

---

## Parte 5 · Cierre (CP)

### 37. `pm-cierre-proyecto` — cierre planificado
- **Prompt del usuario:** "Estamos terminando la etapa 3: prepará el cierre y decime qué falta aceptar."
- **Respuestas del usuario:**
  1. Sofía Ramírez, usuaria sénior: "Acepto los productos según el registro de aceptación."
  2. Laura Méndez, ejecutiva: "Confirmo la aceptación."
  3. Laura Méndez, ejecutiva, por la junta: "Autorizamos el cierre del proyecto."
- **Quién:** orquestador → `pm-cierre` → `pm-cierre-proyecto` (con pm-bmad-puente, pm-caso-de-negocio, pm-lecciones-aprendidas, pm-adquisiciones); luego `pm-director`.
- **Qué pregunta o verifica:** aceptación por requisito con la fachada; con BMAD, `verificar` limpio y sin traspasos pendientes (el desvío de épicas por FR-4 y FR-5 se trató como elaboración progresiva, I-004, y nueva línea base de épicas 1.1); handover con propietario de operación; beneficios pendientes con dueño y fecha; contratos con sus tres condiciones; variaciones contra el PID y el business case v1.0.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/estado.py --proyecto gestion cierre
  python3 $E/especificacion.py --proyecto gestion listar requisitos
  python3 $B --proyecto gestion verificar
  python3 $E/evm.py --pv 169500 --ev 169500 --ac 171000 --bac 169500 --tol-costo 8
  python3 $E/registro.py --proyecto gestion resumen --corte 2027-04-30
  python3 $X --proyecto gestion listar cierre
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: la cobertura por requisito se lee por la fachada y BMAD por el puente; reales y registros ya están en la carpeta. Las aceptaciones y la decisión de cierre llegan como respuestas.
- **Salidas (qué queda y dónde verificarlo):**
  - En `gestion/04-cierre/`: `registro-aceptacion.md` (FR-1 a FR-5 aceptados; NFR-1 con concesión), `handover.md`, `recomendaciones-seguimiento.md`, `plan-revision-beneficios.md` (B-01 medido el 2027-07-26 y el 2027-10-26; B-02 el 2027-11-30), `informe-lecciones.md`, `informe-fin-proyecto.md` (CPI 0,991, SPI 1,00, VAC −1.500), `notificacion-cierre.md` en borrador.
  - `gestion/estado.json`: `artefactos.registro-aceptacion` en `aprobado`; puerta `autorizar-cierre` en `puertas[]`; `fase` = `cerrado`.
  - Cómo verificarlo: abrir los archivos de `gestion/04-cierre/`; o escribir "¿Qué sigue?" (atajo `/pm-method:pm-estado`), que recuerda las revisiones de beneficios.
- **Decisión humana:** dos puertas. Aceptación: Sofía acepta y Laura confirma; pm-director ejecuta `estado.py aprobar registro-aceptacion --por "Usuario sénior: Sofía Ramírez; Ejecutivo: Laura Méndez"`. Cierre: la junta autoriza y pm-director registra `estado.py puerta autorizar-cierre --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-05-07`; la fase pasa a `cerrado` y `siguiente` recuerda las revisiones de beneficios. La notificación la firma la ejecutiva y se envía con confirmación (por ejemplo, por la capa de canales con `envios.py nuevo --origen 04-cierre/notificacion-cierre.md --proposito comunicado`; caso 44). El ZIP de cierre sale con `python3 $X --proyecto gestion cierre`.

---

## Parte 6 · Maestro de interesados, comunicación por canales, OKR, identificación de riesgos, controles permanentes y mapas (transversal)

Estos casos atraviesan el ciclo: el maestro de interesados se arma en SU e IP, se mantiene en cada etapa (CS) y se revisa en cada límite (SB). Los datos son los de la corrida de referencia de la guía [E2E-3](guias/E2E-3-interesados-okr-avance.md) (evidencia en [salida-g3.md](guias/evidencia/salida-g3.md)): diez interesados ST-001…ST-010, entre ellos Laura Méndez (ST-001), el Consejo directivo (ST-002), Sofía Ramírez (ST-003), el Sindicato de operadores (ST-004, confidencial), los socios piloto (ST-005), TI del núcleo (ST-006), la Unidad de cumplimiento (ST-007), Diego Ferreira (ST-008), Martín Suárez (ST-009) y Lucía Benítez (ST-010). Donde un caso muestra una salida que no está en esa evidencia, se aclara que viene de una corrida complementaria del 2026-10-17 sobre la misma carpeta, con los scripts del paquete. El maestro (`stakeholders.csv`) es la única fuente de personas: OKR, RACI, preferencias, envíos y registros lo citan por `ST-###` o por el nombre exacto. Nada de esto es asesoramiento jurídico; los límites de privacidad están en la guía de `pm-interesados` §10.

### 38. `pm-interesados` — matriz poder/interés y estrategia por cuadrante
- **Prompt del usuario:** "Ubicá a los interesados en la matriz poder/interés y decime la estrategia para cada cuadrante. Hacé el análisis de interesados (restringido)." Después: "¿Y si los «medio» cuentan como bajo?"
- **Respuestas del usuario:**
  1. Martín Suárez, gestor (si pregunta quién validó las valoraciones): "Las revisé con Laura; registralas."
- **Quién:** orquestador → `pm-inicio` → `pm-interesados` (plantilla `templates/analisis-stakeholders.md`).
- **Qué pregunta o verifica:** que cada interesado tenga poder e interés (si falta alguno, aviso STK-01 y no se ubica); poder es la autoridad real (aprobar presupuestos, asignar recursos, vetar decisiones) e interés, el involucramiento, la preocupación o el impacto que el proyecto le genera. Un valor «medio» se ubica del lado alto por convención del paquete y se marca como frontera (◇); `--medio bajo` aplica la convención contraria. Las valoraciones (actitud, compromiso) son de circulación restringida.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $I --proyecto gestion matriz
  python3 $I --proyecto gestion --medio bajo matriz          # la pregunta de seguimiento
  python3 $E/estado.py --proyecto gestion artefacto analisis-stakeholders \
      --ruta 01-inicio/analisis-stakeholders.md --estado en-revision
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: los diez interesados ya están en `gestion/03-control/registros/stakeholders.csv` con poder, interés, actitud, compromiso actual y deseado, canal, frecuencia, responsable de la relación y correo (guía E2E-3, paso 2). La pregunta de seguimiento va en el prompt.
- **Salidas (qué queda y dónde verificarlo):**
  - En la respuesta, la matriz con su estrategia (salida real):
    ```text
    Gestionar de cerca (7): ST-001 Laura Méndez, ST-002 Consejo directivo ◇, ST-003 Sofía Ramírez, ST-004 Sindicato de operadores ◇, ST-006 Área de TI del núcleo operativo ◇, ST-008 Diego Ferreira ◇, ST-009 Martín Suárez ◇
       Los actores más críticos: comunicación constante, participación activa en las decisiones y máxima atención.
    Mantener satisfecho (1): ST-007 Unidad de cumplimiento
       No abrumar con detalles; reportes ejecutivos de alto nivel sobre beneficios y avance.
    Mantener informado (2): ST-005 Socios usuarios piloto, ST-010 Lucía Benítez
       Canales claros (boletines, reuniones informativas) y escucha activa de su retroalimentación: suelen ser aliados y fuente de información.
    Monitorear (0): —
       Supervisar con el menor esfuerzo, sin gastar recursos innecesarios, salvo que cambien de posición en la matriz.
    ◇ = frontera ('medio' ubicado como alto)
    ```
  - Con `--medio bajo` (corrida complementaria): gestionar de cerca 2 (ST-001, ST-003); mantener satisfecho 3 (ST-002 ◇, ST-006 ◇, ST-007); mantener informado 5 (ST-004 ◇, ST-005, ST-008 ◇, ST-009 ◇, ST-010); monitorear 0.
  - Cada cuadrante trae además un perfil de comunicación por defecto que se usa si nada más lo define: gestionar de cerca = reunión · conclusión primero · resumen · semanal; mantener satisfecho = correo · conclusión primero · ejecutivo · mensual; mantener informado = correo · lista · resumen · quincenal; monitorear = tablero · lista · ejecutivo · a demanda.
  - `gestion/01-inicio/analisis-stakeholders.md` (`en-revision`, circulación restringida; `artefactos.analisis-stakeholders`). Con `matriz --markdown <archivo>` la tabla queda también en un Markdown.
  - Cómo verificarlo: abrir el análisis; escribir "¿En qué cuadrante está el sindicato y qué estrategia le corresponde?"; la matriz dibujada aparece en el reporte del caso 46.
- **Decisión humana:** el gestor valida las valoraciones antes de registrarlas y decide qué convención usar para los «medio»; el análisis no se comparte fuera de la junta.

### 39. `pm-interesados` — estereotipos semilla y asignación
- **Prompt del usuario:** "Cargá los estereotipos de audiencia y asigná: Laura y el Consejo a dirección-patrocinador, Sofía a product owner y usuarios clave, el panel a cliente-usuario, cumplimiento a regulador-comunidad, Diego a proveedores, Martín y Lucía a equipo." Más adelante: "¿Sugerís estereotipo para los que quedaron sin asignar?"
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "No los asignes: el sindicato y TI quedan sin estereotipo; su perfil sale del cuadrante y de sus preferencias."
- **Quién:** orquestador → `pm-inicio` → `pm-interesados`.
- **Qué pregunta o verifica:** la semilla solo se carga en un catálogo vacío (si `estereotipos.csv` ya tiene filas, lo rechaza); cada asignación cita un estereotipo existente (el registro valida la referencia); las sugerencias de `--sugerir` no se aplican solas.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $I --proyecto gestion estereotipos --semilla
  python3 $E/registro.py --proyecto gestion actualizar stakeholders ST-001 --campo estereotipo=ET-001
  # … ST-002 → ET-001, ST-003 → ET-006, ST-005 → ET-003, ST-007 → ET-005, ST-008 → ET-004, ST-009 y ST-010 → ET-002
  python3 $I --proyecto gestion estereotipos
  python3 $I --proyecto gestion estereotipos --sugerir
  ```
- **Entradas (qué aporta el usuario y cómo):** las asignaciones, escritas en el prompt. Los seis estereotipos semilla salen de la guía de `pm-comunicacion-stakeholders` §1; se ajustan después con `registro.py actualizar estereotipos …`.
- **Salidas (qué queda y dónde verificarlo):**
  - `gestion/03-control/registros/estereotipos.csv` (registro opcional, se crea al primer uso) con ET-001…ET-006. Salida real tras las asignaciones:
    ```text
    ET-001 direccion-patrocinador [activo] gestionar-de-cerca · reunion · conclusion-primero · ejecutivo · por-hito → ST-001, ST-002
    ET-002 equipo [activo] mantener-informado ·  · lista · detallado · semanal → ST-009, ST-010
    ET-003 cliente-usuario [activo] mantener-informado · correo · narrativa · resumen · quincenal → ST-005
    ET-004 proveedores [activo] mantener-satisfecho · correo · lista · resumen · por-hito → ST-008
    ET-005 regulador-comunidad [activo] mantener-satisfecho · correo · conclusion-primero · ejecutivo · por-hito → ST-007
    ET-006 product-owner-usuarios-clave [activo] gestionar-de-cerca · reunion · datos · detallado · semanal → ST-003
    ```
  - Columna `estereotipo` de `stakeholders.csv`. Un estereotipo inexistente se rechaza: `Integridad referencial: - estereotipo='ET-009' no existe en estereotipos.csv` (corrida complementaria).
  - `--sugerir` (corrida complementaria, al final del recorrido): "Asignar ST-004 → ET-001 direccion-patrocinador (3 coincidencias)", lo mismo para ST-006, y "Las sugerencias no se aplican solas: el gestor decide."
  - Cómo verificarlo: abrir `estereotipos.csv` y `stakeholders.csv` en un editor o Excel; escribir "¿Qué estereotipo tiene cada interesado?".
- **Decisión humana:** el gestor decide cada asignación y cualquier ajuste del catálogo; un estereotipo que ya no se usa se marca retirado (si alguien lo sigue citando, aviso STK-03).

### 40. `pm-interesados` — preferencias declaradas en una entrevista y su confirmación
- **Prompt del usuario:** "Entrevisté a Laura (3/11): «Prefiero que el avance me llegue por correo, no por chat», «Una página, con la conclusión y lo que tengo que decidir arriba», «Los lunes antes de las 9 lo leo con calma». Registrá sus preferencias y mostrame su perfil de comunicación."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Sí, Laura aceptó que se registren; confirmalas como Martín Suárez, gestor."
- **Quién:** orquestador → `pm-inicio` → `pm-interesados` (plantilla `templates/entrevista-interesado.md`).
- **Qué pregunta o verifica:** que la persona aceptó que se registren sus preferencias; que cada una tenga la cita textual (evidencia), la fuente, la procedencia (`declarado`, `observado` o `inferido`) y una vigencia (por defecto 180 días); que el interesado exista en el maestro. No infiere emociones, personalidad ni datos sensibles: el perfil solo adapta comunicaciones. Mientras una preferencia no esté confirmada, no se aplica.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion agregar preferencias --campo fecha=2026-11-03 --campo stakeholder_id=ST-001 \
      --campo dimension=canal --campo valor=correo --campo procedencia=declarado \
      --campo evidencia="«Prefiero que el avance me llegue por correo, no por chat.»" \
      --campo fuente=01-inicio/entrevistas/2026-11-03-laura-mendez.md --campo vigencia_hasta=2027-05-02
  # … formato=conclusion-primero, nivel_detalle=ejecutivo y horario="antes de las 9", con su cita → PF-002…PF-004
  python3 $I --proyecto gestion confirmar PF-001 PF-002 PF-003 PF-004 --por "Gestor: Martín Suárez"
  python3 $I --proyecto gestion perfil ST-001 --corte 2026-11-03
  ```
- **Entradas (qué aporta el usuario y cómo):** las citas de la entrevista, escritas en el prompt (o la nota de la entrevista adjunta en la sesión); el sistema guarda la entrevista en `gestion/01-inicio/entrevistas/2026-11-03-laura-mendez.md` (restringida). El consentimiento y la confirmación llegan como respuesta al orquestador.
- **Salidas (qué queda y dónde verificarlo):**
  - PF-001…PF-004 en `gestion/03-control/registros/preferencias.csv` (registro opcional), en estado `confirmada`, con `confirmado_por` = "Gestor: Martín Suárez" y `vigencia_hasta` = 2027-05-02.
  - El perfil resuelto, con la procedencia de cada valor (salida real):
    ```text
    ST-001 Laura Méndez · gestionar-de-cerca · estereotipo ET-001 · destino laura.mendez@example.org
       canal: correo  (PF-001 (declarado, 2026-11-03))
       formato: conclusion-primero  (PF-002 (declarado, 2026-11-03))
       nivel_detalle: ejecutivo  (PF-003 (declarado, 2026-11-03))
       frecuencia: quincenal  (matriz de comunicaciones)
       idioma: es  (idioma del proyecto)
       registro: formal  (estereotipo:ET-001)
       horario: antes de las 9  (PF-004 (declarado, 2026-11-03))
       estilo_decision: datos  (estereotipo:ET-001)
    ```
  - Precedencia: cuadrante → idioma del proyecto → estereotipo → matriz de comunicaciones → preferencias confirmadas y vigentes. Las propuestas y las vencidas no se aplican.
  - Cómo verificarlo: abrir `preferencias.csv` (columnas `evidencia`, `fuente`, `vigencia_hasta`, `confirmado_por`); escribir "¿Cómo le tengo que escribir a Laura?".
- **Decisión humana:** el gestor confirma cada preferencia con la persona (`confirmar … --por`). Si una preferencia confirmada vence o queda sin `confirmado_por`, la integridad avisa STK-04 y se vuelve a validar con la persona.

### 41. `pm-interesados` — preferencias propuestas desde la transcripción de una reunión
- **Prompt del usuario:** "Procesá la transcripción del taller de la bandeja del 19/11: armá el acta con decisiones y acciones. El «Delegado sindical» es el Sindicato de operadores. Proponé las preferencias de comunicación que cada uno pidió." (la transcripción, exportada en VTT, guardada en `gestion/03-control/reuniones/2026-11-19-taller-bandeja-original.vtt`)
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Sí, las validé con Sofía y con el delegado; confirmalas como Martín Suárez."
  2. Martín Suárez, gestor (cuando avisa que la frecuencia del sindicato difiere de la matriz): "Actualizá la matriz a quincenal."
- **Quién:** orquestador → `pm-control` → `pm-reuniones` (transcripción y acta) → `pm-interesados` (propuesta y confirmación de preferencias).
- **Qué pregunta o verifica:** analiza solo oraciones en primera persona y guarda la cita con su marca de tiempo; asocia hablantes por nombre exacto o por `--mapa` (los que no puede asociar los lista); no infiere emociones ni rasgos (la preocupación del delegado queda en el acta, no en su perfil); todo queda como `propuesta` hasta que el gestor lo confirme con la persona. El análisis es por patrones: cada propuesta se revisa antes de confirmar y lo que no corresponde se rechaza con `rechazar … --motivo`. Si una preferencia confirmada contradice la matriz de comunicaciones, el perfil lo avisa.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $T gestion/03-control/reuniones/2026-11-19-taller-bandeja-original.vtt \
      --salida gestion/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md
  python3 $I --proyecto gestion proponer --transcripcion gestion/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md \
      --mapa "Delegado sindical=ST-004" --fecha 2026-11-19 --registrar
  python3 $I --proyecto gestion confirmar PF-005 PF-006 PF-007 PF-008 --por "Gestor: Martín Suárez"
  python3 $I --proyecto gestion perfil ST-004 --corte 2026-11-19
  python3 $E/registro.py --proyecto gestion actualizar stakeholders ST-004 --campo frecuencia=quincenal
  ```
- **Entradas (qué aporta el usuario y cómo):** el archivo VTT, que el usuario deja en `gestion/03-control/reuniones/` o adjunta en la sesión (también sirven `.srt`, `.txt`, `.docx` o texto pegado); la correspondencia entre "Delegado sindical" y ST-004, escrita en el prompt; las confirmaciones, como respuestas.
- **Salidas (qué queda y dónde verificarlo):**
  - "5 intervenciones de 4 hablantes" en la transcripción normalizada; el acta, la decisión D-006 y la acción A-004 siguen el flujo de `pm-reuniones` del caso 24.
  - Propuestas (salida real):
    ```text
    PF-005 ST-003 canal=teams (declarado) "A mí mandame las novedades del proyecto por Teams." [00:00:01]
    PF-006 ST-004 canal=correo (declarado) "Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas." [00:00:10]
    PF-007 ST-004 nivel_detalle=ejecutivo (declarado) "Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas." [00:00:10]
    PF-008 ST-004 frecuencia=quincenal (declarado) "Prefiero que las novedades nos lleguen por correo, en un resumen corto, cada dos semanas." [00:00:10]
    Estado: propuesta. Nada se aplica hasta que el gestor confirme con la persona: interesados.py confirmar PF-… --por "Rol: Nombre".
    ```
  - Tras confirmar, el perfil del sindicato avisa: `AVISO frecuencia: la preferencia confirmada PF-008 (quincenal) difiere de la matriz aprobada (mensual); actualizar la matriz (pm-comunicacion-stakeholders)`; ST-004 queda con `frecuencia=quincenal`.
  - Rechazo (corrida complementaria, daily del 12/1 en la que Diego dijo «A mí escribime por Teams» sin confirmarlo después): `interesados.py rechazar PF-010 --por "Gestor: Martín Suárez" --motivo "Diego no lo confirmó: su canal sigue siendo el correo"` → `rechazar: PF-010`; la preferencia queda `rechazada` y no se aplica.
  - Cómo verificarlo: abrir `gestion/03-control/reuniones/2026-11-19-taller-bandeja-transcripcion.md`; abrir `preferencias.csv` (columna `evidencia` con la cita y la marca de tiempo; columna `estado`); escribir "¿Qué preferencias de comunicación están pendientes de confirmar?". Una propuesta sin tratar por más de 30 días aparece como STK-05 (INFO).
- **Decisión humana:** el gestor confirma o rechaza cada propuesta después de validarla con la persona; la actualización de la matriz la decide el gestor y la aprueba quien aprobó la matriz.

### 42. `pm-interesados` — RACI sobre épicas, requisitos, paquetes y KR (y el rechazo de un segundo A)
- **Prompt del usuario:** "Armá la RACI: épica E-1 (A Sofía, R Lucía, C TI, I Laura); épica E-3 (A Sofía, R Lucía, C sindicato y Diego); NFR-1 protección de datos (A cumplimiento, R Lucía, C Sofía); paquete 3.1 de la WBS (A Martín, R Lucía, I Sofía); KR-1.1 (A Laura, R Sofía, C panel de socios, I Consejo) y KR-2.2 (A Laura, R Sofía, I Consejo). Después intentá poner a Laura también como A de E-1. Mostrame quién participa en E-3 y verificá la integridad."
- **Quién:** orquestador → `pm-inicio` → `pm-interesados` (plantilla `templates/matriz-raci.md`).
- **Qué pregunta o verifica:** una fila por elemento × interesado; exactamente un A por elemento y al menos un R; interesados existentes en el maestro; el elemento existe en su fuente: épicas, requisitos e historias en la especificación (fachada de BMAD o `backlog.csv`), paquetes en `wbs.csv`, KR y objetivos en `okr.csv`, decisiones en `decisiones.csv`; un entregable en texto libre no se valida. El registro rechaza el segundo A, la fila duplicada y el interesado inexistente.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $E/registro.py --proyecto gestion agregar raci --campo elemento=E-1 --campo stakeholder_id=ST-003 --campo rol=A   # RC-001
  python3 $E/registro.py --proyecto gestion agregar raci --campo elemento=E-1 --campo stakeholder_id=ST-010 --campo rol=R   # RC-002
  # … una fila por elemento e interesado, hasta RC-021
  python3 $E/registro.py --proyecto gestion agregar raci --campo elemento=E-1 --campo stakeholder_id=ST-001 --campo rol=A   # se rechaza
  python3 $I --proyecto gestion raci --markdown gestion/02-planificacion/matriz-raci.md
  python3 $E/estado.py --proyecto gestion artefacto matriz-raci --ruta 02-planificacion/matriz-raci.md --estado en-revision
  python3 $I --proyecto gestion raci --elemento E-3
  python3 $I --proyecto gestion integridad
  ```
- **Entradas (qué aporta el usuario y cómo):** los roles por elemento, escritos en el prompt; los títulos de cada elemento salen de su fuente (la épica y el requisito, de la especificación de BMAD por la fachada en solo lectura; el paquete, de `wbs.csv`; el KR, de `okr.csv`).
- **Salidas (qué queda y dónde verificarlo):**
  - RC-001…RC-021 en `gestion/03-control/registros/raci.csv` (registro opcional). El segundo A se rechaza (salida real):
    ```text
    Integridad referencial:
      - duplicado elemento=E-1 + stakeholder_id=ST-001 (una fila por combinación: actualizar la existente)
      - elemento E-1 ya tiene un 'A' (exactamente uno: cambiar primero la otra fila)
    ```
  - `gestion/02-planificacion/matriz-raci.md` (`en-revision`; `artefactos.matriz-raci`):

    | Elemento | Descripción | Laura | Consejo | Sofía | Sindicato | Socios | TI | Cumplimiento | Diego | Martín | Lucía |
    |---|---|---|---|---|---|---|---|---|---|---|---|
    | E-1 | Acceso seguro y consulta de mis productos | I | | A | | | C | | | | R |
    | E-3 | Consola de operador | | | A | C | | | | C | | R |
    | NFR-1 | Seguridad y privacidad (Ley 18.331) | | | C | | | | A | | | R |
    | 3.1 | Acceso seguro (WBS) | | | I | | | | | | A | R |
    | KR-1.1 | 30 % de socios registrados | A | I | R | | C | | | | | |
    | KR-2.2 | Más del 90 % de solicitudes completas | A | I | R | | | | | | | |

    y las líneas "RACI válida: un A por elemento, al menos un R, referencias existentes." e "Integridad referencial y calidad del maestro: sin hallazgos.".
  - `raci --elemento E-3`: A ST-003 Sofía Ramírez · R ST-010 Lucía Benítez · C ST-004 Sindicato de operadores · C ST-008 Diego Ferreira.
  - Con la RACI cargada, la verificación de `autorizar-proyecto` ya no muestra el aviso P-10 (sin RACI).
  - Cómo verificarlo: abrir `raci.csv` en un editor o Excel y `matriz-raci.md`; escribir "¿Quién aprueba la consola de operador?".
- **Decisión humana:** la RACI se aprueba con el PID en `autorizar-proyecto` (registra pm-director). Para cambiar el aprobador de un elemento primero se actualiza la fila del A vigente.

### 43. `pm-interesados` — perfil de comunicación y vínculos de un interesado
- **Prompt del usuario:** "¿Cómo le tengo que escribir a Sofía y dónde aparece en el proyecto?"
- **Quién:** orquestador → `pm-control` (o el hilo principal) → `pm-interesados`.
- **Qué pregunta o verifica:** resuelve el perfil con la precedencia del caso 40 a la fecha de corte; busca al interesado por id o por nombre exacto en RACI, OKR (responsables y KR), riesgos, acciones, decisiones, preferencias y envíos.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $I --proyecto gestion perfil ST-003 --corte 2027-01-15
  python3 $I --proyecto gestion vinculos ST-003
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna: el nombre va en el prompt y el resto sale del maestro y de los registros.
- **Salidas (qué queda y dónde verificarlo):**
  - Ninguna en disco. En la respuesta (salida real, al 15/1):
    ```text
    ST-003 Sofía Ramírez · gestionar-de-cerca · estereotipo ET-006 · destino sofia.ramirez@example.org
       canal: teams  (PF-005 (declarado, 2026-11-19))
       formato: datos  (estereotipo:ET-006)
       nivel_detalle: detallado  (estereotipo:ET-006)
       frecuencia: quincenal  (matriz de comunicaciones)
       idioma: es  (idioma del proyecto)
       registro: neutral  (estereotipo:ET-006)
       estilo_decision: datos  (estereotipo:ET-006)
    ```
  - Vínculos de Sofía: A en E-1 y E-3, C en NFR-1, I en 3.1, R en KR-1.1 y KR-2.2; responsable de KR-1.1…KR-2.3; R-001 (propietaria); A-001 y A-002; D-006; PF-005 (confirmada); EN-006 (Teams, 15/1).
  - Con `perfil todos` sale el perfil de los diez; con `--json`, la misma información para otras herramientas.
  - Cómo verificarlo: leer la respuesta; comparar con `raci.csv`, `okr.csv` y `envios.csv`.
- **Decisión humana:** ninguna.

### 44. `pm-comunicacion-stakeholders` — comunicado personalizado: plan de envío, aprobación, simulación y envío por canales
- **Prompt del usuario:** "Prepará el comunicado del avance al 8/1 para todos los de «gestionar de cerca» y «mantener satisfecho» (menos yo, Martín), adaptado al perfil de cada uno, con la decisión pendiente para la junta. Agrupá a quienes comparten perfil. Mostrame los borradores; si los apruebo, mandalos por correo y por Teams y registrá la entrega en la reunión técnica."
- **Respuestas del usuario:**
  1. Martín Suárez, gestor: "Sí, aprobados por Martín Suárez, gestor."
  2. Martín Suárez, gestor: "Sí, enviá." (con las variables de entorno del servidor o un conector conectado; sin ninguno: "Generá los .eml")
- **Quién:** orquestador → `pm-control` → `pm-comunicacion-stakeholders` (contenido y plan de envío, con `pm-interesados`) → `pm-integraciones` (capa de canales, `envios.py`).
- **Qué pregunta o verifica:** la audiencia se resuelve contra el maestro (`todos`, `ST-001`, `cuadrante:<c>`, `estereotipo:ET-001`, `raci:<elemento>:<roles>`, `rol:<texto>`, `-ST-009` para excluir); una audiencia inválida no crea nada. Un borrador por destinatario o por grupo con el mismo perfil, con el perfil en el frontmatter. Nada sale sin (1) mensaje aprobado con `aprobado_por` y (2) `--confirmar`: sin `--confirmar` todo es simulación. Los destinos se toman del maestro en el momento de enviar; un reenvío solo alcanza a quien todavía no recibió. Credenciales solo por variables de entorno (INSTALACION §0.7, "Capa de canales"); nunca en archivos ni en el chat.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $I --proyecto gestion plan-envio --tema "Avance del portal al 8 de enero" \
      --audiencia "cuadrante:gestionar-de-cerca,cuadrante:mantener-satisfecho,-ST-009" --proposito informe \
      --base gestion/03-control/reportes/2027-01-15-comunicado-consejo.md --agrupar --fecha 2027-01-15
  C=gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero
  python3 $V --proyecto gestion estado $C
  # el modelo adapta cada borrador a su perfil; luego, con la aprobación del gestor:
  python3 $V --proyecto gestion aprobar $C --por "Gestor: Martín Suárez"
  python3 $V --proyecto gestion enviar $C --modo smtp                          # simulación
  python3 $V --proyecto gestion enviar $C --modo smtp --confirmar --fecha 2027-01-15
  python3 $V --proyecto gestion enviar $C --modo teams-webhook --confirmar --fecha 2027-01-15
  python3 $V --proyecto gestion registrar $C --mensaje mensaje-04-reunion-st-006.md --modo manual \
      --referencia "reunión técnica del 2027-01-18" --fecha 2027-01-18
  python3 $V --proyecto gestion historial
  ```
- **Entradas (qué aporta el usuario y cómo):** la audiencia y la intención, en el prompt; el contenido base, redactado por la skill en `gestion/03-control/reportes/2027-01-15-comunicado-consejo.md`; los destinos (`correo`, `usuario_chat`) y perfiles, del maestro; las credenciales, solo como variables de entorno de la terminal del usuario (`PM_SMTP_HOST`, `PM_SMTP_REMITENTE` y opcionales; `PM_TEAMS_WEBHOOK_URL`; `PM_SLACK_WEBHOOK_URL`).
- **Salidas (qué queda y dónde verificarlo):**
  - Plan (salida real): "Plan de envío → 03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero/ (7 destinatarios, 5 mensajes en borrador)", con el aviso "AVISO ST-006 Área de TI del núcleo operativo: canal preferido «reunion» no es electrónico: entregarlo por esa vía y registrarlo con envios.py registrar --modo manual".
  - Simulación (salida real, recortada): `SIMULACIÓN mensaje-01-correo-st-001-st-002-st-007.md [smtp] → ST-001 <laura.mendez@example.org>, ST-002 <consejo@example.org>, ST-007 <cumplimiento@example.org> · «Avance del portal al 8 de enero»`, el comienzo del texto, "(faltan variables de entorno: PM_SMTP_HOST, PM_SMTP_REMITENTE)" y "Resumen: 0 enviados, 0 fallidos, 3 simulados, 2 omitidos · simulación: agregar --confirmar para enviar".
  - Envío: correo "Resumen: 5 enviados, 0 fallidos, 0 simulados, 2 omitidos" (EN-001…EN-005); Teams "mensaje-02-teams-st-003.md: enviado · EN-006"; entrega en la reunión técnica registrada a mano, EN-007. En la corrida de referencia el correo y Teams llegaron a servidores de prueba en 127.0.0.1; con las variables del usuario salen a su servidor.

    | Mensaje | Para | Canal | Perfil aplicado | Resultado |
    |---|---|---|---|---|
    | mensaje-01 | ST-001, ST-002, ST-007 | correo | conclusión primero · ejecutivo · formal | EN-001…EN-003 enviados |
    | mensaje-02 | ST-003 | teams | datos · detallado | EN-006 enviado |
    | mensaje-03 | ST-004 | correo | conclusión primero · ejecutivo (su preferencia) | EN-004 enviado |
    | mensaje-04 | ST-006 | reunión (no electrónico) | — | EN-007 registrado a mano |
    | mensaje-05 | ST-008 | correo | lista · resumen | EN-005 enviado |

  - Otras vías (corrida complementaria): `--modo eml --confirmar` deja un `.eml` por destinatario en `<carpeta>/eml/` (cabecera `X-Unsent: 1`), registrado como pendiente hasta `registrar --modo eml`; con un conector MCP de correo, Slack o Teams: `preparar-mcp` → envío con la herramienta tras la vista previa → `registrar --modo mcp --referencia <id>`. Detalle de cada modo en [CASOS-DE-USO-INTEGRACIONES caso 8](CASOS-DE-USO-INTEGRACIONES.md). El mismo flujo sirve para informes, actas, recordatorios, convocatorias, decisiones de puerta y OKR (`envios.py nuevo --origen <archivo> --proposito …`).
  - Cómo verificarlo: abrir la carpeta `gestion/03-control/comunicaciones/2027-01-15-avance-del-portal-al-8-de-enero/` (borradores aprobados y `plan-envio.csv`); abrir `gestion/03-control/registros/envios.csv` (EN-001…EN-007, con `confirmado_por`) y `diario.md`; escribir "¿Qué le enviamos al sindicato y cuándo?".
- **Decisión humana:** el gestor aprueba los borradores (acto humano con nombre y rol) y confirma el envío; sin `--confirmar` no sale nada. Un envío fallido deja código de salida 2 y aviso STK-07 hasta que se reintenta.

### 45. `pm-okr` — OKR: tipos de KR, check-ins, salud y propuesta de sincronización con Tability
- **Prompt del usuario:**
  1. "Definí los OKR del proyecto ligados al business case (B-01, B-02, B-03) y a las métricas de éxito del PRD. Laura es la dueña de los objetivos y Sofía de los KR. Ciclo 2027, desde el 2/11. O-1 aspiracional (KR-1.1 30 % de socios registrados, pesa el doble, en Tability es kr-registro-portal; KR-1.2 bajar de 5.000 a 3.500 consultas); O-2 comprometido (KR-2.1 mantener la respuesta por debajo de 48 h; KR-2.2 más del 90 % de solicitudes completas; KR-2.3 la bandeja en producción para el 12/3 con las iniciativas de las historias 3-1, 3-2 y 3-3). Calculá el puntaje al 20/11."
  2. "Check-ins de Sofía: 11/12 KR-1.1 1 % (confianza 7), KR-1.2 4.950 (6), KR-2.1 92 h (4), KR-2.2 64 % (6); 23/12 …; 8/1 3 %, 4.800, 80 h (5), 72 %."
  3. "¿Cómo van los OKR al 8/1? Decime qué check-ins habría que publicar en Tability."
- **Respuestas del usuario:**
  1. Con el conector de Tability conectado: "Sí, publicá el del 8/1 de KR-1.1." Sin conector: "No, solo mostrame la propuesta."
- **Quién:** orquestador → `pm-inicio` (redacción) y `pm-control` (check-ins) → `pm-okr`; la publicación, vía `pm-integraciones`.
- **Qué pregunta o verifica:** tipos de KR (`de-a` por defecto, `mantener-sobre`, `mantener-bajo`, `binario`, `hito`), compromiso (`aspiracional` por defecto o `comprometido`), peso, iniciativas IN-n ligadas a un KR y a una épica, historia o paquete; responsables del maestro (si no figuran, aviso de `okr.py` y STK-08); vínculo a B-n, SM-n u OBJ-n (la sanidad valida su existencia: ESP-04 y ESP-05). Semáforo 0,7/0,4 para aspiracionales y 1,0/0,7 para comprometidos (convención de la práctica OKR, no de PRINCE2); salud contra el avance esperado lineal entre `fecha_inicio` y `fecha_meta`; confianza 1–3 rojo, 4–6 ámbar, 7–10 verde. Los check-ins solo se agregan: un segundo check-in del mismo KR y fecha se rechaza.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $O gestion/00-direccion/okr.csv --corte 2026-11-20
  python3 $O gestion/00-direccion/okr.csv --checkin KR-1.1 --valor 1 --confianza 7 --fecha 2026-12-11 \
      --autor "Usuaria sénior: Sofía Ramírez"
  # … 12 check-ins en total (4 KR × 3 fechas)
  python3 $O gestion/00-direccion/okr.csv --corte 2027-01-08 --markdown gestion/03-control/reportes/2027-01-08-okr.md
  python3 $O gestion/00-direccion/okr.csv --propuesta-sync tability
  # tras la confirmación y la publicación con la herramienta del MCP oficial:
  python3 $O gestion/00-direccion/okr.csv --marcar-publicado KR-1.1@2027-01-08 --destino tability --ref <id devuelto>
  ```
- **Entradas (qué aporta el usuario y cómo):** objetivos, KR, metas, pesos, compromiso, iniciativas y `ref_externa`, escritos en el prompt (el sistema los vuelca a `gestion/00-direccion/okr.csv`); B-n del business case y SM-n del PRD (leídos por la fachada); los check-ins, dictados en el chat o traídos por el conector como instantánea en `gestion/03-control/fuentes/`.
- **Salidas (qué queda y dónde verificarlo):**
  - Al 20/11, todo en 0,00 con la salud ya calculada: KR-2.1 y KR-2.3 «en riesgo» (salida real: `KR-2.3 Bandeja única de solicitudes en producción para los operadores [0/3 iniciativas] → 0.00 (rojo) · B-03; SM-3 · ST-003 · hito · salud en-riesgo (esperado 0.14)`).
  - `gestion/00-direccion/okr_checkins.csv` con 12 check-ins (columnas `fecha,kr_id,valor,confianza,nota,autor,fuente,publicado_en,ref_externa`). Un duplicado se rechaza (corrida complementaria): "Ya hay un check-in de KR-2.2 el 2027-01-08: los check-ins solo se agregan (registrar uno nuevo con otra fecha o corregir en la nota del siguiente)".
  - Al 8/1 (salida real): O-1 0,11 (rojo, aspiracional, promedio ponderado); KR-1.1 0,10 · salud en camino (esperado 0,16) · confianza 7 (verde); KR-1.2 0,13 en camino; O-2 0,24 (rojo, comprometido); KR-2.1 0,00 en riesgo (mantener-bajo: vale 1 solo al cumplir); KR-2.2 0,40 en camino; KR-2.3 0,33 (1 de 3 iniciativas) en riesgo (esperado 0,52). Tabla en `gestion/03-control/reportes/2027-01-08-okr.md`, con el historial de check-ins.
  - Propuesta de sincronización (salida real): `KR-1.1 2027-01-08 = 3 → tability:kr-registro-portal · tability_create_checkin (MCP oficial de Tability: https://mcp.tability.app/mcp) · confidence green` (y los dos check-ins anteriores), más `AVISO KR-1.2: sin ref_externa 'tability:…' (vincular el KR con su par en tability antes de publicar)` para cada KR sin vínculo. Tras publicar: "KR-1.1@2027-01-08 marcado como publicado en tability" (columna `publicado_en`).
  - Cómo verificarlo: abrir `okr.csv` y `okr_checkins.csv` en un editor o Excel; abrir el reporte del 8/1; escribir "¿Cómo van los OKR?". Con Perdoo el flujo es el mismo (`--propuesta-sync perdoo`); ver [CASOS-DE-USO-INTEGRACIONES caso 9](CASOS-DE-USO-INTEGRACIONES.md).
- **Decisión humana:** la ejecutiva acepta objetivos y KR (pm-director `estado.py aprobar okr`); publicar en Tability o Perdoo requiere vista previa y confirmación explícita. `okr.csv` y `okr_checkins.csv` siguen siendo la fuente.

### 46. `pm-interesados` — reporte de interesados e integridad del maestro (STK)
- **Prompt del usuario:** "Dame el reporte de interesados al 15/1 (sin valoraciones), el perfil de comunicación de todos, dónde aparece Sofía en el proyecto y verificá la integridad y la sanidad. Exportame los registros a Excel."
- **Quién:** orquestador → `pm-control` → `pm-interesados`; sanidad con `pm-sanidad`; Excel con `pm-exportar`.
- **Qué pregunta o verifica:** el reporte HTML es autocontenido (modo claro y oscuro, legible en el teléfono) y sin valoraciones salvo `--restringido`; la integridad referencial y la calidad del maestro con la familia STK: STK-01 sin poder o interés · STK-02 RACI sin A, con más de un A o persona repetida · STK-03 referencia a interesado o estereotipo inexistente (ERROR; AVISO si el estereotipo está retirado o el correo es inválido) · STK-04 preferencia confirmada vencida o sin `confirmado_por` · STK-05 propuesta de más de 30 días · STK-06 actor de «gestionar de cerca» sin rol RACI · STK-07 envío fallido o pendiente · STK-08 responsable de OKR fuera del maestro · STK-09 elemento RACI inexistente en su fuente · STK-10 nombre repetido · STK-11 RACI sin R, sobre-consulta, concentración o A con poder bajo · STK-00 no se pudo verificar. La sanidad corre esta verificación cuando existe alguno de los registros nuevos.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $I --proyecto gestion reporte --html gestion/03-control/reportes/2027-01-15-interesados.html \
      --markdown gestion/03-control/reportes/2027-01-15-interesados.md --corte 2027-01-15
  python3 $E/estado.py --proyecto gestion artefacto reporte-interesados \
      --ruta 03-control/reportes/2027-01-15-interesados.html --estado borrador
  python3 $I --proyecto gestion perfil todos --corte 2027-01-15
  python3 $I --proyecto gestion vinculos ST-003
  python3 $I --proyecto gestion integridad --corte 2027-01-15
  python3 $E/sanidad.py --proyecto gestion --rapido
  python3 $E/exportar.py xlsx --proyecto gestion
  ```
- **Entradas (qué aporta el usuario y cómo):** ninguna nueva: maestro, estereotipos, preferencias, RACI, envíos, OKR y registros ya están en la carpeta.
- **Salidas (qué queda y dónde verificarlo):**
  - Reporte (salida real): "Reporte de interesados → gestion/03-control/reportes/2027-01-15-interesados.html gestion/03-control/reportes/2027-01-15-interesados.md · 10 ubicados, 6 elementos RACI, 0 hallazgos". Secciones: matriz 2×2 en SVG, estrategias, RACI (letra y color), perfiles con procedencia, estereotipos, vínculos con OKR, especificación y WBS, envíos e integridad. Con `--restringido` agrega las valoraciones y lo advierte ("Circulación restringida: incluye valoraciones").
  - Integridad: "Integridad referencial y calidad del maestro: sin hallazgos."; sanidad: "0 ERROR · 0 AVISO · 1 INFO" (ESP-02, índice de especificación desactualizado). Ejemplo de hallazgo (corrida complementaria): un `.eml` generado y todavía no registrado como enviado da `AVISO STK-07: Envío EN-009 a ST-007 en estado pendiente (correo, Highlight report al 8 de enero)`, que desaparece tras `envios.py registrar --modo eml`.
  - `gestion/exportados/<fecha>-registros.xlsx` (una hoja por registro; el sindicato marcado como confidencial).
  - Cómo verificarlo: abrir `gestion/03-control/reportes/2027-01-15-interesados.html` en el navegador y el `.md`; abrir el Excel; escribir "Verificá la integridad del maestro de interesados".
- **Decisión humana:** antes de compartir el reporte o el Excel fuera de la junta, el gestor confirma la audiencia (el reporte por defecto no lleva actitudes; el Excel incluye la hoja `stakeholders`). Un ERROR STK-03 bloquea las puertas hasta corregirlo o hasta una decisión humana registrada.

### 47. `pm-riesgos` — riesgos candidatos desde BMAD, transcripciones, Jira y artefactos
- **Prompt del usuario:** "Antes del taller de riesgos, buscá candidatos en lo que ya tenemos: BMAD, la transcripción de la ronda con TI y el sindicato, y la instantánea de Jira del sprint. Para el proyecto que no usa BMAD, sacalos de los artefactos."
- **Quién:** orquestador → `pm-inicio` (o `pm-control` en ejecución) → `pm-riesgos`; BMAD solo a través de `pm-bmad-puente`; la instantánea de Jira la trae `pm-integraciones`.
- **Qué pregunta o verifica:** qué fuentes existen (sin BMAD informa "no aplica" y usa los artefactos); que cada candidato tenga clase (riesgo, supuesto, pregunta o issue), tipo (amenaza u oportunidad), cita y ubicación (archivo:línea, marca de tiempo o ticket); que lo ya ocurrido (bug, impedimento bloqueado) se trate como issue con su riesgo derivado; posibles duplicados o relaciones con riesgos registrados. No registra nada: cada candidato se formula como causa → evento → efecto y se evalúa con su propietario.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $T gestion/03-control/reuniones/2026-10-27-ronda-riesgos-original.vtt \
      --salida gestion/03-control/reuniones/2026-10-27-ronda-riesgos-transcripcion.md
  python3 $R --proyecto gestion candidatos --fecha 2026-10-28            # BMAD + transcripciones + artefactos
  python3 $R --proyecto gestion candidatos --fuentes tracker --fecha 2026-12-16   # toma la última instantánea de 03-control/fuentes/
  python3 $E/registro.py --proyecto gestion agregar riesgos ... --campo "notas=... origen: brief.md:91 (BMAD) y ronda 2026-10-27 [00:00:13]"
  python3 $E/registro.py --proyecto gestion agregar issues ... --campo "notas=origen: jira:PS-102"
  ```
  (Sintaxis completa en [CATALOGO §5.2](CATALOGO.md).)
- **Entradas (qué aporta el usuario y cómo):** la transcripción `.vtt` de la ronda; la instantánea CSV de Jira (columnas mínimas del formato de pm-integraciones y, opcionales, `prioridad`, `etiquetas`, `vinculo`, `descripcion`); BMAD y los artefactos ya están en la carpeta.
- **Salidas (qué queda y dónde verificarlo):**
  - Salida real (guía E2E-1, paso 4): "bmad: 42 candidatos · 3 fuente(s) leída(s) · transcripciones: 6 candidatos · tracker: 0 candidatos · no disponible · artefactos: 0 candidatos"; por ejemplo `brief.md:91` (riesgo), `prd.md:249` (pregunta abierta), `ARCHITECTURE-SPINE.md:177` (decisión diferida) y «Nos preocupa que el padrón no tenga entorno de pruebas» (TI, ST-003, [00:00:13]).
  - Paso 9 (Jira): "tracker: 3 candidatos": PS-101 (Bug, Highest) y PS-102 (Impedimento, Bloqueado) como issues «¿relacionado con R-001?», PS-104 (etiqueta `riesgo`) «¿duplica R-003?». El gestor registra R-001 ocurrido, I-001 e I-002 con `origen: jira:PS-…`.
  - Paso 13 (sin BMAD): "bmad: no aplica … artefactos: 7 candidatos · 5 fuente(s)" del mandato, el brief, los requisitos y `supuestos.csv`.
  - Borrador `gestion/03-control/reportes/<fecha>-candidatos-riesgo.md`; los registros solo cambian con `registro.py`.
  - Cómo verificarlo: abrir el borrador y `riesgos.csv` / `issues.csv` (columna `notas` con el origen); escribir "Mostrame los riesgos candidatos y su fuente".
- **Decisión humana:** el gestor y cada propietario deciden qué candidatos se registran, se descartan o se fusionan con uno existente; lo ocurrido se escala como issue según las tolerancias.

### 48. `pm-sanidad` y `pm-direccion-decisiones` — controles permanentes: presupuesto de cambio, excepción, calidad a volumen, condiciones de puertas y cadencia de contacto
- **Prompt del usuario:** "Hacé el control del período al 19 de febrero, con la sanidad a esa fecha: ¿cuánto queda del presupuesto de cambio, el pronóstico sigue dentro de la tolerancia, hay historias terminadas sin revisión de calidad, quedan condiciones de la junta abiertas y estamos hablando con cada interesado con la frecuencia que prometimos?"
- **Respuestas del usuario:**
  1. Laura Méndez, ejecutiva (ante C-002, que supera el límite y el saldo de la autoridad de cambio, y el pronóstico fuera de tolerancia): "Pido un plan de excepción para la etapa 2; C-002 queda sujeto a ese plan." Con el plan presentado: "Amplío el presupuesto de cambio a 32.000 y apruebo C-002 con el plan de excepción X-001."
  2. Sofía Ramírez, usuaria sénior (ante las historias `done` sin revisión): "Las cinco se revisaron el 25 de febrero contra sus criterios de aceptación; la 3-3 tiene una observación menor que va al backlog."
  3. Laura Méndez, ejecutiva (condición de la puerta de la etapa 2): "La prueba de carga se aprobó el 2 de marzo y el gate de BMAD quedó en PASS el 3: doy por cumplida la condición."
  4. Martín Suárez, gestor (ante la cadencia de contacto): "Retomamos la reunión técnica semanal con TI; para Lucía, el compromiso de contacto es el checkpoint semanal, no la daily."
- **Quién:** orquestador → `pm-control` → `pm-sanidad` (`sanidad.py --corte`), `pm-progreso-reportes` (`evm.py --guardar`), `pm-issues-cambios` (costo y cargo de cada cambio, informe de excepción), `pm-calidad` (revisiones en lote), `pm-interesados` (STK-12); `pm-director` registra presupuestos, decisiones, la excepción, el cumplimiento de condiciones y las puertas.
- **Qué pregunta o verifica:** lo que en la práctica se revisa a mano, tarde o nunca, y aquí corre en cada sanidad: consumo del presupuesto de cambio y de la reserva de riesgo contra lo que fijó la junta (CAM-03; > 100 % es ERROR y bloquea puertas) y cambios sobre el límite de la autoridad delegada (CAM-04), que además `registro.py` no deja registrar como aprobados (sin saldo o sobre el límite, el cambio queda `pendiente-decision` para la junta); el último corte de EVM guardado contra las tolerancias (TOL-01 si pronostica excepción y no hay excepción abierta); cada historia terminada de `backlog.csv` contra `calidad.csv` (QUA-01) y revisiones vencidas (QUA-02); condiciones abiertas de puertas (EST-12 y, en la verificación de la puerta siguiente, G-01, que bloquea el cierre); y, para los cuadrantes gestionar de cerca, mantener satisfecho y mantener informado, el último contacto registrado contra la frecuencia del perfil (STK-12, tolerancia 1,5 ×). Pregunta quién decide cada corrección: lo que excede la autoridad delegada va a la junta.
- **Comandos:** los ejecuta el sistema; el usuario no los escribe. Cada bloque viene de la corrida de referencia de una guía distinta, con su propia carpeta: E2E-2 ([salida-g2.md](guias/evidencia/salida-g2.md)), E2E-4 ([salida-g4.md](guias/evidencia/salida-g4.md)) y E2E-3 ([salida-g3.md](guias/evidencia/salida-g3.md)).
  ```bash
  # E2E-2, pasos 5 y 10: presupuesto de cambio, cambio con costo y cargo, corte de EVM y sanidad a la fecha de corte
  python3 $E/estado.py --proyecto gestion presupuesto cambio=12000 limite_autoridad_cambio=10000 \
      --por "Ejecutiva: Laura Méndez" --fecha 2026-11-27                                   # pm-director
  python3 $E/registro.py --proyecto gestion agregar cambios --campo "titulo=Consentimiento informado y registro de accesos consultable por el socio" \
      --campo "impacto_costo=+USD 15.000" --campo "costo=15000" --campo "cargo=presupuesto-cambio" ...
  python3 $E/registro.py --proyecto gestion actualizar cambios C-002 --campo "decision=aprobado" --campo "estado=aprobado" \
      --campo "decidido_por=Autoridad de cambio: Sofía Ramírez" ...                        # rechazado: queda pendiente-decision
  python3 $E/evm.py --pv 75000 --ev 60000 --ac 77000 --bac 133000 --modo agil --pct-no-must 20 \
      --proyecto gestion --guardar --corte 2027-02-19
  python3 $E/sanidad.py --proyecto gestion --rapido --corte 2027-02-19
  python3 $E/estado.py --proyecto gestion puerta decision-ad-hoc --decision aprobado --por "Ejecutiva: Laura Méndez" --fecha 2027-02-22 \
      --condiciones "X-001: la junta pide plan de excepción para la etapa 2; C-002 queda sujeto a ese plan"   # pm-director
  python3 $E/estado.py --proyecto gestion limite-etapa --excepcion X-001                                     # pm-director
  python3 $E/estado.py --proyecto gestion cumplir-condiciones decision-ad-hoc --fecha 2027-02-24 \
      --por "Ejecutiva: Laura Méndez" --nota "plan de excepción X-001 presentado; C-002 se decide con él"    # pm-director
  python3 $E/estado.py --proyecto gestion presupuesto cambio=32000 --por "Ejecutiva: Laura Méndez" --fecha 2027-02-26   # pm-director
  python3 $E/registro.py --proyecto gestion actualizar cambios C-002 --campo "decision=aprobado" --campo "estado=aprobado" \
      --campo "decidido_por=Junta: Laura Méndez (ejecutiva) · plan de excepción X-001" ...
  python3 $E/puertas.py --proyecto gestion verificar autorizar-plan-excepcion
  # E2E-4, pasos 8, 12 y 13: condición formal, calidad a volumen y cumplimiento
  python3 $E/estado.py --proyecto gestion puerta autorizar-etapa --decision condicionado --por "Ejecutivo: Laura Méndez" \
      --fecha 2026-11-27 --etapa-nombre "Release 1" --fin 2027-03-05                       # pm-director
  python3 $E/sanidad.py --proyecto gestion --rapido --corte 2027-02-26
  python3 $E/registro.py --proyecto gestion agregar calidad --campo "producto=Release 1 · historia 1-3 Consulta de saldos de ahorro y préstamos" \
      --campo "metodo_verificacion=prueba" --campo "aprobador=Sofía Ramírez" --campo "fecha_real=2027-02-25" \
      --campo "resultado=aprobado" --campo "estado=completada" ...                        # una por historia (Q-004…Q-008)
  python3 $E/puertas.py --proyecto gestion verificar autorizar-etapa
  python3 $E/estado.py --proyecto gestion cumplir-condiciones autorizar-etapa --fecha 2027-03-05 --por "Ejecutivo: Laura Méndez" \
      --nota "Q-001 prueba de carga NFR-3 aprobada el 2027-03-02 (p95 2,4 s); gate de preparación de BMAD en PASS el 2027-03-03"   # pm-director
  # E2E-3, paso 13: cadencia de contacto
  python3 $I --proyecto gestion integridad --corte 2027-02-05
  python3 $E/registro.py --proyecto gestion agregar envios --campo "fecha=2027-02-05" --campo "stakeholder_id=ST-006" --campo "canal=reunion" \
      --campo "modo=manual" --campo "estado=enviado" --campo "asunto=Reunión técnica: integración con el núcleo (NFR-6) y prueba de carga (NFR-3)" \
      --campo "notas=retroalimentación: ..."
  python3 $E/registro.py --proyecto gestion actualizar stakeholders ST-010 --campo "canal=checkpoint" --campo "frecuencia=semanal"
  ```
  (Los `...` abrevian campos descriptivos que están completos en la evidencia; sintaxis en [CATALOGO §5](CATALOGO.md).)
- **Entradas (qué aporta el usuario y cómo):** las decisiones de la junta en el prompt o respondiendo al orquestador (montos sin moneda ni separador de miles); el costo y el cargo de cada cambio; los valores de EVM del período; las revisiones de calidad realizadas; las reuniones y llamadas mantenidas, que se registran como envío manual.
- **Salidas (qué queda y dónde verificarlo):**
  - Aprobación de C-002 por la autoridad de cambio y sanidad del 2027-02-19 en la guía E2E-2 (salida real):
    ```text
    Control de cambios (PRINCE2, autoridad y presupuesto de cambio; no se omite con --forzar):
      - C-002: costo 15.000 supera el límite de la autoridad de cambio (10.000).
      - C-002: el presupuesto de cambio no alcanza: 9.000 ya cargados + 15.000 = 24.000 de 12.000 fijados por la junta.
      → 'Autoridad de cambio: Sofía Ramírez' no es la junta ni el ejecutivo. Dejar estado=pendiente-decision (sin decision=aprobado) y escalar a pm-director: decide la junta o el ejecutivo.
    Sanidad de 'Portal de autoservicio para socios' (entrega/CS): 0 ERROR · 1 AVISO · 1 INFO
      AVISO TOL-01 El EVM del 2027-02-19 pronostica salir de la tolerancia (costo=n/a-agil, cronograma=n/a-agil, alcance=rojo) y no hay excepción abierta.
      INFO  CAM-03 Presupuesto de cambio: 9.000 de 12.000 (75 %).
    ```
    `evm.py` deja `Guardado: 03-control/reportes/evm-2027-02-19.json` (`semaforo_alcance rojo`, `excepcion_prevista True`). C-002 queda `pendiente-decision` y no consume presupuesto; `puertas.py verificar autorizar-plan-excepcion` muestra solo el bloqueo de la lista de control (L-01). La junta amplía el presupuesto a 32.000, aprueba C-002 (sin la ampliación, `registro.py` también le pediría la fuente: `reserva-gestion`, `plan-excepcion` o ampliar), confirma la lista y la puerta se registra. La sanidad del 2027-02-26: `0 ERROR · 1 AVISO · 1 INFO` con `INFO CAM-03 Presupuesto de cambio: 24.000 de 32.000 (75 %).` y `estado.py resumen` muestra `Presupuestos: cambio=32000, limite_autoridad_cambio=10000`.
  - Sanidad del 2027-02-26 en la guía E2E-4 (salida real, extracto): `0 ERROR · 7 AVISO · 3 INFO`, con `AVISO EST-12 Condiciones abiertas de autorizar-etapa: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada).`, cinco `AVISO QUA-01` (por ejemplo, `1-3-consulta-de-saldos-de-ahorro-y-préstamos: terminado sin revisión de calidad registrada.`) y `AVISO QUA-02 Revisión de calidad vencida Q-001 (NFR-3 prueba de carga (consultas de saldos y préstamos), prevista 2027-02-19).` Con las revisiones Q-004…Q-008 registradas: `0 ERROR · 2 AVISO · 2 INFO` (quedan EST-12 y QUA-02). La condición había nacido sola al registrar la puerta: `Condiciones agregadas desde la verificación: gate de preparación de BMAD en CONCERNS (2026-11-26: NFR-3 sin prueba de carga planificada)`. Antes de cumplirla, `puertas.py verificar autorizar-etapa` muestra `condición condiciones abiertas de puertas anteriores: autorizar-etapa 2026-11-27 (…)` (G-01); después, la sanidad del 2027-03-05 queda en `0 ERROR · 0 AVISO · 1 INFO`.
  - Integridad del 2027-02-05 en la guía E2E-3 (salida real): `AVISO STK-12: ST-006 Área de TI del núcleo operativo (gestionar-de-cerca, frecuencia semanal): último contacto registrado el 2027-01-18, hace 18 días (máximo 10)`, y lo mismo para ST-009 (sin contacto desde 2027-01-15, 21 días; máximo 10) y ST-010 (frecuencia diaria; máximo 2). Con la reunión EN-008, los checkpoints EN-009 y EN-010, la acción A-005 y la frecuencia de ST-010 corregida a semanal: `Integridad referencial y calidad del maestro: sin hallazgos.`
  - Dónde verificar: `estado.json` → `presupuestos` y `puertas[]` (`condiciones`, `condiciones_cumplidas`, `condiciones_verificadas_por`, `condiciones_nota`); `cambios.csv` (columnas `costo` y `cargo`); `03-control/reportes/evm-<corte>.json`; `calidad.csv`; `envios.csv`; `decisiones.csv` (presupuestos, decisión ad hoc y cumplimiento de condiciones). Prompts: "¿Cuánto queda del presupuesto de cambio?", "¿Qué condiciones de la junta siguen abiertas?", "¿A quién no contactamos con la frecuencia acordada?".
- **Decisión humana:** la junta (Laura Méndez) decide la excepción, amplía el presupuesto, aprueba el cambio que superaba el límite delegado y da por cumplidas las condiciones; pm-director registra cada decisión con `estado.py` (el hook impide que otro agente ejecute `presupuesto`, `cumplir-condiciones`, `puerta` o `limite-etapa --excepcion`). Sofía Ramírez aprueba las revisiones de calidad; el gestor decide la acción correctiva con TI y corrige la frecuencia. Ningún control decide: detecta, explica el arreglo y señala quién decide.

---

### 49. `pm-mapas-estrategicos` — recorrido del socio y mapa de valor del portal desde la especificación
- **Prompt del usuario:** "Con la especificación de BMAD, armá el recorrido de UJ-2 (Diego pide un préstamo) con lo que hace la operadora como carril interno, y un mapa de valor del portal: qué construye el equipo, qué se compra o terceriza y dónde está la inercia. Mostrame qué controles fallan."
- **Quién:** orquestador → `pm-inicio` → `pm-mapas-estrategicos`; BMAD solo a través de `pm-bmad-puente` (`bmad.py recorridos` y `capacidades`, de solo lectura); los candidatos aceptados se registran con `pm-registros`, `pm-riesgos` y `pm-direccion-decisiones` según su nivel.
- **Qué pregunta o verifica:** la pregunta estratégica del mapa y la persona del recorrido; que cada posición tenga etapa y evidencia y cada emoción su fuente; una acción por paso; que las inercias tengan riesgo, los componentes en producto o commodity marcados construir tengan decisión y los dolores tengan tratamiento (familia MAP de la sanidad).
- **Comandos:** los ejecuta el sistema; el usuario no los escribe.
  ```bash
  python3 $B --proyecto gestion recorridos --id UJ-2
  python3 $M --proyecto gestion recorrido semilla --uj UJ-2 --backstage UJ-3 --fecha 2026-10-29
  python3 $M --proyecto gestion wardley semilla --slug portal --titulo "Portal de socios · qué construir y qué comprar" --pregunta "…" --fecha 2026-10-29
  python3 $M --proyecto gestion recorrido render uj-2 && python3 $M --proyecto gestion wardley render portal
  python3 $M --proyecto gestion controles
  python3 $M --proyecto gestion vincular portal C11 --refs R-001
  ```
  (`$M` = `…/pm-mapas-estrategicos/scripts/mapas.py`; sintaxis completa en [CATALOGO §5.2](CATALOGO.md).)
- **Entradas (qué aporta el usuario y cómo):** la confirmación de las posiciones, las emociones y sus fuentes, y las decisiones de construir o comprar; BMAD ya está en el repositorio.
- **Salidas (qué queda y dónde verificarlo):**
  - Salida real ([salida-g5.md](guias/evidencia/salida-g5.md), paso 17): UJ-2 realizado por FR-6 y FR-7, KPI SM-3 y SM-5, contrapeso SM-C1; semilla del recorrido con 9 pasos y del mapa con 3 anclas, 15 componentes y 6 enlaces (quedan 9 componentes).
  - `controles`: MAP-01 (notificaciones en producto marcada construir sin decisión), MAP-02 (núcleo operativo con inercia), MAP-03 y MAP-04 (paso P6 sin tratamiento ni fuente); tras S-004, D-001, R-001 y los vínculos, "0 aviso(s) de la familia MAP".
  - Fuente en `gestion/02-planificacion/mapas/*.json`; vistas `wardley-portal.md` y `.owm`, `recorrido-uj-2.md` y `.html` en `02-planificacion/visuales/`; artefactos `mapa-wardley-portal` y `mapa-recorrido-uj-2` en revisión.
  - Cómo verificarlo: abrir el HTML del recorrido y escribir "¿Qué dolores del socio no tienen tratamiento?".
- **Decisión humana:** el gestor confirma posiciones, emociones y decisiones de construir o comprar; el riesgo de la inercia queda con su propietario; los mapas siguen en borrador hasta que los confirma el dueño de la decisión.

## Parte 7 · Decidir con datos y controlar de forma continua (en las guías E2E)

Estas capacidades se muestran con la corrida real de las guías de [docs/guias/](guias/README.md): cada caso indica el
pedido típico (frase verificada en vivo, `docs/evaluacion/frases-enrutamiento.tsv`), la skill dueña, el script que corre
por detrás, la decisión humana y el paso de la guía con su evidencia. Las cifras e ids son los de cada guía.

| Caso | Pedido típico (frase verificada) | Skill · script | Decisión humana | Dónde verlo con salidas reales |
|---|---|---|---|---|
| 50 · Opciones de respuesta y plan de contingencia | "Para los riesgos altos compará evitar, reducir, transferir y aceptar con contingencia, y decime cuál conviene" (103) | `pm-riesgos` · `riesgos.py opciones` (valor neto, `--elegir … --por`) y plantilla `plan-contingencia.md`; REG-10 | el propietario del riesgo elige la opción; si no es la recomendada, con motivo | [E2E-1](guias/E2E-1-riesgos.md) pasos 6a, 6b y 13 · [salida-g1.md](guias/evidencia/salida-g1.md) |
| 51 · Personas de usuario y capacidad × persona | "Definí las personas de usuario del portal y mapeá qué requisitos pide, usa o aprovecha cada una" (105) | `pm-interesados` · `interesados.py personas candidatos\|mapa\|priorizacion`; STK-13…16 | el usuario sénior confirma cada persona antes de registrarla | [E2E-2](guias/E2E-2-alcance-roadmap.md) paso 4 · [E2E-5](guias/E2E-5-idea-a-proyecto.md) pasos 10b y 16b |
| 52 · Radar del día y briefing de incorporación | "¿Qué tengo que decidir, escalar y desbloquear hoy en el proyecto?" (108) · "Prepará un briefing de incorporación para la nueva integrante de la junta antes de la puerta" (111) | `pm-orquestador`, `pm-progreso-reportes` · `estado.py radar` y `briefing` (solo lectura) | el radar ordena; decide quien figura en cada ítem | [E2E-1](guias/E2E-1-riesgos.md) paso 12 · [E2E-3](guias/E2E-3-interesados-okr-avance.md) paso 10a · [E2E-5](guias/E2E-5-idea-a-proyecto.md) pasos 7 y 14 |
| 53 · Acuerdos de reunión con cita | "Pasame las decisiones y compromisos de la transcripción del comité de ayer, con responsable y fecha, y preguntame antes de registrarlos" (115) | `pm-reuniones` · `extraccion.py candidatos` y `registrar --confirmar … --por` | quien presidió confirma los ids; las decisiones de la junta las registra pm-director | [E2E-3](guias/E2E-3-interesados-okr-avance.md) paso 8 · [salida-g3.md](guias/evidencia/salida-g3.md) |
| 54 · Análisis de impacto antes del cambio | "Analizá el impacto del cambio C-004 en el camino crítico, el presupuesto de cambio y el VAN, y decime quién lo decide" (117) | `pm-issues-cambios` · `impacto.py analizar` (con `cpm.py`, `release.py` e `inversion.py`) | la autoridad de cambio o la junta, según el límite y el presupuesto delegados | [E2E-2](guias/E2E-2-alcance-roadmap.md) pasos 7 y 10 · [salida-g2.md](guias/evidencia/salida-g2.md) |
| 55 · Tres valores, reserva de cronograma y capacidad del release | "Estimá con tres valores las actividades de la etapa 2 con la fórmula triangular que fija el plan y decime la reserva de cronograma a 1σ del camino crítico" (129) · "Con la velocidad de 20 puntos, ¿entran los Must y Should del release 2 en sus cuatro sprints o tengo que repriorizar?" (130) | `pm-cronograma-estimacion`, `pm-agil-hibrido` · `cpm.py --estimacion`, `release.py capacidad` | el plan fija la distribución y la confianza; el product owner reprioriza | [E2E-2](guias/E2E-2-alcance-roadmap.md) pasos 3 y 4 |
| 56 · Highlight y tablero desde el dato | "Armá el highlight de la quincena desde los datos y el tablero con las mismas cifras; marcá qué semáforos son juicio mío" (127) | `pm-progreso-reportes`, `pm-visuales` · `estado.py periodo --juicio --highlight --tablero` y `--verificar` | el gestor confirma su juicio (puede empeorar un semáforo, no mejorarlo) | [E2E-3](guias/E2E-3-interesados-okr-avance.md) paso 10b · [salida-g3.md](guias/evidencia/salida-g3.md) |
| 57 · Estado de productos y cierre por id | "¿En qué estado está cada producto del Release 1? Armá el product status account y marcá lo que figura terminado o aceptado sin revisión de calidad" (125) | `pm-paquetes-trabajo`, `pm-calidad`, `pm-cierre-proyecto` · `estado.py productos`; QUA-04, C-03 y C-07 | la junta decide el cierre con los faltantes a la vista | [E2E-4](guias/E2E-4-producto-bmad.md) pasos 6 y 9 · [salida-g4.md](guias/evidencia/salida-g4.md) |
| 58 · Ciclo de las lecciones y lecciones de otros proyectos | "Tengo la transcripción de la retrospectiva del sprint 4: proponeme las lecciones y las acciones de mejora con su cita antes de registrar nada" (121) · "¿Qué lecciones de otros proyectos sobre integraciones deberíamos tener en cuenta al arrancar?" (113) | `pm-reuniones`, `pm-lecciones-aprendidas` · `extraccion.py --tipo retrospectiva`, `lecciones.py clasificar\|accionar\|verificar\|informe\|buscar\|incorporar`; E-11, REG-11, REG-12 | el equipo confirma las candidatas; el gestor clasifica, acciona y verifica con su nombre | [E2E-4](guias/E2E-4-producto-bmad.md) pasos 6c a 9 · [E2E-5](guias/E2E-5-idea-a-proyecto.md) paso 1 |
| 59 · Expediente de auditoría verificable | "Armá el expediente de auditoría del proyecto para la PMO con decisiones, líneas base, aprobaciones y evidencia de las puertas" (119) | `pm-exportar` · `paquete.py auditoria` y `verificar` | quien lo entrega elige el período y si es para un tercero (`--externo`) | [E2E-4](guias/E2E-4-producto-bmad.md) paso 9b · [salida-g4.md](guias/evidencia/salida-g4.md) |

## Variantes

### Variante A · Predictivo sin BMAD: renovación de la red de sucursales
Proyecto de infraestructura con 12 sucursales, presupuesto fijo y sin capa de especificación. Lo que cambia respecto del ejemplo principal:

| Momento | Prompt del usuario | Quién | Comandos y efecto | Dónde se verifica |
|---|---|---|---|---|
| Arranque | "Creá el proyecto “Renovación de red de sucursales” en la carpeta ./red, en español y con enfoque predictivo." Atajo: `/pm-method:pm-nuevo "Renovación de red de sucursales" ./red es predictivo` | orquestador → pm-nuevo | `nuevo_proyecto.py … --enfoque predictivo`; no encuentra carpetas de BMAD, así que `integraciones.especificacion` queda distinta de `bmad`. | `red/estado.json`: `enfoque_entrega` = `predictivo` e `integraciones.especificacion` = `ninguna` |
| Requisitos | "Elicitá los requisitos con las áreas de sucursales y armá la matriz de trazabilidad." | orquestador → pm-planificacion → pm-planificacion-por-productos | Escribe `02-planificacion/requisitos.md` (filas REQ-001…) y `matriz-trazabilidad.md`; la columna `ref` de `wbs.csv` cita REQ-###. | `red/02-planificacion/requisitos.md`, `red/02-planificacion/matriz-trazabilidad.md` y columna `ref` de `red/02-planificacion/wbs.csv` |
| Lectura | ninguno propio: lo dispara cualquier skill que necesite requisitos | todas | `especificacion.py --proyecto red resumen` responde igual que con BMAD; el proveedor es pm-method (`requisitos.md`, `backlog.csv`, `wbs.csv`). | prompt "Mostrame el resumen de requisitos del proyecto" |
| Cronograma | "Exportá el cronograma a MS Project." | pm-planificacion → pm-cronograma-estimacion | `cpm.py red/02-planificacion/actividades.csv --inicio 2027-01-11 --mermaid red/02-planificacion/gantt.md --mspdi red/02-planificacion/cronograma.xml --wbs red/02-planificacion/wbs.csv`. | `red/02-planificacion/cronograma.xml` abierto en MS Project o ProjectLibre; `red/02-planificacion/gantt.md` |
| Avance | "Armá el highlight report de este período." Atajo: `/pm-reporte highlight` | pm-control → pm-progreso-reportes | `evm.py --csv … --bac … --tol-costo … --tol-plazo …` en modo predictivo; sin `bmad.py avance` ni `verificar`. | `red/03-control/reportes/<fecha>-highlight-report.md` |
| Cambio | "Sucursales pide agregar Wi-Fi para socios." | pm-control → pm-issues-cambios | `solicitud-cambio` y C-###; si se aprueba, `requisitos.md` lo actualiza pm-planificacion-por-productos. No hay `bmad.py handoff`. | `red/03-control/registros/issues.csv` y `red/03-control/registros/cambios.csv`; prompt "Mostrame los cambios pendientes de decisión" |

Las puertas, los roles y la regla de que solo pm-director registra no cambian.

### Variante B · Agile project in English: member mobile app
Equipo de producto que trabaja en inglés con fecha y costo fijos. Las skills responden y generan en inglés; los datos faltantes salen como `[to be confirmed]`.

| Momento | Prompt del usuario | Quién | Comandos y efecto | Dónde se verifica |
|---|---|---|---|---|
| Arranque | "Create a project called “Member app” in the ./app folder, in English, with an agile approach." Atajo: `/pm-method:pm-nuevo "Member app" ./app en agil` | orquestador → pm-nuevo | `estado.json.idioma = en`, `enfoque_entrega = agil`. | `app/estado.json`: `idioma` y `enfoque_entrega` |
| Perfil | "Small agile app, fixed date: minimal profile, ask me only once." | orquestador → pm-inicio → pm-mandato-y-brief | Perfil ágil mínimo: brief ligero, visión con MVP; las dos confirmaciones (formalidad y enfoque) se combinan en una. | `app/01-inicio/project-brief.md` y `app/01-inicio/declaracion-vision.md` |
| Backlog | "Create the MoSCoW backlog using the minimal agile profile; we have no WBS." | pm-planificacion → pm-agil-hibrido | `backlog.csv` reemplaza a PBS, WBS, diccionario y flujo; release plan por etapas con DoD/DoR. Las puertas de etapa siguen. | `app/02-planificacion/backlog.csv` (editor o Excel) y `app/02-planificacion/release-plan.md` |
| Sprint | "Set up sprint 4 as a work package: these are the committed backlog items and the definition of done." | pm-control → pm-paquetes-trabajo | WP con alcance = ids de ítems, DoD como criterio de calidad. | `app/03-control/paquetes-trabajo/WP-###-<nombre>.md` |
| Swap | "The PO wants to swap the PDF export story for the filters story." | pm-control → pm-agil-hibrido | Should por Should, sin tocar Must, fecha ni costo: decisión `nivel=product-owner` con `registro.py agregar decisiones`; no hay solicitud de cambio. | fila `nivel=product-owner` en `app/03-control/registros/decisiones.csv` |
| EVM | "Run agile EVM for sprint 6: we are on budget but behind on points." | pm-control → pm-progreso-reportes | `evm.py --pv … --ev … --ac … --bac … --modo agil --pct-no-must 30 --idioma en`: EAC > BAC se lee como alcance que no entra; hay excepción solo si peligran los Must. | la respuesta; si se pide el análisis, `app/03-control/reportes/<date>-analisis-valor-ganado.md` |
| Retro | "Let's run the sprint 6 retrospective." | pm-control → pm-agil-hibrido | `03-control/reportes/<date>-retrospectiva-S6.md`; el taller de etapa sigue siendo de pm-lecciones-aprendidas. | `app/03-control/reportes/<date>-retrospectiva-S6.md` |

### Variante C · Proyecto con Jira y Teams conectados vía pm-integraciones
Mismo portal de socios, pero el proveedor gestiona sus tickets en Jira y la cooperativa usa Teams. El usuario conectó los servidores MCP en su cliente (el paquete no trae conectores ni credenciales).

1. **Detectar y registrar.** Prompt del usuario: "Ya conectamos Jira y Teams: configurá las integraciones." Orquestador → pm-control → pm-integraciones. La skill revisa las herramientas `mcp__<servidor>__<herramienta>` presentes y las clasifica por capacidad. Con el servidor oficial de Atlassian (Rovo MCP Server) primero obtiene el `cloudId` con su herramienta de recursos accesibles. Para Teams, avisa que el servidor "Teams (preview)" de Microsoft figura como legado y que conviene usar el que la organización tenga aprobado (por ejemplo Work IQ).
   ```bash
   python3 $E/estado.py --proyecto gestion integracion tracker=jira chat=teams
   ```
   Dónde se verifica: `gestion/estado.json` → `integraciones.tracker` = `jira` e `integraciones.chat` = `teams`; o el prompt "¿Qué integraciones tiene el proyecto?".
2. **Leer sin confirmación.** Prompt del usuario: "Traé los tickets abiertos del sprint actual de Jira." Consulta por JQL y guarda una instantánea inmutable `03-control/fuentes/jira-2026-12-10.csv` con columnas `clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url`. Dónde se verifica: `gestion/03-control/fuentes/jira-2026-12-10.csv` en un editor o Excel (no se edita: la próxima lectura crea otra con su fecha).
3. **Conciliar.** Compara la instantánea con `backlog.csv`, `acciones.csv` e `issues.csv`. Las diferencias se proponen; un ticket de alcance que no rastrea al backlog va a pm-issues-cambios. Las columnas de gobierno (moscow, release, producto_pbs, prioridad) siguen siendo solo de pm-method; la clave de Jira se guarda en `notas` como `jira:ABC-12`. Prompt del usuario: "Compará lo que trajiste de Jira con el backlog y los registros." Dónde se verifica: las diferencias propuestas, en la respuesta; las que se aceptan, en `gestion/02-planificacion/backlog.csv` y en `gestion/03-control/registros/acciones.csv` o `issues.csv` (columna `notas`).
4. **Escribir con confirmación.** Prompt del usuario: "Creá tickets en Jira para las acciones abiertas del proveedor." Respuesta del usuario: Martín Suárez, gestor: "Confirmo el lote tal como está en la vista previa." Como corre en un subagente, pm-control devuelve la vista previa exacta (proyecto Jira, resumen, asignado, vencimiento) como decisión humana requerida. El orquestador la muestra, Martín confirma el lote, y recién entonces se crean los tickets; las claves quedan en `notas` de cada A-###. Dónde se verifica: columna `notas` de `gestion/03-control/registros/acciones.csv` y los tickets en Jira.
5. **Publicar.** Prompt del usuario: "Publicá el highlight de esta semana en el canal del proyecto en Teams." Respuesta del usuario: Martín Suárez, gestor: "Confirmo; publicalo." pm-integraciones prepara el mensaje en el idioma de la audiencia según la matriz de comunicaciones; vista previa → confirmación del gestor → publicación → anotación en `diario.md`. Si la publicación va dirigida a interesados del maestro, la capa de canales la registra además en `envios.csv` (`envios.py preparar-mcp` → publicación con la herramienta → `envios.py registrar --modo mcp`; caso 44). Dónde se verifica: el mensaje en el canal de Teams y la anotación en `gestion/03-control/registros/diario.md`.
6. **Informes.** pm-progreso-reportes y pm-visuales citan la instantánea `jira-2026-12-10.csv` como fuente; riesgos, issues y acciones siguen saliendo de los registros. Prompt del usuario en cada período: "Volvé a traer los tickets de Jira." (atajo: `/pm-sync tracker`), que repite la lectura y crea una instantánea nueva por fecha. Dónde se verifica: la cita de la instantánea en el informe (`gestion/03-control/reportes/<fecha>-highlight-report.md`) y la nueva `gestion/03-control/fuentes/jira-AAAA-MM-DD.csv`.

Si una herramienta falla dos veces o no tiene la operación, la skill lo informa y ofrece la alternativa local (CSV, Markdown o borrador para copiar; para mensajes a interesados, la capa de canales: webhook, correo SMTP o `.eml`).
