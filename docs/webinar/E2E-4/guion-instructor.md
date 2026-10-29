# Guion del instructor · E2E-4 · Producto con BMAD gobernado con PRINCE2

Guía del caso: [E2E-4-producto-bmad.md](../../guias/E2E-4-producto-bmad.md) · Evidencia:
[salida-g4.md](../../guias/evidencia/salida-g4.md) · Ejercicio: [ejercicio.md](ejercicio.md) · Diapositivas:
[diapositivas.json](diapositivas.json). Todas las cifras de este guion salen de la evidencia de la corrida de referencia.
Los números de diapositiva de las agendas cuentan dentro de cada clase, sin las portadas que agrega el generador.

## Por qué dos clases

El caso responde dos preguntas distintas y cada una necesita su demostración completa:

1. **Clase 1 · Gobernar la construcción con BMAD.** ¿Cómo controla la junta lo que construye un equipo que especifica
   con BMAD, sin copiar la especificación? Condición formal, paquete de trabajo, valor ganado, cambio con presupuesto y
   calidad a volumen por entrega (pasos 1 a 6). Termina con el Release 1 revisado historia por historia.
2. **Clase 2 · Recorrido, lecciones, cierre y beneficios.** ¿Cómo se llega a la puerta de cierre con cada dolor de la
   socia tratado y cada lección de la retrospectiva convertida en un cambio verificado, cómo se entrega a la auditoría
   una evidencia que no se puede editar sin que se note y, meses después, cómo se sabe si valió la pena? Pasos 6b a 11,
   con 6c y 9b.

La idea y el diseño del proyecto se ven en [E2E-5](../../guias/E2E-5-idea-a-proyecto.md); aquí el paso 1 se resume en
5 minutos.

## Objetivos de aprendizaje

Al terminar, cada asistente puede:

1. Explicar la división de trabajo: BMAD especifica y construye; pm-method gobierna y nunca escribe en `_bmad-output/`.
2. Convertir una aprobación "con condiciones" en una condición formal con seguimiento y cierre registrado, y decidir
   con las decisiones vigentes (lo reemplazado queda en la historia).
3. Controlar un cambio con costo y cargo contra el presupuesto de cambio de la junta.
4. Diseñar la calidad **por entrega** (una revisión registrada por historia) y tratar un rechazo con traza, comparando
   corregir y conceder.
5. Mapear el recorrido del cliente sobre lo entregado y darle a cada dolor un tratamiento con id.
6. Llevar una lección de la retrospectiva hasta el cambio que produce: clasificada por impacto y ámbito, con acción en
   el sprint o en el plan de la etapa, verificada, y compartida en el índice de la organización.
7. Entregar a una auditoría un expediente armado desde los registros, verificar la integridad de cada copia y mostrar
   con la bitácora de escrituras si un cambio salió o no de los scripts.
8. Distinguir puntaje de OKR, salud contra la trayectoria y tolerancia de beneficios al revisar beneficios después del
   cierre.

## Requisitos previos

- **Asistentes:** nociones de etapas, puertas y business case (PRINCE2 o PMBOK) o experiencia liderando iniciativas.
  No hace falta saber programar ni conocer BMAD.
- **Instructor:** Claude Code con pm-method; copia del fixture `scripts/pruebas/fixtures/bmad-v6.12-real` en
  `~/proyectos-prueba/portal-e2e-4`; la evidencia y las imágenes `docs/guias/img/g4-*.png` abiertas en pestañas; para
  la clase 2, el driver `scripts/pruebas/guias_e2e/g4.py` ya corrido (menos de un minuto) y su carpeta abierta, con
  `02-planificacion/visuales/recorrido-uj-1.html` en el navegador; para la demostración del paso 6c en vivo, copiá la
  transcripción de la retrospectiva (está en la evidencia, paso 6c) a
  `gestion/03-control/reuniones/2027-02-26-retro-sprint-4-original.vtt`.
- **Opcional, para el paso 9c:** pm-kb instalado ([INSTALACION-WSL2.md](../../INSTALACION-WSL2.md) §8 o
  [INSTALACION-DOCKER.md](../../INSTALACION-DOCKER.md) §8); sin pm-kb, el paso se muestra con la evidencia.
