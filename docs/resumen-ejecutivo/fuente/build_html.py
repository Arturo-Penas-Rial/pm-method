"""Resumen ejecutivo comercial de pm-method · HTML autocontenido.

Uso: python3 build_html.py   (lee datos.json y diagramas/; escribe ../resumen-ejecutivo-pm-method.html)
Un solo archivo: CSS y JS en línea, imágenes como data URI; claro, oscuro o automático; imprimible (una diapositiva por
página apaisada); navegación por diapositiva; glosario con anclas y enlaces desde el texto.
"""
import base64, html, json, os, pathlib, re, unicodedata

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
os.chdir(AQUI)
D = json.load(open("datos.json", encoding="utf-8"))
T, NN = D["txt"], D["n"]
SALIDA = AQUI.parent / "resumen-ejecutivo-pm-method.html"
e = html.escape


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def data_uri(p):
    p = pathlib.Path(p)
    mime = "image/png" if p.suffix == ".png" else "image/svg+xml"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


# ---------- glosario: enlaza la primera aparición de cada término por diapositiva ----------
FORMAS = sorted(((f, "g-" + slug(g["termino"])) for g in D["glosario"] for f in g["formas"]), key=lambda x: -len(x[0]))
_usados = set()


def glos(texto):
    """Escapa `texto` y enlaza al glosario la primera aparición (en esta diapositiva) de cada término."""
    t = e(texto)
    for forma, ancla in FORMAS:
        if ancla in _usados:
            continue
        pat = re.compile(r"(?<![\w>/#-])(" + re.escape(e(forma)) + r")(?![\w<])", flags=0 if forma[:1].isupper() else re.I)
        partes = re.split(r"(<[^>]+>)", t)
        hecho = False
        for i, p in enumerate(partes):
            if hecho or p.startswith("<") or (i > 0 and partes[i - 1].startswith("<a ")):
                continue
            m = pat.search(p)
            if m:
                partes[i] = p[:m.start()] + f'<a class="glos" href="#{ancla}">{m.group(1)}</a>' + p[m.end():]
                hecho = True
        if hecho:
            _usados.add(ancla)
            t = "".join(partes)
    return t


def code(t):
    return re.sub(r"`([^`]*)`", r"<code>\1</code>", t)


SLIDES = []


def diapositiva(seccion, titulo, cuerpo, en="", clase=""):
    SLIDES.append({"seccion": seccion, "titulo": titulo, "cuerpo": cuerpo, "en": en, "clase": clase})
    _usados.clear()


def kicker(t):
    return f'<p class="kicker">{e(t)}</p>'


# ====================== 1 · Portada
P = T["portada"]
cifras = "".join(f'<div class="cifra"><b>{e(v)}</b><span>{e(t)}</span></div>' for v, t in P["cifras"])
diapositiva("Propuesta", P["titulo"], f"""
<div class="logo-ieee logo-portada" aria-label="Espacio para el logo de IEEE">Logo IEEE</div>
<p class="kicker claro">{e(P['kicker'])}</p>
<h1>{e(P['titulo'])}</h1>
<p class="sub">{e(P['subtitulo'])}</p>
<div class="cifras">{cifras}</div>
<p class="fecha">pm-method {e(D['meta']['version'])} · {e(D['meta']['fecha_larga'])}</p>""", P["en"], "portada")
_usados.clear()

# ====================== 2 · Problema
P = T["problema"]
filas = "".join(f"""<div class="pr-fila"><div class="pr-hoy">{e(h)}</div><div class="pr-flecha" aria-hidden="true">→</div>
<div class="pr-pm">{glos(p)}</div><div class="pr-cod">{e(c)}</div></div>""" for h, p, c in P["filas"])
diapositiva("Propuesta", P["titulo"], f"""
<div class="pr-cab"><span>{e(P['col_hoy'])}</span><span></span><span>{e(P['col_pm'])}</span><span>Control</span></div>
{filas}
<p class="lema">{e(D['lema'])}</p>""", P["en"])

# ====================== 3 · Perfiles
P = T["perfiles"]
cards = "".join(f"""<article class="card {'tinta' if i in (0, 3) else 'calida'}"><div class="num">{i + 1}</div><h3>{e(p['titulo'])}</h3>
<p class="rot">{e(P['obtiene'])}</p><p>{glos(p['obtiene'][0].upper() + p['obtiene'][1:])}.</p>
<p class="empieza"><b>{e(P['empieza'])}:</b> {e(p['empieza'])}</p></article>""" for i, p in enumerate(D["perfiles"]))
diapositiva("Propuesta", P["titulo"], f'<div class="grid2">{cards}</div>', P["en"])

# ====================== 4 · Qué es
P = T["que_es"]
capas = "".join(f'<div class="capa c{i}"><b>{i + 1} · {e(c["capa"])}</b><span>{glos(c["rol"][0].upper() + c["rol"][1:])}</span></div>' for i, c in enumerate(D["jerarquia"]))
kpis = "".join(f'<div class="kpi"><div><b>{e(v)}</b><span>{e(t)}</span></div><p>{e(d)}</p></div>' for v, t, d in P["kpis"])
diapositiva("Producto", P["titulo"], f"""<div class="dos-col"><div><p class="rot">{e(P['jerarquia'])}</p><div class="capas">{capas}</div></div>
<div class="kpis">{kpis}</div></div><p class="nota">{glos(P['nota'])}</p>""", P["en"])

# ====================== 5 · Arquitectura
P = T["arquitectura"]
puntos = "".join(f'<article class="card {"calida" if i == 0 else "tinta"}"><h3>{e(t)}</h3><p>{glos(d)}</p></article>' for i, (t, d) in enumerate(P["puntos"]))
diapositiva("Producto", P["titulo"], f"""<figure class="diag"><img src="{data_uri(D['diagramas']['arquitectura'])}" alt="Diagrama de arquitectura de pm-method: personas, orquestador, subagentes, skills, BMAD, MCP, carpeta del proyecto, hooks y sanidad"></figure>
<div class="grid3">{puntos}</div>""", P["en"])

