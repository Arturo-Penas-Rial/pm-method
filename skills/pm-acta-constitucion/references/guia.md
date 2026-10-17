# Guía de acta y PID · Charter and PID guide

## 1. Acta, PID o ambos
| Contexto | Producir | Motivo |
|---|---|---|
| Organización sin cultura PRINCE2, proyecto chico | acta mínima fusionada con enunciado del alcance + PID `documento` breve | una sola firma; el PID breve sostiene los controles |
| Entorno PRINCE2 o PMO que audita | PID `indice` (+ acta de una página para firmas, opcional) | trazabilidad de cada componente |
| Ágil mínimo | PID `compacto`; acta solo si el patrocinador la pide | evitar duplicar el brief |
| Contrato con cliente externo | PID `indice` con secciones confidenciales + acta para el cliente | el business case del proveedor no se comparte |

Formatos: (a) acta sola (proyectos pequeños o entornos PMBOK); (b) PID solo (entornos PRINCE2); (c) ambos (el acta como resumen de una a tres páginas del PID para firmas y comunicación).

## 2. PID compacto (perfil ágil mínimo, SPEC §1.10.12)
Formato `compacto` de `templates/pid.md`, un documento de 3–5 páginas:
| Sección del PID | Contenido | Fuente |
|---|---|---|
| Definición y enfoque | brief ligero + visión; enfoque ágil dentro de etapas | `pm-mandato-y-brief` |
| Business case | una página: costo fijo, beneficios por escenario MoSCoW | `pm-caso-de-negocio` |
| Estructura y roles | junta de tres intereses + product owner (usuario sénior delegado) + equipo con punto único de contacto | `pm-organizacion-roles` |
| Enfoques | una página cada uno (calidad con DoD/DoR, riesgo, issues y cambios con swaps del PO, comunicación, datos) | `pm-enfoques-gestion` |
| Plan de proyecto | backlog priorizado (MoSCoW, puntos, criterios de aceptación), release plan por etapas, presupuesto por iteración | `pm-agil-hibrido`, `pm-costos-presupuesto` |
| Controles | etapas = grupos de releases; tiempo/costo fijos, alcance en MoSCoW; highlight corto con burn-up | este documento |
| Adaptación | qué se omitió (PBS/WBS completa, diccionario) y por qué | este documento |
Las puertas de etapa se mantienen; se aligeran los documentos, no las decisiones.

## 3. Controles del proyecto
- Número y límites de etapas: etapa 1 = iniciación; etapas de entrega 2…n. El plan que acompaña al PID para `autorizar-etapa` es `plan-etapa-2.md`.
- Tolerancias por nivel: proyecto en `estado.json` (`estado.py tolerancia --nivel proyecto`); etapa, la fija la junta en cada `autorizar-etapa`; paquete de trabajo, vive en cada `WP-###`.
- Frecuencia y formato de informes (highlight, checkpoint); procedimiento de escalado (jefe de equipo → gestor → junta → negocio); autoridad delegada y su monitoreo; presupuesto de riesgo y de cambio.
- Comprobar que `estado.json.tolerancias` coincide con el texto del PID.

## 4. Sección de adaptación de PRINCE2
- Fuentes: brief (requisitos de adaptación conocidos) y decisiones de los enfoques.
- Listar: técnica propia sustituida (gestión del caso de negocio, diseño organizacional, planificación basada en productos, gestión de la calidad), cambios de terminología (p. ej. "product owner" ≈ usuario sénior delegado), productos combinados u omitidos y por qué.
- Diagnóstico de adaptación con la técnica PMBOK de `pmbok8-dominios-procesos-adaptacion.md` §3.4–3.6, aplicada dentro de IP.
- Con BMAD: declarar que la especificación de producto se produce con BMAD como productos especialistas y que la PBS se sustituye o se complementa con referencias a ids del PRD.

## 5. Checklist de consistencia y ejemplo
Comprobar:
- Presupuesto igual en acta, business case y plan.
- Hitos iguales en acta, roadmap y plan.
- Tolerancias iguales en PID, `estado.json` y enfoques.
- Un solo ejecutivo; separación gestor / ejecutivo / aseguramiento.
- Cada enfoque nombra sus escalas y las mismas se usan en los registros.
- Cada producto mayor del plan tiene descripción de producto (o ids del PRD) y vía de entrega (híbrido).
- La adaptación justifica cada desviación.
Ejemplo: el acta dice "presupuesto preaprobado 240 k", el business case "costo 228 k + reserva de gestión 12 k" y el plan "BAC 228 k". Coinciden si el acta muestra el **presupuesto autorizado** (BAC + reserva de gestión, SPEC §1.10.6): se corrige la etiqueta del acta, no la cifra, y se anota en "Consistencia" con ambas rutas.

## 6. Variante BMAD
| Sección del PID | Qué se pone | Qué no |
|---|---|---|
| Definición del proyecto | resumen del brief + referencia al brief de producto BMAD (ruta, sha) | problema/usuarios copiados |
| Enfoque del proyecto | ruta de planificación BMAD elegida; artefactos BMAD como productos especialistas en paquetes de trabajo | flujos BMAD por nombre como obligatorios |
| Plan de proyecto | PBS/descripciones que citan FR/NFR; matriz de trazabilidad derivada (`bmad.py trazabilidad`) | listas de requisitos |
| Controles | línea base del PRD y arquitectura en `autorizar-proyecto`; `verificar` en cada período y antes de cada puerta; desvío = solicitud de cambio | el "sí" del correct-course como decisión |
| Adaptación | BMAD como capa de especificación, compatibilidad declarada | — |
Precondición adicional de la puerta: PRD con `status: final`, arquitectura suficiente para estimar y `bmad.py verificar` sin desvíos no tratados.

## 7. Reglas extendidas
1. [PRINCE2] El PID tiene tres usos: base sólida antes de comprometer recursos mayores, punto de comparación para progreso e issues, referencia para quien se incorpora; cada sección sirve a al menos uno.
2. [PRINCE2] Ensamblar el PID es la actividad donde soporte de proyecto ejecuta y el gestor rinde cuentas; aseguramiento se consulta antes de pedir la autorización.
3. [PRINCE2] Cada producto de gestión del PID con creador, revisor y aprobador identificados.
4. [PMBOK→Organizing/IP] En el acta, el riesgo general se valora con un criterio declarado (volatilidad, incertidumbre, complejidad, ambigüedad).
5. [Plantillas] Al fusionar artefactos (acta + enunciado del alcance; visión + acta en híbridos) se conservan los campos obligatorios de ambos y el título declara la fusión.
6. [Plantillas] Al reducir a mínima se lista lo omitido y por qué; al ampliar, nada de texto genérico: `[por confirmar]`.
7. [Plantillas] Criterios de salida objetivos (aceptación firmada, ciclos en operación, traspaso), nunca "cuando el patrocinador esté satisfecho".
8. [Plantillas] Perfil ágil mínimo: PID compacto con backlog y release plan en lugar de PBS/WBS completa.

## 8. Casos borde
- Discrepancias no resueltas → issue `problema-preocupacion` (severidad `mayor` si afecta tolerancias) y acción `A-###` en `acciones.csv` para el dueño del componente; PID no apto para la puerta hasta resolverlas.
- Cambio al mandato durante la iniciación → solicitud de cambio o cierre prematuro, según decida la junta; `pm-director`.
- Proveedor externo → secciones confidenciales (business case del cliente) acordadas con el ejecutivo.
- PID mantenido en una wiki conectada → la fuente de verdad sigue en la carpeta del proyecto; publicar copia vía `pm-integraciones` con confirmación.
