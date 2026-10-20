#!/usr/bin/env python3
"""Capa de canales de pm-method · Delivery channels layer.

Envía cualquier comunicación aprobada (comunicado personalizado, informe, recordatorio de acciones, convocatoria, decisión
de puerta, check-in de OKR, acta) a los interesados del maestro (stakeholders.csv) por correo SMTP, webhook de Slack,
webhook de Teams (Workflows), archivo .eml o, a través de un conector MCP conectado en la sesión (el agente envía y este
script registra). Cada mensaje es un .md con frontmatter dentro de 03-control/comunicaciones/<fecha>-<tema>/, generado
por `interesados.py plan-envio` o por `envios.py nuevo --origen <archivo>`.

Reglas: nada sale sin (1) mensaje en estado `aprobado` con `aprobado_por` (acto humano) y (2) `--confirmar` explícito;
sin `--confirmar` todo es simulación. Los destinos se resuelven SIEMPRE contra el maestro vigente (fuente única), no
contra el texto del mensaje. Credenciales solo por variables de entorno; nunca en archivos ni en la salida.

Uso / Usage:
  envios.py --proyecto G nuevo --origen 03-control/reportes/2026-11-20-highlight.md --audiencia "cuadrante:mantener-satisfecho"
            --asunto "Informe de avance 3" [--proposito informe] [--agrupar] [--fecha AAAA-MM-DD]
  envios.py --proyecto G estado CARPETA [--json]
  envios.py --proyecto G aprobar CARPETA [--mensaje ARCHIVO …] --por "Gestor: Nombre"
  envios.py --proyecto G enviar CARPETA --modo smtp|slack-webhook|teams-webhook|eml [--confirmar] [--mensaje ARCHIVO …] [--fecha AAAA-MM-DD]
  envios.py --proyecto G preparar-mcp CARPETA [--canal correo|slack|teams]     # JSON para enviar con un conector MCP
  envios.py --proyecto G registrar CARPETA --mensaje ARCHIVO --modo mcp|eml|manual --referencia X [--estado enviado|fallido]
  envios.py --proyecto G historial [--stakeholder ST-001] [--json]
  envios.py --proyecto G verificar --modo smtp|slack-webhook|teams-webhook  # comprueba variables de entorno (sin red)
Variables de entorno: PM_SMTP_HOST, PM_SMTP_PUERTO (587), PM_SMTP_TLS (starttls|ssl|ninguno), PM_SMTP_USUARIO, PM_SMTP_CLAVE,
PM_SMTP_REMITENTE · PM_SLACK_WEBHOOK_URL · PM_TEAMS_WEBHOOK_URL.
Con PM_SMTP_TLS=ninguno hacia un host que no es de bucle local (127.0.0.1, localhost) se avisa y, si hay usuario y
contraseña, no se envía. Las URL de webhook deben ser https:// (http:// solo hacia bucle local, para pruebas).
`aprobar` y `enviar --confirmar` los confirma siempre una persona: el hook guardian.py pide permiso (docs/SEGURIDAD.md).
"""
import argparse, csv, datetime, glob, json, os, re, smtplib, ssl, sys, time, urllib.parse, urllib.request
from email.message import EmailMessage
from email.utils import make_msgid, formatdate

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-estado-proyecto", "scripts")))
sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-interesados", "scripts")))
import esquema as E
import interesados as I

IDIOMA = "es"
def t(es, en): return en if IDIOMA == "en" else es

CANAL_DE_MODO = {"smtp": "correo", "eml": "correo", "slack-webhook": "slack", "teams-webhook": "teams"}
ENV = {"smtp": ["PM_SMTP_HOST", "PM_SMTP_REMITENTE"], "slack-webhook": ["PM_SLACK_WEBHOOK_URL"], "teams-webhook": ["PM_TEAMS_WEBHOOK_URL"], "eml": []}
MARCAS_SIN_REDACTAR = ("[redactar el mensaje]", "[write the message]")
LIMITE_TEAMS = 28 * 1024      # tamaño máximo de mensaje de Teams Workflows (documentación de Microsoft)

