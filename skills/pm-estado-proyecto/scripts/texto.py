#!/usr/bin/env python3
"""Normalización de texto para buscar en registros y documentos en español e inglés (biblioteca estándar, sin modelo).
Text folding for Spanish/English search over registers and documents (standard library, no model).

La usan `decision.py expediente --tema` y la vigencia de decisiones (sanidad DEC-05); está pensada también para el
futuro indexador. Es determinista y explicable: cada término de una consulta coincide con un término de la fila o no.

Qué pliega (SPEC.md §1.10.15):
- minúsculas y sin tildes (ñ → n); palabras vacías frecuentes en español e inglés;
- flexiones con un lematizador ligero (`lema`): plurales (decisiones → decision, proveedores → proveedor), género y
  vocal final (normativa = normativo = normative → normativ), participios y gerundios (aprobado, aprobada, aprobamos,
  aprobación → aprob; approved → approv), y un glosario corto inglés → español de términos de gestión (board → junta,
  risk → riesgo, budget → presupuesto, gate → puerta, approve → aprobar…) para que una consulta en un idioma encuentre
  filas escritas en el otro;
- fechas: ISO (2027-01-12), dd/mm/aaaa (día primero), "15 de marzo de 2027", "March 15, 2027", "enero 2027",
  "Jan 2027"; una fecha de la fila también vale por su mes (2027-01), su año, su trimestre (2027-t1) y el mes sin año
  ("enero" → mes-01). "T1 2027" y "Q1 2027" → 2027-t1;
- cifras: 39.800 = 39,800 = 39800 = 39,8 mil = 39.8k (un solo separador seguido de tres dígitos es de miles; si no,
  decimal); "2.500" en la búsqueda vale 2500 (en las hojas de decisión sigue rechazándose por ambiguo);
- versiones (v1.0, v1.1) e ids: R-3 = R-003 para los prefijos de los registros; B-01 = B-1 para los demás.
Coincidencia de palabras: igual, o una es prefijo de la otra con al menos 5 letras y hasta 3 de diferencia.
Límites conocidos: no es un lematizador completo (cambios de raíz como aprueba/aprobado no se unen) ni entiende
sinónimos fuera del glosario; mm/dd/aaaa en inglés se lee como día primero salvo que el primer número pase de 12.
"""
import re, unicodedata

PALABRAS_VACIAS = set("""
a al algo algun alguna algunas alguno algunos ante antes aqui asi aun cada como con contra cual cuales cuando de del
desde donde dos el ella ellas ellos en entre era es esa esas ese eso esos esta estaba estado estan estar este esto estos
fue fueron ha habia han hasta hay la las le les lo los mas me mi mientras mismo muy nos o otra otras otro otros para
pero poco por porque pues que quien se ser si sido sin sobre son su sus tal tambien tanto te tiene tienen todo todos
toda todas tras tu un una unas uno unos usted ya y
about after all also an and any are as at be been before being both but by can could did do does each for from had has
have how if in into is it its may might more most of on or our over same should so some such than that the their them
then there these they this those through to under until very was we were what when where which while who why will
with would you
""".split())
NEGACIONES = {"no", "nunca", "jamas", "ni", "tampoco", "ningun", "ninguna", "ninguno", "not", "never", "nor", "none", "without"}

MESES = {"enero": 1, "january": 1, "febrero": 2, "february": 2, "marzo": 3, "march": 3, "abril": 4, "april": 4,
         "mayo": 5, "junio": 6, "june": 6, "julio": 7, "july": 7, "agosto": 8, "august": 8, "septiembre": 9,
         "setiembre": 9, "september": 9, "octubre": 10, "october": 10, "noviembre": 11, "november": 11,
         "diciembre": 12, "december": 12}
# abreviaturas: solo junto a un año o a un día (solas son palabras comunes: mar, may, set, dec…)
MESES_ABREV = {"ene": 1, "jan": 1, "feb": 2, "mar": 3, "abr": 4, "apr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8,
               "aug": 8, "sep": 9, "sept": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12, "dec": 12}
