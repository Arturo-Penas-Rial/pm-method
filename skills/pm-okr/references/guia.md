# Guía de OKR del proyecto · Project OKR guide

## §1. Dónde encajan los OKR en PRINCE2
- PRINCE2 encadena **salidas** (productos del proyecto) → **resultados** (cambios observables al usarlos) → **beneficios** (mejoras medibles que alguien valora) → **objetivos de negocio** de la organización. El business case es el dueño de esa cadena.
- Los OKR pertenecen a la **capa de negocio** (o a la gestión de producto) y expresan la misma cadena en el lenguaje que la organización ya usa para fijar metas trimestrales o anuales. No son un producto de gestión PRINCE2: no figuran en el PID como documento obligatorio, no tienen puerta propia y no reemplazan al enfoque de gestión de beneficios.
- Correspondencia práctica:

| Concepto OKR | Equivalente PRINCE2 | Dónde vive el dato |
|---|---|---|
| Objetivo (O-n) | Objetivo de negocio al que contribuye el proyecto (OBJ-n) | business case |
| Resultado clave (KR-n.m) | Indicador de un beneficio (B-nn) o métrica de éxito del producto (SM-n) | business case / enfoque de beneficios / PRD |
| Iniciativas | Productos y paquetes de trabajo del plan | plan de proyecto / etapa |
| Check-in | Información de progreso para la junta | highlight, informe de fin de etapa |

- Quién hace qué: el **ejecutivo** es dueño del objetivo y responde por los beneficios; el **usuario sénior** especifica y realiza los beneficios, por lo que suele ser dueño de los KR; el **gestor del proyecto** mantiene `okr.csv` y produce la tabla puntuada; el **aseguramiento** verifica que los vínculos existan.

## §2. Redactar buenos objetivos y KR
Objetivo: cualitativo, inspirador pero concreto, limitado en el tiempo, uno a tres por proyecto. KR: cuantitativo, con línea base, meta y fecha; dos a cinco por objetivo.

Ejemplo inventado (proyecto de autogestión de turnos en una red de clínicas):
- O-1 "Que los pacientes resuelvan sus turnos sin llamar" · `vinculo=OBJ-2` (reducir costo de atención) · responsable: Ejecutivo.
  - KR-1.1 Turnos tomados por canal digital: 18 % → 60 % al 2027-06-30 · `B-01`.
  - KR-1.2 Llamadas al call center por turnos/semana: 4 200 → 2 000 · `B-02`.
  - KR-1.3 Tasa de finalización del flujo de reserva: 55 % → 85 % · `SM-3`.

Antipatrones y su corrección:
| Mal | Por qué | Mejor |
|---|---|---|
| "Lanzar la app en marzo" | es un hito del plan | "Usuarios activos mensuales: 0 → 5 000" |
| "Mejorar la satisfacción" | sin base ni meta | "NPS de pacientes: 22 → 40" |
| Ocho KR para un objetivo | dispersa el foco | 2–5 KR; el resto, métricas de seguimiento |
| KR sin vínculo | no se puede justificar | vincular a B-nn/SM-n o pedir el beneficio faltante |

## §3. Vínculos sin duplicar datos
- `vinculo` acepta uno o varios ids separados por `;` (`B-01;SM-3`). El script exige al menos uno `B`, `SM` u `OBJ` en cada KR; el paquete exige además que los KR usen B o SM (OBJ solo en objetivos). Revisarlo a mano.
- El beneficio conserva su medida, base, meta, fecha, dueño y tolerancia en el business case/enfoque de beneficios. En `okr.csv` se repiten solo `linea_base` y `meta` cuando el script los necesita para puntuar, con `notas=fuente: business-case v1.0 §beneficios`. Si el business case cambia, se actualiza primero allí y después en el OKR.
- Una meta de KR más ambiciosa que la meta del beneficio es válida (estiramiento), pero la tolerancia y la justificación se juzgan siempre contra el beneficio.
- SM-n del PRD: el PRD es dueño de su definición; el OKR cita el id y la fuente (`requisitos-bmad.csv`, sha corto).

