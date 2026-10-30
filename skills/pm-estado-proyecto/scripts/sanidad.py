#!/usr/bin/env python3
"""Sanidad del ecosistema pm-method: consistencia del proyecto, de la columna vertebral BMAD ↔ PRINCE2 y de las
integraciones. Health check of the project folder, the BMAD↔PRINCE2 backbone and installed integrations.

Uso / Usage:
  sanidad.py --proyecto ./gestion                 # todas las comprobaciones
  sanidad.py --proyecto ./gestion --rapido        # subconjunto rápido (lo usa el hook de inicio de sesión)
  sanidad.py --proyecto ./gestion --informe       # además escribe 03-control/reportes/<fecha>-sanidad.md
  sanidad.py --proyecto ./gestion --reparar       # arreglos seguros: columnas de registros, índice de especificación
  sanidad.py --proyecto ./gestion --json
  sanidad.py --proyecto ./gestion --corte 2027-01-15   # fecha de corte de los controles con vencimiento
Salida: hallazgos ERROR / AVISO / INFO con código, mensaje y cómo corregir. Código de salida 1 si hay ERROR.
Familias: INS instalación · EST estado y puertas · ART artefactos · REG registros · ESP especificación/BMAD · INT integraciones ·
  CAM cambios y presupuestos · QUA calidad · TOL pronóstico contra tolerancias · SUP supuestos críticos · STK interesados ·
  MAP mapas de Wardley y de recorrido (solo avisos) · DEC hojas de decisión con matriz y vigencia de decisiones (solo avisos) ·
  BIT bitácora de escrituras: cadena y cambios fuera de los scripts (solo avisos) · DAT archivos de datos ilegibles (DAT-01).
Un estado.json ilegible no admite comprobaciones: mensaje con el archivo, el motivo y qué hacer, código 1 y nada reescrito.
"""
import argparse, csv, datetime, glob, importlib.util, json, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import esquema as E

H = []
def add(sev, cod, msg, arreglo=""): H.append({"severidad": sev, "codigo": cod, "mensaje": msg, "arreglo": arreglo})

# idioma de los hallazgos = estado.json.idioma (los fija cada chk_* con su `e`, también cuando los llama estado.py radar);
# los códigos, las severidades y las claves del JSON no se traducen
IDIOMA = "es"
def T(es, en): return E.t(IDIOMA, es, en)
def _idioma(e):
    global IDIOMA
    IDIOMA = (e or {}).get("idioma", "es") if isinstance(e, dict) else "es"

def ilegible(proyecto, x):
    """DAT-01: archivo de datos que no se puede leer (E.DatosIlegibles: otra codificación, CSV mal formado, JSON inválido).
    Es ERROR y no se reemplaza por "vacío"; una vez por archivo."""
    rel = os.path.relpath(x.archivo, proyecto) if x.archivo else "?"
    if any(h["codigo"] == "DAT-01" and h["mensaje"].startswith(rel + ":") for h in H): return
    add("ERROR", "DAT-01", T(f"{rel}: {x.motivo}; los controles que lo usan no se evaluaron.", f"{rel}: {getattr(x, 'motivo_en', '') or x.motivo}; the checks that use it were not evaluated."),
        T(x.accion or "Restaurarlo desde git o corregirlo.", getattr(x, "accion_en", "") or "Restore it from git or fix it."))

def leer_fm(p):
    try: t = open(p, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError): return None
    if not t.startswith("---"): return {}
    partes = t.split("---", 2)
    if len(partes) < 3: return {}
    return {k: v.strip().strip('"') for k, v in re.findall(r"(?m)^(\w+):\s*(.*)$", partes[1])}

# ------------------------------------------------------------------ INS: instalación e integraciones externas
def dirs_skills(proyecto):
    home = os.path.expanduser("~")
    cands = [os.path.join(proyecto, "..", ".claude", "skills"), os.path.join(os.getcwd(), ".claude", "skills"),
             os.path.join(home, ".claude", "skills"), os.path.join(home, ".hermes", "skills"),
             os.path.normpath(os.path.join(AQUI, "..", ".."))]
    # plugins: solo la ruta activa de cada plugin instalado (installed_plugins.json); no los clones de marketplaces/ ni
    # versiones viejas del caché, que Claude Code no carga (evita falsos INS-04 "instalada 2 veces")
    try: ip = json.load(open(os.path.join(home, ".claude", "plugins", "installed_plugins.json"), encoding="utf-8")).get("plugins", {})
    except (OSError, ValueError): ip = {}
    for entradas in ip.values():
        for ent in entradas if isinstance(entradas, list) else [entradas]:
            if ent.get("installPath"): cands.append(os.path.join(ent["installPath"], "skills"))
    out = []
    for c in cands:
        c = os.path.abspath(c)
        if os.path.isdir(c) and c not in out: out.append(c)
    return out

def inventario_skills(proyecto):
    vistos = {}
    for d in dirs_skills(proyecto):
        for p in glob.glob(os.path.join(d, "**", "SKILL.md"), recursive=True)[:3000]:
            fm = leer_fm(p) or {}
            n = fm.get("name") or os.path.basename(os.path.dirname(p))
            vistos.setdefault(n, []).append({"ruta": p, "description": fm.get("description", ""), "modelo": fm.get("disable-model-invocation", "") != "true"})
    return vistos

def _ancestros(p):
    p, out = os.path.abspath(p), []
    while True:
        out.append(p)
        q = os.path.dirname(p)
        if q == p: return out
        p = q

def _skills_en(base):
    """SKILL.md de una carpeta de skills (<base>/<skill>/SKILL.md, también en subcarpetas como synced/<id>/)."""
    return glob.glob(os.path.join(base, "*", "SKILL.md")) + glob.glob(os.path.join(base, "*", "*", "*", "SKILL.md"))

