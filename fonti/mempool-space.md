# mempool.space

**Esito: funziona.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://mempool.space/api/…` |
| Chiave | **No** |
| Formato | JSON |
| Storico hashrate e difficoltà | dal 2009-01-03 (`/api/v1/mining/hashrate/all`, primo punto 1231006505) |
| Limiti | Non dichiarati nelle risposte; nessun errore sulle chiamate provate. Da gestire con richieste distanziate |

## Chiamate

```
GET /api/v1/fees/recommended          fee consigliate (sat/vB)
GET /api/mempool                      dimensione e istogramma delle fee
GET /api/v1/mining/hashrate/3m        hashrate e difficoltà (1m, 3m, 6m, 1y, …, all)
```

## Nota

bitview.space espone la stessa forma di API (è compatibile con mempool.space): per le fee e il
mempool si possono confrontare le due fonti.

## Come citarla

«Dati: mempool.space.»

Esempi: [esempi/mempool-space.json](esempi/mempool-space.json),
[esempi/mempool-space-hashrate.json](esempi/mempool-space-hashrate.json)