## §4. Puntuación, semáforo, salud y check-ins
- **Por tipo de KR** (`tipo_kr`, defecto `de-a`):

| tipo_kr | Puntuación | Ejemplo |
|---|---|---|
| `de-a` | `(actual − base) / (meta − base)`, acotada a 0–1; sirve para metas de reducción | base 4 200, meta 2 000, actual 3 100 → 0,50 |
| `mantener-sobre` / `mantener-bajo` | 1 si cumple el umbral (`meta`), 0 si no | satisfacción ≥ 4 |
| `binario` | 1 si `actual` es sí, hecho, 1 o 100 %; 0 si no | certificación obtenida |
| `hito` | proporción (ponderada por `peso`) de iniciativas `IN-n` completadas; sin iniciativas, `actual` como % | pago en línea publicado |

- **Objetivo** = promedio **ponderado** por `peso` (defecto 1) de sus KR con dato.
- **Semáforo**: aspiracional (defecto) ≥ 0,7 verde · 0,4–0,69 ámbar · < 0,4 rojo; comprometido ≥ 1,0 verde · 0,7–0,99 ámbar · < 0,7 rojo. Convenciones difundidas de la práctica OKR (la guía de Google re:Work considera sana la zona 0,6–0,7 en metas aspiracionales y espera 1,0 de las comprometidas), **no** reglas de PRINCE2 ni del PMBOK. `--umbrales verde,ambar` cambia el par aspiracional; declararlo en el informe. Fuente: https://rework.withgoogle.com/en/guides/set-goals-with-okrs
- **Salud** (independiente del semáforo): compara la puntuación con el avance esperado lineal entre `fecha_inicio` (del KR, de su objetivo o del primer check-in) y `fecha_meta` a la fecha de corte: `en-camino` (≥ esperado − 0,10), `en-riesgo` (≥ esperado − 0,25), `desviado`. Para binarios y mantener: `en-camino` si cumple; si no, `en-riesgo` antes de la fecha meta y `desviado` después. Un comprometido en rojo a mitad de ciclo puede estar `en-camino`.
- **Confianza** 1–10 del responsable: 1–3 rojo, 4–6 ámbar, 7–10 verde (criterio del paquete para alinear con herramientas que usan rojo/amarillo/verde).
- **Check-ins** (`okr_checkins.csv`, junto a `okr.csv`): `okr.py <csv> --checkin KR-1.1 --valor 900 --confianza 7 --nota … --autor ST-001 [--fecha …]`. Solo se agregan (uno por KR y fecha); el `actual` usado es el último check-in con fecha ≤ corte y, si no hay, la columna `actual`. La tabla Markdown incluye el historial.
- **Historia de los KR de hito**: las iniciativas guardan su estado actual, no su historia; al puntuar un corte pasado se usa el estado de hoy. Para la tendencia de un hito, registrar check-ins con el % de avance o leer la tendencia en los cortes ya publicados.
- **Cascada**: `padre_id` de un objetivo apunta a otro `O-n` (o a un `OBJ-n` del business case); la salida ordena padres antes que hijos (↳).
- **Avisos de calidad** además de los de vínculo: enunciado que empieza con verbo de actividad (realizar, ayudar, analizar…), responsable fuera del maestro, `tipo_kr`/`compromiso`/`peso` inválidos, iniciativa sin KR o sin vínculo a épica, historia o paquete, KR de hito sin iniciativas, check-in de un KR inexistente y todos los KR aspiracionales en 1,0 al cierre (metas posiblemente poco ambiciosas).
- Este semáforo no sustituye al de tolerancias de `evm.py`: uno mide resultados de negocio; el otro, desempeño del plan. `--json` alimenta el tablero de `pm-visuales`.
- Las columnas opcionales y los check-ins no son obligatorios: un `okr.csv` con solo las columnas base es válido.

