// Presentaciones light de pm-method para IEEE · PPTX.
// Uso: node build_pptx.js resumen|informe   (lee datos-<nombre>.json; escribe ../pm-method-ieee-<nombre>-light.pptx)
// Estética sobria del resumen ejecutivo (docs/resumen-ejecutivo/fuente/build_pptx.js): Arial, azul marino, azul y naranja,
// con tonos de azul propios (17324D, 2B6A9A) para no usar colores de marca de ninguna organización;
// 13,33" × 7,5", título-conclusión en la banda azul, número de diapositiva del layout y recuadro «Logo IEEE».
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
process.chdir(__dirname);
const APPLY_THEME = ["/mnt/skills/public/pptx/scripts/apply_theme.js"].find(p => fs.existsSync(p));
const { applyTheme } = APPLY_THEME ? require(APPLY_THEME) : { applyTheme: async () => {} };
const NOMBRE = process.argv[2];
if (!["resumen", "informe"].includes(NOMBRE)) { console.error("uso: node build_pptx.js resumen|informe"); process.exit(2); }
const D = JSON.parse(fs.readFileSync(`datos-${NOMBRE}.json`, "utf8"));
const RAIZ = path.resolve(__dirname, "../../..");
const SALIDA = path.resolve(__dirname, `../${D.meta.archivo}.pptx`);

const THEME = { name: "pm-method IEEE light", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "272425", lt1: "FFFFFF", dk2: "17324D", lt2: "F4F6F8", accent1: "2B6A9A", accent2: "B5651D", accent3: "17324D", accent4: "696969", accent5: "2A78D6", accent6: "EB6834", hlink: "2B6A9A", folHlink: "17324D" } };
const NAVY = "17324D", BLUE = "2B6A9A", ORANGE = "B5651D", GRAY = "696969", CHAR = "272425", WHITE = "FFFFFF", LT = "F4F6F8",
  BLUETINT = "E9F1F8", ORTINT = "FBF1E6", NAVY2 = "22476E", SKY = "9FD0F0", MID = "5B8DB8";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };
pres.author = "pm-method"; pres.title = D.meta.titulo_doc; pres.subject = D.meta.descripcion;
const W = 13.33, H = 7.5;

// ---------- layouts
const logoBox = (x, y, w, h, color) => [
  { rect: { x, y, w, h, fill: { color: "FFFFFF", transparency: 100 }, line: { color, width: 1, dashType: "dash" } } },
  { text: { text: "Logo IEEE", options: { x, y, w, h, fontSize: 9, color, align: "center", valign: "middle", margin: 0 } } }];
pres.defineSlideMaster({ title: "PORTADA", background: { color: NAVY }, objects: [...logoBox(0.6, 0.5, 2.0, 0.8, SKY)] });
// número de diapositiva: propiedad `slideNumber` del layout (pptxgenjs ignora un slideNumber dentro de objects)
pres.defineSlideMaster({ title: "CONTENIDO", background: { color: WHITE }, margin: [0.5, 0.5, 0.9, 0.5],
  slideNumber: { x: W - 1.2, y: H - 0.48, w: 0.7, h: 0.3, fontSize: 9, color: GRAY, align: "right" }, objects: [
    ...logoBox(W - 2.2, 0.4, 1.7, 0.78, GRAY),
    { rect: { x: 0.5, y: 0.4, w: 10.45, h: 0.78, fill: { color: BLUE }, rectRadius: 0.1, shape: "roundRect" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 0.4, w: 10.1, h: 0.78, fontSize: 19, bold: true, color: WHITE, margin: 0, valign: "middle", align: "left" } } },
    { text: { text: D.meta.pie, options: { x: 0.5, y: H - 0.48, w: 9, h: 0.3, fontSize: 9, color: GRAY, margin: 0 } } }] });

