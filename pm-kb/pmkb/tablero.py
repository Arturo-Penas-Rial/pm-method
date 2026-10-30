"""Tablero del proyecto en pm-kb: publicar en el índice el pm-tablero/1 del núcleo de pm-method y sus instantáneas.
docs/PM-KB.md §11.1 · SPEC §1.10.17.

pm-kb no calcula el tablero: ejecuta `tablero.py generar --json` del núcleo (solo lectura: PM_SOLO_LECTURA=1, sin bloqueo
ni escrituras, también sobre una carpeta de solo lectura) y `tablero.py listar --json`, lee las instantáneas congeladas
de `03-control/reportes/tableros/` (que escribe pm-method) y guarda todo en `pmkb.tablero` y `pmkb.instantanea`. La
comparación de dos tableros usa la función `comparar` del núcleo, en el mismo proceso. Nunca escribe en la carpeta.

Circulación: el tablero se guarda en una fila `equipo` sin las tarjetas cuya fuente es de circulación restringida (ids
estables y archivos restringidos del índice) y, solo si eso quitó algo, en una fila `restringida` completa; RLS elige.

Por actor (docs/PM-KB.md §11.8): el tablero publicado (o una instantánea) se filtra en el mismo proceso con la API pública
del núcleo (`actores` y `filtrar_actor` de tablero.py, las reglas de `tablero.py generar --actor`), leyendo la carpeta
indexada en modo de solo lectura; pm-kb no repite esas reglas.
"""
import copy, datetime, hashlib, importlib, importlib.util, json, os, re, subprocess, sys, threading
from pathlib import Path

from . import fuentes, indexador

NUCLEO = fuentes.RAIZ_PAQUETE / "skills" / "pm-estado-proyecto" / "scripts"
SCRIPT = NUCLEO / "tablero.py"
FORMATO = "pm-tablero/1"
DIR_TABLEROS = "03-control/reportes/tableros"
ID_INSTANTANEA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]{0,80}$")
GRUPOS = ("decidir", "escalar", "desbloquear", "vigilar")
ORIGENES = ("indexar", "vigilar", "tablero", "web")
PLAZO = 120


class ErrorTablero(RuntimeError):
    """El núcleo no pudo generar o listar el tablero (el mensaje es el del núcleo, sin traza)."""


