// pm-kb · página de un enlace compartido (/v y /v/ficha/<ref>). El token llega en el fragmento (#), que el navegador no
// envía al servidor ni deja en los registros: la página lo borra de la barra de direcciones y lo canjea con
// POST /v/canje por una sesión (cookie HttpOnly con un id aleatorio, nunca el token). Después dibuja solo el tablero del
// enlace (tablero.js en modo compartido: el actual o la instantánea, filtrado por actor si el enlace lo tiene) o la ficha
// de una de sus tarjetas. Sin pestañas, sin buscar ni preguntar: el servicio rechaza todo lo demás. Todo texto se inserta
// como texto.
"use strict";
(() => {
  const { $, el, api, chip, fecha, copiar } = window.PMKB;
  const S = { info: null, montado: null };
  const vista = () => $("#vista");
  const rutaFicha = (ref) => "/v/ficha/" + encodeURIComponent(ref);
  const enlace = (href, texto, attrs = {}) => el("a", { href, "data-nav": true, ...attrs }, texto);
  const venceTexto = (iso) => { const d = new Date(iso); return Number.isNaN(d.getTime()) ? String(iso || "—") : d.toLocaleString("es", { dateStyle: "medium", timeStyle: "short" }); };
  const SIN_SESION = "Sin sesión: abrí el enlace completo que recibiste (con todo lo que sigue a «#»). Si ya lo abriste, venció o fue revocado: pedí uno nuevo a quien te lo envió.";

  function aviso(texto) {
    $("#vigencia").textContent = "";
    vista().replaceChildren(el("div", { class: "aviso-enlace", role: "alert" }, el("h1", { text: "No se puede abrir el tablero" }), el("p", { text: texto })));
  }

  // ---------------------------------------------------------------- canje del token del fragmento
  async function canjear() {
    if (location.hash.length < 2) return true;
    let tok = location.hash.slice(1);
    try { tok = decodeURIComponent(tok); } catch { /* se manda tal cual */ }
    history.replaceState(null, "", location.pathname + location.search);   // el token no queda en la barra ni en el historial
    let r;
    try {
      r = await fetch("/v/canje", { method: "POST", credentials: "same-origin", cache: "no-store", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: tok }) });
    } catch { aviso("No se pudo contactar al servicio."); return false; }
    const d = await r.json().catch(() => ({}));
    if (!r.ok) { aviso(d.error || `error ${r.status}`); return false; }
    return true;
  }

  function pintarVigencia() {
    const c = S.info;
    const alcance = c.instantanea ? `instantánea «${c.instantanea.etiqueta || c.instantanea.id}»${c.instantanea.fecha ? " del " + c.instantanea.fecha : ""}` : "tablero actual";
    $("#vigencia").textContent = [`solo lectura · vence ${venceTexto(c.vence)}`, alcance, c.actor ? `actor: ${c.actor}` : "",
      c.restringida ? "incluye circulación restringida" : ""].filter(Boolean).join(" · ");
  }

  // ---------------------------------------------------------------- navegación (solo dentro de /v)
  function navegar(url) { history.pushState(null, "", url); dibujar(); }
  document.addEventListener("click", (e) => {
    const a = e.target.closest && e.target.closest("a[data-nav]");
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || a.target) return;
    const u = new URL(a.href, location.href);
    if (u.origin !== location.origin || !(u.pathname === "/v" || u.pathname.startsWith("/v/"))) return;
    e.preventDefault();
    navegar(u.pathname + u.search);
  });
  window.addEventListener("popstate", () => dibujar());

  async function dibujar() {
    if (S.montado) { S.montado.parar(); S.montado = null; }
    window.scrollTo(0, 0);
    const partes = location.pathname.split("/").filter(Boolean);
    try {
      if (partes[1] === "ficha" && partes.length > 2) {
        let ref = partes.slice(2).join("/");
        try { ref = decodeURIComponent(ref); } catch { /* tal cual */ }
        await vistaFicha(ref);
      } else await vistaTablero();
    } catch (e) {
      if (e.estado === 401) aviso(SIN_SESION);
      else vista().replaceChildren(el("p", { class: "error", text: e.message }), el("p", {}, enlace("/v", "Volver al tablero")));
    }
  }

  async function vistaTablero() {
    const c = S.info;
    document.title = `Tablero de ${c.proyecto} · pm-kb`;
    const raiz = el("section", { class: "panel", "aria-label": "Tablero" });
    const q = new URLSearchParams(location.search);
    vista().replaceChildren(el("div", { class: "cabecera-vista" }, el("h1", {}, c.proyecto, c.actor ? el("span", { class: "sub", text: " · " + c.actor }) : null)), raiz);
    S.montado = await window.PMKBTablero.montar(raiz, {
      proyecto: c.proyecto, compartido: true, instantanea: c.alcance === "actual" ? null : c.alcance, rutaFicha, vista: q.get("vista"),
      alCambiar: (cambios) => {
        for (const [k, v] of Object.entries(cambios)) if (k === "vista") { if (v) q.set(k, v); else q.delete(k); }
        history.replaceState(null, "", location.pathname + (q.toString() ? "?" + q : ""));
      } });
  }

  // ---------------------------------------------------------------- ficha (solo las tarjetas del tablero del enlace)
  async function vistaFicha(ref) {
    vista().replaceChildren(el("p", { class: "nota", text: "Cargando la ficha…" }));
    let f;
    try { f = await api("/api/ficha", { id: ref }); }
    catch (e) {
      if (e.estado === 404) {
        vista().replaceChildren(el("p", { class: "error", text: `«${ref}» no está en el tablero de este enlace.` }), el("p", {}, enlace("/v", "Volver al tablero")));
        return;
      }
      throw e;
    }
    const id = f.ref || f.id;
    document.title = `${id} · ${S.info.proyecto} · pm-kb`;
    const partes = [
      el("p", {}, enlace("/v", "← Volver al tablero")),
      el("p", { class: "nota", text: `${f.proyecto} · ${f.registro ? "registro " + f.registro : f.tipo}` + (f.ref && f.ref !== f.id ? ` · id estable ${f.ref}` : "") }),
      el("h1", { class: "titulo-ficha", text: f.titulo.startsWith(id) ? f.titulo : `${id} · ${f.titulo}` }),
      el("div", { class: "meta" }, f.insignia ? chip(f.insignia, f.estado === "aprobado" ? "aprobado" : "") : null,
        f.vigente ? null : chip("no vigente", "aviso"), f.confianza === "externo" ? chip("fuente externa", "externo") : null),
      el("p", {}, el("span", { class: "cita", text: f.cita }), " ", el("button", { type: "button", class: "copiar", onclick: (e) => copiar(f.cita, e.target) }, "copiar cita")),
    ];
    for (const a of f.avisos || []) partes.push(el("p", { class: "aviso-ficha", role: "note", text: a }));
    const u = f.ubicacion;
    if (u) {
      partes.push(el("h2", { text: "Dónde está" }), el("dl", { class: "datos-ficha" },
        el("dt", { text: "Ubicación" }), el("dd", {}, el("span", { class: "cita", text: (u.ruta || "—") + (u.rango ? ":" + u.rango : "") }), " ", chip(u.tipo)),
        u.desde ? [el("dt", { text: "Desde" }), el("dd", { text: fecha(u.desde) })] : null,
        (f.movimientos || []).length ? [el("dt", { text: "Movimientos" }), el("dd", {}, el("ul", { class: "lista-rel" }, f.movimientos.map((m) => el("li", { text: `${m.texto} (${m.motivo})` }))))] : null));
    }
    const b = f.tablero;
    if (b) {
      partes.push(el("h2", { text: "En el tablero" }), el("dl", { class: "datos-ficha" },
        el("dt", { text: "Vista · columna" }), el("dd", { text: `${b.vista} · ${b.columna || b.estado || "—"}` }),
        el("dt", { text: "Descripción" }), el("dd", { text: b.descripcion || "—" }),
        (b.senales || []).length ? [el("dt", { text: "Señales" }), el("dd", {}, b.senales.map((s) => chip(s, "aviso")))] : null,
        el("dt", { text: "Tablero" }), el("dd", { text: b.instantanea ? `instantánea ${b.instantanea} · corte ${b.corte}` : `versión ${b.tablero_version} · corte ${b.corte}` })));
    }
    if (f.texto) partes.push(el("h2", { text: "Contenido" }), el("pre", { class: "texto-ficha", text: f.texto }));
    const rel = f.relacionados || {};
    if (Object.keys(rel).length || f.fuera_del_tablero) {
      partes.push(el("h2", { text: "Relacionados en este tablero" }));
      if (Object.keys(rel).length) partes.push(el("div", { class: "relacionados" }, Object.entries(rel).map(([g, xs]) =>
        el("div", { class: "grupo-rel" }, el("h3", { text: `${g} (${xs.length})` }), el("ul", { class: "lista-rel" }, xs.map((x) => el("li", {},
          enlace(rutaFicha(x.id), x.id), el("span", { class: "nota", text: ` (${x.tipo}${x.sentido === "entra" ? ", lo cita" : ""}) ${x.titulo ? x.titulo.slice(0, 90) : ""}` }))))))));
      if (f.fuera_del_tablero) partes.push(el("p", { class: "nota", text: `${f.fuera_del_tablero} relación(es) con elementos que no están en este tablero: no se muestran.` }));
    }
    if ((f.relaciones || []).length) {
      partes.push(el("h2", { text: "Relaciones" }), el("ul", { class: "lista-rel" }, f.relaciones.map((a) => el("li", {}, a.sentido === "sale" ? "→ " : "← ",
        enlace(rutaFicha(a.id), a.id), ` (${a.tipo}) `, el("span", { class: "nota", text: a.titulo ? a.titulo.slice(0, 90) : "" })))));
    }
    const vs = f.versiones;
    if (vs && (vs.lista || []).length) {
      partes.push(el("h2", { text: `Versiones (vigente v${vs.vigente || "—"} · aprobada v${vs.aprobada || "—"})` }),
        el("ul", { class: "linea-tiempo" }, vs.lista.map((x) => el("li", { class: [x.estado === "aprobado" ? "aprobado" : "", x.vigente ? "vigente" : ""].join(" ") },
          `v${x.version || "—"} · ${x.estado || "sin estado"} · ${x.fecha || "—"}${x.aprobado_por ? " · aprobó " + x.aprobado_por : ""}${x.decision ? " (" + x.decision + ")" : ""}`))));
    }
    if ((f.historia || []).length) {
      partes.push(el("h2", { text: "Historia (bitácora)" }), el("ul", { class: "linea-tiempo" }, f.historia.map((h) => el("li", {},
        `#${h.n} · ${String(h.fecha).slice(0, 10)} · ${h.operacion}${h.por ? " · " + h.por : ""}`,
        h.cambios && Object.keys(h.cambios).length ? el("div", { class: "nota", text: (Array.isArray(h.cambios) ? h.cambios.join(", ")
          : Object.entries(h.cambios).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(" → ") : v}`).join(" · ")).slice(0, 300) }) : null))));
    }
    vista().replaceChildren(el("article", { class: "ficha-pagina" }, partes));
  }

  // ---------------------------------------------------------------- inicio
  async function iniciar() {
    const habia = location.hash.length > 1;
    if (!(await canjear())) return;
    try {
      const e = await api("/api/estado");
      if (!e.compartido) {
        vista().replaceChildren(el("p", {}, "Esta página abre enlaces compartidos; tu sesión es del portal. ", el("a", { href: "/" }, "Ir al portal")));
        return;
      }
      S.info = e.compartido;
    } catch (x) {
      aviso(x.estado === 401 ? (habia ? "El enlace venció o fue revocado: pedí uno nuevo a quien te lo envió." : SIN_SESION) : x.message);
      return;
    }
    pintarVigencia();
    await dibujar();
  }
  document.addEventListener("DOMContentLoaded", iniciar);
})();