# ====================== 6 · Componentes
P = T["componentes"]
cols = []
for a in D["agentes"]:
    sk = sorted((s for s in D["skills"] if s["agente"] == a["nombre"]), key=lambda s: (s["comando"], s["nombre"]))
    li = "".join(f'<li class="{"cmd" if s["comando"] else ""}" title="{e(s["usar"])}">{e(s["nombre"])}{" <small>" + e(P["comando"]) + "</small>" if s["comando"] else ""}</li>' for s in sk)
    cols.append(f"""<div class="agente {'dir' if a['nombre'] == 'pm-director' else ''}"><header><b>{e(a['nombre'])}</b>
<span class="cuenta">{len(sk)}<small> skills</small></span><span class="rol">{e(P['roles'].get(a['nombre'], ''))}</span></header><ul>{li}</ul></div>""")
diapositiva("Producto", P["titulo"], f'<div class="agentes">{"".join(cols)}</div><p class="nota">{glos(P["nota"])}</p>', P["en"])

# ====================== 7 · Ciclo de vida
P = T["ciclo"]
puertas = ["autorizar-inicio", "autorizar-proyecto + autorizar-etapa", "límite de etapa", "cierre", "autorizar-cierre"]
pasos = []
for i, c in enumerate(D["ciclo"]):
    es_p = not (puertas[i].startswith("límite") or puertas[i] == "cierre")
    pasos.append(f"""<div class="proc"><div class="chev">{e(c['codigo'])}<span>{e(c['nombre'])}</span></div>
<div class="gate {'si' if es_p else 'no'}"><i aria-hidden="true"></i>→ {e(puertas[i])}</div>
<p class="etapa">{e(c['etapa'])}</p><p class="ag">{e(' + '.join(c['agentes']))}</p><p class="prod">{e(c['produce'])}</p>
<ul>{''.join(f'<li>{e(s)}</li>' for s in c['skills'])}</ul></div>""")
diapositiva("Producto", P["titulo"], f"""<div class="dp">{glos(P['direccion'])}</div><div class="ciclo">{''.join(pasos)}</div>
<p class="leyenda"><span class="g si"><i></i>puerta de la junta</span><span class="g no"><i></i>transición que prepara el gestor</span>
<b>SB → CS: autorizar-etapa (n+1) · {e(P['excepcion'])}</b></p><p class="nota">{glos(P['antes'])}</p>""", P["en"])

# ====================== 8 · Controles (gráfico de datos: SVG en línea con tooltip y vista de tabla)
P = T["controles"]
fam = sorted(D["controles"]["familias"], key=lambda f: (-len(f["codigos"]), f["familia"]))
mx = max(len(f["codigos"]) for f in fam)
barras = []
for f in fam:
    k = len(f["codigos"])
    tip = f'{f["familia"]} · {f["nombre"]}: {k} códigos ({", ".join(f["codigos"])})'
    barras.append(f"""<div class="fila" data-tip="{e(tip)}" tabindex="0" role="listitem" aria-label="{e(tip)}"><span class="cat">{e(f['familia'])} · {e(f['nombre'])}</span>
<span class="pista"><span class="barra {'perm' if f['permanente'] else 'otra'}" style="width:calc((100% - 28px) * {k / mx:.3f})"></span><b class="val">{k}</b></span></div>""")
tabla_fam = "".join(f"<tr><td>{e(f['familia'])}</td><td>{e(f['nombre'])}</td><td>{len(f['codigos'])}</td><td>{'sí' if f['permanente'] else 'no'}</td><td><code>{e(', '.join(f['codigos']))}</code></td></tr>" for f in fam)
ejemplos = "".join(f'<article class="card {"calida" if i % 2 == 0 else "tinta"}"><p><span class="cod">{e(x["codigo"])}</span> <b class="cas">{e(x["caso"])}</b></p><p>{glos(x["texto"])}</p></article>' for i, x in enumerate(D["controles"]["ejemplos"]))
diapositiva("Producto", P["titulo"], f"""<div class="dos-col ctrl"><div><p class="rot azul">{e(P['grafico'])}</p>
<p class="leyenda"><span class="sw perm"></span>{e(P['leyenda_perm'])} <span class="sw otra"></span>{e(P['leyenda_otro'])}</p>
<figure class="grafico"><div class="barras" role="list" aria-label="{e(P['grafico'])}">{''.join(barras)}</div>
<div class="tip" role="status" hidden></div></figure>
<details><summary>Ver como tabla</summary><div class="scroll"><table><thead><tr><th>Familia</th><th>Nombre</th><th>Códigos</th><th>Permanente</th><th>Lista</th></tr></thead><tbody>{tabla_fam}</tbody></table></div></details>
<p class="destaca">{glos(P['puerta'])}</p></div>
<div><p class="rot azul">{e(P['ejemplos_titulo'])}</p><div class="pila">{ejemplos}</div></div></div>""", P["en"])

# ====================== 9 · Decidir con contexto y buscar con evidencia
P = T["decidir"]
cols = []
for k, (t, pts, im) in enumerate([(P["col1"], P["puntos1"], D["decidir"]["img1"]), (P["col2"], P["puntos2"], D["decidir"]["img2"])]):
    cols.append(f"""<article class="card {'tinta' if k else 'gris'}"><p class="rot {'azul' if k else 'marino'}">{e(t)}</p><ul class="vin">{''.join(f'<li>{glos(x)}</li>' for x in pts)}</ul>
<figure class="foto"><img src="{data_uri(RAIZ / im['archivo'])}" alt="{e(im['alt'])}"><figcaption>{e(im['alt'])}</figcaption></figure></article>""")
diapositiva("Producto", P["titulo"], f'<div class="grid2">{"".join(cols)}</div><p class="lema chico">{e(P["codigos"])}</p>', P["en"])

