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
├── config.py              → totes les regles, 108 ETFs i 114 accions
├── torneo.py              → el motor (una ronda setmanal completa)
├── connectors_ia.py       → les trucades reals a cada API d'IA
├── actualitzar_preus.py   → refresca el valor de les carteres cada dia (gratis)
├── generar_web.py         → converteix els CSV en dades per a la web
├── generar_univers_web.py → passa l'univers de config.py a la web
├── prompts/
│   └── prompt_setmanal.txt → les instruccions que rep cada IA
├── dades/                 → l'historial del torneig
│   ├── decisions.csv       → totes les decisions i justificacions
│   ├── canvis.csv          → cada operació aplicada
│   ├── carteres.csv        → foto actual de cada cartera (amb sector i país)
│   ├── comissions.csv      → què ha pagat cada IA en comissions
│   ├── titulars.csv        → els titulars que ha vist cada IA cada setmana
│   ├── valors_diaris.csv   → valor de cada cartera cada dia de mercat
│   ├── briefings/          → el text exacte enviat a cada IA (traçabilitat)
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
- 1 decisió per setmana (dilluns). El valor de les carteres es recalcula **cada dia** de mercat.
- Univers: **114 accions d'empreses concretes** (de 15 països) i **108 ETFs**.
- Màxim **20%** de la cartera en una sola acció; màxim **40%** en un sol ETF.
- Comissió del 0,1% per operació.
- Sense palanquejament ni posicions curtes.
- Totes les IAs reben exactament la mateixa informació (mateixos preus i titulars).
- Tots els preus es converteixen a **euros** abans de calcular res.

> ⚠️ Les regles es van ampliar la setmana 4 (27/07/2026). El detall complet i el
> motiu estan a [CANVI_DE_REGLES.md](CANVI_DE_REGLES.md) — document pensat per
> citar-lo directament al Treball de Recerca.

## Estat actual

🟡 En construcció — motor complet en mode de prova (IAs simulades) i web
funcionant amb dades de demostració. Quan el torneig arranqui de veritat,
esborra `dades/` (les dades de prova), posa les claus i llança la primera ronda.
