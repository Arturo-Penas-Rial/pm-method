"""Música original del spot, sintetizada con numpy y scipy (sin samples ni material de terceros).

Pad de cuerdas sintéticas (sierras desafinadas filtradas), bajo, pulso suave (bombo senoidal y ticks de ruido
filtrado), arpegio de pulsos en la escena de prueba, barridos de ruido en los cambios de escena y un acorde final que
resuelve. Progresión Si m – Sol – Re – La a 96 BPM. Todo depende de la línea de tiempo que arma construir.py.

    from musica import componer
    estereo = componer(linea_de_tiempo, sr=48000)   # ndarray (n, 2) float32, pico ≈ −6 dBFS
"""
import numpy as np
from scipy.signal import butter, sosfilt

BPM = 96.0
BEAT = 60.0 / BPM
# progresión (MIDI de la fundamental y tipo): Bm, G, D, A — dos compases (8 tiempos) por acorde
PROG = [(47, "m"), (43, "M"), (50, "M"), (45, "M")]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def acorde(root, tipo):
    t3 = 3 if tipo == "m" else 4
    return [root + 12, root + 12 + t3, root + 19, root + 24, root + 24 + t3]


def lp(x, f, sr, orden=2):
    return sosfilt(butter(orden, f / (sr / 2), "low", output="sos"), x)


def hp(x, f, sr, orden=2):
    return sosfilt(butter(orden, f / (sr / 2), "high", output="sos"), x)


def bp(x, f1, f2, sr):
    return sosfilt(butter(2, [f1 / (sr / 2), f2 / (sr / 2)], "band", output="sos"), x)


def sierra(f, t, armonicos=None, sr=48000):
    """Sierra de banda limitada por suma aditiva (sin aliasing)."""
    n = armonicos or max(1, int(min(6000, sr / 2 - 1000) / f))
    y = np.zeros_like(t)
    for k in range(1, n + 1):
        y += np.sin(2 * np.pi * f * k * t) / k
    return y * (2 / np.pi)


