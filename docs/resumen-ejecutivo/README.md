# Resumen ejecutivo comercial · pm-method

- `resumen-ejecutivo-pm-method.pptx` y `.html`: el resumen para presentar y vender pm-method (mismo contenido en los dos
  formatos; 21 diapositivas): problema y propuesta de valor, para quién, qué es, arquitectura (con pm-kb, opcional), agentes y
  skills por fase, ciclo de vida con las puertas, controles permanentes, decidir con contexto, controlar cada escritura y
  buscar en los proyectos con evidencia citada, integraciones, catálogo de los casos E2E (uno por diapositiva, con una imagen
  real de cada guía), webinar e inducción, calidad y confianza, comparativo honesto con PMI Infinity y la gestión
  tradicional (tabla breve, cuándo conviene cada uno y lo que pm-method no hace; la tabla completa con fuentes está en
  `docs/RESUMEN-EJECUTIVO.md` §9), cómo empezar y glosario. El HTML es un solo archivo
  (claro, oscuro o automático; imprimible, una diapositiva por página; navegación con ◀ ▶ y las flechas del teclado;
  glosario con anclas).
- `fuente/`: el generador. **Ninguna cifra está escrita a mano**: `extraer.py` cuenta skills, agentes, hooks, registros,
  puertas, códigos de control, casos y sus pasos (con el mismo criterio de `docs/guias/README.md`, y se detiene si no
  coinciden) en el repositorio, corre las pruebas gratuitas y guarda todo en `datos.json`; el
  texto propio vive en `fuente/narrativa.json` con marcadores `{clave}` que se completan con esas cifras.

## Regenerar

Desde esta carpeta (`docs/resumen-ejecutivo/`):

```bash
cd fuente
python3 extraer.py          # cuenta, corre validar_paquete, probar_paquete, guias_e2e/correr y validar_mermaid (≈ 5 min) y dibuja el diagrama
python3 build_html.py       # → ../resumen-ejecutivo-pm-method.html
node build_pptx.js          # → ../resumen-ejecutivo-pm-method.pptx
```

`python3 extraer.py --reusar-pruebas` reusa los resultados de pruebas del `datos.json` anterior (solo para iterar el
diseño; para publicar, correr sin la opción). `VERSION=X.Y.Z python3 extraer.py` hace que el material declare esa versión
cuando se genera para una versión que todavía no figura en `plugin.json` (avisa la diferencia). Requiere Python 3.9+ con `pyyaml`, Node.js con `pptxgenjs` y `mmdc`
(`@mermaid-js/mermaid-cli`; si no encuentra Chromium, `PUPPETEER_CFG=<json con executablePath>`). Si una guía E2E
cambia sus imágenes, `extraer.py` avisa y usa otra de la sección «Indicadores que vas a ver»; si una cifra o un código
citado ya no existe, se detiene con el motivo.

Control de calidad (las capturas van a la carpeta que se indique, fuera del repositorio):

```bash
sh qa_pptx.sh /tmp/qa-pptx           # LibreOffice → PDF → PNG y texto fuera del área segura
python3 qa_html.py /tmp/qa-html      # Playwright: claro, oscuro y 390 px; desbordes, anclas e imágenes rotas; PDF impreso
```

Sin marca ni logo de empresa: un recuadro rotulado «Logo IEEE» en la portada y en cada diapositiva.
