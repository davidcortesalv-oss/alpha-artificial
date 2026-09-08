# Es comporten les IAs com inversors humans?

> **Anàlisi conductual del torneig ALPHA ARTIFICIAL**
> Tancat el **8 de setembre de 2026**, amb **16 setmanes jugades de 22**.
>
> Aquest document respon la **segona pregunta d'investigació** del TR: si les
> intel·ligències artificials, quan decideixen on posar els diners, cauen en
> els mateixos biaixos que l'economia conductual ha documentat en les persones
> —excés de confiança, sobreoperació, pànic davant les pèrdues.
>
> La primera pregunta (*bat alguna IA el mercat?*) es respon a la secció 1.
> La verificació que els números són reals és a **AUDITORIA.md**.

---

## Nota metodològica (llegir abans de les taules)

Totes les xifres surten de `dades/decisions.csv`, `dades/canvis.csv` i
`dades/comissions.csv`, que són públics al repositori.

**S'han exclòs 6 rondes** en què una IA no va poder respondre perquè l'API del
seu proveïdor estava caiguda o va tallar la resposta. No van ser decisions de
mantenir la cartera: van ser avaries. Comptar-les com si la IA hagués triat
quedar-se quieta inflaria artificialment la seva paciència i li rebaixaria la
confiança mitjana. Queden visibles a l'historial, però fora d'aquestes
mètriques.

Queden, doncs, **74 decisions vàlides** de 80.

Per mesurar si una setmana va anar bé o malament es fa servir el rendiment
setmanal que calcula el propi motor (`rend_setmana`), no la diferència entre
els valors de cartera de dues decisions consecutives. Són coses distintes: la
segona barreja el moviment del mercat amb el moment exacte en què es va
executar la ronda, i dona resultats enganyosos.

---

## 1. On som: ningú no bat l'índex

| | Participant | Cartera | Rendiment |
|---|---|---|---|
| 🥇 | **S&P 500** (gestió passiva) | 10.064 € | **+0,64 %** |
| 🥈 | GPT | 10.034 € | +0,34 % |
| 🥉 | Claude | 9.965 € | −0,35 % |
| 4t | DeepSeek | 9.865 € | −1,35 % |
| 5è | Mistral | 9.814 € | −1,86 % |
| 6è | Gemini | 9.814 € | −1,86 % |

**Cap de les cinc IAs va per davant de l'índex, i només una està en positiu.**

I no és que l'índex guanyi assumint més risc: en guanya assumint-ne **menys**.

| Participant | Volatilitat | Pitjor caiguda | Ràtio de Sharpe |
|---|---|---|---|
| **S&P 500** | 11,2 | **−3,2 %** | **+0,48** |
| GPT | 16,1 | −5,5 % | +0,33 |
| Claude | 10,8 | −4,1 % | −0,08 |
| DeepSeek | 12,2 | −4,1 % | −0,67 |
| Gemini | 11,4 | −3,7 % | −1,06 |
| Mistral | 9,3 | −4,2 % | −1,29 |

> La **ràtio de Sharpe** mesura quanta rendibilitat s'obté per cada unitat de
> risc assumit. Com més alta, millor. L'índex té la millor de totes i la
> caiguda més suau: guanya més i pateix menys.

**Això no és una anomalia.** Els informes SPIVA d'S&P Dow Jones Indices
mostren any rere any que entre el 80 % i el 90 % dels gestors professionals no
baten el seu índex de referència. Que cinc gestors seguits no ho aconsegueixin
en setze setmanes és el resultat majoritari, no l'excepció.

---

## 2. El resultat principal: com més segures, pitjor ho fan

Aquesta és la troballa més sòlida de tot el treball.

Cada setmana, cada IA ha de declarar del **1 al 10** com de segura està de la
seva decisió. Si es posen en ordre de confiança i al costat s'hi posa el que
han guanyat, surt això:

| IA | Confiança mitjana | Rendiment |
|---|---|---|
| Mistral | **7,1** | −1,86 % |
| Gemini | 6,7 | −1,86 % |
| DeepSeek | 6,3 | −1,35 % |
| Claude | 5,9 | −0,35 % |
| GPT | **5,6** | **+0,34 %** |

L'ordre és **exactament l'invers**. La correlació entre confiança i rendiment
és de **−0,94**, gairebé una línia recta descendent: com més segura es declara
una IA, pitjor acaba.

I hi ha una segona baula que tanca el cercle:

| Relació | Correlació |
|---|---|
| Confiança ↔ rendiment | **−0,94** |
| Confiança ↔ operar més | **+0,77** |
| Operar més ↔ rendiment | −0,58 |

