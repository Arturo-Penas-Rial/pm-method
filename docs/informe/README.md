# Informe 2 · Documentación del ecosistema pm-method (v2.1)

- `informe-2-ecosistema-pm-method-v2.1.html` y `.pptx`: el informe (mismo contenido, 173 diapositivas), generado desde
  la documentación de este repositorio. Incluye resumen ejecutivo, diagramas, arquitectura, columna vertebral BMAD ↔
  PRINCE2, sanidad, puertas de la junta (verificación y registro), dependencias con URL de origen, instalación y configuración, catálogo, RACI, casos de uso por skill
  y por repositorio integrado, caso maestro, pruebas, índice y glosario.
- `fuente/`: el generador. Regenerar después de cambiar la documentación:

```bash
cd docs/informe/fuente
npm install pptxgenjs                      # una vez (o tenerlo global y usar NODE_PATH=$(npm root -g))
python3 extraer.py                         # lee README, SPEC, docs/ y compatibilidad.json → data.json y diagramas
python3 build_html.py                      # → salida-v2.1/informe-2-ecosistema-pm-method-v2.1.html
node build_pptx.js                         # → salida-v2.1/informe-2-ecosistema-pm-method-v2.1.pptx
```

Requiere Python 3.9+, Node.js y `mmdc` (`@mermaid-js/mermaid-cli`) en el `PATH`; si `mmdc` no encuentra Chromium,
definir `PUPPETEER_CFG=<json con executablePath>`. Luego copiar los dos archivos de `salida-v2.1/` a esta carpeta.
Control de calidad: `python3 qa_html.py` y `sh qa_pptx.sh` (requiere LibreOffice y poppler).
El logo de IEEE es opcional (`logo.png` junto a los scripts); no se aplica ninguna otra marca.
