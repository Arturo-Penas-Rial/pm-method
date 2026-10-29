// pm-kb · interfaz web (sin dependencias salvo Cytoscape.js para el grafo). Todo texto del índice se inserta como texto,
// nunca como HTML: el único marcado que se interpreta son las marcas «…» del resaltado, convertidas a <mark> después de escapar.
"use strict";

const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...hijos) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (v !== undefined && v !== null && v !== false) e.setAttribute(k, v === true ? "" : v);
  }
  for (const h of hijos.flat()) if (h !== null && h !== undefined) e.append(h.nodeType ? h : document.createTextNode(String(h)));
  return e;
};
const escapar = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const resaltado = (t) => { const s = el("span"); s.innerHTML = escapar(t).replace(/«/g, "<mark>").replace(/»/g, "</mark>"); return s; };

async function api(ruta, params = {}, opciones = {}) {
  const u = new URL(ruta, location.origin);
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, v);
  const r = await fetch(u, { credentials: "same-origin", ...opciones });
  if (r.status === 401) { location.href = "/"; throw new Error("sin sesión"); }
  const d = await r.json();
  if (!r.ok) throw new Error(d.error || `error ${r.status}`);
  return d;
}

const estado = { filtros: {}, ultima: null, historial: [] };
const COLORES = { riesgos: "#c0504d", decisiones: "#2f6db5", cambios: "#8a5cc2", issues: "#d08a1e", acciones: "#2e8b6e",
  lecciones: "#5b8c2a", supuestos: "#b5568c", otro: "#6b7a8f", documento: "#8a8a80", "sin ficha": "#b8b8ae" };
const colorDe = (n) => COLORES[n.registro] || (n.tipo === "sin ficha" ? COLORES["sin ficha"] : n.registro ? COLORES.otro : COLORES.documento);

// ---------------------------------------------------------------- pestañas
function pestana(nombre) {
  for (const b of document.querySelectorAll(".pestanas button")) b.setAttribute("aria-selected", String(b.dataset.pestana === nombre));
  $("#panel-buscar").hidden = nombre !== "buscar";
  $("#panel-preguntar").hidden = nombre !== "preguntar";
  (nombre === "buscar" ? $("#q") : $("#pregunta")).focus();
}

// ---------------------------------------------------------------- buscar
function modo() { return document.querySelector("input[name=modo]:checked").value; }

async function buscar(ev) {
  if (ev) ev.preventDefault();
  const q = $("#q").value.trim();
  if (!q) return;
  const m = modo();
  $("#resumen").textContent = "Buscando…";
  try {
    const r = await api("/api/buscar", { q, proyecto: $("#proyecto").value, estado: m === "aprobado" ? "aprobado" : "",
      historia: m === "historia" ? "1" : "", tipo: estado.filtros.tipo, registro: estado.filtros.registro, k: 10 });
    estado.ultima = r;
    pintarResultados(r);
  } catch (e) { $("#resumen").textContent = ""; $("#resultados").replaceChildren(el("li", { class: "error", text: e.message })); }
}

function pintarResultados(r) {
  const n = r.resultados.length;
  const partes = [`${n} resultado${n === 1 ? "" : "s"}`, `búsqueda ${r.modo}`, `filtro ${r.filtro}`, `~${r.tokens} tokens`];
  if (r.equivalencias.length) partes.push(`equivalencias: ${r.equivalencias.join("; ")}`);
  $("#resumen").textContent = partes.join(" · ");
  pintarFacetas(r.facetas || {});
  const lista = $("#resultados");
  if (!n) { lista.replaceChildren(el("li", { class: "vacio", text: "Sin resultados en los proyectos que podés ver. Probá otras palabras o «Con historia»." })); return; }
  lista.replaceChildren(...r.resultados.map((x) => {
    const chips = [];
    if (x.insignia) chips.push(el("span", { class: "chip" + (x.estado === "aprobado" ? " aprobado" : ""), text: x.insignia }));
    for (const a of x.avisos) chips.push(el("span", { class: "chip " + (a.startsWith("fuente externa") ? "externo" : "aviso"), text: a }));
    if (x.circulacion === "restringida") chips.push(el("span", { class: "chip aviso", text: "circulación restringida" }));
    const titulo = x.titulo.startsWith(x.id) ? x.titulo : `${x.id} · ${x.titulo}`;
    return el("li", { class: "resultado" },
      el("h2", {}, el("button", { type: "button", onclick: () => abrirFicha(x.proyecto, x.id), text: titulo })),
      el("div", { class: "meta" }, chips, el("span", { class: "chip", text: x.proyecto })),
      el("p", { class: "extracto" }, resaltado(x.extracto)),
      el("div", { class: "pie-resultado" },
        el("span", { class: "cita", text: x.cita }),
        el("button", { type: "button", class: "copiar", onclick: (e) => copiar(x.cita, e.target), text: "copiar cita" }),
        x.por_que ? el("span", { text: x.por_que }) : null,
        x.tambien_en.length ? el("span", { text: "también en: " + x.tambien_en.join(", ") }) : null));
  }));
}

