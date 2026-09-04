# Auditoria del torneig — són reals els resultats?

> **Actualitzat el 4 de setembre de 2026** (setmana 15 de 22) amb la secció 6,
> que explica l'incident de les dues setmanes que el torneig va passar
> desatès. Les seccions 1 a 5 són de la revisió original.
>
> Document d'auditoria fet el **17 d'agost de 2026** (setmana 13 de 22) per
> respondre la pregunta més important del TR: **els números que ensenya la web
> són els que tindria de veritat algú que hagués invertit aquests diners?**
>
> Tot el que hi ha aquí està comprovat amb dades, no amb suposicions. Els
> càlculs de verificació es van fer de manera **independent**: baixant els
> preus de Yahoo Finance i reconstruint cada cartera des de zero, sense mirar
> les dades guardades pel torneig.

---

## 1. Els valors de les carteres són reals

Es van agafar les **unitats** que té cada IA de cada actiu, es van multiplicar
pel **preu real** de Yahoo Finance convertit a euros, i es va comparar amb el
que ensenya la web:

| Participant | Reconstruït des de zero | La web deia | Diferència |
|---|---|---|---|
| GPT | 10.149,00 € | 10.107,47 € | −41,53 € (0,41 %) |
| Claude | 10.060,63 € | 10.028,22 € | −32,41 € (0,32 %) |
| Gemini | 9.879,78 € | 9.887,44 € | +7,66 € (0,08 %) |
| DeepSeek | 10.037,48 € | 10.005,79 € | −31,69 € (0,32 %) |
| Mistral | 9.820,35 € | 9.798,27 € | −22,08 € (0,23 %) |
| **S&P 500** | 10.150,02 € | 10.158,71 € | +8,69 € (0,09 %) |

**Conclusió:** les diferències són inferiors al 0,5 % i s'expliquen perquè la
web guarda el valor del moment en què es va executar el robot i la
verificació fa servir el preu d'unes hores després. **No hi ha cap desviació
sistemàtica.** Les carteres són reproduïbles per qualsevol.

### L'índex es pot comprovar a mà

L'S&P 500 del torneig són **15,194748 participacions de SPY**, comprades el
9 de juliol de 2026:

```
SPY el 09/07/2026 = 751,71 $  ·  EUR/USD = 1,1422  →  658,12 €
10.000 € / 658,12 € = 15,194748 participacions
```

Qualsevol pot agafar Yahoo Finance, mirar aquestes dues dades i obtenir el
mateix número.

---

## 2. És estrany que cap IA vagi per davant de l'índex?

**No. És el resultat esperat.**

### Què ha passat de veritat

Totes les IAs **van superar l'índex el 13 de juliol** (la primera setmana):

| IA | Millor moment vs índex | Punts per davant | Ara |
|---|---|---|---|
| GPT | +0,48 pts (13/07) | 1 de 20 | −0,51 pts |
| Gemini | +0,43 pts (13/07) | 2 de 20 | −2,71 pts |
| Claude | +0,41 pts (13/07) | 2 de 20 | −1,30 pts |
| DeepSeek | +0,41 pts (13/07) | 2 de 20 | −1,53 pts |
| Mistral | +0,29 pts (13/07) | 1 de 20 | −3,60 pts |

Des de mitjans de juliol, l'índex va al davant de manera constant.

### Per què no és estrany

1. **És el que diu la literatura financera.** Els informes SPIVA (S&P Dow
   Jones Indices) mostren any rere any que entre el **80 % i el 90 %** dels
   gestors professionals no baten el seu índex de referència a llarg termini.
   Que cinc gestors seguits no el batin en tres mesos no és cap anomalia:
   és el cas majoritari.

2. **Les IAs paguen comissions i l'índex no.** Cada operació costa un 0,1 %.
   L'índex no opera mai: compra el primer dia i no torna a moure's. Aquesta
   diferència de costos és exactament la que estudia el TR.

3. **Tres mesos és molt poc temps.** Amb 13 setmanes de 22, les diferències
   (entre −0,5 i −3,6 punts) estan dins del que el simple atzar pot moure.

**Aquest resultat sosté la hipòtesi central del TR**, no la contradiu.

---

## 3. Les IAs llegeixen les notícies de veritat?

**Sí, i les filtren.** Des que es va afegir el registre obligatori
(`noticies_clau` i `lectura_noticies`):

