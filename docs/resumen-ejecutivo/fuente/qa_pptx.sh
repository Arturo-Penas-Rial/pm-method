#!/bin/sh
# QA visual del PPTX: PDF con LibreOffice, PNG por diapositiva (pdftoppm) y control de texto fuera de la zona de contenido.
# Uso: sh qa_pptx.sh CARPETA_DE_SALIDA   (por defecto, una carpeta temporal; nunca dentro del repositorio)
AQUI=$(cd "$(dirname "$0")" && pwd)
P="$AQUI/../resumen-ejecutivo-pm-method.pptx"
Q=${1:-$(mktemp -d)}
rm -rf "$Q" && mkdir -p "$Q"
SOFF=/mnt/skills/public/pptx/scripts/office/soffice.py
if [ -f "$SOFF" ]; then python3 "$SOFF" --headless --convert-to pdf --outdir "$Q" "$P" >/dev/null 2>&1
else soffice --headless --convert-to pdf --outdir "$Q" "$P" >/dev/null 2>&1; fi
PDF=$(ls "$Q"/*.pdf)
pdftoppm -r 80 -png "$PDF" "$Q/s"
python3 - "$PDF" <<'PY'
import sys, re, subprocess
pdf = sys.argv[1]
out = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
paginas = out.split("<page ")[1:]
print(len(paginas), "diapositivas")
malas = []
for i, p in enumerate(paginas, 1):
    w = float(re.search(r'width="([\d.]+)"', p).group(1)); h = float(re.search(r'height="([\d.]+)"', p).group(1))
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">', p):
        x0, y0, x1, y1 = map(float, m.groups())
        if x1 > w - 20 or x0 < 20 or y1 > h - 8:
            malas.append(i); break
print("diapositivas con texto fuera del área segura:", malas or "ninguna")
PY
echo "PNG en $Q"
