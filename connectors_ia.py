# -*- coding: utf-8 -*-
"""
connectors_ia.py — La "centralita" que habla con cada IA real
=============================================================
Cada empresa (OpenAI, Anthropic, Google, DeepSeek, Mistral) tiene su propia
forma de recibir mensajes. Este archivo esconde esas diferencias: el motor
(torneo.py) solo llama a  demanar(model_id, briefing)  y recibe la respuesta.

CÓMO SE CONFIGURAN LAS CLAVES (elige la que te sea más cómoda):
  a) Copia secrets.example.txt como "secrets.txt" y pon ahí tus claves.
  b) O define variables de entorno (OPENAI_API_KEY, ANTHROPIC_API_KEY...).
     En GitHub Actions se hace con los "Secrets" del repositorio.

Mientras no haya claves, el motor sigue funcionando en MODE_SIMULAT.
"""

import os
import json
import re
import time
import requests
import config

ARXIU_SECRETS = "secrets.txt"

# Qué variable guarda la clave de cada modelo (mismo nombre que secrets.example.txt)
VARIABLE_CLAU = {
    "gpt":      "OPENAI_API_KEY",
    "claude":   "ANTHROPIC_API_KEY",
    "gemini":   "GOOGLE_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "mistral":  "MISTRAL_API_KEY",
}

# Dónde consigue David cada clave (se muestra en la web, panel d'APIs)
URL_CONSOLA = {
    "gpt":      "https://platform.openai.com/api-keys",
    "claude":   "https://console.anthropic.com/",
    "gemini":   "https://aistudio.google.com/apikey",
    "deepseek": "https://platform.deepseek.com/api_keys",
    "mistral":  "https://console.mistral.ai/api-keys",
}


# ------------------------------------------------------------------
#  Lectura de claves: primero secrets.txt, después variables de entorno
# ------------------------------------------------------------------
def llegir_claus():
    """Devuelve {NOMBRE_VARIABLE: clave} con todas las claves que encuentre."""
    claus = {}
    if os.path.exists(ARXIU_SECRETS):
        with open(ARXIU_SECRETS, encoding="utf-8") as f:
            for linia in f:
                linia = linia.strip()
                if not linia or linia.startswith("#") or "=" not in linia:
                    continue
                nom, _, valor = linia.partition("=")
                valor = valor.strip()
                if valor and "aqui_la_teva_clau" not in valor:
                    claus[nom.strip()] = valor
    for nom in VARIABLE_CLAU.values():
        if os.environ.get(nom):
            claus[nom] = os.environ[nom]
    return claus


def clau_de(model_id):
    """Devuelve la clave API de un modelo, o None si aún no está configurada."""
    return llegir_claus().get(VARIABLE_CLAU.get(model_id, ""))


def estat_connexions():
    """Estado de cada conexión, para la web y para los avisos del motor.
    Devuelve {model_id: {"clau": True/False, "actiu": True/False, ...}}."""
    estat = {}
    for mid, dades in config.MODELS.items():
        estat[mid] = {
            "clau": clau_de(mid) is not None,
            "actiu": bool(dades.get("actiu")),
            "model_api": dades.get("model_api", ""),
            "variable": VARIABLE_CLAU.get(mid, ""),
            "url_consola": URL_CONSOLA.get(mid, ""),
        }
    return estat


# ------------------------------------------------------------------
#  Llamada a cada proveedor (todas devuelven el TEXTO de la respuesta)
# ------------------------------------------------------------------
TEMPS_MAXIM = 120  # segundos de espera antes de rendirse


def _openai_compatible(url, clau, model, briefing):
    """OpenAI, DeepSeek y Mistral usan el mismo formato de petición."""
    resposta = requests.post(
        url,
        headers={"Authorization": f"Bearer {clau}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": briefing}],
        },
        timeout=TEMPS_MAXIM,
    )
    resposta.raise_for_status()
    return resposta.json()["choices"][0]["message"]["content"]


def _trucar_gpt(clau, model, briefing):
    return _openai_compatible("https://api.openai.com/v1/chat/completions", clau, model, briefing)


