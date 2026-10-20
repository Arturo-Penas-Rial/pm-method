# Guion del instructor · E2E-4 · Producto con BMAD gobernado con PRINCE2

Guía del caso: [E2E-4-producto-bmad.md](../../guias/E2E-4-producto-bmad.md) · Evidencia:
[salida-g4.md](../../guias/evidencia/salida-g4.md) · Ejercicio: [ejercicio.md](ejercicio.md) · Diapositivas:
[diapositivas.json](diapositivas.json). Todas las cifras de este guion salen de la evidencia de la corrida de referencia.
Los números de diapositiva de las agendas cuentan dentro de cada clase, sin las portadas que agrega el generador.

## Por qué dos clases

El caso responde dos preguntas distintas y cada una necesita su demostración completa:

1. **Clase 1 · Gobernar la construcción con BMAD.** ¿Cómo controla la junta lo que construye un equipo que especifica
   con BMAD, sin copiar la especificación? Condición formal, paquete de trabajo, valor ganado y cambio con presupuesto
   (pasos 1 a 5). Termina con la línea base 1.1, un corte natural.
2. **Clase 2 · Calidad a volumen, recorrido, cierre y beneficios.** ¿Cómo se llega a la puerta de cierre con cada
   historia revisada, cada dolor de la socia tratado y, meses después, cómo se sabe si valió la pena? Pasos 6 a 11.

La idea y el diseño del proyecto se ven en [E2E-5](../../guias/E2E-5-idea-a-proyecto.md); aquí el paso 1 se resume en
5 minutos.

## Objetivos de aprendizaje

Al terminar, cada asistente puede:

1. Explicar la división de trabajo: BMAD especifica y construye; pm-method gobierna y nunca escribe en `_bmad-output/`.
2. Convertir una aprobación "con condiciones" en una condición formal con seguimiento y cierre registrado.
3. Controlar un cambio con costo y cargo contra el presupuesto de cambio de la junta.
4. Diseñar la calidad **por entrega** (una revisión registrada por historia) y tratar un rechazo con traza.
5. Mapear el recorrido del cliente sobre lo entregado y darle a cada dolor un tratamiento con id.
6. Distinguir puntaje de OKR, salud contra la trayectoria y tolerancia de beneficios al revisar beneficios después del
   cierre.

## Requisitos previos

- **Asistentes:** nociones de etapas, puertas y business case (PRINCE2 o PMBOK) o experiencia liderando iniciativas.
  No hace falta saber programar ni conocer BMAD.
- **Instructor:** Claude Code con pm-method 2.3.0; copia del fixture `scripts/pruebas/fixtures/bmad-v6.12-real` en
  `~/proyectos-prueba/portal-e2e-4`; la evidencia y las imágenes `docs/guias/img/g4-*.png` abiertas en pestañas; para
  la clase 2, el driver `scripts/pruebas/guias_e2e/g4.py` ya corrido (unos 40 segundos) y su carpeta abierta, con
  `02-planificacion/visuales/recorrido-uj-1.html` en el navegador.
- **Recomendado:** haber dado E2E-5 antes (la idea y el diseño del mismo tipo de proyecto).

## Clase 1 · Gobernar la construcción con BMAD (90 min)

| Min | Bloque | Qué se hace | Material |
|---|---|---|---|
| 0–10 | Gancho | "Aprobado con condiciones": ¿cuántas condiciones de tus actas se verificaron? Mostrar `g4-cierre.png` como destino: 0 condiciones abiertas al cierre | diapositivas 1–2 |
| 10–25 | Concepto | Dos capas: BMAD (especificación, solo lectura) y pm-method (gobierno). Paso 1 en resumen: qué quedó listo (backlog de 68 puntos, enfoques, presupuesto de cambio, líneas base 1.0). Remite a E2E-5 | diapositivas 3–5 |
| 25–65 | Demostración | Pasos 2 a 5 (detalle abajo) | diapositivas 6–12, guía y evidencia |
| 65–75 | Pregunta y discusión | ¿Quién decide un cambio de USD 6.000? ¿Y uno de USD 9.000? | diapositiva 13 |
| 75–85 | Ejercicio | Parte A del ejercicio (condiciones y presupuesto de cambio de un proyecto propio) | diapositiva 15, ejercicio.md |
| 85–90 | Cierre | Mensajes clave; adelanto de la clase 2 (`g4-calidad-entregas.png`) | diapositivas 14 y 16 |

### Demostración (40 min)

