# Storico dei prezzi (P07)

Come raccogliamo il prezzo di Bitcoin, da dove parte lo storico di ogni fonte e quanto le fonti
concordano. Codice: `bailout_lab/raccolta/storico.py`; controllo: `python -m
bailout_lab.raccolta.controllo_storico`. Misure del 24/10/2026.

## Cosa registriamo

| Serie | Fonte | Dal | Passo |
|---|---|---|---|
| `btc_usd_coinbase_*` | Coinbase Exchange, BTC-USD | 20/07/2015 (al minuto: 01/07/2015, con minuti vuoti) | giorno e minuto |
| `btc_usdt_binance_*` | Binance spot, BTCUSDT | 17/08/2017 | giorno e minuto |
| `btc_usdt_okx_*` | OKX spot, BTC-USDT | 11/01/2018 | giorno e minuto |
| `btc_usd_coinmetrics_chiusura` | Coin Metrics Community, `PriceUSD` | 18/07/2010 | giorno |
| `btc_usd_bitview_chiusura` | bitview.space, `price_close` | 16/08/2010 | giorno |

I campi di ogni candela sono `apertura`, `massimo`, `minimo`, `chiusura`, `volume` (in BTC); le
serie al minuto hanno `_1m_` nel nome (`btc_usdt_binance_1m_chiusura`). Il giorno è UTC (su OKX
si chiede `1Dutc`: la candela `1D` semplice parte alle 16:00 UTC). Si salvano solo candele
chiuse.

Kraken non c'è: la sua API dà soltanto le ultime 720 candele, quindi non offre storia.

## Come si riprende

Ogni lancio riparte dall'ultimo istante già salvato e si ferma allo scadere del tempo: il primo
caricamento di anni di candele al minuto richiede alcuni lanci, poi ogni giro legge solo le ultime
ore. Le serie giornaliere rileggono gli ultimi 10 giorni: se una fonte corregge un valore nasce
una nuova versione, come nel resto dell'archivio.

## Una precisione sul «come era noto»

Lo storico caricato oggi ha come istante di disponibilità **quello della nostra lettura**, non
quello in cui l'exchange pubblicò la candela. Per le candele chiuse degli exchange la differenza
non cambia i valori, ma per un test sul passato conta: la registrazione «come era noto» vale
davvero dal 23/10/2026, giorno in cui abbiamo iniziato a raccogliere.

## Quanto concordano le fonti

Confronto sulla chiusura giornaliera, **dal 01/01/2019** (prima il mercato era frammentato fra
pochi exchange con prezzi che differivano davvero):

| Coppia | Giorni | Entro lo 0,5 % | Scarto mediano |
|---|---|---|---|
| Coinbase / Coin Metrics (le due fonti in dollari indipendenti, giudicate) | 2.852 | **95,8 %** | 0,086 % |
| Coinbase / bitview | 2.853 | 82,7 % | 0,224 % |
| Coin Metrics / bitview | 2.852 | 91,4 % | 0,184 % |
| Coinbase (USD) / Binance (USDT) | 2.853 | 96,4 % | 0,048 % |

Regola dichiarata: due fonti concordano se almeno il 95 % dei giorni dal 2019 sta entro lo
0,5 %. Coinbase e Coin Metrics la rispettano. Gli scarti più grandi sono giorni di forte
movimento (12/03/2020, 12/05/2021, 30/06/2022): l'ora di chiusura e il modo di calcolare il
prezzo del giorno cambiano da una fonte all'altra. Su tutta la storia, Coinbase/Coin Metrics
scende al 92,6 % (il peggiore: 07/05/2017, 5,5 %), perché nel 2015–2018 un exchange poteva quotare
anche il 5 % sopra un altro. Binance e OKX quotano in USDT, non in dollari: si riportano ma non
decidono l'esito.

## Cosa citare

«Prezzi: API pubbliche di Coinbase Exchange, Binance e OKX; Coin Metrics Community Data
(coinmetrics.io); Bitcoin Research Kit (bitview.space).»
