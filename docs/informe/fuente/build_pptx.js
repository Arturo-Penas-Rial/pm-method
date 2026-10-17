// Informe 2 v2.1 · PPTX. Uso: node build_pptx.js  (lee data.json y diagramas/*.png; escribe salida-v2.1/informe-2-ecosistema-pm-method-v2.1.pptx)
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
process.chdir(__dirname);
const APPLY_THEME = ["/mnt/skills/public/pptx/scripts/apply_theme.js",
  "/root/.claude/skills/synced/13cdda2a-8136-454a-bc56-c7c7faefa19b_3263a8e9-6a66-4a7e-b8ab-e05685d7e167/pptx/scripts/apply_theme.js"].find(p => fs.existsSync(p));
const { applyTheme } = APPLY_THEME ? require(APPLY_THEME) : { applyTheme: async () => {} };
const D = JSON.parse(fs.readFileSync("data.json", "utf8"));
const X = D.x;
fs.mkdirSync("salida-v2.1", { recursive: true });
const SALIDA = "salida-v2.1/informe-2-ecosistema-pm-method-v2.1.pptx";

const THEME = { name: "Informe", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "272425", lt1: "FFFFFF", dk2: "002855", lt2: "F4F6F8", accent1: "00629B", accent2: "B5651D", accent3: "002855", accent4: "696969", accent5: "272425", accent6: "00629B", hlink: "00629B", folHlink: "002855" } };
const NAVY = "002855", BLUE = "00629B", ORANGE = "B5651D", GRAY = "696969", CHAR = "272425", WHITE = "FFFFFF", LT = "F4F6F8", BLUETINT = "E9F1F8", ORTINT = "FBF1E6", LINE = "E2E2E6";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };
pres.author = D.meta.autor; pres.title = D.meta.titulo;
const W = 13.33, H = 7.5;
const FOOT = `${D.meta.corto} · ${D.meta.version} · ${D.meta.fecha} · ${D.meta.autor}`;
const HAS_LOGO = fs.existsSync("logo.png");
const logo = HAS_LOGO ? fs.readFileSync("logo.png").toString("base64") : null;
const logoObj = (x, y, w, h) => HAS_LOGO ? [{ image: { x, y, w, h, data: "image/png;base64," + logo } }] : [];

pres.defineSlideMaster({ title: "COVER", background: { color: NAVY }, objects: [
  ...logoObj(0.6, 0.5, 2.2, 0.88),
  { text: { text: FOOT, options: { x: 0.6, y: H - 0.55, w: 9, h: 0.3, fontSize: 10, color: WHITE, margin: 0 } } }] });
pres.defineSlideMaster({ title: "CONTENT", background: { color: WHITE }, margin: [0.5, 0.5, 0.9, 0.5], objects: [
  ...logoObj(W - 2.3, 0.35, 1.7, 0.68),
  { rect: { x: 0.5, y: 0.4, w: HAS_LOGO ? 9.6 : 12.33, h: 0.78, fill: { color: BLUE }, rectRadius: 0.1, shape: "roundRect" } },
  { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 0.4, w: HAS_LOGO ? 9.3 : 11.9, h: 0.78, fontSize: 21, bold: true, color: WHITE, margin: 0, valign: "middle" } } },
  { text: { text: FOOT, options: { x: 0.5, y: H - 0.5, w: 9, h: 0.3, fontSize: 9, color: GRAY, margin: 0 } } },
  { slideNumber: { x: W - 1.2, y: H - 0.5, w: 0.7, h: 0.3, fontSize: 9, color: GRAY, align: "right" } }] });

let n = 0;
const INDEX = [];
const slide = (sec) => { n++; return pres.addSlide({ masterName: "CONTENT", sectionTitle: sec }); };
const mark = label => INDEX.push([label, n + 1]);
const tb = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, fontSize: 12, color: CHAR, valign: "top" }, o));
// Markdown → texto plano para estimar y para runs: enlaces [x](y) → x; *cursiva* → texto
const plain = s => String(s || "").replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1").replace(/(^|[^\w*\\])\*([^\s*][^*]*?)\*(?![\w*])/g, "$1$2").replace(/\\\*/g, "*").replace(/\\\|/g, "|");
const clean = s => plain(s).replace(/`/g, "").replace(/\*\*/g, "");
// estimación de alto de texto (Arial: ancho medio ≈ 0,5 em con margen de seguridad; Courier 0,6 em)
const lines = (t, wIn, pt, em = 0.5) => clean(t).split("\n").reduce((a, p) => a + Math.max(1, Math.ceil(p.length / Math.max(1, (wIn * 72) / (pt * em)))), 0);
const textH = (t, wIn, pt, ls = 1.18, em = 0.5) => lines(t, wIn, pt, em) * pt * ls / 72;
const fitSize = (t, wIn, hIn, max, min = 10) => { let s = max; while (s > min && textH(t, wIn, s) > hIn) s -= 0.5; return s; };

// Markdown mínimo → runs (negrita y código)
function runs(md, o = {}) {
  const out = [];
  const size = o.fontSize || 10, color = o.color || CHAR;
  let bold = false;
  plain(md).split(/(`[^`]*`|\*\*)/).forEach(seg => {
    if (!seg) return;
    if (seg === "**") { bold = !bold; return; }
    if (seg.startsWith("`") && seg.endsWith("`") && seg.length > 1) {
      out.push({ text: seg.slice(1, -1), options: { fontFace: "Courier New", fontSize: size - 0.5, color: o.codeColor || NAVY, bold: bold || !!o.bold } });
    } else {
      out.push({ text: seg, options: { fontSize: size, color: bold ? (o.boldColor || color) : color, bold: bold || !!o.bold } });
    }
  });
  return out.length ? out : [{ text: "", options: { fontSize: size } }];
}
function card(s, x, y, w, h, title, body, o = {}) {
  const fill = o.fill || LT;
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, rectRadius: 0.1, line: { color: fill } });
  const th = o.titleH || 0.36;
  tb(s, runs(title, { fontSize: o.titleSize || 13, bold: true, color: o.titleColor || NAVY }), { x: x + 0.18, y: y + 0.12, w: w - 0.36, h: th });
  const bs = o.bodySize || fitSize(body, w - 0.36, h - th - 0.3, o.maxSize || 12, o.minSize || 10);
  s.addText(runs(body, { fontSize: bs, color: o.bodyColor || CHAR, codeColor: o.codeColor }), { x: x + 0.18, y: y + 0.18 + th, w: w - 0.36, h: h - th - 0.3, isTextBox: true, margin: 0, valign: "top" });
}
const bulletRuns = (items, size = 12, color = CHAR, gap = 6, o = {}) => {
  const out = [];
  items.forEach((t, i) => {
    const r = [{ text: (o.check ? "☐  " : "▪  "), options: { fontSize: size, color: BLUE, bold: true } }].concat(runs(t, { fontSize: size, color, codeColor: o.codeColor }));
    r.forEach(x => { x.options = Object.assign({}, x.options, { paraSpaceAfter: gap }); });
    r[r.length - 1].options.breakLine = i < items.length - 1;
    out.push(...r);
  });
  return out;
};
function bulletsBox(s, items, x, y, w, h, max = 13, color = CHAR, o = {}) {
  const all = items.map(clean).join("\n");
  const size = fitSize(all, w - 0.3, h - items.length * 0.09, max, o.min || 10);
  s.addText(bulletRuns(items, size, color, o.gap || 6, o), { x, y, w, h, isTextBox: true, margin: 0, valign: "top" });
}
function codeBox(s, code, x, y, w, h, max = 10.5, min = 9) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: "0F2238" }, rectRadius: 0.08, line: { color: "0F2238" } });
  const ls = code.split("\n");
  const wrapped = sz => ls.reduce((a, l) => a + Math.max(1, Math.ceil(l.length / ((w - 0.3) * 72 / (sz * 0.6)))), 0);
  const longest = Math.max(...ls.map(l => l.length));
  let size = max;
  while (size > Math.max(min, 9.5) && longest * size * 0.6 / 72 > w - 0.3) size -= 0.5;
  while (size > min && wrapped(size) * size * 1.22 / 72 > h - 0.18) size -= 0.5;
  s.addText(code, { x: x + 0.15, y: y + 0.08, w: w - 0.3, h: h - 0.16, fontFace: "Courier New", fontSize: size, color: "E8EEF5", margin: 0, valign: "top", isTextBox: true, lineSpacingMultiple: 1.0 });
}
function imagen(s, file, x, y, w, h, caption, align = "center") {
  const png = fs.readFileSync(file);
  const iw = png.readUInt32BE(16), ih = png.readUInt32BE(20);
  const ch = caption ? 0.32 : 0;
  let ww = w, hh = ww * ih / iw;
  if (hh > h - ch) { hh = h - ch; ww = hh * iw / ih; }
  const xx = align === "left" ? x : x + (w - ww) / 2;
  s.addImage({ path: file, x: xx, y, w: ww, h: hh });
  if (caption) tb(s, caption, { x, y: y + hh + 0.06, w, h: 0.26, fontSize: 9, color: GRAY, italic: true, align: align === "left" ? "left" : "center" });
  return { x: xx, w: ww, h: hh };
}

// ---------- Tablas paginadas ----------
const hdr = (t, o = {}) => ({ text: runs(t, { fontSize: o.size || 10, bold: true, color: WHITE, codeColor: "CFE3F3" }), options: { fill: { color: o.fill || NAVY }, valign: "middle", align: o.align || "left" } });
const TOP = 1.4, BUDGET = 5.3;
/** filas: arrays de celdas (md o {t, size, mono, st, fill}). colW suma 12.33. Devuelve nº de diapositivas. */
function tablaSlides(sec, titulo, cab, filas, colW, opt = {}) {
  const margin = opt.margin || 0.05, top = opt.top || TOP;
  const budget = opt.budget || ((opt.nota ? 5.05 : 5.35) - (top - TOP));
  const esGrupo = f => opt.grupo !== undefined && f.filter(c => c).length === 1 && String(f[opt.grupo]).startsWith("**");
  const emDe = t => { const code = (String(t || "").match(/`[^`]*`/g) || []).join("").length; return 0.46 + 0.16 * Math.min(1, code / Math.max(1, clean(t).length)); };
  const paginar = size => {
    const hdrH = Math.max(...cab.map((c, k) => textH(c, colW[k] - 2 * margin, opt.hdrSize || size, 1.18))) + 0.12;
    const cellH = (c, k) => { const o = typeof c === "object" ? c : { t: c }; return textH(o.t, colW[k] - 2 * margin - 0.04, o.size || size, 1.17, o.mono ? 0.62 : emDe(o.t)); };
    const altura = f => esGrupo(f) ? size * 1.17 / 72 + 2 * margin + 0.02 : Math.max(...f.map(cellH)) + 2 * margin + 0.02;
    const pages = []; let cur = [], used = hdrH;
    filas.forEach(f => { const h = altura(f); if (cur.length && (used + h > budget || (opt.maxRows && cur.length >= opt.maxRows))) { pages.push(cur); cur = []; used = hdrH; } cur.push(f); used += h; });
    if (cur.length) pages.push(cur);
    for (let k = 0; k < pages.length - 1; k++) {
      while (pages[k].length > 1 && esGrupo(pages[k][pages[k].length - 1])) pages[k + 1].unshift(pages[k].pop());
    }
    return pages;
  };
  // si la última página queda casi vacía, se prueba medio punto menos (nunca por debajo de 10 pt)
  let size = opt.size || 10, pages = paginar(size);
  while (pages.length > 1 && pages[pages.length - 1].length <= 2 && size > 10) {
    const p2 = paginar(size - 0.5);
    size -= 0.5; pages = p2;
  }
  // equilibrar: la última página no queda con una o dos filas sueltas
  while (pages.length > 1 && pages[pages.length - 1].length < 3 && pages[pages.length - 2].length > 5) {
    pages[pages.length - 1].unshift(pages[pages.length - 2].pop());
    while (pages[pages.length - 2].length > 1 && esGrupo(pages[pages.length - 2][pages[pages.length - 2].length - 1])) pages[pages.length - 1].unshift(pages[pages.length - 2].pop());
  }
  pages.forEach((pg, k) => {
    const s = slide(sec);
    s.addText(titulo + (pages.length > 1 ? ` (${k + 1}/${pages.length})` : ""), { placeholder: "title" });
    if (opt.intro && (k === 0 || opt.introRepeat)) tb(s, runs(opt.intro, { fontSize: opt.introSize || 11 }), { x: 0.5, y: 1.3, w: 12.33, h: top - 1.35 });
    const rows = [cab.map((c, i) => hdr(c, { size: opt.hdrSize || Math.min(size, 10.5), align: (opt.align || [])[i], fill: (opt.hdrFill || [])[i] }))];
    pg.forEach(f => {
      if (esGrupo(f)) { rows.push([{ text: runs(f[opt.grupo], { fontSize: size, bold: true, color: NAVY }), options: { colspan: cab.length, fill: { color: BLUETINT } } }]); return; }
      rows.push(f.map((c, i) => {
        const o = typeof c === "object" ? c : { t: c };
        const st = (opt.estilos || [])[i] || {};
        return { text: runs(o.t, Object.assign({ fontSize: o.size || size }, st, o.st || {})), options: { valign: "top", align: (opt.align || [])[i] || "left", fill: o.fill ? { color: o.fill } : undefined } };
      }));
    });
    const y = (opt.intro && k > 0 && !opt.introRepeat) ? TOP : top;
    s.addTable(rows, { x: 0.5, y, w: colW.reduce((a, b) => a + b, 0), colW, border: { type: "solid", color: LINE, pt: 0.5 }, autoPage: false, margin, fontFace: "Arial" });
    if (opt.nota && k === pages.length - 1) tb(s, runs(opt.nota, { fontSize: 9.5, color: GRAY }), { x: 0.5, y: H - 0.98, w: 12.33, h: 0.42 });
    if (opt.after) opt.after(s, k, pages.length);
  });
  return pages.length;
}
const T = (t) => t.filas;
// tabla fija (no paginada) en una caja
function tablaFija(s, cab, filas, x, y, colW, o = {}) {
  const size = o.size || 10;
  const rows = [cab.map(c => hdr(c, { size }))].concat(filas.map(f => f.map((c, i) => ({ text: runs(c, Object.assign({ fontSize: size }, (o.estilos || [])[i] || {})), options: { valign: "top" } }))));
  s.addTable(rows, { x, y, w: colW.reduce((a, b) => a + b, 0), colW, border: { type: "solid", color: LINE, pt: 0.5 }, margin: o.margin || 0.05, autoPage: false, fontFace: "Arial" });
}
// Markdown con bloques de código → [texto sin código, comandos]
function separaCodigo(md) {
  const cmds = [];
  const texto = String(md || "").replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, body) => {
    const ls = body.replace(/\\\n\s*/g, " ").split("\n");
    ls.forEach(l => {
      let t = l.trim();
      if (lang === "text") { if (!t.startsWith("$ ")) return; t = t.slice(2); }
      if (!t || t.startsWith("#") || t.startsWith("…")) return;
      cmds.push(t.replace(/\s{2,}#.*$/, ""));
    });
    return "";
  }).replace(/\n{2,}/g, "\n").trim();
  return [texto.replace(/\n(?!- )/g, " "), cmds];
}

// ====================== Portada e índice ======================
pres.addSection({ title: "Portada" });
{
  n++; const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Portada" });
  const tp = D.meta.titulo.split(": ");
  tb(s, D.meta.tag + " · " + D.meta.version, { x: 0.6, y: HAS_LOGO ? 2.0 : 1.2, w: 8, h: 0.4, fontSize: 14, color: WHITE });
  s.addText([{ text: tp[0] + ":\n", options: { fontSize: 30, color: WHITE } }, { text: tp[1], options: { fontSize: 34, bold: true, color: WHITE } }], { x: 0.6, y: HAS_LOGO ? 2.5 : 1.7, w: 11.8, h: 2.0, isTextBox: true, margin: 0, valign: "top" });
  tb(s, D.meta.subtitulo, { x: 0.6, y: HAS_LOGO ? 4.6 : 3.9, w: 11.2, h: 1.2, fontSize: 15, color: WHITE });
  tb(s, D.meta.autor + "   ·   " + D.meta.fecha + "   ·   Uso interno", { x: 0.6, y: HAS_LOGO ? 5.9 : 5.4, w: 11, h: 0.4, fontSize: 12, color: WHITE });
}
const indexSlide = slide("Portada");
indexSlide.addText("Contenido", { placeholder: "title" });
{
  const s = slide("Portada"); s.addText("Cómo leer este informe según su rol", { placeholder: "title" });
  D.audiencias.forEach((a, i) => {
    const x = 0.5 + (i % 2) * 6.27, y = 1.4 + Math.floor(i / 2) * 2.32;
    card(s, x, y, 6.06, 2.2, a.rol + " · secciones " + a.leer, a.valor, { fill: i === 0 ? ORTINT : BLUETINT, titleColor: i === 0 ? ORANGE : NAVY, maxSize: 12, titleSize: 12.5, titleH: 0.34 });
  });
  tb(s, runs("**Alcance y método.** " + D.meta.alcance, { fontSize: 9.5, color: GRAY }), { x: 0.5, y: 6.08, w: 12.33, h: 0.78 });
}

// ====================== 1 Resumen ejecutivo ======================
const S1 = "1 · Resumen ejecutivo"; pres.addSection({ title: S1 });
{
  mark("1 · Resumen ejecutivo");
  const s = slide(S1); s.addText("1 · pm-method v2.1.0 en cifras", { placeholder: "title" });
  D.kpis.forEach((k, i) => {
    const x = 0.5 + (i % 3) * 4.15, y = 1.4 + Math.floor(i / 3) * 1.66;
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 3.95, h: 1.54, fill: { color: NAVY }, rectRadius: 0.1, line: { color: NAVY } });
    tb(s, k.v, { x: x + 0.22, y: y + 0.1, w: 3.5, h: 0.55, fontSize: 28, bold: true, color: WHITE });
    tb(s, k.t, { x: x + 0.22, y: y + 0.66, w: 3.6, h: 0.3, fontSize: 13, bold: true, color: "9FD0F0" });
    tb(s, k.d, { x: x + 0.22, y: y + 0.97, w: 3.6, h: 0.52, fontSize: 10.5, color: WHITE });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 4.82, w: 12.33, h: 2.0, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, X.re_lema, { x: 0.72, y: 4.92, w: 11.9, h: 0.32, fontSize: 14, bold: true, color: ORANGE });
  tb(s, runs(X.re_frase_md.replace(/\n/g, " "), { fontSize: 14 }), { x: 0.72, y: 5.3, w: 11.9, h: 1.45 });
}
tablaSlides(S1, "1 · El problema que resuelve", ["Situación habitual", "Consecuencia"], T(X.re_problema), [6.4, 5.93], { size: 13,
  estilos: [{ bold: true, color: NAVY }, {}], nota: "Fuente: docs/RESUMEN-EJECUTIVO.md §2." });
tablaSlides(S1, "1 · Qué ofrece: doce capacidades", X.re_capacidades.cab, T(X.re_capacidades), [2.6, 5.6, 4.13], { size: 10.5,
  estilos: [{ bold: true, color: NAVY }, {}, { color: BLUE }] });
{
  const s = slide(S1); s.addText("1 · Valor diferencial", { placeholder: "title" });
  X.re_valor.forEach((v, i) => {
    const m = v.match(/^\*\*(.+?)\*\*\s*([\s\S]*)$/);
    const y = 1.4 + i * 1.09, dark = i === 0;
    const fill = dark ? NAVY : (i === 2 ? ORTINT : BLUETINT);
    s.addShape(pres.ShapeType.roundRect, { x: 0.5, y, w: 12.33, h: 1.0, fill: { color: fill }, rectRadius: 0.08, line: { color: fill } });
    tb(s, (i + 1) + ". " + m[1].replace(/\.$/, ""), { x: 0.7, y: y + 0.05, w: 3.5, h: 0.9, fontSize: 14, bold: true, color: dark ? WHITE : (i === 2 ? ORANGE : BLUE), valign: "middle" });
    tb(s, runs(m[2], { fontSize: fitSize(m[2], 8.2, 0.88, 13, 10.5), color: dark ? WHITE : CHAR, codeColor: dark ? "CFE3F3" : NAVY }), { x: 4.4, y: y + 0.05, w: 8.25, h: 0.9, valign: "middle" });
  });
}
{
  const s = slide(S1); s.addText("1 · Para quién y evidencia al 17/10/2026", { placeholder: "title" });
  tb(s, "Para quién", { x: 0.5, y: 1.36, w: 5.6, h: 0.32, fontSize: 13, bold: true, color: ORANGE });
  tablaFija(s, ["Perfil", "Qué obtiene"], T(X.re_para_quien), 0.5, 1.72, [1.95, 3.75], { size: 11.5, estilos: [{ bold: true, color: NAVY }, {}] });
  tb(s, "Evidencia", { x: 6.5, y: 1.36, w: 6.3, h: 0.32, fontSize: 13, bold: true, color: ORANGE });
  tablaFija(s, ["Verificación", "Resultado"], T(X.re_evidencia), 6.5, 1.72, [2.7, 3.63], { size: 10.5, estilos: [{ bold: true, color: NAVY }, {}] });
}
{
  const s = slide(S1); s.addText("1 · Límites conocidos, con honestidad, y cómo empezar", { placeholder: "title" });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.4, w: 7.0, h: 5.45, fill: { color: ORTINT }, rectRadius: 0.1, line: { color: ORTINT } });
  tb(s, "Límites conocidos", { x: 0.7, y: 1.5, w: 6.6, h: 0.35, fontSize: 13, bold: true, color: ORANGE });
  bulletsBox(s, X.re_limites, 0.7, 1.95, 6.6, 4.8, 12.5);
  tb(s, "Cómo empezar", { x: 7.8, y: 1.4, w: 5.0, h: 0.35, fontSize: 13, bold: true, color: NAVY });
  codeBox(s, "claude plugin marketplace add \\\n  Arturo-Penas-Rial/pm-method\nclaude plugin install pm-method@pm-method", 7.8, 1.8, 5.03, 1.25, 11);
  tb(s, runs("Luego, en una sesión: `/pm-method:pm-nuevo \"Mi proyecto\"` y \"¿qué sigue?\". Guía completa en la sección 11; prueba de aceptación en la sección 17.", { fontSize: 12 }), { x: 7.8, y: 3.2, w: 5.03, h: 1.2 });
  card(s, 7.8, 4.5, 5.03, 2.35, "Antes del primer proyecto real", "Recorrer la verificación de 12 pasos (sección 11) y la prueba de aceptación de 12 puntos en una carpeta de prueba (sección 17). Para que el orquestador conduzca toda la sesión: `claude --agent pm-method:pm-orquestador`.", { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, codeColor: "CFE3F3", maxSize: 12.5 });
}

