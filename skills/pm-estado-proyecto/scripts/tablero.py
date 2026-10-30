#!/usr/bin/env python3
"""Tablero del proyecto en formato pm-tablero/1 (JSON) y HTML autocontenido; instantáneas congeladas e inmutables.
Project board in pm-tablero/1 format (JSON) and self-contained HTML; frozen, immutable snapshots.

Uso / Usage:
  tablero.py --proyecto ./p generar [--corte AAAA-MM-DD] [--json] [--html RUTA] [--origen URL] [--actor "<nombre o rol>"]
  tablero.py --proyecto ./p congelar --etiqueta "highlight de noviembre" [--por "<rol: nombre>"] [--actor "<nombre o rol>"]
  tablero.py --proyecto ./p listar [--json]
  tablero.py --proyecto ./p comparar ID_A ID_B|actual [--json]
(`--proyecto` también se acepta después del subcomando / also accepted after the subcommand.)

Es una vista derivada, sin datos propios: llama en el mismo proceso a las funciones que ya calculan cada cosa
(`estado.py radar` y `productos`, `puertas.py estado`, `registro.py propuestas`) y lee estado.json, los registros de control
y la bitácora. Tres vistas (ciclo y puertas, atención, entrega en dos niveles) y los artefactos clave por grupo; cada
tarjeta lleva un id estable (`ref`: R-003, clave de artefacto, puerta:<tipo>:<etapa>, id de producto, P-###) y un enlace
relativo `ficha/<ref>` que arma el portal (SPEC §1.10.17).

- generar: solo lectura (no toma el bloqueo ni escribe; también sobre una carpeta de solo lectura), salvo el HTML de
  `--html RUTA`, que nunca va a 03-control/reportes/tableros/ ni a 03-control/registros/. Sin --json ni --html, un resumen.
  `--origen URL` (http o https): las tarjetas del HTML enlazan a <URL>/p/<proyecto>/ficha/<ref>; sin origen, al archivo
  fuente con una ruta relativa.
- congelar: escribe 03-control/reportes/tableros/<fecha>-<etiqueta>.json y .html con el mecanismo común (bloqueo,
  escritura atómica y bitácora con huella). Inmutables: si el id existe, se agrega -2, -3. `estado.py puerta` congela
  solo el tablero previo a cada decisión (y `estado.py cierre --prematuro`).
- listar: instantáneas con id, etiqueta, puerta, etapa, decisión, sha256 y si coincide con la bitácora.
- comparar: tarjetas que entraron, salieron o cambiaron de columna o estado entre dos instantáneas (`actual` = ahora).
- --actor (generar, congelar): solo lo de una persona (nombre, "<rol: nombre>", rol o ST-###, sin distinguir mayúsculas
  ni acentos): sus elementos R, A, C o I de raci.csv y lo que tiene a cargo, pidió o decidió en los registros; el ciclo
  y las puertas son comunes. Totales recalculados; bloque `actor` con nombre, rol y letras. Actor inexistente → código 1.
Sin montos ni datos de interesados en el tablero; la ficha de cada tarjeta está en la fuente (o en el portal de pm-kb).

API pública (Python, para pm-kb y otros consumidores; todas de solo lectura salvo congelar):
- construir(proyecto, corte=None, instantanea=None, actor=None) → dict pm-tablero/1 (lo que imprime `generar --json`).
- actores(proyecto) → [{id, nombre, rol, roles}]: las personas que acepta --actor.
- filtrar_actor(datos, proyecto, actor) → copia de `datos` (tablero actual o instantánea) con solo lo de ese actor;
  actor vacío, inexistente o ambiguo → ActorInvalido (ValueError).
- congelar(...), listar(proyecto), comparar(a, b): como los subcomandos del mismo nombre.
"""
import argparse, base64, contextlib, datetime, hashlib, json, os, re, sys, unicodedata, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esquema as E

FORMATO = E.FORMATO_TABLERO
FLUJO_PRODUCTOS = ["no-iniciado", "en-desarrollo", "en-revision", "aprobado", "aceptado"]
EXCEPCION_PRODUCTOS = ["fuera-especificacion", "con-concesion"]
FLUJOS = {   # registro: (columnas visibles en orden, estados terminales que se cuentan sin dibujar)
    "cambios": (["abierto", "en-evaluacion", "pendiente-decision", "aprobado", "implementado"], ["rechazado", "diferido", "cerrado"]),
    "issues": (["abierto", "en-evaluacion", "en-accion", "pendiente-cambio", "escalado"], ["resuelto", "cerrado"]),
    "acciones": (["abierta", "en-curso"], ["completada", "cancelada"]),
}
TIPO_FILA = {"cambios": "cambio", "issues": "issue", "acciones": "accion"}
TITULO = {"cambios": "titulo", "issues": "titulo", "acciones": "descripcion"}
RESPONSABLE = {"cambios": "solicitante", "issues": "responsable", "acciones": "responsable"}
GRUPOS_ATENCION = ("decidir", "escalar", "desbloquear", "vigilar")
EVENTOS_ETAPA = ("decision-ad-hoc", "autorizar-plan-excepcion")    # decisiones dentro de una etapa, no la cierran
NIVELES_JUNTA = ("junta", "ejecutivo")
ID_FILA = re.compile(r"^(?:R|I|C|D|S|L|Q|A|X|P)-\d{3,}$")
ID_INSTANTANEA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]{0,80}$")
MAX_NOMBRE, MAX_DESCRIPCION, MAX_EVENTOS = 80, 140, 8
GRUPOS_ARTEFACTOS = [("generales", "Generales del proyecto", "Project-wide"), ("ciclo", "Del ciclo actual", "Current cycle"),
                     ("cierre-etapas", "Cierre de etapas anteriores", "Closure of previous stages"),
                     ("decisiones-junta", "Decisiones de la junta", "Board decisions")]
GENERALES = ("mandato", "project-brief", "business-case", "pid", "acta-constitucion", "plan-proyecto", "tolerancias-y-autoridad",
             "matriz-raci", "descripcion-producto-proyecto")


def _t(L, es, en): return E.t(L, es, en)


def _hoy(): return datetime.date.today().isoformat()


def _fecha_valida(x, L):
    if x is None: return None
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x): raise ValueError
        datetime.date.fromisoformat(x); return x
    except ValueError:
        sys.exit(_t(L, f"Fecha inválida: {x} (AAAA-MM-DD).", f"Invalid date: {x} (YYYY-MM-DD)."))


def _dias(fecha, corte):
    try: return (datetime.date.fromisoformat(corte) - datetime.date.fromisoformat((fecha or "")[:10])).days
    except ValueError: return None


# ---------------------------------------------------------------- textos de las tarjetas (SPEC §1.10.17)
_MILES = {"es": r"[1-9]\d{0,2}(?:\.\d{3})+(?:,\d+)?", "en": r"[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?"}


def sin_montos(x, L="es"):
    """Reemplaza las cifras con forma de monto (con separador de miles, de 4 o más dígitos que no son un año, o detrás de
    costo, monto, importe, presupuesto o una clave de presupuesto) por «[monto]» / «[amount]»."""
    m = "[amount]" if L == "en" else "[monto]"
    s = re.sub(r"(?<![\w.,/:-])" + _MILES["en" if L == "en" else "es"] + r"(?![\w/-])", m, str(x or ""))
    s = re.sub(r"(?<![\w.,/:-])(?!(?:19|20)\d\d(?!\d))\d{4,}(?:[.,]\d+)?(?![\w/-])", m, s)
    s = re.sub(r"\b(costo|cost|monto|amount|importe|presupuesto|budget)(\s*[:=]?\s*)\d[\d.,]*", lambda g: g.group(1) + g.group(2) + m, s, flags=re.I)
    return re.sub(r"\b(cambio|riesgo|gestion|limite_autoridad_cambio)=\d[\d.,]*", lambda g: g.group(1) + "=" + m, s)


def _corto(x, n):
    x = " ".join(str(x or "").split())
    return x if len(x) <= n else x[:n - 1].rstrip() + "…"


def _limpio(x, n, L): return _corto(sin_montos(x, L), n)


def _tarjeta(ref, tipo, nombre, descripcion, estado, columna, L, responsable="", fecha="", senales=None, fuente="", **extra):
    """Forma común de toda tarjeta: la usa el portal (y un filtro posterior por actor, que cruza `ref` con raci.csv y
    `responsable` con las personas)."""
    return {"ref": ref, "tipo": tipo, "nombre": _limpio(nombre, MAX_NOMBRE, L), "descripcion": _limpio(descripcion, MAX_DESCRIPCION, L),
            "estado": estado or "", "columna": columna or "", "responsable": _corto(responsable, 60), "fecha": fecha or "",
            "senales": list(senales or []), "enlace": "ficha/" + urllib.parse.quote(ref, safe=":"), "fuente": fuente or "", **extra}


def _desc(*partes): return " · ".join(str(p) for p in partes if p not in (None, ""))


# ---------------------------------------------------------------- fuentes (en proceso, sin bloqueo)
@contextlib.contextmanager
def _memo_puertas(PU):
    """radar y estado_puertas verifican la misma próxima puerta (corre sanidad.py --rapido): una sola vez por tablero."""
    original, cache = PU.evaluar_detalle, {}
    def memo(proyecto, e, tipo, tol_nueva=None):
        if tol_nueva: return original(proyecto, e, tipo, tol_nueva)
        k = (os.path.realpath(proyecto), tipo)
        if k not in cache: cache[k] = original(proyecto, e, tipo)
        return cache[k]
    PU.evaluar_detalle = memo
    try: yield
    finally: PU.evaluar_detalle = original


def huella(proyecto):
    """sha256 (16 caracteres) del contenido de estado.json, la bitácora, los registros y las propuestas: cambia con
    cualquier escritura de gobierno (sirve para saber si un tablero publicado quedó viejo)."""
    h = hashlib.sha256()
    rutas = [os.path.join(proyecto, "estado.json"), os.path.join(proyecto, E.ARCHIVO_BITACORA)]
    for sub, patron in (("registros", r".+\.csv"), ("propuestas", r"P-\d+\.json")):
        d = os.path.join(proyecto, "03-control", sub)
        rutas += [os.path.join(d, x) for x in (sorted(os.listdir(d)) if os.path.isdir(d) else []) if re.fullmatch(patron, x)]
    for r in rutas:
        b = E._leer_bytes(r)
        if b is not None: h.update(os.path.relpath(r, proyecto).replace(os.sep, "/").encode() + b"\0" + E._sha(b).encode() + b"\n")
    return h.hexdigest()[:16]


