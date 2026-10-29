#!/usr/bin/env python3
"""Mapas estratégicos del proyecto: mapas de Wardley (cadena de valor × evolución) y mapas de recorrido del cliente
(customer journey) con carriles de service blueprint. Strategic maps: Wardley maps and customer journey maps.

Fuente de verdad: un JSON por mapa en 02-planificacion/mapas/ (wardley-<slug>.json, esquema pm-mapa-wardley/1;
recorrido-<slug>.json, esquema pm-recorrido/1). Las vistas son derivadas y se regeneran con 'render' en
02-planificacion/visuales/: wardley-<slug>.md (Mermaid wardley-beta + tabla), .owm (OnlineWardleyMaps), .png (si hay mmdc);
recorrido-<slug>.md (Mermaid journey + tablas), .html (carriles y curva de emoción, autocontenido), .png (si hay mmdc).
'tablero' dibuja los mapas válidos en SVG propio (sin mmdc) con los avisos MAP vigentes y los vínculos (dolor → tratamiento,
inercia → riesgo): vista autocontenida 02-planificacion/visuales/tablero-mapas.html y, con --insertar, la sección
«Mapas estratégicos» del tablero de avance de pm-visuales (entre <!-- pm-mapas:inicio --> y <!-- pm-mapas:fin -->).

Uso / Usage (--proyecto va ANTES del tipo de mapa):
  mapas.py --proyecto G wardley semilla [--slug S] [--titulo T] [--pregunta P] [--desde auto|bmad|artefactos]
                                        [--anclas "A; B"] [--componentes "X; Y"] [--fecha AAAA-MM-DD] [--forzar] [--json]
  mapas.py --proyecto G recorrido semilla [--uj UJ-2] [--backstage UJ-3] [--slug S] [--titulo T] [--persona P|PU-###]
                                          [--etapas "A; B"] [--desde auto|bmad|artefactos] [--fecha AAAA-MM-DD] [--forzar] [--json]
  mapas.py --proyecto G wardley|recorrido validar <slug|archivo.json> [--json]
  mapas.py --proyecto G wardley|recorrido render <slug|archivo.json> [--png auto|si|no] [--json]
  mapas.py --proyecto G recorrido candidatos <slug|archivo.json> [--salida F.md] [--json]
  mapas.py --proyecto G vincular <slug|archivo.json> <id de componente o paso> --refs R-001,REQ-003 [--quitar]
  mapas.py --proyecto G controles [--json]          # familia MAP de sanidad (solo avisos)
  mapas.py --proyecto G listar [--json]
  mapas.py --proyecto G tablero [--mapas S1,S2] [--insertar TABLERO.html] [--salida F.html] [--json]
'semilla' propone un esqueleto con posiciones y emociones vacías ([por confirmar]): el modelo propone, la persona confirma.
Nada se registra solo: los candidatos se registran con registro.py después de la evaluación humana.
Decisiones (pm-direccion-decisiones): decision.py expediente lee de aquí (contexto()) los componentes y pasos que citan los
ids de la decisión o que la hoja nombra como '<mapa>:<id>' (entregables:C2); matriz --elegir cita la decisión registrada
en esos elementos llamando a 'vincular'.
"""
import argparse, glob, html, json, os, re, shutil, subprocess, sys, tempfile, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.normpath(os.path.join(AQUI, "..", ".."))
NUCLEO = os.path.join(SK, "pm-estado-proyecto", "scripts")
sys.path.insert(0, NUCLEO)
import esquema as E

IDIOMA = "es"
def t(es, en): return E.t(IDIOMA, es, en)

ESQ_W, ESQ_R = "pm-mapa-wardley/1", "pm-recorrido/1"
ETAPAS = ["genesis", "a-medida", "producto", "commodity"]          # cuartos iguales del eje, como los dibuja Mermaid
LIMITES = [0.0, 0.25, 0.50, 0.75, 1.0]
MARGEN = 0.05                                                       # tolerancia en los bordes entre etapas
ROTULOS = {"es": ["Génesis", "A medida", "Producto / alquiler", "Commodity / servicio"],
           "en": ["Genesis", "Custom built", "Product / rental", "Commodity / utility"]}
DECISIONES = {"": None, "construir": "build", "comprar": "buy", "tercerizar": "outsource", "mercado": "market"}
CAUSAS = ["", "rendimiento", "usabilidad", "propuesta-valor", "dependencia-externa", "proceso-interno", "otro"]
KANO = ["", "obligatorio", "desempeno", "atractivo", "indiferente"]
ESCENARIOS = ["", "actual", "futuro"]
ETIQ = {"es": {"rendimiento": "rendimiento", "usabilidad": "usabilidad", "propuesta-valor": "propuesta de valor", "dependencia-externa": "dependencia externa",
               "proceso-interno": "proceso interno", "otro": "otro", "obligatorio": "Kano: obligatorio", "desempeno": "Kano: desempeño", "atractivo": "Kano: atractivo",
               "indiferente": "Kano: indiferente"},
        "en": {"rendimiento": "performance", "usabilidad": "usability", "propuesta-valor": "value proposition", "dependencia-externa": "external dependency",
               "proceso-interno": "internal process", "otro": "other", "obligatorio": "Kano: must-be", "desempeno": "Kano: performance", "atractivo": "Kano: attractive",
               "indiferente": "Kano: indifferent"}}
def emo(v): return "0" if not v else f"{v:+d}"
def etq(v): return ETIQ.get(IDIOMA, ETIQ["es"]).get(v or "", v or "")
MAX_COMPONENTES, MAX_PASOS, SOLAPE = 15, 15, 0.06
POR_CONFIRMAR = re.compile(r"^\s*$|\[por confirmar\]|\[to be confirmed\]|\[verificar\]", re.I)
REF_REG = re.compile(r"^(R|I|C|D|S|L|ST|Q|A|ET|PF|RC|EN)-\d{3,}$")
REF_ESP = re.compile(r"^(REQ-\d{3}|(FR|NFR|UJ|SM|AD|UX-DR)-\d+|SM-C\d+)$")
TRATAMIENTO = re.compile(r"^(REQ|FR|NFR|R|I|D|S|C|Q)-")   # requisito, riesgo, issue, decisión, supuesto, cambio, revisión de calidad
HISTORIAS = set()   # ids (y números) de historias del backlog vía la fachada; también cuentan como tratamiento (ids_conocidos los carga)

def es_tratamiento(r, ids):
    """Un id existente que trata un dolor: requisito, historia del backlog, riesgo, issue, cambio, decisión, supuesto o Q-###."""
    return r in ids and (bool(TRATAMIENTO.match(r)) or r in HISTORIAS)

# ------------------------------------------------------------------ utilidades
def mapas_dir(p): return os.path.join(p, "02-planificacion", "mapas")
def visuales_dir(p): return os.path.join(p, "02-planificacion", "visuales")

def slugify(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:50] or "mapa"

def resolver(p, tipo, arg):
    if arg.endswith(".json"):
        for c in (arg, os.path.join(p, arg), os.path.join(mapas_dir(p), os.path.basename(arg))):
            if os.path.exists(c): return c
        sys.exit(t(f"No existe {arg}", f"{arg} not found"))
    c = os.path.join(mapas_dir(p), f"{tipo}-{arg}.json")
    if not os.path.exists(c): sys.exit(t(f"No existe {os.path.relpath(c, p)}: crear con '{tipo} semilla --slug {arg}'", f"{c} not found"))
    return c

def cargar(ruta):
    try: return json.load(open(ruta, encoding="utf-8"))
    except (OSError, ValueError) as x: sys.exit(t(f"{ruta}: JSON ilegible ({x})", f"{ruta}: unreadable JSON ({x})"))

def guardar(ruta, d):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    E.escribir_atomico(ruta, json.dumps(d, ensure_ascii=False, indent=2) + "\n")

def num(v):
    if isinstance(v, bool) or v is None: return None
    try: return float(v)
    except (TypeError, ValueError): return None

def etapa_de(x):
    for i in range(4):
        if x < LIMITES[i + 1] or i == 3: return ETAPAS[i]

def lista(v):
    if v is None: return []
    return [x for x in (v if isinstance(v, list) else re.split(r"[;,]\s*", str(v))) if str(x).strip()]

def partes(texto):
    """Divide un recorrido narrado en acciones: oraciones, comas fuera de paréntesis y comillas, y el último ' y ' de cada oración."""
    if len(oraciones(texto)) > 1: return [x for o in oraciones(texto) for x in partes(o)]
    out, buf, prof, comillas = [], "", 0, False
    for ch in texto:
        if ch in "([": prof += 1
        elif ch in ")]": prof = max(0, prof - 1)
        elif ch in "\"«»“”": comillas = not comillas if ch in "\"“”" else (ch == "«")
        if ch == "," and prof == 0 and not comillas: out.append(buf); buf = ""
        else: buf += ch
    out.append(buf)
    out = [x.strip(" .") for x in out if x.strip(" .")]
    if out and re.search(r"\s(y|and)\s", out[-1]) and "(" not in out[-1]:
        a, b = re.split(r"\s(?:y|and)\s", out[-1], maxsplit=1); out[-1:] = [a.strip(), b.strip()]
    return [x[0].upper() + x[1:] for x in out if x]

def oraciones(texto):
    return [x.strip()[0].upper() + x.strip()[1:].rstrip(".") for x in re.split(r"(?<=[.!?])\s+", texto or "") if x.strip()]

def estado_proyecto(p):
    if not os.path.exists(os.path.join(p, "estado.json")): sys.exit(f"{p}: falta estado.json / not a project folder")
    return E.cargar_estado(p)

def ids_conocidos(p):
    """Ids que existen hoy: registros (R-, I-, C-, D-, S-…) y especificación vía la fachada (REQ/FR/NFR/UJ/SM/AD).
    Devuelve (ids, abiertos_por_registro, especificacion_disponible)."""
    ids, abiertos = set(), {}
    for reg, spec in E.REGISTROS.items():
        ruta = E.ruta_registro(p, reg)
        if not os.path.exists(ruta): continue
        filas = E.leer_csv(ruta)[1]
        ids |= {f.get("id", "") for f in filas}
        if spec.get("abiertos"): abiertos[reg] = {f.get("id") for f in filas if f.get("estado") in spec["abiertos"]}
    esp = False
    try:
        import especificacion as SP
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            idx, _ = SP.obtener(p)
        for col in ("requisitos", "historias", "epicas"): ids |= {x.get("id") for x in idx.get(col, [])}
        HISTORIAS.clear(); HISTORIAS.update(str(x.get(k)) for x in idx.get("historias", []) for k in ("id", "numero") if x.get(k))
        ids |= HISTORIAS
        esp = True
    except BaseException:
        pass
    return ids, abiertos, esp

def leer_fm(ruta):
    if not os.path.exists(ruta): return {}
    txt = open(ruta, encoding="utf-8").read()
    if not txt.startswith("---"): return {}
    return dict((k, v.strip().strip('"')) for k, v in re.findall(r"(?m)^(\w+):\s*(.*)$", txt.split("---", 2)[1]))

def frontmatter(tipo, d, e, ruta_md, fuente):
    """Conserva estado, versión y aprobación si la vista ya existía (regenerar no borra una aprobación)."""
    prev = leer_fm(ruta_md)
    estado = prev.get("estado") or "borrador"
    return ["---", f"tipo: {tipo}", f"proyecto: \"{e.get('proyecto', '')}\"", f"version: \"{prev.get('version') or '0.1'}\"",
            f"fecha: {d.get('fecha_corte') or ''}", "autor: \"pm-mapas-estrategicos\"", f"estado: {estado}",
            f"aprobado_por: \"{prev.get('aprobado_por', '')}\"", f"idioma: {IDIOMA}", f"fuente: {fuente}"] + \
           [f"{k}: {v}" for k, v in prev.items() if k not in ("tipo", "proyecto", "version", "fecha", "autor", "estado", "aprobado_por", "idioma", "fuente")] + ["---"], estado

