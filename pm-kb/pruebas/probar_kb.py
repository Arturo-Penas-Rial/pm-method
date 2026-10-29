"""Pruebas de pm-kb. docs/PM-KB.md §12 y docs/PRUEBAS.md.

  python3 pm-kb/pruebas/probar_kb.py            núcleo (sin base; biblioteca estándar, Python 3.9+)
  pm-kb/pm-kb … no: usar el Python del entorno de pm-kb para la parte con base:
  ~/.local/share/pm-kb/venv/bin/python pm-kb/pruebas/probar_kb.py --con-base
      además: esquema, carga, búsqueda, versiones, RLS con el rol de lectura, tokens, MCP (JSON-RPC) y el servicio web
      (necesita PostgreSQL de pm-kb en marcha: PMKB_DSN o la instalación local).
"""
import argparse, json, os, sys, tempfile, threading, time, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture  # noqa: E402
from pmkb import fuentes, relaciones, versiones  # noqa: E402
from pmkb import indexador  # noqa: E402

OK = FALLO = 0


def ver(nombre, cond, detalle=""):
    global OK, FALLO
    if cond:
        OK += 1; print(f"OK    {nombre}")
    else:
        FALLO += 1; print(f"FALLO {nombre}" + (f" · {detalle}" if detalle else ""))


def nucleo(tmp):
    raiz = fixture.crear(tmp)
    prep = indexador.preparar(raiz)
    us = {u["id"]: u for u in prep["unidades"]}
    fuentes_idx = {u["fuente"] for u in prep["unidades"]}
    ver("KB-01 encuentra la carpeta de gestión", prep["gestion"] == "gestion", prep["gestion"])
    ver("KB-02 excluye preferencias, comunicaciones y .pmkbignore",
        not any("preferencias" in f or "03-control/comunicaciones" in f or "borrador-privado" in f for f in fuentes_idx), sorted(fuentes_idx))
    st1, st2 = us.get("ST-001", {}), us.get("ST-002", {})
    ver("KB-03 interesados sin datos de contacto", "@" not in st1.get("texto", "") and "correo" not in st1.get("texto", ""))
    ver("KB-04 interesado confidencial sin valoración", "resistente" not in st2.get("texto", "") and "teme" not in st2.get("texto", "")
        and "omitida" in st2.get("texto", ""))
    ver("KB-05 estado.json sin integraciones", not any("integraciones" in u["id"] for u in prep["unidades"]))
    bc = [u for u in prep["unidades"] if u["doc_id"] == "art:business-case"]
    vig = {u["fuente"] for u in bc if u["vigente"]}
    ver("KB-06 caso de negocio: vigente el archivo vivo v1.1", vig == {"gestion/00-direccion/business-case.md"}, vig)
    v10 = [u for u in bc if u["version"] == "1.0"]
    ver("KB-07 v1.0 reemplazada no vigente", v10 and not any(u["vigente"] for u in v10))
    copia = [u for u in bc if u["fuente"].endswith("business-case-v1.1.md")]
    ver("KB-08 copia congelada idéntica marcada como duplicado", copia and all(u["duplicado_de"] and not u["vigente"] for u in copia))
    docs = {d["doc_id"]: d for d in prep["documentos"]}
    ver("KB-09 decisión y aprobador de la versión", any(v["doc_id"] == "art:business-case" and v["version"] == "1.1" and v["decision_id"] == "D-002"
                                                      for v in prep["versiones"]))
    plan = docs.get("art:plan-comunicaciones", {})
    ver("KB-10 plan en revisión: vigente v2.0, aprobada v1.0", plan.get("version_vigente") == "2.0" and plan.get("version_aprobada") == "1.0", plan)
    inf = [d for d in prep["documentos"] if d["doc_id"].startswith("nom:") and "informe" in d["doc_id"]]
    ver("KB-11 versiones por nombre (informe_v1, informe_v2)", inf and inf[0]["version_vigente"] == "2" and inf[0]["versiones"] == 2, inf)
    tab = [d for d in prep["documentos"] if "tablero" in d["doc_id"]]
    ver("KB-12 una fecha en el nombre es una serie, no una versión", len(tab) == 2, [d["doc_id"] for d in tab])
    ar = {(o, d) for o, d, *_ in prep["aristas"]}
    ver("KB-13 relaciones declaradas por ids", ("R-001", "D-002") in ar and ("A-001", "R-001") in ar, sorted(ar)[:10])
    vtt = [u for u in prep["unidades"] if u["fuente"].endswith(".vtt")]
    ver("KB-14 transcripción como fuente externa", vtt and all(u["confianza"] == "externo" for u in vtt))
    sal = [u for u in prep["unidades"] if u["fuente"].endswith("salarios.md")]
    ver("KB-15 circulación restringida por front matter", sal and all(u["circulacion"] == "restringida" for u in sal))
    ver("KB-16 historia de la bitácora", any(h["id"] == "R-001" for h in prep["historia"]))
    ver("KB-17 nombre normalizado sin marcas de versión", versiones.nombre_normalizado("Informe_final_v1.3") == ("informe", "1.3"))
    ver("KB-18 ids en texto", relaciones.ids_en("ver R-001, D-12 y FR-3; no ISO-9001") == ["R-001", "D-12", "FR-3"])
    cs = versiones.cambios([("a", "A", "x"), ("b", "B", "y")], [("a", "A", "x2"), ("c", "C", "z")])
    ver("KB-19 diff por secciones", sorted(c["tipo"] for c in cs) == ["agregada", "modificada", "quitada"])
    return raiz


