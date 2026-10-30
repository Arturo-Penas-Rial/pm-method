#!/usr/bin/env python3
"""Verificación de puertas de la junta (PRINCE2) · Board gate verification.

Cada puerta se verifica en tres capas antes de registrar la decisión con `estado.py puerta`:
  1. Salud: `sanidad.py --rapido` sin ERROR.
  2. Controles automáticos de la puerta: artefactos y tolerancias que PRINCE2 exige, criterios de éxito definidos o
     revisados, revisiones de calidad, registros abiertos y, con BMAD, los controles del propio BMAD (PRD y arquitectura
     en `status: final`, gate de preparación del sprint planning PASS/CONCERNS/FAIL).
  3. Lista de control de la junta: ítems de juicio que confirma una persona con rol (`lista` la genera; `confirmar`
     registra quién la confirmó). Nunca la marca el modelo por su cuenta.
Severidades: `bloqueo` (impide registrar "aprobado"; la junta puede registrar "condicionado" o forzar), `condicion`
(se registra como observación de la puerta), `aviso` (informativo). Cada hallazgo lleva su código de control (P-11,
E-06, S-<código de sanidad>, L-01…L-03 para la lista de control); `verificar` lo muestra y `--json` agrega `hallazgos`
como lista de {severidad, id, mensaje} además de las listas de mensajes `bloqueos`, `condiciones` y `avisos`.

Uso / Usage
  puertas.py --proyecto ./g verificar autorizar-etapa [--json]      # estado de las tres capas, sin escribir nada
  puertas.py --proyecto ./g lista autorizar-etapa                   # crea 00-direccion/decisiones/<fecha>-verificacion-<puerta>.md
  puertas.py --proyecto ./g confirmar autorizar-etapa --por "Ejecutivo: Nombre" [--na V-03="motivo"] [--no V-02="motivo"]
  puertas.py --proyecto ./g estado [--json]                         # insumo de informes: puertas, condiciones abiertas, próxima puerta
  puertas.py --proyecto ./g preparacion-bmad --resultado PASS|CONCERNS|FAIL --por "Arquitecto: Nombre" [--fecha ..] [--nota ..]
`confirmar` y `preparacion-bmad` registran actos humanos: los ejecuta pm-director (el hook lo hace cumplir).
"""
import argparse, csv, datetime, glob, json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import esquema as E

BMAD_DIR = os.path.normpath(os.path.join(AQUI, "..", "..", "pm-bmad-puente", "scripts"))

# idioma de los hallazgos y de la lista de control = estado.json.idioma (lo fija cada entrada con su `e`); los ids
# (I-, P-, E-, X-, C-, G-, L-, S-, V-), las severidades y las claves del JSON no se traducen
IDIOMA = "es"
def T(es, en): return E.t(IDIOMA, es, en)
def _idioma(e):
    global IDIOMA
    IDIOMA = (e or {}).get("idioma", "es") if isinstance(e, dict) else "es"

# ------------------------------------------------------------------ listas de control de la junta (juicio humano)
LISTAS = {
    "autorizar-inicio": [
        "El mandato y el project brief describen un problema u oportunidad que justifica invertir en la iniciación.",
        "El caso de negocio esquemático es plausible y el ejecutivo lo respalda.",
        "La junta está identificada (ejecutivo, usuario sénior, proveedor sénior) o hay un plan para completarla.",
        "El enfoque del proyecto (cómo se entregará) es razonable para el contexto.",
        "El plan de la etapa de iniciación (tiempo, costo, productos) es aceptable.",
    ],
    "autorizar-proyecto": [
        "El business case es viable, deseable y alcanzable; los beneficios son medibles y tienen dueño.",
        "Los criterios de éxito (beneficios, métricas, criterios de aceptación del producto) están definidos y acordados con el usuario sénior.",
        "El plan del proyecto es factible respecto de las tolerancias de proyecto fijadas.",
        "Los riesgos principales están identificados, con dueño y respuesta.",
        "Los enfoques de gestión (riesgo, calidad, cambio, comunicación) y los controles son adecuados.",
        "La especificación (PRD/requisitos) está acordada como línea base o hay una condición explícita para cerrarla.",
    ],
    "autorizar-etapa": [
        "Los productos de la etapa que termina se entregaron con la calidad acordada, o las excepciones están registradas.",
        "Los criterios de éxito y de aceptación de esos productos se verificaron (revisiones de calidad, DoD, aceptación del usuario).",
        "El business case sigue siendo viable con la información actualizada.",
        "El plan de la próxima etapa es factible y está dentro de las tolerancias de proyecto.",
        "Los riesgos y issues abiertos están tratados o asumidos de forma explícita.",
        "Las lecciones de la etapa se registraron y se aplican al plan siguiente.",
    ],
    "autorizar-plan-excepcion": [
        "El informe de excepción explica causa, impacto y opciones.",
        "El plan de excepción recupera el control dentro de las nuevas tolerancias.",
        "El business case sigue justificando continuar.",
    ],
    "autorizar-cierre": [
        "Todos los productos fueron entregados y aceptados, o las excepciones están acordadas.",
        "Se revisaron los criterios de éxito del proyecto (objetivos, métricas, beneficios logrados hasta ahora).",
        "La operación y el mantenimiento están preparados para recibir los productos.",
        "Los issues y riesgos abiertos se traspasaron como recomendaciones de seguimiento.",
        "Las lecciones se registraron y se comunicaron.",
        "Hay un plan de revisión de beneficios posterior al proyecto.",
    ],
}
LISTAS_EN = {
    "autorizar-inicio": [
        "The mandate and the project brief describe a problem or opportunity that justifies investing in initiation.",
        "The outline business case is plausible and the executive backs it.",
        "The board is identified (executive, senior user, senior supplier) or there is a plan to complete it.",
        "The project approach (how it will be delivered) is reasonable for the context.",
        "The initiation stage plan (time, cost, products) is acceptable.",
    ],
    "autorizar-proyecto": [
        "The business case is viable, desirable and achievable; the benefits are measurable and have an owner.",
        "The success criteria (benefits, metrics, product acceptance criteria) are defined and agreed with the senior user.",
        "The project plan is feasible against the project tolerances set.",
        "The main risks are identified, with an owner and a response.",
        "The management approaches (risk, quality, change, communication) and the controls are adequate.",
        "The specification (PRD/requirements) is agreed as a baseline or there is an explicit condition to close it.",
    ],
    "autorizar-etapa": [
        "The products of the ending stage were delivered with the agreed quality, or the exceptions are recorded.",
        "The success and acceptance criteria of those products were verified (quality reviews, DoD, user acceptance).",
        "The business case is still viable with the updated information.",
        "The next stage plan is feasible and within the project tolerances.",
        "Open risks and issues are handled or explicitly accepted.",
        "The stage lessons were recorded and are applied to the next plan.",
    ],
    "autorizar-plan-excepcion": [
        "The exception report explains cause, impact and options.",
        "The exception plan regains control within the new tolerances.",
        "The business case still justifies continuing.",
    ],
    "autorizar-cierre": [
        "All products were delivered and accepted, or the exceptions are agreed.",
        "The project's success criteria were reviewed (objectives, metrics, benefits achieved so far).",
        "Operations and maintenance are ready to receive the products.",
        "Open issues and risks were handed over as follow-on action recommendations.",
        "The lessons were recorded and communicated.",
        "There is a post-project benefits review plan.",
    ],
}

