"""Genera la locución del spot con Kokoro-82M (kokoro-onnx), una frase por escena.

Uso:  python voz.py --modelo DIR_CON_kokoro-v1.0.onnx_Y_voices-v1.0.bin [--voz em_alex]
Salida: voz/<id>.flac (24 kHz, mono) y voz/duraciones.json. Las locuciones generadas quedan versionadas, así que
construir.py no necesita el modelo (≈ 350 MB). Requiere: pip install kokoro-onnx==0.6.1 soundfile.
"""
import argparse, json, os
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

AQUI = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument("--modelo", required=True)
ap.add_argument("--voz")
a = ap.parse_args()
g = json.load(open(os.path.join(AQUI, "guion.json"), encoding="utf-8"))
cfg = g["voz"]
voz = a.voz or cfg["voz"]
k = Kokoro(os.path.join(a.modelo, "kokoro-v1.0.onnx"), os.path.join(a.modelo, "voices-v1.0.bin"))
dur = {}
os.makedirs(os.path.join(AQUI, "voz"), exist_ok=True)
for e in g["escenas"]:
    s, sr = k.create(e["tts"].replace(" | ", " "), voice=voz, speed=cfg["velocidad"], lang=cfg["idioma"])
    s = np.asarray(s, dtype=np.float32)
    # recorta silencios de borde (umbral −50 dBFS) y deja 30 ms
    idx = np.where(np.abs(s) > 10 ** (-50 / 20))[0]
    pad = int(0.03 * sr)
    s = s[max(0, idx[0] - pad): idx[-1] + pad]
    sf.write(os.path.join(AQUI, "voz", e["id"] + ".flac"), s, sr)
    dur[e["id"]] = round(len(s) / sr, 3)
    print(f'{e["id"]:<11} {dur[e["id"]]:5.2f} s  {k.tokenizer.phonemize(e["tts"].replace(" | ", " "), cfg["idioma"])}')
json.dump({"voz": voz, "sr": sr, "duraciones": dur}, open(os.path.join(AQUI, "voz", "duraciones.json"), "w"), indent=1)
print("total voz", round(sum(dur.values()), 2), "s")