# ====================== 10 · Integraciones
P = T["integraciones"]
nodos = "".join(f'<article class="card {"calida" if i % 3 == 0 else "tinta"}"><h3>{e(z["nombre"])}</h3><p class="vals">{e(z["valores"])}</p><p>{glos(z["texto"])}</p></article>' for i, z in enumerate(P["nodos"]))
mitad = (len(P["nodos"]) + 1) // 2
diapositiva("Producto", P["titulo"], f"""<div class="hub"><div class="hub-col">{''.join(re.findall(r'<article.*?</article>', nodos, flags=re.S)[:mitad])}</div>
<div class="centro"><b>{e(P['centro'])}</b><span>{e(P['centro_sub'])}</span></div>
<div class="hub-col">{''.join(re.findall(r'<article.*?</article>', nodos, flags=re.S)[mitad:])}</div></div><p class="nota">{glos(P['nota'])}</p>""", P["en"])

# ====================== 11 · Catálogo E2E y webinar
P = T["catalogo"]
web = {w["caso"]: w for w in D["webinar"]}
primer_caso = len(SLIDES) + 2   # el catálogo es la diapositiva siguiente y los casos van después
filas = "".join(f"<tr><td><a href='#d-{primer_caso + i}'><b>{e(c['id'])}</b></a></td><td>{glos(P['recorre'].get(c['id'], c['titulo_guia']))}</td><td class='n'>{c['pasos']}</td>"
                f"<td class='n'>{web.get(c['id'], {}).get('clases', '—')}</td><td class='n'>{web.get(c['id'], {}).get('minutos', '—')}</td>"
                f"<td class='n'>{web.get(c['id'], {}).get('diapositivas', '—')}</td><td class='n'>{web.get(c['id'], {}).get('glosario', '—')}</td></tr>" for i, c in enumerate(D["casos"]))
cab = "".join(f"<th>{e(h)}</th>" for h in P["cab"])
material = glos(re.sub(r"^[^:]+:\s*", "", P["material"]))
induccion = glos(re.sub(r"^[^:]+:\s*", "", P["induccion"]))
diapositiva("Casos E2E", P["titulo"], f"""<div class="scroll"><table class="cat"><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>
<div class="grid2"><article class="card tinta"><p class="rot azul">Material por caso</p><p>{material}</p></article>
<article class="card calida"><p class="rot">Inducción</p><p>{induccion}</p></article></div>""", P["en"])

# ====================== 12–16 · Casos
R = T["casos"]["rotulos"]
for c in D["casos"]:
    C = T["casos"][c["id"]]
    ficha = R["ficha"].replace("[pasos]", str(c["pasos"])).replace("[clases]", str(c["clases"])).replace("[archivo]", c["archivo"])
    inds = "".join(f"<li>{glos(t)}</li>" for t in c["indicadores"])
    diapositiva("Casos E2E", C["titulo"], f"""<div class="caso">
<div><p class="rot">{e(R['problema'])}</p><p class="grande">{glos(C['problema'])}</p>
<p class="rot azul">{e(R['muestra'])}</p><ul class="vin">{''.join(f'<li>{glos(m)}</li>' for m in C['muestra'])}</ul>
<p class="rot marino">{e(R['indicadores'])}</p><ul class="ind">{inds}</ul></div>
<div><figure class="foto"><img src="{data_uri(RAIZ / c['imagen']['archivo'])}" alt="{e(c['imagen']['alt'])}"><figcaption>{e(c['imagen']['alt'])}</figcaption></figure>
<p class="ficha">{e(ficha)}</p></div></div>""", T["casos"]["en"] + " · " + c["archivo"])

# ====================== 17 · Calidad
P = T["calidad"]
kp = "".join(f'<div class="kpi oscuro"><b>{e(v)}</b><span>{e(t)}</span><p>{e(d)}</p></div>' for v, t, d in P["kpis"])


def corto(t):
    t = re.sub(r"^suite\.py\s+", "", t)
    t = re.sub(r"\s*\(.*$", "", t)
    t = re.sub(r",\s*\d.*$", "", t)
    t = re.sub(r"\s*--skills-extra\s+<[^>]*>", " con skills de BMAD", t)
    t = " ".join(t.split())
    return t if len(t) <= 60 else t[:59] + "…"


vivo = "".join(f"<li><b>{e(v['resultado'])}</b> {e(corto(v['prueba']))} <small>{e(v['fecha'])}</small></li>" for v in D["vivo"][-8:])
seg = "".join(f"<tr><td>{e(f['severidad'])}</td><td class='n'>{e(f['cantidad'])}</td><td>{e(f['corregidos'])}</td></tr>" for f in D["seguridad"]["filas"])
dk = "".join(f"<li>{e(x)}</li>" for x in D["empezar"]["docker_seguridad"][:6])
diapositiva("Confianza y adopción", P["titulo"], f"""<div class="kpis4">{kp}</div><div class="grid3">
<article class="card gris"><p class="rot marino">{e(P['vivo'])}</p><ul class="vivo">{vivo}</ul></article>
<article class="card gris"><p class="rot marino">{e(P['seguridad'])} · {e(D['seguridad']['fecha'])}</p><div class="scroll"><table><thead><tr><th>Severidad</th><th>Hallazgos</th><th>Corregidos</th></tr></thead><tbody>{seg}</tbody></table></div>
<p class="nota">Sin hallazgos de severidad alta. Detalle y estado de cada uno en docs/SEGURIDAD.md.</p></article>
<article class="card gris"><p class="rot marino">{e(P['docker'])}</p><ul class="vin">{dk}</ul></article></div>
<p class="nota">{glos(P['nota'])}</p>""", P["en"])