# ------------------------------------------------------------------ validación
def validar_wardley(d):
    err, av = [], []
    if d.get("esquema") != ESQ_W: err.append(t(f"esquema '{d.get('esquema')}' (se espera {ESQ_W})", f"schema '{d.get('esquema')}' (expected {ESQ_W})"))
    if POR_CONFIRMAR.search(str(d.get("pregunta_estrategica") or "")):
        err.append(t("falta pregunta_estrategica: qué decisión informa el mapa", "missing pregunta_estrategica (which decision the map informs)"))
    nodos, nombres = {}, {}
    for tipo in ("anclas", "componentes"):
        for x in d.get(tipo) or []:
            i = str(x.get("id") or "").strip(); n = str(x.get("nombre") or "").strip()
            if not i: err.append(t(f"{tipo}: elemento sin id ({n or '?'})", f"{tipo}: item without id")); continue
            if i in nodos: err.append(t(f"id duplicado {i}", f"duplicate id {i}"))
            if not n: err.append(t(f"{i}: sin nombre", f"{i}: no name"))
            elif n.lower() in nombres: err.append(t(f"{i}: nombre repetido con {nombres[n.lower()]} ('{n}'); Mermaid los fundiría en uno", f"{i}: duplicate name"))
            nombres[n.lower()] = i; nodos[i] = (tipo, x)
            for eje in ("visibilidad", "evolucion"):
                v = x.get(eje)
                if v is None: err.append(t(f"{i} {n}: {eje} sin completar", f"{i}: {eje} missing")); continue
                if num(v) is None or not 0 <= num(v) <= 1: err.append(t(f"{i} {n}: {eje}={v} fuera de 0–1", f"{i}: {eje}={v} outside 0–1"))
            if tipo == "componentes":
                et = x.get("etapa") or ""; ev = num(x.get("evolucion"))
                if et and et not in ETAPAS: err.append(t(f"{i}: etapa '{et}' desconocida ({', '.join(ETAPAS)})", f"{i}: unknown stage '{et}'"))
                elif et and ev is not None and 0 <= ev <= 1:
                    k = ETAPAS.index(et)
                    if not LIMITES[k] - MARGEN <= ev <= LIMITES[k + 1] + MARGEN:
                        err.append(t(f"{i} {n}: etapa '{et}' incoherente con evolución {ev:.2f} (corresponde '{etapa_de(ev)}')", f"{i}: stage '{et}' inconsistent with evolution {ev:.2f}"))
                if (x.get("decision") or "") not in DECISIONES:
                    err.append(t(f"{i}: decision '{x.get('decision')}' desconocida (construir, comprar, tercerizar, mercado)", f"{i}: unknown decision '{x.get('decision')}'"))
                if not isinstance(x.get("inercia", False), bool): err.append(t(f"{i}: inercia debe ser true o false", f"{i}: inercia must be true/false"))
    comps = [i for i, (tp, _) in nodos.items() if tp == "componentes"]
    if not any(tp == "anclas" for tp, _ in nodos.values()): av.append(t("sin anclas: el mapa parte de un usuario o una necesidad", "no anchors"))
    if len(comps) > MAX_COMPONENTES: av.append(t(f"{len(comps)} componentes (recomendado ≤ {MAX_COMPONENTES}: dividir en submapas)", f"{len(comps)} components (≤ {MAX_COMPONENTES} recommended)"))
    grafo, tocados = {}, set()
    for k, l in enumerate(d.get("enlaces") or [], 1):
        a, b = l.get("de"), l.get("a")
        for x in (a, b):
            if x not in nodos: err.append(t(f"enlace {k}: '{x}' no existe", f"link {k}: '{x}' does not exist"))
        if a in nodos and b in nodos:
            if a == b: err.append(t(f"enlace {k}: {a} apunta a sí mismo", f"link {k}: self-link {a}"))
            grafo.setdefault(a, []).append(b); tocados |= {a, b}
    color = {}
    def dfs(u, camino):
        color[u] = 1
        for v in grafo.get(u, []):
            if color.get(v) == 1: err.append(t(f"ciclo en la cadena de valor: {' → '.join(camino + [v])}", f"cycle: {' → '.join(camino + [v])}")); return True
            if not color.get(v) and dfs(v, camino + [v]): return True
        color[u] = 2; return False
    for u in list(grafo):
        if not color.get(u) and dfs(u, [u]): break
    for i in comps:
        if i not in tocados: av.append(t(f"{i} {nodos[i][1].get('nombre')}: huérfano (sin enlaces)", f"{i}: orphan"))
    for k, m in enumerate(d.get("movimientos") or [], 1):
        c = m.get("componente"); h = num(m.get("hacia"))
        if c not in nodos or nodos[c][0] != "componentes": err.append(t(f"movimiento {k}: componente '{c}' no existe", f"move {k}: unknown component '{c}'")); continue
        if h is None or not 0 <= h <= 1: err.append(t(f"movimiento {k}: hacia={m.get('hacia')} fuera de 0–1", f"move {k}: target outside 0–1")); continue
        ev = num(nodos[c][1].get("evolucion"))
        if ev is not None and h <= ev: err.append(t(f"movimiento {k}: {c} evoluciona hacia la izquierda ({ev:.2f} → {h:.2f}); la evolución solo avanza", f"move {k}: {c} evolves leftwards"))
    for k, n in enumerate(d.get("notas") or [], 1):
        for eje in ("visibilidad", "evolucion"):
            if num(n.get(eje)) is None or not 0 <= num(n.get(eje)) <= 1: err.append(t(f"nota {k}: {eje} fuera de 0–1", f"note {k}: {eje} outside 0–1"))
    pos = [(i, num(x.get("visibilidad")), num(x.get("evolucion"))) for i, (_, x) in nodos.items()]
    pos = [p_ for p_ in pos if p_[1] is not None and p_[2] is not None]
    for a in range(len(pos)):
        for b in range(a + 1, len(pos)):
            if ((pos[a][1] - pos[b][1]) ** 2 + (pos[a][2] - pos[b][2]) ** 2) ** 0.5 < SOLAPE:
                av.append(t(f"{pos[a][0]} y {pos[b][0]} casi superpuestos (distancia < {SOLAPE}): separar para que se lean", f"{pos[a][0]} and {pos[b][0]} overlap"))
    return err, av

def pasos_de(d):
    return [(et, p_) for et in d.get("etapas") or [] for p_ in et.get("pasos") or []]

def validar_recorrido(d):
    err, av = [], []
    if d.get("esquema") != ESQ_R: err.append(t(f"esquema '{d.get('esquema')}' (se espera {ESQ_R})", f"schema '{d.get('esquema')}' (expected {ESQ_R})"))
    if POR_CONFIRMAR.search(str(d.get("persona") or "")): err.append(t("falta persona", "missing persona"))
    if (d.get("escenario") or "") not in ESCENARIOS: err.append(t(f"escenario '{d.get('escenario')}' (actual|futuro)", f"scenario '{d.get('escenario')}' (actual|futuro)"))
    vistos = set()
    if not d.get("etapas"): err.append(t("sin etapas", "no stages"))
    for et in d.get("etapas") or []:
        if not et.get("nombre"): err.append(t(f"etapa {et.get('id', '?')} sin nombre", "stage without name"))
        if not et.get("pasos"): err.append(t(f"etapa {et.get('nombre') or et.get('id')}: sin pasos", "stage without steps"))
    for et, p_ in pasos_de(d):
        i = str(p_.get("id") or "")
        if not i: err.append(t(f"paso sin id en '{et.get('nombre')}'", "step without id")); continue
        if i in vistos: err.append(t(f"id duplicado {i}", f"duplicate id {i}"))
        vistos.add(i)
        acc = str(p_.get("accion") or "").strip()
        if not acc: err.append(t(f"{i}: sin acción", f"{i}: no action"))
        elif re.search(r";|→|->|\by luego\b|\band then\b|\.\s+\S", acc):
            err.append(t(f"{i}: más de una acción en el paso ('{acc[:60]}'): una unidad de tiempo, una acción", f"{i}: more than one action in the step"))
        em = p_.get("emocion")
        if em is None: err.append(t(f"{i}: emoción sin completar (−2…+2)", f"{i}: emotion missing (−2…+2)"))
        elif isinstance(em, bool) or not isinstance(em, int) or not -2 <= em <= 2:
            err.append(t(f"{i}: emoción {em!r} fuera de −2…+2 (entero)", f"{i}: emotion {em!r} outside −2…+2 (integer)"))
        eo = p_.get("emocion_objetivo")
        if eo is not None and (isinstance(eo, bool) or not isinstance(eo, int) or not -2 <= eo <= 2):
            err.append(t(f"{i}: emocion_objetivo {eo!r} fuera de −2…+2", f"{i}: target emotion outside −2…+2"))
        if (p_.get("tipo_causa") or "") not in CAUSAS: err.append(t(f"{i}: tipo_causa '{p_.get('tipo_causa')}' ({', '.join(c for c in CAUSAS if c)})", f"{i}: unknown cause type"))
        if (p_.get("kano") or "") not in KANO: err.append(t(f"{i}: kano '{p_.get('kano')}' ({', '.join(k for k in KANO if k)})", f"{i}: unknown Kano class"))
        if p_.get("dolor") and isinstance(em, int) and em >= 1: av.append(t(f"{i}: dolor con emoción positiva ({em}); revisar", f"{i}: pain with positive emotion"))
    if len(vistos) > MAX_PASOS: av.append(t(f"{len(vistos)} pasos (recomendado ≤ {MAX_PASOS}: dividir el recorrido)", f"{len(vistos)} steps (≤ {MAX_PASOS} recommended)"))
    return err, av

# ------------------------------------------------------------------ controles (familia MAP de sanidad, solo avisos)
ARREGLO = {
    "MAP-00": "Corregir el JSON con 'mapas.py … validar' y regenerar las vistas con 'render'.",
    "MAP-01": "Registrar la decisión de construir (registro.py agregar decisiones) y citarla: mapas.py vincular <mapa> <id> --refs D-…; o cambiar a comprar o tercerizar.",
    "MAP-02": "Registrar el riesgo de la inercia con pm-riesgos (registro.py agregar riesgos) y citarlo: mapas.py vincular <mapa> <id> --refs R-…",
    "MAP-03": "Tratar el dolor con un requisito, historia del backlog, riesgo, issue, cambio, decisión, supuesto o revisión de calidad (Q-###) y citarlo con mapas.py vincular (candidatos: mapas.py recorrido candidatos).",
    "MAP-04": "Agregar la evidencia (fuente y cita) o marcar la posición o la emoción como supuesto explícito.",
    "MAP-05": "Corregir el id (mapas.py vincular … --quitar y volver a vincular) o crear el elemento citado.",
}

def controles(p, detalle=None):
    """Lista de hallazgos (severidad, código, mensaje, arreglo) sobre todos los mapas del proyecto. Con una lista en
    'detalle' agrega además {codigo, mensaje, archivo, elemento} por hallazgo (lo usa el tablero de mapas)."""
    out = []
    archivos = sorted(glob.glob(os.path.join(mapas_dir(p), "wardley-*.json")) + glob.glob(os.path.join(mapas_dir(p), "recorrido-*.json")))
    if not archivos: return out
    ids, abiertos, esp = ids_conocidos(p)
    actual = {"archivo": "", "elemento": ""}
    def add(cod, msg, elem=""):
        out.append(("AVISO", cod, msg, ARREGLO[cod]))
        if detalle is not None: detalle.append({"codigo": cod, "mensaje": msg, "archivo": actual["archivo"], "elemento": elem or ""})
    def rotos(nombre, elem, refs):
        for r in refs:
            if (REF_REG.match(r) or (esp and REF_ESP.match(r))) and r not in ids:
                add("MAP-05", t(f"{nombre} {elem} cita {r}, que no existe", f"{nombre} {elem} cites {r}, which does not exist"), elem if elem and not str(elem).startswith("(") else "")
    for ruta in archivos:
        nombre = os.path.basename(ruta); actual["archivo"] = nombre
        try: d = json.load(open(ruta, encoding="utf-8"))
        except (OSError, ValueError) as x: add("MAP-00", t(f"{nombre}: JSON ilegible ({x})", f"{nombre}: unreadable JSON")); continue
        es_w = nombre.startswith("wardley-")
        err, _ = validar_wardley(d) if es_w else validar_recorrido(d)
        if err: add("MAP-00", t(f"{nombre}: {len(err)} error(es) de validación (p. ej. {err[0]})", f"{nombre}: {len(err)} validation error(s)"))
        rotos(nombre, t("(mapa)", "(map)"), lista(d.get("refs")) + lista(d.get("kpi")) + lista(d.get("contrapesos")))
        if es_w:
            for a in d.get("anclas") or []: rotos(nombre, a.get("id"), lista(a.get("refs")))
            for c in d.get("componentes") or []:
                cid = f"{c.get('id')} {c.get('nombre', '')}"; refs = lista(c.get("refs")); rotos(nombre, c.get("id"), refs)
                ev = num(c.get("evolucion")); et = c.get("etapa") or (etapa_de(ev) if ev is not None and 0 <= ev <= 1 else "")
                if et in ("producto", "commodity") and c.get("decision") == "construir" and not any(r.startswith("D-") and r in ids for r in refs):
                    add("MAP-01", t(f"{nombre} {cid}: en {et} y marcado 'construir' sin decisión registrada", f"{nombre} {cid}: in {et} and marked 'build' without a recorded decision"), c.get("id"))
                if c.get("inercia") is True and not any(r in abiertos.get("riesgos", set()) for r in refs):
                    add("MAP-02", t(f"{nombre} {cid}: inercia sin riesgo abierto registrado", f"{nombre} {cid}: inertia without an open risk"), c.get("id"))
                if (c.get("visibilidad") is not None or ev is not None) and POR_CONFIRMAR.search(str(c.get("evidencia") or "")):
                    add("MAP-04", t(f"{nombre} {cid}: ubicación sin evidencia", f"{nombre} {cid}: position without evidence"), c.get("id"))
        else:
            for _, p_ in pasos_de(d):
                pid = f"{p_.get('id')} «{str(p_.get('accion') or '')[:50]}»"; refs = lista(p_.get("refs")); rotos(nombre, p_.get("id"), refs)
                if str(p_.get("dolor") or "").strip() and not any(es_tratamiento(r, ids) for r in refs):
                    add("MAP-03", t(f"{nombre} {pid}: dolor sin tratamiento (requisito, historia, riesgo, issue, cambio, decisión, supuesto o revisión de calidad)", f"{nombre} {pid}: pain point without treatment"), p_.get("id"))
                if p_.get("emocion") is not None and POR_CONFIRMAR.search(str(p_.get("fuente_emocion") or "")):
                    add("MAP-04", t(f"{nombre} {pid}: emoción sin fuente (entrevista, métrica, observación o supuesto declarado)", f"{nombre} {pid}: emotion without source"), p_.get("id"))
    return out

# ------------------------------------------------------------------ contexto para una decisión (decision.py)
ELEMENTO = re.compile(r"^(?P<mapa>[^:\s]+):(?P<elem>[A-Za-z][\w-]*)$")   # entregables:C2, wardley-entregables:C2, recorrido-paciente.json:P4

def es_elemento(x):
    """¿`x` nombra un elemento de un mapa como '<mapa>:<id>'?"""
    return bool(ELEMENTO.match(str(x or "")))