def _eventos(proyecto):
    lineas = E.leer_bitacora(proyecto); ev = []
    for raw in reversed(lineas):
        if len(ev) >= MAX_EVENTOS: break
        d = E._json_o_none(raw)
        if not d: continue
        reg = d.get("registro") or ""
        if reg in E.REGISTROS_SIN_TABLERO or any((d.get("archivo") or "").endswith(f"/{r}.csv") for r in E.REGISTROS_SIN_TABLERO): continue
        ev.append({"n": d.get("n"), "fecha": (d.get("fecha") or "")[:16].replace("T", " "), "operacion": d.get("operacion", ""),
                   "archivo": d.get("archivo", ""), "registro": reg, "ids": [str(x) for x in (d.get("ids") or [])[:4]], "por": _corto(d.get("por"), 60)})
    return ev, len(lineas)


# ---------------------------------------------------------------- bloques del tablero
def _nombre_columna(k, n, etapa, L):
    if k == 0: return _t(L, "Puesta en marcha (SU)", "Starting up (SU)")
    base = _t(L, "Iniciación (IP)", "Initiating (IP)") if k == 1 else _t(L, f"Etapa {k}", f"Stage {k}")
    nombre = str(etapa.get("nombre") or "")
    propio = k == n and nombre and nombre not in ("Iniciación", "Initiation", f"Etapa {k}", f"Stage {k}")
    return base + (f" · {nombre}" if propio else "")


def _ciclo(e, pu, radar_items, L, avisos):
    etapa = e.get("etapa_actual") or {}
    n = int(etapa.get("numero") or 0); fase = e.get("fase", "")
    hechas = (pu or {}).get("puertas") or []; prox = (pu or {}).get("proxima") or None
    cuenta, refs = {}, []
    for p in hechas:                      # puerta:<tipo>:<etapa>[:k] — estable: la lista de puertas solo se anexa
        k_ = (p.get("tipo"), p.get("etapa")); cuenta[k_] = cuenta.get(k_, 0) + 1
        refs.append(f"puerta:{p.get('tipo')}:{p.get('etapa')}" + (f":{cuenta[k_]}" if cuenta[k_] > 1 else ""))
    def carta(p, ref):
        abiertas = bool(p.get("condiciones")) and not p.get("condiciones_cumplidas") and p.get("decision") in ("aprobado", "condicionado")
        return _tarjeta(ref, "puerta", p.get("tipo"), _desc(p.get("decision"), p.get("fecha"), p.get("decision_id"), p.get("por")), p.get("decision"),
                        f"etapa-{p.get('etapa')}", L, responsable=p.get("por", ""), fecha=p.get("fecha", ""),
                        senales=(["forzada"] if p.get("forzada") else []) + (["condiciones-abiertas"] if abiertas else []),
                        fuente=p.get("lista") or "03-control/registros/decisiones.csv", puerta=p.get("tipo"), etapa=p.get("etapa"),
                        decision=p.get("decision", ""), decision_id=p.get("decision_id", ""), con_condiciones=bool(p.get("condiciones")),
                        condiciones_cumplidas=p.get("condiciones_cumplidas", ""), forzada=bool(p.get("forzada")))
    total = max(n, max([int(p.get("etapa") or 0) for p in hechas] + [0])) + (0 if fase in ("cierre", "cerrado") else 1)
    actual_k = n if fase in ("pre-proyecto", "inicio", "entrega") else None
    columnas = []
    def proxima_col():
        mismas = sum(1 for p in hechas if p.get("tipo") == prox.get("puerta") and p.get("etapa") == n)
        ref = f"puerta:{prox.get('puerta')}:{n}" + (f":{mismas + 1}" if mismas else "")
        hs = [{"severidad": h.get("severidad", ""), "id": h.get("id", ""), "mensaje": _limpio(h.get("mensaje"), MAX_DESCRIPCION, L)} for h in prox.get("hallazgos") or []]
        bl = sum(1 for h in hs if h["severidad"] == "bloqueo")
        c = _tarjeta(ref, "puerta", prox.get("puerta"), _desc(_t(L, "próxima puerta", "next gate"), _t(L, f"{bl} bloqueo(s)", f"{bl} blocker(s)") if bl else _t(L, "sin bloqueos", "no blockers")),
                     "proxima", f"etapa-{n}", L, senales=["bloqueada"] if bl else [], fuente=prox.get("lista") or "", puerta=prox.get("puerta"), etapa=n)
        return {"puerta": True, "estado": "proxima", "tipo": prox.get("puerta"), "tarjeta": c, "hallazgos": hs, "lista": prox.get("lista", "")}
    for k in range(total + 1):
        es_actual = k == actual_k
        col = {"numero": k, "nombre": _nombre_columna(k, n, etapa, L),
               "estado": "actual" if es_actual else ("hecha" if (k < n or fase in ("cierre", "cerrado")) and k <= n else "futura"),
               "eventos": [carta(p, r) for p, r in zip(hechas, refs) if p.get("etapa") == k and p.get("tipo") in EVENTOS_ETAPA]}
        if es_actual:
            col.update({"proceso": e.get("proceso_actual", ""), "inicio": etapa.get("inicio", ""), "fin_previsto": etapa.get("fin_previsto", ""),
                        "senales": [{"regla": i["regla"], "que": _limpio(i["que"], MAX_DESCRIPCION, L), "prioridad": i["prioridad"]}
                                    for i in radar_items if i["regla"][:3] in ("TOL", "CAM")],
                        "excepcion": e.get("excepcion_abierta", "")})
        columnas.append(col)
        salida = [carta(p, r) for p, r in zip(hechas, refs) if p.get("etapa") == k and p.get("tipo") not in EVENTOS_ETAPA and p.get("tipo") != "autorizar-cierre"]
        if salida: columnas.append({"puerta": True, "estado": "hecha", "decisiones": salida})
        if es_actual and prox: columnas.append(proxima_col())
    cierre = {"numero": None, "nombre": _t(L, "Cierre (CP)", "Closing (CP)"), "estado": {"cierre": "actual", "cerrado": "hecha"}.get(fase, "futura"),
              "eventos": [], **({"proceso": e.get("proceso_actual", ""), "excepcion": e.get("excepcion_abierta", "")} if fase == "cierre" else {})}
    columnas.append(cierre)
    fin = [carta(p, r) for p, r in zip(hechas, refs) if p.get("tipo") == "autorizar-cierre"]
    if fin: columnas.append({"puerta": True, "estado": "hecha", "decisiones": fin})
    if fase == "cierre" and prox: columnas.append(proxima_col())
    return {"fase": fase, "proceso": e.get("proceso_actual", ""), "etapa": n, "nombre_etapa": etapa.get("nombre", ""),
            "inicio": etapa.get("inicio", ""), "fin_previsto": etapa.get("fin_previsto", ""), "excepcion": e.get("excepcion_abierta", ""),
            "cierre_prematuro": bool(E.cierre_prematuro(e)), "columnas": columnas,
            "condiciones_abiertas": [r for p, r in zip(hechas, refs) if p.get("decision") in ("condicionado", "aprobado") and p.get("condiciones") and not p.get("condiciones_cumplidas")],
            "forzadas": [r for p, r in zip(hechas, refs) if p.get("forzada")]}


def _ref_atencion(i, ciclo):
    """Id estable del elemento al que apunta un ítem del radar (fila, puerta, excepción) o <regla>:<id> si no lo hay."""
    x = str(i.get("id") or "")
    if ID_FILA.match(x): return x
    if x in E.PUERTAS:
        cartas = [c.get("tarjeta") for c in ciclo["columnas"] if c.get("puerta") and c.get("estado") == "proxima"] + \
                 [d for c in ciclo["columnas"] if c.get("puerta") for d in c.get("decisiones") or []] + \
                 [d for c in ciclo["columnas"] if not c.get("puerta") for d in c.get("eventos") or []]
        if i.get("regla") == "RAD-07":
            prox = [c for c in cartas[:1] if c and c.get("puerta") == x]
            if prox: return prox[0]["ref"]
        hechas = [c for c in cartas if c and c.get("puerta") == x and c.get("estado") != "proxima"]
        if hechas: return hechas[-1]["ref"]
    return f"{i.get('regla')}:{x}"


def _fuente_ref(ref, ciclo):
    """Archivo fuente de una fila (por su prefijo) o de una puerta (su lista de verificación); "" si no se sabe."""
    pref = ref.split("-")[0]
    reg = next((r for r, s in E.REGISTROS.items() if s["prefijo"] == pref), None)
    if reg and reg not in E.REGISTROS_SIN_TABLERO: return f"03-control/registros/{reg}.csv"
    if pref == "P": return f"03-control/propuestas/{ref}.json"
    if ref.startswith("puerta:"):
        for c in ciclo["columnas"]:
            for x in (c.get("decisiones") or []) + (c.get("eventos") or []) + ([c["tarjeta"]] if c.get("tarjeta") else []):
                if x.get("ref") == ref: return x.get("fuente", "")
    return ""


def _atencion(radar, ciclo, corte, L):
    items, en_fila = [], {}
    for g in GRUPOS_ATENCION:
        for i in (radar.get("items") or {}).get(g, []):
            ref = _ref_atencion(i, ciclo)
            nombre = _t(L, f"condiciones abiertas de {i.get('id')}", f"open conditions of {i.get('id')}") if i.get("regla") == "EST-12" else i.get("que")
            c = _tarjeta(ref, "atencion", nombre, _desc(i.get("regla"), f"P{i.get('prioridad')}", i.get("responsable"), "→ " + str(i.get("siguiente") or "")),
                         g, g, L, responsable=i.get("responsable", ""), fecha=i.get("fecha", ""),
                         senales=["bloqueada"] if g == "desbloquear" else [], fuente=_fuente_ref(ref, ciclo), grupo=g, prioridad=i.get("prioridad"), regla=i.get("regla"),
                         id=str(i.get("id") or ""), edad=_dias(i.get("fecha"), corte), siguiente=_limpio(i.get("siguiente"), 200, L))
            items.append(c); en_fila.setdefault(ref, set()).add(g)
    return {"totales": {g: int((radar.get("totales") or {}).get(g, 0)) for g in GRUPOS_ATENCION}, "proxima_puerta": radar.get("proxima_puerta", ""),
            "excepcion_procede": bool(radar.get("excepcion_procede")), "items": items}, en_fila


