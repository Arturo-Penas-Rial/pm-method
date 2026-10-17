"""Diagrama propio de la columna vertebral BMAD ↔ gobierno (SVG + PNG). Síntesis de sincronizacion.md §2–§8."""
import html

NAVY, BLUE, ORANGE, CHAR, GRAY = "#002855", "#00629B", "#B5651D", "#272425", "#696969"
TINT, ORT, LT = "#E9F1F8", "#FBF1E6", "#F4F6F8"
W, H = 1240, 640
COL = {"b": (20, 300), "p": (360, 600), "g1": (660, 920), "g2": (950, 1220)}


def caja(x, y, w, h, titulo, sub="", fill=TINT, borde=BLUE, color=NAVY):
    t = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{borde}" stroke-width="1.5"/>']
    cy = y + h / 2 - (9 if sub else 0)
    t.append(f'<text x="{x + w / 2}" y="{cy + 5}" text-anchor="middle" font-size="15" font-weight="bold" fill="{color}">{html.escape(titulo)}</text>')
    for i, linea in enumerate(sub.split("\n") if sub else []):
        t.append(f'<text x="{x + w / 2}" y="{cy + 25 + i * 16}" text-anchor="middle" font-size="12.5" fill="{CHAR}">{html.escape(linea)}</text>')
    return "".join(t)


def flecha(x1, y1, x2, y2, etiqueta="", punteada=False, color=NAVY):
    d = ' stroke-dasharray="6 5"' if punteada else ""
    t = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{d} marker-end="url(#pta)"/>'
    if etiqueta:
        mx = (x1 + x2) / 2
        t += f'<text x="{mx}" y="{y1 - 8}" text-anchor="middle" font-size="12" fill="{GRAY}">{html.escape(etiqueta)}</text>'
    return t


