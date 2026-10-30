"""Migración desde versiones anteriores (informe de cobertura T-03), parte del nivel «robustez».

  - Proyectos generados con la versión 2.6.1: las guías E2E-2 (gestión por excepción) y E2E-4 (producto con BMAD hasta
    el cierre) corridas con los scripts del ZIP publicado de 2.6.1 (ruta en PM_ZIP_261; sin ella, la parte se omite con la clave
    «migracion-zip-261»),
    extraído en la caché de la suite. Los proyectos de las guías no son deterministas (bitácora con fecha y hora reales,
    fixture BMAD completo), así que no se guardan como fixture: se generan una vez por carpeta de salida y se reutilizan.
    Abiertos con el código actual: sanidad sin ERROR que 2.6.1 no tuviera, bitácora sin BIT, lectura y escritura sin
    traza, expediente de auditoría verificado y, si la versión cambió, version_paquete_anterior anotado.
  - estado.json v1 (tolerancias como texto, fase «ejecucion», sin presupuestos, umbrales ni ágil): se lee, se migra al
    escribir, conserva las tolerancias y no deja BIT espurios.
"""
import json, os, re, shutil, subprocess, sys, zipfile
from comun import RAIZ, Ejecutor, SCR

ZIP_261 = os.environ.get("PM_ZIP_261") or ""
G = "gestion"


def extraer(cache):
    """Extrae del ZIP solo lo necesario (skills, hooks, scripts/pruebas) en una carpeta propia de la caché."""
    dest = os.path.join(cache, "pm-method-2.6.1")
    if os.path.isfile(os.path.join(dest, ".extraido")): return os.path.join(dest, "pm-method")
    shutil.rmtree(dest, ignore_errors=True); os.makedirs(dest)
    with zipfile.ZipFile(ZIP_261) as z:
        for n in z.namelist():
            if re.match(r"pm-method/(skills/|hooks/|scripts/pruebas/(fixtures|guias_e2e)/)", n) and not n.endswith(".png"):
                z.extract(n, dest)
    open(os.path.join(dest, ".extraido"), "w").write("ok\n")
    return os.path.join(dest, "pm-method")


