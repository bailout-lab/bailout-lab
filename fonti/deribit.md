# Deribit

**Esito: funziona.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://www.deribit.com/api/v2/public/…` |
| Chiave | **No** per i dati pubblici |
| DVOL (volatilità implicita) | `get_volatility_index_data?currency=BTC&resolution=1D`, **dal 2021-03-24** (primo punto 1616544000000) |
| Opzioni | `get_book_summary_by_currency?currency=BTC&kind=option`: **930 strumenti** al momento della prova, con open interest, volatilità implicita (`mark_iv`), prezzo, volume |
| Limiti | non misurati; richieste distanziate |

## Nota

Lo storico di open interest per strike non è offerto dall'API pubblica: **si archivia la
fotografia ogni giorno** (come per le liquidazioni). Gamma e max pain si calcolano da qui.

## Come citarla

«Dati sulle opzioni: Deribit.»

Esempi: [esempi/deribit-dvol.json](esempi/deribit-dvol.json),
[esempi/deribit-opzioni.json](esempi/deribit-opzioni.json)
