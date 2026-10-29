#!/usr/bin/env python3
"""Hook PreToolUse de pm-method: protege la columna vertebral de datos y la separación de roles.
- Con Write/Edit no se editan: estado.json, registros CSV (03-control/registros/*.csv), derivados de especificación
  (02-planificacion/especificacion/{spec-index.json,requisitos-bmad.csv,matriz-trazabilidad-bmad.csv,inventario-bmad.json},
  03-control/reportes/avance-bmad.csv), copias congeladas (00-direccion/historial/) ni instantáneas existentes de
  03-control/fuentes/ (se crea una nueva con fecha). Se usan los scripts.
- Con Bash se bloquean las mismas escrituras directas (redirecciones, tee, sed -i, cp/mv/rm hacia esos destinos, escrituras
  Python en línea). El comando se evalúa por segmento (separados por ; && || | & y saltos de línea): solo el segmento que
  ejecuta uno de los scripts del paquete (estado.py, registro.py, bmad.py…) queda exento de la comprobación de destinos,
  y ni siquiera ese segmento puede redirigir su salida hacia un archivo protegido.
- Subagentes pm-*: no escriben en carpetas de BMAD. Nadie salvo pm-director (ni el hilo principal ni otros subagentes)
  ejecuta estado.py puerta/rol/tolerancia/presupuesto/agil/umbrales-riesgo/cumplir-condiciones, limite-etapa --excepcion,
  set --forzar, ni aprobar o set con nivel superior a gestor. (Los comandos que la persona escribe en su propia terminal
  no pasan por el hook.)
- Con Write/Edit ni con Bash se escriben la bitácora (.bitacora.jsonl) ni las propuestas (03-control/propuestas/P-###.json):
  las escriben registro.py y el mecanismo común de escritura (2.6.0).
- registro.py aprobar y registro.py reconocer: el hook pide confirmación ("ask"), como envios.py aprobar.
- decision.py matriz … --elegir y riesgos.py opciones … --elegir: el hook pide confirmación ("ask"); registran en
  decisiones.csv la decisión de la persona que figura en --por.
- envios.py aprobar y envios.py enviar --confirmar: el hook pide confirmación ("ask"), de modo que Claude Code muestre
  el pedido de permiso y lo resuelva una persona, también cuando lo ejecuta pm-director (docs/SEGURIDAD.md, SEG-03).
El hilo principal puede escribir en BMAD porque los flujos del propio BMAD lo hacen.
Salida: JSON con permissionDecision "deny" o "ask" y el motivo; sin salida = sin decisión. Ante cualquier error propio,
no decide. Es un control de integridad del método frente a errores del modelo, no una frontera de seguridad frente a un
actor malicioso (docs/SEGURIDAD.md, SEG-09).
"""
import json, os, re, shlex, sys

DERIVADOS = ("spec-index.json", "requisitos-bmad.csv", "matriz-trazabilidad-bmad.csv", "inventario-bmad.json", "avance-bmad.csv")
REGISTROS = ("riesgos.csv", "issues.csv", "cambios.csv", "decisiones.csv", "supuestos.csv", "lecciones.csv", "stakeholders.csv", "calidad.csv", "acciones.csv",
             "estereotipos.csv", "preferencias.csv", "raci.csv", "envios.csv", "personas.csv")
BMAD = ("_bmad", "_bmad-output", ".bmad-core")
SCRIPTS = ("estado.py", "registro.py", "bmad.py", "nuevo_proyecto.py", "sanidad.py", "especificacion.py", "paquete.py", "exportar.py", "puertas.py",
           "interesados.py", "envios.py")
PYTHON = re.compile(r"^(python(\d+(\.\d+)?)?|py|pypy3?)(\.exe)?$")
REDIR = (">", ">>", ">|", "&>", "&>>", ">&")

def decidir(decision, motivo):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                             "permissionDecisionReason": "pm-method: " + motivo}}, ensure_ascii=False))
    sys.exit(0)

