"""Nivel «integraciones» de la suite de variantes: capa de canales con fallas de entrega y tracker dañado (informe de
cobertura I-01, I-02). Todo en 127.0.0.1, sin red externa.

  I-01  SMTP que rechaza un destinatario (550 en RCPT), que cierra la conexión, que no responde (plazo corto con
        sitio/sitecustomize.py) y webhook de Teams con 500: filas `fallido`, mensaje `fallido`, código 2, sin traza;
        reenvío tras corregir el servidor que solo envía a los faltantes y actualiza la fila fallida (sin duplicar).
  I-02  `envios.py registrar` con `--modo eml` (tras enviar --modo eml) y `--modo mcp` (tras preparar-mcp): EN-### con
        referencia, una fila por destinatario; registrar dos veces no duplica.
  I-03  Instantánea del tracker en otra codificación: riesgos.py candidatos informa el archivo, sin traza.
  I-04  plan de envío sin canal en el perfil: el correo del maestro es el destino (sin el aviso «correo vacío»).
"""
import csv, glob, http.server, json, os, re, socket, socketserver, threading, time
from comun import SITIO, Ejecutor, escribir, leer_csv

G = "g"


class Servidores:
    """SMTP mínimo y receptor HTTP con modos de falla que se cambian en caliente."""
    def __init__(self):
        self.modo_smtp, self.rechazar, self.modo_http = "ok", set(), "ok"
        self.smtp, self.http = [], []
        srv = self
        class SMTPH(socketserver.StreamRequestHandler):
            def handle(self):
                if srv.modo_smtp == "cierra": return                       # acepta y cierra sin saludo
                if srv.modo_smtp == "mudo": time.sleep(6); return            # acepta y no responde
                w = lambda x: self.wfile.write((x + "\r\n").encode())
                w("220 prueba"); datos, m = None, {"rcpt": []}
                while True:
                    l = self.rfile.readline()
                    if not l: break
                    x = l.decode("utf-8", "replace").rstrip("\r\n")
                    if datos is not None:
                        if x == ".": srv.smtp.append(m); m = {"rcpt": []}; datos = None; w("250 OK")
                        else: datos.append(x)
                        continue
                    c = x.upper()
                    if c.startswith(("EHLO", "HELO")): w("250 prueba")
                    elif c.startswith("RCPT TO"):
                        dest = re.search(r"<([^>]+)>", x).group(1).lower()
                        if dest in srv.rechazar: w("550 5.1.1 buzón inexistente")
                        else: m["rcpt"].append(dest); w("250 OK")
                    elif c == "DATA": datos = []; w("354 fin con .")
                    elif c == "QUIT": w("221 adios"); break
                    else: w("250 OK")
        class HTTPH(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0)); cuerpo = self.rfile.read(n)
                if srv.modo_http == "error":
                    self.send_response(500); self.end_headers(); self.wfile.write(b"error interno"); return
                srv.http.append({"ruta": self.path, "cuerpo": json.loads(cuerpo)}); self.send_response(200); self.end_headers(); self.wfile.write(b"1")
            def log_message(self, *a): pass
        self.s1 = socketserver.ThreadingTCPServer(("127.0.0.1", 0), SMTPH); self.s1.daemon_threads = True
        self.s2 = http.server.ThreadingHTTPServer(("127.0.0.1", 0), HTTPH); self.s2.daemon_threads = True
        for x in (self.s1, self.s2): threading.Thread(target=x.serve_forever, daemon=True).start()
        self.env = {"PM_SMTP_HOST": "127.0.0.1", "PM_SMTP_PUERTO": str(self.s1.server_address[1]), "PM_SMTP_TLS": "ninguno",
                    "PM_SMTP_REMITENTE": "pm@example.org", "PM_TEAMS_WEBHOOK_URL": f"http://127.0.0.1:{self.s2.server_address[1]}/teams",
                    "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost",
                    "PYTHONPATH": SITIO, "PM_PRUEBA_SMTP_PLAZO": "2"}
    def cerrar(self):
        for x in (self.s1, self.s2): x.shutdown(); x.server_close()


def correr(base, reg, py):
    d = os.path.join(base, "canales"); os.makedirs(d, exist_ok=True)
    sv = Servidores()
    try:
        _correr(d, reg, py, sv)
    finally:
        sv.cerrar()


