# Coin Metrics — Community API

**Esito: funziona, ma con un catalogo ridotto.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://community-api.coinmetrics.io/v4/…` |
| Chiave | **No** |
| Metriche per BTC | **31** (verificato con `/v4/catalog/assets?assets=btc`) |
| Frequenza | giornaliera (`1d`) per le metriche principali |
| Storico | `PriceUSD` dal 2010-07-18 |
| Limiti | l'intestazione di risposta dichiara 6.000 richieste per finestra scorrevole di 20 secondi (verificato nell'intestazione `x-ratelimit-limit`); 14 chiamate di fila senza errori |

## Cosa c'è e cosa manca

Presenti (verificato): `CapMVRVCur` (MVRV), `PriceUSD`, `CapMrktCurUSD`, `SplyCur`, `AdrActCnt`
(indirizzi attivi), `HashRate`, `TxCnt`, `IssTotUSD`, `FlowInExUSD`/`FlowInExNtv` (flussi verso gli
exchange), `SplyExNtv` (offerta sugli exchange).

**Assenti** nel livello gratuito: capitalizzazione realizzata (`CapRealUSD`), SOPR, NVT, commissioni
totali, difficoltà, offerta attiva per età. Quindi **non è una seconda fonte per tutto**: serve
come controllo su MVRV, prezzo, indirizzi attivi e hashrate.

## Chiamate

```
GET /v4/catalog/assets?assets=btc
GET /v4/timeseries/asset-metrics?assets=btc&metrics=CapMVRVCur,PriceUSD&frequency=1d&start_time=2026-10-15&page_size=5
```

Attenzione: `catalog/asset-metrics?assets=btc` dà errore 400 (`Unsupported parameter 'assets'`);
il catalogo per asset è quello sopra.

## Come citarla

«Dati: Coin Metrics Community Data (coinmetrics.io).» Le condizioni d'uso vanno
rilette sul sito prima della pubblicazione.

Esempi: [esempi/coin-metrics.json](esempi/coin-metrics.json),
[esempi/coin-metrics-catalogo.json](esempi/coin-metrics-catalogo.json)
