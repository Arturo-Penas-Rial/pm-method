"""Línea de comandos de pm-kb. `pm-kb --help` y docs/PM-KB.md §10."""
import argparse, hashlib, json, os, secrets, shutil, sys, tempfile, textwrap
from pathlib import Path

from . import VERSION, config, formato

AYUDA = """\
pm-kb: índice de conocimiento del proyecto (búsqueda citada para personas y agentes). Componente opcional de pm-method.

  pm-kb base crear | base estado                       esquema en PostgreSQL (idempotente) y su estado
  pm-kb indexar --proyecto NOMBRE --ruta CARPETA       indexa (reemplaza el índice de ese proyecto en una transacción) y publica el tablero
         [--excluir GLOB]… [--restringir GLOB]… [--sin-vectores] [--simular]
  pm-kb vigilar --proyecto NOMBRE --ruta CARPETA [--cada 10] [--ciclos N] [--excluir GLOB]… [--restringir GLOB]… [--sin-vectores]
                                                       reindexa y publica el tablero ante cada cambio de un documento indexable (Ctrl+C termina)
  pm-kb tablero --proyecto NOMBRE [--corte AAAA-MM-DD] [--json]
                                                       publica el tablero (núcleo de pm-method, solo lectura) y sus instantáneas
  pm-kb quitar --proyecto NOMBRE                       borra el índice de un proyecto (la carpeta no se toca)
  pm-kb buscar "consulta" [--proyecto P] [--k 5] [--aprobado | --historia] [--tipo T] [--registro R] [--max-tokens N] [--json]
  pm-kb ficha ID [--historia] · relaciones ID [--saltos 1|2] · versiones DOC · cambios DOC [--desde V --hasta V]
         (ID: R-003, clave de artefacto como business-case, doc_id, id de una sección, puerta:<tipo>:<etapa> o un producto;
          la ficha trae ubicación, movimientos y la tarjeta del tablero)
  pm-kb enlaces --proyecto P [--json]                  artefactos con ruta inexistente, citas a rutas que no existen y movimientos
  pm-kb documento RUTA [--rango L10-L40] · contexto "pregunta" · estado
  pm-kb token crear --persona "Nombre" --proyectos p1,p2|* [--restringida] [--dias 90] · token listar · token revocar --persona "Nombre"
  pm-kb compartir crear --proyecto P [--instantanea ID] [--actor "…"] [--dias 7] [--restringida] [--para "…"]
                                                       enlace de solo lectura a un tablero (se muestra una vez; 7 días, 90 como máximo)
  pm-kb compartir listar [--proyecto P] [--json] · compartir revocar --id ID | --proyecto P [--para "…"]
  pm-kb servir [--host 127.0.0.1] [--puerto 8765]      portal web (cartera, tableros, búsqueda, artefactos) y MCP por HTTP (/mcp), con token
  pm-kb mcp                                            MCP por stdio (Claude Code, Hermes u otro cliente MCP local)
  pm-kb verificar                                      prueba de punta a punta de la instalación
  pm-kb db iniciar|detener|estado|reiniciar-datos      PostgreSQL propio (instalación WSL2/Linux; se inicia solo al usarlo)
"""


def _admin():
    try:
        return config.conectar(lector=False)
    except Exception as x:   # psycopg.OperationalError y faltantes de dependencias
        sys.exit(f"pm-kb: no se pudo conectar a PostgreSQL ({type(x).__name__}: {str(x).strip()[:300]}).\n"
                 "  WSL2: pm-kb db estado (y pm-kb db iniciar; registro en ~/.local/share/pm-kb/postgresql.log)\n"
                 "  Docker: docker compose -f docker/compose.yaml --profile kb ps")


def _sesion(a):
    from .busqueda import Sesion
    return Sesion(_admin(), proyectos="*", restringida=True, persona="línea de comandos (dueño del índice)")


def _sal(a, datos, texto):
    print(json.dumps(datos, ensure_ascii=False, indent=2, default=str) if getattr(a, "json", False) else texto)


def cmd_base(a):
    from . import indexador
    c = _admin()
    if a.accion == "crear":
        indexador.crear_esquema(c)
        print("pm-kb: esquema listo (extensiones vector, unaccent y pg_trgm; RLS activa)")
    else:
        v = indexador.version_esquema(c)
        if not v:
            r = c.execute("SELECT current_setting('server_version')").fetchone()
            print(f"PostgreSQL {r[0]} · sin esquema de pm-kb (pm-kb base crear)")
            return
        r = c.execute("""SELECT current_setting('server_version'),
                         (SELECT string_agg(extname || ' ' || extversion, ', ' ORDER BY extname) FROM pg_extension WHERE extname IN ('vector','unaccent','pg_trgm')),
                         (SELECT count(*) FROM pmkb.indice)""").fetchone()
        print(f"PostgreSQL {r[0]} · esquema pm-kb {v} · extensiones: {r[1]} · proyectos indexados: {r[2]}")
        if v < indexador.ESQUEMA:
            print(f"  aviso: este pm-kb usa el esquema {indexador.ESQUEMA}: `pm-kb base crear` lo actualiza sin perder el índice ni los tokens")


