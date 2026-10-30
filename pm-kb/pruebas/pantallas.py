"""Prueba de pantallas del portal de pm-kb con Playwright para Python y Chromium. docs/PM-KB.md §12.

  python3 pm-kb/pruebas/pantallas.py [--salida DIR] [--python-kb RUTA] [--documentos CARPETA]…

Corre con un Python que tenga Playwright (`chromium.launch()` sin opciones); pm-kb (indexar, token y el servicio web) corre
con el Python de su entorno (`--python-kb`, por defecto `$PMKB_VENV/bin/python` o `~/.local/share/pm-kb/venv/bin/python`)
y la base de PMKB_DSN o la instalación local. Arma un proyecto con los scripts del núcleo (pruebas/proyecto_tablero.py:
dos puertas decididas y una instantánea manual), lo indexa como `zz-pantallas`, crea un token de un día y levanta el
servicio en un puerto libre entre 8800 y 8899 con la carpeta del proyecto montada en solo lectura (si se puede: root con
`unshare`; si no, se comprueba igual que la carpeta no cambió). `--documentos` copia además los HTML, SVG y PNG de esa
carpeta a 02-planificacion/visuales/ (por ejemplo, salidas reales de archify, diagram-design o visual-explainer).

Recorre en claro, oscuro y móvil: cartera, pestañas Tableros (tres vistas, línea de tiempo, instantánea, comparar y el
selector «Por actor»), Buscar, Artefactos (documentos en un iframe con sandbox sin allow-same-origin), Preguntar, la
ficha (también por el nombre del proyecto de estado.json), «actualizar ahora» (y su límite, 429) y la vista de un enlace
compartido (`pm-kb compartir crear`, abierto en un navegador limpio: canje del token del fragmento, «solo lectura ·
vence …», ficha de una tarjeta, enlace por actor). PMKB_ORIGENES es la dirección del servicio de la prueba. Verifica 0
violaciones de CSP en el portal
(las de los documentos aislados se informan aparte: son bloqueos esperados, como fuentes web), 0 errores de JavaScript
y sin desborde horizontal en móvil. Guarda las capturas en --salida (por defecto, una carpeta temporal que informa).
"""
import argparse, hashlib, json, os, re, shutil, socket, subprocess, sys, tempfile, time, urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KB = AQUI.parent
sys.path.insert(0, str(AQUI))
import proyecto_tablero  # noqa: E402

OK = FALLO = 0
P = "zz-pantallas"


def ver(nombre, cond, detalle=""):
    global OK, FALLO
    if cond:
        OK += 1; print(f"OK    {nombre}", flush=True)
    else:
        FALLO += 1; print(f"FALLO {nombre}" + (f" · {str(detalle)[:400]}" if detalle else ""), flush=True)