# ítem que se suma a la lista de autorizar-cierre en un cierre prematuro (PRINCE2 CP, criterios de completitud: inventario,
# rescate, estado seguro y brechas elevadas al negocio; pm-knowledge prince2-principios-personas-procesos.md §5.7)
LISTA_PREMATURO = "Cierre prematuro: los productos rescatables están identificados, lo que debe quedar en estado seguro está planificado (o en un plan de excepción) y las brechas que deja la cancelación se elevaron al negocio."
LISTA_PREMATURO_EN = "Premature closure: the salvageable products are identified, what must be made safe is planned (or in an exception plan) and the gaps left by the cancellation were raised to the business."

def items_lista(e, tipo):
    """Ítems de la lista de control de la junta para la puerta `tipo` en el estado `e` (en el idioma del proyecto)."""
    en = (e or {}).get("idioma") == "en"
    return (LISTAS_EN if en else LISTAS)[tipo] + ([LISTA_PREMATURO_EN if en else LISTA_PREMATURO] if tipo == "autorizar-cierre" and E.cierre_prematuro(e) else [])

def leer_csv(proyecto, reg):
    p = os.path.join(proyecto, "03-control", "registros", f"{reg}.csv")
    return E.leer_filas(p) if os.path.exists(p) else []     # ilegible → E.DatosIlegibles (nunca "sin abiertos")

def abiertos(proyecto, reg):
    ab = E.REGISTROS.get(reg, {}).get("abiertos", [])
    return [f for f in leer_csv(proyecto, reg) if f.get("estado") in ab]

def art_ok(proyecto, e, clave):
    a = e.get("artefactos", {}).get(clave)
    return bool(a) and (a.get("externo") or os.path.exists(os.path.join(proyecto, a.get("ruta", ""))))

NIVELES_ACEPTAN_SUPUESTOS = ("junta", "ejecutivo", "capa-negocio")

def supuestos_aceptados(proyecto, ids):
    """{S-###: D-###} para los supuestos de `ids` que una decisión de nivel junta (o ejecutivo, o capa de negocio) cita como
    aceptados: la fila de decisiones.csv menciona el id y el verbo "aceptar"/"accept" (no "aceptación") en su texto."""
    out = {}
    for d in leer_csv(proyecto, "decisiones"):
        if d.get("nivel") not in NIVELES_ACEPTAN_SUPUESTOS: continue
        txt = " ".join(d.get(c, "") for c in ("decision", "contexto", "opciones_consideradas", "artefactos_afectados", "notas"))
        if not re.search(r"\bacept(?:ad[oa]s?|ar|an?|amos|o)\b|\baccept(?:ed|s)?\b", txt, re.I): continue   # no "aceptación"
        for sid in ids:
            if sid not in out and re.search(rf"(?<![\w-]){re.escape(sid)}(?![\w-])", txt): out[sid] = d.get("id", "")
    return out

def art_prefijo(e, prefijo):
    return [k for k in e.get("artefactos", {}) if k.startswith(prefijo)]

def sanidad_errores(proyecto):
    try:
        r = subprocess.run([sys.executable, os.path.join(AQUI, "sanidad.py"), "--proyecto", proyecto, "--rapido", "--json"],
                           capture_output=True, text=True, encoding="utf-8", timeout=90)
        if not (r.stdout or "").strip():     # sanidad no llegó a evaluar (dato ilegible, error): es un bloqueo, no "sin errores"
            det = " ".join((r.stderr or "").strip().splitlines()[:1]) or T(f"código {r.returncode}", f"exit code {r.returncode}")
            return [{"codigo": "SAN", "mensaje": T(f"sanidad.py no pudo evaluar el proyecto: {det}", f"sanidad.py could not evaluate the project: {det}")}]
        return [h for h in json.loads(r.stdout).get("hallazgos", []) if h["severidad"] == "ERROR"]
    except Exception as x:
        return [{"codigo": "SAN", "mensaje": T(f"no se pudo ejecutar sanidad.py: {x}", f"sanidad.py could not be run: {x}")}]

def bmad_estado(proyecto, e):
    """{'prd': status, 'arquitectura': status, 'planning': dir, 'implementation': dir} o None si no hay BMAD."""
    if e.get("integraciones", {}).get("especificacion") != "bmad": return None
    try:
        sys.path.insert(0, BMAD_DIR); import bmad as B
        b = B.detectar_bmad(proyecto, None, e); arts = B.inventario(b)
        return {"prd": (arts.get("prd") or {}).get("estado_bmad", "") if "prd" in arts else None,
                "arquitectura": (arts.get("arquitectura") or {}).get("estado_bmad", "") if "arquitectura" in arts else None,
                "planning": b.get("planning", ""), "implementation": b.get("implementation", "")}
    except BaseException as x:
        return {"error": str(x)}

def preparacion_bmad(proyecto, e, bm):
    """Veredicto del gate de preparación de BMAD (bmad-sprint-planning): el registrado en estado.json o, si BMAD guardó
    hallazgos de FAIL en <planning>/implementation-readiness.md más recientes que sprint-status.yaml, FAIL."""
    reg = (e.get("integraciones", {}).get("bmad", {}) or {}).get("preparacion") or {}
    fail = os.path.join(bm.get("planning", "") or "", "implementation-readiness.md")
    ss = os.path.join(bm.get("implementation", "") or "", "sprint-status.yaml")
    if os.path.exists(fail):
        f_fail = datetime.date.fromtimestamp(os.path.getmtime(fail)).isoformat()
        ss_posterior = os.path.exists(ss) and os.path.getmtime(ss) > os.path.getmtime(fail)
        reg_posterior = bool(reg) and reg.get("registrado", "") > datetime.datetime.fromtimestamp(os.path.getmtime(fail)).isoformat(timespec="seconds")
        if not ss_posterior and not reg_posterior:
            return {"resultado": "FAIL", "fuente": os.path.relpath(fail, proyecto), "fecha": f_fail}
    return reg or None

# prefijo del mensaje de G-01 en español y en inglés (estado.py no lo copia como condición nueva de la puerta)
PREFIJO_G01 = ("condiciones abiertas de puertas anteriores: ", "open conditions from earlier gates: ")

