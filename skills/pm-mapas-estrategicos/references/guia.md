# Guía de mapas estratégicos · Strategic maps guide

> EN: How pm-method uses Wardley maps and customer journey maps: what each one is for, how to place components and
> emotions with evidence, how to read a map for risks, delivery approach and make-or-buy, how maps link to PRINCE2
> products, and which health checks (MAP family) keep them honest. Written in the package's own words.

## §1. Cuándo y para qué
Un mapa vale lo que la decisión que informa. Antes de dibujar, escribir la **pregunta estratégica** (`pregunta_estrategica`):
- "¿Qué construimos, qué compramos y con qué enfoque se entrega cada parte?" → mapa de Wardley de los entregables.
- "¿Dónde sufre hoy la persona y qué arreglo cambia el resultado del business case?" → recorrido del cliente.
- "¿El servicio que prometemos se puede cumplir con lo que hay detrás?" → recorrido con carriles de service blueprint.

| Momento | Mapa | Producto PRINCE2 que alimenta |
|---|---|---|
| Puesta en marcha (SU), con las opciones | Wardley de los entregables; recorrido actual | business case esquemático (opciones), enfoque del proyecto, supuestos |
| Iniciación (IP) | Wardley con decisiones e inercias; recorrido con dolores tratados | business case, estrategia de adquisiciones, registro de riesgos, descripción del producto del proyecto |
| Límite de etapa (SB) | el mismo mapa, revisado | informe de fin de etapa, plan de la etapa siguiente |

No conviene dibujar si nadie va a decidir con el mapa, si no hay fuentes para ubicar nada (primero entrevistar o medir) o si
el pedido es un diagrama de gestión (organigrama, WBS, Gantt): eso es `pm-visuales`.

## §2. Mapa de Wardley
La técnica la propuso Simon Wardley. Se citan aquí sus ideas centrales, explicadas con palabras del paquete.

**Cadena de valor.** Se parte de un **ancla**: quien usa el servicio y la necesidad que lo mueve. Debajo, lo que hace falta
para cubrir esa necesidad, y debajo de cada cosa, lo que esa cosa necesita. Un enlace `de → a` significa "de depende de a".
La cadena no tiene ciclos.

**Eje vertical: visibilidad.** Arriba, lo que la persona ve y valora directamente; abajo, lo que nadie nota mientras funcione
(hosting, mensajería, energía). Valores de 0 a 1.

**Eje horizontal: evolución.** Cuán conocido, difundido y estandarizado está el componente en el mercado, no cuán
importante es para nosotros ni cuándo se entrega. Cuatro etapas:

| Etapa (`etapa`) | Rango (convención del paquete) | Señales observables para ubicarlo |
|---|---|---|
| `genesis` | 0,00–0,25 | se inventa; nadie sabe bien cómo se hace; resultados inciertos; pocos casos |
| `a-medida` | 0,25–0,50 | se construye a medida en cada organización; empieza a entenderse; diferencia |
| `producto` | 0,50–0,75 | hay productos o servicios en alquiler que compiten por funciones; se configura |
| `commodity` | 0,75–1,00 | estándar, intercambiable, se compra por volumen o se usa como servicio; se espera que funcione |

Los cortes en cuartos iguales son una convención del paquete para que la tabla coincida con las columnas que dibuja
Mermaid; no son una medición. Cerca de un borde (±0,05) se acepta cualquiera de las dos etapas.

**Evidencia por ubicación.** Cada componente lleva `evidencia`: una o dos frases con la fuente que justifica la etapa
(oferta de mercado conocida, contrato vigente, resultado de un experimento `S-…`, lección `L-…`, decisión de arquitectura
`AD-…`, cita `archivo:línea`). Sin fuente, la posición es un supuesto: se deja `[por confirmar]` y la sanidad lo señala
(MAP-04). Errores habituales: ubicar por importancia, ubicar por fecha de entrega, ubicar lo "nuestro" siempre a la
izquierda.

