# Ampliamento del corpus delle minuscole

Record del primo batch. Il successivo [consolidamento](SEGMENTATION_CONSOLIDATED.md)
copre tutti i 61 campioni selezionati; il [riesame delegato](../data/research_assessment_2026-10-15.json)
aggiunge osservazioni separate sulle candidate residue, senza promuovere
il CSV storico. La consegna progettuale corrente è la [1.200](REGULAR_1_200.md).

14 ottobre 2026. Primo batch aggiuntivo: **65 campioni candidati per 12 minuscole**, su quattro folii di lavoro del Codice Madrid I, BNE MSS/8937. Il registro passa da 44 a 109 campioni; le 40 identificazioni già confermate restano tali. Questo checkpoint non approva nuove identificazioni o forme del font.

Il [seguito della revisione guidata](GUIDED_REVIEW.md) registra il 15 ottobre
2026 le conferme dei sette gruppi: nel primo batch restano 19 campioni
candidati e 46 revisionati. I metadati del batch conservano la selezione
iniziale; il CSV e le ricevute separate registrano gli esiti successivi.

La [ricerca mirata successiva](LOWERCASE_SEARCH.md) aggiunge 35 candidate
e documenta le questioni aperte k/w e la nuova foliazione di lavoro.

Le sette normalizzazioni della Regular 1.000 derivano dal perimetro del pilota iniziale, non da un limite tecnico. Questo batch prepara l’estensione della ricerca; il TTF, gli SVG, i manifesti del disegno e le ricevute della 1.000 restano invariati.

## Fonti e acquisizione

