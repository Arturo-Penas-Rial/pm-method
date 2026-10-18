# Guías de recorrido de punta a punta (E2E) · pm-method 2.2.0

Cuatro guías paso a paso para **probar las capacidades del ecosistema como usuario**, escribiendo prompts en Claude
Code. Cada una recorre un ciclo completo y termina con un reporte y representaciones gráficas. Cada guía tiene además
una tabla "Controles permanentes que muestra esta guía": problemas que en la práctica se controlan a mano, tarde o
nunca (por falta de estándar, por trabajo manual o por volumen) y el control automático que los detecta (código de
sanidad o de puerta) en el paso donde aparece.

| Guía | Ciclo que recorre | Skills y agentes principales | Gráficos que obtenés | Duración |
|---|---|---|---|---|
| [E2E-1 · Gestión de riesgos](E2E-1-riesgos.md) | identificar desde cuatro fuentes (BMAD, transcripciones, Jira, artefactos sin BMAD) → evaluar (P×I, EMV) → responder con costo justificado → presupuesto de riesgo fijado por la junta y consumo de la reserva vigilado (CAM-02, CAM-03) → seguimiento → materialización desde Jira → escalamiento → auditoría → variante sin BMAD | pm-riesgos, pm-bmad-puente, pm-reuniones, pm-integraciones, pm-registros, pm-issues-cambios, pm-planificacion-por-productos, pm-interesados, pm-visuales, pm-director | matriz de calor P×I, exposición antes/después, mapa riesgo ↔ WBS ↔ interesados, tablero | 13 pasos, 90–115 min |
| [E2E-2 · Alcance, cambio, esfuerzo, priorización y mapa de ruta](E2E-2-alcance-roadmap.md) | enunciado de alcance y descripciones de producto → PBS/WBS → trazabilidad → PERT y camino crítico → MoSCoW y valor/esfuerzo → presupuesto, tolerancias, autoridad de cambio con presupuesto y límite → release plan y línea base → swap del PO → cambio de alcance con costo y cargo → nuevo roadmap → EVM ágil guardado y calidad de lo terminado (QUA-01) → excepción: cambio sobre la autoridad delegada y pronóstico fuera de tolerancia (CAM-03, CAM-04, TOL-01, informe y plan de excepción) | pm-planificacion-por-productos, pm-cronograma-estimacion, pm-costos-presupuesto, pm-agil-hibrido, pm-issues-cambios, pm-progreso-reportes, pm-calidad, pm-bmad-puente, pm-visuales, pm-director | WBS, Gantt con camino crítico, cuadrante valor/esfuerzo, roadmap antes/después | 10 pasos, 80–110 min |
| [E2E-3 · Interesados, comunicaciones, OKR y avance](E2E-3-interesados-okr-avance.md) | maestro de interesados → matriz poder/interés con estrategia → estereotipos y preferencias (entrevista y transcripción) → RACI sobre épicas, requisitos, WBS y KR → OKR con tipos, iniciativas, check-ins y salud → acta → avance (EVM, BMAD) → highlight, Tability y tablero por actor → comunicación personalizada enviada por canales (correo, Teams, reunión) → reporte de interesados e integridad → compromiso sostenido: cadencia de contacto (STK-12), acción correctiva y reevaluación del compromiso | pm-interesados, pm-comunicacion-stakeholders, pm-integraciones, pm-okr, pm-caso-de-negocio, pm-reuniones, pm-progreso-reportes, pm-visuales | matriz poder/interés y RACI (reporte HTML), perfiles, matriz de compromiso, OKR por corte y tendencia de check-ins, curva EVM, burn-up, tablero | 13 pasos, 100–130 min |
| [E2E-4 · Producto de la idea al producto con BMAD](E2E-4-producto-bmad.md) | idea → brief → PRD/UX/arquitectura (BMAD) → puertas → épicas e historias → WBS y trazabilidad → backlog → readiness con condición formal (EST-12, G-01) → sprints → cambio de rumbo con presupuesto de cambio → calidad a volumen (QUA-01, QUA-02) → Release 1 y condición cumplida → Release 2 → aceptación y traspaso a operación → cierre → primera revisión de beneficios posterior al proyecto | pm-bmad-puente, todas las de gobierno, pm-director; del lado BMAD: bmad-forge-idea, bmad-product-brief, bmad-prd, bmad-ux, bmad-architecture, bmad-create-epics-and-stories, bmad-sprint-planning, bmad-build, bmad-code-review, bmad-correct-course, bmad-retrospective | ciclo de vida PRINCE2 + BMAD, trazabilidad, burn-up, tablero, OKR | 15 pasos, 3–4 h |

## Cómo usar las guías

**Preparación común** (una vez, en tu terminal):
```bash
git clone https://github.com/Arturo-Penas-Rial/pm-method.git ~/pm-method        # si todavía no lo tenés
mkdir -p ~/proyectos-prueba
cp -r ~/pm-method/scripts/pruebas/fixtures/bmad-v6.12-real ~/proyectos-prueba/portal-e2e-1   # una copia por guía
cd ~/proyectos-prueba/portal-e2e-1
claude                     # con el plugin instalado (modo A de MIGRACION/INSTALACION)
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
python3 scripts/pruebas/guias_e2e/correr.py --salida /tmp/guias     # ≈ 1 minuto, sin consumo de tokens
```
Escribe `salida-g1.md` … `salida-g4.md` (cada comando con su salida) y, si está instalado `playwright`, las capturas
del tablero y del reporte de interesados. En esos registros, `$PLUGIN` es la raíz del repositorio pm-method; `$EST`, `$BMAD`, `$OKR`, `$PAQ`, `$IN` y `$EV` son
`$PLUGIN/skills/pm-estado-proyecto/scripts`, `…/pm-bmad-puente/scripts/bmad.py`, `…/pm-okr/scripts/okr.py`,
`…/pm-exportar/scripts/paquete.py`, `…/pm-interesados/scripts/interesados.py` y `…/pm-integraciones/scripts/envios.py`;
`<repo>` es la carpeta temporal del proyecto de prueba; los Message-ID de los correos se muestran como `<message-id>`.
La guía 3 envía a un servidor SMTP y a un receptor de webhooks de prueba que levanta en 127.0.0.1 (sin salir a la red). La corrida de referencia está en [evidencia/](evidencia/) y las capturas en [img/](img/). Lo que redacta el
modelo (texto de planes e informes) se reemplaza en esa corrida por archivos mínimos: lo que se verifica es el gobierno,
los registros y los cálculos.

EN: four end-to-end walkthroughs (risks; scope, change, estimation, prioritization and roadmap; stakeholders,
communications, OKR and progress; product from idea to delivery with BMAD) written as user prompts, with expected
results from a reproducible scripted run.
