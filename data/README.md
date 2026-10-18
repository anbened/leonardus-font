# Metadati pubblici e copie di revisione

`human_jkvwxy_integration_review_2026-10-16.json` registra la scelta
esplicita j A, k B, **v B**, w B, x B, y B, distinta dal suggerimento
precedente dell'agente. `glyphs/regular/release-1.230.json` vincola i sei
SVG, le metriche e la ricevuta alla build. Il manifesto dello studio
resta nel suo stato preparatorio; i sei glifi conservano la categoria
`reasoned_completion` e il registro delle evidenze non cambia.

`jkvwxy_variant_study_2026-10-16.json` vincola dodici proposte separate
alla 1.220 e ai confronti già documentati: sei candidate j/v/x/y e tre
contesti K, senza promozione a nuove letture o k minuscole. Registra
ricerche aggiuntive e consultazioni online come piste non usate per
geometria primaria. W resta una sintesi senza campione diretto; tutte
le varianti sono completamenti non approvati. Il CSV storico non cambia.

La correzione metrica 1.211 è registrata in
`glyphs/regular/release-1.211.json`: istruzione ricevuta, font di base,
traslazioni e spazi laterali prima/dopo. Le forme scelte, le ricevute e
il registro storico restano invariati. Non si registra una nuova
approvazione visuale umana delle metriche.

## Completamento delle 26 minuscole - 1.200

`completion_authorization_2026-10-15.json` registra la delega e il
perimetro delle 26 minuscole, senza fingere approvazioni visuali individuali.
`agent_segmentation_review_2026-10-15.json` aggiunge 32 pareri attribuiti
all'agente ai 29 esiti umani già registrati; tutte le 61 segmentazioni
hanno una valutazione. `originals_recovery_2026-10-15.json` documenta il
recupero di file già acquisiti per hash, senza distribuire le immagini.

`research_assessment_2026-10-15.json` valuta dieci candidate e tre
osservazioni K senza promuovere il CSV storico. Il manifesto
`lowercase_completion_2026-10-15.json` vincola sei nuovi contorni originali
e i confronti contestuali: sono completamenti contemporanei ragionati,
non sei nuove letture storiche approvate. Il registro resta a 144 campioni,
101 revisionati e 43 candidati. I checkpoint precedenti restano invariati.

Le sezioni seguenti descrivono la storia delle esportazioni e dei batch.

I CSV conservano il registro delle fonti e i 44 campioni iniziali,
con fonte, folio, coordinate, orientamento, hash immagine e stato
di revisione conservati. Il campo revisore diventa `Human review`;
le etichette di attribuzione diventano `Decisione registrata`.
Citazioni, date e contenuto delle decisioni non vengono modificati;
gli stati non vengono promossi o reinterpretati.
Eventuali riferimenti testuali della cronologia originale restano
contesto, senza implicare che quei documenti siano nell'archivio.
`candidate_context.json` conserva i contesti del dossier iniziale,
con le proprie diciture candidate; lo stato corrente è nel CSV delle evidenze.

Le due ricevute JSON sono estratti delle decisioni reali: status,
data, approvazione M2, mappatura dei folii, approvazione del disegno
e scelta OFL. Non contengono thread ID, dettagli d'installazione
o autorizzazioni per altri documenti. Le frasi di approvazione
richieste dal compilatore rimangono visibili in questi due file.

Il manifesto della release cambia soltanto l'hash della ricevuta
ridotta; il manifesto dei glifi e i contorni restano quelli di
origine. Questa trasformazione è esplicita in MANIFEST.json e
non modifica geometria, metriche o tabelle del TTF.

Non sono incluse immagini. I percorsi relativi verso `scans/`
sono riferimenti per identificare gli originali, non file mancanti
necessari alla build. La verifica degli originali richiede di
acquisirli separatamente nel rispetto dei diritti e dei loro hash.

## Nuove candidate

`lowercase_expansion_2026-10-14.json` documenta 65 nuove candidate,
aggiunte in fondo al CSV senza cambiare i 44 record iniziali. Il totale del primo ampliamento
era 109, con 40 identificazioni già confermate. Le nuove righe hanno
inizialmente campi di revisione vuoti e confidenza non stimata (0.0). Il JSON contiene
contesti, trasformazioni, priorità e motivazioni; la
[guida di revisione](../docs/CORPUS_EXPANSION.md) spiega acquisizione locale
e generazione del dossier. Questi campioni non modificano i manifesti
o la classificazione dei glifi della Regular 1.000.

## Ricerca mirata successiva

