# Campaña de estabilización · pm-method 2.6.2

Fecha: 2026-10-29 · Autor del encargo: Arturo Penas Rial ([LinkedIn](https://www.linkedin.com/in/arturopenasrial/)).

**Objetivo:** una versión estable que se pueda probar en serio. La campaña recorrió:

- caminos alternos, excepciones, dependencias e integraciones;
- los dos entornos, Claude Code y Hermes Agent;
- los opcionales: pm-kb con modelos de vectores y de respuesta, BMAD, diagram-design, visual-explainer y archify;
- la interacción entre esos componentes.

**Criterio de salida:** 0 FALLO en dos corridas seguidas, sin trazas de Python, con las omisiones declaradas en un
manifiesto y con la evidencia de las guías E2E idéntica entre corridas.

Este documento resume la campaña. Lo que la reproduce está en [PRUEBAS §2.5](../../PRUEBAS.md) (suite de variantes) y el
detalle de los cambios, en el `CHANGELOG.md` (2.6.2).

---

## 1. Qué se probó

| Frente | Cómo | Resultado |
|---|---|---|
| **Regresión** | `scripts/probar_paquete.py` | **508 OK · 0 FALLO** con Python 3.13 (1 omisión: DD sin `PM_DIAGRAM_DESIGN`); **506 OK · 0 FALLO** con 3.9.25 (3 omisiones: N y PE por matplotlib y Playwright, y DD) |
| **Integración cruzada** | `scripts/pruebas/integracion/correr.py` (seis cadenas) | **123 OK · 0 FALLO en 40 eslabones** |
| **Guías E2E** | `guias_e2e/correr.py`, dos corridas con pm-kb | **5/5** en las dos; evidencia idéntica entre corridas; cambia frente a 2.6.1 solo en E2E-1 (extractos de pm-kb que empiezan por el estado, versión de pm-kb) y en tres capturas de pm-kb |
| **Suite de variantes** | `variantes/correr.py --nivel todo --repetir 2` | **561 OK · 0 FALLO · 0 trazas · 0 omisiones fuera del manifiesto** en cada corrida (446 s y 372 s), con las mismas comprobaciones en las dos |
| **pm-kb** | `probar_kb.py`, `consultas_oro.py` | núcleo **23 OK** (3.13 y 3.9); con base **58 OK**; consultas de oro **14/15, MRR@5 0,75** |
| **Diagramas** | `validar_mermaid.py --render` | **131 bloques Mermaid · 0 errores** |
| **Docker** | imagen `pm-method:2.6.2`, batería `pm-pruebas` dos veces y perfil `kb` | dos corridas con `Resultado: todas las pruebas OK`: regresión **511 OK · 0 FALLO** con Python 3.14 (caso DD completo), guías **5/5**, integración **122 OK en 40 eslabones**, variantes sin E2E **291 OK · 0 FALLO**, 131 bloques Mermaid y webinar 5/5. Perfil `kb`: `verificar` 14 OK, E2E-1 indexado (444 unidades), token con vencimiento, ingreso por formulario y MCP por HTTP desde el contenedor `pm` |
| **En vivo con Claude Code** | `suite.py todo` y una sesión con pm-kb y diagram-design | ver §4 |

### 1.1 Suite de variantes por nivel

| Nivel | Qué cubre |
|---|---|
| robustez | Datos dañados: BOM, codificación, CSV mal formado, `estado.json` truncado. Migración de proyectos generados con 2.6.1 (E2E-2 y E2E-4) y de un `estado.json` v1 |
| caminos | Cierre normal y prematuro de punta a punta; puertas rechazadas y pendientes; excepción con plan rechazado y luego aprobado; cambios contradictorios |
| matriz | 12 celdas pairwise y 2 degradadas (ver §1.2) |
| integraciones | SMTP que rechaza un destinatario, que cierra la conexión o que no responde; webhook con error 500 y reenvío; `registrar` por `.eml` y MCP; instantánea de tracker dañada |
| contratos | Unas 1.780 citas de `script.py subcomando --opción` en skills, agentes, guías y webinar contra la ayuda real; claves y columnas que leen pm-kb, `paquete.py` e `inicio.py` contra el esquema; versiones del CI |
| hermes | Instalación doble e idéntica, unas 200 rutas, agentes, destino ajeno rechazado, scripts que corren desde la copia de Hermes y contraste con el plugin |
| e2e | Las cinco guías con `--comparar` en Python 3.13 (con pm-kb) y 3.9 |
| opcionales | pm-kb con simuladores de vectores (formatos TEI y OpenAI), re-ranqueo y respuesta (API de Anthropic y compatible con OpenAI); interacción con la bitácora, propuestas, interesados, circulación restringida y BMAD; MCP por stdio y HTTP; diagram-design, archify y visual-explainer en un contenedor sin red, a partir de la WBS de pm-method |

### 1.2 Matriz de entornos (pairwise)

Ejes: Python 3.9 o 3.13 · dependencias completas o mínimas (sin pyyaml, docx, openpyxl, matplotlib ni Playwright) · sin
BMAD, BMAD v4, v6, 6.12.4, 6.12.4 fuera de rango o 6.12.4 con configuración TOML · español o inglés · consola UTF-8 o
cp1252 (la de Windows) · ruta simple o con espacios y acentos · cierre normal o prematuro. Las 192 combinaciones se
cubren de a pares con 12 celdas, más 2 celdas degradadas a propósito. El detalle está en
[PRUEBAS §2.5](../../PRUEBAS.md).

---

## 2. Defectos encontrados y corregidos

Todos tienen su prueba de regresión, y cada prueba falla con el código anterior.

| Área | Defectos |
|---|---|
| **Datos y codificación** | CSV con BOM repetía ids; un registro ilegible se informaba como «ninguno»; trazas de Python con datos dañados; CSV mal formado reescrito en silencio; hook de inicio sin aviso; salida que fallaba con la consola de Windows; el guardián dejaba pasar una escritura de `estado.json` en una ruta con acentos bajo cp1252 |
| **Caminos del ciclo** | `cierre --prematuro` guardaba un dato que nadie usaba y no se podía usar desde la iniciación (ahora es una puerta propia, con C-08); cambios contradictorios que consumían presupuesto; EST-03 bloqueaba un cierre desde la iniciación; la guía de decisiones dejaba una condición abierta en el cierre |
| **Hermes** | El instalador generaba rutas que no existen en la copia de Hermes |
| **Integraciones** | Instantánea de tracker que no es UTF-8 con traza; avisos de canal vacío incorrectos en `plan-envio`; configuración TOML de BMAD ignorada en silencio con Python < 3.11 |
| **pm-kb** | Con el servidor de vectores o de re-ranqueo caído, `buscar` e `indexar` fallaban; propuestas no indexadas; consultas abortadas por un interbloqueo de PostgreSQL; un extracto recortado hacía parecer abierta una fila cerrada (lo provocó un error del modelo en la sesión en vivo); claves inexistentes en el fixture |
| **Docker** | Las variables de envío no llegaban al contenedor; la clave del modelo de pm-kb llegaba al contenedor equivocado |
| **CI y documentación** | El flujo de Docker no se disparaba con cambios en pm-kb y fijaba una etiqueta vieja; `mapas.py render` citado pero inexistente; pasos de guías que no salían como decían |
| **Arnés de pruebas** | Un error abortaba toda la regresión; `python3` fijo; rutas con espacios; temporales que no se borraban; la E2E-5 fallaba sin matplotlib; diferencias de evidencia entre 3.9 y 3.13; en Docker, el lanzador de `python3` de las guías no podía ejecutarse en el `/tmp` montado sin permiso de ejecución (lo encontró la batería de la imagen) |

---

## 3. Instalaciones reales verificadas (contenedores descartables)

| Componente | Resultado |
|---|---|
| pm-kb en Ubuntu 24.04 limpio | instalador tres veces sin cambios; `verificar` 14 OK; web y formulario de ingreso; «Preguntar» contra el simulador de la API |
| pm-kb en Docker (perfil `kb`) | ver §1; la clave del modelo llega solo a `pm-kb` |
| diagram-design 2.6.136, visual-explainer 0.14.0, archify 3.2.0 | instalados como dicen las guías; detección por la sanidad; generación sin red a partir de datos de pm-method |
| pandoc 3.1.3 y zsh 5.9 | pasos de Office y de la lectura de claves en zsh |
| Hermes Agent v0.22.5 | **instalación incompleta**: el instalador oficial necesita `nodejs.org`, bloqueado en la red de prueba. La instalación de las skills de pm-method, sus rutas y los scripts desde la copia de Hermes están verificados (nivel `hermes`) |

---

## 4. En vivo con Claude Code

| Prueba | Resultado |
|---|---|
| `suite.py todo` · enrutamiento | **130/134** frases con la skill esperada. Fallaron 17 y 48, y en 83 y 128 el modelo no eligió ninguna skill. Dos repeticiones de esas cuatro dieron resultados distintos cada vez (17, 83 y 128 acertaron en la primera). Las descripciones de las skills no cambiaron en esta versión: es variabilidad del modelo en frases ambiguas (la 48 ya había sido inestable en corridas anteriores) |
| `suite.py todo` · guardarraíles | **OK**: `estado.json` sin cambios, cada escritura directa negada por el hook, BMAD intacto (USD 0,32) |
| `suite.py todo` · idioma | **OK**: respuesta en inglés y backlog desde BMAD sin escribir fuera de los scripts (USD 0,16) |
| Sesión con el plugin, el MCP de pm-kb y diagram-design | Funcionó, usando las herramientas esperadas y sin escribir registros a mano (USD 0,46). Error del modelo: tomó como abierto un riesgo retirado, porque el extracto no mostraba el estado. Se corrigió pm-kb para que el extracto empiece por el estado (KB-58) |

El arnés no informa el costo de la parte de enrutamiento. La documentación lo estima en USD 5–8 para `todo` completo.

---

## 5. Qué no se probó y queda para tu equipo

Todo esto tiene paso a paso en las guías.

- **Modelos reales de pm-kb** (bge-m3 en TEI, el re-ranqueador y la API de Anthropic): se probaron con simuladores del
  mismo protocolo, porque Hugging Face y ghcr.io están bloqueados acá y esta sesión no tiene una clave de API. Pasos:
  INSTALACION-WSL2 §8.8 e INSTALACION-DOCKER §8.9, con la clave solo en memoria.
- **Hermes Agent completo** (`hermes skills list` y una conversación): INSTALACION-WSL2 §7, con tu clave.
- **Windows nativo, Docker Desktop y arm64**: la consola de Windows se emuló en Linux.
- **Envíos reales** de correo, Slack y Teams, y la autenticación de conectores MCP como Atlassian: probados contra
  servidores locales.
- **Escenarios de robustez en vivo** (`suite.py robustez`: inyección, desorden, varias sesiones, escala): no se
  repitieron en esta versión (unos USD 4).

## 6. Limitaciones conocidas

- En un proyecto en inglés, los hallazgos de `sanidad.py` y `puertas.py verificar` salen en español.
- Queda por decidir si `autorizar-plan-excepcion` debe admitirse durante un cierre prematuro sin volver a la entrega, y
  si un supuesto `transferido` sin destino merece un aviso.
- La prueba de 50 altas simultáneas (caso CC) depende de la carga del equipo. Con la batería en vivo corriendo a la vez,
  4 comprobaciones superaron la espera del bloqueo (30 s); sola, pasa. `PM_BLOQUEO_ESPERA` ajusta la espera.
- Enrutamiento en vivo: variabilidad en frases ambiguas (§4).

## 7. Cómo reproducirlo

```bash
python3 scripts/validar_paquete.py
python3 scripts/probar_paquete.py
python3 scripts/pruebas/integracion/correr.py
python3 scripts/pruebas/guias_e2e/correr.py --salida /tmp/e2e --comparar docs/guias/evidencia
python3 scripts/pruebas/variantes/correr.py --nivel todo --repetir 2 --salida /tmp/variantes
docker compose -f docker/compose.yaml run --rm pruebas        # imagen pm-method:2.6.2
```

Los niveles que necesitan PostgreSQL, Docker o las copias de las skills externas se omiten de forma explícita cuando
falta alguno de ellos ([PRUEBAS §2.5](../../PRUEBAS.md)).
