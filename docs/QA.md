# Verifiche e limiti della Regular

La candidata corrente al 17 ottobre 2026 è **Leonardus Regular 1.270**,
famiglia **Leonardus**, stile **Regular**. Il
[TTF finale](../fonts/Leonardus-Regular-1.270.ttf) conserva disegni e layout
del checkpoint 1.270: 119 codepoint, 121 glifi, tutte le 26 maiuscole selezionate
e le 26 minuscole del piano. La [verifica della denominazione](REGULAR_1_270_NAMING.md)
registra 258 test passati e 5 saltati, build riproducibili, prove raster identiche
e selezione Windows del file finale per byte.

Il [collaudo Office](OFFICE_1_270.md) e il
[rapporto strutturato](QA_OFFICE_1_270.json) distinguono le prove native
precedenti alla rinomina dalla verifica tecnica del nuovo nome e dalla
conferma umana del PDF PowerPoint. La stampa fisica resta da eseguire.
Le sezioni seguenti conservano risultati e limiti dei rispettivi checkpoint.

La [Regular 1.250](REGULAR_1_250.md) integra
C B, D B, E A, G B, P B, T B. Minuscole, sei maiuscole L/A/M/N/R/S,
avanzamenti e spazi p/q sono conservati; È/É e ancore seguono E A.
Il [rapporto 1.250](QA_1_250.json) registra build, isolamento, parole,
copertura, collisioni e installazione Windows verificata per byte.
Nessuna nuova lettura maiuscola revisionata. Prove native Office e
stampa fisica della 1.250 non sono eseguite.

Il checkpoint [Regular 1.220](REGULAR_1_220.md) integra
a A, e A, m B, n B e u B. [QA_1_220.json](QA_1_220.json) registra
le verifiche dei cinque disegni, accenti, conservazione di OPQR e spazi p/q,
coppie a cinque dimensioni e selezione Windows. La prova nativa Office
di questa versione resta da eseguire.

Il checkpoint precedente è la [Regular 1.211](REGULAR_1_211.md), con gli
spazi di p/q riequilibrati e i disegni scelti conservati nella forma.
[QA_1_211.json](QA_1_211.json) riporta geometria, ancore, metriche,
coppie a cinque dimensioni raster, prove nelle parole e selezione Windows.
Le prove native Office della 1.211 restano da eseguire.

La precedente candidata è la [Regular 1.210](REGULAR_1_210.md): integra
o B, p A, q B, r B, con ò e ancore riallineate. Il rapporto
[QA_1_210.json](QA_1_210.json) distingue le verifiche della nuova versione
dal giudizio umano sui quattro disegni e dalle prove native Office ancora
da eseguire. La selezione Windows è verificata per byte.

La precedente [Regular 1.200](REGULAR_1_200.md), con sei
completamenti ragionati e le altre venti minuscole conservate. Le prove
tecniche nuove sono distinte in [QA_1_200.json](QA_1_200.json).
La prova utente, la stampa fisica e le prove native Office 1.200 non
sono dichiarate eseguite. Il repertorio resta di 119 codepoint e 121 glifi.

Le sezioni cronologiche seguenti riguardano la [Regular 1.100](REGULAR_1_100.md), con i tredici
disegni minuscoli approvati e le dipendenze degli accenti integrate.
Le verifiche di questa versione sono riportate nelle sezioni successive;
le prove applicative seguenti riguardano il checkpoint 1.000.
Il rapporto conserva i controlli in ordine cronologico: gli stati
intermedi vanno letti insieme alle sezioni successive di completamento.

Il 13 ottobre 2026 la Regular 1.000 è stata accettata per l'uso locale
concordato in Windows, Word e PowerPoint. Disegno, leggibilità e OFL
sono stati approvati nella revisione umana.

| Verifica precedente della release | Esito documentato |
|---|---|
| Copertura e contorni | 119 codepoint, 121 glifi, 12 compositi; soli spazi vuoti; accenti combinanti ad advance zero |
| Shaping | NFC/NFD, sostituzione della i senza punto e posizionamento mark verificati |
| Spaziatura | 2.704 coppie di lettere senza sovrapposizione dell'inchiostro nelle condizioni raster dichiarate a 128 ppem |
| Word 16.0.20527 | Due pagine e 13 paragrafi dopo salvataggio/riapertura, resa della famiglia finale ispezionata |
| PowerPoint 16.0 build 20527 | Quattro slide dopo salvataggio/riapertura, resa finale ispezionata |
| Installazione Windows | Installazione nell'account Windows, rimozione e reinstallazione verificate |
| PDF Office protetti | Confronto del contenuto confermato nella revisione umana in un lettore autorizzato |
| Riproduzione | Due build da esportazione pulita identiche al TTF consegnato |

