#!/usr/bin/env python3
"""Utilidad para registros CSV del proyecto (agregar, actualizar, listar, resumir) con validación contra el esquema.
CSV register utility (add, update, list, summarize) validated against the package schema.

Uso / Usage:
  python3 registro.py --proyecto ./p listar riesgos [--abiertos | --estado abierto] [--json]
  python3 registro.py --proyecto ./p agregar riesgos --campo evento="..." --campo probabilidad=3 --campo impacto=4 --campo propietario="..."
  python3 registro.py --proyecto ./p actualizar riesgos R-003 --campo estado=cerrado
  python3 registro.py --proyecto ./p resumen [--corte AAAA-MM-DD] [--json]
  python3 registro.py --proyecto ./p esquema riesgos        # columnas y valores permitidos
Registros y prefijos: riesgos R-, issues I-, cambios C-, decisiones D-, supuestos S-, lecciones L-,
stakeholders ST-, calidad Q-, acciones A-. Valores permitidos: ver esquema.py y pm-registros/templates/guia-registros.md.
"""
import argparse, os, sys, datetime, json
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
    for col in spec.get("enteros_1_5", []):
        v = fila.get(col, "")
        if v and not (v.isdigit() and 1 <= int(v) <= 5): errores.append(f"{col}='{v}' " + ("must be an integer 1–5" if en else "debe ser entero 1–5"))
    if errores and not forzar:
        sys.exit(("Validation:" if en else "Validación:") + "\n  - " + "\n  - ".join(errores)
                 + ("\n(use --forzar to record anyway; English aliases such as threat/high/open are accepted)" if en else "\n(usar --forzar para registrar igual; se aceptan alias en inglés como threat/high/open)"))
    return errores

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

def resumen(proyecto, corte=None):
    out = {}; hoy = corte or datetime.date.today().isoformat()
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
            r["top"] = [f"{f['id']} ({pts(f):g}, {nivel_riesgo(pts(f))}) {f.get('evento','')}" for f in sorted(ab, key=pts, reverse=True)[:5]]
        if reg == "acciones":
            r["vencidas"] = [f"{f['id']} {f.get('responsable','')} {f.get('fecha_compromiso','')}" for f in ab if f.get("fecha_compromiso") and f["fecha_compromiso"] < hoy]
            por_resp = {}
            for f in ab: por_resp[f.get("responsable") or "sin-responsable"] = por_resp.get(f.get("responsable") or "sin-responsable", 0) + 1
            r["abiertas_por_responsable"] = por_resp
        if reg == "issues":
            r["sin_responsable"] = [f["id"] for f in ab if not f.get("responsable")]
        out[reg] = r
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proyecto", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("listar"); l.add_argument("registro"); l.add_argument("--estado"); l.add_argument("--abiertos", action="store_true"); l.add_argument("--json", action="store_true")
    a = sub.add_parser("agregar"); a.add_argument("registro"); a.add_argument("--campo", action="append"); a.add_argument("--forzar", action="store_true")
    u = sub.add_parser("actualizar"); u.add_argument("registro"); u.add_argument("id"); u.add_argument("--campo", action="append"); u.add_argument("--forzar", action="store_true")
    r = sub.add_parser("resumen"); r.add_argument("--json", action="store_true"); r.add_argument("--corte", help="fecha de corte AAAA-MM-DD para vencidas (defecto: hoy); usar la misma que el informe o tablero")
    es = sub.add_parser("esquema"); es.add_argument("registro")
    args = ap.parse_args()
    global IDIOMA
    IDIOMA = E.idioma_de(args.proyecto)

    if args.cmd == "resumen":
        out = resumen(args.proyecto, args.corte); out["fecha_corte"] = args.corte or datetime.date.today().isoformat()
        print(json.dumps(out, ensure_ascii=False, indent=2)); return
    if args.registro not in E.REGISTROS:
        sys.exit(f"Registro desconocido / unknown register: {args.registro}. Opciones: {', '.join(E.REGISTROS)}")
    if args.cmd == "esquema":
        spec = E.REGISTROS[args.registro]
        print(f"{args.registro}: prefijo {spec['prefijo']}-, estado inicial {spec['estado_inicial']}")
        for c in spec["columnas"]:
            v = spec.get("valores", {}).get(c)
            print(f"  {c}" + (f": {', '.join(x for x in v if x)}" if v else (": entero 1–5" if c in spec.get('enteros_1_5', []) else "")))
        return
    if not os.path.exists(os.path.join(args.proyecto, "estado.json")):
        sys.exit(f"{args.proyecto} no es una carpeta de proyecto (falta estado.json). Crear con nuevo_proyecto.py.")
    p = E.asegurar_registro(args.proyecto, args.registro)   # crea o migra columnas nuevas
    cols, filas = E.leer_csv(p); spec = E.REGISTROS[args.registro]

    if args.cmd == "listar":
        sel = [f for f in filas if (not args.estado or f.get("estado") == args.estado)
               and (not args.abiertos or f.get("estado") in spec.get("abiertos", []))]
        if args.json: print(json.dumps(sel, ensure_ascii=False, indent=2))
        else:
            for f in sel: print(" | ".join(f"{k}={v}" for k, v in f.items() if v))
        return
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
        filas.append(fila); E.escribir_csv(p, cols, filas); print(fila["id"])
    elif args.cmd == "actualizar":
        for f in filas:
            if f.get("id") == args.id:
                f.update(campos); recalcular(args.registro, f); validar(args.registro, f, args.forzar)
                if f.get("estado") in ("cerrado", "resuelto", "completada") and "fecha_cierre" in cols and not f.get("fecha_cierre"):
                    f["fecha_cierre"] = datetime.date.today().isoformat()
                E.escribir_csv(p, cols, filas); print("ok"); return
        sys.exit(f"No se encontró / not found: {args.id}")

if __name__ == "__main__":
    main()
