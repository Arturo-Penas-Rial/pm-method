import base64 as _b64

def img64(rel):
    return "data:image/png;base64," + _b64.b64encode(open(rel, "rb").read()).decode()

# Cuerpo del Informe 2 (lo ejecuta build_html.py con exec, comparte sus funciones y variables).
# Las subsecciones se escriben como <h3>¶Título</h3>: sec() les antepone "<n>.<k> · ".

def vin(items, clase=""):
    return f"<ul class='{clase}'>" + "".join(f"<li>{inl(x)}</li>" for x in items) + "</ul>"


def sin_cita(t):
    return "\n".join((l[2:] if l.startswith("> ") else l[1:]) if l.startswith(">") else l for l in t.split("\n"))


PENDIENTE = "[pendiente: docs/PRUEBAS.md todavía no registra este resultado]"
X["pru_resultados"]["filas"] = [[PENDIENTE if re.fullmatch(r"RESULTADO_[A-Z]+", c.strip()) else c for c in f] for f in X["pru_resultados"]["filas"]]


def antes_de_h3(t):
    return t.split("\n### ")[0].strip()


# ---------- Portada, audiencias ----------
lectores = tabla_html(["Rol", "Qué obtiene de pm-method", "Secciones clave"],
                      [[f"**{a['rol']}**", a["valor"], a["leer"]] for a in D["audiencias"]], "", ["18%", "", "14%"])

# ---------- 1 · Resumen ejecutivo ----------
kpis = '<div class="kpis">' + "".join(f'<div class="kpi"><span class="v">{e(k["v"])}</span><span class="t">{e(k["t"])}</span><span class="d">{e(k["d"])}</span></div>' for k in D["kpis"]) + "</div>"
valor = '<div class="layers">' + "".join(
    (lambda m: f'<div class="layer"><b>{inl(m.group(1))}</b><p>{inl(m.group(2))}</p></div>')(re.match(r"^\*\*(.+?)\*\*\s*(.*)$", v, re.S)) for v in X["re_valor"]) + "</div>"
s1 = sec("resumen", "1", "Resumen ejecutivo",
         f"<p class='lema'>{e(X['re_lema'])}</p>" + kpis
         + "<h3>¶La propuesta en una frase</h3>" + md(X["re_frase_md"])
         + "<h3>¶El problema que resuelve</h3>" + T(X["re_problema"], "", ["50%", ""])
         + "<h3>¶Qué ofrece</h3><p>" + str(len(X['re_capacidades']['filas'])) + " capacidades, cada una con el mecanismo que la hace posible y el beneficio para quien gestiona o decide.</p>" + T(X["re_capacidades"], "", ["20%", "45%", ""])
         + "<h3>¶Valor diferencial</h3>" + valor
         + "<h3>¶Para quién</h3>" + T(X["re_para_quien"], "", ["28%", ""])
         + "<h4>Cómo leer este informe según su rol</h4>" + lectores
         + "<h3>¶Evidencia al " + "/".join(reversed(X["cifras"]["pruebas_fecha"].split("-"))) + "</h3>" + T(X["re_evidencia"], "", ["42%", ""])
         + "<h3>¶Límites conocidos, con honestidad</h3>" + vin(X["re_limites"])
         + "<h3>¶Cómo empezar</h3>" + md(X["re_empezar_md"]) + "<p>En este informe: guía completa en la sección 11 y prueba de aceptación en la sección 17.</p>",
         "todas las audiencias")

# ---------- 2 · Capacidades de gestión ----------
V = D["cap"]
CIF = X["cifras"]
FECHA_P = "/".join(reversed(CIF["pruebas_fecha"].split("-")))


def indicador(patron):
    """Imagen de la sección «Indicadores que vas a ver» de las guías E2E cuyo nombre coincide con el patrón."""
    for g, items in X["guias_indicadores"].items():
        for it in items:
            if re.search(patron, it["img"]):
                return dict(it, guia=g)
    raise KeyError(f"ninguna imagen de indicadores coincide con {patron}")


def fig_guia(it, ancho="1000px"):
    return (f"<figure style='margin:16px auto;max-width:{ancho}'><img class='captura' src='{img64('../../guias/img/' + it['img'])}' alt='{e(it['alt'])}'>"
            f"<figcaption>{e(it['guia'])} · {inl(it['lectura'])} · <code>docs/guias/img/{e(it['img'])}</code></figcaption></figure>")


EV = X["ev24"]


def fig24(img, ancho="1000px"):
    """Figura de cualquier paso de las guías E2E (no solo de «Indicadores»), con su guía y su paso."""
    f = X["guias_figuras"][img]
    return (f"<figure style='margin:16px auto;max-width:{ancho}'><img class='captura' src='{img64('../../guias/img/' + img)}' alt='{e(f['alt'])}'>"
            f"<figcaption>{e(f['guia'])}, paso {e(f['paso'])} · {inl(f['lectura'])} · <code>docs/guias/img/{e(img)}</code></figcaption></figure>")


def salida(titulo, *bloques):
    return f"<h4>{titulo}</h4>" + "".join(pre(b) for b in bloques)


cuadrantes = tabla_html(["Cuadrante", "Poder · interés", "Estrategia", "Comunicación por defecto (canal · formato · detalle · frecuencia)"],
                        [[f"**{c[0]}**", c[1], c[2], c[3]] for c in V["cuadrantes"]], "", ["17%", "12%", "", "30%"])
rf = X["g1_fuentes"]
riesgos_tab = tabla_html(rf["cab"] + ["Candidatos en la corrida de referencia"], [f + [V["riesgos_cifras"][k]] for k, f in enumerate(rf["filas"])], "", ["16%", "10%", "", "18%", "18%"])
controles_tab = tabla_html(["Problema habitual", "Control", "Código", "Dónde está el control", "Dónde se ve (guía · paso)"],
                           [f + [X["controles_donde"][k]] for k, f in enumerate(V["controles"])], "dec", ["24%", "27%", "10%", "18%", ""])
