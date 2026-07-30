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


def baixar_serie(yf, tickers, actius, parells, periode, interval, etiqueta):
    """Baixa una tanda de preus i els converteix tots a euros.
    Torna (llista_de_dates, {ticker: [valors]})."""
    print(f"[·] Baixant {etiqueta} ({len(tickers)} símbols)...")
    dades = yf.download(tickers, period=periode, interval=interval, progress=False)
    tancaments = dades["Close"]

    # Sèries de canvi de divisa, per convertir cada punt amb el canvi del dia
    canvis = {}
    for parell in parells:
        try:
            canvis[parell] = tancaments[parell].ffill()
        except Exception:
            canvis[parell] = None

    dates = [d.strftime("%Y-%m-%d") for d in tancaments.index]
    resultat = {}
    for tk, info in actius.items():
        try:
            serie = tancaments[tk]
        except Exception:
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

        if sum(1 for x in valors if x is not None) >= 5:
            resultat[tk] = valors
    print(f"    {len(resultat)} actius · {len(dates)} punts")
    return dates, resultat


def main():
    import yfinance as yf

    actius = config.tots_els_actius()
    parells = [d["parell"] for d in config.DIVISES.values() if d["parell"]]
    tickers = list(actius.keys()) + parells

    print("Generant l'historial de preus per als gràfics de la web.")
    print("(pot trigar uns minuts: són dues descàrregues)\n")

    # DIARI de l'últim any: perquè els rangs curts (1M, 3M, 6M, 1A) es vegin
    # amb detall. Amb dades setmanals, "1 mes" només tenia 4 punts i el
    # gràfic sortia pràcticament pla.
    dates_d, preus_d = baixar_serie(
        yf, tickers, actius, parells, "1y", "1d", "1 any de preus DIARIS")

    # SETMANAL de 5 anys: per veure la tendència de fons sense inflar el fitxer.
    dates_s, preus_s = baixar_serie(
        yf, tickers, actius, parells, "5y", "1wk", "5 anys de preus SETMANALS")

    sortida = {
        "diari": {"dates": dates_d, "preus": preus_d},
        "setmanal": {"dates": dates_s, "preus": preus_s},
    }
    os.makedirs("web", exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as f:
        json.dump(sortida, f, ensure_ascii=False, separators=(",", ":"))

    mida = os.path.getsize(RUTA) / 1024
    print(f"\n[OK] Escrit {RUTA}  ({mida:.0f} KB)")
    print(f"     Diari: {len(dates_d)} dies · Setmanal: {len(dates_s)} setmanes")
    sense = [t for t in actius if t not in preus_d and t not in preus_s]
    if sense:
        print(f"     Sense historial ({len(sense)}): {', '.join(sense[:12])}")


if __name__ == "__main__":
    main()
