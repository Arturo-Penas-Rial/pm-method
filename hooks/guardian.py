#!/usr/bin/env python3
"""Hook PreToolUse de pm-method: protege la columna vertebral de datos y la separación de roles.
- Con Write/Edit no se editan: estado.json, registros CSV (03-control/registros/*.csv), derivados de especificación
  (02-planificacion/especificacion/{spec-index.json,requisitos-bmad.csv,matriz-trazabilidad-bmad.csv,inventario-bmad.json},
  03-control/reportes/avance-bmad.csv), copias congeladas (00-direccion/historial/) ni instantáneas existentes de
  03-control/fuentes/ (se crea una nueva con fecha). Se usan los scripts.
- Con Bash se bloquean las mismas escrituras directas (redirecciones, tee, sed -i, cp/mv/rm hacia esos destinos, escrituras
  Python en línea), salvo que el comando sea uno de los scripts del paquete (estado.py, registro.py, bmad.py…).
- Subagentes pm-*: no escriben en carpetas de BMAD. Nadie salvo pm-director (ni el hilo principal ni otros subagentes)
  ejecuta estado.py puerta/rol/tolerancia/presupuesto/agil/umbrales-riesgo/cumplir-condiciones, limite-etapa --excepcion, set --forzar ni
  aprobar de nivel superior a gestor. (Los comandos que la persona escribe en su propia terminal no pasan por el hook.)
El hilo principal puede escribir en BMAD porque los flujos del propio BMAD lo hacen.
Salida: JSON con permissionDecision "deny" y el motivo; sin salida = sin decisión. Ante cualquier error propio, no decide.
"""
import json, os, re, shlex, sys

DERIVADOS = ("spec-index.json", "requisitos-bmad.csv", "matriz-trazabilidad-bmad.csv", "inventario-bmad.json", "avance-bmad.csv")
REGISTROS = ("riesgos.csv", "issues.csv", "cambios.csv", "decisiones.csv", "supuestos.csv", "lecciones.csv", "stakeholders.csv", "calidad.csv", "acciones.csv",
             "estereotipos.csv", "preferencias.csv", "raci.csv", "envios.csv")
BMAD = ("_bmad", "_bmad-output", ".bmad-core")
SCRIPTS = ("estado.py", "registro.py", "bmad.py", "nuevo_proyecto.py", "sanidad.py", "especificacion.py", "paquete.py", "exportar.py", "puertas.py",
           "interesados.py", "envios.py")

def negar(motivo):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": "pm-method: " + motivo}}, ensure_ascii=False))
    sys.exit(0)

def protegido(ruta):
    """Devuelve el motivo si la ruta es un archivo de gobierno protegido, o None."""
    r = ruta.replace("\\", "/")
    base = os.path.basename(r)
    if base == "estado.json":
        return "estado.json se actualiza solo con estado.py (o nuevo_proyecto.py / bmad.py), para mantener puertas, decisiones y migración coherentes."
    if "/03-control/registros/" in "/" + r and base in REGISTROS:
        return f"{base} se modifica con registro.py (valida valores, ids y referencias): registro.py --proyecto <dir> agregar|actualizar …"
    if base in DERIVADOS:
        return f"{base} es un derivado regenerable; se regenera con especificacion.py o bmad.py, no se edita."
    if "/03-control/fuentes/" in "/" + r and os.path.exists(ruta):
        return "03-control/fuentes/ guarda instantáneas fechadas e inmutables de fuentes externas: crear una instantánea nueva con fecha, no modificar la existente."
    if "/00-direccion/decisiones/" in "/" + r and re.search(r"-verificacion-autorizar-[a-z-]+\.md$", base):
        return "la lista de verificación de la puerta la generan y confirman los scripts (puertas.py lista / confirmar --por …), para que quede quién la confirmó."
    if "/00-direccion/historial/" in "/" + r:
        return "00-direccion/historial/ guarda versiones congeladas (líneas base): crear una versión nueva en su lugar."
    return None

def en_bmad(ruta):
    partes = ruta.replace("\\", "/").split("/")
    return any(p in BMAD for p in partes)

def destinos_bash(cmd):
    """Rutas que un comando escribiría: redirecciones, tee, sed -i, cp/mv (destino), rm, python con open(...,'w')."""
    d = []
    d += re.findall(r"(?:^|[^0-9&<>])>{1,2}\s*([^\s;|&<>]+)", cmd)            # > x, >> x (no 2>&1)
    for m in re.finditer(r"\btee\s+(?:-a\s+)?([^\s;|&]+)", cmd): d.append(m.group(1))
    for seg in re.split(r"[;&|]+", cmd):
        try: tok = shlex.split(seg)
        except ValueError: tok = seg.split()
        if not tok: continue
        prog = os.path.basename(tok[0])
        if prog == "sed" and any(t.startswith("-i") for t in tok[1:]): d += [t for t in tok[1:] if not t.startswith("-") and ("/" in t or "." in t)][1:]
        elif prog in ("cp", "mv", "install", "rsync") and len(tok) >= 3: d.append(tok[-1])
        elif prog in ("rm", "truncate", "touch"): d += [t for t in tok[1:] if not t.startswith("-")]
    for m in re.finditer(r"open\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"][wa]", cmd): d.append(m.group(1))
    return d