def contexto(p, ids=(), elementos=()):
    """Contexto de los mapas para una decisión (solo lectura; lo usan decision.py expediente y matriz --elegir).
    Entra cada componente de un mapa de Wardley y cada paso de un recorrido que cita en `refs` alguno de `ids`, o que
    `elementos` nombra como '<mapa>:<id>' (mapa = slug, wardley-<slug>, recorrido-<slug> o el archivo .json). Los campos
    salen tal como están en el JSON, con la cita archivo#id; nada se interpreta ni se puntúa. Devuelve (items, faltan):
    `faltan` lista los elementos nombrados que no existen (o que son anclas)."""
    ids = {str(x) for x in ids if x}
    archivos = sorted(glob.glob(os.path.join(mapas_dir(p), "wardley-*.json"))) + sorted(glob.glob(os.path.join(mapas_dir(p), "recorrido-*.json")))
    mapas = {}
    for ruta in archivos:
        try: mapas[ruta] = json.load(open(ruta, encoding="utf-8"))
        except (OSError, ValueError): pass                         # MAP-00 de la sanidad
    nombrados, faltan = {}, []
    for x in elementos:
        m = ELEMENTO.match(str(x or ""))
        if not m: continue
        b = os.path.basename(m["mapa"])
        cands = [b] if b.endswith(".json") else [f"{b}.json", f"wardley-{b}.json", f"recorrido-{b}.json"]
        rutas = [r for r in archivos if os.path.basename(r) in cands and r in mapas]
        hall = [(r, m["elem"]) for r in rutas if any(e_.get("id") == m["elem"] for e_ in (mapas[r].get("componentes") or []) + [q_ for _, q_ in pasos_de(mapas[r])])]
        if hall: nombrados[hall[0]] = x
        elif rutas: faltan.append(t(f"{x}: {m['elem']} no es un componente ni un paso de {', '.join(os.path.basename(r) for r in rutas)}",
                                    f"{x}: {m['elem']} is not a component or step of {', '.join(os.path.basename(r) for r in rutas)}"))
        else: faltan.append(t(f"{x}: no hay un mapa '{m['mapa']}' legible en 02-planificacion/mapas/", f"{x}: no readable map '{m['mapa']}' in 02-planificacion/mapas/"))
    items = []
    for ruta, d in mapas.items():
        rel = os.path.relpath(ruta, p).replace(os.sep, "/"); base = os.path.basename(ruta)
        def motivo(e_):
            citados = [r for r in lista(e_.get("refs")) if r in ids]
            return citados, nombrados.get((ruta, e_.get("id")), "")
        if base.startswith("wardley-"):
            nom = {x.get("id"): x.get("nombre", "") for x in (d.get("anclas") or []) + (d.get("componentes") or [])}
            for c in d.get("componentes") or []:
                citados, nombre = motivo(c)
                if not citados and not nombre: continue
                ev = num(c.get("evolucion"))
                mov = next(({"hacia": num(m_.get("hacia")), "motivo": m_.get("motivo", "")} for m_ in d.get("movimientos") or [] if m_.get("componente") == c.get("id")), None)
                items.append({"tipo": "wardley", "mapa": rel, "archivo": base, "elemento": c.get("id"), "cita": f"{rel}#{c.get('id')}", "nombrado": nombre, "cita_ids": citados,
                              "titulo": d.get("titulo", ""), "nombre": c.get("nombre", ""), "etapa": c.get("etapa") or (etapa_de(ev) if ev is not None and 0 <= ev <= 1 else ""),
                              "evolucion": ev, "visibilidad": num(c.get("visibilidad")), "decision": c.get("decision") or "", "inercia": c.get("inercia") is True,
                              "evidencia": c.get("evidencia") or "", "dependen": [f"{l.get('de')} {nom.get(l.get('de'), '')}".strip() for l in d.get("enlaces") or [] if l.get("a") == c.get("id")],
                              "movimiento": mov, "refs": lista(c.get("refs"))})
        else:
            for et, q_ in pasos_de(d):
                citados, nombre = motivo(q_)
                if not citados and not nombre: continue
                items.append({"tipo": "recorrido", "mapa": rel, "archivo": base, "elemento": q_.get("id"), "cita": f"{rel}#{q_.get('id')}", "nombrado": nombre, "cita_ids": citados,
                              "titulo": d.get("titulo", ""), "etapa": et.get("nombre", ""), "accion": q_.get("accion", ""), "emocion": q_.get("emocion"),
                              "fuente_emocion": q_.get("fuente_emocion") or "", "emocion_objetivo": q_.get("emocion_objetivo"), "dolor": q_.get("dolor") or "",
                              "tipo_causa": q_.get("tipo_causa") or "", "oportunidad": q_.get("oportunidad") or "", "kano": q_.get("kano") or "",
                              "kpi": lista(d.get("kpi")), "contrapesos": lista(d.get("contrapesos")), "persona": d.get("persona") or "", "persona_id": d.get("persona_id") or "",
                              "refs": lista(q_.get("refs"))})
    return items, faltan

# ------------------------------------------------------------------ semillas
def bmad_mod():
    sys.path.insert(0, os.path.join(SK, "pm-bmad-puente", "scripts"))
    import bmad as B
    return B

def corto(texto, n=48):
    texto = re.sub(r"\s+", " ", texto or "").strip().rstrip(".")
    if len(texto) <= n: return texto
    return texto[:n].rsplit(" ", 1)[0] + "…"

def insumos_artefactos(p):
    """Lo que el proyecto ya sabe y sirve de evidencia: supuestos, riesgos, decisiones, lecciones (solo ids y texto breve)."""
    out = []
    for reg, campo in (("supuestos", "supuesto_o_restriccion"), ("riesgos", "evento"), ("decisiones", "decision"), ("lecciones", "situacion")):
        ruta = E.ruta_registro(p, reg)
        if os.path.exists(ruta):
            for f in E.leer_csv(ruta)[1]: out.append({"id": f.get("id"), "texto": corto(f.get(campo), 90), "fuente": f"{reg}.csv"})
    for rel in ("00-direccion/mandato.md", "01-inicio/project-brief.md", "00-direccion/business-case-esquematico.md", "00-direccion/business-case.md"):
        if os.path.exists(os.path.join(p, rel)): out.append({"id": "", "texto": t("leer: necesidad del usuario, opciones y supuestos", "read: user need, options, assumptions"), "fuente": rel})
    return out

def desde_de(e, pedido):
    if pedido and pedido != "auto": return pedido
    return "bmad" if e.get("integraciones", {}).get("especificacion") == "bmad" else "artefactos"

def semilla_wardley(a, e):
    p = a.proyecto; desde = desde_de(e, a.desde)
    anclas, comps, enlaces, fuentes = [], [], [], []
    vacio = lambda i, n, refs=(), nota="", sug="": {"id": i, "nombre": n, "visibilidad": None, "evolucion": None, "etapa": "", "evidencia": "[por confirmar]",
                                                   "refs": list(refs), "decision": "", "inercia": False, "nota": nota, **({"sugerencia": sug} if sug else {})}
    for k, x in enumerate(lista(a.anclas), 1): anclas.append({"id": f"A{k}", "nombre": x.strip(), "visibilidad": None, "evolucion": None, "refs": []})
    for k, x in enumerate(lista(a.componentes), 1): comps.append(vacio(f"C{k}", x.strip()))
    if desde == "bmad" and not comps:
        B = bmad_mod(); b = B.detectar_bmad(p, None, e); arts = B.inventario(b)
        ujs = B.recorridos(arts); cap = B.capacidades(arts)
        if not anclas:
            for u in ujs: anclas.append({"id": f"A{len(anclas) + 1}", "nombre": corto(f"{u['id']} · {u['titulo']}", 44), "visibilidad": None, "evolucion": None, "refs": [u["id"]],
                                         "_frs": u["frs"] + u["frs_seccion"]})
        for c in cap["capacidades"]:
            comps.append(vacio(f"C{len(comps) + 1}", corto(c["capacidad"], 40), c["ids"] + c["ad"], f"{c['modulo']} · {c['fuente']}:{c['linea']}"))
            comps[-1]["_ids"] = c["ids"]
        for x in cap["diferidas"]:
            comps.append(vacio(f"C{len(comps) + 1}", corto(x["tema"], 40), [], t(f"decisión diferida en la arquitectura · {x['fuente']}:{x['linea']}", f"deferred decision · {x['fuente']}:{x['linea']}"),
                               t("candidato a comprar o tercerizar: decidir con pm-adquisiciones (hacer o comprar)", "buy/outsource candidate: decide with make-or-buy")))
        for an in anclas:
            for c in comps:
                if set(an.get("_frs", [])) & set(c.get("_ids", [])): enlaces.append({"de": an["id"], "a": c["id"]})
        for x in anclas + comps: x.pop("_frs", None); x.pop("_ids", None)
        fuentes = sorted({u["fuente"] for u in ujs} | {c["fuente"] for c in cap["capacidades"]} | {x["fuente"] for x in cap["diferidas"]})
    elif not comps:
        wbs = os.path.join(p, "02-planificacion", "wbs.csv")
        if os.path.exists(wbs):
            import csv
            for f in csv.DictReader(open(wbs, encoding="utf-8")):
                if f.get("tipo") == "producto": comps.append(vacio(f"C{len(comps) + 1}", corto(f.get("nombre"), 40), [], f"WBS {f.get('codigo')}"))
            fuentes.append("02-planificacion/wbs.csv")
        if not comps:
            try:
                import especificacion as SP
                idx, _ = SP.obtener(p)
                for q in idx.get("requisitos", [])[:MAX_COMPONENTES]: comps.append(vacio(f"C{len(comps) + 1}", corto(q.get("titulo"), 40), [q["id"]]))
                if comps: fuentes.append("especificacion.py (fachada)")
            except BaseException: pass
    if not anclas: anclas.append({"id": "A1", "nombre": t("[por confirmar: usuario o necesidad]", "[to be confirmed: user or need]"), "visibilidad": None, "evolucion": None, "refs": []})
    d = {"esquema": ESQ_W, "titulo": a.titulo or t("Mapa de valor", "Value map"),
         "pregunta_estrategica": a.pregunta or t("[por confirmar: qué decisión informa este mapa]", "[to be confirmed]"),
         "alcance": "", "fecha_corte": a.fecha or datetime.date.today().isoformat(), "estado": "borrador", "fuentes": fuentes,
         "anclas": anclas, "componentes": comps, "enlaces": enlaces, "movimientos": [], "notas": [],
         "insumos": insumos_artefactos(p)}
    return d, desde

def semilla_recorrido(a, e):
    p = a.proyecto; desde = desde_de(e, a.desde)
    paso = lambda i, acc, cita="": {"id": i, "accion": acc, "punto_contacto": "", "canal": "", "emocion": None, "fuente_emocion": "[por confirmar]",
                                     "dolor": "", "tipo_causa": "", "oportunidad": "", "kano": "", "refs": [], **({"cita": cita} if cita else {})}
    d = {"esquema": ESQ_R, "titulo": a.titulo or "", "persona": a.persona or "", "trabajo": "", "disparador": "", "escenario": "actual", "exito": "",
         "fecha_corte": a.fecha or datetime.date.today().isoformat(), "estado": "borrador", "fuentes": [], "refs": [], "kpi": [], "contrapesos": [], "etapas": []}
    n = 0
    def nuevo(acc, cita=""):
        nonlocal n; n += 1; return paso(f"P{n}", acc, cita)
    if desde == "bmad" and a.uj:
        B = bmad_mod(); b = B.detectar_bmad(p, None, e); ujs = {u["id"]: u for u in B.recorridos(B.inventario(b))}
        q = re.sub(r"^UJ-?(\d+)$", lambda m: f"UJ-{int(m.group(1))}", a.uj.strip(), flags=re.I)
        if q not in ujs: sys.exit(t(f"No se encontró {a.uj} en el PRD de BMAD (bmad.py recorridos)", f"{a.uj} not found in the BMAD PRD"))
        u = ujs[q]; cita = f"{u['fuente']}:{u['linea']}"
        d.update({"titulo": a.titulo or f"{u['id']} · {u['titulo']}", "persona": a.persona or u["persona"], "disparador": u["entrada"], "exito": u["resolucion"],
                  "fuentes": [cita], "refs": [u["id"]] + u["frs"] + u["frs_seccion"], "kpi": u["kpi"], "contrapesos": u["contrapesos"]})
        d["etapas"] = [{"id": "E1", "nombre": t("Recorrido", "Journey"), "pasos": [nuevo(x, cita) for x in partes(u["recorrido"])]},
                       {"id": "E2", "nombre": t("Clímax", "Climax"), "pasos": [nuevo(x, cita) for x in oraciones(u["climax"])]},
                       {"id": "E3", "nombre": t("Resolución", "Resolution"), "pasos": [nuevo(x, cita) for x in partes(u["resolucion"])]}]
        d["etapas"] = [x for x in d["etapas"] if x["pasos"]]
        if u["caso_limite"]: d["variantes"] = [{"descripcion": u["caso_limite"], "cita": cita}]
        if a.backstage:
            qb = re.sub(r"^UJ-?(\d+)$", lambda m: f"UJ-{int(m.group(1))}", a.backstage.strip(), flags=re.I)
            if qb not in ujs: sys.exit(t(f"No se encontró {a.backstage} en el PRD", f"{a.backstage} not found"))
            ub = ujs[qb]
            d["pendiente_alinear"] = {"backstage": partes(ub["recorrido"]) + oraciones(ub["climax"]), "fuente": f"{ub['id']} · {ub['fuente']}:{ub['linea']}"}
            d["refs"].append(ub["id"])
    else:
        nombres = lista(a.etapas) or [t("Antes", "Before"), t("Durante", "During"), t("Después", "After")]
        d["etapas"] = [{"id": f"E{k}", "nombre": x.strip(), "pasos": [nuevo(t("[por confirmar: una acción]", "[to be confirmed: one action]"))]} for k, x in enumerate(nombres, 1)]
        d["persona"] = a.persona or t("[por confirmar]", "[to be confirmed]")
        trans = sorted(glob.glob(os.path.join(p, "03-control", "reuniones", "*transcripcion*.md")))
        d["fuentes"] = [os.path.relpath(x, p) for x in trans]
        d["insumos"] = insumos_artefactos(p)
    if re.match(r"^PU-\d{3,}$", (a.persona or "").strip()):   # persona de usuario registrada (personas.csv, pm-interesados)
        rp = E.ruta_registro(p, "personas")
        pu = next((f for f in (E.leer_csv(rp)[1] if os.path.exists(rp) else []) if f.get("id") == a.persona.strip()), None)
        if not pu: sys.exit(t(f"No existe {a.persona} en personas.csv (interesados.py personas candidatos)", f"{a.persona} not found in personas.csv"))
        d.update({"persona": ", ".join(x for x in (pu.get("nombre"), pu.get("descripcion")) if x), "persona_id": pu["id"],
                  "trabajo": d.get("trabajo") or pu.get("objetivo") or "", "disparador": d.get("disparador") or pu.get("contexto_uso") or ""})
    return d, desde

# ------------------------------------------------------------------ vistas
def q(nombre): return '"' + str(nombre).replace('"', "'").replace("\n", " ").strip() + '"'

def mermaid_wardley(d):
    titulo = re.sub(r'[\n"]', " ", d.get("titulo") or "")
    L = ["wardley-beta", f"title {titulo}" + (" (BORRADOR)" if d.get("estado", "borrador") != "aprobado" else ""),
         "size [1100, 700]", "evolution " + " -> ".join(q(x) for x in ROTULOS.get(IDIOMA, ROTULOS["es"]))]
    nom = {}
    for x in d.get("anclas") or []:
        nom[x["id"]] = x["nombre"]; L.append(f"anchor {q(x['nombre'])} [{num(x['visibilidad']):.2f}, {num(x['evolucion']):.2f}]")
    for x in d.get("componentes") or []:
        nom[x["id"]] = x["nombre"]; deco = DECISIONES.get(x.get("decision") or "")
        L.append(f"component {q(x['nombre'])} [{num(x['visibilidad']):.2f}, {num(x['evolucion']):.2f}]" + (f" ({deco})" if deco else "") + (" (inertia)" if x.get("inercia") else ""))
    for l in d.get("enlaces") or []: L.append(f"{q(nom[l['de']])} -> {q(nom[l['a']])}")
    for m in d.get("movimientos") or []: L.append(f"evolve {q(nom[m['componente']])} {num(m['hacia']):.2f}")
    for n in d.get("notas") or []: L.append(f"note {q(n.get('texto', ''))} [{num(n['visibilidad']):.2f}, {num(n['evolucion']):.2f}]")
    return "\n".join(L)

