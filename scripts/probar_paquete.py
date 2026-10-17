#!/usr/bin/env python3
"""Pruebas de regresión de punta a punta del paquete pm-method (para el mantenedor).
End-to-end regression tests: BMAD v6, BMAD v4 and native specification, gates, backbone sync and health checks.

Uso / Usage: python3 scripts/probar_paquete.py [--conservar]
Correr después de cualquier cambio del paquete o al adoptar una versión nueva de BMAD (reemplazar o agregar un
fixture en scripts/pruebas/fixtures/ con artefactos reales de esa versión). Requiere PyYAML.
"""
import csv, json, os, shutil, subprocess, sys, tempfile

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
    check("puerta autorizar-inicio", E("puerta", "autorizar-inicio", "--decision", "aprobado", "--por", "Ejecutiva").returncode == 0)
    check("puerta fuera de orden rechazada", E("puerta", "autorizar-cierre", "--decision", "aprobado", "--por", "X").returncode != 0)
    E("tolerancia", "--nivel", "proyecto", "tiempo=±1 mes", "costo=±10 %")
    check("puerta autorizar-proyecto", E("puerta", "autorizar-proyecto", "--decision", "aprobado", "--por", "Ejecutiva").returncode == 0)
    check("línea base PRD v1.0", run([B, "--proyecto", g, "linea-base", "prd", "--version", "1.0", "--por", "Ejecutiva"], repo).returncode == 0)
    check("puerta autorizar-etapa", E("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Ejecutiva", "--etapa-nombre", "Release 1").returncode == 0)
    E("tolerancia", "--nivel", "etapa", "costo=±5 %")
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
    check("limite-etapa + autorizar-etapa", E("limite-etapa").returncode == 0 and E("puerta", "autorizar-etapa", "--decision", "aprobado", "--por", "Ejecutiva").returncode == 0)
    check("cierre + autorizar-cierre", E("cierre").returncode == 0 and E("puerta", "autorizar-cierre", "--decision", "aprobado", "--por", "Ejecutiva").returncode == 0)
    check("paquete de cierre listable", run([os.path.join(RAIZ, "skills", "pm-exportar", "scripts", "paquete.py"), "--proyecto", g, "listar", "cierre"], repo).returncode == 0)

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

def main():
    tmp = tempfile.mkdtemp(prefix="pm-method-pruebas-")
    try:
        caso_v6(tmp); caso_v4(tmp); caso_nativo(tmp)
    finally:
        if "--conservar" not in sys.argv: shutil.rmtree(tmp, ignore_errors=True)
        else: print(f"Conservado en {tmp}")
    print(f"\nResultado: {RES['ok']} OK · {RES['fallo']} FALLO")
    sys.exit(1 if RES["fallo"] else 0)

if __name__ == "__main__":
    main()
