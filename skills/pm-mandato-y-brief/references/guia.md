# Guía de mandato y brief · Mandate and brief guide

## 1. Tabla de decisión: qué producir en la puesta en marcha
| Situación del proyecto | Perfil | Artefactos | Confirmaciones humanas en la skill |
|---|---|---|---|
| Pequeño (≤ 3 meses, 1 equipo, presupuesto bajo el umbral de la PMO), predictivo | Mínimo | mandato + brief (con business case esquemático fusionado) | 1 combinada (nivel + enfoque + artefactos) |
| Producto digital, `enfoque_entrega=agil`, alcance flexible | Ágil mínimo (SPEC §1.10.12) | mandato + brief ligero + visión; épicas iniciales para `pm-agil-hibrido` | 1 combinada |
| Híbrido o con varios interesados | Completo parcial | mandato + propuesta + brief + roadmap con vías por entregable | 2 (nivel; enfoque) |
| Inversión alta, regulado, varios proveedores | Completo | los seis artefactos | 2 (nivel; enfoque) |

La puerta `autorizar-inicio` (tercera decisión humana) existe en todos los perfiles y siempre la registra `pm-director`.
En versión mínima se produce solo propuesta + brief (o brief fusionado con business case esquemático); en completa se añaden canvas, visión y roadmap.

**Confirmación combinada (perfil mínimo):** una sola tabla de tres filas (nivel de formalidad · enfoque de entrega con su puntuación · lista de artefactos; más la ruta BMAD si aplica), una sola respuesta del usuario y una sola fila en `decisiones.csv` que cubre todo.

## 2. Perfil ágil mínimo
Cuando `enfoque_entrega` es `agil` y el proyecto es chico o mediano:
- **Brief ligero** (una o dos páginas): problema, objetivo medible, cliente, alcance por épicas con al menos una exclusión, restricciones (fecha y presupuesto fijos si los hay), tolerancia de alcance en MoSCoW (qué Must no se negocia), product owner prospectivo y referencia al business case de una página (`pm-caso-de-negocio`).
- **Visión** de una frase + campos (`templates/declaracion-vision.md`), que el product owner usará para ordenar el backlog.
- **Roadmap** opcional: releases dentro de etapas de gestión; nunca reemplaza las puertas de etapa.
- No se produce aquí: canvas y propuesta (salvo pedido); la PBS/WBS completa la sustituye luego el backlog priorizado.
- Una sola confirmación humana (paso 5) y luego la puerta `autorizar-inicio`.

## 3. Selección del enfoque de entrega
- Aplicar la tabla de decisión de nueve criterios de `pm-knowledge/references/pmbok8-estandar-principios-ciclos.md` §4.4.4 (elaboración propia a partir de los factores de entregable, proyecto y organización del Estándar PMBOK 8, §4.4.1–4.4.3): cada criterio se puntúa 1 (favorece predictivo), 2 (híbrido) o 3 (adaptativo); la suma va de 9 a 27. Lectura: ≤ 13 → predictivo (evaluar incremental si hay valor en entregas parciales); 14–21 → híbrido; ≥ 22 → adaptativo. Mostrar la puntuación por criterio, la suma y la lectura; la puntuación orienta la conversación y no sustituye el juicio ni el acuerdo con el ejecutivo.
- Entregables que puntúan distinto → híbrido por construcción: cada entregable clave lleva su vía en el brief y en el roadmap.
- El marco sigue siendo el ciclo de vida por etapas de PRINCE2: el enfoque se elige para el trabajo dentro de las etapas (paquetes de trabajo iterativos, sprints, releases).
- La decisión se revisa en cada puerta de etapa; el roadmap lo indica como revisión programada.
- Registro: `estado.py set enfoque_entrega=predictivo|agil|hibrido --por "Rol: Nombre" [--nivel gestor|junta] [--fecha AAAA-MM-DD]`; con `--por`, el cambio queda anotado en `decisiones.csv` ("enfoque de entrega: anterior → nuevo", nivel `gestor` por defecto). El nivel `junta` (o `ejecutivo`) lo registra pm-director.

## 4. Variante BMAD (`estado.json.integraciones.especificacion = bmad`)
### 4.1 Qué es dueño de qué (SPEC §1.13)
| Dato | Dueño | En el project brief |
|---|---|---|
| Problema, usuarios, visión del producto | brief de producto BMAD | referencia (ruta + sha corto), un resumen de una línea como máximo |
| Justificación, beneficios, costos, tolerancias | business case PRINCE2 | sección 2 (esquemático) |
| Organización, etapas, puertas, enfoque del proyecto | PRINCE2 (este brief) | secciones 1, 4, 5, 6 |
| Requisitos FR/NFR, métricas SM | PRD BMAD (aún no existe en SU) | no se anticipan; se espera el PRD en la etapa 1 |