# ====================== 18 · Comparativo: pm-method, PMI Infinity y gestión tradicional
P = T["comparativo"]
cab = "".join(f'<th scope="col"{" class=pm" if i == 1 else ""}>{e(h)}</th>' for i, h in enumerate(P["cab"]))
filas = "".join(f'<tr><th scope="row">{e(f[0])}</th><td class="pm" data-col="{e(P["cab"][1])}">{glos(f[1])}</td>'
                f'<td data-col="{e(P["cab"][2])}">{glos(f[2])}</td><td data-col="{e(P["cab"][3])}">{glos(f[3])}</td></tr>' for f in P["filas"])
fuentes = "".join(f'<li><a href="{e(u)}" rel="noopener">{e(u)}</a></li>' for u in P["fuentes_lista"])
diapositiva("Confianza y adopción", P["titulo"], f"""<p class="grande bajada">{glos(P['bajada'])}</p>
<div class="scroll"><table class="cmp"><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>
<p class="nota fuentes">{e(P['fuentes'])}</p>
<details><summary>Fuentes de terceros</summary><ul class="fuentes">{fuentes}</ul></details>""", P["en"])

# ====================== 19 · Cuándo conviene cada uno y lo que pm-method no hace
P = T["conviene"]
sit = "".join(f"<tr><td>{glos(s)}</td><td class='conv'>{glos(c)}</td></tr>" for s, c in P["situaciones"])
lim = "".join(f"<li>{glos(x)}</li>" for x in P["limites"])
diapositiva("Confianza y adopción", P["titulo"], f"""<div class="grid2"><article class="card tinta"><p class="rot azul">{e(P['col1'])}</p>
<div class="scroll"><table class="conviene"><thead><tr><th>{e(P['cab'][0])}</th><th>{e(P['cab'][1])}</th></tr></thead><tbody>{sit}</tbody></table></div></article>
<article class="card calida"><p class="rot">{e(P['col2'])}</p><ul class="vin">{lim}</ul></article></div>
<p class="lema chico">{glos(P['combinar'])}</p>""", P["en"])

# ====================== 20 · Cómo empezar
P, E = T["empezar"], D["empezar"]
dsteps = "".join(f"<h4>{i + 1} · {e(P['docker_pasos'][i] if i < len(P['docker_pasos']) else '')}</h4><pre>{e(c)}</pre>" for i, c in enumerate(E["docker"]))
diapositiva("Confianza y adopción", P["titulo"], f"""<div class="grid2"><article class="card tinta"><p class="rot marino">{e(P['manual'])}</p><pre>{e(chr(10).join(E['manual']))}</pre>
<p class="rot azul">{e(P['luego'])}</p><p class="grande">{code(e(E['luego']))}</p></article>
<article class="card gris"><p class="rot marino">{e(P['docker'])}</p>{dsteps}</article></div>
<p class="lema chico">{glos(P['siguiente'])}</p>""", P["en"])

# ====================== 21 · Glosario
P = T["glosario"]
letras = []
filas = []
for g in D["glosario"]:
    l = unicodedata.normalize("NFKD", g["termino"][0]).encode("ascii", "ignore").decode().upper()
    ancla_l = ""
    if l not in letras:
        letras.append(l)
        ancla_l = f'<span id="g-letra-{l}"></span>'
    filas.append(f'<dt id="g-{slug(g["termino"])}">{ancla_l}{e(g["termino"])}</dt><dd>{e(g["definicion"])}</dd>')
indice = " ".join(f'<a href="#g-letra-{l}">{l}</a>' for l in letras)
diapositiva("Confianza y adopción", P["titulo"], f'<p class="letras">{indice}</p><dl class="glosario">{"".join(filas)}</dl>', P["en"])

# ====================== ensamblado
nav = "".join(f'<option value="d-{i + 1}">{i + 1} · {e(s["titulo"][:70])}</option>' for i, s in enumerate(SLIDES))
secciones = []
for i, s in enumerate(SLIDES):
    num = i + 1
    if s["clase"] == "portada":
        cab = ""
    else:
        sec = s["seccion"]
        cab = f'<header class="sh">{kicker(f"{num} · {sec}")}<h2>{e(s["titulo"])}</h2><div class="logo-ieee" aria-hidden="true">Logo IEEE</div></header>'
    pie = f'<footer class="sf"><span>{e(T["pie"])} · {e(D["meta"]["fecha"])}</span><span>{num} / {len(SLIDES)}</span></footer>'
    en = f'<p class="en" lang="en">{e(s["en"])}</p>' if s["en"] and s["clase"] != "portada" else (f'<p class="en claro" lang="en">{e(s["en"])}</p>' if s["en"] else "")
    secciones.append(f'<section class="slide {s["clase"]}" id="d-{num}" aria-label="Diapositiva {num}">{cab}<div class="sb">{s["cuerpo"]}</div>{en}{pie}</section>')

