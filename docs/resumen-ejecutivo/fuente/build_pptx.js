// Resumen ejecutivo comercial de pm-method · PPTX.
// Uso: node build_pptx.js   (lee datos.json y diagramas/; escribe ../resumen-ejecutivo-pm-method.pptx)
// Estética del Informe 2 (docs/informe/fuente/build_pptx.js): Arial, azul marino, azul y naranja, 13,33" × 7,5".
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
process.chdir(__dirname);
const APPLY_THEME = ["/mnt/skills/public/pptx/scripts/apply_theme.js"].find(p => fs.existsSync(p));
const { applyTheme } = APPLY_THEME ? require(APPLY_THEME) : { applyTheme: async () => {} };
const D = JSON.parse(fs.readFileSync("datos.json", "utf8"));
const T = D.txt, NN = D.n;
const RAIZ = path.resolve(__dirname, "../../..");
const SALIDA = path.resolve(__dirname, "../resumen-ejecutivo-pm-method.pptx");

const THEME = { name: "Resumen pm-method", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "272425", lt1: "FFFFFF", dk2: "002855", lt2: "F4F6F8", accent1: "00629B", accent2: "B5651D", accent3: "002855", accent4: "696969", accent5: "2A78D6", accent6: "EB6834", hlink: "00629B", folHlink: "002855" } };
const NAVY = "002855", BLUE = "00629B", ORANGE = "B5651D", GRAY = "696969", CHAR = "272425", WHITE = "FFFFFF", LT = "F4F6F8",
  BLUETINT = "E9F1F8", ORTINT = "FBF1E6", LINE = "D5DCE3", NAVY2 = "0B3A6E", SKY = "9FD0F0";
// gráfico de datos: paleta categórica de visuales.py (validada con la skill dataviz: azul y naranja, modo claro)
const SERIE_PERM = "EB6834", SERIE_OTRA = "2A78D6";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };
pres.author = "pm-method"; pres.title = "pm-method · Resumen ejecutivo " + D.meta.version;
pres.subject = "Resumen ejecutivo comercial de pm-method";
const W = 13.33, H = 7.5;
const FOOT = `${T.pie} · ${D.meta.fecha}`;

// ---------- layouts (diseño de diapositiva) ----------
const logoBox = (x, y, w, h, color) => [
  { rect: { x, y, w, h, fill: { color: "FFFFFF", transparency: 100 }, line: { color, width: 1, dashType: "dash" } } },
  { text: { text: "Logo IEEE", options: { x, y, w, h, fontSize: 9, color, align: "center", valign: "middle", margin: 0 } } }];
pres.defineSlideMaster({ title: "PORTADA", background: { color: NAVY }, objects: [...logoBox(0.6, 0.5, 2.0, 0.8, SKY)] });
// número de diapositiva: propiedad `slideNumber` del layout (pptxgenjs 4.0.1 ignora un slideNumber dentro de objects)
pres.defineSlideMaster({ title: "CONTENIDO", background: { color: WHITE }, margin: [0.5, 0.5, 0.9, 0.5],
  slideNumber: { x: W - 1.2, y: H - 0.48, w: 0.7, h: 0.3, fontSize: 9, color: GRAY, align: "right" }, objects: [
    ...logoBox(W - 2.2, 0.4, 1.7, 0.78, GRAY),
    { rect: { x: 0.5, y: 0.4, w: 10.45, h: 0.78, fill: { color: BLUE }, rectRadius: 0.1, shape: "roundRect" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 0.4, w: 10.1, h: 0.78, fontSize: 19, bold: true, color: WHITE, margin: 0, valign: "middle", align: "left" } } },
    { text: { text: FOOT, options: { x: 0.5, y: H - 0.48, w: 9, h: 0.3, fontSize: 9, color: GRAY, margin: 0 } } }] });

