"""Gráficos estáticos (PNG 1600×900, 16:9) para las guías E2E, los guiones de clase y las diapositivas del webinar.

Se generan desde los datos reales de cada recorrido (registros CSV, salidas de cpm.py y evm.py), así que se regeneran
al correr `correr.py`. Paleta de referencia validada (categórica en orden fijo, secuencial azul de un solo tono, estado
siempre con etiqueta de texto). Sin marcas ni logos. Uso típico desde un driver:

    import visuales as V
    V.mapa_calor(filas_riesgos, ruta_png, "Riesgos inherentes", "Riesgos residuales")
    V.consumo([("Reserva de riesgo", 27800, 47800)], ruta_png, "Consumo de reservas")

Cada función devuelve la ruta escrita. Requiere matplotlib (si falta, las funciones no hacen nada y devuelven None).
"""
import os

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    OK = True
except ImportError:          # el recorrido sigue funcionando sin gráficos
    OK = False

# ---------------------------------------------------------------- paleta (referencia validada, modo claro)
SUP = "#fcfcfb"; TINTA = "#0b0b0b"; TINTA2 = "#52514e"; MUDA = "#898781"; GRILLA = "#e1e0d9"; EJE = "#c3c2b7"
SERIE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
ESTADO = {"bien": "#0ca30c", "atencion": "#fab219", "serio": "#ec835a", "critico": "#d03b3b"}
ETIQ_ESTADO = {"bien": "✔ en rango", "atencion": "▲ atención", "serio": "▲ en riesgo", "critico": "✖ fuera de rango"}
ETIQ_CONSUMO = {"bien": "✔ en rango", "serio": "▲ cerca del tope", "critico": "✖ excedido"}
FUENTE = ["DejaVu Sans"]
W, H, DPI = 12.8, 7.2, 125


def _fig(titulo, subtitulo=""):
    plt.rcParams.update({"font.family": FUENTE, "font.size": 13, "axes.edgecolor": EJE, "axes.labelcolor": TINTA2,
                         "xtick.color": MUDA, "ytick.color": MUDA, "axes.titlecolor": TINTA})
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor=SUP)
    fig.text(0.04, 0.94, titulo, fontsize=21, fontweight="bold", color=TINTA, va="top")
    if subtitulo:
        fig.text(0.04, 0.885, subtitulo, fontsize=13, color=TINTA2, va="top")
    return fig


def _ejes(ax, grilla_x=False, grilla_y=True):
    ax.set_facecolor(SUP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(EJE); ax.spines[s].set_linewidth(0.8)
    if grilla_y: ax.yaxis.grid(True, color=GRILLA, linewidth=0.8)
    if grilla_x: ax.xaxis.grid(True, color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=12)


def _guardar(fig, ruta, fuente=""):
    if fuente:
        fig.text(0.04, 0.025, f"Fuente: {fuente}", fontsize=10.5, color=MUDA)
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    fig.savefig(ruta, dpi=DPI, facecolor=SUP)
    plt.close(fig)
    return ruta


def _enteros(eje, valores):
    """Si todos los valores son enteros, el eje solo marca enteros (sin 2,5 o 7,5 redondeados a un entero falso)."""
    vs = [v for v in valores if v is not None]
    if vs and all(float(v).is_integer() for v in vs):
        eje.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))


def _leyenda_aparte(fig, leg, textos):
    """True si la leyenda se superpone en altura y ancho con el título o el subtítulo (hay que darle una fila propia)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer(); bl = leg.get_window_extent(r)
    return any(t.get_window_extent(r).overlaps(bl) for t in textos)


def miles(x, dec=0):
    """Número con separador de miles en punto (formato es-UY)."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- 1. mapa de calor P×I (uno o dos paneles)
