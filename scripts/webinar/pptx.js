// Webinar pm-method · constructor del PPTX. Lo invoca generar.py (no se usa solo):
//   node pptx.js SALIDA.pptx < mazo.json              diapositivas del caso
//   node pptx.js SALIDA.pptx --ficha < ficha.json     ficha promocional del taller (2 diapositivas)
// El JSON lo arma generar.py ya validado: rutas de imagen absolutas con su tamaño en píxeles, glosario ordenado.
// Estética del Informe 2 (docs/informe/fuente/build_pptx.js): Arial, azul marino / azul / naranja, barra de título
// redondeada. Sin marca ni logo de empresa: recuadro rotulado "Logo IEEE" (o la imagen pasada con --logo).
// Escribe avisos de texto que no entra con el tamaño mínimo en stderr como líneas "AVISO: …".
const pptxgen = require("pptxgenjs");
const fs = require("fs");

const APPLY_THEME = [
  process.env.PPTX_APPLY_THEME || "",
  "/mnt/skills/public/pptx/scripts/apply_theme.js",
  ...(fs.existsSync("/root/.claude/skills/synced") ? fs.readdirSync("/root/.claude/skills/synced").map(d => `/root/.claude/skills/synced/${d}/pptx/scripts/apply_theme.js`) : []),
].find(p => p && fs.existsSync(p));
const { applyTheme } = APPLY_THEME ? require(APPLY_THEME) : { applyTheme: async () => {} };

const SALIDA = process.argv[2];
const FICHA = process.argv[3] === "--ficha";
const M = JSON.parse(fs.readFileSync(0, "utf8"));

const THEME = { name: "Webinar pm-method", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "272425", lt1: "FFFFFF", dk2: "002855", lt2: "F4F6F8", accent1: "00629B", accent2: "B5651D", accent3: "002855", accent4: "696969", accent5: "272425", accent6: "00629B", hlink: "00629B", folHlink: "002855" } };
const NAVY = "002855", BLUE = "00629B", ORANGE = "B5651D", GRAY = "696969", CHAR = "272425", WHITE = "FFFFFF", LT = "F4F6F8",
  BLUETINT = "E9F1F8", ORTINT = "FBF1E6", LINE = "E2E2E6", SKY = "9FD0F0", CODEBG = "0F2238", CODEFG = "E8EEF5";
const W = 13.33, H = 7.5, X0 = 0.5, CW = W - 1, TOP = 1.4, BOTTOM = 6.8;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };
pres.title = (FICHA ? `Ficha del taller ${M.caso} · ` : `Webinar ${M.caso} · `) + M.titulo;
pres.subject = `pm-method ${M.version}`;
pres.author = "pm-method";

const AVISOS = [];
let n = 0;
let etiqueta = "";
const aviso = t => AVISOS.push(`${etiqueta}: ${t}`);

// ---------- texto: markdown mínimo y estimación de alto ----------
const limpio = s => String(s || "").replace(/`/g, "").replace(/\*\*/g, "");
const lineas = (t, wIn, pt, em = 0.5) => limpio(t).split("\n").reduce((a, p) => a + Math.max(1, Math.ceil(p.length * pt * em / 72 / Math.max(0.3, wIn))), 0);
const altoTexto = (t, wIn, pt, ls = 1.2, em = 0.5) => lineas(t, wIn, pt, em) * pt * ls / 72;
// mayor tamaño entre max y min que entra; si ni el mínimo entra, avisa
function ajustar(t, wIn, hIn, max, min, que, em = 0.5) {
  let s = max;
  while (s > min && altoTexto(t, wIn, s, 1.2, em) > hIn) s -= 0.5;
  if (altoTexto(t, wIn, s, 1.2, em) > hIn * 1.04) aviso(`${que} no entra ni a ${min} pt; acortá el texto`);
  return s;
}
function runs(md, o = {}) {
  const size = o.fontSize || 16, color = o.color || CHAR, out = [];
  let bold = false;
  String(md || "").split(/(`[^`]*`|\*\*)/).forEach(seg => {
    if (!seg) return;
    if (seg === "**") { bold = !bold; return; }
    if (seg.length > 1 && seg.startsWith("`") && seg.endsWith("`")) {
      out.push({ text: seg.slice(1, -1), options: { fontFace: "Courier New", fontSize: size - 1, color: o.codeColor || NAVY, bold: bold || !!o.bold } });
    } else {
      out.push({ text: seg, options: { fontSize: size, color: bold ? (o.boldColor || color) : color, bold: bold || !!o.bold } });
    }
  });
  return out.length ? out : [{ text: "", options: { fontSize: size } }];
}
const tb = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, fontSize: 16, color: CHAR, valign: "top", fontFace: "Arial" }, o));
const caja = (s, x, y, w, h, fill, extra = {}) => s.addShape(pres.ShapeType.roundRect, Object.assign({ x, y, w, h, fill: { color: fill }, rectRadius: 0.1, line: { color: fill } }, extra));