def owm(d):
    lim = lambda s: re.sub(r"\s+", " ", re.sub(r"->|[\[\]()]", " ", str(s))).strip()
    L = [f"title {lim(d.get('titulo'))}", "evolution " + "->".join(lim(x) for x in ROTULOS.get(IDIOMA, ROTULOS["es"]))]
    nom = {}
    for x in d.get("anclas") or []:
        nom[x["id"]] = lim(x["nombre"]); L.append(f"anchor {nom[x['id']]} [{num(x['visibilidad']):.2f}, {num(x['evolucion']):.2f}]")
    for x in d.get("componentes") or []:
        nom[x["id"]] = lim(x["nombre"]); deco = DECISIONES.get(x.get("decision") or "")
        L.append(f"component {nom[x['id']]} [{num(x['visibilidad']):.2f}, {num(x['evolucion']):.2f}]" + (f" ({deco})" if deco else "") + (" inertia" if x.get("inercia") else ""))
    for l in d.get("enlaces") or []: L.append(f"{nom[l['de']]}->{nom[l['a']]}")
    for m in d.get("movimientos") or []: L.append(f"evolve {nom[m['componente']]} {num(m['hacia']):.2f}")
    for n in d.get("notas") or []: L.append(f"note {lim(n.get('texto', ''))} [{num(n['visibilidad']):.2f}, {num(n['evolucion']):.2f}]")
    return "\n".join(L) + "\n"

def celda(s): return str(s or "").replace("|", "/").replace("\n", " ").strip()

LECTURA = {"genesis": ("adaptativo; exploración con experimentos", "adaptive; explore with experiments"),
           "a-medida": ("adaptativo o híbrido; construir si diferencia", "adaptive or hybrid; build if it differentiates"),
           "producto": ("híbrido; preferir comprar o configurar", "hybrid; prefer buying or configuring"),
           "commodity": ("predictivo; comprar, tercerizar o usar como servicio", "predictive; buy, outsource or use as a service")}

def md_wardley(d, e, ruta_md, fuente):
    fm, estado = frontmatter(f"mapa-wardley-{d['_slug']}", d, e, ruta_md, fuente)
    d = {**d, "estado": estado}
    nom = {x["id"]: x["nombre"] for x in (d.get("anclas") or []) + (d.get("componentes") or [])}
    L = fm + ["", f"# {t('Mapa de Wardley', 'Wardley map')} · {celda(d.get('titulo'))}" + ("" if estado == "aprobado" else " (BORRADOR)"), "",
              f"**{t('Pregunta estratégica', 'Strategic question')}:** {celda(d.get('pregunta_estrategica'))}  ",
              f"**{t('Alcance', 'Scope')}:** {celda(d.get('alcance')) or '—'} · **{t('Corte', 'Cut-off')}:** {d.get('fecha_corte')} · **{t('Fuentes', 'Sources')}:** {celda('; '.join(lista(d.get('fuentes')))) or '—'}", "",
              "```mermaid", mermaid_wardley(d), "```", "",
              t("Eje vertical: visibilidad para el usuario (arriba, lo que el usuario ve). Eje horizontal: evolución (génesis → a medida → producto → commodity); "
                "Mermaid rotula los ejes en inglés (Visibility, Evolution). Marcas: (build) construir, (buy) comprar, (outsource) tercerizar, (market) mercado; "
                "barra = inercia; flecha punteada = movimiento previsto. La evolución no es un cronograma.",
                "Vertical axis: visibility to the user. Horizontal axis: evolution. The evolution axis is not a timeline."), "",
              f"| {t('Componente', 'Component')} | {t('Etapa', 'Stage')} | {t('Evolución', 'Evolution')} | {t('Visibilidad', 'Visibility')} | {t('Decisión', 'Decision')} | {t('Inercia', 'Inertia')} | {t('Evidencia', 'Evidence')} | Refs | {t('Lectura sugerida', 'Suggested reading')} |",
              "|---|---|---|---|---|---|---|---|---|"]
    inerciales = {x["id"] for x in d.get("componentes") or [] if x.get("inercia")}
    depende = {}
    for l in d.get("enlaces") or []: depende.setdefault(l["de"], []).append(l["a"])
    for x in d.get("componentes") or []:
        ev = num(x.get("evolucion")); et = x.get("etapa") or etapa_de(ev)
        dep = [c for c in depende.get(x["id"], []) if c in inerciales]
        lectura = (t("predictivo con hitos de validación: depende de un componente con inercia", "predictive with validation milestones: depends on a component with inertia") + f" ({', '.join(dep)})") if dep else (
            t("riesgo de inercia: registrarlo y planificar la transición", "inertia risk: register it and plan the transition") if x.get("inercia") else t(*LECTURA[et]))
        L.append(f"| {x['id']} {celda(x['nombre'])} | {et} | {ev:.2f} | {num(x.get('visibilidad')):.2f} | {x.get('decision') or '—'} | {t('sí', 'yes') if x.get('inercia') else '—'} | "
                 f"{celda(x.get('evidencia'))} | {', '.join(lista(x.get('refs'))) or '—'} | {lectura} |")
    if d.get("movimientos"):
        L += ["", f"## {t('Movimientos previstos', 'Expected movements')}", ""] + [f"- {nom.get(m['componente'], m['componente'])}: {t('hacia', 'to')} {num(m['hacia']):.2f}" + (f" · {celda(m.get('motivo'))}" if m.get("motivo") else "") for m in d["movimientos"]]
    L += ["", t("Lectura sugerida: heurística del paquete para contrastar el enfoque de entrega y el hacer o comprar; no es una regla de PRINCE2 ni reemplaza los nueve criterios del enfoque.",
                "Suggested reading: package heuristic; not a PRINCE2 rule."), ""]
    return "\n".join(L)

def sanear_journey(s): return re.sub(r"\s+", " ", re.sub(r"[:;#\n]", " -", str(s or ""))).strip(" -")

def mermaid_journey(d):
    actor = sanear_journey(re.split(r"[,(]", d.get("persona") or "Persona")[0])[:30] or "Persona"
    L = ["journey", f"  title {sanear_journey(d.get('titulo'))}" + (" (BORRADOR)" if d.get("estado", "borrador") != "aprobado" else "")]
    for et in d.get("etapas") or []:
        L.append(f"  section {sanear_journey(et.get('nombre'))}")
        for p_ in et.get("pasos") or []: L.append(f"    {sanear_journey(p_.get('accion'))}: {int(p_['emocion']) + 3}: {actor}")
    return "\n".join(L)

def md_recorrido(d, e, ruta_md, fuente, ids):
    fm, estado = frontmatter(f"mapa-recorrido-{d['_slug']}", d, e, ruta_md, fuente)
    d = {**d, "estado": estado}
    L = fm + ["", f"# {t('Mapa de recorrido del cliente', 'Customer journey map')} · {celda(d.get('titulo'))}" + ("" if estado == "aprobado" else " (BORRADOR)"), "",
              f"**{t('Persona', 'Persona')}:** {celda(d.get('persona'))}  ", f"**{t('Trabajo a resolver', 'Job to be done')}:** {celda(d.get('trabajo')) or '—'} · "
              f"**{t('Disparador', 'Trigger')}:** {celda(d.get('disparador')) or '—'} · **{t('Escenario', 'Scenario')}:** {d.get('escenario') or '—'}  ",
              f"**{t('Éxito', 'Success')}:** {celda(d.get('exito')) or '—'} · **KPI:** {', '.join(lista(d.get('kpi'))) or '—'}" + (f" · **{t('Contrapesos', 'Counter-metrics')}:** {', '.join(lista(d.get('contrapesos')))}" if d.get("contrapesos") else "") + "  ",
              f"**{t('Corte', 'Cut-off')}:** {d.get('fecha_corte')} · **Refs:** {', '.join(lista(d.get('refs'))) or '—'} · **{t('Fuentes', 'Sources')}:** {celda('; '.join(lista(d.get('fuentes')))) or '—'}", "",
              "```mermaid", mermaid_journey(d), "```", "",
              t("Puntaje de Mermaid = emoción + 3 (−2…+2 → 1…5). La vista completa, con carriles y curva de emoción, está en el HTML del mismo nombre.",
                "Mermaid score = emotion + 3. The full view (lanes and emotion curve) is in the HTML file of the same name."), "",
              f"| {t('Etapa', 'Stage')} | {t('Paso', 'Step')} | {t('Acción', 'Action')} | {t('Punto de contacto', 'Touchpoint')} | {t('Emoción', 'Emotion')} | {t('Fuente', 'Source')} | {t('Dolor (causa)', 'Pain (cause)')} | {t('Oportunidad (Kano)', 'Opportunity (Kano)')} | {t('Tratamiento', 'Treatment')} |",
              "|---|---|---|---|---|---|---|---|---|"]
    for et, p_ in pasos_de(d):
        refs = lista(p_.get("refs")); trat = [r for r in refs if es_tratamiento(r, ids)]
        dolor = celda(p_.get("dolor"))
        pc = celda(" · ".join(x for x in (p_.get("punto_contacto"), p_.get("canal")) if x)) or "—"
        c_dolor = (dolor + (" (" + etq(p_["tipo_causa"]) + ")" if p_.get("tipo_causa") else "")) if dolor else "—"
        c_op = (celda(p_.get("oportunidad")) + (" (" + etq(p_["kano"]) + ")" if p_.get("kano") else "")) if p_.get("oportunidad") else "—"
        c_tr = ", ".join(trat) if trat else (t("**sin tratamiento**", "**untreated**") if dolor else "—")
        L.append(f"| {celda(et.get('nombre'))} | {p_['id']} | {celda(p_.get('accion'))} | {pc} | {emo(p_.get('emocion'))} | {celda(p_.get('fuente_emocion'))} | {c_dolor} | {c_op} | {c_tr} |")
    carriles = [c for c in ("frontstage", "backstage", "soporte") if any(p_.get(c) for _, p_ in pasos_de(d))]
    if carriles:
        L += ["", f"## {t('Carriles internos (service blueprint)', 'Internal lanes (service blueprint)')}", "",
              "| " + t("Paso", "Step") + " | " + " | ".join(carriles) + " |", "|---" * (len(carriles) + 1) + "|"]
        L += [f"| {p_['id']} | " + " | ".join(celda(p_.get(c)) or "—" for c in carriles) + " |" for _, p_ in pasos_de(d)]
    if d.get("variantes"):
        L += ["", f"## {t('Variantes y casos límite', 'Variants and edge cases')}", ""] + [f"- {celda(v.get('descripcion'))}" + (f" ({v['cita']})" if v.get("cita") else "") for v in d["variantes"]]
    return "\n".join(L) + "\n"

