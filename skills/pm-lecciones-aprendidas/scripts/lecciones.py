#!/usr/bin/env python3
"""Lecciones aprendidas: ciclo en el proyecto y búsqueda entre proyectos · Lessons learned: in-project cycle and cross-project search.

PRINCE2 «aprender de la experiencia» (pm-knowledge: prince2-principios-personas-procesos.md §2.2, §5.1 actividad 2, §5.6
actividades 1 y 5, §5.7 actividad 4; prince2-practicas-riesgo-issues-progreso-productos.md §4.b P-14/P-15, §4.c.7 y §4.d,
registro e informe de lecciones). PMBOK 8: gestionar el conocimiento del proyecto (pmbok8-dominios-procesos-adaptacion.md
§2.1.b.6) y retrospectivas (pmbok8-artefactos-tecnicas-anexos.md §3.13).

Ciclo de una lección en lecciones.csv (las escrituras pasan por registro.py y llevan --por, la persona que decidió):
  registrada (identificada: registro.py, retrospectiva con pm-reuniones/extraccion.py --tipo retrospectiva o incorporar)
  → revisada (clasificar: impacto alto|medio|bajo, recurrencia y aplicar_en ideacion;descubrimiento;planificacion;seguimiento)
  → accionada-proyecto | accionada-organizacion (accionar: accion = ids o artefacto donde vive la acción; verificar_en)
  → verificada (verificar --resultado efectiva) o vuelve a revisada (no-efectiva) · descartada con motivo (descartar).
Criterio de impacto (guía §12): alto = afectó o puede afectar una tolerancia de etapa o de proyecto (tiempo, costo, alcance,
calidad), un beneficio o un riesgo alto, o bloqueó una puerta; medio = consumió margen o retrabajo sin salir de tolerancia;
bajo = efecto local, sin efecto medible en el plan.
Controles (sanidad.py): REG-11 lección de impacto alto sin acción ni decisión; REG-12 lección accionada sin verificar su
efecto (verificar_en vencida, o impacto alto sin verificar_en). puertas.py: E-11 en autorizar-etapa.

Uso / Usage:
  lecciones.py listar --proyecto G [--para ideacion|descubrimiento|planificacion|seguimiento] [--estado E] [--corte F] [--max 10] [--json]
  lecciones.py clasificar --proyecto G L-### --impacto alto|medio|bajo --aplicar-en planificacion,seguimiento [--recurrencia alta|media|baja]
                [--prioridad alta|media|baja] --por "Gestor: Nombre" [--fecha F]
  lecciones.py accionar --proyecto G L-### --accion "A-###; plan-etapa-3" [--destino proyecto|organizacion] [--verificar-en F] --por … [--fecha F]
  lecciones.py verificar --proyecto G L-### --resultado efectiva|no-efectiva --evidencia "…" --por … [--fecha F]
  lecciones.py descartar --proyecto G L-### --motivo "…" --por … [--fecha F]
  lecciones.py informe --proyecto G [--etapa N] [--corte F] [--salida RUTA|-] [--exportar INDICE.csv --por …] [--json]
  lecciones.py buscar (--en DIR … | --indice CSV …) [--texto "integración agenda"] [--categoria X] [--etiqueta X] [--para P]
                [--max 10] [--json] [--exportar INDICE.csv]
  lecciones.py incorporar --proyecto ./gestion (--en DIR … | --indice CSV …) --ids ref,ref [--responsable ".."]
                [--confirmar --por "Gestor: Nombre"]
listar: lecciones del proyecto (sin las descartadas, salvo --estado), por impacto (alto primero), recurrencia, estado e id,
  con lo pendiente de cada una (sin clasificar, sin acción, verificar el …, verificación vencida, verificada); --para deja
  las que aplican a ese proceso (columna aplicar_en). Solo lectura.
informe: informe de lecciones (PRINCE2 lessons report, §4.d; límite de etapa §5.6 y cierre §5.7) desde lecciones.csv, en
  borrador: resumen por impacto, estado y proceso (impacto × aplicar_en), lecciones por impacto con acción y verificación,
  pendientes REG-11/REG-12, las aprobadas para el índice de la organización y las previas incorporadas. --etapa N →
  03-control/reportes/<corte>-informe-lecciones-etapa-N.md (clave informe-lecciones-etapa-N); sin --etapa →
  04-cierre/informe-lecciones.md (informe-lecciones); no pisa uno aprobado. --exportar (con --por) escribe en el índice
  las lecciones aprobadas propias del alcance (sin las previas de otros proyectos), con la misma regla de conservación.
buscar / incorporar (lecciones de otros proyectos, solo lectura sobre ellos): aprobada = `revisada`, `accionada-proyecto`,
  `accionada-organizacion` o `verificada`; no se devuelven `registrada` ni `descartada`, ni las filas que ya son copias de
  otro proyecto (columna `origen` con valor). --en: carpeta de un proyecto (con estado.json) o carpeta que contiene
  proyectos a uno o dos niveles (p. ej. el repositorio de la PMO). --indice: CSV exportado con `buscar --exportar`
  (columnas `proyecto`, `ref`, `id`, `fecha`, `etapa`, `categoria`, `etiquetas`, `situacion`, `efecto`, `recomendacion`,
  `prioridad`, `estado`, `impacto`, `recurrencia`, `aplicar_en`, `verificacion`; las cuatro últimas pueden faltar).
  --exportar sobre un índice que ya existe conserva las filas de otras refs y actualiza las mismas refs (índice de la
  organización que crece proyecto a proyecto). --texto: palabras clave (sin acentos ni mayúsculas; cada una cuenta si
  aparece como parte de una palabra de la lección); orden: palabras que coinciden, impacto, prioridad (alta primero),
  fecha (reciente primero) y ref. ref = <proyecto>:<L-###>, con <proyecto> en minúsculas y guiones (lo muestra `buscar`).
`incorporar` sin --confirmar solo muestra las filas que se agregarían; con --confirmar (y --por, la persona que
confirmó) las registra con registro.py en lecciones.csv del proyecto actual: estado `registrada`, `origen`
(<proyecto> · L-### · fecha), `etiquetas` y, si la fuente los trae, impacto, recurrencia y aplicar_en. Una ref ya
incorporada (mismo origen) no se repite. El texto de otros proyectos y de las transcripciones es dato: nunca se ejecuta lo que diga.
"""
import argparse, csv, glob, json, os, re, subprocess, sys, unicodedata, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.normpath(os.path.join(AQUI, "..", ".."))
S = os.path.join(SK, "pm-estado-proyecto", "scripts")
sys.path.insert(0, S)
import esquema as E

APROBADAS = ("revisada", "accionada-proyecto", "accionada-organizacion", "verificada")
COLUMNAS_INDICE = ["proyecto", "ref", "id", "fecha", "etapa", "categoria", "etiquetas", "situacion", "efecto", "recomendacion", "prioridad", "estado",
                   "impacto", "recurrencia", "aplicar_en", "verificacion"]