# ------------------------------------------------------------------ mensajes (.md con frontmatter)
def leer_mensaje(p):
    txt = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", txt, re.S)
    if not m: sys.exit(t(f"{p}: sin frontmatter", f"{p}: no front matter"))
    fm = {}
    for l in m.group(1).splitlines():
        if ":" in l:
            k, v = l.split(":", 1); v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] == '"': v = v[1:-1]
            fm[k.strip()] = v
    cuerpo = re.sub(r"<!--.*?-->", "", m.group(2), flags=re.S).strip()
    return fm, cuerpo, txt

def actualizar_fm(p, cambios):
    txt = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?", txt, re.S); lineas = m.group(1).splitlines(); vistos = set()
    for i, l in enumerate(lineas):
        k = l.split(":", 1)[0].strip()
        if k in cambios: lineas[i] = f'{k}: "{cambios[k]}"' if any(c in str(cambios[k]) for c in ":#") else f"{k}: {cambios[k]}"; vistos.add(k)
    for k, v in cambios.items():
        if k not in vistos: lineas.append(f'{k}: "{v}"' if any(c in str(v) for c in ":#") else f"{k}: {v}")
    open(p, "w", encoding="utf-8").write("---\n" + "\n".join(lineas) + "\n---\n" + txt[m.end():])

def mensajes(carpeta, solo=None):
    xs = sorted(glob.glob(os.path.join(carpeta, "mensaje-*.md")))
    if solo: xs = [x for x in xs if os.path.basename(x) in {os.path.basename(s) for s in solo}]
    return xs

def carpeta_ok(proyecto, carpeta):
    c = carpeta if os.path.isabs(carpeta) or os.path.exists(carpeta) else os.path.join(proyecto, carpeta)
    if not os.path.isdir(c): sys.exit(t(f"No existe la carpeta {carpeta}", f"Folder not found: {carpeta}"))
    return c

# ------------------------------------------------------------------ registro de envíos (envios.csv) y diario
def registrar_filas(proyecto, filas_nuevas, fecha=None):
    p = E.asegurar_registro(proyecto, "envios"); cols, filas = E.leer_csv(p); ids = []
    for nf in filas_nuevas:
        previa = next((f for f in filas if f.get("archivo") == nf["archivo"] and f.get("stakeholder_id") == nf["stakeholder_id"]
                       and f.get("estado") in ("pendiente", "fallido")), None)
        if previa: previa.update({k: v for k, v in nf.items() if k in cols and v != ""}); ids.append(previa["id"]); continue
        f = {c: "" for c in cols}; f.update({k: v for k, v in nf.items() if k in cols})
        f["id"] = E.siguiente_id("envios", filas); f["fecha"] = f.get("fecha") or fecha or datetime.date.today().isoformat()
        err = I.validar_valores("envios", f)
        if err: sys.exit("envios.csv: " + "; ".join(err))
        filas.append(f); ids.append(f["id"])
    E.escribir_csv(p, cols, filas)
    return ids

def ya_enviado(proyecto, archivo, sid):
    return any(f.get("archivo") == archivo and f.get("stakeholder_id") == sid and f.get("estado") == "enviado" for f in I.leer(proyecto, "envios"))

def diario(proyecto, texto, quien, fecha=None):
    p = os.path.join(proyecto, "03-control", "registros", "diario.md")
    if os.path.exists(p):
        with open(p, "a", encoding="utf-8") as f: f.write(f"| {fecha or datetime.date.today().isoformat()} | {texto} | {quien} | — |\n")

