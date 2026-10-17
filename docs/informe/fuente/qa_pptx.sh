#!/bin/sh
# Render del deck a PDF (LibreOffice) y PNG a 50 dpi, grillas 2x2 numeradas y control de texto fuera de la zona de contenido.
# Uso: qa_pptx.sh [pptx] [carpeta]   (por defecto: salida-v2.1/informe-2-ecosistema-pm-method-v2.1.pptx  qa-pptx/)
P=${1:-salida-v2.1/informe-2-ecosistema-pm-method-v2.1.pptx}; Q=${2:-qa-pptx}
rm -rf "$Q" && mkdir -p "$Q"
soffice --headless --convert-to pdf --outdir "$Q" "$P" >/dev/null 2>&1
PDF=$(ls "$Q"/*.pdf)
pdftoppm -r 50 -png "$PDF" "$Q/s"
python3 - "$Q" "$PDF" <<'PY'
import sys, glob, re, html, subprocess
from PIL import Image, ImageDraw
Q, pdf = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(Q + '/s-*.png')); print(len(fs), "diapositivas")
for k in range(0, len(fs), 4):
    ims = [Image.open(f) for f in fs[k:k+4]]; w, h = ims[0].size
    sh = Image.new('RGB', (2*w+8, 2*h+8), '#777')
    for i, im in enumerate(ims):
        sh.paste(im, ((i % 2)*(w+8), (i//2)*(h+8)))
        ImageDraw.Draw(sh).text(((i % 2)*(w+8)+4, (i//2)*(h+8)+2), str(k+i+1), fill='red')
    sh.save(f'{Q}/q{k//4:02d}.png')
# texto por debajo del área de contenido (pie excluido) o fuera de los márgenes laterales
out = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
malas = []
for i, p in enumerate(out.split("<page ")[1:], 1):
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">', p):
        x0, y0, x1, y1 = map(float, m.groups())
        if i == 1 or (y0 >= 500 and y1 <= 530 and (x0 < 655 or x0 > 860)):
            continue
        if y1 > 500 or x1 > 925 or x0 < 30:
            malas.append(i); break
print("diapositivas con texto fuera de la zona de contenido:", malas or "ninguna")
PY
