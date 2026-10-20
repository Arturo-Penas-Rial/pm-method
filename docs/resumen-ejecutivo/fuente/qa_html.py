"""QA visual del HTML con Playwright: escritorio claro, escritorio oscuro y teléfono de 390 px.

Uso: python3 qa_html.py CARPETA_DE_SALIDA   (capturas por diapositiva; informa desbordes horizontales y anclas rotas)
"""
import pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
URL = (AQUI.parent / "resumen-ejecutivo-pm-method.html").resolve().as_uri()
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/qa-resumen-html")
OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("*.png"):
    f.unlink()
JS = """() => { const d = document.documentElement;
  const malos = [...document.querySelectorAll('body *')].filter(el => { const r = el.getBoundingClientRect();
    return r.width > 0 && r.right > d.clientWidth + 1 && !el.closest('.scroll, pre, select'); }).slice(0, 8)
    .map(el => el.tagName + '.' + el.className + ' ' + Math.round(el.getBoundingClientRect().right));
  const anclas = [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1)).filter(id => id && !document.getElementById(id));
  return {scrollW: d.scrollWidth, clientW: d.clientWidth, desbordes: malos, anclas_rotas: [...new Set(anclas)],
          slides: document.querySelectorAll('section.slide').length, imagenes_rotas: [...document.images].filter(i => !i.naturalWidth).length}; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for nombre, ancho, alto, esquema in (("claro", 1366, 900, "light"), ("oscuro", 1366, 900, "dark"), ("tel", 390, 844, "light")):
        pg = b.new_page(viewport={"width": ancho, "height": alto}, color_scheme=esquema)
        pg.goto(URL)
        pg.wait_for_timeout(500)
        print(nombre, pg.evaluate(JS))
        for i, s in enumerate(pg.query_selector_all("section.slide"), 1):
            s.screenshot(path=str(OUT / f"{nombre}-{i:02d}.png"))
        pg.close()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto(URL)
    pg.pdf(path=str(OUT / "impreso.pdf"), landscape=True, format="A4", print_background=True)
    b.close()
print("capturas en", OUT)
