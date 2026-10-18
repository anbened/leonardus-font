# Collaudo applicativo e campionario della Regular 1.270

La [successiva denominazione approvata](REGULAR_1_270_NAMING.md) usa famiglia
**Leonardus**, stile Regular e versione interna 1.270. Questo rapporto
conserva i nomi e gli hash effettivamente impiegati nel collaudo precedente;
la rinomina mantiene invariati tutti i contorni e le tabelle di impaginazione.

17 ottobre 2026. Font **Leonardus 1270**, Regular, TTF SHA256
`3e1e7e6ac2416f6f321b302b46fb1b598ac04015663d731324224ce0221c240d`.
Il collaudo conserva esattamente il font e tutti i disegni selezionati.

## Esiti e attribuzione delle verifiche

Word e PowerPoint **16.0.20527.20066**, Windows, sono provati su documenti
nuovi con campioni a **12, 18, 36 e 72 punti**. Entrambi salvano una copia
nativa, la chiudono e la riaprono; tutte le quattro pagine Word e le quattro
slide PowerPoint sono ispezionate dopo la riapertura.

| Controllo | Word | PowerPoint |
|---|---|---|
| Rendering dei quattro corpi | Verificato | Verificato |
| Salvataggio nativo | DOCX verificato | PPTX verificato |
| Chiusura e riapertura | Verificate | Verificate |
| Pagine/slide riaperte ispezionate | 4 | 4 |
| Comando di esportazione PDF standard | File prodotto | File prodotto, protetto |
| Contenuto PDF finale | 4 pagine ispezionate dall'agente | Confermato dall'utente il 17 ottobre |
| Contorni incorporati confrontati con il TTF | 115 distinti, tutti coincidenti | Non ispezionabili con gli strumenti PDF disponibili |

**Il controllo del contenuto PDF PowerPoint è chiuso dalla revisione umana.** La
protezione del PPTX viene ereditata dal PDF. Gli strumenti PDF ordinari
leggono una pagina di avviso, che non è una slide del campione. La conferma
umana del contenuto è conservata nella
[ricevuta](../data/human_office_pdf_review_2026-10-17.json), con citazione,
data e perimetro; il numero di pagine controllate e la
procedura umana non sono specificati. Non viene modificata la protezione,
non viene estratto il contenuto protetto e non si attribuiscono all'agente
l'ispezione visiva o un confronto dei contorni del PDF PowerPoint.

## Protocollo e osservazioni

Word apre un RTF con famiglia e dimensioni esplicite, salva un nuovo DOCX,
quindi chiude e riapre quella copia. Il corpo 12 è ereditato dallo stile
di base a 24 mezzi punti; 18/36/72 sono valori espliciti. Le intestazioni
di servizio sono Arial 10. Nel DOCX sono conservati accenti combinanti
gravi e acuti, oltre ai caratteri precomposti. La conversione da RTF al
formato DOCX può cambiare l'andata a capo del rigo ASCII: non si richiede
identità di impaginazione fra i due formati. Il documento riaperto e il
suo PDF hanno quattro pagine, senza righe perdute.

PowerPoint apre quattro slide 16:9 con testo nativo e modificabile,
senza immagini delle lettere, riduzione automatica del corpo o font
alternativi intenzionali. La preparazione del PPTX controlla struttura,
dimensioni e font dichiarato prima dell'apertura. Il corpo 72 e la famiglia
Leonardus 1270 sono ricontrollati anche nell'interfaccia dopo la riapertura.
La protezione impedisce l'ispezione ZIP del PPTX finale; il risultato del
controllo strutturale iniziale non viene attribuito alla copia protetta.

I campioni comprendono A–Z, a–z, parole moderne come Leonardo, Vinci,
Scienza, Jazz, Kilo, Uomo, Volo, Weekend, Xenon, Yoga e Zaino, le coppie
op/pq/qr/pp/qq, numeri, punteggiatura, euro, accenti italiani NFC/NFD e
b con accento combinante. Ai corpi grandi si usa una selezione più breve.
Le frasi sono prove tipografiche moderne, non trascrizioni di Leonardo.

