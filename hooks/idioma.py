#!/usr/bin/env python3
"""Hook UserPromptSubmit de pm-method: si la carpeta de trabajo tiene un proyecto pm-method (estado.json a ≤ 2 niveles)
y el pedido está escrito en otro idioma que el del proyecto (español/inglés), agrega al contexto la instrucción de
responder en el idioma del pedido. Las skills y los scripts están en español, y sin este recordatorio el modelo a veces
contesta en español a un pedido en inglés. No decide nada ni bloquea; ante cualquier error, no imprime nada."""
import glob, json, os, re, sys

EN = r"\b(the|and|is|are|what|how|please|show|set|up|from|with|we|our|my|me|this|next|project|report|plan|risk|stage|board)\b"
ES = r"\b(el|la|los|las|qué|cómo|por|favor|mostrame|armá|hacé|con|del|nuestro|mi|este|esta|siguiente|proyecto|informe|riesgo|etapa|junta|que)\b"

def idioma_de(texto):
    t = texto.lower()
    en, es = len(re.findall(EN, t)), len(re.findall(ES, t))
    if en >= 2 and en > 1.5 * es: return "en"
    if es >= 2 and es > 1.5 * en: return "es"
    return None

def main():
    try: d = json.load(sys.stdin)
    except Exception: return
    prompt = d.get("prompt") or ""
    if prompt.lstrip().startswith("/") and len(prompt.split()) < 3: return
    pedido = idioma_de(prompt)
    if not pedido: return
    cwd = d.get("cwd") or os.getcwd()
    cands = [os.path.join(cwd, "estado.json")] + glob.glob(os.path.join(cwd, "*", "estado.json")) + glob.glob(os.path.join(cwd, "*", "*", "estado.json"))
    for c in cands:
        try:
            e = json.load(open(c, encoding="utf-8"))
        except Exception:
            continue
        if "proceso_actual" not in e: continue
        if e.get("idioma", "es") != pedido:
            msg = ("pm-method: the user wrote this request in English. Reply in English (artifacts stay in the project "
                   f"language '{e.get('idioma', 'es')}' unless the user asks otherwise)." if pedido == "en" else
                   "pm-method: el usuario escribió este pedido en español. Responder en español (los artefactos siguen en el "
                   f"idioma del proyecto '{e.get('idioma')}' salvo que pida otro).")
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}}, ensure_ascii=False))
        return

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