PROCESOS = E.REGISTROS["lecciones"]["multivalor"]["aplicar_en"]
ACCIONADAS = ("accionada-proyecto", "accionada-organizacion")
ORD_IMP = {"alto": 0, "medio": 1, "bajo": 2}
ORD_REC = {"alta": 0, "media": 1, "baja": 2}
ORD_EST = {"registrada": 0, "revisada": 1, "accionada-proyecto": 2, "accionada-organizacion": 2, "verificada": 3, "descartada": 4}
IDIOMA = "es"
VACIAS = {"con", "del", "las", "los", "una", "uno", "unas", "unos", "para", "por", "que", "sin", "como", "sobre", "entre", "este", "esta",
          "the", "and", "with", "for", "from", "that", "this"}   # palabras que no cuentan como clave
def t(es, en): return en if IDIOMA == "en" else es

def norm(x):
    x = unicodedata.normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", x).strip()

def slug(x):
    return re.sub(r"[^a-z0-9]+", "-", norm(x)).strip("-")[:40] or "proyecto"

def linea(x, n):
    x = re.sub(r"[\x00-\x1f\x7f]+", " ", str(x or "")).strip()
    return x if len(x) <= n else x[:n - 1].rstrip() + "…"

def proyectos(dirs):
    """Carpetas de proyecto (con estado.json) bajo cada DIR, a ≤ 2 niveles, sin duplicados."""
    out = []
    for d in dirs:
        if not os.path.isdir(d): sys.exit(t(f"No existe la carpeta {d}.", f"Folder not found: {d}."))
        for c in [os.path.join(d, "estado.json")] + sorted(glob.glob(os.path.join(d, "*", "estado.json")) + glob.glob(os.path.join(d, "*", "*", "estado.json"))):
            p = os.path.realpath(os.path.dirname(c))
            if os.path.exists(c) and p not in out: out.append(p)
    return out

def leer_lecciones(en=None, indice=None):
    """Lecciones aprobadas de las fuentes, como dicts con `proyecto` y `ref`. (filas, omitidas: {motivo: n})."""
    filas, omit = [], {"no_aprobadas": 0, "copias": 0}
    for p in proyectos(en or []):
        try: nombre = json.load(open(os.path.join(p, "estado.json"), encoding="utf-8")).get("proyecto") or os.path.basename(p)
        except (OSError, ValueError): continue
        ruta = E.ruta_registro(p, "lecciones")
        if not os.path.exists(ruta): continue
        for f in E.leer_csv(ruta)[1]:
            if f.get("origen"): omit["copias"] += 1; continue
            if f.get("estado") not in APROBADAS: omit["no_aprobadas"] += 1; continue
            filas.append({**{c: f.get(c, "") for c in COLUMNAS_INDICE if c not in ("proyecto", "ref")}, "proyecto": nombre, "ref": f"{slug(nombre)}:{f.get('id', '')}"})
    for ix in indice or []:
        if not os.path.isfile(ix): sys.exit(t(f"No existe el índice {ix}.", f"Index not found: {ix}."))
        with open(ix, newline="", encoding="utf-8") as fh:
            rd = csv.DictReader(fh)
            faltan = [c for c in ("proyecto", "id", "recomendacion", "estado") if c not in (rd.fieldnames or [])]
            if faltan: sys.exit(t(f"{ix}: faltan columnas {', '.join(faltan)} (se espera el formato de 'buscar --exportar').", f"{ix}: missing columns {', '.join(faltan)}."))
            for f in rd:
                if f.get("estado") not in APROBADAS: omit["no_aprobadas"] += 1; continue
                filas.append({**{c: f.get(c, "") for c in COLUMNAS_INDICE}, "ref": f.get("ref") or f"{slug(f.get('proyecto'))}:{f.get('id', '')}"})
    vistos, unicas = set(), []
    for f in filas:
        if f["ref"] in vistos: continue
        vistos.add(f["ref"]); unicas.append(f)
    return unicas, omit

def procesos_de(f):
    """Procesos de aplicar_en (ideacion, descubrimiento, planificacion, seguimiento) de una fila."""
    return [x.strip() for x in re.split(r"[;,]", f.get("aplicar_en") or "") if x.strip()]

def filtrar(filas, texto=None, categoria=None, etiqueta=None, para=None):
    terminos = [w for w in norm(texto).split() if len(w) >= 3 and w not in VACIAS] if texto else []
    out = []
    for f in filas:
        if categoria and norm(f.get("categoria")) != norm(categoria): continue
        if para and para not in procesos_de(f): continue
        etiquetas = [norm(x) for x in re.split(r"[;,]", f.get("etiquetas") or "") if x.strip()]
        if etiqueta and norm(etiqueta) not in etiquetas: continue
        cuerpo = norm(" ".join(f.get(c, "") for c in ("categoria", "etiquetas", "situacion", "efecto", "recomendacion")))
        coinc = [w for w in terminos if w in cuerpo]
        if terminos and not coinc: continue
        out.append({**f, "coincide": coinc})
    prio = {"alta": 0, "media": 1, "baja": 2}
    out.sort(key=lambda f: f["ref"])
    out.sort(key=lambda f: f.get("fecha", ""), reverse=True)
    out.sort(key=lambda f: (-len(f["coincide"]), ORD_IMP.get(f.get("impacto"), 3), prio.get(f.get("prioridad"), 3)))
    return out

def texto_resultado(sel, total, omit, maximo):
    if not sel:
        return t(f"Sin lecciones aprobadas que coincidan ({total} aprobadas revisadas; omitidas: {omit['no_aprobadas']} sin aprobar, {omit['copias']} copias de otros proyectos).",
                 f"No approved lessons match ({total} approved checked; skipped: {omit['no_aprobadas']} not approved, {omit['copias']} copies from other projects).")
    x = [t(f"Lecciones aprobadas que coinciden: {len(sel)} de {total} (omitidas: {omit['no_aprobadas']} sin aprobar, {omit['copias']} copias).",
           f"Matching approved lessons: {len(sel)} of {total} (skipped: {omit['no_aprobadas']} not approved, {omit['copias']} copies).")]
    for f in sel[:maximo]:
        x.append(f"- {f['ref']} · {linea(f['proyecto'], 50)} · {f.get('fecha', '')} · {f.get('categoria') or '—'}" + (f" · #{f['etiquetas']}" if f.get("etiquetas") else "")
                 + (f" · {f['prioridad']}" if f.get("prioridad") else "") + f" · {f.get('estado')}"
                 + (t(" · impacto ", " · impact ") + f["impacto"] if f.get("impacto") else "") + (t(" · aplicar en ", " · apply in ") + f["aplicar_en"] if f.get("aplicar_en") else "")
                 + (t(" · coincide: ", " · matches: ") + ", ".join(f["coincide"]) if f["coincide"] else ""))
        x.append(t("    situación: ", "    situation: ") + linea(f.get("situacion"), 140))
        x.append(t("    recomendación: ", "    recommendation: ") + linea(f.get("recomendacion"), 180))
    if len(sel) > maximo: x.append(t(f"… y {len(sel) - maximo} más (--max 0 o --json)", f"… and {len(sel) - maximo} more (--max 0 or --json)"))
    x.append(t("Para proponerlas como lecciones previas: lecciones.py incorporar --proyecto <dir> … --ids <ref,ref> (vista previa; registra solo con --confirmar --por).",
               "To propose them as previous lessons: lecciones.py incorporar --proyecto <dir> … --ids <ref,ref> (preview; records only with --confirmar --por)."))
    return "\n".join(x)