CSS = r"""
:root{--bg:#eef1f4;--sup:#ffffff;--sup2:#f4f6f8;--tinta:#e9f1f8;--calida:#fbf1e6;--txt:#272425;--txt2:#52514e;--muda:#696969;
--marino:#002855;--azul:#00629b;--naranja:#b5651d;--linea:#d5dcE3;--cod:#0f2238;--codtxt:#e8eef5;--hero:#002855;--hero2:#0b3a6e;--cielo:#9fd0f0;
--perm:#eb6834;--otra:#2a78d6;--glos:#00629b;--sombra:0 1px 3px rgba(0,0,0,.08),0 6px 18px rgba(0,40,85,.06)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#101418;--sup:#1a1f25;--sup2:#222930;--tinta:#16283a;--calida:#2f2418;
--txt:#e7e9ec;--txt2:#c2c7cd;--muda:#9aa3ad;--marino:#9fc4ea;--azul:#6fb3e6;--naranja:#f0a463;--linea:#33404c;--cod:#0b1520;--codtxt:#dfe8f2;
--hero:#0b2340;--hero2:#14365c;--cielo:#9fd0f0;--perm:#d95926;--otra:#3987e5;--glos:#8cc6f0;--sombra:none}}
:root[data-theme="dark"]{--bg:#101418;--sup:#1a1f25;--sup2:#222930;--tinta:#16283a;--calida:#2f2418;--txt:#e7e9ec;--txt2:#c2c7cd;--muda:#9aa3ad;
--marino:#9fc4ea;--azul:#6fb3e6;--naranja:#f0a463;--linea:#33404c;--cod:#0b1520;--codtxt:#dfe8f2;--hero:#0b2340;--hero2:#14365c;--cielo:#9fd0f0;
--perm:#d95926;--otra:#3987e5;--glos:#8cc6f0;--sombra:none}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--bg);color:var(--txt);font:16px/1.5 Arial,Helvetica,sans-serif;-webkit-text-size-adjust:100%}
a{color:var(--glos)}code,pre{font-family:"Courier New",Courier,monospace}
.barra{position:sticky;top:0;z-index:10;display:flex;gap:10px;align-items:center;padding:8px 16px;background:var(--hero);color:#fff;flex-wrap:wrap}
.barra .marca{font-weight:bold;white-space:nowrap}.barra select{flex:1 1 220px;width:0;min-width:0;max-width:520px;font:inherit;font-size:14px;padding:5px 6px;border-radius:6px;border:0}
.barra button{font:inherit;font-size:14px;padding:5px 10px;border-radius:6px;border:1px solid rgba(255,255,255,.5);background:transparent;color:#fff;cursor:pointer}
.barra button:hover{background:rgba(255,255,255,.12)}.barra .flechas{display:flex;gap:6px}
main{max-width:1180px;margin:0 auto;padding:20px 16px 60px}
.slide{background:var(--sup);border-radius:14px;box-shadow:var(--sombra);margin:0 0 26px;padding:26px 30px 14px;display:flex;flex-direction:column;min-height:560px}
.sb{flex:1}.sh{display:grid;grid-template-columns:1fr auto;gap:4px 18px;align-items:start;margin-bottom:16px}
.sh .kicker{grid-column:1/-1;margin:0}.sh h2{margin:0;padding:12px 18px;border-radius:10px;background:var(--azul);color:#fff;font-size:24px;line-height:1.25}
:root[data-theme="dark"] .sh h2{background:#0d4a77}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .sh h2{background:#0d4a77}}
.kicker{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--naranja);font-weight:bold}
.logo-ieee{border:1.5px dashed var(--muda);color:var(--muda);border-radius:6px;font-size:12px;display:flex;align-items:center;justify-content:center;width:120px;height:52px}
.sf{display:flex;justify-content:space-between;color:var(--muda);font-size:12px;border-top:1px solid var(--linea);padding-top:8px;margin-top:14px}
.en{color:var(--muda);font-size:13px;font-style:italic;margin:12px 0 0}
.rot{font-size:12px;letter-spacing:.06em;text-transform:uppercase;font-weight:bold;color:var(--naranja);margin:0 0 6px}
.rot.azul{color:var(--azul)}.rot.marino{color:var(--marino)}
.nota{color:var(--muda);font-size:14px}.grande{font-size:18px}
/* portada */
.slide.portada{background:var(--hero);color:#fff;padding:34px 40px 18px}.portada .sf{color:var(--cielo);border-color:rgba(255,255,255,.2)}
.portada .logo-ieee{border-color:var(--cielo);color:var(--cielo);width:160px;height:62px}.portada .kicker.claro{color:var(--cielo);margin-top:28px;font-size:15px}
.portada h1{font-size:44px;line-height:1.12;margin:8px 0 14px;max-width:960px}.portada .sub{font-size:20px;max-width:900px;margin:0 0 26px}
.cifras{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.cifra{background:var(--hero2);border-radius:10px;padding:12px 16px}
.cifra b{display:block;font-size:36px;line-height:1.1}.cifra span{color:var(--cielo);font-size:15px}.portada .fecha{margin:20px 0 0}.en.claro{color:var(--cielo)}
/* problema */
.pr-cab,.pr-fila{display:grid;grid-template-columns:1fr 36px 1fr 150px;gap:8px;align-items:stretch}
.pr-cab span{font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:.06em;color:var(--muda)}.pr-cab span:nth-child(3){color:var(--azul)}.pr-cab span:nth-child(4){color:var(--marino)}
.pr-fila{margin:8px 0}.pr-hoy,.pr-pm{padding:10px 14px;border-radius:8px;font-size:16px}.pr-hoy{background:var(--sup2)}.pr-pm{background:var(--tinta);color:var(--marino)}
.pr-flecha{display:flex;align-items:center;justify-content:center;color:var(--naranja);font-weight:bold;font-size:22px}
.pr-cod{display:flex;align-items:center;justify-content:center;text-align:center;background:var(--marino);color:var(--sup);border-radius:8px;font:bold 13px "Courier New",monospace;padding:6px}
.lema{background:var(--calida);color:var(--naranja);border-radius:10px;padding:12px 18px;font-weight:bold;font-style:italic;font-size:19px;margin:16px 0 0}.lema.chico{font-size:16px;font-style:normal}
/* tarjetas */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:14px}
.card{border-radius:12px;padding:16px 18px;position:relative}.card.tinta{background:var(--tinta)}.card.calida{background:var(--calida)}.card.gris{background:var(--sup2)}
.card h3{margin:0 0 6px;color:var(--marino);font-size:19px}.card p{margin:0 0 8px}.card .num{position:absolute;right:16px;top:14px;width:36px;height:36px;border-radius:50%;background:var(--marino);color:var(--sup);display:flex;align-items:center;justify-content:center;font-weight:bold}
.card.calida .num{background:var(--naranja)}.empieza{font-size:14px}.empieza b{color:var(--naranja)}
.dos-col{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.capas{display:flex;flex-direction:column;gap:8px}.capa{border-radius:9px;padding:10px 14px;color:#fff}.capa b{display:block;font-size:18px}.capa span{font-size:14px}
.capa.c0{background:#002855}.capa.c1{background:#00629b;margin-left:14px}.capa.c2{background:#4f86b5;margin-left:28px}.capa.c3{background:var(--tinta);color:var(--marino);margin-left:42px}
.capa a.glos{color:inherit}
.kpis{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-content:start}.kpi{background:var(--sup2);border-radius:10px;padding:12px 14px}
.kpi div{display:flex;align-items:baseline;gap:10px}.kpi b{font-size:34px;color:var(--marino)}.kpi span{font-weight:bold;color:var(--azul)}.kpi p{margin:4px 0 0;color:var(--muda);font-size:14px}
.kpis4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.kpi.oscuro{background:var(--hero);color:#fff}.kpi.oscuro b{display:block;color:#fff;font-size:32px}.kpi.oscuro span{color:var(--cielo)}.kpi.oscuro p{color:#dfe8f2}
figure{margin:0}.diag{background:#fff;border-radius:10px;padding:10px;border:1px solid var(--linea)}.diag img{width:100%;height:auto;display:block;cursor:zoom-in}
/* componentes */
.agentes{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}.agente header{background:#002855;color:#fff;border-radius:10px 10px 0 0;padding:10px 12px;min-height:118px}
.agente.dir header{background:#b5651d}.agente header b{display:block;font-size:15px}.cuenta{display:block;font-size:28px;font-weight:bold;line-height:1.2}.cuenta small{font-size:13px;font-weight:normal}
.agente .rol{display:block;font-size:13px;color:#cfe6f7}.agente.dir .rol{color:#fff2e6}
.agente ul{list-style:none;margin:0;padding:10px 12px;background:var(--sup2);border-radius:0 0 10px 10px;min-height:250px;font-size:14px}
.agente li{margin:0 0 5px;overflow-wrap:anywhere}.agente li.cmd{color:var(--naranja);font-weight:bold}.agente li small{color:var(--muda);font-weight:normal;font-style:italic}
/* ciclo */
.dp{background:#002855;color:#fff;border-radius:9px;padding:9px 14px;font-weight:bold}.dp a.glos{color:#cfe6f7}
.ciclo{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:12px}
.chev{background:var(--azul);color:#fff;font-weight:bold;font-size:20px;padding:12px 26px 12px 18%;clip-path:polygon(0 0,88% 0,100% 50%,88% 100%,0 100%,10% 50%)}
.proc:first-child .chev{clip-path:polygon(0 0,88% 0,100% 50%,88% 100%,0 100%);padding-left:16px}.proc:nth-child(3) .chev{background:#002855}.proc:nth-child(4) .chev{background:#4f86b5}
:root[data-theme="dark"] .chev{background:#0d4a77}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .chev{background:#0d4a77}}
.chev span{display:block;font-size:14px;font-weight:normal}
.gate{display:flex;gap:8px;align-items:center;font-size:13px;margin:10px 0 4px;color:var(--muda)}.gate.si{color:var(--naranja);font-weight:bold}
.gate i,.g i{display:inline-block;width:12px;height:12px;transform:rotate(45deg);border:2px solid var(--muda);flex:none}.gate.si i,.g.si i{background:var(--naranja);border-color:var(--naranja)}
.proc .etapa{font-style:italic;color:var(--muda);font-size:13px;margin:4px 0}.proc .ag{color:var(--azul);font-weight:bold;font-size:14px;margin:0}.proc .prod{font-size:14px;margin:4px 0 8px}
.proc ul{list-style:none;padding:8px 10px;margin:0;background:var(--sup2);border-radius:8px;font-size:13px;color:var(--marino)}.proc li{overflow-wrap:anywhere}
.leyenda{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center;font-size:14px;color:var(--muda)}.leyenda b{color:var(--naranja)}.g{display:inline-flex;gap:8px;align-items:center}
/* controles */
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin:0 4px 0 0;vertical-align:-1px}.sw.perm{background:var(--perm)}.sw.otra{background:var(--otra);margin-left:12px}
.grafico{position:relative}.barras{display:flex;flex-direction:column;gap:2px}
.fila{display:grid;grid-template-columns:minmax(0,46%) 1fr;gap:10px;align-items:center;padding:2px 4px;border-radius:5px;outline:none;font-size:13px}
.fila:hover,.fila:focus{background:var(--sup2)}.fila .cat{text-align:right;color:var(--txt);overflow-wrap:anywhere}
.pista{display:flex;align-items:center;gap:6px;min-width:0}.barra{display:block;height:16px;border-radius:0 4px 4px 0;min-width:4px;flex:none}
.barra.perm{background:var(--perm)}.barra.otra{background:var(--otra)}.val{color:var(--txt2);font-size:13px}
.tip{position:absolute;pointer-events:none;background:var(--txt);color:var(--sup);font-size:13px;padding:6px 9px;border-radius:6px;max-width:300px;z-index:3}
.destaca{color:var(--marino);font-weight:bold}.pila{display:flex;flex-direction:column;gap:10px}
.cod{display:inline-block;background:var(--marino);color:var(--sup);font:bold 13px "Courier New",monospace;padding:3px 8px;border-radius:5px}.cas{color:var(--naranja)}
details{margin:8px 0;font-size:14px}summary{cursor:pointer;color:var(--azul)}
table{border-collapse:collapse;width:100%;font-size:14px}th{background:#002855;color:#fff;text-align:left;padding:7px 9px}td{border-bottom:1px solid var(--linea);padding:7px 9px;vertical-align:top}
td.n{text-align:center}table.cat td:first-child{white-space:nowrap}.scroll{overflow-x:auto;max-width:100%}table.cat{font-size:15px;margin-bottom:16px}
/* integraciones */
.hub{display:grid;grid-template-columns:1fr 200px 1fr;gap:16px;align-items:center}.hub-col{display:flex;flex-direction:column;gap:12px}
.centro{width:190px;height:190px;border-radius:50%;background:#002855;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:16px;margin:auto}
.centro b{font-size:24px}.centro span{color:var(--cielo);font-size:13px}.vals{color:var(--azul);font-weight:bold;font-size:13px}.card.calida .vals{color:var(--naranja)}
/* casos */
.caso{display:grid;grid-template-columns:1fr 1.15fr;gap:22px}.vin,.ind{margin:0 0 12px;padding-left:20px}.vin li,.ind li{margin:0 0 6px}
.ind{background:var(--sup2);border-radius:10px;padding:12px 14px 6px 32px;font-size:15px}.ind li::marker{color:var(--naranja)}
.foto{background:#fff;border:1px solid var(--linea);border-radius:10px;padding:6px}.foto img{width:100%;height:auto;display:block;border-radius:6px;cursor:zoom-in}
.foto figcaption{text-align:center;color:#696969;font-style:italic;font-size:13px;padding-top:4px}
.ficha{background:var(--tinta);color:var(--marino);border-radius:8px;padding:8px 12px;font-weight:bold;font-size:14px;overflow-wrap:anywhere}
/* calidad, empezar */
.vivo{list-style:none;padding:0;margin:0;font-size:14px}.vivo li{margin:0 0 6px}.vivo b{color:var(--naranja)}.vivo small{color:var(--muda)}
pre{background:var(--cod);color:var(--codtxt);border-radius:8px;padding:10px 12px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px;margin:0 0 12px}
.card h4{margin:10px 0 6px;color:var(--azul)}
/* comparativo */
.bajada{margin:0 0 12px;color:var(--txt2)}
table.cmp{font-size:14px;table-layout:fixed;min-width:640px}table.cmp thead th:first-child{width:15%}
table.cmp tbody th{background:var(--sup2);color:var(--marino);font-weight:bold;text-align:left;padding:7px 9px;border-bottom:1px solid var(--linea);vertical-align:top}
table.cmp th.pm{background:var(--azul)}table.cmp td.pm{background:var(--tinta);color:var(--marino)}
.nota.fuentes{font-size:13px;margin:10px 0 0}ul.fuentes{font-size:13px;overflow-wrap:anywhere;margin:6px 0 0}
table.conviene{font-size:14px}table.conviene td{background:var(--sup)}table.conviene td.conv{font-weight:bold;color:var(--marino);width:36%}
:root[data-theme="dark"] table.cmp th.pm{background:#0d4a77}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) table.cmp th.pm{background:#0d4a77}}
/* glosario */
.letras a{display:inline-block;margin:0 6px 6px 0;font-weight:bold}
.glosario{columns:2;column-gap:28px;margin:0}.glosario dt{font-weight:bold;color:var(--marino);break-after:avoid;margin-top:8px;scroll-margin-top:70px}
.glosario dd{margin:2px 0 6px;break-inside:avoid;font-size:15px}.glosario dt:target{background:var(--calida);border-radius:4px}
a.glos{text-decoration:underline dotted;text-underline-offset:3px;color:inherit;text-decoration-color:var(--glos)}
/* ampliar imagen */
.zoom{position:fixed;inset:0;background:rgba(0,0,0,.82);display:flex;align-items:center;justify-content:center;z-index:50;padding:16px;cursor:zoom-out}
.zoom img{max-width:100%;max-height:100%;background:#fff;border-radius:6px}
@media (max-width:900px){.agentes{grid-template-columns:repeat(3,1fr)}.ciclo{grid-template-columns:1fr 1fr}.kpis4{grid-template-columns:1fr 1fr}.cifras{grid-template-columns:repeat(3,1fr)}}
@media (max-width:720px){main{padding:12px 16px 40px}.slide{padding:16px 14px 10px;min-height:0}.sh{grid-template-columns:1fr}.sh .logo-ieee{display:none}.sh h2{font-size:19px}
.grid2,.grid3,.dos-col,.caso,.hub{grid-template-columns:1fr}.agentes{grid-template-columns:1fr 1fr}.ciclo{grid-template-columns:1fr}.kpis{grid-template-columns:1fr 1fr}
.pr-cab{display:none}.pr-fila{grid-template-columns:1fr;gap:4px;margin:12px 0}.pr-flecha{transform:rotate(90deg);height:22px}.pr-cod{justify-self:start;padding:4px 10px}
.portada h1{font-size:30px}.portada .sub{font-size:17px}.cifras{grid-template-columns:1fr 1fr}.cifra b{font-size:28px}.glosario{columns:1}.kpi b{font-size:28px}
table.cmp{min-width:0}table.cmp thead{display:none}table.cmp tr,table.cmp th,table.cmp td{display:block;width:auto}table.cmp tr{margin:0 0 10px;border:1px solid var(--linea);border-radius:8px;overflow:hidden}table.cmp td::before{content:attr(data-col);display:block;font-size:12px;font-weight:bold;color:var(--azul)}
.agente header{min-height:0}.agente ul{min-height:0}.centro{width:150px;height:150px}.barra .marca{display:none}.lema{font-size:16px}}
@media print{@page{size:A4 landscape;margin:10mm}:root{--bg:#fff;--sombra:none}body{background:#fff;font-size:12px}.barra,.zoom,details{display:none!important}
main{max-width:none;padding:0}.slide{break-after:page;page-break-after:always;margin:0;border-radius:0;box-shadow:none;min-height:0;padding:0 4mm;zoom:.74}.slide:last-child{break-after:auto;page-break-after:auto}
.slide.portada{-webkit-print-color-adjust:exact;print-color-adjust:exact}.sh h2,.capa,.chev,.dp,.agente header,.kpi.oscuro,.centro,th,.pr-cod,.cod,.cifra{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.agentes{grid-template-columns:repeat(6,1fr)}.foto img,.diag img{max-height:110mm;width:auto;max-width:100%;margin:auto}a.glos{text-decoration:none}}
"""

