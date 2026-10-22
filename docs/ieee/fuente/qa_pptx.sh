#!/bin/sh
# QA visual de los dos PPTX: PDF con LibreOffice, PNG por diapositiva (pdftoppm) y texto fuera del área segura.
# Uso: sh qa_pptx.sh CARPETA_DE_SALIDA   (por defecto, una carpeta temporal; nunca dentro del repositorio)
AQUI=$(cd "$(dirname "$0")" && pwd)
Q=${1:-$(mktemp -d)}
rm -rf "$Q" && mkdir -p "$Q"
SOFF=/mnt/skills/public/pptx/scripts/office/soffice.py
for N in resumen informe; do
  P="$AQUI/../pm-method-ieee-$N-light.pptx"
  mkdir -p "$Q/$N"
  if [ -f "$SOFF" ]; then python3 "$SOFF" --headless --convert-to pdf --outdir "$Q/$N" "$P" >/dev/null 2>&1
  else soffice --headless --convert-to pdf --outdir "$Q/$N" "$P" >/dev/null 2>&1; fi
  PDF=$(ls "$Q/$N"/*.pdf)
  pdftoppm -r 110 -png "$PDF" "$Q/$N/s" 2>/dev/null
  python3 - "$PDF" "$N" <<'PY'
import sys, re, subprocess
pdf, nombre = sys.argv[1], sys.argv[2]
out = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
paginas = out.split("<page ")[1:]
malas = []
for i, p in enumerate(paginas, 1):
    w = float(re.search(r'width="([\d.]+)"', p).group(1)); h = float(re.search(r'height="([\d.]+)"', p).group(1))
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">', p):
        x0, y0, x1, y1 = map(float, m.groups())
        if x1 > w - 20 or x0 < 20 or y1 > h - 8:
            malas.append(i); break
print(f"{nombre}: {len(paginas)} diapositivas · texto fuera del área segura: {malas or 'ninguna'}")
PY
done
echo "PNG en $Q"