// ---------- layouts ----------
const LOGO = M.logo ? "image/png;base64," + fs.readFileSync(M.logo).toString("base64") : null;
function logoObj(x, y, w, h, oscuro) {
  if (LOGO) return [{ image: { x, y, w, h, data: LOGO, sizing: { type: "contain", w, h } } }];
  const c = oscuro ? "7F9BB8" : "A9A9A9";
  return [
    { rect: { x, y, w, h, fill: { color: oscuro ? NAVY : WHITE, transparency: 100 }, line: { color: c, width: 1, dashType: "dash" } } },
    { text: { text: "Logo IEEE", options: { x, y, w, h, fontSize: h > 0.8 ? 12 : 10, color: c, align: "center", valign: "middle", margin: 0 } } },
  ];
}
const pieTexto = clase => `pm-method ${M.version} · Webinar ${M.caso}` + (clase ? ` · Clase ${clase}` : "");
const LOGO_W = 1.6, LOGO_H = 0.78;
function layouts(clave, clase) {
  const pie = pieTexto(clase);
  pres.defineSlideMaster({ title: "CONTENIDO_" + clave, background: { color: WHITE }, margin: [0.5, 0.5, 0.9, 0.5], objects: [
    ...logoObj(W - X0 - LOGO_W, 0.4, LOGO_W, LOGO_H, false),
    { rect: { x: X0, y: 0.4, w: CW - LOGO_W - 0.2, h: 0.78, fill: { color: BLUE }, rectRadius: 0.1, shape: "roundRect" } },
    { placeholder: { options: { name: "title", type: "title", x: X0 + 0.22, y: 0.4, w: CW - LOGO_W - 0.62, h: 0.78, fontSize: 24, bold: true, color: WHITE, margin: 0, valign: "middle", align: "left", fontFace: "Arial" }, text: "" } },
    { text: { text: pie, options: { x: X0, y: H - 0.48, w: 9, h: 0.3, fontSize: 10, color: GRAY, margin: 0, valign: "top" } } }],
    slideNumber: { x: W - 1.2, y: H - 0.48, w: 0.7, h: 0.3, fontSize: 10, color: GRAY, align: "right", margin: 0 } });
  const oscuros = [["OSCURO_", NAVY, { x: X0 + 0.1, y: 1.25, w: CW - 0.2, h: 1.0, fontSize: 36, color: WHITE }],
    ["SECCION_", BLUE, { x: X0 + 0.1, y: 2.35, w: CW - 0.2, h: 1.1, fontSize: 40, color: WHITE }],
    ["PREGUNTA_", NAVY, { x: X0 + 0.1, y: 0.4, w: CW - LOGO_W - 0.4, h: 0.78, fontSize: 22, color: SKY }]];
  for (const [nombre, fondo, ph] of oscuros) {
    pres.defineSlideMaster({ title: nombre + clave, background: { color: fondo }, objects: [
      ...logoObj(W - X0 - LOGO_W, 0.4, LOGO_W, LOGO_H, true),
      { placeholder: { options: Object.assign({ name: "title", type: "title", bold: true, margin: 0, align: "left", valign: nombre === "PREGUNTA_" ? "middle" : "top", fontFace: "Arial" }, ph), text: "" } },
      { text: { text: pie, options: { x: X0, y: H - 0.48, w: 9, h: 0.3, fontSize: 10, color: "D6E4F0", margin: 0, valign: "top" } } }],
      slideNumber: { x: W - 1.2, y: H - 0.48, w: 0.7, h: 0.3, fontSize: 10, color: "D6E4F0", align: "right", margin: 0 } });
  }
}
const nueva = (layout, seccion) => { n++; return pres.addSlide({ masterName: layout, sectionTitle: seccion }); };
// el tamaño va en el run: las opciones del marcador de posición prevalecen sobre las de addText
const ph = (s, t, size) => s.addText([{ text: limpio(t), options: { fontSize: size } }], { placeholder: "title" });
const titulo = (s, t, max = 24, wIn = CW - LOGO_W - 0.62, hIn = 0.74, min = 16) => ph(s, t, ajustar(t, wIn, hIn, max, min, "el título", 0.55));