# ------------------------------------------------------------------ ciclo de las lecciones del proyecto
def pendiente(f):
    """Abierta y sin acción: registrada o revisada, sin `accion` (ni acción ni decisión de descartarla)."""
    return f.get("estado") in ("registrada", "revisada") and not (f.get("accion") or "").strip()

def controles(filas, corte, idioma="es"):
    """REG-11 y REG-12 para sanidad.py y el radar: [(severidad, código, mensaje, arreglo)]."""
    tt = lambda es, en: en if idioma == "en" else es
    out = []
    for f in filas:
        i, est, imp, ap = f.get("id", ""), f.get("estado", ""), f.get("impacto", ""), "; ".join(procesos_de(f))
        if imp == "alto" and pendiente(f):
            out.append(("AVISO", "REG-11", tt(f"Lección {i} de impacto alto sin acción ni decisión ({est}" + (f"; aplicar en {ap}" if ap else "") + ").",
                                              f"High-impact lesson {i} with no action or decision ({est}" + (f"; apply in {ap}" if ap else "") + ")."),
                        tt(f"lecciones.py accionar {i} --accion <A-###|R-###|plan-etapa-n> --verificar-en AAAA-MM-DD --por … (o descartar {i} --motivo … --por …).",
                           f"lecciones.py accionar {i} --accion … --verificar-en YYYY-MM-DD --por … (or descartar {i} --motivo … --por …).")))
        if est in ACCIONADAS:
            ve = (f.get("verificar_en") or "").strip()
            if ve and ve < corte:
                out.append(("AVISO", "REG-12", tt(f"Lección {i} accionada sin verificar su efecto (verificar_en {ve}; acción: {linea(f.get('accion'), 60) or '—'}).",
                                                  f"Lesson {i} actioned without checking its effect (verificar_en {ve}; action: {linea(f.get('accion'), 60) or '—'})."),
                            tt(f"lecciones.py verificar {i} --resultado efectiva|no-efectiva --evidencia … --por … (o reprogramar verificar_en con registro.py).",
                               f"lecciones.py verificar {i} --resultado efectiva|no-efectiva --evidencia … --por … (or reschedule verificar_en).")))
            elif not ve and imp == "alto":
                out.append(("AVISO", "REG-12", tt(f"Lección {i} de impacto alto accionada sin fecha para verificar su efecto (verificar_en).",
                                                  f"High-impact lesson {i} actioned with no date to check its effect (verificar_en)."),
                            tt(f"registro.py actualizar lecciones {i} --campo verificar_en=AAAA-MM-DD (cuándo se comprueba que la acción funcionó).",
                               f"registro.py actualizar lecciones {i} --campo verificar_en=YYYY-MM-DD.")))
    return out

def que_falta(f, corte):
    est = f.get("estado")
    if est == "descartada": return t("descartada", "discarded")
    if est == "verificada": return t("verificada", "verified") + (f": {linea(f.get('verificacion'), 70)}" if f.get("verificacion") else "")
    if est in ACCIONADAS:
        ve = f.get("verificar_en") or ""
        if not ve: return t("sin fecha de verificación", "no verification date")
        return (t("verificación vencida ", "verification overdue ") if ve < corte else t("verificar el ", "verify on ")) + ve
    if not f.get("impacto") or not procesos_de(f): return t("sin clasificar", "not classified")
    return t("sin acción", "no action") if pendiente(f) else t("acción propuesta: ", "proposed action: ") + linea(f.get("accion"), 40)

def listar(proyecto, para=None, estado=None, corte=None):
    ruta = E.ruta_registro(proyecto, "lecciones")
    filas = E.leer_csv(ruta)[1] if os.path.exists(ruta) else []
    corte = corte or datetime.date.today().isoformat()
    sel, sin_clasificar = [], []
    for f in filas:
        if estado and f.get("estado") != estado: continue
        if not estado and f.get("estado") == "descartada": continue
        if f.get("estado") in ("registrada", "revisada") and (not f.get("impacto") or not procesos_de(f)): sin_clasificar.append(f.get("id"))
        if para and para not in procesos_de(f): continue
        sel.append({**f, "pendiente": que_falta(f, corte)})
    sel.sort(key=lambda f: (ORD_IMP.get(f.get("impacto"), 3), ORD_REC.get(f.get("recurrencia"), 3), ORD_EST.get(f.get("estado"), 5), f.get("id", "")))
    return sel, sin_clasificar, len(filas)

def texto_listar(sel, sin_clasificar, total, para, maximo):
    titulo = t(f"Lecciones que aplican a {para}", f"Lessons that apply to {para}") if para else t("Lecciones del proyecto", "Project lessons")
    x = [titulo + f": {len(sel)} " + t(f"de {total}", f"of {total}") + t(" · por impacto (alto primero), recurrencia y estado", " · by impact (high first), recurrence and status")]
    for f in sel[:maximo]:
        x.append(f"- {f.get('id')} · {f.get('impacto') or t('sin impacto', 'no impact')}" + (t(" · recurrencia ", " · recurrence ") + f["recurrencia"] if f.get("recurrencia") else "")
                 + f" · {f.get('estado')}" + (f" · {linea(f.get('responsable_seguimiento'), 30)}" if f.get("responsable_seguimiento") else "")
                 + (t(" · acción ", " · action ") + linea(f.get("accion"), 50) if f.get("accion") else "") + f" · {f['pendiente']}")
        x.append(t("    recomendación: ", "    recommendation: ") + linea(f.get("recomendacion") or f.get("situacion"), 150)
                 + (t(" · aplicar en ", " · apply in ") + "; ".join(procesos_de(f)) if not para and procesos_de(f) else ""))
    if len(sel) > maximo: x.append(t(f"… y {len(sel) - maximo} más (--max 0 o --json)", f"… and {len(sel) - maximo} more (--max 0 or --json)"))
    if sin_clasificar:
        x.append(t("Sin clasificar (impacto o aplicar_en vacíos): ", "Not classified (impact or aplicar_en empty): ") + ", ".join(sin_clasificar[:12]) + (" …" if len(sin_clasificar) > 12 else "")
                 + t(" → lecciones.py clasificar", " → lecciones.py clasificar"))
    return "\n".join(x)

