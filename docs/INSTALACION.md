# Instalación y configuración · pm-method 2.0.0

Guía para instalar, configurar, verificar, actualizar y desinstalar el paquete de agentes y skills **pm-method** en
Claude Code, Cowork y Hermes Agent, y para conectarlo con BMAD y con las herramientas MCP de la organización.

> Convenciones de este documento
> - `/ruta/a/pm-method` es la carpeta del paquete (la que contiene `SPEC.md` y `.claude-plugin/`).
> - `<pm-estado-proyecto>` es la carpeta instalada de esa skill (ver §7.1).
> - **[verificar]** marca un dato que no se probó en este entorno o que depende de la versión vigente del cliente.

---

## 0. Instalación desde GitHub (recomendada para equipos)

Cuando el paquete está publicado en un repositorio de GitHub (en adelante `<usuario>/pm-method`), cada integrante del equipo
lo instala desde allí y recibe las actualizaciones con un solo comando. La raíz del repositorio es a la vez el plugin
(`.claude-plugin/plugin.json`) y su marketplace (`.claude-plugin/marketplace.json`, nombre `pm-method`).

### 0.1 Publicar el repositorio (una vez, lo hace el responsable del paquete)
```bash
# en la carpeta descomprimida pm-method/
git init && git add . && git commit -m "pm-method 2.0.0"
gh auth login                       # inicia sesión en el navegador; no usar contraseñas en la línea de comandos
gh repo create <usuario>/pm-method --private --source . --push
```
Sin la CLI `gh`: crear el repositorio vacío en github.com y hacer `git remote add origin https://github.com/<usuario>/pm-method.git`
y `git push -u origin main`; GitHub pide un token de acceso personal en lugar de la contraseña de la cuenta. Para repositorios
privados, cada integrante necesita acceso de lectura al repositorio.

### 0.2 Claude Code (cada integrante)
```bash
claude plugin marketplace add <usuario>/pm-method      # acepta un repositorio GitHub como origen
claude plugin install pm-method@pm-method
claude plugin list                                     # pm-method · enabled
# actualizar a una versión nueva publicada:
claude plugin marketplace update pm-method && claude plugin update pm-method@pm-method
```
Dentro de una sesión: `/plugin marketplace add <usuario>/pm-method` y `/plugin install pm-method@pm-method`.
Para todo un equipo con plan Team/Enterprise, el administrador puede declarar el marketplace y habilitar el plugin en la
configuración gestionada (`extraKnownMarketplaces` + `enabledPlugins`) para que se instale solo [verificar en la
documentación vigente de configuración gestionada].
Para un solo repositorio de proyecto: declarar el marketplace con `--scope project` (queda en `.claude/settings.json` del
repositorio y lo comparten quienes confíen en la carpeta).

### 0.3 Hermes Agent
```bash
hermes skills tap add <usuario>/pm-method                         # registra el repositorio como fuente de skills
hermes skills install <usuario>/pm-method/skills/pm-orquestador   # instala una skill (repetir por skill)
/reload-skills                                                    # dentro de Hermes, para refrescar los comandos
```
Alternativa robusta: `git clone https://github.com/<usuario>/pm-method.git` y apuntar `skills.external_dirs` de
`~/.hermes/config.yaml` a `pm-method/skills` (todas las skills, y `git pull` para actualizar). Los agentes se usan como
personas (ver §3). [verificar que `tap add` reconozca la carpeta `skills/` del repositorio con la versión de Hermes instalada]

### 0.4 Verificar
`python3 scripts/validar_paquete.py` y `python3 scripts/probar_paquete.py` en el clon (deben dar OK y 35 OK), y
`/pm-method:pm-ayuda` en Claude Code o `/pm-ayuda` en Hermes.

## 1. Requisitos

