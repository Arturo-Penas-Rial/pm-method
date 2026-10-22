#!/usr/bin/env python3
"""Lee y actualiza estado.json del proyecto: fase, proceso, etapa, tolerancias por nivel, roles, artefactos,
puertas de decisión y transiciones del ciclo de vida por etapas (PRINCE2 por defecto).
Read/update the project's estado.json and drive the stage-based life cycle.

Uso / Usage:
  estado.py --proyecto ./p ver | siguiente
  estado.py --proyecto ./p tolerancia --nivel proyecto tiempo="±2 semanas" costo="±10 %"
  estado.py --proyecto ./p tolerancia --nivel etapa costo="±5 %"
  estado.py --proyecto ./p rol gestor_proyecto="Ana" usuario_senior="Jefa A;Jefe B" product_owner="Luis"
  estado.py --proyecto ./p agil cadencia_iteracion_dias=14 velocidad_referencia=30
  estado.py --proyecto ./p umbrales-riesgo alto=15 medio=6       # si el enfoque de riesgo usa otros umbrales P×I
  estado.py --proyecto ./p integracion tracker=jira diagramas=archify
  estado.py --proyecto ./p artefacto plan-etapa-2 --ruta 02-planificacion/plan-etapa-2.md --estado en-revision --version 0.3
  estado.py --proyecto ./p aprobar plan-etapa-2 --por "Ejecutivo: C. Ruiz" [--version 1.0] [--fecha 2027-02-01]
  estado.py --proyecto ./p puerta autorizar-etapa --decision aprobado --por "Junta" [--condiciones ".."] [--fecha ..] [--etapa-nombre ".."] [--inicio ..] [--fin ..] [--tol costo=5% tiempo=1sem]
  estado.py --proyecto ./p cumplir-condiciones autorizar-etapa [--fecha ..] [--por "Ejecutivo: C. Ruiz"] [--nota ".."]
  estado.py --proyecto ./p presupuesto cambio=15000 riesgo=20000 gestion=10000 limite_autoridad_cambio=5000 [--por ..] [--fecha ..]
  estado.py --proyecto ./p resumen                                # fase, roles, tolerancias, presupuestos, puertas y siguiente paso
  estado.py --proyecto ./p limite-etapa [--excepcion X-001]      # CS → SB (fin de etapa o plan de excepción)
  estado.py --proyecto ./p cierre [--prematuro]                    # CS/SB → CP (cierre planificado o prematuro)
  estado.py --proyecto ./p etapa --numero 2 --nombre "Construcción" --inicio .. --fin ..   # corrección manual
  estado.py --proyecto ./p set enfoque_entrega=hibrido --por "Ejecutivo: C. Ruiz" [--nivel junta] [--fecha ..]   # claves simples validadas
  estado.py --proyecto ./p contexto [--max 2000] [--corte AAAA-MM-DD] [--json]   # resumen derivado para el inicio de sesión
  estado.py --proyecto ./p radar [--corte AAAA-MM-DD] [--max 5] [--json | --linea]   # decidir, escalar, desbloquear y vigilar (solo lectura)
  estado.py --proyecto ./p briefing [--para ST-###] [--corte AAAA-MM-DD] [--salida RUTA|-] [--json]   # briefing de incorporación (≤ 2 páginas)
  estado.py --proyecto ./p periodo --desde AAAA-MM-DD [--corte ..] [--proximo ..] [--juicio J.json] [--tablero [RUTA]] [--highlight [RUTA] [--forzar]] [--json]
                                                                 # datos del período → tablero y borrador del highlight (semáforos por regla)
  estado.py --proyecto ./p periodo --verificar INFORME.md [...] [--corte ..]   # cadena de reporte: cifras del EVM y semáforos (código 1 si difieren)
  estado.py --proyecto ./p productos [--corte AAAA-MM-DD] [--fuente auto|backlog|wbs] [--alcance proyecto|WP-###|R1|3.2] [--max 40] [--json | --markdown [RUTA]]   # estado de productos (solo lectura)

Las puertas las decide una persona con rol en la junta; este script solo registra la decisión (y la anota en
decisiones.csv). Gates are decided by people; this script records them.
"""
import argparse, subprocess, json, os, shutil, sys, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esquema as E

def guardar(p, e):
    e["actualizado"] = datetime.date.today().isoformat(); e["version_estado"] = e.get("version_estado", 0) + 1
    if e.get("version_paquete") != E.VERSION_PAQUETE:     # el estado ya quedó migrado al esquema vigente al leerse
        e["version_paquete_anterior"] = e.get("version_paquete", ""); e["version_paquete"] = E.VERSION_PAQUETE
    json.dump(e, open(os.path.join(p, "estado.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def kv(lst):
    d = {}
    for x in lst or []:
        if "=" not in x: sys.exit(f"Par inválido (usar clave=valor) / invalid pair: {x}")
        k, v = x.split("=", 1); d[k.strip()] = v.strip()
    return d

def pendientes(e):
    return [p for p in e.get("puertas", []) if p.get("decision") == "pendiente" and not p.get("resuelta")]

def condiciones_abiertas(e):
    return [p for p in e.get("puertas", []) if p.get("decision") in ("condicionado", "aprobado") and p.get("condiciones") and not p.get("condiciones_cumplidas")]

def recortar(x, n):
    """Texto de una línea de hasta n caracteres (sin saltos de línea ni caracteres de control)."""
    x = re.sub(r"[\x00-\x1f\x7f]+", " ", str(x or "")).strip()
    return x if len(x) <= n else x[:n - 1].rstrip() + "…"

def lista_ids(ids, k, L):
    """'A, B, C … y N más' con a lo sumo k elementos."""
    ids = list(ids)
    if len(ids) <= k: return ", ".join(ids)
    return ", ".join(ids[:k]) + E.t(L, f" … y {len(ids) - k} más", f" … and {len(ids) - k} more")

CLAVE_VALIDA = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

def validar_clave(nombre, L):
    """SEG-07: la clave de un artefacto forma el nombre de la copia congelada en historial/: sin rutas, '..' ni absolutas."""
    if not CLAVE_VALIDA.match(nombre or "") or ".." in nombre:
        sys.exit(E.t(L, f"Clave de artefacto inválida: {nombre!r} (letras, dígitos, '.', '_' y '-'; sin '/', '..' ni rutas absolutas).",
                     f"Invalid artifact key: {nombre!r} (letters, digits, '.', '_' and '-'; no '/', '..' or absolute paths)."))

PRIORIDAD = {"urgente": 0, "alta": 1, "media": 2, "baja": 3, "": 4}

def contexto(proyecto, e, maximo=2000, corte=None):
    """Resumen derivado de estado.json y los registros para el inicio de sesión (hook inicio.py): conteos abiertos (sin los
    registros de catálogo, como estereotipos), riesgos altos sin respuesta, riesgos con la revisión vencida (REG-09),
    issues abiertos, acciones vencidas, supuestos críticos sin validar, condiciones abiertas de puertas y próxima puerta,
    con ids citados y sin texto libre de los registros. Determinista y de a lo sumo `maximo` caracteres.
    Devuelve (texto, datos)."""
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en); hoy = corte or datetime.date.today().isoformat()
    def filas(reg):
        p = E.ruta_registro(proyecto, reg)
        if not os.path.exists(p): return []
        try: return E.leer_csv(p)[1]
        except Exception: return []
    def num(x):
        try: return float(x or 0)
        except ValueError: return 0.0
    abiertos = {}
    for reg, spec in E.REGISTROS.items():
        ab = spec.get("abiertos") or []
        if ab and not spec.get("catalogo"): abiertos[reg] = [f for f in filas(reg) if f.get("estado") in ab]
    alto = num((e.get("umbrales_riesgo") or {}).get("alto")) or E.UMBRAL_RIESGO_ALTO
    d = {"corte": hoy, "abiertos": {k: len(v) for k, v in abiertos.items() if v},
         "riesgos_altos_sin_respuesta": [f["id"] for f in sorted(abiertos.get("riesgos", []), key=lambda f: -num(f.get("puntuacion")))
                                         if num(f.get("puntuacion")) >= alto and not f.get("respuesta")],
         "riesgos_revision_vencida": [f"{f['id']} ({f['fecha_revision']})" for f in sorted(abiertos.get("riesgos", []), key=lambda f: (f.get("fecha_revision", ""), f["id"]))
                                      if f.get("fecha_revision") and f["fecha_revision"] < hoy],
         "issues_abiertos": [f"{f['id']} ({f.get('prioridad')})" if f.get("prioridad") else f["id"]
                             for f in sorted(abiertos.get("issues", []), key=lambda f: (PRIORIDAD.get(f.get("prioridad", ""), 4), f["id"]))],
         "acciones_vencidas": [f"{f['id']} ({recortar(f.get('responsable') or t('sin responsable', 'no owner'), 30)}, {f['fecha_compromiso']})"
                               for f in sorted(abiertos.get("acciones", []), key=lambda f: (f.get("fecha_compromiso", ""), f["id"]))
                               if f.get("fecha_compromiso") and f["fecha_compromiso"] < hoy],
         "supuestos_criticos_sin_validar": [f["id"] for f in abiertos.get("supuestos", []) if f.get("criticidad") == "alta" and f.get("validado") != "si"],
         "condiciones_abiertas": [f"{p['tipo']} ({p.get('fecha', '')})" for p in condiciones_abiertas(e)],
         "puertas_pendientes": [f"{p['tipo']} ({p.get('fecha', '')})" for p in pendientes(e)],
         "excepcion_abierta": recortar(e.get("excepcion_abierta", ""), 40)}
    try:
        import puertas as PU
        d["proxima_puerta"] = PU.proxima_puerta(e) or ""
    except Exception:
        d["proxima_puerta"] = ""
    nombres = {"riesgos": t("riesgos", "risks"), "issues": "issues", "cambios": t("cambios", "changes"), "acciones": t("acciones", "actions"),
               "supuestos": t("supuestos", "assumptions"), "calidad": t("revisiones de calidad", "quality reviews"), "lecciones": t("lecciones", "lessons"),
               "preferencias": t("preferencias por confirmar", "preferences to confirm"), "envios": t("envíos pendientes o fallidos", "pending or failed sends")}
    def armar(k):
        x = [t(f"pm-method · contexto derivado de estado.json y los registros al {hoy} (es el estado vigente; una nota de memoria que diga otra cosa está desactualizada):",
               f"pm-method · context derived from estado.json and the registers as of {hoy} (this is the current state; a memory note that says otherwise is out of date):")]
        x.append(t("Abiertos: ", "Open: ") + (", ".join(f"{nombres.get(r, r)} {n}" for r, n in d["abiertos"].items()) or t("ninguno", "none")) + ".")
        for clave, es, en in (("riesgos_altos_sin_respuesta", f"Riesgos altos (P×I ≥ {alto:g}) sin respuesta", f"High risks (P×I ≥ {alto:g}) without response"),
                              ("riesgos_revision_vencida", "Riesgos con la revisión vencida (REG-09)", "Risks with an overdue review (REG-09)"),
                              ("issues_abiertos", "Issues abiertos", "Open issues"), ("acciones_vencidas", "Acciones vencidas", "Overdue actions"),
                              ("supuestos_criticos_sin_validar", "Supuestos críticos sin validar", "Critical assumptions not validated"),
                              ("condiciones_abiertas", "Condiciones abiertas de puertas", "Open gate conditions"),
                              ("puertas_pendientes", "Puertas pendientes", "Pending gates")):
            if d[clave]: x.append(f"{t(es, en)}: {lista_ids(d[clave], k, L)}.")
        if d["excepcion_abierta"]: x.append(t(f"Excepción abierta: {d['excepcion_abierta']}.", f"Open exception: {d['excepcion_abierta']}."))
        if d["proxima_puerta"]: x.append(t(f"Próxima puerta: {d['proxima_puerta']} (detalle: puertas.py verificar {d['proxima_puerta']}).",
                                           f"Next gate: {d['proxima_puerta']} (detail: puertas.py verificar {d['proxima_puerta']})."))
        return "\n".join(x)
    for k in (8, 5, 3, 1, 0):
        txt = armar(k)
        if len(txt) <= maximo: break
    if len(txt) > maximo: txt = txt[:maximo - 1] + "…"
    return txt, d

def siguiente(e):
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en)
    enf = e.get("enfoque_entrega", "predictivo"); fase, proc = e.get("fase"), e.get("proceso_actual")
    ag = enf in ("agil", "hibrido")
    if (fase, proc) == ("pre-proyecto", "SU"):
        msg = t("Puesta en marcha (SU): mandato → lecciones previas → brief (con caso de negocio esquemático y enfoque del proyecto) → junta y roles → plan de la etapa de iniciación. "
                + ("Ágil/híbrido: brief ligero + visión y backlog inicial de épicas. " if ag else "")
                + "Agentes: pm-inicio. Puerta: autorizar-inicio (pm-director).",
                "Starting up (SU): mandate → previous lessons → brief (outline business case, project approach) → board and roles → initiation stage plan. "
                + ("Agile/hybrid: light brief + vision and initial epic backlog. " if ag else "")
                + "Agent: pm-inicio. Gate: autorizar-inicio (pm-director).")
    elif (fase, proc) == ("inicio", "IP"):
        if ag and enf == "agil":
            msg = t("Iniciación (IP), perfil ágil mínimo: PID compacto (business case, estructura con PO, enfoques en una página cada uno), backlog priorizado con MoSCoW, release plan por etapas, DoD/DoR, presupuesto por iteración, plan de la primera etapa de entrega. Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa.",
                    "Initiation (IP), minimal agile profile: compact PID (business case, structure with PO, one-page approaches), MoSCoW-prioritized backlog, release plan by stage, DoD/DoR, budget per iteration, first delivery stage plan. Agents: pm-inicio + pm-planificacion. Gates: autorizar-proyecto and autorizar-etapa.")
        else:
            msg = t("Iniciación (IP): enfoques de gestión, controles y tolerancias, PBS/WBS y plan de proyecto (cronograma, costos), business case detallado, PID; luego plan de la primera etapa de entrega. "
                    + ("Híbrido: definir qué productos van con paquetes iterativos y su release plan. " if ag else "")
                    + "Agentes: pm-inicio + pm-planificacion. Puertas: autorizar-proyecto y autorizar-etapa (pm-director).",
                    "Initiation (IP): management approaches, controls and tolerances, PBS/WBS and project plan (schedule, costs), detailed business case, PID; then first delivery stage plan. "
                    + ("Hybrid: decide which products use iterative work packages and their release plan. " if ag else "")
                    + "Agents: pm-inicio + pm-planificacion. Gates: autorizar-proyecto and autorizar-etapa (pm-director).")
        if e.get("proyecto_autorizado"):
            msg += t(" Proyecto ya autorizado: falta autorizar-etapa para la primera etapa de entrega.", " Project already authorized: autorizar-etapa for the first delivery stage is pending.")
    elif (fase, proc) == ("entrega", "CS"):
        msg = t("Control de etapa (CS) + entrega (MP): autorizar paquetes de trabajo, checkpoints, " + ("iteraciones con review/retro, " if ag else "")
                + "revisar riesgos/issues, highlight reports a la junta. Al acercarse el fin de etapa: estado.py limite-etapa. Pronóstico fuera de tolerancia: informe de excepción → pm-director. Agente: pm-control.",
                "Controlling a stage (CS) + delivery (MP): authorize work packages, checkpoints, " + ("iterations with review/retro, " if ag else "")
                + "review risks/issues, highlight reports to the board. Near stage end: estado.py limite-etapa. Forecast outside tolerance: exception report → pm-director. Agent: pm-control.")
    elif (fase, proc) == ("entrega", "SB"):
        if e.get("excepcion_abierta"):
            msg = t(f"Límite de etapa por excepción {e['excepcion_abierta']}: plan de excepción (reemplaza el plan vigente), actualizar plan de proyecto, business case y riesgos. Puerta: autorizar-plan-excepcion (pm-director).",
                    f"Stage boundary for exception {e['excepcion_abierta']}: exception plan (replaces the current plan), update project plan, business case and risks. Gate: autorizar-plan-excepcion (pm-director).")
        else:
            msg = t("Límite de etapa (SB): informe de fin de etapa, plan de la siguiente etapa, actualizar plan de proyecto, business case, riesgos y lecciones. Puerta: autorizar-etapa (o si es la última etapa: estado.py cierre). Agentes: pm-planificacion + pm-control.",
                    "Stage boundary (SB): end stage report, next stage plan, update project plan, business case, risks and lessons. Gate: autorizar-etapa (or, if last stage: estado.py cierre). Agents: pm-planificacion + pm-control.")
    elif (fase, proc) == ("cierre", "CP"):
        msg = t("Cierre (CP): confirmar aceptación de productos, traspaso a operaciones, evaluar el proyecto contra el PID original, lecciones, plan de revisión de beneficios, informe de fin de proyecto y recomendación de cierre. Agente: pm-cierre. Puerta: autorizar-cierre (pm-director).",
                "Closing (CP): confirm product acceptance, handover, evaluate against the original PID, lessons, benefits review plan, end project report and closure recommendation. Agent: pm-cierre. Gate: autorizar-cierre (pm-director).")
    elif fase == "cerrado":
        msg = t("Proyecto cerrado. Pendiente fuera del proyecto: revisiones de beneficios según el plan (responsable: usuario sénior / capa de negocio).",
                "Project closed. Outside the project: benefits reviews per the plan (owner: senior user / business layer).")
    else:
        msg = t("Estado no reconocido; revisar fase/proceso_actual con 'ver'.", "Unrecognized state; check fase/proceso_actual with 'ver'.")
    out = [t(f"Fase: {fase} · Proceso: {proc} · Etapa {e['etapa_actual']['numero']}: {e['etapa_actual']['nombre']} · Enfoque: {enf}",
             f"Phase: {fase} · Process: {proc} · Stage {e['etapa_actual']['numero']}: {e['etapa_actual']['nombre']} · Approach: {enf}"), msg]
    pend = pendientes(e)
    if pend: out.append(t("Puertas pendientes: ", "Pending gates: ") + ", ".join(f"{p['tipo']} ({p['fecha']})" for p in pend))
    cond = condiciones_abiertas(e)
    if cond: out.append(t("Condiciones abiertas: ", "Open conditions: ") + "; ".join(f"{p['tipo']}: {recortar(p['condiciones'], 240)}" for p in cond))
    vac = [d for d in ("tiempo", "costo") if not e["tolerancias"]["proyecto"].get(d)]
    if fase in ("inicio", "entrega") and vac:
        out.append(t(f"Aviso: faltan tolerancias de proyecto ({', '.join(vac)}).", f"Warning: missing project tolerances ({', '.join(vac)})."))
    return "\n".join(out)

def registrar_puerta(a, e):
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en)
    fecha = a.fecha or datetime.date.today().isoformat()
    fase, proc = e["fase"], e["proceso_actual"]
    # precondiciones (se pueden saltar con --forzar, quedando anotado)
    pre = {
        "autorizar-inicio": fase == "pre-proyecto",
        "autorizar-proyecto": fase == "inicio",
        "autorizar-etapa": (fase == "inicio" and bool(e.get("proyecto_autorizado"))) or (fase, proc) == ("entrega", "SB"),
        "autorizar-plan-excepcion": (fase, proc) == ("entrega", "SB") or fase == "inicio",
        "autorizar-cierre": (fase, proc) == ("cierre", "CP"),
        "decision-ad-hoc": True,
    }[a.tipo]
    if not pre and a.decision != "pendiente" and not a.forzar:
        sys.exit(t(f"La puerta {a.tipo} no corresponde al estado actual ({fase}/{proc}). Revisar 'siguiente' o usar --forzar.",
                   f"Gate {a.tipo} does not fit the current state ({fase}/{proc}). Check 'siguiente' or use --forzar."))
    # verificación de la puerta (puertas.py): salud + controles automáticos (PRINCE2 y BMAD) + lista de control de la junta.
    # 'aprobado' se rechaza con bloqueos; 'condicionado' los suma como condiciones; --forzar los anota. Las condiciones de
    # los controles quedan como observaciones de la puerta.
    if a.decision in ("aprobado", "condicionado") and a.tipo != "decision-ad-hoc":
        import puertas as PU
        bloqueos, observaciones, avisos, lista = PU.evaluar(a.proyecto, e, a.tipo, kv(a.tol) if getattr(a, "tol", None) else {})
        for x in avisos: print(t("Aviso: ", "Warning: ") + x)
        if bloqueos:
            if a.forzar:
                print(t("Aviso: puerta registrada con bloqueos (--forzar): ", "Warning: gate recorded with blockers (--forzar): ") + " | ".join(bloqueos))
            elif a.decision == "condicionado":
                a.condiciones = "; ".join(x for x in [a.condiciones] + bloqueos if x)
                print(t("Condiciones agregadas por bloqueos: ", "Conditions added from blockers: ") + " | ".join(bloqueos))
            else:
                sys.exit(t("No se registra 'aprobado' para " + a.tipo + " con estos bloqueos:\n  - " + "\n  - ".join(bloqueos) +
                           "\nOpciones: corregirlos y volver a registrar; registrar --decision condicionado (se suman como condiciones); "
                           "o, si la junta lo decide expresamente, --forzar (queda anotado). Detalle: puertas.py --proyecto <dir> verificar " + a.tipo,
                           "'aprobado' is not recorded for " + a.tipo + " with these blockers:\n  - " + "\n  - ".join(bloqueos) +
                           "\nOptions: fix them; record --decision condicionado (added as conditions); or --forzar if the board explicitly decides so."))
        if a.decision == "condicionado" and observaciones:
            # los hallazgos de tipo condición (p. ej. CONCERNS del gate de preparación de BMAD) pasan a ser condiciones
            # formales de la puerta, con seguimiento (sanidad EST-12, puertas G-01) hasta cumplir-condiciones
            nuevas = [x for x in observaciones if x not in (a.condiciones or "") and not x.startswith(PU.PREFIJO_G01)]
            if nuevas:
                a.condiciones = "; ".join(x for x in [a.condiciones] + nuevas if x)
                print(t("Condiciones agregadas desde la verificación: ", "Conditions added from verification: ") + " | ".join(nuevas))
        a._verificacion = {"lista": (lista or {}).get("ruta", ""), "confirmada_por": (lista or {}).get("confirmada_por", ""),
                           "bloqueos": bloqueos, "observaciones": observaciones}
    for p in pendientes(e):
        if p["tipo"] == a.tipo and a.decision != "pendiente":
            p["resuelta"] = fecha
    reg = {"tipo": a.tipo, "fecha": fecha, "decision": a.decision, "por": a.por, "condiciones": a.condiciones,
           "etapa": e["etapa_actual"]["numero"]}
    if a.forzar: reg["forzada"] = True
    if getattr(a, "_verificacion", None): reg["verificacion"] = a._verificacion
    e["puertas"].append(reg)
    avanza = a.decision in ("aprobado", "condicionado")
    if avanza:
        n = e["etapa_actual"]["numero"]
        if a.tipo == "autorizar-inicio":
            e["fase"], e["proceso_actual"] = "inicio", "IP"
            e["etapa_actual"] = {"numero": 1, "nombre": a.etapa_nombre or t("Iniciación", "Initiation"), "inicio": fecha, "fin_previsto": a.fin or ""}
        elif a.tipo == "autorizar-proyecto":
            e["proyecto_autorizado"] = True
        elif a.tipo == "autorizar-etapa":
            e["fase"], e["proceso_actual"] = "entrega", "CS"
            e["etapa_actual"] = {"numero": n + 1, "nombre": a.etapa_nombre or t(f"Etapa {n + 1}", f"Stage {n + 1}"), "inicio": a.inicio or fecha, "fin_previsto": a.fin or ""}
            tol = kv(a.tol) if a.tol else {}
            for k in tol:
                if k not in E.DIMENSIONES_TOLERANCIA: sys.exit(t(f"Tolerancia desconocida: {k}", f"Unknown tolerance: {k}") + f" ({', '.join(E.DIMENSIONES_TOLERANCIA)})")
            if tol:
                e["tolerancias"]["etapa"] = {k: tol.get(k, "") for k in E.DIMENSIONES_TOLERANCIA}
            elif any(e["tolerancias"].get("etapa", {}).values()):
                print(t("Aviso: se conservan las tolerancias de etapa vigentes; si la junta fijó otras para esta etapa, pasarlas con --tol o 'tolerancia --nivel etapa'.",
                        "Warning: current stage tolerances are kept; if the board set different ones for this stage, pass --tol or use 'tolerancia --nivel etapa'."))
        elif a.tipo == "autorizar-plan-excepcion":
            e["fase"], e["proceso_actual"] = ("inicio", "IP") if fase == "inicio" else ("entrega", "CS")
            e["excepcion_abierta"] = ""
            if a.etapa_nombre: e["etapa_actual"]["nombre"] = a.etapa_nombre
            if a.fin: e["etapa_actual"]["fin_previsto"] = a.fin
        elif a.tipo == "autorizar-cierre":
            e["fase"], e["proceso_actual"] = "cerrado", "CP"
    elif a.decision == "rechazado" and a.tipo in ("autorizar-etapa", "autorizar-plan-excepcion"):
        print(t("Aviso: rechazo de etapa/plan de excepción. Opciones de la junta: pedir replanificación o cierre prematuro (estado.py cierre --prematuro).",
                "Warning: stage/exception plan rejected. Board options: request re-planning or premature closure (estado.py cierre --prematuro)."))
    if a.decision != "pendiente":
        ver = getattr(a, "_verificacion", None) or {}
        nota = f"puerta: {a.tipo}" + (f"; verificación: {ver['lista']}" if ver.get("lista") else "") + \
               (f"; observaciones: {' | '.join(ver['observaciones'])}" if ver.get("observaciones") else "") + ("; FORZADA" if a.forzar else "")
        did = E.anotar_decision(a.proyecto, f"{a.tipo}: {a.decision}" + (f" — condiciones: {a.condiciones}" if a.condiciones else ""),
                                a.por, nivel="junta", contexto=f"{fase}/{proc} etapa {reg['etapa']}",
                                artefactos=ver.get("lista", ""), notas=nota, fecha=fecha)
        reg["decision_id"] = did

