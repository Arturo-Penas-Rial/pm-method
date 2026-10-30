"""Matriz de entorno de la suite de variantes: ejes, celdas por pairwise (todas las parejas de valores) y manifiesto de
omisiones esperadas por celda (docs/PRUEBAS.md §2.5). Cada celda corre ciclo.recorrer con su intérprete, perfil de
dependencias, BMAD, idioma, codificación de la salida y ruta.

Ejes (3.14 solo en la imagen Docker; pm-kb con base solo con el perfil `kb`, fuera de esta matriz):
  python   3.9 (PM_PYTHON39 o /tmp/py39/bin/python) · 3.13 (el intérprete que corre la suite)
  deps     completas · minimas (sitio/sitecustomize.py bloquea yaml, docx, openpyxl, matplotlib y playwright; mmdc fuera del PATH)
  bmad     ninguno · v4 · v6 (sintético) · 6.12.4 (real) · 6.12.4-fuera (manifest 6.99.0) · 6.12.4-toml (_bmad/custom/config.toml)
  idioma   es · en
  salida   utf-8 · cp1252 (PYTHONIOENCODING, como una tubería de Windows)
  ruta     simple · espacios («Gestión de año 2027/Mi proyecto»)
Combinaciones degradadas por diseño (el puente avisa y el ciclo se detiene tras la especificación): v4 sin PyYAML y
capas TOML con Python 3.9. No entran en el pairwise general; cada una tiene su celda propia (D1, D2), que cubre su pareja.
"""
import itertools, os, sys

EJES = [("python", ["3.13", "3.9"]), ("deps", ["completas", "minimas"]),
        ("bmad", ["6.12.4", "ninguno", "v4", "v6", "6.12.4-fuera", "6.12.4-toml"]),
        ("idioma", ["es", "en"]), ("salida", ["utf-8", "cp1252"]), ("ruta", ["simple", "espacios"])]
DEGRADADAS = [{"python": "3.9", "bmad": "6.12.4-toml"}, {"deps": "minimas", "bmad": "v4"}]


def degradada(c):
    return any(all(c.get(k) == v for k, v in d.items()) for d in DEGRADADAS)


def pairwise(ejes=EJES, valida=lambda c: not degradada(c)):
    """Conjunto pequeño de celdas que cubre todas las parejas de valores de dos ejes distintos (algoritmo voraz
    determinista: cada celda nueva maximiza las parejas todavía no cubiertas; las parejas que ninguna celda válida puede
    cubrir quedan fuera y se informan)."""
    nombres = [n for n, _ in ejes]; valores = dict(ejes)
    pendientes = set()
    for (i, a), (j, b) in itertools.combinations(enumerate(nombres), 2):
        for va in valores[a]:
            for vb in valores[b]:
                if valida({a: va, b: vb}): pendientes.add(((a, va), (b, vb)))
    celdas = []
    todas = [dict(zip(nombres, combo)) for combo in itertools.product(*[valores[n] for n in nombres])]
    todas = [c for c in todas if valida(c)]
    def cubre(c): return {((a, c[a]), (b, c[b])) for a, b in itertools.combinations(nombres, 2)} & pendientes
    while pendientes:
        mejor = max(todas, key=lambda c: (len(cubre(c)), -todas.index(c)))
        nuevas = cubre(mejor)
        if not nuevas: break
        celdas.append(mejor); pendientes -= nuevas
    return celdas, pendientes


def celdas():
    """[(id, celda)]: M01… (pairwise) + D1, D2 (degradadas por diseño)."""
    base, _ = pairwise()
    out = [(f"M{i:02d}", dict(c, cierre="prematuro" if i % 4 == 0 else "normal")) for i, c in enumerate(base, 1)]
    defecto = {"python": "3.13", "deps": "completas", "bmad": "6.12.4", "idioma": "es", "salida": "utf-8", "ruta": "simple", "cierre": "normal"}
    for k, d in enumerate(DEGRADADAS, 1):
        out.append((f"D{k}", dict(defecto, **d)))
    return out


def manifiesto(c):
    """Omisiones (o degradaciones) esperadas de una celda: el ciclo debe observar exactamente estas."""
    om = set()
    if c["deps"] == "minimas" and c["bmad"] != "ninguno": om.add("bmad-pyyaml")
    if c["python"] == "3.9" and c["bmad"] == "6.12.4-toml": om.add("bmad-toml")
    if degradada(c): om.add("ciclo-sin-especificacion")
    elif c["deps"] == "minimas": om |= {"exportar-xlsx", "exportar-docx"}
    return om


def correr_celda(cid, c, trabajo, logs, interp, permitidas=()):
    """Corre el ciclo de una celda. trabajo: carpeta de los proyectos; logs: carpeta del registro de comandos."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from comun import Registro
    import ciclo
    reg = Registro("matriz", cid, logs)
    reg.esperadas = sorted(manifiesto(c))
    reg.celda = c
    py = interp.get(c["python"])
    if not py:
        reg.omitir(f"python-{c['python']}", f"no hay intérprete {c['python']} (PM_PYTHON39)")
        return reg
    try:
        ciclo.recorrer(dict(c, python_ruta=py), trabajo, reg)
    except Exception as x:   # un error de la suite cuenta como FALLO de la celda, sin cortar las demás
        import traceback
        reg.check("la celda se ejecutó sin errores de la suite", False, f"{type(x).__name__}: {x} · " + " ← ".join(
            f"{os.path.basename(f.filename)}:{f.lineno}" for f in reversed(traceback.extract_tb(x.__traceback__)[-3:])))
    reg.guardar_log()
    vistas = {o["clave"] for o in reg.omisiones}
    reg.check(f"omisiones = manifiesto de la celda ({', '.join(reg.esperadas) or 'ninguna'})", vistas == set(reg.esperadas),
              f"vistas {sorted(vistas)} · esperadas {reg.esperadas}")
    return reg