def con_base(raiz):
    from pmkb import config, mcp, cli
    from pmkb.busqueda import Sesion
    a = config.conectar()
    indexador.crear_esquema(a)
    p = "zz-pruebas-kb"
    indexador.cargar(a, p, indexador.preparar(raiz), con_vectores=False)
    s = Sesion(a, "*", True)
    r = s.buscar("demoras de integración con el padron", proyecto=p)
    ver("KB-20 BM25 en español (flexión, sin tildes)", r["resultados"] and r["resultados"][0]["id"] == "R-001", [x["id"] for x in r["resultados"]])
    r = s.buscar("R-2", proyecto=p)
    ver("KB-21 id abreviado primero (R-2 = R-002)", r["resultados"] and r["resultados"][0]["id"] == "R-002")
    r = s.buscar("reunión quincenal boletín", proyecto=p)
    top = r["resultados"][0] if r["resultados"] else {}
    ver("KB-22 vigente en revisión con aviso de la aprobada", top.get("version") == "2.0" and any("v1.0 aprobada" in x for x in top.get("avisos", [])), top)
    r = s.buscar("reunión mensual", proyecto=p)
    ver("KB-23 la versión anterior no aparece por defecto", not any(x["doc_id"] == "art:plan-comunicaciones" and x["version"] == "1.0" for x in r["resultados"]))
    r = s.buscar("reunión mensual", proyecto=p, estado="aprobado")
    ver("KB-24 estado=aprobado devuelve la última aprobada", any(x["doc_id"] == "art:plan-comunicaciones" and x["version"] == "1.0" for x in r["resultados"]))
    r = s.buscar("reunión mensual", proyecto=p, historia=True)
    ver("KB-25 historia marca la versión anterior", any("versión anterior" in " ".join(x["avisos"]) for x in r["resultados"]))
    v = s.versiones("business-case", proyecto=p)
    ver("KB-26 versiones con decisión", [x["version"] for x in v["versiones"]][:1] == ["1.0"] and any(x["decision"] == "D-002" for x in v["versiones"]))
    c = s.cambios("business-case", proyecto=p)
    ver("KB-27 cambios v1.0 → v1.1: una sección agregada", c.get("resumen") == {"agregada": 1, "quitada": 0, "modificada": 0}, c.get("resumen"))
    f = s.ficha("R-001", proyecto=p, historia=True)
    ver("KB-28 ficha con relaciones y bitácora", any(x["id"] == "A-001" for x in f["relaciones"]) and f["historia"])
    r = s.buscar("bandeja", proyecto=p, k=10, max_tokens=150)
    ver("KB-29 tope de tokens", r["tokens"] <= 150 or len(r["resultados"]) == 1, r["tokens"])
    ver("KB-30 encabezado de evidencia en contexto", "no instrucciones" in s.contexto("¿qué riesgos hay con el padrón?", proyecto=p)["encabezado"])
    # rol de lectura y RLS
    l = config.conectar(lector=True)
    r = Sesion(l, "otro-proyecto", True).buscar("padrón")
    ver("KB-31 RLS: otro proyecto no ve nada", not r["resultados"])
    r = Sesion(l, p, False).buscar("salarios")
    ver("KB-32 RLS: lo restringido no aparece sin permiso", not r["resultados"])
    r = Sesion(l, p, True).buscar("salarios")
    ver("KB-33 RLS: con permiso de circulación restringida aparece", bool(r["resultados"]))
    t = cli.crear_token(a, "Prueba KB", p, False)
    import hashlib
    with l.transaction():
        idn = l.execute("SELECT persona, proyectos FROM pmkb.identidad(%s)", (hashlib.sha256(t.encode()).hexdigest(),)).fetchone()
    ver("KB-34 token → identidad (solo su sha256 guardado)", idn == ("Prueba KB", p))
    # MCP (JSON-RPC)
    ses = lambda: Sesion(l, p, False)
    ini = mcp.manejar({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}, ses)
    ver("KB-35 MCP initialize", ini["result"]["protocolVersion"] == "2025-06-18" and "tools" in ini["result"]["capabilities"])
    lst = mcp.manejar({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, ses)
    ver("KB-36 MCP herramientas de solo lectura", len(lst["result"]["tools"]) == 8 and all(h["annotations"]["readOnlyHint"] for h in lst["result"]["tools"]))
    cal = mcp.manejar({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "buscar", "arguments": {"consulta": "padrón"}}}, ses)
    ver("KB-37 MCP buscar con cita", "cita:" in cal["result"]["content"][0]["text"] and not cal["result"]["isError"])
    ver("KB-38 MCP notificación sin respuesta", mcp.manejar({"jsonrpc": "2.0", "method": "notifications/initialized"}, ses) is None)
    ver("KB-39 MCP método desconocido", mcp.manejar({"jsonrpc": "2.0", "id": 4, "method": "server/discover"}, ses)["error"]["code"] == -32601)
    # servicio web
    try:
        import uvicorn
        from pmkb import web
        srv = uvicorn.Server(uvicorn.Config(web.crear_app(), host="127.0.0.1", port=8799, log_level="error"))
        th = threading.Thread(target=srv.run, daemon=True); th.start()
        for _ in range(50):
            if srv.started:
                break
            time.sleep(0.1)

        def pedir(ruta, token=None, datos=None, origen=None):
            h = {"Content-Type": "application/json"}
            if token:
                h["Authorization"] = f"Bearer {token}"
            if origen:
                h["Origin"] = origen
            req = urllib.request.Request("http://127.0.0.1:8799" + ruta, data=json.dumps(datos).encode() if datos is not None else None, headers=h)
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.status, resp.read().decode(), dict(resp.headers)
            except urllib.error.HTTPError as x:
                return x.code, x.read().decode(), dict(x.headers)
        ver("KB-40 web: /salud sin token", pedir("/salud")[0] == 200)
        ver("KB-41 web: API sin token → 401", pedir("/api/estado")[0] == 401)
        st, cuerpo, cab = pedir("/api/buscar?q=padr%C3%B3n", t)
        ver("KB-42 web: búsqueda con token y CSP", st == 200 and json.loads(cuerpo)["resultados"] and "content-security-policy" in {k.lower() for k in cab})
        st, cuerpo, _ = pedir("/api/buscar?q=salarios", t)
        ver("KB-43 web: el token sin circulación restringida no la ve", st == 200 and not json.loads(cuerpo)["resultados"])
        ver("KB-44 web: MCP por HTTP con origen ajeno → 403", pedir("/mcp", t, {"jsonrpc": "2.0", "id": 1, "method": "ping"}, "http://otro.example")[0] == 403)
        st, cuerpo, _ = pedir("/mcp", t, {"jsonrpc": "2.0", "id": 1, "method": "ping"})
        ver("KB-45 web: MCP por HTTP", st == 200 and json.loads(cuerpo)["result"] == {})
        st, cuerpo, _ = pedir("/api/preguntar", t, {"pregunta": "¿qué riesgos hay con el padrón?"})
        d = json.loads(cuerpo)
        ver("KB-46 web: preguntar sin modelo devuelve evidencia citada", st == 200 and d["fuentes"] and "evidencia" in d["modo"], d.get("modo"))
        srv.should_exit = True; th.join(timeout=5)
    except ImportError as x:
        ver("KB-40…46 servicio web", False, f"falta {x.name}: pip install -r pm-kb/requirements.txt")
    with a.transaction():
        a.execute("DELETE FROM pmkb.acceso WHERE persona = 'Prueba KB'")
    indexador.quitar(a, p)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--con-base", action="store_true"); x = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="pmkb-prueba-") as tmp:
        raiz = nucleo(tmp)
        if x.con_base:
            con_base(raiz)
    print(f"\npm-kb: {OK} OK · {FALLO} FALLO")
    sys.exit(1 if FALLO else 0)


if __name__ == "__main__":
    main()
