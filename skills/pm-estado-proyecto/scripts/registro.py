#!/usr/bin/env python3
"""Utilidad para registros CSV del proyecto (agregar, actualizar, listar, resumir) con validación contra el esquema.
CSV register utility (add, update, list, summarize) validated against the package schema.

Uso / Usage:
  python3 registro.py --proyecto ./p listar riesgos [--abiertos | --estado abierto] [--json]
  python3 registro.py --proyecto ./p agregar riesgos --campo evento="..." --campo probabilidad=3 --campo impacto=4 --campo propietario="..."
  python3 registro.py --proyecto ./p actualizar riesgos R-003 --campo estado=cerrado
  python3 registro.py --proyecto ./p resumen [--corte AAAA-MM-DD] [--max 25] [--json]   # listas de ids con tope; conteo completo en <lista>_total
  python3 registro.py --proyecto ./p esquema riesgos        # columnas y valores permitidos
  python3 registro.py --proyecto ./p historial [R-003 | riesgos | estado | P-001] [--desde AAAA-MM-DD] [--max 50] [--json]
  python3 registro.py --proyecto ./p reconocer riesgos --por "<rol: nombre>" --motivo "..."   # cambio fuera de los scripts, revisado
  python3 registro.py --proyecto ./p proponer riesgos [R-003] --campo estado=cerrado --por "agente: pm-riesgos" [--motivo "..."]
  python3 registro.py --proyecto ./p propuestas [--estado pendiente|todas|...] [--json]
  python3 registro.py --proyecto ./p aprobar P-001 --por "<rol: nombre>"      # una persona; se aplica, se reaplica o queda en conflicto
  python3 registro.py --proyecto ./p rechazar P-001 --por "<rol: nombre>" --motivo "..."
Bitácora (2.6.0): cada escritura de estado.json, de un registro o de una propuesta queda en <proyecto>/.bitacora.jsonl
(solo anexado, encadenada por huellas sha256; SPEC §1.10.16, sanidad BIT-01/BIT-02).
Registros y prefijos: riesgos R-, issues I-, cambios C-, decisiones D-, supuestos S-, lecciones L-,
stakeholders ST-, calidad Q-, acciones A-; maestro de interesados (opcionales, se crean al primer uso): estereotipos ET-,
preferencias PF-, raci RC-, envios EN-, personas PU-. Se validan claves foráneas (stakeholder_id, estereotipo), unicidad
(raci: elemento + stakeholder_id) y un solo A por elemento de la RACI.
En decisiones, reemplaza y conviven (D-###;…) se validan con vigencia.py: ids existentes, sin ciclos, y reemplazar exige
nivel igual o superior al de la reemplazada (regla de autoridad; no se omite con --forzar). Valores permitidos: ver esquema.py y pm-registros/templates/guia-registros.md.
"""
import argparse, os, re, sys, datetime, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esquema as E

def parse_campos(lst):
    d = {}
    for c in lst or []:
        if "=" not in c: sys.exit(f"Campo inválido (usar clave=valor) / invalid field: {c}")
        k, v = c.split("=", 1); d[k.strip()] = v.strip()
    return d

IDIOMA = "es"

def validar(reg, fila, forzar=False):
    spec = E.REGISTROS[reg]; errores = []; en = IDIOMA == "en"
    for col, permitidos in spec.get("valores", {}).items():
        v = fila.get(col, "")
        if v and v not in permitidos:
            cand = [x for x in E.ALIAS_EN.get(v.lower(), []) if x in permitidos]
            if cand: fila[col] = cand[0]; continue          # alias en inglés → valor canónico
            errores.append(f"{col}='{v}' " + ("not allowed; use: " if en else "no permitido; usar: ") + ", ".join(x for x in permitidos if x))
    for col, permitidos in spec.get("multivalor", {}).items():   # varios valores separados por «;» o «,» → «a;b» en el orden del esquema
        v = (fila.get(col) or "").strip()
        if not v: continue
        ok, malos = set(), []
        for x in (y.strip() for y in re.split(r"[;,]", v) if y.strip()):
            c = x if x in permitidos else next((a for a in E.ALIAS_EN.get(x.lower(), []) if a in permitidos), None)
            if c: ok.add(c)
            else: malos.append(x)
        if malos: errores.append(f"{col}='{', '.join(malos)}' " + ("not allowed; use one or more of: " if en else "no permitido; usar uno o más de: ") + ", ".join(permitidos))
        else: fila[col] = ";".join(x for x in permitidos if x in ok)
    for col in spec.get("enteros_1_5", []):
        v = fila.get(col, "")
        if v and not (v.isdigit() and 1 <= int(v) <= 5): errores.append(f"{col}='{v}' " + ("must be an integer 1–5" if en else "debe ser entero 1–5"))
    for col in spec.get("numericos", []):
        v = (fila.get(col, "") or "").strip()
        if v:
            try:
                if re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", v): raise ValueError   # 9.000 o 9,000: separador de miles ambiguo
                float(v.replace(",", "."))
            except ValueError: errores.append(f"{col}='{v}' " + ("must be a plain number such as 9000 (no currency or thousands separators)" if en else "debe ser un número simple como 9000 (sin moneda ni separador de miles)"))
    if errores and not forzar:
        sys.exit(("Validation:" if en else "Validación:") + "\n  - " + "\n  - ".join(errores)
                 + ("\n(use --forzar to record anyway; English aliases such as threat/high/open are accepted)" if en else "\n(usar --forzar para registrar igual; se aceptan alias en inglés como threat/high/open)"))
    return errores

