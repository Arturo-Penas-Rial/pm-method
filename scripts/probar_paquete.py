#!/usr/bin/env python3
"""Pruebas de regresión de punta a punta del paquete pm-method (para el mantenedor).
End-to-end regression tests: BMAD v6 (synthetic + real 6.12.4 fixture), BMAD v4 and native specification, gates, backbone sync and health checks.

Uso / Usage: python3 scripts/probar_paquete.py [--conservar]
Correr después de cualquier cambio del paquete o al adoptar una versión nueva de BMAD (reemplazar o agregar un
fixture en scripts/pruebas/fixtures/ con artefactos reales de esa versión). Requiere PyYAML.
"""
import csv, glob, json, os, re, shutil, subprocess, sys, tempfile, time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAIZ, "skills", "pm-estado-proyecto", "scripts")
B = os.path.join(RAIZ, "skills", "pm-bmad-puente", "scripts", "bmad.py")
FIX = os.path.join(RAIZ, "scripts", "pruebas", "fixtures")
RES = {"ok": 0, "fallo": 0}

def run(args, cwd, esperar=0, entrada=None):
    r = subprocess.run([sys.executable] + args, cwd=cwd, capture_output=True, text=True, input=entrada)
    if esperar is not None and r.returncode != esperar:
        print(f"    salida: {r.stdout[-600:]}\n    error: {r.stderr[-600:]}")
    return r

PU = os.path.join(S, "puertas.py")

def junta(proyecto, tipo, cwd, arts=(), por="Junta: Ejecutiva"):
    """Prepara una puerta como lo haría pm-director: artefactos mínimos, lista de control y confirmación de la junta."""
    for art, ruta in arts:
        destino = os.path.join(cwd, proyecto, ruta) if not os.path.isabs(proyecto) else os.path.join(proyecto, ruta)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        if not os.path.exists(destino): open(destino, "w", encoding="utf-8").write(f"---\ntipo: {art}\nestado: borrador\n---\n# {art}\nBeneficio B-1.\n")
        run([os.path.join(S, "estado.py"), "--proyecto", proyecto, "artefacto", art, "--ruta", ruta, "--estado", "en-revision"], cwd)
    run([PU, "--proyecto", proyecto, "lista", tipo], cwd)
    return run([PU, "--proyecto", proyecto, "confirmar", tipo, "--por", por], cwd)

def check(nombre, cond, detalle=""):
    RES["ok" if cond else "fallo"] += 1
    print(f"  {'OK   ' if cond else 'FALLO'} {nombre}" + (f" — {detalle}" if detalle and not cond else ""))

def sanidad(proy, cwd):
    r = run([os.path.join(S, "sanidad.py"), "--proyecto", proy, "--json"], cwd, esperar=None)
    try: return json.loads(r.stdout)
    except Exception: print(r.stdout[-500:], r.stderr[-500:]); return {"hallazgos": [], "cuenta": {}}

def codigos(d, sev="ERROR"): return {h["codigo"] for h in d.get("hallazgos", []) if h["severidad"] == sev}