## §5. Cadencia de revisión
| Momento | Qué se hace | Quién | Dónde queda |
|---|---|---|---|
| SU/IP | Borrador de OKR a partir del business case | gestor + ejecutivo | `00-direccion/okr.md` en revisión |
| `autorizar-proyecto` | Ejecutivo acepta O y KR | ejecutivo | `estado.py aprobar okr` |
| Cada límite de etapa (SB) | Puntuación y lectura de tendencia | gestor → junta | adjunto al informe de fin de etapa |
| Highlight | Solo si un KR afecta la tolerancia de beneficios | gestor | sección de beneficios del highlight |
| Cierre (CP) | Estado final; KR pendientes pasan al plan de revisión de beneficios | gestor + usuario sénior | `04-cierre/plan-revision-beneficios.md` |
| Revisiones post-proyecto | Medición real de KR y beneficios | capa de negocio / usuario sénior | fuera del proyecto; el plan indica quién |

## §6. Tability o Perdoo (opcional) vía pm-integraciones
- Ambas tienen **servidor MCP oficial** (verificado el 17/10/2026): Tability `https://mcp.tability.app/mcp` (también
  `mcp-eu.tability.app/mcp` y `mcp-au.tability.app/mcp`; OAuth; requiere "API access" habilitado para el usuario; escribe
  check-ins con `tability_create_checkin`) — https://guides.tability.io/docs/become-a-tability-power-user/integrations/tability-mcp-server ;
  Perdoo `https://mcp.perdoo.com` (OAuth o API key; registra progreso con `update_goal_progress`: valor, estado y nota) —
  https://support.perdoo.com/en/articles/14470891-mcp-server . El plan comercial que habilita cada uno: [verificar].
- `estado.json.integraciones.okr = tability|perdoo`. Cada KR lleva `ref_externa` (`tability:<id>` o `perdoo:<id>`).
- **Publicar** (escritura): `okr.py <csv> --propuesta-sync tability|perdoo` lista los check-ins sin publicar con la
  herramienta a usar y la confianza traducida (Tability: red/yellow/green); vista previa y confirmación explícita →
  el agente publica con la herramienta MCP → `okr.py <csv> --marcar-publicado KR-1.1@2027-01-05 --destino tability --ref <id>`.
- **Leer**: instantánea `03-control/fuentes/<herramienta>-AAAA-MM-DD.csv` con `clave,tipo,titulo,actual,meta,actualizado,url`
  → registrar el valor como check-in con `--fuente tability|perdoo`.
- `okr.csv` y `okr_checkins.csv` siguen siendo la fuente; sin herramienta conectada, todo funciona igual.
- Atlassian Goals y Asana Goals no se exponían por sus MCP oficiales al 17/10/2026 (solo API) [verificar]; Microsoft Viva Goals se retiró
  el 31/12/2025 (https://learn.microsoft.com/viva/goals/goals-retirement).

## §7. Con BMAD
- Las métricas de éxito SM-n del PRD son candidatas naturales a KR de producto. No se copian: se citan.
- Si un SM cambia o se retira en el PRD, `bmad.py verificar` lo detecta como desvío; el KR asociado queda marcado en `notas` hasta que la autoridad de cambio decida.

## §8. Casos borde
- **Sin línea base**: medirla primero (una acción A-### con responsable); mientras tanto el KR queda sin puntuar y el script lo avisa.
- **Proyecto de cumplimiento normativo**: el beneficio se expresa como consecuencia evitada; un KR válido es "hallazgos de auditoría críticos: 5 → 0".
- **Beneficios después del cierre**: la mayoría de los KR se cumplen después del proyecto; durante el proyecto se miden indicadores adelantados (adopción, uso) y el resto pasa al plan de revisión de beneficios.
- **Varios proyectos contribuyen al mismo OKR**: el OKR es del programa o de la organización; el proyecto declara su contribución y no se atribuye todo el resultado.
- **Meta inalcanzable detectada**: no bajar la meta sin decisión; registrar el pronóstico y, si afecta la tolerancia de beneficios, escalar.