# ---------------------------------------------------------------- radar de atención y briefing de incorporación
# Radar: qué hay que decidir, escalar, desbloquear o vigilar al corte, con id, fecha, responsable y siguiente paso (skill o
# script). Solo lectura. PRINCE2 CS «evaluar el estado de la etapa», «capturar», «escalar issues y riesgos» y gestión por
# excepción (pm-knowledge: prince2-principios-personas-procesos.md §5.4; prince2-practicas-riesgo-issues-progreso-productos.md
# §4.c.2 y §7.3). Regla de prioridad (pm-estado-proyecto, references/guia.md §9): 1 = hoy (vencido, fuera de tolerancia o
# presupuesto agotado), 2 = espera una decisión o bloquea, 3 = pendiente sin bloqueo inmediato, 4 = vigilar; orden dentro de
# cada grupo: prioridad, fecha (las vacías al final) e id. Los códigos EST, REG, SUP, CAM, TOL y QUA son los de sanidad.py.
GRUPOS_RADAR = ("decidir", "escalar", "desbloquear", "vigilar")
REGLAS_RADAR = {   # regla: (grupo, prioridad)
    "EST-14": ("decidir", 1), "SUP-02": ("decidir", 1), "RAD-03": ("decidir", 1),
    "RAD-01": ("decidir", 2), "RAD-02": ("decidir", 2), "EST-11": ("decidir", 2), "EST-12": ("decidir", 2), "SUP-03": ("decidir", 2),
    "SUP-01": ("decidir", 3), "REG-11": ("decidir", 3),
    "TOL-01": ("escalar", 1), "CAM-03": ("escalar", 1), "RAD-04": ("escalar", 2), "CAM-04": ("escalar", 2), "CAM-05": ("escalar", 2),
    "REG-07": ("desbloquear", 1), "RAD-05": ("desbloquear", 3), "REG-06": ("desbloquear", 2), "RAD-06": ("desbloquear", 3),
    "QUA-02": ("desbloquear", 3), "QUA-03": ("desbloquear", 3),
    "REG-09": ("vigilar", 3), "REG-12": ("vigilar", 3), "RAD-07": ("vigilar", 3), "TOL-02": ("vigilar", 4), "TOL-03": ("vigilar", 4), "RAD-08": ("vigilar", 4),
}
ID_REG = re.compile(r"\b(?:R|I|C|D|S|L|ST|Q|A)-\d{3}\b")

def _filas(proyecto, reg):
    p = E.ruta_registro(proyecto, reg)
    if not os.path.exists(p): return []
    try: return E.leer_csv(p)[1]
    except Exception: return []

def _cifra(x, L, dec=0):
    s = f"{x:,.{dec}f}"
    return s if L == "en" else s.replace(",", "§").replace(".", ",").replace("§", ".")