def caso_v6(tmp):
    print("Caso A · BMAD v6 + proyecto híbrido")
    repo = os.path.join(tmp, "v6"); shutil.copytree(os.path.join(FIX, "bmad-v6"), repo)
    g = "gestion"
    check("nuevo_proyecto", run([os.path.join(S, "nuevo_proyecto.py"), "--ruta", g, "--nombre", "Portal", "--enfoque", "hibrido", "--ejecutivo", "Ejecutiva", "--gestor", "Gestor"], repo).returncode == 0)
    check("bmad detectar", run([B, "--proyecto", g, "detectar"], repo).returncode == 0)
    r = run([os.path.join(S, "especificacion.py"), "--proyecto", g, "resumen", "--json"], repo)
    res = json.loads(r.stdout or "{}")
    check("fachada: 9 ids y FR-4 sin cobertura", res.get("requisitos") == 9 and res.get("sin_cobertura") == ["FR-4"], str(res))
    r = run([os.path.join(S, "especificacion.py"), "--proyecto", g, "consultar", "FR3", "--json"], repo)
    check("fachada: consultar FR3 → historia 2-2", "2-2-descargar-constancias" in r.stdout)
    with open(os.path.join(repo, g, "02-planificacion", "wbs.csv"), "w", encoding="utf-8") as f:
        f.write("codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref\n1,Acceso,producto,,,,\n1.1,Login,paquete,Dev,40,3000,FR-1\n2,Trámites,producto,,,,\n2.1,Consulta y constancias,paquete,Dev,80,6000,FR-2;FR-3\n2.2,Bandeja de operador,paquete,Dev,60,4500,FR-4\n")
    check("wbs.py", run([os.path.join(S, "wbs.py"), "02-planificacion/wbs.csv", "--mermaid", "02-planificacion/visuales/wbs.md"], os.path.join(repo, g)).returncode == 0)
    with open(os.path.join(repo, g, "02-planificacion", "actividades.csv"), "w", encoding="utf-8") as f:
        f.write("id,nombre,duracion,predecesoras,recurso,wbs\nWP-1,Login,5,,Dev,1.1\nWP-2,Consulta,10,WP-1,Dev,2.1\nWP-3,Bandeja,7,WP-1+2,Dev,2.2\nH-1,Listo,0,WP-2;WP-3,,2.3\n")
    r = run([os.path.join(S, "cpm.py"), "02-planificacion/actividades.csv", "--inicio", "2026-11-02", "--mspdi", "02-planificacion/cronograma.xml", "--wbs", "02-planificacion/wbs.csv"], os.path.join(repo, g))
    ok_xml = False
    try:
        import xml.dom.minidom as m; m.parse(os.path.join(repo, g, "02-planificacion", "cronograma.xml")); ok_xml = True
    except Exception: pass
    check("cpm.py + MSPDI bien formado", r.returncode == 0 and ok_xml)
    E = lambda *a: run([os.path.join(S, "estado.py"), "--proyecto", g] + list(a), repo)
    r0 = E("puerta", "autorizar-inicio", "--decision", "aprobado", "--por", "Ejecutiva")
    check("verificación de puerta: sin brief ni lista de control, 'aprobado' se rechaza", r0.returncode != 0 and "I-01" not in r0.stdout and "project brief" in (r0.stderr + r0.stdout) and "lista de control" in (r0.stderr + r0.stdout), (r0.stderr + r0.stdout)[-400:])
    junta(g, "autorizar-inicio", repo, arts=[("project-brief", "01-inicio/project-brief.md")])
    r0 = E("puerta", "autorizar-inicio", "--decision", "aprobado", "--por", "Ejecutiva")
    check("puerta autorizar-inicio (brief + lista confirmada)", r0.returncode == 0, (r0.stderr + r0.stdout)[-400:])
    check("puerta fuera de orden rechazada", E("puerta", "autorizar-cierre", "--decision", "aprobado", "--por", "X").returncode != 0)
    E("tolerancia", "--nivel", "proyecto", "tiempo=±1 mes", "costo=±10 %")
    r0 = E("puerta", "autorizar-proyecto", "--decision", "aprobado", "--por", "Ejecutiva")
    check("bloqueo de puerta: autorizar-proyecto sin business case ni PID se rechaza", r0.returncode != 0 and "business-case" in (r0.stderr + r0.stdout), r0.stderr[-300:])
    junta(g, "autorizar-proyecto", repo, arts=[("business-case", "00-direccion/business-case.md"), ("pid", "00-direccion/pid.md")])
    r1 = E("puerta", "autorizar-proyecto", "--decision", "aprobado", "--por", "Ejecutiva")
    check("puerta autorizar-proyecto", r1.returncode == 0, (r1.stderr + r1.stdout)[-400:])
    check("línea base PRD v1.0", run([B, "--proyecto", g, "linea-base", "prd", "--version", "1.0", "--por", "Ejecutiva"], repo).returncode == 0)
    def plan(n, extra=()):
        junta(g, "autorizar-etapa", repo, arts=[(f"plan-etapa-{n}", f"02-planificacion/plan-etapa-{n}.md")] + list(extra))
    r2b = E("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Ejecutiva", "--etapa-nombre", "Release 1", "--tol", "costo=±5 %")
    check("bloqueo de puerta: autorizar-etapa sin plan de etapa se rechaza", r2b.returncode != 0 and "plan-etapa-2" in (r2b.stderr + r2b.stdout), (r2b.stderr + r2b.stdout)[-300:])
    plan(2)
    r2 = E("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Ejecutiva", "--etapa-nombre", "Release 1", "--tol", "costo=±5 %")
    check("puerta autorizar-etapa", r2.returncode == 0, (r2.stderr + r2.stdout)[-400:])
    run([B, "--proyecto", g, "backlog"], repo)
    pb = os.path.join(repo, g, "02-planificacion", "backlog.csv")
    filas = list(csv.DictReader(open(pb, encoding="utf-8"))); cols = list(filas[0].keys())
    filas[0]["moscow"] = "must"; filas[0]["estimacion"] = "5"
    with open(pb, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(filas)
    run([B, "--proyecto", g, "backlog"], repo)
    f0 = list(csv.DictReader(open(pb, encoding="utf-8")))[0]
    check("backlog: columnas de gobierno se conservan", f0["moscow"] == "must" and f0["estimacion"] == "5")
    check("avance", run([B, "--proyecto", g, "avance", "--corte", "2026-11-30"], repo).returncode == 0)
    d = sanidad(g, repo)
    check("sanidad sana: 0 ERROR", not codigos(d), str(codigos(d)))
    # columna vertebral: cambio no controlado
    prd = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(repo, "_bmad-output")) for f in fs if f == "prd.md" and "2026-10-01" in dp][0]
    open(prd, "a", encoding="utf-8").write("\n- **FR-9**: Chat en vivo.\n")
    d = sanidad(g, repo)
    check("sanidad detecta cambio no controlado (ESP-10)", "ESP-10" in codigos(d), str(codigos(d)))
    R = lambda *a: run([os.path.join(S, "registro.py"), "--proyecto", g] + list(a), repo)
    R("agregar", "issues", "--campo", "tipo=solicitud-cambio", "--campo", "titulo=FR-9 chat en vivo (bmad-prd)", "--campo", "responsable=Gestor")
    d = sanidad(g, repo)
    check("con issue que lo cita, ESP-10 deja de ser ERROR", "ESP-10" not in codigos(d), str(codigos(d)))
    R("agregar", "cambios", "--campo", "titulo=Chat en vivo", "--campo", "descripcion=Agregar FR-9", "--campo", "decision=aprobado",
      "--campo", "decidido_por=junta Ejecutiva", "--campo", "estado=aprobado", "--campo", "notas=FR-9")
    check("handoff inverso emitido", run([B, "--proyecto", g, "handoff", "--cambio", "C-001"], repo).returncode == 0)
    R("actualizar", "issues", "I-001", "--campo", "estado=cerrado")
    run([B, "--proyecto", g, "linea-base", "prd", "--version", "1.1", "--por", "Ejecutiva"], repo)
    with open(os.path.join(repo, g, "02-planificacion", "wbs.csv"), "a", encoding="utf-8") as f: f.write("2.3,Chat,paquete,Dev,30,2000,FR-9\n")
    d = sanidad(g, repo)
    check("tras nueva línea base: sin ESP-10 ni ESP-03", not ({"ESP-10", "ESP-03"} & codigos(d)), str(codigos(d)))
    check("ESP-13 avisa traspaso sin confirmar", "ESP-13" in codigos(d, "AVISO"))
    # sanidad: defectos sembrados
    R("agregar", "riesgos", "--campo", "evento=Integración con padrón FR-42", "--campo", "probabilidad=3", "--campo", "impacto=3", "--campo", "propietario=Gestor")
    d = sanidad(g, repo)
    check("sanidad detecta id inexistente (ESP-04)", "ESP-04" in codigos(d))
    # guardián
    G = os.path.join(RAIZ, "hooks", "guardian.py")
    neg = lambda payload: "deny" in run([G], repo, entrada=json.dumps(payload)).stdout
    check("guardián: estado.json no editable", neg({"tool_name": "Edit", "tool_input": {"file_path": os.path.join(repo, g, "estado.json")}}))
    check("guardián: registros solo por registro.py", neg({"tool_name": "Write", "tool_input": {"file_path": os.path.join(repo, g, "03-control", "registros", "riesgos.csv")}}))
    check("guardián: subagente pm-* no escribe en BMAD", neg({"tool_name": "Write", "agent_type": "pm-method:pm-control", "tool_input": {"file_path": prd}}))
    check("guardián: hilo principal sí puede (flujos BMAD)", not neg({"tool_name": "Write", "tool_input": {"file_path": prd}}))
    check("guardián: documentos normales permitidos", not neg({"tool_name": "Write", "tool_input": {"file_path": os.path.join(repo, g, "02-planificacion", "plan-etapa-2.md")}}))
    check("hook de inicio resume el proyecto", "pm-method" in run([os.path.join(RAIZ, "hooks", "inicio.py")], repo, entrada=json.dumps({"cwd": repo})).stdout)
    # cierre
    plan(3, [("informe-fin-etapa-2", "03-control/reportes/informe-fin-etapa-2.md")]); r3 = E("limite-etapa"); r4 = E("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Ejecutiva")
    check("bloqueo de puerta: un ERROR de sanidad (ESP-04 sembrado) impide 'aprobado'", r3.returncode == 0 and r4.returncode != 0 and "ESP-04" in (r4.stderr + r4.stdout), (r4.stderr + r4.stdout)[-300:])
    r4 = E("puerta", "autorizar-etapa", "--decision", "condicionado", "--por", "Ejecutiva", "--condiciones", "corregir R-001")
    check("limite-etapa + autorizar-etapa condicionada (el ERROR queda como condición)", r4.returncode == 0, (r4.stderr + r4.stdout)[-400:])
    junta(g, "autorizar-cierre", repo, arts=[("informe-fin-proyecto", "04-cierre/informe-fin-proyecto.md"), ("registro-aceptacion", "04-cierre/registro-aceptacion.md"),
                                             ("recomendaciones-seguimiento", "04-cierre/recomendaciones-seguimiento.md")])
    r5 = E("cierre"); r6 = E("puerta", "autorizar-cierre", "--decision", "condicionado", "--por", "Ejecutiva", "--condiciones", "corregir R-001")
    check("cierre + autorizar-cierre", r5.returncode == 0 and r6.returncode == 0, (r6.stderr + r6.stdout)[-400:])
    check("paquete de cierre listable", run([os.path.join(RAIZ, "skills", "pm-exportar", "scripts", "paquete.py"), "--proyecto", g, "listar", "cierre"], repo).returncode == 0)

