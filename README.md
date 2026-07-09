# ALPHA ARTIFICIAL — Pot una IA batre el mercat?

Sistema del torneig d'inversió autònoma entre cinc models d'intel·ligència artificial, desenvolupat com a part del Treball de Recerca de David Cortés (Monlau, 2026-27).

## Què fa aquest sistema

Cada dilluns, de manera automàtica:

1. Descarrega els preus reals de mercat d'una llista tancada de ~110 ETFs (via `yfinance`).
2. Recupera l'estat del torneig (les carteres de la setmana anterior).
3. Munta un informe setmanal idèntic per a totes les IAs (preus, context i titulars).
4. Envia l'informe a cada model i recull la seva decisió d'inversió (en format JSON).
5. Comprova que cada decisió respecta les regles i **l'aplica de veritat** (compres i vendes amb comissió).
6. Ho guarda tot amb historial complet i actualitza la web pública.

## Estructura del projecte

```
alpha-artificial/
├── config.py              → totes les regles i l'univers de ~110 ETFs
├── torneo.py              → el motor (una ronda setmanal completa)
├── connectors_ia.py       → les trucades reals a cada API d'IA
├── generar_web.py         → converteix els CSV en dades per a la web
├── prompts/
│   └── prompt_setmanal.txt → les instruccions que rep cada IA
├── dades/                 → l'historial del torneig
│   ├── decisions.csv       → totes les decisions i justificacions
│   ├── canvis.csv          → cada operació aplicada
│   ├── carteres.csv        → foto actual de cada cartera
│   ├── index.csv           → la línia del S&P 500 (el rival)
│   ├── destacats.csv       → moments destacats (opcional, escrits a mà)
│   └── estat_torneig.json  → la memòria entre setmanes
├── web/                   → la web pública (HTML/CSS/JS, sense dependències)
│   ├── index.html          → l'aplicació (tauler, informes, canvis, ETFs...)
│   ├── app.js              → la lògica de totes les vistes
│   ├── grafica.js          → el motor de gràfiques interactives
│   ├── etfs.js             → l'univers d'ETFs amb descripcions
│   ├── dades_demo.js       → dades de demostració (fins que arranqui el torneig)
│   └── dades.json          → dades REALS (les escriu generar_web.py)
├── requirements.txt       → llibreries necessàries
└── secrets.example.txt    → plantilla per a les claus API
```

## Com s'executa

```bash
pip install -r requirements.txt   # només el primer cop
python torneo.py                  # una ronda setmanal (ara en mode simulat)
python generar_web.py             # actualitza les dades de la web
```

Per veure la web en local: obre `web/index.html` al navegador, o millor:

```bash
python -m http.server 8099 --directory web
```

i visita http://localhost:8099

## Les claus API

La web té una secció **«Configuració d'APIs»** que mostra l'estat de cada connexió.
Per connectar una IA de veritat:

1. Aconsegueix la clau al web del proveïdor (enllaços a la mateixa secció).
2. Copia `secrets.example.txt` com a `secrets.txt` i posa-hi la clau
   (o defineix-la com a variable d'entorn / Secret de GitHub).
3. A `config.py`, posa `actiu: True` al model.
4. Quan tot estigui a punt, canvia `MODE_SIMULAT = False` a `torneo.py`.

Claus que fa servir el sistema: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
`GOOGLE_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`.
**Cap clau no viatja mai a la web**: només les llegeix el motor en local o a GitHub Actions.

## Regles del torneig

- 10.000 € virtuals per participant, amb preus reals de mercat.
- 1 decisió per setmana (dilluns).
- Màxim 40% de la cartera en un sol ETF.
- Comissió del 0,1% per operació.
- Sense palanquejament ni posicions curtes.
- Totes les IAs reben exactament la mateixa informació.

## Estat actual

🟡 En construcció — motor complet en mode de prova (IAs simulades) i web
funcionant amb dades de demostració. Quan el torneig arranqui de veritat,
esborra `dades/` (les dades de prova), posa les claus i llança la primera ronda.
