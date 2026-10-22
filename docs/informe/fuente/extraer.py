"""Extrae de la documentación de pm-method las tablas y fichas que usa el Informe 2.

Fuente única: la raíz del repositorio pm-method (por defecto ../../.. desde esta carpeta; README, SPEC, compatibilidad.json, docs/, agents/).
Salida: data.json = narrativa.json (texto propio del informe) + estructuras extraídas literalmente.
Volver a ejecutar cuando cambie el paquete:  python3 extraer.py && python3 build_html.py && node build_pptx.js
Las cifras del paquete (skills, agentes, hooks, registros, códigos de sanidad, guías, pasos, diapositivas del webinar…)
se cuentan en el repositorio y quedan en data.json["x"]["cifras"]; el texto propio de narrativa.json las cita con
marcadores {{clave}} que se completan aquí (un marcador desconocido detiene la extracción).
"""
import json, re, pathlib, subprocess, os, sys

BASE = pathlib.Path(os.environ.get("PM_METHOD", pathlib.Path(__file__).resolve().parents[3]))
AQUI = pathlib.Path(__file__).resolve().parent
MMDC = os.environ.get("MMDC", "mmdc")
PUPPETEER = os.environ.get("PUPPETEER_CFG", "")  # opcional: JSON de puppeteer (p. ej. executablePath de Chromium)


def leer(p):
    return (BASE / p).read_text(encoding="utf-8")


# ---------- utilidades de Markdown ----------
def seccion(texto, patron):
    """Devuelve el bloque que empieza en el encabezado que coincide con `patron` hasta el próximo de nivel ≤."""
    lineas = texto.split("\n")
    for i, l in enumerate(lineas):
        m = re.match(r"^(#+)\s+(.*)$", l)
        if m and re.search(patron, m.group(2)):
            nivel = len(m.group(1))
            fin = len(lineas)
            dentro_code = False
            for j in range(i + 1, len(lineas)):
                if lineas[j].lstrip().startswith("```"):
                    dentro_code = not dentro_code
                m2 = re.match(r"^(#+)\s", lineas[j])
                if m2 and not dentro_code and len(m2.group(1)) <= nivel:
                    fin = j
                    break
            return re.sub(r"\n\s*-{3,}\s*$", "", "\n".join(lineas[i + 1:fin]).rstrip())
    raise KeyError(patron)


def celdas(linea):
    s = linea.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    partes, cur, en_code, i = [], "", False, 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"; i += 2; continue
        if ch == "`":
            en_code = not en_code
        if ch == "|" and not en_code:
            partes.append(cur); cur = ""
        else:
            cur += ch
        i += 1
    partes.append(cur)
    return [p.strip() for p in partes]


def tablas(texto):
    res, actual = [], []
    for l in texto.split("\n"):
        if l.strip().startswith("|"):
            actual.append(l)
        else:
            if actual:
                res.append(actual)
                actual = []
    if actual:
        res.append(actual)
    out = []
    for t in res:
        if len(t) < 2:
            continue
        cab = celdas(t[0])
        filas = [celdas(x) for x in t[2:]]
        out.append({"cab": cab, "filas": filas})
    return out


def tabla(texto, patron, k=0):
    return tablas(seccion(texto, patron))[k]


def bloques_mermaid(texto):
    return re.findall(r"```mermaid\n(.*?)```", texto, flags=re.S)


def vinetas_campos(texto):
    """Lista de viñetas '- **Campo:** valor' (con continuación) → lista de (campo, valor_md)."""
    items, cur = [], None
    for l in texto.split("\n"):
        m = re.match(r"^- \*\*(.+?):\*\*\s?(.*)$", l)
        if m:
            cur = [m.group(1), m.group(2)]
            items.append(cur)
        elif cur is not None and (l.startswith("  ") or l.strip() == ""):
            cur[1] += "\n" + (l[2:] if l.startswith("  ") else l)
        elif cur is not None and l.strip():
            cur = None
    return [(c, v.strip()) for c, v in items]


def vinetas_campos2(texto):
    """Como vinetas_campos, pero admite también '- **Campo** (aclaración):' (CASOS-DE-USO-INTEGRACIONES)."""
    items, cur = [], None
    for l in texto.split("\n"):
        m = re.match(r"^- \*\*(.+?):\*\*\s?(.*)$", l) or re.match(r"^- \*\*([^*]+?)\*\*\s*(\(.*\)):\s?(.*)$", l)
        if m:
            cur = [m.group(1), m.group(2) if m.lastindex == 2 else (m.group(2) + " " + m.group(3)).strip()]
            items.append(cur)
        elif cur is not None and (l.startswith("  ") or l.strip() == ""):
            cur[1] += "\n" + (l[2:] if l.startswith("  ") else l)
        elif cur is not None and l.strip():
            cur = None
    return [(c, v.strip()) for c, v in items]


# ---------- extracciones ----------
SPEC = leer("SPEC.md")
README = leer("README.md")
ARQ = leer("docs/ARQUITECTURA.md")
SYNC = leer("docs/sincronizacion.md")
SAN = leer("docs/SANIDAD.md")
INTG = leer("docs/INTEGRACIONES.md")
RACI = leer("docs/RACI.md")
CAT = leer("docs/CATALOGO.md")
CU = leer("docs/CASOS-DE-USO.md")
CM = leer("docs/CASO-MAESTRO.md")
COL = leer("docs/colisiones.md")
INST = leer("docs/INSTALACION.md")
COMPAT = json.loads(leer("compatibilidad.json"))

D = json.loads((AQUI / "narrativa.json").read_text(encoding="utf-8"))
X = {}

# Arquitectura
X["capas"] = tabla(ARQ, r"^2\. Capas")
X["precedencia"] = tabla(ARQ, r"^3\. Precedencia")
X["opciones_agentes"] = tabla(ARQ, r"^4\.1 Opciones")
X["reparto_subagentes"] = tabla(ARQ, r"^4\.2 Reparto")
X["reglas_subagentes_md"] = seccion(ARQ, r"^4\.3 Reglas").strip()
X["retorno"] = re.search(r"```\n(## Retorno.*?)```", seccion(ARQ, r"^4\.4 Protocolo"), re.S).group(1).strip()
X["hermes_equivalencias"] = tabla(ARQ, r"^4\.5 Correspondencia")
X["scripts_arq"] = tabla(ARQ, r"^5\. Herramientas")
X["comandos_arq"] = tabla(ARQ, r"^6\. Comandos")
X["carga"] = tabla(ARQ, r"^7\. Carga progresiva")
X["evaluacion"] = tabla(ARQ, r"^8\.3 Evaluación")

# Sincronización
X["sync_opciones"] = tabla(SYNC, r"^2\. Opciones")
X["sync_duenos"] = tabla(SYNC, r"^Dueño de cada dato")
X["spec_index"] = tabla(SYNC, r"^4\.2 El contrato")
X["handoff"] = tabla(SYNC, r"^5\. Sentido inverso")
X["verificar_tipos"] = tabla(SYNC, r"^6\. Verificación")
X["ids"] = tabla(SYNC, r"^7\. Estabilidad")
X["lee_escribe"] = tabla(SYNC, r"^8\. Qué lee")
X["fallas"] = tabla(SYNC, r"^10\. Modos de falla")
X["mapeo_ciclo_md"] = re.search(r"- \*\*Mapeo de ciclo de vida\*\*: (.*?)\n\n", SPEC + "\n\n", re.S).group(1).replace("\n  ", " ")

# Sanidad
X["controles"] = tabla(SAN, r"^1\. Resumen de los controles")
X["codigos"] = tabla(SAN, r"^2\.1 Familias")
_fam = []
for _f in X["codigos"]["filas"]:
    if _f[0].startswith("**") and not _f[1].strip() and "·" in _f[0]:   # fila de familia: "**CAM · …**" (con nota opcional)
        _fam.append(re.match(r"\*\*([A-Z]+) ·", _f[0]).group(1))
        nota = " ".join(c for c in _f[1:] if c.strip())
        _f[:] = [_f[0] + (" — " + nota if nota else "")] + [""] * (len(_f) - 1)
def _n_codigos(c):
    c = c.replace("*", "").strip()
    m = re.match(r"^([A-Z]+)-(\d+)\s*(?:…|\.\.\.|/)\s*(?:[A-Z]+-)?(\d+)$", c)
    return int(m.group(3)) - int(m.group(2)) + 1 if m else (1 if re.match(r"^[A-Z]+-\d+$", c) else 0)
_cods = [f for f in X["codigos"]["filas"] if f[1].strip()]
X["codigos_familias"] = _fam
X["codigos_n"] = sum(_n_codigos(f[0]) for f in _cods)
assert all(_n_codigos(f[0]) for f in _cods), [f[0] for f in _cods if not _n_codigos(f[0])]
X["guardian"] = tabla(SAN, r"^3\.1 `guardian\.py`", 0)
X["guardian_pruebas"] = tabla(SAN, r"^3\.1 `guardian\.py`", 1)
X["evolucion_error"] = tabla(SAN, r"^2\.2 Ejemplos")
X["semanal"] = tabla(SAN, r"^9\.3 Semanal")
X["limitaciones"] = tabla(SAN, r"^10\. Limitaciones")
X["mant_bmad_md"] = seccion(SAN, r"^9\.1 Después de actualizar BMAD").strip()
X["mant_paquete_md"] = seccion(SAN, r"^9\.2 Después de cambiar").strip()
X["validador_md"] = seccion(SAN, r"^6\. Validador").strip()
X["pruebas_md"] = seccion(SAN, r"^7\. Pruebas de regresión").strip()
X["regla_puerta_md"] = seccion(SAN, r"^4\. Regla de puerta").strip()
X["hermes_sin_hooks_md"] = seccion(SAN, r"^8\. Hermes Agent").strip()