def caso_v6_real(tmp):
    print("Caso A2 · BMAD 6.12.4 real (instalado con npx y artefactos escritos por sus skills)")
    import yaml
    repo = os.path.join(tmp, "v6real"); shutil.copytree(os.path.join(FIX, "bmad-v6.12-real"), repo)
    g = "gestion"; SP = os.path.join(S, "especificacion.py")
    run([os.path.join(S, "nuevo_proyecto.py"), "--ruta", g, "--nombre", "Portal socios", "--enfoque", "hibrido", "--ejecutivo", "Ejecutiva", "--gestor", "Gestor"], repo)
    r = run([B, "--proyecto", g, "detectar"], repo)
    det = json.loads(r.stdout[:r.stdout.rfind("}") + 1] or "{}")
    check("detectar: versión 6.12.4 desde manifest.yaml → soportada", det.get("version") == "6.12.4" and det.get("soporte") == "soportada"
          and det.get("version_fuente") == os.path.join("_bmad", "_config", "manifest.yaml"), str(det))
    inv = json.loads(run([B, "--proyecto", g, "inventario", "--json"], repo).stdout or "{}").get("artefactos", {})
    check("inventario: brief/prd/arquitectura/épicas final + sprint-status + spec de historia",
          all(inv.get(k, {}).get("estado_bmad") == "final" for k in ("brief", "prd", "arquitectura", "epicas")) and "estado-sprint" in inv
          and inv.get("historias", {}).get("rutas") == ["_bmad-output/implementation-artifacts/spec-1-1-alta-y-acceso-del-socio-con-segundo-factor.md"], str({k: v.get("rutas") for k, v in inv.items()}))
    run([B, "--proyecto", g, "requisitos"], repo)
    reqs = list(csv.DictReader(open(os.path.join(repo, g, "02-planificacion", "especificacion", "requisitos-bmad.csv"), encoding="utf-8")))
    cuenta = {}
    for q in reqs: cuenta[q["tipo"]] = cuenta.get(q["tipo"], 0) + 1
    ids = {q["id"] for q in reqs}
    check("requisitos: 12 FR, 6 NFR, 3 UJ, 8 SM (con SM-C1/SM-C2), 13 AD", cuenta == {"UJ": 3, "FR": 12, "NFR": 6, "SM": 8, "AD": 13}
          and {"SM-C1", "SM-C2", "FR-12", "AD-13"} <= ids, str(cuenta))
    tit = {q["id"]: q["titulo"] for q in reqs}
    check("títulos limpios (sin ** ni —)", tit["NFR-1"].startswith("Seguridad y privacidad: ") and tit["AD-1"].startswith("El núcleo") and "**" not in "".join(tit.values()), f"{tit['NFR-1'][:40]} | {tit['AD-1'][:40]}")
    sp = os.path.join(repo, "_bmad-output", "implementation-artifacts", "sprint-status.yaml")
    claves = [k for k in yaml.safe_load(open(sp, encoding="utf-8"))["development_status"] if re.match(r"^\d+-\d+", k)]
    run([B, "--proyecto", g, "backlog"], repo)
    ids_backlog = [f["id"] for f in csv.DictReader(open(os.path.join(repo, g, "02-planificacion", "backlog.csv"), encoding="utf-8"))]
    check("backlog: ids = claves de sprint-status (tildes y corte a 60)", ids_backlog == claves, f"{set(ids_backlog) ^ set(claves)}")
    d0 = next(csv.DictReader(open(os.path.join(repo, g, "02-planificacion", "backlog.csv"), encoding="utf-8")))["descripcion"]
    check("backlog: descripción = historia completa (no solo 'As a socio,')", "I want" in d0 and "So that" in d0, d0[:120])
    res = json.loads(run([SP, "--proyecto", g, "resumen", "--json"], repo).stdout or "{}")
    check("fachada: 42 ids, 10 historias, sin huecos; 1.1 ready-for-dev por su spec aprobado", res.get("requisitos") == 42 and res.get("historias") == 10
          and not res.get("sin_cobertura") and res.get("por_estado", {}).get("ready-for-dev") == 1, str(res))
    q = json.loads(run([SP, "--proyecto", g, "consultar", "FR-11", "--json"], repo).stdout or "{}")
    check("FR-11 trazado a nivel de épica (E-1 y E-3)", q.get("nivel_traza") == "epica" and q.get("epicas") == ["E-1", "E-3"], str({k: q.get(k) for k in ("nivel_traza", "epicas")}))
    check("consultar 1-2 → clave BMAD con tilde", "1-2-recuperación-de-acceso" in run([SP, "--proyecto", g, "consultar", "1-2"], repo).stdout)
    t = run([B, "--proyecto", g, "trazabilidad"], repo).stdout
    check("trazabilidad: sin FR huérfanos ni historias sin requisito", "sin historia: ninguno" in t and "sin requisito: ninguna" in t, t[-400:])
    check("línea base PRD final sin aviso", "AVISO" not in run([B, "--proyecto", g, "linea-base", "prd", "--version", "1.0", "--por", "Ejecutiva"], repo).stdout)
    check("verificar limpio", "Sin desvíos" in run([B, "--proyecto", g, "verificar"], repo).stdout)
    d = sanidad(g, repo)
    check("sanidad real: 0 ERROR", not codigos(d), str(codigos(d)))
    # bmad-build sincroniza sprint-status (in-progress/review); 'contexted' es un estado heredado de v6
    txt = open(sp, encoding="utf-8").read()
    txt = (txt.replace("1-1-alta-y-acceso-del-socio-con-segundo-factor: backlog", "1-1-alta-y-acceso-del-socio-con-segundo-factor: done")
              .replace("1-2-recuperación-de-acceso: backlog", "1-2-recuperación-de-acceso: contexted")
              .replace("1-3-consulta-de-saldos-de-ahorro-y-préstamos: backlog", "1-3-consulta-de-saldos-de-ahorro-y-préstamos: review"))
    open(sp, "w", encoding="utf-8").write(txt)
    av = json.loads(run([B, "--proyecto", g, "avance", "--json"], repo).stdout or "{}")
    check("avance: done 1, in-progress 1 (contexted), review 1, backlog 7", (av.get("done"), av.get("in-progress"), av.get("review"), av.get("backlog")) == (1, 1, 1, 7), str(av))
    prd = os.path.join(repo, "_bmad-output", "planning-artifacts", "prds", "prd-portal-socios-2026-10-17", "prd.md")
    open(prd, "a", encoding="utf-8").write("\n#### FR-13: Chat con un operador\n\nEl socio puede chatear con un operador.\n")
    v = json.loads(run([B, "--proyecto", g, "verificar", "--json"], repo).stdout or "[]")
    check("verificar detecta FR-13 agregado al PRD", any(h.get("ids_agregados") == ["FR-13"] for h in v), str(v))