ejemplos = "<div class='cards'>" + "".join(f"<article class='card'><h4>{inl(x['t'])}</h4><p>{inl(x['d'])}</p></article>" for x in V["ejemplos"]) + "</div>"
img_matriz = "<figure style='margin:16px auto;max-width:1000px'><img class='captura' src='" + img64("../../guias/img/g3-interesados-matriz.png") + "' alt='Matriz poder/interés y estrategias del reporte de interesados'><figcaption>Reporte de interesados (E2E-3, corte 2027-01-15): matriz poder/interés y estrategia por cuadrante · docs/guias/img/g3-interesados-matriz.png</figcaption></figure>"
img_raci = "<figure style='margin:16px auto;max-width:1000px'><img class='captura' src='" + img64("../../guias/img/g3-interesados-raci-perfiles.png") + "' alt='RACI y perfiles de comunicación del reporte de interesados'><figcaption>Mismo reporte: RACI (letra y color) y perfiles de comunicación con la procedencia de cada valor · docs/guias/img/g3-interesados-raci-perfiles.png</figcaption></figure>"
map_tab = tabla_html(["Código", "Severidad", "Qué comprueba", "Corrige"], [f for f in X["codigos"]["filas"] if re.match(r"^MAP-\d", f[0])], "codigos", ["10%", "10%", "", "30%"])
ctx_tab = T(X["pru_contexto"], "", ["24%", "22%", "18%", ""])
s2 = sec("capacidades", "2", "Capacidades de gestión",
         f"<p class='intro'>{inl(V['intro'])}</p>"
         + "<h3>¶Validar antes de invertir: supuestos, experimentos y P-11</h3>" + layers(V["supuestos"]) + fig_guia(indicador(r"supuestos"))
         + "<h3>¶Evaluación de inversiones por opción (<code>inversion.py</code>)</h3>" + layers(V["inversion"])
         + fig_guia(indicador(r"van")) + "<h4>Salida real en la guía E2E-5, paso 4</h4>" + pre(X["ev_inversion"]) + vin(X["ev_inversion_lectura"])
         + "<h4>Fórmulas (<code>inversion.py --help</code>)</h4>" + vin(X["inversion_formulas"]) + pre(X["inversion_uso"])
         + "<h3>¶Mapas estratégicos: Wardley y recorrido del cliente</h3>" + layers(V["mapas"])
         + "<div class='two'>" + fig_guia(indicador(r"wardley"), "100%") + fig_guia(indicador(r"recorrido"), "100%") + "</div>"
         + "<h4>Familia MAP de la sanidad</h4>" + map_tab
         + f"<h4>Comandos (<code>mapas.py --help</code>)</h4><p class='src'>Fuente de verdad: {inl(X['mapas_fuente'])}</p>" + pre("\n".join(X["mapas_uso"]))
         + "<h3>¶Contexto de sesión acotado: los registros mandan sobre la memoria</h3>" + layers(V["contexto"])
         + "<h4>Salidas reales de <code>estado.py contexto</code> (guía E2E-5, pasos 7 y 14)</h4>" + "".join(pre(c) for c in X["ev_contexto"])
         + f"<h4>Topes de contexto medidos</h4><p>{inl(X['pru_contexto_intro'])}</p>" + ctx_tab + f"<p class='src'>{inl(X['pru_contexto_vivo'])}</p>"
         + "<h4>Memoria del cliente y estado del proyecto (INSTALACION §9.1)</h4>" + md(X["memoria_md"])
         + "<h3>¶Maestro de interesados (pm-interesados)</h3><p>El registro de interesados es un <b>maestro</b>: una sola fuente de personas con matriz poder/interés, estrategia por cuadrante, perfil de comunicación por persona y una RACI ligada al plan (fuentes: CASOS-DE-USO casos 38–43 y 46, <code>skills/pm-interesados/references/guia.md</code>).</p>"
         + "<h4>Matriz poder/interés y estrategia por cuadrante</h4><p>Poder (eje vertical): autoridad real, control de recursos, capacidad de aprobar presupuestos o vetar decisiones. Interés (eje horizontal): involucramiento, preocupación o impacto. Un valor «medio» se ubica del lado alto y se marca como frontera (<code>--medio bajo</code> invierte la convención).</p>" + cuadrantes
         + layers(V["interesados_puntos"]) + img_matriz + img_raci
         + "<h3>¶Personas de usuario y capacidad × persona (<code>interesados.py personas</code>)</h3>" + layers(V["personas"])
         + "<div class='two'>" + fig24("g5-personas-mapa.png", "100%") + fig24("g5-personas-mapa-bmad.png", "100%") + "</div>"
         + salida("Salida real en la guía E2E-5, paso 10b", EV["personas_mapa"], EV["personas_prio"])
         + "<h3>¶Capa de canales (envios.py)</h3><p>Una sola vía de salida para cualquier comunicación a interesados —comunicados personalizados, informes, actas, recordatorios, convocatorias, decisiones de puerta y check-ins de OKR—, con <code>skills/pm-integraciones/scripts/envios.py</code> (subcomandos <code>nuevo</code>, <code>estado</code>, <code>aprobar</code>, <code>enviar</code>, <code>preparar-mcp</code>, <code>registrar</code>, <code>historial</code> y <code>verificar</code>). Los borradores salen de <code>interesados.py plan-envio</code> con el perfil de cada destinatario; <code>aprobar</code> y <code>enviar --confirmar</code> piden la confirmación de una persona (hook <code>guardian.py</code>). Fuentes: INTEGRACIONES §3.2 e INSTALACION §0.7.</p>"
         + "<h4>Modos</h4>" + T(X["canales_modos"], "dec", ["13%", "10%", "28%", "", "15%"]) + diag("canales")
         + "<h4>Reglas</h4>" + vin(V["canales_reglas"])
         + "<details><summary>Paso a paso con los comandos (INTEGRACIONES §3.2)</summary>" + T(X["canales_pasos"], "dec", ["12%", "44%", ""]) + "</details>"
         + "<h3>¶OKR ligados a beneficios</h3><p><code>okr.py</code> maneja tipos de KR, compromiso, peso, iniciativas, check-ins y salud, y prepara la sincronización con Tability o Perdoo (fuentes: <code>skills/pm-okr</code>, CASOS-DE-USO caso 45).</p>"
         + tabla_html(["Concepto", "Qué hace"], [[f"**{o[0]}**", o[1]] for o in V["okr"]], "", ["20%", ""]) + f"<div class='callout blue'><p>{inl(V['okr_ejemplo'])}</p></div>"
         + f"<h3>¶Identificación de riesgos desde cuatro fuentes</h3><p>{inl(V['riesgos_intro'])} BMAD se lee solo a través de pm-bmad-puente. Cifras de la guía E2E-1 (pasos {', '.join(dict.fromkeys(f[1].replace('paso ', '') for f in rf['filas']))}) y su evidencia <code>docs/guias/evidencia/salida-g1.md</code>.</p>" + riesgos_tab
         + "<h3 id='opciones-respuesta'>¶Opciones de respuesta y plan de contingencia (<code>riesgos.py opciones</code>)</h3>" + layers(V["opciones"]) + fig24("g1-opciones-valor-neto.png")
         + salida("Salida real en la guía E2E-1, pasos 6a y 6b", EV["opciones"], EV["elegir"])
         + "<h3>¶Presupuesto de riesgo y reserva de gestión para lo no identificado</h3>" + layers(V["reserva"]) + f"<div class='callout blue'><p><b>En la guía E2E-1, paso 7.</b> {inl(X['g1_presupuesto_md'])}</p></div>" + fig24("g1-consumo-reserva.png")
         + "<h3>¶Radar de atención y briefing de incorporación (<code>estado.py radar · briefing</code>)</h3>" + layers(V["radar"]) + fig24("g3-radar.png")
         + salida("Salida real en la guía E2E-3, paso 10a", EV["radar_linea"], EV["radar"], EV["briefing"])
         + "<h3>¶Highlight y tablero desde el dato (<code>estado.py periodo</code>)</h3>" + layers(V["periodo"]) + fig24("g3-highlight-indicadores.png")
         + "<h4>Cadena de reporte verificada (guía E2E-3, paso 10b)</h4><div class='two'>" + pre(EV["verificar"]) + pre(EV["verificar_ok"]) + "</div>"
         + "<h3>¶Estado de productos y cierre verificado por id (<code>estado.py productos</code>, C-03, C-07)</h3>" + layers(V["productos"]) + fig24("g4-cierre.png")
         + salida("Salida real en la guía E2E-4, pasos 6 y 9", EV["productos"], EV["cierre"])
         + "<h3>¶Acuerdos de reunión con cita (<code>extraccion.py</code>)</h3>" + layers(V["reuniones"]) + fig24("g3-candidatos-reunion.png")
         + salida("Salida real en la guía E2E-3, paso 8", EV["candidatos"], EV["registrar_no"], EV["registrar"])
         + "<h3>¶Ciclo de las lecciones y lecciones de otros proyectos (<code>lecciones.py</code>)</h3>" + layers(V["lecciones"]) + fig24("g4-lecciones-ciclo.png")
         + salida("Salidas reales en las guías E2E-4 (paso 6c) y E2E-5 (paso 1)", EV["lecciones_listar"], EV["lecciones_buscar"])
         + "<h3>¶Análisis de impacto antes del cambio (<code>impacto.py</code>)</h3>" + layers(V["impacto"]) + fig24("g2-impacto-c002.png")
         + salida("Salida real en la guía E2E-2, paso 10", EV["impacto"])
         + "<h3>¶Tres valores, reserva de cronograma y capacidad del release (<code>cpm.py</code> · <code>release.py</code>)</h3>" + layers(V["estimacion"]) + fig24("g2-capacidad-release.png")
         + salida("Salidas reales en la guía E2E-2, pasos 3 y 4", EV["cpm"], EV["capacidad"])
         + "<h3>¶Expediente de auditoría verificable (<code>paquete.py auditoria · verificar</code>)</h3>" + layers(V["auditoria"]) + fig24("g4-expediente.png")
         + salida("Salida real en la guía E2E-4, paso 9b", EV["auditoria"], EV["aud_ok"], EV["aud_falla"])
         + f"<h3 id='controles-permanentes'>¶Controles permanentes</h3><p class='intro'>{inl(V['controles_intro'])}</p>" + controles_tab
         + "<p class='src'>Fuentes: SANIDAD §2.1, PUERTAS §3, las tablas «Del uso único al control continuo» de docs/guias/E2E-1…E2E-5 y <code>skills/pm-estado-proyecto/scripts/sanidad.py</code>, <code>puertas.py</code>, <code>estado.py</code>, <code>evm.py</code>, <code>skills/pm-interesados/scripts/interesados.py</code> y <code>skills/pm-mapas-estrategicos/scripts/mapas.py</code>, <code>skills/pm-riesgos/scripts/riesgos.py</code> y <code>skills/pm-lecciones-aprendidas/scripts/lecciones.py</code>. Presupuestos: <code>estado.py presupuesto cambio|riesgo|gestion|limite_autoridad_cambio=&lt;monto&gt; --por …</code>, reservado a pm-director por el hook. <code>sanidad.py --corte AAAA-MM-DD</code> hace reproducibles los controles con vencimiento.</p>"
         + "<h4>Ejemplos reales de la evidencia</h4>" + ejemplos
         + "<details><summary>Diagrama: gestión por excepción en la guía E2E-2 (paso 10)</summary>" + diag("excepcion").replace('<div class="diag-in">', '<div class="diag-in" style="max-width:520px;margin:0 auto">') + "</details>",
         "todas las audiencias")

# ---------- 3 · Justificación ----------
s3 = sec("justificacion", "3", "Justificación de la propuesta",
         "<p class='intro'>El paquete combina cinco fuentes con una precedencia estricta: PRINCE2 decide qué se hace, cuándo y quién decide; las demás aportan técnica, artefactos, especificación y canales, siempre subordinadas al método.</p>"
         + "<h3>¶Qué aporta cada fuente</h3>" + layers(D["marco"])
         + "<h3>¶PRINCE2 manda, el PMBOK aporta el cómo</h3><p>Toda regla tomada del PMBOK se etiqueta con la práctica, proceso o producto PRINCE2 donde se aplica (<code>[PMBOK→&lt;práctica&gt;/&lt;proceso&gt;]</code>). Ante conflicto, manda PRINCE2. El enfoque de entrega (predictivo, ágil o híbrido) cambia cómo se trabaja dentro de las etapas, nunca elimina las puertas.</p>"
         + T(X["precedencia"], "", ["22%", "28%", ""])
         + "<h3>¶Problemas de diseño que resuelve</h3>" + tabla_html(["Problema", "Respuesta del paquete"], [[p["p"], p["r"]] for p in D["problemas"]], "", ["38%", ""])
         + "<h3>¶Reglas que el paquete aplica siempre</h3>" + md(X["reglas_siempre"]),
         "patrocinador, PMO")