def _avisos_enlaces(nombre, r):
    """Líneas de `indexar` y `vigilar` sobre movimientos y artefactos sin fuente (solo si los hay)."""
    L = []
    if r["movimientos"]:
        L.append(f"  movimientos detectados: {len(r['movimientos'])} (" + "; ".join(
            f"{m['ref']}: {m['ruta_anterior']} → {m['ruta_nueva']}" for m in r["movimientos"][:3]) +
            (" …" if len(r["movimientos"]) > 3 else "") + f"); detalle: pm-kb enlaces --proyecto {nombre}")
    if r["sin_fuente"]:
        L.append(f"  aviso: {len(r['sin_fuente'])} artefacto(s) de estado.json con una ruta que no existe ({', '.join(r['sin_fuente'][:5])}"
                 + (" …" if len(r["sin_fuente"]) > 5 else "") + f"): pm-kb enlaces --proyecto {nombre}")
    return L


def cmd_indexar(a):
    from . import indexador
    nombre = indexador.validar_nombre(a.proyecto)
    if a.simular:
        prep = indexador.preparar(a.ruta, a.excluir, a.restringir)
        us = prep["unidades"]
        print(f"[simulación] {nombre}: {len(us)} unidades ({sum(u['vigente'] for u in us)} vigentes), {len(prep['documentos'])} documentos, "
              f"{len(prep['aristas'])} aristas, {len(prep['historia'])} entradas de historia, {len(prep['omitidos'])} omitidos; "
              f"carpeta de gestión: {prep['gestion'] if prep['gestion'] is not None else 'no encontrada'}")
        for f, m in prep["omitidos"][:20]:
            print(f"  omitido {f}: {m}")
        return
    c = _admin()
    prep, r = indexador.indexar(c, nombre, a.ruta, a.excluir, a.restringir, con_vectores=not a.sin_vectores)
    print(f"pm-kb: {nombre} indexado · {r['unidades']} unidades ({r['vigentes']} vigentes) · {r['documentos']} documentos "
          f"({r['con_versiones']} con varias versiones) · {r['aristas']} relaciones · {r['historia']} entradas de historia · "
          f"commit {r['commit'] or 'sin git'} · vectores: {r['modelo'] or 'no'}")
    if prep["gestion"] is None:
        print("  aviso: no hay estado.json en la carpeta (se indexó como documentación sin versiones de pm-method)")
    for l in _avisos_enlaces(nombre, r):
        print(l)
    for f, m in prep["omitidos"][:20]:
        print(f"  omitido {f}: {m}")
    if len(prep["omitidos"]) > 20:
        print(f"  … y {len(prep['omitidos']) - 20} omitidos más (pm-kb estado)")
    if prep["gestion"] is not None:
        _publicar(c, nombre, prep["raiz"], prep["gestion"], "indexar")


def _publicar(c, nombre, raiz, gestion, origen, corte=None, salir=False):
    """Publica el tablero del proyecto en el índice (pm-kb/pmkb/tablero.py). El índice ya quedó cargado: una falla del
    tablero se informa como aviso (o termina con código 1 si `salir`, en `pm-kb tablero`)."""
    from . import tablero
    try:
        r = tablero.publicar(c, nombre, raiz, gestion, origen=origen, corte=corte)
    except (tablero.ErrorTablero, OSError) as x:
        if salir:
            sys.exit(f"pm-kb: no se pudo publicar el tablero de {nombre}: {x}")
        print(f"  aviso: tablero no publicado ({x})", flush=True)
        return None
    print(tablero.linea_publicado(nombre, r), flush=True)
    for x in r["avisos"][:10]:
        print(f"  aviso del tablero: {x}", flush=True)
    return r


