# Leonardus Regular 1.100 — integrazione delle minuscole

15 ottobre 2026. La Regular 1.100 integra i tredici disegni approvati di
**b, c, f, g, h, i, m, p, q, s, t, u, z**, con la s rivista dotata di
curva inferiore. Il [TTF corrente](../fonts/Leonardus-Regular.ttf) mantiene
famiglia Leonardus, stile Regular, repertorio e licenza OFL 1.1.
La versione cambia da 1.000 a 1.100 e ha un identificatore univoco aggiornato.

Il [campionario PDF](../specimen/Leonardus-Specimen.pdf) mostra la nuova
versione a 12, 18, 36 e 72 punti. Sono aggiornati anche i campionari PNG
e l’atlante del repertorio.

## Approvazioni e provenienza

La [prima ricevuta](../data/human_lowercase_design_review_2026-10-15.json)
conserva le dodici approvazioni della colonna Proposta. La
[ricevuta di integrazione](../data/human_lowercase_integration_review_2026-10-15.json)
registra l’approvazione della s rivista e l’integrazione dei tredici
contorni, vincolando file, SHA256 e advance. I tredici SVG approvati
mantengono gli stessi byte: il compilatore non modifica i loro disegni.

I 61 riferimenti hanno letture, foliazione e caso revisionati. Le
segmentazioni annotate restano ipotesi; non sono certificate dalla
conferma dei disegni. Le nuove forme sono classificate `reviewed_design`,
separate dalle sette normalizzazioni del pilota e dai completamenti
contemporanei. Curva inferiore di s, punto di i, chiusure, terminali,
proporzioni e raccordi sono scelte progettuali dichiarate. Non è una
ricostruzione autenticata della grafia o della firma di Leonardo.

[Derivazione per glifo](DERIVAZIONE.csv) e
[manifesto di disegno](../data/lowercase_design_2026-10-15.json) collegano
ogni nuova forma ai suoi riferimenti. Per c, f, i, z il supporto resta
limitato a quattro letture ciascuna. Le altre lettere rare e i dubbi del
corpus non ricevono nuove approvazioni.

## Integrazione tecnica

- Tredici glifi semplici: contorni e advance identici alle forme approvate.
- `dotlessi`: solo il corpo della nuova i, senza il punto. Il compilatore
  verifica che coordinate e tipi dei punti coincidano con il primo
  contorno della i approvata. La sostituzione `ccmp` evita il doppio punto.
- ì e ù: compositi e advance aggiornati alle nuove basi; gli accenti
  rimangono disegni contemporanei. Le altre dieci forme composite restano
  identiche nei contorni e nelle metriche.
- Ancore `mark`: ricompilate dai bounds delle basi; posizionamento degli
  accenti verificato per tutte le tredici lettere con grave e acuto.
- Metriche verticali e larghezza media aggiornate/verificate rispetto al
  font completo; nessun glifo tagliato dai limiti dichiarati.

Cambiano quindi 16 glifi, contando le tre dipendenze tecniche. Gli altri
105 mantengono contorni e metriche della 1.000. La copertura resta
119 codepoint, 121 glifi e 12 compositi. I soli spazi sono vuoti e gli
accenti combinanti hanno advance zero. Non sono introdotti nuovi caratteri.

## Riproducibilità e controlli

Il [manifesto 1.100](../glyphs/regular/release-1.100.json) vincola il
checkpoint, il manifesto dei tredici disegni e la derivata senza punto.
La build ricompila prima la 1.000 dai suoi sorgenti, ne verifica l’hash,
poi integra i disegni e ricostruisce compositi e layout. Non richiede
immagini, servizi esterni o font di terzi.

SHA256 del TTF 1.100:
`1f65d26ece4c8a0fe9c275fcdedfa037fab88a9687b0cd89a941d131eb899632`.

La [1.000 preservata](../fonts/previous/Leonardus-Regular-1.000.ttf) rimane
riproducibile con i manifesti e le ricevute originali, SHA256
`92e3c7d22bcd34652b502b643e1efed61aedf83fac3659c29c73593d028a3d94`.
Le [istruzioni di build](BUILDING.md) riportano entrambi i percorsi.

Le verifiche comprendono build ripetute, corrispondenza esatta dei tredici
contorni, protezione delle ricevute e del checkpoint, repertorio,
contorni non vuoti, licenza e metadati, accenti italiani NFC/NFD equivalenti,
ancore delle nuove basi, spaziatura di 2.704 coppie a 128 ppem senza
collisioni nel criterio raster dichiarato, campionari raster e PDF con
quattro pagine renderizzate e ispezionate. Il [rapporto QA](QA.md) e
[PACKAGE_QA.json](PACKAGE_QA.json) riportano gli esiti.

## Limiti applicativi e distribuzione

La 1.100 è verificata con fontTools, HarfBuzz, FreeType e rendering PDF,
selezione Windows tramite GDI e [prove native Office](OFFICE_1_100.md).
Word e PowerPoint 16.0.20527.20054 superano i controlli su quattro pagine
e quattro slide a 12, 18, 36 e 72 punti, inclusi salvataggio, riapertura
e PDF nativi con contorni incorporati corrispondenti alla 1.100.
Non sono certificati ritmo ottico a ogni
corpo, hinting manuale, stampa fisica o compatibilità universale.

La conferma dei disegni autorizza questa integrazione. La diffusione
pubblica resta una decisione distinta; le verifiche legali e sulle fonti
conservano i limiti già documentati. Le immagini del manoscritto non
sono distribuite. Il corpus, i suoi registri e le ricevute delle letture
rimangono invariati.
