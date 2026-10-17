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
  estado.py --proyecto ./p puerta autorizar-etapa --decision aprobado --por "Junta" [--condiciones ".."] [--fecha ..] [--etapa-nombre ".."] [--fin ..]
  estado.py --proyecto ./p limite-etapa [--excepcion X-001]      # CS → SB (fin de etapa o plan de excepción)
  estado.py --proyecto ./p cierre [--prematuro]                    # CS/SB → CP (cierre planificado o prematuro)
  estado.py --proyecto ./p etapa --numero 2 --nombre "Construcción" --inicio .. --fin ..   # corrección manual
  estado.py --proyecto ./p set enfoque_entrega=hibrido             # claves simples validadas

Las puertas las decide una persona con rol en la junta; este script solo registra la decisión (y la anota en
decisiones.csv). Gates are decided by people; this script records them.
"""
import argparse, json, os, sys, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esquema as E

def guardar(p, e):
    e["actualizado"] = datetime.date.today().isoformat(); e["version_estado"] = e.get("version_estado", 0) + 1
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
    return [p for p in e.get("puertas", []) if p.get("decision") == "condicionado" and p.get("condiciones") and not p.get("condiciones_cumplidas")]

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
    if cond: out.append(t("Condiciones abiertas: ", "Open conditions: ") + "; ".join(f"{p['tipo']}: {p['condiciones']}" for p in cond))
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
    for p in pendientes(e):
        if p["tipo"] == a.tipo and a.decision != "pendiente":
            p["resuelta"] = fecha
    reg = {"tipo": a.tipo, "fecha": fecha, "decision": a.decision, "por": a.por, "condiciones": a.condiciones,
           "etapa": e["etapa_actual"]["numero"]}
    if a.forzar and not pre: reg["forzada"] = True
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
            e["etapa_actual"] = {"numero": n + 1, "nombre": a.etapa_nombre or t(f"Etapa {n + 1}", f"Stage {n + 1}"), "inicio": fecha, "fin_previsto": a.fin or ""}
            e["tolerancias"]["etapa"] = {k: "" for k in E.DIMENSIONES_TOLERANCIA}  # nuevas tolerancias de etapa: 'tolerancia --nivel etapa'
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
        did = E.anotar_decision(a.proyecto, f"{a.tipo}: {a.decision}" + (f" — condiciones: {a.condiciones}" if a.condiciones else ""),
                                a.por, nivel="junta", contexto=f"{fase}/{proc} etapa {reg['etapa']}", notas=f"puerta: {a.tipo}", fecha=fecha)
        reg["decision_id"] = did

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
    art = e["artefactos"].get(a.nombre)
    if not art: sys.exit(f"Artefacto no registrado / not registered: {a.nombre} (usar 'artefacto' primero)")
    if art.get("externo"): sys.exit(f"{a.nombre} es una especificación externa (BMAD): su aprobación se registra con bmad.py linea-base / external spec: use bmad.py linea-base")
    fecha = a.fecha or datetime.date.today().isoformat()
    art.update({"estado": "aprobado", "aprobado_por": a.por, "fecha": fecha})
    if a.version: art["version"] = a.version
    campos = {"estado": "aprobado", "aprobado_por": a.por, "fecha_aprobacion": fecha}
    if a.version: campos["version"] = a.version
    if not art.get("externo"): sincronizar_frontmatter(os.path.join(a.proyecto, art["ruta"]), campos, a.proyecto)
    E.anotar_decision(a.proyecto, f"aprobado {a.nombre} v{art.get('version','')}", a.por, nivel=a.nivel,
                      artefactos=art["ruta"], fecha=fecha)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ver"); sub.add_parser("siguiente")
    s = sub.add_parser("set"); s.add_argument("pares", nargs="+")
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
    cc = sub.add_parser("cumplir-condiciones"); cc.add_argument("tipo", choices=E.PUERTAS)
    le = sub.add_parser("limite-etapa"); le.add_argument("--excepcion", default="")
    ci = sub.add_parser("cierre"); ci.add_argument("--prematuro", action="store_true")
    a = ap.parse_args(); e = E.cargar_estado(a.proyecto); L = e.get("idioma", "es"); t = lambda es, en: E.t(L, es, en)

    if a.cmd == "ver": print(json.dumps(e, ensure_ascii=False, indent=2)); return
    if a.cmd == "siguiente": print(siguiente(e)); return
    if a.cmd == "set":
        permitidos = {"fase": E.FASES, "proceso_actual": E.PROCESOS, "enfoque_entrega": ["predictivo", "agil", "hibrido"], "idioma": ["es", "en"]}
        for k, v in kv(a.pares).items():
            if k not in ("proyecto", "idioma", "enfoque_entrega", "fase", "proceso_actual"):
                sys.exit(t(f"Clave no editable con set: {k}", f"Key not editable with set: {k}"))
            if k in permitidos and v not in permitidos[k]: sys.exit(f"{k}: {', '.join(permitidos[k])}")
            e[k] = v
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
        for k, v in kv(a.pares).items(): e["integraciones"][k] = v
    elif a.cmd == "etapa":
        e["etapa_actual"] = {"numero": a.numero, "nombre": a.nombre, "inicio": a.inicio, "fin_previsto": a.fin}
    elif a.cmd == "artefacto":
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
    elif a.cmd == "cumplir-condiciones":
        for p in condiciones_abiertas(e):
            if p["tipo"] == a.tipo: p["condiciones_cumplidas"] = datetime.date.today().isoformat()
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
