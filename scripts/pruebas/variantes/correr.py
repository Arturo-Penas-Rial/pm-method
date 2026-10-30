#!/usr/bin/env python3
"""Suite de variantes de pm-method: entorno, caminos alternos, fallas de integración, contratos, Hermes y opcionales (docs/PRUEBAS.md §2.5).

Uso:  python3 scripts/pruebas/variantes/correr.py [--nivel todo] [--repetir 2] [--salida DIR] [--json [RUTA]]
                                                 [--celdas M01,D1] [--paralelo 4] [--permitir-omision CLAVE …] [--conservar]
Niveles (--nivel, uno o varios separados por comas; «todo» = todos):
  robustez       probar_paquete.py --casos RB,Y con 3.13 y 3.9 (datos dañados, --help y entradas faltantes) y migración
                 desde 2.6.1 y desde estado.json v1 (migracion.py)
  caminos        probar_paquete.py --casos CP (puertas rechazadas/pendientes, excepción, cierre prematuro) y el ciclo
                 paramétrico con cierre normal y prematuro (ciclo.py)
  matriz         ciclo.py en las celdas pairwise de matriz.py (Python 3.9/3.13 × dependencias completas/mínimas × BMAD ×
                 idioma × salida utf-8/cp1252 × ruta simple/con espacios) más las celdas degradadas D1 y D2, cada una con
                 su manifiesto de omisiones esperadas
  integraciones  SMTP y webhooks con fallas, envios.py registrar (eml y mcp), tracker dañado (integraciones.py)
  contratos      documentación ↔ CLI, esquema ↔ consumidores y versiones del CI (contratos.py)
  hermes         instalar_hermes.py en un destino temporal y los scripts desde la copia (hermes.py)
  e2e            guias_e2e/correr.py --comparar docs/guias/evidencia con 3.13 y 3.9 (pm-kb, si está, solo con 3.13)
  opcionales     pm-kb con modelos simulados (vectores, re-ranqueo y respuesta), su interacción con registro.py,
                 propuestas, interesados, circulación restringida, BMAD y el MCP (stdio y HTTP), el portal con pm-method
                 (instantáneas de las puertas, «actualizar ahora» en solo lectura, propuestas, enlaces compartidos,
                 inglés, `pm-kb enlaces`; portal.py), sus pruebas propias (probar_kb.py y pantallas.py) y las skills
                 externas de diagramas en un contenedor sin red, con sus salidas en el portal (opcionales.py); sin pm-kb,
                 Playwright, Docker o las copias de las skills (PM_SKILLS_EXTERNAS), esas partes se omiten con las claves
                 pm-kb, pm-kb-pantallas, docker y skills-externas (informadas)
Salida en DIR (por defecto, una carpeta nueva del directorio temporal): INFORME.md, resultado.json y, por corrida,
celdas/<unidad>/comandos.log. Los proyectos de trabajo se borran al terminar (--conservar los deja).
Código 1 si hay un FALLO, una traza de Python, una omisión fuera del manifiesto o, con --repetir, resultados distintos
entre corridas (determinismo). Intérpretes: el que corre este archivo (3.13) y PM_PYTHON39 (por defecto /tmp/py39/bin/python).
--permitir-omision declara omisiones esperadas del entorno (p. ej. python-3.9 o migracion-zip-261 en Docker).
"""
import argparse, concurrent.futures as cf, json, os, re, shutil, subprocess, sys, tempfile, time
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from comun import RAIZ, Registro, interpretes, version_de   # noqa: E402

NIVELES = ("robustez", "caminos", "matriz", "integraciones", "contratos", "hermes", "e2e", "opcionales")


