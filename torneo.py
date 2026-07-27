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


def obtenir_titulars():
    """Baja los titulares de actualidad de las fuentes RSS de config.py.
    Se piden UNA vez por ronda y se dan idénticos a las 5 IAs, para que
    ninguna tenga más información que otra (control de variables).
    Si todas las fuentes fallan, devuelve None y el briefing lo dirá."""
    try:
        import feedparser
    except ImportError:
        print("    [!] Falta la llibreria feedparser (pip install feedparser).")
        return None

    titulars, vistos = [], set()
    for url in config.FONTS_TITULARS:
        if len(titulars) >= config.N_TITULARS:
            break
        try:
            canal = feedparser.parse(url)
            for entrada in canal.entries[:8]:
                titol = (entrada.get("title") or "").strip()
                if titol and titol.lower() not in vistos:
                    vistos.add(titol.lower())
                    titulars.append(titol)
                if len(titulars) >= config.N_TITULARS:
                    break
        except Exception:
            continue  # si una font falla, provem la següent
    if not titulars:
        return None
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


def montar_briefing(setmana, preus, cartera, model_id, titulars=None):
    """Rellena los huecos {{...}} del prompt con los datos reales de esta
    semana y de esta IA concreta. Devuelve el texto final a enviar."""
    plantilla = carregar_prompt()

    # --- Lista de activos disponibles, en dos bloques ---
    # Primero las empresas (agrupadas por país, que es como piensa un gestor)
    # y después los fondos. Todos los precios ya vienen en euros.
    per_pais = {}
    for tk, (nom, sector, pais, _mon) in config.UNIVERS_ACCIONS.items():
        p = preus.get(tk)
        if p is not None:
            per_pais.setdefault(pais, []).append(f"    {tk} — {nom} ({sector}) — {p} €")

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
            per_cat.setdefault(cat, []).append(f"    {tk} — {nom} — {p} €")
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

    # Sustituciones
    text = (plantilla
        .replace("{{NUMERO_SETMANA}}", str(setmana))
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
def _afegir_fila(ruta, capcalera, fila):
    """Añade una fila a un CSV, creando el archivo con cabecera si no existe."""
    os.makedirs(config.CARPETA_DADES, exist_ok=True)
    nou = not os.path.exists(ruta)
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nou:
            w.writerow(capcalera)
        w.writerow(fila)


def guardar_decisio(setmana, model_id, decisio, valor):
    """Apunta la decisión de esta IA en el historial (decisions.csv)."""
    _afegir_fila(RUTA_DECISIONS,
        ["data", "setmana", "model", "decisio", "nivell_risc",
         "confianca", "valor_cartera", "justificacio"],
        [datetime.date.today().isoformat(), setmana, model_id,
         decisio.get("decisio"), decisio.get("nivell_risc"),
         decisio.get("confianca"), round(valor, 2),
         (decisio.get("justificacio") or "").replace("\n", " ")])


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
def executar_ronda(setmana=None):
    estat = carregar_estat()
    if setmana is None:
        setmana = estat.get("setmana", 0) + 1

    print(f"\n=== TORNEIG ALPHA ARTIFICIAL · SETMANA {setmana} ===")
    if MODE_SIMULAT:
        print("    (MODE SIMULAT: IAs de mentida, cap cost)\n")

    # 1. Precios y titulares (los mismos para todas las IAs)
    preus = baixar_preus()
    titulars = obtenir_titulars()
    n_tit = len(titulars.splitlines()) if titulars else 0
    print(f"    {n_tit} titulars d'actualitat obtinguts.")

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

    # 3-5. Para cada modelo
    print("\n[2-4] Demanant decisions a les IAs...")
    for model_id in models_a_jugar:
        nom = config.MODELS[model_id]["nom"]

        # Recuperar (o crear) su cartera
        cartera = estat["carteres"].get(model_id)
        if cartera is None:
            cartera = cartera_inicial(preus)
            estat["carteres"][model_id] = cartera

        briefing = montar_briefing(setmana, preus, cartera, model_id, titulars)
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
