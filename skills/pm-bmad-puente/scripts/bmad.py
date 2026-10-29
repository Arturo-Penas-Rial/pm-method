#!/usr/bin/env python3
"""Puente de solo lectura entre BMAD (capa de especificación) y pm-method (gobierno PRINCE2).
Read-only bridge between BMAD specification artifacts and the pm-method project folder.

Principios / Principles
  - Nunca escribe en las carpetas de BMAD (_bmad/, _bmad-output/, .bmad-core/, docs/ de BMAD): solo lee.
  - No depende de nombres de skills ni de rutas fijas de BMAD: descubre por configuración y por patrones.
  - Compatibilidad declarada: BMAD v6.11–v6.12 (salidas en carpetas fechadas) y v4 (docs/ y .bmad-core/).
    Fuera de ese rango funciona en modo degradado y lo advierte.
  - Lo que genera en la carpeta del proyecto es DERIVADO (se regenera): no editarlo a mano, salvo las
    columnas de gobierno de backlog.csv, que el puente nunca sobrescribe.

Uso / Usage (--raiz <repo con BMAD> va ANTES del subcomando: bmad.py --proyecto ./g --raiz .. detectar; por defecto se busca hacia
  arriba desde --proyecto; en estado.json la raíz se guarda relativa a --proyecto):
  bmad.py --proyecto ./gestion detectar                 # layout, versión si es visible, rutas → estado.json.integraciones.bmad
  bmad.py --proyecto ./gestion inventario [--json]      # artefactos encontrados, estado (front matter), huella sha256
  bmad.py --proyecto ./gestion requisitos               # FR/NFR/UJ/SM/AD/UX-DR → 02-planificacion/especificacion/requisitos-bmad.csv
  bmad.py --proyecto ./gestion trazabilidad [--wbs 02-planificacion/wbs.csv]   # FR → historias → paquetes WBS
  bmad.py --proyecto ./gestion backlog                  # sincroniza columnas derivadas de 02-planificacion/backlog.csv
  bmad.py --proyecto ./gestion avance [--json]          # estados de historias/épicas → 03-control/reportes/avance-bmad.csv
  bmad.py --proyecto ./gestion linea-base prd|arquitectura|epicas|brief|ux --version 1.0 --por "Ejecutivo: Nombre" [--fecha AAAA-MM-DD]
  bmad.py --proyecto ./gestion verificar [--json]       # desvíos contra la línea base y propuestas de cambio nuevas
  bmad.py --proyecto ./gestion recorridos [--id UJ-2] [--json]   # detalle de los recorridos UJ-n: campos, FR que los realizan, KPI SM-n
  bmad.py --proyecto ./gestion capacidades [--json]     # mapa de capacidades → módulo → AD-n, decisiones diferidas y stack
  bmad.py --proyecto ./gestion indice                   # contrato pm-spec-index/1 (lo usa especificacion.py; normalmente no hace falta llamarlo)
  bmad.py --proyecto ./gestion handoff [--cambio C-001] # sentido inverso: decisión de gobierno → documento de traspaso al equipo BMAD
"""
import argparse, contextlib, csv, datetime, glob, hashlib, io, json, os, re, shutil, sys

try:
    import yaml
except ImportError:
    yaml = None
try:
    import tomllib
except ImportError:
    tomllib = None

AQUI = os.path.dirname(os.path.abspath(__file__))
for cand in (os.path.join(AQUI, "..", "..", "pm-estado-proyecto", "scripts"),):
    if os.path.isdir(cand): sys.path.insert(0, os.path.abspath(cand))
try:
    import esquema as E
except ImportError:
    E = None

VERSIONES_SOPORTADAS = "v4 · v6.11–v6.12"
IDS = re.compile(r"\b(FR|NFR|UJ|SM-C|SM|AD|UX-DR)-?(\d+)\b")   # SM-Cn: métricas de contrapeso de la plantilla de PRD 6.12
# Estados de historia: vocabulario de sprint-status (6.12) + estados heredados de v6 y del front matter de specs de bmad-build
ESTADOS_HIST = ["backlog", "ready-for-dev", "in-progress", "review", "done"]
ESTADO_LEGADO_V6 = {"drafted": "ready-for-dev", "contexted": "in-progress", "in-review": "review"}
CLAVE_HIST = re.compile(r"^(\d+)-(\d+[a-z]?)-.+")          # gramática de claves de sprint_plan.py (admite 2-6a-…)
STORY_H = re.compile(r"^#{2,4}\s*Story\s+(\d+)\.(\d+[a-z]?)\s*[:.\-–—]?\s*(.*?)\s*#*\s*$", re.I)
EPIC_H = re.compile(r"^#{1,3}\s*Epic\s+(\d+)\s*[:.\-–—]?\s*(.*?)\s*#*\s*$", re.I)
ESTADO_V4 = {"draft": "backlog", "approved": "ready-for-dev", "inprogress": "in-progress", "in progress": "in-progress",
             "review": "review", "done": "done"}

# ------------------------------------------------------------------ utilidades
def hoy(): return datetime.date.today().isoformat()

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""): h.update(b)
    return h.hexdigest()

def sha_conjunto(rutas):
    h = hashlib.sha256()
    for r in sorted(rutas): h.update(sha(r).encode())
    return h.hexdigest()

def front_matter(p):
    try: txt = open(p, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError): return {}
    if not txt.startswith("---"): return {}
    partes = txt.split("---", 2)
    if len(partes) < 3: return {}
    if yaml:
        try: d = yaml.safe_load(partes[1]); return d if isinstance(d, dict) else {}
        except Exception: return {}
    return dict(re.findall(r"(?m)^(\w+):\s*(.+)$", partes[1]))

def norm_id(tipo, num): return f"{tipo}{int(num)}" if tipo == "SM-C" else f"{tipo}-{int(num)}"

def tipo_id(tipo): return "SM" if tipo == "SM-C" else tipo

def slug_bmad(texto, maxlen=60):
    """Misma derivación de claves que sprint_plan.py de BMAD 6.12 (conserva tildes y ñ; corta en 60)."""
    s_ = re.sub(r"[^\w]+", "-", str(texto).lower(), flags=re.UNICODE).strip("-")
    s_ = s_[:maxlen].strip("-")
    return s_ or hashlib.sha256(str(texto).encode("utf-8")).hexdigest()[:8]

def orden_num(numero):
    out = []
    for x in str(numero).split("."):
        m = re.match(r"(\d+)([a-z]?)", x)
        out.append((int(m.group(1)), m.group(2)) if m else (0, x))
    return out

def norm_estado(v):
    v = str(v or "").strip().lower()
    return ESTADO_LEGADO_V6.get(v, v)

def cargar_estado(proyecto):
    f = os.path.join(proyecto, "estado.json")
    if not os.path.exists(f): sys.exit("No existe estado.json en --proyecto; crear el proyecto con nuevo_proyecto.py")
    e = json.load(open(f, encoding="utf-8"))
    return E.migrar(e) if E else e

def guardar_estado(proyecto, e):
    e["actualizado"] = hoy(); e["version_estado"] = e.get("version_estado", 0) + 1
    escribir_texto(os.path.join(proyecto, "estado.json"), json.dumps(e, ensure_ascii=False, indent=2))

def escribir_texto(ruta, texto, newline=None):
    """Escritura atómica con esquema.py (temporal + os.replace); los bytes son los de open(ruta, "w", newline=…)."""
    if E: E.escribir_atomico(ruta, texto, newline=newline)
    else: open(ruta, "w", encoding="utf-8", newline=newline).write(texto)

def escribir_filas(ruta, cols, filas, **kw):
    """CSV con csv.DictWriter (mismas opciones que antes), escrito de forma atómica."""
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=cols, **kw); w.writeheader(); w.writerows(filas)
    escribir_texto(ruta, buf.getvalue(), newline="")

def salida(proyecto, *partes):
    p = os.path.join(proyecto, *partes); os.makedirs(os.path.dirname(p), exist_ok=True); return p

def proteger(ruta_salida, bmad):
    """Garantiza que nada se escriba dentro de carpetas de BMAD."""
    rs = os.path.abspath(ruta_salida)
    for d in bmad.get("carpetas_protegidas", []):
        if rs.startswith(os.path.abspath(d) + os.sep):
            sys.exit(f"Bloqueado: el puente no escribe en carpetas de BMAD ({d}). Ubicar la carpeta del proyecto fuera de ellas.")

