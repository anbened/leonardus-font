# Metodo e scelte di Leonardus

Leonardus trasforma lo studio di campioni documentati della grafia di Leonardo
da Vinci in un carattere contemporaneo utilizzabile. Si legge da sinistra a
destra e comprende le forme necessarie a comporre testi italiani moderni.

## Il percorso

1. **Documentare i campioni.** I riferimenti al Codice Madrid I, BNE MSS/8937,
   vengono registrati con folio, localizzazione e stato della lettura.
2. **Distinguere lettura e forma.** Riconoscere una lettera non certifica il
   confine di ogni tratto né fornisce automaticamente un glifo.
3. **Disegnare e confrontare.** Le proposte vettoriali vengono confrontate in
   isolamento, nelle parole e nei testi. Peso, raccordi e spaziatura sono
   scelte contemporanee.
4. **Selezionare e compilare.** Le decisioni vengono registrate e il font
   viene compilato da SVG e manifesti attraverso fontTools.
5. **Verificare.** I controlli esaminano copertura Unicode, contorni, accenti,
   spaziatura, riproducibilità e resa nelle applicazioni collaudate.

## Cosa deriva dalle fonti nella 1.270

| Classificazione delle minuscole di base | Lettere |
|---|---|
| Normalizzazioni del pilota conservate | `d l` |
| Disegni contemporanei selezionati con riferimenti a letture revisionate | `a b c e f g h i m n o p q r s t u z` |
| Completamenti contemporanei ragionati | `j k v w x y` |

Sono venti minuscole con riferimenti a letture revisionate e sei completamenti.
Le 26 maiuscole restano disegni contemporanei: i confronti formali non sono
attestazioni di capitali storiche. Lo stesso principio distingue cifre,
accenti e segni moderni dalle evidenze storiche. Gli accenti composti
riutilizzano le basi senza aggiungere nuove lettere storiche attestate.

Il corpus comprende 144 campioni: 101 con letture revisionate e 43 candidati
o dubbi conservati. Il conteggio dei campioni non misura il numero di glifi
storicamente attestati. Le 61 segmentazioni dell'ampliamento mantengono
esiti distinti: 29 revisioni umane individuali e 32 valutazioni dell'agente
su delega esplicita. Non sono contorni storici certificati.

La [derivazione corrente](DERIVAZIONE_1_270.csv), il
[registro delle evidenze](../data/glyph_evidence.csv) e la
[provenienza](PROVENANCE.md) permettono di seguire i collegamenti.

## Collaborazione umana e AI

Codex ha assistito nella ricerca, nei confronti, nelle proposte originali
SVG, nel codice e nei controlli. Le scelte umane hanno guidato il progetto
e selezionato le varianti. I registri distinguono decisioni umane,
valutazioni dell'agente e verifiche automatiche.

La compilazione dai sorgenti inclusi non richiede API AI, addestramento
di modelli o immagini dei manoscritti. La demo tecnica sintetica iniziale,
le evidenze dei campioni e il font progettato mantengono ambiti distinti.
[Contributo dell'agente e decisioni](AGENT_CONTRIBUTION.md).

## Ambito del risultato

La 1.270 è una reinterpretazione contemporanea documentata, non una grafia
autenticata o una firma di Leonardo. Non è dichiarato un parere paleografico
indipendente o un avallo delle istituzioni che custodiscono i manoscritti.

Le prove applicative documentate riguardano Windows, Word e PowerPoint;
stampa fisica e collaudo di altre piattaforme non sono dichiarati completati.
Il [rapporto Office](OFFICE_1_270.md) distingue il collaudo del checkpoint
dalle verifiche della denominazione finale.

## Fonti e riproduzioni

Il repository distribuisce contorni originali, registri e collegamenti alle
fonti. Non contiene scansioni, fotografie o ritagli dei manoscritti. Le
condizioni delle riproduzioni restano separate dalle licenze del font e
del codice. [Fonti e diritti](SOURCE_RIGHTS_REVIEW.md).
