# -*- coding: utf-8 -*-
"""
torneo.py — EL MOTOR del torneo ALPHA ARTIFICIAL
=================================================
Este es el programa principal. Cada vez que se ejecuta hace UNA ronda
semanal completa:

  1. Baja los precios reales de los ETFs (yfinance).
  2. Recupera el estado del torneo (carteras de la semana pasada).
  3. Monta el briefing idéntico para todas las IAs.
  4. Pregunta a cada IA qué hace con su cartera.
  5. Comprueba que la decisión cumple las reglas y la APLICA de verdad
     (compra/venta con comisión del 0,1% y regla del 40%).
  6. Guarda TODO con historial: decisions.csv, canvis.csv, carteres.csv,
     index.csv (la línea del S&P 500) y el estado para la semana siguiente.

IMPORTANTE: de momento funciona en "MODE_SIMULAT". Eso significa que,
en vez de llamar a las IAs de verdad (que necesitan claves API y dinero),
una IA de mentira toma decisiones de prueba. Cuando tengas las claves,
pon la clave en secrets.txt, marca 'actiu': True en config.py y cambia
MODE_SIMULAT a False. Las llamadas reales ya están escritas
(connectors_ia.py); no hay que programar nada más.

Para ejecutarlo:  python torneo.py
Después, para actualizar la web:  python generar_web.py
"""

import os
import sys
import csv
import json
import random
import datetime
import config
import connectors_ia

# La consola de Windows a veces no entiende símbolos como → o ✓.
# Esto la pone en UTF-8 para que los mensajes se vean bien.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ============================================================
#  INTERRUPTOR PRINCIPAL
# ============================================================
# True  = usa IAs de mentira (para probar, gratis).
# False = llama a las IAs reales (necesita claves API).
# El 09/07/2026 se puso en False: el torneo está ARMADO. Cada ejecución
# cuenta como una ronda oficial y gasta unos céntimos de API.
MODE_SIMULAT = False

RUTA_ESTAT = os.path.join(config.CARPETA_DADES, "estat_torneig.json")
RUTA_DECISIONS = os.path.join(config.CARPETA_DADES, "decisions.csv")
RUTA_CANVIS = os.path.join(config.CARPETA_DADES, "canvis.csv")
RUTA_CARTERES = os.path.join(config.CARPETA_DADES, "carteres.csv")
RUTA_INDEX = os.path.join(config.CARPETA_DADES, "index.csv")
RUTA_COMISSIONS = os.path.join(config.CARPETA_DADES, "comissions.csv")
RUTA_TITULARS = os.path.join(config.CARPETA_DADES, "titulars.csv")
RUTA_DIVIDENDS = os.path.join(config.CARPETA_DADES, "dividends.csv")

# Data de l'última sessió de borsa dels preus baixats. L'omple baixar_preus().
ULTIMA_DATA_MERCAT = None


# ============================================================
#  PASO 1 — Bajar precios reales del mercado
# ============================================================
def baixar_preus():
    """Descarga el precio de todos los activos del universo (ETFs + acciones),
    los indicadores de contexto y los tipos de cambio. Devuelve los precios YA
    CONVERTIDOS A EUROS, que es la moneda del torneo.

    Esto último es importante: Apple cotiza en dólares, Inditex en euros y
    Shell en peniques. Sumarlos sin convertir daría un valor de cartera falso."""
    import yfinance as yf

    actius = config.tots_els_actius()
    parells = [d["parell"] for d in config.DIVISES.values() if d["parell"]]
    tickers = list(actius.keys()) + list(config.INDICADORS_CONTEXT.keys()) + parells
    print(f"[1] Baixant preus de {len(tickers)} símbols (ETFs, accions i divises)...")

    # yfinance permite bajar muchos de golpe; pedimos los últimos 5 días
    # y nos quedamos con el cierre más reciente de cada uno.
    dades = yf.download(tickers, period="5d", progress=False)

    # Guardem QUIN DIA és el preu que acabem de baixar. No és el mateix que
    # "avui": si el robot s'endarrereix i s'executa a la matinada o en dissabte,
    # el preu que dóna Yahoo segueix sent el de l'última sessió de borsa.
    # Datar pel dia real de mercat evita dies fantasma i dies perduts.
    global ULTIMA_DATA_MERCAT
    try:
        ULTIMA_DATA_MERCAT = dades["Close"]["SPY"].dropna().index[-1].date().isoformat()
    except Exception:
        ULTIMA_DATA_MERCAT = None

    bruts = {}
    for t in tickers:
        try:
            serie = dades["Close"][t].dropna()
            bruts[t] = round(float(serie.iloc[-1]), 4)
        except Exception:
            bruts[t] = None  # si algún ticker falla, lo marcamos como None

    # --- Convertir cada precio a euros ---
    preus = {}
    for t, valor in bruts.items():
        if valor is None:
            preus[t] = None
            continue
        info = actius.get(t)
        if info is None:
            preus[t] = valor      # indicadores y divisas: se dejan tal cual
            continue
        preus[t] = a_euros(valor, info["moneda"], bruts)

    obtinguts = sum(1 for t in actius if preus.get(t) is not None)
    canvi = bruts.get("EURUSD=X")
    print(f"    {obtinguts}/{len(actius)} actius amb preu (convertits a euros)."
          + (f" EUR/USD: {canvi}" if canvi else ""))
    return preus


