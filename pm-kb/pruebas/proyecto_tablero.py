"""Proyecto de pm-method armado con los scripts del núcleo para las pruebas del portal (probar_kb.py --con-base y
pantallas.py): dos puertas decididas (cada una congela el tablero previo), una instantánea manual, un cambio, una
acción vencida, un artefacto de circulación restringida y documentos HTML como los que dejan las skills externas de
pm-visuales (copias sintéticas: no se ejecuta código de esas skills) y una WBS de dos paquetes (productos del tablero). docs/PM-KB.md §12.

  crear(destino) → carpeta del proyecto (con la carpeta de gestión `gestion/`)
"""
import json, os, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NUCLEO = RAIZ / "skills" / "pm-estado-proyecto" / "scripts"
JUNTA = "Junta: Laura Méndez (ejecutiva)"
NOMBRE = "Portal de trámites en línea"

ARCHIFY = """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="generator" content="archify 3.2.0">
<title>WBS · Portal de trámites (BORRADOR)</title>
<style>body{font:15px system-ui;margin:0;padding:24px;background:#10141c;color:#e6e9ef}svg{max-width:100%}.nodo{fill:#24324a;stroke:#8db4ef}</style>
<script>document.documentElement.setAttribute("data-theme", "dark");</script>
</head><body><h1>WBS · Portal de trámites</h1>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" role="img" aria-label="WBS">
<rect class="nodo" x="150" y="10" width="120" height="36" rx="6"/><text x="210" y="33" fill="#fff" text-anchor="middle">1 Portal</text>
<rect class="nodo" x="20" y="90" width="120" height="36" rx="6"/><text x="80" y="113" fill="#fff" text-anchor="middle">1.1 Alta</text>
<rect class="nodo" x="280" y="90" width="120" height="36" rx="6"/><text x="340" y="113" fill="#fff" text-anchor="middle">1.2 Pagos</text>
</svg>
<p id="estado">sin script</p>
<script>document.getElementById("estado").textContent = "dibujado por el script del documento";
try { fetch("/api/estado").then(function () { document.title = "FUGA"; }, function () {}); } catch (e) {}
try { document.cookie; parent.document.title = "FUGA"; } catch (e) { document.getElementById("estado").textContent += " · aislado"; }</script>
</body></html>
"""
DIAGRAM_DESIGN = """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Riesgos de mayor exposición</title>
<style>:root{--color-paper:#f5f5f5;--color-ink:#2d3142}body{background:var(--color-paper);color:var(--color-ink);font:15px system-ui;padding:2rem}
.diagram-container{width:100%;overflow-x:auto}</style></head>
<body><div class="frame"><p class="eyebrow">Riesgos</p><h1>Riesgos de mayor exposición</h1>
<div class="diagram-container"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 120" role="img" aria-label="Riesgos">
<circle cx="80" cy="60" r="30" fill="#bf4520"/><text x="80" y="64" text-anchor="middle" fill="#fff">R-001</text>
<circle cx="200" cy="60" r="22" fill="#4f5d75"/><text x="200" y="64" text-anchor="middle" fill="#fff">R-002</text></svg></div></div></body></html>
"""
VE_FUENTE = """<!doctype html><html lang="es" data-register="instrument"><head><title>One-pager del brief · BORRADOR</title>
<link rel="stylesheet" href="kit.css" data-ve-kit></head><body><h1>One-pager del brief</h1><p>Beneficio B-1.</p></body></html>
"""
VE = """<!doctype html><html lang="es" data-register="instrument"><head><meta charset="utf-8"><title>One-pager del brief · BORRADOR</title>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;600&display=swap" rel="stylesheet">
<style data-ve-kit>body{font:16px system-ui;padding:24px}h1{font-size:28px}</style></head>
<body><h1>One-pager del brief</h1><p>Beneficio B-1: trámites en línea sin turnos.</p>
<script data-ve-kit>document.body.dataset.kit = "listo";</script></body></html>
"""
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 120"><circle cx="80" cy="60" r="30" fill="#bf4520"/></svg>\n'
PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                    "1f15c4890000000d49444154789c6360f8cfc000000301010018dd8db00000000049454e44ae426082")


