# -*- coding: utf-8 -*-
"""
config.py — Configuración central del torneo ALPHA ARTIFICIAL
=============================================================
Aquí se definen TODAS las reglas y los datos fijos del experimento.
Si quieres cambiar algo del torneo (capital, comisión, lista de fondos...),
es el ÚNICO sitio donde tienes que tocar. El resto del programa lee de aquí.
"""

# --- Reglas del torneo (las que salen en tu TR) ---
CAPITAL_INICIAL = 10000.0      # euros virtuales por participante
COMISSIO = 0.001               # 0,1% por operación
MAX_PES_PER_ETF = 0.40         # ningún ETF puede pasar del 40% de la cartera
MAX_PES_PER_ACCIO = 0.20       # ninguna ACCIÓN puede pasar del 20% (más arriesgada)
MONEDA = "EUR"

# --- Cambio de divisa ---
# Las acciones cotizan en la moneda de su bolsa (Apple en dólares, Inditex en
# euros, Shell en peniques...). El torneo se contabiliza en EUROS, así que el
# motor convierte TODOS los precios a euros antes de calcular nada.
# 'factor' corrige mercados que cotizan en subunidades (Londres, en peniques).
DIVISES = {
    "EUR": {"parell": None,       "factor": 1.0},    # ya está en euros
    "USD": {"parell": "EURUSD=X", "factor": 1.0},
    "GBP": {"parell": "EURGBP=X", "factor": 0.01},   # Londres cotiza en penics
    "JPY": {"parell": "EURJPY=X", "factor": 1.0},
    "CHF": {"parell": "EURCHF=X", "factor": 1.0},
    "KRW": {"parell": "EURKRW=X", "factor": 1.0},
}

# --- Los 5 modelos que compiten ---
# 'actiu': False de momento porque aún no tienes las claves API.
# Cuando consigas la clave de uno, lo pones en True y ya entra al torneo.
# 'model_api': el nombre técnico del modelo que se usará al llamar a cada API.
#              Puedes cambiarlo cuando quieras (p. ej. a una versión más nueva).
MODELS = {
    "gpt":      {"nom": "GPT (OpenAI)",       "pais": "EUA",    "actiu": True, "model_api": "gpt-5"},
    "claude":   {"nom": "Claude (Anthropic)", "pais": "EUA",    "actiu": True, "model_api": "claude-sonnet-5"},
    # Nota: el teu compte gratuït de Google no té quota per a gemini-2.5-pro.
    # Si actives la facturació a aistudio.google.com, canvia-ho a "gemini-2.5-pro".
    "gemini":   {"nom": "Gemini (Google)",    "pais": "EUA",    "actiu": True, "model_api": "gemini-2.5-flash"},
    "deepseek": {"nom": "DeepSeek",           "pais": "Xina",   "actiu": True, "model_api": "deepseek-chat"},
    "mistral":  {"nom": "Mistral AI",         "pais": "Europa", "actiu": True, "model_api": "mistral-large-latest"},
}