def integridad(proyecto, reg, fila, filas, forzar=False):
    """Claves foráneas (refs), unicidad (unico) y 'uno por grupo' (uno_por) del esquema: se validan al escribir."""
    spec = E.REGISTROS[reg]; errores = []; en = IDIOMA == "en"
    for col, destino in spec.get("refs", {}).items():
        v = (fila.get(col) or "").strip()
        if not v: continue
        pd = E.ruta_registro(proyecto, destino)
        ids = {f.get("id") for f in E.leer_csv(pd)[1]} if os.path.exists(pd) else set()
        if v not in ids: errores.append(f"{col}='{v}' " + (f"does not exist in {destino}.csv" if en else f"no existe en {destino}.csv"))
    otros = [f for f in filas if f.get("id") != fila.get("id")]
    if spec.get("unico") and all(fila.get(c) for c in spec["unico"]):
        if any(all(f.get(c) == fila.get(c) for c in spec["unico"]) for f in otros):
            errores.append(("duplicate " if en else "duplicado ") + " + ".join(f"{c}={fila.get(c)}" for c in spec["unico"]) + (" (one row per combination; update the existing one)" if en else " (una fila por combinación: actualizar la existente)"))
    u = spec.get("uno_por")
    if u and fila.get("rol") == u["rol"]:
        if any(f.get("rol") == u["rol"] and f.get(u["grupo"]) == fila.get(u["grupo"]) for f in otros):
            errores.append((f"{u['grupo']} {fila.get(u['grupo'])} already has an '{u['rol']}' (exactly one; change the other row first)" if en else
                            f"{u['grupo']} {fila.get(u['grupo'])} ya tiene un '{u['rol']}' (exactamente uno: cambiar primero la otra fila)"))
    if errores and not forzar:
        sys.exit(("Referential integrity:" if en else "Integridad referencial:") + "\n  - " + "\n  - ".join(errores))
    return errores

def _monto_txt(x):
    return f"{x:,.0f}".replace(",", ".") if IDIOMA != "en" else f"{x:,.0f}"

def control_cambio(proyecto, fila, filas, antes=None):
    """Autoridad y presupuesto de cambio (PRINCE2, tema Issues; SPEC §1.10.6). Al dejar un cambio aprobado (decision=aprobado
    o estado aprobado/implementado/cerrado) con costo > 0, rechaza:
      - decidido_por que no es la junta ni el ejecutivo (E.es_junta, el mismo criterio que CAM-04/CAM-05) y
        a) costo > presupuestos.limite_autoridad_cambio, o
        b) cargo=presupuesto-cambio y lo ya cargado + costo > presupuestos.cambio, o
        c) cargo=reserva-gestion o plan-excepcion (fuentes que solo libera la junta);
      - la junta o el ejecutivo con cargo=presupuesto-cambio que no alcanza: debe indicar la fuente (reserva-gestion,
        plan-excepcion) o ampliar antes el presupuesto (estado.py presupuesto cambio=… --por …, decisión registrada).
    Sin presupuesto de cambio fijado se registra con un aviso (sanidad CAM-03). No se omite con --forzar: es una regla de
    autoridad, no de formato. Solo se evalúa cuando la escritura aprueba el cambio o modifica costo, cargo o decidido_por
    de uno ya aprobado, de modo que actualizar otros campos de filas históricas sigue funcionando."""
    if not E.cambio_vigente(fila): return
    if antes is not None and E.cambio_vigente(antes) and all((antes.get(k) or "") == (fila.get(k) or "") for k in ("costo", "cargo", "decidido_por")): return
    costo = E.monto(fila.get("costo"))
    if not costo or costo <= 0: return
    e = E.cargar_estado(proyecto); t = lambda es, en: E.t(IDIOMA, es, en)
    quien = fila.get("decidido_por") or ""; junta = E.es_junta(e, quien)
    errores, aviso = motivos_autoridad(e, fila, filas, junta)
    if aviso: print(aviso, file=sys.stderr)
    escalar = t("Dejar estado=pendiente-decision (sin decision=aprobado) y escalar a pm-director: decide la junta o el ejecutivo.",
                "Leave estado=pendiente-decision (no decision=aprobado) and escalate to pm-director: the board or executive decides.")
    fuente = t("Indicar la fuente: cargo=reserva-gestion o plan-excepcion, o ampliar antes el presupuesto de cambio "
               "(pm-director: estado.py presupuesto cambio=<monto> --por \"<rol: nombre>\", queda la decisión registrada) y volver a registrar.",
               "State the source: cargo=reserva-gestion or plan-excepcion, or first raise the change budget "
               "(pm-director: estado.py presupuesto cambio=<amount> --por \"<role: name>\", recorded as a decision) and record again.")
    if errores:
        sys.exit(t("Control de cambios (PRINCE2, autoridad y presupuesto de cambio; no se omite con --forzar):",
                   "Change control (PRINCE2, change authority and budget; --forzar does not override it):") + "\n  - " + "\n  - ".join(errores)
                 + "\n  → " + (fuente if junta else t(f"'{quien or '(sin decidido_por)'}' no es la junta ni el ejecutivo. ", f"'{quien or '(no decidido_por)'}' is neither the board nor the executive. ") + escalar))

