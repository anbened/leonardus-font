# Crediti di Leonardus

Leonardus è un progetto di ricerca e disegno tipografico sviluppato da
[anbened](https://github.com/anbened) con l'assistenza di Codex.

La direzione del progetto, la scelta tra le varianti e le decisioni umane
sono distinte dalle proposte e dalle verifiche dell'agente. Il
[rapporto sul contributo dell'agente](docs/AGENT_CONTRIBUTION.md) e i
registri delle decisioni ne documentano gli ambiti.

## Fonti storiche

Leonardo da Vinci, **Codice Madrid I**, Biblioteca Nacional de España,
segnatura **MSS/8937**. Il [registro delle fonti](data/source_registry.csv)
e quello dei [campioni](data/glyph_evidence.csv) conservano riferimenti,
localizzazioni e stati di revisione. Le riproduzioni dei manoscritti non
sono incluse. La citazione della biblioteca non implica un suo avallo.

## Strumenti

Il progetto usa fontTools per compilare e ispezionare il font, HarfBuzz e
FreeType per le prove di composizione e rasterizzazione, Pillow per le
immagini, ReportLab per i PDF, pypdf per i controlli PDF e pytest per i test.
Le versioni sono registrate in `requirements-build.txt` e
`requirements-dev.txt`; ogni strumento conserva la propria licenza.

## Attribuzione suggerita

> Leonardus Regular 1.270 — progetto anbened, sviluppato con l'assistenza
> di Codex. Font contemporaneo ispirato alla grafia documentata di Leonardo
> da Vinci. Font e contorni sotto SIL Open Font License 1.1.

Questa formula è un suggerimento editoriale. Per gli obblighi di
redistribuzione fanno fede [OFL.txt](OFL.txt) e [LICENSE-MIT.txt](LICENSE-MIT.txt).
