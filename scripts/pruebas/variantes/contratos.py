"""Nivel «contratos» de la suite de variantes (informe de cobertura T-01, T-02, X-01).

  T-01  Documentación ↔ CLI: cada `script.py subcomando --flag` citado en skills/**/SKILL.md, references/, agents/,
        docs/*.md (con las guías y el webinar), README.md, CLAUDE.md y AGENTS.md existe en el --help real del script
        (subcomandos de la línea «usage» —o de segundo nivel, si la cita omite el primero— y opciones del subcomando, o
        de cualquiera si la cita no nombra el subcomando; un marcador `<…>` cuenta como una palabra).
  T-03  Documentación ↔ CLI de pm-kb: cada `pm-kb subcomando --flag` citado en los mismos documentos existe en
        `pm-kb … --help` (el código de pm-kb de esta copia; la ayuda no necesita la base ni el entorno de pm-kb).
  T-02  Esquema ↔ consumidores: las claves de estado.json que leen pm-kb (RESUMEN_ESTADO), paquete.py e inicio.py
        existen en el esquema (esquema.estado_inicial, SPEC §1.6 o claves que escriben los scripts), y las columnas de
        los registros del fixture de pm-kb y las que lee paquete.py existen en esquema.REGISTROS.
  X-01  Versiones del CI: lo controla validar_paquete.py (workflow sin tags fijos desalineados y disparado por pm-kb/**,
        SPEC.md y compatibilidad.json); acá se corre y se verifica su salida.
"""
import ast, glob, json, os, re, subprocess, sys
from comun import RAIZ

LIBRERIAS = {"esquema.py", "texto.py", "vigencia.py", "escenarios.py", "comun.py", "base.py", "visuales.py"}


def scripts_cli():
    """{basename: ruta} de los scripts con CLI cuyo nombre es único en el repositorio."""
    cands = (glob.glob(os.path.join(RAIZ, "skills", "*", "scripts", "*.py")) + glob.glob(os.path.join(RAIZ, "scripts", "*.py"))
             + glob.glob(os.path.join(RAIZ, "scripts", "webinar", "*.py")))
    por = {}
    for c in cands: por.setdefault(os.path.basename(c), []).append(c)
    return {b: r[0] for b, r in por.items() if len(r) == 1 and b not in LIBRERIAS}


KB_DIR = os.path.join(RAIZ, "pm-kb")