# ------------------------------------------------------------------ destinatarios: siempre desde el maestro vigente
def destinatarios(proyecto, fm):
    sts = {s["id"]: s for s in I.leer(proyecto, "stakeholders")}; out, errores = [], []
    for sid in [x.strip() for x in fm.get("para", "").split(";") if x.strip()]:
        s = sts.get(sid)
        if not s: errores.append(t(f"{sid} ya no existe en stakeholders.csv", f"{sid} no longer exists in stakeholders.csv")); continue
        canal = fm.get("canal", "")
        destino = s.get("correo", "") if canal == "correo" else (s.get("usuario_chat", "") if canal in ("slack", "teams") else "")
        out.append({"id": sid, "nombre": s.get("nombre", ""), "destino": destino})
    return out, errores

def rel(proyecto, p): return os.path.relpath(p, proyecto)

# ------------------------------------------------------------------ transportes
def env_faltantes(modo): return [v for v in ENV.get(modo, []) if not os.environ.get(v)]

BUCLE_LOCAL = ("127.0.0.1", "localhost", "::1")

def revisar_tls():
    """SEG-04: con PM_SMTP_TLS=ninguno la conexión no se cifra. Hacia un host que no es de bucle local: aviso explícito y,
    si hay usuario y contraseña, rechazo (la contraseña viajaría en claro). Devuelve el error o None."""
    host = (os.environ.get("PM_SMTP_HOST") or "").strip().lower()
    if (os.environ.get("PM_SMTP_TLS") or "starttls").lower() != "ninguno" or host in BUCLE_LOCAL: return None
    if os.environ.get("PM_SMTP_USUARIO") and os.environ.get("PM_SMTP_CLAVE"):
        return t(f"PM_SMTP_TLS=ninguno con usuario y contraseña hacia {host}: la contraseña viajaría sin cifrar. Usar PM_SMTP_TLS=starttls o ssl "
                 "(sin TLS solo se admite un servidor de bucle local, 127.0.0.1 o localhost). No se envió nada.",
                 f"PM_SMTP_TLS=ninguno with user and password to {host}: the password would travel unencrypted. Use PM_SMTP_TLS=starttls or ssl "
                 "(no TLS is only allowed for a loopback server). Nothing sent.")
    print(t(f"AVISO: PM_SMTP_TLS=ninguno: la conexión con {host} no está cifrada (el contenido de los mensajes viaja en claro).",
            f"WARNING: PM_SMTP_TLS=ninguno: the connection to {host} is not encrypted."), file=sys.stderr)
    return None

def revisar_url(modo):
    """SEG-05: la URL del webhook debe ser https:// (http:// solo hacia bucle local, para pruebas). Devuelve el error o None."""
    var = "PM_SLACK_WEBHOOK_URL" if modo == "slack-webhook" else "PM_TEAMS_WEBHOOK_URL"
    u = urllib.parse.urlsplit(os.environ.get(var) or "")
    if u.scheme == "https" and u.hostname: return None
    if u.scheme == "http" and (u.hostname or "").lower() in BUCLE_LOCAL: return None
    return t(f"{var} debe empezar con https:// (http:// solo hacia 127.0.0.1 o localhost). No se envió nada.",
             f"{var} must start with https:// (http:// only to a loopback host). Nothing sent.")

def enviar_smtp(fm, cuerpo, destino):
    host = os.environ["PM_SMTP_HOST"]; puerto = int(os.environ.get("PM_SMTP_PUERTO") or 587)
    tls = (os.environ.get("PM_SMTP_TLS") or "starttls").lower(); usuario = os.environ.get("PM_SMTP_USUARIO", ""); clave = os.environ.get("PM_SMTP_CLAVE", "")
    msg = EmailMessage(); msg["From"] = os.environ.get("PM_SMTP_REMITENTE") or usuario; msg["To"] = destino
    msg["Subject"] = fm.get("asunto", "") or fm.get("tema", ""); msg["Date"] = formatdate(localtime=True); msg["Message-ID"] = make_msgid()
    msg.set_content(cuerpo)
    ctx = ssl.create_default_context()
    srv = smtplib.SMTP_SSL(host, puerto, timeout=30, context=ctx) if tls == "ssl" else smtplib.SMTP(host, puerto, timeout=30)
    try:
        if tls == "starttls": srv.starttls(context=ctx)
        if usuario and clave: srv.login(usuario, clave)
        srv.send_message(msg)
    finally:
        try: srv.quit()
        except Exception: pass
    return msg["Message-ID"]

