# Ricompilare Leonardus Regular

## Procedura rapida per la versione corrente

Da PowerShell, nella cartella del repository, crea un ambiente separato:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
$env:SOURCE_DATE_EPOCH = '0'
.\.venv\Scripts\python.exe -m leonardus.cli build-release --version 1.270 --out build/current-integration.ttf
.\.venv\Scripts\python.exe examples/finalize_regular_1270.py --out build/current-named.ttf
.\.venv\Scripts\python.exe -m leonardus.cli audit --font build/current-named.ttf
.\.venv\Scripts\python.exe -m leonardus.cli charset --font build/current-named.ttf
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe examples/check_privacy.py
.\.venv\Scripts\python.exe examples/inventory.py --check
```

Usa destinazioni non ancora esistenti. Confronta `current-integration.ttf`
con `fonts/Leonardus-1270-Regular.ttf` e `current-named.ttf` con
`fonts/Leonardus-Regular-1.270.ttf`: devono coincidere per SHA256.
Il finalizzatore legge il checkpoint distribuito, quindi i due confronti
verificano separatamente compilazione e denominazione. Su altri sistemi
usa il Python del virtualenv con gli stessi argomenti.

Quando una modifica intenzionale aggiorna le dipendenze, verificare il diff
e rigenerare `MANIFEST.json` con `python examples/inventory.py`. Includere il
manifesto aggiornato nella stessa PR ed eseguire
`python examples/inventory.py --check` e la CI completa.

Per le PR di Dependabot verso `main`, il workflow **Dependabot inventory**
interviene dopo una CI fallita se il diff modifica soltanto file esistenti
tra `pyproject.toml`, `requirements-build.txt`, `requirements-dev.txt` e il
manifesto. Aggiorna esclusivamente dimensioni e SHA256 dei file delle
dipendenze modificati, aggiunge un commit a quella PR e avvia nuovamente
**Leonardus checks** sul ramo aggiornato. Un inventario già coerente non
produce commit o altre esecuzioni. Il controllo `verify` rimane obbligatorio
e il merge richiede ancora la normale revisione del progetto.

L'automazione usa il `GITHUB_TOKEN` temporaneo, senza credenziali aggiuntive.
Il workflow e lo script provengono dal ramo predefinito; i file della PR
vengono letti come dati tramite API, senza checkout o installazione delle
sue dipendenze nel job con scrittura. L'automazione rifiuta PR di altri autori,
fork, commit superati, file aggiunti/rimossi/rinominati, link simbolici e
modifiche ad altri sorgenti, workflow o metadati del manifesto. Questi casi
richiedono aggiornamento manuale dell'inventario. Nessuna modifica automatica
a `main`, alle approvazioni, ai font o alle impostazioni di protezione.

Per rigenerare la sola anteprima del README:

```powershell
.\.venv\Scripts\python.exe examples/publication_preview.py
```

Il comando legge il TTF corrente e aggiorna `specimen/Leonardus-Preview.png`.
Ispeziona il risultato e poi aggiorna l'inventario con
`python examples/inventory.py`. Le istruzioni seguenti conservano anche i
comandi dei checkpoint precedenti.

Il font corrente è **Leonardus**, stile **Regular**, versione interna **1.270**.
Il TTF da installare è `fonts/Leonardus-Regular-1.270.ttf`, SHA256
`0d10af2c358d9a4884e41d910cbcb789f1648073f43f048ac20eee0d5afe1201`.
La build comprende il checkpoint di integrazione e la finalizzazione del nome:

```powershell
$env:SOURCE_DATE_EPOCH = '0'
python -m leonardus.cli build-release --version 1.270 --out build/Leonardus-1270-Regular.ttf
python examples/finalize_regular_1270.py --out build/Leonardus-Regular-1.270.ttf
python -m leonardus.cli audit --font build/Leonardus-Regular-1.270.ttf
python -m leonardus.cli charset --font build/Leonardus-Regular-1.270.ttf
python examples/regular_specimen.py --font build/Leonardus-Regular-1.270.ttf --out build/proof-named-1270 --candidate
python examples/print_specimen_1270.py --out build/Leonardus-1270-Print-Specimen.pdf
```

Eseguire i comandi dopo l'installazione delle dipendenze descritta sotto,
con il Python del virtualenv. Scegliere destinazioni nuove. Il finalizzatore
verifica il checkpoint distribuito, senza cambiare contorni o spaziatura;
il primo comando ne verifica separatamente la riproducibilità. Il checkpoint
`fonts/Leonardus-1270-Regular.ttf`, famiglia Leonardus 1270, resta invariato
(SHA256 `3e1e7e6ac2416f6f321b302b46fb1b598ac04015663d731324224ce0221c240d`).
[Denominazione e verifiche](REGULAR_1_270_NAMING.md),
[integrazione delle 26 maiuscole](REGULAR_1_270.md).
Le versioni precedenti restano checkpoint preservati; i comandi seguenti
ne documentano la riproduzione e non cambiano il font corrente.

Il checkpoint 1.220 resta riproducibile con `build-release --version 1.220`;
la sua [scheda](REGULAR_1_220.md) conserva gli hash e la selezione AEMNU.

Per il checkpoint **1.210**, con o B, p A, q B, r B:

```powershell
.\.venv\Scripts\python.exe -m leonardus.cli build-release --version 1.210 --out build/Leonardus-1210-Regular.ttf
.\.venv\Scripts\python.exe -m leonardus.cli audit --font build/Leonardus-1210-Regular.ttf
.\.venv\Scripts\python.exe -m leonardus.cli charset --font build/Leonardus-1210-Regular.ttf
.\.venv\Scripts\python.exe examples/regular_spacing_check.py --font build/Leonardus-1210-Regular.ttf --out build/spacing-1210.json
.\.venv\Scripts\python.exe examples/regular_specimen.py --font build/Leonardus-1210-Regular.ttf --out build/proof-1210 --candidate
.\.venv\Scripts\python.exe examples/opqr_selection_proof.py --out build/opqr-selection.png
```

Il risultato coincide con `fonts/Leonardus-1210-Regular.ttf`, SHA256
`c10aad78edd64c9ba5ac21fc68369f824e97aa6e21b2b895e288156c044d3ef8`.
Il confronto nelle parole usa i due TTF distribuiti. Famiglia, scelta,
ricevuta e ambito della revisione sono nella [scheda 1.210](REGULAR_1_210.md).
Il default `build-release` resta 1.100 per riprodurre il checkpoint.

Usare Python 3.11 o successivo, richiesto dalla versione fissata di fontTools.
La riproduzione del TTF consegnato è
verificata su Python 3.13.9, fontTools 4.66.1 e Pillow 12.3.0, con epoca 0.
Le dipendenze fissate sono in `requirements-build.txt`; gli strumenti
di test, shaping, generazione PDF e verifica dei metadati sono in
`requirements-dev.txt`, con ReportLab 4.4.9 e pypdf 6.19.0.

Da PowerShell, nella cartella estratta:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
$env:SOURCE_DATE_EPOCH = '0'
.\.venv\Scripts\python.exe -m leonardus.cli build-release --out build/Leonardus-Regular.ttf
.\.venv\Scripts\python.exe -m leonardus.cli audit --font build/Leonardus-Regular.ttf
.\.venv\Scripts\python.exe -m leonardus.cli charset --font build/Leonardus-Regular.ttf
.\.venv\Scripts\python.exe -m pytest -q
```