def _correr(gestion, *args, timeout=PLAZO):
    env = {**os.environ, "PM_SOLO_LECTURA": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        r = subprocess.run([sys.executable, str(SCRIPT), "--proyecto", str(gestion), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        raise ErrorTablero(f"tablero.py {args[0]} no terminó en {timeout} s")
    except OSError as x:
        raise ErrorTablero(f"no se pudo ejecutar {SCRIPT}: {x}")
    if r.returncode != 0:
        raise ErrorTablero(f"tablero.py {args[0]} terminó con código {r.returncode}: " + (r.stderr or r.stdout).strip()[-400:])
    return r.stdout


def generar(gestion, corte=None):
    """pm-tablero/1 del proyecto (carpeta con estado.json), con el núcleo de pm-method en modo de solo lectura."""
    salida = _correr(gestion, "generar", "--json", *(["--corte", corte] if corte else []))
    try:
        d = json.loads(salida)
    except ValueError:
        raise ErrorTablero("tablero.py generar --json no devolvió JSON")
    if not isinstance(d, dict) or d.get("formato") != FORMATO:
        raise ErrorTablero(f"tablero.py generar no devolvió el formato {FORMATO}")
    return d


def instantaneas(gestion):
    """(instantáneas en orden, avisos): los metadatos de `tablero.py listar --json` más los datos de cada JSON."""
    carpeta = Path(gestion) / DIR_TABLEROS
    if not carpeta.is_dir():
        return [], []
    try:
        lista = json.loads(_correr(gestion, "listar", "--json"))
    except ValueError:
        raise ErrorTablero("tablero.py listar --json no devolvió JSON")
    out, avisos = [], []
    for x in lista if isinstance(lista, list) else []:
        iid = str(x.get("id") or "")
        if not ID_INSTANTANEA.match(iid):
            avisos.append(f"instantánea con un id inválido: {iid!r}")
            continue
        try:
            d = json.loads((carpeta / f"{iid}.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            avisos.append(f"instantánea {iid} ilegible: {type(e).__name__}")
            continue
        if not isinstance(d, dict) or d.get("formato") != FORMATO:
            avisos.append(f"instantánea {iid} sin el formato {FORMATO}")
            continue
        if x.get("en_bitacora") is False:
            avisos.append(f"instantánea {iid} modificada fuera de los scripts (BIT-02)")
        out.append({**x, "orden": len(out), "datos": d})
    return out, avisos


# ---------------------------------------------------------------- tarjetas
def tarjetas(d):
    """[(vista, tarjeta)] de todas las tarjetas del tablero (misma recorrida que `tarjetas` del núcleo)."""
    out = []
    for col in (d.get("ciclo") or {}).get("columnas", []):
        for c in (col.get("decisiones") or []) + (col.get("eventos") or []) + ([col["tarjeta"]] if col.get("tarjeta") else []):
            out.append(("ciclo", c))
    out += [("atencion", c) for c in (d.get("atencion") or {}).get("items", [])]
    ent = d.get("entrega") or {}
    out += [("productos", c) for c in (ent.get("productos") or {}).get("tarjetas", [])]
    for reg, v in (ent.get("control") or {}).items():
        out += [(reg, c) for c in (v.get("tarjetas") or []) + (v.get("propuestas") or [])]
    out += [("artefactos", c) for c in ((d.get("artefactos") or {}).get("elementos") or {}).values()]
    return out


def tarjeta(d, ref):
    """La tarjeta principal de un id estable (la de su propia vista antes que la del radar), o None."""
    cs = [(v, c) for v, c in tarjetas(d) if c.get("ref") == ref]
    cs.sort(key=lambda x: x[0] == "atencion")
    return cs[0] if cs else None


def columna_puerta(d, ref):
    """Columna del ciclo de la próxima puerta con esa ref (hallazgos y lista de verificación), o None."""
    for col in (d.get("ciclo") or {}).get("columnas", []):
        if col.get("puerta") and col.get("estado") == "proxima" and (col.get("tarjeta") or {}).get("ref") == ref:
            return col
    return None


def detalle_puertas(gestion, d):
    """{ref de puerta: decisión completa} de estado.json.puertas (condiciones, verificación) para la ficha de la puerta."""
    try:
        e = json.loads((Path(gestion) / "estado.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    puertas = [p for p in (e.get("puertas") or []) if isinstance(p, dict)]
    out, usadas = {}, set()
    for v, c in tarjetas(d):
        if v != "ciclo" or c.get("tipo") != "puerta" or c.get("estado") == "proxima" or c["ref"] in out:
            continue
        cand = [i for i, p in enumerate(puertas) if i not in usadas and (
            (c.get("decision_id") and p.get("decision_id") == c.get("decision_id"))
            or (not c.get("decision_id") and p.get("tipo") == c.get("puerta") and p.get("etapa") == c.get("etapa") and p.get("fecha") == c.get("fecha")))]
        if not cand:
            continue
        usadas.add(cand[0])
        p = puertas[cand[0]]
        ver = p.get("verificacion") if isinstance(p.get("verificacion"), dict) else {}
        out[c["ref"]] = {"tipo": p.get("tipo", ""), "etapa": p.get("etapa"), "fecha": p.get("fecha", ""), "decision": p.get("decision", ""),
                         "decision_id": p.get("decision_id", ""), "por": p.get("por", ""), "condiciones": p.get("condiciones", ""),
                         "condiciones_cumplidas": p.get("condiciones_cumplidas", ""), "forzada": bool(p.get("forzada")),
                         "motivo": p.get("motivo", ""), "lista": ver.get("lista", ""), "confirmada_por": ver.get("confirmada_por", ""),
                         "bloqueos": [str(x) for x in (ver.get("bloqueos") or [])][:20],
                         "observaciones": [str(x) for x in (ver.get("observaciones") or [])][:20]}
    return out


# ---------------------------------------------------------------- circulación
def podar(d, refs, rutas):
    """(copia del tablero sin las tarjetas de fuente restringida, cuántas se quitaron). `refs`: ids estables restringidos;
    `rutas`: archivos restringidos, relativos a la carpeta de gestión (como `fuente` de las tarjetas)."""
    refs, rutas = set(refs or ()), set(rutas or ())
    if not refs and not rutas:
        return d, 0
    x = copy.deepcopy(d)
    n = 0
    fuera = lambda c: isinstance(c, dict) and (c.get("ref") in refs or (c.get("fuente") and c.get("fuente") in rutas))

    def filtrar(lst):
        nonlocal n
        quedan = [c for c in lst or [] if not fuera(c)]
        n += len(lst or []) - len(quedan)
        return quedan
    for col in (x.get("ciclo") or {}).get("columnas", []):
        for k in ("decisiones", "eventos"):
            if k in col:
                col[k] = filtrar(col[k])
        if isinstance(col.get("tarjeta"), dict) and fuera(col["tarjeta"]):
            col["tarjeta"]["fuente"] = ""                 # la próxima puerta se mantiene; su lista de verificación, no
    at = x.get("atencion") or {}
    if "items" in at:
        antes = len(at["items"])
        at["items"] = filtrar(at["items"])
        if len(at["items"]) != antes:
            at["totales"] = {g: sum(1 for i in at["items"] if i.get("grupo") == g) for g in GRUPOS}
    ent = x.get("entrega") or {}
    if ent.get("productos"):
        ent["productos"]["tarjetas"] = filtrar(ent["productos"].get("tarjetas"))
    for v in (ent.get("control") or {}).values():
        v["tarjetas"] = filtrar(v.get("tarjetas"))
        v["propuestas"] = filtrar(v.get("propuestas"))
    arts = x.get("artefactos") or {}
    el = arts.get("elementos") or {}
    for k in [k for k, c in el.items() if fuera(c) or k in refs or (c.get("ruta") and c.get("ruta") in rutas)]:
        el.pop(k); n += 1
    for g in arts.get("grupos") or []:
        g["claves"] = [k for k in g.get("claves") or [] if k in el]
    if "eventos" in x:
        antes = len(x["eventos"])
        x["eventos"] = [e for e in x["eventos"] if (e.get("archivo") or "") not in rutas and not set(e.get("ids") or []) & refs]
        n += antes - len(x["eventos"])
    return x, n


def restringidos(cur, proyecto, gestion):
    """(refs, rutas relativas a la gestión) de circulación restringida en el índice del proyecto (dueño del índice)."""
    cur.execute("SELECT ref FROM pmkb.ubicacion WHERE proyecto = %s AND circulacion = 'restringida'", (proyecto,))
    refs = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT DISTINCT fuente FROM pmkb.unidad WHERE proyecto = %s AND circulacion = 'restringida'", (proyecto,))
    pref = (gestion.rstrip("/") + "/") if gestion else ""
    rutas = {f[len(pref):] if pref and f.startswith(pref) else f for (f,) in cur.fetchall()}
    return refs, rutas


def huella_contenido(d):
    """sha256 del tablero sin la hora de generación: igual si no cambió nada que se vea."""
    sin = {k: v for k, v in d.items() if k != "generado"}
    return hashlib.sha256(json.dumps(sin, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- publicar
def carpeta_gestion(raiz, gestion):
    return Path(raiz) / (gestion or "")


def publicar(conn, proyecto, raiz, gestion, origen="tablero", por="", corte=None):
    """Genera el tablero con el núcleo, lee las instantáneas y reemplaza las filas del proyecto en pmkb.tablero y
    pmkb.instantanea en una transacción (conexión del dueño del índice). Devuelve un resumen con los datos completos."""
    if origen not in ORIGENES:
        raise ValueError(f"origen inválido: {origen}")
    g = carpeta_gestion(raiz, gestion)
    if not (g / "estado.json").is_file():
        raise ErrorTablero(f"{g} no tiene estado.json (no es un proyecto de pm-method)")
    d = generar(g, corte)
    ins, avisos = instantaneas(g)
    det = detalle_puertas(g, d)
    sha = huella_contenido(d)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(indexador.BLOQUEO_ESQUEMA_COMPARTIDO)
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('pmkb.tablero:' || %s))", (proyecto,))
        refs, rutas = restringidos(cur, proyecto, gestion or "")
        cur.execute("SELECT version, sha256 FROM pmkb.tablero WHERE proyecto = %s ORDER BY circulacion = 'restringida' DESC LIMIT 1", (proyecto,))
        prev = cur.fetchone()
        version = 1 if not prev else prev[0] + (0 if prev[1] == sha else 1)
        cur.execute("DELETE FROM pmkb.tablero WHERE proyecto = %s", (proyecto,))
        cur.execute("DELETE FROM pmkb.instantanea WHERE proyecto = %s", (proyecto,))
        eq, n = podar(d, refs, rutas)
        det_eq = {k: v for k, v in det.items() if k not in refs and (v.get("lista") or "") not in rutas}
        filas = [("equipo", eq, det_eq)] + ([("restringida", d, det)] if n else [])
        for circ, datos, dt in filas:
            cur.execute("""INSERT INTO pmkb.tablero (proyecto, circulacion, formato, huella, sha256, corte, n_bitacora, version, origen, por, detalle, datos)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (proyecto, circ, d.get("formato", FORMATO), d.get("huella") or "", sha, d.get("corte") or "", d.get("n_bitacora"),
                         version, origen, (por or "")[:120], json.dumps(dt, ensure_ascii=False), json.dumps(datos, ensure_ascii=False)))
        for x in ins:
            datos = x["datos"]
            eqx, nx = podar(datos, refs, rutas)
            for circ, dd in [("equipo", eqx)] + ([("restringida", datos)] if nx else []):
                cur.execute("""INSERT INTO pmkb.instantanea (proyecto, id, circulacion, orden, fecha, tipo, etiqueta, puerta, etapa, decision,
                                                            decision_id, por, corte, archivo, html, sha256, en_bitacora, datos)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (proyecto, x["id"], circ, x["orden"], x.get("fecha") or "", x.get("tipo") or "", x.get("etiqueta") or "",
                             x.get("puerta") or "", x.get("etapa") if isinstance(x.get("etapa"), int) else None, x.get("decision") or "",
                             x.get("decision_id") or "", x.get("por") or "", x.get("corte") or "", x.get("archivo") or "",
                             (x["archivo"][:-5] + ".html") if x.get("html") and x.get("archivo", "").endswith(".json") else "",
                             x.get("sha256") or "", x.get("en_bitacora"), json.dumps(dd, ensure_ascii=False)))
    return {"proyecto": proyecto, "version": version, "cambio": not prev or prev[1] != sha, "datos": d, "instantaneas": len(ins),
            "podadas": n, "avisos": list(d.get("avisos") or []) + avisos}


def linea_publicado(nombre, r):
    """Línea de `indexar`, `vigilar` y `tablero` sobre la publicación."""
    d = r["datos"]
    c, t = d.get("ciclo") or {}, (d.get("atencion") or {}).get("totales") or {}
    return (f"pm-kb: tablero de {nombre} publicado · versión {r['version']}{'' if r['cambio'] else ' (sin cambios)'} · corte {d.get('corte')} · "
            f"{c.get('fase', '')} · etapa {c.get('etapa', '')} · atención: " + ", ".join(f"{t.get(g, 0)} {g}" for g in GRUPOS)
            + f" · próxima puerta: {(d.get('atencion') or {}).get('proxima_puerta') or '—'} · {r['instantaneas']} instantánea(s)"
            + (f" · {r['podadas']} tarjeta(s) restringida(s) fuera de la vista de equipo" if r["podadas"] else ""))


# ---------------------------------------------------------------- comparar (función del núcleo) y cartera
_NUCLEO_MOD = None


def nucleo():
    """El módulo tablero.py del núcleo, cargado una vez en este proceso (para `comparar`, que no lee ni escribe nada)."""
    global _NUCLEO_MOD
    if _NUCLEO_MOD is None:
        spec = importlib.util.spec_from_file_location("pm_method_tablero", str(SCRIPT))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _NUCLEO_MOD = m
    return _NUCLEO_MOD


def comparar(a, b):
    """Tarjetas que entraron, salieron o cambiaron de columna o estado entre dos tableros (`comparar` del núcleo)."""
    return nucleo().comparar(a, b)


# ---------------------------------------------------------------- por actor (API pública del núcleo, en proceso)
_ACTOR = threading.Lock()      # el núcleo marca PM_SOLO_LECTURA en el entorno mientras lee: un filtro a la vez


def _con_nucleo(fn):
    """Corre fn(m) con el núcleo cargado, de a uno por proceso (la API del núcleo lee en modo de solo lectura: sin
    bloqueo ni escrituras). Un actor inexistente o ambiguo (`ActorInvalido` del núcleo), un dato ilegible o un núcleo que
    termina con su mensaje → ErrorTablero."""
    m = nucleo()
    with _ACTOR:
        try:
            return fn(m)
        except m.ActorInvalido as x:
            raise ErrorTablero(str(x))
        except SystemExit as x:
            raise ErrorTablero(str(x.code if x.code is not None else "el núcleo terminó sin mensaje"))
        except ErrorTablero:
            raise
        except Exception as x:
            raise ErrorTablero(f"{type(x).__name__}: {str(x)[:300]}")


def actores(gestion):
    """Personas que pueden ser actor del tablero (`actores` del núcleo: stakeholders.csv y roles de estado.json):
    [{id, nombre, rol}]. Para el selector «Por actor» del portal (sesiones personales)."""
    return _con_nucleo(lambda m: [{"id": c["id"], "nombre": c["nombre"], "rol": c["rol"]} for c in m.actores(str(gestion))])


def por_actor(d, gestion, actor):
    """Copia del tablero `d` (el publicado o una instantánea) con solo lo del actor: `filtrar_actor` del núcleo, las
    mismas reglas que `tablero.py generar --actor`, sobre la carpeta de gestión."""
    return _con_nucleo(lambda m: m.filtrar_actor(d, str(gestion), actor))


def validar_actor(gestion, actor):
    """El bloque `actor` ({id, nombre, rol, letras}) de `tablero.py generar --json --actor` (núcleo, solo lectura); un
    actor inexistente o ambiguo termina el núcleo con código 1 → ErrorTablero con su mensaje."""
    try:
        d = json.loads(_correr(gestion, "generar", "--json", "--actor", actor))
    except ValueError:
        raise ErrorTablero("tablero.py generar --json --actor no devolvió JSON")
    if not isinstance(d, dict) or not isinstance(d.get("actor"), dict):
        raise ErrorTablero("tablero.py generar --actor no devolvió el bloque `actor`")
    return d["actor"]


def refs(d):
    """Ids estables con ficha en el tablero `d`: sus tarjetas y las condiciones abiertas del ciclo (lo que un enlace
    compartido puede abrir)."""
    out = {c.get("ref") for _, c in tarjetas(d) if isinstance(c, dict) and c.get("ref")}
    out.update(str(x) for x in ((d.get("ciclo") or {}).get("condiciones_abiertas") or []) if x)
    return out


def _fecha(x):
    try:
        return datetime.date.fromisoformat(str(x or "")[:10])
    except ValueError:
        return None


def resumen(d, hoy=None):
    """Lo que muestra una fila de la cartera: fase y proceso, etapa y días que faltan, próxima puerta con bloqueos y
    condiciones, totales de atención y excepción."""
    hoy = hoy or datetime.date.today()
    c = d.get("ciclo") or {}
    prox = next((x for x in c.get("columnas", []) if x.get("puerta") and x.get("estado") == "proxima"), None)
    hs = (prox or {}).get("hallazgos") or []
    sev = {s: sum(1 for h in hs if h.get("severidad") == s) for s in ("bloqueo", "condicion", "aviso")}
    fin = _fecha(c.get("fin_previsto"))
    tot = (d.get("atencion") or {}).get("totales") or {}
    return {"fase": c.get("fase", ""), "proceso": c.get("proceso", ""), "etapa": c.get("etapa"), "nombre_etapa": c.get("nombre_etapa", ""),
            "fin_previsto": c.get("fin_previsto", ""), "dias_restantes": (fin - hoy).days if fin else None,
            "proxima": ({"tipo": prox.get("tipo", ""), "ref": (prox.get("tarjeta") or {}).get("ref", ""), "bloqueos": sev["bloqueo"],
                         "condiciones": sev["condicion"], "avisos": sev["aviso"],
                         "hallazgos": [{"severidad": h.get("severidad", ""), "id": h.get("id", ""), "mensaje": h.get("mensaje", "")} for h in hs[:6]]}
                        if prox else None),
            "condiciones_abiertas": list(c.get("condiciones_abiertas") or []), "forzadas": list(c.get("forzadas") or []),
            "excepcion": c.get("excepcion", ""), "atencion": {g: int(tot.get(g, 0) or 0) for g in GRUPOS},
            "corte": d.get("corte", ""), "proyecto_pm": d.get("proyecto", ""), "avisos": len(d.get("avisos") or [])}


def orden_cartera(r):
    """Primero lo que pide acción: excepción abierta, bloqueos de la próxima puerta, «decidir»; después, el resto de la
    atención (escalar, desbloquear) y el nombre. Sin tablero, al final."""
    s = r.get("resumen")
    if not s:
        return (1, 1, 1, 1, 0, r.get("proyecto", ""))
    a = s["atencion"]
    return (0, 0 if s["excepcion"] else 1, 0 if (s["proxima"] or {}).get("bloqueos") else 1, 0 if a["decidir"] else 1,
            -(a["decidir"] + a["escalar"] + a["desbloquear"]), r.get("proyecto", ""))
