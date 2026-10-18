# Regular 1.240 — integrazione di L, A, M, N, R, S

16 ottobre 2026. La candidata integra **L B, A B, M B, N A, R B, S B**,
scelte dopo il confronto con la 1.230. La lista esplicita della revisione
umana prevale sul precedente suggerimento S A: la forma adottata è **S B**.

Il TTF [Leonardus-1240-Regular.ttf](../fonts/Leonardus-1240-Regular.ttf)
usa la famiglia **Leonardus 1240**, stile Regular. La
[ricevuta della scelta](../data/human_capitals_integration_review_2026-10-16.json)
vincola i sei SVG mostrati e la tavola comparativa; il
[manifesto 1.240](../glyphs/regular/release-1.240.json) li collega alla build.
Lo [studio preparatorio](CAPITALS_VARIANT_STUDY.md) conserva il proprio ambito.

| Lettera | Scelta | Disegno adottato |
|---|---|---|
| L | B | Piccola asola superiore e piede mobile. |
| A | B | Fianco obliquo, traversa inclinata e ritorno destro. |
| M | B | Spalle curve diseguali e raccordo corsivo. |
| N | A | Diagonale curva e attacco sobrio. |
| R | B | Occhiello obliquo e ritorno della gamba. |
| S | B | Testa raccolta, vita verticale e arco inferiore più largo. |

I sei contorni coincidono con i sorgenti scelti; nessun ridisegno silenzioso.
À segue la nuova A e il suo accento progettato è riposizionato; le ancore
combinanti seguono le nuove basi. **Tutte le minuscole, gli altri contorni e
tutti gli avanzamenti sono conservati.** Resta il bianco bbox p–q di 115 unità.
I checkpoint 1.000, 1.100, 1.200, 1.210, 1.211, 1.220 e 1.230 restano invariati.

## Ambito storico

Le sei maiuscole restano **disegni contemporanei**, classificati `designed`:
le sette osservazioni formali di caso irrisolto e i quattro confronti con
minuscole non diventano attestazioni di maiuscole storiche. In particolare,
occhiello e gamba di R e diagonale di N sono costruzioni moderne dichiarate.
La scelta approva il disegno, l'integrazione e l'installazione; non introduce
nuove letture, segmentazioni, conferme di caso o foliazione, autenticità,
approvazioni degli altri caratteri o della pubblicazione.

Il registro conserva **144 campioni, 101 revisionati e 43 candidati**.
Restano venti minuscole con riferimenti revisionati e sei completamenti
ragionati; le 61 segmentazioni consolidate non cambiano. Il
[CSV per glifo](DERIVAZIONE_1_240.csv) distingue confronti contestuali,
campioni revisionati e scelte progettuali senza promuovere le minuscole al caso
maiuscolo.

## Spaziatura e prove

Il [confronto con la 1.230](../specimen/Capitals-Integration-1.240.png) comprende
Leonardo, Lucca, Acqua, Arte, Arno, Milano, Macchine, Natura, Navigli, Roma,
Ruote, Studio e Scienza; inoltre frasi, titoli, doppie e successioni
La/Le/Li/Lo/Lu, Na/No, Sc/St, Ra/Ro. Le prove a 12, 18, 36 e 72 pt a 96 DPI
sono renderizzate dal TTF con HarfBuzz e FreeType, senza fallback. La verifica
visiva non richiede nuove metriche o kerning specifico nella combinazione scelta.

| Lettera | Avanzamento | Margine sinistro | Margine destro |
|---|---:|---:|---:|
| L | 445 | 70 | 43 |
| A | 570 | 53 | 60 |
| M | 760 | 55 | 79 |
| N | 610 | 60 | 31 |
| R | 585 | 61 | 52 |
| S | 565 | 70 | 39 |

Sono bounding box in unità su 1000, non misure ottiche su ogni rigo.
La piccola asola di L perde dettaglio ai corpi bassi; il disegno scelto è
conservato. Le 2.704 coppie delle 52 lettere a 16/24/48/96/128 px/em e soglia
127 non hanno collisioni d'inchiostro. Il risultato non certifica tutta la
spaziatura ottica, tutti i corpi o la lettura umana.

Audit e repertorio verificano **119 codepoint e 121 glifi**. I test controllano
build identiche, corrispondenza ai sei SVG, isolamento dei cambiamenti alla
dipendenza À, conservazione degli avanzamenti e delle minuscole, accenti
NFC/NFD e rifiuto di scelte o classificazioni alterate. Gli esiti sono nel
[rapporto QA](QA_1_240.json).

## Installazione e riproduzione

La versione è installata nell'account Windows corrente come **Leonardus 1240**,
Regular. I byte selezionati da GDI coincidono con il TTF, anche in un processo
nuovo. La 1.230 resta registrata e disponibile; file e registrazione precedenti
non sono modificati. Prove native Office 1.240 e stampa fisica non sono dichiarate.

Aprire la [pagina di prova 1.240](../specimen/Leonardus-1240-Trial.html), con
testo libero, alfabeto e confronto con la 1.230.

SHA256: `e6f340ff1f83fc37ecfa036b2180b621411e13ed8bd02b2aad93dd335d650d47`.

```powershell
python -m leonardus.cli build-release --version 1.240 --out build/Leonardus-1240-Regular.ttf
python -m leonardus.cli audit --font build/Leonardus-1240-Regular.ttf
python -m leonardus.cli charset --font build/Leonardus-1240-Regular.ttf
python examples/regular_spacing_check.py --font build/Leonardus-1240-Regular.ttf --ppem 128 --out build/pairs-1240.json
python examples/regular_specimen.py --font build/Leonardus-1240-Regular.ttf --out build/proof-1240 --candidate
python examples/capitals_selection_proof.py --out build/capitals-selection.png
```

Contorni originali: OFL 1.1. Nessuna riproduzione di manoscritto incorporata.