Nei campioni applicativi osservati non si rilevano tagli, glifi mancanti,
collisioni tra lettere o accenti. Il disegno rimane volutamente irregolare;
le piccole asole sono meno evidenti a 12 punti. Questa ispezione non
certifica ogni testo, stampante, sistema operativo o applicazione.

Nel PDF Word si trovano due sottoinsiemi Leonardus con **115 contorni
non vuoti distinti ciascuno**: tutti coincidono, dopo decomposizione dei
compositi, con i glifi agli stessi indici del TTF 1.270. Sono inclusi
J/K/U/V/W/X/Y/Z e Ù. Il nome interno riporta Version 1.270. Le intestazioni
Arial sono escluse dal confronto Leonardus. Sono renderizzate e ispezionate
tutte le quattro pagine del PDF; nessuna sostituzione è osservata nel
testo campione. Il confronto riguarda i glifi incorporati, non tutti i
119 codepoint in ogni pagina o a ogni corpo.

Un processo Windows nuovo seleziona la famiglia Leonardus 1270 con GDI e
restituisce gli stessi byte del TTF previsto. È una verifica distinta dal
rendering nativo Office e dal confronto dei sottoinsiemi PDF.

## Installazione unica consolidata

Il 17 ottobre l'installazione di prova è consolidata sulla sola
**Leonardus 1270 Regular**, versione 1.270. Un processo Windows nuovo
conferma i byte esatti del TTF previsto. Sorgenti e checkpoint sono
conservati nel repository. La successiva
[denominazione finale](REGULAR_1_270_NAMING.md) distingue questo collaudo
dal font da installare oggi; per l'uso vedi la [guida](../INSTALL.md).

## Campionario da stampare

Il [campionario A4](../specimen/Leonardus-1270-Print-Specimen.pdf) contiene
quattro pagine a 12/18/36/72 punti reali. L'insieme dei testi include tutti
i 119 codepoint del repertorio concordato; i corpi grandi usano una
selezione. Il testo Leonardus è disegnato con i contorni vettoriali del TTF,
shaping HarfBuzz e nessun font di ripiego. Le etichette di servizio sono
Helvetica. Non è un'esportazione Office e non incorpora immagini storiche.
Le quattro pagine sono renderizzate e ispezionate.

Stampare in **A4, dimensioni reali / 100%, senza Adatta alla pagina**.
La linea di controllo deve misurare **50 mm**. Verificare prima il corpo
12, poi leggibilità di n/m/u, distinzione I/J/l, spaziatura p/q e accenti;
annotare eventuali parole problematiche. **Nessuna stampa fisica è stata
eseguita in questo collaudo.**

Rigenerazione senza sovrascrivere un file esistente:

```powershell
python examples/print_specimen_1270.py --out build/Leonardus-1270-Print-Specimen.pdf
python -m pytest -q tests/test_print_specimen_1270.py
```

Il test verifica identità del PDF rigenerato, quattro pagine A4, repertorio
dei testi, scala vettoriale di 50 mm, metadati e assenza di immagini o
annotazioni. Il campionario ha metadati generici e resta distinto dagli
artefatti Office locali, conservati esclusivamente sotto `build/` ignorato.

Gli [esiti strutturati](QA_OFFICE_1_270.json) conservano perimetro e limiti.
La build ripetuta è identica al TTF distribuito; audit, repertorio e proof
sono rieseguiti. Suite Windows in checkout isolato: **256 passati, 5 saltati**
per i controlli preesistenti di piattaforma/privilegi symlink.
La verifica PDF tramite Word nativo sostituisce il renderer LibreOffice,
non disponibile nell'ambiente. Nessuna nuova autenticazione paleografica,
modifica del repertorio o approvazione della pubblicazione deriva dal collaudo.
