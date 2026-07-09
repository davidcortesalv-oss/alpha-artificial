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

            decs.append({
                "setmana": s,
                "data": (fila.get("data") or "").strip(),
                "decisio": (fila.get("decisio") or "").strip(),
                "nivell_risc": (fila.get("nivell_risc") or "").strip(),
                "confianca": int(num(fila.get("confianca"), 0)),
                "valor_cartera": round(valor, 2),
                "rend_setmana": round(rend, 2),
                "justificacio": (fila.get("justificacio") or "").strip(),
                "operacions": ops or None,
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

    # --- Carteres actuals (dades/carteres.csv) ---
    carteres = {}
    for f in llegir_csv(RUTA_CARTERES):
        m = (f.get("model") or "").strip()
        if m not in META_MODELS:
            continue
        carteres.setdefault(m, []).append({
            "ticker": (f.get("ticker") or "").strip(),
            "pes": round(num(f.get("pes"))),
            "valor": round(num(f.get("valor"))),
        })
    for m in carteres:
        carteres[m].sort(key=lambda h: -h["pes"])
    if not carteres:
        print(f"[i] Sense {RUTA_CARTERES}: el detall de cada IA no mostrarà la cartera.")

    # --- Moments destacats (opcional, escrits a mà: dades/destacats.csv) ---
    highlights = []
    for f in llegir_csv(RUTA_DESTACATS):
        highlights.append({
            "setmana": int(num(f.get("setmana"), 0)),
            "model": (f.get("model") or "").strip(),
            "titol": (f.get("titol") or "").strip(),
            "text": (f.get("text") or "").strip(),
        })

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
            "moneda": config.MONEDA,
            "setmanes": max(n_set, 22),      # durada prevista del torneig
            "setmanaActual": n_set,
            "dataInici": dies[0] if dies else "",
            "dataActual": dies[-1] if dies else "",
            "font": "real",
            "generat": datetime.datetime.now().isoformat(timespec="minutes"),
            "puntsPerSetmana": 1,            # les dades reals són setmanals
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
    }

    os.makedirs(CARPETA_WEB, exist_ok=True)
    ruta_out = os.path.join(CARPETA_WEB, "dades.json")
    with open(ruta_out, "w", encoding="utf-8") as f:
        json.dump(sortida, f, ensure_ascii=False, indent=2)

    print(f"[OK] Escrit {ruta_out}  ({len(models_json)} participants, {n_set} setmanes).")
    if not algun_valor:
        print("[!] AVÍS: tots els valors de cartera semblen buits o iguals al capital")
        print("    inicial. Comprova que torneo.py ha pogut baixar preus.")


if __name__ == "__main__":
    main()