// ---------- utilidades (las del resumen ejecutivo)
const lines = (t, wIn, pt, em = 0.5) => String(t).split("\n").reduce((a, p) => a + Math.max(1, Math.ceil(p.length / Math.max(1, (wIn * 72) / (pt * em)))), 0);
const textH = (t, wIn, pt, ls = 1.2, em = 0.5) => lines(t, wIn, pt, em) * pt * ls / 72;
const fitSize = (t, wIn, hIn, max, min = 12, em = 0.5) => { let s = max; while (s > min && textH(t, wIn, s, 1.2, em) > hIn) s -= 0.5; return s; };
const avisos = [];
let n = 0;
const tb = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, fontSize: 14, color: CHAR, valign: "top" }, o));
function fit(s, t, x, y, w, h, max, min, o = {}) {
  const em = o.bold ? 0.55 : 0.5;
  const size = fitSize(t, w, h, max, min, em);
  if (textH(t, w, size, 1.2, em) > h + 0.02) avisos.push(`diapositiva ${n}: texto que puede no entrar («${t.slice(0, 50)}…»)`);
  tb(s, t, Object.assign({ x, y, w, h, fontSize: size }, o));
  return size;
}
const rr = (s, x, y, w, h, fill, o = {}) => s.addShape(pres.ShapeType.roundRect, Object.assign({ x, y, w, h, fill: { color: fill }, rectRadius: 0.08, line: { color: o.line || fill, width: o.lw || 0.75, dashType: o.dash || "solid" } }, o.extra || {}));
const circ = (s, x, y, d, fill, txt, size = 16) => {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 } });
  tb(s, txt, { x, y, w: d, h: d, fontSize: size, bold: true, color: WHITE, align: "center", valign: "middle" });
};
const arrow = (s, x, y, w, h, color = ORANGE, o = {}) => s.addShape(pres.ShapeType.line, Object.assign({ x, y, w, h, line: { color, width: 2, endArrowType: "triangle", beginArrowType: o.both ? "triangle" : undefined } }, o.extra || {}));
const label = (s, t, x, y, w, color = ORANGE) => tb(s, t.toUpperCase(), { x, y, w, h: 0.28, fontSize: 11, bold: true, color, charSpacing: 1 });
function imagen(s, file, x, y, w, h) {
  const png = fs.readFileSync(file);
  const iw = png.readUInt32BE(16), ih = png.readUInt32BE(20);
  let ww = w, hh = ww * ih / iw;
  if (hh > h) { hh = h; ww = hh * iw / ih; }
  const xx = x + (w - ww) / 2;
  s.addShape(pres.ShapeType.rect, { x: xx - 0.04, y: y - 0.04, w: ww + 0.08, h: hh + 0.08, fill: { color: WHITE }, line: { color: "D5DCE3", width: 0.75 } });
  s.addImage({ path: file, x: xx, y, w: ww, h: hh, altText: path.basename(file) });
  return { x: xx, w: ww, h: hh };
}
function slide(d) {
  n++;
  const s = pres.addSlide({ masterName: "CONTENIDO" });
  s.addText(d.titulo, { placeholder: "title" });
  if (textH(d.titulo, 10.1, 19, 1.15) > 0.8) avisos.push(`diapositiva ${n}: título largo`);
  if (d.nota) s.addNotes(d.nota);
  return s;
}
// recuadro de siglas, a la derecha
function siglas(s, x, y, w, h) {
  rr(s, x, y, w, h, LT, { line: "D5DCE3" });
  tb(s, D.siglas_titulo, { x: x + 0.22, y: y + 0.16, w: w - 0.4, h: 0.34, fontSize: 15, bold: true, color: NAVY });
  const items = D.siglas.map(([k, v]) => `${k}  ${v}`).join("\n");
  const hb = h - 0.95;
  const size = fitSize(items, w - 0.44, hb - D.siglas.length * 0.08, 13, 11.5);
  if (textH(items, w - 0.44, size) + D.siglas.length * 0.08 > hb) avisos.push(`diapositiva ${n}: siglas que pueden no entrar`);
  const out = [];
  D.siglas.forEach(([k, v], i) => {
    out.push({ text: k + "  ", options: { bold: true, color: NAVY, fontSize: size, paraSpaceAfter: 6 } });
    out.push({ text: v, options: { color: CHAR, fontSize: size, paraSpaceAfter: 6, breakLine: i < D.siglas.length - 1 } });
  });
  s.addText(out, { x: x + 0.22, y: y + 0.6, w: w - 0.44, h: hb, isTextBox: true, margin: 0, valign: "top" });
  tb(s, D.siglas_nota, { x: x + 0.22, y: y + h - 0.36, w: w - 0.44, h: 0.26, fontSize: 10, italic: true, color: GRAY });
}

