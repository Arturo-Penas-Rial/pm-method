"""Presentaciones light para IEEE · prepara los datos de las dos presentaciones.

Uso: python3 preparar.py   (lee contenido-resumen.json y contenido-informe.json; escribe datos-resumen.json y
datos-informe.json, que leen build_pptx.js y build_html.py)

Ninguna cifra se escribe a mano:
- el programa de formación se calcula desde los módulos de contenido-resumen.json (sesiones × minutos) y se verifica
  contra el material real del webinar (docs/webinar/E2E-N/diapositivas.json: clases y duracion_min de cada caso);
- la versión sale de .claude-plugin/plugin.json y la línea de calidad, de la tabla de evidencia del README.
Un marcador {clave} desconocido, una imagen inexistente o una diferencia con el webinar detienen la preparación.
"""
import json, pathlib, re, sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]


def fallar(msg):
    sys.exit(f"preparar.py: {msg}")


def miles(n):
    return f"{n:,}".replace(",", ".")


def horas(minutos):
    h = minutos / 60
    return str(int(h)) if h == int(h) else f"{h:.1f}".replace(".", ",")


version = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
readme = (RAIZ / "README.md").read_text(encoding="utf-8")
m_fecha = re.search(r"\| Evidencia \((\d{4}-\d{2}-\d{2})\) \|", readme)
m_reg = re.search(r"\| Pruebas de regresión \(`probar_paquete\.py`\) \| (\d+) OK · 0 FALLO", readme)
m_e2e = re.search(r"\| Recorridos E2E de las guías \(`guias_e2e/correr\.py`\) \| (\d+)/(\d+) OK", readme)
if not (m_fecha and m_reg and m_e2e):
    fallar("no encuentro la tabla de evidencia del README (fecha, regresión o recorridos E2E)")
if m_e2e.group(1) != m_e2e.group(2):
    fallar("los recorridos E2E del README no están todos OK")

R = json.loads((AQUI / "contenido-resumen.json").read_text(encoding="utf-8"))
I = json.loads((AQUI / "contenido-informe.json").read_text(encoding="utf-8"))
P = R["programa"]
MIN = P["minutos_sesion"]
mods = {m["id"]: m for m in P["modulos"]}

# ---------- verificación contra el material real del webinar
web_clases = web_min = 0
for m in P["modulos"]:
    if "caso" not in m:
        if m["material"] == "existente":
            fallar(f"{m['id']}: material existente sin caso del webinar")
        continue
    f = RAIZ / "docs/webinar" / m["caso"] / "diapositivas.json"
    if not f.exists():
        fallar(f"{m['id']}: no existe {f.relative_to(RAIZ)}")
    w = json.loads(f.read_text(encoding="utf-8"))
    durs = [c["duracion_min"] for c in w["clases"]]
    if len(durs) != m["sesiones"] or any(d != MIN for d in durs):
        fallar(f"{m['id']} ({m['caso']}): el webinar tiene {len(durs)} clases de {durs} min; el programa dice "
               f"{m['sesiones']} sesiones de {MIN} min")
    web_clases += len(durs)
    web_min += sum(durs)
total_casos = len(list((RAIZ / "docs/webinar").glob("E2E-*/diapositivas.json")))
if total_casos != sum(1 for m in P["modulos"] if "caso" in m):
    fallar(f"el webinar tiene {total_casos} casos y el programa usa {sum(1 for m in P['modulos'] if 'caso' in m)}")

ses_total = sum(m["sesiones"] for m in P["modulos"])
min_total = ses_total * MIN
nuevas = sum(m["sesiones"] for m in P["modulos"] if m["material"] != "existente")
assert ses_total * MIN == web_min + nuevas * MIN, "la suma de minutos no coincide"

piloto_base = sum(mods[i]["sesiones"] for i in P["piloto"]["base"])
piloto_max = piloto_base + sum(mods[i]["sesiones"] for i in P["piloto"]["extension"])

# pasos del piloto con su rango de sesiones
pasos, k = [], 1
for i in P["piloto"]["base"] + P["piloto"]["extension"]:
    m = mods[i]
    rango = f"{k}–{k + m['sesiones'] - 1}" if m["sesiones"] > 1 else str(k)
    nombre = m["nombre"] if "caso" not in m else f"Taller: {m['nombre']}"
    pasos.append({"sesiones": f"Sesiones {rango}", "nombre": nombre, "opcional": i in P["piloto"]["extension"],
                  "detalle": m.get("detalle") or f"{m['lema']} · caso {m['caso']}"})
    k += m["sesiones"]


