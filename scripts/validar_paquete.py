#!/usr/bin/env python3
"""Valida la estructura del paquete pm-method.
Validates the pm-method package structure.

Uso / Usage: python3 scripts/validar_paquete.py [--estricto]
Comprueba: frontmatter YAML parseable, name == carpeta, description <= 200 caracteres,
encabezados obligatorios en orden, referencias a skills existentes, plantillas con frontmatter, que todo el Python
compile y que la sintaxis sea compatible con Python 3.9 (la versión mínima): con un intérprete 3.9 si hay uno
(variable PM_PYTHON39, `python3.9` en el PATH o `uv python find 3.9`) y, si no, con un análisis propio de las
f-strings que solo compilan desde 3.12 (barra invertida, comillas iguales anidadas o comentarios en la expresión).
"""
import io, json, os, re, shutil, subprocess, sys, glob, tokenize

LISTADO = []   # largos de description de skills invocables por el modelo (presupuesto del listado)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENCABEZADOS = ["## Cuándo usar", "## Idioma", "## Conocimiento", "## Entradas requeridas", "## Procedimiento",
               "## Reglas del método", "## Artefactos y plantillas", "## Calidad", "## Escalamiento y excepciones",
               "## Ejemplos de invocación", "## EN summary"]

def frontmatter(txt):
    if not txt.startswith("---"): return None, txt
    partes = txt.split("---", 2)
    if len(partes) < 3: return None, txt
    return partes[1], partes[2]

def campo(fm, nombre):
    m = re.search(rf"^{nombre}:\s*(.+)$", fm, re.M)
    if not m: return None
    v = m.group(1).strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")): v = v[1:-1]
    return v

def fstrings_39(src):
    """(línea, problema) de las f-strings que Python 3.9–3.11 no compila y 3.12+ sí (PEP 701). Solo hace falta cuando
    el intérprete es 3.12 o posterior: en 3.9–3.11 esos casos ya fallan al compilar."""
    if not hasattr(tokenize, "FSTRING_START"): return []
    def comilla(s):
        s = s.lstrip("rRbBuUfF")
        return s[:3] if s[:3] in ('"""', "'''") else s[:1]
    try: toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, SyntaxError): return []
    out, pila = set(), []   # pila: comillas de las f-strings abiertas
    for t in toks:
        if pila:
            if t.type == tokenize.COMMENT: out.add((t.start[0], "comentario dentro de la expresión de un f-string"))
            if "\\" in t.string and (t.type == tokenize.STRING or (t.type == tokenize.FSTRING_MIDDLE and len(pila) > 1)):
                out.add((t.start[0], "barra invertida dentro de la expresión de un f-string"))
            if t.type in (tokenize.STRING, tokenize.FSTRING_START):
                q = comilla(t.string)
                if any(q.startswith(p) if len(p) == 1 else q == p for p in pila):
                    out.add((t.start[0], "comillas iguales a las del f-string que las contiene"))
        if t.type == tokenize.FSTRING_START: pila.append(comilla(t.string))
        elif t.type == tokenize.FSTRING_END and pila: pila.pop()
    return sorted(out)

def interprete_39():
    """Ruta de un Python 3.9 instalado (no descarga nada), o None."""
    cands = [os.environ.get("PM_PYTHON39"), shutil.which("python3.9")]
    if shutil.which("uv"):
        try: cands.append(subprocess.run(["uv", "python", "find", "3.9"], capture_output=True, text=True, timeout=30).stdout.strip())
        except (OSError, subprocess.SubprocessError): pass
    for c in cands:
        if not c or not os.path.exists(c): continue
        try:
            v = subprocess.run([c, "-c", "import sys; print(sys.version_info[:2] == (3, 9))"], capture_output=True, text=True, timeout=30).stdout.strip()
        except (OSError, subprocess.SubprocessError): continue
        if v == "True": return c
    return None

ANALIZAR_39 = """import ast, json, sys
out = []
for p in json.load(sys.stdin):
    try: ast.parse(open(p, encoding="utf-8").read(), p)
    except SyntaxError as ex: out.append([p, ex.lineno, ex.msg])
print(json.dumps(out))"""

