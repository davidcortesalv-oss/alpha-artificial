# -*- coding: utf-8 -*-
"""
netejar_dades.py — Repara files incompletes de l'historial
===========================================================
Si una IA falla (API caiguda, resposta tallada), el motor pot haver deixat
una fila amb la decisió buida. Això embruta l'anàlisi del TR: una fila
buida no és el mateix que "va decidir mantenir".

Aquest script busca aquestes files i les completa deixant constància
explícita del que va passar, en comptes de deixar-les en blanc.

    python netejar_dades.py
"""

import os
import csv
import sys
import config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA = os.path.join(config.CARPETA_DADES, "decisions.csv")

MOTIU = ("(incidència tècnica: la resposta del model es va tallar i no es va "
         "poder llegir la decisió; la cartera va quedar sense canvis. "
         "Veure CANVI_DE_REGLES.md)")


def main():
    if not os.path.exists(RUTA):
        print(f"[!] No trobo {RUTA}.")
        return

    with open(RUTA, encoding="utf-8") as f:
        files = list(csv.DictReader(f))
    if not files:
        print("[!] El fitxer és buit.")
        return

    arreglades = []
    for fila in files:
        if (fila.get("decisio") or "").strip():
            continue        # aquesta fila està bé
        fila["decisio"] = "mantenir"
        fila["nivell_risc"] = fila.get("nivell_risc") or "—"
        fila["confianca"] = fila.get("confianca") or "0"
        if not (fila.get("justificacio") or "").strip():
            fila["justificacio"] = MOTIU
        arreglades.append(f"S{fila.get('setmana')} · {fila.get('model')}")

    if not arreglades:
        print("[OK] Cap fila incompleta. Les dades ja estan netes.")
        return

    with open(RUTA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=files[0].keys())
        w.writeheader()
        w.writerows(files)

    print(f"[OK] {len(arreglades)} fila(es) completada(es):")
    for x in arreglades:
        print(f"     {x}")
    print("\n     Ara actualitza la web:  python generar_web.py")


if __name__ == "__main__":
    main()