def _productos(prods, L):
    tarjetas = []
    for p in (prods or {}).get("productos", []):
        fuente = "02-planificacion/backlog.csv" if p.get("fuente") == "backlog" else "02-planificacion/wbs.csv"
        nd = len(p.get("discrepancias") or [])
        tarjetas.append(_tarjeta(str(p.get("id")), "producto", p.get("titulo") or p.get("id"),
                                 _desc(p.get("estado"), (p.get("prioridad") or "").upper(), p.get("q_vigente"), _t(L, f"{nd} discrepancia(s)", f"{nd} discrepancy(ies)") if nd else ""),
                                 p.get("estado"), p.get("estado"), L, senales=["discrepancias"] if nd else [], fuente=fuente,
                                 prioridad=p.get("prioridad", ""), paquetes=list(p.get("paquetes") or [])[:3], q=p.get("q_vigente", ""), discrepancias=nd))
    return {"columnas": FLUJO_PRODUCTOS, "excepcion": EXCEPCION_PRODUCTOS, "fuente": (prods or {}).get("fuente", ""), "tarjetas": tarjetas,
            "conteos": (prods or {}).get("conteos", {})}


def _control(proyecto, corte, propuestas, en_atencion, L):
    out = {}
    pend = [p for p in propuestas or [] if p.get("estado") == "pendiente"]
    objetivos = {p.get("objetivo") for p in pend if p.get("objetivo")}
    for reg, (flujo, terminales) in FLUJOS.items():
        ruta = E.ruta_registro(proyecto, reg); rel = f"03-control/registros/{reg}.csv"
        filas = E.leer_csv(ruta, L)[1] if os.path.exists(ruta) else []
        tarjetas, cerrados, estados = [], {}, {}
        for f in filas:
            est = (f.get("estado") or "").strip(); estados[f.get("id")] = est
            if est not in flujo:
                cerrados[est or "-"] = cerrados.get(est or "-", 0) + 1; continue
            fecha = f.get("fecha") or ""; vence = f.get("fecha_compromiso", "") if reg == "acciones" else ""
            sen = (["vencida"] if vence and vence < corte else []) + (["bloqueada"] if "desbloquear" in en_atencion.get(f.get("id"), ()) else []) + \
                  (["propuesta-pendiente"] if f.get("id") in objetivos else [])
            resp = f.get(RESPONSABLE[reg], "")
            tarjetas.append(_tarjeta(f.get("id", ""), TIPO_FILA[reg], f.get(TITULO[reg]) or f.get("descripcion") or f.get("id"),
                                     _desc(est, resp, f.get("prioridad"), (_t(L, "vence ", "due ") + vence) if vence else fecha), est, est, L,
                                     responsable=resp, fecha=fecha, senales=sen, fuente=rel, edad=_dias(fecha, corte), vence=vence,
                                     prioridad=f.get("prioridad", ""), decide=f.get("decidido_por", "")))
        sombras = []
        for p in pend:
            if p.get("registro") != reg: continue
            destino = (p.get("campos") or {}).get("estado") or estados.get(p.get("objetivo")) or flujo[0]
            nombre = p.get("motivo") or "; ".join(f"{k}={v}" for k, v in (p.get("campos") or {}).items())
            sombras.append(_tarjeta(p.get("id", ""), "propuesta", nombre,
                                    _desc(p.get("objetivo") or _t(L, "alta", "new row"), _t(L, "propone ", "proposed by ") + str(p.get("propuesto_por") or "—"),
                                          _t(L, "espera aprobación", "awaiting approval")),
                                    "pendiente", destino if destino in flujo else flujo[0], L, responsable=p.get("propuesto_por", ""),
                                    fecha=(p.get("fecha") or "")[:10], senales=["propuesta-pendiente"], fuente=f"03-control/propuestas/{p.get('id')}.json",
                                    objetivo=p.get("objetivo") or "", registro=reg, al_aprobar=(p.get("al_aprobar") or {}).get("resultado", "")))
        out[reg] = {"columnas": flujo, "terminales": terminales, "tarjetas": tarjetas, "cerrados": cerrados, "propuestas": sombras}
    return out


def _grupo_artefacto(clave, e, prox):
    n = int((e.get("etapa_actual") or {}).get("numero") or 0)
    if clave in GENERALES or clave.startswith("enfoque-"): return "generales"
    m = re.fullmatch(r"(?:informe-fin-etapa|informe-lecciones-etapa|retrospectiva-etapa)-(\d+)", clave)
    if m: return "cierre-etapas" if int(m.group(1)) < n or e.get("fase") in ("cierre", "cerrado") else "ciclo"
    if clave == f"plan-etapa-{n}" or clave == f"plan-etapa-{n + 1}": return "ciclo"
    if re.fullmatch(r"(?:highlight-.+|informe-excepcion-X-\d+|plan-excepcion-X-\d+|acta-junta-.+)", clave): return "ciclo"
    if prox and clave.startswith(f"solicitud-{prox}"): return "ciclo"
    return None


def _anterior_aprobada(proyecto, clave, a):
    """Copia congelada de la última versión aprobada (00-direccion/historial/<clave>-v<versión>.<ext>), si la vigente no lo está."""
    if a.get("estado") == "aprobado": return ""
    if a.get("copia_congelada") and os.path.isfile(os.path.join(proyecto, a["copia_congelada"])): return a["copia_congelada"].replace(os.sep, "/")
    d = os.path.join(proyecto, "00-direccion", "historial")
    cand = sorted(x for x in (os.listdir(d) if os.path.isdir(d) else []) if re.fullmatch(re.escape(clave) + r"-v[^/\\]+", x))
    return f"00-direccion/historial/{cand[-1]}" if cand else ""


def _rel_dentro(proyecto, ruta):
    if not ruta or os.path.isabs(ruta): return ""
    base = os.path.realpath(proyecto); r = os.path.realpath(os.path.join(proyecto, ruta))
    return os.path.relpath(r, base).replace(os.sep, "/") if os.path.commonpath([base, r]) == base else ""


def _artefactos(proyecto, e, prox, L, avisos):
    """Artefactos clave por grupo (definición del portal §6): generales, del ciclo actual, cierre de etapas anteriores y
    decisiones vigentes de la junta. `elementos`: clave → tarjeta con estado, versión, aprobado_por, ruta, existe, grupo."""
    elementos, por_grupo = {}, {g: [] for g, _, _ in GRUPOS_ARTEFACTOS}
    arts = e.get("artefactos") or {}
    hl = sorted(k for k in arts if k.startswith("highlight-"))[-3:]       # los últimos highlights
    actas = sorted(k for k in arts if k.startswith("acta-junta-"))[-1:]
    exc = e.get("excepcion_abierta") or ""
    for clave, a in arts.items():
        g = _grupo_artefacto(clave, e, prox)
        if g is None or (clave.startswith("highlight-") and clave not in hl) or (clave.startswith("acta-junta-") and clave not in actas): continue
        if re.fullmatch(r"(?:informe|plan)-excepcion-X-\d+", clave) and exc and not clave.endswith(exc): continue
        ruta = a.get("ruta", "")
        existe = bool(ruta) and os.path.exists(os.path.join(proyecto, ruta))     # = sanidad ART-01 (una ruta absoluta se respeta)
        ant = _anterior_aprobada(proyecto, clave, a)
        sen = (["fuente-no-encontrada"] if not existe else []) + (["aprobada-anterior"] if ant else [])
        elementos[clave] = _tarjeta(clave, "artefacto", clave, _desc(a.get("estado"), ("v" + str(a["version"])) if a.get("version") else "",
                                                                     a.get("fecha"), a.get("aprobado_por"),
                                                                     _t(L, "fuente no encontrada", "source not found") if not existe else "",
                                                                     _t(L, "hay una versión aprobada anterior", "a previous approved version exists") if ant else ""),
                                    a.get("estado"), g, L, responsable=a.get("aprobado_por", ""), fecha=a.get("fecha", ""), senales=sen,
                                    fuente=_rel_dentro(proyecto, ruta) if existe else "", grupo=g, version=str(a.get("version") or ""),
                                    aprobado_por=a.get("aprobado_por", ""), ruta=ruta, existe=existe, aprobada_anterior=ant)
        por_grupo[g].append(clave)
    p = E.ruta_registro(proyecto, "decisiones")
    filas = E.leer_csv(p, L)[1] if os.path.exists(p) else []
    try:
        import vigencia as VG
        vig = set(VG.vigentes(filas))
    except Exception as x:
        vig = {f.get("id") for f in filas}; avisos.append(_t(L, f"vigencia de decisiones no disponible: {x}", f"decision validity not available: {x}"))
    for f in filas:
        if f.get("nivel") not in NIVELES_JUNTA or f.get("id") not in vig: continue
        nombre = (f.get("decision") or f.get("id") or "").split(" — ")[0]       # sin condiciones ni motivo (van en la ficha)
        elementos[f["id"]] = _tarjeta(f["id"], "decision", nombre, _desc(f.get("nivel"), f.get("fecha"), f.get("decidido_por")), "vigente",
                                      "decisiones-junta", L, responsable=f.get("decidido_por", ""), fecha=f.get("fecha", ""),
                                      fuente="03-control/registros/decisiones.csv", grupo="decisiones-junta", version="", aprobado_por=f.get("decidido_por", ""),
                                      ruta="03-control/registros/decisiones.csv", existe=True, aprobada_anterior="", nivel=f.get("nivel"))
        por_grupo["decisiones-junta"].append(f["id"])
    return {"grupos": [{"id": g, "nombre": _t(L, es, en), "claves": por_grupo[g]} for g, es, en in GRUPOS_ARTEFACTOS], "elementos": elementos}


# ---------------------------------------------------------------- tablero por actor (filtro RACI, SPEC §1.10.17)
# Roles de estado.json.roles: textos que los nombran (sin acentos ni mayúsculas) y etiqueta. La junta es un órgano
# colectivo: ejecutivo, usuarios sénior y proveedores sénior ven lo que el radar asigna a «junta».
ROLES_ACTOR = {
    "ejecutivo": (("ejecutivo", "ejecutiva", "executive"), "ejecutivo", "executive"),
    "usuario_senior": (("usuario senior", "usuaria senior", "senior user"), "usuario sénior", "senior user"),
    "proveedor_senior": (("proveedor senior", "proveedora senior", "senior supplier"), "proveedor sénior", "senior supplier"),
    "gestor_proyecto": (("gestor", "gestora", "gestor del proyecto", "gestor de proyecto", "project manager"), "gestor del proyecto", "project manager"),
    "product_owner": (("product owner", "dueno del producto", "duena del producto"), "product owner", "product owner"),
    "autoridad_cambio": (("autoridad de cambio", "change authority"), "autoridad de cambio", "change authority"),
    "aseguramiento": (("aseguramiento", "assurance", "project assurance"), "aseguramiento", "assurance"),
    "jefes_equipo": (("jefe de equipo", "jefa de equipo", "team manager"), "jefe de equipo", "team manager"),
    "soporte": (("soporte", "soporte del proyecto", "project support"), "soporte", "project support"),
}
ROLES_JUNTA = ("ejecutivo", "usuario_senior", "proveedor_senior")
# campos de cada registro que nombran a una persona (mismo criterio que `interesados.py vinculos`)
CAMPOS_ACTOR = {"riesgos": ("propietario", "ejecutor"), "issues": ("responsable", "decidido_por"), "cambios": ("solicitante", "decidido_por"),
                "acciones": ("responsable",), "decisiones": ("decidido_por",), "calidad": ("responsable_productor", "revisores", "aprobador"),
                "lecciones": ("responsable_seguimiento",), "supuestos": ("responsable",)}
