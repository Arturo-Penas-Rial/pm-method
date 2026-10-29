"""Resumen ejecutivo comercial de pm-method · extracción de datos.

Lee el repositorio pm-method (por defecto, la raíz tres niveles arriba de este archivo), cuenta lo que hay en el
momento de construir y corre las pruebas gratuitas; escribe datos.json y los diagramas que usan build_pptx.js y
build_html.py. Ninguna cifra del resumen se escribe a mano: o sale de aquí o no aparece.

Uso:
    python3 extraer.py                     # cuenta, corre las pruebas (≈ 5 min) y renderiza los diagramas
    python3 extraer.py --reusar-pruebas    # reusa el bloque "pruebas" del datos.json anterior (solo para iterar el diseño)

Variables de entorno opcionales: PM_METHOD (raíz del repositorio), MMDC (binario de mermaid-cli), PUPPETEER_CFG
(JSON de puppeteer para mmdc), FECHA (AAAA-MM-DD; por defecto, hoy).
"""
import datetime, glob, importlib.util, json, os, pathlib, re, subprocess, sys, tempfile

BASE = pathlib.Path(os.environ.get("PM_METHOD", pathlib.Path(__file__).resolve().parents[3]))
AQUI = pathlib.Path(__file__).resolve().parent
MMDC = os.environ.get("MMDC", "mmdc")
PUPPETEER = os.environ.get("PUPPETEER_CFG", "")
REUSAR = "--reusar-pruebas" in sys.argv


def leer(p):
    return (BASE / p).read_text(encoding="utf-8")


def seccion(texto, patron):
    """Bloque desde el encabezado que coincide con `patron` hasta el siguiente de nivel ≤ (ignora bloques de código)."""
    lineas = texto.split("\n")
    for i, l in enumerate(lineas):
        m = re.match(r"^(#+)\s+(.*)$", l)
        if m and re.search(patron, m.group(2)):
            nivel, dentro = len(m.group(1)), False
            for j in range(i + 1, len(lineas)):
                if lineas[j].lstrip().startswith("```"):
                    dentro = not dentro
                m2 = re.match(r"^(#+)\s", lineas[j])
                if m2 and not dentro and len(m2.group(1)) <= nivel:
                    return "\n".join(lineas[i + 1:j])
            return "\n".join(lineas[i + 1:])
    raise KeyError(f"sin sección {patron!r}")


def celdas(linea):
    s = linea.strip().strip("|")
    out, cur, code = [], "", False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"; i += 2; continue
        if ch == "`":
            code = not code
        if ch == "|" and not code:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
        i += 1
    out.append(cur.strip())
    return out


def tablas(texto):
    res, cur = [], []
    for l in texto.split("\n") + [""]:
        if l.strip().startswith("|"):
            cur.append(l)
        elif cur:
            if len(cur) >= 2:
                res.append({"cab": celdas(cur[0]), "filas": [celdas(x) for x in cur[2:]]})
            cur = []
    return res


def bloques_codigo(texto):
    return re.findall(r"```\w*\n(.*?)```", texto, flags=re.S)


