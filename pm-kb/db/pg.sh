#!/usr/bin/env bash
# PostgreSQL de pm-kb, el mismo guion para los dos caminos de instalación (docs/PM-KB.md §7):
#   pg.sh local iniciar|detener|estado   WSL2/Linux: clúster propio del usuario, solo por socket local (sin puerto TCP,
#                                        sin systemd, sin tocar otro PostgreSQL); datos en ${PMKB_DATOS:-~/.local/share/pm-kb}
#   pg.sh docker                         punto de entrada de la imagen pm-kb-db (contenedor segregado, red interna,
#                                        contraseñas desde /run/secrets; nunca en variables ni en la imagen)
set -euo pipefail

BIN="${PMKB_PG_BIN:-$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)}"
if [ -z "$BIN" ] || [ ! -x "$BIN/initdb" ]; then
  echo "pm-kb: no se encontró PostgreSQL (/usr/lib/postgresql/<versión>/bin). Instalar: sudo apt install postgresql" >&2
  exit 2
fi
export PATH="$BIN:$PATH"
BASE="${PMKB_BASE:-pmkb}"

crear_base_y_roles() {   # $1 = opciones de psql; $2 = dueño de la base
  local PSQL="psql $1 -v ON_ERROR_STOP=1 -qAt"
  $PSQL -d postgres -c "SELECT 1 FROM pg_roles WHERE rolname='pmkb_lector'" | grep -q 1 \
    || $PSQL -d postgres -c "CREATE ROLE pmkb_lector LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT"
  $PSQL -d postgres -c "SELECT 1 FROM pg_database WHERE datname='$BASE'" | grep -q 1 \
    || $PSQL -d postgres -c "CREATE DATABASE $BASE OWNER \"$2\" ENCODING 'UTF8' TEMPLATE template0"
  # extensiones creadas por el superusuario del clúster: el dueño del índice no necesita privilegios especiales
  $PSQL -d "$BASE" -c "CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public; CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public; CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;"
  $PSQL -d "$BASE" -c "REVOKE CREATE ON SCHEMA public FROM PUBLIC; GRANT CONNECT ON DATABASE $BASE TO pmkb_lector;"
}

local_cmd() {
  local DATOS="${PMKB_DATOS:-$HOME/.local/share/pm-kb}"
  local PGD="$DATOS/pg" SOCK="$DATOS/socket" LOG="$DATOS/postgresql.log"
  case "${1:-}" in
    iniciar)
      mkdir -p "$DATOS" "$SOCK"; chmod 700 "$DATOS" "$SOCK"
      if [ ! -s "$PGD/PG_VERSION" ]; then
        initdb -D "$PGD" -U "$(id -un)" --auth=trust -E UTF8 --locale=C.UTF-8 >"$DATOS/initdb.log" 2>&1 \
          || { echo "pm-kb: initdb falló; ver $DATOS/initdb.log" >&2; exit 1; }
        cat >>"$PGD/postgresql.conf" <<EOF