def a_euros(valor, moneda, bruts):
    """Convierte un precio a euros. 'bruts' trae los tipos de cambio del día.
    Ejemplo: Apple a 337 USD con EUR/USD = 1,14 → 337 / 1,14 = 295,61 €."""
    dades = config.DIVISES.get(moneda)
    if dades is None:
        return round(valor, 4)
    valor = valor * dades["factor"]        # peniques → libras, etc.
    if dades["parell"] is None:
        return round(valor, 4)             # ya está en euros
    canvi = bruts.get(dades["parell"])
    if not canvi:
        return None                        # sin tipo de cambio no inventamos nada
    return round(valor / canvi, 4)


# ============================================================
#  PASO 2 — Estado del torneo (la memoria entre semanas)
# ============================================================
def ja_jugat_aquesta_setmana():
    """¿Ya se ha jugado una ronda esta semana (de lunes a domingo)?

    Sirve para poder INTENTAR la ronda varias veces el mismo lunes sin que se
    juegue dos veces. GitHub Actions es poco puntual con las tareas
    programadas —llega tarde y a veces se salta una— así que en vez de una
    sola oportunidad a las 07:37 UTC, el robot lo intenta cada dos horas.
    La primera que entra juega; las demás ven que ya está hecho y no tocan
    nada."""
    if not os.path.exists(RUTA_DECISIONS):
        return False
    try:
        with open(RUTA_DECISIONS, encoding="utf-8") as f:
            files = list(csv.DictReader(f))
    except OSError:
        return False
    if not files:
        return False

    avui = datetime.date.today()
    setmana_avui = avui.isocalendar()[:2]      # (any, número de setmana)
    for fila in reversed(files):
        data = (fila.get("data") or "").strip()
        if not data:
            continue
        try:
            d = datetime.date.fromisoformat(data)
        except ValueError:
            continue
        if d.isocalendar()[:2] == setmana_avui:
            return True
        if d < avui - datetime.timedelta(days=14):
            break        # ya estamos mirando datos viejos
    return False


def carregar_estat():
    """Lee dades/estat_torneig.json. Si no existe, es la semana 0 (aún no
    ha empezado): devolvemos un estado vacío."""
    if os.path.exists(RUTA_ESTAT):
        with open(RUTA_ESTAT, encoding="utf-8") as f:
            return json.load(f)
    return {"setmana": 0, "carteres": {}, "index_unitats": None}


def guardar_estat(estat):
    os.makedirs(config.CARPETA_DADES, exist_ok=True)
    with open(RUTA_ESTAT, "w", encoding="utf-8") as f:
        json.dump(estat, f, ensure_ascii=False, indent=2)


def cartera_inicial(preus):
    """Cartera de partida: reparte los 10.000 € en unos pocos ETFs
    de forma equilibrada (todos arrancan 100% invertidos, como acordamos)."""
    base = ["SPY", "VGK", "GLD", "TLT", "QQQ"]  # reparto inicial sencillo
    per_etf = config.CAPITAL_INICIAL / len(base)
    cartera = {"EFECTIU": 0.0}
    for tk in base:
        p = preus.get(tk)
        if p:
            cartera[tk] = round(per_etf / p, 4)  # cuántas unidades compro
    return cartera


def cobrar_dividends(estat, preus):
    """Cobra els dividends que han pagat els actius des de l'última ronda.

    PER QUÈ CAL AIXÒ: els fons i les accions reparteixen diners als seus
    propietaris (dividends) unes quantes vegades l'any. Yahoo Finance dóna el
    preu SENSE comptar-los, així que sense aquesta funció el torneig
    infravaloraria el que tindria de veritat qualsevol inversor: en una
    compte real aquests diners es cobren i es queden en efectiu.

    L'S&P 500 (SPY) paga cada trimestre, al març, juny, setembre i desembre.
    Entre el juliol i l'agost no n'hi va haver cap, però al setembre i al
    desembre sí, i afecten tant les IAs com l'índex.

    Torna la llista de cobraments aplicats."""
    import yfinance as yf

    avui = datetime.date.today()
    desde = estat.get("ultim_dividend")
    if not desde:
        # Primera vegada: comencem a comptar des d'avui, no des de l'inici
        # del torneig (els dividends anteriors no es van cobrar mai).
        estat["ultim_dividend"] = avui.isoformat()
        print("    (primera vegada: els dividends es comptaran a partir d'avui)")
        return []
    desde = datetime.date.fromisoformat(desde)
    if desde >= avui:
        return []

    # Quins actius té algú a la cartera (i l'índex)
    tinguts = {"SPY"}
    for cartera in estat.get("carteres", {}).values():
        tinguts.update(t for t, u in cartera.items() if t != "EFECTIU" and u > 0)

    actius = config.tots_els_actius()
    cobraments = []
    for tk in sorted(tinguts):
        try:
            divs = yf.Ticker(tk).dividends
        except Exception:
            continue
        if divs is None or len(divs) == 0:
            continue
        for data_pag, import_brut in divs.items():
            dia = data_pag.date() if hasattr(data_pag, "date") else data_pag
            if not (desde < dia <= avui):
                continue
            # El dividend ve en la moneda de l'actiu: cal passar-lo a euros
            moneda = actius.get(tk, {}).get("moneda", "USD")
            d = config.DIVISES.get(moneda, {"parell": None, "factor": 1.0})
            per_unitat = float(import_brut) * d["factor"]
            if d["parell"]:
                canvi = preus.get(d["parell"])
                if not canvi:
                    continue
                per_unitat = per_unitat / canvi

            # Cada IA cobra segons les unitats que tingui
            for mid, cartera in estat.get("carteres", {}).items():
                unitats = cartera.get(tk, 0)
                if unitats > 0:
                    cobrat = unitats * per_unitat
                    cartera["EFECTIU"] = cartera.get("EFECTIU", 0) + cobrat
                    cobraments.append((mid, tk, dia.isoformat(), round(cobrat, 2)))

            # I l'índex també: es reinverteix comprant més participacions
            if tk == "SPY" and estat.get("index_unitats") and preus.get("SPY"):
                cobrat = estat["index_unitats"] * per_unitat
                estat["index_unitats"] += cobrat / preus["SPY"]
                cobraments.append(("index", tk, dia.isoformat(), round(cobrat, 2)))

    estat["ultim_dividend"] = avui.isoformat()

    if cobraments:
        total = sum(c[3] for c in cobraments)
        print(f"    {len(cobraments)} cobraments de dividends, {total:.2f} € en total:")
        for mid, tk, dia, imp in cobraments:
            print(f"       {mid:10} {tk:9} {dia}  +{imp:.2f} €")
            _afegir_fila(RUTA_DIVIDENDS,
                ["data_cobrament", "data_pagament", "model", "ticker", "import_eur"],
                [avui.isoformat(), dia, mid, tk, imp])
    else:
        print("    Cap dividend a cobrar aquesta setmana.")
    return cobraments


