"""Presentaciones light de pm-method para IEEE · HTML autocontenido.

Uso: python3 build_html.py resumen|informe   (lee datos-<nombre>.json; escribe ../pm-method-ieee-<nombre>-light.html)
Un solo archivo: CSS y JS en línea, imágenes como data URI; tema claro, oscuro o automático; imprimible (una
diapositiva por página apaisada); navegación con ◀ ▶ y las flechas del teclado; notas del orador plegables (tecla N).
Mismo contenido que el PPTX (build_pptx.js) y la estética del resumen ejecutivo.
"""
import base64, html, json, pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
if len(sys.argv) != 2 or sys.argv[1] not in ("resumen", "informe"):
    sys.exit("uso: python3 build_html.py resumen|informe")
D = json.loads((AQUI / f"datos-{sys.argv[1]}.json").read_text(encoding="utf-8"))
SALIDA = AQUI.parent / f"{D['meta']['archivo']}.html"
e = html.escape


def data_uri(rel):
    return "data:image/png;base64," + base64.b64encode((RAIZ / rel).read_bytes()).decode()


def cap(t):
    return t[:1].upper() + t[1:]


def siglas():
    filas = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in D["siglas"])
    return (f'<aside class="siglas" aria-label="{e(D["siglas_titulo"])}"><h3>{e(D["siglas_titulo"])}</h3>'
            f'<dl>{filas}</dl><p class="marcas">{e(D["siglas_nota"])}</p></aside>')


def figura(d, clase="foto"):
    return (f'<figure class="{clase}"><img src="{data_uri(d["imagen"])}" alt="{e(d["pie"])}">'
            f'<figcaption>{e(d["pie"])}</figcaption></figure>')


P = D["programa"]
R = {}


def portada(d):
    cards = "".join(f'<div class="pc"><b>{e(t)}</b><span>{e(x)}</span></div>' for t, x in d["tarjetas"])
    return (f'<div class="logo-ieee logo-portada" aria-label="Espacio para el logo de IEEE">Logo IEEE</div>'
            f'<p class="kicker claro">{e(d["kicker"])}</p><h1>{e(d["titulo"])}</h1><p class="sub">{e(d["subtitulo"])}</p>'
            f'<div class="pcards">{cards}</div><p class="fecha">pm-method {e(D["meta"]["version"])} · {e(D["meta"]["portada_linea"])}</p>')


def antes_despues(d):
    filas = "".join(f'<div class="ad"><div class="hoy">{e(h)}</div><div class="fl" aria-hidden="true">→</div><div class="con">{e(c)}</div></div>'
                    for h, c in d["filas"])
    return (f'<div class="ad cab"><span>{e(d["col_hoy"])}</span><span></span><span class="azul">{e(d["col_con"])}</span></div>'
            f'{filas}<p class="lema">{e(d["lema"])}</p>')


def flujo_siglas(d):
    pasos = "".join(f'<li class="{"dec" if i == 1 else ""}"><span class="num">{i + 1}</span><b>{e(t)}</b><p>{e(x)}</p></li>'
                    for i, (t, x) in enumerate(d["pasos"]))
    ven = "".join(f'<div class="card {"tinta" if i % 3 == 0 else "calida"}"><b>✓ {e(t)}</b><p>{e(cap(x))}</p></div>'
                  for i, (t, x) in enumerate(d["ventajas"]))
    return (f'<div class="con-siglas"><div><ol class="flujo">{pasos}</ol><p class="rot azul">{e(d["ventajas_titulo"])}</p>'
            f'<div class="grid2">{ven}</div></div>{siglas()}</div>')


