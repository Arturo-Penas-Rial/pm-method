# Spot de pm-method para LinkedIn

Video breve en español para anunciar el repositorio, pensado para acompañar al [resumen ejecutivo](../README.md).

| Archivo | Qué es |
|---|---|
| `pm-method-spot.mp4` | spot de 54,3 s, 1080×1350 (4:5), 30 fps, H.264 `yuv420p` + AAC 48 kHz, `+faststart`; locución sintética, música original y subtítulos incrustados |
| `pm-method-spot-sin-voz.mp4` | la misma pieza con música y subtítulos, sin locución (para quien prefiera grabar su voz o publicar sin voz sintética) |
| `pm-method-spot.srt` | subtítulos aparte (LinkedIn permite subirlos al publicar) |
| `pm-method-spot-guion.txt` | guion de locución con la ventana de tiempo de cada frase, para grabarla con voz propia |
| `fuente/` | todo lo necesario para regenerarlo |

Estructura (54,3 s), pensada para directivos y PMO:

| Tiempo | Escena | Locución (subtítulo) | En pantalla |
|---|---|---|---|
| 0:00–0:06 | apertura | La estrategia se ejecuta a través de proyectos. Si los resultados importan, los métodos también. | estrategia → proyectos → resultados |
| 0:06–0:11 | pregunta | ¿Cómo gestionar con más eficiencia y foco en valor? Aplicando IA, con método. | la respuesta y «→ pm-method» |
| 0:11–0:17 | jerarquía | Un plugin para Claude Code: PRINCE2 manda, PMBOK aporta técnicas y BMAD es la especificación. | PRINCE2 7 / PMBOK 8 / BMAD |
| 0:17–0:25 | caso | Un cambio llevaría el presupuesto al 200 %. Sin saldo ni autoridad, no se aprueba: sube a la junta el mismo día. | caso E2E-2, paso 10: C-002 de 15.000 aprobado de palabra con un límite de 10.000; 24.000 de 12.000; «no se puede registrar como aprobado»; pendiente de la junta |
| 0:25–0:31 | estrategia | Mapas de Wardley y de recorrido del cliente, opciones con VAN y conexión con BMAD, Jira, Slack y Teams. | gráficos reales de E2E-5 y E2E-4 e integraciones |
| 0:31–0:38 | prueba | 6 agentes, 39 skills, más de 200 pruebas automáticas y 5 casos completos con webinar. | mosaico de cifras (216 pruebas de regresión, 85 controles, 0 hallazgos altos) |
| 0:38–0:54 | cierre | pm-method: código abierto, en GitHub. ¿Estás en proyectos e innovación? Te invito a consultarme: capacitación y transferencia para lograr los beneficios de tus proyectos con IA. Escribime por LinkedIn. Iniciativa con el apoyo de PMI e IEEE (Uruguay). | URL de GitHub, invitación, oferta de capacitación y transferencia, «Escribime por LinkedIn» y la línea de apoyo, solo como texto |

Sin marcas ni logos: las herramientas aparecen solo como texto y el único nombre propio es el usuario de GitHub de la
URL del README. La mención «Iniciativa con el apoyo de PMI e IEEE (Uruguay)» es texto provisto por el autor; va como
texto plano, sin logos ni colores o tipografías de esas organizaciones. En la locución, las siglas se escriben como se
pronuncian solo en `tts` («Pi Em Ai», «i triple e»); los subtítulos llevan la escritura normal.

## Regenerar

```bash
cd docs/resumen-ejecutivo/spot/fuente
python3 construir.py --ambas      # ≈ 5 min: audio, cuadros (Playwright) y MP4; también SRT y guion
python3 construir.py --cuadros 0,12,24,36 --tmp /tmp/spot-qa   # solo PNG de esos instantes, para revisar
```

Requiere Python 3.9+ con `numpy`, `scipy`, `soundfile` y `playwright` (`python -m playwright install chromium`),
`ffmpeg` y la fuente Inter instalada (si falta, usa DejaVu Sans). Las locuciones ya generadas están en `fuente/voz/`,
así que regenerar el video **no** necesita el modelo de voz. Para cambiar el texto o la voz:

1. Editar `fuente/guion.json` (`texto` = subtítulo; `tts` = la misma frase escrita como se pronuncia; ` | ` separa
   subtítulos y debe aparecer las mismas veces en los dos campos).
