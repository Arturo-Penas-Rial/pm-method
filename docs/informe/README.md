# Informe 2 · Documentación del ecosistema pm-method (v2.2)

- `informe-2-ecosistema-pm-method-v2.2.html` y `.pptx`: el informe (mismo contenido, 219 diapositivas), generado desde
  la documentación de este repositorio (versión 2.2.0). Incluye resumen ejecutivo, novedades de la versión 2.2 (antes y
  después 2.1.0 → 2.2.0, maestro de interesados, capa de canales, OKR v2.2, riesgos desde cuatro fuentes, controles
  permanentes y guías E2E actualizadas), diagramas, arquitectura, columna vertebral BMAD ↔ PRINCE2, sanidad, puertas de
  la junta (verificación y registro), dependencias con URL de origen, instalación y configuración, catálogo, RACI, casos
  de uso por skill y por repositorio integrado, caso maestro, pruebas, índice y glosario.
- `fuente/`: el generador. Regenerar después de cambiar la documentación:

```bash
cd docs/informe/fuente
npm install pptxgenjs                      # una vez (o tenerlo global y usar NODE_PATH=$(npm root -g))
python3 extraer.py                         # lee README, CHANGELOG, SPEC, docs/ (incluidas las guías) y compatibilidad.json → data.json y diagramas
python3 build_html.py                      # → salida-v2.2/informe-2-ecosistema-pm-method-v2.2.html
node build_pptx.js                         # → salida-v2.2/informe-2-ecosistema-pm-method-v2.2.pptx
```

Requiere Python 3.9+ con Pillow (recortes de las capturas del reporte de interesados), Node.js y `mmdc`
(`@mermaid-js/mermaid-cli`) en el `PATH`; si `mmdc` no encuentra Chromium, definir `PUPPETEER_CFG=<json con
executablePath>`. Luego copiar los dos archivos de `salida-v2.2/` a esta carpeta.
Control de calidad: `python3 qa_html.py` (requiere Playwright) y `sh qa_pptx.sh` (requiere LibreOffice y poppler).
El texto propio del informe vive en `fuente/narrativa.json` (incluida la clave `v22` con las tablas de la versión 2.2);
el resto se extrae literalmente de la documentación.
El logo de IEEE es opcional (`logo.png` junto a los scripts); no se aplica ninguna otra marca.
