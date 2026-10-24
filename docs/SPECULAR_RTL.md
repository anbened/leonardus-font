# Leonardus Specchio — versione speculare da destra a sinistra

Leonardus Specchio è l'**immagine speculare** di Leonardus Regular 1.270, per
comporre testo da destra a sinistra come nelle annotazioni speculari dei
manoscritti di Leonardo. È una **derivazione tecnica** del TTF corrente: non
aggiunge disegni, letture storiche o scelte umane, e non sostituisce la
Regular 1.270 né ne modifica l'approvazione. Non è una grafia autenticata né
una firma. Resta una candidata di revisione: nessuna approvazione esplicita
né diffusione pubblica è registrata.

Il file è [Leonardus-Specchio-RTL-1.270.ttf](../fonts/Leonardus-Specchio-RTL-1.270.ttf),
famiglia **Leonardus Specchio**, stile **Regular**, nome PostScript
`LeonardusSpecchio-Regular`, versione interna 1.270. La famiglia ha un nome
distinto per non confondersi con Leonardus Regular se installata insieme.

## Come è costruito

- Ogni contorno è riflesso rispetto all'asse verticale del proprio riquadro
  di avanzamento: `x → avanzamento − x`. Il verso dei contorni è invertito
  per mantenere il riempimento TrueType; i composti accentati diventano
  contorni semplici.
- Avanzamenti, metriche verticali, repertorio (119 codepoint, 121 glifi) e
  funzione `ccmp` sono quelli della 1.270. Le ancore di `mark` (accenti
  combinanti grave e acuto) sono riflesse con i contorni, quindi gli accenti
  restano sopra le loro lettere.
- I caratteri con proprietà Unicode *Bidi_Mirrored* (`( ) < > [ ] { }`)
  **non** sono riflessi nel font: in una sequenza da destra a sinistra
  l'algoritmo bidirezionale li scambia già con il partner speculare, e una
  seconda riflessione li riporterebbe al verso sbagliato.
- La tabella `DSIG`, invalidata dalla modifica, è rimossa. Il nome è
  l'unico altro cambiamento di tabella.

Il compilatore è [`leonardus.specular`](../src/leonardus/specular.py); parte
dal TTF 1.270 verificandone lo SHA256, rifiuta di sovrascrivere file
esistenti ed è riproducibile byte per byte.

## Come usarlo

Le lettere latine sono, per Unicode, caratteri da sinistra a destra: il
font da solo non cambia la direzione di un paragrafo. Per ottenere la
riga che è lo specchio esatto di quella normale, imponi la direzione:

- HTML/CSS: `direction: rtl; unicode-bidi: bidi-override;` oppure
  `<bdo dir="rtl">…</bdo>`;
- testo semplice: racchiudi la riga tra U+202E (RIGHT-TO-LEFT OVERRIDE) e
  U+202C (POP DIRECTIONAL FORMATTING), se l'applicazione le supporta.

Con la direzione imposta, anche cifre e numeri sono letti da destra a
sinistra, come nella scrittura speculare. Senza override il testo resta in
ordine sinistra-destra con lettere riflesse, e le parentesi appaiono nel
verso ordinario. La [pagina di prova](../specimen/Leonardus-Specchio-Trial.html)
usa l'override; l'[anteprima](../specimen/Leonardus-Specchio-Preview.png)
affianca le due direzioni, composte con HarfBuzz e FreeType dal font compilato.

## Verifiche

[`tests/test_specular_rtl.py`](../tests/test_specular_rtl.py) controlla che:

- la build sia riproducibile e coincida con il TTF distribuito, e non
  sovrascriva file esistenti;
- nomi, repertorio, ordine dei glifi, avanzamenti e metriche verticali
  corrispondano alla 1.270;
- ogni glifo, rasterizzato a 1000 px/em, sia l'immagine speculare di quello
  originale nel suo riquadro, salvo i caratteri *Bidi_Mirrored*;
- le ancore `mark` siano riflesse;
- una riga con lettere, accenti precomposti e combinanti, simboli e
  punteggiatura, composta da destra a sinistra, collochi ogni glifo nella
  posizione speculare esatta della riga sinistra-destra.

## Ricostruire

```powershell
$env:SOURCE_DATE_EPOCH = '0'
python examples/build_specular_rtl.py --out build/Leonardus-Specchio-RTL-1.270.ttf
python -m leonardus.cli audit --font build/Leonardus-Specchio-RTL-1.270.ttf
python -m leonardus.cli charset --font build/Leonardus-Specchio-RTL-1.270.ttf
python examples/specular_preview.py --out build/Leonardus-Specchio-Preview.png
```

Il primo file deve coincidere per SHA256 con quello in `fonts/`. Scegliere
destinazioni nuove. Contorni derivati sotto OFL 1.1; codice e documentazione
MIT.

## Limiti

La riflessione non è stata rivista visivamente da una persona come scelta di
disegno, e non è stata collaudata in Word, PowerPoint, macOS o Linux. Lo
spazio tra le lettere è quello della versione sinistra-destra riflesso, senza
nuova revisione ottica. La 1.270 non ha *kerning* e nessuno è stato aggiunto.
