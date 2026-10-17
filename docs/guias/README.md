# Guías de recorrido de punta a punta (E2E) · pm-method 2.1.0

Cuatro guías paso a paso para **probar las capacidades del ecosistema como usuario**, escribiendo prompts en Claude
Code. Cada una recorre un ciclo completo y termina con un reporte y representaciones gráficas.

| Guía | Ciclo que recorre | Skills y agentes principales | Gráficos que obtenés | Duración |
|---|---|---|---|---|
| [E2E-1 · Gestión de riesgos](E2E-1-riesgos.md) | identificar → evaluar (P×I, EMV) → responder → presupuesto de riesgo → seguimiento → materialización → escalamiento → auditoría | pm-riesgos, pm-registros, pm-issues-cambios, pm-planificacion-por-productos, pm-organizacion-roles, pm-visuales, pm-director | matriz de calor P×I, exposición antes/después, mapa riesgo ↔ WBS ↔ interesados, tablero | 60–90 min |
| [E2E-2 · Alcance, cambio, esfuerzo, priorización y mapa de ruta](E2E-2-alcance-roadmap.md) | enunciado de alcance → PBS/WBS → trazabilidad → PERT y camino crítico → MoSCoW y valor/esfuerzo → release plan → línea base → swap del PO → cambio de alcance → nuevo roadmap | pm-planificacion-por-productos, pm-cronograma-estimacion, pm-costos-presupuesto, pm-agil-hibrido, pm-issues-cambios, pm-bmad-puente, pm-visuales | WBS, Gantt con camino crítico, cuadrante valor/esfuerzo, roadmap antes/después | 60–90 min |
| [E2E-3 · Interesados, comunicaciones, OKR y avance](E2E-3-interesados-okr-avance.md) | registro y análisis → mapa poder/interés → plan de compromiso y matriz de comunicaciones → OKR ligados a beneficios → acta de reunión → avance (EVM, BMAD) → highlight → tablero con vista por actor → comunicación por audiencia | pm-organizacion-roles, pm-comunicacion-stakeholders, pm-okr, pm-reuniones, pm-progreso-reportes, pm-visuales | mapa poder/interés, matriz de compromiso, OKR por corte, curva EVM, burn-up, tablero | 60–90 min |
| [E2E-4 · Producto de la idea al producto con BMAD](E2E-4-producto-bmad.md) | idea → brief → PRD/UX/arquitectura (BMAD) → puertas → épicas e historias → WBS y trazabilidad → backlog → readiness → sprints → cambio de rumbo → Release 1 → Release 2 → aceptación → beneficios → cierre | pm-bmad-puente, todas las de gobierno, pm-director; del lado BMAD: bmad-forge-idea, bmad-product-brief, bmad-prd, bmad-ux, bmad-architecture, bmad-create-epics-and-stories, bmad-sprint-planning, bmad-build, bmad-code-review, bmad-correct-course, bmad-retrospective | ciclo de vida PRINCE2 + BMAD, trazabilidad, burn-up, tablero, OKR | 2–3 h |

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
del tablero. En esos registros, `$PLUGIN` es la raíz del repositorio pm-method; `$EST`, `$BMAD`, `$OKR` y `$PAQ` son
`$PLUGIN/skills/pm-estado-proyecto/scripts`, `…/pm-bmad-puente/scripts/bmad.py`, `…/pm-okr/scripts/okr.py` y
`…/pm-exportar/scripts/paquete.py`; `<repo>` es la carpeta temporal del proyecto de prueba. La corrida de referencia está en [evidencia/](evidencia/) y las capturas en [img/](img/). Lo que redacta el
modelo (texto de planes e informes) se reemplaza en esa corrida por archivos mínimos: lo que se verifica es el gobierno,
los registros y los cálculos.

EN: four end-to-end walkthroughs (risks; scope, change, estimation, prioritization and roadmap; stakeholders,
communications, OKR and progress; product from idea to delivery with BMAD) written as user prompts, with expected
results from a reproducible scripted run.
