# -*- coding: utf-8 -*-
"""
generar_historic.py — Historial de 5 anys de cada actiu per a la web
=====================================================================
Baixa 5 anys de preus setmanals de TOTS els actius (accions i ETFs), els
converteix a euros i els guarda a  web/historic.json.

La web els fa servir per dibuixar el gràfic històric quan obres la fitxa
d'un actiu, amb selectors 1M / 6M / 1A / 5A.

    python generar_historic.py

Es pot executar un cop per setmana (el robot de GitHub ho fa sol). El
fitxer resultant fa uns 300-400 KB i la web només el carrega quan cal.
"""

import os
import json
import sys
import config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA = os.path.join("web", "historic.json")


def main():
    import yfinance as yf

    actius = config.tots_els_actius()
    parells = [d["parell"] for d in config.DIVISES.values() if d["parell"]]
    tickers = list(actius.keys()) + parells

    print(f"[1] Baixant 5 anys de preus setmanals de {len(tickers)} símbols...")
    print("    (pot trigar un parell de minuts)")
    dades = yf.download(tickers, period="5y", interval="1wk", progress=False)
    tancaments = dades["Close"]

    # --- Sèries de canvi de divisa, per convertir cada setmana ---
    canvis = {}
    for parell in parells:
        try:
            canvis[parell] = tancaments[parell].ffill()
        except Exception:
            canvis[parell] = None

    dates = [d.strftime("%Y-%m-%d") for d in tancaments.index]

    historic = {}
    fallats = []
    for tk, info in actius.items():
        try:
            serie = tancaments[tk]
        except Exception:
            fallats.append(tk)
            continue

        divisa = config.DIVISES.get(info["moneda"], {"parell": None, "factor": 1.0})
        valors = []
        for i in range(len(serie)):
            v = serie.iloc[i]
            if v != v:          # NaN
                valors.append(None)
                continue
            v = float(v) * divisa["factor"]
            if divisa["parell"]:
                c = canvis.get(divisa["parell"])
                if c is None:
                    valors.append(None)
                    continue
                cv = c.iloc[i]
                if cv != cv or not cv:
                    valors.append(None)
                    continue
                v = v / float(cv)
            valors.append(round(v, 2))

        # Si gairebé no hi ha dades, no val la pena guardar-ho
        if sum(1 for x in valors if x is not None) < 10:
            fallats.append(tk)
            continue
        historic[tk] = valors

    sortida = {"dates": dates, "preus": historic}
    os.makedirs("web", exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as f:
        json.dump(sortida, f, ensure_ascii=False, separators=(",", ":"))

    mida = os.path.getsize(RUTA) / 1024
    print(f"\n[OK] Escrit {RUTA}")
    print(f"     {len(historic)} actius · {len(dates)} setmanes · {mida:.0f} KB")
    if fallats:
        print(f"     Sense historial ({len(fallats)}): {', '.join(fallats[:12])}")


if __name__ == "__main__":
    main()
