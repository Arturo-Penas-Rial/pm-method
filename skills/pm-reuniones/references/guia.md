# Guía de reuniones y actas · Meetings and minutes guide

## §1. Fuentes de transcripción
| Vía | Cómo se obtiene | Qué guardar |
|---|---|---|
| Archivo VTT/SRT | exportado de Teams, Zoom, Meet u otra plataforma | el archivo original en `03-control/reuniones/` (si la política lo permite) |
| TXT "Nombre: texto" o con marcas `[00:05:12]` | notas o exportes de grabadoras | ídem |
| DOCX | transcripción descargada como documento | ídem (requiere `python-docx`) |
| Texto pegado | el usuario lo pega en la conversación | guardarlo como `<fecha>-<reunion>-original.txt` antes de procesarlo |
| Herramienta conectada | capacidad `reuniones` de `pm-integraciones` (indicios `granola`, `fireflies`, `zoom`, `minutes`, `teams`) | instantánea `03-control/fuentes/<sistema>-AAAA-MM-DD.md` con front matter `fuente`, `fecha`, `consulta` |

Con herramienta conectada: listar reuniones de un rango de fechas, mostrar título/fecha/asistentes, confirmar cuál, traer la transcripción (no solo el resumen automático, que puede omitir decisiones). Si la herramienta solo entrega su propio resumen, usarlo como fuente y declararlo en el campo `fuente` del acta.

## §2. Normalización con transcripcion.py
- Detecta VTT/SRT por `-->`; si no, interpreta líneas `Nombre: texto`, `[hh:mm:ss] Nombre: texto` o exportes del tipo `Nombre   0:05` seguidos del texto.
- Fusiona turnos consecutivos del mismo hablante y calcula turnos, palabras y % por hablante y la duración si hay tiempos.
- `--anonimizar` reemplaza nombres por P1, P2… en orden de aparición. Recomendado antes de compartir fuera del equipo y obligatorio para el análisis de clima.
- `--json` imprime el resumen de participación (útil para el análisis agregado).
- Revisar: hablantes `?` (líneas sin atribución), nombres partidos ("Ana" y "Ana López" como dos personas) y ruido de subtítulos. Corregir en la fuente y volver a correr; no editar la salida a mano.
- El script no infiere emociones ni evalúa personas: solo cuenta.

## §3. Extracción para el acta
Leer la transcripción normalizada por bloques y anotar con marca de tiempo:
- **Decisiones**: frases de cierre ("entonces queda", "aprobamos", "vamos con la opción B") dichas por alguien con autoridad. Registrar opciones consideradas si se discutieron.
- **Acciones**: compromiso + persona + plazo ("yo le mando el contrato el viernes"). Sin persona o sin plazo → pregunta abierta.
- **Riesgos**: condicionales sobre el futuro ("si el proveedor no entrega…"). Redactar causa → evento → efecto.
- **Issues**: hechos ya ocurridos o pedidos ("el servidor de pruebas no está", "el cliente pide agregar…").
- **Lecciones**: comparaciones entre lo esperado y lo ocurrido, aprendizajes explícitos.
- **Excepciones**: pronósticos de salir de la tolerancia ("no llegamos a fin de mes ni con horas extra").

## §4. Clasificación
| Lo dicho | Es | Registro | Quién decide |
|---|---|---|---|
| "Juan revisa el informe para el jueves" | acción | `acciones.csv` | — (compromiso) |
| "Puede que el permiso municipal se atrase" | riesgo (amenaza) | `riesgos.csv` | propietario del riesgo |
| "Llegó el lote con defectos" | issue `fuera-especificacion` | `issues.csv` | gestor / autoridad de cambio |
| "El cliente quiere un módulo de reportes extra" | issue `solicitud-cambio` | `issues.csv` (+ `cambios.csv` al evaluarlo) | autoridad de cambio |
| "La nueva ley cambia los plazos" | issue `evento-externo` | `issues.csv` | gestor → junta si excede |
| "Aprobamos pasar a la etapa 3" | decisión de puerta | la registra `pm-director` | junta |
| "PO cambia la historia 14 por la 22" | decisión `product-owner` | `decisiones.csv` | product owner dentro de tolerancia |
| "Con este ritmo terminamos un mes tarde" (tolerancia ±2 semanas) | excepción | informe de excepción | junta |

