# bitview.space (Bitcoin Research Kit)

**Esito: funziona.** Verificato il 23/10/2026.

| | |
|---|---|
| Cos'è | Istanza pubblica e gratuita di BRK (Bitcoin Research Kit, MIT): un nodo che calcola le metriche on-chain e le serve via API |
| Indirizzo | `https://bitview.space/api/…` — documentazione `https://bitview.space/api`, specifica `https://bitview.space/openapi.json` |
| Chiave | **No** |
| Formato | JSON (o CSV con `format=csv`) |
| Serie disponibili | **61.949** distinte (verificato con `/api/series/count`) |
| Indici | minuto, ora, giorno (`day1`), settimana, mese, trimestre, anno, e per altezza di blocco (`height`) |
| Storico | dal 2009-01-03; es. MVRV valorizzato dal 2010-09-28 |
| Aggiornamento | segue il nodo: al momento della prova indicizzato all'altezza di punta, ultimo blocco 19:37 UTC (`/health`) |
| Limiti | Nessun limite dichiarato. 25 chiamate di fila senza errori (verificato). La documentazione cita un errore `weight_exceeded`: esiste un tetto per richiesta, quindi tenere le richieste piccole (non raggiunto nelle prove) |
| Contatto | `hello@bitcoinresearchkit.org` (dalla specifica) |

## Chiamate che useremo

```
GET /health                                   stato e altezza indicizzata
GET /api/series/search?q=mvrv                 trova il nome di una serie
GET /api/series/mvrv/day1?start=2026-10-18&end=2026-10-23     intervallo
GET /api/series/mvrv/day1/latest              ultimo valore
GET /api/series/mvrv/day1/version             cambia quando la serie viene ricalcolata
GET /api/series/bulk?series=a,b&index=day1    più serie in una chiamata
GET /api/urpd/{cohort}/{data}                 distribuzione dei prezzi d'acquisto
```

Serie confermate esistenti: `mvrv`, `sth_mvrv`, `lth_mvrv`, `realized_price`, `nupl`,
`sopr_24h` (sul giorno; `sopr` esiste solo per altezza di blocco), `puell_multiple`,
`reserve_risk`, `rhodl_ratio`, `hash_rate`. Per HODL waves e fasce di saldo esistono le serie
`addrs_*` e le coorti URPD (da approfondire in P18).

## Controllo incrociato con Coin Metrics (MVRV, 18–22 ottobre 2026)

| Giorno | bitview | Coin Metrics | Scarto |
|---|---|---|---|
| 18/10 | 1,5196 | 1,5208 | 0,08 % |
| 19/10 | 1,5240 | 1,5201 | 0,26 % |
| 20/10 | 1,5396 | 1,5376 | 0,13 % |
| 21/10 | 1,5633 | 1,5604 | 0,19 % |
| 22/10 | 1,5041 | 1,5031 | 0,07 % |

Il valore del giorno corrente è parziale: il giorno si chiude a mezzanotte UTC.

## Cosa sappiamo e non sappiamo

- Le serie cambiano nel tempo (ricalcoli): per registrare «come era noto» serve salvare noi il
  valore con l'ora in cui lo leggiamo (`/version` aiuta a capire quando è stato ricalcolato).
- Un'istanza sola: se chiude, lo storico che abbiamo salvato resta, il calcolo passa a un nodo
  nostro con BRK (piano B del progetto).

## Come citarla

«Dati on-chain: Bitcoin Research Kit (bitview.space), licenza MIT.»

Esempio: [esempi/bitview-space.json](esempi/bitview-space.json)
