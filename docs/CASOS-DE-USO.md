# Casos de uso de pm-method 2.0.0 · Worked examples

Un ejemplo trabajado por cada una de las 37 skills, incluidos los seis comandos, sobre un mismo proyecto de muestra para que los casos se encadenen de principio a fin. Al final hay tres variantes cortas: predictivo sin BMAD, ágil en inglés y un proyecto con Jira y Teams conectados.

Los datos del proyecto de muestra (personas, montos, fechas, ids) siguen el caso de punta a punta con el que se probó la versión 2: las cifras de los ejemplos coinciden con lo que devolvieron los scripts en esa prueba. Las personas y la cooperativa son ficticias. Las respuestas humanas son simuladas.

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
```

Los scripts que reciben la carpeta usan `--proyecto gestion` y resuelven las rutas internas contra ella. Los que reciben un archivo (`wbs.py`, `cpm.py`, `okr.py`, `transcripcion.py`) llevan la ruta desde la raíz del repositorio.

**Cómo leer cada caso.** *Petición*: lo que escribe el usuario. *Quién*: la cadena orquestador → subagente → skill. *Qué pregunta o verifica*: lo que la skill comprueba antes de producir y lo que pregunta (siempre a través del orquestador, porque los subagentes no preguntan). *Comandos*: los que se ejecutan. *Artefacto*: lo que queda y en qué estado. *Decisión humana*: quién decide y quién registra después.

Regla que atraviesa todos los casos: cuando un subagente necesita una decisión, la devuelve en su bloque "Retorno al orquestador / Return"; el orquestador se la presenta a la persona con el rol que decide; con la respuesta explícita (nombre y rol), el orquestador invoca a `pm-director`, que es el único agente que ejecuta `estado.py puerta` y `estado.py aprobar`.

---

## Parte 1 · Puesta en marcha (SU, etapa 0)

### 1. `/pm-ayuda` — orientarse antes de empezar
- **Petición:** `/pm-method:pm-ayuda puertas`
- **Quién:** orquestador en el hilo principal ejecuta la skill-comando `pm-ayuda`. Sin subagente.
- **Qué pregunta o verifica:** filtra la ayuda al tema pedido (`$ARGUMENTS` = `puertas`). Busca `estado.json`; como todavía no hay proyecto, no agrega el siguiente paso.
- **Comandos:** ninguno (con proyecto, agregaría `python3 $E/estado.py --proyecto gestion siguiente`).
- **Artefacto:** ninguno; respuesta en pantalla con el ciclo SU → `autorizar-inicio` → IP → `autorizar-proyecto` + `autorizar-etapa` → etapas 2…n → `autorizar-cierre`, y la aclaración de que solo pm-director registra puertas.
- **Decisión humana:** ninguna.

### 2. `/pm-nuevo` — crear la carpeta del proyecto
- **Petición:** `/pm-method:pm-nuevo "Portal de autoservicio para socios" ./gestion es hibrido` y, en el mismo mensaje, "la ejecutiva es Laura Méndez y el gestor Martín Suárez".
- **Quién:** orquestador → skill-comando `pm-nuevo`, que usa los scripts de pm-estado-proyecto y pm-bmad-puente.
- **Qué pregunta o verifica:** que `gestion/` no tenga ya un `estado.json` (no sobrescribe); que haya BMAD en la carpeta o en una superior (`_bmad/`, `_bmad-output/` o `.bmad-core/`); que la carpeta del proyecto quede fuera de las de BMAD.
- **Comandos:**
  ```bash
  python3 $E/nuevo_proyecto.py --ruta gestion --nombre "Portal de autoservicio para socios" \
      --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez"
  python3 $B --proyecto gestion detectar
  python3 $E/estado.py --proyecto gestion integracion especificacion=bmad
  python3 $E/estado.py --proyecto gestion siguiente
  ```
- **Artefacto:** `gestion/estado.json` (fase `pre-proyecto`, proceso SU, etapa 0), los nueve CSV de `03-control/registros/`, `diario.md` y `estado.json.integraciones.bmad` con layout v6. En la prueba el soporte salió `version-no-visible`: el script avisa que trabaja por patrones.
- **Decisión humana:** ninguna. El comando ofrece seguir con pm-mandato-y-brief.

### 3. `pm-orquestador` — "¿por dónde empiezo?"
- **Petición:** "Quiero gestionar el portal de socios con el método; ¿por dónde empiezo?"
- **Quién:** orquestador (hilo principal; también `claude --agent pm-method:pm-orquestador`).
- **Qué pregunta o verifica:** corre la sanidad rápida, lee el estado y resume en tres líneas: SU, etapa 0, sin tolerancias ni puertas; enfoque híbrido; especificación BMAD. Clasifica la petición como SU y muestra la secuencia: pm-inicio con pm-mandato-y-brief, pm-organizacion-roles, pm-caso-de-negocio, pm-riesgos y pm-plan-etapa-y-limites → 🔒 `autorizar-inicio` (decide la ejecutiva). Hace una sola pregunta: "¿Tenés el correo o el acta del consejo con el pedido?".
- **Comandos:**
  ```bash
  python3 $E/sanidad.py --proyecto gestion --rapido
  python3 $E/estado.py --proyecto gestion ver
  python3 $E/estado.py --proyecto gestion siguiente
  ```
- **Artefacto:** ninguno; plan de secuencia en la respuesta. Al delegar usa la plantilla de encargo (guía §2): carpeta, objetivo, skills, datos confirmados, restricciones (no registrar puertas, no escribir afuera, BMAD solo lectura) y exigencia del bloque de retorno.
- **Decisión humana:** conformidad del gestor con la secuencia antes de ejecutarla.

### 4. `pm-mandato-y-brief` — mandato y project brief
- **Petición:** "Convertí este correo del consejo en mandato y armá el brief. El brief de producto ya está en BMAD: usalo sin copiarlo."
- **Quién:** orquestador → `pm-inicio` → `pm-mandato-y-brief`.
- **Qué pregunta o verifica:** fase `pre-proyecto`; ejecutivo prospectivo presente (sin él el proyecto no sigue); lecciones previas (busca en proyectos anteriores); nivel de formalidad con la tabla de la guía §1; enfoque de entrega puntuando criterios (los entregables puntúan distinto → híbrido) y ruta de planificación BMAD. Lee el brief de producto solo por la fachada y toma ruta y sha con el inventario.
- **Comandos:**
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
- **Artefacto:** `00-direccion/mandato.md`, `01-inicio/project-brief.md` (problema, usuarios y visión referenciados al brief de producto por ruta y sha corto), lección L-001, decisiones D-001 (formalidad, nivel `gestor`) y D-002 (enfoque, nivel `junta`).
- **Decisión humana:** el primer retorno trae dos preguntas: nivel de formalidad (decide el gestor) y enfoque de entrega (decide la ejecutiva). El orquestador las presenta, Martín elige "mínimo" y Laura confirma "híbrido", y se vuelve a delegar con las respuestas.

### 5. `pm-organizacion-roles` — junta, roles e interesados
- **Petición:** "Diseñá la junta: Laura patrocina, Sofía representa a los socios y será la PO, el desarrollo lo hace un proveedor con Diego como proveedor sénior, Andrea hace aseguramiento y Lucía lidera el equipo del proveedor."
- **Quién:** orquestador → `pm-inicio` → `pm-organizacion-roles`.
- **Qué pregunta o verifica:** un solo ejecutivo distinto del gestor; los tres intereses en la junta; aseguramiento fuera del gestor, los equipos y el soporte; sin responsabilidades huérfanas. Mapea roles ágiles y BMAD (el PM de BMAD no es el gestor del proyecto; la PO es la usuaria sénior). Detecta que el rol de soporte no tiene titular y lo deja `[por confirmar]`.
- **Comandos (después de la confirmación de la ejecutiva):**
  ```bash
  python3 $E/estado.py --proyecto gestion rol ejecutivo="Laura Méndez" gestor_proyecto="Martín Suárez" \
      usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" aseguramiento="Andrea Costa" \
      autoridad_cambio="Sofía Ramírez" product_owner="Sofía Ramírez" jefes_equipo="Lucía Benítez"
  python3 $E/estado.py --proyecto gestion agil cadencia_iteracion_dias=14 velocidad_referencia=30
  python3 $E/registro.py --proyecto gestion agregar stakeholders --campo nombre="Consejo directivo" \
      --campo poder=alto --campo interes=medio --campo actitud=partidario --campo confidencial=no
  ```
- **Artefacto:** `00-direccion/estructura-organizativa.md` (organigrama Mermaid), `01-inicio/analisis-stakeholders.md` (circulación restringida), `02-planificacion/plan-compromiso-stakeholders.md` (cuatro brechas con acción), `stakeholders.csv` con seis interesados (ST-004 con `confidencial=si`).
- **Decisión humana:** dos puertas internas: Laura confirma diseño y nombramientos (decisión nivel `junta`) y Martín revisa las actitudes antes de guardarlas.

### 6. `pm-estado-proyecto` — tolerancias de proyecto
- **Petición:** "Fijá las tolerancias de proyecto que aprobó el consejo: más o menos 3 semanas, más o menos 8 % de costo y hasta 10 % menos de beneficios. ¿Qué falta para la puerta?"
- **Quién:** orquestador → `pm-inicio` → `pm-estado-proyecto`.
- **Qué pregunta o verifica:** que la decisión venga de la capa de negocio (el usuario cita el acta del consejo); que tiempo y costo estén presentes (mínimo obligatorio); que sean de nivel proyecto (las de etapa las fija la junta en cada `autorizar-etapa`).
- **Comandos:**
  ```bash
  python3 $E/estado.py --proyecto gestion tolerancia --nivel proyecto tiempo="±3 semanas" costo="±8 %" beneficios="-10 %"
  python3 $E/estado.py --proyecto gestion siguiente
  ```
- **Artefacto:** `estado.json.tolerancias.proyecto`. `siguiente` lista lo que falta para `autorizar-inicio`.
- **Decisión humana:** ya tomada por el consejo (capa de negocio); el script solo la registra. Si no hubiera acta, el subagente la devolvería como dato faltante.

### 7. `pm-caso-de-negocio` — business case esquemático
- **Petición:** "Armá el business case de una página a partir del mandato; todavía no tenemos costos firmes del proveedor."
- **Quién:** orquestador → `pm-inicio` → `pm-caso-de-negocio` (modo `esquematico`).
- **Qué pregunta o verifica:** cadena de valor (salida → capacidad → resultado → beneficio → objetivo de negocio); tres opciones empezando por "no hacer nada distinto"; cada beneficio medible con línea base, dueño, fecha y tolerancia. La tasa de descuento no la dio la organización: queda `[por confirmar]` a cargo de la ejecutiva. Lee SM-1 por la fachada y lo cita sin copiarlo.
- **Comandos:**
  ```bash
  python3 $E/especificacion.py --proyecto gestion consultar SM-1
  python3 $E/estado.py --proyecto gestion artefacto business-case --ruta 00-direccion/business-case.md --estado en-revision --version 0.9
  ```
- **Artefacto:** `00-direccion/business-case.md`: OBJ-1; B-01 (porcentaje de trámites por el portal, de 0 a 40 %, Refs SM-1 · KR-1.1), B-02 (NPS de 22 a 35, Refs KR-1.2), des-beneficio DB-01; payback ≈ 1,9 años con supuestos declarados.
- **Decisión humana:** la junta lo decide en `autorizar-inicio` (versión esquemática) y en `autorizar-proyecto` (versión 1.0); registra pm-director.

### 8. `pm-okr` — OKR ligados a beneficios
- **Petición:** "El consejo trabaja con OKR: armá los del proyecto a partir de los beneficios."
- **Quién:** orquestador → `pm-inicio` → `pm-okr`.
- **Qué pregunta o verifica:** que el business case tenga OBJ-n y B-nn numerados (si no, propone la numeración en el business case, no en el OKR); que cada KR cite un B-nn o un SM-n existente; que ningún KR sea una tarea.
- **Comandos:**
  ```bash
  python3 $E/especificacion.py --proyecto gestion consultar SM-1
  python3 $O gestion/00-direccion/okr.csv --plantilla
  python3 $O gestion/00-direccion/okr.csv --corte 2026-10-17 --markdown gestion/03-control/reportes/2026-10-17-okr.md
  python3 $E/estado.py --proyecto gestion artefacto okr --ruta 00-direccion/okr.md --estado en-revision
  ```
- **Artefacto:** `00-direccion/okr.csv` (O-1 → OBJ-1; KR-1.1 → B-01 + SM-1; KR-1.2 → B-02; KR-1.3 → B-01), `00-direccion/okr.md`, tabla puntuada. Sin avisos de vínculo; los tres KR salen en rojo porque todavía no hay medición, y el informe lo aclara.
- **Decisión humana:** la ejecutiva acepta objetivo y KR; con su respuesta, pm-director ejecuta `estado.py aprobar okr --por "Ejecutivo: Laura Méndez"`.

### 9. `pm-riesgos` — riesgos iniciales
- **Petición:** "Hagamos los riesgos iniciales: el proveedor es nuevo para nosotros, el padrón de socios está desactualizado y dependemos de la API del core bancario."
- **Quién:** orquestador → `pm-inicio` → `pm-riesgos`.
- **Qué pregunta o verifica:** objetivos con unidades y tolerancias antes de identificar; escala P×I aprobada (todavía no hay enfoque de riesgo, así que redacta la evaluación P×I y deja las puntuaciones como propuesta); causa → evento → efecto; propietario y ejecutor por riesgo; AD-n y NFR del PRD como fuentes.
- **Comandos:**
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar requisitos      # AD-1, AD-2, NFR-1
  python3 $E/registro.py --proyecto gestion agregar riesgos --campo categoria=externo \
      --campo causa="La API del core bancario no tiene entorno de pruebas (AD-2)" \
      --campo evento="La integración se prueba tarde" --campo efecto="Atraso del release 1" \
      --campo tipo=amenaza --campo probabilidad=4 --campo impacto=4 --campo impacto_monetario=30000 \
      --campo propietario="Diego Ferreira" --campo ejecutor="Lucía Benítez" --campo respuesta=reducir
  python3 $E/registro.py --proyecto gestion resumen --json
  ```