def generar(cache, raiz261, guia, py):
    """Proyecto de la guía E2E-<guia> generado con 2.6.1 (una vez por caché)."""
    dest = os.path.join(cache, "proyectos-2.6.1", f"g{guia}")
    if os.path.isfile(os.path.join(dest, ".listo")): return dest, ""
    shutil.rmtree(dest, ignore_errors=True)
    tmp = os.path.join(cache, f"tmp-g{guia}"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    gdir = os.path.join(raiz261, "scripts", "pruebas", "guias_e2e")
    r = subprocess.run([py, os.path.join(gdir, f"g{guia}.py"), os.path.join(tmp, f"salida-g{guia}.md")], cwd=gdir, capture_output=True, text=True,
                       env={**os.environ, "TMPDIR": tmp, "GUIAS_SALIDA": tmp, "PMKB_LANZADOR": "/nonexistent-pm-kb"}, timeout=900)
    m = re.search(r"Carpeta del recorrido: (.+)", r.stdout)
    if r.returncode != 0 or not m: return None, (r.stdout + r.stderr)[-600:]
    shutil.copytree(m.group(1).strip(), dest, symlinks=True)
    shutil.rmtree(tmp, ignore_errors=True)
    open(os.path.join(dest, ".listo"), "w").write("ok\n")
    return dest, ""


def errores(res):
    d = res.json() or {}
    return {h["codigo"] for h in d.get("hallazgos", []) if h.get("severidad") == "ERROR"}, {h["codigo"] for h in d.get("hallazgos", [])}


def correr(base, reg, py, cache):
    proyectos_v1(base, reg, py)
    if not os.path.isfile(ZIP_261):
        reg.omitir("migracion-zip-261", f"sin el ZIP de 2.6.1 (PM_ZIP_261={ZIP_261 or 'sin definir'})"); return
    raiz261 = extraer(cache)
    for guia in ("2", "4"):
        origen, det = generar(cache, raiz261, guia, py)
        if not reg.check(f"T-03 proyecto de la guía E2E-{guia} generado con 2.6.1", origen, det): continue
        p = os.path.join(base, f"mig-g{guia}"); shutil.rmtree(p, ignore_errors=True); shutil.copytree(origen, p, symlinks=True)
        corte = "2027-06-30"
        viejo = Ejecutor(reg, py, cwd=p)(os.path.join(raiz261, "skills", "pm-estado-proyecto", "scripts", "sanidad.py"), "--proyecto", G, "--json", "--corte", corte,
                                          ok=(0, 1), paso=f"E2E-{guia}: sanidad 2.6.1")
        x = Ejecutor(reg, py, cwd=p)
        nuevo = x("sanidad", "--proyecto", G, "--json", "--corte", corte, ok=(0, 1), paso=f"E2E-{guia}: sanidad actual")
        ev, _ = errores(viejo); en, todos = errores(nuevo)
        reg.check(f"T-03 E2E-{guia} (2.6.1) abierto con el código actual: sanidad sin ERROR nuevos y sin BIT", nuevo.json() is not None and not (en - ev)
                  and not {c for c in todos if c.startswith("BIT")}, f"nuevos {sorted(en - ev)} · BIT {sorted(c for c in todos if c.startswith('BIT'))}")
        for args in (("estado", "--proyecto", G, "ver"), ("estado", "--proyecto", G, "contexto", "--corte", corte), ("estado", "--proyecto", G, "radar", "--corte", corte),
                     ("registro", "--proyecto", G, "resumen"), ("puertas", "--proyecto", G, "estado")):
            x(*args, paso=f"E2E-{guia}: {' '.join(args[3:])}")
        h = x("registro", "--proyecto", G, "historial", paso=f"E2E-{guia}: historial")
        version0 = json.load(open(os.path.join(p, G, "estado.json"), encoding="utf-8")).get("version_paquete")
        x("registro", "--proyecto", G, "agregar", "riesgos", "--campo", "evento=Riesgo agregado tras la migración", "--campo", "tipo=amenaza", paso=f"E2E-{guia}: agregar con el código actual")
        x("estado", "--proyecto", G, "set", "enfoque_entrega=hibrido", "--por", "Ejecutiva: Laura Méndez", paso=f"E2E-{guia}: estado.py set")
        h2 = x("registro", "--proyecto", G, "historial", paso=f"E2E-{guia}: historial tras escribir")
        reg.check(f"T-03 E2E-{guia}: bitácora íntegra antes y después de escribir con el código actual (sin BIT-01/02)",
                  "BIT-0" not in h.todo + h2.todo and h2.rc == 0, (h.todo + h2.todo)[-300:])
        e = json.load(open(os.path.join(p, G, "estado.json"), encoding="utf-8"))
        sys.path.insert(0, os.path.dirname(SCR["estado"])); import esquema as E
        if version0 != E.VERSION_PAQUETE:
            reg.check(f"T-03 E2E-{guia}: al escribir, version_paquete pasa a {E.VERSION_PAQUETE} y queda version_paquete_anterior = {version0}",
                      e.get("version_paquete") == E.VERSION_PAQUETE and e.get("version_paquete_anterior") == version0, str({k: e.get(k) for k in ("version_paquete", "version_paquete_anterior")}))
        else:
            reg.notas.append(f"E2E-{guia}: la versión del paquete sigue siendo {version0}; version_paquete_anterior no se ejercita")
        zp = os.path.join(p, "expediente.zip")
        x("paquete", "--proyecto", G, "auditoria", "--proposito", "migración", "--salida", zp, paso=f"E2E-{guia}: auditoria")
        v = x("paquete", "--proyecto", G, "verificar", zp, paso=f"E2E-{guia}: verificar")
        reg.check(f"T-03 E2E-{guia}: expediente de auditoría del proyecto migrado generado y verificado", v.rc == 0 and os.path.exists(zp), v.todo[-200:])


def proyectos_v1(base, reg, py):
    """estado.json v1 sintético: lo que esquema.migrar sabe convertir."""
    d = os.path.join(base, "v1"); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    x = Ejecutor(reg, py, cwd=d)
    x("nuevo", "--ruta", G, "--nombre", "Proyecto v1", "--ejecutivo", "Laura Méndez", "--gestor", "Martín Suárez", "--fecha", "2025-03-01", paso="v1: nuevo_proyecto")
    pe = os.path.join(d, G, "estado.json")
    e = json.load(open(pe, encoding="utf-8"))
    v1 = {k: e[k] for k in ("proyecto", "idioma", "metodo", "enfoque_entrega", "etapa_actual", "roles", "artefactos", "puertas", "creado", "actualizado")}
    v1.update({"fase": "ejecucion", "proceso_actual": "CS", "tolerancias": {"tiempo": "±2 semanas", "costo": "±10 %"},
               "integraciones": {"tracker": "jira", "cronograma": "mermaid"}})
    v1["roles"] = {k: v for k, v in v1["roles"].items() if k not in ("product_owner", "jefes_equipo")}
    for f in os.listdir(os.path.join(d, G)):          # un proyecto v1 no tenía bitácora
        if f.startswith(".bitacora"): os.remove(os.path.join(d, G, f))
    with open(pe, "w", encoding="utf-8") as fh: json.dump(v1, fh, ensure_ascii=False, indent=2)
    s = x("sanidad", "--proyecto", G, "--json", ok=(0, 1), paso="v1: sanidad")
    ver = x("estado", "--proyecto", G, "ver", paso="v1: estado.py ver")
    reg.check("T-03 estado.json v1: sanidad y estado.py ver lo leen (JSON válido, sin traza, sin DAT-01)", s.json() is not None
              and "DAT-01" not in {h["codigo"] for h in (s.json() or {}).get("hallazgos", [])}, s.todo[-300:])
    x("estado", "--proyecto", G, "tolerancia", "--nivel", "etapa", "tiempo=+1 semana", paso="v1: primera escritura")
    e2 = json.load(open(pe, encoding="utf-8"))
    reg.check("T-03 estado.json v1 migrado al escribir: tolerancias de proyecto conservadas, etapa nueva, fase «entrega», cronograma «cpm», presupuestos y umbrales",
              e2["tolerancias"]["proyecto"]["tiempo"] == "±2 semanas" and e2["tolerancias"]["etapa"]["tiempo"] == "+1 semana" and e2["fase"] == "entrega"
              and e2["integraciones"]["cronograma"] == "cpm" and "presupuestos" in e2 and "umbrales_riesgo" in e2 and e2["integraciones"]["tracker"] == "jira",
              json.dumps({k: e2.get(k) for k in ("fase", "tolerancias", "integraciones")}, ensure_ascii=False)[:400])
    s2 = x("sanidad", "--proyecto", G, "--json", ok=(0, 1), paso="v1: sanidad tras escribir")
    h = x("registro", "--proyecto", G, "historial", paso="v1: historial")
    bit = {c for c in errores(s2)[1] if c.startswith("BIT")}
    reg.check("T-03 estado.json v1: la bitácora empieza con la primera escritura, sin BIT espurios", not bit and "BIT-0" not in h.todo, f"{sorted(bit)} {h.todo[-200:]}")
