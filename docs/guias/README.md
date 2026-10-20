# Guías de recorrido de punta a punta (E2E) · pm-method 2.3.0

Cinco guías paso a paso para **probar las capacidades del ecosistema como usuario**, escribiendo prompts en Claude
Code. Cada una recorre un ciclo completo con un escenario ficticio y empieza por cuatro bloques breves: **por qué
importa** (el problema real y lo que cuesta hacerlo a mano o no hacerlo), **qué vas a lograr**, **indicadores que vas a
ver** (imágenes de la corrida real con una línea de lectura) y **clases** (qué pasos cubre cada clase de 90 minutos).
La sección **"Del uso único al control continuo"** de cada guía compara cómo se hace hoy cada actividad (a mano, una
vez o nunca) con la frecuencia y el control de pm-method (código de sanidad o de puerta) y el indicador que lo muestra.
Las cinco guías son también el material del webinar: guion del instructor, ejercicio y diapositivas en
[docs/webinar/](../webinar/README.md).

| Guía | Ciclo que recorre | Skills y agentes principales | Gráficos que obtenés | Duración |
|---|---|---|---|---|
| [E2E-1 · Gestión de riesgos](E2E-1-riesgos.md) | enfoque y apetito → identificar desde cuatro fuentes con cita (BMAD, transcripciones, Jira, artefactos sin BMAD) → evaluar (P×I, EMV) → responder con costo justificado y riesgo secundario → presupuesto de riesgo fijado por la junta y reserva vigilada (CAM-02, CAM-03) → riesgo que ocurre (Jira) → escalamiento y business case → revisión periódica con el resumen de inicio de sesión y REG-09 → reserva al 80 % → límite de etapa → variante sin BMAD | pm-riesgos, pm-enfoques-gestion, pm-bmad-puente, pm-reuniones, pm-integraciones, pm-registros, pm-issues-cambios, pm-planificacion-por-productos, pm-interesados, pm-visuales, pm-director | mapa de calor inherente y residual, exposición antes y después y su tendencia, riesgos con la revisión vencida, consumo de la reserva, tarjetas de fin de etapa, tablero | 15 pasos · 2 clases de 90 min (120–150 min de práctica) |
| [E2E-2 · Alcance, cambio, esfuerzo, priorización y mapa de ruta](E2E-2-alcance-roadmap.md) | alcance por productos y descripciones de producto → PBS/WBS y trazabilidad → PERT y camino crítico → MoSCoW y capacidad → presupuesto, business case con VAN (`inversion.py`), tolerancias y autoridad de cambio con presupuesto y límite → línea base → intercambio del PO → cambio de alcance con tabla de impacto (tiempo, reserva, presupuesto, autoridad, capacidad, VAN) → trazabilidad recalculada → EVM ágil guardado, disparador de riesgo y calidad (QUA-01) → excepción: aprobación fuera de la autoridad rechazada al registrar, TOL-01, informe, plan con business case actualizado, presupuesto ampliado, puerta y REG-09 | pm-planificacion-por-productos, pm-cronograma-estimacion, pm-costos-presupuesto, pm-caso-de-negocio, pm-agil-hibrido, pm-issues-cambios, pm-riesgos, pm-progreso-reportes, pm-calidad, pm-bmad-puente, pm-visuales, pm-director | Gantt con camino crítico, hitos antes y después de C-001, cobertura de trazabilidad, consumo del presupuesto de cambio, alcance que no entra, VAN por escenario, tarjetas | 10 pasos · 2 clases de 90 min (85–115 min de práctica) |
| [E2E-3 · Interesados, comunicaciones, OKR y avance](E2E-3-interesados-okr-avance.md) | junta y maestro de interesados → matriz poder/interés con estrategia → estereotipos y preferencias declaradas → plan de compromiso → beneficios del business case y OKR que los complementan (P-04) → RACI e integridad del maestro → taller y acta → avance (EVM, BMAD, check-ins) → contexto al retomar la sesión → highlight desde el dato con cadena de reporte → envío por canales con confirmación humana (`guardian.py`) → reporte de interesados → compromiso sostenido (STK-12) y brecha de compromiso | pm-interesados, pm-comunicacion-stakeholders, pm-caso-de-negocio, pm-okr, pm-reuniones, pm-progreso-reportes, pm-integraciones, pm-visuales, pm-exportar, pm-director | matriz poder/interés, RACI y perfiles (reporte HTML), indicadores del highlight, salud de los KR, cadencia de contacto (STK-12), brecha de compromiso, tablero y tablero por actor | 14 pasos · 2 clases de 90 min (110–140 min de práctica) |
| [E2E-4 · Producto de la idea al producto con BMAD](E2E-4-producto-bmad.md) | idea → brief → PRD, UX y arquitectura (BMAD) → puertas → épicas e historias → WBS y trazabilidad → backlog → readiness con condición formal (EST-12, G-01) → sprints → cambio de rumbo con presupuesto de cambio → sesión retomada con resumen de contexto → calidad a volumen (QUA-01, QUA-02, QUA-03) → recorrido de la socia sobre lo entregado (UJ-1, MAP-03, R-001) → Release 1 y condición cumplida → Release 2 con un rechazo tratado → aceptación, traspaso y paquete de cierre → revisiones de beneficios posteriores (trayectoria y tolerancia) | pm-bmad-puente, pm-mapas-estrategicos, pm-calidad, pm-issues-cambios, pm-riesgos, pm-caso-de-negocio, pm-okr, pm-cierre-proyecto, pm-exportar, pm-visuales, pm-director; del lado BMAD: bmad-forge-idea … bmad-retrospective | calidad por entrega, recorrido del cliente, burn-up, tablero, cierre en una página, beneficios contra la tolerancia | 13 pasos (0–11 y 6b) · 2 clases de 90 min con el fixture |
| [E2E-5 · De la idea al proyecto diseñado](E2E-5-idea-a-proyecto.md) | mandato y lecciones → mapa de supuestos y experimentos (SUP-01…03) → opciones 0/1/2 con `inversion.py` (VAN, TIR, repago, equilibrio) → enfoque de entrega con nueve criterios (`set --por`) → mapa de valor y recorrido del paciente (MAP-02, MAP-03) → brief y `autorizar-inicio` → contexto de sesión y beneficios (P-04) → PBS/WBS → riesgos, reservas y presupuestos de la junta → organización, interesados y RACI → enfoques adaptados y tres diseños → PID, P-11 validado o aceptado por la junta y `autorizar-proyecto` → tablero y seguimiento (SUP-02, REG-09); variante con BMAD: supuestos desde el descubrimiento, recorrido UJ-2 con backstage y mapa de valor desde la arquitectura (MAP-01…04) | pm-mandato-y-brief, pm-caso-de-negocio, pm-mapas-estrategicos, pm-enfoques-gestion, pm-acta-constitucion, pm-planificacion-por-productos, pm-costos-presupuesto, pm-riesgos, pm-interesados, pm-bmad-puente, pm-visuales, pm-director | mapa de supuestos, VAN por opción, enfoque por entregable, mapa de Wardley, recorrido del paciente, presupuesto con reservas, tres diseños, tablero | 18 pasos · 2 clases de 90 min (120–150 min de práctica) |