function pintarFacetas(f) {
  const cont = $("#facetas");
  cont.replaceChildren();
  const nombres = { tipo: "Tipo", registro: "Registro", estado: "Estado del documento", proyecto: "Proyecto" };
  for (const clave of ["registro", "tipo", "estado", "proyecto"]) {
    const valores = Object.entries(f[clave] || {}).sort((a, b) => b[1] - a[1]);
    if (valores.length < 2 && !estado.filtros[clave]) continue;
    cont.append(el("h3", { text: nombres[clave] }));
    for (const [v, n] of valores) {
      const activa = estado.filtros[clave] === v;
      const etiqueta = v === "—" ? (clave === "registro" ? "documentos" : "sin estado") : v;
      cont.append(el("button", { type: "button", class: activa ? "activa" : "", "aria-pressed": String(activa), onclick: () => {
        if (clave === "proyecto") { $("#proyecto").value = activa ? "" : v; }
        else if (clave === "estado") { return; }
        else estado.filtros[clave] = activa ? undefined : (v === "—" ? undefined : v);
        buscar();
      } }, el("span", { text: etiqueta }), el("span", { class: "n", text: n })));
    }
  }
}

async function copiar(texto, boton) {
  try { await navigator.clipboard.writeText(texto); boton.textContent = "copiada"; setTimeout(() => (boton.textContent = "copiar cita"), 1500); }
  catch { boton.textContent = "no se pudo copiar"; }
}

