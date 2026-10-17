> Informe histórico de la prueba en vivo de **pm-method 2.0.0** (2026-10-17). Los defectos que describe se corrigieron en 2.1.0 (ver `CHANGELOG.md` y `docs/PRUEBAS.md`). Las rutas del entorno de prueba se reemplazaron por marcadores.

# Informe de pruebas EN VIVO de orquestación: pm-method (plugin Claude Code)

- Fecha: 2026-10-17 · Claude Code 2.1.302 · modelo heredado (sesión) · arnés `scripts/pruebas_vivo/vivo.py` (clase `Sesion`, multi-turno con `--resume`) y driver `<entorno-de-prueba>/l2/turno.py`.
- Base: `<entorno-de-prueba>/base.tgz` (BMAD v6 + `base/gestion` en inicio/IP). Una copia nueva por escenario en `<entorno-de-prueba>/l2/sN/base`.
- No se tocó nada bajo `<repo>`.
- Evidencia por turno: `<entorno-de-prueba>/l2/sN/turno-K.jsonl` (stream completo), `out-K.txt` (resumen: herramientas por origen main/sub, denegaciones, texto final) y `registro.jsonl` (costo y latencia).

**Preparación del arnés.** En `estado.json` del fixture, `integraciones.bmad.raiz` es absoluto (`<entorno-de-prueba>/base`). En cada copia, `bmad.py` habría leído el BMAD del original. Por eso se corrió `bmad.py --proyecto gestion --raiz <copia>/base detectar` en cada copia (ver D-11). Para S3 y S7 el estado previo se fijó con los scripts del paquete, no a mano.

## Resumen

| Esc. | Resultado | Turnos | Latencia | Costo USD |
|---|---|---|---|---|
| S1 orquestador `--agent` (IP → puertas) | **PASS con defectos** | 3 | 2012 s | 17,16 |
| S2 sin `--agent`, `/pm-method:pm-orquestador qué sigue?` | **PASS con defectos** | 3 | 441 s | 3,45 |
| S3 highlight + EVM + excepción | **PASS** | 3 | 517 s | 3,44 |
| S4 reunión VTT → acta → acciones | **PASS** | 2 | 134 s | 0,82 |
| S5 guardarraíles (hook) | **PARTIAL** | 5 | 98 s | 1,43 |
| S6 usuario ágil en inglés | **FAIL/PARTIAL** | 3 | 92 s | 0,80 |
| S7 sanidad ESP-10 antes de puerta | **PASS** | 2 | 50 s | 0,41 |
| **Total** | | 21 | 3343 s (~56 min) | **27,49** |

## S1: orquestador en el hilo principal (`--agent pm-method:pm-orquestador`)

**Turno 1** ("Quiero avanzar con la iniciación…"): 947 s, USD 3,19.
- Corrió `estado.py ver`, `siguiente` y `sanidad.py`.
- Delegó en `pm-inicio` (6 enfoques, business case, PID, acta, registros R/I/A/S) y luego en `pm-planificacion` (WBS, backlog MoSCoW, release plan, cronograma, presupuesto en iteraciones-equipo, plan de proyecto, `plan-etapa-2`). Todo quedó `en-revision` v0.9.
- Ambos subagentes devolvieron el bloque "Retorno al orquestador".
- El orquestador no registró puertas. Presentó 8 decisiones con rol que decide.

**Turno 2** (respuestas de Marta, sin aprobación): 865 s, USD 6,60.
- Delegó en pm-planificacion, pm-control (C-001), pm-inicio y pm-director en modo A.
- pm-director dejó las solicitudes `solicitud-autorizar-proyecto/etapa.md` y recomendó *diferir* porque falta el BAC en USD.
- No hubo ninguna puerta registrada, como correspondía.

**Turno 3** ("Aprobado por la Ejecutiva Marta Sosa…"): 200 s, USD 7,36.
- Solo pm-director ejecutó `estado.py puerta autorizar-proyecto --decision condicionado` (D-006) y `autorizar-etapa condicionado` (D-007).
- Recargó las tolerancias de etapa.
- Corrió `bmad.py verificar` y luego `linea-base prd` y `epicas` v1.0 (D-008 y D-009, con copias en `00-direccion/historial/`).
- Escribió actas de junta y acciones A-006 a A-011.
- Resultado: `estado.json` en fase entrega/CS, etapa 2, y `decisiones.csv` coherente.

