// pm-kb · pestaña «Tableros» del proyecto: dibuja el pm-tablero/1 que publica pm-kb (generado por el núcleo de
// pm-method; no calcula reglas ni escribe nada). Tres vistas (ciclo y puertas, atención, entrega), la línea de tiempo de
// instantáneas congeladas, la comparación entre dos tableros, el filtro «Por actor» (reglas del núcleo, aplicadas por el
// servicio) y «actualizar ahora». Cada tarjeta es un enlace a su ficha por id estable (/p/<proyecto>/ficha/<ref>), nunca
// por ruta. Con `compartido` (página de un enlace compartido, /v) dibuja solo el tablero del enlace: sin línea de tiempo,
// sin comparar, sin selector de actor y sin «actualizar ahora»; las fichas van a /v/ficha/<ref>. Todo texto se inserta
// como texto.
"use strict";
(() => {
  const { $, el, api, rutaFicha, chip, fecha, dias } = window.PMKB;
  const CADA_MS = 15000;
  const GRUPOS = [
    ["decidir", "Decidir", "una decisión de tu nivel espera"],
    ["escalar", "Escalar", "supera tu autoridad o tolerancia"],
    ["desbloquear", "Desbloquear", "algo frena a otros"],
    ["vigilar", "Vigilar", "sin acción hoy, pero se acerca"],
  ];
  const NOMBRE_ESTADO = {
    "no-iniciado": "No iniciado", "en-desarrollo": "En desarrollo", "en-revision": "En revisión", aprobado: "Aprobado",
    aceptado: "Aceptado", "fuera-especificacion": "Fuera de especificación", "con-concesion": "Con concesión",
    abierto: "Abierto", "en-evaluacion": "En evaluación", "pendiente-decision": "Pendiente de decisión", implementado: "Implementado",
    "en-accion": "En acción", "pendiente-cambio": "Pendiente de cambio", escalado: "Escalado", abierta: "Abierta", "en-curso": "En curso",
  };
  const REGISTRO = { cambios: "Cambios", issues: "Issues", acciones: "Acciones" };
  const SEVERIDAD = { bloqueo: ["■", "Bloqueo", "mal"], condicion: ["▲", "Condición", "aviso"], aviso: ["●", "Aviso", ""] };
  const DECISION = { aprobado: ["✓", "aprobado", "bien"], condicionado: ["◐", "condicionado", "aviso"], rechazado: ["✕", "rechazado", "mal"] };
  const SENAL = {
    vencida: ["vencida", "mal"], bloqueada: ["bloqueada", "mal"], "propuesta-pendiente": ["propuesta pendiente", "aviso"],
    "fuente-no-encontrada": ["fuente no encontrada", "mal"], "aprobada-anterior": ["hay una versión aprobada anterior", "aviso"],
    forzada: ["forzada", "mal"], "condiciones-abiertas": ["condiciones abiertas", "aviso"], discrepancias: ["discrepancias", "aviso"],
  };
  const VISTAS = [["ciclo", "Ciclo y puertas"], ["atencion", "Atención"], ["entrega", "Entrega"]];
  const nombreEstado = (e) => NOMBRE_ESTADO[e] || e;

  function nuevoEstado(raiz, o) {
    return { raiz, proyecto: o.proyecto, puedeActualizar: !!o.puedeActualizar && !o.compartido, vista: VISTAS.some((v) => v[0] === o.vista) ? o.vista : "ciclo",
      compartido: !!o.compartido, rutaFicha: o.rutaFicha || ((ref) => rutaFicha(o.proyecto, ref)), actor: o.compartido ? "" : (o.actor || ""), actores: [],
      sel: o.instantanea || "actual", comparar: "", datos: null, meta: null, historial: [], gestion: "", version: null,
      carriles: window.matchMedia("(min-width: 900px)").matches, marcadas: new Set(), comparacion: null, temporizador: null,
      pausado: false, alCambiar: o.alCambiar || (() => {}) };
  }

  // ------------------------------------------------------------------ piezas
  function tarjeta(T, c, clase = "", extra = []) {
    if (!c) return null;
    const sen = (c.senales || []).map((s) => { const [t, k] = SENAL[s] || [s, ""]; return chip(t, k); });
    return el("a", { class: "tb-tarjeta " + clase + (T.marcadas.has(c.ref) ? " tb-nueva" : ""), href: T.rutaFicha(c.ref),
      "data-nav": true, "data-ref": c.ref, title: "Ficha de " + c.ref },
      el("span", { class: "tb-fila" }, el("span", { class: "tb-ref", text: c.ref }), extra),
      el("span", { class: "tb-que", text: c.nombre }),
      c.descripcion ? el("span", { class: "tb-sub", text: c.descripcion }) : null,
      sen.length ? el("span", { class: "tb-fila" }, sen) : null);
  }
  function columna(titulo, hijos, clase = "", ayuda = "") {
    const n = hijos.filter(Boolean).length;
    return el("section", { class: "tb-col " + clase, "aria-label": `${titulo}: ${n}` },
      el("header", { class: "tb-col-cab", title: ayuda || null }, el("span", { text: titulo }), el("span", { class: "tb-cuenta", text: String(n) })),
      n ? hijos : el("p", { class: "tb-vacia", text: "—" }));
  }
  const desliza = (...h) => el("div", { class: "tb-desliza" }, h);

  // ------------------------------------------------------------------ pulso
  function pulso(T, d) {
    const c = d.ciclo || {}, cols = c.columnas || [];
    const actual = cols.find((x) => x.estado === "actual" && !x.puerta) || {};
    const prox = cols.find((x) => x.puerta && x.estado === "proxima");
    const hs = prox ? prox.hallazgos || [] : [];
    const bl = hs.filter((h) => h.severidad === "bloqueo").length, cond = hs.filter((h) => h.severidad === "condicion").length;
    const fin = c.fin_previsto || actual.fin_previsto;
    const faltan = fin ? Math.round((Date.parse(fin) - Date.parse(d.corte)) / 86400000) : null;
    const t = (d.atencion || {}).totales || {};
    const dato = (etq, valor, ...sub) => el("div", { class: "tb-dato" }, el("span", { class: "tb-etq", text: etq }), el("strong", { text: valor }), sub);
    return el("div", { class: "tb-pulso" },
      dato("Proyecto", d.proyecto || T.proyecto),
      dato("Fase · proceso", `${c.fase || "—"} · ${c.proceso || "—"}`),
      dato("Etapa", `${c.etapa ?? "—"}${c.nombre_etapa ? " · " + c.nombre_etapa : ""}`,
        fin ? el("span", { class: "tb-sub", text: `fin previsto ${fin}` + (faltan !== null && !Number.isNaN(faltan) ? ` · ${dias(faltan)}` : "") }) : null),
      dato("Próxima puerta", prox ? prox.tipo : "—",
        prox ? el("span", { class: "tb-sub " + (bl ? "tb-mal" : "tb-bien"), text: bl ? `■ ${bl} bloqueo(s)` + (cond ? ` · ▲ ${cond} condición(es)` : "") : (cond ? `▲ ${cond} condición(es)` : "✓ sin bloqueos") }) : null),
      el("div", { class: "tb-dato tb-atencion-resumen" }, el("span", { class: "tb-etq", text: "Atención" }),
        el("span", {}, GRUPOS.map(([g, n]) => chip(`${n} ${t[g] || 0}`, "tb-g-" + g + ((t[g] || 0) ? "" : " tb-cero"))))),
      c.excepcion ? dato("Excepción abierta", c.excepcion) : null,
      d.actor ? dato("Actor", d.actor.nombre, el("span", { class: "tb-sub", text: [d.actor.rol, "RACI " + ["R", "A", "C", "I"].map((k) => `${k} ${((d.actor.letras || {})[k] || []).length}`).join(" · "),
        "solo lo suyo; el ciclo y las puertas son comunes"].filter(Boolean).join(" · ") })) : null,
      dato("Corte", d.corte || "—", el("span", { class: "tb-sub", text: T.sel === "actual" ? `versión ${T.meta ? T.meta.version : "—"}` : "instantánea" })));
  }

  // ------------------------------------------------------------------ vista 1: ciclo con puertas
  function vistaCiclo(T, d) {
    const c = d.ciclo || {};
    const fila = el("div", { class: "tb-ciclo", role: "list" });
    for (const col of c.columnas || []) {
      if (col.puerta && col.estado === "proxima") {
        fila.append(el("div", { class: "tb-puerta tb-proxima", role: "listitem", "aria-label": "Próxima puerta" },
          el("div", { class: "tb-rombo", "aria-hidden": "true", text: "◇" }),
          el("div", { class: "tb-tipo", text: "Próxima: " + col.tipo }),
          tarjeta(T, col.tarjeta),
          (col.hallazgos || []).length ? el("ul", { class: "tb-hallazgos" }, col.hallazgos.map((h) => {
            const [ic, txt] = SEVERIDAD[h.severidad] || ["•", h.severidad];
            return el("li", { class: "tb-s-" + h.severidad }, el("span", { class: "tb-sev", text: `${ic} ${txt} ${h.id}` }), el("span", { text: h.mensaje }));
          })) : el("p", { class: "tb-bien", text: "✓ lista para presentar" })));
        continue;
      }
      if (col.puerta) {
        fila.append(el("div", { class: "tb-puerta tb-hecha", role: "listitem", "aria-label": "Puerta decidida" },
          el("div", { class: "tb-rombo", "aria-hidden": "true", text: "◆" }),
          (col.decisiones || []).map((x) => {
            const [ic, txt, k] = DECISION[x.decision] || ["•", x.decision, ""];
            return tarjeta(T, x, "tb-decision", [chip(`${ic} ${txt}`, k), x.decision_id ? chip(x.decision_id) : null]);
          })));
        continue;
      }
      const marca = { hecha: "✓ hecha", actual: "● en curso", futura: "○ por venir" }[col.estado] || col.estado;
      fila.append(el("div", { class: "tb-etapa tb-" + col.estado, role: "listitem", "aria-current": col.estado === "actual" ? "step" : null },
        el("div", { class: "tb-estado-etapa", text: marca }),
        el("h3", { text: col.nombre }),
        col.estado === "actual" ? [
          col.proceso ? el("div", { class: "tb-sub", text: `proceso ${col.proceso}` + (col.inicio ? ` · ${col.inicio} → ${col.fin_previsto || "…"}` : "") }) : null,
          col.excepcion ? el("div", { class: "tb-excepcion", text: "■ excepción abierta: " + col.excepcion }) : null,
          (col.senales || []).length ? el("ul", { class: "tb-senales", "aria-label": "Tolerancias y cambios" },
            col.senales.map((s) => el("li", {}, chip(s.regla, "tb-g-vigilar"), " ", el("span", { text: s.que })))) : el("div", { class: "tb-bien", text: "✓ dentro de tolerancia" }),
        ] : null,
        (col.eventos || []).map((e) => tarjeta(T, e, "tb-evento"))));
    }
    const extra = [];
    if ((c.condiciones_abiertas || []).length) extra.push(el("p", { class: "tb-nota" }, "Condiciones abiertas: ",
      c.condiciones_abiertas.map((r, i) => [i ? ", " : "", el("a", { href: T.rutaFicha(r), "data-nav": true, text: r })])));
    if ((c.forzadas || []).length) extra.push(el("p", { class: "tb-nota tb-mal", text: "Puertas forzadas: " + c.forzadas.join(", ") }));
    return el("div", {}, desliza(fila), extra);
  }

  // ------------------------------------------------------------------ vista 2: atención
  const tarjetaAtencion = (T, i) => tarjeta(T, i, "tb-p" + (i.prioridad || 4), [chip(i.regla || ""), el("span", { class: "tb-prio", title: "prioridad (1 = más urgente)", text: "P" + (i.prioridad ?? "") })]);
  function vistaAtencion(T, d) {
    const items = [...((d.atencion || {}).items || [])].sort((a, b) => (a.prioridad || 9) - (b.prioridad || 9));
    const control = el("label", { class: "tb-opcion" },
      el("input", { type: "checkbox", ...(T.carriles ? { checked: true } : {}), onchange: (e) => { T.carriles = e.target.checked; pintar(T); } }),
      " carriles por responsable");
    if (!items.length) return el("div", {}, control, el("p", { class: "tb-bien tb-grande", text: "✓ Nada espera atención en este corte." }));
    if (!T.carriles) {
      return el("div", {}, control, desliza(el("div", { class: "tb-tablero tb-4" },
        GRUPOS.map(([g, n, ayuda]) => columna(n, items.filter((i) => i.grupo === g).map((i) => tarjetaAtencion(T, i)), "tb-g-" + g, ayuda)))));
    }
    const tot = (d.atencion || {}).totales || {};
    const personas = [...new Set(items.map((i) => i.responsable || "sin responsable"))];
    const grilla = el("div", { class: "tb-carriles", role: "table", "aria-label": "Atención por responsable" },
      el("div", { class: "tb-carril-cab", role: "row" }, el("span", { role: "columnheader", text: "Responsable" }),
        GRUPOS.map(([g, n, ayuda]) => el("span", { role: "columnheader", class: "tb-g-" + g, title: ayuda, text: `${n} · ${tot[g] || 0}` }))));
    for (const p of personas) {
      const suyos = items.filter((i) => (i.responsable || "sin responsable") === p);
      grilla.append(el("div", { class: "tb-carril", role: "row" }, el("div", { class: "tb-persona", role: "rowheader", text: p }),
        GRUPOS.map(([g]) => el("div", { role: "cell", class: "tb-celda" }, suyos.filter((i) => i.grupo === g).map((i) => tarjetaAtencion(T, i))))));
    }
    return el("div", {}, control, desliza(grilla));
  }

  // ------------------------------------------------------------------ vista 3: entrega en dos niveles
  function vistaEntrega(T, d) {
    const ent = d.entrega || {}, P = ent.productos || { columnas: [], excepcion: [], tarjetas: [] };
    const colProd = (estado) => columna(nombreEstado(estado), P.tarjetas.filter((t) => t.columna === estado || (!t.columna && t.estado === estado))
      .map((t) => tarjeta(T, t, "tb-producto", [t.prioridad ? chip(String(t.prioridad).toUpperCase(), "tb-moscow") : null, t.q ? chip(t.q) : null])), "tb-e-" + estado);
    const enExcepcion = P.tarjetas.some((t) => (P.excepcion || []).includes(t.estado));
    const productos = el("section", { class: "tb-bloque" },
      el("h3", { text: `Productos (${P.tarjetas.length})` }),
      el("p", { class: "tb-nota", text: "Estado derivado de los registros (estado.py productos" + (P.fuente ? `, ${P.fuente}` : "") + ")." }),
      desliza(el("div", { class: "tb-tablero tb-flujo" }, (P.columnas || []).map(colProd), enExcepcion ? (P.excepcion || []).map(colProd) : null)));
    const control = el("section", { class: "tb-bloque" }, el("h3", { text: "Control" }),
      el("p", { class: "tb-nota", text: "Cambios, issues y acciones abiertos. Las propuestas pendientes (punteadas) todavía no cambiaron el registro: las aprueba una persona." }));
    for (const reg of ["cambios", "issues", "acciones"].filter((r) => (ent.control || {})[r])) {
      const v = ent.control[reg];
      const cerrados = Object.entries(v.cerrados || {}).map(([e, n]) => `${n} ${nombreEstado(e).toLowerCase()}`).join(" · ");
      const cols = (v.columnas || []).map((estado) => columna(nombreEstado(estado), [
        ...(v.tarjetas || []).filter((t) => t.columna === estado).map((t) => tarjeta(T, t, "", [t.prioridad ? chip(t.prioridad) : null])),
        ...(v.propuestas || []).filter((s) => s.columna === estado).map((s) => tarjeta(T, s, "tb-sombra", [chip("propuesta")])),
      ]));
      control.append(el("div", { class: "tb-registro" },
        el("h4", {}, REGISTRO[reg] || reg, cerrados ? el("span", { class: "tb-sub", text: " · cerrados: " + cerrados }) : null),
        desliza(el("div", { class: "tb-tablero tb-control" }, cols))));
    }
    return el("div", {}, productos, control);
  }

  function eventos(d) {
    if (!(d.eventos || []).length) return null;
    return el("details", { class: "tb-eventos" }, el("summary", { text: `Últimos eventos de la bitácora (${d.n_bitacora})` }),
      el("ol", {}, d.eventos.map((e) => el("li", {}, el("code", { text: `#${e.n}` }), ` ${e.fecha} · ${e.operacion} ${e.registro || e.archivo} ${(e.ids || []).join(", ")}` + (e.por ? ` · ${e.por}` : "")))));
  }

  // ------------------------------------------------------------------ línea de tiempo, comparar y estado en vivo
  function etiquetaInstantanea(x) {
    return [x.etapa !== null && x.etapa !== undefined ? `Etapa ${x.etapa}` : "", x.puerta ? `al decidir ${x.puerta}` : x.etiqueta, x.fecha].filter(Boolean).join(" · ");
  }

  function lineaTiempo(T) {
    const items = T.historial.map((x) => ({ id: x.id, titulo: etiquetaInstantanea(x), sub: x.decision ? `${x.decision}${x.decision_id ? " · " + x.decision_id : ""}` : (x.tipo || ""), x }))
      .concat([{ id: "actual", titulo: "Actual (en vivo)", sub: T.meta && T.sel === "actual" ? `versión ${T.meta.version}` : "", x: null }]);
    return el("ol", { class: "tb-linea", "aria-label": "Línea de tiempo del tablero" }, items.map((it) =>
      el("li", { class: (it.id === "actual" ? "tb-l-actual " : "") + (it.x && it.x.en_bitacora === false ? "tb-l-mod" : "") },
        el("button", { type: "button", "aria-pressed": String(T.sel === it.id), "data-instantanea": it.id, onclick: () => elegir(T, it.id) },
          el("span", { class: "tb-l-titulo", text: it.titulo }), it.sub ? el("span", { class: "tb-sub", text: it.sub }) : null))));
  }

  function barra(T) {
    const otras = [["", "—"]].concat(T.historial.map((x) => [x.id, etiquetaInstantanea(x)]), [["actual", "Actual (en vivo)"]]).filter(([id]) => id !== T.sel);
    const selCmp = el("select", { "aria-label": "Comparar con", class: "tb-comparar", onchange: (e) => { T.comparar = e.target.value; comparar(T); } },
      otras.map(([id, n]) => el("option", { value: id, ...(id === T.comparar ? { selected: true } : {}) }, n)));
    const selActor = T.compartido || !T.actores.length ? null : el("select", { "aria-label": "Por actor", class: "tb-actor", onchange: (e) => elegirActor(T, e.target.value) },
      el("option", { value: "" }, "Todos"), T.actores.map((a) => { const v = a.id || a.nombre;
        return el("option", { value: v, ...(v === T.actor ? { selected: true } : {}) }, a.nombre + (a.rol ? ` (${a.rol})` : "")); }));
    return el("div", { class: "tb-barra" },
      el("div", { class: "tb-vistas", role: "group", "aria-label": "Vista" },
        VISTAS.map(([v, n]) => el("button", { type: "button", "data-vista": v, "aria-pressed": String(T.vista === v), onclick: () => { T.vista = v; T.alCambiar({ vista: v }); pintar(T); } }, n))),
      selActor ? el("label", { class: "tb-opcion", title: "Solo lo de esa persona según raci.csv y sus responsabilidades (núcleo de pm-method)" }, "Por actor ", selActor) : null,
      T.compartido ? null : el("label", { class: "tb-opcion" }, "Comparar con ", selCmp),
      el("span", { class: "tb-vivo", role: "status" }),
      T.puedeActualizar && T.sel === "actual" ? el("button", { type: "button", class: "tb-actualizar", onclick: (e) => actualizar(T, e.target) }, "Actualizar ahora") : null,
      T.sel === "actual" ? el("button", { type: "button", class: "enlace", onclick: (e) => { T.pausado = !T.pausado; e.target.textContent = T.pausado ? "reanudar" : "pausar"; } }, "pausar") : null);
  }

  function estadoVivo(T, texto, clase = "") {
    const v = $(".tb-vivo", T.raiz);
    if (v) { v.className = "tb-vivo " + clase; v.textContent = texto; }
  }

  function aviso(T) {
    if (T.sel === "actual") return null;
    const x = T.historial.find((h) => h.id === T.sel) || (T.meta || {});
    return el("div", { class: "tb-congelada", role: "note" },
      el("strong", { text: "Instantánea congelada: no se actualiza. " }),
      `«${x.etiqueta || x.id}» · corte ${x.corte || "—"}` + (x.decision ? ` · decisión ${x.decision}` : "") + (x.decision_id ? ` (${x.decision_id})` : "") + (x.por ? ` · ${x.por}` : ""),
      x.en_bitacora === false ? el("span", { class: "chip mal", text: "modificada fuera de los scripts (BIT-02)" }) : null,
      x.html_ruta ? [" · ", el("a", { href: "/archivo/" + encodeURIComponent(T.proyecto) + "/" + x.html_ruta.split("/").map(encodeURIComponent).join("/") + "?descargar=1", text: "descargar el HTML estático" })] : null);
  }

  function pintarComparacion(T) {
    const cont = $(".tb-comparacion", T.raiz);
    if (!cont) return;
    const c = T.comparacion;
    if (!c) { cont.replaceChildren(); return; }
    if (c.error) { cont.replaceChildren(el("p", { class: "error", text: c.error })); return; }
    const lista = (titulo, xs, fn) => el("div", { class: "tb-cmp-grupo" }, el("h4", { text: `${titulo} (${xs.length})` }),
      xs.length ? el("ul", {}, xs.slice(0, 60).map(fn)) : el("p", { class: "tb-nota", text: "—" }), xs.length > 60 ? el("p", { class: "tb-nota", text: `… y ${xs.length - 60} más` }) : null);
    const a = (x) => el("a", { href: T.rutaFicha(x.ref), "data-nav": true, text: x.ref });
    cont.replaceChildren(el("section", { class: "tb-cmp", "aria-label": "Comparación" },
      el("h3", { text: `Comparación: ${c.a} (${c.corte_a}) → ${c.b} (${c.corte_b})` }),
      el("div", { class: "tb-cmp-cols" },
        lista("Entraron", c.entraron, (x) => el("li", {}, chip(x.vista), " ", a(x), " ", el("span", { text: `${x.nombre} · ${x.columna || x.estado}` }))),
        lista("Salieron", c.salieron, (x) => el("li", {}, chip(x.vista), " ", a(x), " ", el("span", { text: `${x.nombre} · ${x.columna || x.estado}` }))),
        lista("Cambiaron de columna o estado", c.cambiaron, (x) => el("li", {}, chip(x.vista), " ", a(x), " ",
          el("span", { text: `${x.nombre}: ` + (x.de.columna === x.a.columna ? `${x.de.estado || "—"} → ${x.a.estado || "—"} (${x.a.columna})` : `${x.de.columna || x.de.estado} → ${x.a.columna || x.a.estado}`) })))),
      el("p", { class: "tb-nota", text: "Resaltadas en el tablero: las tarjetas que entraron o cambiaron (cuando el tablero que se ve es el más nuevo de los dos)." })));
  }

  async function comparar(T) {
    T.comparacion = null; T.marcadas = new Set();
    if (T.comparar) {
      const orden = (id) => (id === "actual" ? 1e9 : (T.historial.find((h) => h.id === id) || { orden: -1 }).orden);
      const [a, b] = orden(T.comparar) < orden(T.sel) ? [T.comparar, T.sel] : [T.sel, T.comparar];
      try {
        T.comparacion = await api("/api/tablero/comparar", { proyecto: T.proyecto, a, b, actor: T.actor });
        if (b === T.sel) T.marcadas = new Set([...T.comparacion.entraron, ...T.comparacion.cambiaron].map((x) => x.ref));
      } catch (e) { T.comparacion = { error: e.message }; }
    }
    T.alCambiar({ comparar: T.comparar });
    pintar(T);
  }

  function pintar(T) {
    const d = T.datos;
    if (!d) return;
    T.raiz.replaceChildren(...[
      T.compartido ? null : lineaTiempo(T), barra(T), aviso(T), el("div", { class: "tb-comparacion" }),
      el("div", { class: "tb-pulso-cont" }, pulso(T, d)),
      el("div", { class: "tb-vista" }, { ciclo: vistaCiclo, atencion: vistaAtencion, entrega: vistaEntrega }[T.vista](T, d),
        (d.avisos || []).map((a) => el("p", { class: "tb-nota tb-mal", text: "aviso: " + a }))),
      el("div", { class: "tb-eventos-cont" }, eventos(d)),
      el("p", { class: "tb-nota", text: "Solo lectura: el tablero se deriva de estado.json, los registros y la bitácora del proyecto (núcleo de pm-method). "
        + (T.compartido ? "Cada tarjeta abre su ficha." : "Los cambios se hacen con pm-method, o como propuesta que aprueba una persona.") })].filter(Boolean));
    pintarComparacion(T);
    if (T.sel === "actual" && T.meta) estadoVivo(T, `● en vivo · versión ${T.meta.version} · publicado ${fecha(T.meta.generado_en)} (${T.meta.origen || "—"})`, "tb-ok");
    else estadoVivo(T, "○ instantánea congelada");
  }

  const huellas = (d) => {
    const m = new Map();
    const poner = (c) => { if (c && c.ref) m.set(c.ref, `${c.columna}|${c.estado}`); };
    for (const col of (d.ciclo || {}).columnas || []) { (col.decisiones || []).forEach(poner); (col.eventos || []).forEach(poner); poner(col.tarjeta); }
    ((d.atencion || {}).items || []).forEach(poner);
    (((d.entrega || {}).productos || {}).tarjetas || []).forEach(poner);
    for (const v of Object.values((d.entrega || {}).control || {})) { (v.tarjetas || []).forEach(poner); (v.propuestas || []).forEach(poner); }
    Object.values((d.artefactos || {}).elementos || {}).forEach(poner);
    return m;
  };

  async function cargar(T, resaltar = false) {
    const r = await api("/api/tablero", { proyecto: T.proyecto, instantanea: T.sel === "actual" ? "" : T.sel, actor: T.actor });
    if (resaltar && T.datos) {
      const antes = huellas(T.datos), despues = huellas(r.datos);
      T.marcadas = new Set([...despues].filter(([k, v]) => antes.get(k) !== v).map(([k]) => k));
      if (T.marcadas.size) {
        $("#anuncio").textContent = `Tablero actualizado: ${T.marcadas.size} cambio(s) resaltado(s).`;
        setTimeout(() => { T.marcadas = new Set(); for (const n of T.raiz.querySelectorAll(".tb-nueva")) n.classList.remove("tb-nueva"); }, 15000);
      }
    }
    T.datos = r.datos;
    T.meta = r.instantanea || r;
    T.version = r.version ?? null;
    pintar(T);
  }

  async function elegir(T, id) {
    T.sel = id; T.comparar = T.comparar === id ? "" : T.comparar; T.marcadas = new Set();
    if (!T.comparar) T.comparacion = null;          // sin comparación elegida, no queda la anterior a la vista
    T.alCambiar({ instantanea: id === "actual" ? "" : id, comparar: T.comparar });
    try { await cargar(T); if (T.comparar) await comparar(T); } catch (e) { estadoVivo(T, "○ " + e.message, "tb-mal"); }
  }

  async function elegirActor(T, v) {
    T.actor = v; T.marcadas = new Set();
    if (!T.comparar) T.comparacion = null;
    T.alCambiar({ actor: v });
    try { await cargar(T); if (T.comparar) await comparar(T); } catch (e) { estadoVivo(T, "○ " + e.message, "tb-mal"); }
  }

  async function sondear(T) {
    if (T.sel !== "actual" || T.pausado || document.hidden || !T.raiz.isConnected) return;
    try {
      const v = await api("/api/tablero/version", { proyecto: T.proyecto });
      if (v.version !== T.version) await cargar(T, true);
      else { T.meta = { ...T.meta, generado_en: v.generado_en, origen: v.origen }; estadoVivo(T, `● en vivo · versión ${v.version} · publicado ${fecha(v.generado_en)} (${v.origen || "—"})`, "tb-ok"); }
    } catch (e) { estadoVivo(T, "○ " + e.message, "tb-mal"); }
  }

  async function actualizar(T, boton) {
    boton.disabled = true;
    const texto = boton.textContent;
    boton.textContent = "Actualizando…";
    try {
      const r = await api("/api/tablero/actualizar", {}, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ proyecto: T.proyecto }) });
      $("#anuncio").textContent = `Tablero regenerado: versión ${r.version}` + (r.cambio ? "" : " (sin cambios)");
      await cargar(T, true);
      estadoVivo(T, `● actualizado ahora · versión ${r.version}` + (r.cambio ? "" : " (sin cambios)"), "tb-ok");
    } catch (e) {
      estadoVivo(T, (e.estado === 429 ? "○ " : "○ no se pudo actualizar: ") + e.message, "tb-mal");
    } finally {
      const b = $(".tb-actualizar", T.raiz);
      if (b) { b.disabled = false; b.textContent = texto; }
    }
  }

  async function montar(raiz, opciones) {
    const T = nuevoEstado(raiz, opciones);
    raiz.classList.add("tb");
    raiz.replaceChildren(el("p", { class: "nota", text: "Cargando el tablero…" }));
    try {
      // Enlace compartido: su único tablero (sin historial, que el servicio no le da). Portal: historial y actores.
      const h = T.compartido ? { instantaneas: [], actual: true } : await api("/api/tablero/historial", { proyecto: T.proyecto });
      T.historial = h.instantaneas || []; T.gestion = h.gestion || "";
      if (!T.compartido) {
        try { T.actores = (await api("/api/tablero/actores", { proyecto: T.proyecto })).actores || []; } catch { T.actores = []; }
        if (T.actor && !T.actores.some((a) => (a.id || a.nombre) === T.actor)) T.actores.push({ id: "", nombre: T.actor, rol: "" });
      }
      if (!T.compartido && T.sel !== "actual" && !T.historial.some((x) => x.id === T.sel)) T.sel = "actual";
      if (!h.actual && T.sel === "actual") {
        raiz.replaceChildren(el("p", { class: "tb-mal tb-grande", text: "Sin tablero publicado para este proyecto." }),
          el("p", { class: "nota", text: `Se publica al indexar, con pm-kb vigilar o con: pm-kb tablero --proyecto ${T.proyecto}` }));
        return { parar() {} };
      }
      await cargar(T);
      if (opciones.comparar) { T.comparar = opciones.comparar; await comparar(T); }
    } catch (e) {
      raiz.replaceChildren(el("p", { class: "error", text: e.message }));
      return { parar() {} };
    }
    T.temporizador = setInterval(() => sondear(T), CADA_MS);
    return { parar() { if (T.temporizador) clearInterval(T.temporizador); T.temporizador = null; } };
  }

  window.PMKBTablero = { montar };
})();