| Requisito | Obligatorio | Para qué | Nota |
|---|---|---|---|
| Python ≥ 3.9 | sí | todos los scripts deterministas (`estado.py`, `registro.py`, `sanidad.py`, `bmad.py`…) | solo biblioteca estándar para el núcleo |
| Cliente compatible | sí | Claude Code (plugin o copia), Cowork (plugin) o Hermes Agent (skills) | CLI usada en las pruebas de este entorno: Claude Code 2.1.302 |
| `pyyaml` | recomendado | leer la configuración de BMAD y `sprint-status.yaml`; lo exige `probar_paquete.py` | sin él, el puente BMAD no funciona |
| `python-docx` | recomendado | exportar `.docx` y leer actas en `.docx` | |
| `openpyxl` | recomendado | exportar `.xlsx` | |
| Node.js / `npx` | solo con BMAD | `npx bmad-method install` en el repositorio del producto | el paquete no instala BMAD |
| `@mermaid-js/mermaid-cli` (`mmdc`) | opcional | insertar diagramas Mermaid como imagen en Word | |
| Java + `mpxj` | opcional | solo para validar o convertir MSPDI / `.mpp` | `cpm.py --mspdi` no lo necesita |

Las dependencias están declaradas en `compatibilidad.json` (`dependencias.obligatorias` está vacío: el núcleo funciona
solo con la biblioteca estándar).

---

## 2. Instalación en Claude Code

### 2.1 Como plugin desde el marketplace local (recomendado)

La carpeta del paquete es a la vez un plugin (`.claude-plugin/plugin.json`, nombre `pm-method`, versión 2.0.0) y un
marketplace local (`.claude-plugin/marketplace.json`, nombre `pm-method`). Es la única modalidad que activa los
**hooks** de protección y de sanidad (§9).

Desde la terminal:

```bash
claude plugin marketplace add /ruta/a/pm-method
claude plugin install pm-method@pm-method
claude plugin list                       # pm-method debe figurar instalado y habilitado
```

O dentro de una sesión de Claude Code:

```
/plugin marketplace add /ruta/a/pm-method
/plugin install pm-method@pm-method
```

Qué queda disponible:
- 37 skills, invocables como `/pm-method:<skill>` (31 que el modelo puede activar solo y 6 comandos de uso humano).
- 6 agentes: `pm-method:pm-orquestador` (para el hilo principal) y los subagentes de fase `pm-method:pm-director`,
  `pm-method:pm-inicio`, `pm-method:pm-planificacion`, `pm-method:pm-control`, `pm-method:pm-cierre`.
- Hooks `PreToolUse` (`hooks/guardian.py`) y `SessionStart` (`hooks/inicio.py`), declarados en `hooks/hooks.json`.

Los scripts se ubican con `${CLAUDE_PLUGIN_ROOT}` (raíz del plugin) y `${CLAUDE_SKILL_DIR}` (carpeta de cada skill),
que Claude Code expande en skills, agentes y hooks. No hay carpeta `commands/`: es un formato heredado y en v2 los
comandos son skills.

### 2.2 Copia manual (sin plugin)

```bash
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r /ruta/a/pm-method/skills/* ~/.claude/skills/
cp /ruta/a/pm-method/agents/*.md ~/.claude/agents/
```

- Para un solo repositorio, copiar a `.claude/skills/` y `.claude/agents/` de ese repositorio.
- Las skills se invocan como `/<skill>` (sin prefijo) y los subagentes como `pm-inicio`, `pm-control`, etc.
- Los scripts quedan en `~/.claude/skills/<skill>/scripts/`.
- **Diferencia importante:** la copia manual **no registra los hooks** (dependen de `hooks/hooks.json` del plugin). La
  sanidad sigue disponible a demanda (`/pm-sanidad`) y la exigen `pm-puerta` y `pm-orquestador`, pero no hay bloqueo
  automático de ediciones sobre `estado.json` ni sobre los registros.
- No combinar plugin y copia manual: la sanidad lo detecta como **INS-04** (skill instalada más de una vez).

### 2.3 Cowork

Cowork usa el formato de plugin: instalar `pm-method` desde la gestión de plugins de la aplicación, apuntando al mismo
paquete. **[verificar]** el recorrido exacto de pantallas en la versión vigente de la aplicación. Las skills personales
de `~/.claude/skills/` no son una vía de instalación para Cowork.

---

## 3. Instalación en Hermes Agent

Hermes lee skills en formato `SKILL.md`, de modo que las 37 skills se usan sin cambios. No tiene un comando documentado
para instalar desde una carpeta local: se copia o se declara un directorio externo.

**Opción A: copiar**
```bash
cp -r /ruta/a/pm-method/skills/* ~/.hermes/skills/
```

**Opción B: directorio externo** (sin copiar), en `~/.hermes/config.yaml`:
```yaml
skills:
  external_dirs: ["/ruta/a/pm-method/skills"]
```

