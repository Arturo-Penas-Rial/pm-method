#!/usr/bin/env python3
"""Suite de integración cruzada de pm-method: encadena las fuentes y las skills sobre un mismo proyecto temporal y
verifica, en cada eslabón, que el dato que produce una fuente lo consume la siguiente sin volver a escribirlo a mano,
con integridad referencial (ids, sumas y fechas).

Uso / Usage:
  python3 scripts/pruebas/integracion/correr.py [--sin-e2e | --e2e DIR] [--conservar] [--json ARCHIVO]

Cadenas (un solo proyecto, copia de scripts/pruebas/fixtures/bmad-v6.12-real; la fixture no se modifica):
  1. BMAD → bmad.py / especificacion.py → requisitos, épicas e historias → backlog → WBS → cpm.py → evm.py → okr.py
     → sanidad.py → puertas.py
  2. transcripción (transcripcion.py) + instantánea de Jira + BMAD → riesgos.py candidatos → registro de riesgos e
     issues → presupuestos de la junta y cambios (CAM) → sanidad --informe → tablero de avance
  3. interesados.py (matriz, preferencias, RACI ligada a épicas, requisitos y KR) ↔ okr.py ↔ envios.py (archivo .eml,
     sin red) → registro de envíos → familia STK
  4. mapas.py (Wardley y recorrido) desde BMAD y desde la WBS → vínculos a requisitos, riesgos, issues y decisiones →
     familia MAP de sanidad → inversion.py con las opciones del business case
  5. exportar.py (xlsx y docx) y paquete.py de una puerta con todos los artefactos → verificación del contenido;
     huella de BMAD sin cambios
  6. salidas de los recorridos E2E (scripts/pruebas/guias_e2e/, en paralelo) → webinar/generar.py --validar y, si hay
     Node.js con pptxgenjs, la generación real (HTML y PPTX con las imágenes de los recorridos)
Lo que en la práctica decide o redacta una persona o el modelo (estimaciones, coordenadas del mapa, texto de un
mensaje, costos reales) se simula con valores fijos; todo lo demás se toma de la salida del eslabón anterior.
Sin red: los envíos usan el modo .eml. Código de salida 1 si falla alguna comprobación. Requiere PyYAML; openpyxl y
python-docx son opcionales (sin ellos se omiten las comprobaciones de exportar.py, con aviso).
--sin-e2e omite la cadena 6; --e2e DIR usa salidas ya generadas por guias_e2e/correr.py en lugar de correr los recorridos.
EN: cross-integration suite: chains BMAD, transcripts, Jira, stakeholders, OKR, channels, maps, investment appraisal,
export and gate packages on one temporary project and checks referential integrity at every link.
"""
import argparse, csv, datetime, glob, hashlib, json, math, os, re, shutil, subprocess, sys, tempfile, time, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", ".."))
SK = os.path.join(RAIZ, "skills")
S = os.path.join(SK, "pm-estado-proyecto", "scripts")
SCR = {
    "estado": os.path.join(S, "estado.py"), "registro": os.path.join(S, "registro.py"), "nuevo": os.path.join(S, "nuevo_proyecto.py"),
    "espec": os.path.join(S, "especificacion.py"), "sanidad": os.path.join(S, "sanidad.py"), "puertas": os.path.join(S, "puertas.py"),
    "wbs": os.path.join(S, "wbs.py"), "cpm": os.path.join(S, "cpm.py"), "evm": os.path.join(S, "evm.py"), "exportar": os.path.join(S, "exportar.py"),
    "bmad": os.path.join(SK, "pm-bmad-puente", "scripts", "bmad.py"), "okr": os.path.join(SK, "pm-okr", "scripts", "okr.py"),
    "riesgos": os.path.join(SK, "pm-riesgos", "scripts", "riesgos.py"), "transcripcion": os.path.join(SK, "pm-reuniones", "scripts", "transcripcion.py"),
    "interesados": os.path.join(SK, "pm-interesados", "scripts", "interesados.py"), "envios": os.path.join(SK, "pm-integraciones", "scripts", "envios.py"),
    "mapas": os.path.join(SK, "pm-mapas-estrategicos", "scripts", "mapas.py"), "inversion": os.path.join(SK, "pm-caso-de-negocio", "scripts", "inversion.py"),
    "paquete": os.path.join(SK, "pm-exportar", "scripts", "paquete.py"), "generar": os.path.join(RAIZ, "scripts", "webinar", "generar.py"),
    "e2e": os.path.join(RAIZ, "scripts", "pruebas", "guias_e2e", "correr.py"),
}
FIXTURE = os.path.join(RAIZ, "scripts", "pruebas", "fixtures", "bmad-v6.12-real")
TABLERO = os.path.join(SK, "pm-visuales", "templates", "tablero-avance.html")
G = "gestion"
RES = {"ok": 0, "fallo": 0, "eslabones": []}
D = {}   # datos que pasan de un eslabón al siguiente


class Falla(Exception):
    pass


def run(clave, *args, cwd=None, ok=(0,), entrada=None, env=None):
    """Ejecuta un script del paquete con el mismo intérprete; si el código de salida no es el esperado, Falla."""
    r = subprocess.run([sys.executable, SCR[clave]] + [str(a) for a in args], cwd=cwd or D["repo"], capture_output=True, text=True,
                       input=entrada, env=env)
    if ok is not None and r.returncode not in ok:
        raise Falla(f"{os.path.basename(SCR[clave])} {' '.join(str(a) for a in args)[:160]} → código {r.returncode}\n{(r.stdout + r.stderr)[-700:]}")
    return r


def js(clave, *args, **kw):
    r = run(clave, *args, **kw)
    try:
        return json.loads(r.stdout)
    except ValueError:
        raise Falla(f"{os.path.basename(SCR[clave])} {' '.join(args)[:120]}: la salida no es JSON: {r.stdout[:300]}")


def check(eslabon, nombre, cond, detalle=""):
    RES["ok" if cond else "fallo"] += 1
    RES["eslabones"].append({"eslabon": eslabon, "comprobacion": nombre, "ok": bool(cond), "detalle": "" if cond else str(detalle)[:600]})
    print(f"  {'OK   ' if cond else 'FALLO'} [{eslabon}] {nombre}" + (f" — {str(detalle)[:600]}" if detalle and not cond else ""))


def eslabon(codigo, titulo):
    """Decorador: un eslabón que lanza una excepción cuenta como FALLO con el mensaje, y la suite sigue."""
    def deco(f):
        def envuelto(*a, **k):
            print(f"\n[{codigo}] {titulo}")
            t0 = time.time()
            try:
                f(*a, **k)
            except Falla as x:
                check(codigo, "el eslabón se ejecutó sin errores", False, x)
            except Exception as x:   # un error de programación de la suite también se informa como fallo del eslabón
                check(codigo, "el eslabón se ejecutó sin errores", False, f"{type(x).__name__}: {x}")
            print(f"  ({time.time() - t0:.1f} s)")
        return envuelto
    return deco