def ayuda(py, script, *sub):
    cmd, cwd = ([py, "-m", "pmkb"], KB_DIR) if script == "pm-kb" else ([py, script], RAIZ)
    try:
        r = subprocess.run([*cmd, *sub, "--help"], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL, cwd=cwd,
                           env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    except subprocess.TimeoutExpired:
        return ""
    return r.stdout if r.returncode == 0 else ""


def interfaz(py, script):
    """{'flags': set, 'subs': {sub: {'flags', 'subs'}}} desde --help (dos niveles de subcomandos)."""
    def nivel(*sub):
        h = ayuda(py, script, *sub)
        if not re.search(r"usage:", h): return None
        usage = h.split("\n\n")[0]
        m = re.search(r"\{([a-z0-9,_-]+)\}\s*\.\.\.", usage)   # subparsers: «{a,b,…} ...» (no los choices de una opción)
        subs = {}
        if m and len(sub) < 2:
            for s in m.group(1).split(","):
                subs[s] = nivel(*sub, s) or {"flags": set(), "subs": {}, "posicionales": set()}
        pos = set()
        return {"flags": set(re.findall(r"(?<![\w-])(--[a-z][a-z0-9-]*)", h)), "subs": subs, "posicionales": pos}
    return nivel()


def citas(texto):
    """[(script, resto)] de cada mención `script.py …` en spans de código y bloques ``` del texto."""
    trozos = re.findall(r"```[^\n]*\n(.*?)```", texto, re.S)
    sin_bloques = re.sub(r"```.*?```", "", texto, flags=re.S)
    trozos += re.findall(r"`([^`\n]+)`", sin_bloques)
    out = []
    for t in trozos:
        for linea in t.splitlines():
            for m in re.finditer(r"(?<![\w-])([a-z_][a-z0-9_]*\.py)\b(.*?)(?=(?<![\w-])[a-z_][a-z0-9_]*\.py\b|$)", linea):
                resto = re.split(r"\s(?:;|&&|\|\||\||→|#)\s|\)|\]", m.group(2))[0]
                out.append((m.group(1), resto))
    return out


CMD_PMKB = r"(?<![\w.-])(?:(?<=bin/)|(?<=pm-kb/)|(?<!/))pm-kb(?=\s)"


def citas_pmkb(texto):
    """[('pm-kb', resto)] de cada orden `pm-kb …` en código del texto: el comando (también ~/.local/bin/pm-kb y el lanzador
    pm-kb/pm-kb), no la carpeta pm-kb/, pm-kb-db ni el nombre del servidor en `claude mcp add … pm-kb …`; las líneas de
    salida («pm-kb: …», «pm-kb 2.6.3: …», «pm-kb instalado.») no son órdenes."""
    trozos = re.findall(r"```[^\n]*\n(.*?)```", texto, re.S)
    trozos += re.findall(r"`([^`\n]+)`", re.sub(r"```.*?```", "", texto, flags=re.S))
    out = []
    for t in trozos:
        for linea in t.splitlines():
            for m in re.finditer(CMD_PMKB + r"(.*?)(?=" + CMD_PMKB + r"|$)", linea):
                if re.search(r"\bmcp (?:add|remove|get|test)\b|MCP server\s*$", linea[:m.start()]): continue
                resto = re.split(r"\s(?:;|&&|\|\||\||→|#)\s|\)", m.group(1).replace("[", " ").replace("]", " "))[0]
                primero = (resto.split() or [""])[0]
                if resto.strip() and not primero.endswith((":", ".")): out.append(("pm-kb", resto))
    return out


def documentos():
    pats = ["skills/*/SKILL.md", "skills/*/references/*.md", "agents/*.md", "docs/*.md", "docs/guias/*.md", "docs/webinar/*.md", "docs/webinar/*/*.md",
            "README.md", "CLAUDE.md", "AGENTS.md"]
    return sorted({p for x in pats for p in glob.glob(os.path.join(RAIZ, x))})


def t01(reg, py, pmkb=False):
    cli = {"pm-kb": "pm-kb"} if pmkb else scripts_cli()
    cache, problemas, n = {}, [], 0
    for doc in documentos():
        texto = open(doc, encoding="utf-8").read()
        for script, resto in (citas_pmkb(texto) if pmkb else citas(texto)):
            if script not in cli: continue
            if script not in cache: cache[script] = interfaz(py, cli[script])
            itf = cache[script]
            if not itf: continue
            n += 1
            toks = [x.strip(".,:;'\"") for x in re.sub(r"<[^<>]*>", "<x>", resto).split()]
            # subcomando: la primera palabra simple que no sea valor de una opción
            sub, i = None, 0
            while i < len(toks):
                tk = toks[i]
                if tk.startswith("--"):
                    i += 1 if "=" in tk or (i + 1 < len(toks) and toks[i + 1].startswith("-")) else 2; continue
                if itf["subs"] and re.fullmatch(r"[a-z][a-z0-9-]*(\|[a-z][a-z0-9-]*)*", tk):
                    alternativas = tk.split("|")
                    malas = [a for a in alternativas if a not in itf["subs"]]
                    if malas and alternativas[0] in itf["subs"]:
                        malas = []      # «resumen|consultar <id>|listar historias|epicas»: alternativas mezcladas con argumentos
                    segundo = [s for s in itf["subs"].values() if all(a in (s or {}).get("subs", {}) for a in alternativas)]
                    if malas and segundo:   # «mapas.py render»: subcomando de segundo nivel sin el primero (wardley|recorrido render)
                        malas, sub = [], segundo[0]["subs"][alternativas[0]]
                    elif malas: problemas.append(f"{os.path.relpath(doc, RAIZ)}: `{script} {tk}`: subcomando inexistente ({', '.join(sorted(itf['subs']))})")
                    else: sub = itf["subs"].get(alternativas[0])
                break
            flags = {re.sub(r"=.*$", "", x) for x in toks if re.fullmatch(r"--[a-z][a-z0-9-]*(=.*)?", x)}
            validas = set(itf["flags"])
            if sub: validas |= sub["flags"] | {f for s in sub["subs"].values() for f in s["flags"]}
            else: validas |= {f for s in itf["subs"].values() for f in s["flags"] | {g for ss in s["subs"].values() for g in ss["flags"]}}
            for f in sorted(flags - validas):
                problemas.append(f"{os.path.relpath(doc, RAIZ)}: `{script}{' ' + tk if sub else ''} … {f}`: la opción no existe en --help")
    problemas = sorted(set(problemas))
    if pmkb:
        reg.check(f"T-03 documentación ↔ CLI de pm-kb: {n} citas de `pm-kb …` en SKILL.md, references, agentes, docs/ (guías y webinar), README, CLAUDE y AGENTS; "
                  "subcomandos y opciones existen en `pm-kb … --help`", n > 0 and not problemas,
                  "\n".join(problemas[:25]) + (f"\n… ({len(problemas)} en total)" if len(problemas) > 25 else ""))
    else:
        reg.check(f"T-01 documentación ↔ CLI: {n} citas de scripts en SKILL.md, references, agentes, docs/ (guías y webinar), README, CLAUDE y AGENTS; "
                  "subcomandos y opciones existen en --help",
                  not problemas, "\n".join(problemas[:25]) + (f"\n… ({len(problemas)} en total)" if len(problemas) > 25 else ""))
    return problemas


def claves_esquema():
    sys.path.insert(0, os.path.join(RAIZ, "skills", "pm-estado-proyecto", "scripts"))
    import esquema as E
    ini = E.estado_inicial("x")
    claves = set()
    def rec(o):
        if isinstance(o, dict):
            for k, v in o.items(): claves.add(k); rec(v)
        elif isinstance(o, list):
            for v in o: rec(v)
    rec(ini)
    top = set(ini)
    spec = open(os.path.join(RAIZ, "SPEC.md"), encoding="utf-8").read()
    bloque = re.search(r"### 1\.6 estado\.json.*?```json\n(.*?)```", spec, re.S)
    if bloque:
        sp = set(re.findall(r'"([a-z_]+)":', bloque.group(1)))
        claves |= sp
        try:   # el bloque es JSON con comentarios //: sin ellos, sus claves de primer nivel
            top |= set(json.loads(re.sub(r"//[^\n]*", "", bloque.group(1))))
        except ValueError:
            top |= set(re.findall(r'^ {2}"([a-z_]+)":', bloque.group(1), re.M))
    escritas = set()
    for p in glob.glob(os.path.join(RAIZ, "skills", "*", "scripts", "*.py")):
        t = open(p, encoding="utf-8").read()
        escritas |= set(re.findall(r'\be\["([a-z_]+)"\]\s*=(?!=)', t)) | set(re.findall(r'\be\.setdefault\("([a-z_]+)"', t))
    return top | escritas, claves | escritas, E


def accesos(ruta, nombres):
    """Literales leídos con <v>.get("k") o <v>["k"] para v en nombres."""
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    out = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and isinstance(n.func.value, ast.Name) \
                and n.func.value.id in nombres and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            out.add(n.args[0].value)
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id in nombres:
            s = n.slice if not hasattr(ast, "Index") or not isinstance(n.slice, getattr(ast, "Index")) else n.slice.value
            if isinstance(s, ast.Constant) and isinstance(s.value, str): out.add(s.value)
    return out


def t02(reg):
    top, todas, E = claves_esquema()
    problemas = []
    # pm-kb: claves del resumen de estado.json
    fu = open(os.path.join(RAIZ, "pm-kb", "pmkb", "fuentes.py"), encoding="utf-8").read()
    m = re.search(r"RESUMEN_ESTADO = \(([^)]*)\)", fu)
    for k in re.findall(r'"([a-z_]+)"', m.group(1) if m else ""):
        if k not in top: problemas.append(f"pm-kb/pmkb/fuentes.py RESUMEN_ESTADO lee estado.json «{k}», que no existe en el esquema")
    # paquete.py e inicio.py: estado.json
    for ruta, nombres in ((os.path.join(RAIZ, "skills", "pm-exportar", "scripts", "paquete.py"), {"estado", "e"}),
                          (os.path.join(RAIZ, "hooks", "inicio.py"), {"e", "estado"})):
        for k in sorted(accesos(ruta, nombres) - todas):
            problemas.append(f"{os.path.relpath(ruta, RAIZ)} lee estado.json «{k}», que no existe en el esquema")
    # columnas: fixture de pm-kb (CSV escritos a mano) y filas que lee paquete.py
    cols = {r: set(d["columnas"]) for r, d in E.REGISTROS.items()}
    fx = open(os.path.join(RAIZ, "pm-kb", "pruebas", "fixture.py"), encoding="utf-8").read()
    for reg_, cab in re.findall(r'\(reg / "([a-z_]+)\.csv"\)\.write_text\(\s*"([^"\\]+)\\n', fx):
        if reg_ in cols:
            for c in cab.split(","):
                if c not in cols[reg_]: problemas.append(f"pm-kb/pruebas/fixture.py: {reg_}.csv usa la columna «{c}», que no existe en esquema.REGISTROS")
    todas_cols = set().union(*cols.values())
    pq = accesos(os.path.join(RAIZ, "skills", "pm-exportar", "scripts", "paquete.py"), {"r", "q", "c", "s", "f"})
    for k in sorted(pq - todas_cols - todas):
        problemas.append(f"skills/pm-exportar/scripts/paquete.py lee la columna «{k}» de una fila, que no existe en ningún registro")
    reg.check("T-02 esquema ↔ consumidores: claves de estado.json (pm-kb, paquete.py, inicio.py) y columnas (fixture de pm-kb, paquete.py) existen en el esquema",
              not problemas, "\n".join(problemas[:25]))
    return problemas


def x01(reg, py):
    r = subprocess.run([py, os.path.join(RAIZ, "scripts", "validar_paquete.py")], capture_output=True, text=True, timeout=600)
    ci = [l for l in r.stdout.splitlines() if "CI" in l and l.startswith(("ERROR", "AVISO"))]
    reg.check("X-01 validar_paquete.py OK, con el control de versiones y disparadores del CI (sin errores de CI)",
              r.returncode == 0 and "CI:" in r.stdout and not ci, (r.stdout + r.stderr)[-600:])


def correr(base, reg, py):
    t01(reg, py); t01(reg, py, pmkb=True); t02(reg); x01(reg, py)