def mapa_calor(filas, ruta, titulo="Mapa de calor probabilidad × impacto", subtitulo="", fuente="riesgos.csv",
               residual_titulo=None, umbral_alto=15, umbral_medio=6):
    """filas: dicts de riesgos.csv (id, probabilidad, impacto y, si se pide el panel residual, probabilidad_residual e
    impacto_residual). Celdas: tono secuencial por cantidad; ids escritos en cada celda; zona alta con borde."""
    if not OK: return None
    paneles = [("probabilidad", "impacto", "Inherente")]
    if residual_titulo: paneles.append(("probabilidad_residual", "impacto_residual", residual_titulo))
    fig = _fig(titulo, subtitulo)
    n = len(paneles)
    for k, (cp, ci, nombre) in enumerate(paneles):
        ax = fig.add_axes([0.07 + k * (0.88 / n), 0.12, 0.88 / n - 0.07, 0.68])
        celdas = {}
        for f in filas:
            try: p, i = int(f.get(cp) or 0), int(f.get(ci) or 0)
            except ValueError: continue
            if 1 <= p <= 5 and 1 <= i <= 5: celdas.setdefault((p, i), []).append(f.get("id", ""))
        maxc = max([len(v) for v in celdas.values()] + [1])
        for p in range(1, 6):
            for i in range(1, 6):
                ids = celdas.get((p, i), [])
                tono = "#f0efec" if not ids else SEQ[min(len(SEQ) - 1, 2 + int(8 * len(ids) / maxc))]
                ax.add_patch(Rectangle((i - 0.5 + 0.03, p - 0.5 + 0.03), 0.94, 0.94, facecolor=tono, edgecolor=SUP, linewidth=2))
                if p * i >= umbral_alto:
                    ax.add_patch(Rectangle((i - 0.5 + 0.06, p - 0.5 + 0.06), 0.88, 0.88, fill=False, edgecolor=ESTADO["critico"], linewidth=1.4))
                if ids:
                    txt = "\n".join(ids[:3]) + (f"\n+{len(ids) - 3}" if len(ids) > 3 else "")
                    oscuro = SEQ.index(tono) >= 7 if tono in SEQ else False
                    ax.text(i, p, txt, ha="center", va="center", fontsize=10.5, color=SUP if oscuro else TINTA)
        ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.set_aspect("equal")
        ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
        ax.set_xlabel("Impacto (1–5)"); ax.set_ylabel("Probabilidad (1–5)")
        for s in ax.spines.values(): s.set_visible(False)
        ax.tick_params(length=0, labelsize=12, colors=MUDA)
        tot = sum(len(v) for v in celdas.values()); altos = sum(len(v) for (p, i), v in celdas.items() if p * i >= umbral_alto)
        ax.set_title(f"{nombre}: {tot} riesgos · {altos} en zona alta (P×I ≥ {umbral_alto})", fontsize=13.5, color=TINTA, pad=10)
    fig.text(0.96, 0.025, "Borde rojo = zona alta · tono más oscuro = más riesgos en la celda", fontsize=10.5, color=MUDA, ha="right")
    return _guardar(fig, ruta, fuente)


# ---------------------------------------------------------------- 2. barras horizontales agrupadas (antes / después)
def barras_comparadas(etiquetas, series, ruta, titulo, subtitulo="", fuente="", unidad="", nombres=None, leyenda="lower right"):
    """series: lista de listas de valores (máx. 3 series, una por color en orden fijo). Etiqueta de valor al final de
    cada barra solo para la última serie (la que cuenta la historia). leyenda: posición de matplotlib dentro del
    gráfico ("lower right", "upper right", "center right"…), "arriba" (fila propia entre el subtítulo y el gráfico) o
    None (sin leyenda)."""
    if not OK: return None
    nombres = nombres or [f"Serie {k + 1}" for k in range(len(series))]
    fig = _fig(titulo, subtitulo)
    ax = fig.add_axes([0.27, 0.12, 0.66, 0.68]); _ejes(ax, grilla_x=True, grilla_y=False)
    n = len(series); alto = 0.8 / n
    ys = list(range(len(etiquetas)))[::-1]
    mx = max(max(s) for s in series) or 1
    for k, s in enumerate(series):
        pos = [y + (n - 1 - k - (n - 1) / 2) * alto for y in ys]
        ax.barh(pos, s, height=alto - 0.04, color=SERIE[k], label=nombres[k])
        if k == n - 1:
            for y, v in zip(pos, s):
                ax.text(v + mx * 0.01, y, f"{miles(v)}{unidad}", va="center", fontsize=11, color=TINTA2)
    ax.set_yticks(ys); ax.set_yticklabels(etiquetas, fontsize=12, color=TINTA)
    ax.set_xlim(0, mx * 1.15)
    _enteros(ax.xaxis, [v for s in series for v in s])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: miles(v)))
    if leyenda == "arriba":
        fig.legend(*ax.get_legend_handles_labels(), loc="lower left", bbox_to_anchor=(0.27, 0.805), frameon=False, fontsize=12, ncol=len(series))
    elif leyenda:
        ax.legend(loc=leyenda, frameon=False, fontsize=12)
    return _guardar(fig, ruta, fuente)