def motivos_autoridad(e, fila, filas, junta):
    """Regla de autoridad y presupuesto de cambio de control_cambio como función pura (la reutiliza
    pm-issues-cambios/scripts/impacto.py para decir quién decide antes de pedir la decisión). Devuelve (errores, aviso):
    errores = motivos por los que `junta` (True: la junta o el ejecutivo; False: la autoridad delegada) no puede dejar
    aprobado el cambio `fila` con su costo y cargo; aviso = texto si se carga al presupuesto de cambio sin que la junta
    lo haya fijado (no bloquea)."""
    pres = e.get("presupuestos") or {}; t = lambda es, en: E.t(IDIOMA, es, en)
    costo = E.monto(fila.get("costo")) or 0.0; cargo = fila.get("cargo") or ""; cid = fila.get("id")
    m = _monto_txt; errores = []; aviso = ""
    if costo <= 0: return errores, aviso
    lim = E.monto(pres.get("limite_autoridad_cambio"))
    if not junta and lim is not None and costo > lim:
        errores.append(t(f"{cid}: costo {m(costo)} supera el límite de la autoridad de cambio ({m(lim)}).",
                         f"{cid}: cost {m(costo)} exceeds the change authority limit ({m(lim)})."))
    if not junta and cargo in ("reserva-gestion", "plan-excepcion"):
        errores.append(t(f"{cid}: cargo={cargo} solo lo autoriza la junta o el ejecutivo.",
                         f"{cid}: cargo={cargo} can only be authorised by the board or executive."))
    if cargo == "presupuesto-cambio":
        tope = E.monto(pres.get("cambio")); usado = E.consumo_cambios(filas, excluir=cid)["presupuesto-cambio"]
        if tope is None:
            aviso = t(f"Aviso: {cid} se carga al presupuesto de cambio, pero la junta no lo fijó; no se controla el saldo (sanidad CAM-03). pm-director: estado.py presupuesto cambio=<monto> --por …",
                      f"Warning: {cid} is charged to the change budget, but the board has not set it; the balance is not checked (health CAM-03). pm-director: estado.py presupuesto cambio=<amount> --por …")
        elif usado + costo > tope:
            saldo = t(f"el presupuesto de cambio no alcanza: {m(usado)} ya cargados + {m(costo)} = {m(usado + costo)} de {m(tope)} fijados por la junta",
                      f"the change budget is not enough: {m(usado)} already charged + {m(costo)} = {m(usado + costo)} of {m(tope)} set by the board")
            errores.append(f"{cid}: {saldo}.")
    return errores, aviso

def control_vigencia(proyecto, fila, filas, forzar=False):
    """Columnas reemplaza y conviven de decisiones.csv (vigencia.py; pm-direccion-decisiones regla 12): ids D-###
    existentes, sin ciclos ni reemplazos dobles (se omiten con --forzar) y autoridad: reemplazar exige nivel igual o
    superior al de la reemplazada y que quien decide tenga esa autoridad (esquema.nivel_autoridad; no se omite con --forzar)."""
    if not ((fila.get("reemplaza") or "").strip() or (fila.get("conviven") or "").strip()): return
    import vigencia as V
    for col in ("reemplaza", "conviven"):      # forma canónica: D-001;D-002
        if fila.get(col): fila[col] = ";".join(dict.fromkeys(x.upper() for x in V.lista_ids(fila[col])))
    t = lambda es, en: E.t(IDIOMA, es, en)
    formato, autoridad = V.motivos_reemplazo(E.cargar_estado(proyecto), fila, filas, IDIOMA)
    if autoridad:
        sys.exit(t("Vigencia de decisiones (autoridad; no se omite con --forzar):", "Decision validity (authority; --forzar does not override it):") + "\n  - " + "\n  - ".join(autoridad + formato)
                 + "\n  → " + t("Una decisión posterior de nivel inferior no deja sin efecto la de un nivel superior: llevarla a quien tiene ese nivel "
                                 "(junta o capa de negocio: pm-director, estado.py puerta decision-ad-hoc --por …) y marcar reemplaza en la decisión que registre.",
                                 "A later decision at a lower level does not supersede a higher-level one: take it to that level (board: pm-director) and mark reemplaza on the decision it records."))
    if formato and not forzar:
        sys.exit(t("Vigencia de decisiones:", "Decision validity:") + "\n  - " + "\n  - ".join(formato) + t("\n(usar --forzar para registrar igual)", "\n(use --forzar to record anyway)"))

def recalcular(reg, f):
    if reg != "riesgos": return
    try: f["puntuacion"] = str(int(f["probabilidad"]) * int(f["impacto"])) if f.get("probabilidad") and f.get("impacto") else f.get("puntuacion", "")
    except ValueError: pass
    try:
        if f.get("impacto_monetario") and f.get("probabilidad"):
            # valor esperado aproximado: probabilidad de la escala 1–5 mapeada a 10/30/50/70/90 %
            pct = {1: .1, 2: .3, 3: .5, 4: .7, 5: .9}[int(f["probabilidad"])]
            f["valor_esperado"] = f"{float(f['impacto_monetario']) * pct:.0f}"
    except (ValueError, KeyError): pass

UMBRALES = {"alto": E.UMBRAL_RIESGO_ALTO, "medio": E.UMBRAL_RIESGO_MEDIO}

def nivel_riesgo(p):
    return "alto" if p >= UMBRALES["alto"] else ("medio" if p >= UMBRALES["medio"] else "bajo")

TOPE_LISTAS = 25   # ids por lista en `resumen` (control del contexto); el conteo completo va en <lista>_total

def corto(x, n=120):
    x = " ".join(str(x or "").split())
    return x if len(x) <= n else x[:n - 1] + "…"

def acotar(r, campos, maximo):
    """Recorta cada lista a `maximo` elementos (0 = sin tope) y agrega <campo>_total con el conteo completo."""
    recortado = False
    for c in campos:
        if c in r:
            r[c + "_total"] = len(r[c])
            if maximo and len(r[c]) > maximo: r[c] = r[c][:maximo]; recortado = True
    return recortado