**Movimiento.** Los componentes evolucionan hacia la derecha con el tiempo, empujados por la competencia y la difusión.
Un `movimiento` (`evolve`) marca hacia dónde se espera que vaya un componente y por qué; nunca hacia la izquierda.

**Inercia.** Resistencia a evolucionar: un sistema legado, un contrato largo, una costumbre, una inversión hecha.
`inercia: true` en el componente. Toda inercia es un riesgo para el proyecto y se registra (MAP-02).

**Decisiones.** `construir` (build), `comprar` (buy), `tercerizar` (outsource) o `mercado` (market). Regla general: se
construye lo que diferencia y todavía está a la izquierda; se compra o terceriza lo que ya es producto o commodity.
Construir algo que el mercado ya ofrece como producto o commodity exige una decisión registrada que lo justifique
(MAP-01).

**Tamaño.** De 8 a 15 componentes. Si hacen falta más, dividir en submapas por ancla o por capacidad.

## §3. Cómo leer el mapa para la gestión
| Lectura | Qué buscar | A dónde va |
|---|---|---|
| Enfoque de entrega | génesis y a medida → adaptativo; producto → híbrido; commodity → predictivo o compra; lo que depende de un componente con inercia → predictivo con hitos de validación | contraste con los nueve criterios (`pm-mandato-y-brief`); la decisión se toma con los criterios y se registra |
| Hacer o comprar | componentes en producto o commodity marcados construir; componentes a medida que podrían comprarse | `pm-adquisiciones` (análisis con costos totales y riesgos); para comparar construir, comprar y tercerizar, la matriz de `pm-direccion-decisiones` con `--criterios hacer-o-comprar` |
| Riesgos | inercias, dependencias de un único proveedor, componentes en génesis con contrato a precio fijo o enfoque predictivo | `pm-riesgos` (causa → evento → efecto, propietario) |
| Opciones del business case | qué cambia entre opciones: qué se construye en cada una y qué se compra | `pm-caso-de-negocio` (opciones 0/1/2, VAN) |
| Requisitos de calidad | componentes muy visibles para el usuario: expectativas de calidad del cliente | descripción del producto del proyecto (`pm-planificacion-por-productos`) |

`mapas.py wardley render` agrega una columna "Lectura sugerida" con esta heurística; es un punto de partida para la conversación,
no una regla de PRINCE2 ni un sustituto de los criterios del enfoque.

**Decisiones que leen el mapa** (`pm-direccion-decisiones`, guía §13.11 de esa skill). Una hoja de decisión nombra un
componente o un paso como `<mapa>:<id>` (`entregables:C2`): `decision.py expediente` trae, con su cita `archivo#id`, lo
que el mapa dice de él (etapa, evolución, decisión, inercia, evidencia, lo que depende de él y el movimiento previsto;
o emoción con su fuente, dolor, clase Kano, KPI y persona), y también los componentes y pasos que citan en `refs` un id
de la decisión. Es contexto, no criterio: la evolución describe el componente, no las opciones. Para el hacer o comprar,
`decision.py matriz <ID> --proponer --tipo adquisicion --criterios hacer-o-comprar` usa seis criterios (diferenciación,
costo total, tiempo hasta disponible, dependencia del proveedor, capacidad interna y riesgo de construir algo que va a
volverse commodity). Al elegir (`matriz <ID> --elegir … --por …`), la decisión registrada queda citada en el elemento
nombrado con `mapas.py vincular` (cierra MAP-01 o, en un paso, MAP-03); la columna `decision` del componente no cambia:
si la elección la contradice, se corrige en el JSON con la persona y se regenera la vista.

## §4. Recorrido del cliente (customer journey map)
Describe cómo una persona concreta intenta lograr algo, paso a paso, y qué siente en cada paso.

