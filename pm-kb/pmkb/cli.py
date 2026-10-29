"""Línea de comandos de pm-kb. `pm-kb --help` y docs/PM-KB.md §10."""
import argparse, hashlib, json, os, secrets, shutil, sys, tempfile, textwrap
from pathlib import Path

from . import VERSION, config, formato

AYUDA = """\
pm-kb: índice de conocimiento del proyecto (búsqueda citada para personas y agentes). Componente opcional de pm-method.

  pm-kb base crear | base estado                       esquema en PostgreSQL (idempotente) y su estado
  pm-kb indexar --proyecto NOMBRE --ruta CARPETA       indexa (reemplaza el índice de ese proyecto en una transacción)
         [--excluir GLOB]… [--restringir GLOB]… [--sin-vectores] [--simular]
  pm-kb quitar --proyecto NOMBRE                       borra el índice de un proyecto (la carpeta no se toca)
  pm-kb buscar "consulta" [--proyecto P] [--k 5] [--aprobado | --historia] [--tipo T] [--registro R] [--max-tokens N] [--json]
  pm-kb ficha ID [--historia] · relaciones ID [--saltos 1|2] · versiones DOC · cambios DOC [--desde V --hasta V]
  pm-kb documento RUTA [--rango L10-L40] · contexto "pregunta" · estado
  pm-kb token crear --persona "Nombre" --proyectos p1,p2|* [--restringida] · token listar · token revocar --persona "Nombre"
  pm-kb servir [--host 127.0.0.1] [--puerto 8765]      interfaz web y MCP por HTTP (/mcp), con token
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
        r = c.execute("""SELECT current_setting('server_version'), (SELECT valor FROM pmkb.meta WHERE clave = 'esquema'),
                         (SELECT string_agg(extname || ' ' || extversion, ', ' ORDER BY extname) FROM pg_extension WHERE extname IN ('vector','unaccent','pg_trgm')),
                         (SELECT count(*) FROM pmkb.indice)""").fetchone()
        print(f"PostgreSQL {r[0]} · esquema pm-kb {r[1]} · extensiones: {r[2]} · proyectos indexados: {r[3]}")


def cmd_indexar(a):
    from . import indexador
    nombre = indexador.validar_nombre(a.proyecto)
    prep = indexador.preparar(a.ruta, a.excluir, a.restringir)
    if a.simular:
        us = prep["unidades"]
        print(f"[simulación] {nombre}: {len(us)} unidades ({sum(u['vigente'] for u in us)} vigentes), {len(prep['documentos'])} documentos, "
              f"{len(prep['aristas'])} aristas, {len(prep['historia'])} entradas de historia, {len(prep['omitidos'])} omitidos; "
              f"carpeta de gestión: {prep['gestion'] if prep['gestion'] is not None else 'no encontrada'}")
        for f, m in prep["omitidos"][:20]:
            print(f"  omitido {f}: {m}")
        return
    c = _admin()
    r = indexador.cargar(c, nombre, prep, con_vectores=not a.sin_vectores)
    print(f"pm-kb: {nombre} indexado · {r['unidades']} unidades ({r['vigentes']} vigentes) · {r['documentos']} documentos "
          f"({r['con_versiones']} con varias versiones) · {r['aristas']} relaciones · {r['historia']} entradas de historia · "
          f"commit {r['commit'] or 'sin git'} · vectores: {r['modelo'] or 'no'}")
    if prep["gestion"] is None:
        print("  aviso: no hay estado.json en la carpeta (se indexó como documentación sin versiones de pm-method)")
    for f, m in prep["omitidos"][:20]:
        print(f"  omitido {f}: {m}")
    if len(prep["omitidos"]) > 20:
        print(f"  … y {len(prep['omitidos']) - 20} omitidos más (pm-kb estado)")


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


def crear_token(conn, persona, proyectos, restringida=False):
    t = "pmkb_" + secrets.token_urlsafe(32)
    with conn.transaction():
        conn.execute("INSERT INTO pmkb.acceso (token_sha, persona, proyectos, restringida) VALUES (%s, %s, %s, %s)",
                     (sha_token(t), persona, proyectos, restringida))
    return t


def cmd_token(a):
    c = _admin()
    if a.accion == "crear":
        if not a.persona or not a.proyectos:
            sys.exit("pm-kb: token crear necesita --persona y --proyectos (lista separada por comas, o * para todos)")
        t = crear_token(c, a.persona, a.proyectos.replace(" ", ""), a.restringida)
        print(f"Token para {a.persona} ({a.proyectos}{', con circulación restringida' if a.restringida else ''}). "
              "Se muestra UNA sola vez; guardalo en un gestor de contraseñas o en una variable de entorno:\n" + t)
    elif a.accion == "listar":
        for p, pr, r, cr, rv in c.execute("SELECT persona, proyectos, restringida, creado, revocado FROM pmkb.acceso ORDER BY creado"):
            print(f"  {p} · {pr}{' · restringida' if r else ''} · creado {cr:%Y-%m-%d}" + (f" · revocado {rv:%Y-%m-%d}" if rv else ""))
    elif a.accion == "revocar":
        with c.transaction():
            n = c.execute("UPDATE pmkb.acceso SET revocado = now() WHERE persona = %s AND revocado IS NULL", (a.persona,)).rowcount
        print(f"pm-kb: {n} token(s) revocado(s) de {a.persona}")


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
        (tmp / "estado.json").write_text(json.dumps({"nombre": "Verificación", "artefactos": {}}), encoding="utf-8")
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
            try:
                with l.transaction():
                    l.execute("SELECT count(*) FROM pmkb.acceso").fetchone()
                paso("el lector no puede leer los tokens", False)
            except Exception:
                paso("el lector no puede leer los tokens", True)
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
    t.add_argument("--proyectos"); t.add_argument("--restringida", action="store_true"); t.set_defaults(f=cmd_token)
    s = sub.add_parser("servir"); s.add_argument("--host", default="127.0.0.1"); s.add_argument("--puerto", type=int, default=8765)
    s.set_defaults(f=cmd_servir)
    m = sub.add_parser("mcp"); m.set_defaults(f=cmd_mcp)
    d = sub.add_parser("db"); d.add_argument("accion", choices=["iniciar", "detener", "estado", "reiniciar-datos"]); d.set_defaults(f=cmd_db)
    v = sub.add_parser("verificar"); v.set_defaults(f=cmd_verificar)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