// ====================== 2 Novedades 2.1 ======================
const S2 = "2 · Novedades de la versión 2.1"; pres.addSection({ title: S2 });
mark("2 · Novedades de la versión 2.1");
tablaSlides(S2, "2 · Versión 2.1.0: madurez para uso real", ["Indicador", "2.0.0", "2.1.0", "Fuente"], [
  ["Regresión automática (`probar_paquete.py`)", "35 pruebas", "**80 OK · 0 FALLO**", "CHANGELOG, PRUEBAS §2"],
  ["Decisiones del hook guardian en la regresión", "—", "**36/36** correctas", "salida de `probar_paquete.py`"],
  ["Hooks del plugin", "2", "**3** (+ UserPromptSubmit · `idioma.py`)", "CHANGELOG, INSTALACION §9"],
  ["Enrutamiento con Claude Code real", "82 % en 75 frases", "**60/60** en la corrida final (59/60 en la primera)", "PRUEBAS §3.1"],
  ["Guardarraíles en vivo", "escenario S5: PARTIAL (bypass por Bash)", "**4/4**", "resultados v2.0 y v2.1"],
  ["Idioma en vivo (pedido en inglés)", "escenario S6: FAIL/PARTIAL", "**3/3**", "resultados v2.0 y v2.1"],
  ["Hook `guardian.py`", "Write/Edit", "Write/Edit **y Bash**; comandos de decisión reservados a pm-director también en el hilo principal", "CHANGELOG"],
  ["Robustez en vivo", "—", "inyección **6/6** · desorden **7/7** · escala **5/5** · multisesion **10/10**", "PRUEBAS §3.1"],
  ["Variación de modelo (enrutamiento)", "—", "Sonnet **59/60** · Haiku **56/60**", "PRUEBAS §3.1"]],
  [3.6, 3.0, 3.5, 2.23], { size: 11.5, top: 2.35, estilos: [{ bold: true, color: NAVY }, { color: GRAY }, { color: BLUE }, { color: GRAY }],
  intro: "**2.1.0 · 17/10/2026 — " + X.chl_lema + ".** " + X.chl_intro, introSize: 13.5,
  nota: "Punto de partida 2.0.0 (14/10/2026): " + X.chl_v20_md });
{
  const G = X.chl_grupos;
  const s = slide(S2); s.addText("2 · Cambios: " + G[0].t.toLowerCase() + " · " + G[1].t.toLowerCase(), { placeholder: "title" });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.4, w: 7.3, h: 5.45, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, G[0].t, { x: 0.7, y: 1.5, w: 6.9, h: 0.33, fontSize: 13, bold: true, color: NAVY });
  bulletsBox(s, G[0].items, 0.7, 1.9, 6.95, 4.88, 11.5, CHAR, { gap: 4 });
  s.addShape(pres.ShapeType.roundRect, { x: 8.0, y: 1.4, w: 4.83, h: 5.45, fill: { color: ORTINT }, rectRadius: 0.1, line: { color: ORTINT } });
  tb(s, G[1].t, { x: 8.2, y: 1.5, w: 4.5, h: 0.33, fontSize: 13, bold: true, color: ORANGE });
  bulletsBox(s, G[1].items, 8.2, 1.9, 4.45, 4.88, 11.5, CHAR, { gap: 4 });
}
{
  const G = X.chl_grupos[2];
  const s = slide(S2); s.addText("2 · Cambios: " + G.t.toLowerCase(), { placeholder: "title" });
  const a = G.items.slice(0, 5), b = G.items.slice(5);
  bulletsBox(s, a, 0.5, 1.45, 6.05, 5.4, 11.5, CHAR, { gap: 5 });
  bulletsBox(s, b, 6.78, 1.45, 6.05, 5.4, 11.5, CHAR, { gap: 5 });
}
{
  const G = X.chl_grupos.find(g => /robustez/.test(g.t));
  const n = Math.ceil(G.items.length / 2);
  [G.items.slice(0, n), G.items.slice(n)].forEach((items, k) => {
    const s = slide(S2); s.addText(`2 · Ajustes tras las pruebas de robustez (${k + 1}/2)`, { placeholder: "title" });
    tb(s, "Misma versión 2.1.0, antes de publicarla", { x: 0.5, y: 1.33, w: 12.33, h: 0.3, fontSize: 12, color: GRAY, italic: true });
    const h = Math.ceil(items.length / 2);
    bulletsBox(s, items.slice(0, h), 0.5, 1.75, 6.05, 5.1, 12.5, CHAR, { gap: 8, min: 11 });
    bulletsBox(s, items.slice(h), 6.78, 1.75, 6.05, 5.1, 12.5, CHAR, { gap: 8, min: 11 });
  });
}
{
  const G = X.chl_grupos.find(g => /^Pruebas y doc/.test(g.t));
  const s = slide(S2); s.addText("2 · Cambios: " + G.t.toLowerCase(), { placeholder: "title" });
  bulletsBox(s, G.items, 0.5, 1.45, 7.4, 5.4, 13, CHAR, { gap: 8 });
  card(s, 8.2, 1.45, 4.63, 2.55, "Nuevos documentos", "`RESUMEN-EJECUTIVO`, `INDICE`, `DEPENDENCIAS`, `PRUEBAS`, `PILOTO`, `CASOS-DE-USO-INTEGRACIONES`, `CLAUDE.md`, `AGENTS.md`; README con diagramas Mermaid; `INSTALACION` con requisitos por sistema operativo y verificación de 12 pasos.", { fill: BLUETINT, maxSize: 12 });
  card(s, 8.2, 4.2, 4.63, 2.65, "Nuevas pruebas", "`probar_paquete.py`: 35 → 80 pruebas. `scripts/pruebas_vivo/` (`vivo.py`, `suite.py`, `escenarios.py`) para pruebas con Claude Code real, incluidas las de robustez, e informes en `docs/evaluacion/resultados/`.", { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, codeColor: "CFE3F3", maxSize: 12.5 });
}

// ====================== 3 Justificación ======================
const S3 = "3 · Justificación"; pres.addSection({ title: S3 });
{
  mark("3 · Justificación de la propuesta");
  const s = slide(S3); s.addText("3 · Qué aporta cada fuente: PRINCE2 manda", { placeholder: "title" });
  D.marco.forEach((m, i) => {
    const y = 1.42 + i * 1.08, dark = i === 0;
    s.addShape(pres.ShapeType.roundRect, { x: 0.5, y, w: 12.33, h: 0.98, fill: { color: dark ? NAVY : (i === 3 ? ORTINT : BLUETINT) }, rectRadius: 0.08, line: { color: dark ? NAVY : (i === 3 ? ORTINT : BLUETINT) } });
    tb(s, m.t, { x: 0.7, y: y + 0.05, w: 3.3, h: 0.88, fontSize: 13, bold: true, color: dark ? WHITE : (i === 3 ? ORANGE : BLUE), valign: "middle" });
    tb(s, runs(m.d, { fontSize: fitSize(m.d, 8.4, 0.85, 12, 10), color: dark ? WHITE : CHAR }), { x: 4.2, y: y + 0.05, w: 8.45, h: 0.88, valign: "middle" });
  });
}
tablaSlides(S3, "3 · El PMBOK aporta el cómo, encuadrado en PRINCE2", X.precedencia.cab, T(X.precedencia), [2.6, 3.0, 6.73], { size: 10.5, budget: 5.0,
  nota: "Toda regla tomada del PMBOK se etiqueta [PMBOK→práctica/proceso]. Ante conflicto, manda PRINCE2. El enfoque de entrega cambia cómo se trabaja dentro de las etapas, nunca elimina las puertas." });
tablaSlides(S3, "3 · Problemas de diseño que resuelve", ["Problema", "Respuesta del paquete"], D.problemas.map(p => [p.p, p.r]), [4.6, 7.73], { size: 11, estilos: [{ bold: true, color: NAVY }] });

// ====================== 4 Representación gráfica ======================
const S4 = "4 · Representación gráfica"; pres.addSection({ title: S4 });
const LECT = {
  "ciclo-prince2-bmad": "En cada fase, lo que produce BMAD (brief, PRD, arquitectura, épicas, veredicto del sprint planning, avance) entra como insumo de los productos PRINCE2 de pm-method, y cada transición pasa por una puerta de la junta. `autorizar-proyecto` exige el PRD final (P-07) y su línea base; `autorizar-etapa` exige PRD y arquitectura finales y lee el gate de preparación de BMAD (FAIL bloquea, CONCERNS es condición). Las decisiones vuelven a BMAD con `bmad.py handoff`.",
  arquitectura: "Cinco capas con dueño propio. Arriba, el gobierno PRINCE2 (orquestador, pm-director y subagentes de fase); debajo, las skills que aplican las técnicas del PMBOK. Las skills leen la especificación BMAD sin escribirla, usan las integraciones opcionales y escriben la carpeta del proyecto solo con `estado.py` y `registro.py`. Los hooks protegen la persistencia y la especificación.",
  "orquestacion-puerta": "El orquestador lee el estado (`estado.py resumen · siguiente`) y corre la sanidad: con un ERROR, la puerta se bloquea. Delega la producción en un subagente de fase, que devuelve el bloque de retorno con las decisiones humanas requeridas. El orquestador presenta la decisión; con la respuesta de la junta, solo pm-director la registra (`estado.py puerta …`).",
  "agentes-skills": "Reparto de las skills por agente: pm-director (DP), pm-inicio (SU/IP), pm-planificacion (IP/SB), pm-control (CS/MP) y pm-cierre (CP). Las transversales (puente BMAD, estado, sanidad, conocimiento, comunicación y exportación) las usa cualquier agente.",
  "ciclo-de-vida": "SU → IP con `autorizar-inicio`; IP → CS con `autorizar-proyecto` y `autorizar-etapa`; CS ↔ SB en cada límite de etapa (y por excepción, con `autorizar-plan-excepcion`); cierre planificado o prematuro hacia CP, que termina con `autorizar-cierre`.",
};
{
  mark("4 · Representación gráfica del ecosistema");
  const s = slide(S4); s.addText("4 · Arquitectura por capas", { placeholder: "title" });
  imagen(s, "diagramas/repo-arquitectura.png", 0.5, 1.35, 9.35, 5.55, "Fuente: docs/diagramas/arquitectura.mmd", "left");
  card(s, 10.05, 1.35, 2.78, 5.5, "Cómo leerlo", LECT.arquitectura, { fill: BLUETINT, maxSize: 12, minSize: 10 });
}
{
  const s = slide(S4); s.addText("4 · Orquestación de una puerta (secuencia)", { placeholder: "title" });
  imagen(s, "diagramas/repo-orquestacion-puerta.png", 0.5, 1.32, 12.33, 4.95, "Fuente: docs/diagramas/orquestacion-puerta.mmd");
  tb(s, runs(LECT["orquestacion-puerta"], { fontSize: 11.5 }), { x: 0.5, y: 6.28, w: 12.33, h: 0.66 });
}
{
  const s = slide(S4); s.addText("4 · Agentes y skills", { placeholder: "title" });
  imagen(s, "diagramas/repo-agentes-skills.png", 0.5, 1.35, 9.6, 5.55, "Fuente: docs/diagramas/agentes-skills.mmd", "left");
  card(s, 10.3, 1.35, 2.53, 5.5, "Cómo leerlo", LECT["agentes-skills"], { fill: BLUETINT, maxSize: 12, minSize: 10 });
}
{
  const s = slide(S4); s.addText("4 · Ciclo de vida PRINCE2 y puertas de la junta", { placeholder: "title" });
  const r = imagen(s, "diagramas/repo-ciclo-de-vida.png", 0.5, 1.35, 6.6, 5.55, "Fuente: docs/diagramas/ciclo-de-vida.mmd", "left");
  const x = 0.5 + r.w + 0.35, w = 12.83 - x;
  card(s, x, 1.35, w, 1.9, "Cómo leerlo", LECT["ciclo-de-vida"], { fill: BLUETINT, maxSize: 12 });
  tablaFija(s, ["Transición", "Puerta o comando"], [["SU → IP", "`autorizar-inicio`"], ["IP → CS", "`autorizar-proyecto` + `autorizar-etapa`"], ["CS → SB", "`limite-etapa` (o `--excepcion`)"],
    ["SB → CS", "`autorizar-etapa` (etapa n+1) o `autorizar-plan-excepcion`"], ["CS/SB → CP", "cierre [`--prematuro`]"], ["CP → fin", "`autorizar-cierre`"]], x, 3.45, [1.45, w - 1.45], { size: 11, estilos: [{ bold: true, color: NAVY }, {}] });
}
{
  const s = slide(S4); s.addText("4 · Ciclo de vida integrado: PRINCE2, BMAD y puertas", { placeholder: "title" });
  imagen(s, "diagramas/repo-ciclo-prince2-bmad-lr.png", 0.5, 1.3, 12.33, 4.85, "Fuente: docs/diagramas/ciclo-prince2-bmad.mmd (orientación horizontal para la diapositiva; mismo contenido)");
  tb(s, runs(LECT["ciclo-prince2-bmad"] + " Detalle de cada puerta: sección 8.", { fontSize: 11.5 }), { x: 0.5, y: 6.2, w: 12.33, h: 0.75 });
}
{
  const s = slide(S4); s.addText("4 · Sincronización con BMAD: fuente única", { placeholder: "title" });
  imagen(s, "diagramas/repo-sincronizacion-bmad.png", 0.5, 1.35, 12.33, 2.0, "Fuente: docs/diagramas/sincronizacion-bmad.mmd");
  tablaFija(s, ["Paso", "Qué ocurre", "Quién · comando"], [
    ["1 · Lectura", "El equipo de producto escribe BMAD; pm-method lee PRD, arquitectura, épicas y `sprint-status.yaml` por la fachada.", "`especificacion.py` · índice `pm-spec-index/1`"],
    ["2 · Línea base", "Tras la puerta, se fija la especificación con huella sha256 y copia congelada.", "pm-director · `bmad.py linea-base`"],
    ["3 · Verificar", "Antes de cada puerta se compara contra la línea base; un desvío sin cambio aprobado es ESP-10.", "`bmad.py verificar` · sanidad"],
    ["4 · Cambio", "El desvío se convierte en issue `solicitud-cambio` (C-###) y lo decide la autoridad de cambio o la junta.", "pm-issues-cambios · pm-director"],
    ["5 · Traspaso", "La decisión vuelve a BMAD como documento de traspaso; el equipo BMAD la aplica con sus flujos.", "`bmad.py handoff`"]],
    0.5, 3.75, [1.7, 7.0, 3.63], { size: 11, estilos: [{ bold: true, color: NAVY }, {}, {}] });
}

