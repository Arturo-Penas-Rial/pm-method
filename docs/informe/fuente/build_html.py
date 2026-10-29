"""Informe 2 · HTML. Uso: python3 build_html.py  (lee data.json y diagramas/; escribe salida-<versión>/informe-2-ecosistema-pm-method-<versión>.html)"""
import json, base64, html, pathlib, os, re, unicodedata

AQUI = pathlib.Path(__file__).resolve().parent
os.chdir(AQUI)
D = json.load(open("data.json", encoding="utf-8"))
X = D["x"]
Mt = D["meta"]
e = html.escape
LOGO = ("data:image/png;base64," + base64.b64encode(open("logo.png", "rb").read()).decode()) if os.path.exists("logo.png") else ""
VER = Mt["version"]                                   # "v2.6"
SALIDA = f"salida-{VER}/informe-2-ecosistema-pm-method-{VER}.html"
pathlib.Path(f"salida-{VER}").mkdir(exist_ok=True)


# ---------- Markdown mínimo (inline + bloques) ----------
def inl(s):
    """`code`, **negrita**, [texto](enlace) → HTML seguro."""
    codigos = []
    def guarda(m):
        codigos.append(m.group(1))
        return f"\x01{len(codigos) - 1}\x02"
    t = re.sub(r"`([^`]*)`", guarda, s or "")
    t = e(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*\\])\*([^\s*][^*]*?[^\s*\\]|[^\s*])\*(?![\w*])", r"<i>\1</i>", t)
    enl = []
    def guarda_enl(m):
        enl.append(m.group(0))
        return f"\x03{len(enl) - 1}\x04"
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", guarda_enl, t)
    # URL sueltas → enlace (las que están entre comillas invertidas quedan como código)
    t = re.sub(r"(https?://[^\s<>\"\x01\x03]+[^\s<>\"\x01\x03.,;:)*])", r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    def repone(m):
        x = enl[int(m.group(1))]
        x = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', x)
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<i>\1</i>", x)
    t = re.sub(r"\x03(\d+)\x04", repone, t)
    t = t.replace("&lt;br&gt;", "<br>")   # saltos de línea que la documentación escribe dentro de celdas de tabla
    return re.sub(r"\x01(\d+)\x02", lambda m: f"<code>{e(codigos[int(m.group(1))])}</code>", t)


def md(texto):
    lineas = (texto or "").split("\n")
    out, i = [], 0
    while i < len(lineas):
        l = lineas[i]
        s = l.strip()
        if s.startswith("```"):
            j = i + 1
            buf = []
            while j < len(lineas) and not lineas[j].strip().startswith("```"):
                buf.append(lineas[j])
                j += 1
            ind = len(l) - len(l.lstrip())
            out.append("<pre>" + e("\n".join(b[ind:] if b[:ind].strip() == "" else b for b in buf)) + "</pre>")
            i = j + 1
            continue
        if s.startswith("|"):
            j = i
            filas = []
            while j < len(lineas) and lineas[j].strip().startswith("|"):
                filas.append(lineas[j])
                j += 1
            cel = lambda x: [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", x.strip().strip("|"))]
            cab = cel(filas[0])
            cuerpo = [cel(f) for f in filas[2:]]
            out.append(tabla_html(cab, cuerpo))
            i = j
            continue
        m = re.match(r"^(#{2,4})\s+(.*)$", s)
        if m:
            out.append(f"<h4>{inl(m.group(2))}</h4>")
            i += 1
            continue
        if re.match(r"^(- |\* |\d+\. )", s):
            ordenada = bool(re.match(r"^\d+\. ", s))
            items, j = [], i
            while j < len(lineas):
                sj = lineas[j].strip()
                if re.match(r"^(- |\* |\d+\. )", sj) and (len(lineas[j]) - len(lineas[j].lstrip())) <= (len(l) - len(l.lstrip())):
                    items.append(re.sub(r"^(- |\* |\d+\. )", "", sj))
                elif sj and items and (lineas[j].startswith("  ") or lineas[j].startswith("\t")):
                    if sj.startswith("```"):
                        k = j + 1
                        buf = []
                        while k < len(lineas) and not lineas[k].strip().startswith("```"):
                            buf.append(lineas[k].strip("\n"))
                            k += 1
                        ind = len(lineas[j]) - len(lineas[j].lstrip())
                        items[-1] += "\x00PRE" + "\n".join(b[ind:] for b in buf)
                        j = k + 1
                        continue
                    sub = re.sub(r"^(- |\* )", "", sj)
                    ult = items[-1].rsplit("\x00", 1)
                    sep_txt = "\x00T " if len(ult) > 1 and ult[1].startswith("PRE") else " "
                    items[-1] += ("\x00LI" if re.match(r"^(- |\* )", sj) else sep_txt) + sub
                else:
                    break
                j += 1
            tag = "ol" if ordenada else "ul"
            def item_html(it):
                partes = re.split(r"(\x00PRE[^\x00]*|\x00LI[^\x00]*|\x00T[^\x00]*)", it)
                h, subs = "", []
                for p in partes:
                    if p.startswith("\x00PRE"):
                        h += "<pre>" + e(p[4:]) + "</pre>"
                    elif p.startswith("\x00LI"):
                        subs.append(p[3:])
                    elif p.startswith("\x00T"):
                        h += inl(p[2:])
                    else:
                        cb = re.match(r"^\[( |x)\] (.*)$", p)
                        h += ("☐ " + inl(cb.group(2))) if cb else inl(p)
                if subs:
                    h += "<ul>" + "".join(f"<li>{inl(x)}</li>" for x in subs) + "</ul>"
                return h
            out.append(f"<{tag}>" + "".join(f"<li>{item_html(it)}</li>" for it in items) + f"</{tag}>")
            i = j
            continue
        if s.startswith(">"):
            buf = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                buf.append(lineas[i].strip()[1:].strip())
                i += 1
            out.append('<div class="callout blue"><p>' + inl(" ".join(buf)) + "</p></div>")
            continue
        if not s or re.match(r"^-{3,}$", s):
            i += 1
            continue
        buf = []
        while i < len(lineas) and lineas[i].strip() and not re.match(r"^(```|\||#{2,4}\s|- |\* |\d+\. |>)", lineas[i].strip()):
            buf.append(lineas[i].strip())
            i += 1
        out.append("<p>" + inl(" ".join(buf)) + "</p>")
    return "\n".join(out)


def tabla_html(cab, filas, clase="", anchos=None, grupo_col=None):
    clase = (clase + (" ancha" if len(cab) >= 4 else "")).strip()
    h = [f'<div class="scroll"><table class="{clase}">']
    estilo = lambda k: f' style="width:{anchos[k]}"' if anchos and anchos[k] else ""   # sin barra invertida dentro del f-string (Python 3.9–3.11)
    h.append("<tr>" + "".join(f"<th{estilo(k)}>{inl(c)}</th>" for k, c in enumerate(cab)) + "</tr>")
    for f in filas:
        no_vacias = [c for c in f if c]
        if grupo_col is not None and len(no_vacias) == 1 and f[grupo_col] and f[grupo_col].startswith("**"):
            h.append(f'<tr class="grupo"><td colspan="{len(cab)}">{inl(f[grupo_col])}</td></tr>')
            continue
        h.append("<tr>" + "".join(f"<td>{inl(c)}</td>" for c in f) + "</tr>")
    h.append("</table></div>")
    return "".join(h)


def T(t, clase="", anchos=None, grupo_col=None):
    return tabla_html(t["cab"], t["filas"], clase, anchos, grupo_col)


def diag(id_):
    d = next(x for x in X["diagramas"] if x["id"] == id_)
    svg = (AQUI / "diagramas" / f"{id_}.svg").read_text(encoding="utf-8")
    svg = re.sub(r"^<\?xml[^>]*>", "", svg).strip()
    return f'<figure class="diag"><div class="diag-in">{svg}</div><figcaption>{e(d["titulo"])} · fuente: {e(d["origen"])}</figcaption></figure>'


def layers(items, clase="layers"):
    return f'<div class="{clase}">' + "".join(f'<div class="layer"><b>{inl(it["t"])}</b><p>{inl(it["d"])}</p></div>' for it in items) + "</div>"


def pre(t):
    return f"<pre>{e(t)}</pre>"


def link(u):
    return f'<a href="{e(u)}" target="_blank" rel="noopener">{e(u)}</a>'


SEC = []  # (id, etiqueta)


def sec(id_, num, titulo, cuerpo, audiencia=""):
    SEC.append((id_, f"{num} {titulo}" if num else titulo))
    aud = f'<p class="aud">Para: {e(audiencia)}</p>' if audiencia else ""
    k = [0]
    def _num(m):
        k[0] += 1
        return f"{m.group(1)}{num}.{k[0]} · "
    cuerpo = re.sub(r"(<h3[^>]*>)¶", _num, cuerpo)
    return f'<section id="{id_}"><h2>{e(num + " · " if num else "")}{e(titulo)}</h2>{aud}{cuerpo}</section>'


exec(open("cuerpo_html.py", encoding="utf-8").read())
tparts = Mt["titulo"].split(": ")
title_html = f"{e(tparts[0])}:<br><b>{e(tparts[1])}</b>"
toc = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in SEC)

CSS = """
:root{--navy:#002855;--blue:#00629b;--orange:#b5651d;--gray:#696969;--char:#272425;--page:#ffffff;--bg:#f4f6f8;--tint:#e9f1f8;--ortint:#fbf1e6;--line:#e2e2e6;
--head:#002855;--link:#00629b;--h2bg:#00629b;--hero:#002855;--kpi:#002855;--cod:#0f2238;--codtxt:#e8eef5;--sombra:0 2px 10px rgba(0,40,85,.05);--fig:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--char:#e7e9ec;--gray:#a3abb4;--page:#101418;--bg:#1a1f25;--tint:#16283a;--ortint:#2f2418;--line:#33404c;
--head:#9fc4ea;--link:#6fb3e6;--orange:#f0a463;--h2bg:#0d4a77;--hero:#0b2340;--kpi:#0b2340;--cod:#0b1520;--codtxt:#dfe8f2;--sombra:none}}
:root[data-theme="dark"]{--char:#e7e9ec;--gray:#a3abb4;--page:#101418;--bg:#1a1f25;--tint:#16283a;--ortint:#2f2418;--line:#33404c;
--head:#9fc4ea;--link:#6fb3e6;--orange:#f0a463;--h2bg:#0d4a77;--hero:#0b2340;--kpi:#0b2340;--cod:#0b1520;--codtxt:#dfe8f2;--sombra:none}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:Arial,Helvetica,sans-serif;font-weight:300;color:var(--char);background:var(--page);line-height:1.55;font-size:16px}
h1,h2,h3,h4{font-family:Arial,Helvetica,sans-serif;margin:0 0 .5em}
h1{font-weight:300;font-size:2.3rem;line-height:1.15} h1 b{font-weight:600}
h2{font-weight:600;font-size:1.45rem;color:#fff;background:var(--h2bg);display:inline-block;padding:.35em .9em;border-radius:10px;margin:0 0 .4em}
h3{font-weight:500;font-size:1.15rem;color:var(--head);margin-top:1.6em} h4{font-weight:600;font-size:1rem;color:var(--head);margin-top:1.1em}
a{color:var(--link);text-decoration:none;overflow-wrap:anywhere} a:hover{text-decoration:underline}
code{font-family:"Courier New",monospace;font-size:.88em;background:var(--bg);padding:.05em .3em;border-radius:4px;overflow-wrap:anywhere}
pre{font-family:"Courier New",monospace;font-size:.82rem;background:var(--cod);color:var(--codtxt);padding:14px 16px;border-radius:10px;overflow-x:auto;line-height:1.45;margin:10px 0 16px;white-space:pre}
#tema{position:fixed;top:10px;right:10px;z-index:10;font:600 .8rem Arial,Helvetica,sans-serif;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:var(--page);color:var(--char);cursor:pointer;opacity:.92}
.cover{background:var(--hero);color:#fff;padding:44px 7vw}
.cover img.logo{height:64px;margin-bottom:18px;display:block}
.logo-ieee{border:1.5px dashed #9fd0f0;color:#9fd0f0;border-radius:6px;font-size:12px;display:flex;align-items:center;justify-content:center;width:160px;height:62px;margin-bottom:18px}
.logo-ieee.pie{width:120px;height:44px;margin:0}
.cover .tag{display:inline-block;background:#00629b;padding:.3em .8em;border-radius:8px;font-weight:500;font-size:.85rem;margin:0 0 18px}
.cover p{max-width:900px;font-size:1.05rem;opacity:.92} .cover .meta{font-size:.9rem;opacity:.85;margin-top:24px;display:flex;gap:28px;flex-wrap:wrap}
.cover .meta a{color:inherit;text-decoration:underline;text-underline-offset:3px}
main{max-width:1200px;margin:0 auto;padding:36px 7vw 60px} section{margin:48px 0}
.aud{margin:0 0 1em;font-size:.85rem;color:var(--orange);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.intro{font-size:1.02rem;max-width:980px} .lema{font-size:1.25rem;font-weight:600;color:var(--head);margin:.2em 0 .8em}
ol.check{list-style:none;padding-left:0} ol.check li{margin:.45em 0;padding:6px 10px;background:var(--bg);border-radius:8px}
table.dep{min-width:1100px;font-size:.8rem} table.dep td{overflow-wrap:anywhere} .notice{background:var(--bg);border-radius:12px;padding:18px 22px;margin:24px 0} .notice b{color:var(--orange)}
.scroll{overflow-x:auto;margin:12px 0 20px}
table{border-collapse:collapse;width:100%;font-size:.9rem} td,th{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top} th{font-weight:600;color:var(--head);background:var(--bg)}
tr.grupo td{background:var(--tint);color:var(--head);font-weight:600}
table.raci{min-width:1250px;font-size:.78rem} table.raci td,table.raci th{padding:5px 5px;text-align:center} table.raci td:nth-child(2),table.raci th:nth-child(2),table.raci td:last-child{text-align:left} table.raci td:nth-child(2){min-width:220px}
table.raci2{min-width:1100px;font-size:.8rem} table.raci2 td{text-align:center} table.raci2 td:first-child,table.raci2 td:nth-child(2),table.raci2 td:last-child{text-align:left}
table.dec{min-width:900px} table.scripts td:last-child{font-size:.82rem}
table.codigos td:first-child{white-space:nowrap}
ul{padding-left:1.2em} li{margin:.3em 0} ul.res li{margin:.55em 0}
.callout{border-radius:14px;padding:18px 22px;margin:18px 0} .callout.blue{background:var(--tint)} .callout.orange{background:var(--ortint)} .callout.orange h4{color:var(--orange)}
.callout.navy{background:var(--hero);color:#fff} .callout.navy p{margin:0} .callout.navy code{background:#173d66;color:#fff}
.callout p{margin:.3em 0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:22px} .two>*{min-width:0} @media(max-width:860px){.two{grid-template-columns:1fr}}
.layers{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;margin:12px 0 18px} .layer{border-radius:12px;padding:14px 18px;background:var(--tint)} .layer b{font-weight:600;color:var(--link)} .layer p{margin:.3em 0 0;font-size:.94rem}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:8px 0 20px} @media(max-width:700px){.kpis{grid-template-columns:1fr 1fr}}
.kpi{background:var(--kpi);color:#fff;border-radius:12px;padding:16px 16px 14px;display:flex;flex-direction:column;min-width:0}
.kpi .v{font-size:2rem;font-weight:600;line-height:1.1;overflow-wrap:anywhere} .kpi .t{font-weight:600;color:#9fd0f0;margin:.2em 0} .kpi .d{font-size:.82rem;opacity:.85}
figure.diag{width:min(calc(100vw - 32px),1500px);position:relative;left:50%;transform:translateX(-50%);margin:18px 0 24px;border:1px solid var(--line);border-radius:12px;padding:12px;background:var(--fig)}
figure.diag figcaption{color:#5a5a5a}
.diag-in{overflow-x:auto} .diag-in svg{display:block;margin:0 auto;max-width:100%;height:auto} @media(max-width:860px){.diag-in svg{max-width:none;min-width:680px}}
figcaption{font-size:.82rem;color:var(--gray);margin-top:8px;text-align:center}
img.captura{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:10px;background:#fff}
.galeria{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;margin:10px 0 22px} .galeria figure{margin:0;min-width:0} .galeria figcaption{text-align:left}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:12px;padding:16px 18px;box-shadow:var(--sombra);font-size:.9rem;min-width:0}
.card h4{margin:0 0 .4em;font-size:1rem} .card ul{margin:.4em 0;padding-left:1.1em} .card li{margin:.25em 0}
.card .tema{color:var(--orange);font-weight:600;margin:.1em 0 .4em;font-size:.88rem} .card .usar{background:var(--bg);border-radius:8px;padding:8px 10px;margin:.6em 0 0}
.caso{margin:12px 0} .caso dl{display:grid;grid-template-columns:180px 1fr;gap:6px 14px;margin:.6em 0 0} .caso dt{font-weight:600;color:var(--head)} .caso dd{margin:0;min-width:0}
@media(max-width:700px){.caso dl{grid-template-columns:1fr} .caso dt{margin-top:6px}}
.num{display:inline-flex;align-items:center;justify-content:center;min-width:28px;height:28px;border-radius:8px;background:var(--kpi);color:#fff;font-size:.85rem;margin-right:6px;padding:0 6px}
h4.parte{margin-top:1.6em;color:var(--orange);text-transform:uppercase;letter-spacing:.03em;font-size:.9rem}
details{margin-top:8px} summary{cursor:pointer;color:var(--link);font-weight:600}
.steps .step{display:flex;gap:16px;margin:14px 0} .steps .step>span{flex:0 0 38px;height:38px;border-radius:10px;background:var(--h2bg);color:#fff;font-weight:600;display:flex;align-items:center;justify-content:center} .steps .step>div{min-width:0;flex:1}
.steps h4{margin-top:.4em}
ul.cols{columns:3;font-size:.86rem} @media(max-width:700px){ul.cols{columns:1}}
.src{font-size:.82rem;color:var(--gray)}
footer{background:var(--hero);color:#fff;padding:28px 7vw;font-size:.85rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px} footer img{height:40px}
.toc{display:flex;flex-wrap:wrap;gap:6px 8px} .toc a{display:inline-block;padding:4px 10px;border-radius:8px;background:var(--bg);font-weight:500;font-size:.86rem;overflow-wrap:normal}
@media(max-width:600px){table.ancha{min-width:640px} main{padding:24px 16px 48px} .cover{padding:52px 16px 32px} h1{font-size:1.7rem} h2{font-size:1.2rem} .cards,.galeria{grid-template-columns:1fr} pre{font-size:.75rem} .layers{grid-template-columns:1fr} .kpi .v{font-size:1.6rem}}
@media print{#tema{display:none}.cover,.kpi,h2,pre,.callout.navy{-webkit-print-color-adjust:exact;print-color-adjust:exact} .card,figure{break-inside:avoid} details{display:block}}
"""

JS = r"""
(function(){
  var root=document.documentElement, KEY='pm-informe2-tema', b=document.getElementById('tema');
  function aplicar(t){ if(t==='light'||t==='dark'){root.setAttribute('data-theme',t);} else {root.removeAttribute('data-theme');}
    if(b){b.textContent={light:'Tema: claro',dark:'Tema: oscuro'}[t]||'Tema: automático';} }
  var t=null; try{t=localStorage.getItem(KEY);}catch(e){} aplicar(t);
  if(b){b.addEventListener('click',function(){ var orden=[null,'light','dark'];
    var cur=root.getAttribute('data-theme'); var sig=orden[(orden.indexOf(cur)+1)%3]; aplicar(sig);
    try{ if(sig){localStorage.setItem(KEY,sig);} else {localStorage.removeItem(KEY);} }catch(e){} });}
})();
"""

page = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(Mt['corto'])}</title><meta name="color-scheme" content="light dark"><style>{CSS}</style></head>
<body>
<button id="tema" type="button" aria-label="Cambiar el tema">Tema: automático</button>
<header class="cover">
  {('<img class="logo" src="' + LOGO + '" alt="IEEE">') if LOGO else '<div class="logo-ieee" aria-label="Espacio para el logo de IEEE">Logo IEEE</div>'}
  <div><span class="tag">{e(Mt['tag'])} · {e(Mt['version'])}</span></div>
  <h1>{title_html}</h1>
  <p>{e(Mt['subtitulo'])}</p>
  <div class="meta"><span>{('<a href="' + e(Mt['autor_url']) + '" target="_blank" rel="noopener">' + e(Mt['autor']) + '</a>') if Mt.get('autor_url') else e(Mt['autor'])}</span><span>{e(Mt['fecha'])}</span></div>
</header>
<main>
<nav class="toc">{toc}</nav>
<div class="notice"><b>Alcance y método.</b> {e(Mt['alcance'])}</div>
{cuerpo}
</main>
<footer>{('<img src="' + LOGO + '" alt="IEEE">') if LOGO else '<div class="logo-ieee pie" aria-hidden="true">Logo IEEE</div>'}<span>{e(Mt['corto'])} · {e(Mt['version'])} · {e(Mt['fecha'])} · {e(Mt['autor'])}</span></footer>
<script>{JS}</script>
</body></html>"""
pathlib.Path(SALIDA).write_text(page, encoding="utf-8")
print("html ok", SALIDA, len(page))