def evm_ultimo(proyecto, corte):
    """(nombre de archivo, datos) del último corte de EVM guardado con fecha ≤ corte, o (None, {})."""
    import glob
    xs = sorted(x for x in glob.glob(os.path.join(proyecto, "03-control", "reportes", "evm-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))
                if os.path.basename(x)[4:14] <= corte)
    if not xs: return None, {}
    try: return os.path.basename(xs[-1]), json.load(open(xs[-1], encoding="utf-8"))
    except (OSError, ValueError): return os.path.basename(xs[-1]), {}

def radar(proyecto, e, corte=None, rapido=False):
    """Ítems del radar: lista de {grupo, prioridad, regla, id, fecha, responsable, que, siguiente}, ordenada. `rapido` omite
    la verificación de la próxima puerta (RAD-07), que corre sanidad en un subproceso."""
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en); hoy = corte or datetime.date.today().isoformat()
    roles = e.get("roles", {}) or {}
    gestor = roles.get("gestor_proyecto") or t("gestor", "project manager")
    junta = t("junta", "board") + (f" ({roles['ejecutivo']})" if roles.get("ejecutivo") else "")
    regs = {r: _filas(proyecto, r) for r in E.REGISTROS}
    ab = lambda reg: [f for f in regs.get(reg, []) if f.get("estado") in (E.REGISTROS[reg].get("abiertos") or [])]
    por_id = {f.get("id"): f for r in regs.values() for f in r}
    items, vistos = [], set()
    def add(regla, id_, fecha, responsable, que, siguiente, prioridad=None, grupo=None):
        if (regla, id_) in vistos: return
        vistos.add((regla, id_)); g, p = REGLAS_RADAR[regla]
        items.append({"grupo": grupo or g, "prioridad": prioridad or p, "regla": regla, "id": id_, "fecha": fecha or "",
                      "responsable": recortar(responsable, 40), "que": recortar(que, 150), "siguiente": siguiente})
    alto = E.monto((e.get("umbrales_riesgo") or {}).get("alto")) or E.UMBRAL_RIESGO_ALTO
    # --- decidir
    if e.get("excepcion_abierta"):
        add("EST-14", recortar(e["excepcion_abierta"], 20), "", junta, t("excepción abierta: el plan de excepción reemplaza al plan de etapa", "open exception: the exception plan replaces the stage plan"),
            t("pm-planificacion: plan de excepción → pm-director: puerta autorizar-plan-excepcion", "pm-planificacion: exception plan → pm-director: autorizar-plan-excepcion gate"))
    for p in pendientes(e):
        add("EST-11", p["tipo"], p.get("fecha"), junta, t("puerta pendiente de decisión", "gate awaiting a decision"),
            t(f"pm-puerta (solicitud) → pm-director: estado.py puerta {p['tipo']}", f"pm-puerta (request) → pm-director: estado.py puerta {p['tipo']}"))
    for p in condiciones_abiertas(e):
        add("EST-12", p["tipo"], p.get("fecha"), junta, t("condiciones abiertas: ", "open conditions: ") + recortar(p.get("condiciones"), 100),
            t(f"pm-director: estado.py cumplir-condiciones {p['tipo']} --por … al verificarlas", f"pm-director: estado.py cumplir-condiciones {p['tipo']} --por … once verified"))
    pres = e.get("presupuestos", {}) or {}
    lim, tope = E.monto(pres.get("limite_autoridad_cambio")), E.monto(pres.get("cambio"))
    consumo = E.consumo_cambios(regs.get("cambios", []))
    for f in regs.get("cambios", []):
        if f.get("estado") != "pendiente-decision": continue
        costo = E.monto(f.get("costo")) or 0.0
        a_junta = (not roles.get("autoridad_cambio") or (lim is not None and costo > lim) or f.get("cargo") in ("reserva-gestion", "plan-excepcion")
                   or (tope is not None and f.get("cargo") == "presupuesto-cambio" and consumo["presupuesto-cambio"] + costo > tope))
        que = f"«{recortar(f.get('titulo'), 60)}»" + (f" · {t('costo', 'cost')} {_cifra(costo, L)}" if costo else "") + (f" · {f['cargo']}" if f.get("cargo") else "")
        add("RAD-01", f["id"], f.get("fecha"), junta if a_junta else roles["autoridad_cambio"], que,
            t("pm-direccion-decisiones: solicitud de decisión a la junta (supera la autoridad o el presupuesto delegados; registra pm-director)",
              "pm-direccion-decisiones: decision request to the board (exceeds delegated authority or budget; pm-director records it)") if a_junta else
            t(f"pm-issues-cambios: decide la autoridad de cambio (registro.py actualizar cambios {f['id']} --campo decision=…)",
              f"pm-issues-cambios: the change authority decides (registro.py actualizar cambios {f['id']} --campo decision=…)"))
    for reg in ("issues", "riesgos"):
        for f in regs.get(reg, []):
            if f.get("estado") == "escalado":
                add("RAD-02", f["id"], f.get("fecha") or f.get("fecha_identificacion"), junta,
                    t("escalado: espera la decisión de la junta", "escalated: awaiting the board's decision") + f" · «{recortar(f.get('titulo') or f.get('evento'), 60)}»",
                    t("pm-direccion-decisiones: solicitud de decisión (registra pm-director)", "pm-direccion-decisiones: decision request (pm-director records it)"))
    financiadas = {r for c in regs.get("cambios", []) if E.cambio_vigente(c) and c.get("cargo") == "reserva-riesgo"
                   for r in ID_REG.findall(" ".join(str(v) for k, v in c.items() if k != "id"))}
    for f in regs.get("riesgos", []):
        if f.get("respuesta") != "contingencia" or f["id"] in financiadas: continue
        ocurrido = f.get("estado") == "ocurrido"
        if ocurrido or (f.get("estado") in E.REGISTROS["riesgos"]["abiertos"] and f.get("proximidad") == "inminente"):
            add("RAD-03", f["id"], f.get("fecha_revision"), f.get("propietario") or gestor,
                t("contingencia por activar (", "contingency to trigger (") + (t("ocurrido", "occurred") if ocurrido else t("inminente", "imminent")) + f") · «{recortar(f.get('evento'), 60)}»",
                t(f"pm-riesgos: activar la contingencia (cambio con cargo reserva-riesgo que cite {f['id']}; si ocurrió, issue en pm-issues-cambios)",
                  f"pm-riesgos: trigger the contingency (change charged to reserva-riesgo citing {f['id']}; if it occurred, an issue in pm-issues-cambios)"))
    # --- hallazgos de sanidad.py (mismas reglas que la sanidad: SUP, CAM, TOL, QUA)
    hall = []
    try:
        import sanidad as SA
        SA.H.clear()
        for chk in (lambda: SA.chk_cambios(proyecto, e, regs), lambda: SA.chk_tolerancias(proyecto, e, hoy),
                    lambda: SA.chk_supuestos(proyecto, e, regs, hoy), lambda: SA.chk_calidad(proyecto, e, regs, hoy)):
            try: chk()
            except Exception: pass
        hall = list(SA.H); SA.H.clear()
    except Exception:
        pass
    ev_archivo, ev = evm_ultimo(proyecto, hoy)
    def ev_texto():
        sem = ", ".join(f"{k[9:]}={ev[k]}" for k in ("semaforo_cronograma", "semaforo_costo", "semaforo_alcance") if ev.get(k))
        idx = " · ".join(f"{k} {_cifra(ev[k], L, 3)}" for k in ("SPI", "CPI") if isinstance(ev.get(k), (int, float)))
        return " · ".join(x for x in (idx, sem) if x)
    for h in hall:
        c, m = h["codigo"], h["mensaje"]; i = (ID_REG.findall(m) or [""])[0]; f = por_id.get(i, {})
        if c in ("SUP-01", "SUP-02", "SUP-03"):
            que = {"SUP-01": t("supuesto crítico sin experimento o sin fecha límite", "critical assumption without an experiment or a deadline"),
                   "SUP-02": t("fecha límite vencida sin resultado: seguir, cambiar o detener", "deadline passed without a result: continue, change or stop"),
                   "SUP-03": t("invalidado sin issue, cambio, riesgo o decisión que trate su efecto", "invalidated with no issue, change, risk or decision handling its effect")}[c]
            add(c, i, f.get("fecha_limite"), f.get("responsable") or gestor, que + f" · «{recortar(f.get('supuesto_o_restriccion'), 60)}»",
                t("pm-mandato-y-brief (experimento y resultado) o pm-caso-de-negocio (efecto en el caso); la junta decide si se acepta sin validar",
                  "pm-mandato-y-brief (experiment and result) or pm-caso-de-negocio (effect on the case); the board decides whether to accept it unvalidated"))
        elif c == "TOL-01":
            add(c, ev_archivo[:-5] if ev_archivo else "evm", ev.get("corte"), gestor, t("pronóstico fuera de tolerancia sin excepción abierta: ", "forecast outside tolerance with no open exception: ") + ev_texto(),
                t("pm-progreso-reportes: aviso temprano e informe de excepción → pm-director", "pm-progreso-reportes: early warning and exception report → pm-director"))
        elif c == "TOL-02":
            add(c, ev_archivo[:-5] if ev_archivo else "evm", ev.get("corte"), gestor, t("ámbar (50–100 % de la tolerancia): ", "amber (50–100 % of tolerance): ") + ev_texto(),
                t("pm-progreso-reportes: acciones correctivas y su lugar en el highlight", "pm-progreso-reportes: corrective actions, reported in the highlight"))
        elif c == "TOL-03":
            add(c, ev_archivo[:-5] if ev_archivo else "evm", ev.get("corte"), gestor, t("sin corte de EVM reciente: el pronóstico no se vigila", "no recent EVM cut-off: the forecast is not monitored"),
                t("evm.py … --proyecto <dir> --guardar --corte AAAA-MM-DD (pm-progreso-reportes)", "evm.py … --proyecto <dir> --guardar --corte YYYY-MM-DD (pm-progreso-reportes)"))
        elif c == "CAM-03" and h["severidad"] in ("ERROR", "AVISO"):
            cargo = "reserva-riesgo" if "reserva de riesgo" in m.lower() else "presupuesto-cambio"
            usado, top = consumo.get(cargo, 0.0), E.monto(pres.get(E.CARGO_PRESUPUESTO[cargo]))
            que = f"{cargo}: {_cifra(usado, L)}" + (f" {t('de', 'of')} {_cifra(top, L)} ({100 * usado / top:.0f} %)" if top else t(" sin presupuesto fijado por la junta", " with no budget set by the board"))
            if h["severidad"] == "ERROR":
                add(c, cargo, "", gestor, t("presupuesto agotado: ", "budget exhausted: ") + que,
                    t("pm-direccion-decisiones: escalar a la junta (ampliación del presupuesto o informe de excepción)", "pm-direccion-decisiones: escalate to the board (budget increase or exception report)"))
            else:
                add(c, cargo, "", gestor, que, t("avisar a la junta antes de aprobar más cambios (pm-issues-cambios)", "warn the board before approving more changes (pm-issues-cambios)"), prioridad=3, grupo="vigilar")
        elif c in ("CAM-04", "CAM-05"):
            add(c, i, f.get("fecha_decision") or f.get("fecha"), junta,
                (t("supera el límite de la autoridad de cambio", "exceeds the change authority's limit") if c == "CAM-04" else t("usa la reserva de gestión sin decisión de la junta", "uses the management reserve without a board decision"))
                + f" · {t('decidió', 'decided by')} {recortar(f.get('decidido_por'), 30)}",
                t("pm-direccion-decisiones: llevarlo a la junta y registrar su decisión (pm-director)", "pm-direccion-decisiones: take it to the board and record its decision (pm-director)"))
        elif c in ("QUA-02", "QUA-03"):
            add(c, i, f.get("fecha_prevista"), f.get("responsable_productor") or gestor,
                (t("revisión de calidad vencida", "overdue quality review") if c == "QUA-02" else t("revisión rechazada sin issue, acción o cambio", "rejected review with no issue, action or change")) + f" · «{recortar(f.get('producto'), 60)}»",
                t("pm-calidad: realizarla o replanificarla; si se rechazó, pm-issues-cambios (fuera de especificación)", "pm-calidad: hold or reschedule it; if rejected, pm-issues-cambios (off-specification)"))
    # --- lecciones (pm-lecciones-aprendidas/lecciones.py, mismas reglas que la sanidad): REG-11 decidir, REG-12 vigilar
    if regs.get("lecciones"):
        try:
            sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pm-lecciones-aprendidas", "scripts")))
            import lecciones as LX
            for _sev, c, m, _arr in LX.controles(regs["lecciones"], hoy, L):
                i = (re.findall(r"\bL-\d{3}\b", m) or [""])[0]; f = por_id.get(i, {})
                if c == "REG-11":
                    add(c, i, f.get("fecha"), f.get("responsable_seguimiento") or gestor,
                        t("lección de impacto alto sin acción ni decisión", "high-impact lesson with no action or decision") + f" · «{recortar(f.get('recomendacion') or f.get('situacion'), 60)}»",
                        t(f"pm-lecciones-aprendidas: lecciones.py accionar {i} (o descartar con motivo)", f"pm-lecciones-aprendidas: lecciones.py accionar {i} (or discard with a reason)"))
                else:
                    add(c, i, f.get("verificar_en"), f.get("responsable_seguimiento") or gestor,
                        t("lección accionada sin verificar su efecto", "actioned lesson whose effect is not checked") + (f" · {t('acción', 'action')} {recortar(f.get('accion'), 40)}" if f.get("accion") else ""),
                        t(f"pm-lecciones-aprendidas: lecciones.py verificar {i} --resultado …", f"pm-lecciones-aprendidas: lecciones.py verificar {i} --resultado …"))
        except Exception:
            pass
    # --- escalar (riesgos cuya respuesta es escalar y siguen sin escalar, A-19)
    for f in ab("riesgos"):
        if f.get("respuesta") == "escalar" and f.get("estado") != "escalado":
            add("RAD-04", f["id"], f.get("fecha_revision"), f.get("propietario") or gestor, t("respuesta «escalar» sin escalar", "response «escalate» not yet escalated") + f" · «{recortar(f.get('evento'), 60)}»",
                t("pm-riesgos → pm-director: escalar a la junta y marcar estado=escalado", "pm-riesgos → pm-director: escalate to the board and set estado=escalado"))
    # --- desbloquear
    for f in sorted(ab("acciones"), key=lambda f: (f.get("fecha_compromiso", ""), f["id"])):
        if f.get("fecha_compromiso") and f["fecha_compromiso"] < hoy:
            add("REG-07", f["id"], f["fecha_compromiso"], f.get("responsable") or t("sin responsable", "no owner"), t("acción vencida", "overdue action") + f" · «{recortar(f.get('descripcion'), 60)}»",
                t(f"pm-registros: replanificar o cerrar con el responsable (registro.py actualizar acciones {f['id']} …)", f"pm-registros: reschedule or close with the owner (registro.py actualizar acciones {f['id']} …)"))
    for f in ab("riesgos"):
        if E.monto(f.get("puntuacion")) is not None and E.monto(f.get("puntuacion")) >= alto and not (f.get("respuesta") and f.get("propietario")):
            add("REG-06", f["id"], f.get("fecha_revision"), f.get("propietario") or t("sin propietario", "no owner"),
                t(f"riesgo alto (P×I {f.get('puntuacion')}) sin ", f"high risk (P×I {f.get('puntuacion')}) without ") + (t("propietario", "owner") if not f.get("propietario") else t("respuesta", "response")),
                t("pm-riesgos: asignar propietario y respuesta", "pm-riesgos: assign owner and response"))
    for f in ab("issues"):
        if f.get("estado") != "escalado" and not f.get("responsable"):
            add("RAD-05", f["id"], f.get("fecha"), t("sin responsable", "no owner"), (f"{f['prioridad']} · " if f.get("prioridad") else "") + f"«{recortar(f.get('titulo'), 60)}»",
                t(f"pm-issues-cambios: asignar responsable (registro.py actualizar issues {f['id']} --campo responsable=…)", f"pm-issues-cambios: assign an owner (registro.py actualizar issues {f['id']} --campo responsable=…)"),
                prioridad={"urgente": 1, "alta": 2}.get(f.get("prioridad"), 3))
    abiertos_ids = {f["id"]: reg for reg in ("issues", "cambios", "acciones", "calidad") for f in ab(reg)}
    for reg in ("issues", "acciones"):
        for f in ab(reg):
            deps = sorted(x for x in set(ID_REG.findall(" ".join(str(v) for k, v in f.items() if k != "id"))) if x != f["id"] and x in abiertos_ids)
            if deps:
                add("RAD-06", f["id"], f.get("fecha_compromiso") or f.get("fecha"), f.get("responsable") or gestor,
                    t("espera ", "waits for ") + ", ".join(f"{d} ({por_id[d].get('estado')})" for d in deps[:3]) + (" …" if len(deps) > 3 else ""),
                    t(f"resolver primero {deps[0]} (o quitar la dependencia)", f"resolve {deps[0]} first (or remove the dependency)"))
    # --- vigilar
    for f in sorted(ab("riesgos"), key=lambda f: (f.get("fecha_revision", ""), f["id"])):
        if f.get("fecha_revision") and f["fecha_revision"] < hoy:
            add("REG-09", f["id"], f["fecha_revision"], f.get("propietario") or t("sin propietario", "no owner"), t("revisión del riesgo vencida", "risk review overdue"),
                t("pm-riesgos: revisarlo con el propietario y actualizar fecha_revision", "pm-riesgos: review it with the owner and update fecha_revision"))
    for f in ab("supuestos"):
        if f.get("criticidad") == "alta" and f.get("validado") != "si" and f.get("experimento") and f.get("fecha_limite") and f["fecha_limite"] >= hoy:
            add("RAD-08", f["id"], f["fecha_limite"], f.get("responsable") or gestor, t("supuesto crítico en validación", "critical assumption being validated") + f" · «{recortar(f.get('experimento'), 50)}»",
                t("pm-mandato-y-brief: registrar la evidencia al vencer la fecha límite", "pm-mandato-y-brief: record the evidence by the deadline"))
    if not rapido:
        try:
            import puertas as PU
            prox = PU.proxima_puerta(e)
            if prox:
                hs, _ = PU.evaluar_detalle(proyecto, e, prox)
                bl = sorted({h["id"] for h in hs if h["severidad"] == "bloqueo"})
                if bl:
                    add("RAD-07", prox, "", gestor, t(f"{len(bl)} bloqueo(s) de la próxima puerta: ", f"{len(bl)} blocker(s) for the next gate: ") + ", ".join(bl[:6]) + (" …" if len(bl) > 6 else ""),
                        t(f"pm-puerta: puertas.py verificar {prox}", f"pm-puerta: puertas.py verificar {prox}"))
        except Exception:
            pass
    orden = {g: i for i, g in enumerate(GRUPOS_RADAR)}
    items.sort(key=lambda x: (orden[x["grupo"]], x["prioridad"], x["fecha"] or "9999-99-99", x["id"]))
    return items

def datos_radar(proyecto, e, corte=None, limite=5, rapido=False):
    """Radar como dict para --json y para el briefing: totales, «hoy» (primer ítem de decidir, escalar y desbloquear) e ítems
    por grupo (a lo sumo `limite` por grupo; 0 = sin tope)."""
    hoy = corte or datetime.date.today().isoformat()
    its = radar(proyecto, e, hoy, rapido)
    por = {g: [x for x in its if x["grupo"] == g] for g in GRUPOS_RADAR}
    _, cx = contexto(proyecto, e, 2000, hoy)
    return {"proyecto": e.get("proyecto"), "corte": hoy, "fase": e.get("fase"), "proceso": e.get("proceso_actual"), "etapa": e.get("etapa_actual", {}).get("numero"),
            "totales": {g: len(v) for g, v in por.items()}, "abiertos": cx.get("abiertos", {}), "proxima_puerta": cx.get("proxima_puerta", ""),
            "hoy": {g: (por[g][0]["id"] if por[g] else "") for g in ("decidir", "escalar", "desbloquear")},
            "items": {g: (v[:limite] if limite else v) for g, v in por.items()},
            "excepcion_procede": any(x["regla"] in ("TOL-01", "CAM-03") for x in por["escalar"])}

def texto_radar(d, idioma="es", limite=5, maximo=3500):
    t = lambda es, en: E.t(idioma, es, en)
    nombres = {"decidir": t("DECIDIR", "DECIDE"), "escalar": t("ESCALAR", "ESCALATE"), "desbloquear": t("DESBLOQUEAR", "UNBLOCK"), "vigilar": t("VIGILAR", "WATCH")}
    verbos = {"decidir": t("decidir", "decide"), "escalar": t("escalar", "escalate"), "desbloquear": t("desbloquear", "unblock")}
    def armar(k):
        x = [t(f"Radar de atención · {recortar(d['proyecto'], 60)} ({d['fase']}/{d['proceso']}, etapa {d['etapa']}) al {d['corte']}: ",
               f"Attention radar · {recortar(d['proyecto'], 60)} ({d['fase']}/{d['proceso']}, stage {d['etapa']}) as of {d['corte']}: ")
             + " · ".join(f"{d['totales'][g]} {verbos.get(g, t('vigilar', 'watch'))}" for g in GRUPOS_RADAR)]
        x.append(t("Hoy: ", "Today: ") + " · ".join(f"{verbos[g]} {d['hoy'][g] or '—'}" for g in verbos) + ".")
        for g in GRUPOS_RADAR:
            its = d["items"][g]; n = d["totales"][g]
            if not n: x.append(f"{nombres[g]}: " + t("nada.", "nothing.")); continue
            x.append(f"{nombres[g]} ({n})")
            for it in its[:k]:
                x.append(f"  P{it['prioridad']} [{it['regla']}] {it['id']}" + (f" · {it['fecha']}" if it["fecha"] else "") + f" · {it['responsable']} — {it['que']}")
                x.append(f"      → {it['siguiente']}")
            if n > min(k, len(its)): x.append("  " + t(f"… y {n - min(k, len(its))} más (estado.py radar --json --max 0)", f"… and {n - min(k, len(its))} more (estado.py radar --json --max 0)"))
        x.append(t("Opciones: generar el highlight del período (pm-progreso-reportes) · ", "Options: produce the period's highlight (pm-progreso-reportes) · ")
                 + (t("escalar una excepción (pm-progreso-reportes: informe de excepción → pm-director).", "escalate an exception (pm-progreso-reportes: exception report → pm-director).")
                    if d["excepcion_procede"] else t("escalar una excepción no corresponde: ningún pronóstico fuera de tolerancia ni presupuesto agotado.",
                                                     "escalating an exception does not apply: no forecast outside tolerance and no exhausted budget.")))
        x.append(t("Prioridad: 1 hoy (vencido, fuera de tolerancia o presupuesto agotado) · 2 espera una decisión o bloquea · 3 pendiente · 4 vigilar; orden: prioridad, fecha, id.",
                   "Priority: 1 today (overdue, outside tolerance or budget exhausted) · 2 awaits a decision or blocks · 3 pending · 4 watch; order: priority, date, id."))
        return "\n".join(x)
    for k in (limite or 999, 3, 2, 1, 0):
        txt = armar(k)
        if len(txt) <= maximo: break
    return txt if len(txt) <= maximo else txt[:maximo - 1] + "…"

def linea_radar(d, idioma="es"):
    """Una línea para el hook de inicio: totales por grupo con el primer id de cada uno (sin texto libre de los registros)."""
    t = lambda es, en: E.t(idioma, es, en)
    verbos = {"decidir": t("decidir", "decide"), "escalar": t("escalar", "escalate"), "desbloquear": t("desbloquear", "unblock"), "vigilar": t("vigilar", "watch")}
    partes = [f"{verbos[g]} {d['totales'][g]}" + (f" ({recortar(d['items'][g][0]['id'], 30)})" if d["items"][g] else "") for g in GRUPOS_RADAR]
    return recortar(t(f"pm-method · radar al {d['corte']}: ", f"pm-method · radar as of {d['corte']}: ") + " · ".join(partes)
                    + t("; detalle, responsables y siguiente paso: pm-orquestador (estado.py radar).", "; detail, owners and next step: pm-orquestador (estado.py radar)."), 320)

def _md(x, n=90):
    """Texto de una celda o línea de Markdown: una línea, recortado y sin '|' ni etiquetas HTML que rompan la tabla."""
    return recortar(x, n).replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")

def briefing(proyecto, e, corte=None, para=None, maximo=6500):
    """Briefing de incorporación (≤ 2 páginas) desde estado.json, los registros, el último EVM guardado, las puertas y el radar.
    Devuelve (markdown, datos). Plantilla: pm-progreso-reportes/templates/briefing-incorporacion.md."""
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en); hoy = corte or datetime.date.today().isoformat()
    plantilla_ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pm-progreso-reportes", "templates", "briefing-incorporacion.md")
    if not os.path.exists(plantilla_ruta):
        sys.exit(t(f"Falta la plantilla {plantilla_ruta}: instalar pm-progreso-reportes junto a pm-estado-proyecto.",
                   f"Missing template {plantilla_ruta}: install pm-progreso-reportes next to pm-estado-proyecto."))
    plantilla = open(plantilla_ruta, encoding="utf-8").read()
    regs = {r: _filas(proyecto, r) for r in E.REGISTROS}
    ab = lambda reg: [f for f in regs.get(reg, []) if f.get("estado") in (E.REGISTROS[reg].get("abiertos") or [])]
    roles = e.get("roles", {}) or {}; et = e.get("etapa_actual", {}) or {}
    st = None
    if para:
        st = next((f for f in regs.get("stakeholders", []) if f.get("id") == para), None)
        if not st: sys.exit(t(f"No existe {para} en stakeholders.csv (usar el id ST-### del maestro de interesados).", f"{para} not found in stakeholders.csv (use the ST-### id)."))
    rd = datos_radar(proyecto, e, hoy, limite=0)
    ev_archivo, ev = evm_ultimo(proyecto, hoy)
    alto = E.monto((e.get("umbrales_riesgo") or {}).get("alto")) or E.UMBRAL_RIESGO_ALTO
    def mas(n, k): return [t(f"- … y {n - k} más.", f"- … and {n - k} more.")] if n > k else []
    def tabla(cab, filas, k):
        if not filas: return []
        return ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)] + ["| " + " | ".join(c) + " |" for c in filas[:k]] + ([""] + mas(len(filas), k) if len(filas) > k else [])
    rol_txt = lambda v: ", ".join(v) if isinstance(v, list) else (v or "")
    nombres_rol = {"ejecutivo": t("ejecutivo", "executive"), "usuario_senior": t("usuario sénior", "senior user"), "proveedor_senior": t("proveedor sénior", "senior supplier"),
                   "gestor_proyecto": t("gestor", "project manager"), "aseguramiento": t("aseguramiento", "assurance"), "autoridad_cambio": t("autoridad de cambio", "change authority"),
                   "product_owner": "product owner", "jefes_equipo": t("jefes de equipo", "team managers"), "soporte": t("soporte", "support")}
    def armar(k):
        s = {}
        tol = e.get("tolerancias", {}) or {}
        tol_txt = " · ".join(f"{n}: " + ", ".join(f"{a}={b}" for a, b in v.items() if b) for n, v in tol.items() if any(v.values())) or t("sin tolerancias fijadas", "no tolerances set")
        pres = {a: b for a, b in (e.get("presupuestos") or {}).items() if b}
        abiertos = ", ".join(f"{r} {n}" for r, n in rd["abiertos"].items()) or t("ninguno", "none")
        s["contexto"] = "\n".join([
            t(f"- **Proyecto:** {_md(e.get('proyecto'), 80)} · fase {e.get('fase')}/{e.get('proceso_actual')} · etapa {et.get('numero')} «{_md(et.get('nombre'), 40)}» ({et.get('inicio', '')} → {et.get('fin_previsto', '') or '—'}) · enfoque {e.get('enfoque_entrega')} (`estado.json`).",
              f"- **Project:** {_md(e.get('proyecto'), 80)} · phase {e.get('fase')}/{e.get('proceso_actual')} · stage {et.get('numero')} «{_md(et.get('nombre'), 40)}» ({et.get('inicio', '')} → {et.get('fin_previsto', '') or '—'}) · approach {e.get('enfoque_entrega')} (`estado.json`)."),
            t("- **Junta y roles:** ", "- **Board and roles:** ") + ("; ".join(f"{nombres_rol.get(r, r)} {_md(rol_txt(v), 60)}" for r, v in roles.items() if rol_txt(v)) or t("sin roles registrados", "no roles recorded")) + ".",
            t("- **Tolerancias:** ", "- **Tolerances:** ") + _md(tol_txt, 300) + ".",
            t("- **Presupuestos de la junta:** ", "- **Board budgets:** ") + (", ".join(f"{a}={b}" for a, b in pres.items()) + t(f" (consumo de cambios: sanidad CAM-03)", " (change consumption: health check CAM-03)") if pres else t("sin fijar", "not set")) + ".",
            t(f"- **Abiertos en los registros:** {abiertos} (`03-control/registros/`).", f"- **Open in the registers:** {abiertos} (`03-control/registros/`)."),
        ] + ([t(f"- **Excepción abierta:** {_md(e['excepcion_abierta'], 20)}.", f"- **Open exception:** {_md(e['excepcion_abierta'], 20)}.")] if e.get("excepcion_abierta") else []))
        if st:
            nombre = st.get("nombre", ""); nl = nombre.lower()
            en_junta = [nombres_rol.get(r, r) for r, v in roles.items() if nl and nl in rol_txt(v).lower()]
            raci = [f for f in regs.get("raci", []) if f.get("stakeholder_id") == st["id"]]
            suyos = lambda reg, col: [f["id"] for f in ab(reg) if nl and nl in (f.get(col) or "").lower()]
            lineas = [t(f"- **{_md(nombre, 60)}** ({st['id']}) · rol en el proyecto: {_md(st.get('rol_proyecto'), 50) or '—'} · organización: {_md(st.get('rol_organizacion'), 50) or '—'}"
                        + (f" · en la junta: {', '.join(en_junta)}" if en_junta else "") + ("" if st.get("confidencial") == "si" else f" · poder {st.get('poder') or '—'}, interés {st.get('interes') or '—'}") + " (`stakeholders.csv`).",
                        f"- **{_md(nombre, 60)}** ({st['id']}) · project role: {_md(st.get('rol_proyecto'), 50) or '—'} · organization: {_md(st.get('rol_organizacion'), 50) or '—'}"
                        + (f" · on the board: {', '.join(en_junta)}" if en_junta else "") + ("" if st.get("confidencial") == "si" else f" · power {st.get('poder') or '—'}, interest {st.get('interes') or '—'}") + " (`stakeholders.csv`)."),
                      t(f"- **Contacto acordado:** {_md(st.get('canal'), 30) or '—'}, {_md(st.get('frecuencia'), 30) or '—'}.", f"- **Agreed contact:** {_md(st.get('canal'), 30) or '—'}, {_md(st.get('frecuencia'), 30) or '—'}.")]
            a_cargo = [(t("acciones", "actions"), suyos("acciones", "responsable")), (t("riesgos", "risks"), suyos("riesgos", "propietario")), ("issues", suyos("issues", "responsable"))]
            lineas.append(t("- **A su cargo:** ", "- **Owned:** ") + ("; ".join(f"{n} {', '.join(ids[:8])}" + (" …" if len(ids) > 8 else "") for n, ids in a_cargo if ids) or t("nada abierto a su nombre", "nothing open in their name")) + ".")
            reglas = {}
            for g in GRUPOS_RADAR:
                for x in rd["items"][g]:
                    if nl and nl in x["responsable"].lower(): reglas.setdefault(x["id"], []).append(x["regla"])
            en_radar = [f"{i} ({', '.join(r)})" for i, r in reglas.items()]
            if en_radar: lineas.append(t("- **En el radar a su nombre** (`estado.py radar`): ", "- **On the radar in their name** (`estado.py radar`): ") + lista_ids(en_radar, 8, L) + ".")
            if raci:
                lineas += ["", t("RACI (`raci.csv`):", "RACI (`raci.csv`):"), ""] + tabla([t("Elemento", "Item"), t("Tipo", "Type"), t("Rol", "Role"), "Id"],
                                                                                   [[_md(f.get("elemento"), 40), f.get("tipo_elemento") or "—", f.get("rol", ""), f["id"]] for f in raci], k)
            else:
                lineas.append(t("- Sin filas en la RACI (pm-interesados).", "- No RACI rows (pm-interesados)."))
            s["rol"] = "\n".join(lineas)
        else:
            s["rol"] = t("Sin destinatario: con `--para ST-###` esta sección muestra su rol, su RACI y lo que tiene a cargo. Roles de la junta: sección 1.",
                         "No recipient: with `--para ST-###` this section shows their role, RACI and what they own. Board roles: section 1.")
        dec = sorted((f for f in regs.get("decisiones", []) if f.get("nivel") in ("junta", "ejecutivo", "capa-negocio")), key=lambda f: (f.get("fecha", ""), f.get("id", "")), reverse=True)
        s["decisiones"] = "\n".join(tabla(["Id", t("Fecha", "Date"), t("Decisión", "Decision"), t("Decidió", "Decided by"), t("Nivel", "Level")],
                                          [[f["id"], f.get("fecha", ""), _md(f.get("decision"), 110), _md(f.get("decidido_por"), 30), f.get("nivel", "")] for f in dec], k)) \
            or t("Sin decisiones de nivel junta, ejecutivo o capa de negocio en `decisiones.csv`.", "No board, executive or business-layer decisions in `decisiones.csv`.")
        riesgos = sorted(ab("riesgos"), key=lambda f: (-(E.monto(f.get("puntuacion")) or 0), f["id"]))
        altos = [f for f in riesgos if (E.monto(f.get("puntuacion")) or 0) >= alto]
        filas = [[f["id"], t("riesgo", "risk"), f"P×I {f.get('puntuacion') or '—'}", _md(f.get("propietario"), 30) or "—", _md(f.get("evento"), 80) + (f" · {f['respuesta']}" if f.get("respuesta") else "")] for f in altos]
        filas += [[f["id"], "issue", f.get("prioridad") or f.get("estado", ""), _md(f.get("responsable"), 30) or t("sin responsable", "no owner"), _md(f.get("titulo"), 80)]
                  for f in sorted(ab("issues"), key=lambda f: (PRIORIDAD.get(f.get("prioridad", ""), 4), f["id"]))]
        decide = {x["id"]: x["responsable"] for x in rd["items"]["decidir"] if x["regla"] == "RAD-01"}
        filas += [[f["id"], t("cambio", "change"), f.get("estado", ""), _md(decide.get(f["id"]) or f.get("decidido_por") or f.get("solicitante"), 30) or "—", _md(f.get("titulo"), 70) + (f" · {t('costo', 'cost')} {f['costo']}" if f.get("costo") else "")]
                  for f in ab("cambios") if f.get("estado") in ("abierto", "en-evaluacion", "pendiente-decision")]
        otros = [f["id"] for f in riesgos if f not in altos]
        s["riesgos"] = "\n".join((tabla(["Id", t("Tipo", "Type"), t("Estado / P×I", "Status / P×I"), t("Responsable", "Owner"), t("Descripción", "Description")], filas, k) or
                                  [t("Sin riesgos altos, issues abiertos ni cambios pendientes.", "No high risks, open issues or pending changes.")])
                                 + ["", t(f"Riesgos altos: P×I ≥ {alto:g} (`riesgos.csv`). Otros riesgos abiertos: ", f"High risks: P×I ≥ {alto:g} (`riesgos.csv`). Other open risks: ")
                                    + (lista_ids(otros, 8, L) if otros else t("ninguno", "none")) + "."])
        if ev:
            num = lambda c, dd=3: _cifra(ev[c], L, dd) if isinstance(ev.get(c), (int, float)) else "—"
            s["desempeno"] = "\n".join([
                t(f"- **Último corte de EVM:** {ev.get('corte', '')} (`03-control/reportes/{ev_archivo}`): SPI {num('SPI')}, CPI {num('CPI')}, EAC {num('EAC', 0)} contra BAC {num('BAC', 0)}; "
                  f"semáforos cronograma={ev.get('semaforo_cronograma', '—')}, costo={ev.get('semaforo_costo', '—')}; excepción prevista: {'sí' if ev.get('excepcion_prevista') else 'no'}.",
                  f"- **Last EVM cut-off:** {ev.get('corte', '')} (`03-control/reportes/{ev_archivo}`): SPI {num('SPI')}, CPI {num('CPI')}, EAC {num('EAC', 0)} against BAC {num('BAC', 0)}; "
                  f"RAG schedule={ev.get('semaforo_cronograma', '—')}, cost={ev.get('semaforo_costo', '—')}; forecast exception: {'yes' if ev.get('excepcion_prevista') else 'no'}."),
                t(f"- Regla del semáforo: verde ≤ 50 % de la tolerancia, ámbar 50–100 %, rojo fuera (excepción a la junta).", "- RAG rule: green ≤ 50 % of tolerance, amber 50–100 %, red outside (exception to the board).")])
        else:
            s["desempeno"] = t("Sin corte de EVM guardado (`evm.py … --guardar`): el pronóstico contra tolerancias no se puede citar.", "No saved EVM cut-off (`evm.py … --guardar`): the forecast against tolerances cannot be cited.")
        arts = sorted(((c, a) for c, a in (e.get("artefactos") or {}).items() if a.get("estado") == "aprobado" or a.get("sha256")), key=lambda x: (x[1].get("fecha", ""), x[0]), reverse=True)
        s["artefactos"] = "\n".join(tabla([t("Clave", "Key"), t("Versión", "Version"), t("Aprobó", "Approved by"), t("Fecha", "Date"), t("Archivo", "File")],
                                          [[_md(c, 40), a.get("version", "") or "—", _md(a.get("aprobado_por") or (t("línea base", "baseline") if a.get("sha256") else ""), 30) or "—",
                                            a.get("fecha", "") or "—", f"`{_md(a.get('copia_congelada') or a.get('ruta'), 70)}`"] for c, a in arts], k)) \
            or t("Ningún artefacto aprobado todavía (`estado.json.artefactos`).", "No approved artifacts yet (`estado.json.artefactos`).")
        prox = rd["proxima_puerta"]
        if prox:
            try:
                import puertas as PU
                hs, _ = PU.evaluar_detalle(proyecto, e, prox)
            except Exception:
                hs = []
            lineas = [t(f"**{prox}** · decide la junta (verificación: `puertas.py verificar {prox}`).", f"**{prox}** · decided by the board (check: `puertas.py verificar {prox}`).")]
            for sev, et_ in (("bloqueo", t("bloqueo", "blocker")), ("condicion", t("condición", "condition"))):
                sel = [h for h in hs if h["severidad"] == sev]
                lineas += [f"- {et_} {h['id']}: {_md(h['mensaje'], 110)}" for h in sel[:k]] + mas(len(sel), k)
            if len(lineas) == 1: lineas.append(t("- Sin bloqueos ni condiciones automáticas.", "- No automatic blockers or conditions."))
            s["puerta"] = "\n".join(lineas)
        else:
            s["puerta"] = t("No corresponde otra puerta (proyecto cerrado).", "No further gate (project closed).")
        pasos = sorted((x for g in ("decidir", "escalar", "desbloquear") for x in rd["items"][g]), key=lambda x: (x["prioridad"], x["fecha"] or "9999-99-99", x["id"]))
        s["pasos"] = "\n".join([f"{n}. P{x['prioridad']} [{x['regla']}] {t(x['grupo'], {'decidir': 'decide', 'escalar': 'escalate', 'desbloquear': 'unblock'}[x['grupo']])} {_md(x['id'], 30)}"
                                + (f" ({x['fecha']})" if x["fecha"] else "") + f" · {_md(x['responsable'], 40)} — {_md(x['que'], 110)} → {_md(x['siguiente'], 110)}" for n, x in enumerate(pasos[:min(k, 5)], 1)]
                               + mas(len(pasos), min(k, 5))) or t("Nada que decidir, escalar ni desbloquear al corte (`estado.py radar`).", "Nothing to decide, escalate or unblock as of the cut-off (`estado.py radar`).")
        intro = t(f"Lectura de 10 minutos al {hoy}, generada desde `estado.json`, los registros, el último corte de EVM, las puertas y el radar (`estado.py briefing`). Cada cifra cita su id o su archivo; borrador hasta que el gestor lo revise.",
                  f"A 10-minute read as of {hoy}, generated from `estado.json`, the registers, the last EVM cut-off, the gates and the radar (`estado.py briefing`). Every figure cites its id or file; draft until the project manager reviews it.")
        md = plantilla
        valores = {"proyecto": recortar(e.get("proyecto"), 80).replace('"', "'"), "corte": hoy, "para": (f"{st['id']} {recortar(st.get('nombre'), 60)}" if st else "").replace('"', "'"),
                   "idioma": L, "intro": intro, **s}
        for clave, v in valores.items(): md = md.replace("{{" + clave + "}}", v)
        return md, s
    for k in (6, 4, 3, 2, 1):
        md, s = armar(k)
        if len(md) <= maximo: break
    datos = {"proyecto": e.get("proyecto"), "corte": hoy, "para": para or "", "caracteres": len(md), "paginas": -(-len(md) // 3500), "radar": rd["totales"],
             "evm": ev_archivo or "", "proxima_puerta": rd["proxima_puerta"]}
    return md, datos

# ------------------------------------------------------------------ estado de productos (product status account): registro de
# productos de PRINCE2 7 (A13) derivado de los registros, sin registro propio. Lo usan pm-paquetes-trabajo (product status
# account), pm-calidad (aceptación), sanidad QUA-04 (WBS) y puertas.py C-07 (cierre). Regla y convenciones: guía de
# pm-paquetes-trabajo §5.
ESTADOS_PRODUCTO = ("no-iniciado", "en-desarrollo", "en-revision", "aprobado", "aceptado", "con-concesion", "fuera-especificacion")
ETQ_PRODUCTO = {"no-iniciado": ("no iniciado", "not started"), "en-desarrollo": ("en desarrollo", "in development"),
                "en-revision": ("en revisión", "in quality review"), "aprobado": ("aprobado", "approved"), "aceptado": ("aceptado", "accepted"),
                "con-concesion": ("con concesión", "concession"), "fuera-especificacion": ("fuera de especificación", "off-specification")}
B_TERMINADO = {"done", "terminado", "terminada", "hecho", "hecha", "completado", "completada", "cerrado", "cerrada", "aceptado", "aceptada"}  # = QUA-01
B_REVISION = {"review", "in-review", "en-revision", "revision", "revisión", "en-revisión"}
B_DESARROLLO = {"in-progress", "en-curso", "en-progreso", "en-desarrollo", "doing", "wip"}
Q_APROBADO = ("aprobado", "aprobado-con-observaciones")
DISCREPANCIAS = {   # código: (texto es, texto en, control de la sanidad que lo vigila)
    "terminado-sin-revision": ("terminado en {f} sin revisión de calidad aprobada", "done in {f} without an approved quality review", "QUA-01"),
    "aceptado-sin-revision": ("aceptado ({x}) sin revisión de calidad aprobada", "accepted ({x}) without an approved quality review", "QUA-04"),
    "recibido-sin-revision": ("{x} recibido sin revisión de calidad aprobada del producto", "{x} received without an approved quality review of the product", "QUA-04"),
    "rechazo-sin-tratamiento": ("{x} rechazada sin issue, acción o cambio que la trate", "{x} rejected with no issue, action or change treating it", "QUA-03"),
    "revision-vencida": ("{x} vencida (prevista {f})", "{x} overdue (planned {f})", "QUA-02"),
}

def _moscow(v):
    x = re.sub(r"[\s_]+", "-", (v or "").strip().lower()).replace("'", "")
    for k, al in (("must", ("must", "m", "must-have", "obligatorio", "imprescindible")), ("should", ("should", "s", "should-have", "deberia", "debería")),
                  ("could", ("could", "c", "could-have", "opcional", "podria", "podría")), ("wont", ("wont", "w", "wont-have", "no-ahora", "excluido"))):
        if x in al: return k
    return ""

def _patron_backlog(bid):
    """Misma regla que QUA-01: el id completo o la clave corta N-M (p. ej. «historia 1-3»)."""
    corto = (re.match(r"^(\d+-\d+)(?:-|$)", bid) or [None, None])[1]
    return re.compile(rf"(?<![\w-]){re.escape(bid)}(?![\w-])" + (rf"|(?<![\w.-]){re.escape(corto)}(?![\w-]|\.\d|\d)" if corto else ""))

def _patron_wbs(codigo):
    """Un elemento de la WBS se cita por su código precedido de «WBS», «producto(s)» o «paquete(s)» (también en listas:
    «productos 3.1, 3.2 y 4.1»)."""
    item = r"\d+(?:\.\d+)*"
    return re.compile(rf"(?i)\b(?:wbs|productos?|products?|paquetes?|packages?)\s+(?:{item}\s*(?:,|;|\by\b|\be\b|\band\b)\s*)*"
                      + re.escape(codigo) + r"(?!\d|\.\d)")

def _fisico(estado):
    x = (estado or "").strip().lower()
    return "terminado" if x in B_TERMINADO else "en-revision" if x in B_REVISION else "en-desarrollo" if x in B_DESARROLLO else ""

def productos(proyecto, e, corte=None, fuente="auto", alcance="proyecto", must=True):
    """Estado de cada producto al corte, derivado de backlog.csv o wbs.csv, calidad.csv, issues.csv, acciones.csv,
    cambios.csv, decisiones.csv (recepción de paquetes) y las aceptaciones de estado.json. Devuelve un dict con
    `productos`, `conteos` (suman `total`), `discrepancias`, `paquetes` y `must` (requisitos y productos Must sin aceptar).
    Sin `corte` no se filtra por fecha (lo usa la verificación de puertas); las vencidas se miden contra hoy."""
    import csv
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en); hoy = corte or datetime.date.today().isoformat(); lim = corte or "9999-12-31"
    pl = os.path.join(proyecto, "02-planificacion")
    univ = {"backlog": [], "wbs": []}
    pb = os.path.join(pl, "backlog.csv")
    if os.path.exists(pb):
        for b in csv.DictReader(open(pb, encoding="utf-8")):
            bid = (b.get("id") or "").strip()
            if not bid or "{{" in bid or (b.get("tipo") or "historia").strip().lower() in ("epica", "épica", "epic") or (b.get("estado") or "").startswith("retirada"): continue
            univ["backlog"].append({"id": bid, "clave": (re.match(r"^(\d+-\d+)(?:-|$)", bid) or [None, bid])[1], "titulo": b.get("titulo", ""),
                                    "fuente": "backlog", "prioridad": _moscow(b.get("moscow")) or _moscow(b.get("prioridad")),
                                    "estado_registrado": (b.get("estado") or "").strip(), "grupo": [b.get("release", ""), b.get("iteracion", "")],
                                    "pbs": (b.get("producto_pbs") or "").strip(), "_pat": _patron_backlog(bid)})
    pw = os.path.join(pl, "wbs.csv")
    if os.path.exists(pw):
        filas = [r for r in csv.DictReader(open(pw, encoding="utf-8")) if (r.get("codigo") or "").strip()]
        cods = [r["codigo"].strip() for r in filas]
        for r in filas:
            c = r["codigo"].strip()
            if (r.get("tipo") or "").strip() == "hito" or any(x.startswith(c + ".") for x in cods): continue   # hojas: paquetes y productos sin hijos
            univ["wbs"].append({"id": c, "clave": c, "titulo": r.get("nombre", ""), "fuente": "wbs", "prioridad": "", "estado_registrado": "",
                                "grupo": [c], "pbs": c, "_pat": _patron_wbs(c)})
    if fuente == "auto": fuente = "backlog" if univ["backlog"] else "wbs"
    regs = {r: _filas(proyecto, r) for r in ("calidad", "issues", "acciones", "cambios", "decisiones")}
    q_txt = [(q, " ".join(str(q.get(k, "")) for k in ("producto", "criterios", "notas"))) for q in regs["calidad"] if q.get("estado") != "cancelada"]
    txt_fila = lambda f: " ".join(str(v) for v in f.values())
    trata = " ".join(txt_fila(f) for r in ("issues", "acciones", "cambios") for f in regs[r])
    arts = e.get("artefactos", {}) or {}
    aprobado_al = lambda a: bool(a) and a.get("estado") == "aprobado" and (a.get("fecha") or "") <= lim
    proy_acc = arts.get("registro-aceptacion") if aprobado_al(arts.get("registro-aceptacion")) else None
    # paquetes de trabajo: productos que cita la descripción (alcance por ids) y su recepción en decisiones.csv
    wps = {}
    for k, a in sorted(arts.items()):
        if not re.match(r"^WP-\d{3}$", k): continue
        txt = ""
        try:
            if not a.get("externo") and a.get("ruta"): txt = open(os.path.join(proyecto, a["ruta"]), encoding="utf-8", errors="replace").read()
        except OSError: pass
        rec = [d for d in regs["decisiones"] if re.search(rf"(?<![\w-]){k}(?![\w-])", d.get("decision", "")) and (d.get("fecha") or "") <= lim
               and re.search(r"recib|received|\bacept(?:ad[oa]|o)\b|\baccepted\b", d.get("decision", ""), re.I) and not (d.get("decision") or "").startswith("aprobado ")]
        wps[k] = {"id": k, "texto": txt, "autorizado": aprobado_al(a), "recepcion": rec[-1].get("id", "") if rec else "", "productos": []}
    out = []
    for p in univ["backlog"] + univ["wbs"]:
        pat = p.pop("_pat")
        qs = sorted((q for q, tx in q_txt if pat.search(tx) and not (q.get("estado") == "completada" and (q.get("fecha_real") or "") > lim)),
                    key=lambda q: (q.get("fecha_real") or q.get("fecha_prevista") or "", q.get("id", "")))   # una revisión hecha después del corte no existía
        hechas = [q for q in qs if q.get("estado") == "completada"]
        pend = [q for q in qs if q not in hechas]
        ult = hechas[-1] if hechas else None
        aprob = ult if ult and ult.get("resultado") in Q_APROBADO else None
        ids_q = [q.get("id", "") for q in qs]
        cita = lambda f: pat.search(" ".join(str(f.get(c, "")) for c in ("titulo", "descripcion", "decision", "notas"))) or any(
            re.search(rf"(?<![\w-]){i}(?![\w-])", txt_fila(f)) for i in ids_q if i)
        offs = [f for f in regs["issues"] if f.get("tipo") == "fuera-especificacion" and (f.get("fecha") or "") <= lim and cita(f)]
        off_ab = [f for f in offs if f.get("estado") in E.REGISTROS["issues"]["abiertos"]]
        conc = [f for f in offs if f not in off_ab and re.search(r"concesi|concession", txt_fila(f), re.I)]
        claves = {p["id"].lower(), p["clave"].lower()}
        acc_k = next((k for k, a in sorted(arts.items()) if k.lower().startswith("aceptacion-") and k.lower()[11:] in claves and aprobado_al(a)), None)
        acc = None
        if acc_k: acc = {"clave": acc_k, "por": arts[acc_k].get("aprobado_por", ""), "fecha": arts[acc_k].get("fecha", "")}
        elif proy_acc and aprob and not pend and (aprob.get("fecha_real") or "") <= (proy_acc.get("fecha") or ""):
            acc = {"clave": "registro-aceptacion", "por": proy_acc.get("aprobado_por", ""), "fecha": proy_acc.get("fecha", "")}
        fis = _fisico(p["estado_registrado"])
        paq = [w["id"] for w in wps.values() if pat.search(w["texto"])]
        for w in paq: wps[w]["productos"].append(p["clave"])
        disc = []
        if off_ab: est = "fuera-especificacion"
        elif acc: est = "aceptado"
        elif ult and ult.get("resultado") == "rechazado" and not pend: est = "con-concesion" if conc else "fuera-especificacion"
        elif aprob and not pend: est = "aprobado"
        elif pend or fis in ("en-revision", "terminado"): est = "en-revision"
        elif fis == "en-desarrollo" or any(wps[w]["autorizado"] for w in paq): est = "en-desarrollo"
        else: est = "no-iniciado"
        if fis == "terminado" and not aprob: disc.append(("terminado-sin-revision", {"f": p["fuente"] + ".csv"}))
        if acc_k and not aprob: disc.append(("aceptado-sin-revision", {"x": acc_k}))
        for w in paq:
            if wps[w]["recepcion"] and not aprob: disc.append(("recibido-sin-revision", {"x": f"{w} ({wps[w]['recepcion']})"}))
        for q in hechas:
            if q.get("resultado") == "rechazado" and not re.search(rf"(?<![\w-]){q.get('id')}(?![\w-])", trata): disc.append(("rechazo-sin-tratamiento", {"x": q.get("id")}))
        for q in pend:
            if q.get("estado") in ("planificada", "en-curso") and q.get("fecha_prevista") and q["fecha_prevista"] < hoy: disc.append(("revision-vencida", {"x": q.get("id"), "f": q["fecha_prevista"]}))
        p.update({"estado": est, "fisico": fis, "paquetes": paq, "q": ids_q, "q_vigente": (ult or {}).get("id", ""), "resultado": (ult or {}).get("resultado", ""),
                  "aprobado": f"{aprob.get('aprobador', '')} · {aprob.get('fecha_real', '')}".strip(" ·") if aprob else "",
                  "aceptado": f"{acc['por']} · {acc['fecha']} ({acc['clave']})" if acc else "",
                  "issues": [f.get("id", "") for f in offs],
                  "discrepancias": [{"codigo": c, "control": DISCREPANCIAS[c][2] if p["fuente"] == "wbs" or DISCREPANCIAS[c][2] != "QUA-04" else "", "texto": t(DISCREPANCIAS[c][0], DISCREPANCIAS[c][1]).format(**{"f": "", "x": "", **kw})} for c, kw in disc]})
        out.append(p)
    sel = [p for p in out if p["fuente"] == fuente]
    if alcance and alcance != "proyecto":
        if re.match(r"^WP-\d{3}$", alcance):
            if alcance not in wps: raise ValueError(t(f"{alcance} no está registrado en estado.json.", f"{alcance} is not recorded in estado.json."))
            sel = [p for p in sel if alcance in p["paquetes"]]
        else:
            a_ = alcance.lower()
            sel = [p for p in sel if any((g or "").strip().lower() == a_ for g in p["grupo"]) or (p["fuente"] == "wbs" and p["id"].startswith(alcance + "."))]
            if not sel: raise ValueError(t(f"Alcance «{alcance}» sin productos: usar proyecto, WP-###, una release o iteración de backlog.csv o un código de la WBS.",
                                           f"Scope «{alcance}» has no products: use proyecto, WP-###, a backlog.csv release or iteration, or a WBS code."))
    conteos = {s: sum(1 for p in sel if p["estado"] == s) for s in ESTADOS_PRODUCTO}
    # Must sin aceptar (C-07): requisitos Must (propia o la más alta de sus historias) cuyos productos no están todos aceptados
    est_de = {p["id"]: p for p in out}
    ids_sel = {p["id"] for p in sel}
    must_p = [p["clave"] for p in sel if p["fuente"] == "backlog" and p["prioridad"] == "must" and p["estado"] not in ("aceptado", "con-concesion")]
    must_r = []
    try:
        if not must: raise StopIteration
        import especificacion as SP
        idx, _ = SP.obtener(proyecto)
        for q in idx.get("requisitos", []):
            if q.get("tipo") not in ("REQ", "FR", "NFR"): continue
            prods = [est_de[h] for h in q.get("historias", []) if h in est_de] or [est_de[c] for c in q.get("paquetes_wbs", []) if c in est_de]
            prio = _moscow(q.get("prioridad")) or ("must" if any(x["prioridad"] == "must" for x in prods) else "")
            if prio != "must": continue
            falta = [x for x in prods if x["estado"] not in ("aceptado", "con-concesion")]
            if (falta or not prods) and (alcance in ("", "proyecto", None) or any(x["id"] in ids_sel for x in prods)):
                must_r.append({"id": q["id"], "productos": [f"{x['clave']} {E.t(L, *ETQ_PRODUCTO[x['estado']])}" for x in falta]})
    except BaseException:
        pass
    for p in out: p.pop("grupo", None)
    return {"proyecto": e.get("proyecto"), "corte": corte or "", "hoy": hoy, "fuente": fuente, "alcance": alcance or "proyecto", "total": len(sel), "conteos": conteos,
            "productos": sel, "discrepancias": [{"producto": p["clave"], **d} for p in sel for d in p["discrepancias"]],
            "paquetes": [{k: v for k, v in w.items() if k != "texto"} for w in wps.values()],
            "must": {"requisitos": must_r, "productos": must_p}}