def probar_paquete(nivel, unidad, py, casos, logs):
    """probar_paquete.py --casos … --json como una unidad de la suite."""
    reg = Registro(nivel, unidad, logs)
    js = os.path.join(logs, "probar_paquete.json")
    t0 = time.time()
    try:
        r = subprocess.run([py, os.path.join(RAIZ, "scripts", "probar_paquete.py"), "--casos", casos, "--sin-integracion", "--json", js],
                           capture_output=True, text=True, timeout=1800, cwd=RAIZ)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, err, rc = "", "sin respuesta en 1800 s", -9
    with open(os.path.join(logs, "comandos.log"), "w", encoding="utf-8") as fh: fh.write(f"$ probar_paquete.py --casos {casos} ({py}) · código {rc} · {time.time() - t0:.0f} s\n{out}\n{err}\n")
    try: d = json.load(open(js, encoding="utf-8"))
    except (OSError, ValueError): d = None
    if d is None:
        reg.check(f"probar_paquete.py --casos {casos}: terminó y escribió --json", False, (out + err)[-500:]); return reg
    for c in sorted(d["casos"]):
        x = d["casos"][c]
        fallos = [f for f in d["fallos"] if f["caso"] == c]
        reg.check(f"probar_paquete {c}: {x['ok']} OK · {x['fallo']} FALLO", x["fallo"] == 0 and x["ok"] > 0, "; ".join(f["comprobacion"][:120] for f in fallos))
    for o in d["omitidas"]: reg.omitir(f"pp-{o['caso']}:{o['motivo'][:60]}", o["motivo"])
    if "Traceback (most recent call last)" in out + err: reg.trazas.append({"paso": f"probar_paquete {casos}", "comando": "probar_paquete.py", "cola": (out + err)[-600:]})
    if rc not in (0, 1): reg.check(f"probar_paquete.py código {rc}", False, err[-300:])
    return reg


def e2e(unidad, py, logs, trabajo, con_kb=True):
    """Guías E2E comparadas con la evidencia. pm-kb (si está) solo en una unidad (`con_kb`): las guías indexan con nombres
    fijos (portal-socios, producto-bmad) y dos unidades en paralelo se quitarían el índice una a la otra."""
    reg = Registro("e2e", unidad, logs)
    sal = os.path.join(trabajo, unidad)
    env = dict(os.environ) if con_kb else dict(os.environ, PMKB_LANZADOR=os.path.join(trabajo, "sin-pm-kb"))
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "pruebas", "guias_e2e", "correr.py"), "--salida", sal, "--python", py,
                        "--comparar", os.path.join(RAIZ, "docs", "guias", "evidencia")], capture_output=True, text=True, timeout=3600, cwd=RAIZ, env=env)
    with open(os.path.join(logs, "comandos.log"), "w", encoding="utf-8") as fh: fh.write(f"$ guias_e2e/correr.py --python {py} --comparar · código {r.returncode} · {time.time() - t0:.0f} s\n{r.stdout}\n{r.stderr}\n")
    for l in r.stdout.splitlines():
        m = re.match(r"(OK   |FALLO) (guía E2E-\d|evidencia E2E-\d)", l)
        if m: reg.check(re.sub(r" · \d+ s$", "", l[6:].split(" · /")[0])[:160], m.group(1) == "OK   ", l)   # sin la duración: el nombre es estable entre corridas
        if l.strip().startswith("OMITIDO pm-kb"): reg.omitir("pm-kb", "pm-kb no instalado" + ("" if con_kb else " o reservado a la unidad e2e-3.13")
                                                             + ": pasos 16 (E2E-1) y 9c (E2E-4) omitidos y fuera de la comparación")
    if not reg.checks: reg.check("guias_e2e/correr.py produjo resultados", False, (r.stdout + r.stderr)[-500:])
    if "Traceback (most recent call last)" in r.stdout + r.stderr: reg.trazas.append({"paso": "guias_e2e", "comando": "correr.py", "cola": (r.stdout + r.stderr)[-600:]})
    return reg