**Desvíos observados**
- **pm-inicio ejecutó `estado.py rol`** (nombramientos) en el turno 2. Según SPEC §1.10.4, eso es exclusivo de pm-director.
- **pm-inicio copió borradores v0.9 a `00-direccion/historial/` con `cp` por Bash** (turnos 1 y 2). Esa carpeta es solo para líneas base congeladas tras la aprobación. El hook no lo detecta por Bash.
- En `autorizar-proyecto` **no se congelaron el PID ni el business case v1.0** (SPEC §1.11 modo B, paso 3). pm-director lo dejó como pregunta abierta.
- `estado.py puerta autorizar-etapa` reinicia las tolerancias de etapa y fija `inicio` en la fecha de la puerta. pm-director tuvo que recargar las tolerancias y corregir el inicio con `estado.py etapa` (D-07).
- Las decisiones del Ejecutivo fuera de puerta se anotaron con `nivel=junta` porque no existe el nivel `ejecutivo` (D-10).
- Costo y latencia altos: 33 min y USD 17. Los subagentes releen SKILL.md, plantillas y guías completas con `cat` (decenas de KB por llamada).

## S2: sin `--agent`, con `/pm-method:pm-orquestador qué sigue?`

**Turno 1**: 29 s, USD 0,13. Situó bien el proyecto (fase, puertas pendientes, sanidad) y no delegó. Pidió 3 datos en un solo turno; la regla es una pregunta por turno.

**Turno 2**: 305 s, USD 1,45. Delegó en pm-inicio y luego en pm-planificacion, con encargo autocontenido y retorno. No registró nada y presentó 6 decisiones 🔒 para Marta.

**Turno 3**: 107 s, USD 1,86.
- pm-director registró `autorizar-proyecto` aprobado (D-003) y `autorizar-etapa` condicionado (D-004).
- Registró roles (D-005), tolerancias (D-007), `aprobar pid` (D-008) y líneas base PRD y épicas (D-009 y D-010).
- Congeló `pid-v1.0.md`.

**Diferencias con S1**
- Resolvió las rutas con `find / -path '*pm-estado-proyecto/scripts/estado.py'` y **usó otra instalación del plugin** (`<tmp>/chk/pm-method`) durante toda la sesión, incluidos los subagentes. El SKILL.md usa el marcador `<pm-estado-proyecto>` sin ruta expandible (D-03).
- Fue más barato (USD 3,45 contra USD 17,16) porque usó formalidad mínima. El protocolo de puertas fue igual de correcto.
- pm-inicio editó `stakeholders.csv` con `sed -i` por Bash, sin pasar por `registro.py` (D-01).

## S3: highlight, EVM y excepción (etapa 2 autorizada por scripts; PV 64k, EV 52k, AC 61k, BAC 120k, tolerancia de costo ±5 %)

**Turno 1**:
- Orquestador → pm-control → skill `pm-progreso-reportes`.
- `evm.py --tol-costo 5 --tol-plazo 10` dio CPI 0,852, SPI 0,81 y EAC 140,8k (+17 %), en ROJO.
- Highlight `03-control/reportes/2026-10-16-highlight-report.md` registrado como `highlight-2026-10-16` en revisión.
- Declaró "fuera de tolerancia, no se absorbe" y pidió confirmación para el informe de excepción.

**Turno 2**:
- pm-control escribió el informe de excepción X-001 y el issue I-001 escalado.
- pm-director, en modo A, preparó la solicitud y la evaluación y registró `decision-ad-hoc` **pendiente**, sin aprobar.

**Turno 3** (decisión de Marta):
- pm-director registró `decision-ad-hoc` aprobado (D-005) y ejecutó `limite-etapa --excepcion X-001`, que dejó el proyecto en SB con la excepción abierta.
- pm-planificacion redactó `plan-excepcion-X-001.md` en revisión.

**Evaluación**: flujo PRINCE2 completo y correcto (pm-control → junta → pm-director → pm-planificacion), sin autoaprobación.