- **Artefacto:** `riesgos.csv` con R-001…R-005: R-001 puntuación 16 (alto) EMV 21.000; R-002 9, EMV 9.000; R-003 12, EMV 20.000; R-004 9, EMV 5.000; R-005 oportunidad 6, EMV 2.400. Resumen: un riesgo alto, ninguno sin respuesta ni propietario. `02-planificacion/enfoques/evaluacion-probabilidad-impacto.md` como propuesta.
- **Decisión humana:** la ejecutiva aprueba la escala (luego pm-director `estado.py aprobar evaluacion-probabilidad-impacto`); cada propietario acepta su respuesta.

### 10. `pm-registros` — supuesto y clasificación
- **Petición:** "Registrá un supuesto: el padrón de socios estará disponible en marzo."
- **Quién:** orquestador → `pm-control` (o directamente en el hilo principal en SU) → `pm-registros`.
- **Qué pregunta o verifica:** prueba de certeza (no ocurrió, no es riesgo todavía: es un supuesto); formal o informal (afecta el plan del release 2 → formal); responsable, que no se inventa: lo pide.
- **Comandos:**
  ```bash
  python3 $E/registro.py --proyecto gestion esquema supuestos
  python3 $E/registro.py --proyecto gestion agregar supuestos \
      --campo supuesto_o_restriccion="El padrón de socios depurado estará disponible en marzo de 2027" \
      --campo tipo=supuesto --campo validado=pendiente --campo responsable="Sofía Ramírez"
  ```