def fila_de(proyecto, lid):
    ruta = E.ruta_registro(proyecto, "lecciones")
    for f in (E.leer_csv(ruta)[1] if os.path.exists(ruta) else []):
        if f.get("id") == lid: return f
    sys.exit(t(f"No existe la lección {lid} en lecciones.csv.", f"Lesson {lid} not found in lecciones.csv."))

def fecha_ok(x, nombre):
    try: return datetime.date.fromisoformat(x).isoformat()
    except (TypeError, ValueError): sys.exit(t(f"{nombre} inválida: {x} (AAAA-MM-DD).", f"Invalid {nombre}: {x} (YYYY-MM-DD)."))

def actualizar(proyecto, lid, campos):
    cmd = [sys.executable, os.path.join(S, "registro.py"), "--proyecto", proyecto, "actualizar", "lecciones", lid] + [x for k, v in campos.items() for x in ("--campo", f"{k}={v}")]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0: sys.exit(t(f"registro.py rechazó la actualización de {lid}: ", f"registro.py rejected {lid}: ") + (r.stderr or r.stdout).strip()[-400:])

def nota(f, texto): return ((f.get("notas") or "").strip() + " · " if (f.get("notas") or "").strip() else "") + texto

def cmd_ciclo(a):
    f = fila_de(a.proyecto, a.id); fecha = fecha_ok(a.fecha, "--fecha") if a.fecha else datetime.date.today().isoformat()
    por = linea(a.por, 60); est = f.get("estado")
    if a.cmd == "clasificar":
        if est in ("verificada", "descartada"): sys.exit(t(f"{a.id} está {est}: no se reclasifica.", f"{a.id} is {est}: not reclassified."))
        campos = {"impacto": a.impacto, "aplicar_en": a.aplicar_en}
        if a.recurrencia: campos["recurrencia"] = a.recurrencia
        if a.prioridad: campos["prioridad"] = a.prioridad
        if est == "registrada": campos["estado"] = "revisada"
        campos["notas"] = nota(f, t(f"clasificada {fecha} por {por}", f"classified {fecha} by {por}"))
        actualizar(a.proyecto, a.id, campos)
        g = fila_de(a.proyecto, a.id)
        print(t(f"{a.id} clasificada: impacto {g['impacto']}" + (f", recurrencia {g['recurrencia']}" if g.get("recurrencia") else "") + f", aplicar en {g['aplicar_en']} · estado {g['estado']}.",
                f"{a.id} classified: impact {g['impacto']}" + (f", recurrence {g['recurrencia']}" if g.get("recurrencia") else "") + f", apply in {g['aplicar_en']} · status {g['estado']}."))
        if g.get("impacto") == "alto" and pendiente(g):
            print(t(f"Impacto alto: la sanidad la marca (REG-11) hasta que tenga acción (lecciones.py accionar {a.id} …) o se descarte con motivo.",
                    f"High impact: sanidad flags it (REG-11) until it has an action (lecciones.py accionar {a.id} …) or is discarded."))
        return
    if a.cmd == "accionar":
        if est not in ("registrada", "revisada") + ACCIONADAS: sys.exit(t(f"{a.id} está {est}: no se acciona.", f"{a.id} is {est}: cannot be actioned."))
        if not f.get("impacto") or not procesos_de(f): sys.exit(t(f"Clasificar primero {a.id} (lecciones.py clasificar {a.id} --impacto … --aplicar-en … --por …).", f"Classify {a.id} first."))
        ve = fecha_ok(a.verificar_en, "--verificar-en") if a.verificar_en else ""
        if a.destino == "proyecto" and not ve: sys.exit(t("--verificar-en AAAA-MM-DD es obligatorio para una acción en el proyecto (cuándo se comprueba su efecto).", "--verificar-en is required for a project action."))
        if ve and ve < fecha: sys.exit(t(f"--verificar-en {ve} es anterior a la fecha {fecha}.", f"--verificar-en {ve} is before {fecha}."))
        campos = {"accion": linea(a.accion, 200), "estado": f"accionada-{a.destino}", "notas": nota(f, t(f"accionada {fecha} por {por}", f"actioned {fecha} by {por}"))}
        if ve: campos["verificar_en"] = ve
        actualizar(a.proyecto, a.id, campos)
        print(t(f"{a.id} accionada-{a.destino}: acción {campos['accion']}" + (f" · verificar el efecto el {ve}" if ve else "") + ".",
                f"{a.id} accionada-{a.destino}: action {campos['accion']}" + (f" · check its effect on {ve}" if ve else "") + "."))
        return
    if a.cmd == "verificar":
        if est not in ACCIONADAS: sys.exit(t(f"{a.id} está {est}: solo se verifica una lección accionada.", f"{a.id} is {est}: only actioned lessons are verified."))
        txt = f"{fecha} · {a.resultado} · {linea(a.evidencia, 220)} · {por}"
        if a.resultado == "efectiva":
            campos = {"estado": "verificada", "verificacion": txt}
        else:   # la acción no tuvo efecto: vuelve a revisada, sin acción, con el antecedente en verificacion
            campos = {"estado": "revisada", "accion": "", "verificar_en": "", "verificacion": t(f"{txt} (acción anterior: {linea(f.get('accion'), 80)})", f"{txt} (previous action: {linea(f.get('accion'), 80)})")}
        actualizar(a.proyecto, a.id, campos)
        print(t(f"{a.id} {'verificada' if a.resultado == 'efectiva' else 'vuelve a revisada: la acción no tuvo efecto; definir otra (lecciones.py accionar)'} · {txt}",
                f"{a.id} {'verified' if a.resultado == 'efectiva' else 'back to revisada: the action had no effect; define another one'} · {txt}"))
        return
    # descartar
    if est in ("verificada", "descartada"): sys.exit(t(f"{a.id} está {est}.", f"{a.id} is {est}."))
    actualizar(a.proyecto, a.id, {"estado": "descartada", "notas": nota(f, t(f"descartada {fecha} por {por}: {linea(a.motivo, 160)}", f"discarded {fecha} by {por}: {linea(a.motivo, 160)}"))})
    print(t(f"{a.id} descartada (motivo: {linea(a.motivo, 160)}).", f"{a.id} discarded (reason: {linea(a.motivo, 160)})."))

def exportar_indice(ruta, sel):
    """Escribe el índice; si ya existe, conserva las filas de otras refs y actualiza las mismas refs. (conservadas, total)."""
    previas = []
    if os.path.isfile(ruta):
        with open(ruta, newline="", encoding="utf-8") as fh: previas = list(csv.DictReader(fh))
    nuevas = {f["ref"]: f for f in sel}
    filas, vistos = [], set()
    for f in previas:
        r = f.get("ref")
        if r in nuevas: filas.append(nuevas[r]); vistos.add(r)
        else: filas.append(f)
    filas += [f for f in sel if f["ref"] not in vistos]
    conservadas = len(previas) - len(vistos)
    E.escribir_csv(ruta, COLUMNAS_INDICE, [{c: f.get(c, "") for c in COLUMNAS_INDICE} for f in filas])
    return conservadas, len(filas)

