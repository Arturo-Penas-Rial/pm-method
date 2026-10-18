#!/usr/bin/env python3
"""Descubrimiento de riesgos candidatos · Risk discovery.

Destila **candidatos** (no riesgos registrados) desde cuatro fuentes, cada uno con su cita y su origen trazable:
  bmad            artefactos de BMAD vía pm-bmad-puente (solo lectura): fase de descubrimiento (brainstorming, PRFAQ,
                  investigación), brief, PRD (supuestos, preguntas abiertas, NFR con [SUPUESTO]), arquitectura (decisiones
                  diferidas, preguntas abiertas), UX.
  transcripciones entrevistas y reuniones (VTT, SRT, TXT o la salida normalizada de pm-reuniones): frases de
                  preocupación, dependencia, incertidumbre u oportunidad, con hablante y marca de tiempo.
  tracker         instantánea de Jira u otro tracker (03-control/fuentes/<sistema>-AAAA-MM-DD.csv, vía pm-integraciones):
                  bugs, incidentes, bloqueos, prioridad alta o etiqueta de riesgo → issue (ya ocurrió) y riesgo derivado.
  artefactos      artefactos del proyecto (sin BMAD o además de él): mandato, brief, canvas, business case, requisitos,
                  plan del proyecto, enfoques, supuestos sin validar (supuestos.csv) y lecciones (lecciones.csv).
Nada se registra solo: pm-riesgos redacta causa → evento → efecto, evalúa P×I con el propietario y registra con
registro.py (--campo notas="origen: CR-nn · <fuente>"); lo ocurrido va a pm-issues-cambios como issue.

Uso / Usage:
  riesgos.py --proyecto G candidatos [--fuentes bmad,transcripciones,tracker,artefactos] [--transcripcion F …]
             [--instantanea F] [--desde AAAA-MM-DD] [--salida F.md] [--json]
Por defecto las cuatro fuentes: bmad solo aplica si integraciones.especificacion = bmad (si no, lo informa y los riesgos salen
de los artefactos); transcripciones = 03-control/reuniones/*transcripcion*.md
(o --transcripcion); tracker = la instantánea más reciente de 03-control/fuentes/ (o --instantanea); artefactos siempre.
"""
import argparse, csv, datetime, glob, json, os, re, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.normpath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SK, "pm-estado-proyecto", "scripts"))
import esquema as E

IDIOMA = "es"
def t(es, en): return en if IDIOMA == "en" else es

ENCABEZADO_RIESGO = re.compile(r"riesgo|risk|restricci|constraint|pregunta|open question|dependenc|pendiente|amenaza|threat|"
                               r"preocupaci|concern|incertidumbre|uncertaint|supuesto|assumption|decisiones diferidas|deferred|lecci|lesson", re.I)
MARCA = re.compile(r"\[(SUPUESTO|ASSUMPTION|POR CONFIRMAR|TBD|VERIFICAR)\]|\bTBD\b|\[por confirmar\]|\bpor confirmar\b", re.I)
EXPLICITO = re.compile(r"\b(riesgo|risk)\s*:", re.I)
IDS = re.compile(r"\b(FR|NFR|AD|SM|UJ|REQ|E)-\d+\b|\b\d{1,2}-\d{1,2}-[a-záéíóúñ][\w-]*", re.I)
VOC_RIESGO = re.compile(r"\b(riesgo|nos preocupa|me preocupa|preocupaci[oó]n|preocupa|tememos|temen|teme|temor|miedo|puede que no|podr[ií]a(mos)? no|"
                        r"si no (llega|llegan|est[aá]|tenemos|conseguimos|se aprueba)|no llegamos|no vamos a (poder|llegar)|dependemos de|"
                        r"depende(mos)? de|atras(o|ar|arnos)|demora|bloque(o|ado|ada)|no est[aá] claro|incertidumbre|quiz[aá]s no|"
                        r"risk|worried|concern|might not|may not|depends on|blocked|delay|not sure)\b", re.I)