def post_json(url, datos):
    req = urllib.request.Request(url, data=json.dumps(datos).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read(200).decode("utf-8", "replace")

def enviar_slack(fm, cuerpo, dest):
    menciones = " ".join(f"<@{d['destino']}>" for d in dest if re.match(r"^[UW][A-Z0-9]{6,}$", d["destino"] or ""))
    texto = f"*{fm.get('asunto', '')}*" + (f"\n{menciones}" if menciones else "") + f"\n{cuerpo}"
    st, body = post_json(os.environ["PM_SLACK_WEBHOOK_URL"], {"text": texto})
    if st != 200: raise RuntimeError(f"HTTP {st} {body}")
    return f"slack-webhook HTTP {st}"

def enviar_teams(fm, cuerpo, dest):
    para = ", ".join(d["nombre"] for d in dest)
    carta = {"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": {
        "type": "AdaptiveCard", "$schema": "http://adaptivecards.io/schemas/adaptive-card.json", "version": "1.0",
        "body": [{"type": "TextBlock", "text": fm.get("asunto", ""), "weight": "Bolder", "size": "Medium", "wrap": True},
                 {"type": "TextBlock", "text": t("Para: ", "To: ") + para, "isSubtle": True, "wrap": True},
                 {"type": "TextBlock", "text": cuerpo, "wrap": True}]}}]}
    if len(json.dumps(carta).encode("utf-8")) > LIMITE_TEAMS: raise RuntimeError(t("el mensaje supera 28 KB (límite de Teams Workflows)", "message exceeds 28 KB"))
    st, body = post_json(os.environ["PM_TEAMS_WEBHOOK_URL"], carta)
    if st not in (200, 202): raise RuntimeError(f"HTTP {st} {body}")
    return f"teams-webhook HTTP {st}"

def escribir_eml(carpeta, archivo, fm, cuerpo, d):
    msg = EmailMessage(); msg["To"] = d["destino"]; msg["Subject"] = fm.get("asunto", ""); msg["Date"] = formatdate(localtime=True)
    msg["X-Unsent"] = "1"    # Outlook lo abre como borrador para enviar
    msg.set_content(cuerpo)
    os.makedirs(os.path.join(carpeta, "eml"), exist_ok=True)
    p = os.path.join(carpeta, "eml", f"{archivo[:-3]}-{d['id'].lower()}.eml"); open(p, "wb").write(bytes(msg)); return p

# ------------------------------------------------------------------ comandos
def cmd_estado(proyecto, carpeta, como_json):
    out = []
    for p in mensajes(carpeta):
        fm, cuerpo, _ = leer_mensaje(p)
        out.append({"archivo": os.path.basename(p), "para": fm.get("para"), "canal": fm.get("canal"), "proposito": fm.get("proposito", ""),
                    "estado": fm.get("estado"), "aprobado_por": fm.get("aprobado_por", ""), "redactado": not any(m in cuerpo for m in MARCAS_SIN_REDACTAR)})
    if como_json: print(json.dumps(out, ensure_ascii=False, indent=2)); return
    for x in out: print(f"{x['archivo']}: {x['canal']} → {x['para']} · {x['estado']}" + (f" ({x['aprobado_por']})" if x["aprobado_por"] else "") + ("" if x["redactado"] else t(" · SIN REDACTAR", " · NOT DRAFTED")))