def valor_cartera(cartera, preus):
    """Calcula el valor total en euros de una cartera."""
    total = cartera.get("EFECTIU", 0)
    for tk, unitats in cartera.items():
        if tk == "EFECTIU":
            continue
        p = preus.get(tk)
        if p:
            total += unitats * p
    return total


# ============================================================
#  PASO 3 — Montar el briefing semanal (igual para todas)
# ============================================================
def carregar_prompt():
    """Lee el archivo del prompt semanal."""
    ruta = os.path.join(config.CARPETA_PROMPTS, "prompt_setmanal.txt")
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def carregar_variacions():
    """Calcula quant ha pujat o baixat cada actiu en 1 setmana, 1 mes i 1 any,
    a partir de l'historial que genera generar_historic.py.

    PER QUÈ EXISTEIX AIXÒ (30/07/2026): abans, el briefing només donava el
    preu d'avui. Amb un ETF n'hi ha prou (el nom ja diu què compres: "Or
    físic", "Bons EUA 20+ anys"), però amb una acció el preu sol no diu res:
    saber que Apple val 296 € no et permet decidir si comprar-la. Les cinc
    IAs van dir explícitament que per això treballaven gairebé només amb
    ETFs. Aquestes dades igualen el terreny: són les mateixes que té a la
    pantalla qualsevol gestor real, i es donen per a TOTS els actius per
    igual, sense afavorir accions ni fons.

    Torna {ticker: {"s": %1setmana, "m": %1mes, "a": %1any}}.
    Si no hi ha historial, torna {} i el briefing simplement no les mostra."""
    ruta = os.path.join("web", "historic.json")
    if not os.path.exists(ruta):
        print("    [i] Sense web/historic.json: el briefing no portarà variacions.")
        return {}
    try:
        with open(ruta, encoding="utf-8") as f:
            hist = json.load(f)
    except (ValueError, OSError):
        return {}

    diari = hist.get("diari", {}).get("preus", {})
    setmanal = hist.get("setmanal", {}).get("preus", {})

    def variacio(serie, punts_enrere):
        """% de canvi entre fa 'punts_enrere' punts i l'últim valor."""
        nets = [v for v in serie if v is not None]
        if len(nets) < 2:
            return None
        actual = nets[-1]
        i = max(0, len(nets) - 1 - punts_enrere)
        abans = nets[i]
        if not abans:
            return None
        return round((actual / abans - 1) * 100, 1)

    variacions = {}
    for tk in config.tots_els_actius():
        d, s = diari.get(tk), setmanal.get(tk)
        if not d and not s:
            continue
        variacions[tk] = {
            "s": variacio(d, 5) if d else None,       # ~5 dies de mercat
            "m": variacio(d, 21) if d else None,      # ~21 dies de mercat
            "a": variacio(d, 252) if d else (variacio(s, 52) if s else None),
        }
    if variacions:
        print(f"    Variacions de mercat calculades per a {len(variacions)} actius.")
    return variacions


