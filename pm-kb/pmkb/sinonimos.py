"""Expansión de la consulta con equivalencias del dominio (sin modelo): la consulta original más los equivalentes.

Fuentes: el glosario inglés → español de `texto.py` (el mismo que usa `decision.py --tema`) y una lista corta de
sinónimos de gestión de proyectos en español. `PMKB_SINONIMOS` (CSV "termino,equivalente") agrega los de la
organización. La expansión solo suma candidatos (consulta OR): no quita resultados.
"""
import csv, os, re, unicodedata

from . import fuentes  # noqa: F401  (agrega el núcleo de pm-method a sys.path)
import texto as T  # noqa: E402

PARES = [
    ("programador", "desarrollador"), ("programadores", "desarrolladores"), ("lentitud", "timeout"), ("lento", "timeout"),
    ("lentitud", "latencia"), ("demora", "retraso"), ("demo", "demostracion"), ("caso de negocio", "business case"),
    ("jefe de proyecto", "gestor del proyecto"), ("project manager", "gestor del proyecto"), ("interesado", "stakeholder"),
    ("cronograma", "calendario"), ("presupuesto", "costo"), ("proveedor", "contratista"), ("incidencia", "issue"),
    ("compra", "adquisicion"), ("riesgo", "amenaza"), ("caida", "indisponibilidad"),
    ("datos personales", "proteccion de datos"), ("sindicato", "gremio"),
]


def _plano(x):
    return unicodedata.normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().lower()


def _pares():
    ps = [(a, b, True) for a, b in PARES] + [(en, es, False) for en, es in T.GLOSARIO]   # glosario: solo inglés → español
    ruta = os.environ.get("PMKB_SINONIMOS")
    if ruta and os.path.isfile(ruta):
        with open(ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if len(fila) >= 2 and fila[0].strip() and not fila[0].startswith("#"):
                    ps.append((fila[0].strip(), fila[1].strip(), True))
    return [(_plano(a), _plano(b), ida_y_vuelta) for a, b, ida_y_vuelta in ps]


def expandir(consulta):
    """(consulta expandida, equivalencias usadas)."""
    q = " " + re.sub(r"[^\w\s-]", " ", _plano(consulta)) + " "
    extra, usados = [], []
    for a, b, doble in _pares():
        for x, y in (((a, b), (b, a)) if doble else ((a, b),)):
            if f" {x} " in q and f" {y} " not in q and y not in extra:
                extra.append(y); usados.append(f"{x} → {y}")
    return (consulta + (" " + " ".join(extra) if extra else "")), usados