def negar(motivo): decidir("deny", motivo)

def protegido(ruta):
    """Devuelve el motivo si la ruta es un archivo de gobierno protegido, o None."""
    r = ruta.replace("\\", "/")
    base = os.path.basename(r)
    if base == "estado.json":
        return "estado.json se actualiza solo con estado.py (o nuevo_proyecto.py / bmad.py), para mantener puertas, decisiones y migración coherentes."
    if "/03-control/registros/" in "/" + r and base in REGISTROS:
        return f"{base} se modifica con registro.py (valida valores, ids y referencias): registro.py --proyecto <dir> agregar|actualizar …"
    if base == ".bitacora.jsonl":
        return ".bitacora.jsonl es la bitácora de escrituras (solo anexado, encadenada por huellas): la escriben los scripts; un cambio hecho fuera de ellos se reconoce con registro.py reconocer … --por … --motivo …"
    if "/03-control/propuestas/" in "/" + r and re.fullmatch(r"P-\d+\.json", base):
        return f"{base} es una propuesta con huella: se crea con registro.py proponer y se resuelve con registro.py aprobar|rechazar --por …"
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

def segmentos(cmd):
    """Divide el comando en comandos simples por ; && || | & y saltos de línea, respetando comillas y escapes.
    `>&`, `&>` y `>|` son redirecciones, no separadores."""
    segs, cur, q, i, n = [], [], None, 0, len(cmd)
    while i < n:
        c = cmd[i]
        if q:
            cur.append(c)
            if c == "\\" and q == '"' and i + 1 < n: cur.append(cmd[i + 1]); i += 2; continue
            if c == q: q = None
            i += 1; continue
        if c == "\\" and i + 1 < n: cur += [c, cmd[i + 1]]; i += 2; continue
        if c in "'\"": q = c; cur.append(c); i += 1; continue
        prev, nxt = (cmd[i - 1] if i else ""), (cmd[i + 1] if i + 1 < n else "")
        sep = c in ";\n" or (c == "|" and prev != ">") or (c == "&" and prev not in "<>" and nxt != ">")
        if sep:
            segs.append("".join(cur)); cur = []
            i += 2 if c in "|&" and nxt == c else 1
            continue
        cur.append(c); i += 1
    segs.append("".join(cur))
    return [s.strip() for s in segs if s.strip()]

def tokens(seg):
    try:
        lx = shlex.shlex(seg, posix=True, punctuation_chars=True); lx.whitespace_split = True
        return list(lx)
    except ValueError:
        return seg.split()

def invoca_script(tok, cmd):
    """True si el segmento ejecuta uno de los scripts del paquete (y no solo lo menciona, como `cp x/estado.py …`)."""
    i = 0
    while i < len(tok) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok[i]): i += 1      # VAR=valor delante del comando
    while i < len(tok) and tok[i] in ("env", "exec", "time", "nice", "command"): i += 1
    if i >= len(tok): return False
    prog = os.path.basename(tok[i])
    if prog in SCRIPTS: return True
    if tok[i].startswith("$"): return any(s in cmd for s in SCRIPTS)       # $E resumen, con E="python3 …/estado.py …"
    if prog == "sh" and i + 1 < len(tok) and tok[i + 1].endswith("py.sh"): i += 1; prog = "python3"
    if PYTHON.match(prog):
        j = i + 1
        while j < len(tok) and tok[j].startswith("-"):
            j += 2 if tok[j] in ("-X", "-W") else 1
        return j < len(tok) and os.path.basename(tok[j]) in SCRIPTS
    return False

def redirecciones(tok):
    return [tok[k + 1] for k, x in enumerate(tok[:-1]) if x in REDIR and not re.fullmatch(r"\d+|-", tok[k + 1])]