| Min | Paso | En vivo | Con evidencia |
|---|---|---|---|
| 25–35 | 2 · condición formal | prompt del gate: "El gate de preparación de BMAD dio CONCERNS el 26/11 …" | verificación con L-01 y E-10; "Condiciones agregadas desde la verificación: gate de preparación de BMAD en CONCERNS …"; sanidad con EST-12 |
| 35–45 | 3 · sprint como paquete | prompt "Traé el avance de BMAD al 23/12 …" | checkpoint con Q-002 y Q-003; "D-015" |
| 45–50 | 4 · valor ganado | prompt "Highlight del sprint 2 al 8/1 …" | SPI 0,927 · CPI 0,938; próxima puerta con 2 bloqueos y 3 condiciones (G-01, E-05, E-10) |
| 50–65 | 5 · cambio de rumbo | prompt "Verificá la especificación contra la línea base y corré la sanidad al 12/1 …" | "2 ERROR · 2 AVISO · 1 INFO" (ESP-10, ESP-03); C-001 con `costo=6000`; CAM-03 "6.000 de 15.000 (40 %)"; líneas base 1.1 |

Si el tiempo aprieta, el paso 4 se muestra solo con la evidencia.

### Mensajes clave (clase 1)

- pm-method **lee** la especificación de BMAD y le devuelve decisiones por traspaso: una sola fuente por dato.
- Una condición de puerta es un registro con dueño, no una frase del acta: reaparece en cada sanidad (EST-12), en la
  puerta siguiente (G-01) y bloquea el cierre.
- Un cambio sin monto no es un cambio controlado: costo, cargo y presupuesto de la junta (CAM-03); por encima del
  límite de la autoridad de cambio avisa CAM-04.

### Preguntas para la audiencia (clase 1)

| Pregunta | Respuesta esperada |
|---|---|
| ¿Por qué la sanidad marca FR-13 como ERROR y no como aviso? | Porque es un cambio no controlado contra la línea base aprobada (ESP-10): bloquea la próxima puerta hasta tramitarlo. |
| Sofía aprobó C-001 por USD 6.000. ¿Podía? | Sí: su límite como autoridad de cambio es USD 8.000 por cambio; arriba de eso CAM-04 avisa que decide la junta. |
| El checkpoint dice "2 productos completados". ¿Por qué no 3, si la 1.3 está en review? | Solo cuentan los productos con revisión de calidad aprobada (Q-002 y Q-003). |

## Clase 2 · Calidad a volumen, recorrido, cierre y beneficios (90 min)

| Min | Bloque | Qué se hace | Material |
|---|---|---|---|
| 0–10 | Gancho | "Done no es aceptado": la 2-4 pasó la revisión de código y fue rechazada contra sus criterios. ¿Dónde quedaría eso en tu proyecto? Abrir con lo que ve el gestor al retomar la sesión (`estado.py contexto`) | diapositivas 1–2 |
| 10–25 | Concepto | Calidad por entrega (registro de calidad, QUA-01/02/03); recorrido del cliente (dolor con tratamiento, MAP-03); beneficios: puntaje, salud y tolerancia | diapositivas 3–7 |
| 25–65 | Demostración | Pasos 6 a 11 (detalle abajo) | diapositivas 8–16, guía y evidencia |
| 65–75 | Pregunta y discusión | El objetivo O-1 sale 0,91 en verde: ¿está todo bien? | diapositiva 17 |
| 75–85 | Ejercicio | Parte B del ejercicio (calidad por entrega, un dolor del recorrido y plan de revisión de beneficios) | diapositiva 19, ejercicio.md |
| 85–90 | Cierre | Mensajes clave; conexión con los otros casos | diapositivas 18 y 20 |

### Demostración (40 min)

| Min | Paso | En vivo | Con evidencia |
|---|---|---|---|
| 25–31 | 6 · calidad a volumen | prompt "Al 26/2 el equipo terminó las historias 1.3, 1.4, 3.1, 3.2 y 3.3 …" | "0 ERROR · 7 AVISO · 3 INFO": cinco QUA-01 y QUA-02; después del lote "0 ERROR · 2 AVISO · 2 INFO" |
| 31–39 | 6b · recorrido de la socia | prompt "Armá el mapa de recorrido de UJ-1 desde la especificación de BMAD …" | dos MAP-03; candidatos; R-001; "0 aviso(s) de la familia MAP"; `g4-recorrido.png` o el HTML del recorrido |
| 39–44 | 7 · condición cumplida | prompt "La prueba de carga de NFR-3 se hizo el 2/3 …" | G-01 antes de `cumplir-condiciones`; después "0 bloqueo(s) · 0 condición(es) · 0 aviso(s)"; `g4-tablero.png` con R-001 en zona media y la sección «Mapas estratégicos» (`g4-tablero-mapas-169.png`: cada dolor con su tratamiento enlazado, 0 avisos MAP) |
| 44–52 | 8 · Release 2 con un rechazo | prompt "Release 2 terminado en BMAD …" | QUA-01 "terminado con revisión Q-012 sin aprobar" y QUA-03; I-002; Q-013; sanidad final "0 AVISO"; `g4-calidad-entregas.png` |
| 52–57 | 9 · cierre | solo evidencia | verificación de cierre solo con L-01; recomendaciones con R-001; paquete "COMPLETO PARA LA PUERTA" que excluye el PRD vivo de BMAD; `g4-cierre.png` |
| 57–65 | 10 y 11 · beneficios | prompt del paso 10 "Soy Sofía Ramírez, de servicios al socio …" | 30/6: O-1 0,37 rojo, salud en camino (esperado 0,20); 31/12: O-1 0,91 verde, KR-1.1 0,83 en riesgo y fuera de tolerancia; D-029 apunta a R-001; `g4-beneficios.png` |

