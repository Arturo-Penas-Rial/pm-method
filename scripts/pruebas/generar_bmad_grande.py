#!/usr/bin/env python3
"""Genera un repositorio BMAD 6.12 sintético GRANDE para pruebas de escala, con el mismo formato que el fixture real
(scripts/pruebas/fixtures/bmad-v6.12-real): PRD con FR-n/NFR-n/SM-n, epics.md con mapa de cobertura por épica e
historias "As a / I want / So that", sprint-status.yaml con claves N-M-slug.

Uso: python3 generar_bmad_grande.py <destino> [--epicas 25] [--historias 6] [--fr 300] [--nfr 40]
"""
import argparse, os, random, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
REAL = os.path.join(AQUI, "fixtures", "bmad-v6.12-real")
ESTADOS = ["done"] * 3 + ["review", "in-progress", "ready-for-dev"] + ["backlog"] * 6

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("destino"); ap.add_argument("--epicas", type=int, default=25)
    ap.add_argument("--historias", type=int, default=6); ap.add_argument("--fr", type=int, default=300); ap.add_argument("--nfr", type=int, default=40)
    ap.add_argument("--semilla", type=int, default=7)
    a = ap.parse_args(); random.seed(a.semilla)
    if os.path.exists(a.destino): shutil.rmtree(a.destino)
    shutil.copytree(os.path.join(REAL, "_bmad"), os.path.join(a.destino, "_bmad"))
    pa = os.path.join(a.destino, "_bmad-output", "planning-artifacts"); ia = os.path.join(a.destino, "_bmad-output", "implementation-artifacts")
    prd_dir = os.path.join(pa, "prds", "prd-plataforma-2026-10-17"); os.makedirs(prd_dir); os.makedirs(ia)
    # PRD
    L = ["---", "status: final", "---", "", "# PRD · Plataforma grande (sintético)", "", "## 4. Funcionalidades", ""]
    for i in range(1, a.fr + 1):
        L += [f"#### FR-{i}: Capacidad {i}", "", f"El usuario puede realizar la operación {i} con validación y auditoría.", ""]
    L += ["## 5. Requisitos no funcionales", ""] + [f"- **NFR-{i} Atributo {i}:** umbral medible {i}." for i in range(1, a.nfr + 1)]
    L += ["", "## 7. Métricas de éxito", ""] + [f"- **SM-{i} Métrica {i}:** meta {i * 5} %. Valida FR-{i}." for i in range(1, 11)]
    open(os.path.join(prd_dir, "prd.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # épicas: cada épica cubre un bloque de FR; algunos FR quedan sin cubrir a propósito (los últimos 3)
    cubiertos = a.fr - 3; por_epica = -(-cubiertos // a.epicas)
    E = ["---", "status: final", "---", "", "# Plataforma grande - Desglose de épicas", "", "## Requirements Inventory", "", "### Functional Requirements", ""]
    E += [f"FR{i}: Capacidad {i}." for i in range(1, a.fr + 1)] + ["", "### FR Coverage Map", ""]
    rangos = {}
    for e in range(1, a.epicas + 1):
        ini = (e - 1) * por_epica + 1; fin = min(e * por_epica, cubiertos)
        rangos[e] = list(range(ini, fin + 1))
        E += [f"FR{i}: Epic {e} - Capacidad {i}" for i in rangos[e]]
    E += ["", "## Epic List", ""]
    for e in range(1, a.epicas + 1):
        E += [f"### Epic {e}: Épica {e}", f"Objetivo de la épica {e}.", f"**FRs covered:** {', '.join('FR' + str(i) for i in rangos[e])}", ""]
    S = ["generated: 10-17-2026 11:02", "last_updated: 10-17-2026 11:02", "project: plataforma", "project_key: NOKEY",
         "tracking_system: file-system", "story_location: _bmad-output/implementation-artifacts", "development_status:"]
    for e in range(1, a.epicas + 1):
        E += [f"## Epic {e}: Épica {e}", "", f"Objetivo de la épica {e}.", ""]
        estados = [random.choice(ESTADOS) for _ in range(a.historias)]
        ep = "done" if all(x == "done" for x in estados) else ("backlog" if all(x == "backlog" for x in estados) else "in-progress")
        S.append(f"  epic-{e}: {ep}")
        for h in range(1, a.historias + 1):
            E += [f"### Story {e}.{h}: Historia {e}.{h} de la épica {e}", "", "As a usuario,", f"I want la función {e}.{h},",
                  f"So that obtenga el resultado {e}.{h}.", "", "**Acceptance Criteria:**", "", "**Given** un contexto", "**When** actúo", "**Then** obtengo el resultado", ""]
            S.append(f"  {e}-{h}-historia-{e}-{h}-de-la-épica-{e}: {estados[h - 1]}")
        S.append(f"  epic-{e}-retrospective: optional")
    open(os.path.join(pa, "epics.md"), "w", encoding="utf-8").write("\n".join(E) + "\n")
    open(os.path.join(ia, "sprint-status.yaml"), "w", encoding="utf-8").write("\n".join(S) + "\n")
    print(f"BMAD grande en {a.destino}: {a.epicas} épicas, {a.epicas * a.historias} historias, {a.fr} FR ({cubiertos} cubiertos), {a.nfr} NFR, 10 SM")

if __name__ == "__main__":
    main()