def cmd_aprobar(proyecto, carpeta, solo, por):
    n = 0
    for p in mensajes(carpeta, solo):
        fm, cuerpo, _ = leer_mensaje(p)
        if fm.get("estado") in ("enviado",): continue
        if any(m in cuerpo for m in MARCAS_SIN_REDACTAR) or not cuerpo.strip():
            print(t(f"NO aprobado {os.path.basename(p)}: el cuerpo no está redactado", f"NOT approved {os.path.basename(p)}: body not drafted")); continue
        if "Contenido base (adaptar" in cuerpo or "Base content (adapt" in cuerpo:
            print(t(f"AVISO {os.path.basename(p)}: conserva el título 'Contenido base (adaptar…)'; revisar que se haya adaptado", f"WARNING {os.path.basename(p)}: base heading still present"))
        _, errores = destinatarios(proyecto, fm)
        if errores: print(t(f"NO aprobado {os.path.basename(p)}: ", f"NOT approved {os.path.basename(p)}: ") + "; ".join(errores)); continue
        actualizar_fm(p, {"estado": "aprobado", "aprobado_por": por, "fecha_aprobacion": datetime.date.today().isoformat()}); n += 1
    print(t(f"{n} mensaje(s) aprobados por {por}", f"{n} message(s) approved by {por}"))