# ------------------------------------------------------------------ detección
def buscar_raiz(desde):
    d = os.path.abspath(desde)
    while True:
        if os.path.isdir(os.path.join(d, "_bmad")) or os.path.isdir(os.path.join(d, ".bmad-core")): return d
        padre = os.path.dirname(d)
        if padre == d: return None
        d = padre

def _plano(d, pref=""):
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, dict): out.update(_plano(v, f"{pref}{k}."))
        else: out[f"{pref}{k}"] = v; out.setdefault(k, v)
    return out

def leer_config_v6(raiz):
    cfg = {}
    for p in sorted(glob.glob(os.path.join(raiz, "_bmad", "*", "config.yaml"))):
        if yaml:
            try: cfg.update({k: v for k, v in _plano(yaml.safe_load(open(p, encoding="utf-8")) or {}).items() if not isinstance(v, (list, dict))})
            except Exception: pass
    if tomllib:   # capas TOML de v6.11+: equipo, usuario y personalizaciones (estas últimas mandan)
        for p in [os.path.join(raiz, "_bmad", "config.toml"), os.path.join(raiz, "_bmad", "config.user.toml")] + sorted(glob.glob(os.path.join(raiz, "_bmad", "custom", "config*.toml"))):
            if os.path.exists(p):
                try: cfg.update({k: v for k, v in _plano(tomllib.load(open(p, "rb"))).items() if not isinstance(v, (list, dict))})
                except Exception: pass
    def res(v):
        v = str(v)
        for _ in range(4):
            v = v.replace("{project-root}", raiz).replace("{project_root}", raiz)
            for k in ("output_folder", "planning_artifacts", "implementation_artifacts"):
                if "{" + k + "}" in v and k in cfg: v = v.replace("{" + k + "}", str(cfg[k]))
        return os.path.normpath(v if os.path.isabs(v) else os.path.join(raiz, v))
    salida_ = res(cfg.get("output_folder", "_bmad-output"))
    cfg["output_folder"] = salida_
    plan = res(cfg.get("planning_artifacts", os.path.join(salida_, "planning-artifacts")))
    impl = res(cfg.get("implementation_artifacts", os.path.join(salida_, "implementation-artifacts")))
    version, fuente_v = leer_version_v6(raiz)
    return {"layout": "v6", "raiz": raiz, "salida": salida_, "planning": plan, "implementation": impl, "version": version,
            "version_fuente": os.path.relpath(fuente_v, raiz) if fuente_v else "",
            "carpetas_protegidas": [os.path.join(raiz, "_bmad"), salida_]}

def leer_version_v6(raiz):
    """6.12 registra la versión en _bmad/_config/manifest.yaml (installation.version y una por módulo) y en la cabecera
    '# Version: x.y.z' de cada _bmad/<módulo>/config.yaml. Se lee en ese orden; nunca se infiere."""
    man = os.path.join(raiz, "_bmad", "_config", "manifest.yaml")
    if os.path.exists(man):
        try:
            txt = open(man, encoding="utf-8").read()
            if yaml:
                d = yaml.safe_load(txt) or {}
                v = (d.get("installation") or {}).get("version") or next((m.get("version") for m in d.get("modules") or []
                                                                           if isinstance(m, dict) and m.get("name") in ("bmm", "core")), "")
                if v: return str(v), man
            m = re.search(r"(?m)^\s*version:\s*['\"]?(\d+\.\d+[\w.\-]*)", txt)
            if m: return m.group(1), man
        except (OSError, UnicodeDecodeError): pass
    for p in sorted(glob.glob(os.path.join(raiz, "_bmad", "*", "config.yaml"))) + sorted(glob.glob(os.path.join(raiz, "_bmad", "_config", "*.yaml"))):
        try:
            m = re.search(r"(?mi)^\s*#?\s*version:\s*['\"]?v?(\d+\.\d+[\w.\-]*)", open(p, encoding="utf-8").read())
            if m: return m.group(1), p
        except (OSError, UnicodeDecodeError, IsADirectoryError): pass
    return "", ""

def leer_config_v4(raiz):
    cfg = {}
    p = os.path.join(raiz, ".bmad-core", "core-config.yaml")
    if yaml and os.path.exists(p):
        try: cfg = _plano(yaml.safe_load(open(p, encoding="utf-8")) or {})
        except Exception: cfg = {}
    j = lambda v, d: os.path.normpath(os.path.join(raiz, str(cfg.get(v, d))))
    return {"layout": "v4", "raiz": raiz, "prd": j("prdFile", "docs/prd.md"), "prd_shard": j("prdShardedLocation", "docs/prd"),
            "prd_sharded": bool(cfg.get("prdSharded", False)), "arquitectura": j("architectureFile", "docs/architecture.md"),
            "arquitectura_shard": j("architectureShardedLocation", "docs/architecture"), "historias": j("devStoryLocation", "docs/stories"),
            "version": str(cfg.get("version", "")), "carpetas_protegidas": [os.path.join(raiz, ".bmad-core")]}

def detectar_bmad(proyecto, raiz_arg=None, e=None):
    e = e or cargar_estado(proyecto)
    guardada = (e.get("integraciones", {}).get("bmad", {}) or {}).get("raiz") if e else None
    if guardada and not os.path.isabs(guardada): guardada = os.path.normpath(os.path.join(proyecto, guardada))  # relativa a --proyecto
    elif guardada and not raiz_arg:
        # raíz absoluta de una versión anterior: si no contiene al proyecto (repositorio copiado o movido), manda el BMAD propio
        propia = buscar_raiz(proyecto)
        if propia and os.path.abspath(propia) != os.path.abspath(guardada) and \
                not (os.path.abspath(proyecto) + os.sep).startswith(os.path.abspath(guardada).rstrip(os.sep) + os.sep):
            print(f"AVISO: estado.json apunta a BMAD en {guardada}, que no contiene al proyecto; se usa el del repositorio ({propia}). "
                  "Correr 'bmad.py detectar' para guardar la raíz relativa.", file=sys.stderr)
            guardada = propia
    raiz = raiz_arg or guardada or buscar_raiz(proyecto)
    if not raiz or not os.path.isdir(raiz): sys.exit("No se encontró BMAD (_bmad/ o .bmad-core/). Indicar --raiz <carpeta del repositorio>.")
    raiz = os.path.abspath(raiz)
    if os.path.isdir(os.path.join(raiz, "_bmad")): b = leer_config_v6(raiz)
    elif os.path.isdir(os.path.join(raiz, ".bmad-core")): b = leer_config_v4(raiz)
    else: sys.exit(f"En {raiz} no hay _bmad/ ni .bmad-core/.")
    v = b.get("version", "")
    b["soporte"] = ("v4" if b["layout"] == "v4" else
                    ("soportada" if re.match(r"6\.1[12]\b", v) else ("version-no-visible" if not v else f"no-probada ({v})")))
    return b

# ------------------------------------------------------------------ inventario
def _ultimo(patron):
    xs = glob.glob(patron, recursive=True)
    return sorted(xs, key=lambda p: (re.findall(r"\d{4}-\d{2}-\d{2}", p) or [""])[-1] + str(os.path.getmtime(p)))

