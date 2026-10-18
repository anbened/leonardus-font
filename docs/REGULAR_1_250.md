# Regular 1.250 — integrazione di C, D, E, G, P, T

16 ottobre 2026. La candidata integra **C B, D B, E A, G B, P B, T B**.
Le scelte esplicite E A, G B e P B prevalgono sui precedenti suggerimenti
E B, G A e P A. Il TTF è [Leonardus-1250-Regular.ttf](../fonts/Leonardus-1250-Regular.ttf),
famiglia **Leonardus 1250**, stile Regular.

La [ricevuta della scelta](../data/human_cdegpt_integration_review_2026-10-16.json)
conserva la citazione e vincola i sei SVG e la tavola mostrata. Il
[manifesto 1.250](../glyphs/regular/release-1.250.json) li collega alla build
da 1.240. Lo [studio preparatorio](CDEGPT_VARIANT_STUDY.md) resta il checkpoint
di confronto; non riceve nuove approvazioni delle letture storiche.

| Lettera | Scelta | Disegno adottato |
|---|---|---|
| C | B | Corpo obliquo e ritorno inferiore marcato. |
| D | B | Asta curva e occhiello obliquo. |
| E | A | Tre terminali leggibili e asta lievemente curva. |
| G | B | Ritorno interno a spirale. |
| P | B | Occhiello obliquo e piccolo ritorno al piede. |
| T | B | Traversa arcuata e ritorno al piede. |

Sono i sei contorni esatti scelti, senza ridisegni successivi. **È ed É**
seguono E A: gli accenti progettati sono riallineati e le ancore combinanti
ricalcolate. Tutte le minuscole, L B/A B/M B/N A/R B/S B della 1.240, gli
altri contorni e tutti gli avanzamenti sono conservati. Il bianco bbox p–q
resta 115 unità. Tutti i checkpoint precedenti mantengono gli stessi byte.

## Ambito storico

Le sei maiuscole restano classificate **`designed`**, anche dopo la selezione.
Le quattro osservazioni formali di caso irrisolto e gli otto confronti con
minuscole non diventano nuove letture maiuscole confermate. La E del campione
non fornisce gli accenti È/É; G e C sono confrontate soprattutto con minuscole.
Altezza, peso, proporzioni e raccordi leggibili restano scelte contemporanee.

La selezione riguarda il disegno nel flusso di integrazione e installazione;
non conferma letture, segmentazioni, caso, foliazione, autenticità, altri
caratteri o pubblicazione. Il registro mantiene **144 campioni: 101 revisionati
e 43 candidati**, venti minuscole con letture revisionate e sei completamenti
ragionati; le 61 segmentazioni non cambiano. Il
[CSV per glifo](DERIVAZIONE_1_250.csv) aggiorna soltanto i sei sorgenti e i due
compositi dipendenti, conservando la distinzione fra evidenza e progetto.

## Spaziatura e verifica

Il [confronto con la 1.240](../specimen/CDEGPT-Integration-1.250.png) comprende
Codice, Carta, Disegno, Duca, Esperienza, Europa, Genio, Geometria, Pittura,
Progetto, Tempo e Toscana; inoltre frasi, titoli, doppie, accenti NFC/NFD e
Ca/Co, Di/Do, Es/Eu, Ge/Gi, Pi/Pr, Te/To. Prove a 12/18/36/72 pt e 96 DPI,
renderizzate con HarfBuzz e FreeType senza fallback. La verifica visiva non
richiede nuovi avanzamenti o kerning specifico per la combinazione scelta.

| Lettera | Avanzamento | Margine sinistro | Margine destro |
|---|---:|---:|---:|
| C | 600 | 56 | 38 |
| D | 610 | 56 | 54 |
| E | 520 | 62 | 28 |
| G | 625 | 44 | 45 |
| P | 545 | 56 | 20 |
| T | 550 | 65 | 24 |

Sono bounding box in unità su 1000, non distanze ottiche su ogni rigo.
Il ritorno di G B può avvicinarsi alla cifra 6 ai corpi piccoli: la forma
scelta è conservata e confrontata nelle parole. Le 2.704 coppie delle 52
lettere a 16/24/48/96/128 px/em, soglia 127, non hanno collisioni d'inchiostro.
Il controllo non certifica la spaziatura ottica a ogni corpo o la lettura umana.

Audit e repertorio verificano **119 codepoint e 121 glifi**. I test controllano
build identiche, contorni esatti, conservazione delle forme precedenti e degli
avanzamenti, accenti, corrispondenza del CSV ai compositi e rifiuto di selezioni
o classificazioni alterate. Esiti nel [rapporto QA](QA_1_250.json).

## Installazione e riproduzione

Installata nell'account Windows corrente come **Leonardus 1250**, Regular.
La selezione GDI restituisce gli stessi byte del TTF, anche in un processo
nuovo. File e registrazione della 1.240 restano invariati. Prove native Office
1.250 e stampa fisica non sono dichiarate.

La [pagina di prova 1.250](../specimen/Leonardus-1250-Trial.html) offre testo
libero, alfabeto e confronto con la 1.240.

SHA256: `6e383ce0792149a50023ac73e5d7f33105534db07004bd88bceac491cc6d2ffb`.

```powershell
python -m leonardus.cli build-release --version 1.250 --out build/Leonardus-1250-Regular.ttf
python -m leonardus.cli audit --font build/Leonardus-1250-Regular.ttf
python -m leonardus.cli charset --font build/Leonardus-1250-Regular.ttf
python examples/regular_spacing_check.py --font build/Leonardus-1250-Regular.ttf --ppem 128 --out build/pairs-1250.json
python examples/regular_specimen.py --font build/Leonardus-1250-Regular.ttf --out build/proof-1250 --candidate
python examples/cdegpt_selection_proof.py --out build/cdegpt-selection.png
```

Contorni originali OFL 1.1; nessuna riproduzione di manoscritto incorporata.
