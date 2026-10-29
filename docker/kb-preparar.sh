#!/usr/bin/env bash
# Prepara el perfil "kb" de docker/compose.yaml (pm-kb): genera las dos contraseñas de la base segregada como secretos
# de Docker en docker/kb-secretos/ (carpeta 0700, fuera de git y de la imagen) y la carpeta vacía por defecto de
# proyectos. Idempotente: no pisa secretos existentes. Guía: docs/INSTALACION-DOCKER.md §8.
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
umask 077
mkdir -p "$D/kb-secretos" "$D/kb-sin-proyectos"
chmod 700 "$D/kb-secretos"
for f in pmkb_admin_clave pmkb_lector_clave; do
  if [ -s "$D/kb-secretos/$f" ]; then echo "existe: docker/kb-secretos/$f (no se modifica)"; continue; fi
  python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > "$D/kb-secretos/$f"
  # 0644 dentro de una carpeta 0700: solo tu usuario llega al archivo en el host, y los usuarios sin privilegios de
  # los contenedores (postgres y pm) pueden leer el secreto montado
  chmod 644 "$D/kb-secretos/$f"
  echo "creado: docker/kb-secretos/$f"
done
echo "Listo. Siguiente: docker compose -f docker/compose.yaml --profile kb build && docker compose -f docker/compose.yaml --profile kb up -d pm-kb"