def compat_39(archivos):
    """Errores de sintaxis en Python 3.9 y el método usado."""
    py39 = sys.executable if sys.version_info[:2] == (3, 9) else interprete_39()
    if py39:
        r = subprocess.run([py39, "-I", "-c", ANALIZAR_39], input=json.dumps(archivos), capture_output=True, text=True, timeout=300)
        try: return [f"{os.path.relpath(p, RAIZ)}:{n}: {m}" for p, n, m in json.loads(r.stdout)], f"intérprete {py39}"
        except ValueError: return [f"no se pudo analizar con {py39}: {r.stderr[-300:]}"], f"intérprete {py39}"
    errs = []
    for p in archivos:
        for n, m in fstrings_39(open(p, encoding="utf-8").read()):
            errs.append(f"{os.path.relpath(p, RAIZ)}:{n}: {m}")
    return errs, "análisis de f-strings (no hay un intérprete 3.9 instalado)"

def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip()); return
    estricto = "--estricto" in sys.argv
    errores, avisos = [], []
    skills = sorted(d for d in os.listdir(os.path.join(RAIZ, "skills")) if os.path.isdir(os.path.join(RAIZ, "skills", d)))
    for s in skills:
        p = os.path.join(RAIZ, "skills", s, "SKILL.md")
        if not os.path.exists(p): errores.append(f"{s}: falta SKILL.md"); continue
        txt = open(p, encoding="utf-8").read()
        fm, cuerpo = frontmatter(txt)
        if fm is None: errores.append(f"{s}: sin frontmatter"); continue
        try:
            import yaml  # opcional
            yaml.safe_load(fm)
        except ImportError:
            pass
        except Exception as e:
            errores.append(f"{s}: frontmatter YAML inválido ({e.__class__.__name__})")
        n = campo(fm, "name"); d = campo(fm, "description")
        if n != s: errores.append(f"{s}: name '{n}' no coincide con la carpeta")
        if not d: errores.append(f"{s}: falta description")
        elif len(d) > 240: errores.append(f"{s}: description de {len(d)} caracteres (>240)")
        else:
            comando = re.search(r"^disable-model-invocation:\s*true", fm, re.M) is not None
            if not comando:
                LISTADO.append(len(d))
                if "Usar:" not in d or "No:" not in d: errores.append(f"{s}: description sin 'Usar:' y 'No:' (SPEC 1.3)")
        pos = -1
        for h in ENCABEZADOS:
            i = cuerpo.find(h)
            if i < 0: errores.append(f"{s}: falta encabezado '{h}'")
            elif i < pos: errores.append(f"{s}: encabezado fuera de orden '{h}'")
            else: pos = i
        lineas = txt.count("\n"); chars = len(txt.encode("utf-8"))
        if chars > 12500 or lineas > 200: errores.append(f"{s}: SKILL.md excede la carga progresiva ({chars} bytes, {lineas} líneas; máx. ≈12 000 / 200)")
        # referencias a archivos: templates/, scripts/, references/ (propias o de otra skill con prefijo pm-x/)
        for m in re.finditer(r"(?:<?(pm-[a-z0-9-]+)>?/)?((?:templates|scripts|references)/[A-Za-z0-9_.\-]+\.(?:md|py|csv|html))", txt):
            dueño = m.group(1) or s
            if dueño not in skills: continue
            if not os.path.exists(os.path.join(RAIZ, "skills", dueño, m.group(2))):
                errores.append(f"{s}: referencia rota {dueño}/{m.group(2)}")
        for ref in set(re.findall(r"`(pm-[a-z0-9-]+)`", txt)):
            if ref not in skills and not os.path.exists(os.path.join(RAIZ, "agents", ref + ".md")):
                avisos.append(f"{s}: referencia a '{ref}' que no existe como skill ni agente")
        for t in glob.glob(os.path.join(RAIZ, "skills", s, "templates", "*.md")):
            tt = open(t, encoding="utf-8").read()
            if not tt.startswith("---"):
                avisos.append(f"{s}: plantilla sin frontmatter {os.path.basename(t)}")
            elif re.search(r"(?m)^idioma:\s*(es|en)\s*$", tt.split("---", 2)[1]):
                avisos.append(f"{s}: plantilla con idioma fijo {os.path.basename(t)} (usar \"{{{{idioma}}}}\")")
    for a in sorted(glob.glob(os.path.join(RAIZ, "agents", "*.md")) + glob.glob(os.path.join(RAIZ, "commands", "*.md"))):
        ta = open(a, encoding="utf-8").read()
        for ref in set(re.findall(r"`(pm-[a-z0-9-]+)`", ta)):
            if ref not in skills and not os.path.exists(os.path.join(RAIZ, "agents", ref + ".md")):
                errores.append(f"{os.path.basename(a)}: referencia a '{ref}' inexistente")
        if "README" in ta and not os.path.exists(os.path.join(RAIZ, "README.md")):
            errores.append(f"{os.path.basename(a)}: menciona README.md pero no existe")
        if "/commands/" in a: continue
        fm, _ = frontmatter(ta)
        if fm and re.search(r"^tools:", fm, re.M): errores.append(f"agente {os.path.basename(a)}: declara 'tools' (debe heredar, SPEC 1.11)")
        if fm and "pm-orquestador" not in a and not re.search(r"^disallowedTools:.*Agent", fm, re.M):
            errores.append(f"agente {os.path.basename(a)}: falta 'disallowedTools: Agent' (SPEC 1.11)")
        if fm is None or not campo(fm, "name") or not campo(fm, "description"):
            errores.append(f"agente {os.path.basename(a)}: frontmatter incompleto")
    # orquestación: toda skill invocable por el modelo es alcanzable desde el orquestador; metadata.agente válido
    orq = open(os.path.join(RAIZ, "skills", "pm-orquestador", "SKILL.md"), encoding="utf-8").read()
    agentes = {os.path.basename(x)[:-3] for x in glob.glob(os.path.join(RAIZ, "agents", "*.md"))}
    for s in skills:
        t = open(os.path.join(RAIZ, "skills", s, "SKILL.md"), encoding="utf-8").read()
        comando = re.search(r"^disable-model-invocation:\s*true", t, re.M) is not None
        if not comando and s != "pm-orquestador" and s not in orq: errores.append(f"orquestación: {s} no figura en la tabla de enrutamiento de pm-orquestador")
        m = re.search(r"^\s+agente:\s*([\w-]+)", t, re.M)
        if m and m.group(1) not in agentes: errores.append(f"{s}: metadata agente '{m.group(1)}' no existe")
    # hooks, versiones y scripts
    hj = os.path.join(RAIZ, "hooks", "hooks.json")
    if os.path.exists(hj):
        import json as _j
        try:
            hd = _j.load(open(hj, encoding="utf-8"))
            for ev, grupos in hd.get("hooks", {}).items():
                for g in grupos:
                    for h in g.get("hooks", []):
                        for sc in re.findall(r"hooks/[\w.]+\.py", h.get("command", "")):
                            if not os.path.exists(os.path.join(RAIZ, sc)): errores.append(f"hooks.json ({ev}) referencia {sc}, que no existe")
        except Exception as ex: errores.append(f"hooks.json inválido: {ex}")
    try:
        import json as _j
        vp = _j.load(open(os.path.join(RAIZ, ".claude-plugin", "plugin.json"), encoding="utf-8")).get("version")
        vc = _j.load(open(os.path.join(RAIZ, "compatibilidad.json"), encoding="utf-8")).get("version")
        ve = re.search(r'VERSION_PAQUETE = "([^"]+)"', open(os.path.join(RAIZ, "skills", "pm-estado-proyecto", "scripts", "esquema.py"), encoding="utf-8").read()).group(1)
        if len({vp, vc, ve}) != 1: errores.append(f"versiones desalineadas: plugin.json {vp}, compatibilidad.json {vc}, esquema.py {ve}")
    except Exception as ex: errores.append(f"no se pudo verificar versiones: {ex}")
    import py_compile
    pys = [py for py in glob.glob(os.path.join(RAIZ, "**", "*.py"), recursive=True) if "/fixtures/" not in py and "/node_modules/" not in py]
    for py in pys:
        try: py_compile.compile(py, doraise=True)
        except Exception as ex: errores.append(f"script no compila: {os.path.relpath(py, RAIZ)} ({ex.__class__.__name__})")
    errs39, metodo39 = compat_39(pys)
    errores += [f"sintaxis incompatible con Python 3.9: {x}" for x in errs39]
    tot = sum(LISTADO)
    if tot > 7500: errores.append(f"listado de descriptions = {tot} caracteres (>7 500, SPEC 1.3)")
    print(f"Skills: {len(skills)} ({len(LISTADO)} invocables por el modelo, listado {tot} caracteres) · Agentes: {len(glob.glob(os.path.join(RAIZ, 'agents', '*.md')))}")
    print(f"Python 3.9: {len(pys)} archivos .py verificados con {metodo39}")
    for e in errores: print("ERROR ", e)
    for w in avisos: print("AVISO ", w)
    if errores or (estricto and avisos): sys.exit(1)
    print("OK")

if __name__ == "__main__":
    main()
