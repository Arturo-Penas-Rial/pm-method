from base import *
import re, datetime
G = "gestion"

def escribir(repo, rel, texto):
    p = os.path.join(repo, G, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(texto)

def art(repo, clave, rel, estado="en-revision", version=None, texto=None):
    if texto or not os.path.exists(os.path.join(repo, G, rel)):
        escribir(repo, rel, texto or f"# {clave}\n\nContenido de ejemplo generado por la skill dueña (recorrido E2E).\n")
    v = f" --version {version}" if version else ""
    run(E(f'estado.py --proyecto {G} artefacto {clave} --ruta {rel} --estado {estado}{v}'), repo, mostrar=False)

def reg(repo, registro, **campos):
    args = " ".join(f'--campo "{k}={v}"' for k, v in campos.items())
    out = run(E(f'registro.py --proyecto {G} agregar {registro} {args}'), repo)
    m = re.search(r"\b([A-Z]{1,2}-\d{3})\b", out)
    return m.group(1) if m else None

def act(repo, registro, id_, **campos):
    args = " ".join(f'--campo "{k}={v}"' for k, v in campos.items())
    return run(E(f'registro.py --proyecto {G} actualizar {registro} {id_} {args}'), repo)

def puerta(repo, tipo, por, fecha, extra="", decision="aprobado", lista=True):
    run(E(f'puertas.py --proyecto {G} verificar {tipo}'), repo, ok=(0, 1, 2))
    if lista:
        run(E(f'puertas.py --proyecto {G} lista {tipo}'), repo, mostrar=False)
        run(E(f'puertas.py --proyecto {G} confirmar {tipo} --por "{por}"'), repo)
    return run(E(f'estado.py --proyecto {G} puerta {tipo} --decision {decision} --por "{por}" --fecha {fecha} {extra}'), repo)

def base_su(repo):
    """Proyecto creado, BMAD detectado, roles y tolerancias (equivale a los pasos de puesta en marcha)."""
    run(E(f'nuevo_proyecto.py --ruta {G} --nombre "Portal de autoservicio para socios" --idioma es --enfoque hibrido --ejecutivo "Laura Méndez" --gestor "Martín Suárez"'), repo)
    run(f'python3 {BMAD} --proyecto {G} detectar', repo, mostrar=False)
    run(f'python3 {BMAD} --proyecto {G} requisitos', repo, mostrar=False)
    run(E(f'estado.py --proyecto {G} rol usuario_senior="Sofía Ramírez" proveedor_senior="Diego Ferreira" product_owner="Sofía Ramírez" autoridad_cambio="Sofía Ramírez" aseguramiento="Andrea Costa" jefes_equipo="Lucía Benítez"'), repo, mostrar=False)
    run(E(f'estado.py --proyecto {G} agil cadencia_iteracion_dias=14 velocidad_referencia=8'), repo, mostrar=False)

def hasta_etapa2(repo, mostrar=False):
    """Atajo de preparación: artefactos mínimos y las tres primeras puertas (inicio, proyecto, etapa 2)."""
    for c, r in (("mandato", "00-direccion/mandato.md"), ("project-brief", "01-inicio/project-brief.md"),
                 ("business-case-esquematico", "00-direccion/business-case-esquematico.md"), ("plan-etapa-1", "02-planificacion/plan-etapa-1.md")):
        art(repo, c, r)
    puerta(repo, "autorizar-inicio", "Ejecutivo: Laura Méndez", "2026-10-30", "--fin 2026-11-27")
    art(repo, "business-case", "00-direccion/business-case.md", texto="# Business case\n\nBeneficios B-01 (desvío de consultas, SM-2) y B-02 (adopción, SM-1).\n")
    art(repo, "pid", "00-direccion/pid.md"); art(repo, "plan-proyecto", "02-planificacion/plan-proyecto.md")
    run(E(f'estado.py --proyecto {G} tolerancia --nivel proyecto "tiempo=±3 semanas" "costo=±8 %" "alcance=Must sin tolerancia" "riesgo=ningún riesgo alto sin respuesta"'), repo, mostrar=False)
    puerta(repo, "autorizar-proyecto", "Ejecutivo: Laura Méndez", "2026-11-27")
    run(f'python3 {BMAD} --proyecto {G} linea-base prd --version 1.0 --por "Ejecutivo: Laura Méndez"', repo, mostrar=mostrar)
    run(E(f'puertas.py --proyecto {G} preparacion-bmad --resultado CONCERNS --por "Arquitecto: Diego Ferreira" --fecha 2026-11-26 --nota "NFR-3 sin prueba de carga planificada"'), repo, mostrar=mostrar)
    art(repo, "plan-etapa-2", "02-planificacion/plan-etapa-2.md")
    puerta(repo, "autorizar-etapa", "Ejecutivo: Laura Méndez", "2026-11-27", '--etapa-nombre "Release 1" --fin 2027-03-05 --tol "tiempo=+2 semanas" "costo=±10 %"', decision="condicionado")

def escribir_csv(ruta, cab, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab); w.writeheader(); w.writerows(filas)

def reg_json(repo, *a):
    import json as _j
    r = subprocess.run(["python3", f"{EST}/registro.py", "--proyecto", G, *a, "--json"], cwd=repo, capture_output=True, text=True, check=True)
    return _j.loads(r.stdout)

def tablero(repo, corte, desde, hasta, proximo, objetivos, hitos, decisiones, iteraciones, comentario, fuentes, salida_png=None, actor=None, fecha_fija="", fecha_pronostico=""):
    """Receta de pm-visuales/references/guia.md §3: arma el JSON y reemplaza el bloque datos-tablero."""
    import json as _j, pathlib
    e = _j.load(open(os.path.join(repo, G, "estado.json"), encoding="utf-8"))
    datos = {"proyecto": e["proyecto"], "etapa": e["etapa_actual"]["nombre"], "enfoque_entrega": e["enfoque_entrega"],
             "idioma": e["idioma"], "estado": "borrador", "fecha_corte": corte, "periodo_desde": desde, "periodo_hasta": hasta,
             "proximo_hasta": proximo, "riesgos": reg_json(repo, "listar", "riesgos", "--abiertos"),
             "issues": reg_json(repo, "listar", "issues", "--abiertos"), "acciones": reg_json(repo, "listar", "acciones"),
             "resumen_registros": reg_json(repo, "resumen", "--corte", corte), "umbrales_riesgo": {"alto": 15, "medio": 6},
             "objetivos": objetivos, "hitos": hitos, "decisiones_pendientes": decisiones,
             "agil": {"iteraciones": iteraciones, "ventana_velocidad": 3, "fecha_fija": fecha_fija, "fecha_pronostico": fecha_pronostico, "must_en_riesgo": []},
             "comentario_gestor": comentario, "fuentes": fuentes, "fecha_generacion": corte, "confirmado_por": ""}
    T = f"{RAIZ}/skills/pm-visuales/templates/tablero-avance.html"
    html = pathlib.Path(T).read_text(encoding="utf-8")
    bloque = _j.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html = re.sub(r'(<script type="application/json" id="datos-tablero">)(.*?)(</script>)', lambda m: m.group(1) + bloque + m.group(3), html, count=1, flags=re.S)
    rel = f"03-control/reportes/{corte}-tablero-avance.html"
    escribir(repo, rel, html)
    run(E(f'estado.py --proyecto {G} artefacto tablero-avance --ruta {rel} --estado en-revision'), repo, mostrar=False)
    LOG.append((f"(pm-visuales arma el tablero con la receta de references/guia.md §3 → gestion/{rel})", f"riesgos abiertos {len(datos['riesgos'])} · issues {len(datos['issues'])} · acciones {len(datos['acciones'])} · iteraciones {len(iteraciones)}"))
    if salida_png:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("AVISO: playwright no está instalado; se omite la captura del tablero"); return os.path.join(repo, G, rel)
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1.5)
            url = "file://" + os.path.join(repo, G, rel) + (f"?actor={actor}" if actor else "")
            pg.goto(url); pg.wait_for_timeout(600); pg.screenshot(path=salida_png, full_page=True); b.close()
    return os.path.join(repo, G, rel)