# --- Universo de inversión: lista CERRADA pero amplia de ETFs reales ---
# El programa solo bajará precios de estos. Cada IA solo puede comprar de aquí.
# Formato: "TICKER": ("nom llegible", "categoria")
# Los tickers son los de Yahoo Finance (yfinance).
# OJO: la web (web/etfs.js) tiene una copia de esta lista con descripciones.
#      Si añades o quitas un ETF aquí, actualízalo también allí.
UNIVERS_ETFS = {
    # ── Índexs principals ──────────────────────────────────────────
    "SPY":  ("S&P 500 (SPDR)",                  "Índexs principals"),
    "VOO":  ("S&P 500 (Vanguard)",              "Índexs principals"),
    "IVV":  ("S&P 500 (iShares Core)",          "Índexs principals"),
    "VTI":  ("Mercat total EUA",                "Índexs principals"),
    "QQQ":  ("Nasdaq 100",                      "Índexs principals"),
    "DIA":  ("Dow Jones Industrial",            "Índexs principals"),
    "IWM":  ("Russell 2000 (small caps)",       "Índexs principals"),
    "RSP":  ("S&P 500 equiponderat",            "Índexs principals"),
    "VT":   ("Mercat mundial total",            "Índexs principals"),
    "ACWI": ("Món desenvolupat i emergent",     "Índexs principals"),

    # ── Tecnologia ─────────────────────────────────────────────────
    "XLK":  ("Tecnologia EUA (S&P)",            "Tecnologia"),
    "VGT":  ("Tecnologia (Vanguard)",           "Tecnologia"),
    "IGV":  ("Programari EUA",                  "Tecnologia"),
    "FDN":  ("Internet EUA",                    "Tecnologia"),
    "SKYY": ("Computació al núvol",             "Tecnologia"),
    "CIBR": ("Ciberseguretat",                  "Tecnologia"),
    "ARKK": ("Innovació disruptiva (ARK)",      "Tecnologia"),

    # ── IA i semiconductors ────────────────────────────────────────
    "SMH":  ("Semiconductors (VanEck)",         "IA i semiconductors"),
    "SOXX": ("Semiconductors (iShares)",        "IA i semiconductors"),
    "BOTZ": ("Robòtica i IA (Global X)",        "IA i semiconductors"),
    "ROBO": ("Robòtica i automatització",       "IA i semiconductors"),
    "AIQ":  ("Intel·ligència artificial",       "IA i semiconductors"),
    "ARKQ": ("Autonomia i robòtica (ARK)",      "IA i semiconductors"),

    # ── Energia ────────────────────────────────────────────────────
    "XLE":  ("Energia EUA",                     "Energia"),
    "XOP":  ("Exploració de petroli i gas",     "Energia"),
    "OIH":  ("Serveis petroliers",              "Energia"),
    "ICLN": ("Energies netes globals",          "Energia"),
    "TAN":  ("Energia solar",                   "Energia"),
    "FAN":  ("Energia eòlica",                  "Energia"),
    "URA":  ("Urani i energia nuclear",         "Energia"),

    # ── Salut ──────────────────────────────────────────────────────
    "XLV":  ("Salut EUA",                       "Salut"),
    "VHT":  ("Sanitat (Vanguard)",              "Salut"),
    "IBB":  ("Biotecnologia (Nasdaq)",          "Salut"),
    "XBI":  ("Biotecnologia (S&P)",             "Salut"),
    "IHI":  ("Equipament mèdic",                "Salut"),

    # ── Renda fixa (bons) ──────────────────────────────────────────
    "TLT":  ("Bons EUA 20+ anys",               "Renda fixa"),
    "IEF":  ("Bons EUA 7-10 anys",              "Renda fixa"),
    "SHY":  ("Bons EUA 1-3 anys",               "Renda fixa"),
    "BIL":  ("Lletres del Tresor (1-3 mesos)",  "Renda fixa"),
    "AGG":  ("Bons EUA agregats",               "Renda fixa"),
    "BND":  ("Mercat total de bons EUA",        "Renda fixa"),
    "LQD":  ("Bons corporatius de qualitat",    "Renda fixa"),
    "HYG":  ("Bons d'alt rendiment",            "Renda fixa"),
    "TIP":  ("Bons lligats a la inflació",      "Renda fixa"),
    "EMB":  ("Deute de mercats emergents",      "Renda fixa"),
    "MUB":  ("Bons municipals EUA",             "Renda fixa"),
    "GOVT": ("Bons del Tresor EUA",             "Renda fixa"),

    # ── Mercats internacionals ─────────────────────────────────────
    "VGK":  ("Europa (Vanguard)",               "Mercats internacionals"),
    "EZU":  ("Zona euro",                       "Mercats internacionals"),
    "EWG":  ("Alemanya",                        "Mercats internacionals"),
    "EWQ":  ("França",                          "Mercats internacionals"),
    "EWU":  ("Regne Unit",                      "Mercats internacionals"),
    "EWJ":  ("Japó",                            "Mercats internacionals"),
    "MCHI": ("Xina (MSCI)",                     "Mercats internacionals"),
    "FXI":  ("Xina (grans empreses)",           "Mercats internacionals"),
    "EWY":  ("Corea del Sud",                   "Mercats internacionals"),
    "EWT":  ("Taiwan",                          "Mercats internacionals"),
    "EEM":  ("Mercats emergents (MSCI)",        "Mercats internacionals"),
    "VWO":  ("Mercats emergents (Vanguard)",    "Mercats internacionals"),
    "INDA": ("Índia",                           "Mercats internacionals"),
    "EWZ":  ("Brasil",                          "Mercats internacionals"),
    "EWC":  ("Canadà",                          "Mercats internacionals"),

    # ── Matèries primeres ──────────────────────────────────────────
    "DBC":  ("Cistella de matèries primeres",   "Matèries primeres"),
    "PDBC": ("Matèries primeres (optimitzat)",  "Matèries primeres"),
    "GSG":  ("Índex GSCI de matèries primeres", "Matèries primeres"),
    "USO":  ("Petroli WTI",                     "Matèries primeres"),
    "BNO":  ("Petroli Brent",                   "Matèries primeres"),
    "UNG":  ("Gas natural",                     "Matèries primeres"),
    "DBA":  ("Agricultura",                     "Matèries primeres"),
    "CPER": ("Coure",                           "Matèries primeres"),
    "DBB":  ("Metalls industrials",             "Matèries primeres"),

    # ── Metalls preciosos ──────────────────────────────────────────
    "GLD":  ("Or físic (SPDR)",                 "Metalls preciosos"),
    "IAU":  ("Or físic (iShares)",              "Metalls preciosos"),
    "SGOL": ("Or físic (abrdn)",                "Metalls preciosos"),
    "SLV":  ("Plata física (iShares)",          "Metalls preciosos"),
    "SIVR": ("Plata física (abrdn)",            "Metalls preciosos"),
    "PPLT": ("Platí físic",                     "Metalls preciosos"),
    "PALL": ("Pal·ladi físic",                  "Metalls preciosos"),
    "GDX":  ("Mineres d'or",                    "Metalls preciosos"),
    "GDXJ": ("Mineres d'or júnior",             "Metalls preciosos"),

    # ── Immobiliari ────────────────────────────────────────────────
    "VNQ":  ("Immobiliari EUA (REITs)",         "Immobiliari"),
    "VNQI": ("Immobiliari internacional",       "Immobiliari"),
    "IYR":  ("Immobiliari EUA (iShares)",       "Immobiliari"),
    "SCHH": ("REITs EUA (Schwab)",              "Immobiliari"),
    "REM":  ("REITs hipotecaris",               "Immobiliari"),

    # ── Dividends ──────────────────────────────────────────────────
    "VIG":  ("Dividends creixents (Vanguard)",  "Dividends"),
    "VYM":  ("Alt dividend (Vanguard)",         "Dividends"),
    "SCHD": ("Dividends de qualitat (Schwab)",  "Dividends"),
    "DVY":  ("Dividends selectes (iShares)",    "Dividends"),
    "HDV":  ("Alt dividend (iShares)",          "Dividends"),
    "SDY":  ("Aristòcrates del dividend (SPDR)","Dividends"),
    "NOBL": ("Aristòcrates del dividend (S&P)", "Dividends"),
    "DGRO": ("Creixement de dividends",         "Dividends"),

    # ── Defensius ──────────────────────────────────────────────────
    "USMV": ("Mínima volatilitat EUA",          "Defensius"),
    "SPLV": ("Baixa volatilitat S&P 500",       "Defensius"),
    "QUAL": ("Factor qualitat (MSCI)",          "Defensius"),
    "SPHD": ("Alt dividend i baixa volatilitat","Defensius"),
    "XLP":  ("Consum bàsic EUA",                "Defensius"),
    "XLU":  ("Serveis públics (utilities)",     "Defensius"),

    # ── Sectors EUA ────────────────────────────────────────────────
    "XLF":  ("Banca i finances EUA",            "Sectors EUA"),
    "XLY":  ("Consum discrecional EUA",         "Sectors EUA"),
    "XLI":  ("Indústria EUA",                   "Sectors EUA"),
    "XLB":  ("Materials EUA",                   "Sectors EUA"),
    "XLRE": ("Immobiliari EUA (sector S&P)",    "Sectors EUA"),
    "XLC":  ("Serveis de comunicació EUA",      "Sectors EUA"),
    "KBE":  ("Bancs EUA",                       "Sectors EUA"),
    "ITA":  ("Aeroespacial i defensa",          "Sectors EUA"),
    "JETS": ("Aerolínies",                      "Sectors EUA"),
}

