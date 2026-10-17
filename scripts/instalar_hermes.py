#!/usr/bin/env python3
"""Instala pm-method en Hermes Agent (NousResearch/hermes-agent) como skills.

Hermes lee SKILL.md igual que Claude Code, pero expande ${HERMES_SKILL_DIR} (no ${CLAUDE_SKILL_DIR}) y no tiene
${CLAUDE_PLUGIN_ROOT}, hooks ni subagentes con nombre. Este script genera una copia adaptada:
  - skills/  → <destino>/<skill>/   con ${CLAUDE_SKILL_DIR} → ${HERMES_SKILL_DIR} y ${CLAUDE_PLUGIN_ROOT} → ruta absoluta
  - agents/  → <destino>/_agentes/  (texto de persona: SOUL.md de un perfil o personalidades; no son skills)
  - hooks/   no se copian (Hermes no ejecuta hooks de Claude Code): la sanidad la hacen pm-orquestador y pm-puerta.

Uso:
  python3 scripts/instalar_hermes.py                         # → ~/.hermes/skills/pm-method/  (skills locales de Hermes)
  python3 scripts/instalar_hermes.py --destino ~/pm-hermes   # carpeta propia; luego agregarla a skills.external_dirs
  python3 scripts/instalar_hermes.py --verificar             # solo informa qué haría
Después: en Hermes, /reload-skills (o reiniciar) y `hermes skills list | grep pm-`.
Volver a correrlo tras cada actualización del repositorio (reemplaza la copia; no toca otras skills).
"""
import argparse, os, re, shutil, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--destino", default=os.path.join(os.path.expanduser("~"), ".hermes", "skills", "pm-method"))
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()
    dest = os.path.abspath(os.path.expanduser(a.destino))
    skills = sorted(d for d in os.listdir(os.path.join(RAIZ, "skills")) if os.path.isfile(os.path.join(RAIZ, "skills", d, "SKILL.md")))
    print(f"pm-method → Hermes: {len(skills)} skills y {len(os.listdir(os.path.join(RAIZ, 'agents')))} agentes en {dest}")
    if a.verificar: return
    if os.path.exists(dest):
        if not os.path.exists(os.path.join(dest, ".pm-method")):
            sys.exit(f"{dest} existe y no fue creado por este script; elegir otro --destino.")
        shutil.rmtree(dest)
    os.makedirs(dest)
    open(os.path.join(dest, ".pm-method"), "w").write("copia generada por scripts/instalar_hermes.py; se reemplaza en cada instalación\n")
    cambiados = 0
    def adaptar(txt):
        nonlocal cambiados
        nuevo = txt.replace("${CLAUDE_SKILL_DIR}", "${HERMES_SKILL_DIR}").replace("${CLAUDE_PLUGIN_ROOT}", dest.replace("\\", "/"))
        if nuevo != txt: cambiados += 1
        return nuevo
    for s in skills:
        shutil.copytree(os.path.join(RAIZ, "skills", s), os.path.join(dest, s), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for base, _, archivos in os.walk(dest):
        for f in archivos:
            if f.endswith((".md", ".txt", ".yaml", ".yml", ".json")):
                p = os.path.join(base, f)
                try: t = open(p, encoding="utf-8").read()
                except UnicodeDecodeError: continue
                open(p, "w", encoding="utf-8").write(adaptar(t))
    # agentes: en una carpeta sin SKILL.md (Hermes no los indexa como skills); rutas de scripts → copia de Hermes
    ag = os.path.join(dest, "_agentes"); os.makedirs(ag)
    for f in sorted(os.listdir(os.path.join(RAIZ, "agents"))):
        t = open(os.path.join(RAIZ, "agents", f), encoding="utf-8").read()
        t = t.replace("${CLAUDE_PLUGIN_ROOT}/skills/", dest.replace("\\", "/") + "/")
        open(os.path.join(ag, f), "w", encoding="utf-8").write(t)
    restos = [os.path.join(b, f) for b, _, fs in os.walk(dest) for f in fs if f.endswith(".md")
              and re.search(r"\$\{CLAUDE_(SKILL_DIR|PLUGIN_ROOT)\}", open(os.path.join(b, f), encoding="utf-8").read())]
    print(f"Listo: {len(skills)} skills ({cambiados} archivos adaptados), agentes en {ag}.")
    if restos: print("AVISO: quedaron referencias sin adaptar en: " + ", ".join(restos[:5]))
    if not dest.startswith(os.path.join(os.path.expanduser("~"), ".hermes", "skills")):
        print(f"Agregar a ~/.hermes/config.yaml:\n  skills:\n    external_dirs:\n      - {dest}")
    print("En Hermes: /reload-skills y probar /pm-ayuda. Scripts: python3 " + os.path.join(dest, "pm-estado-proyecto", "scripts", "estado.py") + " …")

if __name__ == "__main__":
    main()