| IA | Rondes en què cita notícies | Titulars citats de mitjana |
|---|---|---|
| GPT | 4 de 4 | 6,5 |
| Mistral | 4 de 4 | 4,8 |
| Gemini | 4 de 4 | 4,2 |
| Claude | 4 de 4 | 3,8 |
| DeepSeek | 4 de 4 | 3,8 |

### La prova que no les citen a l'atzar

Dels 12 titulars de la setmana 13, mira quines van triar:

| Titular | Quantes IAs el citen |
|---|---|
| Els preus al consum pugen un 0,1 % al juliol | **5 de 5** |
| El trànsit a l'estret d'Ormuz s'atura (tensió EUA-Iran) | **5 de 5** |
| S'esvaeixen les apostes d'una pujada de tipus imminent | 4 de 5 |
| L'economia xinesa es frena al juliol | 4 de 5 |
| El bo japonès a 10 anys, en màxims de tres dècades | 3 de 5 |
| *Bill Ackman reforça aquestes accions* | **0 de 5** |
| *Jefferies rebaixa BSE* | **0 de 5** |
| *Retractable Technologies presenta resultats* | **0 de 5** |
| *Crèdit privat sota pressió* | **0 de 5** |

Les notícies **macroeconòmiques i geopolítiques** les llegeixen totes; les
anecdòtiques o de companyies irrellevants, **cap**. No és lectura mecànica:
hi ha criteri.

### Les fonts són actuals

Comprovació de les 9 fonts: **9 de 9 vives**, i 7 amb notícies del mateix
dia. El motor descarta automàticament qualsevol titular de més de 8 dies i
avisa si una font queda obsoleta (com va passar amb el *Wall Street Journal*
— vegeu el Canvi núm. 2 a CANVI_DE_REGLES.md).

---

## 4. El gràfic es mou cada dia, però les decisions són setmanals

Comprovat:

| Element | Valor |
|---|---|
| Punts al gràfic | **20** |
| Decisions preses | **13** (una per setmana) |
| Dies de mercat amb valoració | 14 de 15 laborables |
| Setmanes amb més d'una ronda | **cap** |

Hi ha dos robots separats i això és intencionat:

- **Ronda setmanal** (dilluns): les IAs decideixen. Una sola vegada per
  setmana, garantit pel propi motor, que rebutja jugar dues rondes la mateixa
  setmana.
- **Preus diaris** (de dilluns a divendres): recalcula què valen les carteres
  amb els preus del dia. **No consulta cap IA**, així que no costa res i no
  altera cap decisió.

Resultat: el gràfic té moviment diari amb només 13 decisions preses.

---

## 5. Què s'ha corregit arran d'aquesta auditoria

**Els dividends.** Yahoo Finance dóna el preu dels actius **sense** comptar
els dividends que reparteixen. En una compte real, aquests diners es cobren.
Sense comptar-los, el torneig infravalorava el resultat de tothom.

Ara el motor els cobra automàticament abans de cada ronda: als comptes de les
IAs entren com a efectiu (i cada IA decideix què en fa), i a l'índex es
reinverteixen comprant més participacions, que és el que fa un fons
acumulatiu.

Efecte mesurat en una simulació de sis mesos:

| Participant | Dividends cobrats | % de la cartera |
|---|---|---|
| Mistral | 85,88 € | 0,87 % |
| Claude | 74,05 € | 0,73 % |
| Gemini | 55,80 € | 0,56 % |
| DeepSeek | 40,08 € | 0,40 % |
| GPT | 37,88 € | 0,37 % |
| S&P 500 | +0,479 % en participacions | 0,48 % |

**Important per al TR:** els dividends no afecten tothom igual. Mistral, que
té Nestlé i fons de dividends, cobra més del doble que GPT. Sense
comptabilitzar-los, el torneig penalitzava injustament les estratègies
basades en dividends.

L'S&P 500 (SPY) paga cada trimestre —març, juny, setembre i desembre—, així
que entre el juliol i l'agost no n'hi va haver cap. Al **setembre i al
desembre sí**, i llavors serà un factor rellevant.

---

## 6. Incident del 24 d'agost al 4 de setembre de 2026

> Aquesta secció s'afegeix el **4 de setembre de 2026**. Durant dues setmanes
> el torneig va anar sol, sense ningú al davant, i és el primer cop que se li
> fa un repàs després d'un període desatès. Va sortir-ne feina.