**Opción C: desde un repositorio GitHub** (si el paquete se publica en uno):
```bash
hermes skills install <owner>/<repo>/skills/pm-orquestador    # una skill
hermes skills tap add <owner>/<repo>                          # registrar el repositorio como fuente
```

Tras instalar, `/reload-skills` recarga el catálogo. Cada skill es un comando `/nombre-skill` (Hermes admite hasta
cinco apiladas en un mismo mensaje).

**Agentes en Hermes.** Hermes no tiene subagentes con nombre (delega con `delegate_task`, sin archivos de agente). Los
seis archivos de `agents/` se usan como texto de persona:
- Perfil dedicado: `hermes profile create pm` (crea `~/.hermes/profiles/pm/`) y copiar el cuerpo de
  `agents/pm-orquestador.md` como `SOUL.md` del perfil (o en `~/.hermes/SOUL.md` para la persona global).
- Personalidades: declarar los demás agentes en `config.yaml` (`agent.personalities`) y activarlos con
  `/personality <nombre>`.
- La lógica de fase vive en las skills, que el orquestador ejecuta en el mismo hilo (ver `ARQUITECTURA.md` §4.5).

**Rutas de scripts en Hermes:** `python3 ~/.hermes/skills/pm-estado-proyecto/scripts/estado.py …`; con
`external_dirs`, la ruta es la del directorio externo. Hermes no tiene hooks equivalentes documentados: la sanidad la
ejecutan `pm-orquestador` (al empezar) y `pm-puerta` (antes de cada puerta).

**[verificar]** la sintaxis vigente de `config.yaml`, perfiles y personalidades en la documentación de Hermes.

---

## 4. BMAD en el repositorio del producto (opcional)

pm-method **no instala ni actualiza BMAD**; lo instala el equipo del producto en su repositorio:

```bash
cd /ruta/al/repositorio
npx bmad-method install
```

En Claude Code, BMAD se instala como skills (`bmad-prd`, `bmad-architecture`, `bmad-create-epics-and-stories`,
`bmad-sprint-planning`, `bmad-build`, `bmad-correct-course`, `bmad-help`, entre otras) y escribe sus salidas en
`_bmad-output/planning-artifacts/` (carpetas fechadas para brief, PRD, arquitectura y UX; `epics.md` fijo) e
`_bmad-output/implementation-artifacts/sprint-status.yaml`. En v4 usa `docs/` y `.bmad-core/core-config.yaml`.

**Detección desde pm-method.** La carpeta del proyecto de gestión debe quedar **fuera** de `_bmad/`, `_bmad-output/` y
`.bmad-core/` (por ejemplo, `repositorio/gestion/`):

```bash
python3 <pm-bmad-puente>/scripts/bmad.py --proyecto ./gestion detectar
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion integracion especificacion=bmad
```

`detectar` registra en `estado.json.integraciones.bmad` el layout (`v6` | `v4`), las rutas y el soporte (`soportada`,
`v4`, `version-no-visible`, `no-probada`). Si BMAD no está en un directorio superior, agregar `--raiz <repo>`. El
comando `/pm-nuevo` hace esta detección automáticamente al crear el proyecto.

Compatibilidad declarada (`compatibilidad.json`): probado con BMAD 4.x, 6.11 y 6.12; relevado `bmad-method@6.12.4`
(14-oct-2026). BMAD introduce cambios incompatibles en casi cada versión menor 6.x; fuera de rango el puente trabaja en
**modo degradado con aviso** (sanidad ESP-07) y conviene correr `scripts/probar_paquete.py` antes de la siguiente puerta.

---

## 5. Dependencias Python

```bash
pip install pyyaml python-docx openpyxl
```

En sistemas con Python gestionado por el sistema operativo puede hacer falta un entorno virtual o la opción
`--break-system-packages`. La sanidad informa la falta de cada módulo como **INS-01** con el comando de instalación.

---

## 6. Conexión de herramientas MCP

El paquete **no trae `.mcp.json` ni credenciales** y no predefine conectores. Las skills describen capacidades y
`pm-integraciones` las resuelve con los MCP presentes en la sesión.

1. Conectar los servidores con la gestión de conectores del propio cliente (en Claude Code, `claude mcp add …` o la
   gestión de conectores de la aplicación; en Hermes, su configuración MCP). Las credenciales quedan en el cliente.