def skills_externas(proyecto):
    """Skills invocables en Claude Code / Hermes por nombre real: {nombre_corto: [{"invocar", "origen", "ruta"}]}.
    Fuentes: .claude/skills del proyecto (y carpetas superiores, de la carpeta del proyecto y del cwd), ~/.claude/skills
    (incluye las sincronizadas de claude.ai, que se ven como anthropic-skills:<n>), plugins instalados según
    ~/.claude/plugins/installed_plugins.json (se ven como <plugin>:<skill>) y ~/.hermes/skills. Un plugin cargado solo
    con --plugin-dir no deja rastro en disco."""
    home, inv = os.path.expanduser("~"), {}
    def alta(p, invocar_fmt, origen):
        fm = leer_fm(p) or {}
        n = fm.get("name") or os.path.basename(os.path.dirname(p))
        inv.setdefault(n, []).append({"invocar": invocar_fmt.format(n=n), "origen": origen, "ruta": p})
    vistos = set()
    for d in _ancestros(proyecto) + _ancestros(os.getcwd()):
        c = os.path.join(d, ".claude", "skills")
        if c in vistos or not os.path.isdir(c) or d == home: continue
        vistos.add(c)
        for p in _skills_en(c): alta(p, "{n}", f"proyecto ({c})")
    u = os.path.join(home, ".claude", "skills")
    for p in glob.glob(os.path.join(u, "*", "SKILL.md")): alta(p, "{n}", "usuario (~/.claude/skills)")
    for p in glob.glob(os.path.join(u, "synced", "*", "*", "SKILL.md")): alta(p, "anthropic-skills:{n}", "claude.ai (skills sincronizadas)")
    for p in glob.glob(os.path.join(home, ".hermes", "skills", "**", "SKILL.md"), recursive=True): alta(p, "{n}", "Hermes (~/.hermes/skills)")
    try: ip = json.load(open(os.path.join(home, ".claude", "plugins", "installed_plugins.json"), encoding="utf-8")).get("plugins", {})
    except (OSError, ValueError): ip = {}
    raices = {os.path.realpath(x) for x in _ancestros(proyecto) + _ancestros(os.getcwd())}
    for clave, entradas in ip.items():
        plugin, _, mkt = clave.partition("@")
        for ent in entradas if isinstance(entradas, list) else [entradas]:
            if ent.get("scope") in ("project", "local") and os.path.realpath(ent.get("projectPath", "")) not in raices: continue
            ruta = ent.get("installPath", "")
            if not os.path.isdir(ruta): continue
            permitidas = None  # plugins de marketplace con lista explícita de skills (p. ej. document-skills)
            try:
                mk = json.load(open(os.path.join(home, ".claude", "plugins", "marketplaces", mkt, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
                for pl in mk.get("plugins", []):
                    if pl.get("name") == plugin and pl.get("skills"): permitidas = {os.path.basename(s.rstrip("/")) for s in pl["skills"]}
            except (OSError, ValueError): pass
            cands = glob.glob(os.path.join(ruta, "skills", "*", "SKILL.md")) + glob.glob(os.path.join(ruta, "SKILL.md"))
            for p in cands:
                if permitidas is not None and os.path.basename(os.path.dirname(p)) not in permitidas: continue
                alta(p, plugin + ":{n}", f"plugin {clave} ({ent.get('scope', 'user')})")
    return inv

EXTERNAS = {  # integración → skills requeridas (nombre real del frontmatter) y requisitos de ejecución
    "archify": {"skills": ["archify"], "node": True, "chrome": True},
    "diagram-design": {"skills": ["diagram-design"], "node": False, "chrome": False},
    "visual-explainer": {"skills": ["visual-explainer"], "node": True, "chrome": False},
    "skills-office": {"skills": ["docx", "xlsx", "pptx"], "node": True, "chrome": False},
}

def chk_externas(proyecto, e):
    import shutil
    integ = e.get("integraciones", {})
    pedidas = [v.strip() for v in str(integ.get("diagramas", "")).split(",") if v.strip() in EXTERNAS]
    if integ.get("export") == "skills-office": pedidas.append("skills-office")
    if not pedidas: return
    ext = skills_externas(proyecto)
    for valor in pedidas:
        req = EXTERNAS[valor]
        for n in req["skills"]:
            if n in ext:
                x, nombres = ext[n][0], " o ".join(dict.fromkeys(f"'{y['invocar']}'" for y in ext[n]))
                add("INFO", "INS-03", T(f"Skill externa '{n}' ({valor}) instalada: invocar como {nombres} · {x['origen']} · {x['ruta']}",
                                        f"External skill '{n}' ({valor}) installed: invoke it as {nombres} · {x['origen']} · {x['ruta']}"))
            elif valor == "skills-office" and n == "pptx":
                add("INFO", "INS-03", T("export = skills-office sin la skill 'pptx': el deck de puerta sale como guion Markdown.", "export = skills-office without the 'pptx' skill: the gate deck is produced as a Markdown script."),
                    T("Instalarla: ver docs/INSTALACION.md §6.1.", "Install it: see docs/INSTALACION.md §6.1."))
            else:
                clave = "export" if valor == "skills-office" else "diagramas"
                add("AVISO", "INS-03", T(f"integraciones.{clave} = {valor}, pero no se encontró la skill '{n}' (ni '<plugin>:{n}') en .claude/skills del proyecto, ~/.claude/skills ni en los plugins instalados.",
                                         f"integraciones.{clave} = {valor}, but the skill '{n}' (or '<plugin>:{n}') was not found in the project's .claude/skills, ~/.claude/skills or the installed plugins."),
                    T(f"Instalarla (docs/INSTALACION.md §6.1) o volver al respaldo (estado.py integracion {clave}={'scripts' if clave == 'export' else 'mermaid'}). Si se carga con --plugin-dir, ignorar este aviso.",
                      f"Install it (docs/INSTALACION.md §6.1) or go back to the fallback (estado.py integracion {clave}={'scripts' if clave == 'export' else 'mermaid'}). If it is loaded with --plugin-dir, ignore this warning."))
        instalada = all(n in ext for n in req["skills"])
        if req["node"] and not shutil.which("node"):
            add("AVISO", "INS-03", T(f"{valor} necesita Node.js y no está en el PATH (archify ≥ 18; `npx skills add` ≥ 22.20).", f"{valor} needs Node.js and it is not on the PATH (archify ≥ 18; `npx skills add` ≥ 22.20)."),
                T("Instalar Node.js o volver al respaldo interno.", "Install Node.js or go back to the built-in fallback."))
        win = [os.path.join(os.environ.get(v, ""), "Google", "Chrome", "Application", "chrome.exe") for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA") if os.environ.get(v)]
        if req["chrome"] and instalada and not (os.environ.get("ARCHIFY_CHROME") or any(shutil.which(b) for b in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"))) \
                and not any(os.path.exists(p) for p in ["/Applications/Google Chrome.app", "/Applications/Chromium.app"] + win):
            add("INFO", "INS-03", T("archify: no se encontró Chrome/Chromium; su verificación en navegador (browser-check) quedará omitida.", "archify: Chrome/Chromium was not found; its in-browser check (browser-check) will be skipped."),
                T("Instalar Chrome o definir ARCHIFY_CHROME=<ejecutable>.", "Install Chrome or set ARCHIFY_CHROME=<executable>."))

def chk_instalacion(proyecto, e, rapido):
    _idioma(e)
    for mod, uso, uso_en in (("yaml", "leer BMAD y sprint-status", "read BMAD and sprint-status"), ("docx", "exportar .docx / actas .docx", "export .docx / .docx minutes"), ("openpyxl", "exportar .xlsx", "export .xlsx")):
        # find_spec comprueba que el módulo está instalado sin importarlo (importar openpyxl o docx tarda segundos)
        if importlib.util.find_spec(mod) is None: add("AVISO", "INS-01", T(f"Falta el módulo Python '{mod}' ({uso}).", f"Python module '{mod}' is missing ({uso_en})."), f"pip install {'pyyaml' if mod == 'yaml' else ('python-docx' if mod == 'docx' else mod)}")
    vp = e.get("version_paquete")
    if vp and vp != E.VERSION_PAQUETE:
        add("AVISO", "INS-02", T(f"El proyecto fue creado con pm-method {vp} y el instalado es {E.VERSION_PAQUETE}.", f"The project was created with pm-method {vp} and the installed one is {E.VERSION_PAQUETE}."),
            T("Revisar notas de versión; estado.json se migra al leerse y la versión se actualiza en la próxima escritura con estado.py.", "Review the release notes; estado.json is migrated when read and the version is updated on the next write with estado.py."))
    if rapido: return
    inv = inventario_skills(proyecto)
    # skills externas declaradas en integraciones (diagramas, export=skills-office), por nombre real y plugins instalados
    chk_externas(proyecto, e)
    # duplicados de nombre (p. ej. plugin + copia manual)
    for n, lst in inv.items():
        rutas = {os.path.realpath(x["ruta"]) for x in lst}
        if n.startswith("pm-") and len(rutas) > 1:
            add("AVISO", "INS-04", T(f"La skill {n} está instalada {len(rutas)} veces ({', '.join(sorted(rutas))[:300]}).", f"The skill {n} is installed {len(rutas)} times ({', '.join(sorted(rutas))[:300]})."),
                T("Dejar una sola instalación (plugin o copia) para evitar versiones mezcladas.", "Keep a single installation (plugin or copy) to avoid mixed versions."))
    # presupuesto del listado y colisiones de activación con skills de otros repos
    total = sum(len(x[0]["description"]) for x in inv.values() if x[0]["modelo"])
    bm = [n for n in inv if n.startswith("bmad-")]
    if total > 8000:
        add("AVISO", "INS-05", T(f"Las descripciones de las {sum(1 for x in inv.values() if x[0]['modelo'])} skills visibles suman ≈{total} caracteres{' (incluye ' + str(len(bm)) + ' de BMAD)' if bm else ''}; el listado de Claude Code usa ≈1 % del contexto y puede recortarlas.",
                                 f"The descriptions of the {sum(1 for x in inv.values() if x[0]['modelo'])} visible skills add up to ≈{total} characters{' (including ' + str(len(bm)) + ' from BMAD)' if bm else ''}; the Claude Code listing uses ≈1 % of the context and may truncate them."),
            T('En settings.json: "skillListingBudgetFraction": 0.02, o marcar skills poco usadas como "name-only" en skillOverrides (no aplica a skills de plugins).',
              'In settings.json: "skillListingBudgetFraction": 0.02, or mark rarely used skills as "name-only" in skillOverrides (does not apply to plugin skills).'))
    pm = {n: x[0]["description"] for n, x in inv.items() if n.startswith("pm-")}
    def claves(d):
        m = re.search(r"Usar:(.*?)(No:|$)", d)
        return {w.strip().lower() for w in (m.group(1) if m else "").split(",") if len(w.strip()) > 3}
    for n, lst in inv.items():
        if n.startswith("pm-") or not lst[0]["modelo"]: continue
        dl = lst[0]["description"].lower()
        for pn, pd in pm.items():
            comunes = [k for k in claves(pd) if k.strip(". ") in dl]
            if len(comunes) >= 3:
                add("AVISO", "INS-06", T(f"Posible colisión de activación entre '{n}' (externa) y '{pn}': comparten {', '.join(sorted(comunes))[:120]}.",
                                         f"Possible activation clash between '{n}' (external) and '{pn}': they share {', '.join(sorted(comunes))[:120]}."),
                    T("Confirmar cuál debe responder; ajustar la descripción local o usar skillOverrides para la externa.", "Confirm which one should respond; adjust the local description or use skillOverrides for the external one."))

# ------------------------------------------------------------------ EST: estado y puertas
def chk_estado(proyecto, e):
    _idioma(e)
    fase, proc = e.get("fase"), e.get("proceso_actual")
    validos = {("pre-proyecto", "SU"), ("inicio", "IP"), ("entrega", "CS"), ("entrega", "SB"), ("cierre", "CP"), ("cerrado", "CP")}
    if (fase, proc) not in validos: add("ERROR", "EST-01", T(f"Combinación fase/proceso inválida: {fase}/{proc}.", f"Invalid phase/process combination: {fase}/{proc}."), T("estado.py set fase=… proceso_actual=… o rehacer la última transición.", "estado.py set fase=… proceso_actual=… or redo the last transition."))
    ok = lambda t: [p for p in e.get("puertas", []) if p.get("tipo") == t and p.get("decision") in ("aprobado", "condicionado")]
    if fase in ("inicio", "entrega", "cierre", "cerrado") and not ok("autorizar-inicio"):
        add("ERROR", "EST-02", T(f"Fase {fase} sin puerta autorizar-inicio registrada.", f"Phase {fase} with no autorizar-inicio gate recorded."), T("Registrar la decisión con pm-director (estado.py puerta autorizar-inicio …).", "Record the decision with pm-director (estado.py puerta autorizar-inicio …)."))
    # un cierre prematuro desde la iniciación llega a CP sin autorizar-proyecto ni autorizar-etapa (PRINCE2 DP: si no se
    # autoriza el proyecto, se cierra prematuramente); la decisión de la junta queda en cierre_prematuro.decision
    prematuro_inicio = fase in ("cierre", "cerrado") and str(E.cierre_prematuro(e).get("desde", "")).startswith("inicio")
    if fase in ("entrega", "cierre", "cerrado") and not prematuro_inicio and not (ok("autorizar-proyecto") and ok("autorizar-etapa")):
        add("ERROR", "EST-03", T(f"Fase {fase} sin autorizar-proyecto y autorizar-etapa.", f"Phase {fase} without autorizar-proyecto and autorizar-etapa."), T("Revisar las decisiones de la junta.", "Review the board's decisions."))
    if fase == "cerrado" and not ok("autorizar-cierre"): add("ERROR", "EST-04", T("Proyecto cerrado sin autorizar-cierre.", "Project closed without autorizar-cierre."), "")
    n_etapa = e.get("etapa_actual", {}).get("numero", 0)
    esperado = (1 if ok("autorizar-inicio") else 0) + len(ok("autorizar-etapa"))
    if fase in ("inicio", "entrega") and n_etapa != esperado:
        add("AVISO", "EST-05", T(f"etapa_actual = {n_etapa}, pero las puertas registradas implican la etapa {esperado}.", f"etapa_actual = {n_etapa}, but the recorded gates imply stage {esperado}."),
            T("Corregir con estado.py etapa --numero … si fue un ajuste manual.", "Fix it with estado.py etapa --numero … if it was a manual adjustment."))
    tol = e.get("tolerancias", {}).get("proyecto", {})
    faltan = [d for d in ("tiempo", "costo") if not tol.get(d)]
    if faltan and (e.get("proyecto_autorizado") or fase in ("entrega",)):
        add("ERROR", "EST-06", T(f"Proyecto autorizado sin tolerancias de proyecto: {', '.join(faltan)}.", f"Authorized project without project tolerances: {', '.join(faltan)}."), "estado.py tolerancia --nivel proyecto tiempo=… costo=…")
    if fase == "entrega" and not any(e.get("tolerancias", {}).get("etapa", {}).values()):
        add("AVISO", "EST-07", T("Etapa de entrega sin tolerancias de etapa.", "Delivery stage without stage tolerances."), "estado.py tolerancia --nivel etapa …")
    r = e.get("roles", {})
    if fase != "pre-proyecto" and not r.get("ejecutivo"): add("ERROR", "EST-08", T("Sin ejecutivo designado (no hay proyecto sin ejecutivo).", "No executive appointed (there is no project without an executive)."), "estado.py rol ejecutivo=…")
    if r.get("ejecutivo") and r.get("ejecutivo") == r.get("gestor_proyecto"): add("ERROR", "EST-09", T("El ejecutivo y el gestor son la misma persona.", "The executive and the project manager are the same person."), T("Separar los roles.", "Separate the roles."))
    if r.get("gestor_proyecto") and r.get("gestor_proyecto") in (r.get("aseguramiento") or []): add("ERROR", "EST-10", T("El gestor figura en aseguramiento.", "The project manager is listed under assurance."), T("El aseguramiento es independiente del gestor.", "Assurance is independent of the project manager."))
    for p in e.get("puertas", []):
        if p.get("decision") == "pendiente" and not p.get("resuelta"): add("AVISO", "EST-11", T(f"Puerta pendiente: {p['tipo']} ({p.get('fecha')}).", f"Pending gate: {p['tipo']} ({p.get('fecha')})."), T("Llevarla a la junta (pm-puerta).", "Take it to the board (pm-puerta)."))
        if p.get("decision") in ("condicionado", "aprobado") and p.get("condiciones") and not p.get("condiciones_cumplidas"):
            add("AVISO", "EST-12", T(f"Condiciones abiertas de {p['tipo']}: {p['condiciones']}.", f"Open conditions of {p['tipo']}: {p['condiciones']}."), T("estado.py cumplir-condiciones <tipo> cuando se cumplan.", "estado.py cumplir-condiciones <tipo> once they are met."))
        if p.get("forzada"): add("AVISO", "EST-13", T(f"La puerta {p['tipo']} se registró con --forzar.", f"Gate {p['tipo']} was recorded with --forzar."), T("Justificar en decisiones.csv.", "Justify it in decisiones.csv."))
    if e.get("excepcion_abierta"): add("AVISO", "EST-14", T(f"Excepción abierta {e['excepcion_abierta']} esperando plan de excepción.", f"Open exception {e['excepcion_abierta']} awaiting an exception plan."), "")

# ------------------------------------------------------------------ ART: artefactos
def chk_artefactos(proyecto, e):
    _idioma(e)
    for k, a in e.get("artefactos", {}).items():
        ruta = os.path.join(proyecto, a.get("ruta", ""))
        if not os.path.exists(ruta):
            add("ERROR", "ART-01", T(f"Artefacto {k} registrado pero no existe: {a.get('ruta')}.", f"Artifact {k} is registered but does not exist: {a.get('ruta')}."), T("Restaurarlo o corregir la ruta con estado.py artefacto.", "Restore it or fix the path with estado.py artefacto."))
            continue
        if a.get("externo"):
            if not a.get("sha256"): add("AVISO", "ART-04", T(f"Especificación externa {k} sin huella.", f"External specification {k} without a hash."), T("Registrar con bmad.py linea-base.", "Record it with bmad.py linea-base."))
            continue
        if a.get("estado") == "aprobado" and not a.get("aprobado_por"): add("AVISO", "ART-02", T(f"{k} aprobado sin aprobado_por.", f"{k} approved without aprobado_por."), "estado.py aprobar … --por …")
        if ruta.endswith(".md"):
            fm = leer_fm(ruta) or {}
            if fm.get("estado") and fm["estado"] != a.get("estado"):
                add("AVISO", "ART-03", T(f"{k}: estado.json dice '{a.get('estado')}' y el documento '{fm['estado']}'.", f"{k}: estado.json says '{a.get('estado')}' and the document '{fm['estado']}'."), T("estado.py artefacto/aprobar sincroniza ambos.", "estado.py artefacto/aprobar keeps both in sync."))
    for p in glob.glob(os.path.join(proyecto, "00-direccion", "historial", "*")):
        pass  # las copias congeladas no se validan contra su contenido; el hook impide editarlas

# ------------------------------------------------------------------ REG: registros
def chk_registros(proyecto, e, reparar, corte=None):
    _idioma(e)
    hoy = corte or datetime.date.today().isoformat(); ids_todos = set()
    filas_por = {}
    for reg, spec in E.REGISTROS.items():
        p = E.ruta_registro(proyecto, reg)
        if spec.get("opcional") and not os.path.exists(p): continue      # maestro de interesados: se crea al primer uso
        if not os.path.exists(p): add("ERROR", "REG-01", T(f"Falta el registro {reg}.csv.", f"Register {reg}.csv is missing."), T("sanidad.py --reparar lo crea vacío.", "sanidad.py --reparar creates it empty."));
        try:
            if reparar: E.asegurar_registro(proyecto, reg)
            # sin --reparar la sanidad no escribe ni toma el bloqueo (carpeta de solo lectura): el registro que falta (REG-01) se evalúa vacío
            cols, filas = E.leer_csv(p) if os.path.exists(p) else (list(spec["columnas"]), [])
        except E.DatosIlegibles as x:
            ilegible(proyecto, x); continue
        faltan = [c for c in spec["columnas"] if c not in cols]
        if faltan: add("AVISO", "REG-02", T(f"{reg}.csv sin columnas del esquema v2: {', '.join(faltan)}.", f"{reg}.csv lacks schema v2 columns: {', '.join(faltan)}."), T("sanidad.py --reparar (o cualquier registro.py) las agrega.", "sanidad.py --reparar (or any registro.py) adds them."))
        vistos = set()
        for f in filas:
            i = f.get("id", "")
            if not re.match(rf"^{spec['prefijo']}-\d{{3,}}$", i): add("ERROR", "REG-03", T(f"{reg}: id inválido '{i}'.", f"{reg}: invalid id '{i}'."), T(f"Formato {spec['prefijo']}-###.", f"Format {spec['prefijo']}-###."))
            if i in vistos: add("ERROR", "REG-04", T(f"{reg}: id duplicado {i}.", f"{reg}: duplicate id {i}."), T("Renumerar el duplicado.", "Renumber the duplicate."))
            vistos.add(i); ids_todos.add(i)
            for col, perm in spec.get("valores", {}).items():
                v = f.get(col, "")
                if v and v not in perm: add("ERROR", "REG-05", T(f"{reg} {i}: {col}='{v}' fuera del esquema.", f"{reg} {i}: {col}='{v}' outside the schema."), T(f"Valores: {', '.join(x for x in perm if x)}", f"Values: {', '.join(x for x in perm if x)}"))
            for col, perm in spec.get("multivalor", {}).items():
                malos = [x.strip() for x in re.split(r"[;,]", f.get(col, "") or "") if x.strip() and x.strip() not in perm]
                if malos: add("ERROR", "REG-05", T(f"{reg} {i}: {col}='{'; '.join(malos)}' fuera del esquema.", f"{reg} {i}: {col}='{'; '.join(malos)}' outside the schema."), T(f"Valores (uno o más, separados por ;): {', '.join(perm)}", f"Values (one or more, separated by ;): {', '.join(perm)}"))
            for col in spec.get("enteros_1_5", []):
                v = f.get(col, "")
                if v and not (v.isdigit() and 1 <= int(v) <= 5): add("ERROR", "REG-05", T(f"{reg} {i}: {col}='{v}' no es 1–5.", f"{reg} {i}: {col}='{v}' is not 1–5."), "")
        filas_por[reg] = filas
    for f in filas_por.get("riesgos", []):
        if f.get("estado") in E.REGISTROS["riesgos"]["abiertos"]:
            try: pts = float(f.get("puntuacion") or 0)
            except ValueError: pts = 0
            umbral = float((e.get("umbrales_riesgo") or {}).get("alto", E.UMBRAL_RIESGO_ALTO))
            if pts >= umbral and not (f.get("respuesta") and f.get("propietario")):
                add("AVISO", "REG-06", T(f"Riesgo alto {f['id']} sin respuesta o propietario.", f"High risk {f['id']} without a response or owner."), "pm-riesgos.")
    for f in filas_por.get("acciones", []):
        if f.get("estado") in ("abierta", "en-curso") and f.get("fecha_compromiso") and f["fecha_compromiso"] < hoy:
            add("AVISO", "REG-07", T(f"Acción vencida {f['id']} ({f.get('responsable','sin responsable')}, {f['fecha_compromiso']}).", f"Overdue action {f['id']} ({f.get('responsable','no owner')}, {f['fecha_compromiso']})."), T("Recordatorio o replanificación.", "Reminder or re-planning."))
    for f in filas_por.get("riesgos", []):
        if f.get("estado") in E.REGISTROS["riesgos"]["abiertos"] and f.get("fecha_revision") and f["fecha_revision"] < hoy:
            add("AVISO", "REG-09", T(f"Riesgo {f['id']} abierto con la revisión vencida ({f['fecha_revision']}; propietario: {f.get('propietario') or 'sin propietario'}).",
                                     f"Open risk {f['id']} with its review overdue ({f['fecha_revision']}; owner: {f.get('propietario') or 'no owner'})."),
                T("Revisarlo con el propietario (pm-riesgos) y actualizar estado, evaluación y fecha_revision (registro.py actualizar riesgos R-… --campo fecha_revision=…).",
                  "Review it with the owner (pm-riesgos) and update status, assessment and fecha_revision (registro.py actualizar riesgos R-… --campo fecha_revision=…)."))
    # REG-10: amenaza alta con respuesta sin opciones evaluadas, o aceptada sin disparador o plan de contingencia (pm-riesgos/riesgos.py)
    if filas_por.get("riesgos"):
        try:
            sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-riesgos", "scripts"))); import riesgos as RK
            RK.IDIOMA = IDIOMA
            for sev, cod, msg, arreglo in RK.controles(proyecto, e, filas_por["riesgos"]): add(sev, cod, msg, arreglo)
        except E.DatosIlegibles as x: ilegible(proyecto, x)
        except BaseException as x:
            add("AVISO", "REG-10", T(f"No se pudieron verificar las opciones de respuesta: {x}", f"The response options could not be checked: {x}"), T("Revisar que pm-riesgos esté instalada junto a pm-estado-proyecto.", "Check that pm-riesgos is installed next to pm-estado-proyecto."))
    # REG-11/REG-12: ciclo de las lecciones (impacto alto sin acción ni decisión; accionada sin verificar su efecto) (pm-lecciones-aprendidas/lecciones.py)
    if filas_por.get("lecciones"):
        try:
            sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-lecciones-aprendidas", "scripts"))); import lecciones as LX
            for sev, cod, msg, arreglo in LX.controles(filas_por["lecciones"], hoy, e.get("idioma", "es")): add(sev, cod, msg, arreglo)
        except E.DatosIlegibles as x: ilegible(proyecto, x)
        except BaseException as x:
            add("AVISO", "REG-11", T(f"No se pudo revisar el ciclo de las lecciones: {x}", f"The lessons cycle could not be checked: {x}"), T("Revisar que pm-lecciones-aprendidas esté instalada junto a pm-estado-proyecto.", "Check that pm-lecciones-aprendidas is installed next to pm-estado-proyecto."))
    # referencias cruzadas entre registros (R-, I-, C-, D-, S-, L-, ST-, Q-, A-, ET-, PF-, RC-, EN-, PU-)
    for reg, filas in filas_por.items():
        for f in filas:
            if reg == "lecciones" and f.get("origen"): continue   # lección previa de otro proyecto: cita ids de su proyecto de origen
            texto = " ".join(str(v) for k, v in f.items() if k != "id")
            for ref in set(re.findall(r"\b(?:R|I|C|D|S|L|ST|Q|A|ET|PF|RC|EN|PU)-\d{3}\b", texto)):
                if ref not in ids_todos: add("AVISO", "REG-08", T(f"{reg} {f.get('id')} cita {ref}, que no existe.", f"{reg} {f.get('id')} cites {ref}, which does not exist."), T("Corregir la referencia.", "Fix the reference."))
    return filas_por

# ------------------------------------------------------------------ controles permanentes: CAM cambios y presupuestos ·
# QUA calidad a volumen · TOL pronóstico contra tolerancias (lo que en la práctica se revisa a mano, tarde o nunca)
_num = E.monto
def _m(x): return f"{x:,.0f}" if IDIOMA == "en" else f"{x:,.0f}".replace(",", ".")   # miles con punto en español, con coma en inglés
_es_junta = E.es_junta

def chk_cambios(proyecto, e, filas_por):
    _idioma(e)
    pres = e.get("presupuestos", {}) or {}
    for f in filas_por.get("cambios", []):
        if E.cambio_contradictorio(f):   # registro.py ya no lo deja escribir: datos anteriores o escritos fuera de los scripts
            vig = E.cambio_vigente(f)
            add("AVISO", "CAM-06", T(f"Cambio {f['id']} con decision={f.get('decision')} y estado={f.get('estado')}, que se contradicen; "
                                     + ("cuenta contra el presupuesto por el estado." if vig else "no cuenta contra el presupuesto."),
                                     f"Change {f['id']} with decision={f.get('decision')} and estado={f.get('estado')}, which contradict each other; "
                                     + ("it counts against the budget because of estado." if vig else "it does not count against the budget.")),
                T(f"Corregir la que no corresponde: registro.py actualizar cambios {f['id']} --campo decision=… --campo estado=… (guía de registros §3).",
                  f"Fix the one that does not apply: registro.py actualizar cambios {f['id']} --campo decision=… --campo estado=… (register guide §3)."))
        if not E.cambio_vigente(f): continue
        costo = _num(f.get("costo")); cargo = f.get("cargo", "")
        if costo is None:
            if re.search(r"\d", f.get("impacto_costo", "") or "") and not cargo:
                add("AVISO", "CAM-01", T(f"Cambio aprobado {f['id']} con impacto de costo ('{f.get('impacto_costo')}') sin monto en 'costo' ni 'cargo'.",
                                         f"Approved change {f['id']} with a cost impact ('{f.get('impacto_costo')}') and no amount in 'costo' or 'cargo'."),
                    T("registro.py actualizar cambios C-… --campo costo=<monto> --campo cargo=presupuesto-cambio|reserva-riesgo|reserva-gestion|plan-excepcion",
                      "registro.py actualizar cambios C-… --campo costo=<amount> --campo cargo=presupuesto-cambio|reserva-riesgo|reserva-gestion|plan-excepcion"))
            continue
        if costo > 0 and not cargo:
            add("AVISO", "CAM-01", T(f"Cambio aprobado {f['id']} por {_m(costo)} sin 'cargo' (¿contra qué presupuesto?).", f"Approved change {f['id']} for {_m(costo)} without 'cargo' (charged to which budget?)."),
                T("Indicar cargo: presupuesto-cambio (lo habitual), reserva-riesgo, reserva-gestion o plan-excepcion.", "Set cargo: presupuesto-cambio (the usual one), reserva-riesgo, reserva-gestion or plan-excepcion."))
        if cargo == "reserva-riesgo" and not re.search(r"\bR-\d{3}\b", " ".join(str(f.get(k, "")) for k in ("descripcion", "justificacion", "impacto_riesgo", "notas"))):
            add("AVISO", "CAM-02", T(f"Cambio {f['id']} cargado a la reserva de riesgo sin citar el riesgo R-### que responde.", f"Change {f['id']} charged to the risk reserve without citing the R-### risk it responds to."),
                T("La reserva de riesgo solo financia respuestas a riesgos; si no, presupuesto de cambio o junta.", "The risk reserve only funds risk responses; otherwise, change budget or the board."))
        if cargo == "reserva-gestion" and not _es_junta(e, f.get("decidido_por")):
            add("AVISO", "CAM-05", T(f"Cambio {f['id']} usa la reserva de gestión decidido por '{f.get('decidido_por')}', no por la junta o el ejecutivo.", f"Change {f['id']} uses the management reserve, decided by '{f.get('decidido_por')}', not by the board or the executive."),
                T("Solo la junta libera la reserva de gestión (pm-director).", "Only the board releases the management reserve (pm-director)."))
        lim = _num(pres.get("limite_autoridad_cambio"))
        if lim is not None and costo > lim and not _es_junta(e, f.get("decidido_por")):
            add("AVISO", "CAM-04", T(f"Cambio {f['id']} ({_m(costo)}) supera el límite de la autoridad de cambio ({_m(lim)}) y lo decidió '{f.get('decidido_por')}'.", f"Change {f['id']} ({_m(costo)}) exceeds the change authority's limit ({_m(lim)}) and was decided by '{f.get('decidido_por')}'."),
                T("Escalar a la junta y registrar su decisión (decision-ad-hoc), o ajustar el límite delegado.", "Escalate to the board and record its decision (decision-ad-hoc), or adjust the delegated limit."))
    consumo = E.consumo_cambios(filas_por.get("cambios", []))   # misma regla que registro.py al aprobar
    for cargo, clave, nombre, nombre_en in (("presupuesto-cambio", "cambio", "presupuesto de cambio", "change budget"), ("reserva-riesgo", "riesgo", "reserva de riesgo", "risk reserve")):
        usado = consumo[cargo]; tope = _num(pres.get(clave))
        if not usado: continue
        if tope is None:
            add("AVISO", "CAM-03", T(f"Se cargaron {_m(usado)} a {nombre} pero la junta no fijó ese presupuesto.", f"{_m(usado)} were charged to the {nombre_en} but the board did not set that budget."),
                T(f"pm-director: estado.py presupuesto {clave}=<monto> --por …", f"pm-director: estado.py presupuesto {clave}=<amount> --por …"))
        elif usado > tope:
            add("ERROR", "CAM-03", T(f"{nombre.capitalize()} excedido: {_m(usado)} de {_m(tope)} ({100 * usado / tope:.0f} %).", f"{nombre_en.capitalize()} exceeded: {_m(usado)} of {_m(tope)} ({100 * usado / tope:.0f} %)."),
                T("Escalar a la junta: informe de excepción o ampliación del presupuesto (decisión registrada).", "Escalate to the board: exception report or budget increase (recorded decision)."))
        elif usado >= 0.8 * tope:
            add("AVISO", "CAM-03", T(f"{nombre.capitalize()} al {100 * usado / tope:.0f} % ({_m(usado)} de {_m(tope)}).", f"{nombre_en.capitalize()} at {100 * usado / tope:.0f} % ({_m(usado)} of {_m(tope)})."),
                T("Avisar a la junta antes de aprobar más cambios.", "Warn the board before approving more changes."))
        else:
            add("INFO", "CAM-03", T(f"{nombre.capitalize()}: {_m(usado)} de {_m(tope)} ({100 * usado / tope:.0f} %).", f"{nombre_en.capitalize()}: {_m(usado)} of {_m(tope)} ({100 * usado / tope:.0f} %)."))

def chk_supuestos(proyecto, e, filas_por, corte):
    """SUP: supuestos críticos tratados como hipótesis (validar antes de invertir); SUP-04, supuesto transferido sin el
    riesgo o issue que lo recibe (esquema.destino_transferido; registro.py ya no lo deja escribir)."""
    _idioma(e)
    sup = filas_por.get("supuestos", [])
    citado = " ".join(" ".join(str(v) for v in f.values()) for reg in ("issues", "cambios", "decisiones", "riesgos") for f in filas_por.get(reg, []))
    for f in sup:
        abierto = f.get("estado") == "abierto" and f.get("validado") != "si"
        if abierto and f.get("criticidad") == "alta" and (not f.get("experimento") or not f.get("fecha_limite")):
            add("AVISO", "SUP-01", T(f"Supuesto crítico {f['id']} sin {'experimento' if not f.get('experimento') else 'fecha límite'} para validarlo: «{(f.get('supuesto_o_restriccion') or '')[:70]}».",
                                     f"Critical assumption {f['id']} without {'an experiment' if not f.get('experimento') else 'a deadline'} to validate it: «{(f.get('supuesto_o_restriccion') or '')[:70]}»."),
                T("Definir cómo se valida (experimento), el criterio para seguir y la fecha límite (registro.py actualizar supuestos S-…).",
                  "Define how it is validated (experiment), the criterion to continue and the deadline (registro.py actualizar supuestos S-…)."))
        if abierto and f.get("fecha_limite") and f["fecha_limite"] < corte:
            add("AVISO", "SUP-02", T(f"Supuesto {f['id']} con fecha límite {f['fecha_limite']} vencida y sin validar.", f"Assumption {f['id']} with deadline {f['fecha_limite']} passed and not validated."),
                T("Registrar la evidencia y el resultado (validado=si|no) o replanificar con la junta.", "Record the evidence and the result (validado=si|no) or re-plan with the board."))
        if (f.get("validado") == "no" or f.get("estado") == "invalidado") and not re.search(rf"\b{re.escape(f['id'])}\b", citado):
            add("AVISO", "SUP-03", T(f"Supuesto {f['id']} invalidado sin issue, cambio, riesgo o decisión que trate su efecto.", f"Assumption {f['id']} invalidated with no issue, change, risk or decision handling its effect."),
                T("Revisar el business case y registrar la decisión (pm-caso-de-negocio, pm-direccion-decisiones).", "Review the business case and record the decision (pm-caso-de-negocio, pm-direccion-decisiones)."))
        if f.get("estado") == "transferido":
            destino = E.destino_transferido(f)
            existentes = {x.get("id") for reg in ("riesgos", "issues") for x in filas_por.get(reg, [])}
            if not destino or destino not in existentes:
                add("AVISO", "SUP-04", T(f"Supuesto {f['id']} transferido " + (f"a {destino}, que no existe en riesgos.csv ni en issues.csv." if destino else "sin el riesgo o issue que lo recibe (notas sin «→ R-###» ni «→ I-###»)."),
                                         f"Assumption {f['id']} transferred " + (f"to {destino}, which does not exist in riesgos.csv or issues.csv." if destino else "without the risk or issue that receives it (notas without «→ R-###» or «→ I-###»).")),
                    T(f"Registrar el riesgo o issue que lo recibe y citarlo: registro.py actualizar supuestos {f['id']} --campo \"notas=→ R-###\" (o → I-###), o volver a estado=abierto (guía de registros, supuestos).",
                      f"Record the risk or issue that receives it and cite it: registro.py actualizar supuestos {f['id']} --campo \"notas=→ R-###\" (or → I-###), or go back to estado=abierto (register guide, assumptions)."))

TERMINADO = {"done", "terminado", "terminada", "hecho", "hecha", "completado", "completada", "cerrado", "cerrada", "aceptado", "aceptada"}

def chk_calidad(proyecto, e, filas_por, corte):
    _idioma(e)
    q = filas_por.get("calidad", [])
    texto_q = [(f, " ".join(str(f.get(k, "")) for k in ("producto", "criterios", "notas"))) for f in q]
    p = os.path.join(proyecto, "02-planificacion", "backlog.csv")
    if os.path.exists(p):
        for b in E.leer_filas(p):
            if (b.get("estado") or "").strip().lower() not in TERMINADO: continue
            bid = b.get("id", ""); corto = (re.match(r"^(\d+-\d+)(?:-|$)", bid) or [None, None])[1]
            pat = re.compile(rf"(?<![\w-]){re.escape(bid)}(?![\w-])" + (rf"|(?<![\w.-]){re.escape(corto)}(?![\w-]|\.\d|\d)" if corto else ""))   # «historia 1-2.» sí; «1-2.3» no
            rev = [f for f, t in texto_q if pat.search(t)]
            if not rev:
                add("AVISO", "QUA-01", T(f"{bid}: terminado sin revisión de calidad registrada.", f"{bid}: done with no quality review recorded."),
                    T("pm-calidad: registrar la revisión (registro.py agregar calidad --campo producto=\"… historia N-M\") o aplicar el criterio de aceptación por lote.",
                      "pm-calidad: record the review (registro.py agregar calidad --campo producto=\"… historia N-M\") or apply the batch acceptance criterion."))
            elif not any(f.get("estado") == "completada" and f.get("resultado") in ("aprobado", "aprobado-con-observaciones") for f in rev):
                add("AVISO", "QUA-01", T(f"{bid}: terminado con revisión {', '.join(f['id'] for f in rev)} sin aprobar.", f"{bid}: done with review {', '.join(f['id'] for f in rev)} not approved."),
                    T("Completar la revisión o reabrir el elemento.", "Complete the review or reopen the item."))
    for f in q:
        if f.get("estado") in ("planificada", "en-curso") and f.get("fecha_prevista") and f["fecha_prevista"] < corte:
            add("AVISO", "QUA-02", T(f"Revisión de calidad vencida {f['id']} ({f.get('producto', '')[:60]}, prevista {f['fecha_prevista']}).", f"Overdue quality review {f['id']} ({f.get('producto', '')[:60]}, planned {f['fecha_prevista']})."),
                T("Realizarla o replanificarla.", "Hold it or reschedule it."))
    citados = " ".join(" ".join(str(v) for v in f.values()) for reg in ("issues", "acciones", "cambios") for f in filas_por.get(reg, []))
    for f in q:
        if f.get("resultado") == "rechazado" and not re.search(rf"\b{re.escape(f['id'])}\b", citados):
            add("AVISO", "QUA-03", T(f"Revisión {f['id']} rechazada sin issue, acción o cambio que la trate.", f"Review {f['id']} rejected with no issue, action or change handling it."),
                T("pm-issues-cambios (fuera de especificación) o una acción correctiva que cite el Q-###.", "pm-issues-cambios (off-specification) or a corrective action citing the Q-###."))
    # QUA-04, el equivalente de QUA-01 para los productos de la WBS (proyectos predictivos): elemento aceptado
    # (aceptacion-<código>) o con su paquete recibido sin revisión aprobada que lo cite («producto 3.1»); misma derivación que
    # estado.py productos (registro de productos de PRINCE2, A13)
    if os.path.exists(os.path.join(proyecto, "02-planificacion", "wbs.csv")):
        try:
            import estado as ESTADO_PY
            dp = ESTADO_PY.productos(proyecto, e, corte, fuente="wbs", must=False)
        except Exception:
            dp = {"discrepancias": []}
        for z in dp["discrepancias"]:
            if z["control"] == "QUA-04":
                add("AVISO", "QUA-04", T(f"Producto {z['producto']} de la WBS: {z['texto']}.", f"WBS product {z['producto']}: {z['texto']}."),
                    T("pm-calidad: registrar la revisión que cite «producto <código>» (registro.py agregar calidad) o revisar la aceptación o la recepción.",
                      "pm-calidad: record the review citing «producto <code>» (registro.py agregar calidad) or check the acceptance or the receipt."))

def chk_tolerancias(proyecto, e, corte):
    _idioma(e)
    xs = sorted(glob.glob(os.path.join(proyecto, "03-control", "reportes", "evm-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json")))
    xs = [x for x in xs if os.path.basename(x)[4:14] <= corte]
    if not xs:
        if e.get("fase") == "entrega": add("INFO", "TOL-03", T("Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.", "Delivery stage with no saved EVM cut-off: the forecast against tolerances is not monitored."),
                                           T("evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.", "evm.py … --proyecto <dir> --guardar --corte YYYY-MM-DD in each period."))
        return
    ult = E.leer_json(xs[-1]); f = ult.get("corte", os.path.basename(xs[-1])[4:14])
    sem = {k: ult.get(k) for k in ("semaforo_costo", "semaforo_cronograma", "semaforo_alcance") if ult.get(k)}
    if ult.get("excepcion_prevista"):
        tratada = bool(e.get("excepcion_abierta")) or any(p.get("tipo") == "autorizar-plan-excepcion" and (p.get("fecha") or "") >= f for p in e.get("puertas", []))
        if not tratada:
            add("AVISO", "TOL-01", T(f"El EVM del {f} pronostica salir de la tolerancia ({', '.join(f'{k[9:]}={v}' for k, v in sem.items())}) y no hay excepción abierta.",
                                     f"The EVM of {f} forecasts going outside tolerance ({', '.join(f'{k[9:]}={v}' for k, v in sem.items())}) and there is no open exception."),
                T("pm-progreso-reportes: informe de excepción; pm-director: estado.py limite-etapa --excepcion X-### y puerta autorizar-plan-excepcion.",
                  "pm-progreso-reportes: exception report; pm-director: estado.py limite-etapa --excepcion X-### and gate autorizar-plan-excepcion."))
    elif any(str(v).startswith("ambar") or str(v).startswith("ámbar") for v in sem.values()):
        add("INFO", "TOL-02", T(f"El EVM del {f} está en ámbar ({', '.join(f'{k[9:]}={v}' for k, v in sem.items())}): 50–100 % de la tolerancia.", f"The EVM of {f} is amber ({', '.join(f'{k[9:]}={v}' for k, v in sem.items())}): 50–100 % of tolerance."),
            T("Anticipar acciones correctivas y reportarlo en el highlight.", "Anticipate corrective actions and report it in the highlight."))
    try:
        if e.get("fase") == "entrega" and (datetime.date.fromisoformat(corte) - datetime.date.fromisoformat(f)).days > 31:
            add("INFO", "TOL-03", T(f"Último corte de EVM guardado el {f} (más de 31 días).", f"Last EVM cut-off saved on {f} (more than 31 days)."), T("evm.py … --guardar en cada período de informe.", "evm.py … --guardar in each reporting period."))
    except ValueError: pass

# ------------------------------------------------------------------ ESP: especificación y columna vertebral BMAD
def chk_especificacion(proyecto, e, filas_por, reparar, rapido):
    import especificacion as SP
    _idioma(e)
    bm = e.get("integraciones", {}).get("especificacion") == "bmad"
    try:
        h = SP.huella(proyecto, e)
    except SystemExit as x:
        add("ERROR", "ESP-01", T(f"No se pudo leer la especificación: {x}", f"The specification could not be read: {x}"), T("Revisar integraciones.bmad.raiz o correr bmad.py detectar.", "Check integraciones.bmad.raiz or run bmad.py detectar.")); return
    ri = SP.ruta_indice(proyecto)
    try: vigente = os.path.exists(ri) and E.leer_json(ri).get("_huella") == h
    except E.DatosIlegibles: vigente = False      # caché derivada ilegible: se reconstruye (ESP-02), no es un dato de gobierno
    if not vigente:
        if reparar: SP.obtener(proyecto, forzar=True); add("INFO", "ESP-02", T("Índice de especificación reconstruido.", "Specification index rebuilt."))
        else: add("INFO", "ESP-02", T("El índice de especificación está desactualizado (se reconstruye solo al consultarlo).", "The specification index is out of date (it is rebuilt automatically when queried)."), T("especificacion.py indice o sanidad.py --reparar.", "especificacion.py indice or sanidad.py --reparar."))
    if rapido and not bm: return
    idx, _ = SP.obtener(proyecto)
    ids = {x["id"] for x in idx.get("requisitos", [])} | {x["id"] for x in idx.get("historias", [])} | {x["id"] for x in idx.get("epicas", [])}
    sinc = [q["id"] for q in idx.get("requisitos", []) if q.get("cobertura") == "sin-cobertura"]
    if sinc: add("AVISO" if e.get("fase") in ("pre-proyecto", "inicio") else "ERROR", "ESP-03", T(f"Requisitos sin cobertura (ni historia ni paquete de la WBS): {', '.join(sinc)}.", f"Requirements without coverage (no story or WBS work package): {', '.join(sinc)}."),
                 T("Planificarlos (pm-planificacion-por-productos / pm-agil-hibrido) o retirarlos mediante control de cambios.", "Plan them (pm-planificacion-por-productos / pm-agil-hibrido) or withdraw them through change control."))
    patron = re.compile(r"\b(?:REQ-\d{3}|FR-\d+|NFR-\d+|UJ-\d+|SM-\d+|AD-\d+|UX-DR-\d+)\b")
    def revisar(nombre, texto):
        for r in set(patron.findall(texto)):
            if r not in ids: add("ERROR", "ESP-04", T(f"{nombre} cita {r}, que no existe en la especificación vigente ({idx['proveedor']}).", f"{nombre} cites {r}, which does not exist in the current specification ({idx['proveedor']})."),
                                 T("Corregir el id o tramitar el cambio de alcance.", "Fix the id or process the scope change."))
    pw = os.path.join(proyecto, "02-planificacion", "wbs.csv")
    if os.path.exists(pw):
        for r in E.leer_filas(pw): revisar(f"wbs.csv {r.get('codigo')}", r.get("ref", ""))
    for reg in ("riesgos", "issues", "calidad", "supuestos"):
        for f in filas_por.get(reg, []): revisar(f"{reg} {f.get('id')}", " ".join(str(v) for v in f.values()))
    po = os.path.join(proyecto, "00-direccion", "okr.csv")
    if os.path.exists(po):
        bc = ""
        for c in glob.glob(os.path.join(proyecto, "00-direccion", "*business-case*.md")): bc += open(c, encoding="utf-8").read()
        for r in E.leer_filas(po):
            if r.get("tipo") != "kr": continue
            v = r.get("vinculo", "")
            revisar(f"okr {r.get('id')}", v)
            for b in re.findall(r"\bB-?\d+\b", v):
                if bc and not re.search(r"\b" + re.escape(b) + r"\b|\bB-0*" + re.sub(r"\D", "", b) + r"\b", bc): add("AVISO", "ESP-05", T(f"okr {r.get('id')} cita el beneficio {b}, que no aparece en el business case.", f"okr {r.get('id')} cites benefit {b}, which does not appear in the business case."), T("Alinear con pm-caso-de-negocio.", "Align it with pm-caso-de-negocio."))
    if not bm: return
    sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-bmad-puente", "scripts")))
    import bmad as B
    try: b = B.detectar_bmad(proyecto, None, e)
    except SystemExit as x: add("ERROR", "ESP-06", T(f"BMAD declarado pero no detectado: {x}", f"BMAD declared but not detected: {x}"), "bmad.py detectar --raiz …"); return
    if b["soporte"] not in ("soportada", "v4"): add("AVISO", "ESP-07", T(f"Versión de BMAD {b['soporte']} (probadas: {B.VERSIONES_SOPORTADAS}).", f"BMAD version {b['soporte']} (tested: {B.VERSIONES_SOPORTADAS})."), T("Correr scripts/probar_paquete.py del paquete y revisar el inventario.", "Run the package's scripts/probar_paquete.py and review the inventory."))
    pa = os.path.abspath(proyecto)
    for d in b.get("carpetas_protegidas", []):
        if pa.startswith(os.path.abspath(d) + os.sep): add("ERROR", "ESP-08", T("La carpeta del proyecto está dentro de una carpeta de BMAD.", "The project folder is inside a BMAD folder."), T("Moverla fuera (p. ej. <repo>/gestion).", "Move it out (e.g. <repo>/gestion)."))
    arts = B.inventario(b)
    # desvíos contra líneas base: cada uno debe tener un issue/cambio abierto que lo cite
    texto_cambios = " ".join(" ".join(str(v) for v in f.values()) for reg in ("issues", "cambios") for f in filas_por.get(reg, [])
                             if f.get("estado") not in ("cerrado", "resuelto", "rechazado"))
    for art_k, clave in B.CLAVES_LB.items():
        lb = e.get("artefactos", {}).get(clave)
        if not lb or "sha256" not in lb: continue
        if art_k not in arts: add("ERROR", "ESP-09", T(f"El artefacto con línea base {clave} ya no se encuentra en BMAD.", f"The baselined artifact {clave} is no longer found in BMAD."), T("Investigar y tramitar como cambio.", "Investigate and process it as a change.")); continue
        if arts[art_k]["sha256"] != lb["sha256"]:
            nuevos = set(B.ids_de(arts, art_k)) ^ set(lb.get("ids", []))
            citado = clave in texto_cambios or any(i in texto_cambios for i in nuevos) or art_k in texto_cambios
            if citado: add("AVISO", "ESP-10", T(f"{clave} difiere de su línea base v{lb.get('version')} y hay un issue/cambio abierto que lo trata.", f"{clave} differs from its baseline v{lb.get('version')} and an open issue/change handles it."),
                           T("Al aprobarse: bmad.py linea-base con versión mayor.", "Once approved: bmad.py linea-base with a higher version."))
            else: add("ERROR", "ESP-10", T(f"Cambio no controlado: {clave} difiere de la línea base v{lb.get('version')}{' (ids ' + ', '.join(sorted(nuevos)) + ')' if nuevos else ''} y ningún issue/cambio abierto lo cita.",
                                           f"Uncontrolled change: {clave} differs from baseline v{lb.get('version')}{' (ids ' + ', '.join(sorted(nuevos)) + ')' if nuevos else ''} and no open issue/change cites it."),
                      T("pm-issues-cambios: registrar solicitud-cambio (o declarar elaboración progresiva y fijar nueva línea base).", "pm-issues-cambios: record a solicitud-cambio (or declare progressive elaboration and set a new baseline)."))
    if e.get("fase") in ("entrega", "cierre", "cerrado") and "bmad-prd" not in e.get("artefactos", {}):
        add("ERROR", "ESP-11", T("Etapas de entrega sin línea base del PRD.", "Delivery stages without a PRD baseline."), "pm-director: bmad.py linea-base prd --version 1.0 --por …")
    vistas = set(e.get("integraciones", {}).get("bmad", {}).get("propuestas_vistas", []))
    for r in arts.get("propuestas-cambio", {}).get("rutas", []):
        rel = os.path.relpath(r, b["raiz"])
        if rel not in vistas and os.path.basename(r) not in texto_cambios: add("AVISO", "ESP-12", T(f"Sprint Change Proposal sin tratar: {rel}.", f"Untreated Sprint Change Proposal: {rel}."), T("bmad.py verificar y registrar issue solicitud-cambio.", "bmad.py verificar and record a solicitud-cambio issue."))
    for hdf in e.get("integraciones", {}).get("bmad", {}).get("handoffs", []):
        fm = leer_fm(os.path.join(proyecto, hdf["archivo"])) or {}
        if fm.get("estado") != "aplicado":
            add("AVISO", "ESP-13", T(f"Traspaso a BMAD sin confirmar: {hdf['archivo']}.", f"Unconfirmed handoff to BMAD: {hdf['archivo']}."),
                T("Cuando el equipo BMAD lo aplique: marcar estado: aplicado en el documento, bmad.py verificar y nueva línea base.", "When the BMAD team applies it: set estado: aplicado in the document, bmad.py verificar and a new baseline."))
    # derivados editados a mano
    pr = os.path.join(proyecto, "02-planificacion", "especificacion", "requisitos-bmad.csv")
    if os.path.exists(pr):
        actual = [r.get("id") for r in E.leer_filas(pr)]
        if actual != [q["id"] for q in B.requisitos(b, arts)]: add("AVISO", "ESP-14", T("requisitos-bmad.csv no coincide con el PRD vigente (desactualizado o editado).", "requisitos-bmad.csv does not match the current PRD (out of date or edited)."), T("bmad.py requisitos (es derivado: no se edita).", "bmad.py requisitos (it is derived: do not edit it)."))
    pb = os.path.join(proyecto, "02-planificacion", "backlog.csv")
    if os.path.exists(pb):
        hs = B.historias(b, arts)
        for f in E.leer_filas(pb):
            if f.get("origen") != "bmad": continue
            h = hs.get(f["id"])
            if h and f.get("estado") != h["estado"]: add("AVISO", "ESP-15", T(f"backlog.csv {f['id']}: estado '{f.get('estado')}' ≠ BMAD '{h['estado']}'.", f"backlog.csv {f['id']}: status '{f.get('estado')}' ≠ BMAD '{h['estado']}'."), T("bmad.py backlog (sincroniza las columnas derivadas).", "bmad.py backlog (syncs the derived columns).")); break

# ------------------------------------------------------------------ INT: integraciones MCP (instantáneas)
def chk_integraciones(proyecto, e):
    _idioma(e)
    conocidos = E.VALORES_INTEGRACION
    for k, vals in conocidos.items():
        v = e.get("integraciones", {}).get(k)
        if k == "diagramas" and isinstance(v, str) and "," in v and all(x.strip() in vals for x in v.split(",")): continue
        if v and v not in vals: add("AVISO", "INT-01", T(f"integraciones.{k} = '{v}' no es un valor conocido ({', '.join(sorted(vals))}).", f"integraciones.{k} = '{v}' is not a known value ({', '.join(sorted(vals))})."),
                                    T("Usarlo solo si pm-integraciones sabe mapearlo; si no, corregir.", "Use it only if pm-integraciones knows how to map it; otherwise, fix it."))
    trk = e.get("integraciones", {}).get("tracker", "ninguno")
    if trk not in ("ninguno", None) and e.get("fase") == "entrega":
        snaps = sorted(glob.glob(os.path.join(proyecto, "03-control", "fuentes", f"{trk}-*")))
        if not snaps: add("AVISO", "INT-02", T(f"Tracker {trk} declarado sin instantáneas en 03-control/fuentes/.", f"Tracker {trk} declared without snapshots in 03-control/fuentes/."), T("pm-integraciones: leer y guardar instantánea fechada.", "pm-integraciones: read it and save a dated snapshot."))
        else:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(snaps[-1]))
            if m and (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days > 14:
                add("AVISO", "INT-03", T(f"La última instantánea de {trk} tiene más de 14 días ({m.group(1)}).", f"The last snapshot of {trk} is more than 14 days old ({m.group(1)})."), T("Actualizarla antes del próximo informe.", "Refresh it before the next report."))
    for f in glob.glob(os.path.join(proyecto, "03-control", "fuentes", "*")):
        if not re.search(r"-\d{4}-\d{2}-\d{2}\.\w+$", f): add("AVISO", "INT-04", T(f"Instantánea sin fecha en el nombre: {os.path.basename(f)}.", f"Snapshot without a date in its name: {os.path.basename(f)}."), T("<sistema>-AAAA-MM-DD.<ext>", "<system>-YYYY-MM-DD.<ext>"))

# ------------------------------------------------------------------ STK: maestro de interesados (integridad referencial y calidad)
ARREGLO_STK = {
    "STK-01": "Completar poder e interés (registro.py actualizar stakeholders ST-… --campo poder=… --campo interes=…).",
    "STK-02": "RACI: exactamente un A por elemento (registro.py actualizar raci RC-… --campo rol=…).",
    "STK-03": "Corregir la referencia al maestro (stakeholder_id / estereotipo) o crear el interesado o estereotipo faltante.",
    "STK-04": "Revalidar con la persona y confirmar de nuevo (interesados.py confirmar PF-… --por …) o rechazarla.",
    "STK-05": "Tratar las propuestas: interesados.py confirmar | rechazar PF-… --por …",
    "STK-06": "Asignarle un rol en la RACI de los elementos clave (A, R o C).",
    "STK-07": "Revisar el envío: envios.py enviar (reintento) o registrar --estado enviado|fallido.",
    "STK-08": "Usar el id ST-… o el nombre exacto del maestro en okr.csv (columna responsable).",
    "STK-09": "Corregir el id del elemento o su tipo_elemento (especificación, OKR, WBS, actividades, decisiones) o el id que cita la persona (capacidad o beneficio B-##).",
    "STK-10": "Unificar o diferenciar los nombres duplicados del maestro.",
    "STK-11": "Revisar la RACI (R faltante, sobre-consulta, concentración de A, A con poder bajo).",
    "STK-13": "Vincular el requisito o la épica Must a la persona que lo pide, lo usa o se beneficia (registro.py actualizar personas PU-… --campo usa=…) o revisar su prioridad.",
    "STK-14": "Mapear la persona a sus capacidades (solicita, usa, beneficia) o retirarla (registro.py actualizar personas PU-… --campo estado=retirada).",
    "STK-15": "Declarar la fuente de la persona (entrevista, bmad-uj, encuesta, observacion, documento o supuesto) y su evidencia.",
    "STK-16": "Registrar la persona del recorrido (interesados.py personas candidatos) o usar su nombre registrado o su persona_id en el mapa.",
    "STK-12": "Contactarlo según su perfil (envios.py o registrar la reunión o llamada: registro.py agregar envios --campo canal=reunion --campo modo=manual --campo estado=enviado …) o revisar la frecuencia acordada.",
}
ARREGLO_STK_EN = {
    "STK-01": "Fill in power and interest (registro.py actualizar stakeholders ST-… --campo poder=… --campo interes=…).",
    "STK-02": "RACI: exactly one A per item (registro.py actualizar raci RC-… --campo rol=…).",
    "STK-03": "Fix the reference to the master (stakeholder_id / estereotipo) or create the missing stakeholder or stereotype.",
    "STK-04": "Revalidate it with the person and confirm it again (interesados.py confirmar PF-… --por …) or reject it.",
    "STK-05": "Handle the proposals: interesados.py confirmar | rechazar PF-… --por …",
    "STK-06": "Give them a role in the RACI of the key items (A, R or C).",
    "STK-07": "Review the dispatch: envios.py enviar (retry) or registrar --estado enviado|fallido.",
    "STK-08": "Use the ST-… id or the exact name from the master in okr.csv (responsable column).",
    "STK-09": "Fix the item id or its tipo_elemento (specification, OKR, WBS, activities, decisions) or the id the persona cites (capability or benefit B-##).",
    "STK-10": "Merge or tell apart the duplicate names in the master.",
    "STK-11": "Review the RACI (missing R, over-consultation, concentration of A, A with low power).",
    "STK-13": "Link the Must requirement or epic to the persona who asks for it, uses it or benefits from it (registro.py actualizar personas PU-… --campo usa=…) or review its priority.",
    "STK-14": "Map the persona to its capabilities (solicita, usa, beneficia) or retire it (registro.py actualizar personas PU-… --campo estado=retirada).",
    "STK-15": "Declare the persona's source (entrevista, bmad-uj, encuesta, observacion, documento or supuesto) and its evidence.",
    "STK-16": "Record the journey's persona (interesados.py personas candidatos) or use its registered name or its persona_id in the map.",
    "STK-12": "Contact them according to their profile (envios.py or record the meeting or call: registro.py agregar envios --campo canal=reunion --campo modo=manual --campo estado=enviado …) or review the agreed frequency.",
}

def chk_mapas(proyecto):
    """MAP: mapas de Wardley y de recorrido (pm-mapas-estrategicos). Solo avisos: los mapas son apoyo, no productos obligatorios."""
    if not glob.glob(os.path.join(proyecto, "02-planificacion", "mapas", "*.json")): return
    d = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-mapas-estrategicos", "scripts"))
    try:
        sys.path.insert(0, d); import mapas as MP
        MP.IDIOMA = E.idioma_de(proyecto)
        for sev, cod, msg, arreglo in MP.controles(proyecto): add(sev, cod, msg, arreglo)
    except E.DatosIlegibles as x: ilegible(proyecto, x)
    except BaseException as x:
        add("AVISO", "MAP-00", T(f"No se pudieron verificar los mapas: {x}", f"The maps could not be checked: {x}"), T("Revisar que pm-mapas-estrategicos esté instalada junto a pm-estado-proyecto.", "Check that pm-mapas-estrategicos is installed next to pm-estado-proyecto."))

def chk_decisiones(proyecto, e):
    """DEC: hojas de decisión con matriz (pm-direccion-decisiones/decision.py) que ya tienen una decisión registrada."""
    if not os.path.isdir(os.path.join(proyecto, "03-control", "decisiones")): return
    d = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-direccion-decisiones", "scripts"))
    try:
        sys.path.insert(0, d); import decision as DC
        for sev, cod, msg, arreglo in DC.controles(proyecto, e): add(sev, cod, msg, arreglo)
    except E.DatosIlegibles as x: ilegible(proyecto, x)
    except BaseException as x:
        add("AVISO", "DEC-01", T(f"No se pudieron verificar las hojas de decisión: {x}", f"The decision sheets could not be checked: {x}"), T("Revisar que pm-direccion-decisiones esté instalada junto a pm-estado-proyecto.", "Check that pm-direccion-decisiones is installed next to pm-estado-proyecto."))

def chk_vigencia(e, filas_por, corte):
    """DEC-05/DEC-06: decisiones vigentes del mismo asunto que parecen contradecirse sin reemplaza ni conviven, y
    revisar_en vencido sin una decisión posterior del mismo asunto (vigencia.py; solo avisos)."""
    if not filas_por.get("decisiones"): return
    try:
        import vigencia as V
        for sev, cod, msg, arreglo in V.controles(filas_por["decisiones"], corte, e.get("idioma", "es"), filas_por): add(sev, cod, msg, arreglo)
    except BaseException as x:
        add("AVISO", "DEC-05", T(f"No se pudo revisar la vigencia de las decisiones: {x}", f"Decision validity could not be checked: {x}"), T("Revisar vigencia.py y texto.py en pm-estado-proyecto/scripts.", "Check vigencia.py and texto.py in pm-estado-proyecto/scripts."))

def chk_bitacora(proyecto, e):
    """BIT: bitácora de escrituras (.bitacora.jsonl, 2.6.0): cadena rota (BIT-01) y cambios de estado.json, registros o
    propuestas hechos fuera de los scripts y no reconocidos (BIT-02). Sin bitácora (proyectos anteriores) no hay nada que verificar."""
    _idioma(e)
    try:
        _, probs = E.verificar_bitacora(proyecto, e.get("idioma", "es"))
    except BaseException as x:
        add("AVISO", "BIT-01", T(f"No se pudo leer la bitácora {E.ARCHIVO_BITACORA}: {x}", f"The write log {E.ARCHIVO_BITACORA} could not be read: {x}"), T("Revisar los permisos y el contenido del archivo.", "Check the file's permissions and content.")); return
    for cod, msg in probs:
        add("AVISO", cod, msg, T(ARREGLO_BIT[cod], ARREGLO_BIT_EN[cod]))

ARREGLO_BIT = {
    "BIT-01": "La bitácora no se edita: restaurarla desde git o desde la copia de un expediente (paquete.py auditoria --con-bitacora); si no es posible, dejar constancia en un issue para la auditoría (pm-issues-cambios).",
    "BIT-02": "Ver qué cambió (git diff, registro.py historial <registro>). Si es correcto (merge de git, corrección revisada): registro.py reconocer <registro|estado> --por \"<rol: nombre>\" --motivo \"…\"; si no, restaurar el archivo y escribir con registro.py o estado.py.",
}
ARREGLO_BIT_EN = {
    "BIT-01": "The write log is not edited: restore it from git or from the copy in an audit file (paquete.py auditoria --con-bitacora); if that is not possible, leave a record in an issue for the audit (pm-issues-cambios).",
    "BIT-02": "See what changed (git diff, registro.py historial <register>). If it is correct (git merge, reviewed fix): registro.py reconocer <register|estado> --por \"<role: name>\" --motivo \"…\"; otherwise, restore the file and write with registro.py or estado.py.",
}

def chk_interesados(proyecto, corte=None):
    hay = any(os.path.exists(E.ruta_registro(proyecto, r)) for r in ("estereotipos", "preferencias", "raci", "envios", "personas"))
    if not hay: return     # sin maestro extendido: nada que verificar (compatibilidad con proyectos 2.1)
    d = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-interesados", "scripts"))
    try:
        sys.path.insert(0, d); import interesados as IN
        IN.IDIOMA = E.idioma_de(proyecto)
        for sev, cod, msg in IN.integridad(proyecto, corte):
            add(sev, cod, msg, T(ARREGLO_STK.get(cod, ""), ARREGLO_STK_EN.get(cod, "")))
    except E.DatosIlegibles as x: ilegible(proyecto, x)
    except BaseException as x:
        add("AVISO", "STK-00", T(f"No se pudo verificar el maestro de interesados: {x}", f"The stakeholder master could not be checked: {x}"), T("Revisar que pm-interesados esté instalada junto a pm-estado-proyecto.", "Check that pm-interesados is installed next to pm-estado-proyecto."))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", required=True); ap.add_argument("--rapido", action="store_true"); ap.add_argument("--informe", action="store_true")
    ap.add_argument("--reparar", action="store_true"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--corte", help="fecha de corte AAAA-MM-DD para los controles con vencimiento (defecto: hoy)")
    a = ap.parse_args(); corte = a.corte or datetime.date.today().isoformat()
    e = E.cargar_estado(a.proyecto)      # estado.json ilegible: E.DatosIlegibles (mensaje, código 1, sin traza)
    _idioma(e)
    def seguro(fn, *xs):                 # un archivo de datos ilegible es DAT-01 (ERROR) y la sanidad sigue con el resto
        try: return fn(*xs)
        except E.DatosIlegibles as x: ilegible(a.proyecto, x)
    chk_instalacion(a.proyecto, e, a.rapido); chk_estado(a.proyecto, e); chk_artefactos(a.proyecto, e)
    filas = chk_registros(a.proyecto, e, a.reparar, corte)
    seguro(chk_especificacion, a.proyecto, e, filas, a.reparar, a.rapido)
    seguro(chk_cambios, a.proyecto, e, filas); seguro(chk_calidad, a.proyecto, e, filas, corte); seguro(chk_tolerancias, a.proyecto, e, corte)
    seguro(chk_supuestos, a.proyecto, e, filas, corte)
    seguro(chk_interesados, a.proyecto, corte)
    seguro(chk_mapas, a.proyecto)
    seguro(chk_decisiones, a.proyecto, e)
    seguro(chk_vigencia, e, filas, corte)
    seguro(chk_bitacora, a.proyecto, e)
    if not a.rapido: seguro(chk_integraciones, a.proyecto, e)
    orden = {"ERROR": 0, "AVISO": 1, "INFO": 2}
    H.sort(key=lambda h: (orden[h["severidad"]], h["codigo"]))
    cuenta = {s: sum(1 for h in H if h["severidad"] == s) for s in orden}
    if a.json: print(json.dumps({"proyecto": e.get("proyecto"), "fecha": datetime.date.today().isoformat(), "corte": corte, "cuenta": cuenta, "hallazgos": H}, ensure_ascii=False, indent=2))
    else:
        print(T(f"Sanidad de '{e.get('proyecto')}' ({e.get('fase')}/{e.get('proceso_actual')}): {cuenta['ERROR']} ERROR · {cuenta['AVISO']} AVISO · {cuenta['INFO']} INFO",
                f"Health check of '{e.get('proyecto')}' ({e.get('fase')}/{e.get('proceso_actual')}): {cuenta['ERROR']} ERROR · {cuenta['AVISO']} AVISO · {cuenta['INFO']} INFO"))
        por_cod = {}
        for h in H: por_cod.setdefault((h["severidad"], h["codigo"]), []).append(h)
        for (sev, cod), hs in por_cod.items():   # en pantalla, más de 5 hallazgos del mismo código se agrupan (el --informe y --json los listan todos)
            mostrar = hs if len(hs) <= 5 else hs[:5]
            for h in mostrar: print(f"  {sev:5s} {cod} {h['mensaje']}" + (f"\n        → {h['arreglo']}" if h["arreglo"] and h is mostrar[-1] else ""))
            if len(hs) > 5:
                n = len(hs) - 5; masc = "hallazgo más" if n == 1 else "hallazgos más"
                print(T(f"  {sev:5s} {cod} … y {n} {masc} con el mismo código {cod} y la misma corrección (lista completa: sanidad.py --json o --informe)",
                        f"  {sev:5s} {cod} … and {n} more finding{'' if n == 1 else 's'} with the same code {cod} and the same fix (full list: sanidad.py --json or --informe)"))
    if a.informe:
        p = os.path.join(a.proyecto, "03-control", "reportes", f"{datetime.date.today().isoformat()}-sanidad.md")
        L = ["---", "tipo: informe-sanidad", f"fecha: {datetime.date.today().isoformat()}", "estado: borrador", "---", "",
             T(f"# Sanidad del proyecto · Health check — {e.get('proyecto')}", f"# Project health check — {e.get('proyecto')}"), "", f"{cuenta['ERROR']} ERROR · {cuenta['AVISO']} AVISO · {cuenta['INFO']} INFO", "",
             T("| Severidad | Código | Hallazgo | Cómo corregir |", "| Severity | Code | Finding | How to fix |"), "|---|---|---|---|"] + [f"| {h['severidad']} | {h['codigo']} | {h['mensaje']} | {h['arreglo']} |" for h in H]
        open(p, "w", encoding="utf-8").write("\n".join(L) + "\n"); print(T(f"Informe: {p}", f"Report: {p}"))
    sys.exit(1 if cuenta["ERROR"] else 0)

if __name__ == "__main__":
    main()
