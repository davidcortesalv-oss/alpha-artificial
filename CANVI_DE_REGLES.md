# Registre de canvis en les regles del torneig

> Aquest document existeix per **transparència metodològica**. Qualsevol
> modificació de les regles del torneig un cop començat queda registrada aquí,
> amb la data i el motiu. És material citable directament al Treball de Recerca.

---

## Canvi núm. 1 — Ampliació a accions concretes

**Data d'aplicació:** 27 de juliol de 2026
**Afecta a partir de:** setmana 4 del torneig
**Setmanes jugades amb les regles anteriors:** 1, 2 i 3

### Què s'ha canviat

| Element | Abans (setmanes 1-3) | Després (a partir de la setmana 4) |
|---|---|---|
| Univers d'inversió | 109 ETFs (fons cotitzats) | 108 ETFs **+ 114 accions d'empreses concretes** |
| Tipus d'actiu | Només fons diversificats | Fons **i** empreses individuals (Apple, Inditex, Nvidia…) |
| Límit de concentració | 40% per a qualsevol actiu | **20% per acció individual**, 40% per ETF |
| Països representats | Exposició global via fons | 15 països amb empreses concretes |
| Divises | Tot es tractava com una sola moneda | **Conversió real a euros** (USD, GBP, JPY, CHF, KRW) |
| Freqüència de decisió | 1 per setmana (dilluns) | 1 per setmana (dilluns) — **sense canvis** |
| Freqüència de valoració | Setmanal | **Diària** (dies de mercat) |

### Per què s'ha canviat

1. **Valor divulgatiu i analític.** Que una IA digui «compro Chevron perquè el
   petroli pujarà» és molt més informatiu —i molt més analitzable des de
   l'economia conductual— que «compro el sector energètic». Permet estudiar si
   les IAs justifiquen decisions concretes o s'amaguen darrere de generalitats.

2. **Aparició de nous biaixos observables.** Amb empreses concretes es poden
   mesurar biaixos que amb ETFs són invisibles:
   - **Biaix domèstic** (*home bias*): tendeixen a comprar empreses del seu país d'origen?
   - **Biaix de familiaritat**: compren només marques molt conegudes?
   - **Concentració**: aposten fort per una sola empresa o diversifiquen?

3. **Rigor en la valoració.** El sistema anterior barrejava implícitament
   monedes. Amb empreses europees (en euros), britàniques (en penics) i
   japoneses (en iens), la conversió a euros passa a ser imprescindible per
   calcular correctament el valor de les carteres.

### Per què el límit baixa al 20% per a accions

Una sola empresa pot caure un 40% en un dia per un mal resultat trimestral; un
fons diversificat, gairebé mai. Mantenir el límit del 40% per a accions
individuals hauria permès que una IA es jugués gairebé la meitat del capital a
una sola companyia, cosa que cap gestor professional faria i que convertiria el
torneig en una loteria. El límit del 20% per a accions i del 40% per a fons
reflecteix la pràctica habitual del sector.

### Impacte sobre les dades ja recollides

- Les setmanes **1, 2 i 3 es conserven íntegrament**: no s'ha esborrat ni
  modificat cap dada. Es van jugar amb el univers antic i així consten.
- El torneig **no s'ha reiniciat**: totes les carteres continuen des del valor
  que tenien, i el capital inicial de referència segueix sent 10.000 €.
- A l'anàlisi del TR cal tenir en compte que les tres primeres setmanes
  s'expliquen amb un univers d'inversió més limitat.

### Què NO s'ha canviat

- Capital inicial: 10.000 € per participant.
- Comissió: 0,1% per operació.
- Una decisió per setmana (dilluns).
- Totes les IAs reben exactament la mateixa informació.
- Sense palanquejament ni posicions curtes.
- Els cinc models participants i el rival (índex S&P 500).

### Ajust comptable associat (important per al TR)

En passar a comptabilitzar en euros de veritat, totes les carteres van
"caure" un 12,0% de cop. **No va ser una pèrdua de mercat**: fins aleshores
els preus en dòlars es tractaven com si fossin euros, i el canvi d'unitat de
compte (1 € = 1,14 $) va aflorar la diferència.

Per no introduir un salt artificial a les gràfiques, es va aplicar un **ajust
de redenominació** d'una sola vegada (script `corregir_divises.py`): es van
reescalar les unitats de cada cartera perquè, valorades correctament en
euros, valguessin exactament el mateix que valien just abans del canvi.

