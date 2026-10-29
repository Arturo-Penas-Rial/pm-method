"""Configuración por variables de entorno (nunca credenciales en archivos del repositorio). docs/PM-KB.md §8.

Conexión a PostgreSQL
  PMKB_DSN            conexión del dueño del índice (crear esquema, indexar, tokens). Por defecto, el clúster local de
                      `db/pg.sh local`: host=<PMKB_DATOS>/socket dbname=pmkb (usuario del sistema).
  PMKB_DSN_LECTOR     conexión del servicio (solo lectura, sujeta a RLS). Por defecto, la misma con user=pmkb_lector.
  PMKB_CLAVE_ARCHIVO / PMKB_CLAVE_LECTOR_ARCHIVO   archivos con la contraseña (Docker: /run/secrets/...).
Modelos (opcionales; sin ellos la búsqueda es léxica BM25 con sinónimos)
  PMKB_EMBED_URL, PMKB_EMBED_TIPO (tei | openai), PMKB_EMBED_MODELO   vectores
  PMKB_RERANK_URL                                                     re-ranqueo (TEI /rerank)
  PMKB_LLM_TIPO (anthropic | openai), PMKB_LLM_URL, PMKB_LLM_MODELO,
  PMKB_LLM_CLAVE_VAR  nombre de la variable que tiene la clave (por defecto ANTHROPIC_API_KEY u OPENAI_API_KEY)
Servicio
  PMKB_ORIGENES       orígenes web admitidos además del propio (separados por coma)
  PMKB_SINONIMOS      CSV opcional "termino,equivalente" que se suma a los sinónimos del paquete
"""
import os
from pathlib import Path


def datos():
    return Path(os.environ.get("PMKB_DATOS") or Path.home() / ".local" / "share" / "pm-kb")


def _clave(var):
    p = os.environ.get(var)
    if p and Path(p).is_file():
        return Path(p).read_text(encoding="utf-8").strip()
    return None


def dsn(lector=False):
    if lector:
        base = os.environ.get("PMKB_DSN_LECTOR")
        if not base:
            base = (os.environ.get("PMKB_DSN") or f"host={datos() / 'socket'} dbname=pmkb")
            base = " ".join(p for p in base.split() if not p.startswith("user=")) + " user=pmkb_lector"
        clave = _clave("PMKB_CLAVE_LECTOR_ARCHIVO")
    else:
        base = os.environ.get("PMKB_DSN") or f"host={datos() / 'socket'} dbname=pmkb"
        clave = _clave("PMKB_CLAVE_ARCHIVO")
    return base, clave


PG_SH = Path(__file__).resolve().parents[1] / "db" / "pg.sh"


def local():
    """True si se usa el clúster propio del usuario (instalación WSL2/Linux sin PMKB_DSN)."""
    return not os.environ.get("PMKB_DSN")


def iniciar_local():
    import subprocess
    r = subprocess.run(["bash", str(PG_SH), "local", "iniciar"], capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def conectar(lector=False, autocommit=True):
    """Conexión a PostgreSQL. En la instalación local, si el clúster no está en marcha (p. ej. tras reiniciar WSL), lo
    inicia una vez con db/pg.sh y reintenta."""
    import psycopg
    base, clave = dsn(lector)
    kw = {"password": clave} if clave else {}
    try:
        return psycopg.connect(base, autocommit=autocommit, connect_timeout=10, application_name="pm-kb", **kw)
    except psycopg.OperationalError:
        if not local() or not (datos() / "pg").is_dir():
            raise
        ok, salida = iniciar_local()
        if not ok:
            raise
        return psycopg.connect(base, autocommit=autocommit, connect_timeout=10, application_name="pm-kb", **kw)


def embed():
    url = os.environ.get("PMKB_EMBED_URL", "").rstrip("/")
    if not url:
        return None
    return {"url": url, "tipo": os.environ.get("PMKB_EMBED_TIPO", "tei"), "modelo": os.environ.get("PMKB_EMBED_MODELO", "")}


def rerank():
    url = os.environ.get("PMKB_RERANK_URL", "").rstrip("/")
    return {"url": url} if url else None


def llm():
    tipo = os.environ.get("PMKB_LLM_TIPO", "").lower()
    modelo = os.environ.get("PMKB_LLM_MODELO", "")
    if not tipo or not modelo:
        return None
    var = os.environ.get("PMKB_LLM_CLAVE_VAR") or ("ANTHROPIC_API_KEY" if tipo == "anthropic" else "OPENAI_API_KEY")
    url = os.environ.get("PMKB_LLM_URL", "").rstrip("/") or ("https://api.anthropic.com" if tipo == "anthropic" else "")
    if not url:
        return None
    return {"tipo": tipo, "url": url, "modelo": modelo, "clave": os.environ.get(var, "")}


def origenes():
    return [o.strip().rstrip("/") for o in os.environ.get("PMKB_ORIGENES", "").split(",") if o.strip()]