La stampa fisica non è stata eseguita: il confronto PDF era l'alternativa
prevista. Quelle prove della 1.000 non sostituiscono le successive
[prove native della 1.100](OFFICE_1_100.md). I file Office protetti e le ricevute
integrali non sono redistribuiti.

Non sono certificati autenticità paleografica, assenza di ogni collisione
ottica a tutte le dimensioni, hinting manuale, compatibilità universale o
assenza di diritti anteriori. Il repertorio è quello italiano concordato,
non l'intero Latin-1 o CP1252.

[PACKAGE_QA.json](PACKAGE_QA.json) registra le verifiche effettivamente
eseguite sul pacchetto pubblico estratto e ne distingue i risultati dalle
prove precedenti. I test pubblici riproducono un sottoinsieme tecnico,
con build, contorni, licenza, shaping e gate di provenienza.

La candidata include inoltre test di riservatezza per dati testuali,
metadati PDF anche compressi, autori personali, PDF cifrati, archivi
annidati e contenitori Office. PDF e PNG sono rigenerati dal TTF;
le quattro pagine PDF sono state renderizzate e ispezionate.
Il controllo di inventario verifica ogni file distribuibile e i suoi hash.
La [scheda di revisione](REVIEW.md) distingue queste verifiche dalla
successiva decisione sul rilascio pubblico.

## Verifica del corpus aggiuntivo

Il batch documentato in [CORPUS_EXPANSION.md](CORPUS_EXPANSION.md)
aggiunge 65 candidate, verificate contro quattro originali BNE riacquisiti
e relativi hash. Coordinate, contesti, specchiatura e corrispondenza
CSV/JSON sono controllati; il dossier locale contiene 130 PNG derivati.
I 44 record iniziali restano byte per byte invariati. La suite locale
passa con 39 test e due controlli sui symlink saltati per i privilegi
richiesti da Windows; la CI Linux esegue anche questi due controlli.
Build, audit, copertura, spaziatura e rendering sono stati rieseguiti;
il TTF ricompilato conserva lo SHA256 accettato. Le nuove candidate
non hanno ancora revisione umana.

## Verifica della ricerca mirata

Il [secondo batch](LOWERCASE_SEARCH.md) aggiunge 35 candidate verificate
contro 12 originali locali e preserva i 109 record precedenti byte per byte.
Il dossier contiene 35 schede e 70 immagini caricate correttamente nel
browser, con 35 avvisi di foliazione da revisionare. La suite locale
passa con 43 test e gli stessi due controlli sui symlink saltati su Windows;
la CI Linux li esegue. La build, l’audit, la copertura, le 2.704 coppie
di spaziatura e il rendering sono stati rieseguiti con TTF invariato.
I campioni restano proposte, non autenticazioni o nuove approvazioni.

## Verifica della revisione guidata

Il [percorso guidato](GUIDED_REVIEW.md) seleziona 61 candidate in sette
gruppi dai due batch fissati con SHA256. Il generatore controlla entrambi
i batch e i registri prima di scrivere il dossier locale: 61 schede e
183 immagini caricate nel browser, comprese le viste originali.
Navigazione, conteggi e due esportazioni JSON sono stati verificati:
una bozza con annotazione sintetica di test e una interamente vuota.
Le annotazioni di test non sono revisioni storiche e non sono state
importate; il dossier consegnato parte con tutte le scelte vuote.

La suite locale passa con 70 test e quattro controlli sui symlink saltati
per i privilegi Windows; la CI Linux esegue anche questi ultimi.
Build, audit, copertura, 2.704 coppie di spaziatura e rendering sono stati
rieseguiti. TTF, PDF ricostruito, registro delle evidenze e registro delle
fonti conservano gli stessi byte. Il controllo dei 187 file distribuibili
non rileva dati sensibili secondo le regole documentate; 64 collegamenti
Markdown locali sono stati verificati.

