# Studio di C, D, E, G, P, T — 16 ottobre 2026

Questa scheda conserva lo studio preparatorio rispetto alla 1.240, con due
varianti per ciascuna maiuscola. La successiva [scelta umana](REGULAR_1_250.md)
integra **C B, D B, E A, G B, P B, T B** nella 1.250. E A, G B e P B
prevalgono sui precedenti suggerimenti; il registro dello studio e i suoi
stati sono preservati, senza trasformarli in nuove approvazioni storiche.

## Ricerca, confronti e limiti

Studio mirato sulle riproduzioni BNE del Madrid I già disponibili: nessuna nuova
acquisizione o risoluzione maggiore. Consultati i testi istituzionali e-Leo,
Biblioteca Leonardiana, per [1r](https://www.leonardodigitale.com/sfoglia/madrid-I/0001-r/),
[1v](https://www.leonardodigitale.com/sfoglia/madrid-I/0001-v/) e
[4r](https://www.leonardodigitale.com/sfoglia/madrid-I/0004-r/), confrontando
contesto e riproduzioni locali specchiate. I confronti minuscoli includono anche
2r e 3r. Non è una ricerca esaustiva in tutti i manoscritti.

Il [registro](../data/cdegpt_variant_study_2026-10-16.json) vincola **12 confronti**:
quattro osservazioni formali nuove di caso non revisionato e otto minuscole già
revisionate nel CSV storico. Per ogni confronto conserva folio di lavoro,
pagina del visualizzatore, ID e hash dell'immagine, coordinate originali e
specchiate, contesto e riserve. Le nuove osservazioni non sono campioni storici
approvati: il registro `data/glyph_evidence.csv`, le sue 144 righe e i precedenti
manifest conservano gli stessi byte. Nessuna nuova lettura maiuscola revisionata.

La distinzione fra iniziale editoriale e forma grafica rimane esplicita: la c
all'inizio del passo Considera conserva il caso minuscolo già revisionato.
La E aperta è nel passo **E alcuna volta**, senza accento; il precedente
riconoscimento preliminare del contesto come È necessario è escluso.
La T confrontata è all'inizio di **Tutte le molli**, sotto il diagramma del 4r;
il segno all'inizio della frase superiore **Il peso** non è usato come T.
Questi controlli evitano di costruire varianti su una lettura contestuale errata.

| Lettera | Base del confronto | A | B | Parere di disegno |
|---|---|---|---|---|
| C | Due c minuscole del 1r: apertura e terminali diseguali. Nessuna capitale autonoma selezionata. | Arco regolare e corpo ampio. | Corpo più obliquo e ritorno inferiore marcato. | **B**: differenza misurata, coerente con le minuscole. |
| D | Iniziale del titolo De denti delle rote (1v), di caso non confermato, e d revisionata del 2r. | Corpo largo e attacco semplice. | Asta curva e occhiello obliquo. | **B**: più vicina al ritmo della R B scelta; la struttura capitale è moderna. |
| E | Forma aperta del 1v e e minuscola del 3r. Il campione nuovo offre arco e traversa, senza accento. | Tre terminali leggibili e asta curva. | Due archi aperti, simili a epsilon, e traversa breve. | **B**: il confronto formale più caratterizzato; verificare la preferenza nella lettura di Esperienza. |
| G | g minuscole del 2r e 4r: occhiello e ritorno a cappio. Nessuna G capitale completa confermata. | Apertura e barra corta. | Ritorno interno a spirale. | **A**: lettura più immediata; B esplora un ritorno che può avvicinarsi alla cifra 6. |
| P | Iniziale Perché del 1r, non revisionata, e p minuscola nello stesso folio. | Occhiello leggibile e asta sobria. | Occhiello obliquo e piccolo ritorno al piede. | **A**: meno enfasi sul piede in Pittura e Progetto. |
| T | Iniziale del passo sotto il diagramma del 4r e t minuscola del 1r. | Traversa appena curva e asta continua. | Traversa arcuata e ritorno al piede. | **B**: rende meno rigida la T mantenendola riconoscibile. |

Tutte le proposte sono `unapproved_contemporary_reinterpretation`, senza
attestazione di maiuscola storica. Contorni, altezza, peso, proporzioni e
raccordi sono progettati. Le minuscole revisionate non attestano il caso
maiuscolo; la trascrizione editoriale non approva geometria e segmentazione.
Un'eventuale futura attribuzione a una forma storica richiederà prima la relativa
voce e revisione nel registro delle evidenze. Nessuna autenticità paleografica,
sequenza, pressione o velocità dei tratti viene certificata.

## Prova e scelta

La [tavola delle parole](../specimen/CDEGPT-Study-Words-2026-10-16.png) confronta
la 1.240 con A e B: **in ciascuna riga cambia soltanto la maiuscola indicata**.
Codice, Carta, Disegno, Duca, Esperienza, Europa, Genio, Geometria, Pittura,
Progetto, Tempo e Toscana sono parole moderne di prova, non trascrizioni storiche.
La pagina locale aggiunge frasi, titoli, testo libero, corpo regolabile,
campioni con contesto e selettori per combinazioni miste.

La combinazione proposta è **C B, D B, E B, G A, P A, T B**. Il pulsante
«Prova la combinazione proposta» applica soltanto l'anteprima: non registra
un'approvazione o modifica il font installato. Si può conservare la 1.240 per
qualsiasi lettera. La scelta umana successiva riguarda i disegni, non nuove conferme
delle letture, dei confini, del caso o dell'autenticità.

## Riproduzione e verifiche

```powershell
python examples/cdegpt_study.py --out build/cdegpt-study
# Facoltativo: originali locali già acquisiti; nessun download automatico.
python examples/cdegpt_study.py --out build/cdegpt-study-with-sources --originals build/quality-completion/originals
python -m pytest -q tests/test_cdegpt_study.py
python -m leonardus.cli audit --font build/cdegpt-study/Leonardus-CDEGPT-A.ttf
python -m leonardus.cli charset --font build/cdegpt-study/Leonardus-CDEGPT-A.ttf
python examples/regular_spacing_check.py --font build/cdegpt-study/Leonardus-CDEGPT-A.ttf --ppem 128 --out build/cdegpt-study/pairs-A-128.json
```

Ripetuti audit e copertura per entrambe le serie: 119 codepoint, 121 glifi,
contorni entro le metriche verticali. **2.704 coppie per serie** a 16, 24, 48,
96 e 128 px/em, soglia 127: nessuna collisione d'inchiostro. Il controllo non è
una certificazione della spaziatura ottica. Prove raster a 12/18/36/72 pt,
96 DPI, HarfBuzz e FreeType; anteprima verificata nel browser. Nessuna prova
nativa Office o stampa fisica delle proposte.

Le famiglie `Leonardus CDEGPT A/B`, versione tecnica 1.241, restano esperimenti
distinti dalla Regular. Cambiano solo le sei basi e le dipendenze È/É; tutti
gli avanzamenti, le minuscole e le sei maiuscole della 1.240 sono conservati.
Nell'anteprima mista È/É seguono E e i combinanti restano nella stessa famiglia
della base. Test di riproducibilità, isolamento, accenti e rifiuto di promozioni
indebite delle evidenze sono registrati nel [rapporto QA](QA_CDEGPT_STUDY_2026-10-16.json).

Fonte: [BNE, Madrid I MSS/8937](https://bnedigital.bne.es/bd/card?oid=0000040157&site=bdh).
**Imágenes procedentes de los fondos de la Biblioteca Nacional de España**.
Ritaglio, specchiatura e ingrandimento dichiarati; nessun avallo BNE.
L'ingrandimento non aggiunge dettagli e i rettangoli localizzano segni, non
certificano contorni. Immagini escluse da Git; valgono gli ambiti locali della
[verifica dei diritti](SOURCE_RIGHTS_REVIEW.md). Contorni originali OFL 1.1;
codice e documentazione MIT.
