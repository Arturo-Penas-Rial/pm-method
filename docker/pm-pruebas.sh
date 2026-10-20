#!/bin/bash
# pm-pruebas: corre dentro del contenedor las pruebas gratuitas de pm-method (no consume tokens ni sale a la red).
# Uso: pm-pruebas [--salida DIR]      (por defecto DIR = /tmp/pm-pruebas; montar un volumen para conservarla)
# Código de salida 1 si falla alguna prueba. Ver docs/DOCKER.md §4.
set -u
R="${PM_METHOD_DIR:-/opt/pm-method}"
SALIDA="/tmp/pm-pruebas"
while [ $# -gt 0 ]; do
  case "$1" in
    --salida) SALIDA="$2"; shift 2 ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    *) echo "argumento desconocido: $1" >&2; exit 2 ;;
  esac
done
mkdir -p "$SALIDA"
fallos=0
resumen=""

# paso <nombre> <archivo de registro> <comando…>; un paso falla si el comando devuelve != 0.
paso() {
  local nombre="$1" log="$SALIDA/$2"; shift 2
  local t0=$SECONDS
  echo "== $nombre"
  if "$@" >"$log" 2>&1; then estado="OK"; else estado="FALLO"; fallos=$((fallos + 1)); fi
  tail -n 3 "$log" | sed 's/^/   /'
  resumen="${resumen}$(printf '%-6s %-44s %4ss  %s' "$estado" "$nombre" "$((SECONDS - t0))" "$log")\n"
}

paso "claude --version"                       01-claude-version.log      claude --version
paso "claude plugin validate"                 01b-plugin-validate.log    claude plugin validate "$R"
paso "validar_paquete.py"                     02-validar-paquete.log     python3 "$R/scripts/validar_paquete.py"
paso "probar_paquete.py"                      03-probar-paquete.log      python3 "$R/scripts/probar_paquete.py"
paso "guias_e2e/correr.py"                    04-guias-e2e.log           python3 "$R/scripts/pruebas/guias_e2e/correr.py" --salida "$SALIDA/guias"
paso "integracion/correr.py (cadenas 1-6)"    04b-integracion.log        python3 "$R/scripts/pruebas/integracion/correr.py" --e2e "$SALIDA/guias" --json "$SALIDA/integracion.json"
paso "validar_mermaid.py --render"            05-validar-mermaid.log     python3 "$R/scripts/validar_mermaid.py" --render
paso "webinar/generar.py --todos --validar"   06-webinar-validar.log     python3 "$R/scripts/webinar/generar.py" --todos --validar
paso "webinar/generar.py --todos (HTML+PPTX)" 07-webinar-generar.log     python3 "$R/scripts/webinar/generar.py" --todos --salida "$SALIDA/webinar"

# Comprobaciones adicionales sobre las salidas (el texto exacto que imprimen los scripts).
# Compatibilidad con Python 3.9: la hace validar_paquete.py (sin intérprete 3.9 en la imagen, con su análisis de f-strings).
if grep -q "^Python 3.9: .* verificados" "$SALIDA/02-validar-paquete.log" && ! grep -q "incompatible con Python 3.9" "$SALIDA/02-validar-paquete.log"; then
  resumen="${resumen}$(printf '%-6s %-44s %4s   %s' OK "compatibilidad con Python 3.9 (sintaxis)" "-" "$SALIDA/02-validar-paquete.log")\n"
else
  echo "FALLO: compatibilidad con Python 3.9"; fallos=$((fallos + 1))
  resumen="${resumen}$(printf '%-6s %-44s %4s   %s' FALLO "compatibilidad con Python 3.9 (sintaxis)" "-" "$SALIDA/02-validar-paquete.log")\n"
fi
if grep -q "AVISO mmdc no está instalado" "$SALIDA/05-validar-mermaid.log"; then
  echo "FALLO: validar_mermaid no encontró mmdc"; fallos=$((fallos + 1))
fi
if ! ls "$SALIDA"/guias/*.png >/dev/null 2>&1; then
  echo "AVISO: los recorridos E2E no generaron capturas PNG (¿playwright?)"
fi

echo
echo "Resumen (salida en $SALIDA):"
printf "%b" "$resumen"
if [ "$fallos" -eq 0 ]; then echo "Resultado: todas las pruebas OK"; else echo "Resultado: $fallos prueba(s) con FALLO"; fi
exit $((fallos > 0))
