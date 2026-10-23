# Fonti dei dati

Censimento del **23/10/2026** (passo P03). Per ogni fonte è stata fatta una chiamata vera, da
script, senza account e senza pagare. Ogni scheda dice *cosa* dà la fonte, *dove*, *da quando*,
*con quali limiti* e *come citarla*. In `esempi/` c'è una risposta reale, accorciata, con la
richiesta che l'ha prodotta.

**Come leggere le schede.** «Verificato» = l'ho visto con una chiamata il 23/10/2026.
«Dichiarato» = lo scrive la fonte e non l'ho misurato. Le fonti cambiano: chi riprende questo
lavoro deve rifare la chiamata prima di fidarsi di un numero.

## Esito in una tabella

| Fonte | Esito | Serve chiave? | Cosa ci prendiamo | Scheda |
|---|---|---|---|---|
| bitview.space (BRK) | **funziona** | no | on-chain: MVRV, prezzo realizzato, SOPR, NUPL, Puell, Reserve Risk, RHODL, hashrate, URPD… (~62.000 serie) | [bitview-space.md](bitview-space.md) |
| Coin Metrics Community | **funziona**, ma solo 31 metriche per BTC | no | secondo parere su MVRV, prezzo, indirizzi attivi, hashrate, flussi verso gli exchange | [coin-metrics.md](coin-metrics.md) |
| BGeometrics | **funziona, in ritardo di 7 giorni** | no (gratis) | confronti storici singoli, non una fonte continua | [bgeometrics.md](bgeometrics.md) |
| mempool.space | **funziona** | no | fee, mempool, hashrate e difficoltà dal 2009 | [mempool-space.md](mempool-space.md) |
| Exchange (OKX, Binance, Bybit, Coinbase, Kraken) | **funziona** | no | prezzi, funding, open interest, long/short; liquidazioni solo recenti | [exchange.md](exchange.md) |
| Deribit | **funziona** | no | indice DVOL dal 2021, tutte le opzioni | [deribit.md](deribit.md) |
| FRED / ALFRED | **funziona** | sì, gratuita | macro, liquidità, tassi; ALFRED dà i valori «come erano noti» | [fred-alfred.md](fred-alfred.md) |
| BCE | **funziona** | no | tassi della BCE | [bce.md](bce.md) |
| CFTC (report COT) | **funziona** | no | posizioni dei grandi operatori sui futures Bitcoin del CME, dal 2018 | [cftc.md](cftc.md) |
| SEC EDGAR | **funziona con User-Agent dichiarato**; senza è 403 | no | documenti ufficiali di Strategy e delle altre treasury company | [edgar.md](edgar.md) |
| SoSoValue | **funziona** (chiave gratuita ottenuta) | sì, gratuita | flussi giornalieri degli ETF spot, 300 giorni per chiamata | [sosovalue.md](sosovalue.md) |
| Farside | **bloccata** (403, sfida anti-robot) | — | solo controllo a mano | [farside.md](farside.md) |
| Fear & Greed | **funziona** | no | sentiment giornaliero dal 2018 | [fear-greed.md](fear-greed.md) |
| Google Trends | **non utilizzabile**: nessuna API ufficiale stabile | — | alternativa candidata: visite Wikipedia | [google-trends.md](google-trends.md) |
| Altre (Polymarket, CoinGecko, BitcoinTreasuries) | Polymarket e CoinGecko funzionano; BitcoinTreasuries solo pagina | no | attese di mercato, prezzo di controllo, elenco treasury | [altre-fonti.md](altre-fonti.md) |

## Cosa cambia per i passi successivi

- **On-chain (P10, P18)**: la fonte principale c'è ed è molto ricca; il controllo incrociato è
  possibile **solo su poche metriche** (MVRV, prezzo, indirizzi attivi, hashrate) perché Coin
  Metrics Community non offre SOPR, prezzo realizzato, Reserve Risk. Su MVRV i due valori
  coincidono entro lo 0,3 % (vedi [bitview-space.md](bitview-space.md)).
- **Derivati (P08)**: lo storico gratuito è corto per open interest (Binance 30 giorni) e per le
  liquidazioni (solo le più recenti): serve archiviarli noi da subito, come previsto.
- **ETF (P22)**: SoSoValue funziona ma dà 300 giorni per chiamata (da agosto 2025): lo storico dal 2024 va cercato altrove o con parametri da verificare. Farside non è automatizzabile.
- **Macro (P09)**: ALFRED funziona e dà le versioni storiche; il prezzo dell'S&P 500 su FRED parte
  solo dal 2016 (limite di licenza), da integrare altrove se serve più indietro.
