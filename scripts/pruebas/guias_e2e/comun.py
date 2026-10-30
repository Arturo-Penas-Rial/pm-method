from base import *
import re, datetime
G = "gestion"

def escribir(repo, rel, texto):
    p = os.path.join(repo, G, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(texto)

def art(repo, clave, rel, estado="en-revision", version=None, texto=None):
    if texto or not os.path.exists(os.path.join(repo, G, rel)):
        escribir(repo, rel, texto or f"# {clave}\n\nContenido de ejemplo generado por la skill dueña (recorrido E2E).\n")
    v = f" --version {version}" if version else ""
    run(E(f'estado.py --proyecto {G} artefacto {clave} --ruta {rel} --estado {estado}{v}'), repo, mostrar=False)

def reg(repo, registro, **campos):
    args = " ".join(f'--campo "{k}={v}"' for k, v in campos.items())
    out = run(E(f'registro.py --proyecto {G} agregar {registro} {args}'), repo)
    m = re.search(r"\b([A-Z]{1,2}-\d{3})\b", out)
    return m.group(1) if m else None

def act(repo, registro, id_, **campos):
    args = " ".join(f'--campo "{k}={v}"' for k, v in campos.items())
    return run(E(f'registro.py --proyecto {G} actualizar {registro} {id_} {args}'), repo)

def puerta(repo, tipo, por, fecha, extra="", decision="aprobado", lista=True):
    run(E(f'puertas.py --proyecto {G} verificar {tipo}'), repo, ok=(0, 1, 2))
    if lista:
        run(E(f'puertas.py --proyecto {G} lista {tipo} --fecha {fecha}'), repo, mostrar=False)
        run(E(f'puertas.py --proyecto {G} confirmar {tipo} --por "{por}" --fecha {fecha}'), repo)
    return run(E(f'estado.py --proyecto {G} puerta {tipo} --decision {decision} --por "{por}" --fecha {fecha} {extra}'), repo)

def base_su(repo, fecha):
    """Proyecto creado, BMAD detectado, roles y tolerancias (equivale a los pasos de puesta en marcha).
    `fecha` es la fecha de creación del proyecto (nuevo_proyecto.py --fecha): estado.json no depende del día de la corrida."""
    run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez" --fecha {fecha}'), repo)
    run(f'python3 {BMAD} --proyecto {G} detectar', repo, mostrar=False)
    run(f'python3 {BMAD} --proyecto {G} requisitos', repo, mostrar=False)
    run(E(f'estado.py --proyecto {G} rol usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" product_owner="Sofía Ramírez" autoridad_cambio="Sofía Ramírez" aseguramiento="Andrea Costa" jefes_equipo="Lucía Benítez"'), repo, mostrar=False)
    run(E(f'estado.py --proyecto {G} agil cadencia_iteracion_dias=14 velocidad_referencia=8'), repo, mostrar=False)

def hasta_etapa2(repo, mostrar=False):
    """Atajo de preparación: artefactos mínimos y las tres primeras puertas (inicio, proyecto, etapa 2)."""
    for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"),
                 ("business-case-esquematico", "00-direccion/business-case-esquematico.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
        art(repo, c, r)
    puerta(repo, "autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")
    art(repo, "business-case", "00-direccion/business-case.md", texto="# Business case\n\nBeneficios B-01 (desvío de consultas, SM-2) y B-02 (adopción, SM-1).\n")
    art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
    run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "riesgo=ningún riesgo alto sin respuesta"'), repo, mostrar=False)
    puerta(repo, "autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
    run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"', repo, mostrar=mostrar)
    run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado CONCERNS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26 --nota "NFR-3 sin prueba de carga planificada"'), repo, mostrar=mostrar)
    art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
    puerta(repo, "autorizar-etapa", "Ejecutivo: Laura Méndez", "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=+2 semanas" "costo=±10 %"', decision="condicionado")

def escribir_csv(ruta, cab, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab); w.writeheader(); w.writerows(filas)

def reg_json(repo, *a):
    import json as _j
    r = subprocess.run([PY, f"{EST}/registro.py", "--proyecto", G, *a, "--json"], cwd=repo, capture_output=True, text=True, check=True)
    return _j.loads(r.stdout)

MAPAS = f"{RAIZ}/skills/pm-mapas-estrategicos/scripts/mapas.py"

def captura_seccion(html, png, selector, ancho=1280, alto=720, escala=1.5):
    """Recorte 16:9 (para diapositivas) que empieza en la sección indicada de una página HTML."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": ancho, "height": 900}, device_scale_factor=escala)
            pg.goto("file://" + html); pg.wait_for_timeout(600)
            y = pg.evaluate(f"document.querySelector({json.dumps(selector)}).getBoundingClientRect().top + window.scrollY")
            completa = pg.screenshot(full_page=True); b.close()
        # se recorta la captura de página completa (la misma que da las capturas deterministas de los tableros)
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(completa)); alto_px = round(alto * escala)
        y0 = max(0, min(round((y - 8) * escala), im.height - alto_px))
        im.crop((0, y0, round(ancho * escala), y0 + alto_px)).save(png)
        return True
    except Exception as x:
        print("captura omitida:", x); return False

def tablero(repo, corte, desde, hasta, proximo, objetivos, hitos, decisiones, iteraciones, comentario, fuentes, salida_png=None, actor=None, fecha_fija="", fecha_pronostico="",
            mapas=False, salida_mapas_png=None, juicio_rel=None, moneda=""):
    """pm-visuales arma el tablero con el script del plugin (estado.py periodo --tablero; pm-visuales/references/guia.md §3):
    semáforos por regla, registros, umbrales de estado.json e iteraciones de avance-bmad.csv; lo que es juicio del gestor
    (objetivos sin regla y notas, hitos, decisiones, nombre y plan de cada iteración, comentario) va en un JSON que se
    muestra en la evidencia. Con juicio_rel se usa un juicio ya escrito (el del highlight). `hasta` es siempre el corte.
    Con mapas=True, pm-mapas-estrategicos completa la sección «Mapas estratégicos» (mapas.py tablero --insertar) y, con
    salida_mapas_png, se guarda además un recorte 16:9 que empieza en esa sección."""
    assert hasta == corte
    if juicio_rel is None:
        j = {"objetivos": {o["clave"]: {k: o[k] for k in ("rag", "pronostico", "detalle", "tol_etapa", "tol_proyecto") if o.get(k)} for o in objetivos if o.get("pronostico") != "[por confirmar]"},
             "hitos": hitos, "decisiones": decisiones, "comentario": comentario}
        if iteraciones: j["agil"] = {"iteraciones": iteraciones}
        if fecha_fija or fecha_pronostico: j.setdefault("agil", {}).update({"fecha_fija": fecha_fija, "fecha_pronostico": fecha_pronostico})
        if fuentes: j["fuentes"] = fuentes
        if moneda: j["moneda"] = moneda
        juicio_rel = f"03-control/reportes/{corte}-juicio-gestor.json"
        escribir(repo, juicio_rel, json.dumps(j, ensure_ascii=False, indent=1) + "\n")
        LOG.append((f"(juicio del gestor para el tablero → gestion/{juicio_rel})", "\n".join(f'"{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in j.items())))
    rel = f"03-control/reportes/{corte}-tablero-avance.html"
    run(E(f'estado.py --proyecto {G} periodo --desde {desde} --corte {corte} --proximo {proximo} --juicio {G}/{juicio_rel} --tablero'), repo)
    if mapas:
        run(f'python3 {MAPAS} --proyecto {G} tablero --insertar {G}/{rel}', repo)
    if salida_png and captura_tablero(os.path.join(repo, G, rel), salida_png, actor) and mapas and salida_mapas_png:
        captura_seccion(os.path.join(repo, G, rel), salida_mapas_png, "#s-mapas")
    return os.path.join(repo, G, rel)

def captura_tablero(html, salida_png, actor=None):
    """Captura de página completa del tablero (con ?actor=<Nombre>, la vista por actor del mismo tablero)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("AVISO: playwright no está instalado; se omite la captura del tablero"); return False
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1.5)
        pg.goto("file://" + html + (f"?actor={actor}" if actor else "")); pg.wait_for_timeout(600); pg.screenshot(path=salida_png, full_page=True); b.close()
    return True


def servidores_prueba():
    """Servidor SMTP mínimo y receptor de webhooks en 127.0.0.1 (solo para la corrida de referencia; sin red externa)."""
    import socketserver, threading, http.server
    rec = {"smtp": [], "http": []}
    class SMTPH(socketserver.StreamRequestHandler):
        def handle(self):
            w = lambda x: self.wfile.write((x + "\r\n").encode()); w("220 servidor-de-prueba"); datos = None; m = {"rcpt": []}
            while True:
                l = self.rfile.readline()
                if not l: break
                x = l.decode("utf-8", "replace").rstrip("\r\n")
                if datos is not None:
                    if x == ".": m["data"] = "\n".join(datos); rec["smtp"].append(m); m = {"rcpt": []}; datos = None; w("250 OK")
                    else: datos.append(x)
                    continue
                c = x.upper()
                if c.startswith(("EHLO", "HELO")): w("250 servidor-de-prueba")
                elif c.startswith("RCPT TO"): m["rcpt"].append("rcpt to:" + x[8:]); w("250 OK")   # verbo en minúsculas: smtplib 3.9 envía «rcpt TO:», 3.13 «rcpt to:»
                elif c == "DATA": datos = []; w("354 fin con .")
                elif c == "QUIT": w("221 adios"); break
                else: w("250 OK")
    class HTTPH(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0)); rec["http"].append({"ruta": self.path, "cuerpo": json.loads(self.rfile.read(n))})
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        def log_message(self, *a): pass
    s1 = socketserver.ThreadingTCPServer(("127.0.0.1", 0), SMTPH); s1.daemon_threads = True
    s2 = http.server.ThreadingHTTPServer(("127.0.0.1", 0), HTTPH)
    for x in (s1, s2): threading.Thread(target=x.serve_forever, daemon=True).start()
    env = {"PM_SMTP_HOST": "127.0.0.1", "PM_SMTP_PUERTO": str(s1.server_address[1]), "PM_SMTP_TLS": "ninguno", "PM_SMTP_REMITENTE": "martin.suarez@example.org",
           "PM_TEAMS_WEBHOOK_URL": f"http://127.0.0.1:{s2.server_address[1]}/teams", "PM_SLACK_WEBHOOK_URL": f"http://127.0.0.1:{s2.server_address[1]}/slack",
           "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost"}
    return s1, s2, rec, env

def run_env(cmd, cwd, env_extra, ok=(0,)):
    """Como run(), con variables de entorno extra (las de los servidores de prueba). En el registro se muestran como $PM_…"""
    viejo = {k: os.environ.get(k) for k in env_extra}
    os.environ.update(env_extra)
    try: return run(cmd, cwd, ok=ok)
    finally:
        for k, v in viejo.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v

def captura_html(html, png, ancho=1280, alto=900):
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": ancho, "height": alto}); pg.goto("file://" + html); pg.wait_for_timeout(300)
            pg.screenshot(path=png, full_page=True); b.close()
        return True
    except Exception as x:
        print("captura omitida:", x); return False


# ---- pm-kb (componente opcional, docs/PM-KB.md): búsqueda citada sobre la carpeta del proyecto
_KB_OK = []
def kb_disponible():
    """True si el lanzador de pm-kb existe y su base responde (`pm-kb base estado`). Sin pm-kb, el paso se omite."""
    if not _KB_OK:
        try:
            r = subprocess.run([KB, "base", "estado"], capture_output=True, text=True, timeout=60)
            _KB_OK.append(r.returncode == 0)
        except (OSError, subprocess.TimeoutExpired):
            _KB_OK.append(False)
    return _KB_OK[0]

def kb_omitido(paso):
    """Paso de pm-kb sin pm-kb: se anota y el recorrido sigue."""
    m = f"OMITIDO pm-kb (no instalado): {paso} · instalar con docs/INSTALACION-WSL2.md o docs/INSTALACION-DOCKER.md"
    print(m); LOG.append((f"({m})", "sin pm-kb: `pm-kb base estado` no responde"))

def sin_variables_kb(texto):
    """Lo que cambia en cada corrida se enmascara (como la bitácora en g4): fecha y hora del indexado, fechas reales de
    la bitácora en la historia de una fila, puerto y token de la sesión de `pm-kb servir`; de un enlace compartido, su
    token, su id, quién lo creó (el usuario del sistema), las fechas de creación, vencimiento y último uso; la fecha desde
    la que vale la ubicación de una ficha (la del indexado); y, en la línea del tablero publicado por `indexar` y en la
    ficha (que usan el día de la corrida como corte), el corte y los totales de atención."""
    texto = re.sub(r"indexado \d{4}-\d{2}-\d{2}T[\d:.]+(?:[+-]\d{2}:\d{2})?", "indexado <fecha y hora del indexado>", texto)
    texto = re.sub(r"^(\s*#\d+) \d{4}-\d{2}-\d{2} ", r"\1 <fecha real> ", texto, flags=re.M)
    texto = re.sub(r"(/v#)[A-Za-z0-9_\-]+", r"\1<token del enlace>", texto)
    texto = re.sub(r"\be-[0-9a-f]{8}\b", "e-<id>", texto)
    texto = re.sub(r"\bvence \d{4}-\d{2}-\d{2} \d{2}:\d{2}", "vence <fecha y hora>", texto)
    texto = re.sub(r"\bcreado \d{4}-\d{2}-\d{2} por \S+ \(línea de comandos\)", "creado <fecha> por <usuario del sistema> (línea de comandos)", texto)
    texto = re.sub(r"\búltimo \d{4}-\d{2}-\d{2} \d{2}:\d{2}", "último <fecha y hora>", texto)
    texto = re.sub(r"^(ubicación \([^)\n]*\): [^\n]* · desde )\d{4}-\d{2}-\d{2}$", r"\1<fecha del indexado>", texto, flags=re.M)
    hoy = datetime.date.today().isoformat()
    texto = re.sub(r"^(en el tablero \(versión \d+, corte )" + hoy + r"\)", r"\1<día de la corrida>)", texto, flags=re.M)
    texto = re.sub(r"(publicado · versión \d+(?: \(sin cambios\))? · corte )" + hoy + r"( · [^·\n]* · etapa [^·\n]* · atención: )[^·\n]+",
                   r"\1<día de la corrida>\2<al día de la corrida> ", texto)
    return re.sub(r"http://localhost:\d+/ingresar\?token=\S+", "http://localhost:<puerto>/ingresar?token=<token de la sesión>", texto)

def kb(args, repo, **kw):
    """pm-kb con la salida enmascarada en la evidencia; en el registro el comando se ve como `pm-kb …`."""
    out = run(f'{KB} {args}', repo, mostrar=False, **kw)
    c_, o_ = LOG[-1]; LOG[-1] = (c_, sin_variables_kb(o_)); print("$", c_); print(LOG[-1][1]); print()
    return out

def kb_pie(pg):
    """El pie del portal muestra la fecha y hora del indexado: se enmascara en la captura como en la evidencia."""
    pg.locator("#pie", has_text="indexado").wait_for()   # sin wait_for_function: la CSP de pm-kb no admite eval
    pg.evaluate("const p = document.querySelector('#pie'); p.textContent = p.textContent.replace(/indexado [0-9-]+ [0-9:]+/g, 'indexado <fecha y hora>')")


VISTA_KB = {"width": 1280, "height": 720}     # capturas del portal: 1920×1080 con device_scale_factor 1,5


def kb_capturas(proyecto, pasos):
    """Sirve la interfaz web (`pm-kb servir` en un puerto libre de 127.0.0.1), ingresa con el enlace de la sesión (abre la
    cartera) y captura con playwright cada pantalla de `pasos`: lista de (png, función(página, url_base)); si la función
    devuelve otra página (por ejemplo, la de un contexto limpio para un enlace compartido), se captura esa. Cierra el
    servidor al terminar. Sin playwright, se omiten las capturas con un aviso."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("AVISO: playwright no está instalado; se omiten las capturas de pm-kb"); return []
    kb_exclusivo_inicio()
    try:
        return _kb_capturas(proyecto, pasos, sync_playwright)
    finally:
        kb_exclusivo_fin()


_KB_EXCL = {"n": 0, "f": None}


def kb_exclusivo_inicio():
    """Toma el uso exclusivo de pm-kb entre las guías que corren a la vez sobre la misma base (integración cruzada):
    E2E-1 y E2E-3 indexan y quitan el mismo proyecto, y `pm-kb servir` revoca la sesión local anterior al arrancar.
    Bloqueo de archivo entre procesos, reentrante dentro del proceso; se libera con kb_exclusivo_fin() o al terminar.
    Sin fcntl (Windows) no bloquea: las guías de a una no lo necesitan."""
    if _KB_EXCL["n"] == 0:
        try:
            import fcntl
            d = os.path.join(os.path.expanduser("~"), ".cache", "pm-method")   # no TMPDIR: correr.py fija uno por guía
            os.makedirs(d, exist_ok=True)
            f = open(os.path.join(d, "guias-kb.lock"), "w")
            fcntl.flock(f, fcntl.LOCK_EX)
            _KB_EXCL["f"] = f
        except ImportError:
            pass
    _KB_EXCL["n"] += 1


def kb_exclusivo_fin():
    _KB_EXCL["n"] = max(0, _KB_EXCL["n"] - 1)
    if _KB_EXCL["n"] == 0 and _KB_EXCL["f"]:
        _KB_EXCL["f"].close(); _KB_EXCL["f"] = None


def _kb_capturas(proyecto, pasos, sync_playwright):
    import socket, select, time as _t
    s = socket.socket(); s.bind(("127.0.0.1", 0)); puerto = s.getsockname()[1]; s.close()
    env = {**os.environ, "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost", "PYTHONUNBUFFERED": "1"}
    pr = subprocess.Popen([KB, "servir", "--puerto", str(puerto)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    hechas, enlace, fin = [], None, _t.time() + 30
    try:
        while enlace is None and _t.time() < fin and pr.poll() is None:
            if select.select([pr.stdout], [], [], 1)[0]:
                linea = pr.stdout.readline(); m = re.search(r"(http://\S+/ingresar\?token=\S+)", linea)
                if m: enlace = m.group(1)
        if not enlace:
            print("AVISO: pm-kb servir no mostró el enlace de ingreso; se omiten las capturas"); return []
        LOG.append((f"pm-kb servir --puerto <puerto libre>", sin_variables_kb(linea.strip()) + "\n(ingreso con ese enlace; capturas: " + ", ".join(os.path.basename(p) for p, _ in pasos) + ")"))
        base_url = enlace.split("/ingresar")[0]
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport=VISTA_KB, device_scale_factor=1.5, color_scheme="light")
            pg.set_default_timeout(90000)     # con las cinco guías en paralelo (integración cruzada), el servicio puede tardar
            pg.goto(enlace); pg.wait_for_selector(".cartera")      # el ingreso abre la cartera
            for png, accion in pasos:
                otra = accion(pg, base_url)                     # una acción puede devolver otra página (p. ej., un navegador limpio)
                (otra or pg).screenshot(path=png); hechas.append(png)
            b.close()
    finally:
        pr.terminate()
        try: pr.wait(timeout=10)
        except subprocess.TimeoutExpired: pr.kill()
        # el token de la sesión local no queda activo después de la corrida
        subprocess.run([KB, "token", "revocar", "--persona", "sesión local (servir)"], capture_output=True, text=True)
    return hechas