Per la sola build basta installare `requirements-build.txt` al posto
di `requirements-dev.txt`. Su altri sistemi usare `python` dal proprio
virtualenv con gli stessi argomenti. `build-release` produce per default la Regular
1.100; `build-regular` produce il checkpoint alpha con metadati storici.
I comandi della demo e dei piloti richiedono input aggiuntivi non inclusi.

Per il checkpoint 1.200 usare esplicitamente la versione, conservando
il default 1.100 per riprodurre il checkpoint approvato:

```powershell
.\.venv\Scripts\python.exe -m leonardus.cli build-release --version 1.200 --out build/Leonardus-1200-Regular.ttf
.\.venv\Scripts\python.exe -m leonardus.cli audit --font build/Leonardus-1200-Regular.ttf
.\.venv\Scripts\python.exe -m leonardus.cli charset --font build/Leonardus-1200-Regular.ttf
.\.venv\Scripts\python.exe examples/regular_spacing_check.py --font build/Leonardus-1200-Regular.ttf --out build/spacing-1200.json
.\.venv\Scripts\python.exe examples/regular_specimen.py --font build/Leonardus-1200-Regular.ttf --out build/proof-1200 --candidate
.\.venv\Scripts\python.exe examples/regular_pdf_specimen.py --font build/Leonardus-1200-Regular.ttf --out build/Leonardus-1200-Specimen.pdf
```

Il TTF coincide con `fonts/Leonardus-1200-Regular.ttf`, SHA256
`5186db19d2c3def93bd8346aa512ad1de8ebf71b5171ac8444e034f0785f6bba`.
La build rifiuta la sovrascrittura dei checkpoint approvati e verifica
sorgenti, ricerca e delega; non richiede le immagini dei manoscritti.
La [scheda 1.200](REGULAR_1_200.md) descrive il tester locale e il nome
di famiglia separato. Per i campionari usare `--candidate`: la candidata
non viene etichettata come nuovo disegno visualmente approvato dall'utente.

