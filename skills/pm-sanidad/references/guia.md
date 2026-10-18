# Catálogo de comprobaciones de sanidad · Health check catalogue

## 1. Comprobaciones
| Código | Severidad | Qué verifica | Causa típica | Corrección |
|---|---|---|---|---|
| INS-01 | AVISO | módulos Python (pyyaml, python-docx, openpyxl) | instalación nueva | `pip install …` |
| INS-02 | AVISO | versión de pm-method del proyecto vs instalada | actualización del paquete | leer notas; estado.json migra solo |
| INS-03 | AVISO/INFO | skill externa declarada (archify, diagram-design, visual-explainer; docx/xlsx/pptx con `export=skills-office`) instalada; da el nombre de invocación | integración declarada sin instalar, falta Node/Chrome, o plugin cargado con `--plugin-dir` (no detectable) | instalarla (INSTALACION §6.1) o volver a `mermaid` / `export=scripts` |
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
| REG-08 | AVISO | referencias entre registros (R-, I-, C-, D-, S-, L-, ST-, Q-, A-, ET-, PF-, RC-, EN-) | id mal escrito | corregir |
| CAM-01 | AVISO | cambio aprobado (o implementado, cerrado, `decision=aprobado`) con impacto de costo sin `costo` ni `cargo`, o con costo sin cargo | el costo quedó solo en el texto de `impacto_costo` | `registro.py actualizar cambios C-… --campo costo=… --campo cargo=…` |
| CAM-02 | AVISO | `cargo=reserva-riesgo` sin citar un R-### | la contingencia usada como bolsa general | citar el riesgo, o cargar al presupuesto de cambio o a la junta |
| CAM-03 | INFO/AVISO/ERROR | consumo del presupuesto de cambio y de la reserva de riesgo contra `estado.json.presupuestos`: < 80 % INFO, ≥ 80 % AVISO, > 100 % ERROR (bloquea puertas); AVISO si se cargó sin presupuesto fijado | nadie suma lo que consumen los cambios aprobados | avisar a la junta; excedido: excepción o `estado.py presupuesto … --por` (pm-director) |
| CAM-04 | AVISO | costo > `limite_autoridad_cambio` y no decidió la junta ni el ejecutivo | la autoridad de cambio aprueba por encima de su límite | escalar a la junta (`decision-ad-hoc`) o ajustar el límite |
| CAM-05 | AVISO | `cargo=reserva-gestion` no decidido por la junta | la reserva de gestión liberada sin la junta | decisión de la junta (pm-director) |
| QUA-01 | AVISO | elemento terminado de `02-planificacion/backlog.csv` sin revisión completada y aprobada en `calidad.csv` que lo cite (id o clave corta `N-M`) | con decenas de historias `done`, nadie verifica una por una | pm-calidad: registrar la revisión (también en lote) o reabrir |
| QUA-02 | AVISO | revisión planificada o en curso con `fecha_prevista` vencida al corte | la revisión prometida (p. ej. para cumplir una condición) se olvida | realizarla o replanificarla |
| QUA-03 | AVISO | revisión rechazada sin issue, acción o cambio que cite su Q-### | el rechazo queda sin tratamiento | pm-issues-cambios (fuera de especificación) o acción correctiva |
| TOL-01 | AVISO | el último corte de `evm.py --guardar` (≤ corte) pronostica excepción y no hay excepción abierta ni `autorizar-plan-excepcion` posterior | el pronóstico se calcula para el informe y nadie lo vuelve a mirar | informe de excepción (pm-progreso-reportes) y pm-director |
| TOL-02/03 | INFO | último corte en ámbar; etapa de entrega sin corte guardado o con el último de más de 31 días | EVM sin guardar | `evm.py … --proyecto <dir> --guardar --corte …` en cada período |
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
| STK-00…11 | ERROR/AVISO/INFO | maestro de interesados (claves foráneas, RACI, preferencias, envíos, OKR); solo si existe algún registro opcional | ver `docs/SANIDAD.md` §2.1 | pm-interesados |
| STK-12 | AVISO | interesado de gestionar de cerca, mantener satisfecho o mantener informado cuyo último envío `enviado` supera 1,5 × su frecuencia (diaria 1, semanal 7, quincenal 14, mensual 31, trimestral 92 días) | con muchos interesados, la cadencia prometida se pierde | contactarlo (`envios.py`, o reunión o llamada como envío manual) o revisar la frecuencia |
| INT-01…04 | AVISO | valores de integración conocidos, instantáneas fechadas y recientes | tracker sin leer | pm-integraciones |

## 2. Dueño de cada familia
| Familia | Dueño de la corrección |
|---|---|
| INS | usuario / mantenedor del paquete |
| EST, ART (aprobaciones) | pm-director (pm-direccion-decisiones) |
| REG | pm-registros, pm-riesgos, pm-issues-cambios |
| CAM | pm-issues-cambios; presupuestos, CAM-03 excedido, CAM-04 y CAM-05 → pm-director |
| QUA | pm-calidad |
| TOL | pm-progreso-reportes; excepción → pm-director |
| STK | pm-interesados (STK-07 → pm-integraciones; STK-08 → pm-okr) |
| ESP | pm-bmad-puente, pm-planificacion-por-productos, pm-issues-cambios |
| INT | pm-integraciones |

## 3. Controles permanentes que acompañan a la sanidad
- **Hook PreToolUse (Claude Code)**: impide editar con Write/Edit `estado.json`, los registros CSV, los derivados de especificación y las copias congeladas; impide a los subagentes pm-* escribir en carpetas de BMAD.
- **Hook SessionStart**: sanidad rápida y resumen del proyecto al abrir la sesión.
- **pm-puerta**: no presenta una puerta con ERROR sin decisión humana explícita. Con `condicionado`, los hallazgos de tipo condición pasan a condiciones formales; EST-12 y G-01 (en la verificación de la puerta siguiente; bloqueo en `autorizar-cierre`) las siguen hasta `estado.py cumplir-condiciones <tipo> --fecha … --por … --nota …` (pm-director).
- **Mantenedor**: `scripts/validar_paquete.py` (estructura, orquestación, presupuesto de descripciones) y `scripts/probar_paquete.py` (regresión con BMAD v6, v4 y sin BMAD) después de cualquier cambio del paquete o de BMAD.
- **Hermes** (sin hooks): la sanidad se ejecuta desde pm-orquestador al empezar y desde pm-puerta; puede programarse con el planificador de tareas de Hermes (verificar su sintaxis vigente).