Il seguito della ricerca propone la concordanza 67v/BNE 131 e due nuovi
obiettivi per y. Sono indizi da revisionare, non nuove evidenze approvate.
Nessuna scansione, ritaglio o bozza di annotazioni viene distribuita.

## Registrazione del gruppo m/t — 15 ottobre 2026

La ricevuta del primo gruppo registra cinque m e cinque t, tutte con
lettura compatibile, foliazione confermata dal confronto e caso minuscolo.
Il CSV modifica soltanto i quattro campi di revisione dei dieci record:
stato, revisore, nota e data. Gli altri 134 record, il piano, i due batch,
il registro delle fonti e i contorni del font sono invariati.

La suite locale passa con 80 test e quattro controlli sui symlink saltati
per i privilegi Windows. Sono verificati esiti estranei al gruppo, bozze
presentate come ricevute, hash non corrispondenti, conferme incomplete e
discordanze con il CSV. Il checkpoint precedente resta ricostruibile e
verificato rimuovendo soltanto le revisioni registrate.

Il browser apre b/h con dieci schede registrate su 61, lascia vuote le
51 rimanenti e blocca i 40 controlli del gruppo m/t. Tutte le 183 immagini
sono caricate; l'esportazione conserva le dieci conferme senza inventare
decisioni sugli altri campioni. Build, audit, repertorio, spaziatura e
campionari sono rieseguiti con TTF e PDF identici a quelli approvati.

## Completamento dei sette gruppi — 15 ottobre 2026

Le altre 51 conferme sono registrate in sei ricevute, vincolate ai gruppi
02–07 e allo stesso piano. Il corpus contiene ora 101 campioni revisionati
e 43 candidati; nessuna revisione è estesa alle 39 candidate aggiuntive
fuori dal percorso o ai quattro dubbi iniziali.

La suite locale passa con 82 test e quattro controlli sui symlink saltati
per i privilegi Windows. Verifica l'esatta selezione di tutti i sette
gruppi, i conteggi per lettera e per batch, le ricevute e la ricostruzione
dei checkpoint. In questo passaggio cambiano soltanto i quattro campi
di revisione di 51 record; gli altri 93 record conservano i propri byte.
Il dossier completo mostra 61 schede registrate, 244 controlli bloccati
e tutte le 183 immagini. I campioni revisionati del secondo batch non
mostrano più avvisi di foliazione o caso ancora da confermare; i metadati
originali del batch restano invariati come checkpoint.

Build, audit, repertorio, spaziatura e campionari sono rieseguiti con
TTF e PDF identici a quelli approvati. Il completamento delle letture
non modifica contorni, metriche, classificazione o licenza del font.

## Segmentazioni e proposte — 15 ottobre 2026

Il [dossier di disegno](SEGMENTATION_DESIGN_REVIEW.md) comprende 61
annotazioni manuali proposte, tredici SVG principali e una s corta
alternativa. Hash, copertura degli ID, ricevute, limiti dei poligoni,
chiusura dei contorni, bounds e margini sono verificati. I campioni
conservano le proprie revisioni di lettura; segmentazioni e disegni
restano esplicitamente non approvati.

La suite locale passa con 100 test e cinque controlli sui symlink saltati
per i privilegi Windows. Le build TTF di studio sono ripetibili e hanno
famiglie distinte dalla Regular; gli output restano vincolati a build/.
Le prove raster mostrano tutte le nuove forme nel contesto del nucleo
approvato. Il browser carica 61 schede, 244 immagini, 14 anteprime SVG
e le due famiglie sperimentali per confrontare s lunga e corta.
Tutte le regioni mantenute contengono inchiostro visibile; questo controllo
non certifica che la delimitazione proposta sia corretta.

La Regular ricompilata e il suo PDF restano identici ai file approvati;
copertura, audit, spaziatura e campionari sono rieseguiti. Anche lo studio
con s lunga passa il controllo delle 2.704 coppie a 128 ppem, senza
collisioni d'inchiostro nel criterio raster dichiarato. Non è una
valutazione definitiva di ritmo, leggibilità o ancore degli accenti.
CSV, registri, ricevute delle letture e contorni della Regular restano
invariati. Immagini BNE e TTF sperimentali non sono distribuiti.


