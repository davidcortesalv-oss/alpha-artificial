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
MONEDA = "EUR"

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
    "IRBO": ("IA i robòtica (iShares)",         "IA i semiconductors"),
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
# Si una fuente falla, se prueba con la siguiente.
FONTS_TITULARS = [
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",         # Wall Street Journal · Mercats
    "https://www.cnbc.com/id/20910258/device/rss/rss.html",  # CNBC · Markets
    "http://feeds.marketwatch.com/marketwatch/topstories/",  # MarketWatch · Portada
]
N_TITULARS = 10   # cuántos titulares recibe cada IA

# --- Carpetas donde se guarda todo ---
CARPETA_DADES = "dades"        # aquí van los CSV con el historial
CARPETA_PROMPTS = "prompts"    # aquí vive el prompt semanal