VOC_OPORTUNIDAD = re.compile(r"\b(oportunidad|podr[ií]amos aprovechar|aprovechar|reutilizar|reusar|ahorrar|opportunity|could reuse|leverage)\b", re.I)
CATEGORIAS = [
    ("externo", r"\bley\b|norma|regulac|\bbcu\b|cumplimiento|compliance|mercado|residencia de datos"),
    ("organizacional", r"sindicato|resistencia|adopci|rotaci|capacitaci|personal|cultura|operadores|usuarios no|equipo disponible"),
    ("comercial", r"contrato|licenci|proveedor externo|costo del proveedor|precio|factura"),
    ("gestion", r"presupuesto|plazo|alcance|l[ií]nea base|cronograma|equipo|recursos|budget|schedule|scope"),
    ("tecnico", r"integraci|\bapi\b|rendimiento|disponibilidad|seguridad|n[uú]cleo|sistema|sms|identidad|datos|hosting|t[eé]cnic|performance|security"),
]
TIPOS_ISSUE = {"bug", "error", "defecto", "incidente", "incident", "impedimento", "impediment", "blocker", "bloqueo", "problema", "problem"}
PRIORIDAD_ALTA = {"highest", "high", "alta", "muy alta", "critica", "crítica", "critical", "blocker", "urgente"}
ESTADO_BLOQUEO = {"bloqueado", "blocked", "impedido", "on hold", "en espera"}
STOP = set("para como este esta pero porque cuando donde desde hasta sobre entre todos todas puede pueden tiene tienen hacer estar "
           "with that this from have will would there their they which about could should portal socios proyecto project".split())

def norm_txt(s): return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
def palabras(s): return {w for w in re.findall(r"[a-z0-9]{4,}", norm_txt(s)) if w not in STOP}

def categoria(txt):
    for c, rx in CATEGORIAS:
        if re.search(rx, txt, re.I): return c
    return "otro"

def rel(proyecto, p):
    base = os.path.dirname(os.path.abspath(proyecto))            # rutas relativas a la carpeta del repositorio
    return os.path.relpath(os.path.abspath(p), base)

# ------------------------------------------------------------------ extracción de documentos Markdown
def items_documento(ruta):
    """(línea, texto, motivo): ítems bajo encabezados de riesgo, líneas con marcas de supuesto/pendiente o 'riesgo:'."""
    out = []; en_seccion = None; nivel_sec = 9
    lineas = open(ruta, encoding="utf-8", errors="replace").read().splitlines()
    for n, l in enumerate(lineas, 1):
        h = re.match(r"^(#{1,6})\s+(.*)$", l)
        if h:
            nivel = len(h.group(1))
            if en_seccion and nivel <= nivel_sec: en_seccion = None
            if ENCABEZADO_RIESGO.search(h.group(2)): en_seccion, nivel_sec = h.group(2).strip(), nivel
            continue
        texto = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", l).strip()
        if not texto or texto.startswith(("|---", "```", ">")) or l.lstrip().startswith(">"): continue      # citas en bloque: notas del autor
        if en_seccion and (re.match(r"^\s*([-*+]|\d+[.)])\s+", l) or (len(texto) > 40 and not texto.startswith("|"))):
            out.append((n, texto, t(f"sección «{en_seccion}»", f"section «{en_seccion}»")))
        elif MARCA.search(texto):
            out.append((n, texto, t("marcado como supuesto o pendiente", "marked as assumption or pending")))
        elif EXPLICITO.search(texto):
            out.append((n, texto, t("mención explícita de riesgo", "explicit risk mention")))
    return out

