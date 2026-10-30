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
  riesgos.py --proyecto G opciones [--riesgo R-###] [--umbral N] [--proponer] [--max N] [--json]
  riesgos.py --proyecto G opciones --riesgo R-### --elegir O# --por "<rol: nombre>" [--motivo T] [--nivel gestor]
             [--decision D-###] [--revision AAAA-MM-DD] [--fecha AAAA-MM-DD]
Por defecto las cuatro fuentes: bmad solo aplica si integraciones.especificacion = bmad (si no, lo informa y los riesgos salen
de los artefactos); transcripciones = 03-control/reuniones/*transcripcion*.md
(o --transcripcion); tracker = la instantánea más reciente de 03-control/fuentes/ (o --instantanea); artefactos siempre.

opciones: para los riesgos abiertos con P×I ≥ umbral (por defecto estado.json.umbrales_riesgo.alto, 15) lee las opciones
de respuesta de 03-control/registros/opciones-riesgo/R-###.csv (las redacta el modelo o la persona; --proponer crea la
plantilla sin pisar una existente), valida cifras y rangos de la escala, calcula EMV residual y valor neto
(EMV inherente − EMV residual − EMV del secundario − costo; en oportunidades, el aumento de EMV), ordena y marca la
recomendada sin decidir. --elegir registra la opción que decide la persona (PUERTA HUMANA: exige --por) en riesgos.csv
y su decisión en decisiones.csv, siempre con registro.py.
"""
import argparse, csv, datetime, glob, io, json, os, re, subprocess, sys, unicodedata

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
def corto(x, n=120):
    x = " ".join(str(x or "").split())
    return x if len(x) <= n else x[:n - 1] + "…"
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

def leer_instantanea(proyecto, p):
    """Texto de una instantánea del tracker (UTF-8, con o sin BOM). Ilegible → mensaje con el archivo y el motivo, sin
    traza (2.6.2: un dato ilegible no se toma como vacío)."""
    try:
        with open(p, encoding="utf-8-sig", newline="") as fh: return fh.read()
    except UnicodeDecodeError as x:
        sys.exit(t(f"{rel(proyecto, p)}: la instantánea del tracker no está en UTF-8 (byte {x.start}); exportarla de nuevo como CSV UTF-8. No se generaron candidatos.",
                   f"{rel(proyecto, p)}: the tracker snapshot is not UTF-8 (byte {x.start}); export it again as UTF-8 CSV. No candidates generated."))
    except OSError as x:
        sys.exit(t(f"{p}: no se pudo leer la instantánea del tracker ({x.strerror or type(x).__name__}).", f"{p}: cannot read the tracker snapshot ({x.strerror or type(x).__name__})."))

def fuente_tracker(proyecto, instantanea):
    if not instantanea:
        xs = sorted(glob.glob(os.path.join(proyecto, "03-control", "fuentes", "*-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].csv")),
                    key=lambda p: re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p)).group(1))
        xs = [x for x in xs if "clave" in leer_instantanea(proyecto, x).split("\n", 1)[0]]
        instantanea = xs[-1] if xs else None
    if not instantanea: return [], []
    cands = []
    sistema = os.path.basename(instantanea).split("-")[0]
    try: filas = list(csv.DictReader(io.StringIO(leer_instantanea(proyecto, instantanea))))
    except csv.Error as x:
        sys.exit(t(f"{rel(proyecto, instantanea)}: CSV mal formado ({x}). No se generaron candidatos.", f"{rel(proyecto, instantanea)}: malformed CSV ({x}). No candidates generated."))
    for f in filas:
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

# ------------------------------------------------------------------ opciones de respuesta y plan de contingencia
# Archivo de opciones por riesgo (SPEC §1.10.9): 03-control/registros/opciones-riesgo/R-###.csv, una fila por opción.
# No es un registro del paquete (no tiene id propio ni lo protege el guardián): es la hoja de trabajo de la que sale la
# respuesta elegida, que sí se registra en riesgos.csv con registro.py. PRINCE2 2.c.4 (catálogo), R-10 (costo frente a la
# reducción de EMV), R-12 (disparador y contingencia), R-14 (secundarios), R-15 (residual); PMBOK 8 §3.11 (estrategias).
COLS_OPC = ["opcion", "estrategia", "descripcion", "costo", "probabilidad_residual", "impacto_residual",
            "impacto_monetario_residual", "monto_contingencia", "disparador", "riesgo_secundario", "emv_secundario", "notas"]
ESTRATEGIAS = {"amenaza": ["evitar", "reducir", "transferir", "compartir", "aceptar", "contingencia", "escalar"],
               "oportunidad": ["explotar", "mejorar", "compartir", "aceptar", "contingencia", "escalar"]}
MINIMAS = {"amenaza": ["evitar", "reducir", "transferir", "contingencia"], "oportunidad": ["explotar", "mejorar", "aceptar"]}
PCT = {1: .1, 2: .3, 3: .5, 4: .7, 5: .9}          # conversión 1–5 → % del paquete (la misma de registro.py recalcular)
REGISTRO = os.path.join(SK, "pm-estado-proyecto", "scripts", "registro.py")
MAX_OPCIONES = 10                                   # opciones mostradas por riesgo (control del contexto)

def ruta_opciones(proyecto, rid): return os.path.join(proyecto, "03-control", "registros", "opciones-riesgo", f"{rid}.csv")
def ruta_plan(proyecto, rid): return os.path.join(proyecto, "03-control", "registros", f"{rid}-plan-contingencia.md")
def miles(x): return f"{x:,.0f}".replace(",", "." if IDIOMA != "en" else ",")
def flt(v):
    try: return float(str(v or "").replace(",", "."))
    except ValueError: return None

def emv_inherente(r):
    v = flt(r.get("valor_esperado"))
    if v is not None: return v
    m, p = flt(r.get("impacto_monetario")), (r.get("probabilidad") or "")
    return m * PCT[int(p)] if m is not None and p.isdigit() and int(p) in PCT else None

def _num(o, col, err, defecto=None):
    """Monto simple ≥ 0 (sin moneda ni separador de miles, como registro.py); vacío → defecto."""
    v = (o.get(col) or "").strip()
    if not v: return defecto
    if re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", v) or not re.fullmatch(r"\d+([.,]\d+)?", v):
        err.append(t(f"{col}='{v}' debe ser un número simple ≥ 0 como 2000 (sin moneda ni separador de miles)",
                     f"{col}='{v}' must be a plain number ≥ 0 such as 2000 (no currency or thousands separators)")); return None
    return float(v.replace(",", "."))

def _escala(o, col, err):
    v = (o.get(col) or "").strip()
    if not v: return None
    if not (v.isdigit() and 1 <= int(v) <= 5):
        err.append(t(f"{col}='{v}' debe ser entero 1–5 (escala P×I)", f"{col}='{v}' must be an integer 1–5")); return None
    return int(v)

def evaluar_opcion(o, r, umbral):
    """Valida y calcula una opción. estado: evaluada | sin-evaluar (faltan datos) | invalida (valores fuera de la escala)."""
    err, falta, avisos = [], [], []
    tipo = r.get("tipo") or "amenaza"; est = (o.get("estrategia") or "").strip().lower()
    if est not in ESTRATEGIAS.get(tipo, ESTRATEGIAS["amenaza"]):
        err.append(t(f"estrategia='{est}' no aplica a una {tipo}; usar: {', '.join(ESTRATEGIAS.get(tipo, []))}",
                     f"strategy='{est}' does not apply to a {tipo}; use: {', '.join(ESTRATEGIAS.get(tipo, []))}"))
    costo = _num(o, "costo", err); pr, ir = _escala(o, "probabilidad_residual", err), _escala(o, "impacto_residual", err)
    imr = _num(o, "impacto_monetario_residual", err, flt(r.get("impacto_monetario")))
    mc = _num(o, "monto_contingencia", err, 0.0); es = _num(o, "emv_secundario", err, 0.0)
    desc = (o.get("descripcion") or "").strip()
    if not desc or "[por confirmar]" in desc.lower() or "[to be confirmed]" in desc.lower(): falta.append(t("descripción", "description"))
    for nombre, v in ((t("costo", "cost"), (o.get("costo") or "").strip()), ("probabilidad_residual", (o.get("probabilidad_residual") or "").strip()),
                      ("impacto_residual", (o.get("impacto_residual") or "").strip())):
        if not v: falta.append(nombre)
    if est == "contingencia" and not (o.get("disparador") or "").strip(): falta.append(t("disparador (sin disparador no hay contingencia)", "trigger"))
    if imr is None and not any("impacto_monetario_residual" in x for x in err): falta.append(t("impacto monetario (del riesgo o de la opción)", "monetary impact"))
    x = {"opcion": (o.get("opcion") or "").strip(), "estrategia": est, "descripcion": desc, "disparador": (o.get("disparador") or "").strip(),
         "riesgo_secundario": (o.get("riesgo_secundario") or "").strip(), "notas": (o.get("notas") or "").strip(),
         "costo": costo, "probabilidad_residual": pr, "impacto_residual": ir, "impacto_monetario_residual": imr,
         "monto_contingencia": mc, "emv_secundario": es, "errores": err, "faltan": falta, "avisos": avisos, "recomendada": False}
    if err: x["estado"] = "invalida"; return x
    if falta: x["estado"] = "sin-evaluar"; return x
    ei = emv_inherente(r)
    if ei is None: x["estado"] = "sin-evaluar"; x["faltan"].append(t("EMV inherente del riesgo (impacto_monetario)", "inherent EMV")); return x
    er = PCT[pr] * (imr + mc)                       # la contingencia se paga solo si ocurre: entra ponderada por la probabilidad
    x.update(estado="evaluada", emv_inherente=ei, emv_residual=er, puntuacion_residual=pr * ir,
             delta_emv=(er - ei) if tipo == "oportunidad" else (ei - er))
    x["valor_neto"] = x["delta_emv"] - es - costo
    x["sobre_linea"] = tipo == "amenaza" and pr * ir >= umbral
    p0, i0 = (r.get("probabilidad") or ""), (r.get("impacto") or "")
    if tipo == "amenaza" and p0.isdigit() and i0.isdigit() and (pr > int(p0) or ir > int(i0)):
        avisos.append(t("el residual supera la evaluación inherente", "residual above the inherent assessment"))
    if x["valor_neto"] < 0 and est not in ("aceptar", "escalar"):
        avisos.append(t("cuesta más de lo que reduce: requiere justificación no económica (R-10)", "costs more than it reduces (R-10)"))
    return x

def leer_opciones(proyecto, r, umbral):
    """(ruta, opciones evaluadas y ordenadas, estrategias mínimas que faltan, id recomendada). Sin archivo: opciones None."""
    p = ruta_opciones(proyecto, r["id"])
    if not os.path.exists(p): return p, None, list(MINIMAS.get(r.get("tipo") or "amenaza", [])), ""
    filas = E.leer_filas(p)      # UTF-8 con o sin BOM; otra codificación o CSV mal formado → E.DatosIlegibles
    ops = [evaluar_opcion(o, r, umbral) for o in filas if any((v or "").strip() for v in o.values() if isinstance(v, str))]
    vistos = set()
    for i, o in enumerate(ops, 1):
        if not o["opcion"] or o["opcion"] in vistos: o["opcion"] = f"O{i}" if f"O{i}" not in vistos else f"O{i}-{i}"
        vistos.add(o["opcion"])
    faltan = [s for s in MINIMAS.get(r.get("tipo") or "amenaza", []) if s not in {o["estrategia"] for o in ops}]
    ev = [o for o in ops if o["estado"] == "evaluada"]
    clave = lambda o: (o["sobre_linea"], -o["valor_neto"], o["emv_residual"], o["costo"])
    ev.sort(key=clave)
    rec = ev[0]["opcion"] if len(ev) >= 2 else ""     # recomendar exige comparar: al menos dos opciones evaluadas
    if rec: ev[0]["recomendada"] = True
    resto = [o for o in ops if o["estado"] != "evaluada"]
    return p, ev + sorted(resto, key=lambda o: o["estado"] != "sin-evaluar"), faltan, rec

def umbral_alto(e):
    try: return float((e.get("umbrales_riesgo") or {}).get("alto", E.UMBRAL_RIESGO_ALTO))
    except (TypeError, ValueError): return float(E.UMBRAL_RIESGO_ALTO)

def puntos(r):
    try: return float(r.get("puntuacion") or 0)
    except ValueError: return 0.0

def tiene_plan(proyecto, r):
    """Plan de contingencia: R-###-plan-contingencia.md junto a riesgos.csv, o una ruta …plan-contingencia….md citada en notas o acciones."""
    if os.path.exists(ruta_plan(proyecto, r["id"])): return True
    for m in re.finditer(r"[\w./-]*plan-contingencia[\w.-]*\.md", f"{r.get('notas', '')} {r.get('acciones', '')}"):
        if os.path.exists(os.path.join(proyecto, m.group(0))) or os.path.exists(os.path.join(proyecto, "03-control", "registros", os.path.basename(m.group(0)))): return True
    return False

ARREGLO_REG10 = ("pm-riesgos: evaluar las opciones (riesgos.py --proyecto <dir> opciones --riesgo R-### --proponer; decide el propietario con "
                 "--elegir O# --por …) y, si la respuesta es aceptar o contingencia, disparador medible y plan de contingencia "
                 "(templates/plan-contingencia.md → 03-control/registros/R-###-plan-contingencia.md).")
ARREGLO_REG10_EN = ("pm-riesgos: evaluate the options (riesgos.py --proyecto <dir> opciones --riesgo R-### --proponer; the owner decides with "
                    "--elegir O# --por …) and, if the response is aceptar or contingencia, a measurable trigger and a contingency plan "
                    "(templates/plan-contingencia.md → 03-control/registros/R-###-plan-contingencia.md).")

def controles(proyecto, e, riesgos):
    """REG-10 para sanidad.py (avisos): amenaza abierta con P×I ≥ umbral alto (a) con respuesta elegida y menos de dos
    opciones evaluadas en su archivo de opciones, o (b) con respuesta aceptar o contingencia sin disparador o sin plan de contingencia."""
    out = []; u = umbral_alto(e)
    for r in riesgos:
        if r.get("estado") not in E.REGISTROS["riesgos"]["abiertos"] or (r.get("tipo") or "amenaza") != "amenaza" or puntos(r) < u: continue
        resp = r.get("respuesta") or ""
        if resp and resp != "escalar":
            _, ops, _, _ = leer_opciones(proyecto, r, u)
            if sum(1 for o in (ops or []) if o["estado"] == "evaluada") < 2:      # evaluar es comparar: al menos dos opciones
                out.append(("AVISO", "REG-10", t(f"Riesgo alto {r['id']} con respuesta '{resp}' sin opciones evaluadas (al menos dos entre evitar, reducir, transferir y contingencia).",
                                                 f"High risk {r['id']} with response '{resp}' and no evaluated options (at least two among evitar, reducir, transferir and contingencia)."),
                            t(ARREGLO_REG10, ARREGLO_REG10_EN)))
        if resp in ("aceptar", "contingencia"):
            faltan = ([] if (r.get("disparador") or "").strip() else ["disparador"]) + ([] if tiene_plan(proyecto, r) else ["plan de contingencia"])
            if faltan:
                faltan_en = [{"disparador": "trigger", "plan de contingencia": "contingency plan"}[x] for x in faltan]
                out.append(("AVISO", "REG-10", t(f"Riesgo alto {r['id']} con respuesta '{resp}' sin {' ni '.join(faltan)}.",
                                                 f"High risk {r['id']} with response '{resp}' and no {' or '.join(faltan_en)}."),
                            t(ARREGLO_REG10, ARREGLO_REG10_EN)))
    return out

def plantilla_opciones(r):
    """Filas de la plantilla: estrategias mínimas + compartir (si aplica) + aceptar pasivo como referencia (valor neto 0)."""
    tipo = r.get("tipo") or "amenaza"; pc = "[por confirmar]" if IDIOMA != "en" else "[to be confirmed]"
    ests = (["evitar", "reducir", "transferir", "compartir", "contingencia"] if tipo == "amenaza" else ["explotar", "mejorar", "compartir", "contingencia"])
    pista = {"evitar": t("eliminar la causa (replanificar, cambiar enfoque o proveedor); impacto_monetario_residual=0 si desaparece", "remove the cause"),
             "reducir": t("acción ahora que baja P o I", "action now that lowers P or I"),
             "transferir": t("seguro, garantía o cláusula: impacto_monetario_residual = lo que no cubre el tercero (el atraso no se transfiere)", "insurance or clause: residual = what the third party does not cover"),
             "compartir": t("si aplica (si no, borrar la fila): reparto con fórmula acordada en contrato", "if applicable: contractual sharing formula"),
             "contingencia": t("aceptar con plan de contingencia: P sin cambio, impacto tras el plan, monto_contingencia y disparador medible", "accept with a contingency plan: amount and measurable trigger"),
             "explotar": t("asegurar que ocurra", "make it happen"), "mejorar": t("acción que sube P o el beneficio", "raise P or benefit")}
    filas = [{"opcion": f"O{i}", "estrategia": s, "descripcion": f"{pc} {pista[s]}"} for i, s in enumerate(ests, 1)]
    filas.append({"opcion": f"O{len(ests) + 1}", "estrategia": "aceptar", "descripcion": t("aceptar sin acciones (referencia para comparar)", "accept with no action (baseline)"),
                  "costo": "0", "probabilidad_residual": r.get("probabilidad", ""), "impacto_residual": r.get("impacto", ""),
                  "notas": t("aceptación pasiva: solo revisión periódica", "passive acceptance")})
    return filas

def linea_opcion(o):
    if o["estado"] != "evaluada":
        motivo = "; ".join(o["errores"]) if o["estado"] == "invalida" else t("falta: ", "missing: ") + ", ".join(o["faltan"])
        return f"    {o['opcion']:4s} {o['estrategia']:12s} {o['estado']} · {motivo}"
    marca = "★" if o["recomendada"] else " "
    extra = (f" · {t('contingencia', 'contingency')} {miles(o['monto_contingencia'])}" if o["monto_contingencia"] else "") + \
            (f" · {t('secundario', 'secondary')} {miles(o['emv_secundario'])}" if o["emv_secundario"] else "") + \
            (f" · {t('SOBRE LA LÍNEA', 'ABOVE THE LINE')}" if o["sobre_linea"] else "") + (f" · {'; '.join(o['avisos'])}" if o["avisos"] else "")
    return (f"  {marca} {o['opcion']:4s} {o['estrategia']:12s} {t('costo', 'cost')} {miles(o['costo']):>7} · P×I res {o['probabilidad_residual']}×{o['impacto_residual']}={o['puntuacion_residual']:<2} · "
            f"EMV res {miles(o['emv_residual']):>7} · {t('valor neto', 'net value')} {miles(o['valor_neto']):>7}{extra}")

def cmd_opciones(a, e):
    u = a.umbral if a.umbral is not None else umbral_alto(e)
    p = E.ruta_registro(a.proyecto, "riesgos")
    riesgos = E.leer_csv(p)[1] if os.path.exists(p) else []
    if a.riesgo:
        sel = [r for r in riesgos if r.get("id") == a.riesgo]
        if not sel: sys.exit(t(f"{a.riesgo} no existe en riesgos.csv.", f"{a.riesgo} not found in riesgos.csv."))
    else:
        sel = sorted([r for r in riesgos if r.get("estado") in E.REGISTROS["riesgos"]["abiertos"] and puntos(r) >= u],
                     key=lambda r: (-puntos(r), -(emv_inherente(r) or 0), r["id"]))
    if a.elegir:
        if not a.riesgo: sys.exit(t("--elegir requiere --riesgo R-###.", "--elegir requires --riesgo R-###."))
        return elegir(a, e, sel[0], u)
    creadas, info, errores = [], [], 0
    for r in sel:
        ruta, ops, faltan, rec = leer_opciones(a.proyecto, r, u)
        if ops is None and a.proponer:
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            with open(ruta, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=COLS_OPC); w.writeheader(); w.writerows(plantilla_opciones(r))
            creadas.append(rel(a.proyecto, ruta)); ruta, ops, faltan, rec = leer_opciones(a.proyecto, r, u)
        errores += sum(1 for o in (ops or []) if o["estado"] == "invalida")
        info.append({"id": r["id"], "tipo": r.get("tipo", ""), "evento": r.get("evento", ""), "puntuacion": puntos(r), "emv_inherente": emv_inherente(r),
                     "propietario": r.get("propietario", ""), "respuesta_actual": r.get("respuesta", ""), "disparador_actual": r.get("disparador", ""),
                     "plan_contingencia": tiene_plan(a.proyecto, r), "archivo": rel(a.proyecto, ruta), "opciones": ops, "faltan_estrategias": faltan,
                     "recomendada": rec, "evaluadas": sum(1 for o in (ops or []) if o["estado"] == "evaluada")})
    mostrar = info[:a.max] if a.max else info
    if a.json:
        print(json.dumps({"umbral": u, "total": len(info), "mostrados": len(mostrar), "plantillas_creadas": creadas, "riesgos": mostrar,
                          "nota": t("La recomendada es una propuesta: decide el propietario del riesgo (PUERTA HUMANA).", "The recommended option is a proposal: the risk owner decides.")},
                         ensure_ascii=False, indent=2))
        sys.exit(1 if errores else 0)
    print(t(f"Riesgos abiertos con P×I ≥ {u:g}: {len(info)}", f"Open risks with P×I ≥ {u:g}: {len(info)}") if not a.riesgo else t(f"Riesgo {a.riesgo} (umbral {u:g})", f"Risk {a.riesgo} (threshold {u:g})"))
    for x in mostrar:
        emv = miles(x["emv_inherente"]) if x["emv_inherente"] is not None else "[por confirmar]"
        print(f"\n{x['id']} · {x['tipo']} · P×I {x['puntuacion']:g} · EMV {emv} · {t('propietario', 'owner')} {x['propietario'] or '—'} · "
              f"{t('respuesta actual', 'current response')}: {x['respuesta_actual'] or '—'} · {corto(x['evento'], 70)}")
        if x["opciones"] is None:
            print("    " + t(f"sin opciones evaluadas: {x['archivo']} no existe (--proponer crea la plantilla)", f"no options: {x['archivo']} missing (--proponer creates the template)")); continue
        print(f"    {x['archivo']}")
        for o in x["opciones"][:MAX_OPCIONES]: print(linea_opcion(o))
        if len(x["opciones"]) > MAX_OPCIONES: print(t(f"    … y {len(x['opciones']) - MAX_OPCIONES} opciones más (--json las lista todas)", f"    … and {len(x['opciones']) - MAX_OPCIONES} more"))
        if x["faltan_estrategias"]: print("    " + t("faltan estrategias: ", "missing strategies: ") + ", ".join(x["faltan_estrategias"]))
        if x["recomendada"]:
            o = next(o for o in x["opciones"] if o["opcion"] == x["recomendada"])
            nota = t("todas quedan sobre la línea: combinar respuestas o escalar (R-15, R-16)", "all above the line: combine or escalate") if o["sobre_linea"] else \
                   (t("mayor valor neto bajo la línea", "highest net value below the line"))
            print("    " + t(f"→ recomendada {o['opcion']} ({o['estrategia']}): {nota}. Decide el propietario (PUERTA HUMANA): "
                              f"opciones --riesgo {x['id']} --elegir {o['opcion']} --por \"<rol: nombre>\"",
                              f"→ recommended {o['opcion']} ({o['estrategia']}): {nota}. The owner decides: opciones --riesgo {x['id']} --elegir {o['opcion']} --por \"<role: name>\""))
        elif x["opciones"]: print("    " + t("sin recomendación: hacen falta al menos dos opciones evaluadas (descripción, costo y residual)", "no recommendation: at least two evaluated options are needed"))
    if a.max and len(info) > a.max: print(t(f"\n… y {len(info) - a.max} riesgos más (--max 0 o --riesgo R-###)", f"\n… and {len(info) - a.max} more risks (--max 0 or --riesgo R-###)"))
    for c in creadas: print(t(f"Plantilla creada: {c} (la completa el modelo o la persona; nada se registró)", f"Template created: {c} (nothing was recorded)"))
    sys.exit(1 if errores else 0)

def _registro(proyecto, *args):
    r = subprocess.run([sys.executable, REGISTRO, "--proyecto", proyecto] + list(args), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0: sys.exit((r.stderr or r.stdout).strip())
    return r.stdout.strip()

def elegir(a, e, r, u):
    """Registra la opción que decidió la persona: riesgos.csv (respuesta, residual, disparador, acciones) y decisiones.csv."""
    if not (a.por or "").strip():
        sys.exit(t("PUERTA HUMANA: --elegir registra una decisión de la persona; indicar --por \"<rol: nombre>\" (el propietario del riesgo o la autoridad que fije el enfoque).",
                   "HUMAN GATE: --elegir records a person's decision; pass --por \"<role: name>\"."))
    if r.get("estado") not in E.REGISTROS["riesgos"]["abiertos"]: sys.exit(t(f"{r['id']} no está abierto ({r.get('estado')}).", f"{r['id']} is not open."))
    ruta, ops, _, rec = leer_opciones(a.proyecto, r, u)
    if ops is None: sys.exit(t(f"{rel(a.proyecto, ruta)} no existe: primero opciones --riesgo {r['id']} --proponer y evaluarlas.", f"{rel(a.proyecto, ruta)} missing."))
    o = next((o for o in ops if o["opcion"].lower() == a.elegir.lower()), None)
    if not o: sys.exit(t(f"La opción {a.elegir} no está en {rel(a.proyecto, ruta)}: {', '.join(x['opcion'] for x in ops)}", f"Option {a.elegir} not found."))
    if o["estado"] != "evaluada":
        sys.exit(t(f"{o['opcion']} no está evaluada ({'; '.join(o['errores']) or 'falta: ' + ', '.join(o['faltan'])}).", f"{o['opcion']} is not evaluated."))
    if o["opcion"] != rec and not (a.motivo or "").strip():
        sys.exit(t(f"La recomendada es {rec} y se eligió {o['opcion']}: indicar --motivo (p. ej. justificación no económica, regulatoria o de plazo)." if rec else
                   f"Sin recomendación (menos de dos opciones evaluadas): indicar --motivo para elegir {o['opcion']}.",
                   f"{rec} is recommended and {o['opcion']} was chosen: pass --motivo." if rec else "No recommendation (fewer than two evaluated options): pass --motivo."))
    nivel = a.nivel or "gestor"
    if a.decision:        # decisión ya registrada (p. ej. de la junta, por pm-director): su nivel es el de la fila citada
        pd = E.ruta_registro(a.proyecto, "decisiones")
        fila_d = next((f for f in (E.leer_csv(pd)[1] if os.path.exists(pd) else []) if f.get("id") == a.decision), None)
        if fila_d is None: sys.exit(t(f"{a.decision} no existe en decisiones.csv.", f"{a.decision} not found."))
        nivel = fila_d.get("nivel") or nivel
        if a.nivel and a.nivel != nivel:
            print(t(f"Aviso: --nivel {a.nivel} no se usa: {a.decision} está registrada con nivel {nivel}.", f"Warning: --nivel {a.nivel} is ignored: {a.decision} is recorded at level {nivel}."), file=sys.stderr)
    prop = (r.get("propietario") or "").strip()
    if prop and norm_txt(prop) not in norm_txt(a.por):
        print(t(f"Aviso: decide '{a.por}' y el propietario de {r['id']} es {prop}: confirmar que tiene esa autoridad (enfoque de riesgo).",
                f"Warning: '{a.por}' decides and the owner of {r['id']} is {prop}."), file=sys.stderr)
    fecha = a.fecha or datetime.date.today().isoformat(); arch = rel(a.proyecto, ruta)
    consideradas = " · ".join(f"{x['opcion']} {x['estrategia']} " + (t("neto ", "net ") + miles(x["valor_neto"]) if x["estado"] == "evaluada" else x["estado"]) for x in ops)
    previa = (f"{r['respuesta']} P{r.get('probabilidad_residual') or '?'} I{r.get('impacto_residual') or '?'}" if r.get("respuesta") else "—")
    dec = a.decision or _registro(a.proyecto, "agregar", "decisiones", "--campo", f"fecha={fecha}",
        "--campo", "decision=" + t(f"Respuesta de {r['id']}: {o['estrategia']} ({o['opcion']}) · {o['descripcion']}", f"Response to {r['id']}: {o['estrategia']} ({o['opcion']}) · {o['descripcion']}"),
        "--campo", "contexto=" + t(f"{r['id']} P×I {puntos(r):g}, EMV {miles(o['emv_inherente'])} → residual {miles(o['emv_residual'])}, costo {miles(o['costo'])}, valor neto {miles(o['valor_neto'])}; "
                                   f"recomendada {rec}; respuesta previa {previa}", f"{r['id']} P×I {puntos(r):g}, EMV {miles(o['emv_inherente'])} → {miles(o['emv_residual'])}; recommended {rec}"),
        "--campo", f"opciones_consideradas={consideradas}", "--campo", f"decidido_por={a.por}", "--campo", f"nivel={nivel}",
        "--campo", f"artefactos_afectados=riesgos.csv {r['id']}; {arch}", "--campo", f"notas={a.motivo or ''}").splitlines()[-1]
    acciones = (f"{o['descripcion']} · {t('costo', 'cost')} {miles(o['costo'])} · ΔEMV {miles(o['delta_emv'])} · {t('valor neto', 'net value')} {miles(o['valor_neto'])}"
                + (f" · {t('contingencia', 'contingency')} {miles(o['monto_contingencia'])}" if o["monto_contingencia"] else "") + f" · {o['opcion']} ({arch}) · {dec}")
    campos = [f"respuesta={o['estrategia']}", f"probabilidad_residual={o['probabilidad_residual']}", f"impacto_residual={o['impacto_residual']}", f"acciones={acciones}"]
    if o["disparador"]: campos.append(f"disparador={o['disparador']}")
    if r.get("estado") == "abierto": campos.append("estado=en-seguimiento")
    if a.revision: campos.append(f"fecha_revision={a.revision}")
    _registro(a.proyecto, "actualizar", "riesgos", r["id"], *sum((["--campo", c] for c in campos), []))
    print(t(f"{r['id']}: respuesta {o['estrategia']} ({o['opcion']}) registrada en riesgos.csv · decisión {dec} ({a.por}, nivel {nivel}).",
            f"{r['id']}: response {o['estrategia']} ({o['opcion']}) recorded · decision {dec}."))
    if o["estrategia"] in ("aceptar", "contingencia") and puntos(r) >= u and not tiene_plan(a.proyecto, r):
        print(t(f"Falta el plan de contingencia: templates/plan-contingencia.md → 03-control/registros/{r['id']}-plan-contingencia.md (sanidad REG-10).",
                f"Contingency plan missing: 03-control/registros/{r['id']}-plan-contingencia.md (health REG-10)."))
    if o["costo"] or o["monto_contingencia"]:
        print(t("El costo y la contingencia se financian con el presupuesto de riesgo: uso registrado en cambios.csv con cargo=reserva-riesgo y el R-### (CAM-02, CAM-03); acciones con fecha en acciones.csv (origen R-###).",
                "Cost and contingency are funded from the risk budget: cambios.csv cargo=reserva-riesgo citing the R-### (CAM-02, CAM-03)."))

def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidatos"); c.add_argument("--fuentes"); c.add_argument("--transcripcion", action="append"); c.add_argument("--instantanea")
    c.add_argument("--desde"); c.add_argument("--salida"); c.add_argument("--json", action="store_true"); c.add_argument("--fecha")
    o = sub.add_parser("opciones", help="opciones de respuesta de los riesgos sobre el umbral: comparar, recomendar y registrar la elegida")
    o.add_argument("--riesgo", help="un riesgo R-### (aunque esté bajo el umbral)")
    o.add_argument("--umbral", type=float, help="P×I mínimo (defecto: estado.json.umbrales_riesgo.alto, 15)")
    o.add_argument("--proponer", action="store_true", help="crea la plantilla de opciones de los riesgos que no la tienen (no pisa una existente)")
    o.add_argument("--elegir", metavar="O#", help="registra la opción que decidió la persona (requiere --riesgo y --por)")
    o.add_argument("--por", help="quién decide: \"<rol: nombre>\" (PUERTA HUMANA)")
    o.add_argument("--motivo", help="justificación; obligatoria si la elegida no es la recomendada")
    o.add_argument("--nivel", choices=[x for x in E.REGISTROS["decisiones"]["valores"]["nivel"] if x not in ("junta", "capa-negocio")],
                   help="nivel de la decisión en decisiones.csv (defecto gestor; con --decision, el de esa fila; las de la junta las registra pm-director)")
    o.add_argument("--decision", metavar="D-###", help="cita una decisión ya registrada en lugar de crear otra")
    o.add_argument("--revision", metavar="AAAA-MM-DD", help="próxima revisión del riesgo (fecha_revision)")
    o.add_argument("--fecha", help="fecha de la decisión (defecto: hoy)")
    o.add_argument("--max", type=int, default=10, help="riesgos mostrados (defecto 10; 0 = todos)")
    o.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.proyecto, "estado.json")): sys.exit(f"{a.proyecto}: falta estado.json / not a project folder")
    e = E.cargar_estado(a.proyecto); IDIOMA = e.get("idioma", "es")
    if a.cmd == "opciones": return cmd_opciones(a, e)
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