- **Artefacto:** fila S-002 en `supuestos.csv` (estado `abierto`). Si se hubiera usado una columna inexistente, `registro.py` la rechaza y lista las válidas; se corrige en lugar de forzar.
- **Decisión humana:** ninguna para el alta. Cerrar el supuesto (validado o invalidado) exige confirmación del gestor.

### 11. `/pm-puerta autorizar-inicio` — primera puerta
- **Petición:** `/pm-method:pm-puerta autorizar-inicio`
- **Quién:** orquestador → `pm-director` (modo A) → `pm-direccion-decisiones`, `pm-exportar`, `pm-bmad-puente`, `pm-sanidad`; luego orquestador → humano → `pm-director` (modo B).
- **Qué pregunta o verifica:** sanidad completa sin ERROR; obligatorios de la puerta presentes en `aprobado` o `en-revision`; cobertura de la especificación; desvíos de BMAD; traspasos pendientes. En la prueba, `verificar` encontró una Sprint Change Proposal previa: se registró como issue I-001 (`solicitud-cambio`), la autoridad de cambio difirió "notificaciones" como Could (D-003, nivel `autoridad-cambio`) y `verificar --marcar-vistas` dejó el desvío visto.
- **Comandos:**
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
- **Artefacto:** `00-direccion/decisiones/2026-10-17-solicitud-autorizar-inicio.md` (`en-revision`); tras la decisión, D-004 en `decisiones.csv`, fase `inicio`, proceso IP, etapa 1 "Iniciación".
- **Decisión humana:** el orquestador presenta las opciones (aprobar, condicionar, rechazar, pedir información, cierre prematuro) y pide nombre y rol. Laura Méndez aprueba. Sin esa respuesta no se registra nada.

---

## Parte 2 · Iniciación (IP, etapa 1)

### 12. `pm-enfoques-gestion` — enfoques del PID
- **Petición:** "Escribí los enfoques del PID en una página. Usamos BMAD: dejá claro cuándo un ajuste al PRD es elaboración y cuándo es solicitud de cambio."
- **Quién:** orquestador → `pm-inicio` → `pm-enfoques-gestion`.
- **Qué pregunta o verifica:** nivel de formalidad por enfoque; escalas iguales a las que acepta `registro.py`; tolerancias iguales a las de `estado.json`; integraciones conectadas (ninguna). En el enfoque de issues y cambios completa la sección 5.1: detallar un requisito sin cambiar ids es elaboración progresiva; agregar o retirar ids, cambiar la intención de un FR o de una SM-n o una Sprint Change Proposal es `solicitud-cambio`. Comunicación se escribe al final.
- **Comandos:**
  ```bash
  python3 $E/registro.py --proyecto gestion esquema issues
  python3 $E/estado.py --proyecto gestion artefacto enfoque-issues-cambios \
      --ruta 02-planificacion/enfoques/enfoque-issues-cambios.md --estado borrador
  ```
- **Artefacto:** `02-planificacion/enfoques/` con calidad (DoD/DoR, code review y gate de preparación de BMAD como métodos de verificación), riesgo, issues y cambios, comunicación, datos y tecnología digital, en versión de una página.
- **Decisión humana:** el gestor confirma el nivel por enfoque; la ejecutiva los aprueba con el PID en `autorizar-proyecto` (registra pm-director).