// ---------- utilidades ----------
const plain = s => String(s || "").replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1");
const clean = s => plain(s).replace(/`/g, "").replace(/\*\*/g, "");
const lines = (t, wIn, pt, em = 0.5) => clean(t).split("\n").reduce((a, p) => a + Math.max(1, Math.ceil(p.length / Math.max(1, (wIn * 72) / (pt * em)))), 0);
const textH = (t, wIn, pt, ls = 1.2, em = 0.5) => lines(t, wIn, pt, em) * pt * ls / 72;
const fitSize = (t, wIn, hIn, max, min = 10) => { let s = max; while (s > min && textH(t, wIn, s) > hIn) s -= 0.5; return s; };
const avisos = [];
const tb = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, fontSize: 12, color: CHAR, valign: "top" }, o));
function runs(md, o = {}) {
  const out = [], size = o.fontSize || 12, color = o.color || CHAR;
  let bold = false;
  plain(md).split(/(`[^`]*`|\*\*)/).forEach(seg => {
    if (!seg) return;
    if (seg === "**") { bold = !bold; return; }
    if (seg.startsWith("`") && seg.endsWith("`") && seg.length > 1)
      out.push({ text: seg.slice(1, -1), options: { fontFace: "Courier New", fontSize: size - 0.5, color: o.codeColor || NAVY, bold: bold || !!o.bold } });
    else out.push({ text: seg, options: { fontSize: size, color, bold: bold || !!o.bold, italic: !!o.italic } });
  });
  return out.length ? out : [{ text: "", options: { fontSize: size } }];
}
// texto ajustado a su caja: baja el cuerpo hasta `min` y avisa si aun así no entra
function fit(s, t, x, y, w, h, max, min, o = {}) {
  const size = fitSize(t, w, h, max, min);
  if (textH(t, w, size) > h + 0.02) avisos.push(`diapositiva ${n}: texto que puede no entrar («${clean(t).slice(0, 50)}…»)`);
  tb(s, runs(t, Object.assign({}, o, { fontSize: size })), Object.assign({ x, y, w, h }, o.box || {}));
  return size;
}
function bullets(s, items, x, y, w, h, max = 13, min = 11, o = {}) {
  const all = items.map(clean).join("\n");
  const size = fitSize(all, w - 0.3, h - items.length * (o.gap || 6) / 72, max, min);
  const out = [];
  items.forEach((t, i) => {
    const r = [{ text: (o.marca || "▪") + "  ", options: { fontSize: size, color: o.marcaColor || BLUE, bold: true } }].concat(runs(t, { fontSize: size, color: o.color || CHAR }));
    r.forEach(z => { z.options = Object.assign({}, z.options, { paraSpaceAfter: o.gap || 6 }); });
    r[r.length - 1].options.breakLine = i < items.length - 1;
    out.push(...r);
  });
  s.addText(out, { x, y, w, h, isTextBox: true, margin: 0, valign: "top" });
}
const rr = (s, x, y, w, h, fill, o = {}) => s.addShape(pres.ShapeType.roundRect, Object.assign({ x, y, w, h, fill: { color: fill }, rectRadius: 0.08, line: { color: o.line || fill, width: o.lw || 0.75 } }, o.extra || {}));
function codeBox(s, code, x, y, w, h, max = 11, min = 9) {
  rr(s, x, y, w, h, "0F2238");
  const ls = code.split("\n");
  const wrapped = sz => ls.reduce((a, l) => a + Math.max(1, Math.ceil(l.length / ((w - 0.3) * 72 / (sz * 0.6)))), 0);
  let size = max;
  const longest = Math.max(...ls.map(l => l.length));
  while (size > min && longest * size * 0.6 / 72 > w - 0.3) size -= 0.5;
  while (size > min && wrapped(size) * size * 1.2 / 72 > h - 0.18) size -= 0.5;
  if (wrapped(size) * size * 1.2 / 72 > h - 0.12) avisos.push(`diapositiva ${n}: código que puede no entrar`);
  s.addText(code, { x: x + 0.15, y: y + 0.09, w: w - 0.3, h: h - 0.18, fontFace: "Courier New", fontSize: size, color: "E8EEF5", margin: 0, valign: "top", isTextBox: true });
}
function imagen(s, file, x, y, w, h) {
  const png = fs.readFileSync(file);
  const iw = png.readUInt32BE(16), ih = png.readUInt32BE(20);
  let ww = w, hh = ww * ih / iw;
  if (hh > h) { hh = h; ww = hh * iw / ih; }
  const xx = x + (w - ww) / 2;
  s.addImage({ path: file, x: xx, y, w: ww, h: hh });
  return { x: xx, w: ww, h: hh };
}
const label = (s, t, x, y, w, color = ORANGE) => tb(s, t.toUpperCase(), { x, y, w, h: 0.26, fontSize: 10, bold: true, color, charSpacing: 1 });

let n = 0;
function slide(sec, titulo, en) {
  n++;
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: sec });
  s.addText(titulo, { placeholder: "title" });
  if (textH(titulo, 10.1, 19, 1.15) > 0.78) avisos.push(`diapositiva ${n}: título largo`);
  if (en) s.addNotes(en);
  return s;
}

// =============================================================== 1 · Portada
const S0 = "Propuesta"; pres.addSection({ title: S0 });
{
  n++;
  const s = pres.addSlide({ masterName: "PORTADA", sectionTitle: S0 });
  const P = T.portada;
  tb(s, P.kicker, { x: 0.6, y: 1.75, w: 11, h: 0.4, fontSize: 15, bold: true, color: SKY });
  fit(s, P.titulo, 0.6, 2.2, 11.6, 1.6, 36, 28, { color: WHITE, bold: true });
  fit(s, P.subtitulo, 0.6, 3.9, 11.2, 0.9, 16, 13, { color: WHITE });
  const k = P.cifras.length, gap = 0.18, w = (12.13 - gap * (k - 1)) / k;
  P.cifras.forEach(([v, t], i) => {
    const x = 0.6 + i * (w + gap);
    rr(s, x, 5.05, w, 1.15, NAVY2);
    tb(s, v, { x: x + 0.2, y: 5.13, w: w - 0.4, h: 0.6, fontSize: 30, bold: true, color: WHITE });
    tb(s, t, { x: x + 0.2, y: 5.73, w: w - 0.3, h: 0.4, fontSize: 12, color: SKY });
  });
  tb(s, `pm-method ${D.meta.version} · ${D.meta.fecha_larga}`, { x: 0.6, y: 6.55, w: 8, h: 0.3, fontSize: 11, color: WHITE });
  tb(s, P.en, { x: 0.6, y: 6.85, w: 12, h: 0.3, fontSize: 9.5, color: SKY, italic: true });
  s.addNotes(P.en);
}

