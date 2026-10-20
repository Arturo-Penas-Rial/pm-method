# Informe 2 · Documentación del ecosistema pm-method (v2.3)

- `informe-2-ecosistema-pm-method-v2.3.html` y `.pptx`: el informe (mismo contenido; 270 diapositivas), generado
  desde la documentación de este repositorio (versión 2.3.0). Describe el ecosistema tal como es: resumen ejecutivo,
  capacidades de gestión (validar antes de invertir, evaluación de inversiones con `inversion.py`, mapas de Wardley y de
  recorrido, contexto de sesión acotado, maestro de interesados, capa de canales, OKR, riesgos desde cuatro fuentes y
  controles permanentes), diagramas, arquitectura, columna vertebral BMAD ↔ PRINCE2, sanidad (85 códigos en 12
  familias), guardarraíles y seguridad, puertas de la junta (con P-11 y los códigos de control de `verificar`),
  componentes, dependencias con URL de origen, instalación y configuración (incluido el entorno Docker), catálogo,
  RACI, casos de uso por skill y por repositorio integrado, caso maestro, guías E2E con sus indicadores y material de
  formación, pruebas (regresión, integración cruzada, recorridos E2E, Python 3.9 y pruebas en vivo del 2026-10-20),
  piloto, índice, mantenimiento, cómo seguir evolucionando, historial de versiones (sección 22, el único lugar que
  describe cambios entre versiones), glosario, fuentes y estructura de carpetas.
- `fuente/`: el generador. Regenerar después de cambiar la documentación (también cuando cambian las imágenes de
  `docs/guias/img/`, que el informe toma de la sección «Indicadores que vas a ver» de cada guía):

```bash
cd docs/informe/fuente
npm install pptxgenjs                      # una vez (o tenerlo global y usar NODE_PATH=$(npm root -g))
python3 extraer.py                         # lee README, CHANGELOG, SPEC, docs/ (guías, webinar, seguridad, Docker) y compatibilidad.json → data.json y diagramas
python3 build_html.py                      # → salida-v2.3/informe-2-ecosistema-pm-method-v2.3.html
node build_pptx.js                         # → salida-v2.3/informe-2-ecosistema-pm-method-v2.3.pptx
cp salida-v2.3/informe-2-ecosistema-pm-method-v2.3.* ..
```

Requiere Python 3.9+ con Pillow (recortes de las capturas del reporte de interesados), Node.js y `mmdc`
(`@mermaid-js/mermaid-cli`) en el `PATH`; si `mmdc` no encuentra Chromium, definir `PUPPETEER_CFG=<json con
executablePath>`. La carpeta de salida sale de `meta.version` de `fuente/narrativa.json` y está excluida por git.

**Cifras.** Ninguna cifra del texto propio está escrita a mano: `extraer.py` cuenta en el repositorio skills, agentes,
hooks, registros, códigos y familias de sanidad, guías, pasos, imágenes y diapositivas del webinar, corre
`validar_paquete.py` y los `--help` de `inversion.py` y `mapas.py`, toma los resultados de pruebas de
`docs/PRUEBAS.md` y las salidas reales de `docs/guias/evidencia/`, y guarda todo en `data.json["x"]["cifras"]`. El texto
propio (`fuente/narrativa.json`) cita esas cifras con marcadores `{{clave}}`; un marcador desconocido detiene la
extracción. Si una guía cita una imagen que todavía no está en `docs/guias/img/`, `extraer.py` la omite con un aviso:
volver a extraer cuando exista.

Control de calidad (las capturas van a la carpeta que se indique, fuera del repositorio):

```bash
sh qa_pptx.sh "" /tmp/qa-pptx              # LibreOffice → PDF → PNG (grillas 2×2) y texto fuera de la zona de contenido
python3 qa_html.py "" /tmp/qa-html         # Playwright: claro y oscuro a 1366 px y a 390 px; desbordes horizontales y SVG vacíos
```

Sin marca de empresa: un recuadro rotulado «Logo IEEE» en la portada y en cada diapositiva (o `logo.png` junto a los
scripts para usar el logo de IEEE). El HTML trae tema claro, oscuro o automático (botón «Tema»).