`lowercase_search_2026-10-14.json` conserva 35 nuove candidate e il registro
delle ricerche, delle concordanze dei folii e di quattro osservazioni
escluse dalle evidenze di minuscole. Il totale del CSV è 144:
al checkpoint del secondo batch le 40 identificazioni confermate e i
109 record precedenti restavano invariati. I nuovi folii sono riferimenti di lavoro
da revisionare, dichiarati sia nelle note CSV sia nel dossier.
La [guida alla ricerca mirata](../docs/LOWERCASE_SEARCH.md) distingue
forma osservata, associazione proposta, etichetta tecnica e normalizzazione.

## Piano di revisione e seguito della ricerca

`guided_review_2026-10-14.json` seleziona 61 candidate dei due batch in
sette gruppi, con ID, motivazioni, domande e SHA256 dei batch. Lo stato
rimane `pending_human_review`: non è una ricevuta di approvazione.
`research_followup_2026-10-14.json` registra una proposta di concordanza
67v/BNE 131 e nuovi obiettivi per y, senza nuove righe nel CSV.
La [revisione guidata](../docs/GUIDED_REVIEW.md) descrive generazione locale,
esportazione delle bozze e significato dei campi. Le bozze e le immagini
restano fuori dai file distribuibili; nessuna decisione viene importata
automaticamente.

## Revisione registrata del primo gruppo

`human_guided_review_2026-10-15_group-01.json` registra dieci decisioni
esplicite: cinque m e cinque t, tutte compatibili, con foliazione
confermata dal confronto e caso minuscolo. Il CSV aggiorna soltanto
stato, revisore generico, nota e data di questi dieci record. Questo primo
passaggio portava a 50 campioni revisionati e 94 candidati; la confidenza numerica
non viene trasformata in una probabilità o modificata.

Batch e piano conservano i rispettivi byte e hash. I controlli ricostruiscono
il checkpoint precedente rimuovendo soltanto i campi di revisione coperti
dalla ricevuta, senza ignorare cambi a fonti, coordinate o letture proposte.
Il dossier precompila le conferme registrate.
Le nuove bozze esportate restano annotazioni da controllare, non ricevute.

## Completamento della revisione guidata

Le ricevute `human_guided_review_2026-10-15_group-02.json` fino a
`human_guided_review_2026-10-15_group-07.json` registrano le altre 51
conferme. Tutte le 61 schede del piano hanno lettura compatibile,
foliazione confermata dal confronto e caso minuscolo. Il totale corrente
è 101 campioni revisionati e 43 candidati: 39 esclusi dal percorso negli
ampliamenti e quattro dubbi iniziali. I sette gruppi restano distinti;
nessuna conferma è estesa a campioni non selezionati.

Il CSV conserva tutte le coordinate, le fonti, le confidenze e gli altri
campi originari; le revisioni cambiano solo i quattro campi previsti.
Il dossier mostra il completamento e le schede registrate sono bloccate.
La revisione dei disegni è registrata separatamente dalle letture.

## Segmentazioni e proposte di disegno

`lowercase_design_2026-10-15.json` registra tredici disegni principali,
la s precedente e l'alternativa corta non selezionata, con hash di piano,
evidenze, annotazioni e SVG.
`human_lowercase_design_review_2026-10-15.json` vincola file, hash e advance
delle dodici proposte approvate: b, c, f, g, h, i, m, p, q, t, u, z.
Questa prima ricevuta riguarda soltanto dodici scelte di disegno.
`human_lowercase_integration_review_2026-10-15.json` registra poi
l’approvazione della nuova s e l’integrazione dei tredici disegni nel
font, vincolando tutti gli SVG e gli advance. La prima ricevuta rimane
immutata e collegata con SHA256. Le segmentazioni storiche non sono approvate.
Il timestamp registra la registrazione della decisione, non l'ispezione. I tre JSON sotto
`segmentation/` conservano regioni e tagli manuali proposti per i 61 ID
già revisionati. Le coordinate sono locali al crop specchiato 1×;
non sono contorni autenticati o segmentazioni già approvate.
CSV e ricevute delle letture restano invariati. La Regular 1.100
integra i disegni approvati; la 1.000 è conservata come checkpoint.
La [guida](../docs/SEGMENTATION_DESIGN_REVIEW.md) distingue annotazioni,
ridisegno contemporaneo e futura revisione visuale.

## Studio OPQR

`human_opqr_integration_review_2026-10-15.json` registra la successiva
scelta umana o B, p A, q B, r B, con i quattro hash e il proprio ambito.
`glyphs/regular/release-1.210.json` vincola questa integrazione alla 1.200.
Lo studio iniziale conserva i propri stati, senza trasformare una scelta
di disegno in nuove approvazioni storiche o in un'approvazione generale.