def programa(d):
    bloques = []
    for m in P["modulos"]:
        nuevo = m["material"] != "existente"
        rot = "Inicio" if m["id"] == "M0" else "Cierre" if m["id"] == "TI" else f"Taller {m['id'][1:]}"
        lema = m["lema"] + (f" · {m['caso']}" if m.get("caso") else "")
        bloques.append(f'<li class="{"nuevo" if nuevo else ""}"><header><span>{e(rot)}</span><b>{m["sesiones"]}</b> sesiones</header>'
                       f'<div><b>{e(m["nombre"])}</b><i>{e(lema)}</i></div></li>')
    det = "".join(f'<div class="card gris"><b class="naranja">{e(m["nombre"])}</b><p>{e(m["detalle"])}</p></div>'
                  for m in P["modulos"] if m["material"] != "existente")
    ritmo = "".join(f'<div class="ritmo {"calida" if i else "tinta"}"><b>{e(v)}</b><span>{e(r)}</span></div>'
                    for i, (r, v) in enumerate(P["ritmo_total"]))
    return (f'<ol class="timeline">{"".join(bloques)}</ol>'
            f'<p class="leyenda"><span class="it"><span class="sw existente"></span> material ya listo (guía, ejercicio y diapositivas)</span>'
            f'<span class="it"><span class="sw nuevo"></span> a preparar para IEEE</span> <i>{e(d["rotulo"])}</i></p>'
            f'<div class="grid2">{det}</div>'
            f'<div class="calc-fila"><div class="calc"><b>{"<br>".join(e(x) for x in d["calculo"])}</b><p>{e(d["material"])}</p></div>{ritmo}</div>')


def piloto(d):
    pasos = "".join(f'<li class="{"opc" if p["opcional"] else ""}"><span class="ses">{e(p["sesiones"])}{" · opcional" if p["opcional"] else ""}</span>'
                    f'<b>{e(p["nombre"])}</b><p>{e(cap(p["detalle"]))}</p></li>' for p in P["pasos_piloto"])
    calc = "".join(f'<div class="pc2 {"osc" if i == 0 else ""}"><b>{e(c["rot"])}: {e(c["cuenta"])}</b><span>{e(c["ritmo"])}</span></div>'
                   for i, c in enumerate(P["calculo_piloto"]))
    return (f'<div class="dos"><div><ol class="pasos">{pasos}</ol>{calc}</div>'
            f'<div>{figura(d)}<p class="lema chico">{e(d["despues"])}</p></div></div>')


def problemas(d):
    cards = "".join(f'<div class="prob"><span class="num">{i + 1}</span><p class="rot gris">{e(d["rot_problema"])}</p><b>{e(p)}</b>'
                    f'<div class="resp"><p class="rot azul">→ {e(d["rot_respuesta"])}</p><p>{e(r)}</p></div></div>'
                    for i, (p, r) in enumerate(d["tarjetas"]))
    return f'<div class="grid2">{cards}</div>'


def capas_siglas(d):
    capas = "".join(f'<div class="capa c{i}"><b>{i + 1} · {e(t)}</b><span>{e(cap(x))}</span></div>' for i, (t, x) in enumerate(d["capas"]))
    return f'<div class="con-siglas"><div><p class="rot">{e(d["rotulo"])}</p><div class="capas">{capas}</div></div>{siglas()}</div>'


def roles(d):
    c = lambda k, cl: f'<div class="rol {cl}"><b>{e(d[k][0])}</b><p>{e(cap(d[k][1]))}</p></div>'
    ay = "".join(f"<span>{e(a)}</span>" for a in d["ayudantes"])
    return (f'<div class="roles-a">{c("persona", "calida")}<span class="fl" aria-hidden="true">⇄</span>{c("coordinador", "marino")}'
            f'<span class="fl" aria-hidden="true">→</span>{c("registrador", "naranja")}</div>'
            f'<div class="fl abajo" aria-hidden="true">↓</div>'
            f'<div class="ayud"><b>{e(d["ayudantes_titulo"])}</b><div>{ay}</div></div>'
            f'<div class="fl abajo" aria-hidden="true">↓</div>'
            f'<div class="grid2">{c("guardian", "gris punteado")}{c("archivos", "gris")}</div>')