def ritmo(n):
    return [["1 sesión por semana", f"{n} semanas"], ["2 sesiones por semana", f"{-(-n // 2)} semanas"]]


calc_piloto = [
    {"rot": f"Piloto base ({piloto_base} sesiones)",
     "cuenta": f"{piloto_base} × {MIN} min = {miles(piloto_base * MIN)} min = {horas(piloto_base * MIN)} h",
     "ritmo": f"{piloto_base} semanas a 1 por semana · {-(-piloto_base // 2)} a 2 por semana"},
    {"rot": f"Piloto ampliado ({piloto_max} sesiones)",
     "cuenta": f"{piloto_max} × {MIN} min = {miles(piloto_max * MIN)} min = {horas(piloto_max * MIN)} h",
     "ritmo": f"{piloto_max} semanas a 1 por semana · {-(-piloto_max // 2)} a 2 por semana"}]

V = {
    "version": version, "minutos_sesion": MIN,
    "sesiones_total": ses_total, "min_total_txt": miles(min_total), "horas_total": horas(min_total),
    "webinar_clases": web_clases, "webinar_horas": horas(web_min),
    "nuevas_sesiones": nuevas, "nuevas_horas": horas(nuevas * MIN),
    "piloto_min": piloto_base, "piloto_max": piloto_max,
    "regresion_ok": m_reg.group(1), "e2e_ok": m_e2e.group(1), "evidencia_fecha": m_fecha.group(1),
}
# cálculo explícito: introducción + talleres × sesiones + integrador
intro = [m for m in P["modulos"] if m["id"] == "M0"][0]["sesiones"]
talleres = [m for m in P["modulos"] if "caso" in m]
integ = [m for m in P["modulos"] if m["id"] == "TI"][0]["sesiones"]
if len({m["sesiones"] for m in talleres}) != 1:
    fallar("los talleres no tienen todos la misma cantidad de sesiones")
V["talleres_n"] = len(talleres)
V["calculo_sesiones"] = f"{intro} + {len(talleres)} × {talleres[0]['sesiones']} + {integ} = {ses_total}"
if intro + len(talleres) * talleres[0]["sesiones"] + integ != ses_total:
    fallar("el cálculo explícito no coincide con la suma de módulos")


def completar(o):
    if isinstance(o, str):
        def rep(mm):
            if mm.group(1) not in V:
                fallar(f"marcador desconocido {{{mm.group(1)}}}")
            return str(V[mm.group(1)])
        return re.sub(r"\{([a-z0-9_]+)\}", rep, o)
    if isinstance(o, list):
        return [completar(x) for x in o]
    if isinstance(o, dict):
        return {k: completar(v) for k, v in o.items()}
    return o


def imagenes(doc):
    for d in doc["diapositivas"]:
        if "imagen" in d and not (RAIZ / d["imagen"]).exists():
            fallar(f"imagen inexistente: {d['imagen']}")


for nombre, doc in (("resumen", R), ("informe", I)):
    imagenes(doc)
    out = completar(doc)
    out["valores"] = V
    out["meta"]["version"] = version
    out["programa"] = completar(P)
    out["programa"]["ritmo_total"] = ritmo(ses_total)
    out["programa"]["pasos_piloto"] = pasos
    out["programa"]["calculo_piloto"] = calc_piloto
    out["casos"] = [{"caso": m["caso"], "nombre": m["nombre"], "lema": m["lema"]} for m in talleres]
    (AQUI / f"datos-{nombre}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print(f"programa: {V['calculo_sesiones']} sesiones · {ses_total} × {MIN} min = {V['min_total_txt']} min = {V['horas_total']} h "
      f"· webinar real {web_clases} clases = {V['webinar_horas']} h + {nuevas} sesiones nuevas = {V['nuevas_horas']} h")
print(f"ritmo: {ritmo(ses_total)} · piloto {piloto_base}–{piloto_max} sesiones")
print(f"calidad: {V['regresion_ok']} pruebas · {V['e2e_ok']} recorridos · {V['evidencia_fecha']} · versión {version}")
