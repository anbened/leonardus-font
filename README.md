# Leonardus

**Un carattere contemporaneo ispirato alla grafia documentata di Leonardo da Vinci.**

Leonardus Regular porta un lavoro di ricerca e disegno tipografico in un font
leggibile da sinistra a destra. Puoi scaricarlo e usarlo nei tuoi documenti,
oppure esplorarne i sorgenti e il percorso di realizzazione.

**[Font TTF 1.270](fonts/Leonardus-Regular-1.270.ttf)** ·
**[Installazione](INSTALL.md)** ·
**[Campionario PDF](specimen/Leonardus-1270-Print-Specimen.pdf)**

![Leonardus Regular 1.270: parole, alfabeti e accenti](specimen/Leonardus-Preview.png)

## Scaricare e installare

1. Apri [Font TTF 1.270](fonts/Leonardus-Regular-1.270.ttf) e premi
   **Download raw file** nella pagina
   GitHub per salvare `Leonardus-Regular-1.270.ttf`.
2. Su Windows apri il file e scegli **Installa**.
3. Riapri l'applicazione e seleziona **Leonardus**, stile **Regular**.

Per installare Leonardus basta questo **singolo TTF**. Gli altri font nella
cartella `fonts/` sono checkpoint conservati per confronto.
Il font non richiede Python o altri strumenti di sviluppo per essere usato.
La [guida](INSTALL.md) comprende la prova locale nel browser e i problemi più
comuni. Il PDF mostra il carattere a 12, 18, 36 e 72 punti.

## Cosa contiene il font

La versione **1.270** comprende un solo stile Regular, con 119 caratteri
Unicode e 121 glifi: le 26 minuscole, le 26 maiuscole, le cifre, gli accenti
italiani, punteggiatura e simboli selezionati, compreso l'euro.
Sono supportati anche gli accenti combinanti grave e acuto.

Il repertorio è pensato per l'italiano e il latino di base. Non copre tutte
le lingue che usano l'alfabeto latino. La compatibilità è stata verificata
su Windows, Word e PowerPoint nel perimetro del
[rapporto di collaudo](docs/OFFICE_1_270.md); macOS e Linux non hanno qui
un collaudo applicativo documentato.

## Versione speculare da destra a sinistra

[Leonardus Specchio](docs/SPECULAR_RTL.md) è l'immagine speculare della 1.270
per comporre testo da destra a sinistra, come nelle annotazioni speculari
dei manoscritti. È una derivazione tecnica, non una nuova scelta di
disegno né una grafia autenticata, e non sostituisce Leonardus Regular.
[TTF](fonts/Leonardus-Specchio-RTL-1.270.ttf) ·
[Anteprima](specimen/Leonardus-Specchio-Preview.png) ·
[Prova nel browser](specimen/Leonardus-Specchio-Trial.html).

## Dalle fonti al disegno

La ricerca parte da campioni del **Codice Madrid I, Biblioteca Nacional de
España, MSS/8937**. I registri collegano i campioni ai folii e mantengono
esplicite le letture dubbie.

Nella 1.270, venti minuscole hanno riferimenti documentati a letture storiche
revisionate; le altre sei (`j k v w x y`) sono completamenti contemporanei
ragionati. Anche maiuscole, cifre e segni necessari all'uso moderno sono
disegni contemporanei dichiarati. Il passaggio dai campioni al font comprende
scelte di forma, peso, raccordo e spaziatura.

**Leonardus è una reinterpretazione contemporanea documentata.** Non è una
grafia autenticata o una firma ricostruita di Leonardo, e non ha avallo museale.
La [guida al progetto](docs/PROJECT.md) spiega il metodo, il ruolo dell'AI e
la distinzione tra evidenza storica e scelte di disegno.

## Dentro il repository

Il comando GitHub **Code > Download ZIP** scarica l'intero progetto, con
sorgenti, documentazione e prove. Serve a chi vuole esplorare o ricostruire
il font; per installarlo basta il TTF indicato sopra.

| Percorso | Contenuto |
|---|---|
| `fonts/` | TTF corrente e checkpoint per confronti e controlli. Per installare Leonardus usa solo `Leonardus-Regular-1.270.ttf`; `Leonardus-Specchio-RTL-1.270.ttf` è la derivazione speculare opzionale. |
| `specimen/` | Campionario PDF, anteprima e prova HTML locale; tavole degli studi precedenti. |
| `glyphs/` | Contorni SVG, manifesti e varianti di disegno. |
| `data/` | Provenienza, classificazioni ed estratti delle decisioni. |
| `src/`, `examples/`, `tests/` | Compilatore Python, strumenti di verifica e test. |
| `docs/` | Metodo, derivazione dei glifi, licenze, verifiche e documenti delle versioni. |

La build funziona dai sorgenti inclusi, senza immagini dei manoscritti e
senza API AI. Le riproduzioni museali e i documenti Office di lavoro non
sono distribuiti. I checkpoint e le relative decisioni mantengono il loro
ambito originale: la loro presenza non li rende versioni correnti.

## Usare e modificare Leonardus

Il font e i sorgenti dei contorni sono sotto **SIL Open Font License 1.1**.
Codice, metadati originali e documentazione sono sotto **MIT**. Puoi usare
il font anche in progetti commerciali, secondo le condizioni OFL. I documenti
composti con Leonardus non devono adottare la licenza del font.

Leggi [OFL.txt](OFL.txt), [LICENSE-MIT.txt](LICENSE-MIT.txt) e gli
[ambiti delle licenze](docs/LICENSES.md). I riferimenti alle fonti non
concedono diritti sulle riproduzioni dei manoscritti.

## Approfondire e contribuire

- [Indice della documentazione](docs/README.md).
- [Derivazione per glifo della 1.270](docs/DERIVAZIONE_1_270.csv).
- [Ricostruire il font e verificare il pacchetto](docs/BUILDING.md).
- [Crediti e attribuzione](CREDITS.md).
- [Note sulla versione 1.270](CHANGELOG.md).
- [Segnalare problemi e proporre contributi](CONTRIBUTING.md).

Per una segnalazione indica testo di prova, applicazione, sistema operativo
e versione del font. Gli ampliamenti del repertorio e gli altri stili
richiedono nuove scelte di disegno e verifiche.