# ---------------------------------------------------------------- 3. consumo de presupuestos (barras con tope)
def consumo(items, ruta, titulo="Consumo de presupuestos de la junta", subtitulo="", fuente="sanidad CAM-03 · estado.json presupuestos"):
    """items: (nombre, usado, tope). Barra de fondo = tope; barra = usado con color de estado y etiqueta de texto."""
    if not OK: return None
    fig = _fig(titulo, subtitulo)
    ax = fig.add_axes([0.27, 0.14, 0.62, 0.66]); _ejes(ax, grilla_x=True, grilla_y=False)
    ys = list(range(len(items)))[::-1]
    mx = max(max(u, t) for _, u, t in items) or 1
    for y, (nombre, usado, tope) in zip(ys, items):
        pct = 100 * usado / tope if tope else 0
        est = "critico" if pct > 100 else "serio" if pct >= 80 else "bien"
        ax.barh(y, tope, height=0.55, color="#f0efec")
        ax.barh(y, usado, height=0.55, color=ESTADO[est])
        ax.plot([tope, tope], [y - 0.36, y + 0.36], color=TINTA, linewidth=1.6)
        ax.text(max(usado, tope) + mx * 0.015, y, f"{miles(usado)} de {miles(tope)} · {pct:.0f} % · {ETIQ_CONSUMO[est]}",
                va="center", fontsize=12, color=TINTA)
    ax.set_yticks(ys); ax.set_yticklabels([i[0] for i in items], fontsize=12.5, color=TINTA)
    ax.set_xlim(0, mx * 1.55)
    _enteros(ax.xaxis, [x for _, u, tp in items for x in (u, tp)])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: miles(v)))
    fig.text(0.96, 0.07, "Línea negra = tope fijado por la junta", fontsize=10.5, color=MUDA, ha="right")
    return _guardar(fig, ruta, fuente)


# ---------------------------------------------------------------- 4. líneas en el tiempo (EVM, burn-up, salud)
def lineas(x, series, ruta, titulo, subtitulo="", fuente="", nombres=None, unidad="", ylim0=True, referencia=None):
    """series: lista de listas (None = sin dato). Máx. 3-4 series en orden fijo; etiqueta directa al final de cada línea.
    referencia: (valor, texto) dibuja una línea horizontal fina (p. ej. BAC o alcance total). La leyenda va arriba a la
    derecha; si se superpone con un título o subtítulo largos, pasa a una fila propia entre el subtítulo y el gráfico."""
    if not OK: return None
    nombres = nombres or [f"Serie {k + 1}" for k in range(len(series))]
    fig = _fig(titulo, subtitulo)
    textos = list(fig.texts)
    ax = fig.add_axes([0.08, 0.14, 0.76, 0.66]); _ejes(ax)
    xs = list(range(len(x)))
    finales = []
    for k, s in enumerate(series):
        pts = [(i, v) for i, v in zip(xs, s) if v is not None]
        if not pts: continue
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=SERIE[k], linewidth=2.2, marker="o", markersize=6,
                markeredgecolor=SUP, markeredgewidth=1.5, label=nombres[k])
        finales.append([pts[-1][0], pts[-1][1], f"{nombres[k]} {miles(pts[-1][1])}{unidad}"])
    if referencia:
        ax.axhline(referencia[0], color=MUDA, linewidth=1)
        ax.text(len(x) - 1 + 0.85, referencia[0], f"{referencia[1]}", va="bottom", ha="right", fontsize=11, color=TINTA2)
    ymax = max([v for s in series for v in s if v is not None] + [referencia[0] if referencia else 0]) or 1
    sep = ymax * 0.045                                       # separa etiquetas finales que se pisan
    for a_ in sorted(finales, key=lambda f: f[1]):
        for b_ in finales:
            if b_ is not a_ and b_[0] == a_[0] and b_[1] < a_[1] + sep and b_[1] >= a_[1] and b_ is not a_:
                b_[1] = a_[1] + sep
    for i, v, t in finales:
        ax.text(i + 0.12, v, t, va="center", fontsize=11.5, color=TINTA)
    ax.set_xticks(xs); ax.set_xticklabels(x, fontsize=11.5, rotation=0)
    if ylim0: ax.set_ylim(bottom=0)
    ax.set_xlim(-0.3, len(x) - 0.3 + 0.9)
    _enteros(ax.yaxis, [v for s in series for v in s] + ([referencia[0]] if referencia else []))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: miles(v)))
    leg = fig.legend(loc="upper right", bbox_to_anchor=(0.96, 0.93), frameon=False, fontsize=12, ncol=len(series))
    if _leyenda_aparte(fig, leg, textos):
        leg.remove()
        fig.legend(*ax.get_legend_handles_labels(), loc="lower left", bbox_to_anchor=(0.08, 0.805), frameon=False, fontsize=12, ncol=len(series))
    return _guardar(fig, ruta, fuente)


