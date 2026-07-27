/* =====================================================================
   ALPHA ARTIFICIAL — grafica.js  (el motor de gràfiques, SVG a mà)
   ---------------------------------------------------------------------
   Sin librerías externas: dibuja líneas multi-serie con
     - rango temporal (últimos N puntos)
     - modo € (valor) o % (rebasado al inicio del rango)
     - series visibles/ocultas + serie enfocada
     - área verde/roja cuando solo hay una serie protagonista
     - tooltip al pasar el ratón (el HTML lo pone quien llama)
   Uso:  AlphaChart.render(elemento, config)  → ver app.js
   ===================================================================== */
(function () {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const MESOS = ["gen", "febr", "març", "abr", "maig", "juny", "jul", "ag", "set", "oct", "nov", "des"];

  function fmtData(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    return `${d} ${MESOS[m - 1]}`;
  }
  function fmtDataLlarga(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    return `${d} ${MESOS[m - 1]} ${y}`;
  }
  const euro = (n) => Math.round(n).toLocaleString("ca-ES") + " €";
  const pct = (n) => (n >= 0 ? "+" : "") +
    n.toLocaleString("ca-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " %";

  function render(el, cfg) {
    const small = !!cfg.small;
    const W = cfg.width || 1100;
    const H = cfg.height || (small ? 120 : 480);
    const padL = small ? 4 : 74;
    const padR = small ? 4 : 20;
    const padT = small ? 6 : 18;
    const padB = small ? 6 : 34;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;

    const totalN = cfg.dies.length;
    const range = cfg.range && cfg.range !== Infinity ? Math.min(cfg.range, totalN) : totalN;
    const start = totalN - range;
    const N = range;

    const visibles = cfg.visible.filter((id) => cfg.series[id]);
    const mode = cfg.mode || "value";

    // --- valores de cada serie dentro del rango (rebasados si es %) ---
    const vals = {};
    visibles.forEach((id) => {
      const s = cfg.series[id];
      const base = mode === "pct" ? (start === 0 ? cfg.capital : s[start]) : 1;
      vals[id] = [];
      for (let i = start; i < totalN; i++) {
        vals[id].push(mode === "pct" ? (s[i] / base - 1) * 100 : s[i]);
      }
    });

    // --- rango Y global ---
    let lo = Infinity, hi = -Infinity;
    visibles.forEach((id) => vals[id].forEach((v) => { if (v < lo) lo = v; if (v > hi) hi = v; }));
    if (!isFinite(lo)) { lo = 0; hi = 1; }
    // que la línea base (capital / 0%) quede dentro si está cerca
    const baseV = mode === "pct" ? 0 : cfg.capital;
    if (!small) { lo = Math.min(lo, baseV); hi = Math.max(hi, baseV); }
    const span = hi - lo || 1;
    lo -= span * 0.06; hi += span * 0.07;

    const x = (i) => padL + (N <= 1 ? plotW / 2 : (plotW * i) / (N - 1));
    const y = (v) => padT + plotH * (1 - (v - lo) / (hi - lo));

    // --- ¿hay una única protagonista? → área verde/roja ---
    const protagonistes = visibles.filter((id) => {
      const m = cfg.models.find((mm) => mm.id === id);
      return m && !m.isIndex;
    });
    const heroina = protagonistes.length === 1 ? protagonistes[0] : null;

    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    // el sparkline puede estirarse; la gráfica grande mantiene proporciones
    svg.setAttribute("preserveAspectRatio", small ? "none" : "xMidYMid meet");
    svg.classList.add("achart");
    if (small) svg.classList.add("achart-small");

    const defs = document.createElementNS(NS, "defs");
    svg.appendChild(defs);

    const put = (parent, tag, attrs, text) => {
      const n = document.createElementNS(NS, tag);
      for (const k in attrs) n.setAttribute(k, attrs[k]);
      if (text != null) n.textContent = text;
      parent.appendChild(n);
      return n;
    };

    // --- rejilla + etiquetas ---
    if (!small) {
      const ticks = 5;
      for (let t = 0; t <= ticks; t++) {
        const v = lo + ((hi - lo) * t) / ticks;
        const yy = y(v);
        put(svg, "line", { x1: padL, y1: yy, x2: W - padR, y2: yy, class: "ag-line" });
        put(svg, "text", { x: padL - 10, y: yy + 4, class: "ag-label", "text-anchor": "end" },
          mode === "pct" ? pct(v) : euro(v));
      }
      const by = y(baseV);
      put(svg, "line", { x1: padL, y1: by, x2: W - padR, y2: by, class: "ag-base" });

      // etiquetas de fecha (unas 6)
      const nLab = Math.min(6, N);
      for (let t = 0; t < nLab; t++) {
        const i = Math.round((t * (N - 1)) / Math.max(1, nLab - 1));
        put(svg, "text", { x: x(i), y: H - 10, class: "ag-label", "text-anchor": t === 0 ? "start" : t === nLab - 1 ? "end" : "middle" },
          fmtData(cfg.dies[start + i]));
      }
    }

    // --- orden de dibujo: índice y autor debajo, competidoras encima ---
    const ordre = [...visibles].sort((a, b) => {
      const score = (id) => {
        const m = cfg.models.find((mm) => mm.id === id);
        return m.isIndex ? 0 : m.isAuthor ? 1 : 2;
      };
      return score(a) - score(b);
    });

    ordre.forEach((id) => {
      const m = cfg.models.find((mm) => mm.id === id);
      const arr = vals[id];
      const first = arr[0], last = arr[arr.length - 1];
      const puja = last >= first;
      const esHeroina = heroina === id;
      const color = esHeroina ? (puja ? "var(--verd)" : "var(--vermell)") : m.color;

      // área bajo la protagonista (o en modo sparkline)
      if (esHeroina || small) {
        const gid = "ag-grad-" + id + "-" + (puja ? "p" : "n") + (small ? "-s" : "");
        const grad = put(defs, "linearGradient", { id: gid, x1: 0, y1: 0, x2: 0, y2: 1 });
        const c = puja ? "70, 209, 138" : "255, 95, 107";
        put(grad, "stop", { offset: 0, "stop-color": `rgba(${c}, ${small ? 0.28 : 0.22})` });
        put(grad, "stop", { offset: 1, "stop-color": `rgba(${c}, 0)` });
        let dArea = `M ${x(0)} ${y(arr[0])}`;
        for (let i = 1; i < arr.length; i++) dArea += ` L ${x(i)} ${y(arr[i])}`;
        dArea += ` L ${x(arr.length - 1)} ${padT + plotH} L ${x(0)} ${padT + plotH} Z`;
        put(svg, "path", { d: dArea, fill: `url(#${gid})`, stroke: "none" });
      }

      let d = `M ${x(0)} ${y(arr[0])}`;
      for (let i = 1; i < arr.length; i++) d += ` L ${x(i)} ${y(arr[i])}`;
      const dim = cfg.focus && cfg.focus !== id;
      put(svg, "path", {
        d, fill: "none",
        stroke: color,
        "stroke-width": small ? 2.2 : (m.isIndex ? 2.2 : m.isAuthor ? 1.8 : esHeroina ? 3 : 2.6),
        "stroke-linejoin": "round", "stroke-linecap": "round",
        "stroke-dasharray": m.dash || "none",
        class: "ag-serie" + (dim ? " ag-dim" : ""),
        "data-id": id,
        "vector-effect": "non-scaling-stroke",
      });

      // punto final
      if (!small) {
        put(svg, "circle", {
          cx: x(arr.length - 1), cy: y(last), r: 4,
          fill: color, stroke: "var(--fons)", "stroke-width": 1.6,
          class: dim ? "ag-dim" : "",
        });
      }
    });

    // --- capa de hover ---
    el.innerHTML = "";
    el.appendChild(svg);
    if (small || !cfg.tooltip) return;

    const hoverLayer = document.createElementNS(NS, "g");
    svg.appendChild(hoverLayer);
    const hitRect = put(svg, "rect", {
      x: padL, y: padT, width: plotW, height: plotH, fill: "transparent",
      style: "cursor: crosshair",
    });

    const tip = cfg.tooltipEl;
    const move = (clientX, clientY) => {
      const r = svg.getBoundingClientRect();
      const px = ((clientX - r.left) / r.width) * W;
      let i = Math.round(((px - padL) / plotW) * (N - 1));
      i = Math.max(0, Math.min(N - 1, i));

      // guía + puntos
      hoverLayer.innerHTML = "";
      put(hoverLayer, "line", { x1: x(i), y1: padT, x2: x(i), y2: padT + plotH, class: "ag-guia" });
      const rows = [];
      visibles.forEach((id) => {
        const m = cfg.models.find((mm) => mm.id === id);
        const v = vals[id][i];
        const esHeroina = heroina === id;
        const arr = vals[id];
        const color = esHeroina ? (arr[arr.length - 1] >= arr[0] ? "var(--verd)" : "var(--vermell)") : m.color;
        put(hoverLayer, "circle", { cx: x(i), cy: y(v), r: 4, fill: color, stroke: "var(--fons)", "stroke-width": 1.6 });
        rows.push({ m, v, iGlobal: start + i });
      });

      if (tip) {
        tip.innerHTML = cfg.tooltip(start + i, rows);
        tip.hidden = false;
        const stage = el.parentElement;
        const sr = stage.getBoundingClientRect();
        const cx = r.left + (x(i) / W) * r.width - sr.left;
        const half = tip.offsetWidth / 2 || 130;
        tip.style.left = Math.min(Math.max(cx, half + 4), sr.width - half - 4) + "px";
        tip.style.top = Math.max(8, clientY - sr.top - tip.offsetHeight - 18) + "px";
      }
    };
    hitRect.addEventListener("mousemove", (ev) => move(ev.clientX, ev.clientY));
    hitRect.addEventListener("touchmove", (ev) => {
      if (ev.touches.length) { move(ev.touches[0].clientX, ev.touches[0].clientY); ev.preventDefault(); }
    }, { passive: false });
    const out = () => { hoverLayer.innerHTML = ""; if (tip) tip.hidden = true; };
    hitRect.addEventListener("mouseleave", out);
    hitRect.addEventListener("touchend", out);
  }

  /* ===================================================================
     GRÀFIC DE DISC (donut) — per a la composició de carteres
     -------------------------------------------------------------------
     cfg = {
       dades: [{etiqueta, valor, color}],   // valor en % o en €
       unitat: "%" | "€",
       centre: {dalt, baix},                // text del forat del mig
       llegenda: true/false
     }
     =================================================================== */
  const PALETA = [
    "#ffb000", "#3fd07a", "#5b8def", "#cc785c", "#9a7bff", "#ff4d6d",
    "#19c3a0", "#ffd84d", "#c084fc", "#7aa8d8", "#f0a06a", "#8be0f8",
    "#b6f04d", "#ff9f68", "#6a9fb5", "#d884ff",
  ];

  function donut(el, cfg) {
    const dades = (cfg.dades || []).filter((d) => d.valor > 0);
    if (!dades.length) { el.innerHTML = '<p class="buit">Sense dades.</p>'; return; }

    const total = dades.reduce((s, d) => s + d.valor, 0) || 1;
    const R = 100, r = 62, cx = 110, cy = 110;   // radis exterior/interior
    const fmt = (v) => cfg.unitat === "€"
      ? Math.round(v).toLocaleString("ca-ES") + " €"
      : v.toLocaleString("ca-ES", { maximumFractionDigits: 1 }) + " %";

    let angle = -Math.PI / 2;   // comencem a dalt
    let camins = "";
    dades.forEach((d, i) => {
      const frac = d.valor / total;
      const fi = angle + frac * Math.PI * 2;
      const color = d.color || PALETA[i % PALETA.length];
      // un sector "gairebé sencer" es dibuixa com dos arcs per evitar bugs SVG
      const gran = frac > 0.5 ? 1 : 0;
      const x1 = cx + Math.cos(angle) * R, y1 = cy + Math.sin(angle) * R;
      const x2 = cx + Math.cos(fi) * R, y2 = cy + Math.sin(fi) * R;
      const x3 = cx + Math.cos(fi) * r, y3 = cy + Math.sin(fi) * r;
      const x4 = cx + Math.cos(angle) * r, y4 = cy + Math.sin(angle) * r;
      const d0 = frac >= 0.999
        ? `M ${cx - R} ${cy} A ${R} ${R} 0 1 1 ${cx + R} ${cy} A ${R} ${R} 0 1 1 ${cx - R} ${cy} Z
           M ${cx - r} ${cy} A ${r} ${r} 0 1 0 ${cx + r} ${cy} A ${r} ${r} 0 1 0 ${cx - r} ${cy} Z`
        : `M ${x1} ${y1} A ${R} ${R} 0 ${gran} 1 ${x2} ${y2} L ${x3} ${y3} A ${r} ${r} 0 ${gran} 0 ${x4} ${y4} Z`;
      camins += `<path d="${d0}" fill="${color}" class="donut-tros"
        data-etiqueta="${d.etiqueta}" data-valor="${fmt(d.valor)}"
        fill-rule="evenodd"><title>${d.etiqueta}: ${fmt(d.valor)}</title></path>`;
      angle = fi;
    });

    const centre = cfg.centre || {};
    const svg = `<svg viewBox="0 0 220 220" class="donut">
      ${camins}
      ${centre.dalt ? `<text x="${cx}" y="${cy - 4}" class="donut-c1" text-anchor="middle">${centre.dalt}</text>` : ""}
      ${centre.baix ? `<text x="${cx}" y="${cy + 16}" class="donut-c2" text-anchor="middle">${centre.baix}</text>` : ""}
    </svg>`;

    const llegenda = cfg.llegenda === false ? "" : `<div class="donut-leg">${
      dades.map((d, i) => `<div class="donut-fila">
        <span class="donut-punt" style="background:${d.color || PALETA[i % PALETA.length]}"></span>
        <span class="donut-nom">${d.etiqueta}</span>
        <span class="donut-val">${fmt(d.valor)}</span>
      </div>`).join("")}</div>`;

    el.innerHTML = `<div class="donut-wrap">${svg}${llegenda}</div>`;
  }

  window.AlphaChart = { render, donut, fmtData, fmtDataLlarga, PALETA };
})();
