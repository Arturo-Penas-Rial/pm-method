#!/usr/bin/env python3
"""Inteligencia de reuniones: candidatos de decisiones, compromisos, supuestos y riesgos desde una transcripción, con cita y
marca de tiempo, que se registran solo tras la confirmación de una persona.
Meeting intelligence: decision, commitment, assumption and risk candidates from a transcript, quoted and time-stamped,
recorded only after a person confirms them.

Uso / Usage:
  extraccion.py --proyecto G candidatos --transcripcion F [--reunion comite] [--tipo retrospectiva|planificacion|seguimiento|otra]
                [--fecha AAAA-MM-DD] [--salida F.md] [--max 20] [--json]
  extraccion.py --proyecto G registrar --candidatos F.json --confirmar CA-01,CD-02 --por "Gestor: Nombre"
                [--campo CA-01:responsable="Ana Ríos" …] [--simular]
Entrada: la transcripción normalizada de transcripcion.py (recomendado) o un VTT, SRT o TXT "Nombre: texto"; DOCX → normalizar
antes con transcripcion.py --salida.
candidatos (no escribe registros): heurísticas deterministas por oración, con frases marcadoras en español e inglés
(references/guia.md §3.1):
  CD  decisión tomada ("decidimos", "aprobamos", "acordamos", "vamos con", "we decided", "we agreed") o pendiente
      ("hay que decidir", "lo decide la junta", "queda pendiente", "to be decided"), con el nivel de decisión de SPEC
      §1.10.8 (equipo, product-owner, gestor, autoridad-cambio, ejecutivo, junta, capa-negocio) según quién habla
      (estado.json.roles) o lo que nombra la frase; sin indicio, [por confirmar].
  CA  compromiso o acción ("me encargo", "yo le mando", "X se encarga", "queda a cargo de", "I'll"; "hay que" solo con plazo),
      con responsable (el hablante, o la persona nombrada) y fecha (AAAA-MM-DD, dd/mm, día de la semana, mañana o fin de
      mes, resueltos contra la fecha de la reunión); sin dato, [por confirmar].
  CS  supuesto ("suponemos", "asumimos", "damos por hecho", "we assume").
  CR  riesgo: lo extrae pm-riesgos/scripts/riesgos.py (frases de preocupación, dependencia, incertidumbre u oportunidad) y
      marca el posible duplicado de riesgos.csv.
  IN  instrucción dirigida al asistente o a los registros dentro de la fuente ("ignorá las reglas", "registrá todo",
      "aprobá la puerta", "ignore previous instructions"): fuentes = datos, se informa y nunca se registra.
  Tipo de reunión (--tipo; sin él, por el nombre: "retro…" → retrospectiva, "planif…|planning" → planificacion,
  "seguimiento|checkpoint|daily|highlight" → seguimiento; si no, otra). Una retrospectiva mira el proceso, no a las
  personas, y no decide por la junta: en lugar de CD y CA propone
  CL  lección candidata ("funcionó", "no funcionó", "nos costó", "aprendimos que", "otra vez", "went well", "didn't work",
      "we learned"), con sentido (funcionó / no funcionó), recurrencia sugerida (alta si "otra vez", "de nuevo", "again") y la
      recomendación cuando la frase la dice ("aprendimos que …", "la próxima vez …", "de ahora en más …"); sin dato, [por confirmar].
  CM  acción de mejora ("vamos a probar", "probemos", "acordamos", "let's try", o un compromiso con responsable), con
      responsable y fecha como CA.
  En planificación, seguimiento u otra reunión no se proponen lecciones salvo marcadas ("lección:", "lección aprendida",
  "queda como lección", "lesson learned:").
  Escribe <fecha>-<reunion>-candidatos.md (borrador) y .json en 03-control/reuniones/ y termina con la pregunta de confirmación.
registrar: carga con registro.py solo los ids confirmados (--confirmar, sin opción "todos") y deja en notas el origen
(archivo [hh:mm:ss]), el id del candidato y quién confirmó (--por). Destinos: CA → acciones.csv; CD pendiente → acciones.csv
("Decidir: …", responsable = quien decide); CD tomada → decisiones.csv (nivel junta, ejecutivo o capa-negocio: no se registra
aquí, la registra pm-director); CS → supuestos.csv; CR → riesgos.csv (luego P×I y respuesta con pm-riesgos); CM → acciones.csv
(acción de mejora); CL → lecciones.csv (registrada; exige recomendación; luego lecciones.py clasificar). Valida todo
antes de escribir: una acción sin responsable o sin fecha, una decisión sin nivel o un IN se rechazan y no se registra nada;
un candidato ya registrado se omite. Si la transcripción cambió desde la propuesta, pide volver a correr candidatos.
"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.normpath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SK, "pm-estado-proyecto", "scripts"))
sys.path.insert(0, os.path.join(SK, "pm-riesgos", "scripts"))
import esquema as E
import riesgos as R

REG = os.path.join(SK, "pm-estado-proyecto", "scripts", "registro.py")
IDIOMA = "es"
POR_CONFIRMAR = "[por confirmar]"
def t(es, en): return en if IDIOMA == "en" else es

# ------------------------------------------------------------------ frases marcadoras (ES/EN), documentadas en guia.md §3.1
INSTRUCCION = re.compile(r"\b(ignor[aáe]\w*\s+(las|todas|tus|the|all|any|previous|prior)?\s*(reglas|instrucciones|rules|instructions)|"
                         r"ignore (all |any )?(previous |prior )?(rules|instructions)|registr[aá] (todo|todas|todos)|"
                         r"aprob[aá] (la|las) puertas?|marc[aá]\w* .{0,40}como (aprobad|completad|cerrad)|"
                         r"(record|register|approve|mark) (all|everything|the gate)|system prompt|como (asistente|ia|modelo)|"
                         r"(claude|chatgpt|asistente|assistant)[,:]\s|ejecut[aá] (el comando|estado\.py|registro\.py)|"
                         r"(borr|elimin)[aá] (el|los|las|todo)\b.{0,30}(registro|csv|archivo))", re.I)
DEC_PENDIENTE = re.compile(r"\b(hay que decidir|falta decidir|queda pendiente|quedan pendientes|pendiente de (aprobaci[oó]n|decisi[oó]n)|"
                           r"a decidir|lo decide|la decide|lo decidir[aá]|lo tiene que decidir|lo tienen que decidir|lo elevamos|lo escalamos|"
                           r"decidir(lo|la)? en la pr[oó]xima|definir(lo|la)? en la pr[oó]xima|need to decide|to be decided|pending decision|"
                           r"decide (next|at the next)|escalate (it|this) to)\b", re.I)
DEC_TOMADA = re.compile(r"\b(decidimos|decidido|queda decidido|se decidi[oó]|aprobamos|queda aprobad[oa]|se aprueba|se aprob[oó]|acordamos|"
                        r"se acord[oó]|queda acordado|vamos con (la|el|los|las)|nos quedamos con|elegimos|resolvimos|"
                        r"we decided|we agreed|agreed to|it was agreed|we approved|we('ll| will) go with|let'?s go with|decision:)", re.I)
SUPUESTO = re.compile(r"\b(suponemos|asumimos|damos por (hecho|sentado)|partimos de la base|suponiendo que|asumiendo que|en el supuesto de|"
                      r"se supone que|we assume|assuming( that)?|our assumption|assumption:)", re.I)
PRIMERA = re.compile(r"\b(me encargo|me ocupo|me comprometo|yo (me encargo|lo|la|le|les|te|se lo|se la|mando|env[ií]o|preparo|reviso|armo|hago|llamo|"
                     r"coordino|confirmo|actualizo|paso|averiguo)|voy a|lo hago|te (lo |la )?(mando|paso|env[ií]o)|les (mando|paso|env[ií]o)|"
                     r"i'll|i will|i'm going to|i can take)\b", re.I)
NOMBRE = r"([A-ZÁÉÍÓÚÑ][a-záéíóúñü]+(?:\s[A-ZÁÉÍÓÚÑ][a-záéíóúñü]+)?)"
TERCERA = [re.compile(r"\b(?:queda a cargo de|a cargo de|responsable:?|owner:?|lo toma|se lo asignamos a|asignado a|assigned to)\s+" + NOMBRE),
           re.compile(NOMBRE + r"\s+(?:se encarga|se ocupa|se compromete|va a|lo hace|lo prepara|lo manda|will|is going to)\b")]
OBLIGACION = re.compile(r"\b(hay que|tenemos que|habr[ií]a que|queda como acci[oó]n|acci[oó]n:|tarea:|action item|action:|we need to|we have to)\b", re.I)
# retrospectiva (y lecciones marcadas en otras reuniones), documentadas en guia.md §3.1
LECCION_EXPLICITA = re.compile(r"\b(lecci[oó]n( aprendida)?:|queda como lecci[oó]n|anot(emos|amos|ar) (como|una) lecci[oó]n|lesson( learned)?:)", re.I)
LEC_NEG = re.compile(r"\b(no funcion[oó]|tampoco funcion[oó]|no anduvo|nos cost[oó]|sali[oó] mal|otra vez|de nuevo|volvi[oó] a pasar|ya nos pas[oó]|deber[ií]amos haber|"
                     r"didn'?t work|did not work|went wrong|again)\b", re.I)
LEC_POS = re.compile(r"\b(funcion[oó]( muy)? bien|funcion[oó]|anduvo bien|sali[oó] bien|nos sirvi[oó]|went well|worked( well)?)\b", re.I)
LEC_APR = re.compile(r"\b(aprendimos( que)?|la lecci[oó]n es( que)?|nos dimos cuenta( de)?( que)?|we learned( that)?)\b", re.I)
RECOMIENDA = re.compile(r"\b(?:aprendimos que|la lecci[oó]n es que|la pr[oó]xima vez,?|de ahora en m[aá]s,?|a partir de ahora,?|we learned that|next time,?|from now on,?)\s+(.{8,})$", re.I)
RECURRE = re.compile(r"\b(otra vez|de nuevo|volvi[oó] a pasar|ya nos pas[oó]|como en el sprint|again)\b", re.I)
MEJORA = re.compile(r"\b(vamos a probar|probemos|probamos con|vamos a intentar|acordamos|decidimos|let'?s try|we('ll| will) try|we agreed)\b", re.I)
TIPOS_REUNION = ("retrospectiva", "planificacion", "seguimiento", "otra")

def tipo_de(nombre):
    n = norm(nombre)
    if re.search(r"retro", n): return "retrospectiva"
    if re.search(r"planif|planning", n): return "planificacion"
    if re.search(r"seguimiento|checkpoint|daily|highlight|standup", n): return "seguimiento"
    return "otra"

NIVEL_TEXTO = [("capa-negocio", r"capa de negocio|direcci[oó]n corporativa|corporativo|business layer|corporate"),
               ("junta", r"\bjunta\b|comit[eé] (de direcci[oó]n|directivo)|\bboard\b|steering|\bpuerta\b|autorizar-|pasar a la etapa|\bgate\b"),
               ("ejecutivo", r"ejecutiv[oa]|executive|patrocinador|sponsor"),
               ("autoridad-cambio", r"autoridad de cambio|change authority|comit[eé] de cambios|\bccb\b"),
               ("product-owner", r"product owner|\bpo\b"),
               ("gestor", r"gestor del proyecto|project manager|\bpm\b"),
               ("equipo", r"\bel equipo\b|the team|equipo de desarrollo")]
ROL_NIVEL = [("ejecutivo", "ejecutivo"), ("autoridad_cambio", "autoridad-cambio"), ("product_owner", "product-owner"), ("gestor_proyecto", "gestor"), ("jefes_equipo", "equipo")]
ROL_TXT = {"ejecutivo": "Ejecutivo", "autoridad-cambio": "Autoridad de cambio", "product-owner": "Product owner", "gestor": "Gestor", "equipo": "Equipo"}
DIRECTOR = ("junta", "ejecutivo", "capa-negocio")     # SPEC §1.10.4: esas decisiones las registra pm-director
DIAS = {"lunes": 0, "martes": 1, "miercoles": 2, "jueves": 3, "viernes": 4, "sabado": 5, "domingo": 6,
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}

def norm(s): return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()

def fecha_dicha(texto, base):
    """(fecha ISO o "", texto dicho): AAAA-MM-DD, dd/mm[/aaaa], día de la semana (el próximo), mañana/tomorrow, hoy/today,
    fin de mes/end of the month, resueltos contra la fecha de la reunión `base` (date o None)."""
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", texto)
    if m: return m.group(1), m.group(1)
    m = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", texto)
    if m:
        d, mes = int(m.group(1)), int(m.group(2)); a = m.group(3)
        anio = (int(a) + 2000 if len(a) == 2 else int(a)) if a else (base.year if base else None)
        if anio:
            try:
                f = datetime.date(anio, mes, d)
                if not a and base and f < base: f = datetime.date(anio + 1, mes, d)
                return f.isoformat(), m.group(0)
            except ValueError: pass
        return "", m.group(0)
    n = norm(texto)
    for k, wd in DIAS.items():
        mm = re.search(rf"\b{k}\b", n)
        if mm:
            if not base: return "", k
            delta = (wd - base.weekday()) % 7 or 7
            return (base + datetime.timedelta(days=delta)).isoformat(), k
    for k, dd in (("manana", 1), ("tomorrow", 1), ("hoy", 0), ("today", 0)):
        if re.search(rf"\b{k}\b", n) and not (k == "manana" and re.search(r"\bla manana\b|\bde manana\b|\bpor la manana\b", n)):
            return ((base + datetime.timedelta(days=dd)).isoformat() if base else ""), k
    if re.search(r"fin de mes|end of the month|fin del mes", n):
        if not base: return "", "fin de mes"
        sig = (base.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        return (sig - datetime.timedelta(days=1)).isoformat(), "fin de mes"
    return "", ""

def nivel_decision(oracion, hablante, roles):
    n = norm(oracion)
    for nivel, rx in NIVEL_TEXTO:
        if re.search(rx, n): return nivel, t("lo nombra la frase", "named in the sentence")
    h = norm(hablante)
    for rol, nivel in ROL_NIVEL:
        v = roles.get(rol)
        for x in (v if isinstance(v, list) else [v]):
            if x and h and (norm(x) in h or h in norm(x)): return nivel, t(f"rol de {hablante} en estado.json", f"{hablante}'s role in estado.json")
    return "", ""

def responsable(oracion, hablante, conocidos):
    if PRIMERA.search(oracion): return hablante if hablante != "?" else ""
    for rx in TERCERA:
        m = rx.search(oracion)
        if m:
            nombre = m.group(1).strip()
            for c in conocidos:     # "Ana" → "Ana Ríos" si es hablante o interesado conocido
                if norm(c).split()[:1] == norm(nombre).split()[:1]: return c
            return nombre
    return ""

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def ruta_rel(proyecto, p): return os.path.relpath(os.path.abspath(p), os.path.dirname(os.path.abspath(proyecto)))

def leccion_cand(o, base_c, motivo, etapa):
    neg, pos, apr = LEC_NEG.search(o), LEC_POS.search(o), LEC_APR.search(o)
    sentido = t("no funcionó", "did not work") if neg else t("funcionó", "worked") if pos else t("aprendizaje", "learning")
    rm = RECOMIENDA.search(o)
    return {**base_c, "clase": "leccion", "sentido": sentido, "recurrencia": "alta" if RECURRE.search(o) else "", "motivo": motivo, "registro": "lecciones",
            "campos": {"situacion": o[:300], "efecto": POR_CONFIRMAR, "recomendacion": rm.group(1).strip(" .")[:300] if rm else POR_CONFIRMAR,
                       "recurrencia": "alta" if RECURRE.search(o) else "", "etapa": etapa, "fecha": base_c.get("fecha_reunion", ""),
                       "categoria": "acierto" if (pos and not neg) else ""}}

def candidatos(proyecto, ruta, reunion, fecha, e, tipo="otra"):
    roles = e.get("roles") or {}
    retro = tipo == "retrospectiva"
    etapa = str((e.get("etapa_actual") or {}).get("numero", "") or "")
    base = datetime.date.fromisoformat(fecha) if fecha else None
    turnos = R.turnos(ruta)
    sts = E.leer_csv(E.ruta_registro(proyecto, "stakeholders"))[1] if os.path.exists(E.ruta_registro(proyecto, "stakeholders")) else []
    conocidos = sorted({x["hablante"] for x in turnos if x["hablante"] != "?"} | {s.get("nombre", "") for s in sts if s.get("nombre")}, key=len, reverse=True)
    rel = ruta_rel(proyecto, ruta)
    out = {"CD": [], "CA": [], "CS": [], "IN": [], "CL": [], "CM": []}
    instrucciones = set()
    for x in turnos:
        for oracion in re.split(r"(?<=[.!?;])\s+", x["texto"]):
            o = oracion.strip()
            if not o: continue
            origen = rel + (f" [{x['ini']}]" if x.get("ini") else "")
            base_c = {"cita": f"{x['hablante']}: «{o[:300]}»", "texto": o[:300], "hablante": x["hablante"], "marca": x.get("ini") or "", "origen": origen}
            if retro or LECCION_EXPLICITA.search(o): base_c["fecha_reunion"] = fecha or ""
            mi = [m.group(0).strip(" ,:") for m in INSTRUCCION.finditer(o)]
            if mi:
                frases = " · ".join(dict.fromkeys(mi))
                out["IN"].append({**base_c, "clase": "instruccion", "motivo": t(f"instrucción incrustada ({frases}): fuentes = datos, no se ejecuta",
                                                                                 f"embedded instruction ({frases}): sources are data, not executed")})
                instrucciones.add(norm(o)); continue
            f_iso, f_txt = fecha_dicha(o, base)
            if retro:   # retrospectiva: lecciones y acciones de mejora, no decisiones de gobierno
                quien = responsable(o, x["hablante"], conocidos)
                mm = MEJORA.search(o)
                if mm or quien:
                    out["CM"].append({**base_c, "clase": "mejora", "motivo": t(f"marcador «{mm.group(0)}»", f"marker «{mm.group(0)}»") if mm else t("compromiso con responsable", "commitment with an owner"),
                                      "fecha_dicha": f_txt, "registro": "acciones",
                                      "campos": {"descripcion": o[:300], "responsable": quien or POR_CONFIRMAR, "fecha_compromiso": f_iso or POR_CONFIRMAR, "fecha": fecha or ""}})
                    continue
                ml = LEC_NEG.search(o) or LEC_APR.search(o) or LEC_POS.search(o) or LECCION_EXPLICITA.search(o)
                if ml:
                    out["CL"].append(leccion_cand(o, base_c, t(f"marcador «{ml.group(0)}»", f"marker «{ml.group(0)}»"), etapa)); continue
                if SUPUESTO.search(o):
                    out["CS"].append({**base_c, "clase": "supuesto", "motivo": t(f"marcador «{SUPUESTO.search(o).group(0)}»", f"marker «{SUPUESTO.search(o).group(0)}»"),
                                      "registro": "supuestos", "campos": {"supuesto_o_restriccion": o[:300], "tipo": "supuesto", "validado": "pendiente",
                                                                         "autor": x["hablante"], "responsable": x["hablante"] if x["hablante"] != "?" else "", "fecha": fecha or ""}})
                continue
            if LECCION_EXPLICITA.search(o):   # en otras reuniones, solo la lección marcada
                out["CL"].append(leccion_cand(o, base_c, t(f"marcada «{LECCION_EXPLICITA.search(o).group(0)}»", f"marked «{LECCION_EXPLICITA.search(o).group(0)}»"), etapa)); continue
            mp, mt = DEC_PENDIENTE.search(o), DEC_TOMADA.search(o)
            if mp or mt:
                nivel, por_que = nivel_decision(o, x["hablante"], roles)
                c = {**base_c, "clase": "decision", "estado": "pendiente" if mp else "tomada", "nivel": nivel or POR_CONFIRMAR,
                     "motivo": t(f"marcador «{(mp or mt).group(0)}»", f"marker «{(mp or mt).group(0)}»") + (f" · nivel: {por_que}" if nivel else "")}
                if mp:   # se sigue como acción hasta que alguien decide
                    rol_de = {"ejecutivo": "ejecutivo", "autoridad-cambio": "autoridad_cambio", "product-owner": "product_owner", "gestor": "gestor_proyecto"}
                    quien = ({"junta": t("Junta", "Board"), "capa-negocio": t("Capa de negocio", "Business layer")}.get(nivel)
                             or str(roles.get(rol_de.get(nivel, "")) or "") or responsable(o, x["hablante"], conocidos))
                    c.update(registro="acciones", campos={"descripcion": t("Decidir: ", "Decide: ") + o[:280], "responsable": quien or POR_CONFIRMAR,
                                                          "fecha_compromiso": f_iso or POR_CONFIRMAR}, fecha_dicha=f_txt)
                else:
                    rol = ROL_TXT.get(nivel_decision("", x["hablante"], roles)[0])
                    c.update(registro="decisiones", campos={"decision": o[:300], "decidido_por": (f"{rol}: {x['hablante']}" if rol else x["hablante"]),
                                                            "nivel": nivel or POR_CONFIRMAR, "fecha": fecha or "",
                                                            "contexto": t(f"reunión {reunion} {fecha}", f"meeting {reunion} {fecha}").strip()})
                out["CD"].append(c)
                if mp: continue
            elif SUPUESTO.search(o):
                out["CS"].append({**base_c, "clase": "supuesto", "motivo": t(f"marcador «{SUPUESTO.search(o).group(0)}»", f"marker «{SUPUESTO.search(o).group(0)}»"),
                                  "registro": "supuestos", "campos": {"supuesto_o_restriccion": o[:300], "tipo": "supuesto", "validado": "pendiente",
                                                                     "autor": x["hablante"], "responsable": x["hablante"] if x["hablante"] != "?" else "", "fecha": fecha or ""}})
                continue
            quien = responsable(o, x["hablante"], conocidos)
            obl = OBLIGACION.search(o)
            if quien or (obl and f_txt):
                motivo = t("compromiso en primera persona" if PRIMERA.search(o) else ("persona nombrada como responsable" if quien else f"«{obl.group(0)}» con plazo"),
                           "first-person commitment" if PRIMERA.search(o) else ("named owner" if quien else f"«{obl.group(0)}» with a deadline"))
                out["CA"].append({**base_c, "clase": "accion", "motivo": motivo, "fecha_dicha": f_txt, "registro": "acciones",
                                  "campos": {"descripcion": o[:300], "responsable": quien or POR_CONFIRMAR, "fecha_compromiso": f_iso or POR_CONFIRMAR}})
    # riesgos: los extrae pm-riesgos (mismas frases de preocupación, dependencia, incertidumbre u oportunidad) y marca duplicados
    R.IDIOMA = IDIOMA
    crs = R.duplicados(proyecto, R.fuente_transcripciones(proyecto, [ruta], None)[0])
    crs = [c for c in crs if not any(i in norm(c["cita"]) for i in instrucciones)]
    ya = {norm(c["texto"]) for k in ("CL", "CM") for c in out[k]}   # una oración ya propuesta como lección o mejora no se repite como riesgo
    crs = [c for c in crs if not any(y and y in norm(c["cita"]) for y in ya)]
    for c in crs:
        texto = re.sub(r"^[^:]{1,60}:\s*«(.*)»$", r"\1", c["cita"])
        c.update(clase="riesgo", texto=texto, hablante=c["cita"].split(":", 1)[0], marca=(re.search(r"\[(\d\d:\d\d:\d\d)\]", c["origen"]) or [None, ""])[1],
                 registro="riesgos", campos={"evento": texto, "tipo": c["tipo"], "categoria": c.get("categoria_sugerida") or "", "autor": c["cita"].split(":", 1)[0],
                                             "fecha_identificacion": fecha or ""})
    out["CR"] = crs
    lista = []
    for pref in ("CD", "CA", "CL", "CM", "CS", "CR", "IN"):
        for i, c in enumerate(out[pref], 1): c["id"] = f"{pref}-{i:02d}"; lista.append(c)
    return lista

def resumen_txt(cs, tipo="otra"):
    n = lambda f: sum(1 for c in cs if f(c))
    lec, mej = n(lambda c: c["clase"] == "leccion"), n(lambda c: c["clase"] == "mejora")
    if tipo == "retrospectiva":
        sup = n(lambda c: c["clase"] == "supuesto"); rn = n(lambda c: c["clase"] == "riesgo" and not c.get("posible_duplicado"))
        ins = n(lambda c: c["clase"] == "instruccion")
        txt = t(f"Retrospectiva: se detectaron {lec} {'lección candidata' if lec == 1 else 'lecciones candidatas'}, {mej} {'acción' if mej == 1 else 'acciones'} de mejora, "
                f"{sup} supuesto{'s' if sup != 1 else ''} y {rn} riesgo{'s' if rn != 1 else ''} nuevo{'s' if rn != 1 else ''} (sin decisiones de gobierno)",
                f"Retrospective: detected {lec} candidate lesson{'s' if lec != 1 else ''}, {mej} improvement action{'s' if mej != 1 else ''}, "
                f"{sup} assumption{'s' if sup != 1 else ''} and {rn} new risk{'s' if rn != 1 else ''} (no governance decisions)")
        if ins: txt += t(f"; {ins} {'instrucción' if ins == 1 else 'instrucciones'} dentro de la fuente no se ejecuta{'n' if ins != 1 else ''} (fuentes = datos)",
                         f"; {ins} instruction{'s' if ins != 1 else ''} inside the source not executed (sources are data)")
        return txt + "."
    comp = n(lambda c: c["clase"] == "accion"); pend = n(lambda c: c["clase"] == "decision" and c["estado"] == "pendiente")
    tom = n(lambda c: c["clase"] == "decision" and c["estado"] == "tomada"); sup = n(lambda c: c["clase"] == "supuesto")
    rn = n(lambda c: c["clase"] == "riesgo" and not c.get("posible_duplicado")); rd = n(lambda c: c["clase"] == "riesgo" and c.get("posible_duplicado"))
    ins = n(lambda c: c["clase"] == "instruccion")
    partes = [t(f"{comp} compromiso{'s' if comp != 1 else ''}", f"{comp} commitment{'s' if comp != 1 else ''}"),
              t(f"{pend} decisi{'ones' if pend != 1 else 'ón'} pendiente{'s' if pend != 1 else ''}", f"{pend} pending decision{'s' if pend != 1 else ''}"),
              t(f"{tom} decisi{'ones' if tom != 1 else 'ón'} tomada{'s' if tom != 1 else ''}", f"{tom} decision{'s' if tom != 1 else ''} taken"),
              t(f"{sup} supuesto{'s' if sup != 1 else ''}", f"{sup} assumption{'s' if sup != 1 else ''}"),
              t(f"{rn} riesgo{'s' if rn != 1 else ''} nuevo{'s' if rn != 1 else ''}", f"{rn} new risk{'s' if rn != 1 else ''}")]
    txt = t("Se detectaron ", "Detected ") + ", ".join(partes[:-1]) + t(" y ", " and ") + partes[-1]
    if rd: txt += t(f" ({rd} posible{'s' if rd != 1 else ''} duplicado{'s' if rd != 1 else ''} de riesgos ya registrados)", f" ({rd} possible duplicate{'s' if rd != 1 else ''})")
    if lec: txt += t(f"; {lec} {'lección marcada' if lec == 1 else 'lecciones marcadas'}", f"; {lec} marked lesson{'s' if lec != 1 else ''}")
    if ins: txt += t(f"; {ins} {'instrucción' if ins == 1 else 'instrucciones'} dentro de la fuente no se ejecuta{'n' if ins != 1 else ''} (fuentes = datos)",
                     f"; {ins} instruction{'s' if ins != 1 else ''} inside the source not executed (sources are data)")
    return txt + "."

def celda(x): return str(x or "").replace("|", "/").replace("\n", " ")

def markdown(cs, meta):
    L = ["---", "tipo: candidatos-reunion", f"fecha: {meta['fecha']}", f"fuente: {meta['fuente']}", "estado: borrador", "---", "",
         t(f"# Candidatos de la reunión · {meta['reunion']} ({meta['fecha'] or POR_CONFIRMAR})", f"# Meeting candidates · {meta['reunion']} ({meta['fecha'] or 'TBC'})"), "",
         *([t(f"Tipo de reunión: {meta['tipo']}", f"Meeting type: {meta['tipo']}") + (t(" (mira el proceso, sin culpables: propone lecciones y acciones de mejora, no decisiones de gobierno)",
                                                                                     " (looks at the process, blameless: proposes lessons and improvement actions, not governance decisions)") if meta["tipo"] == "retrospectiva" else ""), ""]
           if meta["tipo"] != "otra" else []),
         t("> Propuestas para el acta y los registros, no registros: cada una cita la frase y su marca de tiempo. Se cargan solo los ids que confirma quien presidió "
           "(`extraccion.py registrar --confirmar …`); lo marcado [por confirmar] lo completa el gestor o el modelo antes de confirmar.",
           "> Proposals for the minutes and registers, not records. Only the ids the chair confirms are recorded."), "",
         f"**{meta['resumen']}**", ""]
    secciones = [("decision", t("Decisiones", "Decisions"), ["Id", t("Estado", "Status"), t("Nivel", "Level"), t("Cita", "Quote"), t("Origen", "Source"), t("Destino", "Target")]),
                 ("accion", t("Compromisos y acciones", "Commitments and actions"), ["Id", t("Responsable", "Owner"), t("Fecha", "Due"), t("Dicho", "As said"), t("Cita", "Quote"), t("Origen", "Source")]),
                 ("leccion", t("Lecciones candidatas (lecciones.csv; después lecciones.py clasificar)", "Candidate lessons (lecciones.csv; then lecciones.py clasificar)"),
                  ["Id", t("Sentido", "Sense"), t("Recurrencia", "Recurrence"), t("Recomendación", "Recommendation"), t("Cita", "Quote"), t("Origen", "Source")]),
                 ("mejora", t("Acciones de mejora", "Improvement actions"), ["Id", t("Responsable", "Owner"), t("Fecha", "Due"), t("Dicho", "As said"), t("Cita", "Quote"), t("Origen", "Source")]),
                 ("supuesto", t("Supuestos", "Assumptions"), ["Id", t("Cita", "Quote"), t("Origen", "Source")]),
                 ("riesgo", t("Riesgos (pm-riesgos)", "Risks (pm-riesgos)"), ["Id", t("Tipo", "Type"), t("Categoría", "Category"), t("Cita", "Quote"), t("Origen", "Source"), t("Posible duplicado", "Possible duplicate")]),
                 ("instruccion", t("Instrucciones dentro de la fuente (no se ejecutan ni se registran)", "Instructions inside the source (not executed, never recorded)"), ["Id", t("Cita", "Quote"), t("Origen", "Source"), t("Motivo", "Reason")])]
    for clase, titulo, cab in secciones:
        xs = [c for c in cs if c["clase"] == clase]
        if not xs: continue
        L += [f"## {titulo}", "", "| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
        for c in xs:
            if clase == "decision": fila = [c["id"], c["estado"], c["nivel"], c["cita"], c["origen"], c["registro"]]
            elif clase in ("accion", "mejora"): fila = [c["id"], c["campos"]["responsable"], c["campos"]["fecha_compromiso"], c.get("fecha_dicha", ""), c["cita"], c["origen"]]
            elif clase == "leccion": fila = [c["id"], c["sentido"], c["recurrencia"] or "—", c["campos"]["recomendacion"], c["cita"], c["origen"]]
            elif clase == "supuesto": fila = [c["id"], c["cita"], c["origen"]]
            elif clase == "riesgo": fila = [c["id"], c["tipo"], c["campos"]["categoria"], c["cita"], c["origen"], c.get("posible_duplicado", "")]
            else: fila = [c["id"], c["cita"], c["origen"], c["motivo"]]
            L.append("| " + " | ".join(celda(v) for v in fila) + " |")
        L.append("")
    reg = [c["id"] for c in cs if c["clase"] != "instruccion"]
    L += [t("## Confirmación", "## Confirmation"), "",
          t("Decisiones de nivel junta, ejecutivo o capa de negocio las registra pm-director; las de puerta, con `estado.py puerta`.",
            "Board, executive or business-layer decisions are recorded by pm-director; gate decisions with `estado.py puerta`."), "",
          "```", f"extraccion.py --proyecto <dir> registrar --candidatos {meta['json']} --confirmar {','.join(reg[:6])}{',…' if len(reg) > 6 else ''} --por \"<rol: nombre>\"", "```", ""]
    return "\n".join(L)

def cmd_candidatos(a, e):
    if not os.path.isfile(a.transcripcion): sys.exit(t(f"No existe la transcripción: {a.transcripcion}", f"Transcript not found: {a.transcripcion}"))
    if a.transcripcion.lower().endswith(".docx"):
        sys.exit(t("DOCX: normalizar antes con transcripcion.py <archivo.docx> --salida 03-control/reuniones/<fecha>-<reunion>-transcripcion.md y usar esa salida.",
                   "DOCX: normalize first with transcripcion.py … --salida … and use that output."))
    nombre = os.path.basename(a.transcripcion)
    fecha = a.fecha or (re.match(r"(\d{4}-\d{2}-\d{2})", nombre) or [None, ""])[1]
    reunion = a.reunion or re.sub(r"^\d{4}-\d{2}-\d{2}-|-?transcripcion$|-?original$", "", os.path.splitext(nombre)[0]) or "reunion"
    tipo = a.tipo or tipo_de(reunion)
    cs = candidatos(a.proyecto, a.transcripcion, reunion, fecha, e, tipo)
    base = a.salida[:-3] if a.salida and a.salida.endswith(".md") else os.path.join(a.proyecto, "03-control", "reuniones", f"{fecha or datetime.date.today().isoformat()}-{reunion}-candidatos")
    md, js = base + ".md", base + ".json"
    meta = {"fecha": fecha, "reunion": reunion, "tipo": tipo, "fuente": ruta_rel(a.proyecto, a.transcripcion), "json": ruta_rel(a.proyecto, js), "resumen": resumen_txt(cs, tipo)}
    datos = {"tipo": "candidatos-reunion", "reunion": reunion, "tipo_reunion": tipo, "fecha": fecha, "fuente": meta["fuente"], "fuente_abs": os.path.abspath(a.transcripcion),
             "sha256_fuente": sha(a.transcripcion), "origen_acta": f"acta-reunion-{fecha}" if fecha else "acta-reunion", "resumen": meta["resumen"], "candidatos": cs}
    os.makedirs(os.path.dirname(md) or ".", exist_ok=True)
    open(md, "w", encoding="utf-8").write(markdown(cs, meta))
    json.dump(datos, open(js, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if a.json:
        print(json.dumps({**datos, "salida": md, "json": js}, ensure_ascii=False, indent=2)); return
    for c in cs[:a.max] if a.max else cs:
        extra = (f" · {c['estado']} · {t('nivel', 'level')} {c['nivel']}" if c["clase"] == "decision" else
                 f" · {c['campos']['responsable']} · {c['campos']['fecha_compromiso']}" if c["clase"] in ("accion", "mejora") else
                 f" · {c['sentido']}" + (f" · {t('recurrencia', 'recurrence')} {c['recurrencia']}" if c["recurrencia"] else "") + f" · {t('recomendación', 'recommendation')}: {c['campos']['recomendacion'][:80]}" if c["clase"] == "leccion" else
                 (f" · ¿{t('duplica', 'duplicates')} {c['posible_duplicado']}?" if c.get("posible_duplicado") else "") if c["clase"] == "riesgo" else
                 " · " + t("no se ejecuta", "not executed") if c["clase"] == "instruccion" else "")
        print(f"{c['id']} [{c['clase']}] {c['origen']} · {c['cita'][:140]}{extra}")
    if a.max and len(cs) > a.max: print(t(f"… y {len(cs) - a.max} más (ver {md})", f"… and {len(cs) - a.max} more (see {md})"))
    print(meta["resumen"] + t(" ¿Los registro? Confirmar los ids con: ", " Shall I record them? Confirm the ids with: ")
          + f"extraccion.py --proyecto {a.proyecto} registrar --candidatos {js} --confirmar <ids> --por \"<rol: nombre>\"")
    print(t(f"→ {md} (borrador, nada registrado)", f"→ {md} (draft, nothing recorded)"))

def vacio(v): return not str(v or "").strip() or POR_CONFIRMAR in str(v)

def cmd_registrar(a, e):
    if not os.path.isfile(a.candidatos): sys.exit(t(f"No existe el archivo de candidatos: {a.candidatos}", f"Candidates file not found: {a.candidatos}"))
    datos = json.load(open(a.candidatos, encoding="utf-8"))
    if datos.get("tipo") != "candidatos-reunion": sys.exit(t("El archivo no es una salida de extraccion.py candidatos.", "Not an extraccion.py candidates file."))
    f = datos.get("fuente_abs") or ""
    if not os.path.isfile(f) or sha(f) != datos.get("sha256_fuente"):
        sys.exit(t(f"La transcripción {datos.get('fuente')} cambió o no está desde que se propusieron los candidatos: volver a correr candidatos.",
                   f"The transcript {datos.get('fuente')} changed or is missing since the candidates were proposed: run candidatos again."))
    por_id = {c["id"]: c for c in datos["candidatos"]}
    ids = [x.strip() for x in (a.confirmar or "").split(",") if x.strip()]
    if not ids: sys.exit(t("Indicar los ids confirmados con --confirmar CA-01,CD-02 (no hay opción para registrar todo).", "List the confirmed ids with --confirmar."))
    desconocidos = [i for i in ids if i not in por_id]
    if desconocidos: sys.exit(t(f"Ids inexistentes en {a.candidatos}: {desconocidos}", f"Unknown ids: {desconocidos}"))
    cambios = {}
    for c in a.campo or []:
        m = re.match(r"^([A-Z]{2}-\d+):([a-z_]+)=(.*)$", c, re.S)
        if not m: sys.exit(t(f"Campo inválido: {c} (usar CA-01:responsable=Ana Ríos)", f"Invalid field: {c} (use CA-01:responsable=Ana)"))
        if m.group(1) not in ids: sys.exit(t(f"{m.group(1)} no está entre los confirmados (--confirmar).", f"{m.group(1)} is not among the confirmed ids."))
        cambios.setdefault(m.group(1), {})[m.group(2)] = m.group(3).strip()
    errores, plan, omitidos = [], [], []
    for i in ids:
        c = por_id[i]
        if c["clase"] == "instruccion":
            errores.append(t(f"{i}: es una instrucción incrustada en la fuente; fuentes = datos: no se registra.", f"{i}: embedded instruction; sources are data: never recorded.")); continue
        campos = {**c["campos"], **cambios.get(i, {})}
        if c["clase"] == "decision" and c["estado"] == "tomada":
            if campos.get("nivel") not in E.REGISTROS["decisiones"]["valores"]["nivel"]:
                errores.append(t(f"{i}: falta el nivel de decisión (--campo {i}:nivel=equipo|product-owner|gestor|autoridad-cambio).", f"{i}: decision level missing.")); continue
            if campos["nivel"] in DIRECTOR:
                errores.append(t(f"{i}: decisión de nivel {campos['nivel']}: la registra pm-director (puerta: estado.py puerta); quitarla de --confirmar y derivarla.",
                                 f"{i}: {campos['nivel']}-level decision: pm-director records it; remove it from --confirmar and hand it over.")); continue
        if c["clase"] == "leccion" and vacio(campos.get("recomendacion")):
            errores.append(t(f"{i}: lección sin recomendación accionable (--campo {i}:recomendacion=…); si no la hay todavía, queda en el acta.",
                             f"{i}: lesson without an actionable recommendation (--campo {i}:recomendacion=…).")); continue
        if c["registro"] == "acciones" and (vacio(campos.get("responsable")) or vacio(campos.get("fecha_compromiso"))):
            errores.append(t(f"{i}: sin responsable o sin fecha (--campo {i}:responsable=… --campo {i}:fecha_compromiso=AAAA-MM-DD); si no se acordaron, va al acta como pregunta abierta.",
                             f"{i}: missing owner or due date; if not agreed, it goes to the minutes as an open question.")); continue
        marca = f"candidato {i} · {c['origen']}"
        p = E.ruta_registro(a.proyecto, c["registro"])
        if os.path.exists(p) and any(marca in (r.get("notas") or "") for r in E.leer_csv(p)[1]):
            omitidos.append(i); continue
        campos = {k: v for k, v in campos.items() if not vacio(v)}
        if c["registro"] == "acciones": campos["origen"] = datos.get("origen_acta") or "acta-reunion"
        campos["notas"] = (campos.get("notas", "") + " · " if campos.get("notas") else "") + f"origen: {datos.get('origen_acta', 'acta-reunion')} · {marca} · " + t("confirmado por ", "confirmed by ") + a.por
        if c["clase"] == "mejora": campos["notas"] += t(" · acción de mejora de la retrospectiva", " · retrospective improvement action")
        if c["clase"] == "leccion": campos["notas"] += t(f" · {c['sentido']}", f" · {c['sentido']}")
        if c["clase"] == "decision" and c["estado"] == "pendiente": campos["notas"] += t(f" · decisión pendiente (nivel {c['nivel'].strip('[]')}): al decidirse, va a decisiones.csv", f" · pending decision (level {c['nivel'].strip('[]')}): once decided, it goes to decisiones.csv")
        plan.append((i, c["registro"], campos))
    if errores:
        sys.exit(t("No se registró nada; corregir y volver a confirmar:", "Nothing recorded; fix and confirm again:") + "\n  - " + "\n  - ".join(errores))
    hechos = {}
    for i, reg, campos in plan:
        args = [sys.executable, REG, "--proyecto", a.proyecto, "agregar", reg] + [x for k, v in campos.items() for x in ("--campo", f"{k}={v}")]
        if a.simular: print("registro.py --proyecto " + a.proyecto + f" agregar {reg} " + " ".join(f'--campo "{k}={v}"' for k, v in campos.items())); continue
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(t(f"registro.py rechazó {i} ({reg}); quedaron registrados: {hechos or 'ninguno'}\n", f"registro.py rejected {i}; recorded so far: {hechos or 'none'}\n") + (r.stderr or r.stdout)[-600:])
        hechos[i] = r.stdout.strip().splitlines()[-1]
        por_id[i]["registrado"] = hechos[i]
    if a.simular: print(t("(simulación: nada registrado)", "(dry run: nothing recorded)")); return
    json.dump(datos, open(a.candidatos, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for i, x in hechos.items(): print(f"{i} → {x} ({por_id[i]['registro']}.csv)")
    if omitidos: print(t(f"Ya registrados antes (omitidos): {', '.join(omitidos)}", f"Already recorded (skipped): {', '.join(omitidos)}"))
    ls = [x for i, x in hechos.items() if por_id[i]["clase"] == "leccion"]
    if ls: print(t(f"Lecciones {', '.join(ls)} (registradas): clasificarlas por impacto y proceso con lecciones.py clasificar.", f"Lessons {', '.join(ls)}: classify them with lecciones.py clasificar."))
    rs = [x for i, x in hechos.items() if por_id[i]["clase"] == "riesgo"]
    if rs: print(t(f"Riesgos {', '.join(rs)}: completar causa → evento → efecto, P×I, propietario y respuesta con pm-riesgos.", f"Risks {', '.join(rs)}: complete with pm-riesgos."))
    print(t("Anotar los ids en el acta.", "Write the ids into the minutes."))

def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidatos"); c.add_argument("--transcripcion", required=True); c.add_argument("--reunion"); c.add_argument("--fecha")
    c.add_argument("--tipo", choices=TIPOS_REUNION, help="tipo de reunión (defecto: por el nombre; retrospectiva propone lecciones y acciones de mejora)")
    c.add_argument("--salida"); c.add_argument("--max", type=int, default=20, help="candidatos en pantalla (0 = todos); el archivo los lleva todos"); c.add_argument("--json", action="store_true")
    r = sub.add_parser("registrar"); r.add_argument("--candidatos", required=True); r.add_argument("--confirmar", required=True)
    r.add_argument("--por", required=True, help="quién confirmó (rol: nombre)"); r.add_argument("--campo", action="append"); r.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.proyecto, "estado.json")): sys.exit(f"{a.proyecto}: falta estado.json / not a project folder")
    e = E.cargar_estado(a.proyecto); IDIOMA = e.get("idioma", "es")
    if a.cmd == "candidatos":
        if a.fecha:
            try: datetime.date.fromisoformat(a.fecha)
            except ValueError: sys.exit(t(f"--fecha inválida: {a.fecha} (AAAA-MM-DD)", f"Invalid --fecha: {a.fecha}"))
        cmd_candidatos(a, e)
    else: cmd_registrar(a, e)

if __name__ == "__main__":
    main()