// ---------- tipos de diapositiva
const R = {};
R.portada = d => {
  n++;
  const s = pres.addSlide({ masterName: "PORTADA" });
  tb(s, d.kicker, { x: 0.6, y: 1.6, w: 11, h: 0.4, fontSize: 16, bold: true, color: SKY });
  const ts = fit(s, d.titulo, 0.6, 2.05, 12.1, 1.75, 38, 28, { color: WHITE, bold: true });
  const ys = 2.05 + Math.min(1.75, textH(d.titulo, 12.1, ts, 1.2, 0.55)) + 0.12;
  fit(s, d.subtitulo, 0.6, ys, 11.6, 4.7 - ys, 19, 15, { color: WHITE });
  const k = d.tarjetas.length, gap = 0.2, w = (12.13 - gap * (k - 1)) / k;
  d.tarjetas.forEach(([t, x2], i) => {
    const x = 0.6 + i * (w + gap);
    rr(s, x, 4.85, w, 1.5, NAVY2);
    tb(s, t, { x: x + 0.22, y: 4.97, w: w - 0.44, h: 0.36, fontSize: 16, bold: true, color: WHITE });
    fit(s, x2, x + 0.22, 5.36, w - 0.44, 0.92, 15, 13, { color: SKY });
  });
  tb(s, `pm-method ${D.meta.version} · ${D.meta.portada_linea}`, { x: 0.6, y: 6.7, w: 8, h: 0.3, fontSize: 11, color: SKY });
  if (d.nota) s.addNotes(d.nota);
};

R.antes_despues = d => {
  const s = slide(d);
  label(s, d.col_hoy, 0.5, 1.42, 5.5, GRAY); label(s, d.col_con, 6.75, 1.42, 6, BLUE);
  const k = d.filas.length, y0 = 1.78, rh = k > 4 ? 0.74 : 0.86, g = k > 4 ? 0.1 : 0.14;
  d.filas.forEach(([hoy, con], i) => {
    const y = y0 + i * (rh + g);
    rr(s, 0.5, y, 5.6, rh, LT);
    fit(s, hoy, 0.7, y + 0.08, 5.2, rh - 0.16, 16, 14, { valign: "middle" });
    tb(s, "→", { x: 6.15, y, w: 0.55, h: rh, fontSize: 24, bold: true, color: ORANGE, align: "center", valign: "middle" });
    rr(s, 6.75, y, 6.08, rh, BLUETINT);
    fit(s, con, 6.95, y + 0.08, 5.7, rh - 0.16, 16, 14, { color: NAVY, bold: true, valign: "middle" });
  });
  const yl = y0 + d.filas.length * (rh + g) + 0.12;
  rr(s, 0.5, yl, 12.33, 0.66, ORTINT);
  tb(s, d.lema, { x: 0.75, y: yl, w: 11.9, h: 0.66, fontSize: 18, bold: true, italic: true, color: ORANGE, valign: "middle" });
};