// =============================================================== 2 · Problema y propuesta de valor
{
  const P = T.problema;
  const s = slide(S0, P.titulo, P.en);
  label(s, P.col_hoy, 0.5, 1.4, 5, GRAY); label(s, P.col_pm, 6.05, 1.4, 5, BLUE); label(s, "Control", 11.3, 1.4, 1.5, NAVY);
  const g = 0.1, y0 = 1.75, rh = Math.min(0.62, (4.45 - g * (P.filas.length - 1)) / P.filas.length);
  P.filas.forEach(([hoy, pm, cod], i) => {
    const y = y0 + i * (rh + g);
    rr(s, 0.5, y, 5.1, rh, LT);
    fit(s, hoy, 0.66, y + 0.06, 4.8, rh - 0.12, 13, 11, { color: CHAR, box: { valign: "middle" } });
    tb(s, "→", { x: 5.62, y, w: 0.4, h: rh, fontSize: 18, bold: true, color: ORANGE, align: "center", valign: "middle" });
    rr(s, 6.05, y, 5.1, rh, BLUETINT);
    fit(s, pm, 6.2, y + 0.06, 4.8, rh - 0.12, 13, 11, { color: NAVY, box: { valign: "middle" } });
    rr(s, 11.3, y + 0.1, 1.53, rh - 0.2, NAVY);
    tb(s, cod, { x: 11.3, y: y + 0.1, w: 1.53, h: rh - 0.2, fontSize: 10, bold: true, color: WHITE, fontFace: "Courier New", align: "center", valign: "middle" });
  });
  const yl = y0 + P.filas.length * (rh + g) + 0.05;
  rr(s, 0.5, yl, 12.33, 0.5, ORTINT);
  tb(s, D.lema, { x: 0.7, y: yl, w: 12, h: 0.5, fontSize: 15, bold: true, italic: true, color: ORANGE, valign: "middle" });
}

// =============================================================== 3 · Para quién
{
  const P = T.perfiles;
  const s = slide(S0, P.titulo, P.en);
  D.perfiles.forEach((p, i) => {
    const x = 0.5 + (i % 2) * 6.27, y = 1.45 + Math.floor(i / 2) * 2.68, w = 6.06, h = 2.5;
    rr(s, x, y, w, h, i % 2 === Math.floor(i / 2) % 2 ? BLUETINT : ORTINT);
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.22, y: y + 0.22, w: 0.5, h: 0.5, fill: { color: i % 2 === Math.floor(i / 2) % 2 ? NAVY : ORANGE }, line: { color: WHITE, width: 0 } });
    tb(s, String(i + 1), { x: x + 0.22, y: y + 0.22, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle" });
    tb(s, p.titulo, { x: x + 0.88, y: y + 0.24, w: w - 1.1, h: 0.46, fontSize: 17, bold: true, color: NAVY, valign: "middle" });
    label(s, P.obtiene, x + 0.25, y + 0.88, 3, GRAY);
    fit(s, p.obtiene.charAt(0).toUpperCase() + p.obtiene.slice(1) + ".", x + 0.25, y + 1.14, w - 0.5, 0.78, 14, 12);
    tb(s, [{ text: P.empieza + ": ", options: { bold: true, color: ORANGE, fontSize: 12 } }, { text: p.empieza, options: { color: CHAR, fontSize: 12 } }], { x: x + 0.25, y: y + 1.98, w: w - 0.5, h: 0.36 });
  });
}

// =============================================================== 4 · Qué es
const S1 = "Producto"; pres.addSection({ title: S1 });
{
  const P = T.que_es;
  const s = slide(S1, P.titulo, P.en);
  label(s, P.jerarquia, 0.5, 1.4, 5);
  const fills = [NAVY, BLUE, "4F86B5", BLUETINT], tcol = [WHITE, WHITE, WHITE, NAVY];
  D.jerarquia.forEach((c, i) => {
    const y = 1.72 + i * 1.08, ind = i * 0.18;
    rr(s, 0.5 + ind, y, 5.75 - ind, 0.96, fills[i]);
    tb(s, `${i + 1} · ${c.capa}`, { x: 0.7 + ind, y: y + 0.08, w: 5.4 - ind, h: 0.32, fontSize: 15, bold: true, color: tcol[i] });
    fit(s, c.rol.charAt(0).toUpperCase() + c.rol.slice(1), 0.7 + ind, y + 0.42, 5.4 - ind, 0.5, 12, 10.5, { color: tcol[i] });
  });
  P.kpis.forEach(([v, t, d], i) => {
    const x = 6.55 + (i % 2) * 3.2, y = 1.45 + Math.floor(i / 2) * 1.5;
    rr(s, x, y, 3.08, 1.38, LT);
    tb(s, [{ text: v + "  ", options: { fontSize: 32, bold: true, color: NAVY } }, { text: t, options: { fontSize: 14, bold: true, color: BLUE } }], { x: x + 0.2, y: y + 0.1, w: 2.8, h: 0.62, valign: "bottom" });
    fit(s, d, x + 0.2, y + 0.78, 2.75, 0.52, 11.5, 10, { color: GRAY });
  });
  fit(s, P.nota, 0.5, 6.18, 12.33, 0.5, 12, 10.5, { color: GRAY });
}