def obtenir_titulars():
    """Baja los titulares de actualidad y devuelve los más recientes y
    relevantes. Se piden UNA vez por ronda y se dan idénticos a las 5 IAs,
    para que ninguna tenga más información que otra (control de variables).

    Reglas importantes (ver el aviso en config.py):
      · Se descarta cualquier noticia de más de MAX_DIES_TITULAR días. Un feed
        abandonado sirve las mismas noticias durante años y envenenaría el
        experimento.
      · Se recogen titulares de TODAS las fuentes y se mezclan, en vez de
        llenar el cupo con la primera.
      · Se priorizan los titulares de mercados/economía sobre los de consumo.
    Si no se consigue nada fresco, devuelve None y el briefing lo dirá."""
    try:
        import feedparser
    except ImportError:
        print("    [!] Falta la llibreria feedparser (pip install feedparser).")
        return None

    ara = datetime.datetime.now(datetime.timezone.utc)

    def antiguitat(entrada):
        """Días desde la publicación, o None si el feed no da fecha."""
        for camp in ("published_parsed", "updated_parsed"):
            valor = getattr(entrada, camp, None)
            if valor:
                try:
                    dt = datetime.datetime(*valor[:6], tzinfo=datetime.timezone.utc)
                    return (ara - dt).days
                except (TypeError, ValueError):
                    continue
        return None

    def es_rellevant(titol):
        t = titol.lower()
        return any(p in t for p in config.PARAULES_RELLEVANTS)

    # --- Recollir de cada font per separat ---
    per_font = []
    fonts_obsoletes = []
    for url in config.FONTS_TITULARS:
        try:
            canal = feedparser.parse(url)
        except Exception:
            continue
        if not getattr(canal, "entries", None):
            continue

        frescos, mes_nou = [], None
        for entrada in canal.entries[:15]:
            titol = " ".join((entrada.get("title") or "").split())
            if not titol:
                continue
            dies = antiguitat(entrada)
            if dies is not None:
                mes_nou = dies if mes_nou is None else min(mes_nou, dies)
                if dies > config.MAX_DIES_TITULAR:
                    continue          # noticia vella: fora
            frescos.append((titol, dies if dies is not None else 99))

        # Avisar si tota la font està obsoleta (com el WSJ el 2026)
        nom_font = url.split("/")[2]
        if mes_nou is not None and mes_nou > config.MAX_DIES_TITULAR:
            fonts_obsoletes.append(f"{nom_font} ({mes_nou} dies)")
            continue
        if frescos:
            # dins de cada font, primer les rellevants i les més recents
            frescos.sort(key=lambda x: (not es_rellevant(x[0]), x[1]))
            per_font.append(frescos)

    if fonts_obsoletes:
        print(f"    [!] Fonts obsoletes ignorades: {', '.join(fonts_obsoletes)}")
    if not per_font:
        print("    [!] Cap font ha donat titulars recents.")
        return None

    # --- Mezclar: uno de cada fuente por turnos (round-robin) ---
    # Así ninguna fuente monopoliza el briefing y hay variedad de enfoques.
    # Se hacen dos pasadas: primero solo titulares de mercados/economía y,
    # si no se llena el cupo, se completa con el resto (MarketWatch y Yahoo
    # mezclan noticias de consumo que no aportan nada a una decisión de
    # inversión).
    titulars, vistos = [], set()

    def recollir(nomes_rellevants):
        for volta in range(15):
            if len(titulars) >= config.N_TITULARS:
                return
            for llista in per_font:
                if volta >= len(llista) or len(titulars) >= config.N_TITULARS:
                    continue
                titol = llista[volta][0]
                if nomes_rellevants and not es_rellevant(titol):
                    continue
                clau = titol.lower()[:60]
                if clau in vistos:
                    continue
                vistos.add(clau)
                titulars.append(titol)

    recollir(nomes_rellevants=True)
    if len(titulars) < config.N_TITULARS:
        recollir(nomes_rellevants=False)

    if not titulars:
        return None
    print(f"    {len(titulars)} titulars recents de {len(per_font)} fonts diferents.")
    return "\n".join(f"  {i + 1}. {t}" for i, t in enumerate(titulars))


def historial_model(model_id, maxim=8):
    """Resume las últimas decisiones de esta IA para recordárselas en el
    briefing (así puede ser coherente consigo misma)."""
    if not os.path.exists(RUTA_DECISIONS):
        return None
    with open(RUTA_DECISIONS, encoding="utf-8") as f:
        files = [x for x in csv.DictReader(f) if x.get("model") == model_id]
    if not files:
        return None
    linies = []
    for x in files[-maxim:]:
        linies.append(
            f"  S{x['setmana']}: {x['decisio']} (risc {x['nivell_risc']}, "
            f"confiança {x['confianca']}/10, cartera {x['valor_cartera']} €) — {x['justificacio'][:140]}"
        )
    return "\n".join(linies)


def valor_setmana_anterior(model_id):
    """Último valor de cartera apuntado para esta IA (para calcular la
    rendibilidad semanal que se le enseña en el briefing)."""
    if not os.path.exists(RUTA_DECISIONS):
        return None
    with open(RUTA_DECISIONS, encoding="utf-8") as f:
        files = [x for x in csv.DictReader(f) if x.get("model") == model_id]
    if not files:
        return None
    try:
        v = float(files[-1]["valor_cartera"])
        return v if v > 0 else None
    except (KeyError, ValueError):
        return None


