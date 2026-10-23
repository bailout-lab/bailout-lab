# Exchange: OKX, Binance, Bybit, Coinbase, Kraken

**Esito: tutti rispondono senza chiave.** Verificato il 23/10/2026. Sono API pubbliche di mercato.

| Exchange | Prezzi giornalieri | Funding | Open interest | Long/short | Liquidazioni |
|---|---|---|---|---|---|
| **OKX** | sì, almeno dal 2019-06 (`history-candles`) | sì, ogni 8 ore, paginato | sì (`rubik/stat/contracts/open-interest-history`) | non provato | **solo le più recenti** (`public/liquidation-orders`) |
| **Binance** | dal 2017-08-17 (`klines`) | dal 2019-09-10, ogni 8 ore | **solo 30 giorni** (`openInterestHist`) | sì (`globalLongShortAccountRatio`) | non provato |
| **Bybit** | sì (`market/kline`) | sì (`funding/history`) | sì (`market/open-interest`) | sì (`market/account-ratio`) | non provato |
| **Coinbase** | **350 candele per chiamata** | — | — | — | — |
| **Kraken** | **721 candele per chiamata** (la finestra recente) | — | — | — | — |

## Cosa ne segue

- **Prezzi storici (P07)**: Binance dal 2017 e OKX dal 2019 reggono lo storico lungo; Coinbase e
  Kraken vanno scaricati a finestre, e per il periodo prima del 2017 serve un'altra fonte
  (es. serie di prezzo di bitview.space, dal 2009).
- **Open interest storico**: Binance ne dà 30 giorni (verificato: 30 punti con `limit=500`).
  Per averne di più bisogna **archiviarlo noi a partire da oggi**; è già nel piano.
- **Liquidazioni**: nessun storico profondo gratuito. Si archivia dal momento in cui si comincia
  a raccogliere.
- **Funding Binance**: la richiesta con `startTime=0` risponde con il valore più recente; per
  lo storico serve un `startTime` reale (es. 1500000000000 → primo valore 2019-09-10).
- Ogni exchange ha **limiti di richieste** propri (dichiarati nelle loro documentazioni, non
  misurati qui): i raccoglitori li rispetteranno e useranno la chiamata più «larga» possibile.

## Come citarli

«Dati di mercato: API pubbliche di OKX, Binance, Bybit, Coinbase Exchange e Kraken.»

Esempi: [okx](esempi/exchange-okx.json) · [binance](esempi/exchange-binance.json) ·
[bybit](esempi/exchange-bybit.json) · [coinbase](esempi/exchange-coinbase.json) ·
[kraken](esempi/exchange-kraken.json)
