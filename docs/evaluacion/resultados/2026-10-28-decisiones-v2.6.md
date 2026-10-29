# Pruebas en vivo de enrutamiento · decisiones con contexto: expediente, matriz multicriterio y pregunta tipada (pm-direccion-decisiones) · 2026-10-28

- **Qué se probó:** las 4 frases nuevas de `docs/evaluacion/frases-enrutamiento.tsv` (ids 131 a 134), que deben llegar
  a `pm-direccion-decisiones`: una matriz de decisión con pesos y sensibilidad para alternativas de OKR (131), el
  expediente de una decisión de la junta sobre un riesgo (132), la evaluación ponderada de proveedores con eliminatorios
  y la elección de la ejecutiva, en inglés (133), y criterios no monetarios con pesos sobre opciones de negocio que ya
  tienen VAN, con la pregunta cerrada para la ejecutiva (134). Junto con ellas, 7 frases de control de las skills
  vecinas, para comprobar que la descripción nueva no les quita pedidos: business case con VAN (11), OKR (12), puerta de
  fin de etapa (21), licitación (36), comité de dirección (73), comité de control de cambios (83) y opciones de
  respuesta a riesgos altos (103).
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py enrutamiento --ids 131,132,133,134,11,12,21,36,73,83,103 --par 6`
  con Claude Code 2.1.312 real (`claude -p … --plugin-dir <repo>`), modelo por defecto de la CLI, sobre un proyecto
  desechable creado desde el fixture BMAD 6.12.4. Se compara la primera skill elegida; la sesión se corta apenas elige.
- **Descripción que cambió:** la de `pm-direccion-decisiones`. Primera corrida con una versión de 236 caracteres
  ("… excepciones, matriz multicriterio. Usar: …, excepción, matriz de decisión, pesos, board decision, stage gate. No:
  anotar riesgos o issues→pm-registros."); como empujaba el total de las descripciones visibles en el recorrido E2E-4 a
  ≈ 8.032 caracteres y hacía aparecer el aviso INS-05 en su evidencia, se acortó a la versión final de 196 caracteres
  ("Decisiones de la junta: puertas, tolerancias, excepciones, matriz de decisión. Usar: aprobar etapa, autorizar
  proyecto, junta, pesos, board decision, stage gate. No: riesgos o issues→pm-registros.") y se repitió la corrida. Las
  demás descripciones no cambiaron.
- **Resultado: 11/11 OK en las dos corridas**; las cuatro frases nuevas eligieron la skill esperada (no la alternativa
  aceptable de la columna 4). La tabla es la de la corrida con la descripción final.

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 131 | Armá una matriz de decisión con pesos para elegir entre las tres alternativas de OKR del ciclo y decime qué tan sensible es el resultado a los pesos | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 132 | Antes de que la junta decida sobre R-007, prepará el expediente con todo lo aplicable: tolerancias, apetito, registros relacionados, lecciones y las cifras de las opciones | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 133 | Score the two vendors with weighted criteria and knock-out thresholds, check how sensitive the ranking is to the weights, and record the executive's choice | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 134 | Ya tengo el VAN de las tres opciones de negocio; sumá riesgo y ajuste estratégico con pesos explícitos y dame una pregunta cerrada para que la ejecutiva elija | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 11 | Escribí el business case con VAN y payback | pm-caso-de-negocio | pm-caso-de-negocio | OK |
| 12 | Definamos los OKR del proyecto para el próximo semestre | pm-okr | pm-okr | OK |
| 21 | La junta tiene que aprobar el fin de etapa, prepará la decisión | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 36 | Necesitamos licitar el desarrollo con tres proveedores | pm-adquisiciones | pm-adquisiciones | OK |
| 73 | El comité de dirección tiene que decidir si seguimos con la etapa 3 | pm-direccion-decisiones | pm-direccion-decisiones | OK |
| 83 | Llevá esta solicitud al comité de control de cambios | pm-issues-cambios | pm-issues-cambios | OK |
| 103 | Para los riesgos altos compará evitar, reducir, transferir y aceptar con contingencia, y decime cuál conviene | pm-riesgos | pm-riesgos | OK |

Observaciones:
- La 103 (comparar respuestas de riesgo sin pedir pesos) sigue en `pm-riesgos`, y la 11 (VAN y payback) en
  `pm-caso-de-negocio`: la matriz solo atrae los pedidos que nombran pesos, criterios o una matriz de decisión.
- La 132 nombra un riesgo y aun así eligió la skill de dirección, porque pide el material para que decida la junta.
- Dos corridas por frase, con descripciones distintas: la variabilidad del modelo no está medida con rigor. Antes de
  publicar la versión, correr `suite.py todo` (incluye todas las frases).
