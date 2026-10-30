"""Construye el spot de pm-method: línea de tiempo, audio (música + locución), cuadros, MP4, SRT y guion con tiempos.

    python3 construir.py [--sin-voz] [--fps 30] [--tmp DIR] [--hasta SEG] [--cuadros 1.5,7,...]

Lee guion.json (frases y, en «pantalla», las cifras y la versión que muestran los cuadros) y voz/duraciones.json
(generado por voz.py), compone la música (musica.py), renderiza spot.html cuadro a
cuadro con Playwright (Chromium) y codifica con ffmpeg (H.264 yuv420p + AAC, +faststart). Salidas en ../:
  pm-method-spot.mp4          locución + música + subtítulos incrustados
  pm-method-spot-sin-voz.mp4  música + subtítulos (con --sin-voz o --ambas)
  pm-method-spot.srt          subtítulos aparte
  pm-method-spot-guion.txt    guion de locución con tiempos (para grabar con voz propia)
Requiere: Python 3.9+, numpy, scipy, soundfile, playwright (python -m playwright install chromium) y ffmpeg.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from musica import componer  # noqa: E402

SR = 48000
W, H = 1080, 1350


def linea_de_tiempo():
    g = json.load(open(os.path.join(AQUI, "guion.json"), encoding="utf-8"))
    d = json.load(open(os.path.join(AQUI, "voz", "duraciones.json"), encoding="utf-8"))["duraciones"]
    t = 0.0
    escenas, subs = [], []
    for e in g["escenas"]:
        dv = d[e["id"]]
        dur = max(e["min"], e["pre"] + dv + e["post"])
        v0 = t + e["pre"]
        escenas.append({"id": e["id"], "inicio": round(t, 3), "fin": round(t + dur, 3), "voz_ini": round(v0, 3),
                        "voz_fin": round(v0 + dv, 3), "texto": e["texto"].replace(" | ", " "),
                        "tts": e["tts"].replace(" | ", " ")})
        # subtítulos: cortes marcados con " | ", tiempo proporcional a los caracteres pronunciados (tts)
        tx, ts = e["texto"].split(" | "), e["tts"].split(" | ")
        assert len(tx) == len(ts), e["id"]
        tot = sum(len(x) for x in ts)
        c = v0
        for i, (a, b) in enumerate(zip(tx, ts)):
            dd = dv * len(b) / tot
            fin = c + dd + (0.25 if i == len(tx) - 1 else 0.0)
            subs.append({"ini": round(c - 0.05, 3), "fin": round(fin, 3), "texto": a})
            c += dd
        t += dur
    # evitar solapes entre cortes consecutivos
    for a, b in zip(subs, subs[1:]):
        a["fin"] = min(a["fin"], b["ini"])
    # cifras y rótulo de versión que muestra spot.html (guion.json → pantalla)
    return {"total": round(t, 3), "escenas": escenas, "subtitulos": subs, "pantalla": g.get("pantalla", {})}


def mezcla(lt, con_voz=True, pistas=False):
    m = componer(lt, SR).astype(np.float64)
    n = m.shape[0]
    voz = np.zeros(n)
    if con_voz:
        for e in lt["escenas"]:
            s, sr = sf.read(os.path.join(AQUI, "voz", e["id"] + ".flac"), dtype="float64")
            s = resample_poly(s, SR, sr)
            s = sosfilt(butter(2, 90 / (SR / 2), "high", output="sos"), s)
            i0 = int(e["voz_ini"] * SR)
            s = s[: max(0, n - i0)]
            voz[i0:i0 + len(s)] += s
        voz /= max(1e-9, np.abs(voz).max())
        voz *= 10 ** (-3 / 20)
        # ducking: envolvente de la voz suavizada (ataque 60 ms, liberación 350 ms) → −9 dB a la música
        act = (np.abs(voz) > 0.02).astype(float)
        k = int(0.35 * SR)
        act = np.convolve(act, np.ones(k) / k, mode="same") > 0.02
        g = np.where(act, 10 ** (-9 / 20), 1.0)
        g = sosfilt(butter(1, 3 / (SR / 2), "low", output="sos"), g)
        musica = m * g[:, None] * 10 ** (-4 / 20)
    else:
        musica = m * 10 ** (-1 / 20)
    if pistas:
        return musica, voz
    x = musica + voz[:, None]
    return (x / max(1.0, np.abs(x).max() / 0.98)).astype(np.float32)


def normalizar(entrada, salida):
    """loudnorm en dos pasadas: −14 LUFS integrados, pico verdadero −1,5 dBTP."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", entrada, "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    js = r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1]
    m = json.loads(js)
    f = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
         "measured_thresh={input_thresh}:offset={target_offset}:linear=true").format(**m)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", entrada, "-af", f, "-ar", str(SR),
                    salida], check=True)


