// pm-kb · utilidades comunes del portal (sin dependencias). Todo texto del índice se inserta como texto, nunca como
// HTML. La navegación interna usa enlaces reales (<a href data-nav>) que app.js intercepta para no recargar la página.
"use strict";
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const el = (tag, attrs = {}, ...hijos) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "class") e.className = v;
      else if (k === "text") e.textContent = v;
      else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2), v);
      else if (v !== undefined && v !== null && v !== false) e.setAttribute(k, v === true ? "" : v);
    }
    for (const h of hijos.flat(Infinity)) if (h !== null && h !== undefined && h !== false) e.append(h.nodeType ? h : document.createTextNode(String(h)));
    return e;
  };
  const escapar = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  // Único marcado que se interpreta: las marcas «…» del resaltado, convertidas a <mark> después de escapar.
  const resaltado = (t) => { const s = el("span"); s.innerHTML = escapar(t).replace(/«/g, "<mark>").replace(/»/g, "</mark>"); return s; };

  class ErrorApi extends Error { constructor(m, estado, datos) { super(m); this.estado = estado; this.datos = datos || {}; } }

  async function api(ruta, params = {}, opciones = {}) {
    const u = new URL(ruta, location.origin);
    for (const [k, v] of Object.entries(params || {})) if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, v);
    const r = await fetch(u, { credentials: "same-origin", cache: "no-store", ...opciones });
    // Sin sesión: el portal vuelve al ingreso; la página de un enlace compartido (/v) muestra su propio aviso.
    if (r.status === 401) { if (!document.body.classList.contains("compartido")) location.href = "/"; throw new ErrorApi("sin sesión", 401); }
    let d = {};
    try { d = await r.json(); } catch { d = {}; }
    if (!r.ok) throw new ErrorApi(d.error || `error ${r.status}`, r.status, d);
    return d;
  }

  const rutaProyecto = (p, resto = "") => "/p/" + encodeURIComponent(p) + (resto ? "/" + resto : "");
  const rutaFicha = (p, ref) => rutaProyecto(p, "ficha/" + encodeURIComponent(ref));
  const enlace = (href, texto, attrs = {}) => el("a", { href, "data-nav": true, ...attrs }, texto);
  const enlaceFicha = (p, ref, texto, attrs = {}) => enlace(rutaFicha(p, ref), texto ?? ref, attrs);
  const chip = (texto, clase = "") => el("span", { class: "chip " + clase, text: texto });
  const fecha = (iso) => String(iso || "").slice(0, 16).replace("T", " ");
  const dias = (n) => (n === null || n === undefined ? "" : n < 0 ? `venció hace ${-n} día${n === -1 ? "" : "s"}` : n === 0 ? "vence hoy" : `faltan ${n} día${n === 1 ? "" : "s"}`);

  async function copiar(texto, boton, etiqueta = "copiar cita") {
    try { await navigator.clipboard.writeText(texto); boton.textContent = "copiada"; setTimeout(() => (boton.textContent = etiqueta), 1500); }
    catch { boton.textContent = "no se pudo copiar"; }
  }

  window.PMKB = { $, $$, el, escapar, resaltado, api, ErrorApi, rutaProyecto, rutaFicha, enlace, enlaceFicha, chip, fecha, dias, copiar };
})();