def cmd_enviar(proyecto, carpeta, modo, confirmar, solo, fecha=None):
    canal_modo = CANAL_DE_MODO[modo]; falt = env_faltantes(modo)
    if confirmar and falt: sys.exit(t(f"Faltan variables de entorno para {modo}: {', '.join(falt)} (ver docs/INSTALACION.md §0.7). No se envió nada.", f"Missing environment variables for {modo}: {', '.join(falt)}. Nothing sent."))
    if confirmar:
        err = revisar_tls() if modo == "smtp" else (revisar_url(modo) if modo in ("slack-webhook", "teams-webhook") else None)
        if err: sys.exit(err)
    resumen = {"enviados": 0, "fallidos": 0, "omitidos": 0, "simulados": 0}
    for p in mensajes(carpeta, solo):
        fm, cuerpo, _ = leer_mensaje(p); arch = os.path.basename(p)
        if fm.get("canal") != canal_modo:
            resumen["omitidos"] += 1; print(t(f"· {arch}: canal {fm.get('canal')} no corresponde a --modo {modo}", f"· {arch}: channel {fm.get('canal')} does not match {modo}")); continue
        if fm.get("estado") == "enviado": resumen["omitidos"] += 1; print(t(f"· {arch}: ya enviado", f"· {arch}: already sent")); continue
        if fm.get("estado") not in ("aprobado", "parcial", "fallido") or not fm.get("aprobado_por"):
            resumen["omitidos"] += 1; print(t(f"· {arch}: no aprobado (envios.py aprobar … --por)", f"· {arch}: not approved")); continue
        dest, errores = destinatarios(proyecto, fm)
        if errores: resumen["omitidos"] += 1; print(t(f"· {arch}: integridad: ", f"· {arch}: integrity: ") + "; ".join(errores)); continue
        pend = [d for d in dest if not ya_enviado(proyecto, rel(proyecto, p), d["id"])]
        sin_destino = [d for d in pend if not d["destino"] and modo in ("smtp", "eml")]
        if not confirmar:
            resumen["simulados"] += 1
            print(t(f"SIMULACIÓN {arch} [{modo}] → ", f"SIMULATION {arch} [{modo}] → ") + ", ".join(f"{d['id']} <{d['destino'] or '—'}>" for d in pend) + f" · «{fm.get('asunto','')}»")
            print("   " + cuerpo[:240].replace("\n", " ") + ("…" if len(cuerpo) > 240 else ""))
            if sin_destino: print(t("   AVISO sin correo: ", "   WARNING no e-mail: ") + ", ".join(d["id"] for d in sin_destino))
            if falt: print(t(f"   (faltan variables de entorno: {', '.join(falt)})", f"   (missing env vars: {', '.join(falt)})"))
            continue
        filas, ok_all, ok_any = [], True, False
        base = {"canal": canal_modo, "modo": modo, "asunto": fm.get("asunto", ""), "proposito": fm.get("proposito", ""), "archivo": rel(proyecto, p), "confirmado_por": fm.get("aprobado_por", "")}
        try:
            if modo in ("slack-webhook", "teams-webhook"):
                ref = (enviar_slack if modo == "slack-webhook" else enviar_teams)(fm, cuerpo, pend); time.sleep(0.3)
                for d in pend: filas.append({**base, "stakeholder_id": d["id"], "destino": d["destino"] or t("canal del webhook", "webhook channel"), "estado": "enviado", "referencia": ref})
                ok_any = True
            else:
                for d in pend:
                    if not d["destino"]:
                        filas.append({**base, "stakeholder_id": d["id"], "estado": "fallido", "notas": t("sin correo en stakeholders.csv", "no e-mail in stakeholders.csv")}); ok_all = False; continue
                    try:
                        if modo == "smtp":
                            ref = enviar_smtp(fm, cuerpo, d["destino"]); filas.append({**base, "stakeholder_id": d["id"], "destino": d["destino"], "estado": "enviado", "referencia": ref}); ok_any = True
                        else:
                            pe = escribir_eml(carpeta, arch, fm, cuerpo, d)
                            filas.append({**base, "stakeholder_id": d["id"], "destino": d["destino"], "estado": "pendiente", "referencia": rel(proyecto, pe),
                                          "notas": t("abrir el .eml y enviarlo desde el cliente de correo; luego envios.py registrar --modo eml", "open the .eml and send it; then envios.py registrar")}); ok_any = True
                    except Exception as x:
                        filas.append({**base, "stakeholder_id": d["id"], "destino": d["destino"], "estado": "fallido", "notas": f"{type(x).__name__}: {str(x)[:120]}"}); ok_all = False
        except Exception as x:
            for d in pend: filas.append({**base, "stakeholder_id": d["id"], "destino": d["destino"], "estado": "fallido", "notas": f"{type(x).__name__}: {str(x)[:120]}"})
            ok_all = False
        ids = registrar_filas(proyecto, filas, fecha)
        enviados = sum(1 for f in filas if f["estado"] == "enviado"); fallidos = sum(1 for f in filas if f["estado"] == "fallido")
        resumen["enviados"] += enviados; resumen["fallidos"] += fallidos
        nuevo = "enviado" if (ok_all and modo != "eml") else ("eml-generado" if modo == "eml" and ok_all else ("parcial" if ok_any else "fallido"))
        actualizar_fm(p, {"estado": nuevo, "fecha_envio": fecha or datetime.date.today().isoformat()})
        diario(proyecto, t(f"Envío {modo} «{fm.get('asunto','')}» ({fm.get('proposito','')}) a {', '.join(d['id'] for d in pend)}: {enviados} enviados, {fallidos} fallidos ({', '.join(ids)})",
                           f"Delivery {modo} «{fm.get('asunto','')}»: {enviados} sent, {fallidos} failed"), fm.get("aprobado_por", ""), fecha)
        print(f"{arch}: {nuevo} · {', '.join(ids)}")
    print(t(f"Resumen: {resumen['enviados']} enviados, {resumen['fallidos']} fallidos, {resumen['simulados']} simulados, {resumen['omitidos']} omitidos" + ("" if confirmar else " · simulación: agregar --confirmar para enviar"),
            f"Summary: {resumen['enviados']} sent, {resumen['fallidos']} failed, {resumen['simulados']} simulated, {resumen['omitidos']} skipped"))
    if confirmar and resumen["fallidos"]: sys.exit(2)

