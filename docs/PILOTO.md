# Plan de piloto · pm-method 2.2

Cómo pasar de "probado en laboratorio" a "útil en un proyecto real" con evidencia medible, sin poner en riesgo el
proyecto. EN: *pilot plan with metrics, expert review rubric and usability test.*

---

## 1. Objetivo y preguntas que debe responder

| Pregunta | Cómo se responde |
|---|---|
| ¿Funciona en el equipo del usuario (Windows, su Claude Code, su red)? | Fase 0 · instalación con evidencia |
| ¿Ahorra tiempo real al líder del proyecto? | horas registradas con y sin pm-method (§4) |
| ¿Los artefactos tienen calidad para una junta real? | revisión experta con rúbrica (§5) |
| ¿Un líder no técnico puede usarlo solo? | prueba de usabilidad con tareas (§6) |
| ¿Se mantiene coherente durante semanas? | sanidad semanal y registro de incidentes (§4) |
| ¿Cuánto cuesta por semana? | costo de tokens por semana (§4) |

## 2. Alcance y modalidad

- **Modalidad "en paralelo" (shadow):** el proyecto sigue gestionándose como siempre. pm-method produce lo mismo en una
  carpeta aparte y se compara. Nada de lo que produce se envía a la junta sin revisión humana.
- **Proyecto elegido:** real, de bajo riesgo, con 2 a 4 semanas de actividad visible (idealmente con PRD o BMAD).
  Datos sensibles: usar el proyecto con datos anonimizados o con permiso explícito de su dueño.
- **Duración:** 4 semanas (1 de preparación + 3 de uso). Prórroga de 2 semanas si hay una puerta en camino.
- **Participantes:** el líder piloto (usuario), 2 o 3 practicantes PMP/PRINCE2 para la revisión experta y 3 a 5
  líderes no técnicos para la usabilidad (por ejemplo, del CoE de IA de un capítulo PMI).

## 3. Fases

| Fase | Semana | Actividades | Criterio para avanzar |
|---|---|---|---|
| 0 · Instalación | 1 | instalar desde GitHub en el equipo del líder; correr la lista de aceptación de [PRUEBAS §6](PRUEBAS.md); en Windows verificar que el resumen de inicio aparece y que una edición manual de `estado.json` queda bloqueada | 13/13 puntos de la lista o desvíos explicados |
| 1 · Arranque | 1 | `pm-nuevo`; cargar mandato, roles, riesgos conocidos; conectar BMAD si existe; elegir 3 productos a comparar (p. ej. highlight, registro de riesgos, plan de etapa) | carpeta del proyecto con sanidad 0 ERROR |
| 2 · Uso semanal | 2–4 | cada semana: actas de reuniones, actualización de registros, highlight, sanidad; una puerta si corresponde; si se usan (v2.2): check-ins de OKR (`okr.py --checkin`) y el comunicado semanal por la capa de canales, empezando por `.eml` o simulación antes de enviar de verdad ([INTEGRACIONES §3.2](INTEGRACIONES.md)) | registro semanal completo (§4) |
| 3 · Evaluación | 4 | revisión experta (§5), usabilidad (§6), costo, retrospectiva; decisión de adopción | informe de piloto con decisión |

## 4. Métricas (registro semanal)

| Métrica | Cómo se mide | Meta orientativa |
|---|---|---|
| Tiempo por producto | minutos del líder por highlight, acta, actualización de riesgos, plan, con y sin pm-method | −40 % o más |
| Correcciones | cantidad de cambios que el líder tuvo que hacer a cada borrador antes de usarlo | tendencia decreciente |
| Incidentes | veces que algo falló: skill equivocada, comando con error, archivo incoherente, respuesta en otro idioma | 0 incidentes bloqueantes; < 3 menores por semana |
| Integridad | `sanidad.py` semanal: cantidad de ERROR y AVISO | 0 ERROR antes de cada puerta |
| Trazabilidad | requisitos con historia o paquete (ESP-03), decisiones con fila en `decisiones.csv` | 100 % de puertas con fila |
| Costo | USD por semana (en `claude -p` o la consola de uso) y por producto | definido por el líder |
| Adopción | ¿el líder usaría pm-method en el próximo proyecto? (sí / con cambios / no) | "sí" o "con cambios" |