def svg():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Arial, Helvetica, sans-serif" role="img" aria-label="Columna vertebral BMAD y gobierno">',
         f'<defs><marker id="pta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{NAVY}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    # encabezados de columna
    for (x1, x2), txt, fill in [(COL["b"], "Especificación · BMAD", ORANGE), (COL["p"], "Puente · pm-bmad-puente", BLUE),
                                ((COL["g1"][0], COL["g2"][1]), "Gobierno · carpeta del proyecto", NAVY)]:
        o.append(f'<rect x="{x1}" y="12" width="{x2 - x1}" height="40" rx="8" fill="{fill}"/>')
        o.append(f'<text x="{(x1 + x2) / 2}" y="38" text-anchor="middle" font-size="16" font-weight="bold" fill="#fff">{txt}</text>')
    o.append(f'<text x="{(COL["b"][0] + COL["b"][1]) / 2}" y="70" text-anchor="middle" font-size="12" fill="{GRAY}">dueño: equipo BMAD · pm-method solo lee</text>')
    o.append(f'<text x="{(COL["p"][0] + COL["p"][1]) / 2}" y="70" text-anchor="middle" font-size="12" fill="{GRAY}">bmad.py: único código que abre BMAD</text>')
    o.append(f'<text x="{(COL["g1"][0] + COL["g2"][1]) / 2}" y="70" text-anchor="middle" font-size="12" fill="{GRAY}">dueño: skills pm-* · se citan ids, nunca textos</text>')
    filas = [("1 · LEER", 92), ("2 · FIJAR LÍNEA BASE", 232), ("3 · DETECTAR", 372), ("4 · TRASPASAR", 512)]
    h = 96
    for lab, y in filas:
        o.append(f'<rect x="8" y="{y - 6}" width="{W - 16}" height="{h + 4}" rx="12" fill="{LT}" opacity="0.6"/>')
        o.append(f'<text x="{COL["b"][0] + 26}" y="{y + 10}" font-size="11.5" font-weight="bold" fill="{ORANGE}" letter-spacing="1">{lab}</text>')
    bx, bw = COL["b"][0], COL["b"][1] - COL["b"][0]
    px, pw = COL["p"][0], COL["p"][1] - COL["p"][0]
    g1x, g1w = COL["g1"][0], COL["g1"][1] - COL["g1"][0]
    g2x, g2w = COL["g2"][0], COL["g2"][1] - COL["g2"][0]
    y = 108; hh = 72
    # fila 1: leer
    o.append(caja(bx, y, bw, hh, "PRD · arquitectura · épicas", "sprint-status.yaml (FR, NFR, UJ, SM, AD)", ORT, ORANGE))
    o.append(caja(px, y, pw, hh, "construir índice", "huella sha256 de las fuentes"))
    o.append(caja(g1x, y, g1w, hh, "spec-index.json", "contrato pm-spec-index/1 · caché"))
    o.append(caja(g2x, y, g2w, hh, "especificacion.py", "fachada única ← ~20 skills pm-*", NAVY, NAVY, "#fff").replace(f'fill="{CHAR}"', 'fill="#ffffff"'))
    o.append(flecha(bx + bw, y + hh / 2, px - 4, y + hh / 2, "lee"))
    o.append(flecha(px + pw, y + hh / 2, g1x - 4, y + hh / 2, "guarda"))
    o.append(flecha(g2x, y + hh / 2, g1x + g1w + 4, y + hh / 2))
    # fila 2: línea base
    y = 248
    o.append(caja(bx, y, bw, hh, "PRD · arquitectura · épicas", "aprobados en la puerta", ORT, ORANGE))
    o.append(caja(px, y, pw, hh, "linea-base --version X.Y", "solo pm-director, tras decisión humana"))
    o.append(caja(g1x, y, g1w + g2w + 30, hh, "00-direccion/historial/bmad-<art>-v<ver>/", "copia congelada + sha256 + ids en estado.json · decisiones.csv"))
    o.append(flecha(bx + bw, y + hh / 2, px - 4, y + hh / 2, "copia"))
    o.append(flecha(px + pw, y + hh / 2, g1x - 4, y + hh / 2, "congela"))
    # fila 3: detectar
    y = 388
    o.append(caja(bx, y, bw, hh, "PRD / épicas cambian", "o Sprint Change Proposal nueva", ORT, ORANGE))
    o.append(caja(px, y, pw, hh, "verificar", "desvío · falta · propuesta-cambio"))
    o.append(caja(g1x, y, g1w, hh, "sanidad ESP-10", "ERROR si ningún issue lo cita", "#ffffff", ORANGE, ORANGE))
    o.append(caja(g2x, y, g2w, hh, "issue solicitud-cambio", "decide autoridad de cambio o junta"))
    o.append(flecha(bx + bw, y + hh / 2, px - 4, y + hh / 2, "sha256"))
    o.append(flecha(px + pw, y + hh / 2, g1x - 4, y + hh / 2))
    o.append(flecha(g1x + g1w, y + hh / 2, g2x - 4, y + hh / 2))
    # fila 4: traspasar (derecha → izquierda)
    y = 528
    o.append(caja(bx, y, bw, hh, "el equipo BMAD aplica", "con sus flujos y marca \"aplicado\"", ORT, ORANGE))
    o.append(caja(px, y, pw, hh, "handoff [--cambio C-###]", "solo decisiones tomadas"))
    o.append(caja(g1x, y, g1w, hh, "handoff-bmad-<fecha>.md", "ids afectados · ESP-13 si no se confirma"))
    o.append(caja(g2x, y, g2w, hh, "cambio aprobado C-###", "o prioridades de backlog.csv"))
    o.append(flecha(g2x, y + hh / 2, g1x + g1w + 4, y + hh / 2))
    o.append(flecha(g1x, y + hh / 2, px + pw + 4, y + hh / 2, "emite"))
    o.append(flecha(px, y + hh / 2, bx + bw + 4, y + hh / 2, "entrega"))
    # cierre del ciclo: aplicado → verificar limpio → nueva línea base
    o.append(f'<path d="M{bx + 12},{y} C{bx - 4},{470} {bx - 4},{330} {bx + 12},{320}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#pta)"/>')
    o.append(f'<text x="{bx + 30}" y="{491}" font-size="11.5" fill="{BLUE}">→ verificar limpio → línea base de versión mayor</text>')
    o.append("</svg>")
    return "".join(o)


def generar(carpeta):
    s = svg()
    (carpeta / "col-vertebral.svg").write_text(s, encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        pg.set_content(f'<html><body style="margin:0">{s}</body></html>')
        pg.screenshot(path=str(carpeta / "col-vertebral.png"), clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