R.flujo_siglas = d => {
  const s = slide(d);
  const x0 = 0.5, wl = 7.5, k = d.pasos.length, cw = wl / k, dd = 1.05;
  d.pasos.forEach(([t, x2], i) => {
    const cx = x0 + cw * i + cw / 2;
    circ(s, cx - dd / 2, 1.55, dd, i === 1 ? ORANGE : NAVY, String(i + 1), 26);
    if (i < k - 1) arrow(s, cx + dd / 2 + 0.12, 1.55 + dd / 2, cw - dd - 0.24, 0, GRAY);
    tb(s, t, { x: cx - cw / 2 + 0.08, y: 2.72, w: cw - 0.16, h: 0.36, fontSize: 17, bold: true, color: i === 1 ? ORANGE : NAVY, align: "center" });
    fit(s, x2, cx - cw / 2 + 0.12, 3.1, cw - 0.24, 1.0, 14, 13, { align: "center" });
  });
  label(s, d.ventajas_titulo, x0, 4.3, 5, BLUE);
  const vw = (wl - 0.2) / 2, vh = 1.0;
  d.ventajas.forEach(([t, x2], i) => {
    const x = x0 + (i % 2) * (vw + 0.2), y = 4.64 + Math.floor(i / 2) * (vh + 0.14);
    rr(s, x, y, vw, vh, i % 3 === 0 ? BLUETINT : ORTINT);
    tb(s, [{ text: "✓  ", options: { color: i % 3 === 0 ? BLUE : ORANGE, bold: true, fontSize: 15 } }, { text: t, options: { color: NAVY, bold: true, fontSize: 15 } }], { x: x + 0.18, y: y + 0.1, w: vw - 0.3, h: 0.32 });
    fit(s, x2.charAt(0).toUpperCase() + x2.slice(1), x + 0.18, y + 0.44, vw - 0.32, vh - 0.5, 14, 12.5);
  });
  siglas(s, 8.3, 1.42, 4.53, 5.36);
};

R.programa = d => {
  const s = slide(d);
  const P = D.programa, mods = P.modulos, k = mods.length, g = 0.1, w = (12.33 - g * (k - 1)) / k, y = 1.42, hh = 0.95, hb = 1.45;
  mods.forEach((m, i) => {
    const x = 0.5 + i * (w + g), nuevo = m.material !== "existente";
    rr(s, x, y, w, hh, nuevo ? ORANGE : NAVY);
    tb(s, m.id === "M0" ? "Inicio" : m.id === "TI" ? "Cierre" : `Taller ${m.id.slice(1)}`, { x: x + 0.1, y: y + 0.08, w: w - 0.2, h: 0.28, fontSize: 12, bold: true, color: nuevo ? "FFF2E6" : SKY });
    tb(s, [{ text: String(m.sesiones), options: { fontSize: 26, bold: true, color: WHITE } }, { text: "  sesiones", options: { fontSize: 12, color: WHITE } }], { x: x + 0.1, y: y + 0.36, w: w - 0.2, h: 0.52, valign: "middle" });
    rr(s, x, y + hh + 0.06, w, hb, nuevo ? ORTINT : BLUETINT);
    fit(s, m.nombre, x + 0.1, y + hh + 0.14, w - 0.2, 0.92, 14, 12, { bold: true, color: NAVY });
    fit(s, m.lema + (m.caso ? ` · ${m.caso}` : ""), x + 0.1, y + hh + 1.06, w - 0.2, 0.42, 12, 10.5, { italic: true, color: GRAY });
  });
  // leyenda
  const yl = y + hh + 0.06 + hb + 0.1;
  tb(s, [{ text: "■ ", options: { color: NAVY, fontSize: 13 } }, { text: "material ya listo (guía, ejercicio y diapositivas)     ", options: { color: CHAR, fontSize: 12 } },
    { text: "■ ", options: { color: ORANGE, fontSize: 13 } }, { text: "a preparar para IEEE     ", options: { color: CHAR, fontSize: 12 } },
    { text: d.rotulo, options: { color: GRAY, fontSize: 12, italic: true } }], { x: 0.5, y: yl, w: 12.33, h: 0.3 });
  // detalle de los módulos nuevos
  const yd = yl + 0.4, wd = 6.06, hd = 0.92;
  mods.filter(m => m.material !== "existente").forEach((m, i) => {
    const x = 0.5 + i * (wd + 0.21);
    rr(s, x, yd, wd, hd, LT);
    tb(s, m.nombre, { x: x + 0.18, y: yd + 0.08, w: wd - 0.36, h: 0.3, fontSize: 14, bold: true, color: ORANGE });
    fit(s, m.detalle, x + 0.18, yd + 0.38, wd - 0.36, hd - 0.44, 13, 12);
  });
  // cálculo y ritmo
  const yc = yd + hd + 0.14, hc = 6.84 - yc;
  rr(s, 0.5, yc, 6.06, hc, NAVY);
  tb(s, d.calculo.join("\n"), { x: 0.7, y: yc + 0.1, w: 5.7, h: 0.64, fontSize: 17, bold: true, color: WHITE });
  fit(s, d.material, 0.7, yc + 0.78, 5.7, hc - 0.84, 12.5, 11, { color: "DCE8F3" });
  P.ritmo_total.forEach(([r, v], i) => {
    const x = 6.77 + i * 3.08;
    rr(s, x, yc, 2.95, hc, i ? ORTINT : BLUETINT);
    tb(s, v, { x: x + 0.2, y: yc + 0.16, w: 2.6, h: 0.62, fontSize: 30, bold: true, color: i ? ORANGE : NAVY });
    tb(s, r, { x: x + 0.2, y: yc + 0.82, w: 2.6, h: 0.32, fontSize: 14, color: CHAR });
  });
};

