# -*- coding: utf-8 -*-
"""
comprovar_salut.py
==================

Revisa la última ronda jugada y avisa si algo ha ido mal.

POR QUÉ EXISTE
--------------
El 31/08/2026 Mistral dejó de responder (error 403: su plan ya no incluía el
modelo que usábamos). La ronda siguió adelante, anotó "mantenir" por defecto y
GitHub marcó la ejecución como CORRECTA, en verde. Nadie se enteró hasta una
semana después.

Una IA muerta no puede esconderse detrás de un tick verde: este script deja el
aviso bien visible en el resumen de la ejecución de GitHub.

No hace fallar la ronda a propósito: los datos de las otras IAs son válidos y
hay que guardarlos igual. Solo avisa.
"""

import os
import csv
import sys
import config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA_DECISIONS = os.path.join(config.CARPETA_DADES, "decisions.csv")

# Señales de que una IA no ha contestado de verdad.
SENYALS = ("sense resposta", "incidència tècnica", "error HTTP")


def main():
    if not os.path.exists(RUTA_DECISIONS):
        print("[!] Encara no hi ha decisions.")
        return

    with open(RUTA_DECISIONS, encoding="utf-8") as f:
        files = list(csv.DictReader(f))
    if not files:
        return

    ultima = max(x["data"] for x in files)
    ronda = [x for x in files if x["data"] == ultima]

    fallades = [
        x for x in ronda
        if any(s in x.get("justificacio", "") for s in SENYALS)
        or x.get("confianca") in ("0", "")
    ]

    linies = [f"## Ronda del {ultima} (setmana {ronda[0]['setmana']})", ""]
    for x in ronda:
        ok = x not in fallades
        nom = config.MODELS.get(x["model"], {}).get("nom", x["model"])
        if ok:
            linies.append(f"- ✅ **{nom}** — {x['decisio']} "
                          f"(confiança {x['confianca']}, {x['valor_cartera']} €)")
        else:
            motiu = x.get("justificacio", "")[:120]
            linies.append(f"- ❌ **{nom}** — NO HA RESPOST: {motiu}")

    if fallades:
        noms = ", ".join(config.MODELS.get(x["model"], {}).get("nom", x["model"])
                         for x in fallades)
        linies += ["", f"> ⚠️ **{len(fallades)} de {len(ronda)} IAs no han respost: {noms}.**",
                   "> Cal revisar la clau o el pla del proveïdor abans de la ronda vinent."]

    text = "\n".join(linies)
    print(text)

    # En GitHub, esto sale en grande en la pestaña de la ejecución.
    resum = os.environ.get("GITHUB_STEP_SUMMARY")
    if resum:
        with open(resum, "a", encoding="utf-8") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