def svg_emocion(pasos, colw):
    n = len(pasos); w, h, top = n * colw, 150, 12
    y = lambda v: top + (2 - v) * (h - 2 * top) / 4
    x = lambda i: i * colw + colw / 2
    s = [f'<svg class="curva" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(t("Curva de emoción", "Emotion curve"))}">',
         f'<rect x="0" y="{y(0):.1f}" width="{w}" height="{h - top - y(0):.1f}" class="zona-dolor"/>']
    for v in (2, 1, 0, -1, -2): s.append(f'<line x1="0" x2="{w}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="{"cero" if v == 0 else "guia"}"/>')
    obj = [(i, p_.get("emocion_objetivo")) for i, p_ in enumerate(pasos) if p_.get("emocion_objetivo") is not None]
    if obj: s.append('<polyline class="objetivo" points="' + " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in obj) + '"/>')
    for i, v in obj: s.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="5" class="meta-obj"><title>{html.escape(t("emoción esperada", "expected emotion"))}: {v:+d}</title></circle>')
    s.append('<polyline class="linea" points="' + " ".join(f"{x(i):.1f},{y(p_['emocion']):.1f}" for i, p_ in enumerate(pasos)) + '"/>')
    for i, p_ in enumerate(pasos):
        v = p_["emocion"]
        s.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="7" class="{"neg" if v < 0 else ("pos" if v > 0 else "neu")}"><title>{html.escape(str(p_.get("accion")))}: {v:+d}</title></circle>')
        s.append(f'<text x="{x(i) + 9:.1f}" y="{y(v) + (18 if v == 2 else -9):.1f}" class="valor">{emo(v)}</text>')
    return "".join(s) + "</svg>"

def html_recorrido(d, e, ids, estado):
    plantilla = open(os.path.join(SK, "pm-mapas-estrategicos", "templates", "recorrido.html"), encoding="utf-8").read()
    esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)
    pasos = [p_ for _, p_ in pasos_de(d)]; colw = 170
    fila_et = "".join(f'<th colspan="{len(et.get("pasos") or [])}" class="etapa">{esc(et.get("nombre"))}</th>' for et in d.get("etapas") or [])
    def fila(clave, etiqueta, fn, clase=""):
        return f'<tr class="{clase}"><th scope="row">{esc(etiqueta)}</th>' + "".join(f"<td>{fn(p_)}</td>" for p_ in pasos) + "</tr>"
    def trat(p_):
        refs = lista(p_.get("refs")); tr = [r for r in refs if es_tratamiento(r, ids)]
        if not p_.get("dolor"): return esc(", ".join(refs)) or "—"
        return esc(", ".join(refs)) if tr else '<span class="alerta">' + esc(t("sin tratamiento", "untreated")) + "</span>" + (f" · {esc(', '.join(refs))}" if refs else "")
    filas = [f'<tr><th scope="row">{esc(t("Etapa", "Stage"))}</th>{fila_et}</tr>',
             fila("accion", t("Acción", "Action"), lambda p_: f"<b>{esc(p_.get('id'))}</b> {esc(p_.get('accion'))}"),
             fila("pc", t("Punto de contacto", "Touchpoint"), lambda p_: esc(" · ".join(x for x in (p_.get("punto_contacto"), p_.get("canal")) if x)) or "—"),
             f'<tr class="emocion"><th scope="row">{esc(t("Emoción (−2…+2)", "Emotion (−2…+2)"))}</th><td colspan="{len(pasos)}" class="sin-relleno">{svg_emocion(pasos, colw)}</td></tr>',
             fila("fuente", t("Fuente de la emoción", "Emotion source"), lambda p_: esc(p_.get("fuente_emocion")) or "—", "chica"),
             fila("dolor", t("Dolor", "Pain point"), lambda p_: (esc(p_.get("dolor")) + (f' <span class="causa">{esc(etq(p_.get("tipo_causa")))}</span>' if p_.get("tipo_causa") else "")) if p_.get("dolor") else "—", "dolor"),
             fila("oport", t("Oportunidad", "Opportunity"), lambda p_: (esc(p_.get("oportunidad")) + (f' <span class="kano">{esc(etq(p_.get("kano")))}</span>' if p_.get("kano") else "")) if p_.get("oportunidad") else "—", "oportunidad"),
             fila("trat", t("Tratamiento / refs", "Treatment / refs"), trat, "chica")]
    for c, et_ in (("frontstage", t("Frontstage (lo que la persona ve)", "Frontstage")), ("backstage", t("Backstage (lo que no ve)", "Backstage")), ("soporte", t("Procesos de soporte", "Support processes"))):
        if any(p_.get(c) for p_ in pasos): filas.append(fila(c, et_, lambda p_, c=c: esc(p_.get(c)) or "—", f"carril {c}"))
    if d.get("pendiente_alinear"):
        pa = d["pendiente_alinear"]
        filas.append(f'<tr class="carril"><th scope="row">{esc(t("Backstage por alinear", "Backstage to align"))}</th><td colspan="{len(pasos)}">{esc(" · ".join(pa.get("backstage", [])))} <span class="chica">({esc(pa.get("fuente"))})</span></td></tr>')
    cab = [(t("Persona", "Persona"), d.get("persona")), (t("Trabajo a resolver", "Job to be done"), d.get("trabajo")), (t("Disparador", "Trigger"), d.get("disparador")),
           (t("Éxito", "Success"), d.get("exito")), (t("Escenario", "Scenario"), d.get("escenario")), ("KPI", ", ".join(lista(d.get("kpi")) + lista(d.get("contrapesos")))),
           ("Refs", ", ".join(lista(d.get("refs")))), (t("Fuentes", "Sources"), "; ".join(lista(d.get("fuentes"))))]
    ficha = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v) or '—'}</dd></div>" for k, v in cab)
    variantes = "".join(f"<li>{esc(v.get('descripcion'))}</li>" for v in d.get("variantes") or [])
    cont = (f'<dl class="ficha">{ficha}</dl><div class="tabla"><table style="width:{140 + colw * len(pasos)}px"><colgroup><col style="width:140px">' +
            "".join(f'<col style="width:{colw}px">' for _ in pasos) + "</colgroup>" + "".join(filas) + "</table></div>" +
            (f"<h2>{esc(t('Variantes y casos límite', 'Variants and edge cases'))}</h2><ul>{variantes}</ul>" if variantes else ""))
    titulo = esc(d.get("titulo")) + ("" if estado == "aprobado" else " (BORRADOR)")
    rep = {"{{idioma}}": esc(IDIOMA), "{{titulo}}": titulo, "{{corte}}": esc(d.get("fecha_corte")), "{{estado}}": esc(estado), "{{proyecto}}": esc(e.get("proyecto")),
           "{{leyenda}}": esc(t("Línea continua: emoción actual · línea punteada: emoción esperada con las oportunidades · zona sombreada: emoción negativa. "
                               "Sin fuente, la emoción es un supuesto.", "Solid line: current emotion · dotted line: expected emotion · shaded: negative emotion.")),
           "{{contenido}}": cont}
    return re.sub(r"\{\{\w+\}\}", lambda m: rep.get(m.group(0), m.group(0)), plantilla)   # una sola pasada: los datos no se reinterpretan

def mmdc_png(codigo, salida):
    """PNG con mmdc si está instalado. Devuelve (ok, mensaje). mmdc puede terminar en 0 con un SVG de 'Syntax error':
    primero se renderiza a SVG y se busca el error."""
    if not shutil.which("mmdc"): return False, t("mmdc no está instalado: queda el bloque Mermaid (npm i -g @mermaid-js/mermaid-cli)", "mmdc not installed")
    with tempfile.TemporaryDirectory() as tmp:
        ent = os.path.join(tmp, "m.mmd"); open(ent, "w", encoding="utf-8").write(codigo)
        r = subprocess.run(["mmdc", "-i", ent, "-o", os.path.join(tmp, "m.svg"), "-b", "white"], capture_output=True, text=True, timeout=180)
        svg = open(os.path.join(tmp, "m.svg"), encoding="utf-8", errors="replace").read() if os.path.exists(os.path.join(tmp, "m.svg")) else ""
        if r.returncode != 0 or "Syntax error" in svg or not svg: return False, mmdc_error(r.stdout + r.stderr, svg)
        r = subprocess.run(["mmdc", "-i", ent, "-o", salida, "-b", "white", "-s", "2"], capture_output=True, text=True, timeout=180)
        return r.returncode == 0, salida if r.returncode == 0 else mmdc_error(r.stdout + r.stderr, "")

def mmdc_error(salida, svg):
    """Mensaje claro según la causa: el navegador headless que usa mmdc no arranca, error de sintaxis de Mermaid u otro."""
    if re.search(r"Failed to launch the browser|Could not find (Chrome|Chromium|browser)|socket path|ENAMETOOLONG", salida, re.I):
        n = len(tempfile.gettempdir())
        if n > 50:   # la ruta del socket de Chromium (TMPDIR + perfil temporal + nombre del socket) no puede superar ~107 caracteres
            return t(f"mmdc no pudo iniciar el navegador (Chromium headless): no se generó el PNG y el bloque Mermaid queda en el .md. "
                     f"Causa probable: TMPDIR tiene una ruta larga ({n} caracteres) y la ruta del socket de Chromium no puede superar ~107. "
                     f"Solución: correr con un TMPDIR corto, p. ej. TMPDIR=/tmp.",
                     f"mmdc could not launch the browser (headless Chromium): no PNG was written and the Mermaid block stays in the .md. "
                     f"Likely cause: TMPDIR is a long path ({n} characters) and Chromium's socket path cannot exceed ~107. "
                     f"Fix: run with a short TMPDIR, e.g. TMPDIR=/tmp.")
        return t("mmdc no pudo iniciar el navegador (Chromium headless): no se generó el PNG y el bloque Mermaid queda en el .md. "
                 "Solución: revisar la instalación de mermaid-cli y de su navegador, y que TMPDIR sea una ruta corta.",
                 "mmdc could not launch the browser (headless Chromium): no PNG was written and the Mermaid block stays in the .md. "
                 "Fix: check the mermaid-cli installation and its browser, and keep TMPDIR short.")
    if "Syntax error" in svg or re.search(r"Parse error|Syntax error|Lexical error|No diagram type detected", salida, re.I):
        return t("Mermaid no pudo dibujar el bloque (error de sintaxis)", "Mermaid syntax error")
    return t(f"mmdc terminó con error: {salida.strip()[-300:]}", f"mmdc failed: {salida.strip()[-300:]}")

# ------------------------------------------------------------------ tablero de mapas (vista gráfica para el tablero de avance)
MARCA_INI = re.compile(r"<!-- pm-mapas:inicio[^>]*-->")
MARCA_FIN = "<!-- pm-mapas:fin -->"
COLOR_DECISION = {"construir": "var(--accent, #1f4e79)", "comprar": "var(--green, #2e8b57)", "tercerizar": "var(--grey, #8a93a2)", "mercado": "var(--amber, #d08c00)"}
REF_TEXTO = {"riesgos": ("evento", "propietario"), "issues": ("titulo", "responsable"), "cambios": ("titulo", "solicitante"), "decisiones": ("decision", "decidido_por"),
             "supuestos": ("supuesto_o_restriccion", "responsable"), "lecciones": ("situacion", "responsable_seguimiento"), "calidad": ("producto", "responsable_productor"),
             "acciones": ("descripcion", "responsable")}

TIPO_REF = {"riesgos": ("riesgo", "risk"), "issues": ("issue", "issue"), "cambios": ("cambio", "change"), "decisiones": ("decisión", "decision"),
            "supuestos": ("supuesto", "assumption"), "lecciones": ("lección", "lesson"), "calidad": ("revisión de calidad", "quality review"), "acciones": ("acción", "action")}

def esc(v): return html.escape(str(v if v is not None else ""), quote=True)

def recortar(texto, n):
    texto = re.sub(r"\s+", " ", str(texto or "")).strip()
    return texto if len(texto) <= n else texto[:n - 1].rstrip() + "…"

def renglones(texto, n, maximo=2):
    """Parte un texto en hasta 'maximo' renglones de n caracteres (el último con «…» si no entra)."""
    palabras, out, linea = re.sub(r"\s+", " ", str(texto or "")).strip().split(" "), [], ""
    for w in palabras:
        if len(linea) + len(w) + (1 if linea else 0) <= n: linea = (linea + " " + w).strip()
        else:
            if linea: out.append(linea)
            linea = w
            if len(out) == maximo: break
    if linea and len(out) < maximo: out.append(linea)
    resto = " ".join(palabras)
    if len(" ".join(out)) < len(resto): out[-1] = recortar(out[-1] + " …", n)
    return [recortar(x, n) for x in out]

def tipo_espec(i, defecto):
    for pref_, es, en in (("AD-", "decisión de arquitectura", "architecture decision"), ("NFR-", "requisito no funcional", "non-functional requirement"),
                          ("FR-", "requisito funcional", "functional requirement"), ("UX-DR-", "requisito de diseño", "design requirement")):
        if i.startswith(pref_): return t(es, en)
    return defecto

def catalogo_refs(p):
    """id → {tipo, texto, estado, responsable} para los ids que citan los mapas: registros y especificación (vía la fachada)."""
    cat = {}
    for reg, (campo, resp) in REF_TEXTO.items():
        ruta = E.ruta_registro(p, reg)
        if not os.path.exists(ruta): continue
        for f in E.leer_csv(ruta)[1]:
            if f.get("id"): cat[f["id"]] = {"tipo": t(*TIPO_REF[reg]), "texto": f.get(campo, ""), "estado": f.get("estado", ""), "responsable": f.get(resp, "")}
    try:
        import especificacion as SP
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            idx, _ = SP.obtener(p)
        for col, tipo in (("requisitos", t("requisito", "requirement")), ("historias", t("historia", "story")), ("epicas", t("épica", "epic"))):
            for x in idx.get(col, []):
                if x.get("id") and x["id"] not in cat: cat[x["id"]] = {"tipo": tipo_espec(x["id"], tipo), "texto": x.get("titulo", ""), "estado": x.get("estado", ""), "responsable": ""}
    except BaseException:
        pass
    return cat

def enlace_ref(r, cat, tabla=None):
    """Un id citado: enlace a su fila en la tabla de vínculos (registros y tratamientos de dolores); otro id existente de la
    especificación, como texto; uno inexistente, marcado como roto."""
    if r in cat and (tabla is None or r in tabla): return f'<a class="ref" href="#mapa-ref-{esc(r)}">{esc(r)}</a>'
    if r in cat: return f'<span class="ref">{esc(r)}</span>'
    return f'<span class="ref roto" title="{esc(t("no existe en los registros ni en la especificación", "not found in registers or specification"))}">{esc(r)}</span>'

