# -*- coding: utf-8 -*-
"""
generar_web.py — Converteix els CSV del torneig en dades per a la web
=====================================================================
La web (carpeta web/) ensenya per defecte dades de DEMOSTRACIÓ. Quan el
torneig real ja tingui historial, executa aquest script:

    python generar_web.py

Llegeix els CSV de dades/ i escriu  web/dades.json. La web detecta aquest
fitxer automàticament (el comprova cada minut) i mostra les dades REALS
en comptes de la demo.

Pensat per executar-se cada setmana, just després de torneo.py.

Fitxers que llegeix (tots els escriu torneo.py, tret de destacats.csv):
  dades/decisions.csv   → decisions i justificacions          (obligatori)
  dades/index.csv       → la línia del S&P 500                (opcional)
  dades/carteres.csv    → composició actual de cada cartera   (opcional)
  dades/canvis.csv      → operacions aplicades                (opcional)
  dades/destacats.csv   → moments destacats escrits a mà      (opcional)
                          columnes: setmana,model,titol,text
"""

import os
import csv
import json
import math
import re
import datetime
import config

try:
    import connectors_ia
except ImportError:
    connectors_ia = None

CARPETA_WEB = "web"
RUTA_DECISIONS = os.path.join(config.CARPETA_DADES, "decisions.csv")
RUTA_INDEX = os.path.join(config.CARPETA_DADES, "index.csv")
RUTA_CARTERES = os.path.join(config.CARPETA_DADES, "carteres.csv")
RUTA_CANVIS = os.path.join(config.CARPETA_DADES, "canvis.csv")
RUTA_DESTACATS = os.path.join(config.CARPETA_DADES, "destacats.csv")
RUTA_COMISSIONS = os.path.join(config.CARPETA_DADES, "comissions.csv")
RUTA_TITULARS = os.path.join(config.CARPETA_DADES, "titulars.csv")
RUTA_DIARIS = os.path.join(config.CARPETA_DADES, "valors_diaris.csv")

# --- Metadades visuals i de perfil de cada participant ---
#     (els colors han de coincidir amb l'estètica de la web)
META_MODELS = {
    "claude": {
        "nom": "Claude", "empresa": "Anthropic", "color": "#cc785c",
        "perfil": "Model d'Anthropic. El seu estil inversor real es descobrirà durant el torneig.",
    },
    "gpt": {
        "nom": "GPT", "empresa": "OpenAI", "color": "#19c37d",
        "perfil": "Model d'OpenAI. El seu estil inversor real es descobrirà durant el torneig.",
    },
    "gemini": {
        "nom": "Gemini", "empresa": "Google", "color": "#5b8def",
        "perfil": "Model de Google. El seu estil inversor real es descobrirà durant el torneig.",
    },
    "deepseek": {
        "nom": "DeepSeek", "empresa": "DeepSeek", "color": "#9a7bff",
        "perfil": "Model de DeepSeek. El seu estil inversor real es descobrirà durant el torneig.",
    },
    "mistral": {
        "nom": "Mistral", "empresa": "Mistral AI", "color": "#ff4d6d",
        "perfil": "Model de Mistral AI. El seu estil inversor real es descobrirà durant el torneig.",
    },
}


def llegir_csv(ruta):
    """Llegeix un CSV i el torna com a llista de diccionaris (o [] si no hi és)."""
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x, default=0.0):
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return default


def escriure_versio():
    """Escriu web/versio.json amb el número de versió que hi ha a index.html.

    Serveix perquè el navegador detecti que té una còpia antiga de la pàgina
    guardada i es recarregui sol (el detector és al principi de l'index.html).
    Es llegeix del propi HTML per no haver de mantenir el número en dos llocs."""
    ruta_html = os.path.join(CARPETA_WEB, "index.html")
    if not os.path.exists(ruta_html):
        return
    with open(ruta_html, encoding="utf-8") as f:
        trobat = re.search(r"VERSIO_ACTUAL\s*=\s*(\d+)", f.read())
    if not trobat:
        return
    versio = int(trobat.group(1))
    with open(os.path.join(CARPETA_WEB, "versio.json"), "w", encoding="utf-8") as f:
        json.dump({"versio": versio}, f)
    return versio