## Approvazione di dodici disegni e revisione della s — 15 ottobre 2026

La ricevuta separata vincola file, SHA256 e advance dei dodici disegni
approvati nella colonna Proposta: b, c, f, g, h, i, m, p, q, t, u, z.
I loro SVG conservano gli stessi byte. La s è rivista con una curva
inferiore ampia e terminale rientrante; la nuova forma è da confermare.
La versione precedente è conservata per il confronto, mentre la s corta
resta un'alternativa non selezionata. Le 61 segmentazioni non sono approvate.

La suite locale passa con 104 test e cinque controlli sui symlink saltati
per i privilegi Windows. I nuovi controlli impediscono di estendere la
conferma alla s o alle segmentazioni e di modificare i disegni approvati
aggiornando soltanto gli hash del manifesto. Il confronto dedicato è
riprodotto dai contorni compilati, con shaping, e verificato visivamente
per s, scienza, stesso e sasso. Il dossier carica 244 immagini su 61
schede, 15 anteprime vettoriali e mostra dodici disegni approvati e la s
ancora da confermare. Lo studio con s rivista passa le 2.704 coppie a
128 ppem senza collisioni nel criterio raster dichiarato.

Build-release, audit, repertorio, spaziatura e campionari sono rieseguiti;
TTF e PDF della Regular restano identici ai file accettati. CSV,
annotazioni, registri e ricevute delle letture restano invariati.
Inventario e controllo privacy coprono 220 file distribuibili; le
immagini BNE e i TTF sperimentali restano esclusi.


## Integrazione Regular 1.100 — 15 ottobre 2026

Tutti i tredici disegni sono approvati, compresa la nuova s con curva
inferiore. La ricevuta di integrazione conserva la prima approvazione
delle dodici forme e aggiunge s e autorizzazione all’integrazione.
Gli SVG approvati restano identici; cambiano nel font solo le tredici
minuscole e dotlessi, ì, ù. Gli altri 105 glifi mantengono contorni e
metriche. Il checkpoint 1.000 è conservato e riproducibile.

La suite locale passa con 113 test e cinque controlli sui symlink saltati
per i privilegi Windows. Verifica anche il rifiuto di approvazioni
alterate, l’identità del corpo di i senza punto, la protezione della
1.000, la corrispondenza dei tredici contorni agli SVG e gli advance.
I dodici accenti italiani NFC/NFD producono lo stesso shaping; le ancore
con grave e acuto sono verificate sulle tredici nuove basi, compresa
la sostituzione senza punto di i. Copertura: 119 codepoint, 121 glifi,
12 compositi; spazi vuoti e accenti combinanti ad advance zero.
Le metriche verticali coerenti sono 916/-254, con tutti i bounds contenuti.

Due build della 1.100 coincidono con il TTF distribuito. La ricompilazione
della 1.000 conserva lo SHA256 originale. Audit, repertorio e 2.704 coppie
a 128 ppem passano senza collisioni nel criterio raster dichiarato.
I campionari PNG a 12/18/36/72 punti e l’atlante sono rigenerati dal TTF.
Le quattro pagine del PDF sono renderizzate con Poppler e ispezionate;
metadati PDF e PNG sono verificati. Il PDF è riproducibile con epoca 0.
Il dossier storico mostra tredici disegni approvati, 61 schede,
244 immagini caricate e 15 anteprime vettoriali.

CSV, registri, annotazioni e ricevute delle letture restano invariati;
le segmentazioni storiche non sono promosse ad approvate. Non sono
ripetute installazione e prove native Word/PowerPoint sulla 1.100.
La documentazione distingue i controlli tecnici dalle prove applicative
della 1.000 e dalla successiva decisione sulla diffusione pubblica.


## Selezione Windows e avvio delle prove Office — 15 ottobre 2026

Stato intermedio, seguito dal completamento documentato nella sezione seguente.

Il sistema Windows seleziona il TTF 1.100 corretto: `GetFontData` restituisce
byte identici al font corrente, non soltanto lo stesso nome di famiglia.
Il controllo negativo con il checkpoint 1.000 è respinto. La registrazione
per il profilo è aggiornata e il file installato precedente è conservato.