- **Persona y trabajo**: `persona` (arquetipo construido con datos del proyecto, no una persona real), `trabajo` (lo que
  quiere lograr, más allá de la función), `disparador` (qué la pone en marcha) y `exito` (cómo sabe que terminó bien).
  Si el proyecto registra personas de usuario (`personas.csv`, `pm-interesados` guía §13), `recorrido semilla --persona
  PU-###` toma de la persona el nombre, la descripción, el objetivo (`trabajo`) y el contexto (`disparador`) y deja
  `persona_id` en el mapa; con `personas.csv`, un recorrido cuya persona no está registrada (ni por `persona_id` ni por su
  nombre) da STK-16.
- **Escenario**: `actual` (as-is) primero. El recorrido `futuro` (to-be) se dibuja después, con las oportunidades.
- **Etapas y pasos**: etapas con nombre propio del servicio; en cada paso **una sola acción** en una unidad de tiempo
  (validar rechaza "elige y paga", "→" o dos oraciones). Hasta 15 pasos por mapa.
- **Punto de contacto** (`punto_contacto`, `canal`): dónde ocurre la interacción (call center, sitio, ventanilla, correo).
- **Emoción** (`emocion`): entero de −2 (muy mal) a +2 (muy bien), con `fuente_emocion`: cita de entrevista,
  métrica, observación o "supuesto declarado: …". La curva se lee como acumulada: un paso malo pesa en los siguientes.
  `emocion_objetivo` (opcional) dibuja la línea esperada si se implementan las oportunidades.
- **Dolor** (`dolor`, `tipo_causa`): qué falla y por qué: `rendimiento`, `usabilidad`, `propuesta-valor`,
  `dependencia-externa`, `proceso-interno`, `otro`.
- **Oportunidad** (`oportunidad`, `kano`): el arreglo y su clase en el modelo de Noriaki Kano: `obligatorio` (si falta,
  molesta; si está, no se nota), `desempeno` (más es mejor), `atractivo` (sorprende), `indiferente`.
- **Tratamiento** (`refs`): el id que trata el dolor: requisito (`REQ-…`, `FR-…`, `NFR-…`), historia del backlog (su
  id en la fachada de especificación), riesgo `R-…`, issue `I-…`, decisión `D-…`, supuesto `S-…`, cambio `C-…` o
  revisión de calidad `Q-…`. El id tiene que existir. Sin tratamiento, MAP-03.
- **KPI** (`kpi`, `contrapesos`): métricas que miden el recorrido (con BMAD, `SM-n` y sus contrapesos `SM-Cn`).
- **Variantes** (`variantes`): casos límite o caminos alternativos que no entran en la curva principal.

Para validar el mapa conviene revisarlo con dos o tres personas del perfil y con quien atiende el servicio.

## §5. Carriles internos (service blueprint liviano)
El service blueprint lo propuso G. Lynn Shostack para diseñar servicios. El paquete usa tres carriles por paso:
`frontstage` (lo que la persona ve del servicio), `backstage` (lo que hace el personal sin que la persona lo vea) y
`soporte` (sistemas y procesos que sostienen a los otros dos). En la vista HTML, una línea punteada separa lo visible de
lo invisible. Se busca dónde el frente promete algo que el fondo no puede cumplir (un plazo sin proceso que lo sostenga,
un dato que nadie actualiza): eso es un riesgo o un requisito.

Con BMAD, `recorrido semilla --uj UJ-2 --backstage UJ-3` deja los pasos del recorrido interno en `pendiente_alinear`;
la persona los asigna al paso que corresponde y borra la lista.

## §6. Vínculos con PRINCE2
| Producto o práctica | Qué toma del mapa |
|---|---|
| Business case (opciones, beneficios) | qué se construye y qué se compra en cada opción; dolores que explican cada beneficio |
| Enfoque del proyecto / de entrega | contraste por componente con los nueve criterios; dependencias con inercia |
| Riesgo | inercias, dependencias externas, dolores de causa externa |
| Requisitos y descripción del producto del proyecto | oportunidades como requisitos; expectativas de calidad de lo más visible |
| Beneficios | KPI del recorrido como indicadores adelantados del beneficio |
| Estrategia comercial (adquisiciones) | componentes a comprar o tercerizar |

