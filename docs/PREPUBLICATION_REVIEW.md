# Verifica prima della diffusione pubblica — Regular 1.100

La candidata corrente al 17 ottobre 2026 è **Leonardus Regular 1.270**,
con [denominazione finale](REGULAR_1_270_NAMING.md) e
[derivazione aggiornata](DERIVAZIONE_1_270.csv). I successivi studi, le scelte
dei disegni, il collaudo Office e la rinomina non estendono lo screening
qui documentato della 1.100 ai nuovi contorni e non approvano la diffusione
pubblica. Gli esiti tecnici correnti sono nel [rapporto QA](QA.md).

Il presente controllo resta riferito alla 1.100. La successiva candidata
[1.200](REGULAR_1_200.md) ha sorgenti e verifiche tecniche separate;
non eredita una nuova approvazione della pubblicazione o uno screening
sistematico dei sei contorni rielaborati da questo record.

15 ottobre 2026. Le verifiche tecniche e di esposizione descritte qui sono
completate sul checkpoint `9a960bf` e sulla successiva revisione documentale.
La diffusione pubblica resta da approvare. Nessun cambio di visibilità,
release o modifica dell'archivio di ricerca è eseguito in questo passaggio.

## Contenuto e documentazione

Il TTF corrente mantiene SHA256
`1f65d26ece4c8a0fe9c275fcdedfa037fab88a9687b0cd89a941d131eb899632`.
Il checkpoint 1.000 mantiene il proprio hash in `fonts/previous/`.
README, istruzioni per contribuire, scheda di revisione e contributo
dell'agente distinguono ora le due versioni e le rispettive verifiche.
Il riferimento errato all'hash 1.000 come font corrente è corretto.

Le [prove Office](OFFICE_1_100.md) della 1.100 comprendono quattro pagine
Word e quattro slide PowerPoint, quattro corpi, salvataggio, riapertura
e PDF nativi. I 61 ritagli storici restano ipotesi di segmentazione:
la loro revisione non è necessaria per distribuire i disegni contemporanei
approvati, purché resti esplicita questa distinzione.

Font e contorni restano OFL 1.1, codice e documentazione MIT. Non sono
aggiunte immagini dei manoscritti o risorse tipografiche di terzi.

## Cronologia, log e superfici GitHub

Sul checkpoint iniziale sono controllati tutti i 12 commit raggiungibili,
373 blob distinti e i metadati di autore e committer. I nomi sono identità
di progetto e gli indirizzi sono GitHub noreply. Il controllo privacy
decodifica anche i formati supportati dal validatore; non trova rilievi.
Gitleaks 8.30.1 esamina la cronologia completa senza esclusioni tramite
commenti di allowlist: nessuna credenziale rilevata.

Tutti i log delle 12 esecuzioni Actions presenti sono acquisiti e
controllati, compresa la prima esecuzione fallita: 1.607.098 byte di log,
nessun rilievo privacy e nessuna credenziale rilevata. I rapporti grezzi
e i dati API restano locali sotto `build/`. Le risposte API non sono
materiale distribuibile e sono ridotte ai campi necessari alla verifica.

L'inventario remoto mostra soltanto `main`, senza tag o riferimenti PR.
Non risultano issue, pull request, release, artifact Actions, webhook,
deploy key o ambienti di distribuzione. Wiki e Pages non sono attive.
L'elenco dei collaboratori contiene soltanto il proprietario del progetto.
Le superfici assenti non sono dichiarate sottoposte a un esame di contenuto.

