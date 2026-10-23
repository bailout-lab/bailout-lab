# Altre fonti incontrate

Provate il 23/10/2026 perché citate nel catalogo dei dati.

## Polymarket (attese di mercato)

**Funziona, senza chiave.** `https://gamma-api.polymarket.com/markets?limit=1` risponde con
domanda, esiti e prezzi (probabilità implicite). Da usare in P09/P23 per le attese su tassi e
eventi; va filtrato per i mercati pertinenti. Esempio: [esempi/polymarket.json](esempi/polymarket.json).
Kalshi: non provata.

## CoinGecko (prezzo di controllo)

**Funziona, senza chiave**, ma con limiti stretti nel livello gratuito (non misurati).
`https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`. Utile solo come
controllo del prezzo, non come fonte di storico. Esempio: [esempi/coingecko.json](esempi/coingecko.json).

## BitcoinTreasuries (treasury company)

**Solo pagina web**: `https://bitcointreasuries.net/` risponde 200 ma con HTML (circa 1 MB), non
è emersa un'API pubblica. Per le treasury company la fonte primaria resta EDGAR
([edgar.md](edgar.md)); BitcoinTreasuries serve come elenco di confronto da leggere a mano.