def montar_briefing(setmana, preus, cartera, model_id, titulars=None, variacions=None):
    """Rellena los huecos {{...}} del prompt con los datos reales de esta
    semana y de esta IA concreta. Devuelve el texto final a enviar."""
    plantilla = carregar_prompt()

    # --- Lista de activos disponibles, en dos bloques ---
    # Primero las empresas (agrupadas por país, que es como piensa un gestor)
    # y después los fondos. Todos los precios ya vienen en euros, y cada
    # activo lleva su evolución reciente (misma información para todos).
    variacions = variacions or {}

    def evolucio(tk):
        """Text amb l'evolució recent d'un actiu, per posar al costat del preu."""
        v = variacions.get(tk)
        if not v:
            return ""
        parts = []
        for clau, etiqueta in (("s", "1set"), ("m", "1mes"), ("a", "1any")):
            valor = v.get(clau)
            if valor is not None:
                parts.append(f"{etiqueta} {valor:+.1f}%")
        return ("  | " + " · ".join(parts)) if parts else ""

    per_pais = {}
    for tk, (nom, sector, pais, _mon) in config.UNIVERS_ACCIONS.items():
        p = preus.get(tk)
        if p is not None:
            per_pais.setdefault(pais, []).append(
                f"    {tk} — {nom} ({sector}) — {p} €{evolucio(tk)}")

    linies = ["ACCIONS D'EMPRESES CONCRETES (màxim "
              f"{int(config.MAX_PES_PER_ACCIO * 100)}% de la cartera per empresa):"]
    for pais in sorted(per_pais):
        linies.append(f"  · {pais}")
        linies.extend(sorted(per_pais[pais]))

    linies.append("")
    linies.append("FONS COTITZATS / ETFs (màxim "
                  f"{int(config.MAX_PES_PER_ETF * 100)}% de la cartera per fons):")
    per_cat = {}
    for tk, (nom, cat) in config.UNIVERS_ETFS.items():
        p = preus.get(tk)
        if p is not None:
            per_cat.setdefault(cat, []).append(f"    {tk} — {nom} — {p} €{evolucio(tk)}")
    for cat in per_cat:
        linies.append(f"  · {cat}")
        linies.extend(per_cat[cat])

    llista_etfs = "\n".join(linies)

    # Contexto de mercado (VIX, bono, EUR/USD)
    linies_ctx = []
    for sym, nom in config.INDICADORS_CONTEXT.items():
        p = preus.get(sym)
        if p is not None:
            linies_ctx.append(f"  {nom}: {p}")
    context = "\n".join(linies_ctx)

    # Posiciones actuales de la cartera
    actius = config.tots_els_actius()
    valor_total = valor_cartera(cartera, preus)
    linies_pos = []
    for tk, unitats in cartera.items():
        if tk == "EFECTIU" or unitats == 0:
            continue
        p = preus.get(tk)
        if p:
            val = round(unitats * p, 2)
            pes = round(100 * val / valor_total, 1) if valor_total else 0
            nom = actius.get(tk, {}).get("nom", tk)
            limit = int(config.max_pes(tk) * 100)
            linies_pos.append(f"  {tk} ({nom}) — {unitats} unitats — "
                              f"{val} € ({pes}% de {limit}% permès)")
    posicions = "\n".join(linies_pos) if linies_pos else "  (cap posició)"

    # Rendibilidad semanal (comparando con lo apuntado la semana pasada)
    v_ant = valor_setmana_anterior(model_id)
    rend_setmanal = "—"
    if v_ant and valor_total:
        rend_setmanal = str(round(100 * (valor_total / v_ant - 1), 2))

    historial = historial_model(model_id)

    # --- Horitzó: quant queda de torneig ---
    # Un gestor real sempre sap quan es tanca el seu mandat. Li donem el dato
    # i prou; què en fa (ser més prudent, més agressiu, evitar segons quins
    # actius) ho decideix ell, i és part del que estudia el TR.
    try:
        fi = datetime.date.fromisoformat(config.DATA_FI)
        dies_restants = (fi - datetime.date.today()).days
        setmanes_restants = max(0, round(dies_restants / 7))
        data_fi_llegible = fi.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        setmanes_restants, data_fi_llegible = "—", "—"

    # Sustituciones
    text = (plantilla
        .replace("{{NUMERO_SETMANA}}", str(setmana))
        .replace("{{DATA_FI}}", str(data_fi_llegible))
        .replace("{{SETMANES_RESTANTS}}", str(setmanes_restants))
        .replace("{{DATA}}", datetime.date.today().isoformat())
        .replace("{{VALOR_TOTAL}}", str(round(valor_total, 2)))
        .replace("{{POSICIONS_ACTUALS}}", posicions)
        .replace("{{EFECTIU}}", str(round(cartera.get("EFECTIU", 0), 2)))
        .replace("{{REND_SETMANAL}}", rend_setmanal)
        .replace("{{REND_ACUMULADA}}", str(round(100*(valor_total/config.CAPITAL_INICIAL - 1), 2)))
        .replace("{{HISTORIAL}}", historial or "  (cap, primera setmana)")
        .replace("{{LLISTA_ETFS}}", llista_etfs)
        .replace("{{CONTEXT_MERCAT}}", context)
        .replace("{{TITULARS}}", titulars or "  (cap titular disponible aquesta setmana)")
    )
    return text


# ============================================================
#  PASO 4 — Preguntar a cada IA
# ============================================================
def demanar_decisio(model_id, briefing, cartera):
    """Envía el briefing a una IA y devuelve su decisión como diccionario.
    Si MODE_SIMULAT está activo, usa una IA de mentira."""
    if MODE_SIMULAT:
        return decisio_simulada(cartera), ""
    return connectors_ia.demanar(model_id, briefing)