def svg_wardley(d, avisos, abiertos, pref):
    """Mapa de Wardley en SVG propio (sin mmdc): ejes, etapas en cuartos, enlaces, componentes coloreados por decisión,
    barra de inercia con su riesgo, movimientos y halo en los elementos con avisos MAP. Todo el texto escapado."""
    W, H, x0, x1, y0, y1 = 660, 440, 30, 648, 12, 388
    X = lambda e: x0 + (x1 - x0) * e
    Y = lambda v: y0 + (y1 - y0) * (1 - v)
    s = [f'<svg class="wardley" viewBox="0 0 {W} {H}" style="max-width:{int(W * 1.3)}px" role="img" aria-label="{esc(t("Mapa de Wardley", "Wardley map") + ": " + str(d.get("titulo") or ""))}">',
         f'<defs><marker id="{pref}-flecha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M0,0 L10,5 L0,10 z" class="punta"/></marker></defs>',
         f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" class="fondo"/>']
    for k in (1, 2, 3): s.append(f'<line x1="{X(k / 4):.1f}" x2="{X(k / 4):.1f}" y1="{y0}" y2="{y1}" class="divisoria"/>')
    s.append(f'<line x1="{x0}" x2="{x0}" y1="{y0}" y2="{y1}" class="eje"/><line x1="{x0}" x2="{x1}" y1="{y1}" y2="{y1}" class="eje"/>')
    for k, r in enumerate(ROTULOS.get(IDIOMA, ROTULOS["es"])): s.append(f'<text x="{X(k / 4 + 0.125):.1f}" y="{y1 + 17}" class="etapa-eje">{esc(r)}</text>')
    s.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{y1 + 38}" class="titulo-eje">{esc(t("Evolución →", "Evolution →"))}</text>')
    s.append(f'<text transform="translate(14 {(y0 + y1) / 2:.1f}) rotate(-90)" class="titulo-eje">{esc(t("Visibilidad para el usuario →", "Visibility to the user →"))}</text>')
    pos = {}
    for x in (d.get("anclas") or []) + (d.get("componentes") or []):
        if num(x.get("visibilidad")) is not None and num(x.get("evolucion")) is not None: pos[x["id"]] = (X(num(x["evolucion"])), Y(num(x["visibilidad"])))
    for l in d.get("enlaces") or []:
        if l.get("de") in pos and l.get("a") in pos:
            (ax, ay), (bx, by) = pos[l["de"]], pos[l["a"]]
            s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" class="enlace"/>')
    for m in d.get("movimientos") or []:
        c = m.get("componente"); h = num(m.get("hacia"))
        if c in pos and h is not None:
            cx, cy = pos[c]
            s.append(f'<line x1="{cx + 8:.1f}" y1="{cy:.1f}" x2="{X(h) - 8:.1f}" y2="{cy:.1f}" class="movimiento" marker-end="url(#{pref}-flecha)"/>')
            s.append(f'<circle cx="{X(h):.1f}" cy="{cy:.1f}" r="6" class="destino"><title>{esc(t("movimiento previsto", "expected movement"))}: {h:.2f}</title></circle>')
    for n_ in d.get("notas") or []:
        if num(n_.get("visibilidad")) is not None and num(n_.get("evolucion")) is not None:
            s.append(f'<text x="{X(num(n_["evolucion"])):.1f}" y="{Y(num(n_["visibilidad"])):.1f}" class="nota-mapa">{esc(recortar(n_.get("texto"), 70))}</text>')
    cajas = []   # rótulos ya ubicados (x0, y0, x1, y1): los siguientes buscan un lugar libre
    for a in d.get("anclas") or []:
        if a["id"] in pos:
            ax, ay = pos[a["id"]]; txt = recortar(a.get("nombre"), 40); w = len(txt) * 7.2
            cajas.append((ax - w / 2, ay - 9, ax + w / 2, ay + 6))
            s.append(f'<text x="{ax:.1f}" y="{ay + 4:.1f}" class="ancla"><title>{esc(a.get("id"))} {esc(a.get("nombre"))}</title>{esc(txt)}</text>')
    comps = [c for c in d.get("componentes") or [] if c["id"] in pos]
    puntos = [pos[c["id"]] for c in comps]
    for c in comps:
        cx, cy = pos[c["id"]]; dec = c.get("decision") or ""
        cods = sorted({x["codigo"] for x in avisos if x["elemento"] == c["id"]})
        if cods: s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" class="halo"><title>{esc(", ".join(cods))}</title></circle>')
        relleno = f' style="fill:{COLOR_DECISION[dec]}"' if dec in COLOR_DECISION else ""
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" class="comp{" sin-decision" if not relleno else ""}"{relleno}><title>{esc(c["id"])} {esc(c.get("nombre"))}'
                 f' · {esc(dec or t("sin decisión", "no decision"))}</title></circle>')
        if c.get("inercia"):
            s.append(f'<rect x="{cx + 13:.1f}" y="{cy - 9:.1f}" width="4" height="18" class="inercia"><title>{esc(t("inercia", "inertia"))}</title></rect>')
    def choca(caja):
        x0_, y0_, x1_, y1_ = caja
        if x0_ < x0 + 2 or x1_ > W - 2 or y0_ < 0 or y1_ > y1 - 2: return True
        if any(not (x1_ < b[0] or x0_ > b[2] or y1_ < b[1] or y0_ > b[3]) for b in cajas): return True
        return any(x0_ - 7 < px < x1_ + 7 and y0_ - 7 < py < y1_ + 7 for px, py in puntos)
    for c in comps:
        cx, cy = pos[c["id"]]; dec = c.get("decision") or ""
        dx = 22 if c.get("inercia") else 15
        nombre = recortar(c.get("nombre"), 34)
        partes_, largo = ([esc(dec)] if dec else []), len(dec)
        if c.get("inercia"):
            rs = [r for r in lista(c.get("refs")) if r in abiertos]
            etiqueta = t("inercia → ", "inertia → ") + ", ".join(rs) if rs else t("inercia sin riesgo", "inertia without risk")
            partes_.append(f'<tspan class="{"ok" if rs else "falta"}">{esc(etiqueta)}</tspan>'); largo += len(etiqueta) + 3
        w = max(len(nombre) * 6.7, largo * 5.8); alto = 17 if partes_ else 0
        pref_izq = num(c.get("evolucion")) > 0.70
        opciones = []
        for izq in (pref_izq, not pref_izq):
            for dy in (0, 16, -16, 30, -30):
                opciones.append((izq, dy))
        elegido = None
        for izq, dy in opciones:
            tx = cx - dx if izq else cx + dx
            caja = (tx - w if izq else tx, cy - 4 + dy - 11, tx if izq else tx + w, cy - 4 + dy + alto + 2)
            if not choca(caja): elegido = (izq, dy, tx, caja); break
        if not elegido:
            tx = cx - dx if pref_izq else cx + dx
            elegido = (pref_izq, 0, tx, (tx - w if pref_izq else tx, cy - 15, tx if pref_izq else tx + w, cy + alto - 2))
        izq, dy, tx, caja = elegido; cajas.append(caja); ancla = "end" if izq else "start"
        s.append(f'<text x="{tx:.1f}" y="{cy - 4 + dy:.1f}" class="nombre" text-anchor="{ancla}">{esc(nombre)}</text>')
        if partes_: s.append(f'<text x="{tx:.1f}" y="{cy + 13 + dy:.1f}" class="detalle" text-anchor="{ancla}">{" · ".join(partes_)}</text>')
    return "".join(s) + "</svg>"