### 4.2 Cómo referenciar el brief de producto
1. `python3 ${CLAUDE_SKILL_DIR}/../pm-bmad-puente/scripts/bmad.py --proyecto <dir> inventario` → ruta, `status` y sha del brief de producto.
2. En el project brief, campo **Brief de producto BMAD / BMAD product brief** (sección 8 Referencias y en Antecedentes): `ruta · sha corto · status · fecha`.
3. No copiar párrafos. Si la junta necesita leer el problema, se adjunta el brief de producto al paquete de la puerta (`pm-direccion-decisiones`).
4. Si el brief de producto no existe todavía: el project brief se redacta igual y declara "brief de producto BMAD pendiente (rol Analyst)"; pm-method no lo escribe.
5. Si el contenido del brief de producto contradice el mandato (otro problema, otro cliente), es una discrepancia a reportar, no a resolver eligiendo una versión.

### 4.3 Ruta de planificación BMAD en el enfoque del proyecto
El enfoque del proyecto (sección 4 del brief, campo "Método de entrega") declara la ruta de planificación BMAD que el equipo seguirá. Nombres orientativos según BMAD v6 (verificar contra la versión instalada; el puente detecta por configuración, no por nombre de flujo):
| Ruta | Cuándo elegirla | Artefactos BMAD esperados | Consecuencia PRINCE2 |
|---|---|---|---|
| Rápida (quick flow / especificación técnica) | cambio acotado, bajo riesgo, un equipo, sin decisiones de arquitectura relevantes | especificación técnica + historias | perfil mínimo o ágil mínimo; etapa 1 corta |
| Método estándar (PRD + arquitectura + UX) | producto nuevo o rediseño con varios journeys | brief de producto, PRD, arquitectura, UX, épicas | PRD `final` y arquitectura suficiente para estimar antes de `autorizar-proyecto` |
| Empresarial (agrega seguridad, operación, cumplimiento) | regulado, varios proveedores, integración crítica | lo anterior + artefactos de seguridad/operación | perfil completo; aseguramiento revisa los artefactos adicionales |
La ruta es una decisión humana (puerta 2) y se revisa en cada puerta de etapa como el resto del enfoque.

### 4.4 Roadmap con BMAD
- SU (etapa 0): brief de producto (insumo).
- Etapa 1 (iniciación): PRD `final`, arquitectura suficiente para estimar, épicas iniciales; línea base del PRD en `autorizar-proyecto`.
- Etapas de entrega: releases por épica; cada sprint = paquete de trabajo; el gate de preparación de BMAD es insumo de `autorizar-etapa`.

## 5. Reglas extendidas
1. [PRINCE2] Las lecciones previas se buscan antes de redactar el brief y se registran en `lecciones.csv`; si no se encontraron, el brief lo declara.
2. [PRINCE2] El brief no exige precisión que aún no existe ni detalla lo que corresponde al PID.
3. [Plantillas] Metas y objetivos se distinguen (general vs. específico) y ambos llevan criterio de éxito medible; restricciones y supuestos van separados.
4. [Plantillas] La visión cabe en treinta segundos, nombra un cliente concreto y no contiene soluciones técnicas.
5. Visuales: canvas y roadmap llevan Mermaid por defecto; si `estado.json.integraciones.diagramas` declara otra herramienta, ofrecer a `pm-visuales` la versión mejorada sin cambiar el contenido.
6. [PRINCE2] La puesta en marcha no tiene plan de etapa propio; el primer plan es `02-planificacion/plan-etapa-1.md`.
7. [PRINCE2] El brief se absorbe en el PID y no se mantiene después de `autorizar-proyecto`.

