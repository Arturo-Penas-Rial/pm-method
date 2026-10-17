#!/usr/bin/env python3
"""EDT/WBS desde CSV: validación, consolidación de esfuerzo y costo por nivel, diagrama Mermaid y esqueleto de diccionario.
WBS from CSV: validation, effort/cost roll-up, Mermaid tree and dictionary skeleton.

CSV (cabecera): codigo,nombre,tipo,responsable,esfuerzo_h,costo[,ref]
  - codigo: 1, 1.2, 1.2.3 … (el padre de 1.2.3 es 1.2; el nivel 0 es el proyecto, implícito)
  - tipo: producto | paquete | hito   (los paquetes y los hitos son hojas; la regla del 100 % se aplica sobre las hojas)
  - esfuerzo_h y costo solo en las hojas; los niveles superiores se consolidan
  - ref (opcional): ids de requisitos o historias (FR-3; 1-2-login) para trazabilidad con el PRD
Uso / Usage:
  python3 wbs.py 02-planificacion/wbs.csv [--titulo "Proyecto"] [--mermaid 02-planificacion/visuales/wbs.md]
                 [--diccionario 02-planificacion/diccionario-wbs-esqueleto.md] [--json] [--profundidad 3]
"""
IDIOMA = 'es'
import argparse, csv, json, sys, re

def clave(c): return [int(x) if x.isdigit() else x for x in c.split(".")]

def cargar(p):
    filas = list(csv.DictReader(open(p, encoding="utf-8")))
    nodos, errores, avisos = {}, [], []
    for r in filas:
        c = (r.get("codigo") or "").strip()
        if not c: errores.append("fila sin código"); continue
        if not re.match(r"^\d+(\.\d+)*$", c): errores.append(f"código inválido: {c}")
        if c in nodos: errores.append(f"código duplicado: {c}")
        def num(k):
            v = (r.get(k) or "").strip().replace(",", ".")
            try: return float(v) if v else 0.0
            except ValueError: errores.append(f"{c}: {k} no numérico ({v})"); return 0.0
        nodos[c] = {"codigo": c, "nombre": (r.get("nombre") or "").strip(), "tipo": (r.get("tipo") or "").strip() or "producto",
                    "responsable": (r.get("responsable") or "").strip(), "esfuerzo_h": num("esfuerzo_h"), "costo": num("costo"),
                    "ref": (r.get("ref") or "").strip(), "hijos": []}
    for c, n in nodos.items():
        if "." in c:
            padre = c.rsplit(".", 1)[0]
            if padre not in nodos: errores.append(f"{c}: falta el padre {padre}")
            else: nodos[padre]["hijos"].append(c)
    for c, n in nodos.items():
        n["hijos"].sort(key=clave)
        if n["hijos"] and (n["esfuerzo_h"] or n["costo"]):
            avisos.append(f"{c}: tiene hijos y valores propios; se ignoran y se consolida desde las hojas (regla del 100 %)")
        if not n["hijos"] and n["tipo"] == "producto":
            avisos.append(f"{c}: hoja de tipo producto; descomponer en paquetes o marcarla como paquete")
        if not n["hijos"] and n["tipo"] == "paquete" and not n["responsable"]:
            avisos.append(f"{c}: paquete sin responsable")
    return nodos, errores, avisos

def consolidar(nodos, c):
    n = nodos[c]
    if n["hijos"]:
        n["esfuerzo_tot"] = sum(consolidar(nodos, h)[0] for h in n["hijos"])
        n["costo_tot"] = sum(nodos[h]["costo_tot"] for h in n["hijos"])
    else:
        n["esfuerzo_tot"], n["costo_tot"] = n["esfuerzo_h"], n["costo"]
    return n["esfuerzo_tot"], n["costo_tot"]

