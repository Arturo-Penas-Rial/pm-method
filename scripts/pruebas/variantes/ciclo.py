#!/usr/bin/env python3
"""Recorrido paramétrico del ciclo PRINCE2 sobre cualquier fixture de BMAD (docs/PRUEBAS.md §2.5; informe de cobertura §7.2).

Uso:  python3 scripts/pruebas/variantes/ciclo.py [--bmad 6.12.4] [--idioma es] [--python RUTA] [--deps completas|minimas]
                                                [--salida-cp utf-8|cp1252] [--ruta simple|espacios] [--cierre normal|prematuro]
                                                [--dir DIR]
Las guías E2E están escritas sobre los ids del fixture real; este recorrido no depende de ids: nuevo proyecto →
especificación (BMAD o nativa) → autorizar-inicio → autorizar-proyecto rechazado y después aprobado → etapa condicionada
→ cumplir-condiciones → presupuestos, riesgos, cambios e issues → límite de etapa con excepción → plan rechazado y
después aprobado → decisión con matriz y --elegir → período con tablero → exportar, expediente de auditoría y verificar
→ cierre (normal o --prematuro). En cada paso verifica: código esperado, cero trazas, JSON válido, y al final: ids
únicos, bitácora íntegra (registro.py historial sin BIT), huella de BMAD sin cambios, idioma de la salida, sanidad sin
ERROR fuera de lo esperado, guardián y hook de inicio con la decisión esperada. Las degradaciones por el entorno
(PyYAML, openpyxl, python-docx faltantes; capas TOML ignoradas antes de 3.11) se informan como omisiones observadas
para compararlas con el manifiesto de la celda (matriz.py).
"""
import argparse, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import FIX, RAIZ, SITIO, Ejecutor, Registro, escribir, huella, idioma_de, ids_repetidos, interpretes, leer_csv

BMADS = ("ninguno", "v4", "v6", "6.12.4", "6.12.4-fuera", "6.12.4-toml")
DEPS_OPCIONALES = "yaml,docx,openpyxl,matplotlib,playwright"
G = "gestion"
EJ, GE = "Laura Méndez", "Martín Suárez"
POR_EJ = "Ejecutiva: Laura Méndez"


def preparar_repo(base, bmad, ruta):
    """Copia del fixture (o carpeta vacía) en una ruta simple o con espacios y acentos."""
    repo = os.path.join(base, "Gestión de año 2027", "Mi proyecto") if ruta == "espacios" else os.path.join(base, "repo")
    if os.path.exists(repo): shutil.rmtree(repo)
    os.makedirs(os.path.dirname(repo), exist_ok=True)
    origen = {"v4": "bmad-v4", "v6": "bmad-v6"}.get(bmad, "bmad-v6.12-real")
    if bmad == "ninguno": os.makedirs(repo)
    else: shutil.copytree(os.path.join(FIX, origen), repo)
    if bmad == "6.12.4-fuera":      # versión fuera del rango probado → modo degradado con aviso
        m = os.path.join(repo, "_bmad", "_config", "manifest.yaml")
        with open(m, encoding="utf-8") as fh: t = fh.read()
        escribir(m, t.replace("6.12.4", "6.99.0"))
    if bmad == "6.12.4-toml":       # personalización del equipo: planning_artifacts en otra carpeta (capa TOML de v6.11+)
        os.rename(os.path.join(repo, "_bmad-output", "planning-artifacts"), os.path.join(repo, "_bmad-output", "planificacion"))
        escribir(os.path.join(repo, "_bmad", "custom", "config.toml"),
                 '[modules.bmm]\nplanning_artifacts = "{project-root}/_bmad-output/planificacion"\n')
    return repo


def art(x, repo, clave, rel, texto=None):
    escribir(os.path.join(repo, G, rel), texto or f"---\ntipo: {clave}\nestado: borrador\n---\n# {clave}\nBeneficio B-1. Contenido mínimo del recorrido de variantes.\n")
    x("estado", "--proyecto", G, "artefacto", clave, "--ruta", rel, "--estado", "en-revision", paso=f"artefacto {clave}")