# Integraciones y dependencias
X["dependencias"] = tabla(INTG, r"^1\. Dependencias")
X["decisiones_integracion"] = tabla(INTG, r"^2\. Decisiones de integración")
X["contratos"] = tabla(INTG, r"^3\. Contrato")
X["checklist_integracion_md"] = seccion(INTG, r"^5\. Cómo agregar").strip()

# Instalación
X["requisitos"] = tabla(INST, r"^1\. Requisitos")
X["capacidades_mcp"] = tabla(INST, r"^Paso 2: declarar")
X["rutas_scripts"] = tabla(INST, r"^7\.1 Ubicación")
X["verificacion"] = tabla(INST, r"^8\. Verificación")
X["hooks_inst"] = tabla(INST, r"^9\. Hooks")
X["problemas"] = tabla(INST, r"^12\. Solución")
for k, pat in [("gh_publicar", r"^0\.2 Publicar"), ("gh_claude", r"^0\.3 Claude Code"), ("gh_hermes", r"^0\.5 Hermes"),
               ("gh_credenciales", r"^0\.1 Credenciales"), ("gh_actualizar", r"^0\.4 Actualizar"), ("gh_intro", r"^0\. Instalación desde GitHub"),
               ("req_windows", r"^1\.2 Windows"), ("req_macos", r"^1\.3 macOS"), ("req_linux", r"^1\.4 Linux"),
               ("bmad_instalar", r"^4\.1 Instalar BMAD"), ("bmad_detectar", r"^4\.2 Detectar BMAD"), ("bmad_compat", r"^4\.3 Compatibilidad"),
               ("python_dep", r"^5\. Dependencias Python"), ("mcp_paso1", r"^Paso 1: conectar"), ("mcp_paso2", r"^Paso 2: declarar"),
               ("skills_ext", r"^6\.1 Skills externas"), ("hooks_md", r"^9\. Hooks"),
               ("local_plugin", r"^2\.1 Como plugin"), ("local_copia", r"^2\.2 Copia manual"), ("hermes_local", r"^3\. Instalación en Hermes"),
               ("bmad_inst", r"^4\. BMAD en el repositorio"), ("config_proyecto", r"^7\.2 Crear un proyecto"),
               ("config_tolerancias", r"^7\.3 Umbrales"), ("config_settings", r"^7\.4 Settings"), ("config_orq", r"^7\.5 Orquestador"),
               ("actualizacion", r"^10\. Actualización"), ("desinstalacion", r"^11\. Desinstalación"), ("cowork", r"^2\.3 Cowork")]:
    X[k + "_md"] = seccion(INST, pat).strip()

# Instalación v2.1: tablas nuevas
X["inst_recorrido"] = tabla(INST, r"^Recorrido de punta a punta")
GUI = leer("docs/guias/README.md")
X["guias"] = tablas(GUI)[0]
X["guias"]["filas"] = [[re.sub(r"\[(.*?)\]\(.*?\)", r"\1", c) for c in f] for f in X["guias"]["filas"]]
X["guias_leer"] = tabla(GUI, r"^Cómo usar las guías")
X["credenciales"] = tabla(INST, r"^0\.7 Claves")
X["orca_inst"] = tabla(INST, r"^0\.8 Orca")
X["credenciales_md"] = seccion(INST, r"^0\.7 Claves").split("\n", 1)[1].strip()
X["orca_md"] = seccion(INST, r"^0\.8 Orca").split("\n", 1)[1].strip()
X["inst_requisitos_so"] = tabla(INST, r"^1\.1 Lista de comprobación")
X["bmad_opciones"] = tabla(INST, r"^4\.1 Instalar BMAD")
X["python_paquetes"] = tabla(INST, r"^5\. Dependencias Python")
X["mcp_ejemplos"] = tabla(INST, r"^Paso 1: conectar")
X["skills_externas"] = tabla(INST, r"^6\.1 Skills externas")
X["herramientas_sistema"] = tabla(INST, r"^6\.2 Herramientas opcionales")
X["ins_esperados"] = tabla(INST, r"^8\. Verificación", 1)

# Documentos nuevos de la versión 2.1
RES = leer("docs/RESUMEN-EJECUTIVO.md")
IDXD = leer("docs/INDICE.md")
DEP = leer("docs/DEPENDENCIAS.md")
PRU = leer("docs/PRUEBAS.md")
CUI = leer("docs/CASOS-DE-USO-INTEGRACIONES.md")
CHL = leer("CHANGELOG.md")
CLA = leer("CLAUDE.md")

# Resumen ejecutivo
X["re_lema"] = [l for l in RES.split("\n") if l.startswith("**")][0].strip("*")
X["re_frase_md"] = seccion(RES, r"^1\. La propuesta").strip()
X["re_problema"] = tabla(RES, r"^2\. El problema")
X["re_capacidades"] = tabla(RES, r"^3\. Qué ofrece")
X["re_valor"] = [re.sub(r"^\d+\.\s*", "", b).replace("\n   ", " ").strip() for b in re.split(r"\n(?=\d+\. )", seccion(RES, r"^4\. Valor diferencial").strip())]
X["re_para_quien"] = tabla(RES, r"^5\. Para quién")
X["re_evidencia"] = tabla(RES, r"^6\. Evidencia")
X["re_limites"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(RES, r"^7\. Límites").strip())]
X["re_empezar_md"] = seccion(RES, r"^8\. Cómo empezar").strip()

# Índice de documentación y pruebas
X["idx_rutas"] = tabla(IDXD, r"^1\. Rutas de lectura")
X["idx_docs"] = tabla(IDXD, r"^2\. Documentos")
X["idx_diagramas"] = tabla(IDXD, r"^3\. Diagramas")
X["idx_pruebas"] = tabla(IDXD, r"^4\. Pruebas y evidencia")
X["idx_componentes"] = tabla(IDXD, r"^5\. Componentes del paquete")
X["idx_pendientes"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(IDXD, r"^6\. Pendientes").strip())]

# Dependencias
X["dep_convenciones_md"] = re.search(r"> Convenciones\n(.*?)\n\n", DEP, re.S).group(1)
X["dep_resumen"] = tabla(DEP, r"^0\. Resumen")
X["dep_node_md"] = seccion(DEP, r"^0\. Resumen").split("**Node.js: versión mínima efectiva.**")[1].strip()
X["dep_clientes"] = tabla(DEP, r"^1\.1 Cliente")
X["dep_clientes_nota_md"] = seccion(DEP, r"^1\.1 Cliente").split("\n\n")[-1].strip() if False else [b for b in seccion(DEP, r"^1\.1 Cliente").strip().split("\n\n") if b.startswith("Documentación")][0]
X["dep_base"] = tabla(DEP, r"^1\.2 Herramientas de base")
X["dep_python"] = tabla(DEP, r"^2\. Paquetes Python")
X["dep_opcionales"] = tabla(DEP, r"^3\. Herramientas opcionales")
X["dep_bmad"] = tabla(DEP, r"^4\.1 El paquete")
X["dep_skills"] = tabla(DEP, r"^4\.2 Skills externas")
X["dep_drawio"] = tabla(DEP, r"^4\.3 draw\.io")
X["dep_mcp"] = tabla(DEP, r"^5\. Conectores MCP")
X["dep_declara"] = tabla(DEP, r"^6\. Dónde se declara")
X["dep_ver_repos"] = tabla(DEP, r"^7\.1 Repositorios")
X["dep_ver_npm"] = tabla(DEP, r"^7\.2 Paquetes npm")
X["dep_ver_pypi"] = tabla(DEP, r"^7\.3 Paquetes PyPI")
X["dep_no_verificadas"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(DEP, r"^7\.4 No verificadas").strip())]
X["dep_ver_intro_md"] = seccion(DEP, r"^7\. Verificación").strip().split("\n\n")[0]

# Pruebas
X["pru_niveles"] = tabla(PRU, r"^1\. Niveles")
X["pru_regresion"] = tabla(PRU, r"^2\. Regresión")
X["pru_regresion_res_md"] = [l for l in seccion(PRU, r"^2\. Regresión").split("\n") if l.startswith("Resultado")][0]
X["pru_vivo_md"] = seccion(PRU, r"^3\. Pruebas en vivo").split("### 3.1")[0].strip()
# la tabla de §3.1 está partida por una línea en blanco: se unen todas sus filas
_ls = [l for l in seccion(PRU, r"^3\.1 Resultados").split("\n") if l.strip().startswith("|")]
X["pru_resultados"] = {"cab": celdas(_ls[0]), "filas": [celdas(l) for l in _ls[1:] if not re.match(r"^\|[\s|:-]+\|$", l.strip())]}
X["pru_placeholders"] = sorted(set(re.findall(r"RESULTADO_[A-Z]+", PRU)))
X["pru_resultados_nota_md"] = seccion(PRU, r"^3\.1 Resultados").strip().split("\n\n")[-1]
X["pru_casos"] = tabla(PRU, r"^\d\. Casos de uso documentados")
X["pru_aceptacion"] = [re.sub(r"^\d+\. \[ \] ", "", b.split("\n\n")[0]).replace("\n   ", " ").strip() for b in re.split(r"\n(?=\d+\. \[)", seccion(PRU, r"^\d\. Prueba de aceptación").strip()) if re.match(r"^\d+\. \[", b)]
X["pru_aceptacion_nota_md"] = seccion(PRU, r"^\d\. Prueba de aceptación").strip().split("\n\n")[-1]
X["pru_suite_enrut"] = tabla(leer("docs/evaluacion/resultados/2026-10-17-suite-v2.1.md"), r"^Enrutamiento")
X["pru_resultados_archivos"] = sorted(p.name for p in (BASE / "docs/evaluacion/resultados").iterdir())

