#!/usr/bin/env python3
"""Maestro de interesados de pm-method · Stakeholder master.

Un solo catálogo (03-control/registros/stakeholders.csv) que usa todo el ecosistema: matriz poder/interés con estrategia
por cuadrante, matriz RACI (raci.csv) vinculada a productos, paquetes, requisitos, épicas, historias y KR, estereotipos
(estereotipos.csv) y preferencias individuales con procedencia y evidencia (preferencias.csv), perfil de comunicación
resuelto, vínculos de cada interesado en el resto de los registros, reporte HTML y plan de envío para la capa de canales
(pm-integraciones/scripts/envios.py).

Uso / Usage (todas las rutas relativas a la carpeta de trabajo; --proyecto = carpeta con estado.json):
  interesados.py --proyecto G matriz [--medio alto|bajo] [--markdown F] [--json]
  interesados.py --proyecto G estereotipos [--semilla] [--sugerir] [--json]
  interesados.py --proyecto G proponer --transcripcion F [--mapa "Nombre=ST-001;Otro=ST-002"] [--fecha AAAA-MM-DD]
                 [--fuente RUTA] [--vigencia-dias 180] [--registrar] [--json]
  interesados.py --proyecto G confirmar PF-001 [PF-002 …] --por "Rol: Nombre" [--vigencia-hasta AAAA-MM-DD]
  interesados.py --proyecto G rechazar PF-001 [...] --por "Rol: Nombre" [--motivo "…"]
  interesados.py --proyecto G perfil ST-001|todos [--corte AAAA-MM-DD] [--json]
  interesados.py --proyecto G raci [--elemento ID] [--markdown F] [--json]
  interesados.py --proyecto G vinculos ST-001 [--json]
  interesados.py --proyecto G integridad [--json]
  interesados.py --proyecto G reporte --html F [--markdown F] [--corte AAAA-MM-DD] [--restringido] [--medio alto|bajo]
  interesados.py --proyecto G plan-envio --tema "…" --audiencia "cuadrante:gestionar-de-cerca,ST-004,raci:E-2:AR"
                 [--proposito comunicado] [--base archivo.md] [--agrupar] [--fecha AAAA-MM-DD]
  interesados.py --proyecto G personas candidatos [--desde auto|bmad|artefactos] [--limite 40] [--json]
  interesados.py --proyecto G personas mapa|priorizacion [--limite 40] [--json]
Personas de usuario (personas.csv, PU-###): arquetipos que piden (solicita), usan (usa) o se benefician (beneficia) de
  requisitos, épicas, historias o productos; no son interesados ni estereotipos de comunicación. 'candidatos' las propone
  desde los recorridos UJ-n de BMAD (solo lectura), los recorridos de pm-mapas-estrategicos y las historias «Como <rol>…»;
  se registran con registro.py después de confirmarlas. Controles STK-13…16 en 'integridad' (y en sanidad).
Audiencia: todos · ST-001 · cuadrante:<c> · estereotipo:ET-001 · raci:<elemento>:<roles RACI> · rol:<texto en rol_proyecto>;
  -ST-009 (o !ST-009) excluye a alguien (p. ej. a quien envía).
Privacidad: el script no infiere emociones, personalidad ni rasgos sensibles; solo registra lo que la persona declaró
(con cita) y lo que el gestor confirma. Las valoraciones (actitud, compromiso) solo aparecen con --restringido.
"""
import argparse, csv, datetime, glob, html, json, os, re, shlex, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
NUCLEO = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-estado-proyecto", "scripts"))
REUNIONES = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-reuniones", "scripts"))
sys.path.insert(0, NUCLEO)
import esquema as E

IDIOMA = "es"
def t(es, en): return en if IDIOMA == "en" else es

# ------------------------------------------------------------------ cuadrantes y estrategias
CUADRANTES = ["gestionar-de-cerca", "mantener-satisfecho", "mantener-informado", "monitorear"]
ESTRATEGIA = {
    "gestionar-de-cerca": {
        "nombre": ("Gestionar de cerca", "Manage closely"), "poder": "alto", "interes": "alto",
        "quienes": ("Patrocinadores clave, dirección general, clientes principales.", "Key sponsors, senior executives, main customers."),
        "estrategia": ("Los actores más críticos: comunicación constante, participación activa en las decisiones y máxima atención.",
                       "The most critical actors: constant communication, active participation in decisions and maximum attention."),
        "defecto": {"canal": "reunion", "formato": "conclusion-primero", "nivel_detalle": "resumen", "frecuencia": "semanal"},
        "raci": ("A, R o C en las decisiones y entregables clave", "A, R or C on key decisions and deliverables")},
    "mantener-satisfecho": {
        "nombre": ("Mantener satisfecho", "Keep satisfied"), "poder": "alto", "interes": "bajo",
        "quienes": ("Directivos de alto nivel o reguladores que no participan del día a día pero pueden frenar el proyecto.",
                    "Senior managers or regulators who are not involved day to day but can stop the project."),
        "estrategia": ("No abrumar con detalles; reportes ejecutivos de alto nivel sobre beneficios y avance.",
                       "Do not overload with detail; high-level executive reports on benefits and progress."),
        "defecto": {"canal": "correo", "formato": "conclusion-primero", "nivel_detalle": "ejecutivo", "frecuencia": "mensual"},
        "raci": ("C en hitos y cambios que los afectan; I del avance", "C on milestones and changes that affect them; I on progress")},
    "mantener-informado": {
        "nombre": ("Mantener informado", "Keep informed"), "poder": "bajo", "interes": "alto",
        "quienes": ("Usuarios finales, equipos colaboradores, áreas secundarias afectadas.", "End users, contributing teams, affected secondary areas."),
        "estrategia": ("Canales claros (boletines, reuniones informativas) y escucha activa de su retroalimentación: suelen ser aliados y fuente de información.",
                       "Clear channels (newsletters, briefings) and active listening: they are often allies and a source of information."),
        "defecto": {"canal": "correo", "formato": "lista", "nivel_detalle": "resumen", "frecuencia": "quincenal"},
        "raci": ("C (retroalimentación) o I", "C (feedback) or I")},
    "monitorear": {
        "nombre": ("Monitorear", "Monitor"), "poder": "bajo", "interes": "bajo",
        "quienes": ("Público general o áreas muy periféricas.", "General public or very peripheral areas."),
        "estrategia": ("Supervisar con el menor esfuerzo, sin gastar recursos innecesarios, salvo que cambien de posición en la matriz.",
                       "Watch with minimum effort and no unnecessary resources, unless they move in the grid."),
        "defecto": {"canal": "tablero", "formato": "lista", "nivel_detalle": "ejecutivo", "frecuencia": "a-demanda"},
        "raci": ("I solo si corresponde", "I only when relevant")},
}
DIMENSIONES = ["canal", "formato", "nivel_detalle", "frecuencia", "idioma", "registro", "horario", "estilo_decision", "evitar"]

# estereotipos semilla = los estereotipos de audiencia de pm-comunicacion-stakeholders (guía §1)
SEMILLA = [
    ("direccion-patrocinador", "Ejecutivo, junta, capa de negocio, PMO: decisiones pendientes, desvíos contra tolerancias, riesgos del business case.",
     "gestionar-de-cerca", "reunion", "conclusion-primero", "ejecutivo", "por-hito", "formal", "datos"),
    ("equipo", "Gestores de equipo y miembros: bloqueos, prioridades, cambios aprobados, tolerancias de paquete.",
     "mantener-informado", "", "lista", "detallado", "semanal", "cercano", ""),
    ("cliente-usuario", "Usuario sénior, usuarios finales, cliente: hitos y entregas, qué recibe y cuándo, qué se le pide.",
     "mantener-informado", "correo", "narrativa", "resumen", "quincenal", "neutral", ""),
    ("proveedores", "Proveedor sénior y contratistas: dependencias, fechas de entrada, aceptaciones, hitos de pago.",
     "mantener-satisfecho", "correo", "lista", "resumen", "por-hito", "formal", ""),
    ("regulador-comunidad", "Autoridades y comunidad: cumplimiento, impacto, hitos públicos autorizados por el ejecutivo.",
     "mantener-satisfecho", "correo", "conclusion-primero", "ejecutivo", "por-hito", "formal", ""),
    ("product-owner-usuarios-clave", "PO y usuarios clave (ágil): incremento terminado, retroalimentación, cambios del backlog, Must en riesgo.",
     "gestionar-de-cerca", "reunion", "datos", "detallado", "semanal", "neutral", "datos"),
]

# ------------------------------------------------------------------ datos
def ruta(p, *x): return os.path.join(p, *x)

def leer(proyecto, reg):
    p = E.ruta_registro(proyecto, reg)
    return E.leer_csv(p)[1] if os.path.exists(p) else []

def guardar(proyecto, reg, filas):
    with E.bloqueo(proyecto):            # quien leyó `filas` debería tener ya el bloqueo (reentrante)
        p = E.asegurar_registro(proyecto, reg); cols, _ = E.leer_csv(p)
        E.escribir_csv(p, cols, filas)

def agregar(proyecto, reg, fila):
    with E.bloqueo(proyecto):            # id siguiente sobre el archivo releído bajo el bloqueo del proyecto
        p = E.asegurar_registro(proyecto, reg); cols, filas = E.leer_csv(p)
        f = {c: "" for c in cols}; f.update({k: v for k, v in fila.items() if k in cols})
        f["id"] = f.get("id") or E.siguiente_id(reg, filas)
        if "estado" in cols and not f.get("estado") and E.REGISTROS[reg].get("estado_inicial"): f["estado"] = E.REGISTROS[reg]["estado_inicial"]
        errores = validar_valores(reg, f)
        if errores: sys.exit(t("Validación: ", "Validation: ") + "; ".join(errores))
        filas.append(f); E.escribir_csv(p, cols, filas); return f["id"]

def validar_valores(reg, f):
    out = []
    for col, perm in E.REGISTROS[reg].get("valores", {}).items():
        v = f.get(col, "")
        if v and v not in perm: out.append(f"{col}='{v}' ∉ {{{', '.join(x for x in perm if x)}}}")
    return out

