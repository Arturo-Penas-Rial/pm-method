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
    r = subprocess.run(["python3", f"{EST}/registro.py", "--proyecto", G, *a, "--json"], cwd=repo, capture_output=True, text=True, check=True)
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
            mapas=False, salida_mapas_png=None):
    """Receta de pm-visuales/references/guia.md §3: arma el JSON y reemplaza el bloque datos-tablero. Con mapas=True,
    pm-mapas-estrategicos completa la sección opcional «Mapas estratégicos» (mapas.py tablero --insertar) y, con
    salida_mapas_png, se guarda además un recorte 16:9 que empieza en esa sección."""
    import json as _j, pathlib
    e = _j.load(open(os.path.join(repo, G, "estado.json"), encoding="utf-8"))
    datos = {"proyecto": e["proyecto"], "etapa": e["etapa_actual"]["nombre"], "enfoque_entrega": e["enfoque_entrega"],
             "idioma": e["idioma"], "estado": "borrador", "fecha_corte": corte, "periodo_desde": desde, "periodo_hasta": hasta,
             "proximo_hasta": proximo, "riesgos": reg_json(repo, "listar", "riesgos", "--abiertos"),
             "issues": reg_json(repo, "listar", "issues", "--abiertos"), "acciones": reg_json(repo, "listar", "acciones"),
             "resumen_registros": reg_json(repo, "resumen", "--corte", corte), "umbrales_riesgo": {"alto": 15, "medio": 6},
             "objetivos": objetivos, "hitos": hitos, "decisiones_pendientes": decisiones,
             "agil": {"iteraciones": iteraciones, "ventana_velocidad": 3, "fecha_fija": fecha_fija, "fecha_pronostico": fecha_pronostico, "must_en_riesgo": []},
             "comentario_gestor": comentario, "fuentes": fuentes, "fecha_generacion": corte, "confirmado_por": ""}
    T = f"{RAIZ}/skills/pm-visuales/templates/tablero-avance.html"
    html = pathlib.Path(T).read_text(encoding="utf-8")
    bloque = _j.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html = re.sub(r'(<script type="application/json" id="datos-tablero">)(.*?)(</script>)', lambda m: m.group(1) + bloque + m.group(3), html, count=1, flags=re.S)
    rel = f"03-control/reportes/{corte}-tablero-avance.html"
    escribir(repo, rel, html)
    run(E(f'estado.py --proyecto {G} artefacto tablero-avance --ruta {rel} --estado en-revision'), repo, mostrar=False)
    LOG.append((f"(pm-visuales arma el tablero con la receta de references/guia.md §3 → gestion/{rel})", f"riesgos abiertos {len(datos['riesgos'])} · issues {len(datos['issues'])} · acciones {len(datos['acciones'])} · iteraciones {len(iteraciones)}"))
    if mapas:
        run(f'python3 {MAPAS} --proyecto {G} tablero --insertar {G}/{rel}', repo)
    if salida_png:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("AVISO: playwright no está instalado; se omite la captura del tablero"); return os.path.join(repo, G, rel)
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1.5)
            url = "file://" + os.path.join(repo, G, rel) + (f"?actor={actor}" if actor else "")
            pg.goto(url); pg.wait_for_timeout(600); pg.screenshot(path=salida_png, full_page=True); b.close()
        if mapas and salida_mapas_png: captura_seccion(os.path.join(repo, G, rel), salida_mapas_png, "#s-mapas")
    return os.path.join(repo, G, rel)


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
                elif c.startswith("RCPT TO"): m["rcpt"].append(x); w("250 OK")
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