def resumen(proyecto, corte=None, maximo=TOPE_LISTAS):
    out = {}; hoy = corte or datetime.date.today().isoformat(); recortes = []
    try:  # umbrales propios del enfoque de riesgo, si se declararon en estado.json.umbrales_riesgo
        u = E.cargar_estado(proyecto).get("umbrales_riesgo") or {}
        UMBRALES.update({k: float(v) for k, v in u.items() if k in UMBRALES and str(v).strip()})
    except SystemExit: pass
    for reg, spec in E.REGISTROS.items():
        p = E.ruta_registro(proyecto, reg)
        if not os.path.exists(p): continue
        cols, filas = E.leer_csv(p)
        r = {"total": len(filas)}
        if "estado" in cols:
            por = {}
            for f in filas: por[f.get("estado") or "sin-estado"] = por.get(f.get("estado") or "sin-estado", 0) + 1
            r["por_estado"] = por
            ab = [f for f in filas if f.get("estado") in spec.get("abiertos", [])]
            r["abiertos"] = len(ab)
        if reg == "riesgos":
            def pts(f):
                try: return float(f.get("puntuacion") or 0)
                except ValueError: return 0
            r["altos_abiertos"] = sum(1 for f in ab if pts(f) >= UMBRALES["alto"])
            r["umbrales"] = dict(UMBRALES)
            r["sin_respuesta"] = [f["id"] for f in ab if not f.get("respuesta")]
            r["sin_propietario"] = [f["id"] for f in ab if not f.get("propietario")]
            r["top"] = [f"{f['id']} ({pts(f):g}, {nivel_riesgo(pts(f))}) {corto(f.get('evento',''))}" for f in sorted(ab, key=pts, reverse=True)[:5]]
        if reg == "acciones":
            r["vencidas"] = [f"{f['id']} {f.get('responsable','')} {f.get('fecha_compromiso','')}" for f in ab if f.get("fecha_compromiso") and f["fecha_compromiso"] < hoy]
            por_resp = {}
            for f in ab: por_resp[f.get("responsable") or "sin-responsable"] = por_resp.get(f.get("responsable") or "sin-responsable", 0) + 1
            if maximo and len(por_resp) > maximo:      # los responsables con más acciones; el resto se suma en "otros"
                orden = sorted(por_resp.items(), key=lambda kv: (-kv[1], kv[0])); por_resp = dict(orden[:maximo])
                por_resp["otros"] = por_resp.get("otros", 0) + sum(v for _, v in orden[maximo:]); recortes.append("acciones.abiertas_por_responsable")
            r["abiertas_por_responsable"] = por_resp
        if reg == "issues":
            r["sin_responsable"] = [f["id"] for f in ab if not f.get("responsable")]
        if acotar(r, ("sin_respuesta", "sin_propietario", "vencidas", "sin_responsable"), maximo): recortes.append(reg)
        out[reg] = r
    if recortes:
        out["recortado"] = {"tope": maximo, "en": recortes, "nota": "listas con más elementos que el tope: ver <lista>_total o usar --max 0 / lists capped: see <list>_total or use --max 0"}
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("listar"); l.add_argument("registro"); l.add_argument("--estado"); l.add_argument("--abiertos", action="store_true"); l.add_argument("--json", action="store_true"); l.add_argument("--limite", type=int, default=60, help="máximo de filas en pantalla (0 = sin límite)")
    a = sub.add_parser("agregar"); a.add_argument("registro"); a.add_argument("--campo", action="append"); a.add_argument("--forzar", action="store_true")
    u = sub.add_parser("actualizar"); u.add_argument("registro"); u.add_argument("id"); u.add_argument("--campo", action="append"); u.add_argument("--forzar", action="store_true")
    r = sub.add_parser("resumen"); r.add_argument("--json", action="store_true"); r.add_argument("--corte", help="fecha de corte AAAA-MM-DD para vencidas (defecto: hoy); usar la misma que el informe o tablero")
    r.add_argument("--max", type=int, default=TOPE_LISTAS, help=f"tope de ids por lista (defecto {TOPE_LISTAS}; 0 = sin tope); el conteo completo va en <lista>_total")
    es = sub.add_parser("esquema"); es.add_argument("registro")
    agregar_subcomandos_bitacora(sub)     # historial, proponer, propuestas, aprobar, rechazar (2.6.0)
    args = ap.parse_args()
    global IDIOMA
    IDIOMA = E.idioma_de(args.proyecto)
    if args.cmd in COMANDOS_BITACORA:
        if not os.path.exists(os.path.join(args.proyecto, "estado.json")):
            sys.exit(f"{args.proyecto} no es una carpeta de proyecto (falta estado.json) / not a project folder.")
        COMANDOS_BITACORA[args.cmd](args); return

    if args.cmd == "resumen":
        out = resumen(args.proyecto, args.corte, args.max); out["fecha_corte"] = args.corte or datetime.date.today().isoformat()
        print(json.dumps(out, ensure_ascii=False, indent=2)); return
    if args.registro not in E.REGISTROS:
        sys.exit(f"Registro desconocido / unknown register: {args.registro}. Opciones: {', '.join(E.REGISTROS)}")
    if args.cmd == "esquema":
        spec = E.REGISTROS[args.registro]
        print(f"{args.registro}: prefijo {spec['prefijo']}-, estado inicial {spec['estado_inicial']}")
        for c in spec["columnas"]:
            v = spec.get("valores", {}).get(c); mv = spec.get("multivalor", {}).get(c)
            print(f"  {c}" + (f": {', '.join(x for x in v if x)}" if v else f": {'; '.join(mv)} (uno o más, separados por ;)" if mv else (": entero 1–5" if c in spec.get('enteros_1_5', []) else "")))
        return
    if not os.path.exists(os.path.join(args.proyecto, "estado.json")):
        sys.exit(f"{args.proyecto} no es una carpeta de proyecto (falta estado.json). Crear con nuevo_proyecto.py.")
    if args.cmd != "listar":
        with E.bloqueo(args.proyecto):    # lectura, id siguiente y escritura atómica bajo el bloqueo del proyecto
            p = E.asegurar_registro(args.proyecto, args.registro)
            cols, filas = E.leer_csv(p)
            modificar(args, p, cols, filas, E.REGISTROS[args.registro])
        return
    p = E.asegurar_registro(args.proyecto, args.registro)   # crea o migra columnas nuevas
    cols, filas = E.leer_csv(p); spec = E.REGISTROS[args.registro]

    if args.cmd == "listar":
        sel = [f for f in filas if (not args.estado or f.get("estado") == args.estado)
               and (not args.abiertos or f.get("estado") in spec.get("abiertos", []))]
        if args.json: print(json.dumps(sel, ensure_ascii=False, indent=2))
        else:
            for f in (sel[:args.limite] if args.limite else sel): print(" | ".join(f"{k}={v}" for k, v in f.items() if v))
            if args.limite and len(sel) > args.limite:
                print(f"… {len(sel) - args.limite} de {len(sel)} más sin mostrar: filtrar con --estado/--abiertos, usar 'resumen' o --limite 0 · "
                      f"{len(sel) - args.limite} of {len(sel)} more not shown")

