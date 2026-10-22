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
  MAP mapas de Wardley y de recorrido (solo avisos).
"""
import argparse, csv, datetime, glob, importlib.util, json, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import esquema as E

H = []
def add(sev, cod, msg, arreglo=""): H.append({"severidad": sev, "codigo": cod, "mensaje": msg, "arreglo": arreglo})

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
                add("INFO", "INS-03", f"Skill externa '{n}' ({valor}) instalada: invocar como {nombres} · {x['origen']} · {x['ruta']}")
            elif valor == "skills-office" and n == "pptx":
                add("INFO", "INS-03", "export = skills-office sin la skill 'pptx': el deck de puerta sale como guion Markdown.", "Instalarla: ver docs/INSTALACION.md §6.1.")
            else:
                clave = "export" if valor == "skills-office" else "diagramas"
                add("AVISO", "INS-03", f"integraciones.{clave} = {valor}, pero no se encontró la skill '{n}' (ni '<plugin>:{n}') en .claude/skills del proyecto, ~/.claude/skills ni en los plugins instalados.",
                    f"Instalarla (docs/INSTALACION.md §6.1) o volver al respaldo (estado.py integracion {clave}={'scripts' if clave == 'export' else 'mermaid'}). Si se carga con --plugin-dir, ignorar este aviso.")
        instalada = all(n in ext for n in req["skills"])
        if req["node"] and not shutil.which("node"):
            add("AVISO", "INS-03", f"{valor} necesita Node.js y no está en el PATH (archify ≥ 18; `npx skills add` ≥ 22.20).", "Instalar Node.js o volver al respaldo interno.")
        win = [os.path.join(os.environ.get(v, ""), "Google", "Chrome", "Application", "chrome.exe") for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA") if os.environ.get(v)]
        if req["chrome"] and instalada and not (os.environ.get("ARCHIFY_CHROME") or any(shutil.which(b) for b in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"))) \
                and not any(os.path.exists(p) for p in ["/Applications/Google Chrome.app", "/Applications/Chromium.app"] + win):
            add("INFO", "INS-03", "archify: no se encontró Chrome/Chromium; su verificación en navegador (browser-check) quedará omitida.", "Instalar Chrome o definir ARCHIFY_CHROME=<ejecutable>.")

def chk_instalacion(proyecto, e, rapido):
    for mod, uso in (("yaml", "leer BMAD y sprint-status"), ("docx", "exportar .docx / actas .docx"), ("openpyxl", "exportar .xlsx")):
        # find_spec comprueba que el módulo está instalado sin importarlo (importar openpyxl o docx tarda segundos)
        if importlib.util.find_spec(mod) is None: add("AVISO", "INS-01", f"Falta el módulo Python '{mod}' ({uso}).", f"pip install {'pyyaml' if mod == 'yaml' else ('python-docx' if mod == 'docx' else mod)}")
    vp = e.get("version_paquete")
    if vp and vp != E.VERSION_PAQUETE:
        add("AVISO", "INS-02", f"El proyecto fue creado con pm-method {vp} y el instalado es {E.VERSION_PAQUETE}.", "Revisar notas de versión; estado.json se migra al leerse y la versión se actualiza en la próxima escritura con estado.py.")
    if rapido: return
    inv = inventario_skills(proyecto)
    # skills externas declaradas en integraciones (diagramas, export=skills-office), por nombre real y plugins instalados
    chk_externas(proyecto, e)
    # duplicados de nombre (p. ej. plugin + copia manual)
    for n, lst in inv.items():
        rutas = {os.path.realpath(x["ruta"]) for x in lst}
        if n.startswith("pm-") and len(rutas) > 1:
            add("AVISO", "INS-04", f"La skill {n} está instalada {len(rutas)} veces ({', '.join(sorted(rutas))[:300]}).", "Dejar una sola instalación (plugin o copia) para evitar versiones mezcladas.")
    # presupuesto del listado y colisiones de activación con skills de otros repos
    total = sum(len(x[0]["description"]) for x in inv.values() if x[0]["modelo"])
    bm = [n for n in inv if n.startswith("bmad-")]
    if total > 8000:
        add("AVISO", "INS-05", f"Las descripciones de las {sum(1 for x in inv.values() if x[0]['modelo'])} skills visibles suman ≈{total} caracteres{' (incluye ' + str(len(bm)) + ' de BMAD)' if bm else ''}; el listado de Claude Code usa ≈1 % del contexto y puede recortarlas.",
            'En settings.json: "skillListingBudgetFraction": 0.02, o marcar skills poco usadas como "name-only" en skillOverrides (no aplica a skills de plugins).')
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
                add("AVISO", "INS-06", f"Posible colisión de activación entre '{n}' (externa) y '{pn}': comparten {', '.join(sorted(comunes))[:120]}.",
                    "Confirmar cuál debe responder; ajustar la descripción local o usar skillOverrides para la externa.")

# ------------------------------------------------------------------ EST: estado y puertas
def chk_estado(proyecto, e):
    fase, proc = e.get("fase"), e.get("proceso_actual")
    validos = {("pre-proyecto", "SU"), ("inicio", "IP"), ("entrega", "CS"), ("entrega", "SB"), ("cierre", "CP"), ("cerrado", "CP")}
    if (fase, proc) not in validos: add("ERROR", "EST-01", f"Combinación fase/proceso inválida: {fase}/{proc}.", "estado.py set fase=… proceso_actual=… o rehacer la última transición.")
    ok = lambda t: [p for p in e.get("puertas", []) if p.get("tipo") == t and p.get("decision") in ("aprobado", "condicionado")]
    if fase in ("inicio", "entrega", "cierre", "cerrado") and not ok("autorizar-inicio"):
        add("ERROR", "EST-02", f"Fase {fase} sin puerta autorizar-inicio registrada.", "Registrar la decisión con pm-director (estado.py puerta autorizar-inicio …).")
    if fase in ("entrega", "cierre", "cerrado") and not (ok("autorizar-proyecto") and ok("autorizar-etapa")):
        add("ERROR", "EST-03", f"Fase {fase} sin autorizar-proyecto y autorizar-etapa.", "Revisar las decisiones de la junta.")
    if fase == "cerrado" and not ok("autorizar-cierre"): add("ERROR", "EST-04", "Proyecto cerrado sin autorizar-cierre.", "")
    n_etapa = e.get("etapa_actual", {}).get("numero", 0)
    esperado = (1 if ok("autorizar-inicio") else 0) + len(ok("autorizar-etapa"))
    if fase in ("inicio", "entrega") and n_etapa != esperado:
        add("AVISO", "EST-05", f"etapa_actual = {n_etapa}, pero las puertas registradas implican la etapa {esperado}.", "Corregir con estado.py etapa --numero … si fue un ajuste manual.")
    tol = e.get("tolerancias", {}).get("proyecto", {})
    faltan = [d for d in ("tiempo", "costo") if not tol.get(d)]
    if faltan and (e.get("proyecto_autorizado") or fase in ("entrega",)):
        add("ERROR", "EST-06", f"Proyecto autorizado sin tolerancias de proyecto: {', '.join(faltan)}.", "estado.py tolerancia --nivel proyecto tiempo=… costo=…")
    if fase == "entrega" and not any(e.get("tolerancias", {}).get("etapa", {}).values()):
        add("AVISO", "EST-07", "Etapa de entrega sin tolerancias de etapa.", "estado.py tolerancia --nivel etapa …")
    r = e.get("roles", {})
    if fase != "pre-proyecto" and not r.get("ejecutivo"): add("ERROR", "EST-08", "Sin ejecutivo designado (no hay proyecto sin ejecutivo).", "estado.py rol ejecutivo=…")
    if r.get("ejecutivo") and r.get("ejecutivo") == r.get("gestor_proyecto"): add("ERROR", "EST-09", "El ejecutivo y el gestor son la misma persona.", "Separar los roles.")
    if r.get("gestor_proyecto") and r.get("gestor_proyecto") in (r.get("aseguramiento") or []): add("ERROR", "EST-10", "El gestor figura en aseguramiento.", "El aseguramiento es independiente del gestor.")
    for p in e.get("puertas", []):
        if p.get("decision") == "pendiente" and not p.get("resuelta"): add("AVISO", "EST-11", f"Puerta pendiente: {p['tipo']} ({p.get('fecha')}).", "Llevarla a la junta (pm-puerta).")
        if p.get("decision") in ("condicionado", "aprobado") and p.get("condiciones") and not p.get("condiciones_cumplidas"):
            add("AVISO", "EST-12", f"Condiciones abiertas de {p['tipo']}: {p['condiciones']}.", "estado.py cumplir-condiciones <tipo> cuando se cumplan.")
        if p.get("forzada"): add("AVISO", "EST-13", f"La puerta {p['tipo']} se registró con --forzar.", "Justificar en decisiones.csv.")
    if e.get("excepcion_abierta"): add("AVISO", "EST-14", f"Excepción abierta {e['excepcion_abierta']} esperando plan de excepción.", "")

# ------------------------------------------------------------------ ART: artefactos
def chk_artefactos(proyecto, e):
    for k, a in e.get("artefactos", {}).items():
        ruta = os.path.join(proyecto, a.get("ruta", ""))
        if not os.path.exists(ruta):
            add("ERROR", "ART-01", f"Artefacto {k} registrado pero no existe: {a.get('ruta')}.", "Restaurarlo o corregir la ruta con estado.py artefacto.")
            continue
        if a.get("externo"):
            if not a.get("sha256"): add("AVISO", "ART-04", f"Especificación externa {k} sin huella.", "Registrar con bmad.py linea-base.")
            continue
        if a.get("estado") == "aprobado" and not a.get("aprobado_por"): add("AVISO", "ART-02", f"{k} aprobado sin aprobado_por.", "estado.py aprobar … --por …")
        if ruta.endswith(".md"):
            fm = leer_fm(ruta) or {}
            if fm.get("estado") and fm["estado"] != a.get("estado"):
                add("AVISO", "ART-03", f"{k}: estado.json dice '{a.get('estado')}' y el documento '{fm['estado']}'.", "estado.py artefacto/aprobar sincroniza ambos.")
    for p in glob.glob(os.path.join(proyecto, "00-direccion", "historial", "*")):
        pass  # las copias congeladas no se validan contra su contenido; el hook impide editarlas

# ------------------------------------------------------------------ REG: registros
def chk_registros(proyecto, e, reparar, corte=None):
    hoy = corte or datetime.date.today().isoformat(); ids_todos = set()
    filas_por = {}
    for reg, spec in E.REGISTROS.items():
        p = E.ruta_registro(proyecto, reg)
        if spec.get("opcional") and not os.path.exists(p): continue      # maestro de interesados: se crea al primer uso
        if not os.path.exists(p): add("ERROR", "REG-01", f"Falta el registro {reg}.csv.", "sanidad.py --reparar lo crea vacío.");
        if reparar or not os.path.exists(p): E.asegurar_registro(proyecto, reg)
        cols, filas = E.leer_csv(p)
        faltan = [c for c in spec["columnas"] if c not in cols]
        if faltan: add("AVISO", "REG-02", f"{reg}.csv sin columnas del esquema v2: {', '.join(faltan)}.", "sanidad.py --reparar (o cualquier registro.py) las agrega.")
        vistos = set()
        for f in filas:
            i = f.get("id", "")
            if not re.match(rf"^{spec['prefijo']}-\d{{3,}}$", i): add("ERROR", "REG-03", f"{reg}: id inválido '{i}'.", f"Formato {spec['prefijo']}-###.")
            if i in vistos: add("ERROR", "REG-04", f"{reg}: id duplicado {i}.", "Renumerar el duplicado.")
            vistos.add(i); ids_todos.add(i)
            for col, perm in spec.get("valores", {}).items():
                v = f.get(col, "")
                if v and v not in perm: add("ERROR", "REG-05", f"{reg} {i}: {col}='{v}' fuera del esquema.", f"Valores: {', '.join(x for x in perm if x)}")
            for col, perm in spec.get("multivalor", {}).items():
                malos = [x.strip() for x in re.split(r"[;,]", f.get(col, "") or "") if x.strip() and x.strip() not in perm]
                if malos: add("ERROR", "REG-05", f"{reg} {i}: {col}='{'; '.join(malos)}' fuera del esquema.", f"Valores (uno o más, separados por ;): {', '.join(perm)}")
            for col in spec.get("enteros_1_5", []):
                v = f.get(col, "")
                if v and not (v.isdigit() and 1 <= int(v) <= 5): add("ERROR", "REG-05", f"{reg} {i}: {col}='{v}' no es 1–5.", "")
        filas_por[reg] = filas
    for f in filas_por.get("riesgos", []):
        if f.get("estado") in E.REGISTROS["riesgos"]["abiertos"]:
            try: pts = float(f.get("puntuacion") or 0)
            except ValueError: pts = 0
            umbral = float((e.get("umbrales_riesgo") or {}).get("alto", E.UMBRAL_RIESGO_ALTO))
            if pts >= umbral and not (f.get("respuesta") and f.get("propietario")):
                add("AVISO", "REG-06", f"Riesgo alto {f['id']} sin respuesta o propietario.", "pm-riesgos.")
    for f in filas_por.get("acciones", []):
        if f.get("estado") in ("abierta", "en-curso") and f.get("fecha_compromiso") and f["fecha_compromiso"] < hoy:
            add("AVISO", "REG-07", f"Acción vencida {f['id']} ({f.get('responsable','sin responsable')}, {f['fecha_compromiso']}).", "Recordatorio o replanificación.")
    for f in filas_por.get("riesgos", []):
        if f.get("estado") in E.REGISTROS["riesgos"]["abiertos"] and f.get("fecha_revision") and f["fecha_revision"] < hoy:
            add("AVISO", "REG-09", f"Riesgo {f['id']} abierto con la revisión vencida ({f['fecha_revision']}; propietario: {f.get('propietario') or 'sin propietario'}).",
                "Revisarlo con el propietario (pm-riesgos) y actualizar estado, evaluación y fecha_revision (registro.py actualizar riesgos R-… --campo fecha_revision=…).")
    # REG-10: amenaza alta con respuesta sin opciones evaluadas, o aceptada sin disparador o plan de contingencia (pm-riesgos/riesgos.py)
    if filas_por.get("riesgos"):
        try:
            sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-riesgos", "scripts"))); import riesgos as RK
            for sev, cod, msg, arreglo in RK.controles(proyecto, e, filas_por["riesgos"]): add(sev, cod, msg, arreglo)
        except BaseException as x:
            add("AVISO", "REG-10", f"No se pudieron verificar las opciones de respuesta: {x}", "Revisar que pm-riesgos esté instalada junto a pm-estado-proyecto.")
    # REG-11/REG-12: ciclo de las lecciones (impacto alto sin acción ni decisión; accionada sin verificar su efecto) (pm-lecciones-aprendidas/lecciones.py)
    if filas_por.get("lecciones"):
        try:
            sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-lecciones-aprendidas", "scripts"))); import lecciones as LX
            for sev, cod, msg, arreglo in LX.controles(filas_por["lecciones"], hoy, e.get("idioma", "es")): add(sev, cod, msg, arreglo)
        except BaseException as x:
            add("AVISO", "REG-11", f"No se pudo revisar el ciclo de las lecciones: {x}", "Revisar que pm-lecciones-aprendidas esté instalada junto a pm-estado-proyecto.")
    # referencias cruzadas entre registros (R-, I-, C-, D-, S-, L-, ST-, Q-, A-, ET-, PF-, RC-, EN-, PU-)
    for reg, filas in filas_por.items():
        for f in filas:
            if reg == "lecciones" and f.get("origen"): continue   # lección previa de otro proyecto: cita ids de su proyecto de origen
            texto = " ".join(str(v) for k, v in f.items() if k != "id")
            for ref in set(re.findall(r"\b(?:R|I|C|D|S|L|ST|Q|A|ET|PF|RC|EN|PU)-\d{3}\b", texto)):
                if ref not in ids_todos: add("AVISO", "REG-08", f"{reg} {f.get('id')} cita {ref}, que no existe.", "Corregir la referencia.")
    return filas_por

# ------------------------------------------------------------------ controles permanentes: CAM cambios y presupuestos ·
# QUA calidad a volumen · TOL pronóstico contra tolerancias (lo que en la práctica se revisa a mano, tarde o nunca)
_num = E.monto
def _m(x): return f"{x:,.0f}".replace(",", ".")   # miles con punto (salida en español)
_es_junta = E.es_junta

def chk_cambios(proyecto, e, filas_por):
    pres = e.get("presupuestos", {}) or {}
    for f in filas_por.get("cambios", []):
        if not E.cambio_vigente(f): continue
        costo = _num(f.get("costo")); cargo = f.get("cargo", "")
        if costo is None:
            if re.search(r"\d", f.get("impacto_costo", "") or "") and not cargo:
                add("AVISO", "CAM-01", f"Cambio aprobado {f['id']} con impacto de costo ('{f.get('impacto_costo')}') sin monto en 'costo' ni 'cargo'.",
                    "registro.py actualizar cambios C-… --campo costo=<monto> --campo cargo=presupuesto-cambio|reserva-riesgo|reserva-gestion|plan-excepcion")
            continue
        if costo > 0 and not cargo:
            add("AVISO", "CAM-01", f"Cambio aprobado {f['id']} por {_m(costo)} sin 'cargo' (¿contra qué presupuesto?).", "Indicar cargo: presupuesto-cambio (lo habitual), reserva-riesgo, reserva-gestion o plan-excepcion.")
        if cargo == "reserva-riesgo" and not re.search(r"\bR-\d{3}\b", " ".join(str(f.get(k, "")) for k in ("descripcion", "justificacion", "impacto_riesgo", "notas"))):
            add("AVISO", "CAM-02", f"Cambio {f['id']} cargado a la reserva de riesgo sin citar el riesgo R-### que responde.", "La reserva de riesgo solo financia respuestas a riesgos; si no, presupuesto de cambio o junta.")
        if cargo == "reserva-gestion" and not _es_junta(e, f.get("decidido_por")):
            add("AVISO", "CAM-05", f"Cambio {f['id']} usa la reserva de gestión decidido por '{f.get('decidido_por')}', no por la junta o el ejecutivo.", "Solo la junta libera la reserva de gestión (pm-director).")
        lim = _num(pres.get("limite_autoridad_cambio"))
        if lim is not None and costo > lim and not _es_junta(e, f.get("decidido_por")):
            add("AVISO", "CAM-04", f"Cambio {f['id']} ({_m(costo)}) supera el límite de la autoridad de cambio ({_m(lim)}) y lo decidió '{f.get('decidido_por')}'.", "Escalar a la junta y registrar su decisión (decision-ad-hoc), o ajustar el límite delegado.")
    consumo = E.consumo_cambios(filas_por.get("cambios", []))   # misma regla que registro.py al aprobar
    for cargo, clave, nombre in (("presupuesto-cambio", "cambio", "presupuesto de cambio"), ("reserva-riesgo", "riesgo", "reserva de riesgo")):
        usado = consumo[cargo]; tope = _num(pres.get(clave))
        if not usado: continue
        if tope is None:
            add("AVISO", "CAM-03", f"Se cargaron {_m(usado)} a {nombre} pero la junta no fijó ese presupuesto.", f"pm-director: estado.py presupuesto {clave}=<monto> --por …")
        elif usado > tope:
            add("ERROR", "CAM-03", f"{nombre.capitalize()} excedido: {_m(usado)} de {_m(tope)} ({100 * usado / tope:.0f} %).", "Escalar a la junta: informe de excepción o ampliación del presupuesto (decisión registrada).")
        elif usado >= 0.8 * tope:
            add("AVISO", "CAM-03", f"{nombre.capitalize()} al {100 * usado / tope:.0f} % ({_m(usado)} de {_m(tope)}).", "Avisar a la junta antes de aprobar más cambios.")
        else:
            add("INFO", "CAM-03", f"{nombre.capitalize()}: {_m(usado)} de {_m(tope)} ({100 * usado / tope:.0f} %).")

def chk_supuestos(proyecto, e, filas_por, corte):
    """SUP: supuestos críticos tratados como hipótesis (validar antes de invertir)."""
    sup = filas_por.get("supuestos", [])
    citado = " ".join(" ".join(str(v) for v in f.values()) for reg in ("issues", "cambios", "decisiones", "riesgos") for f in filas_por.get(reg, []))
    for f in sup:
        abierto = f.get("estado") == "abierto" and f.get("validado") != "si"
        if abierto and f.get("criticidad") == "alta" and (not f.get("experimento") or not f.get("fecha_limite")):
            add("AVISO", "SUP-01", f"Supuesto crítico {f['id']} sin {'experimento' if not f.get('experimento') else 'fecha límite'} para validarlo: «{(f.get('supuesto_o_restriccion') or '')[:70]}».",
                "Definir cómo se valida (experimento), el criterio para seguir y la fecha límite (registro.py actualizar supuestos S-…).")
        if abierto and f.get("fecha_limite") and f["fecha_limite"] < corte:
            add("AVISO", "SUP-02", f"Supuesto {f['id']} con fecha límite {f['fecha_limite']} vencida y sin validar.", "Registrar la evidencia y el resultado (validado=si|no) o replanificar con la junta.")
        if (f.get("validado") == "no" or f.get("estado") == "invalidado") and not re.search(rf"\b{re.escape(f['id'])}\b", citado):
            add("AVISO", "SUP-03", f"Supuesto {f['id']} invalidado sin issue, cambio, riesgo o decisión que trate su efecto.", "Revisar el business case y registrar la decisión (pm-caso-de-negocio, pm-direccion-decisiones).")

TERMINADO = {"done", "terminado", "terminada", "hecho", "hecha", "completado", "completada", "cerrado", "cerrada", "aceptado", "aceptada"}

def chk_calidad(proyecto, e, filas_por, corte):
    q = filas_por.get("calidad", [])
    texto_q = [(f, " ".join(str(f.get(k, "")) for k in ("producto", "criterios", "notas"))) for f in q]
    p = os.path.join(proyecto, "02-planificacion", "backlog.csv")
    if os.path.exists(p):
        for b in csv.DictReader(open(p, encoding="utf-8")):
            if (b.get("estado") or "").strip().lower() not in TERMINADO: continue
            bid = b.get("id", ""); corto = (re.match(r"^(\d+-\d+)(?:-|$)", bid) or [None, None])[1]
            pat = re.compile(rf"(?<![\w-]){re.escape(bid)}(?![\w-])" + (rf"|(?<![\w.-]){re.escape(corto)}(?![\w-]|\.\d|\d)" if corto else ""))   # «historia 1-2.» sí; «1-2.3» no
            rev = [f for f, t in texto_q if pat.search(t)]
            if not rev:
                add("AVISO", "QUA-01", f"{bid}: terminado sin revisión de calidad registrada.", "pm-calidad: registrar la revisión (registro.py agregar calidad --campo producto=\"… historia N-M\") o aplicar el criterio de aceptación por lote.")
            elif not any(f.get("estado") == "completada" and f.get("resultado") in ("aprobado", "aprobado-con-observaciones") for f in rev):
                add("AVISO", "QUA-01", f"{bid}: terminado con revisión {', '.join(f['id'] for f in rev)} sin aprobar.", "Completar la revisión o reabrir el elemento.")
    for f in q:
        if f.get("estado") in ("planificada", "en-curso") and f.get("fecha_prevista") and f["fecha_prevista"] < corte:
            add("AVISO", "QUA-02", f"Revisión de calidad vencida {f['id']} ({f.get('producto', '')[:60]}, prevista {f['fecha_prevista']}).", "Realizarla o replanificarla.")
    citados = " ".join(" ".join(str(v) for v in f.values()) for reg in ("issues", "acciones", "cambios") for f in filas_por.get(reg, []))
    for f in q:
        if f.get("resultado") == "rechazado" and not re.search(rf"\b{re.escape(f['id'])}\b", citados):
            add("AVISO", "QUA-03", f"Revisión {f['id']} rechazada sin issue, acción o cambio que la trate.", "pm-issues-cambios (fuera de especificación) o una acción correctiva que cite el Q-###.")
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
                add("AVISO", "QUA-04", f"Producto {z['producto']} de la WBS: {z['texto']}.", "pm-calidad: registrar la revisión que cite «producto <código>» (registro.py agregar calidad) o revisar la aceptación o la recepción.")

def chk_tolerancias(proyecto, e, corte):
    xs = sorted(glob.glob(os.path.join(proyecto, "03-control", "reportes", "evm-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json")))
    xs = [x for x in xs if os.path.basename(x)[4:14] <= corte]
    if not xs:
        if e.get("fase") == "entrega": add("INFO", "TOL-03", "Etapa de entrega sin corte de EVM guardado: el pronóstico contra tolerancias no se vigila.", "evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD en cada período.")
        return
    ult = json.load(open(xs[-1], encoding="utf-8")); f = ult.get("corte", os.path.basename(xs[-1])[4:14])
    sem = {k: ult.get(k) for k in ("semaforo_costo", "semaforo_cronograma", "semaforo_alcance") if ult.get(k)}
    if ult.get("excepcion_prevista"):
        tratada = bool(e.get("excepcion_abierta")) or any(p.get("tipo") == "autorizar-plan-excepcion" and (p.get("fecha") or "") >= f for p in e.get("puertas", []))
        if not tratada:
            add("AVISO", "TOL-01", f"El EVM del {f} pronostica salir de la tolerancia ({', '.join(f'{k[9:]}={v}' for k, v in sem.items())}) y no hay excepción abierta.",
                "pm-progreso-reportes: informe de excepción; pm-director: estado.py limite-etapa --excepcion X-### y puerta autorizar-plan-excepcion.")
    elif any(str(v).startswith("ambar") or str(v).startswith("ámbar") for v in sem.values()):
        add("INFO", "TOL-02", f"El EVM del {f} está en ámbar ({', '.join(f'{k[9:]}={v}' for k, v in sem.items())}): 50–100 % de la tolerancia.", "Anticipar acciones correctivas y reportarlo en el highlight.")
    try:
        if e.get("fase") == "entrega" and (datetime.date.fromisoformat(corte) - datetime.date.fromisoformat(f)).days > 31:
            add("INFO", "TOL-03", f"Último corte de EVM guardado el {f} (más de 31 días).", "evm.py … --guardar en cada período de informe.")
    except ValueError: pass

# ------------------------------------------------------------------ ESP: especificación y columna vertebral BMAD
def chk_especificacion(proyecto, e, filas_por, reparar, rapido):
    import especificacion as SP
    bm = e.get("integraciones", {}).get("especificacion") == "bmad"
    try:
        h = SP.huella(proyecto, e)
    except SystemExit as x:
        add("ERROR", "ESP-01", f"No se pudo leer la especificación: {x}", "Revisar integraciones.bmad.raiz o correr bmad.py detectar."); return
    ri = SP.ruta_indice(proyecto)
    vigente = os.path.exists(ri) and json.load(open(ri, encoding="utf-8")).get("_huella") == h
    if not vigente:
        if reparar: SP.obtener(proyecto, forzar=True); add("INFO", "ESP-02", "Índice de especificación reconstruido.")
        else: add("INFO", "ESP-02", "El índice de especificación está desactualizado (se reconstruye solo al consultarlo).", "especificacion.py indice o sanidad.py --reparar.")
    if rapido and not bm: return
    idx, _ = SP.obtener(proyecto)
    ids = {x["id"] for x in idx.get("requisitos", [])} | {x["id"] for x in idx.get("historias", [])} | {x["id"] for x in idx.get("epicas", [])}
    sinc = [q["id"] for q in idx.get("requisitos", []) if q.get("cobertura") == "sin-cobertura"]
    if sinc: add("AVISO" if e.get("fase") in ("pre-proyecto", "inicio") else "ERROR", "ESP-03", f"Requisitos sin cobertura (ni historia ni paquete de la WBS): {', '.join(sinc)}.", "Planificarlos (pm-planificacion-por-productos / pm-agil-hibrido) o retirarlos mediante control de cambios.")
    patron = re.compile(r"\b(?:REQ-\d{3}|FR-\d+|NFR-\d+|UJ-\d+|SM-\d+|AD-\d+|UX-DR-\d+)\b")
    def revisar(nombre, texto):
        for r in set(patron.findall(texto)):
            if r not in ids: add("ERROR", "ESP-04", f"{nombre} cita {r}, que no existe en la especificación vigente ({idx['proveedor']}).", "Corregir el id o tramitar el cambio de alcance.")
    pw = os.path.join(proyecto, "02-planificacion", "wbs.csv")
    if os.path.exists(pw):
        for r in csv.DictReader(open(pw, encoding="utf-8")): revisar(f"wbs.csv {r.get('codigo')}", r.get("ref", ""))
    for reg in ("riesgos", "issues", "calidad", "supuestos"):
        for f in filas_por.get(reg, []): revisar(f"{reg} {f.get('id')}", " ".join(str(v) for v in f.values()))
    po = os.path.join(proyecto, "00-direccion", "okr.csv")
    if os.path.exists(po):
        bc = ""
        for c in glob.glob(os.path.join(proyecto, "00-direccion", "*business-case*.md")): bc += open(c, encoding="utf-8").read()
        for r in csv.DictReader(open(po, encoding="utf-8")):
            if r.get("tipo") != "kr": continue
            v = r.get("vinculo", "")
            revisar(f"okr {r.get('id')}", v)
            for b in re.findall(r"\bB-?\d+\b", v):
                if bc and not re.search(r"\b" + re.escape(b) + r"\b|\bB-0*" + re.sub(r"\D", "", b) + r"\b", bc): add("AVISO", "ESP-05", f"okr {r.get('id')} cita el beneficio {b}, que no aparece en el business case.", "Alinear con pm-caso-de-negocio.")
    if not bm: return
    sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-bmad-puente", "scripts")))
    import bmad as B
    try: b = B.detectar_bmad(proyecto, None, e)
    except SystemExit as x: add("ERROR", "ESP-06", f"BMAD declarado pero no detectado: {x}", "bmad.py detectar --raiz …"); return
    if b["soporte"] not in ("soportada", "v4"): add("AVISO", "ESP-07", f"Versión de BMAD {b['soporte']} (probadas: {B.VERSIONES_SOPORTADAS}).", "Correr scripts/probar_paquete.py del paquete y revisar el inventario.")
    pa = os.path.abspath(proyecto)
    for d in b.get("carpetas_protegidas", []):
        if pa.startswith(os.path.abspath(d) + os.sep): add("ERROR", "ESP-08", "La carpeta del proyecto está dentro de una carpeta de BMAD.", "Moverla fuera (p. ej. <repo>/gestion).")
    arts = B.inventario(b)
    # desvíos contra líneas base: cada uno debe tener un issue/cambio abierto que lo cite
    texto_cambios = " ".join(" ".join(str(v) for v in f.values()) for reg in ("issues", "cambios") for f in filas_por.get(reg, [])
                             if f.get("estado") not in ("cerrado", "resuelto", "rechazado"))
    for art_k, clave in B.CLAVES_LB.items():
        lb = e.get("artefactos", {}).get(clave)
        if not lb or "sha256" not in lb: continue
        if art_k not in arts: add("ERROR", "ESP-09", f"El artefacto con línea base {clave} ya no se encuentra en BMAD.", "Investigar y tramitar como cambio."); continue
        if arts[art_k]["sha256"] != lb["sha256"]:
            nuevos = set(B.ids_de(arts, art_k)) ^ set(lb.get("ids", []))
            citado = clave in texto_cambios or any(i in texto_cambios for i in nuevos) or art_k in texto_cambios
            if citado: add("AVISO", "ESP-10", f"{clave} difiere de su línea base v{lb.get('version')} y hay un issue/cambio abierto que lo trata.", "Al aprobarse: bmad.py linea-base con versión mayor.")
            else: add("ERROR", "ESP-10", f"Cambio no controlado: {clave} difiere de la línea base v{lb.get('version')}{' (ids ' + ', '.join(sorted(nuevos)) + ')' if nuevos else ''} y ningún issue/cambio abierto lo cita.", "pm-issues-cambios: registrar solicitud-cambio (o declarar elaboración progresiva y fijar nueva línea base).")
    if e.get("fase") in ("entrega", "cierre", "cerrado") and "bmad-prd" not in e.get("artefactos", {}):
        add("ERROR", "ESP-11", "Etapas de entrega sin línea base del PRD.", "pm-director: bmad.py linea-base prd --version 1.0 --por …")
    vistas = set(e.get("integraciones", {}).get("bmad", {}).get("propuestas_vistas", []))
    for r in arts.get("propuestas-cambio", {}).get("rutas", []):
        rel = os.path.relpath(r, b["raiz"])
        if rel not in vistas and os.path.basename(r) not in texto_cambios: add("AVISO", "ESP-12", f"Sprint Change Proposal sin tratar: {rel}.", "bmad.py verificar y registrar issue solicitud-cambio.")
    for hdf in e.get("integraciones", {}).get("bmad", {}).get("handoffs", []):
        fm = leer_fm(os.path.join(proyecto, hdf["archivo"])) or {}
        if fm.get("estado") != "aplicado":
            add("AVISO", "ESP-13", f"Traspaso a BMAD sin confirmar: {hdf['archivo']}.", "Cuando el equipo BMAD lo aplique: marcar estado: aplicado en el documento, bmad.py verificar y nueva línea base.")
    # derivados editados a mano
    pr = os.path.join(proyecto, "02-planificacion", "especificacion", "requisitos-bmad.csv")
    if os.path.exists(pr):
        actual = [r["id"] for r in csv.DictReader(open(pr, encoding="utf-8"))]
        if actual != [q["id"] for q in B.requisitos(b, arts)]: add("AVISO", "ESP-14", "requisitos-bmad.csv no coincide con el PRD vigente (desactualizado o editado).", "bmad.py requisitos (es derivado: no se edita).")
    pb = os.path.join(proyecto, "02-planificacion", "backlog.csv")
    if os.path.exists(pb):
        hs = B.historias(b, arts)
        for f in csv.DictReader(open(pb, encoding="utf-8")):
            if f.get("origen") != "bmad": continue
            h = hs.get(f["id"])
            if h and f.get("estado") != h["estado"]: add("AVISO", "ESP-15", f"backlog.csv {f['id']}: estado '{f.get('estado')}' ≠ BMAD '{h['estado']}'.", "bmad.py backlog (sincroniza las columnas derivadas)."); break

# ------------------------------------------------------------------ INT: integraciones MCP (instantáneas)
def chk_integraciones(proyecto, e):
    conocidos = E.VALORES_INTEGRACION
    for k, vals in conocidos.items():
        v = e.get("integraciones", {}).get(k)
        if k == "diagramas" and isinstance(v, str) and "," in v and all(x.strip() in vals for x in v.split(",")): continue
        if v and v not in vals: add("AVISO", "INT-01", f"integraciones.{k} = '{v}' no es un valor conocido ({', '.join(sorted(vals))}).", "Usarlo solo si pm-integraciones sabe mapearlo; si no, corregir.")
    trk = e.get("integraciones", {}).get("tracker", "ninguno")
    if trk not in ("ninguno", None) and e.get("fase") == "entrega":
        snaps = sorted(glob.glob(os.path.join(proyecto, "03-control", "fuentes", f"{trk}-*")))
        if not snaps: add("AVISO", "INT-02", f"Tracker {trk} declarado sin instantáneas en 03-control/fuentes/.", "pm-integraciones: leer y guardar instantánea fechada.")
        else:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(snaps[-1]))
            if m and (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days > 14:
                add("AVISO", "INT-03", f"La última instantánea de {trk} tiene más de 14 días ({m.group(1)}).", "Actualizarla antes del próximo informe.")
    for f in glob.glob(os.path.join(proyecto, "03-control", "fuentes", "*")):
        if not re.search(r"-\d{4}-\d{2}-\d{2}\.\w+$", f): add("AVISO", "INT-04", f"Instantánea sin fecha en el nombre: {os.path.basename(f)}.", "<sistema>-AAAA-MM-DD.<ext>")

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

def chk_mapas(proyecto):
    """MAP: mapas de Wardley y de recorrido (pm-mapas-estrategicos). Solo avisos: los mapas son apoyo, no productos obligatorios."""
    if not glob.glob(os.path.join(proyecto, "02-planificacion", "mapas", "*.json")): return
    d = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-mapas-estrategicos", "scripts"))
    try:
        sys.path.insert(0, d); import mapas as MP
        MP.IDIOMA = E.idioma_de(proyecto)
        for sev, cod, msg, arreglo in MP.controles(proyecto): add(sev, cod, msg, arreglo)
    except BaseException as x:
        add("AVISO", "MAP-00", f"No se pudieron verificar los mapas: {x}", "Revisar que pm-mapas-estrategicos esté instalada junto a pm-estado-proyecto.")

def chk_interesados(proyecto, corte=None):
    hay = any(os.path.exists(E.ruta_registro(proyecto, r)) for r in ("estereotipos", "preferencias", "raci", "envios", "personas"))
    if not hay: return     # sin maestro extendido: nada que verificar (compatibilidad con proyectos 2.1)
    d = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-interesados", "scripts"))
    try:
        sys.path.insert(0, d); import interesados as IN
        IN.IDIOMA = E.idioma_de(proyecto)
        for sev, cod, msg in IN.integridad(proyecto, corte):
            add(sev, cod, msg, ARREGLO_STK.get(cod, ""))
    except BaseException as x:
        add("AVISO", "STK-00", f"No se pudo verificar el maestro de interesados: {x}", "Revisar que pm-interesados esté instalada junto a pm-estado-proyecto.")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", required=True); ap.add_argument("--rapido", action="store_true"); ap.add_argument("--informe", action="store_true")
    ap.add_argument("--reparar", action="store_true"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--corte", help="fecha de corte AAAA-MM-DD para los controles con vencimiento (defecto: hoy)")
    a = ap.parse_args(); corte = a.corte or datetime.date.today().isoformat()
    e = E.cargar_estado(a.proyecto)
    chk_instalacion(a.proyecto, e, a.rapido); chk_estado(a.proyecto, e); chk_artefactos(a.proyecto, e)
    filas = chk_registros(a.proyecto, e, a.reparar, corte)
    chk_especificacion(a.proyecto, e, filas, a.reparar, a.rapido)
    chk_cambios(a.proyecto, e, filas); chk_calidad(a.proyecto, e, filas, corte); chk_tolerancias(a.proyecto, e, corte)
    chk_supuestos(a.proyecto, e, filas, corte)
    chk_interesados(a.proyecto, corte)
    chk_mapas(a.proyecto)
    if not a.rapido: chk_integraciones(a.proyecto, e)
    orden = {"ERROR": 0, "AVISO": 1, "INFO": 2}
    H.sort(key=lambda h: (orden[h["severidad"]], h["codigo"]))
    cuenta = {s: sum(1 for h in H if h["severidad"] == s) for s in orden}
    if a.json: print(json.dumps({"proyecto": e.get("proyecto"), "fecha": datetime.date.today().isoformat(), "corte": corte, "cuenta": cuenta, "hallazgos": H}, ensure_ascii=False, indent=2))
    else:
        print(f"Sanidad de '{e.get('proyecto')}' ({e.get('fase')}/{e.get('proceso_actual')}): {cuenta['ERROR']} ERROR · {cuenta['AVISO']} AVISO · {cuenta['INFO']} INFO")
        por_cod = {}
        for h in H: por_cod.setdefault((h["severidad"], h["codigo"]), []).append(h)
        for (sev, cod), hs in por_cod.items():   # en pantalla, más de 5 hallazgos del mismo código se agrupan (el --informe y --json los listan todos)
            mostrar = hs if len(hs) <= 5 else hs[:5]
            for h in mostrar: print(f"  {sev:5s} {cod} {h['mensaje']}" + (f"\n        → {h['arreglo']}" if h["arreglo"] and h is mostrar[-1] else ""))
            if len(hs) > 5:
                n = len(hs) - 5; masc = "hallazgo más" if n == 1 else "hallazgos más"
                print(f"  {sev:5s} {cod} … y {n} {masc} con el mismo código {cod} y la misma corrección (lista completa: sanidad.py --json o --informe)")
    if a.informe:
        p = os.path.join(a.proyecto, "03-control", "reportes", f"{datetime.date.today().isoformat()}-sanidad.md")
        L = ["---", "tipo: informe-sanidad", f"fecha: {datetime.date.today().isoformat()}", "estado: borrador", "---", "",
             f"# Sanidad del proyecto · Health check — {e.get('proyecto')}", "", f"{cuenta['ERROR']} ERROR · {cuenta['AVISO']} AVISO · {cuenta['INFO']} INFO", "",
             "| Severidad | Código | Hallazgo | Cómo corregir |", "|---|---|---|---|"] + [f"| {h['severidad']} | {h['codigo']} | {h['mensaje']} | {h['arreglo']} |" for h in H]
        open(p, "w", encoding="utf-8").write("\n".join(L) + "\n"); print(f"Informe: {p}")
    sys.exit(1 if cuenta["ERROR"] else 0)

if __name__ == "__main__":
    main()
