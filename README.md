# pm-method · Agentes y skills de gestión de proyectos (ES/EN) · v2.0.0

Paquete bilingüe de **6 agentes**, **37 skills** y **2 hooks** que aplica un método de gestión de proyectos
consolidado, de la idea al cierre:

- **PRINCE2 7** es el **método y el ciclo de vida** (manda siempre): etapas de gestión, gestión por excepción, junta
  del proyecto, procesos SU, DP, IP, CS, MP, SB y CP.
- **PMBOK 8** aporta **solo el cómo**: técnicas (EVM, CPM, PERT, P×I, EMV, VAN…) aplicadas dentro de una práctica o
  proceso PRINCE2.
- **El libro de plantillas** aporta los **artefactos** (campos y listas de verificación, con etiquetas bilingües).
- **BMAD** (opcional) es la **capa de especificación** del producto (brief, PRD, arquitectura, épicas, historias), de
  solo lectura para pm-method.
- **Las herramientas MCP** que conecte el usuario (Jira, Confluence, Slack, Teams, transcripciones, OKR) son fuentes y
  canales opcionales; el paquete no predefine conectores.

La fuente de verdad es una **carpeta de proyecto** en Markdown, CSV y `estado.json`. Los `.docx`, `.xlsx` y `.zip` se
generan bajo demanda en `exportados/`. El enfoque de entrega puede ser predictivo, ágil o híbrido: cambia cómo se
trabaja dentro de las etapas, nunca elimina las puertas de decisión. Todo el conocimiento de las fuentes está destilado
en palabras propias.

---

## Novedades de v2

- **Orquestador en el hilo principal** y **5 subagentes de fase** con protocolo de retorno: solo el orquestador pregunta
  al usuario y presenta las puertas.
- **Comandos como skills** (`pm-ayuda`, `pm-nuevo`, `pm-estado`, `pm-reporte`, `pm-puerta`, `pm-sync`); la carpeta
  `commands/` ya no existe.
- **Puente BMAD** de solo lectura (v4, v6.11–v6.12) con fachada única de especificación (`especificacion.py`, contrato
  `pm-spec-index/1`) y traspaso de decisiones (`bmad.py handoff`).
- **Integraciones MCP genéricas** (`pm-integraciones`), **OKR** ligados a beneficios (`pm-okr`), **actas desde
  transcripciones** (`pm-reuniones`), exportación **MSPDI** para MS Project (`cpm.py --mspdi`).
- **Sanidad** del ecosistema (`pm-sanidad`, `sanidad.py`) y **hooks** de protección y de inicio de sesión.
- Proyectos v1: `estado.json` y los registros migran solos al leerse.

---


### Instalación rápida desde GitHub
```bash
claude plugin marketplace add <usuario>/pm-method
claude plugin install pm-method@pm-method
```
Hermes: `hermes skills tap add <usuario>/pm-method` o clonar y usar `skills.external_dirs`. Detalle y publicación del repositorio en [docs/INSTALACION.md §0](docs/INSTALACION.md).

## Inicio rápido (Claude Code)

```bash
claude plugin marketplace add /ruta/a/pm-method
claude plugin install pm-method@pm-method
pip install pyyaml python-docx openpyxl          # recomendado
```

En una sesión:

```
/pm-method:pm-ayuda                      # qué escribir en cada situación
/pm-method:pm-nuevo "Proyecto Faro"      # crea la carpeta del proyecto y detecta BMAD
/pm-method:pm-orquestador                # o, en lenguaje natural: "¿qué sigue?"
```

Para que el orquestador sea el agente de toda la sesión: `claude --agent pm-method:pm-orquestador`.
Copia manual, Cowork, Hermes, BMAD, MCP y configuración: **[docs/INSTALACION.md](docs/INSTALACION.md)**.

---

## Componentes

### Agentes