// ---------- piezas ----------
function filasNumeradas(s, puntos, y, hDisp, o = {}) {
  const k = puntos.length; if (!k) return;
  const gap = 0.16, rowH = Math.min(o.maxRow || 1.15, (hDisp - gap * (k - 1)) / k);
  const wTxt = (o.w || CW) - 1.15;
  const txt = puntos.join("\n");
  let size = o.max || 20;
  while (size > 14 && puntos.some(p => altoTexto(p, wTxt, size) > rowH - 0.16)) size -= 0.5;
  puntos.forEach((p, i) => {
    const yy = y + i * (rowH + gap), x = o.x || X0;
    caja(s, x, yy, o.w || CW, rowH, i % 2 ? LT : BLUETINT);
    caja(s, x + 0.18, yy + (rowH - 0.5) / 2, 0.5, 0.5, o.color || BLUE, { rectRadius: 0.08 });
    tb(s, String(i + 1), { x: x + 0.18, y: yy + (rowH - 0.5) / 2, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle" });
    if (altoTexto(p, wTxt, size) > rowH - 0.1) aviso(`el punto ${i + 1} no entra ni a 14 pt; acortalo`);
    tb(s, runs(p, { fontSize: size }), { x: x + 0.9, y: yy + 0.06, w: wTxt, h: rowH - 0.12, valign: "middle" });
  });
  return txt;
}
function viñetas(s, puntos, x, y, w, h, o = {}) {
  if (!puntos.length) return;
  const gap = o.gap || 8, color = o.color || CHAR, marca = o.marca || "▪", colMarca = o.colMarca || BLUE, em = o.em || 0.53;
  const alto = sz => puntos.reduce((a, p) => a + altoTexto("XX " + p, w, sz, 1.2, em) + gap / 72, 0);
  let size = o.max || 20;
  while (size > (o.min || 14) && alto(size) > h) size -= 0.5;
  if (alto(size) > h * 1.04) aviso(`la lista no entra ni a ${o.min || 14} pt; acortá los puntos`);
  const out = [];
  puntos.forEach((p, i) => {
    const r = [{ text: marca + "  ", options: { fontSize: size, color: colMarca, bold: true } }].concat(runs(p, { fontSize: size, color, codeColor: o.codeColor }));
    r.forEach(z => { z.options = Object.assign({}, z.options, { paraSpaceAfter: gap }); });
    r[r.length - 1].options.breakLine = i < puntos.length - 1;
    out.push(...r);
  });
  tb(s, out, { x, y, w, h });
}
function subtitulo(s, d, y, o = {}) {
  if (!d.subtitulo) return y;
  const w = o.w || CW, max = o.max || 18;
  const size = ajustar(d.subtitulo, w, o.h || 0.62, max, 14, "el subtítulo");
  const h = Math.max(0.36, Math.min(o.h || 0.62, altoTexto(d.subtitulo, w, size) + 0.04));
  tb(s, runs(d.subtitulo, { fontSize: size, color: o.color || ORANGE, bold: o.bold !== false }), { x: o.x || X0, y, w, h });
  return y + h + 0.2;
}
function imagen(s, img, x, y, w, h) {
  let ww = w, hh = w * img.h / img.w;
  if (hh > h) { hh = h; ww = h * img.w / img.h; }
  const xx = x + (w - ww) / 2, yy = y + (h - hh) / 2;
  s.addImage({ path: img.ruta, x: xx, y: yy, w: ww, h: hh, altText: img.alt || "" });
  s.addShape(pres.ShapeType.rect, { x: xx, y: yy, w: ww, h: hh, fill: { color: WHITE, transparency: 100 }, line: { color: LINE, width: 0.75 } });
}
function codigo(s, texto, x, y, w, hMax) {
  let size = 18;
  const alto = sz => altoTexto(texto, w - 0.5, sz, 1.25, 0.6) + 0.36;
  while (size > 13 && alto(size) > hMax) size -= 0.5;
  if (alto(size) > hMax * 1.04) aviso("el prompt no entra ni a 13 pt; acortalo o partilo en dos diapositivas");
  const h = Math.min(hMax, Math.max(0.8, alto(size)));
  caja(s, x, y, w, h, CODEBG, { rectRadius: 0.08 });
  tb(s, texto, { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: h - 0.36, fontFace: "Courier New", fontSize: size, color: CODEFG, valign: "middle" });
  return h;
}
function tarjetas(s, puntos, y, hDisp, o = {}) {
  const k = puntos.length; if (!k) return;
  const porFila = o.porFila || (k <= 3 ? k : Math.ceil(k / 2)), filas = Math.ceil(k / porFila), gap = 0.3;
  const w = (CW - gap * (porFila - 1)) / porFila, h = Math.min(o.maxH || 99, (hDisp - gap * (filas - 1)) / filas);
  y += (hDisp - (h * filas + gap * (filas - 1))) / 2;
  // tarjeta de indicador: "**valor** texto" → valor grande y texto debajo
  const kpi = o.kpi && puntos.every(p => /^\*\*[^*]+\*\*\s*\S/.test(p));
  if (kpi) {
    puntos.forEach((p, i) => {
      const [, v, t] = p.match(/^\*\*([^*]+)\*\*\s*([\s\S]*)$/);
      const x = X0 + (i % porFila) * (w + gap), yy = y + Math.floor(i / porFila) * (h + gap), oscura = i === 0;
      caja(s, x, yy, w, h, oscura ? NAVY : BLUETINT);
      const sv = ajustar(v, w - 0.44, 0.95, 40, 24, `el valor del indicador ${i + 1}`, 0.55);
      tb(s, v, { x: x + 0.22, y: yy + 0.25, w: w - 0.44, h: 0.95, fontSize: sv, bold: true, color: oscura ? WHITE : NAVY, valign: "bottom" });
      tb(s, runs(t, { fontSize: ajustar(t, w - 0.44, h - 1.45, 18, 14, `el texto del indicador ${i + 1}`), color: oscura ? SKY : CHAR }), { x: x + 0.22, y: yy + 1.3, w: w - 0.44, h: h - 1.45 });
    });
    return;
  }
  const top = o.numero ? 0.62 : 0.22, wt = w - 0.44, ht = h - top - 0.2;
  let size = o.max || 20;
  while (size > 14 && puntos.some(p => altoTexto(p, wt, size) > ht)) size -= 0.5;
  puntos.forEach((p, i) => {
    const x = X0 + (i % porFila) * (w + gap), yy = y + Math.floor(i / porFila) * (h + gap);
    const oscura = o.primeraOscura && i === 0;
    caja(s, x, yy, w, h, oscura ? NAVY : (o.fill || BLUETINT));
    if (o.numero) tb(s, String(i + 1), { x: x + 0.22, y: yy + 0.12, w: 0.8, h: 0.46, fontSize: 26, bold: true, color: oscura ? SKY : ORANGE });
    if (altoTexto(p, wt, size) > ht * 1.04) aviso(`la tarjeta ${i + 1} no entra ni a 14 pt; acortala`);
    tb(s, runs(p, { fontSize: size, color: oscura ? WHITE : CHAR, codeColor: oscura ? "CFE3F3" : NAVY }), { x: x + 0.22, y: yy + top, w: wt, h: ht, valign: o.numero ? "top" : "middle" });
  });
}

// ---------- tipos de diapositiva ----------
const R = {};
R.contenido = (s, d) => { titulo(s, d.titulo); const y = subtitulo(s, d, TOP); filasNumeradas(s, d.puntos, y, BOTTOM - y); };
R.gancho = (s, d) => {
  titulo(s, d.titulo);
  let y = TOP + 0.1;
  if (d.subtitulo) {
    const size = ajustar(d.subtitulo, CW, 1.5, 32, 20, "el subtítulo");
    tb(s, runs(d.subtitulo, { fontSize: size, color: NAVY, bold: true }), { x: X0, y, w: CW, h: 1.5, valign: "middle" });
    y += 1.8;
  }
  if (d.puntos.length) tarjetas(s, d.puntos, y, BOTTOM - y, { primeraOscura: true, porFila: d.puntos.length <= 3 ? d.puntos.length : (d.puntos.length === 4 ? 4 : 5), max: 22, maxH: 3.2 });
};
R.seccion = (s, d, c) => {
  tb(s, `Clase ${c.numero}`, { x: X0 + 0.1, y: 1.8, w: 6, h: 0.45, fontSize: 18, bold: true, color: SKY });
  titulo(s, d.titulo, 40, CW - 0.2, 1.1, 24);
  let y = 3.6;
  if (d.subtitulo) {
    const size = ajustar(d.subtitulo, CW - 0.2, 0.9, 22, 16, "el subtítulo");
    tb(s, runs(d.subtitulo, { fontSize: size, color: WHITE }), { x: X0 + 0.1, y, w: CW - 0.2, h: 0.9 }); y += 1.05;
  }
  viñetas(s, d.puntos, X0 + 0.1, y, CW - 0.2, BOTTOM - y, { color: WHITE, colMarca: SKY, codeColor: "CFE3F3", max: 18 });
};
function conImagen(s, d, lectura) {
  titulo(s, d.titulo);
  let y = subtitulo(s, d, TOP, { color: CHAR, bold: false, max: 17 });
  const h = BOTTOM - y;
  if (!d.imagen) { tarjetas(s, d.puntos, y, h, { porFila: d.puntos.length <= 3 ? d.puntos.length : 3, primeraOscura: true, kpi: true, maxH: 2.6, max: 22 }); return; }
  if (d.puntos.length) {
    const wc = lectura ? 4.6 : 3.95, wi = CW - wc - 0.3;
    imagen(s, d.imagen, X0, y, wi, h);
    const xc = X0 + wi + 0.3;
    caja(s, xc, y, wc, h, lectura ? BLUETINT : LT);
    tb(s, lectura ? "Cómo leerlo" : "Para mirar", { x: xc + 0.22, y: y + 0.16, w: wc - 0.44, h: 0.38, fontSize: 16, bold: true, color: lectura ? NAVY : ORANGE });
    viñetas(s, d.puntos, xc + 0.22, y + 0.62, wc - 0.44, h - 0.8, { max: 17 });
  } else imagen(s, d.imagen, X0, y, CW, h);
}
R.imagen = (s, d) => conImagen(s, d, false);
R.indicadores = (s, d) => conImagen(s, d, true);
R.demo = (s, d) => {
  titulo(s, d.titulo);
  let y = subtitulo(s, d, TOP);
  tb(s, "Prompt · escribilo tal cual", { x: X0, y, w: 6, h: 0.32, fontSize: 13, bold: true, color: GRAY });
  y += 0.38;
  y += codigo(s, d.prompt_vista || d.prompt, X0, y, CW, d.puntos.length ? 2.3 : BOTTOM - y) + 0.3;
  if (d.puntos.length) {
    caja(s, X0, y, CW, BOTTOM - y, LT);
    tb(s, "Qué deberías ver", { x: X0 + 0.25, y: y + 0.14, w: 6, h: 0.36, fontSize: 16, bold: true, color: NAVY });
    viñetas(s, d.puntos, X0 + 0.25, y + 0.58, CW - 0.5, BOTTOM - y - 0.7, { marca: "✓", max: 18 });
  }
};
R.pregunta = (s, d) => {
  titulo(s, d.titulo, 22, CW - LOGO_W - 0.4, 0.74);
  let y = 1.55;
  if (d.subtitulo) { const sz = ajustar(d.subtitulo, CW - 0.2, 0.5, 18, 14, "el subtítulo"); tb(s, runs(d.subtitulo, { fontSize: sz, color: "D6E4F0" }), { x: X0 + 0.1, y, w: CW - 0.2, h: 0.5 }); y += 0.65; }
  const hq = d.puntos.length ? 2.6 : BOTTOM - y - 0.2;
  s.addShape(pres.ShapeType.ellipse, { x: X0 + 0.1, y: y + (hq - 1.3) / 2, w: 1.3, h: 1.3, fill: { color: ORANGE }, line: { color: ORANGE } });
  tb(s, "?", { x: X0 + 0.1, y: y + (hq - 1.3) / 2, w: 1.3, h: 1.3, fontSize: 54, bold: true, color: WHITE, align: "center", valign: "middle" });
  const wq = CW - 1.9, size = ajustar(d.pregunta, wq, hq, 32, 20, "la pregunta", 0.52);
  tb(s, runs(d.pregunta, { fontSize: size, color: WHITE, bold: true, codeColor: "CFE3F3" }), { x: X0 + 1.8, y, w: wq, h: hq, valign: "middle" });
  y += hq + 0.35;
  if (d.puntos.length) {
    const k = d.puntos.length, gap = 0.25, w = (CW - gap * (k - 1)) / k, h = Math.min(1.7, BOTTOM - y);
    let sz = 18;
    while (sz > 14 && d.puntos.some(p => altoTexto(p, w - 0.4, sz) > h - 0.3)) sz -= 0.5;
    d.puntos.forEach((p, i) => {
      const x = X0 + i * (w + gap);
      caja(s, x, y, w, h, "173D66");
      if (altoTexto(p, w - 0.4, sz) > (h - 0.3) * 1.04) aviso(`la opción ${i + 1} no entra ni a 14 pt; acortala`);
      tb(s, runs(p, { fontSize: sz, color: WHITE, codeColor: "CFE3F3" }), { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: h - 0.3, valign: "middle" });
    });
  }
};
R.ejercicio = (s, d) => {
  titulo(s, d.titulo);
  const y = subtitulo(s, d, TOP);
  tarjetas(s, d.puntos, y, BOTTOM - y, { numero: true, fill: ORTINT, max: 20, maxH: 2.6 });
};
R.tabla = (s, d) => {
  titulo(s, d.titulo);
  const y = subtitulo(s, d, TOP);
  const t = d.tabla, nc = t.cab.length;
  // anchos proporcionales al texto más largo de cada columna (mínimo 1,6")
  const largo = t.cab.map((c, k) => Math.max(limpio(c).length, ...t.filas.map(f => limpio(f[k] || "").length)));
  const raw = largo.map(l => Math.max(8, Math.min(60, l)));
  let colW = raw.map(r => r / raw.reduce((a, b) => a + b, 0) * CW);
  const falta = colW.reduce((a, w) => a + Math.max(0, 1.6 - w), 0);
  if (falta > 0) { const sobra = colW.filter(w => w > 1.6).reduce((a, b) => a + b, 0); colW = colW.map(w => w < 1.6 ? 1.6 : w - falta * w / sobra); }
  const m = 0.08;
  const altoTabla = sz => [t.cab, ...t.filas].reduce((a, f, i) => a + Math.max(...f.map((c, k) => altoTexto(c, colW[k] - 2 * m - 0.04, sz, 1.18, i ? 0.5 : 0.55))) + 2 * m + 0.04, 0);
  let size = 18;
  while (size > 12 && altoTabla(size) > BOTTOM - y) size -= 0.5;
  if (altoTabla(size) > (BOTTOM - y) * 1.04) aviso("la tabla no entra ni a 12 pt; acortá las celdas");
  const rows = [t.cab.map(c => ({ text: runs(c, { fontSize: size, bold: true, color: WHITE, codeColor: "CFE3F3" }), options: { fill: { color: NAVY }, valign: "middle" } }))]
    .concat(t.filas.map((f, i) => t.cab.map((_, k) => ({ text: runs(f[k] || "", { fontSize: size, bold: k === 0, color: k === 0 ? NAVY : CHAR }), options: { valign: "top", fill: { color: i % 2 ? WHITE : LT } } }))));
  s.addTable(rows, { x: X0, y, w: CW, colW, border: { type: "solid", color: LINE, pt: 0.75 }, margin: m, autoPage: false, fontFace: "Arial" });
};
R.cierre = (s, d) => {
  titulo(s, d.titulo, 36, CW - 0.2, 1.0, 22);
  let y = 2.4;
  if (d.subtitulo) { const sz = ajustar(d.subtitulo, CW - 0.2, 0.8, 20, 16, "el subtítulo"); tb(s, runs(d.subtitulo, { fontSize: sz, color: SKY, bold: true }), { x: X0 + 0.1, y, w: CW - 0.2, h: 0.8 }); y += 0.95; }
  viñetas(s, d.puntos, X0 + 0.1, y, CW - 0.2, BOTTOM - y, { color: WHITE, colMarca: SKY, marca: "✓", codeColor: "CFE3F3", max: 22, gap: 12 });
};
const LAYOUT = { seccion: "SECCION_", pregunta: "PREGUNTA_", cierre: "OSCURO_" };

// ====================================================================== mazo del caso
function mazo() {
pres.defineSlideMaster({ title: "PORTADA", background: { color: NAVY }, objects: [
  ...logoObj(0.6, 0.5, 2.2, 0.88, true),
  { text: { text: pieTexto(null), options: { x: 0.6, y: H - 0.55, w: 9, h: 0.3, fontSize: 10, color: "D6E4F0", margin: 0 } } }] });
layouts("G", null);
M.clases.forEach(c => layouts(String(c.numero), c.numero));

// ---------- portada del caso ----------
pres.addSection({ title: "Portada" });
{
  etiqueta = "portada";
  const s = nueva("PORTADA", "Portada");
  tb(s, `Webinar · pm-method ${M.version} · ${M.caso}`, { x: 0.6, y: 1.75, w: 9, h: 0.4, fontSize: 16, color: SKY, bold: true });
  const st = ajustar(M.titulo, 11.8, 1.5, 40, 26, "el título del caso", 0.55);
  tb(s, M.titulo, { x: 0.6, y: 2.25, w: 11.8, h: 1.5, fontSize: st, bold: true, color: WHITE });
  if (M.subtitulo) tb(s, runs(M.subtitulo, { fontSize: ajustar(M.subtitulo, 11.8, 0.95, 20, 14, "el subtítulo del caso"), color: "D6E4F0" }), { x: 0.6, y: 3.85, w: 11.8, h: 0.95 });
  const k = M.clases.length, gap = 0.3, w = Math.min(4.0, (12.13 - gap * (k - 1)) / k);
  M.clases.forEach((c, i) => {
    const x = 0.6 + i * (w + gap);
    caja(s, x, 5.05, w, 1.45, "173D66");
    tb(s, `Clase ${c.numero} · ${c.duracion_min} min`, { x: x + 0.22, y: 5.17, w: w - 0.44, h: 0.34, fontSize: 14, bold: true, color: SKY });
    tb(s, c.titulo, { x: x + 0.22, y: 5.55, w: w - 0.44, h: 0.85, fontSize: ajustar(c.titulo, w - 0.44, 0.85, 16, 12, `el título de la clase ${c.numero}`), color: WHITE });
  });
  s.addNotes(`Caso ${M.caso}: ${M.titulo}. ${k === 1 ? "Una clase" : k + " clases"} de ${[...new Set(M.clases.map(c => c.duracion_min))].join(" y ")} minutos. Presentá el problema que resuelve el caso y qué se van a llevar los asistentes.`);
}

// ---------- clases ----------
M.clases.forEach(c => {
  const sec = `Clase ${c.numero} · ${c.titulo}`;
  pres.addSection({ title: sec });
  {
    etiqueta = `clase ${c.numero}, portada`;
    const s = nueva("OSCURO_" + c.numero, sec);
    tb(s, `Clase ${c.numero} · ${c.duracion_min} minutos`, { x: X0 + 0.1, y: 0.7, w: 8, h: 0.4, fontSize: 16, bold: true, color: SKY });
    titulo(s, c.titulo, 36, CW - 0.2, 1.0, 24);
    tb(s, "Objetivos de la clase", { x: X0 + 0.1, y: 2.45, w: 8, h: 0.4, fontSize: 18, bold: true, color: WHITE });
    const obj = c.objetivos.slice(0, 6), gap = 0.14, y0 = 3.0, rowH = Math.min(0.85, (BOTTOM - y0 - gap * (obj.length - 1)) / Math.max(1, obj.length));
    let sz = 18;
    while (sz > 14 && obj.some(o => altoTexto(o, CW - 1.1, sz) > rowH - 0.1)) sz -= 0.5;
    obj.forEach((o, i) => {
      const y = y0 + i * (rowH + gap);
      caja(s, X0 + 0.1, y, CW - 0.2, rowH, "173D66");
      tb(s, String(i + 1), { x: X0 + 0.25, y, w: 0.45, h: rowH, fontSize: 20, bold: true, color: SKY, valign: "middle" });
      if (altoTexto(o, CW - 1.1, sz) > rowH) aviso(`el objetivo ${i + 1} no entra ni a 14 pt`);
      tb(s, runs(o, { fontSize: sz, color: WHITE, codeColor: "CFE3F3" }), { x: X0 + 0.85, y: y + 0.04, w: CW - 1.1, h: rowH - 0.08, valign: "middle" });
    });
    s.addNotes(`Clase ${c.numero} (${c.duracion_min} minutos): ${c.titulo}. Objetivos: ${c.objetivos.map(limpio).join("; ")}.`);
  }
  c.diapositivas.forEach((d, i) => {
    etiqueta = `clase ${c.numero}, diapositiva ${i + 1} (${d.tipo})`;
    const s = nueva((LAYOUT[d.tipo] || "CONTENIDO_") + c.numero, sec);
    R[d.tipo](s, d, c);
    if (d.nota) s.addNotes(limpio(d.nota));
  });
});

// ---------- glosario ----------
if (M.glosario.length) {
  pres.addSection({ title: "Glosario" });
  const colW = [2.15, 3.85], size = 12, m = 0.06, BUD = BOTTOM - TOP - 0.05;
  const alto = g => Math.max(altoTexto(g.termino, colW[0] - 2 * m - 0.04, size, 1.18, 0.55), altoTexto(g.definicion, colW[1] - 2 * m - 0.04, size, 1.18)) + 2 * m + 0.04;
  const hdrH = 0.42;
  const partir = tope => { const cols = []; let cur = [], usado = hdrH;
    M.glosario.forEach(g => { const h = alto(g); if (cur.length && usado + h > tope) { cols.push(cur); cur = []; usado = hdrH; } cur.push(g); usado += h; });
    if (cur.length) cols.push(cur); return cols; };
  let cols = partir(BUD);
  const npag = Math.ceil(cols.length / 2);
  // equilibrar: el menor alto de columna que sigue entrando en 2 × npag columnas
  const total = M.glosario.reduce((a, g) => a + alto(g), 0);
  for (let tope = hdrH + total / (2 * npag); tope < BUD; tope += 0.1) { const c = partir(tope); if (c.length <= 2 * npag) { cols = c; break; } }
  const hdr = t => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: size, valign: "middle" } });
  for (let k = 0; k < npag; k++) {
    etiqueta = `glosario ${k + 1}`;
    const s = nueva("CONTENIDO_G", "Glosario");
    ph(s, `Glosario${npag > 1 ? ` (${k + 1}/${npag})` : ""}`, 24);
    [cols[2 * k], cols[2 * k + 1]].forEach((col, j) => {
      if (!col) return;
      const rows = [[hdr("Término"), hdr("Definición")]].concat(col.map((g, i) => [
        { text: runs(g.termino, { fontSize: size, bold: true, color: NAVY }), options: { valign: "top", fill: { color: i % 2 ? WHITE : LT } } },
        { text: runs(g.definicion, { fontSize: size }), options: { valign: "top", fill: { color: i % 2 ? WHITE : LT } } }]));
      s.addTable(rows, { x: X0 + j * 6.33, y: TOP, w: 6.0, colW, border: { type: "solid", color: LINE, pt: 0.75 }, margin: m, autoPage: false, fontFace: "Arial" });
    });
    s.addNotes(`Glosario del caso ${M.caso}: ${M.glosario.length} términos${npag > 1 ? `, página ${k + 1} de ${npag}` : ""}.`);
  }
}
}