# =====================================================================
#  ACCIONES CONCRETAS (añadidas en la semana 3 — ver CANVI_DE_REGLES.md)
# ---------------------------------------------------------------------
#  Ahora las IAs no solo eligen "tecnología" o "Europa": pueden decir
#  "compro Nvidia" o "compro Inditex" y explicar por qué. Mucho más
#  interesante de leer y de analizar en el TR.
#  Formato: "TICKER": ("nom", "sector", "pais", "moneda")
#  OJO: la moneda importa — el motor lo convierte todo a euros.
# =====================================================================
UNIVERS_ACCIONS = {
    # ── EUA · Tecnologia ───────────────────────────────────────────
    "AAPL":  ("Apple",                  "Tecnologia",   "EUA",        "USD"),
    "MSFT":  ("Microsoft",              "Tecnologia",   "EUA",        "USD"),
    "NVDA":  ("Nvidia",                 "Semiconductors", "EUA",      "USD"),
    "GOOGL": ("Alphabet (Google)",      "Tecnologia",   "EUA",        "USD"),
    "AMZN":  ("Amazon",                 "Consum",       "EUA",        "USD"),
    "META":  ("Meta (Facebook)",        "Tecnologia",   "EUA",        "USD"),
    "TSLA":  ("Tesla",                  "Automoció",    "EUA",        "USD"),
    "AMD":   ("AMD",                    "Semiconductors", "EUA",      "USD"),
    "INTC":  ("Intel",                  "Semiconductors", "EUA",      "USD"),
    "AVGO":  ("Broadcom",               "Semiconductors", "EUA",      "USD"),
    "QCOM":  ("Qualcomm",               "Semiconductors", "EUA",      "USD"),
    "CRM":   ("Salesforce",             "Tecnologia",   "EUA",        "USD"),
    "ORCL":  ("Oracle",                 "Tecnologia",   "EUA",        "USD"),
    "ADBE":  ("Adobe",                  "Tecnologia",   "EUA",        "USD"),
    "IBM":   ("IBM",                    "Tecnologia",   "EUA",        "USD"),
    "CSCO":  ("Cisco",                  "Tecnologia",   "EUA",        "USD"),
    "NFLX":  ("Netflix",                "Mitjans",      "EUA",        "USD"),
    "PLTR":  ("Palantir",               "Tecnologia",   "EUA",        "USD"),

    # ── EUA · Salut ────────────────────────────────────────────────
    "JNJ":   ("Johnson & Johnson",      "Salut",        "EUA",        "USD"),
    "LLY":   ("Eli Lilly",              "Salut",        "EUA",        "USD"),
    "PFE":   ("Pfizer",                 "Salut",        "EUA",        "USD"),
    "MRK":   ("Merck",                  "Salut",        "EUA",        "USD"),
    "ABBV":  ("AbbVie",                 "Salut",        "EUA",        "USD"),
    "UNH":   ("UnitedHealth",           "Salut",        "EUA",        "USD"),
    "AMGN":  ("Amgen",                  "Salut",        "EUA",        "USD"),
    "MRNA":  ("Moderna",                "Salut",        "EUA",        "USD"),

    # ── EUA · Finances ─────────────────────────────────────────────
    "JPM":   ("JPMorgan Chase",         "Finances",     "EUA",        "USD"),
    "BAC":   ("Bank of America",        "Finances",     "EUA",        "USD"),
    "GS":    ("Goldman Sachs",          "Finances",     "EUA",        "USD"),
    "V":     ("Visa",                   "Finances",     "EUA",        "USD"),
    "MA":    ("Mastercard",             "Finances",     "EUA",        "USD"),
    "AXP":   ("American Express",       "Finances",     "EUA",        "USD"),
    "BRK-B": ("Berkshire Hathaway",     "Finances",     "EUA",        "USD"),
    "PYPL":  ("PayPal",                 "Finances",     "EUA",        "USD"),

    # ── EUA · Consum ───────────────────────────────────────────────
    "KO":    ("Coca-Cola",              "Consum",       "EUA",        "USD"),
    "PEP":   ("PepsiCo",                "Consum",       "EUA",        "USD"),
    "MCD":   ("McDonald's",             "Consum",       "EUA",        "USD"),
    "NKE":   ("Nike",                   "Consum",       "EUA",        "USD"),
    "SBUX":  ("Starbucks",              "Consum",       "EUA",        "USD"),
    "WMT":   ("Walmart",                "Consum",       "EUA",        "USD"),
    "COST":  ("Costco",                 "Consum",       "EUA",        "USD"),
    "PG":    ("Procter & Gamble",       "Consum",       "EUA",        "USD"),
    "HD":    ("Home Depot",             "Consum",       "EUA",        "USD"),
    "DIS":   ("Walt Disney",            "Mitjans",      "EUA",        "USD"),

    # ── EUA · Energia i indústria ──────────────────────────────────
    "XOM":   ("ExxonMobil",             "Energia",      "EUA",        "USD"),
    "CVX":   ("Chevron",                "Energia",      "EUA",        "USD"),
    "BA":    ("Boeing",                 "Indústria",    "EUA",        "USD"),
    "CAT":   ("Caterpillar",            "Indústria",    "EUA",        "USD"),
    "GE":    ("General Electric",       "Indústria",    "EUA",        "USD"),
    "LMT":   ("Lockheed Martin",        "Defensa",      "EUA",        "USD"),
    "RTX":   ("RTX (Raytheon)",         "Defensa",      "EUA",        "USD"),
    "DE":    ("John Deere",             "Indústria",    "EUA",        "USD"),
    "UPS":   ("UPS",                    "Logística",    "EUA",        "USD"),

    # ── EUA · Altres ───────────────────────────────────────────────
    "T":     ("AT&T",                   "Telecomunicacions", "EUA",   "USD"),
    "VZ":    ("Verizon",                "Telecomunicacions", "EUA",   "USD"),
    "UBER":  ("Uber",                   "Tecnologia",   "EUA",        "USD"),
    "ABNB":  ("Airbnb",                 "Consum",       "EUA",        "USD"),
    "COIN":  ("Coinbase",               "Finances",     "EUA",        "USD"),
    "F":     ("Ford",                   "Automoció",    "EUA",        "USD"),
    "GM":    ("General Motors",         "Automoció",    "EUA",        "USD"),

    # ── Espanya (empreses que reconeixeràs del dia a dia) ──────────
    "ITX.MC":  ("Inditex (Zara)",       "Consum",       "Espanya",    "EUR"),
    "SAN.MC":  ("Banco Santander",      "Finances",     "Espanya",    "EUR"),
    "BBVA.MC": ("BBVA",                 "Finances",     "Espanya",    "EUR"),
    "IBE.MC":  ("Iberdrola",            "Energia",      "Espanya",    "EUR"),
    "TEF.MC":  ("Telefónica",           "Telecomunicacions", "Espanya", "EUR"),
    "REP.MC":  ("Repsol",               "Energia",      "Espanya",    "EUR"),
    "GRF.MC":  ("Grifols",              "Salut",        "Catalunya",  "EUR"),
    "CLNX.MC": ("Cellnex",              "Telecomunicacions", "Catalunya", "EUR"),
    "FER.MC":  ("Ferrovial",            "Indústria",    "Espanya",    "EUR"),
    "AENA.MC": ("Aena (aeroports)",     "Indústria",    "Espanya",    "EUR"),
    "ELE.MC":  ("Endesa",               "Energia",      "Espanya",    "EUR"),
    "AMS.MC":  ("Amadeus",              "Tecnologia",   "Espanya",    "EUR"),

    # ── França ─────────────────────────────────────────────────────
    "MC.PA":  ("LVMH (Louis Vuitton)",  "Luxe",         "França",     "EUR"),
    "RMS.PA": ("Hermès",                "Luxe",         "França",     "EUR"),
    "OR.PA":  ("L'Oréal",               "Consum",       "França",     "EUR"),
    "AIR.PA": ("Airbus",                "Indústria",    "França",     "EUR"),
    "TTE.PA": ("TotalEnergies",         "Energia",      "França",     "EUR"),
    "SAN.PA": ("Sanofi",                "Salut",        "França",     "EUR"),
    "BNP.PA": ("BNP Paribas",           "Finances",     "França",     "EUR"),
    "CAP.PA": ("Capgemini",             "Tecnologia",   "França",     "EUR"),

    # ── Alemanya ───────────────────────────────────────────────────
    "SAP.DE": ("SAP",                   "Tecnologia",   "Alemanya",   "EUR"),
    "SIE.DE": ("Siemens",               "Indústria",    "Alemanya",   "EUR"),
    "ALV.DE": ("Allianz",               "Finances",     "Alemanya",   "EUR"),
    "BMW.DE": ("BMW",                   "Automoció",    "Alemanya",   "EUR"),
    "MBG.DE": ("Mercedes-Benz",         "Automoció",    "Alemanya",   "EUR"),
    "ADS.DE": ("Adidas",                "Consum",       "Alemanya",   "EUR"),
    "DTE.DE": ("Deutsche Telekom",      "Telecomunicacions", "Alemanya", "EUR"),
    "BAS.DE": ("BASF",                  "Química",      "Alemanya",   "EUR"),

    # ── Països Baixos, Bèlgica i Itàlia ────────────────────────────
    "ASML.AS":  ("ASML",                "Semiconductors", "Països Baixos", "EUR"),
    "ADYEN.AS": ("Adyen",               "Finances",     "Països Baixos", "EUR"),
    "PHIA.AS":  ("Philips",             "Salut",        "Països Baixos", "EUR"),
    "ABI.BR":   ("AB InBev",            "Consum",       "Bèlgica",    "EUR"),
    "RACE":     ("Ferrari",             "Automoció",    "Itàlia",     "USD"),
    "ENI.MI":   ("Eni",                 "Energia",      "Itàlia",     "EUR"),
    "ISP.MI":   ("Intesa Sanpaolo",     "Finances",     "Itàlia",     "EUR"),
    "STLAM.MI": ("Stellantis",          "Automoció",    "Itàlia",     "EUR"),

    # ── Suïssa ─────────────────────────────────────────────────────
    "NESN.SW": ("Nestlé",               "Consum",       "Suïssa",     "CHF"),
    "NOVN.SW": ("Novartis",             "Salut",        "Suïssa",     "CHF"),
    "UBSG.SW": ("UBS",                  "Finances",     "Suïssa",     "CHF"),

    # ── Regne Unit (cotitzen en penics: el motor ho ajusta) ────────
    "SHEL.L": ("Shell",                 "Energia",      "Regne Unit", "GBP"),
    "BP.L":   ("BP",                    "Energia",      "Regne Unit", "GBP"),
    "AZN.L":  ("AstraZeneca",           "Salut",        "Regne Unit", "GBP"),
    "HSBA.L": ("HSBC",                  "Finances",     "Regne Unit", "GBP"),
    "ULVR.L": ("Unilever",              "Consum",       "Regne Unit", "GBP"),
    "RIO.L":  ("Rio Tinto",             "Mineria",      "Regne Unit", "GBP"),

    # ── Àsia i emergents ───────────────────────────────────────────
    "TSM":      ("TSMC (xips Taiwan)",  "Semiconductors", "Taiwan",   "USD"),
    "7203.T":   ("Toyota",              "Automoció",    "Japó",       "JPY"),
    "6758.T":   ("Sony",                "Tecnologia",   "Japó",       "JPY"),
    "005930.KS":("Samsung Electronics", "Tecnologia",   "Corea del Sud", "KRW"),
    "BABA":     ("Alibaba",             "Consum",       "Xina",       "USD"),
    "PDD":      ("PDD (Temu)",          "Consum",       "Xina",       "USD"),
    "NTES":     ("NetEase",             "Mitjans",      "Xina",       "USD"),
    "INFY":     ("Infosys",             "Tecnologia",   "Índia",      "USD"),
    "HDB":      ("HDFC Bank",           "Finances",     "Índia",      "USD"),
}