| Agente | Tipo | Procesos | Qué hace |
|---|---|---|---|
| `pm-orquestador` | hilo principal (también skill) | todos | lee el estado, pregunta, delega, presenta puertas |
| `pm-director` | subagente | DP | solicitudes de decisión; **único** que registra puertas y aprobaciones |
| `pm-inicio` | subagente | SU, IP | mandato, brief, business case, OKR, organización, enfoques, PID |
| `pm-planificacion` | subagente | Plans, IP, SB | PBS/WBS o backlog, estimación, cronograma, presupuesto, planes |
| `pm-control` | subagente | CS, MP | paquetes, registros, riesgos, issues, informes, calidad, actas, sincronización |
| `pm-cierre` | subagente | CP | aceptación, handover, lecciones, revisión de beneficios, informe final |

Los subagentes no preguntan al usuario, no delegan en otros agentes y heredan las herramientas de la sesión (incluidos
los MCP). Razones del diseño: [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md).

### Comandos de uso humano

Toda skill es invocable como `/pm-method:<skill>` (plugin) o `/<skill>` (copia manual y Hermes). Seis skills son
comandos que el modelo no activa solo y no consumen contexto:

| Comando | Uso |
|---|---|
| `pm-ayuda [tema]` | ayuda contextual |
| `pm-nuevo "Nombre" [carpeta]` | crear un proyecto |
| `pm-estado [carpeta]` | estado y siguiente paso |
| `pm-reporte highlight\|checkpoint\|excepcion` | informe de avance |
| `pm-puerta <tipo>` | preparar una puerta de la junta |
| `pm-sync [bmad\|tracker\|okr]` | sincronizar fuentes externas |

### Hooks (plugin de Claude Code)

- `PreToolUse` (`hooks/guardian.py`): impide editar a mano `estado.json`, los registros CSV, los derivados de la
  especificación y las copias congeladas; impide que los subagentes escriban en carpetas de BMAD.
- `SessionStart` (`hooks/inicio.py`): al abrir, retomar, limpiar o compactar, agrega fase, etapa y sanidad rápida del
  proyecto.

---

## Catálogo resumido (37 skills)

| Grupo | Skills |
|---|---|
| Dirección y estado | `pm-orquestador`, `pm-direccion-decisiones`, `pm-estado-proyecto`, `pm-sanidad` |
| Inicio (SU, IP) | `pm-mandato-y-brief`, `pm-caso-de-negocio`, `pm-okr`, `pm-organizacion-roles`, `pm-enfoques-gestion`, `pm-acta-constitucion` |
| Planificación | `pm-planificacion-por-productos`, `pm-cronograma-estimacion`, `pm-costos-presupuesto`, `pm-plan-etapa-y-limites`, `pm-agil-hibrido`, `pm-adquisiciones` |
| Control (CS, MP) | `pm-paquetes-trabajo`, `pm-registros`, `pm-riesgos`, `pm-issues-cambios`, `pm-progreso-reportes`, `pm-calidad`, `pm-comunicacion-stakeholders`, `pm-reuniones`, `pm-visuales` |
| Cierre (CP) | `pm-cierre-proyecto`, `pm-lecciones-aprendidas` |
| Transversales | `pm-bmad-puente`, `pm-integraciones`, `pm-exportar`, `pm-knowledge` |
| Comandos | `pm-ayuda`, `pm-nuevo`, `pm-estado`, `pm-reporte`, `pm-puerta`, `pm-sync` |

Detalle de cada skill (disparadores, artefactos, agente, scripts): **[docs/CATALOGO.md](docs/CATALOGO.md)**.

### Ciclo de vida

```
SU (etapa 0) ──autorizar-inicio──▶ IP (etapa 1 = iniciación)
IP ──autorizar-proyecto + autorizar-etapa──▶ entrega (etapa 2): CS/MP
CS ──estado.py limite-etapa──▶ SB ──autorizar-etapa──▶ CS (etapa n+1)
CS ──informe de excepción → decisión de la junta → limite-etapa --excepcion──▶ SB ──autorizar-plan-excepcion──▶ CS
CS/SB ──estado.py cierre [--prematuro]──▶ CP ──autorizar-cierre──▶ cerrado
```

Las puertas las decide una persona con rol en la junta; `pm-director` las registra (`estado.py puerta`, que también
escribe `decisiones.csv`).

---

## Documentación