def puertas(d):
    etapas = "".join(f'<li><div class="chev"><b>{e(t)}</b><span>{e(x)}</span></div><div class="gate"><i aria-hidden="true"></i>{e(g)}</div></li>'
                     for (t, x), g in zip(d["etapas"], d["puertas"]))
    ver = "".join(f'<div class="vc"><span class="num">{i + 1}</span><b>{e(t)}</b><p>{e(cap(x))}</p></div>' for i, (t, x) in enumerate(d["verif"]))
    return (f'<ol class="etapas">{etapas}</ol><p class="leyenda"><span class="it"><span class="g"><i></i></span> puerta: decide una persona con autoridad (la «junta»)</span></p>'
            f'<p class="rot marino">{e(d["verif_titulo"])}</p><div class="verif">{ver}'
            f'<div class="vc dec"><b>{e(d["decision"][0])}</b><p>{e(cap(d["decision"][1]))}</p></div></div>'
            f'<p class="lema chico">{e(d["excepcion"])}</p>')


def imagen_puntos(d):
    pts = "".join(f'<li class="{"calida" if i % 2 else "tinta"}"><span class="num">{i + 1}</span>{e(p)}</li>' for i, p in enumerate(d["puntos"]))
    return f'<div class="img-pts"><div>{figura(d)}</div><div><p class="rot azul">{e(d["puntos_titulo"])}</p><ol class="pts">{pts}</ol></div></div>'


def ventajas(d):
    cards = "".join(f'<div class="card {"calida" if i in (1, 2) else "tinta"} vt"><span class="num">{i + 1}</span><b>{e(t)}</b><p>{e(x)}</p></div>'
                    for i, (t, x) in enumerate(d["tarjetas"]))
    return f'<div class="grid2">{cards}</div><p class="calidad">✓ {e(d["calidad"])}</p><p class="abierto">{e(d["abierto"])}</p>'


def cierre(d):
    lim = "".join(f"<li>{e(t)}</li>" for t in d["col1"])
    casos = "".join(f'<li><span class="num">{i + 1}</span><b>{e(c["nombre"])}</b><i>{e(c["lema"])} · caso {e(c["caso"])}</i></li>'
                    for i, c in enumerate(D["casos"]))
    return (f'<div class="grid2"><div class="card gris"><p class="rot marino">{e(d["col1_titulo"])}</p><ul class="lim">{lim}</ul></div>'
            f'<div class="card tinta"><p class="rot azul">{e(d["col2_titulo"])}</p><ol class="casos">{casos}</ol></div></div>'
            f'<p class="lema chico">{e(d["siguiente"])}</p>')


R.update(portada=portada, antes_despues=antes_despues, flujo_siglas=flujo_siglas, programa=programa, piloto=piloto,
         problemas=problemas, capas_siglas=capas_siglas, roles=roles, puertas=puertas, imagen_puntos=imagen_puntos,
         ventajas=ventajas, cierre=cierre)

N = len(D["diapositivas"])
secciones, opciones = [], []
for i, d in enumerate(D["diapositivas"], 1):
    cuerpo = R[d["tipo"]](d)
    es_portada = d["tipo"] == "portada"
    cab = "" if es_portada else f'<header class="sh"><h2>{e(d["titulo"])}</h2><div class="logo-ieee" aria-hidden="true">Logo IEEE</div></header>'
    nota = f'<details class="nota-orador"><summary>Notas del orador</summary><p>{e(d["nota"])}</p></details>' if d.get("nota") else ""
    pie = "" if es_portada else f'<footer class="sf"><span>{e(D["meta"]["pie"])}</span><span>{i} / {N}</span></footer>'
    secciones.append(f'<section class="slide {"portada" if es_portada else ""} t-{d["tipo"]}" id="d-{i}" aria-label="Diapositiva {i}">'
                     f'{cab}<div class="sb">{cuerpo}</div>{pie}</section>{nota}')
    opciones.append(f'<option value="d-{i}">{i} · {e(d["titulo"][:70])}</option>')