JS = r"""
(function(){
  var root=document.documentElement, KEY='pm-resumen-tema';
  function aplicar(t){ if(t==='light'||t==='dark'){root.setAttribute('data-theme',t);} else {root.removeAttribute('data-theme');}
    var b=document.getElementById('tema'); if(b){b.textContent={light:'Tema: claro',dark:'Tema: oscuro'}[t]||'Tema: automático';} }
  var t=null; try{t=localStorage.getItem(KEY);}catch(e){} aplicar(t);
  document.getElementById('tema').addEventListener('click',function(){ var orden=[null,'light','dark'];
    var cur=root.getAttribute('data-theme'); var sig=orden[(orden.indexOf(cur)+1)%3]; aplicar(sig);
    try{ if(sig){localStorage.setItem(KEY,sig);} else {localStorage.removeItem(KEY);} }catch(e){} });
  document.getElementById('imprimir').addEventListener('click',function(){window.print();});
  var sel=document.getElementById('ir'), slides=[].slice.call(document.querySelectorAll('section.slide'));
  sel.addEventListener('change',function(){ location.hash=sel.value; });
  function actual(){ var y=window.scrollY+90, k=0; slides.forEach(function(s,i){ if(s.offsetTop<=y){k=i;} }); return k; }
  function ir(d){ var k=Math.max(0,Math.min(slides.length-1,actual()+d)); slides[k].scrollIntoView({behavior:'smooth'}); sel.value=slides[k].id; }
  document.getElementById('ant').addEventListener('click',function(){ir(-1);});
  document.getElementById('sig').addEventListener('click',function(){ir(1);});
  document.addEventListener('keydown',function(ev){ if(ev.target.tagName==='SELECT'||ev.altKey||ev.ctrlKey||ev.metaKey){return;}
    if(ev.key==='ArrowRight'||ev.key==='PageDown'){ev.preventDefault();ir(1);} if(ev.key==='ArrowLeft'||ev.key==='PageUp'){ev.preventDefault();ir(-1);} });
  window.addEventListener('scroll',function(){ var k=actual(); if(sel.value!==slides[k].id){sel.value=slides[k].id;} },{passive:true});
  // tooltip del gráfico
  [].forEach.call(document.querySelectorAll('.grafico'),function(fig){ var tip=fig.querySelector('.tip');
    function mostrar(g,x,y){ tip.textContent=g.getAttribute('data-tip'); tip.hidden=false; var r=fig.getBoundingClientRect();
      var l=Math.min(x-r.left+12, r.width-tip.offsetWidth-4); tip.style.left=Math.max(0,l)+'px'; tip.style.top=(y-r.top+14)+'px'; }
    [].forEach.call(fig.querySelectorAll('.fila'),function(g){
      g.addEventListener('mousemove',function(ev){mostrar(g,ev.clientX,ev.clientY);});
      g.addEventListener('mouseleave',function(){tip.hidden=true;});
      g.addEventListener('focus',function(){ var b=g.getBoundingClientRect(); mostrar(g,b.left+b.width/2,b.top+b.height/2); });
      g.addEventListener('blur',function(){tip.hidden=true;}); }); });
  // ampliar imágenes
  [].forEach.call(document.querySelectorAll('.foto img,.diag img'),function(im){ im.addEventListener('click',function(){
    var z=document.createElement('div'); z.className='zoom'; z.setAttribute('role','dialog'); z.setAttribute('aria-label','Imagen ampliada');
    var c=document.createElement('img'); c.src=im.src; c.alt=im.alt; z.appendChild(c); z.addEventListener('click',function(){z.remove();});
    document.addEventListener('keydown',function esc(ev){ if(ev.key==='Escape'){z.remove(); document.removeEventListener('keydown',esc);} });
    document.body.appendChild(z); }); });
})();
"""

doc = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>pm-method · Resumen ejecutivo</title>
<meta name="description" content="Resumen ejecutivo comercial de pm-method {e(D['meta']['version'])}: propósito, alcance, agentes y skills, arquitectura, ciclo de vida, controles permanentes, integraciones, catálogo de casos E2E y comparativo con PMI Infinity y la gestión tradicional.">
<style>{CSS}</style></head>
<body>
<nav class="barra" aria-label="Navegación"><span class="marca">pm-method · Resumen ejecutivo</span>
<label class="vh" for="ir" style="position:absolute;left:-9999px">Ir a la diapositiva</label><select id="ir">{nav}</select>
<span class="flechas"><button id="ant" type="button" aria-label="Diapositiva anterior">◀</button><button id="sig" type="button" aria-label="Diapositiva siguiente">▶</button></span>
<button id="tema" type="button">Tema: automático</button><button id="imprimir" type="button">Imprimir</button></nav>
<main>{''.join(secciones)}</main>
<script>{JS}</script>
</body></html>
"""
SALIDA.write_text(doc, encoding="utf-8")
print(f"{SALIDA.relative_to(RAIZ)} · {len(SLIDES)} diapositivas · {len(doc) / 1e6:.2f} MB")