LETRAS_RACI = ("R", "A", "C", "I")


def _palabras(x): return " ".join(re.findall(r"[a-z0-9]+", E._plano(x)))


def _contiene(nombre, texto):
    """¿`texto` nombra a `nombre`? (nombre completo como palabras seguidas, sin acentos ni mayúsculas)."""
    n = _palabras(nombre)
    return len(n) >= 3 and f" {n} " in f" {_palabras(texto)} "


def _filas(proyecto, reg, L):
    p = E.ruta_registro(proyecto, reg)
    return E.leer_csv(p, L)[1] if os.path.exists(p) else []


def _actores(proyecto, e, L):
    """Personas que pueden ser actor: las de stakeholders.csv (id, nombre, rol_proyecto) y las de estado.json.roles, unidas
    por nombre; `roles` = claves de estado.json.roles que ocupa."""
    cands = [{"id": s.get("id", ""), "nombre": (s.get("nombre") or "").strip(), "rol": (s.get("rol_proyecto") or "").strip(), "roles": []}
             for s in _filas(proyecto, "stakeholders", L) if (s.get("nombre") or "").strip()]
    for clave in ROLES_ACTOR:
        v = (e.get("roles") or {}).get(clave)
        for n in (v if isinstance(v, list) else re.split(r"[;,]", v or "")):
            n = str(n or "").split(":")[-1].strip()
            if not n: continue
            c = next((c for c in cands if E._plano(c["nombre"]) == E._plano(n)), None)
            if c is None:
                c = {"id": "", "nombre": n, "rol": "", "roles": []}; cands.append(c)
            if clave not in c["roles"]: c["roles"].append(clave)
    return cands


def _rol_actor(c, L):
    etiquetas = [_t(L, ROLES_ACTOR[k][1], ROLES_ACTOR[k][2]) for k in c["roles"] if E._plano(c["rol"]) not in ROLES_ACTOR[k][0]]
    partes = ([c["rol"]] if c["rol"] else []) + [x for x in etiquetas if E._plano(x) != E._plano(c["rol"])]
    return ", ".join(partes)


def _es_rol(c, texto):
    """¿`texto` (sin acentos) es el rol de `c`? Su rol_proyecto o un texto de un rol de estado.json que ocupa."""
    return bool(texto) and (texto == E._plano(c["rol"]) or any(texto in ROLES_ACTOR[k][0] for k in c["roles"]))


def resolver_actor(proyecto, e, texto, L):
    """Actor del tablero filtrado: ST-###, nombre (completo o una parte que lo identifique sin ambigüedad), «<rol: nombre>»
    o un rol (rol_proyecto de stakeholders.csv o un rol de estado.json.roles), sin distinguir mayúsculas ni acentos.
    Inexistente o ambiguo → mensaje y código 1."""
    txt = " ".join(str(texto or "").split())
    cands = _actores(proyecto, e, L)
    def lista(cs): return "; ".join(f"{c['id'] + ' ' if c['id'] else ''}{c['nombre']}" + (f" ({_rol_actor(c, L)})" if _rol_actor(c, L) else "") for c in cs[:12]) or "—"
    if not txt: sys.exit(_t(L, "--actor no puede estar vacío.", "--actor cannot be empty."))
    if re.fullmatch(r"(?i)ST-\d{3,}", txt):
        sel = [c for c in cands if c["id"] == txt.upper()]
    else:
        rol_t, _, nom_t = txt.rpartition(":"); rol_t, nom_t = E._plano(rol_t), E._plano(nom_t)
        sel = [c for c in cands if E._plano(c["nombre"]) == nom_t]                          # nombre completo
        if not sel: sel = [c for c in cands if _contiene(nom_t, c["nombre"])]              # parte del nombre («Ana»)
        if not sel and not rol_t: sel = [c for c in cands if _es_rol(c, nom_t)]           # un rol («ejecutivo»)
        if len(sel) > 1 and rol_t:                                                          # «<rol: nombre>» desempata
            por_rol = [c for c in sel if _es_rol(c, rol_t)]
            sel = por_rol or sel
    if not sel:
        sys.exit(_t(L, f"No hay ningún actor «{txt}» en stakeholders.csv ni en los roles de estado.json. Actores: {lista(cands)}.",
                    f"No actor «{txt}» in stakeholders.csv or in estado.json roles. Actors: {lista(cands)}."))
    if len(sel) > 1:
        sys.exit(_t(L, f"«{txt}» corresponde a {len(sel)} actores: {lista(sel)}. Usar el id ST-### o el nombre completo.",
                    f"«{txt}» matches {len(sel)} actors: {lista(sel)}. Use the ST-### id or the full name."))
    return sel[0]


def _filtrar_actor(d, proyecto, e, c, prods, L):
    """Deja en el tablero `d` solo lo del actor `c` (resolver_actor) y recalcula los totales. Del actor: los elementos de
    raci.csv donde es R, A, C o I; las filas que lo nombran en CAMPOS_ACTOR (acciones y riesgos de los que es responsable,
    propietario o ejecutor, issues y cambios que pidió, tiene a cargo o decidió, decisiones que tomó); los productos de la
    RACI (también por un código padre de la WBS o por su paquete de trabajo); los artefactos de la RACI o que aprobó; los
    ítems del radar sobre esos elementos o a su nombre (o a su rol, p. ej. «junta» para ejecutivo, usuarios y proveedores
    sénior), y en Entrega y Artefactos también las tarjetas de esos ítems (un cambio que espera la decisión de la junta); las propuestas que hizo o que tocan lo suyo; los eventos de la bitácora con su nombre o sus ids. El ciclo (fase,
    etapas, puertas y la próxima puerta con sus bloqueos) es contexto común y no se filtra."""
    raci = {}
    if c["id"]:
        for f in _filas(proyecto, "raci", L):
            if f.get("stakeholder_id") == c["id"] and f.get("rol") in LETRAS_RACI and f.get("elemento"): raci[f["elemento"].strip()] = f["rol"]
    alias = {E._plano(c["rol"])} if c["rol"] else set()
    for k in c["roles"]: alias.update(ROLES_ACTOR[k][0])
    if any(k in ROLES_JUNTA for k in c["roles"]): alias.update(("junta", "board"))
    alias.discard("")
    def nombra(texto):
        texto = str(texto or "")
        if not texto.strip(): return False
        if c["id"] and re.search(r"(?<![\w-])" + re.escape(c["id"]) + r"(?![\w-])", texto): return True
        if _contiene(c["nombre"], texto): return True
        return E._plano(re.sub(r"\([^)]*\)", "", texto)).strip(" :.-") in alias      # el campo nombra solo un rol suyo
    suyos, filas = set(), {}
    for reg, cols in CAMPOS_ACTOR.items():
        filas[reg] = _filas(proyecto, reg, L)
        suyos.update(f.get("id") for f in filas[reg] if f.get("id") and any(nombra(f.get(col)) for col in cols))
    def letra(ref, *mas):
        for x in (ref,) + mas:
            if x in raci: return raci[x]
        return ""
    def propio(ref): return ref in suyos or ref in raci
    def marcar(t_, l_=None): t_ = dict(t_); t_["raci"] = letra(t_["ref"]) if l_ is None else l_; return t_
    # atención
    at = d["atencion"]
    items = [marcar(i) for i in at["items"] if propio(i["ref"]) or propio(i.get("id", "")) or nombra(i.get("responsable"))]
    at.update(items=items, totales={g: sum(1 for i in items if i.get("grupo") == g) for g in GRUPOS_ATENCION})
    a_su_cargo = {i["ref"] for i in items}            # lo que el radar le pide (p. ej. un cambio que decide la junta)
    def propio_o_radar(ref): return propio(ref) or ref in a_su_cargo
    # productos (por su id, un código padre de la WBS o su paquete de trabajo)
    pq = {str(p.get("id")): list(p.get("paquetes") or []) for p in (prods or {}).get("productos", [])}
    def de_producto(ref):
        padres = [ref[:i] for i in range(len(ref)) if ref[i] == "."]
        return letra(ref, *(padres[::-1] + pq.get(ref, [])))
    P = d["entrega"]["productos"]
    P["tarjetas"] = [marcar(x, de_producto(x["ref"])) for x in P["tarjetas"] if de_producto(x["ref"])]
    total = len(P["tarjetas"])
    P["conteos"] = {**{k: sum(1 for x in P["tarjetas"] if x.get("estado") == k) for k in (P.get("conteos") or {}) if k != "total"},
                    **({"total": total} if "total" in (P.get("conteos") or {}) else {})}
    # control: cambios, issues y acciones (y los cerrados del actor), propuestas
    for reg, v in d["entrega"]["control"].items():
        v["tarjetas"] = [marcar(x) for x in v["tarjetas"] if propio_o_radar(x["ref"])]
        v["propuestas"] = [marcar(x, letra(x.get("objetivo", ""))) for x in v["propuestas"] if nombra(x.get("responsable")) or propio(x.get("objetivo", ""))]
        cerr = {}
        for f in filas.get(reg) or _filas(proyecto, reg, L):
            est = (f.get("estado") or "").strip()
            if est not in v["columnas"] and propio(f.get("id", "")): cerr[est or "-"] = cerr.get(est or "-", 0) + 1
        v["cerrados"] = cerr
    # artefactos clave (de la RACI o aprobados por el actor) y decisiones de la junta (las que tomó o tiene en la RACI)
    A = d["artefactos"]
    A["elementos"] = {k: marcar(x) for k, x in A["elementos"].items()
                      if propio_o_radar(k) or (x.get("tipo") == "artefacto" and nombra(x.get("aprobado_por")))}
    for g in A["grupos"]: g["claves"] = [k for k in g["claves"] if k in A["elementos"]]
    d["eventos"] = [x for x in d["eventos"] if nombra(x.get("por")) or any(propio(i) for i in x.get("ids") or [])]
    d["actor"] = {"id": c["id"], "nombre": c["nombre"], "rol": _rol_actor(c, L),
                  "letras": {k: sorted(el for el, r in raci.items() if r == k) for k in LETRAS_RACI}}
    return d


