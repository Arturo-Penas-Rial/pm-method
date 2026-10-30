"""Nivel «hermes» de la suite de variantes: el entorno Hermes Agent sin instalar Hermes (informe de cobertura H-02).

scripts/instalar_hermes.py contra un destino temporal, dos veces (idempotente), y comparación con el entorno Claude Code
(plugin): mismas skills, ninguna variable ${CLAUDE_…} sin reemplazar, toda ruta a un script o archivo citada en las
skills y en los agentes existe en la copia (en el plugin, las mismas rutas existen bajo la raíz del repositorio),
descripciones dentro de los límites, agentes como personas en _agentes/ (docs/INSTALACION.md §3.2; INSTALACION-WSL2
§7.3–7.4), sin hooks, destino ajeno rechazado, --verificar sin escribir nada, y los scripts corren desde la copia
instalada con las rutas que muestran las guías de Hermes (nuevo_proyecto.py, estado.py contexto|radar, registro.py,
sanidad.py, bmad.py y envios.py, que importa interesados.py de la skill vecina).
"""
import glob, hashlib, os, re, shutil, subprocess
from comun import FIX, RAIZ, Ejecutor, escribir

INSTALADOR = os.path.join(RAIZ, "scripts", "instalar_hermes.py")
LIMITE_DESCRIPCION = 1024   # especificación Agent Skills (agentskills.io), la que Hermes declara seguir [verificar en Hermes]