La CI di quella revisione riguarda il checkpoint descritto e non attesta
l'edizione corrente. Le verifiche di questa edizione sono consultabili in
[Actions](https://github.com/anbened/leonardus-font/actions).
L'esportazione Git finale è confrontata con inventario e file locali;
documenti Office, scansioni, prove locali e dump API sono esclusi.

## Impostazioni di sicurezza

| Controllo | Esito del 15 ottobre |
|---|---|
| Permessi predefiniti dei workflow | Lettura; approvazione di PR tramite Actions disabilitata. |
| Actions ammesse | Limitate a quelle di GitHub; creatori verificati generici e pattern aggiuntivi non ammessi. |
| Riferimenti delle Actions | SHA completi richiesti nelle impostazioni; workflow già fissato a commit. |
| Avvisi sulle dipendenze | Attivati; nessun alert restituito al controllo. |
| Gitleaks | Cronologia e dati distribuibili controllati; scansione della cronologia inclusa nella CI. |
| Protezione di main e ruleset | API 403: funzionalità non disponibile con il piano e la configurazione attuali. Non applicata. |
| Approvazione workflow da fork esterni | API 422: impostazione non applicabile nella configurazione attuale. Da riesaminare prima di accettare contributi esterni. |
| Secret scanning e push protection gestiti da GitHub | Disponibilità e attivazione non confermate; non dichiarate attive sulla base di un valore API nullo. |

Le restrizioni sulle Actions non coprono i comandi shell: il download di
Gitleaks nel workflow resta fissato a versione e SHA256. Lo screening OSV
è aggiornato sulle sette dipendenze Python elencate in
[PACKAGE_QA.json](PACKAGE_QA.json), senza segnalazioni per quelle versioni.
Non è una verifica completa di dipendenze transitive o librerie native.

Le conseguenze del cambio di visibilità, compresa l'esposizione dei log,
sono descritte da [GitHub](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility).
Le [impostazioni Actions](https://docs.github.com/en/rest/actions/permissions)
sono verificate anche tramite lettura successiva alle modifiche.

## Confronto e punti da valutare

Il [confronto aggiornato](COMPARISON.md) comprende tutte le tredici nuove
minuscole rispetto a tre famiglie esterne, otto risultati TMview Contains,
28 risultati fuzzy nelle classi 9/42 e il dettaglio dei sei risultati
indicati come attivi o pendenti. Sono osservate venti miniature DesignView
su 614 risultati filtrati. Questi limiti sono dichiarati, non superati
per inferenza. Il marchio italiano che comprende servizi grafici è
riportato fra i riferimenti da valutare, senza attribuirgli un conflitto
accertato né escluderlo automaticamente.

Non è stata ottenuta una certificazione di disponibilità del nome o una
valutazione legale esaustiva. Le licenze del progetto non sostituiscono
questo giudizio. La stampa fisica, altre piattaforme e l'esame completo
dei disegni anteriori restano fuori dall'ambito verificato.

## Controlli conclusivi per la pubblicazione

Non risultano difetti tecnici aperti che richiedano un nuovo disegno del
font per distribuire la candidata corrente. Prima del cambio di visibilità
restano necessari questi controlli sul contenuto scelto:

- Confermare il commit e il pacchetto esatti, gli ambiti OFL/MIT e le
  dichiarazioni sui disegni contemporanei e sull'evidenza storica.
- Verificare l'esito della CI sul commit finale: test, privacy, cronologia,
  inventario, build riproducibili e campionari. Ripetere i controlli se
  intervengono altre modifiche.
- Controllare che i contenuti esclusi dalla pubblicazione non siano
  raggiungibili anche attraverso la cronologia, altri riferimenti o log.
  La sola cancellazione di un file non basta; neppure una riscrittura della
  cronologia garantisce la rimozione delle copie conservate dal servizio.
- Riesaminare le protezioni disponibili per `main`, secret scanning e
  push protection, e configurare l'approvazione delle esecuzioni CI prima
  di accettare contributi esterni. Dichiarare le funzioni non disponibili
  senza aggirarle cambiando piano o visibilità.

La conservazione di viste dei vecchi commit dopo una riscrittura è
descritta nella [documentazione GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
Se un contenuto deve essere escluso con certezza dalla futura esposizione,
una cronologia pulita sullo stesso repository non certifica la cancellazione
lato servizio: occorre risolvere questo punto prima di cambiare visibilità,
eventualmente destinando alla diffusione un repository indipendente che
non abbia mai ricevuto quel contenuto.

Stampa fisica, prove su altre piattaforme e ampliamento o revisione delle
segmentazioni sono miglioramenti successivi, non prerequisiti tecnici per
distribuire gli attuali disegni contemporanei con i limiti dichiarati.
Un parere legale professionale resta un approfondimento distinto; questo
rapporto non lo presenta come ottenuto o come test tecnico da superare.
Il cambio di visibilità richiede comunque una decisione esplicita separata.

I risultati non garantiscono l'assenza di qualsiasi dato sensibile o
diritto anteriore: descrivono controlli ripetibili e osservazioni sul
materiale effettivamente esaminato. Ogni nuova modifica richiede revisione.