def cmd_tablero(a):
    """Publica el tablero de un proyecto ya indexado (sin reindexar): núcleo de pm-method en solo lectura sobre la carpeta
    indexada, más las instantáneas congeladas; con --json, imprime el pm-tablero/1 publicado."""
    from . import indexador
    nombre = indexador.validar_nombre(a.proyecto)
    c = _admin()
    indexador.exigir_esquema(c)
    x = c.execute("SELECT raiz, gestion FROM pmkb.indice WHERE proyecto = %s", (nombre,)).fetchone()
    if not x:
        sys.exit(f"pm-kb: el proyecto '{nombre}' no está indexado (pm-kb indexar --proyecto {nombre} --ruta CARPETA)")
    if x[1] is None:
        sys.exit(f"pm-kb: {x[0]} no tiene estado.json: sin tablero (no es un proyecto de pm-method)")
    if a.corte:
        import datetime
        try:
            datetime.date.fromisoformat(a.corte)
        except ValueError:
            sys.exit(f"pm-kb: --corte inválida: {a.corte} (AAAA-MM-DD)")
    if a.json:
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            r = _publicar(c, nombre, x[0], x[1], "tablero", a.corte, salir=True)
        print(json.dumps(r["datos"], ensure_ascii=False, indent=1))
    else:
        _publicar(c, nombre, x[0], x[1], "tablero", a.corte, salir=True)


def cmd_vigilar(a):
    """Bucle: compara la huella de todos los documentos indexables de la carpeta (fuentes.huella: ruta, tamaño y fecha de
    cada archivo, más la bitácora) y, si cambió, reindexa (con la detección de movimientos) y publica el tablero. Si
    solo cambió la fecha (vencidas y edades del tablero), vuelve a publicar el tablero sin reindexar. Un error se informa
    y se reintenta en la vuelta siguiente; Ctrl+C termina."""
    import datetime, time
    from . import fuentes, indexador
    nombre = indexador.validar_nombre(a.proyecto)
    if a.cada < 1:
        sys.exit("pm-kb: --cada debe ser 1 o más segundos")
    raiz = Path(a.ruta).resolve()
    if not raiz.is_dir():
        sys.exit(f"pm-kb: no existe la carpeta {raiz}")
    c = _admin()
    indexador.exigir_esquema(c)
    previa, vueltas, dia = None, 0, None
    print(f"pm-kb: vigilando {raiz} cada {a.cada} s para {nombre} (Ctrl+C para terminar)", flush=True)
    try:
        while True:
            try:
                h = fuentes.huella(raiz, a.excluir)
                if h != previa:
                    prep, r = indexador.indexar(c, nombre, raiz, a.excluir, a.restringir, con_vectores=not a.sin_vectores,
                                                avisar=lambda m: print(m, flush=True))
                    print(f"pm-kb: cambio detectado (huella {h}) · {nombre} reindexado · {r['unidades']} unidades ({r['vigentes']} vigentes) · "
                          f"{r['documentos']} documentos · {len(r['movimientos'])} movimientos", flush=True)
                    for l in _avisos_enlaces(nombre, r):
                        print(l, flush=True)
                    previa = h
                    if prep["gestion"] is not None:
                        _publicar(c, nombre, prep["raiz"], prep["gestion"], "vigilar")
                    dia = datetime.date.today()
                elif dia != datetime.date.today():
                    x = c.execute("SELECT raiz, gestion FROM pmkb.indice WHERE proyecto = %s", (nombre,)).fetchone()
                    if x and x[1] is not None:
                        _publicar(c, nombre, x[0], x[1], "vigilar")
                    dia = datetime.date.today()
            except (Exception, SystemExit) as x:      # base caída, carpeta en escritura, etc.: se informa y se reintenta
                if isinstance(x, SystemExit) and x.code in (0, None):
                    raise
                print(f"pm-kb: aviso: no se pudo reindexar ({type(x).__name__}: {str(x)[:200]}); se reintenta en {a.cada} s",
                      file=sys.stderr, flush=True)
                try:
                    c.close()
                except Exception:
                    pass
                try:
                    c = _admin_sin_salir()
                except Exception:
                    pass
            vueltas += 1
            if a.ciclos and vueltas >= a.ciclos:
                break
            time.sleep(a.cada)
    except KeyboardInterrupt:
        pass


def _admin_sin_salir():
    return config.conectar(lector=False)


def cmd_enlaces(a):
    from . import indexador
    nombre = indexador.validar_nombre(a.proyecto)
    r = _sesion(a).enlaces(nombre)
    _sal(a, r, formato.enlaces(r))
    if "error" in r:
        sys.exit(1)


def cmd_quitar(a):
    from . import indexador
    indexador.quitar(_admin(), indexador.validar_nombre(a.proyecto))
    print(f"pm-kb: índice de {a.proyecto} borrado")


