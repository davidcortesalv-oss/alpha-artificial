# -*- coding: utf-8 -*-
"""
prova_connexio.py — Comprova UNA connexió d'IA des de GitHub Actions
====================================================================
S'executa dins del workflow "Prova de connexions" (un pas per IA).
Envia un missatge mínim ("Respon: OK") al model indicat i falla el pas
si la clau no hi és o l'API no respon després de 3 intents.

Ús:  python .github/prova_connexio.py gpt|claude|gemini|deepseek|mistral
"""
import sys
import time

sys.path.insert(0, ".")
import config
import connectors_ia as con

model_id = sys.argv[1]
nom = config.MODELS[model_id]["nom"]
model_api = config.MODELS[model_id]["model_api"]

clau = con.clau_de(model_id)
if not clau:
    print(f"[X] {nom}: NO hi ha clau. Revisa el Secret "
          f"'{con.VARIABLE_CLAU[model_id]}' (Settings → Secrets → Actions).")
    sys.exit(1)

darrer_error = ""
for intent in range(1, 4):
    try:
        resposta = con.TRUCADES[model_id](clau, model_api, "Respon nomes amb la paraula: OK")
        print(f"[OK] {nom} ({model_api}) ha respost: {resposta.strip()[:40]}")
        sys.exit(0)
    except Exception as e:
        darrer_error = str(e)[:160]
        print(f"    intent {intent}/3 fallit: {darrer_error}")
        if intent < 3:
            time.sleep(20)

print(f"[X] {nom}: sense resposta despres de 3 intents. Ultim error: {darrer_error}")
sys.exit(1)