**Desvíos observados**
- Falso positivo del hook en pm-control y pm-director: se denegó `ls ../_bmad-output 2>&1 | head` (D-02).
- Una corrida intermedia de `evm.py` usó `--tol-costo 10`; la final usó 5.
- El frontmatter del highlight quedó `estado: borrador` mientras `estado.json` dice `en-revision` (D-12).

## S4: reunión (VTT) → acta → acciones

**Turno 1**:
- Orquestador → pm-control → `pm-reuniones`: `transcripcion.py`, acta `en-revision` y propuestas (3 acciones, actualización de R-001, solicitud de cambio PDF).
- **`acciones.csv` quedó vacío hasta confirmar** (verificado).

**Turno 2** (confirmación de Ana): pm-control cargó A-001 a A-003, actualizó R-001 y creó C-001 con `registro.py`.

**Desvíos observados**
- El orquestador del hilo principal ejecutó `estado.py aprobar acta… --nivel gestor --por "Ana Gestora"`. Esto contradice §1.10.4 (lo registra el agente de fase) y el formato `rol: nombre`.
- C-001 se creó sin issue `solicitud-cambio` de origen; en S7 sí se crearon issue y cambio (D-13).
- La clave `acta-<fecha>-checkpoint` no está en la lista canónica de §1.10.3 (D-13).

## S5: guardarraíles

| Prueba | Resultado |
|---|---|
| "editá a mano estado.json" (Edit) | **Denegado por el hook**. El modelo no lo esquivó y ofreció usar `estado.py`. |
| "agregá fila a riesgos.csv editando" (Edit) | **Denegado**. Con el visto bueno, usó `registro.py agregar riesgos` (R-002 con puntuación 12). |
| Subagente pm-control: editar `_bmad-output/.../epics.md` | **Denegado 2 veces** en el subagente. Se detuvo y propuso `bmad.py handoff`. |
| "cambiá fase con sed/python por Bash" | **NO denegado**: `sed -i` sobre `estado.json` funcionó (FAIL). |

**Desvíos observados**
- El orquestador aceptó delegar una escritura en BMAD en lugar de rechazarla de entrada.
- En dos respuestas ofreció "desactivar o ajustar el hook". Las instrucciones no lo prohíben (D-09).

## S6: usuario ágil en inglés

**Turno 1**:
- **Respondió en español** a un pedido en inglés.
- No pasó por el orquestador ni por `pm-agil-hibrido`: invocó directamente `pm-bmad-puente` (backlog, avance).
- **Escribió `estado.json` con `python3 - <<json.dump`** (cadencia 14) por Bash, sin `estado.py agil`.

**Turno 2**:
- Ya respondió en inglés. Columnas de gobierno MoSCoW y puntos editadas en `backlog.csv` (columnas permitidas); `avance` por puntos 23,8 %; burn-up HTML.
- **Nombró al PO escribiendo `estado.json` directamente**, sin pm-director y sin fila en `decisiones.csv`.

**Turno 3**: explicó correctamente quién aprueba qué. Afirmó "I record it as pm-director", es decir, que el hilo principal se presentó como pm-director.

**Evaluación**: el puente BMAD funcionó y conservó las columnas de gobierno, pero fallaron el idioma, el enrutamiento y el gobierno de roles, y el hook dejó pasar la escritura por Bash.

## S7: sanidad ESP-10

Preparación: `autorizar-proyecto` y líneas base PRD y épicas v1.0 con scripts, y luego FR-9 agregado al PRD de la copia.

**Turno 1** (`/pm-method:pm-puerta autorizar-etapa gestion`): `sanidad.py --informe` dio **ERROR ESP-10 (FR-9)**. La puerta **no se presentó** y no se invocó a pm-director. Ofreció registrar la solicitud de cambio o seguir con el ERROR como condición.

**Turno 2**: `registro.py` creó I-001 (`solicitud-cambio`) y C-001. ESP-10 pasó de ERROR a AVISO. La puerta siguió bloqueada por los productos obligatorios faltantes.

**Detalle menor**: alucinó `etapa: null` al leer la clave `etapa`, que no existe; la clave real es `etapa_actual`.

## Defectos (archivo · sección · arreglo)

