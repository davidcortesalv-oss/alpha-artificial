# -*- coding: utf-8 -*-
"""
corregir_dates_diaries.py
=========================

Repara las fechas mal puestas en dades/valors_diaris.csv entre el 26/08/2026
y el 01/09/2026.

QUÉ PASÓ (en corto)
-------------------
El robot de precios diarios ponía como fecha "el día en que se ejecuta"
(datetime.date.today()). Normalmente corría a las 21:42 UTC, con la bolsa ya
cerrada, así que la fecha era correcta.

A finales de agosto de 2026 GitHub sufrió retrasos enormes en sus tareas
programadas (hasta 7h45m). Varios robots acabaron ejecutándose de MADRUGADA,
ya pasada la medianoche. Como la bolsa de EE.UU. abre a las 13:30 UTC, a esa
hora el último cierre disponible seguía siendo el del día anterior... pero el
robot lo guardaba con la fecha del día nuevo.

Resultado: toda la serie quedó desplazada un día de bolsa. Por eso "faltaba"
el miércoles 26 y "sobraba" un sábado 29 con la bolsa cerrada.

QUÉ HACE ESTE SCRIPT
--------------------
NO inventa ningún dato. Solo devuelve cada fila a la fecha del cierre que
realmente contiene. Es un renombrado, no un recálculo.

La causa de raíz ya está arreglada en actualitzar_preus.py: ahora la fecha se
toma del último cierre real de Yahoo, no del reloj del robot.
"""

import os
import csv
import sys
import shutil
import config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUTA = os.path.join(config.CARPETA_DADES, "valors_diaris.csv")

# Cada fila guardada -> el día de bolsa que de verdad contiene.
# Deducido de la hora exacta en que se ejecutó cada robot (registro de GitHub):
#   robot 27/08 01:03 UTC -> antes de abrir la bolsa -> último cierre: 26/08
#   robot 28/08 05:49 UTC -> antes de abrir la bolsa -> último cierre: 27/08
#   robot 29/08 03:22 UTC -> sábado de madrugada     -> último cierre: 28/08
#   robot 01/09 00:46 UTC -> antes de abrir la bolsa -> último cierre: 31/08
CORRECCIONS = {
    "2026-08-27": "2026-08-26",
    "2026-08-28": "2026-08-27",
    "2026-08-29": "2026-08-28",
    "2026-09-01": "2026-08-31",
}


def main():
    if not os.path.exists(RUTA):
        print("[!] No hi ha valors_diaris.csv. No hi ha res a corregir.")
        return

    with open(RUTA, encoding="utf-8") as f:
        files = list(csv.DictReader(f))

    if not files:
        print("[!] El fitxer és buit.")
        return

    # Seguridad: hay que reconocer el fichero SIN corregir, no las fechas a
    # corregir. Ojo, que "2026-08-27" y "2026-08-28" también existen DESPUÉS de
    # corregir (son el resultado del renombrado), así que mirarlas haría que el
    # script se aplicase dos veces y destrozase los datos.
    # La huella inequívoca del fichero roto es el SÁBADO 29/08: un día con la
    # bolsa cerrada, que solo puede estar ahí si la corrección no se ha hecho.
    SENYAL_SENSE_CORREGIR = "2026-08-29"
    if SENYAL_SENSE_CORREGIR not in {x["data"] for x in files}:
        print("[=] Les dates ja estan corregides (no hi ha el dissabte 29/08). No es toca res.")
        return

    còpia = RUTA + ".abans_de_corregir_dates"
    if os.path.exists(còpia):
        print(f"[!] Ja existeix {os.path.basename(còpia)}; no se sobreescriu.")
    else:
        shutil.copy2(RUTA, còpia)
        print(f"[1] Còpia de seguretat a: {os.path.basename(còpia)}")

    canviades = 0
    for x in files:
        nova = CORRECCIONS.get(x["data"])
        if nova:
            x["data"] = nova
            canviades += 1

    # Quitar posibles duplicados (data, model), quedándonos con el último.
    vistes = {}
    for x in files:
        vistes[(x["data"], x["model"])] = x
    files = sorted(vistes.values(), key=lambda x: (x["data"], x["model"]))

    with open(RUTA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["data", "model", "valor"])
        w.writeheader()
        w.writerows(files)

    print(f"[2] {canviades} files reetiquetades amb el seu dia de borsa real.")
    print("[3] Dies que ara hi ha al fitxer (des del 24/08):")
    for d in sorted({x["data"] for x in files if x["data"] >= "2026-08-24"}):
        print(f"      {d}")
    print("\n[✓] Fet. La causa de fons ja està arreglada a actualitzar_preus.py.")


if __name__ == "__main__":
    main()