| Participant | Valor abans de l'ajust | Valor després | Factor |
|---|---|---|---|
| GPT | 8.508,97 € | 9.757,72 € | 1,1468 |
| Claude | 8.650,43 € | 9.824,11 € | 1,1357 |
| Gemini | 8.646,93 € | 9.797,62 € | 1,1331 |
| DeepSeek | 8.648,75 € | 9.824,11 € | 1,1359 |
| Mistral | 8.539,62 € | 9.707,67 € | 1,1368 |
| S&P 500 (índex) | 8.673,43 € | 9.871,36 € | 1,1381 |

Conseqüències:
- **La comparació entre participants no queda afectada**: tots es reescalen
  amb el mateix criteri, inclòs l'índex de referència.
- Les rendibilitats acumulades i les posicions relatives es mantenen.
- A partir de la setmana 8, l'efecte divisa (que un inversor europeu amb
  actius en dòlars pateix de veritat) **sí que compta** al resultat.

### Incidència tècnica detectada la mateixa setmana

A la setmana 8, la resposta de **Claude** es va tallar a mitges perquè el
límit de longitud de resposta (2.048 tokens) s'havia quedat curt amb un
univers de 222 actius. El sistema va registrar una decisió buida. Es va
corregir apujant el límit a 8.000 tokens i afegint una comprovació que
rebutja qualsevol resposta sense el camp `decisio`, de manera que un tall
similar quedi registrat com a error explícit i no com una decisió buida.

---

## Canvi núm. 2 — Correcció greu de les fonts de notícies

**Data:** 30 de juliol de 2026
**Afecta a partir de:** setmana 10
**Setmanes afectades pel problema:** 1 a 9

### El problema

Una de les tres fonts de titulars configurades (el canal RSS de mercats del
*Wall Street Journal*, `feeds.a.dj.com/rss/RSSMarketsMain.xml`) **estava
abandonada i servia sempre les mateixes notícies del 27 de gener de 2025** —
és a dir, amb **548 dies d'antiguitat**.