2. Pedir a pm-method que detecte y registre las capacidades (`pm-integraciones` o `/pm-method:pm-sync`), o
   registrarlas a mano:
   ```bash
   python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion integracion tracker=jira chat=teams
   ```

| Capacidad (`estado.json.integraciones`) | Valores reconocidos | Ejemplos de servidor |
|---|---|---|
| `tracker` | `ninguno`, `jira`, `linear`, `github`, `azure-devops` | Atlassian Rovo MCP Server |
| `docs` | `ninguno`, `confluence`, `notion`, `sharepoint` | Atlassian Rovo (Confluence) |
| `chat` | `ninguno`, `slack`, `teams` | Slack MCP oficial; Teams/Work IQ |
| `reuniones` | `manual`, `archivo`, `granola`, `fireflies`, `zoom`, `minutes` | Granola, Fireflies, Zoom, minutes-mcp |
| `okr` | `archivo`, `tability` | Tability MCP |
| `diagramas` | `mermaid`, `diagram-design`, `archify`, `visual-explainer`, `drawio` | drawio-mcp; skills externas |
| `cronograma` | `cpm`, `mspdi` | — (interno) |
| `export` | `scripts`, `skills-office` | skills oficiales docx/xlsx/pptx |

Reglas que aplica el paquete: lectura libre; **escritura externa solo con vista previa y confirmación explícita**; los
datos externos entran como instantáneas fechadas en `03-control/fuentes/`. Detalle y justificación en
`INTEGRACIONES.md`. Notas de proveedores relevadas al 2026-10-17: el servidor "Teams (preview)" de Microsoft está
marcado como legado (se recomienda Work IQ); el Slack MCP oficial está restringido a apps publicadas o internas; la
obtención de transcripciones por Zoom MCP **no está confirmada**.

---

## 7. Configuración

### 7.1 Ubicación de los scripts

| Instalación | `<pm-estado-proyecto>` |
|---|---|
| Plugin de Claude Code / Cowork | `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/` |
| Copia manual | `~/.claude/skills/pm-estado-proyecto/` (o `.claude/skills/…` del repositorio) |
| Hermes | `~/.hermes/skills/pm-estado-proyecto/` (o el directorio de `external_dirs`) |

Todos los scripts aceptan `--proyecto <dir>` y pueden ejecutarse desde cualquier carpeta.

### 7.2 Crear un proyecto e idioma

```bash
python3 <pm-estado-proyecto>/scripts/nuevo_proyecto.py --ruta ./gestion --nombre "Proyecto Faro" \
    --idioma es --enfoque hibrido --ejecutivo "Nombre" --gestor "Nombre"
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion set idioma=en     # cambiar idioma después
```

`--idioma` acepta `es` | `en` y `--enfoque` `predictivo` | `agil` | `hibrido`. El idioma de `estado.json` rige las
respuestas de los scripts; las skills responden en el idioma del usuario.

### 7.3 Umbrales de riesgo y tolerancias

```bash
# Umbrales P×I (por defecto: alto ≥ 15, medio 6–12, bajo ≤ 5)
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion umbrales-riesgo alto=15 medio=6

# Tolerancias por nivel (dimensiones: tiempo, costo, alcance, calidad, beneficios, riesgo, sostenibilidad)
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion tolerancia --nivel proyecto tiempo="±2 semanas" costo="±10 %"
python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion tolerancia --nivel etapa costo="±5 %"
```

Las tolerancias son decisiones de gobierno: las de proyecto las fija la capa de negocio/ejecutivo y las de etapa la
junta en cada `autorizar-etapa`. En operación normal las registra `pm-director` tras la decisión humana; el comando
directo sirve para la carga inicial o una corrección. Tiempo y costo son el mínimo obligatorio (sanidad EST-06/07).

### 7.4 Settings recomendados en Claude Code

El listado de descripciones de skills de Claude Code tiene un presupuesto de ≈1 % de la ventana de contexto. Las 31
skills de pm-method que el modelo puede activar suman 6.160 caracteres; si en la misma sesión hay BMAD u otros repos de
skills, el total puede superar el presupuesto y el listado se recorta. En ese caso, en `settings.json`:

```json
{
  "skillListingBudgetFraction": 0.02
}
```