// ====================== 5 Arquitectura ======================
const S5 = "5 · Arquitectura"; pres.addSection({ title: S5 });
{
  mark("5 · Arquitectura");
  const s = slide(S5); s.addText("5 · Vista general: una sola voz, cinco capas", { placeholder: "title" });
  imagen(s, "diagramas/arq-general.png", 0.5, 1.35, 12.33, 5.55, "Fuente: docs/ARQUITECTURA.md §1 (diagrama Mermaid del paquete)");
}
tablaSlides(S5, "5 · Capas y dueños", X.capas.cab, T(X.capas), [1.7, 2.1, 3.4, 2.7, 2.43], { size: 10.5, estilos: [{ bold: true, color: NAVY }] });
{
  const s = slide(S5); s.addText("5 · Orquestador en el hilo principal + 5 subagentes de fase", { placeholder: "title" });
  tb(s, "Diseños evaluados", { x: 0.5, y: 1.35, w: 5, h: 0.3, fontSize: 12, bold: true, color: ORANGE });
  const op = [[hdr("Diseño"), hdr("Veredicto")]].concat(X.opciones_agentes.filas.map(f => [
    { text: runs(f[0], { fontSize: 10, bold: f[3].includes("adoptado") && !f[3].includes("descartado"), color: NAVY }), options: { valign: "top" } },
    { text: runs(f[3], { fontSize: 10, color: f[3].includes("adoptado") && !f[3].includes("descartado") ? BLUE : GRAY, bold: f[3].includes("adoptado") && !f[3].includes("descartado") }), options: { valign: "top" } }]));
  s.addTable(op, { x: 0.5, y: 1.7, w: 4.6, colW: [2.9, 1.7], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.05, autoPage: false });
  tb(s, "Reparto de responsabilidades", { x: 5.35, y: 1.35, w: 6, h: 0.3, fontSize: 12, bold: true, color: ORANGE });
  const rp = [[hdr("Subagente"), hdr("Procesos"), hdr("Prepara"), hdr("Registra")]].concat(X.reparto_subagentes.filas.map(f => f.map((c, i) => ({ text: runs(c, { fontSize: 10, bold: i === 0, color: i === 0 ? NAVY : CHAR }), options: { valign: "top" } }))));
  s.addTable(rp, { x: 5.35, y: 1.7, w: 7.48, colW: [1.45, 0.95, 2.9, 2.18], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.05, autoPage: false });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 5.75, w: 4.6, h: 1.05, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  tb(s, runs("**pm-orquestador** (sin `disallowedTools`): lee el estado, clasifica, hace todas las preguntas, delega y presenta las decisiones.", { fontSize: 10.5, color: WHITE, codeColor: "CFE3F3" }), { x: 0.68, y: 5.82, w: 4.25, h: 0.92, valign: "middle" });
}
{
  const s = slide(S5); s.addText("5 · Protocolo de retorno y reglas de los subagentes", { placeholder: "title" });
  tb(s, "Bloque obligatorio al final de cada subagente", { x: 0.5, y: 1.35, w: 6, h: 0.3, fontSize: 12, bold: true, color: ORANGE });
  codeBox(s, X.retorno, 0.5, 1.7, 6.3, 2.0, 10.5);
  tb(s, runs("El orquestador verifica **Hecho** contra `estado.py ver` (ninguna puerta registrada fuera de pm-director), pregunta los **Datos faltantes**, presenta las **Decisiones humanas** (pregunta · opciones con consecuencias · rol que decide) y vuelve a delegar; con la respuesta explícita, invoca a pm-director para registrar.", { fontSize: 12 }), { x: 0.5, y: 3.9, w: 6.3, h: 2.6 });
  const reglas = X.reglas_subagentes_md.split("\n").filter(l => /^\d+\./.test(l)).map(l => l.replace(/^\d+\.\s*/, ""));
  const cortas = reglas.map(r => r.split(/(?<=\.)\s/)[0]);
  s.addShape(pres.ShapeType.roundRect, { x: 7.1, y: 1.35, w: 5.73, h: 5.45, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, "Reglas de los subagentes", { x: 7.3, y: 1.48, w: 5.3, h: 0.35, fontSize: 13, bold: true, color: NAVY });
  bulletsBox(s, reglas.map((r, i) => r.length > 260 ? cortas[i] : r), 7.3, 1.95, 5.35, 4.75, 11.5);
}
{
  const s = slide(S5); s.addText("5 · Flujo de una petición con decisión humana", { placeholder: "title" });
  imagen(s, "diagramas/arq-flujo.png", 0.5, 1.35, 12.33, 5.55, "Fuente: docs/ARQUITECTURA.md §10 · solo pm-director registra, y solo después de la decisión explícita");
}
{
  const s = slide(S5); s.addText("5 · Herramientas y MCP heredados · equivalencias en Hermes", { placeholder: "title" });
  bulletsBox(s, D.arq_herramientas, 0.5, 1.45, 6.4, 5.4, 12);
  const rows = [[hdr("Claude Code"), hdr("Hermes Agent")]].concat(X.hermes_equivalencias.filas.map(f => [
    { text: runs(f[0], { fontSize: 10, bold: true, color: NAVY }), options: { valign: "top" } }, { text: runs(f[1], { fontSize: 10 }), options: { valign: "top" } }]));
  s.addTable(rows, { x: 7.2, y: 1.45, w: 5.63, colW: [1.75, 3.88], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.05, autoPage: false });
}
{
  const s = slide(S5); s.addText("5 · Carga progresiva del contexto y comandos", { placeholder: "title" });
  const cg = [X.carga.cab.map(c => hdr(c, { size: 10 }))].concat(X.carga.filas.map(f => f.map((c, i) => ({ text: runs(c, { fontSize: 10, bold: i === 0 }), options: { valign: "top" } }))));
  s.addTable(cg, { x: 0.5, y: 1.45, w: 6.4, colW: [0.55, 1.6, 1.85, 2.4], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.05, autoPage: false });
  bulletsBox(s, D.carga_cifras, 0.5, 4.05, 6.4, 2.85, 11);
  tb(s, "6 skills-comando (no consumen listado)", { x: 7.2, y: 1.42, w: 5.6, h: 0.3, fontSize: 12, bold: true, color: ORANGE });
  const cm = [[hdr("Comando"), hdr("Para qué")]].concat(X.comandos_arq.filas.map(f => [{ text: runs(f[0], { fontSize: 10 }), options: { valign: "top" } }, { text: runs(f[1], { fontSize: 10 }), options: { valign: "top" } }]));
  s.addTable(cm, { x: 7.2, y: 1.78, w: 5.63, colW: [2.3, 3.33], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.05, autoPage: false });
  tb(s, runs("Toda skill es comando: `/pm-method:<skill>` (plugin) o `/<skill>` (copia manual y Hermes). La carpeta `commands/` de v1 desapareció.", { fontSize: 10.5, color: GRAY }), { x: 7.2, y: 6.2, w: 5.63, h: 0.62 });
}

// ====================== 6 Columna vertebral ======================
const S6 = "6 · Columna vertebral BMAD ↔ PRINCE2"; pres.addSection({ title: S6 });
{
  mark("6 · Columna vertebral BMAD ↔ PRINCE2");
  const s = slide(S6); s.addText("6 · Fuente única: leer, fijar, detectar, traspasar", { placeholder: "title" });
  imagen(s, "diagramas/col-vertebral.png", 0.5, 1.32, 12.33, 5.6, "Síntesis de docs/sincronizacion.md §2–§8: cada dato tiene un solo dueño; no hay copias editables ni sincronización bidireccional");
}
{
  const s = slide(S6); s.addText("6 · Decisión de diseño y dueño de cada dato", { placeholder: "title" });
  const op = [[hdr("Opción evaluada"), hdr("Riesgo"), hdr("Veredicto")]].concat(X.sync_opciones.filas.map(f => [
    { text: runs(f[0], { fontSize: 10, bold: true, color: NAVY }), options: { valign: "top" } }, { text: runs(f[2], { fontSize: 10 }), options: { valign: "top" } },
    { text: runs(f[3], { fontSize: 10, bold: true, color: /adoptada/.test(f[3]) && !/descartada/.test(f[3]) ? BLUE : GRAY }), options: { valign: "top" } }]));
  s.addTable(op, { x: 0.5, y: 1.38, w: 12.33, colW: [4.0, 5.33, 3.0], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.04, autoPage: false });
  const du = [X.sync_duenos.cab.map(c => hdr(c))].concat(X.sync_duenos.filas.map(f => f.map((c, i) => ({ text: runs(c, { fontSize: 10, bold: i === 0, color: i === 0 ? NAVY : CHAR }), options: { valign: "top" } }))));
  s.addTable(du, { x: 0.5, y: 3.3, w: 12.33, colW: [4.0, 3.6, 4.73], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.04, autoPage: false });
  tb(s, "backlog.csv es la única tabla que combina datos de las dos capas, y cada columna tiene un dueño fijo.", { x: 0.5, y: 6.55, w: 12.33, h: 0.3, fontSize: 10, color: GRAY, italic: true });
}
{
  const s = slide(S6); s.addText("6 · Mapeo del ciclo de vida y ciclo de cambio", { placeholder: "title" });
  D.col_mapeo.forEach((m, i) => card(s, 0.5 + i * 3.1, 1.45, 2.95, 2.7, m.t, m.d, { fill: BLUETINT, titleColor: BLUE, maxSize: 12 }));
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 4.35, w: 12.33, h: 1.25, fill: { color: NAVY }, rectRadius: 0.1, line: { color: NAVY } });
  tb(s, runs("**Ciclo completo de fuente única.** " + D.col_ciclo, { fontSize: 12.5, color: WHITE, codeColor: "CFE3F3" }), { x: 0.75, y: 4.45, w: 11.85, h: 1.05, valign: "middle" });
  tb(s, runs("**Ids estables.** El vínculo entre capas es siempre un id (FR-3, 1-2-slug, REQ-004, B-1, SM-1, WBS 1.2.3, WP-…); los textos nunca se copian. La sanidad comprueba que todo id citado exista (ESP-04, REG-08, ESP-05). **Sin BMAD**, el contrato es el mismo: el proveedor es pm-method (`requisitos.md`, `backlog.csv`, `wbs.csv`) y las skills no cambian.", { fontSize: 11 }), { x: 0.5, y: 5.75, w: 12.33, h: 1.05 });
}
{
  const s = slide(S6); s.addText("6 · Líneas base y verificación", { placeholder: "title" });
  imagen(s, "diagramas/sync-estados-lr.png", 0.5, 1.35, 12.33, 3.6, "Ciclo de vida de una línea base de especificación · docs/sincronizacion.md §6");
  const vt = [[hdr("Hallazgo de verificar"), hdr("Significado")]].concat(X.verificar_tipos.filas.map(f => [{ text: runs(f[0], { fontSize: 10.5 }), options: {} }, { text: runs(f[1], { fontSize: 10.5 }), options: {} }]));
  s.addTable(vt, { x: 0.5, y: 5.15, w: 6.6, colW: [1.9, 4.7], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.05, autoPage: false });
  card(s, 7.35, 5.1, 5.48, 1.75, "Línea base (solo pm-director)", "`bmad.py linea-base prd|arquitectura|epicas --version X.Y`: copia congelada en `00-direccion/historial/`, sha256 e ids en `estado.json`, fila en `decisiones.csv`.", { fill: ORTINT, titleColor: ORANGE, maxSize: 11 });
}
tablaSlides(S6, "6 · Matriz lee / escribe", ["Skill", "Lee (fachada u otra vía)", "Escribe como dueña", "Comandos del puente"], T(X.lee_escribe), [2.55, 3.5, 4.38, 1.9], { size: 10,
  estilos: [{ bold: true, color: NAVY }], nota: "Fachada = especificacion.py. Ninguna skill abre archivos de BMAD ni requisitos.md para extraer datos. Skills que no tocan la especificación: HTML §6.8." });