def cuadros(lt, fps, destino_ffmpeg=None, instantes=None, carpeta=None, hasta=None):
    from playwright.sync_api import sync_playwright
    url = "file://" + os.path.join(AQUI, "spot.html")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(url)
        pg.wait_for_function("window.listo === true")
        pg.evaluate("lt => { window.LT = lt; }", lt)
        pg.evaluate("document.fonts.ready.then(()=>true)")
        pg.wait_for_load_state("networkidle")
        if instantes:
            for t in instantes:
                pg.evaluate(f"window.render({t})")
                pg.screenshot(path=os.path.join(carpeta, f"cuadro_{t:06.2f}.png"))
            b.close()
            return
        total = int(round((hasta or lt["total"]) * fps))
        for i in range(total):
            pg.evaluate(f"window.render({i / fps})")
            destino_ffmpeg.stdin.write(pg.screenshot(type="jpeg", quality=94))
            if i % (fps * 5) == 0:
                print(f"  cuadro {i}/{total}", flush=True)
        b.close()


def srt(lt, ruta):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(ruta, "w", encoding="utf-8") as f:
        for i, s in enumerate(lt["subtitulos"], 1):
            f.write(f"{i}\n{ts(s['ini'])} --> {ts(s['fin'])}\n{s['texto']}\n\n")


def guion_txt(lt, ruta):
    def mmss(x):
        return f"{int(x // 60):d}:{x % 60:05.2f}"
    filas = ["pm-method · spot para LinkedIn · guion de locución con tiempos",
             f"Duración total: {lt['total']:.1f} s · 1080×1350 · español (es-419), tono claro y seguro, ritmo ágil.",
             "Para grabar con voz propia: decir cada frase dentro de su ventana (inicio → fin de voz); la música y los",
             "cuadros ya están sincronizados con esas ventanas. Pronunciación: pm-method «pi em método», BMAD «bi-mad».",
             ""]
    for e in lt["escenas"]:
        filas.append(f"[{mmss(e['inicio'])} – {mmss(e['fin'])}] escena «{e['id']}» · voz {mmss(e['voz_ini'])} → "
                     f"{mmss(e['voz_fin'])} ({e['voz_fin'] - e['voz_ini']:.1f} s)")
        filas.append(f"    {e['texto']}")
        filas.append("")
    open(ruta, "w", encoding="utf-8").write("\n".join(filas))


def video(lt, fps, wav, mp4, tmp, hasta=None):
    dur = hasta or lt["total"]
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
           "-i", wav, "-t", f"{dur:.3f}",
           "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-profile:v", "high", "-level", "4.1",
           "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(fps * 2),
           "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
           "-movflags", "+faststart", "-metadata", "title=pm-method · spot", "-metadata", "language=spa", mp4]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cuadros(lt, fps, destino_ffmpeg=pr, hasta=hasta)
    pr.stdin.close()
    if pr.wait() != 0:
        sys.exit("ffmpeg falló")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--ambas", action="store_true", help="también la versión sin voz (música + subtítulos)")
    ap.add_argument("--solo-audio", action="store_true")
    ap.add_argument("--hasta", type=float, help="cortar a N segundos (pruebas)")
    ap.add_argument("--cuadros", help="solo exportar PNG de estos instantes (s, separados por coma) a --tmp")
    ap.add_argument("--tmp")
    a = ap.parse_args()
    tmp = a.tmp or tempfile.mkdtemp(prefix="spot-")
    os.makedirs(tmp, exist_ok=True)
    lt = linea_de_tiempo()
    json.dump(lt, open(os.path.join(tmp, "linea_de_tiempo.json"), "w"), ensure_ascii=False, indent=1)
    print(f"duración {lt['total']:.2f} s · {len(lt['subtitulos'])} subtítulos")
    if a.cuadros:
        cuadros(lt, a.fps, instantes=[float(x) for x in a.cuadros.split(",")], carpeta=tmp)
        print("cuadros en", tmp)
        return
    versiones = [("pm-method-spot", True)] + ([("pm-method-spot-sin-voz", False)] if a.ambas else [])
    for nombre, con_voz in versiones:
        crudo, norm = os.path.join(tmp, nombre + "-crudo.wav"), os.path.join(tmp, nombre + ".wav")
        sf.write(crudo, mezcla(lt, con_voz), SR, subtype="FLOAT")
        normalizar(crudo, norm)
        print("audio", norm)
        if a.solo_audio:
            continue
        video(lt, a.fps, norm, os.path.join(SALIDA, nombre + ".mp4"), tmp, a.hasta)
        print("video", os.path.join(SALIDA, nombre + ".mp4"))
    if not a.solo_audio and not a.hasta:
        srt(lt, os.path.join(SALIDA, "pm-method-spot.srt"))
        guion_txt(lt, os.path.join(SALIDA, "pm-method-spot-guion.txt"))
    if not a.tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
