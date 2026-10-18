# Regular 1.270 — integrazione di J, K, U, V, W, X, Y, Z

**Denominazione attuale, 17 ottobre:** famiglia **Leonardus**, stile
**Regular**, versione interna **1.270**. Installare
[Leonardus-Regular-1.270.ttf](../fonts/Leonardus-Regular-1.270.ttf).
La [rinomina approvata](REGULAR_1_270_NAMING.md) conserva disegni, metriche
e shaping; il TTF e i conteggi seguenti documentano il checkpoint precedente
con famiglia Leonardus 1270, conservato senza modifiche.

16 ottobre 2026. Integrate **J B, K B, U B, V B, W B, X B, Y B, Z B**.
Le scelte esplicite J/W/Y/Z B prevalgono sui suggerimenti precedenti A.
Il TTF è [Leonardus-1270-Regular.ttf](../fonts/Leonardus-1270-Regular.ttf),
famiglia **Leonardus 1270**, Regular.

La [ricevuta umana](../data/human_jkuvwxyz_integration_review_2026-10-16.json)
conserva la citazione completa, gli hash degli otto SVG e della tavola mostrata.
Il [manifesto 1.270](../glyphs/regular/release-1.270.json) vincola la build
alla 1.260 preservata. Lo [studio](JKUVWXYZ_VARIANT_STUDY.md) rimane il registro
preparatorio, con i suoi stati originari. Nessun contorno scelto è ridisegnato
successivamente. **Ù** segue U B con accento riallineato e ancore combinanti
aggiornate. Le altre diciotto maiuscole, tutte le minuscole e gli altri contorni
sono conservati, come tutti gli avanzamenti e il bianco bbox p–q di 115 unità.
La [derivazione per glifo](DERIVAZIONE_1_270.csv) aggiorna otto sorgenti e Ù,
conservando riferimenti contestuali e motivi di progetto.

## Ciclo delle maiuscole completato

Le quattro selezioni 1.240/1.250/1.260/1.270 coprono esattamente le **26
maiuscole A–Z**, senza omissioni o sovrapposizioni: **23 B, E/I/N A**.
Non resta un altro gruppo di lettere maiuscole di base da selezionare.
À, È, É, Ì, Ò e Ù riutilizzano le rispettive basi scelte; non sono sei nuove
attestazioni storiche. Il repertorio concordato resta di 119 codepoint e 121 glifi.
Estensioni ulteriori al latino di base non fanno parte di questa selezione.

| Maiuscola | Variante selezionata |
|---|---|
| A | B |
| B | B |
| C | B |
| D | B |
| E | A |
| F | B |
| G | B |
| H | B |
| I | A |
| J | B |
| K | B |
| L | B |
| M | B |
| N | A |
| O | B |
| P | B |
| Q | B |
| R | B |
| S | B |
| T | B |
| U | B |
| V | B |
| W | B |
| X | B |
| Y | B |
| Z | B |

La chiusura riguarda il confronto e la scelta dei disegni. **Tutte le capitali
restano `designed`**, non 26 capitali manoscritte attestate. Il registro storico
mantiene gli stessi byte: 144 campioni, 101 revisionati e 43 candidati, venti
minuscole collegate a letture revisionate e sei completamenti ragionati.
Le 61 segmentazioni restano invariate. Nessuna nuova lettura, segmentazione,
foliazione, autenticità, approvazione di altri caratteri o pubblicazione è dedotta.

Per questo gruppo i 13 confronti conservano sei candidate, tre osservazioni K
di caso irrisolto e quattro minuscole revisionate. **J alfabetica e W sono
completamenti contemporanei dichiarati**: J non usa il segno candidato ambiguo
come geometria primaria; W non ha campione diretto. La distinzione U/V, la
forcella Y e la traversa di Z B sono progettate. La scelta umana degli otto
contorni non modifica queste riserve, né autentica una grafia o una firma.

## Spaziatura e prove