Es llegeix així: **més confiança porta a operar més, i operar més porta a
guanyar menys.** És literalment la cadena que Barber i Odean van documentar en
inversors humans a *«Trading Is Hazardous to Your Wealth»* (2000), on van
demostrar que els inversors particulars més actius eren precisament els que
menys guanyaven, i que la causa era l'excés de confiança.

**Que aparegui igual en màquines és el resultat central d'aquest TR.**

> ⚠️ **Honestedat estadística:** aquestes correlacions s'han calculat amb
> **cinc punts** (una per IA). Amb tan poques observacions, un sol cas
> desplaçat canviaria el número. Són **indicatives, no significatives**. El que
> les fa interessants no és la xifra, sinó que apunten en la mateixa direcció
> que la literatura i que la relació sigui monòtona: no hi ha ni una sola IA
> que trenqui l'ordre.

---

## 3. Sobreoperació: Mistral no s'ha aturat ni una setmana

| IA | Setmanes que reajusta | Volum mogut | Comissions pagades |
|---|---|---|---|
| Mistral | **14 de 14 (100 %)** | 1,9 × la cartera | 15,72 € |
| Gemini | 11 de 15 (73 %) | **2,2 × la cartera** | 19,50 € |
| GPT | 10 de 16 (62 %) | 1,0 × la cartera | 16,00 € |
| DeepSeek | 8 de 15 (53 %) | 1,3 × la cartera | **25,26 €** |
| Claude | **3 de 14 (21 %)** | 0,4 × la cartera | 7,06 € |

**Mistral no ha decidit mantenir ni una sola vegada.** Cada setmana, sense
excepció, ha trobat un motiu per moure la cartera. Gemini ha arribat a moure
més del doble del que té.

A l'altre extrem, Claude ha tocat la cartera **3 vegades en 14 setmanes** i ha
pagat menys d'un terç de comissions que DeepSeek.

**Matís important i honest:** la relació entre operar i perdre **no és neta**
en aquestes dades. GPT opera bastant (62 %) i és la que millor ho fa. La
correlació és de −0,58, prou fluixa. El que sí que és contundent és la
confiança. Al TR convé dir-ho així i no forçar la conclusió.

---

## 4. Compren el rival: totes tenen l'índex a la cartera

Aquest és el comportament més revelador i el menys esperat.

**Les cinc IAs tenen S&P 500 (SPY) a la cartera** — el mateix índex que han de
batre. Si s'hi sumen els altres fons d'índex ampli:

| IA | En índexs amplis | Composició |
|---|---|---|
| DeepSeek | **57,6 %** | SPY 37,0 % + QQQ 20,6 % |
| Claude | 38,5 % | SPY 20,2 % + QQQ 18,3 % |
| GPT | 33,9 % | QQQ 18,2 % + SPY 15,7 % |
| Gemini | 26,4 % | SPY 14,2 % + VTI 12,2 % |
| Mistral | 19,0 % | SPY 19,0 % |

**DeepSeek té gairebé el 60 % dels diners en el seu propi rival.** Amb aquesta
cartera no el pot batre: la meitat del que té ÉS l'índex, i a sobre paga
comissions per tenir-lo mentre que l'índex no en paga cap.

Això té nom en el món de la gestió de fons: ***closet indexing***, o
indexació encoberta. El gestor que té por de quedar malament davant del seu
índex de referència acaba comprant-lo, cosa que li garanteix no quedar-ne
gaire lluny... però també **no superar-lo mai**, perquè els costos hi juguen
en contra. Cremers i Petajisto ho van quantificar el 2009 amb el concepte
d'*active share*.

És, en el fons, **aversió a la pèrdua aplicada a la reputació**: val més no
equivocar-se gaire que encertar-la molt.

---

## 5. Fugen de les empreses concretes

El torneig els ofereix **114 accions d'empreses reals** (Nvidia, Inditex,
Ferrari, Nestlé, Grifols, Cellnex...) i **108 fons cotitzats**. Podrien triar
el que volguessin. Trien fons:

| IA | En fons (ETFs) | En accions concretes |
|---|---|---|
| Claude | **100 %** | **0 %** |
| GPT | 92 % | 8 % |
| Gemini | 88 % | 12 % |
| Mistral | 87 % | 13 % |
| DeepSeek | 86 % | 14 % |

**Claude no té ni una sola acció individual.** Cap de les cinc passa del 14 %.