def caso_v4(tmp):
    print("Caso B · BMAD v4 (docs/, .bmad-core)")
    repo = os.path.join(tmp, "v4"); shutil.copytree(os.path.join(FIX, "bmad-v4"), repo)
    run([os.path.join(S, "nuevo_proyecto.py"), "--ruta", "gestion", "--nombre", "Tareas", "--enfoque", "agil", "--idioma", "en"], repo)
    check("detectar v4", '"v4"' in run([B, "--proyecto", "gestion", "detectar"], repo).stdout)
    run([B, "--proyecto", "gestion", "backlog"], repo)
    r = run([os.path.join(S, "especificacion.py"), "--proyecto", "gestion", "resumen", "--json"], repo)
    res = json.loads(r.stdout or "{}")
    check("fachada v4: 3 ids, 2 historias, sin huecos", res.get("requisitos") == 3 and res.get("historias") == 2 and not res.get("sin_cobertura"), str(res))
    check("avance v4", "in-progress 1" in run([B, "--proyecto", "gestion", "avance"], repo).stdout)
    raiz = json.load(open(os.path.join(repo, "gestion", "estado.json"), encoding="utf-8"))["integraciones"]["bmad"]["raiz"]
    check("raíz BMAD guardada relativa al proyecto", raiz == "..", raiz)
    movido = os.path.join(tmp, "v4-movido"); shutil.move(repo, movido)
    check("repositorio movido: el puente sigue leyendo su propio BMAD", "in-progress 1" in run([B, "--proyecto", "gestion", "avance"], movido).stdout)
    copia = os.path.join(tmp, "v4-copia"); shutil.copytree(movido, copia)
    ej = os.path.join(copia, "gestion", "estado.json"); e = json.load(open(ej, encoding="utf-8"))
    e["integraciones"]["bmad"]["raiz"] = movido; json.dump(e, open(ej, "w", encoding="utf-8"))   # raíz absoluta heredada de v2.0
    r = subprocess.run([sys.executable, B, "--proyecto", "gestion", "avance"], cwd=copia, capture_output=True, text=True)
    check("raíz absoluta ajena: avisa y usa el BMAD del propio repositorio", "AVISO" in r.stderr and os.path.exists(os.path.join(copia, "gestion", "03-control", "reportes", "avance-bmad.csv")), r.stderr[-200:])

