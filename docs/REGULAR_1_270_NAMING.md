# Leonardus / Regular — denominazione della 1.270

17 ottobre 2026. La [scelta umana](../data/human_family_naming_review_2026-10-17.json)
seleziona **Leonardus** come famiglia, **Regular** come stile e **1.270** come
versione interna. Il font da installare è
[Leonardus-Regular-1.270.ttf](../fonts/Leonardus-Regular-1.270.ttf).

| Campo | Valore |
|---|---|
| Famiglia, name ID 1 e 16 | Leonardus |
| Stile, name ID 2 e 17 | Regular |
| Nome completo, name ID 4 | Leonardus Regular |
| Versione, name ID 5 | Version 1.270 |
| Nome PostScript, name ID 6 | Leonardus-Regular |
| Versione in head | 1.270, invariata |

SHA256 del TTF rinominato:
`0d10af2c358d9a4884e41d910cbcb789f1648073f43f048ac20eee0d5afe1201`.

Il [checkpoint precedente](../fonts/Leonardus-1270-Regular.ttf), famiglia
Leonardus 1270, resta invariato, con SHA256
`3e1e7e6ac2416f6f321b302b46fb1b598ac04015663d731324224ce0221c240d`.
La [build dell'integrazione](../glyphs/regular/release-1.270.json), gli hash
dei disegni selezionati, le ricevute umane e gli [esiti Office](OFFICE_1_270.md)
mantengono il loro riferimento originale. Non sono riscritti retroattivamente.

## Verifiche della rinomina

Il nuovo file differisce soltanto nella tabella `name` e nel checksum
`head.checkSumAdjustment` necessario al nuovo contenuto. Ogni altra tabella
e ogni altro campo di `head` sono identici. Rimangono **119 codepoint e
121 glifi**, gli stessi contorni, avanzamenti, margini, accenti, kerning e
funzioni OpenType. Nessuna modifica di disegno, lettura o autenticità.

Due build indipendenti producono gli stessi byte del TTF distribuito.
I controlli confrontano tutte le tabelle estranee al nome, rifiutano una
ricevuta con perimetro alterato e impediscono la sovrascrittura di file
esistenti. Lo shaping di parole, coppie e accenti è identico a 12/18/36/72 pt.
Le cinque immagini HarfBuzz/FreeType — quattro corpi e atlante del repertorio —
sono identiche pixel per pixel rispetto al checkpoint. Audit e repertorio
sono rieseguiti sul TTF rinominato.
Suite Windows in checkout isolato: **258 passati, 5 saltati** per i controlli
preesistenti di piattaforma/privilegi symlink.

Il [campionario A4](../specimen/Leonardus-1270-Print-Specimen.pdf) rimane
identico per byte, SHA256
`165e2418c3cc5a4633415b0764378c64f7416b7a9d30fae1025a7d431d74584b`:
usa i contorni vettoriali ed etichette Leonardus Regular 1.270, senza
incorporare il nome precedente. La sua build usa ora il TTF rinominato.
La [pagina di prova](../specimen/Leonardus-1270-Trial.html) carica e offre
in download lo stesso file finale.

## Installazione Windows

Installata e registrata per l'utente **Leonardus Regular**, versione interna
1.270. Il file e la registrazione con famiglia Leonardus 1270 sono rimossi.
L'inventario delle cartelle e dei registri font utente/sistema trova un solo
file del progetto e una sola registrazione: Leonardus Regular. Nessuna
installazione del progetto a livello di sistema.

Un processo Windows nuovo richiede **Leonardus** e ottiene esattamente
i byte del nuovo TTF; la vecchia famiglia Leonardus 1270 non è più selezionabile.
Windows riceve la notifica del cambiamento. Riaprire le applicazioni già
avviate per aggiornare l'elenco dei font e selezionare **Leonardus**, Regular.
Il checkpoint 1.100 nel repository usa anch'esso famiglia Leonardus: è un
riferimento conservato e non va installato insieme alla 1.270.

Il collaudo Office documentato precede la rinomina; non viene dichiarata
una nuova esecuzione completa di Word/PowerPoint sul TTF rinominato. La
conservazione dei contorni e delle tabelle di layout è verificata separatamente.
Stampa fisica e pubblicazione di una release restano decisioni distinte.
[Esiti strutturati](QA_NAMING_1_270.json).

```powershell
python -m leonardus.cli build-release --version 1.270 --out build/Leonardus-1270-Regular.ttf
python examples/finalize_regular_1270.py --out build/Leonardus-Regular-1.270.ttf
python -m leonardus.cli audit --font build/Leonardus-Regular-1.270.ttf
python -m leonardus.cli charset --font build/Leonardus-Regular-1.270.ttf
python examples/windows_font_check.py --family Leonardus --font fonts/Leonardus-Regular-1.270.ttf
```

Il finalizzatore usa il checkpoint distribuito e ne verifica l'hash; il
primo comando ne ripete la build separatamente. Scegliere destinazioni nuove.
Contorni originali OFL 1.1; codice e documentazione MIT.
