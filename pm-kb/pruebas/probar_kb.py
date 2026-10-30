"""Pruebas de pm-kb. docs/PM-KB.md §12 y docs/PRUEBAS.md.

  python3 pm-kb/pruebas/probar_kb.py            núcleo (sin base; biblioteca estándar, Python 3.9+)
  pm-kb/pm-kb … no: usar el Python del entorno de pm-kb para la parte con base:
  ~/.local/share/pm-kb/venv/bin/python pm-kb/pruebas/probar_kb.py --con-base
      además: esquema (y sus migraciones 2 → 3 y 3 → 4), carga, búsqueda, versiones, ubicaciones y movimientos, enlaces,
      tablero publicado e instantáneas, RLS con el rol de lectura, tokens, MCP (JSON-RPC), el servicio web (portal,
      documentos aislados, «actualizar ahora», sesiones, enlaces compartidos y tableros por actor) y `vigilar` (necesita PostgreSQL de pm-kb en marcha: PMKB_DSN o la
      instalación local). El servicio web de la prueba escucha en un puerto libre entre 8800 y 8899.
  Las pantallas del portal (Playwright): pruebas/pantallas.py.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, threading, time, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture  # noqa: E402
import proyecto_tablero  # noqa: E402
from pmkb import documentos, enlaces, fuentes, relaciones, versiones  # noqa: E402
from pmkb import indexador  # noqa: E402
from pmkb import tablero as TB  # noqa: E402

OK = FALLO = 0
VIGILAR = []


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
    res = next((u for u in prep["unidades"] if u["id"].endswith("estado.json#resumen")), {})
    filas = [u for u in prep["unidades"] if u.get("registro") and "estado:" in (u.get("texto") or "")]
    ver("KB-58 el extracto de una fila de registro empieza por su estado (un extracto recortado no la hace parecer abierta)",
        filas and all(u["texto"].startswith("estado:") for u in filas), [u["id"] for u in filas if not u["texto"].startswith("estado:")][:5])
    ver("KB-47 resumen de estado.json con las claves del proyecto (proyecto, proceso, etapa)",
        res.get("titulo") == "Estado del proyecto · Prueba KB" and "proceso_actual: CS" in res.get("texto", "")
        and "etapa_actual: 2 · Release 1" in res.get("texto", "") and not any(u["id"].endswith("estado.json#proyecto") for u in prep["unidades"]),
        (res.get("titulo"), res.get("texto")))
    ver("KB-51 puerto: TIME_WAIT de un servicio detenido no lo bloquea; un proceso escuchando sí", *puerto_reusable())
    prop = lambda reg, campos: " ".join(u["texto"] for u in fuentes.unidades_json(
        "gestion/03-control/propuestas/P-001.json", json.dumps({"id": "P-001", "estado": "pendiente", "registro": reg, "operacion": "agregar", "campos": campos})))
    p_r = prop("riesgos", {"evento": "Saturación del centro de llamadas"})
    p_s = prop("stakeholders", {"nombre": "Ana", "correo": "ana@example.org", "actitud": "resistente"})
    p_e = prop("envios", {"destinatario": "ana@example.org"})
    ver("KB-53 propuestas: el contenido propuesto (campos) se indexa, sin contacto ni valoración de interesados ni envíos",
        "campos.evento: Saturación del centro de llamadas" in p_r and "campos.nombre: Ana" in p_s and "example.org" not in p_s + p_e
        and "resistente" not in p_s, (p_r, p_s, p_e))
    ubicaciones_nucleo(raiz, tmp)
    portal_nucleo(tmp)
    return raiz


def portal_nucleo(tmp):
    """KB-79…KB-86: lo del portal que no necesita base: historia de artefactos, enlaces de decisiones, tablero del núcleo
    en solo lectura e instantáneas, poda por circulación, cartera y documentos aislados."""
    g = Path(tmp) / "bit"
    g.mkdir()
    lineas = [{"n": 1, "fecha": "2026-10-01", "operacion": "artefacto", "archivo": "estado.json", "claves": ["artefactos.business-case", "version_estado"]},
              {"n": 2, "fecha": "2026-10-02", "operacion": "aprobar", "archivo": "estado.json", "por": "Junta", "claves": ["artefactos.business-case"]},
              {"n": 3, "fecha": "2026-10-03", "operacion": "rol", "archivo": "estado.json", "claves": ["roles.ejecutivo"]},
              {"n": 4, "fecha": "2026-10-03", "operacion": "agregar", "archivo": "03-control/registros/riesgos.csv", "registro": "riesgos", "ids": ["R-001"]}]
    (g / ".bitacora.jsonl").write_text("\n".join(json.dumps(x) for x in lineas) + "\n", encoding="utf-8")
    h = fuentes.bitacora(g)
    ver("KB-79 la historia de un artefacto (cambios de estado.json.artefactos.<clave> en la bitácora) entra con la clave como id",
        [(x["id"], x["n"], x["operacion"]) for x in h] == [("business-case", 1, "artefacto"), ("business-case", 2, "aprobar"), ("R-001", 4, "agregar")], h)
    base = {"fuente": "gestion/03-control/registros/decisiones.csv", "rango": "L3", "id": "D-002", "ruta_citada": "00-direccion/caso.md",
            "texto": "artefactos_afectados: 00-direccion/caso.md", "columna": "artefactos_afectados", "cita_sugerida": "archivo/caso.md"}
    a1 = enlaces.accion_cita("/x", "gestion", {**base, "registro": "decisiones", "sugerida": "gestion/archivo/caso.md", "como": "movimiento"})
    a2 = enlaces.accion_cita("/x", "gestion", {**base, "registro": "decisiones", "sugerida": "gestion/archivo/caso.md", "como": "nombre"})
    a3 = enlaces.accion_cita("/x", "gestion", {**base, "registro": "riesgos", "id": "R-001", "sugerida": "gestion/archivo/caso.md", "como": "movimiento"})
    ver("KB-80 pm-kb enlaces nunca sugiere editar una fila de decisiones.csv (registro histórico): informa el movimiento y que el id ya resuelve; en otros registros, registro.py actualizar",
        "registro.py" not in a1 + a2 and "no se edita" in a1 and "enlace por id ya lo resuelve" in a1 and "archivo/caso.md" in a2
        and "registro.py" in a3 and "actualizar riesgos R-001" in a3, (a1, a2, a3))
    pt = proyecto_tablero.crear(Path(tmp) / "pt")
    gest = pt / "gestion"
    antes = _arbol(gest)
    d = TB.generar(gest, "2026-10-30")
    ins, avisos = TB.instantaneas(gest)
    ver("KB-81 el tablero lo genera el núcleo (tablero.py generar --json, PM_SOLO_LECTURA) sin escribir en la carpeta; las 3 instantáneas se leen en orden",
        d["formato"] == "pm-tablero/1" and d["corte"] == "2026-10-30" and _arbol(gest) == antes and not avisos
        and [x["id"] for x in ins] == ["2026-10-05-autorizar-inicio-etapa-0", "2026-10-20-autorizar-proyecto-etapa-1", "2026-10-30-junta-de-octubre"]
        and ins[1]["datos"]["instantanea"]["decision"] == "condicionado", ([x["id"] for x in ins], avisos))
    det = TB.detalle_puertas(gest, d)
    c = TB.comparar(ins[0]["datos"], d)
    ver("KB-82 detalle de las puertas desde estado.json (decisión, D-###, condiciones, verificación) y `comparar` del núcleo sobre dos tableros",
        det.get("puerta:autorizar-proyecto:1", {}).get("condiciones", "").startswith("presentar el plan de pruebas de carga")
        and det["puerta:autorizar-proyecto:1"]["decision_id"] and any(x["ref"] == "C-001" for x in c["entraron"]) and c["b"] == "actual", (det, c.get("b")))
    eq, n = TB.podar(d, {"tolerancias-y-autoridad"}, {"03-control/registros/acciones.csv"})
    ver("KB-83 poda por circulación: sin el artefacto restringido ni las tarjetas de un archivo restringido; totales de atención recalculados",
        n >= 2 and "tolerancias-y-autoridad" in d["artefactos"]["elementos"] and "tolerancias-y-autoridad" not in eq["artefactos"]["elementos"]
        and not any(x["ref"].startswith("A-") for x in eq["atencion"]["items"]) and sum(eq["atencion"]["totales"].values()) == len(eq["atencion"]["items"])
        and TB.podar(d, set(), set()) == (d, 0), n)
    r1 = {"proyecto": "b", "resumen": TB.resumen(d)}
    r2 = {"proyecto": "a", "resumen": {**TB.resumen(d), "excepcion": "X-001"}}
    r3 = {"proyecto": "c", "resumen": None}
    ver("KB-84 cartera: resumen (fase, etapa y días, próxima puerta con bloqueos y condiciones, atención) y orden por lo que pide acción",
        r1["resumen"]["proxima"]["tipo"] == "autorizar-etapa" and r1["resumen"]["proxima"]["bloqueos"] >= 1 and r1["resumen"]["atencion"]["decidir"] >= 1
        and [x["proyecto"] for x in sorted([r3, r1, r2], key=TB.orden_cartera)] == ["a", "b", "c"], r1["resumen"])
    vis = gest / "02-planificacion" / "visuales"
    (Path(tmp) / "fuera.html").write_text("<p>fuera</p>", encoding="utf-8")
    try:
        os.symlink(Path(tmp) / "fuera.html", vis / "enlace.html")
        hay_enlace = True
    except OSError:
        hay_enlace = False
    lista = documentos.listar(str(pt), [{"fuente": f"gestion/02-planificacion/visuales/{x}", "titulo": x} for x in
                                        ("wbs.html", "riesgos.html", "one-pager-brief.html", "one-pager-brief.src.html")])
    m = {Path(x["fuente"]).name: x for x in lista}
    ver("KB-85 documentos: motor reconocido (archify, diagram-design, visual-explainer), scripts solo si hay <script> ejecutable, SVG y PNG del diagrama, sin la fuente .src.html",
        m["wbs.html"]["motor"] == "archify" and m["wbs.html"]["scripts"] and m["riesgos.html"]["motor"] == "diagram-design" and not m["riesgos.html"]["scripts"]
        and m["riesgos.html"]["exportaciones"] == ["gestion/02-planificacion/visuales/riesgos.svg", "gestion/02-planificacion/visuales/riesgos.png"]
        and m["one-pager-brief.html"]["motor"] == "visual-explainer" and "one-pager-brief.src.html" not in m, {k: (v["motor"], v["scripts"]) for k, v in m.items()})
    ver("KB-86 documentos: nunca una ruta fuera de la carpeta indexada (.., absoluta, enlace simbólico hacia afuera); CSP aislada con sandbox y sin red",
        documentos.dentro(str(pt), "gestion/02-planificacion/visuales/wbs.html") and not documentos.dentro(str(pt), "../fuera.html")
        and not documentos.dentro(str(pt), str(Path(tmp) / "fuera.html")) and not documentos.dentro(str(pt), "gestion/../../fuera.html")
        and (not hay_enlace or not documentos.dentro(str(pt), "gestion/02-planificacion/visuales/enlace.html"))
        and documentos.csp(False).startswith("sandbox; ") and "script-src 'none'" in documentos.csp(False)
        and documentos.csp(True).startswith("sandbox allow-scripts;") and "connect-src 'none'" in documentos.csp(True) and "allow-same-origin" not in documentos.csp(True))
    if hay_enlace:
        os.unlink(vis / "enlace.html")


def _arbol(p):
    import hashlib
    out = {}
    for raiz, dirs, archivos in os.walk(p):
        for x in dirs:
            out[os.path.relpath(os.path.join(raiz, x), p)] = "dir"
        for x in archivos:
            q = os.path.join(raiz, x)
            with open(q, "rb") as fh:
                out[os.path.relpath(q, p)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def mover(raiz, de, a):
    destino = Path(raiz) / a
    destino.parent.mkdir(parents=True, exist_ok=True)
    (Path(raiz) / de).rename(destino)


def ubicaciones_nucleo(raiz, tmp):
    """KB-59…KB-66: huella de vigilar, ids estables → ubicación, movimientos de artefactos y documentos, citas rotas y
    la acción sugerida (estado.py artefacto), sin base de datos, sobre una copia del proyecto de prueba."""
    c = Path(tempfile.mkdtemp(prefix="pmkb-prueba-mov-")) / "copia"          # fuera de la carpeta del proyecto de prueba
    shutil.copytree(raiz, c)
    (c / "notas").mkdir()
    (c / "notas" / "externa.md").write_text("# Nota externa\n\nFuera de la carpeta de gestión.\n", encoding="utf-8")
    h0 = fuentes.huella(c)
    (c / "gestion" / "docs" / "borrador-privado.md").write_text("# Notas privadas\n\nOtra cosa.\n", encoding="utf-8")   # .pmkbignore
    (c / "gestion" / "docs" / "imagen.png").write_bytes(b"\x89PNG")
    h1 = fuentes.huella(c)
    (c / "notas" / "externa.md").write_text("# Nota externa\n\nEditada.\n", encoding="utf-8")
    h2 = fuentes.huella(c)
    with open(c / "gestion" / ".bitacora.jsonl", "a", encoding="utf-8") as f:
        f.write("\n")
    h3 = fuentes.huella(c)
    ver("KB-59 vigilar: la huella cambia con un documento indexable fuera de la carpeta de gestión y con la bitácora, no con uno excluido ni con uno no indexable",
        h0 == h1 and h1 != h2 and h2 != h3, (h0, h1, h2, h3))
    p1 = indexador.preparar(c)
    u1, m1 = enlaces.ubicaciones(p1, {})
    ub = {u["ref"]: u for u in u1}
    inf = next((d for d in p1["documentos"] if d["doc_id"].startswith("nom:") and "informe" in d["doc_id"]), {})
    ver("KB-60 ids estables → ubicación: fila (CSV y líneas), artefacto (clave y ruta de estado.json) y documento sin clave (doc_id)",
        ub.get("R-001", {}).get("ruta") == "gestion/03-control/registros/riesgos.csv" and ub["R-001"]["rango"] == "L2"
        and ub.get("business-case", {}).get("ruta") == "gestion/00-direccion/business-case.md" and ub["business-case"]["estado"] == "vigente"
        and ub.get(inf.get("doc_id"), {}).get("ruta") == inf.get("fuente_vigente") and not m1 and len(ub["R-001"]["sha256"]) == 64,
        {k: (v["ruta"], v["estado"]) for k, v in ub.items() if k in ("R-001", "business-case", inf.get("doc_id"))})
    previas = {u["ref"]: u for u in u1}
    mover(c, "gestion/00-direccion/business-case.md", "gestion/archivo/caso-de-negocio.md")          # renombrado: por huella (copia congelada)
    mover(c, "gestion/02-planificacion/plan-comunicaciones.md", "gestion/archivo/plan-comunicaciones.md")   # mismo nombre
    mover(c, "gestion/docs/2027-01-10-tablero.md", "gestion/archivo/2027-01-10-tablero.md")          # documento sin clave
    p2 = indexador.preparar(c, previas=previas)
    u2, m2 = enlaces.ubicaciones(p2, previas)
    ub2 = {u["ref"]: u for u in u2}
    bc = [u for u in p2["unidades"] if u["doc_id"] == "art:business-case" and u["vigente"]]
    mov = {m["ref"]: m for m in m2}
    ver("KB-61 artefacto movido y renombrado sin corregir estado.json: se encuentra por huella, conserva art:business-case v1.1 y el movimiento queda registrado",
        ub2["business-case"]["estado"] == "movida" and ub2["business-case"]["ruta"] == "gestion/archivo/caso-de-negocio.md"
        and ub2["business-case"]["encontrada_por"] == "huella" and bc and bc[0]["fuente"] == "gestion/archivo/caso-de-negocio.md" and bc[0]["version"] == "1.1"
        and mov.get("business-case", {}).get("ruta_anterior") == "gestion/00-direccion/business-case.md", (ub2["business-case"], mov.get("business-case")))
    pc = ub2["plan-comunicaciones"]
    ver("KB-62 artefacto movido con el mismo nombre: se encuentra por huella de la indexación anterior y, sin ella, por nombre",
        pc["estado"] == "movida" and pc["encontrada_por"] == "huella" and pc["ruta"] == "gestion/archivo/plan-comunicaciones.md"
        and {a["ref"]: a for a in indexador.preparar(c)["artefactos"]}["plan-comunicaciones"]["encontrada_por"] == "nombre", pc)
    viejo = "ruta:gestion/docs/2027-01-10-tablero.md"
    ver("KB-63 documento sin clave movido: el id anterior queda como alias de la ruta nueva (por huella) y el movimiento se registra",
        ub2.get(viejo, {}).get("ruta") == "gestion/archivo/2027-01-10-tablero.md" and ub2[viejo]["doc_id"] == "ruta:gestion/archivo/2027-01-10-tablero.md"
        and mov.get(viejo, {}).get("motivo") == "huella" and "ruta:gestion/archivo/2027-01-10-tablero.md" in ub2, (ub2.get(viejo), mov.get(viejo)))
    (c / "gestion" / "archivo" / "2027-01-10-tablero.md").unlink()
    p3 = indexador.preparar(c, previas=ub2)
    u3, m3 = enlaces.ubicaciones(p3, ub2)
    est = json.loads((c / "gestion" / "estado.json").read_text(encoding="utf-8"))
    est["artefactos"]["plan-calidad"] = {"ruta": "02-planificacion/plan-calidad-no-existe.md", "version": "0.1", "estado": "borrador"}
    (c / "gestion" / "estado.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
    a4 = {a["ref"]: a for a in indexador.preparar(c)["artefactos"]}
    ver("KB-64 ruta rota: un documento borrado deja de resolverse y un artefacto sin archivo ni candidato queda no-encontrado, sin movimiento",
        viejo not in {u["ref"] for u in u3} and not m3 and a4["plan-calidad"]["estado"] == "no-encontrada", a4["plan-calidad"])
    (c / "gestion" / "docs" / "acta-enlaces.md").write_text(
        "# Acta\n\nVer `02-planificacion/plan-comunicaciones.md`, `03-control/registros/riesgos.csv` y `.github/workflows/ci.yml`.\n", encoding="utf-8")
    us = [{"id": u["id"], "fuente": u["fuente"], "rango": u["rango"], "registro": u.get("registro") or "", "texto": u["texto"]}
          for u in indexador.preparar(c)["unidades"] if u["vigente"] and not u.get("copia")]
    movs = [m for m in m2 if m["ref"] == "plan-comunicaciones"]
    cs = enlaces.citas_rotas(us, c, "gestion", movs, [])
    ver("KB-65 citas a rutas que no existen: la ruta movida se informa con la nueva (por el movimiento); la existente y la de otro repositorio, no",
        [(x["ruta_citada"], x["sugerida"], x["como"], x["cita_sugerida"]) for x in cs if x["fuente"].endswith("acta-enlaces.md")]
        == [("02-planificacion/plan-comunicaciones.md", "gestion/archivo/plan-comunicaciones.md", "movimiento", "archivo/plan-comunicaciones.md")],
        [(x["fuente"], x["ruta_citada"], x["sugerida"]) for x in cs])
    arte = dict(ub2["business-case"])
    cmd = enlaces.accion_artefacto(str(c), "gestion", arte)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    est = json.loads((c / "gestion" / "estado.json").read_text(encoding="utf-8"))["artefactos"]["business-case"]
    a5 = {a["ref"]: a for a in indexador.preparar(c)["artefactos"]}["business-case"]
    ver("KB-66 la acción sugerida para un artefacto movido (estado.py artefacto … --estado … --version …) funciona: ruta corregida, sigue aprobado v1.1",
        r.returncode == 0 and "estado.py" in cmd and est["ruta"] == "archivo/caso-de-negocio.md" and est["estado"] == "aprobado" and est["version"] == "1.1"
        and est.get("aprobado_por") and a5["estado"] == "vigente", (cmd, r.returncode, (r.stdout + r.stderr)[-300:], est))
    shutil.rmtree(c.parent, ignore_errors=True)


def puerto_reusable():
    """Servicio que cierra primero una conexión (deja TIME_WAIT en su puerto) y se detiene: se puede volver a escuchar."""
    import socket
    from pmkb import config
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); srv.bind(("127.0.0.1", 0)); srv.listen(1)
    puerto = srv.getsockname()[1]
    ocupado_escuchando = config.puerto_ocupado("127.0.0.1", puerto)
    cli = socket.create_connection(("127.0.0.1", puerto)); con, _ = srv.accept()
    con.close(); time.sleep(0.2); cli.close(); srv.close(); time.sleep(0.2)
    sin_reuso = socket.socket()
    try:
        sin_reuso.bind(("127.0.0.1", puerto)); time_wait = False
    except OSError:
        time_wait = True
    finally:
        sin_reuso.close()
    libre = config.puerto_ocupado("127.0.0.1", puerto)
    return (bool(ocupado_escuchando) and libre is None,
            f"escuchando: {ocupado_escuchando!r} · TIME_WAIT reproducido: {time_wait} · después de detener: {libre!r}")


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
    # modelos opcionales que no responden: la indexación y la búsqueda siguen, léxicas y con aviso (§9; antes, traza)
    import socket
    with socket.socket() as so:
        so.bind(("127.0.0.1", 0)); cerrado = f"http://127.0.0.1:{so.getsockname()[1]}"
    previas = {k: os.environ.get(k) for k in ("PMKB_EMBED_URL", "PMKB_EMBED_MODELO", "PMKB_EMBED_TIPO", "PMKB_RERANK_URL")}
    try:
        for k in previas:
            os.environ.pop(k, None)
        base_ids = [x["id"] for x in s.buscar("demoras de integración con el padron", proyecto=p)["resultados"]]
        os.environ.update(PMKB_EMBED_URL=cerrado, PMKB_EMBED_MODELO="zz-modelo-caido")
        avisos = []
        rv = indexador.cargar(a, p + "-v", indexador.preparar(raiz), avisar=avisos.append)
        ver("KB-54 indexar con el servidor de vectores caído: índice léxico y aviso, sin traza",
            rv["modelo"] == "" and rv["unidades"] > 0 and any("no respondió" in x for x in avisos), (rv["modelo"], avisos))
        indexador.quitar(a, p + "-v")
        with a.transaction():   # un vector de ese modelo, para que la búsqueda intente usarlo
            a.execute("""INSERT INTO pmkb.vector (proyecto, unidad_id, modelo, emb) SELECT proyecto, id, 'zz-modelo-caido', '[1,0,0]'::vector
                         FROM pmkb.unidad WHERE proyecto = %s AND vigente LIMIT 1""", (p,))
        r = s.buscar("demoras de integración con el padron", proyecto=p)
        ver("KB-55 buscar con el servidor de vectores caído: léxica, mismos resultados y aviso",
            r["modo"] == "léxica (BM25)" and [x["id"] for x in r["resultados"]] == base_ids and any("vectores no respondió" in x for x in r["avisos"]), (r["modo"], r["avisos"]))
        os.environ.pop("PMKB_EMBED_URL"); os.environ.pop("PMKB_EMBED_MODELO"); os.environ["PMKB_RERANK_URL"] = cerrado
        r = s.buscar("demoras de integración con el padron", proyecto=p)
        ver("KB-56 buscar con el re-ranqueo caído: orden sin re-ranqueo y aviso",
            "re-ranqueo" not in r["modo"] and [x["id"] for x in r["resultados"]] == base_ids and any("re-ranqueo no respondió" in x for x in r["avisos"]), (r["modo"], r["avisos"]))
    finally:
        for k, v in previas.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
        with a.transaction():
            a.execute("DELETE FROM pmkb.vector WHERE modelo = 'zz-modelo-caido'")
    import psycopg
    sd, original, intentos = Sesion(a, "*", True), Sesion._tx_una, []

    def con_interbloqueo(self, fn, arriba):
        intentos.append(arriba)
        if len(intentos) == 1:
            raise psycopg.errors.DeadlockDetected("interbloqueo simulado")
        return original(self, fn, arriba)
    sd._tx_una = con_interbloqueo.__get__(sd)
    r = sd.buscar("demoras de integración con el padron", proyecto=p)
    ver("KB-57 consulta abortada por un interbloqueo (p. ej. `pm-kb verificar` mientras se sirve): se reintenta y responde",
        r["resultados"] and r["resultados"][0]["id"] == "R-001" and intentos[:2] == [True, True], intentos)
    migracion(a)
    migracion_4(a)
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cli.cmd_base(argparse.Namespace(accion="estado"))
    ver("KB-68 pm-kb base estado informa el esquema 4", f"esquema pm-kb {indexador.ESQUEMA} ·" in buf.getvalue() and indexador.ESQUEMA == 4, buf.getvalue())
    pm = p + "-mov"
    copia = Path(tempfile.mkdtemp(prefix="pmkb-prueba-mov-")) / "copia"
    shutil.copytree(raiz, copia)
    indexador.quitar(a, pm)
    indexador.indexar(a, pm, copia, con_vectores=False, avisar=lambda *x: None)
    mover(copia, "gestion/00-direccion/business-case.md", "gestion/archivo/caso-de-negocio.md")
    mover(copia, "gestion/docs/2027-02-10-tablero.md", "gestion/archivo/2027-02-10-tablero.md")
    est = json.loads((copia / "gestion" / "estado.json").read_text(encoding="utf-8"))
    est["artefactos"]["plan-calidad"] = {"ruta": "02-planificacion/plan-calidad.md", "version": "0.1", "estado": "borrador"}
    (copia / "gestion" / "estado.json").write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")
    (copia / "gestion" / "docs" / "acta-enlaces.md").write_text("# Acta\n\nEl tablero de febrero está en `docs/2027-02-10-tablero.md`.\n", encoding="utf-8")
    _, rr = indexador.indexar(a, pm, copia, con_vectores=False, avisar=lambda *x: None)
    s = Sesion(a, "*", True)
    fb = s.ficha("business-case", proyecto=pm)
    viejo = "ruta:gestion/docs/2027-02-10-tablero.md"
    fd = s.ficha(viejo, proyecto=pm)
    with a.transaction():
        nm = a.execute("SELECT ref, ruta_anterior, ruta_nueva, motivo FROM pmkb.movimiento WHERE proyecto = %s ORDER BY ref", (pm,)).fetchall()
    ver("KB-69 mover un artefacto y un documento: el enlace por id (business-case, doc_id anterior) sigue funcionando y el movimiento queda registrado",
        fb.get("ubicacion", {}).get("ruta") == "gestion/archivo/caso-de-negocio.md" and "caso-de-negocio.md" in fb.get("cita", "")
        and fb["movimiento"]["texto"].startswith("se movió de gestion/00-direccion/business-case.md a gestion/archivo/caso-de-negocio.md el ")
        and fd.get("ubicacion", {}).get("ruta") == "gestion/archivo/2027-02-10-tablero.md" and "Avance 55" in fd.get("texto", "")
        and ("business-case", "gestion/00-direccion/business-case.md", "gestion/archivo/caso-de-negocio.md", "huella") in nm
        and (viejo, "gestion/docs/2027-02-10-tablero.md", "gestion/archivo/2027-02-10-tablero.md", "huella") in nm
        and len(rr["movimientos"]) == 2 and s.versiones(viejo, proyecto=pm).get("doc_id") == "ruta:gestion/archivo/2027-02-10-tablero.md",
        (fb.get("ubicacion"), fd.get("ubicacion"), nm))
    e = s.enlaces(pm)
    arts = {x["ref"]: x for x in e["artefactos"]}
    cit = [x for x in e["citas"] if x["fuente"].endswith("acta-enlaces.md")]
    fp = s.ficha("plan-calidad", proyecto=pm)
    ver("KB-70 pm-kb enlaces: artefacto movido con ruta sugerida y comando de estado.py; ruta rota (sin candidato) informada; cita a la ruta vieja con la nueva",
        arts.get("business-case", {}).get("sugerida") == "gestion/archivo/caso-de-negocio.md"
        and "estado.py --proyecto" in arts["business-case"]["accion"] and "artefacto business-case --ruta archivo/caso-de-negocio.md --estado aprobado --version 1.1" in arts["business-case"]["accion"]
        and arts.get("plan-calidad", {}).get("estado") == "no-encontrada" and not arts["plan-calidad"]["sugerida"]
        and cit and cit[0]["sugerida"] == "gestion/archivo/2027-02-10-tablero.md" and cit[0]["resuelta"]
        and e["totales"]["movimientos"] == 2 and set(e) >= {"proyecto", "artefactos", "citas", "movimientos", "totales", "avisos"}
        and "error" not in fp and any("fuente no encontrada" in x for x in fp.get("avisos", [])), (e["artefactos"], cit, fp.get("avisos")))
    _, rr2 = indexador.indexar(a, pm, copia, con_vectores=False, avisar=lambda *x: None)
    with a.transaction():
        n2 = a.execute("SELECT count(*) FROM pmkb.movimiento WHERE proyecto = %s", (pm,)).fetchone()[0]
        desde = a.execute("SELECT desde < now() - interval '0 seconds' FROM pmkb.ubicacion WHERE proyecto = %s AND ref = 'R-001'", (pm,)).fetchone()
    ver("KB-71 reindexar sin cambios no repite movimientos ni pierde las ubicaciones", not rr2["movimientos"] and n2 == 2 and desde and desde[0], (rr2["movimientos"], n2))
    # rol de lectura y RLS
    l = config.conectar(lector=True)
    cuenta = lambda proy, restr, q: Sesion(l, proy, restr)._tx(lambda cur: cur.execute(q, (pm,)).fetchone()[0])
    ver("KB-72 RLS de ubicacion y movimiento: un token sin el proyecto no ve sus filas; con el proyecto, sí; lo restringido solo con circulación restringida",
        cuenta("otro-proyecto", True, "SELECT count(*) FROM pmkb.ubicacion WHERE proyecto = %s") == 0
        and cuenta("otro-proyecto", True, "SELECT count(*) FROM pmkb.movimiento WHERE proyecto = %s") == 0
        and cuenta(pm, False, "SELECT count(*) FROM pmkb.ubicacion WHERE proyecto = %s") > 0
        and cuenta(pm, False, "SELECT count(*) FROM pmkb.movimiento WHERE proyecto = %s") == 2
        and cuenta(pm, False, "SELECT count(*) FROM pmkb.ubicacion WHERE proyecto = %s AND ruta LIKE '%%salarios%%'") == 0
        and cuenta(pm, True, "SELECT count(*) FROM pmkb.ubicacion WHERE proyecto = %s AND ruta LIKE '%%salarios%%'") == 1)
    sm = lambda: Sesion(l, pm, False)
    fm = mcp.manejar({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "ficha", "arguments": {"id": "business-case", "historia": True}}}, sm)
    tx = fm["result"]["content"][0]["text"]
    ver("KB-73 MCP ficha ampliada: ubicación, aviso «se movió de A a B el …», versiones y relacionados por id",
        not fm["result"]["isError"] and "ubicación (artefacto de estado.json business-case): gestion/archivo/caso-de-negocio.md" in tx
        and "aviso: se movió de gestion/00-direccion/business-case.md a gestion/archivo/caso-de-negocio.md el " in tx and "versiones: vigente v1.1" in tx
        and "Relacionados por id:" in tx, tx[:600])
    ver("KB-74 vigilar: reindexa al cambiar un documento fuera de la carpeta de gestión", *vigilar(copia, pm))
    ver("KB-91 vigilar: publica el tablero en cada reindexación", sum(1 for x in VIGILAR if x.startswith(f"pm-kb: tablero de {pm} publicado")) == 2, VIGILAR[-6:])
    portal = portal_con_base(a, l, p)
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
    with a.transaction():
        dias = a.execute("SELECT round(extract(epoch FROM vence - creado) / 86400) FROM pmkb.acceso WHERE token_sha = %s",
                         (hashlib.sha256(t.encode()).hexdigest(),)).fetchone()[0]
    malos = []
    for d in (0, 366):
        try:
            cli.crear_token(a, "Prueba KB", p, False, dias=d); malos.append(d)
        except ValueError:
            pass
    ver("KB-48 token con vencimiento: 90 días por defecto, fuera de 1–365 se rechaza", dias == 90 and not malos, (dias, malos))
    tv = cli.crear_token(a, "Prueba KB", p, False, dias=1)
    with a.transaction():
        a.execute("UPDATE pmkb.acceso SET vence = now() - interval '1 minute' WHERE token_sha = %s", (hashlib.sha256(tv.encode()).hexdigest(),))
    with l.transaction():
        idv = l.execute("SELECT persona FROM pmkb.identidad(%s)", (hashlib.sha256(tv.encode()).hexdigest(),)).fetchone()
    ver("KB-49 token vencido → sin identidad", idv is None, idv)
    # MCP (JSON-RPC)
    ses = lambda: Sesion(l, p, False)
    ini = mcp.manejar({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}, ses)
    ver("KB-35 MCP initialize", ini["result"]["protocolVersion"] == "2025-06-18" and "tools" in ini["result"]["capabilities"])
    lst = mcp.manejar({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, ses)
    ver("KB-36 MCP herramientas de solo lectura (9, con `tablero`)", len(lst["result"]["tools"]) == 9 and all(h["annotations"]["readOnlyHint"] for h in lst["result"]["tools"]))
    cal = mcp.manejar({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "buscar", "arguments": {"consulta": "padrón"}}}, ses)
    ver("KB-37 MCP buscar con cita", "cita:" in cal["result"]["content"][0]["text"] and not cal["result"]["isError"])
    ver("KB-38 MCP notificación sin respuesta", mcp.manejar({"jsonrpc": "2.0", "method": "notifications/initialized"}, ses) is None)
    ver("KB-39 MCP método desconocido", mcp.manejar({"jsonrpc": "2.0", "id": 4, "method": "server/discover"}, ses)["error"]["code"] == -32601)
    # servicio web
    try:
        import uvicorn
        from pmkb import web
        puerto = next((x for x in range(8800, 8900) if config.puerto_ocupado("127.0.0.1", x) is None), None)
        if puerto is None:
            raise RuntimeError("no hay un puerto libre entre 8800 y 8899 para el servicio web de la prueba")
        srv = uvicorn.Server(uvicorn.Config(web.crear_app(), host="127.0.0.1", port=puerto, log_level="error"))
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
            req = urllib.request.Request(f"http://127.0.0.1:{puerto}" + ruta, data=json.dumps(datos).encode() if datos is not None else None, headers=h)
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
        ver("KB-50 web: token vencido → 401", pedir("/api/estado", tv)[0] == 401)
        tm = cli.crear_token(a, "Prueba KB", pm, False)
        st, cuerpo, _ = pedir("/api/ficha?id=business-case&proyecto=" + pm, tm)
        fw = json.loads(cuerpo) if st == 200 else {}
        ver("KB-75 web: /api/ficha devuelve la ficha ampliada (ubicación, movimiento, versiones, relacionados por id e historia)",
            st == 200 and fw.get("ref") == "business-case" and fw.get("ubicacion", {}).get("tipo") == "artefacto"
            and "se movió de" in (fw.get("movimiento") or {}).get("texto", "") and fw.get("versiones", {}).get("aprobada") == "1.1"
            and "decisiones" in fw.get("relacionados", {}) and isinstance(fw.get("historia"), list), {k: fw.get(k) for k in ("ref", "ubicacion", "movimiento")})
        st, cuerpo, _ = pedir("/api/ficha?id=R-001&proyecto=" + pm, tm)
        fw = json.loads(cuerpo) if st == 200 else {}
        ver("KB-76 web: la ficha de una fila trae su ubicación (CSV y líneas) y la historia de la bitácora",
            st == 200 and fw.get("ubicacion", {}).get("rango") == "L2" and fw.get("historia") and fw.get("versiones") is None, fw.get("ubicacion"))

        class SinRedirigir(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None

        def formulario(token):
            req = urllib.request.Request(f"http://127.0.0.1:{puerto}/ingresar", data=urllib.parse.urlencode({"token": token}).encode(),
                                         headers={"Content-Type": "application/x-www-form-urlencoded"})
            try:
                with urllib.request.build_opener(SinRedirigir).open(req, timeout=10) as resp:
                    return resp.status, dict(resp.headers)
            except urllib.error.HTTPError as x:
                return x.code, dict(x.headers)
        st, cab = formulario(t); st2, cab2 = formulario("pmkb_falso")
        ver("KB-52 web: ingreso por el formulario (POST) con token válido → cookie; con uno falso → error",
            st == 303 and cab.get("location") == "/" and "pmkb=" in cab.get("set-cookie", "") and "HttpOnly" in cab.get("set-cookie", "")
            and st2 == 303 and cab2.get("location") == "/?error=token" and "set-cookie" not in {k.lower() for k in cab2}, (st, st2))
        portal_web(pedir, portal, puerto)
        compartir_web(a, l, portal, puerto)
        srv.should_exit = True; th.join(timeout=5)
    except ImportError as x:
        ver("KB-40…46, KB-50 y KB-52 servicio web", False, f"falta {x.name}: pip install -r pm-kb/requirements.txt")
    with a.transaction():
        a.execute("DELETE FROM pmkb.acceso WHERE persona = 'Prueba KB'")
    indexador.quitar(a, p)
    indexador.quitar(a, pm)
    indexador.quitar(a, portal["proyecto"])
    with a.transaction():
        a.execute("DELETE FROM pmkb.acceso WHERE persona LIKE 'Prueba portal%%'")
        quedan_t = a.execute("""SELECT (SELECT count(*) FROM pmkb.tablero WHERE proyecto = %s) + (SELECT count(*) FROM pmkb.instantanea WHERE proyecto = %s)
                                       + (SELECT count(*) FROM pmkb.enlace WHERE proyecto = %s)""",
                             (portal["proyecto"], portal["proyecto"], portal["proyecto"])).fetchone()[0]
    ver("KB-99 quitar borra también el tablero, las instantáneas y los enlaces compartidos del proyecto", quedan_t == 0, quedan_t)
    shutil.rmtree(portal["carpeta"].parent, ignore_errors=True)
    with a.transaction():
        quedan = a.execute("SELECT (SELECT count(*) FROM pmkb.ubicacion WHERE proyecto = %s) + (SELECT count(*) FROM pmkb.movimiento WHERE proyecto = %s)",
                           (pm, pm)).fetchone()[0]
    ver("KB-77 quitar borra también las ubicaciones y los movimientos del proyecto", quedan == 0, quedan)
    shutil.rmtree(copia.parent, ignore_errors=True)


def vigilar(carpeta, proyecto):
    """`pm-kb vigilar --cada 1 --ciclos N` en un proceso aparte: primera indexación, un documento nuevo fuera de la
    carpeta de gestión → segunda indexación."""
    env = {**os.environ, "PYTHONPATH": str(RAIZ) + os.pathsep + os.environ.get("PYTHONPATH", "")}
    pr = subprocess.Popen([sys.executable, "-m", "pmkb", "vigilar", "--proyecto", proyecto, "--ruta", str(carpeta), "--cada", "1",
                           "--ciclos", "12", "--sin-vectores"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, cwd=str(RAIZ))
    lineas, listo = [], threading.Event()

    def leer():
        for l in pr.stdout:
            lineas.append(l.rstrip())
            if "cambio detectado" in l:
                listo.set()
    th = threading.Thread(target=leer, daemon=True); th.start()
    listo.wait(60)
    (Path(carpeta) / "notas").mkdir(exist_ok=True)
    (Path(carpeta) / "notas" / "vigilada.md").write_text("# Nota vigilada\n\nUn documento fuera de la carpeta de gestión.\n", encoding="utf-8")
    try:
        pr.wait(90)
    except subprocess.TimeoutExpired:
        pr.kill(); pr.wait()
    th.join(5)
    VIGILAR.extend(lineas)
    cambios = [l for l in lineas if "cambio detectado" in l]
    return len(cambios) == 2 and pr.returncode == 0, lineas[-6:]


def migracion(a):
    """KB-67: base creada con el esquema 2 (copia congelada pruebas/esquema-2.sql) en un esquema temporal con otro
    nombre, con índice y tokens; aplicarle pmkb/esquema.sql la lleva al 3 sin perder nada. No toca el esquema pmkb."""
    import re
    tmp = "zz_pmkb_migracion"
    nombre = lambda sql: re.sub(r"\bpmkb\b(?!_)", tmp, sql)
    v2 = (Path(__file__).resolve().parent / "esquema-2.sql").read_text(encoding="utf-8")
    v3 = (RAIZ / "pmkb" / "esquema.sql").read_text(encoding="utf-8")
    try:
        with a.transaction():
            a.execute(f"DROP SCHEMA IF EXISTS {tmp} CASCADE")
            a.execute(nombre(v2))
            antes = a.execute(f"SELECT valor, to_regclass('{tmp}.ubicacion') IS NULL FROM {tmp}.meta WHERE clave = 'esquema'").fetchone()
            a.execute(f"INSERT INTO {tmp}.indice (proyecto, raiz, unidades, vigentes) VALUES ('zz-mig', '/carpeta', 1, 1)")
            a.execute(f"""INSERT INTO {tmp}.unidad (proyecto, id, doc_id, version, tipo, titulo, texto, fuente, rango, vigente, aprobada)
                          VALUES ('zz-mig', 'R-001', 'ruta:r.csv', '', 'fila', 'R-001 · Demora', 'Demora del padrón', 'r.csv', 'L2', true, true)""")
            a.execute(f"INSERT INTO {tmp}.acceso (token_sha, persona, proyectos, vence) VALUES ('sha-prueba', 'Prueba migración', 'zz-mig', now() + interval '1 day')")
        with a.transaction():
            a.execute(nombre(v3))
            a.execute(nombre(v3))         # idempotente
        with a.transaction():
            r = a.execute(f"""SELECT (SELECT valor FROM {tmp}.meta WHERE clave = 'esquema'),
                                     (SELECT count(*) FROM {tmp}.indice), (SELECT count(*) FROM {tmp}.unidad WHERE tsv @@ to_tsquery('{tmp}.es', 'padron')),
                                     (SELECT count(*) FROM {tmp}.acceso WHERE persona = 'Prueba migración'),
                                     (SELECT bool_and(c.relrowsecurity) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                                       WHERE n.nspname = '{tmp}' AND c.relname IN ('ubicacion', 'movimiento')),
                                     (SELECT count(*) FROM pg_policies WHERE schemaname = '{tmp}' AND tablename IN ('ubicacion', 'movimiento')),
                                     has_table_privilege('pmkb_lector', '{tmp}.ubicacion', 'SELECT') AND has_table_privilege('pmkb_lector', '{tmp}.movimiento', 'SELECT'),
                                     (SELECT count(*) FROM information_schema.columns WHERE table_schema = '{tmp}' AND table_name = 'indice' AND column_name = 'gestion')""").fetchone()
        ver("KB-67 migración desde el esquema 2: pasa al actual (ubicacion y movimiento con RLS, política y lectura del rol lector) sin perder índice ni tokens",
            antes == ("2", True) and r == (str(indexador.ESQUEMA), 1, 1, 1, True, 2, True, 1), (antes, r))
    finally:
        with a.transaction():
            a.execute(f"DROP SCHEMA IF EXISTS {tmp} CASCADE")


def migracion_4(a):
    """KB-78: base con el esquema 3 (copia congelada pruebas/esquema-3.sql) en un esquema temporal, con índice y tokens;
    aplicarle pmkb/esquema.sql la lleva al 4 (tablero, instantanea, circulación de documento y version) sin perder nada."""
    import re
    tmp = "zz_pmkb_migracion4"
    nombre = lambda sql: re.sub(r"\bpmkb\b(?!_)", tmp, sql)
    v3 = (Path(__file__).resolve().parent / "esquema-3.sql").read_text(encoding="utf-8")
    v4 = (RAIZ / "pmkb" / "esquema.sql").read_text(encoding="utf-8")
    try:
        with a.transaction():
            a.execute(f"DROP SCHEMA IF EXISTS {tmp} CASCADE")
            a.execute(nombre(v3))
            antes = a.execute(f"SELECT valor, to_regclass('{tmp}.tablero') IS NULL FROM {tmp}.meta WHERE clave = 'esquema'").fetchone()
            a.execute(f"INSERT INTO {tmp}.indice (proyecto, raiz, unidades, vigentes, gestion) VALUES ('zz-mig', '/carpeta', 1, 1, 'gestion')")
            a.execute(f"""INSERT INTO {tmp}.documento (proyecto, doc_id, titulo, fuente_vigente, versiones) VALUES ('zz-mig', 'ruta:r.md', 'R', 'r.md', 1)""")
            a.execute(f"""INSERT INTO {tmp}.version (proyecto, doc_id, version, orden, fuente) VALUES ('zz-mig', 'ruta:r.md', '', 0, 'r.md')""")
            a.execute(f"INSERT INTO {tmp}.ubicacion (proyecto, ref, tipo, ruta) VALUES ('zz-mig', 'R-001', 'fila', 'r.csv')")
            a.execute(f"INSERT INTO {tmp}.acceso (token_sha, persona, proyectos, vence) VALUES ('sha-prueba', 'Prueba migración', 'zz-mig', now() + interval '1 day')")
        with a.transaction():
            a.execute(nombre(v4))
            a.execute(nombre(v4))         # idempotente
        with a.transaction():
            r = a.execute(f"""SELECT (SELECT valor FROM {tmp}.meta WHERE clave = 'esquema'),
                                     (SELECT count(*) FROM {tmp}.indice), (SELECT count(*) FROM {tmp}.ubicacion),
                                     (SELECT count(*) FROM {tmp}.acceso WHERE persona = 'Prueba migración'),
                                     (SELECT string_agg(circulacion, ',') FROM {tmp}.documento) || '|' || (SELECT string_agg(circulacion, ',') FROM {tmp}.version),
                                     (SELECT bool_and(c.relrowsecurity) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                                       WHERE n.nspname = '{tmp}' AND c.relname IN ('tablero', 'instantanea')),
                                     (SELECT count(*) FROM pg_policies WHERE schemaname = '{tmp}' AND tablename IN ('tablero', 'instantanea')),
                                     (SELECT count(*) FROM pg_policies WHERE schemaname = '{tmp}' AND tablename IN ('documento', 'version') AND qual LIKE '%circulacion%'),
                                     has_table_privilege('pmkb_lector', '{tmp}.tablero', 'SELECT') AND has_table_privilege('pmkb_lector', '{tmp}.instantanea', 'SELECT')
                                       AND NOT has_table_privilege('pmkb_lector', '{tmp}.tablero', 'INSERT'),
                                     (SELECT count(*) FROM information_schema.columns WHERE table_schema = '{tmp}' AND table_name = 'indice' AND column_name = 'nombre'),
                                     (SELECT bool_and(c.relrowsecurity) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                                       WHERE n.nspname = '{tmp}' AND c.relname IN ('enlace', 'sesion'))
                                       AND NOT has_table_privilege('pmkb_lector', '{tmp}.enlace', 'SELECT') AND NOT has_table_privilege('pmkb_lector', '{tmp}.sesion', 'SELECT')
                                       AND has_function_privilege('pmkb_lector', '{tmp}.canjear(text, text, int)', 'EXECUTE')""").fetchone()
        ver("KB-78 migración 3 → 4: tablero e instantanea con RLS y lectura (sin escritura) del rol lector, circulación en documento y version con su política, enlaces y sesiones con RLS y sin lectura del lector (solo sus funciones), sin perder índice, ubicaciones ni tokens",
            antes == ("3", True) and r == ("4", 1, 1, 1, "equipo|equipo", True, 2, 2, True, 1, True), (antes, r))
    finally:
        with a.transaction():
            a.execute(f"DROP SCHEMA IF EXISTS {tmp} CASCADE")


def portal_con_base(a, l, p_fixture):
    """KB-87…KB-98 con base: publicar el tablero (indexar y pm-kb tablero), versiones, RLS del tablero y de documento y
    version por circulación, fichas de puertas, productos y artefactos (con su historia), cartera, historial, comparar y
    el MCP `tablero`. Devuelve lo que usa la prueba web."""
    import contextlib, io
    from pmkb import cli, mcp
    from pmkb.busqueda import Sesion
    pp = "zz-pruebas-portal"
    carpeta = proyecto_tablero.crear(Path(tempfile.mkdtemp(prefix="pmkb-prueba-portal-")) / "proyecto")
    indexador.quitar(a, pp)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cli.cmd_indexar(argparse.Namespace(proyecto=pp, ruta=str(carpeta), excluir=[], restringir=[], sin_vectores=True, simular=False))
    out = buf.getvalue()
    with a.transaction():
        filas = a.execute("SELECT circulacion, version, origen, formato FROM pmkb.tablero WHERE proyecto = %s ORDER BY circulacion", (pp,)).fetchall()
        n_ins = a.execute("SELECT count(DISTINCT id) FROM pmkb.instantanea WHERE proyecto = %s", (pp,)).fetchone()[0]
        nombre = a.execute("SELECT nombre FROM pmkb.indice WHERE proyecto = %s", (pp,)).fetchone()[0]
    ver("KB-87 indexar publica el tablero del núcleo (fila de equipo sin lo restringido y fila restringida completa) y las 3 instantáneas",
        f"pm-kb: tablero de {pp} publicado · versión 1" in out and filas == [("equipo", 1, "indexar", "pm-tablero/1"), ("restringida", 1, "indexar", "pm-tablero/1")]
        and n_ins == 3 and nombre == proyecto_tablero.NOMBRE, (out[-400:], filas, n_ins))
    antes = _arbol(carpeta)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cli.cmd_tablero(argparse.Namespace(proyecto=pp, corte=None, json=False))
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        cli.cmd_tablero(argparse.Namespace(proyecto=pp, corte="2026-10-10", json=True))
    dj = json.loads(buf2.getvalue())
    with a.transaction():
        v2 = a.execute("SELECT version, origen, corte FROM pmkb.tablero WHERE proyecto = %s AND circulacion = 'equipo'", (pp,)).fetchone()
    ver("KB-88 pm-kb tablero: sin cambios la versión no sube; con otro corte sube; --json imprime el pm-tablero/1 publicado; la carpeta no cambia",
        "versión 1 (sin cambios)" in buf.getvalue() and v2 == (2, "tablero", "2026-10-10") and dj["corte"] == "2026-10-10" and dj["formato"] == "pm-tablero/1"
        and _arbol(carpeta) == antes, (buf.getvalue()[-200:], v2))
    with contextlib.redirect_stdout(io.StringIO()):
        cli.cmd_tablero(argparse.Namespace(proyecto=pp, corte=None, json=False))
    se, sr, so = Sesion(l, pp, False), Sesion(l, pp, True), Sesion(l, "otro-proyecto", True)
    te, tr = se.tablero(pp), sr.tablero(pp)
    ver("KB-89 RLS del tablero: el token sin circulación restringida ve la fila de equipo (sin el artefacto restringido); con ella, la completa; otro proyecto, nada",
        te["circulacion"] == "equipo" and "tolerancias-y-autoridad" not in te["datos"]["artefactos"]["elementos"]
        and tr["circulacion"] == "restringida" and "tolerancias-y-autoridad" in tr["datos"]["artefactos"]["elementos"]
        and "error" in so.tablero(pp) and not so.historial(pp).get("instantaneas") and not [x for x in so.cartera()["proyectos"] if x["proyecto"] == pp],
        (te.get("circulacion"), tr.get("circulacion")))
    cuenta = lambda proy, restr, q, arg: Sesion(l, proy, restr)._tx(lambda cur: cur.execute(q, (arg,)).fetchone()[0])
    qd = "SELECT count(*) FROM pmkb.documento WHERE proyecto = %s AND fuente_vigente LIKE '%%salarios%%'"
    qv = "SELECT count(*) FROM pmkb.version WHERE proyecto = %s AND fuente LIKE '%%salarios%%'"
    ver("KB-90 RLS de documento y version por circulación (no solo por proyecto): sin --restringida no se ve el documento restringido ni sus versiones",
        cuenta(p_fixture, False, qd, p_fixture) == 0 and cuenta(p_fixture, False, qv, p_fixture) == 0
        and cuenta(p_fixture, True, qd, p_fixture) == 1 and cuenta(p_fixture, True, qv, p_fixture) >= 1
        and "error" in Sesion(l, p_fixture, False).versiones("gestion/docs/salarios.md", proyecto=p_fixture)
        and cuenta(pp, False, "SELECT count(*) FROM pmkb.documento WHERE proyecto = %s AND clave_pm = 'tolerancias-y-autoridad'", pp) == 0)
    fp = se.ficha("puerta:autorizar-proyecto:1", proyecto=proyecto_tablero.NOMBRE, historia=True)
    ver("KB-92 ficha de una puerta (por el nombre de estado.json): decisión, D-###, fecha, condiciones y verificación; ubicación en estado.json; historia de su decisión",
        fp.get("proyecto") == pp and fp.get("ubicacion", {}).get("tipo") == "puerta" and "condiciones: presentar el plan de pruebas de carga" in fp.get("texto", "")
        and "condicionado" in fp["texto"] and fp["relacionados"].get("decisiones") and fp["historia"] and fp["tablero"]["vista"] == "ciclo",
        {k: fp.get(k) for k in ("proyecto", "texto", "ubicacion")})
    fx = se.ficha("1.2", proyecto=pp)
    fprox = se.ficha("puerta:autorizar-etapa:1", proyecto=pp)
    ver("KB-93 ficha de un producto (estado, paquetes, revisión de calidad) y de la próxima puerta (hallazgos)",
        fx.get("tipo") == "producto" and "estado: no-iniciado" in fx.get("texto", "") and "revisión de calidad" in fx["texto"] and fx["ubicacion"]["ruta"].endswith("02-planificacion/wbs.csv")
        and (fprox.get("tablero") or {}).get("estado") == "proxima" and "bloqueo" in fprox.get("texto", ""), (fx.get("texto"), fprox.get("texto")))
    fa = se.ficha("pbs-wbs", proyecto=pp, historia=True)
    fc = se.ficha("C-001", proyecto=pp)
    ver("KB-94 ficha de un artefacto con su historia de estado.json (bitácora) y bloque del tablero; una fila de registro también trae su tarjeta",
        [h["operacion"] for h in fa.get("historia", [])] == ["artefacto"] and (fa.get("tablero") or {}).get("vista") in ("artefactos", None)
        and (fc.get("tablero") or {}).get("vista") in ("cambios", "atencion") and "error" in se.ficha("puerta:no-existe:9", proyecto=pp), (fa.get("historia"), fc.get("tablero")))
    h, cmp_, car, art = se.historial(pp), se.comparar_tableros(pp, "2026-10-05-autorizar-inicio-etapa-0", "actual"), se.cartera(), se.artefactos(pp)
    fila = next(x for x in car["proyectos"] if x["proyecto"] == pp)
    ver("KB-95 historial (línea de tiempo con la ruta del HTML), comparar con el núcleo, cartera (resumen) y artefactos (ciclos anteriores, borrador)",
        [x["id"] for x in h["instantaneas"]][0] == "2026-10-05-autorizar-inicio-etapa-0" and h["instantaneas"][0]["html_ruta"].startswith("gestion/03-control/reportes/tableros/")
        and h["nombre"] == proyecto_tablero.NOMBRE and any(x["ref"] == "C-001" for x in cmp_["entraron"])
        and fila["resumen"]["proxima"]["tipo"] == "autorizar-etapa" and art["elementos"]["project-brief"]["ciclos"] and art["elementos"]["project-brief"]["borrador"],
        (h.get("instantaneas", [])[:1], fila.get("resumen")))
    sm = lambda: Sesion(l, pp, False)
    m1 = mcp.manejar({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "tablero", "arguments": {"proyecto": pp}}}, sm)
    m2 = mcp.manejar({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "tablero", "arguments": {"historial": True}}}, sm)
    m3 = mcp.manejar({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "tablero", "arguments": {"proyecto": pp, "instantanea": "2026-10-05-autorizar-inicio-etapa-0", "comparar": "actual"}}}, sm)
    t1, t2, t3 = (m["result"]["content"][0]["text"] for m in (m1, m2, m3))
    ver("KB-96 MCP `tablero` (solo lectura): actual con la ref de cada tarjeta, historial (sin proyecto si el token ve uno) y comparar",
        "Próxima puerta [puerta:autorizar-etapa:1]" in t1 and "[C-001]" in t1 and "tolerancias-y-autoridad" not in t1 and "2026-10-20-autorizar-proyecto-etapa-1" in t2
        and "entraron" in t3 and not any(m["result"]["isError"] for m in (m1, m2, m3)), (t1[:300], t2[:200], t3[:200]))
    from pmkb import cli as _cli
    tok = _cli.crear_token(a, "Prueba portal", pp, False, dias=1)
    tok_r = _cli.crear_token(a, "Prueba portal restringida", pp, True, dias=1)
    return {"proyecto": pp, "carpeta": carpeta, "token": tok, "token_r": tok_r, "nombre": proyecto_tablero.NOMBRE}


def portal_web(pedir, portal, puerto):
    """KB-97 y KB-98: rutas del portal y «actualizar ahora» por HTTP."""
    pp, t, tr = portal["proyecto"], portal["token"], portal["token_r"]
    q = urllib.parse.quote
    st_c, c, _ = pedir("/api/cartera", t)
    st_t, tb, _ = pedir(f"/api/tablero?proyecto={q(portal['nombre'])}", t)
    st_v, v, _ = pedir(f"/api/tablero/version?proyecto={pp}", t)
    st_h, h, _ = pedir(f"/api/tablero/historial?proyecto={pp}", t)
    st_k, k, _ = pedir(f"/api/tablero/comparar?proyecto={pp}&a=2026-10-05-autorizar-inicio-etapa-0&b=actual", t)
    st_i, ins, _ = pedir(f"/api/tablero?proyecto={pp}&instantanea=2026-10-20-autorizar-proyecto-etapa-1", t)
    st_a, art, _ = pedir(f"/api/artefactos?proyecto={pp}", t)
    st_d, docs, _ = pedir(f"/api/documentos?proyecto={pp}", t)
    st_f, fh, cab_f = pedir(f"/p/{q(portal['nombre'])}/ficha/{q('puerta:autorizar-inicio:0', safe='')}", t)
    st_x, _, _ = pedir(f"/api/tablero?proyecto={pp}", None)
    dd = json.loads(docs) if st_d == 200 else {}
    ver("KB-97 web: cartera, tablero (también por el nombre de estado.json), versión, historial, comparar, instantánea, artefactos, documentos y la página de la ficha",
        all(s == 200 for s in (st_c, st_t, st_v, st_h, st_k, st_i, st_a, st_d, st_f)) and st_x == 401
        and json.loads(tb)["proyecto"] == pp and "datos" not in json.loads(v) and len(json.loads(h)["instantaneas"]) == 3
        and json.loads(k)["entraron"] and json.loads(ins)["instantanea"]["decision"] == "condicionado"
        and {x["motor"] for x in dd.get("documentos", [])} >= {"archify", "diagram-design", "visual-explainer"} and 'src="/estatico/app.js"' in fh
        and "script-src 'self'" in cab_f.get("content-security-policy", ""), (st_c, st_t, st_v, st_h, st_k, st_i, st_a, st_d, st_f, st_x))
    st1, cuerpo1, cab1 = pedir(f"/archivo/{pp}/gestion/02-planificacion/visuales/wbs.html?descargar=1", t)
    st2, _, cab2 = pedir(f"/archivo/{pp}/gestion/02-planificacion/visuales/riesgos.svg", t)
    st3, _, _ = pedir(f"/archivo/{pp}/gestion/00-direccion/tolerancias-y-autoridad.md", tr)
    st4, _, _ = pedir(f"/archivo/{pp}/gestion/estado.json", t)
    st5, _, _ = pedir(f"/archivo/{pp}/..%2F..%2F..%2Fetc%2Fpasswd", t)
    st6, _, _ = pedir(f"/archivo/otro-proyecto/gestion/02-planificacion/visuales/wbs.html", t)
    ver("KB-98 web: /archivo entrega un documento visible con CSP aislada (sandbox, sin red), X-Frame-Options SAMEORIGIN y la descarga como adjunto; nada fuera de la carpeta ni de otro proyecto",
        st1 == 200 and cab1.get("content-disposition", "").startswith("attachment;") and cab1.get("content-security-policy", "").startswith("sandbox allow-scripts;")
        and "connect-src 'none'" in cab1["content-security-policy"] and cab1.get("x-frame-options") == "SAMEORIGIN" and "archify" in cuerpo1
        and st2 == 200 and cab2.get("content-type", "").startswith("image/svg+xml") and cab2.get("content-security-policy", "").startswith("sandbox;")
        and st3 == 404 and st4 == 404 and st5 == 404 and st6 == 404, (st1, st2, st3, st4, st5, st6, cab1.get("content-security-policy")))
    antes = _arbol(portal["carpeta"])
    o = f"http://127.0.0.1:{puerto}"
    s0, _, _ = pedir("/api/tablero/actualizar", t, {"proyecto": pp})                       # sin Origin
    s1, _, _ = pedir("/api/tablero/actualizar", t, {"proyecto": pp}, "http://otro.example")
    s2, c2, _ = pedir("/api/tablero/actualizar", t, {"proyecto": portal["nombre"]}, o)
    s3, c3, cab3 = pedir("/api/tablero/actualizar", t, {"proyecto": pp}, o)
    s4, _, _ = pedir("/api/tablero/actualizar", portal["token_r"], {"proyecto": "otro-proyecto"}, o)
    r2 = json.loads(c2) if s2 == 200 else {}
    ver("KB-100 actualizar ahora: exige Origin del portal (403 sin él o ajeno), regenera el tablero en el índice (origen web), 429 con Retry-After al repetir, 404 fuera del token, y no escribe en la carpeta",
        s0 == 403 and s1 == 403 and s2 == 200 and r2.get("proyecto") == pp and isinstance(r2.get("version"), int) and s3 == 429 and int(cab3.get("retry-after", "0")) > 0
        and s4 == 404 and _arbol(portal["carpeta"]) == antes, (s0, s1, s2, c2[:200], s3, s4))


def compartir_web(a, l, portal, puerto):
    """KB-101…KB-115: enlaces compartidos (pm-kb compartir, canje en /v, sesión con id propio, qué ve el destinatario,
    revocación, vencimiento, límite de canjes, --restringida, instantánea, por actor) y sesiones personales."""
    import contextlib, hashlib, io, re
    from pmkb import cli, web
    pp, nombre, t = portal["proyecto"], portal["nombre"], portal["token"]
    base = f"http://127.0.0.1:{puerto}"
    previo = os.environ.get("PMKB_ORIGENES")
    os.environ["PMKB_ORIGENES"] = base
    web.FALLOS.fallos.clear()
    q = urllib.parse.quote

    class SinRedirigir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *x, **k):
            return None
    abrir = urllib.request.build_opener(SinRedirigir).open

    def http(ruta, datos=None, cookie=None, origen=None, bearer=None, crudo=None):
        h = {"Content-Type": "application/json"}
        if cookie:
            h["Cookie"] = f"pmkb={cookie}"
        if origen:
            h["Origin"] = origen
        if bearer:
            h["Authorization"] = f"Bearer {bearer}"
        cuerpo = crudo if crudo is not None else (json.dumps(datos).encode() if datos is not None else None)
        req = urllib.request.Request(base + ruta, data=cuerpo, headers=h)
        try:
            with abrir(req, timeout=30) as r:
                return r.status, r.read().decode(), {k.lower(): v for k, v in r.headers.items()}
        except urllib.error.HTTPError as x:
            return x.code, x.read().decode(), {k.lower(): v for k, v in x.headers.items()}

    def compartir(**kw):
        ns = argparse.Namespace(**{"accion": "crear", "proyecto": None, "instantanea": None, "actor": None, "dias": cli.DIAS_ENLACE,
                                   "restringida": False, "para": None, "id": None, "json": False, **kw})
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                cli.cmd_compartir(ns)
            return 0, buf.getvalue()
        except SystemExit as x:
            return 1, buf.getvalue() + str(x.code)

    def crear(**kw):
        rc, out = compartir(accion="crear", proyecto=pp, **kw)
        m = re.search(r"^(\S+)/v#(pmkb_\S+)$", out, re.M)
        eid = re.search(r"Enlace (e-[0-9a-f]{8}) ", out)
        return (eid.group(1) if eid else None), (m.group(2) if m else None), out, (m.group(1) if m else None)

    def canjear(tok, origen=base):
        st, cuerpo, cab = http("/v/canje", {"token": tok}, origen=origen)
        m = re.search(r"pmkb=([^;]*)", cab.get("set-cookie", ""))
        return st, (m.group(1) if m else None), cab, cuerpo

    def jget(ruta, cookie):
        st, cuerpo, _ = http(ruta, cookie=cookie)
        try:
            return st, json.loads(cuerpo)
        except ValueError:
            return st, {}

    def admin(sql, *p):
        with a.transaction():
            cur = a.execute(sql, p)
            return cur.fetchall() if cur.description else None

    refs_de = lambda d: {c.get("ref") for _, c in TB.tarjetas(d)}
    try:
        # ------------------------------------------------------------ crear, listar, validaciones
        eid, tok, out, origen = crear(para="Comité de socios")
        fila = admin("SELECT token_sha, round(extract(epoch FROM vence - creado) / 86400), usos, alcance, restringida, para, creado_por FROM pmkb.enlace WHERE id = %s", eid)
        rc_l, out_l = compartir(accion="listar", proyecto=pp)
        rc_j, out_j = compartir(accion="listar", proyecto=pp, json=True)
        lj = json.loads(out_j) if rc_j == 0 else []
        ver("KB-101 compartir crear: id corto público, URL una sola vez con el origen configurado (<origen>/v#<token>), solo el sha256 en la base, 7 días por defecto; listar (texto y JSON) sin tokens",
            bool(eid and tok) and origen == base and out.count(tok) == 1 and fila and fila[0][0] == hashlib.sha256(tok.encode()).hexdigest()
            and fila[0][1:6] == (7, 0, "actual", False, "Comité de socios") and fila[0][6] and tok not in out_l and tok not in out_j
            and fila[0][0] not in out_j and eid in out_l and any(x["id"] == eid and x["estado"] == "vigente" and "token_sha" not in x for x in lj),
            (out[-300:], fila, out_l[-200:]))
        malos = [compartir(accion="crear", proyecto=pp, dias=d)[0] for d in (0, 91)]
        rc_i, out_i = compartir(accion="crear", proyecto=pp, instantanea="2026-01-01-no-existe")
        rc_a, out_a = compartir(accion="crear", proyecto=pp, actor="Nadie Inexistente")
        try:
            admin("""INSERT INTO pmkb.enlace (id, token_sha, proyecto, vence) VALUES ('e-00000000', 'x', %s, now() + interval '91 days')""", pp)
            check_db = False
        except Exception:
            check_db = True
        ver("KB-102 compartir crear rechaza --dias fuera de 1–90 (y la base, un vencimiento de más de 90 días), una instantánea inexistente y un actor que el núcleo no encuentra (tablero.py generar --actor, código 1)",
            malos == [1, 1] and check_db and rc_i == 1 and "Instantáneas publicadas" in out_i and rc_a == 1 and "No hay ningún actor" in out_a, (malos, check_db, out_i[-160:], out_a[-200:]))
        # ------------------------------------------------------------ canje
        st_v, html_v, cab_v = http("/v")
        st_x, _, _ = http("/v/canje", {"token": tok}, origen="http://otro.example")[0:3]
        st_s, _, _ = http("/v/canje", {"token": tok})[0:3]
        st, sid, cab, cuerpo = canjear(tok)
        uso = admin("SELECT usos, ultimo_uso IS NOT NULL FROM pmkb.enlace WHERE id = %s", eid)[0]
        ver("KB-103 /v es estática (CSP script-src 'self', sin scripts en línea; el token va en el fragmento) y /v/canje exige Origin de PMKB_ORIGENES (ajeno o sin Origin → 403)",
            st_v == 200 and "script-src 'self'" in cab_v.get("content-security-policy", "") and "<script>" not in html_v and 'src="/estatico/compartido.js"' in html_v
            and st_x == 403 and st_s == 403, (st_v, st_x, st_s))
        ver("KB-104 canje: cookie de sesión HttpOnly y SameSite=Strict con un id aleatorio (no el token), Max-Age ≤ 12 h, y el uso queda registrado (usos, último uso)",
            st == 200 and sid and sid != tok and "pmkb_" not in cab.get("set-cookie", "") and tok not in cab.get("set-cookie", "")
            and "httponly" in cab.get("set-cookie", "").lower() and "samesite=strict" in cab.get("set-cookie", "").lower()
            and 0 < int(re.search(r"Max-Age=(\d+)", cab.get("set-cookie", "")).group(1)) <= 12 * 3600 and uso == (1, True), (st, cab.get("set-cookie"), uso, cuerpo[:200]))
        # ------------------------------------------------------------ qué ve el destinatario
        st_e, est = jget("/api/estado", sid)
        st_t, tab = jget("/api/tablero", sid)
        st_t2, _ = jget(f"/api/tablero?proyecto={q(nombre)}", sid)
        st_ver, _ = jget("/api/tablero/version", sid)
        st_f, fc = jget("/api/ficha?id=C-001", sid)
        st_fp, fp = jget("/api/ficha?id=" + q("puerta:autorizar-proyecto:1", safe=""), sid)
        st_r, _ = jget("/api/ficha?id=R-001", sid)
        st_o, _ = jget("/api/tablero?proyecto=zz-pruebas-kb", sid)
        st_oi, _ = jget("/api/tablero?instantanea=2026-10-20-autorizar-proyecto-etapa-1", sid)
        st_of, _ = jget("/api/ficha?id=R-001&proyecto=zz-pruebas-kb", sid)
        permitidos = TB.refs(tab.get("datos") or {})
        rel_ok = all(x["id"] in permitidos for xs in (fp.get("relacionados") or {}).values() for x in xs) and all(x["id"] in permitidos for x in fp.get("relaciones") or [])
        ver("KB-105 el destinatario ve su proyecto y su tablero (también por el nombre de estado.json) y la ficha completa de una tarjeta; `/api/estado` con puede_actualizar false y la vigencia",
            st_e == 200 and est.get("puede_actualizar") is False and est.get("compartido", {}).get("proyecto") == pp and est["compartido"].get("vence")
            and not est.get("proyectos") and st_t == 200 and tab.get("proyecto") == pp and st_t2 == 200 and st_ver == 200
            and st_f == 200 and fc.get("id") == "C-001" and "solicitante" in fc.get("texto", "") and st_fp == 200 and rel_ok,
            (st_e, est, st_t, st_t2, st_ver, st_f, st_fp))
        ver("KB-106 mínimo privilegio: ficha de un id que no está en el tablero compartido → 404; otro proyecto (tablero o ficha) → 404; otra instantánea → 404; los relacionados fuera del tablero no se listan",
            st_r == 404 and st_o == 404 and st_oi == 404 and st_of == 404 and rel_ok and "R-001" not in permitidos, (st_r, st_o, st_oi, st_of))
        rech = {}
        for nom, ruta, datos, org in (("buscar", "/api/buscar?q=riesgo", None, None), ("preguntar", "/api/preguntar", {"pregunta": "¿qué riesgos hay?"}, None),
                                      ("mcp", "/mcp", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, None), ("cartera", "/api/cartera", None, None),
                                      ("actualizar", "/api/tablero/actualizar", {"proyecto": pp}, base), ("historial", f"/api/tablero/historial?proyecto={pp}", None, None),
                                      ("comparar", f"/api/tablero/comparar?proyecto={pp}&a=2026-10-05-autorizar-inicio-etapa-0&b=actual", None, None),
                                      ("artefactos", f"/api/artefactos?proyecto={pp}", None, None), ("documentos", f"/api/documentos?proyecto={pp}", None, None),
                                      ("archivo", f"/archivo/{pp}/gestion/02-planificacion/visuales/wbs.html", None, None),
                                      ("relaciones", "/api/relaciones?id=C-001", None, None), ("actores", f"/api/tablero/actores?proyecto={pp}", None, None),
                                      ("versiones", "/api/versiones?doc=x", None, None), ("documento", "/api/documento?fuente=x", None, None)):
            rech[nom] = http(ruta, datos, cookie=sid, origen=org)[0]
        st_ini, _, cab_ini = http("/", cookie=sid)
        st_p, _, cab_p = http(f"/p/{pp}/buscar", cookie=sid)
        st_b, _, _ = http("/api/estado", bearer=tok)
        ver("KB-107 con la sesión compartida, buscar, preguntar, MCP, cartera, «actualizar ahora», historial, comparar, artefactos, documentos, relaciones y actores → 403; la portada y el portal llevan a /v; el token del enlace no vale como Bearer (401)",
            all(v == 403 for v in rech.values()) and st_ini == 303 and cab_ini.get("location") == "/v" and st_p == 303 and cab_p.get("location") == "/v" and st_b == 401,
            (rech, st_ini, st_p, st_b))
        # ------------------------------------------------------------ restringida
        eid_r, tok_r, _, _ = crear(restringida=True, para="Junta")
        _, sid_r, _, _ = canjear(tok_r)
        _, tab_r = jget("/api/tablero", sid_r)
        st_fr, _ = jget("/api/ficha?id=tolerancias-y-autoridad", sid_r)
        st_fe, _ = jget("/api/ficha?id=tolerancias-y-autoridad", sid)
        ver("KB-108 --restringida: el enlace con circulación restringida ve el artefacto restringido y su ficha; sin --restringida, ni la tarjeta ni la ficha (404)",
            "tolerancias-y-autoridad" in refs_de(tab_r.get("datos") or {}) and st_fr == 200 and "tolerancias-y-autoridad" not in permitidos and st_fe == 404,
            (st_fr, st_fe))
        # ------------------------------------------------------------ instantánea
        iid = "2026-10-05-autorizar-inicio-etapa-0"
        eid_i, tok_i, _, _ = crear(instantanea=iid)
        _, sid_i, _, _ = canjear(tok_i)
        st_ti, tab_i = jget("/api/tablero", sid_i)
        st_ti2, _ = jget(f"/api/tablero?instantanea={iid}", sid_i)
        st_act, _ = jget("/api/tablero?instantanea=actual", sid_i)
        st_ei, est_i = jget("/api/estado", sid_i)
        ri = sorted(TB.refs(tab_i.get("datos") or {}))
        st_fi, fi = jget("/api/ficha?id=" + q("puerta:autorizar-inicio:0", safe=""), sid_i)
        st_fc, _ = jget("/api/ficha?id=C-001", sid_i)
        ver("KB-109 enlace a una instantánea: ve esa instantánea (no el tablero actual), la ficha muestra la tarjeta como estaba y una tarjeta que no estaba en ella → 404",
            st_ti == 200 and (tab_i.get("instantanea") or {}).get("id") == iid and st_ti2 == 200 and st_act == 404 and st_ei == 200
            and (est_i.get("compartido", {}).get("instantanea") or {}).get("id") == iid and st_fi == 200 and (fi.get("tablero") or {}).get("instantanea") == iid
            and "C-001" not in ri and st_fc == 404, (st_ti, st_ti2, st_act, st_fi, st_fc, ri[:8]))
        # ------------------------------------------------------------ por actor
        eid_la, tok_la, out_la, _ = crear(actor="Laura")
        eid_ma, tok_ma, _, _ = crear(actor="gestor")
        _, sid_la, _, _ = canjear(tok_la)
        _, sid_ma, _, _ = canjear(tok_ma)
        _, tla = jget("/api/tablero", sid_la)
        _, tma = jget("/api/tablero", sid_ma)
        rla, rma = TB.refs(tla.get("datos") or {}), TB.refs(tma.get("datos") or {})
        st_c_la, _ = jget("/api/ficha?id=C-001", sid_la)
        st_c_ma, _ = jget("/api/ficha?id=C-001", sid_ma)
        st_a_la, _ = jget("/api/ficha?id=A-001", sid_la)
        _, est_la = jget("/api/estado", sid_la)
        ver("KB-110 enlace por actor: cada uno ve solo lo suyo (reglas del núcleo); el de un actor no ve lo de otro (tarjeta ausente y ficha 404); el actor queda resuelto en el enlace",
            (tla.get("datos") or {}).get("actor", {}).get("nombre") == "Laura Méndez" and (tma.get("datos") or {}).get("actor", {}).get("nombre") == "Martín Suárez"
            and "C-001" in rla and "C-001" not in rma and st_c_la == 200 and st_c_ma == 404 and "A-001" not in rla and st_a_la == 404 and "A-001" in permitidos
            and rla != rma and "Laura Méndez" in est_la.get("compartido", {}).get("actor", "") and "Laura Méndez (ejecutivo)" in out_la,
            (sorted(rla), sorted(rma), st_c_la, st_c_ma, st_a_la))
        stp, tp = http(f"/api/tablero?proyecto={pp}&actor=Laura", bearer=t)[0:2]
        tpd = json.loads(tp) if stp == 200 else {}
        sta, ac = http(f"/api/tablero/actores?proyecto={pp}", bearer=t)[0:2]
        acd = json.loads(ac) if sta == 200 else {}
        stn, tn = http(f"/api/tablero?proyecto={pp}&actor=Nadie", bearer=t)[0:2]
        stc, cmpa = http(f"/api/tablero/comparar?proyecto={pp}&a=2026-10-05-autorizar-inicio-etapa-0&b=actual&actor=gestor", bearer=t)[0:2]
        stin, tin = http(f"/api/tablero?proyecto={pp}&instantanea=2026-10-20-autorizar-proyecto-etapa-1&actor=gestor", bearer=t)[0:2]
        ver("KB-111 portal «Por actor» (token personal): actores del proyecto, tablero actual e instantánea filtrados con las mismas reglas que el enlace, comparar filtrado y actor inexistente → 404 con la lista",
            stp == 200 and TB.refs(tpd.get("datos") or {}) == rla and sta == 200 and {x["nombre"] for x in acd.get("actores", [])} >= {"Laura Méndez", "Martín Suárez"}
            and stn == 404 and "Actores:" in json.loads(tn).get("error", "") and stc == 200 and "C-001" not in [x["ref"] for x in json.loads(cmpa).get("entraron", [])]
            and stin == 200 and json.loads(tin).get("datos", {}).get("actor", {}).get("nombre") == "Martín Suárez", (stp, sta, stn, stc, stin))
        # ------------------------------------------------------------ revocación, vencimiento, sesión ≤ enlace
        antes = http("/api/tablero", cookie=sid_ma)[0]
        rc_rv, out_rv = compartir(accion="revocar", id=eid_ma)
        despues = http("/api/tablero", cookie=sid_ma)[0]
        st_rc = canjear(tok_ma)[0]
        rc_rp, out_rp = compartir(accion="revocar", proyecto=pp, para="Junta")
        quedan = {r[0]: r[1] for r in admin("SELECT id, revocado IS NOT NULL FROM pmkb.enlace WHERE proyecto = %s", pp)}
        ver("KB-112 revocar corta la sesión abierta en la petición siguiente y el enlace ya no se canjea; revocar --proyecto --para revoca solo los de ese destinatario",
            antes == 200 and rc_rv == 0 and "1 enlace(s) revocado(s)" in out_rv and despues == 401 and st_rc == 401 and rc_rp == 0 and quedan.get(eid_r) is True
            and quedan.get(eid) is False and quedan.get(eid_la) is False, (antes, despues, st_rc, out_rv, out_rp, quedan))
        admin("UPDATE pmkb.enlace SET vence = now() - interval '1 minute' WHERE id = %s", eid_la)
        st_venc = http("/api/tablero", cookie=sid_la)[0]
        st_venc_c = canjear(tok_la)[0]
        eid_c, tok_c, _, _ = crear(dias=1)
        admin("UPDATE pmkb.enlace SET vence = now() + interval '2 hours' WHERE id = %s", eid_c)
        st_cc, sid_c, cab_c, _ = canjear(tok_c)
        dif = admin("SELECT abs(extract(epoch FROM s.vence - e.vence)) FROM pmkb.sesion s JOIN pmkb.enlace e ON e.id = s.enlace WHERE e.id = %s", eid_c)
        edad = int(re.search(r"Max-Age=(\d+)", cab_c.get("set-cookie", "") or "Max-Age=0").group(1))
        ver("KB-113 vencimiento (fecha simulada en la base): la sesión abierta cae y el enlace no se canjea; la sesión nunca dura más que el enlace (cookie ≤ 2 h si al enlace le quedan 2 h)",
            st_venc == 401 and st_venc_c == 401 and st_cc == 200 and dif and dif[0][0] < 1 and 0 < edad <= 7200, (st_venc, st_venc_c, st_cc, dif, edad))
        # ------------------------------------------------------------ sesiones personales
        req = urllib.request.Request(base + "/ingresar", data=urllib.parse.urlencode({"token": t}).encode(),
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with abrir(req, timeout=10) as r:
                cab_in = {k.lower(): v for k, v in r.headers.items()}
        except urllib.error.HTTPError as x:
            cab_in = {k.lower(): v for k, v in x.headers.items()}
        sidp = (re.search(r"pmkb=([^;]*)", cab_in.get("set-cookie", "")) or [None, None])[1]
        st_p1, ep = jget("/api/estado", sidp)
        st_sal, _, cab_sal = http("/salir", {}, cookie=sidp)
        st_p2 = http("/api/estado", cookie=sidp)[0]
        tq = cli.crear_token(a, "Prueba portal sesión", pp, False, dias=1)
        req = urllib.request.Request(base + "/ingresar?token=" + q(tq))
        try:
            with abrir(req, timeout=10) as r:
                cab_q = {k.lower(): v for k, v in r.headers.items()}
        except urllib.error.HTTPError as x:
            cab_q = {k.lower(): v for k, v in x.headers.items()}
        sidq = (re.search(r"pmkb=([^;]*)", cab_q.get("set-cookie", "")) or [None, None])[1]
        st_q1 = http("/api/estado", cookie=sidq)[0]
        with contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_token(argparse.Namespace(accion="revocar", persona="Prueba portal sesión"))
        st_q2 = http("/api/estado", cookie=sidq)[0]
        ver("KB-114 sesiones personales: /ingresar deja un id de sesión (no el token) en la cookie; /salir la borra; revocar el token corta su sesión en la petición siguiente",
            sidp and sidp != t and "pmkb_" not in cab_in.get("set-cookie", "") and st_p1 == 200 and ep.get("puede_actualizar") is True and st_sal == 303
            and st_p2 == 401 and sidq and st_q1 == 200 and st_q2 == 401, (sidp is not None, st_p1, st_sal, st_p2, st_q1, st_q2))
        # ------------------------------------------------------------ límite de canjes fallidos
        web.FALLOS.fallos.clear()
        sts = [canjear("pmkb_falso" + str(i))[0] for i in range(11)]
        st_429, _, cab_429 = http("/v/canje", {"token": tok}, origen=base)
        web.FALLOS.fallos.clear()
        ver("KB-115 límite de canjes fallidos por IP: 10 × 401 y después 429 con Retry-After (también para un token válido)",
            sts[:10] == [401] * 10 and sts[10] == 429 and st_429 == 429 and int(cab_429.get("retry-after", "0")) > 0, (sts, st_429))
        # ------------------------------------------------------------ RLS y grants
        with l.transaction():
            fun = l.execute("""SELECT has_table_privilege('pmkb_lector', 'pmkb.enlace', 'SELECT'), has_table_privilege('pmkb_lector', 'pmkb.sesion', 'SELECT'),
                                      has_function_privilege('pmkb_lector', 'pmkb.canjear(text, text, int)', 'EXECUTE'),
                                      has_function_privilege('pmkb_lector', 'pmkb.sesion_identidad(text)', 'EXECUTE'),
                                      (SELECT bool_and(relrowsecurity) FROM pg_class WHERE oid IN ('pmkb.enlace'::regclass, 'pmkb.sesion'::regclass))""").fetchone()
        try:
            with l.transaction():
                l.execute("SELECT token_sha FROM pmkb.enlace").fetchall()
            lee = True
        except Exception:
            lee = False
        ver("KB-116 RLS y permisos: el rol lector no lee pmkb.enlace ni pmkb.sesion (hashes), solo ejecuta las funciones de canje y sesión",
            fun == (False, False, True, True, True) and not lee, (fun, lee))
    finally:
        if previo is None:
            os.environ.pop("PMKB_ORIGENES", None)
        else:
            os.environ["PMKB_ORIGENES"] = previo
        web.FALLOS.fallos.clear()


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