# ---------- 4 · Representación gráfica ----------
LECTURA_DIAG = {
    "arquitectura": "Cinco capas con dueño propio. Arriba, el gobierno PRINCE2 (orquestador, pm-director y subagentes de fase); debajo, las skills que aplican las técnicas del PMBOK. Las skills leen la especificación BMAD sin escribirla, usan las integraciones opcionales y escriben la carpeta del proyecto solo con `estado.py` y `registro.py`. Los hooks protegen la persistencia y la especificación.",
    "orquestacion-puerta": "Secuencia de una puerta: el orquestador lee el estado (`estado.py resumen · siguiente`) y corre la sanidad; si hay un ERROR, la puerta se bloquea. Delega la producción en un subagente de fase, que devuelve el bloque de retorno con las decisiones humanas requeridas. El orquestador presenta la decisión; con la respuesta de la junta, pm-director la registra con `estado.py puerta …`.",
    "agentes-skills": "Reparto de las skills por agente: pm-director (DP), pm-inicio (SU/IP), pm-planificacion (IP/SB), pm-control (CS/MP) y pm-cierre (CP); las transversales (puente BMAD, estado, sanidad, conocimiento, comunicación, exportación) las usa cualquier agente.",
    "ciclo-de-vida": "Ciclo de vida PRINCE2 con las puertas de la junta: SU → IP con `autorizar-inicio`; IP → CS con `autorizar-proyecto` y `autorizar-etapa`; CS ↔ SB en cada límite de etapa o excepción; cierre (planificado o prematuro) hacia CP y `autorizar-cierre`.",
    "ciclo-prince2-bmad": "Ciclo de vida integrado: en cada fase, lo que produce BMAD (brief, PRD, arquitectura, épicas, veredicto del sprint planning, avance) entra como insumo de los productos PRINCE2 de pm-method, y cada transición pasa por una puerta de la junta. `autorizar-proyecto` exige el PRD final (P-07) y su línea base; `autorizar-etapa` exige PRD y arquitectura finales y lee el gate de preparación de BMAD (FAIL bloquea, CONCERNS es condición). Las decisiones vuelven a BMAD con `bmad.py handoff`.",
    "sincronizacion-bmad": "Fuente única: el equipo de producto escribe BMAD; pm-method lo lee por la fachada (`especificacion.py`, índice `pm-spec-index/1`), fija líneas base con sha256 y copia congelada, y `verificar` detecta desvíos (ESP-10). Un desvío se convierte en solicitud de cambio y, una vez decidida, vuelve a BMAD como documento de traspaso (`bmad.py handoff`).",
}
s4 = sec("graficos", "4", "Representación gráfica del ecosistema",
         "<p class='intro'>Los diagramas oficiales del paquete (<code>docs/diagramas/</code>, fuentes Mermaid y SVG, los mismos del README), insertados tal cual. Cada uno va acompañado de una guía de lectura.</p>"
         + "".join(f"<h3>¶{e(t)}</h3><p>{inl(LECTURA_DIAG[c])}</p>" + diag("repo-" + c) for c, t in [
             ("arquitectura", "Arquitectura por capas"), ("orquestacion-puerta", "Orquestación de una puerta (secuencia)"),
             ("agentes-skills", "Agentes y skills"), ("ciclo-de-vida", "Ciclo de vida PRINCE2 y puertas"),
             ("ciclo-prince2-bmad", "Ciclo de vida integrado: PRINCE2, BMAD y puertas"), ("sincronizacion-bmad", "Sincronización con BMAD")]),
         "todas las audiencias")

# ---------- 5 · Arquitectura ----------
s5 = sec("arquitectura", "5", "Arquitectura",
         f"<p class='intro'>{inl(D['arq_intro'])}</p>" + diag("arq-general")
         + "<h3>¶Capas</h3>" + T(X["capas"], "", ["14%", "16%", "", "18%", "18%"])
         + "<h3>¶Orquestador en el hilo principal y subagentes de fase</h3><p>Se evaluaron cinco diseños. El adoptado da una sola voz ante el usuario, producción aislada por fase y decisiones siempre visibles, a cambio de un protocolo de retorno estricto.</p>"
         + T(X["opciones_agentes"], "", ["22%", "", "", "14%"]) + T(X["reparto_subagentes"], "", ["16%", "14%", "", "30%"])
         + "<h4>Reglas de los subagentes</h4>" + md(X["reglas_subagentes_md"])
         + "<h3>¶Protocolo de retorno</h3><p>Obligatorio al final de cada subagente. El orquestador verifica <i>Hecho</i> contra <code>estado.py ver</code> (ninguna puerta registrada fuera de pm-director), pregunta los <i>Datos faltantes</i>, presenta las <i>Decisiones humanas</i> y vuelve a delegar.</p>"
         + pre(X["retorno"]) + diag("arq-flujo")
         + "<h3>¶Herramientas y MCP heredados</h3><ul>" + "".join(f"<li>{inl(x)}</li>" for x in D["arq_herramientas"]) + "</ul>"
         + "<h4>Correspondencia en Hermes Agent</h4>" + T(X["hermes_equivalencias"], "", ["28%", ""])
         + "<h3>¶Carga progresiva del contexto</h3>" + T(X["carga"]) + "<ul>" + "".join(f"<li>{inl(x)}</li>" for x in D["carga_cifras"]) + "</ul>"
         + "<h3>¶Comandos</h3><p>Toda skill es invocable como comando (<code>/pm-method:&lt;skill&gt;</code> en el plugin; <code>/&lt;skill&gt;</code> en copia manual y Hermes). Seis skills-comando llevan <code>disable-model-invocation: true</code>: el modelo no las activa solo y no consumen presupuesto del listado.</p>"
         + T(X["comandos_arq"], "", ["34%", ""]),
         "mantenedor técnico, PMO")

# ---------- 6 · Columna vertebral ----------
s6 = sec("columna", "6", "Columna vertebral BMAD ↔ PRINCE2",
         f"<p class='intro'>{inl(D['col_intro'])}</p>" + diag("col-vertebral")
         + "<h3>¶Opciones evaluadas y decisión</h3>" + T(X["sync_opciones"], "", ["26%", "", "", "18%"])
         + "<h3>¶Dueño de cada dato</h3><p><code>backlog.csv</code> es la única tabla que combina datos de las dos capas, y cada columna tiene un dueño fijo.</p>" + T(X["sync_duenos"], "", ["30%", "28%", ""])
         + "<h3>¶Mapeo del ciclo de vida</h3>" + layers(D["col_mapeo"])
         + "<h3>¶Fachada única de lectura</h3><p>Ninguna skill abre archivos de BMAD ni <code>requisitos.md</code> para extraer datos. Con <code>integraciones.especificacion = bmad</code> la fachada delega en <code>bmad.py</code>; con cualquier otro valor el proveedor es pm-method (<code>requisitos.md</code>, <code>backlog.csv</code>, <code>wbs.csv</code>) y las skills no cambian. <code>consultar</code> normaliza ids (<code>FR3</code> → <code>FR-3</code>, <code>REQ4</code> → <code>REQ-004</code>).</p>"
         + pre(D["fachada_cmds"]) + "<h4>Contrato <code>pm-spec-index/1</code></h4>" + T(X["spec_index"], "", ["22%", ""]) + diag("sync-cache")
         + "<h3>¶Traspaso de decisiones (gobierno → BMAD)</h3>" + T(X["handoff"], "", ["24%", ""])
         + f"<div class='callout navy'><p><b>Ciclo completo de fuente única.</b> {inl(D['col_ciclo'])}</p></div>"
         + "<h3>¶Líneas base y verificación</h3>" + diag("sync-estados") + T(X["verificar_tipos"], "", ["22%", ""])
         + "<h3>¶Estabilidad de los ids</h3>" + T(X["ids"])
         + "<h3>¶Matriz lee / escribe</h3><p>Lista completa de las skills y comandos que tocan la especificación (fachada = <code>especificacion.py</code>).</p>" + T(X["lee_escribe"], "", ["20%", "", "", "14%"])
         + "<h3>¶Modos de falla y cómo se detectan</h3>" + T(X["fallas"], "", ["24%", "", "", ""]),
         "PMO, mantenedor técnico")

# ---------- 7 · Sanidad ----------
s7 = sec("sanidad", "7", "Sanidad, guardarraíles y seguridad",
         f"<p class='intro'>{inl(D['san_intro'])}</p>" + diag("sanidad") + T(X["controles"], "", ["22%", "20%", "", "12%"])
         + "<h3>¶<code>sanidad.py</code></h3>" + pre(D["san_cmds"]) + "<ul>" + "".join(f"<li>{inl(x)}</li>" for x in D["san_puntos"]) + "</ul>"
         + f"<h3>¶Familias y códigos</h3><p>{CIF['codigos']} códigos en {CIF['familias']} familias ({e(CIF['familias_lista'])}).</p>" + T(X["codigos"], "codigos", ["10%", "14%", "", "30%"], 0)
         + "<h3>¶Hooks (Claude Code, plugin)</h3><p><code>hooks/hooks.json</code> declara los tres hooks (PreToolUse, SessionStart y UserPromptSubmit), que se lanzan con <code>sh \"${CLAUDE_PLUGIN_ROOT}/hooks/py.sh\" …</code>. Corren también dentro de los subagentes; la entrada trae <code>agent_type</code>, y así el guardián distingue a un subagente pm-* del hilo principal, que sí puede escribir en BMAD porque así trabajan los flujos del propio BMAD. El guardián también analiza cada segmento de los comandos Bash, niega los subcomandos de decisión reservados a pm-director (también en el hilo principal) y pide la confirmación de una persona para <code>envios.py aprobar</code> y <code>enviar --confirmar</code>. El hook de inicio agrega el resumen de contexto derivado de los registros (<code>estado.py contexto</code>), declara que los registros prevalecen sobre la memoria del cliente y aplica la regla «fuentes = datos»: las instrucciones incrustadas en transcripciones, tickets o BMAD se informan y no se ejecutan.</p>"
         + T(X["guardian"], "", ["20%", "20%", "", ""]) + "<h4>Resultados de la corrida del caso maestro</h4>" + T(X["guardian_pruebas"], "", ["62%", ""])
         + "<h3>¶Regla de puerta</h3>" + md(X["regla_puerta_md"])
         + "<h4>Cómo evolucionó un ERROR real (FR-5 agregado al PRD sin control)</h4>" + T(X["evolucion_error"], "", ["60%", ""])
         + "<h3>¶Validador del paquete</h3>" + md(X["validador_md"])
         + "<h3>¶Pruebas de regresión</h3>" + md(X["pruebas_md"]) + "<p>Detalle de los casos " + e(X["cifras"]["regresion_casos"]) + ", de la integración cruzada, de las pruebas en vivo y de la lista de aceptación: sección 17.</p>"
         + "<h3>¶Hermes Agent (sin hooks)</h3>" + md(X["hermes_sin_hooks_md"])
         + "<h3>¶Controles permanentes</h3><p>Las familias CAM (cambios contra los presupuestos de la junta), QUA (calidad a volumen), TOL (pronóstico de EVM contra tolerancias) y SUP (supuestos críticos), REG-09 (revisión de riesgos vencida) y STK-12 (cadencia de contacto), junto con G-01, P-04 y P-11 en la verificación de puertas, convierten en controles de cada corrida lo que en la práctica se revisa a mano, tarde o nunca. Tabla problema → control → código → dónde se ve, y ejemplos reales de las guías: <a href='#controles-permanentes'>sección 2, «Controles permanentes»</a>.</p>"
         + f"<h3>¶Seguridad del paquete</h3><p>{inl(X['seg_intro'])} Fuente: <code>docs/SEGURIDAD.md</code>.</p>" + T(X["seg_resultado"], "", ["16%", "12%", "28%", "16%", ""]) + f"<p>{inl(X['seg_resultado_nota'])}</p>"
         + "<h4>Alcance</h4>" + T(X["seg_alcance"], "", ["32%", ""]) + "<h4>Método y herramientas</h4>" + f"<p class='src'>{inl(X['seg_entorno'])}</p>" + T(X["seg_herramientas"], "", ["16%", "12%", ""])
         + "<h4>Modelo de amenazas</h4>" + vin(X["seg_amenazas"])
         + "<h4>Hallazgos con severidad y estado</h4>" + tabla_html(["Id", "Severidad", "Hallazgo", "Estado"], X["seg_hallazgos"], "", ["9%", "11%", "", "28%"])
         + "<div class='two'><div class='callout blue'><h4>Lo que ya está bien (verificado)</h4>" + vin(X["seg_bien"]) + "</div><div class='callout orange'><h4>Buenas prácticas para quien instala</h4><ol>" + "".join(f"<li>{inl(x)}</li>" for x in X["seg_practicas"]) + "</ol></div></div>"
         + "<h4>Cómo repetir la revisión</h4>" + pre(X["seg_repetir"]),
         "PMO, mantenedor técnico, patrocinador (regla de puerta)")