# pm-kb: solo socket local en una carpeta privada (0700); sin TCP
listen_addresses = ''
unix_socket_directories = '$SOCK'
unix_socket_permissions = 0700
shared_buffers = 128MB
EOF
      elif [ "$(cat "$PGD/PG_VERSION")" != "$(basename "$(dirname "$BIN")")" ]; then
        echo "pm-kb: los datos son de PostgreSQL $(cat "$PGD/PG_VERSION") y el instalado es $(basename "$(dirname "$BIN")")." >&2
        echo "       El índice es derivado: 'pm-kb db reiniciar-datos' borra $PGD y luego 'pm-kb indexar' lo reconstruye." >&2
        exit 1
      fi
      if pg_ctl -D "$PGD" status >/dev/null 2>&1; then echo "pm-kb: PostgreSQL ya estaba en marcha ($SOCK)"; else
        pg_ctl -D "$PGD" -l "$LOG" -w -t 60 start >/dev/null || { echo "pm-kb: no arrancó; ver $LOG" >&2; exit 1; }
        echo "pm-kb: PostgreSQL en marcha (socket $SOCK)"
      fi
      crear_base_y_roles "-h $SOCK" "$(id -un)"
      ;;
    detener) pg_ctl -D "$PGD" -m fast -w stop >/dev/null 2>&1 && echo "pm-kb: PostgreSQL detenido" || echo "pm-kb: no estaba en marcha" ;;
    estado)
      if pg_ctl -D "$PGD" status >/dev/null 2>&1; then echo "en marcha · socket $SOCK · datos $PGD"; else echo "detenido · datos $PGD"; exit 3; fi ;;
    reiniciar-datos)
      pg_ctl -D "$PGD" -m fast -w stop >/dev/null 2>&1 || true
      rm -rf "$PGD"; echo "pm-kb: datos borrados ($PGD); correr 'pm-kb base crear' y 'pm-kb indexar'" ;;
    *) echo "uso: pg.sh local iniciar|detener|estado|reiniciar-datos" >&2; exit 64 ;;
  esac
}

docker_cmd() {
  local PGD="${PGDATA:-/var/lib/postgresql/data}" S=/run/secrets
  for f in pmkb_admin_clave pmkb_lector_clave; do
    [ -s "$S/$f" ] || { echo "pm-kb-db: falta el secreto $S/$f (docker/kb-secretos/; ver docs/INSTALACION-DOCKER.md)" >&2; exit 1; }
  done
  if [ ! -s "$PGD/PG_VERSION" ]; then
    initdb -D "$PGD" -U postgres --auth-local=peer --auth-host=scram-sha-256 -E UTF8 --locale=C.UTF-8 >/tmp/initdb.log 2>&1 \
      || { cat /tmp/initdb.log >&2; exit 1; }
    cat >"$PGD/pg_hba.conf" <<'EOF'
# pm-kb-db: superusuario solo por socket dentro del contenedor; la red interna solo para los dos roles del índice
local   all     postgres                    peer
host    pmkb    pmkb,pmkb_lector  0.0.0.0/0 scram-sha-256
host    pmkb    pmkb,pmkb_lector  ::/0      scram-sha-256
EOF
    printf "\n# pm-kb-db\npassword_encryption = scram-sha-256\nshared_buffers = 256MB\n" >>"$PGD/postgresql.conf"
  fi
  # arranque temporal sin red, en otro socket (el chequeo de salud mira /tmp), para crear o actualizar roles y
  # contraseñas (rotación: cambiar el secreto y reiniciar el contenedor)
  mkdir -p /tmp/inicio
  pg_ctl -D "$PGD" -o "-c listen_addresses='' -c unix_socket_directories=/tmp/inicio" -w -t 60 start >/dev/null
  local PSQL="psql -h /tmp/inicio -U postgres -v ON_ERROR_STOP=1 -qAt"
  $PSQL -d postgres -c "SELECT 1 FROM pg_roles WHERE rolname='pmkb'" | grep -q 1 \
    || $PSQL -d postgres -c "CREATE ROLE pmkb LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE"
  crear_base_y_roles "-h /tmp/inicio -U postgres" pmkb
  $PSQL -d postgres -v a="$(cat $S/pmkb_admin_clave)" -v l="$(cat $S/pmkb_lector_clave)" <<'EOF'
ALTER ROLE pmkb PASSWORD :'a';
ALTER ROLE pmkb_lector PASSWORD :'l';
EOF
  pg_ctl -D "$PGD" -m fast -w stop >/dev/null
  exec postgres -D "$PGD" -c listen_addresses='*' -c unix_socket_directories=/tmp
}

case "${1:-}" in
  local) shift; local_cmd "$@" ;;
  docker) docker_cmd ;;
  *) echo "uso: pg.sh local iniciar|detener|estado|reiniciar-datos | pg.sh docker" >&2; exit 64 ;;
esac