# ---------------------------------------------------------------- 5. Gantt con camino crítico
def gantt(tareas, ruta, titulo="Cronograma y camino crítico", subtitulo="", fuente="cpm.py", unidad="días"):
    """tareas: dicts con id, nombre, inicio (número), fin (número), critica (bool). Dos identidades: crítica / con
    holgura, con leyenda; etiqueta de duración al final de cada barra crítica."""
    if not OK: return None
    fig = _fig(titulo, subtitulo)
    ax = fig.add_axes([0.30, 0.13, 0.63, 0.67]); _ejes(ax, grilla_x=True, grilla_y=False)
    ys = list(range(len(tareas)))[::-1]
    for y, t in zip(ys, tareas):
        c = SERIE[1] if t.get("critica") else SERIE[0]
        ax.barh(y, t["fin"] - t["inicio"], left=t["inicio"], height=0.56, color=c)
        if t.get("critica"):
            ax.text(t["fin"] + 0.6, y, f"{t['fin'] - t['inicio']:g} {unidad}", va="center", fontsize=10.5, color=TINTA2)
    ax.set_yticks(ys); ax.set_yticklabels([f"{t['id']} {t['nombre'][:34]}" for t in tareas], fontsize=11.5, color=TINTA)
    ax.set_xlabel(f"Tiempo ({unidad} desde el inicio)")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=SERIE[1], label="Camino crítico (holgura 0)"), Patch(color=SERIE[0], label="Con holgura")],
               loc="upper right", bbox_to_anchor=(0.96, 0.93), frameon=False, fontsize=12, ncol=2)
    return _guardar(fig, ruta, fuente)


# ---------------------------------------------------------------- 6. puntajes con estado (OKR, objetivos, calidad)
def estados(items, ruta, titulo, subtitulo="", fuente="", maximo=1.0, decimales=2, sufijo=""):
    """items: (etiqueta, valor, estado[, texto de estado]) con estado en bien|atencion|serio|critico. Barra horizontal
    con color de estado, valor y estado en texto (el color nunca va solo)."""
    if not OK: return None
    fig = _fig(titulo, subtitulo)
    ax = fig.add_axes([0.30, 0.13, 0.50, 0.67]); _ejes(ax, grilla_x=True, grilla_y=False)
    ys = list(range(len(items)))[::-1]
    for y, it in zip(ys, items):
        et, v, est = it[:3]; txt = it[3] if len(it) > 3 else ETIQ_ESTADO.get(est, est)
        ax.barh(y, maximo, height=0.5, color="#f0efec")
        ax.barh(y, min(v, maximo), height=0.5, color=ESTADO.get(est, SERIE[0]))
        ax.text(maximo * 1.02, y, f"{miles(v, decimales)}{sufijo} · {txt}", va="center", fontsize=12, color=TINTA)
    ax.set_yticks(ys); ax.set_yticklabels([i[0][:42] for i in items], fontsize=12, color=TINTA)
    ax.set_xlim(0, maximo * 1.45)
    ax.set_xticks([maximo * k / 4 for k in range(5)])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: miles(v, decimales if maximo <= 1 else 0)))
    return _guardar(fig, ruta, fuente)


