/* =====================================================================
   ALPHA ARTIFICIAL — etfs.js
   ---------------------------------------------------------------------
   Univers d'inversió complet (espejo de config.py → UNIVERS_ETFS).
   Cada ETF: nom, categoria, descripció breu, risc (1-5) i clau d'art.
   Si cambias la lista en config.py, actualízala también aquí.
   ===================================================================== */
(function () {
  "use strict";

  // Orden de las categorías tal como se muestran en la galería
  window.ALPHA_CATEGORIES = [
    "Índexs principals",
    "Tecnologia",
    "IA i semiconductors",
    "Energia",
    "Salut",
    "Renda fixa",
    "Mercats internacionals",
    "Matèries primeres",
    "Metalls preciosos",
    "Immobiliari",
    "Dividends",
    "Defensius",
    "Sectors EUA",
  ];

  // d = definición compacta: [nom, categoria, art, risc, descripció]
  const d = (nom, cat, art, risc, desc) => ({ nom, cat, art, risc, desc });

  window.ALPHA_ETFS = {
    // ── Índexs principals ──────────────────────────────────────────
    SPY:  d("S&P 500 (SPDR)", "Índexs principals", "usa", 3, "Les 500 empreses més grans dels EUA. La referència mundial i el rival a batre del torneig."),
    VOO:  d("S&P 500 (Vanguard)", "Índexs principals", "usa", 3, "El mateix S&P 500 amb comissions mínimes. Gestió passiva pura."),
    IVV:  d("S&P 500 (iShares Core)", "Índexs principals", "usa", 3, "Tercera gran porta d'entrada al S&P 500, de la casa iShares."),
    VTI:  d("Mercat total EUA", "Índexs principals", "usa", 3, "Tota la borsa americana en un sol fons: grans, mitjanes i petites empreses."),
    QQQ:  d("Nasdaq 100", "Índexs principals", "tech", 4, "Les 100 grans del Nasdaq. Molt pes de tecnologia: puja i baixa amb força."),
    DIA:  d("Dow Jones Industrial", "Índexs principals", "usa", 3, "Les 30 empreses clàssiques de la borsa americana. L'índex més antic."),
    IWM:  d("Russell 2000 (small caps)", "Índexs principals", "smallcaps", 4, "2.000 empreses petites dels EUA. Més potencial, més sotracs."),
    RSP:  d("S&P 500 equiponderat", "Índexs principals", "usa", 3, "El S&P 500 donant el mateix pes a totes les empreses, no només a les gegants."),
    VT:   d("Mercat mundial total", "Índexs principals", "world", 3, "Tot el món en un sol ETF: més de 9.000 empreses de tots els continents."),
    ACWI: d("Món desenvolupat i emergent", "Índexs principals", "world", 3, "Índex MSCI ACWI: combina països desenvolupats i emergents."),

    // ── Tecnologia ─────────────────────────────────────────────────
    XLK:  d("Tecnologia EUA (S&P)", "Tecnologia", "tech", 4, "El sector tecnològic del S&P 500: Apple, Microsoft, Nvidia i companyia."),
    VGT:  d("Tecnologia (Vanguard)", "Tecnologia", "tech", 4, "Versió àmplia del sector tecnològic americà, amb més de 300 empreses."),
    IGV:  d("Programari EUA", "Tecnologia", "tech", 4, "Empreses de software i aplicacions: el negoci de vendre codi."),
    FDN:  d("Internet EUA", "Tecnologia", "tech", 4, "Els grans negocis d'internet: comerç, xarxes i serveis en línia."),
    SKYY: d("Computació al núvol", "Tecnologia", "cloud", 4, "Empreses del 'cloud': servidors i serveis on viu la informàtica moderna."),
    CIBR: d("Ciberseguretat", "Tecnologia", "cyber", 4, "Els guardians digitals: empreses que protegeixen xarxes i dades."),
    ARKK: d("Innovació disruptiva (ARK)", "Tecnologia", "tech", 5, "Aposta agressiva per empreses que volen canviar-ho tot. Molt volàtil."),

    // ── IA i semiconductors ────────────────────────────────────────
    SMH:  d("Semiconductors (VanEck)", "IA i semiconductors", "ai", 5, "Els fabricants de xips que alimenten la revolució de la IA."),
    SOXX: d("Semiconductors (iShares)", "IA i semiconductors", "ai", 5, "L'altre gran ETF de xips: Nvidia, AMD, TSMC, Broadcom..."),
    BOTZ: d("Robòtica i IA (Global X)", "IA i semiconductors", "ai", 4, "Robots industrials, automatització i intel·ligència artificial global."),
    ROBO: d("Robòtica i automatització", "IA i semiconductors", "ai", 4, "Pioner en robòtica: de fàbriques intel·ligents a cirurgia robòtica."),
    AIQ:  d("Intel·ligència artificial", "IA i semiconductors", "ai", 4, "Empreses que desenvolupen o aprofiten la IA en el seu negoci."),
    IRBO: d("IA i robòtica (iShares)", "IA i semiconductors", "ai", 4, "Aposta diversificada per IA i robòtica amb pesos equilibrats."),
    ARKQ: d("Autonomia i robòtica (ARK)", "IA i semiconductors", "ai", 5, "Vehicles autònoms, drons i robòtica segons la visió d'ARK Invest."),

    // ── Energia ────────────────────────────────────────────────────
    XLE:  d("Energia EUA", "Energia", "energy", 4, "Les grans petrolieres americanes: Exxon, Chevron i companyia."),
    XOP:  d("Exploració de petroli i gas", "Energia", "oil", 5, "Empreses que busquen i extreuen cru. Molt lligat al preu del petroli."),
    OIH:  d("Serveis petroliers", "Energia", "oil", 5, "Els que posen la maquinària: perforació, plataformes i serveis."),
    ICLN: d("Energies netes globals", "Energia", "clean", 4, "Solar, eòlica i renovables d'arreu del món en un sol fons."),
    TAN:  d("Energia solar", "Energia", "solar", 5, "Fabricants de plaques i parcs solars. Sensible a tipus d'interès i subvencions."),
    FAN:  d("Energia eòlica", "Energia", "wind", 4, "La força del vent: turbines, parcs eòlics i els seus operadors."),
    URA:  d("Urani i energia nuclear", "Energia", "nuclear", 5, "Mineres d'urani i indústria nuclear. Aposta de nínxol amb molt caràcter."),

    // ── Salut ──────────────────────────────────────────────────────
    XLV:  d("Salut EUA", "Salut", "health", 3, "Farmacèutiques, asseguradores i hospitals del S&P 500. Sector clàssicament defensiu."),
    VHT:  d("Sanitat (Vanguard)", "Salut", "health", 3, "Versió àmplia del sector salut americà, amb centenars d'empreses."),
    IBB:  d("Biotecnologia (Nasdaq)", "Salut", "bio", 5, "Les grans biotecnològiques: recerca de fàrmacs amb risc i recompensa alts."),
    XBI:  d("Biotecnologia (S&P)", "Salut", "bio", 5, "Biotec amb pesos equilibrats: més exposició a empreses petites."),
    IHI:  d("Equipament mèdic", "Salut", "health", 3, "Aparells i dispositius mèdics: de bisturís robòtics a marcapassos."),

    // ── Renda fixa ─────────────────────────────────────────────────
    TLT:  d("Bons EUA 20+ anys", "Renda fixa", "bond", 3, "Deute americà a molt llarg termini. Refugi clàssic, sensible als tipus."),
    IEF:  d("Bons EUA 7-10 anys", "Renda fixa", "bond", 2, "Deute americà a mitjà termini: menys sotracs que el llarg termini."),
    SHY:  d("Bons EUA 1-3 anys", "Renda fixa", "bond", 1, "Deute americà a curt termini. Gairebé com aparcar els diners."),
    BIL:  d("Lletres del Tresor (1-3 mesos)", "Renda fixa", "bond", 1, "El més semblant a l'efectiu que cotitza en borsa."),
    AGG:  d("Bons EUA agregats", "Renda fixa", "bond", 2, "Toda la renda fixa americana de qualitat en un sol fons."),
    BND:  d("Mercat total de bons EUA", "Renda fixa", "bond", 2, "La versió Vanguard del mercat sencer de bons americans."),
    LQD:  d("Bons corporatius de qualitat", "Renda fixa", "corp", 2, "Deute d'empreses sòlides amb grau d'inversió."),
    HYG:  d("Bons d'alt rendiment", "Renda fixa", "corp", 4, "'High yield': paguen més interès perquè tenen més risc d'impagament."),
    TIP:  d("Bons lligats a la inflació", "Renda fixa", "bond", 2, "Bons del Tresor que es revaloren amb la inflació (TIPS)."),
    EMB:  d("Deute de mercats emergents", "Renda fixa", "emerging", 4, "Bons de governs emergents en dòlars: més cupó, més risc país."),
    MUB:  d("Bons municipals EUA", "Renda fixa", "bond", 2, "Deute de ciutats i estats americans, tradicionalment estable."),
    GOVT: d("Bons del Tresor EUA", "Renda fixa", "bond", 2, "Tot el deute públic americà, de curt a llarg termini."),

    // ── Mercats internacionals ─────────────────────────────────────
    VGK:  d("Europa (Vanguard)", "Mercats internacionals", "europe", 3, "Les grans empreses europees: Nestlé, ASML, LVMH, SAP..."),
    EZU:  d("Zona euro", "Mercats internacionals", "europe", 3, "Només països de l'euro: Alemanya, França, Itàlia, Espanya..."),
    EWG:  d("Alemanya", "Mercats internacionals", "europe", 4, "La primera economia europea: indústria, automòbil i química."),
    EWQ:  d("França", "Mercats internacionals", "europe", 4, "Luxe, energia i bancs: el pes pesat francès."),
    EWU:  d("Regne Unit", "Mercats internacionals", "europe", 3, "La borsa de Londres: energia, mineria, bancs i consum."),
    EWJ:  d("Japó", "Mercats internacionals", "japan", 3, "Toyota, Sony i la resta del gegant japonès."),
    MCHI: d("Xina (MSCI)", "Mercats internacionals", "china", 5, "El mercat xinès ampli: tecnologia, consum i indústria."),
    FXI:  d("Xina (grans empreses)", "Mercats internacionals", "china", 5, "Les 50 empreses xineses més grans cotitzades a Hong Kong."),
    EWY:  d("Corea del Sud", "Mercats internacionals", "asia", 4, "Samsung i l'ecosistema tecnològic i industrial coreà."),
    EWT:  d("Taiwan", "Mercats internacionals", "asia", 4, "Dominat per TSMC: el cor mundial de la fabricació de xips."),
    EEM:  d("Mercats emergents (MSCI)", "Mercats internacionals", "emerging", 4, "Xina, Índia, Brasil, Taiwan... el bloc emergent clàssic."),
    VWO:  d("Mercats emergents (Vanguard)", "Mercats internacionals", "emerging", 4, "La versió Vanguard dels emergents, amb comissions més baixes."),
    INDA: d("Índia", "Mercats internacionals", "india", 4, "L'economia gran que més creix del món, en un sol ETF."),
    EWZ:  d("Brasil", "Mercats internacionals", "emerging", 5, "Matèries primeres i bancs: la borsa brasilera, molt volàtil."),
    EWC:  d("Canadà", "Mercats internacionals", "world", 3, "Bancs sòlids i molta energia: el veí tranquil del nord."),

    // ── Matèries primeres ──────────────────────────────────────────
    DBC:  d("Cistella de matèries primeres", "Matèries primeres", "basket", 4, "Petroli, or, blat, coure... una cistella diversificada de 'coses reals'."),
    PDBC: d("Matèries primeres (optimitzat)", "Matèries primeres", "basket", 4, "Cistella similar a DBC amb gestió optimitzada dels contractes."),
    GSG:  d("Índex GSCI de matèries primeres", "Matèries primeres", "basket", 4, "L'índex de matèries primeres més seguit, amb molt pes d'energia."),
    USO:  d("Petroli WTI", "Matèries primeres", "oil", 5, "Segueix el preu del barril americà. Pura aposta pel cru."),
    BNO:  d("Petroli Brent", "Matèries primeres", "oil", 5, "El barril europeu de referència, germà del WTI."),
    UNG:  d("Gas natural", "Matèries primeres", "gas", 5, "El preu del gas natural americà: extremadament mogut."),
    DBA:  d("Agricultura", "Matèries primeres", "agri", 4, "Blat, blat de moro, sucre, cafè... el rebost mundial cotitzat."),
    CPER: d("Coure", "Matèries primeres", "copper", 4, "El metall de l'electrificació: cables, motors i renovables."),
    DBB:  d("Metalls industrials", "Matèries primeres", "copper", 4, "Coure, alumini i zinc: els materials de la indústria global."),

    // ── Metalls preciosos ──────────────────────────────────────────
    GLD:  d("Or físic (SPDR)", "Metalls preciosos", "gold", 3, "El refugi mil·lenari. Lingots reals guardats en càmeres cuirassades."),
    IAU:  d("Or físic (iShares)", "Metalls preciosos", "gold", 3, "Or físic amb comissió més baixa que GLD. Mateix metall, mateix brillo."),
    SGOL: d("Or físic (abrdn)", "Metalls preciosos", "gold", 3, "Or físic custodiat a Suïssa, amb els lingots auditats i numerats."),
    SLV:  d("Plata física (iShares)", "Metalls preciosos", "silver", 4, "Plata física: metall preciós i industrial alhora. Més volàtil que l'or."),
    SIVR: d("Plata física (abrdn)", "Metalls preciosos", "silver", 4, "L'alternativa de baix cost per invertir en plata física."),
    PPLT: d("Platí físic", "Metalls preciosos", "platinum", 4, "Platí físic: joieria i catalitzadors. Escàs i cíclic."),
    PALL: d("Pal·ladi físic", "Metalls preciosos", "platinum", 5, "Pal·ladi físic: clau en catalitzadors d'automòbils. Mercat petit i brusc."),
    GDX:  d("Mineres d'or", "Metalls preciosos", "goldmine", 5, "Les empreses que extreuen l'or: amplifiquen els moviments del metall."),
    GDXJ: d("Mineres d'or júnior", "Metalls preciosos", "goldmine", 5, "Mineres petites i exploradores: la versió més arriscada de l'or."),

    // ── Immobiliari ────────────────────────────────────────────────
    VNQ:  d("Immobiliari EUA (REITs)", "Immobiliari", "realestate", 3, "Centres comercials, oficines, pisos i naus: cobra lloguers via borsa."),
    VNQI: d("Immobiliari internacional", "Immobiliari", "realestate", 4, "REITs de fora dels EUA: Europa, Àsia i emergents."),
    IYR:  d("Immobiliari EUA (iShares)", "Immobiliari", "realestate", 3, "L'altre gran fons d'immobiliari americà cotitzat."),
    SCHH: d("REITs EUA (Schwab)", "Immobiliari", "realestate", 3, "REITs americans amb una de les comissions més baixes del mercat."),
    REM:  d("REITs hipotecaris", "Immobiliari", "realestate", 5, "REITs que inverteixen en hipoteques: molt cupó, molt risc de tipus."),

    // ── Dividends ──────────────────────────────────────────────────
    VIG:  d("Dividends creixents (Vanguard)", "Dividends", "dividend", 2, "Empreses que porten 10+ anys apujant el dividend cada any."),
    VYM:  d("Alt dividend (Vanguard)", "Dividends", "dividend", 3, "Les empreses americanes que més dividend reparteixen."),
    SCHD: d("Dividends de qualitat (Schwab)", "Dividends", "dividend", 2, "Dividend alt però només d'empreses financerament sòlides."),
    DVY:  d("Dividends selectes (iShares)", "Dividends", "dividend", 3, "Cent empreses veteranes amb dividends consistents."),
    HDV:  d("Alt dividend (iShares)", "Dividends", "dividend", 2, "Dividend elevat amb filtre de salut financera."),
    SDY:  d("Aristòcrates del dividend (SPDR)", "Dividends", "dividend", 2, "Empreses amb 20+ anys seguits apujant el dividend."),
    NOBL: d("Aristòcrates del dividend (S&P)", "Dividends", "dividend", 2, "L'elit: 25+ anys consecutius apujant el dividend."),
    DGRO: d("Creixement de dividends", "Dividends", "dividend", 2, "Empreses amb dividends creixents i sostenibles, segons iShares."),

    // ── Defensius ──────────────────────────────────────────────────
    USMV: d("Mínima volatilitat EUA", "Defensius", "shield", 2, "Accions americanes seleccionades per moure's el mínim possible."),
    SPLV: d("Baixa volatilitat S&P 500", "Defensius", "shield", 2, "Les 100 empreses més tranquil·les del S&P 500."),
    QUAL: d("Factor qualitat (MSCI)", "Defensius", "shield", 3, "Empreses amb comptes sanejats i beneficis estables."),
    SPHD: d("Alt dividend i baixa volatilitat", "Defensius", "shield", 3, "Combina dividend generós amb moviments suaus."),
    XLP:  d("Consum bàsic EUA", "Defensius", "consumer", 2, "Coca-Cola, P&G, Walmart: coses que la gent compra passi el que passi."),
    XLU:  d("Serveis públics (utilities)", "Defensius", "utility", 2, "Elèctriques i aigües: negocis regulats i previsibles."),

    // ── Sectors EUA ────────────────────────────────────────────────
    XLF:  d("Banca i finances EUA", "Sectors EUA", "finance", 4, "Bancs, asseguradores i gestores del S&P 500."),
    XLY:  d("Consum discrecional EUA", "Sectors EUA", "consumer", 4, "Amazon, Tesla, Nike: el que comprem quan van bé les coses."),
    XLI:  d("Indústria EUA", "Sectors EUA", "industry", 3, "Fàbriques, ferrocarrils, maquinària i logística."),
    XLB:  d("Materials EUA", "Sectors EUA", "industry", 4, "Química, mineria i materials de construcció."),
    XLRE: d("Immobiliari EUA (sector S&P)", "Sectors EUA", "realestate", 3, "El sector immobiliari dins del S&P 500."),
    XLC:  d("Serveis de comunicació EUA", "Sectors EUA", "media", 4, "Google, Meta, Netflix, Disney: qui controla pantalles i xarxes."),
    KBE:  d("Bancs EUA", "Sectors EUA", "finance", 4, "Només bancs, grans i regionals, amb pesos equilibrats."),
    ITA:  d("Aeroespacial i defensa", "Sectors EUA", "defense", 3, "Boeing, Lockheed i la indústria aeroespacial americana."),
    JETS: d("Aerolínies", "Sectors EUA", "airline", 5, "Companyies aèries: cícliques, sensibles al fuel i al turisme."),
  };

  /* ===================================================================
     IL·LUSTRACIONS SVG per categoria/temàtica (cap imatge externa).
     Cada funció torna un SVG petit que fa de "fons visual" de la targeta.
     =================================================================== */
  const G = (id, stops) =>
    `<linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">${stops
      .map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`)
      .join("")}</linearGradient>`;

  window.ALPHA_ART = {
    gold: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_g",[[0,"#2a210c"],[1,"#0c0a05"]])}<linearGradient id="a_gb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe08a"/><stop offset=".5" stop-color="#f6b21e"/><stop offset="1" stop-color="#a9760a"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_g)"/><g transform="translate(96 38)"><g transform="skewX(-18)"><rect x="60" y="44" width="78" height="26" rx="3" fill="url(#a_gb)"/><rect x="20" y="18" width="78" height="26" rx="3" fill="url(#a_gb)"/><rect x="100" y="18" width="78" height="26" rx="3" fill="url(#a_gb)"/><rect x="60" y="-8" width="78" height="26" rx="3" fill="url(#a_gb)"/></g><rect x="40" y="20" width="20" height="3" fill="#fff" opacity=".5"/></g></svg>`,

    goldmine: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_gm",[[0,"#241b08"],[1,"#0a0703"]])}</defs><rect width="300" height="132" fill="url(#a_gm)"/><path d="M0 110 L60 60 L110 92 L170 40 L230 84 L300 52 L300 132 L0 132 Z" fill="#171106"/><path d="M0 110 L60 60 L110 92 L170 40 L230 84 L300 52" fill="none" stroke="#5a4413" stroke-width="2"/><g fill="#f6b21e"><circle cx="170" cy="40" r="5"/><circle cx="152" cy="58" r="2.4" opacity=".7"/><circle cx="190" cy="55" r="2" opacity=".6"/></g></svg>`,

    silver: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_s",[[0,"#1a1d22"],[1,"#08090b"]])}<linearGradient id="a_sb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f7fb"/><stop offset=".5" stop-color="#b8c2cf"/><stop offset="1" stop-color="#6d7884"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_s)"/><g transform="translate(96 38)"><g transform="skewX(-18)"><rect x="60" y="44" width="78" height="26" rx="3" fill="url(#a_sb)"/><rect x="20" y="18" width="78" height="26" rx="3" fill="url(#a_sb)"/><rect x="100" y="18" width="78" height="26" rx="3" fill="url(#a_sb)"/></g></g><circle cx="58" cy="66" r="22" fill="url(#a_sb)"/><text x="58" y="72" text-anchor="middle" font-family="serif" font-size="20" fill="#5a636e">Ag</text></svg>`,

    platinum: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_p",[[0,"#1c2026"],[1,"#0a0b0e"]])}<linearGradient id="a_pb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8f0f8"/><stop offset=".5" stop-color="#aebdcd"/><stop offset="1" stop-color="#5f6d7c"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_p)"/><g transform="translate(114 30)"><polygon points="36,0 72,26 58,70 14,70 0,26" fill="url(#a_pb)"/><polygon points="36,12 60,30 51,60 21,60 12,30" fill="#1c2026" opacity=".35"/></g><text x="150" y="122" text-anchor="middle" font-family="serif" font-size="13" fill="#8fa0b0">Pt · Pd</text></svg>`,

    oil: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_o",[[0,"#10261f"],[1,"#05100c"]])}${G("a_ob",[[0,"#3a4a44"],[1,"#16201c"]])}</defs><rect width="300" height="132" fill="url(#a_o)"/><g transform="translate(118 24)"><rect x="0" y="0" width="64" height="84" rx="8" fill="url(#a_ob)" stroke="#0c1512" stroke-width="2"/><ellipse cx="32" cy="0" rx="32" ry="9" fill="#46584f"/><rect x="0" y="22" width="64" height="6" fill="#0c1512"/><rect x="0" y="58" width="64" height="6" fill="#0c1512"/></g><path d="M150 96 q-18 14 0 26 q18-12 0-26" fill="#0f1f19" stroke="#3fd07a" stroke-width="2"/></svg>`,

    gas: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_ga",[[0,"#101c2e"],[1,"#060a12"]])}</defs><rect width="300" height="132" fill="url(#a_ga)"/><g fill="none" stroke="#5b9def" stroke-width="2.5" stroke-linecap="round"><path d="M120 100 q-14-18 4-34 q-4 16 12 22 q-2-26 20-40 q-6 22 10 30 q6-10 4-20 q16 14 10 36 q-6 22-30 24 q-22 2-30-18z" fill="#0d1a2c"/></g><circle cx="150" cy="88" r="8" fill="#5b9def" opacity=".5"/></svg>`,

    basket: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_bk",[[0,"#26210f"],[1,"#0b0a05"]])}</defs><rect width="300" height="132" fill="url(#a_bk)"/><g transform="translate(112 30)"><circle cx="14" cy="20" r="14" fill="#f6b21e"/><circle cx="44" cy="16" r="13" fill="#b8c2cf"/><circle cx="70" cy="24" r="12" fill="#3fd07a"/><circle cx="30" cy="44" r="13" fill="#ff7a59"/><circle cx="60" cy="46" r="12" fill="#5b8def"/></g><path d="M104 70 h92 l-10 34 h-72 z" fill="#1a160b" stroke="#f6b21e" stroke-width="2"/><path d="M112 70 l4 34 M152 70 v34 M188 70 l-4 34" stroke="#5a4a1e" stroke-width="1.5"/></svg>`,

    agri: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_ag",[[0,"#15230d"],[1,"#070d04"]])}</defs><rect width="300" height="132" fill="url(#a_ag)"/><g stroke="#c8b24a" stroke-width="2.5" fill="none" stroke-linecap="round"><path d="M110 116 V56"/><path d="M150 116 V44"/><path d="M190 116 V60"/></g><g fill="#e5cd5a">${[0,1,2,3].map(i=>`<ellipse cx="${104-i*1}" cy="${52-i*10}" rx="6" ry="3.4" transform="rotate(-30 ${104} ${52-i*10})"/><ellipse cx="${116+i*1}" cy="${52-i*10}" rx="6" ry="3.4" transform="rotate(30 ${116} ${52-i*10})"/>`).join("")}</g><g fill="#f0d868">${[0,1,2,3,4].map(i=>`<ellipse cx="${143-i*1}" cy="${40-i*9}" rx="6" ry="3.4" transform="rotate(-30 ${143} ${40-i*9})"/><ellipse cx="${157+i*1}" cy="${40-i*9}" rx="6" ry="3.4" transform="rotate(30 ${157} ${40-i*9})"/>`).join("")}</g><g fill="#d8c052">${[0,1,2].map(i=>`<ellipse cx="${184-i*1}" cy="${56-i*10}" rx="6" ry="3.4" transform="rotate(-30 ${184} ${56-i*10})"/><ellipse cx="${196+i*1}" cy="${56-i*10}" rx="6" ry="3.4" transform="rotate(30 ${196} ${56-i*10})"/>`).join("")}</g></svg>`,

    copper: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_cu",[[0,"#241408"],[1,"#0c0603"]])}<linearGradient id="a_cub" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f0a06a"/><stop offset=".5" stop-color="#c2632a"/><stop offset="1" stop-color="#7a3a14"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_cu)"/><g transform="translate(105 30)"><circle cx="45" cy="36" r="34" fill="url(#a_cub)"/><circle cx="45" cy="36" r="24" fill="none" stroke="#5c2c0e" stroke-width="3"/><circle cx="45" cy="36" r="14" fill="none" stroke="#5c2c0e" stroke-width="3"/></g><path d="M40 110 h220" stroke="#c2632a" stroke-width="3" stroke-dasharray="1 10" stroke-linecap="round"/></svg>`,

    usa: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="a_us" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101a2e"/><stop offset="1" stop-color="#070b14"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_us)"/><g opacity=".5">${[0,1,2,3].map(i=>`<rect x="0" y="${24+i*26}" width="300" height="11" fill="#21314e"/>`).join("")}</g><rect x="0" y="0" width="118" height="62" fill="#16233d"/><g fill="#cfe0ff">${[0,1,2].map(r=>[0,1,2,3].map(c=>`<circle cx="${20+c*26}" cy="${16+r*18}" r="2.4"/>`).join("")).join("")}</g><polyline points="20,108 70,92 110,100 160,72 210,84 260,52 290,40" fill="none" stroke="#3fd07a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,

    world: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs><radialGradient id="a_w" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#0c1f33"/><stop offset="1" stop-color="#050b12"/></radialGradient></defs><rect width="300" height="132" fill="url(#a_w)"/><circle cx="150" cy="66" r="44" fill="none" stroke="#5b9def" stroke-width="2"/><ellipse cx="150" cy="66" rx="44" ry="17" fill="none" stroke="#5b9def" stroke-width="1.5" opacity=".6"/><ellipse cx="150" cy="66" rx="17" ry="44" fill="none" stroke="#5b9def" stroke-width="1.5" opacity=".6"/><line x1="106" y1="66" x2="194" y2="66" stroke="#5b9def" stroke-width="1.5" opacity=".6"/><circle cx="150" cy="66" r="44" fill="#5b9def" opacity=".08"/><circle cx="132" cy="52" r="3" fill="#8fc2ff"/><circle cx="168" cy="78" r="3" fill="#8fc2ff"/><circle cx="158" cy="40" r="2.2" fill="#8fc2ff"/></svg>`,

    europe: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs><radialGradient id="a_eu" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#0b1740"/><stop offset="1" stop-color="#05081a"/></radialGradient></defs><rect width="300" height="132" fill="url(#a_eu)"/><g fill="#ffd84d">${Array.from({length:12},(_,i)=>{const a=(i/12)*Math.PI*2-Math.PI/2;const cx=150+Math.cos(a)*40;const cy=66+Math.sin(a)*40;return `<path transform="translate(${cx} ${cy})" d="M0,-7 2,-2 7,-2 3,1 5,7 0,3 -5,7 -3,1 -7,-2 -2,-2Z"/>`;}).join("")}</g></svg>`,

    japan: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_jp",[[0,"#1a1115"],[1,"#0a0608"]])}</defs><rect width="300" height="132" fill="url(#a_jp)"/><circle cx="150" cy="66" r="40" fill="#ff4d6d"/><g stroke="#ff4d6d" stroke-width="3" opacity=".5">${Array.from({length:12},(_,i)=>{const a=(i/12)*Math.PI*2;return `<line x1="${150+Math.cos(a)*46}" y1="${66+Math.sin(a)*46}" x2="${150+Math.cos(a)*60}" y2="${66+Math.sin(a)*60}"/>`;}).join("")}</g></svg>`,

    china: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="a_cn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a0d10"/><stop offset="1" stop-color="#140405"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_cn)"/><g fill="#ffd84d" transform="translate(120 40)"><path d="M0,-22 6,-6 23,-6 9,4 14,21 0,11 -14,21 -9,4 -23,-6 -6,-6Z"/></g><g fill="#ffd84d" transform="translate(176 30) scale(.4)"><path d="M0,-22 6,-6 23,-6 9,4 14,21 0,11 -14,21 -9,4 -23,-6 -6,-6Z"/></g></svg>`,

    asia: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_as",[[0,"#1c1024"],[1,"#0a0610"]])}</defs><rect width="300" height="132" fill="url(#a_as)"/><g transform="translate(150 70)"><circle r="34" fill="none" stroke="#c084fc" stroke-width="2"/><path d="M0,-34 A34,34 0 0 1 0,34 A17,17 0 0 1 0,0 A17,17 0 0 0 0,-34" fill="#c084fc" opacity=".5"/></g><polyline points="30,110 80,96 130,104 190,78 250,88 285,66" fill="none" stroke="#c084fc" stroke-width="2.4" stroke-linecap="round" opacity=".8"/></svg>`,

    emerging: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs><radialGradient id="a_em" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#0c2a23"/><stop offset="1" stop-color="#050f0c"/></radialGradient></defs><rect width="300" height="132" fill="url(#a_em)"/><circle cx="150" cy="66" r="42" fill="none" stroke="#3fd07a" stroke-width="2"/><ellipse cx="150" cy="66" rx="42" ry="16" fill="none" stroke="#3fd07a" stroke-width="1.5" opacity=".6"/><ellipse cx="150" cy="66" rx="16" ry="42" fill="none" stroke="#3fd07a" stroke-width="1.5" opacity=".6"/><line x1="108" y1="66" x2="192" y2="66" stroke="#3fd07a" stroke-width="1.5" opacity=".6"/><circle cx="150" cy="66" r="42" fill="#3fd07a" opacity=".08"/></svg>`,

    india: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_in",[[0,"#2a1604"],[1,"#0b0602"]])}</defs><rect width="300" height="132" fill="url(#a_in)"/><circle cx="150" cy="66" r="30" fill="none" stroke="#ff9933" stroke-width="3"/><circle cx="150" cy="66" r="9" fill="#3a6df0"/><g stroke="#3a6df0" stroke-width="1.5">${Array.from({length:24},(_,i)=>{const a=(i/24)*Math.PI*2;return `<line x1="${150+Math.cos(a)*9}" y1="${66+Math.sin(a)*9}" x2="${150+Math.cos(a)*30}" y2="${66+Math.sin(a)*30}"/>`;}).join("")}</g></svg>`,

    tech: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="a_t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a1f24"/><stop offset="1" stop-color="#050d0f"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_t)"/><g transform="translate(110 26)"><rect x="0" y="0" width="80" height="80" rx="8" fill="#0c2a30" stroke="#19c3a0" stroke-width="2"/><rect x="20" y="20" width="40" height="40" rx="4" fill="#0a3a40" stroke="#19c3a0" stroke-width="1.5"/><g stroke="#19c3a0" stroke-width="2">${[0,1,2].map(i=>`<line x1="${20+i*20}" y1="0" x2="${20+i*20}" y2="-12"/><line x1="${20+i*20}" y1="80" x2="${20+i*20}" y2="92"/><line x1="0" y1="${20+i*20}" x2="-12" y2="${20+i*20}"/><line x1="80" y1="${20+i*20}" x2="92" y2="${20+i*20}"/>`).join("")}</g><circle cx="40" cy="40" r="6" fill="#19c3a0"/></g></svg>`,

    ai: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_ai",[[0,"#160f2e"],[1,"#080512"]])}</defs><rect width="300" height="132" fill="url(#a_ai)"/><g stroke="#8b6bff" stroke-width="1.6" fill="none" opacity=".9"><path d="M60 96 L110 66 L150 84 L196 46 L244 60"/><path d="M60 40 L110 66 M150 84 L150 30 M196 46 L244 96"/></g><g fill="#0d0a20" stroke="#a78bff" stroke-width="2"><circle cx="60" cy="96" r="7"/><circle cx="60" cy="40" r="7"/><circle cx="110" cy="66" r="9"/><circle cx="150" cy="84" r="7"/><circle cx="150" cy="30" r="7"/><circle cx="196" cy="46" r="9"/><circle cx="244" cy="60" r="7"/><circle cx="244" cy="96" r="7"/></g><circle cx="110" cy="66" r="3.4" fill="#c4b0ff"/><circle cx="196" cy="46" r="3.4" fill="#c4b0ff"/></svg>`,

    cloud: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_cl",[[0,"#0d1b2e"],[1,"#060b13"]])}</defs><rect width="300" height="132" fill="url(#a_cl)"/><path d="M104 84 a20 20 0 0 1 6-39 a26 26 0 0 1 50-8 a18 18 0 0 1 26 16 a16 16 0 0 1 -4 31 z" fill="#12283f" stroke="#5b9def" stroke-width="2"/><g stroke="#5b9def" stroke-width="2" stroke-linecap="round"><line x1="126" y1="96" x2="126" y2="112"/><line x1="150" y1="96" x2="150" y2="118"/><line x1="174" y1="96" x2="174" y2="112"/></g></svg>`,

    cyber: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_cy",[[0,"#0d2418"],[1,"#050f0a"]])}</defs><rect width="300" height="132" fill="url(#a_cy)"/><path d="M150 18 L192 34 V66 c0 26 -18 40 -42 50 c-24 -10 -42 -24 -42 -50 V34 Z" fill="#0c2a1c" stroke="#3fd07a" stroke-width="2.5"/><path d="M136 66 l10 10 l20 -22" fill="none" stroke="#3fd07a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,

    smallcaps: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_sc",[[0,"#1d1430"],[1,"#0a0714"]])}</defs><rect width="300" height="132" fill="url(#a_sc)"/><g transform="translate(70 22)">${[20,46,30,64,40,78,58,90].map((h,i)=>`<rect x="${i*20}" y="${96-h}" width="13" height="${h}" rx="2" fill="#9a7bff" opacity="${0.55+i*0.05}"/>`).join("")}</g></svg>`,

    energy: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_en",[[0,"#2c1606"],[1,"#0c0602"]])}</defs><rect width="300" height="132" fill="url(#a_en)"/><path d="M168 16 L120 74 h28 l-14 44 56 -64 h-30 z" fill="#ffb000"/></svg>`,

    clean: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_cn2",[[0,"#0d2415"],[1,"#050f08"]])}</defs><rect width="300" height="132" fill="url(#a_cn2)"/><g stroke="#3fd07a" stroke-width="2.5" fill="none" stroke-linecap="round"><path d="M110 112 q40 -30 30 -70 q30 20 26 58"/><path d="M140 42 q-30 6 -44 34"/></g><circle cx="196" cy="40" r="16" fill="none" stroke="#ffd84d" stroke-width="2.5"/><g stroke="#ffd84d" stroke-width="2.5" stroke-linecap="round">${[0,1,2,3,4,5,6,7].map(i=>{const a=(i/8)*Math.PI*2;return `<line x1="${196+Math.cos(a)*22}" y1="${40+Math.sin(a)*22}" x2="${196+Math.cos(a)*28}" y2="${40+Math.sin(a)*28}"/>`;}).join("")}</g></svg>`,

    solar: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_so",[[0,"#241a06"],[1,"#0d0903"]])}</defs><rect width="300" height="132" fill="url(#a_so)"/><circle cx="150" cy="30" r="14" fill="#ffd84d"/><g stroke="#ffd84d" stroke-width="2.4" stroke-linecap="round">${[0,1,2,3,4,5,6,7].map(i=>{const a=(i/8)*Math.PI*2;return `<line x1="${150+Math.cos(a)*20}" y1="${30+Math.sin(a)*20}" x2="${150+Math.cos(a)*26}" y2="${30+Math.sin(a)*26}"/>`;}).join("")}</g><g transform="translate(96 62)" stroke="#ffb000" stroke-width="1.6" fill="#1c1408"><path d="M8 0 h92 l12 40 h-116 z"/><path d="M22 0 l-6 40 M46 0 l-3 40 M70 0 l3 40 M94 0 l6 40 M4 14 h100 M0 27 h108"/></g></svg>`,

    wind: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_wi",[[0,"#0e1c28"],[1,"#060c11"]])}</defs><rect width="300" height="132" fill="url(#a_wi)"/><line x1="150" y1="58" x2="150" y2="120" stroke="#9fb8c8" stroke-width="4" stroke-linecap="round"/><g fill="#dceaf4"><path d="M150 58 l-4 -44 q4 -6 8 0 l-4 44" /><path d="M150 58 l40 20 q2 7 -5 7 l-35 -27"/><path d="M150 58 l-40 20 q-2 7 5 7 l35 -27"/></g><circle cx="150" cy="58" r="5" fill="#eef6fc"/></svg>`,

    nuclear: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_nu",[[0,"#13240d"],[1,"#080f05"]])}</defs><rect width="300" height="132" fill="url(#a_nu)"/><g transform="translate(150 66)"><circle r="7" fill="#b6f04d"/><g fill="none" stroke="#b6f04d" stroke-width="2.4"><ellipse rx="40" ry="15"/><ellipse rx="40" ry="15" transform="rotate(60)"/><ellipse rx="40" ry="15" transform="rotate(120)"/></g></g></svg>`,

    health: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="a_h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101d2e"/><stop offset="1" stop-color="#060b13"/></linearGradient></defs><rect width="300" height="132" fill="url(#a_h)"/><path d="M30 66 H96 l10 -26 18 52 14 -40 12 22 H270" fill="none" stroke="#5b8def" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><g fill="#5b8def" opacity=".25" transform="translate(132 40)"><rect x="14" y="0" width="12" height="40" rx="3"/><rect x="0" y="14" width="40" height="12" rx="3"/></g></svg>`,

    bio: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_bi",[[0,"#101c2b"],[1,"#070c12"]])}</defs><rect width="300" height="132" fill="url(#a_bi)"/><g stroke="#5bd0ef" stroke-width="2.4" fill="none"><path d="M128 14 q44 26 0 52 q-44 26 0 52"/><path d="M172 14 q-44 26 0 52 q44 26 0 52"/></g><g stroke="#8be0f8" stroke-width="2">${[24,40,66,92,108].map(y=>`<line x1="${y===66?128:134}" y1="${y}" x2="${y===66?172:166}" y2="${y}"/>`).join("")}</g></svg>`,

    bond: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_bd",[[0,"#241a2e"],[1,"#0a0712"]])}</defs><rect width="300" height="132" fill="url(#a_bd)"/><g transform="translate(96 24)"><rect x="0" y="0" width="108" height="84" rx="6" fill="#15101f" stroke="#9a7bff" stroke-width="2"/><line x1="14" y1="20" x2="94" y2="20" stroke="#9a7bff" stroke-width="2" opacity=".7"/><line x1="14" y1="36" x2="74" y2="36" stroke="#6a5a8a" stroke-width="2"/><text x="54" y="68" text-anchor="middle" font-family="serif" font-size="22" fill="#9a7bff">%</text></g></svg>`,

    corp: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_cp",[[0,"#241a2e"],[1,"#0a0712"]])}</defs><rect width="300" height="132" fill="url(#a_cp)"/><g transform="translate(116 26)" fill="#15101f" stroke="#9a7bff" stroke-width="2"><rect x="0" y="14" width="32" height="66"/><rect x="36" y="0" width="32" height="80"/></g><g fill="#9a7bff">${[0,1,2].map(r=>`<rect x="122" y="${42+r*16}" width="8" height="6"/><rect x="138" y="${30+r*16}" width="8" height="6"/><rect x="154" y="${42+r*16}" width="8" height="6"/>`).join("")}</g></svg>`,

    realestate: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_re",[[0,"#2a210c"],[1,"#0b0805"]])}</defs><rect width="300" height="132" fill="url(#a_re)"/><g transform="translate(96 22)" stroke="#ffb000" stroke-width="2" fill="#1a1407"><rect x="0" y="36" width="40" height="52"/><rect x="46" y="14" width="32" height="74"/><rect x="84" y="46" width="36" height="42"/></g><g fill="#ffb000">${[0,1,2].map(r=>[0,1].map(c=>`<rect x="${52+c*14}" y="${24+r*16}" width="6" height="8"/>`).join("")).join("")}</g></svg>`,

    dividend: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_dv",[[0,"#0f2418"],[1,"#060f0a"]])}</defs><rect width="300" height="132" fill="url(#a_dv)"/><g transform="translate(150 60)"><circle r="30" fill="#0d2a1a" stroke="#3fd07a" stroke-width="2.5"/><text x="0" y="9" text-anchor="middle" font-family="serif" font-size="30" fill="#3fd07a">€</text></g><g stroke="#3fd07a" stroke-width="2" stroke-linecap="round" opacity=".7"><path d="M104 108 q46 18 92 0"/><path d="M114 118 q36 12 72 0"/></g></svg>`,

    shield: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_sh",[[0,"#101c2a"],[1,"#070c12"]])}</defs><rect width="300" height="132" fill="url(#a_sh)"/><path d="M150 16 L194 32 V68 c0 26 -20 42 -44 52 c-24 -10 -44 -26 -44 -52 V32 Z" fill="#0e1a28" stroke="#7aa8d8" stroke-width="2.5"/><polyline points="122,74 138,58 152,70 176,44" fill="none" stroke="#7aa8d8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,

    consumer: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_co",[[0,"#241a10"],[1,"#0c0805"]])}</defs><rect width="300" height="132" fill="url(#a_co)"/><g stroke="#e8b56a" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M104 40 h14 l12 52 h56 l12 -40 h-72"/><circle cx="138" cy="106" r="7"/><circle cx="182" cy="106" r="7"/></g></svg>`,

    utility: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_ut",[[0,"#1a2410"],[1,"#0a0d05"]])}</defs><rect width="300" height="132" fill="url(#a_ut)"/><g stroke="#c8d84a" stroke-width="2.4" fill="none"><path d="M150 18 L128 108 M150 18 L172 108 M128 108 h44"/><path d="M136 44 h28 M131 70 h38"/><path d="M60 44 q46 18 76 0 M164 44 q46 18 76 0" opacity=".6"/></g><circle cx="150" cy="18" r="4" fill="#c8d84a"/></svg>`,

    finance: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_f",[[0,"#10261f"],[1,"#050f0b"]])}</defs><rect width="300" height="132" fill="url(#a_f)"/><g transform="translate(105 30)" fill="none" stroke="#46d18a" stroke-width="2.5"><path d="M45 0 L90 24 H0 Z" fill="#0e2a1f"/><line x1="10" y1="30" x2="10" y2="68"/><line x1="32" y1="30" x2="32" y2="68"/><line x1="58" y1="30" x2="58" y2="68"/><line x1="80" y1="30" x2="80" y2="68"/><line x1="-4" y1="74" x2="94" y2="74"/></g></svg>`,

    industry: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_id",[[0,"#1e1a14"],[1,"#0b0906"]])}</defs><rect width="300" height="132" fill="url(#a_id)"/><g fill="#241f16" stroke="#d8a04a" stroke-width="2"><path d="M96 108 V60 l28 20 V60 l28 20 V60 l28 20 v28 z"/><rect x="100" y="30" width="12" height="30"/></g><g stroke="#8a7248" stroke-width="2" opacity=".7"><path d="M106 22 q6 -8 0 -14" fill="none"/></g></svg>`,

    media: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_me",[[0,"#20102a"],[1,"#0c0512"]])}</defs><rect width="300" height="132" fill="url(#a_me)"/><g transform="translate(150 70)"><circle r="10" fill="#d884ff"/><g fill="none" stroke="#d884ff" stroke-width="2.4" opacity=".8"><path d="M-20 -20 a28 28 0 0 1 40 0"/><path d="M-32 -32 a45 45 0 0 1 64 0"/><path d="M-44 -44 a62 62 0 0 1 88 0"/></g><line x1="0" y1="10" x2="0" y2="44" stroke="#d884ff" stroke-width="3"/></g></svg>`,

    defense: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_df",[[0,"#151d26"],[1,"#080c10"]])}</defs><rect width="300" height="132" fill="url(#a_df)"/><g transform="translate(150 76) rotate(-35)" fill="#9fb8c8"><path d="M0 -46 L10 -14 h-20 Z"/><rect x="-7" y="-16" width="14" height="42" rx="4"/><path d="M-7 14 l-12 16 h12 z M7 14 l12 16 h-12 z"/></g><g stroke="#3a4c5c" stroke-width="1.6" opacity=".8"><circle cx="70" cy="40" r="1.6" fill="#9fb8c8"/><circle cx="236" cy="88" r="1.6" fill="#9fb8c8"/><circle cx="216" cy="30" r="1.6" fill="#9fb8c8"/></g></svg>`,

    airline: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><defs>${G("a_al",[[0,"#0e1a2e"],[1,"#060a12"]])}</defs><rect width="300" height="132" fill="url(#a_al)"/><g transform="translate(150 62) rotate(15)" fill="#cfe0ff"><path d="M-40 0 h56 l24 -8 q10 -2 8 4 l-30 12 h-58 q-8 0 -8 -4 t8 -4"/><path d="M-6 0 l-18 -22 h10 l24 22 z"/><path d="M-6 8 l-14 16 h9 l19 -16 z"/></g><path d="M40 100 q60 -40 130 -58" stroke="#3a4c66" stroke-width="1.6" stroke-dasharray="3 6" fill="none"/></svg>`,

    generic: () => `<svg viewBox="0 0 300 132" preserveAspectRatio="xMidYMid slice"><rect width="300" height="132" fill="#15140f"/><polyline points="20,96 80,70 140,82 200,50 280,40" fill="none" stroke="#ffb000" stroke-width="3"/></svg>`,
  };
})();
