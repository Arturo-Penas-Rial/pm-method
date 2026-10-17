#!/bin/sh
# pm-method: ejecuta un script Python del plugin con el primer intérprete 3.9+ disponible (python3, python, py -3).
# Necesario en Windows, donde Claude Code corre los hooks con Git Bash y a menudo no existe "python3"
# (o es el alias de Microsoft Store, que no ejecuta nada). Sin Python, no bloquea: avisa por stderr y sale con 0.
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" </dev/null >/dev/null 2>&1; then
    exec "$c" "$@"
  fi
done
if command -v py >/dev/null 2>&1 && py -3 -c "import sys" </dev/null >/dev/null 2>&1; then
  exec py -3 "$@"
fi
echo "pm-method: no se encontró Python 3.9+ (python3, python o py); los hooks y scripts del plugin no funcionan. Ver docs/INSTALACION.md §1." >&2
exit 0