RESERVADOS = ("puerta", "rol", "tolerancia", "presupuesto", "agil", "cumplir-condiciones", "umbrales-riesgo")

def subcomandos_estado(cmd, script="estado.py"):
    """Para cada invocación de `script` (estado.py, puertas.py) en el comando: (subcomando, argumentos restantes)."""
    res = []
    for seg in re.split(r"[;&|]+", cmd):
        try: tok = shlex.split(seg)
        except ValueError: tok = seg.split()
        for i, x in enumerate(tok):
            # invocación directa (…/estado.py) o vía variable de shell ($E, ${E}) cuando el comando define o usa estado.py
            if os.path.basename(x) == script or (x.startswith("$") and script in cmd):
                j = i + 1
                while j < len(tok) and tok[j].startswith("--"):
                    j += 1 if "=" in tok[j] else 2
                if j < len(tok): res.append((tok[j], tok[j + 1:]))
    # forma lista (subprocess desde Python): ["python3", ".../estado.py", "--proyecto", "g", "puerta", …]
    for m in re.finditer(re.escape(script) + r"['\"]\s*,\s*(?:['\"]--proyecto['\"]\s*,\s*['\"][^'\"]*['\"]\s*,\s*)?['\"]([a-z-]+)['\"]((?:\s*,\s*['\"][^'\"]*['\"])*)", cmd):
        res.append((m.group(1), re.findall(r"['\"]([^'\"]*)['\"]", m.group(2))))
    return res

def main():
    try: datos = json.load(sys.stdin)
    except Exception: sys.exit(0)
    herramienta = datos.get("tool_name", ""); ti = datos.get("tool_input") or {}
    agente = str(datos.get("agent_type") or "")
    sub_pm = (agente.startswith("pm-") or ":pm-" in agente)
    director = "pm-director" in agente
    if herramienta == "Bash":
        cmd = ti.get("command", "")
        usa_script = any(re.search(rf"\b{re.escape(s)}\b", cmd) for s in SCRIPTS)
        # separación de roles: comandos de dirección solo desde pm-director (o el hilo principal)
        if not director:   # subagentes pm-* y también el hilo principal: las decisiones de la junta las registra pm-director
            for sc, resto in subcomandos_estado(cmd):
                r = " ".join(resto)
                if sc in RESERVADOS or (sc == "limite-etapa" and "--excepcion" in r) or (sc == "set" and "--forzar" in r):
                    negar("ese comando de estado.py está reservado a pm-director (puertas, nombramientos, tolerancias, excepciones, correcciones forzadas). "
                          + ("Devolvé la decisión en el bloque de retorno." if sub_pm else "Delegá en el subagente pm-method:pm-director con la decisión explícita (quién decidió, qué y con qué condiciones)."))
                if sc == "aprobar" and not re.search(r"--nivel[ =](gestor|product-owner|equipo)\b", r):
                    negar("aprobar de nivel junta, ejecutivo o capa de negocio lo registra pm-director; este agente solo usa --nivel gestor|product-owner|equipo.")
            for sc, _ in subcomandos_estado(cmd, "puertas.py"):
                if sc in ("confirmar", "preparacion-bmad"):
                    negar("puertas.py confirmar/preparacion-bmad registran actos humanos (confirmación de la junta, veredicto de BMAD): los ejecuta pm-director con la confirmación explícita de la persona. "
                          + ("Devolvé la confirmación requerida en el bloque de retorno." if sub_pm else "Delegá en el subagente pm-method:pm-director indicando quién confirmó qué."))
        for dst in destinos_bash(cmd):
            if sub_pm and en_bmad(dst):
                negar("los agentes de gestión no escriben en carpetas de BMAD (solo lectura vía pm-bmad-puente). Para cambiar la especificación: bmad.py handoff.")
            if not usa_script:
                motivo = protegido(dst)
                if motivo: negar(motivo)
        if not usa_script and re.search(r"(estado\.json|/registros/\w+\.csv)", cmd) and re.search(r"json\.dump|\.write\(|to_csv\(", cmd):
            negar("escritura directa de estado.json o de un registro desde código en línea: usar estado.py o registro.py.")
        sys.exit(0)
    ruta = ti.get("file_path") or ti.get("path") or ti.get("notebook_path") or ""
    if not ruta: sys.exit(0)
    if sub_pm and en_bmad(ruta):
        negar("los agentes de gestión no escriben en carpetas de BMAD. Usar bmad.py handoff para traspasar la decisión al equipo BMAD.")
    motivo = protegido(ruta)
    if motivo: negar(motivo)
    sys.exit(0)

if __name__ == "__main__":
    try: main()
    except SystemExit: raise
    except Exception: sys.exit(0)