### 13. `pm-planificacion-por-productos` — PBS y WBS
- **Petición:** "Armá la PBS y la WBS con responsables; los requisitos están en el PRD, citá los ids."
- **Quién:** orquestador → `pm-planificacion` → `pm-planificacion-por-productos`.
- **Qué pregunta o verifica:** productos antes que actividades; regla del 100 %; un responsable por paquete; `ref` con ids que existen en la fachada; con BMAD no escribe requisitos. La descripción del producto del proyecto ya se había producido para `autorizar-inicio` y cita FR, NFR, UJ y AD.
- **Comandos:**
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar requisitos
  python3 $E/wbs.py gestion/02-planificacion/wbs.csv --mermaid gestion/02-planificacion/visuales/wbs.md \
      --diccionario gestion/02-planificacion/diccionario-wbs-esqueleto.md
  python3 $E/estado.py --proyecto gestion artefacto pbs-wbs --ruta 02-planificacion/pbs-wbs.md --estado en-revision --version 0.9
  ```
- **Artefacto:** `02-planificacion/wbs.csv` (15 elementos, 11 hojas), `visuales/wbs.md`, `diccionario-wbs.md`. Tras cargar estimación y costo, `wbs.py` consolida 2.760 h y USD 138.000.
- **Decisión humana:** la usuaria sénior aprueba las descripciones de producto; el conjunto se aprueba con el plan en `autorizar-proyecto`.

### 14. `pm-bmad-puente` — requisitos y trazabilidad
- **Petición:** "Trazá los FR del PRD a los paquetes de la WBS y decime qué requisitos no tienen historia."
- **Quién:** orquestador → `pm-planificacion` → `pm-bmad-puente`.
- **Qué pregunta o verifica:** que la carpeta del proyecto esté fuera de las de BMAD; versión de BMAD soportada; que los derivados se regeneren y no se editen.
- **Comandos:**
  ```bash
  python3 $B --proyecto gestion requisitos
  python3 $B --proyecto gestion trazabilidad --wbs 02-planificacion/wbs.csv
  ```
- **Artefacto:** `02-planificacion/especificacion/requisitos-bmad.csv` (9 ids: 4 FR, 1 NFR, 1 UJ, 1 SM, 2 AD) y `matriz-trazabilidad-bmad.csv`: FR-1 → paquetes 2.1, 3.1 y 3.2; FR-4 sin historia; la historia `1-2-recuperar-contrasena` sin requisito; cero referencias rotas.
- **Decisión humana:** ninguna directa. FR-4 sin historia va a la PO (pm-agil-hibrido) para planificarla; la historia sin requisito va a pm-calidad o a pm-issues-cambios si es alcance nuevo.

### 15. `pm-cronograma-estimacion` — camino crítico y MS Project
- **Petición:** "Estimá con PERT las actividades críticas, calculá el camino crítico y exportalo para abrirlo en MS Project."
- **Quién:** orquestador → `pm-planificacion` → `pm-cronograma-estimacion`.
- **Qué pregunta o verifica:** cada actividad con paquete (`wbs`), técnica, supuestos, estimador y confianza; `P ≥ M ≥ O`; fin contra el mandato y la tolerancia de tiempo; reserva fuera del estimado base.
- **Comandos:**
  ```bash
  python3 $E/cpm.py gestion/02-planificacion/actividades.csv --inicio 2026-11-09 \
      --mermaid gestion/02-planificacion/gantt.md \
      --mspdi gestion/02-planificacion/cronograma.xml --titulo "Portal de autoservicio" \
      --wbs gestion/02-planificacion/wbs.csv
  python3 $E/estado.py --proyecto gestion artefacto cronograma --ruta 02-planificacion/cronograma.md --estado en-revision
  ```
- **Artefacto:** `02-planificacion/cronograma.md` (120 días laborables, fin 2027-04-26, camino crítico A00→A02→A04→A05→A07→A08→A10), `gantt.md` y `cronograma.xml` (MSPDI con tareas resumen por paquete de la WBS).
- **Decisión humana:** ninguna en este paso; el cronograma se aprueba con el plan. Si el fin no entrara, pasaría opciones a la junta vía pm-director.

### 16. `pm-costos-presupuesto` — BAC y reservas
- **Petición:** "Costeá los paquetes y calculá la contingencia desde el registro de riesgos, sin duplicarla. El mandato dice 180 mil."
- **Quién:** orquestador → `pm-planificacion` → `pm-costos-presupuesto`.
- **Qué pregunta o verifica:** tarifas y cotizaciones con fuente (las del proveedor se piden a Diego); ningún paquete con reserva adentro; contingencia una sola vez, ligada a riesgos con EMV; total de `wbs.py` igual a la hoja de costeo; Σ PV = BAC.
- **Comandos:**
  ```bash
  python3 $E/wbs.py gestion/02-planificacion/wbs.csv
  python3 $E/registro.py --proyecto gestion listar riesgos --abiertos --json
  python3 $E/estado.py --proyecto gestion artefacto presupuesto --ruta 02-planificacion/presupuesto.md --estado en-revision
  python3 $E/estado.py --proyecto gestion artefacto linea-base-costo --ruta 02-planificacion/linea-base-costo.csv --estado en-revision
  ```
- **Artefacto:** `02-planificacion/presupuesto.md`: base 138.000 + contingencia 27.000 (EMV de R-001 y R-002 menos la oportunidad R-005) = BAC 165.000; reserva de gestión 15.000 fuera del BAC; presupuesto autorizado 180.000, igual al mandato. `linea-base-costo.csv` con PV por período.
- **Decisión humana:** la reserva de gestión es una propuesta: la aprueba la junta en `autorizar-proyecto`.

### 17. `pm-adquisiciones` — estrategia con el proveedor
- **Petición:** "El desarrollo lo hace un proveedor externo: armá el hacer o comprar y la estrategia, precio fijo por release con retención del 10 %."
- **Quién:** orquestador → `pm-inicio` (en IP) → `pm-adquisiciones`.
- **Qué pregunta o verifica:** costo total y riesgos de ambas opciones; tipo de contrato contra la definición del alcance (precio fijo exige alcance definido: el enunciado del trabajo cita los FR del PRD); hitos de pago en los límites de etapa; quién de compras y legal aprueba (lo pregunta).
- **Comandos:**
  ```bash
  python3 $E/estado.py --proyecto gestion artefacto estrategia-adquisiciones \
      --ruta 02-planificacion/adquisiciones/estrategia-adquisiciones.md --estado en-revision
  ```
- **Artefacto:** `02-planificacion/adquisiciones/estrategia-adquisiciones.md`; riesgos contractuales propuestos a pm-riesgos, hitos a pm-cronograma-estimacion, monto a pm-costos-presupuesto.
- **Decisión humana:** la estrategia se aprueba con el plan en `autorizar-proyecto`; adjudicación y firma son decisión de la autoridad de la cooperativa (Laura) con legal, y se devuelven como decisión humana requerida.

### 18. `pm-agil-hibrido` — backlog, release plan y DoD
- **Petición:** "Armá el backlog con MoSCoW y releases a partir de las historias de BMAD, y el release plan con DoD."
- **Quién:** orquestador → `pm-planificacion` → `pm-agil-hibrido` (usa pm-bmad-puente para las columnas derivadas).
- **Qué pregunta o verifica:** cadencia de 14 días y PO registrados; Must ≤ ~60 % de la capacidad; `Σ puntos Must+Should ≤ velocidad × iteraciones`; con BMAD, nada de historias a mano: el puente refresca las derivadas y la PO completa solo las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs).
- **Comandos:**
  ```bash
  python3 $B --proyecto gestion backlog            # primera sincronización: 4 historias nuevas
  # la PO completa las columnas de gobierno y agrega PM-001 (Could, por I-001)
  python3 $B --proyecto gestion backlog            # segunda: gobierno intacto, PM-001 se conserva
  python3 $B --proyecto gestion handoff            # prioridades de gobierno → documento para el equipo BMAD
  python3 $E/estado.py --proyecto gestion artefacto backlog --ruta 02-planificacion/backlog.csv --estado en-revision
  python3 $E/estado.py --proyecto gestion artefacto release-plan --ruta 02-planificacion/release-plan.md --estado en-revision
  ```
- **Artefacto:** `02-planificacion/backlog.csv`, `02-planificacion/release-plan.md` (cadencia, DoD/DoR, ceremonias, línea base), `02-planificacion/especificacion/handoff-bmad-<fecha>-prioridades.md`.
- **Decisión humana:** DoD y DoR las acuerdan el equipo y la usuaria sénior; backlog comprometido y release plan se aprueban con el plan de etapa en `autorizar-etapa`.

### 19. `pm-comunicacion-stakeholders` — matriz de comunicaciones
- **Petición:** "Armá la matriz de comunicaciones con el consejo, la junta, el equipo del proveedor y los socios piloto."
- **Quién:** orquestador → `pm-inicio` → `pm-comunicacion-stakeholders`.
- **Qué pregunta o verifica:** que exista el enfoque de comunicación (dueño pm-enfoques-gestion) y que la matriz lo respete; que todo `stakeholders.csv` quede cubierto; que las filas con `confidencial=si` no entren en comunicados amplios; idioma por audiencia.
- **Comandos:**
  ```bash
  python3 $E/registro.py --proyecto gestion listar stakeholders --json
  python3 $E/estado.py --proyecto gestion artefacto matriz-comunicaciones \
      --ruta 02-planificacion/matriz-comunicaciones.md --estado en-revision
  # tras la aprobación:
  python3 $E/registro.py --proyecto gestion actualizar stakeholders ST-001 --campo canal=correo --campo frecuencia=mensual
  ```
- **Artefacto:** `02-planificacion/matriz-comunicaciones.md` con la sprint review como evento recurrente.
- **Decisión humana:** la ejecutiva aprueba la matriz dentro del PID (pm-director `estado.py aprobar matriz-comunicaciones`).

### 20. `pm-acta-constitucion` — PID por referencia
- **Petición:** "Ya tenemos brief, business case, roles, enfoques y planes: armá el PID por referencia y decime qué falta para autorizar el proyecto."
- **Quién:** orquestador → `pm-inicio` → `pm-acta-constitucion`.
- **Qué pregunta o verifica:** `autorizar-inicio` aprobada; formato (PID índice, versión mínima); componentes con ruta, versión, estado, creador, revisor y aprobador; consistencia (presupuesto 180.000 en mandato, business case y presupuesto; tolerancias iguales a `estado.json`); con BMAD, PRD en `final` y `verificar` sin desvíos; plan de la etapa 2 presente.
- **Comandos:**
  ```bash
  python3 $B --proyecto gestion verificar
  python3 $E/estado.py --proyecto gestion artefacto pid --ruta 00-direccion/pid.md --estado en-revision --version 0.9
  ```
- **Artefacto:** `00-direccion/pid.md` (cita brief de producto, PRD y arquitectura por ruta y sha), copia `00-direccion/historial/pid-v0.9.md`, lista de bloqueantes (ninguno).
- **Decisión humana:** el gestor confirma el formato; la junta decide `autorizar-proyecto`.

### 21. `pm-direccion-decisiones` — autorizar el proyecto y la etapa 2
- **Petición:** "La junta del 6 de noviembre tiene que autorizar el proyecto y la primera etapa de entrega: prepará la decisión."
- **Quién:** orquestador → `pm-director` → `pm-direccion-decisiones` (modo A); orquestador → junta; orquestador → `pm-director` (modo B).
- **Qué pregunta o verifica:** justificación continua (deseable, viable, alcanzable) con el business case; productos requeridos; desempeño contra tolerancias; `verificar` limpio; ejecutivo nombrado. Redacta dos solicitudes con al menos tres opciones y recomendación con grado de confianza.
- **Comandos:**
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
- **Artefacto:** `00-direccion/decisiones/2026-11-06-solicitud-autorizar-proyecto.md` y `…-solicitud-autorizar-etapa.md`; acta `2026-11-06-acta-junta-autorizar-proyecto.md`; PID y business case v1.0 en `00-direccion/historial/`; líneas base `bmad-prd-v1.0/` (sha ea90ca87952b), `bmad-arquitectura-v1.0/`, `bmad-epicas-v1.0/`; fase `entrega`, proceso CS, etapa 2.
- **Decisión humana:** la junta (Laura decide; Sofía y Diego participan) aprueba ambas puertas. pm-director registra solo después de que el orquestador trae la respuesta literal con nombre y rol.

---

## Parte 3 · Etapa de entrega 2 (CS y MP)

### 22. `pm-integraciones` — proyecto sin conectores
- **Petición:** "No conectamos Jira ni Teams; las transcripciones las bajamos como archivo. ¿Cómo quedan las integraciones?"
- **Quién:** orquestador → `pm-control` → `pm-integraciones`.
- **Qué pregunta o verifica:** qué herramientas MCP hay en la sesión (ninguna de tracker, chat ni docs); qué capacidad queda cubierta por alternativa local.
- **Comandos:**
  ```bash
  python3 $E/estado.py --proyecto gestion integracion tracker=ninguno chat=ninguno docs=ninguno reuniones=archivo okr=archivo
  ```
- **Artefacto:** `estado.json.integraciones` y una nota en `diario.md`. Las alternativas son el `backlog.csv`, la transcripción por archivo, borradores de mensajes para copiar y `okr.csv`.
- **Decisión humana:** ninguna. La skill sugiere conectar un tracker si el equipo lo usa, sin bloquear el trabajo (ver variante C).

### 23. `pm-paquetes-trabajo` — el sprint 3 como paquete
- **Petición:** "Autorizá el sprint 3 como paquete de trabajo para el equipo de Lucía; la etapa 2 ya está aprobada."
- **Quién:** orquestador → `pm-control` → `pm-paquetes-trabajo`.
- **Qué pregunta o verifica:** fase `entrega`, proceso CS y `autorizar-etapa` aprobada; descripciones de producto con revisor independiente y autoridad de aceptación; tolerancias del paquete dentro de las de la etapa; frecuencia de checkpoint; con proveedor, coherencia con el contrato. Alcance = ids de historias, sin copiar texto.
- **Comandos:**
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar historias --epica E-1
  python3 $E/registro.py --proyecto gestion agregar calidad --campo producto="1-1-login-de-socio" \
      --campo metodo_verificacion=prueba --campo criterios="Criterios de la historia y NFR-1" \
      --campo responsable_productor="Lucía Benítez" --campo revisores="Andrea Costa" --campo aprobador="Sofía Ramírez"
  # tras el acuerdo:
  python3 $E/registro.py --proyecto gestion agregar decisiones --campo decision="WP-003 autorizado y aceptado" \
      --campo decidido_por="Gestor: Martín Suárez; Jefa de equipo: Lucía Benítez" --campo nivel=equipo
  ```