def controles(proyecto, e, tipo, tol_nueva=None):
    """Lista de (severidad, id, mensaje) de las capas 1 y 2 para la puerta `tipo`."""
    _idioma(e)
    out = []
    add = lambda sev, i, m: out.append((sev, i, m))
    for h in sanidad_errores(proyecto):
        add("bloqueo", f"S-{h['codigo']}", T(f"sanidad {h['codigo']}: {h['mensaje']}", f"health check {h['codigo']}: {h['mensaje']}"))
    n = e.get("etapa_actual", {}).get("numero", 0)
    bm = bmad_estado(proyecto, e)
    if bm and bm.get("error"): add("bloqueo", "B-00", T(f"BMAD declarado pero no legible: {bm['error']}", f"BMAD declared but not readable: {bm['error']}")); bm = None
    previas = [p for p in e.get("puertas", []) if p.get("decision") in ("condicionado", "aprobado") and p.get("condiciones") and not p.get("condiciones_cumplidas")]
    if previas and tipo in ("autorizar-proyecto", "autorizar-etapa", "autorizar-plan-excepcion", "autorizar-cierre"):
        txt = "; ".join(f"{p['tipo']} {p.get('fecha', '')}" for p in previas)
        add("bloqueo" if tipo == "autorizar-cierre" else "condicion", "G-01",
            T(f"{PREFIJO_G01[0]}{txt} (verificarlas y registrar estado.py cumplir-condiciones, o traspasarlas como recomendación)",
              f"{PREFIJO_G01[1]}{txt} (verify them and record estado.py cumplir-condiciones, or hand them over as a recommendation)"))
    if tipo == "autorizar-inicio":
        if not art_ok(proyecto, e, "project-brief"): add("bloqueo", "I-01", T("falta el project brief (pm-mandato-y-brief)", "the project brief is missing (pm-mandato-y-brief)"))
        if not e["roles"].get("ejecutivo"): add("bloqueo", "I-02", T("sin ejecutivo designado", "no executive appointed"))
        if not art_ok(proyecto, e, "plan-etapa-1"): add("condicion", "I-03", T("sin plan de la etapa de iniciación (plan-etapa-1)", "no initiation stage plan (plan-etapa-1)"))
    elif tipo == "autorizar-proyecto":
        for art, i in (("pid", "P-01"), ("business-case", "P-02")):
            if not art_ok(proyecto, e, art): add("bloqueo", i, T(f"falta el artefacto {art} (o su archivo)", f"the artifact {art} (or its file) is missing"))
        faltan = [d for d in ("tiempo", "costo") if not e["tolerancias"]["proyecto"].get(d)]
        if faltan: add("bloqueo", "P-03", T(f"faltan tolerancias de proyecto ({', '.join(faltan)}): las fija la junta; pm-director las registra",
                                            f"project tolerances are missing ({', '.join(faltan)}): the board sets them; pm-director records them"))
        beneficios = bool(art_prefijo(e, "enfoque-beneficios"))
        bc = e["artefactos"].get("business-case", {}).get("ruta", "")
        if bc and os.path.exists(os.path.join(proyecto, bc)):
            beneficios = beneficios or bool(re.search(r"\bB-\d+|\bSM-C?\d+|beneficio", open(os.path.join(proyecto, bc), encoding="utf-8").read(), re.I))
        okr = bool(art_prefijo(e, "okr"))
        if not beneficios and not okr: add("condicion", "P-04", T("no se encontraron criterios de éxito (beneficios B-n, métricas SM-n, enfoque de beneficios u OKR)",
                                                                  "no success criteria were found (benefits B-n, metrics SM-n, benefits management approach or OKR)"))
        elif not beneficios: add("condicion", "P-04", T("los criterios de éxito están solo en OKR: faltan beneficios B-n en el business case o un enfoque de beneficios con dueño y fecha de medición (los OKR complementan, no reemplazan, la revisión de beneficios)",
                                                        "the success criteria are only in OKR: benefits B-n in the business case or a benefits management approach with an owner and a measurement date are missing (OKR complement the benefits review, they do not replace it)"))
        elif not art_prefijo(e, "enfoque-beneficios"): add("aviso", "P-04", T("sin enfoque de beneficios (cómo, cuándo y quién mide cada beneficio, incluso después del proyecto)",
                                                                              "no benefits management approach (how, when and who measures each benefit, also after the project)"))
        for r in ("usuario_senior", "proveedor_senior"):
            if not e["roles"].get(r): add("condicion", "P-05", T(f"junta incompleta: falta {r}", f"incomplete board: {r} is missing"))
        if not art_ok(proyecto, e, "plan-proyecto"): add("condicion", "P-06", T("sin plan de proyecto registrado (o incluido en el PID)", "no project plan recorded (or included in the PID)"))
        criticos = [f["id"] for f in abiertos(proyecto, "supuestos") if f.get("criticidad") == "alta" and f.get("validado") != "si"]
        acept = supuestos_aceptados(proyecto, criticos) if criticos else {}
        resto = [x for x in criticos if x not in acept]
        if resto: add("condicion", "P-11", T(f"supuestos críticos sin validar: {', '.join(resto[:8])}{' …' if len(resto) > 8 else ''} (la junta invierte sobre hipótesis; acordar experimento, criterio y fecha o aceptarlos explícitamente con una decisión de la junta)",
                                             f"unvalidated critical assumptions: {', '.join(resto[:8])}{' …' if len(resto) > 8 else ''} (the board would invest on hypotheses; agree experiment, criterion and deadline or accept them explicitly with a board decision)"))
        if acept: add("aviso", "P-11", T(f"supuestos críticos sin validar aceptados por decisión de la junta: {', '.join(f'{k} ({v})' for k, v in list(acept.items())[:8])}{' …' if len(acept) > 8 else ''} (seguir su validación; la sanidad SUP sigue mostrándolos)",
                                         f"unvalidated critical assumptions accepted by board decision: {', '.join(f'{k} ({v})' for k, v in list(acept.items())[:8])}{' …' if len(acept) > 8 else ''} (keep validating them; the SUP health checks still show them)"))
        sts = leer_csv(proyecto, "stakeholders")
        sin_mapa = [f["id"] for f in sts if not f.get("poder") or not f.get("interes")]
        if not sts: add("aviso", "P-09", T("registro de interesados vacío: sin matriz poder/interés (pm-interesados)", "empty stakeholder register: no power/interest grid (pm-interesados)"))
        elif sin_mapa: add("aviso", "P-09", T(f"interesados sin ubicar en la matriz poder/interés: {', '.join(sin_mapa[:8])}{' …' if len(sin_mapa) > 8 else ''}",
                                              f"stakeholders not placed on the power/interest grid: {', '.join(sin_mapa[:8])}{' …' if len(sin_mapa) > 8 else ''}"))
        if not leer_csv(proyecto, "raci") and not art_ok(proyecto, e, "matriz-raci"):
            add("aviso", "P-10", T("sin matriz RACI (raci.csv o artefacto matriz-raci): quién es R, A, C e I en productos y decisiones clave",
                                   "no RACI matrix (raci.csv or matriz-raci artifact): who is R, A, C and I for key products and decisions"))
        if bm:
            if bm["prd"] is None: add("bloqueo", "P-07", T("BMAD declarado pero sin PRD", "BMAD declared but without a PRD"))
            elif bm["prd"] not in ("final", "approved"): add("bloqueo", "P-07", T(f"el PRD de BMAD no está final (status: {bm['prd'] or 'sin estado'}); cerrarlo con bmad-prd",
                                                                                f"the BMAD PRD is not final (status: {bm['prd'] or 'no status'}); close it with bmad-prd"))
            if bm["arquitectura"] is not None and bm["arquitectura"] not in ("final", "approved"):
                add("condicion", "P-08", T(f"arquitectura de BMAD no final (status: {bm['arquitectura'] or 'sin estado'}): suficiente para estimar, cerrarla antes de la primera etapa de entrega",
                                           f"BMAD architecture not final (status: {bm['arquitectura'] or 'no status'}): enough to estimate, close it before the first delivery stage"))
    elif tipo == "autorizar-etapa":
        if not art_ok(proyecto, e, f"plan-etapa-{n + 1}"): add("bloqueo", "E-01", T(f"falta el plan de la etapa a autorizar (plan-etapa-{n + 1})", f"the plan of the stage to authorize is missing (plan-etapa-{n + 1})"))
        if not (tol_nueva or any(e["tolerancias"].get("etapa", {}).values())): add("bloqueo", "E-02", T("faltan tolerancias de la etapa (--tol o 'tolerancia --nivel etapa')", "stage tolerances are missing (--tol or 'tolerancia --nivel etapa')"))
        if e.get("excepcion_abierta"): add("bloqueo", "E-03", T(f"hay una excepción abierta ({e['excepcion_abierta']}): corresponde autorizar-plan-excepcion", f"there is an open exception ({e['excepcion_abierta']}): autorizar-plan-excepcion applies"))
        if e.get("fase") == "entrega" and not art_ok(proyecto, e, f"informe-fin-etapa-{n}"):
            add("bloqueo", "E-04", T(f"falta el informe de fin de la etapa {n} (informe-fin-etapa-{n})", f"the end stage report of stage {n} is missing (informe-fin-etapa-{n})"))
        q = abiertos(proyecto, "calidad")
        if q: add("condicion", "E-05", T(f"revisiones de calidad sin cerrar: {', '.join(f['id'] for f in q[:8])}{' …' if len(q) > 8 else ''}", f"quality reviews not closed: {', '.join(f['id'] for f in q[:8])}{' …' if len(q) > 8 else ''}"))
        altos = [f for f in abiertos(proyecto, "riesgos") if (f.get("puntuacion") or "0").replace(".", "").isdigit()
                 and float(f.get("puntuacion") or 0) >= float(e.get("umbrales_riesgo", {}).get("alto", 15)) and not f.get("respuesta")]
        if altos: add("condicion", "E-06", T(f"riesgos altos sin respuesta: {', '.join(f['id'] for f in altos[:8])}", f"high risks without a response: {', '.join(f['id'] for f in altos[:8])}"))
        # E-11 (PRINCE2 SB, preparar el plan de la siguiente etapa: revisar el registro de lecciones; §4.c.7 lecciones incorporadas):
        # lecciones clasificadas para planificación que siguen abiertas sin acción (pm-lecciones-aprendidas, lecciones.py)
        plan_l = [f for f in leer_csv(proyecto, "lecciones") if "planificacion" in re.split(r"[;,]\s*", f.get("aplicar_en") or "")
                  and f.get("estado") in ("registrada", "revisada") and not (f.get("accion") or "").strip()]
        if plan_l:
            plan_l.sort(key=lambda f: ({"alto": 0, "medio": 1, "bajo": 2}.get(f.get("impacto"), 3), f.get("id", "")))
            add("aviso", "E-11", T(f"lecciones para planificación sin considerar en el plan de la etapa: {', '.join(f['id'] + (' (' + f['impacto'] + ')' if f.get('impacto') else '') for f in plan_l[:8])}{' …' if len(plan_l) > 8 else ''} (accionarlas en el plan o descartarlas con motivo: lecciones.py accionar|descartar)",
                                   f"planning lessons not considered in the stage plan: {', '.join(f['id'] + (' (' + f['impacto'] + ')' if f.get('impacto') else '') for f in plan_l[:8])}{' …' if len(plan_l) > 8 else ''} (action them in the plan or discard them with a reason: lecciones.py accionar|descartar)"))
        if bm:
            if "bmad-prd" not in e.get("artefactos", {}): add("bloqueo", "E-07", T("sin línea base del PRD de BMAD: bmad.py linea-base prd --version 1.0 --por …", "no baseline of the BMAD PRD: bmad.py linea-base prd --version 1.0 --por …"))
            if bm["prd"] not in ("final", "approved"): add("bloqueo", "E-08", T(f"el PRD de BMAD no está final (status: {bm['prd'] or 'sin estado'})", f"the BMAD PRD is not final (status: {bm['prd'] or 'no status'})"))
            if bm["arquitectura"] is None: add("bloqueo", "E-09", T("BMAD sin arquitectura: BMAD la exige antes de crear épicas e historias", "BMAD without architecture: BMAD requires it before creating epics and stories"))
            elif bm["arquitectura"] not in ("final", "approved"): add("bloqueo", "E-09", T(f"la arquitectura de BMAD no está final (status: {bm['arquitectura'] or 'sin estado'})", f"the BMAD architecture is not final (status: {bm['arquitectura'] or 'no status'})"))
            pr = preparacion_bmad(proyecto, e, bm)
            if not pr: add("aviso", "E-10", T("sin veredicto del gate de preparación de BMAD (bmad-sprint-planning, intent readiness); registrarlo con puertas.py preparacion-bmad",
                                              "no verdict from the BMAD readiness gate (bmad-sprint-planning, intent readiness); record it with puertas.py preparacion-bmad"))
            elif pr.get("resultado") == "FAIL": add("bloqueo", "E-10", T(f"gate de preparación de BMAD en FAIL{' (' + pr['fuente'] + ')' if pr.get('fuente') else ''}: corregir con bmad-correct-course o la skill de plan que corresponda",
                                                                       f"BMAD readiness gate at FAIL{' (' + pr['fuente'] + ')' if pr.get('fuente') else ''}: fix it with bmad-correct-course or the matching planning skill"))
            elif pr.get("resultado") == "CONCERNS":
                # el mismo veredicto ya lo trató la junta como condición de una puerta posterior a él, y esa condición se cumplió: aviso
                tratada = [p for p in e.get("puertas", []) if p.get("decision") in ("condicionado", "aprobado") and p.get("condiciones_cumplidas")
                           and (p.get("fecha") or "") >= (pr.get("fecha") or "9999")
                           and ("preparación de BMAD" in (p.get("condiciones") or "") or "E-10" in (p.get("condiciones") or ""))]
                if tratada:
                    t = tratada[-1]
                    add("aviso", "E-10", T(f"gate de preparación de BMAD en CONCERNS ({pr.get('fecha', '')}) ya tratado en {t['tipo']} {t.get('fecha', '')}"
                                           f"{' (' + t['decision_id'] + ')' if t.get('decision_id') else ''}, condiciones cumplidas {t['condiciones_cumplidas']}; "
                                           "si el plan cambió, registrar un veredicto nuevo con puertas.py preparacion-bmad",
                                           f"BMAD readiness gate at CONCERNS ({pr.get('fecha', '')}) already handled in {t['tipo']} {t.get('fecha', '')}"
                                           f"{' (' + t['decision_id'] + ')' if t.get('decision_id') else ''}, conditions met {t['condiciones_cumplidas']}; "
                                           "if the plan changed, record a new verdict with puertas.py preparacion-bmad"))
                else:
                    add("condicion", "E-10", T(f"gate de preparación de BMAD en CONCERNS ({pr.get('fecha', '')}{': ' + pr['nota'] if pr.get('nota') else ''})",
                                               f"BMAD readiness gate at CONCERNS ({pr.get('fecha', '')}{': ' + pr['nota'] if pr.get('nota') else ''})"))
    elif tipo == "autorizar-plan-excepcion":
        if not art_prefijo(e, "plan-excepcion"): add("bloqueo", "X-01", T("falta el plan de excepción (plan-excepcion-X-###)", "the exception plan is missing (plan-excepcion-X-###)"))
        if not art_prefijo(e, "informe-excepcion"): add("condicion", "X-02", T("no hay informe de excepción registrado", "no exception report recorded"))
    elif tipo == "autorizar-cierre":
        # cierre prematuro (PRINCE2 CP, preparar el cierre prematuro; docs/PUERTAS.md §3.2): C-08 exige el inventario de
        # productos por estado; los Must sin aceptar (C-07) se pueden transferir legítimamente y pasan a aviso; las revisiones
        # de calidad abiertas (C-04) siguen bloqueando: se completan o se cancelan
        prem = E.cierre_prematuro(e)
        if prem and not art_ok(proyecto, e, "inventario-cierre-prematuro"):
            add("bloqueo", "C-08", T("cierre prematuro sin inventario de productos por estado (artefacto inventario-cierre-prematuro: aprobados, en desarrollo, "
                                     "con concesión, no iniciados, a dejar en estado seguro y útiles para otros; guía de pm-cierre-proyecto §3)",
                                     "premature closure without a product inventory by status (artifact inventario-cierre-prematuro: approved, in development, "
                                     "under concession, not started, to be made safe and useful to others; pm-cierre-proyecto guide §3)"))
        # C-09 (PRINCE2 CP, preparar el cierre prematuro: el trabajo de rescate o de estado seguro puede requerir un plan de
        # excepción; docs/PUERTAS.md §3.2): el plan aprobado durante el cierre se completa o se cierra antes de autorizar el cierre
        pe = prem.get("plan_excepcion") if isinstance(prem.get("plan_excepcion"), dict) else {}
        if pe and pe.get("estado") not in ("completado", "cerrado"):
            ref = ", ".join(x for x in (pe.get("artefacto"), pe.get("decision"), pe.get("fecha")) if x)
            add("bloqueo", "C-09", T(f"plan de excepción del cierre prematuro sin completar ni cerrar ({ref}): estado.py cierre --plan-excepcion completado|cerrado --por \"<rol: nombre>\" (pm-director)",
                                     f"premature closure exception plan neither completed nor closed ({ref}): estado.py cierre --plan-excepcion completado|cerrado --por \"<role: name>\" (pm-director)"))
        for art, i in (("informe-fin-proyecto", "C-01"), ("registro-aceptacion", "C-02")):
            if not art_ok(proyecto, e, art): add("bloqueo", i, T(f"falta {art}", f"{art} is missing"))
        # C-03 por id (PRINCE2 CP, recomendar el cierre: issues y riesgos abiertos → recomendaciones de seguimiento con dueño)
        ab = abiertos(proyecto, "issues") + abiertos(proyecto, "riesgos")
        faltan = sin_recomendacion(proyecto, e, [f["id"] for f in ab]) if ab else {}
        if faltan == "externo":
            add("aviso", "C-03", T(f"recomendaciones de seguimiento externas: comprobar a mano que citen con responsable {lista_ids(sorted(f['id'] for f in ab))}",
                                   f"external follow-on action recommendations: check by hand that they cite, with an owner, {lista_ids(sorted(f['id'] for f in ab))}"))
        elif faltan is None:
            add("bloqueo", "C-03", T(f"{len(ab)} issues/riesgos abiertos sin recomendaciones de seguimiento: {lista_ids(sorted(f['id'] for f in ab))}",
                                     f"{len(ab)} open issues/risks without follow-on action recommendations: {lista_ids(sorted(f['id'] for f in ab))}"))
        elif faltan:
            motivo_en = {"no citado": "not cited", "citado sin responsable": "cited without an owner"}
            add("bloqueo", "C-03", T("issues/riesgos abiertos sin recomendación de seguimiento con responsable: "
                                     + lista_ids([f"{i} ({m})" for i, m in sorted(faltan.items())]) + " (citarlos por id en recomendaciones-seguimiento, con responsable)",
                                     "open issues/risks without a follow-on action recommendation with an owner: "
                                     + lista_ids([f"{i} ({motivo_en.get(m, m)})" for i, m in sorted(faltan.items())]) + " (cite them by id in recomendaciones-seguimiento, with an owner)"))
        q = abiertos(proyecto, "calidad")
        if q: add("bloqueo", "C-04", T(f"revisiones de calidad sin cerrar: {', '.join(f['id'] for f in q[:8])}"
                                     + (" (cierre prematuro: completarlas o cancelarlas, registro.py actualizar calidad Q-### --campo estado=cancelada)" if prem else ""),
                                     f"quality reviews not closed: {', '.join(f['id'] for f in q[:8])}"
                                     + (" (premature closure: complete or cancel them, registro.py actualizar calidad Q-### --campo estado=cancelada)" if prem else "")))
        if not art_ok(proyecto, e, "informe-lecciones"): add("condicion", "C-05", T("sin informe de lecciones", "no lessons report"))
        if not art_ok(proyecto, e, "plan-revision-beneficios"): add("condicion", "C-06", T("sin plan de revisión de beneficios (criterios de éxito posteriores al proyecto)", "no benefits review plan (post-project success criteria)"))
        # C-07 (PRINCE2 CP, confirmar la aceptación de los productos; registro de productos A13): requisitos y productos Must
        # cuyo estado derivado (estado.py productos) no es aceptado ni con concesión
        try:
            import estado as ES_
            m = ES_.productos(proyecto, e)["must"]
        except Exception as x:          # sin verificar no es "todo aceptado": queda como condición con el motivo
            m = {"requisitos": [], "productos": []}
            add("aviso" if prem else "condicion", "C-07", T(f"no se pudo verificar la aceptación de los Must ({x}); revisar con estado.py productos",
                                                            f"the acceptance of the Must items could not be checked ({x}); review it with estado.py productos"))
        if m["requisitos"] or m["productos"]:
            add("aviso" if prem else "condicion", "C-07", T("Must sin aceptar: " + "; ".join(([f"requisitos {lista_ids([r['id'] for r in m['requisitos']])}"] if m["requisitos"] else [])
                                                                     + ([f"productos {lista_ids(m['productos'])}"] if m["productos"] else []))
                + (" (cierre prematuro: transferirlos es legítimo; declararlos en el inventario y en recomendaciones-seguimiento)" if prem else
                   " (registrar la aceptación: registro-aceptacion o aceptacion-<producto>, o la concesión; detalle: estado.py productos)"),
                "Must items not accepted: " + "; ".join(([f"requirements {lista_ids([r['id'] for r in m['requisitos']])}"] if m["requisitos"] else [])
                                                        + ([f"products {lista_ids(m['productos'])}"] if m["productos"] else []))
                + (" (premature closure: handing them over is legitimate; declare them in the inventory and in recomendaciones-seguimiento)" if prem else
                   " (record the acceptance: registro-aceptacion or aceptacion-<product>, or the concession; detail: estado.py productos)")))
    return out