def junta(x, repo, tipo, fecha, arts=()):
    for clave, rel in arts: art(x, repo, clave, rel)
    x("puertas", "--proyecto", G, "lista", tipo, "--fecha", fecha, paso=f"lista {tipo}")
    x("puertas", "--proyecto", G, "confirmar", tipo, "--por", POR_EJ, "--fecha", fecha, paso=f"confirmar {tipo}")


BLOQUEOS_ESPERADOS = {"v4": (r"PRD de BMAD no est[áa] final", r"BMAD PRD is not final")}   # el PRD del fixture v4 no tiene status


def decidir(x, reg, bmad, tipo, fecha, *extra, paso=""):
    """Registra 'aprobado'; si la verificación lo bloquea, los bloqueos deben ser los esperados de la celda (control
    legítimo, mensaje sin traza) y la junta decide 'condicionado' (los bloqueos pasan a ser condiciones)."""
    r = x("estado", "--proyecto", G, "puerta", tipo, "--decision", "aprobado", "--por", POR_EJ, "--fecha", fecha, *extra, ok=(0, 1), paso=paso or f"puerta {tipo}")
    if r.rc == 0: return r
    bloqueos = [l.strip()[2:] for l in r.err.splitlines() if l.strip().startswith("- ")]
    esperados = BLOQUEOS_ESPERADOS.get(bmad, ())
    inesperados = [b for b in bloqueos if not any(re.search(p, b) for p in esperados)]
    reg.check(f"{paso or tipo}: 'aprobado' solo se bloquea por los controles esperados de la celda", bloqueos and not inesperados, inesperados or r.err[-300:])
    return x("estado", "--proyecto", G, "puerta", tipo, "--decision", "condicionado", "--por", POR_EJ, "--fecha", fecha, *extra,
             "--condiciones", "resolver los bloqueos de la verificación", paso=(paso or f"puerta {tipo}") + " (condicionada)")


def estado(repo):
    with open(os.path.join(repo, G, "estado.json"), encoding="utf-8") as fh: return json.load(fh)