# ---------------------------------------------------------------- API pública del filtro por actor (pm-kb y otros)
class ActorInvalido(ValueError):
    """Actor vacío, inexistente o ambiguo; el mensaje es el mismo que `generar --actor` imprime antes de salir con código 1."""


def _estado_e_idioma(proyecto):
    e = E.cargar_estado(proyecto)
    return e, (e.get("idioma") if e.get("idioma") in ("es", "en") else "es")


def actores(proyecto):
    """API pública. Personas que pueden ser actor del tablero, como las resuelve `--actor`: las de stakeholders.csv y las
    de estado.json.roles, unidas por nombre. Devuelve [{id (ST-### o ""), nombre, rol (texto para mostrar, en el idioma
    del proyecto), roles (claves de estado.json.roles que ocupa)}]. Solo lectura: sin bloqueo ni escrituras."""
    with E.modo_solo_lectura():
        e, L = _estado_e_idioma(proyecto)
        return [{"id": c["id"], "nombre": c["nombre"], "rol": _rol_actor(c, L), "roles": list(c["roles"])} for c in _actores(proyecto, e, L)]


def filtrar_actor(datos, proyecto, actor):
    """API pública. Copia del tablero `datos` (dict pm-tablero/1: el actual o una instantánea congelada) con solo lo de
    `actor` (nombre, "<rol: nombre>", rol o ST-###), con las mismas reglas que `generar --actor` y la RACI y los registros
    vigentes de `proyecto`; los totales se recalculan y se agrega el bloque `actor`. `datos` no se modifica. Actor vacío,
    inexistente o ambiguo → ActorInvalido (ValueError). Solo lectura: sin bloqueo ni escrituras."""
    import copy
    with E.modo_solo_lectura():
        e, L = _estado_e_idioma(proyecto)
        try:
            c = resolver_actor(proyecto, e, actor, L)
        except SystemExit as x:
            raise ActorInvalido(str(x.code if x.code is not None else actor)) from None
        try:
            import estado as ES
            prods = ES.productos(proyecto, e)
        except (Exception, SystemExit):     # sin productos legibles: los paquetes que trae el propio tablero
            prods = {"productos": [{"id": t.get("ref"), "paquetes": t.get("paquetes") or []}
                                   for t in (((datos.get("entrega") or {}).get("productos") or {}).get("tarjetas") or [])]}
        return _filtrar_actor(copy.deepcopy(datos), proyecto, e, c, prods, L)


def construir(proyecto, corte=None, instantanea=None, actor=None):
    """Tablero del proyecto (dict pm-tablero/1). Solo lectura: no toma el bloqueo ni escribe (PM_SOLO_LECTURA=1 durante el
    cálculo, también para sanidad.py --rapido que corre la verificación de la próxima puerta). Un bloque que falla queda
    en `avisos`; un dato ilegible termina con su mensaje (E.DatosIlegibles). `actor` (nombre, rol o ST-###): el tablero
    filtrado por la RACI y las responsabilidades de esa persona (_filtrar_actor); inexistente o ambiguo → código 1."""
    with E.modo_solo_lectura():
        e = E.cargar_estado(proyecto)
        L = e.get("idioma") if e.get("idioma") in ("es", "en") else "es"
        quien = resolver_actor(proyecto, e, actor, L) if actor is not None else None
        corte = corte or _hoy(); avisos = []
        import estado as ES, puertas as PU, registro as RG
        RG.IDIOMA = L
        def paso(nombre, fn, defecto):
            try: return fn()
            except E.DatosIlegibles: raise
            except (Exception, SystemExit) as x:
                avisos.append(f"{nombre}: {_corto(x, 200)}"); return defecto
        with _memo_puertas(PU):
            radar = paso("estado.py radar", lambda: ES.datos_radar(proyecto, e, corte, 0), {})
            pu = paso("puertas.py estado", lambda: PU.estado_puertas(proyecto, e), {})
        prods = paso("estado.py productos", lambda: ES.productos(proyecto, e), {})
        props = paso("registro.py propuestas", lambda: RG.listar_propuestas(proyecto, "pendiente"), [])
        radar_items = [i for g in GRUPOS_ATENCION for i in (radar.get("items") or {}).get(g, [])]
        ciclo = _ciclo(e, pu, radar_items, L, avisos)
        atencion, en_atencion = _atencion(radar, ciclo, corte, L)
        prox = ((pu or {}).get("proxima") or {}).get("puerta", "")
        control = paso("registros de control", lambda: _control(proyecto, corte, props, en_atencion, L), {})
        artefactos = paso("artefactos", lambda: _artefactos(proyecto, e, prox, L, avisos), {"grupos": [], "elementos": {}})
        eventos, n_bit = _eventos(proyecto)
        d = {"formato": FORMATO, "proyecto": e.get("proyecto", ""), "idioma": L, "corte": corte,
             "generado": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "huella": huella(proyecto), "n_bitacora": n_bit,
             "instantanea": instantanea, "actor": None, "ciclo": ciclo, "atencion": atencion,
             "entrega": {"productos": _productos(prods, L), "control": control}, "artefactos": artefactos,
             "eventos": eventos, "avisos": avisos}
        return _filtrar_actor(d, proyecto, e, quien, prods, L) if quien else d


# ---------------------------------------------------------------- HTML autocontenido (CSP propia por hash)
ESTILO = """
:root{--fondo:#f6f7f9;--panel:#fff;--texto:#1d2330;--suave:#5b6474;--borde:#d9dde4;--acento:#2f5fb3;--bien:#1f7a44;--mal:#b3261e;--alerta:#9a6200;--sombra:#eef1f6}
@media (prefers-color-scheme:dark){:root{--fondo:#14171c;--panel:#1d2128;--texto:#e6e9ef;--suave:#a3abb8;--borde:#343a45;--acento:#8fb3ff;--bien:#6fcf97;--mal:#ff8a80;--alerta:#f2c94c;--sombra:#262b34}}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--texto);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header,main,footer{padding:12px 16px}
h1{font-size:1.25rem;margin:0 0 4px}h2{font-size:1.05rem;margin:18px 0 8px}h3{font-size:.95rem;margin:0 0 6px}
.leyenda{display:inline-block;margin-top:4px;padding:2px 8px;border:1px solid var(--alerta);border-radius:12px;color:var(--alerta);font-size:.82rem}
.congelada{margin-top:6px;font-size:.88rem;color:var(--suave)}
.pulso{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.dato{background:var(--panel);border:1px solid var(--borde);border-radius:8px;padding:6px 10px;min-width:140px;flex:1 1 140px}
.etq{display:block;font-size:.75rem;color:var(--suave);text-transform:uppercase;letter-spacing:.03em}
.vistas{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.vistas button{font:inherit;padding:6px 12px;border:1px solid var(--borde);border-radius:6px;background:var(--panel);color:var(--texto);cursor:pointer}
.vistas button[aria-pressed=true]{border-color:var(--acento);color:var(--acento);font-weight:600}
.desliza{overflow-x:auto;padding-bottom:6px}
.fila{display:flex;gap:10px;align-items:flex-start;min-width:min-content}
.col{background:var(--sombra);border:1px solid var(--borde);border-radius:8px;padding:8px;min-width:230px;max-width:300px;flex:0 0 250px}
.col>header{display:flex;justify-content:space-between;padding:0 0 6px;font-weight:600;font-size:.88rem}
.cuenta{color:var(--suave)}
.tarjeta{display:block;background:var(--panel);border:1px solid var(--borde);border-radius:6px;padding:7px 9px;margin:0 0 7px;color:inherit;text-decoration:none}
a.tarjeta:hover,a.tarjeta:focus{border-color:var(--acento);outline:none}
.tarjeta .nombre{font-weight:600;font-size:.9rem}
.tarjeta .desc{font-size:.82rem;color:var(--suave);margin-top:2px}
.ref{font:600 .75rem ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--acento)}
.chip{display:inline-block;font-size:.72rem;border:1px solid var(--borde);border-radius:10px;padding:0 6px;margin:2px 4px 0 0;color:var(--suave)}
.chip.mal{border-color:var(--mal);color:var(--mal)}.chip.bien{border-color:var(--bien);color:var(--bien)}.chip.alerta{border-color:var(--alerta);color:var(--alerta)}
.sombra{border-style:dashed;opacity:.85}
.etapa.actual{border-color:var(--acento);border-width:2px}.etapa.futura{opacity:.7}
.puerta{min-width:200px;flex:0 0 220px;background:var(--panel)}
.puerta.proxima{border-style:dashed;border-color:var(--alerta)}
.hallazgos{margin:6px 0 0;padding-left:16px;font-size:.8rem}
.vacia{color:var(--suave);font-size:.85rem;margin:0}
.nota{font-size:.82rem;color:var(--suave)}
.mal{color:var(--mal)}.bien{color:var(--bien)}
details{margin-top:14px}summary{cursor:pointer;color:var(--suave)}
ol.eventos{font-size:.82rem;padding-left:20px}
@media (max-width:600px){.col{flex-basis:78vw;min-width:78vw}.dato{flex-basis:100%}}
"""