# Puertas de la junta
PUE = leer("docs/PUERTAS.md")
X["pue_intro"] = PUE.split("\n\n")[1].replace("\n", " ").strip()
X["pue_componentes"] = tabla(PUE, r"^1\. Ciclo de vida integrado")
_s2 = seccion(PUE, r"^2\. Cómo se verifica").split("```")[-1].strip()
X["pue_capas_intro"] = _s2.split("\n\n")[0].replace("\n", " ")
X["pue_capas"] = [re.sub(r"^\d+\.\s*", "", b).replace("\n   ", " ").strip() for b in re.split(r"\n(?=\d+\. )", _s2.split("\n\n")[1])]
X["pue_verificar"] = next(b for b in _s2.split("\n\n") if b.startswith("`puertas.py verificar")).replace("\n", " ")
X["pue_severidades"] = next(b for b in _s2.split("\n\n") if b.startswith("Severidades:")).replace("\n", " ")
_cf = seccion(PUE, r"^3\.1 Condiciones formales").strip()
X["pue_condiciones_intro"] = _cf.split("\n\n")[0].replace("\n", " ")
X["pue_condiciones"] = [re.sub(r"^\d+\.\s*", "", b).replace("\n   ", " ").strip() for b in re.split(r"\n(?=\d+\. )", _cf.split("\n\n")[1])]
X["pue_condiciones_ejemplo"] = _cf.split("\n\n")[-1].replace("\n", " ")
X["pue_controles"] = tabla(PUE, r"^3\. Controles automáticos")
X["pue_criterios_exito"] = next(b for b in seccion(PUE, r"^3\. Controles automáticos").strip().split("\n\n") if b.startswith("Los criterios de éxito")).replace("\n", " ")
X["pue_bmad"] = tabla(PUE, r"^4\. Controles de BMAD")
X["pue_bmad_titulo"] = re.search(r"^## 4\. (.+)$", PUE, re.M).group(1)
X["pue_bmad_nota"] = seccion(PUE, r"^4\. Controles de BMAD").strip().split("\n\n")[-1].replace("\n", " ")
X["pue_informes"] = tabla(PUE, r"^5\. Insumo")
X["pue_informes_intro"] = seccion(PUE, r"^5\. Insumo").strip().split("\n\n")[0].replace("\n", " ")
X["pue_comandos"] = re.search(r"```bash\n(.*?)```", seccion(PUE, r"^6\. Comandos"), re.S).group(1).rstrip()

# Plan de piloto
PIL = leer("docs/PILOTO.md")
X["pil_intro"] = PIL.split("\n\n")[1].replace("\n", " ").strip()
X["pil_preguntas"] = tabla(PIL, r"^1\. Objetivo")
X["pil_alcance"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(PIL, r"^2\. Alcance").strip())]
X["pil_fases"] = tabla(PIL, r"^3\. Fases")
X["pil_metricas"] = tabla(PIL, r"^4\. Métricas", 0)
X["pil_registro"] = tabla(PIL, r"^4\. Métricas", 1)
X["pil_rubrica_intro"] = seccion(PIL, r"^5\. Rúbrica").strip().split("\n\n")[0].replace("\n", " ")
X["pil_rubrica"] = tabla(PIL, r"^5\. Rúbrica")
X["pil_rubrica_res"] = seccion(PIL, r"^5\. Rúbrica").strip().split("\n\n")[-1].replace("\n", " ")
_us = seccion(PIL, r"^6\. Prueba de usabilidad").strip()
X["pil_usab_intro"] = _us.split("\n\n")[0].replace("\n", " ")
X["pil_usab_tareas"] = [re.sub(r"^\d+\.\s*", "", l).strip() for l in _us.split("\n") if re.match(r"^\d+\. ", l)]
X["pil_usab_medir"] = _us.split("\n\n")[-1].replace("\n", " ")
X["pil_riesgos"] = tabla(PIL, r"^7\. Riesgos")
X["pil_criterios"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(PIL, r"^8\. Criterios").strip().split("\n\n")[0])]
X["pil_cierre"] = seccion(PIL, r"^8\. Criterios").strip().split("\n\n")[-1].replace("\n", " ")