# ---------- 8 · Puertas de la junta ----------
pue_intro = X["pue_intro"].split(" EN:")[0]
s8p = sec("puertas", "8", "Puertas de la junta: verificación y registro",
          f"<p class='intro'>{inl(pue_intro)} Cada puerta de la junta (salvo <code>decision-ad-hoc</code>) se verifica en tres capas antes de decidir, y la decisión queda registrada con la referencia a la lista de control (<code>docs/PUERTAS.md</code>).</p>"
          + "<h3>¶Ciclo de vida integrado: PRINCE2 (gobierno) y BMAD (especificación)</h3><p>" + inl(LECTURA_DIAG["ciclo-prince2-bmad"]) + "</p>" + diag("repo-ciclo-prince2-bmad")
          + "<h4>Componentes en el ciclo de vida</h4>" + T(X["pue_componentes"], "", ["32%", "30%", ""])
          + "<h3>¶Cómo se verifica una puerta</h3>" + diag("repo-verificacion-puertas") + f"<p>{inl(X['pue_capas_intro'])}</p><ol>" + "".join(f"<li>{inl(c)}</li>" for c in X["pue_capas"]) + "</ol>"
          + "<h3>¶Controles automáticos por puerta</h3><p>Ids: <code>S-</code> salud, <code>I-</code> autorizar-inicio, <code>P-</code> autorizar-proyecto, <code>E-</code> autorizar-etapa, <code>X-</code> autorizar-plan-excepcion y <code>C-</code> autorizar-cierre.</p>" + T(X["pue_controles"], "", ["18%", "12%", "", "12%"]) + f"<div class='callout blue'><p>{inl(X['pue_criterios_exito'])}</p></div>"
          + f"<h3>¶{e(X['pue_bmad_titulo'])}</h3>" + T(X["pue_bmad"], "dec", ["22%", "38%", ""]) + f"<p>{inl(X['pue_bmad_nota'])}</p>"
          + f"<h3>¶Las puertas como insumo de los informes</h3><p>{inl(X['pue_informes_intro'])}</p>" + T(X["pue_informes"], "", ["24%", "42%", ""])
          + f"<h3>¶Severidades y registro de la decisión</h3><div class='callout navy'><p>{inl(X['pue_severidades'])}</p></div>"
          + f"<h3>¶Códigos de control en la verificación</h3><p>{inl(X['pue_verificar'])}</p>"
          + f"<h3>¶Condiciones formales y su seguimiento</h3><p>{inl(X['pue_condiciones_intro'])}</p><ol>" + "".join(f"<li>{inl(c)}</li>" for c in X["pue_condiciones"]) + "</ol>"
          + "<p class='src'>Ejemplo en la guía E2E-4: el CONCERNS del gate de preparación de BMAD pasa a condición de <code>autorizar-etapa</code>, la sanidad muestra EST-12 en cada corte y G-01 desaparece con <code>cumplir-condiciones</code> (sección 2, «Ejemplos reales de la evidencia»).</p>"
          + "<h3>¶Comandos</h3>" + pre(X["pue_comandos"]),
          "patrocinador, PMO, mantenedor técnico")

# ---------- 8 · Componentes ----------
C = X["compatibilidad"]
SE = C["integraciones_externas_opcionales"].get("skills_probadas_en_vivo", {})
compat = f"""<div class="two"><div class="callout blue"><h4>compatibilidad.json</h4><ul>
<li><b>Paquete:</b> {e(C['paquete'])} {e(C['version'])} · spec {e(C['spec'])}</li>
<li><b>Esquemas:</b> {e('; '.join(f'{k}: {v}' for k, v in C['esquemas'].items()))}</li>
<li><b>BMAD probado:</b> {e(', '.join(C['bmad']['probado']))} · relevado {e(C['bmad']['relevado'])}</li>
<li><b>Fuera de rango:</b> {e(C['bmad']['fuera_de_rango'])}</li>
<li><b>Python:</b> {e(C['python'])}</li>
<li><b>Skills externas probadas en vivo:</b> {e(SE.get('fecha', ''))}, Claude Code {e(SE.get('claude_code', ''))}: {e(', '.join(k for k in SE if isinstance(SE[k], dict)))}</li></ul></div>
<div class="callout orange"><h4>Conducta por cliente</h4><ul>{''.join(f'<li><b>{e(k)}:</b> {e(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))}</li>' for k, v in C['clientes'].items())}</ul>
<h4>Integraciones externas opcionales</h4><p><b>Skills:</b> {e(', '.join(C['integraciones_externas_opcionales']['skills']))}</p><p><b>MCP:</b> {e(', '.join(C['integraciones_externas_opcionales']['mcp']))}</p></div></div>"""
s8 = sec("componentes", "9", "Componentes del paquete",
         "<p class='intro'>Principio rector: <b>el núcleo funciona sin nada externo</b>. Cada integración es un contrato de insumo y salida con un respaldo interno (Mermaid, CSV, scripts propios): si la herramienta externa no está o falla, la skill sigue con el respaldo y lo anota.</p>"
         + "<h3>¶Componentes</h3>" + layers(D["componentes"]) + T(X["idx_componentes"], "", ["30%", "", "30%"])
         + "<h3>¶Scripts compartidos</h3><p>Su motor son scripts deterministas en Python: dan el mismo resultado para la misma entrada, validan valores y dejan traza. Todos aceptan <code>--proyecto &lt;dir&gt;</code> (o un archivo, en <code>wbs.py</code>, <code>cpm.py</code>, <code>okr.py</code> y <code>transcripcion.py</code>).</p>"
         + T(X["scripts_compartidos"], "scripts", ["13%", "25%", ""]) + "<h4>Scripts de otras skills</h4>" + T(X["scripts_otros"], "scripts", ["22%", "22%", ""])
         + "<h4>Scripts del mantenedor y hooks</h4>" + T(X["scripts_mantenedor"], "", ["26%", "16%", ""])
         + "<h3>¶Manifiesto de compatibilidad</h3>" + compat
         + "<h3>¶Plugins, skills y MCP opcionales: decisión de integración</h3><p>Los candidatos provienen del informe 1; la valoración en estrellas es la de ese informe.</p>"
         + T(X["decisiones_integracion"], "dec", ["14%", "8%", "18%", "13%", ""])
         + "<h3>¶Contrato de cada integración</h3><p>Cada integración se declara en <code>estado.json.integraciones</code> y cumple tres reglas: insumo preparado por la skill dueña, salida guardada en la carpeta del proyecto y respaldo interno.</p>"
         + T(X["contratos"], "dec", ["10%", "14%", "11%", "", "", ""]),
         "mantenedor técnico, PMO")

# ---------- 9 · Dependencias ----------
DEP_W = ["12%", "16%", "10%", "12%", "12%", "17%", ""]
def dep_tabla():
    cab = ["Nombre", "Para qué lo usa pm-method", "Nivel", "Versión probada", "Licencia", "URL de origen", "Instalación"]
    filas = []
    for t, k in [("1.1 Cliente (al menos uno)", "dep_clientes"), ("1.2 Herramientas de base", "dep_base"), ("2 · Paquetes Python recomendados", "dep_python"),
                 ("3 · Herramientas opcionales", "dep_opcionales"), ("4.1 El paquete y la capa de especificación", "dep_bmad"),
                 ("4.2 Skills externas (diagramas y Office)", "dep_skills"), ("4.3 draw.io", "dep_drawio")]:
        filas.append([f"**{t}**"] + [""] * 6)
        filas += X[k]["filas"]
    return tabla_html(cab, filas, "dep", DEP_W, 0)
s9 = sec("dependencias", "10", "Dependencias",
         "<p class='intro'>Lista completa de lo que pm-method necesita o puede usar, con la URL de origen de cada elemento, el nivel, la versión probada, la licencia y el comando de instalación, tal como figura en <code>docs/DEPENDENCIAS.md</code>. Las marcas <b>[verificar]</b> y <b>\"URL a confirmar por el usuario\"</b> se conservan sin cambios: indican lo que no se pudo comprobar desde el entorno de verificación.</p>"
         + "<h3>¶Convenciones</h3>" + md(sin_cita(X["dep_convenciones_md"]))
         + "<h3>¶Qué instalar según el uso</h3>" + T(X["dep_resumen"], "", ["45%", ""])
         + f"<div class='callout orange'><p><b>Node.js: versión mínima efectiva.</b> {inl(X['dep_node_md'])}</p></div>"
         + "<h3>¶Tabla de dependencias</h3>" + dep_tabla() + f"<p class='src'>{inl(X['dep_clientes_nota_md'])}</p>"
         + "<h3>¶Conectores MCP opcionales</h3><p>pm-method no trae <code>.mcp.json</code> ni credenciales y no predefine conectores: <code>pm-integraciones</code> resuelve capacidades (<code>tracker</code>, <code>docs</code>, <code>chat</code>, <code>reuniones</code>, <code>okr</code>, <code>diagramas</code>) con los servidores conectados en la sesión.</p>"
         + T(X["dep_mcp"], "dep", ["13%", "12%", "12%", "11%", "12%", "20%", ""])
         + "<h3>¶Dónde se declara cada dependencia en el paquete</h3>" + T(X["dep_declara"], "", ["32%", ""])
         + "<h3>¶Cómo se verificó</h3><p>" + inl(X["dep_ver_intro_md"].replace("\n", " ")) + "</p>"
         + "<details><summary>Repositorios GitHub comprobados con <code>git ls-remote</code> (" + str(len(X["dep_ver_repos"]["filas"])) + ")</summary>" + T(X["dep_ver_repos"], "", ["26%", "14%", ""]) + "</details>"
         + "<details><summary>Paquetes npm (" + str(len(X["dep_ver_npm"]["filas"])) + ")</summary>" + T(X["dep_ver_npm"]) + "</details>"
         + "<details><summary>Paquetes PyPI (" + str(len(X["dep_ver_pypi"]["filas"])) + ")</summary>" + T(X["dep_ver_pypi"]) + "</details>"
         + "<h4>No verificadas</h4>" + vin(X["dep_no_verificadas"]),
         "mantenedor técnico, quien integra herramientas, PMO")