def texto_productos(d, idioma="es", maximo=40):
    t = lambda es, en: E.t(idioma, es, en)
    lista = lambda xs, n=8: ", ".join(xs[:n]) + (t(f" … y {len(xs) - n} más", f" … and {len(xs) - n} more") if len(xs) > n else "")
    al = t(f"al {d['corte']}", f"as of {d['corte']}") if d["corte"] else t("sin fecha de corte", "no cut-off date")
    x = [t(f"Estado de productos {al} · fuente {d['fuente']}.csv · alcance {d['alcance']} · {d['total']} productos",
           f"Product status {al} · source {d['fuente']}.csv · scope {d['alcance']} · {d['total']} products"),
         " · ".join(f"{E.t(idioma, *ETQ_PRODUCTO[s])} {d['conteos'][s]}" for s in ESTADOS_PRODUCTO) + f" = {sum(d['conteos'].values())}"]
    ds = d["discrepancias"]
    x.append(t(f"Diferencias entre lo registrado y lo físico: {len(ds)}", f"Recorded vs physical discrepancies: {len(ds)}"))
    x += [f"  {z['producto']} · {z['texto']}" + (f" ({z['control']})" if z["control"] else "") for z in ds[:maximo]]
    if len(ds) > maximo: x.append(t(f"  … y {len(ds) - maximo} más (--json)", f"  … and {len(ds) - maximo} more (--json)"))
    m = d["must"]
    if m["requisitos"] or m["productos"]:
        x.append(t("Must sin aceptar (C-07 en autorizar-cierre): ", "Must not accepted (C-07 at autorizar-cierre): ")
                 + (t(f"requisitos {lista([r['id'] for r in m['requisitos']])}", f"requirements {lista([r['id'] for r in m['requisitos']])}") if m["requisitos"] else "")
                 + ("; " if m["requisitos"] and m["productos"] else "")
                 + (t(f"productos {lista(m['productos'])}", f"products {lista(m['productos'])}") if m["productos"] else ""))
    x.append(t("Detalle:", "Detail:"))
    for p in d["productos"][:maximo]:
        q = f"{p['q_vigente']} {p['resultado']}".strip() if p["q_vigente"] else t("sin revisión", "no review")
        x.append(f"  {p['clave']} · {recortar(p['titulo'], 40)}" + (f" · {p['prioridad'].capitalize()}" if p["prioridad"] else "")
                 + (f" · {', '.join(p['paquetes'])}" if p["paquetes"] else "") + (f" · {p['estado_registrado']}" if p["estado_registrado"] else "")
                 + f" → {E.t(idioma, *ETQ_PRODUCTO[p['estado']])} · {q}" + (f" · {p['aceptado'].split(' · ')[-1]}" if p["aceptado"] else ""))
    if len(d["productos"]) > maximo: x.append(t(f"  … y {len(d['productos']) - maximo} más (--max 0 o --json)", f"  … and {len(d['productos']) - maximo} more (--max 0 or --json)"))
    return "\n".join(x)