def de_documentos(proyecto, rutas, fuente):
    cands = []
    for r in rutas:
        for n, texto, motivo in items_documento(r):
            if "?" in texto: clase = "pregunta"
            elif re.search(r"riesgo|risk|amenaza|threat|dependenc|restricci|constraint|preocupaci|incertidumbre|lecci|lesson", motivo, re.I): clase = "riesgo"
            elif MARCA.search(texto) or re.search(r"supuesto|assumption", motivo, re.I): clase = "supuesto"
            elif re.search(r"pregunta|question", motivo, re.I): clase = "pregunta"
            else: clase = "riesgo"
            tipo = "oportunidad" if VOC_OPORTUNIDAD.search(texto) else "amenaza"
            cands.append({"fuente": fuente, "origen": f"{rel(proyecto, r)}:{n}", "cita": texto[:300], "motivo": motivo, "clase": clase, "tipo": tipo,
                          "refs": sorted(set(m.group(0) for m in IDS.finditer(texto))), "interesado": ""})
    return cands

# ------------------------------------------------------------------ fuentes
def fuente_bmad(proyecto, e):
    sys.path.insert(0, os.path.join(SK, "pm-bmad-puente", "scripts"))
    import bmad as B
    b = B.detectar_bmad(proyecto, None, e); arts = B.inventario(b)
    rutas = []
    for clave in ("descubrimiento", "brief", "prd", "arquitectura", "ux"):
        rutas += arts.get(clave, {}).get("rutas", [])
    leidos = [rel(proyecto, r) for r in rutas]
    return de_documentos(proyecto, rutas, "bmad"), leidos

def turnos(ruta):
    txt = open(ruta, encoding="utf-8-sig", errors="replace").read()
    md = re.findall(r"(?m)^\*\*(?:\[(\d\d:\d\d:\d\d)\]\s*)?([^:*\n]{1,60}):\*\*\s*(.+)$", txt)
    if md: return [{"ini": a, "hablante": h.strip(), "texto": x.strip()} for a, h, x in md]
    sys.path.insert(0, os.path.join(SK, "pm-reuniones", "scripts"))
    import transcripcion as T
    crudos = T.parse_vtt_srt(txt) if "-->" in txt else T.parse_txt(txt)
    return [{"ini": T.fmt(x["ini"]) if x.get("ini") is not None else "", "hablante": x["hablante"], "texto": x["texto"]} for x in crudos]

def fuente_transcripciones(proyecto, archivos, desde):
    if not archivos:
        archivos = sorted(glob.glob(os.path.join(proyecto, "03-control", "reuniones", "*transcripcion*.md")))
        if desde: archivos = [a for a in archivos if (re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(a)) or [None, "9999"])[1] >= desde]
    sts = []
    p = E.ruta_registro(proyecto, "stakeholders")
    if os.path.exists(p): sts = E.leer_csv(p)[1]
    por_nombre = {norm_txt(s.get("nombre")): s["id"] for s in sts}
    cands = []
    for a in archivos:
        for x in turnos(a):
            for oracion in re.split(r"(?<=[.!?])\s+", x["texto"]):
                riesgo, oport = VOC_RIESGO.search(oracion), VOC_OPORTUNIDAD.search(oracion)
                if not (riesgo or oport): continue
                cands.append({"fuente": "transcripcion", "origen": f"{rel(proyecto, a)}" + (f" [{x['ini']}]" if x.get("ini") else ""),
                              "cita": f"{x['hablante']}: «{oracion.strip()[:260]}»", "motivo": t("frase de preocupación, dependencia o incertidumbre", "concern, dependency or uncertainty")
                              if riesgo else t("frase de oportunidad", "opportunity"), "clase": "riesgo", "tipo": "oportunidad" if oport and not riesgo else "amenaza",
                              "refs": sorted(set(m.group(0) for m in IDS.finditer(oracion))), "interesado": por_nombre.get(norm_txt(x["hablante"]), "")})
    return cands, [rel(proyecto, a) for a in archivos]