// =============================================================== 5 · Arquitectura
{
  const P = T.arquitectura;
  const s = slide(S1, P.titulo, P.en);
  imagen(s, D.diagramas.arquitectura, 0.5, 1.42, 12.33, 4.05);
  P.puntos.forEach(([t, d], i) => {
    const x = 0.5 + i * 4.18, y = 5.62;
    rr(s, x, y, 3.97, 1.2, i === 0 ? ORTINT : BLUETINT);
    tb(s, t, { x: x + 0.18, y: y + 0.1, w: 3.6, h: 0.3, fontSize: 13, bold: true, color: i === 0 ? ORANGE : NAVY });
    fit(s, d, x + 0.18, y + 0.42, 3.62, 0.72, 11.5, 10);
  });
}

// =============================================================== 6 · Componentes
{
  const P = T.componentes;
  const s = slide(S1, P.titulo, P.en);
  const k = D.agentes.length, gap = 0.12, w = (12.33 - gap * (k - 1)) / k;
  D.agentes.forEach((a, i) => {
    const x = 0.5 + i * (w + gap);
    const sk = D.skills.filter(z => z.agente === a.nombre).sort((p, q) => (p.comando - q.comando) || p.nombre.localeCompare(q.nombre));
    const fill = a.nombre === "pm-director" ? ORANGE : NAVY;
    rr(s, x, 1.42, w, 1.3, fill);
    tb(s, a.nombre, { x: x + 0.12, y: 1.5, w: w - 0.24, h: 0.3, fontSize: 12, bold: true, color: WHITE });
    tb(s, [{ text: String(sk.length), options: { fontSize: 22, bold: true, color: WHITE } }, { text: "  skills", options: { fontSize: 11, color: WHITE } }], { x: x + 0.12, y: 1.8, w: w - 0.24, h: 0.4, valign: "middle" });
    fit(s, P.roles[a.nombre] || "", x + 0.12, 2.22, w - 0.24, 0.46, 10, 9, { color: a.nombre === "pm-director" ? "FFF2E6" : SKY });
    rr(s, x, 2.82, w, 3.6, LT);
    const items = sk.map(z => z.nombre + (z.comando ? "  ·  " + P.comando : ""));
    const size = fitSize(items.join("\n"), w - 0.26, 3.4 - items.length * 0.05, 11, 9);
    const out = [];
    sk.forEach((z, j) => {
      out.push({ text: z.nombre, options: { fontSize: size, color: z.comando ? ORANGE : CHAR, bold: z.comando, breakLine: !z.comando && j < sk.length - 1, paraSpaceAfter: 4 } });
      if (z.comando) out.push({ text: "  " + P.comando, options: { fontSize: size - 1.5, color: GRAY, italic: true, breakLine: j < sk.length - 1, paraSpaceAfter: 4 } });
    });
    s.addText(out, { x: x + 0.13, y: 2.94, w: w - 0.2, h: 3.4, isTextBox: true, margin: 0, valign: "top" });
  });
  fit(s, P.nota, 0.5, 6.5, 12.33, 0.36, 10.5, 9.5, { color: GRAY });
}