# ---------- 10 · Instalación ----------
vias = tabla_html(["Vía", "Cómo", "Hooks"], [[f"**{v['t']}**", v["d"], v["hooks"]] for v in D["inst_vias"]], "", ["18%", "", "22%"])
paso = lambda n, t, cuerpo: f"<div class='step'><span>{n}</span><div><h4>{t}</h4>{cuerpo}</div></div>"
s10 = sec("instalacion", "11", "Guía de instalación y configuración",
          f"<p class='intro'>{inl(D['inst_intro'])}</p><p class='src'>Las referencias «§» dentro de los bloques citados remiten a <code>docs/INSTALACION.md</code>. Comandos comprobados el 17/10/2026 con Claude Code 2.1.302.</p>"
          + "<h3>¶Recorrido de punta a punta</h3>" + T(X["inst_recorrido"], "", ["8%", "", "14%"]) + "<h4>Vías de instalación</h4>" + vias
          + "<h3>¶Requisitos previos por sistema operativo</h3>" + T(X["inst_requisitos_so"], "", ["20%", "22%", "", ""])
          + "<div class='two'><div class='callout blue'><h4>Windows (Git for Windows + PowerShell)</h4>" + md(X["req_windows_md"]) + "</div><div><div class='callout blue'><h4>macOS</h4>" + md(X["req_macos_md"]) + "</div><div class='callout blue'><h4>Linux</h4>" + md(X["req_linux_md"]) + "</div></div></div>"
          + "<h3>¶Instalación desde GitHub (recomendada)</h3>" + md(antes_de_h3(X["gh_intro_md"]))
          + "<div class='steps'>" + paso(1, "Credenciales de GitHub", md(X["gh_credenciales_md"]))
          + paso(2, "Claude Code (cada integrante)", md(X["gh_claude_md"]))
          + paso(3, "Actualizar", md(X["gh_actualizar_md"]))
          + paso(4, "Hermes Agent", md(X["gh_hermes_md"]))
          + paso(5, "Publicar una versión (responsable del paquete)", md(X["gh_publicar_md"]))
          + paso(6, "Verificar", "<p>Seguir la verificación de 12 pasos de esta sección.</p>") + "</div>"
          + "<h3>¶Credenciales y claves de API (API-KEY)</h3>" + md(X["credenciales_md"])
          + "<h3>¶Orca (opcional): varios agentes y proyectos en paralelo</h3>" + md(X["orca_md"])
          + "<h3>¶Instalación desde una carpeta local, Cowork y Hermes</h3><h4>Plugin desde el marketplace local</h4>" + md(X["local_plugin_md"])
          + "<h4>Copia manual (sin plugin)</h4>" + md(X["local_copia_md"]) + "<h4>Cowork</h4>" + md(X["cowork_md"]) + "<h4>Hermes Agent desde carpeta local</h4>" + md(X["hermes_local_md"])
          + "<h3>¶Paquetes Python</h3>" + md(X["python_dep_md"])
          + "<h3>¶BMAD en el repositorio del producto (opcional)</h3>" + md(antes_de_h3(X["bmad_inst_md"])) + "<h4>Instalar BMAD (versión probada)</h4>" + md(X["bmad_instalar_md"])
          + "<h4>Detectar BMAD desde pm-method</h4>" + md(X["bmad_detectar_md"]) + "<h4>Compatibilidad y actualización de BMAD</h4>" + md(X["bmad_compat_md"])
          + "<h3>¶Skills externas: instalación y declaración</h3>" + md(X["skills_ext_md"])
          + "<h3>¶Conectores MCP</h3><p>El paquete <b>no trae <code>.mcp.json</code> ni credenciales</b> y no predefine conectores. Las skills describen capacidades y <code>pm-integraciones</code> las resuelve con los MCP presentes en la sesión.</p><h4>Paso 1: conectar el servidor en el cliente</h4>" + md(X["mcp_paso1_md"])
          + "<h4>Paso 2: declarar la capacidad en el proyecto</h4>" + md(X["mcp_paso2_md"])
          + "<h4>Herramientas opcionales del sistema</h4>" + T(X["herramientas_sistema"], "", ["18%", "", "", ""])
          + "<h3>¶Configuración</h3><h4>Ubicación de los scripts</h4>" + T(X["rutas_scripts"], "", ["28%", ""])
          + "<h4>Crear un proyecto e idioma</h4>" + md(X["config_proyecto_md"]) + "<h4>Umbrales de riesgo y tolerancias</h4>" + md(X["config_tolerancias_md"])
          + "<h4>Settings recomendados en Claude Code</h4>" + md(X["config_settings_md"]) + "<h4>Orquestador en el hilo principal</h4>" + md(X["config_orq_md"])
          + "<h4>Primer uso</h4>" + pre(D["inst_inicio"])
          + "<h3>¶Verificación de la instalación (12 pasos)</h3>" + T(X["verificacion"], "", ["4%", "18%", "34%", ""]) + "<p class='src'>Paso 5: resultado vigente " + str(CIF['regresion_ok']) + " OK · 0 FALLO con Python " + CIF['regresion_py'] + " y " + str(CIF['regresion_ok39']) + " con 3.9 (PRUEBAS.md §2).</p>"
          + "<h4>Hallazgos de instalación esperables (familia INS)</h4>" + T(X["ins_esperados"], "", ["10%", "34%", ""])
          + "<h3>¶Hooks instalados</h3>" + md(X["hooks_md_md"])
          + "<h3>¶Actualización, migración y desinstalación</h3>" + md(X["actualizacion_md"]) + md(X["desinstalacion_md"])
          + "<h3>¶Solución de problemas</h3>" + T(X["problemas"], "", ["28%", "26%", ""])
          + f"<h3 id='docker'>¶Entorno Docker opcional</h3><p>{inl(X['dock_intro'])}</p><p class='src'>Fuente: <code>docs/DOCKER.md</code>.</p>"
          + "<h4>Cuándo conviene</h4>" + T(X["dock_cuando"], "", ["60%", ""]) + "<h4>Qué incluye</h4>" + T(X["dock_incluye"], "", ["16%", "", "34%"])
          + "<h4>Archivos</h4>" + T(X["dock_archivos"], "", ["34%", ""])
          + "<h4>Construir, usar y probar</h4>" + pre(X["dock_construir"]) + pre(X["dock_usar"]) + pre(X["dock_pruebas"])
          + "<h4>Seguridad del contenedor</h4>" + T(X["dock_seguridad"], "", ["24%", "26%", ""])
          + f"<h4>Verificación registrada</h4><p>{inl(X['dock_verif_intro'])}</p>" + T(X["dock_verif"], "", ["38%", "", "10%"]) + f"<p class='src'>{inl(X['dock_verif_no'])}</p>"
          + "<h4>Limitaciones</h4>" + vin(X["dock_limitaciones"]),
          "PM no programador, mantenedor técnico")

# ---------- 11 · Catálogo ----------
def ficha_skill(s):
    filas = "".join(f"<li><b>{inl(c)}:</b> {inl(v)}</li>" for c, v in s["campos"] if c not in ("Usar",))
    return f"""<article class="card" id="sk-{s['nombre']}"><h4><code>{e(s['nombre'])}</code></h4><p class="tema">{inl(s['tema'])}</p>
<ul>{filas}</ul><p class="usar"><b>Usar:</b> {inl(s.get('usar', ''))}<br><b>No:</b> {inl(s.get('no', ''))}</p></article>"""


def ficha_agente(nombre, campos):
    return f'<article class="card"><h4><code>{e(nombre)}</code></h4><ul>' + "".join(f"<li><b>{inl(c)}:</b> {inl(v)}</li>" for c, v in campos) + "</ul></article>"


grupos_html = ""
for g in X["catalogo"]:
    com = "".join(f'<div class="callout blue"><p><b>{inl(c["t"].split(chr(10))[0])}.</b> {inl(" ".join(c["t"].split(chr(10))[1:]) + " " + c["md"])}</p></div>' for c in g["comandos"])
    grupos_html += f'<h3 id="cat-{g["id"]}">¶{e(g["titulo"])} — {len(g["skills"])} skills</h3><div class="cards">' + "".join(ficha_skill(s) for s in g["skills"]) + "</div>" + com