- **Artefacto:** `03-control/paquetes-trabajo/WP-003-sprint-3.md` (`estado_paquete: autorizado` tras el acuerdo) y filas Q-### en `calidad.csv`.
- **Decisión humana:** dos actos: el gestor autoriza y la jefa de equipo acepta. pm-control los devuelve como decisión humana; con las respuestas, escribe la fila de aceptación. Si además se quiere marcar el documento WP-003 como aprobado con `estado.py aprobar`, lo ejecuta pm-director.

### 24. `pm-reuniones` — acta del checkpoint
- **Petición:** "Te paso el VTT del checkpoint del sprint 3: armá el acta y proponé las acciones."
- **Quién:** orquestador → `pm-control` → `pm-reuniones`.
- **Qué pregunta o verifica:** nombre, tipo, fecha y quién presidió (Martín); hablantes `?` o nombres partidos tras normalizar; clasificación de cada hallazgo (acción ≠ issue; riesgo = incierto); decisiones de junta marcadas para pm-director. No hay consentimiento para análisis de clima, así que ese paso no corre.
- **Comandos:**
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
- **Artefacto:** transcripción normalizada (9 intervenciones, 3 hablantes), `03-control/reuniones/2026-12-03-acta-checkpoint-sprint3.md`, y tras confirmar: D-026, A-001 (Lucía, 2026-12-11), A-002 (Sofía, 2026-12-09), R-006 (P4 × I3 = 12, EMV 8.400) e I-002 (`problema-preocupacion`).
- **Decisión humana:** Martín, que presidió, confirma el acta y la lista de cargas. Nada entra a los registros antes.

### 25. `pm-calidad` — aceptación por requisito del login
- **Petición:** "¿Qué FR del release 1 ya podemos dar por aceptados? Armá la aceptación del login."
- **Quién:** orquestador → `pm-control` → `pm-calidad`.
- **Qué pregunta o verifica:** dos evidencias (control del proyecto y revisión independiente); fila Q-### con resultado `aprobado`; cobertura `terminado` de la fachada; `done` en BMAD no alcanza por sí solo.
- **Comandos:**
  ```bash
  python3 $E/especificacion.py --proyecto gestion listar requisitos --cobertura terminado
  python3 $E/registro.py --proyecto gestion actualizar calidad Q-001 --campo resultado=aprobado \
      --campo estado=completada --campo fecha_real=2026-12-09
  ```
- **Artefacto:** `03-control/reportes/2026-12-10-aceptacion-login.md` (clave `aceptacion-login`).
- **Decisión humana:** Sofía acepta como autoridad nombrada; con su respuesta, pm-director ejecuta `estado.py aprobar aceptacion-login --por "Usuario sénior: Sofía Ramírez" --nivel junta` y se actualiza el product status account.

### 26. `/pm-reporte highlight` — informe de la quincena
- **Petición:** `/pm-method:pm-reporte highlight`
- **Quién:** orquestador → `pm-control` → `pm-progreso-reportes`.
- **Qué pregunta o verifica:** período y fecha de corte (2026-12-10); conteos idénticos a `registro.py resumen`; semáforo contra tolerancias de etapa; desvíos de BMAD del período.
- **Comandos:**
  ```bash
  python3 $E/registro.py --proyecto gestion resumen --json --corte 2026-12-10
  python3 $E/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 95000 --tol-costo 10 --tol-plazo 14 --proyecto gestion
  python3 $B --proyecto gestion avance
  python3 $B --proyecto gestion verificar
  python3 $E/estado.py --proyecto gestion artefacto highlight-2026-12-10 \
      --ruta 03-control/reportes/2026-12-10-highlight-report.md --estado en-revision
  ```
- **Artefacto:** `03-control/reportes/2026-12-10-highlight-report.md`: PV 52.000, EV 47.000, AC 50.000, SPI 0,90, CPI 0,94, EAC 101.064, costo y plazo en ámbar, sin excepción; avance BMAD 13/21 puntos (61,9 %); 6 riesgos abiertos (1 alto), 1 issue abierto, A-002 vencida.
- **Decisión humana:** aseguramiento (Andrea) confirma; con la revisión del gestor, pm-director ejecuta `estado.py aprobar highlight-2026-12-10 --por "Gestor: Martín Suárez"`. Publicarlo en un canal requiere confirmación aparte.