def _trucar_deepseek(clau, model, briefing):
    return _openai_compatible("https://api.deepseek.com/chat/completions", clau, model, briefing)


def _trucar_mistral(clau, model, briefing):
    return _openai_compatible("https://api.mistral.ai/v1/chat/completions", clau, model, briefing)


def _trucar_claude(clau, model, briefing):
    resposta = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": clau,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": briefing}],
        },
        timeout=TEMPS_MAXIM,
    )
    resposta.raise_for_status()
    # La resposta pot portar més d'un bloc (p. ex. "thinking" + "text"):
    # ens quedem amb tots els blocs de text units.
    blocs = resposta.json().get("content", [])
    return "".join(b.get("text", "") for b in blocs if b.get("type") == "text")


def _trucar_gemini(clau, model, briefing):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    resposta = requests.post(
        url,
        headers={"x-goog-api-key": clau, "Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": briefing}]}]},
        timeout=TEMPS_MAXIM,
    )
    resposta.raise_for_status()
    return resposta.json()["candidates"][0]["content"]["parts"][0]["text"]


TRUCADES = {
    "gpt": _trucar_gpt,
    "claude": _trucar_claude,
    "gemini": _trucar_gemini,
    "deepseek": _trucar_deepseek,
    "mistral": _trucar_mistral,
}


# ------------------------------------------------------------------
#  Convertir el texto de la IA en el JSON de decisión
# ------------------------------------------------------------------
def extreure_json(text):
    """Las IAs deben responder solo JSON, pero a veces lo envuelven en texto
    o en ```json ... ```. Esta función rescata el primer objeto {...} válido."""
    text = text.strip()
    # Quitar envoltorio de bloque de código si lo hay
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Buscar el primer { ... } equilibrado dentro del texto
    inici = text.find("{")
    while inici != -1:
        profunditat = 0
        for i in range(inici, len(text)):
            if text[i] == "{":
                profunditat += 1
            elif text[i] == "}":
                profunditat -= 1
                if profunditat == 0:
                    try:
                        return json.loads(text[inici:i + 1])
                    except json.JSONDecodeError:
                        break
        inici = text.find("{", inici + 1)
    return None


INTENTS = 5                # cuántas veces probamos si la API falla
ESPERA_ENTRE_INTENTS = 45  # segundos entre intento e intento
# (el torneo corre una vez por semana: vale la pena insistir unos minutos
#  antes de dar por perdida la decisión de una IA; Google, por ejemplo,
#  devuelve errores 503 intermitentes en su nivel gratuito)


def demanar(model_id, briefing):
    """Envía el briefing a la IA indicada y devuelve su decisión (dict).
    Si la API falla (cosa habitual de manera puntual: un 503, un límit de
    peticions...), ho reintenta fins a 3 cops. Si tot i així no hi ha
    manera, devuelve (None, motivo) para que el motor lo registre sin
    romperse: esa IA queda como "mantenir" esa semana."""
    clau = clau_de(model_id)
    if not clau:
        return None, f"Sense clau API ({VARIABLE_CLAU.get(model_id)})"

    model_api = config.MODELS[model_id].get("model_api", "")
    error = ""
    for intent in range(1, INTENTS + 1):
        try:
            text = TRUCADES[model_id](clau, model_api, briefing)
            decisio = extreure_json(text)
            if decisio is None:
                error = "La resposta no contenia un JSON vàlid"
            else:
                return decisio, ""
        except requests.exceptions.RequestException as e:
            error = f"Error de connexió: {e}"
        except Exception as e:
            # Cualquier otra sorpresa (formato inesperado, etc.)
            error = f"Resposta inesperada de l'API: {type(e).__name__}: {e}"
        if intent < INTENTS:
            print(f"      [{model_id}] intent {intent} fallit ({error[:80]}...). "
                  f"Reintento en {ESPERA_ENTRE_INTENTS} s")
            time.sleep(ESPERA_ENTRE_INTENTS)
    return None, error