PREFIJOS_REGISTRO = {"r", "i", "c", "d", "s", "l", "st", "q", "a", "et", "pf", "rc", "en", "pu"}
MULTIPLICADORES = {"mil": 1e3, "k": 1e3, "thousand": 1e3, "millon": 1e6, "millones": 1e6,
                   "million": 1e6, "millions": 1e6}
# glosario corto inglés → español (términos de gestión que más se buscan); se aplica sobre los lemas
GLOSARIO = [("board", "junta"), ("risk", "riesgo"), ("budget", "presupuesto"), ("reserve", "reserva"), ("change", "cambio"),
            ("stage", "etapa"), ("gate", "puerta"), ("approve", "aprobar"), ("approval", "aprobacion"), ("reject", "rechazar"),
            ("contingency", "contingencia"), ("supplier", "proveedor"), ("vendor", "proveedor"), ("scope", "alcance"),
            ("cost", "costo"), ("schedule", "cronograma"), ("lesson", "leccion"), ("assumption", "supuesto"),
            ("benefit", "beneficio"), ("quality", "calidad"), ("requirement", "requisito"), ("delivery", "entrega"),
            ("deliver", "entregar"), ("approach", "enfoque"), ("tolerance", "tolerancia"), ("executive", "ejecutivo"),
            ("project", "proyecto"), ("milestone", "hito"), ("contract", "contrato"), ("decision", "decision"),
            ("stakeholder", "interesado"), ("compliance", "cumplimiento"),
            ("regulatory", "normativo"), ("delegation", "delegacion"), ("exception", "excepcion"), ("plan", "plan"),
            ("issue", "incidencia"), ("deadline", "plazo"), ("release", "release"), ("customer", "cliente"),
            ("option", "opcion"), ("postpone", "postergar"), ("defer", "diferir"), ("response", "respuesta"), ("owner", "propietario")]


def plano(x):
    """Minúsculas y sin tildes."""
    return unicodedata.normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().lower()


def lema(w):
    """Lema ligero español/inglés de una palabra ya plana (ver el docstring del módulo). Determinista."""
    if len(w) <= 3 or not w.isalpha(): return _fin(w)
    for suf in ("amos", "emos", "imos", "ando", "iendo"):                    # decidimos, aprobamos, revisando
        if w.endswith(suf) and len(w) - len(suf) >= 4: return _fin(w[:-len(suf)])
    if w.endswith("iones") and len(w) > 6: w = w[:-2]                       # decisiones → decision
    elif w.endswith("ces") and len(w) > 5: w = w[:-3] + "z"                  # veces → vez
    elif w.endswith("es") and len(w) > 5 and w[-3] in "rlndjy": w = w[:-2]   # proveedores → proveedor, canales → canal
    elif w.endswith("s") and not w.endswith(("ss", "us", "is")) and len(w) > 4: w = w[:-1]
    if w.endswith("ing") and len(w) > 6: w = w[:-3]                      # approving → approv
    elif w.endswith("ed") and len(w) > 5: w = w[:-2]                     # approved → approv
    elif w.endswith(("acion", "icion")) and len(w) > 7: w = w[:-5]       # aprobacion → aprob, delegacion → deleg
    elif w.endswith("sion") and len(w) > 6: w = w[:-3]                   # revision → revis, decision → decis
    elif w.endswith("ation") and len(w) > 7: w = w[:-5]                  # delegation → deleg
    elif w.endswith(("ado", "ada", "ido", "ida")) and len(w) > 6: w = w[:-3]   # aprobado → aprob, suspendida → suspend
    if w.endswith(("ad", "id")) and len(w) > 6 and not w.endswith(("dad", "tad")): w = w[:-2]
    if w[-1] in "aoe" and len(w) > 4: w = w[:-1]                             # normativa, normativo, normative → normativ
    if w.endswith("ar") and len(w) > 5: w = w[:-2]                           # aprobar → aprob, delegar → deleg
    elif w.endswith(("er", "ir")) and len(w) > 6 and not w.endswith(("der", "ier")): w = w[:-2]
    return _fin(w)


def _fin(w):
    return EQUIV.get(w, w) if "EQUIV" in globals() else w


EQUIV = {lema(en): lema(es) for en, es in GLOSARIO if lema(en) != lema(es)}