def _correr(d, reg, py, sv):
    x = Ejecutor(reg, py, sv.env, cwd=d)
    P = os.path.join(d, G); REG = os.path.join(P, "03-control", "registros")
    envios = lambda: leer_csv(os.path.join(REG, "envios.csv")) if os.path.exists(os.path.join(REG, "envios.csv")) else []
    fm = lambda p: dict(re.findall(r"^(\w+): ?\"?([^\"\n]*)\"?$", open(p, encoding="utf-8").read().split("---")[1], re.M))
    x("nuevo", "--ruta", G, "--nombre", "Canales", "--ejecutivo", "Laura Méndez", "--gestor", "Martín Suárez", "--fecha", "2026-10-01")
    for n, c, u in (("Laura Méndez", "laura@example.org", ""), ("Diego Ferreira", "diego@example.org", ""), ("Ana Ríos", "ana@example.org", ""),
                    ("Sofía Ramírez", "sofia@example.org", "sofia.ramirez")):
        x("registro", "--proyecto", G, "agregar", "stakeholders", "--campo", f"nombre={n}", "--campo", f"correo={c}", *(["--campo", f"usuario_chat={u}"] if u else []))
    escribir(os.path.join(d, "base.md"), "Avance de la etapa 2: verde; sin decisiones pendientes.\n")

    def comunicacion(tema, audiencia, fecha, canal=None, por="Gestor: Martín Suárez"):
        r = x("envios", "--proyecto", G, "nuevo", "--origen", "base.md", "--audiencia", audiencia, "--asunto", tema, "--proposito", "informe", "--fecha", fecha, paso=f"nuevo «{tema}»")
        carpeta = glob.glob(os.path.join(P, "03-control", "comunicaciones", f"{fecha}-*"))[-1]
        for m in sorted(glob.glob(os.path.join(carpeta, "mensaje-*.md"))):
            t = open(m, encoding="utf-8").read().replace("## Contenido base (adaptar al perfil y borrar este título)\n\n", "")
            if canal: t = re.sub(r"^canal: .*$", f"canal: {canal}", t, count=1, flags=re.M)
            escribir(m, t)
        x("envios", "--proyecto", G, "aprobar", os.path.relpath(carpeta, d), "--por", por, paso=f"aprobar «{tema}»")
        return r, os.path.relpath(carpeta, d), carpeta

    # I-04 · plan de envío: sin canal en el perfil, el destino es el correo del maestro
    r, c1, abs1 = comunicacion("Avance", "ST-001,ST-002,ST-003", "2026-11-02")
    plan = leer_csv(os.path.join(abs1, "plan-envio.csv"))
    reg.check("I-04 plan de envío sin canal en el perfil: destino = correo del maestro y sin el aviso «correo vacío»",
              "correo vacío" not in r.todo and [f["destino"] for f in plan] == ["laura@example.org", "diego@example.org", "ana@example.org"], r.todo[-300:] + str([f["destino"] for f in plan]))

    # I-01a · SMTP que rechaza un destinatario (550)
    sv.rechazar = {"ana@example.org"}
    e1 = x("envios", "--proyecto", G, "enviar", c1, "--modo", "smtp", "--confirmar", "--fecha", "2026-11-02", ok=(2,), paso="SMTP con un destinatario rechazado")
    f1 = {f["stakeholder_id"]: f for f in envios()}
    msg3 = glob.glob(os.path.join(abs1, "mensaje-*st-003.md"))[0]
    reg.check("I-01 SMTP 550 a un destinatario: código 2, ST-001 y ST-002 enviados, ST-003 fallido con el motivo, su mensaje queda «fallido»",
              e1.rc == 2 and {k: v["estado"] for k, v in f1.items()} == {"ST-001": "enviado", "ST-002": "enviado", "ST-003": "fallido"}
              and "Refused" in f1.get("ST-003", {}).get("notas", "") and fm(msg3).get("estado") == "fallido" and "1 fallidos" in e1.out,
              e1.todo[-300:] + str({k: (v["estado"], v["notas"][:60]) for k, v in f1.items()}))
    # reenvío: solo al faltante; la fila fallida se actualiza
    sv.rechazar = set(); antes = len(sv.smtp)
    e2 = x("envios", "--proyecto", G, "enviar", c1, "--modo", "smtp", "--confirmar", "--fecha", "2026-11-03", paso="reenvío SMTP")
    f2 = envios()
    reg.check("I-01 reenvío tras corregir el servidor: solo ST-003 recibe (1 correo nuevo), la fila fallida pasa a «enviado» sin duplicar (3 filas)",
              e2.rc == 0 and len(sv.smtp) - antes == 1 and sv.smtp[-1]["rcpt"] == ["ana@example.org"] and len(f2) == 3 and {f["estado"] for f in f2} == {"enviado"},
              e2.todo[-300:] + str([(f["id"], f["stakeholder_id"], f["estado"]) for f in f2]))
    e3 = x("envios", "--proyecto", G, "enviar", c1, "--modo", "smtp", "--confirmar", paso="tercer envío (ya enviado)")
    reg.check("I-01 un tercer envío no reenvía nada (ya enviado)", e3.rc == 0 and len(sv.smtp) - antes == 1 and len(envios()) == 3, e3.out[-200:])

    # I-01b · SMTP que cierra la conexión y que no responde (plazo de 2 s)
    for modo, tema, fecha, motivo in (("cierra", "Cierre de conexion", "2026-11-04", r"Disconnected|Reset|closed"), ("mudo", "Sin respuesta", "2026-11-05", r"timed out|timeout|Timeout")):
        _, c, ab = comunicacion(tema, "ST-001", fecha)
        sv.modo_smtp = modo; t0 = time.time()
        r_ = x("envios", "--proyecto", G, "enviar", c, "--modo", "smtp", "--confirmar", "--fecha", fecha, ok=(2,), paso=f"SMTP {modo}")
        dur = time.time() - t0; sv.modo_smtp = "ok"
        fila = [f for f in envios() if f["archivo"].startswith(os.path.relpath(ab, P))]
        reg.check(f"I-01 SMTP que {'cierra la conexión' if modo == 'cierra' else 'no responde (plazo de 2 s)'}: código 2, fila «fallido» con el motivo, sin traza"
                  + ("" if modo == "cierra" else ", en menos de 20 s"),
                  r_.rc == 2 and len(fila) == 1 and fila[0]["estado"] == "fallido" and re.search(motivo, fila[0]["notas"]) and (modo == "cierra" or dur < 20),
                  r_.todo[-300:] + str([(f["estado"], f["notas"]) for f in fila]))

    # I-01c · webhook de Teams con 500 y reenvío
    _, c4, ab4 = comunicacion("Puerta de etapa", "ST-004", "2026-11-06", canal="teams", por="Ejecutiva: Laura Méndez")
    sv.modo_http = "error"
    w1 = x("envios", "--proyecto", G, "enviar", c4, "--modo", "teams-webhook", "--confirmar", "--fecha", "2026-11-06", ok=(2,), paso="webhook 500")
    fw = [f for f in envios() if f["archivo"].startswith(os.path.relpath(ab4, P))]
    reg.check("I-01 webhook de Teams con 500: código 2, fila «fallido» con HTTP 500, sin traza",
              w1.rc == 2 and len(fw) == 1 and fw[0]["estado"] == "fallido" and "500" in fw[0]["notas"], w1.todo[-300:] + str(fw))
    sv.modo_http = "ok"
    w2 = x("envios", "--proyecto", G, "enviar", c4, "--modo", "teams-webhook", "--confirmar", "--fecha", "2026-11-07", paso="webhook reenvío")
    fw = [f for f in envios() if f["archivo"].startswith(os.path.relpath(ab4, P))]
    reg.check("I-01 webhook reenvío: entregado (1 POST), la fila pasa a «enviado» sin duplicar", w2.rc == 0 and len(sv.http) == 1 and len(fw) == 1 and fw[0]["estado"] == "enviado",
              w2.todo[-300:] + str(fw))

    # I-02a · .eml y registrar --modo eml (dos veces)
    _, c5, ab5 = comunicacion("Acta del comite", "ST-001,ST-002", "2026-11-09")
    x("envios", "--proyecto", G, "enviar", c5, "--modo", "eml", "--confirmar", "--fecha", "2026-11-09", paso="enviar --modo eml")
    rel5 = os.path.relpath(ab5, P)
    pend = [f for f in envios() if f["archivo"].startswith(rel5)]
    emls = glob.glob(os.path.join(ab5, "*.eml")) + glob.glob(os.path.join(ab5, "*", "*.eml"))
    reg.check("I-02 enviar --modo eml: un .eml por destinatario y filas «pendiente»", len(emls) == 2 and [f["estado"] for f in pend] == ["pendiente", "pendiente"], str(pend)[:300])
    m5 = sorted(glob.glob(os.path.join(ab5, "mensaje-*.md")))
    for m in m5:
        x("envios", "--proyecto", G, "registrar", c5, "--mensaje", os.path.basename(m), "--modo", "eml", "--referencia", "enviado desde el cliente de correo",
          "--fecha", "2026-11-09", paso="registrar --modo eml")
    reg_eml = [f for f in envios() if f["archivo"].startswith(rel5)]
    r2 = x("envios", "--proyecto", G, "registrar", c5, "--mensaje", os.path.basename(m5[0]), "--modo", "eml", "--referencia", "otra vez", ok=(1,), paso="registrar --modo eml (repetido)")
    reg.check("I-02 registrar --modo eml: las filas pendientes pasan a «enviado» con la referencia (2 filas); repetirlo se rechaza y no duplica",
              [f["estado"] for f in reg_eml] == ["enviado", "enviado"] and all(f["referencia"] == "enviado desde el cliente de correo" for f in reg_eml)
              and r2.rc == 1 and len([f for f in envios() if f["archivo"].startswith(rel5)]) == 2, str([(f["estado"], f["referencia"]) for f in reg_eml]) + r2.todo[-200:])

    # I-02b · preparar-mcp y registrar --modo mcp (dos veces)
    _, c6, ab6 = comunicacion("Recordatorio", "ST-003", "2026-11-10")
    pm = x("envios", "--proyecto", G, "preparar-mcp", c6, paso="preparar-mcp")
    pj = pm.json() or {}
    reg.check("I-02 preparar-mcp: JSON con el destinatario y el comando para registrar después",
              len(pj.get("mensajes", [])) == 1 and pj["mensajes"][0]["destinatarios"][0]["destino"] == "ana@example.org" and "--modo mcp" in pj["mensajes"][0]["registrar_despues"], pm.out[:300])
    m6 = glob.glob(os.path.join(ab6, "mensaje-*.md"))[0]
    x("envios", "--proyecto", G, "registrar", c6, "--mensaje", os.path.basename(m6), "--modo", "mcp", "--referencia", "msg-123", "--fecha", "2026-11-10", paso="registrar --modo mcp")
    r3 = x("envios", "--proyecto", G, "registrar", c6, "--mensaje", os.path.basename(m6), "--modo", "mcp", "--referencia", "msg-124", ok=(1,), paso="registrar --modo mcp (repetido)")
    f6 = [f for f in envios() if f["archivo"].startswith(os.path.relpath(ab6, P))]
    reg.check("I-02 registrar --modo mcp: EN-### «enviado» con la referencia msg-123; repetirlo se rechaza y no duplica",
              len(f6) == 1 and f6[0]["estado"] == "enviado" and f6[0]["referencia"] == "msg-123" and f6[0]["modo"] == "mcp" and r3.rc == 1, str(f6) + r3.todo[-200:])
    ids = [f["id"] for f in envios()]
    reg.check("envios.csv: ids únicos y una fila por (mensaje, destinatario)", len(ids) == len(set(ids))
              and len({(f["archivo"], f["stakeholder_id"]) for f in envios()}) == len(ids), ids)
    h = x("envios", "--proyecto", G, "historial", "--json", paso="historial --json")
    reg.check("envios.py historial --json: JSON válido", h.json() is not None, h.out[:200])

    # I-03 · instantánea del tracker en otra codificación y mal formada
    fu = os.path.join(P, "03-control", "fuentes"); os.makedirs(fu, exist_ok=True)
    with open(os.path.join(fu, "jira-2026-11-11.csv"), "wb") as fh:
        fh.write("clave,tipo,titulo,prioridad,estado,etiquetas\nPS-1,bug,Caída del módulo de pagos,alta,bloqueado,riesgo\n".encode("cp1252"))
    t1 = x("riesgos", "--proyecto", G, "candidatos", "--fuentes", "tracker", "--fecha", "2026-11-11", ok=(1,), paso="tracker en cp1252")
    reg.check("I-03 instantánea del tracker en cp1252: riesgos.py candidatos termina con código 1 y nombra el archivo y «UTF-8» (antes: traza)",
              t1.rc == 1 and "jira-2026-11-11.csv" in t1.err and "UTF-8" in t1.err, t1.todo[-300:])
    os.remove(os.path.join(fu, "jira-2026-11-11.csv"))
    escribir(os.path.join(fu, "jira-2026-11-12.csv"), 'clave,tipo,titulo,prioridad,estado,etiquetas\nPS-2,bug,"Comilla sin cerrar,alta,bloqueado,riesgo\nPS-3,historia\n')
    t2 = x("riesgos", "--proyecto", G, "candidatos", "--fuentes", "tracker", "--json", "--fecha", "2026-11-12", ok=(0, 1), paso="tracker mal formado")
    reg.check("I-03 instantánea con comilla sin cerrar y fila corta: sin traza; JSON válido o mensaje con el archivo",
              (t2.rc == 0 and t2.json() is not None) or (t2.rc == 1 and "jira-2026-11-12.csv" in t2.err), t2.todo[-300:])
    s = x("sanidad", "--proyecto", G, "--json", ok=(0, 1), paso="sanidad con instantánea mal formada")
    reg.check("sanidad con una instantánea del tracker mal formada: JSON válido, sin traza", s.json() is not None, s.todo[-200:])
