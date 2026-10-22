# Presentaciones light para IEEE · pm-method

Dos presentaciones cortas para miembros de IEEE que no conocen la jerga de gestión de proyectos (PMI, PMBOK, PRINCE2,
PMO): lenguaje simple, un mensaje por diapositiva con título-conclusión, un recuadro «¿Qué significan las siglas?» y
notas del orador. Mismo contenido en PPTX y en HTML autocontenido (claro, oscuro o automático; imprimible, una
diapositiva por página; navegación con ◀ ▶ y las flechas; tecla N o botón «Notas» para las notas del orador).

| Archivo | Diapositivas | Contenido |
|---|---|---|
| `pm-method-ieee-resumen-light.pptx` / `.html` | 5 | qué resuelve, cómo trabaja y sus ventajas, programa de formación propuesto y ruta de entrada (piloto) |
| `pm-method-ieee-informe-light.pptx` / `.html` | 9 | resumen del [Informe 2](../informe/README.md): problema, capas del método, quién hace qué, puertas, controles permanentes, radar y seguridad de la IA agéntica, ventajas, límites y cómo seguir |

**Programa de formación propuesto** (ajustable, no es un dato): introducción (2 sesiones) + 5 talleres de casos × 2
sesiones + taller integrador (2) = 14 sesiones de 90 min = 1.260 min = 21 h; 14 semanas a una sesión por semana o 7 a
dos. Los 5 talleres usan el material ya listo de [docs/webinar/](../webinar/README.md) (10 clases de 90 min = 15 h);
la introducción y el integrador (4 sesiones = 6 h) están por preparar. Ruta de entrada: piloto de 4 sesiones
(introducción + taller de riesgos = 6 h) o 6 sesiones (+ taller de cambios = 9 h), que cuentan para el programa completo.

## Regenerar

```bash
cd docs/ieee/fuente
python3 preparar.py                 # calcula el programa y lo verifica contra docs/webinar/E2E-*/diapositivas.json → datos-*.json
node build_pptx.js resumen          # → ../pm-method-ieee-resumen-light.pptx  (también: informe)
python3 build_html.py resumen       # → ../pm-method-ieee-resumen-light.html  (también: informe)
```

El texto vive en `fuente/contenido-resumen.json` y `fuente/contenido-informe.json` con marcadores `{clave}`. Ninguna
cifra está escrita a mano: `preparar.py` suma sesiones y minutos de los módulos, comprueba que cada taller tenga en el
webinar tantas clases de 90 minutos como sesiones, toma la versión de `.claude-plugin/plugin.json` y la línea de
calidad de la tabla de evidencia del README; si algo no coincide, se detiene con el motivo. Requiere Python 3.9+ y
Node.js con `pptxgenjs`.

Control de calidad (capturas fuera del repositorio): `sh qa_pptx.sh /tmp/qa-ieee-pptx` (LibreOffice → PDF → PNG y texto
fuera del área segura) y `python3 qa_html.py /tmp/qa-ieee-html` (Playwright: claro, oscuro y 390 px, desbordes, texto
cortado e imágenes rotas, y PDF impreso).

Sin marcas, logos ni colores de marca de empresas u organizaciones: un recuadro rotulado «Logo IEEE» en la portada y en
cada diapositiva, y tonos de azul propios. Las imágenes son capturas reales de las guías E2E (`docs/guias/img/`).