def mermaid(nodos, raices, titulo, prof):
    L = ["```mermaid", "flowchart TD", f'    P0["{titulo}"]']
    def nid(c): return "N" + c.replace(".", "_")
    def lab(n):
        t = n["nombre"].replace('"', "'")
        extra = f"<br/>{n['responsable']}" if n["responsable"] and not n["hijos"] else ""
        cifras = f"<br/>{n['esfuerzo_tot']:g} h · {n['costo_tot']:,.0f}" if (n["esfuerzo_tot"] or n["costo_tot"]) else ""
        return f'{n["codigo"]} {t}{extra}{cifras}'
    def rec(c, padre, nivel):
        if nivel > prof: return
        n = nodos[c]
        forma = ('(["', '"])') if n["tipo"] == "hito" else (('["', '"]') if n["hijos"] else ('("', '")'))
        L.append(f'    {nid(c)}{forma[0]}{lab(n)}{forma[1]}')
        L.append(f"    {padre} --> {nid(c)}")
        for h in n["hijos"]: rec(h, nid(c), nivel + 1)
    for r in raices: rec(r, "P0", 1)
    L.append("```")
    return "\n".join(L) + "\n"

def diccionario(nodos):
    L = ["---", "tipo: diccionario-wbs", f'idioma: {IDIOMA}', "estado: borrador", "---", "",
         "# Diccionario de la EDT/WBS (esqueleto generado) · WBS dictionary skeleton", "",
         "> Generado por wbs.py desde wbs.csv. Completar cada paquete con la plantilla de pm-planificacion-por-productos. Borrador.", ""]
    for c in sorted(nodos, key=clave):
        n = nodos[c]
        if n["hijos"]: continue
        L += [f"## {c} · {n['nombre']}", "", f"- **Tipo / Type:** {n['tipo']}", f"- **Responsable / Owner:** {n['responsable'] or '[por confirmar]'}",
              f"- **Esfuerzo / Effort (h):** {n['esfuerzo_h']:g}", f"- **Costo / Cost:** {n['costo']:,.0f}",
              f"- **Requisitos o historias / Refs:** {n['ref'] or '[por confirmar]'}",
              "- **Descripción del trabajo / Work description:** [por confirmar]", "- **Criterios de aceptación / Acceptance criteria:** [por confirmar]",
              "- **Supuestos y riesgos / Assumptions and risks:** [por confirmar]", ""]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--titulo", default="Proyecto"); ap.add_argument("--mermaid"); ap.add_argument("--diccionario")
    ap.add_argument("--json", action="store_true"); ap.add_argument("--profundidad", type=int, default=9)
    ap.add_argument("--idioma", choices=["es", "en"], default="es")
    a = ap.parse_args()
    global IDIOMA; IDIOMA = a.idioma
    nodos, errores, avisos = cargar(a.csv)
    if errores: sys.exit("Errores en la WBS:\n  - " + "\n  - ".join(errores))
    raices = sorted([c for c in nodos if "." not in c], key=clave)
    tot_h = sum(consolidar(nodos, r)[0] for r in raices); tot_c = sum(nodos[r]["costo_tot"] for r in raices)
    hojas = [c for c in nodos if not nodos[c]["hijos"]]
    if a.json:
        print(json.dumps({"total_esfuerzo_h": tot_h, "total_costo": tot_c, "hojas": len(hojas), "avisos": avisos,
                          "nodos": [{k: v for k, v in nodos[c].items() if k != "hijos"} for c in sorted(nodos, key=clave)]}, ensure_ascii=False, indent=2))
    else:
        print(f"{a.titulo}: {len(nodos)} elementos, {len(hojas)} hojas · esfuerzo {tot_h:g} h · costo {tot_c:,.0f}")
        for c in sorted(nodos, key=clave):
            n = nodos[c]; print(f"{'  ' * (c.count('.'))}{c} {n['nombre']} [{n['tipo']}] {n['esfuerzo_tot']:g} h · {n['costo_tot']:,.0f}{' · ' + n['responsable'] if n['responsable'] else ''}")
        for w in avisos: print("AVISO", w)
    if a.mermaid:
        open(a.mermaid, "w", encoding="utf-8").write(mermaid(nodos, raices, a.titulo, a.profundidad)); print(f"Mermaid escrito en {a.mermaid}")
    if a.diccionario:
        open(a.diccionario, "w", encoding="utf-8").write(diccionario(nodos)); print(f"Diccionario escrito en {a.diccionario}")

if __name__ == "__main__":
    main()
