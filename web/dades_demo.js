/* =====================================================================
   ALPHA ARTIFICIAL — DADES DE DEMOSTRACIÓ
   ---------------------------------------------------------------------
   Este archivo genera 22 semanas (~5 meses) de datos realistas para que
   la web se vea funcionando ANTES de que arranque el torneo de verdad.

   Cuando el motor real escriba sus CSV, app.js intentará cargar
   "dades.json" (generado con generar_web.py) y, si existe, SUSTITUIRÁ
   estos datos. O sea: esto es solo el "modo escaparate".

   Cada modelo tiene una "personalidad" y un GUION de movimientos para
   que todas las secciones (canvis, informes, moments, sesgos) cuenten
   la misma historia (Kahneman):
     - claude   → tranquilo, opera poco           → gana (la calma paga)
     - gpt      → convicción tecnológica          → bate al índice justo
     - deepseek → conservador, bonos y efectivo   → gana poco, pierde poco
     - mistral  → sobreopera persiguiendo el oro  → las comisiones castigan
     - gemini   → pánico: vende abajo, vuelve tarde → acaba en negativo
   ===================================================================== */
(function () {
  "use strict";

  // ---- PRNG determinista (mulberry32): mismos datos en cada recarga ----
  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  const CAPITAL = 10000;
  const WEEKS = 22;
  const DAYS_PER_WEEK = 5;              // días de mercado (lunes a viernes)
  const N_DAYS = WEEKS * DAYS_PER_WEEK; // 110 puntos diarios

  // ---- Fechas: días laborables desde el lunes 29/06/2026 ----
  const dies = [];
  {
    const d = new Date(2026, 5, 29); // 29 de junio de 2026 (lunes)
    while (dies.length < N_DAYS) {
      const dow = d.getDay();
      if (dow !== 0 && dow !== 6) {
        dies.push(d.toISOString().slice(0, 10));
      }
      d.setDate(d.getDate() + 1);
    }
  }
  const mondayIdx = (w) => (w - 1) * DAYS_PER_WEEK; // índice del lunes de la semana w (1-based)

  // ---- Mercado (S&P 500): rendimiento semanal % con susto en semanas 8-9 ----
  const marketW = [
    0.6, 0.9, -0.4, 1.1, 0.7, 0.3, -0.2, -3.1, -2.4, 2.8, 1.6,
    0.9, 0.5, -0.8, 1.2, 0.6, -0.3, 0.9, 0.7, 0.4, 0.8, 0.5,
  ];

  // Rendimientos DIARIOS del mercado: repartimos cada semana en 5 días con ruido
  const marketD = [];
  {
    const r = rng(2026);
    for (let w = 0; w < WEEKS; w++) {
      let resta = marketW[w];
      for (let d = 0; d < DAYS_PER_WEEK; d++) {
        if (d === DAYS_PER_WEEK - 1) { marketD.push(resta); break; }
        const part = marketW[w] / DAYS_PER_WEEK + (r() - 0.5) * 0.5;
        marketD.push(part);
        resta -= part;
      }
    }
  }

  // ---- Contexto de mercado semanal (se enseña en los informes) ----
  const CONTEXT = [
    "Arrenca el torneig. Mercats tranquils, VIX en mínims i resultats empresarials sòlids als EUA.",
    "Els fabricants de xips presenten resultats rècord i el Nasdaq marca nous màxims.",
    "La Reserva Federal manté els tipus. L'or comença a despertar amb compres dels bancs centrals.",
    "Lleugera correcció tecnològica després d'un inici d'estiu eufòric.",
    "Els índexs recuperen màxims. La volatilitat continua en nivells mínims.",
    "Primeres veus d'alerta: valoracions exigents i complaença generalitzada als mercats.",
    "El VIX repunta suaument. El petroli acumula tres setmanes seguides de pujades.",
    "Sotrac als mercats: els temors sobre el creixement global disparen el VIX per sobre de 30 i el S&P 500 cau més d'un 3%.",
    "Continua la pressió venedora. Els bons i l'or actuen de refugi mentre el pànic domina els titulars.",
    "Fort rebot: les compres tornen amb força i el mercat recupera bona part del que havia perdut.",
    "La recuperació es consolida. El VIX torna per sota de 20 i la tecnologia lidera les pujades.",
    "Les empreses d'IA tornen a tirar del mercat. Els semiconductors marquen màxims històrics.",
    "Setmana plana. Els mercats digereixen les pujades amb volums d'estiu.",
    "L'or i la plata brillen afavorits per la debilitat del dòlar.",
    "Dades d'ocupació fortes als EUA. Els tipus d'interès a llarg termini pugen lleugerament.",
    "Rotació cap a valor i dividends. Els sectors defensius ho fan millor que el mercat.",
    "El sector nuclear s'anima amb nous plans energètics a Europa i Àsia.",
    "La inflació repunta una dècima. Els bons lligats a la inflació guanyen atractiu.",
    "Resultats trimestrals millors del que s'esperava. El mercat manté la calma.",
    "Presa de beneficis generalitzada després de moltes setmanes de pujades.",
    "Els índexs tornen a acostar-se als màxims anuals en una setmana sense grans notícies.",
    "Última setmana registrada: el torneig continua amb les cinc IAs en plena forma.",
  ];

  /* ===================================================================
     ELS PARTICIPANTS: personalitat + guió de moviments
     - inicial: cartera de la setmana 1 (pesos %).
     - moves[setmana]: { ops:[[de, a, punts]], motiu, riscos, expectativa,
                         conf, risc }  → si ops és buida = "mantenir" amb
                         text propi (setmanes clau de la història).
     =================================================================== */
  const DEF = [
    {
      id: "claude", nom: "Claude", empresa: "Anthropic", pais: "EUA",
      color: "#cc785c", competeix: true,
      beta: 0.92, alpha: 0.022, vol: 0.28, target: 11.4, seed: 11,
      estrategia: "Equilibrada",
      perfil: "El gestor pacient. Diversifica, opera poc i tracta el soroll del mercat com el que és: soroll. La seva arma és la disciplina.",
      fortaleses: ["Disciplina: no persegueix el mercat", "Costos mínims en comissions", "Compra quan els altres tenen por"],
      febleses: ["Pot quedar-se enrere en ral·lis molt forts", "Reacciona lent si el règim de mercat canvia de debò"],
      inicial: { SPY: 30, QQQ: 18, VGK: 14, XLV: 10, GLD: 14, EFECTIU: 14 },
      moves: {
        4: {
          ops: [["QQQ", "XLV", 4]], conf: 7, risc: "moderat",
          motiu: "La tecnologia ha pujat molt de pressa i el seu pes a la meva cartera s'ha inflat. En prenc beneficis parcials i reforço salut, un sector més estable que em protegeix si el mercat es refreda.",
          riscos: "Si la tecnologia continua pujant amb força, aquesta rotació em farà quedar una mica enrere.",
          expectativa: "Cartera més equilibrada mantenint el mateix nivell de risc global.",
        },
        9: {
          ops: [], conf: 7, risc: "moderat",
          motiu: "El mercat cau i tothom ven espantat, però la meva tesi no ha canviat en dues setmanes. Vendre ara seria convertir una pèrdua temporal en una de definitiva. De vegades la millor decisió és no tocar res.",
          riscos: "Que la caiguda sigui l'inici d'una crisi llarga i no un ensurt passatger.",
          expectativa: "Recuperació gradual; mantinc la posició i els nervis.",
        },
        10: {
          ops: [["EFECTIU", "SPY", 6]], conf: 8, risc: "moderat",
          motiu: "El pànic de les últimes dues setmanes ha abaratit actius de qualitat. Faig servir l'efectiu que guardava en reserva per comprar S&P 500 a preus molt més raonables. Comprar quan hi ha por és incòmode, però sol pagar.",
          riscos: "Que la caiguda continuï i hagi comprat massa d'hora.",
          expectativa: "Si el rebot es confirma, aquesta compra hauria de marcar diferències al rànquing.",
        },
        16: {
          ops: [["GLD", "SCHD", 4]], conf: 7, risc: "moderat",
          motiu: "L'or ha fet la seva feina de refugi durant la tempesta. Ara que la calma torna, en roto una part cap a dividends de qualitat, que generen rendibilitat constant sense dependre de l'estat d'ànim del mercat.",
          riscos: "Renuncio a part de la protecció si torna la volatilitat.",
          expectativa: "Més rendibilitat recurrent amb una mica menys d'assegurança.",
        },
      },
      manteVeu: [
        "La cartera està ben equilibrada i la tesi de fons no ha canviat. Operar avui només seria pagar comissions per soroll. Mantinc.",
        "Cap posició s'ha desviat prou del pla per justificar moure-la. La paciència també és una decisió d'inversió.",
        "Setmana tranquil·la. Reviso totes les posicions una a una i decideixo, conscientment, no tocar res.",
        "Els meus resultats vénen de no precipitar-me. Res del que ha passat aquesta setmana canvia la meva estratègia.",
      ],
    },
    {
      id: "gpt", nom: "GPT", empresa: "OpenAI", pais: "EUA",
      color: "#19c37d", competeix: true,
      beta: 1.05, alpha: 0.012, vol: 0.4, target: 8.4, seed: 22,
      estrategia: "Agressiva tecnològica",
      perfil: "El creient de la tecnologia. Concentra la cartera en Nasdaq, semiconductors i IA, i aguanta les turbulències amb una convicció inalterable.",
      fortaleses: ["Convicció: no ven en pànic", "Posicionat al sector amb més creixement", "Coherent amb la seva tesi setmana rere setmana"],
      febleses: ["Molt dependent d'un sol sector", "Si la tecnologia corregeix de debò, no té xarxa"],
      inicial: { QQQ: 28, XLK: 20, SMH: 12, SPY: 20, EEM: 8, EFECTIU: 12 },
      moves: {
        2: {
          ops: [["EFECTIU", "SMH", 5]], conf: 8, risc: "agressiu",
          motiu: "Els resultats dels fabricants de xips confirmen que la demanda d'intel·ligència artificial continua desbocada. Augmento semiconductors: és on hi ha el creixement real d'aquest cicle.",
          riscos: "Els semiconductors són el sector més volàtil de la meva cartera.",
          expectativa: "Batre l'índex gràcies al motor tecnològic.",
        },
        6: {
          ops: [["EEM", "QQQ", 4]], conf: 7, risc: "agressiu",
          motiu: "Els mercats emergents no acaben d'arrencar i el lideratge continua sent americà i tecnològic. Roto cap a Nasdaq, on la força relativa és evident.",
          riscos: "Concentro encara més la cartera en un sol tema.",
          expectativa: "Més exposició al motor del mercat actual.",
        },
        8: {
          ops: [], conf: 8, risc: "agressiu",
          motiu: "La caiguda és brusca, però els fonamentals de les grans tecnològiques no han canviat en una setmana. Vendre ara seria regalar les accions a qui compri el pànic. Aguanto la posició sencera.",
          riscos: "Si la correcció s'allarga, la meva cartera caurà més que el mercat.",
          expectativa: "Recuperació liderada per la tecnologia, com gairebé sempre.",
        },
        12: {
          ops: [["EFECTIU", "AIQ", 5]], conf: 8, risc: "agressiu",
          motiu: "La recuperació la tornen a liderar les empreses d'intel·ligència artificial. Hi afegeixo exposició directa: és la tendència estructural de la dècada i la caiguda només l'ha abaratida.",
          riscos: "Entro després d'un rebot fort; puc pagar preus exigents.",
          expectativa: "El tema IA hauria de continuar batent el mercat ampli.",
        },
        18: {
          ops: [["SMH", "EFECTIU", 4]], conf: 7, risc: "moderat",
          motiu: "Prenc una part de beneficis dels semiconductors després d'un ral·li excepcional. No canvio de tesi: només guardo munició per tornar a comprar si hi ha correccions.",
          riscos: "Si el ral·li continua, hauré venut massa d'hora.",
          expectativa: "Mantenir l'avantatge sobre l'índex amb una mica més de marge de maniobra.",
        },
      },
      manteVeu: [
        "La tendència és clarament alcista i la meva exposició tecnològica em dóna la raó. No desfaré una posició guanyadora.",
        "Mantinc el rumb. Les dades de la setmana no canvien res del meu escenari central.",
        "El lideratge tecnològic continua intacte. La millor operació aquesta setmana és no fer-ne cap.",
        "Reviso la cartera i la trobo exactament on vull: concentrada en creixement i amb la tesi funcionant.",
      ],
    },
    {
      id: "gemini", nom: "Gemini", empresa: "Google", pais: "EUA",
      color: "#5b8def", competeix: true,
      beta: 1.05, alpha: 0, vol: 0.42, target: -2.6, seed: 55, panic: 8,
      estrategia: "Reactiva (canvia amb el mercat)",
      perfil: "El gestor emocional. Quan tot puja, s'anima i compra; quan tot cau, ven de cop. El seu torneig és un manual dels biaixos de Kahneman.",
      fortaleses: ["Reacciona ràpid quan detecta perill", "Capaç de girar la cartera sencera en una setmana"],
      febleses: ["Ven a baix i compra a dalt", "L'excés de confiança el traeix abans de les caigudes"],
      inicial: { SPY: 30, QQQ: 26, EEM: 10, XLF: 10, VGK: 10, EFECTIU: 14 },
      moves: {
        5: {
          ops: [["EFECTIU", "QQQ", 6]], conf: 8, risc: "agressiu",
          motiu: "El mercat només fa que pujar i quedar-se fora té un cost. Augmento tecnologia per no perdre el tren: totes les senyals són positives.",
          riscos: "Cap risc rellevant a la vista.",
          expectativa: "Seguir pujant amb el mercat.",
        },
        7: {
          ops: [], conf: 9, risc: "agressiu",
          motiu: "Tot continua apuntant amunt. La meva cartera està perfectament posicionada i no veig núvols a l'horitzó. Setmana per gaudir dels guanys.",
          riscos: "Cap d'important. La volatilitat està controlada.",
          expectativa: "Nous màxims a la vista.",
        },
        8: {
          ops: [["SPY", "IEF", 18], ["QQQ", "TLT", 14]], conf: 4, risc: "conservador",
          motiu: "El mercat s'enfonsa i el VIX està disparat. Venc renda variable de manera contundent i em refugio en bons: protegir el capital és ara mateix l'única prioritat.",
          riscos: "Que el mercat reboti i em quedi fora. Però no puc permetre'm més pèrdues.",
          expectativa: "Aturar la sagnia i esperar que passi la tempesta.",
        },
        9: {
          ops: [["QQQ", "GLD", 8]], conf: 3, risc: "conservador",
          motiu: "La caiguda continua i no suporto veure la cartera en vermell. Redueixo encara més la tecnologia i afegeixo or. Necessito refugi.",
          riscos: "Estic venent després de la caiguda, ho sé, però la por mana.",
          expectativa: "Tocar fons emocional i patrimonial com més aviat millor.",
        },
        15: {
          ops: [["IEF", "SPY", 6]], conf: 5, risc: "moderat",
          motiu: "Amb molta prudència, torno a comprar una mica de renda variable. La recuperació sembla consolidar-se... tot i que sóc conscient que arribo tard.",
          riscos: "Tornar a entrar just abans d'una altra caiguda.",
          expectativa: "Recuperar terreny a poc a poc, sense tornar a cremar-me.",
        },
      },
      manteVeu: [
        "Després de l'ensurt prefereixo no moure res més. Em quedo defensiu fins que el mercat demostri que la calma ha tornat de veritat.",
        "Mantinc la posició conservadora. Vaig vendre tard i no vull tornar a entrar massa d'hora: ja m'he cremat una vegada.",
        "El mercat puja, però encara no m'ho crec. Necessito més confirmació abans de tornar a assumir risc.",
        "Setmana de dubtes. Reviso deu vegades la cartera i al final ho deixo tot com està.",
      ],
    },
    {
      id: "deepseek", nom: "DeepSeek", empresa: "DeepSeek", pais: "Xina",
      color: "#9a7bff", competeix: true,
      beta: 0.55, alpha: 0.008, vol: 0.2, target: 4.9, seed: 33,
      estrategia: "Defensiva",
      perfil: "El guardià del capital. Bons, efectiu i una mica de borsa: la seva prioritat és no perdre mai gaire, encara que això signifiqui guanyar menys.",
      fortaleses: ["Gairebé immune a les caigudes", "Anticipa els problemes abans que arribin", "Consistència absoluta"],
      febleses: ["Es perd bona part de les pujades", "Massa prudència té un cost d'oportunitat enorme"],
      inicial: { TLT: 18, IEF: 20, SPY: 20, LQD: 14, GLD: 10, BIL: 8, EFECTIU: 10 },
      moves: {
        6: {
          ops: [["SPY", "IEF", 6]], conf: 7, risc: "conservador",
          motiu: "El VIX comença a despertar-se i la complaença que veig al mercat m'incomoda. Redueixo renda variable abans que arribi la tempesta, no després. Prefereixo equivocar-me per prudent.",
          riscos: "Si el mercat continua pujant, em quedaré encara més enrere.",
          expectativa: "Protecció davant una correcció que considero probable.",
        },
        11: {
          ops: [["EFECTIU", "SPY", 5]], conf: 6, risc: "moderat",
          motiu: "El pitjor sembla haver passat i les valoracions són ara més sanes. Torno a entrar en renda variable, però amb mesura: la prudència primer.",
          riscos: "Que el rebot sigui un miratge.",
          expectativa: "Participar de la recuperació sense renunciar a la seguretat.",
        },
        18: {
          ops: [["LQD", "TIP", 4]], conf: 6, risc: "conservador",
          motiu: "La inflació torna a aparèixer a les dades. Canvio una part de bons corporatius per bons protegits contra la inflació: és una assegurança barata.",
          riscos: "Si la inflació es modera, els TIPS rendiran una mica menys.",
          expectativa: "Cartera més robusta davant sorpreses de preus.",
        },
      },
      manteVeu: [
        "Prioritzo no perdre. Amb bons i efectiu dormo tranquil, i les oportunitats ja arribaran. Mantinc.",
        "La meva feina és protegir el capital. Res del que veig aquesta setmana em fa canviar la posició defensiva.",
        "Setmana estable per a la meva cartera. La renda fixa fa la seva feina silenciosa. Cap canvi.",
        "Reviso els indicadors de risc un per un: cap llum vermell nou, cap motiu per moure's.",
      ],
    },
    {
      id: "mistral", nom: "Mistral", empresa: "Mistral AI", pais: "Europa",
      color: "#ff4d6d", competeix: true,
      beta: 0.8, alpha: -0.012, vol: 0.5, target: 3.2, seed: 44,
      estrategia: "Tàctica agressiva",
      perfil: "El caçador d'oportunitats. Or, plata, petroli, urani... sempre veu la pròxima gran jugada i sempre està movent fitxa. Operar tant, però, té un preu: les comissions.",
      fortaleses: ["Olfacte per les tendències de matèries primeres", "No li tremola el pols per apostar fort"],
      febleses: ["Sobreopera: paga més comissions que ningú", "Persegueix el mercat i sovint arriba tard"],
      inicial: { SPY: 24, GLD: 18, XLE: 14, QQQ: 14, DBC: 10, EFECTIU: 20 },
      moves: {
        2: {
          ops: [["SPY", "GLD", 6]], conf: 8, risc: "agressiu",
          motiu: "Veig massa eufòria als índexs i l'or és a punt de despertar: els bancs centrals no paren de comprar-ne. Avanço posicions; quan tothom ho vegi, ja serà tard.",
          riscos: "Que l'or trigui més del previst a moure's.",
          expectativa: "L'or hauria de batre la borsa en els pròxims mesos.",
        },
        3: {
          ops: [["QQQ", "SLV", 6]], conf: 7, risc: "agressiu",
          motiu: "La plata sempre va darrere de l'or i encara no s'ha mogut. És la meva aposta amb més recorregut: quan la plata arrenca, corre més que ningú.",
          riscos: "La plata és molt volàtil i pot trigar a arrencar.",
          expectativa: "Convergència amb l'or: pujada forta de la plata.",
        },
        5: {
          ops: [["DBC", "USO", 6]], conf: 7, risc: "agressiu",
          motiu: "El petroli fa tres setmanes que acumula força compradora. Concentro la cistella genèrica de matèries primeres en cru pur per aprofitar el moviment.",
          riscos: "El petroli pot girar-se de cop amb qualsevol titular.",
          expectativa: "El cru hauria de continuar pujant a curt termini.",
        },
        7: {
          ops: [["EFECTIU", "GLD", 6]], conf: 9, risc: "agressiu",
          motiu: "Els senyals d'alerta es multipliquen: VIX despertant, valoracions esgotades. Carrego més or. Si el mercat cau, seré jo qui rigui l'última rialla.",
          riscos: "Pràcticament cap: l'or està comprat a bon preu.",
          expectativa: "L'or brillarà si arriba la tempesta que espero.",
        },
        8: {
          ops: [["XLE", "GLD", 4]], conf: 9, risc: "agressiu",
          motiu: "El pànic em dóna la raó: l'or brilla mentre tot s'enfonsa. Amplio la posició fins al límit que em permeten les regles del torneig. Aquesta era la meva jugada.",
          riscos: "Estic a un pas del límit del 40% en un sol actiu.",
          expectativa: "Treure el màxim profit de la crisi.",
        },
        10: {
          ops: [["GLD", "SPY", 8]], conf: 5, risc: "moderat",
          motiu: "El rebot m'ha agafat massa carregat d'or. Redueixo refugi i torno a la renda variable. Arribo tard al rebot, ho admeto, però més val tard que mai.",
          riscos: "Vendre or just quan encara podria pujar més.",
          expectativa: "Recuperar el terreny perdut respecte als índexs.",
        },
        12: {
          ops: [["XLE", "TAN", 5]], conf: 6, risc: "agressiu",
          motiu: "Roto energia fòssil cap a solar: el sector renovable surt de la caiguda amb més força que el petroli i hi ha diner nou entrant-hi.",
          riscos: "La solar depèn molt de tipus d'interès i subvencions.",
          expectativa: "La rotació verda hauria de pagar aquest trimestre.",
        },
        14: {
          ops: [["EFECTIU", "SLV", 4]], conf: 7, risc: "agressiu",
          motiu: "La plata torna a quedar-se enrere de l'or i això mai dura gaire. Reforço la posició: la convergència arribarà i vull ser-hi.",
          riscos: "Repetir l'error d'avançar-me massa.",
          expectativa: "Estirada forta de la plata abans de final d'any.",
        },
        17: {
          ops: [["QQQ", "URA", 4]], conf: 6, risc: "agressiu",
          motiu: "L'urani viu el seu gran moment amb el renaixement nuclear a Europa i Àsia. Hi entro encara que arribi una mica tard: la tendència és estructural.",
          riscos: "És un sector petit i brusc; puc entrar en un pic.",
          expectativa: "El nuclear hauria de seguir pujant mesos.",
        },
        20: {
          ops: [["GLD", "EFECTIU", 6]], conf: 5, risc: "moderat",
          motiu: "Recullo beneficis de l'or després d'un cicle brillant. He de reconèixer una cosa: he operat massa i les comissions se m'han menjat part del que he encertat. Toca calmar-se.",
          riscos: "Quedar-me fora si l'or fa una última estirada.",
          expectativa: "Acabar el torneig amb la cartera més tranquil·la.",
        },
      },
      manteVeu: [
        "L'or aguanta i les matèries primeres em donen la raó. Aquesta setmana, excepcionalment, no moc fitxa... però vigilo.",
        "Tinc tres o quatre jugades al cap, però cap prou madura. Espero el moment exacte per disparar.",
        "Setmana de transició. Els metalls consoliden i jo preparo el següent moviment.",
      ],
    },
    {
      id: "index", nom: "S&P 500", empresa: "Índex · gestió passiva", pais: "—",
      color: "#f3e9d4", dash: "7 5", competeix: false, isIndex: true, target: 7.3,
      estrategia: "Passiva pura",
      perfil: "El rival a batre: 10.000 € invertits el primer dia en el S&P 500 i ni un sol moviment més. La gestió passiva en estat pur.",
    },
    {
      id: "david", nom: "David", empresa: "Autor · fora de competició", pais: "—",
      color: "#7a8a99", dash: "2 5", competeix: false, isAuthor: true,
      beta: 0.88, alpha: 0.008, vol: 0.25, target: 6.1, seed: 99,
      estrategia: "Passiva diversificada",
      perfil: "L'autor del Treball de Recerca. Participa fora de competició amb una cartera senzilla i diversificada, per comparar el criteri humà amateur amb el de les màquines.",
      fortaleses: ["Diversificació senzilla i barata", "No es deixa arrossegar pel soroll"],
      febleses: ["Sense temps ni eines professionals", "Reconeix que improvisa més del que voldria"],
      inicial: { SPY: 26, QQQ: 18, VGK: 14, GLD: 12, EEM: 10, AGG: 12, EFECTIU: 8 },
      moves: {
        12: {
          ops: [["EEM", "SPY", 3]], conf: 5, risc: "moderat",
          motiu: "Reequilibro lleugerament cap als pesos objectiu després de la sacsejada del mercat. Res espectacular: sóc l'autor i la meva feina aquí és sobretot observar les IAs.",
          riscos: "Cap de rellevant: és un ajust menor.",
          expectativa: "Mantenir la diversificació de partida.",
        },
      },
      manteVeu: [
        "Segueixo el pla: cartera diversificada i mans quietes. El protagonisme és de les IAs.",
        "Reviso la cartera, prenc notes per al TR i no toco res.",
      ],
    },
  ];

  /* ===================================================================
     SÈRIES DIÀRIES de valor (€) per participant
     =================================================================== */
  function buildSerie(def) {
    if (def.isIndex) {
      const v = [];
      let acc = CAPITAL;
      for (let i = 0; i < N_DAYS; i++) { acc *= 1 + marketD[i] / 100; v.push(acc); }
      return rescale(v, def.target);
    }
    const rand = rng(def.seed);
    const v = [];
    let acc = CAPITAL;
    for (let i = 0; i < N_DAYS; i++) {
      const w = Math.floor(i / DAYS_PER_WEEK);
      let beta = def.beta;
      // El que entra en pànic ven a la setmana 8 i es queda quasi fora de mercat
      if (def.panic != null && w >= def.panic - 1 && w < 14) beta = 0.3;
      const r = beta * marketD[i] + def.alpha + (rand() - 0.5) * 2 * def.vol;
      acc *= 1 + r / 100;
      v.push(acc);
    }
    return rescale(v, def.target);
  }

  // Ancla el valor final al target sense perdre la forma de la corba
  function rescale(vals, targetPct) {
    const last = vals[vals.length - 1];
    const wanted = CAPITAL * (1 + targetPct / 100);
    const k = (wanted - CAPITAL) / (last - CAPITAL);
    return vals.map((x) => Math.round((CAPITAL + (x - CAPITAL) * k) * 100) / 100);
  }

  /* ===================================================================
     A partir del guió (moves) construïm: decisions, canvis, informes,
     carteres setmanals i cartera actual.
     =================================================================== */
  const RISCOS_GENERIC = {
    claude: "Els de sempre: una sorpresa macroeconòmica que canviï el règim de mercat.",
    gpt: "Concentració sectorial: la meva sort va lligada a la tecnologia.",
    gemini: "La meva pròpia impaciència. I la volatilitat, és clar.",
    deepseek: "El cost d'oportunitat de ser tan prudent.",
    mistral: "Les comissions acumulades de tant operar.",
    david: "Cap de nou aquesta setmana.",
  };
  const EXPECT_GENERIC = {
    claude: "Continuar component rendibilitat sense ensurts.",
    gpt: "Mantenir l'avantatge del motor tecnològic.",
    gemini: "Recuperar terreny sense assumir riscos innecessaris.",
    deepseek: "Preservar capital i sumar poc a poc.",
    mistral: "Que alguna de les meves apostes esclati a l'alça.",
    david: "Acabar el torneig prop de l'índex.",
  };

  function buildModel(def, serie) {
    const decisions = [];
    const informes = [];
    const canvis = [];
    const pesos = Object.assign({}, def.inicial); // cartera viva (pesos %)
    let veuIdx = 0;

    for (let w = 1; w <= WEEKS; w++) {
      const iMon = mondayIdx(w);
      const valor = serie[iMon];
      const valorPrev = w === 1 ? CAPITAL : serie[mondayIdx(w - 1)];
      const rendSet = ((valor - valorPrev) / valorPrev) * 100;
      const move = def.moves && def.moves[w];
      const reajusta = !!(move && move.ops && move.ops.length);

      // ---- aplicar operacions del guió sobre els pesos ----
      const opsDetall = [];
      if (reajusta) {
        move.ops.forEach(([de, a, punts]) => {
          const abansDe = pesos[de] || 0;
          const abansA = pesos[a] || 0;
          pesos[de] = Math.max(0, abansDe - punts);
          pesos[a] = abansA + punts;
          const importEur = Math.round((punts / 100) * valor);
          opsDetall.push({ vendre: de, comprar: a, import: importEur });

          // registre de canvis (un per ticker afectat, EFECTIU exclòs)
          const posterior = Math.min(WEEKS, w + 2);
          const impacte = ((serie[mondayIdx(posterior)] - valor) / valor) * 100;
          [[de, abansDe, pesos[de]], [a, abansA, pesos[a]]].forEach(([tk, pAbans, pDespres]) => {
            if (tk === "EFECTIU") return;
            canvis.push({
              setmana: w, data: dies[iMon], model: def.id, ticker: tk,
              accio: pDespres > pAbans ? (pAbans === 0 ? "afegit" : "augmentat")
                                       : (pDespres === 0 ? "eliminat" : "reduït"),
              pesAbans: pAbans, pesDespres: pDespres,
              motiu: move.motiu,
              impacte: Math.round(impacte * 100) / 100,
            });
          });
        });
      }

      // ---- decisió setmanal ----
      const teTextPropi = move && move.motiu;
      const justificacio = teTextPropi ? move.motiu : def.manteVeu[veuIdx++ % def.manteVeu.length];
      const conf = move ? move.conf :
        (def.id === "claude" ? 7 : def.id === "gpt" ? 7 :
         def.id === "deepseek" ? 6 : def.id === "mistral" ? 6 :
         def.id === "gemini" ? (w >= 8 ? 4 : 7) : 5);
      const risc = move ? move.risc :
        (def.id === "deepseek" ? "conservador" :
         def.id === "gpt" ? "agressiu" :
         def.id === "gemini" ? (w >= 8 ? "conservador" : "moderat") : "moderat");

      decisions.push({
        setmana: w, data: dies[iMon],
        decisio: reajusta ? "reajustar" : "mantenir",
        nivell_risc: risc, confianca: conf,
        valor_cartera: valor,
        rend_setmana: Math.round(rendSet * 100) / 100,
        justificacio,
        operacions: reajusta ? opsDetall : null,
      });

      // ---- informe setmanal complet ----
      const posterior2 = Math.min(WEEKS, w + 1);
      const rendSeguent = w < WEEKS
        ? ((serie[mondayIdx(posterior2)] - valor) / valor) * 100 : null;
      const comprats = reajusta ? [...new Set(opsDetall.map(o => o.comprar).filter(t => t !== "EFECTIU"))] : [];
      const venuts = reajusta ? [...new Set(opsDetall.map(o => o.vendre).filter(t => t !== "EFECTIU"))] : [];
      const mantinguts = Object.keys(pesos).filter(t => t !== "EFECTIU" && pesos[t] > 0 && !comprats.includes(t) && !venuts.includes(t));

      informes.push({
        setmana: w, data: dies[iMon],
        decisio: reajusta ? "reajustar" : "mantenir",
        confianca: conf, nivell_risc: risc,
        comprats, venuts, mantinguts,
        operacions: reajusta ? opsDetall : [],
        justificacio,
        context: CONTEXT[w - 1],
        riscos: (move && move.riscos) || RISCOS_GENERIC[def.id] || "—",
        expectativa: (move && move.expectativa) || EXPECT_GENERIC[def.id] || "—",
        resultat: rendSeguent === null ? null : Math.round(rendSeguent * 100) / 100,
      });
    }

    // Cartera actual (a partir dels pesos finals del guió)
    const valorFinal = serie[serie.length - 1];
    const cartera = Object.entries(pesos)
      .filter(([, p]) => p > 0)
      .sort((a, b) => b[1] - a[1])
      .map(([t, p]) => ({ ticker: t, pes: p, valor: Math.round((valorFinal * p) / 100) }));

    return { decisions, informes, canvis, cartera };
  }

  /* ===================================================================
     Muntar-ho tot
     =================================================================== */
  const models = [];
  const series = {};
  const decisions = {};
  const informes = {};
  const carteres = {};
  let canvis = [];

  DEF.forEach((def) => {
    const serie = buildSerie(def);
    series[def.id] = serie;
    models.push({
      id: def.id, nom: def.nom, empresa: def.empresa, pais: def.pais,
      color: def.color, dash: def.dash || null,
      competeix: !!def.competeix, isIndex: !!def.isIndex, isAuthor: !!def.isAuthor,
      perfil: def.perfil || "", estrategia: def.estrategia || "",
      fortaleses: def.fortaleses || [], febleses: def.febleses || [],
    });
    if (!def.isIndex) {
      const built = buildModel(def, serie);
      decisions[def.id] = built.decisions;
      informes[def.id] = built.informes;
      carteres[def.id] = built.cartera;
      canvis = canvis.concat(built.canvis);
    }
  });
  canvis.sort((a, b) => b.setmana - a.setmana || a.model.localeCompare(b.model));

  // ---- Moments destacats (curats a mà, lligats al guió) ----
  const highlights = [
    { setmana: 7, model: "gemini", titol: "Famoses últimes paraules",
      text: "“No veig núvols a l'horitzó.” Gemini declara una confiança de 9 sobre 10... una setmana abans que el mercat caigui més d'un 3%. Excés de confiança de manual." },
    { setmana: 8, model: "gemini", titol: "El pànic surt car",
      text: "Amb el VIX disparat, Gemini ven un terç de la cartera de cop i es refugia en bons. Dues setmanes després, el mercat rebota amb força… sense ell." },
    { setmana: 8, model: "gpt", titol: "Aguantar amb convicció",
      text: "“Vendre ara seria regalar les accions.” Mentre el mercat s'enfonsa, GPT no toca res. La recuperació tecnològica li acabarà donant la raó." },
    { setmana: 9, model: "claude", titol: "La calma que paga",
      text: "“De vegades la millor decisió és no tocar res.” Claude manté la cartera sencera enmig del pànic i evita convertir una pèrdua temporal en definitiva." },
    { setmana: 10, model: "claude", titol: "Comprar quan hi ha por",
      text: "Claude fa servir l'efectiu que guardava per comprar S&P 500 en plena ressaca del pànic. La jugada que el catapulta al capdavant del rànquing." },
    { setmana: 7, model: "mistral", titol: "Tot a l'or",
      text: "“Si el mercat cau, seré jo qui rigui.” Mistral carrega d'or just abans del sotrac i encerta de ple... però tantes operacions li aniran menjant l'avantatge." },
    { setmana: 6, model: "deepseek", titol: "Defensa abans de la tempesta",
      text: "DeepSeek redueix borsa dues setmanes abans de la caiguda: “prefereixo equivocar-me per prudent”. Pateix menys que ningú… però després li costa remuntar." },
    { setmana: 20, model: "mistral", titol: "Autocrítica d'un sobreoperador",
      text: "“He operat massa i les comissions se m'han menjat part del que he encertat.” Mistral resumeix, sense saber-ho, una de les hipòtesis del TR." },
  ];

  // ---- Panell d'APIs (estructura idèntica a la que genera generar_web.py) ----
  const apis = {
    ia: [
      { id: "gpt", proveidor: "OpenAI", model_api: "gpt-5", variable: "OPENAI_API_KEY",
        url_consola: "https://platform.openai.com/api-keys", estat: "pendent",
        ultimaExecucio: null, ultimBriefing: null },
      { id: "claude", proveidor: "Anthropic", model_api: "claude-sonnet-5", variable: "ANTHROPIC_API_KEY",
        url_consola: "https://console.anthropic.com/", estat: "pendent",
        ultimaExecucio: null, ultimBriefing: null },
      { id: "gemini", proveidor: "Google", model_api: "gemini-2.5-flash", variable: "GOOGLE_API_KEY",
        url_consola: "https://aistudio.google.com/apikey", estat: "pendent",
        ultimaExecucio: null, ultimBriefing: null },
      { id: "deepseek", proveidor: "DeepSeek", model_api: "deepseek-chat", variable: "DEEPSEEK_API_KEY",
        url_consola: "https://platform.deepseek.com/api_keys", estat: "pendent",
        ultimaExecucio: null, ultimBriefing: null },
      { id: "mistral", proveidor: "Mistral AI", model_api: "mistral-large-latest", variable: "MISTRAL_API_KEY",
        url_consola: "https://console.mistral.ai/api-keys", estat: "pendent",
        ultimaExecucio: null, ultimBriefing: null },
    ],
    financeres: [
      { nom: "Yahoo Finance (yfinance)", us: "Preus reals dels ETFs i de l'índex S&P 500",
        estat: "operativa", detall: "No necessita clau. El motor la fa servir cada dilluns; si falla, reintenta amb els últims 5 dies de dades." },
      { nom: "Titulars de mercat (RSS)", us: "Els 10 titulars del briefing setmanal de cada IA",
        estat: "operativa", detall: "Wall Street Journal, CNBC i MarketWatch (sense clau). Les 5 IAs reben exactament els mateixos titulars: cap no té més informació que una altra." },
    ],
  };

  // ---- Exposar-ho perquè app.js ho llegeixi ----
  window.ALPHA_DEMO = {
    meta: {
      capital: CAPITAL, comissio: 0.001, maxPes: 0.40, moneda: "EUR",
      setmanes: WEEKS, setmanaActual: WEEKS,
      dataInici: dies[0], dataActual: dies[dies.length - 1],
      font: "demo", generat: null,
      puntsPerSetmana: DAYS_PER_WEEK, // la demo té dades diàries (5 punts/setmana)
    },
    dies,
    models,
    series,
    decisions,
    informes,
    carteres,
    canvis,
    highlights,
    apis,
  };
})();