// =============================================================== 7 · Ciclo de vida
{
  const P = T.ciclo;
  const s = slide(S1, P.titulo, P.en);
  rr(s, 0.5, 1.4, 12.33, 0.42, NAVY);
  tb(s, P.direccion, { x: 0.7, y: 1.4, w: 12, h: 0.42, fontSize: 12, bold: true, color: WHITE, valign: "middle" });
  const k = D.ciclo.length, g = 0.42, w = (12.33 - g * k) / k, yc = 2.36, hc = 0.86;
  const puertas = ["autorizar-inicio", "autorizar-proyecto + autorizar-etapa", "límite de etapa", "cierre", "autorizar-cierre"];
  D.ciclo.forEach((c, i) => {
    const x = 0.5 + i * (w + g);
    s.addShape(i === 0 ? pres.ShapeType.homePlate : pres.ShapeType.chevron, { x, y: yc, w, h: hc, fill: { color: [BLUE, BLUE, NAVY, "4F86B5", BLUE][i] || BLUE }, line: { color: WHITE, width: 0 } });
    tb(s, [{ text: c.codigo + "\n", options: { fontSize: 15, bold: true, color: WHITE } }, { text: c.nombre, options: { fontSize: 11, color: WHITE } }], { x: x + (i ? 0.5 : 0.16), y: yc, w: w - (i ? 0.8 : 0.5), h: hc, valign: "middle" });
    // puerta o transición a la derecha del proceso
    const gx = x + w + g / 2, esPuerta = !puertas[i].startsWith("límite") && puertas[i] !== "cierre";
    s.addShape(pres.ShapeType.diamond, { x: gx - 0.13, y: yc + hc / 2 - 0.13, w: 0.26, h: 0.26, fill: { color: esPuerta ? ORANGE : WHITE }, line: { color: esPuerta ? ORANGE : GRAY, width: 1.25 } });
    const lw = 2.3, lx = Math.min(gx - lw / 2, 12.83 - lw);
    tb(s, puertas[i], { x: lx, y: 1.88, w: lw, h: 0.44, fontSize: 9.5, bold: esPuerta, color: esPuerta ? ORANGE : GRAY, align: lx < gx - lw / 2 ? "right" : "center", valign: "bottom" });
    // detalle bajo el proceso
    const yd = yc + hc + 0.1;
    tb(s, c.etapa, { x, y: yd, w: w + 0.3, h: 0.24, fontSize: 10, italic: true, color: GRAY });
    tb(s, c.agentes.join(" + "), { x, y: yd + 0.25, w: w + 0.3, h: 0.4, fontSize: 10.5, bold: true, color: BLUE });
    fit(s, c.produce, x, yd + 0.66, w + 0.3, 0.56, 11, 9.5, { color: CHAR });
    const yb = yd + 1.26, hb = 5.98 - yb;
    rr(s, x, yb, w + 0.3, hb, LT);
    const sz = fitSize(c.skills.join("\n"), w + 0.1, hb - 0.14, 10, 8.5);
    if (textH(c.skills.join("\n"), w + 0.1, sz) > hb - 0.1) avisos.push(`diapositiva ${n}: skills de ${c.codigo} no entran`);
    tb(s, c.skills.join("\n"), { x: x + 0.1, y: yb + 0.08, w: w + 0.12, h: hb - 0.14, fontSize: sz, color: NAVY });
  });
  tb(s, [{ text: "◆  ", options: { color: ORANGE, bold: true, fontSize: 11 } }, { text: "puerta de la junta     ", options: { color: GRAY, fontSize: 10 } }, { text: "◇  ", options: { color: GRAY, bold: true, fontSize: 11 } }, { text: "transición que prepara el gestor     ", options: { color: GRAY, fontSize: 10 } }, { text: "SB → CS: autorizar-etapa (n+1)     ·     " + P.excepcion, options: { color: ORANGE, fontSize: 10, bold: true } }], { x: 0.5, y: 6.06, w: 12.33, h: 0.28 });
  fit(s, P.antes, 0.5, 6.4, 12.33, 0.44, 10.5, 9.5, { color: GRAY });
}

// =============================================================== 8 · Controles permanentes
{
  const P = T.controles;
  const s = slide(S1, P.titulo, P.en);
  const fam = D.controles.familias.slice().sort((a, b) => b.codigos.length - a.codigos.length || a.familia.localeCompare(b.familia));
  label(s, P.grafico, 0.5, 1.4, 6.6, NAVY);
  tb(s, [{ text: "■ ", options: { color: SERIE_PERM, fontSize: 12 } }, { text: P.leyenda_perm + "     ", options: { color: CHAR, fontSize: 10.5 } }, { text: "■ ", options: { color: SERIE_OTRA, fontSize: 12 } }, { text: P.leyenda_otro, options: { color: CHAR, fontSize: 10.5 } }], { x: 0.5, y: 1.68, w: 6.6, h: 0.28 });
  const cats = fam.map(f => `${f.familia} · ${f.nombre}`).reverse();
  const perm = fam.map(f => f.permanente ? f.codigos.length : 0).reverse();
  const otra = fam.map(f => f.permanente ? 0 : f.codigos.length).reverse();
  s.addChart(pres.ChartType.bar, [{ name: P.leyenda_perm, labels: cats, values: perm }, { name: P.leyenda_otro, labels: cats, values: otra }], {
    x: 0.4, y: 1.98, w: 6.8, h: 4.2, barDir: "bar", barGrouping: "stacked", barGapWidthPct: 45, chartColors: [SERIE_PERM, SERIE_OTRA],
    showLegend: false, showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: "0;;;", dataLabelColor: WHITE, dataLabelFontSize: 9, dataLabelFontBold: true,
    catAxisLabelColor: CHAR, catAxisLabelFontSize: 9.5, catAxisLabelFontFace: "+mn-lt", valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    catAxisLineShow: false, dataLabelFontFace: "+mn-lt" });
  fit(s, P.puerta, 0.5, 6.26, 6.6, 0.5, 11.5, 10, { color: NAVY, bold: true });
  label(s, P.ejemplos_titulo, 7.45, 1.4, 5.4, NAVY);
  const ej = D.controles.ejemplos, hh = (5.1 - 0.1 * (ej.length - 1)) / ej.length;
  ej.forEach((e, i) => {
    const y = 1.75 + i * (hh + 0.1);
    rr(s, 7.45, y, 5.38, hh, i % 2 ? BLUETINT : ORTINT);
    rr(s, 7.6, y + 0.12, 1.05, 0.32, NAVY);
    tb(s, e.codigo, { x: 7.6, y: y + 0.12, w: 1.05, h: 0.32, fontSize: 10, bold: true, color: WHITE, fontFace: "Courier New", align: "center", valign: "middle" });
    tb(s, e.caso, { x: 8.75, y: y + 0.12, w: 1.5, h: 0.32, fontSize: 11, bold: true, color: ORANGE, valign: "middle" });
    fit(s, e.texto, 7.6, y + 0.5, 5.08, hh - 0.58, 11.5, 9.5);
  });
}

