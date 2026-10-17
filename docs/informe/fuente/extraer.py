"""Extrae de la documentación de pm-method las tablas y fichas que usa el Informe 2.

Fuente única: la raíz del repositorio pm-method (por defecto ../../.. desde esta carpeta; README, SPEC, compatibilidad.json, docs/, agents/).
Salida: data.json = narrativa.json (texto propio del informe) + estructuras extraídas literalmente.
Volver a ejecutar cuando cambie el paquete:  python3 extraer.py && python3 build_html.py && node build_pptx.js
"""
import json, re, pathlib, subprocess, os

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
X["pue_severidades"] = _s2.split("\n\n")[2].replace("\n", " ")
X["pue_controles"] = tabla(PUE, r"^3\. Controles automáticos")
X["pue_criterios_exito"] = seccion(PUE, r"^3\. Controles automáticos").strip().split("\n\n")[-1].replace("\n", " ")
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
for l_m in re.finditer(r"^(## Parte .*|### (\d+)\. `([^`]+)` — (.*))$", CU, re.M):
    if l_m.group(1).startswith("## Parte"):
        parte = l_m.group(1)[3:]
        continue
    n, skill, titulo = int(l_m.group(2)), l_m.group(3), l_m.group(4)
    cuerpo = seccion(CU, r"^" + str(n) + r"\. `")
    campos = dict(vinetas_campos(cuerpo))
    com = campos.get("Comandos", "")
    m = re.search(r"```bash\n(.*?)```", com, re.S)
    casos.append({"n": n, "skill": skill.lstrip("/").split(" ")[0], "comando": skill, "titulo": titulo, "parte": parte,
                  "peticion": campos.get("Petición", ""), "quien": campos.get("Quién", ""),
                  "verifica": campos.get("Qué pregunta o verifica", ""),
                  "comandos": m.group(1).rstrip() if m else "", "comandos_txt": "" if m else com,
                  "artefacto": campos.get("Artefacto", ""), "decision": campos.get("Decisión humana", "")})
X["casos"] = casos
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
(DG / "sync-estados-lr.mmd").write_text(codigo_estados, encoding="utf-8")
fuentes_mmd += [("sync-estados-lr", None, None, "Ciclo de vida de una línea base (horizontal)", "sincronizacion.md §6")]
for clave, archivo, k, titulo, origen in fuentes_mmd:
    if archivo is None:
        codigo = (DG / f"{clave}.mmd").read_text(encoding="utf-8")
    else:
        codigo = bloques_mermaid(leer(archivo))[k]
    if codigo.lstrip().startswith("sequenceDiagram"):
        # En sequenceDiagram ';' separa sentencias: se escapa en el texto de los mensajes (solo para renderizar)
        codigo = "\n".join(re.sub(r"^(\s*[^:]+:)(.*)$", lambda m: m.group(1) + m.group(2).replace(";", "#59;"), l) if "->>" in l or "-->>" in l else l
                           for l in codigo.split("\n"))
    if archivo is not None:
        (DG / f"{clave}.mmd").write_text(codigo, encoding="utf-8")
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
        subprocess.run([MMDC] + (["-p", PUPPETEER] if PUPPETEER else []) + ["-i", str(mmd), "-o", str(png), "-w", "1600", "-b", "white"], check=True, capture_output=True)
    diagramas.append({"id": f"repo-{clave}", "titulo": titulo, "origen": f"docs/diagramas/{clave}.mmd · .svg"})
    X.setdefault("diagramas_repo_mmd", {})[clave] = mmd.read_text(encoding="utf-8").rstrip()
# Variante horizontal del ciclo integrado para diapositivas 16:9 (mismo contenido; solo cambia la orientación)
_lr = (BASE / "docs/diagramas/ciclo-prince2-bmad.mmd").read_text(encoding="utf-8").replace("flowchart TB", "flowchart LR", 1).replace("direction LR", "direction TB")
(DG / "repo-ciclo-prince2-bmad-lr.mmd").write_text(_lr, encoding="utf-8")
_png = DG / "repo-ciclo-prince2-bmad-lr.png"
if not _png.exists() or _png.stat().st_mtime < (DG / "repo-ciclo-prince2-bmad-lr.mmd").stat().st_mtime:
    subprocess.run([MMDC] + (["-p", PUPPETEER] if PUPPETEER else []) + ["-i", str(DG / "repo-ciclo-prince2-bmad-lr.mmd"), "-o", str(_png), "-w", "2400", "-b", "white"], check=True, capture_output=True)
import columna
columna.generar(DG)
diagramas.append({"id": "col-vertebral", "titulo": "Columna vertebral: leer, fijar, detectar y traspasar (síntesis del informe)", "origen": "sincronizacion.md §2–§8"})
X["diagramas"] = diagramas

D["x"] = X
(AQUI / "data.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
print("data.json ok · skills en catálogo:", X["catalogo_total"], "· casos:", len(casos), "· pasos:", len(pasos),
      "· filas RACI:", len(X["raci"]["filas"]), "· códigos:", len(X["codigos"]["filas"]))
