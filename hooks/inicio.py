#!/usr/bin/env python3
"""Hook SessionStart de pm-method: si la carpeta de trabajo contiene un proyecto (estado.json a ≤2 niveles), agrega al
contexto un resumen breve: fase, puertas pendientes y resultado rápido de sanidad. Si no hay proyecto, no imprime nada."""
import glob, json, os, subprocess, sys

def main():
    try: datos = json.load(sys.stdin)
    except Exception: datos = {}
    cwd = datos.get("cwd") or os.getcwd()
    cands = [os.path.join(cwd, "estado.json")] + glob.glob(os.path.join(cwd, "*", "estado.json")) + glob.glob(os.path.join(cwd, "*", "*", "estado.json"))
    cands = [c for c in cands if os.path.exists(c) and "proceso_actual" in json.load(open(c, encoding="utf-8"))][:3]
    if not cands: sys.exit(0)
    raiz = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    s = os.path.join(raiz, "skills", "pm-estado-proyecto", "scripts", "sanidad.py")
    lineas = []
    for c in cands:
        proy = os.path.dirname(c)
        try:
            r = subprocess.run([sys.executable, s, "--proyecto", proy, "--rapido", "--json"], capture_output=True, text=True, timeout=25)
            d = json.loads(r.stdout or "{}")
            e = json.load(open(c, encoding="utf-8"))
            errs = [h for h in d.get("hallazgos", []) if h["severidad"] == "ERROR"]
            lineas.append(f"pm-method · proyecto '{e.get('proyecto')}' en {os.path.relpath(proy, cwd) or '.'}: fase {e.get('fase')}/{e.get('proceso_actual')}, etapa {e.get('etapa_actual', {}).get('numero')}; "
                          f"sanidad rápida {d.get('cuenta', {}).get('ERROR', '?')} ERROR / {d.get('cuenta', {}).get('AVISO', '?')} AVISO."
                          + (" Errores: " + "; ".join(f"{h['codigo']} {h['mensaje']}" for h in errs[:3]) if errs else "")
                          + " Antes de producir artefactos o preparar una puerta, usar pm-orquestador / pm-sanidad.")
        except Exception:
            continue
    if lineas: print("\n".join(lineas))

if __name__ == "__main__":
    try: main()
    except Exception: sys.exit(0)