La sanidad avisa con **INS-05** cuando las descripciones visibles superan ≈8.000 caracteres. `skillOverrides`
(`on` | `name-only` | `user-invocable-only` | `off`) permite reducir skills de otros orígenes, pero **no aplica a
skills de plugins**.

### 7.5 Orquestador en el hilo principal

El orquestador es el único componente que conversa con el usuario. Dos formas de usarlo:
- Como skill, dentro de cualquier sesión: `/pm-method:pm-orquestador` (`/pm-orquestador` en copia manual o Hermes).
- Como agente principal de toda la sesión:
  ```bash
  claude --agent pm-method:pm-orquestador
  ```
  También puede fijarse con la clave `"agent"` de `settings.json` **[verificar el formato del valor en la documentación
  vigente]**.

---

## 8. Verificación post-instalación

| Paso | Comando | Resultado esperado |
|---|---|---|
| Manifiestos del plugin | `claude plugin validate /ruta/a/pm-method` | validación correcta |
| Estructura del paquete | `python3 /ruta/a/pm-method/scripts/validar_paquete.py` | `Skills: 37 (31 invocables por el modelo, listado 6160 caracteres) · Agentes: 6` y `OK` |
| Regresión de punta a punta (requiere PyYAML) | `python3 /ruta/a/pm-method/scripts/probar_paquete.py` | `Resultado: 35 OK · 0 FALLO` (BMAD v6, BMAD v4 y sin BMAD) |
| Skills visibles | `/pm-method:pm-ayuda` | tabla "qué escribir", catálogo de skills y comandos |
| Proyecto de prueba | `nuevo_proyecto.py --ruta /tmp/prueba --nombre "Prueba"` y `estado.py --proyecto /tmp/prueba siguiente` | carpeta creada y siguiente paso del método |
| Sanidad | `/pm-method:pm-sanidad` o `sanidad.py --proyecto /tmp/prueba --informe` | informe en `03-control/reportes/<fecha>-sanidad.md`, 0 ERROR en un proyecto nuevo (comprobado en este entorno; pueden aparecer AVISO de instalación, p. ej. INS-05 si hay otras skills instaladas) |
| Hook de inicio | abrir una sesión en una carpeta que contenga el proyecto | línea de contexto "pm-method · proyecto '…': fase …; sanidad rápida …" |

---

## 9. Hooks (solo plugin de Claude Code)

| Hook | Disparo | Qué hace |
|---|---|---|
| `PreToolUse` → `hooks/guardian.py` | cada `Write`, `Edit`, `MultiEdit`, `NotebookEdit` y `Bash` | niega (`permissionDecision: "deny"`) con el motivo: editar `estado.json` a mano (solo `estado.py`, `nuevo_proyecto.py`, `bmad.py`); editar con Write/Edit los nueve registros CSV de `03-control/registros/` (solo `registro.py`); editar derivados de especificación (`spec-index.json`, `requisitos-bmad.csv`, `matriz-trazabilidad-bmad.csv`, `inventario-bmad.json`, `avance-bmad.csv`) o las copias congeladas de `00-direccion/historial/`; y que un subagente `pm-*` escriba en `_bmad/`, `_bmad-output/` o `.bmad-core/` |
| `SessionStart` → `hooks/inicio.py` | `startup`, `resume`, `clear`, `compact` | si hay un `estado.json` a ≤ 2 niveles de la carpeta de trabajo (hasta 3 proyectos), agrega al contexto fase, proceso, etapa y el resultado de `sanidad.py --rapido` con los primeros ERROR |

Comportamiento relevante:
- Solo actúan dentro de una carpeta de proyecto pm-method (con `estado.json`); fuera de ella no deciden nada.
- El hilo principal **sí** puede escribir en carpetas de BMAD (los flujos propios de BMAD lo necesitan); la
  restricción aplica a los subagentes de pm-method, identificados por `agent_type` en la entrada del hook.
- Ante un error propio, el hook termina sin decidir (no bloquea por fallas internas).

**Cómo prescindir de los hooks.** El paquete no ofrece una opción para desactivarlos por separado. Las vías son:
- deshabilitar el plugin: `claude plugin disable pm-method` (y `claude plugin enable pm-method` para volver);
- o usar la copia manual (§2.2), que no registra hooks.

En ambos casos se pierde la protección automática; la disciplina de escribir solo por scripts queda a cargo de las
skills y de la sanidad.

---

## 10. Actualización y migración