## 6. Ejemplo trabajado
Mandato por correo: "Necesitamos que los técnicos de campo carguen las órdenes desde el celular antes de marzo; tenemos 60 k". Paso 2: autoridad emisora = gerencia de operaciones; ejecutivo prospectivo = `[por confirmar]` (bloqueante); restricciones de fecha (marzo) y costo (60 k, fuente: el correo). Paso 5 (1 = predictivo, 5 = adaptativo): requisitos poco estables 4, entregable divisible 5, usuarios disponibles 4, cultura 3, regulación 2 → lectura **ágil** con la regulación como restricción de calidad. Confirmación combinada: "Perfil ágil mínimo · enfoque ágil · mandato + brief ligero + visión". Tolerancias: `estado.py tolerancia --nivel proyecto tiempo="+0 semanas (fecha fija)" costo="+5 %" alcance="Must intocables; Could negociables"`.
Variante BMAD: el equipo ya tiene `brief.md` de BMAD (status `draft`). El project brief lo cita en Referencias (`planning-artifacts/briefs/brief-campo-2026-10-01/brief.md · a1b2c3d · draft`), no copia usuarios ni problema, y el enfoque declara "ruta rápida" porque es una app con un solo journey principal; se revisará en `autorizar-proyecto`.

## 7. Casos borde y escalamiento ampliado
- Proyecto dentro de un programa que ya aporta brief y junta → validar lo recibido, proponer ajustes, no duplicar.
- Discrepancias que el usuario no quiere resolver → issue `problema-preocupacion` (severidad `menor`, prioridad `media`) en `issues.csv`; si alguien debe hacer algo concreto ("confirmar el presupuesto con finanzas"), es una acción `A-###` en `acciones.csv`, no un issue.
- Pedido de enviar la propuesta por correo o publicarla → solo con vista previa y confirmación, vía `pm-integraciones`.
- Mandato que llega como página de una wiki o hilo de chat conectado → leerlo vía `pm-integraciones` y guardar instantánea en `03-control/fuentes/`.

## 8. Columnas del registro de lecciones
`id`, `fecha`, `etapa` (stage), `categoria` (category), `situacion` (situation), `efecto` (effect), `recomendacion` (recommendation), `prioridad` (priority), `responsable_seguimiento` (follow-up owner), `estado` (status), `notas` (notes).

## 9. Validar antes de invertir: supuestos como hipótesis
- **Cuándo:** la idea tiene incertidumbre alta (producto nuevo, usuarios nuevos, tecnología o proveedor no probados) o
  la junta duda. Se hace en la puesta en marcha y en la iniciación; es trabajo de la etapa 1 (paquetes de trabajo cortos).
- **Cómo:** listar los supuestos que sostienen la idea en tres familias (deseabilidad, viabilidad, factibilidad);
  calificar cada uno por `criticidad` (cuánto cambia el business case si es falso) y `certeza` (cuánta evidencia hay
  hoy); priorizar el cuadrante criticidad alta + certeza baja; para cada uno, el experimento más barato que dé evidencia,
  el criterio decidido de antemano (qué resultado cambiaría la decisión) y la fecha límite.
- **Registro:** `registro.py agregar supuestos --campo supuesto_o_restriccion=… --campo tipo=supuesto --campo categoria=deseabilidad|viabilidad|factibilidad --campo criticidad=alta --campo certeza=baja --campo experimento=… --campo criterio=… --campo fecha_limite=AAAA-MM-DD --campo responsable=…`;
  al cerrar el experimento: `actualizar supuestos S-… --campo validado=si|no --campo estado=validado|invalidado --campo fecha_validacion=… --campo evidencia=…`.
- **Controles:** sanidad SUP-01 (crítico sin experimento o sin fecha), SUP-02 (fecha vencida sin resultado), SUP-03
  (invalidado sin issue, cambio, riesgo o decisión que trate su efecto); puerta `autorizar-proyecto` con condición
  P-11 si quedan supuestos críticos sin validar. La junta puede aceptarlos de forma explícita: una decisión de nivel
  `junta` (o `ejecutivo`, o `capa-negocio`) en `decisiones.csv` que cite el id y diga que se acepta (verbo "aceptar" o
  "accept"; "aceptación" no cuenta), por ejemplo `registro.py agregar decisiones --campo decision="La junta acepta S-003
  sin validar: la prueba técnica se hace en la etapa 1" --campo decidido_por="Ejecutiva: …" --campo nivel=junta`
  (lo registra pm-director). Con esa decisión, P-11 baja de condición a aviso para ese supuesto y cita la D-###; la
  sanidad SUP lo sigue mostrando hasta que se valide.
- **Vista para la junta:** `templates/hipotesis-y-experimentos.md` (supuestos, experimentos, resultados y
  recomendación de seguir, ajustar o abandonar). Un supuesto que no se puede validar a tiempo pasa a `pm-riesgos`.
- **Con BMAD:** los supuestos y preguntas abiertas del brief, el PRFAQ o la investigación de BMAD son la fuente
  (`riesgos.py candidatos` los lista como clase supuesto o pregunta); pm-method no escribe en BMAD.

