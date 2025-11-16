Kildekode for eigedomsskattekalkulator for Malvik kommune:

https://malvikeskattkalkulator.streamlit.app/


Dette er ein enkel kalkulator som reknar ut konsekvensen av å endre eigedomsskatten i Malvik kommune, både for kommunebudsjettet og huseigarar. Eksperimenter med promillesats og botnfrådrag og sjå konsekvensen.

Kalkulatoren bruker data henta frå offentleg ettersyn, eiendomsskatt 2025 i Malvik. All data som er brukt ligg opent tilgjengeleg på nett.

Moglege feilkjelder: data er henta inn frå eit PDF-dokument og konvertert til tabellformat og sjølv om manuell kontroll av data er utført kan slik metode gi enkelte feil. Vidare tar den forenkla kalkulatoren ikkje omsyn til "delvis fritak" for eigedomsskatt.

Ta gjerne kontakt med jens.morten.nilsen@gmail.com for spørsmål eller kommentarar.

Utviklaren er kommunestyrerepresentant for Raudt i Malvik men vil undertreke at kalkulatoren kan brukast av alle, og den reknar like bra utansett som skatten går opp eller ned.

Validering av kalkulatoren ved sammenligning med<a href="https://pub.framsikt.net/2026/malvik/bm-2026-hop_2026_2029#/generic/summary/introduction/ab2c2b22-5314-4136-90c7-3d4fd3e39a93-cn">  kommunediretørens beregning: </a>


|                          | test 1 | test 2 | test 3 | test 4 | test 5 | test 6 |
|--------------------------|-----|-----|-----|-----|-----|-----|
| **Promillesats bolig**   | 1.4 | 1.8 | 1.9 | 2.9 | 3.9 | 4 |
| **Promillesats næring**  | 4 | 4 | 4 | 5 | 6 | 7 |
| **Kalkulatoens berekning (mill kr)**           | 29.3 | 35.8 | 37.5 | 55.5 | 73.5 | 76.7 |
| **Kommunedirektørens berekning (mll kr)** | 29.7 | 35.8 | 37.4 | 55 | 74.2 | 77.7 |
| **Differanse (mill kr)**           | 0.4 | 0 | -0.1 | -0.5 | 0.7 | 1 |
| **Relative differanse**  | 1.3% | 0.0% |-0.3%| -0.9%| 0.9% | 1.3% |  


Som ein skan sjå er den relative diffeansel for disse punkt-sjekkene mellom -0.3% og 1.3%, årsaka er truleg punkt som er diskutert over under "moglege feilkjelder". Brukaren må sjølv ta stilling til om avviket er akseptabelt for aktuell bruk. 