def inventario(b):
    arts = {}
    def add(clave, rutas, previas=()):
        rutas = [r for r in rutas if os.path.isfile(r)]
        if rutas: arts[clave] = {"rutas": rutas, "previas": [p for p in previas if os.path.isfile(p)]}
    if b["layout"] == "v6":
        P, I = b["planning"], b["implementation"]
        for clave, pats in {"brief": ["briefs/**/brief.md", "*brief*.md", "product-brief*.md"],
                            "prd": ["prds/**/prd.md", "*prd*.md", "*prd*/index.md"],
                            "arquitectura": ["architecture/**/ARCHITECTURE-SPINE.md", "architecture/**/*.md", "*architecture*.md"],
                            "ux": ["ux-designs/**/DESIGN.md", "ux-designs/**/EXPERIENCE.md", "*ux*.md"]}.items():
            for pat in pats:
                xs = _ultimo(os.path.join(P, pat))
                xs = [x for x in xs if not os.path.basename(x).startswith(".") and not x.endswith(("addendum.md",))]
                if xs:
                    if clave == "ux":
                        carpeta = os.path.dirname(xs[-1]); add(clave, sorted(glob.glob(os.path.join(carpeta, "*.md"))), [])
                    elif clave == "arquitectura" and "ARCHITECTURE-SPINE" not in xs[-1] and pat == "architecture/**/*.md":
                        add(clave, [xs[-1]], xs[:-1])
                    else:
                        add(clave, [xs[-1]], xs[:-1])
                    break
        # fase de descubrimiento (brainstorming, PRFAQ, investigación): solo se leen; nombres de carpeta tomados como patrones amplios [verificar por versión]
        desc = []
        for pat in ("brainstorming/**/*.md", "*brainstorm*.md", "prfaq*/**/*.md", "*prfaq*.md", "research/**/*.md", "*research*.md", "*investigacion*.md"):
            desc += [x for x in glob.glob(os.path.join(P, pat), recursive=True) if not os.path.basename(x).startswith(".") and x not in desc]
        add("descubrimiento", sorted(desc))
        add("epicas", [os.path.join(P, "epics.md")] if os.path.exists(os.path.join(P, "epics.md")) else glob.glob(os.path.join(P, "*epic*.md")))
        add("estado-sprint", [os.path.join(I, "sprint-status.yaml")])
        add("propuestas-cambio", sorted(glob.glob(os.path.join(P, "sprint-change-proposal-*.md"))))
        add("historias", sorted(glob.glob(os.path.join(I, "[0-9]*-[0-9]*-*.md")) + glob.glob(os.path.join(I, "spec-*.md"))))
    else:
        if b["prd_sharded"] and os.path.isdir(b["prd_shard"]): add("prd", sorted(glob.glob(os.path.join(b["prd_shard"], "*.md"))))
        else: add("prd", [b["prd"]])
        if os.path.isdir(b["arquitectura_shard"]): add("arquitectura", sorted(glob.glob(os.path.join(b["arquitectura_shard"], "*.md"))))
        else: add("arquitectura", [b["arquitectura"]])
        docs = os.path.dirname(b["prd"])
        add("brief", [os.path.join(docs, "brief.md"), os.path.join(docs, "project-brief.md")])
        add("ux", [os.path.join(docs, "front-end-spec.md")])
        add("epicas", sorted(glob.glob(os.path.join(b["prd_shard"], "epic-*.md")) + glob.glob(os.path.join(docs, "epic-*.md"))))
        add("historias", sorted(glob.glob(os.path.join(b["historias"], "*.story.md"))))
    for k, a in arts.items():
        a["sha256"] = sha_conjunto(a["rutas"])
        fm = front_matter(a["rutas"][0]) if a["rutas"][0].endswith(".md") else {}
        a["estado_bmad"] = str(fm.get("status", "")) if fm else ""
        a["modificado"] = datetime.datetime.fromtimestamp(max(os.path.getmtime(r) for r in a["rutas"])).isoformat(timespec="minutes")
    return arts

# ------------------------------------------------------------------ requisitos
def extraer_ids(rutas, fuente):
    vistos, filas = set(), []
    for r in rutas:
        for n, linea in enumerate(open(r, encoding="utf-8", errors="replace"), 1):
            for m in IDS.finditer(linea):
                i = norm_id(m.group(1), m.group(2))
                # definición = la primera aparición en una línea que empieza por viñeta/encabezado/negrita con el id
                if i in vistos: continue
                if not re.match(r"^\s*([-*]|#+|\*\*|\|)?\s*\**\s*" + re.escape(m.group(0)), linea): continue
                titulo = re.sub(r"^\s*([-*]|#+|\|)?\s*\**\s*" + re.escape(m.group(0)) + r"\**\s*[:.\-–—]?\s*\**", "", linea)
                titulo = re.sub(r"\s+", " ", titulo.replace("**", "")).strip(" *|:—–-\n")
                vistos.add(i); filas.append({"id": i, "tipo": tipo_id(m.group(1)), "titulo": titulo[:200], "fuente": os.path.relpath(r), "linea": n})
    return filas

def requisitos(b, arts):
    filas = []
    if "prd" in arts: filas += extraer_ids(arts["prd"]["rutas"], "prd")
    if "arquitectura" in arts: filas += [f for f in extraer_ids(arts["arquitectura"]["rutas"], "arquitectura") if f["tipo"] == "AD"]
    if "epicas" in arts: filas += [f for f in extraer_ids(arts["epicas"]["rutas"], "epicas") if f["tipo"] == "UX-DR"]
    vistos, out = set(), []
    for f in filas:
        if f["id"] not in vistos: vistos.add(f["id"]); out.append(f)
    return out

