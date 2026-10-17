# Catálogo de comprobaciones de sanidad · Health check catalogue

## 1. Comprobaciones
| Código | Severidad | Qué verifica | Causa típica | Corrección |
|---|---|---|---|---|
| INS-01 | AVISO | módulos Python (pyyaml, python-docx, openpyxl) | instalación nueva | `pip install …` |
| INS-02 | AVISO | versión de pm-method del proyecto vs instalada | actualización del paquete | leer notas; estado.json migra solo |
| INS-03 | AVISO/INFO | skill externa declarada (archify, diagram-design, visual-explainer) instalada | integración declarada sin instalar | instalarla o volver a `mermaid` |
| INS-04 | AVISO | skill pm-* instalada más de una vez | plugin + copia manual | dejar una sola |
| INS-05 | AVISO | presupuesto del listado de skills (incluye BMAD y otros repos) | muchas skills instaladas | `skillListingBudgetFraction`, `skillOverrides` |
| INS-06 | AVISO | posible colisión de activación con skills de otros repos | disparadores compartidos | ajustar descripciones u ocultar la externa |
| EST-01…04 | ERROR | fase/proceso válidos y puertas que los habilitan | edición manual o puerta faltante | registrar la decisión o corregir |
| EST-05 | AVISO | número de etapa vs puertas | ajuste manual | `estado.py etapa` |
| EST-06/07 | ERROR/AVISO | tolerancias de proyecto y de etapa | olvido al autorizar | `estado.py tolerancia --nivel …` |
| EST-08…10 | ERROR | ejecutivo designado, separación de roles | estructura incompleta | pm-organizacion-roles |
| EST-11…14 | AVISO | puertas pendientes, condiciones abiertas, puertas forzadas, excepción abierta | flujo en curso | pm-direccion-decisiones |
| ART-01…04 | ERROR/AVISO | artefactos registrados existen; estado coherente con el documento; huella de externos | archivos movidos, edición sin script | `estado.py artefacto/aprobar`, `bmad.py linea-base` |
| REG-01…05 | ERROR/AVISO | registros completos, ids y valores del esquema | edición manual de CSV | `registro.py` |
| REG-06/07 | AVISO | riesgos altos sin respuesta, acciones vencidas | seguimiento | pm-riesgos, pm-registros |
| REG-08 | AVISO | referencias entre registros (R-, I-, C-, D-, S-, L-, ST-, Q-, A-) | id mal escrito | corregir |
| ESP-01/02 | ERROR/INFO | especificación legible; índice vigente | ruta BMAD movida | `bmad.py detectar`, `especificacion.py indice` |
| ESP-03 | AVISO→ERROR en entrega | requisitos sin cobertura (historia o paquete WBS) | alcance no planificado | planificar o retirar vía cambio |
| ESP-04 | ERROR | ids citados en WBS, registros y OKR existen | id inventado o retirado | corregir o tramitar cambio |
| ESP-05 | AVISO | beneficios citados por OKR existen en el business case | desalineación | pm-caso-de-negocio / pm-okr |
| ESP-06…08 | ERROR/AVISO | BMAD detectado, versión probada, carpeta del proyecto fuera de BMAD | instalación o ubicación | `bmad.py detectar`, mover carpeta |
| ESP-09/10 | ERROR | líneas base vs especificación actual; desvío sin issue = **cambio no controlado** | edición del PRD fuera del control de cambios | pm-issues-cambios |
| ESP-11 | ERROR | línea base del PRD antes de las etapas de entrega | puerta sin fijar línea base | pm-director: `bmad.py linea-base` |
| ESP-12 | AVISO | Sprint Change Proposals sin tratar | flujo BMAD sin pasar a gobierno | `bmad.py verificar` + issue |
| ESP-13 | AVISO | traspasos a BMAD sin confirmar | equipo BMAD no aplicó o no marcó | marcar `estado: aplicado`, verificar, nueva línea base |
| ESP-14/15 | AVISO | derivados desactualizados o editados; backlog vs estado BMAD | falta sincronizar | `bmad.py requisitos/backlog` |
| INT-01…04 | AVISO | valores de integración conocidos, instantáneas fechadas y recientes | tracker sin leer | pm-integraciones |

## 2. Dueño de cada familia
| Familia | Dueño de la corrección |
|---|---|
| INS | usuario / mantenedor del paquete |
| EST, ART (aprobaciones) | pm-director (pm-direccion-decisiones) |
| REG | pm-registros, pm-riesgos, pm-issues-cambios |
| ESP | pm-bmad-puente, pm-planificacion-por-productos, pm-issues-cambios |
| INT | pm-integraciones |

## 3. Controles permanentes que acompañan a la sanidad
- **Hook PreToolUse (Claude Code)**: impide editar con Write/Edit `estado.json`, los registros CSV, los derivados de especificación y las copias congeladas; impide a los subagentes pm-* escribir en carpetas de BMAD.
- **Hook SessionStart**: sanidad rápida y resumen del proyecto al abrir la sesión.
- **pm-puerta**: no presenta una puerta con ERROR sin decisión humana explícita.
- **Mantenedor**: `scripts/validar_paquete.py` (estructura, orquestación, presupuesto de descripciones) y `scripts/probar_paquete.py` (regresión con BMAD v6, v4 y sin BMAD) después de cualquier cambio del paquete o de BMAD.
- **Hermes** (sin hooks): la sanidad se ejecuta desde pm-orquestador al empezar y desde pm-puerta; puede programarse con el planificador de tareas de Hermes (verificar su sintaxis vigente).