## §5. Propuestas a registros (tras confirmar)
Presentar una tabla con: tipo, texto propuesto, campos, registro destino. Tras el "sí", cargar en lote. Ejemplos:
```
registro.py --proyecto <dir> agregar acciones --campo origen=acta-2026-10-17-comite --campo descripcion="Enviar contrato revisado al proveedor" --campo responsable="J. Pérez" --campo fecha_compromiso=2026-10-24 --campo prioridad=alta
registro.py --proyecto <dir> agregar riesgos --campo causa="Dependencia de permiso municipal" --campo evento="Atraso del permiso" --campo efecto="Retraso de obra 3 semanas" --campo tipo=amenaza --campo probabilidad=3 --campo impacto=4 --campo propietario="Gestor"
registro.py --proyecto <dir> agregar issues --campo tipo=solicitud-cambio --campo titulo="Módulo de reportes adicional" --campo descripcion="Pedido del cliente en comité 2026-10-17" --campo prioridad=media
registro.py --proyecto <dir> agregar decisiones --campo decision="Intercambio de historias 14↔22" --campo decidido_por="PO: L. Ruiz" --campo nivel=product-owner
registro.py --proyecto <dir> agregar lecciones --campo situacion="La demo sin datos reales confundió al cliente" --campo recomendacion="Preparar datos de muestra realistas" --campo etapa=2
```
Los riesgos se evalúan después con `pm-riesgos`; los issues, con `pm-issues-cambios`.

## §6. Clima de equipo agregado y privacidad
Condiciones previas (todas):
1. Los participantes fueron informados y aceptaron; se registra quién lo confirmó, cuándo y cómo (no la lista de nombres si no hace falta).
2. Transcripción con `--anonimizar`.
3. Resultado a nivel de equipo o de rol, nunca de persona; si un rol tiene una sola persona, agregarlo con otro.

Señales permitidas (observables, no psicológicas):
- distribución del tiempo de palabra (concentración: % de los dos hablantes principales; equilibrio entre roles);
- temas con más vueltas sin decisión; decisiones pospuestas;
- preguntas que quedaron sin respuesta; acciones sin responsable;
- tendencia entre reuniones (más o menos participación, menos acciones vencidas);
- menciones explícitas del propio equipo sobre la forma de trabajar (citadas sin atribución).

No permitido: inferir emociones, estrés, motivación o actitud de una persona; puntuar desempeño individual; guardar valoraciones personales; usar el análisis en evaluaciones de desempeño. Si el equipo lo pide expresamente, hablarlo en una retrospectiva (`pm-agil-hibrido`) o en el taller de lecciones (`pm-lecciones-aprendidas`), no en un documento.

Salida: ajustes de formato de reunión y de comunicación (rotar facilitación, agenda con tiempos, ronda de cierre de acciones) para el gestor y, si corresponde, sugerencias a la matriz de comunicaciones (`pm-comunicacion-stakeholders`). Conservar solo el informe agregado; borrar intermedios con datos nominativos si se generaron.

## §7. Reuniones típicas en PRINCE2
| Reunión | Proceso | Énfasis del acta | Quién confirma |
|---|---|---|---|
| Junta (puerta o ad hoc) | DP | decisiones, condiciones, tolerancias | ejecutivo; acta formal vía `pm-direccion-decisiones` |
| Checkpoint del paquete | MP→CS | avance, bloqueos, calidad | gestor de equipo |
| Revisión de etapa / fin de etapa | SB | lecciones, plan siguiente | gestor del proyecto |
| Daily / revisión de iteración | MP | bloqueos → acciones; demo → `calidad.csv` | equipo / PO |
| Reunión con cliente o proveedor | CS | compromisos contractuales, cambios pedidos | gestor del proyecto |
| Taller de cierre | CP | lecciones, handover | gestor del proyecto |

## §8. Casos borde
- **Sin transcripción**: reconstruir con notas del usuario; `fuente: reconstruida de memoria` y más `[por confirmar]`.
- **Reunión en varios idiomas**: acta en el idioma del proyecto; citas en el original.
- **Información confidencial** (salarios, sanciones, salud): no transcribir al acta; anotar "tema confidencial tratado, ver responsable".
- **Grabación sin consentimiento conocido**: preguntar antes de procesarla; si no se confirma, trabajar solo con notas.
- **Decisión contradictoria con una anterior**: anotar ambas con ids y proponer issue para aclararlo.
- **Muchas acciones para una persona**: señalarlo al gestor como posible sobrecarga (agregado por persona en `registro.py resumen`, que es dato operativo, no clima).