def desar_si_ha_canviat(ruta, dades):
    """Guarda el JSON només si les dades han canviat de veritat.

    El camp 'generat' canvia a cada execució, així que si es comparés el
    fitxer sencer sempre semblaria diferent. Això generava un commit brossa
    cada vegada que el robot s'executava (fins a quatre per dilluns). Aquí
    es compara ignorant l'hora: si la resta és idèntica, no es toca el
    fitxer i no hi ha commit."""
    nou = dict(dades)
    if os.path.exists(ruta):
        try:
            with open(ruta, encoding="utf-8") as f:
                antic = json.load(f)
            a = dict(antic.get("meta", {}))
            b = dict(nou.get("meta", {}))
            a.pop("generat", None)
            b.pop("generat", None)
            if (a == b and
                    {k: v for k, v in antic.items() if k != "meta"} ==
                    {k: v for k, v in nou.items() if k != "meta"}):
                print("[i] Les dades no han canviat: no es reescriu el fitxer.")
                return False
        except (ValueError, OSError):
            pass
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(nou, f, ensure_ascii=False, indent=2)
    return True


# =====================================================================
#  MÈTRIQUES DE RISC (el que fa que el TR sembli professional)
# ---------------------------------------------------------------------
#  No n'hi ha prou amb saber qui guanya més: importa QUANT RISC ha
#  assumit per guanyar-ho. Aquests tres números són els que fa servir
#  qualsevol gestora de debò.
# =====================================================================
def metriques_risc(serie, punts_per_any=252):
    """Calcula volatilitat, màxima caiguda i ràtio de Sharpe d'una sèrie de
    valors de cartera. 'punts_per_any' = 252 si les dades són diàries,
    52 si són setmanals.

    - volatilitat: com de moguda és la cartera (%, anualitzada). Menys és
      més tranquil.
    - max_caiguda: la pitjor caiguda des d'un màxim fins a un mínim (%).
      És el "quant vaig arribar a perdre pel camí".
    - sharpe: rendibilitat obtinguda per cada unitat de risc. Més és millor.
      Per sobre d'1 es considera bo.
    """
    if not serie or len(serie) < 3:
        return {"volatilitat": None, "max_caiguda": None, "sharpe": None}

    # Rendimientos de un punto al siguiente
    rends = []
    for i in range(1, len(serie)):
        anterior = serie[i - 1]
        if anterior:
            rends.append(serie[i] / anterior - 1)
    if len(rends) < 2:
        return {"volatilitat": None, "max_caiguda": None, "sharpe": None}

    mitjana = sum(rends) / len(rends)
    variancia = sum((r - mitjana) ** 2 for r in rends) / (len(rends) - 1)
    desviacio = math.sqrt(variancia)

    volatilitat = desviacio * math.sqrt(punts_per_any) * 100
    rend_anual = mitjana * punts_per_any * 100
    sharpe = (rend_anual / volatilitat) if volatilitat > 0.0001 else None

    # Máxima caída: el peor bajón desde un pico anterior
    maxim, max_caiguda = serie[0], 0.0
    for v in serie:
        maxim = max(maxim, v)
        if maxim:
            caiguda = (v - maxim) / maxim * 100
            max_caiguda = min(max_caiguda, caiguda)

    return {
        "volatilitat": round(volatilitat, 2),
        "max_caiguda": round(max_caiguda, 2),
        "sharpe": round(sharpe, 2) if sharpe is not None else None,
    }