// ====================================================================== ficha del taller
// Dos diapositivas: 1) problema, objetivos, destinatarios e imagen del caso; 2) cómo se trabaja con el agente,
// requisitos y modalidad, contenidos por clase y beneficios. Las dos columnas de la 2 usan un único tamaño de letra
// (14 a 10,5 pt), el mayor con el que todo entra; si ni 10,5 pt alcanza, avisa.
// ancho medio de carácter calibrado con el render (Arial / Liberation Sans, texto en castellano): 0,44–0,46 em
const EM_FICHA = 0.46;
const altoLista = (puntos, w, sz, gap) => puntos.reduce((a, p) => a + altoTexto("XX " + p, w, sz, 1.2, EM_FICHA) + gap / 72, 0);
const PAD = 0.11, ROT = 0.36, SUB = sz => sz * 1.3 / 72, GAPL = 4;
// mayor tamaño (14 a 10,5 pt) con el que entran todas las columnas: las dos columnas usan el mismo
function tamColumnas(w, hDisp, columnas) {
  let sz = 14;
  while (sz > 10.5 && columnas.some(b => altoColumna(b, w, sz) > hDisp * 1.02)) sz -= 0.5;
  return sz;
}
const altoParte = (p, sz, wi) => p.sub ? SUB(sz) : p.lista ? altoLista(p.lista, wi, sz, GAPL) + 0.04
  : altoTexto((p.prefijo || "") + p.parrafo, wi, sz, 1.2, EM_FICHA) + 0.06;
