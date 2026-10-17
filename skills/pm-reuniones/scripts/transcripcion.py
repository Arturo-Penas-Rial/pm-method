#!/usr/bin/env python3
"""Normaliza transcripciones de reuniones (WebVTT, SRT, TXT con "Nombre: texto", DOCX) y calcula participación agregada.
Normalize meeting transcripts (VTT, SRT, TXT, DOCX) and compute aggregate participation.

Uso / Usage:
  python3 transcripcion.py reunion.vtt --salida 03-control/reuniones/2026-10-17-comite.md [--anonimizar] [--json]
Salida: Markdown con intervenciones "**[hh:mm:ss] Hablante:** texto" y una tabla de participación (palabras y % por hablante,
duración si hay tiempos). --anonimizar reemplaza nombres por P1, P2… (recomendado antes de cualquier análisis de clima).
Privacidad: el script no infiere emociones ni evalúa personas; solo cuenta palabras y turnos.
"""
IDIOMA = 'es'
import argparse, json, os, re, sys

TS = r"(?:(\d{1,2}):)?(\d{1,2}):(\d{2})[.,](\d{1,3})"

def seg(m):
    h, mi, s, ms = m.groups(); return int(h or 0) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000

def fmt(t): t = int(t or 0); return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"

def leer(p):
    if p.lower().endswith(".docx"):
        try: from docx import Document
        except ImportError: sys.exit("Falta python-docx para leer .docx")
        return "\n".join(par.text for par in Document(p).paragraphs)
    return open(p, encoding="utf-8-sig", errors="replace").read()

def parse_vtt_srt(txt):
    turnos = []; bloques = re.split(r"\n\s*\n", txt.replace("\r", ""))
    for b in bloques:
        lineas = [l for l in b.split("\n") if l.strip()]
        idx = next((i for i, l in enumerate(lineas) if "-->" in l), None)
        if idx is None: continue
        ts = re.findall(TS, lineas[idx])
        ini = fin = None
        ms = list(re.finditer(TS, lineas[idx]))
        if ms: ini = seg(ms[0]); fin = seg(ms[-1]) if len(ms) > 1 else ini
        texto = " ".join(lineas[idx + 1:])
        hablante = ""
        m = re.match(r"^<v\s+([^>]+)>(.*)$", texto)
        if m: hablante, texto = m.group(1).strip(), m.group(2)
        texto = re.sub(r"</?v[^>]*>|</?[ibuc][^>]*>", "", texto).strip()
        if not hablante:
            m = re.match(r"^([A-ZÁÉÍÓÚÑ][\w .'\-]{1,40}):\s+(.*)$", texto)
            if m: hablante, texto = m.group(1).strip(), m.group(2)
        if texto: turnos.append({"ini": ini, "fin": fin, "hablante": hablante or "?", "texto": texto})
    return turnos