def modificar(args, p, cols, filas, spec):
    """agregar / actualizar; el llamador tiene el bloqueo del proyecto (el id se calcula sobre el archivo releído)."""
    campos = parse_campos(args.campo)
    desconocidos = [k for k in campos if k not in cols]
    if desconocidos: sys.exit(f"Columnas inexistentes / unknown columns: {desconocidos}. Columnas: {cols}")
    if args.cmd == "agregar":
        fila = {c: "" for c in cols}; fila.update(campos)
        fila["id"] = fila.get("id") or E.siguiente_id(args.registro, filas)
        for fc in ("fecha", "fecha_identificacion"):
            if fc in cols and not fila.get(fc): fila[fc] = datetime.date.today().isoformat()
        if "estado" in cols and not fila.get("estado") and spec.get("estado_inicial"): fila["estado"] = spec["estado_inicial"]
        recalcular(args.registro, fila); validar(args.registro, fila, args.forzar)
        integridad(args.proyecto, args.registro, fila, filas, args.forzar)
        if args.registro == "cambios": control_cambio(args.proyecto, fila, filas)
        if args.registro == "decisiones": control_vigencia(args.proyecto, fila, filas, args.forzar)
        filas.append(fila); E.escribir_csv(p, cols, filas); print(fila["id"])
    elif args.cmd == "actualizar":
        for f in filas:
            if f.get("id") == args.id:
                antes = dict(f); f.update(campos); recalcular(args.registro, f); validar(args.registro, f, args.forzar)
                integridad(args.proyecto, args.registro, f, filas, args.forzar)
                if args.registro == "cambios": control_cambio(args.proyecto, f, filas, antes)
                if args.registro == "decisiones" and any((antes.get(k) or "") != (f.get(k) or "") for k in ("reemplaza", "conviven", "nivel", "decidido_por", "fecha")):
                    control_vigencia(args.proyecto, f, filas, args.forzar)
                if f.get("estado") in ("cerrado", "resuelto", "completada") and "fecha_cierre" in cols and not f.get("fecha_cierre"):
                    f["fecha_cierre"] = datetime.date.today().isoformat()
                E.escribir_csv(p, cols, filas); print("ok"); return
        sys.exit(f"No se encontró / not found: {args.id}")

# ---------------------------------------------------------------- bitácora y propuestas (2.6.0)
# Bitácora: esquema.anotar_bitacora anota cada escritura en <proyecto>/.bitacora.jsonl; aquí solo se lee (historial).
# Propuestas: un agente propone un cambio a un registro (03-control/propuestas/P-###.json, con la huella del registro y
# los valores base de los campos que toca); una persona lo aprueba con --por y se aplica con las mismas validaciones de
# agregar/actualizar. Si el registro cambió: se reaplica cuando ninguno de los campos tocados cambió (rebase); si alguno
# cambió a otro valor, queda en conflicto con la explicación (volver a proponer). SPEC §1.10.16.

def _t(es, en): return E.t(IDIOMA, es, en)

def _linea_historial(d, solo=None):
    """Texto de una línea de la bitácora; `solo` = id para mostrar solo sus cambios."""
    cab = f"#{d.get('n')} {(d.get('fecha') or '')[:16].replace('T', ' ')} · {d.get('script', '')} {d.get('operacion', '')}"
    if d.get("por"): cab += f" · --por {d['por']}"
    if d.get("propuesta"): cab += f" · {d['propuesta']}" + (_t(f" (propuso {d['propuesto_por']})", f" (proposed by {d['propuesto_por']})") if d.get("propuesto_por") else "")
    arch = d.get("archivo", ""); L = [cab + f" · {arch}"]
    if d.get("operacion") == "reconocer":
        L.append("    " + _t("cambio hecho fuera de los scripts, reconocido: ", "change made outside the scripts, acknowledged: ") + corto(d.get("motivo"), 200))
    if arch == "estado.json":
        L.append("    " + _t("claves: ", "keys: ") + (", ".join(d.get("claves") or []) or "—"))
    elif arch.startswith("03-control/propuestas/"):
        L.append("    " + _t("propuesta → ", "proposal → ") + f"{d.get('propuesta_estado', '')}" + (f" ({d.get('registro')} {' '.join(d.get('ids') or [])})" if d.get("registro") else ""))
    else:
        cambios = d.get("cambios") or {}; altas = set(d.get("altas") or [])
        for i in d.get("ids") or []:
            if solo and i != solo: continue
            if i in (d.get("bajas") or []): L.append(f"    {i}: " + _t("fila quitada", "row removed")); continue
            c = cambios.get(i)
            if isinstance(c, list): txt = ", ".join(c) + _t(" (valores no anotados: datos de interesados o confidenciales)", " (values not logged)")
            else: txt = "; ".join((f"{k}=«{v[1]}»" if i in altas else f"{k}: «{v[0]}» → «{v[1]}»") for k, v in (c or {}).items())
            L.append(f"    {i} " + (_t("alta", "added") + ": " if i in altas else "") + corto(txt, 240))
        if d.get("columnas_nuevas"): L.append("    " + _t("columnas nuevas: ", "new columns: ") + ", ".join(d["columnas_nuevas"]))
    L.append(f"    sha256 {(d.get('antes') or '—')[:12]} → {(d.get('despues') or '')[:12]}")
    return "\n".join(L)