def tareas(nivel, corrida, a, interp, cache):
    """[(unidad, función sin argumentos que devuelve un Registro)] del nivel."""
    import matriz, ciclo, integraciones, contratos, hermes, migracion, opcionales, portal
    logs = lambda u: os.path.join(corrida, "celdas", u)
    trabajo = lambda u: os.path.join(corrida, "trabajo", u)
    py13, py39 = interp["3.13"], interp["3.9"]
    def unidad(niv, u, f):
        def g():
            reg = Registro(niv, u, logs(u)); os.makedirs(trabajo(u), exist_ok=True)
            try: f(reg)
            except Exception as x:
                import traceback
                reg.check(f"{u}: la unidad se ejecutó sin errores de la suite", False, f"{type(x).__name__}: {x} · " + " ← ".join(
                    f"{os.path.basename(fr.filename)}:{fr.lineno}" for fr in reversed(traceback.extract_tb(x.__traceback__)[-3:])))
            reg.guardar_log(); return reg
        return g
    out = []
    if nivel == "robustez":
        out.append(("pp-robustez-3.13", lambda: probar_paquete("robustez", "pp-robustez-3.13", py13, "RB,Y", logs("pp-robustez-3.13"))))
        if py39: out.append(("pp-robustez-3.9", lambda: probar_paquete("robustez", "pp-robustez-3.9", py39, "RB,Y", logs("pp-robustez-3.9"))))
        out.append(("migracion", unidad("robustez", "migracion", lambda reg: migracion.correr(trabajo("migracion"), reg, py13, cache))))
    elif nivel == "caminos":
        out.append(("pp-caminos-3.13", lambda: probar_paquete("caminos", "pp-caminos-3.13", py13, "CP", logs("pp-caminos-3.13"))))
        for cierre in ("normal", "prematuro"):
            c = {"python": "3.13", "deps": "completas", "bmad": "6.12.4", "idioma": "es", "salida": "utf-8", "ruta": "simple", "cierre": cierre}
            out.append((f"ciclo-{cierre}", unidad("caminos", f"ciclo-{cierre}", lambda reg, c=c: ciclo.recorrer(dict(c, python_ruta=py13), trabajo(f"ciclo-{c['cierre']}"), reg))))
    elif nivel == "matriz":
        sel = {x.strip() for x in a.celdas.split(",")} if a.celdas else None
        for cid, c in matriz.celdas():
            if sel and cid not in sel: continue
            out.append((cid, lambda cid=cid, c=c: matriz.correr_celda(cid, c, trabajo(cid), logs(cid), interp)))
    elif nivel == "integraciones":
        out.append(("canales", unidad("integraciones", "canales", lambda reg: integraciones.correr(trabajo("canales"), reg, py13))))
    elif nivel == "contratos":
        out.append(("contratos", unidad("contratos", "contratos", lambda reg: contratos.correr(trabajo("contratos"), reg, py13))))
    elif nivel == "hermes":
        out.append(("hermes", unidad("hermes", "hermes", lambda reg: hermes.correr(trabajo("hermes"), reg, py13))))
    elif nivel == "e2e":
        out.append(("e2e-3.13", lambda: e2e("e2e-3.13", py13, logs("e2e-3.13"), trabajo("e2e"))))
        if py39: out.append(("e2e-3.9", lambda: e2e("e2e-3.9", py39, logs("e2e-3.9"), trabajo("e2e"), con_kb=False)))
    elif nivel == "opcionales":
        for u, f in {**opcionales.UNIDADES, **portal.UNIDADES}.items():
            out.append((u, unidad("opcionales", u, lambda reg, u=u, f=f: f(trabajo(u), reg, cache))))
    return out


def evaluar(res, permitidas):
    """Agrega a cada unidad sus omisiones inesperadas (fuera del manifiesto y de --permitir-omision)."""
    for u in res:
        vistas = {o["clave"] for o in u["omisiones"]}
        perm = set(u.get("esperadas") or []) | set(permitidas)
        if u["nivel"] == "e2e": perm.add("pm-kb")                         # pm-kb es opcional en las guías (omisión informada)
        if u["nivel"] == "opcionales": perm |= {"pm-kb", "docker", "skills-externas"}   # componentes opcionales ausentes (omisión informada)
        u["omisiones_inesperadas"] = sorted(k for k in vistas if not any(k == p or k.startswith(p) for p in perm))
    return res