`opqr_variant_study_2026-10-15.json` registra il confronto di 22 campioni
già revisionati e otto proposte di disegno separate, con hash dei sorgenti,
coordinate, limiti e ancore principali. Non modifica il CSV storico o le
ricevute umane; le famiglie A/B sono studi non approvati per il confronto
nelle parole, distinti dalla candidata 1.200. Le immagini restano locali.

Lo studio `aemnu_variant_study_2026-10-15.json` documenta dieci proposte
non approvate per a/e/m/n/u, 27 localizzazioni esistenti, la ricerca del
dettaglio senza nuove acquisizioni ad alta risoluzione e le piste escluse
dal disegno. Non promuove letture o segmentazioni e conserva il CSV storico.

La ricevuta `human_aemnu_integration_review_2026-10-15.json` registra
la scelta umana a A, e A, m B, n B, u B. Il manifesto di release 1.220
vincola i cinque SVG e la tavola mostrata. Lo studio originario conserva
il proprio stato preparatorio, il CSV storico conserva gli stessi byte.

## Studio esplorativo delle maiuscole

`capitals_variant_study_2026-10-16.json` vincola dodici SVG, il TTF 1.230
e il CSV storico invariati. Registra sette osservazioni formali di caso
irrisolto e quattro confronti con minuscole esistenti, con folio, ID
immagine, hash e coordinate. Le osservazioni nuove non sono campioni
maiuscoli approvati: nessuna lettura storica viene aggiunta o promossa.
Il parere sulla combinazione L B, A B, M B, N A, R B, S A è una proposta
di disegno in attesa della scelta umana. [Ambito](../docs/CAPITALS_VARIANT_STUDY.md).

La ricevuta `human_capitals_integration_review_2026-10-16.json` registra
L B, A B, M B, N A, R B, S B. Il manifesto 1.240 vincola i sei contorni
e la dipendenza À; la scelta S B prevale sul parere precedente S A.
Maiuscole classificate `designed`, senza nuove letture storiche approvate.

`cdegpt_variant_study_2026-10-16.json` vincola dodici proposte non approvate
alla 1.240, con quattro osservazioni formali di caso irrisolto e otto
confronti minuscoli esistenti. Non cambia il CSV storico, le sei maiuscole
appena integrate o il font installato. Il registro conserva la fase preparatoria; la scelta successiva è registrata
separatamente nella ricevuta della 1.250.

La ricevuta `human_cdegpt_integration_review_2026-10-16.json` registra
C B, D B, E A, G B, P B, T B; prevalgono le scelte esplicite E A, G B e P B.
Il manifesto 1.250 vincola i sei contorni, mantenendo le maiuscole
`designed`; È/É seguono E A. Il registro dello studio non viene riscritto.

`bfhioq_variant_study_2026-10-16.json` vincola dodici SVG non approvati
alla 1.250 e al CSV storico invariati, con quattro osservazioni di iniziali
di caso irrisolto e dodici confronti minuscoli già revisionati. Folio, ID,
hash, coordinate e contesti restano espliciti. Nessuna lettura capitale
aggiunta o promossa; nessuna integrazione, installazione o scelta umana
registrata. [Ambito](../docs/BFHIOQ_VARIANT_STUDY.md).

La ricevuta `human_bfhioq_integration_review_2026-10-16.json` registra B B,
F B, H B, I A, O B, Q B: H B prevale sul suggerimento H A. Il manifesto
1.260 vincola sei contorni esatti e dipendenze Ì/Ò; le maiuscole restano
`designed`. Nessuna nuova lettura storica o modifica del CSV.

`jkuvwxyz_variant_study_2026-10-16.json` registra sedici proposte non approvate
rispetto alla 1.260, con sei candidate esistenti, tre osservazioni K e quattro
minuscole revisionate. Il precedente studio JKVWXY è vincolato per hash;
nessuna promozione di stato. J non usa la candidata come geometria primaria;
W non ha campione diretto e riporta i motivi contemporanei. Nessuna selezione
umana dei nuovi otto disegni o installazione degli studi.

La ricevuta `human_jkuvwxyz_integration_review_2026-10-16.json` registra tutte
le otto B, prevalenti sui suggerimenti A per J/W/Y/Z. Il manifesto 1.270
vincola otto SVG e Ù, con riferimenti contestuali e motivi progettuali,
senza promozioni di letture o classificazioni. Le quattro selezioni coprono
esattamente tutte le 26 maiuscole A–Z: E/I/N A e 23 B. Il CSV storico e gli
stati dei manifest di studio restano invariati.
