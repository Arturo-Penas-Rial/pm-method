"""QA del HTML del informe: capturas en claro (1366 px), oscuro (1366 px) y teléfono (390 px), desbordes horizontales y SVG vacíos.
Uso: python3 qa_html.py [html] [carpeta]   (por defecto: el HTML de salida-<versión>/ y qa-html/)"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "qa-html"); OUT.mkdir(exist_ok=True)
for f in OUT.glob("*.png"): f.unlink()
VER = json.load(open(pathlib.Path(__file__).with_name("data.json"), encoding="utf-8"))["meta"]["version"]
url = "file://" + str(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else f"salida-{VER}/informe-2-ecosistema-pm-method-{VER}.html").resolve())
JS = """() => { const d=document.documentElement; const malos=[...document.querySelectorAll('body *')].filter(el=>{const r=el.getBoundingClientRect(); return r.right>d.clientWidth+1 && !el.closest('.scroll,.diag-in,pre')}).slice(0,8).map(el=>el.tagName+'.'+el.className+' '+(el.id||'')+' '+Math.round(el.getBoundingClientRect().right)); return {sw:d.scrollWidth, cw:d.clientWidth, h:d.scrollHeight, desbordes:malos} }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for nombre, w, vh, esquema in (("desk", 1366, 2000, "light"), ("dark", 1366, 2000, "dark"), ("mob", 390, 2400, "light"), ("mobdark", 390, 2400, "dark")):
        pg = b.new_page(viewport={"width": w, "height": vh}, color_scheme=esquema)
        pg.goto(url); pg.wait_for_timeout(400)
        info = pg.evaluate(JS); print(nombre, info)
        svgs = pg.evaluate("() => [...document.querySelectorAll('figure.diag svg')].map(s => {const r = s.getBoundingClientRect(); return [s.id || '(sin id)', Math.round(r.width), Math.round(r.height), s.querySelectorAll('g').length]})")
        print(nombre, "SVG en línea:", len(svgs), "· vacíos o sin tamaño:", [x for x in svgs if x[1] < 50 or x[2] < 50 or x[3] == 0] or "ninguno")
        n = 0
        for y in range(0, info["h"], vh):
            pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(60)
            pg.screenshot(path=str(OUT / f"{nombre}-{n:03d}.png")); n += 1
        print(nombre, "capturas", n)
    b.close()
