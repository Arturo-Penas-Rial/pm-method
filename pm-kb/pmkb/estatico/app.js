// pm-kb · portal web: cartera, proyecto (Tableros, Buscar, Artefactos, Preguntar) y ficha ampliada por id estable.
// Sin dependencias salvo Cytoscape.js para el grafo de la ficha. Rutas (todas sirven esta misma página):
//   /                          cartera: una fila por proyecto visible, primero lo que pide acción
//   /p/<proyecto>[/tableros|/buscar|/artefactos|/preguntar]   proyecto con pestañas
//   /p/<proyecto>/ficha/<ref>  ficha ampliada (destino de toda tarjeta: enlace por id, nunca por ruta)
//   /buscar · /preguntar       en todos los proyectos visibles
// <proyecto> acepta el nombre de la instancia en pm-kb o el `proyecto` de estado.json (el que usan los HTML del tablero).
"use strict";
(() => {
  const { $, $$, el, resaltado, api, rutaProyecto, rutaFicha, enlace, enlaceFicha, chip, fecha, dias, copiar } = window.PMKB;
  const S = { estado: null, montado: null, historial: [] };
  const PESTANAS = [["tableros", "Tableros"], ["buscar", "Buscar"], ["artefactos", "Artefactos"], ["preguntar", "Preguntar"]];
  const COLORES = { riesgos: "#c0504d", decisiones: "#2f6db5", cambios: "#8a5cc2", issues: "#d08a1e", acciones: "#2e8b6e",
    lecciones: "#5b8c2a", supuestos: "#b5568c", otro: "#6b7a8f", documento: "#8a8a80", "sin ficha": "#b8b8ae" };
  const colorDe = (n) => COLORES[n.registro] || (n.tipo === "sin ficha" ? COLORES["sin ficha"] : n.registro ? COLORES.otro : COLORES.documento);
  const vista = () => $("#vista");
  const anunciar = (t) => { $("#anuncio").textContent = t; };

  // ---------------------------------------------------------------- navegación
  function navegar(url, reemplazar = false) {
    if (reemplazar) history.replaceState(null, "", url); else history.pushState(null, "", url);
    dibujar();
  }
  document.addEventListener("click", (e) => {
    const a = e.target.closest && e.target.closest("a[data-nav]");
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || a.target) return;
    const u = new URL(a.href, location.href);
    if (u.origin !== location.origin) return;
    e.preventDefault();
    navegar(u.pathname + u.search);
  });
  window.addEventListener("popstate", () => dibujar());

  function ruta() {
    const partes = location.pathname.split("/").filter(Boolean).map((x) => { try { return decodeURIComponent(x); } catch { return x; } });
    const q = new URLSearchParams(location.search);
    if (!partes.length) return { vista: "cartera", q };
    if (partes[0] === "buscar") return { vista: "buscar", q };
    if (partes[0] === "preguntar") return { vista: "preguntar", q };
    if (partes[0] === "p" && partes[1]) {
      if (partes[2] === "ficha" && partes.length > 3) return { vista: "ficha", proyecto: partes[1], ref: partes.slice(3).join("/"), q };
      return { vista: "proyecto", proyecto: partes[1], pestana: PESTANAS.some((p) => p[0] === partes[2]) ? partes[2] : "tableros", q };
    }
    return { vista: "cartera", q };
  }

  function migas(items) {
    $("#migas").replaceChildren(el("ol", {}, [el("li", {}, items.length ? enlace("/", "Cartera") : el("span", { "aria-current": "page", text: "Cartera" }))].concat(items.map((x, i) =>
      el("li", {}, x.href && i < items.length - 1 ? enlace(x.href, x.texto) : el("span", { "aria-current": "page", text: x.texto }))))));
  }

  async function dibujar() {
    if (S.montado) { S.montado.parar(); S.montado = null; }
    const r = ruta();
    vista().classList.toggle("ancho", r.vista === "proyecto" && r.pestana === "tableros");
    window.scrollTo(0, 0);
    try {
      if (r.vista === "cartera") await vistaCartera();
      else if (r.vista === "buscar") vistaBuscarGlobal(r.q);
      else if (r.vista === "preguntar") vistaPreguntarGlobal();
      else if (r.vista === "ficha") await vistaFicha(r.proyecto, r.ref);
      else await vistaProyecto(r.proyecto, r.pestana, r.q);
    } catch (e) {
      vista().replaceChildren(el("p", { class: "error", text: e.message }), el("p", {}, enlace("/", "Volver a la cartera")));
    }
  }

  // ---------------------------------------------------------------- cartera
  async function vistaCartera() {
    migas([]);
    document.title = "Cartera · pm-kb";
    vista().replaceChildren(el("p", { class: "nota", text: "Cargando la cartera…" }));
    const c = await api("/api/cartera");
    const filas = c.proyectos.map(filaCartera);
    vista().replaceChildren(
      el("div", { class: "cabecera-vista" }, el("h1", { text: "Cartera" }),
        el("p", { class: "nota", text: `${c.proyectos.length} proyecto(s) que podés ver. Primero, lo que pide acción: excepción abierta, bloqueos de la próxima puerta y decisiones pendientes.` })),
      filas.length ? el("ol", { class: "cartera" }, filas) : el("p", { class: "vacio", text: "Tu token no ve ningún proyecto indexado." }));
  }

  function filaCartera(p) {
    const s = p.resumen;
    const titulo = el("h2", {}, enlace(rutaProyecto(p.proyecto), p.proyecto), s && s.proyecto_pm && s.proyecto_pm !== p.proyecto ? el("span", { class: "sub", text: " · " + s.proyecto_pm }) : null);
    if (!s) {
      return el("li", { class: "fila-cartera sin-tablero" }, titulo,
        el("p", { class: "nota" }, "Sin tablero: no es un proyecto de pm-method o todavía no se publicó. ", enlace(rutaProyecto(p.proyecto, "buscar"), "Buscar en este proyecto")),
        el("p", { class: "nota", text: `${p.vigentes} unidades vigentes · indexado ${fecha(p.indexado_en)}` }));
    }
    const a = s.atencion, px = s.proxima;
    const pide = s.excepcion || (px && px.bloqueos) || a.decidir;
    return el("li", { class: "fila-cartera" + (pide ? " pide-accion" : "") },
      el("div", { class: "fila-cab" }, titulo, s.excepcion ? chip("■ excepción " + s.excepcion, "mal") : null),
      el("dl", { class: "fila-datos" },
        el("div", {}, el("dt", { text: "Fase · proceso" }), el("dd", { text: `${s.fase || "—"} · ${s.proceso || "—"}` })),
        el("div", {}, el("dt", { text: "Etapa" }), el("dd", {}, `${s.etapa ?? "—"}${s.nombre_etapa ? " · " + s.nombre_etapa : ""}`,
          s.fin_previsto ? el("span", { class: "sub " + (s.dias_restantes !== null && s.dias_restantes < 0 ? "tb-mal" : ""), text: ` · ${dias(s.dias_restantes)} (${s.fin_previsto})` }) : null)),
        el("div", {}, el("dt", { text: "Próxima puerta" }), el("dd", {},
          px ? [enlaceFicha(p.proyecto, px.ref, px.tipo), " ",
            px.bloqueos ? chip(`■ ${px.bloqueos} bloqueo(s)`, "mal") : chip("✓ sin bloqueos", "aprobado"),
            px.condiciones ? chip(`▲ ${px.condiciones} condición(es)`, "aviso") : null,
            (px.hallazgos || []).filter((h) => h.severidad !== "aviso").length ? el("span", { class: "sub", text: " " + px.hallazgos.filter((h) => h.severidad !== "aviso").map((h) => h.id).join(", ") }) : null]
            : "—",
          (s.condiciones_abiertas || []).length ? el("div", { class: "sub" }, "condiciones abiertas: ",
            s.condiciones_abiertas.map((r, i) => [i ? ", " : "", enlaceFicha(p.proyecto, r)])) : null)),
        el("div", {}, el("dt", { text: "Atención" }), el("dd", {}, [["decidir", "Decidir"], ["escalar", "Escalar"], ["desbloquear", "Desbloquear"], ["vigilar", "Vigilar"]]
          .map(([g, n]) => chip(`${n} ${a[g]}`, "tb-g-" + g + (a[g] ? "" : " tb-cero"))))),
        el("div", {}, el("dt", { text: "Tablero" }), el("dd", {}, enlace(rutaProyecto(p.proyecto, "tableros"), `versión ${p.version}`),
          el("span", { class: "sub", text: ` · corte ${s.corte} · publicado ${fecha(p.generado_en)}` + (s.avisos ? ` · ${s.avisos} aviso(s)` : "") })))));
  }

  // ---------------------------------------------------------------- proyecto
  async function vistaProyecto(p, pestana, q) {
    const h = await api("/api/tablero/historial", { proyecto: p });
    if (h.proyecto !== p) { navegar(rutaProyecto(h.proyecto, pestana === "tableros" ? "" : pestana) + location.search, true); return; }
    S.historial = h.instantaneas || [];
    document.title = `${p} · pm-kb`;
    migas([{ href: rutaProyecto(p), texto: p }, { texto: PESTANAS.find((x) => x[0] === pestana)[1] }]);
    const panel = el("section", { id: "panel-" + pestana, class: "panel", role: "tabpanel", "aria-labelledby": "tab-" + pestana });
    vista().replaceChildren(
      el("div", { class: "cabecera-vista" }, el("h1", {}, p, h.nombre && h.nombre !== p ? el("span", { class: "sub", text: " · " + h.nombre }) : null)),
      el("nav", { class: "pestanas", role: "tablist", "aria-label": "Secciones del proyecto" }, PESTANAS.map(([id, n]) =>
        el("a", { id: "tab-" + id, role: "tab", href: rutaProyecto(p, id === "tableros" ? "" : id), "data-nav": true, "aria-selected": String(id === pestana) }, n))),
      panel);
    if (pestana === "tableros") {
      if (!h.pm_method) { panel.replaceChildren(el("p", { class: "nota", text: "Este proyecto no es de pm-method (sin estado.json): no tiene tablero. Usá Buscar o Preguntar." })); return; }
      const qs = new URLSearchParams(location.search);
      S.montado = await window.PMKBTablero.montar(panel, {
        proyecto: p, puedeActualizar: !!(S.estado && S.estado.puede_actualizar), vista: q.get("vista"), instantanea: q.get("instantanea"), comparar: q.get("comparar"),
        actor: q.get("actor"),
        alCambiar: (cambios) => {
          for (const [k, v] of Object.entries(cambios)) { if (v) qs.set(k, v); else qs.delete(k); }
          history.replaceState(null, "", location.pathname + (qs.toString() ? "?" + qs : ""));
        } });
    } else if (pestana === "buscar") panelBuscar(panel, p, q);
    else if (pestana === "artefactos") await panelArtefactos(panel, p, h);
    else panelPreguntar(panel, p);
  }

  // ---------------------------------------------------------------- buscar
  function panelBuscar(panel, proyecto, q) {
    const estado = { filtros: {} };
    const sel = proyecto ? null : el("select", { id: "proyecto", "aria-label": "Proyecto" }, el("option", { value: "" }, "Todos los proyectos"),
      ((S.estado || {}).proyectos || []).map((x) => el("option", { value: x.proyecto }, x.proyecto)));
    const entrada = el("input", { id: "q", type: "search", autocomplete: "off", required: true, "aria-label": "Consulta",
      placeholder: "Preguntá o escribí palabras clave: ¿por qué se rechazó la compra de licencias?, R-003, caso de negocio…" });
    const modo = (v, n, t, c) => el("label", { title: t }, el("input", { type: "radio", name: "modo", value: v, ...(c ? { checked: true } : {}), onchange: () => buscar() }), " " + n);
    const resumen = el("div", { class: "resumen", "aria-live": "polite" }), facetas = el("aside", { class: "facetas", "aria-label": "Filtros" });
    const lista = el("ol", { class: "resultados" });
    const form = el("form", { class: "consulta", onsubmit: (e) => { e.preventDefault(); estado.filtros = {}; buscar(); } }, entrada, sel,
      el("button", { type: "submit" }, "Buscar"),
      el("fieldset", { class: "modo" }, el("legend", { class: "oculto", text: "Versiones" }),
        modo("vigente", "Vigente", "La última versión de cada documento, con aviso si hay una aprobada anterior", true),
        modo("aprobado", "Aprobado", "Solo la última versión aprobada (consultas de gobierno)"),
        modo("historia", "Con historia", "Todas las versiones, marcadas")));
    if (sel) sel.addEventListener("change", () => buscar());
    panel.replaceChildren(form, resumen, el("div", { class: "cuerpo" }, facetas, lista));

    async function buscar() {
      const texto = entrada.value.trim();
      if (!texto) return;
      const m = $("input[name=modo]:checked", form).value;
      resumen.textContent = "Buscando…";
      try {
        const r = await api("/api/buscar", { q: texto, proyecto: proyecto || (sel && sel.value), estado: m === "aprobado" ? "aprobado" : "",
          historia: m === "historia" ? "1" : "", tipo: estado.filtros.tipo, registro: estado.filtros.registro, k: 10 });
        pintar(r);
        const u = new URL(location.href); u.searchParams.set("q", texto); history.replaceState(null, "", u.pathname + u.search);
      } catch (e) { resumen.textContent = ""; lista.replaceChildren(el("li", { class: "error", text: e.message })); }
    }

    function pintar(r) {
      const n = r.resultados.length;
      const partes = [`${n} resultado${n === 1 ? "" : "s"}`, `búsqueda ${r.modo}`, `filtro ${r.filtro}`, `~${r.tokens} tokens`];
      if (r.equivalencias.length) partes.push(`equivalencias: ${r.equivalencias.join("; ")}`);
      resumen.textContent = partes.join(" · ");
      pintarFacetas(r.facetas || {});
      if (!n) { lista.replaceChildren(el("li", { class: "vacio", text: "Sin resultados en los proyectos que podés ver. Probá otras palabras o «Con historia»." })); return; }
      lista.replaceChildren(...r.resultados.map((x) => {
        const chips = [];
        if (x.insignia) chips.push(chip(x.insignia, x.estado === "aprobado" ? "aprobado" : ""));
        for (const a of x.avisos) chips.push(chip(a, a.startsWith("fuente externa") ? "externo" : "aviso"));
        if (x.circulacion === "restringida") chips.push(chip("circulación restringida", "aviso"));
        const titulo = x.titulo.startsWith(x.id) ? x.titulo : `${x.id} · ${x.titulo}`;
        return el("li", { class: "resultado" },
          el("h2", {}, enlaceFicha(x.proyecto, x.id, titulo)),
          el("div", { class: "meta" }, chips, proyecto ? null : chip(x.proyecto)),
          el("p", { class: "extracto" }, resaltado(x.extracto)),
          el("div", { class: "pie-resultado" }, el("span", { class: "cita", text: x.cita }),
            el("button", { type: "button", class: "copiar", onclick: (e) => copiar(x.cita, e.target) }, "copiar cita"),
            x.por_que ? el("span", { text: x.por_que }) : null,
            x.tambien_en.length ? el("span", { text: "también en: " + x.tambien_en.join(", ") }) : null));
      }));
    }

    function pintarFacetas(f) {
      facetas.replaceChildren();
      const nombres = { tipo: "Tipo", registro: "Registro", estado: "Estado del documento", proyecto: "Proyecto" };
      for (const clave of ["registro", "tipo", "estado", "proyecto"]) {
        if (clave === "proyecto" && proyecto) continue;
        const valores = Object.entries(f[clave] || {}).sort((a, b) => b[1] - a[1]);
        if (valores.length < 2 && !estado.filtros[clave]) continue;
        facetas.append(el("h3", { text: nombres[clave] }));
        for (const [v, n] of valores) {
          const activa = estado.filtros[clave] === v;
          const etiqueta = v === "—" ? (clave === "registro" ? "documentos" : "sin estado") : v;
          facetas.append(el("button", { type: "button", class: activa ? "activa" : "", "aria-pressed": String(activa), onclick: () => {
            if (clave === "proyecto") { sel.value = activa ? "" : v; }
            else if (clave === "estado") { return; }
            else estado.filtros[clave] = activa ? undefined : (v === "—" ? undefined : v);
            buscar();
          } }, el("span", { text: etiqueta }), el("span", { class: "n", text: n })));
        }
      }
    }
    const inicial = q && q.get("q");
    if (inicial) { entrada.value = inicial; buscar(); }
    entrada.focus();
  }

  function vistaBuscarGlobal(q) {
    migas([{ texto: "Buscar en todo" }]);
    document.title = "Buscar · pm-kb";
    const panel = el("section", { class: "panel" });
    vista().replaceChildren(el("div", { class: "cabecera-vista" }, el("h1", { text: "Buscar en todos los proyectos" }),
      el("p", { class: "nota" }, "También: ", enlace("/preguntar", "Preguntar"), " con la evidencia citada.")), panel);
    panelBuscar(panel, null, q);
  }

  // ---------------------------------------------------------------- preguntar
  function panelPreguntar(panel, proyecto) {
    const historial = [];
    const conv = el("div", { class: "conversacion", "aria-live": "polite" });
    const entrada = el("input", { id: "pregunta", type: "text", autocomplete: "off", required: true, "aria-label": "Pregunta",
      placeholder: "¿Quién aprobó el caso de negocio y qué cambió en la última versión?" });
    const solo = el("input", { type: "checkbox", id: "solo-aprobado" });
    const nota = el("p", { class: "nota", text: S.estado && S.estado.respuesta_con_modelo
      ? "Las respuestas las redacta el modelo configurado solo con la evidencia citada; verificá las citas."
      : "Sin modelo de lenguaje configurado: «Preguntar» devuelve la evidencia citada (docs/PM-KB.md §11.3)." });
    panel.replaceChildren(conv, el("form", { class: "consulta", onsubmit: preguntar }, entrada, el("label", { class: "chico" }, solo, " solo aprobado"),
      el("button", { type: "submit" }, "Preguntar")), nota);
    entrada.focus();

    async function preguntar(ev) {
      ev.preventDefault();
      const p = entrada.value.trim();
      if (!p) return;
      conv.append(el("div", { class: "mensaje persona", text: p }));
      entrada.value = "";
      const espera = el("div", { class: "mensaje", text: "Buscando evidencia…" });
      conv.append(espera);
      try {
        const r = await api("/api/preguntar", {}, { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pregunta: p, historial: historial.slice(-6), proyecto: proyecto || "", aprobado: solo.checked }) });
        espera.replaceChildren();
        if (r.respuesta) {
          const cuerpo = el("div");
          for (const [i, linea] of r.respuesta.split("\n").entries()) {
            if (i) cuerpo.append(el("br"));
            for (const parte of linea.split(/(\[\d+\])/)) {
              const m = parte.match(/^\[(\d+)\]$/);
              cuerpo.append(m ? el("a", { class: "ref", href: "#f-" + m[1], text: parte }) : parte);
            }
          }
          espera.append(cuerpo);
          historial.push({ role: "user", content: p }, { role: "assistant", content: r.respuesta });
        } else if (r.fuentes.length) espera.append(el("p", { text: "Esta es la evidencia más relevante (sin modelo de lenguaje configurado, pm-kb no redacta respuestas):" }));
        else espera.append(el("p", { text: "No encontré evidencia sobre eso en los proyectos que podés ver." }));
        if (r.fuentes.length) espera.append(el("ol", { class: "fuentes" }, r.fuentes.map((f) => el("li", { id: "f-" + f.n },
          enlaceFicha(f.proyecto || proyecto || "", f.id, f.titulo),
          el("div", { class: "cita", text: f.cita + (f.insignia ? " · " + f.insignia : "") }),
          f.avisos.length ? el("div", { class: "nota", text: f.avisos.join("; ") }) : null,
          r.respuesta ? null : el("div", {}, resaltado(f.texto))))));
        for (const a of r.avisos || []) espera.append(el("p", { class: "nota", text: a }));
        if (r.error) espera.append(el("p", { class: "error", text: r.error }));
        espera.append(el("div", { class: "modo", text: r.modo }));
      } catch (e) { espera.replaceChildren(el("span", { class: "error", text: e.message })); }
      espera.scrollIntoView({ block: "nearest" });
    }
  }

  function vistaPreguntarGlobal() {
    migas([{ texto: "Preguntar" }]);
    document.title = "Preguntar · pm-kb";
    const panel = el("section", { class: "panel" });
    vista().replaceChildren(el("div", { class: "cabecera-vista" }, el("h1", { text: "Preguntar sobre todos los proyectos" })), panel);
    panelPreguntar(panel, null);
  }

  // ---------------------------------------------------------------- artefactos y documentos
  const ESTADO_ART = { borrador: "aviso", "en-revision": "aviso", aprobado: "aprobado", obsoleto: "", vigente: "aprobado" };
  async function panelArtefactos(panel, p, h) {
    panel.replaceChildren(el("p", { class: "nota", text: "Cargando los artefactos…" }));
    const [a, d] = await Promise.all([api("/api/artefactos", { proyecto: p }).catch((e) => ({ error: e.message })),
      api("/api/documentos", { proyecto: p }).catch((e) => ({ error: e.message }))]);
    const partes = [el("p", { class: "nota", text: "Publicar es mostrar: la versión vigente y la aprobada de cada artefacto, desde la carpeta del proyecto, "
      + "con la marca de borrador cuando corresponde. La aprobación sigue en pm-method (estado.py aprobar)." })];
    if (a.error) partes.push(el("p", { class: "error", text: a.error }));
    else {
      partes.push(el("p", { class: "nota", text: `Tablero versión ${a.version}, corte ${a.corte}.` }));
      for (const g of a.grupos) {
        partes.push(el("h2", { class: "grupo-art", text: `${g.nombre} (${g.claves.length})` }));
        partes.push(g.claves.length ? el("ul", { class: "artefactos" }, g.claves.map((k) => tarjetaArtefacto(p, a.elementos[k]))) : el("p", { class: "nota", text: "—" }));
      }
    }
    partes.push(el("h2", { class: "grupo-art", id: "documentos", text: "Documentos" }));
    partes.push(el("p", { class: "nota", text: "HTML del proyecto (archify, diagram-design, visual-explainer y los de pm-method), en un marco aislado: "
      + "sin acceso a tu sesión ni al portal, sin red. Se pueden descargar; de los diagramas, también el SVG o el PNG si existen." }));
    if (d.error) partes.push(el("p", { class: "error", text: d.error }));
    else if (!d.accesible) partes.push(el("p", { class: "nota", text: "La carpeta indexada no está accesible desde el servicio: no se pueden mostrar los documentos." }));
    else if (!d.documentos.length) partes.push(el("p", { class: "nota", text: "Sin documentos HTML en este proyecto." }));
    else {
      const visor = el("div", { class: "visor", hidden: true });
      partes.push(el("ul", { class: "documentos" }, d.documentos.map((x) => filaDocumento(p, x, visor))), visor);
    }
    panel.replaceChildren(...partes);
  }

  function tarjetaArtefacto(p, x) {
    const marcas = [chip(x.estado || "sin estado", ESTADO_ART[x.estado] || "")];
    if (x.borrador) marcas.push(chip("BORRADOR", "aviso"));
    if (x.version) marcas.push(chip("v" + x.version));
    if (x.indice && x.indice.aprobada && x.indice.aprobada !== x.indice.vigente) marcas.push(chip(`aprobada v${x.indice.aprobada}`, "aprobado"));
    for (const s of x.senales || []) marcas.push(chip({ "fuente-no-encontrada": "fuente no encontrada", "aprobada-anterior": "hay una versión aprobada anterior" }[s] || s, s === "fuente-no-encontrada" ? "mal" : "aviso"));
    if (x.solo_instantaneas) marcas.push(chip("solo en instantáneas"));
    const detalles = [];
    if ((x.ciclos || []).length) detalles.push(el("details", { class: "ciclos" }, el("summary", { text: `Ciclos anteriores (${x.ciclos.length} instantánea(s))` }),
      el("ul", { class: "linea-tiempo" }, x.ciclos.map((c) => el("li", {}, enlace(rutaProyecto(p) + "?instantanea=" + encodeURIComponent(c.instantanea), c.etiqueta || c.instantanea),
        el("span", { class: "nota", text: ` · ${c.fecha} · ${c.estado || "—"}${c.version ? " v" + c.version : ""}` }))))));
    if ((x.historial || []).length) detalles.push(el("details", { class: "ciclos" }, el("summary", { text: `Copias congeladas en 00-direccion/historial/ (${x.historial.length})` }),
      el("ul", { class: "linea-tiempo" }, x.historial.map((c) => el("li", { class: c.estado === "aprobado" ? "aprobado" : "" },
        `v${c.version || "—"} · ${c.estado || "—"} · ${c.fecha || "—"}` + (c.aprobado_por ? ` · aprobó ${c.aprobado_por}` : ""), el("div", { class: "cita", text: c.fuente }))))));
    return el("li", { class: "artefacto" },
      el("h3", {}, enlaceFicha(p, x.ref, x.nombre && x.nombre !== x.ref ? `${x.ref} · ${x.nombre}` : x.ref)),
      el("div", { class: "meta" }, marcas),
      el("p", { class: "nota", text: [x.fecha, x.aprobado_por ? "aprobó " + x.aprobado_por : "", x.ruta || ""].filter(Boolean).join(" · ") }),
      detalles);
  }

  const rutaArchivo = (p, f) => "/archivo/" + encodeURIComponent(p) + "/" + f.split("/").map(encodeURIComponent).join("/");
  const tam = (b) => (b > 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1024))} KB`);
  function filaDocumento(p, x, visor) {
    const motor = { archify: "archify", "diagram-design": "diagram-design", "visual-explainer": "visual-explainer", "pm-method": "pm-method", html: "HTML" }[x.motor] || "HTML";
    return el("li", { class: "documento" },
      el("div", { class: "doc-cab" }, chip(motor, "motor"), el("strong", { text: x.titulo || x.fuente }), x.estado ? chip(x.estado, ESTADO_ART[x.estado] || "") : null,
        x.circulacion === "restringida" ? chip("circulación restringida", "aviso") : null),
      el("div", { class: "cita", text: x.fuente + (x.existe ? ` · ${tam(x.bytes)}` : " · no encontrado en la carpeta") }),
      x.existe ? el("div", { class: "doc-acciones" },
        el("button", { type: "button", onclick: () => abrirDocumento(p, x, visor) }, "Ver aquí"),
        el("a", { href: rutaArchivo(p, x.fuente) + "?descargar=1", class: "boton-sec" }, "Descargar"),
        (x.exportaciones || []).map((f) => el("a", { href: rutaArchivo(p, f) + "?descargar=1", class: "boton-sec" }, f.endsWith(".svg") ? "SVG" : "PNG")),
        x.doc_id ? enlaceFicha(p, x.clave || x.doc_id, "Ficha", { class: "boton-sec" }) : null) : null);
  }

  function abrirDocumento(p, x, visor) {
    // Marco aislado: sandbox sin allow-same-origin (origen opaco: sin cookies ni acceso al portal); scripts solo si el
    // documento los necesita para dibujarse (el servicio repite la restricción con su propia CSP `sandbox`).
    const marco = el("iframe", { src: rutaArchivo(p, x.fuente), title: `Documento: ${x.titulo || x.fuente}`, sandbox: x.scripts ? "allow-scripts" : "",
      referrerpolicy: "no-referrer", loading: "lazy", class: "marco-doc" });
    visor.hidden = false;
    visor.replaceChildren(el("div", { class: "visor-cab" }, el("strong", { text: x.titulo || x.fuente }),
      el("span", { class: "nota", text: x.scripts ? " · marco aislado con scripts del documento (sin acceso al portal)" : " · marco aislado sin scripts" }),
      el("button", { type: "button", class: "enlace", onclick: () => { visor.hidden = true; visor.replaceChildren(); } }, "Cerrar")), marco);
    visor.scrollIntoView({ block: "start" });
  }

  // ---------------------------------------------------------------- ficha ampliada
  const VISTA_TABLERO = { ciclo: "ciclo", atencion: "atencion", productos: "entrega", cambios: "entrega", issues: "entrega", acciones: "entrega" };
  async function vistaFicha(p, ref) {
    vista().replaceChildren(el("p", { class: "nota", text: "Cargando la ficha…" }));
    const f = await api("/api/ficha", { id: ref, proyecto: p });
    if (f.proyecto !== p) { navegar(rutaFicha(f.proyecto, ref), true); return; }
    document.title = `${f.ref || f.id} · ${f.proyecto} · pm-kb`;
    migas([{ href: rutaProyecto(f.proyecto), texto: f.proyecto }, { texto: "Ficha " + (f.ref || f.id) }]);
    const partes = [
      el("p", { class: "nota", text: `${f.proyecto} · ${f.registro ? "registro " + f.registro : f.tipo}` + (f.ref && f.ref !== f.id ? ` · id estable ${f.ref}` : "") }),
      el("h1", { class: "titulo-ficha", text: f.titulo.startsWith(f.ref || f.id) ? f.titulo : `${f.ref || f.id} · ${f.titulo}` }),
      el("div", { class: "meta" }, f.insignia ? chip(f.insignia, f.estado === "aprobado" ? "aprobado" : "") : null,
        f.vigente ? null : chip("no vigente", "aviso"), f.confianza === "externo" ? chip("fuente externa", "externo") : null),
      el("p", {}, el("span", { class: "cita", text: f.cita }), " ", el("button", { type: "button", class: "copiar", onclick: (e) => copiar(f.cita, e.target) }, "copiar cita")),
    ];
    for (const a of f.avisos || []) partes.push(el("p", { class: "aviso-ficha", role: "note", text: a }));
    const u = f.ubicacion;
    if (u) {
      partes.push(el("h2", { text: "Dónde está" }), el("dl", { class: "datos-ficha" },
        el("dt", { text: "Ubicación vigente" }), el("dd", {}, el("span", { class: "cita", text: (u.ruta || "—") + (u.rango ? ":" + u.rango : "") }), chip(u.tipo), u.estado && u.estado !== "vigente" ? chip(u.estado, "aviso") : null),
        u.declarada && u.declarada !== u.ruta ? [el("dt", { text: "Declarada en estado.json" }), el("dd", { class: "cita", text: u.declarada })] : null,
        u.lista ? [el("dt", { text: "Verificación" }), el("dd", { class: "cita", text: u.lista })] : null,
        u.desde ? [el("dt", { text: "Desde" }), el("dd", { text: fecha(u.desde) })] : null,
        (f.movimientos || []).length ? [el("dt", { text: "Movimientos" }), el("dd", {}, el("ul", { class: "lista-rel" }, f.movimientos.map((m) => el("li", { text: `${m.texto} (${m.motivo})` }))))] : null));
    }
    const b = f.tablero;
    if (b) {
      const v = VISTA_TABLERO[b.vista];
      partes.push(el("h2", { text: "En el tablero" }), el("dl", { class: "datos-ficha" },
        el("dt", { text: "Vista · columna" }), el("dd", {}, `${b.vista} · ${b.columna || "—"}`, " ",
          v ? enlace(rutaProyecto(f.proyecto) + "?vista=" + v, "ver en el tablero") : enlace(rutaProyecto(f.proyecto, "artefactos"), "ver en Artefactos")),
        el("dt", { text: "Descripción" }), el("dd", { text: b.descripcion || "—" }),
        (b.senales || []).length ? [el("dt", { text: "Señales" }), el("dd", {}, b.senales.map((s) => chip(s, "aviso")))] : null,
        el("dt", { text: "Tablero" }), el("dd", { text: `versión ${b.tablero_version} · corte ${b.corte}` })));
    }
    if (f.texto) partes.push(el("h2", { text: "Contenido" }), el("pre", { class: "texto-ficha", text: f.texto }));
    if (f.tambien_en && f.tambien_en.length) partes.push(el("p", { class: "nota", text: "También en: " + f.tambien_en.join(", ") }));
    const rel = f.relacionados || {};
    if (Object.keys(rel).length) {
      partes.push(el("h2", { text: "Relacionados por id" }), el("div", { class: "relacionados" }, Object.entries(rel).map(([g, xs]) =>
        el("div", { class: "grupo-rel" }, el("h3", { text: `${g} (${xs.length})` }), el("ul", { class: "lista-rel" }, xs.map((x) => el("li", {},
          x.ficha ? enlaceFicha(f.proyecto, x.id) : el("span", { text: x.id }), el("span", { class: "nota", text: ` (${x.tipo}${x.sentido === "entra" ? ", lo cita" : ""}) ${x.titulo ? x.titulo.slice(0, 90) : ""}` }))))))));
    }
    if ((f.relaciones || []).length) {
      partes.push(el("h2", { text: "Relaciones (grafo a un salto)" }), el("div", { id: "grafo", role: "img", "aria-label": "Grafo de relaciones a un salto" }), leyenda(),
        el("ul", { class: "lista-rel" }, f.relaciones.map((a) => el("li", {}, a.sentido === "sale" ? "→ " : "← ",
          a.ficha ? enlaceFicha(f.proyecto, a.id) : el("span", { text: a.id }), ` (${a.tipo}) `, el("span", { class: "nota", text: a.titulo ? a.titulo.slice(0, 90) : "sin ficha" })))));
    }
    const vs = f.versiones;
    if (vs && (vs.lista || []).length) {
      const destino = el("div");
      partes.push(el("h2", { text: `Versiones (vigente v${vs.vigente || "—"} · aprobada v${vs.aprobada || "—"})` }),
        el("ul", { class: "linea-tiempo" }, vs.lista.map((x) => el("li", { class: [x.estado === "aprobado" ? "aprobado" : "", x.vigente ? "vigente" : ""].join(" ") },
          `v${x.version || "—"} · ${x.estado || "sin estado"} · ${x.fecha || "—"}${x.aprobado_por ? " · aprobó " + x.aprobado_por : ""}${x.decision ? " (" + x.decision + ")" : ""}`,
          el("div", { class: "nota", text: `${x.fuente}${x.copia ? " · copia congelada" : ""}${x.vigente ? " · vigente" : ""}${x.aprobada && !x.vigente ? " · aprobada" : ""}` })))),
        vs.n > 1 ? el("button", { type: "button", onclick: () => pintarCambios(f.proyecto, vs.doc_id, destino) }, "Comparar la vigente con la anterior") : null, destino);
    }
    if ((f.historia || []).length) {
      partes.push(el("h2", { text: "Historia (bitácora)" }), el("ul", { class: "linea-tiempo" }, f.historia.map((h) => el("li", {},
        `#${h.n} · ${String(h.fecha).slice(0, 10)} · ${h.operacion}${h.por ? " · " + h.por : ""}`,
        h.cambios && Object.keys(h.cambios).length ? el("div", { class: "nota", text: (Array.isArray(h.cambios) ? h.cambios.join(", ")
          : Object.entries(h.cambios).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(" → ") : v}`).join(" · ")).slice(0, 300) }) : null))));
    }
    if ((f.otros_proyectos || []).length) partes.push(el("p", { class: "nota" }, "También existe en: ", f.otros_proyectos.map((x, i) => [i ? ", " : "", enlaceFicha(x, f.ref || f.id, x)])));
    vista().replaceChildren(el("article", { class: "ficha-pagina" }, partes));
    if ((f.relaciones || []).length) dibujarGrafo(f);
  }

  function leyenda() {
    return el("div", { class: "leyenda" }, ["riesgos", "decisiones", "cambios", "issues", "acciones", "lecciones", "documento", "sin ficha"].map((k) => {
      const i = el("i"); i.style.background = COLORES[k]; return el("span", {}, i, k);
    }));
  }

  async function dibujarGrafo(f) {
    if (!window.cytoscape || !$("#grafo")) return;
    const r = await api("/api/relaciones", { id: f.id, proyecto: f.proyecto, saltos: 1 });
    const oscuro = matchMedia("(prefers-color-scheme: dark)").matches;
    const corto = (i) => (i.includes("#") ? i.split("/").pop().split("#")[0] : i).slice(0, 26);
    const elementos = r.nodos.map((n) => ({ data: { id: n.id, etiqueta: corto(n.id), nivel: n.id === f.id ? 2 : 1, color: colorDe(n), ficha: n.tipo !== "sin ficha" } }))
      .concat(r.aristas.map((a, i) => ({ data: { id: "a" + i, source: a.origen, target: a.destino, etiqueta: a.tipo } })));
    const cy = window.cytoscape({
      container: $("#grafo"), elements: elementos, wheelSensitivity: 0.3,
      layout: { name: "concentric", concentric: (n) => n.data("nivel"), levelWidth: () => 1, minNodeSpacing: 34, padding: 24, animate: false },
      style: [
        { selector: "node", style: { "background-color": "data(color)", label: "data(etiqueta)", "font-size": 11, color: oscuro ? "#ecece6" : "#1d1d1b",
          "text-valign": "bottom", "text-margin-y": 4, width: 18, height: 18, "border-width": 2, "border-color": oscuro ? "#1d1d1b" : "#ffffff" } },
        { selector: `node[id = "${f.id.replace(/["\\]/g, "")}"]`, style: { width: 28, height: 28, "font-weight": "bold" } },
        { selector: "edge", style: { width: 1.5, "line-color": oscuro ? "#5a5a54" : "#b8b8ae", "target-arrow-shape": "triangle",
          "target-arrow-color": oscuro ? "#5a5a54" : "#b8b8ae", "curve-style": "bezier", label: "data(etiqueta)", "font-size": 9,
          color: oscuro ? "#8d8d84" : "#7a7a72", "text-rotation": "autorotate" } },
      ],
    });
    cy.on("tap", "node", (e) => { const d = e.target.data(); if (d.ficha && d.id !== f.id) navegar(rutaFicha(f.proyecto, d.id)); });
  }

  async function pintarCambios(p, doc, destino) {
    try {
      const c = await api("/api/cambios", { doc, proyecto: p });
      if (!c.cambios || !c.cambios.length) { destino.replaceChildren(el("p", { class: "nota", text: c.aviso || "Sin cambios por secciones." })); return; }
      destino.replaceChildren(el("p", { class: "nota", text: `v${c.desde} → v${c.hasta}: ${c.resumen.agregada} agregadas, ${c.resumen.quitada} quitadas, ${c.resumen.modificada} modificadas` }),
        ...c.cambios.map((x) => el("div", { class: "cambio " + x.tipo }, el("strong", { text: `${x.tipo} · ${x.titulo}` }), el("pre", { text: x.resumen }))));
    } catch (e) { destino.replaceChildren(el("p", { class: "error", text: e.message })); }
  }

  // ---------------------------------------------------------------- inicio
  async function iniciar() {
    try {
      S.estado = await api("/api/estado");
      $("#persona").textContent = S.estado.persona;
      $("#pie").textContent = S.estado.proyectos.map((p) => `${p.proyecto}: ${p.vigentes} unidades vigentes, ${p.documentos} documentos, commit ${p.commit}, indexado ${fecha(p.indexado_en)}`).join(" · ")
        + ` · vectores: ${S.estado.proyectos[0] ? S.estado.proyectos[0].modelo_vectores : "—"}`;
    } catch (e) { $("#pie").textContent = e.message; }
    await dibujar();
    anunciar("");
  }
  document.addEventListener("DOMContentLoaded", iniciar);
})();
