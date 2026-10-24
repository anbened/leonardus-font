# Installare e provare Leonardus

Il file corrente è [Leonardus-Regular-1.270.ttf](fonts/Leonardus-Regular-1.270.ttf).
La famiglia da selezionare è **Leonardus**, lo stile **Regular** e la versione
interna **1.270**. Il font è in formato TrueType.

## Windows

1. Scarica il TTF. Se GitHub mostra la pagina del file, scegli **Download raw file**.
   Se hai scaricato un archivio ZIP, estrailo prima di aprire il font.
2. Apri il TTF e premi **Installa**, oppure usa **Installa** nel menu contestuale.
3. Chiudi e riapri Word, PowerPoint o l'applicazione in cui vuoi usarlo.
4. Seleziona **Leonardus** dall'elenco dei caratteri.

Per provare, scrivi:

> Leonardo osserva la natura: città, perché, qualità, più, così, però.
>
> ABCDEFGHIJKLMNOPQRSTUVWXYZ
>
> abcdefghijklmnopqrstuvwxyz
>
> 0123456789

Il collaudo documentato riguarda Windows e Microsoft Word/PowerPoint.
Su altri sistemi usa la consueta procedura di installazione TTF; il progetto
non dichiara prove applicative equivalenti su macOS o Linux.

## Se il font non compare o sembra una versione precedente

- Riapri l'applicazione dopo l'installazione.
- Cerca **Leonardus**, senza il numero di versione nel nome della famiglia.
- Se hai una precedente versione Leonardus, rimuovila tramite la gestione
  dei caratteri del sistema prima di installare quella nuova. Conserva prima
  i file che ti servono per eventuali confronti.
- Non installare tutti i TTF del repository: gli altri sono checkpoint
  di sviluppo e possono avere nomi di famiglia coincidenti.

## Provare senza installare

Scarica la cartella completa del repository e apri
[Prova-Leonardus.html](specimen/Prova-Leonardus.html) nel browser. La pagina
usa il TTF nella cartella `fonts/`: scrivi nel riquadro e regola la dimensione.
Il testo rimane nel browser e non viene inviato a un servizio.

Se il browser blocca il font aperto da file locale, dalla cartella del
repository puoi avviare un server locale con Python:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Apri `http://127.0.0.1:8000/specimen/Prova-Leonardus.html` sullo stesso
computer. Interrompi il server con `Ctrl+C` quando hai finito.
GitHub mostra il sorgente HTML: la prova funziona nella copia scaricata
o tramite il server locale.

## Leonardus Specchio: prova e installazione

[Leonardus Specchio](docs/SPECULAR_RTL.md) è la variante speculare opzionale
della Regular 1.270. La famiglia da selezionare è **Leonardus Specchio**,
lo stile **Regular** e la versione interna **1.270**.

### Provare nel browser senza installare

1. Dalla [pagina del repository](https://github.com/anbened/leonardus-font),
   scegli **Code > Download ZIP**.
2. Sullo ZIP scaricato scegli **Estrai tutto**. Mantieni le cartelle `fonts/`
   e `specimen/` nella stessa cartella del progetto: la pagina carica il font
   dalla cartella `fonts/`.
3. Nella cartella estratta apri `specimen/Leonardus-Specchio-Trial.html`
   con Edge o Chrome.
4. Attendi il messaggio **Font caricato: Leonardus Specchio Regular 1.270.**,
   poi scrivi nel riquadro e regola la dimensione con il cursore **Corpo**.

La [pagina di prova](specimen/Leonardus-Specchio-Trial.html) imposta già
la composizione da destra a sinistra, comprese le cifre. Il font viene
caricato dal progetto scaricato; non occorre installarlo nel sistema.
Il testo rimane nel browser e non viene inviato a un servizio.
Aprendo il collegamento HTML su GitHub si vede il sorgente: la prova
interattiva richiede la copia estratta sul computer.

Se il font non viene caricato da file locale, avvia il server Python
descritto sopra dalla cartella del progetto e apri
`http://127.0.0.1:8000/specimen/Leonardus-Specchio-Trial.html`.
Interrompi il server con `Ctrl+C` quando hai finito.

### Installare su Windows

1. Scarica [Leonardus-Specchio-RTL-1.270.ttf](fonts/Leonardus-Specchio-RTL-1.270.ttf)
   scegliendo **Download raw file** su GitHub, oppure usa lo stesso file
   nella cartella `fonts/` dello ZIP estratto.
2. Apri il TTF e premi **Installa**.
3. Chiudi e riapri Word, PowerPoint o l'applicazione in cui vuoi provarlo.
4. Seleziona **Leonardus Specchio**, stile **Regular**, dall'elenco dei caratteri.

Leonardus Specchio ha un nome di famiglia distinto e può essere installato
insieme a Leonardus Regular.

### Direzione del testo e limiti

Selezionare il font rende speculari le lettere, ma non imposta da solo
l'ordine del testo da destra a sinistra. Per una prima prova usa la pagina
nel browser, che applica già l'impostazione necessaria. Per comporre il testo
in altri contesti consulta [Come usarlo](docs/SPECULAR_RTL.md#come-usarlo).

Il collaudo applicativo della Regular non si estende automaticamente a
Specchio: per la variante non è documentato un collaudo in Word, PowerPoint,
macOS o Linux. La [guida dedicata](docs/SPECULAR_RTL.md#limiti) descrive i limiti.

## Campionario e limiti

Il [campionario A4](specimen/Leonardus-1270-Print-Specimen.pdf) contiene
quattro pagine a 12, 18, 36 e 72 punti. Per stampare scegli **100%** o
**dimensioni reali**, disattivando l'adattamento alla pagina. La stampa
fisica non è compresa nei collaudi documentati.

I caratteri assenti possono apparire con un altro font scelto dall'applicazione.
La pagina di prova li segnala. Il repertorio effettivo è registrato in
[charset_regular_v1.json](data/charset_regular_v1.json).