[Scheda BNE](https://bnedigital.bne.es/bd/card?oid=0000040157&site=bdh) e [viewer ufficiale](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e). Il 14 ottobre la scheda e il pannello JPEG della pagina 14 dichiaravano pubblico dominio, CC BY 4.0 o equivalente, attribuzione BNE e uso gratuito senza autorizzazione previa. Sono state selezionate le pagine 14, 16, 18 e 20 dal download JPEG ufficiale. Gli hash dei quattro originali riacquisiti coincidono con quelli già registrati.

**Credito:** Imágenes procedentes de los fondos de la Biblioteca Nacional de España. Le immagini sono solo in cartelle locali ignorate, non nei file versionati. OFL e MIT non si estendono alle riproduzioni BNE. Nessun avallo BNE è dichiarato.

La mappatura di lavoro conservata è 14→1r, 16→2r, 18→3r, 20→4r. I nomi JPEG 1–4 seguono l’ordine delle pagine selezionate, non la foliazione. Questo batch non aggiunge una certificazione indipendente della foliazione o dell’autenticità.

## Scelte di ricerca e copertura

Prima priorità: **c, i, u, m, s, t, p, q**, per ampliare le forme di base e confrontare aste, minimi, archi e discendenti con il nucleo esistente. **f e g** aggiungono confronti utili sulle forme lunghe e sui cappi; **b e z** sono esplorative, con una sola occorrenza ciascuna. La selezione considera leggibilità, contesto e varietà; non tratta il numero di crop come conferma di copertura storica.

| Lettera | Candidate | Folii di lavoro |
|---|---:|---|
| b | 1 | 1r |
| c | 4 | 1r, 4r |
| f | 5 | 1r, 3r, 4r |
| g | 5 | 2r, 4r |
| i | 2 | 2r, 3r |
| m | 8 | 1r, 2r, 3r, 4r |
| p | 9 | 1r, 2r, 3r, 4r |
| q | 5 | 1r, 3r, 4r |
| s | 6 | 1r, 2r, 3r, 4r |
| t | 10 | 1r, 2r, 3r, 4r |
| u | 9 | 2r, 3r, 4r |
| z | 1 | 4r |

Restano da cercare **h, j, k, v, w, x, y**. Nessuna assenza dal manoscritto viene dedotta dalla selezione di quattro pagine. Per v va chiarita la distinzione fra forma osservata e associazione moderna u/v; per i/j l’asta senza punto non autorizza una classificazione automatica. Non si inventano occorrenze per completare la tabella.

## Come vedere e revisionare i campioni

I [metadati del batch](../data/lowercase_expansion_2026-10-14.json) contengono coordinate originali, coordinate specchiate, contesto, hash e motivazioni. Il [registro delle evidenze](../data/glyph_evidence.csv) conserva le righe inizialmente candidate; 46 campioni del primo batch hanno ora i campi della revisione del 15 ottobre. La confidenza 0.0 delle nuove righe significa **non stimata**, non rifiuto o probabilità calibrata, e resta invariata anche dopo la conferma della lettura.

Per riprodurre il dossier, acquisire dal viewer BNE le sole pagine 14,16,18,20 nel rispetto delle condizioni specifiche. Rinominare i quattro JPEG, nell’ordine, `page-014.jpg`, `page-016.jpg`, `page-018.jpg`, `page-020.jpg` e collocarli in `data/scans/expansion-2026-10-14/`. Il generatore controlla hash e dimensioni prima di scrivere i ritagli; non scarica immagini o legge altri progetti.

```powershell
.\.venv\Scripts\python.exe examples/corpus_review.py --check-only
.\.venv\Scripts\python.exe examples/corpus_review.py
```

Aprire `build/corpus-review/index.html`: indice per lettera, ritagli specchiati ingranditi 3×, contesto con bersaglio rosso, link al folio nel viewer e dubbi per campione. I contesti sono a scala 1:1; non sono stati applicati contrasto, rotazione, ricostruzione o generazione AI. Gli originali restano invariati. Tutte le immagini derivate e il dossier visuale restano in `build/`, ignorato da Git.

La scheda locale `review.csv` parte con decisioni vuote e non viene sovrascritta alla rigenerazione. Registrare accepted, uncertain oppure rejected per l’identificazione della lettera, con data e motivazione; il file non modifica automaticamente registri o font. Una lettura confirmed non approva l’intera parola, i confini del contorno, una nuova normalizzazione o il rilascio.

## Questioni raccolte per la revisione

| Questione | Proposta operativa |
|---|---|
| s lunga / f | Valutare traversa, cappio e contesto; mantenere uncertain se non distinguibili. |
| q / p / g | Confrontare discendente e lobo sul contesto; non confermare sulla sola parola suggerita. |
| u / v e i / j | Confermare prima il segno osservato; decidere la normalizzazione moderna separatamente. |
| m / n e connessioni | Le finestre localizzano il bersaglio; non certificano la separazione delle aste o dei tratti condivisi. |
| b e z, un solo campione | Trattarle come esplorative; cercare altri contesti prima del disegno. |
| Etichetta f isolata | Stabilire se è lettera o simbolo di diagramma; confrontare con le f nel testo. |
| Token con ? o … | Leggere la singola lettera nel contesto; non assumere la trascrizione completa della parola. |

Queste questioni non fermano la raccolta di altre occorrenze. Il passo successivo è rinforzare c e i, cercare h e altre b/z, poi estendere a ulteriori folii. Obiettivo di ricerca: più occorrenze distinte e, dove disponibili, almeno due folii per lettera; non una soglia che autorizzi automaticamente un glifo storico. Un nuovo disegno richiederà derivazione documentata e prove di leggibilità.

## Indice dei campioni

Tutte le righe seguenti sono proposte non revisionate. I token sono ipotesi di localizzazione. Le coordinate `[x,y,w,h]` sono nell’immagine specchiata di 1578×2174; il JSON contiene anche quelle originali.

| ID | Lettera | Folio / pagina | Token proposto | Bersaglio specchiato |
|---|---|---|---|---|
| BNE_MI_EXP_014_B_01 | b | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | impossibile (?) | [455, 1671, 22, 44] |
| BNE_MI_EXP_014_C_01 | c | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | con[?] | [1317, 370, 24, 26] |
| BNE_MI_EXP_014_C_02 | c | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | manco (?) | [189, 1017, 22, 22] |
| BNE_MI_EXP_020_C_03 | c | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | c quale? | [791, 1503, 34, 31] |
| BNE_MI_EXP_020_C_04 | c | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | sin…? | [510, 1675, 23, 24] |
| BNE_MI_EXP_014_F_01 | f | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | fiamma (?) | [509, 103, 33, 69] |
| BNE_MI_EXP_014_F_02 | f | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | ferro (?) | [131, 904, 24, 55] |
| BNE_MI_EXP_018_F_03 | f | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | finito? | [1189, 497, 30, 68] |
| BNE_MI_EXP_020_F_04 | f | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | in fra…? | [1055, 1647, 34, 83] |
| BNE_MI_EXP_020_F_05 | f | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | f | [540, 1719, 27, 81] |
| BNE_MI_EXP_016_G_01 | g | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | Ogni | [444, 96, 28, 76] |
| BNE_MI_EXP_016_G_02 | g | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | bisogni (?) | [1090, 102, 27, 59] |
| BNE_MI_EXP_016_G_03 | g | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | [?]g[?] | [951, 1877, 36, 53] |
| BNE_MI_EXP_020_G_04 | g | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | magior…? | [650, 1673, 30, 64] |
| BNE_MI_EXP_020_G_05 | g | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | degradando? | [826, 1729, 36, 64] |
| BNE_MI_EXP_016_I_01 | i | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | Ogni | [488, 109, 12, 41] |
| BNE_MI_EXP_018_I_02 | i | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | qui? | [1280, 267, 16, 33] |
| BNE_MI_EXP_014_M_01 | m | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | manco (?) | [125, 1018, 29, 21] |
| BNE_MI_EXP_016_M_02 | m | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | dimanda | [692, 105, 31, 27] |
| BNE_MI_EXP_016_M_03 | m | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | dimanda | [539, 172, 32, 25] |
| BNE_MI_EXP_018_M_04 | m | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | …sima? | [1130, 220, 33, 27] |
| BNE_MI_EXP_018_M_05 | m | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | …numero? | [1090, 411, 31, 24] |
| BNE_MI_EXP_018_M_06 | m | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | moto | [1016, 463, 32, 24] |
| BNE_MI_EXP_018_M_07 | m | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | moto? | [975, 526, 32, 28] |
| BNE_MI_EXP_020_M_08 | m | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | numero? | [780, 1675, 32, 25] |
| BNE_MI_EXP_014_P_01 | p | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | ap[?] | [245, 876, 23, 32] |
| BNE_MI_EXP_014_P_02 | p | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | prima (?) | [227, 1017, 24, 36] |
| BNE_MI_EXP_016_P_03 | p | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | corpo | [593, 108, 29, 54] |
| BNE_MI_EXP_016_P_04 | p | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | parti (?) | [1060, 213, 27, 54] |
| BNE_MI_EXP_018_P_05 | p | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | polo? | [968, 270, 30, 49] |
| BNE_MI_EXP_018_P_06 | p | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | che p…? | [1018, 411, 28, 48] |
| BNE_MI_EXP_020_P_07 | p | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | un po? | [638, 1556, 27, 65] |
| BNE_MI_EXP_020_P_08 | p | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | parti? | [702, 1776, 32, 60] |
| BNE_MI_EXP_020_P_09 | p | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | poten…? | [931, 1880, 33, 61] |
| BNE_MI_EXP_014_Q_01 | q | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | acqua (?) | [477, 182, 31, 51] |
| BNE_MI_EXP_014_Q_02 | q | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | que[?] | [511, 1745, 39, 39] |
| BNE_MI_EXP_018_Q_03 | q | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | qui? | [1248, 272, 18, 60] |
| BNE_MI_EXP_018_Q_04 | q | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | questa? | [771, 463, 30, 63] |
| BNE_MI_EXP_020_Q_05 | q | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | quale? | [822, 1496, 25, 73] |
| BNE_MI_EXP_014_S_01 | s | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | con[?] | [1361, 353, 28, 48] |
| BNE_MI_EXP_016_S_02 | s | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | sua | [839, 80, 29, 74] |
| BNE_MI_EXP_016_S_03 | s | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | sua | [995, 198, 25, 71] |
| BNE_MI_EXP_018_S_04 | s | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | …sima? | [1104, 204, 24, 54] |
| BNE_MI_EXP_018_S_05 | s | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | questa? | [827, 449, 26, 51] |
| BNE_MI_EXP_020_S_06 | s | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | …s…? | [743, 1539, 28, 62] |
| BNE_MI_EXP_014_T_01 | t | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | tutti (?) | [303, 801, 18, 30] |
| BNE_MI_EXP_014_T_02 | t | [1r / 14](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=14) | tutti (?) | [331, 804, 17, 30] |
| BNE_MI_EXP_016_T_03 | t | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | parti (?) | [1115, 212, 21, 32] |
| BNE_MI_EXP_018_T_04 | t | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | tutte? | [812, 220, 26, 29] |
| BNE_MI_EXP_018_T_05 | t | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | moto? | [1067, 272, 35, 24] |
| BNE_MI_EXP_018_T_06 | t | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | tutte | [814, 406, 21, 33] |
| BNE_MI_EXP_018_T_07 | t | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | tutte | [771, 407, 28, 33] |
| BNE_MI_EXP_018_T_08 | t | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | moto | [1067, 459, 31, 28] |
| BNE_MI_EXP_020_T_09 | t | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | tutte | [353, 1504, 36, 43] |
| BNE_MI_EXP_020_T_10 | t | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | …? | [873, 1718, 32, 44] |
| BNE_MI_EXP_016_U_01 | u | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | sua | [852, 104, 23, 23] |
| BNE_MI_EXP_016_U_02 | u | [2r / 16](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=16) | sua | [1017, 216, 18, 28] |
| BNE_MI_EXP_018_U_03 | u | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | tutte? | [772, 228, 23, 25] |
| BNE_MI_EXP_018_U_04 | u | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | qui? | [1264, 273, 16, 29] |
| BNE_MI_EXP_018_U_05 | u | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | tutte | [794, 415, 23, 23] |
| BNE_MI_EXP_018_U_06 | u | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | questa? | [798, 470, 22, 26] |
| BNE_MI_EXP_018_U_07 | u | [3r / 18](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=18) | quel? | [1098, 527, 33, 28] |
| BNE_MI_EXP_020_U_08 | u | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | quale? | [847, 1499, 27, 25] |
| BNE_MI_EXP_020_U_09 | u | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | tutte | [372, 1518, 19, 24] |
| BNE_MI_EXP_020_Z_01 | z | [4r / 20](https://bnedigital.bne.es/bd/es/viewer?id=1354ee8e-5c8d-4f9c-bb4c-6963121b7a7e&page=20) | meza? | [465, 1567, 21, 38] |

## Verifica e limiti

Il generatore controlla integrità delle immagini, contenimento del bersaglio nel contesto, formula di specchiatura, duplicati e corrispondenza JSON/CSV. La CI verifica i metadati senza scaricare immagini. La prima parte del CSV conserva byte per byte i 44 record iniziali, verificati da un test dedicato. La build della 1.000 deve mantenere il suo SHA256 accettato.

L’ispezione dell’agente è una proposta, non revisione umana o autenticazione paleografica. Le candidate non vengono usate per riclassificare i completamenti della 1.000.