def cmd_preparar_mcp(proyecto, carpeta, canal):
    out = []
    for p in mensajes(carpeta):
        fm, cuerpo, _ = leer_mensaje(p)
        if canal and fm.get("canal") != canal: continue
        if fm.get("estado") not in ("aprobado", "parcial"): continue
        dest, errores = destinatarios(proyecto, fm)
        out.append({"archivo": os.path.basename(p), "canal": fm.get("canal"), "asunto": fm.get("asunto"), "proposito": fm.get("proposito", ""),
                    "destinatarios": [d for d in dest if not ya_enviado(proyecto, rel(proyecto, p), d["id"])], "errores": errores, "cuerpo": cuerpo,
                    "registrar_despues": f"envios.py --proyecto {proyecto} registrar {rel(proyecto, carpeta)} --mensaje {os.path.basename(p)} --modo mcp --referencia <id del mensaje>"})
    print(json.dumps({"mensajes": out, "nota": t("Enviar con la herramienta MCP conectada SOLO tras mostrar la vista previa y obtener confirmación explícita; luego registrar cada envío.",
                                                   "Send with the connected MCP tool only after preview and explicit confirmation; then register each delivery.")}, ensure_ascii=False, indent=2))

def cmd_registrar(proyecto, carpeta, archivo, modo, referencia, estado, nota, fecha=None):
    p = os.path.join(carpeta, os.path.basename(archivo))
    if not os.path.exists(p): sys.exit(t(f"No existe {archivo} en la carpeta", f"{archivo} not found"))
    fm, _, _ = leer_mensaje(p)
    if estado == "enviado" and (fm.get("estado") not in ("aprobado", "parcial", "eml-generado") or not fm.get("aprobado_por")):
        sys.exit(t("El mensaje no está aprobado: no se registra como enviado.", "Message not approved: cannot be recorded as sent."))
    dest, errores = destinatarios(proyecto, fm)
    if errores: sys.exit("; ".join(errores))
    filas = [{"stakeholder_id": d["id"], "canal": fm.get("canal", ""), "modo": modo, "destino": d["destino"], "asunto": fm.get("asunto", ""), "proposito": fm.get("proposito", ""),
              "archivo": rel(proyecto, p), "estado": estado, "referencia": referencia, "confirmado_por": fm.get("aprobado_por", ""), "notas": nota} for d in dest]
    ids = registrar_filas(proyecto, filas, fecha)
    actualizar_fm(p, {"estado": "enviado" if estado == "enviado" else "fallido", "fecha_envio": fecha or datetime.date.today().isoformat()})
    diario(proyecto, t(f"Envío {modo} «{fm.get('asunto','')}» registrado como {estado} ({', '.join(ids)}; ref {referencia})", f"Delivery {modo} recorded as {estado}"), fm.get("aprobado_por", ""), fecha)
    print(", ".join(ids))

