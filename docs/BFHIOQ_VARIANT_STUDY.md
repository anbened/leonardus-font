# Studio di B, F, H, I, O, Q — 16 ottobre 2026

Questa scheda conserva lo studio preparatorio rispetto alla **Regular 1.250**.
La successiva [scelta umana](REGULAR_1_260.md) integra **B B, F B, H B, I A,
O B, Q B** nella 1.260: H B prevale sul suggerimento iniziale H A. Il registro
originario mantiene gli stati della fase preparatoria, senza nuove approvazioni
storiche. Parole, frasi e titoli conservano il confronto precedente.

## Ricerca e limiti

Riesaminate sei riproduzioni del Madrid I BNE già disponibili (pagine del
visualizzatore 14, 15, 16, 18, 20, 21; folii di lavoro 1r, 1v, 2r, 3r, 4r, 4v).
Consultati i contesti istituzionali e-Leo, Biblioteca Leonardiana, di
[1r](https://www.leonardodigitale.com/sfoglia/madrid-I/0001-r/),
[1v](https://www.leonardodigitale.com/sfoglia/madrid-I/0001-v/),
[2r](https://www.leonardodigitale.com/sfoglia/madrid-I/0002-r/) e
[4r](https://www.leonardodigitale.com/sfoglia/madrid-I/0004-r/).
Nessun nuovo download o dettaglio a risoluzione maggiore; non è una ricerca
esaustiva in tutti i manoscritti di Leonardo.

Il [registro dello studio](../data/bfhioq_variant_study_2026-10-16.json)
vincola **16 confronti**: quattro osservazioni di iniziali di caso irrisolto
e dodici minuscole già revisionate, due per lettera. Ogni localizzazione
registra folio, pagina, ID e hash dell’immagine, coordinate originali e
specchiate, contesto e riserve. I riquadri sono localizzazioni, non nuove
segmentazioni approvate. La trascrizione editoriale serve al riconoscimento
del contesto e non conferma il caso grafico.

Il CSV storico conserva le sue **144 righe, 101 revisionate e 43 candidate**,
e gli stessi byte. Non cambia nessuna delle 61 segmentazioni consolidate.
**Nessuna nuova lettura maiuscola revisionata.** Le osservazioni di questo
studio restano confronti esplorativi; non sono nuove attestazioni storiche
delle capitali. Per attribuire in futuro un disegno a una capitale attestata
serviranno prima la relativa voce nel registro storico e una revisione.

| Lettera | Confronto | A | B | Proposta |
|---|---|---|---|---|
| B | Due b minuscole, 1r e 1v; nessuna B capitale autonoma selezionata. | Due occhielli chiari, asta curva, corpo inferiore più ampio. | Occhielli obliqui e diseguali, fondo arrotondato. | **B**: rende meno meccanico il doppio corpo e si accorda con P/R già scelte. |
| F | Iniziale di Fa lle tue piastre (1v), caso irrisolto; f del 1r e 3r. | Testa ondulata e traversa continua. | Piccola asola alta e traversa in risalita. | **B**: riprende il rapporto fra uncino e traversa con una struttura capitale moderna. |
| H | Due h minuscole, 1v e 4v; nessuna H capitale completa confermata. | Due aste appena curve e traversa morbida. | Asola nell’asta sinistra e ritorno al piede destro. | **A**: più sobria nelle parole e nelle sigle; B enfatizza un’asola non attestata come capitale. |
| I | Iniziale di Il peso (4r), caso irrisolto; i del 2r e 3r. | Attacco curvo breve e piede distinto. | Piccola asola d’ingresso e piede più curvo. | **A**: migliore separazione da l minuscola e cifra 1. B è più gestuale ma può avvicinarsi alla cifra. |
| O | Iniziale Ogni (2r), caso irrisolto; due o revisionate nello stesso folio. | Ovale obliquo e controforma asimmetrica. | Corpo più rotondo e piccolo ritorno interno alto. | **B**: chiusura meno geometrica, coerente con la o già scelta. Il ritorno esatto è progettato. |
| Q | Iniziale Quisiti (1r), caso irrisolto; q del 1r e 3r. | Corpo O A e coda diagonale breve. | Corpo O B e coda arcuata sotto il corpo. | **B**: evoca il ritorno inferiore osservato, contenendolo nella larghezza; il percorso esatto è moderno. |

L’iniziale di **Il peso** non è una T. Il confronto I riguarda il gesto curvo
nel suo insieme; la l e la p adiacenti non diventano parti del disegno.
Il ritorno della **Q di Quisiti** incontra altri tratti: non se ne assume un
confine completo certo. B e H sono sintesi da confronti minuscoli, che non
attestano le rispettive capitali. Le altezze, il peso, le controforme, il
doppio corpo di B e la traversa di H sono decisioni contemporanee.

Tutti i dodici SVG sono `unapproved_contemporary_reinterpretation`;
`historical_capital_attestation`, approvazione umana e integrazione restano
false. Non si certificano autenticità, sequenza, pressione o velocità dei tratti.

## Confronto e scelta

La [tavola nelle parole](../specimen/BFHIOQ-Study-Words-2026-10-16.png)
mostra 1.250, A e B; **ogni riga cambia soltanto la lettera indicata**.
Bottega, Bellezza, Firenze, Forma, Italia, Ingegno, Opera, Ombra, Quaderno
e Quiete sono parole reali di prova. Historia e Homo sono esempi latini,
utili per H iniziale; non sono citazioni del manoscritto. Le frasi di prova
sono moderne. Tutte le dodici maiuscole selezionate nei gruppi precedenti
sono identiche nelle tre colonne.

La pagina locale generata aggiunge campioni storici con contesto, corpo
regolabile, testo libero, serie complete e sei selettori indipendenti.
La combinazione consigliata è **B B, F B, H A, I A, O B, Q B**. Il pulsante
«Prova la combinazione proposta» cambia soltanto l’anteprima. Si può mantenere
la 1.250 per qualsiasi lettera; la scelta non viene registrata automaticamente.
Ì e Ò seguono le rispettive I e O; i combinanti restano nella famiglia della base.
Una scelta successiva approverà i disegni, senza promuovere letture o autenticità.

Dopo la selezione BFHIOQ sono **18 maiuscole integrate**; le otto
rimanenti, J/K/U/V/W/X/Y/Z, hanno un [nuovo studio](JKUVWXYZ_VARIANT_STUDY.md). Tutte le 26 esistono già
nel font; questi conteggi descrivono il nuovo ciclo di approfondimento.

## Riproduzione e verifiche

```powershell
python examples/bfhioq_study.py --out build/bfhioq-study
# Facoltativo, solo con gli originali locali già acquisiti:
python examples/bfhioq_study.py --out build/bfhioq-study-with-sources --originals build/quality-completion/originals
python -m pytest -q tests/test_bfhioq_study.py
python -m leonardus.cli audit --font build/bfhioq-study/Leonardus-BFHIOQ-A.ttf
python -m leonardus.cli charset --font build/bfhioq-study/Leonardus-BFHIOQ-A.ttf
python examples/regular_spacing_check.py --font build/bfhioq-study/Leonardus-BFHIOQ-A.ttf --ppem 128 --out build/bfhioq-study/pairs-A-128.json
```

Le famiglie separate `Leonardus BFHIOQ A/B`, versione tecnica **1.251**,
sono esperimenti; non costituiscono una nuova release Regular. Sono modificati
soltanto B/F/H/I/O/Q e le dipendenze Ì/Ò; tutti gli avanzamenti sono conservati.
Audit e repertorio su entrambe le serie: 119 codepoint e 121 glifi; accenti
entro le metriche verticali. Verificate **2.704 coppie per serie e dimensione**
a 16/24/48/96/128 px/em: nessuna collisione d’inchiostro nel criterio dichiarato
(soglia 127). Il controllo non certifica la spaziatura ottica a ogni corpo.
Prove a 12/18/36/72 pt, 96 DPI, HarfBuzz e FreeType; confronti visuali e
anteprima nel browser. Nessuna prova nativa Office o stampa fisica degli studi.
Il [rapporto QA](QA_BFHIOQ_STUDY_2026-10-16.json) registra gli esiti effettivi.

Fonte: [BNE, Madrid I MSS/8937](https://bnedigital.bne.es/bd/card?oid=0000040157&site=bdh).
**Imágenes procedentes de los fondos de la Biblioteca Nacional de España**.
Ritaglio, specchiatura e ingrandimento dichiarati; l’ingrandimento non aggiunge
dettagli. Riproduzioni escluse da Git, nessun avallo BNE; ambiti e riserve nella
[verifica dei diritti](SOURCE_RIGHTS_REVIEW.md). Contorni originali OFL 1.1;
codice, metadati e documentazione MIT.
