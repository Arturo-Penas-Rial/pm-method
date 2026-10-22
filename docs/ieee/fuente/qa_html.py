"""QA visual de los dos HTML con Playwright: escritorio claro, escritorio oscuro y teléfono de 390 px, y PDF impreso.

Uso: python3 qa_html.py CARPETA_DE_SALIDA   (capturas por diapositiva; informa desbordes horizontales, texto cortado,
anclas e imágenes rotas). Si Chromium no está en la ruta por defecto de Playwright: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers.
"""
import pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/qa-ieee-html")
JS = """() => { const d = document.documentElement;
  const fuera = [...document.querySelectorAll('section.slide *')].filter(el => { const r = el.getBoundingClientRect();
    return r.width > 0 && r.right > d.clientWidth + 1; }).slice(0, 8).map(el => el.tagName + '.' + el.className);
  const cortado = [...document.querySelectorAll('section.slide *')].filter(el => el.children.length === 0 && el.textContent.trim()
    && (el.scrollWidth > el.clientWidth + 2 || el.scrollHeight > el.clientHeight + 2) && getComputedStyle(el).overflow !== 'visible').slice(0, 8)
    .map(el => el.tagName + ' ' + el.textContent.slice(0, 40));
  const anclas = [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1)).filter(id => id && !document.getElementById(id));
  return {scrollW: d.scrollWidth, clientW: d.clientWidth, fuera, cortado, anclas_rotas: anclas,
          slides: document.querySelectorAll('section.slide').length, imagenes_rotas: [...document.images].filter(i => !i.naturalWidth).length}; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for nombre in ("resumen", "informe"):
        url = (AQUI.parent / f"pm-method-ieee-{nombre}-light.html").resolve().as_uri()
        dest = OUT / nombre
        dest.mkdir(parents=True, exist_ok=True)
        for f in dest.glob("*.png"):
            f.unlink()
        for modo, ancho, alto, esquema in (("claro", 1366, 900, "light"), ("oscuro", 1366, 900, "dark"), ("tel", 390, 844, "light")):
            pg = b.new_page(viewport={"width": ancho, "height": alto}, color_scheme=esquema)
            pg.goto(url)
            pg.wait_for_timeout(300)
            print(nombre, modo, pg.evaluate(JS))
            pg.add_style_tag(content=".barra{position:static!important}")  # la barra fija taparía las capturas por diapositiva
            for i, s in enumerate(pg.query_selector_all("section.slide"), 1):
                s.screenshot(path=str(dest / f"{modo}-{i:02d}.png"))
            pg.close()
        pg = b.new_page(viewport={"width": 1366, "height": 900})
        pg.goto(url)
        pg.pdf(path=str(dest / "impreso.pdf"), landscape=True, format="A4", print_background=True)
        pg.close()
    b.close()
print("capturas en", OUT)