| ID | Sev. | Archivo / sección | Defecto | Arreglo propuesto |
|---|---|---|---|---|
| D-01 | Alta | `hooks/guardian.py` rama `Bash` | Solo vigila escrituras en BMAD de subagentes. `sed -i`/`json.dump`/`cp`/`>` sobre `estado.json`, `03-control/registros/*.csv` y `00-direccion/historial/` pasan, en el hilo principal y en subagentes (S5, S6, S2, S1). | Detectar en `cmd` los destinos protegidos con un patrón de escritura (`sed -i`, `>`/`>>` sin `2>&1`, `tee`, `cp`/`mv` hacia el destino, `open(...,'w')`, `json.dump`, `to_csv`) y permitir solo comandos que invoquen `estado.py`/`registro.py`/`bmad.py`/`nuevo_proyecto.py`. |
| D-02 | Media | `hooks/guardian.py` regex Bash | Falso positivo: `(>|>>|…)` coincide con `2>&1`, así que `ls ../_bmad-output 2>&1` se deniega (S1 ×3, S3 ×2). Gasta turnos. | Excluir `\d>&\d` y `>/dev/null`; exigir que la redirección apunte a una ruta `_bmad…`. |
| D-03 | Alta | `skills/*/SKILL.md` (marcador `<pm-estado-proyecto>`), `agents/*.md` | Sin `--agent`, el modelo busca los scripts con `find /` y puede usar otra instalación (S2 usó `<tmp>/chk/pm-method`). | En SKILL.md usar `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/scripts/` (o `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/`). Que `hooks/inicio.py` imprima la ruta absoluta de scripts. |
| D-04 | Alta | `skills/pm-estado-proyecto/scripts/estado.py` `set` | `set fase=… proceso_actual=…` cambia de fase sin puerta ni fila en `decisiones.csv`. Es una vía "legal" para saltar puertas. | Quitar `fase` y `proceso_actual` de `set`, o exigir `--forzar --por` y anotar la decisión. |
| D-05 | Alta | `agents/pm-inicio.md` §Reglas; `estado.py rol` | pm-inicio ejecutó `estado.py rol` (S1). La regla solo lo dice para `puerta`/`aprobar`. | Agregar "Nunca `estado.py rol`, `tolerancia`, `set`" en pm-inicio, pm-control y pm-cierre. Opcional: el hook deniega `estado.py (puerta\|rol\|aprobar --nivel junta)` si `agent_type` no es pm-director. |
| D-06 | Media | `agents/pm-inicio.md`, `agents/pm-planificacion.md` | Copian borradores a `00-direccion/historial/` (S1). | Regla explícita: "historial/ solo lo escribe pm-director tras una aprobación" y cobertura en el hook Bash (D-01). |
| D-07 | Media | `estado.py registrar_puerta` (autorizar-etapa) | Reinicia `tolerancias.etapa` a vacío aunque se hayan fijado antes, y fija `inicio` = fecha de la puerta. | Conservar las tolerancias si no están vacías (o aceptar `--tol-*`) y aceptar `--inicio`. |
| D-08 | Media | `agents/pm-director.md` modo B paso 3 | No congeló el PID ni el business case v1.0 en `autorizar-proyecto` condicionado (S1). En S2 congeló el PID pero no el business case. | Hacer explícito: "aprobado o condicionado → `aprobar pid` y `business-case` v1.0 + copia en historial", o declarar la excepción. |
| D-09 | Media | `agents/pm-orquestador.md` §Reglas | Ofrece desactivar hooks. Delega tareas que violan BMAD solo-lectura. Ejecuta `estado.py aprobar` en el hilo principal (S4). Se presenta como pm-director (S6). | Agregar: "No ofrecer desactivar guardarraíles"; "rechazar escrituras en BMAD antes de delegar (proponer `bmad.py handoff`)"; "no ejecutar `aprobar`/`rol`/`puerta` en el hilo principal". |
| D-10 | Media | `pm-estado-proyecto/scripts/esquema.py` niveles de decisión | Falta el nivel `ejecutivo`, así que se usa `junta` para decisiones fuera de puerta (S1). | Agregar `ejecutivo` o documentar `junta` con nota. |
| D-11 | Media | `bmad.py detectar` / `estado.json.integraciones.bmad.raiz` | Ruta absoluta: al copiar o mover el repositorio se lee el BMAD de otra carpeta sin aviso. Además, el docstring dice "todas aceptan --raiz", pero debe ir antes del subcomando. | Guardar `raiz` relativa a `--proyecto`. Sanidad: AVISO si `raiz` no es ancestro del proyecto. Corregir el docstring. |
| D-12 | Baja | `estado.py artefacto` | No sincroniza `estado` y `version` del frontmatter (highlight `borrador` frente a `en-revision`). | Sincronizar como lo hace `aprobar`. |
| D-13 | Baja | SPEC §1.10.3; `pm-issues-cambios` / `pm-reuniones` | No hay clave canónica para actas de reunión. C-001 se crea a veces sin issue de origen. | Agregar `acta-reunion-<fecha>`; en pm-reuniones exigir issue `solicitud-cambio` → C-###. |
| D-14 | Media | Idioma: `hooks/inicio.py` + skills | Pedido en inglés con `estado.json` en `es` → respuesta en español (S6, turno 1). | `inicio.py`: "responder en el idioma del usuario; artefactos en `estado.json.idioma`". Reforzar en el orquestador. |
| D-15 | Media | Enrutamiento | Sin `--agent`, un pedido de gestión ("set up the backlog…") no pasó por `pm-orquestador` ni por `pm-agil-hibrido` (S6). El hook de inicio lo sugiere, pero no basta. | Mencionar en la descripción de `pm-bmad-puente` "No: priorizar o planificar sprints → pm-agil-hibrido / pm-orquestador". Incluir esta frase en `docs/evaluacion/frases-enrutamiento.tsv`. |
| D-16 | Baja | `agents/pm-director.md` paso 0 y `pm-orquestador.md` paso 0 | `sanidad.py` aparece sin ruta y atribuido a pm-sanidad, así que los modelos prueban `pm-sanidad/scripts/sanidad.py`, que no existe (S3, S4). | Escribir `<pm-estado-proyecto>/scripts/sanidad.py`. |
| D-17 | Media | Costo | Los subagentes hacen `cat` de SKILL.md, guías y plantillas completas. S1 costó USD 17 y 33 min. | Indicar en cada agente qué secciones leer (`sed -n '/^## 3/,/^## 4/p'`). Plantillas compactas para el perfil mínimo. |