def markdown_productos(proyecto, d, e):
    """Borrador del product status account (pm-paquetes-trabajo/templates/product-status-account.md) con lo derivable."""
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en); c = lambda v: _md(v, 120) or "—"
    fuentes = [f"02-planificacion/{d['fuente']}.csv", "03-control/registros/calidad.csv", "issues.csv", "decisiones.csv", "estado.json (aceptaciones)"]
    x = ["---", "tipo: product-status-account", f'proyecto: "{e.get("proyecto", "")}"', 'version: "0.1"', f'fecha: "{d["corte"] or d["hoy"]}"', 'autor: "estado.py productos"',
         "estado: borrador", 'aprobado_por: ""', f'idioma: "{L}"', "---", "",
         f"# Estado de productos · Product status account — {_md(e.get('proyecto', ''), 120)}", "",
         t("> Borrador derivado de los registros con `estado.py productos`; cada fila cita su fuente (Q-###, I-###, clave de aceptación). Lo que no se deriva queda `[por confirmar]`.",
           "> Draft derived from the registers with `estado.py productos`; every row cites its source (Q-###, I-###, acceptance key). What cannot be derived stays `[por confirmar]`."), "",
         "## 1. Alcance del informe / Report scope", "", f"**Fecha de corte / Cut-off date:** {d['corte'] or t('sin corte (registros vigentes al ', 'none (registers as of ') + d['hoy'] + ')'}", "",
         f"**Alcance / Scope:** {d['alcance']} ({d['fuente']}.csv)", "", "**Motivo / Reason:** [por confirmar]", "", f"**Fuentes / Sources:** {'; '.join(fuentes)}", "",
         "## 2. Resumen / Summary", "", "| Estado / Status | Cantidad / Count |", "|---|---|"]
    x += [f"| {ETQ_PRODUCTO[s][0].capitalize()} / {ETQ_PRODUCTO[s][1].capitalize()} | {d['conteos'][s]} |" for s in ESTADOS_PRODUCTO]
    x += [f"| **Total** | **{d['total']}** |", "", "## 3. Detalle por producto / Product detail", "",
          "| Id / Id | Producto / Product | Paquete / Work package | Versión / Version | Descripción aprobada el / Description approved on | Estado / Status | Actividad de calidad (Q-nnn) / Quality activity | Resultado / Result | Aprobado por · fecha / Approved by · date | Aceptado por · fecha / Accepted by · date | Observaciones / Notes |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in d["productos"]:
        obs = "; ".join([t(f"registrado: {p['estado_registrado']}", f"recorded: {p['estado_registrado']}")] if p["estado_registrado"] else [])
        obs = "; ".join([o for o in [obs] + [z["texto"] for z in p["discrepancias"]] + ([", ".join(p["issues"])] if p["issues"] else []) if o])
        x.append(f"| {c(p['clave'])} | {c(p['titulo'])} | {c(', '.join(p['paquetes']) or p['pbs'])} | — | — | {E.t(L, *ETQ_PRODUCTO[p['estado']])} | {c(', '.join(p['q']))} | {c(p['resultado'])} | {c(p['aprobado'])} | {c(p['aceptado'])} | {c(obs)} |")
    off = sorted({i for p in d["productos"] for i in p["issues"]})
    venc = [f"{z['producto']} ({z['texto']})" for z in d["discrepancias"] if z["codigo"] == "revision-vencida"]
    otras = [f"{z['producto']}: {z['texto']}" + (f" ({z['control']})" if z["control"] else "") for z in d["discrepancias"] if z["codigo"] != "revision-vencida"]
    x += ["", "## 4. Desviaciones y pendientes / Deviations and open items", "",
          f"**Fuera de especificación / Off-specifications:** {', '.join(off) or t('ninguno', 'none')}", "",
          f"**Productos con actividades de calidad vencidas / Products with overdue quality activities:** {_md('; '.join(venc), 600) or t('ninguno', 'none')}", "",
          "**Productos sin descripción aprobada / Products without approved description:** [por confirmar]", "",
          f"**Discrepancias entre registro y estado físico / Register vs. physical state discrepancies:** {_md('; '.join(otras), 1500) or t('ninguna', 'none')}", "",
          "## 5. Estado de paquetes de trabajo / Work package status", "",
          "| Paquete / Work package | Gestor de equipo / Team manager | Estado / Status | Pronóstico vs. tolerancias / Forecast vs. tolerances | Último checkpoint / Last checkpoint | Issues y riesgos abiertos / Open issues and risks |",
          "|---|---|---|---|---|---|"]
    import glob
    for w in d["paquetes"]:
        cp = sorted(glob.glob(os.path.join(proyecto, "03-control", "reportes", f"*checkpoint-{w['id']}*.md")))
        est = t(f"completado ({w['recepcion']})", f"completed ({w['recepcion']})") if w["recepcion"] else t("autorizado", "authorized") if w["autorizado"] else t("sin autorizar", "not authorized")
        x.append(f"| {w['id']} ({c(', '.join(w['productos']))}) | [por confirmar] | {est} | [por confirmar] | {c(os.path.basename(cp[-1]) if cp else '')} | [por confirmar] |")
    if not d["paquetes"]: x.append("| — | — | — | — | — | — |")
    m = d["must"]
    x += ["", "## 6. Conclusión y siguiente paso / Conclusion and next step", "",
          (t("Must sin aceptar: ", "Must not accepted: ") + _md("; ".join(([t("requisitos ", "requirements ") + ", ".join(r["id"] for r in m["requisitos"])] if m["requisitos"] else [])
                                                                       + ([t("productos ", "products ") + ", ".join(m["productos"])] if m["productos"] else [])), 600) + ". "
           if m["requisitos"] or m["productos"] else "") + "[por confirmar]", "",
          "## Lista de verificación / Checklist",
          "- [ ] Todos los productos del plan vigente aparecen en la tabla, sin omisiones.",
          "- [ ] Cada fila cita la actividad de calidad y la aprobación que la sustenta; vacíos reales, no inferidos.",
          "- [ ] Los conteos del resumen coinciden con la tabla de detalle.",
          "- [ ] Off-specifications con decisión o marcados como pendientes.",
          "- [ ] Fecha de corte y fuentes declaradas.",
          "- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.", ""]
    return "\n".join(x)

# --- Datos del período → tablero (pm-visuales) y highlight (pm-progreso-reportes), con la cadena de reporte verificada ---
# Reglas: pm-progreso-reportes/references/guia.md §8, §9 y §14 (semáforos por regla, productos del período, juicio del
# gestor); pm-visuales/references/guia.md §3 (bloque datos-tablero). PRINCE2 §4.c.3 (cadena de informes) y §4.a (tolerancias).
OBJETIVOS = ("tiempo", "costo", "alcance", "calidad", "beneficios", "riesgo", "sostenibilidad")
GRAVEDAD = {"na": -1, "verde": 0, "ambar": 1, "rojo": 2}
NOMBRES_OBJ = {"tiempo": ("Tiempo", "Time"), "costo": ("Costo", "Cost"), "alcance": ("Alcance", "Scope"), "calidad": ("Calidad", "Quality"),
               "beneficios": ("Beneficios", "Benefits"), "riesgo": ("Riesgo", "Risk"), "sostenibilidad": ("Sostenibilidad", "Sustainability")}
RAG_TXT = {"verde": ("verde", "green"), "ambar": ("ámbar", "amber"), "rojo": ("rojo", "red"), "na": ("[por confirmar]", "[to be confirmed]")}

def _rag(v):
    v = str(v or "").strip().lower().replace("á", "a")
    return {"green": "verde", "amber": "ambar", "red": "rojo", "n/a": "na", "": ""}.get(v, v)

def _n(x, L, dec=None):
    """Cifra con la convención del idioma; sin decimales si es entera (dec=None)."""
    if dec is None: dec = 0 if float(x) == int(float(x)) else 1
    return _cifra(float(x), L, dec)

def leer_juicio(ruta, L):
    """Insumo del gestor (JSON): objetivos sin regla (alcance predictivo, beneficios, sostenibilidad; tiempo y costo sin corte
    de EVM), notas, hitos, decisiones, iteraciones (nombre y plan de cada corte de avance-bmad.csv), comentario, moneda y fuentes."""
    if not ruta: return {}
    try: j = json.load(open(ruta, encoding="utf-8"))
    except (OSError, ValueError) as x: sys.exit(E.t(L, f"No se pudo leer el juicio del gestor {ruta}: {x}", f"Could not read the manager's judgement {ruta}: {x}"))
    if not isinstance(j, dict): sys.exit(E.t(L, f"{ruta}: se espera un objeto JSON.", f"{ruta}: a JSON object is expected."))
    for k, o in (j.get("objetivos") or {}).items():
        if k not in OBJETIVOS or not isinstance(o, dict) or _rag(o.get("rag")) not in ("", *GRAVEDAD):
            sys.exit(E.t(L, f"{ruta}: objetivo inválido {k!r} (claves {', '.join(OBJETIVOS)}; rag verde|ambar|rojo|na).",
                         f"{ruta}: invalid objective {k!r} (keys {', '.join(OBJETIVOS)}; rag verde|ambar|rojo|na)."))
    return j

def datos_periodo(proyecto, e, desde, corte, proximo="", juicio=None, con_radar=True):
    """Datos del período: siete objetivos con semáforo por regla (tiempo y costo del último corte de EVM del período, riesgo
    con los umbrales de estado.json, calidad con QUA-01…03 y fuera de especificación, alcance con el EVM ágil) o por juicio
    del gestor (marcado), productos aceptados, cambios y fuera de especificación del período, decisiones, iteraciones y el
    bloque del tablero. El juicio puede empeorar un semáforo derivado, nunca mejorarlo."""
    import csv
    import registro as RG
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en); j = juicio or {}; jo = j.get("objetivos") or {}
    regs = {r: _filas(proyecto, r) for r in E.REGISTROS}
    ab = lambda reg: [f for f in regs.get(reg, []) if f.get("estado") in (E.REGISTROS[reg].get("abiertos") or [])]
    en_periodo = lambda f: desde <= (f or "")[:10] <= corte
    U = {k: E.monto((e.get("umbrales_riesgo") or {}).get(k)) or d for k, d in (("alto", E.UMBRAL_RIESGO_ALTO), ("medio", E.UMBRAL_RIESGO_MEDIO))}
    res = RG.resumen(proyecto, corte); res["fecha_corte"] = corte
    avisos = []
    ev_arch, ev = evm_ultimo(proyecto, corte)
    if ev and str(ev.get("corte") or ev_arch[4:14]) < desde:
        avisos.append(t(f"El último corte de EVM ({ev_arch}) es anterior al período: tiempo y costo quedan sin regla (evm.py … --guardar --corte {corte}).",
                        f"The last EVM cut-off ({ev_arch}) predates the period: time and cost have no rule (evm.py … --guardar --corte {corte})."))
        ev_arch, ev = None, {}
    mon = (str(j.get("moneda") or "").strip() + " ") if j.get("moneda") else ""
    num = lambda c, d=3: _cifra(float(ev[c]), L, d)
    tol = lambda nivel, c: str(((e.get("tolerancias") or {}).get(nivel) or {}).get(c) or "")
    av = []
    p_av = os.path.join(proyecto, "03-control", "reportes", "avance-bmad.csv")
    if os.path.exists(p_av): av = [f for f in csv.DictReader(open(p_av, encoding="utf-8")) if (f.get("fecha") or "") <= corte]
    pts = lambda f, c: float(f.get(c) or 0)
    derivados = {}   # clave: (rag, pronóstico corto, cifra y umbral, fuente)
    color = lambda s: s if s in ("verde", "ambar", "rojo") else None
    if ev and color(ev.get("semaforo_cronograma")):
        sv = max(float(ev.get("SV_pct_del_PV") or 0), 0); tp = ev.get("tol_plazo_pct")
        derivados["tiempo"] = (ev["semaforo_cronograma"], f"SPI {num('SPI')}" + (t(f" · desvío {_n(sv, L, 1)} % del PV", f" · {_n(sv, L, 1)} % of PV behind") if sv else ""),
                               f"SPI {num('SPI')}; " + (t(f"desvío de {_n(sv, L, 1)} % del PV contra una tolerancia de {_n(tp, L)} % (ámbar = 50–100 %)",
                                                          f"{_n(sv, L, 1)} % of PV behind against a {_n(tp, L)} % tolerance (amber = 50–100 %)") if tp is not None
                                                        else t("sin tolerancia en %: umbrales de referencia 0,95 / 0,85", "no % tolerance: reference thresholds 0.95 / 0.85")), ev_arch)
    if ev and color(ev.get("semaforo_costo")):
        sc = float(ev.get("sobrecosto_pct") or 0); tc = ev.get("tol_costo_pct"); sg = "+" if sc > 0 else ""
        derivados["costo"] = (ev["semaforo_costo"], f"CPI {num('CPI')} · EAC {mon}{num('EAC', 0)} ({sg}{_n(sc, L, 1)} %)",
                              f"CPI {num('CPI')}; EAC {mon}{num('EAC', 0)}, " + (t(f"sobrecosto de {_n(sc, L, 1)} %", f"overrun of {_n(sc, L, 1)} %") if sc > 0 else t(f"{_n(-sc, L, 1)} % bajo el BAC", f"{_n(-sc, L, 1)} % under BAC"))
                              + (t(f" contra {_n(tc, L)} %", f" against {_n(tc, L)} %") if tc is not None else t(" (umbrales de referencia 0,95 / 0,85)", " (reference thresholds 0.95 / 0.85)")), ev_arch)
    if ev and color(ev.get("semaforo_alcance")):
        x = float(ev.get("alcance_no_entregable_pct") or 0)
        derivados["alcance"] = (ev["semaforo_alcance"], t(f"{_n(x, L, 1)} % del alcance no entra", f"{_n(x, L, 1)} % of scope does not fit"),
                                t(f"EVM ágil: {_n(x, L, 1)} % del alcance no entra contra {_n(ev.get('pct_no_must') or 0, L)} % Should/Could", f"agile EVM: {_n(x, L, 1)} % of scope does not fit against {_n(ev.get('pct_no_must') or 0, L)} % Should/Could"), ev_arch)
    q = regs.get("calidad", [])
    aprob = [f for f in q if f.get("estado") == "completada" and f.get("resultado") in ("aprobado", "aprobado-con-observaciones")]
    if q:
        qua = []
        try:
            import sanidad as SA
            SA.H.clear(); SA.chk_calidad(proyecto, e, regs, corte); qua = sorted({h["codigo"] for h in SA.H if h["codigo"].startswith("QUA")}); SA.H.clear()
        except Exception:
            pass
        oe = [f["id"] for f in ab("issues") if f.get("tipo") == "fuera-especificacion"]
        extra = ([t(f"{len(oe)} fuera de especificación abierto(s) ({lista_ids(oe, 4, L)})", f"{len(oe)} open off-specification(s) ({lista_ids(oe, 4, L)})")] if oe else []) + ([", ".join(qua)] if qua else [])
        derivados["calidad"] = ("ambar" if (oe or qua) else "verde",
                                t(f"{len(aprob)} revisiones aprobadas", f"{len(aprob)} reviews approved") + "".join(f"; {x}" for x in extra),
                                t(f"{len(aprob)} revisiones completadas y aprobadas, {len(ab('calidad'))} abiertas", f"{len(aprob)} reviews completed and approved, {len(ab('calidad'))} open") + "".join(f"; {x}" for x in extra),
                                t("registro.py resumen · sanidad QUA", "registro.py resumen · health check QUA"))
    rab = ab("riesgos"); pxi = lambda f: E.monto(f.get("puntuacion")) or 0
    altos = sorted((f for f in rab if pxi(f) >= U["alto"]), key=lambda f: (-pxi(f), f["id"]))
    rotos = [f["id"] for f in altos if not f.get("respuesta") or not f.get("propietario")]
    sin_r = [f["id"] for f in rab if not f.get("respuesta")]; sin_p = [f["id"] for f in rab if not f.get("propietario")]
    derivados["riesgo"] = ("rojo" if rotos else "ambar" if altos else "verde",
                           t(f"alto sin respuesta o sin propietario: {lista_ids(rotos, 4, L)}", f"high risk with no response or owner: {lista_ids(rotos, 4, L)}") if rotos
                           else t(f"{len(altos)} {'alto' if len(altos) == 1 else 'altos'} con respuesta ({lista_ids([f['id'] for f in altos], 4, L)})", f"{len(altos)} high {'risk' if len(altos) == 1 else 'risks'} with a response ({lista_ids([f['id'] for f in altos], 4, L)})") if altos
                           else t("sin riesgos altos abiertos", "no open high risks"),
                           t(f"{len(rab)} riesgo(s) abierto(s), {len(altos)} alto(s) (P×I ≥ {U['alto']:g}), {len(sin_r)} sin respuesta, {len(sin_p)} sin propietario",
                             f"{len(rab)} open risk(s), {len(altos)} high (P×I ≥ {U['alto']:g}), {len(sin_r)} with no response, {len(sin_p)} with no owner"),
                           "registro.py resumen")
    objetivos = []
    for c in OBJETIVOS:
        jc = jo.get(c) or {}; jr = _rag(jc.get("rag")); nota = str(jc.get("pronostico") or "").strip()
        te = tol("etapa", c) or str(jc.get("tol_etapa") or ""); tp_ = tol("proyecto", c) or str(jc.get("tol_proyecto") or "")
        if c == "tiempo" and ev.get("tol_plazo_pct") is not None and c in derivados: te = f"±{_n(ev['tol_plazo_pct'], L)} %"
        if c == "costo" and ev.get("tol_costo_pct") is not None and c in derivados: te = f"±{_n(ev['tol_costo_pct'], L)} %"
        if c in derivados:
            rag, pron, cifra, fuente = derivados[c]; base = "regla"
            if jr and GRAVEDAD[jr] > GRAVEDAD[rag]: rag = jr; base = "regla+juicio"
            elif jr and jr != rag:
                avisos.append(t(f"{c}: el semáforo sale de {fuente} ({RAG_TXT[rag][0]}); el juicio ({RAG_TXT.get(jr, (jr,))[0]}) no puede mejorarlo y se ignora.",
                                f"{c}: the RAG comes from {fuente} ({RAG_TXT[rag][1]}); the judgement ({RAG_TXT.get(jr, ('', jr))[1]}) cannot improve it and is ignored."))
            if nota: pron += " · " + nota
        else:
            rag = jr or "na"; pron = nota or t("[por confirmar]", "[to be confirmed]"); base = "juicio" if jc else "sin-dato"
            fuente = t("juicio del gestor", "manager's judgement") if jc else "—"
            apoyo = ""
            if c == "alcance" and av:
                apoyo = t(f"sobre el burn-up: {_n(pts(av[-1], 'puntos_terminados'), L)} de {_n(pts(av[-1], 'puntos_total'), L)} puntos", f"on the burn-up: {_n(pts(av[-1], 'puntos_terminados'), L)} of {_n(pts(av[-1], 'puntos_total'), L)} points")
                fuente = "avance-bmad.csv"
            elif c == "beneficios" and tp_:
                apoyo = t(f"contra la tolerancia de {tp_}", f"against the {tp_} tolerance")
            detalle = str(jc.get("detalle") or pron)
            cifra = (f"{detalle} (" + t("pronóstico del gestor", "manager's forecast") + (f" {apoyo}" if apoyo else "") + ")") if jc else t("sin medida ni juicio registrado", "no measure or judgement recorded")
        objetivos.append({"clave": c, "pronostico": pron, "tol_etapa": te, "tol_proyecto": tp_, "rag": rag, "base": base, "cifra": cifra, "fuente": fuente})
    general = max((o["rag"] for o in objetivos if o["rag"] != "na"), key=lambda r: GRAVEDAD[r], default="na")
    productos = [{"id": f["id"], "producto": f.get("producto", ""), "fecha": f.get("fecha_real", "")} for f in sorted(aprob, key=lambda f: (f.get("fecha_real", ""), f["id"])) if en_periodo(f.get("fecha_real"))]
    cambios = [{"id": f["id"], "titulo": f.get("titulo", ""), "estado": f.get("estado", "")} for f in regs.get("cambios", []) if en_periodo(f.get("fecha")) or en_periodo(f.get("fecha_decision"))]
    fuera_esp = [{"id": f["id"], "titulo": f.get("titulo", ""), "estado": f.get("estado", "")} for f in regs.get("issues", []) if f.get("tipo") == "fuera-especificacion" and en_periodo(f.get("fecha"))]
    proximas = sorted(({"id": f["id"], "responsable": f.get("responsable", ""), "fecha": f.get("fecha_compromiso", ""), "accion": f.get("accion") or f.get("titulo") or f.get("descripcion", "")}
                       for f in ab("acciones") if corte < (f.get("fecha_compromiso") or "") <= (proximo or corte)), key=lambda x: (x["fecha"], x["id"]))
    radar_dec = []
    if con_radar:
        try: radar_dec = [{"id": x["id"], "texto": recortar(x["que"], 160), "fecha_limite": ""} for x in datos_radar(proyecto, e, corte, 0, rapido=True)["items"]["decidir"]]
        except Exception: radar_dec = []
    if "decisiones" in j:
        decisiones = [{"id": str(d.get("id", "")), "texto": str(d.get("texto", "")), "fecha_limite": str(d.get("fecha_limite", ""))} for d in j.get("decisiones") or []]
        fuera = [d["id"] for d in radar_dec if d["id"] not in {x["id"] for x in decisiones}]
        if fuera: avisos.append(t(f"El radar tiene además para decidir: {lista_ids(fuera, 6, L)} (estado.py radar).", f"The radar also lists to decide: {lista_ids(fuera, 6, L)} (estado.py radar)."))
    else:
        decisiones = radar_dec
    # iteraciones: puntos de avance-bmad.csv; nombre y plan de cada corte, del gestor (por defecto, todos los cortes y la velocidad de referencia)
    ji = (j.get("agil") or {}).get("iteraciones")
    por_fecha = {f["fecha"]: f for f in av}
    sel = [(x.get("fecha"), x.get("nombre"), x.get("planificado")) for x in ji] if ji else [(f["fecha"], f["fecha"], None) for f in av]
    falt = [s[0] for s in sel if s[0] not in por_fecha]
    if falt: sys.exit(t(f"Iteraciones del juicio sin fila en avance-bmad.csv al corte: {', '.join(map(str, falt))}.", f"Judgement iterations with no avance-bmad.csv row by the cut-off: {', '.join(map(str, falt))}."))
    vref = (e.get("agil") or {}).get("velocidad_referencia") or 0
    iteraciones, prev = [], 0.0
    for fecha, nombre, plan in sel:
        f = por_fecha[fecha]; acum = pts(f, "puntos_terminados")
        iteraciones.append({"nombre": nombre or fecha, "planificado": plan if plan is not None else vref, "terminado": acum - prev, "alcance_total": pts(f, "puntos_total"), "terminado_acumulado": acum, "fecha": fecha}); prev = acum
    ja = j.get("agil") or {}
    fuentes = "; ".join(["estado.json"] + ([ev_arch] if ev_arch else []) + [t(f"registros al {corte}", f"registers as of {corte}")] + (["avance-bmad.csv"] if av else [])
                        + ([str(j["fuentes"])] if j.get("fuentes") else []))
    tablero = {"proyecto": e.get("proyecto"), "etapa": (e.get("etapa_actual") or {}).get("nombre", ""), "enfoque_entrega": e.get("enfoque_entrega"), "idioma": L,
               "estado": "borrador", "fecha_corte": corte, "periodo_desde": desde, "periodo_hasta": corte, "proximo_hasta": proximo,
               "riesgos": rab, "issues": ab("issues"), "acciones": regs.get("acciones", []), "resumen_registros": res, "umbrales_riesgo": U,
               "objetivos": [{k: o[k] for k in ("clave", "pronostico", "tol_etapa", "tol_proyecto", "rag", "base")} for o in objetivos],
               "hitos": list(j.get("hitos") or []), "decisiones_pendientes": decisiones,
               "agil": {"iteraciones": [{k: x[k] for k in ("nombre", "planificado", "terminado", "alcance_total", "terminado_acumulado")} for x in iteraciones],
                        "ventana_velocidad": 3, "fecha_fija": str(ja.get("fecha_fija") or ""), "fecha_pronostico": str(ja.get("fecha_pronostico") or ""), "must_en_riesgo": list(ja.get("must_en_riesgo") or [])},
               "comentario_gestor": str(j.get("comentario") or t("[por confirmar]", "[to be confirmed]")), "fuentes": fuentes, "fecha_generacion": corte, "confirmado_por": ""}
    return {"proyecto": e.get("proyecto"), "desde": desde, "corte": corte, "proximo": proximo, "idioma": L, "evm": ev_arch or "",
            "evm_datos": {k: ev.get(k) for k in ("SPI", "CPI", "EAC", "BAC", "SV_pct_del_PV", "sobrecosto_pct", "tol_plazo_pct", "tol_costo_pct", "excepcion_prevista", "modo") if k in ev},
            "umbrales_riesgo": U, "objetivos": objetivos, "general": general, "productos_aceptados": productos, "revisiones_aprobadas": len(aprob),
            "cambios": cambios, "fuera_especificacion": fuera_esp, "acciones_vencidas": res.get("acciones", {}).get("vencidas", []),
            "acciones_proximas": proximas, "decisiones": decisiones, "iteraciones": iteraciones, "moneda": mon.strip(), "registros": res,
            "avance": dict(av[-1]) if av else {}, "fuentes": fuentes, "avisos": avisos, "tablero": tablero}