def firma(u):
    return ([(c["comprobacion"], c["ok"]) for c in u["checks"]], sorted(o["clave"] for o in u["omisiones"]))


def informe(salida, datos):
    L = [f"# Suite de variantes · {datos['fecha']}", "",
         "Intérpretes: " + ", ".join(f"{k} → {v or 'no disponible'}" for k, v in datos["interpretes"].items()) + f" · niveles: {', '.join(datos['niveles'])} · "
         f"corridas: {len(datos['corridas'])} · resultado: **{'OK' if datos['ok'] else 'FALLO'}**", ""]
    for c in datos["corridas"]:
        L += [f"## Corrida {c['n']} · {c['duracion_s']:.0f} s · {c['ok']} OK · {c['fallo']} FALLO · {c['trazas']} trazas · {c['omisiones_inesperadas']} omisiones fuera del manifiesto", "",
              "| Nivel | Unidad | Ejes | OK | FALLO | Omisiones (vistas / esperadas) | Duración | Primera falla |", "|---|---|---|---|---|---|---|---|"]
        for u in c["unidades"]:
            ejes = " · ".join(f"{v}" for k, v in (u.get("celda") or {}).items()) if u.get("celda") else ""
            prim = next((f"{x['comprobacion'][:90]}: {x['detalle'][:160]}" for x in u["checks"] if not x["ok"]), "")
            if not prim and u["trazas"]: prim = f"traza en {u['trazas'][0]['paso']}"
            if not prim and u["omisiones_inesperadas"]: prim = f"omisión fuera del manifiesto: {', '.join(u['omisiones_inesperadas'])}"
            om = ", ".join(sorted(o["clave"] for o in u["omisiones"])) or "—"
            L.append(f"| {u['nivel']} | {u['unidad']} | {ejes} | {u['ok']} | {u['fallo']} | {om} / {', '.join(u.get('esperadas') or []) or '—'} | {u['duracion_s']:.0f} s | "
                     + prim.replace("|", "\\|").replace("\n", " ") + " |")
        L += ["", "Duración por nivel: " + " · ".join(f"{k} {v:.0f} s" for k, v in c["duracion_niveles"].items()), ""]
        notas = sorted({n for u in c["unidades"] for n in u.get("notas", [])})
        if notas: L += ["Notas (no son fallas):", ""] + [f"- {n}" for n in notas] + [""]
    if datos.get("determinismo") is not None:
        L += ["## Determinismo", "", ("Las corridas dieron las mismas comprobaciones, resultados y omisiones." if not datos["determinismo"]
                                       else "Diferencias entre corridas: " + "; ".join(datos["determinismo"][:20])), ""]
    open(os.path.join(salida, "INFORME.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog="\n".join(__doc__.splitlines()[1:]))
    ap.add_argument("--nivel", default="todo"); ap.add_argument("--repetir", type=int, default=1)
    ap.add_argument("--salida"); ap.add_argument("--json", nargs="?", const="", default=None, metavar="RUTA", help="también escribe el resultado en RUTA (o lo imprime sin RUTA)")
    ap.add_argument("--celdas", help="solo esas celdas de la matriz (M01,…,D2)"); ap.add_argument("--paralelo", type=int, default=4)
    ap.add_argument("--permitir-omision", action="append", default=[], metavar="CLAVE"); ap.add_argument("--conservar", action="store_true")
    a = ap.parse_args()
    niveles = list(NIVELES) if a.nivel == "todo" else [n.strip() for n in a.nivel.split(",") if n.strip()]
    malos = [n for n in niveles if n not in NIVELES]
    if malos: sys.exit(f"--nivel: desconocido(s) {', '.join(malos)}; válidos: {', '.join(NIVELES)} o todo")
    salida = os.path.abspath(a.salida or tempfile.mkdtemp(prefix="pm-variantes-")); os.makedirs(salida, exist_ok=True)
    interp = interpretes()
    vers = {k: (version_de(v) if v else "") for k, v in interp.items()}
    if interp["3.9"] and vers["3.9"] != "3.9": interp["3.9"] = None
    cache = os.path.join(salida, "cache")
    datos = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "interpretes": {k: f"{interp[k]} ({vers[k]})" if interp[k] else None for k in interp},
             "niveles": niveles, "corridas": []}
    print(f"Suite de variantes → {salida} · niveles {', '.join(niveles)} · intérpretes {datos['interpretes']}", flush=True)
    for n in range(1, a.repetir + 1):
        corrida = os.path.join(salida, f"corrida-{n}"); shutil.rmtree(corrida, ignore_errors=True); os.makedirs(corrida)
        t0 = time.time(); unidades, dur = [], {}
        for nivel in niveles:
            print(f"\n=== corrida {n} · nivel {nivel}", flush=True)
            t1 = time.time()
            ts = tareas(nivel, corrida, a, interp, cache)
            with cf.ThreadPoolExecutor(max_workers=max(1, a.paralelo)) as ex:   # unidades en paralelo; resumen (y duración) al terminar cada una
                unidades += list(ex.map(lambda t: t[1]().resumen(), ts))
            dur[nivel] = round(time.time() - t1, 1)
        evaluar(unidades, a.permitir_omision)
        c = {"n": n, "duracion_s": round(time.time() - t0, 1), "duracion_niveles": dur, "unidades": unidades,
             "ok": sum(u["ok"] for u in unidades), "fallo": sum(u["fallo"] for u in unidades), "trazas": sum(len(u["trazas"]) for u in unidades),
             "omisiones_inesperadas": sum(len(u["omisiones_inesperadas"]) for u in unidades)}
        datos["corridas"].append(c)
        print(f"\nCorrida {n}: {c['ok']} OK · {c['fallo']} FALLO · {c['trazas']} trazas · {c['omisiones_inesperadas']} omisiones fuera del manifiesto · {c['duracion_s']:.0f} s "
              f"({', '.join(f'{k} {v:.0f} s' for k, v in dur.items())})", flush=True)
        if not a.conservar: shutil.rmtree(os.path.join(corrida, "trabajo"), ignore_errors=True)
    det = None
    if len(datos["corridas"]) > 1:
        det = []
        base = {u["unidad"]: firma(u) for u in datos["corridas"][0]["unidades"]}
        for c in datos["corridas"][1:]:
            otra = {u["unidad"]: firma(u) for u in c["unidades"]}
            for k in sorted(set(base) | set(otra)):
                if base.get(k) != otra.get(k): det.append(f"{k} (corrida 1 ≠ corrida {c['n']})")
    datos["determinismo"] = det
    datos["ok"] = all(c["fallo"] == 0 and c["trazas"] == 0 and c["omisiones_inesperadas"] == 0 for c in datos["corridas"]) and not det
    if not a.conservar: shutil.rmtree(cache, ignore_errors=True)
    with open(os.path.join(salida, "resultado.json"), "w", encoding="utf-8") as fh: json.dump(datos, fh, ensure_ascii=False, indent=1)
    informe(salida, datos)
    if a.json is not None:
        if a.json: shutil.copy(os.path.join(salida, "resultado.json"), a.json)
        else: print(json.dumps({k: v for k, v in datos.items() if k != "corridas"} | {"corridas": [{k: v for k, v in c.items() if k != "unidades"} for c in datos["corridas"]]}, ensure_ascii=False))
    print(f"\nResultado: {'OK' if datos['ok'] else 'FALLO'}" + (f" · determinismo: {len(det)} diferencias" if det else "") + f" · {os.path.join(salida, 'INFORME.md')}")
    sys.exit(0 if datos["ok"] else 1)


if __name__ == "__main__":
    main()