| Documento | Contenido |
|---|---|
| [INSTALACION](docs/INSTALACION.md) | requisitos, plugin, copia manual, Cowork, Hermes, BMAD, MCP, configuración, hooks, verificación, actualización, desinstalación, problemas frecuentes |
| [ARQUITECTURA](docs/ARQUITECTURA.md) | capas, precedencia PRINCE2/PMBOK, agentes vs subagentes, scripts, comandos, carga progresiva, precisión de activación, diagramas |
| [INTEGRACIONES](docs/INTEGRACIONES.md) | dependencias, decisiones por candidato, contratos de integración, controles, cómo agregar una integración |
| [SINCRONIZACION](docs/sincronizacion.md) | fuente única, fachada de especificación y traspaso de decisiones BMAD ↔ gobierno |
| [SANIDAD](docs/SANIDAD.md) | comprobaciones de consistencia y controles permanentes |
| [RACI](docs/RACI.md) | responsabilidades por rol, agente y skill |
| [CATALOGO](docs/CATALOGO.md) | catálogo completo de las 37 skills |
| [CASOS-DE-USO](docs/CASOS-DE-USO.md) | situaciones típicas y qué invocar |
| [CASO-MAESTRO](docs/CASO-MAESTRO.md) | caso de punta a punta con BMAD |
| [Colisiones](docs/colisiones.md) | dueños únicos y pistas de alcance entre skills |
| [SPEC.md](SPEC.md) | especificación de construcción (para autores de skills) |

---

## Estructura del paquete

```
pm-method/
  .claude-plugin/     plugin.json (pm-method 2.0.0) · marketplace.json (pm-method)
  agents/             6 agentes (orquestador + 5 subagentes; personas en Hermes)
  skills/             37 skills (SKILL.md + references/ + templates/ + scripts/)
  hooks/              hooks.json · guardian.py (PreToolUse) · inicio.py (SessionStart)
  scripts/            validar_paquete.py · probar_paquete.py · pruebas/fixtures (BMAD v4, v6)
  docs/               documentación · evaluacion/frases-enrutamiento.tsv
  compatibilidad.json versiones probadas, dependencias y clientes
  SPEC.md             especificación y convenciones canónicas
```

Verificación del paquete: `python3 scripts/validar_paquete.py` (estructura, tamaños, descripciones, agentes, hooks) y
`python3 scripts/probar_paquete.py` (35 pruebas de regresión con BMAD v6, BMAD v4 y sin BMAD).

---

## Reglas que el paquete aplica siempre

Etapas de gestión por defecto; toda desviación prevista fuera de tolerancia se escala como excepción; nada se da por
aprobado sin un acto humano registrado; escrituras externas solo con confirmación; un dueño por dato; contenido
generado marcado como borrador y datos faltantes como `[por confirmar]` / `[to be confirmed]`; respuesta en el idioma
del usuario. Convenciones completas: `SPEC.md` §1.10.

---

## English summary

pm-method 2.0.0 is a bilingual (Spanish/English) pack of 6 agents, 37 Agent Skills and 2 hooks for end-to-end project
management. PRINCE2 7 provides the method and life cycle, PMBOK 8 only the techniques, a templates book the artifacts,
BMAD (optional) the read-only product specification layer, and user-connected MCP tools the optional sources and
channels. A main-thread orchestrator is the only component that talks to the user; five phase subagents produce
artifacts in isolated contexts and return a structured block. Install as a Claude Code plugin
(`claude plugin marketplace add <path>`, then `claude plugin install pm-method@pm-method`), by copying skills and
agents, in Cowork as a plugin, or in Hermes (`~/.hermes/skills/` or `skills.external_dirs`; agents become personas).
Start with `/pm-method:pm-ayuda` or `/pm-method:pm-orquestador`. See `docs/` for installation, architecture and
integrations.

---

## Licencia

MIT (ver `.claude-plugin/plugin.json`). El contenido de las fuentes está destilado en palabras propias, sin texto
literal. PRINCE2® y PMBOK® son marcas registradas de sus respectivos titulares; BMAD Method es un proyecto MIT de
terceros que el paquete no incluye.