_ISO = re.compile(r"\b(\d{4})-(\d{1,2})(?:-(\d{1,2}))?\b")
_DMA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_DIA_MES = re.compile(r"\b(\d{1,2})(?:\s+de)?\s+([a-z]{3,10})\.?(?:\s+de|,)?\s+(\d{4})\b")
_MES_DIA = re.compile(r"\b([a-z]{3,10})\.?\s+(\d{1,2}),?\s+(\d{4})\b")
_MES_ANIO = re.compile(r"\b([a-z]{3,10})\.?(?:\s+de|\s*-|\s*,)?\s+(\d{4})\b|\b([a-z]{3})-(\d{4})\b")
_TRIM = re.compile(r"\b(?:([tq])([1-4])\s*(?:de\s+)?(\d{4})|(\d{4})\s*-?\s*([tq])([1-4]))\b")
_VERSION = re.compile(r"\bv(\d+(?:\.\d+)*)\b")
_ID = re.compile(r"\b([a-z]{1,4})-(\d+(?:\.\d+)*)\b")
_NUM = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)*)(?:\s*(mil|k|thousand|millon|millones|million|millions)\b)?(?![\w])")


def _mes(nombre, con_anio):
    n = MESES.get(nombre)
    if n is None and con_anio: n = MESES_ABREV.get(nombre)
    return n


def _fecha(a, m, d=None):
    try:
        a, m = int(a), int(m)
        if not (1 <= m <= 12 and 1900 <= a <= 2200): return None
        if d is not None:
            d = int(d)
            if not 1 <= d <= 31: return None
            return f"{a:04d}-{m:02d}-{d:02d}"
        return f"{a:04d}-{m:02d}"
    except (TypeError, ValueError):
        return None


def expandir_fecha(f):
    """Términos que representa una fecha ISO (día o mes): la fecha, el mes, el año, el trimestre y el mes sin año."""
    a, m = f[:4], int(f[5:7])
    out = [f] + ([f[:7]] if len(f) == 10 else []) + [a, f"{a}-t{(m - 1) // 3 + 1}", f"mes-{m:02d}"]
    return out


def cifra(txt, mult=None):
    """Número de una cifra escrita con separadores (39.800, 39,800, 39,8 + mil, 1.234,5); None si no se puede leer."""
    s = txt.replace(" ", ".").replace(" ", ".")
    if "." in s and "," in s:
        dec = "." if s.rfind(".") > s.rfind(",") else ","
        s = s.replace("," if dec == "." else ".", "").replace(dec, ".")
    else:
        sep = "." if "." in s else ("," if "," in s else "")
        if sep:
            partes = s.split(sep)
            if len(partes) > 2 or (len(partes[-1]) == 3 and len(partes[0]) <= 3 and partes[0] not in ("0", "")): s = "".join(partes)
            else: s = s.replace(sep, ".")
    try: v = float(s)
    except ValueError: return None
    if mult: v *= MULTIPLICADORES.get(mult, 1)
    return v


def _num_txt(v):
    return str(int(v)) if float(v).is_integer() else f"{v:.6g}"