def historial(a):
    """registro.py historial [ID|registro|estado|P-###] [--desde AAAA-MM-DD] [--max N] [--json]: escrituras anotadas en la
    bitácora (las más recientes al final) y verificación de la cadena y de la continuidad de cada archivo."""
    lineas, problemas = E.verificar_bitacora(a.proyecto, IDIOMA); o = a.objetivo; sel = lineas
    if o in E.REGISTROS: sel = [d for d in lineas if (d.get("archivo") or "") == f"03-control/registros/{o}.csv"]
    elif o in ("estado", "estado.json"): sel = [d for d in lineas if d.get("archivo") == "estado.json"]
    elif o and re.fullmatch(r"P-\d+", o): sel = [d for d in lineas if d.get("propuesta") == o or (d.get("archivo") or "").endswith(f"/{o}.json")]
    elif o: sel = [d for d in lineas if o in (d.get("ids") or [])]
    if a.desde: sel = [d for d in sel if (d.get("fecha") or "")[:10] >= a.desde]
    total = len(sel); mostrar = sel[-a.max:] if a.max else sel
    if a.json:
        print(json.dumps({"total": total, "lineas": mostrar, "lineas_bitacora": len(lineas),
                          "problemas": [{"codigo": c, "mensaje": m} for c, m in problemas]}, ensure_ascii=False, indent=2)); return
    if not lineas and not problemas:
        print(_t(f"Sin bitácora todavía ({E.ARCHIVO_BITACORA}): se crea con la primera escritura de un script desde 2.6.0.",
                 f"No write log yet ({E.ARCHIVO_BITACORA}): it starts with the first script write since 2.6.0.")); return
    if total > len(mostrar): print(_t(f"… {total - len(mostrar)} escrituras anteriores sin mostrar (--max 0 para todas)", f"… {total - len(mostrar)} earlier writes not shown (--max 0 for all)"))
    for d in mostrar: print(_linea_historial(d, o if o and o not in E.REGISTROS and not re.fullmatch(r"P-\d+|estado(\.json)?", o) else None))
    if not sel: print(_t(f"Ninguna escritura anotada para {o}.", f"No logged write for {o}."))
    if problemas:
        print(_t(f"Verificación: {len(problemas)} problema(s) (sanidad BIT):", f"Check: {len(problemas)} problem(s) (health BIT):"))
        for c, m in problemas[:TOPE_LISTAS]: print(f"  {c} {m}")
    else:
        print(_t(f"Verificación: cadena íntegra ({len(lineas)} líneas) y cada archivo coincide con su última escritura anotada.",
                 f"Check: chain intact ({len(lineas)} lines) and every file matches its last logged write."))

def _ruta_prop(proyecto, pid):
    if not re.fullmatch(r"P-\d+", pid or ""): sys.exit(_t(f"Id de propuesta inválido: {pid} (P-###).", f"Invalid proposal id: {pid} (P-###)."))
    return os.path.join(proyecto, E.DIR_PROPUESTAS, f"{pid}.json")

def _leer_prop(proyecto, pid):
    r = _ruta_prop(proyecto, pid)
    if not os.path.isfile(r): sys.exit(_t(f"No existe la propuesta {pid}.", f"Proposal {pid} not found."))
    return json.load(open(r, encoding="utf-8"))

def _plano(x): return " ".join(str(x or "").lower().split())

def _huella_fila(f): return E._sha(json.dumps(f, sort_keys=True, ensure_ascii=False).encode("utf-8"))

def proponer(a):
    """Crea P-### con los campos validados como en agregar/actualizar, la huella del registro y los valores base."""
    reg = a.registro
    if reg not in E.REGISTROS: sys.exit(f"Registro desconocido / unknown register: {reg}. Opciones: {', '.join(E.REGISTROS)}")
    campos = parse_campos(a.campo)
    if not campos: sys.exit(_t("Indicar al menos un --campo clave=valor.", "Give at least one --campo key=value."))
    with E.bloqueo(a.proyecto):
        p = E.asegurar_registro(a.proyecto, reg); cols, filas = E.leer_csv(p)
        desconocidos = [k for k in campos if k not in cols]
        if desconocidos: sys.exit(f"Columnas inexistentes / unknown columns: {desconocidos}. Columnas: {cols}")
        base = {"huella_registro": E._sha(open(p, "rb").read())}
        if a.id:
            fila = next((f for f in filas if f.get("id") == a.id), None)
            if fila is None: sys.exit(_t(f"No se encontró {a.id} en {reg}.csv.", f"{a.id} not found in {reg}.csv."))
            prueba = dict(fila); prueba.update(campos)
            base.update(huella_fila=_huella_fila(fila), valores={c: fila.get(c, "") for c in campos})
        else:
            prueba = {c: "" for c in cols}; prueba.update(campos); prueba["id"] = prueba.get("id") or E.siguiente_id(reg, filas)
        recalcular(reg, prueba); validar(reg, prueba); integridad(a.proyecto, reg, prueba, filas)
        campos = {c: prueba.get(c, "") for c in campos}          # valores canónicos (alias en inglés resueltos)
        if a.id and all(fila.get(c, "") == v for c, v in campos.items()):
            sys.exit(_t(f"Nada que proponer: {a.id} ya tiene esos valores.", f"Nothing to propose: {a.id} already has those values."))
        d = os.path.join(a.proyecto, E.DIR_PROPUESTAS); os.makedirs(d, exist_ok=True)
        n = max([int(m.group(1)) for m in (re.fullmatch(r"P-(\d+)\.json", x) for x in os.listdir(d)) if m] or [0]) + 1
        pid = f"P-{n:03d}"
        prop = {"id": pid, "fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "estado": "pendiente",
                "registro": reg, "operacion": "actualizar" if a.id else "agregar", "objetivo": a.id or "", "campos": campos,
                "propuesto_por": a.por, "motivo": a.motivo or "", "base": base}
        E.contexto_bitacora(operacion="proponer", propuesta=pid, por=a.por)
        E.escribir_json(_ruta_prop(a.proyecto, pid), prop)
    print(pid)
    print(_t(f"Propuesta {pid} pendiente: la aprueba una persona con registro.py --proyecto {a.proyecto} aprobar {pid} --por \"<rol: nombre>\" (o rechazar {pid} --por … --motivo …).",
             f"Proposal {pid} pending: a person approves it with registro.py --proyecto {a.proyecto} aprobar {pid} --por \"<role: name>\" (or rechazar)."), file=sys.stderr)