def huellas(raiz):
    out = {}
    for d, _, fs in os.walk(raiz):
        for f in fs:
            p = os.path.join(d, f)
            with open(p, "rb") as fh: out[os.path.relpath(p, raiz)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def frontmatter(p):
    t = open(p, encoding="utf-8").read()
    if not t.startswith("---"): return {}
    fm = t.split("---", 2)[1]
    return {k: v.strip().strip('"').strip("'") for k, v in re.findall(r"^([a-z-]+):\s*(.*)$", fm, re.M)}


def rutas_citadas(texto, base_skill, raiz_inst):
    """Rutas a archivos citadas con ${HERMES_SKILL_DIR}/… o con la raíz absoluta de la instalación."""
    out = []
    for m in re.finditer(r"\$\{HERMES_SKILL_DIR\}/([^\s`'\")|,;]+)", texto):
        out.append(os.path.normpath(os.path.join(base_skill, m.group(1).rstrip(".:…"))))
    for m in re.finditer(re.escape(raiz_inst) + r"/([^\s`'\")|,;]+)", texto):
        out.append(os.path.normpath(os.path.join(raiz_inst, m.group(1).rstrip(".:…"))))
    # solo archivos concretos (no plantillas con <…>, comodines ni carpetas genéricas)
    return [p for p in out if re.search(r"\.(py|md|csv|html|json|js|txt)$", p) and not re.search(r"[<>*…{}]", p)]


def correr(base, reg, py):
    x = Ejecutor(reg, py, cwd=base)
    skills = sorted(d for d in os.listdir(os.path.join(RAIZ, "skills")) if os.path.isfile(os.path.join(RAIZ, "skills", d, "SKILL.md")))
    agentes = sorted(os.listdir(os.path.join(RAIZ, "agents")))
    dest = os.path.join(base, "hermes", "skills", "pm-method")

    v = x(INSTALADOR, "--destino", dest, "--verificar", paso="instalar_hermes --verificar")
    reg.check(f"--verificar informa {len(skills)} skills y {len(agentes)} agentes y no escribe nada",
              f"{len(skills)} skills y {len(agentes)} agentes" in v.out and not os.path.exists(dest), v.out[-200:])
    i1 = x(INSTALADOR, "--destino", dest, paso="instalar_hermes (1.ª vez)")
    h1 = huellas(dest)
    i2 = x(INSTALADOR, "--destino", dest, paso="instalar_hermes (2.ª vez)")
    h2 = huellas(dest)
    reg.check("instalación idempotente: la segunda corrida termina OK y deja exactamente los mismos archivos", i1.rc == 0 and i2.rc == 0 and h1 == h2 and h1,
              sorted(set(h1) ^ set(h2))[:5])
    inst = sorted(d for d in os.listdir(dest) if os.path.isfile(os.path.join(dest, d, "SKILL.md")))
    reg.check(f"todas las skills presentes ({len(skills)}), como carpetas <destino>/<skill>/ con SKILL.md (Hermes: /<skill>)", inst == skills,
              sorted(set(inst) ^ set(skills)))
    reg.check("sin hooks (Hermes no ejecuta hooks de Claude Code) y con la marca .pm-method",
              not os.path.exists(os.path.join(dest, "hooks")) and os.path.isfile(os.path.join(dest, ".pm-method")))
    textos = {}
    for d, _, fs in os.walk(dest):
        for f in fs:
            p = os.path.join(d, f)
            try: textos[p] = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError): pass
    restos = sorted(os.path.relpath(p, dest) for p, t in textos.items() if "${CLAUDE_" in t and p.endswith((".md", ".txt", ".yaml", ".yml", ".json")))
    reg.check("ninguna variable ${CLAUDE_…} sin reemplazar en SKILL.md, references, plantillas ni agentes", not restos, restos[:5])
    rotas, vistas = [], 0
    for p, t in textos.items():
        if not p.endswith(".md"): continue
        rel = os.path.relpath(p, dest); skill_dir = os.path.join(dest, rel.split(os.sep)[0])
        for r in rutas_citadas(t, skill_dir, dest.replace("\\", "/")):
            vistas += 1
            if not os.path.exists(r): rotas.append(f"{rel} → {os.path.relpath(r, dest)}")
    rotas = sorted(set(rotas))
    reg.check(f"rutas a scripts y archivos citadas en la copia ({vistas}) existen (antes: ${{CLAUDE_PLUGIN_ROOT}}/skills/… → <destino>/skills/…, inexistente)",
              not rotas and vistas > 50, rotas[:8])
    malas = []
    for s in inst:
        fm = frontmatter(os.path.join(dest, s, "SKILL.md"))
        if fm.get("name") != s: malas.append(f"{s}: name «{fm.get('name')}»")
        if not fm.get("description") or len(fm["description"]) > min(240, LIMITE_DESCRIPCION): malas.append(f"{s}: description de {len(fm.get('description', ''))} caracteres")
    reg.check("frontmatter de cada skill: name = carpeta y description ≤ 240 caracteres (regla del paquete; Agent Skills admite 1024)", not malas, malas[:5])
    ag = os.path.join(dest, "_agentes")
    copia_ag = sorted(os.listdir(ag)) if os.path.isdir(ag) else []
    orq = open(os.path.join(ag, "pm-orquestador.md"), encoding="utf-8").read() if "pm-orquestador.md" in copia_ag else ""
    citadas = set(re.findall(r"`(pm-[a-z0-9-]+)`", orq))
    faltan = sorted(c for c in citadas if c not in inst and c + ".md" not in copia_ag)
    reg.check("agentes como personas en _agentes/ (6, sin SKILL.md: Hermes no los indexa); el orquestador solo nombra skills y agentes que existen en la copia",
              copia_ag == agentes and not glob.glob(os.path.join(ag, "*", "SKILL.md")) and orq and not faltan, f"{copia_ag} · faltan {faltan}")
    ajeno = os.path.join(base, "ajeno"); os.makedirs(ajeno, exist_ok=True); escribir(os.path.join(ajeno, "mio.txt"), "no tocar\n")
    r = x(INSTALADOR, "--destino", ajeno, ok=(1,), paso="instalar_hermes en un destino ajeno")
    reg.check("destino ajeno (sin la marca .pm-method) rechazado con mensaje y sin tocar nada",
              r.rc != 0 and "no fue creado por este script" in r.todo and os.listdir(ajeno) == ["mio.txt"], r.todo[-200:])

    # scripts desde la copia instalada (rutas de INSTALACION-WSL2 §7.4)
    repo = os.path.join(base, "proyecto-hermes"); shutil.copytree(os.path.join(FIX, "bmad-v6.12-real"), repo)
    sc = lambda skill, script: os.path.join(dest, skill, "scripts", script)
    y = Ejecutor(reg, py, cwd=repo)
    y(sc("pm-estado-proyecto", "nuevo_proyecto.py"), "--ruta", "gestion", "--nombre", "Portal", "--ejecutivo", "Laura Méndez", "--gestor", "Martín Suárez", "--fecha", "2026-10-01",
      paso="Hermes: nuevo_proyecto.py")
    y(sc("pm-bmad-puente", "bmad.py"), "--proyecto", "gestion", "detectar", paso="Hermes: bmad.py detectar")
    y(sc("pm-estado-proyecto", "registro.py"), "--proyecto", "gestion", "agregar", "riesgos", "--campo", "evento=Demora del proveedor", "--campo", "tipo=amenaza",
      paso="Hermes: registro.py agregar")
    y(sc("pm-estado-proyecto", "registro.py"), "--proyecto", "gestion", "agregar", "stakeholders", "--campo", "nombre=Laura Méndez", "--campo", "correo=laura@example.org",
      paso="Hermes: registro.py agregar stakeholders")
    cx = y(sc("pm-estado-proyecto", "estado.py"), "--proyecto", "gestion", "contexto", "--corte", "2026-10-29", paso="Hermes: estado.py contexto")
    ra = y(sc("pm-estado-proyecto", "estado.py"), "--proyecto", "gestion", "radar", "--corte", "2026-10-29", paso="Hermes: estado.py radar")
    sa = y(sc("pm-estado-proyecto", "sanidad.py"), "--proyecto", "gestion", "--json", ok=(0, 1), paso="Hermes: sanidad.py")
    ev = y(sc("pm-integraciones", "envios.py"), "--proyecto", "gestion", "historial", paso="Hermes: envios.py historial (importa interesados.py)")
    reg.check("Hermes: los scripts corren desde la copia instalada (contexto con el riesgo abierto, radar, sanidad en JSON, envios.py importa la skill vecina)",
              re.search(r"riesgos 1\b|risks 1\b", cx.out) and ra.rc == 0 and sa.json() is not None and ev.rc == 0, (cx.out + ra.out)[-300:])
    ins = (sa.json() or {}).get("hallazgos", [])
    reg.check("Hermes: la sanidad no confunde la copia de Hermes con una instalación rota (sin INS de ERROR)",
              not [h for h in ins if h["codigo"].startswith("INS") and h["severidad"] == "ERROR"], [h["codigo"] for h in ins if h["codigo"].startswith("INS")])

    # contraste con Claude Code (plugin): mismas rutas relativas bajo la raíz del repositorio
    divergencias = []
    for p, t in textos.items():
        if not p.endswith(".md") or "/_agentes/" in p: continue
        rel = os.path.relpath(p, dest); orig = os.path.join(RAIZ, "skills", rel)
        if not os.path.exists(orig): divergencias.append(f"{rel}: no existe en el plugin"); continue
        to = open(orig, encoding="utf-8").read()
        n_cl = len(re.findall(r"\$\{CLAUDE_(?:SKILL_DIR|PLUGIN_ROOT)\}", to)); n_he = len(re.findall(r"\$\{HERMES_SKILL_DIR\}", t)) + t.count(dest.replace("\\", "/"))
        if n_cl and n_he < n_cl: divergencias.append(f"{rel}: {n_cl} rutas en el plugin y {n_he} en Hermes")
    reg.check("contraste plugin ↔ Hermes: cada SKILL.md y referencia de la copia existe en el plugin y conserva sus rutas (adaptadas)",
              not divergencias, divergencias[:5])
    if not os.path.exists(os.path.join(RAIZ, "hooks", "hooks.json")): return
    reg.notas.append("Divergencia esperada (documentada en INSTALACION-WSL2 §7.4): en Hermes no hay hooks (guardián, inicio, idioma) "
                     "ni subagentes con nombre; el resumen de inicio se pide con estado.py contexto y radar.")