// =============================================================== 9 · Decidir con contexto y buscar con evidencia
{
  const P = T.decidir;
  const s = slide(S1, P.titulo, P.en);
  [[P.col1, P.puntos1, D.decidir.img1, NAVY], [P.col2, P.puntos2, D.decidir.img2, BLUE]].forEach(([t, pts, im, col], k) => {
    const x = 0.5 + k * 6.27, w = 6.06;
    rr(s, x, 1.38, w, 5.0, k ? BLUETINT : LT);
    label(s, t, x + 0.2, 1.5, w - 0.4, col);
    bullets(s, pts, x + 0.2, 1.84, w - 0.4, 1.95, 12.5, 10.5, { gap: 4 });
    const r = imagen(s, path.join(RAIZ, im.archivo), x + 0.2, 3.86, w - 0.4, 2.15);
    tb(s, im.alt, { x: x + 0.2, y: 3.86 + r.h + 0.04, w: w - 0.4, h: 0.26, fontSize: 9.5, italic: true, color: GRAY, align: "center" });
  });
  rr(s, 0.5, 6.48, 12.33, 0.36, NAVY);
  tb(s, P.codigos, { x: 0.7, y: 6.48, w: 12, h: 0.36, fontSize: 11, bold: true, color: WHITE, valign: "middle" });
}

// =============================================================== 10 · Integraciones
{
  const P = T.integraciones;
  const s = slide(S1, P.titulo, P.en);
  const cx = W / 2, cy = 3.95, r = 1.0;
  const nd = P.nodos, filas = Math.ceil(nd.length / 2), ch = 1.45, gy = (4.75 - filas * ch) / Math.max(1, filas - 1);
  nd.forEach((z, i) => {
    const izq = i < filas, fila = izq ? i : i - filas;
    const x = izq ? 0.5 : 8.68, y = 1.45 + fila * (ch + gy), w = 4.15;
    s.addShape(pres.ShapeType.line, { x: izq ? x + w : cx + r * 0.75, y: Math.min(y + ch / 2, cy), w: izq ? (cx - r * 0.75) - (x + w) : x - (cx + r * 0.75), h: Math.abs(y + ch / 2 - cy) || 0.001, line: { color: "AFC0D0", width: 1.25 }, flipV: (izq ? (y + ch / 2 > cy) : (y + ch / 2 < cy)) });
    rr(s, x, y, w, ch, i % 3 === 0 ? ORTINT : BLUETINT);
    tb(s, z.nombre, { x: x + 0.18, y: y + 0.1, w: w - 0.36, h: 0.3, fontSize: 13.5, bold: true, color: NAVY });
    tb(s, z.valores, { x: x + 0.18, y: y + 0.4, w: w - 0.36, h: 0.26, fontSize: 9.5, bold: true, color: i % 3 === 0 ? ORANGE : BLUE });
    fit(s, z.texto, x + 0.18, y + 0.68, w - 0.36, ch - 0.74, 11, 9.5);
  });
  s.addShape(pres.ShapeType.ellipse, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { color: NAVY }, line: { color: WHITE, width: 0 } });
  tb(s, P.centro, { x: cx - r + 0.1, y: cy - 0.42, w: 2 * r - 0.2, h: 0.4, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "bottom" });
  tb(s, P.centro_sub, { x: cx - r + 0.25, y: cy + 0.02, w: 2 * r - 0.5, h: 0.5, fontSize: 10, color: SKY, align: "center" });
  fit(s, P.nota, 0.5, 6.42, 12.33, 0.42, 11, 10, { color: GRAY });
}

// =============================================================== 11 · Catálogo E2E y webinar
const S2 = "Casos E2E"; pres.addSection({ title: S2 });
{
  const P = T.catalogo;
  const s = slide(S2, P.titulo, P.en);
  const web = Object.fromEntries(D.webinar.map(w => [w.caso, w]));
  const hdr = t => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 11.5, valign: "middle" } });
  const rows = [P.cab.map(hdr)];
  D.casos.forEach(c => {
    const w = web[c.id] || {};
    const cel = (t, o = {}) => ({ text: String(t ?? "—"), options: Object.assign({ fontSize: 12, color: CHAR, valign: "middle" }, o) });
    rows.push([cel(c.id, { bold: true, color: NAVY }), cel(P.recorre[c.id] || c.titulo_guia), cel(c.pasos, { align: "center" }), cel(w.clases, { align: "center" }),
      cel(w.minutos, { align: "center" }), cel(w.diapositivas, { align: "center" }), cel(w.glosario, { align: "center" })]);
  });
  s.addTable(rows, { x: 0.5, y: 1.42, w: 12.33, colW: [1.0, 6.33, 0.85, 0.85, 1.0, 1.25, 1.05], rowH: [0.42].concat(D.casos.map(() => 0.56)), border: { type: "solid", color: LINE, pt: 0.75 }, fontFace: "Arial", margin: 0.07, autoPage: false });
  const yb = 1.42 + 0.42 + D.casos.length * 0.56 + 0.3;
  [[P.material, BLUETINT, NAVY, "Material por caso"], [P.induccion, ORTINT, ORANGE, "Inducción"]].forEach(([t, f, c, l], i) => {
    const x = 0.5 + i * 6.27;
    rr(s, x, yb, 6.06, 6.82 - yb, f);
    label(s, l, x + 0.2, yb + 0.14, 5, c);
    fit(s, t.replace(/^[^:]+:\s*/, ""), x + 0.2, yb + 0.46, 5.66, 6.82 - yb - 0.56, 15, 12);
  });
}