2. Bajar el modelo de sus releases de GitHub y generar las locuciones:
   ```bash
   pip install kokoro-onnx==0.6.1 soundfile
   curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
   curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin
   python voz.py --modelo . [--escenas caso,cierre]   # → fuente/voz/*.flac y duraciones.json (otras voces: --voz ef_dora | em_santa)
   ```
3. `python3 construir.py --ambas`. La línea de tiempo (escenas, música y subtítulos) se ajusta sola a la duración de
   cada frase; si una escena cambia mucho de largo, revisar los tiempos `data-in` de `fuente/spot.html`.

| Archivo de `fuente/` | Función |
|---|---|
| `guion.json` | frases, pronunciación, pausas por escena y configuración de la voz |
| `voz.py` | locución con Kokoro (una frase por escena, recorte de silencios) |
| `musica.py` | música original sintetizada: pad, bajo, pulso, arpegio, barridos y acorde final al terminar la locución (Si m – Sol – Re – La, 96 BPM) |
| `spot.html` | cuadros: tipografía cinética, gráficos de `docs/guias/img/`, paleta de `scripts/pruebas/guias_e2e/visuales.py` |
| `construir.py` | línea de tiempo, mezcla con ducking (−9 dB bajo la voz), loudnorm a −14 LUFS / −1,5 dBTP, render y codificación |

## Cifras

Todas salen del repositorio al 2026-10-20 (versión 2.3.0): 6 agentes (`agents/`), 39 skills (`skills/`; 33 que activa
el modelo y 6 comandos), 3 hooks (`hooks/hooks.json`), 85 códigos de sanidad en 12 familias (contados en
`skills/*/scripts/*.py` y en `docs/SANIDAD.md`), 223 pruebas de regresión con 0 fallos (`scripts/probar_paquete.py`,
vuelto a correr al hacer el spot; la locución dice «más de 200») y 61 de integración cruzada ([PRUEBAS](../../PRUEBAS.md)), 5 casos E2E con webinar
([guías](../../guias/README.md)), revisión de seguridad con 0 hallazgos de severidad alta y 3 medios corregidos
([SEGURIDAD](../../SEGURIDAD.md)), caso E2E-2: C-002 de 15.000 aprobado de palabra por una autoridad de cambio con límite de 10.000, que llevaría el presupuesto de cambio a 24.000 de 12.000 (200 %) y que `registro.py` no deja registrar como aprobado: queda pendiente de la junta el mismo día ([guía E2E-2](../../guias/E2E-2-alcance-roadmap.md), introducción y paso 10; `docs/guias/img/g2-consumo-cambio.png`),
licencia MIT y URL de GitHub del [README](../../../README.md). No hay promesas de ahorro ni datos de la industria.

## Licencias de los componentes

| Componente | Licencia | Origen |
|---|---|---|
| Música, efectos, guion, diseño y código de `fuente/` | MIT, como el repositorio | escritos para este spot; síntesis con numpy y scipy, sin samples |
| Voz: modelo Kokoro-82M v1.0 (`em_alex`, español) | Apache 2.0 | pesos de hexgrad/kokoro; archivos ONNX de los releases de GitHub de `thewh1teagle/kokoro-onnx` |
| Motor `kokoro-onnx` 0.6.1 | MIT | PyPI |
| Fonemizador: `phonemizer` 3.4.0 y eSpeak NG (vía `espeakng-loader` 0.2.4, MIT) | GPL-3.0 | PyPI; se usan solo como herramientas al generar el audio y no se distribuyen aquí |
| `onnxruntime` | MIT | PyPI |
| Fuente Inter | SIL Open Font License 1.1 | paquete del sistema |
| Imágenes de las escenas | MIT | `docs/guias/img/` de este repositorio |

PRINCE2® y PMBOK® son marcas de sus titulares; Claude Code, Jira, Slack y Teams se nombran solo como texto.

## Antes de publicar

- **Escuchar la locución.** La voz es sintética (neural, acento neutro con seseo) y se generó sin poder escucharla en
  el entorno de construcción: se revisaron duración, niveles, espectro y relación voz/música, no la naturalidad. Si no
  convence, publicar `pm-method-spot-sin-voz.mp4` o grabar la voz con `pm-method-spot-guion.txt` y mezclarla sobre
  esa versión.
- Al subir a LinkedIn, adjuntar `pm-method-spot.srt` como subtítulos si se quieren también como pista seleccionable.
- No hay versión 16:9; para una, ajustar las posiciones de `spot.html` a 1920×1080 y las constantes `W`, `H` de
  `construir.py`.
