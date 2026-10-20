# Pruebas en vivo · terminología PRINCE2 / PMBOK / uso habitual · pm-method 2.2.0 · 2026-10-18

**Objetivo:** verificar que los pedidos escritos con el vocabulario que traen las personas (PRINCE2 en español, PMBOK en
español y términos habituales de las organizaciones), y no con las palabras de las descripciones de las skills, llegan
a la skill correcta. Antes, un análisis estático de 104 términos mostró que muchos no figuraban en ningún disparador
(por ejemplo: incidencia, informe de aspectos destacados, junta del proyecto, comité de dirección, ruta crítica,
registro de interesados, comité de control de cambios).

**Cómo:** `suite.py enrutamiento --ids 67..94` con Claude Code 2.1.302 real (`--plugin-dir`, modelo por defecto) sobre
el proyecto base; se compara la primera skill elegida. Frases nuevas 67–94 agregadas a `frases-enrutamiento.tsv`.

## 1. Medición inicial: 27/28

| id | frase | esperada | elegida | veredicto |
|---|---|---|---|---|
| 67 | Prepará el informe de aspectos destacados de esta semana para la junta | pm-progreso-reportes | pm-progreso-reportes | OK |
| 68 | Necesito el informe de punto de control del paquete de trabajo del equ | pm-progreso-reportes | pm-progreso-reportes | OK |
| 69 | Registrá una incidencia: el proveedor entregó el módulo de pagos fuera | pm-issues-cambios | pm-issues-cambios | OK |
| 70 | Abrí el registro de incidentes con los problemas de esta semana | pm-issues-cambios | — | SIN SKILL |
| 71 | Armá el resumen del proyecto a partir del mandato que nos mandó el dir | pm-mandato-y-brief | pm-mandato-y-brief | OK |
| 72 | Convocá a la junta del proyecto para aprobar el plan de la próxima eta | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 73 | El comité de dirección tiene que decidir si seguimos con la etapa 3 | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 74 | Preparame el material para el steering committee del jueves | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 75 | Anotá en el registro diario que el proveedor llamó por el retraso | pm-registros | pm-registros | OK |
| 76 | Calculá la ruta crítica del cronograma | pm-cronograma-estimacion | pm-cronograma-estimacion | OK |
| 77 | Armá la estructura de desglose del trabajo con su diccionario | pm-planificacion-por-productos | pm-planificacion-por-productos | OK |
| 78 | Fijemos la línea base de costos con la reserva de contingencia | pm-costos-presupuesto | pm-costos-presupuesto | OK |
| 79 | Actualizá el registro de interesados con los nuevos gerentes de sucurs | pm-interesados | pm-interesados | OK |
| 80 | Armá el plan de involucramiento de los interesados | pm-interesados | pm-interesados | OK |
| 81 | Hacé la matriz de asignación de responsabilidades del equipo | pm-interesados | pm-interesados | OK |
| 82 | Necesito el plan de gestión de las comunicaciones | pm-comunicacion-stakeholders | pm-comunicacion-stakeholders | OK |
| 83 | Llevá esta solicitud al comité de control de cambios | pm-issues-cambios | pm-issues-cambios | OK |
| 84 | Armá la matriz de riesgos con probabilidad e impacto | pm-riesgos | pm-riesgos | OK |
| 85 | Hay un impedimento: infraestructura no nos da el ambiente de pruebas | pm-issues-cambios | pm-issues-cambios | OK |
| 86 | Mandame el informe de estado del proyecto | pm-progreso-reportes | pm-progreso-reportes | OK |
| 87 | Quiero la documentación de inicio del proyecto (DIP) para la junta | pm-acta-constitucion | pm-acta-constitucion | OK |
| 88 | Agregá al registro de supuestos que TI asigna dos personas a tiempo co | pm-registros | pm-registros | OK |
| 89 | Cerremos el límite de etapa y prepará el informe de fin de etapa | pm-plan-etapa-y-limites | pm-plan-etapa-y-limites | OK |
| 90 | Actualizá el estado de los productos del paquete de trabajo 2 | pm-paquetes-trabajo | pm-paquetes-trabajo | OK |
| 91 | El cliente pide alcance adicional: agregar pagos con QR | pm-issues-cambios | pm-issues-cambios | OK |
| 92 | Hacé el registro de lecciones aprendidas de la etapa | pm-lecciones-aprendidas | pm-lecciones-aprendidas | OK |
| 93 | Necesito el plan para la dirección del proyecto con sus planes de gest | pm-enfoques-gestion | pm-acta-constitucion | OK |
| 94 | Armá el diagrama de Gantt con los hitos del proyecto | pm-cronograma-estimacion | pm-cronograma-estimacion | OK |

- **70 "Abrí el registro de incidentes…"** quedó sin skill en esa corrida: el modelo empezó a revisar los registros con
  scripts sin cargar la skill dueña. En una corrida de diagnóstico aparte sí cargó `pm-issues-cambios`, es decir, era un
  caso límite.
- **93 "plan para la dirección del proyecto…"** fue a `pm-acta-constitucion`, aceptable: el plan para la dirección del
  proyecto de PMBOK equivale al PID ensamblado de PRINCE2.

## 2. Ajustes

- Descripción de `pm-issues-cambios`: + "incidencia, registro de incidentes" (listado total 6.582 caracteres).
- Tabla de enrutamiento de `pm-orquestador`: "issue o incidencia" y "junta o comité de dirección".
- Documento nuevo `docs/TERMINOLOGIA.md` con las equivalencias PRINCE2 7 (EN) · pm-method · PRINCE2 ES · PMBOK ES · uso
  habitual · skill · frase verificada.

## 3. Repetición tras los ajustes (vecinos de issues y registros, dos corridas)

| id | Frase | Esperada | Corrida A | Corrida B |
|---|---|---|---|---|
| 69 | Registrá una incidencia: el proveedor entregó el módulo de pagos fuera de especificación | pm-issues-cambios | OK | OK |
| 70 | Abrí el registro de incidentes con los problemas de esta semana | pm-issues-cambios | OK | OK |
| 75 | Anotá en el registro diario que el proveedor llamó por el retraso | pm-registros | OK | OK |
| 83 | Llevá esta solicitud al comité de control de cambios | pm-issues-cambios | sin skill | OK |
| 85 | Hay un impedimento: infraestructura no nos da el ambiente de pruebas | pm-issues-cambios | OK | OK |
| 88 | Agregá al registro de supuestos que TI asigna dos personas a tiempo completo | pm-registros | OK | OK |
| 91 | El cliente pide alcance adicional: agregar pagos con QR | pm-issues-cambios | OK | OK |

La 83 no trae la solicitud: en una corrida de diagnóstico, el modelo cargó `pm-issues-cambios` y pidió el texto o el id
de la solicitud antes de seguir; la corrida sin skill corresponde a esa misma repregunta hecha sin cargarla. No se
modificó nada por ese caso. Las frases de `pm-registros` (75, 88) no se desviaron hacia `pm-issues-cambios` con el
cambio de descripción.

Costo aproximado de las tres corridas y los dos diagnósticos: USD 4–5 [verificar: la suite corta cada sesión al elegir
y no registra el costo de cada frase; los diagnósticos costaron USD 0,13 y 0,11].
