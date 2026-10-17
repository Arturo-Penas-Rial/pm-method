#!/usr/bin/env python3
"""Arma el paquete de puerta o de cierre (ZIP) con manifiesto, a partir de estado.json y la carpeta del proyecto.
Builds the gate or closure package (ZIP) with a manifest from estado.json and the project folder.

Solo biblioteca estándar. No convierte formatos: incluye los Markdown/CSV tal cual y, si existen en exportados/,
los .docx/.xlsx/.pptx más recientes del mismo tipo. Para convertir, usar antes exportar.py o las skills oficiales.

Uso / Usage:
  python3 paquete.py --proyecto ./p puerta autorizar-etapa [--salida exportados/2026-10-16-paquete-autorizar-etapa-v1.zip] [--extra ruta ...]
  python3 paquete.py --proyecto ./p cierre [--salida ...] [--extra ruta ...]
  python3 paquete.py --proyecto ./p listar puerta autorizar-proyecto     # muestra obligatorios/opcionales y qué falta, sin crear ZIP
Salida: ZIP con los artefactos + MANIFIESTO.md. Si falta un obligatorio o alguno sigue en borrador, el nombre lleva -BORRADOR (los productos que la puerta decide pueden ir "en-revision").
"""
import argparse, datetime, glob, json, os, re, sys, zipfile