def destinos_comando(seg, tok):
    """Rutas que escribiría un comando simple: tee, sed -i, cp/mv (destino), rm, python con open(...,'w')."""
    d = []
    if tok:
        prog = os.path.basename(tok[0])
        args = [t for t in tok[1:] if t not in REDIR]
        if prog == "tee": d += [t for t in args if not t.startswith("-")]
        elif prog == "sed" and any(t.startswith("-i") for t in args): d += [t for t in args if not t.startswith("-") and ("/" in t or "." in t)][1:]
        elif prog in ("cp", "mv", "install", "rsync") and len(args) >= 2: d.append(args[-1])
        elif prog in ("rm", "truncate", "touch"): d += [t for t in args if not t.startswith("-")]
    for m in re.finditer(r"open\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"][wa]", seg): d.append(m.group(1))
    return d

def tiene_opcion(args, opcion):
    """argparse acepta prefijos de opciones largas (--conf = --confirmar): se cuentan los prefijos de 3+ caracteres."""
    for a in args:
        k = a.split("=", 1)[0]
        if len(k) >= 3 and k.startswith("--") and opcion.startswith(k): return True
    return False

RESERVADOS = ("puerta", "rol", "tolerancia", "presupuesto", "agil", "cumplir-condiciones", "umbrales-riesgo")
ESCRITURA_EN_LINEA = (re.compile(r"(estado\.json|/registros/\w+\.csv)"), re.compile(r"json\.dump|\.write\(|to_csv\("))

def subcomandos_estado(cmd, script="estado.py"):
    """Para cada invocación de `script` (estado.py, puertas.py, envios.py) en el comando: (subcomando, argumentos restantes)."""
    res = []
    for seg in segmentos(cmd):
        try: tok = shlex.split(seg)
        except ValueError: tok = seg.split()
        for i, x in enumerate(tok):
            # invocación directa (…/estado.py) o vía variable de shell ($E, ${E}) cuando el comando define o usa el script
            if os.path.basename(x) == script or (x.startswith("$") and script in cmd):
                j = i + 1
                while j < len(tok) and tok[j].startswith("--"):
                    j += 1 if "=" in tok[j] else 2
                if j < len(tok): res.append((tok[j], tok[j + 1:]))
    # forma lista (subprocess desde Python): ["python3", ".../estado.py", "--proyecto", "g", "puerta", …]
    for m in re.finditer(re.escape(script) + r"['\"]\s*,\s*(?:['\"]--proyecto['\"]\s*,\s*['\"][^'\"]*['\"]\s*,\s*)?['\"]([a-z-]+)['\"]((?:\s*,\s*['\"][^'\"]*['\"])*)", cmd):
        res.append((m.group(1), re.findall(r"['\"]([^'\"]*)['\"]", m.group(2))))
    return res