def main():
    files = llegir_csv(RUTA_DECISIONS)
    if not files:
        print(f"[!] No trobo {RUTA_DECISIONS}. Executa abans torneo.py.")
        return

    # --- Agrupar per model i setmana (si hi ha duplicats, ens quedem l'últim) ---
    per_model = {}
    setmanes = set()
    data_de_setmana = {}
    for fila in files:
        m = (fila.get("model") or "").strip()
        if m not in META_MODELS:
            continue
        s = int(num(fila.get("setmana"), 0))
        if s <= 0:
            continue
        per_model.setdefault(m, {})[s] = fila
        setmanes.add(s)
        data_de_setmana[s] = (fila.get("data") or "").strip()

    if not setmanes:
        print("[!] El CSV no té decisions vàlides encara.")
        return

    n_set = max(setmanes)
    setmanes_ord = list(range(1, n_set + 1))
    dies = [data_de_setmana.get(s, "") for s in setmanes_ord]

    # --- Canvis (operacions aplicades pel motor) ---
    canvis_raw = llegir_csv(RUTA_CANVIS)

    models_json = []
    series = {}
    decisions = {}
    informes = {}
    canvis_json = []
    algun_valor = False

    for mid, meta in META_MODELS.items():
        if mid not in per_model:
            continue
        files_m = per_model[mid]
        serie = []
        decs = []
        infs = []
        valor_previ = config.CAPITAL_INICIAL
        for s in setmanes_ord:
            fila = files_m.get(s)
            if fila is None:
                serie.append(round(valor_previ, 2))  # arrossega l'últim valor
                continue
            valor = num(fila.get("valor_cartera"), valor_previ) or valor_previ
            if valor and valor != config.CAPITAL_INICIAL:
                algun_valor = True
            rend = ((valor - valor_previ) / valor_previ * 100) if valor_previ else 0
            serie.append(round(valor, 2))

            # operacions d'aquesta setmana (de canvis.csv)
            ops = [
                {"vendre": (c.get("vendre") or "").strip(),
                 "comprar": (c.get("comprar") or "").strip(),
                 "import": round(num(c.get("import_eur")), 2)}
                for c in canvis_raw
                if (c.get("model") or "").strip() == mid and int(num(c.get("setmana"), 0)) == s
            ]

            # Quins titulars diu la IA que ha tingut en compte
            claus_txt = (fila.get("noticies_clau") or "").strip()
            noticies_clau = [int(num(x)) for x in claus_txt.split() if num(x, 0)] if claus_txt else []

            # ¿Esta semana la IA realmente decidió, o falló su API?
            # Es importante distinguirlo: una ronda fallida NO es "decidió
            # mantener". Si se cuentan como decisiones, las métricas de
            # sobreoperación y de confianza salen falseadas.
            just = (fila.get("justificacio") or "").strip()
            incidencia = ("sense resposta" in just.lower()
                          or "incidència tècnica" in just.lower())

            decs.append({
                "setmana": s,
                "data": (fila.get("data") or "").strip(),
                "decisio": (fila.get("decisio") or "").strip(),
                "nivell_risc": (fila.get("nivell_risc") or "").strip(),
                "confianca": int(num(fila.get("confianca"), 0)),
                "valor_cartera": round(valor, 2),
                "rend_setmana": round(rend, 2),
                "justificacio": just,
                "operacions": ops or None,
                "noticies_clau": noticies_clau,
                "lectura_noticies": (fila.get("lectura_noticies") or "").strip(),
                "incidencia": incidencia,
            })
            valor_previ = valor

        # informes: una fitxa per setmana a partir de la decisió
        for i, d in enumerate(decs):
            seguent = decs[i + 1] if i + 1 < len(decs) else None
            infs.append({
                "setmana": d["setmana"], "data": d["data"],
                "decisio": d["decisio"], "confianca": d["confianca"],
                "nivell_risc": d["nivell_risc"],
                "comprats": sorted({o["comprar"] for o in (d["operacions"] or []) if o["comprar"] and o["comprar"] != "EFECTIU"}),
                "venuts": sorted({o["vendre"] for o in (d["operacions"] or []) if o["vendre"] and o["vendre"] != "EFECTIU"}),
                "mantinguts": [],   # (el motor encara no guarda la foto setmanal de cada cartera)
                "operacions": d["operacions"] or [],
                "justificacio": d["justificacio"],
                "context": None,    # (es podrà omplir quan el motor guardi els titulars)
                "riscos": None,
                "expectativa": None,
                "resultat": seguent["rend_setmana"] if seguent else None,
            })

        series[mid] = serie
        decisions[mid] = decs
        informes[mid] = infs
        models_json.append({
            "id": mid, "nom": meta["nom"], "empresa": meta["empresa"],
            "pais": config.MODELS.get(mid, {}).get("pais", "—"),
            "color": meta["color"], "dash": None,
            "competeix": True, "isIndex": False, "isAuthor": False,
            "perfil": meta.get("perfil", ""), "estrategia": "",
            "fortaleses": [], "febleses": [],
        })

        # canvis per a la web (amb l'impacte 2 setmanes després)
        for c in canvis_raw:
            if (c.get("model") or "").strip() != mid:
                continue
            s = int(num(c.get("setmana"), 0))
            if s <= 0 or s > n_set:
                continue
            v_ara = series[mid][s - 1]
            v_despres = series[mid][min(n_set, s + 2) - 1]
            impacte = round((v_despres - v_ara) / v_ara * 100, 2) if v_ara else None
            fila_dec = files_m.get(s) or {}
            motiu = (fila_dec.get("justificacio") or "").strip()
            for ticker, accio in ((c.get("vendre"), "reduït"), (c.get("comprar"), "augmentat")):
                ticker = (ticker or "").strip()
                if not ticker or ticker == "EFECTIU":
                    continue
                canvis_json.append({
                    "setmana": s, "data": (c.get("data") or "").strip(), "model": mid,
                    "ticker": ticker, "accio": accio,
                    "pesAbans": None, "pesDespres": None,   # el motor no guarda pesos històrics
                    "import": round(num(c.get("import_eur")), 2),
                    "motiu": motiu, "impacte": impacte,
                })

    # --- Índex S&P 500 (dades/index.csv) ---
    files_idx = llegir_csv(RUTA_INDEX)
    if files_idx:
        idx_per_set = {int(num(f.get("setmana"))): num(f.get("valor")) for f in files_idx if f.get("setmana")}
        serie_idx, previ = [], config.CAPITAL_INICIAL
        for s in setmanes_ord:
            v = idx_per_set.get(s, previ) or previ
            serie_idx.append(round(v, 2))
            previ = v
        series["index"] = serie_idx
        models_json.append({
            "id": "index", "nom": "S&P 500", "empresa": "Índex · gestió passiva",
            "pais": "—", "color": "#f3e9d4", "dash": "7 5",
            "competeix": False, "isIndex": True, "isAuthor": False,
            "perfil": "El rival a batre: 10.000 € invertits el primer dia i ni un moviment més.",
            "estrategia": "Passiva pura", "fortaleses": [], "febleses": [],
        })
    else:
        print(f"[i] Sense {RUTA_INDEX}: la web no dibuixarà la línia de l'índex.")

    # --- Carteres actuals (dades/carteres.csv), amb sector, país i tipus ---
    carteres = {}
    for f in llegir_csv(RUTA_CARTERES):
        m = (f.get("model") or "").strip()
        if m not in META_MODELS:
            continue
        carteres.setdefault(m, []).append({
            "ticker": (f.get("ticker") or "").strip(),
            "nom": (f.get("nom") or "").strip(),
            "tipus": (f.get("tipus") or "etf").strip(),
            "sector": (f.get("sector") or "—").strip(),
            "pais": (f.get("pais") or "—").strip(),
            "pes": round(num(f.get("pes")), 1),
            "valor": round(num(f.get("valor"))),
        })
    for m in carteres:
        carteres[m].sort(key=lambda h: -h["pes"])
    if not carteres:
        print(f"[i] Sense {RUTA_CARTERES}: el detall de cada IA no mostrarà la cartera.")

    # --- Exposició per sector, país i tipus (per als gràfics de disc) ---
    exposicio = {}
    for m, posicions in carteres.items():
        sectors, paisos, tipus = {}, {}, {}
        for h in posicions:
            sectors[h["sector"]] = round(sectors.get(h["sector"], 0) + h["pes"], 1)
            paisos[h["pais"]] = round(paisos.get(h["pais"], 0) + h["pes"], 1)
            etiqueta = {"accio": "Accions", "etf": "Fons (ETFs)",
                        "efectiu": "Efectiu"}.get(h["tipus"], h["tipus"])
            tipus[etiqueta] = round(tipus.get(etiqueta, 0) + h["pes"], 1)
        ordena = lambda d: dict(sorted(d.items(), key=lambda x: -x[1]))
        exposicio[m] = {"sectors": ordena(sectors), "paisos": ordena(paisos),
                        "tipus": ordena(tipus)}

    # --- Consens: quins actius comparteixen les IAs i quins són apostes soles ---
    tinences = {}
    for m, posicions in carteres.items():
        for h in posicions:
            if h["ticker"] == "EFECTIU":
                continue
            reg = tinences.setdefault(h["ticker"], {
                "ticker": h["ticker"], "nom": h["nom"], "tipus": h["tipus"],
                "sector": h["sector"], "models": []})
            reg["models"].append({"model": m, "pes": h["pes"]})
    consens = sorted(tinences.values(),
                     key=lambda r: (-len(r["models"]),
                                    -sum(x["pes"] for x in r["models"])))

    # --- Comissions acumulades (la prova de si sobreoperar surt car) ---
    comissions = {}
    for f in llegir_csv(RUTA_COMISSIONS):
        m = (f.get("model") or "").strip()
        if m in META_MODELS:
            comissions[m] = round(num(f.get("comissio_acumulada")), 2)

    # --- Titulars que han vist les IAs (traçabilitat per al TR) ---
    titulars = []
    for f in llegir_csv(RUTA_TITULARS):
        titulars.append({
            "setmana": int(num(f.get("setmana"), 0)),
            "data": (f.get("data") or "").strip(),
            "titular": (f.get("titular") or "").strip(),
        })
    titulars.sort(key=lambda t: -t["setmana"])

    # --- Moments destacats (opcional, escrits a mà: dades/destacats.csv) ---
    highlights = []
    for f in llegir_csv(RUTA_DESTACATS):
        highlights.append({
            "setmana": int(num(f.get("setmana"), 0)),
            "model": (f.get("model") or "").strip(),
            "titol": (f.get("titol") or "").strip(),
            "text": (f.get("text") or "").strip(),
        })

    # --- LÍNIA TEMPORAL COMPLETA de la gràfica principal ---
    # Aquí es COMBINEN dues fonts, i és important que sigui així:
    #   · decisions.csv → un valor per setmana des del primer dia del torneig
    #   · valors_diaris.csv → un valor per dia de mercat (només des del dia
    #     que es va activar la valoració diària)
    # Si només es fes servir la diària, la gràfica perdria tot l'historial
    # anterior (era el bug: es veien només els últims 3 dies en comptes de
    # tot el torneig). Si només es fes servir la setmanal, es perdria el
    # detall dels últims dies. Amb les dues, la gràfica va del dia 1 fins avui.
    per_data = {}          # {data: {model: valor}}

    # 1) Valors setmanals de cada IA (de les seves decisions)
    for mid, files_m in per_model.items():
        if mid not in series:
            continue
        for s, fila in files_m.items():
            data = (fila.get("data") or "").strip()
            valor = num(fila.get("valor_cartera"), 0)
            if data and valor:
                per_data.setdefault(data, {})[mid] = valor

    # 2) Valors setmanals de l'índex
    for f in files_idx:
        data = (f.get("data") or "").strip()
        valor = num(f.get("valor"), 0)
        if data and valor:
            per_data.setdefault(data, {})["index"] = valor

    # 3) Valors diaris (tenen prioritat: són els més precisos)
    files_diaris = llegir_csv(RUTA_DIARIS)
    for f in files_diaris:
        data = (f.get("data") or "").strip()
        m = (f.get("model") or "").strip()
        valor = num(f.get("valor"), 0)
        if data and m and valor:
            per_data.setdefault(data, {})[m] = valor

    dates_ord = sorted(d for d in per_data if d)
    if len(dates_ord) >= 2:
        ids = list(series.keys())
        series_completes = {mid: [] for mid in ids}
        previ = {mid: config.CAPITAL_INICIAL for mid in ids}
        for data in dates_ord:
            for mid in ids:
                v = per_data[data].get(mid, previ[mid])   # arrossega l'últim conegut
                series_completes[mid].append(round(v, 2))
                previ[mid] = v
        series = series_completes
        dies = dates_ord

        # Densitat real de punts: serveix per als selectors de temps de la web
        try:
            d0 = datetime.date.fromisoformat(dates_ord[0])
            d1 = datetime.date.fromisoformat(dates_ord[-1])
            setmanes_transcorregudes = max(1, (d1 - d0).days / 7)
            punts_per_setmana = max(1, round(len(dates_ord) / setmanes_transcorregudes))
        except ValueError:
            punts_per_setmana = 1
        print(f"[i] Gràfica principal: {len(dates_ord)} punts "
              f"({dates_ord[0]} → {dates_ord[-1]}), "
              f"~{punts_per_setmana} punt(s) per setmana.")
    else:
        punts_per_setmana = 1

    # --- Mètriques de risc de cada participant ---
    punts_any = 252 if punts_per_setmana > 1 else 52
    risc = {mid: metriques_risc(s, punts_any) for mid, s in series.items()}

    # --- Estat de les APIs (per al panell "Configuració d'APIs") ---
    apis = {"ia": [], "financeres": []}
    estat_con = connectors_ia.estat_connexions() if connectors_ia else {}
    for mid, meta in META_MODELS.items():
        con = estat_con.get(mid, {})
        decs = decisions.get(mid, [])
        ultima = decs[-1] if decs else None
        apis["ia"].append({
            "id": mid,
            "proveidor": meta["empresa"],
            "model_api": con.get("model_api") or config.MODELS.get(mid, {}).get("model_api", ""),
            "variable": con.get("variable", ""),
            "url_consola": con.get("url_consola", ""),
            "estat": "connectada" if (con.get("clau") and con.get("actiu")) else "pendent",
            "ultimaExecucio": f"Setmana {ultima['setmana']} · {ultima['data']}" if ultima else None,
            "ultimBriefing": (ultima["justificacio"][:160] + ("…" if len(ultima["justificacio"]) > 160 else "")) if ultima else None,
        })
    apis["financeres"] = [
        {"nom": "Yahoo Finance (yfinance)", "us": "Preus reals dels ETFs i de l'índex S&P 500",
         "estat": "operativa",
         "detall": "No necessita clau. El motor la fa servir cada dilluns; si un ticker falla, es reintenta amb els últims 5 dies de dades."},
        {"nom": "Titulars de mercat (RSS)", "us": "Els 10 titulars del briefing setmanal de cada IA",
         "estat": "operativa",
         "detall": "Wall Street Journal, CNBC i MarketWatch (sense clau). Les 5 IAs reben exactament els mateixos titulars."},
    ]

    sortida = {
        "meta": {
            "capital": config.CAPITAL_INICIAL,
            "comissio": config.COMISSIO,
            "maxPes": config.MAX_PES_PER_ETF,
            "maxPesEtf": config.MAX_PES_PER_ETF,
            "maxPesAccio": config.MAX_PES_PER_ACCIO,
            "moneda": config.MONEDA,
            "setmanes": max(n_set, 22),      # durada prevista del torneig
            "setmanaActual": n_set,
            "dataInici": dies[0] if dies else "",
            "dataActual": dies[-1] if dies else "",
            "font": "real",
            "generat": datetime.datetime.now().isoformat(timespec="minutes"),
            "puntsPerSetmana": punts_per_setmana,
            "nAccions": len(config.UNIVERS_ACCIONS),
            "nEtfs": len(config.UNIVERS_ETFS),
        },
        "dies": dies,
        "models": models_json,
        "series": series,
        "decisions": decisions,
        "informes": informes,
        "carteres": carteres,
        "canvis": sorted(canvis_json, key=lambda c: -c["setmana"]),
        "highlights": highlights,
        "apis": apis,
        "risc": risc,
        "comissions": comissions,
        "consens": consens,
        "exposicio": exposicio,
        "titulars": titulars,
    }

    os.makedirs(CARPETA_WEB, exist_ok=True)
    ruta_out = os.path.join(CARPETA_WEB, "dades.json")
    canviat = desar_si_ha_canviat(ruta_out, sortida)
    versio = escriure_versio()

    if canviat:
        print(f"[OK] Escrit {ruta_out}  ({len(models_json)} participants, {n_set} setmanes).")
    if versio:
        print(f"[i] Versió de la web: {versio} (a web/versio.json)")
    if not algun_valor:
        print("[!] AVÍS: tots els valors de cartera semblen buits o iguals al capital")
        print("    inicial. Comprova que torneo.py ha pogut baixar preus.")


if __name__ == "__main__":
    main()
