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
import math
import tempfile
import config
import torneo

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA_DIARIS = os.path.join(config.CARPETA_DADES, "valors_diaris.csv")


def guardar_valors(ruta, data, valors):
    """Actualiza la última sesión sin duplicarla ni reescribir días anteriores.

    Un refresco intradía no debe bloquear el cierre nocturno. La escritura
    es atómica: un fallo nunca deja medio CSV guardado.
    """
    files = []
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8", newline="") as f:
            files = list(csv.DictReader(f))
    if files and data < max(f["data"] for f in files):
        raise ValueError("Cotitzacions anteriors a l'última valoració: no es modifica l'historial.")
    if not valors or any(not math.isfinite(v) or v <= 0 for v in valors.values()):
        raise ValueError("Valoració incompleta o no vàlida: no es desa res.")
    afectades = [f for f in files if f["data"] == data and f["model"] in valors]
    anteriors = {f["model"]: float(f["valor"]) for f in afectades}
    canvis = sum(anteriors.get(mid) != round(v, 2) for mid, v in valors.items())
    if not canvis and len(afectades) == len(valors):
        return 0
    noves = [f for f in files if not (f["data"] == data and f["model"] in valors)]
    noves.extend({"data": data, "model": mid, "valor": round(v, 2)} for mid, v in valors.items())
    carpeta = os.path.dirname(os.path.abspath(ruta))
    os.makedirs(carpeta, exist_ok=True)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=carpeta,
                                         prefix=".valoracio-", suffix=".tmp", delete=False) as f:
            temporal = f.name
            w = csv.DictWriter(f, fieldnames=["data", "model", "valor"])
            w.writeheader()
            w.writerows(noves)
        os.replace(temporal, ruta)
        temporal = None
    finally:
        if temporal is not None and os.path.exists(temporal):
            os.remove(temporal)
    return canvis


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
    # Durant la sessió el punt és provisional. En tornar a executar el script
    # després del tancament, s'actualitza el mateix dia en lloc de saltar-lo.
    avui = torneo.ULTIMA_DATA_MERCAT
    if not avui:
        raise ValueError("No s'ha pogut verificar la data de mercat. No es desa cap valoració.")
    if torneo.ULTIMA_DATA_MERCAT != datetime.date.today().isoformat():
        print(f"    (el robot corre el {datetime.date.today().isoformat()}, "
              f"però les cotitzacions corresponen al {avui}: es data per la sessió)")

    # ¿Hay precios de verdad? (un festivo o un fallo de red no debe ensuciar el histórico)
    p_spy = preus.get("SPY")
    if not p_spy:
        print("[!] Sense preus vàlids avui (mercat tancat o error de xarxa). No es guarda res.")
        return

    necessaris = {tk for cartera in estat["carteres"].values() for tk, unitats in cartera.items()
                  if tk != "EFECTIU" and unitats > 0}
    if estat.get("index_unitats"):
        necessaris.add("SPY")
    absents = sorted(tk for tk in necessaris
                     if not isinstance(preus.get(tk), (int, float))
                     or not math.isfinite(preus[tk]) or preus[tk] <= 0)
    if absents:
        raise ValueError("Falten preus d'actius en cartera: " + ", ".join(absents) + ". No es desa res.")

    valors = {mid: torneo.valor_cartera(cartera, preus) for mid, cartera in estat["carteres"].items()}
    if estat.get("index_unitats"):
        valors["index"] = estat["index_unitats"] * p_spy
    escrites = guardar_valors(RUTA_DIARIS, avui, valors)
    for model_id, valor in valors.items():
        print(f"    {model_id:10} {round(valor, 2):>10} €")

    if escrites:
        print(f"\n[OK] {escrites} valors actualitzats a {RUTA_DIARIS} ({avui}).")
        print("     Cotitzacions disponibles ara; valoració provisional mentre el mercat és obert.")
        print("     Ara pots actualitzar la web amb:  python generar_web.py")
    else:
        print(f"[i] Els valors de la sessió ({avui}) no han canviat. Res a fer.")


if __name__ == "__main__":
    main()