s11 = sec("catalogo", "12", "Catálogo de agentes y skills",
          "<p class='intro'>6 agentes y " + str(len(X['skills_dirs'])) + " skills: " + str(X['catalogo_total']) + " que el modelo activa por su descripción y 6 comandos de uso humano. Cada ficha sale de <code>docs/CATALOGO.md</code> (que a su vez resume el frontmatter y el cuerpo de cada SKILL.md); el tema del que es dueña cada skill sale de <code>docs/colisiones.md</code>. Todas las skills comparten la regla de idioma: responder en el idioma del usuario y escribir los artefactos en <code>estado.json.idioma</code>.</p>"
          + "<h3>¶Agentes</h3>" + T(X["agentes"], "", ["14%", "18%", "", "14%", "18%"])
          + "<div class='cards'>" + "".join(ficha_agente(n, c) for n, c in X["fichas_agentes"].items()) + "</div>"
          + "<h3>¶Comandos de uso humano</h3>" + T(X["comandos"], "", ["10%", "18%", "", "18%", "10%"])
          + "<h3>¶Skills por agente y fase</h3><p>Formato de cada ficha: <b>Produce</b> (artefactos y ruta), <b>PRINCE2</b> (procesos · prácticas), <b>PMBOK como cómo</b>, <b>Plantillas</b>, <b>Scripts</b>, <b>Lee de la fachada</b> y la pista de activación <b>Usar / No</b>.</p>"
          + grupos_html
          + "<h3>¶Reparto por agente (control de totales)</h3>" + T(X["reparto_agentes"], "", ["18%", "", "8%"])
          + "<h3>¶Pares sensibles y criterio para separarlos</h3>" + T(X["pares_sensibles"], "", ["30%", ""]),
          "PM no programador, PMO")

# ---------- 12 · RACI ----------
R = X["raci"]
s12 = sec("raci", "13", "Matriz RACI",
          "<p class='intro'>Quién hace qué a lo largo del ciclo de vida cuando se trabaja con los agentes del paquete. La matriz cruza los roles humanos del método con los seis agentes y nombra las skills que ejecutan cada actividad; está verificada contra SPEC, <code>agents/*.md</code> y los procedimientos de las skills.</p>"
          + "<h3>¶Reglas</h3>" + md(X["raci_reglas_md"]) + "<h3>¶Leyenda</h3>" + md(X["raci_leyenda_md"])
          + f"<h3>¶Matriz principal ({sum(1 for f in R['filas'] if len([c for c in f if c]) > 1)} actividades)</h3>" + tabla_html(R["cab"], R["filas"], "raci", None, 1)
          + "<h4>Cómo se leen algunas filas</h4>" + md(X["raci_lectura_md"])
          + "<h3>¶Decisiones sensibles: skills × humanos</h3><p>Solo las decisiones que cambian líneas base, comprometen dinero, salen del proyecto o afectan a personas. En todas, el agente prepara y el humano decide; la última columna dice qué script deja la constancia y qué agente lo ejecuta después de la decisión.</p>"
          + T(X["raci_sensibles"], "raci2") + md(X["raci_sensibles_notas_md"])
          + "<h3>¶Verificación de consistencia</h3>" + T(X["raci_verif"], "", ["24%", "", "22%"]),
          "patrocinador, PMO")

# ---------- 13 · Casos de uso ----------
CR = D["casos_resumen"]
resumen_casos = tabla_html(["#", "Skill", "Agente", "Resultado"], [[str(c["n"]), f"`{c['comando']}`", CR[str(c["n"])][0], CR[str(c["n"])][1]] for c in X["casos"]], "", ["4%", "24%", "18%", ""])


def caso_html(c):
    cmds = pre(c["comandos"]) if c["comandos"] else f"<p>{inl(c['comandos_txt'])}</p>"
    resp = f"<dt>Respuestas del usuario</dt><dd>{md(c['respuestas'])}</dd>" if c.get("respuestas") else ""
    return f"""<article class="card caso" id="caso-{c['n']}"><h4><span class="num">{c['n']}</span> <code>{e(c['comando'])}</code> — {e(c['titulo'])}</h4>
<dl><dt>Prompt del usuario</dt><dd>{md(c['peticion'])}</dd>{resp}<dt>Quién</dt><dd>{inl(c['quien'])}</dd><dt>Qué pregunta o verifica</dt><dd>{inl(c['verifica'])}</dd>
<dt>Comandos (los ejecuta el sistema)</dt><dd>{cmds}</dd><dt>Entradas (qué aporta el usuario y cómo)</dt><dd>{md(c['entradas'])}</dd><dt>Salidas (qué queda y dónde verificarlo)</dt><dd>{md(c['artefacto'])}</dd><dt>Decisión humana</dt><dd>{inl(c['decision'])}</dd></dl></article>"""


detalle, parte = "", None
for c in X["casos"]:
    if c["parte"] != parte:
        parte = c["parte"]
        detalle += f"<h4 class='parte'>{e(parte)}</h4>"
    detalle += caso_html(c)
s13 = sec("casos", "14", "Casos de uso: un ejemplo por skill",
          "<p class='intro'>" + str(X['cifras']['casos_uso']) + " casos documentados: " + str(len(X['casos'])) + " ejemplos trabajados uno por cada una de las " + str(len(X['skills_dirs'])) + " skills, incluidos los seis comandos, y los casos transversales de la parte 6 (interesados, canales, OKR, riesgos, controles permanentes y mapas estratégicos), sobre un mismo proyecto de muestra para que los casos se encadenen de principio a fin, y la parte 7 (casos " + X['casos_p7']['filas'][0][0].split(' ')[0] + " a " + X['casos_p7']['filas'][-1][0].split(' ')[0] + "), que remite cada capacidad para decidir con datos al paso de la guía E2E donde se recorre. Las cifras coinciden con lo que devolvieron los scripts en la prueba; las personas y la cooperativa son ficticias y las respuestas humanas, simuladas. Regla transversal: cuando un subagente necesita una decisión la devuelve en su bloque de retorno; el orquestador la presenta a la persona con el rol que decide y, con la respuesta explícita, invoca a pm-director.</p>"
          + "<h3>¶Proyecto de muestra</h3>" + T(X["muestra"], "", ["28%", ""])
          + f"<h3>¶Resumen de los {len(X['casos'])} casos</h3>" + resumen_casos
          + "<h3>¶Detalle de cada caso</h3>" + detalle
          + f"<h3>¶{e(X['casos_p7_titulo'])}</h3><p>{inl(X['casos_p7_intro'])}</p>" + T(X["casos_p7"], "", ["16%", "26%", "22%", "16%", ""])
          + "<h3>¶Variantes</h3><h4>Variante A · Predictivo sin BMAD</h4><p>" + inl(X["variante_a"]["intro"]) + "</p>" + T(X["variante_a"]["tabla"], "", ["9%", "26%", "15%", "", "22%"])
          + "<h4>Variante B · Proyecto ágil en inglés</h4><p>" + inl(X["variante_b"]["intro"]) + "</p>" + T(X["variante_b"]["tabla"], "", ["9%", "26%", "15%", "", "22%"])
          + "<h4>Variante C · Jira y Teams conectados vía pm-integraciones</h4>" + md(X["variante_c_md"]),
          "PM no programador")

# ---------- 14 · Casos de uso por integración ----------
def ficha_cui(titulo, campos, id_):
    filas = "".join(f"<dt>{e(k)}</dt><dd>{md(v)}</dd>" for k, v in campos)
    return f'<article class="card caso" id="{id_}"><h4>{inl(titulo)}</h4><dl>{filas}</dl></article>'


cui_html = ""
for c in X["cui_casos"]:
    cui_html += f"<h3 id='cui-{c['n']}'>¶Caso {c['n']} · {inl(c['titulo'])}</h3>"
    if c["intro_md"]:
        cui_html += md(c["intro_md"])
    if c["campos"]:
        cui_html += ficha_cui(c["titulo"], c["campos"], f"cui-{c['n']}-f")
    for s_ in c["subs"]:
        cui_html += ficha_cui(f"<span class='num'>{s_['id']}</span> {s_['titulo']}", s_["campos"], "cui-" + s_["id"].replace(".", "-"))
s14 = sec("casos-integraciones", "15", "Casos de uso por repositorio integrado",
          f"<p class='intro'>{inl(X['cui_intro_md'].replace(chr(10), ' '))}</p><div class='notice'><b>Regla de evidencia.</b> {inl(X['cui_evidencia_md'].replace('Regla de evidencia de este documento. ', '').replace(chr(10), ' '))}</div>"
          + "<h4>Estados de verificación</h4>" + vin(X["cui_estados"])
          + "<h3>¶Qué repositorio cubre cada caso</h3>" + T(X["cui_repos"], "", ["8%", "34%", "26%", ""])
          + "<h4>Ejemplos reales guardados en <code>docs/ejemplos/integraciones/</code></h4>" + T(X["cui_ejemplos"], "", ["44%", ""])
          + cui_html
          + "<h3>¶Matriz de cierre: integración × skill × agente × respaldo × control × verificación</h3>" + T(X["cui_matriz"], "dec", ["13%", "15%", "14%", "16%", "14%", ""])
          + f"<div class='callout navy'><p><b>Controles transversales.</b> {inl(X['cui_transversal_md'].replace('Controles transversales: ', '').replace(chr(10), ' '))}</p></div>",
          "PM no programador, quien integra herramientas, PMO")

# ---------- 15 · Caso maestro ----------
pasos_clave = tabla_html(["Paso", "Momento PRINCE2 · técnica", "Qué se hizo", "Resultado (cifras reales)"],
                         [[p["n"], p["m"], p["t"], p["r"]] for p in D["pasos_clave"]], "", ["7%", "22%", "24%", ""])
pasos_html, etapa = "", None
for p in X["pasos"]:
    if p["etapa"] != etapa:
        etapa = p["etapa"]
        pasos_html += f"<h4 class='parte'>{e(etapa)}</h4>"
    c = p["campos"]
    filas = "".join(f"<dt>{e(k)}</dt><dd>{inl(v)}</dd>" for k, v in c.items())
    extra = f"<details><summary>Comandos y salidas</summary>{md(p['resto_md'])}</details>" if p["resto_md"] else ""
    pasos_html += f'<article class="card caso"><h4><span class="num">{p["n"]}</span> {inl(p["titulo"])}</h4><dl>{filas}</dl>{extra}</article>'