def fuente_tracker(proyecto, instantanea):
    if not instantanea:
        xs = sorted(glob.glob(os.path.join(proyecto, "03-control", "fuentes", "*-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].csv")),
                    key=lambda p: re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p)).group(1))
        xs = [x for x in xs if "clave" in (open(x, encoding="utf-8").readline())]
        instantanea = xs[-1] if xs else None
    if not instantanea: return [], []
    cands = []
    sistema = os.path.basename(instantanea).split("-")[0]
    for f in csv.DictReader(open(instantanea, encoding="utf-8")):
        tipo = norm_txt(f.get("tipo")); prio = norm_txt(f.get("prioridad")); est = norm_txt(f.get("estado")); etq = norm_txt(f.get("etiquetas"))
        es_issue = tipo in {norm_txt(x) for x in TIPOS_ISSUE} or est in {norm_txt(x) for x in ESTADO_BLOQUEO}
        es_riesgo = "riesgo" in etq or "risk" in etq
        alta = prio in {norm_txt(x) for x in PRIORIDAD_ALTA}
        if not (es_issue or es_riesgo or (alta and tipo not in ("historia", "story", "tarea", "task", "epic", "epica"))): continue
        texto = f"{f.get('titulo', '')}" + (f" — {f.get('descripcion', '')}" if f.get("descripcion") else "")
        motivo = []
        if es_issue: motivo.append(t(f"{f.get('tipo')} {f.get('estado')}: ya ocurrió → issue; evaluar el riesgo derivado (efecto en plazo, costo o calidad)",
                                   f"{f.get('tipo')} {f.get('estado')}: already happened → issue; assess the derived risk"))
        if es_riesgo: motivo.append(t("etiquetado como riesgo en el tracker", "labelled as risk in the tracker"))
        if alta and not motivo: motivo.append(t(f"prioridad {f.get('prioridad')}", f"priority {f.get('prioridad')}"))
        cands.append({"fuente": "tracker", "origen": f"{sistema}:{f.get('clave', '')} ({rel(proyecto, instantanea)})", "cita": texto[:300], "motivo": "; ".join(motivo),
                      "clase": "issue" if es_issue and not es_riesgo else "riesgo", "tipo": "amenaza",
                      "refs": sorted(set(m.group(0) for m in IDS.finditer(texto + " " + (f.get("vinculo") or "")))), "interesado": ""})
    return cands, [rel(proyecto, instantanea)]

ARTEFACTOS = ["00-direccion/mandato.md", "01-inicio/project-brief.md", "01-inicio/canvas-arranque.md", "00-direccion/business-case-esquematico.md",
              "00-direccion/business-case.md", "02-planificacion/requisitos.md", "02-planificacion/plan-proyecto.md", "00-direccion/pid.md"]

def fuente_artefactos(proyecto):
    rutas = [os.path.join(proyecto, r) for r in ARTEFACTOS if os.path.exists(os.path.join(proyecto, r))]
    # el enfoque de riesgo y la escala P×I describen el método (no son fuentes de riesgos): se excluyen
    rutas += [r for r in sorted(glob.glob(os.path.join(proyecto, "02-planificacion", "enfoques", "*.md")))
              if not re.match(r"(enfoque-riesgo|evaluacion-probabilidad-impacto)", os.path.basename(r))]
    cands = de_documentos(proyecto, rutas, "artefacto")
    leidos = [rel(proyecto, r) for r in rutas]
    p = E.ruta_registro(proyecto, "supuestos")
    if os.path.exists(p):
        leidos.append(rel(proyecto, p))
        for s in E.leer_csv(p)[1]:
            if s.get("estado") == "abierto" and s.get("validado") != "si":
                cands.append({"fuente": "artefacto", "origen": f"supuestos.csv {s['id']}", "cita": s.get("supuesto_o_restriccion", "")[:300],
                              "motivo": t(f"{s.get('tipo') or 'supuesto'} sin validar: si resulta falso, ¿qué objetivo afecta?", "unvalidated assumption"),
                              "clase": "supuesto", "tipo": "amenaza", "refs": [s["id"]], "interesado": s.get("responsable", "")})
    p = E.ruta_registro(proyecto, "lecciones")
    if os.path.exists(p):
        leidos.append(rel(proyecto, p))
        for l in E.leer_csv(p)[1]:
            texto = f"{l.get('situacion', '')} → {l.get('efecto', '')}"
            if re.search(r"riesgo|risk|atras|sobrecost|problema|falla|demora", texto + l.get("categoria", ""), re.I):
                cands.append({"fuente": "artefacto", "origen": f"lecciones.csv {l['id']}", "cita": texto[:300], "motivo": t("lección previa: ¿puede repetirse?", "previous lesson: can it recur?"),
                              "clase": "riesgo", "tipo": "amenaza", "refs": [l["id"]], "interesado": ""})
    return cands, leidos