def arbol(p):
    out = {}
    for raiz, dirs, archivos in os.walk(p):
        for x in dirs:
            out[os.path.relpath(os.path.join(raiz, x), p)] = "dir"
        for x in archivos:
            q = os.path.join(raiz, x)
            with open(q, "rb") as fh:
                out[os.path.relpath(q, p)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def puerto_libre():
    for x in range(8800, 8900):
        with socket.socket() as so:
            try:
                so.bind(("127.0.0.1", x)); return x
            except OSError:
                continue
    raise SystemExit("no hay un puerto libre entre 8800 y 8899")


def kb(py, *args):
    r = subprocess.run([py, "-m", "pmkb", *args], cwd=str(KB), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"pm-kb {' '.join(args)} falló: {(r.stdout + r.stderr)[-600:]}")
    return r.stdout


def solo_lectura_disponible(carpeta):
    if os.name != "posix" or os.geteuid() != 0 or not shutil.which("unshare"):
        return False
    r = subprocess.run(["unshare", "-m", "sh", "-c", 'mount --bind "$1" "$1" && mount -o remount,bind,ro "$1" "$1" && ! touch "$1/.prueba-ro" 2>/dev/null', "sh", str(carpeta)],
                       capture_output=True)
    return r.returncode == 0 and not (Path(carpeta) / ".prueba-ro").exists()


INICIO = """
(() => {
  const avisar = (e) => console.log("PMKB-CSP " + JSON.stringify({ doc: String(location.href), bloqueado: e.blockedURI, directiva: e.violatedDirective }));
  document.addEventListener("securitypolicyviolation", avisar);
})();
"""


def main():
    ap = argparse.ArgumentParser(description="Prueba de pantallas del portal de pm-kb (Playwright).")
    ap.add_argument("--salida", help="carpeta de las capturas (por defecto, una temporal)")
    ap.add_argument("--python-kb", help="Python del entorno de pm-kb")
    ap.add_argument("--documentos", action="append", default=[], help="carpeta con HTML/SVG/PNG a copiar en 02-planificacion/visuales/")
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("pantallas.py necesita Playwright para Python (python3 -m pip install playwright) y Chromium")
    py = a.python_kb or (os.path.join(os.environ["PMKB_VENV"], "bin", "python") if os.environ.get("PMKB_VENV") else
                         str(Path.home() / ".local" / "share" / "pm-kb" / "venv" / "bin" / "python"))
    salida = Path(a.salida or tempfile.mkdtemp(prefix="pmkb-pantallas-"))
    salida.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="pmkb-pantallas-proy-"))
    srv, token = None, None
    try:
        proy = proyecto_tablero.crear(tmp / "proyecto")
        vis = proy / "gestion" / "02-planificacion" / "visuales"
        for carpeta in a.documentos:
            for f in sorted(Path(carpeta).iterdir()):
                if f.suffix.lower() in (".html", ".svg", ".png") and f.is_file():
                    shutil.copy2(f, vis / f.name)
        print(kb(py, "indexar", "--proyecto", P, "--ruta", str(proy), "--sin-vectores").strip())
        token = kb(py, "token", "crear", "--persona", "Prueba de pantallas", "--proyectos", P, "--dias", "1").strip().splitlines()[-1].strip()
        puerto = puerto_libre()
        base = f"http://127.0.0.1:{puerto}"
        os.environ["PMKB_ORIGENES"] = base            # los enlaces compartidos se arman con el origen configurado
        enlaces = {"general": kb(py, "compartir", "crear", "--proyecto", P, "--para", "Prueba de pantallas").strip().splitlines()[-1].strip(),
                   "actor": kb(py, "compartir", "crear", "--proyecto", P, "--actor", "Laura", "--para", "Prueba de pantallas").strip().splitlines()[-1].strip()}
        antes = arbol(proy)
        lanzar = [py, "-c", f"import uvicorn; from pmkb import web; uvicorn.run(web.crear_app(), host='127.0.0.1', port={puerto}, log_level='warning')"]
        ro = solo_lectura_disponible(proy)
        if ro:
            lanzar = ["unshare", "-m", "sh", "-c", 'mount --bind "$1" "$1" && mount -o remount,bind,ro "$1" "$1" && shift && exec "$@"', "sh", str(proy)] + lanzar
        env = {**os.environ, "PMKB_ORIGENES": base}
        registro = open(salida / "servicio.log", "w", encoding="utf-8")
        srv = subprocess.Popen(lanzar, cwd=str(KB), env=env, stdout=registro, stderr=subprocess.STDOUT, text=True)
        for _ in range(100):
            try:
                with socket.create_connection(("127.0.0.1", puerto), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        print(f"servicio en {base} (pid {srv.pid}; carpeta del proyecto en solo lectura: {'sí, montaje ro' if ro else 'no disponible: se compara el árbol'})")
        recorrer(sync_playwright, base, token, salida, ro, enlaces)
        despues = arbol(proy)
        ver("PAN-30 la carpeta del proyecto no cambió (índice y «actualizar ahora» no escriben en ella)", antes == despues,
            sorted(set(antes.items()) ^ set(despues.items()))[:6])
    finally:
        if srv:
            srv.terminate()
            try:
                srv.wait(10)
            except subprocess.TimeoutExpired:
                srv.kill()
        try:
            kb(py, "compartir", "revocar", "--proyecto", P)
            kb(py, "quitar", "--proyecto", P)
            kb(py, "token", "revocar", "--persona", "Prueba de pantallas")
        except SystemExit as x:
            print(f"aviso al limpiar: {x}")
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\ncapturas en {salida}")
    print(f"pm-kb pantallas: {OK} OK · {FALLO} FALLO")
    sys.exit(1 if FALLO else 0)


def recorrer(sync_playwright, base, token, salida, ro, enlaces):
    modos = [("claro", {"viewport": {"width": 1366, "height": 900}, "color_scheme": "light"}),
             ("oscuro", {"viewport": {"width": 1366, "height": 900}, "color_scheme": "dark"}),
             ("movil", {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2, "color_scheme": "light"})]
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for modo, opciones in modos:
            csp_portal, csp_docs, errores = [], [], []
            ctx = nav.new_context(**opciones)
            ctx.add_init_script(INICIO)
            pg = ctx.new_page()

            def consola(m, modo=modo):
                t, url = m.text, (m.location or {}).get("url", "")
                if t.startswith("PMKB-CSP "):
                    x = json.loads(t[9:])
                    (csp_docs if "/archivo/" in x["doc"] or x["doc"] in ("about:srcdoc", "") else csp_portal).append(x)
                elif m.type == "error" and "Content Security Policy" in t:
                    (csp_docs if "/archivo/" in url or not url.startswith(base) else csp_portal).append({"doc": url, "mensaje": t[:160]})
                elif m.type == "error" and "/archivo/" not in url and not ("status of 429" in t and "/api/tablero/actualizar" in url):   # el 429 esperado
                    errores.append(t[:200])
            pg.on("console", consola)
            pg.on("pageerror", lambda e: errores.append(f"pageerror: {e}"))
            cap = lambda n: pg.screenshot(path=str(salida / f"{modo}-{n}.png"), full_page=True)
            desborde = lambda: pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            pg.goto(f"{base}/ingresar?token={urllib.parse.quote(token)}")
            pg.wait_for_selector(".cartera")
            fila = pg.locator(".fila-cartera", has_text=P)
            ver(f"PAN-01 [{modo}] cartera: la fila del proyecto con fase, etapa, próxima puerta con bloqueos y totales de atención",
                fila.count() == 1 and all(x in fila.inner_text().lower() for x in ("próxima puerta", "bloqueo", "decidir", "etapa", "fase")), fila.inner_text()[:300] if fila.count() else "")
            cap("cartera")
            if modo == "movil":
                ver("PAN-02 [movil] cartera sin desborde horizontal", desborde() <= 1, desborde())
            fila.locator("h2 a").first.click()
            pg.wait_for_selector(".tb-pulso")
            ver(f"PAN-03 [{modo}] Tableros: línea de tiempo con 3 instantáneas y «Actual (en vivo)», pulso y vista de ciclo con puertas",
                pg.locator(".tb-linea li").count() == 4 and pg.locator(".tb-puerta.tb-proxima").count() == 1 and pg.locator("a.tb-tarjeta").count() > 2,
                (pg.locator(".tb-linea li").count(), pg.locator(".tb-puerta.tb-proxima").count()))
            cap("tablero-ciclo")
            if modo == "movil":
                ver("PAN-24 [movil] tablero sin desborde horizontal de la página (las filas anchas se deslizan dentro de su caja)", desborde() <= 1, desborde())
            if modo != "movil":
                pg.click(".tb-vistas button[data-vista=atencion]")
                ver(f"PAN-04 [{modo}] vista Atención: tarjetas por grupo", pg.locator(".tb-carriles a.tb-tarjeta, .tb-tablero a.tb-tarjeta").count() >= 1)
                cap("tablero-atencion")
                pg.click(".tb-vistas button[data-vista=entrega]")
                ver(f"PAN-05 [{modo}] vista Entrega: productos y control (cambio pendiente de decisión)", pg.locator("text=Productos").count() >= 1 and pg.locator("a.tb-tarjeta[data-ref='C-001']").count() == 1)
                cap("tablero-entrega")
                pg.click(".tb-vistas button[data-vista=ciclo]")
            pg.click(".tb-linea li:first-child button")
            pg.wait_for_selector(".tb-congelada")
            ver(f"PAN-06 [{modo}] instantánea congelada elegida en la línea de tiempo: aviso «no se actualiza» y enlace al HTML estático",
                "no se actualiza" in pg.locator(".tb-congelada").inner_text() and pg.locator(".tb-congelada a").count() == 1)
            pg.select_option(".tb-comparar", "actual")
            pg.wait_for_selector(".tb-cmp")
            txt = pg.locator(".tb-cmp").inner_text().lower()
            ver(f"PAN-07 [{modo}] comparar la instantánea con el actual: entraron, salieron y cambiaron (función comparar del núcleo)",
                "entraron" in txt and "cambiaron" in txt and "→ actual" in txt, txt[:200])
            cap("tablero-comparar")
            pg.click(".tb-linea li:last-child button")
            pg.wait_for_selector(".tb-vivo.tb-ok")
            ops_actor = pg.locator("select.tb-actor option").all_inner_texts()
            pg.select_option("select.tb-actor", label="Laura Méndez (ejecutivo)")
            pg.wait_for_selector(".tb-pulso :text('Laura Méndez')")
            if modo != "movil":
                pg.click(".tb-vistas button[data-vista=atencion]")
                pg.wait_for_selector(".tb-vista a.tb-tarjeta")
            refs_actor = [pg.locator(".tb-vista a.tb-tarjeta").nth(i).get_attribute("data-ref") for i in range(pg.locator(".tb-vista a.tb-tarjeta").count())]
            ver(f"PAN-25 [{modo}] Tableros «Por actor»: el selector lista los actores (núcleo) y el tablero muestra solo lo de la persona elegida (sin la acción de otra, A-001), con el bloque del actor",
                {"Todos", "Laura Méndez (ejecutivo)", "Martín Suárez (gestor del proyecto)"} <= set(ops_actor) and "actor=" in pg.url and "A-001" not in refs_actor
                and (modo == "movil" or "C-001" in refs_actor), (ops_actor, refs_actor, pg.url))
            cap("tablero-por-actor")
            pg.select_option("select.tb-actor", "")
            pg.wait_for_selector(".tb-pulso :text('Laura Méndez')", state="detached")
            if modo != "movil":
                pg.click(".tb-vistas button[data-vista=ciclo]")
            tarjeta = pg.locator(".tb-puerta.tb-hecha a.tb-tarjeta").first
            ref = tarjeta.get_attribute("data-ref")
            tarjeta.click()
            pg.wait_for_selector(".ficha-pagina")
            ver(f"PAN-08 [{modo}] la tarjeta de una puerta abre su ficha por id (/p/<proyecto>/ficha/<ref>) con decisión y relacionados",
                pg.url.endswith("/ficha/" + urllib.parse.quote(ref, safe="")) and "decisión:" in pg.inner_text(".ficha-pagina").lower() and "relacionados por id" in pg.inner_text(".ficha-pagina").lower(),
                (pg.url, ref))
            cap("ficha-puerta")
            if modo == "movil":
                ver("PAN-09 [movil] ficha sin desborde horizontal", desborde() <= 1, desborde())
            pg.goto(f"{base}/p/{urllib.parse.quote(proyecto_tablero.NOMBRE)}/ficha/C-001")
            pg.wait_for_selector(".ficha-pagina")
            ver(f"PAN-10 [{modo}] enlace con el nombre de estado.json (el que arma el HTML del núcleo) → ficha de la instancia",
                pg.url == f"{base}/p/{P}/ficha/C-001" and "en el tablero" in pg.inner_text(".ficha-pagina").lower(), pg.url)
            pg.click(f"#migas a[href='/p/{P}']")
            pg.wait_for_selector(".tb-pulso")
            pg.click("#tab-buscar")
            pg.fill("#q", "proveedor firma digital")
            pg.press("#q", "Enter")
            pg.wait_for_selector(".resultado, .vacio")
            ver(f"PAN-11 [{modo}] Buscar filtrado al proyecto: resultados con cita que enlazan a la ficha",
                pg.locator(".resultado").count() >= 1 and "/ficha/" in (pg.locator(".resultado h2 a").first.get_attribute("href") or ""))
            cap("buscar")
            pg.click("#tab-artefactos")
            pg.wait_for_selector(".documentos")
            ver(f"PAN-12 [{modo}] Artefactos: grupos con estado, versión y marca de borrador; ciclos anteriores por instantáneas",
                pg.locator(".artefacto").count() >= 3 and pg.locator(".artefacto .chip", has_text="BORRADOR").count() >= 1 and pg.locator("details.ciclos").count() >= 1)
            docs = pg.locator(".documento")
            motores = [docs.nth(i).locator(".chip.motor").inner_text() for i in range(docs.count())]
            ver(f"PAN-13 [{modo}] Documentos: archify, diagram-design y visual-explainer reconocidos; sin la fuente .src.html; SVG y PNG del diagrama",
                {"archify", "diagram-design", "visual-explainer"} <= set(motores) and pg.locator(".documento .cita", has_text=".src.html").count() == 0
                and pg.locator(".documento a", has_text="SVG").count() >= 1 and pg.locator(".documento a", has_text="PNG").count() >= 1, motores)
            pg.locator(".documento", has_text="visuales/wbs.html").locator("button", has_text="Ver aquí").first.click()
            marco = pg.locator("iframe.marco-doc")
            marco.wait_for()
            sb = marco.get_attribute("sandbox")
            fr = pg.frame_locator("iframe.marco-doc")
            try:
                fr.locator("#estado", has_text="aislado").wait_for(timeout=8000)
                interno = fr.locator("#estado").inner_text()
            except Exception as x:
                interno = f"sin texto: {x}"
            ver(f"PAN-14 [{modo}] documento con scripts en iframe sandbox=allow-scripts sin allow-same-origin: se dibuja y no alcanza la sesión ni el portal",
                sb == "allow-scripts" and "dibujado por el script del documento" in interno and "aislado" in interno and "FUGA" not in pg.title(), (sb, interno, pg.title()))
            cap("documento-archify")
            pg.locator(".documento", has_text="visuales/riesgos.html").locator("button", has_text="Ver aquí").first.click()
            pg.frame_locator("iframe.marco-doc").locator("h1", has_text="Riesgos").wait_for(timeout=8000)
            ver(f"PAN-15 [{modo}] documento sin scripts en iframe con sandbox vacío", pg.locator("iframe.marco-doc").get_attribute("sandbox") == "")
            if modo == "claro":
                r = ctx.request.get(base + pg.locator(".documento", has_text="visuales/wbs.html").locator("a", has_text="Descargar").get_attribute("href"))
                h = r.headers
                ver("PAN-16 descarga: Content-Disposition attachment y CSP aislada (sandbox, sin red, frame-ancestors 'self')",
                    r.status == 200 and h.get("content-disposition", "").startswith("attachment;") and "sandbox allow-scripts" in h.get("content-security-policy", "")
                    and "connect-src 'none'" in h.get("content-security-policy", "") and "frame-ancestors 'self'" in h.get("content-security-policy", ""), dict(h))
                fuera = ctx.request.get(f"{base}/archivo/{P}/..%2F..%2Fetc%2Fpasswd")
                fuera2 = ctx.request.get(f"{base}/archivo/{P}/gestion/estado.json")
                ver("PAN-17 /archivo no sirve rutas fuera de la carpeta indexada ni archivos que no son documentos HTML/SVG/PNG", fuera.status == 404 and fuera2.status == 404,
                    (fuera.status, fuera2.status))
            if modo == "claro":
                vistos = []
                for i in range(docs.count()):
                    docs.nth(i).locator("button", has_text="Ver aquí").click()
                    m = pg.locator("iframe.marco-doc")
                    m.wait_for()
                    try:
                        pg.frame_locator("iframe.marco-doc").locator("body").wait_for(timeout=15000)
                        largo = len(pg.frame_locator("iframe.marco-doc").locator("body").inner_text(timeout=15000))
                    except Exception:
                        largo = 0
                    vistos.append((docs.nth(i).locator(".cita").inner_text().split(" · ")[0].rsplit("/", 1)[-1], m.get_attribute("sandbox"), largo))
                print("      documentos en el marco aislado (archivo, sandbox, caracteres visibles): " + "; ".join(f"{a} {b!r} {c}" for a, b, c in vistos))
                ver("PAN-23 cada documento de la lista se abre en el marco aislado (nunca allow-same-origin) y muestra contenido",
                    vistos and all(s in ("", "allow-scripts") and n > 0 for _, s, n in vistos), vistos)
                cap("documentos")
            pg.click("#tab-preguntar")
            pg.fill("#pregunta", "¿Qué riesgo hay con el proveedor?")
            pg.press("#pregunta", "Enter")
            pg.wait_for_selector(".mensaje .modo")
            ver(f"PAN-18 [{modo}] Preguntar: evidencia citada con enlaces a fichas", pg.locator(".mensaje .fuentes a").count() >= 1)
            cap("preguntar")
            if modo == "claro":
                pg.click("#tab-tableros")
                pg.wait_for_selector(".tb-actualizar")
                pg.click(".tb-actualizar")
                pg.wait_for_selector(".tb-vivo:text-matches('actualizado ahora|no se pudo')", timeout=60000)
                t1 = pg.inner_text(".tb-vivo")
                pg.click(".tb-actualizar")
                pg.wait_for_selector(".tb-vivo:text-matches('demasiados pedidos|no se pudo')", timeout=30000)
                t2 = pg.inner_text(".tb-vivo")
                ver("PAN-19 «actualizar ahora» regenera el tablero en el índice (carpeta en solo lectura) y el segundo pedido inmediato recibe 429",
                    "actualizado ahora" in t1 and "demasiados pedidos" in t2, (t1, t2, "solo lectura" if ro else "sin montaje ro"))
                cap("tablero-actualizado")
                ajeno = ctx.request.post(base + "/api/tablero/actualizar", data=json.dumps({"proyecto": P}),
                                         headers={"Content-Type": "application/json", "Origin": "http://otro.example"})
                sin = ctx.request.post(base + "/api/tablero/actualizar", data=json.dumps({"proyecto": P}), headers={"Content-Type": "application/json"})
                ver("PAN-20 «actualizar ahora» con Origin ajeno o sin Origin → 403", ajeno.status == 403 and sin.status == 403, (ajeno.status, sin.status))
            ctx.close()
            # ---------------------------------------------------------- vista de un enlace compartido (navegador limpio)
            ctx = nav.new_context(**opciones)
            ctx.add_init_script(INICIO)
            pg = ctx.new_page()
            pg.on("console", consola)
            pg.on("pageerror", lambda e: errores.append(f"pageerror: {e}"))
            pedidos = []
            pg.on("request", lambda r: pedidos.append(r.url))
            cap = lambda n: pg.screenshot(path=str(salida / f"{modo}-{n}.png"), full_page=True)
            tok = enlaces["general"].split("#", 1)[1]
            pg.goto(enlaces["general"])
            pg.wait_for_selector(".tb-pulso")
            vig = pg.inner_text("#vigencia")
            ver(f"PAN-26 [{modo}] vista compartida: sin pestañas ni búsqueda, «solo lectura · vence …» visible, el token salió de la barra y de todo pedido; sin línea de tiempo, comparar, actor ni «actualizar ahora»",
                vig.startswith("solo lectura · vence ") and "#" not in pg.url and pg.url.endswith("/v") and not any(tok in u for u in pedidos)
                and pg.locator(".pestanas, #q, .tb-linea, .tb-comparar, select.tb-actor, .tb-actualizar").count() == 0 and pg.locator("a.tb-tarjeta").count() > 2,
                (vig, pg.url, len(pedidos)))
            cap("compartido-ciclo")
            if modo == "movil":
                ver("PAN-27 [movil] vista compartida sin desborde horizontal", desborde() <= 1, desborde())
            t = pg.locator(".tb-puerta.tb-hecha a.tb-tarjeta").first
            ref = t.get_attribute("data-ref")
            t.click()
            pg.wait_for_selector(".ficha-pagina")
            ver(f"PAN-28 [{modo}] vista compartida: la tarjeta abre su ficha completa en /v/ficha/<ref> (sin salir del enlace) y vuelve al tablero",
                pg.url.endswith("/v/ficha/" + urllib.parse.quote(ref, safe="")) and "decisión:" in pg.inner_text(".ficha-pagina").lower()
                and pg.locator(".ficha-pagina a[href='/v']").count() >= 1, (pg.url, ref))
            cap("compartido-ficha")
            if modo == "movil":
                ver("PAN-29 [movil] ficha compartida sin desborde horizontal", desborde() <= 1, desborde())
            pg.click(".ficha-pagina a[href='/v']")
            pg.wait_for_selector(".tb-pulso")
            if modo == "claro":
                rq = ctx.request              # comparte la cookie de la sesión compartida (sin errores de consola esperados)
                estados = [rq.get(base + "/api/buscar?q=riesgo").status, rq.get(base + "/api/cartera").status, rq.get(base + "/api/ficha?id=R-001").status,
                           rq.post(base + "/mcp", data='{"jsonrpc":"2.0","id":1,"method":"ping"}', headers={"Content-Type": "application/json"}).status]
                pg.goto(base + "/")
                pg.wait_for_selector(".tb-pulso")
                ver("PAN-31 desde la vista compartida: buscar, cartera y MCP → 403, una ficha fuera del tablero → 404 y la portada vuelve a /v",
                    estados == [403, 403, 404, 403] and pg.url.endswith("/v"), (estados, pg.url))
                ctx2 = nav.new_context(**opciones)
                ctx2.add_init_script(INICIO)
                pa = ctx2.new_page()
                pa.on("console", consola)
                pa.goto(enlaces["actor"])
                pa.wait_for_selector(".tb-pulso")
                pa.click(".tb-vistas button[data-vista=atencion]")
                pa.wait_for_selector(".tb-vista a.tb-tarjeta")
                ra = [pa.locator(".tb-vista a.tb-tarjeta").nth(i).get_attribute("data-ref") for i in range(pa.locator(".tb-vista a.tb-tarjeta").count())]
                ver("PAN-32 enlace por actor: la vigencia nombra al actor y el tablero muestra solo lo suyo (C-001 sí, la acción de otra persona A-001 no)",
                    "actor: Laura Méndez" in pa.inner_text("#vigencia") and "C-001" in ra and "A-001" not in ra, (pa.inner_text("#vigencia"), ra))
                pa.screenshot(path=str(salida / "claro-compartido-actor.png"), full_page=True)
                ctx2.close()
            ver(f"PAN-21 [{modo}] 0 violaciones de CSP en el portal y en la vista compartida", not csp_portal, csp_portal[:3])
            ver(f"PAN-22 [{modo}] 0 errores de JavaScript en el portal y en la vista compartida", not errores, errores[:3])
            print(f"      [{modo}] bloqueos de CSP dentro de los documentos aislados (esperados): {len(csp_docs)}"
                  + (f" · p. ej. {csp_docs[0].get('bloqueado') or csp_docs[0].get('mensaje', '')[:80]}" if csp_docs else ""))
            ctx.close()
        nav.close()


if __name__ == "__main__":
    main()