GUION = r"""
"use strict";
(function () {
  var D = JSON.parse(document.getElementById("datos-tablero").textContent);
  var V = JSON.parse(document.getElementById("vinculos-tablero").textContent);
  var EN = D.idioma === "en";
  function t(es, en) { return EN ? en : es; }
  function el(tag, cls, texto) { var e = document.createElement(tag); if (cls) e.className = cls; if (texto !== undefined && texto !== null) e.textContent = String(texto); return e; }
  function add(p) { for (var i = 1; i < arguments.length; i++) { var h = arguments[i]; if (h === null || h === undefined || h === false) continue; if (Array.isArray(h)) h.forEach(function (x) { if (x) p.appendChild(x); }); else p.appendChild(h); } return p; }
  var GRUPOS = [["decidir", t("Decidir", "Decide")], ["escalar", t("Escalar", "Escalate")], ["desbloquear", t("Desbloquear", "Unblock")], ["vigilar", t("Vigilar", "Watch")]];
  var REG = { cambios: t("Cambios", "Changes"), issues: "Issues", acciones: t("Acciones", "Actions") };
  var SENAL = { vencida: [t("vencida", "overdue"), "mal"], bloqueada: [t("bloqueada", "blocked"), "mal"], "propuesta-pendiente": [t("propuesta pendiente", "pending proposal"), "alerta"],
    "fuente-no-encontrada": [t("fuente no encontrada", "source not found"), "mal"], "aprobada-anterior": [t("hay una versión aprobada anterior", "previous approved version"), "alerta"],
    forzada: [t("forzada", "forced"), "mal"], "condiciones-abiertas": [t("condiciones abiertas", "open conditions"), "alerta"], discrepancias: [t("discrepancias", "discrepancies"), "alerta"] };
  function href(c) {
    if (V.origen) return V.origen + "/p/" + encodeURIComponent(D.proyecto) + "/ficha/" + encodeURIComponent(c.ref);
    if (c.fuente) return (V.base ? V.base + "/" : "") + c.fuente.split("/").map(encodeURIComponent).join("/");
    return null;
  }
  function tarjeta(c, extra) {
    var h = href(c), a = el(h ? "a" : "div", "tarjeta" + (c.tipo === "propuesta" ? " sombra" : ""));
    if (h) { a.setAttribute("href", h); a.setAttribute("rel", "noopener noreferrer"); }
    add(a, el("div", "ref", c.ref), el("div", "nombre", c.nombre), c.descripcion ? el("div", "desc", c.descripcion) : null);
    var chips = el("div");
    (c.senales || []).forEach(function (s) { var x = SENAL[s] || [s, ""]; chips.appendChild(el("span", "chip " + x[1], x[0])); });
    if (extra) extra.forEach(function (x) { chips.appendChild(el("span", "chip", x)); });
    if (c.raci) chips.appendChild(el("span", "chip bien", "RACI " + c.raci));
    if (chips.childNodes.length) a.appendChild(chips);
    return a;
  }
  function columna(titulo, cartas, cls) {
    var s = el("section", "col " + (cls || "")); s.setAttribute("aria-label", titulo + ": " + cartas.length);
    var cab = el("header"); add(cab, el("span", "", titulo), el("span", "cuenta", cartas.length)); s.appendChild(cab);
    if (cartas.length) add(s, cartas); else s.appendChild(el("p", "vacia", "—"));
    return s;
  }
  function fila(cols) { var d = el("div", "desliza"), f = el("div", "fila"); add(f, cols); d.appendChild(f); return d; }

  function pulso() {
    var c = D.ciclo, prox = c.columnas.filter(function (x) { return x.puerta && x.estado === "proxima"; })[0];
    var bl = prox ? prox.hallazgos.filter(function (h) { return h.severidad === "bloqueo"; }).length : 0;
    var p = el("div", "pulso");
    function dato(etq, valor, sub, cls) { var d = el("div", "dato"); add(d, el("span", "etq", etq), el("strong", "", valor), sub ? el("div", "nota " + (cls || ""), sub) : null); p.appendChild(d); }
    dato(t("Fase · proceso", "Phase · process"), c.fase + " · " + c.proceso);
    dato(t("Etapa", "Stage"), String(c.etapa) + (c.nombre_etapa && c.nombre_etapa !== t("Etapa ", "Stage ") + c.etapa ? " · " + c.nombre_etapa : ""), c.fin_previsto ? t("fin previsto ", "planned end ") + c.fin_previsto : "");
    dato(t("Próxima puerta", "Next gate"), prox ? prox.tipo : "—", prox ? (bl ? t(bl + " bloqueo(s)", bl + " blocker(s)") : t("sin bloqueos", "no blockers")) : "", bl ? "mal" : "bien");
    dato(t("Atención", "Attention"), GRUPOS.map(function (g) { return g[1] + " " + (D.atencion.totales[g[0]] || 0); }).join(" · "));
    if (c.excepcion) dato(t("Excepción abierta", "Open exception"), c.excepcion, "", "mal");
    return p;
  }
  function vistaCiclo() {
    var cols = D.ciclo.columnas.map(function (col) {
      if (col.puerta && col.estado === "proxima") {
        var s = el("section", "col puerta proxima"); s.appendChild(el("header", "", t("◇ Próxima puerta", "◇ Next gate")));
        s.appendChild(tarjeta(col.tarjeta));
        if (col.hallazgos.length) { var ul = el("ul", "hallazgos"); col.hallazgos.forEach(function (h) { ul.appendChild(el("li", h.severidad === "bloqueo" ? "mal" : "", h.id + " · " + h.mensaje)); }); s.appendChild(ul); }
        else s.appendChild(el("p", "bien", t("lista para presentar", "ready to submit")));
        return s;
      }
      if (col.puerta) return columna(t("◆ Puerta", "◆ Gate"), col.decisiones.map(function (d) { return tarjeta(d); }), "puerta");
      var marca = { hecha: t("✓ hecha", "✓ done"), actual: t("● en curso", "● in progress"), futura: t("○ por venir", "○ upcoming") }[col.estado];
      var s2 = el("section", "col etapa " + col.estado); add(s2, el("div", "nota", marca), el("h3", "", col.nombre));
      if (col.estado === "actual") {
        if (col.proceso) s2.appendChild(el("div", "nota", t("proceso ", "process ") + col.proceso + (col.inicio ? " · " + col.inicio + " → " + (col.fin_previsto || "…") : "")));
        if (col.excepcion) s2.appendChild(el("div", "mal", t("excepción abierta: ", "open exception: ") + col.excepcion));
        (col.senales || []).forEach(function (x) { s2.appendChild(el("div", "nota", x.regla + " · " + x.que)); });
      }
      (col.eventos || []).forEach(function (ev) { s2.appendChild(tarjeta(ev)); });
      return s2;
    });
    return fila(cols);
  }
  function vistaAtencion() {
    var it = D.atencion.items;
    return fila(GRUPOS.map(function (g) {
      return columna(g[1], it.filter(function (i) { return i.grupo === g[0]; }).map(function (i) { return tarjeta(i, ["P" + i.prioridad, i.regla]); }));
    }));
  }
  function vistaEntrega() {
    var P = D.entrega.productos, cont = el("div");
    cont.appendChild(el("h2", "", t("Productos", "Products")));
    var exc = P.tarjetas.some(function (x) { return P.excepcion.indexOf(x.estado) >= 0; });
    var est = P.columnas.concat(exc ? P.excepcion : []);
    cont.appendChild(fila(est.map(function (s) { return columna(s, P.tarjetas.filter(function (x) { return x.estado === s; }).map(function (x) { return tarjeta(x); })); })));
    cont.appendChild(el("h2", "", t("Control", "Control")));
    cont.appendChild(el("p", "nota", t("Las propuestas pendientes (punteadas) todavía no cambiaron el registro: las aprueba una persona.", "Pending proposals (dashed) have not changed the register yet: a person approves them.")));
    ["cambios", "issues", "acciones"].forEach(function (r) {
      var v = D.entrega.control[r]; if (!v) return;
      var cerr = Object.keys(v.cerrados).map(function (k) { return v.cerrados[k] + " " + k; }).join(" · ");
      cont.appendChild(el("h3", "", REG[r] + (cerr ? " · " + t("cerrados: ", "closed: ") + cerr : "")));
      cont.appendChild(fila(v.columnas.map(function (s) {
        return columna(s, v.tarjetas.filter(function (x) { return x.columna === s; }).map(function (x) { return tarjeta(x); })
          .concat(v.propuestas.filter(function (x) { return x.columna === s; }).map(function (x) { return tarjeta(x); })));
      })));
    });
    return cont;
  }
  function vistaArtefactos() {
    var A = D.artefactos, cont = el("div");
    A.grupos.forEach(function (g) {
      cont.appendChild(el("h2", "", g.nombre));
      var cartas = g.claves.map(function (k) { return tarjeta(A.elementos[k]); });
      cont.appendChild(cartas.length ? fila([columna(t("Tarjetas", "Cards"), cartas)]) : el("p", "vacia", "—"));
    });
    return cont;
  }
  var VISTAS = [["ciclo", t("Ciclo y puertas", "Cycle and gates"), vistaCiclo], ["atencion", t("Atención", "Attention"), vistaAtencion],
    ["entrega", t("Entrega", "Delivery"), vistaEntrega], ["artefactos", t("Artefactos", "Artifacts"), vistaArtefactos]];
  var actual = "ciclo";
  function pintar() {
    var m = document.getElementById("vista"); m.textContent = "";
    VISTAS.forEach(function (v) { if (v[0] === actual) m.appendChild(v[2]()); });
    Array.prototype.forEach.call(document.querySelectorAll(".vistas button"), function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-vista") === actual)); });
  }
  var cab = document.getElementById("cabecera");
  add(cab, el("h1", "", t("Tablero · ", "Board · ") + D.proyecto),
    el("span", "leyenda", t("Instantánea al " + D.corte + ": no se actualiza", "Snapshot as of " + D.corte + ": it does not update")));
  if (D.actor) {
    var A = D.actor, LT = ["R", "A", "C", "I"].map(function (k) { return k + " " + ((A.letras || {})[k] || []).length; }).join(" · ");
    cab.appendChild(el("div", "congelada", t("Vista de ", "View for ") + A.nombre + (A.rol ? " (" + A.rol + ")" : "") + " · RACI " + LT
      + t(" · solo lo suyo; el ciclo y las puertas son comunes", " · only their items; the cycle and gates are shared")));
  }
  if (D.instantanea) {
    var I = D.instantanea;
    cab.appendChild(el("div", "congelada", t("Congelada: ", "Frozen: ") + I.etiqueta + (I.decision ? " · " + t("decisión ", "decision ") + I.decision : "") + (I.decision_id ? " (" + I.decision_id + ")" : "") + (I.por ? " · " + I.por : "")));
  }
  cab.appendChild(pulso());
  var bar = el("nav", "vistas"); bar.setAttribute("aria-label", t("Vista", "View"));
  VISTAS.forEach(function (v) { var b = el("button", "", v[1]); b.type = "button"; b.setAttribute("data-vista", v[0]); b.addEventListener("click", function () { actual = v[0]; pintar(); }); bar.appendChild(b); });
  cab.appendChild(bar);
  var pie = document.getElementById("pie");
  if (D.eventos.length) {
    var det = el("details"); det.appendChild(el("summary", "", t("Últimos eventos de la bitácora (" + D.n_bitacora + ")", "Latest write-log events (" + D.n_bitacora + ")")));
    var ol = el("ol", "eventos"); D.eventos.forEach(function (e) { ol.appendChild(el("li", "", "#" + e.n + " " + e.fecha + " · " + e.operacion + " " + (e.registro || e.archivo) + " " + e.ids.join(", ") + (e.por ? " · " + e.por : ""))); });
    det.appendChild(ol); pie.appendChild(det);
  }
  (D.avisos || []).forEach(function (a) { pie.appendChild(el("p", "nota mal", t("aviso: ", "warning: ") + a)); });
  pie.appendChild(el("p", "nota", t("Solo lectura, derivado de estado.json, los registros y la bitácora (" + D.formato + ", huella " + D.huella + ", generado " + D.generado + "). Los cambios se hacen con pm-method.",
    "Read-only, derived from estado.json, the registers and the write log (" + D.formato + ", fingerprint " + D.huella + ", generated " + D.generado + "). Changes are made with pm-method.")));
  pintar();
})();
"""