const altoBloque = (b, sz, w) => b.rotulo ? ROT : PAD * 2 + b.partes.reduce((a, p) => a + altoParte(p, sz, w - 2 * PAD), 0);
const altoColumna = (bloques, w, sz) => bloques.reduce((a, b, i) => a + altoBloque(b, sz, w) + (i ? (b.rotulo ? 0.12 : 0.07) : 0), 0);
function columna(s, x, y, w, hDisp, bloques, que, sz) {
  const total = z => altoColumna(bloques, w, z);
  if (total(sz) > hDisp * 1.03) aviso(`${que} no entra ni a 10,5 pt; acortá los textos`);
  bloques.forEach((b, i) => {
    if (i) y += b.rotulo ? 0.12 : 0.07;
    if (b.rotulo) { tb(s, b.rotulo, { x, y, w, h: 0.32, fontSize: 16, bold: true, color: b.color || NAVY }); y += ROT; return; }
    const h = altoBloque(b, sz, w), oscuro = b.fill === NAVY;
    caja(s, x, y, w, h, b.fill, { rectRadius: 0.08 });
    let yy = y + PAD;
    b.partes.forEach(p => {
      const hp = altoParte(p, sz, w - 2 * PAD);
      if (p.sub) tb(s, p.sub, { x: x + PAD, y: yy, w: w - 2 * PAD, h: hp, fontSize: sz, bold: true, color: p.color || NAVY, valign: "top" });
      else if (p.lista) viñetas(s, p.lista, x + PAD, yy, w - 2 * PAD, hp + 0.05, { max: sz, min: sz, gap: GAPL, em: EM_FICHA,
        color: oscuro ? WHITE : CHAR, colMarca: oscuro ? SKY : (p.colMarca || BLUE), codeColor: oscuro ? "CFE3F3" : NAVY });
      else tb(s, (p.prefijo ? [{ text: p.prefijo, options: { fontSize: sz, bold: true, color: oscuro ? SKY : (p.colPrefijo || NAVY) } }] : [])
        .concat(runs(p.parrafo, { fontSize: sz, color: oscuro ? WHITE : CHAR, codeColor: oscuro ? "CFE3F3" : NAVY })), { x: x + PAD, y: yy, w: w - 2 * PAD, h: hp });
      yy += hp;
    });
    y += h;
  });
}