CSS = r"""
:root{--bg:#eef1f4;--sup:#ffffff;--sup2:#f4f6f8;--tinta:#e9f1f8;--calida:#fbf1e6;--txt:#272425;--muda:#696969;
--marino:#17324d;--azul:#2b6a9a;--naranja:#b5651d;--linea:#d5dce3;--hero:#17324d;--hero2:#22476e;--cielo:#9fd0f0;
--banda:#2b6a9a;--solido:#17324d;--solido2:#2b6a9a;--solido3:#5b8db8;--sombra:0 1px 3px rgba(0,0,0,.08),0 6px 18px rgba(0,40,85,.06)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#101418;--sup:#1a1f25;--sup2:#222930;--tinta:#16283a;--calida:#2f2418;
--txt:#e7e9ec;--muda:#9aa3ad;--marino:#9fc4ea;--azul:#6fb3e6;--naranja:#f0a463;--linea:#33404c;--hero:#0b2340;--hero2:#14365c;
--banda:#0d4a77;--solido:#0b2a4a;--solido2:#0d4a77;--solido3:#2f5f8a;--sombra:none}}
:root[data-theme="dark"]{--bg:#101418;--sup:#1a1f25;--sup2:#222930;--tinta:#16283a;--calida:#2f2418;--txt:#e7e9ec;--muda:#9aa3ad;
--marino:#9fc4ea;--azul:#6fb3e6;--naranja:#f0a463;--linea:#33404c;--hero:#0b2340;--hero2:#14365c;--banda:#0d4a77;--solido:#0b2a4a;
--solido2:#0d4a77;--solido3:#2f5f8a;--sombra:none}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--bg);color:var(--txt);font:17px/1.45 Arial,Helvetica,sans-serif;-webkit-text-size-adjust:100%}
.barra{position:sticky;top:0;z-index:10;display:flex;gap:10px;align-items:center;padding:8px 16px;background:var(--hero);color:#fff;flex-wrap:wrap}
.barra .marca{font-weight:bold;white-space:nowrap}.barra select{flex:1 1 200px;width:0;min-width:0;max-width:520px;font:inherit;font-size:14px;padding:5px 6px;border-radius:6px;border:0}
.barra button{font:inherit;font-size:14px;padding:5px 10px;border-radius:6px;border:1px solid rgba(255,255,255,.5);background:transparent;color:#fff;cursor:pointer}
.barra button:hover{background:rgba(255,255,255,.12)}.barra .flechas{display:flex;gap:6px}
main{max-width:1180px;margin:0 auto;padding:20px 16px 60px}
.slide{background:var(--sup);border-radius:14px;box-shadow:var(--sombra);margin:0 0 10px;padding:26px 30px 14px;display:flex;flex-direction:column;min-height:600px}
.sb{flex:1}.sh{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center;margin-bottom:18px}
.sh h2{margin:0;padding:12px 18px;border-radius:10px;background:var(--banda);color:#fff;font-size:25px;line-height:1.25}
.logo-ieee{border:1.5px dashed var(--muda);color:var(--muda);border-radius:6px;font-size:12px;display:flex;align-items:center;justify-content:center;width:130px;height:56px}
.sf{display:flex;justify-content:space-between;color:var(--muda);font-size:12px;border-top:1px solid var(--linea);padding-top:8px;margin-top:16px}
.nota-orador{max-width:1180px;margin:0 0 26px;font-size:15px;color:var(--muda)}.nota-orador summary{cursor:pointer;color:var(--azul)}
.nota-orador p{margin:6px 0 0;background:var(--sup);border-radius:8px;padding:10px 14px;color:var(--txt)}
.rot{font-size:12px;letter-spacing:.07em;text-transform:uppercase;font-weight:bold;color:var(--naranja);margin:0 0 8px}
.rot.azul{color:var(--azul)}.rot.marino{color:var(--marino)}.rot.gris{color:var(--muda)}.naranja{color:var(--naranja)}
.kicker{font-size:13px;letter-spacing:.06em;font-weight:bold}
.num{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;background:var(--marino);color:var(--sup);font-weight:bold;flex:none}
.card{border-radius:12px;padding:14px 18px}.card p{margin:4px 0 0}.card.tinta{background:var(--tinta)}.card.calida{background:var(--calida)}.card.gris{background:var(--sup2)}
.card b{color:var(--marino)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}.dos{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.lema{background:var(--calida);color:var(--naranja);border-radius:10px;padding:12px 18px;font-weight:bold;font-style:italic;font-size:20px;margin:16px 0 0}
.lema.chico{font-size:17px;font-style:normal}
figure{margin:0}.foto{background:#fff;border:1px solid var(--linea);border-radius:10px;padding:6px}.foto img{width:100%;height:auto;display:block;border-radius:6px;cursor:zoom-in}
.foto figcaption{color:#696969;font-style:italic;font-size:14px;padding:6px 4px 2px}
/* portada */
.slide.portada{background:var(--hero);color:#fff;padding:34px 40px 18px}.portada .sf{color:var(--cielo);border-color:rgba(255,255,255,.2)}
.portada .logo-ieee{border-color:var(--cielo);color:var(--cielo);width:160px;height:62px}.kicker.claro{color:var(--cielo);margin-top:28px;font-size:16px}
.portada h1{font-size:42px;line-height:1.15;margin:8px 0 14px;max-width:1000px}.portada .sub{font-size:21px;max-width:920px;margin:0 0 26px}
.pcards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.pc{background:var(--hero2);border-radius:10px;padding:14px 18px}
.pc b{display:block;font-size:18px;margin-bottom:4px}.pc span{color:var(--cielo);font-size:16px}.portada .fecha{margin:22px 0 0;color:var(--cielo);font-size:14px}
/* antes y después */
.ad{display:grid;grid-template-columns:1fr 44px 1.08fr;gap:8px;margin:10px 0}.ad.cab span{font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:.07em;color:var(--muda)}
.ad.cab .azul{color:var(--azul)}.hoy,.con{border-radius:9px;padding:14px 18px;font-size:18px}.hoy{background:var(--sup2)}.con{background:var(--tinta);color:var(--marino);font-weight:bold}
.fl{display:flex;align-items:center;justify-content:center;color:var(--naranja);font-weight:bold;font-size:26px}
/* flujo y siglas */
.con-siglas{display:grid;grid-template-columns:1.65fr 1fr;gap:24px;align-items:start}
.flujo{list-style:none;padding:0;margin:0 0 18px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;text-align:center}
.flujo li{position:relative}.flujo .num{width:76px;height:76px;font-size:30px;margin:0 auto 8px}.flujo li.dec .num{background:var(--naranja)}
.flujo li:not(:last-child)::after{content:"→";position:absolute;right:-16px;top:22px;font-size:26px;color:var(--muda)}
.flujo b{display:block;font-size:20px;color:var(--marino)}.flujo li.dec b{color:var(--naranja)}.flujo p{margin:4px 0 0;font-size:16px}
.siglas{background:var(--sup2);border:1px solid var(--linea);border-radius:12px;padding:16px 18px}.siglas h3{margin:0 0 8px;color:var(--marino);font-size:18px}
.siglas dl{margin:0}.siglas dt{font-weight:bold;color:var(--marino);margin-top:8px}.siglas dd{margin:0;font-size:15px}.marcas{font-size:12px;font-style:italic;color:var(--muda);margin:12px 0 0}
/* programa */
.timeline{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(7,1fr);gap:8px}
.timeline li{display:flex;flex-direction:column;border-radius:10px;overflow:hidden;background:var(--tinta)}.timeline li.nuevo{background:var(--calida)}
.timeline header{background:var(--solido);color:#fff;padding:8px 10px;font-size:13px}.timeline li.nuevo header{background:#b5651d}
.timeline header span{display:block;color:var(--cielo);font-weight:bold}.timeline li.nuevo header span{color:#fff2e6}.timeline header b{font-size:28px}
.timeline li>div{padding:8px 10px;display:flex;flex-direction:column;justify-content:space-between;flex:1;gap:6px}
.timeline li>div b{color:var(--marino);font-size:15px;line-height:1.25}.timeline i{color:var(--muda);font-size:13px}
.leyenda{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-size:14px;color:var(--txt);margin:12px 0}.leyenda i{color:var(--muda)}
.sw{display:inline-block;width:13px;height:13px;border-radius:3px;vertical-align:-1px;outline:1px solid var(--linea)}.leyenda .it{display:inline-flex;gap:6px;align-items:center}.sw.existente{background:#17324d}.sw.nuevo{background:#b5651d}
.calc-fila{display:grid;grid-template-columns:2fr 1fr 1fr;gap:14px;margin-top:14px}
.calc{background:#17324d;color:#fff;border-radius:12px;padding:14px 18px}.calc b{font-size:20px}.calc p{margin:8px 0 0;font-size:14px;color:#dce8f3}
.ritmo{border-radius:12px;padding:14px 18px}.ritmo.tinta{background:var(--tinta)}.ritmo.calida{background:var(--calida)}
.ritmo b{display:block;font-size:34px;color:var(--marino)}.ritmo.calida b{color:var(--naranja)}
/* piloto */
.pasos{list-style:none;padding:0;margin:0 0 12px;display:flex;flex-direction:column;gap:10px}
.pasos li{border-radius:10px;padding:12px 16px;background:var(--tinta)}.pasos li:first-child{background:var(--calida)}
.pasos li.opc{background:transparent;border:1.5px dashed var(--muda)}
.pasos .ses{display:block;color:var(--naranja);font-weight:bold;font-size:14px}.pasos b{display:block;color:var(--marino);font-size:18px}.pasos p{margin:4px 0 0;font-size:15px}
.pc2{border-radius:10px;padding:10px 16px;margin-top:8px;background:var(--sup2)}.pc2 b{display:block;color:var(--marino)}.pc2 span{font-size:14px;color:var(--muda)}
.pc2.osc{background:#17324d}.pc2.osc b{color:#fff}.pc2.osc span{color:#dce8f3}
/* problemas */
.prob{position:relative;background:var(--sup2);border-radius:12px;padding:16px 18px 16px 66px}.prob .num{position:absolute;left:16px;top:16px}
.prob>b{display:block;font-size:18px;margin-bottom:12px}.resp{background:var(--tinta);border-radius:9px;padding:10px 14px;margin-left:-48px}.resp p{margin:0;color:var(--marino)}
.resp p.rot{margin-bottom:4px;color:var(--azul)}
/* capas */
.capas{display:flex;flex-direction:column;gap:10px}.capa{border-radius:10px;padding:14px 18px;color:#fff}.capa b{display:block;font-size:20px}.capa span{font-size:16px}
.capa.c0{background:#17324d}.capa.c1{background:#2b6a9a;margin-left:22px}.capa.c2{background:#5b8db8;margin-left:44px}.capa.c3{background:var(--tinta);color:var(--marino);margin-left:66px}
/* roles */
.roles-a{display:grid;grid-template-columns:1fr 40px 1.2fr 40px 1.1fr;gap:6px;align-items:stretch}
.rol{border-radius:12px;padding:14px 18px}.rol b{display:block;font-size:18px}.rol p{margin:6px 0 0;font-size:16px}
.rol.calida{background:var(--calida)}.rol.calida b{color:var(--naranja)}.rol.marino{background:#17324d;color:#fff}.rol.marino p{color:#dce8f3}
.rol.naranja{background:#b5651d;color:#fff}.rol.gris{background:var(--sup2)}.rol.gris b{color:var(--marino)}.rol.punteado{border:1.5px dashed var(--muda)}
.fl.abajo{color:var(--muda);height:34px}
.ayud{background:var(--tinta);border-radius:12px;padding:14px 18px;margin:0 8%}.ayud>b{color:var(--marino);font-size:17px}
.ayud div{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:10px}.ayud span{background:var(--solido2);color:#fff;font-weight:bold;text-align:center;border-radius:8px;padding:12px 6px}
/* puertas */
.etapas{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.chev{background:var(--solido2);color:#fff;padding:14px 30px 14px 22px;clip-path:polygon(0 0,90% 0,100% 50%,90% 100%,0 100%,8% 50%);min-height:84px}
.etapas li:first-child .chev{clip-path:polygon(0 0,90% 0,100% 50%,90% 100%,0 100%);padding-left:16px}.etapas li:nth-child(3) .chev{background:var(--solido)}.etapas li:nth-child(4) .chev{background:var(--solido3)}
.chev b{display:block;font-size:19px}.chev span{font-size:14px}
.gate{display:flex;gap:8px;align-items:center;color:var(--naranja);font-weight:bold;font-size:15px;margin-top:8px}
.gate i,.g i{display:inline-block;width:13px;height:13px;transform:rotate(45deg);background:var(--naranja);flex:none}
.verif{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.vc{background:var(--tinta);border-radius:12px;padding:14px 16px}
.vc .num{width:30px;height:30px;margin-right:8px}.vc b{color:var(--marino);font-size:17px}.vc p{margin:8px 0 0;font-size:15px}
.vc.dec{background:#b5651d;color:#fff}.vc.dec b{color:#fff}
/* imagen y puntos */
.img-pts{display:grid;grid-template-columns:1.7fr 1fr;gap:24px;align-items:start}
.pts{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px}.pts li{display:flex;gap:12px;align-items:center;border-radius:10px;padding:14px 16px;color:var(--marino);font-size:17px}
.pts li.tinta{background:var(--tinta)}.pts li.calida{background:var(--calida)}.pts li.calida .num{background:var(--naranja)}
/* ventajas */
.vt{position:relative;padding-left:66px}.vt .num{position:absolute;left:16px;top:14px}.vt.calida .num{background:var(--naranja)}.vt b{font-size:19px}
.calidad{background:#17324d;color:#fff;font-weight:bold;border-radius:10px;padding:12px 18px;margin:16px 0 0;font-size:17px}
.abierto{background:var(--sup2);color:var(--marino);border-radius:10px;padding:10px 18px;margin:10px 0 0}
/* cierre */
.lim{margin:0;padding-left:20px}.lim li{margin:0 0 10px}.lim li::marker{color:var(--naranja)}
.casos{list-style:none;padding:0;margin:0}.casos li{display:grid;grid-template-columns:auto 1fr;gap:0 12px;margin-bottom:10px}.casos .num{grid-row:span 2}
.casos b{color:var(--marino)}.casos i{color:var(--muda);font-size:14px}
.zoom{position:fixed;inset:0;background:rgba(0,0,0,.82);display:flex;align-items:center;justify-content:center;z-index:50;padding:16px;cursor:zoom-out}
.zoom img{max-width:100%;max-height:100%;background:#fff;border-radius:6px}
@media (max-width:900px){.timeline{grid-template-columns:repeat(4,1fr)}.calc-fila{grid-template-columns:1fr 1fr}.calc{grid-column:1/-1}.verif{grid-template-columns:1fr 1fr}}
@media (max-width:720px){main{padding:12px 16px 40px}.slide{padding:16px 14px 10px;min-height:0}.sh{grid-template-columns:1fr}.sh .logo-ieee{display:none}.sh h2{font-size:19px}
.grid2,.dos,.con-siglas,.img-pts,.pcards,.etapas,.verif{grid-template-columns:1fr}.timeline{grid-template-columns:1fr 1fr}
.ad{grid-template-columns:1fr;gap:4px;margin:12px 0}.ad.cab{display:none}.ad .fl{transform:rotate(90deg);height:26px}.hoy,.con{font-size:16px}
.flujo{grid-template-columns:1fr}.flujo li:not(:last-child)::after{content:"↓";position:static;display:block;margin-top:6px}
.roles-a{grid-template-columns:1fr}.roles-a .fl{transform:rotate(90deg);height:30px}.ayud{margin:0}.ayud div{grid-template-columns:1fr 1fr}
.portada h1{font-size:29px}.portada .sub{font-size:17px}.lema{font-size:17px}.capa{margin-left:0!important}.barra .marca{display:none}
.chev{clip-path:none;border-radius:10px;min-height:0}#imprimir,#notas{display:none}.barra{padding:6px 10px;gap:6px}.resp{margin-left:-48px}.ritmo b{font-size:22px}.sf{font-size:11px}}
@media print{@page{size:A4 landscape;margin:8mm}:root{--bg:#fff;--sombra:none}body{background:#fff}.barra,.zoom{display:none!important}
main{max-width:none;padding:0}.slide{break-after:page;page-break-after:always;margin:0;border-radius:0;box-shadow:none;min-height:0;padding:0 4mm;zoom:.82}
.nota-orador{display:none}body.con-notas .nota-orador{display:block;break-after:page;page-break-after:always}
.slide,.slide *{-webkit-print-color-adjust:exact;print-color-adjust:exact}.foto img{max-height:105mm;width:auto;max-width:100%;margin:auto}}
"""

