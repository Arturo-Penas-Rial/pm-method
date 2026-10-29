"""Guía E2E-5 · De la idea al proyecto diseñado: validar supuestos, comparar opciones, elegir el enfoque, adaptar la gestión
y fijar presupuestos y tolerancias (puesta en marcha e iniciación) con scripts reales.

Variante b) principal, sin BMAD: turnos en línea para una red de policlínicas ficticia (todo con skills de pm-method).
Variante a) con BMAD: los supuestos y requisitos salen del fixture BMAD real (portal de socios), leído con pm-bmad-puente.
Bloque C: el mismo proyecto con tres diseños (interno pequeño, regulado, producto digital ágil), cada uno con su estado.json.
Los mapas de Wardley y de recorrido de cada variante terminan en su tablero de mapas (mapas.py tablero):
g5-tablero-mapas.png (y el recorte 16:9 g5-tablero-mapas-169.png) y g5-tablero-mapas-bmad.png.
Lecciones previas desde el índice de la red (lecciones.py, paso 1; accionadas con su control en el paso 6); personas de
usuario y capacidad × persona en las dos variantes (interesados.py personas, pasos 10b y 16b: g5-personas-mapa.png y
g5-personas-mapa-bmad.png); línea de radar del hook al retomar (paso 7) y radar al 2027-02-01 (estado.py radar, paso 14).
Decisiones con contexto (decision.py, pm-direccion-decisiones): matriz de las opciones de negocio con el VAN importado de
inversion.py, expediente y pregunta tipada (paso 4, g5-matriz-opciones.png); hacer o comprar de C2 con los criterios
hacer-o-comprar, el contexto de los mapas en el expediente y la decisión citada en el componente (paso 5b,
g5-hacer-comprar-c2.png); elección registrada en la aprobación del
caso esquemático (paso 6, --decision), revisión del enfoque que reemplaza a D-003 y vigentes --tema (paso 13) y DEC-06
de la aceptación de S-006 con vigentes --ids (paso 14).
"""
from comun import *
import io
import visuales as V

OUT = os.environ.get("GUIAS_SALIDA", os.getcwd())
P = lambda t: print(f"\n######## {t}\n") or LOG.append((f"## {t}", ""))
EJ = "Ejecutiva: Carmen Olivera"
usd = lambda n: V.miles(round(n))
pct = lambda x, d=1: V.miles(100 * x, d)
INV = f"python3 {RAIZ}/skills/pm-caso-de-negocio/scripts/inversion.py"