### 27. `pm-progreso-reportes` — ¿estamos cerca de la tolerancia de proyecto?
- **Petición:** "La junta pregunta qué tan cerca estamos de la tolerancia de costo del proyecto. Calculalo y decime qué EAC usar."
- **Quién:** orquestador → `pm-control` → `pm-progreso-reportes`.
- **Qué pregunta o verifica:** BAC vigente sin reserva de gestión (165.000); método del EV declarado; dos EAC y la elegida justificada; se compara el pronóstico, no el acumulado. Corre además una prueba de sensibilidad.
- **Comandos:**
  ```bash
  python3 $E/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 165000 --tol-costo 8 --proyecto gestion
  python3 $E/evm.py --pv 52000 --ev 47000 --ac 51000 --bac 165000 --tol-costo 8 --json     # sensibilidad
  ```
- **Artefacto:** respuesta con EAC 175.532 (−6,4 %, ámbar). Con AC 51.000, VAC −8,5 % supera el 8 %: el script marca `excepcion_prevista` y avisa que hay que preparar el informe de excepción. Si se pide, `03-control/reportes/2026-12-10-analisis-valor-ganado.md`.
- **Decisión humana:** dentro de tolerancia, el gestor confirma acciones correctivas (van a `acciones.csv`). Si el pronóstico real saliera de tolerancia, pm-control emitiría el informe de excepción con la plantilla de pm-issues-cambios y lo derivaría a pm-director.

### 28. `pm-visuales` — tablero con vista por actor
- **Petición:** "Generá el tablero de esta semana con la vista por actor para mandarle a cada uno su link."
- **Quién:** orquestador → `pm-control` → `pm-visuales`.
- **Qué pregunta o verifica:** fuentes del tablero (highlight vigente, `evm.py --json`, registros, `avance-bmad.csv`); que los objetivos en rojo tengan issue o excepción; que las acciones salgan de `acciones.csv` y no de `issues.csv`; legibilidad y fecha de corte.
- **Comandos:**
  ```bash
  python3 $E/evm.py --csv gestion/03-control/reportes/progreso.csv --bac 95000 --tol-costo 10 --tol-plazo 14 --json
  python3 $E/registro.py --proyecto gestion listar acciones --abiertos --json
  python3 $E/registro.py --proyecto gestion listar riesgos --abiertos --json
  python3 $E/especificacion.py --proyecto gestion resumen --json
  python3 $E/estado.py --proyecto gestion artefacto tablero-avance \
      --ruta 03-control/reportes/2026-12-10-tablero-avance.html --estado borrador
  ```
- **Artefacto:** `03-control/reportes/2026-12-10-tablero-avance.html` (2 acciones, 6 riesgos, 1 issue). Con `?actor=Sofía Ramírez` muestra A-002 vencida y los riesgos R-003, R-004 y R-006 de los que es propietaria.
- **Decisión humana:** el gestor confirma antes de compartirlo. Sin chat conectado, se entrega el texto con los enlaces para pegar.

### 29. `/pm-estado` — dónde estamos
- **Petición:** `/pm-method:pm-estado`
- **Quién:** orquestador → skill-comando `pm-estado` (scripts de pm-estado-proyecto, pm-sanidad y pm-bmad-puente).
- **Qué pregunta o verifica:** fase, proceso y etapa; tolerancias y excepción abierta; puertas pendientes; ERROR de sanidad; avance BMAD.
- **Comandos:**
  ```bash
  python3 $E/estado.py --proyecto gestion ver
  python3 $E/estado.py --proyecto gestion siguiente
  python3 $E/registro.py --proyecto gestion resumen
  python3 $E/sanidad.py --proyecto gestion --rapido
  python3 $B --proyecto gestion avance
  ```
- **Artefacto:** ninguno nuevo; una fila en `03-control/reportes/avance-bmad.csv` (una por fecha de corte).
- **Decisión humana:** ninguna. El siguiente paso se muestra con el rol que decide.

### 30. `/pm-sync bmad` — el PRD cambió
- **Petición:** `/pm-method:pm-sync bmad` (el equipo BMAD corrió una corrección de rumbo y agregó FR-5 al PRD).
- **Quién:** orquestador → `pm-control` → `pm-bmad-puente`, `pm-sanidad`.
- **Qué pregunta o verifica:** cobertura y requisitos sin historia; desvíos contra la línea base; Sprint Change Proposals nuevas; traspasos pendientes en `estado.json.integraciones.bmad.handoffs`; columnas de gobierno intactas.
- **Comandos:**
  ```bash
  python3 $E/especificacion.py --proyecto gestion resumen
  python3 $B --proyecto gestion backlog
  python3 $B --proyecto gestion avance
  python3 $B --proyecto gestion verificar --json
  python3 $E/sanidad.py --proyecto gestion
  ```
- **Artefacto:** `verificar` informa `desvio bmad-prd v1.0 · agregados ['FR-5']` y `sprint-change-proposal-2027-01-12.md`. La skill propone un issue `solicitud-cambio`; no lo crea sola.
- **Decisión humana:** el gestor confirma que se registre el issue. El "sí" del flujo de corrección de rumbo de BMAD no aprueba nada en PRINCE2.

### 31. `pm-sanidad` — "algo no cuadra"
- **Petición:** "Algo no cuadra: el tablero muestra cuatro historias y el equipo dice que hay un requisito nuevo. Revisá la sanidad."
- **Quién:** orquestador en el hilo principal → `pm-sanidad` (sin subagente; la tabla de enrutamiento la deja en el hilo principal).
- **Qué pregunta o verifica:** las seis familias de controles. Encuentra ESP-10: la especificación difiere de su línea base y ningún issue la cita (cambio no controlado), que siempre es ERROR.
- **Comandos:**
  ```bash
  python3 $E/sanidad.py --proyecto gestion --informe
  python3 $E/registro.py --proyecto gestion agregar acciones --campo origen=sanidad-2027-01-13 \
      --campo descripcion="Tramitar FR-5 como solicitud de cambio" --campo responsable="Martín Suárez" \
      --campo fecha_compromiso=2027-01-14
  ```
- **Artefacto:** `03-control/reportes/2027-01-13-sanidad.md` y una acción con responsable. El ERROR se deriva a pm-issues-cambios. Mientras siga abierto, no se presenta ninguna puerta, salvo que el humano decida seguir y quede como condición.
- **Decisión humana:** ninguna para el informe. `--reparar` no se usa: solo agregaría columnas faltantes o reconstruiría el índice, y no corrige datos de negocio.

### 32. `pm-issues-cambios` — solicitud de cambio por FR-5
- **Petición:** "`bmad.py verificar` dice que el PRD tiene un FR nuevo desde la línea base: armá la solicitud de cambio y decime quién la aprueba."
- **Quién:** orquestador → `pm-control` → `pm-issues-cambios`; luego `pm-director`.
- **Qué pregunta o verifica:** tipo (uno de cinco: `solicitud-cambio`); impacto sobre los siete objetivos (+5 puntos, +USD 4.500 = 2,7 % del BAC, 0 días en el camino crítico); al menos dos opciones; autoridad: la autoridad de cambio delegada no tiene presupuesto de cambio suficiente y el cambio consume reserva de gestión, así que decide la junta.
- **Comandos:**
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
- **Artefacto:** I-003, C-001, `03-control/reportes/2027-01-13-solicitud-cambio-C-001.md`, D-028, `02-planificacion/especificacion/handoff-bmad-<fecha>-C-001.md`, `00-direccion/historial/bmad-prd-v1.1/` (sha 661eccce6457). Luego pm-planificacion agrega el paquete 3.7 a la WBS: base 142.500, BAC 169.500, reserva remanente 10.500.
- **Decisión humana:** la junta aprueba C-001 con Laura como decisora. El agente nunca decide un cambio.