def ruta_indice_ok(ra):
    if os.sep + os.path.join("03-control", "registros") + os.sep in ra or any(x in ra.split(os.sep) for x in ("_bmad", "_bmad-output", ".bmad-core")):
        sys.exit(t("El índice no se escribe en 03-control/registros/ ni en carpetas de BMAD.", "The index is not written into 03-control/registros/ or BMAD folders."))

# ------------------------------------------------------------------ informe de lecciones (PRINCE2 lessons report) desde el registro
def celda(x, n=160):
    return linea(x, n).replace("|", "\\|") or "—"

def datos_informe(proyecto, etapa=None, corte=None):
    """Lecciones del alcance (etapa o proyecto), totales por impacto, estado y proceso, pendientes y previas incorporadas."""
    ruta = E.ruta_registro(proyecto, "lecciones")
    filas = E.leer_csv(ruta)[1] if os.path.exists(ruta) else []
    propias = [f for f in filas if not (f.get("origen") or "").strip()]
    previas = [f for f in filas if (f.get("origen") or "").strip()]
    alc = [f for f in propias if etapa is None or str(f.get("etapa", "")).strip() == str(etapa)]
    vivas = [f for f in alc if f.get("estado") != "descartada"]
    vivas.sort(key=lambda f: (ORD_IMP.get(f.get("impacto"), 3), ORD_REC.get(f.get("recurrencia"), 3), ORD_EST.get(f.get("estado"), 5), f.get("id", "")))
    imp = {k: sum(1 for f in vivas if (f.get("impacto") or "") == k) for k in ("alto", "medio", "bajo", "")}
    est = {k: sum(1 for f in alc if f.get("estado") == k) for k in E.REGISTROS["lecciones"]["valores"]["estado"]}
    matriz = {i: {p: sum(1 for f in vivas if f.get("impacto") == i and p in procesos_de(f)) for p in PROCESOS} for i in ("alto", "medio", "bajo")}
    aciertos = sum(1 for f in vivas if norm(f.get("categoria")) == "acierto" or re.search(r"(^|· )funciono( ·|$)", norm(f.get("notas"))))
    pend = [(c, m) for _s, c, m, _a in controles(alc, corte, IDIOMA)]
    sin_cl = [f.get("id") for f in vivas if f.get("estado") in ("registrada", "revisada") and (not f.get("impacto") or not procesos_de(f))]
    org = [f for f in vivas if f.get("estado") in APROBADAS]
    return {"total": len(alc), "descartadas": est.get("descartada", 0), "por_impacto": {k or "sin_clasificar": v for k, v in imp.items()},
            "por_estado": est, "impacto_proceso": matriz, "aciertos": aciertos, "lecciones": vivas, "pendientes": pend, "sin_clasificar": sin_cl,
            "para_indice": org, "previas": previas}

def markdown_informe(e, d, alcance, corte):
    nom = e.get("proyecto") or "proyecto"
    titulo = t(f"Etapa {alcance}", f"Stage {alcance}") if alcance else t("Proyecto completo", "Whole project")
    pi = d["por_impacto"]; pe = d["por_estado"]
    acc = pe.get("accionada-proyecto", 0) + pe.get("accionada-organizacion", 0)
    L = ["---", "tipo: informe-lecciones", f"proyecto: \"{linea(nom, 80)}\"", f"alcance: \"{titulo}\"", f"fecha: \"{corte}\"",
         "fuente: 03-control/registros/lecciones.csv", "estado: borrador", "aprobado_por: \"\"", f"idioma: \"{IDIOMA}\"", "---", "",
         t(f"# Informe de lecciones · Lessons report — {linea(nom, 80)} — {titulo}", f"# Lessons report — {linea(nom, 80)} — {titulo}"), "",
         t(f"> Borrador generado desde `lecciones.csv` al {corte} (lecciones.py informe). Cada fila cita su L-### y la acción que la "
           "convirtió en cambio; aseguramiento confirma responsables y la junta lo revisa antes de aprobarlo (estado.py aprobar). "
           "Lo que no sale del registro (análisis por área, proveedores, desempeño excepcional) se completa con templates/informe-lecciones.md.",
           f"> Draft generated from `lecciones.csv` at {corte} (lecciones.py informe). Each row cites its L-### and the action that turned it "
           "into a change; assurance confirms owners and the board reviews it before approval."), "",
         t("## 1. Resumen", "## 1. Summary"), "",
         t(f"- Lecciones en el alcance: **{d['total']}** ({d['descartadas']} descartadas con motivo) · aciertos: {d['aciertos']}",
           f"- Lessons in scope: **{d['total']}** ({d['descartadas']} discarded with a reason) · what worked: {d['aciertos']}"),
         t(f"- Por impacto: alto {pi['alto']} · medio {pi['medio']} · bajo {pi['bajo']} · sin clasificar {pi['sin_clasificar']}",
           f"- By impact: high {pi['alto']} · medium {pi['medio']} · low {pi['bajo']} · not classified {pi['sin_clasificar']}"),
         t(f"- Ciclo: registradas {pe.get('registrada', 0)} · revisadas {pe.get('revisada', 0)} · accionadas {acc} · verificadas {pe.get('verificada', 0)}",
           f"- Cycle: registered {pe.get('registrada', 0)} · reviewed {pe.get('revisada', 0)} · actioned {acc} · verified {pe.get('verificada', 0)}"), "",
         "| " + t("Impacto", "Impact") + " | " + " | ".join(PROCESOS) + " |", "|---|" + "---:|" * len(PROCESOS)]
    for i in ("alto", "medio", "bajo"):
        L.append(f"| {i} | " + " | ".join(str(d["impacto_proceso"][i][p]) for p in PROCESOS) + " |")
    L += ["", t("*Una lección puede aplicar a más de un proceso (columna `aplicar_en`).*", "*A lesson may apply to more than one process (`aplicar_en`).*"), "",
          t("## 2. Lecciones por impacto", "## 2. Lessons by impact"), ""]
    if d["lecciones"]:
        L += ["| Id | " + t("Impacto · recurrencia", "Impact · recurrence") + " | " + t("Aplica en", "Apply in") + " | " + t("Situación", "Situation") + " | "
              + t("Recomendación", "Recommendation") + " | " + t("Acción", "Action") + " | " + t("Verificación", "Verification") + " | " + t("Estado", "Status") + " |",
              "|---|---|---|---|---|---|---|---|"]
        for f in d["lecciones"]:
            ver = f.get("verificacion") or (t("verificar el ", "verify on ") + f["verificar_en"] if f.get("verificar_en") else "")
            L.append(f"| {f.get('id')} | {(f.get('impacto') or t('sin clasificar', 'not classified')) + (' · ' + f['recurrencia'] if f.get('recurrencia') else '')} | "
                     f"{celda('; '.join(procesos_de(f)), 60)} | {celda(f.get('situacion'), 140)} | {celda(f.get('recomendacion'), 160)} | {celda(f.get('accion'), 60)} | "
                     f"{celda(ver, 120)} | {f.get('estado')} |")
    else:
        L.append(t("Sin lecciones registradas en el alcance: declararlo y revisar que el taller o la retrospectiva se hayan hecho.",
                   "No lessons in scope: state it and check that the workshop or retrospective took place."))
    L += ["", t("## 3. Pendientes al corte", "## 3. Open items at cut-off"), ""]
    if d["pendientes"] or d["sin_clasificar"]:
        L += [f"- {c}: {celda(m, 220)}" for c, m in d["pendientes"]]
        if d["sin_clasificar"]: L.append(t("- Sin clasificar (impacto o aplicar_en vacíos): ", "- Not classified: ") + ", ".join(d["sin_clasificar"]) + " → lecciones.py clasificar")
    else:
        L.append(t("Ninguno: cada lección de impacto alto tiene acción y cada acción vencida está verificada (REG-11 y REG-12 en cero).",
                   "None: every high-impact lesson has an action and every due action is verified (REG-11 and REG-12 at zero)."))
    L += ["", t("## 4. Para la organización (índice de lecciones)", "## 4. For the organization (lessons index)"), ""]
    if d["para_indice"]:
        L.append(t(f"Lecciones aprobadas que se comparten en el índice de la organización ({len(d['para_indice'])}); las consultan la ideación y el descubrimiento "
                   "de los proyectos siguientes (`lecciones.py buscar --indice <índice> --para ideacion|descubrimiento`):",
                   f"Approved lessons shared in the organization's index ({len(d['para_indice'])}); next projects query them in ideation and discovery:"))
        for f in d["para_indice"]:
            L.append(f"- {f.get('id')} ({f.get('impacto') or '—'}; {'; '.join(procesos_de(f)) or '—'}; {f.get('estado')}): {celda(f.get('recomendacion'), 180)}")
    else:
        L.append(t("Ninguna aprobada todavía (se comparten las revisadas, accionadas o verificadas).", "None approved yet."))
    if d["previas"]:
        L += ["", t("## 5. Lecciones previas incorporadas (de otros proyectos)", "## 5. Previous lessons incorporated (other projects)"), "",
              "| Id | " + t("Origen", "Source") + " | " + t("Acción", "Action") + " | " + t("Estado", "Status") + " |", "|---|---|---|---|"]
        for f in d["previas"]:
            L.append(f"| {f.get('id')} | {celda(f.get('origen'), 80)} | {celda(f.get('accion') or f.get('notas'), 100)} | {f.get('estado')} |")
    L += ["", t("## Revisión", "## Review"), "", t("- Aseguramiento (confirma responsables): [por confirmar]", "- Assurance (confirms owners): [TBC]"),
          t("- Junta (revisa y aprueba): [por confirmar]", "- Board (reviews and approves): [TBC]"), ""]
    return "\n".join(L)