Plantilla de registro semanal (copiar a `diario.md` del proyecto piloto o a una planilla):

| Semana | Producto | Min. sin | Min. con | Correcciones | Incidentes | Sanidad (E/A) | USD |
|---|---|---|---|---|---|---|---|
| 1 | highlight | | | | | | |

## 5. Rúbrica de revisión experta

Cada revisor puntúa de 1 (inaceptable) a 4 (listo para la junta) tres a cinco artefactos generados en el piloto
(sugeridos: business case, plan de etapa, highlight report, informe de excepción, registro de riesgos).

| Criterio | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Fidelidad al método (PRINCE2 manda, PMBOK como técnica) | contradice el método | mezcla conceptos | correcto con detalles menores | correcto y claro |
| Exactitud de los datos | cifras inventadas o erróneas | errores relevantes | errores menores | sin errores; faltantes marcados `[por confirmar]` |
| Trazabilidad | sin referencias | referencias sueltas | ids de requisitos/riesgos citados | ids citados y coherentes con los registros |
| Utilidad para decidir | no sirve para decidir | requiere reescritura | decide con ajustes | decide tal cual |
| Claridad y extensión | confuso o excesivo | largo o vago | claro con ajustes | claro y proporcionado |
| Honestidad | presenta supuestos como hechos | supuestos no señalados | supuestos señalados | supuestos y límites explícitos |

Resultado: promedio por artefacto y por criterio; un 1 en "Exactitud" o "Honestidad" es bloqueante.

## 6. Prueba de usabilidad (3 a 5 líderes no técnicos)

Tareas cronometradas, sin ayuda salvo bloqueo total, pensando en voz alta:

1. Instalar el plugin desde GitHub siguiendo [INSTALACION](INSTALACION.md).
2. Crear un proyecto y pedir "¿qué sigue?".
3. Registrar dos riesgos y un issue a partir de un texto dado.
4. Generar un highlight report de la semana.
5. Preparar la puerta "autorizar-proyecto" y entender quién debe decidir.

Medir: tareas completadas sin ayuda, tiempo por tarea, errores, y al final una escala SUS (System Usability Scale, 10
preguntas) y tres preguntas abiertas: qué fue lo más útil, qué fue lo más confuso, ¿lo usaría?

## 7. Riesgos del piloto y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Datos sensibles del proyecto en sesiones de IA | anonimizar o pedir permiso; no incluir datos personales en transcripciones; revisar la política de datos de la organización |
| Confianza excesiva en borradores | modalidad en paralelo; ningún artefacto sale sin revisión humana |
| Costo mayor al previsto | medir por semana; usar Sonnet si alcanza (ver [PRUEBAS §3.1](PRUEBAS.md)) |
| Fallas en Windows | Fase 0 antes de empezar; registrar el incidente con el texto del error |
| Varias personas editando la carpeta | un solo editor por carpeta durante el piloto; git con commits frecuentes |

## 8. Criterios de decisión al cierre

- **Adoptar:** 0 incidentes bloqueantes en las últimas 2 semanas, rúbrica promedio ≥ 3 sin criterios bloqueantes,
  ahorro de tiempo ≥ 30 %, usabilidad SUS ≥ 68.
- **Adoptar con cambios:** metas parcialmente cumplidas con causas identificadas y corregibles.
- **No adoptar todavía:** incidentes bloqueantes recurrentes o rúbrica < 2,5.

El informe del piloto se guarda en `docs/evaluacion/resultados/` del repositorio, con la fecha.