def env_ar(n, sr, a, r):
    e = np.ones(n)
    na, nr = int(a * sr), int(r * sr)
    if na:
        e[:na] = np.linspace(0, 1, na) ** 2
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def componer(lt, sr=48000, semilla=7):
    rng = np.random.default_rng(semilla)
    total = lt["total"]
    N = int(total * sr)
    L = np.zeros(N)
    R = np.zeros(N)
    esc = {e["id"]: e for e in lt["escenas"]}
    t_giro = esc["giro"]["inicio"]
    t_ctrl = esc["controles"]["inicio"]
    t_prueba = esc["prueba"]["inicio"]
    t_cierre = esc["cierre"]["inicio"]

    def poner(sig, t0, pan=0.0, g=1.0):
        i0 = int(t0 * sr)
        if i0 >= N:
            return
        s = sig[: N - i0] * g
        L[i0:i0 + len(s)] += s * np.sqrt(0.5 * (1 - pan))
        R[i0:i0 + len(s)] += s * np.sqrt(0.5 * (1 + pan))

    # ---------- pad: un acorde cada 8 tiempos desde el giro; antes, un bordón tenso en Si
    bloque = 8 * BEAT
    # bordón del gancho (Si + Fa# graves, con un leve batido) y un ascenso de ruido hacia el giro
    d = t_giro + 0.4
    t = np.arange(int(d * sr)) / sr
    bord = sum(sierra(hz(m) * (1 + det), t, sr=sr) for m in (35, 42, 47) for det in (-0.004, 0.004))
    bord = lp(bord, 600, sr) * env_ar(len(t), sr, 0.02, 0.6) * 0.10
    poner(bord, 0.0)
    sw = rng.standard_normal(len(t))
    sw = bp(sw, 400, 5000, sr) * np.linspace(0, 1, len(t)) ** 3 * env_ar(len(t), sr, 0, 0.35) * 0.05
    poner(sw, 0.0)
    # golpe grave al entrar el giro
    tk = np.arange(int(1.2 * sr)) / sr
    golpe = np.sin(2 * np.pi * (45 * tk + 40 * (1 - np.exp(-tk * 18)) / 18)) * np.exp(-tk * 4) * 0.45
    poner(golpe, t_giro)

    k = 0
    t0 = t_giro
    fin_pad = t_cierre
    while t0 < fin_pad - 0.05:
        root, tipo = PROG[k % len(PROG)]
        dur = min(bloque, fin_pad - t0) + 0.9
        t = np.arange(int(dur * sr)) / sr
        voces = acorde(root, tipo)
        for j, m in enumerate(voces):
            f = hz(m)
            for det, pan in ((-0.006, -0.6), (0.0, 0.0), (0.006, 0.6)):
                v = sierra(f * (1 + det), t, armonicos=12, sr=sr)
                v = lp(v, 1400 + 500 * (k % 2), sr) * env_ar(len(t), sr, 0.5, 0.9) * 0.022
                poner(v, t0, pan)
        # bajo
        b = np.sin(2 * np.pi * hz(root - 12) * t) + 0.25 * np.sin(2 * np.pi * hz(root) * t)
        pulso = 0.55 + 0.45 * np.exp(-((t % BEAT) / 0.22))
        poner(b * pulso * env_ar(len(t), sr, 0.05, 0.6) * 0.13, t0)
        t0 += bloque
        k += 1

    # ---------- pulso: bombo suave en 1 y 3 desde el giro; ticks desde los controles
    tk = np.arange(int(0.35 * sr)) / sr
    bombo = np.sin(2 * np.pi * (48 * tk + 90 * (1 - np.exp(-tk * 30)) / 30)) * np.exp(-tk * 11)
    bombo = lp(bombo, 900, sr) * 0.30
    tick = hp(rng.standard_normal(int(0.06 * sr)), 6500, sr) * np.exp(-np.arange(int(0.06 * sr)) / sr * 70) * 0.05
    t = t_giro
    i = 0
    while t < t_cierre - 0.1:
        if i % 2 == 0:
            poner(bombo, t)
        if t >= t_ctrl - 0.01:
            poner(tick, t + BEAT / 2, pan=0.3 if i % 2 else -0.3)
        if t >= t_prueba - 0.01:
            poner(tick * 0.6, t + BEAT / 4, pan=-0.2)
            poner(tick * 0.6, t + 3 * BEAT / 4, pan=0.2)
        t += BEAT
        i += 1

    # ---------- arpegio de pulsos en la escena de prueba (corcheas sobre el acorde vigente)
    t = t_prueba
    while t < t_cierre - 0.05:
        kk = int((t - t_giro) // bloque)
        root, tipo = PROG[kk % len(PROG)]
        notas = acorde(root, tipo)[1:4] + [acorde(root, tipo)[3] + 7]
        j = int(round((t - t_prueba) / (BEAT / 2)))
        f = hz(notas[j % len(notas)] + 12)
        tn = np.arange(int(0.28 * sr)) / sr
        p = (np.sin(2 * np.pi * f * tn) + 0.3 * np.sin(4 * np.pi * f * tn)) * np.exp(-tn * 14) * 0.06
        poner(p, t, pan=0.35 if j % 2 else -0.35)
        t += BEAT / 2

    # ---------- barridos en los cambios de escena (salvo el primero)
    for e in lt["escenas"][1:]:
        dsw = 0.55
        n = int(dsw * sr)
        x = rng.standard_normal(n)
        cortes = np.linspace(500, 7000, 8)
        y = np.zeros(n)
        seg = n // len(cortes)
        for c_i, c in enumerate(cortes):
            a, b = c_i * seg, min(n, (c_i + 1) * seg + seg)
            y[a:b] += bp(x[a:b], c * 0.6, min(c * 1.4, sr / 2 - 100), sr) * np.hanning(b - a)
        y *= np.linspace(0.2, 1, n) ** 2 * 0.035
        poner(y, max(0, e["inicio"] - dsw + 0.05), pan=0.0)

    # ---------- cierre: acorde de Re mayor con quinta arriba, cola larga
    dur = total - t_cierre
    t = np.arange(int(dur * sr)) / sr
    for m in (50, 57, 62, 66, 69, 74):
        for det, pan in ((-0.005, -0.5), (0.005, 0.5)):
            v = lp(sierra(hz(m) * (1 + det), t, armonicos=10, sr=sr), 1800, sr)
            poner(v * env_ar(len(t), sr, 0.08, min(2.5, dur * 0.6)) * 0.026, t_cierre, pan)
    poner(np.sin(2 * np.pi * hz(38) * t) * env_ar(len(t), sr, 0.03, min(2.5, dur * 0.6)) * 0.16, t_cierre)
    poner(golpe * 0.8, t_cierre)
    # campanita final (sinusoides inarmónicas suaves)
    tb = np.arange(int(2.0 * sr)) / sr
    campana = sum(np.sin(2 * np.pi * hz(86) * r * tb) * a for r, a in ((1, 1), (2.01, 0.4), (3.0, 0.2))) * np.exp(-tb * 2.5) * 0.04
    poner(campana, t_cierre + 0.05, pan=0.2)

    x = np.stack([L, R], axis=1)
    x = hp(x.T, 30, sr).T
    # fundido general de entrada y salida
    f_in, f_out = int(0.03 * sr), int(0.8 * sr)
    x[:f_in] *= np.linspace(0, 1, f_in)[:, None]
    x[-f_out:] *= np.linspace(1, 0, f_out)[:, None] ** 1.5
    x /= max(1e-9, np.abs(x).max())
    return (x * 10 ** (-6 / 20)).astype(np.float32)
