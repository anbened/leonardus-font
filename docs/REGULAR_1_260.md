# Regular 1.260 — integrazione di B, F, H, I, O, Q

16 ottobre 2026. La candidata integra **B B, F B, H B, I A, O B, Q B**.
**H B è la scelta esplicita** e prevale sul suggerimento iniziale H A.
Il TTF è [Leonardus-1260-Regular.ttf](../fonts/Leonardus-1260-Regular.ttf),
famiglia **Leonardus 1260**, Regular.

La [ricevuta](../data/human_bfhioq_integration_review_2026-10-16.json) conserva
la citazione della scelta, gli hash dei sei SVG e della tavola mostrata.
Il [manifesto 1.260](../glyphs/regular/release-1.260.json) vincola la build
alla 1.250 preservata. Lo [studio BFHIOQ](BFHIOQ_VARIANT_STUDY.md) mantiene
il suo registro preparatorio, senza promozioni di letture o autenticità.

Sono integrati esattamente i contorni selezionati, senza ridisegni:
B con occhielli obliqui; F con asola alta; H con asola sinistra e ritorno
al piede; I con testa e piede più sobri; O con chiusura interna diseguale;
Q con ritorno arcuato sotto il corpo. **Ì e Ò** riutilizzano I A e O B,
con accenti riallineati e ancore combinanti aggiornate.

Tutte le minuscole, le dodici maiuscole precedentemente selezionate e gli
altri glifi conservano i contorni. Tutti gli avanzamenti sono invariati;
il bianco bbox p–q rimane 115 unità. I checkpoint precedenti conservano
esattamente i loro byte. La [derivazione per glifo](DERIVAZIONE_1_260.csv)
aggiorna soltanto sei sorgenti e due compositi dipendenti.

## Ambito storico

Le sei maiuscole restano **`designed`**: i quattro confronti di iniziali
di caso irrisolto e le dodici minuscole di confronto non sono nuove
attestazioni capitali. In particolare B e H sono sintesi da riferimenti
minuscoli, I e Q mantengono riserve sui confini osservati. La scelta umana
approva i disegni per l’integrazione, senza confermare nuove letture, caso,
foliazione, segmentazioni, autenticità, altri caratteri o pubblicazione.

Il CSV storico resta invariato: **144 righe, 101 revisionate e 43 candidate**;
20 minuscole con letture revisionate e sei completamenti ragionati.
Le 61 segmentazioni non cambiano. Nessun avallo istituzionale o firma
ricostruita. Le diciotto maiuscole ora selezionate sono reinterpretazioni
contemporanee documentate. Le altre otto hanno un
[confronto A/B](JKUVWXYZ_VARIANT_STUDY.md) separato, in attesa di scelta.

## Spaziatura e prove

Il [confronto con la 1.250](../specimen/BFHIOQ-Integration-1.260.png)
comprende Bottega, Bellezza, Firenze, Forma, Historia, Homo, Italia,
Ingegno, Opera, Ombra, Quaderno e Quiete; inoltre frasi, titoli, doppie,
Ba/Be, Fi/Fo, Hi/Ho, Il/In, Op/Om, Qu/Qo, I/l/1 e O/0/Q. Le prove latine
Historia/Homo sono esempi di lettura, non citazioni del manoscritto.

Prove HarfBuzz + FreeType a 12/18/36/72 pt, 96 DPI, senza fallback.
La verifica visiva della combinazione scelta non richiede nuovi avanzamenti
o kerning specifico. BBox in unità su 1000:

| Lettera | Avanzamento | Margine sinistro | Margine destro |
|---|---:|---:|---:|
| B | 550 | 58 | 49 |
| F | 505 | 61 | 14 |
| H | 610 | 57 | 48 |
| I | 285 | 31 | 41 |
| O | 635 | 82 | 58 |
| Q | 645 | 82 | 24 |

Le 2.704 coppie delle 52 lettere a 16/24/48/96/128 px/em, soglia 127,
non presentano collisioni d’inchiostro. Il criterio non certifica la spaziatura
ottica a ogni corpo o la leggibilità umana. Le asole minute di F/H sono più
discrete ai corpi piccoli; i disegni scelti sono conservati.

Audit e repertorio: **119 codepoint, 121 glifi**, contorni entro le metriche
verticali. Test di build identiche, contorni selezionati esatti, isolamento,
conservazione degli avanzamenti e della spaziatura p/q, compositi e accenti
NFC/NFD, corrispondenza del CSV e rifiuto di selezioni o classificazioni alterate.
Risultati nel [rapporto QA](QA_1_260.json).

## Installazione e riproduzione

Installata nell’account Windows corrente come **Leonardus 1260**, Regular.
La selezione GDI verifica gli stessi byte del TTF anche da un processo nuovo.
File e registrazione della 1.250 sono conservati. Prove native Office della
1.260 e stampa fisica non sono dichiarate.

La [pagina di prova](../specimen/Leonardus-1260-Trial.html) offre testo libero,
alfabeto e confronto con la 1.250.

SHA256: `f0c1ed6faeb76e66ab88a54cff7ca52c6c30fd33884c72b74cc915b5030e70bf`.

```powershell
python -m leonardus.cli build-release --version 1.260 --out build/Leonardus-1260-Regular.ttf
python -m leonardus.cli audit --font build/Leonardus-1260-Regular.ttf
python -m leonardus.cli charset --font build/Leonardus-1260-Regular.ttf
python examples/regular_spacing_check.py --font build/Leonardus-1260-Regular.ttf --ppem 128 --out build/pairs-1260.json
python examples/regular_specimen.py --font build/Leonardus-1260-Regular.ttf --out build/proof-1260 --candidate
python examples/bfhioq_selection_proof.py --out build/bfhioq-selection.png
```

Contorni originali OFL 1.1; codice e documentazione MIT. Nessuna immagine
manoscritta incorporata o distribuita.