def _py(script, *args, cwd):
    r = subprocess.run([sys.executable, str(NUCLEO / script), *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode not in (0, 1):
        raise RuntimeError(f"{script} {' '.join(args)}: rc={r.returncode} {(r.stdout + r.stderr)[-400:]}")
    return r


def _junta(g, tipo, cwd, arts=()):
    for art, ruta in arts:
        destino = Path(cwd) / g / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists():
            destino.write_text(f"---\ntipo: {art}\nestado: borrador\n---\n# {art}\nBeneficio B-1.\n", encoding="utf-8")
        _py("estado.py", "--proyecto", g, "artefacto", art, "--ruta", ruta, "--estado", "en-revision", cwd=cwd)
    _py("puertas.py", "--proyecto", g, "lista", tipo, cwd=cwd)
    _py("puertas.py", "--proyecto", g, "confirmar", tipo, "--por", JUNTA, cwd=cwd)


def crear(destino):
    d = Path(destino)
    d.mkdir(parents=True, exist_ok=True)
    g = "gestion"
    _py("nuevo_proyecto.py", "--ruta", g, "--nombre", NOMBRE, "--fecha", "2026-10-01", "--ejecutivo", "Laura Méndez", "--gestor", "Martín Suárez", cwd=d)
    _py("registro.py", "--proyecto", g, "agregar", "riesgos", "--campo", "evento=Demora del proveedor de firma digital", "--campo", "propietario=Martín Suárez", cwd=d)
    _py("registro.py", "--proyecto", g, "agregar", "acciones", "--campo", "descripcion=Revisar el contrato del proveedor", "--campo", "responsable=Ana Pérez",
        "--campo", "fecha_compromiso=2026-10-05", cwd=d)
    _junta(g, "autorizar-inicio", d, arts=[("project-brief", "01-inicio/project-brief.md")])
    _py("estado.py", "--proyecto", g, "puerta", "autorizar-inicio", "--decision", "aprobado", "--por", JUNTA, "--fecha", "2026-10-05", cwd=d)
    _junta(g, "autorizar-proyecto", d)
    _py("estado.py", "--proyecto", g, "puerta", "autorizar-proyecto", "--decision", "condicionado", "--por", JUNTA, "--fecha", "2026-10-20",
        "--condiciones", "presentar el plan de pruebas de carga", cwd=d)
    _py("registro.py", "--proyecto", g, "agregar", "cambios", "--campo", "titulo=Agregar pagos con tarjeta", "--campo", "solicitante=Ana Pérez",
        "--campo", "estado=pendiente-decision", cwd=d)
    (d / g / "02-planificacion" / "wbs.csv").write_text("codigo,nombre,tipo,responsable,esfuerzo_h,costo,ref\n1,Portal de trámites,producto,Martín Suárez,,,\n"
                                                       "1.1,Alta de usuarios,paquete,Ana Pérez,120,,\n1.2,Pagos en línea,paquete,Ana Pérez,200,,\n", encoding="utf-8")
    reservado = d / g / "00-direccion" / "tolerancias-y-autoridad.md"
    reservado.write_text("---\ncirculacion: restringida\n---\n# Tolerancias y autoridad\n\nLímites de la junta (reservado).\n", encoding="utf-8")
    _py("estado.py", "--proyecto", g, "artefacto", "tolerancias-y-autoridad", "--ruta", "00-direccion/tolerancias-y-autoridad.md", "--estado", "borrador", cwd=d)
    _py("tablero.py", "--proyecto", g, "congelar", "--etiqueta", "junta de octubre", "--por", JUNTA, cwd=d)
    vis = d / g / "02-planificacion" / "visuales"
    vis.mkdir(parents=True, exist_ok=True)
    (vis / "wbs.html").write_text(ARCHIFY, encoding="utf-8")
    (vis / "wbs.candidate.json").write_text(json.dumps({"meta": {"output": "wbs.html"}}), encoding="utf-8")
    (vis / "riesgos.html").write_text(DIAGRAM_DESIGN, encoding="utf-8")
    (vis / "riesgos.svg").write_text(SVG, encoding="utf-8")
    (vis / "riesgos.png").write_bytes(PNG)
    (vis / "one-pager-brief.src.html").write_text(VE_FUENTE, encoding="utf-8")
    (vis / "one-pager-brief.html").write_text(VE, encoding="utf-8")
    for clave, ruta in (("pbs-wbs", "02-planificacion/visuales/wbs.html"), ("riesgos-exposicion", "02-planificacion/visuales/riesgos.html"),
                        ("one-pager-brief", "02-planificacion/visuales/one-pager-brief.html")):
        _py("estado.py", "--proyecto", g, "artefacto", clave, "--ruta", ruta, "--estado", "borrador", cwd=d)
    import shutil
    shutil.rmtree(d / g / ".pm-bloqueo", ignore_errors=True)
    return d


if __name__ == "__main__":
    print(crear(sys.argv[1]))