def evaluar(prop, filas, huella):
    """Qué pasaría al aprobar: ('aplicar' | 'reaplicar' | 'conflicto', conflictos [(campo, base, hoy, propuesto)], detalle)."""
    base = prop.get("base") or {}; campos = prop.get("campos") or {}
    mismo = huella == base.get("huella_registro")
    if prop.get("operacion") == "agregar":
        return ("aplicar", [], "") if mismo else ("reaplicar", [], _t("el registro cambió desde la propuesta; el alta se reaplica sobre la versión actual, con el id siguiente y las validaciones de hoy",
                                                                       "the register changed since the proposal; the new row is reapplied on the current version"))
    fila = next((f for f in filas if f.get("id") == prop.get("objetivo")), None)
    if fila is None: return "conflicto", [], _t(f"la fila {prop.get('objetivo')} ya no existe", f"row {prop.get('objetivo')} no longer exists")
    if mismo: return "aplicar", [], ""
    vb = base.get("valores") or {}
    conf = [(c, vb.get(c, ""), fila.get(c, ""), v) for c, v in campos.items() if fila.get(c, "") != vb.get(c, "") and fila.get(c, "") != v]
    if conf:
        return "conflicto", conf, _t("cambiaron campos que la propuesta también toca: ", "fields the proposal also touches have changed: ") + "; ".join(
            _t(f"{c}: base «{b}», hoy «{h}», propuesto «{v}»", f"{c}: base «{b}», now «{h}», proposed «{v}»") for c, b, h, v in conf)
    otra = _huella_fila(fila) != base.get("huella_fila")
    return "reaplicar", [], (_t(f"{prop.get('objetivo')} cambió en otros campos; los propuestos siguen como en la base: se reaplica", f"{prop.get('objetivo')} changed in other fields; reapplied")
                             if otra else _t("cambiaron otras filas del registro; se reaplica", "other rows changed; reapplied"))

def _resolver(a, prop, estado, resultado, detalle, id_=""):
    prop["estado"] = estado
    prop["resolucion"] = {"fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "por": a.por,
                          "resultado": resultado, "id": id_, "detalle": detalle, **({"motivo": a.motivo} if getattr(a, "motivo", "") else {})}
    E.contexto_bitacora(operacion=a.cmd, propuesta=prop["id"], por=a.por, propuesto_por=prop.get("propuesto_por"))
    E.escribir_json(_ruta_prop(a.proyecto, prop["id"]), prop)

def aprobar(a):
    """Aplica la propuesta si la fuente no cambió o si se puede reaplicar; si hay conflicto la cierra con la explicación."""
    prop = _leer_prop(a.proyecto, a.propuesta)
    if prop.get("estado") != "pendiente": sys.exit(_t(f"{a.propuesta} ya está {prop.get('estado')}.", f"{a.propuesta} is already {prop.get('estado')}."))
    if _plano(a.por) == _plano(prop.get("propuesto_por")):
        sys.exit(_t(f"Quien aprueba debe ser una persona distinta de quien propuso ({prop.get('propuesto_por')}).",
                    f"The approver must be a person other than the proposer ({prop.get('propuesto_por')})."))
    reg = prop["registro"]
    with E.bloqueo(a.proyecto):
        p = E.asegurar_registro(a.proyecto, reg); cols, filas = E.leer_csv(p)
        res, _, detalle = evaluar(prop, filas, E._sha(open(p, "rb").read()))
        if res == "conflicto":
            _resolver(a, prop, "conflicto", "conflicto", detalle)
            sys.exit(_t(f"{a.propuesta} no se aplicó: {detalle}. Quedó en conflicto; volver a proponer sobre la versión actual (registro.py listar {reg}).",
                        f"{a.propuesta} not applied: {detalle}. Marked as conflict; propose again on the current version."))
        ns = argparse.Namespace(cmd=prop["operacion"], registro=reg, id=prop.get("objetivo") or "", proyecto=a.proyecto,
                                campo=[f"{k}={v}" for k, v in (prop.get("campos") or {}).items()], forzar=False)
        E.contexto_bitacora(operacion="aprobar", propuesta=prop["id"], por=a.por, propuesto_por=prop.get("propuesto_por"))
        try: modificar(ns, p, cols, filas, E.REGISTROS[reg])
        except SystemExit as x:
            if x.code not in (None, 0):
                print(_t(f"{a.propuesta} sigue pendiente: la aplicación no pasó las validaciones de registro.py (arriba).",
                         f"{a.propuesta} is still pending: applying it failed registro.py validations (above)."), file=sys.stderr)
            raise
        id_ = filas[-1]["id"] if prop["operacion"] == "agregar" else prop.get("objetivo")
        estado = "aplicada" if res == "aplicar" else "reaplicada"; _resolver(a, prop, estado, estado, detalle, id_)
    print(_t(f"{a.propuesta} {'aplicada' if res == 'aplicar' else 'reaplicada'} en {reg} {id_}" + (f": {detalle}" if detalle else ""),
             f"{a.propuesta} {'applied' if res == 'aplicar' else 'reapplied'} to {reg} {id_}" + (f": {detalle}" if detalle else "")), file=sys.stderr)