R.piloto = d => {
  const s = slide(d);
  const P = D.programa, xl = 0.5, wl = 6.0;
  let y = 1.42;
  P.pasos_piloto.forEach((p, i) => {
    const det = p.detalle.charAt(0).toUpperCase() + p.detalle.slice(1);
    const hn = textH(p.nombre, wl - 0.4, 15, 1.2, 0.55), hdt = textH(det, wl - 0.4, 13);
    const h = 0.1 + 0.28 + hn + 0.06 + hdt + 0.12;
    rr(s, xl, y, wl, h, p.opcional ? WHITE : (i ? BLUETINT : ORTINT), { line: p.opcional ? GRAY : undefined, dash: p.opcional ? "dash" : undefined, lw: 1 });
    tb(s, p.sesiones + (p.opcional ? " · opcional" : ""), { x: xl + 0.2, y: y + 0.1, w: wl - 0.4, h: 0.26, fontSize: 12, bold: true, color: ORANGE });
    tb(s, p.nombre, { x: xl + 0.2, y: y + 0.38, w: wl - 0.4, h: hn, fontSize: 15, bold: true, color: NAVY });
    tb(s, det, { x: xl + 0.2, y: y + 0.38 + hn + 0.06, w: wl - 0.4, h: hdt, fontSize: 13, color: CHAR });
    y += h + 0.12;
  });
  y += 0.04;
  P.calculo_piloto.forEach((c, i) => {
    rr(s, xl, y, wl, 0.66, i ? LT : NAVY);
    tb(s, [{ text: c.rot + ":  ", options: { bold: true, fontSize: 13, color: i ? NAVY : SKY } }, { text: c.cuenta, options: { bold: true, fontSize: 14, color: i ? NAVY : WHITE } }], { x: xl + 0.2, y: y + 0.06, w: wl - 0.4, h: 0.3 });
    tb(s, c.ritmo, { x: xl + 0.2, y: y + 0.36, w: wl - 0.4, h: 0.26, fontSize: 12, color: i ? GRAY : "DCE8F3" });
    y += 0.76;
  });
  if (y > 6.9) avisos.push(`diapositiva ${n}: el piloto no entra (${y.toFixed(2)} in)`);
  const xr = 6.85, wr = 5.98;
  const im = imagen(s, path.join(RAIZ, d.imagen), xr, 1.5, wr, 3.4);
  const yp = 1.5 + im.h + 0.12;
  fit(s, d.pie, im.x, yp, im.w, 0.66, 12.5, 11, { italic: true, color: GRAY });
  rr(s, xr, 5.62, wr, 1.2, ORTINT);
  fit(s, d.despues, xr + 0.22, 5.7, wr - 0.44, 1.04, 15, 13, { color: ORANGE, bold: true, valign: "middle" });
};

R.problemas = d => {
  const s = slide(d);
  const w = 6.06, h = 2.55, g = 0.21;
  d.tarjetas.forEach(([p, r], i) => {
    const x = 0.5 + (i % 2) * (w + g), y = 1.42 + Math.floor(i / 2) * (h + 0.2);
    rr(s, x, y, w, h, LT);
    circ(s, x + 0.2, y + 0.18, 0.48, NAVY, String(i + 1), 16);
    label(s, d.rot_problema, x + 0.85, y + 0.2, 3, GRAY);
    fit(s, p, x + 0.85, y + 0.48, w - 1.05, 0.78, 16, 14, { bold: true });
    rr(s, x + 0.2, y + 1.36, w - 0.4, h - 1.56, BLUETINT);
    label(s, "→ " + d.rot_respuesta, x + 0.38, y + 1.44, 5, BLUE);
    fit(s, r, x + 0.38, y + 1.74, w - 0.76, h - 1.98, 15, 13, { color: NAVY });
  });
};