def decisio_simulada(cartera):
    """IA de mentira: toma una decisión de prueba aleatoria pero válida.
    Sirve para comprobar que todo el sistema funciona sin gastar dinero."""
    en_cartera = [t for t, u in cartera.items() if t != "EFECTIU" and u > 0]
    tickers = list(config.UNIVERS_ETFS.keys())
    if random.random() < 0.5 or not en_cartera:
        decisio = "mantenir"
        operacions = []
    else:
        decisio = "reajustar"
        operacions = [{
            "vendre": random.choice(en_cartera),
            "import_eur": random.choice([500, 1000, 1500]),
            "comprar": random.choice(tickers),
        }]
    return {
        "reflexio_historial": "(simulat) Reviso les meves decisions anteriors.",
        "analisi_cartera": "(simulat) Anàlisi de prova de la cartera.",
        "nivell_risc": random.choice(["conservador", "moderat", "agressiu"]),
        "decisio": decisio,
        "operacions": operacions,
        "justificacio": "(simulat) Decisió de prova per validar el sistema.",
        "confianca": random.randint(1, 10),
    }


# ============================================================
#  PASO 5 — Validar y APLICAR la decisión (con reglas de verdad)
# ============================================================
def validar_decisio(decisio):
    """Comprobaciones básicas antes de tocar la cartera."""
    if decisio.get("decisio") == "mantenir":
        return True, ""
    permesos = config.tots_els_actius()
    for op in decisio.get("operacions", []):
        tk_compra = op.get("comprar")
        tk_venda = op.get("vendre")
        if tk_compra and tk_compra not in permesos and tk_compra != "EFECTIU":
            return False, f"Actiu no permès: {tk_compra}"
        if tk_venda and tk_venda not in permesos and tk_venda != "EFECTIU":
            return False, f"Actiu no permès: {tk_venda}"
        if op.get("import_eur", 0) < 0:
            return False, "Import negatiu"
    return True, ""


def aplicar_operacions(cartera, decisio, preus):
    """Ejecuta las operaciones válidas sobre la cartera, cobrando la comisión y
    respetando el límite de concentración (20% por acción, 40% por ETF).
    Devuelve (operaciones aplicadas, comisión total pagada en euros)."""
    aplicades = []
    comissio_pagada = 0.0
    for op in decisio.get("operacions", []):
        tk_v = op.get("vendre")
        tk_c = op.get("comprar")
        import_eur = float(op.get("import_eur", 0) or 0)
        if import_eur <= 0:
            continue

        # --- VENDER (o sacar de efectivo) ---
        if tk_v and tk_v != "EFECTIU":
            p_v = preus.get(tk_v)
            if not p_v or cartera.get(tk_v, 0) <= 0:
                continue
            disponible = cartera[tk_v] * p_v
            import_real = min(import_eur, disponible)
            cartera[tk_v] = round(cartera[tk_v] - import_real / p_v, 6)
            if cartera[tk_v] < 1e-6:
                cartera[tk_v] = 0.0
            # el dinero de la venta entra en efectivo, menos la comisión
            comissio_pagada += import_real * config.COMISSIO
            cartera["EFECTIU"] = cartera.get("EFECTIU", 0) + import_real * (1 - config.COMISSIO)
        else:
            import_real = min(import_eur, cartera.get("EFECTIU", 0))
            if import_real <= 0:
                continue

        # --- COMPRAR ---
        if tk_c:
            p_c = preus.get(tk_c)
            if not p_c:
                continue
            gastar = min(import_real, cartera.get("EFECTIU", 0))
            if gastar <= 0:
                continue
            # Límite de concentración (20% acciones / 40% ETFs): si la compra
            # se pasa del máximo permitido para ESE activo, se recorta.
            valor_total = valor_cartera(cartera, preus)
            valor_tk = cartera.get(tk_c, 0) * p_c
            maxim_permes = config.max_pes(tk_c) * valor_total - valor_tk
            gastar = max(0.0, min(gastar, maxim_permes))
            if gastar <= 0:
                continue
            cartera["EFECTIU"] = cartera.get("EFECTIU", 0) - gastar
            comissio_pagada += gastar * config.COMISSIO
            cartera[tk_c] = round(cartera.get(tk_c, 0) + gastar * (1 - config.COMISSIO) / p_c, 6)
            import_real = gastar

        aplicades.append({"vendre": tk_v or "EFECTIU", "comprar": tk_c or "EFECTIU",
                          "import_eur": round(import_real, 2)})
    return aplicades, round(comissio_pagada, 2)


# ============================================================
#  PASO 6 — Guardar el historial en CSV
# ============================================================
def _assegurar_columnes(ruta, capcalera):
    """Si el CSV ja existeix però amb menys columnes que ara (perquè hem
    afegit dades noves al motor), el reescriu afegint les columnes que falten
    buides. Sense això, les files noves quedarien desalineades respecte a les
    antigues i l'historial es corrompria."""
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as f:
        files = list(csv.reader(f))
    if not files:
        return
    antiga = files[0]
    if antiga == list(capcalera):
        return                      # ja està al dia
    if not set(antiga).issubset(set(capcalera)):
        return                      # canvi estrany: no toquem res
    # Reescriure mantenint els valors que ja hi havia, per nom de columna
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(capcalera)
        for fila in files[1:]:
            reg = dict(zip(antiga, fila))
            w.writerow([reg.get(c, "") for c in capcalera])
    print(f"    [i] {os.path.basename(ruta)}: afegides les columnes noves "
          f"({', '.join(c for c in capcalera if c not in antiga)}).")