def rechazar(a):
    prop = _leer_prop(a.proyecto, a.propuesta)
    if prop.get("estado") != "pendiente": sys.exit(_t(f"{a.propuesta} ya está {prop.get('estado')}.", f"{a.propuesta} is already {prop.get('estado')}."))
    with E.bloqueo(a.proyecto): _resolver(a, prop, "rechazada", "rechazada", "")
    print(_t(f"{a.propuesta} rechazada por {a.por}.", f"{a.propuesta} rejected by {a.por}."))

def propuestas(a):
    """Lista las propuestas (pendientes por defecto) y, para las pendientes, qué pasaría al aprobarlas hoy."""
    d = os.path.join(a.proyecto, E.DIR_PROPUESTAS); out = []
    for x in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not re.fullmatch(r"P-\d+\.json", x): continue
        pr = json.load(open(os.path.join(d, x), encoding="utf-8"))
        if a.estado != "todas" and pr.get("estado") != a.estado: continue
        if pr.get("estado") == "pendiente":
            p = E.ruta_registro(a.proyecto, pr.get("registro", ""))
            filas = E.leer_csv(p)[1] if os.path.exists(p) else []
            res, _, det = evaluar(pr, filas, E._sha(open(p, "rb").read()) if os.path.exists(p) else "")
            pr["al_aprobar"] = {"resultado": res, "detalle": det}
        out.append(pr)
    if a.json: print(json.dumps(out, ensure_ascii=False, indent=2)); return
    if not out: print(_t(f"Sin propuestas ({a.estado}).", f"No proposals ({a.estado}).")); return
    for pr in out:
        print(f"{pr['id']} · {pr.get('estado')} · {pr.get('operacion')} {pr.get('registro')} {pr.get('objetivo') or ''}".rstrip()
              + f" · {_t('propuso', 'by')} {pr.get('propuesto_por')} · {(pr.get('fecha') or '')[:10]}")
        print("    " + corto("; ".join(f"{k}=«{v}»" for k, v in (pr.get("campos") or {}).items()), 240) + (f" · {_t('motivo', 'reason')}: {corto(pr['motivo'], 120)}" if pr.get("motivo") else ""))
        if pr.get("al_aprobar"):
            r = pr["al_aprobar"]
            print("    " + _t("al aprobar hoy: ", "if approved today: ") + {"aplicar": _t("se aplica tal cual", "applies as is"), "reaplicar": _t("se reaplica", "reapplied"),
                                                                             "conflicto": _t("conflicto", "conflict")}[r["resultado"]] + (f" ({r['detalle']})" if r["detalle"] else ""))
        elif pr.get("resolucion"):
            r = pr["resolucion"]; print("    " + f"{r.get('resultado')} · {r.get('por')} · {(r.get('fecha') or '')[:10]}" + (f" · {r.get('id')}" if r.get("id") else "")
                                         + (f" · {corto(r.get('detalle') or r.get('motivo'), 160)}" if r.get("detalle") or r.get("motivo") else ""))

def reconocer(a):
    """Una persona deja constancia de un cambio hecho fuera de los scripts (merge de git, corrección manual revisada)."""
    o = a.archivo
    rel = f"03-control/registros/{o}.csv" if o in E.REGISTROS else ("estado.json" if o in ("estado", "estado.json") else o.replace(os.sep, "/"))
    n = E.reconocer_bitacora(a.proyecto, rel, a.por, a.motivo)
    print(_t(f"{rel} ya coincide con la bitácora; nada que reconocer.", f"{rel} already matches the write log; nothing to acknowledge.") if n is None else
          _t(f"Línea {n} de la bitácora: {a.por} reconoce el cambio de {rel} hecho fuera de los scripts ({a.motivo}).",
             f"Write-log line {n}: {a.por} acknowledges the change to {rel} made outside the scripts."))

COMANDOS_BITACORA = {"reconocer": reconocer, "historial": historial, "proponer": proponer, "propuestas": propuestas, "aprobar": aprobar, "rechazar": rechazar}

def agregar_subcomandos_bitacora(sub):
    h = sub.add_parser("historial", help="escrituras anotadas en la bitácora (.bitacora.jsonl) y su verificación")
    h.add_argument("objetivo", nargs="?", help="id (R-003), registro (riesgos), estado o P-###; sin valor: todo")
    h.add_argument("--desde", help="AAAA-MM-DD (fecha real de la escritura)"); h.add_argument("--max", type=int, default=50, help="últimas N (0 = todas)")
    h.add_argument("--json", action="store_true")
    pr = sub.add_parser("proponer", help="propone un alta (sin id) o un cambio (con id); lo aprueba una persona")
    pr.add_argument("registro"); pr.add_argument("id", nargs="?"); pr.add_argument("--campo", action="append")
    pr.add_argument("--por", required=True, help="quién propone, p. ej. \"agente: pm-planificacion\""); pr.add_argument("--motivo", default="")
    ps = sub.add_parser("propuestas", help="lista propuestas y qué pasaría al aprobarlas hoy")
    ps.add_argument("--estado", default="pendiente", choices=["pendiente", "aplicada", "reaplicada", "conflicto", "rechazada", "todas"]); ps.add_argument("--json", action="store_true")
    ap_ = sub.add_parser("aprobar", help="una persona aprueba la propuesta: se aplica, se reaplica o queda en conflicto")
    ap_.add_argument("propuesta"); ap_.add_argument("--por", required=True, help="\"<rol: nombre>\" de la persona que aprueba")
    rj = sub.add_parser("rechazar"); rj.add_argument("propuesta"); rj.add_argument("--por", required=True); rj.add_argument("--motivo", required=True)
    rc = sub.add_parser("reconocer", help="deja constancia en la bitácora de un cambio hecho fuera de los scripts (cierra BIT-02)")
    rc.add_argument("archivo", help="registro (riesgos), estado o ruta relativa (03-control/propuestas/P-001.json)")
    rc.add_argument("--por", required=True); rc.add_argument("--motivo", required=True)

if __name__ == "__main__":
    main()