def cmd_consulta(a):
    s = _sesion(a)
    if a.cmd == "buscar":
        r = s.buscar(a.consulta, proyecto=a.proyecto, k=a.k, estado="aprobado" if a.aprobado else None, historia=a.historia,
                     max_tokens=a.max_tokens, tipo=a.tipo, registro=a.registro)
        _sal(a, r, formato.buscar(r))
    elif a.cmd == "ficha":
        r = s.ficha(a.id, proyecto=a.proyecto, historia=a.historia); _sal(a, r, formato.ficha(r))
    elif a.cmd == "relaciones":
        r = s.relaciones(a.id, proyecto=a.proyecto, saltos=a.saltos); _sal(a, r, formato.relaciones(r))
    elif a.cmd == "versiones":
        r = s.versiones(a.doc, proyecto=a.proyecto); _sal(a, r, formato.versiones(r))
    elif a.cmd == "cambios":
        r = s.cambios(a.doc, a.desde, a.hasta, proyecto=a.proyecto); _sal(a, r, formato.cambios(r))
    elif a.cmd == "documento":
        r = s.documento(a.ruta, a.rango, proyecto=a.proyecto); _sal(a, r, formato.documento(r))
    elif a.cmd == "contexto":
        r = s.contexto(a.pregunta, proyecto=a.proyecto); _sal(a, r, formato.contexto(r))
    elif a.cmd == "estado":
        r = s.estado_indice(); _sal(a, r, formato.estado(r))