// =============================================================== 12–16 · Casos
{
  const R = T.casos.rotulos;
  D.casos.forEach(c => {
    const C = T.casos[c.id];
    const s = slide(S2, C.titulo, T.casos.en + " · " + c.archivo);
    const xl = 0.5, wl = 5.6;
    label(s, R.problema, xl, 1.42, wl);
    fit(s, C.problema, xl, 1.7, wl, 0.82, 13.5, 11.5, { color: CHAR });
    label(s, R.muestra, xl, 2.58, wl, BLUE);
    bullets(s, C.muestra, xl, 2.86, wl, 1.42, 12.5, 11);
    label(s, R.indicadores, xl, 4.32, wl, NAVY);
    rr(s, xl, 4.6, wl, 2.22, LT);
    const it = c.indicadores;
    const size = fitSize(it.join("\n"), wl - 0.6, 2.05 - it.length * 0.06, 11.5, 9.5);
    if (textH(it.join("\n"), wl - 0.6, size) > 2.05) avisos.push(`diapositiva ${n}: indicadores que pueden no entrar`);
    const out = [];
    it.forEach((t, j) => {
      out.push({ text: "●  ", options: { fontSize: size, color: ORANGE, bold: true, paraSpaceAfter: 5 } });
      out.push({ text: t, options: { fontSize: size, color: CHAR, paraSpaceAfter: 5, breakLine: j < it.length - 1 } });
    });
    s.addText(out, { x: xl + 0.15, y: 4.7, w: wl - 0.3, h: 2.05, isTextBox: true, margin: 0, valign: "top" });
    const im = imagen(s, path.join(RAIZ, c.imagen.archivo), 6.35, 1.42, 6.48, 4.65);
    tb(s, c.imagen.alt, { x: 6.35, y: 1.42 + im.h + 0.06, w: 6.48, h: 0.28, fontSize: 10, italic: true, color: GRAY, align: "center" });
    const ficha = R.ficha.replace("[pasos]", c.pasos).replace("[clases]", c.clases).replace("[archivo]", c.archivo);
    rr(s, 6.35, 6.45, 6.48, 0.37, BLUETINT);
    tb(s, ficha, { x: 6.5, y: 6.45, w: 6.2, h: 0.37, fontSize: 10.5, bold: true, color: NAVY, valign: "middle" });
  });
}

// =============================================================== 17 · Calidad y confianza
const S3 = "Confianza y adopción"; pres.addSection({ title: S3 });
{
  const P = T.calidad;
  const s = slide(S3, P.titulo, P.en);
  P.kpis.forEach(([v, t, d], i) => {
    const x = 0.5 + i * 3.13, w = 2.95;
    rr(s, x, 1.42, w, 1.32, NAVY);
    tb(s, v, { x: x + 0.18, y: 1.48, w: w - 0.3, h: 0.56, fontSize: 28, bold: true, color: WHITE });
    tb(s, t, { x: x + 0.18, y: 2.04, w: w - 0.3, h: 0.3, fontSize: 12, bold: true, color: SKY });
    tb(s, d, { x: x + 0.18, y: 2.34, w: w - 0.3, h: 0.34, fontSize: 10, color: WHITE });
  });
  const y = 2.92, h = 3.45, w = 4.0;
  // pruebas en vivo
  rr(s, 0.5, y, w, h, LT);
  label(s, P.vivo, 0.68, y + 0.12, w - 0.3, NAVY);
  const corto = t => { let x = t.replace(/^suite\.py\s+/, "").replace(/\s*\(.*$/, "").replace(/,\s*\d.*$/, "").replace(/\s*--skills-extra\s+<[^>]*>/, " con skills de BMAD").replace(/\s+/g, " ").trim(); return x.length > 44 ? x.slice(0, 43) + "…" : x; };
  const vivo = D.vivo.slice(-8);
  const vs = vivo.length ? fitSize(vivo.map(v => corto(v.prueba) + "  " + v.resultado).join("\n"), w - 0.4, h - 0.6, 11, 9) : 10;
  tb(s, vivo.flatMap((v, j) => [{ text: v.resultado + "  ", options: { fontSize: vs, bold: true, color: ORANGE } }, { text: corto(v.prueba) + "  ", options: { fontSize: vs, color: CHAR } }, { text: v.fecha.slice(5).split("-").reverse().join("/"), options: { fontSize: vs - 1, color: GRAY, breakLine: j < vivo.length - 1, paraSpaceAfter: 4 } }]), { x: 0.68, y: y + 0.48, w: w - 0.36, h: h - 0.56 });
  // seguridad
  const x2 = 0.5 + w + 0.165;
  rr(s, x2, y, w, h, LT);
  label(s, P.seguridad + " · " + D.seguridad.fecha, x2 + 0.18, y + 0.12, w - 0.3, NAVY);
  const hdr = t => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10 } });
  const filas = [[hdr("Severidad"), hdr("Hallazgos"), hdr("Corregidos")]].concat(D.seguridad.filas.map(f => [f.severidad, f.cantidad, f.corregidos].map(t => ({ text: t.replace("—", "–"), options: { fontSize: 10, color: CHAR } }))));
  s.addTable(filas, { x: x2 + 0.18, y: y + 0.5, w: w - 0.36, colW: [1.05, 0.9, w - 0.36 - 1.95], border: { type: "solid", color: LINE, pt: 0.5 }, fontFace: "Arial", margin: 0.05, autoPage: false });
  tb(s, "Sin hallazgos de severidad alta. Detalle y estado de cada uno en docs/SEGURIDAD.md.", { x: x2 + 0.18, y: y + h - 0.72, w: w - 0.36, h: 0.6, fontSize: 10, color: GRAY });
  // docker
  const x3 = x2 + w + 0.165;
  rr(s, x3, y, w, h, LT);
  label(s, P.docker, x3 + 0.18, y + 0.12, w - 0.3, NAVY);
  bullets(s, D.empezar.docker_seguridad.slice(0, 6), x3 + 0.18, y + 0.5, w - 0.36, h - 0.6, 11, 9.5, { gap: 4 });
  fit(s, P.nota, 0.5, 6.45, 12.33, 0.4, 10.5, 9.5, { color: GRAY });
}