def html_tablero(d):
    """Plantilla de pm-visuales con el bloque datos-tablero reemplazado. Escape único: todo '<' va como \\u003c (JSON válido),
    de modo que ni '</script>' ni '<!--' de un texto de los registros cortan el bloque."""
    T = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pm-visuales", "templates", "tablero-avance.html")
    if not os.path.exists(T): sys.exit(E.t(d["idioma"], f"Falta la plantilla {T}: instalar pm-visuales junto a pm-estado-proyecto.", f"Missing template {T}: install pm-visuales next to pm-estado-proyecto."))
    bloque = json.dumps(d["tablero"], ensure_ascii=False).replace("<", "\\u003c")
    html, n = re.subn(r'(<script type="application/json" id="datos-tablero">)(.*?)(</script>)', lambda m: m.group(1) + bloque + m.group(3), open(T, encoding="utf-8").read(), count=1, flags=re.S)
    if not n: sys.exit(E.t(d["idioma"], f"{T} no tiene el bloque datos-tablero.", f"{T} has no datos-tablero block."))
    return html

def md_highlight(d, e, proyecto):
    """Variante mínima del highlight (secciones [mín] de pm-progreso-reportes/templates/highlight-report.md) con cifras e ids
    del período; la narrativa queda «[por redactar]» para el gestor."""
    L = d["idioma"]; t = lambda es, en: E.t(L, es, en); ev = d["evm_datos"]; et = e.get("etapa_actual") or {}
    PR = t("[por redactar]", "[to be written]"); m = lambda x: _md(x, 140)
    nombre = lambda c: NOMBRES_OBJ[c][0 if L == "es" else 1]; rt = lambda r: RAG_TXT.get(r, (r, r))[0 if L == "es" else 1]
    ob = {o["clave"]: o for o in d["objetivos"]}
    tc = [rt(ob[c]["rag"]) for c in ("tiempo", "costo") if ob[c]["base"] != "sin-dato"]
    res1 = t(f"Estado general **{rt(d['general'])}**.", f"Overall status **{rt(d['general'])}**.")
    if d["evm"] and "SPI" in ev:
        res1 += " " + t(f"Tiempo y costo en {' y '.join(dict.fromkeys(tc))}: SPI {_cifra(ev['SPI'], L, 3)}, CPI {_cifra(ev['CPI'], L, 3)}, EAC {(d['moneda'] + ' ') if d['moneda'] else ''}{_cifra(ev['EAC'], L, 0)}"
                        f" ({'+' if (ev.get('sobrecosto_pct') or 0) > 0 else ''}{_cifra(ev.get('sobrecosto_pct') or 0, L, 1)} %); excepción prevista: {'sí' if ev.get('excepcion_prevista') else 'no'} ({d['evm']}).",
                        f"Time and cost {' and '.join(dict.fromkeys(tc))}: SPI {_cifra(ev['SPI'], L, 3)}, CPI {_cifra(ev['CPI'], L, 3)}, EAC {(d['moneda'] + ' ') if d['moneda'] else ''}{_cifra(ev['EAC'], L, 0)}"
                        f" ({'+' if (ev.get('sobrecosto_pct') or 0) > 0 else ''}{_cifra(ev.get('sobrecosto_pct') or 0, L, 1)} %); forecast exception: {'yes' if ev.get('excepcion_prevista') else 'no'} ({d['evm']}).")
    filas = "\n".join(f"| {nombre(o['clave'])} | {rt(o['rag'])} | {_md(o['cifra'], 300)} | {m(o['fuente'])} |" for o in d["objetivos"])
    hist = "; ".join(f"{p['id']} {m(p['producto'])} ({p['fecha']})" for p in d["productos_aceptados"][:8]) + (t(f" … y {len(d['productos_aceptados']) - 8} más", f" … and {len(d['productos_aceptados']) - 8} more") if len(d["productos_aceptados"]) > 8 else "")
    av = d["avance"]; pts = lambda c: float(av.get(c) or 0)
    ant = [x for x in d["iteraciones"] if x["fecha"] < d["desde"]]
    linea_av = (t(f" · **Puntos terminados:** {_n(pts('puntos_terminados'), L)} de {_n(pts('puntos_total'), L)} ({str(av.get('pct_terminado', '')).replace('.', ',')} %), {_n(pts('puntos_terminados') - (ant[-1]['terminado_acumulado'] if ant else 0), L)} en el período (avance-bmad.csv)",
                  f" · **Points done:** {_n(pts('puntos_terminados'), L)} of {_n(pts('puntos_total'), L)} ({av.get('pct_terminado', '')} %), {_n(pts('puntos_terminados') - (ant[-1]['terminado_acumulado'] if ant else 0), L)} in the period (avance-bmad.csv)") if av else "")
    ids = lambda xs: "; ".join(f"{x['id']} {m(x['titulo'])} ({x['estado']})" for x in xs[:8]) or t("ninguna", "none")
    venc = d["acciones_vencidas"]
    prox = "; ".join(f"{x['id']} {m(x['accion'])} ({x['responsable']}, {x['fecha']})" for x in d["acciones_proximas"][:8]) or t("ninguna", "none")
    try:
        import puertas as PU
        pu = PU.markdown_estado(PU.estado_puertas(proyecto, e), L).split("\n", 1)[1].strip()
    except Exception:
        pu = t("(puertas.py estado --markdown no disponible)", "(puertas.py estado --markdown not available)")
    decs = "\n".join(f"| {d_['id']}: {m(d_['texto'])} | {PR} | {d_['fecha_limite'] or '—'} |" for d_ in d["decisiones"][:8]) or f"| {t('ninguna', 'none')} | — | — |"
    burn = "\n".join(f"| {x['nombre']} ({x['fecha']}) | {_n(x['alcance_total'], L)} | {_n(x['terminado_acumulado'], L)} | {_n(x['terminado'], L)} | {_n(x['planificado'] or 0, L)} |" for x in d["iteraciones"])
    R = d["registros"]; rr = R.get("riesgos", {}); ii = R.get("issues", {}); aa = R.get("acciones", {})
    fm = lambda x, n: recortar(x, n).replace('"', "'")
    fm_proy, fm_autor, fm_fuentes = fm(e.get("proyecto"), 80), fm((e.get("roles") or {}).get("gestor_proyecto"), 60), fm(d["fuentes"], 300)
    return f"""---
tipo: highlight-report
proyecto: "{fm_proy}"
fecha: "{d['corte']}"
periodo_desde: "{d['desde']}"
autor: "{fm_autor}"
estado: borrador
variante: minima
idioma: "{L}"
fuentes: "{fm_fuentes}"
generado_con: "estado.py periodo --highlight"
---

# {t('Informe de aspectos destacados (highlight report)', 'Highlight report')} · {d['corte']}

**{t('Etapa', 'Stage')}:** {_md(et.get('nombre'), 60)} · **{t('Período', 'Period')}:** {d['desde']} – {d['corte']} · **{t('Variante', 'Variant')}:** {t('mínima', 'minimum')} · **{t('Audiencia', 'Audience')}:** {t('junta del proyecto', 'project board')}

## 1. {t('Resumen ejecutivo', 'Executive summary')}
{res1} {PR}

## 2. {t('Semáforo por objetivo', 'RAG by objective')}
| {t('Objetivo', 'Objective')} | {t('Estado', 'Status')} | {t('Cifra y umbral', 'Figure and threshold')} | {t('Fuente', 'Source')} |
|---|---|---|---|
{filas}

## 4. {t('Este período', 'This period')}
**{t('Productos aceptados en el período (calidad aprobada)', 'Products accepted in the period (quality approved)')}:** {hist or t('ninguno', 'none')} ({d['revisiones_aprobadas']} {t('revisiones aprobadas en total', 'approved reviews in total')}){linea_av}.
**{t('Compromisos vencidos', 'Overdue commitments')}:** {'; '.join(venc) or t('ninguno', 'none')}.
**{t('Solicitudes de cambio del período', 'Change requests in the period')}:** {ids(d['cambios'])} · **{t('Fuera de especificación', 'Off-specifications')}:** {ids(d['fuera_especificacion'])}.

## 5. {t('Próximo período', 'Next period')} ({t('hasta', 'until')} {d['proximo'] or '—'})
**{t('Acciones que vencen', 'Actions due')}:** {prox}. {PR}

## 6. {t('Decisiones que necesita la junta', 'Decisions required from the board')}
{pu}

| {t('Decisión', 'Decision')} | {t('Recomendación', 'Recommendation')} | {t('Fecha límite', 'Needed by')} |
|---|---|---|
{decs}
""" + (f"""
## 7b. {t('Avance ágil (burn-up)', 'Agile progress (burn-up)')}
| {t('Corte', 'Cut-off')} | {t('Alcance total (pts)', 'Total scope (pts)')} | {t('Terminado acumulado (pts)', 'Done to date (pts)')} | {t('Velocidad (pts)', 'Velocity (pts)')} | {t('Planificado (pts)', 'Planned (pts)')} |
|---|---|---|---|---|
{burn}
""" if d["iteraciones"] else "") + f"""
## 10. {t('Registros', 'Registers')}
{t('Riesgos abiertos', 'Open risks')} {rr.get('abiertos', 0)} · {t('altos', 'high')} {rr.get('altos_abiertos', 0)} (P×I ≥ {d['umbrales_riesgo']['alto']:g}) · {t('issues abiertos', 'open issues')} {ii.get('abiertos', 0)} · {t('acciones abiertas', 'open actions')} {aa.get('abiertos', 0)} · {t('vencidas', 'overdue')} {aa.get('vencidas_total', len(venc))} · {t('cambios', 'changes')} {R.get('cambios', {}).get('total', 0)} (registro.py resumen --corte {d['corte']}).
"""