Encaixa amb l'**aversió a l'ambigüetat** (la paradoxa d'Ellsberg): davant
d'una opció concreta i incerta —aquesta empresa en particular pot ensorrar-se
per una notícia dolenta— i una de genèrica i difusa —un fons de 500 empreses—,
es tria sistemàticament la segona, encara que no hi hagi cap regla que ho
obligui.

També es pot llegir com a **prudència raonable**: diversificar és el consell
estàndard. La diferència és que aquí ningú no els ha demanat prudència, i
totes cinc hi han anat igualment.

---

## 6. No hi ha pànic: hi ha eufòria

Aquí esperàvem trobar el biaix més típic —moure fitxa nerviosament després de
perdre diners— i les dades diuen **just el contrari**.

| IA | Reajusta després de PERDRE | Reajusta després de GUANYAR |
|---|---|---|
| Mistral | 8 de 8 (100 %) | 5 de 5 (100 %) |
| Gemini | **6 de 8 (75 %)** | 4 de 6 (67 %) |
| GPT | 3 de 7 (43 %) | **6 de 8 (75 %)** |
| DeepSeek | 2 de 6 (33 %) | **6 de 8 (75 %)** |
| Claude | 1 de 7 (14 %) | 2 de 6 (33 %) |
| **TOTAL** | **20 de 36 (56 %)** | **23 de 33 (70 %)** |

> *Nota:* la fila TOTAL ajunta totes les decisions de les cinc IAs (20 de 36).
> La web, a la pestanya Biaixos, fa la mitjana dels cinc percentatges per
> separat i li surt 53,1 %. Les dues xifres són correctes: mesuren coses
> lleugerament diferents (una pondera per nombre de decisions i l'altra dona
> el mateix pes a cada IA). La conclusió no canvia.

Després d'una setmana en verd reajusten el **70 %** de les vegades; després
d'una en vermell, només el **56 %**. **Toquen més la cartera quan els va bé
que quan els va malament.**

GPT i DeepSeek són els casos més marcats: passen del 33-43 % després de perdre
al 75 % després de guanyar. L'única que encaixa amb el patró de pànic és
**Gemini** (75 % vs 67 %), i per poc.

Es pot llegir de dues maneres, i totes dues són interessants per al TR:

- Com a **eufòria**: una bona setmana s'interpreta com a confirmació que la
  lectura del mercat és bona, i això anima a fer més moviments.
- Com a **efecte disposició** (Shefrin i Statman, 1985): quan hi ha guanys es
  toca la cartera per realitzar-los; quan hi ha pèrdues s'espera «a veure si
  recupera».

> ⚠️ **Compte amb aquesta xifra.** Depèn molt de com es defineixi «setmana
> dolenta». Aquí es fa servir el rendiment setmanal que calcula el motor. Si
> en comptes d'això es compara el valor de la cartera entre dues decisions
> consecutives —que barreja el mercat amb l'hora d'execució de la ronda— el
> resultat **s'inverteix**. És un bon exemple, per al TR, de com la manera de
> mesurar pot canviar la conclusió: convé dir sempre quina s'ha fet servir.

### El que sí que no fan: recalibrar-se

| IA | Confiança després de PERDRE | Confiança després de GUANYAR |
|---|---|---|
| Mistral | **7,4** | 6,8 |
| DeepSeek | **6,5** | 6,1 |
| Gemini | 6,8 | 7,0 |
| Claude | 5,7 | 6,0 |
| GPT | 5,6 | 5,6 |

**Mistral i DeepSeek pugen la confiança després de perdre diners.** Mistral
passa de 6,8 a 7,4: com pitjor li ha anat la setmana, més segura es declara la
següent. GPT no es mou gens. Només Claude i Gemini la baixen una mica, que és
el que faria algú que aprèn de l'error.

I no és casualitat que les dues que pugen la confiança quan perden siguin
també **les dues que pitjor ho fan** del grup (Mistral −1,86 %, DeepSeek
−1,35 %).

Aquesta és una forma d'excés de confiança especialment humana: no és només
declarar-se segur, és **no actualitzar-se quan la realitat et contradiu**.
Kahneman ho descriu a *Pensar ràpid, pensar a poc a poc* (2011): la confiança
subjectiva neix de la coherència del relat que ens expliquem, no de la seva
exactitud, i per això sobreviu a l'evidència en contra.

---

## 7. Diuen una cosa i en fan una altra

Cada setmana declaren també el seu **nivell de risc**. Gairebé totes diuen
sempre el mateix:

| IA | Risc declarat | Volatilitat real |
|---|---|---|
| GPT | «moderat» 16 de 16 | **16,1** (la més alta) |
| Claude | «moderat» 14 de 14 | 10,8 |
| Mistral | «moderat» 14 de 14 | **9,3** (la més baixa) |
| Gemini | «moderat» 13, «agressiu» 2 | 11,4 |
| DeepSeek | «moderat» 13, «agressiu» 1, «conservador» 1 | 12,2 |

**Totes es declaren «moderades», i la volatilitat real va del 9,3 al 16,1.**
GPT es diu moderada i és, de fet, la més arriscada de les cinc: gairebé el
doble que Mistral, que es descriu exactament igual.

L'etiqueta, doncs, **no informa de res**. És una autodescripció que no es
correspon amb el comportament — un altre paral·lelisme incòmode amb els
inversors humans, que solen definir-se com a prudents amb independència del
que després fan.

---

## 8. Resum: quins biaixos apareixen i quins no

| Biaix | Apareix? | Evidència |
|---|---|---|
| **Excés de confiança** | ✅ Molt clar | Correlació −0,94 entre confiança i rendiment |
| **Manca de recalibració** | ✅ Clar | Mistral i DeepSeek pugen la confiança després de perdre |
| **Indexació encoberta** | ✅ Molt clar | Les 5 tenen SPY; DeepSeek, 57,6 % en índexs |
| **Aversió a l'ambigüitat** | ✅ Clar | 86-100 % en fons havent-hi 114 accions |
| **Autodescripció inexacta** | ✅ Clar | Totes «moderades», volatilitat de 9,3 a 16,1 |
| **Sobreoperació** | ⚠️ Parcial | Mistral 100 %, però GPT opera i guanya |
| **Efecte ramat** | ⚠️ Parcial | Coincideixen en SPY, GLD i SMH, però les carteres divergeixen molt |
| **Pànic davant pèrdues** | ❌ **No apareix** | Reajusten més després de guanyar (70 %) que de perdre (56 %) |

---

## 9. Límits d'aquesta anàlisi

Cal dir-ho al TR, i dir-ho abans que ho digui ningú altre:

- **Setze setmanes són poc temps.** Les diferències van de dècimes a 2,5
  punts, dins del que el simple atzar pot moure en tres mesos.
- **Cinc subjectes són pocs.** Qualsevol correlació calculada amb cinc punts
  és fràgil per definició.
- **Mistral porta dues setmanes sense decidir** per un problema del seu
  proveïdor (vegeu el Canvi núm. 7): les seves últimes dues rondes són
  «mantenir» forçat, no una decisió seva.
- **No sabem *per què* decideixen el que decideixen.** Tenim les seves
  justificacions escrites, però una justificació no és una explicació del
  procés intern. Es descriu el comportament, no el mecanisme.
- **Les IAs no tenen diners de veritat.** Tot el que s'anomena aquí «por» o
  «confiança» és una analogia amb el comportament humà, no una afirmació sobre
  el que senten. **No senten res.** El que és rellevant és que el patró de
  decisions és indistingible del que produeixen aquests biaixos en persones.

---

## 10. La conclusió que sosté el TR

Les cinc IAs han rebut cada setmana **exactament la mateixa informació**: els
mateixos preus, els mateixos titulars, el mateix moment. Cap avantatge per a
ningú. I tot i així:

1. **Cap no ha superat una estratègia que no fa res** —comprar l'índex el
   primer dia i no tornar-lo a tocar.
2. **Totes han acabat comprant, en part, aquest mateix índex.**
3. **La que es declarava més segura és la que pitjor ho ha fet**, i la que
   menys segura es declarava, la millor.

La resposta provisional a la pregunta del TR és, doncs, que **una IA no bat el
mercat pel simple fet de ser una IA**, i que en intentar-ho reprodueix uns
patrons de decisió que fins ara consideràvem defectes ben humans.

Falten sis setmanes. Res del que hi ha aquí és definitiu.

---

*Document generat el 08/09/2026 a partir de les dades públiques del
repositori. Es pot regenerar en qualsevol moment. Vegeu també AUDITORIA.md
(són reals aquests números?) i CANVI_DE_REGLES.md (què s'ha canviat i per què).*

### Referències

- Barber, B. i Odean, T. (2000). *Trading Is Hazardous to Your Wealth*. The Journal of Finance.
- Cremers, M. i Petajisto, A. (2009). *How Active Is Your Fund Manager?* Review of Financial Studies.
- Kahneman, D. (2011). *Thinking, Fast and Slow*.
- Shefrin, H. i Statman, M. (1985). *The Disposition to Sell Winners Too Early and Ride Losers Too Long*. The Journal of Finance.
- S&P Dow Jones Indices. *SPIVA Scorecards* (informes periòdics).