def caso_nativo(tmp):
    print("Caso C · especificación nativa (sin BMAD)")
    p = os.path.join(tmp, "nat")
    run([os.path.join(S, "nuevo_proyecto.py"), "--ruta", p, "--nombre", "Nativo", "--ejecutivo", "Ex", "--gestor", "Ge"], tmp)
    open(os.path.join(p, "02-planificacion", "requisitos.md"), "w", encoding="utf-8").write(
        "| Id | Requisito | Interesado | Categoría | Prioridad | Criterio | Método | Fase | Padre | Estado |\n|---|---|---|---|---|---|---|---|---|---|\n"
        "| REQ-001 | Login | Socio | solucion_funcional | alta | x | prueba | 1 | | aprobado |\n| REQ-002 | Reporte | Jefe | negocio | media | y | demostracion | 2 | | propuesto |\n")
    open(os.path.join(p, "02-planificacion", "wbs.csv"), "w", encoding="utf-8").write("codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref\n1,Login,paquete,Dev,10,100,REQ-001\n")
    r = run([os.path.join(S, "especificacion.py"), "--proyecto", p, "resumen", "--json"], tmp)
    res = json.loads(r.stdout or "{}")
    check("fachada nativa: REQ-002 sin cobertura", res.get("sin_cobertura") == ["REQ-002"], str(res))
    with open(os.path.join(p, "02-planificacion", "wbs.csv"), "a", encoding="utf-8") as f: f.write("2,Fantasma,paquete,Dev,1,1,REQ-099\n")
    check("sanidad nativa detecta REQ-099 (ESP-04)", "ESP-04" in codigos(sanidad(p, tmp)))
    check("evm modo ágil sin falsa excepción", "excepcion_prevista     False" in run([os.path.join(S, "evm.py"), "--pv", "60000", "--ev", "50000", "--ac", "58000", "--bac", "120000", "--modo", "agil", "--pct-no-must", "30"], tmp).stdout)

