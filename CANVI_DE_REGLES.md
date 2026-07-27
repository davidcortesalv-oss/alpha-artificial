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