def revisar_bash(cmd, sub_pm, director):
    # separación de roles: comandos de dirección solo desde pm-director (o el hilo principal)
    if not director:   # subagentes pm-* y también el hilo principal: las decisiones de la junta las registra pm-director
        for sc, resto in subcomandos_estado(cmd):
            r = " ".join(resto)
            if sc in RESERVADOS or (sc == "limite-etapa" and tiene_opcion(resto, "--excepcion")) or (sc == "set" and tiene_opcion(resto, "--forzar")):
                negar("ese comando de estado.py está reservado a pm-director (puertas, nombramientos, tolerancias, excepciones, correcciones forzadas). "
                      + ("Devolvé la decisión en el bloque de retorno." if sub_pm else "Delegá en el subagente pm-method:pm-director con la decisión explícita (quién decidió, qué y con qué condiciones)."))
            if sc == "aprobar" and not re.search(r"--nivel[ =](gestor|product-owner|equipo)\b", r):
                negar("aprobar de nivel junta, ejecutivo o capa de negocio lo registra pm-director; este agente solo usa --nivel gestor|product-owner|equipo.")
            if sc == "set" and tiene_opcion(resto, "--nivel") and not re.search(r"--nivel[ =](gestor|product-owner|equipo)\b", r):
                negar("set con --nivel junta, ejecutivo o capa de negocio lo registra pm-director; este agente solo usa --nivel gestor|product-owner|equipo.")
        for sc, _ in subcomandos_estado(cmd, "puertas.py"):
            if sc in ("confirmar", "preparacion-bmad"):
                negar("puertas.py confirmar/preparacion-bmad registran actos humanos (confirmación de la junta, veredicto de BMAD): los ejecuta pm-director con la confirmación explícita de la persona. "
                      + ("Devolvé la confirmación requerida en el bloque de retorno." if sub_pm else "Delegá en el subagente pm-method:pm-director indicando quién confirmó qué."))
    # escrituras directas, segmento por segmento (SEG-09): mencionar un script no exime al resto del comando
    segs = segmentos(cmd); algun_script = False
    for seg in segs:
        tok = tokens(seg); es_script = invoca_script(tok, cmd); algun_script = algun_script or es_script
        destinos = redirecciones(tok) + ([] if es_script else destinos_comando(seg, tok))
        for dst in destinos:
            if sub_pm and en_bmad(dst):
                negar("los agentes de gestión no escriben en carpetas de BMAD (solo lectura vía pm-bmad-puente). Para cambiar la especificación: bmad.py handoff.")
            motivo = protegido(dst)
            if motivo: negar(motivo)
        if not es_script and all(rx.search(seg) for rx in ESCRITURA_EN_LINEA):
            negar("escritura directa de estado.json o de un registro desde código en línea: usar estado.py o registro.py.")
    if not algun_script and all(rx.search(cmd) for rx in ESCRITURA_EN_LINEA):    # código en línea repartido en varias líneas
        negar("escritura directa de estado.json o de un registro desde código en línea: usar estado.py o registro.py.")
    # acto humano: aprobar o enviar comunicaciones lo confirma siempre una persona en el pedido de permiso (SEG-03)
    for sc, resto in subcomandos_estado(cmd, "registro.py"):
        if sc in ("aprobar", "reconocer"):
            decidir("ask", f"registro.py {sc} registra un acto humano (aprobar una propuesta de cambio a un registro, o reconocer un cambio hecho fuera de los scripts) "
                           "a nombre de --por. Confirmar solo si esa persona lo revisó y lo pidió. / Records a human act on behalf of --por: confirm only if that person reviewed and asked for it.")
    for script, sub_ in (("decision.py", "matriz"), ("riesgos.py", "opciones")):
        for sc, resto in subcomandos_estado(cmd, script):
            if sc == sub_ and tiene_opcion(resto, "--elegir"):
                decidir("ask", f"{script} {sub_} --elegir registra en decisiones.csv la decisión de la persona que figura en --por (PUERTA HUMANA). "
                               "Confirmar solo si esa persona decidió esa opción y lo pidió. / Records a person's decision on behalf of --por: confirm only if that person decided it and asked for it.")
    for sc, resto in subcomandos_estado(cmd, "envios.py"):
        if sc == "aprobar":
            decidir("ask", "envios.py aprobar registra la aprobación humana de un mensaje (aprobado_por). Confirmar solo si la persona "
                           "que figura en --por aprobó este mensaje. / Records a human approval: confirm only if that person approved it.")
        if sc == "enviar" and tiene_opcion(resto, "--confirmar"):
            decidir("ask", "envios.py enviar --confirmar envía mensajes reales a los interesados (SMTP o webhook). Confirmar solo si la "
                           "persona revisó la vista previa y pidió el envío. / Sends real messages: confirm only after reviewing the preview.")

def main():
    try: datos = json.load(sys.stdin)
    except Exception: sys.exit(0)
    herramienta = datos.get("tool_name", ""); ti = datos.get("tool_input") or {}
    agente = str(datos.get("agent_type") or "")
    sub_pm = (agente.startswith("pm-") or ":pm-" in agente)
    director = "pm-director" in agente
    if herramienta == "Bash":
        revisar_bash(ti.get("command", ""), sub_pm, director)
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