### Què semblava que passava

Que les rondes dels dilluns 24 i 31 d'agost **no s'havien jugat**: qui entrava
a la web durant el dia no hi veia res nou.

### Què passava de veritat

Les rondes **sí que es van jugar, totes dues, i soles**. Ho diu el registre
d'execucions de GitHub: 12 execucions automàtiques en aquestes dues setmanes,
totes marcades com a correctes i **cap llançada a mà**. Les setmanes 14 i 15
tenen les seves 5 decisions guardades, com totes les altres.

El problema era **l'hora**:

| Dia | Hora prevista | Hora real | Retard |
|---|---|---|---|
| dl 24/08 | 09:37 | 10:22 | 45 min |
| dl 31/08 | 09:37 | **17:22** | **7 h 45 min** |
| dt 01/09 | 10:51 | 15:42 | 4 h 51 min |

El 31 d'agost la ronda no es va jugar fins a un quart de sis de la tarda. Qui
mirés la web al matí, a migdia o després de dinar veia el mateix que la
setmana anterior i concloïa, amb tota la lògica del món, que allò estava
espatllat.

**Per què passa.** Les tasques programades de GitHub són gratuïtes i, a canvi,
no tenen hora garantida: GitHub les posa en una cua i les executa *quan pot*.
La seva pròpia documentació ho diu obertament. Si aquell dia hi ha molta feina
—i el començament de mes n'hi sol haver— la cua s'allarga hores. No és una
avaria; és el tracte que s'accepta en no pagar.

### Els dos problemes de debò

El retard, en si mateix, no fa mal: la ronda s'acaba jugant. El que sí que va
fer mal van ser dues coses que el retard va destapar.

**Problema 1 — Mistral va deixar de participar.**

El 31 d'agost Mistral va respondre amb un error 403, que vol dir *"aquest
model ja no entra al teu pla"*. Mistral havia tret el model que fèiem servir
(`mistral-large-latest`) del compte gratuït. Com que el motor està pensat per
no aturar-se si una IA falla, va anotar "mantenir" per defecte i va continuar.

I aquí ve el que és realment greu: **GitHub va marcar la ronda en verd, com un
èxit.** Havia funcionat tot menys una de les cinc IAs, i no ho deia enlloc.
Sense mirar el CSV a mà, era invisible.

**Problema 2 — el gràfic tenia dies mal posats.**

Aquest és conseqüència directa dels retards, i és el més subtil dels tres.