def lista_ids(xs, n=8):
    return ", ".join(xs[:n]) + (T(f" … y {len(xs) - n} más", f" … and {len(xs) - n} more") if len(xs) > n else "")

VACIO_CELDA = re.compile(r"^\s*(?:|—|-|\{\{.*\}\}|\[por confirmar\]|\[to be confirmed\])\s*$", re.I)
CAB_RESPONSABLE = re.compile(r"^(?:responsable|destinatario|dueñ[oa]|owner|addressee|proposed owner|responsible)", re.I)

def sin_recomendacion(proyecto, e, ids):
    """C-03 por id: {id: motivo} de los issues y riesgos abiertos que `recomendaciones-seguimiento` no cita con un
    responsable (fila de tabla con la columna Responsable o Destinatario llena, o línea «… Responsable: <nombre>»).
    None si falta el artefacto; "externo" si es un enlace que no se puede leer."""
    a = e.get("artefactos", {}).get("recomendaciones-seguimiento")
    if not art_ok(proyecto, e, "recomendaciones-seguimiento"): return None
    if a.get("externo"): return "externo"
    try: lineas = open(os.path.join(proyecto, a["ruta"]), encoding="utf-8", errors="replace").read().splitlines()
    except OSError: return None
    estado = {}; cols = None
    for l in lineas:
        if l.lstrip().startswith("|"):
            celdas = [c.strip() for c in l.strip().strip("|").split("|")]
            if all(re.match(r"^:?-{3,}:?$", c) for c in celdas if c): continue
            citados = [i for i in ids if re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", l)]
            if not citados:
                cs = [j for j, c in enumerate(celdas) if CAB_RESPONSABLE.match(c)]
                if cs: cols = cs
                continue
            con = bool(cols) and any(j < len(celdas) and not VACIO_CELDA.match(celdas[j]) for j in cols)
        else:
            cols = None
            citados = [i for i in ids if re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", l)]
            con = bool(re.search(r"(?i)\b(?:responsable|owner|dueñ[oa])\s*:\s*[^\s\[{—-]", l))
        for i in citados:
            if con: estado[i] = "ok"
            else: estado.setdefault(i, "citado sin responsable")
    return {i: estado.get(i, "no citado") for i in ids if estado.get(i) != "ok"}

# ------------------------------------------------------------------ lista de control (capa 3)
def ruta_lista(proyecto, tipo):
    xs = sorted(glob.glob(os.path.join(proyecto, "00-direccion", "decisiones", f"*-verificacion-{tipo}.md")))
    return xs[-1] if xs else None

def estado_lista(proyecto, tipo):
    """{'ruta','pendientes','no_cumple','confirmada_por'} de la lista más reciente de la puerta, o None."""
    p = ruta_lista(proyecto, tipo)
    if not p: return None
    t = open(p, encoding="utf-8").read()
    pend = re.findall(r"(?m)^- \[ \] (V-\d+)", t); no = re.findall(r"(?m)^- \[!\] (V-\d+)", t)
    por = re.search(r"(?m)^confirmada_por:\s*\"?([^\"\n]*)", t)
    return {"ruta": os.path.relpath(p, proyecto), "pendientes": pend, "no_cumple": no, "confirmada_por": (por.group(1).strip() if por else "")}

def evaluar_detalle(proyecto, e, tipo, tol_nueva=None):
    """Hallazgos de las tres capas como lista de {severidad, id, mensaje}, más el resumen de la lista de control."""
    hs = [{"severidad": s, "id": i, "mensaje": m} for s, i, m in controles(proyecto, e, tipo, tol_nueva)]
    li = estado_lista(proyecto, tipo)
    if not li: hs.append({"severidad": "bloqueo", "id": "L-01", "mensaje": T(f"falta la lista de control de la junta: puertas.py --proyecto <dir> lista {tipo} y confirmarla (puertas.py confirmar …)",
                                                                            f"the board checklist is missing: puertas.py --proyecto <dir> lista {tipo} and confirm it (puertas.py confirmar …)")})
    else:
        if li["no_cumple"]: hs.append({"severidad": "bloqueo", "id": "L-02", "mensaje": T(f"la junta marcó ítems que no se cumplen en {li['ruta']}: {', '.join(li['no_cumple'])}",
                                                                                         f"the board marked items as not met in {li['ruta']}: {', '.join(li['no_cumple'])}")})
        if li["pendientes"]: hs.append({"severidad": "bloqueo", "id": "L-03", "mensaje": T(f"lista de control sin confirmar ({li['ruta']}): {', '.join(li['pendientes'])}",
                                                                                          f"checklist not confirmed ({li['ruta']}): {', '.join(li['pendientes'])}")})
    return hs, li

def evaluar(proyecto, e, tipo, tol_nueva=None):
    """Para estado.py: (bloqueos, condiciones, avisos, resumen_lista), listas de mensajes."""
    hs, li = evaluar_detalle(proyecto, e, tipo, tol_nueva)
    sel = lambda sev: [h["mensaje"] for h in hs if h["severidad"] == sev]
    return sel("bloqueo"), sel("condicion"), sel("aviso"), li

def crear_lista(a, e):
    hoy = a.fecha or datetime.date.today().isoformat()
    d = os.path.join(a.proyecto, "00-direccion", "decisiones"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{hoy}-verificacion-{a.tipo}.md")
    cs = controles(a.proyecto, e, a.tipo)
    simb = {"bloqueo": T("BLOQUEO", "BLOCKER"), "condicion": T("condición", "condition"), "aviso": T("aviso", "warning")}
    L = ["---", "tipo: verificacion-puerta", f"puerta: {a.tipo}", f"fecha: {hoy}", f"etapa: {e.get('etapa_actual', {}).get('numero')}",
         'confirmada_por: ""', "estado: pendiente", "---", "",
         T(f"# Verificación de la puerta {a.tipo} · Gate verification — {e.get('proyecto')}", f"# Gate verification {a.tipo} — {e.get('proyecto')}"), "",
         T("## 1-2. Salud y controles automáticos · Health and automatic checks", "## 1-2. Health and automatic checks"), "",
         T("| Severidad | Id | Hallazgo |", "| Severity | Id | Finding |"), "|---|---|---|"]
    L += [f"| {simb[s]} | {i} | {m} |" for s, i, m in cs] or [T("| — | — | sin hallazgos (sanidad sin ERROR y controles cumplidos) |", "| — | — | no findings (health check without ERROR and checks met) |")]
    L += ["", T(f"Generado por `puertas.py verificar` el {hoy}. Los bloqueos impiden registrar `aprobado`; la junta puede decidir `condicionado` (pasan a condiciones) o forzar con constancia.",
                f"Generated by `puertas.py verificar` on {hoy}. Blockers prevent recording `aprobado`; the board can decide `condicionado` (they become conditions) or force it, on record."), "",
          T("## 3. Lista de control de la junta · Board checklist", "## 3. Board checklist"), "",
          T("La confirma una persona con rol en la junta (`puertas.py confirmar … --por \"Rol: Nombre\"`). `[x]` cumple · `[!]` no cumple · `N/A` con motivo.",
            "A person with a board role confirms it (`puertas.py confirmar … --por \"Role: Name\"`). `[x]` met · `[!]` not met · `N/A` with a reason."), ""]
    items = items_lista(e, a.tipo)
    L += [f"- [ ] V-{k:02d} {txt}" for k, txt in enumerate(items, 1)]
    E.escribir_atomico(p, "\n".join(L) + "\n")
    print(T(f"Lista creada: {os.path.relpath(p, a.proyecto)} ({len(cs)} hallazgos automáticos, {len(items)} ítems para la junta)",
            f"Checklist created: {os.path.relpath(p, a.proyecto)} ({len(cs)} automatic findings, {len(items)} items for the board)"))

def confirmar(a, e):
    p = ruta_lista(a.proyecto, a.tipo)
    if not p: sys.exit(T(f"No hay lista para {a.tipo}: puertas.py --proyecto {a.proyecto} lista {a.tipo}", f"There is no checklist for {a.tipo}: puertas.py --proyecto {a.proyecto} lista {a.tipo}"))
    t = open(p, encoding="utf-8").read()
    def pares(xs):
        d = {}
        for x in xs or []:
            k, _, v = x.partition("=")
            if not re.match(r"^V-\d+$", k.strip()) or not v.strip(): sys.exit(T(f"Formato: V-03=\"motivo\" ({x})", f"Format: V-03=\"reason\" ({x})"))
            d[k.strip()] = v.strip()
        return d
    na, no = pares(a.na), pares(a.no)
    def marca(m):
        i, txt = m.group(1), m.group(2)
        if i in no: return f"- [!] {i} {txt} — **no cumple:** {no[i]}"
        if i in na: return f"- [x] {i} {txt} — N/A: {na[i]}"
        return f"- [x] {i} {txt}"
    t = re.sub(r"(?m)^- \[[ x!]\] (V-\d+) (.*?)(?: — (?:N/A: .*|\*\*no cumple:\*\* .*))?$", marca, t)
    t = re.sub(r'(?m)^confirmada_por:.*$', f'confirmada_por: "{a.por}"', t, count=1)
    t = re.sub(r"(?m)^estado:.*$", f"estado: {'con-incumplimientos' if no else 'confirmada'}", t, count=1)
    t = t.rstrip("\n") + T(f"\n\nConfirmada por {a.por} el {a.fecha or datetime.date.today().isoformat()}.\n", f"\n\nConfirmed by {a.por} on {a.fecha or datetime.date.today().isoformat()}.\n")
    E.escribir_atomico(p, t)
    print(T(f"Lista {os.path.relpath(p, a.proyecto)} confirmada por {a.por}" + (f"; no cumple: {', '.join(no)}" if no else ""),
            f"Checklist {os.path.relpath(p, a.proyecto)} confirmed by {a.por}" + (f"; not met: {', '.join(no)}" if no else "")))

def proxima_puerta(e):
    """Puerta que corresponde según el estado (para informes y para '¿cómo venimos?')."""
    fase, proc = e.get("fase"), e.get("proceso_actual")
    if e.get("excepcion_abierta") and (fase, proc) == ("entrega", "SB"): return "autorizar-plan-excepcion"
    if fase == "pre-proyecto": return "autorizar-inicio"
    if fase == "inicio": return "autorizar-etapa" if e.get("proyecto_autorizado") else "autorizar-proyecto"
    if fase == "entrega": return "autorizar-etapa"
    if fase == "cierre": return "autorizar-cierre"
    return None

def estado_puertas(proyecto, e):
    """Insumo para informes (highlight, fin de etapa, tablero, '¿cómo venimos?'): puertas registradas con su verificación,
    condiciones abiertas y preparación de la próxima puerta."""
    regs = []
    for p in e.get("puertas", []):
        v = p.get("verificacion") or {}
        regs.append({"tipo": p["tipo"], "fecha": p.get("fecha"), "decision": p.get("decision"), "por": p.get("por"), "etapa": p.get("etapa"),
                     "condiciones": p.get("condiciones", ""), "condiciones_cumplidas": p.get("condiciones_cumplidas", ""),
                     "observaciones": v.get("observaciones", []), "lista": v.get("lista", ""), "confirmada_por": v.get("confirmada_por", ""),
                     "forzada": bool(p.get("forzada")), "decision_id": p.get("decision_id", "")})
    prox = proxima_puerta(e); prep = None
    if prox:
        hs, li = evaluar_detalle(proyecto, e, prox)
        sel = lambda sev: [h["mensaje"] for h in hs if h["severidad"] == sev]
        prep = {"puerta": prox, "bloqueos": sel("bloqueo"), "condiciones": sel("condicion"), "avisos": sel("aviso"),
                "hallazgos": hs, "lista": (li or {}).get("ruta", "")}
    return {"puertas": regs, "cierre_prematuro": E.cierre_prematuro(e), "condiciones_abiertas": [r for r in regs if r["decision"] in ("condicionado", "aprobado") and r["condiciones"] and not r["condiciones_cumplidas"]],
            "forzadas": [r for r in regs if r["forzada"]], "proxima": prep}

def markdown_estado(d, idioma="es"):
    tt = lambda es, en: E.t(idioma, es, en)
    L = [tt("### Puertas y verificación / Gates and verification", "### Gates and verification"), "",
         tt("| Puerta | Fecha | Decisión | Por | Condiciones (estado) | Observaciones de la verificación | Lista |", "| Gate | Date | Decision | By | Conditions (status) | Verification observations | Checklist |"), "|---|---|---|---|---|---|---|"]
    for r in d["puertas"]:
        cond = (r["condiciones"] + (tt(" (cumplidas ", " (met ") + r["condiciones_cumplidas"] + ")" if r["condiciones_cumplidas"] else tt(" (abiertas)", " (open)") if r["condiciones"] else "")) or "—"
        L.append(f"| {r['tipo']}{tt(' **(forzada)**', ' **(forced)**') if r['forzada'] else ''} | {r['fecha']} | {r['decision']} | {r['por']} | {cond} | {'; '.join(r['observaciones']) or '—'} | {r['lista'] or '—'} |")
    cp = d.get("cierre_prematuro") or {}
    if cp:
        L += ["", tt(f"**Cierre prematuro / Premature closure**: desde {cp.get('desde') or '—'}, decisión {cp.get('decision') or '—'} del {cp.get('fecha') or '—'}"
                     + (f", excepción {cp['excepcion']}" if cp.get("excepcion") else "") + (f": {cp['motivo']}" if cp.get("motivo") else "") + ".",
                     f"**Premature closure**: from {cp.get('desde') or '—'}, decision {cp.get('decision') or '—'} of {cp.get('fecha') or '—'}"
                     + (f", exception {cp['excepcion']}" if cp.get("excepcion") else "") + (f": {cp['motivo']}" if cp.get("motivo") else "") + ".")]
        pe = cp.get("plan_excepcion") if isinstance(cp.get("plan_excepcion"), dict) else {}
        if pe:
            L.append(tt(f"Plan de excepción del cierre: {pe.get('artefacto') or '—'} ({pe.get('decision') or '—'}, {pe.get('fecha') or '—'}), estado {pe.get('estado') or '—'}.",
                        f"Closure exception plan: {pe.get('artefacto') or '—'} ({pe.get('decision') or '—'}, {pe.get('fecha') or '—'}), status {pe.get('estado') or '—'}."))
    p = d.get("proxima")
    if p:
        L += ["", tt(f"**Próxima puerta / Next gate: {p['puerta']}** — {len(p['bloqueos'])} bloqueo(s), {len(p['condiciones'])} condición(es), {len(p['avisos'])} aviso(s).",
                     f"**Next gate: {p['puerta']}** — {len(p['bloqueos'])} blocker(s), {len(p['condiciones'])} condition(s), {len(p['avisos'])} warning(s).")]
        hs = p.get("hallazgos") or [{"severidad": sev, "id": "", "mensaje": m} for sev, k in (("bloqueo", "bloqueos"), ("condicion", "condiciones"), ("aviso", "avisos")) for m in p[k]]
        for sev, etiqueta in (("bloqueo", tt("bloqueo", "blocker")), ("condicion", tt("condición", "condition")), ("aviso", tt("aviso", "warning"))):   # mismos códigos que puertas.py verificar
            L += [f"- {etiqueta}: {(h['id'] + ' ') if h['id'] else ''}{h['mensaje']}" for h in [h for h in hs if h["severidad"] == sev][:8]]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verificar"); v.add_argument("tipo", choices=list(LISTAS)); v.add_argument("--json", action="store_true")
    l = sub.add_parser("lista"); l.add_argument("tipo", choices=list(LISTAS)); l.add_argument("--fecha")
    c = sub.add_parser("confirmar"); c.add_argument("tipo", choices=list(LISTAS)); c.add_argument("--por", required=True)
    c.add_argument("--na", action="append"); c.add_argument("--no", action="append"); c.add_argument("--fecha")
    es = sub.add_parser("estado", help="puertas registradas, condiciones abiertas y preparación de la próxima (insumo de informes)")
    es.add_argument("--json", action="store_true"); es.add_argument("--markdown", action="store_true")
    pb = sub.add_parser("preparacion-bmad"); pb.add_argument("--resultado", required=True, choices=["PASS", "CONCERNS", "FAIL"])
    pb.add_argument("--por", required=True); pb.add_argument("--fecha"); pb.add_argument("--nota", default="")
    a = ap.parse_args()
    if a.cmd in ("verificar", "estado"): return ejecutar(a)
    with E.bloqueo(a.proyecto):          # lista, confirmar y preparacion-bmad reescriben archivos de gobierno
        ejecutar(a)

def ejecutar(a):
    e = E.cargar_estado(a.proyecto)
    _idioma(e)
    if a.cmd == "verificar":
        hs, li = evaluar_detalle(a.proyecto, e, a.tipo)
        sel = lambda sev: [h["mensaje"] for h in hs if h["severidad"] == sev]
        bl, co, av = sel("bloqueo"), sel("condicion"), sel("aviso")
        if a.json: print(json.dumps({"puerta": a.tipo, "bloqueos": bl, "condiciones": co, "avisos": av, "lista": li, "hallazgos": hs}, ensure_ascii=False, indent=2)); return
        print(T(f"Puerta {a.tipo}: {len(bl)} bloqueo(s) · {len(co)} condición(es) · {len(av)} aviso(s)", f"Gate {a.tipo}: {len(bl)} blocker(s) · {len(co)} condition(s) · {len(av)} warning(s)"))
        for sev, etiqueta in (("bloqueo", T("BLOQUEO", "BLOCKER")), ("condicion", T("condición", "condition")), ("aviso", T("aviso", "warning"))):
            for h in hs:
                if h["severidad"] == sev: print(f"  {etiqueta:9s} {h['id']} {h['mensaje']}")
        print(T("  → aprobado posible", "  → 'aprobado' possible") if not bl else T("  → 'aprobado' no se registra: corregir, o decisión 'condicionado' (o --forzar) de la junta",
                                                                                   "  → 'aprobado' is not recorded: fix them, or a 'condicionado' decision (or --forzar) by the board"))
    elif a.cmd == "estado":
        d = estado_puertas(a.proyecto, e)
        if a.json: print(json.dumps(d, ensure_ascii=False, indent=2))
        else: print(markdown_estado(d, e.get("idioma", "es")))
    elif a.cmd == "lista": crear_lista(a, e)
    elif a.cmd == "confirmar": confirmar(a, e)
    elif a.cmd == "preparacion-bmad":
        e.setdefault("integraciones", {}).setdefault("bmad", {})["preparacion"] = {
            "resultado": a.resultado, "fecha": a.fecha or datetime.date.today().isoformat(), "por": a.por, "nota": a.nota,
            "registrado": datetime.datetime.now().isoformat(timespec="seconds")}
        e["actualizado"] = datetime.date.today().isoformat(); e["version_estado"] = e.get("version_estado", 0) + 1
        E.escribir_json(os.path.join(a.proyecto, "estado.json"), e)
        E.anotar_decision(a.proyecto, f"gate de preparación de BMAD: {a.resultado}" + (f" — {a.nota}" if a.nota else ""), a.por, nivel="gestor",
                          contexto=f"{e['fase']}/{e['proceso_actual']}", notas="bmad-sprint-planning readiness", fecha=a.fecha)
        print(T(f"Preparación BMAD registrada: {a.resultado}", f"BMAD readiness recorded: {a.resultado}"))

if __name__ == "__main__":
    main()