Il [confronto 1.260/1.270](../specimen/JKUVWXYZ-Integration-1.270.png) comprende
Jazz, Junior, Kilo, Karate, Uomo, Universo, Vinci, Volo, Weekend, Whisky,
Xilofono, Xenon, Yogurt, Yoga, Zefiro e Zaino; inoltre frasi, doppie, coppie
iniziali, I/J/j, U/V/W, X/Y/Z/2 e U/Ù in NFC/NFD. Sono parole reali moderne,
anche prestiti; non trascrizioni di Leonardo. Prove HarfBuzz + FreeType senza
fallback a 12/18/36/72 pt, 96 DPI, e campionario completo della 1.270.

La verifica visiva della combinazione non richiede nuovi avanzamenti o
kerning specifico. Le piccole asole di J/K/U/V/W e il piede di Y sono più
discreti ai corpi piccoli; la traversa di Z B è conservata come scelta esplicita.
BBox in unità su 1000, non distanze ottiche:

| Lettera | Avanzamento | Margine sinistro | Margine destro |
|---|---:|---:|---:|
| J | 430 | 45 | 7 |
| K | 580 | 57 | 26 |
| U | 610 | 74 | 52 |
| V | 565 | 105 | 13 |
| W | 810 | 104 | 10 |
| X | 570 | 41 | 20 |
| Y | 560 | 109 | 12 |
| Z | 565 | 55 | 30 |

Le 2.704 coppie delle 52 lettere a 16/24/48/96/128 px/em, soglia 127, non
hanno collisioni d’inchiostro nel criterio dichiarato. Non è una certificazione
della spaziatura ottica o della leggibilità umana a ogni corpo.
Audit e repertorio: 119 codepoint e 121 glifi, entro le metriche verticali.
I test verificano build identiche, contorni esatti, conservazione delle forme
precedenti e degli avanzamenti, accenti, corrispondenza CSV e compositi,
rifiuto di selezioni alterate e corrispondenza di tutte le 26 capitali alle
quattro selezioni umane. [Esiti QA](QA_1_270.json).

## Installazione e uso

Il collaudo Windows di **Leonardus 1270**, Regular, verifica per byte la
selezione GDI del TTF anche da un processo nuovo. La
[denominazione finale](REGULAR_1_270_NAMING.md) usa famiglia **Leonardus**;
le [istruzioni di installazione](../INSTALL.md) indicano il file corrente.
I checkpoint conservano il rispettivo ambito di verifica. La
[pagina di prova](../specimen/Leonardus-1270-Trial.html) offre alfabeto, testo
libero, parole e confronto con la versione precedente.

Il [collaudo del 17 ottobre](OFFICE_1_270.md) verifica i quattro corpi
12/18/36/72, salvataggio e riapertura in Word/PowerPoint e il PDF Word,
con 115 contorni incorporati coincidenti con il TTF. Il PDF PowerPoint
è prodotto con protezione e il suo contenuto è confermato
dall'utente il 17 ottobre; nessun confronto automatico dei suoi contorni
è dichiarato. È pronto il [campionario A4](../specimen/Leonardus-1270-Print-Specimen.pdf).
Stampa fisica e parere paleografico indipendente non sono eseguiti.
Non occorre inventare altri gruppi
A–Z per considerare conclusa questa selezione di disegno. Eventuali futuri
miglioramenti resteranno revisioni motivate e versionate.

SHA256: `3e1e7e6ac2416f6f321b302b46fb1b598ac04015663d731324224ce0221c240d`.

```powershell
python -m leonardus.cli build-release --version 1.270 --out build/Leonardus-1270-Regular.ttf
python -m leonardus.cli audit --font build/Leonardus-1270-Regular.ttf
python -m leonardus.cli charset --font build/Leonardus-1270-Regular.ttf
python examples/regular_spacing_check.py --font build/Leonardus-1270-Regular.ttf --ppem 128 --out build/pairs-1270.json
python examples/regular_specimen.py --font build/Leonardus-1270-Regular.ttf --out build/proof-1270 --candidate
python examples/jkuvwxyz_selection_proof.py --out build/jkuvwxyz-selection.png
```

Contorni originali OFL 1.1; codice e documentazione MIT. Nessuna riproduzione
manoscritta incorporata o distribuita. La pubblicazione resta una decisione distinta.