def _hash(texto): return base64.b64encode(hashlib.sha256(texto.encode("utf-8")).digest()).decode()


def html(d, base="", origen=""):
    """HTML de un solo archivo: CSS y JS en línea autorizados por su hash sha256 (CSP propia), datos en un bloque JSON
    escapado (todo '<' como \\u003c). `base`: ruta relativa del HTML a la carpeta del proyecto (enlaces a la fuente);
    `origen`: URL del portal (enlaces a <origen>/p/<proyecto>/ficha/<ref>)."""
    L = d.get("idioma", "es")
    datos = json.dumps(d, ensure_ascii=False).replace("<", "\\u003c")
    vinculos = json.dumps({"origen": origen or "", "base": base or ""}, ensure_ascii=False).replace("<", "\\u003c")
    csp = (f"default-src 'none'; script-src 'sha256-{_hash(GUION)}'; style-src 'sha256-{_hash(ESTILO)}'; img-src data:; "
           "base-uri 'none'; form-action 'none'")
    titulo = (_t(L, "Tablero · ", "Board · ") + str(d.get("proyecto") or "") + (" · " + str(d["actor"].get("nombre") or "") if d.get("actor") else "")
              + " · " + str(d.get("corte") or "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (f'<!doctype html>\n<html lang="{L}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n<meta name="referrer" content="no-referrer">\n'
            f'<meta name="generator" content="pm-method {FORMATO}">\n<title>{titulo}</title>\n<style>{ESTILO}</style>\n</head>\n<body>\n'
            f'<header id="cabecera"></header>\n<main id="vista"></main>\n<footer id="pie"></footer>\n'
            f'<noscript><p>{_t(L, "Este tablero necesita JavaScript para dibujarse; los datos están en el bloque datos-tablero (pm-tablero/1).", "This board needs JavaScript to render; the data are in the datos-tablero block (pm-tablero/1).")}</p></noscript>\n'
            f'<script type="application/json" id="datos-tablero">{datos}</script>\n'
            f'<script type="application/json" id="vinculos-tablero">{vinculos}</script>\n'
            f'<script>{GUION}</script>\n</body>\n</html>\n')


def _origen_valido(x, L):
    if not x: return ""
    u = urllib.parse.urlsplit(x.strip())
    if u.scheme not in ("http", "https") or not u.netloc or u.query or u.fragment or u.username or u.password:
        sys.exit(_t(L, f"--origen debe ser una URL http o https sin parámetros ni credenciales (p. ej. https://portal.ejemplo:8080): {x}",
                    f"--origen must be an http or https URL without query or credentials (e.g. https://portal.example:8080): {x}"))
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path.rstrip("/"), "", ""))


# ---------------------------------------------------------------- instantáneas congeladas
def _dir(proyecto): return os.path.join(proyecto, E.DIR_TABLEROS)


def slug(texto):
    s = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60].rstrip("-") or "tablero"