## Cómo usar las guías

**Preparación común** (una vez, en tu terminal):
```bash
git clone https://github.com/Arturo-Penas-Rial/pm-method.git ~/pm-method        # si todavía no lo tenés
mkdir -p ~/proyectos-prueba
cp -r ~/pm-method/scripts/pruebas/fixtures/bmad-v6.12-real ~/proyectos-prueba/portal-e2e-1   # una copia por guía
cd ~/proyectos-prueba/portal-e2e-1
claude                     # con el plugin instalado (docs/INSTALACION.md §0)
# o, para probar tu versión local: claude --plugin-dir ~/pm-method
```
La copia trae una instalación real de **BMAD 6.12.4** con brief, PRD, arquitectura y épicas ya en `status: final`
(proyecto ficticio "Portal de autoservicio para socios" de una cooperativa). Así podés concentrarte en el gobierno;
la guía E2E-4 explica además cómo producir esos artefactos desde cero con BMAD.

**Cómo leer cada paso**

| Bloque | Qué es |
|---|---|
| **Prompt** | lo que escribís en Claude Code (copiar y pegar). Podés cambiar datos; los nombres son ficticios. |
| **Si te pregunta** | lo que respondés cuando el sistema pide datos o una decisión (con nombre y rol: así queda registrado quién decidió). |
| **Qué hace el sistema** | agente, skill y comandos que ejecuta por detrás (referencia: no los escribís). |
| **Qué deberías ver** | resultado esperado, con cifras reales de la corrida de referencia. |
| **Dónde verificar** | archivo, registro o campo que cambió, y un prompt de verificación. |