Le [prove applicative](OFFICE_1_100.md) sono avviate ma non completate:
le finestre di prova non sono rimaste disponibili fino alla verifica di
salvataggio e riapertura. Word e PowerPoint risultano in versione
16.0.20527.20054; non è ancora certificato il caricamento della 1.100
nei loro motori di rendering. I documenti preesistenti restano intatti.

Sono rieseguiti i 113 test locali, con cinque controlli sui symlink saltati,
build, audit, repertorio, spaziatura e prove raster. Il TTF e gli SVG
approvati rimangono invariati. Le prove Office della 1.000 conservano
il proprio ambito; non diventano esiti positivi sulla nuova versione.

## Completamento delle prove native Office — 15 ottobre 2026

Word e PowerPoint 16.0.20527.20054 sono verificati con Leonardus Regular
1.100 su quattro pagine e quattro slide a 12, 18, 36 e 72 punti.
Salvataggio DOCX/PPTX, chiusura e riapertura riescono; tutte le pagine e
slide sono ricontrollate. Famiglia, corpi e stringhe NFC/NFD persistono
nei pacchetti OOXML. Nei campioni non si osservano tagli o collisioni.

Entrambi i PDF nativi hanno quattro pagine, renderizzate e ispezionate.
Il sottoinsieme incorporato dichiara la 1.100: gli 88 glifi non vuoti
coincidono con i contorni decomposti del TTF, comprese le sedici forme
modificate rispetto alla 1.000. Non è una verifica applicativa esaustiva
del repertorio. Protocollo, riscontri e limiti sono nelle
[prove Office](OFFICE_1_100.md); i dati sono in [PACKAGE_QA.json](PACKAGE_QA.json).

Sono ripetuti 113 test locali, con cinque skip per i symlink Windows,
build riproducibile, audit, copertura cmap, spaziatura su 2704 coppie
senza collisioni nel criterio dichiarato e campionari raster.
Font e sorgenti rimangono invariati. Documenti preesistenti intatti;
documenti Office, esportazioni native e schermate restano locali sotto
`build/`, esclusi dalla distribuzione. La stampa fisica resta da verificare.

## Studio delle maiuscole L/A/M/N/R/S — 16 ottobre 2026

Le dodici proposte restano separate dalla Regular 1.230. Il
[rapporto dello studio](CAPITALS_VARIANT_STUDY.md) e il
[registro QA](QA_CAPITALS_STUDY_2026-10-16.json) documentano isolamento dei
contorni, accenti, build riproducibile, repertorio, prove a quattro corpi
e controllo delle 2.704 coppie per serie a cinque dimensioni. Nessuna
nuova lettura maiuscola revisionata o approvazione di integrazione. Le
minuscole, il TTF corrente e le precedenti prove mantengono il proprio ambito.

## Confronto C/D/E/G/P/T — 16 ottobre 2026

Dodici proposte separate dalla 1.240: [metodo e limiti](CDEGPT_VARIANT_STUDY.md),
[esiti QA](QA_CDEGPT_STUDY_2026-10-16.json). Conservati minuscole, L/A/M/N/R/S
appena integrate e tutti gli avanzamenti; È/É e ancore seguono la E sperimentale.
Nessuna installazione delle proposte o nuova lettura maiuscola revisionata.

## Confronto B/F/H/I/O/Q — 16 ottobre 2026

Dodici proposte separate dalla 1.250: [metodo e limiti](BFHIOQ_VARIANT_STUDY.md),
[esiti QA](QA_BFHIOQ_STUDY_2026-10-16.json). Conservati tutti gli avanzamenti,
le minuscole e le dodici maiuscole già scelte; Ì/Ò e ancore seguono le basi
sperimentali. Riproducibilità, isolamento, accenti, audit, repertorio,
2.704 coppie per serie a cinque corpi e prove di parole a quattro corpi.
Nessuna installazione, approvazione di integrazione o nuova lettura storica.

## Regular 1.260 e confronto J/K/U/V/W/X/Y/Z — 16 ottobre 2026

La [1.260](REGULAR_1_260.md) integra B/F/H/O/Q B e I A, con H B esplicita.
[Esiti QA](QA_1_260.json): contorni scelti esatti, Ì/Ò e ancore riallineati,
avanzamenti, minuscole e dodici capitali precedenti conservati. Prove nelle
parole e su 2.704 coppie a cinque dimensioni; installazione per utente Windows
e selezione GDI verificata per byte, anche da un nuovo processo. Prove native
Office 1.260 e stampa fisica non dichiarate.