def cmd_informe(a):
    e = E.cargar_estado(a.proyecto)
    corte = fecha_ok(a.corte, "--corte") if a.corte else datetime.date.today().isoformat()
    d = datos_informe(a.proyecto, a.etapa, corte)
    clave = f"informe-lecciones-etapa-{a.etapa}" if a.etapa else "informe-lecciones"
    rel = os.path.join("03-control", "reportes", f"{corte}-informe-lecciones-etapa-{a.etapa}.md") if a.etapa else os.path.join("04-cierre", "informe-lecciones.md")
    salida = a.salida or os.path.join(a.proyecto, rel)
    if salida != "-":
        art = (e.get("artefactos") or {}).get(clave) or {}
        if art.get("estado") == "aprobado" and os.path.normpath(os.path.join(a.proyecto, art.get("ruta", ""))) == os.path.normpath(salida):
            sys.exit(t(f"{clave} ya está aprobado en {art.get('ruta')}: no se pisa (usar --salida para una versión nueva).", f"{clave} is already approved: not overwritten (use --salida)."))
    exportadas = None
    if a.exportar:
        if not a.por: sys.exit(t("--exportar requiere --por \"Rol: Nombre\" (quién decidió compartir las lecciones con la organización).", "--exportar requires --por \"Role: Name\"."))
        ra = os.path.abspath(a.exportar); ruta_indice_ok(ra); os.makedirs(os.path.dirname(ra), exist_ok=True)
        nom = e.get("proyecto") or os.path.basename(os.path.abspath(a.proyecto))
        sel = [{**{c: f.get(c, "") for c in COLUMNAS_INDICE if c not in ("proyecto", "ref")}, "proyecto": nom, "ref": f"{slug(nom)}:{f.get('id', '')}"} for f in d["para_indice"]]
        conservadas, total_ix = exportar_indice(ra, sel)
        exportadas = {"indice": a.exportar, "lecciones": len(sel), "conservadas": conservadas, "total": total_ix, "por": linea(a.por, 60), "fecha": corte}
    md = markdown_informe(e, d, a.etapa, corte)
    if exportadas:
        md = md.rstrip("\n") + "\n" + t(f"- Exportado al índice de la organización: `{exportadas['indice']}` ({exportadas['lecciones']} lecciones; total del índice {exportadas['total']}) · {exportadas['fecha']} · {exportadas['por']}",
                                        f"- Exported to the organization's index: `{exportadas['indice']}` ({exportadas['lecciones']} lessons; index total {exportadas['total']}) · {exportadas['fecha']} · {exportadas['por']}") + "\n"
    if salida == "-":
        if not a.json: print(md)
    else:
        os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True); open(salida, "w", encoding="utf-8").write(md)
    if a.json:
        print(json.dumps({"alcance": f"etapa {a.etapa}" if a.etapa else "proyecto", "corte": corte, "clave": clave, "salida": salida,
                          **{k: v for k, v in d.items() if k not in ("lecciones", "para_indice", "previas")},
                          "lecciones": [{c: f.get(c, "") for c in ("id", "etapa", "categoria", "impacto", "recurrencia", "aplicar_en", "estado", "accion", "verificar_en", "verificacion", "recomendacion")} for f in d["lecciones"]],
                          "para_indice": [f.get("id") for f in d["para_indice"]], "previas": [f.get("id") for f in d["previas"]], "exportado": exportadas,
                          **({"markdown": md} if salida == "-" else {})}, ensure_ascii=False, indent=2))
        return
    if salida != "-":
        pi = d["por_impacto"]
        print(t(f"Informe de lecciones ({'etapa ' + str(a.etapa) if a.etapa else 'proyecto'}): {salida} · {d['total']} lecciones (alto {pi['alto']}, medio {pi['medio']}, bajo {pi['bajo']}) · "
                f"{len(d['pendientes'])} pendientes · {len(d['para_indice'])} para el índice.",
                f"Lessons report ({'stage ' + str(a.etapa) if a.etapa else 'project'}): {salida} · {d['total']} lessons (high {pi['alto']}, medium {pi['medio']}, low {pi['bajo']}) · "
                f"{len(d['pendientes'])} open · {len(d['para_indice'])} for the index."))
        if exportadas:
            print(t(f"Índice: {exportadas['indice']} ({exportadas['lecciones']} lecciones aprobadas" + (f"; se conservan {exportadas['conservadas']} de otras refs" if exportadas["conservadas"] else "") + f"; total {exportadas['total']}).",
                    f"Index: {exportadas['indice']} ({exportadas['lecciones']} approved lessons; total {exportadas['total']})."))
        print(t(f"Siguiente: estado.py artefacto {clave} --ruta {os.path.relpath(os.path.abspath(salida), os.path.abspath(a.proyecto))} --estado en-revision; tras la revisión de la junta, estado.py aprobar {clave} --por \"<rol: nombre>\".",
                f"Next: estado.py artefacto {clave} --ruta … --estado en-revision; after the board review, estado.py aprobar {clave} --por \"<role: name>\"."))


