# Verifica Windows e prove Office della Regular 1.100

15 ottobre 2026. **Prove native completate in Word e PowerPoint su
Windows: quattro pagine e quattro slide a 12, 18, 36 e 72 punti,
salvataggio, chiusura, riapertura ed esportazione PDF verificati.**
I risultati riguardano i campioni e le versioni applicative indicati.

## Esito verificato su Windows

La registrazione per il profilo Windows è aggiornata dalla 1.000 alla
1.100. Il file precedente è conservato. Il controllo non si limita al
nome della famiglia o al percorso registrato: crea un contesto GDI,
richiede Leonardus Regular e legge con `GetFontData` l’intero font
selezionato dal sistema.

I byte ottenuti coincidono con
[Leonardus-Regular.ttf](../fonts/Leonardus-Regular.ttf), versione
`Version 1.100; contemporary LTR Regular`, SHA256
`1f65d26ece4c8a0fe9c275fcdedfa037fab88a9687b0cd89a941d131eb899632`.
Il confronto negativo con il checkpoint 1.000 viene correttamente
respinto: lo stesso nome di famiglia non basta per superare il controllo.

Il controllo è ripetibile su Windows con il font già registrato:

```powershell
.\.venv\Scripts\python.exe examples/windows_font_check.py
```

Lo [strumento](../examples/windows_font_check.py) non installa font e non
modifica le applicazioni. Restituisce codice 0 solo se i byte selezionati
coincidono con il TTF atteso; il rapporto resta sotto `build/`.
Non è una verifica del motore di rendering o della cache di Office.

## Stato delle prove applicative

Le prove sono eseguite con Word e PowerPoint 16.0.20527.20054 in documenti
separati. Word apre un campione RTF con famiglia e corpi espliciti e lo
salva in DOCX; PowerPoint apre quattro slide con caselle di testo native
e salva una nuova copia PPTX. Entrambi i file vengono chiusi e riaperti.
Le quattro pagine e le quattro slide sono ricontrollate nelle applicazioni.

| Verifica 1.100 | Word | PowerPoint |
|---|---|---|
| Versione del programma rilevata | 16.0.20527.20054 | 16.0.20527.20054 |
| Applicazione del font e confronto visuale | Superati, quattro corpi | Superati, quattro corpi |
| Salvataggio e riapertura | DOCX, superati | PPTX, superati |
| Verifica di tutte le pagine o slide | Quattro pagine | Quattro slide |
| Esportazione nativa e confronto | PDF, quattro pagine | PDF, quattro pagine |

Nei campioni osservati non si rilevano tagli, collisioni degli accenti o
sostituzioni visibili. La curva inferiore della nuova s resta visibile
anche nelle parole «scienza stesso sasso». A 36 e 72 punti Word manda
alcune righe a capo entro i margini A4, mantenendo quattro pagine e il
corpo impostato. Le slide conservano i corpi senza riduzione automatica.

L'ispezione dei pacchetti OOXML conferma Leonardus e i corpi previsti:
nel DOCX 12 punti sono il valore predefinito, con 18, 36 e 72 punti
espliciti; nel PPTX sono espliciti tutti e quattro i corpi. Le stringhe
attese, comprese le sequenze NFC e NFD, persistono nel DOCX. Tutti i testi
delle quattro slide coincidono esattamente prima e dopo il salvataggio.

## Riscontro sui PDF nativi

Le otto pagine esportate sono renderizzate con Poppler e ispezionate
singolarmente. Entrambi i PDF incorporano un sottoinsieme TrueType con
versione `Version 1.100; contemporary LTR Regular` e SHA256
`535829dc8420ea65cc447f30de96f37c35c354f9dfdce06ad2b2a905bef5c649`.
Il sottoinsieme non ha lo stesso hash del TTF completo.

Il confronto usa gli indici dei glifi preservati nei sottoinsiemi Office
e i contorni decomposti con fontTools, risolvendo le componenti. Tutti
gli **88 glifi non vuoti** incorporati coincidono con il font corrente:
zero discrepanze, comprese tutte le tredici minuscole integrate, dotless i,
ì e ù. Queste sedici forme distinguono la prova dalla versione 1.000.
Il nome della famiglia, da solo, non è usato come prova della versione.

Il campione applicativo comprende alfabeti, numeri, punteggiatura scelta,
accenti italiani NFC/NFD e combinazioni b con grave/acuto, i con grave/acuto
e u con grave. Non è una prova applicativa esaustiva dei 119 codepoint:
la copertura completa resta oggetto del controllo cmap e dell'atlante.

Le prove della 1.000 conservano il proprio ambito nel [rapporto QA](QA.md).
Il TTF, i sorgenti e gli SVG approvati restano invariati. Non sono
verificate stampa fisica, altre versioni di Office, altri sistemi operativi,
incorporamento nei documenti Office o compatibilità universale.

## Protocollo ripetibile

Usare soltanto nuovi documenti di prova nella cartella locale ignorata
`build/office-1.100/`. Lasciare intatti i documenti già aperti.

1. Impostare esplicitamente Leonardus Regular nelle aree di prova.
   Preparare quattro pagine Word e quattro slide PowerPoint con campioni
   a 12, 18, 36 e 72 punti, senza riduzione automatica del corpo previsto.
2. Includere tutte le tredici nuove minuscole `b c f g h i m p q s t u z`,
   l’alfabeto completo, numeri e un campione di punteggiatura. Nel testo
   confrontare «bambino macchina panni ghiaccio quaderno» e
   «scienza stesso sasso», con attenzione alla curva inferiore di s.
3. Confrontare `à è é ì ò ù À È É Ì Ò Ù` in NFC e NFD. Verificare
   separatamente i con grave/acuto senza punto aggiuntivo, u con grave
   e i campioni b con accento combinante. Controllare tagli, collisioni,
   sostituzioni e leggibilità nei corpi scelti.
4. Salvare DOCX e PPTX, chiudere soltanto le finestre di prova e riaprire
   i file. Ricontrollare famiglia, corpi, contenuto, numero di pagine o
   slide e resa di tutti i campioni.
5. Completare la verifica con esportazioni native, quando disponibili,
   e confrontarle con il TTF corrente. Registrare separatamente limiti
   di esportazione, stampa fisica e compatibilità non verificata.

Pubblicare soltanto esiti e metadati tecnici essenziali. Documenti
Office, esportazioni applicative, schermate con account e log contenenti
percorsi personali restano locali e non entrano nel pacchetto.
I risultati correnti sono in [PACKAGE_QA.json](PACKAGE_QA.json).