def norm(s):
    s = (s or "").split(":")[-1] if ":" in (s or "") else (s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()

def corto(nombre, n=18):
    """Nombre abreviado para tablas y la matriz: completo si entra; si no, cortado en una palabra con «…»."""
    nombre = (nombre or "").strip()
    if len(nombre) <= n: return nombre
    out = ""
    for w in nombre.split():
        if len(out) + len(w) + (1 if out else 0) > n - 1: break
        out = (out + " " + w).strip()
    return (out or nombre[:n - 1]) + "…"

def estado_json(proyecto):
    try: return E.cargar_estado(proyecto)
    except SystemExit: return {}

def okr_filas(proyecto):
    p = ruta(proyecto, "00-direccion", "okr.csv")
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []

# ------------------------------------------------------------------ matriz poder/interés
def binario(v, medio):
    return {"alto": "alto", "bajo": "bajo", "medio": medio}.get((v or "").strip())

def cuadrante(st, medio="alto"):
    p, i = binario(st.get("poder"), medio), binario(st.get("interes"), medio)
    if not p or not i: return ""
    return {("alto", "alto"): "gestionar-de-cerca", ("alto", "bajo"): "mantener-satisfecho",
            ("bajo", "alto"): "mantener-informado", ("bajo", "bajo"): "monitorear"}[(p, i)]

def frontera(st): return "medio" in ((st.get("poder") or ""), (st.get("interes") or ""))

def matriz(proyecto, medio="alto"):
    sts = leer(proyecto, "stakeholders"); out = {c: [] for c in CUADRANTES}; sin = []
    for s in sts:
        c = cuadrante(s, medio)
        (out[c] if c else sin).append(s)
    return out, sin

# ------------------------------------------------------------------ perfil de comunicación (precedencia documentada)
def vigente(pf, corte): return not pf.get("vigencia_hasta") or pf["vigencia_hasta"] >= corte

def perfil(proyecto, st, corte=None, medio="alto", cache=None):
    """Resuelve cada dimensión con su procedencia. Precedencia (de menor a mayor):
    cuadrante → idioma del proyecto → estereotipo → matriz de comunicaciones (canal/frecuencia del registro) →
    preferencias confirmadas y vigentes (la más reciente gana). Propuestas y vencidas se informan, no se aplican."""
    corte = corte or datetime.date.today().isoformat()
    c = cache or {}
    ets = c.get("et") or {x["id"]: x for x in leer(proyecto, "estereotipos")}
    pfs = c.get("pf") if c.get("pf") is not None else leer(proyecto, "preferencias")
    e = c.get("estado") or estado_json(proyecto)
    res = {d: {"valor": "", "fuente": ""} for d in DIMENSIONES}
    def poner(d, v, fuente):
        if v: res[d] = {"valor": v, "fuente": fuente}
    q = cuadrante(st, medio)
    if q:
        for d, v in ESTRATEGIA[q]["defecto"].items(): poner(d, v, f"cuadrante:{q}")
    poner("idioma", e.get("idioma", "es"), t("idioma del proyecto", "project language"))
    et = ets.get(st.get("estereotipo", ""))
    if et and et.get("estado", "activo") == "activo":
        for d in DIMENSIONES:
            v = et.get(d, "")
            if d == "canal" and not v and et.get("nombre") == "equipo":
                v = {"slack": "slack", "teams": "teams"}.get(e.get("integraciones", {}).get("chat", ""), "")
            poner(d, v, f"estereotipo:{et['id']}")
    matriz_vals = {}
    canal_reg = (st.get("canal") or "").strip().lower()
    if canal_reg in E.REGISTROS["estereotipos"]["valores"]["canal"] and canal_reg:
        poner("canal", canal_reg, t("matriz de comunicaciones", "communications matrix")); matriz_vals["canal"] = canal_reg
    frec_reg = (st.get("frecuencia") or "").strip().lower()
    if frec_reg in E.REGISTROS["estereotipos"]["valores"]["frecuencia"] and frec_reg:
        poner("frecuencia", frec_reg, t("matriz de comunicaciones", "communications matrix")); matriz_vals["frecuencia"] = frec_reg
    propias = [p for p in pfs if p.get("stakeholder_id") == st.get("id")]
    pendientes, vencidas, conflictos, evitar = [], [], [], []
    for p in sorted(propias, key=lambda x: (x.get("fecha", ""), x.get("id", ""))):
        if p.get("estado") == "propuesta": pendientes.append(p); continue
        if p.get("estado") != "confirmada": continue
        if not vigente(p, corte): vencidas.append(p); continue
        d = p.get("dimension")
        if d == "evitar": evitar.append(p.get("valor", "")); continue
        if d in res:
            if d in matriz_vals and matriz_vals[d] != p.get("valor"):
                conflictos.append(t(f"{d}: la preferencia confirmada {p['id']} ({p.get('valor')}) difiere de la matriz aprobada ({matriz_vals[d]}); actualizar la matriz (pm-comunicacion-stakeholders)",
                                    f"{d}: confirmed preference {p['id']} ({p.get('valor')}) differs from the approved matrix ({matriz_vals[d]}); update the matrix"))
            poner(d, p.get("valor", ""), f"{p['id']} ({p.get('procedencia', '')}, {p.get('fecha', '')})")
    if evitar: res["evitar"] = {"valor": "; ".join(evitar), "fuente": t("preferencias confirmadas", "confirmed preferences")}
    canal = res["canal"]["valor"]
    destino = st.get("correo", "") if canal == "correo" else (st.get("usuario_chat", "") if canal in ("slack", "teams") else "")
    return {"id": st.get("id"), "nombre": st.get("nombre", ""), "cuadrante": q, "frontera": frontera(st),
            "estereotipo": st.get("estereotipo", ""), "dimensiones": res, "destino": destino,
            "pendientes": [p["id"] for p in pendientes], "vencidas": [p["id"] for p in vencidas], "conflictos": conflictos}

# ------------------------------------------------------------------ ids conocidos (integridad referencial)
PATRON_SPEC = re.compile(r"^(REQ|FR|NFR|UJ|SM|AD|UX-DR)-?\d+$|^E-?\d+$|^\d+-\d+(-[\w-]+)?$")

def ids_conocidos(proyecto):
    """{tipo: set(ids)} de las fuentes del ecosistema (solo lectura)."""
    out = {"spec": set(), "okr": set(), "wbs": set(), "backlog": set(), "actividades": set(), "decisiones": set(),
           "tit": {k: {} for k in ("spec", "okr", "wbs", "backlog", "actividades", "decisiones")}}
    try:
        sys.path.insert(0, NUCLEO); import especificacion as SP
        idx, _ = SP.obtener(proyecto)
        for col in ("requisitos", "epicas", "historias"):
            for x in idx.get(col, []):
                for k in ("id", "numero"):
                    if x.get(k): out["spec"].add(str(x[k])); out["tit"]["spec"][str(x[k])] = x.get("titulo", "")
    except BaseException: pass
    for f in okr_filas(proyecto):
        out["okr"].add(f.get("id", "")); out["tit"]["okr"][f.get("id", "")] = f.get("enunciado", "")
    for nombre, col, clave in (("wbs.csv", "codigo", "wbs"), ("backlog.csv", "id", "backlog"), ("actividades.csv", "id", "actividades")):
        p = ruta(proyecto, "02-planificacion", nombre)
        if os.path.exists(p):
            for f in csv.DictReader(open(p, encoding="utf-8")):
                v = (f.get(col) or "").strip()
                if v: out[clave].add(v); out["tit"][clave][v] = f.get("nombre") or f.get("titulo") or ""
    for f in leer(proyecto, "decisiones"): out["decisiones"].add(f.get("id", "")); out["tit"]["decisiones"][f.get("id", "")] = f.get("decision", "")
    return out

FUENTES_TITULO = {"requisito": ("spec", "backlog"), "epica": ("spec",), "historia": ("spec", "backlog"), "kr": ("okr",), "objetivo": ("okr",),
                  "producto": ("wbs",), "paquete": ("wbs",), "actividad": ("actividades", "wbs"), "decision": ("decisiones",)}

def titulo_de(ids, elemento, tipo, n=90):
    """Título del elemento según su tipo (evita confundir el paquete 3.1 de la WBS con la historia 3.1)."""
    for fuente in FUENTES_TITULO.get(tipo, ()):
        tt = ids["tit"][fuente].get(elemento)
        if tt: return tt if len(tt) <= n else tt[:n - 1].rstrip() + "…"
    return ""

def tipo_de(elemento, declarado):
    if declarado: return declarado
    if re.match(r"^KR-", elemento): return "kr"
    if re.match(r"^O-\d", elemento): return "objetivo"
    if re.match(r"^D-\d{3}$", elemento): return "decision"
    if re.match(r"^E-?\d+$", elemento): return "epica"
    if re.match(r"^\d+-\d+", elemento): return "historia"
    if PATRON_SPEC.match(elemento): return "requisito"
    if re.match(r"^\d+(\.\d+)*$", elemento): return "paquete"
    return "otro"

def elemento_existe(ids, elemento, tipo):
    if tipo in ("requisito", "epica", "historia"): return elemento in ids["spec"] or elemento in ids["backlog"]
    if tipo in ("kr", "objetivo"): return elemento in ids["okr"]
    if tipo in ("producto", "paquete"): return elemento in ids["wbs"]
    if tipo == "actividad": return elemento in ids["actividades"] or elemento in ids["wbs"]
    if tipo == "decision": return elemento in ids["decisiones"]
    return True     # entregable / otro: texto libre, no se valida

# ------------------------------------------------------------------ RACI
def raci(proyecto, medio="alto", ids=None):
    filas = leer(proyecto, "raci"); sts = {s["id"]: s for s in leer(proyecto, "stakeholders")}
    ids = ids or ids_conocidos(proyecto)
    por = {}
    for f in filas: por.setdefault(f.get("elemento", ""), []).append(f)
    hall = []          # (severidad, codigo, mensaje)
    for el, fs in por.items():
        tipo = tipo_de(el, next((x.get("tipo_elemento") for x in fs if x.get("tipo_elemento")), ""))
        roles = [x.get("rol") for x in fs if x.get("stakeholder_id") in sts]     # solo interesados existentes
        if roles.count("A") == 0: hall.append(("AVISO", "STK-02", t(f"RACI {el}: sin Aprobador (A); debe haber exactamente uno", f"RACI {el}: no Accountable (A); exactly one is required")))
        if roles.count("A") > 1: hall.append(("AVISO", "STK-02", t(f"RACI {el}: {roles.count('A')} Aprobadores (A); debe haber exactamente uno", f"RACI {el}: {roles.count('A')} Accountables; exactly one")))
        if roles.count("R") == 0: hall.append(("AVISO", "STK-11", t(f"RACI {el}: sin Responsable (R)", f"RACI {el}: no Responsible (R)")))
        if roles.count("C") > 3: hall.append(("INFO", "STK-11", t(f"RACI {el}: {roles.count('C')} Consultados (sobre-consulta, >3)", f"RACI {el}: {roles.count('C')} Consulted (over-consultation)")))
        vistos = {}
        for x in fs:
            sid = x.get("stakeholder_id", "")
            if sid not in sts: hall.append(("ERROR", "STK-03", t(f"raci {x.get('id')}: interesado {sid or '(vacío)'} inexistente en stakeholders.csv", f"raci {x.get('id')}: stakeholder {sid or '(empty)'} not in stakeholders.csv"))); continue
            if sid in vistos: hall.append(("AVISO", "STK-02", t(f"RACI {el}: {sid} figura dos veces ({vistos[sid]} y {x.get('rol')}); un rol por persona y elemento", f"RACI {el}: {sid} appears twice")))
            vistos[sid] = x.get("rol")
            if x.get("rol") == "A" and binario(sts[sid].get("poder"), medio) == "bajo":
                hall.append(("INFO", "STK-11", t(f"RACI {el}: el Aprobador {sid} tiene poder bajo en la matriz; confirmar su autoridad", f"RACI {el}: Accountable {sid} has low power")))
        if not elemento_existe(ids, el, tipo):
            hall.append(("AVISO", "STK-09", t(f"RACI {el} ({tipo}): no se encontró en su fuente (especificación, OKR, WBS, actividades o decisiones)", f"RACI {el} ({tipo}): not found in its source")))
    if len(por) >= 5:
        cuenta = {}
        for fs in por.values():
            for x in fs:
                if x.get("rol") == "A": cuenta[x["stakeholder_id"]] = cuenta.get(x["stakeholder_id"], 0) + 1
        for sid, n in cuenta.items():
            if n / len(por) > 0.4: hall.append(("INFO", "STK-11", t(f"RACI: {sid} es Aprobador en {n} de {len(por)} elementos (>40 %): concentración", f"RACI: {sid} is Accountable on {n}/{len(por)} items (>40%)")))
    if por:
        con_rol = {x.get("stakeholder_id") for f in por.values() for x in f}
        for s in sts.values():
            if cuadrante(s, medio) == "gestionar-de-cerca" and s["id"] not in con_rol:
                hall.append(("AVISO", "STK-06", t(f"{s['id']} {s.get('nombre','')} es 'gestionar de cerca' y no tiene rol en la RACI", f"{s['id']} is 'manage closely' with no RACI role")))
    return por, hall

# ------------------------------------------------------------------ integridad referencial (la usa sanidad.py)
def integridad(proyecto, corte=None, medio="alto"):
    corte = corte or datetime.date.today().isoformat(); h = []
    sts = leer(proyecto, "stakeholders"); ids_st = {s["id"] for s in sts}
    ets = {x["id"]: x for x in leer(proyecto, "estereotipos")}
    nombres = {}
    for s in sts:
        if not s.get("poder") or not s.get("interes"):
            h.append(("AVISO", "STK-01", t(f"{s['id']} {s.get('nombre','')}: sin poder o interés; no se puede ubicar en la matriz", f"{s['id']}: missing power or interest")))
        if s.get("estereotipo") and s["estereotipo"] not in ets:
            h.append(("ERROR", "STK-03", t(f"{s['id']}: estereotipo {s['estereotipo']} inexistente en estereotipos.csv", f"{s['id']}: stereotype {s['estereotipo']} does not exist")))
        elif s.get("estereotipo") and ets[s["estereotipo"]].get("estado") == "retirado":
            h.append(("AVISO", "STK-03", t(f"{s['id']}: usa el estereotipo retirado {s['estereotipo']}", f"{s['id']}: uses retired stereotype {s['estereotipo']}")))
        n = norm(s.get("nombre"))
        if n: nombres.setdefault(n, []).append(s["id"])
        if s.get("correo") and not re.match(r"^[^@\s;]+@[^@\s;]+\.[^@\s;]+$", s["correo"]):
            h.append(("AVISO", "STK-03", t(f"{s['id']}: correo con formato inválido", f"{s['id']}: invalid e-mail format")))
    for n, xs in nombres.items():
        if len(xs) > 1: h.append(("AVISO", "STK-10", t(f"Nombre repetido en el maestro: {', '.join(xs)}", f"Duplicate name in the master: {', '.join(xs)}")))
    for reg in ("preferencias", "envios", "personas"):
        for f in leer(proyecto, reg):
            sid = f.get("stakeholder_id", "")
            if sid and sid not in ids_st: h.append(("ERROR", "STK-03", t(f"{reg} {f.get('id')}: interesado {sid} inexistente", f"{reg} {f.get('id')}: stakeholder {sid} does not exist")))
            if reg == "preferencias" and not sid: h.append(("ERROR", "STK-03", t(f"preferencias {f.get('id')}: sin stakeholder_id", f"preferencias {f.get('id')}: no stakeholder_id")))
    for p in leer(proyecto, "preferencias"):
        if p.get("estado") == "confirmada" and not vigente(p, corte):
            h.append(("AVISO", "STK-04", t(f"Preferencia {p['id']} de {p.get('stakeholder_id')} vencida el {p.get('vigencia_hasta')}: revalidar con la persona", f"Preference {p['id']} expired on {p.get('vigencia_hasta')}: revalidate")))
        if p.get("estado") == "propuesta" and p.get("fecha"):
            try:
                if (datetime.date.fromisoformat(corte) - datetime.date.fromisoformat(p["fecha"])).days > 30:
                    h.append(("INFO", "STK-05", t(f"Preferencia propuesta {p['id']} sin confirmar desde {p['fecha']}", f"Proposed preference {p['id']} unconfirmed since {p['fecha']}")))
            except ValueError: pass
        if p.get("estado") == "confirmada" and not p.get("confirmado_por"):
            h.append(("AVISO", "STK-04", t(f"Preferencia {p['id']} confirmada sin confirmado_por", f"Preference {p['id']} confirmed without confirmado_por")))
    for f in leer(proyecto, "envios"):
        if f.get("estado") in ("fallido", "pendiente"):
            h.append(("AVISO", "STK-07", t(f"Envío {f['id']} a {f.get('stakeholder_id')} en estado {f['estado']} ({f.get('canal')}, {f.get('asunto','')[:50]})", f"Delivery {f['id']} is {f['estado']}")))
    if sts:
        por_nombre = {norm(s.get("nombre")): s["id"] for s in sts}
        for f in okr_filas(proyecto):
            r = (f.get("responsable") or "").strip()
            if r and r not in ids_st and norm(r) not in por_nombre:
                h.append(("AVISO", "STK-08", t(f"OKR {f.get('id')}: el responsable '{r}' no está en el maestro de interesados", f"OKR {f.get('id')}: owner '{r}' is not in the stakeholder master")))
    if leer(proyecto, "raci"):
        _, hr = raci(proyecto, medio); h += hr
    h += cadencia(proyecto, corte, medio, sts)
    h += controles_personas(proyecto)
    return h

DIAS_FRECUENCIA = {"diaria": 1, "semanal": 7, "quincenal": 14, "mensual": 31, "trimestral": 92}

def cadencia(proyecto, corte, medio="alto", sts=None):
    """STK-12: compromiso sostenido. Para cada interesado de los cuadrantes que exigen contacto periódico, compara el
    último contacto registrado en envios.csv (estado enviado: correo, chat, reunión o llamada registrados) con la
    frecuencia de su perfil; tolerancia 1,5 × el período. Solo corre si el proyecto registra envíos."""
    envs = [f for f in leer(proyecto, "envios") if f.get("estado") == "enviado" and f.get("fecha") and f["fecha"] <= corte]
    if not envs: return []
    sts = sts if sts is not None else leer(proyecto, "stakeholders")
    inicio = min(f["fecha"] for f in envs); ultimo = {}
    for f in envs: ultimo[f.get("stakeholder_id", "")] = max(ultimo.get(f.get("stakeholder_id", ""), ""), f["fecha"])
    cache = {"et": {x["id"]: x for x in leer(proyecto, "estereotipos")}, "pf": leer(proyecto, "preferencias"), "estado": estado_json(proyecto)}
    out = []
    for s in sts:
        q = cuadrante(s, medio)
        if q not in ("gestionar-de-cerca", "mantener-satisfecho", "mantener-informado"): continue
        frec = perfil(proyecto, s, corte, medio, cache)["dimensiones"]["frecuencia"]["valor"]
        dias = DIAS_FRECUENCIA.get(frec)
        if not dias: continue
        limite = round(dias * 1.5)
        try:
            desde = ultimo.get(s["id"]) or inicio
            gap = (datetime.date.fromisoformat(corte) - datetime.date.fromisoformat(desde)).days
        except ValueError: continue
        if gap > limite:
            if s["id"] in ultimo:
                out.append(("AVISO", "STK-12", t(f"{s['id']} {s.get('nombre','')} ({q}, frecuencia {frec}): último contacto registrado el {ultimo[s['id']]}, hace {gap} días (máximo {limite})",
                                                 f"{s['id']} ({q}, {frec}): last recorded contact on {ultimo[s['id']]}, {gap} days ago (max {limite})")))
            else:
                out.append(("AVISO", "STK-12", t(f"{s['id']} {s.get('nombre','')} ({q}, frecuencia {frec}): sin contacto registrado desde {inicio} ({gap} días; máximo {limite})",
                                                 f"{s['id']} ({q}, {frec}): no recorded contact since {inicio} ({gap} days; max {limite})")))
    return out

def resolver_st(proyecto, valor, sts=None):
    """ST-id o nombre (exacto, sin acentos) → fila del maestro, o None."""
    sts = sts if sts is not None else leer(proyecto, "stakeholders")
    for s in sts:
        if s["id"] == valor: return s
    n = norm(valor)
    for s in sts:
        if norm(s.get("nombre")) == n: return s
    return None

# ------------------------------------------------------------------ vínculos de un interesado en el ecosistema
def vinculos(proyecto, sid):
    sts = leer(proyecto, "stakeholders"); s = resolver_st(proyecto, sid, sts)
    if not s: sys.exit(t(f"No existe {sid} en stakeholders.csv", f"{sid} not found in stakeholders.csv"))
    clave = {s["id"], norm(s.get("nombre"))}
    def es(v): return bool(v) and (v.strip() in clave or norm(v) in clave or any(norm(x) in clave for x in re.split(r"[;,/]", v)))
    ids = ids_conocidos(proyecto); out = {"interesado": {k: s.get(k, "") for k in ("id", "nombre", "rol_proyecto", "estereotipo")},
                                         "cuadrante": cuadrante(s), "raci": [], "okr": [], "registros": [], "preferencias": [], "envios": []}
    for f in leer(proyecto, "raci"):
        if f.get("stakeholder_id") == s["id"]:
            out["raci"].append({"elemento": f["elemento"], "rol": f["rol"], "tipo": tipo_de(f["elemento"], f.get("tipo_elemento")), "titulo": titulo_de(ids, f["elemento"], tipo_de(f["elemento"], f.get("tipo_elemento"))) or f.get("descripcion", "")})
    for f in okr_filas(proyecto):
        if es(f.get("responsable", "")): out["okr"].append({"id": f["id"], "tipo": f.get("tipo"), "enunciado": f.get("enunciado", "")})
    campos = {"riesgos": ("propietario", "ejecutor"), "issues": ("responsable", "decidido_por"), "acciones": ("responsable",),
              "calidad": ("responsable_productor", "revisores", "aprobador"), "lecciones": ("responsable_seguimiento",),
              "supuestos": ("responsable",), "decisiones": ("decidido_por",), "cambios": ("solicitante", "decidido_por")}
    for reg, cols in campos.items():
        for f in leer(proyecto, reg):
            for c in cols:
                if es(f.get(c, "")): out["registros"].append({"registro": reg, "id": f["id"], "como": c, "estado": f.get("estado", "")}); break
    out["preferencias"] = [{"id": p["id"], "dimension": p["dimension"], "valor": p["valor"], "estado": p["estado"]} for p in leer(proyecto, "preferencias") if p.get("stakeholder_id") == s["id"]]
    out["envios"] = [{"id": f["id"], "fecha": f["fecha"], "canal": f["canal"], "asunto": f["asunto"], "estado": f["estado"]} for f in leer(proyecto, "envios") if f.get("stakeholder_id") == s["id"]]
    return out

# ------------------------------------------------------------------ preferencias desde transcripciones (solo lo declarado, con cita)
PRIMERA_PERSONA = re.compile(r"\b(prefiero|preferir[ií]a|me sirve|me viene mejor|me resulta|mand[aá]me|env[ií]ame|escrib[ií]me|esc?r[ií]beme|p[aá]same|"
                             r"necesito|quiero|no me|para m[ií]|yo leo|i prefer|i'd prefer|i would prefer|send me|email me|ping me|i need|i want|"
                             r"please (?:send|keep|copy)|don't (?:send|cc|copy) me|for me)\b", re.I)
PATRONES = [
    ("canal", "correo", r"\b(correo|mail|e-?mail)\b"), ("canal", "slack", r"\bslack\b"), ("canal", "teams", r"\bteams\b"),
    ("canal", "llamada", r"\b(llamada|llam[aá]me|phone call|call me)\b"), ("canal", "reunion", r"\b(reuni[oó]n|en persona|meeting|in person)\b"),
    ("canal", "tablero", r"\b(tablero|dashboard)\b"),
    ("formato", "conclusion-primero", r"(al grano|conclusi[oó]n (primero|arriba|al principio)|la decisi[oó]n primero|bottom line|lead with the (conclusion|decision))"),
    ("formato", "datos", r"\b(datos|n[uú]meros|cifras|numbers|data|figures)\b"), ("formato", "visual", r"\b(gr[aá]fic\w*|visual\w*|charts?)\b"),
    ("formato", "lista", r"\b(vi[ñn]etas|bullets?|punteo|en lista|bullet points)\b"), ("formato", "narrativa", r"(contexto completo|la historia completa|narrativ\w*|the full story)"),
    ("nivel_detalle", "ejecutivo", r"(una (sola )?p[aá]gina|resumen ejecutivo|one[- ]pager|solo lo esencial|executive summary|lo m[ií]nimo|breve|corto\b|short\b)"),
    ("nivel_detalle", "detallado", r"(en detalle|detallad\w*|todo el detalle|in detail|full detail|detailed)"),
    ("frecuencia", "diaria", r"\b(diari\w*|todos los d[ií]as|daily|every day)\b"),
    ("frecuencia", "semanal", r"(cada semana|semanal\w*|\blos (lunes|martes|mi[eé]rcoles|jueves|viernes)\b|weekly|every (week|monday|tuesday|wednesday|thursday|friday)|on (mondays|tuesdays|wednesdays|thursdays|fridays))"),
    ("frecuencia", "quincenal", r"(cada dos semanas|quincenal\w*|biweekly|every two weeks|fortnightly)"),
    ("frecuencia", "mensual", r"(mensual\w*|una vez (al|por) mes|cada mes|monthly|once a month)"),
    ("frecuencia", "trimestral", r"(trimestral\w*|cada tres meses|una vez (al|por) trimestre|quarterly|every (three|3) months)"),
    ("frecuencia", "por-hito", r"((solo|s[oó]lo) (en|cuando haya|con) (los )?hitos|por hito|at milestones|only at milestones)"),
    ("frecuencia", "a-demanda", r"(solo si hay (problemas|novedades|desv[ií]os)|cuando sea necesario|only if (there are )?(issues|problems)|when needed)"),
    ("idioma", "en", r"(en ingl[eé]s|in english)"), ("idioma", "es", r"(en espa[nñ]ol|in spanish)"), ("idioma", "pt", r"(en portugu[eé]s|in portuguese)"),
    ("registro", "formal", r"\bformal\b"), ("registro", "cercano", r"\b(informal|sin vueltas|casual)\b"),
    ("estilo_decision", "datos", r"(decido con datos|necesito (los )?datos para decidir|data to decide)"),
    ("estilo_decision", "consenso", r"(lo decidimos entre todos|por consenso|consensus)"),
]
HORARIO = re.compile(r"(antes de las \d{1,2}(?::\d\d)?|despu[eé]s de las \d{1,2}(?::\d\d)?|por la ma[nñ]ana|por la tarde|"
                     r"before \d{1,2}(?::\d\d)?\s*(?:am|pm)?|after \d{1,2}(?::\d\d)?\s*(?:am|pm)?|in the morning|in the afternoon)", re.I)
EVITAR = re.compile(r"(no me (?:mandes|mand[eé]s|env[ií]es|copies|incluyas|pongas en copia)|no quiero recibir|don't (?:send|cc|copy) me|do not (?:send|cc|copy) me)\s*([^.;!?]{0,70})", re.I)

def negado(oracion, inicio):
    """«por Slack, no por correo»: la mención precedida de una negación no es una preferencia por ese valor."""
    previo = oracion[max(0, inicio - 16):inicio].lower()
    return bool(re.search(r"\b(no|not|ni|nunca|never|sin)\s+(por|en|v[ií]a|by|on|through|a)?\s*(el|la|los|las)?\s*$", previo))

def turnos_transcripcion(ruta_t):
    txt = open(ruta_t, encoding="utf-8-sig", errors="replace").read()
    norm_md = re.findall(r"(?m)^\*\*(?:\[(\d\d:\d\d:\d\d)\]\s*)?([^:*\n]{1,60}):\*\*\s*(.+)$", txt)
    if norm_md:     # salida normalizada de transcripcion.py
        return [{"ini": ts, "hablante": h.strip(), "texto": x.strip()} for ts, h, x in norm_md]
    sys.path.insert(0, REUNIONES)
    try: import transcripcion as T
    except ImportError: sys.exit("No se encontró pm-reuniones/scripts/transcripcion.py junto a esta skill.")
    crudos = T.parse_vtt_srt(txt) if "-->" in txt else T.parse_txt(txt)
    return [{"ini": T.fmt(x["ini"]) if x.get("ini") is not None else "", "hablante": x["hablante"], "texto": x["texto"]} for x in crudos]

def proponer(proyecto, ruta_t, mapa_txt="", fecha=None, fuente=None, vigencia_dias=180):
    fecha = fecha or datetime.date.today().isoformat()
    sts = leer(proyecto, "stakeholders")
    mapa = {}
    for par in (mapa_txt or "").split(";"):
        if "=" in par:
            k, v = par.split("=", 1); mapa[norm(k)] = v.strip()
    turnos = turnos_transcripcion(ruta_t)
    hablantes = {}
    for x in turnos: hablantes.setdefault(x["hablante"], 0); hablantes[x["hablante"]] += len(x["texto"].split())
    asignados, sin = {}, []
    for h in hablantes:
        sid = mapa.get(norm(h))
        if not sid:
            s = resolver_st(proyecto, h, sts)
            if not s:   # nombre de pila único
                cand = [z for z in sts if norm(z.get("nombre")).split(" ")[:1] == norm(h).split(" ")[:1]] if norm(h) else []
                s = cand[0] if len(cand) == 1 and len(norm(h).split()) == 1 else None
            sid = s["id"] if s else ""
        if sid and not any(z["id"] == sid for z in sts):
            sys.exit(t(f"--mapa apunta a {sid}, que no existe en stakeholders.csv", f"--mapa points to {sid}, which does not exist"))
        (asignados.__setitem__(h, sid) if sid else sin.append(h))
    existentes = {(p.get("stakeholder_id"), p.get("dimension"), p.get("valor")) for p in leer(proyecto, "preferencias") if p.get("estado") in ("propuesta", "confirmada")}
    propuestas, vistos = [], set()
    fuente_v = fuente or os.path.relpath(ruta_t, proyecto)
    vig = (datetime.date.fromisoformat(fecha) + datetime.timedelta(days=vigencia_dias)).isoformat()
    for x in turnos:
        sid = asignados.get(x["hablante"])
        if not sid: continue
        for oracion in re.split(r"(?<=[.!?])\s+", x["texto"]):
            if not PRIMERA_PERSONA.search(oracion): continue
            hallados = []
            for dim, val, rx in PATRONES:
                ms = [m for m in re.finditer(rx, oracion, re.I) if not negado(oracion, m.start())]
                if ms: hallados.append((dim, val))
            m = HORARIO.search(oracion)
            if m: hallados.append(("horario", m.group(1).lower()))
            m = EVITAR.search(oracion)
            if m: hallados.append(("evitar", (m.group(1) + " " + m.group(2)).strip().rstrip(",").lower()))
            # 'evitar' anula canal/formato de la misma oración ("no me mandes correos" no es preferencia por correo)
            if any(d == "evitar" for d, _ in hallados): hallados = [hv for hv in hallados if hv[0] in ("evitar", "horario")]
            for dim, val in hallados:
                k = (sid, dim, val)
                if k in vistos or k in existentes: continue
                vistos.add(k)
                propuestas.append({"stakeholder_id": sid, "hablante": x["hablante"], "dimension": dim, "valor": val, "procedencia": "declarado",
                                   "evidencia": f"\"{oracion.strip()[:220]}\"" + (f" [{x['ini']}]" if x.get("ini") else ""),
                                   "fuente": fuente_v,
                                   "fecha": fecha, "vigencia_hasta": vig})
    total = sum(hablantes.values()) or 1
    participacion = [{"hablante": h, "stakeholder_id": asignados.get(h, ""), "pct_palabras": round(100 * n / total, 1)} for h, n in sorted(hablantes.items(), key=lambda kv: -kv[1])]
    return propuestas, sin, participacion

# ------------------------------------------------------------------ estereotipos
def sugerir_estereotipos(proyecto, corte=None, medio="alto"):
    sts = leer(proyecto, "stakeholders"); ets = leer(proyecto, "estereotipos"); cache = {"et": {x["id"]: x for x in ets}, "pf": leer(proyecto, "preferencias"), "estado": estado_json(proyecto)}
    grupos, asignar = {}, []
    for s in sts:
        pf = perfil(proyecto, s, corte, medio, cache)
        d = pf["dimensiones"]
        firma = (pf["cuadrante"], d["canal"]["valor"], d["formato"]["valor"], d["nivel_detalle"]["valor"])
        tiene_pf = any(v["fuente"].startswith("PF-") for v in d.values())
        if not s.get("estereotipo") and tiene_pf: grupos.setdefault(firma, []).append(s["id"])
        if not s.get("estereotipo"):
            mejor, score = None, 0
            for et in ets:
                if et.get("estado") == "retirado": continue
                sc = sum(1 for k, i in (("cuadrante", 0), ("canal", 1), ("formato", 2), ("nivel_detalle", 3)) if et.get(k) and et.get(k) == firma[i])
                if sc > score: mejor, score = et, sc
            if mejor and score >= 2: asignar.append({"stakeholder_id": s["id"], "estereotipo": mejor["id"], "nombre": mejor["nombre"], "coincidencias": score})
    nuevos = [{"cuadrante": f[0], "canal": f[1], "formato": f[2], "nivel_detalle": f[3], "miembros": m} for f, m in grupos.items() if len(m) >= 2]
    return nuevos, asignar

# ------------------------------------------------------------------ audiencia y plan de envío (lo consume envios.py)
def resolver_audiencia(proyecto, spec, medio="alto"):
    sts = leer(proyecto, "stakeholders"); por_id = {s["id"]: s for s in sts}; sel, errores = [], []
    def add(s):
        if s and s not in sel: sel.append(s)
    raci_f = leer(proyecto, "raci")
    toks = [x.strip() for x in (spec or "").split(",") if x.strip()]
    excluir = [x[1:].strip() for x in toks if x[:1] in ("-", "!")]
    for x in excluir:
        if x not in por_id: errores.append(t(f"exclusión de {x}: no existe", f"exclusion of {x}: does not exist"))
    for tok in [x for x in toks if x[:1] not in ("-", "!")]:
        if tok == "todos" or tok == "all":
            for s in sts: add(s)
        elif re.match(r"^ST-\d{3,}$", tok):
            add(por_id.get(tok)) if tok in por_id else errores.append(t(f"{tok} no existe", f"{tok} does not exist"))
        elif tok.startswith("cuadrante:"):
            c = tok.split(":", 1)[1]
            if c not in CUADRANTES: errores.append(t(f"cuadrante desconocido: {c}", f"unknown quadrant: {c}")); continue
            for s in sts:
                if cuadrante(s, medio) == c: add(s)
        elif tok.startswith("estereotipo:"):
            et = tok.split(":", 1)[1]
            if et not in {x["id"] for x in leer(proyecto, "estereotipos")}: errores.append(t(f"estereotipo inexistente: {et}", f"unknown stereotype: {et}")); continue
            for s in sts:
                if s.get("estereotipo") == et: add(s)
        elif tok.startswith("raci:"):
            partes = tok.split(":")
            if len(partes) < 2: errores.append(tok); continue
            el = partes[1]; roles = set(partes[2]) if len(partes) > 2 and partes[2] else set("RACI")
            filas = [f for f in raci_f if f.get("elemento") == el]
            if not filas: errores.append(t(f"sin filas RACI para {el}", f"no RACI rows for {el}")); continue
            for f in filas:
                if f.get("rol") in roles: add(por_id.get(f.get("stakeholder_id")))
        elif tok.startswith("rol:"):
            txt = norm(tok.split(":", 1)[1])
            for s in sts:
                if txt and txt in norm(s.get("rol_proyecto", "") + " " + s.get("rol_organizacion", "")): add(s)
        else: errores.append(t(f"token de audiencia no reconocido: {tok}", f"unrecognised audience token: {tok}"))
    sel = [s for s in sel if s["id"] not in excluir]
    return sel, errores

def slug(x):
    t_ = unicodedata.normalize("NFKD", x or "").encode("ascii", "ignore").decode().lower()   # sin el recorte de "Rol: Nombre" de norm()
    return re.sub(r"[^a-z0-9]+", "-", t_).strip("-")[:40].strip("-") or "comunicado"

MODO_POR_CANAL = {"correo": "smtp|eml|mcp", "slack": "slack-webhook|mcp", "teams": "teams-webhook|mcp"}

def plan_envio(proyecto, tema, audiencia, proposito="comunicado", base=None, agrupar=False, fecha=None, medio="alto"):
    fecha = fecha or datetime.date.today().isoformat()
    sel, errores = resolver_audiencia(proyecto, audiencia, medio)
    if errores: sys.exit(t("Audiencia inválida: ", "Invalid audience: ") + "; ".join(errores))
    if not sel: sys.exit(t("La audiencia no incluye a ningún interesado.", "The audience selects no stakeholder."))
    cache = {"et": {x["id"]: x for x in leer(proyecto, "estereotipos")}, "pf": leer(proyecto, "preferencias"), "estado": estado_json(proyecto)}
    carpeta = ruta(proyecto, "03-control", "comunicaciones", f"{fecha}-{slug(tema)}")
    if os.path.exists(ruta(carpeta, "plan-envio.csv")): sys.exit(t(f"Ya existe {os.path.relpath(carpeta, proyecto)}: usar otro tema o fecha.", f"{carpeta} already exists"))
    os.makedirs(carpeta, exist_ok=True)
    filas, avisos = [], []
    for s in sel:
        pf = perfil(proyecto, s, fecha, medio, cache); d = {k: v["valor"] for k, v in pf["dimensiones"].items()}
        canal = d["canal"] or "correo"
        if canal in ("correo", "slack", "teams") and not pf["destino"]:
            avisos.append(t(f"{s['id']} {s.get('nombre','')}: canal {canal} sin destino ({'correo' if canal == 'correo' else 'usuario_chat'} vacío en stakeholders.csv)", f"{s['id']}: channel {canal} without destination"))
        if canal not in ("correo", "slack", "teams"):
            avisos.append(t(f"{s['id']} {s.get('nombre','')}: canal preferido «{canal}» no es electrónico: entregarlo por esa vía y registrarlo con envios.py registrar --modo manual",
                            f"{s['id']}: preferred channel «{canal}» is not electronic; deliver it and record with envios.py registrar --modo manual"))
        if pf["vencidas"]: avisos.append(t(f"{s['id']}: preferencias vencidas sin aplicar ({', '.join(pf['vencidas'])}); revalidar", f"{s['id']}: expired preferences not applied"))
        if d.get("evitar"): avisos.append(t(f"{s['id']}: pidió evitar «{d['evitar']}»; revisar si este envío corresponde", f"{s['id']}: asked to avoid «{d['evitar']}»"))
        filas.append({"stakeholder_id": s["id"], "nombre": s.get("nombre", ""), "cuadrante": pf["cuadrante"], "canal": canal, "destino": pf["destino"],
                      "modos": MODO_POR_CANAL.get(canal, "manual"), "formato": d["formato"], "nivel_detalle": d["nivel_detalle"], "idioma": d["idioma"],
                      "registro": d["registro"], "horario": d["horario"], "estereotipo": s.get("estereotipo", "")})
    grupos = {}
    for f in filas:
        k = (f["canal"], f["formato"], f["nivel_detalle"], f["idioma"], f["registro"]) if agrupar else (f["stakeholder_id"],)
        grupos.setdefault(k, []).append(f)
    cuerpo_base = open(base, encoding="utf-8").read() if base else ""
    for n, (k, fs) in enumerate(grupos.items(), 1):
        f0 = fs[0]; nombre = f"mensaje-{n:02d}-{f0['canal']}-{'-'.join(x['stakeholder_id'].lower() for x in fs)[:40]}.md"
        for f in fs: f["archivo"] = nombre
        guia = t(f"Redactar para {', '.join(x['nombre'] or x['stakeholder_id'] for x in fs)}: canal {f0['canal']}, formato {f0['formato'] or '-'}, nivel {f0['nivel_detalle'] or '-'}, "
                 f"idioma {f0['idioma'] or '-'}, registro {f0['registro'] or '-'}. Cuadrante {f0['cuadrante'] or '-'}: {ESTRATEGIA.get(f0['cuadrante'], {}).get('estrategia', ('', ''))[0]}",
                 f"Write for {', '.join(x['nombre'] or x['stakeholder_id'] for x in fs)}: channel {f0['canal']}, format {f0['formato'] or '-'}, level {f0['nivel_detalle'] or '-'}, language {f0['idioma'] or '-'}.")
        fm = ["---", "tipo: comunicado-personalizado", f"proposito: {proposito}", f'tema: "{tema}"', f"para: {';'.join(x['stakeholder_id'] for x in fs)}",
              f"canal: {f0['canal']}", f"destino: {';'.join(x['destino'] for x in fs if x['destino'])}", f"formato: {f0['formato']}",
              f"nivel_detalle: {f0['nivel_detalle']}", f"idioma: {f0['idioma']}", f"registro: {f0['registro']}", f"horario: \"{'; '.join(sorted({x['horario'] for x in fs if x['horario']}))}\"",
              f'asunto: "{tema}"', "estado: borrador", 'aprobado_por: ""', f"origen: {os.path.relpath(base, proyecto) if base else ''}", "---", ""]
        texto = "\n".join(fm) + f"<!-- {guia} -->\n\n" + (t("## Contenido base (adaptar al perfil y borrar este título)\n\n", "## Base content (adapt and remove this heading)\n\n") + cuerpo_base if cuerpo_base else t("[redactar el mensaje]\n", "[write the message]\n"))
        open(ruta(carpeta, nombre), "w", encoding="utf-8").write(texto)
    cols = ["stakeholder_id", "nombre", "cuadrante", "estereotipo", "canal", "destino", "modos", "formato", "nivel_detalle", "idioma", "registro", "horario", "archivo"]
    with open(ruta(carpeta, "plan-envio.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    return carpeta, filas, avisos

# ------------------------------------------------------------------ reporte HTML (matriz, estrategias, RACI, perfiles, integridad)
CSS = """
:root{--surface:#fcfcfb;--surface-2:#f3f2ef;--ink:#0b0b0b;--ink-2:#52514e;--muted:#7b7a75;--rule:#e2e1dc;
--q1:#2a78d6;--q2:#eb6834;--q3:#1baf7a;--q4:#8a8984;--a:#184f95;--r:#3987e5;--c:#9ec5f4;--i:#e7f0fc;--on-dark:#ffffff;--on-light:#0b0b0b;
--good:#0ca30c;--warning:#b77d00;--critical:#d03b3b}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--surface:#1a1a19;--surface-2:#242422;--ink:#f0efec;--ink-2:#c3c2b7;--muted:#9a998f;--rule:#3a3a37;
--q1:#3987e5;--q2:#d95926;--q3:#199e70;--q4:#77766f;--a:#9ec5f4;--r:#3987e5;--c:#1c5cab;--i:#103a6b;--on-dark:#0b0b0b;--on-light:#f0efec;--warning:#fab219}}
:root[data-theme="dark"]{--surface:#1a1a19;--surface-2:#242422;--ink:#f0efec;--ink-2:#c3c2b7;--muted:#9a998f;--rule:#3a3a37;
--q1:#3987e5;--q2:#d95926;--q3:#199e70;--q4:#77766f;--a:#9ec5f4;--r:#3987e5;--c:#1c5cab;--i:#103a6b;--on-dark:#0b0b0b;--on-light:#f0efec;--warning:#fab219}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:36px 0 10px;border-bottom:1px solid var(--rule);padding-bottom:6px}
.sub{color:var(--ink-2);margin:0 0 8px}.restr{display:inline-block;border:1px solid var(--critical);color:var(--critical);padding:2px 8px;border-radius:4px;font-size:13px}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{border-bottom:1px solid var(--rule);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--ink-2);font-weight:600;background:var(--surface-2)}td.c{text-align:center;font-weight:700;min-width:34px}
.A{background:var(--a);color:var(--on-dark)}.R{background:var(--r);color:var(--on-dark)}.C{background:var(--c);color:var(--on-light)}.I{background:var(--i);color:var(--on-light)}
.leg{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;color:var(--ink-2);margin:8px 0}.leg span{display:inline-flex;align-items:center;gap:6px}
.sw{display:inline-block;width:22px;height:16px;border-radius:3px;text-align:center;font-size:11px;font-weight:700;line-height:16px}
.grid4{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}.card{background:var(--surface-2);border-radius:8px;padding:12px 14px;border-left:4px solid var(--q4)}
.card h3{margin:0 0 4px;font-size:15px}.card p{margin:4px 0;color:var(--ink-2);font-size:13.5px}.chips{margin-top:6px;font-size:13px}
.sev{font-weight:700}.sev.ERROR{color:var(--critical)}.sev.AVISO{color:var(--warning)}.sev.INFO{color:var(--ink-2)}.ok{color:var(--good);font-weight:700}
svg text{fill:var(--ink)}svg .muted{fill:var(--ink-2)}.fuente{color:var(--muted);font-size:12px}.dim{color:var(--ink-2);font-size:12px}
footer{margin-top:40px;color:var(--muted);font-size:12px}
"""

def svg_matriz(cuads, medio):
    """Cuadrícula 2×2 (poder vertical, interés horizontal) con cada interesado en su banda (alto, medio, bajo)."""
    maxl = 17
    filas_max = max([min(len(v), maxl + 1) for v in cuads.values()] + [3])
    QH = max(150, 76 + filas_max * 18)              # alto de cada cuadrante según su contenido
    W, L, T, PW = 980, 70, 20, 890; PH = 2 * QH; H = PH + 70
    col = {"gestionar-de-cerca": "var(--q1)", "mantener-satisfecho": "var(--q2)", "mantener-informado": "var(--q3)", "monitorear": "var(--q4)"}
    pos_q = {"mantener-satisfecho": (0, 0), "gestionar-de-cerca": (1, 0), "monitorear": (0, 1), "mantener-informado": (1, 1)}
    o = [f'<div class="scroll"><svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{t("Matriz poder/interés", "Power/interest grid")}" style="max-width:{W}px;min-width:680px">']
    for q, (cx, cy) in pos_q.items():
        x, y = L + cx * PW / 2, T + cy * PH / 2
        o.append(f'<rect x="{x + 1}" y="{y + 1}" width="{PW / 2 - 2}" height="{PH / 2 - 2}" rx="6" fill="{col[q]}" fill-opacity="0.10" stroke="{col[q]}" stroke-opacity="0.55"/>')
        o.append(f'<text x="{x + 12}" y="{y + 24}" font-size="15" font-weight="700">{html.escape(ESTRATEGIA[q]["nombre"][IDIOMA == "en"])}</text>')
        o.append(f'<text x="{x + 12}" y="{y + 42}" font-size="12" class="muted">{html.escape(t("Poder ", "Power ") + ESTRATEGIA[q]["poder"] + t(" · Interés ", " · Interest ") + ESTRATEGIA[q]["interes"])}</text>')
        filas = list(cuads[q])
        for k, s in enumerate(filas[:maxl]):
            yy = y + 66 + k * 18; fr = frontera(s)
            etiqueta = f"{s['id']} · {corto(s.get('nombre', ''), 22)}" + (f" · {s.get('poder','?')[0]}/{s.get('interes','?')[0]}" if fr else "")
            tip = html.escape(f"{s['id']} {s.get('nombre','')} — {t('poder', 'power')} {s.get('poder','')}, {t('interés', 'interest')} {s.get('interes','')}" + (t(" (frontera: 'medio' ubicado como ", " (boundary: 'medium' placed as ") + medio + ")" if fr else ""))
            o.append(f'<g><title>{tip}</title><circle cx="{x + 20}" cy="{yy - 4}" r="5" fill="{col[q]}" stroke="var(--surface)" stroke-width="2"' + (' stroke-dasharray="2 2"' if fr else "") + '/>'
                     f'<text x="{x + 32}" y="{yy}" font-size="13">{html.escape(etiqueta)}</text></g>')
        if len(filas) > maxl: o.append(f'<text x="{x + 32}" y="{y + 66 + maxl * 18}" font-size="12" class="muted">+{len(filas) - maxl} {t("más (ver tabla)", "more (see table)")}</text>')
    o.append(f'<line x1="{L}" y1="{T + PH}" x2="{L + PW}" y2="{T + PH}" stroke="var(--ink-2)"/><line x1="{L}" y1="{T}" x2="{L}" y2="{T + PH}" stroke="var(--ink-2)"/>')
    o.append(f'<text x="{L + PW / 2}" y="{T + PH + 36}" font-size="13" text-anchor="middle" class="muted">{t("Interés (involucramiento, preocupación o impacto) →", "Interest (involvement, concern or impact) →")}</text>')
    o.append(f'<text transform="translate(22 {T + PH / 2}) rotate(-90)" font-size="13" text-anchor="middle" class="muted">{t("Poder (autoridad, recursos, aprobar o vetar) →", "Power (authority, resources, approve or veto) →")}</text>')
    o.append(f'<text x="{L + 4}" y="{T + PH + 18}" font-size="11" class="muted">{t("bajo", "low")}</text><text x="{L + PW - 4}" y="{T + PH + 18}" font-size="11" text-anchor="end" class="muted">{t("alto", "high")}</text>')
    o.append("</svg></div>"); return "".join(o)

class HtmlSeguro(str):
    """Fragmento HTML armado por este script (no por datos de los registros): tabla() lo inserta sin escapar."""

def tabla(cab, filas, clases=None):
    # Todo valor se escapa salvo los fragmentos marcados como HtmlSeguro: un dato de un registro que empiece con "<"
    # (nombre, expectativas, asunto, descripción…) no debe convertirse en HTML activo (XSS en el reporte).
    o = ['<div class="scroll"><table><thead><tr>' + "".join(f"<th>{html.escape(str(c))}</th>" for c in cab) + "</tr></thead><tbody>"]
    for i, f in enumerate(filas):
        o.append("<tr>" + "".join(f'<td{(" class=" + chr(34) + html.escape(clases[i][j]) + chr(34)) if clases and clases[i][j] else ""}>{c if isinstance(c, HtmlSeguro) else html.escape(str(c))}</td>' for j, c in enumerate(f)) + "</tr>")
    return "".join(o) + "</tbody></table></div>"

def reporte(proyecto, salida_html=None, salida_md=None, corte=None, restringido=False, medio="alto"):
    corte = corte or datetime.date.today().isoformat(); e = estado_json(proyecto)
    sts = leer(proyecto, "stakeholders"); cuads, sin = matriz(proyecto, medio)
    ids = ids_conocidos(proyecto); por_el, hall_raci = raci(proyecto, medio, ids); integ = integridad(proyecto, corte, medio)
    cache = {"et": {x["id"]: x for x in leer(proyecto, "estereotipos")}, "pf": leer(proyecto, "preferencias"), "estado": e}
    perfiles = [perfil(proyecto, s, corte, medio, cache) for s in sts]
    titulo = t("Interesados: matriz poder/interés, RACI y perfiles de comunicación", "Stakeholders: power/interest grid, RACI and communication profiles")
    H = [f'<!doctype html><html lang="{IDIOMA}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(titulo)}</title><style>{CSS}</style></head><body><main>']
    H.append(f"<h1>{html.escape(titulo)}</h1><p class='sub'>{html.escape(e.get('proyecto', ''))} · {t('corte', 'cut-off')} {html.escape(corte)} · {len(sts)} {t('interesados', 'stakeholders')}"
             + (f" · <span class='restr'>{t('Circulación restringida: incluye valoraciones', 'Restricted: includes assessments')}</span>" if restringido else "") + "</p>")
    # 1 matriz
    H.append(f"<h2>1. {t('Matriz poder/interés', 'Power/interest grid')}</h2><p class='sub'>{t('Poder: autoridad real, control de recursos, capacidad de aprobar presupuestos o vetar decisiones. Interés: grado de involucramiento, preocupación o impacto que el proyecto genera en el actor.', 'Power: real authority, control of resources, ability to approve budgets or veto decisions. Interest: degree of involvement, concern or impact.')} "
             + t(f"Los valores «medio» se ubican del lado «{medio}» y se marcan con borde punteado (frontera).", f"'Medium' values are placed on the '{medio}' side and marked with a dashed ring.") + "</p>")
    H.append(svg_matriz(cuads, medio))
    if sin: H.append(f"<p class='sev AVISO'>{t('Sin ubicar (falta poder o interés)', 'Not placed (missing power or interest)')}: {html.escape(', '.join(s['id'] for s in sin))}</p>")
    # 2 estrategias
    H.append(f"<h2>2. {t('Estrategia por cuadrante', 'Strategy per quadrant')}</h2><div class='grid4'>")
    colq = {"gestionar-de-cerca": "var(--q1)", "mantener-satisfecho": "var(--q2)", "mantener-informado": "var(--q3)", "monitorear": "var(--q4)"}
    for q in CUADRANTES:
        es_ = ESTRATEGIA[q]; d = es_["defecto"]; en = IDIOMA == "en"
        H.append(f"<div class='card' style='border-left-color:{colq[q]}'><h3>{html.escape(es_['nombre'][en])} ({len(cuads[q])})</h3><p><b>{t('Quiénes', 'Who')}:</b> {html.escape(es_['quienes'][en])}</p>"
                 f"<p><b>{t('Estrategia', 'Strategy')}:</b> {html.escape(es_['estrategia'][en])}</p><p><b>{t('Por defecto', 'Default')}:</b> {d['canal']} · {d['formato']} · {d['nivel_detalle']} · {d['frecuencia']}</p>"
                 f"<p><b>RACI {t('típico', 'typical')}:</b> {html.escape(es_['raci'][en])}</p><div class='chips'>{html.escape(', '.join(s['id'] + ' ' + corto(s.get('nombre', '')) for s in cuads[q]) or '—')}</div></div>")
    H.append("</div>")
    # 3 RACI
    H.append(f"<h2>3. {t('Matriz RACI', 'RACI matrix')}</h2>")
    if por_el:
        usados = [s for s in sts if any(x.get("stakeholder_id") == s["id"] for fs in por_el.values() for x in fs)]
        H.append("<div class='leg'>" + "".join(f"<span><i class='sw {r}'>{r}</i>{n}</span>" for r, n in (("R", t("Responsable", "Responsible")), ("A", t("Aprobador", "Accountable")), ("C", t("Consultado", "Consulted")), ("I", t("Informado", "Informed")))) + "</div>")
        filas, clases = [], []
        for el, fs in por_el.items():
            m = {x["stakeholder_id"]: x["rol"] for x in fs}
            tipo = tipo_de(el, next((x.get("tipo_elemento") for x in fs if x.get("tipo_elemento")), ""))
            tit = titulo_de(ids, el, tipo) or next((x.get("descripcion") for x in fs if x.get("descripcion")), "")
            filas.append([el, tipo, tit] + [m.get(s["id"], "") for s in usados]); clases.append(["", "", ""] + [("c " + m[s["id"]]) if s["id"] in m else "c" for s in usados])
        H.append(tabla([t("Elemento", "Item"), t("Tipo", "Type"), t("Descripción", "Description")] + [f"{s['id']} {corto(s.get('nombre', ''), 16)}" for s in usados], filas, clases))
    else: H.append(f"<p class='sub'>{t('Sin filas en raci.csv todavía.', 'No rows in raci.csv yet.')}</p>")
    # 4 perfiles
    H.append(f"<h2>4. {t('Perfiles de comunicación (resueltos)', 'Communication profiles (resolved)')}</h2><p class='sub'>{t('Precedencia: cuadrante → idioma del proyecto → estereotipo → matriz de comunicaciones → preferencias confirmadas vigentes. Entre paréntesis, la procedencia.', 'Precedence: quadrant → project language → stereotype → communications matrix → confirmed current preferences.')}</p>")
    filas = []
    # Seis columnas con dos o tres líneas por celda (dimensión: valor y procedencia) para que la tabla entre en 1.280 px.
    for p in perfiles:
        d = p["dimensiones"]
        def f(k, etq):
            v = d[k]["valor"]
            return (f"<span class='dim'>{html.escape(etq)}</span> " + (f"{html.escape(str(v))} <span class='fuente'>({html.escape(d[k]['fuente'])})</span>" if v else "—")) if k in d else ""
        celda = lambda *xs: HtmlSeguro("<br>".join(x for x in xs if x))
        texto = lambda etq, v: f"<span class='dim'>{html.escape(etq)}</span> {html.escape(str(v or '—'))}"
        filas.append([p["id"] + " " + p["nombre"],
                      celda(html.escape(ESTRATEGIA.get(p["cuadrante"], {}).get("nombre", ("—", "—"))[IDIOMA == "en"]), texto(t("estereotipo", "stereotype"), p["estereotipo"])),
                      celda(f("canal", t("canal", "channel")), f("frecuencia", t("frecuencia", "frequency"))),
                      celda(f("formato", t("formato", "format")), f("nivel_detalle", t("nivel", "level"))),
                      celda(f("idioma", t("idioma", "language")), texto(t("horario", "hours"), d["horario"]["valor"]) + " · " + texto(t("evitar", "avoid"), d["evitar"]["valor"])),
                      celda(texto(t("propuestas", "proposed"), ", ".join(p["pendientes"])) + " · " + texto(t("vencidas", "expired"), ", ".join(p["vencidas"])))])
    H.append(tabla([t("Interesado", "Stakeholder"), t("Cuadrante y estereotipo", "Quadrant and stereotype"), t("Canal y frecuencia", "Channel and frequency"),
                    t("Formato y nivel", "Format and level"), t("Idioma, horario, evitar", "Language, hours, avoid"), t("Preferencias", "Preferences")], filas))
    if restringido:
        H.append(f"<h3>{t('Valoraciones (restringido)', 'Assessments (restricted)')}</h3>")
        H.append(tabla(["ID", t("Nombre", "Name"), t("Actitud", "Attitude"), t("Compromiso actual", "Current engagement"), t("Deseado", "Desired"), t("Expectativas", "Expectations")],
                       [[s["id"], s.get("nombre", ""), s.get("actitud", ""), s.get("nivel_compromiso_actual", ""), s.get("nivel_compromiso_deseado", ""), s.get("expectativas", "")] for s in sts]))
    # 5 estereotipos
    ets = leer(proyecto, "estereotipos")
    H.append(f"<h2>5. {t('Estereotipos', 'Stereotypes')}</h2>")
    H.append(tabla(["ID", t("Nombre", "Name"), t("Cuadrante", "Quadrant"), "Canal", "Formato", t("Nivel", "Level"), t("Frecuencia", "Frequency"), t("Miembros", "Members"), t("Estado", "Status")],
                   [[x["id"], x.get("nombre", ""), x.get("cuadrante", ""), x.get("canal", ""), x.get("formato", ""), x.get("nivel_detalle", ""), x.get("frecuencia", ""),
                     ", ".join(s["id"] for s in sts if s.get("estereotipo") == x["id"]) or "—", x.get("estado", "")] for x in ets]) if ets else f"<p class='sub'>{t('Sin estereotipos (interesados.py estereotipos --semilla crea los seis de la guía de comunicación).', 'No stereotypes yet.')}</p>")
    # 6 vínculos con OKR y especificación
    H.append(f"<h2>6. {t('Vínculos en el ecosistema', 'Links across the ecosystem')}</h2>")
    filas = []
    okrs = okr_filas(proyecto)
    for s in sts:
        n_okr = [f["id"] for f in okrs if (f.get("responsable") or "").strip() in (s["id"],) or norm(f.get("responsable")) == norm(s.get("nombre"))]
        spec = [f"{el}:{x['rol']}" for el, fs in por_el.items() for x in fs if x["stakeholder_id"] == s["id"] and tipo_de(el, x.get("tipo_elemento")) in ("requisito", "epica", "historia")]
        otros = [f"{el}:{x['rol']}" for el, fs in por_el.items() for x in fs if x["stakeholder_id"] == s["id"] and tipo_de(el, x.get("tipo_elemento")) not in ("requisito", "epica", "historia")]
        filas.append([s["id"] + " " + s.get("nombre", ""), ", ".join(n_okr) or "—", ", ".join(spec) or "—", ", ".join(otros) or "—"])
    H.append(tabla([t("Interesado", "Stakeholder"), t("OKR (responsable)", "OKR (owner)"), t("Especificación (PRD, épicas, historias)", "Specification"), t("WBS, KR, decisiones y otros", "WBS, KR, decisions and others")], filas))
    # 7 envíos
    env = leer(proyecto, "envios")
    H.append(f"<h2>7. {t('Envíos registrados', 'Recorded deliveries')}</h2>")
    H.append(tabla(["ID", t("Fecha", "Date"), t("Interesado", "Stakeholder"), "Canal", t("Modo", "Mode"), t("Asunto", "Subject"), t("Estado", "Status")],
                   [[f["id"], f.get("fecha", ""), f.get("stakeholder_id", ""), f.get("canal", ""), f.get("modo", ""), f.get("asunto", ""), f.get("estado", "")] for f in env[-30:]]) if env else f"<p class='sub'>{t('Sin envíos registrados.', 'No deliveries recorded.')}</p>")
    # 8 integridad
    H.append(f"<h2>8. {t('Integridad y calidad de los datos', 'Data integrity and quality')}</h2>")
    H.append(tabla([t("Severidad", "Severity"), t("Código", "Code"), t("Hallazgo", "Finding")], [[HtmlSeguro(f"<span class='sev {html.escape(s)}'>{html.escape(s)}</span>"), c, m] for s, c, m in integ]) if integ else f"<p class='ok'>✓ {t('Sin hallazgos', 'No findings')}</p>")
    H.append(f"<footer>{t('Generado por pm-method · interesados.py. Fuente única: 03-control/registros/stakeholders.csv, raci.csv, estereotipos.csv, preferencias.csv, envios.csv. No contiene inferencias de emociones ni de personalidad.', 'Generated by pm-method · interesados.py. No emotion or personality inference.')}</footer></main></body></html>")
    if salida_html:
        os.makedirs(os.path.dirname(salida_html) or ".", exist_ok=True); open(salida_html, "w", encoding="utf-8").write("".join(H))
    if salida_md:
        M = [f"# {titulo}", "", f"{e.get('proyecto', '')} · {t('corte', 'cut-off')} {corte}", "", f"## 1. {t('Matriz poder/interés', 'Power/interest grid')}", "",
             f"| {t('Cuadrante', 'Quadrant')} | {t('Estrategia', 'Strategy')} | {t('Interesados', 'Stakeholders')} |", "|---|---|---|"]
        for q in CUADRANTES:
            M.append(f"| {ESTRATEGIA[q]['nombre'][IDIOMA == 'en']} | {ESTRATEGIA[q]['estrategia'][IDIOMA == 'en']} | {', '.join(s['id'] + ' ' + s.get('nombre', '') + (' (frontera)' if frontera(s) else '') for s in cuads[q]) or '—'} |")
        M += ["", f"## 2. {t('Matriz RACI', 'RACI matrix')}", ""] + raci_markdown(proyecto, por_el, ids, sts) + ["", f"## 3. {t('Perfiles de comunicación', 'Communication profiles')}", "",
              f"| {t('Interesado', 'Stakeholder')} | Canal | Formato | {t('Nivel', 'Level')} | {t('Frecuencia', 'Frequency')} | {t('Idioma', 'Language')} | {t('Procedencia del canal', 'Channel source')} |", "|---|---|---|---|---|---|---|"]
        for p in perfiles:
            d = p["dimensiones"]; M.append(f"| {p['id']} {p['nombre']} | {d['canal']['valor']} | {d['formato']['valor']} | {d['nivel_detalle']['valor']} | {d['frecuencia']['valor']} | {d['idioma']['valor']} | {d['canal']['fuente']} |")
        M += ["", f"## 4. {t('Integridad', 'Integrity')}", ""] + [f"- {s} {c}: {m}" for s, c, m in integ] + ([t("- Sin hallazgos.", "- No findings.")] if not integ else [])
        os.makedirs(os.path.dirname(salida_md) or ".", exist_ok=True); open(salida_md, "w", encoding="utf-8").write("\n".join(M) + "\n")
    return {"cuadrantes": {q: [s["id"] for s in cuads[q]] for q in CUADRANTES}, "sin_ubicar": [s["id"] for s in sin], "elementos_raci": len(por_el), "hallazgos": len(integ)}

def raci_markdown(proyecto, por_el, ids, sts):
    usados = [s for s in sts if any(x.get("stakeholder_id") == s["id"] for fs in por_el.values() for x in fs)]
    if not por_el: return [t("Sin filas en raci.csv.", "No rows in raci.csv.")]
    L = ["| " + t("Elemento", "Item") + " | " + t("Descripción", "Description") + " | " + " | ".join(f"{s['id']} {corto(s.get('nombre', ''), 16)}" for s in usados) + " |",
         "|---|---|" + "---|" * len(usados)]
    for el, fs in por_el.items():
        m = {x["stakeholder_id"]: x["rol"] for x in fs}
        tit = titulo_de(ids, el, tipo_de(el, next((x.get("tipo_elemento") for x in fs if x.get("tipo_elemento")), ""))) or next((x.get("descripcion") for x in fs if x.get("descripcion")), "")
        L.append(f"| {el} | {tit} | " + " | ".join(m.get(s["id"], "") for s in usados) + " |")
    return L + ["", t("Leyenda: R responsable · A aprobador (uno por elemento) · C consultado · I informado.", "Legend: R responsible · A accountable (one per item) · C consulted · I informed.")]

# ------------------------------------------------------------------ personas de usuario × capacidades (personas.csv, PU-###)
# Una persona es un arquetipo de quien usa, pide o se beneficia de una capacidad (PMBOK: análisis de usuarios al elicitar
# requisitos; PRINCE2: el usuario sénior representa a los usuarios y especifica resultados y beneficios). No es un
# interesado (persona u organización real del maestro) ni un estereotipo de comunicación (estereotipos.csv).
ROLES_PERSONA = (("solicita", "solicitante", "S"), ("usa", "usuario", "U"), ("beneficia", "beneficiario", "B"))
MOSCOW = ("must", "should", "could", "wont")
ALIAS_MOSCOW = {"must": "must", "m": "must", "must-have": "must", "imprescindible": "must", "obligatorio": "must", "1": "must",
                "should": "should", "s": "should", "should-have": "should", "deseable": "should", "2": "should",
                "could": "could", "c": "could", "could-have": "could", "opcional": "could", "3": "could",
                "wont": "wont", "won't": "wont", "w": "wont", "wont-have": "wont", "no-ahora": "wont", "excluido": "wont"}
POR_CONFIRMAR_P = re.compile(r"^\s*$|\[por confirmar\]|\[to be confirmed\]|\[verificar\]", re.I)

def moscow(v):
    """Prioridad MoSCoW canónica (must|should|could|wont) o '' si el valor no es MoSCoW."""
    x = unicodedata.normalize("NFKD", (v or "").strip().lower()).encode("ascii", "ignore").decode().replace(" ", "-")
    return ALIAS_MOSCOW.get(x, "")

def etq_moscow(k): return {"must": "Must", "should": "Should", "could": "Could", "wont": "Won't"}.get(k, t("sin prioridad", "no priority"))

def orden_id(x): return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", str(x))]

def ids_lista(v):
    """Ids de una celda (separados por «;», «,» o espacios), sin repetir y en orden."""
    out = []
    for x in re.split(r"[;,\s]+", v or ""):
        if x and x not in out: out.append(x)
    return out

def vista_spec(proyecto):
    """{id: {tipo, titulo, prioridad}} de requisitos, épicas e historias vía la fachada (solo lectura) y sus relaciones
    {"abajo": épica → historias y requisitos que cubre, historia → requisitos que realiza (con trazas por épica, los de su
    épica); "arriba": la inversa}. Prioridad: MoSCoW del requisito (requisitos.md) o de la historia (backlog.csv: moscow); el requisito o la épica
    sin prioridad propia toma la más alta de sus historias."""
    try:
        sys.path.insert(0, NUCLEO); import especificacion as SP
        idx, _ = SP.obtener(proyecto)
    except BaseException:
        return {}, {"abajo": {}, "arriba": {}}
    el, rel = {}, {"abajo": {}, "arriba": {}}
    def unir(sup, inf):
        if sup and inf and sup != inf: rel["abajo"].setdefault(sup, set()).add(inf); rel["arriba"].setdefault(inf, set()).add(sup)
    mejor = lambda xs: next((m for m in MOSCOW if m in xs), "")
    for h in idx.get("historias", []):
        gob = h.get("gobierno") or {}
        tipo = "epica" if re.match(r"^E-?\d+$", h["id"]) else "historia"
        el[h["id"]] = {"tipo": tipo, "titulo": h.get("titulo", ""), "prioridad": moscow(gob.get("moscow")) or moscow(gob.get("prioridad"))}
        if h.get("epica") and h["epica"] != h["id"]: unir(h["epica"], h["id"])
        for r in h.get("refs", []): unir(h["id"], r)
    for ep in idx.get("epicas", []):
        el.setdefault(ep["id"], {"tipo": "epica", "titulo": ep.get("titulo", ""), "prioridad": ""})
        for x in ep.get("historias", []) + ep.get("refs", []): unir(ep["id"], x)
    for q in idx.get("requisitos", []):
        if q.get("tipo") not in ("REQ", "FR", "NFR"): continue
        el[q["id"]] = {"tipo": "requisito", "titulo": q.get("titulo", ""), "prioridad": moscow(q.get("prioridad"))}
        for ep in q.get("epicas", []): unir(ep, q["id"])
        for h in q.get("historias", []): unir(h, q["id"])   # con trazas por épica (BMAD), las historias de la épica
    for x, d in el.items():
        if d["prioridad"] or d["tipo"] not in ("requisito", "epica"): continue
        hs = {v for v in rel["arriba"].get(x, set()) | rel["abajo"].get(x, set()) if el.get(v, {}).get("tipo") == "historia"}
        d["prioridad"] = mejor({el[v]["prioridad"] for v in hs if v in el})
    for x in [x for x, d in el.items() if d["tipo"] == "requisito"]:   # requisito → épica de sus historias (sin BMAD)
        for h in [v for v in rel["arriba"].get(x, set()) if el.get(v, {}).get("tipo") == "historia"]:
            for ep in rel["arriba"].get(h, ()): unir(ep, x)
    return el, rel

def beneficios_caso(proyecto):
    """Beneficios B-## y des-beneficios DB-## del business case y del enfoque de beneficios: {id: {titulo, refs}} y si hay fuente."""
    e = estado_json(proyecto); out = {}; hay = False
    for clave, defecto in (("business-case", "00-direccion/business-case.md"), ("enfoque-beneficios", "00-direccion/enfoque-beneficios.md")):
        p = ruta(proyecto, (e.get("artefactos", {}).get(clave) or {}).get("ruta") or defecto)
        if not os.path.exists(p): continue
        hay = True
        for l in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"^\|\s*((?:B|DB)-\d+)\s*\|\s*([^|]*)\|", l)
            if m and "{{" not in l:
                b = out.setdefault(m.group(1), {"titulo": m.group(2).strip()[:90], "refs": set()})
                b["refs"] |= set(re.findall(r"\b(?:SM-C?\d+|KR-[\w.]+)\b", l))
    return out, hay

def cubre(p, rel):
    """Ids que la persona cita (solicita, usa, beneficia) y los que cubre: los citados, la épica de cada uno y, hacia abajo,
    lo que contiene cada citado (épica → historias y requisitos; historia → requisitos que realiza)."""
    s = set()
    for col, _, _ in ROLES_PERSONA: s |= set(ids_lista(p.get(col)))
    c = set(s) | {v for x in s for v in rel["arriba"].get(x, ())}
    pend = list(s)
    while pend:
        for v in rel["abajo"].get(pend.pop(), ()):
            if v not in c: c.add(v); pend.append(v)
    return s, c

def palabras(x):
    return re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", x or "").encode("ascii", "ignore").decode().lower())

def coincide(nombre, texto):
    """¿El texto de un recorrido nombra a la persona? (nombre completo contenido como palabras, sin acentos ni mayúsculas)."""
    n, tx = " ".join(palabras(nombre)), " ".join(palabras(texto))
    return bool(n) and f" {n} " in f" {tx} "

def personas_activas(proyecto): return [p for p in leer(proyecto, "personas") if p.get("estado") != "retirada"]

def controles_personas(proyecto):
    """STK-13…16 y STK-09 sobre personas.csv (solo si el registro existe). Lista de (severidad, código, mensaje)."""
    if not os.path.exists(E.ruta_registro(proyecto, "personas")): return []
    h = []; pers = personas_activas(proyecto); el, rel = vista_spec(proyecto); ids = ids_conocidos(proyecto); bens, hay_ben = beneficios_caso(proyecto)
    existe = lambda x: x in ids["spec"] or x in ids["backlog"] or x in ids["wbs"] or x in el
    cubiertos = set()
    for p in pers:
        pid = f"{p['id']} {p.get('nombre', '')}"
        s, c = cubre(p, rel); cubiertos |= c
        if not s: h.append(("AVISO", "STK-14", t(f"Persona {pid}: sin capacidades (no solicita, usa ni se beneficia de ningún requisito, épica, historia o producto)", f"Persona {pid}: no capabilities mapped")))
        if not p.get("fuente"): h.append(("AVISO", "STK-15", t(f"Persona {pid}: sin fuente (entrevista, bmad-uj, encuesta, observacion, documento o supuesto)", f"Persona {pid}: no source")))
        elif p["fuente"] != "supuesto" and POR_CONFIRMAR_P.search(p.get("evidencia") or ""):
            h.append(("AVISO", "STK-15", t(f"Persona {pid}: fuente {p['fuente']} sin evidencia (cita, archivo o UJ-n)", f"Persona {pid}: source {p['fuente']} without evidence")))
        for x in sorted(s):
            if not existe(x): h.append(("AVISO", "STK-09", t(f"Persona {pid}: cita {x}, que no existe en la especificación, el backlog ni la WBS", f"Persona {pid}: cites {x}, not found in the specification, backlog or WBS")))
        for b in ids_lista(p.get("beneficios")):
            if not re.match(r"^(B|DB)-\d+$", b) or (hay_ben and b not in bens):
                h.append(("AVISO", "STK-09", t(f"Persona {pid}: beneficio {b} no declarado en el business case ni en el enfoque de beneficios", f"Persona {pid}: benefit {b} not declared in the business case")))
    for x, d in sorted(el.items(), key=lambda kv: orden_id(kv[0])):
        if d["prioridad"] == "must" and d["tipo"] in ("requisito", "epica") and x not in cubiertos:
            h.append(("AVISO", "STK-13", t(f"{x} ({d['tipo']} Must) sin persona que lo pida, lo use o se beneficie: {recortar_p(d['titulo'])}", f"{x} (Must {d['tipo']}) has no persona: {recortar_p(d['titulo'])}")))
    ids_pu = {p["id"] for p in pers}
    for rj in sorted(glob.glob(ruta(proyecto, "02-planificacion", "mapas", "recorrido-*.json"))):
        try: d = json.load(open(rj, encoding="utf-8"))
        except (OSError, ValueError): continue
        nom = os.path.basename(rj); pid = (d.get("persona_id") or "").strip()
        if pid and pid not in ids_pu:
            h.append(("AVISO", "STK-16", t(f"{nom}: persona_id {pid} no existe en personas.csv o está retirada", f"{nom}: persona_id {pid} not in personas.csv or retired")))
        elif not pid and not POR_CONFIRMAR_P.search(str(d.get("persona") or "")) and not any(coincide(p.get("nombre"), d.get("persona")) for p in pers):
            h.append(("AVISO", "STK-16", t(f"{nom}: la persona «{recortar_p(d.get('persona'), 60)}» no está en personas.csv", f"{nom}: persona «{recortar_p(d.get('persona'), 60)}» is not in personas.csv")))
    return h

def recortar_p(x, n=70):
    x = re.sub(r"\s+", " ", str(x or "")).strip()
    return x if len(x) <= n else x[:n - 1].rstrip() + "…"

def mapa_personas(proyecto):
    """Mapa capacidad × persona con el rol de cada una (solicitante, usuario, beneficiario) y la prioridad MoSCoW."""
    pers = personas_activas(proyecto); el, rel = vista_spec(proyecto); ids = ids_conocidos(proyecto)
    filas, cubiertos = {}, set()
    for p in pers:
        cubiertos |= cubre(p, rel)[1]
        for col, rol, _ in ROLES_PERSONA:
            for x in ids_lista(p.get(col)):
                f = filas.setdefault(x, {"id": x, "titulo": (el.get(x) or {}).get("titulo") or ids["tit"]["wbs"].get(x, "") or ids["tit"]["backlog"].get(x, ""),
                                         "tipo": (el.get(x) or {}).get("tipo") or ("producto" if x in ids["wbs"] else ""),
                                         "prioridad": (el.get(x) or {}).get("prioridad", ""), "personas": {}})
                f["personas"].setdefault(p["id"], []).append(rol)
    orden = {m: i for i, m in enumerate(MOSCOW)}
    caps = sorted(filas.values(), key=lambda f: (orden.get(f["prioridad"], 9), orden_id(f["id"])))
    sin = [{"id": x, "tipo": d["tipo"], "titulo": d["titulo"]} for x, d in sorted(el.items(), key=lambda kv: orden_id(kv[0]))
           if d["prioridad"] == "must" and d["tipo"] in ("requisito", "epica") and x not in cubiertos]
    return {"personas": [{"id": p["id"], "nombre": p.get("nombre", "")} for p in pers], "capacidades": caps, "must_sin_persona": sin}

def priorizacion_personas(proyecto):
    """Por persona: capacidades citadas por prioridad MoSCoW y por rol, y beneficios vinculados (para priorizar y graficar)."""
    m = mapa_personas(proyecto); bens, _ = beneficios_caso(proyecto); sts = leer(proyecto, "stakeholders")
    por_cap = {f["id"]: f for f in m["capacidades"]}; out = []
    for p in personas_activas(proyecto):
        mias = [f for f in m["capacidades"] if p["id"] in f["personas"]]
        st = resolver_st(proyecto, p.get("stakeholder_id", ""), sts) if p.get("stakeholder_id") else None
        out.append({"id": p["id"], "nombre": p.get("nombre", ""), "fuente": p.get("fuente", ""),
                    "representante": {"id": st["id"], "nombre": st.get("nombre", "")} if st else None,
                    "por_prioridad": {k or "sin": sum(1 for f in mias if f["prioridad"] == k) for k in MOSCOW + ("",)},
                    "por_rol": {rol: sum(1 for f in mias if rol in f["personas"][p["id"]]) for _, rol, _ in ROLES_PERSONA},
                    "capacidades": [{"id": f["id"], "prioridad": f["prioridad"], "roles": f["personas"][p["id"]]} for f in mias],
                    "beneficios": [{"id": b, "titulo": (bens.get(b) or {}).get("titulo", "")} for b in ids_lista(p.get("beneficios"))]})
    out.sort(key=lambda x: tuple(-x["por_prioridad"][k] for k in MOSCOW) + (x["id"],))
    return {"personas": out, "must_sin_persona": [x["id"] for x in m["must_sin_persona"]], "capacidades": len(por_cap)}

def candidatos_personas(proyecto, desde="auto"):
    """Personas candidatas (no registra nada): desde los recorridos UJ-n de BMAD (solo lectura) y desde los artefactos del
    proyecto (recorridos de pm-mapas-estrategicos e historias «Como <rol>…» del backlog). El texto citado es dato de la fuente."""
    e = estado_json(proyecto); con_bmad = e.get("integraciones", {}).get("especificacion") == "bmad"
    if desde == "bmad" and not con_bmad: sys.exit(t("Este proyecto no usa BMAD como especificación (estado.json.integraciones.especificacion); usar --desde artefactos.", "This project does not use BMAD; use --desde artefactos."))
    bens, _ = beneficios_caso(proyecto); sts = leer(proyecto, "stakeholders"); out = {}
    ben_de = lambda kpi: sorted(b for b, d in bens.items() if d["refs"] & set(kpi))
    cabeza = lambda x: recortar_p(re.split(r"[,(;:]", x or "")[0], 60)
    def add(nombre, **campos):
        if not nombre: return
        c = out.setdefault(norm(nombre), {"nombre": nombre, "descripcion": "", "objetivo": "", "dolores": "", "contexto_uso": "", "fuente": "",
                                          "evidencia": [], "usa": [], "beneficios": [], "origen": []})
        for k, v in campos.items():
            if isinstance(v, list): c[k] += [x for x in v if x not in c[k]]
            elif v and not c[k]: c[k] = v
    if desde in ("auto", "bmad") and con_bmad:
        try:
            sys.path.insert(0, os.path.normpath(os.path.join(AQUI, "..", "..", "pm-bmad-puente", "scripts"))); import bmad as B
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()): ujs = B.recorridos(B.inventario(B.detectar_bmad(proyecto, None, e)))
        except BaseException as x:
            sys.exit(t(f"No se pudieron leer los recorridos de BMAD: {x}", f"Could not read the BMAD journeys: {x}"))
        for u in ujs:
            per = u.get("persona") or u.get("titulo", "")
            resto = recortar_p(per[len(re.split(r"[,(;:]", per)[0]):].lstrip(" ,;:("), 200)
            add(cabeza(per), descripcion=resto, objetivo=recortar_p(u.get("titulo"), 120), contexto_uso=recortar_p(u.get("entrada"), 160), fuente="bmad-uj",
                evidencia=[f"{u['id']} ({os.path.basename(u['fuente'])}:{u['linea']})"], usa=u.get("frs", []) + u.get("frs_seccion", []),
                beneficios=ben_de(u.get("kpi", [])), origen=[u["id"]])
    if desde in ("auto", "artefactos"):
        for rj in sorted(glob.glob(ruta(proyecto, "02-planificacion", "mapas", "recorrido-*.json"))):
            try: d = json.load(open(rj, encoding="utf-8"))
            except (OSError, ValueError): continue
            per = str(d.get("persona") or "")
            if POR_CONFIRMAR_P.search(per): continue
            pasos = [p_ for et in d.get("etapas") or [] for p_ in et.get("pasos") or []]
            fuentes = " ".join(str(p_.get("fuente_emocion") or "") for p_ in pasos).lower()
            fuente = next((f for f, rx in (("entrevista", r"entrevista|interview"), ("encuesta", r"encuesta|survey"),
                                           ("observacion", r"observ|m[eé]trica|metric|registro")) if re.search(rx, fuentes)),
                          "bmad-uj" if any(re.match(r"^UJ-\d+$", str(r)) for r in d.get("refs") or []) else "supuesto")
            dolores = "; ".join(dict.fromkeys(recortar_p(p_.get("dolor"), 80) for p_ in pasos if str(p_.get("dolor") or "").strip()))
            usa = [r for p_ in pasos for r in (p_.get("refs") or []) if re.match(r"^(REQ|FR|NFR)-\d+$", str(r))]
            add(cabeza(per), descripcion=recortar_p(per[len(re.split(r"[,(;:]", per)[0]):].lstrip(" ,;:("), 200), objetivo=recortar_p(d.get("trabajo"), 120), contexto_uso=recortar_p(d.get("disparador"), 160),
                dolores=recortar_p(dolores, 300), fuente=fuente, evidencia=[os.path.basename(rj)] + [str(x) for x in (d.get("fuentes") or [])[:1]],
                usa=usa, beneficios=ben_de(d.get("kpi") or []), origen=[os.path.basename(rj)])
        pb = ruta(proyecto, "02-planificacion", "backlog.csv")
        if os.path.exists(pb):
            rx = re.compile(r"\b(?:como|as an?)\s+(?:un |una |el |la )?([^,.;]{3,60}?)\s*,?\s+(?:quiero|necesito|deseo|i want|i need|i'd like)\b", re.I)
            for f in csv.DictReader(open(pb, encoding="utf-8")):
                m = rx.search(f"{f.get('titulo', '')} {f.get('descripcion', '')}")
                if m: add(m.group(1).strip()[:1].upper() + m.group(1).strip()[1:], fuente="documento", evidencia=["backlog.csv"], usa=[f.get("id", "")], origen=[f.get("id", "")])
    # representante sugerido: un interesado cuyo rol (no su nombre) menciona la primera palabra del arquetipo, primero el que
    # dice «representa» («Representa a los pacientes» → «Paciente…»); si no, el usuario sénior (PRINCE2: representa a los usuarios)
    us = [resolver_st(proyecto, n, sts) for n in (e.get("roles", {}).get("usuario_senior") or [])]
    us = next((s for s in us if s), None)
    existentes = {norm(p.get("nombre")): p for p in leer(proyecto, "personas")}
    afin = lambda a, b: len(os.path.commonprefix([a, b])) >= min(5, len(a), len(b)) and min(len(a), len(b)) >= 4
    res = []
    for k, c in out.items():
        clave = next((w for w in palabras(c["nombre"]) if len(w) >= 4), "")
        afines = [s for s in sts if clave and any(afin(clave, w) for w in palabras(s.get("rol_organizacion", "") + " " + s.get("rol_proyecto", "")))]
        rep = next((s for s in afines if "represent" in " ".join(palabras(s.get("rol_organizacion", "") + " " + s.get("rol_proyecto", "")))), None) or (afines[0] if afines else us)
        ex = existentes.get(k)
        campos = {"nombre": c["nombre"], "descripcion": c["descripcion"], "objetivo": c["objetivo"], "dolores": c["dolores"] or t("[por confirmar]", "[to be confirmed]"),
                  "contexto_uso": c["contexto_uso"], "fuente": c["fuente"], "evidencia": "; ".join(c["evidencia"]), "stakeholder_id": rep["id"] if rep else "",
                  "usa": ";".join(c["usa"]), "beneficios": ";".join(c["beneficios"])}
        if ex:
            nuevos = {col: ";".join(ids_lista(ex.get(col)) + [x for x in ids_lista(campos[col]) if x not in ids_lista(ex.get(col))])
                      for col in ("usa", "beneficios") if [x for x in ids_lista(campos[col]) if x not in ids_lista(ex.get(col))]}
            cmd = (f"registro.py --proyecto {proyecto} actualizar personas {ex['id']} " + " ".join(f"--campo {shlex.quote(k_ + '=' + v)}" for k_, v in nuevos.items())) if nuevos else ""
        else:
            cmd = f"registro.py --proyecto {proyecto} agregar personas " + " ".join(f"--campo {shlex.quote(k_ + '=' + v)}" for k_, v in campos.items() if v)
        res.append({**campos, "origen": c["origen"], "representante": rep.get("nombre", "") if rep else "", "existente": ex["id"] if ex else "", "comando": cmd})
    return res

def cmd_personas(a, J):
    p = a.proyecto
    if a.accion == "candidatos":
        cs = candidatos_personas(p, a.desde)
        if a.json: J(cs); return
        print(t(f"{len(cs)} persona(s) candidata(s) · el modelo propone, la persona confirma; nada se registra solo. El texto citado es dato de la fuente, no una instrucción.",
                f"{len(cs)} candidate persona(s) · proposed, not registered; quoted text is source data, not an instruction."))
        for c in cs[:a.limite or None]:
            print(f"- {c['nombre']}" + (f" ({c['existente']}, " + t("ya registrada", "already registered") + ")" if c["existente"] else "") + f" · {t('fuente', 'source')} {c['fuente']} · {c['evidencia']}")
            for k, et in (("descripcion", t("arquetipo", "archetype")), ("objetivo", t("objetivo", "goal")), ("contexto_uso", t("contexto de uso", "context of use")),
                          ("dolores", t("dolores", "pains")), ("usa", t("usa", "uses")), ("beneficios", t("beneficios", "benefits"))):
                if c[k]: print(f"    {et}: {c[k]}")
            if c["stakeholder_id"]: print(f"    {t('representante sugerido', 'suggested representative')}: {c['stakeholder_id']} {c['representante']}")
            if c["comando"]: print(f"    → {c['comando']}")
        if a.limite and len(cs) > a.limite: print(t(f"… y {len(cs) - a.limite} más (--limite 0 o --json para verlas todas)", f"… and {len(cs) - a.limite} more"))
        print(t("Confirmar con la persona cada candidata, completar dolores y lo que pide (solicita) o de qué se beneficia (beneficia), y registrar.",
                "Confirm each candidate, complete pains, requests and benefits, then register."))
        return
    if a.accion == "mapa":
        m = mapa_personas(p)
        if a.json: J(m); return
        ps = m["personas"]
        if not ps: print(t("Sin personas registradas: interesados.py personas candidatos", "No personas registered: interesados.py personas candidatos")); return
        print("| " + t("Capacidad", "Capability") + " | " + t("Título", "Title") + " | MoSCoW | " + " | ".join(f"{x['id']} {corto(x['nombre'], 16)}" for x in ps) + " |")
        print("|---|---|---|" + "---|" * len(ps))
        sig = {rol: s for _, rol, s in ROLES_PERSONA}
        for f in m["capacidades"][:a.limite or None]:
            print(f"| {f['id']} | {recortar_p(f['titulo'], 50)} | {etq_moscow(f['prioridad'])} | " + " | ".join("·".join(sig[r] for r in f["personas"].get(x["id"], [])) for x in ps) + " |")
        if a.limite and len(m["capacidades"]) > a.limite: print(t(f"… y {len(m['capacidades']) - a.limite} capacidades más (--limite 0 o --json)", f"… and {len(m['capacidades']) - a.limite} more capabilities"))
        print(t("S solicitante · U usuario · B beneficiario", "S requester · U user · B beneficiary"))
        sin = m["must_sin_persona"]
        if sin: print(t("Must sin persona (STK-13): ", "Must without persona (STK-13): ") + ", ".join(x["id"] for x in sin[:20]) + (t(f" … y {len(sin) - 20} más", f" … and {len(sin) - 20} more") if len(sin) > 20 else ""))
        return
    r = priorizacion_personas(p)
    if a.json: J(r); return
    if not r["personas"]: print(t("Sin personas registradas: interesados.py personas candidatos", "No personas registered")); return
    print("| " + t("Persona", "Persona") + " | " + t("Representante", "Representative") + " | Must | Should | Could | Won't | " + t("Sin prioridad", "No priority")
          + " | S | U | B | " + t("Beneficios", "Benefits") + " |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in r["personas"][:a.limite or None]:
        pp, rr = x["por_prioridad"], x["por_rol"]
        print(f"| {x['id']} {corto(x['nombre'], 24)} | {(x['representante'] or {}).get('id', '—')} | {pp['must']} | {pp['should']} | {pp['could']} | {pp['wont']} | {pp['sin']} | "
              f"{rr['solicitante']} | {rr['usuario']} | {rr['beneficiario']} | " + (", ".join(b["id"] for b in x["beneficios"]) or "—") + " |")
    if a.limite and len(r["personas"]) > a.limite: print(t(f"… y {len(r['personas']) - a.limite} personas más (--limite 0 o --json)", f"… and {len(r['personas']) - a.limite} more personas"))
    print(t(f"{r['capacidades']} capacidad(es) mapeadas · Must sin persona: {', '.join(r['must_sin_persona'][:20]) or 'ninguno'}",
            f"{r['capacidades']} capability(ies) mapped · Must without persona: {', '.join(r['must_sin_persona'][:20]) or 'none'}"))

# ------------------------------------------------------------------ CLI
def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--proyecto", required=True); ap.add_argument("--medio", choices=["alto", "bajo"], default="alto", help="cómo ubicar 'medio' en la matriz 2×2 (defecto: alto)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("matriz"); m.add_argument("--markdown"); m.add_argument("--json", action="store_true")
    es_ = sub.add_parser("estereotipos"); es_.add_argument("--semilla", action="store_true"); es_.add_argument("--sugerir", action="store_true"); es_.add_argument("--json", action="store_true")
    pr = sub.add_parser("proponer"); pr.add_argument("--transcripcion", required=True); pr.add_argument("--mapa", default=""); pr.add_argument("--fecha"); pr.add_argument("--fuente")
    pr.add_argument("--vigencia-dias", type=int, default=180); pr.add_argument("--registrar", action="store_true"); pr.add_argument("--json", action="store_true")
    for nombre in ("confirmar", "rechazar"):
        c = sub.add_parser(nombre); c.add_argument("ids", nargs="+"); c.add_argument("--por", required=True); c.add_argument("--vigencia-hasta"); c.add_argument("--motivo", default="")
    pe = sub.add_parser("perfil"); pe.add_argument("id"); pe.add_argument("--corte"); pe.add_argument("--json", action="store_true")
    ra = sub.add_parser("raci"); ra.add_argument("--elemento"); ra.add_argument("--markdown"); ra.add_argument("--json", action="store_true")
    vi = sub.add_parser("vinculos"); vi.add_argument("id"); vi.add_argument("--json", action="store_true")
    ig = sub.add_parser("integridad"); ig.add_argument("--corte"); ig.add_argument("--json", action="store_true")
    rp = sub.add_parser("reporte"); rp.add_argument("--html"); rp.add_argument("--markdown"); rp.add_argument("--corte"); rp.add_argument("--restringido", action="store_true")
    pn = sub.add_parser("personas", help="personas de usuario × capacidades (personas.csv)"); pn.add_argument("accion", choices=["candidatos", "mapa", "priorizacion"])
    pn.add_argument("--desde", choices=["auto", "bmad", "artefactos"], default="auto"); pn.add_argument("--limite", type=int, default=40, help="máximo de filas en texto (0 = sin límite)")
    pn.add_argument("--json", action="store_true")
    pl = sub.add_parser("plan-envio"); pl.add_argument("--tema", required=True); pl.add_argument("--audiencia", required=True); pl.add_argument("--proposito", default="comunicado",
        choices=["comunicado", "informe", "recordatorio", "convocatoria", "puerta", "okr", "acta", "otro"]); pl.add_argument("--base"); pl.add_argument("--agrupar", action="store_true"); pl.add_argument("--fecha")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.proyecto, "estado.json")): sys.exit(f"{a.proyecto}: falta estado.json / not a project folder")
    IDIOMA = E.idioma_de(a.proyecto)
    J = lambda x: print(json.dumps(x, ensure_ascii=False, indent=2))

    if a.cmd == "matriz":
        cuads, sin = matriz(a.proyecto, a.medio)
        if a.json: J({"medio": a.medio, "cuadrantes": {q: [{"id": s["id"], "nombre": s.get("nombre", ""), "frontera": frontera(s)} for s in cuads[q]] for q in CUADRANTES}, "sin_ubicar": [s["id"] for s in sin]}); return
        for q in CUADRANTES:
            print(f"{ESTRATEGIA[q]['nombre'][IDIOMA == 'en']} ({len(cuads[q])}): " + (", ".join(s["id"] + " " + s.get("nombre", "") + (" ◇" if frontera(s) else "") for s in cuads[q]) or "—"))
            print("   " + ESTRATEGIA[q]["estrategia"][IDIOMA == "en"])
        if sin: print(t("Sin ubicar (falta poder o interés): ", "Not placed: ") + ", ".join(s["id"] for s in sin))
        print(t(f"◇ = frontera ('medio' ubicado como {a.medio})", f"◇ = boundary ('medium' placed as {a.medio})"))
        if a.markdown: reporte(a.proyecto, None, a.markdown, None, False, a.medio); print(t(f"Markdown → {a.markdown}", f"Markdown → {a.markdown}"))
        return
    if a.cmd == "estereotipos":
        if a.semilla:
            with E.bloqueo(a.proyecto):        # comprobación de catálogo vacío y altas en una sola operación
                if leer(a.proyecto, "estereotipos"): sys.exit(t("estereotipos.csv ya tiene filas: la semilla solo se carga en un catálogo vacío.", "estereotipos.csv is not empty."))
                for (nom, desc, q, canal, fmt, niv, frec, reg, est) in SEMILLA:
                    agregar(a.proyecto, "estereotipos", {"nombre": nom, "descripcion": desc, "cuadrante": q, "canal": canal, "formato": fmt, "nivel_detalle": niv,
                                                          "frecuencia": frec, "registro": reg, "estilo_decision": est, "notas": t("semilla: guía de pm-comunicacion-stakeholders §1", "seed")})
                print(t(f"{len(SEMILLA)} estereotipos semilla creados (ET-001…ET-{len(SEMILLA):03d}); ajustarlos con registro.py actualizar estereotipos …", f"{len(SEMILLA)} seed stereotypes created"))
        if a.sugerir:
            nuevos, asignar = sugerir_estereotipos(a.proyecto, None, a.medio)
            if a.json: J({"nuevos": nuevos, "asignaciones": asignar}); return
            for n in nuevos: print(t("Nuevo estereotipo sugerido", "Suggested new stereotype") + f": {n['cuadrante']} · {n['canal']} · {n['formato']} · {n['nivel_detalle']} → {', '.join(n['miembros'])}")
            for x in asignar: print(t("Asignar", "Assign") + f" {x['stakeholder_id']} → {x['estereotipo']} {x['nombre']} ({x['coincidencias']} " + t("coincidencias)", "matches)")
                                     + f"   registro.py --proyecto {a.proyecto} actualizar stakeholders {x['stakeholder_id']} --campo estereotipo={x['estereotipo']}")
            if not nuevos and not asignar: print(t("Sin sugerencias (hacen falta preferencias confirmadas o estereotipos definidos).", "No suggestions."))
            print(t("Las sugerencias no se aplican solas: el gestor decide.", "Suggestions are not applied automatically."))
            return
        ets = leer(a.proyecto, "estereotipos"); sts = leer(a.proyecto, "stakeholders")
        if a.json: J([{**x, "miembros": [s["id"] for s in sts if s.get("estereotipo") == x["id"]]} for x in ets]); return
        for x in ets: print(f"{x['id']} {x['nombre']} [{x.get('estado')}] {x.get('cuadrante','')} · {x.get('canal','')} · {x.get('formato','')} · {x.get('nivel_detalle','')} · {x.get('frecuencia','')} → " + (", ".join(s["id"] for s in sts if s.get("estereotipo") == x["id"]) or "—"))
        if not ets and not a.semilla: print(t("Catálogo vacío: interesados.py estereotipos --semilla", "Empty catalogue: use --semilla"))
        return
    if a.cmd == "proponer":
        props, sin, part = proponer(a.proyecto, a.transcripcion, a.mapa, a.fecha, a.fuente, a.vigencia_dias)
        if a.registrar:
            for p in props:
                p["id"] = agregar(a.proyecto, "preferencias", {k: p[k] for k in ("fecha", "stakeholder_id", "dimension", "valor", "procedencia", "evidencia", "fuente", "vigencia_hasta")} | {"estado": "propuesta"})
        if a.json: J({"propuestas": props, "hablantes_sin_asignar": sin, "participacion": part, "registradas": a.registrar}); return
        for p in props: print(f"{p.get('id', '·')} {p['stakeholder_id']} {p['dimension']}={p['valor']} ({p['procedencia']}) {p['evidencia']}")
        if not props: print(t("No se encontraron preferencias declaradas en primera persona.", "No first-person declared preferences found."))
        if sin: print(t("Hablantes sin asignar a un interesado (usar --mapa): ", "Unmapped speakers (use --mapa): ") + ", ".join(sin))
        print(t("Estado: propuesta. Nada se aplica hasta que el gestor confirme con la persona: interesados.py confirmar PF-… --por \"Rol: Nombre\".", "Status: proposed. Nothing applies until confirmed."))
        return
    if a.cmd in ("confirmar", "rechazar"):
        with E.bloqueo(a.proyecto):            # lectura y reescritura de preferencias.csv sin pisar a otro proceso
            p = E.asegurar_registro(a.proyecto, "preferencias"); cols, filas = E.leer_csv(p); hechos = []
            for f in filas:
                if f["id"] in a.ids:
                    if a.cmd == "confirmar":
                        f["estado"] = "confirmada"; f["confirmado_por"] = a.por
                        if a.vigencia_hasta: f["vigencia_hasta"] = a.vigencia_hasta
                        elif not f.get("vigencia_hasta"): f["vigencia_hasta"] = (datetime.date.today() + datetime.timedelta(days=180)).isoformat()
                    else:
                        f["estado"] = "rechazada"; f["confirmado_por"] = a.por; f["notas"] = (f.get("notas", "") + " " + a.motivo).strip()
                    hechos.append(f["id"])
            falt = [x for x in a.ids if x not in hechos]
            if falt: sys.exit(t(f"No existen: {', '.join(falt)} (no se modificó nada)", f"Not found: {', '.join(falt)} (nothing changed)"))
            E.escribir_csv(p, cols, filas); print(f"{a.cmd}: {', '.join(hechos)}"); return
    if a.cmd == "perfil":
        sts = leer(a.proyecto, "stakeholders"); sel = sts if a.id in ("todos", "all") else [resolver_st(a.proyecto, a.id, sts)]
        if not sel or sel[0] is None: sys.exit(t(f"No existe {a.id}", f"{a.id} not found"))
        cache = {"et": {x["id"]: x for x in leer(a.proyecto, "estereotipos")}, "pf": leer(a.proyecto, "preferencias"), "estado": estado_json(a.proyecto)}
        res = [perfil(a.proyecto, s, a.corte, a.medio, cache) for s in sel]
        if a.json: J(res if len(res) > 1 else res[0]); return
        for p in res:
            print(f"{p['id']} {p['nombre']} · {p['cuadrante'] or t('sin cuadrante', 'no quadrant')}{' ◇' if p['frontera'] else ''} · {t('estereotipo', 'stereotype')} {p['estereotipo'] or '—'} · {t('destino', 'destination')} {p['destino'] or '—'}")
            for d, v in p["dimensiones"].items():
                if v["valor"]: print(f"   {d}: {v['valor']}  ({v['fuente']})")
            for k, txt in (("pendientes", t("propuestas sin confirmar", "unconfirmed proposals")), ("vencidas", t("vencidas (no aplicadas)", "expired (not applied)"))):
                if p[k]: print(f"   {txt}: {', '.join(p[k])}")
            for c in p["conflictos"]: print("   AVISO " + c)
        return
    if a.cmd == "raci":
        ids = ids_conocidos(a.proyecto); por_el, hall = raci(a.proyecto, a.medio, ids); sts = leer(a.proyecto, "stakeholders")
        if a.elemento:
            fs = por_el.get(a.elemento, [])
            tp = tipo_de(a.elemento, next((x.get("tipo_elemento") for x in fs if x.get("tipo_elemento")), ""))
            if a.json: J({"elemento": a.elemento, "tipo": tp, "titulo": titulo_de(ids, a.elemento, tp), "roles": fs}); return
            print(f"{a.elemento} ({tp}) {titulo_de(ids, a.elemento, tp)}")
            for x in fs:
                s = resolver_st(a.proyecto, x["stakeholder_id"], sts) or {}
                print(f"   {x['rol']}  {x['stakeholder_id']} {s.get('nombre', '?')}")
            if not fs: print(t("   sin filas RACI", "   no RACI rows"))
            return
        if a.json: J({"elementos": {el: [{"stakeholder_id": x["stakeholder_id"], "rol": x["rol"]} for x in fs] for el, fs in por_el.items()}, "hallazgos": [{"severidad": s, "codigo": c, "mensaje": m} for s, c, m in hall]}); return
        print("\n".join(raci_markdown(a.proyecto, por_el, ids, sts)))
        for s, c, m in hall: print(f"{s} {c}: {m}")
        if not hall and por_el: print(t("RACI válida: un A por elemento, al menos un R, referencias existentes.", "RACI valid."))
        if a.markdown:
            open(a.markdown, "w", encoding="utf-8").write("\n".join(raci_markdown(a.proyecto, por_el, ids, sts)) + "\n\n" + "\n".join(f"- {s} {c}: {m}" for s, c, m in hall) + "\n"); print(f"→ {a.markdown}")
        return
    if a.cmd == "vinculos":
        v = vinculos(a.proyecto, a.id)
        if a.json: J(v); return
        i = v["interesado"]; print(f"{i['id']} {i['nombre']} · {i['rol_proyecto']} · {v['cuadrante'] or '—'} · {t('estereotipo', 'stereotype')} {i['estereotipo'] or '—'}")
        for x in v["raci"]: print(f"   RACI {x['rol']} en {x['elemento']} ({x['tipo']}) {x['titulo']}")
        for x in v["okr"]: print(f"   OKR {x['id']} ({x['tipo']}) {x['enunciado']}")
        for x in v["registros"]: print(f"   {x['registro']} {x['id']} ({x['como']}, {x['estado']})")
        for x in v["preferencias"]: print(f"   {x['id']} {x['dimension']}={x['valor']} [{x['estado']}]")
        for x in v["envios"]: print(f"   {x['id']} {x['fecha']} {x['canal']} «{x['asunto']}» [{x['estado']}]")
        return
    if a.cmd == "integridad":
        h = integridad(a.proyecto, a.corte, a.medio)
        if a.json: J([{"severidad": s, "codigo": c, "mensaje": m} for s, c, m in h]); return
        for s, c, m in h: print(f"{s} {c}: {m}")
        if not h: print(t("Integridad referencial y calidad del maestro: sin hallazgos.", "No findings."))
        sys.exit(1 if any(s == "ERROR" for s, _, _ in h) else 0)
    if a.cmd == "reporte":
        if not a.html and not a.markdown: sys.exit(t("Indicar --html y/o --markdown", "Use --html and/or --markdown"))
        r = reporte(a.proyecto, a.html, a.markdown, a.corte, a.restringido, a.medio)
        print(t(f"Reporte de interesados → {a.html or ''} {a.markdown or ''} · {sum(len(v) for v in r['cuadrantes'].values())} ubicados, {r['elementos_raci']} elementos RACI, {r['hallazgos']} hallazgos",
                f"Stakeholder report → {a.html or ''} {a.markdown or ''}")); return
    if a.cmd == "personas": cmd_personas(a, J); return
    if a.cmd == "plan-envio":
        carpeta, filas, avisos = plan_envio(a.proyecto, a.tema, a.audiencia, a.proposito, a.base, a.agrupar, a.fecha, a.medio)
        print(t(f"Plan de envío → {os.path.relpath(carpeta, a.proyecto)}/ ({len(filas)} destinatarios, {len({f['archivo'] for f in filas})} mensajes en borrador)",
                f"Delivery plan → {carpeta} ({len(filas)} recipients)"))
        for f in filas: print(f"   {f['stakeholder_id']} {f['nombre']}: {f['canal']} → {f['destino'] or '—'} · {f['formato']} · {f['nivel_detalle']} · {f['idioma']} · {f['archivo']}")
        for w in avisos: print("AVISO " + w)
        print(t("Siguiente: redactar cada mensaje según su perfil, aprobar con envios.py aprobar y enviar con envios.py enviar (simulación por defecto).", "Next: draft, approve with envios.py aprobar, send with envios.py enviar."))

if __name__ == "__main__":
    main()