# --- Funciones de apoyo: el universo completo (ETFs + acciones) ---
def es_accio(ticker):
    """¿Este ticker es una acción concreta (una empresa)?"""
    return ticker in UNIVERS_ACCIONS


def max_pes(ticker):
    """Límite de cartera de este activo: 20% si es una acción, 40% si es ETF."""
    return MAX_PES_PER_ACCIO if es_accio(ticker) else MAX_PES_PER_ETF


def moneda_de(ticker):
    """En qué moneda cotiza este activo (los ETFs de la lista son en USD)."""
    if ticker in UNIVERS_ACCIONS:
        return UNIVERS_ACCIONS[ticker][3]
    return "USD"


def tots_els_actius():
    """Todo el universo en un solo diccionario, con la misma forma:
    {ticker: {"nom", "categoria", "tipus", "pais", "moneda"}}"""
    total = {}
    for tk, (nom, cat) in UNIVERS_ETFS.items():
        total[tk] = {"nom": nom, "categoria": cat, "tipus": "etf",
                     "pais": "Global", "moneda": "USD"}
    for tk, (nom, sector, pais, mon) in UNIVERS_ACCIONS.items():
        total[tk] = {"nom": nom, "categoria": sector, "tipus": "accio",
                     "pais": pais, "moneda": mon}
    return total