def main():
    global IDIOMA
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def fuentes(p):
        p.add_argument("--en", nargs="+", metavar="DIR", help="carpetas de proyectos (o que los contienen a ≤ 2 niveles)")
        p.add_argument("--indice", nargs="+", metavar="CSV", help="índices de lecciones exportados con 'buscar --exportar'")
    b = sub.add_parser("buscar", help="lecciones aprobadas de otros proyectos por palabras clave, categoría o etiqueta (solo lectura)"); fuentes(b)
    b.add_argument("--texto"); b.add_argument("--categoria"); b.add_argument("--etiqueta")
    b.add_argument("--max", type=int, default=10, help="lecciones en pantalla (defecto 10; 0 = todas)"); b.add_argument("--json", action="store_true")
    b.add_argument("--exportar", metavar="CSV", help="escribir las lecciones seleccionadas como índice (fuera de 03-control/registros/)")
    b.add_argument("--idioma", choices=["es", "en"], default="es")
    b.add_argument("--para", choices=PROCESOS, help="solo las lecciones que aplican a ese proceso (columna aplicar_en)")
    l = sub.add_parser("listar", help="lecciones del proyecto por impacto, con lo pendiente de cada una (solo lectura)")
    l.add_argument("--proyecto", required=True); l.add_argument("--para", choices=PROCESOS, help="proceso donde se usan: ideacion, descubrimiento, planificacion o seguimiento")
    l.add_argument("--estado", choices=E.REGISTROS["lecciones"]["valores"]["estado"]); l.add_argument("--corte", help="fecha de corte AAAA-MM-DD para vencimientos (defecto: hoy)")
    l.add_argument("--max", type=int, default=10, help="lecciones en pantalla (defecto 10; 0 = todas)"); l.add_argument("--json", action="store_true")
    def ciclo(nombre, ayuda):
        p_ = sub.add_parser(nombre, help=ayuda); p_.add_argument("id", help="L-###"); p_.add_argument("--proyecto", required=True)
        p_.add_argument("--por", required=True, help="quién decidió (Rol: Nombre)"); p_.add_argument("--fecha", help="AAAA-MM-DD (defecto: hoy)"); return p_
    c = ciclo("clasificar", "impacto, recurrencia y procesos donde aplica (registrada → revisada)")
    c.add_argument("--impacto", required=True, choices=["alto", "medio", "bajo"]); c.add_argument("--recurrencia", choices=["alta", "media", "baja"])
    c.add_argument("--aplicar-en", dest="aplicar_en", required=True, help="uno o más de: " + ", ".join(PROCESOS) + " (separados por coma)")
    c.add_argument("--prioridad", choices=["alta", "media", "baja"], help="urgencia de la acción (opcional)")
    ac = ciclo("accionar", "acción en el proyecto o la organización y fecha para verificar su efecto (→ accionada-…)")
    ac.add_argument("--accion", required=True, help="ids o artefacto donde vive la acción (A-###, R-###, historia, plan-etapa-n)")
    ac.add_argument("--destino", choices=["proyecto", "organizacion"], default="proyecto"); ac.add_argument("--verificar-en", dest="verificar_en", help="AAAA-MM-DD (obligatorio con destino proyecto)")
    v = ciclo("verificar", "¿la acción tuvo efecto? efectiva → verificada; no-efectiva → revisada")
    v.add_argument("--resultado", required=True, choices=["efectiva", "no-efectiva"]); v.add_argument("--evidencia", required=True, help="qué se observó, con ids")
    d = ciclo("descartar", "descartar con motivo (nunca se borra)"); d.add_argument("--motivo", required=True)
    inf = sub.add_parser("informe", help="informe de lecciones de la etapa o del proyecto desde lecciones.csv (borrador) y, con --exportar, índice de la organización")
    inf.add_argument("--proyecto", required=True); inf.add_argument("--etapa", help="número de etapa (defecto: proyecto completo, 04-cierre/informe-lecciones.md)")
    inf.add_argument("--corte", help="fecha del informe y de los vencimientos AAAA-MM-DD (defecto: hoy)"); inf.add_argument("--salida", help="ruta del .md o - para pantalla")
    inf.add_argument("--exportar", metavar="CSV", help="índice de lecciones de la organización (conserva las otras refs; requiere --por)")
    inf.add_argument("--por", help="quién decidió compartirlas (Rol: Nombre)"); inf.add_argument("--json", action="store_true")
    i = sub.add_parser("incorporar", help="proponer (y con --confirmar registrar) lecciones de otros proyectos como lecciones previas"); fuentes(i)
    i.add_argument("--proyecto", required=True); i.add_argument("--ids", required=True, help="refs <proyecto>:<L-###> separadas por coma")
    i.add_argument("--responsable", help="responsable_seguimiento (defecto: el gestor de estado.json)")
    i.add_argument("--confirmar", action="store_true", help="registrar las filas (sin esto, solo vista previa)"); i.add_argument("--por", help="quién confirmó la incorporación (Rol: Nombre)")
    i.add_argument("--fecha", help="fecha de registro AAAA-MM-DD (defecto: hoy)")
    a = ap.parse_args()
    if a.cmd in ("listar", "clasificar", "accionar", "verificar", "descartar", "informe"):
        if not os.path.exists(os.path.join(a.proyecto, "estado.json")):
            sys.exit(f"{a.proyecto}: no es una carpeta de proyecto (falta estado.json) / not a project folder")
        IDIOMA = E.idioma_de(a.proyecto)
        if a.cmd == "informe": return cmd_informe(a)
        if a.cmd != "listar": return cmd_ciclo(a)
        corte = fecha_ok(a.corte, "--corte") if a.corte else None
        sel, sin_cl, total = listar(a.proyecto, a.para, a.estado, corte)
        if a.json:
            print(json.dumps({"para": a.para or "", "corte": corte or datetime.date.today().isoformat(), "total": total, "sin_clasificar": sin_cl,
                              "lecciones": sel[:a.max or len(sel)]}, ensure_ascii=False, indent=2)); return
        print(texto_listar(sel, sin_cl, total, a.para, a.max or len(sel))); return
    if a.cmd == "incorporar":
        if not os.path.exists(os.path.join(a.proyecto, "estado.json")):
            sys.exit(f"{a.proyecto}: no es una carpeta de proyecto (falta estado.json) / not a project folder")
        IDIOMA = E.idioma_de(a.proyecto)
    else:
        IDIOMA = a.idioma
    if not (a.en or a.indice): sys.exit(t("Indicar --en <carpetas de proyectos> o --indice <CSV exportado>.", "Pass --en <project folders> or --indice <exported CSV>."))
    filas, omit = leer_lecciones(a.en, a.indice)
    if a.cmd == "buscar":
        sel = filtrar(filas, a.texto, a.categoria, a.etiqueta, a.para)
        if a.exportar:
            ra = os.path.abspath(a.exportar); ruta_indice_ok(ra)
            os.makedirs(os.path.dirname(ra), exist_ok=True)
            conservadas, total_ix = exportar_indice(ra, sel)
            print(t(f"Índice: {a.exportar} ({len(sel)} lecciones aprobadas).", f"Index: {a.exportar} ({len(sel)} approved lessons).")
                  + (t(f" Se conservan {conservadas} de otras refs; total {total_ix}.", f" Kept {conservadas} from other refs; total {total_ix}.") if conservadas else ""),
                  file=sys.stderr if a.json else sys.stdout)
        if a.json:
            m = a.max or len(sel)
            print(json.dumps({"total_aprobadas": len(filas), "omitidas": omit, "coinciden": len(sel), "lecciones": sel[:m]}, ensure_ascii=False, indent=2)); return
        print(texto_resultado(sel, len(filas), omit, a.max or len(sel))); return
    # incorporar
    refs = [x.strip() for x in a.ids.split(",") if x.strip()]
    por_ref = {f["ref"]: f for f in filas}
    faltan = [r for r in refs if r not in por_ref]
    if faltan: sys.exit(t(f"No se encontraron como lecciones aprobadas: {', '.join(faltan)} (ver 'buscar').", f"Not found among approved lessons: {', '.join(faltan)} (see 'buscar')."))
    e = E.cargar_estado(a.proyecto)
    propias = E.leer_csv(E.ruta_registro(a.proyecto, "lecciones"))[1] if os.path.exists(E.ruta_registro(a.proyecto, "lecciones")) else []
    ya = {" · ".join(f["origen"].split(" · ")[:2]): f.get("id") for f in propias if f.get("origen")}   # <proyecto> · L-### → id local
    responsable = a.responsable or e.get("roles", {}).get("gestor_proyecto", "")
    nuevas, repetidas = [], []
    for r in refs:
        f = por_ref[r]; clave = f"{linea(f['proyecto'], 80)} · {f['id']}"
        if clave in ya: repetidas.append(f"{r} = {ya[clave]}"); continue
        nuevas.append({"etapa": str(e.get("etapa_actual", {}).get("numero", "")), "categoria": linea(f.get("categoria"), 40), "situacion": linea(f.get("situacion"), 400),
                       "efecto": linea(f.get("efecto"), 300), "recomendacion": linea(f.get("recomendacion"), 400),
                       "prioridad": f.get("prioridad") if f.get("prioridad") in ("alta", "media", "baja") else "",
                       "responsable_seguimiento": linea(responsable, 60), "origen": f"{clave} · {f.get('fecha', '')}", "etiquetas": linea(f.get("etiquetas"), 80),
                       "impacto": f.get("impacto") if f.get("impacto") in ORD_IMP else "", "recurrencia": f.get("recurrencia") if f.get("recurrencia") in ORD_REC else "",
                       "aplicar_en": ";".join(x for x in procesos_de(f) if x in PROCESOS),
                       "notas": t("lección previa de otro proyecto", "previous lesson from another project") + (f"; {t('confirmada por', 'confirmed by')} {linea(a.por, 60)}" if a.por else "")})
    for x in repetidas: print(t(f"Ya incorporada: {x}", f"Already incorporated: {x}"))
    if not nuevas: print(t("Nada nuevo para incorporar.", "Nothing new to incorporate.")); return
    if not a.confirmar:
        print(t(f"Vista previa: {len(nuevas)} lección(es) previa(s) para {a.proyecto}/03-control/registros/lecciones.csv (no se registró nada):",
                f"Preview: {len(nuevas)} previous lesson(s) for {a.proyecto}/03-control/registros/lecciones.csv (nothing recorded):"))
        for n in nuevas:
            print(f"- {n['origen']} · {n['categoria'] or '—'}" + (f" · #{n['etiquetas']}" if n["etiquetas"] else "") + f" · {t('responsable', 'owner')} {n['responsable_seguimiento'] or '—'}")
            print(t("    recomendación: ", "    recommendation: ") + linea(n["recomendacion"], 180))
        print(t("Confirmar con la persona y repetir con --confirmar --por \"Gestor: Nombre\". Luego convertir cada una en un control temprano (riesgo con respuesta, acción o "
                "condición del plan) y marcarla accionada-proyecto con notas=incorporada: <artefacto>.",
                "Confirm with the person and rerun with --confirmar --por \"Manager: Name\". Then turn each into an early control (risk with a response, action or "
                "plan condition) and mark it accionada-proyecto with notas=incorporada: <artifact>."))
        return
    if not a.por: sys.exit(t("--confirmar requiere --por \"Rol: Nombre\" (quién confirmó la incorporación).", "--confirmar requires --por \"Role: Name\" (who confirmed)."))
    ids = []
    for n in nuevas:
        cmd = [sys.executable, os.path.join(S, "registro.py"), "--proyecto", a.proyecto, "agregar", "lecciones"] + [x for k, v in n.items() if v for x in ("--campo", f"{k}={v}")]
        if a.fecha: cmd += ["--campo", f"fecha={a.fecha}"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0: sys.exit(t(f"registro.py rechazó {n['origen']}: ", f"registro.py rejected {n['origen']}: ") + (r.stderr or r.stdout).strip()[-400:])
        ids.append(f"{r.stdout.strip().splitlines()[-1]} ← {n['origen']}")
    print(t("Lecciones previas registradas (estado registrada): ", "Previous lessons recorded (status registrada): ") + "; ".join(ids))
    print(t("Siguiente: un control temprano por lección (pm-riesgos, acción en pm-registros o condición del plan de la etapa) y marcarla accionada-proyecto con notas=incorporada: <artefacto>.",
            "Next: one early control per lesson (pm-riesgos, an action in pm-registros or a stage-plan condition) and mark it accionada-proyecto with notas=incorporada: <artifact>."))

if __name__ == "__main__":
    main()
