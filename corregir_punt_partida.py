# -*- coding: utf-8 -*-
"""
corregir_punt_partida.py — Que els 10.000 € siguin exactes i verificables
==========================================================================
PER QUÈ EXISTEIX AQUEST FITXER

El 30/07/2026, en corregir el problema de les divises, es van reescalar les
unitats de cada cartera prenent com a referència els valors de la setmana
anterior... que estaven inflats justament per aquell error. Resultat: totes
les carteres (i l'índex) van quedar amb un 0,163% d'unitats de més.

Efecte pràctic: si algú comprovava a Yahoo Finance què valdrien 10.000 €
posats a l'S&P 500 el primer dia del torneig, no li sortia el mateix número
que ensenyava la web.

Aquest script ho arregla d'una vegada:
  1. Calcula les unitats EXACTES que compren 10.000 € el primer dia,
     amb el preu real de SPY convertit a euros amb el canvi d'aquell dia.
  2. Recalcula TOT l'historial de l'índex des d'aquestes unitats i els preus
     reals de cada data: així queda verificable per qualsevol.
  3. Aplica el mateix factor de correcció a les cinc IAs, perquè totes
     parteixin dels mateixos 10.000 € reals i la comparació segueixi essent
     justa.

Fa una còpia de seguretat abans de tocar res.

    python corregir_punt_partida.py
"""

import os
import csv
import json
import shutil
import sys
import datetime
import config
import torneo

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA_MARCA = os.path.join(config.CARPETA_DADES, ".punt_partida_corregit")
RUTA_DIARIS = os.path.join(config.CARPETA_DADES, "valors_diaris.csv")
CARPETA_COPIA = os.path.join(config.CARPETA_DADES, "copia_abans_correccio")


def copia_seguretat():
    os.makedirs(CARPETA_COPIA, exist_ok=True)
    for nom in ("decisions.csv", "index.csv", "valors_diaris.csv",
                "carteres.csv", "estat_torneig.json"):
        origen = os.path.join(config.CARPETA_DADES, nom)
        if os.path.exists(origen):
            shutil.copy2(origen, os.path.join(CARPETA_COPIA, nom))
    print(f"[1] Còpia de seguretat feta a {CARPETA_COPIA}/")


def preus_spy_historics(data_inici):
    """Preu de SPY en euros per a cada dia de mercat des de l'inici."""
    import yfinance as yf
    inici = (datetime.date.fromisoformat(data_inici) -
             datetime.timedelta(days=5)).isoformat()
    dades = yf.download(["SPY", "EURUSD=X"], start=inici, progress=False)["Close"].dropna()
    return {d.strftime("%Y-%m-%d"): float(f["SPY"]) / float(f["EURUSD=X"])
            for d, f in dades.iterrows()}


def preu_del_dia(taula, dia):
    """Preu del dia demanat, o l'últim disponible abans (caps de setmana)."""
    candidats = [d for d in taula if d <= dia]
    return taula[max(candidats)] if candidats else None


def main():
    if os.path.exists(RUTA_MARCA):
        print("[i] La correcció ja es va aplicar. No cal tornar-hi.")
        return

    estat = torneo.carregar_estat()
    if not estat.get("carteres") or not estat.get("index_unitats"):
        print("[!] Falten dades del torneig.")
        return

    files_idx = list(csv.DictReader(open(torneo.RUTA_INDEX, encoding="utf-8")))
    if not files_idx:
        print("[!] No hi ha dades/index.csv.")
        return
    data_inici = files_idx[0]["data"]

    copia_seguretat()

    print("[2] Baixant preus reals de SPY des de l'inici del torneig...")
    taula = preus_spy_historics(data_inici)
    preu_inici = preu_del_dia(taula, data_inici)
    if not preu_inici:
        print("[!] No he pogut obtenir el preu inicial de SPY.")
        return

    unitats_ok = config.CAPITAL_INICIAL / preu_inici
    factor = unitats_ok / estat["index_unitats"]

    print(f"\n    Primer dia del torneig : {data_inici}")
    print(f"    SPY en euros aquell dia: {preu_inici:,.2f} €")
    print(f"    Unitats correctes      : {unitats_ok:.6f}")
    print(f"    Unitats actuals        : {estat['index_unitats']:.6f}")
    print(f"    Factor de correcció    : {factor:.6f}  "
          f"({(factor - 1) * 100:+.3f} %)\n")

    # --- 3. Índex: es recalcula tot l'historial des de zero ---
    print("[3] Recalculant l'historial de l'índex amb preus reals...")
    for fila in files_idx:
        p = preu_del_dia(taula, fila["data"])
        if p:
            fila["valor"] = round(unitats_ok * p, 2)
    with open(torneo.RUTA_INDEX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=files_idx[0].keys())
        w.writeheader()
        w.writerows(files_idx)
    estat["index_unitats"] = round(unitats_ok, 6)
    print(f"    {len(files_idx)} valors de l'índex recalculats.")

    # --- 4. Les cinc IAs: mateix factor, per partir dels mateixos 10.000 € ---
    print("[4] Aplicant el factor a les carteres de les IAs...")
    for mid, cartera in estat["carteres"].items():
        for tk in cartera:
            cartera[tk] = round(cartera[tk] * factor, 6)
        print(f"    {mid:10} unitats ajustades")

    # --- 5. Escalar els valors ja registrats a l'historial ---
    print("[5] Ajustant els valors històrics ja guardats...")
    files_dec = list(csv.DictReader(open(torneo.RUTA_DECISIONS, encoding="utf-8")))
    for fila in files_dec:
        try:
            fila["valor_cartera"] = round(float(fila["valor_cartera"]) * factor, 2)
        except (ValueError, KeyError):
            continue
    with open(torneo.RUTA_DECISIONS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=files_dec[0].keys())
        w.writeheader()
        w.writerows(files_dec)

    if os.path.exists(RUTA_DIARIS):
        files_d = list(csv.DictReader(open(RUTA_DIARIS, encoding="utf-8")))
        for fila in files_d:
            try:
                if fila["model"] == "index":
                    p = preu_del_dia(taula, fila["data"])
                    if p:
                        fila["valor"] = round(unitats_ok * p, 2)
                else:
                    fila["valor"] = round(float(fila["valor"]) * factor, 2)
            except (ValueError, KeyError):
                continue
        with open(RUTA_DIARIS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=files_d[0].keys())
            w.writeheader()
            w.writerows(files_d)
        print(f"    {len(files_d)} valors diaris ajustats.")

    # --- 6. Guardar-ho tot i refer la foto de carteres ---
    preus = torneo.baixar_preus()
    torneo.guardar_carteres(estat, preus)
    torneo.guardar_estat(estat)

    with open(RUTA_MARCA, "w", encoding="utf-8") as f:
        f.write("Punt de partida corregit. Veure CANVI_DE_REGLES.md (Canvi 5).\n")

    # --- 7. Comprovació final ---
    print("\n[6] COMPROVACIÓ")
    ultim_dia = files_idx[-1]["data"]
    p_final = preu_del_dia(taula, ultim_dia)
    valor_idx = unitats_ok * p_final
    print(f"    10.000 € posats a l'S&P 500 el {data_inici}")
    print(f"    valdrien el {ultim_dia}: {valor_idx:,.2f} €  "
          f"({(valor_idx / config.CAPITAL_INICIAL - 1) * 100:+.2f} %)")
    print(f"    L'índex del torneig ara diu: {float(files_idx[-1]['valor']):,.2f} €")
    print("\n[OK] Fet. Actualitza la web amb:  python generar_web.py")


if __name__ == "__main__":
    main()