# ------------------------------------------------------------------ épicas e historias
def slug(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def refs_epicas(arts):
    """Cobertura declarada a nivel de épica en epics.md (6.12: 'FR1: Epic 1 - …' en el FR Coverage Map y
    '**FRs covered:** FR1, FR2' bajo cada épica). Devuelve {numero_epica: set(ids)}."""
    out = {}
    for r in arts.get("epicas", {}).get("rutas", []):
        seccion, epica, en_codigo = "", None, False
        for linea in open(r, encoding="utf-8", errors="replace"):
            if re.match(r"^\s{0,3}(```|~~~)", linea): en_codigo = not en_codigo; continue
            if en_codigo: continue
            m = EPIC_H.match(linea)
            if m: epica = m.group(1); seccion = "epica"; continue
            if re.match(r"^#{1,4}\s", linea):
                if re.search(r"coverage|cobertura", linea, re.I): seccion, epica = "cobertura", None
                elif not (epica and STORY_H.match(linea)): seccion, epica = "otra", None   # las historias no cierran su épica
                continue
            if seccion == "cobertura":
                m = re.match(r"^\s*[-*]?\s*\**\s*(FR-?\d+|NFR-?\d+|UX-DR-?\d+)\s*\**\s*:\s*(.*)$", linea)
                if m and not re.search(r"Story\s+\d+\.\d+", m.group(2), re.I):
                    mm = IDS.match(m.group(1))
                    for ep in re.findall(r"\bEpic\s+(\d+)", m.group(2), re.I): out.setdefault(ep, set()).add(norm_id(mm.group(1), mm.group(2)))
            elif epica and re.search(r"(FRs?|NFRs?|requisitos?|requirements?)\s*(covered|cubiertos?)", linea, re.I):
                for mm in IDS.finditer(linea): out.setdefault(epica, set()).add(norm_id(mm.group(1), mm.group(2)))
    return out

def archivos_historia_v6(arts):
    """Archivos de historia de 6.12: specs de bmad-build (spec-N-M-slug.md, status draft|ready-for-dev|in-progress|in-review|done)
    y archivos N-M-slug.md (create-story heredado / shims). Devuelve {numero: (ruta, estado_normalizado)}."""
    out = {}
    for r in arts.get("historias", {}).get("rutas", []):
        base = os.path.basename(r)
        m = re.match(r"^(?:spec-)?(\d+)-(\d+[a-z]?)-", base)
        if not m: continue
        fm = front_matter(r)
        est = norm_estado(fm.get("status") if fm else "")
        if not est:
            mm = re.search(r"(?mi)^\s*(?:#+\s*)?Status\s*:?\s*\n*\s*([A-Za-z\-]+)", open(r, encoding="utf-8", errors="replace").read())
            est = norm_estado(mm.group(1)) if mm else ""
        out[f"{m.group(1)}.{m.group(2)}"] = (r, est)
    return out

def historias(b, arts):
    """Devuelve {clave: {epica, numero, titulo, refs, refs_epica, estado}} combinando épicas y estado de sprint/historias.
    v6: la clave es la de sprint-status.yaml cuando existe (BMAD conserva tildes y corta en 60 caracteres); si no, se deriva
    con la misma regla que sprint_plan.py."""
    hs = {}
    for r in arts.get("epicas", {}).get("rutas", []):
        actual = None; en_codigo = False
        for linea in open(r, encoding="utf-8", errors="replace"):
            if re.match(r"^\s{0,3}(```|~~~)", linea): en_codigo = not en_codigo
            m = None if en_codigo else EPIC_H.match(linea)
            if m: actual = None; continue
            m = None if en_codigo else STORY_H.match(linea)
            if m:
                e_, s_, t_ = m.groups()
                clave = f"{e_}-{s_}-{slug_bmad(t_) if b['layout'] == 'v6' else slug(t_)}"
                actual = clave; hs[clave] = {"epica": e_, "numero": f"{e_}.{s_}", "titulo": t_.strip(), "refs": set(), "estado": "", "texto": ""}
                continue
            if actual and not en_codigo and re.match(r"^#{1,2}\s", linea): actual = None; continue
            if actual:
                hs[actual]["texto"] += linea
                for mm in IDS.finditer(linea): hs[actual]["refs"].add(norm_id(mm.group(1), mm.group(2)))
    # mapa de cobertura con historia explícita (FR1: Epic 1 (Story 1.1))
    for r in arts.get("epicas", {}).get("rutas", []):
        for linea in open(r, encoding="utf-8", errors="replace"):
            m = re.match(r"^\s*[-*]?\s*\**\s*(FR-?\d+)\s*\**\s*:\s*(.*)$", linea)
            if m:
                fr = norm_id("FR", re.sub(r"\D", "", m.group(1)))
                for s in re.findall(r"Story\s+(\d+\.\d+[a-z]?)", m.group(2)):
                    for k, h in hs.items():
                        if h["numero"] == s: h["refs"].add(fr)
    rep = refs_epicas(arts) if b["layout"] == "v6" else {}
    # estado: v6 sprint-status.yaml (+ piso por archivo de historia); v4 archivos de historia
    if b["layout"] == "v6":
        if "estado-sprint" in arts and yaml:
            try: ds = (yaml.safe_load(open(arts["estado-sprint"]["rutas"][0], encoding="utf-8")) or {}).get("development_status", {}) or {}
            except Exception: ds = {}
            por_num = {h["numero"]: k for k, h in hs.items()}
            for k, v in ds.items():
                k = str(k); m = CLAVE_HIST.match(k)
                if not m: continue
                num = f"{m.group(1)}.{m.group(2)}"
                if k in hs: hs[k]["estado"] = norm_estado(v)
                elif num in por_num:   # misma historia con otra derivación de slug: manda la clave de sprint-status
                    h = hs.pop(por_num[num]); h["estado"] = norm_estado(v); hs[k] = h; por_num[num] = k
                else:
                    hs[k] = {"epica": m.group(1), "numero": num, "titulo": k.split("-", 2)[2].replace("-", " "), "refs": set(), "estado": norm_estado(v), "texto": ""}
                    por_num[num] = k
        por_num = {h["numero"]: k for k, h in hs.items()}
        for num, (ruta, est) in archivos_historia_v6(arts).items():
            k = por_num.get(num)
            if not k: continue
            hs[k]["archivo"] = os.path.relpath(ruta, b["raiz"]); hs[k]["estado_archivo"] = est
            # piso como sprint_plan.py: un archivo de historia aprobado implica al menos ready-for-dev; sprint-status manda hacia arriba
            if est and est != "draft" and hs[k]["estado"] in ("", "backlog"): hs[k]["estado"] = "ready-for-dev"
    elif b["layout"] == "v4":
        for r in arts.get("historias", {}).get("rutas", []):
            txt = open(r, encoding="utf-8", errors="replace").read()
            num = os.path.basename(r).split(".story")[0]
            m = re.search(r"(?mi)^#+\s*Status\s*\n+\s*([A-Za-z ]+)", txt)
            est = ESTADO_V4.get((m.group(1).strip().lower() if m else ""), (m.group(1).strip().lower() if m else ""))
            t = re.search(r"(?m)^#\s*Story\s+[\d.]+\s*[:.\-–]?\s*(.*)$", txt)
            k = next((kk for kk, h in hs.items() if h["numero"] == num), None)
            if not k:
                k = f"{num.replace('.', '-')}-{slug(t.group(1)) if t else 'historia'}"
                hs[k] = {"epica": num.split(".")[0], "numero": num, "titulo": t.group(1).strip() if t else num, "refs": set(), "estado": "", "texto": txt}
            hs[k]["estado"] = est
            for mm in IDS.finditer(txt): hs[k]["refs"].add(norm_id(mm.group(1), mm.group(2)))
    for h in hs.values():
        h["estado"] = h["estado"] or "backlog"
        h["refs_epica"] = set(rep.get(h["epica"], set()))
    return hs

def historias_de(q_id, hs):
    """Historias que cubren un id: primero por referencia directa; si no hay, por la cobertura declarada de su épica.
    Devuelve (claves, nivel) con nivel 'historia' | 'epica' | ''."""
    directas = sorted(k for k, h in hs.items() if q_id in h["refs"])
    if directas: return directas, "historia"
    por_epica = sorted((k for k, h in hs.items() if q_id in h.get("refs_epica", ())), key=lambda k: orden_num(hs[k]["numero"]))
    return (por_epica, "epica") if por_epica else ([], "")

# ------------------------------------------------------------------ detalle de solo lectura: recorridos UJ y mapa de capacidades
CAMPOS_UJ = [("persona", r"persona"), ("entrada", r"estado de entrada|entry state|entry"), ("recorrido", r"recorrido|journey|path|flow"),
             ("climax", r"cl[ií]max|climax"), ("resolucion", r"resoluci[oó]n|resolution"), ("caso_limite", r"caso l[ií]mite|edge case")]

def _ids_rango(texto, tipo="FR"):
    """Ids de un tipo en un texto, con rangos 'FR-1 a FR-8' / 'FR-1 to FR-8' expandidos."""
    out = set()
    for m in re.finditer(rf"\b{tipo}-(\d+)\s+(?:a|to|al|hasta)\s+{tipo}-(\d+)\b", texto):
        out |= {f"{tipo}-{i}" for i in range(int(m.group(1)), int(m.group(2)) + 1)}
    out |= {f"{tipo}-{int(n)}" for n in re.findall(rf"\b{tipo}-(\d+)\b", texto)}
    return out

def recorridos(arts):
    """Recorridos de usuario (UJ-n) del PRD con sus campos, los FR que los realizan y las métricas SM-n que validan esos FR.
    Solo lectura. Un FR realiza un UJ si su bloque dice 'Realiza UJ-n' (o 'Realizes'); si solo lo dice la sección, nivel 'seccion'."""
    rutas = arts.get("prd", {}).get("rutas", [])
    ujs, frs, sms, contrapesos = {}, {}, {}, {}
    for r in rutas:
        actual = None; fr = None; seccion_uj = set(); seccion_frs = []
        for n, l in enumerate(open(r, encoding="utf-8", errors="replace"), 1):
            h = re.match(r"^(#{1,6})\s+(.*)$", l)
            if h:
                actual = None
                mfr = re.match(r"^(FR)-?(\d+)\b", h.group(2).strip())
                if mfr: fr = f"FR-{int(mfr.group(2))}"; frs.setdefault(fr, {"directos": set(), "seccion": set(seccion_uj)}); seccion_frs.append(fr)
                elif len(h.group(1)) <= 3: fr = None; seccion_uj = set(); seccion_frs = []
                continue
            mu = re.match(r"^\s*[-*]\s*\*\*\s*UJ-?(\d+)\s*[.:\-–—]?\s*(.*?)\*\*\s*(.*)$", l)
            if mu:
                actual = f"UJ-{int(mu.group(1))}"
                ujs[actual] = {"id": actual, "titulo": (mu.group(2) + " " + mu.group(3)).strip().rstrip("."), "fuente": os.path.relpath(r), "linea": n,
                               **{k: "" for k, _ in CAMPOS_UJ}}
                continue
            if actual:
                mc = re.match(r"^\s+[-*]\s*\*\*([^*:]+):?\*\*:?\s*(.*)$", l)
                if mc:
                    for k, rx in CAMPOS_UJ:
                        if re.match(rf"^\s*({rx})", mc.group(1).strip(), re.I) and not ujs[actual][k]:
                            ujs[actual][k] = mc.group(2).strip(); break
                    continue
                if l.strip() and not l.startswith((" ", "\t")): actual = None
            if re.search(r"\b(Realiza|Realizes|Realises)\b", l):
                u = {f"UJ-{int(x)}" for x in re.findall(r"\bUJ-?(\d+)\b", l)}
                if fr: frs[fr]["directos"] |= u
                else: seccion_uj |= u
            ms = re.match(r"^\s*[-*]\s*\*\*\s*(SM-C?)(\d+)\b[^*]*\*\*\s*(.*)$", l)
            if ms:
                sid = f"{ms.group(1)}{int(ms.group(2))}" if ms.group(1) == "SM-C" else f"SM-{int(ms.group(2))}"
                if ms.group(1) == "SM-C": contrapesos[sid] = {f"SM-{int(x)}" for x in re.findall(r"\bSM-(\d+)\b", l)}
                else: sms[sid] = _ids_rango(l)
    out = []
    for uid, u in sorted(ujs.items(), key=lambda kv: int(kv[0][3:])):
        directos = sorted((f for f, d in frs.items() if uid in d["directos"]), key=lambda x: int(x[3:]))
        seccion = sorted((f for f, d in frs.items() if uid in d["seccion"] and uid not in d["directos"] and not d["directos"]), key=lambda x: int(x[3:]))
        todos = set(directos) | set(seccion)
        kpi = sorted((s for s, fs in sms.items() if fs & todos), key=lambda x: int(x[3:]))
        out.append({**u, "frs": directos, "frs_seccion": seccion, "kpi": kpi,
                    "contrapesos": sorted(c for c, base in contrapesos.items() if base & set(kpi))})
    return out

def capacidades(arts):
    """Mapa de capacidades → módulo → decisiones (AD-n), decisiones diferidas y stack de la arquitectura. Solo lectura."""
    filas, diferidas, stack = [], [], []
    for r in arts.get("arquitectura", {}).get("rutas", []):
        seccion = ""
        for n, l in enumerate(open(r, encoding="utf-8", errors="replace"), 1):
            h = re.match(r"^#{1,6}\s+(.*)$", l)
            if h: seccion = h.group(1).strip().lower(); continue
            celdas = [c.strip() for c in l.strip().strip("|").split("|")] if l.lstrip().startswith("|") else []
            if celdas and set("".join(celdas)) <= set("-: "): continue
            if re.search(r"capabilit|capacidad", seccion) and len(celdas) >= 3 and not re.match(r"^(capability|capacidad)", celdas[0], re.I):
                ids = sorted(_ids_rango(celdas[0], "FR") | _ids_rango(celdas[0], "NFR"), key=lambda x: (x.split("-")[0], int(x.split("-")[1])))
                nombre = re.sub(r"^\s*((N?FR-\d+)\s*(,|y|and|a|to)?\s*)+", "", celdas[0]).strip()
                filas.append({"capacidad": nombre or celdas[0], "ids": ids, "modulo": celdas[1].replace("`", ""),
                              "ad": sorted({f"AD-{int(x)}" for x in re.findall(r"\bAD-(\d+)\b", celdas[2])}, key=lambda x: int(x[3:])),
                              "fuente": os.path.relpath(r), "linea": n})
            elif re.search(r"deferred|diferid|pendiente", seccion) and re.match(r"^\s*[-*]\s+\S", l):
                texto = re.sub(r"^\s*[-*]\s+", "", l).strip()
                diferidas.append({"texto": texto, "tema": re.split(r"\s*[:(]", texto)[0].strip(), "fuente": os.path.relpath(r), "linea": n})
            elif seccion == "stack" and len(celdas) >= 2 and not re.match(r"^(name|nombre)$", celdas[0], re.I):
                stack.append({"nombre": celdas[0], "version": celdas[1], "fuente": os.path.relpath(r), "linea": n})
    return {"capacidades": filas, "diferidas": diferidas, "stack": stack}

# ------------------------------------------------------------------ comandos
def cmd_detectar(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e)
    e.setdefault("integraciones", {})["especificacion"] = "bmad"
    previo = e["integraciones"].get("bmad") or {}
    conservar = {k: previo[k] for k in ("handoffs", "propuestas_vistas", "ultimo_handoff_prioridades") if k in previo}
    e["integraciones"]["bmad"] = {k: (os.path.relpath(v, a.proyecto) if isinstance(v, str) and os.path.isabs(v) else v)
                                  for k, v in b.items() if k != "carpetas_protegidas"}
    e["integraciones"]["bmad"].update(conservar)
    e["integraciones"]["bmad"]["raiz"] = os.path.relpath(b["raiz"], a.proyecto)   # relativa: el repositorio se puede mover o clonar
    guardar_estado(a.proyecto, e)
    print(json.dumps({k: v for k, v in b.items() if k != "carpetas_protegidas"}, ensure_ascii=False, indent=2))
    if b["soporte"] not in ("soportada", "v4"):
        print(f"AVISO: versión de BMAD {b['soporte']}; el puente está probado con {VERSIONES_SOPORTADAS}. Se usa descubrimiento por patrones (modo degradado).")

def cmd_inventario(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e); arts = inventario(b)
    out = salida(a.proyecto, "02-planificacion", "especificacion", "inventario-bmad.json"); proteger(out, b)
    datos = {"generado": hoy(), "layout": b["layout"], "soporte": b["soporte"],
             "artefactos": {k: {**v, "rutas": [os.path.relpath(r, b["raiz"]) for r in v["rutas"]],
                                "previas": [os.path.relpath(r, b["raiz"]) for r in v["previas"]]} for k, v in arts.items()}}
    escribir_texto(out, json.dumps(datos, ensure_ascii=False, indent=2))
    if a.json: print(json.dumps(datos, ensure_ascii=False, indent=2)); return
    print(f"BMAD {b['layout']} ({b['soporte']}) en {b['raiz']}")
    for k, v in arts.items():
        print(f"  {k:18s} {len(v['rutas'])} archivo(s) · estado={v['estado_bmad'] or '-'} · {v['modificado']} · sha {v['sha256'][:12]} · {os.path.relpath(v['rutas'][0], b['raiz'])}"
              + (f" · {len(v['previas'])} versión(es) anterior(es)" if v["previas"] else ""))
    faltan = [k for k in ("brief", "prd", "arquitectura", "epicas") if k not in arts]
    if faltan: print("  No encontrados:", ", ".join(faltan))
    print(f"Inventario escrito en {os.path.relpath(out)}")

def cmd_requisitos(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e); arts = inventario(b); filas = requisitos(b, arts)
    out = salida(a.proyecto, "02-planificacion", "especificacion", "requisitos-bmad.csv"); proteger(out, b)
    escribir_filas(out, ["id", "tipo", "titulo", "fuente", "linea"], filas)
    cuenta = {}
    for f in filas: cuenta[f["tipo"]] = cuenta.get(f["tipo"], 0) + 1
    print(f"{len(filas)} identificadores · {cuenta} → {os.path.relpath(out)} (derivado: no editar)")

def cmd_trazabilidad(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e); arts = inventario(b); reqs = requisitos(b, arts); hs = historias(b, arts)
    wbs_refs = {}
    wbs = a.wbs or os.path.join("02-planificacion", "wbs.csv")
    if not os.path.isabs(wbs) and not os.path.exists(wbs): wbs = os.path.join(a.proyecto, wbs)
    if a.wbs and not os.path.exists(wbs): sys.exit(f"No existe la WBS indicada: {a.wbs} (se busca relativa a la carpeta actual y a --proyecto)")
    if os.path.exists(wbs):
        for r in csv.DictReader(open(wbs, encoding="utf-8")):
            for i in re.split(r"[;, ]+", r.get("ref") or ""):
                m = IDS.match(i.strip())
                if m: wbs_refs.setdefault(norm_id(m.group(1), m.group(2)), []).append(r["codigo"])
    filas = []
    for q in reqs:
        if q["tipo"] not in ("FR", "NFR", "UX-DR"): continue
        hh, nivel = historias_de(q["id"], hs)
        estados = [hs[k]["estado"] for k in hh]
        filas.append({"requisito": q["id"], "titulo": q["titulo"], "historias": ";".join(hh), "nivel_traza": nivel, "estados": ";".join(estados),
                      "paquetes_wbs": ";".join(wbs_refs.get(q["id"], [])),
                      "cubierto": "si" if hh else ("na" if q["tipo"] == "NFR" else "no"),
                      "terminado": "si" if hh and all(s == "done" for s in estados) else "no"})
    out = salida(a.proyecto, "02-planificacion", "especificacion", "matriz-trazabilidad-bmad.csv"); proteger(out, b)
    escribir_filas(out, list(filas[0].keys()) if filas else ["requisito"], filas)
    ids_validos = {q["id"] for q in reqs}
    sin_hist = [f["requisito"] for f in filas if f["cubierto"] == "no"]
    hist_sin_req = [k for k, h in hs.items() if not ((h["refs"] | h.get("refs_epica", set())) & ids_validos)]
    por_epica = [f["requisito"] for f in filas if f["nivel_traza"] == "epica"]
    refs_rotas = sorted(set(wbs_refs) - ids_validos)
    print(f"{len(filas)} requisitos trazados → {os.path.relpath(out)}")
    print(f"  Requisitos funcionales sin historia: {', '.join(sin_hist) or 'ninguno'}")
    print(f"  Historias sin requisito: {', '.join(hist_sin_req) or 'ninguna'}")
    if por_epica: print(f"  Trazados solo a nivel de épica (epics.md no cita el id en la historia): {', '.join(por_epica)}")
    if os.path.exists(wbs): print(f"  Referencias de la WBS a ids inexistentes: {', '.join(refs_rotas) or 'ninguna'}")

COL_BACKLOG = ["id", "tipo", "titulo", "descripcion", "prioridad", "moscow", "estimacion", "estado", "iteracion", "release",
               "producto_pbs", "criterios_aceptacion", "origen", "refs"]
DERIVADAS = {"tipo", "titulo", "descripcion", "estado", "origen", "refs", "criterios_aceptacion"}

def cmd_backlog(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e); arts = inventario(b); hs = historias(b, arts)
    p = os.path.join(a.proyecto, "02-planificacion", "backlog.csv"); proteger(p, b)
    filas, cols = [], list(COL_BACKLOG)
    if os.path.exists(p):
        with open(p, newline="", encoding="utf-8") as f:
            rd = csv.DictReader(f); filas = list(rd); cols = list(rd.fieldnames or COL_BACKLOG)
        cols += [c for c in COL_BACKLOG if c not in cols]
    por_id = {f.get("id"): f for f in filas}
    nuevos = actualizados = 0
    for k, h in sorted(hs.items(), key=lambda kv: orden_num(kv[1]["numero"])):
        fila = por_id.get(k)
        if not fila:
            fila = {c: "" for c in cols}; fila["id"] = k; filas.append(fila); por_id[k] = fila; nuevos += 1
        else: actualizados += 1
        parrafo = []                                    # primer párrafo (la historia "As a…, I want…, so that…" suele ocupar varias líneas)
        for l in h["texto"].splitlines():
            l = l.strip()
            if not l:
                if parrafo: break
                continue
            if l.startswith("#") or (parrafo and re.match(r"^(\*\*|[-*] |\d+\.)", l)): break
            parrafo.append(re.sub(r"^\*\*|\*\*$", "", l).strip())
        primera = re.sub(r"\*\*", "", " ".join(parrafo))
        fila.update({"tipo": "historia", "titulo": h["titulo"], "descripcion": primera[:240], "estado": h["estado"], "origen": "bmad",
                     "refs": ";".join(sorted(h["refs"] or h.get("refs_epica", set()))), "criterios_aceptacion": f"ver épicas BMAD, historia {h['numero']}"})
    retiradas = [f["id"] for f in filas if f.get("origen") == "bmad" and f["id"] not in hs]
    for f in filas:
        if f["id"] in retiradas: f["estado"] = "retirada-en-bmad"
    escribir_filas(p, cols, filas, extrasaction="ignore")
    print(f"backlog.csv: {nuevos} nuevas, {actualizados} actualizadas, {len(retiradas)} retiradas en BMAD. "
          f"Columnas derivadas ({', '.join(sorted(DERIVADAS))}) se sobrescriben; las de gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs) no se tocan.")

def cmd_avance(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e); arts = inventario(b); hs = historias(b, arts)
    estados = ["backlog", "ready-for-dev", "in-progress", "review", "done"]
    cuenta = {s: 0 for s in estados}
    for h in hs.values(): cuenta[h["estado"]] = cuenta.get(h["estado"], 0) + 1
    puntos = {}
    p = os.path.join(a.proyecto, "02-planificacion", "backlog.csv")
    if os.path.exists(p):
        for f in csv.DictReader(open(p, encoding="utf-8")):
            try: puntos[f["id"]] = float(f.get("estimacion") or 0)
            except ValueError: pass
    tot_pts = sum(puntos.get(k, 0) for k in hs); done_pts = sum(puntos.get(k, 0) for k, h in hs.items() if h["estado"] == "done")
    epicas = {}
    for h in hs.values(): epicas.setdefault(h["epica"], []).append(h["estado"])
    ep_done = sum(1 for v in epicas.values() if v and all(s == "done" for s in v))
    fila = {"fecha": a.corte or hoy(), "historias": len(hs), **{s: cuenta.get(s, 0) for s in estados}, "epicas": len(epicas), "epicas_terminadas": ep_done,
            "puntos_total": tot_pts, "puntos_terminados": done_pts,
            "pct_terminado": round(100 * (done_pts / tot_pts if tot_pts else cuenta["done"] / len(hs) if hs else 0), 1),
            "base_pct": "puntos" if tot_pts else "historias"}
    out = salida(a.proyecto, "03-control", "reportes", "avance-bmad.csv"); proteger(out, b)
    previas = []
    if os.path.exists(out):
        with open(out, newline="", encoding="utf-8") as f: previas = [r for r in csv.DictReader(f) if r.get("fecha") != fila["fecha"]]
    escribir_filas(out, list(fila.keys()), previas + [fila], extrasaction="ignore")   # una fila por fecha de corte (re-ejecutar no duplica)
    if a.json: print(json.dumps(fila, ensure_ascii=False, indent=2))
    else: print(f"Historias {len(hs)} · " + " · ".join(f"{s} {cuenta.get(s,0)}" for s in estados) + f" · épicas terminadas {ep_done}/{len(epicas)} · {fila['pct_terminado']} % ({fila['base_pct']}) → {os.path.relpath(out)}")

CLAVES_LB = {"prd": "bmad-prd", "arquitectura": "bmad-arquitectura", "epicas": "bmad-epicas", "brief": "bmad-brief", "ux": "bmad-ux"}

def ids_de(arts, clave):
    return sorted({f["id"] for f in extraer_ids(arts[clave]["rutas"], clave)}) if clave in arts else []

def cmd_linea_base(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e); arts = inventario(b)
    if a.artefacto not in arts: sys.exit(f"No se encontró el artefacto BMAD '{a.artefacto}'. Ejecutar 'inventario'.")
    art = arts[a.artefacto]; clave = CLAVES_LB[a.artefacto]
    if a.artefacto in ("prd", "arquitectura") and art["estado_bmad"] and art["estado_bmad"] not in ("final", "approved"):
        print(f"AVISO: el front matter de BMAD dice status={art['estado_bmad']}; una línea base normalmente se fija sobre status: final.")
    hist = salida(a.proyecto, "00-direccion", "historial", f"{clave}-v{a.version}"); proteger(hist, b)
    os.makedirs(hist, exist_ok=True)
    for r in art["rutas"]: shutil.copy2(r, os.path.join(hist, os.path.basename(r)))
    copia_principal = os.path.join(hist, os.path.basename(art["rutas"][0]))
    e["artefactos"][clave] = {"ruta": os.path.relpath(copia_principal, a.proyecto), "externo": "bmad",
                              "rutas_bmad": [os.path.relpath(r, b["raiz"]) for r in art["rutas"]],
                              "estado": "aprobado", "version": a.version, "aprobado_por": a.por, "fecha": a.fecha or hoy(), "sha256": art["sha256"],
                              "copia": os.path.relpath(hist, a.proyecto), "ids": ids_de(arts, a.artefacto)}
    guardar_estado(a.proyecto, e)
    if E: E.anotar_decision(a.proyecto, f"línea base {clave} v{a.version} (sha {art['sha256'][:12]})", a.por, nivel=a.nivel,
                            artefactos=";".join(e["artefactos"][clave]["rutas_bmad"]), notas="puente BMAD", fecha=a.fecha)
    print(f"Línea base {clave} v{a.version} registrada · sha {art['sha256'][:12]} · copia congelada en {os.path.relpath(hist)}")

def cmd_verificar(a, e):
    b = detectar_bmad(a.proyecto, a.raiz, e); arts = inventario(b)
    hallazgos = []
    for art_k, clave in CLAVES_LB.items():
        lb = e.get("artefactos", {}).get(clave)
        if not lb or "sha256" not in lb: continue
        if art_k not in arts: hallazgos.append({"tipo": "falta", "artefacto": clave, "detalle": "el artefacto con línea base ya no se encuentra"}); continue
        if arts[art_k]["sha256"] != lb["sha256"]:
            antes, ahora = set(lb.get("ids", [])), set(ids_de(arts, art_k))
            hallazgos.append({"tipo": "desvio", "artefacto": clave, "version_base": lb.get("version"),
                              "ids_agregados": sorted(ahora - antes), "ids_retirados": sorted(antes - ahora),
                              "detalle": "contenido distinto de la línea base aprobada → tratar como solicitud de cambio (pm-issues-cambios) salvo elaboración progresiva declarada"})
    visto = set(e.get("integraciones", {}).get("bmad", {}).get("propuestas_vistas", []))
    nuevas = [os.path.relpath(r, b["raiz"]) for r in arts.get("propuestas-cambio", {}).get("rutas", []) if os.path.relpath(r, b["raiz"]) not in visto]
    for n in nuevas: hallazgos.append({"tipo": "propuesta-cambio", "artefacto": n, "detalle": "Sprint Change Proposal de BMAD: registrar issue solicitud-cambio y decidir por la autoridad de cambio PRINCE2"})
    if a.marcar_vistas and nuevas:
        e.setdefault("integraciones", {}).setdefault("bmad", {})["propuestas_vistas"] = sorted(visto | set(nuevas)); guardar_estado(a.proyecto, e)
    if a.json: print(json.dumps(hallazgos, ensure_ascii=False, indent=2)); return
    if not hallazgos: print("Sin desvíos: la especificación coincide con las líneas base registradas."); return
    for h in hallazgos:
        print(f"- [{h['tipo']}] {h['artefacto']}: {h['detalle']}" + (f" · agregados {h['ids_agregados']} · retirados {h['ids_retirados']}" if h["tipo"] == "desvio" else ""))

# ------------------------------------------------------------------ índice de especificación (contrato pm-spec-index/1)
GOBIERNO = ["prioridad", "moscow", "estimacion", "iteracion", "release", "producto_pbs"]

def leer_wbs_refs(proyecto):
    refs = {}
    p = os.path.join(proyecto, "02-planificacion", "wbs.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            for i in re.split(r"[;, ]+", r.get("ref") or ""):
                m = IDS.match(i.strip())
                if m: refs.setdefault(norm_id(m.group(1), m.group(2)), []).append(r["codigo"])
                elif re.match(r"^\d+-\d+-", i.strip()): refs.setdefault(i.strip(), []).append(r["codigo"])
    return refs

def cobertura(tipo, estados):
    """Valores comunes del contrato pm-spec-index/1: sin-cobertura | planificado | en-curso | terminado | n/a."""
    if not estados: return "sin-cobertura" if tipo in ("FR", "REQ") else "n/a"
    if all(x in ("done", "terminado", "hecho") for x in estados): return "terminado"
    if any(x not in ("backlog", "ready-for-dev", "pendiente", "") for x in estados): return "en-curso"
    return "planificado"

def construir_indice(proyecto, e=None, raiz=None):
    """Vista normalizada BMAD (especificación) + pm-method (gobierno). Es un caché derivado, no una fuente."""
    e = e or cargar_estado(proyecto)
    b = detectar_bmad(proyecto, raiz, e); arts = inventario(b); reqs = requisitos(b, arts); hs = historias(b, arts)
    gob = {}
    pb = os.path.join(proyecto, "02-planificacion", "backlog.csv")
    if os.path.exists(pb):
        for f in csv.DictReader(open(pb, encoding="utf-8")): gob[f.get("id")] = {k: f.get(k, "") for k in GOBIERNO}
    wref = leer_wbs_refs(proyecto)
    hist = []
    for k, h in sorted(hs.items(), key=lambda kv: orden_num(kv[1]["numero"])):
        hist.append({"id": k, "numero": h["numero"], "epica": f"E-{h['epica']}", "titulo": h["titulo"], "estado": h["estado"],
                     "refs": sorted(h["refs"]), "refs_epica": sorted(h.get("refs_epica", set())), "archivo": h.get("archivo", ""),
                     "estado_archivo": h.get("estado_archivo", ""), "paquetes_wbs": wref.get(k, []), "gobierno": gob.get(k, {})})
    epicas = {}
    for h in hist:
        ep = epicas.setdefault(h["epica"], {"id": h["epica"], "historias": [], "estados": []}); ep["historias"].append(h["id"]); ep["estados"].append(h["estado"])
    if "epicas" in arts:
        for r in arts["epicas"]["rutas"]:
            for linea in open(r, encoding="utf-8", errors="replace"):
                m = EPIC_H.match(linea)
                if m: epicas.setdefault(f"E-{m.group(1)}", {"id": f"E-{m.group(1)}", "historias": [], "estados": []})["titulo"] = m.group(2).strip()
    rep_ = refs_epicas(arts) if b["layout"] == "v6" else {}
    for ep in epicas.values():
        st = ep.pop("estados"); ep["estado"] = "done" if st and all(x == "done" for x in st) else ("in-progress" if any(x in ("in-progress", "review", "done") for x in st) else "backlog")
        ep["refs"] = sorted(rep_.get(ep["id"][2:], set()))
    reqs_out = []
    for q in reqs:
        hh, nivel = historias_de(q["id"], hs)
        est = [hs[k]["estado"] for k in hh]
        cob = cobertura(q["tipo"], est)
        if cob == "sin-cobertura" and wref.get(q["id"]): cob = "planificado"   # cubierto por un paquete de la WBS aunque aún no haya historia
        reqs_out.append({**q, "historias": hh, "nivel_traza": nivel, "epicas": sorted({f"E-{hs[k]['epica']}" for k in hh}, key=lambda x: int(x[2:])),
                         "paquetes_wbs": wref.get(q["id"], []), "cobertura": cob})
    lb = {k: {"version": v.get("version"), "sha256": v.get("sha256")} for k, v in e.get("artefactos", {}).items() if v.get("externo") == "bmad"}
    huella = hashlib.sha256(json.dumps({k: v["sha256"] for k, v in arts.items()}, sort_keys=True).encode()).hexdigest()
    return {"esquema": "pm-spec-index/1", "generado": datetime.datetime.now().isoformat(timespec="seconds"), "proveedor": "bmad",
            "fuente": {"layout": b["layout"], "version": b.get("version", ""), "version_fuente": b.get("version_fuente", ""), "soporte": b["soporte"], "raiz": b["raiz"]},
            "huella_fuentes": huella,
            "artefactos": {k: {"rutas": [os.path.relpath(r, b["raiz"]) for r in v["rutas"]], "sha256": v["sha256"], "estado": v["estado_bmad"]} for k, v in arts.items()},
            "lineas_base": lb,
            "dueños": {"requisitos, épicas, historias, estado de desarrollo": "BMAD (solo lectura)",
                       "gobierno (prioridad, moscow, estimacion, iteracion, release, producto_pbs)": "pm-method backlog.csv",
                       "paquetes_wbs": "pm-method wbs.csv (columna ref)"},
            "requisitos": reqs_out, "epicas": sorted(epicas.values(), key=lambda x: int(x["id"][2:])), "historias": hist,
            "resumen": {"requisitos": len(reqs_out), "sin_cobertura": [r["id"] for r in reqs_out if r["cobertura"] == "sin-cobertura"],
                        "historias": len(hist), "por_estado": {s_: sum(1 for h in hist if h["estado"] == s_) for s_ in ["backlog", "ready-for-dev", "in-progress", "review", "done"]}}}

def huella_actual(proyecto, e=None, raiz=None):
    e = e or cargar_estado(proyecto)
    b = detectar_bmad(proyecto, raiz, e); arts = inventario(b)
    return hashlib.sha256(json.dumps({k: v["sha256"] for k, v in arts.items()}, sort_keys=True).encode()).hexdigest()

def cmd_indice(a, e):
    idx = construir_indice(a.proyecto, e, a.raiz)
    out = salida(a.proyecto, "02-planificacion", "especificacion", "spec-index.json")
    escribir_texto(out, json.dumps(idx, ensure_ascii=False, indent=2))
    r = idx["resumen"]; print(f"Índice de especificación (BMAD {idx['fuente']['layout']}): {r['requisitos']} ids, {r['historias']} historias, sin cobertura {r['sin_cobertura'] or 'ninguno'} → {os.path.relpath(out)}")

# ------------------------------------------------------------------ sentido inverso: decisiones de gobierno → BMAD
def cmd_handoff(a, e):
    """Genera el documento de traspaso para que el equipo BMAD aplique, con sus propios flujos, una decisión de gobierno."""
    b = detectar_bmad(a.proyecto, a.raiz, e)
    cambio = None
    if a.cambio:
        pc = os.path.join(a.proyecto, "03-control", "registros", "cambios.csv")
        for f in (csv.DictReader(open(pc, encoding="utf-8")) if os.path.exists(pc) else []):
            if f.get("id") == a.cambio: cambio = f
        if not cambio: sys.exit(f"No existe {a.cambio} en cambios.csv")
        if (cambio.get("decision") or "") != "aprobado": sys.exit(f"{a.cambio} no está aprobado (decision={cambio.get('decision') or 'vacía'}): solo se traspasan decisiones tomadas")
    hist = []
    pb = os.path.join(a.proyecto, "02-planificacion", "backlog.csv")
    if os.path.exists(pb): hist = [f for f in csv.DictReader(open(pb, encoding="utf-8")) if f.get("origen") == "bmad"]
    orden = {"must": 0, "should": 1, "could": 2, "wont": 3, "won't": 3}
    prios = sorted([h for h in hist if h.get("moscow")], key=lambda h: (orden.get(h["moscow"].lower(), 9), h.get("release", ""), h["id"]))
    ultimo = e.get("integraciones", {}).get("bmad", {}).get("ultimo_handoff_prioridades", {})
    actual = {h["id"]: f"{h.get('moscow','')}|{h.get('release','')}|{h.get('iteracion','')}" for h in prios}
    cambios_prio = {k: v for k, v in actual.items() if ultimo.get(k) != v}
    if not cambio and not cambios_prio: print("Nada que traspasar: sin cambio aprobado indicado y sin cambios de prioridad desde el último traspaso."); return
    fecha = hoy(); base_n = f"handoff-bmad-{fecha}" + (f"-{a.cambio}" if a.cambio else "-prioridades")
    out = salida(a.proyecto, "02-planificacion", "especificacion", base_n + ".md"); n = 2
    while os.path.exists(out): out = salida(a.proyecto, "02-planificacion", "especificacion", f"{base_n}-{n}.md"); n += 1
    proteger(out, b)
    L = ["---", "tipo: handoff-bmad", f"fecha: {fecha}", "estado: emitido", f'cambio: "{a.cambio or ""}"', "---", "",
         "# Traspaso de decisiones de gobierno al equipo BMAD · Governance handoff to BMAD", "",
         "> Lo aplica el equipo de especificación con los flujos de BMAD (actualización del PRD, corrección de rumbo, planificación del sprint).",
         "> pm-method no edita archivos de BMAD. Después: `bmad.py verificar` y, si corresponde, nueva línea base por pm-director.", ""]
    sec = 0
    if cambio:
        sec += 1
        L += [f"## {sec}. Cambio aprobado {cambio['id']} · {cambio.get('titulo','')}", "",
              f"- **Decidido por / Decided by:** {cambio.get('decidido_por','')} · {cambio.get('fecha_decision','')}",
              f"- **Descripción / Description:** {cambio.get('descripcion','')}",
              f"- **Impacto en alcance / Scope impact:** {cambio.get('impacto_alcance','')}",
              f"- **Ids afectados / Affected ids:** {cambio.get('notas','') or '[por confirmar]'}", "",
              "**Acciones esperadas en BMAD / Expected BMAD actions:**",
              "- [ ] Actualizar el PRD con ids estables (no renumerar ni reutilizar ids retirados).",
              "- [ ] Si afecta épicas/historias en curso: flujo de corrección de rumbo de BMAD y ajuste de la planificación del sprint.",
              "- [ ] Avisar al gestor para `bmad.py verificar` y línea base nueva (versión mayor).", ""]
    if cambios_prio:
        sec += 1
        L += [f"## {sec}. Prioridades de gobierno vigentes (MoSCoW, release, iteración) · Governance priorities", "",
              "Insumo para la planificación del sprint de BMAD; el orden dentro de cada grupo lo decide el product owner.", "",
              "| Historia | MoSCoW | Release | Iteración | Cambió |", "|---|---|---|---|---|"]
        for h in prios:
            L.append(f"| {h['id']} | {h.get('moscow','')} | {h.get('release','')} | {h.get('iteracion','')} | {'sí' if h['id'] in cambios_prio else ''} |")
        L.append("")
    sec += 1
    L += [f"## {sec}. Confirmación del equipo BMAD · Confirmation", "", "- Aplicado por / Applied by: {{nombre}} · fecha: {{fecha}}", "- Artefactos BMAD actualizados / Updated artifacts: {{rutas}}", ""]
    open(out, "w", encoding="utf-8").write("\n".join(L))
    e.setdefault("integraciones", {}).setdefault("bmad", {})["ultimo_handoff_prioridades"] = actual
    e["integraciones"]["bmad"].setdefault("handoffs", []).append({"fecha": fecha, "archivo": os.path.relpath(out, a.proyecto), "cambio": a.cambio or ""})
    guardar_estado(a.proyecto, e)
    print(f"Traspaso emitido → {os.path.relpath(out)} ({'cambio ' + a.cambio if a.cambio else ''}{' · ' if a.cambio and cambios_prio else ''}{str(len(cambios_prio)) + ' prioridades cambiadas' if cambios_prio else ''})")

def cmd_recorridos(a, e):
    """Detalle de los recorridos UJ-n (solo lectura; no escribe nada)."""
    b = detectar_bmad(a.proyecto, a.raiz, e); xs = recorridos(inventario(b))
    if a.id:
        q = re.sub(r"^UJ-?(\d+)$", lambda m: f"UJ-{int(m.group(1))}", a.id.strip(), flags=re.I)
        xs = [x for x in xs if x["id"] == q]
        if not xs: sys.exit(f"No se encontró {a.id} en el PRD de BMAD.")
    if a.json: print(json.dumps(xs, ensure_ascii=False, indent=2)); return
    for x in xs:
        print(f"{x['id']} {x['titulo']} ({x['fuente']}:{x['linea']})")
        for k, _ in CAMPOS_UJ:
            if x[k]: print(f"  {k}: {x[k]}")
        print(f"  FR: {', '.join(x['frs']) or '-'}" + (f" · por sección: {', '.join(x['frs_seccion'])}" if x["frs_seccion"] else "")
              + f" · KPI: {', '.join(x['kpi']) or '-'}" + (f" · contrapesos: {', '.join(x['contrapesos'])}" if x["contrapesos"] else ""))

def cmd_capacidades(a, e):
    """Mapa de capacidades, decisiones diferidas y stack de la arquitectura (solo lectura; no escribe nada)."""
    b = detectar_bmad(a.proyecto, a.raiz, e); d = capacidades(inventario(b))
    if a.json: print(json.dumps(d, ensure_ascii=False, indent=2)); return
    for c in d["capacidades"]: print(f"capacidad {c['capacidad']} · {', '.join(c['ids'])} · {c['modulo']} · {', '.join(c['ad'])} ({c['fuente']}:{c['linea']})")
    for x in d["diferidas"]: print(f"diferida {x['tema']} ({x['fuente']}:{x['linea']})")
    for x in d["stack"]: print(f"stack {x['nombre']} {x['version']}")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", required=True); ap.add_argument("--raiz")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("detectar")
    i = sub.add_parser("inventario"); i.add_argument("--json", action="store_true")
    sub.add_parser("requisitos")
    t = sub.add_parser("trazabilidad"); t.add_argument("--wbs")
    sub.add_parser("backlog")
    av = sub.add_parser("avance"); av.add_argument("--json", action="store_true"); av.add_argument("--corte", help="fecha de corte AAAA-MM-DD (defecto hoy); una fila por fecha")
    lb = sub.add_parser("linea-base"); lb.add_argument("artefacto", choices=list(CLAVES_LB)); lb.add_argument("--version", required=True); lb.add_argument("--por", required=True)
    lb.add_argument("--fecha", help="fecha de la decisión AAAA-MM-DD (defecto hoy)"); lb.add_argument("--nivel", default="junta", choices=["junta", "capa-negocio", "autoridad-cambio", "gestor", "product-owner"])
    sub.add_parser("indice")
    ho = sub.add_parser("handoff"); ho.add_argument("--cambio", help="id C-### aprobado en cambios.csv")
    v = sub.add_parser("verificar"); v.add_argument("--json", action="store_true"); v.add_argument("--marcar-vistas", action="store_true", dest="marcar_vistas")
    rc = sub.add_parser("recorridos"); rc.add_argument("--id", help="UJ-n (defecto: todos)"); rc.add_argument("--json", action="store_true")
    ca = sub.add_parser("capacidades"); ca.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "linea-base" and a.fecha:
        try: datetime.date.fromisoformat(a.fecha)
        except ValueError: sys.exit(f"--fecha {a.fecha}: formato AAAA-MM-DD")
    if not yaml: print("AVISO: falta PyYAML (pip install pyyaml); sin él no se leen config.yaml ni sprint-status.yaml.", file=sys.stderr)
    escribe = a.cmd not in ("recorridos", "capacidades") and not (a.cmd == "verificar" and not a.marcar_vistas)
    with (E.bloqueo(a.proyecto) if E and escribe else contextlib.nullcontext()):   # estado.json, backlog y derivados
        ejecutar(a)

def ejecutar(a):
    e = cargar_estado(a.proyecto)
    {"detectar": cmd_detectar, "inventario": cmd_inventario, "requisitos": cmd_requisitos, "trazabilidad": cmd_trazabilidad,
     "backlog": cmd_backlog, "avance": cmd_avance, "linea-base": cmd_linea_base, "verificar": cmd_verificar,
     "indice": cmd_indice, "handoff": cmd_handoff, "recorridos": cmd_recorridos, "capacidades": cmd_capacidades}[a.cmd](a, e)

if __name__ == "__main__":
    main()