# ------------------------------------------------------------------ deduplicación y salida
def duplicados(proyecto, cands):
    p = E.ruta_registro(proyecto, "riesgos")
    riesgos = E.leer_csv(p)[1] if os.path.exists(p) else []
    vistos = {}
    out = []
    for c in cands:
        clave = norm_txt(c["cita"])[:160]
        if clave in vistos: continue
        vistos[clave] = True
        w = palabras(c["cita"]); c["posible_duplicado"] = ""; c["relacionado"] = ""
        for r in riesgos:
            if c["origen"].split(" (")[0] in (r.get("notas") or ""): c["posible_duplicado"] = r["id"]; break
            wr = palabras(" ".join(r.get(k, "") for k in ("causa", "evento", "efecto")))
            if w and wr and len(w & wr) / len(w | wr) >= 0.35: c["posible_duplicado"] = r["id"]; break
            if w and wr and len(w & wr) >= 3 and not c["relacionado"]: c["relacionado"] = r["id"]     # p. ej. un issue que materializa un riesgo
        c["categoria_sugerida"] = categoria(c["cita"])
        out.append(c)
    for i, c in enumerate(out, 1): c["id"] = f"CR-{i:02d}"
    return out

SIGUIENTE = {"riesgo": "redactar causa → evento → efecto, evaluar P×I con el propietario y registrar (registro.py agregar riesgos … --campo notas=\"origen: {id} · {origen}\")",
             "supuesto": "validar el supuesto (supuestos.csv); si no se puede, registrar el riesgo de que sea falso",
             "pregunta": "asignar dueño y fecha a la pregunta; registrar el riesgo si su respuesta puede afectar un objetivo",
             "issue": "registrar como issue (pm-issues-cambios) y evaluar el riesgo derivado sobre el plan"}