def _afegir_fila(ruta, capcalera, fila):
    """Añade una fila a un CSV, creando el archivo con cabecera si no existe.
    Si el archivo ya existe con una cabecera más corta, la actualiza primero."""
    os.makedirs(config.CARPETA_DADES, exist_ok=True)
    _assegurar_columnes(ruta, capcalera)
    nou = not os.path.exists(ruta)
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nou:
            w.writerow(capcalera)
        w.writerow(fila)


def guardar_decisio(setmana, model_id, decisio, valor):
    """Apunta la decisión de esta IA en el historial (decisions.csv).
    Incluye qué titulares dice haber tenido en cuenta: así se puede comprobar
    que las IAs leen de verdad las noticias, y se puede analizar en el TR qué
    tipo de noticia mueve a cada modelo."""
    claus = decisio.get("noticies_clau")
    if isinstance(claus, list):
        noticies = " ".join(str(x) for x in claus)
    else:
        noticies = str(claus or "")
    _afegir_fila(RUTA_DECISIONS,
        ["data", "setmana", "model", "decisio", "nivell_risc",
         "confianca", "valor_cartera", "justificacio",
         "noticies_clau", "lectura_noticies"],
        [datetime.date.today().isoformat(), setmana, model_id,
         decisio.get("decisio"), decisio.get("nivell_risc"),
         decisio.get("confianca"), round(valor, 2),
         (decisio.get("justificacio") or "").replace("\n", " "),
         noticies,
         (decisio.get("lectura_noticies") or "").replace("\n", " ")])


def guardar_canvis(setmana, model_id, aplicades):
    """Apunta cada operación aplicada en canvis.csv (para la web)."""
    for op in aplicades:
        _afegir_fila(RUTA_CANVIS,
            ["data", "setmana", "model", "vendre", "comprar", "import_eur"],
            [datetime.date.today().isoformat(), setmana, model_id,
             op["vendre"], op["comprar"], op["import_eur"]])


def guardar_comissions(setmana, model_id, comissio, acumulada):
    """Apunta lo que ha pagado esta IA en comisiones. Es la prueba directa
    de si sobreoperar sale caro (una de las hipótesis del TR)."""
    _afegir_fila(RUTA_COMISSIONS,
        ["data", "setmana", "model", "comissio_setmana", "comissio_acumulada"],
        [datetime.date.today().isoformat(), setmana, model_id,
         round(comissio, 2), round(acumulada, 2)])


def guardar_titulars(setmana, titulars):
    """Guarda los titulares que han visto TODAS las IAs esta semana.
    Sirve para demostrar en el TR que la información fue idéntica."""
    if not titulars:
        return
    for linia in titulars.splitlines():
        text = linia.strip()
        if not text:
            continue
        # las líneas vienen como "  1. Titular..."; quitamos la numeración
        if "." in text[:4]:
            text = text.split(".", 1)[1].strip()
        _afegir_fila(RUTA_TITULARS,
            ["data", "setmana", "titular"],
            [datetime.date.today().isoformat(), setmana, text])


def guardar_briefing(setmana, model_id, briefing):
    """Guarda el briefing exacto que ha recibido cada IA (trazabilidad).
    Un archivo por IA y semana, dentro de dades/briefings/."""
    carpeta = os.path.join(config.CARPETA_DADES, "briefings")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"S{setmana:02d}_{model_id}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(briefing)


def guardar_carteres(estat, preus):
    """Reescribe carteres.csv con la foto actual de todas las carteras,
    incluyendo tipo (acción/ETF), sector y país — para los gráficos de la web."""
    os.makedirs(config.CARPETA_DADES, exist_ok=True)
    actius = config.tots_els_actius()
    with open(RUTA_CARTERES, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "ticker", "nom", "tipus", "sector", "pais",
                    "unitats", "valor", "pes"])
        for mid, cartera in estat["carteres"].items():
            total = valor_cartera(cartera, preus) or 1
            for tk, unitats in cartera.items():
                if tk == "EFECTIU":
                    val = unitats
                    info = {"nom": "Efectiu", "tipus": "efectiu",
                            "categoria": "Efectiu", "pais": "—"}
                else:
                    p = preus.get(tk)
                    if not p or unitats <= 0:
                        continue
                    val = unitats * p
                    info = actius.get(tk, {"nom": tk, "tipus": "etf",
                                           "categoria": "—", "pais": "—"})
                if val < 0.5:
                    continue
                w.writerow([mid, tk, info["nom"], info["tipus"],
                            info["categoria"], info["pais"],
                            round(unitats, 6), round(val, 2),
                            round(100 * val / total, 2)])


def guardar_index(setmana, estat, preus):
    """Apunta el valor semanal de "10.000 € en el S&P 500 y no tocar nada"
    (la gestión pasiva contra la que compiten las IAs)."""
    p_spy = preus.get("SPY")
    if not p_spy:
        return
    if estat.get("index_unitats") is None:
        estat["index_unitats"] = config.CAPITAL_INICIAL / p_spy
    valor = estat["index_unitats"] * p_spy
    _afegir_fila(RUTA_INDEX,
        ["data", "setmana", "valor"],
        [datetime.date.today().isoformat(), setmana, round(valor, 2)])