# Casos de uso de integraciones
X["cui_intro_md"] = CUI.split("\n\n")[1].strip()
X["cui_evidencia_md"] = [b for b in CUI.split("\n\n") if b.startswith("Regla de evidencia")][0]
X["cui_estados"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", re.search(r"Estados de verificación usados en todo el documento:\n(.*?)\n\n", CUI, re.S).group(1))]
X["cui_repos"] = tabla(CUI, r"^Qué repo cubre")
X["cui_ejemplos"] = tabla(CUI, r"^Proyecto de prueba")
X["cui_matriz"] = tabla(CUI, r"^Matriz de cierre")
X["cui_transversal_md"] = seccion(CUI, r"^Matriz de cierre").strip().split("\n\n")[-1]
cui_casos = []
for m in re.finditer(r"^## (Caso (\d+) · (.+))$", CUI, re.M):
    cuerpo = seccion(CUI, "^" + re.escape(m.group(1)) + "$")
    intro = cuerpo.split("\n### ")[0].strip()
    subs = []
    for m2 in re.finditer(r"^### (\d+\.\d+) (.+)$", cuerpo, re.M):
        b = seccion(cuerpo, "^" + re.escape(m2.group(1)) + " ")
        subs.append({"id": m2.group(1), "titulo": m2.group(2), "campos": vinetas_campos2(b)})
    campos_intro = vinetas_campos2(intro) if not subs else []
    intro_md = intro if subs else ""
    cui_casos.append({"n": int(m.group(2)), "titulo": m.group(3), "intro_md": intro_md, "subs": subs, "campos": campos_intro})
X["cui_casos"] = cui_casos

# Novedades 2.1 (CHANGELOG)
s21 = seccion(CHL, r"^2\.1\.0")
X["chl_lema"] = re.search(r"2\.1\.0 · (\S+) — (.+)", CHL).group(2)
X["chl_intro"] = s21.strip().split("\n\n")[0].replace("\n", " ")
nov = []
for m in re.finditer(r"^### (.+)$", s21, re.M):
    b = seccion(s21, "^" + re.escape(m.group(1)) + "$").strip()
    items = [re.sub(r"^- ", "", x).replace("\n  ", " ").strip() for x in re.split(r"\n(?=- )", b) if x.startswith("- ")]
    nov.append({"t": m.group(1), "items": items})
X["chl_grupos"] = nov
X["chl_v20_md"] = seccion(CHL, r"^2\.0\.0").strip().replace("\n", " ")

# Novedades 2.2 (CHANGELOG): lema, introducción y grupos (la sección "Controles permanentes" trae un párrafo propio)
s22 = seccion(CHL, r"^2\.2\.0")
X["chl22_lema"] = re.search(r"2\.2\.0 · (\S+) — (.+)", CHL).group(2)
X["chl22_intro"] = s22.strip().split("\n\n")[0].replace("\n", " ")
nov22 = []
for m in re.finditer(r"^### (.+)$", s22, re.M):
    b = seccion(s22, "^" + re.escape(m.group(1)) + "$").strip()
    intro = b.split("\n- ")[0].strip() if not b.startswith("- ") else ""
    items = [re.sub(r"^- ", "", x).replace("\n  ", " ").strip() for x in re.split(r"\n(?=- )", b) if x.startswith("- ")]
    nov22.append({"t": m.group(1), "intro": intro.replace("\n", " "), "items": items})
X["chl22_grupos"] = nov22

# Guías E2E: tabla "Del uso único al control continuo" de cada guía, pasos (con 5b, 6b y los de la variante, sin contar
# el paso 0 de preparación) y fuentes de identificación (E2E-1)
GUIAS_E2E = {"E2E-1": "docs/guias/E2E-1-riesgos.md", "E2E-2": "docs/guias/E2E-2-alcance-roadmap.md",
             "E2E-3": "docs/guias/E2E-3-interesados-okr-avance.md", "E2E-4": "docs/guias/E2E-4-producto-bmad.md",
             "E2E-5": "docs/guias/E2E-5-idea-a-proyecto.md"}
X["guias_controles"] = {}
X["guias_pasos"] = {}
for g, ruta in GUIAS_E2E.items():
    txt = leer(ruta)
    X["guias_controles"][g] = tabla(txt, r"^Del uso único al control continuo")
    # un paso partido en «6a» y «6b» (sin «6») cuenta una vez; «6b» junto a un «6» cuenta aparte (criterio de guias/README)
    _ps = re.findall(r"^#{2,3} Paso (\d+)([a-z]?) · ", txt, re.M)
    _base = {n for n, l in _ps if not l}
    X["guias_pasos"][g] = len({n for n, l in _ps}) + sum(1 for n, l in _ps if l and n in _base)
X["g1_fuentes"] = tabla(leer(GUIAS_E2E["E2E-1"]), r"^Cobertura de fuentes")

# Guías E2E: indicadores (imagen + lectura), clases y pasos con los códigos que muestran
X["guias_indicadores"], X["guias_clases"], X["guias_codigos_pasos"], X["guias_titulos"] = {}, {}, {}, {}
for g, ruta in GUIAS_E2E.items():
    txt = leer(ruta)
    X["guias_titulos"][g] = re.match(r"^# Guía E2E-\d · (.+)$", txt.split("\n")[0]).group(1)
    ind = seccion(txt, r"^Indicadores que vas a ver")
    X["guias_indicadores"][g] = [{"img": m.group(2), "alt": m.group(1), "lectura": m.group(3).replace("\n", " ").strip()}
                                 for m in re.finditer(r"!\[([^\]]*)\]\(img/([^)]+\.png)\)\n(.*?)(?=\n\n|\n!\[|\Z)", ind, re.S)]
    faltan = [it["img"] for it in X["guias_indicadores"][g] if not (BASE / "docs/guias/img" / it["img"]).exists()]
    if faltan:   # una guía que cita una imagen todavía no generada: se omite con aviso (volver a extraer cuando exista)
        print(f"AVISO: {g} cita imágenes que no están en docs/guias/img/: {', '.join(faltan)} (se omiten)", file=sys.stderr)
        X["guias_indicadores"][g] = [it for it in X["guias_indicadores"][g] if it["img"] not in faltan]
    X["guias_clases"][g] = tabla(txt, r"^Clases")
    # en qué pasos aparece cada código de control (para la tabla «dónde se ve»)
    pasos_cod = {}
    for m in re.finditer(r"^#{2,3} Paso (\d+[a-z]?) · .*$", txt, re.M):
        fin = re.search(r"^#{2,3} (?:Paso \d|Reporte|Representaciones|Lista de|Siguiente|Qué cambia|Variante)", txt[m.end():], re.M)
        cuerpo = txt[m.end(): m.end() + fin.start()] if fin else txt[m.end():]
        for c in set(re.findall(r"\b(?:S-)?(?:[A-Z]{3}-\d{2}|[GPEIXCL]-\d{2})\b", cuerpo)):
            pasos_cod.setdefault(c, []).append(m.group(1))
    X["guias_codigos_pasos"][g] = pasos_cod
X["guias_imagenes"] = sorted({f for t in GUIAS_E2E.values() for f in re.findall(r"img/([a-z0-9-]+\.png)", leer(t))})
X["guias_evidencia"] = re.search(r"Escribe `salida-g1\.md` … `salida-g(\d)\.md` \(cada comando con su salida\) y las (\d+) imágenes", GUI).groups()

# Salidas reales de la evidencia (E2E-5): inversion.py y estado.py contexto
_g5 = leer("docs/guias/evidencia/salida-g5.md")
_blq = re.findall(r"```\n(\$ [^\n]*\n.*?)```", _g5, re.S)
_inv = next(b for b in _blq if "inversion.py" in b.split("\n")[0] and "flujos-opciones.csv" in b.split("\n")[0])
X["ev_inversion"] = "\n".join(_inv.split("\n")[:8]).replace("$PLUGIN/skills/pm-caso-de-negocio/scripts/", "")
X["ev_inversion_lectura"] = next(b for b in _blq if b.startswith("$ (lectura de pm-caso-de-negocio, de inversion.py --json)") and "159.213" in b).strip().split("\n")[1:]
X["ev_contexto"] = [b.strip().replace("$EST/", "") for b in _blq if " contexto --corte " in b.split("\n")[0]]

# Mapas e inversión: ayuda real de los scripts (verificada al extraer)
def ayuda(rel):
    r = subprocess.run([sys.executable, str(BASE / rel), "--help"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, (rel, r.stderr)
    return r.stdout
_inv_help = ayuda("skills/pm-caso-de-negocio/scripts/inversion.py")
X["inversion_formulas"] = [re.sub(r"\s+", " ", b.replace("\n", " ")).strip() for b in re.split(r"\n- ", _inv_help.split("Fórmulas")[1].split("Uso / Usage")[0])[1:]]
X["inversion_uso"] = re.search(r"Uso / Usage:\n\s*(.+)", _inv_help).group(1).strip()
_map_help = ayuda("skills/pm-mapas-estrategicos/scripts/mapas.py")
_mu = []
for l in _map_help.split("Uso / Usage (--proyecto va ANTES del tipo de mapa):")[1].split("'semilla'")[0].strip().split("\n"):
    if l.strip().startswith("mapas.py"):
        _mu.append(l.strip())
    elif l.strip() and _mu:
        _mu[-1] += " " + l.strip()
X["mapas_uso"] = [re.sub(r"\s{2,}", " ", x) for x in _mu]
X["mapas_fuente"] = re.sub(r"\s+", " ", _map_help.split("Fuente de verdad:")[1].split("Uso / Usage")[0]).strip()

# CHANGELOG 2.3.0: lema, introducción, cifras y grupos
s23 = seccion(CHL, r"^2\.3\.0")
X["chl23_lema"] = re.search(r"2\.3\.0 · (\S+) — (.+)", CHL).group(2)
X["chl23_fecha"] = re.search(r"2\.3\.0 · (\S+) — ", CHL).group(1)
X["chl23_intro"] = s23.strip().split("\n\n")[0].replace("\n", " ")
X["chl23_cifras"] = s23.strip().split("\n\n")[1].replace("\n", " ")
nov23 = []
for m in re.finditer(r"^### (.+)$", s23, re.M):
    b = seccion(s23, "^" + re.escape(m.group(1)) + "$").strip()
    nov23.append({"t": m.group(1), "items": [re.sub(r"^- ", "", x).replace("\n  ", " ").strip() for x in re.split(r"\n(?=- )", b) if x.startswith("- ")]})
X["chl23_grupos"] = nov23

# CHANGELOG 2.4.0: lema, introducción, cifras y grupos (mismo formato que 2.3.0)
s24 = seccion(CHL, r"^2\.4\.0")
X["chl24_lema"] = re.search(r"2\.4\.0 · (\S+) — (.+)", CHL).group(2)
X["chl24_fecha"] = re.search(r"2\.4\.0 · (\S+) — ", CHL).group(1)
X["chl24_intro"] = s24.strip().split("\n\n")[0].replace("\n", " ")
X["chl24_cifras"] = s24.strip().split("\n\n")[1].replace("\n", " ")
X["chl24_grupos"] = []
for m in re.finditer(r"^### (.+)$", s24, re.M):
    b = seccion(s24, "^" + re.escape(m.group(1)) + "$").strip()
    X["chl24_grupos"].append({"t": m.group(1), "items": [re.sub(r"^- ", "", x).replace("\n  ", " ").strip() for x in re.split(r"\n(?=- )", b) if x.startswith("- ")]})
assert X["chl24_cifras"].startswith("En cifras"), X["chl24_cifras"][:60]

# Todas las figuras de las guías E2E (imagen, guía, paso, texto alternativo y lectura), no solo las de «Indicadores»
X["guias_figuras"] = {}
for g, ruta in GUIAS_E2E.items():
    txt = leer(ruta)
    pasos = [(m.start(), m.group(1)) for m in re.finditer(r"^#{2,3} Paso (\d+[a-z]?) · ", txt, re.M)]
    for m in re.finditer(r"!\[([^\]]*)\]\(img/([^)]+\.png)\)\n(.*?)(?=\n\n|\n!\[|\Z)", txt, re.S):
        paso = [p for pos, p in pasos if pos < m.start()]
        if m.group(2) in X["guias_figuras"]:   # citada en «Indicadores» y luego en un paso: se completa el paso
            if not X["guias_figuras"][m.group(2)]["paso"] and paso:
                X["guias_figuras"][m.group(2)]["paso"] = paso[-1]
            continue
        if not (BASE / "docs/guias/img" / m.group(2)).exists():
            continue
        X["guias_figuras"][m.group(2)] = {"img": m.group(2), "guia": g, "paso": paso[-1] if paso else "", "alt": m.group(1),
                                          "lectura": m.group(3).replace("\n", " ").strip()}

# Salidas reales de la evidencia para las capacidades de 2.4 (cada bloque con su comando; rutas acortadas)
_EVB = {g: re.findall(r"```\n(\$ [^\n]*\n.*?)```", leer(f"docs/guias/evidencia/salida-g{g[-1]}.md"), re.S) for g in GUIAS_E2E}
def _corto(b):
    b = re.sub(r"\$PLUGIN/skills/[a-z-]+/scripts/", "", b.strip())
    for k, v in (("$EST/", ""), ("$IN ", "interesados.py "), ("$PAQ ", "paquete.py "), ("python3 ", ""), ("--proyecto gestion ", ""),
                 ('HOME="$(mktemp -d)" ', ""), ("gestion/03-control/reuniones/", ""), ("gestion/03-control/reportes/", ""), ("gestion/exportados/", "")):
        b = b.replace(k, v)
    return b
def _ev(g, patron, k=0):
    hs = [b for b in _EVB[g] if re.search(patron, b.split("\n")[0])]
    assert len(hs) > k, f"evidencia {g}: no hay bloque cuyo comando coincida con {patron}"
    return _corto(hs[k])
EV = {
    "opciones": _ev("E2E-1", r"riesgos\.py --proyecto gestion opciones$"),
    "elegir": _ev("E2E-1", r"opciones --riesgo R-003 --elegir O4"),
    "radar_linea": _ev("E2E-3", r"radar --corte 2027-01-08 --linea"),
    "radar": _ev("E2E-3", r"radar --corte 2027-01-08$"),
    "radar_json": _ev("E2E-3", r"radar --corte 2027-01-08 --json"),
    "briefing": _ev("E2E-3", r"briefing --para"),
    "verificar": _ev("E2E-3", r"periodo --verificar"),
    "verificar_ok": _ev("E2E-3", r"periodo --verificar", 1),
    "productos": _ev("E2E-4", r"productos --corte 2027-02-26 --alcance R1"),
    "cierre": _ev("E2E-4", r"verificar autorizar-cierre$"),
    "candidatos": _ev("E2E-3", r"extraccion\.py --proyecto gestion candidatos"),
    "registrar_no": _ev("E2E-3", r"registrar .*--confirmar CD-01,IN-01"),
    "registrar": _ev("E2E-3", r"registrar .*--confirmar CD-01,CA-01"),
    "impacto": _ev("E2E-2", r"impacto\.py --proyecto gestion analizar C-002"),
    "cpm": _ev("E2E-2", r"cpm\.py .*--estimacion"),
    "capacidad": _ev("E2E-2", r"release\.py --proyecto gestion capacidad"),
    "personas_mapa": _ev("E2E-5", r"personas mapa$"),
    "personas_prio": _ev("E2E-5", r"personas priorizacion$"),
    "lecciones_listar": _ev("E2E-4", r"lecciones\.py listar --proyecto gestion --corte 2027-02-26"),
    "lecciones_buscar": _ev("E2E-5", r"lecciones\.py buscar"),
    "auditoria": _ev("E2E-4", r"auditoria --hasta"),
    "aud_ok": _ev("E2E-4", r"verificar gestion/exportados/.*expediente"),
    "aud_falla": _ev("E2E-4", r"verificar copia-auditoria"),
}
assert "INTEGRIDAD: OK" in EV["aud_ok"] and "INTEGRIDAD: FALLA" in EV["aud_falla"] and "DIFIERE" in EV["verificar"], "evidencia 2.4: bloques inesperados"
X["ev24"] = EV
# E2E-1, paso 7: presupuesto de riesgo y reserva de gestión («Qué hace el sistema», tal cual)
_p7 = seccion(leer(GUIAS_E2E["E2E-1"]), r"^Paso 7 · ")
X["g1_presupuesto_md"] = re.search(r"\*\*Qué hace el sistema:\*\* (.*?)(?=\n\n)", _p7, re.S).group(1).replace("\n", " ")

# CASOS-DE-USO, parte 7 (casos 50 en adelante): tabla con la capacidad, la frase verificada, la skill, la decisión y la guía
X["casos_p7_titulo"] = re.search(r"^## (Parte 7 · .+)$", CU, re.M).group(1)
X["casos_p7_intro"] = seccion(CU, r"^Parte 7 · ").strip().split("\n\n")[0].replace("\n", " ")
X["casos_p7"] = tabla(CU, r"^Parte 7 · ")

# Seguridad (docs/SEGURIDAD.md)
SEG = leer("docs/SEGURIDAD.md")
X["seg_titulo"] = SEG.split("\n")[0].lstrip("# ").strip()
X["seg_intro"] = SEG.split("\n\n")[1].replace("\n", " ").strip()
X["seg_resultado"] = tabla(SEG, r"^1\. Resultado")
X["seg_resultado_nota"] = seccion(SEG, r"^1\. Resultado").strip().split("\n\n")[-1].replace("\n", " ")
X["seg_alcance"] = tabla(SEG, r"^2\. Alcance")
X["seg_herramientas"] = tabla(SEG, r"^3\. Método")
X["seg_entorno"] = [l for l in seccion(SEG, r"^3\. Método").split("\n") if l.startswith("Entorno:")][0]
X["seg_amenazas"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(SEG, r"^4\. Modelo").strip())]
X["seg_hallazgos"] = []
for sev in ("Media", "Baja", "Informativa"):
    for m in re.finditer(r"^\*\*(SEG-\d+) · (.+?) · (.+?)\*\*$", seccion(SEG, r"^" + sev), re.M):
        X["seg_hallazgos"].append([m.group(1), sev.replace("Informativa", "Informativa"), m.group(2), m.group(3)])
X["seg_bien"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(SEG, r"^7\. Lo que ya está bien").strip())]
X["seg_practicas"] = [re.sub(r"^\d+\.\s*", "", b).replace("\n   ", " ").strip() for b in re.split(r"\n(?=\d+\. )", seccion(SEG, r"^8\. Buenas prácticas").strip())]
X["seg_repetir"] = re.search(r"```bash\n(.*?)```", seccion(SEG, r"^10\. Cómo repetir"), re.S).group(1).rstrip()
assert len(X["seg_hallazgos"]) == 17, len(X["seg_hallazgos"])

# Docker (docs/DOCKER.md)
DOC = leer("docs/DOCKER.md")
X["dock_intro"] = DOC.split("\n\n")[1].replace("\n", " ").strip()
X["dock_cuando"] = tabla(DOC, r"^1\. Cuándo conviene")
X["dock_incluye"] = tabla(DOC, r"^2\. Qué incluye", 0)
X["dock_archivos"] = tabla(DOC, r"^2\. Qué incluye", 1)
X["dock_construir"] = re.search(r"```bash\n(.*?)```", seccion(DOC, r"^4\. Construir"), re.S).group(1).rstrip()
X["dock_usar"] = re.search(r"```bash\n(.*?)```", seccion(DOC, r"^5\.1 Abrir una shell"), re.S).group(1).rstrip()
X["dock_pruebas"] = re.search(r"```bash\n(.*?)```", seccion(DOC, r"^5\.5 Pruebas"), re.S).group(1).rstrip()
_v = seccion(DOC, r"^10\. Verificación registrada").strip()
X["dock_verif_intro"] = _v.split("\n\n")[0].replace("\n", " ")
X["dock_verif"] = tablas(_v)[0]
X["dock_verif_no"] = _v.split("\n\n")[-1].replace("\n", " ")
X["dock_seguridad"] = tabla(DOC, r"^7\. Seguridad del contenedor")
X["dock_limitaciones"] = [re.sub(r"^- ", "", b.split("\n\n")[0]).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(DOC, r"^9\. Limitaciones").strip()) if b.startswith("- ")]