function ficha() {
  const pie = `pm-method ${M.version} · Webinar ${M.caso} · Ficha del taller`, BAND = 2.3, wT = CW - LOGO_W - 0.4;
  const num = { x: W - 1.2, y: H - 0.48, w: 0.7, h: 0.3, fontSize: 10, color: GRAY, align: "right", margin: 0 };
  const pieObj = { text: { text: pie, options: { x: X0, y: H - 0.48, w: 9, h: 0.3, fontSize: 10, color: GRAY, margin: 0, valign: "top" } } };
  pres.defineSlideMaster({ title: "FICHA_PORTADA", background: { color: WHITE }, objects: [
    { rect: { x: 0, y: 0, w: W, h: BAND, fill: { color: NAVY }, line: { color: NAVY } } },
    ...logoObj(W - X0 - LOGO_W, 0.36, LOGO_W, LOGO_H, true),
    { placeholder: { options: { name: "title", type: "title", x: X0, y: 0.72, w: wT, h: 0.92, fontSize: 30, bold: true, color: WHITE, margin: 0, valign: "middle", align: "left", fontFace: "Arial" }, text: "" } },
    pieObj], slideNumber: num });
  pres.defineSlideMaster({ title: "FICHA_DETALLE", background: { color: WHITE }, margin: [0.5, 0.5, 0.9, 0.5], objects: [
    ...logoObj(W - X0 - LOGO_W, 0.4, LOGO_W, LOGO_H, false),
    { rect: { x: X0, y: 0.4, w: CW - LOGO_W - 0.2, h: 0.78, fill: { color: BLUE }, rectRadius: 0.1, shape: "roundRect" } },
    { placeholder: { options: { name: "title", type: "title", x: X0 + 0.22, y: 0.4, w: CW - LOGO_W - 0.62, h: 0.78, fontSize: 24, bold: true, color: WHITE, margin: 0, valign: "middle", align: "left", fontFace: "Arial" }, text: "" } },
    pieObj], slideNumber: num });
  pres.addSection({ title: "Ficha del taller" });

  // ---------- 1 · el problema, qué vas a poder hacer, para quién y el caso real ----------
  etiqueta = "ficha, diapositiva 1";
  let s = nueva("FICHA_PORTADA", "Ficha del taller");
  tb(s, M.kicker, { x: X0, y: 0.34, w: wT, h: 0.34, fontSize: 14, bold: true, color: SKY });
  ph(s, M.titulo, ajustar(M.titulo, wT, 0.92, 30, 22, "el título", 0.55));
  tb(s, runs(M.bajada, { fontSize: ajustar(M.bajada, CW, 0.52, 17, 12, "la bajada"), color: "D6E4F0", codeColor: "CFE3F3" }), { x: X0, y: 1.72, w: CW, h: 0.52 });
  const wl = 6.95, xr = X0 + wl + 0.35, wr = W - X0 - xr;
  let y = BAND + 0.22;
  tb(s, "Qué vas a poder hacer", { x: X0, y, w: wl, h: 0.36, fontSize: 16, bold: true, color: ORANGE });
  y += 0.42;
  const k = M.objetivos.length, gap = 0.08, rowH = Math.min(0.6, (2.36 - gap * (k - 1)) / k), wo = wl - 0.72;
  let so = 15;
  while (so > 12 && M.objetivos.some(o => altoTexto(o, wo, so, 1.2, EM_FICHA) > rowH - 0.06)) so -= 0.5;
  M.objetivos.forEach((o, i) => {
    const yy = y + i * (rowH + gap);
    caja(s, X0, yy, wl, rowH, i % 2 ? LT : BLUETINT, { rectRadius: 0.06 });
    tb(s, String(i + 1), { x: X0 + 0.1, y: yy, w: 0.42, h: rowH, fontSize: 18, bold: true, color: BLUE, align: "center", valign: "middle" });
    if (altoTexto(o, wo, so, 1.2, EM_FICHA) > rowH * 1.04) aviso(`el objetivo ${i + 1} no entra ni a 12 pt; acortalo`);
    tb(s, runs(o, { fontSize: so }), { x: X0 + 0.6, y: yy + 0.03, w: wo, h: rowH - 0.06, valign: "middle" });
  });
  y += k * rowH + (k - 1) * gap + 0.16;
  tb(s, "Para quién es", { x: X0, y, w: wl, h: 0.36, fontSize: 16, bold: true, color: ORANGE });
  y += 0.4;
  viñetas(s, M.para_quien, X0, y, wl, BOTTOM + 0.05 - y, { max: 15, min: 12, gap: 6, em: EM_FICHA });
  const im = M.imagen, yi = BAND + 0.22, hi = Math.min(2.9, wr * im.h / im.w);
  imagen(s, im, xr, yi, wr, hi);
  const yc = yi + hi + 0.06;
  tb(s, runs(im.pie, { fontSize: ajustar(im.pie, wr, 0.46, 12, 10, "el pie de la imagen"), color: GRAY }), { x: xr, y: yc, w: wr, h: 0.46, italic: true });
  const yk = yc + 0.56, hk = BOTTOM + 0.05 - yk;
  caja(s, xr, yk, wr, hk, NAVY, { rectRadius: 0.08 });
  tb(s, M.duracion_txt, { x: xr + 0.2, y: yk + 0.1, w: wr - 0.4, h: 0.34, fontSize: 16, bold: true, color: SKY });
  tb(s, runs(M.convocatoria, { fontSize: ajustar(M.convocatoria, wr - 0.4, hk - 0.52, 13, 10, "la convocatoria"), color: WHITE }), { x: xr + 0.2, y: yk + 0.44, w: wr - 0.4, h: hk - 0.52 });
  s.addNotes(limpio(M.notas[0]));

  // ---------- 2 · cómo se trabaja con el agente, requisitos, contenidos y beneficios ----------
  etiqueta = "ficha, diapositiva 2";
  s = nueva("FICHA_DETALLE", "Ficha del taller");
  titulo(s, "Cómo es el taller y qué te llevás");
  const wc = (CW - 0.3) / 2, xR = X0 + wc + 0.3, y2 = TOP - 0.08, hc = H - 0.58 - y2;
  const izq = [
    { rotulo: "Cómo trabajás con el agente" },
    { fill: BLUETINT, partes: [{ sub: "Lo hace el agente (Claude Code con pm-method)" }, { lista: M.agente }] },
    { fill: ORTINT, partes: [{ sub: "Lo decidís vos", color: ORANGE }, { lista: M.persona, colMarca: ORANGE }] },
    { fill: NAVY, partes: [{ prefijo: "Control humano: ", parrafo: M.control }] },
    { fill: LT, partes: [{ sub: "Antes de inscribirte", color: ORANGE }, { lista: M.requisitos, colMarca: ORANGE }, { prefijo: "Modalidad: ", parrafo: M.modalidad }] },
  ];
  const der = [
    { rotulo: "Contenidos" },
    ...M.clases.map(c => ({ fill: LT, partes: [{ sub: `Clase ${c.numero} · ${c.duracion_min} min · ${limpio(c.titulo)}` }, { lista: c.temas }] })),
    { rotulo: "Qué te llevás" },
    { fill: BLUETINT, partes: [{ sub: "Para vos" }, { lista: M.beneficios_vos }, { sub: "Para tu organización" }, { lista: M.beneficios_org }] },
  ];
  const sz2 = tamColumnas(wc, hc, [izq, der]);
  columna(s, X0, y2, wc, hc, izq, "la columna izquierda", sz2);
  columna(s, xR, y2, wc, hc, der, "la columna derecha", sz2);
  s.addNotes(limpio(M.notas[1] || `Cómo es el taller: el agente propone, calcula y avisa; las decisiones las toma una persona. ${M.clases.length} clases: ` +
    M.clases.map(c => `${c.titulo} (${c.duracion_min} min)`).join(" y ") + "."));
}

FICHA ? ficha() : mazo();

(async () => {
  await pres.writeFile({ fileName: SALIDA });
  await applyTheme(SALIDA, THEME);
  AVISOS.forEach(a => process.stderr.write("AVISO: " + a + "\n"));
  process.stdout.write(JSON.stringify({ diapositivas: n, avisos: AVISOS.length }) + "\n");
})().catch(e => { process.stderr.write("ERROR: " + (e && e.stack || e) + "\n"); process.exit(1); });