Si el tiempo aprieta, el paso 7 se muestra con el tablero y el paso 9 con `g4-cierre.png`.

### Mensajes clave (clase 2)

- La calidad se registra **por entrega**: cada historia terminada con su revisión aprobada antes de la puerta, no una
  revisión general al final.
- Un rechazo de calidad sin issue, acción o cambio que lo cite es un rechazo olvidado (QUA-03).
- Todo `done` no es lo mismo que un recorrido sin fricción: cada dolor de la persona necesita un tratamiento con id
  (MAP-03). El tratamiento no siempre es alcance: puede ser un riesgo con respuesta del negocio.
- Los beneficios los mide el negocio después del cierre; el proyecto deja el plan, la línea base, el criterio de desvío
  y los riesgos que los amenazan.
- Rojo en el OKR no es desvío (comparar con la trayectoria), y verde en el objetivo no garantiza que cada beneficio
  esté dentro de tolerancia.

### Preguntas para la audiencia (clase 2)

| Pregunta | Respuesta esperada |
|---|---|
| Al 26/2, ¿cuántas historias terminadas no tenían revisión? ¿Cómo lo supimos? | Cinco; la sanidad las listó una por una con QUA-01. |
| El sistema propuso tratar el dolor del primer ingreso como requisito. ¿Por qué se registró como riesgo? | A una etapa del cierre no justifica alcance nuevo, pero amenaza B-02 adopción: R-001 con dueña en el negocio y respuesta (alta asistida). |
| Al 30/6 el OKR está en rojo (0,37). ¿Hay que informar a la ejecutiva? | No: la salud es "en camino" (esperado 0,20: van 46 de los 230 días entre el 15/5 y el 31/12); el plan escala la revisión intermedia solo si está en riesgo o desviada. |
| Al 31/12 el objetivo sale 0,91 en verde. ¿Todo bien? | No: B-02 adopción llega a 0,83, por debajo de 0,90 (tolerancia −10 %); se informa a la ejecutiva (D-029), que empieza por R-001. |

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
  (conteos abiertos, condiciones de puertas, próxima puerta). Si una nota de memoria dice otra cosa, mandan los
  registros.
- **¿Por qué el paquete de cierre no incluyó el PRD de BMAD?** Porque está fuera de la carpeta del proyecto: el paquete
  solo lleva archivos de `gestion/` y anota en el manifiesto lo que excluyó. La especificación viaja como línea base
  congelada (`00-direccion/historial/bmad-prd-v1.1/`).
- **¿Las decisiones humanas están simuladas?** Sí, con los nombres del escenario; en uso real las toma cada rol y el
  hook reserva a pm-director los comandos de la junta.
- **¿Las fechas del paquete de cierre son distintas a las de la guía?** `paquete.py`, `exportar.py` y `bmad.py
  handoff` nombran el archivo con la fecha de la corrida; el contenido no cambia.

## Plan B si la demostración en vivo falla

1. Seguir con la evidencia: cada paso de la guía remite a su bloque en `salida-g4.md` (encabezados "Paso N").
2. Mostrar las imágenes ya generadas (`g4-calidad-entregas.png`, `g4-recorrido.png`, `g4-burnup.png`,
   `g4-tablero.png`, `g4-tablero-mapas-169.png`, `g4-cierre.png`, `g4-beneficios.png`): cuentan la historia completa sin terminal.
3. Si falla solo un paso, correr el driver completo en segundo plano (`g4.py`, unos 40 segundos) y abrir la carpeta del
   recorrido que imprime al final.

## Conexión con los otros casos

- **Antes:** E2E-5 muestra cómo se llegó al proyecto autorizado (supuestos, opciones, enfoque, presupuestos y
  tolerancias de la junta) y el recorrido de UJ-2 en el diseño. E2E-4 arranca donde termina E2E-5 y vuelve al
  recorrido del cliente, esta vez sobre lo entregado.
- **Después:** E2E-1 (riesgos) profundiza lo que aquí quedó como un riesgo medio con respuesta; E2E-2 (alcance y
  cambios) muestra la ruta de excepción cuando un cambio no entra en las tolerancias; E2E-3 (interesados y avance)
  amplía el informe de aspectos destacados y los OKR.