# Pruebas: recorridos E2E, contexto, integración cruzada y Python 3.9
X["pru_e2e"] = tabla(PRU, r"^2\.1 Recorridos E2E")
X["pru_e2e_res"] = re.search(r"Resultado al\s+(\d{4}-\d{2}-\d{2}): \*\*(.+?)\*\*,? (.+?)\.", seccion(PRU, r"^2\.1 Recorridos E2E").replace("\n", " ")).groups()
X["pru_contexto"] = tabla(PRU, r"^2\.2 Control del contexto")
X["pru_contexto_intro"] = seccion(PRU, r"^2\.2 Control del contexto").strip().split("\n\n")[0].replace("\n", " ")
X["pru_contexto_vivo"] = [b for b in seccion(PRU, r"^2\.2 Control del contexto").strip().split("\n\n") if b.startswith("En vivo")][0].replace("\n", " ")
_i = seccion(PRU, r"^2\.3 Integración cruzada").strip()
X["pru_integ_intro"] = _i.split("\n\n")[0].replace("\n", " ")
X["pru_integ"] = tabla(PRU, r"^2\.3 Integración cruzada")
X["pru_integ_res"] = [b for b in _i.split("\n\n") if b.startswith("Resultado al")][0].replace("\n", " ")
X["pru_integ_cmds"] = re.search(r"```bash\n(.*?)```", _i, re.S).group(1).rstrip()
_p9 = seccion(PRU, r"^2\.4 Compatibilidad").strip()
X["pru_py39_intro"] = _p9.split("\n\n")[0].replace("\n", " ")
X["pru_py39_cmds"] = re.search(r"```bash\n(.*?)```", _p9, re.S).group(1).rstrip()
X["pru_py39_res"] = _p9.split("\n\n")[-1].replace("\n", " ")
X["pru_vivo_repetir"] = seccion(PRU, r"^3\.2 Cuándo repetir").strip().split("\n\n")[-1].replace("\n", " ")

