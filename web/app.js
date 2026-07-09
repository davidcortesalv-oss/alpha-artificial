/* =====================================================================
   ALPHA ARTIFICIAL — app.js  (la lógica de toda la web)
   ---------------------------------------------------------------------
   - Carga los datos (demo o reales desde dades.json) y los refresca solo
   - Enrutador por hash: #/ (tauler), #/informes, #/canvis, #/moments,
     #/etfs, #/biaixos, #/apis, #/ia/<id>
   - Cada vista se pinta con innerHTML; la gráfica la dibuja grafica.js
   Comentarios en castellano; todo lo visible, en catalán.
   ===================================================================== */
(function () {
  "use strict";

  // ------------------------------------------------------------------
  //  Utilidades de formato (locale catalán)
  // ------------------------------------------------------------------
  const euro = (n) => Math.round(n).toLocaleString("ca-ES") + " €";
  const euro2 = (n) => n.toLocaleString("ca-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
  const pct = (n) => (n >= 0 ? "+" : "") + n.toLocaleString("ca-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " %";
  const pts = (n) => (n >= 0 ? "+" : "") + n.toLocaleString("ca-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " pts";
  const dec1 = (n) => n.toLocaleString("ca-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const cls = (n) => (n >= 0 ? "pos" : "neg");
  const $ = (sel, ctx) => (ctx || document).querySelector(sel);
  const fmtData = (iso) => (iso ? window.AlphaChart.fmtDataLlarga(iso) : "—");

  // ------------------------------------------------------------------
  //  Estado global
  // ------------------------------------------------------------------
  let DATA = null;
  let chartState = { visible: null, mode: "value", range: Infinity, focus: null };
  let etfState = { cat: "Totes", cerca: "" };
  let informesFiltre = "tots";
  let canvisFiltre = "tots";

  // ------------------------------------------------------------------
  //  Carga de datos: demo → intenta dades.json → refresco periódico
  // ------------------------------------------------------------------
  function boot() {
    DATA = window.ALPHA_DEMO;
    carregarDadesReals(true);
    setInterval(() => carregarDadesReals(false), 60000); // refresc cada minut
    window.addEventListener("hashchange", route);
    bindNav();
    route();
  }

  function carregarDadesReals(primerCop) {
    fetch("dades.json", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .then((real) => {
        if (real && real.models && real.series) {
          const canvi = !DATA || DATA.meta.generat !== real.meta.generat || DATA.meta.font !== "real";
          if (canvi) {
            real.meta.font = "real";
            DATA = real;
            chartState.visible = null; // recalcular series visibles
            route();
          }
        }
        pintarEstatFont();
      })
      .catch(() => pintarEstatFont());
  }

  function pintarEstatFont() {
    const el = $("#font-dades");
    if (!el || !DATA) return;
    if (DATA.meta.font === "real") {
      el.innerHTML = `<span class="dot dot-verd"></span> DADES REALS` +
        (DATA.meta.generat ? ` <span class="font-sub">· actualitzat ${DATA.meta.generat.slice(0, 16).replace("T", " ")}</span>` : "");
    } else {
      el.innerHTML = `<span class="dot dot-ambre"></span> DEMOSTRACIÓ <span class="font-sub">· esperant el torneig real</span>`;
    }
  }

  // ------------------------------------------------------------------
  //  Derivados de los datos
  // ------------------------------------------------------------------
  const model = (id) => DATA.models.find((m) => m.id === id);
  const serie = (id) => DATA.series[id] || [];
  const lastVal = (id) => { const s = serie(id); return s[s.length - 1] || DATA.meta.capital; };
  const retPct = (id) => (lastVal(id) / DATA.meta.capital - 1) * 100;
  const retAt = (id, i) => ((serie(id)[i] || DATA.meta.capital) / DATA.meta.capital - 1) * 100;
  const teIndex = () => !!DATA.series.index;

  const competidors = () => DATA.models.filter((m) => m.competeix);
  const rankingList = () => [...competidors()].sort((a, b) => retPct(b.id) - retPct(a.id));
  const posicioDe = (id) => rankingList().findIndex((m) => m.id === id) + 1;
  const posicioAt = (id, i) => {
    const ordre = [...competidors()].sort((a, b) => (serie(b.id)[i] || 0) - (serie(a.id)[i] || 0));
    return ordre.findIndex((m) => m.id === id) + 1;
  };
  const diffVsIndex = (id) => (teIndex() ? retPct(id) - retPct("index") : null);

  const canvisDe = (id) => (DATA.canvis || []).filter((c) => c.model === id);
  const decisionsDe = (id) => (DATA.decisions && DATA.decisions[id]) || [];
  const informesDe = (id) => (DATA.informes && DATA.informes[id]) || [];

  function ultimMoviment(id) {
    const decs = decisionsDe(id).filter((d) => d.decisio === "reajustar" && d.operacions && d.operacions.length);
    if (!decs.length) return "Encara cap reajust";
    const d = decs[decs.length - 1];
    const op = d.operacions[0];
    const de = op.vendre === "EFECTIU" ? "efectiu" : op.vendre;
    const a = op.comprar === "EFECTIU" ? "efectiu" : op.comprar;
    return `S${d.setmana}: ${de} → ${a}`;
  }

  function millorPitjor(id) {
    const cs = canvisDe(id).filter((c) => ["afegit", "augmentat"].includes(c.accio) && c.impacte != null);
    if (!cs.length) return { millor: null, pitjor: null };
    const ordenats = [...cs].sort((a, b) => b.impacte - a.impacte);
    return { millor: ordenats[0], pitjor: ordenats[ordenats.length - 1] };
  }

  const nomETF = (tk) => tk === "EFECTIU" ? "Efectiu" :
    (window.ALPHA_ETFS[tk] ? window.ALPHA_ETFS[tk].nom : tk);

  const swatch = (color, s) => `<span class="sw" style="--c:${color};width:${s || 10}px;height:${s || 10}px"></span>`;

  // ------------------------------------------------------------------
  //  Enrutador
  // ------------------------------------------------------------------
  function route() {
    if (!DATA) return;
    const h = location.hash.replace(/^#\/?/, "");
    const [nom, param] = h.split("/");
    const vistes = {
      "": viewTauler, informes: viewInformes, canvis: viewCanvis,
      moments: viewMoments, etfs: viewEtfs, biaixos: viewBiaixos,
      apis: viewApis, ia: () => viewIA(param),
    };
    (vistes[nom] || viewTauler)();
    marcarNav(nom);
    pintarEstatFont();
    window.scrollTo({ top: 0 });
  }

  function marcarNav(nom) {
    document.querySelectorAll(".nav a").forEach((a) => {
      const r = a.getAttribute("data-ruta");
      a.classList.toggle("active", r === (nom || ""));
    });
    $("#nav-links").classList.remove("obert");
  }

  function bindNav() {
    $("#nav-burger").onclick = () => $("#nav-links").classList.toggle("obert");
  }

  const VISTA = () => $("#vista");

  /* ==================================================================
     VISTA 1 · TAULER  (la gráfica grande + rànquing)
     ================================================================== */
  function viewTauler() {
    if (!chartState.visible) chartState.visible = DATA.models.map((m) => m.id);

    const compet = competidors();
    const lider = rankingList()[0];
    const idxRet = teIndex() ? retPct("index") : null;
    const baten = teIndex() ? compet.filter((m) => retPct(m.id) > idxRet).length : null;

    VISTA().innerHTML = `
      <section class="hero">
        <div class="hero-cols">
          <div>
            <div class="kicker">TREBALL DE RECERCA · EXPERIMENT EN DIRECTE</div>
            <h1>Pot una intel·ligència<br>artificial batre el mercat?</h1>
            <p class="hero-sub">Cinc IAs gestionen <b>10.000 €</b> cadascuna durant cinc mesos,
            invertint en un univers de <b>${Object.keys(window.ALPHA_ETFS).length} ETFs reals</b>.
            El rival a batre: l'índex <b>S&P 500</b>.</p>
          </div>
          <div class="kpis">
            <div class="kpi"><div class="k-l">Setmana</div><div class="k-v">${DATA.meta.setmanaActual} <span class="k-de">/ ${DATA.meta.setmanes}</span></div></div>
            <div class="kpi"><div class="k-l">Líder actual</div><div class="k-v ambre">${lider ? lider.nom : "—"}</div></div>
            <div class="kpi"><div class="k-l">S&P 500</div><div class="k-v ${idxRet != null ? cls(idxRet) : ""}">${idxRet != null ? pct(idxRet) : "—"}</div></div>
            <div class="kpi"><div class="k-l">Baten l'índex</div><div class="k-v">${baten != null ? `${baten} <span class="k-de">de ${compet.length}</span>` : "—"}</div></div>
          </div>
        </div>
      </section>

      <section class="card chart-card">
        <div class="chart-top">
          <div class="chips" id="chart-chips"></div>
          <div class="chart-controls">
            <div class="seg" id="chart-modes">
              <button data-mode="value" class="${chartState.mode === "value" ? "active" : ""}">€</button>
              <button data-mode="pct" class="${chartState.mode === "pct" ? "active" : ""}">%</button>
            </div>
            <div class="seg" id="chart-ranges"></div>
          </div>
        </div>
        <div class="chart-stage">
          <div id="chart"></div>
          <div class="chart-tooltip" id="chart-tooltip" hidden></div>
        </div>
        <div class="chart-hint">Passa el ratolí per la gràfica · clic a una IA per mostrar-la o amagar-la · doble clic per veure-la sola</div>
      </section>

      <section class="bloc">
        <div class="bloc-head">
          <h2>Rànquing</h2>
          <p>Classificació per rendibilitat acumulada. Clica una IA per veure el seu detall complet.</p>
        </div>
        <div id="ranking"></div>
      </section>

      <section class="bloc">
        <div class="bloc-head bloc-head-link">
          <div><h2>Moments destacats</h2><p>Les jugades que estan marcant el torneig.</p></div>
          <a class="btn-ghost" href="#/moments">Veure'ls tots →</a>
        </div>
        <div class="hl-strip">${(DATA.highlights || []).slice(0, 3).map(hlCard).join("")}</div>
      </section>`;

    pintarChips();
    pintarRangs();
    pintarChart();
    pintarRanking();

    document.querySelectorAll("#chart-modes button").forEach((b) => {
      b.onclick = () => { chartState.mode = b.dataset.mode; viewTauler(); };
    });
  }

  // --- chips de la llegenda (mostrar/amagar sèries) ---
  function pintarChips() {
    const wrap = $("#chart-chips");
    wrap.innerHTML = DATA.models.map((m) => {
      const on = chartState.visible.includes(m.id);
      const r = retPct(m.id);
      const extra = m.isIndex ? "chip-index" : m.isAuthor ? "chip-autor" : "";
      return `<button class="chip ${on ? "on" : ""} ${extra}" data-id="${m.id}" style="--c:${m.color}">
        <span class="chip-dot"></span>${m.nom}
        <span class="chip-val ${cls(r)}">${pct(r)}</span>
      </button>`;
    }).join("");
    wrap.querySelectorAll(".chip").forEach((c) => {
      let t = null;
      c.addEventListener("click", () => {
        clearTimeout(t);
        t = setTimeout(() => {
          const id = c.dataset.id;
          const v = chartState.visible;
          chartState.visible = v.includes(id) ? v.filter((x) => x !== id) : [...v, id];
          if (!chartState.visible.length) chartState.visible = DATA.models.map((m) => m.id);
          pintarChips(); pintarChart();
        }, 180);
      });
      c.addEventListener("dblclick", () => {
        clearTimeout(t);
        const id = c.dataset.id;
        const nomes = chartState.visible.length === 1 && chartState.visible[0] === id;
        chartState.visible = nomes ? DATA.models.map((m) => m.id) : [id];
        pintarChips(); pintarChart();
      });
    });
  }

  // --- botones de rango temporal ---
  // puntsPerSetmana: 5 en la demo (datos diarios), 1 con datos reales (semanales)
  const pps = () => (DATA.meta && DATA.meta.puntsPerSetmana) || 5;
  function pintarRangs() {
    const n = DATA.dies.length;
    const p = pps();
    const rangs = [
      ["1S", Math.max(2, p)], ["1M", Math.round(p * 4.4)], ["3M", Math.round(p * 13)],
      ["6M", Math.round(p * 26)], ["1A", Math.round(p * 52)], ["TOT", Infinity],
    ].filter(([, d]) => d === Infinity || d < n * 1.3);
    $("#chart-ranges").innerHTML = rangs.map(([lab, d]) =>
      `<button data-range="${d}" class="${String(chartState.range) === String(d) ? "active" : ""}">${lab}</button>`).join("");
    document.querySelectorAll("#chart-ranges button").forEach((b) => {
      b.onclick = () => {
        chartState.range = b.dataset.range === "Infinity" ? Infinity : Number(b.dataset.range);
        pintarRangs(); pintarChart();
      };
    });
  }

  function pintarChart() {
    window.AlphaChart.render($("#chart"), {
      dies: DATA.dies,
      series: DATA.series,
      models: DATA.models,
      visible: chartState.visible,
      mode: chartState.mode,
      range: chartState.range,
      capital: DATA.meta.capital,
      focus: chartState.focus,
      height: 470,
      tooltipEl: $("#chart-tooltip"),
      tooltip: (iGlobal, rows) => {
        const dia = DATA.dies[iGlobal];
        const setm = Math.floor(iGlobal / pps()) + 1;
        rows.sort((a, b) => (serie(b.m.id)[iGlobal] || 0) - (serie(a.m.id)[iGlobal] || 0));
        const files = rows.map(({ m }) => {
          const v = serie(m.id)[iGlobal];
          const r = retAt(m.id, iGlobal);
          const dif = teIndex() && !m.isIndex ? r - retAt("index", iGlobal) : null;
          const rank = m.competeix ? `<span class="tt-rank">#${posicioAt(m.id, iGlobal)}</span>` : `<span class="tt-rank tt-rank-off">—</span>`;
          return `<div class="tt-row">
            ${rank}
            <span class="tt-nom">${swatch(m.color, 8)}${m.nom}</span>
            <span class="tt-cel">${euro(v)}</span>
            <span class="tt-cel ${cls(r)}">${pct(r)}</span>
            <span class="tt-cel tt-dif">${dif == null ? "" : pts(dif)}</span>
          </div>`;
        }).join("");
        return `<div class="tt-cap"><b>${fmtData(dia)}</b> · Setmana ${setm}</div>
          <div class="tt-row tt-head"><span class="tt-rank">#</span><span class="tt-nom">Participant</span>
          <span class="tt-cel">Valor</span><span class="tt-cel">Rendib.</span><span class="tt-cel tt-dif">vs S&P</span></div>${files}`;
      },
    });
  }

  // --- rànquing amb targetes ---
  function pintarRanking() {
    const list = rankingList();
    if (teIndex()) {
      // insertamos el índice en su posición por rentabilidad
      const idx = model("index");
      let pos = list.findIndex((m) => retPct(m.id) < retPct("index"));
      if (pos === -1) pos = list.length;
      list.splice(pos, 0, idx);
    }
    const autor = DATA.models.find((m) => m.isAuthor);

    const fila = (m, i, fora) => {
      const r = retPct(m.id);
      const dif = m.isIndex ? null : diffVsIndex(m.id);
      const mp = millorPitjor(m.id);
      const decs = decisionsDe(m.id);
      const reaj = decs.filter((d) => d.decisio === "reajustar").length;
      const esLider = !fora && !m.isIndex && i === 0;
      return `<div class="rk ${m.isIndex ? "rk-index" : ""} ${esLider ? "rk-lider" : ""} ${fora ? "rk-fora" : ""}" data-id="${m.id}">
        <div class="rk-pos">${fora ? "·" : m.isIndex ? "—" : `<b>${i + 1}</b>`}</div>
        <div class="rk-qui">
          ${swatch(m.color, 12)}
          <div>
            <div class="rk-nom">${m.nom} ${esLider ? '<span class="tag tag-lider">LÍDER</span>' : ""}${m.isIndex ? '<span class="tag tag-index">EL RIVAL</span>' : ""}${fora ? '<span class="tag">FORA DE CONCURS</span>' : ""}</div>
            <div class="rk-sub">${m.empresa}${m.estrategia && !m.isIndex ? ` · ${m.estrategia}` : ""}</div>
          </div>
        </div>
        <div class="rk-spark"><div class="spark" data-spark="${m.id}"></div></div>
        <div class="rk-cel"><div class="rk-l">Capital</div><div class="rk-v">${euro(lastVal(m.id))}</div></div>
        <div class="rk-cel"><div class="rk-l">Rendibilitat</div><div class="rk-v ${cls(r)}">${r >= 0 ? "▲" : "▼"} ${pct(r)}</div></div>
        <div class="rk-cel"><div class="rk-l">vs S&P 500</div><div class="rk-v ${dif == null ? "" : cls(dif)}">${dif == null ? "—" : pts(dif)}</div></div>
        ${m.isIndex ? '<div class="rk-cel rk-ample"><div class="rk-l">Estratègia</div><div class="rk-v-s">Comprar i no tocar res</div></div>' : `
        <div class="rk-cel"><div class="rk-l">Millor jugada</div><div class="rk-v-s ${mp.millor ? "pos" : ""}">${mp.millor ? `${mp.millor.ticker} ${pct(mp.millor.impacte)}` : "—"}</div></div>
        <div class="rk-cel"><div class="rk-l">Pitjor jugada</div><div class="rk-v-s ${mp.pitjor ? "neg" : ""}">${mp.pitjor ? `${mp.pitjor.ticker} ${pct(mp.pitjor.impacte)}` : "—"}</div></div>
        <div class="rk-cel rk-ample"><div class="rk-l">Últim moviment · ${reaj} reajustos</div><div class="rk-v-s">${ultimMoviment(m.id)}</div></div>`}
      </div>`;
    };

    let html = list.map((m, i) => fila(m, i, false)).join("");
    if (autor) html += fila(autor, -1, true);
    $("#ranking").innerHTML = html;

    // sparklines (últim mes)
    document.querySelectorAll(".spark").forEach((el) => {
      const id = el.dataset.spark;
      window.AlphaChart.render(el, {
        dies: DATA.dies, series: DATA.series, models: DATA.models,
        visible: [id], mode: "value", range: Math.round(pps() * 4.4),
        capital: DATA.meta.capital,
        small: true, width: 220, height: 56,
      });
    });

    document.querySelectorAll(".rk").forEach((row) => {
      const id = row.dataset.id;
      row.addEventListener("mouseenter", () => { chartState.focus = id; pintarChart(); });
      row.addEventListener("mouseleave", () => { chartState.focus = null; pintarChart(); });
      if (!model(id).isIndex) row.addEventListener("click", () => { location.hash = "#/ia/" + id; });
    });
  }

  function hlCard(h) {
    const m = model(h.model);
    return `<div class="hl" style="--c:${m.color}">
      <div class="hl-top">${swatch(m.color, 9)}<b>${m.nom}</b><span class="hl-set">SETMANA ${h.setmana}</span></div>
      <div class="hl-titol">${h.titol}</div>
      <div class="hl-text">${h.text}</div>
    </div>`;
  }

  /* ==================================================================
     VISTA 2 · INFORMES SETMANALS
     ================================================================== */
  function viewInformes() {
    const ids = Object.keys(DATA.informes || {});
    if (!ids.length) {
      VISTA().innerHTML = capçaleraVista("Informes setmanals",
        "Encara no hi ha informes: apareixeran aquí quan el torneig arranqui.") + "";
      return;
    }
    VISTA().innerHTML = `
      ${capçaleraVista("Informes setmanals", "El raonament complet de cada IA, setmana a setmana: què ha comprat, què ha venut, per què, quins riscos veia i com li va sortir.")}
      <div class="filtres" id="inf-filtres"></div>
      <div id="inf-llista"></div>`;
    pintarFiltresInformes();
    pintarInformes();
  }

  function pintarFiltresInformes() {
    const compet = DATA.models.filter((m) => !m.isIndex && DATA.informes[m.id]);
    $("#inf-filtres").innerHTML =
      `<button class="chip ${informesFiltre === "tots" ? "on" : ""}" data-f="tots" style="--c:var(--ambre)"><span class="chip-dot"></span>Totes les IAs</button>` +
      compet.map((m) => `<button class="chip ${informesFiltre === m.id ? "on" : ""}" data-f="${m.id}" style="--c:${m.color}"><span class="chip-dot"></span>${m.nom}</button>`).join("");
    document.querySelectorAll("#inf-filtres .chip").forEach((c) => {
      c.onclick = () => { informesFiltre = c.dataset.f; pintarFiltresInformes(); pintarInformes(); };
    });
  }

  function pintarInformes() {
    const ids = informesFiltre === "tots"
      ? DATA.models.filter((m) => !m.isIndex && DATA.informes[m.id]).map((m) => m.id)
      : [informesFiltre];
    let tots = [];
    ids.forEach((id) => informesDe(id).forEach((inf) => tots.push({ id, inf })));
    tots.sort((a, b) => b.inf.setmana - a.inf.setmana);
    if (informesFiltre === "tots") tots = tots.slice(0, 30);

    $("#inf-llista").innerHTML = tots.map(({ id, inf }) => {
      const m = model(id);
      const llista = (arr) => arr && arr.length
        ? arr.map((t) => `<span class="mini-tk">${t}</span>`).join("") : '<span class="buit">—</span>';
      return `<article class="card informe" style="--c:${m.color}">
        <header class="inf-cap">
          <div class="inf-qui">${swatch(m.color, 11)}<b>${m.nom}</b><span class="inf-data">Setmana ${inf.setmana} · ${fmtData(inf.data)}</span></div>
          <div class="inf-tags">
            <span class="tag ${inf.decisio === "reajustar" ? "tag-reajust" : "tag-mante"}">${inf.decisio}</span>
            <span class="tag">risc ${inf.nivell_risc}</span>
            <span class="tag">confiança ${inf.confianca}/10</span>
          </div>
        </header>
        <p class="inf-just">«${inf.justificacio}»</p>
        <div class="inf-grid">
          <div><div class="inf-l">Comprats</div><div>${llista(inf.comprats)}</div></div>
          <div><div class="inf-l">Venuts</div><div>${llista(inf.venuts)}</div></div>
          <div><div class="inf-l">Mantinguts</div><div class="inf-mant">${llista(inf.mantinguts)}</div></div>
        </div>
        <div class="inf-grid inf-grid-text">
          <div><div class="inf-l">Context de mercat</div><div class="inf-t">${inf.context || "—"}</div></div>
          <div><div class="inf-l">Riscos detectats</div><div class="inf-t">${inf.riscos || "—"}</div></div>
          <div><div class="inf-l">Expectativa</div><div class="inf-t">${inf.expectativa || "—"}</div></div>
        </div>
        <footer class="inf-peu">
          Resultat una setmana després:
          ${inf.resultat == null ? '<b class="buit">encara sense dades</b>' : `<b class="${cls(inf.resultat)}">${pct(inf.resultat)}</b> de la cartera`}
        </footer>
      </article>`;
    }).join("") || '<p class="buit-gran">Cap informe encara.</p>';
  }

  /* ==================================================================
     VISTA 3 · CANVIS DE CARTERA
     ================================================================== */
  function viewCanvis() {
    VISTA().innerHTML = `
      ${capçaleraVista("Canvis de cartera", "Cada moviment de cada IA: què ha entrat, què ha sortit, amb quin pes i amb quin resultat dues setmanes després.")}
      <div class="filtres" id="cv-filtres"></div>
      <div id="cv-llista"></div>`;
    pintarFiltresCanvis();
    pintarCanvis();
  }

  function pintarFiltresCanvis() {
    const compet = DATA.models.filter((m) => !m.isIndex && canvisDe(m.id).length);
    $("#cv-filtres").innerHTML =
      `<button class="chip ${canvisFiltre === "tots" ? "on" : ""}" data-f="tots" style="--c:var(--ambre)"><span class="chip-dot"></span>Totes</button>` +
      compet.map((m) => `<button class="chip ${canvisFiltre === m.id ? "on" : ""}" data-f="${m.id}" style="--c:${m.color}"><span class="chip-dot"></span>${m.nom} <span class="chip-val">${canvisDe(m.id).length}</span></button>`).join("");
    document.querySelectorAll("#cv-filtres .chip").forEach((c) => {
      c.onclick = () => { canvisFiltre = c.dataset.f; pintarFiltresCanvis(); pintarCanvis(); };
    });
  }

  function pintarCanvis() {
    let llista = DATA.canvis || [];
    if (canvisFiltre !== "tots") llista = llista.filter((c) => c.model === canvisFiltre);
    if (!llista.length) {
      $("#cv-llista").innerHTML = '<p class="buit-gran">Encara no hi ha canvis de cartera registrats.</p>';
      return;
    }
    // agrupar por (model, setmana) para enseñar el movimiento completo
    const grups = [];
    const clau = {};
    llista.forEach((c) => {
      const k = c.model + "·" + c.setmana;
      if (!clau[k]) { clau[k] = { model: c.model, setmana: c.setmana, data: c.data, motiu: c.motiu, items: [] }; grups.push(clau[k]); }
      clau[k].items.push(c);
    });
    grups.sort((a, b) => b.setmana - a.setmana);

    $("#cv-llista").innerHTML = grups.map((g) => {
      const m = model(g.model);
      const files = g.items.map((c) => {
        const colorAccio = { afegit: "pos", augmentat: "pos", "reduït": "neg", eliminat: "neg" }[c.accio] || "";
        // con datos reales el motor aún no guarda pesos históricos → enseñamos el importe
        const tePesos = c.pesAbans != null && c.pesDespres != null;
        const pes = tePesos
          ? `<div class="cv-barres">
              <div class="cv-bar"><span style="width:${(c.pesAbans / 40) * 100}%"></span><i>${c.pesAbans}%</i></div>
              <div class="cv-fletxa">→</div>
              <div class="cv-bar cv-bar-nou"><span style="width:${(c.pesDespres / 40) * 100}%;background:${m.color}"></span><i>${c.pesDespres}%</i></div>
            </div>`
          : `<div class="cv-import">Import del moviment: <b>${c.import != null ? euro(c.import) : "—"}</b></div>`;
        return `<div class="cv-fila">
          <div class="cv-tk"><b>${c.ticker}</b><span>${nomETF(c.ticker)}</span></div>
          <div class="cv-accio ${colorAccio}">${c.accio.toUpperCase()}</div>
          <div class="cv-pes">${pes}</div>
          <div class="cv-imp ${c.impacte != null ? cls(c.impacte) : ""}">${c.impacte != null ? pct(c.impacte) : "—"}<span>en 2 setm.</span></div>
        </div>`;
      }).join("");
      return `<article class="card canvi" style="--c:${m.color}">
        <header class="inf-cap">
          <div class="inf-qui">${swatch(m.color, 11)}<b>${m.nom}</b><span class="inf-data">Setmana ${g.setmana} · ${fmtData(g.data)}</span></div>
          <a class="btn-ghost btn-mini" href="#/ia/${g.model}">Veure la IA →</a>
        </header>
        ${files}
        <p class="cv-motiu">«${g.motiu}»</p>
      </article>`;
    }).join("");
  }

  /* ==================================================================
     VISTA 4 · MOMENTS DESTACATS
     ================================================================== */
  function viewMoments() {
    VISTA().innerHTML = `
      ${capçaleraVista("Moments destacats", "Frases i jugades que resumeixen el caràcter de cada IA. Material de primera per a l'anàlisi de biaixos del TR.")}
      <div class="hl-grid">${(DATA.highlights || []).map(hlCard).join("") || '<p class="buit-gran">Encara cap moment destacat.</p>'}</div>`;
  }

  /* ==================================================================
     VISTA 5 · UNIVERS D'ETFs
     ================================================================== */
  function viewEtfs() {
    VISTA().innerHTML = `
      ${capçaleraVista("Univers d'inversió", `Els ${Object.keys(window.ALPHA_ETFS).length} fons cotitzats (ETFs) on les IAs poden invertir. Llista tancada: cap IA pot comprar res de fora.`)}
      <div class="etf-eines">
        <input id="etf-cerca" type="search" placeholder="Cerca per nom o ticker… (p. ex. «or», SMH)" value="${etfState.cerca}">
        <div class="filtres" id="etf-cats"></div>
      </div>
      <div id="etf-grid" class="etf-grid"></div>
      <div class="etf-modal" id="etf-modal" hidden></div>`;
    pintarCatsETF();
    pintarETFs();
    $("#etf-cerca").addEventListener("input", (e) => { etfState.cerca = e.target.value; pintarETFs(); });
  }

  function pintarCatsETF() {
    const cats = ["Totes", ...window.ALPHA_CATEGORIES];
    $("#etf-cats").innerHTML = cats.map((c) =>
      `<button class="chip chip-cat ${etfState.cat === c ? "on" : ""}" data-c="${c}"><span class="chip-dot"></span>${c}</button>`).join("");
    document.querySelectorAll(".chip-cat").forEach((b) => {
      b.onclick = () => { etfState.cat = b.dataset.c; pintarCatsETF(); pintarETFs(); };
    });
  }

  function tenedors(tk) {
    // qué IAs tienen este ETF ahora mismo en cartera
    return DATA.models.filter((m) => !m.isIndex &&
      (DATA.carteres[m.id] || []).some((h) => h.ticker === tk && h.pes > 0));
  }

  function pintarETFs() {
    const cerca = etfState.cerca.trim().toLowerCase();
    const entrades = Object.entries(window.ALPHA_ETFS).filter(([tk, e]) => {
      if (etfState.cat !== "Totes" && e.cat !== etfState.cat) return false;
      if (!cerca) return true;
      return tk.toLowerCase().includes(cerca) || e.nom.toLowerCase().includes(cerca) ||
        e.cat.toLowerCase().includes(cerca) || e.desc.toLowerCase().includes(cerca);
    });
    $("#etf-grid").innerHTML = entrades.map(([tk, e]) => {
      const art = window.ALPHA_ART[e.art] || window.ALPHA_ART.generic;
      const qui = tenedors(tk);
      return `<div class="etf" data-tk="${tk}">
        <div class="etf-art">${art()}
          <span class="etf-cat">${e.cat}</span>
          <span class="etf-tk">${tk}</span>
        </div>
        <div class="etf-cos">
          <div class="etf-nom">${e.nom}</div>
          <div class="etf-desc">${e.desc}</div>
          <div class="etf-peu">
            <span class="etf-risc" title="Nivell de risc ${e.risc} de 5">${"●".repeat(e.risc)}${"○".repeat(5 - e.risc)}</span>
            <span class="etf-qui">${qui.map((m) => swatch(m.color, 8)).join("")}</span>
            <button class="btn-ghost btn-mini">Detalls</button>
          </div>
        </div>
      </div>`;
    }).join("") || '<p class="buit-gran">Cap ETF coincideix amb la cerca.</p>';

    document.querySelectorAll(".etf").forEach((el) => {
      el.onclick = () => obrirModalETF(el.dataset.tk);
    });
  }

  function obrirModalETF(tk) {
    const e = window.ALPHA_ETFS[tk];
    const art = window.ALPHA_ART[e.art] || window.ALPHA_ART.generic;
    const qui = tenedors(tk).map((m) => {
      const h = (DATA.carteres[m.id] || []).find((x) => x.ticker === tk);
      return `<div class="mod-tenedor">${swatch(m.color, 10)}<b>${m.nom}</b><span>${h.pes}% de la cartera · ${euro(h.valor)}</span></div>`;
    }).join("");
    const modal = $("#etf-modal");
    modal.hidden = false;
    modal.innerHTML = `<div class="mod-fons"></div>
      <div class="mod-caixa">
        <div class="mod-art">${art()}</div>
        <div class="mod-cos">
          <div class="mod-cap"><span class="etf-tk-gran">${tk}</span><span class="tag">${e.cat}</span>
            <span class="etf-risc">risc ${"●".repeat(e.risc)}${"○".repeat(5 - e.risc)}</span></div>
          <h3>${e.nom}</h3>
          <p>${e.desc}</p>
          <div class="inf-l" style="margin-top:14px">Qui el té ara en cartera</div>
          ${qui || '<p class="buit">Cap IA el té en cartera ara mateix.</p>'}
          <div class="mod-peu">Ticker de Yahoo Finance: <code>${tk}</code> · Els preus reals els baixa el motor cada dilluns.</div>
          <button class="btn-ghost" id="mod-tancar">Tancar ✕</button>
        </div>
      </div>`;
    $("#mod-tancar").onclick = () => { modal.hidden = true; };
    modal.querySelector(".mod-fons").onclick = () => { modal.hidden = true; };
  }

  /* ==================================================================
     VISTA 6 · DETALL D'UNA IA
     ================================================================== */
  function viewIA(id) {
    const m = model(id) || DATA.models.find((x) => !x.isIndex);
    if (!m) { viewTauler(); return; }
    id = m.id;
    const r = retPct(id);
    const dif = diffVsIndex(id);
    const decs = decisionsDe(id);
    const reaj = decs.filter((d) => d.decisio === "reajustar").length;
    const confMitja = decs.length ? decs.reduce((s, d) => s + d.confianca, 0) / decs.length : 0;
    const cart = DATA.carteres[id] || [];
    const mp = millorPitjor(id);
    const altres = DATA.models.filter((x) => !x.isIndex);

    VISTA().innerHTML = `
      <div class="ia-nav">
        ${altres.map((x) => `<a class="chip ${x.id === id ? "on" : ""}" href="#/ia/${x.id}" style="--c:${x.color}"><span class="chip-dot"></span>${x.nom}</a>`).join("")}
      </div>

      <section class="card ia-cap" style="--c:${m.color}">
        <div class="ia-id">
          <div class="ia-avatar" style="background:${m.color}"></div>
          <div>
            <h1>${m.nom} ${m.isAuthor ? '<span class="tag">FORA DE CONCURS</span>' : `<span class="tag tag-lider">#${posicioDe(id)} DEL RÀNQUING</span>`}</h1>
            <div class="rk-sub">${m.empresa} · ${m.pais} · Estratègia: <b>${m.estrategia || "—"}</b></div>
            <p class="ia-perfil">${m.perfil || ""}</p>
          </div>
        </div>
        <div class="kpis kpis-ia">
          <div class="kpi"><div class="k-l">Capital inicial</div><div class="k-v">${euro(DATA.meta.capital)}</div></div>
          <div class="kpi"><div class="k-l">Capital actual</div><div class="k-v">${euro(lastVal(id))}</div></div>
          <div class="kpi"><div class="k-l">Rendibilitat</div><div class="k-v ${cls(r)}">${pct(r)}</div></div>
          <div class="kpi"><div class="k-l">vs S&P 500</div><div class="k-v ${dif == null ? "" : cls(dif)}">${dif == null ? "—" : pts(dif)}</div></div>
          <div class="kpi"><div class="k-l">Reajustos</div><div class="k-v">${reaj} <span class="k-de">/ ${decs.length} setm.</span></div></div>
          <div class="kpi"><div class="k-l">Confiança mitjana</div><div class="k-v">${dec1(confMitja)} <span class="k-de">/ 10</span></div></div>
        </div>
      </section>

      <section class="card">
        <h2 class="h-card">Evolució ${teIndex() ? "contra el S&P 500" : ""}</h2>
        <div class="chart-stage chart-stage-ia">
          <div id="ia-chart"></div>
          <div class="chart-tooltip" id="ia-tooltip" hidden></div>
        </div>
      </section>

      <div class="ia-2col">
        <section class="card">
          <h2 class="h-card">Cartera actual</h2>
          ${cart.length ? cart.map((h) => `
            <div class="hold">
              <div class="hold-top">
                <span class="hold-nom"><b>${h.ticker === "EFECTIU" ? "💶 Efectiu" : h.ticker}</b> ${h.ticker === "EFECTIU" ? "" : "· " + nomETF(h.ticker)}</span>
                <span class="hold-xifres">${h.pes}% · ${euro(h.valor)}</span>
              </div>
              <div class="hold-bar"><span style="width:${(h.pes / 40) * 100}%;background:${h.ticker === "EFECTIU" ? "var(--apagat)" : m.color}"></span></div>
            </div>`).join("")
          : '<p class="buit">Encara no hi ha dades de cartera (el motor les escriurà a dades/carteres.csv).</p>'}
          <div class="hold-nota">La barra plena = límit del 40% per ETF.</div>
        </section>

        <section class="card">
          <h2 class="h-card">Fortaleses i febleses</h2>
          <div class="ff">
            <div><div class="inf-l pos">Fortaleses</div><ul>${(m.fortaleses || []).map((f) => `<li>${f}</li>`).join("") || "<li>—</li>"}</ul></div>
            <div><div class="inf-l neg">Febleses</div><ul>${(m.febleses || []).map((f) => `<li>${f}</li>`).join("") || "<li>—</li>"}</ul></div>
          </div>
          <h2 class="h-card" style="margin-top:20px">Millor i pitjor jugada</h2>
          ${mp.millor ? `
            <div class="jugada"><span class="tag tag-mante">MILLOR</span><b>${mp.millor.ticker}</b> ${mp.millor.accio} (S${mp.millor.setmana}) <span class="pos">${pct(mp.millor.impacte)}</span></div>
            <div class="jugada"><span class="tag tag-reajust">PITJOR</span><b>${mp.pitjor.ticker}</b> ${mp.pitjor.accio} (S${mp.pitjor.setmana}) <span class="neg">${pct(mp.pitjor.impacte)}</span></div>`
          : '<p class="buit">Encara sense prou moviments.</p>'}
        </section>
      </div>

      <section class="card">
        <div class="bloc-head-link">
          <h2 class="h-card">Historial de decisions</h2>
          <a class="btn-ghost btn-mini" href="#/informes">Veure informes complets →</a>
        </div>
        <div class="timeline">
          ${[...decs].reverse().map((d) => `
            <div class="tl">
              <div class="tl-cap">
                <span class="tl-set">S${d.setmana} · ${fmtData(d.data)}</span>
                <span class="tag ${d.decisio === "reajustar" ? "tag-reajust" : "tag-mante"}">${d.decisio}</span>
                <span class="tag">risc ${d.nivell_risc}</span>
                <span class="tag">confiança ${d.confianca}/10</span>
                <span class="tl-val">${euro(d.valor_cartera)} <i class="${cls(d.rend_setmana)}">${pct(d.rend_setmana)}</i></span>
              </div>
              <div class="tl-text">«${d.justificacio}»</div>
              ${d.operacions && d.operacions.length ? `<div class="tl-ops">${d.operacions.map((o) =>
                `<code>${o.vendre === "EFECTIU" ? "efectiu" : o.vendre} → ${o.comprar === "EFECTIU" ? "efectiu" : o.comprar} (${euro(o.import)})</code>`).join(" ")}</div>` : ""}
            </div>`).join("")}
        </div>
      </section>`;

    // gráfica individual: la IA vs el índice
    window.AlphaChart.render($("#ia-chart"), {
      dies: DATA.dies, series: DATA.series, models: DATA.models,
      visible: teIndex() ? [id, "index"] : [id],
      mode: "value", range: Infinity, capital: DATA.meta.capital,
      height: 330, tooltipEl: $("#ia-tooltip"),
      tooltip: (iGlobal, rows) => {
        const files = rows.sort((a, b) => (serie(b.m.id)[iGlobal] || 0) - (serie(a.m.id)[iGlobal] || 0))
          .map(({ m: mm }) => {
            const v = serie(mm.id)[iGlobal]; const rr = retAt(mm.id, iGlobal);
            return `<div class="tt-row"><span class="tt-nom">${swatch(mm.color, 8)}${mm.nom}</span>
              <span class="tt-cel">${euro(v)}</span><span class="tt-cel ${cls(rr)}">${pct(rr)}</span></div>`;
          }).join("");
        return `<div class="tt-cap"><b>${fmtData(DATA.dies[iGlobal])}</b></div>${files}`;
      },
    });
  }

  /* ==================================================================
     VISTA 7 · BIAIXOS CONDUCTUALS
     ================================================================== */
  function viewBiaixos() {
    const comp = competidors();
    const metrica = {};
    comp.forEach((m) => {
      const d = decisionsDe(m.id);
      const reaj = d.filter((x) => x.decisio === "reajustar").length;
      const confMitja = d.length ? d.reduce((s, x) => s + x.confianca, 0) / d.length : 0;
      const perdudes = d.filter((x) => x.rend_setmana < 0);
      const confEnPerdues = perdudes.length ? perdudes.reduce((s, x) => s + x.confianca, 0) / perdudes.length : 0;
      // "efecte disposició": reajusta just després d'una setmana en negatiu
      const veneEnVermell = d.filter((x, i) => i > 0 && d[i - 1].rend_setmana < 0 && x.decisio === "reajustar").length;
      metrica[m.id] = { reaj, total: d.length, confMitja, confEnPerdues, veneEnVermell };
    });

    const targetes = [
      { t: "Sobreoperació", q: "Qui opera de més? Cada operació costa un 0,1%. La hipòtesi del TR: l'excés d'activitat no compensa.",
        f: (id) => metrica[id].reaj, fmt: (v) => `${v} reajustos`,
        peu: (top, baix) => `<b>${top.nom}</b> és qui més mou la cartera; <b>${baix.nom}</b>, qui menys la toca.` },
      { t: "Excés de confiança", q: "Quina IA es mostra més segura justament les setmanes en què acaba perdent diners?",
        f: (id) => metrica[id].confEnPerdues, fmt: (v) => `${dec1(v)}/10`,
        peu: (top) => `<b>${top.nom}</b> manté la confiança més alta fins i tot en setmanes de pèrdues: el biaix més humà de tots.` },
      { t: "Reacció a les pèrdues", q: "Qui reajusta la cartera just després d'una setmana en vermell? (possible pànic o efecte disposició)",
        f: (id) => metrica[id].veneEnVermell, fmt: (v) => `${v} cops`,
        peu: (top) => `<b>${top.nom}</b> és qui més sovint mou fitxa immediatament després de perdre.` },
      { t: "Confiança mitjana", q: "Com de segures es mostren en general (d'1 a 10)? Més confiança no vol dir més encert.",
        f: (id) => metrica[id].confMitja, fmt: (v) => `${dec1(v)}/10`,
        peu: (top) => `<b>${top.nom}</b> és la IA que es declara més segura del torneig.` },
    ];

    VISTA().innerHTML = `
      ${capçaleraVista("Anàlisi de biaixos conductuals", "Mostren les IAs els mateixos biaixos que els inversors humans? Pànic, sobreoperació, excés de confiança… Economia conductual, en la línia de Kahneman.")}
      <div class="bias-grid">
        ${targetes.map((c) => {
          const files = comp.map((m) => ({ m, v: c.f(m.id) })).sort((a, b) => b.v - a.v);
          const maxv = Math.max(...files.map((x) => x.v), 0.001);
          return `<div class="card bias">
            <h3>${c.t}</h3><p class="bias-q">${c.q}</p>
            ${files.map(({ m, v }) => `
              <div class="bias-fila">
                <span class="bias-nom">${swatch(m.color, 9)}${m.nom}</span>
                <span class="bias-val">${c.fmt(v)}</span>
                <span class="bias-bar"><span style="width:${(v / maxv) * 100}%;background:${m.color}"></span></span>
              </div>`).join("")}
            <p class="bias-peu">${c.peu(files[0].m, files[files.length - 1].m)}</p>
          </div>`;
        }).join("")}
      </div>`;
  }

  /* ==================================================================
     VISTA 8 · CONFIGURACIÓ D'APIs
     ================================================================== */
  function viewApis() {
    const apis = DATA.apis || { ia: [], financeres: [] };
    const estatTag = (e) => e === "connectada" || e === "operativa"
      ? `<span class="tag tag-mante">● ${e}</span>`
      : e === "error" ? `<span class="tag tag-reajust">● error</span>`
      : `<span class="tag tag-pendent">● pendent</span>`;

    VISTA().innerHTML = `
      ${capçaleraVista("Configuració d'APIs", "L'estat de cada connexió del sistema. Les claus NO s'introdueixen mai en aquesta web: es guarden al fitxer secrets.txt del motor (o als Secrets de GitHub), fora de l'abast del navegador.")}

      <div class="api-avis card">
        <b>Com connectar una IA (3 passos):</b>
        <ol>
          <li>Crea la clau al web del proveïdor (enllaç «Aconseguir clau» de cada targeta).</li>
          <li>Copia-la a <code>secrets.txt</code> (fes servir <code>secrets.example.txt</code> de plantilla) o als Secrets de GitHub.</li>
          <li>A <code>config.py</code>, posa <code>actiu: True</code> al model. A la propera ronda, la IA entra al torneig.</li>
        </ol>
      </div>

      <h2 class="h-seccio">Intel·ligències artificials</h2>
      <div class="api-grid">
        ${apis.ia.map((a) => {
          const m = model(a.id) || {};
          return `<div class="card api" style="--c:${m.color || "var(--ambre)"}">
            <div class="api-cap">${swatch(m.color || "#888", 11)}<b>${m.nom || a.id}</b>${estatTag(a.estat)}</div>
            <div class="api-fila"><span>Proveïdor</span><b>${a.proveidor}</b></div>
            <div class="api-fila"><span>Model</span><code>${a.model_api}</code></div>
            <div class="api-fila"><span>Clau necessària</span><code>${a.variable}</code></div>
            <div class="api-fila"><span>Última execució</span><b>${a.ultimaExecucio || "—"}</b></div>
            <div class="api-fila api-brief"><span>Últim briefing</span><b>${a.ultimBriefing ? `«${a.ultimBriefing}»` : "—"}</b></div>
            <a class="btn-ghost btn-mini" href="${a.url_consola}" target="_blank" rel="noopener">Aconseguir clau ↗</a>
          </div>`;
        }).join("")}
      </div>

      <h2 class="h-seccio">APIs financeres</h2>
      <div class="api-grid">
        ${apis.financeres.map((a) => `
          <div class="card api">
            <div class="api-cap"><b>${a.nom}</b>${estatTag(a.estat)}</div>
            <div class="api-fila"><span>Per a què serveix</span><b>${a.us}</b></div>
            <p class="api-detall">${a.detall}</p>
          </div>`).join("")}
      </div>

      <div class="api-avis card">
        <b>Arquitectura de les dades (per què la web sempre funciona):</b>
        <p>El motor (<code>torneo.py</code>) baixa preus reals amb yfinance cada dilluns, pregunta a les IAs i ho guarda tot en CSV
        a la carpeta <code>dades/</code>. Després, <code>generar_web.py</code> converteix aquest historial en <code>dades.json</code>,
        que aquesta web llegeix i refresca automàticament cada minut. Si cap API externa falla, la web continua mostrant
        l'última foto vàlida del torneig — mai es queda en blanc.</p>
      </div>`;
  }

  // ------------------------------------------------------------------
  //  Piezas comunes
  // ------------------------------------------------------------------
  function capçaleraVista(titol, sub) {
    return `<section class="bloc-head bloc-head-vista"><h1>${titol}</h1><p>${sub}</p></section>`;
  }

  // Arranque
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