El robot de preus posava com a data **el dia en què s'executava**. Normalment
corre a les 23:42 (hora d'aquí), amb la borsa ja tancada, i encerta. Però amb
els retards, uns quants robots es van executar **de matinada**:

| El robot corre | Etiqueta que posava | Preus que portava de veritat |
|---|---|---|
| dj 27/08 a les 03:03 | 27/08 | **26/08** (la borsa encara no havia obert) |
| dv 28/08 a les 07:49 | 28/08 | **27/08** |
| ds 29/08 a les 05:22 | 29/08 | **28/08** |
| dt 01/09 a les 02:46 | 01/09 | **31/08** |

La borsa dels EUA obre a les 15:30 d'aquí. Un robot que corre a les tres de la
matinada no pot tenir els preus d'aquell dia, perquè encara no existeixen:
agafa l'últim tancament, que és el del dia abans. Però els guardava amb la
data del dia nou.

Resultat: tota la sèrie va quedar **desplaçada un dia**. Al gràfic hi havia un
**dissabte 29 d'agost amb la borsa tancada** i, en canvi, hi faltava el
**dimecres 26**. I encara una altra: el dimarts 1 de setembre el robot de la
nit va veure que ja hi havia una fila amb aquella data (la de matinada, amb
preus del 31) i es va saltar la feina, així que el tancament real de l'1 de
setembre no es va arribar a guardar mai.

### Què s'ha fet

| Problema | Solució |
|---|---|
| Mistral fora del pla | Canviat a `mistral-medium-latest`, que el compte sí que admet |
| Una IA morta passava desapercebuda | Nou `comprovar_salut.py`: si una IA no respon, surt en gran al resum de GitHub |
| Dates posades pel rellotge | `actualitzar_preus.py` ara data pel **tancament real de Yahoo**, no per l'hora del robot |
| Sèrie desplaçada un dia | `corregir_dates_diaries.py` retorna cada fila al seu dia |
| L'1 de setembre perdut | `recuperar_dia.py` el reconstrueix amb els tancaments reals d'aquell dia |

Sobre la correcció de dates, que és la que toca dades ja guardades: **no
s'inventa cap número**. Cada fila conserva els preus que portava; només se li
posa la data del dia de borsa al qual pertanyen de debò. Quin dia és, no és
opinable: se sap de l'hora exacta en què es va executar cada robot, que GitHub
guarda, i del calendari de la borsa.

L'únic dia realment perdut, l'1 de setembre, s'ha reconstruït amb el mateix
mètode que fa servir aquesta auditoria: les unitats que tenia cada cartera
aquell dia (entre dues rondes no es toquen) pels tancaments reals de Yahoo del
dia 1. La comprovació: el valor de l'índex reconstruït dóna 9.963,04 € i el
càlcul independent fet a part en dóna 9.963,34 € — **3 dècimes d'euro de
diferència sobre 10.000**.

Després de la reparació, la sèrie del 17 d'agost al 3 de setembre té **tots**
els dies de borsa, cap dia de mercat tancat, i cap forat.

### Què no s'ha pogut arreglar des d'aquí

**El compte de Mistral no té quota.** Canviar el model treu l'error 403, però
el compte respon ara amb un altre error dient que té **0 peticions per minut
disponibles**. Això és una qüestió del compte de Mistral —de saldo o de
verificació—, i s'ha de resoldre al seu web. Fins que no es resolgui, Mistral
seguirà sense decidir i el motor li anotarà "mantenir" cada dilluns.

**Els retards de GitHub no es poden evitar.** Són com són. El que s'ha fet és
que deixin de fer mal: hi ha sis intents repartits entre dilluns i dimarts
(amb que n'entri un, la ronda es juga) i, des d'ara, l'hora a la qual
s'executi el robot ja no afecta les dades, perquè la data surt del mercat i no
del rellotge.

### Per al TR

Aquest incident val la pena explicar-lo, i no amagar-lo. És un cas real de
**per què les dades s'han d'auditar encara que tot sembli anar bé**: durant
dotze dies el sistema va donar totes les senyals de funcionar correctament
—execucions en verd, web actualitzada, gràfic ple de punts— mentre arrossegava
una IA morta i una sèrie de dates desplaçada. Cap alarma va saltar. Es va
trobar mirant-ho a mà.

---

## Resum: què és real i què no

### Sí que és realista

- Preus reals de mercat de Yahoo Finance, convertits a euros amb el canvi del dia.
- Comissió del 0,1 % per operació (comparable a un broker en línia).
- Límits de concentració (20 % per acció, 40 % per fons).
- Dividends cobrats.
- Totes les IAs reben la mateixa informació el mateix dia.

### Limitacions que queden (i que cal esmentar al TR)

| Limitació | Efecte |
|---|---|
| No es compta la diferència entre preu de compra i de venda (*spread*) | Molt petit en ETFs i accions grans (0,01-0,05 %) |
| Es fan servir preus de tancament, no el preu exacte del moment de l'ordre | Diferències de dècimes |
| Es permeten fraccions d'accions | Realista: molts brokers ja ho permeten |
| No es descompten impostos sobre dividends | Un inversor real pagaria retenció |
| Les setmanes 1-7 arrosseguen l'antiga comptabilitat en dòlars, reescalada | Documentat al Canvi núm. 5 |
| Mistral no va decidir la setmana 15 (el seu proveïdor va tallar-li l'accés) | Se li va anotar "mantenir"; vegeu la secció 6 |
| Quatre dies del gràfic de finals d'agost porten el tipus de canvi de la matinada, no el del tancament | Diferència d'una dècima; els preus de borsa sí que són del dia correcte |

**Conclusió:** els números són reals i verificables. Si algú hagués fet
aquestes mateixes operacions en un compte real, tindria pràcticament el
mateix, amb diferències de dècimes atribuïbles al moment exacte d'execució i
a la fiscalitat dels dividends.

---

*Aquesta auditoria es pot repetir en qualsevol moment. Els scripts de
verificació estan a la carpeta de treball i tots els CSV del torneig són
públics al repositori.*