JS = r"""
(function(){
  var root=document.documentElement, KEY='pm-ieee-light-tema';
  function aplicar(t){ if(t==='light'||t==='dark'){root.setAttribute('data-theme',t);} else {root.removeAttribute('data-theme');}
    document.getElementById('tema').textContent={light:'Tema: claro',dark:'Tema: oscuro'}[t]||'Tema: automático'; }
  var t=null; try{t=localStorage.getItem(KEY);}catch(e){} aplicar(t);
  document.getElementById('tema').addEventListener('click',function(){ var orden=[null,'light','dark'];
    var sig=orden[(orden.indexOf(root.getAttribute('data-theme'))+1)%3]; aplicar(sig);
    try{ if(sig){localStorage.setItem(KEY,sig);} else {localStorage.removeItem(KEY);} }catch(e){} });
  document.getElementById('imprimir').addEventListener('click',function(){window.print();});
  var notas=[].slice.call(document.querySelectorAll('.nota-orador'));
  function alternarNotas(){ var abrir=!notas.every(function(n){return n.open;}); notas.forEach(function(n){n.open=abrir;});
    document.body.classList.toggle('con-notas',abrir); }
  document.getElementById('notas').addEventListener('click',alternarNotas);
  var sel=document.getElementById('ir'), slides=[].slice.call(document.querySelectorAll('section.slide'));
  sel.addEventListener('change',function(){ location.hash=sel.value; });
  function actual(){ var y=window.scrollY+90, k=0; slides.forEach(function(s,i){ if(s.offsetTop<=y){k=i;} }); return k; }
  function ir(d){ var k=Math.max(0,Math.min(slides.length-1,actual()+d)); slides[k].scrollIntoView({behavior:'smooth'}); sel.value=slides[k].id; }
  document.getElementById('ant').addEventListener('click',function(){ir(-1);});
  document.getElementById('sig').addEventListener('click',function(){ir(1);});
  document.addEventListener('keydown',function(ev){ if(ev.target.tagName==='SELECT'||ev.altKey||ev.ctrlKey||ev.metaKey){return;}
    if(ev.key==='ArrowRight'||ev.key==='PageDown'){ev.preventDefault();ir(1);} if(ev.key==='ArrowLeft'||ev.key==='PageUp'){ev.preventDefault();ir(-1);}
    if(ev.key==='n'||ev.key==='N'){alternarNotas();} });
  window.addEventListener('scroll',function(){ var k=actual(); if(sel.value!==slides[k].id){sel.value=slides[k].id;} },{passive:true});
  [].forEach.call(document.querySelectorAll('.foto img'),function(im){ im.addEventListener('click',function(){
    var z=document.createElement('div'); z.className='zoom'; z.setAttribute('role','dialog'); z.setAttribute('aria-label','Imagen ampliada');
    var c=document.createElement('img'); c.src=im.src; c.alt=im.alt; z.appendChild(c); z.addEventListener('click',function(){z.remove();});
    document.addEventListener('keydown',function esc(ev){ if(ev.key==='Escape'){z.remove(); document.removeEventListener('keydown',esc);} });
    document.body.appendChild(z); }); });
})();
"""

doc = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(D['meta']['titulo_doc'])}</title>
<meta name="description" content="{e(D['meta']['descripcion'])}">
<style>{CSS}</style></head>
<body>
<nav class="barra" aria-label="Navegación"><span class="marca">{e(D['meta']['titulo_doc'])}</span>
<label for="ir" style="position:absolute;left:-9999px">Ir a la diapositiva</label><select id="ir">{''.join(opciones)}</select>
<span class="flechas"><button id="ant" type="button" aria-label="Diapositiva anterior">◀</button><button id="sig" type="button" aria-label="Diapositiva siguiente">▶</button></span>
<button id="notas" type="button">Notas</button><button id="tema" type="button">Tema: automático</button><button id="imprimir" type="button">Imprimir</button></nav>
<main>{''.join(secciones)}</main>
<script>{JS}</script>
</body></html>
"""
SALIDA.write_text(doc, encoding="utf-8")
print(f"{SALIDA.relative_to(RAIZ)} · {N} diapositivas · {len(doc) / 1e6:.2f} MB")