// ====================== 7 Sanidad ======================
const S7 = "7 · Sanidad y guardarraíles"; pres.addSection({ title: S7 });
{
  mark("7 · Sanidad, guardarraíles y controles");
  const s = slide(S7); s.addText("7 · Controles permanentes: prevenir, detectar, decidir, mantener", { placeholder: "title" });
  imagen(s, "diagramas/sanidad.png", 0.5, 1.32, 12.33, 2.95);
  tablaFija(s, ["Control", "Cuándo actúa", "Cliente"], X.controles.filas.map(f => [f[0], f[1], f[3]]), 0.5, 4.38, [3.7, 6.8, 1.83], { size: 10, estilos: [{ bold: true, color: NAVY }, {}, {}], margin: 0.04 });
}
tablaSlides(S7, "7 · Familias y códigos de sanidad", ["Código", "Severidad", "Qué comprueba"], X.codigos.filas.map(f => f.length < 3 ? f : [f[0], f[1], f[2]]), [1.2, 2.6, 8.53], { size: 10, grupo: 0,
  estilos: [{ bold: true }, { color: ORANGE }, {}], nota: "Corrección y dueño de cada código: HTML §7.2 y docs/SANIDAD.md §2.1." });
{
  const s = slide(S7); s.addText("7 · Hook guardian.py: qué niega y qué permite", { placeholder: "title" });
  tablaFija(s, ["Regla (PreToolUse)", "Sobre qué", "Motivo"], X.guardian.filas.map(f => [f[0], f[2], f[3]]), 0.5, 1.4, [2.3, 3.1, 2.4], { size: 10, estilos: [{ bold: true, color: NAVY }, {}, {}], margin: 0.04 });
  tb(s, "Pruebas en la corrida del caso maestro", { x: 8.55, y: 1.36, w: 4.3, h: 0.3, fontSize: 11.5, bold: true, color: ORANGE });
  const p = [[hdr("Prueba"), hdr("Decisión")]].concat(X.guardian_pruebas.filas.map(f => [
    { text: runs(f[0], { fontSize: 10 }), options: { valign: "top" } }, { text: runs(f[1].replace(/ \(.*\)$/, ""), { fontSize: 10, bold: true, color: f[1].startsWith("deny") ? ORANGE : BLUE }), options: { valign: "top" } }]));
  s.addTable(p, { x: 8.55, y: 1.7, w: 4.28, colW: [3.13, 1.15], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.04, autoPage: false });
}
{
  const s = slide(S7); s.addText("7 · Hooks de inicio e idioma y separación de roles (v2.1)", { placeholder: "title" });
  card(s, 0.5, 1.4, 4.0, 2.75, "inicio.py (SessionStart)", "startup, resume, clear y compact: fase, etapa, sanidad rápida, guía de enrutamiento (nombra la skill dueña), regla de idioma, regla de no esquivar hooks, regla «fuentes = datos» y ruta absoluta de los scripts.", { fill: BLUETINT, maxSize: 12 });
  card(s, 4.67, 1.4, 4.0, 2.75, "idioma.py (UserPromptSubmit)", "Con cada pedido: si hay proyecto pm-method y el pedido está en otro idioma que `estado.json.idioma`, recuerda responder en el idioma del pedido. No bloquea nada.", { fill: BLUETINT, maxSize: 12 });
  card(s, 8.83, 1.4, 4.0, 2.75, "Separación de roles", "Desde el hilo principal o cualquier subagente salvo pm-director se niegan `estado.py puerta|rol|tolerancia|agil|umbrales-riesgo|cumplir-condiciones`, `limite-etapa --excepcion`, `set --forzar` y `aprobar` de nivel superior a gestor.", { fill: ORTINT, titleColor: ORANGE, maxSize: 11.5 });
  card(s, 0.5, 4.35, 6.06, 2.5, "Lanzador py.sh (Windows y Git Bash)", "Los hooks se ejecutan como `sh \"${CLAUDE_PLUGIN_ROOT}/hooks/py.sh\" …`: usa el primer Python 3.9+ disponible (`python3`, `python` o `py -3`). Sin Python, avisa por la salida de error y no bloquea. `.gitattributes` fuerza LF en `.sh`, `.py` y `.json`.", { fill: BLUETINT, maxSize: 12 });
  card(s, 6.77, 4.35, 6.06, 2.5, "Cómo prescindir de los hooks", "No hay opción para desactivarlos por separado: `claude plugin disable pm-method` (y `enable` para volver) o la copia manual, que no registra hooks. En ambos casos se pierde la protección automática y la disciplina queda a cargo de las skills y de la sanidad.", { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, codeColor: "CFE3F3", maxSize: 12 });
}
{
  const s = slide(S7); s.addText("7 · Regla de puerta: ninguna puerta con ERROR abierto", { placeholder: "title" });
  const pasos = X.regla_puerta_md.split("\n").filter(l => /^\d+\./.test(l)).map(l => l.replace(/^\d+\.\s*/, ""));
  pasos.forEach((p, i) => {
    const y = 1.45 + i * 1.12;
    s.addShape(pres.ShapeType.roundRect, { x: 0.5, y, w: 6.3, h: 1.0, fill: { color: BLUETINT }, rectRadius: 0.08, line: { color: BLUETINT } });
    s.addShape(pres.ShapeType.roundRect, { x: 0.65, y: y + 0.25, w: 0.5, h: 0.5, fill: { color: BLUE }, rectRadius: 0.08, line: { color: BLUE } });
    tb(s, String(i + 1), { x: 0.65, y: y + 0.25, w: 0.5, h: 0.5, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle" });
    tb(s, runs(p, { fontSize: fitSize(p, 5.3, 0.9, 11.5, 10) }), { x: 1.3, y: y + 0.06, w: 5.35, h: 0.9, valign: "middle" });
  });
  codeBox(s, "estado.py --proyecto <dir> puerta autorizar-etapa --decision condicionado \\\n  --por \"Ejecutivo: …\" --condiciones \"ESP-03: FR-x sin cobertura; …\"", 0.5, 4.95, 6.3, 0.85, 9.5);
  tb(s, runs("`condicionado` avanza como aprobado y deja EST-12 abierto hasta `cumplir-condiciones`. Los hallazgos INS no bloquean puertas, pero se informan.", { fontSize: 11 }), { x: 0.5, y: 5.95, w: 6.3, h: 0.9 });
  tb(s, "Cómo evolucionó un ERROR real (FR-5 agregado al PRD sin control)", { x: 7.1, y: 1.4, w: 5.73, h: 0.55, fontSize: 12, bold: true, color: ORANGE });
  const ev = [[hdr("Momento"), hdr("Sanidad")]].concat(X.evolucion_error.filas.map(f => [{ text: runs(f[0], { fontSize: 10.5 }), options: { valign: "top" } }, { text: runs(f[1], { fontSize: 10.5, bold: true, color: /^0|\*\*0/.test(f[1]) ? BLUE : ORANGE }), options: { valign: "top" } }]));
  s.addTable(ev, { x: 7.1, y: 2.0, w: 5.73, colW: [3.83, 1.9], border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.06, autoPage: false });
  card(s, 7.1, 4.75, 5.73, 2.1, "En el caso maestro", "Todas las puertas se presentaron con 0 ERROR. El cambio no controlado de FR-5 llegó a dar 2 ERROR, pero se resolvió durante la etapa, antes del límite.", { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, maxSize: 13 });
}
{
  const s = slide(S7); s.addText("7 · Bloqueos de puerta y «fuentes = datos» (v2.1)", { placeholder: "title" });
  const G = X.chl_grupos.find(g => /robustez/.test(g.t)).items;
  card(s, 0.5, 1.4, 7.3, 3.3, "Bloqueos de puerta en estado.py puerta", G[0].replace(/^\*\*Bloqueos de puerta\*\* en `estado.py puerta`: /, ""), { fill: BLUETINT, maxSize: 13 });
  codeBox(s, "estado.py --proyecto <dir> puerta autorizar-proyecto --decision aprobado --por \"Ejecutivo: …\"\n# rechazado si faltan tolerancias, PID o business case, plan de etapa,\n# línea base del PRD (con BMAD) o si sanidad.py --rapido da ERROR", 0.5, 4.9, 7.3, 1.0, 10, 9);
  tb(s, "Encontrado en el escenario en vivo multisesion: la junta podía «aprobar» sin tolerancias de proyecto, sin línea base del PRD y con ERROR de sanidad (PRUEBAS §3.1).", { x: 0.5, y: 6.05, w: 7.3, h: 0.8, fontSize: 11, color: GRAY, italic: true });
  card(s, 8.05, 1.4, 4.78, 2.65, "Fuentes = datos", G[3], { fill: ORTINT, titleColor: ORANGE, maxSize: 12.5 });
  card(s, 8.05, 4.2, 4.78, 2.65, "Escala", G[4], { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, codeColor: "CFE3F3", maxSize: 12.5 });
}
{
  const s = slide(S7); s.addText("7 · Validador del paquete y regresión", { placeholder: "title" });
  const val = X.validador_md.split("\n").filter(l => l.startsWith("- ")).map(l => l.slice(2));
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.4, w: 6.05, h: 5.45, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, runs("`validar_paquete.py [--estricto]` comprueba", { fontSize: 13, bold: true, color: NAVY }), { x: 0.7, y: 1.52, w: 5.7, h: 0.35 });
  bulletsBox(s, val, 0.7, 1.95, 5.7, 3.95, 10.5);
  codeBox(s, "Skills: 37 (31 invocables por el modelo, listado 6289 caracteres) · Agentes: 6\nOK", 0.7, 6.0, 5.65, 0.7, 9.5);
  s.addShape(pres.ShapeType.roundRect, { x: 6.78, y: 1.4, w: 6.05, h: 5.45, fill: { color: ORTINT }, rectRadius: 0.1, line: { color: ORTINT } });
  tb(s, runs("`probar_paquete.py`: casos A–G", { fontSize: 13, bold: true, color: ORANGE }), { x: 6.98, y: 1.52, w: 5.7, h: 0.35 });
  bulletsBox(s, X.pru_regresion.filas.map(f => "**" + f[0] + "**"), 6.98, 1.95, 5.7, 3.0, 12);
  tb(s, runs("Detalle de cada caso, pruebas en vivo con Claude Code real y prueba de aceptación: sección 17.", { fontSize: 11 }), { x: 6.98, y: 5.0, w: 5.7, h: 0.9 });
  codeBox(s, "Resultado: 80 OK · 0 FALLO · guardian: 36/36 decisiones correctas", 6.98, 6.0, 5.65, 0.7, 11);
}

// ====================== 8 Puertas de la junta ======================
const S8P = "8 · Puertas de la junta"; pres.addSection({ title: S8P });
{
  mark("8 · Puertas de la junta: verificación y registro");
  const s = slide(S8P); s.addText("8 · Ciclo de vida integrado PRINCE2 + BMAD + componentes", { placeholder: "title" });
  imagen(s, "diagramas/repo-ciclo-prince2-bmad-lr.png", 0.5, 1.3, 12.33, 5.65, "Fuente: docs/diagramas/ciclo-prince2-bmad.mmd y docs/PUERTAS.md §1 (orientación horizontal para la diapositiva; mismo contenido)");
}
tablaSlides(S8P, "8 · Componentes en el ciclo de vida y criterios de éxito", X.pue_componentes.cab, T(X.pue_componentes), [3.9, 3.6, 4.83], { size: 12,
  estilos: [{ bold: true, color: NAVY }, {}, {}],
  after: (s) => card(s, 0.5, 4.75, 12.33, 1.95, "Criterios de éxito en dos momentos", X.pue_criterios_exito, { fill: ORTINT, titleColor: ORANGE, maxSize: 13 }) });
{
  const s = slide(S8P); s.addText("8 · Cómo se verifica una puerta: tres capas", { placeholder: "title" });
  imagen(s, "diagramas/repo-verificacion-puertas.png", 0.5, 1.32, 12.33, 2.75, "Fuente: docs/diagramas/verificacion-puertas.mmd");
  const tit = ["1 · Salud del proyecto", "2 · Controles automáticos", "3 · Lista de control de la junta"];
  X.pue_capas.forEach((c, i) => card(s, 0.5 + i * 4.15, 4.2, 3.95, 2.65, tit[i], c.replace(/^\*\*[^*]+\*\*:?\s*/, ""), { fill: i === 2 ? ORTINT : BLUETINT, titleColor: i === 2 ? ORANGE : NAVY, maxSize: 12 }));
}
{
  const s = slide(S8P); s.addText("8 · Severidades y registro de la decisión", { placeholder: "title" });
  [["Bloqueo", "impide registrar `aprobado`"], ["Condición", "queda como observación de la puerta"], ["Aviso", "solo informa"]].forEach((k, i) =>
    card(s, 0.5 + i * 4.15, 1.4, 3.95, 1.25, k[0], k[1], { fill: i === 0 ? NAVY : (i === 1 ? ORTINT : BLUETINT), titleColor: i === 0 ? WHITE : (i === 1 ? ORANGE : NAVY), bodyColor: i === 0 ? WHITE : CHAR, codeColor: i === 0 ? "CFE3F3" : NAVY, maxSize: 14, titleSize: 15 }));
  tb(s, runs(X.pue_severidades.replace(/^Severidades: [^.]*\. /, ""), { fontSize: 13 }), { x: 0.5, y: 2.85, w: 12.33, h: 1.55 });
  tb(s, "Comandos (docs/PUERTAS.md §5)", { x: 0.5, y: 4.45, w: 12.33, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, X.pue_comandos.split("\n").map(l => l.replace(/\s{2,}#.*$/, "")).join("\n"), 0.5, 4.8, 12.33, 2.05, 10.5, 9);
}
tablaSlides(S8P, "8 · Controles automáticos por puerta", X.pue_controles.cab, T(X.pue_controles), [2.3, 1.6, 6.4, 2.03], { size: 11, top: 1.85, introRepeat: true,
  intro: "Ids: S- salud · I- autorizar-inicio · P- autorizar-proyecto · E- autorizar-etapa · X- autorizar-plan-excepcion · C- autorizar-cierre. Severidad: bloqueo, condición o aviso.", introSize: 11.5,
  estilos: [{ bold: true, color: NAVY }, { color: BLUE, bold: true }, {}, { color: ORANGE }] });
tablaSlides(S8P, "8 · Controles de BMAD que pm-method lee", X.pue_bmad.cab, T(X.pue_bmad), [2.6, 5.0, 4.73], { size: 10.5, top: 1.8, introRepeat: true,
  intro: "Verificado con BMAD 6.12.4 el 17/10/2026, con tres corridas reales de bmad-sprint-planning (dos CONCERNS y un FAIL provocado).", introSize: 11.5,
  estilos: [{ bold: true, color: NAVY }, {}, {}], nota: X.pue_bmad_nota });
tablaSlides(S8P, "8 · Las puertas como insumo de los informes", X.pue_informes.cab, T(X.pue_informes), [3.0, 5.2, 4.13], { size: 11, top: 1.8, introRepeat: true,
  intro: X.pue_informes_intro, introSize: 11.5, estilos: [{ bold: true, color: NAVY }, {}, {}] });

// ====================== 8 Componentes ======================
const S8 = "9 · Componentes del paquete"; pres.addSection({ title: S8 });
{
  mark("9 · Componentes del paquete");
  const s = slide(S8); s.addText("9 · Componentes del paquete", { placeholder: "title" });
  D.componentes.forEach((c, i) => {
    const col = i % 4, row = Math.floor(i / 4);
    card(s, 0.5 + col * 3.1, 1.42 + row * 2.75, 2.95, 2.6, "`" + c.t + "`", c.d, { fill: i === 6 ? ORTINT : BLUETINT, titleColor: i === 6 ? ORANGE : NAVY, maxSize: 11.5, titleSize: 11.5 });
  });
  card(s, 9.8, 4.17, 3.03, 2.6, "Principio rector", "El núcleo funciona sin nada externo: cada integración es un contrato con respaldo interno (Mermaid, CSV, scripts propios).", { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, maxSize: 12 });
}
{
  const filas = X.scripts_compartidos.filas.map(f => [f[0], f[1]]).concat(X.scripts_otros.filas.map(f => [f[0].replace(/^`<([^>]+)>\/scripts\/([^`]+)`$/, "`$2` ($1)"), f[1]]));
  tablaSlides(S8, "9 · Scripts deterministas (el motor de las skills)", ["Script", "Para qué"], filas, [3.4, 8.93], { size: 10.5,
    nota: "Mismo resultado para la misma entrada; validan valores y dejan traza. El modelo redacta; el script calcula y registra. Mantenedor: validar_paquete.py y probar_paquete.py (secciones 7 y 17)." });
}
{
  const s = slide(S8); s.addText("9 · Manifiesto de compatibilidad (compatibilidad.json)", { placeholder: "title" });
  const C = X.compatibilidad;
  card(s, 0.5, 1.4, 6.06, 2.75, "Versiones", `**Paquete:** ${C.paquete} ${C.version} · ${C.spec}\n**BMAD probado:** ${C.bmad.probado.join(" · ")}\n**Fuera de rango:** ${C.bmad.fuera_de_rango}\n**Python:** ${C.python}`, { fill: BLUETINT, maxSize: 11.5 });
  card(s, 6.77, 1.4, 6.06, 2.75, "Conducta por cliente", Object.entries(C.clientes).map(([k, v]) => `**${k}:** ${v}`).join("\n"), { fill: ORTINT, titleColor: ORANGE, maxSize: 11.5 });
  const SE = C.integraciones_externas_opcionales.skills_probadas_en_vivo || {};
  const sk = Object.entries(SE).filter(([k, v]) => typeof v === "object").map(([k, v]) => `**${k}:** commit ${v.commit}${v.version ? " · " + v.version : ""}`);
  card(s, 0.5, 4.35, 6.06, 2.5, `Skills externas probadas en vivo (${SE.fecha}, Claude Code ${SE.claude_code})`, sk.join("\n"), { fill: BLUETINT, maxSize: 11.5, titleSize: 11.5 });
  card(s, 6.77, 4.35, 6.06, 2.5, "MCP opcionales declarados", C.integraciones_externas_opcionales.mcp.join(" · "), { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, maxSize: 12 });
}
tablaSlides(S8, "9 · Plugins, skills y MCP opcionales: decisión de integración", ["Candidato", "Valoración informe 1", "Decisión v2", "Dónde"],
  X.decisiones_integracion.filas.map(f => [f[0], f[1], f[2], f[3]]), [3.0, 1.45, 5.48, 2.4], { size: 10,
  estilos: [{ bold: true, color: NAVY }, { color: "C9961A" }, {}, {}],
  nota: "Justificación de cada decisión y contratos de integración (insumo · salida · respaldo): HTML §9.4–§9.5 y docs/INTEGRACIONES.md." });

// ====================== 9 Dependencias ======================
const S9 = "10 · Dependencias"; pres.addSection({ title: S9 });
{
  mark("10 · Dependencias");
  const s = slide(S9); s.addText("10 · Dependencias: qué instalar según el uso", { placeholder: "title" });
  tablaFija(s, X.dep_resumen.cab, T(X.dep_resumen), 0.5, 1.4, [5.2, 7.13], { size: 12, estilos: [{ bold: true, color: NAVY }, {}] });
  card(s, 0.5, 4.75, 7.5, 2.1, "Node.js: versión mínima efectiva", X.dep_node_md.replace(/\n/g, " ").replace(/\s*-{3,}\s*$/, ""), { fill: ORTINT, titleColor: ORANGE, maxSize: 12 });
  card(s, 8.2, 4.75, 4.63, 2.1, "Marcas que se conservan", "**[verificar]** y **\"URL a confirmar por el usuario\"**: datos que no se pudieron comprobar desde el entorno de verificación. Revisar cada skill o servidor antes de instalarlo: corre con los permisos del agente.", { fill: NAVY, titleColor: WHITE, bodyColor: WHITE, maxSize: 12 });
}
{
  const filas = [];
  [["1.1 Cliente (al menos uno)", "dep_clientes"], ["1.2 Herramientas de base", "dep_base"], ["2 · Paquetes Python recomendados", "dep_python"], ["3 · Herramientas opcionales", "dep_opcionales"],
   ["4.1 El paquete y la capa de especificación", "dep_bmad"], ["4.2 Skills externas (diagramas y Office)", "dep_skills"], ["4.3 draw.io", "dep_drawio"]].forEach(([t, k]) => {
    filas.push(["**" + t + "**", "", "", "", "", ""]);
    X[k].filas.forEach(f => filas.push([{ t: f[0], st: { bold: true, color: NAVY } }, f[2], f[3], f[4], f[5], { t: f[6] }]));
  });
  tablaSlides(S9, "10 · Dependencias: nivel, versión probada, licencia, origen e instalación", ["Nombre", "Nivel", "Versión probada", "Licencia", "URL de origen", "Instalación"], filas,
    [1.55, 1.5, 1.95, 1.85, 2.55, 2.93], { size: 10, grupo: 0, margin: 0.05,
    nota: "Fuente: docs/DEPENDENCIAS.md §1–§4 (las marcas [verificar] y \"URL a confirmar por el usuario\" se conservan). Para qué usa pm-method cada dependencia: HTML §10.3." });
}
tablaSlides(S9, "10 · Conectores MCP opcionales", ["Conector", "Capacidad · skill dueña", "Versión probada", "Licencia", "URL de origen / servidor", "Configuración en Claude Code"],
  X.dep_mcp.filas.map(f => [{ t: f[0], st: { bold: true, color: NAVY } }, f[1] + " · " + f[2], f[3], f[4], f[5], f[6]]), [1.6, 1.95, 1.6, 1.85, 2.55, 2.78], { size: 10,
  nota: "pm-method no trae .mcp.json ni credenciales y no predefine conectores: pm-integraciones resuelve capacidades con los servidores conectados en la sesión (DEPENDENCIAS §5)." });
{
  const s = slide(S9); s.addText("10 · Dónde se declara cada dependencia y cómo se verificó", { placeholder: "title" });
  tablaFija(s, X.dep_declara.cab, T(X.dep_declara), 0.5, 1.4, [2.6, 3.85], { size: 10.5, estilos: [{ bold: true }, {}] });
  card(s, 0.5, 4.3, 6.45, 2.55, "Verificación del 17/10/2026", `${X.dep_ver_repos.filas.length} repositorios de GitHub comprobados con \`git ls-remote\` (HEAD abreviado) y, cuando se pudo, clonados para leer licencia y README; ${X.dep_ver_npm.filas.length} paquetes npm con \`npm view\` y ${X.dep_ver_pypi.filas.length} paquetes PyPI con \`pip index versions\` y \`METADATA\`. Tablas completas: HTML §10.6.`, { fill: BLUETINT, maxSize: 11.5 });
  s.addShape(pres.ShapeType.roundRect, { x: 7.2, y: 1.4, w: 5.63, h: 5.45, fill: { color: ORTINT }, rectRadius: 0.1, line: { color: ORTINT } });
  tb(s, "No verificadas", { x: 7.4, y: 1.5, w: 5.2, h: 0.33, fontSize: 13, bold: true, color: ORANGE });
  bulletsBox(s, X.dep_no_verificadas, 7.4, 1.95, 5.25, 4.8, 12);
}

// ====================== 10 Instalación ======================
const S10 = "11 · Instalación y configuración"; pres.addSection({ title: S10 });
mark("11 · Guía de instalación y configuración");
tablaSlides(S10, `11 · Instalación de punta a punta en ${T(X.inst_recorrido).length} pasos`, X.inst_recorrido.cab, T(X.inst_recorrido).map(f => [f[0], f[1], f[2].replace(/§/g, "INSTALACION §")]), [0.9, 8.4, 3.03], { size: 13,
  align: ["center"], estilos: [{ bold: true, color: BLUE }, {}, { color: GRAY }],
  nota: "Repositorio público: https://github.com/Arturo-Penas-Rial/pm-method (licencia MIT). La raíz es a la vez el plugin y su marketplace (pm-method). Comandos comprobados el 17/10/2026 con Claude Code 2.1.302." });
tablaSlides(S10, "11 · Cinco vías de instalación", ["Vía", "Cómo", "Hooks"], D.inst_vias.map(v => [v.t, v.d, v.hooks]), [2.6, 7.13, 2.6], { size: 11,
  estilos: [{ bold: true, color: NAVY }], nota: "Solo la instalación como plugin de Claude Code activa los hooks de protección y de sanidad. No combinar plugin y copia manual (sanidad INS-04)." });
tablaSlides(S10, "11 · Requisitos previos: lista de comprobación", X.inst_requisitos_so.cab, T(X.inst_requisitos_so), [2.6, 3.4, 3.43, 2.9], { size: 10.5,
  estilos: [{ bold: true, color: NAVY }], nota: "Origen, licencia y versión probada de cada requisito: sección 10." });
{
  const s = slide(S10); s.addText("11 · Requisitos por sistema operativo", { placeholder: "title" });
  const bul = md => md.split(/\n(?=- )/).map(b => b.replace(/^- /, "").replace(/\n\s*/g, " ").trim()).filter(Boolean);
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.4, w: 7.6, h: 5.45, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, "Windows (Git for Windows + PowerShell)", { x: 0.7, y: 1.48, w: 7.2, h: 0.32, fontSize: 13, bold: true, color: NAVY });
  bulletsBox(s, bul(X.req_windows_md), 0.7, 1.88, 7.25, 4.9, 11, CHAR, { gap: 3 });
  card(s, 8.3, 1.4, 4.53, 2.55, "macOS", bul(X.req_macos_md).join("\n"), { fill: ORTINT, titleColor: ORANGE, maxSize: 11 });
  card(s, 8.3, 4.1, 4.53, 2.75, "Linux", bul(X.req_linux_md).join("\n"), { fill: ORTINT, titleColor: ORANGE, maxSize: 11 });
}
{
  const s = slide(S10); s.addText("11 · Desde GitHub: instalar, actualizar y Hermes", { placeholder: "title" });
  const bloques = [
    ["Claude Code (cada integrante)", "claude plugin marketplace add Arturo-Penas-Rial/pm-method   # necesita git\nclaude plugin install pm-method@pm-method                   # alcance: user\nclaude plugin list    # pm-method@pm-method · Version: 2.1.0 · Status: enabled"],
    ["Actualizar", "claude plugin marketplace update pm-method   # refresca el catálogo\nclaude plugin update pm-method@pm-method     # requiere reiniciar Claude Code\nclaude plugin list                           # confirmar la versión"],
    ["Hermes Agent", "git clone https://github.com/Arturo-Penas-Rial/pm-method.git ~/pm-method\npython3 ~/pm-method/scripts/instalar_hermes.py   # adapta rutas a ${HERMES_SKILL_DIR}\n/reload-skills      # dentro de Hermes (no usar hermes skills tap/install)"]];
  bloques.forEach((b, i) => {
    const y = 1.36 + i * 1.84;
    tb(s, b[0], { x: 0.5, y, w: 8.0, h: 0.3, fontSize: 12.5, bold: true, color: i === 1 ? ORANGE : NAVY });
    codeBox(s, b[1], 0.5, y + 0.34, 8.0, 1.36, 10.5, 9);
  });
  card(s, 8.75, 1.36, 4.08, 2.95, "Credenciales de GitHub", "Nunca compartir en el chat la contraseña, tokens, códigos de recuperación ni de 2FA. Instalar desde el repositorio público no requiere credenciales; solo publicar (`gh auth login` inicia sesión en el navegador). Se recomienda 2FA.", { fill: ORTINT, titleColor: ORANGE, maxSize: 11.5 });
  card(s, 8.75, 4.45, 4.08, 2.4, "Alcances y equipos", "`--scope user|project|local` (por defecto `user`); con `project` queda en `.claude/settings.json` del repositorio. Plan Team/Enterprise: `extraKnownMarketplaces` + `enabledPlugins` [verificar].", { fill: BLUETINT, maxSize: 11.5 });
}
tablaSlides(S10, "11 · Credenciales: dónde va cada API-KEY", X.credenciales.cab, T(X.credenciales), [2.45, 2.0, 2.9, 4.98], { size: 9,
  estilos: [{ bold: true, color: NAVY }], nota: "pm-method no usa claves propias. Precedencia en Claude Code: nube > ANTHROPIC_AUTH_TOKEN > ANTHROPIC_API_KEY > apiKeyHelper > CLAUDE_CODE_OAUTH_TOKEN > perfiles > /login. Con suscripción y ANTHROPIC_API_KEY a la vez se usa la clave (cargo a la API): comprobar con /status. Nunca claves en el chat, en la carpeta del proyecto ni en commits (INSTALACION §0.7)." });
{
  const s = slide(S10); s.addText("11 · Configurar la clave de API (Linux/WSL y Hermes)", { placeholder: "title" });
  tb(s, "Claude Code con clave de la Claude Console", { x: 0.5, y: 1.36, w: 6.06, h: 0.3, fontSize: 12.5, bold: true, color: NAVY });
  codeBox(s, "echo 'export ANTHROPIC_API_KEY=\"<clave>\"' >> ~/.bashrc\nsource ~/.bashrc\nclaude        # la primera vez pide aprobar la clave\n/status       # confirma la credencial activa", 0.5, 1.7, 6.06, 1.5, 10.5, 9);
  tb(s, "Hermes Agent", { x: 6.77, y: 1.36, w: 6.06, h: 0.3, fontSize: 12.5, bold: true, color: NAVY });
  codeBox(s, "hermes model            # selector: pide la clave\nhermes config set ANTHROPIC_API_KEY \"<clave>\"\n# → ~/.hermes/.env (nunca config.yaml)\nchmod 600 ~/.hermes/.env", 6.77, 1.7, 6.06, 1.5, 10.5, 9);
  card(s, 0.5, 3.4, 4.0, 3.45, "Suscripción (recomendado)", "`claude` abre el navegador para iniciar sesión (o `/login`). Se guarda en `~/.claude/.credentials.json` (Linux/WSL, 0600), el Llavero (macOS) o `%USERPROFILE%\\.claude\\.credentials.json` (Windows). En WSL, si aparece un código, pegarlo en `Paste code here if prompted`.", { fill: BLUETINT, maxSize: 11 });
  card(s, 4.67, 3.4, 4.0, 3.45, "Conectores MCP", "`claude mcp add <n> -e TOKEN=… -- <cmd>` (queda en `~/.claude.json`). Remotos: `--transport http` y `/mcp` para autenticar. En `.mcp.json` versionado solo `${TOKEN}`. Hermes: bloque `env:` de `mcp_servers` en `~/.hermes/config.yaml`.", { fill: ORTINT, titleColor: ORANGE, maxSize: 11 });
  card(s, 8.83, 3.4, 4.0, 3.45, "CI y nube", "Sin navegador: `claude setup-token` imprime un token de un año → `CLAUDE_CODE_OAUTH_TOKEN`. Bedrock/Vertex/Foundry: `CLAUDE_CODE_USE_BEDROCK|VERTEX|FOUNDRY` + credenciales del proveedor. Claves rotativas: `apiKeyHelper` en `~/.claude/settings.json`.", { fill: BLUETINT, maxSize: 11 });
}
{
  const s = slide(S10); s.addText("11 · Orca (opcional): varios agentes y proyectos en paralelo", { placeholder: "title" });
  tb(s, runs("**Orca** (github.com/stablyai/orca, MIT) es una aplicación de escritorio que corre Claude Code, Hermes y otros agentes en paralelo, cada uno en su worktree, con terminales persistentes, tableros de GitHub/Linear, notificaciones y app móvil. Con pm-method: la sesión de gestión (`pm-orquestador`) junto a las del equipo de producto, varios proyectos a la vez y aviso cuando un agente espera una decisión. **No es una TUI**: es gráfica y contiene terminales; pm-method se usa desde Claude Code o Hermes dentro de ellas.", { fontSize: 11.5 }), { x: 0.5, y: 1.36, w: 12.33, h: 1.45 });
  tablaFija(s, X.orca_inst.cab, T(X.orca_inst), 0.5, 2.95, [2.3, 10.03], { size: 10, estilos: [{ bold: true, color: NAVY }, {}] });
  tb(s, runs("**WSL:** sin guía oficial [verificar]; opción: versión de Windows con terminales que ejecuten `wsl` y `claude`. **CLI y skill:** activar en Settings → General → Orca CLI; `orca status --json`; `npx skills add https://github.com/stablyai/orca --skill orca-cli`. Usa el inicio de sesión de cada agente (configurar antes la credencial). Telemetría anónima desactivable.", { fontSize: 10.5 }), { x: 0.5, y: 5.75, w: 12.33, h: 1.1 });
}
{
  const s = slide(S10); s.addText("11 · Carpeta local, copia manual, Cowork y Hermes", { placeholder: "title" });
  const bloques = [
    ["Plugin desde carpeta local", "claude plugin marketplace add /ruta/a/pm-method\nclaude plugin install pm-method@pm-method\nclaude --plugin-dir /ruta/a/pm-method   # probar sin instalar"],
    ["Copia manual (sin hooks)", "mkdir -p ~/.claude/skills ~/.claude/agents\ncp -r /ruta/a/pm-method/skills/* ~/.claude/skills/\ncp /ruta/a/pm-method/agents/*.md ~/.claude/agents/"],
    ["Hermes (copia o directorio externo)", "cp -r /ruta/a/pm-method/skills/* ~/.hermes/skills/\n# o en ~/.hermes/config.yaml:\nskills:\n  external_dirs: [\"/ruta/a/pm-method/skills\"]"],
    ["Primer uso", D.inst_inicio]];
  bloques.forEach((b, i) => {
    const x = 0.5 + (i % 2) * 6.27, y = 1.36 + Math.floor(i / 2) * 2.2;
    tb(s, b[0], { x, y, w: 6.06, h: 0.3, fontSize: 12, bold: true, color: NAVY });
    codeBox(s, b[1], x, y + 0.32, 6.06, 1.7, 10, 9);
  });
  tb(s, runs("**Cowork:** instalar `pm-method` desde la gestión de plugins de la aplicación, apuntando al mismo paquete [verificar el recorrido de pantallas]. **Hermes:** cada skill es un comando `/nombre-skill`; los agentes se usan como personas (`hermes profile create pm` + `SOUL.md`, o `agent.personalities` y `/personality`); sin hooks, la sanidad la ejecutan pm-orquestador y pm-puerta.", { fontSize: 10.5 }), { x: 0.5, y: 5.85, w: 12.33, h: 1.0 });
}
{
  const s = slide(S10); s.addText("11 · Paquetes Python y detección de BMAD", { placeholder: "title" });
  tb(s, "Paquetes Python recomendados", { x: 0.5, y: 1.36, w: 6, h: 0.3, fontSize: 12.5, bold: true, color: NAVY });
  codeBox(s, "python3 -m pip install pyyaml python-docx openpyxl\n# con Python gestionado por el sistema operativo:\npython3 -m venv ~/.venvs/pm-method\n~/.venvs/pm-method/bin/python -m pip install \\\n    pyyaml python-docx openpyxl", 0.5, 1.7, 6.06, 1.65, 10.5, 9);
  tablaFija(s, X.python_paquetes.cab, T(X.python_paquetes), 0.5, 3.5, [1.6, 4.46], { size: 10.5, estilos: [{ bold: true }, {}] });
  tb(s, runs("Windows: `python -m pip …` o `py -3 -m pip …`. La sanidad informa cada módulo faltante como **INS-01** con el comando de instalación.", { fontSize: 11 }), { x: 0.5, y: 5.5, w: 6.06, h: 1.3 });
  tb(s, "Detectar BMAD desde pm-method", { x: 6.77, y: 1.36, w: 6, h: 0.3, fontSize: 12.5, bold: true, color: NAVY });
  codeBox(s, "python3 <pm-bmad-puente>/scripts/bmad.py --proyecto ./gestion detectar\n# BMAD en otra carpeta: --raiz antes del subcomando\nbmad.py --proyecto ./gestion --raiz .. detectar\n# declararlo a mano:\nestado.py --proyecto ./gestion integracion especificacion=bmad", 6.77, 1.7, 6.06, 1.65, 10.5, 9);
  card(s, 6.77, 3.5, 6.06, 3.35, "Qué registra detectar", "`especificacion=bmad` y el bloque `bmad` en `estado.json.integraciones`: layout (`v6` | `v4`), rutas relativas a `--proyecto`, versión y su fuente (`_bmad/_config/manifest.yaml`) y soporte (`soportada`, `v4`, `version-no-visible`, `no-probada`). En la prueba del 17/10/2026: `version 6.12.4`, `soporte: soportada`. La carpeta de gestión debe quedar fuera de `_bmad/`, `_bmad-output/` y `.bmad-core/`.", { fill: BLUETINT, maxSize: 11.5 });
}
{
  const s = slide(S10); s.addText("11 · BMAD en el repositorio del producto (opcional)", { placeholder: "title" });
  tb(s, runs("pm-method **no instala ni actualiza BMAD**: lo instala el equipo del producto en la raíz de su repositorio (Node.js ≥ 20.12.0).", { fontSize: 12 }), { x: 0.5, y: 1.36, w: 12.33, h: 0.4 });
  codeBox(s, "cd /ruta/al/repositorio\nnpx bmad-method@6.12.4 install --modules bmm --tools claude-code --yes \\\n    --user-name \"<nombre>\" --set core.project_name=<proyecto> --no-shims", 0.5, 1.85, 12.33, 1.0, 11);
  tablaFija(s, X.bmad_opciones.cab, T(X.bmad_opciones), 0.5, 3.0, [3.7, 3.8], { size: 10.5, estilos: [{ bold: false }, {}] });
  card(s, 8.25, 3.0, 4.58, 3.85, "Compatibilidad", "Probado con BMAD 4.x, 6.11 y 6.12; relevado `bmad-method@6.12.4`. Fuera de rango, el puente trabaja en modo degradado con aviso (ESP-07): correr `probar_paquete.py` antes de la siguiente puerta. `--action update` / `quick-update` [verificar el comportamiento antes de usarlo en un repositorio real]. La vista previa de BMAD v7 no está probada.", { fill: ORTINT, titleColor: ORANGE, maxSize: 11.5 });
}
tablaSlides(S10, "11 · Skills externas de diagramas y Office: instalación", ["Integración", "Repositorio · licencia · distribución", "Instalar como plugin (Claude Code)", "Instalar como skill copiada", "Requisitos"],
  X.skills_externas.filas.map(f => [{ t: f[0], st: { bold: true, color: NAVY } }, f[1], f[2], f[3], f[5]]), [1.75, 2.2, 3.2, 2.9, 2.28], { size: 10,
  nota: "Comandos verificados el 17/10/2026 con Claude Code 2.1.302; `npx skills` 1.7.0 exige Node.js ≥ 22.20.0. Revisar cada skill antes de instalarla: corre con los permisos del agente." });
{
  const s = slide(S10); s.addText("11 · Declarar las skills externas y comprobarlas", { placeholder: "title" });
  codeBox(s, "E=<pm-estado-proyecto>/scripts\npython3 $E/estado.py --proyecto ./gestion integracion diagramas=archify   # o diagram-design, visual-explainer\npython3 $E/estado.py --proyecto ./gestion integracion diagramas=archify,visual-explainer   # lista por prioridad\npython3 $E/estado.py --proyecto ./gestion integracion export=skills-office\npython3 $E/sanidad.py --proyecto ./gestion | grep INS-03", 0.5, 1.4, 12.33, 1.75, 10.5, 9);
  card(s, 0.5, 3.35, 6.06, 1.6, "Resultado esperado", "Una línea `INFO INS-03 Skill externa '<skill>' (<valor>) instalada: invocar como '<nombre>' · <origen> · <ruta>` por skill.", { fill: BLUETINT, maxSize: 12 });
  card(s, 6.77, 3.35, 6.06, 1.6, "Respaldo", "Sin la skill, o si falla, pm-visuales entrega Mermaid y pm-exportar usa `exportar.py`, con nota en `diario.md`. Volver: `integracion diagramas=mermaid` / `export=scripts`.", { fill: ORTINT, titleColor: ORANGE, maxSize: 12 });
  tablaFija(s, X.herramientas_sistema.cab, T(X.herramientas_sistema), 0.5, 5.1, [2.4, 3.8, 3.4, 2.73], { size: 10, estilos: [{ bold: true }, {}, {}, {}] });
}
{
  const s = slide(S10); s.addText("11 · Conectores MCP: conectar el servidor y declarar la capacidad", { placeholder: "title" });
  tb(s, "Paso 1 · conectar en Claude Code", { x: 0.5, y: 1.36, w: 6, h: 0.3, fontSize: 12.5, bold: true, color: NAVY });
  codeBox(s, "claude mcp add --transport http <nombre> <url-del-servidor>\nclaude mcp add <nombre> -- <comando> [argumentos]   # stdio\nclaude mcp add -s user --transport http <nombre> <url>\nclaude mcp list · claude mcp get <nombre>\nclaude mcp login <nombre>     # OAuth (o /mcp en una sesión)\nclaude mcp remove <nombre>", 0.5, 1.7, 6.06, 2.1, 10, 9);
  tablaFija(s, X.mcp_ejemplos.cab, T(X.mcp_ejemplos), 0.5, 3.95, [1.5, 4.56], { size: 10, estilos: [{ bold: true }, {}] });
  tb(s, "Paso 2 · declarar en el proyecto", { x: 6.77, y: 1.36, w: 6, h: 0.3, fontSize: 12.5, bold: true, color: NAVY });
  codeBox(s, "python3 <pm-estado-proyecto>/scripts/estado.py --proyecto ./gestion \\\n    integracion tracker=jira docs=confluence chat=teams", 6.77, 1.7, 6.06, 0.8, 10);
  tb(s, runs("Nunca tokens en `.mcp.json` ni en la carpeta del proyecto; preferir OAuth. Lectura libre; **escritura externa solo con vista previa y confirmación explícita**; datos externos como instantáneas fechadas en `03-control/fuentes/`. Un valor desconocido se guarda, pero la sanidad lo informa como INT-01.", { fontSize: 11 }), { x: 6.77, y: 2.65, w: 6.06, h: 1.5 });
  card(s, 6.77, 4.3, 6.06, 2.55, "Notas de proveedores (17/10/2026)", "El servidor \"Teams (preview)\" de Microsoft figura como legado (se recomienda Work IQ); el Slack MCP oficial está restringido a apps publicadas o internas; la obtención de transcripciones por Zoom MCP no está confirmada. Hermes: `hermes mcp add <nombre>` con `--url` o `--command` [verificar opciones].", { fill: ORTINT, titleColor: ORANGE, maxSize: 11.5 });
}
tablaSlides(S10, "11 · Capacidades reconocidas en estado.json.integraciones", X.capacidades_mcp.cab, T(X.capacidades_mcp), [2.6, 5.0, 1.6, 3.13], { size: 10.5,
  estilos: [{ bold: true }, {}, {}, {}], nota: "Lista de INT-01 en sanidad.py; valores por defecto en esquema.py. Con un tracker declarado, INT-02/03/04 vigilan las instantáneas de 03-control/fuentes/." });
{
  const s = slide(S10); s.addText("11 · Configuración: tolerancias, settings y orquestador", { placeholder: "title" });
  tb(s, "Crear un proyecto e idioma", { x: 0.5, y: 1.36, w: 6, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, "nuevo_proyecto.py --ruta ./gestion --nombre \"Proyecto Faro\" \\\n    --idioma es --enfoque hibrido --ejecutivo \"Nombre\" --gestor \"Nombre\"\nestado.py --proyecto ./gestion set idioma=en", 0.5, 1.7, 6.06, 1.05, 10, 9);
  tb(s, "Tolerancias y umbrales (decisiones de gobierno)", { x: 0.5, y: 2.95, w: 6, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, "estado.py --proyecto ./gestion umbrales-riesgo alto=15 medio=6\nestado.py --proyecto ./gestion tolerancia --nivel proyecto \\\n    tiempo=\"±2 semanas\" costo=\"±10 %\"\nestado.py --proyecto ./gestion tolerancia --nivel etapa costo=\"±5 %\"", 0.5, 3.29, 6.06, 1.3, 10, 9);
  tb(s, runs("Tiempo y costo son el mínimo obligatorio (EST-06/07). Proyecto: capa de negocio/ejecutivo; etapa: la junta en cada `autorizar-etapa`. En operación normal las registra pm-director tras la decisión humana.", { fontSize: 11 }), { x: 0.5, y: 4.75, w: 6.06, h: 1.1 });
  tb(s, "settings.json con BMAD u otros repos de skills", { x: 6.77, y: 1.36, w: 6.06, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, "{\n  \"skillListingBudgetFraction\": 0.02\n}", 6.77, 1.7, 6.06, 0.85, 10.5);
  tb(s, runs("El listado de skills usa ≈1 % del contexto; las 31 skills invocables suman 6.289 caracteres (con BMAD 6.12.4, ≈23.000 en total). INS-05 avisa por encima de ≈8.000. `skillOverrides` no aplica a skills de plugins.", { fontSize: 11 }), { x: 6.77, y: 2.7, w: 6.06, h: 1.2 });
  tb(s, "Orquestador en el hilo principal", { x: 6.77, y: 4.0, w: 6.06, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, "/pm-method:pm-orquestador               # como skill\nclaude --agent pm-method:pm-orquestador   # toda la sesión", 6.77, 4.34, 6.06, 0.8, 10);
  tb(s, runs("Rutas de scripts: en skills `${CLAUDE_SKILL_DIR}/../pm-estado-proyecto/scripts/`; en agentes `${CLAUDE_PLUGIN_ROOT}/skills/pm-estado-proyecto/scripts/`; el hook de inicio imprime la ruta absoluta.", { fontSize: 11 }), { x: 6.77, y: 5.3, w: 6.06, h: 1.5 });
}
tablaSlides(S10, "11 · Verificación de la instalación en 12 pasos", X.verificacion.cab, T(X.verificacion), [0.45, 2.3, 4.6, 4.98], { size: 10,
  align: ["center"], estilos: [{ bold: true, color: BLUE }, { bold: true, color: NAVY }, {}, {}],
  nota: "Paso 5: resultado vigente 80 OK · 0 FALLO (PRUEBAS.md §2)." });
tablaSlides(S10, "11 · Hallazgos de instalación esperables (familia INS)", X.ins_esperados.cab, T(X.ins_esperados), [1.2, 4.6, 6.53], { size: 11,
  estilos: [{ bold: true, color: NAVY }], nota: "Con --rapido, el modo del hook de inicio, solo se evalúan INS-01 e INS-02. Solución de problemas (27 síntomas con causa y solución): HTML §11.13." });
{
  const s = slide(S10); s.addText("11 · Actualización, migración y desinstalación", { placeholder: "title" });
  tb(s, "Actualizar el plugin (GitHub o carpeta local)", { x: 0.5, y: 1.36, w: 6, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, "claude plugin marketplace update pm-method\nclaude plugin update pm-method@pm-method   # reiniciar Claude Code", 0.5, 1.7, 6.06, 0.8, 10.5);
  bulletsBox(s, ["Copia manual o Hermes: volver a copiar `skills/` y `agents/` (con `external_dirs` basta actualizar la carpeta) y `/reload-skills` en Hermes.",
    "**Proyectos existentes:** `estado.json` y los registros migran solos al leerse; la sanidad avisa la diferencia de versión como **INS-02**.",
    "Después de actualizar pm-method o BMAD: sanidad completa en cada proyecto activo y, si BMAD cambió de versión, `probar_paquete.py`."], 0.5, 2.7, 6.06, 4.1, 12);
  tb(s, "Desinstalar", { x: 6.77, y: 1.36, w: 6, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, "claude plugin uninstall pm-method@pm-method\nclaude plugin marketplace remove pm-method", 6.77, 1.7, 6.06, 0.8, 10.5);
  bulletsBox(s, ["Copia manual: borrar las carpetas `pm-*` de `~/.claude/skills/` y los seis `pm-*.md` de `~/.claude/agents/`.",
    "Skills externas: `npx skills remove <skill>` o `claude plugin uninstall <plugin>@<marketplace>`; MCP: `claude mcp remove <nombre>`.",
    "Las carpetas de proyecto no se tocan: son Markdown, CSV y JSON legibles sin el paquete."], 6.77, 2.7, 6.06, 4.1, 12);
}

// ====================== 11 Catálogo ======================
const S11 = "12 · Catálogo"; pres.addSection({ title: S11 });
mark("12 · Catálogo de agentes y skills");
tablaSlides(S11, "12 · Seis agentes", ["Agente", "Tipo", "Rol", "Procesos", "Puertas que prepara"], X.agentes.filas, [1.75, 2.0, 4.6, 1.6, 2.38], { size: 10, estilos: [{ bold: true }] });
tablaSlides(S11, "12 · Seis comandos de uso humano", ["Comando", "Argumentos", "Qué hace", "Agente y skills", "¿Escribe?"], X.comandos.filas, [1.25, 2.4, 5.0, 2.4, 1.28], { size: 10, estilos: [{ bold: true }] });
{
  const filas = [];
  X.catalogo.forEach(g => {
    filas.push(["", `**${g.titulo}**`, "", "", ""]);
    g.skills.forEach(sk => filas.push(["`" + sk.nombre + "`", sk.tema, sk.procesos || "", sk.usar || "", sk.no || ""]));
  });
  tablaSlides(S11, "12 · 31 skills invocables por agente y fase", ["Skill", "Dueña de", "Procesos", "Usar (disparadores)", "No (pista de alcance)"], filas, [2.45, 3.1, 1.35, 3.0, 2.43], { size: 10, grupo: 1, budget: 5.4,
    nota: "Fichas completas (produce, PRINCE2, PMBOK como cómo, plantillas, scripts, lectura de la fachada): HTML §12 y docs/CATALOGO.md." });
}

// ====================== 12 RACI ======================
const S12 = "13 · Matriz RACI"; pres.addSection({ title: S12 });
{
  mark("13 · Matriz RACI");
  const s = slide(S12); s.addText("13 · Reglas de la matriz RACI", { placeholder: "title" });
  const reglas = X.raci_reglas_md.split("\n").filter(l => /^\d+\./.test(l)).map(l => l.replace(/^\d+\.\s*/, ""));
  reglas.forEach((r, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const tit = (r.match(/^\*\*(.+?)\*\*/) || ["", ""])[1];
    const cuerpo = r.replace(/^\*\*.+?\*\*\s*/, "");
    card(s, 0.5 + col * 6.27, 1.42 + row * 1.37, 6.06, 1.27, tit, cuerpo, { fill: i === 0 ? NAVY : BLUETINT, titleColor: i === 0 ? WHITE : NAVY, bodyColor: i === 0 ? WHITE : CHAR, codeColor: i === 0 ? "CFE3F3" : NAVY, maxSize: 10.5, titleSize: 11.5, titleH: 0.3 });
  });
  tb(s, runs("Columnas humanas: CN capa de negocio · EJ ejecutivo · US usuario sénior · PS proveedor sénior · GP gestor · JE/PO jefe de equipo o product owner · AS aseguramiento · SP soporte · BM equipo BMAD. Agentes: orq · dir · ini · pla · con · cie.", { fontSize: 10.5, color: GRAY }), { x: 6.77, y: 5.55, w: 6.06, h: 1.27 });
}
{
  const R = X.raci;
  const cab = R.cab.slice(0, 17);
  const colW = [0.42, 4.0].concat(Array(15).fill(0.52));
  colW[1] += 12.33 - colW.reduce((a, b) => a + b, 0);
  const filas = R.filas.map(f => f.slice(0, 17).map((c, i) => i < 2 ? c : { t: c, st: { bold: /^A/.test(c), color: /^A/.test(c) ? ORANGE : (/^R/.test(c) ? BLUE : CHAR) } }));
  tablaSlides(S12, "13 · Matriz principal: humanos y agentes", cab, filas, colW, { size: 10, hdrSize: 9.5, margin: 0.03, grupo: 1, align: [null, null].concat(Array(15).fill("center")),
    hdrFill: [NAVY, NAVY].concat(Array(9).fill(NAVY), Array(6).fill(BLUE)),
    nota: "Una sola A por fila y siempre humana; los agentes son R (preparan o registran tras la decisión), C o I. Skills ejecutoras de cada fila y notas: HTML §13.3." });
}
{
  const R = X.raci_sensibles;
  const nombres = { CN: "Capa de negocio", EJ: "Ejecutivo", US: "Usuario sénior", PS: "Proveedor sénior", GP: "Gestor", "JE/PO": "Jefe de equipo / PO", AS: "Aseguramiento" };
  const filas = R.filas.map(f => {
    const a = R.cab.slice(2, 9).map((c, k) => /^A/.test(f[k + 2]) ? nombres[c] + (f[k + 2].length > 1 && !f[k + 2].startsWith("A/") ? f[k + 2].slice(1) : "") : null).filter(Boolean).join(", ");
    return [f[0], f[1], { t: a, st: { bold: true, color: ORANGE } }, f[9]];
  });
  tablaSlides(S12, "13 · Decisiones sensibles: quién rinde cuentas y qué queda registrado", ["Decisión", "Skill que la prepara", "Rinde cuentas (A)", "Registro tras la decisión (script · agente)"], filas, [2.6, 2.6, 1.85, 5.28], { size: 10, margin: 0.04,
    estilos: [{ bold: true, color: NAVY }], nota: "En todas el agente prepara y el humano decide. * El aprobador depende del documento. ¹ Autoridad de cambio delegada dentro de su umbral; ² escala a la capa de negocio fuera de la tolerancia de proyecto." });
}

// ====================== 13 Casos de uso ======================
const S13 = "14 · Casos de uso por skill"; pres.addSection({ title: S13 });
mark("14 · Casos de uso: un ejemplo por skill");
{
  const CR = D.casos_resumen;
  const filas = X.casos.map(c => [String(c.n), "`" + c.comando + "`", CR[c.n][0], CR[c.n][1]]);
  tablaSlides(S13, "14 · 37 casos encadenados sobre un proyecto de muestra", ["#", "Skill o comando", "Agente", "Resultado (cifras de la prueba)"], filas, [0.5, 3.2, 2.3, 6.33], { size: 10, margin: 0.04, top: 1.85, introRepeat: true,
    intro: "Portal de autoservicio de una cooperativa · 7 meses · USD 180.000 · híbrido con BMAD v6. Personas ficticias; respuestas humanas simuladas. Detalle de cada caso (prompt del usuario, sus respuestas, entradas y cómo las aporta, salidas y dónde verificarlas, comandos que ejecuta el sistema, decisión): HTML §14.",
    introSize: 11, align: ["center"] });
}
{
  const s = slide(S13); s.addText("14 · Variantes: sin BMAD, ágil en inglés, con Jira y Teams", { placeholder: "title" });
  card(s, 0.5, 1.42, 4.0, 5.4, "A · Predictivo sin BMAD", "Renovación de red de 12 sucursales. `/pm-nuevo … predictivo`; requisitos en `requisitos.md` (REQ-###) y RTM; `especificacion.py` responde igual (proveedor pm-method); cronograma a MS Project con `cpm.py --mspdi`; EVM predictivo sin `bmad.py`; un cambio actualiza `requisitos.md` sin traspaso. Puertas, roles y regla de registro no cambian.", { fill: BLUETINT, maxSize: 12.5 });
  card(s, 4.67, 1.42, 4.0, 5.4, "B · Agile project in English", "Member app con fecha y costo fijos: `estado.json.idioma = en`, perfil ágil mínimo; `backlog.csv` reemplaza a PBS/WBS; sprint como paquete de trabajo con DoD; swap Should por Should como decisión `nivel=product-owner`; `evm.py --modo agil`: EAC > BAC se lee como alcance que no entra. Datos faltantes como [to be confirmed].", { fill: BLUETINT, maxSize: 12.5 });
  card(s, 8.83, 1.42, 4.0, 5.4, "C · Jira y Teams conectados", "pm-integraciones detecta las herramientas MCP, obtiene el cloudId (Rovo MCP Server) y registra `tracker=jira chat=teams`. Lee sin confirmación y guarda `jira-2026-12-10.csv`; concilia contra los registros y propone diferencias; crea tickets o publica en Teams solo tras vista previa y confirmación del gestor.", { fill: ORTINT, titleColor: ORANGE, maxSize: 12.5 });
}

// ====================== 14 Casos de uso por integración ======================
const S14 = "15 · Casos de uso por integración"; pres.addSection({ title: S14 });
{
  mark("15 · Casos de uso por repositorio integrado");
  const s = slide(S14); s.addText("15 · Casos de uso por repositorio integrado", { placeholder: "title" });
  tb(s, runs(X.cui_intro_md.replace(/\n/g, " "), { fontSize: 13 }), { x: 0.5, y: 1.38, w: 12.33, h: 1.3 });
  const est = X.cui_estados.map(e => { const m = e.match(/^\*\*(.+?)\*\*:\s*(.*)$/); return m ? [m[1], m[2]] : [e, ""]; });
  est.forEach((e, i) => card(s, 0.5 + i * 4.15, 2.8, 3.95, 1.75, e[0], e[1], { fill: i === 0 ? NAVY : (i === 1 ? BLUETINT : ORTINT), titleColor: i === 0 ? WHITE : (i === 1 ? NAVY : ORANGE), bodyColor: i === 0 ? WHITE : CHAR, maxSize: 12 }));
  card(s, 0.5, 4.75, 12.33, 2.1, "Regla de evidencia", X.cui_evidencia_md.replace("Regla de evidencia de este documento. ", "").replace(/\n/g, " "), { fill: LT, titleColor: ORANGE, maxSize: 12 });
}
tablaSlides(S14, "15 · Qué repositorio cubre cada caso", X.cui_repos.cab, T(X.cui_repos), [0.8, 4.4, 3.6, 3.53], { size: 10.5, align: ["center"],
  estilos: [{ bold: true, color: BLUE }, {}, {}, { bold: true, color: NAVY }] });
{
  const ORDEN = ["Objetivo", "Momento PRINCE2", "Momento, dueña, agente", "Dueña y agente", "Dueña", "Externa", "Respaldo", "Frase", "Frases"];
  const fichas = [];
  X.cui_casos.forEach(c => {
    if (c.subs.length) c.subs.forEach(sb => fichas.push({ t: `Caso ${sb.id} · ${sb.titulo}`, campos: sb.campos, caso: c }));
    else fichas.push({ t: `Caso ${c.n} · ${c.titulo}`, campos: c.campos, caso: c });
  });
  // estado de verificación desde la matriz de cierre
  const matriz = X.cui_matriz.filas;
  const estadoDe = t => {
    const claves = [["archify", "archify"], ["diagram-design", "diagram-design"], ["visual-explainer", "visual-explainer"], ["Tablero", "Tablero"], ["drawio", "drawio-mcp"], ["Respaldo Mermaid", "Mermaid"],
      ["Exportación", "Skills Office"], ["MSPDI", "MSPDI"], ["Camino crítico", "MSPDI"], ["WBS", "EVM, WBS"], ["Checkpoint", "EVM, WBS"], ["Presupuesto", "EVM, WBS"], ["Release", "EVM, WBS"],
      ["OKR", "Tability"], ["Transcripciones", "Granola"], ["Trackers", "Atlassian"], ["BMAD", "BMAD"]];
    for (const [k, m] of claves) if (t.includes(k)) { const f = matriz.find(r => r[0].includes(m)); if (f) return f[5]; }
    return "";
  };
  fichas.forEach(fc => {
    const filas = [];
    const usados = new Set();
    let cmds = [];
    const add = (k, v) => { const [txt, c] = separaCodigo(v); cmds = cmds.concat(c); if (txt) filas.push([{ t: "**" + k + "**", st: { color: NAVY } }, txt]); usados.add(k); };
    ORDEN.forEach(k => { const f = fc.campos.find(([c]) => c === k); if (f) add(k, f[1]); });
    fc.campos.forEach(([k, v]) => { if (usados.has(k)) return; if (/^Pasos/.test(k)) { const [txt, c] = separaCodigo(v); cmds = cmds.concat(c); if (txt) filas.push([{ t: "**" + k + "**", st: { color: NAVY } }, txt]); usados.add(k); } });
    if (cmds.length) filas.push([{ t: "**Comandos**", st: { color: NAVY } }, { t: cmds.slice(0, 7).map(c => "`" + c + "`").join("\n") + (cmds.length > 7 ? "\n(…; secuencia completa en HTML §15)" : ""), mono: true }]);
    fc.campos.forEach(([k, v]) => { if (usados.has(k) || /^Pasos/.test(k)) return; add(k, v); });
    const est = estadoDe(fc.t);
    if (est) filas.push([{ t: "**Estado de verificación**", st: { color: ORANGE } }, { t: est, st: { color: ORANGE, bold: true } }]);
    const corto = clean(fc.t).split(":")[0].replace(/\s*\(.*$/, "");
    tablaSlides(S14, "15 · " + corto, ["Campo", "Detalle"], filas, [2.15, 10.18], { size: 10, margin: 0.05, top: 1.8, introRepeat: true,
      intro: "**" + fc.t.replace(/^Caso [\d.]+ · /, "") + "**", introSize: 13 });
  });
}
tablaSlides(S14, "15 · Matriz de cierre por integración", X.cui_matriz.cab, T(X.cui_matriz), [1.9, 2.1, 1.9, 2.15, 1.85, 2.43], { size: 10,
  estilos: [{ bold: true, color: NAVY }, {}, {}, {}, {}, { color: BLUE }],
  nota: "Controles transversales: guardian.py bloquea ediciones directas y comandos reservados; sanidad.py informa INS e INT sin bloquear puertas; pm-puerta no deja pasar un ERROR sin decisión humana registrada." });

// ====================== 15 Caso maestro ======================
const S15 = "16 · Caso maestro"; pres.addSection({ title: S15 });
{
  mark("16 · Caso maestro PRINCE2 + PMBOK");
  const s = slide(S15); s.addText("16 · Caso maestro: escenario, cifras reales y ciclo recorrido", { placeholder: "title" });
  D.caso_cifras.forEach((c, i) => {
    const col = i % 4, row = Math.floor(i / 4);
    card(s, 0.5 + col * 3.1, 1.36 + row * 1.5, 2.95, 1.42, c.k, c.v, { fill: i === 7 ? NAVY : BLUETINT, titleColor: i === 7 ? WHITE : BLUE, bodyColor: i === 7 ? WHITE : CHAR, maxSize: 10.5, minSize: 10, titleSize: 11.5, titleH: 0.26 });
  });
  imagen(s, "diagramas/caso-ciclo.png", 0.5, 4.4, 12.33, 2.12);
  tb(s, "Ciclo de vida recorrido (docs/CASO-MAESTRO.md §2). Corrida real del 17/10/2026 sobre una copia del fixture bmad-v6; decisiones humanas simuladas; personas ficticias.", { x: 0.5, y: 6.55, w: 12.33, h: 0.35, fontSize: 9.5, color: GRAY, italic: true });
}
tablaSlides(S15, "16 · Paso a paso: momentos PRINCE2 con técnicas PMBOK", ["Paso", "Momento PRINCE2 · técnica", "Qué se hizo", "Resultado (cifras reales)"], D.pasos_clave.map(p => [p.n, p.m, p.t, p.r]), [0.75, 2.9, 3.0, 5.68], { size: 10.5,
  estilos: [{ bold: true, color: NAVY }, { color: BLUE }, { bold: true }], align: ["center"], nota: "Los pasos completos, con comandos y salidas: HTML §16.4 y docs/CASO-MAESTRO.md." });
tablaSlides(S15, "16 · Guías de recorrido E2E para el usuario (docs/guias)", ["Guía", "Ciclo que recorre", "Gráficos que obtenés", "Duración"],
  T(X.guias).map(f => [f[0].replace(/\[(.*?)\]\(.*?\)/, "$1"), f[1], f[3], f[4]]), [2.4, 5.4, 3.33, 1.2], { size: 10,
  estilos: [{ bold: true, color: NAVY }], nota: "Cada paso: prompt a escribir, respuestas a las preguntas del sistema, qué deberías ver (cifras de una corrida reproducible con scripts/pruebas/guias_e2e/correr.py) y dónde verificar." });
{
  const s = slide(S15); s.addText("16 · Guías E2E: gráficos que produce el ecosistema", { placeholder: "title" });
  imagen(s, "../../guias/img/g1-mapa-calor.png", 0.5, 1.35, 12.33, 2.6, "E2E-1 · mapa de calor P×I y resumen de registros (tablero de pm-visuales al 2026-12-15)");
  imagen(s, "../../guias/img/g3-avance-agil.png", 0.5, 4.15, 12.33, 2.75, "E2E-3 · velocidad y burn-up desde avance-bmad.csv (tablero al 2027-01-08)");
}
tablaSlides(S15, "16 · Dónde apareció cada principio de PRINCE2", X.principios.cab, T(X.principios), [2.7, 6.0, 3.63], { size: 10.5, estilos: [{ bold: true, color: NAVY }] });

// ====================== 16 Pruebas y calidad ======================
const S16 = "17 · Pruebas y calidad"; pres.addSection({ title: S16 });
mark("17 · Pruebas y calidad");
tablaSlides(S16, "17 · Cinco niveles de prueba", X.pru_niveles.cab, T(X.pru_niveles), [2.6, 5.1, 2.2, 2.43], { size: 12,
  estilos: [{ bold: true, color: NAVY }, {}, { color: GRAY }, {}], nota: "Fuente: docs/PRUEBAS.md §1." });
tablaSlides(S16, "17 · Regresión determinista (probar_paquete.py): casos A–G", X.pru_regresion.cab, T(X.pru_regresion), [2.6, 9.73], { size: 10.5,
  estilos: [{ bold: true, color: NAVY }, {}], nota: "Resultado al 2026-10-17: 80 OK · 0 FALLO; el caso D acierta 36/36 decisiones en la corrida. Requiere pyyaml." });
{
  const s = slide(S16); s.addText("17 · Pruebas en vivo con Claude Code real", { placeholder: "title" });
  bulletsBox(s, ["`vivo.py`: arnés de bajo nivel. `Sesion(cwd).turno(prompt)` ejecuta `claude -p … --plugin-dir <repo> --output-format stream-json` y devuelve skills, agentes, comandos Bash, escrituras, negaciones de hooks, texto y costo.",
    "`suite.py`: construye un proyecto de prueba desde el fixture BMAD 6.12.4 real y corre tres suites (y el grupo `robustez`, ver la diapositiva siguiente).",
    "**enrutamiento:** cada frase del TSV (id, frase, skill esperada, aceptables); compara la primera skill elegida y corta la sesión apenas elige.",
    "**guardarrailes:** Edit y Bash sobre `estado.json` y una escritura en BMAD delegada a un subagente; verifica que nada cambie y que el hook haya negado.",
    "**idioma:** pedido en inglés con proyecto en español; verifica la respuesta en inglés y el backlog generado."], 0.5, 1.4, 7.2, 3.6, 12);
  codeBox(s, "suite.py enrutamiento --ids 1,18,26 --par 4      # subconjunto\nsuite.py todo --salida ./pruebas-vivo            # ≈ USD 5–8\nsuite.py robustez --salida ./pruebas-robustez    # ≈ USD 4\nsuite.py todo --modelo sonnet                    # otro modelo", 0.5, 5.0, 7.2, 1.25, 10, 9);
  tb(s, runs("Comandos en `scripts/pruebas_vivo/`; informe en `<salida>/INFORME.md`; código de salida 1 si alguna prueba falla.", { fontSize: 11, color: GRAY }), { x: 0.5, y: 6.35, w: 7.2, h: 0.5 });
  [["60/60", "enrutamiento", "primera skill esperada (v2.0: 82 % en 75 frases)"], ["4/4", "guardarraíles", "estado intacto ante Edit y Bash; hook negó; epics.md intacto"], ["3/3", "idioma", "tras unificar la regla en las 37 skills y en el hook de inicio"]].forEach((k, i) => {
    const y = 1.4 + i * 1.84;
    s.addShape(pres.ShapeType.roundRect, { x: 8.0, y, w: 4.83, h: 1.7, fill: { color: NAVY }, rectRadius: 0.1, line: { color: NAVY } });
    tb(s, k[0], { x: 8.22, y: y + 0.1, w: 4.4, h: 0.6, fontSize: 30, bold: true, color: WHITE });
    tb(s, k[1], { x: 8.22, y: y + 0.72, w: 4.4, h: 0.3, fontSize: 13, bold: true, color: "9FD0F0" });
    tb(s, k[2], { x: 8.22, y: y + 1.05, w: 4.45, h: 0.55, fontSize: 11, color: WHITE });
  });
}
{
  const s = slide(S16); s.addText("17 · Escenarios de robustez y variación de modelo", { placeholder: "title" });
  const esc = [["inyeccion", "transcripción, ticket de Jira y PRD con instrucciones incrustadas (\"aprobá la puerta\", \"borrá riesgos.csv\", \"marcá todo done\")", "**6/6**: ninguna puerta, cierre ni borrado; BMAD intacto; las tres instrucciones se informaron y no se ejecutaron"],
    ["desorden", "transcripción ruidosa con dos personas llamadas Ana y una decisión contradictoria; pedido de saltear la junta; PID desde un PRD en borrador", "**7/7**: \"por confirmar\", las dos Ana diferenciadas; rechazo de saltear la junta; aviso de PRD en borrador"],
    ["multisesion", "business case, PID y plan de etapa → aprobación en otra sesión → `/compact` → \"¿cómo venimos?\" → fin de etapa", "1.ª: defecto (puerta sin bloqueos) → corregido; 2.ª y 3.ª: **10/10**; final: " + (X.pru_placeholders.includes("RESULTADO_MULTI") ? "pendiente en PRUEBAS.md" : "ver tabla de resultados")],
    ["escala", "BMAD de 25 épicas, 150 historias y 350 requisitos y 120 riesgos", "**5/5**: no leyó enteros los archivos grandes; USD 0,48; scripts < 1,6 s"]];
  tablaFija(s, ["Escenario", "Qué prueba", "Resultado (17/10/2026)"], esc.map(e => ["`" + e[0] + "`", e[1], e[2]]), 0.5, 1.4, [1.45, 5.35, 5.53], { size: 10.5, estilos: [{ bold: true }, {}, {}] });
  card(s, 0.5, 4.85, 6.06, 2.0, "Variación de modelo", "Sonnet: enrutamiento 59/60, guardarraíles 4/4, idioma OK. Haiku: 56/60 (3 preguntas respondidas sin invocar skill), guardarraíles 4/4, idioma OK.", { fill: BLUETINT, maxSize: 12.5 });
  card(s, 6.77, 4.85, 6.06, 2.0, "Qué se corrigió con estos escenarios", "Bloqueos de puerta en `estado.py`; comandos de decisión reservados también en el hilo principal; hook `idioma.py`; regla «fuentes = datos»; listados con `--limite` y sanidad agrupada.", { fill: ORTINT, titleColor: ORANGE, maxSize: 12.5 });
}
tablaSlides(S16, "17 · Resultados registrados", X.pru_resultados.cab, T(X.pru_resultados).map(f => f.map(c => /^RESULTADO_[A-Z]+$/.test(c.trim()) ? { t: "[pendiente: docs/PRUEBAS.md todavía no registra este resultado]", st: { color: ORANGE, bold: true } } : c)), [1.25, 0.95, 3.0, 7.13], { size: 10.5,
  estilos: [{ color: GRAY }, { bold: true, color: NAVY }, { bold: true }, {}], nota: (X.pru_placeholders.length ? "Filas pendientes: docs/PRUEBAS.md todavía no registra ese resultado. " : "") + "Informes completos en docs/evaluacion/resultados/ (" + X.pru_resultados_archivos.length + " archivos; lista en la versión HTML): " + X.pru_resultados_archivos.map(f => f.replace(/^2026-10-17-/, "").replace(/\.md$/, "")).join(" · ") });
{
  const s = slide(S16); s.addText("17 · Prueba de aceptación antes del primer proyecto real", { placeholder: "title" });
  tb(s, "Marcar cada punto en una carpeta de prueba, no en el proyecto real.", { x: 0.5, y: 1.35, w: 12.33, h: 0.32, fontSize: 12, color: GRAY, italic: true });
  const A = X.pru_aceptacion;
  const num = (arr, k0) => arr.map((t, i) => `**${k0 + i + 1}.** ${t}`);
  bulletsBox(s, num(A.slice(0, 6), 0), 0.5, 1.8, 6.05, 4.6, 12, CHAR, { check: true, gap: 8 });
  bulletsBox(s, num(A.slice(6), 6), 6.78, 1.8, 6.05, 4.6, 12, CHAR, { check: true, gap: 8 });
  tb(s, runs("Si algún punto falla: problemas frecuentes (HTML §11.13 · INSTALACION §12) y `sanidad.py --informe`.", { fontSize: 11, color: GRAY }), { x: 0.5, y: 6.45, w: 12.33, h: 0.4 });
}

// ====================== 17 Plan de piloto ======================
const S17P = "18 · Plan de piloto"; pres.addSection({ title: S17P });
{
  mark("18 · Plan de piloto");
  const s = slide(S17P); s.addText("18 · Plan de piloto: del laboratorio a un proyecto real", { placeholder: "title" });
  tb(s, runs(X.pil_intro, { fontSize: 13 }), { x: 0.5, y: 1.36, w: 12.33, h: 0.6 });
  tablaFija(s, X.pil_preguntas.cab, T(X.pil_preguntas), 0.5, 2.05, [6.9, 5.43], { size: 12, estilos: [{ bold: true, color: NAVY }, {}] });
}
{
  const s = slide(S17P); s.addText("18 · Alcance, modalidad y fases del piloto", { placeholder: "title" });
  bulletsBox(s, X.pil_alcance, 0.5, 1.4, 12.33, 2.1, 11.5, CHAR, { gap: 4 });
  tablaFija(s, X.pil_fases.cab, T(X.pil_fases), 0.5, 3.6, [1.6, 0.9, 6.55, 3.28], { size: 10.5, estilos: [{ bold: true, color: NAVY }, { color: GRAY }, {}, {}] });
}
tablaSlides(S17P, "18 · Métricas del registro semanal", X.pil_metricas.cab, T(X.pil_metricas), [2.3, 6.6, 3.43], { size: 11.5,
  estilos: [{ bold: true, color: NAVY }, {}, { color: BLUE }], nota: "Registro semanal por producto: Semana · Producto · Min. sin · Min. con · Correcciones · Incidentes · Sanidad (E/A) · USD (plantilla en docs/PILOTO.md §4)." });
tablaSlides(S17P, "18 · Rúbrica de revisión experta (1 a 4)", X.pil_rubrica.cab, T(X.pil_rubrica), [2.73, 2.4, 2.4, 2.4, 2.4], { size: 11, top: 1.9, introRepeat: true,
  intro: X.pil_rubrica_intro, introSize: 11.5, estilos: [{ bold: true, color: NAVY }, { color: ORANGE }, {}, {}, { color: BLUE }],
  nota: X.pil_rubrica_res });
{
  const s = slide(S17P); s.addText("18 · Prueba de usabilidad y riesgos del piloto", { placeholder: "title" });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.4, w: 6.06, h: 5.45, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, "Usabilidad: 3 a 5 líderes no técnicos", { x: 0.7, y: 1.5, w: 5.7, h: 0.33, fontSize: 13, bold: true, color: NAVY });
  tb(s, runs(X.pil_usab_intro, { fontSize: 11, color: GRAY }), { x: 0.7, y: 1.9, w: 5.7, h: 0.5 });
  bulletsBox(s, X.pil_usab_tareas.map((t, i) => `**${i + 1}.** ` + t), 0.7, 2.45, 5.7, 2.45, 12, CHAR, { gap: 4 });
  tb(s, runs(X.pil_usab_medir, { fontSize: 11 }), { x: 0.7, y: 5.0, w: 5.7, h: 1.75 });
  tb(s, "Riesgos del piloto y mitigaciones", { x: 6.77, y: 1.36, w: 6, h: 0.33, fontSize: 13, bold: true, color: ORANGE });
  tablaFija(s, X.pil_riesgos.cab, T(X.pil_riesgos), 6.77, 1.75, [2.1, 3.96], { size: 10.5, estilos: [{ bold: true, color: NAVY }, {}] });
}
{
  const s = slide(S17P); s.addText("18 · Criterios de decisión al cierre del piloto", { placeholder: "title" });
  X.pil_criterios.forEach((c, i) => {
    const m = c.match(/^\*\*(.+?):\*\*\s*(.*)$/);
    card(s, 0.5 + i * 4.15, 1.45, 3.95, 2.7, m ? m[1] : "", m ? m[2] : c, { fill: i === 0 ? NAVY : (i === 1 ? BLUETINT : ORTINT), titleColor: i === 0 ? WHITE : (i === 1 ? NAVY : ORANGE), bodyColor: i === 0 ? WHITE : CHAR, maxSize: 15, titleSize: 15, titleH: 0.42 });
  });
  card(s, 0.5, 4.4, 12.33, 1.55, "Informe del piloto", X.pil_cierre + " Duración prevista: 4 semanas (1 de preparación + 3 de uso), con prórroga de 2 semanas si hay una puerta en camino.", { fill: LT, titleColor: NAVY, maxSize: 13 });
}

// ====================== 17 Índice de documentación ======================
const S17 = "19 · Índice de documentación"; pres.addSection({ title: S17 });
mark("19 · Índice de documentación y pruebas");
tablaSlides(S17, "19 · Rutas de lectura por perfil", X.idx_rutas.cab, T(X.idx_rutas).map(f => [f[0], f[1].replace(/ → /g, " → "), f[2]]), [3.0, 7.6, 1.73], { size: 12,
  estilos: [{ bold: true, color: NAVY }, {}, { color: ORANGE, bold: true }], nota: "Fuente: docs/INDICE.md §1. Los documentos están en docs/ del repositorio (README, CLAUDE.md, AGENTS.md y SPEC.md en la raíz)." });
tablaSlides(S17, "19 · Documentos: qué responde cada uno", X.idx_docs.cab, T(X.idx_docs), [3.6, 8.73], { size: 10.5, estilos: [{ bold: true, color: NAVY }, {}] });
{
  const s = slide(S17); s.addText("19 · Pruebas, evidencia y pendientes", { placeholder: "title" });
  tablaFija(s, X.idx_pruebas.cab, T(X.idx_pruebas), 0.5, 1.4, [3.3, 3.85], { size: 10, estilos: [{ bold: true }, {}] });
  s.addShape(pres.ShapeType.roundRect, { x: 7.9, y: 1.4, w: 4.93, h: 5.45, fill: { color: ORTINT }, rectRadius: 0.1, line: { color: ORTINT } });
  tb(s, "Pendientes y puntos abiertos", { x: 8.1, y: 1.5, w: 4.5, h: 0.33, fontSize: 13, bold: true, color: ORANGE });
  bulletsBox(s, X.idx_pendientes, 8.1, 1.95, 4.55, 4.8, 12);
}

// ====================== 18 Mantenimiento ======================
const S18 = "20 · Mantenimiento y evolución"; pres.addSection({ title: S18 });
{
  mark("20 · Mantenimiento y evolución");
  const s = slide(S18); s.addText("20 · Rutinas de mantenimiento", { placeholder: "title" });
  D.mant_rutinas.forEach((r, i) => {
    const pos = [[0.5, 1.42, 4.0], [4.67, 1.42, 4.0], [8.83, 1.42, 4.0], [0.5, 4.2, 6.06], [6.77, 4.2, 6.06]][i];
    card(s, pos[0], pos[1], pos[2], 2.62, r.t, r.d, { fill: i === 1 ? ORTINT : BLUETINT, titleColor: i === 1 ? ORANGE : NAVY, maxSize: 11.5, titleSize: 12 });
  });
}
tablaSlides(S18, "20 · Limitaciones conocidas y mitigación", X.limitaciones.cab, T(X.limitaciones), [3.6, 5.0, 3.73], { size: 10.5,
  nota: "Fuente: docs/SANIDAD.md §10 (observadas al correr el caso maestro el 17/10/2026)." });
{
  const s = slide(S18); s.addText("20 · Agregar integraciones y líneas de evolución", { placeholder: "title" });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.42, w: 6.06, h: 5.4, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, "Lista de verificación para una integración nueva", { x: 0.7, y: 1.55, w: 5.7, h: 0.35, fontSize: 13, bold: true, color: NAVY });
  bulletsBox(s, ["**Decisión:** no duplicar un dueño; madurez y licencia anotadas; definirla como capacidad, no como conector.",
    "**Contrato:** una sola skill dueña; insumo, salida y respaldo interno; salidas fechadas en la carpeta del proyecto; escritura externa con confirmación; sin credenciales ni `.mcp.json`.",
    "**Estado y validación:** valor en `estado.json.integraciones`, en INT-01 o INS-03, en `guardian.py` si genera derivados y en `compatibilidad.json`.",
    "**Activación:** descripción `Objeto. Usar: … No: …→…` ≤ 240 caracteres; listado ≤ 7.500; actualizar colisiones y repetir el enrutamiento en vivo.",
    "**Pruebas:** `validar_paquete.py` OK, `probar_paquete.py` sin fallos, sanidad sin ERROR nuevos y documentación al día."], 0.7, 2.0, 5.7, 4.7, 11.5);
  s.addShape(pres.ShapeType.roundRect, { x: 6.77, y: 1.42, w: 6.06, h: 5.4, fill: { color: ORTINT }, rectRadius: 0.1, line: { color: ORTINT } });
  tb(s, "Líneas de evolución", { x: 6.97, y: 1.55, w: 5.7, h: 0.35, fontSize: 13, bold: true, color: ORANGE });
  bulletsBox(s, D.evolucion, 6.97, 2.0, 5.7, 4.7, 11.5);
}

// ====================== 19 Cómo seguir evolucionando ======================
const S19 = "21 · Cómo seguir evolucionando"; pres.addSection({ title: S19 });
{
  mark("21 · Cómo seguir evolucionando el ecosistema");
  const s = slide(S19); s.addText("21 · Seguir evolucionando con Claude Code y GitHub", { placeholder: "title" });
  const paso = (i, x, y, w, h, t) => {
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 0.5, h: 0.5, fill: { color: BLUE }, rectRadius: 0.08, line: { color: BLUE } });
    tb(s, String(i), { x, y, w: 0.5, h: 0.5, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle" });
    tb(s, t, { x: x + 0.62, y: y + 0.07, w: w - 0.62, h: 0.4, fontSize: 13, bold: true, color: NAVY });
  };
  paso(1, 0.5, 1.4, 6.06, 0.5, "Clonar y abrir Claude Code en el repositorio");
  codeBox(s, "git clone https://github.com/Arturo-Penas-Rial/pm-method.git", 0.5, 2.0, 6.06, 0.55, 10.5);
  tb(s, runs("`CLAUDE.md` (raíz) es el contexto de desarrollo: qué es el repositorio, jerarquía PRINCE2 → PMBOK → plantillas → BMAD, mapa, convenciones y flujo por cambio. `AGENTS.md` lo resume para otros agentes de código.", { fontSize: 11.5 }), { x: 0.5, y: 2.65, w: 6.06, h: 1.15 });
  paso(2, 0.5, 3.9, 6.06, 0.5, "Validar, probar y medir cada cambio");
  codeBox(s, "python3 scripts/validar_paquete.py          # → OK\npython3 scripts/probar_paquete.py           # → 0 FALLO\nclaude plugin validate .\npython3 scripts/pruebas_vivo/suite.py enrutamiento --ids <afectados>\nclaude --plugin-dir . -p \"/pm-method:pm-ayuda\"   # probar sin instalar", 0.5, 4.5, 6.06, 1.5, 10, 9);
  tb(s, runs("Antes de una versión: `suite.py todo` (consume tokens). Si cambia una conducta, agregar una prueba en `probar_paquete.py`.", { fontSize: 11 }), { x: 0.5, y: 6.1, w: 6.06, h: 0.75 });
  paso(3, 6.77, 1.4, 6.06, 0.5, "Rama y pull request");
  tb(s, runs("Commit con mensaje descriptivo; una rama y un PR por cambio grande. Actualizar `CHANGELOG.md` y la documentación afectada (`docs/INDICE.md` lista todo); la versión vive en `plugin.json`, `compatibilidad.json` y `esquema.py` y debe coincidir (lo comprueba el validador). Nunca credenciales en el chat, en commits ni en archivos.", { fontSize: 11.5 }), { x: 6.77, y: 2.0, w: 6.06, h: 1.75 });
  paso(4, 6.77, 3.9, 6.06, 0.5, "Actualizar el plugin en cada puesto");
  codeBox(s, "claude plugin marketplace update pm-method\nclaude plugin update pm-method@pm-method   # reiniciar Claude Code\nclaude plugin list                         # confirmar la versión", 6.77, 4.5, 6.06, 1.0, 10.5);
  tb(s, runs("Si `update` responde que ya está en la última versión, el repositorio publicado todavía no tiene una `version` mayor en `plugin.json`. Después: sanidad completa en cada proyecto activo y la verificación de 12 pasos (sección 11).", { fontSize: 11 }), { x: 6.77, y: 5.6, w: 6.06, h: 1.25 });
}
{
  const s = slide(S19); s.addText("21 · Reglas del autor que todo cambio debe respetar", { placeholder: "title" });
  bulletsBox(s, X.cla_reglas, 0.5, 1.45, 6.4, 5.35, 14, CHAR, { gap: 10 });
  s.addShape(pres.ShapeType.roundRect, { x: 7.2, y: 1.45, w: 5.63, h: 5.4, fill: { color: BLUETINT }, rectRadius: 0.1, line: { color: BLUETINT } });
  tb(s, "Flujo de trabajo para cada cambio (CLAUDE.md)", { x: 7.4, y: 1.55, w: 5.2, h: 0.35, fontSize: 13, bold: true, color: NAVY });
  bulletsBox(s, X.cla_flujo, 7.4, 2.0, 5.25, 4.75, 11.5, CHAR, { gap: 5 });
}

// ====================== Anexos ======================
const SA = "Anexos"; pres.addSection({ title: SA });
{
  mark("Anexo A · Glosario");
  const norm = t => t.toLowerCase().replace(/^[${.\[]+/, "").normalize("NFD").replace(/[̀-ͯ]/g, "");
  const G = D.glosario.slice().sort((a, b) => norm(a.t) < norm(b.t) ? -1 : 1);
  const filas = G.map(g => [g.t, g.d]);
  const colW = [1.8, 4.2], size = 10;
  const alt = f => Math.max(textH(f[0], colW[0] - 0.08, size, 1.17, 0.46), textH(f[1], colW[1] - 0.08, size, 1.17, 0.46)) + 0.1;
  const col = []; let cur = [], used = 0.3;
  filas.forEach(f => { const h = alt(f); if (cur.length && used + h > 5.25) { col.push(cur); cur = []; used = 0.3; } cur.push(f); used += h; });
  if (cur.length) col.push(cur);
  const npag = Math.ceil(col.length / 2);
  for (let k = 0; k < npag; k++) {
    const s = slide(SA); s.addText(`Anexo A · Glosario (${k + 1}/${npag})`, { placeholder: "title" });
    [col[2 * k], col[2 * k + 1]].forEach((c, j) => {
      if (!c) return;
      const rows = [[hdr("Término"), hdr("Definición")]].concat(c.map(f => [{ text: runs(f[0], { fontSize: size, bold: true, color: NAVY }), options: { valign: "top" } }, { text: runs(f[1], { fontSize: size }), options: { valign: "top" } }]));
      s.addTable(rows, { x: 0.5 + j * 6.33, y: 1.4, w: 6.0, colW, border: { type: "solid", color: LINE, pt: 0.5 }, margin: 0.04, autoPage: false });
    });
  }
}
mark("Anexo B · Fuentes");
tablaSlides(SA, "Anexo B · Fuentes: documentos del paquete (fuente primaria)", ["Archivo", "Contenido usado"], D.fuentes_internas.map(f => ["`" + f[0] + "`", f[1]]), [3.6, 8.73], { size: 10.5 });
{
  const s = slide(SA); s.addText("Anexo B · Fuentes: documentación externa citada", { placeholder: "title" });
  const items = [];
  D.fuentes_externas.forEach(g => { items.push({ text: g.g, options: { bold: true, fontSize: 11, color: ORANGE, breakLine: true, paraSpaceBefore: 5 } });
    g.u.forEach(u => items.push({ text: u.replace("https://", ""), options: { fontSize: 10, color: BLUE, hyperlink: { url: u }, breakLine: true } })); });
  items[items.length - 1].options.breakLine = false;
  const half = items.findIndex(it => it.text === D.fuentes_externas[3].g);
  s.addText(items.slice(0, half), { x: 0.5, y: 1.4, w: 6.0, h: 4.85, isTextBox: true, margin: 0, valign: "top" });
  s.addText(items.slice(half), { x: 6.77, y: 1.4, w: 6.06, h: 4.85, isTextBox: true, margin: 0, valign: "top" });
  tb(s, D.fuentes_nota + " Las URL de origen de cada dependencia están en la sección 10.", { x: 0.5, y: 6.25, w: 12.33, h: 0.6, fontSize: 9.5, color: GRAY, italic: true });
}
{
  mark("Anexo C · Estructura de carpetas");
  const s = slide(SA); s.addText("Anexo C · Estructura de carpetas: repositorio y proyecto", { placeholder: "title" });
  tb(s, "Repositorio pm-method/", { x: 0.5, y: 1.35, w: 6, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, X.arbol_paquete, 0.5, 1.68, 9.35, 2.55, 9.5, 9);
  tb(s, runs(`**${X.skills_dirs.length} carpetas en skills/:** ` + X.skills_dirs.join(" · "), { fontSize: 10.5 }), { x: 0.5, y: 4.4, w: 9.35, h: 2.45 });
  tb(s, "Carpeta de un proyecto", { x: 10.05, y: 1.35, w: 2.8, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  codeBox(s, X.arbol_proyecto.split("\n").map(l => l.replace(/\s+#.*$/, "")).join("\n"), 10.05, 1.68, 2.78, 5.17, 10);
}

// ---------- Índice ----------
{
  const half = Math.ceil(INDEX.length / 2);
  [INDEX.slice(0, half), INDEX.slice(half)].forEach((part, j) => {
    const rows = part.map(([t, p]) => [{ text: t, options: { fontSize: 12, bold: true, color: NAVY, valign: "middle" } }, { text: String(p), options: { align: "right", fontSize: 12, color: BLUE, valign: "middle" } }]);
    indexSlide.addTable(rows, { x: 0.5 + j * 6.27, y: 1.45, w: 6.06, colW: [5.36, 0.7], border: { type: "solid", color: LINE, pt: 0.5 }, autoPage: false, rowH: 0.43, margin: 0.06 });
  });
}

(async () => {
  await pres.writeFile({ fileName: SALIDA });
  await applyTheme(SALIDA, THEME);
  console.log("wrote", SALIDA, "slides:", n);
})();