s15 = sec("caso-maestro", "16", "Caso maestro, guías E2E y formación",
          "<p class='intro'>Un proyecto completo, del mandato a la revisión de beneficios, corrido el 17/10/2026 con los scripts del paquete sobre una copia del fixture <code>bmad-v6</code>. Cada paso muestra el momento PRINCE2, la técnica del PMBOK que lo resuelve, quién decide, el comando y lo que devolvió. Las decisiones humanas están simuladas.</p>"
          + "<h3>¶Escenario</h3>" + T(X["escenario"], "", ["30%", ""])
          + "<h3>¶Cifras clave</h3>" + layers([{"t": c["k"], "d": c["v"]} for c in D["caso_cifras"]])
          + diag("caso-ciclo")
          + "<h3>¶Pasos clave</h3>" + pasos_clave
          + "<h3>¶Paso a paso completo</h3>" + pasos_html + diag("caso-wbs")
          + "<h3>¶Guías de recorrido de punta a punta para el usuario</h3><p>" + str(CIF['guias']) + " guías (" + str(CIF['pasos']) + " pasos) en <code>docs/guias/</code> escritas como prompts del usuario: qué escribir, qué responder cuando el sistema pregunta, qué deberías ver (con cifras de una corrida de referencia reproducible con <code>scripts/pruebas/guias_e2e/correr.py</code>) y dónde verificar cada registro. Cada una termina con un reporte de ejemplo y representaciones gráficas.</p>"
          + T(X["guias"], "", ["20%", "", "", "", "9%"]) + "<h4>Cómo leer cada paso</h4>" + T(X["guias_leer"], "", ["22%", ""])
          + "<h4>Del uso único al control continuo</h4><p>Cada guía compara, actividad por actividad, cómo se hace hoy (a mano, una vez o nunca) con la frecuencia y el control de pm-method y el indicador que lo muestra.</p>"
          + "".join(f"<details><summary>{e(g)} · {e(X['guias_titulos'][g])} ({len(t['filas'])} actividades)</summary>" + T(t, "dec") + "</details>" for g, t in X["guias_controles"].items())
          + "<h4>Indicadores que vas a ver (imágenes de la corrida real)</h4>"
          + "".join(f"<h4 class='parte'>{e(g)} · {e(X['guias_titulos'][g])}</h4><div class='galeria'>" + "".join(f"<figure><img class='captura' src='{img64('../../guias/img/' + it['img'])}' alt='{e(it['alt'])}' loading='lazy'><figcaption>{inl(it['lectura'])} · <code>{e(it['img'])}</code></figcaption></figure>" for it in its) + "</div>" for g, its in X["guias_indicadores"].items())
          + f"<h3>¶Material de formación: webinar y resumen ejecutivo</h3><p>{inl(X['web_intro'])}</p>" + T(X["web_casos"], "", ["8%", "22%", "18%", "", "10%", "10%"])
          + f"<p class='src'>{inl(X['web_casos_nota'])}</p><h4>Qué agrega el generador</h4>" + vin(X["web_agrega"]) + pre(X["web_estructura"])
          + "<h4>Resumen ejecutivo comercial</h4>" + vin(X["rex_items"]) + pre(X["rex_regenerar"])
          + "<h3>¶Dónde apareció cada principio de PRINCE2</h3>" + T(X["principios"], "", ["20%", "", "28%"])
          + "<h3>¶Lecciones del caso</h3>" + md(X["lecciones_caso_md"])
          + "<h3>¶Integridad al final</h3>" + md(X["integridad_md"]),
          "patrocinador, PMO, PM no programador")

# ---------- 16 · Pruebas y calidad ----------
acept = "<ol class='check'>" + "".join(f"<li>☐ {inl(x)}</li>" for x in X["pru_aceptacion"]) + "</ol>"
s16 = sec("pruebas", "17", "Pruebas y calidad",
          "<p class='intro'>Cómo se verifica el ecosistema, qué cubre cada prueba, qué resultados quedaron registrados y cómo hacer la prueba de aceptación antes de usarlo en un proyecto real (<code>docs/PRUEBAS.md</code>). La regresión da <b>" + str(CIF['regresion_ok']) + " OK · 0 FALLO</b> con Python " + CIF['regresion_py'] + " (" + str(CIF['regresion_ok39']) + " con 3.9) y la integración cruzada <b>" + str(CIF['integ_ok']) + " OK · 0 FALLO</b> en " + str(CIF['integ_eslabones']) + " eslabones (" + e(FECHA_P) + "). Las pruebas en vivo con Claude Code real de la versión " + e(CIF['version']) + " (" + e(CIF['vivo24_fechas']) + ") dan <b>" + str(CIF['vivo24_ok']) + "/" + str(CIF['vivo24_total']) + "</b> en las frases " + str(CIF['vivo24_desde']) + "–" + str(CIF['vivo24_hasta']) + " y de control, y " + str(CIF['vivo24_reg_ok']) + "/" + str(CIF['vivo24_reg_total']) + " de regresión; la integración con BMAD instalado (" + CIF['vivo_integracion'] + ") es del 20/10/2026 y los escenarios de robustez, del 17/10/2026.</p>"
          + "<h3>¶Niveles de prueba</h3>" + T(X["pru_niveles"], "", ["20%", "38%", "16%", ""])
          + "<h3>¶Regresión determinista: casos " + e(CIF["regresion_casos"]) + "</h3>" + T(X["pru_regresion"], "", ["22%", ""]) + md(X["pru_regresion_res_md"])
          + f"<h3>¶Integración cruzada</h3><p>{inl(X['pru_integ_intro'])}</p>" + T(X["pru_integ"], "", ["16%", "30%", ""]) + pre(X["pru_integ_cmds"]) + f"<p>{inl(X['pru_integ_res'])}</p>"
          + "<h3>¶Recorridos E2E reproducibles</h3>" + T(X["pru_e2e"], "", ["10%", "22%", ""]) + f"<p>Resultado al {e(X['pru_e2e_res'][0])}: <b>{e(X['pru_e2e_res'][1])}</b>, {e(X['pru_e2e_res'][2])}.</p>"
          + f"<h3>¶Compatibilidad con Python 3.9</h3><p>{inl(X['pru_py39_intro'])}</p>" + pre(X["pru_py39_cmds"]) + f"<p>{inl(X['pru_py39_res'])}</p>" + pre(X["validar_salida"])
          + "<h3>¶Pruebas en vivo con Claude Code real</h3>" + md(X["pru_vivo_md"])
          + "<h3>¶Resultados registrados</h3>" + T(X["pru_resultados"], "", ["11%", "8%", "24%", ""]) + md(X["pru_resultados_nota_md"]) + ("<p class='src'>Filas marcadas como pendientes: el documento fuente todavía tiene el marcador sin el resultado.</p>" if X["pru_placeholders"] else "")
          + "<details><summary>Batería base de enrutamiento (2026-10-17, versión 2.1.0, primera corrida): las 60 frases y la skill elegida (59/60; la corrida final dio 60/60)</summary>" + T(X["pru_suite_enrut"], "", ["5%", "", "22%", "22%", "8%"]) + "</details>"
          + "<h4>Antecedente: evaluación ciega de las descripciones (v2.0, docs/ARQUITECTURA.md §8.3)</h4>" + T(X["evaluacion"]) + f"<p>El conjunto de frases creció de 52 a {X['frases_eval']} y ahora se corre en vivo con <code>suite.py</code>.</p>"
          + "<h3>¶Casos de uso documentados (pruebas manuales guiadas)</h3>" + T(X["pru_casos"], "", ["34%", ""])
          + "<h3>¶Prueba de aceptación antes del primer proyecto real</h3><p>Marcar cada punto en una carpeta de prueba, no en el proyecto real.</p>" + acept + md(X["pru_aceptacion_nota_md"]),
          "patrocinador, PMO, PM no programador, mantenedor técnico")

# ---------- 17 · Plan de piloto ----------
s17p = sec("piloto", "18", "Plan de piloto",
          f"<p class='intro'>{inl(X['pil_intro'])} Lo que el laboratorio no puede probar (Windows real, conectores reales, usuarios no técnicos, calidad experta, varias semanas) se evalúa en un piloto real (<code>docs/PILOTO.md</code>).</p>"
          + "<h3>¶Objetivo y preguntas que debe responder</h3>" + T(X["pil_preguntas"], "", ["50%", ""])
          + "<h3>¶Alcance y modalidad</h3>" + vin(X["pil_alcance"])
          + "<h3>¶Fases</h3>" + T(X["pil_fases"], "", ["14%", "8%", "", "24%"])
          + "<h3>¶Métricas del registro semanal</h3>" + T(X["pil_metricas"], "", ["18%", "", "28%"])
          + "<h4>Plantilla de registro semanal</h4>" + T(X["pil_registro"])
          + f"<h3>¶Rúbrica de revisión experta</h3><p>{inl(X['pil_rubrica_intro'])}</p>" + T(X["pil_rubrica"], "dec", ["20%", "20%", "20%", "20%", ""]) + f"<div class='callout orange'><p>{inl(X['pil_rubrica_res'])}</p></div>"
          + f"<h3>¶Prueba de usabilidad</h3><p>{inl(X['pil_usab_intro'])}</p><ol>" + "".join(f"<li>{inl(t)}</li>" for t in X["pil_usab_tareas"]) + f"</ol><p>{inl(X['pil_usab_medir'])}</p>"
          + "<h3>¶Riesgos del piloto y mitigaciones</h3>" + T(X["pil_riesgos"], "", ["34%", ""])
          + "<h3>¶Criterios de decisión al cierre</h3>" + vin(X["pil_criterios"]) + f"<p>{inl(X['pil_cierre'])}</p>",
          "patrocinador, PMO, PM no programador")

# ---------- 17 · Índice de documentación ----------
s17 = sec("indice-doc", "19", "Índice de documentación y pruebas",
          "<p class='intro'>Mapa de todo lo que hay en el repositorio para entenderlo rápido (<code>docs/INDICE.md</code>).</p>"
          + "<h3>¶Rutas de lectura por perfil</h3>" + T(X["idx_rutas"], "", ["24%", "", "14%"])
          + "<h3>¶Documentos</h3>" + T(X["idx_docs"], "", ["30%", ""])
          + "<h3>¶Diagramas</h3>" + T(X["idx_diagramas"], "", ["40%", ""]) + "<p>Insertados en la sección 4.</p>"
          + "<h3>¶Pruebas y evidencia</h3>" + T(X["idx_pruebas"], "", ["40%", ""])
          + "<h3>¶Pendientes y puntos abiertos</h3>" + vin(X["idx_pendientes"]),
          "todas las audiencias")