### 33. `pm-knowledge` — una pregunta de método
- **Petición:** "¿Quién puede aprobar un cambio que consume reserva de gestión, y para qué está la autoridad de cambio?"
- **Quién:** orquestador en el hilo principal → `pm-knowledge`.
- **Qué pregunta o verifica:** clasifica la pregunta (método PRINCE2 con una convención del paquete); localiza la sección con `grep` y lee solo esa.
- **Comandos:**
  ```bash
  grep -n '^### 3\.' "$PM/pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md"
  ```
- **Artefacto:** ninguno. Respuesta en palabras propias: la autoridad de cambio decide dentro de su umbral y presupuesto de cambio; por encima, o si se toca la reserva de gestión, decide la junta (SPEC §1.10.6: la reserva de gestión queda fuera del BAC y solo la libera la junta). Cita archivo y encabezado.
- **Decisión humana:** ninguna. Si el usuario pidiera "entonces aprobalo", la petición pasa a pm-director vía el orquestador.

---

## Parte 4 · Límite de etapa (SB)

### 34. `pm-lecciones-aprendidas` — taller de la etapa 2
- **Petición:** "Facilitá el taller de lecciones de la etapa 2 con estrella de mar y registrá que el proveedor no tenía entorno de pruebas del core."
- **Quién:** orquestador → `pm-control` (en SB) → `pm-lecciones-aprendidas`.
- **Qué pregunta o verifica:** acciones del taller anterior; formato y facilitador declarados (ambiente sin culpas); 1–3 acciones con dueño y fecha; aciertos además de problemas; si alguien pide "la retro del sprint", eso es de pm-agil-hibrido.
- **Comandos:**
  ```bash
  python3 $E/registro.py --proyecto gestion agregar lecciones --campo etapa=2 \
      --campo situacion="El proveedor no tenía entorno de pruebas del core bancario" \
      --campo efecto="R-001 se materializó parcialmente; cinco días de atraso" \
      --campo recomendacion="Incluir el entorno de pruebas como condición contractual del primer hito" \
      --campo prioridad=alta --campo responsable_seguimiento="Martín Suárez" --campo notas="R-001; impacto_organizacional=si"
  python3 $E/registro.py --proyecto gestion listar lecciones --abiertos
  ```
- **Artefacto:** L-002, `03-control/reportes/2027-02-12-retrospectiva-etapa-2.md`, `03-control/reportes/2027-02-12-informe-lecciones-etapa-2.md`.
- **Decisión humana:** aseguramiento confirma responsables y la junta revisa; luego pm-director ejecuta `estado.py aprobar informe-lecciones-etapa-2 --por "Ejecutivo: Laura Méndez"`. Elevar L-002 a la organización lo decide la ejecutiva.

### 35. `pm-plan-etapa-y-limites` — cerrar la etapa 2 y planificar la 3
- **Petición:** "Cerrá la etapa 2: informe de fin de etapa, plan de la etapa 3, y verificá si cambió el PRD."
- **Quién:** orquestador → `pm-control` (`limite-etapa`) + `pm-planificacion` → `pm-plan-etapa-y-limites`; luego `pm-director`.
- **Qué pregunta o verifica:** reales y pronósticos contra tolerancias; business case actualizado (vía pm-caso-de-negocio); lecciones incorporadas al plan siguiente; especificación antes de la puerta; traspasos pendientes; gate de sprint planning de BMAD como insumo.
- **Comandos:**
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
- **Artefacto:** informe de fin de etapa 2 (avance 16/21 puntos = 76,2 %, épicas 1/2, sin desvíos), `02-planificacion/plan-etapa-3.md` (BAC de etapa 74.500), solicitud `00-direccion/decisiones/2027-02-12-solicitud-autorizar-etapa.md`.
- **Decisión humana:** la junta decide `autorizar-etapa`; pm-director registra `estado.py puerta autorizar-etapa --decision aprobado --por "Ejecutivo: Laura Méndez" --etapa-nombre "Release 2 y transición" --fin 2027-04-26` y las tolerancias de la etapa 3. Pasa a CS, etapa 3.

### 36. `pm-exportar` — paquete de puerta y Excel
- **Petición:** "Armá el paquete de puerta para autorizar la etapa 3 y exportá los registros a Excel para la junta del jueves."
- **Quién:** orquestador → `pm-director` (preparación de puerta) → `pm-exportar`.
- **Qué pregunta o verifica:** obligatorios de la puerta (faltante o borrador = ZIP `-BORRADOR`); solicitud incluida; estado de cada fuente; que la hoja de stakeholders con valoraciones no vaya en paquetes para terceros.
- **Comandos:**
  ```bash
  python3 $X --proyecto gestion listar puerta autorizar-etapa
  python3 $X --proyecto gestion puerta autorizar-etapa \
      --extra 02-planificacion/especificacion/matriz-trazabilidad-bmad.csv 00-direccion/historial/bmad-prd-v1.1/prd.md
  python3 $E/exportar.py xlsx --proyecto gestion --salida gestion/exportados/2027-02-12-registros-v1.xlsx
  ```
- **Artefacto:** `exportados/2027-02-12-paquete-autorizar-etapa-v1.zip` con `MANIFIESTO.md` y `exportados/2027-02-12-registros-v1.xlsx` (una hoja por registro). Nota en `diario.md`.
- **Decisión humana:** el usuario confirma antes de enviar o subir los archivos; el envío lo hace pm-comunicacion-stakeholders.

---

## Parte 5 · Cierre (CP)

### 37. `pm-cierre-proyecto` — cierre planificado
- **Petición:** "Estamos terminando la etapa 3: prepará el cierre y decime qué falta aceptar."
- **Quién:** orquestador → `pm-cierre` → `pm-cierre-proyecto` (con pm-bmad-puente, pm-caso-de-negocio, pm-lecciones-aprendidas, pm-adquisiciones); luego `pm-director`.
- **Qué pregunta o verifica:** aceptación por requisito con la fachada; con BMAD, `verificar` limpio y sin traspasos pendientes (el desvío de épicas por FR-4 y FR-5 se trató como elaboración progresiva, I-004, y nueva línea base de épicas 1.1); handover con propietario de operación; beneficios pendientes con dueño y fecha; contratos con sus tres condiciones; variaciones contra el PID y el business case v1.0.
- **Comandos:**
  ```bash
  python3 $E/estado.py --proyecto gestion cierre
  python3 $E/especificacion.py --proyecto gestion listar requisitos
  python3 $B --proyecto gestion verificar
  python3 $E/evm.py --pv 169500 --ev 169500 --ac 171000 --bac 169500 --tol-costo 8
  python3 $E/registro.py --proyecto gestion resumen --corte 2027-04-30
  python3 $X --proyecto gestion listar cierre
  ```