R.capas_siglas = d => {
  const s = slide(d);
  label(s, d.rotulo, 0.5, 1.42, 7);
  const fills = [NAVY, BLUE, MID, BLUETINT], tcol = [WHITE, WHITE, WHITE, NAVY];
  d.capas.forEach(([t, x2], i) => {
    const y = 1.8 + i * 1.24, ind = i * 0.3;
    rr(s, 0.5 + ind, y, 7.5 - ind, 1.1, fills[i]);
    tb(s, `${i + 1} · ${t}`, { x: 0.75 + ind, y: y + 0.12, w: 7.0 - ind, h: 0.38, fontSize: 18, bold: true, color: tcol[i] });
    fit(s, x2.charAt(0).toUpperCase() + x2.slice(1), 0.75 + ind, y + 0.52, 7.0 - ind, 0.5, 15, 13, { color: tcol[i] });
  });
  siglas(s, 8.3, 1.42, 4.53, 5.36);
};

R.roles = d => {
  const s = slide(d);
  const card = (x, y, w, h, [t, x2], fill, tc, dc, o = {}) => {
    rr(s, x, y, w, h, fill, o);
    tb(s, t, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.34, fontSize: 16, bold: true, color: tc });
    fit(s, x2.charAt(0).toUpperCase() + x2.slice(1), x + 0.2, y + 0.5, w - 0.4, h - 0.58, 14, 12, { color: dc });
  };
  const ya = 1.5, ha = 1.3;
  card(0.5, ya, 3.3, ha, d.persona, ORTINT, ORANGE, CHAR);
  card(4.55, ya, 3.9, ha, d.coordinador, NAVY, WHITE, "DCE8F3");
  card(9.2, ya, 3.63, ha, d.registrador, ORANGE, WHITE, "FFF2E6");
  arrow(s, 3.85, ya + ha / 2, 0.65, 0, ORANGE, { both: true });
  arrow(s, 8.5, ya + ha / 2, 0.65, 0, ORANGE);
  // ayudantes
  const yb = 3.35, hb = 1.5, xb = 2.2, wb = 8.93;
  arrow(s, 6.5, ya + ha + 0.03, 0, yb - ya - ha - 0.06, GRAY);
  rr(s, xb, yb, wb, hb, BLUETINT);
  tb(s, d.ayudantes_titulo, { x: xb + 0.25, y: yb + 0.12, w: wb - 0.5, h: 0.34, fontSize: 15, bold: true, color: NAVY });
  const k = d.ayudantes.length, pg = 0.2, pw = (wb - 0.5 - pg * (k - 1)) / k;
  d.ayudantes.forEach((a, i) => {
    rr(s, xb + 0.25 + i * (pw + pg), yb + 0.6, pw, 0.68, BLUE);
    tb(s, a, { x: xb + 0.25 + i * (pw + pg), y: yb + 0.6, w: pw, h: 0.68, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle" });
  });
  // guardián y archivos
  const yc = 5.3, hc = 1.4;
  arrow(s, 9.4, yb + hb + 0.03, 0, yc - yb - hb - 0.06, GRAY);
  arrow(s, 12.0, ya + ha + 0.03, 0, yc - ya - ha - 0.06, ORANGE);
  card(0.5, yc, 6.0, hc, d.guardian, LT, NAVY, CHAR, { line: GRAY, dash: "dash", lw: 1 });
  card(6.83, yc, 6.0, hc, d.archivos, LT, NAVY, CHAR);
};

R.puertas = d => {
  const s = slide(d);
  const k = d.etapas.length, g = 0.6, w = (12.33 - g * k) / k + g / k, yc = 1.55, hc = 1.0;
  const ww = (12.33 - g * k) / k;
  d.etapas.forEach(([t, x2], i) => {
    const x = 0.5 + i * (ww + g);
    s.addShape(i === 0 ? pres.ShapeType.homePlate : pres.ShapeType.chevron, { x, y: yc, w: ww, h: hc, fill: { color: [BLUE, BLUE, NAVY, MID][i] || BLUE }, line: { color: WHITE, width: 0 } });
    tb(s, [{ text: t + "\n", options: { fontSize: 17, bold: true, color: WHITE } }, { text: x2, options: { fontSize: 13, color: WHITE } }], { x: x + (i ? 0.5 : 0.2), y: yc, w: ww - (i ? 0.85 : 0.55), h: hc, valign: "middle" });
    const gx = x + ww + g / 2;
    s.addShape(pres.ShapeType.diamond, { x: gx - 0.17, y: yc + hc / 2 - 0.17, w: 0.34, h: 0.34, fill: { color: ORANGE }, line: { color: ORANGE, width: 1 } });
    const lw = 2.1, lx = Math.min(gx - lw / 2, 12.83 - lw);
    tb(s, d.puertas[i], { x: lx, y: yc + hc + 0.08, w: lw, h: 0.5, fontSize: 13, bold: true, color: ORANGE, align: lx < gx - lw / 2 ? "right" : "center" });
  });
  tb(s, [{ text: "◆  ", options: { color: ORANGE, bold: true, fontSize: 13 } }, { text: "puerta: decide una persona con autoridad (la «junta»)", options: { color: GRAY, fontSize: 13 } }], { x: 0.5, y: 3.2, w: 12.33, h: 0.3 });
  label(s, d.verif_titulo, 0.5, 3.66, 9, NAVY);
  const vk = d.verif.length + 1, vg = 0.45, vw = (12.33 - vg * (vk - 1)) / vk, yv = 4.0, hv = 1.45;
  d.verif.concat([d.decision]).forEach(([t, x2], i) => {
    const x = 0.5 + i * (vw + vg), dec = i === vk - 1;
    rr(s, x, yv, vw, hv, dec ? ORANGE : BLUETINT);
    if (!dec) circ(s, x + 0.18, yv + 0.16, 0.42, NAVY, String(i + 1), 14);
    tb(s, t, { x: x + (dec ? 0.2 : 0.72), y: yv + 0.16, w: vw - (dec ? 0.4 : 0.9), h: 0.42, fontSize: 15, bold: true, color: dec ? WHITE : NAVY, valign: "middle" });
    fit(s, x2.charAt(0).toUpperCase() + x2.slice(1), x + 0.2, yv + 0.7, vw - 0.4, hv - 0.78, 14, 12.5, { color: dec ? WHITE : CHAR });
    if (i < vk - 1) tb(s, "→", { x: x + vw, y: yv, w: vg, h: hv, fontSize: 22, bold: true, color: ORANGE, align: "center", valign: "middle" });
  });
  rr(s, 0.5, 5.7, 12.33, 0.7, ORTINT);
  fit(s, d.excepcion, 0.75, 5.7, 11.9, 0.7, 16, 13, { bold: true, color: ORANGE, valign: "middle" });
};

R.imagen_puntos = d => {
  const s = slide(d);
  const im = imagen(s, path.join(RAIZ, d.imagen), 0.5, 1.5, 7.6, 4.3);
  fit(s, d.pie, 0.5, 1.5 + im.h + 0.14, 7.6, 0.66, 13, 11.5, { italic: true, color: GRAY });
  const xr = 8.45, wr = 4.38;
  label(s, d.puntos_titulo, xr, 1.42, wr, BLUE);
  const k = d.puntos.length, hp = (4.95 - 0.14 * (k - 1)) / k;
  d.puntos.forEach((p, i) => {
    const y = 1.78 + i * (hp + 0.14);
    rr(s, xr, y, wr, hp, i % 2 ? ORTINT : BLUETINT);
    circ(s, xr + 0.18, y + hp / 2 - 0.22, 0.44, i % 2 ? ORANGE : NAVY, String(i + 1), 14);
    fit(s, p, xr + 0.8, y + 0.1, wr - 0.98, hp - 0.2, 16, 14, { color: NAVY, valign: "middle" });
  });
};

R.ventajas = d => {
  const s = slide(d);
  const w = 6.06, h = 1.72, g = 0.21;
  d.tarjetas.forEach(([t, x2], i) => {
    const x = 0.5 + (i % 2) * (w + g), y = 1.42 + Math.floor(i / 2) * (h + 0.18);
    const calida = i === 1 || i === 2;
    rr(s, x, y, w, h, calida ? ORTINT : BLUETINT);
    circ(s, x + 0.22, y + 0.2, 0.5, calida ? ORANGE : NAVY, String(i + 1), 16);
    tb(s, t, { x: x + 0.9, y: y + 0.2, w: w - 1.1, h: 0.5, fontSize: 18, bold: true, color: NAVY, valign: "middle" });
    fit(s, x2, x + 0.9, y + 0.78, w - 1.1, h - 0.9, 15, 13);
  });
  const yq = 1.42 + 2 * (h + 0.18) + 0.06;
  rr(s, 0.5, yq, 12.33, 0.7, NAVY);
  tb(s, [{ text: "✓  ", options: { color: SKY, bold: true, fontSize: 18 } }, { text: d.calidad, options: { color: WHITE, bold: true, fontSize: 15 } }], { x: 0.75, y: yq, w: 11.9, h: 0.7, valign: "middle" });
  rr(s, 0.5, yq + 0.84, 12.33, 0.6, LT);
  tb(s, d.abierto, { x: 0.75, y: yq + 0.84, w: 11.9, h: 0.6, fontSize: 15, color: NAVY, valign: "middle" });
};

R.cierre = d => {
  const s = slide(d);
  const w = 6.06, y = 1.42, h = 4.5;
  rr(s, 0.5, y, w, h, LT);
  label(s, d.col1_titulo, 0.72, y + 0.18, w - 0.4, NAVY);
  const out = [];
  d.col1.forEach((t, i) => {
    out.push({ text: "▪  ", options: { color: ORANGE, bold: true, fontSize: 15, paraSpaceAfter: 10 } });
    out.push({ text: t, options: { color: CHAR, fontSize: 15, paraSpaceAfter: 10, breakLine: i < d.col1.length - 1 } });
  });
  if (textH(d.col1.join("\n"), w - 0.5, 15) + d.col1.length * 0.14 > h - 0.7) avisos.push(`diapositiva ${n}: límites que pueden no entrar`);
  s.addText(out, { x: 0.72, y: y + 0.6, w: w - 0.44, h: h - 0.75, isTextBox: true, margin: 0, valign: "top" });
  const x2 = 0.5 + w + 0.21;
  rr(s, x2, y, w, h, BLUETINT);
  label(s, d.col2_titulo, x2 + 0.22, y + 0.18, w - 0.4, BLUE);
  D.casos.forEach((c, i) => {
    const yy = y + 0.62 + i * 0.75;
    circ(s, x2 + 0.22, yy + 0.04, 0.46, NAVY, String(i + 1), 14);
    tb(s, c.nombre, { x: x2 + 0.84, y: yy, w: w - 1.05, h: 0.32, fontSize: 15, bold: true, color: NAVY });
    tb(s, `${c.lema} · caso ${c.caso}`, { x: x2 + 0.84, y: yy + 0.32, w: w - 1.05, h: 0.26, fontSize: 12, italic: true, color: GRAY });
  });
  rr(s, 0.5, 6.08, 12.33, 0.74, ORTINT);
  fit(s, d.siguiente, 0.75, 6.08, 11.9, 0.74, 16, 14, { bold: true, color: ORANGE, valign: "middle" });
};

D.diapositivas.forEach(d => {
  if (!R[d.tipo]) throw new Error(`tipo desconocido: ${d.tipo}`);
  R[d.tipo](d);
});

(async () => {
  await pres.writeFile({ fileName: SALIDA });
  await applyTheme(SALIDA, THEME);
  console.log(`${path.relative(RAIZ, SALIDA)} · ${n} diapositivas`);
  avisos.forEach(a => console.log("aviso: " + a));
})();