El mapa nunca aprueba nada: la junta decide sobre los productos PRINCE2, que citan el mapa como evidencia.

## §7. Con BMAD y sin BMAD
- **Con BMAD** (solo lectura): `bmad.py recorridos [--id UJ-n] --json` da los campos del recorrido (persona, estado de
  entrada, recorrido, clímax, resolución, caso límite), los FR que dicen "Realiza UJ-n" (o los de su sección) y las
  métricas SM-n que validan esos FR, con sus contrapesos. `bmad.py capacidades --json` da el mapa de capacidades
  (FR → módulo → AD-n), las decisiones diferidas (candidatas a comprar o tercerizar) y el stack. `mapas.py … semilla` usa
  ambos. Los ids se verifican con la fachada `especificacion.py`; un id retirado de la especificación dispara MAP-05.
- **Sin BMAD**: semilla desde `--componentes`/`--anclas`, los productos de `wbs.csv` o los requisitos de la fachada;
  la sección `insumos` lista supuestos, riesgos, decisiones y lecciones para citarlos como evidencia. Para el recorrido,
  `--persona` y `--etapas`, con las transcripciones de `pm-reuniones` como fuente de emociones y dolores.

## §8. Controles y validación
**`validar`** (errores que impiden generar la vista): esquema, pregunta estratégica, ids duplicados o vacíos, nombres
repetidos, coordenadas fuera de 0–1, etapa incoherente con la evolución, decisión desconocida, enlaces a ids inexistentes,
ciclos, movimientos hacia la izquierda; en el recorrido, persona, emoción fuera de −2…+2 o sin completar, más de una acción
por paso, causa o clase Kano desconocidas. **Avisos**: sin anclas, más de 15 componentes o pasos, huérfanos, rótulos casi
superpuestos (distancia < 0,06), dolor con emoción positiva.

**Sanidad, familia MAP (solo AVISO):**
| Código | Qué detecta | Cómo se corrige |
|---|---|---|
| MAP-00 | mapa ilegible o con errores de validación | `mapas.py … validar` |
| MAP-01 | componente en producto o commodity marcado `construir` sin decisión `D-…` citada | registrar la decisión (con la matriz de hacer o comprar queda citada al elegir) o cambiar a comprar o tercerizar |
| MAP-02 | componente con inercia sin riesgo abierto `R-…` citado | registrar el riesgo (pm-riesgos) y vincularlo |
| MAP-03 | dolor sin tratamiento | requisito, historia, riesgo, issue, cambio, decisión, supuesto o revisión de calidad, y `vincular` |
| MAP-04 | posición o emoción sin evidencia | agregar la fuente o declararla como supuesto |
| MAP-05 | id citado que no existe (registros o especificación) | corregir la referencia o crear el elemento |

## §9. Formatos de salida
- **Mermaid `wardley-beta`** (Mermaid 11.14 o posterior; diagrama en beta: la sintaxis puede cambiar). El script pone
  todos los nombres entre comillas: sin comillas fallan los que tienen tildes, eñe o una palabra que empieza por dígito.
  El título va sin comillas. `validar_mermaid.py` controla esas reglas.
- **Mermaid `journey`**: puntaje entero 1–5 = emoción + 3; sin `:` en el texto de la tarea (el script lo reemplaza).
- **OWM** (`.owm`): texto para OnlineWardleyMaps y sus extensiones: `title`, `evolution`, `anchor`, `component … [v, e]`
  con `(build)`, `(buy)`, `(outsource)` o `(market)`, `inertia`, enlaces `A->B`, `evolve`, `note`. Formato portátil: no
  depende de ninguna herramienta instalada. Un componente con decisión e inercia sale como `(build) inertia`; la
  documentación de OWM muestra cada marca por separado, no combinadas [verificar en OWM].
- **HTML** (`recorrido-<slug>.html`): autocontenido, sin red ni scripts, todo el texto escapado; carriles, curva de
  emoción en SVG, zona negativa sombreada, línea esperada punteada, modo oscuro y A4 apaisado al imprimir.