def markdown(cands, cobertura, fecha):
    L = ["---", "tipo: candidatos-riesgo", f"fecha: {fecha}", "estado: borrador", "---", "",
         f"# Riesgos candidatos · Risk candidates ({fecha})", "",
         t("> Candidatos para el taller o la revisión de riesgos: no son riesgos registrados. Cada uno cita su origen; pm-riesgos los formula como causa → evento → efecto y los registra solo tras la evaluación con el propietario. Lo ocurrido es un issue.",
           "> Candidates for the risk workshop or review, not registered risks."), "", "## Cobertura de fuentes", "",
         "| Fuente | Leído | Candidatos |", "|---|---|---|"]
    for f, (leidos, n) in cobertura.items():
        L.append(f"| {f} | {'; '.join(leidos) if leidos else t('— (no disponible o no solicitada)', '— (not available)')} | {n} |")
    L += ["", "## Candidatos", "", "| CR | Clase | Tipo | Fuente | Origen | Cita | Refs | Interesado | Categoría sugerida | Posible duplicado | Relacionado |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cands:
        L.append(f"| {c['id']} | {c['clase']} | {c['tipo']} | {c['fuente']} | {c['origen']} | {c['cita'].replace('|', '/')} | {', '.join(c['refs'])} | {c['interesado']} | {c['categoria_sugerida']} | {c['posible_duplicado']} | {c.get('relacionado', '')} |")
    L += ["", "## Siguiente paso por clase", ""] + [f"- **{k}**: {v}" for k, v in SIGUIENTE.items()]
    return "\n".join(L) + "\n"

def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidatos"); c.add_argument("--fuentes"); c.add_argument("--transcripcion", action="append"); c.add_argument("--instantanea")
    c.add_argument("--desde"); c.add_argument("--salida"); c.add_argument("--json", action="store_true"); c.add_argument("--fecha")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.proyecto, "estado.json")): sys.exit(f"{a.proyecto}: falta estado.json / not a project folder")
    e = E.cargar_estado(a.proyecto); IDIOMA = e.get("idioma", "es")
    fuentes = a.fuentes.split(",") if a.fuentes else ["bmad", "transcripciones", "tracker", "artefactos"]
    desconocidas = [f for f in fuentes if f not in ("bmad", "transcripciones", "tracker", "artefactos")]
    if desconocidas: sys.exit(t(f"Fuentes desconocidas: {desconocidas}", f"Unknown sources: {desconocidas}"))
    todos, cobertura = [], {}
    for f in fuentes:
        if f == "bmad":
            if e.get("integraciones", {}).get("especificacion") != "bmad": cobertura[f] = ([], 0); continue   # sin BMAD: no aplica
            cs, leidos = fuente_bmad(a.proyecto, e)
        elif f == "transcripciones": cs, leidos = fuente_transcripciones(a.proyecto, a.transcripcion, a.desde)
        elif f == "tracker": cs, leidos = fuente_tracker(a.proyecto, a.instantanea)
        else: cs, leidos = fuente_artefactos(a.proyecto)
        cobertura[f] = (leidos, len(cs)); todos += cs
    cands = duplicados(a.proyecto, todos)
    for f in cobertura:
        cobertura[f] = (cobertura[f][0], sum(1 for c in cands if c["fuente"] == {"transcripciones": "transcripcion", "artefactos": "artefacto"}.get(f, f)))
    fecha = a.fecha or datetime.date.today().isoformat()
    salida = a.salida or os.path.join(a.proyecto, "03-control", "reportes", f"{fecha}-candidatos-riesgo.md")
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True); open(salida, "w", encoding="utf-8").write(markdown(cands, cobertura, fecha))
    if a.json: print(json.dumps({"cobertura": {k: {"leido": v[0], "candidatos": v[1]} for k, v in cobertura.items()}, "candidatos": cands, "salida": salida}, ensure_ascii=False, indent=2)); return
    sin_bmad = e.get("integraciones", {}).get("especificacion") != "bmad"
    for f, (leidos, n) in cobertura.items():
        if f == "bmad" and sin_bmad: print(t("bmad: no aplica (el proyecto no usa BMAD: los riesgos salen de los artefactos del proyecto)", "bmad: not applicable (no BMAD)")); continue
        print(f"{f}: {n} " + t("candidatos", "candidates") + (f" · {len(leidos)} " + t("fuente(s) leída(s)", "source(s) read") if leidos else t(" · no disponible", " · not available")))
    for c in cands:
        print(f"{c['id']} [{c['clase']}/{c['tipo']}] {c['origen']} · {c['cita'][:140]}" + (f" · refs {', '.join(c['refs'])}" if c["refs"] else "")
              + (f" · {c['interesado']}" if c["interesado"] else "") + (f" · ¿duplica {c['posible_duplicado']}?" if c["posible_duplicado"] else "")
              + (f" · ¿relacionado con {c['relacionado']}?" if c.get("relacionado") and not c["posible_duplicado"] else ""))
    print(t(f"→ {salida} (borrador). Son candidatos: pm-riesgos los formula, evalúa con el propietario y registra; lo ocurrido va a issues.", f"→ {salida} (draft)."))

if __name__ == "__main__":
    main()
