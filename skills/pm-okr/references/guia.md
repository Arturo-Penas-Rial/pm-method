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

## §4. Puntuación y semáforo
- Fórmula del script: `p = (actual − base) / (meta − base)`, acotada a 0–1. Funciona igual para metas de reducción (base 4 200, meta 2 000, actual 3 100 → p = 0,50).
- Objetivo = promedio simple de sus KR con dato. Si un KR pesa más, explicarlo en la narrativa; el script no pondera.
- Semáforo por defecto ≥ 0,7 verde · 0,4–0,69 ámbar · < 0,4 rojo. Es una convención difundida en la práctica OKR (metas "aspiracionales" donde 0,7 se considera buen resultado), **no** una regla de PRINCE2 ni del PMBOK. Se cambia con `--umbrales verde,ambar` y se declara en el informe. Si la organización usa OKR "comprometidos" (se espera 1,0), usar `--umbrales 1.0,0.7`.
- Este semáforo no sustituye al de tolerancias de `evm.py`: uno mide resultados de negocio; el otro, desempeño del plan.
- `--json` sirve para alimentar el tablero de `pm-visuales`.

## §5. Cadencia de revisión
| Momento | Qué se hace | Quién | Dónde queda |
|---|---|---|---|
| SU/IP | Borrador de OKR a partir del business case | gestor + ejecutivo | `00-direccion/okr.md` en revisión |
| `autorizar-proyecto` | Ejecutivo acepta O y KR | ejecutivo | `estado.py aprobar okr` |
| Cada límite de etapa (SB) | Puntuación y lectura de tendencia | gestor → junta | adjunto al informe de fin de etapa |
| Highlight | Solo si un KR afecta la tolerancia de beneficios | gestor | sección de beneficios del highlight |
| Cierre (CP) | Estado final; KR pendientes pasan al plan de revisión de beneficios | gestor + usuario sénior | `04-cierre/plan-revision-beneficios.md` |
| Revisiones post-proyecto | Medición real de KR y beneficios | capa de negocio / usuario sénior | fuera del proyecto; el plan indica quién |

## §6. Tability (opcional) vía pm-integraciones
- Capacidad `okr`. Detectar herramientas con indicio `tability` en la sesión; leer su descripción real.
- Lectura: objetivos, KR y último check-in → instantánea `03-control/fuentes/tability-AAAA-MM-DD.csv` con columnas `clave,tipo,titulo,actual,meta,actualizado,url` → conciliar por título o por `notas=tability:<clave>` y actualizar `actual`.
- Escritura (crear KR o check-in): solo con vista previa y confirmación explícita; en subagente, devolverla como decisión humana.
- Sin Tability: `okr.csv` es la única fuente; puede exportarse con `pm-exportar`.

## §7. Con BMAD
- Las métricas de éxito SM-n del PRD son candidatas naturales a KR de producto. No se copian: se citan.
- Si un SM cambia o se retira en el PRD, `bmad.py verificar` lo detecta como desvío; el KR asociado queda marcado en `notas` hasta que la autoridad de cambio decida.

## §8. Casos borde
- **Sin línea base**: medirla primero (una acción A-### con responsable); mientras tanto el KR queda sin puntuar y el script lo avisa.
- **Proyecto de cumplimiento normativo**: el beneficio se expresa como consecuencia evitada; un KR válido es "hallazgos de auditoría críticos: 5 → 0".
- **Beneficios después del cierre**: la mayoría de los KR se cumplen después del proyecto; durante el proyecto se miden indicadores adelantados (adopción, uso) y el resto pasa al plan de revisión de beneficios.
- **Varios proyectos contribuyen al mismo OKR**: el OKR es del programa o de la organización; el proyecto declara su contribución y no se atribuye todo el resultado.
- **Meta inalcanzable detectada**: no bajar la meta sin decisión; registrar el pronóstico y, si afecta la tolerancia de beneficios, escalar.