CIFRA_ES = r"[−-]?\d{1,3}(?:\.\d{3})+(?:,\d+)?|[−-]?\d+(?:,\d+)?"
CIFRA_EN = r"[−-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[−-]?\d+(?:\.\d+)?"

def verificar_cifras(proyecto, e, texto, corte, desde=None):
    """Cadena de reporte (regla 12 de pm-progreso-reportes): las cifras rotuladas del EVM (SPI, CPI, EAC, ETC, VAC, BAC, PV,
    EV, AC, SV, CV; sobrecosto y desvío en % del PV) coinciden con el corte guardado al redondeo citado («≈» o «~»: ±1 %),
    y el semáforo de cada objetivo con regla no es mejor que el derivado. Devuelve [(estado, detalle)], estado OK|DIFIERE|INFO."""
    L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en)
    NUM = CIFRA_ES if L == "es" else CIFRA_EN
    def valor(s):
        s = s.replace("−", "-"); s = s.replace(".", "").replace(",", ".") if L == "es" else s.replace(",", "")
        return float(s), (len(s.split(".")[1]) if "." in s else 0)
    ev_arch, ev = evm_ultimo(proyecto, corte); out = []
    cuerpo = texto.split("---", 2)[2] if texto.startswith("---") and texto.count("---") >= 2 else texto
    pats = [(rf"\b(SPI|CPI|EAC|ETC|VAC|BAC|PV|EV|AC|SV|CV)\b\s*[:=]?\s*(≈|~)?\s*(?:(?:[A-Z]{{3}}|US\$|\$|€)\s*)?(≈|~)?\s*({NUM})", None),
            (rf"(?:sobrecosto|overrun)(?:\s+(?:de|del|previsto|of))?\s*()()\+?({NUM})\s*%", "sobrecosto_pct"),
            (rf"\bEAC\b[^\n|(]{{0,40}}\(\s*()()\+?({NUM})\s*%\s*\)", "sobrecosto_pct"),
            (rf"(?:desv[ií]o(?:\s+de)?\s*)()()({NUM})\s*%\s*del PV", "SV_pct_del_PV"), (rf"()()({NUM})\s*%\s*of PV", "SV_pct_del_PV")]
    vistos = set()
    for pat, clave in pats:
        for mm in re.finditer(pat, cuerpo):
            k = clave or mm.group(1); aprox = bool((mm.group(2) if clave is None else "") or (mm.group(3) if clave is None else ""))
            cita = mm.group(4) if clave is None else mm.group(3)
            if (k, cita, aprox) in vistos: continue      # una comprobación por cifra citada (aunque se repita)
            vistos.add((k, cita, aprox))
            if not ev:
                out.append(("INFO", t(f"{k} {cita}: no hay corte de EVM guardado al {corte}.", f"{k} {cita}: no saved EVM cut-off by {corte}."))); continue
            v = ev.get(k)
            if not isinstance(v, (int, float)):
                out.append(("INFO", t(f"{k} {cita}: {ev_arch} no tiene ese valor.", f"{k} {cita}: {ev_arch} has no such value."))); continue
            x, dec = valor(cita)
            ok = abs(x - v) <= 0.01 * abs(v) + 1e-9 if aprox else abs(round(v, dec) - x) < 10 ** -(dec + 3)
            et_ = {"sobrecosto_pct": t("sobrecosto %", "overrun %"), "SV_pct_del_PV": t("desvío % del PV", "% of PV behind")}.get(k, k)
            out.append(("OK" if ok else "DIFIERE", f"{et_} {('≈ ' if aprox else '')}{cita} · {ev_arch}: {_cifra(v, L, 3 if abs(v) < 100 else 0)}"))
    d = datos_periodo(proyecto, e, desde or "0000-00-00", corte, con_radar=False)
    regla = {o["clave"]: o["rag"] for o in d["objetivos"] if o["base"].startswith("regla")}
    nombres = {n.lower(): c for c, ns in NOMBRES_OBJ.items() for n in ns}; nombres.update({"general": "general", "overall": "general"})
    peor = max(regla.values(), key=lambda r: GRAVEDAD[r], default=None)
    lineas = cuerpo.splitlines(); idx = 1
    for i, ln in enumerate(lineas):
        if not ln.startswith("|"): continue
        cel = [re.sub(r"[*_`]", "", c).strip() for c in ln.strip().strip("|").split("|")]
        if i + 1 < len(lineas) and re.match(r"^\|[\s:|-]+\|?\s*$", lineas[i + 1]):   # encabezado: columna del período actual
            cab = [x.lower() for x in cel]
            idx = next((k for k, x in enumerate(cab) if "este período" in x or "current" in x), next((k for k, x in enumerate(cab) if x.startswith(("estado", "status"))), 1))
            continue
        c = nombres.get(cel[0].split("/")[0].strip().lower()) if cel else None
        if not c or idx >= len(cel): continue
        col = _rag(cel[idx].split("/")[0]) if _rag(cel[idx].split("/")[0]) in ("verde", "ambar", "rojo") else None
        ref = peor if c == "general" else regla.get(c)
        if not col or not ref: continue
        bien = GRAVEDAD[col] >= GRAVEDAD[ref]
        out.append(("OK" if bien else "DIFIERE", t(f"semáforo {cel[0]}: {RAG_TXT[col][0]} (regla: {RAG_TXT[ref][0]})", f"RAG {cel[0]}: {RAG_TXT[col][1]} (rule: {RAG_TXT[ref][1]})")))
    if not out: out.append(("INFO", t("sin cifras del EVM ni semáforos que verificar.", "no EVM figures or RAG rows to check.")))
    return out

def texto_periodo(d, maximo=12):
    L = d["idioma"]; t = lambda es, en: E.t(L, es, en); rt = lambda r: RAG_TXT.get(r, (r, r))[0 if L == "es" else 1]
    x = [t(f"Período {d['desde']} – {d['corte']} · estado general {rt(d['general'])} · EVM: {d['evm'] or 'sin corte en el período'} · umbral alto P×I ≥ {d['umbrales_riesgo']['alto']:g}",
           f"Period {d['desde']} – {d['corte']} · overall {rt(d['general'])} · EVM: {d['evm'] or 'no cut-off in the period'} · high P×I ≥ {d['umbrales_riesgo']['alto']:g}")]
    for o in d["objetivos"]:
        x.append(f"  {NOMBRES_OBJ[o['clave']][0 if L == 'es' else 1]:15s} {rt(o['rag']):16s} {recortar(o['cifra'], 150)} [{o['base']}]")
    lst = lambda xs, f, nada=("ninguno", "none"): (", ".join(f(i) for i in xs[:maximo]) + (t(f" … y {len(xs) - maximo} más", f" … and {len(xs) - maximo} more") if len(xs) > maximo else "")) or t(*nada)
    x.append(t("Productos aceptados en el período: ", "Products accepted in the period: ") + lst(d["productos_aceptados"], lambda p: p["id"]))
    x.append(t("Cambios del período: ", "Changes in the period: ") + lst(d["cambios"], lambda c: f"{c['id']} ({c['estado']})") + t(" · fuera de especificación: ", " · off-specifications: ") + lst(d["fuera_especificacion"], lambda c: c["id"]))
    x.append(t("Decisiones para la junta: ", "Decisions for the board: ") + lst(d["decisiones"], lambda c: c["id"], ("ninguna", "none")))
    x.append(t("Iteraciones: ", "Iterations: ") + lst(d["iteraciones"], lambda i: f"{i['nombre']} {_n(i['terminado'], L)}/{_n(i['planificado'] or 0, L)}", ("ninguna", "none")))
    x += [t("AVISO: ", "WARNING: ") + a for a in d["avisos"]]
    return "\n".join(x)

PROTEGIDAS = ("_bmad", "_bmad-output", ".bmad-core")

def sincronizar_frontmatter(ruta, campos, proyecto=None):
    """Actualiza claves del frontmatter YAML simple de un .md (si existe). Nunca escribe fuera de la carpeta del
    proyecto ni en carpetas de BMAD (las especificaciones externas son de solo lectura)."""
    if not (os.path.exists(ruta) and ruta.endswith(".md")): return
    ra = os.path.abspath(ruta)
    if proyecto and not ra.startswith(os.path.abspath(proyecto) + os.sep): return
    if any(p in ra.split(os.sep) for p in PROTEGIDAS): return
    txt = open(ruta, encoding="utf-8").read()
    if not txt.startswith("---"): return
    partes = txt.split("---", 2)
    if len(partes) < 3: return
    fm = partes[1]
    for k, v in campos.items():
        val = f'"{v}"' if k == "aprobado_por" else v
        if re.search(rf"(?m)^{k}:", fm): fm = re.sub(rf"(?m)^{k}:.*$", lambda m: f"{k}: {val}", fm)
        else: fm = fm.rstrip("\n") + f"\n{k}: {val}\n"
    open(ruta, "w", encoding="utf-8").write("---" + fm + "---" + partes[2])