def recorrer(celda, base, reg):
    """celda: dict con python_ruta, deps, bmad, idioma, salida, ruta y cierre. Anota comprobaciones y omisiones en reg y
    devuelve la carpeta del repositorio de trabajo."""
    py = celda["python_ruta"]
    env = {"PYTHONIOENCODING": "cp1252"} if celda.get("salida") == "cp1252" else {}
    if celda.get("deps") == "minimas":
        env.update({"PYTHONPATH": SITIO, "PM_SIN_DEPS": DEPS_OPCIONALES,
                    "PATH": os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep) if not os.path.exists(os.path.join(p, "mmdc")))})
    repo = preparar_repo(base, celda["bmad"], celda.get("ruta", "simple"))
    x = Ejecutor(reg, py, env, cwd=repo)
    idioma, bmad = celda.get("idioma", "es"), celda["bmad"]
    h0 = huella(repo)
    salidas_idioma = []

    # 1 · nuevo proyecto
    x("nuevo", "--ruta", G, "--nombre", "Portal de socios", "--idioma", idioma, "--enfoque", "hibrido", "--ejecutivo", EJ, "--gestor", GE,
      "--fecha", "2026-10-01", paso="nuevo_proyecto")
    x("estado", "--proyecto", G, "rol", "autoridad_cambio=Sofía Ramírez", "usuario_senior=Sofía Ramírez", "proveedor_senior=Diego Ferreira", paso="roles")

    # 2 · especificación: BMAD (detectar, requisitos) o nativa
    if bmad == "ninguno":
        escribir(os.path.join(repo, G, "02-planificacion", "requisitos.md"),
                 "| Id | Requisito | Interesado | Categoría | Prioridad | Criterio | Método | Fase | Padre | Estado |\n|---|---|---|---|---|---|---|---|---|---|\n"
                 "| REQ-001 | Acceso del socio | Socio | solucion_funcional | alta | x | prueba | 1 | | aprobado |\n"
                 "| REQ-002 | Consulta de saldos | Socio | solucion_funcional | media | y | demostracion | 1 | | aprobado |\n")
    else:
        d = x("bmad", "--proyecto", G, "detectar", paso="bmad detectar")
        det = {}
        try: det = json.loads(d.out[:d.out.rfind("}") + 1] or "{}")
        except ValueError: reg.check("bmad detectar: JSON válido", False, d.out[:300])
        esperado = {"v4": "v4", "v6": None, "6.12.4": "soportada", "6.12.4-toml": "soportada"}.get(bmad)
        if bmad == "6.12.4-fuera":
            reg.check("bmad detectar fuera de rango (6.99.0): modo degradado con AVISO", det.get("soporte") not in ("soportada", "v4") and "modo degradado" in d.out, d.out[-300:])
        elif esperado:
            reg.check(f"bmad detectar: soporte «{esperado}»", det.get("soporte") == esperado, str(det.get("soporte")))
        if "PyYAML" in d.err: reg.omitir("bmad-pyyaml", "bmad.py: falta PyYAML (config.yaml y sprint-status.yaml no se leen)")
        if re.search(r"TOML", d.err + d.out) and "tomllib" in (d.err + d.out): reg.omitir("bmad-toml", "bmad.py: capas TOML de BMAD ignoradas (sin tomllib, Python < 3.11)")
        x("bmad", "--proyecto", G, "requisitos", paso="bmad requisitos")
    r = x("especificacion", "--proyecto", G, "resumen", "--json", paso="especificacion resumen")
    res = r.json()
    if isinstance(res, dict) and not res.get("requisitos") and {"bmad-pyyaml", "bmad-toml"} & {o["clave"] for o in reg.omisiones}:
        # BMAD inutilizable en este entorno (v4 sin PyYAML; capas TOML sin tomllib) y el puente lo avisó: el resto del
        # ciclo depende de la especificación, así que se verifica lo que sí vale (sin traza, BMAD intacto, hooks) y se termina
        reg.omitir("ciclo-sin-especificacion", "BMAD no se puede leer en este entorno (el puente lo avisa): el ciclo se detiene tras la especificación")
        reg.check("BMAD intacto tras el aviso", huella(repo) == h0)
        ini = x("inicio", entrada=json.dumps({"cwd": repo}, ensure_ascii=False).encode("utf-8"), paso="hook de inicio")
        reg.check("hook de inicio: resume el proyecto", "pm-method · proyecto" in ini.out, ini.out[-300:])
        return repo
    reg.check("especificacion resumen --json: JSON válido con requisitos", isinstance(res, dict) and (res.get("requisitos") or 0) > 0, r.out[:300])
    sinc = (res or {}).get("sin_cobertura") or [] if isinstance(res, dict) else []
    if sinc:   # paquetes de la WBS que cubren lo que la especificación deja sin historia (ESP-03 en entrega)
        escribir(os.path.join(repo, G, "02-planificacion", "wbs.csv"), "codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref\n1,Producto,producto,,,,\n"
                 + "".join(f"1.{i},Paquete {r_},paquete,Equipo,40,3000,{r_}\n" for i, r_ in enumerate(sinc, 1)))
        r2 = x("especificacion", "--proyecto", G, "resumen", "--json", paso="especificacion resumen (con WBS)")
        reg.check("WBS de cobertura: la fachada no deja requisitos sin cobertura", not ((r2.json() or {}).get("sin_cobertura")), r2.out[:300])
    if bmad == "6.12.4-toml" and isinstance(res, dict):
        toml_ok = res.get("requisitos") == 42
        reg.check("BMAD con _bmad/custom/config.toml: la fachada ve los 42 ids (la capa TOML se aplica) o el puente avisa que la ignora",
                  toml_ok or any(o["clave"] == "bmad-toml" for o in reg.omisiones), f"requisitos={res.get('requisitos')} omisiones={reg.omisiones}")

    # 3 · hooks: guardián y hook de inicio con la decisión esperada
    pe = os.path.join(repo, G, "estado.json")
    gd = x("guardian", entrada=json.dumps({"tool_name": "Write", "tool_input": {"file_path": pe}}, ensure_ascii=False).encode("utf-8"), paso="guardián estado.json")
    gp = x("guardian", entrada=json.dumps({"tool_name": "Write", "tool_input": {"file_path": os.path.join(repo, G, "02-planificacion", "plan.md")}}).encode("utf-8"), paso="guardián plan.md")
    reg.check("guardián: niega escribir estado.json y deja escribir un documento", '"deny"' in gd.out and '"deny"' not in gp.out, gd.out[-200:] + gp.out[-200:])
    pedido = "please show me the next step of the project and the risk report" if idioma == "es" else "mostrame el siguiente paso del proyecto y el informe de riesgos por favor"
    hi = x("idioma", entrada=json.dumps({"prompt": pedido, "cwd": repo}, ensure_ascii=False).encode("utf-8"), paso="hook de idioma")
    reg.check("hook de idioma: un pedido en el otro idioma agrega la instrucción de responder en ese idioma", "additionalContext" in hi.out, hi.out[-200:])

    # 4 · autorizar-inicio
    junta(x, repo, "autorizar-inicio", "2026-10-05", [("project-brief", "01-inicio/project-brief.md")])
    decidir(x, reg, bmad, "autorizar-inicio", "2026-10-05", "--fin", "2026-10-30", paso="puerta autorizar-inicio")

    # 5 · autorizar-proyecto rechazado y después aprobado
    x("estado", "--proyecto", G, "tolerancia", "--nivel", "proyecto", "tiempo=±3 semanas", "costo=±10 %", paso="tolerancias")
    junta(x, repo, "autorizar-proyecto", "2026-10-20", [("business-case", "00-direccion/business-case.md"), ("pid", "00-direccion/pid.md"),
                                                       ("plan-proyecto", "02-planificacion/plan-proyecto.md")])
    fase0 = estado(repo).get("fase")
    x("estado", "--proyecto", G, "puerta", "autorizar-proyecto", "--decision", "rechazado", "--por", POR_EJ, "--fecha", "2026-10-20", paso="puerta autorizar-proyecto rechazado")
    e = estado(repo)
    reg.check("autorizar-proyecto rechazado: el proyecto no queda autorizado ni cambia de fase", not e.get("proyecto_autorizado") and e.get("fase") == fase0, f"{e.get('fase')} {e.get('proyecto_autorizado')}")
    junta(x, repo, "autorizar-proyecto", "2026-10-27")
    decidir(x, reg, bmad, "autorizar-proyecto", "2026-10-27", paso="puerta autorizar-proyecto aprobado")
    reg.check("autorizar-proyecto aprobado: proyecto autorizado", estado(repo).get("proyecto_autorizado") is True)
    if bmad != "ninguno":   # línea base del PRD antes de las etapas de entrega (ESP-11), como en las guías
        x("bmad", "--proyecto", G, "linea-base", "prd", "--version", "1.0", "--por", POR_EJ, "--fecha", "2026-10-27", paso="bmad linea-base prd")

    # 6 · etapa condicionada → cumplir-condiciones
    junta(x, repo, "autorizar-etapa", "2026-10-27", [("plan-etapa-2", "02-planificacion/plan-etapa-2.md")])
    x("estado", "--proyecto", G, "puerta", "autorizar-etapa", "--decision", "condicionado", "--por", POR_EJ, "--fecha", "2026-10-27",
      "--etapa-nombre", "Release 1", "--fin", "2027-01-29", "--tol", "costo=±10 %", "tiempo=+2 semanas", "--condiciones", "prueba de carga planificada",
      paso="puerta autorizar-etapa condicionada")
    x("estado", "--proyecto", G, "cumplir-condiciones", "autorizar-etapa", "--fecha", "2026-11-03", "--por", "Aseguramiento: Andrea Costa",
      "--nota", "plan de prueba de carga aprobado", paso="cumplir-condiciones")
    reg.check("etapa autorizada: fase de entrega", estado(repo).get("fase") == "entrega", estado(repo).get("fase"))

    # 7 · presupuestos, riesgos, cambios e issues
    x("estado", "--proyecto", G, "presupuesto", "cambio=10000", "riesgo=5000", "--por", POR_EJ, "--fecha", "2026-10-27", paso="presupuestos")
    R = lambda registro, *campos, paso="", ok=(0,): x("registro", "--proyecto", G, "agregar", registro, *[y for c in campos for y in ("--campo", c)], paso=paso or f"agregar {registro}", ok=ok)
    R("riesgos", "evento=Proveedor de SMS sin disponibilidad", "tipo=amenaza", "probabilidad=3", "impacto=4", "propietario=Diego Ferreira", "fecha_identificacion=2026-11-02", "fecha_revision=2026-12-15")
    R("riesgos", "evento=Adopción menor a la prevista", "tipo=amenaza", "probabilidad=2", "impacto=3", "propietario=Sofía Ramírez", "fecha_identificacion=2026-11-02", "fecha_revision=2026-12-15")
    R("issues", "tipo=solicitud-cambio", "titulo=Pagos con QR", "responsable=Martín Suárez", "fecha=2026-11-10")
    R("cambios", "titulo=Pagos con QR", "descripcion=Agregar pagos con QR", "fecha=2026-11-10", "estado=pendiente-decision", "costo=3000")
    lr = x("registro", "--proyecto", G, "listar", "riesgos", "--json", paso="listar riesgos --json")
    reg.check("registro.py listar riesgos --json: JSON válido con 2 riesgos", isinstance(lr.json(), list) and len(lr.json()) == 2, lr.out[:200])

    # 8 · límite de etapa con excepción → plan rechazado → plan aprobado
    R("issues", "tipo=problema-preocupacion", "titulo=Excepción X-001: pronóstico fuera de la tolerancia de tiempo", "prioridad=urgente",
      "severidad=critica", "responsable=Martín Suárez", "estado=escalado", "fecha=2026-12-01")
    art(x, repo, "informe-excepcion-X-001", "03-control/reportes/2026-12-01-informe-excepcion-X-001.md")
    x("estado", "--proyecto", G, "limite-etapa", "--excepcion", "X-001", paso="limite-etapa --excepcion")
    reg.check("límite de etapa con excepción: excepción abierta X-001", estado(repo).get("excepcion_abierta") == "X-001", estado(repo).get("excepcion_abierta"))
    junta(x, repo, "autorizar-plan-excepcion", "2026-12-04", [("plan-excepcion-X-001", "02-planificacion/plan-excepcion-X-001.md")])
    x("estado", "--proyecto", G, "puerta", "autorizar-plan-excepcion", "--decision", "rechazado", "--por", POR_EJ, "--fecha", "2026-12-04", paso="plan de excepción rechazado")
    reg.check("plan de excepción rechazado: la excepción sigue abierta", estado(repo).get("excepcion_abierta") == "X-001", estado(repo).get("excepcion_abierta"))
    junta(x, repo, "autorizar-plan-excepcion", "2026-12-08")
    decidir(x, reg, bmad, "autorizar-plan-excepcion", "2026-12-08", "--fin", "2027-02-26", paso="plan de excepción aprobado")
    reg.check("plan de excepción aprobado: la excepción se cierra", not estado(repo).get("excepcion_abierta"), estado(repo).get("excepcion_abierta"))

    # 9 · decisión con matriz → --elegir
    x("decision", "--proyecto", G, "matriz", "qr", "--proponer", "--tipo", "planificacion", "--pregunta", "¿Cuándo entregamos los pagos con QR?",
      "--fecha", "2026-12-09", paso="matriz --proponer")
    hoja = os.path.join(repo, G, "03-control", "decisiones", "qr")
    escribir(os.path.join(hoja, "criterios.csv"), "criterio,descripcion,peso,sentido,escala,eliminatorio,importar,fuente_peso,notas\n"
             "valor,Valor para el socio,60,mayor,1-5,,,plan de etapa,\ncosto,Costo,40,menor,num,,,plan de etapa,\n")
    escribir(os.path.join(hoja, "opciones.csv"), "opcion,descripcion,ref,valor,valor_fuente,costo,costo_fuente,notas\n"
             "O1,Release 1,,5,encuesta de socios,3000,presupuesto,\nO2,Release 2,,3,encuesta de socios,2000,presupuesto,\nO3,No hacer nada,,1,encuesta de socios,0,presupuesto,\n")
    mz = x("decision", "--proyecto", G, "matriz", "qr", "--json", paso="matriz --json")
    mj = mz.json() or {}
    reg.check("decision.py matriz --json: JSON válido con recomendada", bool(mj.get("recomendada")), mz.out[:300])
    rec = mj.get("recomendada") or "O1"
    x("decision", "--proyecto", G, "matriz", "qr", "--elegir", rec, "--por", POR_EJ, "--fecha", "2026-12-09", paso="matriz --elegir")
    decs = leer_csv(os.path.join(repo, G, "03-control", "registros", "decisiones.csv"))
    reg.check("--elegir registra la decisión con la hoja", any("qr" in (f.get("notas", "") + f.get("opciones_consideradas", "") + f.get("decision", "")).lower() for f in decs), str(decs[-1:])[:300])

    # 10 · período: JSON, tablero; radar y contexto
    pj = x("estado", "--proyecto", G, "periodo", "--desde", "2026-11-01", "--corte", "2026-12-15", "--json", paso="periodo --json")
    reg.check("estado.py periodo --json: JSON válido", isinstance(pj.json(), dict), pj.out[:200])
    x("estado", "--proyecto", G, "periodo", "--desde", "2026-11-01", "--corte", "2026-12-15", "--tablero", paso="periodo --tablero")
    reg.check("tablero de avance generado", os.path.exists(os.path.join(repo, G, "03-control", "reportes", "2026-12-15-tablero-avance.html")))
    rj = x("estado", "--proyecto", G, "radar", "--corte", "2026-12-15", "--json", paso="radar --json")
    reg.check("estado.py radar --json: JSON válido", isinstance(rj.json(), dict), rj.out[:200])
    ra = x("estado", "--proyecto", G, "radar", "--corte", "2026-12-15", paso="radar")
    cx = x("estado", "--proyecto", G, "contexto", "--corte", "2026-12-15", paso="contexto")
    pv = x("puertas", "--proyecto", G, "verificar", "autorizar-cierre", ok=(0, 1, 2), paso="puertas verificar autorizar-cierre")
    salidas_idioma += [ra.out, cx.out]
    solo_es = [pv.out]

    # 11 · exportar, expediente de auditoría y verificar
    xs = x("exportar", "xlsx", "--proyecto", G, "--salida", os.path.join(G, "exportados", "registros.xlsx"), ok=None, paso="exportar xlsx")
    if xs.rc != 0:
        reg.check("exportar xlsx sin openpyxl: mensaje claro que nombra openpyxl", "openpyxl" in xs.todo, xs.todo[-300:])
        reg.omitir("exportar-xlsx", "exportar.py xlsx: falta openpyxl")
    else:
        reg.check("exportar xlsx: archivo generado", os.path.exists(os.path.join(repo, G, "exportados", "registros.xlsx")))
    xd = x("exportar", "docx", "--entrada", os.path.join(G, "00-direccion", "pid.md"), "--salida", os.path.join(G, "exportados", "pid.docx"), ok=None, paso="exportar docx")
    if xd.rc != 0:
        reg.check("exportar docx sin python-docx: mensaje claro que nombra python-docx", "docx" in xd.todo, xd.todo[-300:])
        reg.omitir("exportar-docx", "exportar.py docx: falta python-docx")
    else:
        reg.check("exportar docx: archivo generado", os.path.exists(os.path.join(repo, G, "exportados", "pid.docx")))
    zp = os.path.join(repo, "expediente.zip")
    x("paquete", "--proyecto", G, "auditoria", "--proposito", "auditoría interna", "--salida", zp, paso="paquete auditoria")
    vz = x("paquete", "--proyecto", G, "verificar", zp, paso="paquete verificar")
    reg.check("expediente de auditoría generado y verificado", os.path.exists(zp) and vz.rc == 0, vz.todo[-300:])

    # 12 · cierre normal o prematuro
    prematuro = celda.get("cierre") == "prematuro"
    if prematuro:   # la junta ordena el cierre (decisión registrada por pm-director) y el cierre la cita
        x("estado", "--proyecto", G, "puerta", "decision-ad-hoc", "--decision", "aprobado", "--por", POR_EJ, "--fecha", "2027-02-20",
          "--motivo", "cierre prematuro: el business case dejó de ser viable", paso="decisión de la junta: cierre prematuro")
        did = estado(repo)["puertas"][-1].get("decision_id", "")
        x("estado", "--proyecto", G, "cierre", "--prematuro", "--decision", did, paso="cierre --prematuro")
        cp = estado(repo).get("cierre_prematuro") or {}
        reg.check("cierre prematuro: estado.json cita la decisión de la junta", cp.get("decision") == did and estado(repo).get("fase") == "cierre", str(cp)[:200])
    else:
        x("estado", "--proyecto", G, "cierre", paso="cierre")
    junta(x, repo, "autorizar-cierre", "2027-02-26", [("informe-fin-proyecto", "04-cierre/informe-fin-proyecto.md"), ("registro-aceptacion", "04-cierre/registro-aceptacion.md"),
                                                     ("recomendaciones-seguimiento", "04-cierre/recomendaciones-seguimiento.md")])
    import glob as _glob
    solo_es += [open(f_, encoding="utf-8").read() for f_ in sorted(_glob.glob(os.path.join(repo, G, "00-direccion", "decisiones", "*-verificacion-autorizar-cierre.md")))[-1:]]
    pc = x("estado", "--proyecto", G, "puerta", "autorizar-cierre", "--decision", "condicionado", "--por", POR_EJ, "--fecha", "2027-02-26",
           "--condiciones", "cerrar los riesgos abiertos en el traspaso", ok=(0, 1), paso="puerta autorizar-cierre")
    if pc.rc == 0: reg.check("autorizar-cierre (condicionada): proyecto cerrado", estado(repo).get("fase") in ("cerrado", "cierre"), estado(repo).get("fase"))
    else: reg.check("autorizar-cierre rechazada por un bloqueo explícito (sin traza)", "BLOQUEO" in pc.todo or "bloque" in pc.todo.lower(), pc.todo[-300:])

    # 13 · invariantes finales
    sj = x("sanidad", "--proyecto", G, "--json", "--corte", "2027-02-26", ok=(0, 1), paso="sanidad final")
    s = sj.json() or {}
    errores = sorted({h["codigo"] for h in s.get("hallazgos", []) if h.get("severidad") == "ERROR"})
    permitidos = set(celda.get("errores_permitidos", ()))
    reg.check("sanidad final: JSON válido y sin ERROR fuera de lo esperado", isinstance(s, dict) and "hallazgos" in s and not (set(errores) - permitidos),
              f"ERROR {errores} (permitidos {sorted(permitidos)})")
    st = x("sanidad", "--proyecto", G, "--corte", "2027-02-26", ok=(0, 1), paso="sanidad (texto)")
    solo_es.append(st.out)
    hist = x("registro", "--proyecto", G, "historial", ok=(0, 1), paso="registro historial")
    reg.check("bitácora íntegra: registro.py historial sin BIT-01/BIT-02", "BIT-0" not in hist.todo and hist.rc == 0, hist.todo[-300:])
    rep = ids_repetidos(os.path.join(repo, G))
    reg.check("ids únicos en todos los registros", not rep, rep)
    reg.check("BMAD intacto: ningún archivo de _bmad/, _bmad-output/, .bmad-core/ o docs/ cambió", huella(repo) == h0,
              sorted(k for k in set(h0) | set(huella(repo)) if h0.get(k) != huella(repo).get(k))[:5])
    ini = x("inicio", entrada=json.dumps({"cwd": repo}, ensure_ascii=False).encode("utf-8"), paso="hook de inicio")
    reg.check("hook de inicio: resume el proyecto (sin AVISO de proyecto roto)", "pm-method · proyecto" in ini.out and "pm-method · AVISO" not in ini.out, ini.out[-300:])
    otro = "en" if idioma == "es" else "es"
    malos = [t_[:120] for t_ in salidas_idioma if idioma_de(t_) == otro]
    reg.check(f"idioma de la salida: radar y contexto no salen en «{otro}» en un proyecto «{idioma}»", not malos, malos)
    if idioma == "en":   # 2.6.3: hallazgos de sanidad y puertas en el idioma del proyecto (antes era una nota)
        lineas_es = [l.strip()[:160] for t_ in solo_es for l in t_.splitlines()
                     if idioma_de(re.sub(r"«[^»]*»|`[^`]*`|\S+-\S+", "", l)) == "es"]   # sin datos citados, código ni ids (informe-fin-proyecto)
        reg.check("idioma de la salida: los hallazgos de sanidad.py y puertas.py verificar no salen en «es» en un proyecto «en»",
                  not lineas_es and not any(idioma_de(t_) == "es" for t_ in solo_es), lineas_es[:5])
    if celda.get("salida") == "cp1252":
        reg.check("salida con PYTHONIOENCODING=cp1252: sin UnicodeEncodeError en ningún comando",
                  not any("UnicodeEncodeError" in c["err"] for c in reg.log), [c["cmd"] for c in reg.log if "UnicodeEncodeError" in c["err"]][:3])
    return repo


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bmad", default="6.12.4", choices=BMADS); ap.add_argument("--idioma", default="es", choices=("es", "en"))
    ap.add_argument("--python", help="intérprete (defecto: el que corre este archivo)"); ap.add_argument("--deps", default="completas", choices=("completas", "minimas"))
    ap.add_argument("--salida-cp", default="utf-8", choices=("utf-8", "cp1252")); ap.add_argument("--ruta", default="simple", choices=("simple", "espacios"))
    ap.add_argument("--cierre", default="normal", choices=("normal", "prematuro")); ap.add_argument("--dir", help="carpeta de trabajo (se conserva)")
    a = ap.parse_args()
    import tempfile
    base = a.dir or tempfile.mkdtemp(prefix="pm-ciclo-")
    celda = {"python_ruta": a.python or interpretes()["3.13"], "deps": a.deps, "bmad": a.bmad, "idioma": a.idioma, "salida": a.salida_cp,
             "ruta": a.ruta, "cierre": a.cierre}
    reg = Registro("ciclo", "ciclo", os.path.join(base, "registro"))
    recorrer(celda, base, reg)
    reg.guardar_log()
    r = reg.resumen()
    print(f"\nResultado: {r['ok']} OK · {r['fallo']} FALLO · omisiones {[o['clave'] for o in r['omisiones']]} · {len(r['trazas'])} trazas · {base}")
    sys.exit(1 if r["fallo"] or r["trazas"] else 0)


if __name__ == "__main__":
    main()
