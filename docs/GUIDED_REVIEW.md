# Revisione guidata delle minuscole

Questo record conserva la revisione umana di lettura, foliazione e caso
dei 61 campioni. Il successivo [consolidamento dei confini](SEGMENTATION_CONSOLIDATED.md)
è completo, con attribuzione distinta dei pareri delegati. Le scelte
progettuali delle 26 minuscole sono nella [1.200](REGULAR_1_200.md);
le candidate non selezionate non diventano revisioni umane per questo seguito.

Il percorso seleziona **61 campioni in sette gruppi**, con quattro–dieci
schede ciascuno. Serve a raccogliere letture motivate prima di disegnare
altre normalizzazioni. Il corpus contiene 144 campioni: **101 revisionati
e 43 ancora candidati**. La revisione dei sette gruppi è completata il
15 ottobre 2026: **61 schede su 61**, tutte con lettura compatibile,
foliazione confermata dal confronto e caso minuscolo.
La Regular 1.000 conserva contorni e classificazioni approvati.

## Revisione registrata del 15 ottobre 2026

I dieci campioni del gruppo 1, cinque m e cinque t, hanno tutti esito
**compatibile / confermata dal confronto / minuscola**. La
[ricevuta della revisione](../data/human_guided_review_2026-10-15_group-01.json)
fissa il piano, gli ID e gli esiti. Le ricevute dei gruppi successivi
registrano le altre 51 conferme: [b/h](../data/human_guided_review_2026-10-15_group-02.json),
[p/g](../data/human_guided_review_2026-10-15_group-03.json),
[s/f](../data/human_guided_review_2026-10-15_group-04.json),
[c/i](../data/human_guided_review_2026-10-15_group-05.json),
[q/u](../data/human_guided_review_2026-10-15_group-06.json) e
[z](../data/human_guided_review_2026-10-15_group-07.json).
Il CSV modifica soltanto i campi di revisione dei 61 campioni selezionati;
gli altri 83 record conservano i rispettivi byte e stati precedenti.

La conferma riguarda lettura, corrispondenza del folio e caso. Non approva
la trascrizione dell'intera parola, la segmentazione dei contorni,
l'autenticità paleografica o il disegno delle nuove forme. I batch JSON
restano checkpoint della selezione iniziale; le revisioni successive sono
conservate separatamente e verificate contro piano, batch e CSV.

## Percorso e criteri

| Ordine | Lettere | Schede | Scopo del confronto |
|---|---|---:|---|
| 1 | m, t | 10 | Minimi, traverse e confini in quattro folii di lavoro. |
| 2 | b, h | 10 | Pancia chiusa e spalla aperta; distinguere parole, richiami e diagrammi. |
| 3 | p, g | 10 | Lobi, cappi e discendenti; separare righi e linee tecniche. |
| 4 | s, f | 9 | Distinguere s lunga, traversa propria e collegamenti. |
| 5 | c, i | 8 | Disambiguare archi, aste, punti e possibili abbreviazioni. |
| 6 | q, u | 10 | Distinguere q/p/g, n/u e associazione moderna u/v. |
| 7 | z | 4 | Distinguere z, e e abbreviazioni in contesti ancora poco vari. |

Il [piano JSON](../data/guided_review_2026-10-14.json) contiene gli ID
selezionati, le motivazioni, le domande per lettera e le note specifiche.
Fissa con SHA256 i due batch di provenienza: una bozza rimane associata
all'esatta versione del piano.

Sono privilegiati contesti leggibili e, quando disponibili, folii diversi.
Un'etichetta tecnica non equivale a un'occorrenza in parola. Alcuni casi
meno adatti al primo confronto restano nel corpus completo: f isolata nel
diagramma, c forse abbreviativa, i dedotta dalla sequenza di etichette e
z sospetta di abbreviazione nel folio editoriale 153v. Non sono stati
cancellati o riclassificati.

Il numero di schede è una scelta di revisione, non una soglia di autenticità.
In particolare f, c, i e z hanno quattro campioni revisionati ciascuna;
b, g, h, m, p, q, s, t e u ne hanno cinque. Anche per queste ultime
servono delimitazione dei tratti, valutazione della varietà e una
successiva revisione del disegno.

## Aprire e usare il dossier

Le immagini restano locali e ignorate da Git. Acquisizione, nomi e hash
degli originali sono descritti nelle guide al [primo batch](CORPUS_EXPANSION.md)
e al [secondo batch](LOWERCASE_SEARCH.md). Non servono alla build del font.

```powershell
.\.venv\Scripts\python.exe examples/guided_review.py --check-only
.\.venv\Scripts\python.exe examples/guided_review.py
```

Aprire `build/guided-review/index.html`, utilizzabile offline. Il generatore
verifica tutti i 100 campioni dei batch contro registri e immagini prima
di produrre le 61 schede. Per ciascuna mostra bersaglio specchiato 3×,
contesto specchiato con riquadro rosso e ritaglio nell'orientamento originale
1:1, oltre a fonte, coordinate, hash e dubbi. Non altera gli originali.