# Webinar y resumen ejecutivo
WEB = leer("docs/webinar/README.md")
X["web_intro"] = WEB.split("\n\n")[1].replace("\n", " ").strip()
X["web_casos"] = tabla(WEB, r"^Casos")
X["web_casos_nota"] = seccion(WEB, r"^Casos").strip().split("\n\n")[-1].replace("\n", " ")
X["web_agrega"] = [re.sub(r"^- ", "", b.split("\n\n")[0]).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(WEB, r"^Qué agrega el generador").strip()) if b.startswith("- ")]
X["web_estructura"] = re.search(r"```text\n(.*?)```", seccion(WEB, r"^Estructura de carpetas"), re.S).group(1).rstrip()
REX = leer("docs/resumen-ejecutivo/README.md")
X["rex_items"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", REX.split("\n## ")[0].split("\n", 1)[1].strip()) if b.startswith("- ")]
X["rex_regenerar"] = re.search(r"```bash\n(.*?)```", REX, re.S).group(1).rstrip()

# Terminología y memoria del cliente
TER = leer("docs/TERMINOLOGIA.md")
X["ter_intro"] = TER.split("\n\n")[1].replace("\n", " ").strip()
X["ter_verificacion"] = seccion(TER, r"^Cómo se verificó").strip().replace("\n", " ")
X["ter_filas"] = sum(len(tablas(seccion(TER, "^" + t))[0]["filas"]) for t in ("Gobierno", "Arranque", "Control", "Cierre"))
X["memoria_md"] = seccion(INST, r"^9\.1 Memoria").split("**Cómo prescindir")[0].strip()

# Cifras contadas en el repositorio (fuente única de los números del texto propio)
sys.path.insert(0, str(BASE / "skills/pm-estado-proyecto/scripts"))
import esquema as _esq
_skills = sorted(p for p in (BASE / "skills").iterdir() if (p / "SKILL.md").exists())
_comando = [p.name for p in _skills if re.search(r"^disable-model-invocation:\s*true", (p / "SKILL.md").read_text(encoding="utf-8"), re.M)]
_hooks = json.loads(leer("hooks/hooks.json"))["hooks"]
_web = []
for d in sorted((BASE / "docs/webinar").glob("E2E-*/diapositivas.json")):
    j = json.loads(d.read_text(encoding="utf-8"))
    _web.append({"caso": j["caso"], "clases": len(j["clases"]), "diapositivas": sum(len(c["diapositivas"]) for c in j["clases"]), "glosario": len(j.get("glosario", []))})
_tot_web = [f for f in X["web_casos"]["filas"] if f[0].startswith("**Total")][0]
assert int(re.sub(r"\D", "", _tot_web[4])) == sum(w["diapositivas"] for w in _web) and int(re.sub(r"\D", "", _tot_web[5])) == sum(w["glosario"] for w in _web), ("webinar: README y diapositivas.json no coinciden", _tot_web, _web)
_vp = subprocess.run([sys.executable, str(BASE / "scripts/validar_paquete.py")], capture_output=True, text=True, timeout=600)
_m = re.search(r"Skills: (\d+) \((\d+) invocables por el modelo, listado (\d+) caracteres\) · Agentes: (\d+)", _vp.stdout)
assert _m, _vp.stdout + _vp.stderr
if _vp.returncode != 0:   # las cifras salen igual; el aviso recuerda volver a validar antes de publicar
    print("AVISO: validar_paquete.py no dio OK:\n" + "\n".join(l for l in _vp.stdout.splitlines() if l.startswith(("ERROR", "AVISO"))), file=sys.stderr)
CIF = {
    "version": COMPAT["version"], "skills": len(_skills), "invocables": len(_skills) - len(_comando), "comandos": len(_comando),
    "agentes": len(list((BASE / "agents").glob("*.md"))), "hooks": len(_hooks), "hooks_eventos": " · ".join(_hooks),
    "registros": len(_esq.REGISTROS), "registros_base": sum(1 for r in _esq.REGISTROS.values() if not r.get("opcional")),
    "registros_opcionales": sum(1 for r in _esq.REGISTROS.values() if r.get("opcional")),
    "codigos": X["codigos_n"], "familias": len(X["codigos_familias"]), "familias_lista": ", ".join(X["codigos_familias"]),
    "guias": len(GUIAS_E2E), "pasos": sum(X["guias_pasos"].values()), "pasos_lista": ", ".join(str(v) for v in X["guias_pasos"].values()),
    "imagenes_guias": len(X["guias_imagenes"]),
    "frases": sum(1 for l in leer("docs/evaluacion/frases-enrutamiento.tsv").splitlines() if l.strip()), "web_clases": sum(w["clases"] for w in _web), "web_diapositivas": sum(w["diapositivas"] for w in _web),
    "web_glosario": sum(w["glosario"] for w in _web), "seg_hallazgos": len(X["seg_hallazgos"]),
    "listado": format(int(_m.group(3)), ",").replace(",", "."), "validar_skills": int(_m.group(1)), "validar_invocables": int(_m.group(2)),
    "validar_py39": ("verificado con intérprete 3.9" if "intérprete" in _vp.stdout else "análisis de f-strings"),
}
assert CIF["validar_skills"] == CIF["skills"] and CIF["validar_invocables"] == CIF["invocables"], CIF
assert CIF["guias_evidencia"] if False else int(X["guias_evidencia"][1]) == CIF["imagenes_guias"], ("guías: README dice", X["guias_evidencia"], "las guías citan", CIF["imagenes_guias"])
_rr = re.search(r"Resultado al (\d{4}-\d{2}-\d{2}) \(versión ([\d.]+), casos ([^)]+)\): \*\*(\d+) OK · 0 FALLO\*\* con Python ([\d.]+); con Python 3\.9, \*\*(\d+) OK · 0 FALLO\*\*", X["pru_regresion_res_md"])
_ri = re.search(r"\*\*(\d+) OK · 0 FALLO en (\d+) eslabones\*\*", X["pru_integ_res"])
_rm = re.search(r"`validar_mermaid\.py --render`: (?:\*\*)?(\d+)(?:\*\*)? bloques, 0 errores", s24)
# pasos por guía: el conteo de encabezados coincide con la tabla de docs/guias/README.md («15 pasos (el 6 en 6a y 6b)»)
_pr = {re.search(r"E2E-\d", f[0]).group(): int(re.match(r"(\d+) pasos", f[4]).group(1)) for f in X["guias"]["filas"]}
assert _pr == X["guias_pasos"], ("pasos: guias/README.md dice", _pr, "los encabezados de las guías dan", X["guias_pasos"])
assert _rr and _ri and _rm, "no se encontraron los resultados de pruebas en PRUEBAS.md / CHANGELOG"
CIF.update({"pruebas_fecha": _rr.group(1), "regresion_casos": _rr.group(3), "regresion_ok": int(_rr.group(4)), "regresion_py": _rr.group(5),
            "regresion_ok39": int(_rr.group(6)), "integ_ok": int(_ri.group(1)), "integ_eslabones": int(_ri.group(2)), "mermaid_bloques": int(_rm.group(1))})
_tam = sorted(((len((p / "SKILL.md").read_bytes()), len((p / "SKILL.md").read_text(encoding="utf-8").splitlines()), p.name) for p in _skills), reverse=True)
CIF.update({"skill_max_bytes": format(_tam[0][0], ",").replace(",", "."), "skill_max_nombre": _tam[0][2],
            "skill_max_lineas": max(t[1] for t in _tam), "knowledge_refs": len(list((BASE / "skills/pm-knowledge/references").iterdir()))})
# pruebas en vivo del 2026-10-20 (PRUEBAS §3.1)
_viv = {f[2]: f[3] for f in X["pru_resultados"]["filas"] if f[0] == "2026-10-20"}
_v1 = next(v for k, v in _viv.items() if "resumen de contexto" in k)
_v2 = next(v for k, v in _viv.items() if "95–102" in k)
_v3 = next(v for k, v in _viv.items() if "integracion" in k)
CIF.update({"vivo_contexto": re.match(r"(\d+/\d+)", _v1).group(1), "vivo_mapas": re.match(r"(\d+/\d+)", _v2).group(1),
            "vivo_integracion": re.match(r"\*\*(\d+/\d+)\*\*", _v3).group(1),
            "vivo_tokens_primera": re.search(r"primera llamada ([\d.]+) tokens", _v3).group(1), "vivo_tokens_max": re.search(r"máximo ([\d.]+)", _v3).group(1),
            "vivo_usd": re.search(r"USD ([\d,]+) en total", _v3).group(1)})
# pruebas en vivo de la versión vigente (PRUEBAS §3.1): frases nuevas y de control, y frases de regresión
_vv = [f for f in X["pru_resultados"]["filas"] if f[1] == COMPAT["version"]]
assert _vv, "PRUEBAS §3.1 no registra pruebas en vivo de la versión " + COMPAT["version"]
_ok = [re.match(r"\**(\d+)/(\d+) OK", f[3]) for f in _vv]
_rg = [re.search(r"y (\d+)/(\d+) de regresión", f[3]) for f in _vv]
_ids = [int(x) for f in _vv for x in re.findall(r"ids (\d+)–(\d+)", f[2])[0]] if all(re.search(r"ids \d+–\d+", f[2]) for f in _vv) else []
_fe = sorted({f[0] for f in _vv})
CIF.update({"vivo24_ok": sum(int(m.group(1)) for m in _ok), "vivo24_total": sum(int(m.group(2)) for m in _ok),
            "vivo24_reg_ok": sum(int(m.group(1)) for m in _rg if m), "vivo24_reg_total": sum(int(m.group(2)) for m in _rg if m),
            "vivo24_corridas": len(_vv), "vivo24_desde": min(_ids) if _ids else "", "vivo24_hasta": max(_ids) if _ids else "",
            "vivo24_fechas": " y ".join(x.split("-")[2] for x in _fe) + "/" + "/".join(reversed(_fe[-1].split("-")[:2]))})
X["validar_salida"] = "\n".join(re.sub(r"con intérprete \S+", "con intérprete 3.9", l) for l in _vp.stdout.splitlines() if l.startswith(("Skills:", "Python 3.9:", "OK", "ERROR")))
X["cifras"] = CIF
X["web_por_caso"] = _web

# Capa de canales (INTEGRACIONES §3.2)
X["canales_modos"] = tabla(INTG, r"^3\.2 Capa de canales", 0)
X["canales_pasos"] = tabla(INTG, r"^3\.2 Capa de canales", 1)

# CLAUDE.md (desarrollo con Claude Code)
X["cla_flujo"] = [re.sub(r"^\d+\. ", "", b).replace("\n   ", " ").strip() for b in re.split(r"\n(?=\d+\. )", seccion(CLA, r"^Flujo de trabajo").strip())]
X["cla_reglas"] = [re.sub(r"^- ", "", b).replace("\n  ", " ").strip() for b in re.split(r"\n(?=- )", seccion(CLA, r"^Reglas del autor").strip())]
X["cla_probar_md"] = seccion(CLA, r"^Probar como usuario").strip()

# Catálogo
X["comandos"] = tabla(CAT, r"^2\. Comandos de uso humano")
X["agentes"] = tabla(CAT, r"^3\.1 Resumen")
X["reparto_agentes"] = tabla(CAT, r"^4\.7 Reparto")
X["scripts_compartidos"] = tabla(CAT, r"^5\.1 Scripts compartidos")
X["scripts_otros"] = tabla(CAT, r"^5\.2 Scripts de otras")
X["scripts_mantenedor"] = tabla(CAT, r"^5\.3 Scripts del mantenedor")
fichas_ag = {}
for nombre in ["pm-orquestador", "pm-director", "pm-inicio", "pm-planificacion", "pm-control", "pm-cierre"]:
    fichas_ag[nombre] = vinetas_campos(seccion(CAT, r"^" + nombre + r"$"))
X["fichas_agentes"] = fichas_ag
tema = {f[1].split(" ")[0].split("/")[0].strip(): f[0] for f in tabla(COL, r"^2\. Matriz de dueños")["filas"]}
X["temas_duenos"] = tabla(COL, r"^2\. Matriz de dueños")
X["pares_sensibles"] = tabla(COL, r"^4\. Pares sensibles")
grupos = []
s4 = seccion(CAT, r"^4\. Skills por agente")
for m in re.finditer(r"^### (4\.\d) (.+)$", s4, re.M):
    if m.group(1) == "4.7":
        continue
    bloque = seccion(s4, "^" + re.escape(m.group(1)) + " ")
    skills = []
    for m2 in re.finditer(r"^#### (pm-[a-z-]+)\s*$", bloque, re.M):
        nombre = m2.group(1)
        campos = vinetas_campos(seccion(bloque, "^" + nombre + "$"))
        d = {"nombre": nombre, "campos": campos}
        for c, v in campos:
            if c == "Usar":
                u, _, n = v.partition("**No:**")
                d["usar"] = u.strip().rstrip(".")
                d["no"] = n.strip().rstrip(".")
            if c == "PRINCE2":
                d["procesos"] = v.split("·")[0].strip()
        d["tema"] = tema.get(nombre, "")
        skills.append(d)
    comandos_md = re.findall(r"^#### (Comando[s]? asignado[s]? .*)\n(.*?)(?=\n####|\n###|\Z)", bloque, re.M | re.S)
    grupos.append({"id": m.group(1), "titulo": m.group(2), "skills": skills,
                   "comandos": [{"t": a, "md": b.strip()} for a, b in comandos_md]})
X["catalogo"] = grupos
X["catalogo_total"] = sum(len(g["skills"]) for g in grupos)

# RACI
X["raci_leyenda_md"] = seccion(RACI, r"^1\. Leyenda").strip()
X["raci_reglas_md"] = seccion(RACI, r"^2\. Reglas de la matriz").strip()
X["raci"] = tabla(RACI, r"^3\. Matriz principal")
X["raci_lectura_md"] = seccion(RACI, r"^3\. Matriz principal").split("**Cómo se leen algunas filas.**")[1].strip()
X["raci_sensibles"] = tabla(RACI, r"^4\. Matriz compacta")
X["raci_sensibles_notas_md"] = "\n".join(l for l in seccion(RACI, r"^4\. Matriz compacta").split("\n") if l.startswith("\\*") or l.startswith("†"))
X["raci_verif"] = tabla(RACI, r"^5\. Verificación")

# Casos de uso
casos, parte = [], ""
for l_m in re.finditer(r"^(## Parte .*|### (\d+)\. `([^`]+)`((?: y `[^`]+`)*) — (.*))$", CU, re.M):
    if l_m.group(1).startswith("## Parte"):
        parte = l_m.group(1)[3:]
        continue
    # el caso 48 (v2.2) nombra dos skills: "`pm-sanidad` y `pm-direccion-decisiones`"
    n, skill, titulo = int(l_m.group(2)), l_m.group(3) + re.sub(r" y `([^`]+)`", r" · \1", l_m.group(4) or ""), l_m.group(5)
    cuerpo = seccion(CU, r"^" + str(n) + r"\. `")
    campos = dict(vinetas_campos(cuerpo))
    com = campos.get("Comandos", "")
    m = re.search(r"```bash\n(.*?)```", com, re.S)
    casos.append({"n": n, "skill": skill.lstrip("/").split(" ")[0], "comando": skill, "titulo": titulo, "parte": parte,
                  "peticion": campos.get("Prompt del usuario", campos.get("Petición", "")), "quien": campos.get("Quién", ""),
                  "respuestas": campos.get("Respuestas del usuario", ""),
                  "entradas": campos.get("Entradas (qué aporta el usuario y cómo)", ""),
                  "verifica": campos.get("Qué pregunta o verifica", ""),
                  "comandos": m.group(1).rstrip() if m else "", "comandos_txt": "" if m else com,
                  "artefacto": campos.get("Salidas (qué queda y dónde verificarlo)", campos.get("Artefacto", "")), "decision": campos.get("Decisión humana", "")})
X["casos"] = casos
X["cifras"]["casos_uso"] = len(casos) + len(tabla(CU, r"^Parte 7 · ")["filas"])   # casos con ficha + casos de la parte 7 (tabla)
X["muestra"] = tabla(CU, r"^Proyecto de muestra")
X["variante_a"] = {"intro": seccion(CU, r"^Variante A").split("\n\n")[0].strip() if False else seccion(CU, r"^Variante A").strip().split("\n")[0],
                   "tabla": tabla(CU, r"^Variante A")}
X["variante_b"] = {"intro": seccion(CU, r"^Variante B").strip().split("\n")[0], "tabla": tabla(CU, r"^Variante B")}
X["variante_c_md"] = seccion(CU, r"^Variante C").strip()

# Caso maestro
pasos, etapa = [], ""
for m in re.finditer(r"^(## \d+\. .*|### Paso (\d+) · (.*))$", CM, re.M):
    if m.group(1).startswith("## "):
        etapa = re.sub(r"^## \d+\. ", "", m.group(1))
        continue
    n = int(m.group(2))
    cuerpo = seccion(CM, r"^Paso " + str(n) + r" · ")
    t = tablas(cuerpo)
    campos = {f[0]: f[1] for f in t[0]["filas"]} if t and t[0]["cab"][0] == "Campo" else {}
    resto = cuerpo
    if campos:
        # quitar la tabla de campos
        lineas = cuerpo.split("\n")
        ini = next(i for i, l in enumerate(lineas) if l.startswith("| Campo"))
        fin = ini
        while fin < len(lineas) and lineas[fin].startswith("|"):
            fin += 1
        resto = "\n".join(lineas[:ini] + lineas[fin:])
    pasos.append({"n": n, "titulo": m.group(3), "etapa": etapa, "campos": campos, "resto_md": resto.strip()})
X["pasos"] = pasos
X["escenario"] = tabla(CM, r"^1\. Escenario")
X["principios"] = tabla(CM, r"^10\. Dónde apareció")
X["lecciones_caso_md"] = seccion(CM, r"^9\. Lecciones del caso").strip()
X["integridad_md"] = seccion(CM, r"^Integridad al final").strip()

# Paquete
X["compatibilidad"] = COMPAT
X["arbol_paquete"] = re.search(r"## Estructura del repositorio\n\n```\n(.*?)```", README, re.S).group(1).rstrip()
X["arbol_proyecto"] = re.search(r"### 1\.5 Carpeta del proyecto.*?```\n(.*?)```", SPEC, re.S).group(1).rstrip()
X["ciclo_vida_txt"] = leer("docs/diagramas/ciclo-de-vida.mmd").rstrip()
X["reglas_siempre"] = seccion(README, r"^Reglas que el paquete aplica siempre").strip().rstrip("-").strip()
X["skills_dirs"] = sorted(p.name for p in (BASE / "skills").iterdir() if p.is_dir())
X["knowledge_refs"] = sorted(p.name for p in (BASE / "skills/pm-knowledge/references").iterdir())
X["frases_eval"] = sum(1 for l in leer("docs/evaluacion/frases-enrutamiento.tsv").splitlines() if l.strip())

# Diagramas Mermaid (tomados tal cual de la documentación)
fuentes_mmd = [
    ("arq-general", "docs/ARQUITECTURA.md", 0, "Vista general: hilo principal, subagentes de fase, capas y hooks", "ARQUITECTURA.md §1"),
    ("arq-flujo", "docs/ARQUITECTURA.md", 1, "Flujo de orquestación de una petición con decisión humana", "ARQUITECTURA.md §10"),
    ("sync-general", "docs/sincronizacion.md", 0, "Fuente única: BMAD (solo lectura) → puente → fachada; traspaso de vuelta", "sincronizacion.md §3"),
    ("sync-cache", "docs/sincronizacion.md", 1, "Caché del índice por huella", "sincronizacion.md §4.3"),
    ("sync-estados", "docs/sincronizacion.md", 2, "Ciclo de vida de una línea base de especificación", "sincronizacion.md §6"),
    ("sanidad", "docs/SANIDAD.md", 0, "Controles: prevenir, detectar, decidir, mantener", "SANIDAD.md §1"),
    ("caso-ciclo", "docs/CASO-MAESTRO.md", 0, "Ciclo de vida recorrido en el caso maestro", "CASO-MAESTRO.md §2"),
    ("caso-wbs", "docs/ejemplos/wbs-mermaid.md", 0, "WBS final del caso (con el paquete 3.7 de C-001)", "ejemplos/wbs-mermaid.md"),
]
DG = AQUI / "diagramas"
DG.mkdir(exist_ok=True)
cfg = DG / "mermaid-config.json"
cfg.write_text(json.dumps({"theme": "base", "themeVariables": {
    "fontFamily": "Arial, Helvetica, sans-serif", "fontSize": "15px",
    "primaryColor": "#E9F1F8", "primaryBorderColor": "#00629B", "primaryTextColor": "#002855",
    "secondaryColor": "#FBF1E6", "secondaryBorderColor": "#B5651D", "tertiaryColor": "#F4F6F8", "tertiaryBorderColor": "#002855",
    "lineColor": "#002855", "clusterBkg": "#F4F6F8", "clusterBorder": "#00629B", "titleColor": "#002855",
    "actorBkg": "#E9F1F8", "actorBorder": "#00629B", "actorTextColor": "#002855", "signalColor": "#002855", "signalTextColor": "#272425",
    "noteBkgColor": "#FBF1E6", "noteBorderColor": "#B5651D", "labelBoxBkgColor": "#E9F1F8", "sequenceNumberColor": "#FFFFFF",
    "edgeLabelBackground": "#FFFFFF"},
    "flowchart": {"htmlLabels": True, "curve": "basis"}, "sequence": {"useMaxWidth": True}}), encoding="utf-8")
diagramas = []
codigo_estados = bloques_mermaid(SYNC)[2].replace("stateDiagram-v2", "stateDiagram-v2\n  direction LR", 1)
if not (DG / "sync-estados-lr.mmd").exists() or (DG / "sync-estados-lr.mmd").read_text(encoding="utf-8") != codigo_estados:
    (DG / "sync-estados-lr.mmd").write_text(codigo_estados, encoding="utf-8")
fuentes_mmd += [("sync-estados-lr", None, None, "Ciclo de vida de una línea base (horizontal)", "sincronizacion.md §6")]
# v2.2: flujo de la capa de canales y gestión por excepción de la guía E2E-2 (paso 10), tal cual
fuentes_mmd += [("canales", "docs/INTEGRACIONES.md", 0, "Capa de canales: crear, redactar, aprobar, simular, enviar y registrar", "INTEGRACIONES.md §3.2")]
_exc = next(b for b in bloques_mermaid(leer("docs/guias/E2E-2-alcance-roadmap.md")) if "C-002 · requisito regulatorio" in b)
if not (DG / "excepcion.mmd").exists() or (DG / "excepcion.mmd").read_text(encoding="utf-8") != _exc:
    (DG / "excepcion.mmd").write_text(_exc, encoding="utf-8")
fuentes_mmd += [("excepcion", None, None, "Gestión por excepción en la guía E2E-2, paso 10", "guias/E2E-2-alcance-roadmap.md, «Representaciones gráficas»")]
for clave, archivo, k, titulo, origen in fuentes_mmd:
    if archivo is None:
        codigo = (DG / f"{clave}.mmd").read_text(encoding="utf-8")
    else:
        codigo = bloques_mermaid(leer(archivo))[k]
    if codigo.lstrip().startswith("sequenceDiagram"):
        # En sequenceDiagram ';' separa sentencias: se escapa en el texto de los mensajes (solo para renderizar)
        codigo = "\n".join(re.sub(r"^(\s*[^:]+:)(.*)$", lambda m: m.group(1) + m.group(2).replace(";", "#59;"), l) if "->>" in l or "-->>" in l else l
                           for l in codigo.split("\n"))
    if archivo is not None and (not (DG / f"{clave}.mmd").exists() or (DG / f"{clave}.mmd").read_text(encoding="utf-8") != codigo):
        (DG / f"{clave}.mmd").write_text(codigo, encoding="utf-8")   # solo si cambió: así no se vuelve a dibujar
    for ext, extra in (("svg", ["-I", f"svg-{clave}"]), ("png", ["-s", "3", "-b", "white"])):
        salida = DG / f"{clave}.{ext}"
        if not salida.exists() or salida.stat().st_mtime < (DG / f"{clave}.mmd").stat().st_mtime:
            subprocess.run([MMDC] + (["-p", PUPPETEER] if PUPPETEER else []) + ["-i", str(DG / f"{clave}.mmd"), "-o", str(salida), "-c", str(cfg)] + extra,
                           check=True, capture_output=True)
    diagramas.append({"id": clave, "titulo": titulo, "origen": origen})
# Diagramas oficiales del paquete v2.1 (docs/diagramas/): SVG tal cual (con id único) y PNG con mmdc
diagramas_repo = [
    ("arquitectura", "Arquitectura por capas: gobierno, técnicas, especificación, integración y persistencia, protegidas por los hooks"),
    ("orquestacion-puerta", "Orquestación de una puerta: el orquestador pregunta y presenta; solo pm-director registra"),
    ("agentes-skills", "Agentes y skills: el orquestador, los cinco subagentes de fase y las skills transversales"),
    ("ciclo-de-vida", "Ciclo de vida PRINCE2 y puertas de la junta"),
    ("sincronizacion-bmad", "Sincronización con BMAD: lectura, línea base, verificación, cambio y traspaso"),
    ("ciclo-prince2-bmad", "Ciclo de vida integrado: PRINCE2 (gobierno), BMAD (especificación) y puertas de la junta"),
    ("verificacion-puertas", "Verificación de una puerta en tres capas y registro de la decisión"),
]
for clave, titulo in diagramas_repo:
    origen_svg = BASE / "docs/diagramas" / f"{clave}.svg"
    destino = DG / f"repo-{clave}.svg"
    destino.write_text(origen_svg.read_text(encoding="utf-8").replace("my-svg", f"repo-{clave}"), encoding="utf-8")
    png = DG / f"repo-{clave}.png"
    mmd = BASE / "docs/diagramas" / f"{clave}.mmd"
    if not png.exists() or png.stat().st_mtime < mmd.stat().st_mtime:
        subprocess.run([MMDC] + (["-p", PUPPETEER] if PUPPETEER else []) + ["-i", str(mmd), "-o", str(png), "-s", "3", "-b", "white"], check=True, capture_output=True)
    diagramas.append({"id": f"repo-{clave}", "titulo": titulo, "origen": f"docs/diagramas/{clave}.mmd · .svg"})
    X.setdefault("diagramas_repo_mmd", {})[clave] = mmd.read_text(encoding="utf-8").rstrip()
# Variante horizontal del ciclo integrado para diapositivas 16:9 (mismo contenido; solo cambia la orientación)
_lr = (BASE / "docs/diagramas/ciclo-prince2-bmad.mmd").read_text(encoding="utf-8").replace("flowchart TB", "flowchart LR", 1).replace("direction LR", "direction TB")
if not (DG / "repo-ciclo-prince2-bmad-lr.mmd").exists() or (DG / "repo-ciclo-prince2-bmad-lr.mmd").read_text(encoding="utf-8") != _lr:
    (DG / "repo-ciclo-prince2-bmad-lr.mmd").write_text(_lr, encoding="utf-8")
_png = DG / "repo-ciclo-prince2-bmad-lr.png"
if not _png.exists() or _png.stat().st_mtime < (DG / "repo-ciclo-prince2-bmad-lr.mmd").stat().st_mtime:
    subprocess.run([MMDC] + (["-p", PUPPETEER] if PUPPETEER else []) + ["-i", str(DG / "repo-ciclo-prince2-bmad-lr.mmd"), "-o", str(_png), "-w", "2400", "-b", "white"], check=True, capture_output=True)
import columna
columna.generar(DG)
diagramas.append({"id": "col-vertebral", "titulo": "Columna vertebral: leer, fijar, detectar y traspasar (síntesis del informe)", "origen": "sincronizacion.md §2–§8"})
X["diagramas"] = diagramas

# Recortes (sin escalar ni deformar) de las capturas reales del reporte de interesados, para diapositivas 16:9
from PIL import Image
for origen, caja, destino in [("g3-interesados-matriz.png", (60, 225, 1045, 695), "g3-matriz-recorte.png"),
                              ("g3-interesados-raci-perfiles.png", (55, 30, 1225, 555), "g3-raci-recorte.png")]:
    Image.open(BASE / "docs/guias/img" / origen).crop(caja).save(DG / destino)

def _completar(v):
    if isinstance(v, str):
        def rep(m):
            k = m.group(1)
            if k not in X["cifras"]:
                raise KeyError(f"narrativa.json cita {{{{{k}}}}}, que no está en las cifras extraídas")
            return str(X["cifras"][k])
        return re.sub(r"\{\{([a-z_0-9]+)\}\}", rep, v)
    if isinstance(v, list):
        return [_completar(x) for x in v]
    if isinstance(v, dict):
        return {k: _completar(x) for k, x in v.items()}
    return v
D = _completar(D)
# la etiqueta de la versión del informe (y de la carpeta de salida) sigue a compatibilidad.json
assert D["meta"]["version"] == "v" + ".".join(COMPAT["version"].split(".")[:2]), ("narrativa.json meta.version", D["meta"]["version"], COMPAT["version"])
def _donde(codigos):
    partes = []
    cods = re.findall(r"\b(?:[A-Z]{3}-\d{2}|[GPEXC]-\d{2})\b", codigos)
    for g, mapa in X["guias_codigos_pasos"].items():
        pasos = []
        for c in cods:
            for pz in mapa.get(c, []) + mapa.get("S-" + c, []):
                if pz not in pasos:
                    pasos.append(pz)
        if pasos:
            pasos.sort(key=lambda z: (int(re.match(r"\d+", z).group()), z))
            partes.append(f"{g} {'paso' if len(pasos) == 1 else 'pasos'} {', '.join(pasos)}")
    return " · ".join(partes) or "— (no aparece en los pasos de las guías)"
X["controles_donde"] = [_donde(f[2]) for f in D["cap"]["controles"]]
D["x"] = X
(AQUI / "data.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
print("data.json ok · skills en catálogo:", X["catalogo_total"], "· casos:", len(casos), "· pasos del caso maestro:", len(pasos),
      "· filas RACI:", len(X["raci"]["filas"]), "· códigos de sanidad:", X["codigos_n"], "en", len(X["codigos_familias"]), "familias")
print("cifras:", json.dumps(X["cifras"], ensure_ascii=False))
