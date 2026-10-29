#!/usr/bin/env python3
"""Arma el paquete de puerta o de cierre (ZIP) con manifiesto, a partir de estado.json y la carpeta del proyecto.
Builds the gate or closure package (ZIP) with a manifest from estado.json and the project folder.

Solo biblioteca estándar. No convierte formatos: incluye los Markdown/CSV tal cual y, si existen en exportados/,
los .docx/.xlsx/.pptx más recientes del mismo tipo. Para convertir, usar antes exportar.py o las skills oficiales.

Uso / Usage:
  python3 paquete.py --proyecto ./p puerta autorizar-etapa [--salida exportados/2026-10-16-paquete-autorizar-etapa-v1.zip] [--extra ruta ...]
  python3 paquete.py --proyecto ./p cierre [--salida ...] [--extra ruta ...]
  python3 paquete.py --proyecto ./p listar puerta autorizar-proyecto     # muestra obligatorios/opcionales y qué falta, sin crear ZIP
  python3 paquete.py --proyecto ./p auditoria [--desde AAAA-MM-DD] [--hasta AAAA-MM-DD] [--proposito "auditoría interna"]
                     [--externo] [--con-bitacora] [--salida exportados/<hoy>-expediente-auditoria.zip] [--extra ruta ...]
  python3 paquete.py --proyecto ./p verificar exportados/<hoy>-expediente-auditoria.zip   # rehash contra SHA256SUMS (código 1 si no coincide)
Expediente de auditoría (PMO, auditoría interna, due diligence o entrega al cliente): INDICE.md e INDICE.html (escapado)
navegables, cronologia.csv (puertas, decisiones, aprobaciones, cambios decididos, riesgos aceptados, productos aceptados y
envíos), estado.json, líneas base congeladas de 00-direccion/historial/, registros (con período: filas fechadas en él y sin
fecha), evidencia de puertas (00-direccion/decisiones/), actas, informes, cortes de EVM y comunicaciones, hallazgos de
sanidad al corte (--hasta o hoy), MANIFIESTO.md y SHA256SUMS con la huella de cada archivo; con --con-bitacora, también la
bitácora de escrituras completa (bitacora.jsonl), que `verificar` usa para explicar un registro alterado. Los paquetes de puerta ya
generados se citan con su huella y no se reincluyen. Con período, los archivos fechados en su nombre fuera de él se omiten.
--externo (cliente, proveedor, due diligence): sin el registro de interesados ni sus valoraciones (stakeholders,
estereotipos, preferencias) y sin el destino (correo o canal) de los envíos.
Salida: ZIP con los artefactos + MANIFIESTO.md. Si falta un obligatorio o alguno sigue en borrador, el nombre lleva -BORRADOR (los productos que la puerta decide pueden ir "en-revision").
Solo se incluyen archivos dentro de la carpeta del proyecto: una ruta de estado.json o de --extra que resuelve fuera de ella
(absoluta, con ../ o por un enlace simbólico) se excluye y queda anotada en el manifiesto, salvo --permitir-externos.
"""
import argparse, csv, datetime, glob, hashlib, html, io, json, os, re, subprocess, sys, zipfile