Il dossier mostra **«Revisione guidata completata»** e permette di
consultare tutti i sette gruppi. Le 61 schede registrate sono precompilate
e bloccate; una rettifica richiede una nuova decisione esplicita.
I campi del percorso distinguono:

- **Lettura:** compatibile con la lettera proposta, dubbia oppure respinta.
  Una parola attesa o una trascrizione editoriale non bastano da sole.
- **Foliazione:** confermata dal confronto con la fonte oppure dubbia.
  Il numero del viewer e il folio sono riferimenti distinti; non applicare
  una formula aritmetica all'intera sequenza BNE.
- **Caso:** minuscola, maiuscola oppure dubbio. Una maiuscola tecnica non
  viene trasformata in attestazione di una minuscola.
- **Note:** confini del segno, tratti estranei e alternative di lettura,
  senza informazioni personali.

Lasciare una scelta vuota quando non è ancora stata valutata; usare
«Dubbia» quando il confronto non risolve. Il conteggio delle schede compilate
comprende le scelte dubbie e non misura approvazioni. Queste regole restano
valide per eventuali nuovi percorsi; nel percorso corrente non restano
schede vuote o dubbie.

**Esportare la bozza JSON prima di chiudere o ricaricare la pagina:** le
annotazioni restano soltanto in memoria, senza salvataggio automatico.
È possibile esportare anche dopo un solo gruppo; i restanti campi rimangono
vuoti. La pagina non importa bozze precedenti e non invia dati a servizi
esterni. Conservare separatamente le esportazioni parziali per il successivo
consolidamento.

Per controllare una bozza salvata, senza importarla nel corpus:

```powershell
.\.venv\Scripts\python.exe examples/guided_review.py --validate-decisions build/review-draft.json
```

Lo stato esportato è `review_draft`. Il valore `accepted` significa
soltanto «lettura proposta compatibile»; non approva il contorno, il font
o l'autenticità paleografica. La registrazione nel corpus richiede il
controllo delle decisioni effettive e della provenienza. Disegno, metriche,
versione e build appartengono alla fase successiva, dopo tale revisione.

## Ricerca che procede separatamente

Il [registro del seguito di ricerca](../data/research_followup_2026-10-14.json)
conserva osservazioni istituzionali e limiti, senza nuove righe di evidenza.

- **67v:** proposta una concordanza fra [e-Leo](https://www.leonardodigitale.com/sfoglia/madrid-I/0067-v/)
  e [pagina BNE 131](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=131).
  Coincidono apparato per filare, tre ruote orizzontali, contrappeso ovale,
  manovella e disposizione del testo. Il confronto visivo dell'agente
  resta da revisionare; non valida una formula generale di foliazione.
  Le Y e K editoriali di questo folio non diventano y e k minuscole.
- **y:** nuovi obiettivi nei folii [72r](https://www.leonardodigitale.com/sfoglia/madrid-I/0072-r/)
  e [89r](https://www.leonardodigitale.com/sfoglia/madrid-I/0089-r/).
  Il primo offre etichette e richiami nel testo; il secondo un diagramma
  di leve e pesi. Servono localizzazione BNE, coordinate e revisione della
  forma e del caso prima di aggiungere campioni. Le immagini e-Leo non
  sono state acquisite o distribuite.
- **j:** la ricerca Madrid I estesa alle note nell'[indice e-Leo](https://www.leonardodigitale.com/ricerca-nel-testo/)
  restituisce ancora il solo documento 153v nel filtro registrato.
  Il dato riguarda l'indice, non dimostra assenza nel manoscritto.
- **v, x:** cercare altri folii e distinguere forma, associazione moderna
  ed eventuali croci tecniche; le due proposte per lettera provengono
  tuttora dalla stessa pagina BNE 49.
- **k, w:** nessuna nuova candidata minuscola. Le osservazioni K restano
  separate e l'assenza di w nei contesti esaminati non è un'assenza generale.
- **f, c, i, z:** rinforzare con altri contesti indipendenti i nuclei più
  deboli del percorso; per z evitare che un solo folio domini il corpus.

Le letture dubbie possono rimanere aperte mentre la ricerca continua.
Il dossier guidato e i due dossier completi restano strumenti complementari.

## Fase successiva

Le [prime segmentazioni e proposte di disegno](SEGMENTATION_DESIGN_REVIEW.md)
coprono tutti i 61 campioni. I tredici disegni sono approvati, compresa
la s rivista con curva inferiore, e integrati nella
[Regular 1.100](REGULAR_1_100.md). Le segmentazioni richiedono una revisione
separata per ogni futura pretesa di derivazione diretta dal manoscritto.

Proseguire la revisione delle delimitazioni. Per c, f, i e z
rinforzare il supporto con altri contesti, senza usare il numero come
certificazione paleografica. Le 39 candidate degli ampliamenti escluse
dal percorso e i quattro dubbi iniziali restano tali. Nessuna conferma
si estende automaticamente a j, k, v, w, x, y o alle nuove piste di ricerca.
La conferma dei tredici disegni e l’integrazione sono registrate
separatamente dalle letture e dai ritagli storici.