def congelar(proyecto, etiqueta, por="", datos=None, fecha=None, tipo="manual", puerta="", etapa=None, decision="", decision_id="", motivo="", actor=None):
    """Escribe la instantánea <fecha>-<slug(etiqueta)>.json y .html en 03-control/reportes/tableros/ con el mecanismo
    común (bloqueo, escritura atómica, bitácora con huella). Nunca pisa: si el id existe, -2, -3… `datos`: tablero ya
    calculado (estado.py lo calcula antes de aplicar la decisión); `actor`: congela el tablero filtrado de esa persona.
    Devuelve (id, ruta relativa del JSON, del HTML)."""
    with E.bloqueo(proyecto):
        d = datos if datos is not None else construir(proyecto, actor=actor)
        L = d.get("idioma", "es"); fecha = fecha or d.get("corte") or _hoy()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(fecha)): fecha = _hoy()
        base_id = f"{fecha}-{slug(etiqueta)}"; iid, k = base_id, 2
        carpeta = _dir(proyecto); os.makedirs(carpeta, exist_ok=True)
        while any(os.path.exists(os.path.join(carpeta, iid + x)) for x in (".json", ".html")):
            iid = f"{base_id}-{k}"; k += 1
        d = dict(d)
        d["instantanea"] = {"id": iid, "tipo": tipo, "etiqueta": _corto(etiqueta, 120), "fecha": fecha, "puerta": puerta or "",
                            "etapa": etapa if etapa is not None else (d.get("ciclo") or {}).get("etapa"), "decision": decision or "",
                            "decision_id": decision_id or "", "motivo": _limpio(motivo, 200, L) if motivo else "", "por": _corto(por, 80)}
        rj, rh = os.path.join(carpeta, iid + ".json"), os.path.join(carpeta, iid + ".html")
        E.escribir_atomico(rj, json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        E.escribir_atomico(rh, html(d, base=os.path.relpath(proyecto, carpeta).replace(os.sep, "/")))
    rel = lambda r: os.path.relpath(r, proyecto).replace(os.sep, "/")
    return iid, rel(rj), rel(rh)


def listar(proyecto):
    """Instantáneas congeladas, de la más antigua a la más nueva, con su sha256 y si coincide con la última escritura
    anotada en la bitácora (`en_bitacora`: true, false = modificada fuera de los scripts, null = sin línea)."""
    carpeta = _dir(proyecto); ultimas, orden = {}, {}
    for raw in E.leer_bitacora(proyecto):
        x = E._json_o_none(raw)
        if x and (x.get("archivo") or "").startswith("03-control/reportes/tableros/"):
            ultimas[x["archivo"]] = x.get("despues", ""); orden.setdefault(x["archivo"], x.get("n") or 0)
    out = []
    for f in sorted(os.listdir(carpeta)) if os.path.isdir(carpeta) else []:
        if not f.endswith(".json"): continue
        rel = f"03-control/reportes/tableros/{f}"; b = E._leer_bytes(os.path.join(carpeta, f)) or b""
        try: d = json.loads(b.decode("utf-8"))
        except ValueError: d = {}
        ins = (d.get("instantanea") if isinstance(d, dict) else None) or {}
        sha = E._sha(b)
        out.append({"id": f[:-5], "fecha": ins.get("fecha", ""), "tipo": ins.get("tipo", ""), "etiqueta": ins.get("etiqueta", ""),
                    "puerta": ins.get("puerta", ""), "etapa": ins.get("etapa"), "decision": ins.get("decision", ""), "decision_id": ins.get("decision_id", ""),
                    "por": ins.get("por", ""), "actor": ((d.get("actor") if isinstance(d, dict) else None) or {}).get("nombre", ""),
                    "corte": d.get("corte", "") if isinstance(d, dict) else "", "formato": d.get("formato", "") if isinstance(d, dict) else "",
                    "archivo": rel, "html": os.path.exists(os.path.join(carpeta, f[:-5] + ".html")), "sha256": sha,
                    "en_bitacora": (ultimas[rel] == sha) if rel in ultimas else None, "_n": orden.get(rel, 10 ** 9)})
    out.sort(key=lambda x: (x["fecha"] or x["id"][:10], x.pop("_n")))     # mismo día: en el orden en que se escribieron
    return out


def cargar_instantanea(proyecto, iid, L):
    if not ID_INSTANTANEA.match(iid or ""):
        sys.exit(_t(L, f"Id de instantánea inválido: {iid} (AAAA-MM-DD-<etiqueta>; ver tablero.py listar).", f"Invalid snapshot id: {iid} (see tablero.py listar)."))
    p = os.path.join(_dir(proyecto), iid + ".json")
    if not os.path.isfile(p): sys.exit(_t(L, f"No existe la instantánea {iid} (tablero.py listar).", f"Snapshot {iid} not found (tablero.py listar)."))
    d = E.leer_json(p, dict, L)
    if d.get("formato") != FORMATO: sys.exit(_t(L, f"{iid} no tiene el formato {FORMATO}.", f"{iid} is not in {FORMATO} format."))
    return d


def tarjetas(d):
    """{(vista, clave): (ref, nombre, columna, estado)} de todas las tarjetas de un tablero (para comparar)."""
    out = {}
    def poner(vista, c, clave=None):
        if c: out[(vista, clave or c["ref"])] = (c["ref"], c.get("nombre", ""), c.get("columna", ""), c.get("estado", ""))
    for col in (d.get("ciclo") or {}).get("columnas", []):
        for c in (col.get("decisiones") or []) + (col.get("eventos") or []) + ([col.get("tarjeta")] if col.get("tarjeta") else []): poner("ciclo", c)
    for c in (d.get("atencion") or {}).get("items", []): poner("atencion", c, f"{c['ref']}|{c.get('regla', '')}")
    ent = d.get("entrega") or {}
    for c in (ent.get("productos") or {}).get("tarjetas", []): poner("productos", c)
    for reg, v in (ent.get("control") or {}).items():
        for c in (v.get("tarjetas") or []) + (v.get("propuestas") or []): poner(reg, c)
    for c in ((d.get("artefactos") or {}).get("elementos") or {}).values(): poner("artefactos", c)
    return out


def comparar(a, b):
    ta, tb = tarjetas(a), tarjetas(b)
    fila = lambda k, v: {"vista": k[0], "ref": v[0], "nombre": v[1], "columna": v[2], "estado": v[3]}
    cambiaron = [{"vista": k[0], "ref": tb[k][0], "nombre": tb[k][1], "de": {"columna": ta[k][2], "estado": ta[k][3]}, "a": {"columna": tb[k][2], "estado": tb[k][3]}}
                 for k in tb if k in ta and (ta[k][2], ta[k][3]) != (tb[k][2], tb[k][3])]
    return {"a": (a.get("instantanea") or {}).get("id") or "actual", "b": (b.get("instantanea") or {}).get("id") or "actual",
            "corte_a": a.get("corte", ""), "corte_b": b.get("corte", ""),
            "entraron": [fila(k, v) for k, v in tb.items() if k not in ta], "salieron": [fila(k, v) for k, v in ta.items() if k not in tb],
            "cambiaron": cambiaron}


# ---------------------------------------------------------------- salida de texto
def resumen(d):
    L = d["idioma"]; c = d["ciclo"]; at = d["atencion"]["totales"]
    prox = next((x for x in c["columnas"] if x.get("puerta") and x.get("estado") == "proxima"), None)
    bl = sum(1 for h in (prox or {}).get("hallazgos", []) if h["severidad"] == "bloqueo")
    ctl = d["entrega"]["control"]; arts = d["artefactos"]["elementos"]
    sin_fuente = [k for k, v in arts.items() if v["tipo"] == "artefacto" and not v["existe"]]
    out = [_t(L, f"Tablero de {d['proyecto']} al {d['corte']} ({FORMATO}, huella {d['huella']})", f"Board of {d['proyecto']} as of {d['corte']} ({FORMATO}, fingerprint {d['huella']})"),
           *([_t(L, "Actor: ", "Actor: ") + d["actor"]["nombre"] + (f" ({d['actor']['rol']})" if d["actor"]["rol"] else "") + " · RACI "
              + " · ".join(f"{k} {len(d['actor']['letras'][k])}" for k in LETRAS_RACI)
              + _t(L, " · solo lo suyo (el ciclo y las puertas son comunes)", " · only their items (the cycle and gates are shared)")] if d.get("actor") else []),
           _t(L, f"Fase {c['fase']} · proceso {c['proceso']} · etapa {c['etapa']}", f"Phase {c['fase']} · process {c['proceso']} · stage {c['etapa']}")
           + (_t(L, f" · próxima puerta {prox['tipo']} ({bl} bloqueo(s))", f" · next gate {prox['tipo']} ({bl} blocker(s))") if prox else ""),
           _t(L, "Atención: ", "Attention: ") + " · ".join(f"{g} {at.get(g, 0)}" for g in GRUPOS_ATENCION),
           _t(L, "Entrega: ", "Delivery: ") + f"{len(d['entrega']['productos']['tarjetas'])} " + _t(L, "productos", "products") + " · "
           + " · ".join(f"{r} {len(v['tarjetas'])}" + (_t(L, f" (+{len(v['propuestas'])} propuesta(s))", f" (+{len(v['propuestas'])} proposal(s))") if v["propuestas"] else "") for r, v in ctl.items()),
           _t(L, f"Artefactos clave: {len(arts)}", f"Key artifacts: {len(arts)}") + (_t(L, f" · fuente no encontrada: {', '.join(sin_fuente)}", f" · source not found: {', '.join(sin_fuente)}") if sin_fuente else "")]
    out += [_t(L, "Aviso: ", "Warning: ") + a for a in d["avisos"]]
    out.append(_t(L, "→ --json para el formato pm-tablero/1; --html RUTA para el HTML autocontenido.", "→ --json for the pm-tablero/1 format; --html RUTA for the self-contained HTML."))
    return "\n".join(out)


def _destino_html(proyecto, ruta, e, L):
    ra = os.path.abspath(ruta); partes = ra.split(os.sep)
    prot = os.sep + os.path.join("03-control", "registros") + os.sep in ra or os.sep + E.DIR_TABLEROS + os.sep in ra
    if prot or any(x in partes for x in ("_bmad", "_bmad-output", ".bmad-core")):
        sys.exit(_t(L, "El HTML no se escribe en 03-control/reportes/tableros/ (instantáneas: tablero.py congelar), 03-control/registros/ ni carpetas de BMAD.",
                    "The HTML is not written into 03-control/reportes/tableros/ (snapshots: tablero.py congelar), 03-control/registros/ or BMAD folders."))
    rel = os.path.relpath(ra, os.path.abspath(proyecto))
    aprobado = [k for k, v in (e.get("artefactos") or {}).items() if v.get("estado") == "aprobado" and os.path.normpath(v.get("ruta", "")) == os.path.normpath(rel)]
    if aprobado: sys.exit(_t(L, f"{rel} es la versión aprobada de {aprobado[0]}: no se reescribe.", f"{rel} is the approved version of {aprobado[0]}: not rewritten."))
    return ra


def main(argv=None):
    E.salida_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", help="carpeta del proyecto (la que tiene estado.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    def con_proyecto(p): p.add_argument("--proyecto", default=argparse.SUPPRESS, help="carpeta del proyecto (también antes del subcomando)"); return p
    g = con_proyecto(sub.add_parser("generar", help="tablero actual: resumen, JSON pm-tablero/1 (--json) o HTML (--html RUTA); solo lectura salvo --html"))
    g.add_argument("--corte", help="fecha de corte AAAA-MM-DD para vencidas y edades (defecto: hoy)")
    g.add_argument("--json", action="store_true", help="imprime el tablero en formato pm-tablero/1")
    g.add_argument("--html", metavar="RUTA", help="escribe el HTML autocontenido (CSP por hash) en RUTA")
    g.add_argument("--origen", metavar="URL", help="URL del portal (http/https): las tarjetas del HTML enlazan a <URL>/p/<proyecto>/ficha/<ref>")
    g.add_argument("--actor", metavar="ACTOR", help="solo lo de esa persona según raci.csv y sus responsabilidades: nombre, \"<rol: nombre>\", rol o ST-###")
    c = con_proyecto(sub.add_parser("congelar", help="congela el tablero actual en 03-control/reportes/tableros/<fecha>-<etiqueta>.json y .html (inmutable, bitácora)"))
    c.add_argument("--etiqueta", required=True, help="motivo de la instantánea, p. ej. \"highlight de noviembre\" o \"junta del 2026-11-20\"")
    c.add_argument("--por", default="", help="quién la pide (\"<rol: nombre>\"); queda en la instantánea y en la bitácora")
    c.add_argument("--actor", metavar="ACTOR", help="congela el tablero filtrado de esa persona (como generar --actor)")
    li = con_proyecto(sub.add_parser("listar", help="instantáneas congeladas con su etiqueta, puerta, etapa, decisión y sha256"))
    li.add_argument("--json", action="store_true")
    co = con_proyecto(sub.add_parser("comparar", help="tarjetas que entraron, salieron o cambiaron de columna o estado entre dos instantáneas"))
    co.add_argument("a", help="id de la instantánea anterior (tablero.py listar)"); co.add_argument("b", help="id de la posterior, o «actual» (el tablero de hoy)")
    co.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not a.proyecto: ap.error("falta --proyecto / --proyecto is required")
    if not os.path.isfile(os.path.join(a.proyecto, "estado.json")):
        sys.exit(f"{a.proyecto} no es una carpeta de proyecto (falta estado.json) / not a project folder (estado.json missing).")
    L = E.idioma_de(a.proyecto); L = L if L in ("es", "en") else "es"
    if a.cmd == "generar":
        corte = _fecha_valida(a.corte, L); origen = _origen_valido(a.origen, L)
        if a.origen and not a.html: sys.exit(_t(L, "--origen solo se usa con --html RUTA.", "--origen is only used with --html RUTA."))
        d = construir(a.proyecto, corte, actor=a.actor)
        if a.html:
            ruta = _destino_html(a.proyecto, a.html, E.cargar_estado(a.proyecto), L)
            os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
            base = os.path.relpath(os.path.abspath(a.proyecto), os.path.dirname(ruta)).replace(os.sep, "/")
            with open(ruta, "w", encoding="utf-8") as fh: fh.write(html(d, base=base, origen=origen))
            print(_t(L, f"Tablero HTML: {a.html} (corte {d['corte']}, instantánea que no se actualiza; CSP por hash)", f"HTML board: {a.html} (cut-off {d['corte']}, static snapshot; hash-based CSP)"),
                  file=sys.stderr if a.json else sys.stdout)
        if a.json: print(json.dumps(d, ensure_ascii=False, indent=1))
        elif not a.html: print(resumen(d))
        return
    if a.cmd == "congelar":
        if not a.etiqueta.strip(): sys.exit(_t(L, "--etiqueta no puede estar vacía.", "--etiqueta cannot be empty."))
        iid, rj, rh = congelar(a.proyecto, a.etiqueta.strip(), por=a.por, actor=a.actor)
        print(_t(L, f"Instantánea {iid}: {rj} y {rh} (inmutable; anotada en la bitácora)", f"Snapshot {iid}: {rj} and {rh} (immutable; recorded in the write log)"))
        return
    if a.cmd == "listar":
        xs = listar(a.proyecto)
        if a.json: print(json.dumps(xs, ensure_ascii=False, indent=1)); return
        if not xs: print(_t(L, "Sin instantáneas en 03-control/reportes/tableros/ (se congelan en cada puerta o con tablero.py congelar).",
                            "No snapshots in 03-control/reportes/tableros/ (frozen at each gate or with tablero.py congelar).")); return
        for x in xs:
            marca = {True: "", False: _t(L, " · MODIFICADA fuera de los scripts (BIT-02)", " · MODIFIED outside the scripts (BIT-02)"), None: _t(L, " · sin línea en la bitácora", " · no write-log line")}[x["en_bitacora"]]
            print(f"{x['id']} · {x['etiqueta']}" + (f" · {_t(L, 'etapa', 'stage')} {x['etapa']}" if x["tipo"] == "manual" and x["etapa"] is not None else "")
                  + (f" · {x['decision']}" if x["decision"] else "") + (f" ({x['decision_id']})" if x["decision_id"] else "") + (f" · {x['por']}" if x["por"] else "")
                  + (f" · actor {x['actor']}" if x["actor"] else "")
                  + f" · sha256 {x['sha256'][:12]}{marca}")
        return
    if a.cmd == "comparar":
        da = cargar_instantanea(a.proyecto, a.a, L)
        quien = da.get("actor") or {}                   # una instantánea por actor se compara con el tablero actual del mismo actor
        db = construir(a.proyecto, actor=(quien.get("id") or quien.get("nombre")) if quien else None) if a.b == "actual" else cargar_instantanea(a.proyecto, a.b, L)
        r = comparar(da, db)
        if a.json: print(json.dumps(r, ensure_ascii=False, indent=1)); return
        print(_t(L, f"{r['a']} ({r['corte_a']}) → {r['b']} ({r['corte_b']}): {len(r['entraron'])} entraron · {len(r['salieron'])} salieron · {len(r['cambiaron'])} cambiaron",
                 f"{r['a']} ({r['corte_a']}) → {r['b']} ({r['corte_b']}): {len(r['entraron'])} in · {len(r['salieron'])} out · {len(r['cambiaron'])} changed"))
        for k, sig in (("entraron", "+"), ("salieron", "-")):
            for x in r[k][:40]: print(f"  {sig} [{x['vista']}] {x['ref']} {x['nombre']} ({x['columna'] or x['estado']})")
        for x in r["cambiaron"][:40]:
            print(f"  ~ [{x['vista']}] {x['ref']} {x['nombre']}: {x['de']['columna'] or x['de']['estado']} → {x['a']['columna'] or x['a']['estado']}"
                  + (f" ({x['de']['estado']} → {x['a']['estado']})" if x["de"]["estado"] != x["a"]["estado"] and x["de"]["columna"] != x["de"]["estado"] else ""))


if __name__ == "__main__":
    main()