El motor omplia el cupó de titulars començant per aquesta font, de manera que
les IAs rebien setmana rere setmana el mateix bloc de notícies caducades
(encapçalat per «Stocks Sink in Broad AI Rout Sparked by China's DeepSeek»)
com si fossin els titulars d'aquella setmana.

L'efecte es va detectar per les pròpies justificacions dels models: Claude
escrivia coses com *«el DeepSeek rout porta ja set setmanes sent l'excusa
narrativa dominant»*. No era una observació de mercat: **era literalment la
mateixa notícia repetida**.

### Conseqüència per a l'anàlisi del TR

Les decisions de les setmanes 1 a 9 es van prendre amb **informació de context
obsoleta**. Els preus dels actius sempre van ser reals i actuals (venien de
Yahoo Finance), i el control de variables es va mantenir (totes les IAs van
rebre exactament els mateixos titulars), però el «context de mercat» no
reflectia l'actualitat d'aquelles setmanes.

Cal esmentar-ho en l'anàlisi: durant aquest període, les diferències de
rendibilitat entre models s'expliquen per la seva estratègia i per la
composició de la cartera, **no** per la seva capacitat d'interpretar notícies
recents.

### La correcció

| Element | Abans | Després |
|---|---|---|
| Fonts | 3 (una morta) | **9 fonts verificades** (CNBC ×2, Financial Times, Yahoo Finance, Investing.com ×2, Seeking Alpha, MarketWatch, Expansión) |
| Antiguitat màxima | sense límit | **8 dies**; el que és més vell es descarta |
| Repartiment | s'omplia amb la primera font | **es barregen totes** per torns (round-robin) |
| Filtre temàtic | cap | es prioritzen titulars de mercats i economia |
| Detecció d'errors | cap | si una font queda obsoleta, **el motor ho avisa** i la ignora |
| Nombre de titulars | 10 | 12 |

### Verificació que les IAs llegeixen les notícies

Perquè no torni a passar desapercebut i, sobretot, per **poder demostrar-ho al
TR**, ara cada IA ha de declarar obligatòriament:

- `noticies_clau`: els números dels titulars que han influït en la seva decisió.
- `lectura_noticies`: què n'ha deduït, en una o dues frases.

Tots dos camps es guarden a `dades/decisions.csv`. Això permet analitzar
**quin tipus de notícia mou cada model** i comprovar objectivament que no
ignoren el context. Exemple real de la primera prova (Claude):

> `noticies_clau: [1, 5, 6, 9]` — *«El creixement dels EUA s'ha desaccelerat
> (1,5%) amb inflació encara alta (3,3%), i el rendiment del bo a 30 anys
> s'acosta a màxims de 2007, senyal d'estanflació lleu…»*

---

## Canvi núm. 3 — Les IAs saben quan s'acaba el torneig

**Data:** 30 de juliol de 2026
**Afecta a partir de:** setmana 10

### Què s'ha canviat

Fins ara, cap IA sabia quant durava el torneig. Se'ls demanava que gestionessin
una cartera sense dir-los mai quin era el seu horitzó temporal. Ara, cada
briefing setmanal inclou:

> «Aquest torneig NO és una inversió a llarg termini. Es tanca el 31/12/2026:
> queden **22 setmanes**. La classificació final es decidirà exclusivament pel
> valor de la teva cartera aquell dia; no hi ha res després.
>
> Ets tu qui decideix si aquest horitzó ha d'influir en la teva estratègia i de
> quina manera. No se t'indica cap conclusió: forma part de la teva feina com a
> gestor valorar què implica.»

Les setmanes restants es calculen automàticament cada ronda a partir de
`DATA_FI` (config.py).

### Per què és metodològicament important

1. **Corregeix una asimetria irreal.** Un gestor professional sempre sap quin
   és el seu horitzó: no es gestiona igual un fons de pensions a 30 anys que un
   mandat de cinc mesos. Amagar-los aquesta dada els posava en una situació que
   no es dona a la realitat.

2. **No se'ls suggereix la conclusió.** Se'ls dona el **dato** i prou. No se'ls
   diu que siguin més prudents, ni més agressius, ni que evitin cap tipus
   d'actiu. Què deduir d'un horitzó curt és, precisament, una de les coses que
   el TR vol observar: forma part de la seva capacitat de raonament.

3. **Obre una línia d'anàlisi nova.** Es podrà comparar si els models ajusten
   la durada dels seus actius al termini que els queda, o si l'ignoren. La
   diferència entre models en aquest punt és un resultat en si mateix.

### Primera reacció observada (prova prèvia a la ronda oficial)

En la prova de validació, Claude va reaccionar sense que se li insinués res:

> «Substitueixo **TLT** (bons 20+ anys, molt sensibles a duració) per **SHY**
> (bons 1-3 anys, molt menys sensibles a pujades de tipus) […] mantenint un
> perfil moderat amb **l'horitzó de només 22 setmanes**.»

És a dir: va escurçar la durada de la seva renda fixa i va justificar-ho
citant l'horitzó. Aquesta conclusió no estava al prompt: la va treure ell.
Queda per veure si els altres quatre models arriben al mateix raonament, i
aquesta comparació és material directe per al TR.

---

## Millores metodològiques aplicades el mateix dia

No modifiquen les regles del joc, però sí què es mesura i es guarda:

| Millora | Per a què serveix al TR |
|---|---|
| **Registre de titulars** (`dades/titulars.csv`) | Demostra documentalment que les cinc IAs van rebre la mateixa informació cada setmana. Control de variables verificable. |
| **Còpia dels briefings** (`dades/briefings/`) | Es guarda el text exacte enviat a cada IA cada setmana. Reproductibilitat científica. |
| **Mètriques de risc** (volatilitat, màxima caiguda, ràtio de Sharpe) | Permet distingir entre guanyar molt i guanyar bé. Una IA pot batre l'índex assumint el doble de risc: sense aquestes mètriques, no es veuria. |
| **Comissions acumulades** (`dades/comissions.csv`) | Quantifica en euros el cost de sobreoperar. Evidència directa per a la hipòtesi sobre l'excés d'activitat. |
| **Exposició per sector i país** | Permet detectar el biaix domèstic i el de familiaritat. |
| **Consens i divergència** | Mostra en quins actius coincideixen les IAs i quines són apostes solitàries. |
| **Valoració diària** (`dades/valors_diaris.csv`) | Les decisions segueixen sent setmanals, però el valor de les carteres es calcula cada dia de mercat: gràfiques més precises i mètriques de risc molt més fiables. |

---

*Document generat el 27/07/2026. Si més endavant es fa cap altre canvi de
regles, s'afegirà com a «Canvi núm. 2» amb el mateix nivell de detall.*
