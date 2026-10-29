"""Aristas entre unidades por ids (deterministas, sin modelo): docs/PM-KB.md §5.

- Declaradas: en una fila de registro, cada columna cuyo valor nombra ids (claves foráneas de `esquema.py` como
  `stakeholder_id`, y columnas de texto como `origen`, `reemplaza`, `artefactos_afectados`, `acciones`, `notas`):
  tipo = nombre de la columna.
- Menciones: un id citado en el texto de una sección, diapositiva, transcripción u objeto JSON (`refs` de los mapas):
  tipo `menciona`.
Solo se guardan aristas hacia ids que existen como unidad del proyecto, salvo los ids de especificación (FR, NFR, REQ,
AD, UJ, SM, E, B, KR, OBJ), que se guardan aunque no tengan ficha propia y se muestran como "sin ficha".
"""
import re

PREFIJOS_REGISTRO = ["R", "I", "C", "D", "S", "L", "Q", "A", "ST", "ET", "PF", "RC", "EN", "PU", "P"]
PREFIJOS_ESPEC = ["FR", "NFR", "REQ", "AD", "UJ", "SM", "E", "B", "KR", "OBJ"]
_ID = re.compile(r"(?<![\w-])((?:" + "|".join(sorted(PREFIJOS_REGISTRO + PREFIJOS_ESPEC, key=len, reverse=True)) + r")-\d+(?:\.\d+)?)(?![\w-]|\.\d)")
COLUMNAS_SIN_ARISTA = {"id", "fecha", "autor", "probabilidad", "impacto", "puntuacion"}


def ids_en(texto):
    vistos, out = set(), []
    for m in _ID.finditer(texto or ""):
        i = m.group(1)
        if i not in vistos:
            vistos.add(i); out.append(i)
    return out


def es_espec(i):
    return i.split("-")[0] in PREFIJOS_ESPEC


def aristas(unidades):
    """[(origen_id, destino_id, tipo, fuente, rango)] sin repetidos, solo desde unidades vigentes."""
    existentes = {u["id"] for u in unidades if u.get("registro")}
    # alias: un id de especificación con fila propia en la fachada (requisitos-bmad.csv, spec-index.json) apunta a ella
    alias = {}
    for u in sorted(unidades, key=lambda u: (not u["fuente"].endswith(".csv"), u["fuente"])):
        sufijo = u["id"].rsplit("#", 1)[-1] if "#" in u["id"] else ""
        if sufijo and _ID.fullmatch(sufijo) and u.get("vigente") and sufijo not in alias:
            alias[sufijo] = u["id"]
    out, vistos = [], set()

    def agregar(o, dst, tipo, u):
        dst = alias.get(dst, dst) if dst not in existentes else dst
        if o == dst or (dst not in existentes and dst not in alias.values() and not es_espec(dst)):
            return
        k = (o, dst, tipo)
        if k not in vistos:
            vistos.add(k); out.append((o, dst, tipo, u["fuente"], u["rango"]))

    for u in unidades:
        if not u.get("vigente"):
            continue
        if u.get("registro") and u.get("fila"):
            for col, val in u["fila"].items():
                if col in COLUMNAS_SIN_ARISTA or not val:
                    continue
                for dst in ids_en(val):
                    agregar(u["id"], dst, col, u)
        else:
            for dst in ids_en(u["titulo"] + "\n" + u["texto"]):
                agregar(u["id"], dst, "menciona", u)
            for dst in u.get("menciones") or []:
                agregar(u["id"], dst, "refs", u)
    return out