**Fechas.** Las guías usan fechas del escenario (oct-2026 a may-2027). Decilas en el prompt cuando importen ("con fecha
2026-10-29"). Algunos archivos usan la fecha del día en que corrés la guía (listas de control de puertas, documentos de
traspaso a BMAD): es lo esperado.

**Decisiones humanas.** pm-method nunca decide por vos: aprobaciones, puertas, cambios y respuestas a riesgos quedan
pendientes hasta que respondés con nombre y rol. Si no respondés, el paso queda `[por confirmar]`.

**Si algo sale distinto.** Los modelos de lenguaje no responden siempre igual: el texto de los informes variará; los
**identificadores, registros, cálculos y controles** (R-001, EMV, CPM, EVM, sanidad, puertas) son deterministas y deben
coincidir. Si un registro no aparece, pedí "Mostrame el registro de …" o `/pm-method:pm-estado`, y corré
`/pm-method:pm-sanidad`.

## Evidencia reproducible

Las cifras de "Qué deberías ver" salen de correr **los mismos scripts que usan las skills** sobre una copia del
fixture, con las decisiones humanas simuladas:
```bash
python3 scripts/pruebas/guias_e2e/correr.py --salida /tmp/guias     # ≈ 2 minutos, sin consumo de tokens
```
Escribe `salida-g1.md` … `salida-g5.md` (cada comando con su salida) y las 42 imágenes de las guías: los gráficos de
1600 × 900 (con `matplotlib`), las capturas de tableros, tableros de mapas, reportes y recorridos (con `playwright`; sin
él se omiten con un aviso; los `-169` son recortes 16:9 para diapositivas) y los mapas de Wardley (con `mmdc`). Dos corridas seguidas dan la misma evidencia: las fechas del escenario se
fijan con `--fecha` y `--corte`. En esos registros, `$PLUGIN` es la raíz del repositorio pm-method; `$EST`, `$BMAD`, `$OKR`, `$PAQ`, `$IN` y `$EV` son
`$PLUGIN/skills/pm-estado-proyecto/scripts`, `…/pm-bmad-puente/scripts/bmad.py`, `…/pm-okr/scripts/okr.py`,
`…/pm-exportar/scripts/paquete.py`, `…/pm-interesados/scripts/interesados.py` y `…/pm-integraciones/scripts/envios.py`;
`<repo>` es la carpeta temporal del proyecto de prueba; los Message-ID de los correos se muestran como `<message-id>`.
La guía 3 envía a un servidor SMTP y a un receptor de webhooks de prueba que levanta en 127.0.0.1 (sin salir a la red). La corrida de referencia está en [evidencia/](evidencia/) y las capturas en [img/](img/). Lo que redacta el
modelo (texto de planes e informes) se reemplaza en esa corrida por archivos mínimos: lo que se verifica es el gobierno,
los registros y los cálculos.

EN: five end-to-end walkthroughs (risks; scope, change, estimation, prioritization and roadmap; stakeholders,
communications, OKR and progress; product from idea to delivery with BMAD; from idea to a designed project, with Wardley and journey maps) written as user prompts, with expected
results from a reproducible scripted run.