def caso_guardian(tmp):
    print("Caso D · hook guardian (separación de roles y escrituras protegidas)")
    g = os.path.join(RAIZ, "hooks", "guardian.py")
    def decide(herr, entrada, agente=None):
        d = {"tool_name": herr, "tool_input": entrada}
        if agente: d["agent_type"] = agente
        p = subprocess.run(["sh", os.path.join(RAIZ, "hooks", "py.sh"), g], input=json.dumps(d), capture_output=True, text=True)
        return "deny" if '"deny"' in p.stdout else "allow"
    casos = [
        ("Bash", {"command": "sed -i 's/a/b/' gestion/estado.json"}, None, "deny"),
        ("Bash", {"command": "echo x >> gestion/03-control/registros/riesgos.csv"}, None, "deny"),
        ("Bash", {"command": "python3 -c \"import json; json.dump({}, open('gestion/estado.json','w'))\""}, None, "deny"),
        ("Bash", {"command": "cp a.md gestion/00-direccion/historial/a.md"}, None, "deny"),
        ("Bash", {"command": "python3 x/estado.py --proyecto g puerta autorizar-etapa"}, "pm-method:pm-control-etapa", "deny"),
        ("Bash", {"command": "python3 x/estado.py --proyecto g aprobar --artefacto plan"}, "pm-inicio", "deny"),
        ("Bash", {"command": "echo x > ../_bmad-output/prd.md"}, "pm-method:pm-inicio", "deny"),
        ("Write", {"file_path": "/p/gestion/03-control/registros/acciones.csv"}, None, "deny"),
        ("Edit", {"file_path": "/p/_bmad-output/planning-artifacts/epics.md"}, "pm-method:pm-entrega", "deny"),
        ("Bash", {"command": "python3 /x/estado.py --proyecto g rol ejecutivo=Ana"}, "pm-method:pm-inicio", "deny"),
        ("Bash", {"command": "python3 /x/estado.py --proyecto g set fase=entrega --forzar --por Yo"}, "pm-method:pm-control-etapa", "deny"),
        ("Bash", {"command": "python3 /x/estado.py --proyecto g artefacto plan-agil --ruta 02-planificacion/agil/release.md"}, "pm-method:pm-planificacion", "allow"),
        ("Bash", {"command": "python3 /x/estado.py --proyecto g aprobar release-plan --por PO --nivel=product-owner"}, "pm-method:pm-planificacion", "allow"),
        ("Bash", {"command": "ls ../_bmad-output 2>&1"}, "pm-method:pm-inicio", "allow"),
        ("Bash", {"command": "cat gestion/estado.json"}, None, "allow"),
        ("Bash", {"command": "python3 x/estado.py --proyecto g puerta autorizar-proyecto --decision aprobado --por Junta"}, None, "deny"),
        ("Bash", {"command": "python3 x/estado.py --proyecto g tolerancia --nivel proyecto costo=10%"}, None, "deny"),
        ("Bash", {"command": "python3 x/estado.py --proyecto g resumen"}, None, "allow"),
        ("Bash", {"command": "S=/p/scripts && E=\"python3 $S/estado.py --proyecto gestion\" && $E tolerancia --nivel proyecto tiempo=1mes"}, None, "deny"),
        ("Bash", {"command": "E=\"python3 /p/estado.py --proyecto g\"; $E resumen; $E artefacto plan-agil --ruta x.md"}, None, "allow"),
        ("Bash", {"command": "python3 -c \"import subprocess; subprocess.run(['python3', '/p/estado.py', '--proyecto', 'g', 'puerta', 'autorizar-proyecto', '--decision', 'aprobado'])\""}, None, "deny"),
        ("Bash", {"command": "grep -n tolerancia /p/estado.py | head"}, None, "allow"),
        ("Bash", {"command": "python3 /p/puertas.py --proyecto g confirmar autorizar-etapa --por Junta"}, None, "deny"),
        ("Bash", {"command": "python3 /p/puertas.py --proyecto g confirmar autorizar-etapa --por Junta"}, "pm-method:pm-control", "deny"),
        ("Bash", {"command": "python3 /p/puertas.py --proyecto g confirmar autorizar-etapa --por Junta"}, "pm-method:pm-director", "allow"),
        ("Bash", {"command": "python3 /p/puertas.py --proyecto g verificar autorizar-etapa"}, None, "allow"),
        ("Edit", {"file_path": "/p/gestion/00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md"}, None, "deny"),
        ("Bash", {"command": "sed -i 's/- \\[ \\]/- [x]/' gestion/00-direccion/decisiones/2026-10-17-verificacion-autorizar-etapa.md"}, None, "deny"),
        ("Bash", {"command": "python3 /p/puertas.py --proyecto g lista autorizar-etapa"}, "pm-method:pm-control", "allow"),
        ("Bash", {"command": "python3 x/estado.py --proyecto g puerta autorizar-etapa"}, "pm-method:pm-director", "allow"),
        ("Bash", {"command": "python3 x/estado.py --proyecto g aprobar --artefacto plan --nivel gestor"}, "pm-method:pm-inicio", "allow"),
        ("Bash", {"command": "python3 x/registro.py --proyecto g agregar riesgos > /tmp/salida.txt"}, None, "allow"),
        ("Edit", {"file_path": "/p/gestion/01-inicio/plan-proyecto.md"}, None, "allow"),
        ("Edit", {"file_path": "/p/_bmad-output/planning-artifacts/epics.md"}, None, "allow"),
    ]
    fu = os.path.join(tmp, "fu", "03-control", "fuentes"); os.makedirs(fu, exist_ok=True)
    open(os.path.join(fu, "jira-2026-10-01.json"), "w").write("{}")
    casos += [("Edit", {"file_path": os.path.join(fu, "jira-2026-10-01.json")}, None, "deny"),
              ("Write", {"file_path": os.path.join(fu, "jira-2026-10-17.json")}, None, "allow")]
    malos = [(h, e, a, esp) for h, e, a, esp in casos if decide(h, e, a) != esp]
    check(f"guardian: {len(casos) - len(malos)}/{len(casos)} decisiones correctas", not malos, str(malos)[:600])

def caso_puertas(tmp):
    print("Caso E · ciclo de puertas PRINCE2 (set restringido, tolerancias de etapa, nivel ejecutivo)")
    p = os.path.join(tmp, "pu"); ES = os.path.join(S, "estado.py")
    run([os.path.join(S, "nuevo_proyecto.py"), "--ruta", p, "--nombre", "Puertas", "--ejecutivo", "Ex", "--gestor", "Ge"], tmp)
    r = subprocess.run([sys.executable, ES, "--proyecto", p, "set", "fase=entrega"], capture_output=True, text=True)
    check("set fase sin --forzar se rechaza", r.returncode != 0 and "puerta" in (r.stderr + r.stdout))
    junta(p, "autorizar-inicio", tmp, arts=[("project-brief", "01-inicio/project-brief.md")])
    run([ES, "--proyecto", p, "puerta", "autorizar-inicio", "--decision", "aprobado", "--por", "Ex"], tmp)
    junta(p, "autorizar-proyecto", tmp)
    r = subprocess.run([sys.executable, ES, "--proyecto", p, "puerta", "autorizar-proyecto", "--decision", "condicionado", "--por", "Junta"], capture_output=True, text=True)
    e = json.load(open(os.path.join(p, "estado.json"), encoding="utf-8"))
    check("condicionado con bloqueos: se registra y los suma como condiciones", r.returncode == 0 and "tolerancias de proyecto" in e["puertas"][-1].get("condiciones", ""), (r.stderr + r.stdout)[-300:])
    run([ES, "--proyecto", p, "tolerancia", "--nivel", "proyecto", "tiempo=1mes", "costo=10%"], tmp)
    run([ES, "--proyecto", p, "tolerancia", "--nivel", "etapa", "costo=5%"], tmp)
    junta(p, "autorizar-etapa", tmp, arts=[("plan-etapa-2", "02-planificacion/plan-etapa-2.md"), ("plan-etapa-3", "02-planificacion/plan-etapa-3.md"),
                                           ("informe-fin-etapa-2", "03-control/reportes/informe-fin-etapa-2.md")])
    run([ES, "--proyecto", p, "puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Junta", "--inicio", "2026-11-02"], tmp)
    e = json.load(open(os.path.join(p, "estado.json"), encoding="utf-8"))
    check("autorizar-etapa conserva tolerancias y usa --inicio", e["tolerancias"]["etapa"].get("costo") == "5%" and e["etapa_actual"]["inicio"] == "2026-11-02"
          and e["fase"] == "entrega" and e["etapa_actual"]["numero"] == 2, json.dumps(e["etapa_actual"]))
    run([ES, "--proyecto", p, "limite-etapa"], tmp)
    run([ES, "--proyecto", p, "puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Junta", "--tol", "costo=10%", "tiempo=2sem"], tmp)
    e = json.load(open(os.path.join(p, "estado.json"), encoding="utf-8"))
    check("--tol fija las tolerancias de la nueva etapa", e["tolerancias"]["etapa"].get("costo") == "10%" and e["tolerancias"]["etapa"].get("tiempo") == "2sem")
    run([ES, "--proyecto", p, "set", "proceso_actual=SB", "--forzar", "--por", "Ex"], tmp)
    dec = open(os.path.join(p, "03-control", "registros", "decisiones.csv"), encoding="utf-8").read()
    check("set --forzar queda anotado en decisiones.csv", "corrección forzada" in dec)
    open(os.path.join(p, "00-direccion", "pid.md"), "w", encoding="utf-8").write("---\ntipo: pid\nestado: borrador\n---\n# PID\n")
    run([ES, "--proyecto", p, "artefacto", "pid", "--ruta", "00-direccion/pid.md"], tmp)
    run([ES, "--proyecto", p, "aprobar", "pid", "--por", "Junta", "--version", "1.0"], tmp)
    check("aprobar crea la copia congelada en historial/", os.path.exists(os.path.join(p, "00-direccion", "historial", "pid-v1.0.md")))
    run([os.path.join(S, "registro.py"), "--proyecto", p, "agregar", "decisiones", "--campo", "decision=Prioridad de pagos", "--campo", "decidido_por=Ex", "--campo", "nivel=ejecutivo"], tmp)
    check("nivel 'ejecutivo' aceptado en decisiones", "ejecutivo" in open(os.path.join(p, "03-control", "registros", "decisiones.csv"), encoding="utf-8").read())

