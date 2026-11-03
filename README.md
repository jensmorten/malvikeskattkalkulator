Kildekode for eigedomsskattekalkulator for Malvik kommune:

https://malvikeskattkalkulator.streamlit.app/


Dette er ein enkel kalkulator som reknar ut konsekvensen av å endre eigedomsskatten i Malvik kommune, både for kommunebudsjettet og huseigarar. Eksperimenter med promillesats og botnfrådrag og sjå konsekvensen.

Kalkulatoren bruker data henta frå offentleg ettersyn, eiendomsskatt 2026 i Malvik. All data som er brukt ligg opent tilgjengeleg på nett.

Moglege feilkjelder: data er henta inn frå eit PDF-dokument og konvertert til tabellformat og sjølv om manuell kontroll av data er utført kan slik metode gi enkelte feil. Eigedomar med delvis fritak er tekne med slik dei står i skattelista.

Utrekninga per rad er `floor(max(takst × skattenivå − botnfrådrag × boeiningar, 0) × promille / 1000)`, der talet på boeiningar er Bunnfradrag i lista delt på 320 000. Med vedtatte satsar for 2026 (1.8‰ bolig, 4.0‰ næring, botnfrådrag 320 000) gir formelen nøyaktig skatten i lista for alle 6 498 radene, 35 165 094 kr totalt.

Ta gjerne kontakt med jens.morten.nilsen@gmail.com for spørsmål eller kommentarar.

Utviklaren er kommunestyrerepresentant for Raudt i Malvik men vil understreke at kalkulatoren kan brukast av alle, og den reknar like bra utansett som skatten går opp eller ned.

Validering av kalkulatoren ved sammenligning med<a href="https://pub.framsikt.net/2026/malvik/bm-2026-hop_2026_2029#/generic/summary/introduction/ab2c2b22-5314-4136-90c7-3d4fd3e39a93-cn">  kommunediretørens beregning: </a>


|                          | test 1 | test 2 | test 3 | test 4 | test 5 | test 6 |
|--------------------------|-----|-----|-----|-----|-----|-----|
| **Promillesats bolig**   | 1.4 | 1.8 | 1.9 | 2.9 | 3.9 | 4 |
| **Promillesats næring**  | 4 | 4 | 4 | 5 | 6 | 7 |
| **Kalkulatoens berekning (mill kr)**           | 28.8 | 35.2 | 36.8 | 54.3 | 71.8 | 75.0 |
| **Kommunedirektørens berekning (mll kr)** | 29.7 | 35.8 | 37.4 | 55 | 74.2 | 77.7 |
| **Differanse (mill kr)**           | 0.9 | 0.6 | 0.6 | 0.7 | 2.4 | 2.7 |
| **Relative differanse**  | 3.1% | 1.8% | 1.8% | 1.4% | 3.4% | 3.6% |

Kalkulatoren reknar no utan korreksjonskonstant (tidlegare 1.033) og gir same total som skattelista ved vedtatte satsar. Kommunedirektørens tal for vedtatt nivå (35.8 mill. kr) er 0.6 mill. kr høgare enn summen av skattelista (35.17 mill. kr), så skilnaden kjem frå grunnlaget i budsjettet og ikkje frå utrekninga per eigedom. Brukaren må sjølv ta stilling til om avviket er akseptabelt for aktuell bruk. 

Validering av effekten av bunnfradrag er utført med  <a href="https://pub.framsikt.net/2025/malvik/bm-2025-handlings-_og_%C3%B8konomiplan_2025-2028#/generic/summary/introduction/ead26f38-ec6f-44b7-b320-bececd7a43de-cn"> svar på spørsmål i 2025</a>:

| Bunnfradrag  (1.9 promille på bolig, 4 promille næring)       | Differanse, kommunedirektørens berekning | Differanse, kalkulator |
|---------------------|----------------|-------------------------|
| Ingen               | +1,7           | +1,8                    |
| 100 000             | +0,9           | +0,9                    |
| 200 000             | 0              | 0                       |
| 300 000             | −0,9           | −0,9                    |
| 400 000             | −1,8           | −1,8                    |
| 500 000             | −2,6           | −2,7                    |
