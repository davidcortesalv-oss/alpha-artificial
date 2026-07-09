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

  window.AlphaChart = { render, fmtData, fmtDataLlarga };
})();