def P(*partes): return os.path.join(D["repo"], G, *partes)
def leer_csv(ruta): return list(csv.DictReader(open(ruta, encoding="utf-8")))
def escribir(rel, texto):
    p = P(rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w", encoding="utf-8").write(texto); return p
def escribir_csv(ruta, cab, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab); w.writeheader(); w.writerows(filas)
def sha(ruta): return hashlib.sha256(open(ruta, "rb").read()).hexdigest()
def reg(*a): return run("registro", "--proyecto", G, *a).stdout.strip().splitlines()[-1].split()[0]
def reg_js(*a): return js("registro", "--proyecto", G, *a, "--json")
def san(corte, *extra): return json.loads(run("sanidad", "--proyecto", G, "--json", "--corte", corte, *extra, ok=(0, 1)).stdout)
def cods(d, sev=None): return {h["codigo"] for h in d["hallazgos"] if sev is None or h["severidad"] == sev}
def hall(d, codigo): return [h for h in d["hallazgos"] if h["codigo"] == codigo]
def art(clave, rel, texto, estado="en-revision"):
    escribir(rel, f"---\ntipo: {clave}\nestado: {estado}\n---\n{texto}\n")
    run("estado", "--proyecto", G, "artefacto", clave, "--ruta", rel, "--estado", estado)


def huella_bmad():
    """sha256 de cada archivo de BMAD (_bmad/ y _bmad-output/) salvo sprint-status.yaml, que el equipo BMAD actualiza
    (aquí lo simula la suite)."""
    out = {}
    for r in sorted(glob.glob(os.path.join(D["repo"], "_bmad*", "**", "*"), recursive=True)):
        if os.path.isfile(r) and not r.endswith("sprint-status.yaml"):
            out[os.path.relpath(r, D["repo"])] = sha(r)
    return out


def dias_habiles(inicio, fin):
    """Días hábiles (lunes a viernes) entre dos fechas, con la misma regla que cpm.py."""
    n, d = 0, inicio
    while d < fin:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5: n += 1
    return n


# ================================================================== cadena 1
@eslabon("1.1", "BMAD → bmad.py → especificacion.py (fachada): requisitos, épicas e historias")
def c1_especificacion():
    D["huella"] = huella_bmad()
    run("nuevo", "--ruta", G, "--nombre", "Portal de autoservicio para socios", "--enfoque", "hibrido", "--ejecutivo", "Laura Méndez",
        "--gestor", "Martín Suárez", "--fecha", "2026-11-02")
    det = js("bmad", "--proyecto", G, "detectar")
    run("estado", "--proyecto", G, "integracion", "especificacion=bmad")
    run("bmad", "--proyecto", G, "requisitos")
    filas = leer_csv(P("02-planificacion", "especificacion", "requisitos-bmad.csv"))
    req = js("espec", "--proyecto", G, "listar", "requisitos", "--limite", "0", "--json")
    his = js("espec", "--proyecto", G, "listar", "historias", "--limite", "0", "--json")
    epi = js("espec", "--proyecto", G, "listar", "epicas", "--limite", "0", "--json")
    res = js("espec", "--proyecto", G, "resumen", "--json")
    D.update(req=req, his=his, epi=epi)
    ids_csv = {f.get("id") for f in filas}
    check("1.1", f"detectar: BMAD {det.get('soporte')} desde manifest.yaml; la fachada expone los mismos {len(req)} ids que requisitos-bmad.csv",
          det.get("soporte") == "soportada" and {r["id"] for r in req} == ids_csv and res["requisitos"] == len(req), f"{len(req)} vs {len(ids_csv)}")
    h_epi = {h for e in epi for h in e["historias"]}
    check("1.1", f"épicas e historias coherentes: {len(epi)} épicas cubren las {len(his)} historias; cada historia apunta a su épica",
          h_epi == {h["id"] for h in his} and all(h["id"] in next(e["historias"] for e in epi if e["id"] == h["epica"]) for h in his))
    frs = {r["id"] for r in req if r["tipo"] == "FR"}
    check("1.1", "trazas FR → historias: cada FR citado por una épica figura con esas historias en la fachada",
          all(set(r["historias"]) == {h for e in epi if r["id"] in e["refs"] for h in e["historias"]} for r in req if r["id"] in frs),
          [r["id"] for r in req if r["id"] in frs][:5])


@eslabon("1.2", "historias → backlog.csv (columnas de gobierno) → WBS por productos → wbs.py")
def c1_wbs():
    run("bmad", "--proyecto", G, "backlog")
    pb = P("02-planificacion", "backlog.csv"); filas = leer_csv(pb); cab = list(filas[0].keys())
    check("1.2", "backlog.csv tiene exactamente las historias de la fachada", sorted(f["id"] for f in filas) == sorted(h["id"] for h in D["his"]))
    # gobierno (pm-agil-hibrido): estimación y MoSCoW los decide el equipo; aquí valores fijos derivados del número de historia
    for f in filas:
        n = int(re.match(r"(\d+)-(\d+)", f["id"]).group(2))
        f["estimacion"] = str(3 + 2 * n); f["moscow"] = "Must" if n <= 2 else "Should"
    escribir_csv(pb, cab, filas)
    run("bmad", "--proyecto", G, "backlog")
    est = {f["id"]: int(f["estimacion"]) for f in leer_csv(pb)}
    check("1.2", "bmad.py backlog conserva las columnas de gobierno al regenerar", est and all(est[h] == 3 + 2 * int(re.match(r"\d+-(\d+)", h).group(1)) for h in est))
    nfr = [r["id"] for r in D["req"] if r["tipo"] == "NFR"]
    lineas = ["codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref"]
    paquete_de, producto_de = {}, {}
    for e in D["epi"]:
        n = e["id"].split("-")[1]
        lineas.append(f'{n},"{e["titulo"]}",producto,Lucía Benítez,,,{"; ".join(e["refs"])}')
        producto_de[e["id"]] = n
        for h in (x for x in D["his"] if x["epica"] == e["id"]):
            cod = h["numero"]; horas = est[h["id"]] * 8
            lineas.append(f'{cod},"{h["titulo"]}",paquete,Lucía Benítez,{horas},{horas * 50},{h["id"]}')
            paquete_de[h["id"]] = cod
    nt = str(len(D["epi"]) + 1)
    lineas += [f"{nt},Transición,producto,Sofía Ramírez,,,", f'{nt}.1,Pruebas no funcionales y puesta en producción,paquete,Sofía Ramírez,120,6000,{"; ".join(nfr)}']
    escribir("02-planificacion/wbs.csv", "\n".join(lineas) + "\n")
    w = js("wbs", P("02-planificacion", "wbs.csv"), "--json")
    costo = sum(est[h] * 8 * 50 for h in est) + 6000
    D.update(est=est, paquete_de=paquete_de, producto_de=producto_de, nfr=nfr, transicion=f"{nt}.1", bac=w["total_costo"], wbs=w)
    check("1.2", f"wbs.py: {len(D['his'])} paquetes de historia + 1 de transición; costo consolidado {w['total_costo']:.0f} = Σ estimación × 8 h × 50 + 6000; sin avisos",
          w["hojas"] == len(D["his"]) + 1 and abs(w["total_costo"] - costo) < 0.01 and not w["avisos"], f"{w['hojas']} {w['total_costo']} {w['avisos']}")


@eslabon("1.3", "WBS → bmad.py trazabilidad → fachada (FR → historias → paquetes) sin requisitos sin cobertura")
def c1_trazabilidad():
    run("bmad", "--proyecto", G, "trazabilidad", "--wbs", "02-planificacion/wbs.csv")
    req = {r["id"]: r for r in js("espec", "--proyecto", G, "listar", "requisitos", "--limite", "0", "--json")}
    malos = [i for i, r in req.items() if r["tipo"] == "FR" and set(r["paquetes_wbs"]) != {D["producto_de"][e] for e in r["epicas"]}]
    check("1.3", "cada FR llega al producto de la WBS de su épica (la WBS cita los FR que la fachada asignó a la épica)",
          not malos and all(r["paquetes_wbs"] for r in req.values() if r["tipo"] == "FR"), malos[:5])
    his = {h["id"]: h for h in js("espec", "--proyecto", G, "listar", "historias", "--limite", "0", "--json")}
    check("1.3", "cada historia llega a su paquete de trabajo (código = número de la historia en BMAD)",
          all(his[h]["paquetes_wbs"] == [D["paquete_de"][h]] for h in D["paquete_de"]), {h: his[h]["paquetes_wbs"] for h in list(his)[:3]})
    check("1.3", f"cada NFR ({len(D['nfr'])}) llega al paquete de transición {D['transicion']}", all(req[n]["paquetes_wbs"] == [D["transicion"]] for n in D["nfr"]),
          {n: req[n]["paquetes_wbs"] for n in D["nfr"]})
    res = js("espec", "--proyecto", G, "resumen", "--json")
    check("1.3", "resumen de la fachada: sin requisitos sin cobertura", res["sin_cobertura"] == [], res["sin_cobertura"])
    D["req_idx"] = req


@eslabon("1.4", "WBS → actividades → cpm.py (camino crítico y MSPDI)")
def c1_cpm():
    hojas = [n for n in D["wbs"]["nodos"] if n["tipo"] == "paquete"]
    filas, previo = [], {}
    for n in hojas:
        prod = n["codigo"].split(".")[0]
        dur = math.ceil(n["esfuerzo_h"] / 8)
        pred = previo.get(prod, "") if n["codigo"] != D["transicion"] else ";".join(sorted(previo.values()))
        filas.append({"id": f"WP-{n['codigo']}", "nombre": n["nombre"], "duracion": dur, "predecesoras": pred, "recurso": n["responsable"], "wbs": n["codigo"]})
        if n["codigo"] != D["transicion"]: previo[prod] = f"WP-{n['codigo']}"
    escribir_csv(P("02-planificacion", "actividades.csv"), ["id", "nombre", "duracion", "predecesoras", "recurso", "wbs"], filas)
    c = js("cpm", P("02-planificacion", "actividades.csv"), "--inicio", "2026-12-01", "--json")
    run("cpm", P("02-planificacion", "actividades.csv"), "--inicio", "2026-12-01", "--mspdi", P("02-planificacion", "cronograma.xml"), "--wbs", P("02-planificacion", "wbs.csv"))
    cadena = {}
    for f in filas:
        if f["wbs"] != D["transicion"]: cadena.setdefault(f["wbs"].split(".")[0], []).append(f)
    larga = max(cadena.values(), key=lambda xs: sum(x["duracion"] for x in xs))
    esperado = sum(x["duracion"] for x in larga) + next(f["duracion"] for f in filas if f["wbs"] == D["transicion"])
    criticas = c["camino_critico"]
    check("1.4", f"duración total {c['duracion_total']} días = épica más larga ({sum(x['duracion'] for x in larga)}) + transición; su cadena es el camino crítico",
          c["duracion_total"] == esperado and all(x["id"] in criticas for x in larga), f"{c['duracion_total']} vs {esperado}; {criticas}")
    import xml.dom.minidom as minidom
    tareas = minidom.parse(P("02-planificacion", "cronograma.xml")).getElementsByTagName("Task")
    check("1.4", f"MSPDI bien formado con las {len(filas)} actividades (más resúmenes de la WBS)", len(tareas) >= len(filas))
    D.update(cpm=c, actividades=filas)


@eslabon("1.5", "BMAD sprint-status → bmad.py avance (puntos del backlog) → evm.py --guardar")
def c1_evm():
    hechas = [x for x in D["his"] if x["numero"].endswith(".1")]
    curso = [x for x in D["his"] if x["numero"].endswith(".2")]
    ss = os.path.join(D["repo"], "_bmad-output", "implementation-artifacts", "sprint-status.yaml")
    t = open(ss, encoding="utf-8").read()
    for h, v in [(x, "done") for x in hechas] + [(x, "in-progress") for x in curso]:
        t, n = re.subn(rf"(?m)^(\s*{re.escape(h['id'])}:)\s*\S+", rf"\1 {v}", t)
        if n != 1: raise Falla(f"sprint-status.yaml no tiene la clave {h['id']}")
    open(ss, "w", encoding="utf-8").write(t)
    av = js("bmad", "--proyecto", G, "avance", "--corte", "2027-01-15", "--json")
    pts = sum(D["est"][h["id"]] for h in hechas)
    check("1.5", f"avance: {len(hechas)} historias done y {pts} de {sum(D['est'].values())} puntos (estimaciones del backlog)",
          av["done"] == len(hechas) and av["in-progress"] == len(curso) and av["puntos_terminados"] == pts and av["puntos_total"] == sum(D["est"].values()), av)
    costo = {n["codigo"]: n["costo"] for n in D["wbs"]["nodos"] if n["tipo"] == "paquete"}
    ev = sum(costo[D["paquete_de"][h["id"]]] for h in hechas)
    t_corte = dias_habiles(datetime.date(2026, 12, 1), datetime.date(2027, 1, 15))
    act = {a["id"]: a for a in D["cpm"]["actividades"]}
    pv = sum(costo[f["wbs"]] * min(max(t_corte - act[f["id"]]["ES"], 0), act[f["id"]]["dur"]) / act[f["id"]]["dur"] for f in D["actividades"])
    ac = round(ev * 1.07, 2)   # costo real: lo informa contabilidad (simulado)
    r = js("evm", "--pv", f"{pv:.2f}", "--ev", f"{ev:.2f}", "--ac", f"{ac:.2f}", "--bac", f"{D['bac']:.2f}", "--tol-costo", "10", "--tol-plazo", "10",
           "--proyecto", G, "--guardar", "--corte", "2027-01-15", "--json")
    g = json.load(open(P("03-control", "reportes", "evm-2027-01-15.json"), encoding="utf-8"))
    check("1.5", f"evm-2027-01-15.json: BAC = costo de la WBS ({D['bac']:.0f}), EV = paquetes de historias done ({ev:.0f}), PV del cronograma CPM ({pv:.0f}), CPI = EV/AC",
          abs(g["BAC"] - D["bac"]) < 0.01 and abs(g["EV"] - ev) < 0.01 and abs(g["PV"] - pv) < 0.01 and abs(g["CPI"] - ev / ac) < 1e-6 and r[-1]["CPI"] == g["CPI"], g)
    D.update(evm=g, avance=av, hechas=hechas)


@eslabon("1.6", "métricas de éxito SM-n de BMAD → okr.py (KR vinculados) → sanidad ESP-04 valida los vínculos")
def c1_okr():
    sm = [r for r in D["req"] if r["tipo"] == "SM"][:3]
    lin = ["id,tipo,objetivo_id,enunciado,metrica,linea_base,meta,actual,unidad,responsable,fecha_meta,vinculo,confianza,notas,tipo_kr,compromiso,peso,padre_id,nivel,ciclo,fecha_inicio,estado,ref_externa",
           "O-1,objetivo,,Los socios resuelven sus gestiones simples en línea,,,,,,Laura Méndez,,OBJ-1,,,,,,,proyecto,,2026-12-01,activo,"]
    for i, s in enumerate(sm, 1):
        lin.append(f'KR-1.{i},kr,O-1,"{s["titulo"][:60]}",{s["id"]},0,100,,%,Sofía Ramírez,2027-12-31,{s["id"]}; B-0{i},,,de-a,,1,,,,,activo,')
    for e in D["epi"]:
        lin.append(f'IN-{e["id"]},iniciativa,KR-1.1,"{e["titulo"][:60]}",,,,,,Lucía Benítez,,{e["id"]},,,,,1,,,,,activo,')
    lin.append("KR-1.9,kr,O-1,Métrica mal citada,SM-99,0,1,,n,Sofía Ramírez,2027-12-31,SM-99,,,de-a,,1,,,,,activo,")
    escribir("00-direccion/okr.csv", "\n".join(lin) + "\n")
    run("okr", P("00-direccion", "okr.csv"), "--checkin", "KR-1.1", "--valor", "40", "--confianza", "7", "--fecha", "2027-01-15", "--autor", "Sofía Ramírez")
    o = js("okr", P("00-direccion", "okr.csv"), "--corte", "2027-01-20", "--json")
    k = {x["id"]: x for ob in o["objetivos"] for x in ob["krs"]}
    check("1.6", f"okr.py: KR vinculados a {', '.join(s['id'] for s in sm)} (de la fachada); KR-1.1 toma el check-in (0,40)",
          all(s["id"] in (k[f"KR-1.{i}"]["vinculo"] or "") for i, s in enumerate(sm, 1)) and abs(k["KR-1.1"]["puntuacion"] - 0.4) < 1e-9, json.dumps(k, ensure_ascii=False)[:300])
    d = san("2027-01-20")
    e4 = [h["mensaje"] for h in hall(d, "ESP-04")]
    check("1.6", "sanidad ESP-04: el KR que cita SM-99 (inexistente en BMAD) es ERROR; los SM reales no", any("KR-1.9" in m and "SM-99" in m for m in e4)
          and not any("KR-1.1" in m for m in e4), e4)
    escribir("00-direccion/okr.csv", "\n".join(x for x in lin if not x.startswith("KR-1.9")) + "\n")
    D["sm"] = [s["id"] for s in sm]
    run("estado", "--proyecto", G, "artefacto", "okr", "--ruta", "00-direccion/okr.csv", "--estado", "en-revision")


@eslabon("1.7", "todo lo anterior → sanidad.py (0 ERROR, TOL lee el EVM guardado) → puertas.py verificar/registrar")
def c1_puertas():
    run("estado", "--proyecto", G, "rol", "usuario_senior=Sofía Ramírez", "proveedor_senior=Diego Ferreira", "product_owner=Sofía Ramírez",
        "autoridad_cambio=Sofía Ramírez", "aseguramiento=Andrea Costa", "jefes_equipo=Lucía Benítez")
    art("project-brief", "01-inicio/project-brief.md", "# Project brief\nProducto definido en el brief de BMAD.")
    art("plan-etapa-1", "02-planificacion/plan-etapa-1.md", "# Plan de la etapa de iniciación")
    for tipo, fecha, extra in (("autorizar-inicio", "2026-11-10", ()),):
        run("puertas", "--proyecto", G, "lista", tipo, "--fecha", fecha)
        run("puertas", "--proyecto", G, "confirmar", tipo, "--por", "Ejecutivo: Laura Méndez", "--fecha", fecha)
        run("estado", "--proyecto", G, "puerta", tipo, "--decision", "aprobado", "--por", "Ejecutivo: Laura Méndez", "--fecha", fecha, *extra)
    sm = "; ".join(D["sm"])
    art("business-case", "00-direccion/business-case.md", f"# Business case\nBeneficios B-01, B-02 y B-03 medidos con {sm} (okr.csv).\nBAC {D['bac']:.0f}.")
    art("pid", "00-direccion/pid.md", "# PID\nIncluye el plan de proyecto (WBS 02-planificacion/wbs.csv y cronograma CPM).")
    art("plan-proyecto", "02-planificacion/plan-proyecto.md", "# Plan de proyecto\nWBS, CPM y línea base de costo.")
    art("enfoque-beneficios", "00-direccion/enfoque-beneficios.md", f"# Enfoque de beneficios\nB-01..B-03 con {sm}; dueña: Sofía Ramírez.")
    art("plan-etapa-2", "02-planificacion/plan-etapa-2.md", "# Plan de la etapa 2 (Release 1)")
    run("estado", "--proyecto", G, "tolerancia", "--nivel", "proyecto", "tiempo=±3 semanas", "costo=±10 %", "riesgo=ningún riesgo alto sin respuesta")
    run("bmad", "--proyecto", G, "linea-base", "prd", "--version", "1.0", "--por", "Ejecutivo: Laura Méndez", "--fecha", "2026-11-27")
    d = san("2027-01-15")
    tol = hall(d, "TOL-01") + hall(d, "TOL-02")
    check("1.7", "sanidad: 0 ERROR (ESP-03/ESP-04 limpios) y la familia TOL lee evm-2027-01-15.json",
          not cods(d, "ERROR") and tol and all("2027-01-15" in h["mensaje"] for h in tol), [h["codigo"] + " " + h["mensaje"][:90] for h in d["hallazgos"] if h["severidad"] == "ERROR" or h["codigo"].startswith("TOL")])
    v = js("puertas", "--proyecto", G, "verificar", "autorizar-proyecto", "--json", ok=(0, 1, 2))
    texto = json.dumps(v, ensure_ascii=False)
    check("1.7", "puertas verificar autorizar-proyecto: sin bloqueos y sin la condición de criterios de éxito (los toma de okr.csv y del business case)",
          not [b for b in v["bloqueos"] if "lista de control" not in b] and "criterios de éxito" not in texto, v["bloqueos"] + v["condiciones"])
    run("puertas", "--proyecto", G, "lista", "autorizar-proyecto", "--fecha", "2026-11-27")
    run("puertas", "--proyecto", G, "confirmar", "autorizar-proyecto", "--por", "Ejecutivo: Laura Méndez", "--fecha", "2026-11-27")
    run("estado", "--proyecto", G, "puerta", "autorizar-proyecto", "--decision", "aprobado", "--por", "Ejecutivo: Laura Méndez", "--fecha", "2026-11-27")
    e = json.load(open(P("estado.json"), encoding="utf-8"))
    dec = leer_csv(P("03-control", "registros", "decisiones.csv"))
    check("1.7", "puerta autorizar-proyecto registrada; decisiones.csv tiene la línea base del PRD y la puerta con la fecha de la junta",
          e["proyecto_autorizado"] and any(p["tipo"] == "autorizar-proyecto" and p["fecha"] == "2026-11-27" for p in e["puertas"])
          and any("prd" in x["decision"].lower() and x["fecha"] == "2026-11-27" for x in dec), [p.get("tipo") for p in e["puertas"]])


# ================================================================== cadena 2
VTT = """WEBVTT

00:00:05.000 --> 00:00:14.000
<v Diego Ferreira>Nos preocupa que el núcleo no tenga entorno de pruebas para la integración de saldos; dependemos del área de sistemas centrales.

00:00:15.000 --> 00:00:22.000
<v Sofía Ramírez>Podríamos aprovechar el generador de constancias que ya usa la sucursal.

00:00:23.000 --> 00:00:30.000
<v Sofía Ramírez>Prefiero que me lleguen los avances por correo, un resumen ejecutivo.

00:00:31.000 --> 00:00:33.000
<v Martín Suárez>Gracias a todos, buen día.
"""


@eslabon("2.1", "transcripción VTT → transcripcion.py → acta normalizada en 03-control/reuniones")
def c2_transcripcion():
    vtt = os.path.join(D["tmp"], "ronda-riesgos.vtt"); open(vtt, "w", encoding="utf-8").write(VTT)
    rel = "03-control/reuniones/2027-01-12-ronda-riesgos-transcripcion.md"
    j = js("transcripcion", vtt, "--salida", P(rel), "--json")
    t = open(P(rel), encoding="utf-8").read()
    check("2.1", "acta con 3 intervenciones (dos turnos seguidos de la misma persona se unen), 3 hablantes, marcas [hh:mm:ss] y participación agregada",
          j["intervenciones"] == 3 and j["hablantes"] == 3 and "**[00:00:05] Diego Ferreira:**" in t and abs(sum(x["pct_palabras"] for x in j["participacion"].values()) - 100) < 0.5,
          json.dumps(j, ensure_ascii=False)[:300])
    D["vtt"] = vtt


@eslabon("2.2", "acta + instantánea de Jira + BMAD → riesgos.py candidatos (cuatro fuentes)")
def c2_candidatos():
    h1 = D["hechas"][0]["id"]; h2 = [x for x in D["his"] if x["numero"].endswith(".2")][0]["id"]
    escribir("03-control/fuentes/jira-2027-01-14.csv",
             "clave,tipo,titulo,estado,asignado,sprint,puntos,actualizado,url,prioridad,etiquetas,vinculo\n"
             f"PS-11,Bug,Timeout al consultar saldos en {h2},En curso,Lucía Benítez,S3,,2027-01-14,https://jira.example.org/PS-11,Highest,,{h2}\n"
             f"PS-12,Historia,{h1},Listo,Lucía Benítez,S2,5,2027-01-10,https://jira.example.org/PS-12,Medium,,{h1}\n"
             "PS-13,Tarea,=HYPERLINK(\"http://ejemplo.test\") proveedor de SMS sin acuerdo de nivel de servicio para el segundo factor,Por hacer,Diego Ferreira,S3,,2027-01-13,https://jira.example.org/PS-13,Medium,riesgo,\n")
    j = js("riesgos", "--proyecto", G, "candidatos", "--json", "--fecha", "2027-01-15")
    cob = j["cobertura"]; cs = j["candidatos"]
    tr = [c for c in cs if c["fuente"] == "transcripcion"]; tk = {c["origen"].split(" ")[0]: c for c in cs if c["fuente"] == "tracker"}
    check("2.2", f"cobertura de las cuatro fuentes (BMAD {cob['bmad']['candidatos']}, actas {cob['transcripciones']['candidatos']}, tracker {cob['tracker']['candidatos']})",
          set(cob) == {"bmad", "transcripciones", "tracker", "artefactos"} and cob["bmad"]["candidatos"] > 0 and len(tr) == 2 and set(tk) == {"jira:PS-11", "jira:PS-13"},
          {k: v["candidatos"] for k, v in cob.items()})
    check("2.2", "el acta de 2.1 aporta la preocupación (amenaza, Diego Ferreira, [00:00:05]) y la oportunidad; el saludo no",
          tr and tr[0]["tipo"] == "amenaza" and "[00:00:05]" in tr[0]["origen"] and tr[0]["cita"].startswith("Diego Ferreira:")
          and tr[1]["tipo"] == "oportunidad", json.dumps(tr, ensure_ascii=False)[:300])
    check("2.2", f"Jira: el bug PS-11 es candidato a issue y cita la historia {h2} de la fachada; la tarea etiquetada riesgo es candidata a riesgo",
          tk["jira:PS-11"]["clase"] == "issue" and h2 in json.dumps(tk["jira:PS-11"], ensure_ascii=False) and tk["jira:PS-13"]["clase"] == "riesgo", list(tk))
    D.update(cand=j, h_bug=h2, salida_cand=j.get("salida"))


@eslabon("2.3", "candidatos → registro de riesgos e issues (texto y origen copiados del candidato) → deduplicación")
def c2_registro():
    cs = D["cand"]["candidatos"]
    tr = next(c for c in cs if c["fuente"] == "transcripcion" and c["tipo"] == "amenaza")
    jr = next(c for c in cs if c["origen"].startswith("jira:PS-13"))
    bm = next(c for c in cs if c["fuente"] == "bmad" and c["clase"] == "riesgo")
    ids = []
    for c, p, i, monto in ((tr, 4, 4, 30000), (jr, 3, 5, 20000), (bm, 2, 4, 15000)):
        ids.append(reg("agregar", "riesgos", "--campo", f"evento={c['cita']}", "--campo", f"tipo={c['tipo']}", "--campo", f"categoria={c['categoria_sugerida']}",
                       "--campo", f"probabilidad={p}", "--campo", f"impacto={i}", "--campo", f"impacto_monetario={monto}", "--campo", "propietario=Martín Suárez",
                       "--campo", "respuesta=reducir", "--campo", f"notas=candidato {c['id']} · {c['origen']}", "--campo", "fecha_revision=2027-02-15"))
    bug = next(c for c in cs if c["origen"].startswith("jira:PS-11"))
    iss = reg("agregar", "issues", "--campo", "tipo=problema-preocupacion", "--campo", f"titulo={bug['cita'][:120]}", "--campo", "prioridad=alta",
              "--campo", "responsable=Lucía Benítez", "--campo", f"descripcion=origen {bug['origen']}; historia {D['h_bug']}")
    rs = {r["id"]: r for r in reg_js("listar", "riesgos")}
    ve = {i: float(rs[i]["valor_esperado"] or 0) for i in ids}
    check("2.3", f"{', '.join(ids)} con el texto exacto del candidato, su origen (archivo:línea, [hh:mm:ss] o jira:) y valor esperado calculado por registro.py",
          [rs[i]["evento"] for i in ids] == [tr["cita"], jr["cita"], bm["cita"]] and all(ve[i] > 0 for i in ids) and "[00:00:05]" in rs[ids[0]]["notas"], ve)
    j2 = js("riesgos", "--proyecto", G, "candidatos", "--json", "--fecha", "2027-01-16")
    dup = {c["origen"].split(" ")[0]: c.get("posible_duplicado") for c in j2["candidatos"]}
    check("2.3", "una segunda pasada marca como posible duplicado lo ya registrado (Jira PS-13 → el riesgo creado)", dup.get("jira:PS-13") == ids[1], dup.get("jira:PS-13"))
    D.update(riesgos=ids, issue=iss, ve=ve)


@eslabon("2.4", "registro de riesgos + BAC de la cadena 1 → presupuestos de la junta → cambios → sanidad CAM")
def c2_presupuestos():
    riesgo = round(sum(D["ve"].values())); cambio = round(D["bac"] * 0.10); limite = round(D["bac"] * 0.04)
    run("estado", "--proyecto", G, "presupuesto", f"riesgo={riesgo}", f"cambio={cambio}", f"limite_autoridad_cambio={limite}",
        "--por", "Ejecutivo: Laura Méndez", "--fecha", "2027-01-15")
    r0 = D["riesgos"][0]; consumo = round(riesgo * 0.4)
    c1 = reg("agregar", "cambios", "--campo", "titulo=Entorno de pruebas del núcleo", "--campo", f"descripcion=Respuesta al riesgo {r0}",
             "--campo", f"costo={consumo}", "--campo", "cargo=reserva-riesgo", "--campo", "decision=aprobado", "--campo", "estado=aprobado",
             "--campo", "decidido_por=Ejecutivo: Laura Méndez", "--campo", f"notas={r0}")
    sobre = limite + 500
    c2 = reg("agregar", "cambios", "--campo", "titulo=Consulta de movimientos históricos", "--campo", f"descripcion=Amplía {D['his'][2]['id']}",
             "--campo", f"costo={sobre}", "--campo", "cargo=presupuesto-cambio", "--campo", "estado=pendiente-decision")
    rz = run("registro", "--proyecto", G, "actualizar", "cambios", c2, "--campo", "decision=aprobado", "--campo", "estado=aprobado",
             "--campo", "decidido_por=Sofía Ramírez, autoridad de cambio", ok=(1,))
    pend = {f["id"]: f for f in reg_js("listar", "cambios")}[c2]["estado"]
    run("registro", "--proyecto", G, "actualizar", "cambios", c2, "--campo", "decision=aprobado", "--campo", "estado=aprobado",
        "--campo", "decidido_por=Junta: Laura Méndez", "--campo", "fecha_decision=2027-01-16")
    d = san("2027-01-16")
    c3 = [h["mensaje"] for h in hall(d, "CAM-03")]
    pct_r = round(100 * consumo / riesgo); pct_c = round(100 * sobre / cambio)
    check("2.4", f"CAM-03 con los montos derivados: reserva de riesgo {consumo} de {riesgo} ({pct_r} %) y presupuesto de cambio {sobre} de {cambio} ({pct_c} %)",
          any(f"{pct_r} %" in m for m in c3) and any(f"{pct_c} %" in m for m in c3), c3)
    check("2.4", f"registro.py rechaza que la autoridad de cambio apruebe {c2} ({sobre} supera el límite delegado de {limite}): queda pendiente-decision; "
          f"lo aprueba la junta y no hay CAM-04; CAM-02 no aparece porque {c1} cita {r0}",
          "límite" in rz.stdout + rz.stderr and pend == "pendiente-decision" and not hall(d, "CAM-04") and not hall(d, "CAM-02"),
          [(rz.stdout + rz.stderr)[-200:]] + [h["codigo"] + " " + h["mensaje"] for h in d["hallazgos"] if h["codigo"].startswith("CAM")])
    D.update(pres={"riesgo": riesgo, "cambio": cambio, "limite": limite}, cambios=[c1, c2])


@eslabon("2.5", "registros + EVM + avance BMAD → sanidad --informe y tablero de avance (receta de pm-visuales)")
def c2_tablero():
    r = run("sanidad", "--proyecto", G, "--informe", "--corte", "2027-01-16", ok=(0, 1))
    inf = sorted(glob.glob(P("03-control", "reportes", "*-sanidad.md")))
    txt = open(inf[-1], encoding="utf-8").read() if inf else ""
    check("2.5", "sanidad --informe escribe el informe con los hallazgos CAM y TOL del corte", txt and "CAM-03" in txt and "TOL-0" in txt, (inf, r.stdout[-200:]))
    e = json.load(open(P("estado.json"), encoding="utf-8")); g = D["evm"]
    av = leer_csv(P("03-control", "reportes", "avance-bmad.csv"))
    rag = lambda s: {"verde": "verde", "ambar": "ambar", "rojo": "rojo"}.get(s, "na")
    datos = {"proyecto": e["proyecto"], "etapa": e["etapa_actual"]["nombre"], "enfoque_entrega": e["enfoque_entrega"], "idioma": e["idioma"],
             "estado": "borrador", "fecha_corte": "2027-01-16", "periodo_desde": "2027-01-01", "periodo_hasta": "2027-01-16", "proximo_hasta": "2027-01-31",
             "riesgos": reg_js("listar", "riesgos", "--abiertos"), "issues": reg_js("listar", "issues", "--abiertos"), "acciones": reg_js("listar", "acciones"),
             "resumen_registros": reg_js("resumen", "--corte", "2027-01-16"), "umbrales_riesgo": {"alto": 15, "medio": 6},
             "objetivos": [{"clave": "tiempo", "pronostico": f"SPI {g['SPI']:.2f}", "tol_etapa": "", "tol_proyecto": "±3 semanas", "rag": rag(g.get("semaforo_cronograma"))},
                           {"clave": "costo", "pronostico": f"EAC {g['EAC']:.0f}", "tol_etapa": "", "tol_proyecto": "±10 %", "rag": rag(g.get("semaforo_costo"))}],
             "hitos": [], "decisiones_pendientes": [{"id": D["cambios"][1], "texto": "Ratificar el cambio sobre el límite delegado", "fecha_limite": "2027-01-31"}],
             "agil": {"iteraciones": [{"nombre": f["fecha"], "planificado": int(float(f.get("puntos_total") or 0)), "terminado": int(float(f.get("puntos_terminados") or 0)),
                                       "alcance_total": int(float(f.get("puntos_total") or 0)), "terminado_acumulado": int(float(f.get("puntos_terminados") or 0))} for f in av],
                      "ventana_velocidad": 3, "fecha_fija": "", "fecha_pronostico": "", "must_en_riesgo": []},
             "comentario_gestor": "Integración de saldos condicionada al entorno de pruebas del núcleo </script><!-- prueba de escapado", "fuentes": "registros, evm, avance-bmad",
             "fecha_generacion": "2027-01-16", "confirmado_por": ""}
    html = open(TABLERO, encoding="utf-8").read()
    bloque = json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")
    html = re.sub(r'(<script type="application/json" id="datos-tablero">)(.*?)(</script>)', lambda m: m.group(1) + bloque + m.group(3), html, count=1, flags=re.S)
    rel = "03-control/reportes/2027-01-16-tablero-avance.html"; escribir(rel, html)
    run("estado", "--proyecto", G, "artefacto", "tablero-avance", "--ruta", rel, "--estado", "en-revision")
    m = re.search(r'<script type="application/json" id="datos-tablero">(.*?)</script>', open(P(rel), encoding="utf-8").read(), re.S)
    vuelta = json.loads(m.group(1)) if m else {}
    abiertos = {x["id"] for x in reg_js("listar", "riesgos", "--abiertos")}
    check("2.5", f"tablero: los riesgos ({', '.join(sorted(abiertos))}) y el issue {D['issue']} salen de los registros; semáforos del EVM guardado; burn-up desde avance-bmad.csv",
          {x["id"] for x in vuelta.get("riesgos", [])} == abiertos and D["issue"] in {x["id"] for x in vuelta.get("issues", [])}
          and vuelta["agil"]["iteraciones"][-1]["terminado_acumulado"] == D["avance"]["puntos_terminados"]
          and vuelta["objetivos"][1]["rag"] == rag(g.get("semaforo_costo")), json.dumps(vuelta, ensure_ascii=False)[:300])
    check("2.5", "un texto con </script> y <!-- no corta el bloque JSON del tablero", "</script><!--" not in m.group(1) and "prueba de escapado" in vuelta.get("comentario_gestor", ""))


# ================================================================== cadena 3
@eslabon("3.1", "roles de estado.json → maestro de interesados → matriz poder/interés")
def c3_maestro():
    e = json.load(open(P("estado.json"), encoding="utf-8")); ro = e["roles"]
    personas = {ro["ejecutivo"]: ("alto", "alto"), ro["gestor_proyecto"]: ("medio", "alto")}
    for k in ("usuario_senior", "proveedor_senior", "jefes_equipo", "aseguramiento"):
        for n in (ro[k] if isinstance(ro[k], list) else [ro[k]]):
            personas.setdefault(n, ("alto", "alto") if k in ("usuario_senior", "proveedor_senior") else ("bajo", "alto"))
    st = {}
    for nombre, (po, it) in personas.items():
        corr = nombre.lower().replace(" ", ".").replace("í", "i").replace("é", "e").replace("á", "a") + "@example.org"
        st[nombre] = reg("agregar", "stakeholders", "--campo", f"nombre={nombre}", "--campo", f"poder={po}", "--campo", f"interes={it}", "--campo", f"correo={corr}",
                         "--campo", f"rol_proyecto={', '.join(k for k, v in ro.items() if v == nombre or (isinstance(v, list) and nombre in v))}")
    m = js("interesados", "--proyecto", G, "matriz", "--json")
    q = {x["id"]: c for c, xs in m["cuadrantes"].items() for x in xs}
    check("3.1", f"{len(st)} interesados desde los roles de la junta y del equipo; todos ubicados en la matriz (ejecutiva y usuaria sénior: gestionar de cerca)",
          set(q) == set(st.values()) and q[st["Laura Méndez"]] == "gestionar-de-cerca" and q[st["Sofía Ramírez"]] == "gestionar-de-cerca", q)
    D["st"] = st
    j = js("riesgos", "--proyecto", G, "candidatos", "--json", "--fecha", "2027-01-20", "--fuentes", "transcripciones")
    hab = {c["cita"].split(":")[0]: c.get("interesado") for c in j["candidatos"]}
    check("3.1", "riesgos.py vuelve a leer el acta de 2.1 y ahora asocia cada hablante a su id del maestro",
          hab and all(hab[n] == st[n] for n in hab), hab)


@eslabon("3.2", "épicas y requisitos (fachada) + KR (okr.csv) → RACI → integridad (STK-09) y OKR con responsables del maestro")
def c3_raci():
    st = D["st"]; elems = []
    for e in D["epi"]:
        elems += [(e["id"], "epica", st["Sofía Ramírez"], "A"), (e["id"], "epica", st["Lucía Benítez"], "R"), (e["id"], "epica", st["Laura Méndez"], "I")]
    fr = next(r["id"] for r in D["req"] if r["tipo"] == "FR")
    elems += [(fr, "requisito", st["Sofía Ramírez"], "A"), (fr, "requisito", st["Diego Ferreira"], "R"), ("KR-1.1", "kr", st["Laura Méndez"], "A"),
              ("KR-1.1", "kr", st["Sofía Ramírez"], "R"), ("E-9", "epica", st["Andrea Costa"], "C")]
    ids = [reg("agregar", "raci", "--campo", f"elemento={el}", "--campo", f"tipo_elemento={t}", "--campo", f"stakeholder_id={s}", "--campo", f"rol={r}") for el, t, s, r in elems]
    h = js("interesados", "--proyecto", G, "integridad", "--json", ok=(0, 1))
    s09 = [x["mensaje"] for x in h if x["codigo"] == "STK-09"]
    check("3.2", f"integridad: las {len(D['epi'])} épicas, {fr} y KR-1.1 se encuentran en su fuente; E-9 (inexistente en BMAD) = STK-09",
          len(s09) == 1 and "E-9" in s09[0], s09)
    run("registro", "--proyecto", G, "actualizar", "raci", ids[-1], "--campo", f"elemento={D['epi'][-1]['id']}")
    h = js("interesados", "--proyecto", G, "integridad", "--json", ok=(0, 1))
    check("3.2", "corregido el elemento, sin STK-09 ni STK-02 (un A por elemento)", not [x for x in h if x["codigo"] in ("STK-09", "STK-02", "STK-03")], h)
    po = P("00-direccion", "okr.csv"); filas = leer_csv(po); cab = list(filas[0].keys())
    inv = {v: k for k, v in st.items()}
    for f in filas:
        if f["responsable"] in st: f["responsable"] = st[f["responsable"]]
    escribir_csv(po, cab, filas)
    o = js("okr", po, "--corte", "2027-01-20", "--json")
    check("3.2", "okr.py: los responsables son ids del maestro (ST-…) y no hay avisos de responsable fuera del maestro",
          all(f["responsable"].startswith("ST-") for f in filas if f["responsable"]) and not any("maestro" in a for a in o.get("avisos", [])), o.get("avisos"))
    D["raci_e1"] = {"A": st["Sofía Ramírez"], "R": st["Lucía Benítez"]}; D["inv_st"] = inv


@eslabon("3.3", "RACI de E-1 + informe OKR → interesados.py plan-envio → envios.py (aprobar, simulación, .eml) → envios.csv")
def c3_envios():
    run("okr", P("00-direccion", "okr.csv"), "--corte", "2027-01-20", "--markdown", P("03-control", "reportes", "2027-01-20-okr.md"))
    for s in D["raci_e1"].values():
        reg("agregar", "preferencias", "--campo", f"stakeholder_id={s}", "--campo", "dimension=canal", "--campo", "valor=correo", "--campo", "procedencia=declarado",
            "--campo", "estado=confirmada", "--campo", "confirmado_por=Gestor: Martín Suárez", "--campo", "vigencia_hasta=2099-12-31",
            "--campo", "evidencia=\"Prefiero que me lleguen los avances por correo\" (ronda 2027-01-12)")
    e1 = D["epi"][0]["id"]
    run("interesados", "--proyecto", G, "plan-envio", "--tema", "Avance OKR enero", "--audiencia", f"raci:{e1}:AR", "--base", P("03-control", "reportes", "2027-01-20-okr.md"),
        "--proposito", "okr", "--fecha", "2027-01-20")
    c = P("03-control", "comunicaciones", "2027-01-20-avance-okr-enero")
    msjs = sorted(glob.glob(os.path.join(c, "mensaje-*.md")))
    texto = "".join(open(x, encoding="utf-8").read() for x in msjs)
    check("3.3", f"plan-envio: un borrador por destinatario de la RACI de {e1} (A y R: {', '.join(D['raci_e1'].values())}), por correo, con el informe OKR como base",
          len(msjs) == 2 and all(f"-correo-{s.lower()}" in " ".join(msjs) for s in D["raci_e1"].values()) and "KR-1.1" in texto, msjs)
    for x in msjs:
        t = open(x, encoding="utf-8").read().replace("[redactar el mensaje]", "KR-1.1 en 0,40 con confianza 7; sin decisiones pendientes.")
        open(x, "w", encoding="utf-8").write(t)
    run("envios", "--proyecto", G, "aprobar", c, "--por", "Gestor: Martín Suárez")
    sim = run("envios", "--proyecto", G, "enviar", c, "--modo", "eml", "--fecha", "2027-01-20").stdout
    check("3.3", "enviar sin --confirmar = simulación; no se registra nada", "SIMULACIÓN" in sim and not os.path.exists(P("03-control", "registros", "envios.csv")), sim[-300:])
    run("envios", "--proyecto", G, "enviar", c, "--modo", "eml", "--confirmar", "--fecha", "2027-01-20")
    emls = sorted(glob.glob(os.path.join(c, "eml", "*.eml")))
    for x in msjs:
        run("envios", "--proyecto", G, "registrar", c, "--mensaje", os.path.basename(x), "--modo", "eml", "--referencia", "enviado desde el cliente de correo",
            "--estado", "enviado", "--fecha", "2027-01-20")
    en = leer_csv(P("03-control", "registros", "envios.csv"))
    dest = {f["stakeholder_id"] for f in en if f["estado"] == "enviado"}
    check("3.3", f"{len(emls)} archivos .eml (sin red); envios.csv registra EN-### enviados a exactamente la A y la R de la RACI, con quien aprobó",
          len(emls) == 2 and dest == set(D["raci_e1"].values()) and all(f["confirmado_por"] == "Gestor: Martín Suárez" for f in en if f["estado"] == "enviado")
          and all(re.match(r"EN-\d{3}$", f["id"]) for f in en), [(f["id"], f["stakeholder_id"], f["estado"]) for f in en])
    D["envios"] = en


@eslabon("3.4", "envíos + RACI + OKR → vínculos del interesado y cadencia de contacto (STK-12) → sanidad STK")
def c3_stk():
    a = D["raci_e1"]["A"]
    v = js("interesados", "--proyecto", G, "vinculos", a, "--json")
    tv = json.dumps(v, ensure_ascii=False)
    check("3.4", f"vinculos {a}: RACI (épicas, requisito, KR) y los envíos EN-### registrados", D["epi"][0]["id"] in tv and "KR-1.1" in tv
          and any(f["id"] in tv for f in D["envios"] if f["stakeholder_id"] == a), tv[:300])
    s12 = lambda corte: [x["mensaje"] for x in js("interesados", "--proyecto", G, "integridad", "--corte", corte, "--json", ok=(0, 1)) if x["codigo"] == "STK-12"]
    lm, r_ = D["st"]["Laura Méndez"], D["raci_e1"]["R"]
    antes, despues = s12("2027-01-29"), s12("2027-01-31")
    check("3.4", f"STK-12 calculado desde envios.csv: al 2027-01-29 nadie supera 1,5 × su frecuencia; al 2027-01-31, {a} (último envío el 2027-01-20) y {lm} (sin contacto) sí; {r_} (quincenal) no",
          not antes and any(m.startswith(a) and "2027-01-20" in m for m in despues) and any(m.startswith(lm) and "sin contacto" in m for m in despues)
          and not any(m.startswith(r_) for m in despues), (antes, despues))
    d = san("2027-01-23")
    check("3.4", "sanidad: sin ERROR en la familia STK (ni referencias rotas entre maestro, RACI, preferencias, envíos y OKR)",
          not [h for h in d["hallazgos"] if h["codigo"].startswith("STK") and h["severidad"] == "ERROR"] and "STK-08" not in cods(d),
          [h["codigo"] + " " + h["mensaje"][:80] for h in d["hallazgos"] if h["codigo"].startswith("STK")])


# ================================================================== cadena 4
def completar_wardley(ruta, evidencia):
    """Lo que hace la persona con la semilla: posiciones, etapa de evolución y evidencia de cada componente."""
    w = json.load(open(ruta, encoding="utf-8"))
    for a in w["anclas"]: a.update(visibilidad=0.95, evolucion=0.5)
    n = len(w["componentes"])
    for i, c in enumerate(w["componentes"]):
        c.update(visibilidad=round(0.85 - 0.6 * i / max(n - 1, 1), 2), evolucion=round(0.2 + 0.6 * i / max(n - 1, 1), 2), evidencia=evidencia)
        c["etapa"] = "genesis" if c["evolucion"] < 0.25 else "a-medida" if c["evolucion"] < 0.5 else "producto" if c["evolucion"] < 0.75 else "commodity"
    if "[por confirmar" in w.get("pregunta_estrategica", ""): w["pregunta_estrategica"] = "¿Qué construimos y qué compramos?"
    json.dump(w, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return w


@eslabon("4.1", "BMAD (capacidades y recorridos) → mapas.py semilla de Wardley y de recorrido; WBS → semilla desde artefactos")
def c4_semillas():
    ids = {r["id"] for r in D["req"]}
    run("mapas", "--proyecto", G, "wardley", "semilla", "--slug", "portal", "--titulo", "Portal", "--pregunta", "¿Qué construimos y qué compramos?",
        "--desde", "bmad", "--fecha", "2027-01-20", "--json")
    w = json.load(open(P("02-planificacion", "mapas", "wardley-portal.json"), encoding="utf-8"))
    refs = {x for c in w["componentes"] for x in c["refs"]} | {x for a in w["anclas"] for x in a["refs"]}
    check("4.1", f"Wardley desde BMAD: {len(w['anclas'])} anclas (UJ) y {len(w['componentes'])} componentes; todas sus referencias ({len(refs)}) existen en la fachada",
          w["anclas"] and w["componentes"] and refs and refs <= ids, sorted(refs - ids))
    rec = js("bmad", "--proyecto", G, "recorridos", "--id", "UJ-2", "--json")[0]
    run("mapas", "--proyecto", G, "recorrido", "semilla", "--uj", "UJ-2", "--backstage", "UJ-3", "--fecha", "2027-01-20", "--json")
    r = json.load(open(P("02-planificacion", "mapas", "recorrido-uj-2.json"), encoding="utf-8"))
    check("4.1", f"recorrido UJ-2: KPI {', '.join(rec['kpi'])} y FR {', '.join(rec['frs'])} tomados de bmad.py recorridos; backstage UJ-3 por alinear",
          set(rec["kpi"]) <= set(r.get("kpi", [])) and set(rec["frs"]) <= set(r.get("refs", [])) and r.get("pendiente_alinear", {}).get("backstage"), {k: r.get(k) for k in ("kpi", "refs")})
    run("mapas", "--proyecto", G, "wardley", "semilla", "--slug", "entregables", "--desde", "artefactos", "--anclas", "Socio", "--fecha", "2027-01-20", "--json")
    we = json.load(open(P("02-planificacion", "mapas", "wardley-entregables.json"), encoding="utf-8"))
    prods = [n["nombre"] for n in D["wbs"]["nodos"] if n["tipo"] == "producto"]
    nombres = [c["nombre"] for c in we["componentes"]]
    check("4.1", f"Wardley desde artefactos: los componentes son los {len(prods)} productos de la WBS de la cadena 1 (nombre largo recortado con «…»)",
          len(nombres) == len(prods) and all(p == n or (n.endswith("…") and p.startswith(n[:-1])) for p, n in zip(prods, nombres)), (nombres, prods))
    completar_wardley(os.path.join(P("02-planificacion", "mapas"), "wardley-entregables.json"), "plan de proyecto (WBS por productos)")
    D.update(w=w, r=r)


@eslabon("4.2", "mapas completados por la persona → familia MAP de sanidad → vínculos a riesgos, issues y decisiones")
def c4_vinculos():
    mp = P("02-planificacion", "mapas")
    w = completar_wardley(os.path.join(mp, "wardley-portal.json"), "arquitectura de BMAD (ARCHITECTURE-SPINE.md)")
    com = w["componentes"][-1]; com.update(evolucion=0.9, etapa="commodity", decision="construir")
    ine = w["componentes"][1]; ine["inercia"] = True
    json.dump(w, open(os.path.join(mp, "wardley-portal.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    r = json.load(open(os.path.join(mp, "recorrido-uj-2.json"), encoding="utf-8"))
    pasos = [p for e in r["etapas"] for p in e["pasos"]]
    for i, p in enumerate(pasos): p.update(emocion=[1, 0, -1][i % 3], fuente_emocion="entrevistas de la ronda del 2027-01-12")
    dolor = pasos[3]; dolor.update(emocion=-2, dolor="La consulta de saldos tarda y corta la sesión", tipo_causa="rendimiento")
    r.pop("pendiente_alinear", None)
    json.dump(r, open(os.path.join(mp, "recorrido-uj-2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    run("mapas", "--proyecto", G, "vincular", "portal", com["id"], "--refs", "D-999")
    d = san("2027-01-20"); mc = cods(d, "AVISO")
    check("4.2", "MAP-01 (commodity marcado construir), MAP-02 (inercia sin riesgo), MAP-03 (dolor sin tratamiento) y MAP-05 (D-999 inexistente) como AVISO",
          {"MAP-01", "MAP-02", "MAP-03", "MAP-05"} <= mc and not any(c.startswith("MAP") for c in cods(d, "ERROR")), sorted(c for c in mc if c.startswith("MAP")))
    dec = reg("agregar", "decisiones", "--campo", f"decision=Comprar {com['nombre']} (servicio estándar) en lugar de construirlo", "--campo", "decidido_por=Junta: Laura Méndez",
              "--campo", "nivel=junta", "--campo", "fecha=2027-01-20")
    run("mapas", "--proyecto", G, "vincular", "portal", com["id"], "--refs", "D-999", "--quitar")
    run("mapas", "--proyecto", G, "vincular", "portal", com["id"], "--refs", dec)
    run("mapas", "--proyecto", G, "vincular", "portal", ine["id"], "--refs", D["riesgos"][0])
    run("mapas", "--proyecto", G, "vincular", "uj-2", dolor["id"], "--refs", D["issue"])
    d = san("2027-01-20")
    w2 = json.load(open(os.path.join(mp, "wardley-portal.json"), encoding="utf-8"))
    check("4.2", f"tras vincular {dec} (decisión de la junta), {D['riesgos'][0]} (riesgo de la cadena 2) e {D['issue']} (bug de Jira), sin avisos MAP",
          not {c for c in cods(d) if c.startswith("MAP")} and dec in next(c for c in w2["componentes"] if c["id"] == com["id"])["refs"],
          sorted(h["codigo"] + " " + h["mensaje"][:80] for h in d["hallazgos"] if h["codigo"].startswith("MAP")))
    rw = run("mapas", "--proyecto", G, "wardley", "render", "portal", "--png", "no")
    rr = run("mapas", "--proyecto", G, "recorrido", "render", "uj-2", "--png", "no")
    vis = P("02-planificacion", "visuales")
    h = open(os.path.join(vis, "recorrido-uj-2.html"), encoding="utf-8").read() if os.path.exists(os.path.join(vis, "recorrido-uj-2.html")) else ""
    check("4.2", "render: wardley-portal.md/.owm y recorrido-uj-2.md/.html con el dolor y el issue vinculado",
          os.path.exists(os.path.join(vis, "wardley-portal.md")) and os.path.exists(os.path.join(vis, "wardley-portal.owm")) and "corta la sesión" in h and D["issue"] in h,
          (rw.stdout[-200:], rr.stdout[-200:]))
    D.update(comprar=com, construir=w2["componentes"][0], decision=dec)


@eslabon("4.3", "mapa de Wardley + trazabilidad WBS + presupuestos → opciones del business case → inversion.py")
def c4_inversion():
    c = D["construir"]; frs = [x for x in c["refs"] if x.startswith("FR-")]
    paquetes = sorted({p for f in frs for p in D["req_idx"][f]["paquetes_wbs"]})
    costo = {n["codigo"]: n["costo_tot"] for n in D["wbs"]["nodos"]}
    inv_construir = sum(costo[p] for p in paquetes)
    comp = D["comprar"]["nombre"]
    o1n, o2n = f"1 · Construir {c['nombre']}", f"2 · Construir y comprar {comp}"
    ben = ["", round(inv_construir * 0.5), round(inv_construir * 0.6), round(inv_construir * 0.6)]
    lic = D["pres"]["limite"]
    filas = [["opcion", "concepto", "tipo", "0", "1", "2", "3"], ["0 · No hacer nada", "Sin cambios", "costo", 0, 0, 0, 0],
             [o1n, f"Inversión (paquetes {' '.join(paquetes)})", "inversion", -round(inv_construir), "", "", ""], [o1n, "Consultas desviadas (B-01)", "beneficio"] + ben,
             [o2n, "Inversión", "inversion", -round(inv_construir * 0.8), "", "", ""], [o2n, "Licencia del servicio", "costo", "", -lic, -lic, -lic],
             [o2n, "Consultas desviadas (B-01)", "beneficio"] + ben]
    with open(P("00-direccion", "opciones-inversion.csv"), "w", encoding="utf-8", newline="") as fh: csv.writer(fh).writerows(filas)
    j = js("inversion", P("00-direccion", "opciones-inversion.csv"), "--tasa", "0.10", "--json")
    o1 = j["opciones"][o1n]
    flujos = [-round(inv_construir), round(inv_construir * 0.5), round(inv_construir * 0.6), round(inv_construir * 0.6)]
    van = sum(f / 1.1 ** t for t, f in enumerate(flujos))
    check("4.3", f"opción 1: inversión = costo consolidado en la WBS del producto {', '.join(paquetes)}, que cita {', '.join(frs)} ({inv_construir:.0f}); VAN {o1['van']:.2f} = cálculo independiente",
          paquetes and abs(o1["flujos"][0] + inv_construir) < 1 and abs(o1["van"] - van) < 0.01, (paquetes, o1["flujos"], van))
    o2 = j["opciones"][o2n]
    check("4.3", "VAN incremental frente a la base y TIR coherente (VAN(TIR) ≈ 0)", abs(o1["van_incremental"] - o1["van"]) < 0.01 and o1["tir"]
          and abs(sum(f / (1 + o1["tir"]) ** t for t, f in enumerate(o1["flujos"]))) < 1 and "van" in o2, (o1["van_incremental"], o1["tir"]))
    mejor = max(j["opciones"], key=lambda k: j["opciones"][k]["van"])
    art("business-case-opciones", "00-direccion/business-case-opciones.md",
        "# Opciones del business case\n" + "\n".join(f"- {k}: VAN {v['van']:.0f}" for k, v in j["opciones"].items()) + f"\nRecomendada: {mejor} (decisión {D['decision']}).")
    D["inversion"] = j


# ================================================================== cadena 5
@eslabon("5.1", "registros de las cadenas 1–4 → exportar.py xlsx (una hoja por registro) y docx del informe de sanidad")
def c5_exportar():
    try:
        import openpyxl
    except ImportError:
        print("  (omitido: falta openpyxl)"); return
    sal = P("exportados", "2027-01-20-registros.xlsx")
    run("exportar", "xlsx", "--proyecto", G, "--salida", sal)
    wb = openpyxl.load_workbook(sal)
    regs = sorted(glob.glob(P("03-control", "registros", "*.csv")))
    malas = []
    for r in regs:
        hoja = os.path.splitext(os.path.basename(r))[0][:31]; filas = list(csv.reader(open(r, encoding="utf-8")))
        ws = wb[hoja] if hoja in wb.sheetnames else None
        if ws is None or ws.max_row != len(filas) or [c.value or "" for c in ws[1]] != filas[0]:
            malas.append(hoja); continue
        if [str(ws.cell(row=i + 1, column=1).value or "") for i in range(len(filas))] != [f[0] for f in filas]: malas.append(hoja + " (ids)")
    check("5.1", f"xlsx: {len(regs)} hojas con las mismas filas, cabeceras e ids que los CSV (riesgos {', '.join(D['riesgos'])}, envíos, RACI…)",
          not malas and set(wb.sheetnames) == {os.path.splitext(os.path.basename(r))[0][:31] for r in regs}, malas)
    ws = wb["riesgos"]; cel = [c for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=HYPERLINK")]
    check("5.1", "el texto de Jira que empieza con '=' llegó al registro y se exporta como texto, no como fórmula", cel and all(c.data_type == "s" for c in cel))
    try:
        import docx
    except ImportError:
        print("  (docx omitido: falta python-docx)"); return
    inf = sorted(glob.glob(P("03-control", "reportes", "*-sanidad.md")))[-1]
    run("exportar", "docx", "--entrada", inf, "--salida", P("exportados", "sanidad.docx"))
    doc = docx.Document(P("exportados", "sanidad.docx"))
    txt = "\n".join([p.text for p in doc.paragraphs] + [c.text for tb in doc.tables for row in tb.rows for c in row.cells])
    check("5.1", "docx del informe de sanidad con sus hallazgos CAM", "CAM-03" in txt)
    D["xlsx"] = sal


@eslabon("5.2", "artefactos, mapas, OKR, opciones y xlsx → paquete.py de la puerta autorizar-etapa → contenido del ZIP")
def c5_paquete():
    extras = [P("02-planificacion", "visuales", "wardley-portal.md"), P("02-planificacion", "visuales", "recorrido-uj-2.md"), P("00-direccion", "okr.csv"),
              P("00-direccion", "opciones-inversion.csv")] + ([D["xlsx"]] if D.get("xlsx") else [])
    lst = run("paquete", "--proyecto", P(), "listar", "puerta", "autorizar-etapa").stdout
    sal = os.path.join(D["tmp"], "paquete-autorizar-etapa.zip")
    run("paquete", "--proyecto", P(), "puerta", "autorizar-etapa", "--salida", sal, "--extra", *extras)
    zs = sorted(glob.glob(os.path.join(D["tmp"], "paquete-autorizar-etapa*.zip")))
    z = zipfile.ZipFile(zs[-1]); man = z.read("MANIFIESTO.md").decode("utf-8")
    nombres = z.namelist()
    faltan = [os.path.basename(x) for x in extras if os.path.join("extra", os.path.basename(x)) not in nombres]
    distintos = [n for n in nombres if n != "MANIFIESTO.md" and hashlib.sha256(z.read(n)).hexdigest() not in
                 {sha(os.path.join(dp, f)) for dp, _, fs in os.walk(P()) for f in fs if f == os.path.basename(n)}]
    check("5.2", f"ZIP con MANIFIESTO y {len(nombres) - 1} archivos idénticos a su origen (sha256), incluidos los {len(extras)} extras",
          not faltan and not distintos and "plan-etapa-2" in man and all(os.path.basename(x) in man for x in extras), (faltan, distintos))
    borr = "-BORRADOR" in os.path.basename(zs[-1])
    check("5.2", "el estado del paquete (completo o BORRADOR) coincide con lo que informa 'paquete.py listar'", borr == ("BORRADOR" in lst.split("ESTADO DEL PAQUETE")[1].splitlines()[0]),
          (zs[-1], lst[:300]))


@eslabon("5.3", "integridad final: BMAD sin escrituras de pm-method y sanidad sin ERROR")
def c5_final():
    ahora = huella_bmad()
    cambiados = [k for k in set(ahora) | set(D["huella"]) if ahora.get(k) != D["huella"].get(k)]
    check("5.3", f"huella sha256 de {len(ahora)} archivos de _bmad/ y _bmad-output/ idéntica a la inicial (solo cambió sprint-status.yaml, que simula al equipo BMAD)",
          not cambiados, cambiados)
    d = san("2027-01-23")
    check("5.3", "sanidad del proyecto integrado: 0 ERROR", not cods(d, "ERROR"), [h["codigo"] + " " + h["mensaje"][:100] for h in d["hallazgos"] if h["severidad"] == "ERROR"])


# ================================================================== cadena 6
@eslabon("6.1", "recorridos E2E (guias_e2e, en paralelo) → imágenes y evidencia")
def c6_e2e(dir_e2e, correr):
    if correr:
        procs = [(g, subprocess.Popen([sys.executable, SCR["e2e"], "--guias", g, "--salida", dir_e2e], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
                 for g in "12345"]
        malos = []
        for g, p in procs:
            out = p.communicate()[0]
            if p.returncode != 0: malos.append(f"E2E-{g}: {out[-400:]}")
        check("6.1", "las cinco guías E2E corren con los scripts reales (5/5)", not malos, " | ".join(malos))
    pngs = sorted(glob.glob(os.path.join(dir_e2e, "*.png")))
    sal = sorted(glob.glob(os.path.join(dir_e2e, "salida-g*.md")))
    check("6.1", f"evidencia de los recorridos: {len(sal)} salidas y {len(pngs)} imágenes", len(sal) == 5 and pngs, (sal, len(pngs)))
    D["pngs"] = {os.path.basename(p): p for p in pngs}


@eslabon("6.2", "imágenes de los recorridos → diapositivas del webinar → generar.py --validar y generación real")
def c6_webinar(dir_out):
    r = run("generar", "--todos", "--validar", cwd=RAIZ, ok=None)
    check("6.2", "generar.py --todos --validar (docs/webinar) sin errores", r.returncode == 0, " | ".join(l.strip() for l in r.stdout.splitlines() if "ERROR" in l) or r.stdout[-500:])
    casos = sorted(glob.glob(os.path.join(RAIZ, "docs", "webinar", "E2E-*", "diapositivas.json")))
    usadas, errores = {}, []
    for c in casos:
        nombre = os.path.basename(os.path.dirname(c)); dest = os.path.join(dir_out, nombre); os.makedirs(dest, exist_ok=True)
        datos = json.load(open(c, encoding="utf-8"))
        for cl in datos["clases"]:
            for d in cl["diapositivas"]:
                b = os.path.basename(d.get("imagen") or "")
                if b in D["pngs"]: d["imagen"] = D["pngs"][b]; usadas.setdefault(nombre, []).append(b)
        json.dump(datos, open(os.path.join(dest, "diapositivas.json"), "w", encoding="utf-8"), ensure_ascii=False)
        rv = run("generar", "--caso", dest, "--validar", cwd=RAIZ, ok=None)
        if rv.returncode != 0: errores.append(f"{nombre}: " + " | ".join(l.strip() for l in rv.stdout.splitlines() if "ERROR" in l))
    n = sum(len(v) for v in usadas.values())
    check("6.2", f"los {len(casos)} mazos validan con las imágenes recién generadas por los recorridos ({n} diapositivas las usan)", not errores and n > 0, errores)
    node = shutil.which("node")
    if not node or subprocess.run(["node", "-e", "require('pptxgenjs')"], capture_output=True, env=_entorno_node()).returncode != 0:
        print("  (generación real omitida: falta Node.js o pptxgenjs)"); return
    caso = max(usadas, key=lambda k: len(usadas[k]))
    dest = os.path.join(dir_out, caso)
    rg = run("generar", "--caso", dest, "--salida", os.path.join(dest, "salida"), cwd=RAIZ, ok=None)
    pptx = glob.glob(os.path.join(dest, "salida", "*.pptx")); html = glob.glob(os.path.join(dest, "salida", "*.html"))
    img = D["pngs"][usadas[caso][0]]
    import base64
    b64 = base64.b64encode(open(img, "rb").read()).decode()[:4000]
    medios = {hashlib.sha256(zipfile.ZipFile(pptx[0]).read(n)).hexdigest() for n in zipfile.ZipFile(pptx[0]).namelist() if n.startswith("ppt/media/")} if pptx else set()
    check("6.2", f"{caso}: HTML y PPTX reales; la imagen {usadas[caso][0]} de la corrida va embebida en ambos (base64 en el HTML, mismo sha256 en ppt/media)",
          rg.returncode == 0 and html and b64 in open(html[0], encoding="utf-8").read() and sha(img) in medios, rg.stdout[-400:])


def _entorno_node():
    env = dict(os.environ)
    if shutil.which("npm"):
        try:
            g = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=30).stdout.strip()
            if g: env["NODE_PATH"] = os.pathsep.join([p for p in env.get("NODE_PATH", "").split(os.pathsep) if p] + [g])
        except (OSError, subprocess.SubprocessError):
            pass
    return env


def main():
    ap = argparse.ArgumentParser(description="Suite de integración cruzada de pm-method: seis cadenas de fuentes y skills sobre un mismo proyecto temporal.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n", 3)[3])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sin-e2e", action="store_true", help="omitir la cadena 6 (recorridos E2E y webinar)")
    g.add_argument("--e2e", metavar="DIR", help="usar las salidas ya generadas por guias_e2e/correr.py en DIR")
    ap.add_argument("--conservar", action="store_true", help="no borrar la carpeta temporal (para inspeccionar el proyecto)")
    ap.add_argument("--json", metavar="ARCHIVO", help="escribir el resultado de cada comprobación en ARCHIVO (JSON)")
    a = ap.parse_args()
    try:
        import yaml  # noqa: F401  (lo necesita bmad.py)
    except ImportError:
        sys.exit("Falta PyYAML (pip install pyyaml): bmad.py lo necesita para leer BMAD")
    t0 = time.time()
    D["tmp"] = tempfile.mkdtemp(prefix="pm-method-integracion-")
    D["repo"] = os.path.join(D["tmp"], "portal-socios")
    shutil.copytree(FIXTURE, D["repo"])
    try:
        print("Cadena 1 · BMAD → especificación → WBS/CPM → EVM → OKR → sanidad → puertas")
        for f in (c1_especificacion, c1_wbs, c1_trazabilidad, c1_cpm, c1_evm, c1_okr, c1_puertas): f()
        print("\nCadena 2 · transcripción, Jira y BMAD → riesgos → presupuestos (CAM) → sanidad → tablero")
        for f in (c2_transcripcion, c2_candidatos, c2_registro, c2_presupuestos, c2_tablero): f()
        print("\nCadena 3 · interesados ↔ RACI ↔ OKR ↔ envíos → STK")
        for f in (c3_maestro, c3_raci, c3_envios, c3_stk): f()
        print("\nCadena 4 · mapas desde BMAD y artefactos → vínculos → MAP → inversión")
        for f in (c4_semillas, c4_vinculos, c4_inversion): f()
        print("\nCadena 5 · exportar y paquete de puerta")
        for f in (c5_exportar, c5_paquete, c5_final): f()
        if not a.sin_e2e:
            print("\nCadena 6 · recorridos E2E → webinar")
            dir_e2e = a.e2e or os.path.join(D["tmp"], "e2e")
            c6_e2e(dir_e2e, correr=not a.e2e)
            c6_webinar(os.path.join(D["tmp"], "webinar"))
    finally:
        if a.conservar: print(f"\nConservado en {D['tmp']}")
        else: shutil.rmtree(D["tmp"], ignore_errors=True)
    dur = time.time() - t0
    por = {}
    for x in RES["eslabones"]: por.setdefault(x["eslabon"], []).append(x["ok"])
    print(f"\nResultado: {RES['ok']} OK · {RES['fallo']} FALLO · {len(por)} eslabones · {dur:.0f} s")
    if a.json:
        json.dump({"ok": RES["ok"], "fallo": RES["fallo"], "segundos": round(dur), "python": sys.version.split()[0], "comprobaciones": RES["eslabones"]},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sys.exit(1 if RES["fallo"] else 0)


if __name__ == "__main__":
    main()