def caso_regresiones(tmp):
    print("Caso F · regresiones v2.1 (cpm, evm, okr, exportar, estado resumen)")
    d = os.path.join(tmp, "rg"); os.makedirs(d)
    open(os.path.join(d, "act.csv"), "w", encoding="utf-8").write("id,nombre,duracion,predecesoras,recurso,wbs\nA,Analisis,5,,Ana,1.1\nB,Construccion,10,A,Luis,1.2\nH,Aceptacion,0,B,,2.1\n")
    run([os.path.join(S, "cpm.py"), "act.csv", "--inicio", "2026-11-02", "--mspdi", "c.xml", "--titulo", "Faro"], d)
    x = open(os.path.join(d, "c.xml"), encoding="utf-8").read()
    tareas = re.findall(r"<Task>.*?<WBS>([^<]*)</WBS>.*?<Start>([^<]*)</Start>.*?<Finish>([^<]*)</Finish>", x, re.S)
    check("MSPDI: ninguna tarea termina antes de empezar (resumen de solo hitos)", tareas and all(f[:10] >= st[:10] for _, st, f in tareas), str(tareas))
    ev = run([os.path.join(S, "evm.py"), "--pv", "60000", "--ev", "50000", "--ac", "58000", "--bac", "120000", "--tol-costo", "5", "--json"], d).stdout
    j = json.loads(ev or "{}"); j = j[0] if isinstance(j, list) else j
    check("EVM: VAC_pct con el signo de VAC y sobrecosto_pct positivo", j.get("VAC", 0) < 0 and j.get("VAC_pct", 0) < 0 and j.get("sobrecosto_pct", 0) > 0, str(j)[:300])
    open(os.path.join(d, "okr.csv"), "w", encoding="utf-8").write("id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas\n"
        "O-1,objetivo,,Socios autogestionados,,,,,,Ana,,SM-1,,\nKR-1,kr,O-1,Bajar consultas,consultas,100,50,80,n,Ana,2027-06-30,SM-C1,media,\n")
    o = run([os.path.join(RAIZ, "skills", "pm-okr", "scripts", "okr.py"), "okr.csv", "--corte", "2026-10-17"], d).stdout
    check("OKR: vínculo SM-C1 (métrica de contrapeso de BMAD 6.12) aceptado", "KR-1: sin vínculo" not in o, o[-300:])
    open(os.path.join(d, "x.md"), "w").write("# x\n")
    r = subprocess.run([sys.executable, os.path.join(S, "exportar.py"), "xlsx", "--entrada", "x.md", "--salida", "x.xlsx"], cwd=d, capture_output=True, text=True)
    check("exportar xlsx rechaza un .md", r.returncode != 0 and not os.path.exists(os.path.join(d, "x.xlsx")), r.stderr[-200:])
    p = os.path.join(d, "pr"); run([os.path.join(S, "nuevo_proyecto.py"), "--ruta", p, "--nombre", "R", "--ejecutivo", "E", "--gestor", "G"], d)
    check("estado.py resumen", "Puerta" in run([os.path.join(S, "estado.py"), "--proyecto", p, "resumen"], d).stdout or "autorizar-inicio" in run([os.path.join(S, "estado.py"), "--proyecto", p, "resumen"], d).stdout)

