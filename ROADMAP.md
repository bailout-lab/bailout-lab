# Roadmap di Bailout Lab

Il progetto avanza a passi. Ogni passo ha una verifica precisa e il successivo parte solo quando
il precedente è chiuso davvero. Le date sono indicative.

| Fase | Obiettivo | Passi | Traguardo indicativo |
|---|---|---|---|
| 0 — Fondamenta | Repo pubblico sicuro, fonti verificate, inizio della registrazione dei dati | P01–P06 | metà novembre 2026 |
| 1 — Primo cruscotto | 20 dati, indicatore v0 su mese e anno, pagina su Bailout | P07–P17 | dicembre 2026 |
| 2 — On-chain profondo e apertura | Tutti i dati del catalogo, community aperta | P18–P25 | febbraio 2027 |
| 3 — Studio delle correlazioni | Ogni dato misurato e giudicato | P26–P28 | maggio 2027 |
| 4 — Indicatore v1 | Modelli per orizzonte, registro pubblico, 3 mesi di prova | P29–P33 | settembre 2027 |
| 5 — Intraday e oltre | Aggiornamento a 15 minuti, mappa delle liquidazioni, avvisi | P34–P37 | da ottobre 2027 |

## Fase 0 — Fondamenta

- [x] **P01 — Organizzazione GitHub** dedicata al progetto.
- [x] **P02 — Repo pubblico protetto:** file di base, ricerca automatica di segreti, `main`
  modificabile solo con pull request che passano i test.
- [ ] **P03 — Censimento delle fonti:** per ogni fonte una chiamata vera; endpoint, frequenza,
  inizio dello storico, limiti e come citarla, in `fonti/`.
- [ ] **P04 — Scheletro del codice:** progetto Python, formato dell'archivio «come era noto»
  (Parquet + DuckDB), test automatici.
- [ ] **P05 — Server del progetto:** i raccoglitori girano da soli, con controllo di salute.
- [ ] **P06 — Prima registrazione «come era noto»:** prezzo giornaliero, macro di base, prime
  metriche on-chain, fee, flussi ETF. Da qui la registrazione non si spegne più.

## Fase 1 — Primo cruscotto

- [ ] **P07 — Storico dei prezzi** da più exchange, con i buchi dichiarati.
- [ ] **P08 — Derivati:** funding, open interest, basis, long/short, volatilità implicita.
- [ ] **P09 — Macro e calendario,** con le versioni storiche dei dati rivisti.
- [ ] **P10 — On-chain di base:** MVRV, Realized Price, SOPR, Puell, hashrate, confrontati fra
  due fonti indipendenti.
- [ ] **P11 — Indicatori tecnici:** medie (anche a 200 settimane), RSI, volatilità,
  supporti/resistenze, Fibonacci, volume profile.
- [ ] **P12 — Schede di studio:** il modello della scheda e le prime 20.
- [ ] **P13 — Indicatore v0:** regole trasparenti per mese e anno, provate contro i riferimenti
  semplici. Il risultato si pubblica anche se non li batte.
- [ ] **P14 — Dati pronti per il sito,** pubblicati senza chiavi.
- [ ] **P15 — Progetto grafico** della pagina.
- [ ] **P16 — Pagina nell'area riservata di Bailout,** in anteprima.
- [ ] **P17 — Pagina online.**

## Fase 2 — On-chain profondo e apertura

- [ ] **P18 — Comportamento dei detentori:** HODL waves, monete dormienti che si risvegliano,
  RHODL, Reserve Risk, CDD, Dormancy, Liveliness, URPD.
- [ ] **P19 — Rete e spazio nei blocchi:** fee, mempool, tempi di conferma, OP_RETURN,
  inscriptions/Runes, Lightning.
- [ ] **P20 — Mining:** hashprice, costo di produzione, Hash Ribbons, report delle società
  quotate.
- [ ] **P21 — Treasury, governi, wallet storici:** mNAV, emissioni, indirizzi pubblici con fonte.
- [ ] **P22 — ETF, CME, opzioni:** flussi per fondo, report COT, opzioni.
- [ ] **P23 — Leggi, stagionalità, sentiment.**
- [ ] **P24 — Etichette degli exchange,** con il tasso di copertura dichiarato.
- [ ] **P25 — Apertura alla community:** Discussions accese e i primi compiti *good first
  issue*.

## Fase 3 — Studio delle correlazioni

- [ ] **P26 — Motore di ricerca:** deve ritrovare un segnale noto su dati sintetici e non
  trovare niente sul rumore puro.
- [ ] **P27 — Studi per famiglia:** grafica, derivati, macro, on-chain (valutazione e
  comportamento), mining, flussi.
- [ ] **P28 — Verdetti pubblici:** ogni scheda dice se il dato è promosso, utile solo su certi
  orizzonti o bocciato.

## Fase 4 — Bailout Indicator v1

- [ ] **P29 — Dataset per orizzonte** con i soli dati promossi.
- [ ] **P30 — Modelli per orizzonte,** con la spiegazione di ogni valore.
- [ ] **P31 — Registro pubblico** non modificabile, marcato con OpenTimestamps.
- [ ] **P32 — Pagina «Come sta andando»** e inizio dei 3 mesi di prova pubblica.
- [ ] **P33 — Verdetto:** l'indicatore diventa ufficiale solo se batte i riferimenti fuori
  campione.

## Fase 5 — Intraday e oltre

- [ ] **P34 — Strato a 15 minuti:** liquidità, liquidazioni, flusso ordini, opzioni.
- [ ] **P35 — Mappa delle liquidazioni stimata,** verificata sulle liquidazioni reali.
- [ ] **P36 — Avvisi su Telegram** ai cambi di fase.
- [ ] **P37 — Sfida alla community:** modelli proposti da altri, giudicati sullo stesso
  registro.