def sha_token(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


DIAS_TOKEN, DIAS_TOKEN_MAX = 90, 365


def crear_token(conn, persona, proyectos, restringida=False, dias=DIAS_TOKEN, horas=None):
    """Token nuevo con vencimiento obligatorio: `dias` (1–365) o, para la sesión local de `servir`, `horas`."""
    if horas is None and not (isinstance(dias, int) and 1 <= dias <= DIAS_TOKEN_MAX):
        raise ValueError(f"--dias debe estar entre 1 y {DIAS_TOKEN_MAX}")
    t = "pmkb_" + secrets.token_urlsafe(32)
    with conn.transaction():
        conn.execute("""INSERT INTO pmkb.acceso (token_sha, persona, proyectos, restringida, vence)
                        VALUES (%s, %s, %s, %s, now() + make_interval(days => %s, hours => %s))""",
                     (sha_token(t), persona, proyectos, restringida, 0 if horas is not None else dias, horas or 0))
    return t


def cmd_token(a):
    c = _admin()
    if a.accion == "crear":
        if not a.persona or not a.proyectos:
            sys.exit("pm-kb: token crear necesita --persona y --proyectos (lista separada por comas, o * para todos)")
        try:
            t = crear_token(c, a.persona, a.proyectos.replace(" ", ""), a.restringida, dias=a.dias)
        except ValueError as x:
            sys.exit(f"pm-kb: {x}")
        vence = c.execute("SELECT vence FROM pmkb.acceso WHERE token_sha = %s", (sha_token(t),)).fetchone()[0]
        print(f"Token para {a.persona} ({a.proyectos}{', con circulación restringida' if a.restringida else ''}), vence {vence:%Y-%m-%d %H:%M %Z}. "
              "Se muestra UNA sola vez; guardalo en un gestor de contraseñas o en una variable de entorno:\n" + t)
    elif a.accion == "listar":
        for p, pr, r, cr, rv, ve, vencido in c.execute("""SELECT persona, proyectos, restringida, creado, revocado, vence,
                                                          vence IS NOT NULL AND vence <= now() FROM pmkb.acceso ORDER BY creado"""):
            print(f"  {p} · {pr}{' · restringida' if r else ''} · creado {cr:%Y-%m-%d}"
                  + (f" · {'venció' if vencido else 'vence'} {ve:%Y-%m-%d}" if ve else " · sin vencimiento (revocar y crear uno nuevo)")
                  + (f" · revocado {rv:%Y-%m-%d}" if rv else ""))
    elif a.accion == "revocar":
        with c.transaction():
            n = c.execute("UPDATE pmkb.acceso SET revocado = now() WHERE persona = %s AND revocado IS NULL", (a.persona,)).rowcount
        print(f"pm-kb: {n} token(s) revocado(s) de {a.persona}")


DIAS_ENLACE, DIAS_ENLACE_MAX = 7, 90


def origen_enlaces():
    """(origen con que se arman los enlaces compartidos, aviso): el primero de PMKB_ORIGENES; sin él, el de `pm-kb servir`
    en esta máquina. Nunca la cabecera Host de un pedido."""
    o = config.origenes()
    if o:
        return o[0], ""
    return "http://localhost:8765", ("  aviso: sin PMKB_ORIGENES el enlace usa http://localhost:8765 y solo abre en esta máquina; para compartir fuera, "
                                     "configurá PMKB_ORIGENES con la dirección (https) por la que el destinatario llega al servicio")


def crear_enlace(conn, proyecto, alcance="actual", actor="", actor_nombre="", restringida=False, para="", dias=DIAS_ENLACE, por=""):
    """Enlace compartido nuevo: (id, token, vence). Solo se guarda el sha256 del token; `dias` de 1 a 90."""
    if not (isinstance(dias, int) and 1 <= dias <= DIAS_ENLACE_MAX):
        raise ValueError(f"--dias debe estar entre 1 y {DIAS_ENLACE_MAX} (por defecto {DIAS_ENLACE})")
    t = "pmkb_" + secrets.token_urlsafe(32)
    with conn.transaction():
        for _ in range(5):
            eid = "e-" + secrets.token_hex(4)
            if not conn.execute("SELECT 1 FROM pmkb.enlace WHERE id = %s", (eid,)).fetchone():
                break
        vence = conn.execute("""INSERT INTO pmkb.enlace (id, token_sha, proyecto, alcance, actor, actor_nombre, restringida, para, creado_por, vence)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now() + make_interval(days => %s)) RETURNING vence""",
                             (eid, sha_token(t), proyecto, alcance, actor, actor_nombre, restringida, para, por, dias)).fetchone()[0]
    return eid, t, vence


def _quien():
    import getpass
    try:
        return f"{getpass.getuser()} (línea de comandos)"
    except Exception:
        return "línea de comandos"


def cmd_compartir(a):
    """Enlaces de solo lectura a un tablero (docs/PM-KB.md §11.7): crear (imprime la URL una sola vez), listar y revocar."""
    from . import indexador, tablero
    c = _admin()
    indexador.exigir_esquema(c)
    if a.accion == "crear":
        if not a.proyecto:
            sys.exit("pm-kb: compartir crear necesita --proyecto")
        nombre = indexador.validar_nombre(a.proyecto)
        if not (1 <= a.dias <= DIAS_ENLACE_MAX):
            sys.exit(f"pm-kb: --dias debe estar entre 1 y {DIAS_ENLACE_MAX} (por defecto {DIAS_ENLACE}): un enlace compartido vence en 90 días como máximo")
        x = c.execute("SELECT raiz, gestion FROM pmkb.indice WHERE proyecto = %s", (nombre,)).fetchone()
        if not x:
            sys.exit(f"pm-kb: el proyecto '{nombre}' no está indexado (pm-kb indexar --proyecto {nombre} --ruta CARPETA)")
        if x[1] is None:
            sys.exit(f"pm-kb: {x[0]} no tiene estado.json: sin tablero que compartir (no es un proyecto de pm-method)")
        if not c.execute("SELECT 1 FROM pmkb.tablero WHERE proyecto = %s", (nombre,)).fetchone():
            sys.exit(f"pm-kb: {nombre} no tiene tablero publicado (pm-kb tablero --proyecto {nombre})")
        alcance = "actual"
        if a.instantanea and a.instantanea != "actual":
            if not c.execute("SELECT 1 FROM pmkb.instantanea WHERE proyecto = %s AND id = %s", (nombre, a.instantanea)).fetchone():
                ids = [r[0] for r in c.execute("SELECT DISTINCT id, orden FROM pmkb.instantanea WHERE proyecto = %s ORDER BY orden", (nombre,)).fetchall()]
                sys.exit(f"pm-kb: {nombre} no tiene la instantánea '{a.instantanea}'. Instantáneas publicadas: {', '.join(ids) or 'ninguna'}")
            alcance = a.instantanea
        actor = actor_nombre = ""
        if a.actor is not None:
            try:
                ac = tablero.validar_actor(Path(x[0]) / x[1], a.actor)     # núcleo: tablero.py generar --actor (código 1 si no existe)
            except tablero.ErrorTablero as e:
                sys.exit(f"pm-kb: actor no válido: {str(e).split(': ', 1)[-1] if 'terminó con código' in str(e) else e}")
            actor = ac.get("id") or ac.get("nombre") or a.actor
            actor_nombre = (ac.get("nombre") or actor) + (f" ({ac['rol']})" if ac.get("rol") else "")
        try:
            eid, t, vence = crear_enlace(c, nombre, alcance, actor, actor_nombre, a.restringida, (a.para or "").strip()[:200], a.dias, _quien())
        except ValueError as e:
            sys.exit(f"pm-kb: {e}")
        origen, aviso = origen_enlaces()
        que = "al tablero actual (en vivo)" if alcance == "actual" else f"a la instantánea {alcance}"
        print(f"Enlace {eid} de solo lectura {que} de {nombre}" + (f", actor {actor_nombre}" if actor else "")
              + (", con circulación restringida" if a.restringida else "") + (f", para {a.para}" if a.para else "")
              + f"; vence {vence:%Y-%m-%d %H:%M %Z}. Se muestra UNA sola vez (la base guarda solo su huella); "
              f"para cortarlo antes: pm-kb compartir revocar --id {eid}")
        if aviso:
            print(aviso)
        print(f"{origen}/v#{t}")
    elif a.accion == "listar":
        filas = c.execute("""SELECT id, proyecto, alcance, actor_nombre, restringida, para, creado, creado_por, vence, revocado, usos, ultimo_uso,
                                    CASE WHEN revocado IS NOT NULL THEN 'revocado' WHEN vence <= now() THEN 'vencido' ELSE 'vigente' END
                             FROM pmkb.enlace WHERE %s::text IS NULL OR proyecto = %s ORDER BY creado""", (a.proyecto, a.proyecto)).fetchall()
        cols = ("id", "proyecto", "alcance", "actor", "restringida", "para", "creado", "creado_por", "vence", "revocado", "usos", "ultimo_uso", "estado")
        datos = [dict(zip(cols, f)) for f in filas]
        lineas = [f"  {x['id']} · {x['proyecto']} · {x['alcance']}" + (f" · actor {x['actor']}" if x["actor"] else "")
                  + (" · restringida" if x["restringida"] else "") + (f" · para {x['para']}" if x["para"] else "")
                  + f" · {x['estado']} · creado {x['creado']:%Y-%m-%d} por {x['creado_por'] or '—'} · vence {x['vence']:%Y-%m-%d %H:%M}"
                  + (f" · revocado {x['revocado']:%Y-%m-%d %H:%M}" if x["revocado"] else "")
                  + f" · {x['usos']} uso(s)" + (f", último {x['ultimo_uso']:%Y-%m-%d %H:%M}" if x["ultimo_uso"] else "") for x in datos]
        _sal(a, datos, "\n".join(lineas) if lineas else "pm-kb: sin enlaces compartidos" + (f" de {a.proyecto}" if a.proyecto else ""))
    elif a.accion == "revocar":
        if not a.id and not a.proyecto:
            sys.exit("pm-kb: compartir revocar necesita --id ID, o --proyecto P (todos sus enlaces vigentes, o solo los de --para)")
        with c.transaction():
            if a.id:
                ids = [r[0] for r in c.execute("UPDATE pmkb.enlace SET revocado = now() WHERE id = %s AND revocado IS NULL RETURNING id", (a.id,)).fetchall()]
            else:
                ids = [r[0] for r in c.execute("""UPDATE pmkb.enlace SET revocado = now() WHERE proyecto = %s AND revocado IS NULL
                                                   AND (%s::text IS NULL OR para = %s) RETURNING id""", (a.proyecto, a.para, a.para)).fetchall()]
            if ids:
                c.execute("DELETE FROM pmkb.sesion WHERE enlace = ANY(%s)", (ids,))
        print(f"pm-kb: {len(ids)} enlace(s) revocado(s)" + (f": {', '.join(ids)}" if ids else "") + " · las sesiones abiertas con ellos se cortan en la petición siguiente")


def cmd_db(a):
    import subprocess
    if not config.local():
        sys.exit("pm-kb db: solo para la instalación local (WSL2/Linux). Con Docker: docker compose -f docker/compose.yaml --profile kb …")
    sys.exit(subprocess.run(["bash", str(config.PG_SH), "local", a.accion]).returncode)


def cmd_servir(a):
    from . import web
    web.servir(a.host, a.puerto)


def cmd_mcp(a):
    from . import mcp
    mcp.stdio(proyectos=os.environ.get("PMKB_PROYECTOS", "*"), restringida=os.environ.get("PMKB_RESTRINGIDA", "no") == "si")


def cmd_verificar(a):
    """Prueba de punta a punta con un proyecto mínimo temporal (se borra al final)."""
    ok = True

    def paso(nombre, cond, detalle=""):
        nonlocal ok
        print(f"  {'OK   ' if cond else 'FALLO'} {nombre}" + (f" · {detalle}" if detalle else ""))
        ok = ok and bool(cond)

    print(f"pm-kb {VERSION} · verificación")
    for mod, req in (("psycopg", True), ("starlette", True), ("uvicorn", True), ("markitdown", False)):
        try:
            __import__(mod); paso(f"módulo {mod}", True)
        except ImportError:
            if req:
                paso(f"módulo {mod}", False, "pip install -r pm-kb/requirements.txt")
            else:
                print(f"  AVISO módulo {mod} no instalado: DOCX, PPTX, XLSX y PDF se omiten al indexar")
    from . import indexador
    from .busqueda import Sesion
    c = _admin()
    indexador.crear_esquema(c)
    v = c.execute("SELECT current_setting('server_version_num')::int, (SELECT extversion FROM pg_extension WHERE extname='vector')").fetchone()
    paso("PostgreSQL 16 o posterior", v[0] >= 160000, f"server_version_num {v[0]}")
    paso("extensión vector", bool(v[1]), f"pgvector {v[1]}")
    tmp = Path(tempfile.mkdtemp(prefix="pmkb-verificar-"))
    try:
        (tmp / "03-control" / "registros").mkdir(parents=True)
        (tmp / "estado.json").write_text(json.dumps({"proyecto": "Verificación", "fase": "entrega", "proceso_actual": "CS", "artefactos": {}}), encoding="utf-8")
        (tmp / "03-control" / "registros" / "riesgos.csv").write_text(
            "id,evento,respuesta,notas\nR-001,Demora del proveedor de mensajería,reducir,ver D-001\n", encoding="utf-8")
        (tmp / "03-control" / "registros" / "decisiones.csv").write_text(
            "id,fecha,decision,decidido_por,nivel\nD-001,2026-01-10,Contratar un segundo proveedor por R-001,Junta,junta\n", encoding="utf-8")
        (tmp / "acta.md").write_text("# Acta\n\n## Riesgos\n\nLas aprobaciones se demoran; ver R-001.\n", encoding="utf-8")
        (tmp / "reservado.md").write_text("---\ncirculacion: restringida\n---\n# Reservado\n\nSalarios de la negociación.\n", encoding="utf-8")
        p1, p2 = "zz-verificacion-a", "zz-verificacion-b"
        prep = indexador.preparar(tmp)
        indexador.cargar(c, p1, prep, con_vectores=False)
        indexador.cargar(c, p2, indexador.preparar(tmp), con_vectores=False)
        r = Sesion(c, "*", True).buscar("demoras de los proveedores", proyecto=p1)
        paso("búsqueda en español (flexión y tildes)", any(x["id"] == "R-001" for x in r["resultados"]), f"{len(r['resultados'])} resultados")
        f = Sesion(c, "*", True).ficha("R-001", proyecto=p1)
        paso("relaciones por id", any(x["id"] == "D-001" for x in f.get("relaciones", [])))
        try:
            l = config.conectar(lector=True)
        except Exception as x:
            paso("conexión del rol de lectura pmkb_lector", False, str(x)[:200]); l = None
        if l:
            paso("conexión del rol de lectura pmkb_lector", True)
            s = Sesion(l, p1, False)
            r = s.buscar("demoras proveedores")
            paso("RLS: el lector solo ve su proyecto", all(x["proyecto"] == p1 for x in r["resultados"]) and r["resultados"])
            r = s.buscar("salarios negociación")
            paso("RLS: sin circulación restringida no ve lo restringido", not r["resultados"])
            r = Sesion(l, p1, True).buscar("salarios negociación")
            paso("RLS: con circulación restringida lo ve", bool(r["resultados"]))
            legibles = []          # tokens, y también los hashes de los enlaces compartidos y de las sesiones web
            for tabla in ("acceso", "enlace", "sesion"):
                try:
                    with l.transaction():
                        l.execute(f"SELECT count(*) FROM pmkb.{tabla}").fetchone()
                    legibles.append(f"pmkb.{tabla}")
                except Exception:
                    pass
            paso("el lector no puede leer los tokens", not legibles, ", ".join(legibles))
            try:
                with l.transaction():
                    l.execute("DELETE FROM pmkb.unidad")
                paso("el lector no puede escribir", False)
            except Exception:
                paso("el lector no puede escribir", True)
            l.close()
        emb = config.embed()
        if emb:
            from . import modelos
            try:
                n = len(modelos.vectores(emb, ["prueba"])[0]); paso("modelo de vectores", n > 0, f"{emb['url']} · dimensión {n}")
            except RuntimeError as x:
                paso("modelo de vectores", False, str(x))
        llm = config.llm()
        if llm:
            print(f"  AVISO respuesta con modelo configurada ({llm['tipo']}, {llm['modelo']}); no se prueba para no consumir tokens")
    finally:
        indexador.quitar(c, "zz-verificacion-a"); indexador.quitar(c, "zz-verificacion-b")
        shutil.rmtree(tmp, ignore_errors=True)
    print("pm-kb: verificación " + ("completa sin fallos" if ok else "CON FALLOS"))
    sys.exit(0 if ok else 1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pm-kb", description=AYUDA, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"pm-kb {VERSION}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("base"); b.add_argument("accion", choices=["crear", "estado"]); b.set_defaults(f=cmd_base)
    i = sub.add_parser("indexar"); i.add_argument("--proyecto", required=True); i.add_argument("--ruta", required=True)
    i.add_argument("--excluir", action="append", default=[]); i.add_argument("--restringir", action="append", default=[])
    i.add_argument("--sin-vectores", action="store_true"); i.add_argument("--simular", action="store_true"); i.set_defaults(f=cmd_indexar)
    q = sub.add_parser("quitar"); q.add_argument("--proyecto", required=True); q.set_defaults(f=cmd_quitar)
    vg = sub.add_parser("vigilar"); vg.add_argument("--proyecto", required=True); vg.add_argument("--ruta", required=True)
    vg.add_argument("--cada", type=int, default=10, help="segundos entre comprobaciones (por defecto 10)")
    vg.add_argument("--ciclos", type=int, default=0, help="terminar después de N comprobaciones (0: hasta Ctrl+C)")
    vg.add_argument("--excluir", action="append", default=[]); vg.add_argument("--restringir", action="append", default=[])
    vg.add_argument("--sin-vectores", action="store_true"); vg.set_defaults(f=cmd_vigilar)
    en = sub.add_parser("enlaces"); en.add_argument("--proyecto", required=True); en.add_argument("--json", action="store_true")
    en.set_defaults(f=cmd_enlaces)
    tb = sub.add_parser("tablero"); tb.add_argument("--proyecto", required=True)
    tb.add_argument("--corte", help="fecha de corte AAAA-MM-DD para vencidas y edades (por defecto, hoy)")
    tb.add_argument("--json", action="store_true", help="imprime el tablero publicado (pm-tablero/1)"); tb.set_defaults(f=cmd_tablero)

    def comunes(p):
        p.add_argument("--proyecto"); p.add_argument("--json", action="store_true"); p.set_defaults(f=cmd_consulta)
    p = sub.add_parser("buscar"); p.add_argument("consulta"); p.add_argument("--k", type=int, default=5)
    p.add_argument("--aprobado", action="store_true"); p.add_argument("--historia", action="store_true")
    p.add_argument("--max-tokens", type=int, default=1500); p.add_argument("--tipo"); p.add_argument("--registro"); comunes(p)
    p = sub.add_parser("ficha"); p.add_argument("id"); p.add_argument("--historia", action="store_true"); comunes(p)
    p = sub.add_parser("relaciones"); p.add_argument("id"); p.add_argument("--saltos", type=int, default=1); comunes(p)
    p = sub.add_parser("versiones"); p.add_argument("doc"); comunes(p)
    p = sub.add_parser("cambios"); p.add_argument("doc"); p.add_argument("--desde"); p.add_argument("--hasta"); comunes(p)
    p = sub.add_parser("documento"); p.add_argument("ruta"); p.add_argument("--rango"); comunes(p)
    p = sub.add_parser("contexto"); p.add_argument("pregunta"); comunes(p)
    p = sub.add_parser("estado"); comunes(p)
    t = sub.add_parser("token"); t.add_argument("accion", choices=["crear", "listar", "revocar"]); t.add_argument("--persona")
    t.add_argument("--proyectos"); t.add_argument("--restringida", action="store_true")
    t.add_argument("--dias", type=int, default=DIAS_TOKEN, help=f"vencimiento en días (1–{DIAS_TOKEN_MAX}; por defecto {DIAS_TOKEN})")
    t.set_defaults(f=cmd_token)
    cp = sub.add_parser("compartir", help="enlaces de solo lectura a un tablero")
    cp.add_argument("accion", choices=["crear", "listar", "revocar"])
    cp.add_argument("--proyecto", help="proyecto indexado (crear; en listar y revocar, filtra)")
    cp.add_argument("--instantanea", metavar="ID", help="id de una instantánea congelada (por defecto, el tablero actual en vivo)")
    cp.add_argument("--actor", help="solo lo de esa persona (nombre, \"<rol: nombre>\", rol o ST-###), como tablero.py generar --actor")
    cp.add_argument("--dias", type=int, default=DIAS_ENLACE, help=f"vencimiento en días (1–{DIAS_ENLACE_MAX}; por defecto {DIAS_ENLACE})")
    cp.add_argument("--restringida", action="store_true", help="incluye lo de circulación restringida (por defecto, solo circulación de equipo)")
    cp.add_argument("--para", help="destinatario o nota (crear); en revocar, revoca los enlaces del proyecto con ese --para")
    cp.add_argument("--id", help="id del enlace (revocar), p. ej. e-1a2b3c4d")
    cp.add_argument("--json", action="store_true", help="listar en JSON (sin tokens)")
    cp.set_defaults(f=cmd_compartir)
    s = sub.add_parser("servir"); s.add_argument("--host", default="127.0.0.1"); s.add_argument("--puerto", type=int, default=8765)
    s.set_defaults(f=cmd_servir)
    m = sub.add_parser("mcp"); m.set_defaults(f=cmd_mcp)
    d = sub.add_parser("db"); d.add_argument("accion", choices=["iniciar", "detener", "estado", "reiniciar-datos"]); d.set_defaults(f=cmd_db)
    v = sub.add_parser("verificar"); v.set_defaults(f=cmd_verificar)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