Il SHA256 atteso è
`1f65d26ece4c8a0fe9c275fcdedfa037fab88a9687b0cd89a941d131eb899632` per la 1.100.
La [scheda di integrazione](REGULAR_1_100.md) descrive i tredici disegni
e le tre dipendenze tecniche aggiornate.

Per ricompilare il checkpoint 1.000 senza modificarne i sorgenti:

```powershell
.\.venv\Scripts\python.exe -m leonardus.cli build-release --version 1.000 --out build/Leonardus-Regular-1.000.ttf
```

Il risultato deve coincidere con
`fonts/previous/Leonardus-Regular-1.000.ttf`, SHA256
`92e3c7d22bcd34652b502b643e1efed61aedf83fac3659c29c73593d028a3d94`.
I test pubblici confrontano due build, font incluso, copertura, contorni,
licenza, shaping degli accenti e rifiuto di approvazioni/evidenze alterate.
Non sono la suite completa del repository di ricerca.

Per controllare anche i dati distribuibili e l'inventario:

```powershell
.\.venv\Scripts\python.exe examples/check_privacy.py
.\.venv\Scripts\python.exe examples/inventory.py --check
```

Per produrre nuovi campionari senza leggere documenti precedenti:

```powershell
.\.venv\Scripts\python.exe examples/regular_specimen.py --font fonts/Leonardus-Regular.ttf --out build/proof --release
.\.venv\Scripts\python.exe examples/regular_pdf_specimen.py --font fonts/Leonardus-Regular.ttf --out build/Leonardus-Specimen.pdf
```

Il generatore PDF rifiuta un percorso di output esistente. Prima di
includere un nuovo documento, esaminarne contenuto e metadati; poi aggiornare
gli hash con `python examples/inventory.py`. La CI controlla anche il PDF
incluso e la riproduzione della build con le dipendenze fissate.
Il generatore usa per default `SOURCE_DATE_EPOCH=0`, come la build del font,
per mantenere coerenti i metadati temporali fra Windows e Linux.

La build legge SVG, manifesti, registri ed estratti delle approvazioni.
Le immagini non servono per ricompilare: `validate-evidence` controlla
i metadati. `validate-evidence --check-images` richiede originali non inclusi
e non va presentato come una verifica eseguita da questo archivio.

Le ricevute precedenti conservano il loro ambito originale. La ricevuta
di integrazione del 15 ottobre approva tutti i tredici disegni e la loro
integrazione, mantenendo distinta la segmentazione storica. Versioni,
hash e derivazioni consentono di riprodurre sia la 1.000 sia la 1.100.
Le modifiche ammesse da OFL richiedono un aggiornamento coerente di sorgenti,
manifesti, versione e validazione; non vanno presentate come una nuova
approvazione umana o come grafia autenticata.


Per verificare su Windows il font effettivamente selezionato dalla
famiglia già registrata, senza installare file o modificare applicazioni:

```powershell
.\.venv\Scripts\python.exe examples/windows_font_check.py --family Leonardus --font fonts/Leonardus-Regular-1.270.ttf
```

Il confronto usa i byte restituiti da GDI e fallisce in caso di fallback
o di versione differente. Non sostituisce le [prove Office](OFFICE_1_270.md).

## Studi separati delle maiuscole

`python examples/capitals_study.py --out build/capitals-study` genera
le due serie L/A/M/N/R/S e dodici confronti isolati senza installazione.
Font sperimentali, pagina HTML e prove restano in `build/`; gli originali
non sono necessari per compilare. L’opzione `--originals` verifica gli
hash e genera le tavole locali delle fonti già acquisite, senza download.
[Metodo e comandi](CAPITALS_VARIANT_STUDY.md). Lo studio conserva il confronto con la 1.230; le scelte sono integrate dal checkpoint 1.240.

Il secondo studio si genera con:

```powershell
python examples/cdegpt_study.py --out build/cdegpt-study
```

Famiglie sperimentali CDEGPT A/B,
nessuna installazione o integrazione; [comandi e ambito](CDEGPT_VARIANT_STUDY.md).

Il terzo studio si genera con:

```powershell
python examples/bfhioq_study.py --out build/bfhioq-study
```

Famiglie sperimentali BFHIOQ A/B, versione tecnica 1.251, confrontate con il
checkpoint Regular 1.250. L’opzione `--originals` verifica i file locali e genera
le tavole senza download. [Metodo e verifiche](BFHIOQ_VARIANT_STUDY.md).

Per lo studio separato delle otto maiuscole rimanenti:

```powershell
python examples/jkuvwxyz_study.py --out build/jkuvwxyz-study
```

Famiglie sperimentali JKUVWXYZ A/B, versione tecnica 1.261, confrontate con il
checkpoint Regular 1.260. `--originals` usa soltanto gli originali
locali già acquisiti. [Metodo e comandi](JKUVWXYZ_VARIANT_STUDY.md).