Lo [studio delle otto maiuscole rimanenti](JKUVWXYZ_VARIANT_STUDY.md) mantiene
la 1.260 come base: sedici proposte non approvate e dipendenza Ù, senza
installazione. Riproducibilità, isolamento, accenti, conservazione degli stati
storici e [rapporto QA](QA_JKUVWXYZ_STUDY_2026-10-16.json) distinti dall’integrazione.

## Regular 1.270 — chiusura delle 26 maiuscole, 16 ottobre 2026

La [1.270](REGULAR_1_270.md) integra tutte le otto B di J/K/U/V/W/X/Y/Z;
J/W/Y/Z B prevalgono sui suggerimenti A. Otto contorni esatti e Ù riallineata,
altre forme e avanzamenti conservati. Il nuovo controllo confronta tutte le
26 capitali con le quattro selezioni disgiunte, oltre a riproducibilità,
compositi, accenti NFC/NFD, audit, repertorio e 2.704 coppie a cinque corpi.
Prove nelle parole a 12/18/36/72 pt. [Esiti](QA_1_270.json).
Installazione per utente Windows e selezione GDI verificata per byte anche
da un processo nuovo. Al 16 ottobre Office 1.270, stampa fisica e parere
paleografico indipendente restavano da effettuare; aggiornamento seguente.

## Collaudo Office 1.270 e campionario A4 — 17 ottobre 2026

Word e PowerPoint 16.0.20527.20066: quattro pagine/slide a 12/18/36/72 pt,
salvataggio nativo, chiusura e riapertura verificati. Ispezionati tutti i
campioni riaperti, senza tagli o collisioni osservati. Il PDF Word ha quattro
pagine ispezionate e due sottoinsiemi con 115 contorni Leonardus distinti
ciascuno, tutti coincidenti con il TTF 1.270, comprese le ultime otto capitali
e Ù. Il PDF PowerPoint è esportato con protezione aziendale e il suo
contenuto è successivamente confermato dall'utente il 17 ottobre, nella
[ricevuta umana](../data/human_office_pdf_review_2026-10-17.json).
Non viene attribuita all'agente la revisione del PDF protetto o il confronto
dei suoi contorni; la pagina di avviso non prova il rendering delle slide.

Il nuovo campionario A4 ha quattro pagine a dimensioni reali, testi che
includono tutti i 119 codepoint e linea di scala 50 mm. Rigenerazione
deterministica, controllo geometrico e ispezione delle quattro pagine.
Suite Windows in checkout isolato: 256 passati, 5 saltati per controlli
preesistenti di piattaforma/privilegi symlink. Build 1.270 identica,
audit, repertorio e proof ripetuti. Font, repertorio, contorni e registro
storico invariati. [Rapporto](OFFICE_1_270.md), [esiti strutturati](QA_OFFICE_1_270.json).
Gli artefatti Office rimangono ignorati sotto `build/`; il campionario
distribuibile ha metadati generici. Stampa fisica non eseguita.

Nella stessa data è consolidata l'installazione Windows sulla sola
Leonardus 1270 Regular: rimossi 12 file precedenti e 11 registrazioni,
senza errori; cartelle e registro utente/sistema ricontrollati. Un processo
nuovo verifica i byte della 1.270 e l'indisponibilità delle undici famiglie
precedenti. Sorgenti e checkpoint nel repository rimangono invariati.

## Denominazione Leonardus / Regular — 17 ottobre 2026

La [scelta umana del nome](../data/human_family_naming_review_2026-10-17.json)
mantiene la versione interna 1.270 e seleziona famiglia Leonardus, stile
Regular. Il nuovo TTF [Leonardus-Regular-1.270.ttf](../fonts/Leonardus-Regular-1.270.ttf)
conserva tutte le tabelle estranee al nome, con la sola necessaria variazione
del checksum in `head`. Contorni, cmap, metriche e tabelle OpenType sono
identici; il checkpoint Leonardus 1270 e i suoi esiti Office rimangono intatti.
[Verifiche e installazione](REGULAR_1_270_NAMING.md).