# Claves canónicas de estado.json.artefactos (ver pm-estado-proyecto/SKILL.md, "Claves de artefactos") o patrones de
# archivo si no están registradas, por tipo de paquete. {n} = etapa actual, {n1} = siguiente etapa.
# Cada entrada: (clave, [patrones glob relativos al proyecto, en orden de preferencia], obligatorio)
# El documento de solicitud de decisión (pm-direccion-decisiones) usa la clave solicitud-<puerta>; el ZIP que genera
# este script se registra, si se desea, como exportado-paquete-<puerta> y nunca se reincluye.
PAQUETES = {
    "autorizar-inicio": [
        ("project-brief", ["01-inicio/project-brief.md", "01-inicio/*brief*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], False),  # esquemático: suele vivir en el brief
        ("estructura-organizativa", ["00-direccion/estructura-organizativa.md", "00-direccion/*estructura*.md"], True),
        ("plan-etapa-1", ["02-planificacion/plan-etapa-1*.md"], True),
        ("descripcion-producto-proyecto", ["02-planificacion/descripcion-producto-proyecto.md", "02-planificacion/productos/descripcion-producto-proyecto.md"], False),  # puede venir dentro del brief
        ("solicitud-autorizar-inicio", ["00-direccion/decisiones/*solicitud-autorizar-inicio*.md", "00-direccion/decisiones/*paquete-autorizar-inicio*.md"], False),
        ("canvas-arranque", ["01-inicio/*canvas*"], False),
        ("mandato", ["00-direccion/mandato.md", "01-inicio/mandato.md"], False),
    ],
    "autorizar-proyecto": [
        ("pid", ["00-direccion/pid.md", "00-direccion/*pid*.md", "01-inicio/*pid*.md", "01-inicio/*acta-constitucion*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("plan-proyecto", ["02-planificacion/plan-proyecto.md", "02-planificacion/*plan-proyecto*.md", "02-planificacion/*plan-de-proyecto*.md"], True),
        ("plan-etapa-{n1}", ["02-planificacion/plan-etapa-{n1}*.md"], True),
        ("enfoques", ["02-planificacion/enfoques/*.md"], False),
        ("pbs-wbs", ["02-planificacion/pbs-wbs.md", "02-planificacion/wbs.csv"], False),
        ("cronograma", ["02-planificacion/cronograma.md", "02-planificacion/cronograma.xml"], False),
        ("presupuesto", ["02-planificacion/presupuesto.md"], False),
        ("estrategia-adquisiciones", ["02-planificacion/adquisiciones/*estrategia*.md"], False),
        ("bmad-prd", ["00-direccion/historial/bmad-prd-v*/prd.md", "02-planificacion/especificacion/spec-index.json"], False),
        ("solicitud-autorizar-proyecto", ["00-direccion/decisiones/*solicitud-autorizar-proyecto*.md", "00-direccion/decisiones/*paquete-autorizar-proyecto*.md"], False),
        ("registros", ["03-control/registros/*.csv"], False),
    ],
    "autorizar-etapa": [
        ("informe-fin-etapa-{n}", ["03-control/reportes/*informe-fin-etapa-{n}*.md", "03-control/reportes/*informe-fin-etapa*.md", "03-control/reportes/*end-stage*.md"], True),
        ("plan-etapa-{n1}", ["02-planificacion/plan-etapa-{n1}*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("plan-proyecto", ["02-planificacion/plan-proyecto.md", "02-planificacion/*plan-proyecto*.md"], True),
        ("solicitud-autorizar-etapa", ["00-direccion/decisiones/*solicitud-autorizar-etapa*.md", "00-direccion/decisiones/*paquete-autorizar-etapa*.md"], False),
        ("registros", ["exportados/*registros*.xlsx", "03-control/registros/*.csv"], False),
        ("tablero-avance", ["03-control/reportes/*tablero-avance*.html"], False),
    ],
    "autorizar-plan-excepcion": [
        ("informe-excepcion", ["03-control/reportes/*informe-excepcion*.md"], True),
        ("plan-excepcion", ["02-planificacion/*plan-excepcion*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("plan-proyecto", ["02-planificacion/plan-proyecto.md", "02-planificacion/*plan-proyecto*.md"], False),
        ("evaluacion-excepcion", ["00-direccion/decisiones/*evaluacion-excepcion*.md"], False),
        ("solicitud-autorizar-plan-excepcion", ["00-direccion/decisiones/*solicitud-autorizar-plan-excepcion*.md", "00-direccion/decisiones/*paquete-autorizar-plan-excepcion*.md"], False),
        ("registros", ["exportados/*registros*.xlsx", "03-control/registros/*.csv"], False),
    ],
    "cierre": [
        ("informe-fin-proyecto", ["04-cierre/informe-fin-proyecto.md", "04-cierre/*fin-proyecto*.md"], True),
        ("registro-aceptacion", ["04-cierre/registro-aceptacion.md", "04-cierre/*aceptacion-producto-proyecto*.md", "04-cierre/*aceptacion*.md"], True),
        ("informe-lecciones", ["04-cierre/informe-lecciones.md", "04-cierre/*lecciones*.md"], True),
        ("recomendaciones-seguimiento", ["04-cierre/recomendaciones-seguimiento.md", "04-cierre/*seguimiento*.md", "04-cierre/*recomendaciones*.md"], True),
        ("plan-revision-beneficios", ["04-cierre/plan-revision-beneficios.md", "00-direccion/enfoque-beneficios.md"], True),
        ("business-case-original", ["00-direccion/historial/business-case-v1.0*.md", "00-direccion/historial/*business-case*1.0*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("pid-original", ["00-direccion/historial/pid-v1.0*.md", "00-direccion/historial/*pid*1.0*.md"], False),
        ("registros", ["exportados/*registros*.xlsx", "03-control/registros/*.csv"], True),
        ("solicitud-autorizar-cierre", ["00-direccion/decisiones/*solicitud-autorizar-cierre*.md", "00-direccion/decisiones/*paquete-autorizar-cierre*.md"], False),
        ("handover", ["04-cierre/handover.md", "04-cierre/*traspaso*.md"], False),
        ("cierre-contratos", ["04-cierre/cierre-contrato-*.md"], False),
        ("notificacion-cierre", ["04-cierre/notificacion-cierre.md"], False),
        ("acta-junta", ["00-direccion/decisiones/*acta-*.md"], False),
    ],
}
# Estados aceptables para presentar a la puerta: lo que se decide en la puerta puede venir "en-revision".
ESTADOS_OK = ("aprobado", "en-revision", "registro")

def frontmatter(path):
    """Devuelve dict con version/estado/aprobado_por/tipo del frontmatter YAML simple (o del comentario HTML)."""
    meta = {"version": "", "estado": "", "aprobado_por": "", "tipo": ""}
    try:
        txt = open(path, encoding="utf-8", errors="replace").read(4000)
    except OSError:
        return meta
    for k in meta:
        m = re.search(rf"^{k}:\s*\"?([^\"\n]*)\"?\s*$", txt, re.M)
        if m: meta[k] = m.group(1).strip()
    return meta

def estado_congelada(proyecto, estado, ruta):
    """Copia congelada en 00-direccion/historial/ sin front matter: el estado sale del registro de aprobación
    (estado.json.artefactos[*].copia_congelada, o la decisión «aprobado <clave> v<versión>» de decisiones.csv que anota
    estado.py aprobar). Devuelve (estado, version, aprobado_por) o None si no es una copia congelada reconocible."""
    rel = os.path.relpath(ruta, proyecto).replace(os.sep, "/")
    m = re.match(r"^00-direccion/historial/(?P<clave>[^/]+?)-v(?P<ver>[^/]+)$", os.path.splitext(rel)[0])
    if not m: return None
    clave, ver = m.group("clave"), m.group("ver")
    registrada = None
    for art in (estado.get("artefactos") or {}).values():
        if (art.get("copia_congelada") or "").replace(os.sep, "/") == rel:
            registrada = art
            if str(art.get("version", "")) == ver and art.get("aprobado_por"): return "aprobado", ver, art["aprobado_por"]
    p = os.path.join(proyecto, "03-control", "registros", "decisiones.csv")
    if os.path.exists(p):
        try:
            with open(p, newline="", encoding="utf-8") as fh: filas = list(csv.DictReader(fh))
        except (OSError, csv.Error): filas = []
        for f in reversed(filas):
            if (f.get("decision") or "").strip() == f"aprobado {clave} v{ver}":
                return "aprobado", ver, f.get("decidido_por", "")
    return ("aprobado", ver, "") if registrada else None

def _orden(k):
    return [(0, int(x), "") if x.isdigit() else (1, 0, x) for x in re.split(r"[-.]", k)]

def resolver(proyecto, estado, clave, patrones):
    """Busca el artefacto: estado.json.artefactos (clave exacta o numerada), luego patrones en orden de preferencia."""
    arts = estado.get("artefactos") or {}
    art = arts.get(clave)
    if not art:
        cand = sorted((k for k in arts if k.startswith(clave + "-") and not k.startswith("exportado-")), key=_orden)
        art = arts[cand[-1]] if cand else None
    if art and art.get("ruta") and os.path.exists(os.path.join(proyecto, art["ruta"])):
        return [os.path.join(proyecto, art["ruta"])], art
    for p in patrones:
        hallados = [h for h in glob.glob(os.path.join(proyecto, p)) if not h.endswith(".zip")]
        if not hallados: continue
        if clave in ("registros", "enfoques"):
            xlsx = sorted((h for h in hallados if h.endswith(".xlsx")), key=os.path.getmtime)
            return (xlsx[-1:] if xlsx else sorted(hallados)), None
        return [max(hallados, key=os.path.getmtime)], None
    return [], None

def fuera_del_proyecto(proyecto, ruta):
    """True si la ruta (relativa a la carpeta de trabajo, como las que devuelve resolver() y las de --extra, o absoluta)
    resuelve fuera de la carpeta del proyecto (SEG-06)."""
    base = os.path.realpath(proyecto)
    r = os.path.realpath(ruta)
    return os.path.commonpath([base, r]) != base

# ================================================================== expediente de auditoría y verificación de integridad
# PRINCE2 7: líneas base y gestión de configuración (pista de auditoría de todos los cambios, archivo de versiones anteriores,
# aprobación del nivel correcto: prince2-practicas-riesgo-issues-progreso-productos.md §3.c.4), registro del proyecto (A13) y
# enfoque de gestión de datos (integridad, auditorías de datos: §4.d). PMBOK 8: auditorías (pmbok8-artefactos-tecnicas-anexos.md).
# El expediente consolida lo que ya está en la carpeta del proyecto: no dictamina, no aprueba y no reescribe nada.
FECHA_CSV = {"riesgos": ("fecha_identificacion", "fecha_revision"), "issues": ("fecha", "fecha_cierre"), "cambios": ("fecha", "fecha_decision"),
             "decisiones": ("fecha",), "supuestos": ("fecha", "fecha_validacion"), "lecciones": ("fecha",), "calidad": ("fecha_prevista", "fecha_real"),
             "acciones": ("fecha", "fecha_compromiso", "fecha_cierre"), "preferencias": ("fecha",), "envios": ("fecha",)}
PERSONALES = {"envios": ("destino",)}
VALORACIONES = ("stakeholders", "estereotipos", "preferencias")   # regla 12 de pm-exportar: nunca a un destinatario externo
ARCHIVO_SUMAS = "SHA256SUMS"
TOPE_PANTALLA = 15
ARCHIVO_BITACORA_ZIP = "bitacora.jsonl"   # copia de <proyecto>/.bitacora.jsonl en el expediente (auditoria --con-bitacora)

def _t(e, es, en): return en if (e or {}).get("idioma") == "en" else es

def _en_rango(f, desde, hasta):
    return bool(f) and (not desde or f >= desde) and (not hasta or f <= hasta)

def _fecha_nombre(rel):
    """Fecha AAAA-MM-DD al comienzo del nombre del archivo o de alguna carpeta de su ruta (o None)."""
    for parte in reversed(rel.replace(os.sep, "/").split("/")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})", parte)
        if m: return m.group(1)
    return None

def _sha(datos): return hashlib.sha256(datos).hexdigest()

def _csv_texto(cols, filas):
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    return buf.getvalue()

def _md(x): return str(x if x is not None else "").replace("|", "/").replace("\n", " ")

def cronologia(proyecto, estado, desde, hasta):
    """Decisiones, puertas, cambios decididos, riesgos aceptados, productos aceptados y envíos, en orden de fecha."""
    leer = lambda reg: list(csv.DictReader(open(os.path.join(proyecto, "03-control", "registros", f"{reg}.csv"), encoding="utf-8"))) \
        if os.path.exists(os.path.join(proyecto, "03-control", "registros", f"{reg}.csv")) else []
    ev = []; ids_puerta = set()
    for p in estado.get("puertas") or []:
        ver = (p.get("verificacion") or {})
        ev.append({"fecha": p.get("fecha", ""), "tipo": "puerta", "id": p.get("decision_id", ""), "que": f"{p.get('tipo')}: {p.get('decision')}"
                   + (f" — condiciones: {p['condiciones']}" if p.get("condiciones") else "") + (" (FORZADA)" if p.get("forzada") else ""),
                   "quien": p.get("por", ""), "evidencia": ver.get("lista", "") + (f" · lista confirmada por {ver['confirmada_por']}" if ver.get("confirmada_por") else "")})
        if p.get("decision_id"): ids_puerta.add(p["decision_id"])
    for d in leer("decisiones"):
        if d.get("id") in ids_puerta: continue
        ev.append({"fecha": d.get("fecha", ""), "tipo": "aprobacion" if (d.get("decision") or "").startswith("aprobado ") else "decision", "id": d.get("id", ""),
                   "que": d.get("decision", "") + (f" (nivel {d['nivel']})" if d.get("nivel") else ""), "quien": d.get("decidido_por", ""), "evidencia": d.get("artefactos_afectados", "")})
    for c in leer("cambios"):
        if c.get("decision") or c.get("fecha_decision"):
            ev.append({"fecha": c.get("fecha_decision") or c.get("fecha", ""), "tipo": "cambio", "id": c.get("id", ""),
                       "que": f"{c.get('titulo', '')}: {c.get('decision') or c.get('estado', '')}" + (f" · costo {c['costo']} ({c.get('cargo', '')})" if c.get("costo") else ""),
                       "quien": c.get("decidido_por", ""), "evidencia": c.get("notas", "")[:120]})
    for r in leer("riesgos"):
        if r.get("respuesta") == "aceptar":
            ev.append({"fecha": r.get("fecha_revision") or r.get("fecha_identificacion", ""), "tipo": "aceptacion-riesgo", "id": r.get("id", ""),
                       "que": r.get("evento", "")[:160], "quien": r.get("propietario", ""), "evidencia": r.get("notas", "")[:120]})
    for q in leer("calidad"):
        if q.get("resultado") in ("aprobado", "aprobado-con-observaciones"):
            ev.append({"fecha": q.get("fecha_real") or q.get("fecha_prevista", ""), "tipo": "aceptacion-producto", "id": q.get("id", ""),
                       "que": f"{q.get('producto', '')}: {q.get('resultado')}", "quien": q.get("aprobador", ""), "evidencia": q.get("metodo_verificacion", "")})
    for s in leer("envios"):
        if s.get("estado") in ("enviado", "simulado"):
            ev.append({"fecha": s.get("fecha", ""), "tipo": "comunicacion", "id": s.get("id", ""), "que": f"{s.get('proposito') or 'envío'}: {s.get('asunto', '')} ({s.get('canal', '')}, {s.get('estado')})",
                       "quien": s.get("stakeholder_id", ""), "evidencia": s.get("archivo", "")})
    ev = [x for x in ev if not (desde or hasta) or _en_rango(x["fecha"], desde, hasta)]
    return sorted(ev, key=lambda x: (x["fecha"] or "9999", x["id"], x["tipo"]))

def _secciones_a_texto(titulo, secciones):
    """Mismo contenido en Markdown y en HTML escapado. Bloques: ("p", texto) o ("tabla", cabecera, filas, columna_enlace)."""
    md = [f"# {titulo}", ""]
    h = ["<!doctype html>", '<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         f"<title>{html.escape(titulo)}</title>", "<style>body{font-family:system-ui,sans-serif;margin:24px;max-width:1100px;color:#1d1d1f;background:#fff}"
         "table{border-collapse:collapse;width:100%;margin:8px 0 20px}th,td{border:1px solid #ccc;padding:4px 6px;text-align:left;vertical-align:top;font-size:14px}"
         "th{background:#f2f2f2}nav a{margin-right:12px}code{font-size:13px}</style></head><body>", f"<h1>{html.escape(titulo)}</h1>", "<nav>"]
    h += [f'<a href="#s{i}">{html.escape(s)}</a>' for i, (s, _) in enumerate(secciones, 1)] + ["</nav>"]
    md += [f"{i}. [{s}](#{re.sub(r'[^a-z0-9áéíóúñü -]', '', s.lower()).replace(' ', '-')})" for i, (s, _) in enumerate(secciones, 1)] + [""]
    for i, (s, bloques) in enumerate(secciones, 1):
        md += [f"## {s}", ""]; h.append(f'<h2 id="s{i}">{html.escape(s)}</h2>')
        for b in bloques:
            if b[0] == "p":
                md += [b[1], ""]; h.append(f"<p>{html.escape(b[1])}</p>")
                continue
            _, cab, filas, enlace = b
            if not filas:
                md += ["—", ""]; h.append("<p>—</p>"); continue
            md += ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
            h.append("<table><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in cab) + "</tr>")
            for f in filas:
                md.append("| " + " | ".join((f"[{_md(v)}]({_md(v)})" if j == enlace and v else _md(v)) for j, v in enumerate(f)) + " |")
                h.append("<tr>" + "".join((f'<td><a href="{html.escape(str(v), quote=True)}">{html.escape(str(v))}</a></td>' if j == enlace and v else f"<td>{html.escape(str(v if v is not None else ''))}</td>")
                                          for j, v in enumerate(f)) + "</tr>")
            md.append(""); h.append("</table>")
    h.append("</body></html>")
    return "\n".join(md) + "\n", "\n".join(h) + "\n"

def expediente(a, estado):
    """Arma el expediente de auditoría (ZIP) con índice navegable (Markdown y HTML), cronología, líneas base, registros,
    comunicaciones, evidencia de puertas, hallazgos de sanidad al corte y manifiesto con sha256."""
    p = a.proyecto; hoy = datetime.date.today().isoformat(); corte = a.hasta or hoy
    T = lambda es, en: _t(estado, es, en)
    miembros = {}     # nombre en el ZIP → bytes
    origen = {}       # nombre en el ZIP → (sección, nota)
    externos = []
    def agregar(rel, datos, seccion, nota=""):
        miembros[rel] = datos; origen[rel] = (seccion, nota)
    def archivo(ruta_abs, seccion, nota="", filtrar=True):
        rel = os.path.relpath(ruta_abs, p).replace(os.sep, "/")
        if not getattr(a, "permitir_externos", False) and fuera_del_proyecto(p, ruta_abs):
            externos.append(rel); return
        f = _fecha_nombre(rel)
        if filtrar and (a.desde or a.hasta) and f and not _en_rango(f, a.desde, a.hasta): return
        agregar(rel, open(ruta_abs, "rb").read(), seccion, nota)
    # estado y registros
    agregar("estado.json", open(os.path.join(p, "estado.json"), "rb").read(), "estado", T("puertas, aprobaciones, tolerancias y presupuestos", "gates, approvals, tolerances, budgets"))
    regs = []; omitidos = []
    for ruta in sorted(glob.glob(os.path.join(p, "03-control", "registros", "*.csv"))):
        reg = os.path.splitext(os.path.basename(ruta))[0]; rel = os.path.relpath(ruta, p).replace(os.sep, "/")
        if fuera_del_proyecto(p, ruta) and not getattr(a, "permitir_externos", False): externos.append(rel); continue
        with open(ruta, newline="", encoding="utf-8") as fh: rd = csv.DictReader(fh); cols = list(rd.fieldnames or []); filas = list(rd)
        total = len(filas); sin_fecha = 0
        if (a.desde or a.hasta) and reg in FECHA_CSV:
            sel = []
            for f in filas:
                fechas = [f.get(c) for c in FECHA_CSV[reg] if f.get(c)]
                if not fechas: sin_fecha += 1; sel.append(f)
                elif any(_en_rango(x, a.desde, a.hasta) for x in fechas): sel.append(f)
            filas = sel
        if a.externo and reg in VALORACIONES: omitidos.append(rel); continue
        personales = a.externo and reg in PERSONALES
        if personales: filas = [{**f, **{c: "" for c in PERSONALES[reg] if c in f}} for f in filas]
        # sin período ni anonimización, la copia es byte a byte la del proyecto (misma huella sha256)
        agregar(rel, _csv_texto(cols, filas).encode("utf-8") if personales or len(filas) != total else open(ruta, "rb").read(), "registros")
        regs.append([rel, len(filas), total, sin_fecha])
    # líneas base congeladas, evidencia de puertas, comunicaciones, aceptaciones
    for ruta in sorted(glob.glob(os.path.join(p, "00-direccion", "historial", "**", "*"), recursive=True)):
        if os.path.isfile(ruta): archivo(ruta, "lineas-base", filtrar=False)
    for ruta in sorted(glob.glob(os.path.join(p, "00-direccion", "decisiones", "**", "*"), recursive=True)):
        if os.path.isfile(ruta): archivo(ruta, "puertas")
    for patron in ("03-control/reuniones/*acta*.md", "03-control/reportes/*.md", "03-control/reportes/*.html", "03-control/reportes/evm-*.json", "03-control/comunicaciones/**/*"):
        for ruta in sorted(glob.glob(os.path.join(p, patron), recursive=True)):
            if os.path.isfile(ruta): archivo(ruta, "comunicaciones")
    for ruta in sorted(glob.glob(os.path.join(p, "04-cierre", "*aceptacion*.md"))):
        archivo(ruta, "aceptaciones")
    for e_ in a.extra or []:
        if not os.path.exists(e_): print(f"Aviso: no existe {e_}"); continue
        if fuera_del_proyecto(p, e_) and not a.permitir_externos: externos.append(e_); continue
        rel = os.path.relpath(e_, p).replace(os.sep, "/") if not fuera_del_proyecto(p, e_) else "extra/" + os.path.basename(e_)
        agregar(rel, open(e_, "rb").read(), "extra")
    # bitácora de escrituras (2.6.0), solo con --con-bitacora: entera (es una cadena), aunque haya período
    bit = os.path.join(p, ".bitacora.jsonl"); n_bit = 0
    if getattr(a, "con_bitacora", False) and os.path.isfile(bit):
        datos_bit = open(bit, "rb").read(); n_bit = datos_bit.count(b"\n")
        agregar(ARCHIVO_BITACORA_ZIP, datos_bit, "bitacora", T("bitácora de escrituras completa (cadena de huellas)", "complete write log (hash chain)"))
    # hallazgos de sanidad al corte (solo lectura)
    san = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pm-estado-proyecto", "scripts", "sanidad.py")
    r = subprocess.run([sys.executable, os.path.normpath(san), "--proyecto", p, "--json", "--corte", corte], capture_output=True, text=True)
    try: sj = json.loads(r.stdout)
    except ValueError: sj = {"hallazgos": [], "cuenta": {}, "error": (r.stderr or r.stdout)[-300:]}
    agregar(f"sanidad-{corte}.json", json.dumps(sj, ensure_ascii=False, indent=2).encode("utf-8"), "sanidad")
    # cronología
    crono = cronologia(p, estado, a.desde, a.hasta)
    cab_c = ["fecha", "tipo", "id", "que", "quien", "evidencia"]
    agregar("cronologia.csv", _csv_texto(cab_c, crono).encode("utf-8"), "cronologia")
    # paquetes de puerta ya generados: se citan con su huella, no se reincluyen
    zips = [(os.path.relpath(z, p).replace(os.sep, "/"), _sha(open(z, "rb").read())) for z in sorted(glob.glob(os.path.join(p, "exportados", "*.zip")))
            if "expediente-auditoria" not in os.path.basename(z)]
    # índice
    rango = (a.desde or T("inicio", "start")) + " → " + (a.hasta or corte)
    cuenta = sj.get("cuenta") or {}
    por_sec = lambda s: [[k, len(v), _sha(v)[:16], origen[k][1]] for k, v in sorted(miembros.items()) if origen[k][0] == s]
    secciones = [
        (T("Alcance del expediente", "Scope"), [("p", T(f"Proyecto: {estado.get('proyecto', '')} · propósito: {a.proposito or '[por confirmar]'} · período: {rango} · corte: {corte} · generado: {hoy} con asistencia de IA (consolidación de archivos existentes).",
                                                     f"Project: {estado.get('proyecto', '')} · purpose: {a.proposito or 'TBC'} · period: {rango} · cut-off: {corte} · generated {hoy} with AI assistance.")),
                                                ("p", T(f"Fase {estado.get('fase', '')}, etapa {(estado.get('etapa_actual') or {}).get('numero', '')} ({(estado.get('etapa_actual') or {}).get('nombre', '')}); excepción abierta: {estado.get('excepcion_abierta') or 'ninguna'}.",
                                                        f"Phase {estado.get('fase', '')}, stage {(estado.get('etapa_actual') or {}).get('numero', '')}; open exception: {estado.get('excepcion_abierta') or 'none'}.")),
                                                ("p", T("Este expediente no constituye aprobación ni dictamen: consolida la evidencia registrada. La integridad se comprueba con `paquete.py verificar <zip>` (sha256 de cada archivo contra SHA256SUMS).",
                                                        "This file is not an approval or an opinion. Integrity: `paquete.py verificar <zip>`."))]),
        (T("Cronología de decisiones y puertas", "Decisions and gates timeline"), [("p", T(f"{len(crono)} eventos (también en cronologia.csv).", f"{len(crono)} events (also in cronologia.csv).")),
                                                                                   ("tabla", [T("Fecha", "Date"), T("Tipo", "Type"), "Id", T("Qué", "What"), T("Quién", "Who"), T("Evidencia", "Evidence")],
                                                                                    [[x[k] for k in cab_c] for x in crono], None)]),
        (T("Líneas base congeladas", "Frozen baselines"), [("tabla", [T("Archivo", "File"), "Bytes", "sha256", T("Nota", "Note")], por_sec("lineas-base"), 0)]),
        (T("Registros", "Registers"), [("p", T("Copia de los registros al corte; con período, las filas cuya fecha cae en él y las que no tienen fecha.", "Registers at the cut-off; with a period, rows dated within it and undated rows.")
                                        + (T(f" Destinatario externo: sin {', '.join(omitidos) or 'registros de interesados'} (valoraciones de interesados) y sin el destino de los envíos.",
                                             f" External recipient: without {', '.join(omitidos) or 'stakeholder registers'} and without message recipients.") if a.externo else "")),
                                       ("tabla", [T("Archivo", "File"), T("Filas incluidas", "Rows included"), T("Filas totales", "Total rows"), T("Sin fecha", "Undated")], regs, 0)]),
        (T("Evidencia de puertas", "Gate evidence"), [("tabla", [T("Archivo", "File"), "Bytes", "sha256", T("Nota", "Note")], por_sec("puertas"), 0),
                                                      ("p", T("Paquetes de puerta generados (se citan con su huella; no se reincluyen):", "Gate packages generated (cited by hash, not re-included):")),
                                                      ("tabla", [T("Archivo", "File"), "sha256"], [[z, h] for z, h in zips], None)]),
        (T("Comunicaciones, informes y aceptaciones", "Communications, reports and acceptances"), [("tabla", [T("Archivo", "File"), "Bytes", "sha256", T("Nota", "Note")],
                                                                                                  por_sec("comunicaciones") + por_sec("aceptaciones") + por_sec("extra"), 0)]),
        *([(T("Bitácora de escrituras", "Write log"), [("p", T(f"{ARCHIVO_BITACORA_ZIP}: {n_bit} escrituras de estado.json, registros y propuestas anotadas por los scripts, completa aunque el expediente tenga período (es una cadena: cada línea lleva la huella de la anterior). Cada línea: fecha real, script, operación, ids y campos cambiados (sin valores de interesados ni confidenciales), --por y huellas sha256 antes y después. Su verificación son los hallazgos BIT de la sanidad; `paquete.py verificar` la usa para explicar un archivo alterado.",
                                                                                f"{ARCHIVO_BITACORA_ZIP}: {n_bit} logged writes; complete even with a period (hash chain). Checked by the BIT health findings; `paquete.py verificar` uses it to explain an altered file."))])] if n_bit else []),
        (T("Hallazgos de sanidad al corte", "Health findings at the cut-off"), [("p", f"ERROR {cuenta.get('ERROR', 0)} · AVISO {cuenta.get('AVISO', 0)} · INFO {cuenta.get('INFO', 0)} · sanidad-{corte}.json"),
                                                                                ("tabla", [T("Severidad", "Severity"), T("Código", "Code"), T("Mensaje", "Message")],
                                                                                 [[h.get("severidad"), h.get("codigo"), h.get("mensaje", "")[:200]] for h in sj.get("hallazgos", []) if h.get("severidad") in ("ERROR", "AVISO")], None)]),
        (T("Manifiesto e integridad", "Manifest and integrity"), [("p", T(f"MANIFIESTO.md y {ARCHIVO_SUMAS} listan cada archivo con su sha256.", f"MANIFIESTO.md and {ARCHIVO_SUMAS} list every file with its sha256."))]
                                                                 + ([("p", T("Excluidos por estar fuera de la carpeta del proyecto: ", "Excluded (outside the project folder): ") + "; ".join(externos))] if externos else []))]
    titulo = T(f"Expediente de auditoría · {estado.get('proyecto', '')}", f"Audit file · {estado.get('proyecto', '')}")
    imd, ihtml = _secciones_a_texto(titulo, secciones)
    agregar("INDICE.md", imd.encode("utf-8"), "indice"); agregar("INDICE.html", ihtml.encode("utf-8"), "indice")
    man = [f"# {T('Manifiesto del expediente', 'Audit file manifest')}", "", f"**{T('Proyecto', 'Project')}:** {estado.get('proyecto', '')} · **{T('Período', 'Period')}:** {rango} · **{T('Generado', 'Generated')}:** {hoy}", "",
           "| " + T("Archivo | Sección | Bytes | sha256", "File | Section | Bytes | sha256") + " |", "|---|---|---|---|"]
    man += [f"| {_md(k)} | {origen[k][0]} | {len(v)} | {_sha(v)} |" for k, v in sorted(miembros.items())]
    agregar("MANIFIESTO.md", ("\n".join(man) + "\n").encode("utf-8"), "manifiesto")
    sumas = "".join(f"{_sha(v)}  {k}\n" for k, v in sorted(miembros.items()))
    sufijo = f"-{a.desde or 'inicio'}_{a.hasta or corte}" if (a.desde or a.hasta) else ""
    salida = a.salida or os.path.join(p, "exportados", f"{hoy}-expediente-auditoria{sufijo}.zip")
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in sorted(miembros.items()): z.writestr(k, v)
        z.writestr(ARCHIVO_SUMAS, sumas)
    secs = {}
    for k in miembros: secs[origen[k][0]] = secs.get(origen[k][0], 0) + 1
    print(T(f"Escrito {salida}: {len(miembros) + 1} archivos · {len(crono)} eventos en la cronología · registros {len(regs)} · sanidad ERROR {cuenta.get('ERROR', 0)} AVISO {cuenta.get('AVISO', 0)}",
            f"Written {salida}: {len(miembros) + 1} files · {len(crono)} timeline events · {len(regs)} registers · health ERROR {cuenta.get('ERROR', 0)} AVISO {cuenta.get('AVISO', 0)}"))
    print("  " + " · ".join(f"{s} {n}" for s, n in sorted(secs.items())))
    if externos: print(T("Excluidos por estar fuera del proyecto: ", "Excluded (outside the project): ") + "; ".join(externos[:TOPE_PANTALLA]) + (f" … y {len(externos) - TOPE_PANTALLA} más" if len(externos) > TOPE_PANTALLA else ""))
    print(T(f"Integridad: paquete.py --proyecto {p} verificar {salida}", f"Integrity: paquete.py --proyecto {p} verificar {salida}"))

def _explicar_con_bitacora(z, esperado, alterados, T):
    """Con bitacora.jsonl en el expediente: para cada estado.json o registro alterado, la última escritura que anotaron
    los scripts y si la huella del expediente era la que dejó esa escritura."""
    if ARCHIVO_BITACORA_ZIP not in z.namelist(): return []
    ultima = {}
    for raw in z.read(ARCHIVO_BITACORA_ZIP).splitlines():
        try: d = json.loads(raw.decode("utf-8"))
        except ValueError: continue
        if isinstance(d, dict) and d.get("archivo"): ultima[d["archivo"]] = d
    out = []
    for n in alterados:
        d = ultima.get(n)
        if not d: continue
        cuando = f"#{d.get('n')} {(d.get('fecha') or '')[:16].replace('T', ' ')} · {d.get('script', '')} {d.get('operacion', '')}" + (f" · --por {d['por']}" if d.get("por") else "") + (f" · {' '.join(d.get('ids') or [])}" if d.get("ids") else "")
        if d.get("despues") == esperado.get(n):
            out.append(T(f"{n}: la última escritura anotada en la bitácora ({cuando}) dejó exactamente la versión del expediente; la copia recibida es otra: el cambio no salió de los scripts.",
                         f"{n}: the last logged write ({cuando}) left exactly the packaged version; the received copy differs: the change did not come from the scripts."))
        else:
            out.append(T(f"{n}: la versión del expediente ya no era la de la última escritura anotada ({cuando}): hubo un cambio fuera de los scripts antes de armarlo (sanidad BIT-02).",
                         f"{n}: the packaged version was not the one the last logged write left ({cuando}): changed outside the scripts before packaging (health BIT-02)."))
    return out

def verificar(ruta_zip, estado):
    """Rehash de cada archivo del ZIP contra SHA256SUMS: alterados, faltantes y agregados. Código 1 si algo no coincide."""
    T = lambda es, en: _t(estado, es, en)
    if not os.path.isfile(ruta_zip): sys.exit(T(f"No existe el archivo: {ruta_zip}", f"File not found: {ruta_zip}"))
    try: z = zipfile.ZipFile(ruta_zip)
    except zipfile.BadZipFile: sys.exit(T(f"{ruta_zip} no es un ZIP válido", f"{ruta_zip} is not a valid ZIP"))
    if ARCHIVO_SUMAS not in z.namelist(): sys.exit(T(f"{ruta_zip} no tiene {ARCHIVO_SUMAS}: solo los expedientes de auditoría se verifican.", f"{ruta_zip} has no {ARCHIVO_SUMAS}."))
    esperado = {}
    for l in z.read(ARCHIVO_SUMAS).decode("utf-8").splitlines():
        m = re.match(r"^([0-9a-f]{64})  (.+)$", l)
        if m: esperado[m.group(2)] = m.group(1)
    presentes = [n for n in z.namelist() if n != ARCHIVO_SUMAS and not n.endswith("/")]
    alterados = [n for n in presentes if n in esperado and _sha(z.read(n)) != esperado[n]]
    faltan = [n for n in esperado if n not in presentes]
    agregados = [n for n in presentes if n not in esperado]
    problemas = [T("alterado", "altered") + f": {n}" for n in alterados] + [T("falta", "missing") + f": {n}" for n in faltan] + [T("agregado", "added") + f": {n}" for n in agregados]
    if problemas:
        print(T(f"INTEGRIDAD: FALLA · {len(problemas)} problema(s) en {ruta_zip}", f"INTEGRITY: FAILED · {len(problemas)} problem(s) in {ruta_zip}"))
        for x in problemas[:TOPE_PANTALLA]: print("  " + x)
        for x in _explicar_con_bitacora(z, esperado, alterados, T): print("  " + x)
        if len(problemas) > TOPE_PANTALLA: print(T(f"  … y {len(problemas) - TOPE_PANTALLA} más", f"  … and {len(problemas) - TOPE_PANTALLA} more"))
        sys.exit(1)
    print(T(f"INTEGRIDAD: OK · {len(esperado)} archivos coinciden con {ARCHIVO_SUMAS}", f"INTEGRITY: OK · {len(esperado)} files match {ARCHIVO_SUMAS}"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("puerta"); p.add_argument("tipo", choices=[k for k in PAQUETES if k != "cierre"]); p.add_argument("--salida"); p.add_argument("--extra", nargs="*", default=[])
    c = sub.add_parser("cierre"); c.add_argument("--salida"); c.add_argument("--extra", nargs="*", default=[])
    au = sub.add_parser("auditoria", help="expediente de auditoría: índice MD/HTML, cronología, líneas base, registros, comunicaciones, sanidad y sha256")
    au.add_argument("--desde"); au.add_argument("--hasta"); au.add_argument("--proposito", help="PMO, auditoría interna, due diligence, entrega al cliente…")
    au.add_argument("--externo", action="store_true", help="para un destinatario externo (cliente, proveedor, due diligence): sin stakeholders, estereotipos ni preferencias y sin el destino de los envíos")
    au.add_argument("--salida"); au.add_argument("--extra", nargs="*", default=[])
    au.add_argument("--con-bitacora", action="store_true", help="incluir la bitácora de escrituras (.bitacora.jsonl) completa como bitacora.jsonl")
    for x in (p, c, au): x.add_argument("--permitir-externos", action="store_true", help="incluir también archivos fuera de la carpeta del proyecto")
    v = sub.add_parser("verificar", help="rehash de un expediente contra su SHA256SUMS"); v.add_argument("zip")
    l = sub.add_parser("listar"); l.add_argument("clase", choices=["puerta", "cierre"]); l.add_argument("tipo", nargs="?")
    a = ap.parse_args()

    f_estado = os.path.join(a.proyecto, "estado.json")
    if not os.path.exists(f_estado): sys.exit("No existe estado.json; ejecutar nuevo_proyecto.py")
    estado = json.load(open(f_estado, encoding="utf-8"))
    if a.cmd == "verificar": verificar(a.zip, estado); return
    if a.cmd == "auditoria":
        for f in (a.desde, a.hasta):
            if f and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f): sys.exit(_t(estado, f"Fecha inválida: {f} (AAAA-MM-DD)", f"Invalid date: {f}"))
        if a.desde and a.hasta and a.desde > a.hasta: sys.exit(_t(estado, "--desde es posterior a --hasta", "--desde is after --hasta"))
        expediente(a, estado); return

    if a.cmd == "listar":
        tipo = "cierre" if a.clase == "cierre" else (a.tipo or sys.exit("Indicar tipo de puerta"))
    else:
        tipo = "cierre" if a.cmd == "cierre" else a.tipo
    if tipo not in PAQUETES: sys.exit(f"Tipo desconocido: {tipo}")

    filas, faltan, no_aprobados, externos = [], [], [], []
    permitir = getattr(a, "permitir_externos", False)
    n = int((estado.get("etapa_actual") or {}).get("numero") or 0)
    defs = [(c.format(n=n, n1=n + 1), [x.format(n=n, n1=n + 1) for x in pats], o) for c, pats, o in PAQUETES[tipo]]
    if estado.get("enfoque_entrega") == "agil":   # perfil ágil mínimo: la visión con el MVP sustituye a la descripción del producto del proyecto
        defs = [(c, pats + ["01-inicio/declaracion-vision.md", "01-inicio/*vision*.md"], o) if c == "descripcion-producto-proyecto" else (c, pats, o) for c, pats, o in defs]
    for clave, patrones, oblig in defs:
        rutas, art = resolver(a.proyecto, estado, clave, patrones)
        if not permitir:
            fuera = [r for r in rutas if fuera_del_proyecto(a.proyecto, r)]
            for r in fuera:
                externos.append(f"{clave}: {r}")
                filas.append((clave, "", clave, "", "EXCLUIDO: fuera del proyecto / outside the project (" + r.replace("|", "/") + ")", "obligatorio" if oblig else "opcional", ""))
            rutas = [r for r in rutas if r not in fuera]
            if fuera and not rutas:
                if oblig: faltan.append(clave)
                continue
        if not rutas:
            filas.append((clave, "", clave, "", "FALTA" if oblig else "no incluido", "obligatorio" if oblig else "opcional", ""))
            if oblig: faltan.append(clave)
            continue
        for r in rutas:
            es_doc = r.endswith((".md", ".html"))
            meta = frontmatter(r) if es_doc else {"version": "", "estado": "", "aprobado_por": "", "tipo": ""}
            cong = None if (art or {}).get("estado") or meta["estado"] else estado_congelada(a.proyecto, estado, r)
            if cong: meta = {**meta, "version": meta["version"] or cong[1], "aprobado_por": meta["aprobado_por"] or cong[2]}
            est = (art or {}).get("estado") or meta["estado"] or (cong and cong[0]) or ("registro" if r.endswith((".csv", ".xlsx")) else "sin-estado")
            ver = (art or {}).get("version") or meta["version"] or ""
            if est not in ESTADOS_OK and oblig: no_aprobados.append(f"{clave} ({est})")
            filas.append((clave, os.path.relpath(r, a.proyecto), meta["tipo"] or clave, ver, est, "obligatorio" if oblig else "opcional", meta["aprobado_por"] or ""))
    for e in getattr(a, "extra", []) or []:
        if os.path.exists(e) and not permitir and fuera_del_proyecto(a.proyecto, e):
            externos.append(f"extra: {e}")
            filas.append(("extra", "", "extra", "", "EXCLUIDO: fuera del proyecto / outside the project (" + e.replace("|", "/") + ")", "opcional", ""))
        elif os.path.exists(e):
            meta = frontmatter(e) if e.endswith((".md", ".html")) else {"version": "", "estado": "", "aprobado_por": "", "tipo": ""}
            filas.append(("extra", os.path.relpath(e, a.proyecto) if e.startswith(a.proyecto) else e, meta["tipo"] or "extra", meta["version"], meta["estado"] or "sin-estado", "opcional", meta["aprobado_por"]))
        else:
            print(f"Aviso: no existe {e}")

    borrador = bool(faltan or no_aprobados)
    hoy = datetime.date.today().isoformat()
    cabecera = [f"# Manifiesto del paquete · Package manifest", "",
                f"**Proyecto / Project:** {estado.get('proyecto','')}  ", f"**Paquete / Package:** {tipo}  ",
                f"**Generado / Generated:** {hoy} con asistencia de IA (automatización: consolidación de archivos existentes)  ",
                f"**ESTADO DEL PAQUETE / PACKAGE STATUS:** {'BORRADOR / DRAFT — ' + '; '.join(['faltan: ' + ', '.join(faltan)] if faltan else []) + ('; ' if faltan and no_aprobados else '') + ('en borrador: ' + ', '.join(no_aprobados) if no_aprobados else '') if borrador else 'COMPLETO PARA LA PUERTA / READY FOR THE GATE (fuentes aprobadas o en revisión)'}", "",
                "| Archivo en el ZIP / File | Origen / Source | Tipo / Type | Versión / Version | Estado / Status | Oblig. | Aprobado por / Approved by |", "|---|---|---|---|---|---|---|"]
    for clave, ruta, t, ver, est, oblig, apr in filas:
        nombre = os.path.basename(ruta) if ruta else f"({clave})"
        cabecera.append(f"| {nombre} | {ruta or '—'} | {t} | {ver} | {est} | {oblig} | {apr} |")
    if externos:
        cabecera += ["", "> **Excluidos por estar fuera de la carpeta del proyecto / excluded (outside the project folder):** " + "; ".join(x.replace("|", "/") for x in externos)
                     + ". Para incluirlos, revisar las rutas y volver a generar con `--permitir-externos`."]
    cabecera += ["", "> Este paquete no constituye aprobación. La decisión de la puerta la toma una persona con rol en la junta y se registra con `estado.py puerta` y en `decisiones.csv`."]
    manifiesto = "\n".join(cabecera) + "\n"

    if a.cmd == "listar":
        print(manifiesto); return

    salida = a.salida or os.path.join(a.proyecto, "exportados", f"{hoy}-paquete-{tipo}-v1{'-BORRADOR' if borrador else ''}.zip")
    if borrador and "BORRADOR" not in os.path.basename(salida):
        base, ext = os.path.splitext(salida); salida = f"{base}-BORRADOR{ext}"
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("MANIFIESTO.md", manifiesto)
        for clave, ruta, *_ in filas:
            if not ruta: continue
            src = ruta if os.path.isabs(ruta) else os.path.join(a.proyecto, ruta)
            z.write(src, arcname=os.path.join(clave, os.path.basename(ruta)))
    print(f"Escrito {salida}")
    if faltan: print("Faltan obligatorios:", ", ".join(faltan))
    if no_aprobados: print("En borrador:", ", ".join(no_aprobados))
    if externos: print("Excluidos por estar fuera del proyecto (usar --permitir-externos para incluirlos) / outside the project, excluded:", "; ".join(externos))

if __name__ == "__main__":
    main()