// ---------------------------------------------------------------- ficha
async function abrirFicha(proyecto, id) {
  const panel = $("#ficha"), cuerpo = $("#ficha-cuerpo");
  panel.hidden = false;
  cuerpo.replaceChildren(el("p", { class: "nota", text: "Cargando…" }));
  try {
    const f = await api("/api/ficha", { id, proyecto });
    const partes = [
      el("p", { class: "nota", text: `${f.proyecto} · ${f.registro ? "registro " + f.registro : f.tipo}` }),
      el("h2", { text: f.titulo }),
      el("div", { class: "meta" }, f.insignia ? el("span", { class: "chip" + (f.estado === "aprobado" ? " aprobado" : ""), text: f.insignia }) : null,
        f.vigente ? null : el("span", { class: "chip aviso", text: "no vigente" }),
        f.confianza === "externo" ? el("span", { class: "chip externo", text: "fuente externa" }) : null),
      el("p", {}, el("span", { class: "cita", text: f.cita }), " ", el("button", { type: "button", class: "copiar", onclick: (e) => copiar(f.cita, e.target), text: "copiar cita" })),
      el("pre", { text: f.texto }),
    ];
    if (f.tambien_en.length) partes.push(el("p", { class: "nota", text: "También en: " + f.tambien_en.join(", ") }));
    partes.push(el("h3", { text: "Relaciones por ids" }));
    if (f.relaciones.length) {
      partes.push(el("div", { id: "grafo", role: "img", "aria-label": "Grafo de relaciones a un salto" }));
      partes.push(leyenda());
      partes.push(el("ul", { class: "lista-rel" }, f.relaciones.map((a) => el("li", {},
        a.sentido === "sale" ? "→ " : "← ",
        a.ficha ? el("button", { type: "button", onclick: () => abrirFicha(f.proyecto, a.id), text: a.id }) : el("span", { text: a.id }),
        ` (${a.tipo}) `, el("span", { class: "nota", text: a.titulo ? a.titulo.slice(0, 90) : "sin ficha" })))));
    } else partes.push(el("p", { class: "nota", text: "Ningún registro lo cita ni él cita otros ids: no se inventan relaciones." }));
    if (f.historia.length) {
      partes.push(el("h3", { text: "Historia de la fila (bitácora)" }));
      partes.push(el("ul", { class: "linea-tiempo" }, f.historia.map((h) => el("li", {},
        `#${h.n} · ${String(h.fecha).slice(0, 10)} · ${h.operacion}${h.por ? " · " + h.por : ""}`,
        Object.keys(h.cambios || {}).length ? el("div", { class: "nota", text: Object.entries(h.cambios).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(" → ") : v}`).join(" · ").slice(0, 300) }) : null))));
    }
    const contVersiones = el("div");
    partes.push(contVersiones);
    cuerpo.replaceChildren(...partes);
    if (f.relaciones.length) dibujarGrafo(f);
    if (!f.registro) pintarVersiones(f, contVersiones);
  } catch (e) { cuerpo.replaceChildren(el("p", { class: "error", text: e.message })); }
}

function leyenda() {
  return el("div", { class: "leyenda" }, ["riesgos", "decisiones", "cambios", "issues", "acciones", "lecciones", "documento", "sin ficha"].map((k) => {
    const i = el("i"); i.style.background = COLORES[k]; return el("span", {}, i, k);
  }));
}

async function dibujarGrafo(f) {
  if (!window.cytoscape) return;
  const r = await api("/api/relaciones", { id: f.id, proyecto: f.proyecto, saltos: 1 });
  const oscuro = matchMedia("(prefers-color-scheme: dark)").matches;
  const corto = (i) => (i.includes("#") ? i.split("/").pop().split("#")[0] : i).slice(0, 26);
  const elementos = r.nodos.map((n) => ({ data: { id: n.id, etiqueta: corto(n.id), nivel: n.id === f.id ? 2 : 1, color: colorDe(n), titulo: n.titulo || "", ficha: n.tipo !== "sin ficha" } }))
    .concat(r.aristas.map((a, i) => ({ data: { id: "a" + i, source: a.origen, target: a.destino, etiqueta: a.tipo } })));
  const cy = window.cytoscape({
    container: $("#grafo"), elements: elementos, wheelSensitivity: 0.3,
    layout: { name: "concentric", concentric: (n) => n.data("nivel"), levelWidth: () => 1, minNodeSpacing: 34, padding: 24, animate: false },
    style: [
      { selector: "node", style: { "background-color": "data(color)", label: "data(etiqueta)", "font-size": 11, color: oscuro ? "#ecece6" : "#1d1d1b",
        "text-valign": "bottom", "text-margin-y": 4, width: 18, height: 18, "border-width": 2, "border-color": oscuro ? "#1d1d1b" : "#ffffff" } },
      { selector: `node[id = "${f.id.replace(/"/g, "")}"]`, style: { width: 28, height: 28, "font-weight": "bold" } },
      { selector: "edge", style: { width: 1.5, "line-color": oscuro ? "#5a5a54" : "#b8b8ae", "target-arrow-shape": "triangle",
        "target-arrow-color": oscuro ? "#5a5a54" : "#b8b8ae", "curve-style": "bezier", label: "data(etiqueta)", "font-size": 9,
        color: oscuro ? "#8d8d84" : "#7a7a72", "text-rotation": "autorotate" } },
    ],
  });
  cy.on("tap", "node", (e) => { const d = e.target.data(); if (d.ficha && d.id !== f.id) abrirFicha(f.proyecto, d.id); });
}

async function pintarVersiones(f, cont) {
  try {
    const v = await api("/api/versiones", { doc: f.doc_id, proyecto: f.proyecto });
    if (v.versiones.length < 2) return;
    const lista = el("ul", { class: "linea-tiempo" }, v.versiones.map((x) => el("li", { class: [x.estado === "aprobado" ? "aprobado" : "", x.vigente ? "vigente" : ""].join(" ") },
      `v${x.version || "—"} · ${x.estado || "sin estado"} · ${x.fecha || "—"}${x.aprobado_por ? " · aprobó " + x.aprobado_por : ""}${x.decision ? " (" + x.decision + ")" : ""}`,
      el("div", { class: "nota", text: `${x.fuente}${x.copia ? " · copia congelada" : ""}${x.vigente ? " · vigente" : ""}${x.aprobada && !x.vigente ? " · aprobada" : ""}` }))));
    const destino = el("div");
    cont.append(el("h3", { text: `Versiones de «${v.titulo}»` }), lista,
      el("button", { type: "button", onclick: () => pintarCambios(v, destino), text: "Comparar la vigente con la anterior" }), destino);
  } catch (e) { cont.append(el("p", { class: "error", text: e.message })); }
}

async function pintarCambios(v, destino) {
  const c = await api("/api/cambios", { doc: v.doc_id, proyecto: v.proyecto });
  if (!c.cambios || !c.cambios.length) { destino.replaceChildren(el("p", { class: "nota", text: c.aviso || "Sin cambios por secciones." })); return; }
  destino.replaceChildren(el("p", { class: "nota", text: `v${c.desde} → v${c.hasta}: ${c.resumen.agregada} agregadas, ${c.resumen.quitada} quitadas, ${c.resumen.modificada} modificadas` }),
    ...c.cambios.map((x) => el("div", { class: "cambio " + x.tipo }, el("strong", { text: `${x.tipo} · ${x.titulo}` }), el("pre", { text: x.resumen }))));
}

// ---------------------------------------------------------------- preguntar
async function preguntar(ev) {
  ev.preventDefault();
  const p = $("#pregunta").value.trim();
  if (!p) return;
  const conv = $("#conversacion");
  conv.append(el("div", { class: "mensaje persona", text: p }));
  $("#pregunta").value = "";
  const espera = el("div", { class: "mensaje", text: "Buscando evidencia…" });
  conv.append(espera);
  try {
    const r = await api("/api/preguntar", {}, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pregunta: p, historial: estado.historial.slice(-6), proyecto: $("#proyecto").value, aprobado: $("#solo-aprobado").checked }) });
    espera.replaceChildren();
    if (r.respuesta) {
      const cuerpo = el("div");
      cuerpo.innerHTML = escapar(r.respuesta).replace(/\n/g, "<br>").replace(/\[(\d+)\]/g, '<a class="ref" href="#f-$1">[$1]</a>');
      espera.append(cuerpo);
      estado.historial.push({ role: "user", content: p }, { role: "assistant", content: r.respuesta });
    } else if (r.fuentes.length) {
      espera.append(el("p", { text: "Esta es la evidencia más relevante (sin modelo de lenguaje configurado, pm-kb no redacta respuestas):" }));
    } else espera.append(el("p", { text: "No encontré evidencia sobre eso en los proyectos que podés ver." }));
    if (r.fuentes.length) espera.append(el("ol", { class: "fuentes" }, r.fuentes.map((f) => el("li", { id: "f-" + f.n },
      el("button", { type: "button", class: "enlace", onclick: () => abrirFicha(f.proyecto || undefined, f.id), text: f.titulo }),
      el("div", { class: "cita", text: f.cita + (f.insignia ? " · " + f.insignia : "") }),
      f.avisos.length ? el("div", { class: "nota", text: f.avisos.join("; ") }) : null,
      r.respuesta ? null : el("div", {}, resaltado(f.texto))))));
    for (const a of r.avisos || []) espera.append(el("p", { class: "nota", text: a }));
    if (r.error) espera.append(el("p", { class: "error", text: r.error }));
    espera.append(el("div", { class: "modo", text: r.modo }));
  } catch (e) { espera.replaceChildren(el("span", { class: "error", text: e.message })); }
  espera.scrollIntoView({ block: "nearest" });
}