def svg_recorrido(d, ids, avisos):
    """Curva de emoción del recorrido en SVG: bandas por etapa, emoción actual y esperada, zona negativa, paso y acción,
    y debajo de cada dolor su tratamiento (o «sin tratamiento»). Todo el texto escapado."""
    pasos = [p_ for _, p_ in pasos_de(d)]; n = max(1, len(pasos))
    colw = max(84, 600 // n); x0 = 34; W = x0 + colw * n + 6; H = 262
    X = lambda i: x0 + colw * i + colw / 2
    Y = lambda v: 44 + (2 - v) * 28
    s = [f'<svg class="recorrido" viewBox="0 0 {W} {H}" style="max-width:{int(W * 1.3)}px" role="img" aria-label="{esc(t("Curva de emoción del recorrido", "Journey emotion curve") + ": " + str(d.get("titulo") or ""))}">']
    i = 0
    for et in d.get("etapas") or []:
        k = len(et.get("pasos") or [])
        if not k: continue
        s.append(f'<rect x="{x0 + colw * i + 1}" y="2" width="{colw * k - 2}" height="24" rx="3" class="banda"/>'
                 f'<text x="{x0 + colw * (i + k / 2):.1f}" y="18" class="banda-txt">{esc(recortar(et.get("nombre"), int(colw * k / 7.5)))}</text>')
        i += k
    s.append(f'<rect x="{x0}" y="{Y(0):.1f}" width="{colw * n}" height="{Y(-2) - Y(0) + 10:.1f}" class="zona"/>')
    for v in (2, 1, 0, -1, -2):
        s.append(f'<line x1="{x0}" x2="{x0 + colw * n}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="{"cero" if v == 0 else "guia"}"/>'
                 f'<text x="{x0 - 6}" y="{Y(v) + 4:.1f}" class="escala">{emo(v)}</text>')
    obj = [(k, p_.get("emocion_objetivo")) for k, p_ in enumerate(pasos) if isinstance(p_.get("emocion_objetivo"), int)]
    if obj: s.append('<polyline class="objetivo" points="' + " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in obj) + '"/>')
    for k, v in obj: s.append(f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="4" class="meta-obj"><title>{esc(t("emoción esperada", "expected emotion"))}: {emo(v)}</title></circle>')
    val = [(k, p_["emocion"]) for k, p_ in enumerate(pasos) if isinstance(p_.get("emocion"), int) and not isinstance(p_.get("emocion"), bool)]
    if val: s.append('<polyline class="linea" points="' + " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in val) + '"/>')
    for k, v in val:
        s.append(f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="6" class="{"neg" if v < 0 else ("pos" if v > 0 else "neu")}"><title>{esc(pasos[k].get("id"))} · {esc(pasos[k].get("accion"))}: {emo(v)}</title></circle>')
    car = max(8, int(colw / 6.6))
    for k, p_ in enumerate(pasos):
        cods = sorted({x["codigo"] for x in avisos if x["elemento"] == p_.get("id")})
        s.append(f'<text x="{X(k):.1f}" y="{Y(-2) + 30:.1f}" class="paso-id">{esc(p_.get("id"))}' + (f' <tspan class="falta">⚠</tspan>' if cods else "") + "</text>")
        for j, r in enumerate(renglones(p_.get("accion"), car)):
            s.append(f'<text x="{X(k):.1f}" y="{Y(-2) + 45 + 13 * j:.1f}" class="paso-txt">{esc(r)}</text>')
        if str(p_.get("dolor") or "").strip():
            tr = [r for r in lista(p_.get("refs")) if es_tratamiento(r, ids)]
            s.append(f'<text x="{X(k):.1f}" y="{Y(-2) + 82:.1f}" class="dolor-txt">▲ {esc(t("dolor", "pain"))}</text>')
            s.append(f'<text x="{X(k):.1f}" y="{Y(-2) + 96:.1f}" class="{"ok" if tr else "falta"}">{esc(recortar(", ".join(tr), car)) if tr else esc(t("sin tratamiento", "untreated"))}</text>')
    return "".join(s) + "</svg>"

CSS_MAPAS = """
.pm-mapas .grilla-mapas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(600px, 100%), 1fr)); gap: 14px; align-items: start; }
.pm-mapas article { background: var(--panel, #fff); border: 1px solid var(--line, #d9dee6); border-radius: 8px; padding: 10px 12px; min-width: 0; }
.pm-mapas h3 { font-size: 14px; margin: 0 0 2px; color: var(--ink, #1d2430); text-transform: none; letter-spacing: 0; }
.pm-mapas .sub { color: var(--muted, #5d6675); font-size: 12px; margin: 0 0 6px; }
.pm-mapas .lienzo { overflow-x: auto; }
.pm-mapas .lienzo svg { min-width: 600px; width: 100%; height: auto; display: block; margin: 0 auto; background: var(--panel, #fff); border: 0; }
.pm-mapas svg text { font-size: 11px; fill: var(--muted, #5d6675); }
.pm-mapas svg .fondo { fill: var(--panel, #fff); }
.pm-mapas svg .eje { stroke: var(--ink, #1d2430); stroke-width: 1.2; }
.pm-mapas svg .divisoria { stroke: var(--line, #d9dee6); stroke-dasharray: 5 4; }
.pm-mapas svg .etapa-eje, .pm-mapas svg .titulo-eje, .pm-mapas svg .banda-txt, .pm-mapas svg .paso-id, .pm-mapas svg .paso-txt,
.pm-mapas svg .dolor-txt, .pm-mapas svg .ok, .pm-mapas svg .falta { text-anchor: middle; }
.pm-mapas svg .titulo-eje { font-weight: 600; fill: var(--ink, #1d2430); }
.pm-mapas svg .enlace { stroke: var(--muted, #5d6675); stroke-width: 1.1; }
.pm-mapas svg .movimiento { stroke: var(--red, #c0392b); stroke-width: 1.4; stroke-dasharray: 6 4; }
.pm-mapas svg .punta { fill: var(--red, #c0392b); }
.pm-mapas svg .destino { fill: none; stroke: var(--red, #c0392b); stroke-width: 1.4; stroke-dasharray: 3 2; }
.pm-mapas svg .comp { stroke: var(--ink, #1d2430); stroke-width: 1.4; }
.pm-mapas svg .sin-decision { fill: var(--panel, #fff); }
.pm-mapas svg .halo { fill: none; stroke: var(--amber, #d08c00); stroke-width: 2.5; stroke-dasharray: 4 3; }
.pm-mapas svg .inercia { fill: var(--ink, #1d2430); }
.pm-mapas svg .nombre { font-size: 12px; fill: var(--ink, #1d2430); }
.pm-mapas svg .nombre, .pm-mapas svg .detalle, .pm-mapas svg .ancla, .pm-mapas svg .nota-mapa { paint-order: stroke; stroke: var(--panel, #fff); stroke-width: 3px; stroke-linejoin: round; }
.pm-mapas svg circle.meta-obj { fill: var(--panel, #fff); stroke: var(--accent, #1f4e79); stroke-width: 1.8; }
.pm-mapas svg .ancla { font-size: 12.5px; font-weight: 700; fill: var(--ink, #1d2430); text-anchor: middle; }
.pm-mapas svg .nota-mapa { font-style: italic; text-anchor: middle; }
.pm-mapas svg .detalle { font-size: 10.5px; }
.pm-mapas svg .ok, .pm-mapas svg tspan.ok { fill: var(--green, #2e8b57); font-weight: 600; }
.pm-mapas svg .falta, .pm-mapas svg tspan.falta { fill: var(--red, #c0392b); font-weight: 700; }
.pm-mapas svg .banda { fill: var(--accent, #1f4e79); }
.pm-mapas svg .banda-txt { fill: var(--panel, #fff); font-weight: 600; font-size: 11.5px; }
.pm-mapas svg .zona { fill: color-mix(in srgb, var(--red, #c0392b) 12%, var(--panel, #fff)); }
.pm-mapas svg .guia { stroke: var(--line, #d9dee6); }
.pm-mapas svg .cero { stroke: var(--muted, #5d6675); stroke-width: 1.2; }
.pm-mapas svg .escala { text-anchor: end; font-size: 10px; }
.pm-mapas svg .linea { fill: none; stroke: var(--ink, #1d2430); stroke-width: 2.2; }
.pm-mapas svg .objetivo { fill: none; stroke: var(--accent, #1f4e79); stroke-width: 1.8; stroke-dasharray: 6 5; }
.pm-mapas svg circle.neg { fill: var(--red, #c0392b); stroke: var(--panel, #fff); stroke-width: 2; }
.pm-mapas svg circle.pos { fill: var(--green, #2e8b57); stroke: var(--panel, #fff); stroke-width: 2; }
.pm-mapas svg circle.neu { fill: var(--grey, #8a93a2); stroke: var(--panel, #fff); stroke-width: 2; }
.pm-mapas svg .paso-id { font-weight: 700; fill: var(--ink, #1d2430); }
.pm-mapas svg .paso-txt { font-size: 10.5px; }
.pm-mapas svg .dolor-txt { fill: var(--red, #c0392b); font-weight: 600; }
.pm-mapas .leyenda-mapa { font-size: 12px; color: var(--muted, #5d6675); margin: 6px 0; }
.pm-mapas .leyenda-mapa span { display: inline-block; margin-right: 12px; }
.pm-mapas .leyenda-mapa i { display: inline-block; width: 11px; height: 11px; border-radius: 50%; vertical-align: middle; margin-right: 4px; border: 1px solid var(--ink, #1d2430); }
.pm-mapas .avisos-map { margin: 4px 0 10px; padding: 8px 12px; border-left: 4px solid var(--amber, #d08c00); border-radius: 4px;
  background: color-mix(in srgb, var(--amber, #d08c00) 10%, var(--panel, #fff)); font-size: 13px; }
.pm-mapas .avisos-map.sin { border-left-color: var(--green, #2e8b57); background: color-mix(in srgb, var(--green, #2e8b57) 10%, var(--panel, #fff)); }
.pm-mapas .avisos-map ul { margin: 4px 0 0; padding-left: 18px; }
.pm-mapas .wrap { overflow-x: auto; margin-top: 8px; }
.pm-mapas > h3 { margin-top: 16px; }
.pm-mapas table.vinculos td:first-child { white-space: nowrap; }
.pm-mapas table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.pm-mapas th, .pm-mapas td { text-align: left; padding: 5px 7px; border-bottom: 1px solid var(--line, #d9dee6); vertical-align: top; overflow-wrap: break-word; }
.pm-mapas a.ref { color: var(--accent, #1f4e79); font-weight: 600; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 2px; }
.pm-mapas .ref.roto { color: var(--red, #c0392b); text-decoration: line-through; }
.pm-mapas .falta { color: var(--red, #c0392b); font-weight: 600; }
.pm-mapas tr:target td { background: color-mix(in srgb, var(--accent, #1f4e79) 14%, var(--panel, #fff)); }
@media print { .pm-mapas article { break-inside: avoid; } .pm-mapas .lienzo svg { min-width: 0; } }
"""

def fragmento_mapas(p, slugs=None):
    """Sección «Mapas estratégicos» (HTML escapado, sin scripts ni recursos externos) y su resumen. Sin mapas válidos: ('', resumen)."""
    archivos = sorted(glob.glob(os.path.join(mapas_dir(p), "wardley-*.json"))) + sorted(glob.glob(os.path.join(mapas_dir(p), "recorrido-*.json")))
    if slugs: archivos = [a for a in archivos if re.sub(r"^(wardley|recorrido)-", "", os.path.basename(a)[:-5]) in slugs or os.path.basename(a)[:-5] in slugs]
    detalle = []; controles(p, detalle)
    ids, abiertos, _ = ids_conocidos(p); cat = catalogo_refs(p)
    riesgos_abiertos = abiertos.get("riesgos", set())
    mapas, omitidos = [], []
    for ruta in archivos:
        nombre = os.path.basename(ruta)
        try: d = json.load(open(ruta, encoding="utf-8"))
        except (OSError, ValueError): omitidos.append(nombre); continue
        es_w = nombre.startswith("wardley-")
        if (validar_wardley(d) if es_w else validar_recorrido(d))[0]: omitidos.append(nombre); continue
        mapas.append((nombre, es_w, d))
    res = {"mapas": [m[0] for m in mapas], "omitidos": omitidos, "avisos": [x for x in detalle if x["archivo"] in {m[0] for m in mapas}], "vinculos": []}
    if not mapas: return "", res
    citados = []   # vínculos de gestión: ids de registros (riesgos, decisiones, supuestos…) y tratamientos de dolores
    for nombre, es_w, d in mapas:
        for x in (d.get("componentes") or []) if es_w else [p_ for _, p_ in pasos_de(d)]:
            dolor = not es_w and str(x.get("dolor") or "").strip()
            citados += [r for r in lista(x.get("refs")) if r in cat and (REF_REG.match(r) or (dolor and es_tratamiento(r, ids)))]
    tabla_ids = set(citados)
    arts = []
    for k, (nombre, es_w, d) in enumerate(mapas, 1):
        av = [x for x in detalle if x["archivo"] == nombre]
        estado = leer_fm(os.path.join(visuales_dir(p), nombre[:-5] + ".md")).get("estado") or "borrador"   # la aprobación vive en la vista registrada
        cab = (f'<h3>{esc(t("Mapa de Wardley", "Wardley map") if es_w else t("Recorrido del cliente", "Customer journey"))} · {esc(d.get("titulo"))}'
               + ("" if estado == "aprobado" else f' <span class="borrador">{esc(t("BORRADOR", "DRAFT"))}</span>') + "</h3>")
        if es_w:
            sub = f'{esc(t("Pregunta", "Question"))}: {esc(d.get("pregunta_estrategica"))} · {esc(t("corte", "cut-off"))} {esc(d.get("fecha_corte"))} · {esc(nombre)}'
            grafico = svg_wardley(d, av, riesgos_abiertos, f"pmm{k}")
            ley = "".join(f'<span><i style="background:{COLOR_DECISION[x]}"></i>{esc(x)}</span>' for x in COLOR_DECISION) + \
                  f'<span><i style="background:var(--panel, #fff)"></i>{esc(t("sin decisión", "no decision"))}</span><span>▮ {esc(t("inercia", "inertia"))}</span>' + \
                  f'<span>- - → {esc(t("movimiento previsto", "expected movement"))}</span><span>◌ {esc(t("aviso MAP", "MAP warning"))}</span>'
            filas = []
            for c in d.get("componentes") or []:
                refs = lista(c.get("refs"))
                ev = num(c.get("evolucion")); et = c.get("etapa") or etapa_de(ev)
                ine = ("—" if not c.get("inercia") else (", ".join(enlace_ref(r, cat, tabla_ids) for r in refs if r in riesgos_abiertos) or f'<span class="falta">{esc(t("sin riesgo abierto", "no open risk"))}</span>'))
                cods = ", ".join(sorted({x["codigo"] for x in av if x["elemento"] == c.get("id")}))
                filas.append(f'<tr><td><b>{esc(c.get("id"))}</b> {esc(c.get("nombre"))}</td><td>{esc(et)} ({ev:.2f})</td><td>{esc(c.get("decision") or "—")}</td>'
                             f'<td>{ine}</td><td>{", ".join(enlace_ref(r, cat, tabla_ids) for r in refs) or "—"}</td><td class="falta">{esc(cods)}</td></tr>')
            tabla = (f'<div class="wrap"><table><thead><tr><th>{esc(t("Componente", "Component"))}</th><th>{esc(t("Etapa (evolución)", "Stage (evolution)"))}</th>'
                     f'<th>{esc(t("Decisión", "Decision"))}</th><th>{esc(t("Inercia → riesgo", "Inertia → risk"))}</th><th>Refs</th><th>MAP</th></tr></thead><tbody>{"".join(filas)}</tbody></table></div>')
        else:
            sub = f'{esc(t("Persona", "Persona"))}: {esc(recortar(d.get("persona"), 120))} · {esc(t("corte", "cut-off"))} {esc(d.get("fecha_corte"))} · {esc(nombre)}'
            grafico = svg_recorrido(d, ids, av)
            ley = (f'<span>— {esc(t("emoción actual", "current emotion"))}</span>' +
                   (f'<span>- - {esc(t("emoción esperada", "expected emotion"))}</span>' if any(p_.get("emocion_objetivo") is not None for _, p_ in pasos_de(d)) else "") +
                   f'<span>▲ {esc(t("dolor y su tratamiento", "pain point and its treatment"))}</span><span>⚠ {esc(t("aviso MAP", "MAP warning"))}</span>')
            filas = []
            for et, p_ in pasos_de(d):
                refs = lista(p_.get("refs"))
                if not str(p_.get("dolor") or "").strip(): continue
                tr = [r for r in refs if es_tratamiento(r, ids)]
                cods = ", ".join(sorted({x["codigo"] for x in av if x["elemento"] == p_.get("id")}))
                trat = ", ".join(enlace_ref(r, cat, tabla_ids) for r in tr) if tr else '<span class="falta">' + esc(t("sin tratamiento", "untreated")) + "</span>"
                trat += "".join(" · " + enlace_ref(r, cat) for r in refs if r not in cat)
                filas.append(f'<tr><td><b>{esc(p_.get("id"))}</b> {esc(p_.get("accion"))}</td><td>{esc(emo(p_.get("emocion")))}</td>'
                             f'<td>{esc(p_.get("dolor"))}' + (f' ({esc(etq(p_.get("tipo_causa")))})' if p_.get("tipo_causa") else "") + "</td>"
                             f'<td>{trat}</td><td class="falta">{esc(cods)}</td></tr>')
            tabla = (f'<div class="wrap"><table><thead><tr><th>{esc(t("Paso", "Step"))}</th><th>{esc(t("Emoción", "Emotion"))}</th><th>{esc(t("Dolor (causa)", "Pain (cause)"))}</th>'
                     f'<th>{esc(t("Tratamiento", "Treatment"))}</th><th>MAP</th></tr></thead><tbody>{"".join(filas)}</tbody></table></div>') if filas else \
                    f'<p class="sub">{esc(t("Sin dolores registrados en el recorrido.", "No pain points in the journey."))}</p>'
        arts.append(f'<article id="mapa-{esc(nombre[:-5])}">{cab}<p class="sub">{sub}</p><div class="lienzo">{grafico}</div><p class="leyenda-mapa">{ley}</p>{tabla}</article>')
    vist = []
    for r in citados:
        if r not in vist: vist.append(r)
    filas_v = []
    for r in vist:
        x = cat.get(r)
        if not x: continue
        res["vinculos"].append(r)
        filas_v.append(f'<tr id="mapa-ref-{esc(r)}"><td><b>{esc(r)}</b></td><td>{esc(x["tipo"])}</td><td>{esc(recortar(x["texto"], 160))}</td><td>{esc(x["estado"] or "—")}</td><td>{esc(x["responsable"] or "—")}</td></tr>')
    avisos = res["avisos"]
    caja = (f'<div class="avisos-map{" sin" if not avisos else ""}"><strong>{esc(t("Avisos MAP vigentes", "Current MAP warnings"))}: {len(avisos)}</strong>' +
            ("<ul>" + "".join(f'<li><b>{esc(x["codigo"])}</b> {esc(x["mensaje"])}</li>' for x in avisos) + "</ul>" if avisos else
             " · " + esc(t("cada dolor tiene tratamiento, cada inercia su riesgo y cada posición su evidencia", "every pain point is treated, every inertia has a risk and every position its evidence"))) + "</div>")
    if omitidos: caja += f'<p class="sub">{esc(t("Sin dibujar por errores de validación (corregir con «validar»)", "Not drawn: validation errors"))}: {esc(", ".join(omitidos))}</p>'
    vinc = (f'<h3>{esc(t("Vínculos citados", "Cited links"))}</h3><div class="wrap"><table class="vinculos"><thead><tr><th>Id</th><th>{esc(t("Tipo", "Type"))}</th><th>{esc(t("Descripción", "Description"))}</th>'
            f'<th>{esc(t("Estado", "Status"))}</th><th>{esc(t("Responsable", "Owner"))}</th></tr></thead><tbody>{"".join(filas_v)}</tbody></table></div>') if filas_v else ""
    frag = (f'<section id="s-mapas" class="pm-mapas" aria-labelledby="t-mapas"><style>{CSS_MAPAS}</style>'
            f'<h2 id="t-mapas">Mapas estratégicos / Strategic maps</h2>'
            f'<p class="nota">{esc(t("Generado con mapas.py tablero desde 02-planificacion/mapas/ (fuente: los JSON de cada mapa; no editar a mano). Los ids enlazan a la tabla de vínculos.", "Generated by mapas.py tablero from 02-planificacion/mapas/; do not edit by hand. Ids link to the cited-links table."))}</p>'
            f'{caja}<div class="grilla-mapas">{"".join(arts)}</div>{vinc}</section>')
    return frag, res

def cmd_tablero(a, e):
    p = a.proyecto; slugs = {x.strip() for x in lista(a.mapas)} if a.mapas else None
    frag, res = fragmento_mapas(p, slugs)
    escritos = []
    if a.insertar:
        ruta = a.insertar if os.path.isabs(a.insertar) or os.path.exists(a.insertar) else os.path.join(p, a.insertar)
        if not os.path.exists(ruta): sys.exit(t(f"No existe {a.insertar}", f"{a.insertar} not found"))
        txt = open(ruta, encoding="utf-8").read(); m = MARCA_INI.search(txt); fin = txt.find(MARCA_FIN, m.end()) if m else -1
        if not m or fin < 0:
            sys.exit(t(f"{a.insertar}: faltan los marcadores <!-- pm-mapas:inicio --> y <!-- pm-mapas:fin -->; regenerar el tablero desde pm-visuales/templates/tablero-avance.html",
                       f"{a.insertar}: missing the pm-mapas markers; rebuild the dashboard from pm-visuales/templates/tablero-avance.html"))
        open(ruta, "w", encoding="utf-8").write(txt[:m.end()] + ("\n" + frag + "\n" if frag else "") + txt[fin:])
        escritos.append(ruta)
    if a.salida or not a.insertar:
        salida = a.salida or os.path.join(visuales_dir(p), "tablero-mapas.html")
        plantilla = open(os.path.join(SK, "pm-mapas-estrategicos", "templates", "tablero-mapas.html"), encoding="utf-8").read()
        cortes = sorted(d_ for d_ in (cargar(os.path.join(mapas_dir(p), m)).get("fecha_corte") for m in res["mapas"]) if d_)
        rep = {"{{idioma}}": esc(IDIOMA), "{{proyecto}}": esc(e.get("proyecto")), "{{corte}}": esc(cortes[-1] if cortes else "—"),
               "{{fuentes}}": esc(", ".join(res["mapas"]) or "—"),
               "{{contenido}}": frag or f'<p class="vacio">{esc(t("Sin mapas válidos en 02-planificacion/mapas/: crear uno con «wardley semilla» o «recorrido semilla».", "No valid maps in 02-planificacion/mapas/."))}</p>'}
        os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
        open(salida, "w", encoding="utf-8").write(re.sub(r"\{\{\w+\}\}", lambda m_: rep.get(m_.group(0), m_.group(0)), plantilla))
        escritos.append(salida)
    res["archivos"] = [os.path.relpath(x, p) if os.path.abspath(x).startswith(os.path.abspath(p)) else x for x in escritos]
    if a.json: print(json.dumps(res, ensure_ascii=False, indent=2)); return
    print(t(f"Tablero de mapas: {len(res['mapas'])} mapa(s) dibujado(s) ({', '.join(res['mapas']) or '—'}) · {len(res['avisos'])} aviso(s) MAP · {len(res['vinculos'])} vínculo(s) citado(s)",
            f"Maps board: {len(res['mapas'])} map(s) drawn ({', '.join(res['mapas']) or '—'}) · {len(res['avisos'])} MAP warning(s) · {len(res['vinculos'])} cited link(s)"))
    if res["omitidos"]: print("AVISO", t(f"sin dibujar por errores de validación: {', '.join(res['omitidos'])}", f"not drawn (validation errors): {', '.join(res['omitidos'])}"))
    if a.insertar and not frag: print(t("Sin mapas válidos: la sección de mapas del tablero queda vacía (omitida).", "No valid maps: the dashboard maps section is left empty (omitted)."))
    print(t(f"Escrito: {', '.join(res['archivos'])}", f"Written: {', '.join(res['archivos'])}"))

# ------------------------------------------------------------------ comandos
def cmd_semilla(a, e, tipo):
    d, desde = semilla_wardley(a, e) if tipo == "wardley" else semilla_recorrido(a, e)
    slug = a.slug or (slugify(a.uj) if tipo == "recorrido" and a.uj else slugify(d.get("titulo")))
    ruta = os.path.join(mapas_dir(a.proyecto), f"{tipo}-{slug}.json")
    if os.path.exists(ruta) and not a.forzar: sys.exit(t(f"Ya existe {os.path.relpath(ruta, a.proyecto)} (usar --forzar para reemplazarlo)", f"{ruta} exists (use --forzar)"))
    guardar(ruta, d)
    n = len(d.get("componentes", [])) if tipo == "wardley" else len(pasos_de(d))
    res = {"archivo": os.path.relpath(ruta, a.proyecto), "desde": desde, "elementos": n, "anclas": len(d.get("anclas", [])), "enlaces": len(d.get("enlaces", []))}
    if a.json: print(json.dumps(res, ensure_ascii=False, indent=2)); return
    if tipo == "wardley":
        print(t(f"Semilla {res['archivo']} desde {desde}: {res['anclas']} ancla(s), {n} componente(s), {res['enlaces']} enlace(s); posiciones y evidencia [por confirmar].",
                f"Seed {res['archivo']} from {desde}: {res['anclas']} anchor(s), {n} component(s), {res['enlaces']} link(s); positions and evidence to be confirmed."))
    else:
        print(t(f"Semilla {res['archivo']} desde {desde}: {len(d['etapas'])} etapa(s), {n} paso(s); emociones y fuentes [por confirmar]" + (f" · KPI {', '.join(d['kpi'])}" if d.get("kpi") else ""),
                f"Seed {res['archivo']} from {desde}: {len(d['etapas'])} stage(s), {n} step(s)"))
    print(t("Siguiente: completar con evidencia, 'validar' y 'render'. El modelo propone; la persona confirma.", "Next: complete with evidence, validate and render."))

def informe_validacion(ruta, d, tipo, como_json):
    err, av = validar_wardley(d) if tipo == "wardley" else validar_recorrido(d)
    if como_json: print(json.dumps({"archivo": ruta, "errores": err, "avisos": av, "valido": not err}, ensure_ascii=False, indent=2))
    else:
        for x in err: print("ERROR", x)
        for x in av: print("AVISO", x)
        print(t(f"{os.path.basename(ruta)}: {len(err)} error(es) · {len(av)} aviso(s)", f"{os.path.basename(ruta)}: {len(err)} error(s) · {len(av)} warning(s)"))
    return err

def cmd_render(a, e, tipo):
    ruta = resolver(a.proyecto, tipo, a.mapa); d = cargar(ruta)
    err, av = validar_wardley(d) if tipo == "wardley" else validar_recorrido(d)
    if err:
        for x in err: print("ERROR", x)
        sys.exit(t(f"{len(err)} error(es): no se genera la vista (corregir y volver a 'validar')", f"{len(err)} error(s): nothing rendered"))
    slug = re.sub(rf"^{tipo}-", "", os.path.basename(ruta)[:-5]); d["_slug"] = slug
    vis = visuales_dir(a.proyecto); os.makedirs(vis, exist_ok=True)
    base = os.path.join(vis, f"{tipo}-{slug}"); fuente = os.path.relpath(ruta, a.proyecto)
    escritos = []
    if tipo == "wardley":
        texto = md_wardley(d, e, base + ".md", fuente); open(base + ".md", "w", encoding="utf-8").write(texto); escritos.append(base + ".md")
        open(base + ".owm", "w", encoding="utf-8").write(owm(d)); escritos.append(base + ".owm")
        codigo = mermaid_wardley({**d, "estado": leer_fm(base + ".md").get("estado", "borrador")})
    else:
        ids, _, _ = ids_conocidos(a.proyecto)
        texto = md_recorrido(d, e, base + ".md", fuente, ids); open(base + ".md", "w", encoding="utf-8").write(texto); escritos.append(base + ".md")
        estado = leer_fm(base + ".md").get("estado", "borrador")
        open(base + ".html", "w", encoding="utf-8").write(html_recorrido(d, e, ids, estado)); escritos.append(base + ".html")
        codigo = mermaid_journey({**d, "estado": estado})
    png = None
    if a.png != "no":
        ok, msg = mmdc_png(codigo, base + ".png")
        if ok: escritos.append(base + ".png"); png = True
        elif a.png == "si": sys.exit(msg)
        else: print("AVISO", msg); png = False
    clave = f"mapa-{tipo}-{slug}"
    res = {"vistas": [os.path.relpath(x, a.proyecto) for x in escritos], "avisos": av, "png": png, "artefacto": clave}
    if a.json: print(json.dumps(res, ensure_ascii=False, indent=2)); return
    for x in av: print("AVISO", x)
    print(t(f"Vistas: {', '.join(res['vistas'])}", f"Views: {', '.join(res['vistas'])}"))
    print(t(f"Registrar (si es nuevo): estado.py --proyecto {a.proyecto} artefacto {clave} --ruta {os.path.relpath(base + '.md', a.proyecto)} --estado borrador",
            f"Register (if new): estado.py --proyecto {a.proyecto} artefacto {clave} --ruta {os.path.relpath(base + '.md', a.proyecto)} --estado borrador"))

def cmd_candidatos(a, e):
    ruta = resolver(a.proyecto, "recorrido", a.mapa); d = cargar(ruta); ids, _, _ = ids_conocidos(a.proyecto)
    rel = os.path.relpath(ruta, a.proyecto); out = []
    for et, p_ in pasos_de(d):
        if not str(p_.get("dolor") or "").strip(): continue
        if any(es_tratamiento(r, ids) for r in lista(p_.get("refs"))): continue
        causa = p_.get("tipo_causa") or ""
        clase = "riesgo" if causa == "dependencia-externa" else ("supuesto" if causa == "propuesta-valor" else "requisito")
        texto = {"riesgo": t(f"Causa: {p_['dolor']} → evento: la persona abandona o vuelve al canal anterior en «{p_.get('accion')}» → efecto: el beneficio previsto no se realiza",
                             f"Cause: {p_['dolor']} → event: the person drops out → effect: expected benefit not realised"),
                 "supuesto": t(f"Si se resuelve «{p_['dolor']}», la persona usa el nuevo canal en «{p_.get('accion')}»", f"If «{p_['dolor']}» is solved, the person adopts the new channel"),
                 "requisito": t(f"{p_.get('oportunidad') or 'Resolver: ' + p_['dolor']}", f"{p_.get('oportunidad') or 'Solve: ' + p_['dolor']}")}[clase]
        cmd = {"riesgo": "registro.py agregar riesgos --campo causa=… --campo evento=… --campo efecto=…",
               "supuesto": "registro.py agregar supuestos --campo supuesto_o_restriccion=… --campo criticidad=… --campo certeza=…",
               "requisito": t("pm-planificacion-por-productos (requisitos.md) o, con BMAD, traspaso al equipo de producto (bmad.py handoff)", "requirements owner")}[clase]
        out.append({"paso": p_["id"], "etapa": et.get("nombre"), "dolor": p_["dolor"], "emocion": p_.get("emocion"), "fuente": p_.get("fuente_emocion"),
                    "clase": clase, "propuesta": texto, "cita": f"{rel}#{p_['id']}", "como_registrar": cmd, "luego": f"mapas.py --proyecto {a.proyecto} vincular {rel} {p_['id']} --refs <id>"})
    if a.salida:
        L = [f"# {t('Candidatos desde el recorrido', 'Candidates from the journey')} · {celda(d.get('titulo'))} (BORRADOR)", "",
             t("Son candidatos: se evalúan con la persona responsable antes de registrarlos.", "Candidates: assess before registering."), "",
             f"| {t('Paso', 'Step')} | {t('Dolor', 'Pain')} | {t('Clase', 'Class')} | {t('Propuesta', 'Proposal')} | {t('Cita', 'Source')} |", "|---|---|---|---|---|"]
        L += [f"| {c['paso']} | {celda(c['dolor'])} | {c['clase']} | {celda(c['propuesta'])} | {c['cita']} |" for c in out]
        os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True); open(a.salida, "w", encoding="utf-8").write("\n".join(L) + "\n")
    if a.json: print(json.dumps(out, ensure_ascii=False, indent=2)); return
    for c in out: print(f"{c['paso']} [{c['clase']}] {c['propuesta']} · {c['cita']}")
    print(t(f"{len(out)} candidato(s); se registran solo tras la evaluación humana.", f"{len(out)} candidate(s); register only after human review."))

def cmd_vincular(a, e):
    ruta = None
    for tipo in ("wardley", "recorrido"):
        try_ = a.mapa if a.mapa.endswith(".json") else os.path.join(mapas_dir(a.proyecto), f"{tipo}-{a.mapa}.json")
        if os.path.exists(try_) or os.path.exists(os.path.join(a.proyecto, try_)) or os.path.exists(os.path.join(mapas_dir(a.proyecto), os.path.basename(try_))):
            ruta = resolver(a.proyecto, tipo, a.mapa); break
    if not ruta: sys.exit(t(f"No existe el mapa {a.mapa}", f"Map {a.mapa} not found"))
    with E.bloqueo(a.proyecto):          # leer, modificar y escribir el JSON sin pisar otra escritura concurrente
        d = cargar(ruta)
        elems = (d.get("anclas") or []) + (d.get("componentes") or []) + [p_ for _, p_ in pasos_de(d)]
        x = next((x for x in elems if x.get("id") == a.elemento), None)
        if x is None: sys.exit(t(f"{a.elemento}: no es un ancla, componente ni paso de {os.path.basename(ruta)}", f"{a.elemento}: not found"))
        refs = lista(x.get("refs")); nuevos = [r.strip() for r in lista(a.refs)]
        x["refs"] = [r for r in refs if r not in nuevos] if a.quitar else refs + [r for r in nuevos if r not in refs]
        guardar(ruta, d)
    print(t(f"{os.path.basename(ruta)} {a.elemento}: refs = {', '.join(x['refs']) or '—'}", f"{os.path.basename(ruta)} {a.elemento}: refs = {', '.join(x['refs']) or '—'}"))

def cmd_controles(a, e):
    hs = controles(a.proyecto)
    if a.json: print(json.dumps([{"severidad": s, "codigo": c, "mensaje": m, "arreglo": r} for s, c, m, r in hs], ensure_ascii=False, indent=2)); return
    for s, c, m, _ in hs: print(f"{s} {c} {m}")
    print(t(f"{len(hs)} aviso(s) de la familia MAP", f"{len(hs)} MAP warning(s)"))

def cmd_listar(a, e):
    xs = []
    for ruta in sorted(glob.glob(os.path.join(mapas_dir(a.proyecto), "*.json"))):
        try: d = json.load(open(ruta, encoding="utf-8"))
        except (OSError, ValueError): d = {}
        xs.append({"archivo": os.path.relpath(ruta, a.proyecto), "esquema": d.get("esquema"), "titulo": d.get("titulo"), "fecha_corte": d.get("fecha_corte")})
    if a.json: print(json.dumps(xs, ensure_ascii=False, indent=2)); return
    for x in xs: print(f"{x['archivo']} · {x['esquema']} · {x['titulo']} · {x['fecha_corte']}")
    if not xs: print(t("Sin mapas en 02-planificacion/mapas/", "No maps in 02-planificacion/mapas/"))

def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="tipo", required=True)
    for tipo in ("wardley", "recorrido"):
        s = sub.add_parser(tipo); ss = s.add_subparsers(dest="accion", required=True)
        se = ss.add_parser("semilla"); se.add_argument("--slug"); se.add_argument("--titulo"); se.add_argument("--desde", choices=["auto", "bmad", "artefactos"], default="auto")
        se.add_argument("--fecha"); se.add_argument("--forzar", action="store_true"); se.add_argument("--json", action="store_true")
        if tipo == "wardley": se.add_argument("--pregunta"); se.add_argument("--anclas"); se.add_argument("--componentes")
        else: se.add_argument("--uj"); se.add_argument("--backstage"); se.add_argument("--persona"); se.add_argument("--etapas")
        va = ss.add_parser("validar"); va.add_argument("mapa"); va.add_argument("--json", action="store_true")
        re_ = ss.add_parser("render"); re_.add_argument("mapa"); re_.add_argument("--png", choices=["auto", "si", "no"], default="auto"); re_.add_argument("--json", action="store_true")
        if tipo == "recorrido":
            ca = ss.add_parser("candidatos"); ca.add_argument("mapa"); ca.add_argument("--salida"); ca.add_argument("--json", action="store_true")
    vi = sub.add_parser("vincular"); vi.add_argument("mapa"); vi.add_argument("elemento"); vi.add_argument("--refs", required=True); vi.add_argument("--quitar", action="store_true")
    co = sub.add_parser("controles"); co.add_argument("--json", action="store_true")
    li = sub.add_parser("listar"); li.add_argument("--json", action="store_true")
    tb = sub.add_parser("tablero"); tb.add_argument("--mapas", help="slugs separados por coma (defecto: todos los mapas válidos)")
    tb.add_argument("--insertar", help="tablero de avance (HTML de pm-visuales) donde reemplazar la sección entre los marcadores pm-mapas")
    tb.add_argument("--salida", help="vista autocontenida (defecto: 02-planificacion/visuales/tablero-mapas.html; con --insertar solo si se pide)")
    tb.add_argument("--json", action="store_true")
    a = ap.parse_args()
    e = estado_proyecto(a.proyecto); IDIOMA = e.get("idioma", "es")
    if getattr(a, "fecha", None):
        try: datetime.date.fromisoformat(a.fecha)
        except ValueError: sys.exit(t(f"--fecha {a.fecha}: formato AAAA-MM-DD", f"--fecha {a.fecha}: use YYYY-MM-DD"))
    if a.tipo == "vincular": cmd_vincular(a, e); return
    if a.tipo == "controles": cmd_controles(a, e); return
    if a.tipo == "listar": cmd_listar(a, e); return
    if a.tipo == "tablero": cmd_tablero(a, e); return
    if a.accion == "semilla": cmd_semilla(a, e, a.tipo)
    elif a.accion == "validar":
        ruta = resolver(a.proyecto, a.tipo, a.mapa)
        sys.exit(1 if informe_validacion(os.path.relpath(ruta, a.proyecto), cargar(ruta), a.tipo, a.json) else 0)
    elif a.accion == "render": cmd_render(a, e, a.tipo)
    elif a.accion == "candidatos": cmd_candidatos(a, e)

if __name__ == "__main__":
    main()