def parse_txt(txt):
    turnos = []; actual = None
    for l in txt.replace("\r", "").split("\n"):
        if not l.strip(): continue
        m = re.match(r"^\s*\[?((?:\d{1,2}:)?\d{1,2}:\d{2})\]?\s*[-–]?\s*([^:]{1,40}):\s*(.*)$", l) or None
        if m:
            p = [int(x) for x in m.group(1).split(":")]; t = p[-1] + 60 * p[-2] + (3600 * p[-3] if len(p) == 3 else 0)
            actual = {"ini": t, "fin": None, "hablante": m.group(2).strip(), "texto": m.group(3).strip()}; turnos.append(actual); continue
        m = re.match(r"^\s*([A-ZÁÉÍÓÚÑ][\w .'\-]{1,40}):\s+(.*)$", l)
        if m:
            actual = {"ini": None, "fin": None, "hablante": m.group(1).strip(), "texto": m.group(2).strip()}; turnos.append(actual); continue
        m = re.match(r"^\s*([A-ZÁÉÍÓÚÑ][\w .'\-]{1,40})\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*$", l)   # exportes tipo "Nombre   0:05"
        if m:
            p = [int(x) for x in m.group(2).split(":")]; t = p[-1] + 60 * p[-2] + (3600 * p[-3] if len(p) == 3 else 0)
            actual = {"ini": t, "fin": None, "hablante": m.group(1).strip(), "texto": ""}; turnos.append(actual); continue
        if actual: actual["texto"] = (actual["texto"] + " " + l.strip()).strip()
        else: actual = {"ini": None, "fin": None, "hablante": "?", "texto": l.strip()}; turnos.append(actual)
    return [t for t in turnos if t["texto"]]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("--salida"); ap.add_argument("--anonimizar", action="store_true"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--idioma", choices=["es", "en"], default="es")
    a = ap.parse_args()
    global IDIOMA; IDIOMA = a.idioma
    txt = leer(a.entrada)
    turnos = parse_vtt_srt(txt) if ("-->" in txt) else parse_txt(txt)
    if not turnos: sys.exit("No se reconocieron intervenciones en la transcripción.")
    # fusionar turnos consecutivos del mismo hablante
    fus = []
    for t in turnos:
        if fus and fus[-1]["hablante"] == t["hablante"]: fus[-1]["texto"] += " " + t["texto"]; fus[-1]["fin"] = t["fin"] or fus[-1]["fin"]
        else: fus.append(dict(t))
    alias = {}
    if a.anonimizar:
        for t in fus:
            if t["hablante"] not in alias: alias[t["hablante"]] = f"P{len(alias) + 1}"
            t["hablante"] = alias[t["hablante"]]
    stats = {}
    for t in fus:
        s = stats.setdefault(t["hablante"], {"turnos": 0, "palabras": 0}); s["turnos"] += 1; s["palabras"] += len(t["texto"].split())
    total = sum(s["palabras"] for s in stats.values()) or 1
    tiempos = [x for t in turnos for x in (t["ini"], t["fin"]) if x is not None]
    dur = (max(tiempos) - min(tiempos)) if len(tiempos) > 1 else None
    resumen = {"archivo": os.path.basename(a.entrada), "intervenciones": len(fus), "hablantes": len(stats), "duracion": fmt(dur) if dur else "",
               "participacion": {h: {**s, "pct_palabras": round(100 * s["palabras"] / total, 1)} for h, s in sorted(stats.items(), key=lambda kv: -kv[1]["palabras"])},
               "anonimizado": a.anonimizar}
    if a.salida:
        fm = ["---", "tipo: transcripcion-normalizada", f'idioma: {IDIOMA}', "estado: borrador", f"fuente: {os.path.basename(a.entrada)}",
              f"anonimizado: {'si' if a.anonimizar else 'no'}", "---", "", f"# Transcripción normalizada · {os.path.basename(a.entrada)}", ""]
        tabla = ["| Hablante | Turnos | Palabras | % |", "|---|---|---|---|"] + [f"| {h} | {s['turnos']} | {s['palabras']} | {s['pct_palabras']} |" for h, s in resumen["participacion"].items()]
        cuerpo = [f"**[{fmt(t['ini'])}] {t['hablante']}:** {t['texto']}" if t["ini"] is not None else f"**{t['hablante']}:** {t['texto']}" for t in fus]
        os.makedirs(os.path.dirname(a.salida) or ".", exist_ok=True)
        open(a.salida, "w", encoding="utf-8").write("\n".join(fm) + "\n" + "\n".join(tabla) + f"\n\nDuración: {resumen['duracion'] or 'sin tiempos'} · Intervenciones: {len(fus)}\n\n" + "\n\n".join(cuerpo) + "\n")
    if a.json or not a.salida: print(json.dumps(resumen, ensure_ascii=False, indent=2))
    else: print(f"{len(fus)} intervenciones de {len(stats)} hablantes → {a.salida}")

if __name__ == "__main__":
    main()
