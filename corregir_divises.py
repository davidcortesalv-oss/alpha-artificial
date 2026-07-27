# -*- coding: utf-8 -*-
"""
corregir_divises.py — Ajust puntual pel canvi de comptabilitat a euros
=======================================================================
PER QUÈ EXISTEIX AQUEST FITXER

Fins a la setmana 7, el motor tractava els preus en dòlars com si fossin
euros (tots els ETFs cotitzen en USD, així que el càlcul era coherent
internament però l'etiqueta "€" era incorrecta).

A la setmana 8 es va afegir la conversió real a euros. Efecte immediat:
totes les carteres van "caure" un 12% de cop. NO va ser una pèrdua real
de mercat, va ser el canvi d'unitat de compte (1 € = 1,14 $).

Aquest script fa un ajust d'una sola vegada: reescala les unitats de cada
cartera perquè, valorades correctament en euros, valguin exactament el
mateix que valien just abans del canvi. Així:
  · no hi ha cap salt artificial a la gràfica,
  · l'historial anterior es conserva intacte,
  · i a partir d'ara tot es comptabilitza correctament en euros.

És l'equivalent a una redenominació comptable. Queda documentat a
CANVI_DE_REGLES.md.

    python corregir_divises.py

S'executa UNA sola vegada. Si es torna a executar quan ja no cal, avisa i
no toca res.
"""

import os
import csv
import json
import sys
import config
import torneo

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA_MARCA = os.path.join(config.CARPETA_DADES, ".divises_corregides")


def main():
    if os.path.exists(RUTA_MARCA):
        print("[i] L'ajust de divises ja es va aplicar. No cal tornar-hi.")
        return

    estat = torneo.carregar_estat()
    if not estat.get("carteres"):
        print("[!] No hi ha carteres. Res a corregir.")
        return

    # --- Valor de referència: l'últim registrat ABANS del canvi ---
    files = list(csv.DictReader(open(torneo.RUTA_DECISIONS, encoding="utf-8")))
    setmana_actual = estat.get("setmana", 0)
    referencia = {}
    for f in files:
        try:
            s = int(float(f.get("setmana", 0)))
        except ValueError:
            continue
        m = (f.get("model") or "").strip()
        if s == setmana_actual - 1 and m:
            try:
                referencia[m] = float(f.get("valor_cartera") or 0)
            except ValueError:
                pass

    if not referencia:
        print(f"[!] No trobo valors de la setmana {setmana_actual - 1}. Res a fer.")
        return

    preus = torneo.baixar_preus()

    print(f"\n[2] Reescalant carteres (referència: setmana {setmana_actual - 1})\n")
    for mid, cartera in estat["carteres"].items():
        valor_ara = torneo.valor_cartera(cartera, preus)
        objectiu = referencia.get(mid)
        if not objectiu or not valor_ara:
            print(f"    {mid:10} sense referència, no es toca.")
            continue
        factor = objectiu / valor_ara
        for tk in cartera:
            cartera[tk] = round(cartera[tk] * factor, 6)
        nou = torneo.valor_cartera(cartera, preus)
        print(f"    {mid:10} {valor_ara:9.2f} € → {nou:9.2f} €   (factor {factor:.4f})")

    # --- El mateix per a l'índex S&P 500 (el rival) ---
    files_idx = list(csv.DictReader(open(torneo.RUTA_INDEX, encoding="utf-8"))) \
        if os.path.exists(torneo.RUTA_INDEX) else []
    ref_idx = None
    for f in files_idx:
        try:
            if int(float(f.get("setmana", 0))) == setmana_actual - 1:
                ref_idx = float(f.get("valor") or 0)
        except ValueError:
            continue
    p_spy = preus.get("SPY")
    if ref_idx and p_spy and estat.get("index_unitats"):
        valor_ara = estat["index_unitats"] * p_spy
        factor = ref_idx / valor_ara
        estat["index_unitats"] = round(estat["index_unitats"] * factor, 6)
        print(f"    {'index':10} {valor_ara:9.2f} € → "
              f"{estat['index_unitats'] * p_spy:9.2f} €   (factor {factor:.4f})")

    # --- Corregir la fila ja escrita de la setmana del canvi ---
    for f in files:
        try:
            if int(float(f.get("setmana", 0))) != setmana_actual:
                continue
        except ValueError:
            continue
        m = (f.get("model") or "").strip()
        if m in estat["carteres"]:
            f["valor_cartera"] = round(
                torneo.valor_cartera(estat["carteres"][m], preus), 2)
    with open(torneo.RUTA_DECISIONS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=files[0].keys())
        w.writeheader()
        w.writerows(files)

    if files_idx and ref_idx and p_spy:
        for f in files_idx:
            try:
                if int(float(f.get("setmana", 0))) == setmana_actual:
                    f["valor"] = round(estat["index_unitats"] * p_spy, 2)
            except ValueError:
                continue
        with open(torneo.RUTA_INDEX, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=files_idx[0].keys())
            w.writeheader()
            w.writerows(files_idx)

    torneo.guardar_carteres(estat, preus)
    torneo.guardar_estat(estat)

    with open(RUTA_MARCA, "w", encoding="utf-8") as f:
        f.write("Ajust de divises aplicat. Veure CANVI_DE_REGLES.md\n")

    print("\n[OK] Ajust aplicat. La gràfica ja no tindrà el salt artificial del 12%.")
    print("     Actualitza la web amb:  python generar_web.py")


if __name__ == "__main__":
    main()