# ---------------------------------------------------------------- 7. tarjetas de indicadores (stat tiles)
def tarjetas(items, ruta, titulo, subtitulo="", fuente=""):
    """items: (valor grande, rótulo, detalle, estado o None). Hasta 6 tarjetas en 2 filas."""
    if not OK: return None
    import textwrap
    fig = _fig(titulo, subtitulo)
    n = len(items); cols = 3 if n > 4 else n; filas = (n + cols - 1) // cols
    w = 0.92 / cols; h = min(0.36, 0.72 / filas); arriba = 0.46 + h * filas / 2
    for k, (val, rot, det, est) in enumerate(items):
        c, r = k % cols, k // cols
        x0, y0 = 0.04 + c * w, arriba - (r + 1) * h
        ax = fig.add_axes([x0 + 0.01, y0 + 0.02, w - 0.02, h - 0.04]); ax.axis("off")
        ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="#f0efec", edgecolor="none"))
        if est:
            ax.add_patch(Rectangle((0, 0), 0.015, 1, transform=ax.transAxes, facecolor=ESTADO[est], edgecolor="none"))
        ax.text(0.07, 0.74, str(val), fontsize=30, fontweight="bold", color=TINTA, transform=ax.transAxes, va="center")
        ax.text(0.07, 0.46, rot, fontsize=13.5, color=TINTA, transform=ax.transAxes, va="center")
        ancho = max(16, int(118 * w))
        det2 = det + (f" · {ETIQ_ESTADO[est]}" if est else "")
        ax.text(0.07, 0.22, "\n".join(textwrap.wrap(det2, ancho)[:2]), fontsize=11, color=TINTA2, transform=ax.transAxes, va="center")
    return _guardar(fig, ruta, fuente)


# ---------------------------------------------------------------- 8. mapa de supuestos (criticidad × certeza)
def mapa_supuestos(filas, ruta, titulo="Mapa de supuestos: dónde invertir primero en aprender", subtitulo="",
                   fuente="supuestos.csv"):
    """filas: dicts de supuestos.csv con criticidad y certeza (alta|media|baja). Celda prioritaria (criticidad alta y
    certeza baja) con borde; ids escritos; los validados se marcan con ✔ y los invalidados con ✖."""
    if not OK: return None
    niv = {"baja": 1, "media": 2, "alta": 3}
    fig = _fig(titulo, subtitulo)
    ax = fig.add_axes([0.20, 0.12, 0.60, 0.68])
    celdas = {}
    for f in filas:
        c, k = niv.get(f.get("criticidad", "")), niv.get(f.get("certeza", ""))
        if not c or not k: continue
        marca = " ✔" if f.get("validado") == "si" else " ✖" if f.get("validado") == "no" else ""
        celdas.setdefault((c, k), []).append(f.get("id", "") + marca)
    for c in (1, 2, 3):
        for k in (1, 2, 3):
            prio = c == 3 and k == 1
            ids = celdas.get((c, k), [])
            tono = SEQ[8] if prio and ids else SEQ[3] if ids else "#f0efec"
            ax.add_patch(Rectangle((k - 0.5 + 0.03, c - 0.5 + 0.03), 0.94, 0.94, facecolor=tono, edgecolor=SUP, linewidth=2))
            if prio:
                ax.add_patch(Rectangle((k - 0.5 + 0.06, c - 0.5 + 0.06), 0.88, 0.88, fill=False, edgecolor=ESTADO["critico"], linewidth=1.6))
            if ids:
                ax.text(k, c, "\n".join(ids[:5]) + (f"\n+{len(ids) - 5}" if len(ids) > 5 else ""), ha="center", va="center",
                        fontsize=12, color=SUP if tono == SEQ[8] else TINTA)
    ax.set_xlim(0.5, 3.5); ax.set_ylim(0.5, 3.5)
    ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["baja", "media", "alta"]); ax.set_yticks([1, 2, 3]); ax.set_yticklabels(["baja", "media", "alta"])
    ax.set_xlabel("Certeza hoy (evidencia disponible)"); ax.set_ylabel("Criticidad (si es falso, ¿cuánto cambia el caso?)")
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.tick_params(length=0, labelsize=12, colors=MUDA)
    fig.text(0.82, 0.70, "Borde rojo:\nvalidar primero\n(crítico y sin\nevidencia)", fontsize=12, color=TINTA2, va="top")
    fig.text(0.82, 0.45, "✔ validado\n✖ invalidado", fontsize=12, color=TINTA2, va="top")
    return _guardar(fig, ruta, fuente)