def analizar(texto, expandir=True):
    """Términos normalizados de `texto` como dict: palabras (lemas), numeros, fechas, versiones, ids y negaciones.
    expandir=True (filas): cada fecha agrega mes, año, trimestre y mes sin año; expandir=False (consultas): solo lo escrito."""
    s = " " + plano(texto) + " "
    out = {"palabras": [], "numeros": [], "fechas": [], "versiones": [], "ids": [], "negaciones": []}

    def tomar(rx, fn):
        nonlocal s
        def rep(m):
            v = fn(m)
            if not v: return m.group(0)
            for k, x in v: out[k].append(x)
            return " "
        s = rx.sub(rep, s)

    def f_iso(m):
        f = _fecha(m.group(1), m.group(2), m.group(3))
        return f and [("fechas", f)]
    def f_dma(m):
        d, mm, a = int(m.group(1)), int(m.group(2)), m.group(3)
        if mm > 12 and d <= 12: d, mm = mm, d
        f = _fecha(a, mm, d)
        return f and [("fechas", f)]
    def f_dia_mes(m):
        n = _mes(m.group(2), True)
        f = n and _fecha(m.group(3), n, m.group(1))
        return f and [("fechas", f)]
    def f_mes_dia(m):
        n = _mes(m.group(1), True)
        f = n and _fecha(m.group(3), n, m.group(2))
        return f and [("fechas", f)]
    def f_mes_anio(m):
        nombre, anio = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        n = _mes(nombre, True)
        f = n and _fecha(anio, n)
        return f and [("fechas", f)]
    def f_trim(m):
        q, a = (m.group(2), m.group(3)) if m.group(1) else (m.group(6), m.group(4))
        return [("fechas", f"{a}-t{q}")]
    def f_version(m): return [("versiones", "v" + m.group(1))]
    def f_id(m):
        p, n = m.group(1), m.group(2)
        if "." not in n:
            n = f"{int(n):03d}" if p in PREFIJOS_REGISTRO else str(int(n))
        return [("ids", f"{p}-{n}")]
    def f_num(m):
        v = cifra(m.group(1), m.group(2))
        return v is not None and [("numeros", _num_txt(v))]

    for rx, fn in ((_ISO, f_iso), (_DMA, f_dma), (_DIA_MES, f_dia_mes), (_MES_DIA, f_mes_dia), (_TRIM, f_trim),
                   (_MES_ANIO, f_mes_anio), (_VERSION, f_version), (_ID, f_id), (_NUM, f_num)):
        tomar(rx, fn)
    for w in re.findall(r"[a-z0-9]+", s):
        if w in NEGACIONES: out["negaciones"].append(w); continue
        if w in MESES: out["fechas"].append(f"mes-{MESES[w]:02d}"); continue
        if w in PALABRAS_VACIAS or (len(w) < 3 and not w.isdigit()): continue
        if w.isdigit(): out["numeros"].append(str(int(w))); continue
        out["palabras"].append(lema(w))
    if expandir:
        fechas = []
        for f in out["fechas"]:
            fechas += expandir_fecha(f) if re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", f) else [f]
        out["fechas"] = fechas
    return out


def terminos(texto, expandir=True):
    """Lista de términos normalizados (sin repetir, en orden): palabras, números, fechas, versiones e ids."""
    a = analizar(texto, expandir)
    return list(dict.fromkeys(a["palabras"] + a["numeros"] + a["fechas"] + a["versiones"] + a["ids"]))


def _parecidas(a, b):
    if a == b: return True
    if not (a.isalpha() and b.isalpha()): return False
    c, l = (a, b) if len(a) <= len(b) else (b, a)
    return len(c) >= 5 and l.startswith(c) and len(l) - len(c) <= 3


def coincidencias(consulta, terminos_fila):
    """Términos de `consulta` (lista de terminos(..., expandir=False)) presentes en `terminos_fila` (terminos(...))."""
    fila = set(terminos_fila)
    largas = [x for x in fila if x.isalpha() and len(x) >= 5]
    return [q for q in consulta if q in fila or (q.isalpha() and len(q) >= 5 and any(_parecidas(q, x) for x in largas))]


def minimo_coincidencias(n):
    """Cuántos términos de una consulta de n términos deben coincidir: todos hasta 2; 60 % (al menos 2) desde 3."""
    return n if n <= 2 else max(2, -(-n * 3 // 5))


def buscar(consulta, documentos):
    """[(clave, coincidencias)] de los documentos {clave: texto} que coinciden con la consulta, de más a menos."""
    q = terminos(consulta, expandir=False); need = minimo_coincidencias(len(q))
    out = []
    for clave, txt in documentos.items():
        c = coincidencias(q, terminos(txt))
        if q and len(c) >= need: out.append((clave, c))
    return sorted(out, key=lambda x: -len(x[1]))


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser(description="Términos normalizados de un texto (consulta y fila) / normalized search terms. "
                                 "Uso: texto.py \"enero 2027 presupuesto 39.800\" [--json]")
    ap.add_argument("textos", nargs="+"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    for x in a.textos:
        if a.json: print(json.dumps({"texto": x, "consulta": terminos(x, False), "fila": analizar(x)}, ensure_ascii=False))
        else: print(f"{x}\n  consulta: {' '.join(terminos(x, False)) or '—'}\n  fila:     {' '.join(terminos(x)) or '—'}")