# Claves canónicas de estado.json.artefactos (ver pm-estado-proyecto/SKILL.md, "Claves de artefactos") o patrones de
# archivo si no están registradas, por tipo de paquete. {n} = etapa actual, {n1} = siguiente etapa.
# Cada entrada: (clave, [patrones glob relativos al proyecto, en orden de preferencia], obligatorio)
# El documento de solicitud de decisión (pm-direccion-decisiones) usa la clave solicitud-<puerta>; el ZIP que genera
# este script se registra, si se desea, como exportado-paquete-<puerta> y nunca se reincluye.
PAQUETES = {
    "autorizar-inicio": [
        ("project-brief", ["01-inicio/project-brief.md", "01-inicio/*brief*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], False),  # esquemático: suele vivir en el brief
        ("estructura-organizativa", ["00-direccion/estructura-organizativa.md", "00-direccion/*estructura*.md"], True),
        ("plan-etapa-1", ["02-planificacion/plan-etapa-1*.md"], True),
        ("descripcion-producto-proyecto", ["02-planificacion/descripcion-producto-proyecto.md", "02-planificacion/productos/descripcion-producto-proyecto.md"], False),  # puede venir dentro del brief
        ("solicitud-autorizar-inicio", ["00-direccion/decisiones/*solicitud-autorizar-inicio*.md", "00-direccion/decisiones/*paquete-autorizar-inicio*.md"], False),
        ("canvas-arranque", ["01-inicio/*canvas*"], False),
        ("mandato", ["00-direccion/mandato.md", "01-inicio/mandato.md"], False),
    ],
    "autorizar-proyecto": [
        ("pid", ["00-direccion/pid.md", "00-direccion/*pid*.md", "01-inicio/*pid*.md", "01-inicio/*acta-constitucion*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("plan-proyecto", ["02-planificacion/plan-proyecto.md", "02-planificacion/*plan-proyecto*.md", "02-planificacion/*plan-de-proyecto*.md"], True),
        ("plan-etapa-{n1}", ["02-planificacion/plan-etapa-{n1}*.md"], True),
        ("enfoques", ["02-planificacion/enfoques/*.md"], False),
        ("pbs-wbs", ["02-planificacion/pbs-wbs.md", "02-planificacion/wbs.csv"], False),
        ("cronograma", ["02-planificacion/cronograma.md", "02-planificacion/cronograma.xml"], False),
        ("presupuesto", ["02-planificacion/presupuesto.md"], False),
        ("estrategia-adquisiciones", ["02-planificacion/adquisiciones/*estrategia*.md"], False),
        ("bmad-prd", ["00-direccion/historial/bmad-prd-v*/prd.md", "02-planificacion/especificacion/spec-index.json"], False),
        ("solicitud-autorizar-proyecto", ["00-direccion/decisiones/*solicitud-autorizar-proyecto*.md", "00-direccion/decisiones/*paquete-autorizar-proyecto*.md"], False),
        ("registros", ["03-control/registros/*.csv"], False),
    ],
    "autorizar-etapa": [
        ("informe-fin-etapa-{n}", ["03-control/reportes/*informe-fin-etapa-{n}*.md", "03-control/reportes/*informe-fin-etapa*.md", "03-control/reportes/*end-stage*.md"], True),
        ("plan-etapa-{n1}", ["02-planificacion/plan-etapa-{n1}*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("plan-proyecto", ["02-planificacion/plan-proyecto.md", "02-planificacion/*plan-proyecto*.md"], True),
        ("solicitud-autorizar-etapa", ["00-direccion/decisiones/*solicitud-autorizar-etapa*.md", "00-direccion/decisiones/*paquete-autorizar-etapa*.md"], False),
        ("registros", ["exportados/*registros*.xlsx", "03-control/registros/*.csv"], False),
        ("tablero-avance", ["03-control/reportes/*tablero-avance*.html"], False),
    ],
    "autorizar-plan-excepcion": [
        ("informe-excepcion", ["03-control/reportes/*informe-excepcion*.md"], True),
        ("plan-excepcion", ["02-planificacion/*plan-excepcion*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("plan-proyecto", ["02-planificacion/plan-proyecto.md", "02-planificacion/*plan-proyecto*.md"], False),
        ("evaluacion-excepcion", ["00-direccion/decisiones/*evaluacion-excepcion*.md"], False),
        ("solicitud-autorizar-plan-excepcion", ["00-direccion/decisiones/*solicitud-autorizar-plan-excepcion*.md", "00-direccion/decisiones/*paquete-autorizar-plan-excepcion*.md"], False),
        ("registros", ["exportados/*registros*.xlsx", "03-control/registros/*.csv"], False),
    ],
    "cierre": [
        ("informe-fin-proyecto", ["04-cierre/informe-fin-proyecto.md", "04-cierre/*fin-proyecto*.md"], True),
        ("registro-aceptacion", ["04-cierre/registro-aceptacion.md", "04-cierre/*aceptacion-producto-proyecto*.md", "04-cierre/*aceptacion*.md"], True),
        ("informe-lecciones", ["04-cierre/informe-lecciones.md", "04-cierre/*lecciones*.md"], True),
        ("recomendaciones-seguimiento", ["04-cierre/recomendaciones-seguimiento.md", "04-cierre/*seguimiento*.md", "04-cierre/*recomendaciones*.md"], True),
        ("plan-revision-beneficios", ["04-cierre/plan-revision-beneficios.md", "00-direccion/enfoque-beneficios.md"], True),
        ("business-case-original", ["00-direccion/historial/business-case-v1.0*.md", "00-direccion/historial/*business-case*1.0*.md"], True),
        ("business-case", ["00-direccion/business-case.md", "00-direccion/*business-case*.md"], True),
        ("pid-original", ["00-direccion/historial/pid-v1.0*.md", "00-direccion/historial/*pid*1.0*.md"], False),
        ("registros", ["exportados/*registros*.xlsx", "03-control/registros/*.csv"], True),
        ("solicitud-autorizar-cierre", ["00-direccion/decisiones/*solicitud-autorizar-cierre*.md", "00-direccion/decisiones/*paquete-autorizar-cierre*.md"], False),
        ("handover", ["04-cierre/handover.md", "04-cierre/*traspaso*.md"], False),
        ("cierre-contratos", ["04-cierre/cierre-contrato-*.md"], False),
        ("notificacion-cierre", ["04-cierre/notificacion-cierre.md"], False),
        ("acta-junta", ["00-direccion/decisiones/*acta-*.md"], False),
    ],
}
# Estados aceptables para presentar a la puerta: lo que se decide en la puerta puede venir "en-revision".
ESTADOS_OK = ("aprobado", "en-revision", "registro")

def frontmatter(path):
    """Devuelve dict con version/estado/aprobado_por/tipo del frontmatter YAML simple (o del comentario HTML)."""
    meta = {"version": "", "estado": "", "aprobado_por": "", "tipo": ""}
    try:
        txt = open(path, encoding="utf-8", errors="replace").read(4000)
    except OSError:
        return meta
    for k in meta:
        m = re.search(rf"^{k}:\s*\"?([^\"\n]*)\"?\s*$", txt, re.M)
        if m: meta[k] = m.group(1).strip()
    return meta

def _orden(k):
    return [(0, int(x), "") if x.isdigit() else (1, 0, x) for x in re.split(r"[-.]", k)]

def resolver(proyecto, estado, clave, patrones):
    """Busca el artefacto: estado.json.artefactos (clave exacta o numerada), luego patrones en orden de preferencia."""
    arts = estado.get("artefactos") or {}
    art = arts.get(clave)
    if not art:
        cand = sorted((k for k in arts if k.startswith(clave + "-") and not k.startswith("exportado-")), key=_orden)
        art = arts[cand[-1]] if cand else None
    if art and art.get("ruta") and os.path.exists(os.path.join(proyecto, art["ruta"])):
        return [os.path.join(proyecto, art["ruta"])], art
    for p in patrones:
        hallados = [h for h in glob.glob(os.path.join(proyecto, p)) if not h.endswith(".zip")]
        if not hallados: continue
        if clave in ("registros", "enfoques"):
            xlsx = sorted((h for h in hallados if h.endswith(".xlsx")), key=os.path.getmtime)
            return (xlsx[-1:] if xlsx else sorted(hallados)), None
        return [max(hallados, key=os.path.getmtime)], None
    return [], None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("puerta"); p.add_argument("tipo", choices=[k for k in PAQUETES if k != "cierre"]); p.add_argument("--salida"); p.add_argument("--extra", nargs="*", default=[])
    c = sub.add_parser("cierre"); c.add_argument("--salida"); c.add_argument("--extra", nargs="*", default=[])
    l = sub.add_parser("listar"); l.add_argument("clase", choices=["puerta", "cierre"]); l.add_argument("tipo", nargs="?")
    a = ap.parse_args()

    f_estado = os.path.join(a.proyecto, "estado.json")
    if not os.path.exists(f_estado): sys.exit("No existe estado.json; ejecutar nuevo_proyecto.py")
    estado = json.load(open(f_estado, encoding="utf-8"))

    if a.cmd == "listar":
        tipo = "cierre" if a.clase == "cierre" else (a.tipo or sys.exit("Indicar tipo de puerta"))
    else:
        tipo = "cierre" if a.cmd == "cierre" else a.tipo
    if tipo not in PAQUETES: sys.exit(f"Tipo desconocido: {tipo}")

    filas, faltan, no_aprobados = [], [], []
    n = int((estado.get("etapa_actual") or {}).get("numero") or 0)
    defs = [(c.format(n=n, n1=n + 1), [x.format(n=n, n1=n + 1) for x in pats], o) for c, pats, o in PAQUETES[tipo]]
    if estado.get("enfoque_entrega") == "agil":   # perfil ágil mínimo: la visión con el MVP sustituye a la descripción del producto del proyecto
        defs = [(c, pats + ["01-inicio/declaracion-vision.md", "01-inicio/*vision*.md"], o) if c == "descripcion-producto-proyecto" else (c, pats, o) for c, pats, o in defs]
    for clave, patrones, oblig in defs:
        rutas, art = resolver(a.proyecto, estado, clave, patrones)
        if not rutas:
            filas.append((clave, "", clave, "", "FALTA" if oblig else "no incluido", "obligatorio" if oblig else "opcional", ""))
            if oblig: faltan.append(clave)
            continue
        for r in rutas:
            es_doc = r.endswith((".md", ".html"))
            meta = frontmatter(r) if es_doc else {"version": "", "estado": "", "aprobado_por": "", "tipo": ""}
            est = (art or {}).get("estado") or meta["estado"] or ("registro" if r.endswith((".csv", ".xlsx")) else "sin-estado")
            ver = (art or {}).get("version") or meta["version"] or ""
            if est not in ESTADOS_OK and oblig: no_aprobados.append(f"{clave} ({est})")
            filas.append((clave, os.path.relpath(r, a.proyecto), meta["tipo"] or clave, ver, est, "obligatorio" if oblig else "opcional", meta["aprobado_por"] or ""))
    for e in getattr(a, "extra", []) or []:
        if os.path.exists(e):
            meta = frontmatter(e) if e.endswith((".md", ".html")) else {"version": "", "estado": "", "aprobado_por": "", "tipo": ""}
            filas.append(("extra", os.path.relpath(e, a.proyecto) if e.startswith(a.proyecto) else e, meta["tipo"] or "extra", meta["version"], meta["estado"] or "sin-estado", "opcional", meta["aprobado_por"]))
        else:
            print(f"Aviso: no existe {e}")

    borrador = bool(faltan or no_aprobados)
    hoy = datetime.date.today().isoformat()
    cabecera = [f"# Manifiesto del paquete · Package manifest", "",
                f"**Proyecto / Project:** {estado.get('proyecto','')}  ", f"**Paquete / Package:** {tipo}  ",
                f"**Generado / Generated:** {hoy} con asistencia de IA (automatización: consolidación de archivos existentes)  ",
                f"**ESTADO DEL PAQUETE / PACKAGE STATUS:** {'BORRADOR / DRAFT — ' + '; '.join(['faltan: ' + ', '.join(faltan)] if faltan else []) + ('; ' if faltan and no_aprobados else '') + ('en borrador: ' + ', '.join(no_aprobados) if no_aprobados else '') if borrador else 'COMPLETO PARA LA PUERTA / READY FOR THE GATE (fuentes aprobadas o en revisión)'}", "",
                "| Archivo en el ZIP / File | Origen / Source | Tipo / Type | Versión / Version | Estado / Status | Oblig. | Aprobado por / Approved by |", "|---|---|---|---|---|---|---|"]
    for clave, ruta, t, ver, est, oblig, apr in filas:
        nombre = os.path.basename(ruta) if ruta else f"({clave})"
        cabecera.append(f"| {nombre} | {ruta or '—'} | {t} | {ver} | {est} | {oblig} | {apr} |")
    cabecera += ["", "> Este paquete no constituye aprobación. La decisión de la puerta la toma una persona con rol en la junta y se registra con `estado.py puerta` y en `decisiones.csv`."]
    manifiesto = "\n".join(cabecera) + "\n"

    if a.cmd == "listar":
        print(manifiesto); return

    salida = a.salida or os.path.join(a.proyecto, "exportados", f"{hoy}-paquete-{tipo}-v1{'-BORRADOR' if borrador else ''}.zip")
    if borrador and "BORRADOR" not in os.path.basename(salida):
        base, ext = os.path.splitext(salida); salida = f"{base}-BORRADOR{ext}"
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("MANIFIESTO.md", manifiesto)
        for clave, ruta, *_ in filas:
            if not ruta: continue
            src = ruta if os.path.isabs(ruta) else os.path.join(a.proyecto, ruta)
            z.write(src, arcname=os.path.join(clave, os.path.basename(ruta)))
    print(f"Escrito {salida}")
    if faltan: print("Faltan obligatorios:", ", ".join(faltan))
    if no_aprobados: print("En borrador:", ", ".join(no_aprobados))

if __name__ == "__main__":
    main()