def plano(s):
    """Markdown inline → texto (sin negrita, enlaces ni comillas invertidas)."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s or "")
    return re.sub(r"\*\*|`", "", s).strip()


def exige(cond, msg):
    if not cond:
        sys.exit("extraer.py: " + msg)


def frontmatter(p):
    t = pathlib.Path(p).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", t, flags=re.S)
    return m.group(1) if m else ""


def campo(fm, nombre):
    m = re.search(rf"^\s*{nombre}:\s*(.*)$", fm, flags=re.M)
    return m.group(1).strip().strip('"') if m else ""


def lista_yaml(valor):
    return [x.strip() for x in valor.strip("[]").split(",") if x.strip()]


def correr(cmd, timeout=1500):
    print("·", " ".join(str(c) for c in cmd[1:]), flush=True)
    r = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


N = json.loads((AQUI / "narrativa.json").read_text(encoding="utf-8"))
D = {"generado": datetime.datetime.now().isoformat(timespec="seconds")}

# ---------------------------------------------------------------- versión y meta
plugin = json.loads(leer(".claude-plugin/plugin.json"))
compat = json.loads(leer("compatibilidad.json"))
exige(plugin["version"] == compat["version"], "versión distinta en plugin.json y compatibilidad.json")
fecha = os.environ.get("FECHA") or datetime.date.today().isoformat()
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
f = datetime.date.fromisoformat(fecha)
D["meta"] = {"version": plugin["version"], "licencia": plugin.get("license", ""), "fecha": fecha,
             "fecha_larga": f"{f.day} de {MESES[f.month - 1]} de {f.year}"}

# ---------------------------------------------------------------- jerarquía (CLAUDE.md, "Qué es")
que_es = seccion(leer("CLAUDE.md"), r"^Qué es")
jer = []
for m in re.finditer(r"^\d+\.\s+\*\*(.+?)\*\*[^=\n]*=\s*(.+)$", que_es, flags=re.M):
    texto = m.group(2)
    jer.append({"capa": plano(m.group(1)), "rol": plano(texto).rstrip(".")})
exige(len(jer) == 4, f"se esperaban 4 capas en la jerarquía de CLAUDE.md, hay {len(jer)}")
D["jerarquia"] = jer

# ---------------------------------------------------------------- agentes
cat = leer("docs/CATALOGO.md")
t_ag = {plano(r[0]): r for r in tablas(seccion(cat, r"^3\.1 Resumen"))[0]["filas"]}
agentes = []
for p in sorted(glob.glob(str(BASE / "agents/*.md"))):
    fm = frontmatter(p)
    nombre = campo(fm, "name")
    fila = t_ag.get(nombre)
    agentes.append({"nombre": nombre, "procesos": plano(fila[3]).split(" (")[0] if fila else "",
                    "subagente": "disallowedTools: Agent" in fm})
ORDEN_AG = N["orden_agentes"]
exige(sorted(a["nombre"] for a in agentes) == sorted(ORDEN_AG), "los agentes de agents/ no coinciden con narrativa.orden_agentes")
agentes.sort(key=lambda a: ORDEN_AG.index(a["nombre"]))
D["agentes"] = agentes

# ---------------------------------------------------------------- skills
skills = []
for p in sorted(glob.glob(str(BASE / "skills/*/SKILL.md"))):
    fm = frontmatter(p)
    desc = campo(fm, "description")
    usar = re.search(r"Usar:\s*(.*?)(?:\.\s*No:|$)", desc)
    skills.append({"nombre": campo(fm, "name"), "agente": campo(fm, "agente"), "fase": campo(fm, "fase"),
                   "procesos": lista_yaml(campo(fm, "procesos_prince2")),
                   "comando": bool(re.search(r"^disable-model-invocation:\s*true", fm, flags=re.M)),
                   "usar": usar.group(1).strip() if usar else ""})
exige(all(s["agente"] in ORDEN_AG for s in skills), "skill con agente desconocido")
D["skills"] = skills

# ---------------------------------------------------------------- hooks y registros
hooks = json.loads(leer("hooks/hooks.json"))["hooks"]
scripts_hook = sorted({re.search(r"hooks/(\w+\.py)", h["command"]).group(1)
                       for ev in hooks.values() for grupo in ev for h in grupo["hooks"]})
D["hooks"] = {"scripts": scripts_hook, "eventos": sorted(hooks)}

spec = importlib.util.spec_from_file_location("esquema", BASE / "skills/pm-estado-proyecto/scripts/esquema.py")
esq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(esq)
reg_base = [k for k, v in esq.REGISTROS.items() if not v.get("opcional")]
reg_opc = [k for k, v in esq.REGISTROS.items() if v.get("opcional")]
D["registros"] = {"base": reg_base, "opcionales": reg_opc}
D["puertas"] = list(esq.PUERTAS)
D["integraciones"] = {k: sorted(v) for k, v in esq.VALORES_INTEGRACION.items()}
D["bmad_probado"] = [re.sub(r"\s*\(.*$", "", x) for x in compat["bmad"]["probado"]]

# ---------------------------------------------------------------- códigos de control
fuentes_py = "\n".join(pathlib.Path(p).read_text(encoding="utf-8") for p in glob.glob(str(BASE / "skills/*/scripts/*.py")))
codigos = sorted(set(re.findall(r"\b([A-Z]{3})-(\d{2})\b", fuentes_py)))
fam_san = N["familias_sanidad"]            # familias de sanidad, en el orden en que se muestran
san = {}
for fam, num in codigos:
    if fam in fam_san:
        san.setdefault(fam, []).append(f"{fam}-{num}")
sanidad_md = leer("docs/SANIDAD.md")
nombres_fam, permanentes = {}, []
for m in re.finditer(r"^\|\s*\*\*([A-Z]{3}) · ([^*]+)\*\*", sanidad_md, flags=re.M):
    nombre = re.sub(r"\s*\(.*$", "", m.group(2)).strip()
    nombres_fam[m.group(1)] = nombre
    if "control permanente" in m.group(2):
        permanentes.append(m.group(1))
puertas_py = leer("skills/pm-estado-proyecto/scripts/puertas.py")
cod_puerta = sorted(set(re.findall(r"\"([PG]-\d{2})", puertas_py)), key=lambda c: (c[0] != "P", c))
D["controles"] = {
    "familias": [{"familia": k, "nombre": nombres_fam.get(k) or N["familias_sin_nombre"].get(k, k),
                  "codigos": san[k], "permanente": k in permanentes} for k in fam_san if k in san],
    "puerta": cod_puerta,
}
todos = {c for v in san.values() for c in v} | set(cod_puerta)
for c in set(re.findall(r"\b(?:[A-Z]{3}|[PG])-\d{2}\b", json.dumps(N, ensure_ascii=False))):
    exige(c in todos, f"narrativa.json cita el código {c}, que no existe en los scripts")

# ---------------------------------------------------------------- casos E2E (guías)
casos = []
for p in sorted(glob.glob(str(BASE / "docs/guias/E2E-*.md"))):
    t = pathlib.Path(p).read_text(encoding="utf-8")
    cid = re.match(r"E2E-\d+", pathlib.Path(p).name).group(0)
    titulo = re.match(r"#\s+Guía E2E-\d+\s+·\s+(.*)", t).group(1).strip()
    # como en docs/guias/README.md: un paso partido en «6a» y «6b» (sin «6») cuenta una vez; «6b» junto a un «6», aparte
    # salvo que docs/guias/README.md diga que ese paso va partido («el 7 en 7 y 7b»): entonces cuenta una vez
    _ps = re.findall(r"^#{2,3} Paso (\d+)([a-z]?) · ", t, flags=re.M)
    _base = {n_ for n_, l_ in _ps if not l_}
    _readme = re.search(r"\| \[" + cid + r" · [^\n]*?\| (\d+) pasos([^|]*)\|", leer("docs/guias/README.md"))
    _partidos = set(re.findall(r"el (\d+) en ", _readme.group(2))) if _readme else set()
    pasos = sorted({n_ for n_, l_ in _ps} | {n_ + l_ for n_, l_ in _ps if l_ and n_ in _base and n_ not in _partidos})
    exige(_readme and int(_readme.group(1)) == len(pasos), f"{cid}: {len(pasos)} pasos en la guía y {_readme.group(1) if _readme else '?'} en docs/guias/README.md")
    clases = len(tablas(seccion(t, r"^Clases$"))[0]["filas"])
    ind = seccion(t, r"^Indicadores que vas a ver")
    imagenes = {}
    for m in re.finditer(r"!\[([^\]]*)\]\((img/[^)]+)\)\n(.*?)(?=\n\s*\n|\Z)", ind, flags=re.S):
        imagenes[pathlib.Path(m.group(2)).name] = {"alt": m.group(1), "leyenda": " ".join(plano(m.group(3)).split())}
    n = N["casos"][cid]
    exige(imagenes, f"{cid}: la guía no tiene imágenes en «Indicadores que vas a ver»")
    # preferencias de narrativa.json; si la guía cambió y una imagen ya no está, se usa la siguiente disponible
    faltan = [i for i in [n["imagen"]] + n["indicadores"] if i not in imagenes]
    if faltan:
        print(f"aviso: {cid}: {', '.join(sorted(set(faltan)))} ya no está en «Indicadores que vas a ver»; se usan otras de la guía")
    img_ppal = n["imagen"] if n["imagen"] in imagenes else next(iter(imagenes))
    ind = [i for i in n["indicadores"] if i in imagenes]
    ind += [i for i in imagenes if i not in ind][:max(0, len(n["indicadores"]) - len(ind))]
    n = {"imagen": img_ppal, "indicadores": ind}
    casos.append({"id": cid, "titulo_guia": titulo, "archivo": "docs/guias/" + pathlib.Path(p).name,
                  "pasos": len(pasos), "clases": clases, "imagenes": imagenes,
                  "imagen": {"archivo": "docs/guias/img/" + n["imagen"], **imagenes[n["imagen"]]},
                  "indicadores": [imagenes[i]["leyenda"] for i in n["indicadores"]]})
exige(sorted(N["casos"]) == [c["id"] for c in casos], "narrativa.casos no coincide con las guías E2E del repositorio")
D["casos"] = casos
por_caso = {c["id"]: c for c in casos}
ejemplos = []
for ej in N["textos"]["controles"]["ejemplos"]:
    im = por_caso[ej["caso"]]["imagenes"].get(ej["imagen"])
    if not im:
        print(f"aviso: ejemplo de control {ej['codigo']}: {ej['imagen']} ya no está en los indicadores de {ej['caso']}; se omite")
        continue
    ejemplos.append({"codigo": ej["codigo"], "caso": ej["caso"], "texto": im["leyenda"]})
exige(len(ejemplos) >= 2, "menos de dos ejemplos de controles con su leyenda")
D["controles"]["ejemplos"] = ejemplos

# ---------------------------------------------------------------- decidir con contexto y pm-kb: imágenes reales de las guías
guias_txt = "\n".join(pathlib.Path(p).read_text(encoding="utf-8") for p in sorted(glob.glob(str(BASE / "docs/guias/E2E-*.md"))))
D["decidir"] = {}
for k in ("img1", "img2"):
    im = N["textos"]["decidir"][k]
    m = re.search(r"!\[([^\]]*)\]\(img/" + re.escape(im) + r"\)", guias_txt)
    exige(m and (BASE / "docs/guias/img" / im).exists(), f"decidir: {im} no está en docs/guias/img o ninguna guía la cita")
    D["decidir"][k] = {"archivo": "docs/guias/img/" + im, "alt": m.group(1)}

# ---------------------------------------------------------------- ciclo de vida: skills por proceso (metadata de SKILL.md)
ciclo = []
for c in N["ciclo"]:
    exige(all(a in ORDEN_AG for a in c["agentes"]), f"ciclo {c['codigo']}: agente desconocido")
    sk = [s["nombre"] for s in skills if not s["comando"] and s["agente"] in c.get("skills_de", c["agentes"])
          and any(p in s["procesos"] for p in c["procesos"])]
    ciclo.append({**c, "skills": sk})
D["ciclo"] = ciclo
for t in ("autorizar-inicio", "autorizar-proyecto", "autorizar-etapa", "autorizar-plan-excepcion", "autorizar-cierre"):
    exige(t in D["puertas"], f"la puerta {t} no está en esquema.PUERTAS")

# ---------------------------------------------------------------- integraciones: valores aceptados por el esquema
vi = D["integraciones"]
fuera = {"ninguno", "ninguna", "manual"}
grupos = {"especificacion": vi["especificacion"], "tracker": vi["tracker"], "reuniones": vi["reuniones"],
          "canales": vi["correo"] + vi["chat"], "okr": vi["okr"]}
nom = N["textos"]["integraciones"]["nombres"]
for nd in N["textos"]["integraciones"]["nodos"]:
    if nd["clave"] == "mapas":
        nd["valores"] = N["textos"]["integraciones"]["mapas"]
    elif nd["clave"] == "especificacion":
        nd["valores"] = N["textos"]["integraciones"]["bmad"]
    else:
        vals = [v for v in grupos[nd["clave"]] if v not in fuera]
        nd["valores"] = " · ".join(dict.fromkeys(nom.get(v, v) for v in vals))
exige((BASE / "skills/pm-mapas-estrategicos/scripts/mapas.py").exists(), "falta pm-mapas-estrategicos/scripts/mapas.py")

# ---------------------------------------------------------------- webinar
web = []
for p in sorted(glob.glob(str(BASE / "docs/webinar/E2E-*/diapositivas.json"))):
    w = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    carpeta = pathlib.Path(p).parent
    web.append({"caso": w["caso"], "clases": len(w["clases"]),
                "minutos": sum(c.get("duracion_min", 0) for c in w["clases"]),
                "diapositivas": sum(len(c["diapositivas"]) for c in w["clases"]),
                "glosario": len(w.get("glosario", [])),
                "guion": (carpeta / "guion-instructor.md").exists(), "ejercicio": (carpeta / "ejercicio.md").exists()})
D["webinar"] = web
glos_web = {}
for p in sorted(glob.glob(str(BASE / "docs/webinar/E2E-*/diapositivas.json"))):
    for g in json.loads(pathlib.Path(p).read_text(encoding="utf-8")).get("glosario", []):
        glos_web.setdefault(g["termino"], g["definicion"])
glosario = []
for g in N["glosario"]:
    if "definicion" in g:
        d = g["definicion"]
    else:
        exige(g["termino"] in glos_web, f"término {g['termino']!r} no está en los glosarios del webinar")
        d = glos_web[g["termino"]]
    glosario.append({"termino": g["termino"], "definicion": d, "formas": g.get("formas", []),
                     "fuente": "propia" if "definicion" in g else "webinar"})
D["glosario"] = sorted(glosario, key=lambda g: g["termino"].lower())

# ---------------------------------------------------------------- perfiles (RESUMEN-EJECUTIVO §5)
res = leer("docs/RESUMEN-EJECUTIVO.md")
perf = {plano(r[0]): plano(r[1]) for r in tablas(seccion(res, r"Para quién"))[0]["filas"]}
D["perfiles"] = []
for p in N["perfiles"]:
    exige(p["fila"] in perf, f"perfil {p['fila']!r} no está en RESUMEN-EJECUTIVO §5")
    D["perfiles"].append({**p, "obtiene": perf[p["fila"]]})
lema = re.search(r"El modelo prepara; la persona decide; los scripts verifican y registran\.", leer("README.md"))
exige(lema, "README sin el lema «El modelo prepara; …»")
D["lema"] = lema.group(0)

# ---------------------------------------------------------------- cómo empezar
inst = bloques_codigo(seccion(res, r"Cómo empezar"))[0].strip().split("\n")
luego = re.search(r"Luego, en una sesión: (.*?)\. Guía", seccion(res, r"Cómo empezar"), flags=re.S).group(1)
dk = leer("docs/DOCKER.md")
dk_build = bloques_codigo(seccion(dk, r"^4\. Construir"))[0].strip().split("\n")[0]
dk_usar = [l for l in bloques_codigo(seccion(dk, r"^5\.1 "))[0].split("\n") if l.startswith("PROYECTO=")][0]
dk_pruebas = bloques_codigo(seccion(dk, r"^5\.5 "))[0].strip().split("\n")[0].split("  #")[0].strip()
dk_seg = [plano(r[0]) for r in tablas(seccion(dk, r"^7\. Seguridad del contenedor"))[0]["filas"]]
medidas = [m for m in N["textos"]["calidad"]["docker_medidas"] if not any(x.startswith(m) for x in dk_seg)]
exige(not medidas, f"medidas de Docker que ya no están en DOCKER.md §7: {medidas}")
dk_seg = [x for x in dk_seg if any(x.startswith(m) for m in N["textos"]["calidad"]["docker_medidas"])]
D["empezar"] = {"manual": inst, "luego": " ".join(plano(luego).split()), "docker": [dk_build, dk_usar, dk_pruebas],
                "docker_seguridad": dk_seg}

# ---------------------------------------------------------------- seguridad y pruebas en vivo
seg = leer("docs/SEGURIDAD.md")
D["seguridad"] = {"fecha": re.search(r"revisión del (\d{4}-\d{2}-\d{2})", seg).group(1),
                  "filas": [{"severidad": r[0], "cantidad": r[1],
                             "corregidos": re.sub(r"\s*\(.*?\)", "", r[2]).replace(" y ", " + ")}
                            for r in tablas(seccion(seg, r"Resultado en una tabla"))[0]["filas"]]}
pru = leer("docs/PRUEBAS.md")
vivo = []
# Pruebas en vivo: las más recientes registradas (por fecha), de la serie que sea; vivo_serie es la más reciente.
filas_vivo = tablas(seccion(pru, r"^3\.1 Resultados registrados"))[0]["filas"] + \
    sum((t["filas"] for t in tablas(seccion(pru, r"^3\.1 Resultados registrados"))[1:]), [])
series = [tuple(int(x) for x in r[1].split(".")[:2]) for r in filas_vivo
          if len(r) >= 4 and re.match(r"\d+\.\d+\.", r[1]) and re.search(r"\b\d+/\d+\b", r[3])]
serie = ("%d.%d." % max(series)) if series else ""
D["vivo_serie"] = serie.rstrip(".")
for r in filas_vivo:
    if len(r) >= 4 and re.match(r"\d{4}-\d{2}-\d{2}$", r[0]) and re.match(r"\d+\.\d+\.", r[1]):
        fr = re.findall(r"\b\d+/\d+\b", r[3])
        if fr:
            vivo.append({"fecha": r[0], "prueba": plano(r[2]), "resultado": " · ".join(fr)})
vivo = sorted(vivo, key=lambda v: v["fecha"])[-8:]
D["vivo"] = vivo
D["frases_enrutamiento"] = sum(1 for l in leer("docs/evaluacion/frases-enrutamiento.tsv").splitlines() if l.strip() and not l.startswith("#"))

# ---------------------------------------------------------------- pruebas (se corren ahora)
previo = AQUI / "datos.json"
if REUSAR and previo.exists():
    D["pruebas"] = json.loads(previo.read_text(encoding="utf-8"))["pruebas"]
    D["pruebas"]["reusado"] = True
else:
    P = {"fecha": fecha}
    rc, out = correr([sys.executable, "scripts/validar_paquete.py"])
    m = re.search(r"Skills: (\d+) \((\d+) invocables por el modelo, listado (\d+) caracteres\) · Agentes: (\d+)", out)
    exige(m, "salida inesperada de validar_paquete.py:\n" + out[-800:])
    P["validar"] = {"ok": rc == 0, "skills": int(m.group(1)), "invocables": int(m.group(2)), "listado": int(m.group(3)), "agentes": int(m.group(4))}
    rc, out = correr([sys.executable, "scripts/probar_paquete.py"])
    m = re.search(r"Resultado: (\d+) OK · (\d+) FALLO", out)
    exige(m, "salida inesperada de probar_paquete.py:\n" + out[-800:])
    P["regresion"] = {"ok": int(m.group(1)), "fallo": int(m.group(2)), "casos": len(re.findall(r"^Caso \S+ · ", out, flags=re.M))}
    with tempfile.TemporaryDirectory() as tmp:
        rc, out = correr([sys.executable, "scripts/pruebas/guias_e2e/correr.py", "--salida", tmp])
    P["e2e"] = {"ok": len(re.findall(r"^OK\s+guía E2E-", out, flags=re.M)), "total": len(re.findall(r"^\w+\s+guía E2E-", out, flags=re.M))}
    rc, out = correr([sys.executable, "scripts/validar_mermaid.py"])
    m = re.search(r"(\d+) bloques Mermaid · (\d+) error", out)
    exige(m, "salida inesperada de validar_mermaid.py:\n" + out[-800:])
    P["mermaid"] = {"bloques": int(m.group(1)), "errores": int(m.group(2))}
    D["pruebas"] = P
P = D["pruebas"]
exige(P["validar"]["skills"] == len(skills) and P["validar"]["agentes"] == len(agentes), "validar_paquete.py y el conteo de carpetas no coinciden")

# ---------------------------------------------------------------- cifras para la narrativa
cmd = [s for s in skills if s["comando"]]
D["n"] = {
    "version": D["meta"]["version"], "agentes": len(agentes), "subagentes": sum(a["subagente"] for a in agentes),
    "skills": len(skills), "invocables": len(skills) - len(cmd), "comandos": len(cmd),
    "hooks": len(scripts_hook), "eventos_hooks": len(hooks),
    "registros": len(reg_base) + len(reg_opc), "registros_base": len(reg_base), "registros_opc": len(reg_opc),
    "puertas": len(D["puertas"]), "codigos_sanidad": sum(len(v) for v in san.values()), "familias_sanidad": len(san),
    "codigos_puerta": len(cod_puerta), "codigos": sum(len(v) for v in san.values()) + len(cod_puerta),
    "casos": len(casos), "pasos_casos": sum(c["pasos"] for c in casos),
    "clases_webinar": sum(w["clases"] for w in web), "diapositivas_webinar": sum(w["diapositivas"] for w in web),
    "pruebas_ok": P["regresion"]["ok"], "pruebas_fallo": P["regresion"]["fallo"], "pruebas_casos": P["regresion"]["casos"],
    "e2e_ok": P["e2e"]["ok"], "e2e_total": P["e2e"]["total"], "mermaid": P["mermaid"]["bloques"],
    "mermaid_errores": P["mermaid"]["errores"], "listado": P["validar"]["listado"], "frases": D["frases_enrutamiento"],
    "familias_permanentes": len(permanentes),
    "hooks_nombres": " · ".join(pathlib.Path(s).stem for s in scripts_hook),
    "bmad_probado": ", ".join(D["bmad_probado"]), "licencia": D["meta"]["licencia"],
    "serie_vivo": D["vivo_serie"],
}


def llenar(x):
    if isinstance(x, str):
        return x.format_map(D["n"]) if "{" in x else x
    if isinstance(x, list):
        return [llenar(i) for i in x]
    if isinstance(x, dict):
        return {k: llenar(v) for k, v in x.items()}
    return x


D["txt"] = llenar(N["textos"])

# ---------------------------------------------------------------- diagrama de arquitectura (Mermaid → PNG)
DG = AQUI / "diagramas"
DG.mkdir(exist_ok=True)
mmd = llenar(N["arquitectura_mmd"])
(DG / "arquitectura.mmd").write_text(mmd, encoding="utf-8")
cfg = DG / "mermaid-config.json"
cfg.write_text(json.dumps(N["mermaid_config"], ensure_ascii=False), encoding="utf-8")
subprocess.run([MMDC] + (["-p", PUPPETEER] if PUPPETEER else []) + ["-i", str(DG / "arquitectura.mmd"), "-o",
               str(DG / "arquitectura.png"), "-c", str(cfg), "-s", "3", "-b", "white"], check=True, capture_output=True)
svg = DG / "arquitectura.svg"
subprocess.run([MMDC] + (["-p", PUPPETEER] if PUPPETEER else []) + ["-i", str(DG / "arquitectura.mmd"), "-o", str(svg),
               "-c", str(cfg), "-b", "white"], check=True, capture_output=True)
exige("Syntax error" not in svg.read_text(encoding="utf-8"), "mmdc devolvió un diagrama de error (revisar arquitectura.mmd)")
D["diagramas"] = {"arquitectura": "diagramas/arquitectura.png"}

(AQUI / "datos.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
n = D["n"]
print(f"datos.json · v{n['version']} · {n['agentes']} agentes · {n['skills']} skills ({n['invocables']}+{n['comandos']}) · "
      f"{n['hooks']} hooks · {n['registros']} registros · {n['codigos']} códigos de control · {n['casos']} casos E2E · "
      f"pruebas {n['pruebas_ok']} OK / {n['pruebas_fallo']} FALLO{' (reusadas)' if P.get('reusado') else ''} · "
      f"E2E {n['e2e_ok']}/{n['e2e_total']} · Mermaid {n['mermaid']}")