# ---------- 18 · Mantenimiento ----------
s18 = sec("mantenimiento", "20", "Mantenimiento y evolución",
          "<p class='intro'>El ecosistema se mantiene con rutinas cortas y verificables: la sanidad por proyecto, la regresión y la suite en vivo por paquete, y un procedimiento explícito para cada cambio externo (BMAD, clientes, integraciones).</p>"
          + "<h3>¶Rutinas</h3>" + layers(D["mant_rutinas"])
          + "<h3>¶Semanal, en cada proyecto activo</h3>" + T(X["semanal"], "", ["6%", "36%", ""])
          + "<h3>¶Actualizar BMAD</h3>" + md(X["mant_bmad_md"])
          + "<h3>¶Después de cambiar el paquete</h3>" + md(X["mant_paquete_md"])
          + "<h3>¶Agregar una integración</h3>" + md(X["checklist_integracion_md"])
          + "<h3>¶Limitaciones conocidas</h3>" + T(X["limitaciones"], "", ["30%", "", "28%"])
          + "<h3>¶Líneas de evolución</h3>" + vin(D["evolucion"]),
          "mantenedor técnico, PMO")

# ---------- 19 · Cómo seguir evolucionando ----------
s19 = sec("evolucionar", "21", "Cómo seguir evolucionando el ecosistema",
          "<p class='intro'>El repositorio público <b><a href='https://github.com/Arturo-Penas-Rial/pm-method' target='_blank' rel='noopener'>https://github.com/Arturo-Penas-Rial/pm-method</a></b> es a la vez el plugin y su marketplace. La forma prevista de seguir desarrollándolo es trabajar con Claude Code sobre un clon del repositorio, con <code>CLAUDE.md</code> como contexto de desarrollo, y publicar cada cambio verificado para que los equipos lo reciban con dos comandos.</p>"
          + "<div class='steps'>"
          + paso(1, "Clonar el repositorio y abrir Claude Code en él", pre("git clone https://github.com/Arturo-Penas-Rial/pm-method.git") + "<p><code>CLAUDE.md</code>, en la raíz, explica qué es el repositorio, la jerarquía PRINCE2 → PMBOK → plantillas → BMAD, el mapa de carpetas, las convenciones de código y el flujo para cada cambio (<code>AGENTS.md</code> lo resume para otros agentes de código). Es contexto de desarrollo, no del plugin: <code>claude plugin validate .</code> emite un aviso esperado por él.</p>")
          + paso(2, "Respetar las reglas del autor", vin(X["cla_reglas"]))
          + paso(3, "Cambiar, validar, probar y medir", "<ol>" + "".join(f"<li>{inl(x)}</li>" for x in X["cla_flujo"]) + "</ol>" + md(X["cla_probar_md"]))
          + paso(4, "Rama y pull request", "<p>Commit con mensaje descriptivo; una rama y un PR por cambio grande (CLAUDE.md). Antes de anunciar una versión, la <code>version</code> de <code>.claude-plugin/plugin.json</code> debe coincidir con <code>compatibilidad.json</code> y <code>esquema.py</code> (<code>VERSION_PAQUETE</code>) —<code>validar_paquete.py</code> lo comprueba— y es la que usa <code>claude plugin update</code> para decidir si hay algo nuevo. Credenciales: nunca en el chat, en commits ni en archivos; <code>gh auth login</code> inicia sesión en el navegador.</p>")
          + paso(5, "Actualizar el plugin en cada puesto", pre("claude plugin marketplace update pm-method        # refresca el catálogo desde GitHub\nclaude plugin update pm-method@pm-method          # instala la versión nueva; requiere reiniciar Claude Code\nclaude plugin list                                # confirmar la versión") + "<p>Después: sanidad completa en cada proyecto activo (los proyectos migran solos al leerse; INS-02 avisa la diferencia de versión) y la verificación de 12 pasos de la sección 11.</p>")
          + "</div>",
          "mantenedor técnico")

# ---------- 22 · Historial de versiones ----------
# Único lugar del informe que describe cambios entre versiones; el resto describe el ecosistema tal como es.
VS = D["versiones"]
grupos24 = "".join(f"<details{' open' if i == 0 else ''}><summary>{e(g['t'])} ({len(g['items'])})</summary>{vin(g['items'])}</details>" for i, g in enumerate(X["chl24_grupos"]))
grupos23 = "".join(f"<details><summary>{e(g['t'])} ({len(g['items'])})</summary>{vin(g['items'])}</details>" for i, g in enumerate(X["chl23_grupos"]))
grupos22 = "".join(f"<details><summary>{e(g['t'])} ({len(g['items'])})</summary>{('<p>' + inl(g['intro']) + '</p>') if g['intro'] else ''}{vin(g['items'])}</details>" for g in X["chl22_grupos"])
grupos21 = "".join(f"<details><summary>{e(g['t'])} ({len(g['items'])})</summary>{vin(g['items'])}</details>" for g in X["chl_grupos"])
s22 = sec("versiones", "22", "Historial de versiones",
          "<p class='intro'>Esta sección es el único lugar del informe que describe cambios entre versiones; el resto describe el ecosistema tal como es en la versión " + e(CIF["version"]) + ". Detalle completo: <code>CHANGELOG.md</code>.</p>"
          + f"<h3>¶{e(CIF['version'])} · {e('/'.join(reversed(X['chl24_fecha'].split('-'))))} — {e(X['chl24_lema'])}</h3><p>{inl(X['chl24_intro'])}</p><p class='src'>{inl(X['chl24_cifras'])}</p>"
          + tabla_html(["Indicador", "2.3.0", CIF["version"], "Fuente"], VS["antes_despues_24"], "", ["22%", "22%", "36%", ""])
          + "<h4>Cambios por área</h4>" + grupos24
          + f"<h3>¶2.3.0 · {e('/'.join(reversed(X['chl23_fecha'].split('-'))))} — {e(X['chl23_lema'])}</h3><p>{inl(X['chl23_intro'])}</p><p class='src'>{inl(X['chl23_cifras'])} Tabla tal como se publicó con la versión 2.3.0.</p>"
          + tabla_html(["Indicador", "2.2.0", "2.3.0", "Fuente"], VS["antes_despues_23"], "", ["22%", "22%", "36%", ""])
          + "<h4>Cambios por área</h4>" + grupos23
          + f"<h3>¶2.2.0 · 17/10/2026 — {e(X['chl22_lema'])}</h3><p>{inl(X['chl22_intro'])}</p><p class='src'>Tabla tal como se publicó con la versión 2.2.0.</p>"
          + tabla_html(["Indicador", "2.1.0", "2.2.0", "Fuente"], VS["antes_despues_22"], "", ["24%", "20%", "36%", ""])
          + "<h4>Cambios por área</h4>" + grupos22
          + f"<h3>¶2.1.0 · 17/10/2026 — {e(X['chl_lema'])}</h3><p>{inl(X['chl_intro'])}</p><p class='src'>Tabla tal como se publicó con la versión 2.1.0.</p>"
          + tabla_html(["Indicador", "2.0.0", "2.1.0", "Fuente"], VS["vigente21"], "", ["30%", "22%", "26%", ""])
          + "<h4>Cambios por área</h4>" + grupos21
          + f"<h3>¶2.0.0 · 14/10/2026</h3><p>{inl(X['chl_v20_md'])}</p>",
          "mantenedor técnico, PMO")

# ---------- Anexos ----------
glos = tabla_html(["Término", "Definición"], [[f"**{g['t']}**", g["d"]] for g in sorted(D["glosario"], key=lambda g: unicodedata.normalize("NFD", g["t"].lower().lstrip("${.[")).encode("ascii", "ignore"))], "", ["24%", ""])
anA = sec("anexo-a", "", f"Anexo A · Glosario ({len(D['glosario'])} términos)", glos)
ext = "".join(f"<h4>{e(f['g'])}</h4><ul>" + "".join(f"<li>{link(u)}</li>" for u in f["u"]) + "</ul>" for f in D["fuentes_externas"])
anB = sec("anexo-b", "", "Anexo B · Fuentes",
          "<h3>B.1 · Documentos del paquete (fuente primaria)</h3>" + tabla_html(["Archivo", "Contenido usado"], [[f"`{a}`", b] for a, b in D["fuentes_internas"]], "", ["30%", ""])
          + "<h3>B.2 · Documentación externa citada</h3>" + ext + f"<p class='src'>{e(D['fuentes_nota'])} Las URL de origen de cada dependencia están en la sección 10.</p>")
skills_cols = "".join(f"<li><code>{e(s)}</code></li>" for s in X["skills_dirs"])
anC = sec("anexo-c", "", "Anexo C · Estructura de carpetas",
          "<div><div><h3>C.1 · Repositorio pm-method</h3>" + pre(X["arbol_paquete"])
          + f"<h4>Las {len(X['skills_dirs'])} carpetas de skills/</h4><ul class='cols'>{skills_cols}</ul>"
          + "<h4>Conocimiento destilado (pm-knowledge/references/)</h4><ul>" + "".join(f"<li><code>{e(r)}</code></li>" for r in X["knowledge_refs"]) + "</ul></div>"
          + "<div><h3>C.2 · Carpeta de un proyecto</h3>" + pre(X["arbol_proyecto"])
          + "<p>Nombres en <code>kebab-case</code>, con prefijo de fecha cuando hay secuencia. Todo artefacto Markdown lleva frontmatter con <code>tipo</code>, <code>proyecto</code>, <code>version</code>, <code>fecha</code>, <code>autor</code>, <code>estado</code>, <code>aprobado_por</code> e <code>idioma</code>. Con BMAD, la carpeta del proyecto va fuera de <code>_bmad/</code>, <code>_bmad-output/</code> y <code>.bmad-core/</code> (por ejemplo, <code>repositorio/gestion/</code>).</p>"
          + "<h3>C.3 · Ciclo de vida (fuente Mermaid de docs/diagramas/ciclo-de-vida.mmd; diagrama en la sección 4)</h3>" + pre(X["ciclo_vida_txt"]) + "</div></div>")

cuerpo = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8p + s8 + s9 + s10 + s11 + s12 + s13 + s14 + s15 + s16 + s17p + s17 + s18 + s19 + s22 + anA + anB + anC