def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("nuevo"); n.add_argument("--origen", required=True); n.add_argument("--audiencia", required=True); n.add_argument("--asunto", required=True)
    n.add_argument("--proposito", default="informe", choices=["comunicado", "informe", "recordatorio", "convocatoria", "puerta", "okr", "acta", "otro"]); n.add_argument("--agrupar", action="store_true"); n.add_argument("--fecha")
    s = sub.add_parser("estado"); s.add_argument("carpeta"); s.add_argument("--json", action="store_true")
    a_ = sub.add_parser("aprobar"); a_.add_argument("carpeta"); a_.add_argument("--mensaje", action="append"); a_.add_argument("--por", required=True)
    e = sub.add_parser("enviar"); e.add_argument("carpeta"); e.add_argument("--modo", required=True, choices=list(CANAL_DE_MODO)); e.add_argument("--confirmar", action="store_true"); e.add_argument("--mensaje", action="append"); e.add_argument("--fecha", help="fecha a registrar (defecto: hoy)")
    pm = sub.add_parser("preparar-mcp"); pm.add_argument("carpeta"); pm.add_argument("--canal", choices=["correo", "slack", "teams"])
    r = sub.add_parser("registrar"); r.add_argument("carpeta"); r.add_argument("--mensaje", required=True); r.add_argument("--modo", required=True, choices=["mcp", "eml", "manual"])
    r.add_argument("--referencia", default=""); r.add_argument("--estado", default="enviado", choices=["enviado", "fallido"]); r.add_argument("--nota", default=""); r.add_argument("--fecha", help="fecha a registrar (defecto: hoy)")
    h = sub.add_parser("historial"); h.add_argument("--stakeholder"); h.add_argument("--json", action="store_true")
    v = sub.add_parser("verificar"); v.add_argument("--modo", required=True, choices=list(CANAL_DE_MODO))
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.proyecto, "estado.json")): sys.exit(f"{a.proyecto}: falta estado.json / not a project folder")
    IDIOMA = E.idioma_de(a.proyecto); I.IDIOMA = IDIOMA
    if a.cmd == "nuevo":
        origen = a.origen if os.path.exists(a.origen) else os.path.join(a.proyecto, a.origen)
        if not os.path.exists(origen): sys.exit(t(f"No existe el origen {a.origen}", f"Source not found: {a.origen}"))
        carpeta, filas, avisos = I.plan_envio(a.proyecto, a.asunto, a.audiencia, a.proposito, origen, a.agrupar, a.fecha)
        print(t(f"Comunicación «{a.asunto}» ({a.proposito}) → {rel(a.proyecto, carpeta)}/ · {len(filas)} destinatarios", f"Communication «{a.asunto}» → {carpeta}"))
        for f in filas: print(f"   {f['stakeholder_id']} {f['nombre']}: {f['canal']} · {f['formato']} · {f['nivel_detalle']} · {f['archivo']}")
        for w in avisos: print("AVISO " + w)
        return
    if a.cmd == "historial":
        fs = [f for f in I.leer(a.proyecto, "envios") if not a.stakeholder or f.get("stakeholder_id") == a.stakeholder]
        if a.json: print(json.dumps(fs, ensure_ascii=False, indent=2)); return
        for f in fs: print(f"{f['id']} {f['fecha']} {f['stakeholder_id']} {f['canal']}/{f['modo']} «{f['asunto']}» [{f['estado']}] {f.get('referencia','')}")
        return
    if a.cmd == "verificar":
        falt = env_faltantes(a.modo); opc = {"smtp": ["PM_SMTP_PUERTO", "PM_SMTP_TLS", "PM_SMTP_USUARIO", "PM_SMTP_CLAVE"]}.get(a.modo, [])
        for vname in ENV[a.modo] + opc: print(f"   {vname}: {t('definida', 'set') if os.environ.get(vname) else t('no definida', 'not set')}")
        err = None if falt else (revisar_tls() if a.modo == "smtp" else (revisar_url(a.modo) if a.modo in ("slack-webhook", "teams-webhook") else None))
        if err: print(err.replace(t(" No se envió nada.", " Nothing sent."), "")); sys.exit(1)
        print(t("Listo para enviar." if not falt else f"Faltan: {', '.join(falt)}", "Ready." if not falt else f"Missing: {', '.join(falt)}")); sys.exit(1 if falt else 0)
    carpeta = carpeta_ok(a.proyecto, a.carpeta)
    if a.cmd == "estado": cmd_estado(a.proyecto, carpeta, a.json)
    elif a.cmd == "aprobar": cmd_aprobar(a.proyecto, carpeta, a.mensaje, a.por)
    elif a.cmd == "enviar": cmd_enviar(a.proyecto, carpeta, a.modo, a.confirmar, a.mensaje, a.fecha)
    elif a.cmd == "preparar-mcp": cmd_preparar_mcp(a.proyecto, carpeta, a.canal)
    elif a.cmd == "registrar": cmd_registrar(a.proyecto, carpeta, a.mensaje, a.modo, a.referencia, a.estado, a.nota, a.fecha)

if __name__ == "__main__":
    main()