- **PNG**: con `mmdc` instalado (`--png auto` lo intenta; `si` lo exige; `no` lo omite). Las guías y presentaciones usan
  el PNG porque no todos los visores de Markdown dibujan `wardley-beta`.
- **Tablero de mapas** (`mapas.py --proyecto <dir> tablero [--mapas S1,S2] [--insertar TABLERO.html] [--salida F.html]
  [--json]`): lleva el caso hasta la representación gráfica sin depender de `mmdc`. Dibuja cada mapa válido en SVG propio
  (los inválidos se listan sin dibujar):
  - Wardley: ejes, etapas en cuartos, enlaces, anclas, componentes coloreados por decisión (construir, comprar,
    tercerizar, mercado o sin decisión), barra de inercia con el riesgo abierto que la trata («inercia → R-001») o
    «inercia sin riesgo», movimientos punteados y halo ámbar en los componentes con avisos MAP; los rótulos buscan un
    lugar libre para no pisarse.
  - Recorrido: bandas por etapa, curva de emoción actual y esperada, zona negativa, paso y acción, y debajo de cada
    dolor su tratamiento o «sin tratamiento».
  - Debajo de cada gráfico, una tabla (componentes con decisión, inercia → riesgo y refs; dolores con su tratamiento);
    arriba, los **avisos MAP vigentes** (los mismos de `controles`); al final, la tabla **Vínculos citados**: cada id de
    registro (riesgo, issue, cambio, decisión, supuesto, lección, revisión de calidad, acción) y cada tratamiento de un
    dolor, con descripción, estado y responsable. Los ids son enlaces a esa tabla; los de la especificación que solo son
    evidencia quedan como texto, y los inexistentes, tachados (MAP-05).
  - Salida: `02-planificacion/visuales/tablero-mapas.html` (autocontenido, sin scripts ni red, todo el texto escapado,
    claro y oscuro, dos columnas desde ~1.250 px y una en teléfono, con desplazamiento horizontal dentro del mapa). Con
    `--insertar` reemplaza la sección entre `<!-- pm-mapas:inicio … -->` y `<!-- pm-mapas:fin -->` del tablero de avance
    de `pm-visuales` (`templates/tablero-avance.html`); sin mapas válidos la deja vacía y el tablero no muestra la
    sección. Es una vista derivada: se regenera, no se edita; no requiere registrar un artefacto nuevo.

## §10. Casos borde
- Dos componentes con el mismo nombre: Mermaid los fundiría en uno; `validar` lo rechaza.
- Un mapa aprobado se regenera: el estado, la versión y la aprobación del frontmatter se conservan.
- Componente sin enlaces: aviso de huérfano; o falta la dependencia o sobra el componente.
- Recorrido con un caso límite importante: dibujarlo como recorrido aparte, no mezclarlo en la curva principal.
- Sin `mmdc`: quedan el bloque Mermaid, el OWM, el HTML y el tablero de mapas (SVG propio); el PNG se genera donde haya
  `mmdc`.
- Tablero de avance sin los marcadores `pm-mapas` (armado con otra plantilla): `tablero --insertar` lo rechaza; se
  regenera desde `pm-visuales/templates/tablero-avance.html` o se usa la vista `tablero-mapas.html`.
- Proyecto en inglés: rótulos de etapa y mensajes en inglés (`estado.json.idioma = en`).

## §11. Fuentes
- Simon Wardley, mapas de Wardley (concepto y vocabulario: ancla, cadena de valor, evolución, inercia).
- Noriaki Kano, modelo de clasificación de atributos (citado también en `pm-knowledge`, PMBOK 8 §3.4 y PRINCE2 7, práctica de calidad).
- G. Lynn Shostack, service blueprint.
- Documentación de Mermaid (`wardley-beta`, `journey`) y del lenguaje de OnlineWardleyMaps.
Ningún texto de estas fuentes se copia: el contenido de esta guía está redactado para el paquete.