// ---------------------------------------------------------------- inicio
async function iniciar() {
  for (const b of document.querySelectorAll(".pestanas button")) b.addEventListener("click", () => pestana(b.dataset.pestana));
  $("#f-buscar").addEventListener("submit", (e) => { estado.filtros = {}; buscar(e); });
  for (const r of document.querySelectorAll("input[name=modo]")) r.addEventListener("change", () => buscar());
  $("#proyecto").addEventListener("change", () => buscar());
  $("#f-preguntar").addEventListener("submit", preguntar);
  $("#cerrar-ficha").addEventListener("click", () => ($("#ficha").hidden = true));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("#ficha").hidden = true; });
  try {
    const e = await api("/api/estado");
    $("#persona").textContent = e.persona;
    for (const p of e.proyectos) $("#proyecto").append(el("option", { value: p.proyecto, text: p.proyecto }));
    $("#pie").textContent = e.proyectos.map((p) => `${p.proyecto}: ${p.vigentes} unidades vigentes, ${p.documentos} documentos, commit ${p.commit}, indexado ${p.indexado_en.slice(0, 16).replace("T", " ")}`).join(" · ")
      + ` · vectores: ${e.proyectos[0] ? e.proyectos[0].modelo_vectores : "—"}`;
    $("#nota-modelo").textContent = e.respuesta_con_modelo
      ? "Las respuestas las redacta el modelo configurado solo con la evidencia citada; verificá las citas."
      : "Sin modelo de lenguaje configurado: «Preguntar» devuelve la evidencia citada. Para respuestas redactadas, ver docs/PM-KB.md §11.3.";
  } catch (e) { $("#pie").textContent = e.message; }
  const q = new URLSearchParams(location.search).get("q");
  if (q) { $("#q").value = q; buscar(); }
  $("#q").focus();
}
document.addEventListener("DOMContentLoaded", iniciar);