// =============================================================== 18 · Cómo empezar
{
  const P = T.empezar, E = D.empezar;
  const s = slide(S3, P.titulo, P.en);
  rr(s, 0.5, 1.42, 6.06, 5.4, BLUETINT);
  label(s, P.manual, 0.7, 1.58, 5.6, NAVY);
  codeBox(s, E.manual.join("\n"), 0.7, 1.95, 5.66, 0.82, 11, 9);
  label(s, P.luego, 0.7, 2.98, 5.6, BLUE);
  fit(s, E.luego, 0.7, 3.28, 5.66, 0.75, 15, 12, { color: NAVY, bold: true });
  rr(s, 0.7, 4.2, 5.66, 2.42, ORTINT);
  fit(s, P.siguiente, 0.9, 4.34, 5.26, 2.14, 15, 12, { color: ORANGE, bold: true });
  rr(s, 6.77, 1.42, 6.06, 5.4, LT);
  label(s, P.docker, 6.97, 1.58, 5.6, NAVY);
  E.docker.forEach((c, i) => {
    const y = 2.0 + i * 1.45;
    tb(s, `${i + 1} · ${P.docker_pasos[i] || ""}`, { x: 6.97, y, w: 5.6, h: 0.32, fontSize: 13, bold: true, color: BLUE });
    codeBox(s, c, 6.97, y + 0.38, 5.66, c.length * 11 * 0.6 / 72 > 5.36 ? 0.72 : 0.5, 11, 9);
  });
}

// =============================================================== 19 · Glosario
{
  const P = T.glosario;
  const s = slide(S3, P.titulo, P.en);
  const g = D.glosario, mitad = Math.ceil(g.length / 2);
  // tamaño del glosario: el mayor que entra en las dos columnas
  let GS = 11;
  const altura = (parte, z) => parte.reduce((a, t) => a + Math.max(textH(t.definicion, 4.1, z, 1.17), textH(t.termino, 1.6, z, 1.17)) + 0.1, 0.3);
  while (GS > 9 && Math.max(altura(g.slice(0, mitad), GS), altura(g.slice(mitad), GS)) > 5.3) GS -= 0.5;
  [g.slice(0, mitad), g.slice(mitad)].forEach((parte, k) => {
    const hdr = t => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 10 } });
    const rows = [[hdr("Término"), hdr("Definición")]].concat(parte.map(t => [
      { text: t.termino, options: { bold: true, color: NAVY, fontSize: GS, valign: "top" } },
      { text: t.definicion, options: { color: CHAR, fontSize: GS, valign: "top" } }]));
    const tot = parte.reduce((a, t) => a + Math.max(textH(t.definicion, 4.1, GS, 1.17), textH(t.termino, 1.6, GS, 1.17)) + 0.1, 0.3);
    if (tot > 5.35) avisos.push(`diapositiva ${n}: glosario largo (${tot.toFixed(2)} in)`);
    s.addTable(rows, { x: 0.5 + k * 6.27, y: 1.42, w: 6.06, colW: [1.75, 4.31], border: { type: "solid", color: LINE, pt: 0.5 }, fontFace: "Arial", margin: 0.05, autoPage: false });
  });
}

(async () => {
  await pres.writeFile({ fileName: SALIDA });
  await applyTheme(SALIDA, THEME);
  console.log(`${path.relative(process.cwd(), SALIDA)} · ${n} diapositivas`);
  avisos.forEach(a => console.log("aviso: " + a));
})();