- **Recomendado:** haber dado E2E-5 antes (la idea y el diseño del mismo tipo de proyecto).

## El ejercicio

La hoja es una sola para asistentes e instructor: [ejercicio.md](ejercicio.md) (en HTML, `E2E-4-ejercicio.html`). Se
basta sola: empieza por «Cómo funciona este ejercicio», resume el escenario y los conceptos que hacen falta, trae la
hoja de trabajo con sus criterios de autoevaluación y termina con un **ejemplo resuelto** con el escenario del caso,
plegado, donde cada dato cita el paso de la guía de donde sale.

- **Cuándo:** la parte A en el minuto 75 de la clase 1 y la parte B en el minuto 75 de la clase 2, siempre después de
  la demostración; 10 minutos la parte A y de 10 a 15 la parte B (si el tiempo aprieta, B1 y B2 en clase y B3
  después).
- **Cómo se presenta:** proyectá la diapositiva del ejercicio y leé en voz alta «Cómo funciona este ejercicio» (un
  minuto). Quien no tenga un proyecto propio trabaja con los datos de partida del caso, que están en «Lo que necesitás
  saber».
- **Mientras trabajan:** pedí casos concretos: una condición con verificador y evidencia, una entrega con su foto de
  calidad, un paso del recorrido con su fuente, una lección con su cita y su fecha de verificación.
- **Ejemplo resuelto:** pedí que no lo abran antes de intentar. Mostralo recién en los dos últimos minutos del bloque:
  desplegalo en pantalla y comparalo con la hoja de uno o dos voluntarios. Al imprimir, sale desplegado al final de la
  hoja.
- **Autoevaluación:** cada asistente marca los criterios de su parte; un criterio sin cumplir es un hallazgo sobre su
  proyecto, no un error del ejercicio.

## Clase 1 · Gobernar la construcción con BMAD (90 min)