def limpiar(n=1):
    """Quita de las últimas n entradas del registro las marcas de tiempo de archivos copiados (inventario de BMAD): la
    evidencia sale igual en dos corridas seguidas."""
    for k in range(1, n + 1):
        c, o = LOG[-k]
        LOG[-k] = (c, re.sub(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?\b", "<fecha-hora>", o))

def sanidad(r, corte):
    return run(E(f'sanidad.py --proyecto {G} --rapido --corte {corte}'), r, ok=(0, 1, 2))

def puerta_f(r, tipo, por, fecha, extra="", decision="aprobado"):
    """Como comun.puerta, con la fecha de la junta también en la lista y la confirmación (evidencia determinista)."""
    run(E(f'puertas.py --proyecto {G} verificar {tipo}'), r, ok=(0, 1, 2))
    run(E(f'puertas.py --proyecto {G} lista {tipo} --fecha {fecha}'), r, mostrar=False)
    run(E(f'puertas.py --proyecto {G} confirmar {tipo} --por "{por}" --fecha {fecha}'), r)
    return run(E(f'estado.py --proyecto {G} puerta {tipo} --decision {decision} --por "{por}" --fecha {fecha} {extra}'), r)

def doc(r, clave, rel, texto, estado="en-revision", version=None, origen=""):
    """El texto lo redacta la skill dueña desde su plantilla; aquí, una versión mínima con los datos del escenario."""
    escribir(r, rel, texto)
    v = f" --version {version}" if version else ""
    run(E(f'estado.py --proyecto {G} artefacto {clave} --ruta {rel} --estado {estado}{v}'), r, mostrar=False)
    LOG.pop()
    LOG.append((f"({origen} → gestion/{rel})" if origen else f"(gestion/{rel})", texto.strip()))

def regs(r, registro, **campos):
    """reg() de comun.py para un proyecto distinto del principal."""
    return reg(r, registro, **campos)

def verificar_json(r, tipo):
    """puertas.py verificar --json: la lista `hallazgos` trae severidad, código de control y mensaje."""
    s = subprocess.run(["python3", f"{EST}/puertas.py", "--proyecto", G, "verificar", tipo, "--json"], cwd=r, capture_output=True, text=True)
    return json.loads(s.stdout)

def inversion(r, rel, filas, mostrar=True):
    """Escribe el CSV de flujos por concepto (opcion,concepto,tipo,0…5) y corre inversion.py en texto (evidencia) y en
    --json (cifras para los documentos y los gráficos)."""
    escribir(r, rel, "opcion,concepto,tipo,0,1,2,3,4,5\n" + "".join(",".join([o, c, t] + [str(round(x)) if x else "" for x in fl]) + "\n" for o, c, t, fl in filas))
    LOG.append((f"(pm-caso-de-negocio → gestion/{rel})", open(os.path.join(r, G, rel), encoding="utf-8").read().strip()))
    run(f"{INV} {G}/{rel} --tasa 0.10", r, mostrar=mostrar)
    return json.loads(subprocess.run(f"{INV} {G}/{rel} --tasa 0.10 --json", shell=True, cwd=r, capture_output=True, text=True).stdout)

def csv_filas(r, rel):
    return list(csv.DictReader(open(os.path.join(r, G, rel), encoding="utf-8")))

def personas_json(r, accion, *extra):
    """interesados.py personas candidatos|mapa|priorizacion --json (cifras para el gráfico capacidad × persona)."""
    return json.loads(subprocess.run(["python3", IN, "--proyecto", G, "personas", accion, *extra, "--json"], cwd=r, capture_output=True, text=True).stdout)

def matriz_personas(m, prio, ruta, titulo, subtitulo="", fuente=""):
    """Capacidad × persona (personas mapa --json): prioridad MoSCoW de cada capacidad, el rol de cada persona con letra y
    color (S pide, U usa, B aprovecha), cuántas personas toca cada capacidad y, al pie, lo de cada persona según
    personas priorizacion --json. Paleta, tipografía, tamaño (1600×900) y pie de fuente de visuales.py."""
    import textwrap, matplotlib.lines as ml
    from matplotlib.patches import FancyBboxPatch
    ROL = {"solicitante": "S", "usuario": "U", "beneficiario": "B"}; COL = {"S": V.SERIE[1], "U": V.SERIE[0], "B": V.SERIE[2]}
    MOS = {"must": "Must", "should": "Should", "could": "Could", "wont": "Won't"}
    recortar = lambda x, n: x if len(x) <= n else x[:n - 1].rstrip() + "…"
    pers, caps = m["personas"], m["capacidades"]; pp_ = {x["id"]: x for x in prio["personas"]}
    fig = V._fig(titulo, subtitulo)
    n, k = len(caps), len(pers)
    x_id, x_tit, x_mo, x_n = 0.04, 0.105, 0.43, 0.87
    ancho = min(0.13, 0.39 / max(k, 1)); x_p0 = 0.475 + (0.39 - k * ancho) / 2
    arriba, abajo, hc = 0.735, 0.235, 0.05
    h = min(0.0625, (arriba - hc - abajo) / n)
    linea = lambda y: fig.add_artist(ml.Line2D([0.04, x_n + 0.06], [y, y], transform=fig.transFigure, color=V.EJE, linewidth=0.8))
    for x, t_, ha in ((x_id, "Capacidad", "left"), (x_mo, "MoSCoW", "center"), (x_n + 0.03, "Personas", "center")):
        fig.text(x, arriba - hc / 2, t_, fontsize=12, color=V.TINTA2, fontweight="bold", va="center", ha=ha)
    nl = max(len(textwrap.wrap(p_["nombre"], 20)[:2]) for p_ in pers)
    for j, p_ in enumerate(pers):
        cx = x_p0 + (j + 0.5) * ancho
        fig.text(cx, arriba + 0.012, "\n".join(textwrap.wrap(p_["nombre"], 20)[:2]), fontsize=10.5, color=V.TINTA, va="bottom", ha="center", linespacing=1.15)
        fig.text(cx, arriba + 0.018 + 0.0265 * nl, p_["id"], fontsize=11, color=V.TINTA, fontweight="bold", va="bottom", ha="center")
    linea(arriba - hc)
    for i, c in enumerate(caps):
        y = arriba - hc - h * (i + 0.5); must = c["prioridad"] == "must"
        if i % 2 == 0:
            fig.add_artist(FancyBboxPatch((0.035, y - h / 2), x_n + 0.03, h, boxstyle="square,pad=0", transform=fig.transFigure, facecolor="#f0efec", edgecolor="none", zorder=0))
        fig.text(x_id, y, c["id"], fontsize=11.5, color=V.TINTA, fontweight="bold" if must else "normal", va="center")
        fig.text(x_tit, y, recortar(" ".join(str(c["titulo"] or "").split()), 40), fontsize=11.5, color=V.TINTA, va="center")
        fig.text(x_mo, y, MOS.get(c["prioridad"], "—"), fontsize=11.5, color=V.TINTA if must else V.TINTA2, fontweight="bold" if must else "normal", va="center", ha="center")
        for j, p_ in enumerate(pers):
            roles = [ROL[r] for r in c["personas"].get(p_["id"], [])]
            if not roles: continue
            cx = x_p0 + (j + 0.5) * ancho; w_ = 0.026 + 0.018 * (len(roles) - 1)
            fig.add_artist(FancyBboxPatch((cx - w_ / 2, y - h * 0.34), w_, h * 0.68, boxstyle="round,pad=0,rounding_size=0.006", transform=fig.transFigure,
                                          facecolor=COL[roles[0]], edgecolor="none", zorder=2))
            fig.text(cx, y, "·".join(roles), fontsize=12, color="white", fontweight="bold", va="center", ha="center", zorder=3)
        fig.text(x_n + 0.03, y, str(len(c["personas"])), fontsize=12, color=V.TINTA, va="center", ha="center", fontweight="bold" if len(c["personas"]) == k else "normal")
    yb = arriba - hc - h * n; linea(yb); yp = yb - 0.045
    hay_pr = any(x["por_prioridad"].get(q) for x in prio["personas"] for q in MOS)
    hay_rep = any(x.get("representante") for x in prio["personas"]); hay_ben = any(x.get("beneficios") for x in prio["personas"])
    fig.text(x_id, yp, "Por persona", fontsize=12, color=V.TINTA2, fontweight="bold", va="center")
    for j, p_ in enumerate(pers):
        x = pp_.get(p_["id"]) or {}; pr = x.get("por_prioridad", {})
        partes = [f"{pr[q]} {MOS[q]}" for q in MOS if pr.get(q)] + ([f"{pr['sin']} sin prioridad"] if pr.get("sin") else [])
        rr = x.get("por_rol", {})
        roles = " · ".join(f"{et} {rr[r]}" for r, et in (("solicitante", "pide"), ("usuario", "usa"), ("beneficiario", "aprovecha")) if rr.get(r))
        lin = ([" · ".join(partes)] if hay_pr else [roles]) + ([f"representa {(x.get('representante') or {}).get('id', '—')}"] if hay_rep else []) \
            + ([" · ".join(b["id"] for b in x.get("beneficios", [])) or "—"] if hay_ben else [])
        fig.text(x_p0 + (j + 0.5) * ancho, yp, "\n".join(lin), fontsize=10.5,
                 color=V.TINTA, va="top", ha="center", linespacing=1.3)
    pie = ", ".join((["capacidades por prioridad"] if hay_pr else ["capacidades por rol (el PRD no prioriza)"]) + (["interesado que la representa"] if hay_rep else [])
                    + (["beneficios"] if hay_ben else []))
    fig.text(x_id, yp - 0.04, "S pide · U usa · B aprovecha sin usarla" + (" · Must en negrita" if hay_pr else "") + "\n"
             + "\n".join(textwrap.wrap("Al pie, por persona: " + pie, 60)), fontsize=10.5, color=V.TINTA2, va="top", linespacing=1.3)
    return V._guardar(fig, ruta, fuente)

# ===================================================================================== variante b) sin BMAD
base = tempfile.mkdtemp(prefix="e2e-")
repo = os.path.join(base, "turnos-policlinicas"); os.makedirs(repo); print("REPO", repo)

P("Paso 1 · Mandato y lecciones previas")
run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Turnos en línea · Policlínicas Altamar" --idioma es --ejecutivo "Carmen Olivera" --gestor "Pablo Rinaldi" --fecha 2026-11-02'), repo)
doc(repo, "mandato", "00-direccion/mandato.md", """# Mandato del proyecto · Turnos en línea · Policlínicas Altamar (ficticia)

## 1. Origen
Correo de la gerenta general, Carmen Olivera, del 2026-11-02 a la dirección de la red (6 policlínicas).

## 2. Qué se pide
"Que los pacientes saquen, confirmen y cancelen turnos sin llamar. El call center no da abasto y el ausentismo nos
cuesta caro." Restricción: el canal telefónico y el presencial se mantienen (decisión de la dirección).

## 3. Personas
Autoridad emisora y ejecutiva prospectiva: Carmen Olivera. Gestor propuesto: Pablo Rinaldi.

## 4. Contexto (datos de la red, 2026)
- 240.000 turnos por año; 70 % se agendan por teléfono.
- Ausentismo (el paciente no se presenta ni avisa): 18 %.
- Margen de un turno que se recupera: USD 5 (finanzas). Costo de una llamada atendida: USD 1,20 (finanzas).
- [supuesto] Buena parte de los pacientes sacaría el turno en línea si pudiera.
- [supuesto] Un recordatorio con confirmación baja mucho el ausentismo.
- [supuesto] El proveedor de la agenda clínica permite reservar y cancelar turnos desde otro sistema [por confirmar].

## 5. Anotaciones del gestor
Faltan: presupuesto disponible y fecha deseada [por confirmar con la ejecutiva].
""", origen="pm-mandato-y-brief, templates/mandato.md")
# índice de lecciones de la red, exportado por la PMO con `lecciones.py buscar --exportar` (fuera de gestion/): tres lecciones
# aprobadas que aplican, una aprobada de otro tema y una sin aprobar (no se devuelve)
LECC = f"python3 {RAIZ}/skills/pm-lecciones-aprendidas/scripts/lecciones.py"
IDX = "pmo-altamar/lecciones-indice.csv"
os.makedirs(os.path.join(repo, "pmo-altamar"))
escribir_csv(os.path.join(repo, IDX), ["proyecto", "ref", "id", "fecha", "etapa", "categoria", "etiquetas", "situacion", "efecto", "recomendacion", "prioridad", "estado"], [
    dict(proyecto="App de resultados de laboratorio", ref="app-de-resultados-de-laboratorio:L-004", id="L-004", fecha="2024-11-20", etapa="3", categoria="adopcion",
         etiquetas="pacientes;adopcion;canal-digital", situacion="App de resultados de laboratorio (2024): 11 % de uso en pacientes mayores de 65",
         efecto="la app no redujo las llamadas de ese grupo", recomendacion="mantener un canal asistido y medir la adopción por franja de edad desde el día 1", prioridad="alta", estado="accionada-organizacion"),
    dict(proyecto="Historia clínica electrónica", ref="historia-clinica-electronica:L-007", id="L-007", fecha="2025-06-30", etapa="2", categoria="tecnica",
         etiquetas="agenda-clinica;integracion;proveedor", situacion="Historia clínica (2025): la integración con la agenda clínica se estimó en 4 semanas y llevó 14",
         efecto="el proveedor no tenía una interfaz documentada; atraso de 10 semanas", recomendacion="validar la interfaz del proveedor con una prueba técnica antes de comprometer fechas", prioridad="alta", estado="revisada"),
    dict(proyecto="Historia clínica electrónica", ref="historia-clinica-electronica:L-009", id="L-009", fecha="2025-07-14", etapa="2", categoria="datos",
         etiquetas="agenda-clinica;migracion", situacion="La migración de los turnos históricos a la agenda llevó dos fines de semana",
         efecto="sin efecto en el plan", recomendacion="planificar la migración fuera del horario de atención", prioridad="baja", estado="registrada"),
    dict(proyecto="Piloto de recordatorios de odontología", ref="piloto-de-recordatorios-de-odontologia:L-002", id="L-002", fecha="2025-09-15", etapa="1", categoria="beneficios",
         etiquetas="recordatorios;ausentismo;linea-base", situacion="Piloto de recordatorios por SMS en odontología (2025)",
         efecto="bajó el ausentismo pero nadie midió la línea base y no se pudo justificar la extensión", recomendacion="medir la línea base antes de cualquier piloto", prioridad="alta", estado="accionada-proyecto"),
    dict(proyecto="Mudanza del laboratorio central", ref="mudanza-del-laboratorio-central:L-003", id="L-003", fecha="2025-03-10", etapa="2", categoria="adquisiciones",
         etiquetas="compras;equipamiento", situacion="El equipamiento se adjudicó sin pliego técnico revisado por los usuarios",
         efecto="dos equipos devueltos y un mes de atraso", recomendacion="pliego técnico firmado por el usuario antes de licitar", prioridad="media", estado="revisada")])
LOG.append((f"(índice de lecciones de la red, exportado por la PMO con lecciones.py buscar --exportar → {IDX})", f"5 lecciones de 4 proyectos (una sin aprobar)"))
run(f'{LECC} buscar --indice {IDX} --texto "pacientes turnos agenda recordatorios"', repo)
REFS_L = "app-de-resultados-de-laboratorio:L-004,historia-clinica-electronica:L-007,piloto-de-recordatorios-de-odontologia:L-002"
run(f'{LECC} incorporar --proyecto {G} --indice {IDX} --ids {REFS_L}', repo)
out_l = run(f'{LECC} incorporar --proyecto {G} --indice {IDX} --ids {REFS_L} --confirmar --por "Gestor: Pablo Rinaldi" --fecha 2026-11-02', repo)
L = dict(zip(("L1", "L2", "L3"), re.findall(r"\b(L-\d{3}) ←", out_l)))
run(E(f'registro.py --proyecto {G} listar lecciones'), repo)

P("Paso 2 · Mapa de supuestos: criticidad y certeza (deseabilidad, viabilidad, factibilidad)")
run(f'python3 {RAIZ}/skills/pm-riesgos/scripts/riesgos.py --proyecto {G} candidatos --fuentes artefactos --fecha 2026-11-04', repo)
SUP = [
    ("deseabilidad", "alta", "baja", "Al menos el 40 % de los turnos se sacará en línea desde el segundo año (20 % el primero)", "Inés Ferrer", "sostiene B-02 (llamadas evitadas) · origen: mandato.md §4 y L-001"),
    ("viabilidad", "alta", "baja", "Un recordatorio con confirmación baja el ausentismo del 18 % al 10 %", "Inés Ferrer", "sostiene B-01 (turnos recuperados) · origen: mandato.md §4 y L-003"),
    ("factibilidad", "alta", "baja", "La agenda clínica del proveedor permite reservar y cancelar turnos en tiempo real desde otro sistema", "Tomás Aguirre", "sin esto no hay turnos en línea · origen: mandato.md §4 y L-002"),
    ("viabilidad", "media", "media", "La dirección médica libera las agendas con 60 días de anticipación", "Inés Ferrer", "condiciona la oferta de turnos en línea"),
    ("deseabilidad", "baja", "alta", "Se mantienen el canal telefónico y el presencial", "Carmen Olivera", "restricción de la dirección · origen: mandato.md §2"),
    ("factibilidad", "alta", "media", "La normativa de protección de datos permite enviar recordatorios por mensajería con el consentimiento dado al pedir el turno", "Carmen Olivera", "si no, el recordatorio pierde alcance"),
    ("viabilidad", "baja", "media", "El costo por mensaje se mantiene en USD 0,02", "Tomás Aguirre", "pesa poco en el caso"),
]
S = []
for cat, crit, cert, txt, resp, notas in SUP:
    S.append(reg(repo, "supuestos", fecha="2026-11-04", autor="Pablo Rinaldi", supuesto_o_restriccion=txt, tipo="restriccion" if "mantienen" in txt else "supuesto",
                 categoria=cat, criticidad=crit, certeza=cert, validado="pendiente", responsable=resp, notas=notas))
run(E(f'registro.py --proyecto {G} listar supuestos'), repo)
sanidad(repo, "2026-11-04")
filas_sup = csv_filas(repo, "03-control/registros/supuestos.csv")
crit_baja = [f["id"] for f in filas_sup if f["criticidad"] == "alta" and f["certeza"] == "baja"]
V.mapa_supuestos(filas_sup, os.path.join(OUT, "g5-mapa-supuestos.png"),
                 titulo=f"{len(crit_baja)} supuestos críticos sin evidencia: ahí se invierte primero",
                 subtitulo=f"Turnos en línea · {len(filas_sup)} supuestos al 2026-11-04 · {', '.join(crit_baja)} sostienen los dos beneficios y la factibilidad",
                 fuente="supuestos.csv (registro.py) · corte 2026-11-04")

P("Paso 3 · Experimentos baratos con criterio decidido de antemano, resultados y controles SUP")
EXP = {S[0]: ("prueba de humo: botón «sacá tu turno en línea» en el sitio actual con registro de interés, 3 semanas", "≥ 1.000 registros de interés en 3 semanas", "2026-11-27", "Inés Ferrer"),
       S[1]: ("piloto de recordatorio con confirmación por mensajería en la Policlínica Centro, 4 semanas (2.000 turnos)", "ausentismo del piloto ≤ 12 %", "2026-12-04", "Inés Ferrer"),
       S[2]: ("prueba técnica de 5 días contra el entorno de pruebas del proveedor: reservar y cancelar 50 turnos", "50 de 50 sin intervención manual y respuesta < 2 s", "2026-12-04", "Tomás Aguirre"),
       S[5]: ("consulta formal a la asesoría legal sobre el consentimiento para recordatorios", "dictamen favorable o condiciones de consentimiento por escrito", "2027-01-29", "Carmen Olivera")}
for sid, (exp, cri, fl, resp) in EXP.items():
    act(repo, "supuestos", sid, experimento=exp, criterio=cri, fecha_limite=fl, responsable=resp)
HIP = f"""# Hipótesis y experimentos · Turnos en línea (v0.1)

## 1. Idea y decisión
Idea: que los pacientes saquen, confirmen y cancelen turnos sin llamar. Decisión esperada: autorizar la iniciación
(2026-12-11) y elegir una opción.

## 2. Supuestos que sostienen la idea (cuadrante crítico + certeza baja: {', '.join(crit_baja)})
| Id | Supuesto | Tipo | Criticidad | Certeza |
|---|---|---|---|---|
""" + "\n".join(f"| {S[k]} | {t[3]} | {t[0]} | {t[1]} | {t[2]} |" for k, t in enumerate(SUP)) + f"""

## 3. Experimentos
| Supuesto | Experimento | Criterio para seguir | Fecha límite | Responsable |
|---|---|---|---|---|
""" + "\n".join(f"| {sid} | {e[0]} | {e[1]} | {e[2]} | {e[3]} |" for sid, e in EXP.items()) + "\n"
doc(repo, "hipotesis-y-experimentos", "01-inicio/hipotesis-y-experimentos.md", HIP, version="0.1", origen="pm-mandato-y-brief, templates/hipotesis-y-experimentos.md")
sanidad(repo, "2026-11-05")
# resultados al 2026-12-07: S-001 validado, S-002 invalidado (el piloto bajó el ausentismo, pero no lo suficiente), S-003 sin resultado
act(repo, "supuestos", S[0], validado="si", estado="validado", certeza="alta", fecha_validacion="2026-11-27", evidencia="1.840 registros de interés en 3 semanas (criterio ≥ 1.000)")
act(repo, "supuestos", S[1], validado="no", estado="invalidado", certeza="alta", fecha_validacion="2026-12-04", evidencia="piloto Policlínica Centro: ausentismo del 18 % al 13,5 % en 2.000 turnos (criterio ≤ 12 %)")
sanidad(repo, "2026-12-07")
regs(repo, "decisiones", fecha="2026-12-07", decision=f"{S[1]} invalidado: el business case usa un ausentismo de 13,5 % (resultado del piloto) en lugar de 10 %; la idea sigue con el beneficio B-01 ajustado",
     decidido_por=EJ, nivel="ejecutivo", artefactos_afectados="00-direccion/business-case-esquematico.md; 01-inicio/hipotesis-y-experimentos.md")
regs(repo, "decisiones", fecha="2026-12-07", decision=f"Replanificar la prueba técnica de {S[2]} al 2027-01-14: el proveedor entrega las credenciales del entorno de pruebas el 2027-01-07",
     decidido_por=EJ, nivel="ejecutivo", revisar_en="2027-01-14")
act(repo, "supuestos", S[2], fecha_limite="2027-01-14", notas="sin esto no hay turnos en línea · origen: mandato.md §4 y L-002 · replanificado el 2026-12-07 (credenciales del proveedor el 2027-01-07)")
sanidad(repo, "2026-12-07")
escribir(repo, "01-inicio/hipotesis-y-experimentos.md", HIP.replace("(v0.1)", "(v0.2)") + f"""
## 4. Resultados y decisión (al 2026-12-07)
| Supuesto | Resultado | Evidencia | Efecto en el business case | Decisión |
|---|---|---|---|---|
| {S[0]} | sí | 1.840 registros de interés en 3 semanas (criterio ≥ 1.000) | B-02 se mantiene | seguir |
| {S[1]} | no (parcial) | piloto: ausentismo 18 % → 13,5 % (criterio ≤ 12 %) | B-01 baja de 8 a 4,5 puntos de ausentismo | ajustar |
| {S[2]} | pendiente | el proveedor no entregó credenciales | sin cambio; replanificado al 2027-01-14 | replanificar |
| {S[5]} | pendiente | dictamen previsto para el 2027-01-29 | — | seguir |

Recomendación a la junta: seguir con la idea con los beneficios ajustados; no comprometer fechas de turnos en línea
hasta validar {S[2]}.
""")
run(E(f'estado.py --proyecto {G} artefacto hipotesis-y-experimentos --ruta 01-inicio/hipotesis-y-experimentos.md --estado en-revision --version 0.2'), repo, mostrar=False)
run(E(f'registro.py --proyecto {G} listar supuestos'), repo)

P("Paso 4 · Opciones de negocio 0/1/2 con VAN, TIR, repago y sensibilidad (antes y después de los experimentos)")
TURNOS, AUS0, MARGEN, COSTO_LLAMADA = 240000, 0.18, 5, 1.20
ADOP = [0.20, 0.40, 0.40, 0.40, 0.40]
b01 = lambda aus: TURNOS * (AUS0 - aus) * MARGEN
b02 = lambda a: TURNOS * a * COSTO_LLAMADA
OPC = {0: "0 · No hacer nada distinto", 1: "1 · Mínimo: recordatorios", 2: "2 · Completo: turnos en línea"}
def flujos(aus, inv1=30000, inv2=180000):
    """Filas del CSV de inversion.py: un concepto por fila, flujos de los años 0 a 5 con su signo."""
    return [(OPC[0], "Sin cambios", "costo", [0] * 6),
            (OPC[1], "Inversión", "inversion", [-inv1] + [0] * 5), (OPC[1], "Turnos recuperados (B-01)", "beneficio", [0] + [b01(aus)] * 5),
            (OPC[1], "Operación", "costo", [0] + [-18000] * 5),
            (OPC[2], "Inversión", "inversion", [-inv2] + [0] * 5), (OPC[2], "Turnos recuperados (B-01)", "beneficio", [0] + [b01(aus)] * 5),
            (OPC[2], "Llamadas evitadas (B-02)", "beneficio", [0] + [b02(a) for a in ADOP]), (OPC[2], "Operación", "costo", [0] + [-36000] * 5)]
perdido = TURNOS * AUS0
LOG.append(("(pm-caso-de-negocio: datos de las opciones, del mandato y de finanzas)",
            f"""Base (opción 0): ausentismo 18 % de {usd(TURNOS)} turnos = {usd(perdido)} turnos perdidos por año = USD {usd(perdido * MARGEN)} de margen no realizado
B-01 turnos recuperados = 240.000 × (0,18 − ausentismo) × USD 5 · B-02 llamadas evitadas = 240.000 × adopción × USD 1,20 (adopción 20 % el año 1, 40 % después)
Opción 1: inversión 30.000, operación 18.000/año · Opción 2: inversión 180.000 (orden de magnitud −25/+75 %), operación 36.000/año · tasa 10 % (finanzas) · 5 años
Con los supuestos iniciales: ausentismo 10 % (S-002 sin validar) · después de los experimentos: 13,5 % (piloto de {S[1]})"""))
ja = inversion(repo, "00-direccion/inversion/flujos-supuestos-iniciales.csv", flujos(0.10))
jd = inversion(repo, "00-direccion/inversion/flujos-opciones.csv", flujos(0.135))
VA = {o: ja["opciones"][OPC[o]] for o in OPC}; VD = {o: jd["opciones"][OPC[o]] for o in OPC}
s2 = {c["concepto"]: c for c in VD[2]["sensibilidad"]}
eq_b02 = s2["Llamadas evitadas (B-02)"]["equilibrio"]; adop_eq = eq_b02 * ADOP[-1]
peso_b02 = s2["Llamadas evitadas (B-02)"]["van_concepto"] / (s2["Llamadas evitadas (B-02)"]["van_concepto"] + s2["Turnos recuperados (B-01)"]["van_concepto"])
baja = VA[2]["van"] - VD[2]["van"]
LOG.append(("(lectura de pm-caso-de-negocio, de inversion.py --json)",
            f"""El supuesto de S-002 (10 %) inflaba el VAN de cada opción en USD {usd(baja)}: opción 2 de {usd(VA[2]['van'])} a {usd(VD[2]['van'])}; opción 1 de {usd(VA[1]['van'])} a {usd(VD[1]['van'])}.
B-02 aporta el {pct(peso_b02, 0)} % del valor actual de los beneficios de la opción 2 (más del 50 %: la sensibilidad es obligatoria).
Punto de equilibrio de B-02: {pct(eq_b02)} % de lo estimado = adopción estable de {pct(adop_eq)} % (VAN = 0).
VAN incremental de la opción 2 sobre la 1: USD {usd(VD[2]['van'] - VD[1]['van'])} por USD {usd(180000 - 30000)} más de inversión."""))
BCE = f"""# Business case esquemático · Turnos en línea (v0.1)

## 2. Razones
Ausentismo del 18 %: {usd(perdido)} turnos perdidos por año (USD {usd(perdido * MARGEN)} de margen). El call center atiende el 70 % de los turnos.

## 4. Opciones de negocio (después de los experimentos; VAN a 5 años, r = 10 %; inversion.py con 00-direccion/inversion/flujos-opciones.csv)
| Opción | Inversión | Beneficio neto año 2 | VAN | TIR | Repago |
|---|---|---|---|---|---|
| {OPC[0]} | 0 | 0 | 0 (base) | — | — |
| {OPC[1]} | 30.000 | {usd(VD[1]['flujos'][2])} | {usd(VD[1]['van'])} | {pct(VD[1]['tir'])} % | {V.miles(VD[1]['repago'], 2)} años |
| {OPC[2]} | 180.000 | {usd(VD[2]['flujos'][2])} | {usd(VD[2]['van'])} | {pct(VD[2]['tir'])} % | {V.miles(VD[2]['repago'], 2)} años |

Recomendación: opción 2 en dos releases. El primero entrega el valor de la opción 1 (recordatorios); el segundo, turnos en línea, solo si {S[2]} está validado.
Sensibilidad: B-02 aporta el {pct(peso_b02, 0)} % del valor de los beneficios; el VAN de la opción 2 llega a 0 con una adopción estable de {pct(adop_eq)} % ({pct(eq_b02)} % de lo estimado).

## 5. Beneficios
- B-01 turnos recuperados (ausentismo 18 % → 13,5 %)
- B-02 llamadas evitadas (adopción 40 %)
- DB-01 des-beneficio: dos puestos del call center se reasignan a recepción
"""
doc(repo, "business-case-esquematico", "00-direccion/business-case-esquematico.md", BCE, version="0.1", origen="pm-caso-de-negocio, modo esquemático")
# decisión entre las opciones (pm-direccion-decisiones, decision.py): el VAN entra sin recalcular desde el --json de
# inversion.py; beneficios fuera del VAN, riesgo y ajuste los puntúa el modelo con su fuente y la ejecutiva confirma los
# pesos; la matriz recomienda, mide cuánto depende de los pesos y la pregunta tipada valida la respuesta del modelo
DEC = f"python3 {RAIZ}/skills/pm-direccion-decisiones/scripts/decision.py --proyecto {G}"
HOJA = "opciones-negocio"; RH = f"03-control/decisiones/{HOJA}"
run(f"{INV} {G}/00-direccion/inversion/flujos-opciones.csv --tasa 0.10 --json > {G}/00-direccion/inversion/opciones.json", repo)
run(f'{DEC} matriz {HOJA} --proponer --tipo negocio --ids {S[1]},{S[2]},B-01,B-02 --pregunta "¿Qué opción de negocio lleva el business case esquemático a la junta?" --importar {G}/00-direccion/inversion/opciones.json', repo)
crit_h = open(os.path.join(repo, G, RH, "criterios.csv"), encoding="utf-8").read().replace("[por confirmar]", f"{EJ} (2026-12-08)")
escribir(repo, f"{RH}/criterios.csv", crit_h)
escribir(repo, f"{RH}/opciones.csv", f"""opcion,descripcion,ref,van,van_fuente,beneficios,beneficios_fuente,riesgo,riesgo_fuente,ajuste_estrategico,ajuste_estrategico_fuente,notas
O0,No hacer nada distinto,{OPC[0]},,,1,mandato.md: el call center sigue sin dar abasto,1,sin inversión ni cambio,1,mandato.md: no responde al pedido,base de comparación
O1,Mínimo: recordatorios con confirmación,{OPC[1]},,,3,B-01: piloto de {S[1]},2,{S[5]}: normativa de los mensajes,3,mandato.md: confirmar y cancelar sin llamar,
O2,Completo: turnos en línea con recordatorios,{OPC[2]},,,4,B-01; B-02; {S[0]} validado,4,{S[2]} sin validar; L-002; inversión −25/+75 %,5,mandato.md: sacar; confirmar y cancelar sin llamar,
""")
LOG.append((f"(pm-direccion-decisiones: el modelo completa la hoja con la fuente de cada puntaje; la ejecutiva confirma los pesos → gestion/{RH}/)",
            "criterios.csv: " + " · ".join(f"{f['criterio']} {f['peso']} ({f['sentido']}, {f['escala']}{', importado de ' + f['importar'] if f['importar'] else ''})" for f in csv.DictReader(io.StringIO(crit_h)))
            + f" · fuente de los pesos: {EJ} (2026-12-08)\nopciones.csv:\n" + "\n".join(
                f"{f['opcion']} {f['descripcion']} · beneficios {f['beneficios']} ({f['beneficios_fuente']}) · riesgo {f['riesgo']} ({f['riesgo_fuente']}) · ajuste {f['ajuste_estrategico']} ({f['ajuste_estrategico_fuente']})"
                for f in csv_filas(repo, f"{RH}/opciones.csv"))))
run(f"{DEC} matriz {HOJA} --markdown", repo)
MZ = json.loads(subprocess.run(f"{DEC} matriz {HOJA} --json", shell=True, cwd=repo, capture_output=True, text=True).stdout)
run(f"{DEC} expediente --hoja {HOJA} --corte 2026-12-08 --max-items 4", repo, corte=200)
escribir(repo, f"{RH}/respuesta-libre.json", '{"respuesta": "opción 2 en dos releases", "evidencia": [], "confianza": "alta", "razon": "es la de mayor VAN"}\n')
escribir(repo, f"{RH}/respuesta.json", json.dumps({"respuesta": "O2", "evidencia": ["opciones.json", S[1], S[2], "D-001"], "confianza": "media", "faltan": [],
                                                    "razon": f"Mayor VAN con el ausentismo del piloto ({S[1]}); su riesgo depende de {S[2]}: el segundo release espera la prueba técnica"}, ensure_ascii=False) + "\n")
run(f"{DEC} pregunta {HOJA} --validar {G}/{RH}/respuesta-libre.json", repo, ok=(1,))
run(f"{DEC} pregunta {HOJA} --validar {G}/{RH}/respuesta.json", repo)
pz = {o["opcion"]: o for o in MZ["opciones"]}; sens_r = next(s for s in MZ["sensibilidad"] if s["criterio"] == "riesgo")["sube"]
MZ_TXT = f"""Matriz multicriterio ({RH}/matriz.md; VAN 40, beneficios fuera del VAN 20, riesgo 20, ajuste 20): opción 2 {V.miles(pz['O2']['puntaje'], 1)}, opción 1 {V.miles(pz['O1']['puntaje'], 1)}, opción 0 {V.miles(pz['O0']['puntaje'], 1)}.
Si el peso del riesgo sube de 20 a {V.miles(sens_r['peso'], 1)}, pasa la opción 1: la ventaja de la 2 depende del riesgo de {S[2]}, por eso el segundo release espera la prueba técnica.
"""
BCE = BCE.replace("estimado).\n\n## 5.", "estimado).\n" + MZ_TXT + "\n## 5.")
escribir(repo, "00-direccion/business-case-esquematico.md", BCE)
LOG.append(("(pm-caso-de-negocio agrega la matriz a §4 de gestion/00-direccion/business-case-esquematico.md)", MZ_TXT.strip()))
V.barras_comparadas(["Opción 2 · completo", "Opción 1 · mínimo", "Opción 0 · no hacer nada"], [[VA[o]["van"] for o in (2, 1, 0)], [VD[o]["van"] for o in (2, 1, 0)]],
                    os.path.join(OUT, "g5-van-opciones.png"),
                    "El piloto bajó el VAN de las dos opciones; la 2 sigue siendo la mejor",
                    subtitulo=f"VAN a 5 años (r = 10 %): opción 2 de {usd(VA[2]['van'])} a {usd(VD[2]['van'])}; opción 1 de {usd(VA[1]['van'])} a {usd(VD[1]['van'])} · ausentismo 13,5 % en vez de 10 %",
                    fuente="inversion.py (pm-caso-de-negocio) con flujos-supuestos-iniciales.csv y flujos-opciones.csv", unidad="",
                    nombres=["Con supuestos iniciales", "Después de los experimentos"])

def matriz_grafico(mz, ruta, titulo, subtitulo="", fuente="", nombres_c=None, nombres_o=None, crit_sens="riesgo", etiqueta_sens=None):
    """Matriz de decisión (decision.py matriz --json): a la izquierda, el puntaje de cada opción como suma de los aportes
    de cada criterio (peso normalizado × valor normalizado), en el orden de la hoja; a la derecha, la sensibilidad del
    peso de un criterio (los demás conservan sus proporciones, como en decision.py): puntaje de cada opción de 0 a 100 y
    el peso con el que cambia la primera. Paleta, tamaño y pie de visuales.py."""
    import matplotlib.ticker as mt
    cr = mz["criterios"]; ops = mz["opciones"]; rec = mz["recomendada"]
    nombres_c = nombres_c or {}; nombres_o = nombres_o or {}
    fig = V._fig(titulo, subtitulo)
    ax = fig.add_axes([0.20, 0.17, 0.30, 0.58]); V._ejes(ax, grilla_x=True, grilla_y=False)
    ys = list(range(len(ops)))[::-1]
    for y, o in zip(ys, ops):
        x0 = 0
        for k, c in enumerate(cr):
            v = c["peso_norm"] * o["normalizados"][c["criterio"]]
            if v > 0:
                ax.barh(y, v, left=x0, height=0.56, color=V.SERIE[k], edgecolor=V.SUP, linewidth=2)
            x0 += v
        ax.text(x0 + 1.5, y, V.miles(o["puntaje"], 1) + ("  ★ recomendada" if o["opcion"] == rec else ""), va="center", fontsize=12,
                color=V.TINTA, fontweight="bold" if o["opcion"] == rec else "normal")
    ax.set_yticks(ys); ax.set_yticklabels([nombres_o.get(o["opcion"], o["opcion"]) for o in ops], fontsize=12, color=V.TINTA)
    ax.set_xlim(0, 100); ax.xaxis.set_major_locator(mt.MultipleLocator(20))
    ax.set_xlabel("Puntaje (0–100): aporte de cada criterio", fontsize=12)
    from matplotlib.patches import Patch
    h = [Patch(facecolor=V.SERIE[k]) for k in range(len(cr))]
    fig.legend(h, [f"{nombres_c.get(c['criterio'], c['criterio'])} ({V.miles(c['peso_norm'], 0)})" for c in cr], loc="lower left", bbox_to_anchor=(0.035, 0.785), frameon=False, fontsize=11.5, ncol=len(cr), handlelength=1.2, columnspacing=1.4)
    # sensibilidad: puntaje(w) = w·n_c + (100 − w)·Σ_{j≠c} (p_j/Σp_{≠c})·n_j
    c0 = next(c for c in cr if c["criterio"] == crit_sens); resto = [c for c in cr if c is not c0]; sr = sum(c["peso_norm"] for c in resto)
    lin = lambda o, w: w * o["normalizados"][crit_sens] + (100 - w) * sum(c["peso_norm"] / sr * o["normalizados"][c["criterio"]] for c in resto)
    ax2 = fig.add_axes([0.63, 0.17, 0.26, 0.58]); V._ejes(ax2, grilla_x=False, grilla_y=True)
    s = next(x for x in mz["sensibilidad"] if x["criterio"] == crit_sens); cambio = s.get("sube") or s.get("baja")
    if cambio:
        ax2.axvspan(cambio["peso"], 100 if s.get("sube") else 0, color="#f0efec", zorder=0)
    estilos = {rec: ("-", V.TINTA, 2.4)}
    otros = [o["opcion"] for o in ops if o["opcion"] != rec]
    for k, oid in enumerate(otros): estilos[oid] = (("--", ":")[k % 2], (V.TINTA2, V.MUDA)[k % 2], 2.0)
    for o in ops:
        ls, col, lw = estilos[o["opcion"]]
        ax2.plot([0, 100], [lin(o, 0), lin(o, 100)], ls, color=col, linewidth=lw)
        yf = lin(o, 100)
        ax2.text(102, yf, nombres_o.get(o["opcion"], o["opcion"]).split(" · ")[0] + (" ★" if o["opcion"] == rec else ""), va="center", fontsize=11.5, color=V.TINTA)
    ax2.axvline(c0["peso_norm"], color=V.EJE, linewidth=1.2)
    ax2.text(c0["peso_norm"] + 1, 97, f"hoy {V.miles(c0['peso_norm'], 0)}", fontsize=11, color=V.TINTA2, va="top")
    if cambio:
        ax2.axvline(cambio["peso"], color=V.TINTA2, linewidth=1.2, linestyle="--")
        ax2.text(cambio["peso"] + 1, 89, f"{V.miles(cambio['peso'], 1)}: pasa\n{nombres_o.get(cambio['opcion'], cambio['opcion']).split(' · ')[0]}", fontsize=11, color=V.TINTA, va="top")
    ax2.set_xlim(0, 100); ax2.set_ylim(0, 100); ax2.xaxis.set_major_locator(mt.MultipleLocator(20)); ax2.yaxis.set_major_locator(mt.MultipleLocator(20))
    etq_ = etiqueta_sens or crit_sens
    ax2.set_xlabel(f"Peso del criterio {etq_} (0–100)", fontsize=12); ax2.set_ylabel("Puntaje", fontsize=12)
    ax2.set_title(f"Sensibilidad al peso de la {etq_}" if etiqueta_sens else f"Sensibilidad al peso del {crit_sens}", fontsize=12.5, color=V.TINTA, loc="left", pad=8)
    ax.set_title("Puntaje por opción (orden de la hoja)", fontsize=12.5, color=V.TINTA, loc="left", pad=8)
    return V._guardar(fig, ruta, fuente)

NC = {"van": "VAN", "beneficios": "Beneficios fuera del VAN", "riesgo": "Riesgo (menor es mejor)", "ajuste_estrategico": "Ajuste al mandato"}
NO = {"O0": "Opción 0 · no hacer nada", "O1": "Opción 1 · mínimo", "O2": "Opción 2 · completo"}
matriz_grafico(MZ, os.path.join(OUT, "g5-matriz-opciones.png"),
               f"La opción 2 gana con {V.miles(pz['O2']['puntaje'], 1)}; la 1 solo pasa si el riesgo pesa {V.miles(sens_r['peso'], 1)} o más",
               subtitulo=f"Matriz {HOJA}: VAN de inversion.py sin recalcular · beneficios, riesgo y ajuste de 1 a 5 con fuente · pesos de la ejecutiva",
               fuente=f"decision.py matriz {HOJA} --json (pm-direccion-decisiones) · inversion.py con flujos-opciones.csv",
               nombres_c=NC, nombres_o=NO)

P("Paso 5 · Enfoque de entrega: nueve criterios por entregable (1 = predictivo, 3 = adaptativo)")
CRIT = ["Certeza de requisitos", "Estabilidad del alcance", "Costo del cambio en el entregable", "Regulación / seguridad",
        "Valor de la retroalimentación frecuente", "Disponibilidad de interesados", "Cultura organizativa", "Tamaño del equipo",
        "Presión por entrega temprana de valor"]
PUNT = {"Recordatorios y confirmación": [1, 1, 2, 2, 2, 2, 2, 3, 3],
        "Turnos en línea (portal y app)": [3, 3, 3, 2, 3, 2, 2, 3, 2],
        "Integración con la agenda clínica": [1, 1, 1, 2, 1, 1, 2, 2, 1]}
lectura = lambda s: "predictivo" if s <= 13 else ("híbrido" if s <= 21 else "adaptativo")
LOG.append(("(pm-mandato-y-brief, references/guia.md §3: tabla de nueve criterios de pm-knowledge/references/pmbok8-estandar-principios-ciclos.md §4.4.4; suma ≤ 13 predictivo, 14–21 híbrido, ≥ 22 adaptativo)",
            f"{'criterio':42s} " + " ".join(f"{k[:22]:>23s}" for k in PUNT) + "\n" +
            "\n".join(f"{c:42s} " + " ".join(f"{PUNT[k][i]:>23d}" for k in PUNT) for i, c in enumerate(CRIT)) + "\n" +
            f"{'suma · lectura':42s} " + " ".join(f"{str(sum(v)) + ' · ' + lectura(sum(v)):>23s}" for v in PUNT.values()) +
            "\nEntregables con lecturas distintas → proyecto híbrido por construcción (cada entregable con su vía); se revisa en cada puerta de etapa."))
out_set = run(E(f'estado.py --proyecto {G} set enfoque_entrega=hibrido --por "{EJ}" --nivel ejecutivo --fecha 2026-12-09'), repo)
D_ENF = re.search(r"D-\d{3}", out_set).group(0)
act(repo, "decisiones", D_ENF, opciones_consideradas="predictivo; ágil; híbrido (nueve criterios: integración con la agenda 12, recordatorios 18, turnos en línea 23)",
    revisar_en="cada puerta de etapa", notas="estado.py set · etapas PRINCE2 con sprints de 14 días dentro")
run(E(f'registro.py --proyecto {G} listar decisiones'), repo)
orden = sorted(PUNT, key=lambda k: -sum(PUNT[k]))
CORTO = {"Recordatorios y confirmación": "Recordatorios", "Turnos en línea (portal y app)": "Portal de turnos", "Integración con la agenda clínica": "Integración agenda"}
V.barras_comparadas([f"{CORTO[k]} · {lectura(sum(PUNT[k]))}" for k in orden], [[sum(PUNT[k]) for k in orden]], os.path.join(OUT, "g5-enfoque-entrega.png"),
                    "Cada entregable pide otra vía: el proyecto es híbrido por construcción",
                    subtitulo="Suma de 9 criterios, cada uno de 1 (predictivo) a 3 (adaptativo): ≤ 13 predictivo · 14–21 híbrido · ≥ 22 adaptativo",
                    fuente="puntuación del paso 5 · criterios de pmbok8-estandar-principios-ciclos.md §4.4.4", nombres=["Suma de los 9 criterios (mínimo 9, máximo 27)"])

P("Paso 5b · Mapa de valor de los entregables y recorrido del paciente (pm-mapas-estrategicos)")
MAPAS = f"python3 {RAIZ}/skills/pm-mapas-estrategicos/scripts/mapas.py"
RMAP = lambda r_, nombre: os.path.join(r_, G, "02-planificacion", "mapas", nombre)

def completar(r_, nombre, cambios, origen, resumen):
    """El modelo propone posiciones, emociones y evidencia; la persona confirma. Aquí se aplica la propuesta confirmada al JSON."""
    d_ = json.load(open(RMAP(r_, nombre), encoding="utf-8")); cambios(d_)
    open(RMAP(r_, nombre), "w", encoding="utf-8").write(json.dumps(d_, ensure_ascii=False, indent=2) + "\n")
    LOG.append((f"({origen} → gestion/02-planificacion/mapas/{nombre})", resumen(d_)))
    return d_

def png_mapa(r_, tipo, slug, destino):
    """PNG para la guía: mmdc para Wardley; captura del HTML para el recorrido (no entra en la evidencia)."""
    if tipo == "recorrido":
        n_ = sum(len(et["pasos"]) for et in json.load(open(RMAP(r_, f"recorrido-{slug}.json"), encoding="utf-8"))["etapas"])
        return captura_html(os.path.join(r_, G, "02-planificacion", "visuales", f"recorrido-{slug}.html"), destino, ancho=max(1280, 140 + 170 * n_ + 80))
    # Chromium (mmdc) no arranca si la ruta de su socket supera ~107 caracteres: con un TMPDIR largo se usa una carpeta corta
    # propia, que se borra al terminar.
    corto = tempfile.mkdtemp(prefix="g5-mmdc-", dir="/tmp" if len(tempfile.gettempdir()) > 40 else None)
    try:
        subprocess.run(["python3", f"{RAIZ}/skills/pm-mapas-estrategicos/scripts/mapas.py", "--proyecto", G, tipo, "render", slug, "--png", "auto"],
                       cwd=r_, capture_output=True, text=True, env={**os.environ, "TMPDIR": corto})
    finally:
        shutil.rmtree(corto, ignore_errors=True)
    png_ = os.path.join(r_, G, "02-planificacion", "visuales", f"{tipo}-{slug}.png")
    if os.path.exists(png_): shutil.copy(png_, destino); os.remove(png_)

def fila_w(c):
    return (f"{c['id']} {c['nombre']} · {c['etapa']} ({V.miles(c['evolucion'], 2)}) · visibilidad {V.miles(c['visibilidad'], 2)} · "
            f"{c['decision'] or 'sin decisión'}{' · inercia' if c.get('inercia') else ''} · {c['evidencia']}" + (f" · refs {', '.join(c['refs'])}" if c["refs"] else ""))

def fila_r(et, p_):
    return (f"{et['nombre']} · {p_['id']} {p_['accion']} · {format(p_['emocion'], '+d') if p_['emocion'] else '0'} ({p_['fuente_emocion'] or 'sin fuente'})" + (f" · dolor: {p_['dolor']}" if p_.get("dolor") else "")
            + (f" → {p_['oportunidad']}" if p_.get("oportunidad") else "") + (f" · refs {', '.join(p_['refs'])}" if p_.get("refs") else ""))

run(f'{MAPAS} --proyecto {G} wardley semilla --slug entregables --titulo "Turnos en línea · qué construir y qué comprar" '
    f'--pregunta "¿Qué parte del servicio construimos, cuál compramos y con qué enfoque se entrega cada una?" --anclas "Paciente" '
    f'--componentes "Turnos en línea (portal y app); Recordatorios y confirmación; Mensajería SMS y correo; Adaptador de la agenda clínica; Agenda clínica del proveedor; Hosting" --fecha 2026-12-09', repo)
POS_W = {  # id: (visibilidad, evolución, etapa, decisión, inercia, evidencia, refs)
    "C1": (0.80, 0.35, "a-medida", "construir", False, f"diferencia a la red; {S[0]} validado (1.840 registros de interés); 23 puntos en los nueve criterios", [S[0]]),
    "C2": (0.70, 0.62, "producto", "comprar", False, f"hay plataformas de recordatorio en el mercado; el piloto de {S[1]} usó una existente ({L['L3']} midió sin línea base)", [S[1], L["L3"]]),
    "C3": (0.45, 0.88, "commodity", "tercerizar", False, f"servicio por mensaje con varios proveedores; USD 0,02 por mensaje ({S[6]})", [S[6]]),
    "C4": (0.50, 0.30, "a-medida", "construir", False, f"no hay conector del proveedor: se escribe a medida; {L['L2']}: 4 semanas estimadas, 14 reales", [S[2], L["L2"]]),
    "C5": (0.30, 0.60, "producto", "", True, f"sistema comprado en uso en las 6 policlínicas; reemplazarlo está fuera de alcance; el proveedor controla la interfaz ({S[2]})", [S[2]]),
    "C6": (0.12, 0.90, "commodity", "comprar", False, "servicio estándar de nube ya contratado por TI (Tomás Aguirre)", [])}
def prop_w(d_):
    for c in d_["componentes"]:
        v, e_, et, dec, ine, ev, rf = POS_W[c["id"]]
        c.update({"visibilidad": v, "evolucion": e_, "etapa": et, "decision": dec, "inercia": ine, "evidencia": ev, "refs": rf})
    d_["anclas"][0].update({"visibilidad": 0.95, "evolucion": 0.55})
    d_["alcance"] = "servicio de turnos sin llamada (los tres entregables del paso 5 y lo que necesitan)"
    d_["enlaces"] = [{"de": "A1", "a": "C1"}, {"de": "A1", "a": "C2"}, {"de": "C1", "a": "C4"}, {"de": "C2", "a": "C4"}, {"de": "C2", "a": "C3"},
                     {"de": "C4", "a": "C5"}, {"de": "C1", "a": "C6"}]
    d_["notas"] = [{"texto": "La interfaz de la agenda la controla el proveedor", "visibilidad": 0.20, "evolucion": 0.36}]
    d_["fuentes"] = ["supuestos.csv", "lecciones.csv", "decisiones.csv (D-003)"]
dw = completar(repo, "wardley-entregables.json", prop_w, "pm-mapas-estrategicos propone ubicación, decisión y evidencia de cada componente; Pablo Rinaldi y Tomás Aguirre confirman",
               lambda d_: "\n".join(fila_w(c) for c in d_["componentes"]) + f"\n{len(d_['enlaces'])} enlaces · 1 nota")
run(f'{MAPAS} --proyecto {G} wardley validar entregables', repo)
run(f'{MAPAS} --proyecto {G} wardley render entregables --png no', repo)
png_mapa(repo, "wardley", "entregables", os.path.join(OUT, "g5-wardley.png"))
lect = re.findall(r"^\| (C\d) ([^|]+?) \|.*\| ([^|]+) \|$", open(os.path.join(repo, G, "02-planificacion", "visuales", "wardley-entregables.md"), encoding="utf-8").read(), re.M)
LOG.append(("(lectura sugerida de gestion/02-planificacion/visuales/wardley-entregables.md, contrastada con los nueve criterios del paso 5)",
            "\n".join(f"{i} {n}: {l}" for i, n, l in lect)))
run(E(f'estado.py --proyecto {G} artefacto mapa-wardley-entregables --ruta 02-planificacion/visuales/wardley-entregables.md --estado en-revision'), repo, mostrar=False); LOG.pop()
run(f'{MAPAS} --proyecto {G} recorrido semilla --slug paciente --titulo "Paciente que saca y cancela un turno (hoy)" --persona "Paciente que agenda por teléfono" '
    f'--etapas "Pedir el turno; Esperar el día; Cancelar o asistir" --fecha 2026-12-09', repo)
PASOS_R = [  # etapa, id, acción, punto de contacto, canal, emoción, fuente, dolor, causa, oportunidad, kano, objetivo, refs, backstage, soporte
    (0, "P1", "Llama al call center", "Call center", "teléfono", -1, "mandato §2: «el call center no da abasto»; 70 % de los turnos por teléfono",
     "Espera en línea en las horas pico", "rendimiento", "Sacar el turno en línea 24 × 7", "desempeno", 1, [S[0]], "La operadora busca un hueco en la agenda clínica", "Agenda clínica del proveedor"),
    (0, "P2", "Acuerda fecha y hora con la operadora", "Call center", "teléfono", 0, "supuesto declarado: sin datos de satisfacción del call center",
     "", "", "", "", None, [], "", ""),
    (1, "P3", "Anota el turno", "—", "papel", 0, "supuesto declarado", "", "", "", "", None, [], "", ""),
    (1, "P4", "Olvida el turno", "—", "—", -2, f"métrica: ausentismo del 18 % (mandato §4); el piloto con recordatorio lo bajó al 13,5 % ({S[1]})",
     "Nadie le recuerda el turno", "proceso-interno", "Recordatorio 48 h antes con confirmación", "obligatorio", 1, [S[1]], "El turno queda vacío y nadie lo reasigna", ""),
    (2, "P5", "Intenta avisar que no va", "Call center", "teléfono", -2, "supuesto declarado: solo se cancela llamando en horario de atención (mandato §2)",
     "Solo puede cancelar llamando en horario de atención", "proceso-interno", "Cancelar desde el recordatorio y liberar el turno", "desempeno", 1, [],
     "Recepción libera el turno a mano al día siguiente", "Agenda clínica del proveedor"),
    (2, "P6", "Se atiende en la policlínica", "Recepción", "presencial", 1, "supuesto declarado", "", "", "", "", None, [], "", "")]
def prop_r(d_):
    d_.update({"trabajo": "Conseguir un turno que le sirva y no perderlo", "disparador": "Necesita un control con su médica de cabecera",
               "exito": "Se atiende en la fecha elegida o libera el turno a tiempo", "fuentes": ["00-direccion/mandato.md", "supuestos.csv", "lecciones.csv"],
               "kpi": ["ausentismo mensual (B-01)", "% de turnos sacados en línea (B-02)"]})
    for k_, et in enumerate(d_["etapas"]): et["pasos"] = []
    for (ie, pid, acc, pc, canal, em, fu, do, ca, op, ka, ob, rf, bk, so) in PASOS_R:
        p_ = {"id": pid, "accion": acc, "punto_contacto": pc, "canal": canal, "emocion": em, "fuente_emocion": fu, "dolor": do, "tipo_causa": ca,
              "oportunidad": op, "kano": ka, "refs": rf}
        if ob is not None: p_["emocion_objetivo"] = ob
        if bk: p_["backstage"] = bk
        if so: p_["soporte"] = so
        d_["etapas"][ie]["pasos"].append(p_)
    d_.pop("insumos", None)
dr = completar(repo, "recorrido-paciente.json", prop_r, "pm-mapas-estrategicos propone el recorrido actual con la fuente de cada emoción; Inés Ferrer confirma",
               lambda d_: "\n".join(fila_r(et, p_) for et in d_["etapas"] for p_ in et["pasos"]) + f"\nKPI: {'; '.join(d_['kpi'])} (business case esquemático §5)")
run(f'{MAPAS} --proyecto {G} recorrido validar paciente', repo)
run(f'{MAPAS} --proyecto {G} recorrido render paciente --png no', repo)
png_mapa(repo, "recorrido", "paciente", os.path.join(OUT, "g5-recorrido.png"))
run(E(f'estado.py --proyecto {G} artefacto mapa-recorrido-paciente --ruta 02-planificacion/visuales/recorrido-paciente.md --estado en-revision'), repo, mostrar=False); LOG.pop()
run(f'{MAPAS} --proyecto {G} recorrido candidatos paciente', repo)
# hacer o comprar de C2 (pm-direccion-decisiones con pm-adquisiciones): matriz con el conjunto de criterios hacer-o-comprar;
# el expediente trae el contexto de los mapas (C2 nombrado en la hoja y el paso P4, que cita S-002); la elección queda
# citada en el componente (mapas.py vincular)
HC = "hacer-comprar-c2"; RHC = f"03-control/decisiones/{HC}"
run(f'{DEC} matriz {HC} --proponer --tipo adquisicion --criterios hacer-o-comprar --ids entregables:C2,{S[1]} '
    f'--pregunta "¿Compramos una plataforma, construimos o tercerizamos los recordatorios y la confirmación (C2)?" --fecha 2026-12-09', repo)
crit_c2 = open(os.path.join(repo, G, RHC, "criterios.csv"), encoding="utf-8").read().replace("[por confirmar]", f"{EJ} (2026-12-09)")
escribir(repo, f"{RHC}/criterios.csv", crit_c2)
escribir(repo, f"{RHC}/opciones.csv", f"""opcion,descripcion,ref,diferenciacion,diferenciacion_fuente,costo_total,costo_total_fuente,tiempo_disponible,tiempo_disponible_fuente,dependencia_proveedor,dependencia_proveedor_fuente,capacidad_interna,capacidad_interna_fuente,riesgo_commodity,riesgo_commodity_fuente,notas
O1,Comprar una plataforma de recordatorios,,2,mapa C2: producto; plantillas configurables como en cualquier plataforma,120000,business case esquemático §4 opción 1: 30.000 + 18.000 × 5 años,6,cotización de la plataforma del piloto de {S[1]} (Tomás Aguirre),3,cotización: contrato anual; exporta plantillas y datos,4,TI administró la plataforma en el piloto de {S[1]},1,mapa C2: producto con plataformas en el mercado,
O2,Construir un módulo propio,,4,mapa C2: control total del mensaje y de la confirmación,192000,estimación de TI: 1.200 h × USD 60 + operación 24.000 × 5 años,20,estimación de TI (Tomás Aguirre),1,sin proveedor de plataforma,2,TI está en el adaptador de la agenda (C4); {L['L2']}: 4 semanas estimadas y 14 reales,5,"mapa C2: producto 0,62: lo construido repite lo que ya se compra",
O3,Tercerizar el servicio de recordatorios y confirmación,,1,el proveedor define mensajes y flujo,140000,cotización de servicio gestionado: 28.000 × 5 años,10,cotización: incorporación del servicio y contrato,4,el proveedor opera la confirmación y los datos de contacto,3,contrato de servicio sin experiencia previa en la red,2,mapa C2: producto; el riesgo de obsolescencia queda en el proveedor,
""")
LOG.append((f"(pm-direccion-decisiones con pm-adquisiciones: el modelo completa la hoja con la fuente de cada puntaje; la ejecutiva confirma los pesos → gestion/{RHC}/)",
            "criterios.csv: " + " · ".join(f"{f['criterio']} {f['peso']} ({f['sentido']}, {f['escala']})" for f in csv.DictReader(io.StringIO(crit_c2)))
            + f" · fuente de los pesos: {EJ} (2026-12-09)\nopciones.csv:\n" + "\n".join(
                f"{f['opcion']} {f['descripcion']} · " + " · ".join(f"{c} {f[c]} ({f[c + '_fuente']})" for c in ("diferenciacion", "costo_total", "tiempo_disponible", "dependencia_proveedor", "capacidad_interna", "riesgo_commodity"))
                for f in csv_filas(repo, f"{RHC}/opciones.csv"))))
run(f"{DEC} expediente --hoja {HC} --corte 2026-12-09 --max-items 3", repo, corte=200)
run(f"{DEC} matriz {HC}", repo)
MZ2 = json.loads(subprocess.run(f"{DEC} matriz {HC} --json", shell=True, cwd=repo, capture_output=True, text=True).stdout)
out_c2 = run(f'{DEC} matriz {HC} --elegir {MZ2["recomendada"]} --por "{EJ}" --fecha 2026-12-09', repo)
D_C2 = re.search(r"decisión (D-\d{3})", out_c2).group(1)
run(f'{MAPAS} --proyecto {G} wardley render entregables --png no', repo, mostrar=False); LOG.pop()
c2_ = next(c for c in json.load(open(RMAP(repo, "wardley-entregables.json"), encoding="utf-8"))["componentes"] if c["id"] == "C2")
LOG.append(("(gestion/02-planificacion/mapas/wardley-entregables.json, componente C2 después de elegir)", fila_w(c2_)))
pz2 = {o["opcion"]: o for o in MZ2["opciones"]}; sd2 = next(x for x in MZ2["sensibilidad"] if x["criterio"] == "diferenciacion")["sube"]
NC2 = {"diferenciacion": "Diferenciación", "costo_total": "Costo total", "tiempo_disponible": "Tiempo", "dependencia_proveedor": "Dependencia",
       "capacidad_interna": "Capacidad", "riesgo_commodity": "Commodity"}
matriz_grafico(MZ2, os.path.join(OUT, "g5-hacer-comprar-c2.png"),
               f"Comprar gana con {V.miles(pz2['O1']['puntaje'], 1)}: construir solo pasa con diferenciación ≥ {V.miles(sd2['peso'], 1)}",
               subtitulo=f"C2 recordatorios (producto 0,62 en el mapa) · seis criterios con fuente · pesos de la ejecutiva · {D_C2} citada en C2",
               fuente=f"decision.py matriz {HC} --json (pm-direccion-decisiones) · wardley-entregables.json (pm-mapas-estrategicos)",
               nombres_c=NC2, nombres_o={"O1": "O1 · comprar", "O2": "O2 · construir", "O3": "O3 · tercerizar"}, crit_sens="diferenciacion", etiqueta_sens="diferenciación")
sanidad(repo, "2026-12-09")

P("Paso 6 · Project brief, requisitos, roadmap y canvas → puerta autorizar-inicio")
escribir(repo, "02-planificacion/requisitos.md", """# Requisitos · Turnos en línea

| Id | Requisito | Prioridad | Fuente | Criterio |
|---|---|---|---|---|
| REQ-001 | Enviar un recordatorio 48 h antes del turno por mensajería, con consentimiento | Must | mandato | 95 % de los turnos con recordatorio enviado |
| REQ-002 | Plantillas de recordatorio por especialidad | Should | piloto | plantilla aprobada por especialidad |
| REQ-003 | Confirmar o cancelar desde el recordatorio y liberar el turno | Must | piloto (S-002) | turno liberado en menos de 1 minuto |
| REQ-004 | Sacar turno en línea por especialidad y policlínica | Must | mandato (S-001) | reserva confirmada en menos de 3 pasos |
| REQ-005 | Reprogramar o cancelar en línea | Should | mandato | sin llamada al call center |
| REQ-006 | Reservar y cancelar en la agenda clínica en tiempo real | Must | prueba técnica (S-003) | respuesta < 2 s |
| REQ-007 | Uso accesible para pacientes mayores de 65 (WCAG 2.1 AA) | Should | lección L-001 | auditoría de accesibilidad sin fallas graves |

## Supuestos y dependencias
- REQ-006 depende de la interfaz del proveedor de la agenda clínica [por confirmar: S-003].
""")
LOG.append(("(pm-planificacion-por-productos, templates/requisitos.md → gestion/02-planificacion/requisitos.md; sin BMAD, pm-method es la fuente de la especificación)", "7 requisitos REQ-001…REQ-007 (5 Must, 2 Should)"))
run(E(f'especificacion.py --proyecto {G} fuente'), repo)
run(E(f'especificacion.py --proyecto {G} resumen'), repo)
run(f'{MAPAS} --proyecto {G} vincular paciente P5 --refs REQ-003,REQ-005', repo)
run(f'{MAPAS} --proyecto {G} recorrido render paciente --png no', repo, mostrar=False); LOG.pop()
run(f'{MAPAS} --proyecto {G} controles', repo)
doc(repo, "project-brief", "01-inicio/project-brief.md", f"""# Project brief · Turnos en línea · Policlínicas Altamar (v0.1)

## 1. Definición
Objetivo: bajar el ausentismo y las llamadas para agendar. Alcance: recordatorios con confirmación, turnos en línea,
integración con la agenda clínica, capacitación. Exclusión: telemedicina y pagos en línea.
## 2. Caso de negocio esquemático
Ver 00-direccion/business-case-esquematico.md: opción 2 en dos releases (VAN USD {usd(VD[2]['van'])}, repago {V.miles(VD[2]['repago'], 2)} años).
## 3. Producto del proyecto
Servicio de turnos sin llamada: recordatorios (REQ-001…003), turnos en línea (REQ-004, 005, 007), integración (REQ-006).
## 4. Enfoque del proyecto
Interno con el proveedor de la agenda; adaptar su interfaz, no reemplazarla; híbrido (decisión del 2026-12-09):
integración predictiva, recordatorios incrementales, portal adaptativo. Sostenibilidad: menos traslados por turnos perdidos.
## 5. Estructura
Ejecutiva Carmen Olivera; gestor Pablo Rinaldi; usuaria sénior y proveedor sénior a designar en la iniciación.
## 6. Hitos y etapas
Etapa 1 iniciación (hasta 2027-01-15) · etapa 2 recordatorios · etapa 3 turnos en línea (puerta condicionada a {S[2]}).
## 7. Lecciones aplicadas
{L['L1']} canal asistido · {L['L2']} prueba técnica antes de fechas · {L['L3']} línea base medida (ausentismo 18 %).
## 8. Tolerancias del proyecto (las fija la ejecutiva)
tiempo ±4 semanas · costo ±10 % · alcance: Must sin tolerancia · beneficios −15 % · riesgo: ningún riesgo alto sin respuesta.
""", origen="pm-mandato-y-brief, templates/project-brief.md")
doc(repo, "roadmap", "01-inicio/roadmap.md", """# Hoja de ruta inicial · Turnos en línea
| Etapa | Contenido | Puerta de salida |
|---|---|---|
| 0 · Puesta en marcha | mandato, supuestos, experimentos, brief | autorizar-inicio (2026-12-11) |
| 1 · Iniciación | business case, PBS, presupuesto, enfoques, PID | autorizar-proyecto y autorizar-etapa (2027-01-15) |
| 2 · Release 1: recordatorios | REQ-001…003 en 6 policlínicas | autorizar-etapa (adopción y ausentismo medidos) |
| 3 · Release 2: turnos en línea | REQ-004…007 con la integración | autorizar-cierre |
Revisión del enfoque de entrega en cada puerta de etapa.
""", origen="pm-mandato-y-brief, templates/roadmap.md")
doc(repo, "canvas-arranque", "01-inicio/canvas-arranque.md", f"""# Lienzo de arranque · Turnos en línea
Problema: 18 % de ausentismo y call center saturado · Pacientes: 240.000 turnos/año · Propuesta: sacar, confirmar y cancelar sin llamar ·
Supuestos críticos: {', '.join(crit_baja)} · Experimentos: prueba de humo, piloto, prueba técnica · Métricas: ausentismo, % de turnos en línea ·
Costos: 180.000 (orden de magnitud) · Restricción: se mantienen teléfono y presencial.
""", origen="pm-mandato-y-brief, templates/canvas-arranque.md")
doc(repo, "plan-etapa-1", "02-planificacion/plan-etapa-1.md", f"# Plan de la etapa 1 (iniciación) · 2026-12-11 a 2027-01-15\n\nBusiness case completo, PBS y WBS, presupuesto, enfoques, PID; prueba técnica de {S[2]} (2027-01-14).\n", origen="pm-plan-etapa-y-limites")
# cada lección previa ya tiene su control temprano (brief §7): pm-lecciones-aprendidas la marca accionada-proyecto con el artefacto
for k_, ctl in (("L1", "project-brief §7, canal asistido"), ("L2", f"project-brief §7 y plan-etapa-1, prueba técnica de {S[2]} antes de fechas"),
                ("L3", f"{S[1]}, línea base medida antes del piloto (ausentismo 18 %)")):
    act(repo, "lecciones", L[k_], estado="accionada-proyecto", notas=f"incorporada: {ctl}")
run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±4 semanas" "costo=±10 %" "alcance=Must sin tolerancia" "beneficios=-15 %" "riesgo=ningún riesgo alto sin respuesta"'), repo)
puerta_f(repo, "autorizar-inicio", EJ, "2026-12-11", "--fin 2027-01-15")
for c in ("project-brief", "business-case-esquematico"):
    run(E(f'estado.py --proyecto {G} aprobar {c} --por "{EJ}" --version 1.0 --fecha 2026-12-11'), repo)
# la junta aprueba el business case esquemático con la opción 2: la elección de la matriz del paso 4 se registra en esa
# misma decisión (--decision), sin crear otra
D_BCE = next(f["id"] for f in csv_filas(repo, "03-control/registros/decisiones.csv") if f["decision"] == "aprobado business-case-esquematico v1.0")
run(f'{DEC} matriz {HOJA} --elegir O2 --por "{EJ}" --decision {D_BCE} --fecha 2026-12-11', repo)
fd = next(f for f in csv_filas(repo, "03-control/registros/decisiones.csv") if f["id"] == D_BCE)
LOG.append((f"(gestion/03-control/registros/decisiones.csv, fila {D_BCE})", "\n".join(f"{k}={fd[k]}" for k in ("id", "fecha", "decision", "opciones_consideradas", "decidido_por", "nivel", "artefactos_afectados", "notas"))))
run(E(f'estado.py --proyecto {G} resumen'), repo)

# ------------------------------------------------------------------------------------------- clase 2
P("Paso 7 · Retomar la sesión, mapa de beneficios y enfoque de beneficios (P-04)")
run(E(f'estado.py --proyecto {G} contexto --corte 2027-01-08'), repo)
run(E(f'estado.py --proyecto {G} radar --linea --corte 2027-01-08'), repo)   # la línea que el hook de inicio agrega a la sesión
doc(repo, "business-case", "00-direccion/business-case.md", f"""# Business case · Turnos en línea (v0.9, completo)

## 3. Cadena de valor
Salidas (recordatorios, turnos en línea, integración) → capacidades (confirmar y cancelar sin llamar; reservar 24×7) →
resultados (menos ausentismo; menos llamadas) → beneficios B-01, B-02 → objetivo: más pacientes atendidos con la misma capacidad.

## 5. Beneficios y des-beneficios
| Id | Beneficio | Medida | Línea base | Meta | Dueña | Tolerancia |
|---|---|---|---|---|---|---|
| B-01 | Turnos recuperados | ausentismo mensual | 18 % | 13,5 % | Inés Ferrer | −15 % |
| B-02 | Llamadas evitadas | % de turnos sacados en línea | 0 % | 40 % desde el año 2 | Inés Ferrer | −15 % |
| DB-01 | Dos puestos del call center se reasignan a recepción | puestos reasignados | 0 | 2 | Inés Ferrer | — |

## 9. Evaluación de la inversión
Opción 2: VAN USD {usd(VD[2]['van'])}, TIR {pct(VD[2]['tir'])} %, repago {V.miles(VD[2]['repago'], 2)} años (r = 10 %, 5 años; inversion.py). Se recalcula con el presupuesto de la iniciación (paso 9).
""", version="0.9", origen="pm-caso-de-negocio, modo completo")
run(E(f'puertas.py --proyecto {G} verificar autorizar-proyecto'), repo, ok=(0, 1, 2))
doc(repo, "enfoque-beneficios", "00-direccion/enfoque-beneficios.md", """# Enfoque de gestión de beneficios (v0.9)
| Beneficio | Medida | Línea base | Meta | Dueña | Mediciones |
|---|---|---|---|---|---|
| B-01 turnos recuperados | ausentismo mensual (agenda clínica) | 18 % | 13,5 % | Inés Ferrer | fin de la etapa 2; 6 y 12 meses después del cierre |
| B-02 llamadas evitadas | % de turnos sacados en línea; llamadas atendidas | 0 % | 40 % desde el año 2 | Inés Ferrer | fin de la etapa 3; 6 y 12 meses después del cierre |
| DB-01 reasignación | puestos reasignados | 0 | 2 | Inés Ferrer | al cierre |
Indicador adelantado: adopción por franja de edad (lección L-001). Las revisiones posteriores al cierre las ejecuta y
financia la red (usuaria sénior). Tolerancia: −15 % sobre la meta.
""", version="0.9", origen="pm-caso-de-negocio, templates/enfoque-beneficios.md")

P("Paso 8 · Descripción del producto del proyecto y PBS/WBS por productos")
doc(repo, "descripcion-producto-proyecto", "02-planificacion/descripcion-producto-proyecto.md", """# Descripción del producto del proyecto · Servicio de turnos sin llamada (v0.9)
1. Propósito: que el paciente saque, confirme y cancele turnos sin llamar, y que la red recupere los turnos que hoy se pierden.
2. Productos mayores: recordatorios y confirmación · turnos en línea · integración con la agenda clínica · capacitación de recepción y call center.
4. Expectativas de calidad: el turno se libera al cancelar; nadie queda sin canal (teléfono y presencial se mantienen).
5. Criterios de aceptación priorizados: Must REQ-001, 003, 004, 006 · Should REQ-002, 005, 007.
6. Tolerancias de calidad: REQ-006 respuesta < 2 s; accesibilidad WCAG 2.1 AA sin fallas graves.
7. Aceptación: usuaria sénior Inés Ferrer por release; aseguramiento Valeria Santos revisa la evidencia.
""", version="0.9", origen="pm-planificacion-por-productos, templates/descripcion-producto-proyecto.md")
WBS = """codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref
1,Gestión del proyecto,producto,Pablo Rinaldi,,,
1.1,Gestión de etapas,paquete,Pablo Rinaldi,320,19200,
2,Recordatorios y confirmación,producto,Inés Ferrer,,,
2.1,Plataforma de mensajería y plantillas,paquete,Nicolás Pereyra,160,9600,REQ-001; REQ-002
2.2,Confirmación y liberación de turnos,paquete,Nicolás Pereyra,200,12000,REQ-003
3,Turnos en línea,producto,Inés Ferrer,,,
3.1,Portal web y app de turnos (incluye diseño UX externo 12.000),paquete,Nicolás Pereyra,900,66000,REQ-004; REQ-005; REQ-007
4,Integración con la agenda clínica,producto,Tomás Aguirre,,,
4.1,Adaptador de la interfaz de la agenda,paquete,Tomás Aguirre,480,28800,REQ-006
5,Transición,producto,Inés Ferrer,,,
5.1,Capacitación de recepción y call center,paquete,Inés Ferrer,120,7200,
5.2,Puesta en producción,hito,Inés Ferrer,,,
"""
escribir(repo, "02-planificacion/wbs.csv", WBS)
run(E(f'wbs.py {G}/02-planificacion/wbs.csv --titulo "Turnos en línea" --mermaid {G}/02-planificacion/visuales/wbs.md'), repo)
art(repo, "pbs-wbs", "02-planificacion/wbs.csv"); LOG.pop()
base_wbs = sum(float(f["costo"] or 0) for f in csv.DictReader(io.StringIO(WBS)) if f["tipo"] == "paquete")

P("Paso 9 · Riesgos con EMV, presupuesto con reservas (sin doble conteo) y presupuestos de la junta")
RISK = [dict(categoria="externo", causa=f"La agenda clínica del proveedor no tiene interfaz documentada ({L['L2']}, {S[2]})", evento="La integración en tiempo real se atrasa",
             efecto="Atraso del release de turnos en línea (WBS 4.1 y 3.1)", tipo="amenaza", probabilidad=3, impacto=4, impacto_monetario=30000, proximidad="corto-plazo",
             respuesta="reducir", acciones="prueba técnica en el entorno del proveedor (S-003) y adaptador detrás de una interfaz propia · costo USD 0 (dentro de la etapa 1)",
             probabilidad_residual=2, impacto_residual=4, propietario="Tomás Aguirre", ejecutor="Nicolás Pereyra", disparador="prueba técnica sin 50 de 50 reservas"),
        dict(categoria="organizacional", causa=f"Pacientes mayores de 65 con poca comodidad digital ({L['L1']})", evento=f"La adopción en línea queda bajo el 40 % ({S[0]})",
             efecto="B-02 menor que lo previsto", tipo="amenaza", probabilidad=3, impacto=3, impacto_monetario=12000, proximidad="mediano-plazo",
             respuesta="reducir", acciones="canal asistido en recepción y llamada de confirmación para mayores de 65 · costo USD 4.000",
             probabilidad_residual=2, impacto_residual=3, propietario="Inés Ferrer", ejecutor="Marta Gil", disparador="adopción por franja de edad < 15 % al mes 3 del release 2"),
        dict(categoria="externo", causa=f"No hay dictamen legal sobre el consentimiento para recordatorios por mensajería ({S[5]})", evento="La asesoría legal exige un consentimiento explícito separado",
             efecto="Rediseño del alta del turno y menos pacientes con recordatorio (WBS 2.1)", tipo="amenaza", probabilidad=2, impacto=3, impacto_monetario=10000, proximidad="corto-plazo",
             respuesta="contingencia", acciones="si el dictamen lo exige: consentimiento explícito al pedir el turno y recordatorio por correo para quien no consienta · costo USD 0",
             probabilidad_residual=2, impacto_residual=2, propietario="Carmen Olivera", ejecutor="Pablo Rinaldi", disparador="dictamen de la asesoría legal (2027-01-29)")]
RID = [reg(repo, "riesgos", fecha_identificacion="2027-01-11", autor="Pablo Rinaldi", estado="en-seguimiento", fecha_revision="2027-01-29", **r_) for r_ in RISK]
run(f'{MAPAS} --proyecto {G} vincular entregables C5 --refs {RID[0]}', repo)
run(f'{MAPAS} --proyecto {G} wardley render entregables --png no', repo, mostrar=False); LOG.pop()
run(f'{MAPAS} --proyecto {G} controles', repo)
riesgos_f = csv_filas(repo, "03-control/registros/riesgos.csv")
emv = sum(float(f["valor_esperado"]) for f in riesgos_f); c_resp = 4000
conting = emv + c_resp; bac = base_wbs + conting; gest = round(0.05 * bac); autorizado = bac + gest; CAMBIO, LIM = 10000, 3000
LOG.append(("(pm-costos-presupuesto: reservas sin doble conteo, SPEC §1.10.6 y references/guia.md §3)",
            f"""Paquetes base (Σ WBS, wbs.py)                         {usd(base_wbs):>9}
Contingencia = Σ EMV ({' + '.join(usd(float(f['valor_esperado'])) for f in riesgos_f)} = {usd(emv)}) + respuestas ({usd(c_resp)})   {usd(conting):>9}
BAC = paquetes base + contingencia                     {usd(bac):>9}
Reserva de gestión = 5 % del BAC (la libera solo la junta)   {usd(gest):>9}
Presupuesto autorizado = BAC + reserva de gestión      {usd(autorizado):>9}
Presupuesto de cambio (aparte; autoridad de cambio, tope {usd(LIM)} por cambio)   {usd(CAMBIO):>9}
Clase de exactitud: presupuestaria (−10/+25 %). El orden de magnitud de la puesta en marcha (180.000, −25/+75 % = {usd(180000 * 0.75)}–{usd(180000 * 1.75)}) contiene a {usd(autorizado + CAMBIO)}."""))
PRES = f"""# Presupuesto · Turnos en línea (v0.9)
| Componente | USD | Criterio |
|---|---|---|
| Paquetes base | {usd(base_wbs)} | Σ WBS (wbs.py), tarifa USD 60/h; UX externo 12.000 en 3.1 |
| Contingencia | {usd(conting)} | Σ EMV de {', '.join(RID)} ({usd(emv)}) + costo de respuestas ({usd(c_resp)}) |
| **BAC** | **{usd(bac)}** | paquetes base + contingencia |
| Reserva de gestión | {usd(gest)} | 5 % del BAC; fuera del BAC; la libera la junta |
| **Presupuesto autorizado** | **{usd(autorizado)}** | BAC + reserva de gestión |
| Presupuesto de cambio | {usd(CAMBIO)} | aparte; autoridad de cambio con tope de {usd(LIM)} por cambio |
"""
doc(repo, "presupuesto", "02-planificacion/presupuesto.md", PRES, version="0.9", origen="pm-costos-presupuesto, templates/presupuesto.md")
run(E(f'estado.py --proyecto {G} presupuesto cambio={CAMBIO} riesgo={conting:.0f} gestion={gest} limite_autoridad_cambio={LIM} --por "{EJ}" --fecha 2027-01-12'), repo)
inv_final = autorizado + CAMBIO
OM, PI = "2 · Con el orden de magnitud", "2 · Con el presupuesto"
f2 = [x for x in flujos(0.135) if x[0] == OPC[2]]
jf = inversion(repo, "00-direccion/inversion/flujos-opcion-2-presupuesto.csv",
               [(OM,) + x[1:] for x in f2] + [(PI, c, t, [-inv_final] + [0] * 5 if t == "inversion" else fl) for _, c, t, fl in f2])
van_final, rep_final, tir_final = jf["opciones"][PI]["van"], jf["opciones"][PI]["repago"], jf["opciones"][PI]["tir"]
eq_final = next(c["equilibrio"] for c in jf["opciones"][PI]["sensibilidad"] if c["concepto"] == "Llamadas evitadas (B-02)")
LOG.append(("(lectura de pm-caso-de-negocio, de inversion.py --json)",
            f"Inversión {usd(inv_final)} = presupuesto autorizado {usd(autorizado)} + presupuesto de cambio {usd(CAMBIO)} (orden de magnitud: 180.000) · "
            f"VAN USD {usd(van_final)} ({usd(van_final - VD[2]['van'])}) · TIR {pct(tir_final)} % · repago {V.miles(rep_final, 2)} años · "
            f"adopción estable de equilibrio {pct(eq_final * ADOP[-1])} % (con el orden de magnitud: {pct(adop_eq)} %)"))
V.barras_comparadas(["Paquetes base (WBS)", "Contingencia (EMV + respuestas)", "BAC", "Reserva de gestión", "Presupuesto autorizado", "Presupuesto de cambio (aparte)"],
                    [[base_wbs, conting, bac, gest, autorizado, CAMBIO]], os.path.join(OUT, "g5-presupuesto.png"),
                    f"La junta autoriza USD {usd(autorizado)} y cada reserva tiene su dueño",
                    subtitulo=f"BAC = base + contingencia · reserva de gestión fuera del BAC · cambio aparte (tope de {usd(LIM)} por cambio)",
                    fuente="wbs.py · riesgos.csv (EMV) · estado.json presupuestos (estado.py presupuesto, 2027-01-12)", nombres=["USD"])

P("Paso 10 · Organización, interesados y RACI (breve)")
run(E(f'estado.py --proyecto {G} rol usuario_senior="Inés Ferrer" proveedor_senior="Tomás Aguirre" product_owner="Inés Ferrer" autoridad_cambio="Inés Ferrer" aseguramiento="Valeria Santos" jefes_equipo="Nicolás Pereyra"'), repo)
run(E(f'estado.py --proyecto {G} agil cadencia_iteracion_dias=14'), repo, mostrar=False); LOG.pop()
ST = {}
for nombre, rol, pod, inte, ac, de in (("Carmen Olivera", "Gerenta general · ejecutiva", "alto", "alto", "lider", "lider"),
                                       ("Inés Ferrer", "Jefa de atención al paciente · usuaria sénior", "alto", "alto", "partidario", "lider"),
                                       ("Tomás Aguirre", "Jefe de TI · proveedor sénior", "alto", "medio", "partidario", "partidario"),
                                       ("Dirección médica", "Libera las agendas (S-004)", "alto", "medio", "neutral", "partidario"),
                                       ("Recepción y call center", "Supervisa Marta Gil", "medio", "alto", "resistente", "partidario"),
                                       ("Comisión de usuarios", "Representa a los pacientes", "medio", "alto", "neutral", "partidario"),
                                       ("Proveedor de la agenda clínica", "Dueño de la interfaz (S-003)", "alto", "medio", "neutral", "partidario")):
    ST[nombre] = reg(repo, "stakeholders", nombre=nombre, rol_organizacion=rol, poder=pod, interes=inte, actitud=ac, nivel_compromiso_actual=ac, nivel_compromiso_deseado=de, confidencial="no")
nraci = 0
for elem, tipo, descr, filas_r in (("2", "producto", "Recordatorios y confirmación", (("Tomás Aguirre", "R"), ("Inés Ferrer", "A"), ("Recepción y call center", "C"), ("Comisión de usuarios", "I"), ("Carmen Olivera", "I"))),
                                   ("3", "producto", "Turnos en línea", (("Tomás Aguirre", "R"), ("Inés Ferrer", "A"), ("Dirección médica", "C"), ("Comisión de usuarios", "C"), ("Recepción y call center", "I"), ("Carmen Olivera", "I"))),
                                   ("4", "producto", "Integración con la agenda clínica", (("Proveedor de la agenda clínica", "R"), ("Tomás Aguirre", "A"), ("Inés Ferrer", "I"), ("Carmen Olivera", "I"))),
                                   ("REQ-006", "requisito", "Reservar y cancelar en la agenda clínica en tiempo real", (("Proveedor de la agenda clínica", "R"), ("Tomás Aguirre", "A"), ("Inés Ferrer", "C")))):
    for quien, rol in filas_r:
        run(E(f'registro.py --proyecto {G} agregar raci --campo "elemento={elem}" --campo tipo_elemento={tipo} --campo "descripcion={descr}" --campo stakeholder_id={ST[quien]} --campo rol={rol}'), repo, mostrar=False); LOG.pop(); nraci += 1
LOG.append((f"(pm-interesados registra la matriz RACI en raci.csv con registro.py agregar raci --campo elemento=<código WBS o id de requisito> …: {nraci} filas en 4 elementos, una A por elemento)", ""))
run(f'python3 {IN} --proyecto {G} --medio bajo matriz', repo)
run(f'python3 {IN} --proyecto {G} --medio bajo raci', repo)

P("Paso 10b · Personas de usuario: quién pide, usa o aprovecha cada capacidad")
run(f'python3 {IN} --proyecto {G} personas candidatos', repo)
cand = personas_json(repo, "candidatos")[0]
# Inés Ferrer confirma la candidata y completa lo que usa y sus beneficios; agrega dos personas que el recorrido no muestra
PU = [reg(repo, "personas", nombre=cand["nombre"], descripcion="Adulto que hoy saca, confirma y cancela el turno llamando al call center", objetivo=cand["objetivo"],
          dolores=cand["dolores"], contexto_uso=cand["contexto_uso"], fuente=cand["fuente"], evidencia=cand["evidencia"], stakeholder_id=cand["stakeholder_id"],
          usa=";".join(sorted(set(cand["usa"].split(";")) | {"REQ-001", "REQ-004"})), beneficios="B-01;B-02"),
      reg(repo, "personas", nombre="Recepcionista del call center", descripcion="Atiende el teléfono en las horas pico y libera a mano los turnos que se cancelan",
          objetivo="Atender a quien llama sin colas y no perder los turnos que se liberan", dolores="Colas en las horas pico; libera los turnos cancelados al día siguiente, a mano",
          contexto_uso="Puesto de recepción y call center, en horario de atención", fuente="supuesto",
          evidencia="backstage de P1 y P5 en recorrido-paciente.json; a validar con entrevistas en recepción", stakeholder_id=ST["Recepción y call center"],
          solicita="REQ-003", usa="REQ-002", beneficia="REQ-004", beneficios="B-02;DB-01"),
      reg(repo, "personas", nombre="Paciente mayor de 65", descripcion="Prefiere el teléfono; usa el celular para mensajes, no para aplicaciones",
          objetivo="No perder el turno sin tener que usar una aplicación", dolores="No usa aplicaciones; necesita que alguien lo atienda",
          contexto_uso="Recibe mensajes en el celular; agenda por teléfono o en recepción", fuente="documento",
          evidencia=f"{L['L1']} (App de resultados de laboratorio, 2024: 11 % de uso en mayores de 65)", stakeholder_id=ST["Comisión de usuarios"],
          solicita="REQ-007", usa="REQ-001;REQ-003", beneficios="B-01")]
sanidad(repo, "2027-01-12")
act(repo, "personas", PU[0], beneficia="REQ-006")
run(f'python3 {IN} --proyecto {G} personas mapa', repo)
run(f'python3 {IN} --proyecto {G} personas priorizacion', repo)
mp, pp = personas_json(repo, "mapa"), personas_json(repo, "priorizacion")
todas = [c["id"] for c in mp["capacidades"] if len(c["personas"]) == len(mp["personas"])]
musts = [c for c in mp["capacidades"] if c["prioridad"] == "must"]
matriz_personas(mp, pp, os.path.join(OUT, "g5-personas-mapa.png"),
                f"Los {len(musts)} Must tienen persona y {', '.join(todas)} sirve a las {len(mp['personas'])}",
                subtitulo=f"Turnos en línea · capacidad × persona al 2027-01-12 · el paciente mayor de 65 no usa el portal: lo suyo es el recordatorio",
                fuente="interesados.py personas mapa y priorizacion --json · personas.csv · requisitos.md (MoSCoW)")

P("Paso 11 · Enfoques de gestión adaptados al contexto (tailoring)")
regs(repo, "decisiones", fecha="2027-01-12", decision="Nivel de formalidad de los enfoques: una página cada uno (riesgo, calidad, issues y cambios, comunicación); datos digitales dentro de calidad (datos de salud); sostenibilidad dentro del business case",
     decidido_por="Gestor: Pablo Rinaldi", nivel="gestor")
for clave, txt in (
        ("enfoque-riesgo", f"# Enfoque de riesgos (una página)\nEscala 1–5, alto ≥ 15. Revisión en cada planificación de sprint. Contingencia {usd(conting)} (EMV + respuestas); la reserva de gestión ({usd(gest)}) la libera solo la junta. Supuestos que no se validan a tiempo pasan a riesgo ({S[5]} → {RID[2]})."),
        ("enfoque-calidad", "# Enfoque de calidad (una página)\nDoD por historia; aceptación por release (Inés Ferrer); aseguramiento independiente (Valeria Santos). Datos de salud: mínimo necesario, consentimiento registrado, sin datos clínicos en los mensajes. REQ-006 con prueba de respuesta; REQ-007 con auditoría WCAG 2.1 AA."),
        ("enfoque-issues-cambios", f"# Enfoque de issues y cambios (una página)\nCinco tipos de issue. Autoridad de cambio: Inés Ferrer, hasta USD {usd(LIM)} por cambio y {usd(CAMBIO)} en total (presupuesto de cambio); por encima, la junta. El PO intercambia Should/Could dentro de la tolerancia de alcance sin solicitud de cambio."),
        ("enfoque-comunicacion", "# Enfoque de comunicación (una página)\nHighlight quincenal a la junta con ausentismo y adopción; demo al final de cada sprint con recepción y la comisión de usuarios; regla extraordinaria: todo pronóstico fuera de tolerancia se informa en 48 h.")):
    doc(repo, clave, f"02-planificacion/enfoques/{clave}.md", txt + "\n", version="0.9", origen="pm-enfoques-gestion, versión de una página")

P("Paso 12 · Bloque C: el mismo proyecto, tres diseños (interno pequeño, regulado, producto digital ágil)")
DIS = [("Interno pequeño", "predictivo", 2, ["tiempo=±2 semanas", "costo=±15 %"],
        ["mandato", "project-brief", "acta-constitucion", "pid", "plan-etapa-1", "plan-etapa-2", "enfoque-riesgo"],
        "perfil mínimo; brief con business case fusionado; acta + PID breve; un enfoque de una página (riesgos, issues y cambios); highlight mensual"),
       ("Regulado (datos de salud)", "predictivo", 4, ["tiempo=±2 semanas", "costo=±5 %", "alcance=sin tolerancia", "calidad=cero no conformidades de privacidad", "beneficios=-10 %", "riesgo=ningún riesgo alto sin respuesta", "sostenibilidad=-10 %"],
        ["mandato", "propuesta-proyecto", "project-brief", "business-case", "enfoque-beneficios", "enfoque-calidad", "enfoque-riesgo", "enfoque-issues-cambios",
         "enfoque-comunicacion", "enfoque-datos-digitales", "enfoque-sostenibilidad-gestion", "descripcion-producto-proyecto", "pid", "plan-proyecto", "plan-etapa-1", "plan-etapa-2"],
        "perfil completo; PID índice; aseguramiento independiente; auditoría de privacidad como revisión de calidad; highlight quincenal; cambios solo con la junta"),
       ("Producto digital ágil", "agil", 3, ["tiempo=fecha fija (0 semanas)", "costo=±5 %", "alcance=Must intocables; Could negociables"],
        ["mandato", "project-brief", "declaracion-vision", "business-case", "pid", "release-plan", "plan-etapa-1",
         "enfoque-calidad", "enfoque-riesgo", "enfoque-issues-cambios", "enfoque-comunicacion", "enfoque-datos-digitales"],
        "perfil ágil mínimo; PID compacto; enfoques de una página con DoD/DoR; el PO intercambia alcance; demo y burn-up por sprint")]
RUTA_ART = lambda c: ("00-direccion/" if c in ("mandato", "business-case", "enfoque-beneficios", "pid") else "01-inicio/" if c in ("propuesta-proyecto", "project-brief", "declaracion-vision", "acta-constitucion") else
                      "02-planificacion/enfoques/" if c.startswith("enfoque-") else "02-planificacion/") + c + ".md"
medidas = []
for k, (nombre, enf, etapas, tols, arts, desc) in enumerate(DIS, 1):
    rd = os.path.join(base, f"diseno-{k}"); os.makedirs(rd)
    run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Turnos en línea · diseño {nombre}" --idioma es --enfoque {enf} --ejecutivo "Carmen Olivera" --gestor "Pablo Rinaldi" --fecha 2027-01-12'), rd)
    run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto ' + " ".join(f'"{x}"' for x in tols)), rd, mostrar=False); LOG.pop()
    for c in arts:
        art(rd, c, RUTA_ART(c)); LOG.pop()
    LOG.append((f"(diseño {k} · {nombre}: {len(arts)} artefactos registrados con estado.py artefacto y {len(tols)} tolerancias de proyecto)", desc))
    run(E(f'estado.py --proyecto {G} resumen'), rd)
    e_ = json.load(open(os.path.join(rd, G, "estado.json"), encoding="utf-8"))
    medidas.append((nombre, len(e_["artefactos"]), sum(1 for x in e_["artefactos"] if x.startswith("enfoque-")), etapas,
                    sum(1 for v in e_["tolerancias"]["proyecto"].values() if v), e_["enfoque_entrega"]))
LOG.append(("(bloque C: medidas leídas de los tres estado.json)", "diseño                       artefactos  enfoques  etapas  tolerancias  enfoque de entrega\n" +
            "\n".join(f"{m[0]:28s} {m[1]:>10} {m[2]:>9} {m[3]:>7} {m[4]:>12}  {m[5]}" for m in medidas)))
ETQ = ["Artefactos de gestión", "Enfoques de gestión", "Etapas de gestión", "Tolerancias de proyecto fijadas"]
V.barras_comparadas(ETQ, [[m[1], m[2], m[3], m[4]] for m in medidas], os.path.join(OUT, "g5-tres-disenos.png"),
                    f"El regulado pide {medidas[1][1]} artefactos y {medidas[1][4]} tolerancias; el pequeño, {medidas[0][1]} y {medidas[0][4]}",
                    subtitulo=f"Mismo proyecto de turnos en línea · el ágil ({medidas[2][1]} artefactos) aligera documentos, no puertas · datos de cada estado.json",
                    fuente="estado.json de los tres diseños (nuevo_proyecto.py, estado.py tolerancia y artefacto)", nombres=[m[0] for m in medidas])

P("Paso 13 · PID con adaptación, sanidad y puerta autorizar-proyecto: P-11 y su resolución")
doc(repo, "pid", "00-direccion/pid.md", f"""# PID · Turnos en línea · Policlínicas Altamar (v0.9)
§1–§6: definición, enfoque híbrido, business case v0.9, estructura (ejecutiva Carmen Olivera; usuaria sénior Inés Ferrer;
proveedor sénior Tomás Aguirre; aseguramiento Valeria Santos), enfoques de una página.
## 7. Controles
Etapas: 1 iniciación · 2 recordatorios · 3 turnos en línea. Tolerancias de proyecto: tiempo ±4 semanas, costo ±10 %,
alcance Must sin tolerancia, beneficios −15 %. Presupuesto autorizado {usd(autorizado)} (BAC {usd(bac)} + reserva de gestión {usd(gest)});
presupuesto de cambio {usd(CAMBIO)} con tope de {usd(LIM)} por cambio. Highlight quincenal; sanidad en cada highlight.
## 8. Adaptación (tailoring)
| Qué | Cómo se adaptó | Por qué |
|---|---|---|
| Ciclo de vida | etapas PRINCE2; sprints de 14 días como paquetes de trabajo en las etapas 2 y 3 | entregables con vías distintas (paso 5) |
| Enfoques | una página cada uno; datos digitales dentro de calidad | proyecto mediano, un solo equipo |
| Plan de proyecto | dentro del PID (roadmap + WBS + presupuesto) | evitar duplicar |
| Roles | Inés Ferrer: usuaria sénior, product owner y autoridad de cambio | una sola voz del negocio |
| Validación | supuestos críticos con experimento, criterio y fecha (supuestos.csv); SUP-01…03 y P-11 | idea con incertidumbre alta |
| Puerta de la etapa 3 | condicionada a la adopción medida en el release 1 | VAN sensible a la adopción |
""", version="0.9", origen="pm-acta-constitucion, templates/pid.md (§8 adaptación)")
art(repo, "plan-proyecto", "00-direccion/pid.md"); LOG.pop()
art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md", texto="# Plan de la etapa 2 · Release 1: recordatorios\n\nREQ-001…003 en 6 policlínicas; sprints de 14 días; medición de ausentismo y adopción.\n"); LOG.pop()
sanidad(repo, "2027-01-14")
run(E(f'puertas.py --proyecto {G} verificar autorizar-proyecto'), repo, ok=(0, 1, 2))
act(repo, "supuestos", S[2], validado="si", estado="validado", certeza="alta", fecha_validacion="2027-01-14", evidencia="prueba técnica: 50 de 50 reservas y cancelaciones sin intervención; respuesta media 1,4 s")
D_ACEPTA = regs(repo, "decisiones", fecha="2027-01-15", decision=f"La junta acepta {S[5]} sin validar: invierte sin el dictamen legal y cubre su efecto con el riesgo {RID[2]} y su contingencia; el dictamen sigue como experimento y es condición antes del release de recordatorios",
                decidido_por=EJ, nivel="junta", revisar_en="2027-01-29", artefactos_afectados="03-control/registros/supuestos.csv; 03-control/registros/riesgos.csv")
act(repo, "supuestos", S[5], notas=f"aceptado sin validar por la junta el 2027-01-15 ({D_ACEPTA}); efecto cubierto por {RID[2]}; el dictamen del 2027-01-29 lo valida o lo invalida")
puerta_f(repo, "autorizar-proyecto", EJ, "2027-01-15")
for c in ("business-case", "enfoque-beneficios", "pid", "presupuesto", "descripcion-producto-proyecto", "enfoque-riesgo", "enfoque-calidad", "enfoque-issues-cambios", "enfoque-comunicacion"):
    run(E(f'estado.py --proyecto {G} aprobar {c} --por "{EJ}" --version 1.0 --fecha 2027-01-15'), repo, mostrar=False)
LOG.append(("(pm-director aprueba con estado.py aprobar … --version 1.0 --fecha 2027-01-15: business case, enfoque de beneficios, PID, presupuesto, descripción del producto y los 4 enfoques)", "9 copias congeladas en 00-direccion/historial/ (…-v1.0.md)"))
# D-003 pide revisar el enfoque en cada puerta de etapa: la junta lo revisa con la prueba técnica hecha y la decisión
# nueva reemplaza a la anterior (registro.py valida nivel igual o superior); decision.py vigentes muestra la cadena
D_ENF2 = regs(repo, "decisiones", fecha="2027-01-15", decision=f"Enfoque de entrega revisado en la puerta autorizar-proyecto: se mantiene híbrido; la integración con la agenda clínica pasa a predictiva con alcance fijo ({S[2]} validado el 2027-01-14) y recordatorios y turnos en línea siguen en sprints de 14 días; la puerta de la etapa 3 queda condicionada a la adopción medida en el release 1",
              decidido_por=EJ, nivel="junta", revisar_en="cada puerta de etapa", reemplaza=D_ENF, artefactos_afectados="00-direccion/pid.md")
run(f'{DEC} vigentes --tema "enfoque de entrega" --corte 2027-01-15', repo)
run(f'{DEC} vigentes --tema "delivery approach" --corte 2027-01-15', repo)    # la búsqueda normalizada (texto.py) entiende inglés
run(E(f'estado.py --proyecto {G} resumen'), repo)
sanidad(repo, "2027-01-15")

P("Paso 14 · Tablero de una página y seguimiento después de la puerta")
sup_f = csv_filas(repo, "03-control/registros/supuestos.csv")
criticos = [f for f in sup_f if f["criticidad"] == "alta"]
val = [f["id"] for f in criticos if f["validado"] == "si"]; inv = [f["id"] for f in criticos if f["validado"] == "no"]
vj = verificar_json(repo, "autorizar-proyecto")
p11 = [h for h in vj["hallazgos"] if h["id"] == "P-11"]
acep = re.findall(r"(S-\d{3}) \((D-\d{3})\)", " ".join(h["mensaje"] for h in p11 if h["severidad"] == "aviso"))
LOG.append(("(puertas.py verificar autorizar-proyecto --json → hallazgos con id P-11)", "\n".join(f"{h['severidad']} {h['id']} {h['mensaje']}" for h in p11)))
e_ = json.load(open(os.path.join(repo, G, "estado.json"), encoding="utf-8"))
ult = e_["puertas"][-1]
LOG.append(("(insumos del tablero: supuestos.csv, estado.json, la verificación con --json y los cálculos de los pasos 5 y 9)",
            f"supuestos críticos {len(criticos)}: validados {', '.join(val)} · invalidado y ajustado {', '.join(inv)} · aceptados por la junta {', '.join(f'{a} ({b})' for a, b in acep)} · "
            f"puerta {ult['tipo']} {ult['decision']} {ult['fecha']} · VAN {usd(van_final)} · TIR {pct(tir_final)} % · repago {V.miles(rep_final, 2)} · autorizado {usd(autorizado)}"))
V.tarjetas([(f"USD {usd(van_final)}", "VAN a 5 años de la opción 2", f"TIR {pct(tir_final)} % · repago {V.miles(rep_final, 2)} años · inversión {usd(inv_final)}", "bien"),
            (f"{len(criticos)} de {len(criticos)}", "supuestos críticos tratados", f"{len(val)} validados · {len(inv)} ajustado · {len(acep)} aceptado ({', '.join(b for _, b in acep)})", "bien"),
            (f"USD {usd(autorizado)}", "presupuesto autorizado", f"BAC {usd(bac)} + reserva de gestión {usd(gest)}; cambio {usd(CAMBIO)} aparte", None),
            ("Híbrido", "enfoque de entrega", "integración " + str(sum(PUNT["Integración con la agenda clínica"])) + " · recordatorios " + str(sum(PUNT["Recordatorios y confirmación"])) + " · portal " + str(sum(PUNT["Turnos en línea (portal y app)"])) + " (de 9 a 27)", None),
            ("±10 %", "tolerancia de costo del proyecto", "tiempo ±4 semanas · beneficios −15 % · Must sin tolerancia", None),
            (ult["decision"], f"puerta {ult['tipo']}", f"{ult['fecha']} · P-11 en aviso: " + ", ".join(f"{a} aceptado ({b})" for a, b in acep), "bien")],
           os.path.join(OUT, "g5-tablero.png"), f"Proyecto autorizado el {ult['fecha']}: ningún supuesto crítico sin tratar",
           subtitulo="Turnos en línea · Policlínicas Altamar (ficticia) · de la idea (2026-11-02) al proyecto diseñado",
           fuente="supuestos.csv · estado.json · puertas.py verificar --json · inversion.py y puntuación del paso 5 (salida-g5.md)")
# los mapas del paso 5b, con los vínculos de los pasos 6 y 9, en su tablero gráfico (SVG propio, sin mmdc)
run(f'{MAPAS} --proyecto {G} tablero', repo)
captura_html(os.path.join(repo, G, "02-planificacion", "visuales", "tablero-mapas.html"), os.path.join(OUT, "g5-tablero-mapas.png"), ancho=1600)
captura_seccion(os.path.join(repo, G, "02-planificacion", "visuales", "tablero-mapas.html"), os.path.join(OUT, "g5-tablero-mapas-169.png"), "main", ancho=1600, alto=900, escala=1.25)
# aceptar no es olvidar: al 2027-02-01, sin dictamen y sin revisar los riesgos, la sanidad lo detecta y el radar dice qué
# decidir, escalar, desbloquear y vigilar, con responsable y siguiente paso
sanidad(repo, "2027-02-01")
run(f'{DEC} vigentes --ids {S[5]} --corte 2027-02-01', repo)
run(E(f'estado.py --proyecto {G} radar --corte 2027-02-01'), repo)

# ===================================================================================== variante a) con BMAD
P("Paso 15 · Variante a) con BMAD: supuestos, preguntas y requisitos desde los artefactos de descubrimiento")
ra = proyecto("portal-socios")
run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez" --fecha 2026-10-27'), ra)
run(f'python3 {BMAD} --proyecto {G} detectar', ra, mostrar=False); LOG.pop()
run(f'python3 {BMAD} --proyecto {G} inventario', ra); limpiar()
run(f'python3 {BMAD} --proyecto {G} requisitos', ra)
run(E(f'especificacion.py --proyecto {G} fuente'), ra)
run(E(f'especificacion.py --proyecto {G} resumen'), ra)
run(f'python3 {RAIZ}/skills/pm-riesgos/scripts/riesgos.py --proyecto {G} candidatos --fuentes bmad --fecha 2026-10-28', ra, corte=12)
cj = json.loads(subprocess.run(["python3", f"{RAIZ}/skills/pm-riesgos/scripts/riesgos.py", "--proyecto", G, "candidatos", "--fuentes", "bmad", "--fecha", "2026-10-28", "--json"],
                               cwd=ra, capture_output=True, text=True).stdout)
from collections import Counter
cl = Counter(c.get("clase") for c in cj["candidatos"])
LOG.append(("(candidatos por clase, de riesgos.py candidatos --json)", " · ".join(f"{k}: {v}" for k, v in sorted(cl.items())) + f" · total {sum(cl.values())}"))
SA = []
for txt, cat, origen in (("Hay métricas actuales del volumen de consultas y del costo por gestión para fijar la línea base", "viabilidad", "brief.md:26 (CR-01)"),
                         ("El núcleo operativo ofrece una API o base de lectura utilizable para saldos y préstamos", "factibilidad", "prd.md:64 y prd.md:258"),
                         ("El método de autenticación elegido no frena la adopción de los socios", "deseabilidad", "prd.md:249 (pregunta abierta 1)")):
    SA.append(reg(ra, "supuestos", fecha="2026-10-28", autor="Martín Suárez", supuesto_o_restriccion=txt, tipo="supuesto", categoria=cat, criticidad="alta", certeza="baja",
                  validado="pendiente", responsable="Martín Suárez", notas=f"origen: BMAD {origen} (riesgos.py candidatos)"))

P("Paso 16 · Variante a) con BMAD: qué controles detectan los vacíos")
sanidad(ra, "2026-10-28")
run(E(f'puertas.py --proyecto {G} verificar autorizar-proyecto'), ra, ok=(0, 1, 2))

P("Paso 16b · Variante a) con BMAD: personas de usuario desde los recorridos UJ y capacidad × persona")
run(f'python3 {IN} --proyecto {G} personas candidatos --desde bmad', ra)
# Martín Suárez confirma las tres candidatas, completa los dolores con el texto del PRD y mapea los dos FR que ningún recorrido
# realiza: FR-8 lo usan Diego (el UJ-2 parte «con contacto verificado») y Lucía (aprueba el cambio de domicilio, prd.md:158);
# FR-12 avisa a Diego; Lucía, que hoy transcribe pedidos de varios canales, es quien pide la bandeja única (FR-9)
DOL_A = {"Marta": "Evita los trámites digitales complejos; necesita la constancia para un trámite bancario",
         "Diego": "No sabe en qué estado está su solicitud de préstamo", "Lucía": "Transcribe pedidos que llegan por varios canales"}
EXTRA_A = {"Diego": {"usa": ["FR-8"], "beneficia": ["FR-12"]}, "Lucía": {"usa": ["FR-8"], "solicita": ["FR-9"]}}
PUA = {}
for c in personas_json(ra, "candidatos", "--desde", "bmad"):
    campos = {k_: c[k_] for k_ in ("nombre", "descripcion", "objetivo", "contexto_uso", "fuente", "evidencia", "usa") if c[k_]}
    campos["dolores"] = DOL_A[c["nombre"]]
    for k_, v_ in EXTRA_A.get(c["nombre"], {}).items():
        campos[k_] = ";".join(sorted([x for x in (campos.get(k_) or "").split(";") if x] + v_, key=lambda x: int(x.split("-")[1])))
    PUA[c["nombre"]] = reg(ra, "personas", **campos)
run(f'python3 {IN} --proyecto {G} personas mapa --limite 0', ra)
run(f'python3 {IN} --proyecto {G} personas priorizacion', ra)
mpa, ppa = personas_json(ra, "mapa"), personas_json(ra, "priorizacion")
usos = {p_["id"]: sum(1 for c in mpa["capacidades"] if p_["id"] in c["personas"]) for p_ in mpa["personas"]}
matriz_personas(mpa, ppa, os.path.join(OUT, "g5-personas-mapa-bmad.png"),
                f"Los {len(mpa['capacidades'])} FR del PRD tienen persona: " + ", ".join(f"{p_['nombre']} {usos[p_['id']]}" for p_ in mpa["personas"]),
                subtitulo="Portal de socios · personas desde los recorridos UJ-1…3 del PRD · el PRD no prioriza: MoSCoW llega con el backlog (E2E-4)",
                fuente="interesados.py personas candidatos --desde bmad, mapa y priorizacion --json · personas.csv · prd.md (solo lectura)")

P("Paso 17 · Variante a) con BMAD: recorrido y mapa de valor desde la especificación")
run(f'python3 {BMAD} --proyecto {G} recorridos --id UJ-2', ra)
run(f'{MAPAS} --proyecto {G} recorrido semilla --uj UJ-2 --backstage UJ-3 --persona {PUA["Diego"]} --fecha 2026-10-29', ra)
EMO_A = {  # paso: (emoción, fuente, dolor, causa, oportunidad, kano, refs, frontstage, backstage, soporte)
    "P1": (1, "supuesto declarado: PRD §2.1, «quiero pedir un préstamo pequeño y saber en qué estado está»", "", "", "", "", ["FR-6"], "Formulario guiado", "", ""),
    "P2": (0, "supuesto declarado: formulario con límites por producto (pregunta abierta 3)", "", "", "", "", ["FR-6"], "Validación de límites", "", ""),
    "P3": (0, "supuesto declarado", "", "", "", "", [], "Resumen antes de enviar", "", ""),
    "P4": (1, "supuesto declarado", "", "", "", "", ["FR-6"], "", "La solicitud entra a la bandeja como «Recibida» (FR-9)", ""),
    "P5": (2, "supuesto declarado: clímax del recorrido UJ-2", "", "", "", "", ["FR-12"], "Correo de confirmación", "", "Outbox de notificaciones (AD-7)"),
    "P6": (-1, "", "No sabe cuánto falta para la respuesta", "propuesta-valor", "Mostrar el plazo de respuesta comprometido (48 h, SM-3)", "atractivo", [], "Estado «En revisión»", "Lucía toma la solicitud y revisa los datos (UJ-3)", ""),
    "P7": (-1, "supuesto declarado: pedido de información adicional (FR-10)", "Tiene que buscar el documento y volver a entrar", "usabilidad", "Adjuntar desde el aviso, sin buscar la solicitud", "desempeno", ["FR-7"], "Comentario visible de la operadora", "Lucía pide un documento y pasa a «Información adicional» (FR-10)", ""),
    "P8": (0, "supuesto declarado", "", "", "", "", ["FR-7"], "Adjunto en la solicitud", "", "Adjuntos con formato y tamaño validados (AD-12)"),
    "P9": (2, "supuesto declarado: resolución del recorrido UJ-2", "", "", "", "", ["FR-12"], "Correo de aprobación", "Lucía aprueba; queda en la auditoría (AD-6)", "Outbox de notificaciones (AD-7)")}
def prop_ra(d_):
    for _, p_ in [(et, p_) for et in d_["etapas"] for p_ in et["pasos"]]:
        em, fu, do, ca, op, ka, rf, fr, bk, so = EMO_A[p_["id"]]
        p_.update({"emocion": em, "fuente_emocion": fu, "dolor": do, "tipo_causa": ca, "oportunidad": op, "kano": ka, "refs": rf,
                   "punto_contacto": {"P5": "Correo", "P9": "Correo", "P7": "Correo y portal"}.get(p_["id"], "Portal"), "canal": "celular"})
        for k_, v_ in (("frontstage", fr), ("backstage", bk), ("soporte", so)):
            if v_: p_[k_] = v_
    d_["trabajo"] = "Conseguir un préstamo pequeño para una reparación y saber en qué estado está"
    d_.pop("pendiente_alinear", None)
dra = completar(ra, "recorrido-uj-2.json", prop_ra, "pm-mapas-estrategicos completa la semilla: emociones con fuente, dolores, oportunidades y el backstage de UJ-3 alineado a cada paso; Martín Suárez confirma",
                lambda d_: "\n".join(fila_r(et, p_) for et in d_["etapas"] for p_ in et["pasos"]) + f"\nKPI {', '.join(d_['kpi'])} · contrapeso {', '.join(d_['contrapesos'])}")
run(f'python3 {BMAD} --proyecto {G} capacidades', ra)
run(f'{MAPAS} --proyecto {G} wardley semilla --slug portal --titulo "Portal de socios · qué construir y qué comprar" '
    f'--pregunta "¿Qué construye el equipo, qué se compra o terceriza y dónde está la inercia?" --fecha 2026-10-29', ra)
POS_A = {  # nombre de la semilla → (nombre final, visibilidad, evolución, etapa, decisión, inercia, evidencia, refs extra)
    "Acceso y recuperación": ("Acceso y recuperación", 0.70, 0.48, "a-medida", "construir", False, "reglas propias de alta y bloqueo (AD-5); el proveedor de identidad queda detrás de IdentityPort", []),
    "Saldos y préstamos": ("Saldos y préstamos", 0.76, 0.38, "a-medida", "construir", False, "lectura del núcleo con timeout y sin caché vigente (AD-1)", []),
    "Constancias": ("Constancias", 0.85, 0.36, "a-medida", "construir", False, "PDF al vuelo con código de verificación propio (AD-8); librería estándar del stack", []),
    "Solicitudes del socio": ("Solicitudes del socio", 0.70, 0.30, "a-medida", "construir", False, "máquina de estados única de la cooperativa (AD-3); diferencia el servicio", []),
    "Consola": ("Consola de operador", 0.60, 0.26, "a-medida", "construir", False, "bandeja única con auditoría (AD-3, AD-6)", []),
    "Notificaciones": ("Notificaciones", 0.40, 0.68, "producto", "construir", False, "outbox transaccional propio (AD-7, AD-10); el envío es un servicio de mercado", []),
    "Proveedor y método de identidad": ("Identidad y segundo factor", 0.45, 0.80, "commodity", "comprar", False, "decisión diferida en la arquitectura (pregunta abierta 1); servicios de identidad de mercado", ["AD-5"]),
    "Interfaz y capacidad reales del núcleo operativo": ("Núcleo operativo", 0.28, 0.58, "producto", "", True, "sistema central en uso; su interfaz y capacidad son desconocidas (pregunta abierta 2)", ["AD-1"]),
    "Hosting, proveedor de correo/SMS y almacenamiento de adjuntos": ("Correo, SMS y hosting", 0.15, 0.88, "commodity", "tercerizar", False, "decisión diferida: depende de presupuesto y residencia de datos (preguntas 4 y 6)", ["AD-7"])}
ANCLAS_A = {"A1": ("Socio · consulta y constancias", 0.97, 0.48), "A2": ("Socio · préstamo", 0.93, 0.28), "A3": ("Operadora · bandeja", 0.88, 0.12)}
ENLACES_A = [("Acceso y recuperación", "Identidad y segundo factor"), ("Saldos y préstamos", "Núcleo operativo"), ("Constancias", "Saldos y préstamos"),
             ("Solicitudes del socio", "Notificaciones"), ("Consola de operador", "Solicitudes del socio"), ("Notificaciones", "Correo, SMS y hosting")]
def prop_wa(d_):
    quedan, nombre_id = [], {}
    for c in d_["componentes"]:
        clave = next((k_ for k_ in POS_A if c["nombre"].rstrip("…").strip() and k_.startswith(c["nombre"].rstrip("…").strip())), None)
        if not clave: continue
        n_, v_, e_, et, dec, ine, ev, extra = POS_A[clave]
        c.update({"nombre": n_, "visibilidad": v_, "evolucion": e_, "etapa": et, "decision": dec, "inercia": ine, "evidencia": ev, "refs": c["refs"] + extra})
        c.pop("sugerencia", None); quedan.append(c); nombre_id[n_] = c["id"]
    ids_q = {c["id"] for c in quedan}
    d_["componentes"] = quedan
    for a_ in d_["anclas"]:
        n_, v_, e_ = ANCLAS_A[a_["id"]]; a_.update({"nombre": n_, "visibilidad": v_, "evolucion": e_})
    d_["enlaces"] = [l for l in d_["enlaces"] if l["a"] in ids_q] + [{"de": nombre_id[a_], "a": nombre_id[b_]} for a_, b_ in ENLACES_A]
    d_["notas"] = [{"texto": "Normativa BCU y residencia de datos condicionan el hosting", "visibilidad": 0.06, "evolucion": 0.55}]
    d_.pop("insumos", None)
dwa = completar(ra, "wardley-portal.json", prop_wa, "pm-mapas-estrategicos ubica 9 de los 15 componentes de la semilla: roles y permisos queda dentro de acceso; seguridad y rendimiento son criterios de calidad, no componentes; productos y límites, normativa y observabilidad son configuración o condiciones. Martín Suárez confirma",
                lambda d_: "\n".join(fila_w(c) for c in d_["componentes"]) + f"\n{len(d_['anclas'])} anclas · {len(d_['enlaces'])} enlaces")
run(f'{MAPAS} --proyecto {G} wardley validar portal', ra)
for tipo, slug in (("recorrido", "uj-2"), ("wardley", "portal")):
    run(f'{MAPAS} --proyecto {G} {tipo} render {slug} --png no', ra)
    run(E(f'estado.py --proyecto {G} artefacto mapa-{tipo}-{slug} --ruta 02-planificacion/visuales/{tipo}-{slug}.md --estado en-revision'), ra, mostrar=False); LOG.pop()
png_mapa(ra, "wardley", "portal", os.path.join(OUT, "g5-wardley-bmad.png"))
png_mapa(ra, "recorrido", "uj-2", os.path.join(OUT, "g5-recorrido-bmad.png"))
run(f'{MAPAS} --proyecto {G} controles', ra)
run(f'{MAPAS} --proyecto {G} recorrido candidatos uj-2', ra)
SA.append(reg(ra, "supuestos", fecha="2026-10-29", autor="Martín Suárez", supuesto_o_restriccion="Mostrar el plazo de respuesta comprometido reduce las consultas de seguimiento de los socios",
              tipo="supuesto", categoria="deseabilidad", criticidad="media", certeza="baja", validado="pendiente", responsable="Sofía Ramírez",
              notas="origen: recorrido-uj-2.json#P6 (mapas.py recorrido candidatos)"))
DA = reg(ra, "decisiones", fecha="2026-10-29", decision="Notificaciones: construir el outbox propio (AD-7, AD-10) y tercerizar el envío de correo y SMS",
         contexto="mapa de valor del portal (MAP-01)", opciones_consideradas="construir todo; comprar una plataforma de notificaciones; outbox propio con envío tercerizado",
         decidido_por="Gestor: Martín Suárez", nivel="gestor")
RA = reg(ra, "riesgos", fecha_identificacion="2026-10-29", autor="Martín Suárez", categoria="tecnico",
         causa="El núcleo operativo es un sistema central con interfaz y capacidad desconocidas (pregunta abierta 2, AD-1)",
         evento="El adaptador del núcleo se atrasa o no cumple la latencia de NFR-3", efecto="Atraso de las consultas de saldos, préstamos y constancias (FR-3, FR-4, FR-5)",
         tipo="amenaza", probabilidad=3, impacto=4, proximidad="corto-plazo", respuesta="reducir",
         acciones="prueba técnica de lectura con el entorno de pruebas del núcleo antes de estimar", propietario="Martín Suárez", fecha_revision="2026-11-15")
def nombre_c(r_, nombre):
    return next(c["id"] for c in json.load(open(RMAP(r_, "wardley-portal.json"), encoding="utf-8"))["componentes"] if c["nombre"] == nombre)
for mapa, elem, ref in (("uj-2", "P6", SA[-1]), ("portal", nombre_c(ra, "Notificaciones"), DA), ("portal", nombre_c(ra, "Núcleo operativo"), RA)):
    run(f'{MAPAS} --proyecto {G} vincular {mapa} {elem} --refs {ref}', ra)
def fuente_p6(d_):
    for et in d_["etapas"]:
        for p_ in et["pasos"]:
            if p_["id"] == "P6": p_["fuente_emocion"] = "supuesto declarado: el PRD no informa plazos al socio (FR-7)"
completar(ra, "recorrido-uj-2.json", fuente_p6, "la persona declara la fuente de la emoción del paso P6", lambda d_: "P6: supuesto declarado: el PRD no informa plazos al socio (FR-7)")
for tipo, slug in (("recorrido", "uj-2"), ("wardley", "portal")):
    run(f'{MAPAS} --proyecto {G} {tipo} render {slug} --png no', ra, mostrar=False); LOG.pop()
run(f'{MAPAS} --proyecto {G} controles', ra)
run(f'{MAPAS} --proyecto {G} tablero', ra)
captura_html(os.path.join(ra, G, "02-planificacion", "visuales", "tablero-mapas.html"), os.path.join(OUT, "g5-tablero-mapas-bmad.png"), ancho=1600)

with open(sys.argv[1] if len(sys.argv) > 1 else "salida-g5.md", "w", encoding="utf-8") as f:
    for c, o in LOG:
        f.write((c + "\n" if c.startswith("## ") else f"```\n$ {c}\n{o}\n```\n\n"))
print("Carpeta del recorrido:", repo)