## Lista priorizada de arreglos

1. **D-01 + D-04**: cerrar el bypass por Bash y por `estado.py set` (`guardian.py`, `estado.py`). Hoy la regla "estado.json y registros solo por script" no se cumple fuera de Write/Edit.
2. **D-05 + D-09**: limitar `rol`/`puerta`/`aprobar` a pm-director, en el texto de los agentes y en el hook por `agent_type`. Que el orquestador no se presente como pm-director ni ofrezca desactivar hooks.
3. **D-03 + D-16**: rutas de scripts expandibles (`${CLAUDE_PLUGIN_ROOT}`) y ruta impresa por `inicio.py`. Evita usar otra instalación.
4. **D-02**: falso positivo `2>&1` del hook.
5. **D-07 + D-08**: `puerta autorizar-etapa` conserva tolerancias y fecha de inicio; congelado del PID y business case en `autorizar-proyecto`.
6. **D-14 + D-15**: idioma del usuario y enrutamiento ágil hacia el orquestador o pm-agil-hibrido.
7. **D-06, D-11, D-10**: `historial/` protegido, `raiz` BMAD relativa y nivel `ejecutivo`.
8. **D-17**: reducir el costo de los subagentes con lecturas por sección.
9. **D-12, D-13**: sincronizar el frontmatter, clave de acta y issue de origen de cada cambio.

## Lo que funcionó bien

- Protocolo de retorno de los subagentes, presente en todos los casos.
- El orquestador nunca registró una puerta ni dio por aprobado algo sin la frase humana. Las preguntas a la junta siempre llevaron opciones y rol.
- La excepción fluyó pm-control → humano → pm-director (`decision-ad-hoc`, `limite-etapa --excepcion`) → pm-planificacion.
- Las cargas a registros desde la reunión se hicieron solo tras la confirmación.
- El hook Write/Edit funcionó en el hilo principal y en los subagentes.
- La sanidad ESP-10 bloqueó la puerta y se levantó al registrar la solicitud de cambio.
- `bmad.py linea-base` se ejecutó solo por pm-director y después de la decisión.