1. Reemplazar o actualizar la carpeta del paquete (por ejemplo, con `git pull`).
2. Actualizar el marketplace y el plugin:
   ```bash
   claude plugin marketplace update pm-method
   claude plugin update pm-method@pm-method       # requiere reiniciar Claude Code
   ```
   En este entorno se probó la actualización de 1.0.0 a 2.0.0 con resultado correcto.
3. Copia manual o Hermes: volver a copiar `skills/` y `agents/` (con `external_dirs` basta actualizar la carpeta) y
   ejecutar `/reload-skills` en Hermes.
4. **Proyectos existentes:** `estado.json` y los registros migran solos al leerse (esquema `estado.json` v2 desde v1;
   `esquema.py` v2 con 9 registros). La sanidad avisa la diferencia de versión como **INS-02**.
5. Después de actualizar pm-method o BMAD: correr la sanidad completa en cada proyecto activo y, si BMAD cambió de
   versión, `probar_paquete.py`.

Cambio visible de v1 a v2: desaparece la carpeta `commands/`; los comandos son las skills `pm-ayuda`, `pm-nuevo`,
`pm-estado`, `pm-reporte`, `pm-puerta` y `pm-sync`.

---

## 11. Desinstalación

```bash
claude plugin uninstall pm-method@pm-method
claude plugin marketplace remove pm-method
```

- Copia manual: borrar las carpetas `pm-*` de `~/.claude/skills/` (o `.claude/skills/`) y los seis `pm-*.md` de
  `~/.claude/agents/`.
- Hermes: borrar las carpetas `pm-*` de `~/.hermes/skills/` o quitar la entrada de `external_dirs`; retirar el perfil o
  las personalidades creadas.
- Las carpetas de proyecto no se tocan: son Markdown, CSV y JSON legibles sin el paquete.

---

## 12. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `/pm-method:…` no aparece | plugin no instalado o deshabilitado | `claude plugin list`; `claude plugin enable pm-method`; reiniciar la sesión |
| El modelo no activa la skill esperada | listado recortado por presupuesto (BMAD u otros repos) | `"skillListingBudgetFraction": 0.02` (§7.4); sanidad INS-05; invocar la skill por comando |
| Responde una skill de otro repositorio | colisión de disparadores | sanidad INS-06; ajustar la descripción local u ocultar la externa con `skillOverrides`; ver `docs/colisiones.md` |
| "pm-method: estado.json se actualiza solo con estado.py…" | hook `PreToolUse` | es el comportamiento esperado: usar `estado.py` |
| "… se modifica con registro.py" | edición directa de un registro CSV | `registro.py --proyecto <dir> agregar|actualizar …` |
| "… es un derivado regenerable" | edición de un archivo de `02-planificacion/especificacion/` | regenerar con `bmad.py` o `especificacion.py` |
| "los agentes de gestión no escriben en carpetas de BMAD" | un subagente intentó escribir en BMAD | emitir `bmad.py handoff` y que el equipo BMAD aplique el cambio |
| `bmad.py detectar` no encuentra BMAD | proyecto fuera del árbol del repositorio | `--raiz <repo>` |
| Aviso de versión de BMAD no probada (ESP-07) | BMAD fuera de 4.x / 6.11–6.12 | revisar inventario con el equipo; `probar_paquete.py`; modo degradado |
| ESP-08: carpeta del proyecto dentro de BMAD | proyecto creado en `_bmad-output/` u otra carpeta BMAD | mover la carpeta del proyecto fuera |
| INS-01: falta un módulo | dependencia no instalada | `pip install pyyaml python-docx openpyxl` |
| INS-04: skill duplicada | plugin y copia manual a la vez | dejar una sola instalación |
| No aparece el resumen al abrir la sesión | copia manual, Hermes, o `estado.json` a más de 2 niveles | abrir la sesión cerca del proyecto o correr `/pm-sanidad` |
| Hermes no encuentra los scripts | ruta de plugin usada fuera de Claude Code | usar `~/.hermes/skills/<skill>/scripts/` o la ruta de `external_dirs` |
| Un subagente "pregunta" en su respuesta | diseño: los subagentes no pueden preguntar | el orquestador presenta las preguntas del bloque de retorno |
| Exportar `.docx`/`.xlsx` falla | faltan `python-docx` u `openpyxl` | instalarlos o usar `integraciones.export=skills-office` |
