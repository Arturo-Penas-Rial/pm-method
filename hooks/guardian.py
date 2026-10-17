#!/usr/bin/env python3
"""Hook PreToolUse de pm-method: protege la columna vertebral de datos.
- Archivos derivados (02-planificacion/especificacion/{spec-index.json,requisitos-bmad.csv,matriz-trazabilidad-bmad.csv,
  inventario-bmad.json}) y copias congeladas (00-direccion/historial/) no se editan con Write/Edit: se regeneran con scripts.
- estado.json solo lo escriben estado.py / nuevo_proyecto.py / bmad.py; los registros CSV solo registro.py (validación).
- Los subagentes pm-* no escriben en carpetas de BMAD (_bmad/, _bmad-output/, .bmad-core/): BMAD es solo lectura
  para pm-method. El hilo principal sí puede, porque los flujos del propio BMAD escriben ahí.
Salida: JSON con permissionDecision "deny" y el motivo, o nada (sin decisión). Nunca falla en forma bloqueante por error propio.
"""
import json, os, re, sys

DERIVADOS = ("spec-index.json", "requisitos-bmad.csv", "matriz-trazabilidad-bmad.csv", "inventario-bmad.json", "avance-bmad.csv")
REGISTROS = ("riesgos.csv", "issues.csv", "cambios.csv", "decisiones.csv", "supuestos.csv", "lecciones.csv", "stakeholders.csv", "calidad.csv", "acciones.csv")
BMAD = ("_bmad", "_bmad-output", ".bmad-core")

def negar(motivo):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "pm-method: " + motivo}}, ensure_ascii=False))
    sys.exit(0)

def es_proyecto_pm(ruta):
    d = os.path.dirname(os.path.abspath(ruta))
    for _ in range(6):
        if os.path.exists(os.path.join(d, "estado.json")): return d
        nd = os.path.dirname(d)
        if nd == d: break
        d = nd
    return None

def main():
    try: datos = json.load(sys.stdin)
    except Exception: sys.exit(0)
    herramienta = datos.get("tool_name", ""); ti = datos.get("tool_input") or {}; agente = str(datos.get("agent_type") or "")
    sub_pm = agente.startswith("pm-") or ":pm-" in agente
    cwd = datos.get("cwd") or os.getcwd()
    if herramienta == "Bash":
        cmd = ti.get("command", "")
        if sub_pm and re.search(r"(_bmad-output|_bmad/|\.bmad-core)", cmd) and re.search(r"(>|>>|\btee\b|sed\s+-i|\brm\b|\bmv\b|\bcp\b[^|;]*\s(\S*_bmad))", cmd):
            negar("los agentes de gestión no escriben en carpetas de BMAD (solo lectura vía pm-bmad-puente). Si hay que cambiar la especificación: bmad.py handoff y que lo aplique el equipo BMAD.")
        sys.exit(0)
    ruta = ti.get("file_path") or ti.get("path") or ti.get("notebook_path") or ""
    if not ruta: sys.exit(0)
    ra = ruta if os.path.isabs(ruta) else os.path.join(cwd, ruta)
    partes = os.path.normpath(ra).split(os.sep)
    if sub_pm and any(p in partes for p in BMAD):
        negar("los agentes de gestión no escriben en carpetas de BMAD. Usar bmad.py handoff para traspasar la decisión al equipo BMAD.")
    proy = es_proyecto_pm(ra)
    if not proy: sys.exit(0)
    rel = os.path.relpath(ra, proy).replace(os.sep, "/")
    base = os.path.basename(ra)
    if rel == "estado.json":
        negar("estado.json se actualiza solo con estado.py (o nuevo_proyecto.py / bmad.py) para mantener puertas, migración y decisiones coherentes.")
    if rel.startswith("02-planificacion/especificacion/") and base in DERIVADOS or rel.startswith("03-control/reportes/") and base == "avance-bmad.csv":
        negar(f"{base} es un derivado regenerable (contrato de especificación). Se regenera con especificacion.py / bmad.py; no se edita.")
    if rel.startswith("00-direccion/historial/"):
        negar("00-direccion/historial/ guarda versiones congeladas (líneas base). Crear una versión nueva en su lugar.")
    if rel.startswith("03-control/registros/") and base in REGISTROS and herramienta in ("Write", "Edit", "MultiEdit"):
        negar(f"{base} se modifica con registro.py (valida valores, ids y referencias). Ej.: registro.py --proyecto <dir> agregar|actualizar …")
    sys.exit(0)

if __name__ == "__main__":
    try: main()
    except SystemExit: raise
    except Exception: sys.exit(0)