# --- Indicadores de context que se envían a las IAs cada semana ---
# (símbolos de Yahoo Finance para el "termómetro" del mercado)
INDICADORS_CONTEXT = {
    "^VIX":    "VIX (índex de la por)",
    "^TNX":    "Bo EUA 10 anys (%)",
    "EURUSD=X":"EUR/USD",
}

# --- Fuentes de titulares de mercado (RSS, gratuitas, sin clave) ---
# Cada lunes el motor baja los titulares y se los da IDÉNTICOS a las 5 IAs
# (control de variables: ninguna tiene más información que otra).
#
# ⚠️ LECCIÓN APRENDIDA (30/07/2026): el feed del Wall Street Journal que había
# aquí estaba MUERTO — servía las mismas noticias del 27/01/2025 una y otra
# vez. Las IAs decidieron durante semanas leyendo titulares de hace año y
# medio. Por eso ahora:
#   1. Se usan varias fuentes y se MEZCLAN (no se llena con la primera).
#   2. Se descarta todo titular más antiguo que MAX_DIES_TITULAR.
#   3. Si una fuente se queda obsoleta, el motor lo avisa por pantalla.
# Todas las de esta lista se comprobaron vivas el 30/07/2026.
FONTS_TITULARS = [
    "https://www.cnbc.com/id/20910258/device/rss/rss.html",  # CNBC · Mercats
    "https://www.cnbc.com/id/100003114/device/rss/rss.html", # CNBC · Portada
    "https://www.ft.com/markets?format=rss",                # Financial Times · Mercats
    "https://finance.yahoo.com/news/rssindex",              # Yahoo Finance
    "https://www.investing.com/rss/news_25.rss",            # Investing.com · Mercats
    "https://www.investing.com/rss/news_14.rss",            # Investing.com · Economia
    "https://seekingalpha.com/market_currents.xml",          # Seeking Alpha
    "http://feeds.marketwatch.com/marketwatch/topstories/",  # MarketWatch
    "https://e00-expansion.uecdn.es/rss/mercados.xml",      # Expansión (Espanya)
]
N_TITULARS = 12          # cuántos titulares recibe cada IA
MAX_DIES_TITULAR = 8     # se descarta cualquier noticia más vieja que esto

# Palabras que indican que un titular es de mercados/economía y no de
# consumo o estilo de vida (MarketWatch y Yahoo mezclan mucho). Se usan para
# priorizar, no para excluir: si no hay suficientes, se cogen los demás.
PARAULES_RELLEVANTS = [
    "stock", "stocks", "market", "markets", "shares", "bond", "yield", "fed",
    "inflation", "rate", "rates", "earnings", "profit", "loss", "gdp", "economy",
    "oil", "gold", "dollar", "euro", "tariff", "trade", "recession", "growth",
    "nasdaq", "s&p", "dow", "index", "central bank", "ecb", "treasury",
    "bank", "chip", "chips", "ai", "tech", "chief executive", "revenue",
    "borsa", "mercat", "mercados", "acciones", "tipos", "inflación", "ibex",
    "beneficio", "resultados", "deuda", "prima de riesgo",
]

# --- Carpetas donde se guarda todo ---
CARPETA_DADES = "dades"        # aquí van los CSV con el historial
CARPETA_PROMPTS = "prompts"    # aquí vive el prompt semanal