def aprobar(a, e):
    validar_clave(a.nombre, e.get("idioma", "es"))
    art = e["artefactos"].get(a.nombre)
    if not art: sys.exit(f"Artefacto no registrado / not registered: {a.nombre} (usar 'artefacto' primero)")
    if art.get("externo"): sys.exit(f"{a.nombre} es una especificación externa (BMAD): su aprobación se registra con bmad.py linea-base / external spec: use bmad.py linea-base")
    fecha = a.fecha or datetime.date.today().isoformat()
    art.update({"estado": "aprobado", "aprobado_por": a.por, "fecha": fecha})
    if a.version: art["version"] = a.version
    campos = {"estado": "aprobado", "aprobado_por": a.por, "fecha_aprobacion": fecha}
    if a.version: campos["version"] = a.version
    if not art.get("externo"):
        origen = os.path.join(a.proyecto, art["ruta"])
        sincronizar_frontmatter(origen, campos, a.proyecto)
        # copia congelada de la versión aprobada (línea base): 00-direccion/historial/<clave>-v<versión><ext>; nunca se pisa
        if os.path.isfile(origen):
            hist = os.path.join(a.proyecto, "00-direccion", "historial"); os.makedirs(hist, exist_ok=True)
            destino = os.path.join(hist, f"{a.nombre}-v{art.get('version', '')}{os.path.splitext(origen)[1]}")
            if os.path.dirname(os.path.realpath(destino)) != os.path.realpath(hist):     # la versión tampoco puede sacar la copia de historial/
                sys.exit(E.t(e.get("idioma", "es"), f"La copia congelada saldría de 00-direccion/historial/ ({destino}); revisar la clave y la versión.",
                             f"The frozen copy would leave 00-direccion/historial/ ({destino}); check the key and the version."))
            if not os.path.exists(destino):
                shutil.copy2(origen, destino); art["copia_congelada"] = os.path.relpath(destino, a.proyecto)
                print(f"Copia congelada / frozen copy: {art['copia_congelada']}")
    E.anotar_decision(a.proyecto, f"aprobado {a.nombre} v{art.get('version','')}", a.por, nivel=a.nivel,
                      artefactos=art["ruta"], fecha=fecha)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ver"); sub.add_parser("siguiente"); sub.add_parser("resumen", help="fase, etapa, roles clave, tolerancias, puertas pendientes y siguiente paso")
    s = sub.add_parser("set"); s.add_argument("pares", nargs="+"); s.add_argument("--forzar", action="store_true"); s.add_argument("--por", default="")
    s.add_argument("--nivel", default="gestor", choices=E.REGISTROS["decisiones"]["valores"]["nivel"], help="nivel de la decisión que se anota al cambiar enfoque_entrega")
    s.add_argument("--fecha", help="fecha de la decisión anotada (defecto: hoy)")
    cx = sub.add_parser("contexto", help="resumen derivado para el inicio de sesión: conteos, ids críticos y próxima puerta (≤ --max caracteres)")
    cx.add_argument("--max", type=int, default=2000); cx.add_argument("--corte", help="fecha de corte AAAA-MM-DD para vencidas (defecto: hoy)"); cx.add_argument("--json", action="store_true")
    rd = sub.add_parser("radar", help="qué decidir, escalar, desbloquear y vigilar al corte, con id, fecha, responsable y siguiente paso (solo lectura)")
    rd.add_argument("--corte", help="fecha de corte AAAA-MM-DD (defecto: hoy)"); rd.add_argument("--max", type=int, default=5, help="ítems por grupo (defecto 5; 0 = sin tope)")
    rdx = rd.add_mutually_exclusive_group(); rdx.add_argument("--json", action="store_true"); rdx.add_argument("--linea", action="store_true", help="una línea con los totales (la usa el hook de inicio)")
    br = sub.add_parser("briefing", help="briefing de incorporación (≤ 2 páginas) desde estado.json, registros, EVM, puertas y radar")
    br.add_argument("--para", help="id ST-### del interesado que se incorpora: agrega su rol, su RACI y lo que tiene a cargo")
    br.add_argument("--corte", help="fecha de corte AAAA-MM-DD (defecto: hoy)"); br.add_argument("--json", action="store_true", help="datos del briefing sin escribir el archivo")
    br.add_argument("--salida", help="archivo de salida (defecto: 03-control/reportes/<corte>-briefing-incorporacion[-ST-###].md; '-' = pantalla)")
    ps_ = sub.add_parser("productos", help="estado de productos (product status account) derivado de backlog o WBS, calidad, issues, aceptaciones y paquetes (solo lectura)")
    ps_.add_argument("--corte", help="fecha de corte AAAA-MM-DD (defecto: sin filtrar por fecha; las vencidas, contra hoy)")
    ps_.add_argument("--fuente", choices=["auto", "backlog", "wbs"], default="auto", help="productos de backlog.csv (historias) o de wbs.csv (hojas); auto: backlog si existe")
    ps_.add_argument("--alcance", default="proyecto", help="proyecto | WP-### (productos que cita su descripción) | release o iteración de backlog.csv | código de la WBS")
    ps_.add_argument("--max", type=int, default=40, help="filas de detalle y diferencias en pantalla (0 = sin tope)")
    psx = ps_.add_mutually_exclusive_group(); psx.add_argument("--json", action="store_true")
    psx.add_argument("--markdown", nargs="?", const="auto", metavar="RUTA", help="borrador del product status account (defecto: 03-control/reportes/<corte>-product-status-account.md)")
    pe = sub.add_parser("periodo", help="datos del período (semáforos por regla, productos aceptados, cambios, decisiones, iteraciones) → tablero y highlight; --verificar contrasta cifras con el EVM guardado")
    pe.add_argument("--desde", help="inicio del período AAAA-MM-DD (obligatorio salvo con --verificar)"); pe.add_argument("--corte", help="fin del período AAAA-MM-DD (defecto: hoy)")
    pe.add_argument("--proximo", default="", help="fin del próximo período AAAA-MM-DD (acciones que vencen)")
    pe.add_argument("--juicio", help="JSON del gestor: objetivos sin regla, notas, hitos, decisiones, iteraciones, comentario, moneda, fuentes (guía de pm-progreso-reportes §14)")
    pe.add_argument("--tablero", nargs="?", const="", help="escribe el tablero (defecto: 03-control/reportes/<corte>-tablero-avance.html) y lo registra en-revision")
    pe.add_argument("--highlight", nargs="?", const="", help="escribe el borrador del highlight, variante mínima (defecto: 03-control/reportes/<corte>-highlight-report.md)")
    pe.add_argument("--forzar", action="store_true", help="reescribe un highlight existente no aprobado (pierde lo redactado)")
    pe.add_argument("--verificar", nargs="+", metavar="ARCHIVO", help="cadena de reporte: cifras del EVM y semáforos de uno o más informes contra el corte guardado (código 1 si difieren)")
    pe.add_argument("--json", action="store_true")
    t_ = sub.add_parser("tolerancia"); t_.add_argument("--nivel", choices=E.NIVELES_TOLERANCIA, default="proyecto"); t_.add_argument("pares", nargs="+")
    r = sub.add_parser("rol"); r.add_argument("pares", nargs="+")
    ag = sub.add_parser("agil"); ag.add_argument("pares", nargs="+")
    ur = sub.add_parser("umbrales-riesgo"); ur.add_argument("pares", nargs="+")
    i = sub.add_parser("integracion"); i.add_argument("pares", nargs="+")
    et = sub.add_parser("etapa"); et.add_argument("--numero", type=int, required=True); et.add_argument("--nombre", required=True); et.add_argument("--inicio", default=""); et.add_argument("--fin", default="")
    ar = sub.add_parser("artefacto"); ar.add_argument("nombre"); ar.add_argument("--ruta", required=True); ar.add_argument("--estado", default="borrador", choices=E.ESTADOS_ARTEFACTO); ar.add_argument("--version", default=None)
    apr = sub.add_parser("aprobar"); apr.add_argument("nombre"); apr.add_argument("--por", required=True); apr.add_argument("--version"); apr.add_argument("--fecha"); apr.add_argument("--nivel", default="junta", choices=E.REGISTROS["decisiones"]["valores"]["nivel"])
    pu = sub.add_parser("puerta"); pu.add_argument("tipo", choices=E.PUERTAS); pu.add_argument("--decision", required=True, choices=E.DECISIONES_PUERTA)
    pu.add_argument("--por", required=True); pu.add_argument("--condiciones", default=""); pu.add_argument("--fecha"); pu.add_argument("--etapa-nombre", dest="etapa_nombre", default=""); pu.add_argument("--fin", default=""); pu.add_argument("--forzar", action="store_true")
    pu.add_argument("--inicio", default="", help="fecha de inicio de la etapa autorizada (por defecto, la de la puerta)")
    pu.add_argument("--tol", nargs="+", default=None, help="tolerancias de la etapa autorizada: costo=5%% tiempo=1sem …")
    pr = sub.add_parser("presupuesto", help="presupuestos que fija la junta: cambio, riesgo, gestion, limite_autoridad_cambio (montos)")
    pr.add_argument("pares", nargs="+"); pr.add_argument("--por", default=""); pr.add_argument("--fecha")
    cc = sub.add_parser("cumplir-condiciones"); cc.add_argument("tipo", choices=E.PUERTAS)
    cc.add_argument("--fecha"); cc.add_argument("--por", default="", help="quién verificó el cumplimiento (Rol: Nombre)"); cc.add_argument("--nota", default="")
    le = sub.add_parser("limite-etapa"); le.add_argument("--excepcion", default="")
    ci = sub.add_parser("cierre"); ci.add_argument("--prematuro", action="store_true")
    a = ap.parse_args(); e = E.cargar_estado(a.proyecto); L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en)

    if a.cmd == "ver": print(json.dumps(e, ensure_ascii=False, indent=2)); return
    if a.cmd == "siguiente": print(siguiente(e)); return
    if a.cmd == "contexto":
        txt, d = contexto(a.proyecto, e, max(200, a.max), a.corte)
        print(json.dumps({"texto": txt, "caracteres": len(txt), "datos": d}, ensure_ascii=False, indent=2) if a.json else txt); return
    if a.cmd == "radar":
        corte = a.corte or datetime.date.today().isoformat()
        d = datos_radar(a.proyecto, e, corte, max(0, a.max), rapido=a.linea)
        print(linea_radar(d, L) if a.linea else json.dumps(d, ensure_ascii=False, indent=2) if a.json else texto_radar(d, L, max(0, a.max))); return
    if a.cmd == "briefing":
        corte = a.corte or datetime.date.today().isoformat()
        md, d = briefing(a.proyecto, e, corte, a.para)
        if a.json: print(json.dumps(d, ensure_ascii=False, indent=2)); return
        if a.salida == "-": print(md); return
        ruta = a.salida or os.path.join(a.proyecto, "03-control", "reportes", f"{corte}-briefing-incorporacion" + (f"-{a.para}" if a.para else "") + ".md")
        if any(x in os.path.abspath(ruta).split(os.sep) for x in PROTEGIDAS) or os.sep + os.path.join("03-control", "registros") + os.sep in os.path.abspath(ruta):
            sys.exit(t("El briefing no se escribe en carpetas de BMAD ni en 03-control/registros/.", "The briefing is not written into BMAD folders or 03-control/registros/."))
        os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
        open(ruta, "w", encoding="utf-8").write(md)
        print(t(f"Briefing: {ruta} ({d['caracteres']} caracteres, ≈ {d['paginas']} página(s)); borrador: registrarlo con estado.py artefacto briefing-{corte} --ruta … --estado en-revision si se distribuye.",
                f"Briefing: {ruta} ({d['caracteres']} characters, ≈ {d['paginas']} page(s)); draft: record it with estado.py artefacto briefing-{corte} --ruta … --estado en-revision if distributed.")); return
    if a.cmd == "productos":
        try: d = productos(a.proyecto, e, a.corte, a.fuente, a.alcance)
        except ValueError as x: sys.exit(str(x))
        if a.json: print(json.dumps(d, ensure_ascii=False, indent=2)); return
        if a.markdown:
            ruta = os.path.join(a.proyecto, "03-control", "reportes", f"{d['corte'] or d['hoy']}-product-status-account.md") if a.markdown == "auto" else a.markdown
            ra = os.path.abspath(ruta)
            if any(x in ra.split(os.sep) for x in PROTEGIDAS) or os.sep + os.path.join("03-control", "registros") + os.sep in ra:
                sys.exit(t("El product status account no se escribe en carpetas de BMAD ni en 03-control/registros/.", "The product status account is not written into BMAD folders or 03-control/registros/."))
            if any(x.get("estado") == "aprobado" and x.get("ruta") and os.path.abspath(os.path.join(a.proyecto, x["ruta"])) == ra for x in e.get("artefactos", {}).values()):
                sys.exit(t(f"{ruta} es un artefacto aprobado: no se pisa (elegir otra --markdown RUTA).", f"{ruta} is an approved artefact: not overwritten (choose another --markdown RUTA)."))
            os.makedirs(os.path.dirname(ra), exist_ok=True)
            open(ra, "w", encoding="utf-8").write(markdown_productos(a.proyecto, d, e))
            print("\n".join(texto_productos(d, L, 0).splitlines()[:2]))
            print(t(f"Product status account: {ruta} (borrador; registrarlo con estado.py artefacto product-status-account --ruta … --estado en-revision).",
                    f"Product status account: {ruta} (draft; record it with estado.py artefacto product-status-account --ruta … --estado en-revision).")); return
        print(texto_productos(d, L, a.max if a.max > 0 else 10 ** 6)); return
    if a.cmd == "periodo":
        corte = a.corte or datetime.date.today().isoformat()
        if a.verificar:
            todo, salida = [], []
            for ruta in a.verificar:
                if not os.path.isfile(ruta): sys.exit(t(f"No existe {ruta}.", f"{ruta} not found."))
                txt = open(ruta, encoding="utf-8").read()
                fmc = re.search(r'(?m)^fecha:\s*"?(\d{4}-\d{2}-\d{2})', txt[:1500]) if txt.startswith("---") else None
                fmd = re.search(r'(?m)^periodo_desde:\s*"?(\d{4}-\d{2}-\d{2})', txt[:1500]) if txt.startswith("---") else None
                r_ = verificar_cifras(a.proyecto, e, txt, a.corte or (fmc.group(1) if fmc else corte), a.desde or (fmd.group(1) if fmd else None))
                todo += [{"archivo": ruta, "estado": s_, "detalle": d_} for s_, d_ in r_]
                dif = sum(1 for s_, _ in r_ if s_ == "DIFIERE")
                salida.append(f"{ruta}: " + t(f"{len(r_)} comprobaciones, {dif} difieren", f"{len(r_)} checks, {dif} differ"))
                salida += [f"  {s_:8s} {d_}" for s_, d_ in r_[:25]] + ([t(f"  … y {len(r_) - 25} más (--json)", f"  … and {len(r_) - 25} more (--json)")] if len(r_) > 25 else [])
            print(json.dumps(todo, ensure_ascii=False, indent=2) if a.json else "\n".join(salida))
            if any(x["estado"] == "DIFIERE" for x in todo):
                if not a.json: print(t("→ Cadena de reporte rota: corregir la cifra o el semáforo (o el registro) antes de emitir el informe.", "→ Reporting chain broken: fix the figure or RAG (or the register) before issuing the report."))
                sys.exit(1)
            return
        if not a.desde: sys.exit(t("periodo requiere --desde AAAA-MM-DD (o --verificar ARCHIVO).", "periodo requires --desde YYYY-MM-DD (or --verificar FILE)."))
        if a.desde > corte: sys.exit(t("--desde es posterior a --corte.", "--desde is after --corte."))
        d = datos_periodo(a.proyecto, e, a.desde, corte, a.proximo, leer_juicio(a.juicio, L))
        def destino(ruta, defecto):
            r_ = ruta or os.path.join(a.proyecto, "03-control", "reportes", defecto)
            ra = os.path.abspath(r_)
            if any(x in ra.split(os.sep) for x in PROTEGIDAS) or os.sep + os.path.join("03-control", "registros") + os.sep in ra:
                sys.exit(t("No se escribe en carpetas de BMAD ni en 03-control/registros/.", "Nothing is written into BMAD folders or 03-control/registros/."))
            rel = os.path.relpath(ra, os.path.abspath(a.proyecto))
            aprobado = [k for k, v in (e.get("artefactos") or {}).items() if v.get("estado") == "aprobado" and os.path.normpath(v.get("ruta", "")) == os.path.normpath(rel)]
            if aprobado: sys.exit(t(f"{rel} es la versión aprobada de {aprobado[0]}: no se reescribe.", f"{rel} is the approved version of {aprobado[0]}: not rewritten."))
            os.makedirs(os.path.dirname(ra), exist_ok=True)
            return r_, rel
        msgs = []
        if a.highlight is not None:
            r_, rel = destino(a.highlight, f"{corte}-highlight-report.md")
            if os.path.exists(r_) and not a.forzar:
                sys.exit(t(f"{rel} ya existe (puede tener narrativa redactada): usar --forzar para reescribirlo u otra ruta.", f"{rel} already exists (it may hold written narrative): use --forzar to rewrite it or another path."))
            md = md_highlight(d, e, a.proyecto); open(r_, "w", encoding="utf-8").write(md)
            dif = [x for x in verificar_cifras(a.proyecto, e, md, corte, a.desde) if x[0] == "DIFIERE"]
            msgs.append(t(f"Highlight (borrador, variante mínima): {rel} · {md.count('[por redactar]')} marca(s) [por redactar] · cadena de reporte: {'OK' if not dif else str(len(dif)) + ' diferencia(s)'}. "
                          f"Completar la narrativa, verificar con estado.py periodo --verificar {r_} y registrar con estado.py artefacto highlight-{corte} --ruta {rel} --estado en-revision.",
                          f"Highlight (draft, minimum variant): {rel} · {md.count('[to be written]')} [to be written] mark(s) · reporting chain: {'OK' if not dif else str(len(dif)) + ' difference(s)'}. "
                          f"Complete the narrative, check with estado.py periodo --verificar {r_} and record it with estado.py artefacto highlight-{corte} --ruta {rel} --estado en-revision."))
        if a.tablero is not None:
            r_, rel = destino(a.tablero, f"{corte}-tablero-avance.html")
            open(r_, "w", encoding="utf-8").write(html_tablero(d))
            prev = e["artefactos"].get("tablero-avance", {})
            e["artefactos"]["tablero-avance"] = {**{k: v for k, v in prev.items() if k != "aprobado_por"}, "ruta": rel, "estado": "en-revision",
                                                 "version": prev.get("version") or "0.1", "fecha": datetime.date.today().isoformat()}
            guardar(a.proyecto, e)
            msgs.append(t(f"Tablero: {rel} (registrado tablero-avance, en-revision) · riesgos abiertos {len(d['tablero']['riesgos'])} · issues {len(d['tablero']['issues'])} · acciones {len(d['tablero']['acciones'])} · iteraciones {len(d['iteraciones'])}",
                          f"Dashboard: {rel} (recorded tablero-avance, en-revision) · open risks {len(d['tablero']['riesgos'])} · issues {len(d['tablero']['issues'])} · actions {len(d['tablero']['acciones'])} · iterations {len(d['iteraciones'])}"))
        if a.json:
            print(json.dumps({k: v for k, v in d.items() if k != "tablero"}, ensure_ascii=False, indent=2))
            for x in msgs: print(x, file=sys.stderr)
        else:
            print(texto_periodo(d))
            for x in msgs: print(x)
        return
    if a.cmd == "resumen":
        et = e.get("etapa_actual", {}); r = e.get("roles", {})
        print(f"{e.get('proyecto')} · {e['fase']}/{e['proceso_actual']} · {t('etapa', 'stage')} {et.get('numero')} {et.get('nombre', '')} "
              f"({et.get('inicio', '')} → {et.get('fin_previsto', '')}) · {t('enfoque', 'approach')} {e.get('enfoque_entrega')} · {t('idioma', 'language')} {e.get('idioma')}")
        print(t("Autorizado: ", "Authorized: ") + (t("sí", "yes") if e.get("proyecto_autorizado") else "no") + (f" · {t('excepción abierta', 'open exception')}: {e['excepcion_abierta']}" if e.get("excepcion_abierta") else ""))
        print(t("Roles: ", "Roles: ") + "; ".join(f"{k}={v if not isinstance(v, list) else ', '.join(v)}" for k, v in r.items() if v) or "-")
        print(t("Tolerancias: ", "Tolerances: ") + " | ".join(f"{n}: " + ", ".join(f"{k}={v}" for k, v in d.items() if v) for n, d in e.get("tolerancias", {}).items()))
        pre = {k: v for k, v in e.get("presupuestos", {}).items() if v}
        if pre: print(t("Presupuestos: ", "Budgets: ") + ", ".join(f"{k}={v}" for k, v in pre.items()))
        pend = [p["tipo"] for p in pendientes(e)]; cond = [p["tipo"] for p in condiciones_abiertas(e)]
        if pend: print(t("Puertas pendientes: ", "Pending gates: ") + ", ".join(pend))
        if cond: print(t("Condiciones abiertas: ", "Open conditions: ") + ", ".join(cond))
        arts = e.get("artefactos", {}); print(t("Artefactos: ", "Artifacts: ") + f"{len(arts)} ({sum(1 for x in arts.values() if x.get('estado') == 'aprobado')} {t('aprobados', 'approved')})")
        try:
            import puertas as PU
            ult = e.get("puertas", [])[-1] if e.get("puertas") else None
            if ult:
                v = ult.get("verificacion") or {}
                print(t("Última puerta: ", "Last gate: ") + f"{ult['tipo']} · {ult.get('decision')} · {ult.get('fecha')} · {ult.get('por')}"
                      + (t(" · FORZADA", " · FORCED") if ult.get("forzada") else "")
                      + (t(" · observaciones: ", " · observations: ") + recortar("; ".join(v["observaciones"]), 400) if v.get("observaciones") else ""))
            prox = PU.proxima_puerta(e)
            if prox:
                bl, co, av, li = PU.evaluar(a.proyecto, e, prox)
                print(t("Próxima puerta: ", "Next gate: ") + f"{prox} · {len(bl)} " + t("bloqueo(s)", "blocker(s)") + f" · {len(co)} " + t("condición(es)", "condition(s)")
                      + t(" (detalle: puertas.py verificar ", " (detail: puertas.py verificar ") + prox + ")")
        except Exception:
            pass
        print(siguiente(e)); return
    if a.cmd == "set":
        permitidos = {"fase": E.FASES, "proceso_actual": E.PROCESOS, "enfoque_entrega": ["predictivo", "agil", "hibrido"], "idioma": ["es", "en"]}
        pares = kv(a.pares)
        for k, v in pares.items():
            if k not in ("proyecto", "idioma", "enfoque_entrega", "fase", "proceso_actual"):
                sys.exit(t(f"Clave no editable con set: {k}", f"Key not editable with set: {k}"))
            if k in ("fase", "proceso_actual") and not (a.forzar and a.por):
                sys.exit(t("fase y proceso_actual cambian con las puertas (estado.py puerta …), limite-etapa o cierre. Solo para corregir un error de "
                           "registro: set fase=… --forzar --por \"<quién autoriza>\" (queda anotado en decisiones.csv).",
                           "fase and proceso_actual change through gates (estado.py puerta …), limite-etapa or cierre. Only to fix a recording error: "
                           "set fase=… --forzar --por \"<who authorizes>\" (recorded in decisiones.csv)."))
            if k in permitidos and v not in permitidos[k]: sys.exit(f"{k}: {', '.join(permitidos[k])}")
        if "enfoque_entrega" in pares and pares["enfoque_entrega"] != e.get("enfoque_entrega"):
            if a.por:
                did = E.anotar_decision(a.proyecto, t(f"enfoque de entrega: {e.get('enfoque_entrega')} → {pares['enfoque_entrega']}",
                                                      f"delivery approach: {e.get('enfoque_entrega')} → {pares['enfoque_entrega']}"),
                                        a.por, nivel=a.nivel, contexto=f"{e['fase']}/{e['proceso_actual']}", notas="estado.py set", fecha=a.fecha)
                print(t(f"Decisión anotada: {did}", f"Decision recorded: {did}"))
            else:
                print(t("AVISO: cambio de enfoque_entrega sin --por: no queda anotado en decisiones.csv (agregar --por \"Rol: Nombre\").",
                        "WARNING: enfoque_entrega changed without --por: not recorded in decisiones.csv (add --por \"Role: Name\")."))
        if any(k in ("fase", "proceso_actual") for k in pares):
            E.anotar_decision(a.proyecto, t("corrección forzada de estado: ", "forced state correction: ") + ", ".join(f"{k}={v}" for k, v in pares.items()),
                              a.por, nivel="gestor", contexto=f"{e['fase']}/{e['proceso_actual']}", notas="estado.py set --forzar")
        for k, v in pares.items(): e[k] = v
    elif a.cmd == "tolerancia":
        for k, v in kv(a.pares).items():
            if k not in E.DIMENSIONES_TOLERANCIA: sys.exit(t(f"Tolerancia desconocida: {k}", f"Unknown tolerance: {k}") + f" ({', '.join(E.DIMENSIONES_TOLERANCIA)})")
            e["tolerancias"][a.nivel][k] = v
    elif a.cmd == "rol":
        for k, v in kv(a.pares).items():
            if k not in e["roles"]: sys.exit(t(f"Rol desconocido: {k}", f"Unknown role: {k}") + f" ({', '.join(e['roles'])})")
            e["roles"][k] = [x.strip() for x in v.split(";") if x.strip()] if isinstance(e["roles"][k], list) else v
    elif a.cmd == "agil":
        for k, v in kv(a.pares).items(): e["agil"][k] = int(v) if v.isdigit() else v
    elif a.cmd == "umbrales-riesgo":
        for k, v in kv(a.pares).items():
            if k not in ("alto", "medio") or not v.replace(".", "").isdigit(): sys.exit("umbrales-riesgo alto=<n> medio=<n>")
            e["umbrales_riesgo"][k] = float(v)
    elif a.cmd == "integracion":
        for k, v in kv(a.pares).items():
            vals = E.VALORES_INTEGRACION.get(k)
            if vals and not all(x.strip() in vals for x in v.split(",")):
                print(t(f"AVISO: integraciones.{k}={v} no es un valor conocido ({', '.join(sorted(vals))}); se guarda, pero pm-integraciones debe saber mapearlo (sanidad INT-01).",
                        f"WARNING: integraciones.{k}={v} is not a known value ({', '.join(sorted(vals))}); saved, but pm-integraciones must know how to map it (health INT-01)."))
            e["integraciones"][k] = v
    elif a.cmd == "etapa":
        e["etapa_actual"] = {"numero": a.numero, "nombre": a.nombre, "inicio": a.inicio, "fin_previsto": a.fin}
    elif a.cmd == "artefacto":
        validar_clave(a.nombre, L)
        base = os.path.realpath(a.proyecto); destino_art = os.path.realpath(os.path.join(a.proyecto, a.ruta))
        if os.path.commonpath([base, destino_art]) != base:
            print(t(f"AVISO: {a.ruta} queda fuera de la carpeta del proyecto: paquete.py no lo incluye en el paquete de puerta salvo --permitir-externos.",
                    f"WARNING: {a.ruta} is outside the project folder: paquete.py leaves it out of the gate package unless --permitir-externos."))
        prev = e["artefactos"].get(a.nombre, {})
        if prev.get("externo"): sys.exit(t(f"{a.nombre} es una especificación externa (BMAD): se gestiona con bmad.py linea-base.", f"{a.nombre} is an external (BMAD) spec: use bmad.py linea-base."))
        version = a.version or prev.get("version") or "0.1"
        nuevo = {**prev, "ruta": a.ruta, "estado": a.estado, "version": version, "fecha": datetime.date.today().isoformat()}
        if a.estado != "aprobado": nuevo.pop("aprobado_por", None)   # una nueva versión no hereda la aprobación anterior
        e["artefactos"][a.nombre] = nuevo
        campos = {"estado": a.estado, **({"version": a.version} if a.version else {}), **({} if a.estado == "aprobado" else {"aprobado_por": ""})}
        sincronizar_frontmatter(os.path.join(a.proyecto, a.ruta), campos, a.proyecto)
    elif a.cmd == "aprobar":
        aprobar(a, e)
    elif a.cmd == "puerta":
        registrar_puerta(a, e)
    elif a.cmd == "presupuesto":
        pares = kv(a.pares)
        for k, v in pares.items():
            if k not in E.CLAVES_PRESUPUESTO: sys.exit(t(f"Presupuesto desconocido: {k}", f"Unknown budget: {k}") + f" ({', '.join(E.CLAVES_PRESUPUESTO)})")
            if v:
                try:
                    if re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", v): raise ValueError   # 10.000 o 10,000: separador de miles ambiguo
                    float(v.replace(",", "."))
                except ValueError: sys.exit(t(f"{k}: el monto debe ser un número simple como 10000 (sin moneda ni separador de miles): {v}", f"{k}: amount must be a plain number such as 10000: {v}"))
            e.setdefault("presupuestos", {})[k] = v
        if a.por:
            E.anotar_decision(a.proyecto, t("presupuestos de la junta: ", "board budgets: ") + ", ".join(f"{k}={v}" for k, v in pares.items()),
                              a.por, nivel="junta", contexto=f"{e['fase']}/{e['proceso_actual']}", notas="estado.py presupuesto", fecha=a.fecha)
    elif a.cmd == "cumplir-condiciones":
        hechas = 0
        for p in condiciones_abiertas(e):
            if p["tipo"] == a.tipo:
                p["condiciones_cumplidas"] = a.fecha or datetime.date.today().isoformat(); hechas += 1
                if a.por: p["condiciones_verificadas_por"] = a.por
                if a.nota: p["condiciones_nota"] = a.nota
        if not hechas: sys.exit(t(f"No hay condiciones abiertas de {a.tipo}.", f"No open conditions for {a.tipo}."))
        if a.por:
            E.anotar_decision(a.proyecto, t(f"condiciones de {a.tipo} cumplidas", f"{a.tipo} conditions met") + (f" — {a.nota}" if a.nota else ""),
                              a.por, nivel="junta", contexto=f"{e['fase']}/{e['proceso_actual']}", notas="estado.py cumplir-condiciones", fecha=a.fecha)
    elif a.cmd == "limite-etapa":
        if e["fase"] != "entrega": sys.exit(t("limite-etapa solo en etapas de entrega.", "limite-etapa only during delivery stages."))
        e["proceso_actual"] = "SB"; e["excepcion_abierta"] = a.excepcion
    elif a.cmd == "cierre":
        if e["fase"] not in ("entrega",): sys.exit(t("El cierre se inicia desde una etapa de entrega (CS o SB).", "Closure starts from a delivery stage (CS or SB)."))
        e["fase"], e["proceso_actual"] = "cierre", "CP"; e["cierre_prematuro"] = a.prematuro
    guardar(a.proyecto, e); print("ok")
    if a.cmd in ("puerta", "limite-etapa", "cierre"): print(siguiente(e))

if __name__ == "__main__":
    main()
