# CFTC — Commitments of Traders (report COT)

**Esito: funziona.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://publicreporting.cftc.gov/resource/gpe5-46if.json` (dati aperti, formato Socrata) |
| Chiave | **No** |
| Report | «Traders in Financial Futures» (TFF): posizioni di dealer, gestori, fondi a leva, altri |
| Contratto che ci interessa | **Bitcoin – CME**, codice `133741` (esistono anche contratti minori, es. Bitcoin Cash, da non confondere) |
| Storico | dal **2018-04-10** (verificato) |
| Frequenza | settimanale: la data del report è il **martedì** (ultimo disponibile: 20/10/2026) |
| Ritardo | il report esce dopo qualche giorno; l'ora esatta di pubblicazione va misurata in P06 per registrare quando il dato era davvero noto |
| Limiti | non misurati; usare richieste filtrate e piccole (la piattaforma, di tipo Socrata, può limitare le richieste senza chiave) |

## Chiamata

```
GET /resource/gpe5-46if.json?$limit=1&$where=cftc_contract_market_code='133741'&$order=report_date_as_yyyy_mm_dd DESC
```

Campi principali: `open_interest_all`, `lev_money_positions_long/short` (fondi speculativi),
`asset_mgr_positions_long/short` (gestori), `dealer_positions_long_all/short_all`.
Al 20/10/2026: open interest 21.040 contratti; fondi a leva 5.466 long contro 10.408 short.

## Come citarla

«Dati: U.S. Commodity Futures Trading Commission, Commitments of Traders.»

Esempio: [esempi/cftc-cot-cme.json](esempi/cftc-cot-cme.json)
