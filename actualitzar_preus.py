# -*- coding: utf-8 -*-
"""
actualitzar_preus.py — Refresca el valor de les carteres CADA DIA
==================================================================
Les IAs continuen decidint només els dilluns (com diu el TR), però els
mercats es mouen cada dia. Aquest script baixa els preus del dia i recalcula
què valen les carteres, SENSE preguntar res a cap IA.

Resultat: la gràfica de la web es mou cada dia i sembla una plataforma de
debò, i el cost és ZERO (yfinance és gratis i no es truca cap IA).

    python actualitzar_preus.py

Escriu a  dades/valors_diaris.csv  una fila per participant i dia:
    data, model, valor

L'executa sol el robot de GitHub cada dia de mercat (dilluns a divendres).
"""

import os
import csv
import sys
import datetime
import config
import torneo

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA_DIARIS = os.path.join(config.CARPETA_DADES, "valors_diaris.csv")


def files_existents():
    """Devuelve el conjunto de (data, model) ya guardados, para no duplicar."""
    if not os.path.exists(RUTA_DIARIS):
        return set()
    with open(RUTA_DIARIS, encoding="utf-8") as f:
        return {(x.get("data"), x.get("model")) for x in csv.DictReader(f)}


def main():
    estat = torneo.carregar_estat()
    if not estat.get("carteres"):
        print("[!] Encara no hi ha cap cartera. Executa abans torneo.py.")
        return

    preus = torneo.baixar_preus()

    # La data del punt del gràfic ha de ser la de l'ÚLTIMA SESSIÓ DE BORSA,
    # no la de l'hora en què s'executa el robot. GitHub de vegades s'endarrereix
    # hores i, si datéssim per rellotge, passarien dues coses lletges:
    #   · un robot endarrerit fins passada la mitjanit datava el dia següent,
    #     i el dia real de mercat es perdia (va passar el 26/08/2026);
    #   · un robot del divendres executat el dissabte creava un punt en un dia
    #     amb el mercat tancat (va passar el 29/08/2026).
    # Com que el preu que dóna Yahoo sempre és el de l'últim tancament, datar-lo
    # per aquell dia és el correcte i, de propina, fa la feina idempotent.
    avui = torneo.ULTIMA_DATA_MERCAT or datetime.date.today().isoformat()
    if torneo.ULTIMA_DATA_MERCAT != datetime.date.today().isoformat():
        print(f"    (el robot corre el {datetime.date.today().isoformat()}, "
              f"però l'últim tancament de borsa és del {avui}: es data pel tancament)")
    ja_hi_son = files_existents()

    # ¿Hay precios de verdad? (un festivo o un fallo de red no debe ensuciar el histórico)
    p_spy = preus.get("SPY")
    if not p_spy:
        print("[!] Sense preus vàlids avui (mercat tancat o error de xarxa). No es guarda res.")
        return

    os.makedirs(config.CARPETA_DADES, exist_ok=True)
    nou = not os.path.exists(RUTA_DIARIS)
    escrites = 0

    with open(RUTA_DIARIS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nou:
            w.writerow(["data", "model", "valor"])

        # --- Cada IA ---
        for model_id, cartera in estat["carteres"].items():
            if (avui, model_id) in ja_hi_son:
                continue
            valor = torneo.valor_cartera(cartera, preus)
            if valor <= 0:
                continue
            w.writerow([avui, model_id, round(valor, 2)])
            escrites += 1
            print(f"    {model_id:10} {round(valor, 2):>10} €")

        # --- L'índex S&P 500 (el rival) ---
        if estat.get("index_unitats") and (avui, "index") not in ja_hi_son:
            valor_idx = estat["index_unitats"] * p_spy
            w.writerow([avui, "index", round(valor_idx, 2)])
            escrites += 1
            print(f"    {'index':10} {round(valor_idx, 2):>10} €  (S&P 500)")

    if escrites:
        print(f"\n[OK] {escrites} valors guardats a {RUTA_DIARIS} ({avui}).")
        print("     Ara pots actualitzar la web amb:  python generar_web.py")
    else:
        print(f"[i] Els valors d'avui ({avui}) ja hi eren. Res a fer.")


if __name__ == "__main__":
    main()