| Min | Bloque | Qué se hace | Material |
|---|---|---|---|
| 0–10 | Gancho | "Aprobado con condiciones": ¿cuántas condiciones de tus actas se verificaron? Mostrar `g4-cierre.png` como destino: 0 condiciones abiertas y 11 de 11 productos aceptados al cierre | diapositivas 1–2 |
| 10–25 | Concepto | Dos capas: BMAD (especificación, solo lectura) y pm-method (gobierno). Paso 1 en resumen: qué quedó listo (backlog de 68 puntos, enfoques, presupuesto de cambio, líneas base 1.0). Remite a E2E-5 | diapositivas 3–5 |
| 25–65 | Demostración | Pasos 2 a 6 (detalle abajo) | diapositivas 6–16, guía y evidencia |
| 65–75 | Pregunta y discusión | ¿Quién decide un cambio de USD 6.000? ¿Y uno de USD 9.000? | diapositiva 17 |
| 75–85 | Ejercicio | Parte A del ejercicio (condiciones, presupuesto de cambio y calidad de la última entrega de un proyecto propio); ejemplo resuelto al cerrar el bloque | diapositiva 19, [ejercicio.md](ejercicio.md) · [cómo conducirlo](#el-ejercicio) |
| 85–90 | Cierre | Mensajes clave; adelanto de la clase 2 (¿cuántas lecciones de tu último proyecto cambiaron algo?) | diapositivas 18 y 20 |

### Demostración (40 min)

| Min | Paso | En vivo | Con evidencia |
|---|---|---|---|
| 25–33 | 2 · condición formal | prompt del gate: "El gate de preparación de BMAD dio CONCERNS el 26/11 …" | verificación con L-01 y E-10; "Condiciones agregadas desde la verificación: gate de preparación de BMAD en CONCERNS …"; sanidad con EST-12 |
| 33–40 | 3 · sprint como paquete | prompt "Traé el avance de BMAD al 23/12 …" | checkpoint con Q-002 y Q-003; "D-015" |
| 40–44 | 4 · valor ganado | prompt "Highlight del sprint 2 al 8/1 …" | SPI 0,927 · CPI 0,938; próxima puerta con 2 bloqueos y 3 condiciones (G-01, E-05, E-10) |
| 44–56 | 5 · cambio de rumbo | prompt "Verificá la especificación contra la línea base y corré la sanidad al 12/1 …" | "2 ERROR · 2 AVISO · 1 INFO" (ESP-10, ESP-03); C-001 con `costo=6000`; CAM-03 "6.000 de 15.000 (40 %)"; líneas base 1.1; `g4-burnup.png` |
| 56–65 | 6 · calidad a volumen | prompts "¿Qué tengo que decidir, escalar y desbloquear hoy?" y "Al 26/2 el equipo terminó las historias 1.3, 1.4, 3.1, 3.2 y 3.3 …" | radar "1 decidir · 0 escalar · 1 desbloquear · 2 vigilar" (EST-12, QUA-02 de Q-001, RAD-07 con E-01 y E-04, TOL-03); "0 ERROR · 7 AVISO · 3 INFO": cinco QUA-01 y QUA-02; estado de productos del Release 1 (`estado.py productos --alcance R1`): "en revisión 5 · aprobado 2 · aceptado 0", cinco diferencias QUA-01; después del lote "0 ERROR · 2 AVISO · 2 INFO"; `g4-calidad-entregas.png` |

Si el tiempo aprieta, el paso 4 se muestra solo con la evidencia y el radar del paso 6 con su diapositiva.

### Mensajes clave (clase 1)

- pm-method **lee** la especificación de BMAD y le devuelve decisiones por traspaso: una sola fuente por dato.
- Una condición de puerta es un registro con dueño, no una frase del acta: reaparece en cada sanidad (EST-12), en la
  puerta siguiente (G-01) y bloquea el cierre.
- Un cambio sin monto no es un cambio controlado: costo, cargo y presupuesto de la junta (CAM-03); por encima del
  límite de la autoridad de cambio avisa CAM-04.
- La calidad se registra **por entrega**: cada historia terminada con su revisión aprobada antes de la puerta, no una
  revisión general al final (QUA-01, QUA-02). El estado de cada producto se deriva de los registros
  (`estado.py productos`), no se arma a mano para el fin de etapa.

### Preguntas para la audiencia (clase 1)

| Pregunta | Respuesta esperada |
|---|---|
| ¿Por qué la sanidad marca FR-13 como ERROR y no como aviso? | Porque es un cambio no controlado contra la línea base aprobada (ESP-10): bloquea la próxima puerta hasta tramitarlo. |
| Sofía aprobó C-001 por USD 6.000. ¿Podía? | Sí: su límite como autoridad de cambio es USD 8.000 por cambio; arriba de eso CAM-04 avisa que decide la junta. |
| El checkpoint dice "2 productos completados". ¿Por qué no 3, si la 1.3 está en review? | Solo cuentan los productos con revisión de calidad aprobada (Q-002 y Q-003). |
| Al 26/2, ¿cuántas historias terminadas no tenían revisión? ¿Cómo lo supimos? | Cinco; la sanidad las listó una por una con QUA-01 y el estado de productos las muestra como diferencias entre lo registrado y lo físico. |
| 1-1 y 1-2 tienen revisión aprobada. ¿Por qué el estado de productos no las da por aceptadas? | Aprobado no es aceptado: la aceptación es un acto de la autoridad nombrada (`aceptacion-<producto>` o el registro de aceptación del proyecto), que en el caso llega en el cierre. |

## Clase 2 · Recorrido, lecciones, cierre y beneficios (90 min)

| Min | Bloque | Qué se hace | Material |
|---|---|---|---|
| 0–10 | Gancho | "¿Cuántas lecciones de tu último proyecto cambiaron algo?" Mostrar `g4-lecciones-ciclo.png` como destino: 3 lecciones con cita, 2 de 2 acciones verificadas, 3 en el índice de la organización | diapositivas 1–2 |
| 10–25 | Concepto | Recorrido del cliente (dolor con tratamiento, MAP-03); la retrospectiva como reunión propia; impacto y ámbito de una lección; beneficios: puntaje, salud y tolerancia | diapositivas 3–7 |
| 25–65 | Demostración | Pasos 6b a 11 (detalle abajo) | diapositivas 8–17, guía y evidencia |
| 65–75 | Pregunta y discusión | El objetivo O-1 sale 0,91 en verde: ¿está todo bien? | diapositiva 17 |
| 75–85 | Ejercicio | Parte B del ejercicio (calidad por entrega, un dolor del recorrido y plan de revisión de beneficios); ejemplo resuelto al cerrar el bloque | diapositiva 19, [ejercicio.md](ejercicio.md) · [cómo conducirlo](#el-ejercicio) |
| 85–90 | Cierre | Mensajes clave; conexión con los otros casos | diapositivas 18 y 20 |

### Demostración (40 min)

| Min | Paso | En vivo | Con evidencia |
|---|---|---|---|
| 25–31 | 6b · recorrido de la socia | prompt "Armá el mapa de recorrido de UJ-1 desde la especificación de BMAD …" | dos MAP-03; candidatos; R-001; "0 aviso(s) de la familia MAP"; `g4-recorrido.png` o el HTML del recorrido |
| 31–39 | 6c · retrospectiva del sprint 4 | prompts "Te dejo la transcripción de la retrospectiva del sprint 4 …" y "Confirmo las tres lecciones y las dos acciones …" | "Retrospectiva: se detectaron 3 lecciones candidatas, 2 acciones de mejora, 0 supuestos y 0 riesgos nuevos (sin decisiones de gobierno)"; CL-02 con la cita de Lucía y "recurrencia alta"; L-001…L-003, A-001 y A-002; L-003 alto; REG-11 en la sanidad; L-002 con verificación el 19/3 |
| 39–44 | 7 · lección en el plan, condición cumplida y decisiones vigentes | prompt "La prueba de carga de NFR-3 se hizo el 2/3 …" y "¿Qué lecciones tiene que considerar el plan de la etapa 3? …" | verificación "0 bloqueo(s) · 1 condición(es) · 1 aviso(s)" con G-01 y **E-11** (L-003); plan con «Lecciones incorporadas»; informe de lecciones de la etapa 2; D-018 (PASS) con `reemplaza=D-012`; después "0 bloqueo(s) · 0 condición(es) · 0 aviso(s)" y "Decisiones vigentes: 16 de 19 (reemplazadas: 3) · … · tema: BMAD" con las cadenas D-010 → D-016, D-011 → D-017 y D-012 → D-018; `g4-tablero.png` y su sección de mapas (`g4-tablero-mapas-169.png`) |
| 44–52 | 8 · acción verificada y rechazo tratado | prompts del 8/3 (planificación del sprint 5), del 22/3 y "Release 2 terminado en BMAD …" | la planificación propone "1 compromiso … 1 decisión tomada" y ninguna lección; al 22/3 **REG-12** de L-002 en la sanidad y en Vigilar del radar → "L-002 verificada · … · efectiva"; QUA-01 y QUA-03 por Q-012; I-002; matriz "★O1 81,2" (corregir) contra "O2 63,7" (conceder), sensibilidad "impacto 40,0: si baja a 7,7 (-32,3) pasa O2" y "decisión D-022 (nivel autoridad-cambio)"; Q-013; "L-003 verificada · 2027-05-12"; `g4-calidad-entregas.png` |
| 52–57 | 9, 9b y 9c · cierre verificado por id, informe de lecciones, expediente y versiones | prompt del informe de lecciones; el resto, solo evidencia | verificación previa con **C-03** "1 issues/riesgos abiertos sin recomendaciones de seguimiento: R-001" y **C-07** "Must sin aceptar: requisitos FR-1 … y 4 más; productos 1-1 …"; después de la aceptación, "aceptado 11 … = 11" en el product status account final; "Informe de lecciones (proyecto): … 3 lecciones (alto 1, medio 2, bajo 0) · 0 pendientes · 3 para el índice"; `buscar --para descubrimiento` devuelve L-001; verificación de cierre solo con L-01 (sin C-03 ni C-07); paquete "COMPLETO PARA LA PUERTA"; expediente con `--con-bitacora`: "42 eventos en la cronología", "bitacora.jsonl: 132 escrituras", "INTEGRIDAD: OK · 44 archivos" y, en la copia con D-013 cambiada, "INTEGRIDAD: FALLA" en `decisiones.csv` con "el cambio no salió de los scripts"; `registro.py historial D-013`: una sola escritura (#42, `estado.py puerta`, «condicionado»); `g4-expediente.png`; con pm-kb (opcional), `pm-kb versiones business-case` (v1.0, v1.1 y v1.2 con D-005, D-021 y D-026), `pm-kb cambios business-case` (1.1 → 1.2: 1 agregada, 1 quitada), la misma búsqueda vigente, `--aprobado` y `--historia` (solo esta trae la 1.1, «versión anterior») y `pm-kb ficha D-013 --historia` (la misma escritura #42) |
| 57–65 | 10 y 11 · beneficios | prompt del paso 10 "Soy Sofía Ramírez, de servicios al socio …" | 30/6: O-1 0,37 rojo, salud en camino (esperado 0,20); 31/12: O-1 0,91 verde, KR-1.1 0,83 en riesgo y fuera de tolerancia; D-030 apunta a R-001; `g4-beneficios.png` |

Si el tiempo aprieta, el paso 7 se muestra con el tablero, el paso 8 solo con la parte del 22/3 y los pasos 9 y 9b con
`g4-lecciones-ciclo.png` y `g4-expediente.png`.

### Mensajes clave (clase 2)

- La retrospectiva es una reunión propia: sus lecciones salen con cita y su clasificación por impacto y ámbito dice
  adónde van (el sprint siguiente, el plan de la etapa, el próximo proyecto).
- Una lección identificada no es aprendida hasta que cambia algo y se verifica: REG-11 (impacto alto sin acción), E-11
  (plan que no la considera) y REG-12 (acción sin verificar) lo vigilan.
- Un rechazo de calidad sin issue, acción o cambio que lo cite es un rechazo olvidado (QUA-03).
- El cierre se verifica por id: cada issue y riesgo abierto con responsable en las recomendaciones (C-03) y cada
  requisito o historia Must aceptado (C-07); que el archivo exista no alcanza.
- Todo `done` no es lo mismo que un recorrido sin fricción: cada dolor de la persona necesita un tratamiento con id
  (MAP-03). El tratamiento no siempre es alcance: puede ser un riesgo con respuesta del negocio.
- La evidencia para una auditoría sale de los registros y lleva una huella por archivo: una sola palabra cambiada en
  una copia (D-013 «aprobado» en lugar de «condicionado») y la verificación la delata; la bitácora de escrituras dice
  que ese cambio no salió de los scripts.
- La junta decide con lo vigente: el PASS reemplaza al CONCERNS y la línea base 1.1 a la 1.0; lo reemplazado queda en
  la historia, no en la mesa. Algo fuera de especificación se corrige o se concede, y la autoridad de cambio elige con
  la comparación a la vista.
- Los beneficios los mide el negocio después del cierre; el proyecto deja el plan, la línea base, el criterio de desvío
  y los riesgos que los amenazan.
- Rojo en el OKR no es desvío (comparar con la trayectoria), y verde en el objetivo no garantiza que cada beneficio
  esté dentro de tolerancia.

### Preguntas para la audiencia (clase 2)

| Pregunta | Respuesta esperada |
|---|---|
| En la planificación del sprint 5 no salió ninguna lección. ¿Por qué? | Porque es otra reunión: la planificación propone compromisos y decisiones (CA, CD); la retrospectiva, lecciones y acciones de mejora (CL, CM). Mezclarlas termina en una lista de tareas. |
| ¿Por qué L-003 es de impacto alto y L-002 de impacto medio, si L-002 pasó más veces? | El impacto mide el efecto: L-003 bloqueó una puerta (ESP-10); L-002 obligó a retrabajo sin salir de tolerancia. La recurrencia (alta en L-002) ordena dentro del mismo impacto. |
| El sistema propuso tratar el dolor del primer ingreso como requisito. ¿Por qué se registró como riesgo? | A una etapa del cierre no justifica alcance nuevo, pero amenaza B-02 adopción: R-001 con dueña en el negocio y respuesta (alta asistida). |
| Las recomendaciones de seguimiento existen pero no nombran a R-001. ¿Pasa la puerta de cierre? | No: C-03 busca cada issue y riesgo abierto por id, con responsable o destinatario, y bloquea con "R-001 (no citado)". |
| La auditoría recibió una copia del expediente donde la etapa 2 figura aprobada sin condición. ¿Cómo lo saben? | `paquete.py verificar` recalcula el sha256 de cada archivo: "INTEGRIDAD: FALLA" con "alterado: 03-control/registros/decisiones.csv"; con la bitácora del expediente agrega que la última escritura anotada dejó otra versión (el cambio no salió de los scripts), y `registro.py historial D-013` muestra que los scripts solo escribieron «condicionado». |
| Al preparar la puerta de la etapa 3, ¿sigue en la mesa el CONCERNS de noviembre? | No como decisión vigente: D-018 (PASS, mismo nivel) lo reemplaza y `decision.py vigentes` lo deja en la historia (cadena D-012 → D-018). D-013, la etapa 2 condicionada, sigue vigente: fue lo que se decidió, y D-019 registra que la condición se cumplió. |
| Al 30/6 el OKR está en rojo (0,37). ¿Hay que informar a la ejecutiva? | No: la salud es "en camino" (esperado 0,20: van 46 de los 230 días entre el 15/5 y el 31/12); el plan escala la revisión intermedia solo si está en riesgo o desviada. |
| Al 31/12 el objetivo sale 0,91 en verde. ¿Todo bien? | No: B-02 adopción llega a 0,83, por debajo de 0,90 (tolerancia −10 %); se informa a la ejecutiva (D-030), que empieza por R-001. |

## Dudas frecuentes

- **¿pm-method modifica los archivos de BMAD?** No. Lee por la fachada (`bmad.py`, `especificacion.py`) y emite un
  traspaso (`bmad.py handoff`) que aplica el equipo de BMAD. El mapa de recorrido también parte de BMAD
  (`bmad.py recorridos`) y se guarda en la carpeta de gestión.
- **¿Qué pasa si la historia se reabre en BMAD en vez de quedar `done`?** QUA-01 solo mira historias terminadas: deja
  de avisar, y el rechazo sigue marcado por QUA-03 hasta que algo lo trate.
- **¿Las emociones del mapa son inventadas?** Cada una lleva su fuente (aquí, la observación de la revisión del
  Release 1 con seis socios, o un supuesto declarado). Sin fuente, MAP-04 avisa.
- **¿Por qué los beneficios se registran como check-ins y no editando el OKR?** Porque los check-ins solo se agregan:
  queda la historia de cada medición, con autor y fecha, y la salud se calcula desde el primero.
- **¿Qué ve el gestor al abrir Claude Code después de semanas?** Un resumen derivado de `estado.json` y los registros
  (conteos abiertos, condiciones de puertas, próxima puerta) y la línea del radar (decidir, escalar, desbloquear,
  vigilar). Si una nota de memoria dice otra cosa, mandan los registros. La línea cuenta 1 en vigilar y el radar
  completo 2: la línea no corre la verificación de la próxima puerta (RAD-07).
- **¿Por qué la retrospectiva no registra decisiones?** Porque no decide por la junta ni planifica el trabajo: propone
  lecciones y acciones de mejora. Una decisión de gobierno que aparezca en una retro se lleva a la reunión que
  corresponde. En otras reuniones, una lección se propone solo si alguien la marca ("lección: …").
- **¿Quién verifica una lección y con qué?** El responsable de seguimiento, con evidencia de los registros (una
  revisión, una sanidad, un issue); si la acción no funcionó, la lección vuelve a revisada para definir otra.
- **¿Dónde queda el índice de lecciones?** Fuera de la carpeta del proyecto (en el caso, `pmo/lecciones-indice.csv`);
  el informe de lecciones lo actualiza sin borrar lo de otros proyectos, y `lecciones.py buscar` lo consulta en solo
  lectura.
- **¿El expediente de auditoría reemplaza al paquete de cierre?** No. El paquete de cierre es para la junta en la
  puerta; el expediente se arma cuando alguien audita, cubre todo el período (cronología, copias congeladas, registros,
  evidencia de puertas y sanidad al corte) y cita el paquete de cierre por su huella. Con `--externo` no lleva el
  registro de interesados ni sus valoraciones.
- **¿Por qué la corrida de referencia arma el expediente con una carpeta personal vacía?** Porque la sanidad que el
  expediente incluye revisa también la instalación (familia INS) y sus avisos dependen de las skills de cada equipo;
  en tu equipo pueden aparecer avisos INS que no cambian nada del proyecto.
- **¿Por qué el paquete de cierre no incluyó el PRD de BMAD?** Porque está fuera de la carpeta del proyecto: el paquete
  solo lleva archivos de `gestion/` y anota en el manifiesto lo que excluyó. La especificación viaja como línea base
  congelada (`00-direccion/historial/bmad-prd-v1.1/`).
- **¿Por qué la evidencia muestra «<fecha y hora de la escritura>» en la bitácora?** Porque la bitácora anota la fecha
  y hora reales de cada escritura y huellas que dependen de ellas; el driver las enmascara para que dos corridas den la
  misma evidencia. En tu proyecto vas a ver las reales.
- **¿Quién marca que una decisión reemplaza a otra?** Quien decide, con `registro.py actualizar decisiones D-### --campo
  reemplaza=D-###`: el script rechaza reemplazar una decisión posterior y exige nivel igual o superior (una decisión
  del gestor no deja sin efecto una de la junta). Al aprobar una versión nueva de un
  artefacto o una línea base, y al registrar un gate de preparación de BMAD posterior (el PASS de D-018 reemplaza al
  CONCERNS de D-012), el reemplazo se marca solo.
- **¿Las decisiones humanas están simuladas?** Sí, con los nombres del escenario; en uso real las toma cada rol y el
  hook reserva a pm-director los comandos de la junta.
- **¿Las fechas del paquete de cierre y del expediente son distintas a las de la guía?** `paquete.py`, `exportar.py`
  y `bmad.py handoff` nombran el archivo con la fecha de la corrida; el contenido no cambia.

## Plan B si la demostración en vivo falla

1. Seguir con la evidencia: cada paso de la guía remite a su bloque en `salida-g4.md` (encabezados "Paso N").
2. Mostrar las imágenes ya generadas (`g4-calidad-entregas.png`, `g4-recorrido.png`, `g4-lecciones-ciclo.png`, `g4-burnup.png`,
   `g4-tablero.png`, `g4-tablero-mapas-169.png`, `g4-cierre.png`, `g4-expediente.png`, `g4-beneficios.png`): cuentan la
   historia completa sin terminal.
3. Si falla solo un paso, correr el driver completo en segundo plano (`g4.py`, menos de un minuto) y abrir la carpeta del
   recorrido que imprime al final.

## Conexión con los otros casos

- **Antes:** E2E-5 muestra cómo se llegó al proyecto autorizado (supuestos, opciones, enfoque, presupuestos y
  tolerancias de la junta) y el recorrido de UJ-2 en el diseño. E2E-4 arranca donde termina E2E-5 y vuelve al
  recorrido del cliente, esta vez sobre lo entregado. Al cierre, E2E-4 le devuelve algo a E2E-5: el informe de lecciones
  exporta las aprobadas al índice de la organización, el mismo tipo de índice que E2E-5 consulta en su paso 1 para la
  ideación y el descubrimiento.
- **Después:** E2E-1 (riesgos) profundiza lo que aquí quedó como un riesgo medio con respuesta; E2E-2 (alcance y
  cambios) muestra la ruta de excepción cuando un cambio no entra en las tolerancias; E2E-3 (interesados y avance)
  amplía el informe de aspectos destacados y los OKR.