def caso_puertas_bmad(tmp):
    print("Caso G · verificación de puertas con BMAD (PRD/arquitectura final, gate de preparación, lista de control)")
    repo = os.path.join(tmp, "pg"); shutil.copytree(os.path.join(FIX, "bmad-v6.12-real"), repo); g = "gestion"
    ES = lambda *a: run([os.path.join(S, "estado.py"), "--proyecto", g] + list(a), repo)
    PUr = lambda *a: run([PU, "--proyecto", g] + list(a), repo)
    run([os.path.join(S, "nuevo_proyecto.py"), "--ruta", g, "--nombre", "PG", "--ejecutivo", "Marta", "--gestor", "Ana"], repo)
    run([B, "--proyecto", g, "detectar"], repo)
    junta(g, "autorizar-inicio", repo, arts=[("project-brief", "01-inicio/project-brief.md")]); ES("puerta", "autorizar-inicio", "--decision", "aprobado", "--por", "Marta")
    ES("tolerancia", "--nivel", "proyecto", "tiempo=1mes", "costo=10%")
    prd = glob.glob(os.path.join(repo, "_bmad-output", "planning-artifacts", "prds", "*", "prd.md"))[0]; txt = open(prd, encoding="utf-8").read()
    open(prd, "w", encoding="utf-8").write(txt.replace("status: final", "status: draft", 1))
    junta(g, "autorizar-proyecto", repo, arts=[("business-case", "00-direccion/business-case.md"), ("pid", "00-direccion/pid.md")])
    r = ES("puerta", "autorizar-proyecto", "--decision", "aprobado", "--por", "Marta")
    check("P-07: PRD de BMAD en draft bloquea autorizar-proyecto", r.returncode != 0 and "no está final" in (r.stderr + r.stdout), (r.stderr + r.stdout)[-300:])
    open(prd, "w", encoding="utf-8").write(txt)
    r = ES("puerta", "autorizar-proyecto", "--decision", "aprobado", "--por", "Marta")
    check("autorizar-proyecto con PRD final y lista confirmada", r.returncode == 0, (r.stderr + r.stdout)[-300:])
    dec = open(os.path.join(repo, g, "03-control", "registros", "decisiones.csv"), encoding="utf-8").read()
    check("decisiones.csv referencia la lista de verificación", "verificacion-autorizar-proyecto" in dec)
    run([B, "--proyecto", g, "linea-base", "prd", "--version", "1.0", "--por", "Marta"], repo)
    junta(g, "autorizar-etapa", repo, arts=[("plan-etapa-2", "02-planificacion/plan-etapa-2.md")])
    v = json.loads(PUr("verificar", "autorizar-etapa", "--json").stdout or "{}")
    check("E-10: sin veredicto de preparación BMAD → aviso (no bloquea)", any("preparación de BMAD" in x for x in v.get("avisos", [])), str(v)[:300])
    time.sleep(1.1)
    open(os.path.join(repo, "_bmad-output", "planning-artifacts", "implementation-readiness.md"), "w").write("# FAIL\n- historia 2.1 sin decisión de arquitectura\n")
    r = ES("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Marta", "--tol", "costo=5%")
    check("E-10: hallazgos FAIL guardados por BMAD bloquean autorizar-etapa", r.returncode != 0 and "FAIL" in (r.stderr + r.stdout), (r.stderr + r.stdout)[-300:])
    time.sleep(1.1)
    PUr("preparacion-bmad", "--resultado", "CONCERNS", "--por", "Arquitecto: Luis", "--nota", "falta UX de la bandeja")
    v = json.loads(PUr("verificar", "autorizar-etapa", "--json").stdout or "{}")
    check("E-10: CONCERNS registrado después → condición, no bloqueo", any("CONCERNS" in x for x in v.get("condiciones", [])) and not any("FAIL" in x for x in v.get("bloqueos", [])), str(v)[:400])
    PUr("lista", "autorizar-etapa"); PUr("confirmar", "autorizar-etapa", "--por", "Junta", "--no", "V-03=business case sin actualizar")
    r = ES("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Marta", "--tol", "costo=5%")
    check("lista con un ítem que no cumple bloquea 'aprobado'", r.returncode != 0 and "V-03" in (r.stderr + r.stdout), (r.stderr + r.stdout)[-300:])
    PUr("lista", "autorizar-etapa"); PUr("confirmar", "autorizar-etapa", "--por", "Junta")
    r = ES("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Marta", "--tol", "costo=5%")
    e = json.load(open(os.path.join(repo, g, "estado.json"), encoding="utf-8"))
    check("autorizar-etapa aprobada con observación CONCERNS registrada en la puerta", r.returncode == 0 and any("CONCERNS" in x for x in e["puertas"][-1].get("verificacion", {}).get("observaciones", [])), (r.stderr + r.stdout)[-300:])
    est = json.loads(PUr("estado", "--json").stdout or "{}")
    check("puertas.py estado (insumo de informes): 3 puertas, observación CONCERNS y próxima puerta", len(est.get("puertas", [])) == 3
          and any("CONCERNS" in o for r in est["puertas"] for o in r["observaciones"]) and (est.get("proxima") or {}).get("puerta") == "autorizar-etapa", str(est)[:300])
    check("estado.py resumen muestra última y próxima puerta", "Próxima puerta" in ES("resumen").stdout and "Última puerta" in ES("resumen").stdout)

def main():
    tmp = tempfile.mkdtemp(prefix="pm-method-pruebas-")
    try:
        caso_v6(tmp); caso_v6_real(tmp); caso_v4(tmp); caso_nativo(tmp); caso_guardian(tmp); caso_puertas(tmp); caso_puertas_bmad(tmp); caso_regresiones(tmp)
    finally:
        if "--conservar" not in sys.argv: shutil.rmtree(tmp, ignore_errors=True)
        else: print(f"Conservado en {tmp}")
    print(f"\nResultado: {RES['ok']} OK · {RES['fallo']} FALLO")
    sys.exit(1 if RES["fallo"] else 0)

if __name__ == "__main__":
    main()
