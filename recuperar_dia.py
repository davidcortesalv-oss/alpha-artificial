# -*- coding: utf-8 -*-
"""
recuperar_dia.py
================

Rellena un día de bolsa que el robot diario se saltó, usando los precios de
cierre REALES de ese día (los mismos que habría bajado el robot).

    python recuperar_dia.py 2026-09-01

¿POR QUÉ HACE FALTA?
--------------------
El robot de precios solo sabe mirar el último cierre. Si un día no llega a
ejecutarse (o se ejecuta con la fecha equivocada, como pasó a finales de agosto
de 2026 por los retrasos de GitHub), ese día queda como un agujero en el
gráfico y ya no se recupera solo.

IMPORTANTE — esto NO inventa nada:
  · las UNIDADES de cada cartera son las que había ese día (entre dos rondas
    las carteras no se tocan, así que son exactamente las mismas);
  · los PRECIOS son los cierres reales de Yahoo Finance de esa fecha;
  · el CAMBIO de divisa es el de esa misma fecha.

Es el mismo método que usa la auditoría para comprobar que las carteras son
reproducibles.
"""

import os
import csv
import sys
import config
import torneo

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA = os.path.join(config.CARPETA_DADES, "valors_diaris.csv")


def preus_del_dia(data_iso, tickers):
    """Baixa el tancament real de cada ticker en una data concreta, ja en euros."""
    import datetime
    import yfinance as yf

    d = datetime.date.fromisoformat(data_iso)
    # Pedimos una ventana pequeña alrededor del día y nos quedamos con ESE día.
    dades = yf.download(
        tickers,
        start=(d - datetime.timedelta(days=4)).isoformat(),
        end=(d + datetime.timedelta(days=1)).isoformat(),
        progress=False,
        auto_adjust=False,
    )

    bruts = {}
    for t in tickers:
        try:
            serie = dades["Close"][t].dropna()
            serie = serie[serie.index.date <= d]
            # Solo vale si el último cierre ES el del día pedido (si no, ese
            # ticker no cotizó ese día y lo dejamos fuera).
            if serie.empty or serie.index[-1].date() != d:
                bruts[t] = None
            else:
                bruts[t] = round(float(serie.iloc[-1]), 4)
        except Exception:
            bruts[t] = None

    actius = config.tots_els_actius()
    preus = {}
    for t, valor in bruts.items():
        if valor is None:
            preus[t] = None
        elif t in actius:
            preus[t] = torneo.a_euros(valor, actius[t]["moneda"], bruts)
        else:
            preus[t] = valor
    return preus


def main():
    if len(sys.argv) < 2:
        print("Ús: python recuperar_dia.py 2026-09-01")
        return
    data = sys.argv[1]

    files = []
    if os.path.exists(RUTA):
        with open(RUTA, encoding="utf-8") as f:
            files = list(csv.DictReader(f))
    if any(x["data"] == data for x in files):
        print(f"[=] El {data} ja hi és al fitxer. No es toca res.")
        return

    estat = torneo.carregar_estat()
    if not estat.get("carteres"):
        print("[!] No hi ha carteres a l'estat del torneig.")
        return

    # Solo bajamos lo que de verdad se necesita: lo que hay en cartera + SPY + divisas.
    en_cartera = {tk for c in estat["carteres"].values() for tk in c if tk != "EFECTIU"}
    parells = [d["parell"] for d in config.DIVISES.values() if d["parell"]]
    tickers = sorted(en_cartera | {"SPY"} | set(parells))

    print(f"[1] Baixant el tancament real del {data} ({len(tickers)} símbols)...")
    preus = preus_del_dia(data, tickers)

    if not preus.get("SPY"):
        print(f"[!] El {data} no té tancament de SPY: o la borsa era tancada, o "
              f"Yahoo no en té dades. No s'escriu res.")
        return

    noves = []
    for model_id, cartera in estat["carteres"].items():
        valor = torneo.valor_cartera(cartera, preus)
        if valor > 0:
            noves.append([data, model_id, round(valor, 2)])
            print(f"      {model_id:10} {round(valor, 2):>10} €")

    if estat.get("index_unitats"):
        v_index = estat["index_unitats"] * preus["SPY"]
        noves.append([data, "index", round(v_index, 2)])
        print(f"      {'index':10} {round(v_index, 2):>10} €")

    files += [{"data": r[0], "model": r[1], "valor": r[2]} for r in noves]
    files.sort(key=lambda x: (x["data"], x["model"]))

    with open(RUTA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["data", "model", "valor"])
        w.writeheader()
        w.writerows(files)

    print(f"\n[✓] Recuperat el {data} amb {len(noves)} valors reals.")


if __name__ == "__main__":
    main()
