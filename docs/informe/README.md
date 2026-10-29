# Informe 2 · Documentación del ecosistema pm-method (v2.6)

- `informe-2-ecosistema-pm-method-v2.6.html` y `.pptx`: el informe (mismo contenido; 346 diapositivas), generado
  desde la documentación de este repositorio (versión 2.6.0). Describe el ecosistema tal como es: resumen ejecutivo,
  capacidades de gestión (validar antes de invertir, evaluación de inversiones con `inversion.py`, mapas de Wardley y de
  recorrido, contexto de sesión acotado, maestro de interesados y personas de usuario, capa de canales, OKR, riesgos
  desde cuatro fuentes, opciones de respuesta y plan de contingencia, presupuesto de riesgo y reserva de gestión, radar
  de atención y briefing de incorporación, highlight y tablero desde `estado.py periodo` con la cadena de reporte
  verificada, estado de productos y cierre por id, acuerdos de reunión con cita, ciclo de las lecciones, análisis de
  impacto, tres valores y capacidad del release, expediente de auditoría, decisiones con contexto con `decision.py`
  —expediente, matriz multicriterio, pregunta tipada, RACI ↔ autoridad, vigencia y contradicciones, hacer o comprar con
  los mapas—, bitácora de escrituras y propuestas con huella, pm-kb (búsqueda citada en los proyectos, opcional, con su
  arquitectura y los dos caminos de instalación) y controles permanentes, cada una con la figura y la salida real de su
  guía E2E), diagramas (incluido el de pm-kb), arquitectura, columna vertebral BMAD ↔ PRINCE2, sanidad (101 códigos en
  14 familias), guardarraíles y seguridad, puertas de la junta (con P-11, E-11, C-03 y C-07 y los códigos de control de
  `verificar`), componentes (con las decisiones de integración: diagram-design verificado y ShowAI evaluado),
  dependencias con URL de origen, instalación y configuración (incluido el entorno Docker y los dos caminos de
  instalación, sobre WSL2 o con Docker, con pm-kb en cada uno), catálogo, RACI, casos de uso por skill (con la parte 7,
  casos 50 a 59) y por repositorio integrado, caso maestro, guías E2E con sus indicadores y material de formación,
  pruebas (regresión, integración cruzada, recorridos E2E, Python 3.9 y pruebas en vivo de la versión 2.6.0 del
  28/10/2026), piloto, índice, mantenimiento, cómo seguir evolucionando, historial de versiones (sección 22, el único
  lugar que describe cambios entre versiones), glosario, fuentes y estructura de carpetas.
- `fuente/`: el generador. Regenerar después de cambiar la documentación (también cuando cambian las imágenes de
  `docs/guias/img/`, que el informe toma de las guías: la sección «Indicadores que vas a ver» y las figuras de los
  pasos) o la evidencia de `docs/guias/evidencia/` (las salidas reales de la sección 2):

```bash
cd docs/informe/fuente
npm install pptxgenjs                      # una vez (o tenerlo global y usar NODE_PATH=$(npm root -g))
python3 extraer.py                         # lee README, CHANGELOG, SPEC, docs/ (guías, webinar, seguridad, Docker) y compatibilidad.json → data.json y diagramas
python3 build_html.py                      # → salida-v2.6/informe-2-ecosistema-pm-method-v2.6.html
node build_pptx.js                         # → salida-v2.6/informe-2-ecosistema-pm-method-v2.6.pptx
cp salida-v2.6/informe-2-ecosistema-pm-method-v2.6.* ..
```

Requiere Python 3.9+ con Pillow (recortes de las capturas del reporte de interesados), Node.js y `mmdc`
(`@mermaid-js/mermaid-cli`) en el `PATH`; si `mmdc` no encuentra Chromium, definir `PUPPETEER_CFG=<json con
executablePath>`. La carpeta de salida sale de `meta.version` de `fuente/narrativa.json` y está excluida por git.

**Cifras.** Ninguna cifra del texto propio está escrita a mano: `extraer.py` cuenta en el repositorio skills, agentes,
hooks, registros, códigos y familias de sanidad, guías, pasos, imágenes y diapositivas del webinar, corre
`validar_paquete.py` y los `--help` de `inversion.py` y `mapas.py`, toma los resultados de pruebas de
`docs/PRUEBAS.md` y las salidas reales de `docs/guias/evidencia/`, y guarda todo en `data.json["x"]["cifras"]`. El texto
propio (`fuente/narrativa.json`) cita esas cifras con marcadores `{{clave}}`; un marcador desconocido detiene la
extracción. Los pasos de cada guía se cuentan como en `docs/guias/README.md` (un paso partido en «6a» y «6b» cuenta una
vez) y la extracción se detiene si no coinciden; las pruebas en vivo de la versión más reciente que las registró se suman desde
`docs/PRUEBAS.md` §3.1, y `meta.version` debe coincidir con `compatibilidad.json`. Las tablas «antes y después» de
versiones anteriores quedan como se publicaron (sus valores salen del `data.json` de esa versión). Si una guía cita una
imagen que todavía no está en `docs/guias/img/`, `extraer.py` la omite con un aviso: volver a extraer cuando exista.
Si falta un bloque de evidencia que muestra la sección 2, la extracción se detiene con el comando que buscó.

Control de calidad (las capturas van a la carpeta que se indique, fuera del repositorio):

```bash
sh qa_pptx.sh "" /tmp/qa-pptx              # LibreOffice → PDF → PNG (grillas 2×2) y texto fuera de la zona de contenido
python3 qa_html.py "" /tmp/qa-html         # Playwright: claro y oscuro a 1366 px y a 390 px; desbordes horizontales y SVG vacíos
```

Sin marca de empresa: un recuadro rotulado «Logo IEEE» en la portada y en cada diapositiva (o `logo.png` junto a los
scripts para usar el logo de IEEE). El HTML trae tema claro, oscuro o automático (botón «Tema»).
