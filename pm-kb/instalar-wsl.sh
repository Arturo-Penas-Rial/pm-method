#!/usr/bin/env bash
# Instalación de pm-kb en WSL2 con Ubuntu 24.04 o 26.04 (o Ubuntu nativo). Idempotente: se puede volver a ejecutar.
# Guía: docs/INSTALACION-WSL2.md §8 y referencia docs/PM-KB.md §7.
#
# Qué hace (y por qué):
#   1. Paquetes de Ubuntu (repositorios oficiales, sin repositorios de terceros): PostgreSQL de la distribución, su
#      extensión pgvector (postgresql-<versión>-pgvector) y python3-venv. Si no hay ningún clúster de PostgreSQL todavía,
#      desactiva el clúster "main" automático del sistema: pm-kb usa uno propio del usuario.
#   2. Entorno virtual propio en ~/.local/share/pm-kb/venv con dependencias fijadas por hash (pm-kb/requirements.txt).
#   3. Comando ~/.local/bin/pm-kb (enlace al lanzador del repositorio).
#   4. Clúster de PostgreSQL del usuario, solo por socket en una carpeta privada (sin puerto TCP ni systemd); esquema y
#      prueba de punta a punta (pm-kb verificar).
# Opciones: --si (sin preguntas) · --sin-apt (no instala paquetes del sistema: ya están).
set -euo pipefail

SI=0; SIN_APT=0
for x in "$@"; do
  case "$x" in --si) SI=1 ;; --sin-apt) SIN_APT=1 ;; -h|--help) sed -n 2,14p "$0"; exit 0 ;; *) echo "opción desconocida: $x" >&2; exit 64 ;; esac
done
DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DATOS="${PMKB_DATOS:-$HOME/.local/share/pm-kb}"
VENV="$DATOS/venv"
paso() { printf '\n== %s\n' "$*"; }
falla() { printf '\npm-kb: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -ne 0 ] || falla "ejecutar como tu usuario, no como root (sudo se pide solo para apt)."
[ -r /etc/os-release ] && . /etc/os-release || true
if [ "${ID:-}" != "ubuntu" ]; then echo "AVISO: probado en Ubuntu 24.04 y 26.04; este sistema es ${PRETTY_NAME:-desconocido}."; fi
command -v python3 >/dev/null || falla "falta python3 (sudo apt install python3)."
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' \
  || falla "pm-kb necesita Python 3.11 o posterior (Ubuntu 24.04 trae 3.12)."

paso "1/4 Paquetes del sistema"
if [ "$SIN_APT" -eq 0 ]; then
  if ! apt-cache policy postgresql 2>/dev/null | grep -q "Candidate: [0-9]"; then sudo apt-get update; fi
  CAND="$(apt-cache policy postgresql | awk '/Candidate:/ {print $2}')"
  V="${CAND%%+*}"
  [[ "$V" =~ ^[0-9]+$ ]] || falla "no se pudo determinar la versión de PostgreSQL de Ubuntu (Candidate: '$CAND')."
  PAQ="postgresql-$V postgresql-$V-pgvector python3-venv"
  echo "Se instalará: postgresql-common $PAQ (repositorios de Ubuntu; PostgreSQL $V)."
  if [ "$SI" -eq 0 ]; then read -r -p "¿Continuar? [s/N] " r; [[ "$r" =~ ^[sSyY] ]] || falla "cancelado."; fi
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-common
  if [ -z "$(ls -A /etc/postgresql 2>/dev/null)" ] && [ -f /etc/postgresql-common/createcluster.conf ]; then
    # sin clústeres previos: que apt no cree ni arranque el clúster "main" del sistema (pm-kb usa uno propio)
    sudo sed -i -E 's/^#?[[:space:]]*create_main_cluster[[:space:]]*=.*/create_main_cluster = false/' /etc/postgresql-common/createcluster.conf
    echo "create_main_cluster = false en /etc/postgresql-common/createcluster.conf (no había clústeres)."
  fi
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y $PAQ
else
  echo "omitido (--sin-apt)"
fi
ls -d /usr/lib/postgresql/*/bin >/dev/null 2>&1 || falla "no está PostgreSQL (/usr/lib/postgresql/<versión>/bin)."
PGV="$(ls -d /usr/lib/postgresql/*/bin | sort -V | tail -1 | awk -F/ '{print $5}')"
[ -f "/usr/share/postgresql/$PGV/extension/vector.control" ] || falla "falta pgvector para PostgreSQL $PGV (sudo apt install postgresql-$PGV-pgvector)."
echo "PostgreSQL $PGV con pgvector: listo."

paso "2/4 Entorno virtual y dependencias (fijadas por hash)"
mkdir -p "$DATOS"; chmod 700 "$DATOS"
if [ ! -x "$VENV/bin/python" ]; then python3 -m venv "$VENV" || falla "no se pudo crear el entorno virtual (sudo apt install python3-venv)."; fi
"$VENV/bin/python" -m pip install --disable-pip-version-check -q --require-hashes --only-binary=:all: -r "$DIR/requirements.txt" \
  || falla "pip no pudo instalar las dependencias. Con proxy corporativo: exportar HTTPS_PROXY y PIP_CERT (docs/INSTALACION-WSL2.md §8.9)."
"$VENV/bin/python" -c "import psycopg, starlette, uvicorn, markitdown" || falla "las dependencias no quedaron importables."
echo "Entorno: $VENV"

paso "3/4 Comando pm-kb"
mkdir -p "$HOME/.local/bin"
chmod +x "$DIR/pm-kb" "$DIR/db/pg.sh"     # por si el clon perdió el permiso de ejecución (p. ej. publicado desde Windows)
ln -sfn "$DIR/pm-kb" "$HOME/.local/bin/pm-kb"
mkdir -p "$HOME/.config/pm-kb"; chmod 700 "$HOME/.config/pm-kb"
if [ ! -f "$HOME/.config/pm-kb/pm-kb.env" ]; then
  cat >"$HOME/.config/pm-kb/pm-kb.env" <<'EOF'
# Configuración de pm-kb sin secretos (docs/PM-KB.md §8). Las claves de modelos van solo en variables de la sesión.
# PMKB_EMBED_URL=http://localhost:8080        # Text Embeddings Inference con BAAI/bge-m3 (opcional)
# PMKB_EMBED_TIPO=tei
# PMKB_RERANK_URL=http://localhost:8081       # TEI con BAAI/bge-reranker-v2-m3 (opcional)
# PMKB_LLM_TIPO=anthropic                     # o openai (compatible: Ollama en http://localhost:11434/v1)
# PMKB_LLM_MODELO=                            # nombre exacto del modelo del proveedor
EOF
  chmod 600 "$HOME/.config/pm-kb/pm-kb.env"
fi
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "AVISO: ~/.local/bin no está en el PATH de esta terminal: cerrar y abrir Ubuntu (el .profile de Ubuntu lo agrega)." ;; esac

paso "4/4 PostgreSQL del usuario, esquema y verificación"
"$DIR/pm-kb" db iniciar
"$DIR/pm-kb" base crear
"$DIR/pm-kb" verificar

cat <<EOF

pm-kb instalado. Próximos pasos (docs/INSTALACION-WSL2.md §8):
  pm-kb indexar --proyecto mi-proyecto --ruta ~/proyectos/mi-proyecto     # carpeta con gestion/ (y _bmad-output/ si hay)
  pm-kb servir                                                           # interfaz web: abre el enlace que muestra
  claude mcp add --scope user pm-kb -- $HOME/.local/bin/pm-kb mcp         # MCP para Claude Code
EOF