- **Artefacto:** en `04-cierre/`: `registro-aceptacion.md` (FR-1 a FR-5 aceptados; NFR-1 con concesión), `handover.md`, `recomendaciones-seguimiento.md`, `plan-revision-beneficios.md` (B-01 medido el 2027-07-26 y el 2027-10-26; B-02 el 2027-11-30), `informe-lecciones.md`, `informe-fin-proyecto.md` (CPI 0,991, SPI 1,00, VAC −1.500), `notificacion-cierre.md` en borrador.
- **Decisión humana:** dos puertas. Aceptación: Sofía acepta y Laura confirma; pm-director ejecuta `estado.py aprobar registro-aceptacion --por "Usuario sénior: Sofía Ramírez; Ejecutivo: Laura Méndez"`. Cierre: la junta autoriza y pm-director registra `estado.py puerta autorizar-cierre --decision aprobado --por "Ejecutivo: Laura Méndez" --fecha 2027-05-07`; la fase pasa a `cerrado` y `siguiente` recuerda las revisiones de beneficios. La notificación la firma la ejecutiva y se envía con confirmación. El ZIP de cierre sale con `python3 $X --proyecto gestion cierre`.

---

## Variantes

### Variante A · Predictivo sin BMAD: renovación de la red de sucursales
Proyecto de infraestructura con 12 sucursales, presupuesto fijo y sin capa de especificación. Lo que cambia respecto del ejemplo principal:

| Momento | Petición | Quién | Comandos y efecto |
|---|---|---|---|
| Arranque | `/pm-method:pm-nuevo "Renovación de red de sucursales" ./red es predictivo` | orquestador → pm-nuevo | `nuevo_proyecto.py … --enfoque predictivo`; no encuentra carpetas de BMAD, así que `integraciones.especificacion` queda distinta de `bmad`. |
| Requisitos | "Elicitá los requisitos con las áreas de sucursales y armá la matriz de trazabilidad." | orquestador → pm-planificacion → pm-planificacion-por-productos | Escribe `02-planificacion/requisitos.md` (filas REQ-001…) y `matriz-trazabilidad.md`; la columna `ref` de `wbs.csv` cita REQ-###. |
| Lectura | Cualquier skill que necesite requisitos | todas | `especificacion.py --proyecto red resumen` responde igual que con BMAD; el proveedor es pm-method (`requisitos.md`, `backlog.csv`, `wbs.csv`). |
| Cronograma | "Exportá el cronograma a MS Project." | pm-planificacion → pm-cronograma-estimacion | `cpm.py red/02-planificacion/actividades.csv --inicio 2027-01-11 --mermaid red/02-planificacion/gantt.md --mspdi red/02-planificacion/cronograma.xml --wbs red/02-planificacion/wbs.csv`. |
| Avance | `/pm-reporte highlight` | pm-control → pm-progreso-reportes | `evm.py --csv … --bac … --tol-costo … --tol-plazo …` en modo predictivo; sin `bmad.py avance` ni `verificar`. |
| Cambio | "Sucursales pide agregar Wi-Fi para socios." | pm-control → pm-issues-cambios | `solicitud-cambio` y C-###; si se aprueba, `requisitos.md` lo actualiza pm-planificacion-por-productos. No hay `bmad.py handoff`. |

Las puertas, los roles y la regla de que solo pm-director registra no cambian.

### Variante B · Agile project in English: member mobile app
Equipo de producto que trabaja en inglés con fecha y costo fijos. Las skills responden y generan en inglés; los datos faltantes salen como `[to be confirmed]`.

| Momento | Petición (tal como se escribe) | Quién | Comandos y efecto |
|---|---|---|---|
| Arranque | `/pm-method:pm-nuevo "Member app" ./app en agil` | orquestador → pm-nuevo | `estado.json.idioma = en`, `enfoque_entrega = agil`. |
| Perfil | "Small agile app, fixed date: minimal profile, ask me only once." | orquestador → pm-inicio → pm-mandato-y-brief | Perfil ágil mínimo: brief ligero, visión con MVP; las dos confirmaciones (formalidad y enfoque) se combinan en una. |
| Backlog | "Create the MoSCoW backlog using the minimal agile profile; we have no WBS." | pm-planificacion → pm-agil-hibrido | `backlog.csv` reemplaza a PBS, WBS, diccionario y flujo; release plan por etapas con DoD/DoR. Las puertas de etapa siguen. |
| Sprint | "Set up sprint 4 as a work package: these are the committed backlog items and the definition of done." | pm-control → pm-paquetes-trabajo | WP con alcance = ids de ítems, DoD como criterio de calidad. |
| Swap | "The PO wants to swap the PDF export story for the filters story." | pm-control → pm-agil-hibrido | Should por Should, sin tocar Must, fecha ni costo: decisión `nivel=product-owner` con `registro.py agregar decisiones`; no hay solicitud de cambio. |
| EVM | "Run agile EVM for sprint 6: we are on budget but behind on points." | pm-control → pm-progreso-reportes | `evm.py --pv … --ev … --ac … --bac … --modo agil --pct-no-must 30 --idioma en`: EAC > BAC se lee como alcance que no entra; hay excepción solo si peligran los Must. |
| Retro | "Let's run the sprint 6 retrospective." | pm-control → pm-agil-hibrido | `03-control/reportes/<date>-retrospectiva-S6.md`; el taller de etapa sigue siendo de pm-lecciones-aprendidas. |

### Variante C · Proyecto con Jira y Teams conectados vía pm-integraciones
Mismo portal de socios, pero el proveedor gestiona sus tickets en Jira y la cooperativa usa Teams. El usuario conectó los servidores MCP en su cliente (el paquete no trae conectores ni credenciales).

1. **Detectar y registrar.** Petición: "Ya conectamos Jira y Teams: configurá las integraciones." Orquestador → pm-control → pm-integraciones. La skill revisa las herramientas `mcp__<servidor>__<herramienta>` presentes y las clasifica por capacidad. Con el servidor oficial de Atlassian (Rovo MCP Server) primero obtiene el `cloudId` con su herramienta de recursos accesibles. Para Teams, avisa que el servidor "Teams (preview)" de Microsoft figura como legado y que conviene usar el que la organización tenga aprobado (por ejemplo Work IQ).
   ```bash
   python3 $E/estado.py --proyecto gestion integracion tracker=jira chat=teams
   ```
2. **Leer sin confirmación.** Petición: "Traé los tickets abiertos del sprint actual de Jira." Consulta por JQL y guarda una instantánea inmutable `03-control/fuentes/jira-2026-12-10.csv` con columnas `clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url`.
3. **Conciliar.** Compara la instantánea con `backlog.csv`, `acciones.csv` e `issues.csv`. Las diferencias se proponen; un ticket de alcance que no rastrea al backlog va a pm-issues-cambios. Las columnas de gobierno (moscow, release, producto_pbs, prioridad) siguen siendo solo de pm-method; la clave de Jira se guarda en `notas` como `jira:ABC-12`.
4. **Escribir con confirmación.** Petición: "Creá tickets en Jira para las acciones abiertas del proveedor." Como corre en un subagente, pm-control devuelve la vista previa exacta (proyecto Jira, resumen, asignado, vencimiento) como decisión humana requerida. El orquestador la muestra, Martín confirma el lote, y recién entonces se crean los tickets; las claves quedan en `notas` de cada A-###.
5. **Publicar.** Petición: "Publicá el highlight de esta semana en el canal del proyecto en Teams." pm-integraciones prepara el mensaje en el idioma de la audiencia según la matriz de comunicaciones; vista previa → confirmación del gestor → publicación → anotación en `diario.md`.
6. **Informes.** pm-progreso-reportes y pm-visuales citan la instantánea `jira-2026-12-10.csv` como fuente; riesgos, issues y acciones siguen saliendo de los registros. `/pm-sync tracker` repite la lectura en cada período y crea una instantánea nueva por fecha.

Si una herramienta falla dos veces o no tiene la operación, la skill lo informa y ofrece la alternativa local (CSV, Markdown o borrador para copiar).