# ============================================================
#  PROGRAMA PRINCIPAL — una ronda semanal completa
# ============================================================
def executar_ronda(setmana=None, forcar=False):
    """Juga una ronda. Si aquesta setmana ja se n'ha jugat una, no fa res
    (tret que es demani expressament amb forcar=True o la variable
    d'entorn FORCAR_RONDA=1). Això permet que el robot ho intenti diverses
    vegades cada dilluns sense por de duplicar la ronda."""
    if not forcar and os.environ.get("FORCAR_RONDA") != "1":
        if ja_jugat_aquesta_setmana():
            print("[i] Aquesta setmana la ronda ja s'ha jugat. No es fa res.")
            print("    (Per jugar-ne una d'extra: FORCAR_RONDA=1 python torneo.py)")
            return

    estat = carregar_estat()
    if setmana is None:
        setmana = estat.get("setmana", 0) + 1

    print(f"\n=== TORNEIG ALPHA ARTIFICIAL · SETMANA {setmana} ===")
    if MODE_SIMULAT:
        print("    (MODE SIMULAT: IAs de mentida, cap cost)\n")

    # 1. Precios, titulares y evolución de cada activo (idénticos para todas)
    preus = baixar_preus()
    titulars = obtenir_titulars()
    n_tit = len(titulars.splitlines()) if titulars else 0
    print(f"    {n_tit} titulars d'actualitat obtinguts.")
    variacions = carregar_variacions()

    # 2. Qué modelos juegan
    models_a_jugar = list(config.MODELS.keys()) if MODE_SIMULAT else \
        [m for m, d in config.MODELS.items() if d["actiu"]]
    if not models_a_jugar:
        print("[!] Cap model actiu. Activa'n algun a config.py (actiu: True).")
        return

    # Fre de seguretat: en mode real, si falta alguna clau NO es juga la
    # ronda (evita gravar una setmana oficial buida per una mala configuració).
    if not MODE_SIMULAT:
        sense_clau = [m for m in models_a_jugar if not connectors_ia.clau_de(m)]
        if sense_clau:
            noms = ", ".join(config.MODELS[m]["nom"] for m in sense_clau)
            print(f"[X] RONDA ATURADA: falten les claus API de: {noms}")
            print("    En local: posa-les a secrets.txt")
            print("    A GitHub: Settings → Secrets and variables → Actions")
            sys.exit(1)

    # 2b. Cobrar els dividends pendents ABANS de decidir: així cada IA veu
    #     els diners que ha rebut i pot decidir què en fa.
    print("\n[2b] Dividends cobrats des de l'última ronda...")
    cobrar_dividends(estat, preus)

    # 3-5. Para cada modelo
    print("\n[2-4] Demanant decisions a les IAs...")
    for model_id in models_a_jugar:
        nom = config.MODELS[model_id]["nom"]

        # Recuperar (o crear) su cartera
        cartera = estat["carteres"].get(model_id)
        if cartera is None:
            cartera = cartera_inicial(preus)
            estat["carteres"][model_id] = cartera

        briefing = montar_briefing(setmana, preus, cartera, model_id,
                                   titulars, variacions)
        guardar_briefing(setmana, model_id, briefing)
        decisio, error = demanar_decisio(model_id, briefing, cartera)

        if decisio is None:
            # La IA no ha contestado bien: lo apuntamos como "mantenir" con el motivo
            decisio = {"decisio": "mantenir", "nivell_risc": "—", "confianca": 0,
                       "justificacio": f"(sense resposta: {error})", "operacions": []}

        ok, motiu = validar_decisio(decisio)
        aplicades, comissio = [], 0.0
        if ok and decisio.get("decisio") == "reajustar":
            aplicades, comissio = aplicar_operacions(cartera, decisio, preus)

        # Comisiones acumuladas de esta IA desde el principio del torneo
        acumulades = estat.setdefault("comissions", {})
        acumulades[model_id] = round(acumulades.get(model_id, 0.0) + comissio, 2)

        valor = valor_cartera(cartera, preus)
        estat_txt = "✓ vàlida" if ok else f"✗ rebutjada ({motiu})"
        print(f"    {nom:22} → {decisio.get('decisio','?'):9} "
              f"risc:{str(decisio.get('nivell_risc','—')):12} "
              f"conf:{decisio.get('confianca','—')}/10  "
              f"cartera:{round(valor,2):>9} €  "
              f"comissions:{acumulades[model_id]:>6} €  {estat_txt}")

        if ok:
            guardar_decisio(setmana, model_id, decisio, valor)
            guardar_canvis(setmana, model_id, aplicades)
            guardar_comissions(setmana, model_id, comissio, acumulades[model_id])

    # 6. Índice, titulares, foto de carteras y estado para la próxima semana
    guardar_titulars(setmana, titulars)
    guardar_index(setmana, estat, preus)
    guardar_carteres(estat, preus)
    estat["setmana"] = setmana
    guardar_estat(estat)

    print(f"\n[5] Tot guardat a la carpeta {config.CARPETA_DADES}/")
    print("    Ara pots actualitzar la web amb:  python generar_web.py")
    print("=== Ronda completada ===\n")


if __name__ == "__main__":
    executar_ronda()
