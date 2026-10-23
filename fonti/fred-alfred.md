# FRED e ALFRED (Federal Reserve Bank of St. Louis)

**Esito: funziona.** Verificato il 23/10/2026. **Serve una chiave gratuita**
(`https://fred.stlouisfed.org/docs/api/api_key.html`), da mettere in `FRED_API_KEY` nel proprio
`.env`.

| | |
|---|---|
| Indirizzo | `https://api.stlouisfed.org/fred/…` |
| Formato | JSON (`file_type=json`) |
| Storico | dipende dalla serie, vedi sotto |
| Limiti | la fonte documenta un tetto di richieste al minuto; non misurato (nessun errore nelle ~20 chiamate provate) |

## Serie provate (verificate)

| Serie | Cosa | Frequenza | Da | Ultimo dato al 23/10 |
|---|---|---|---|---|
| `DGS10` | rendimento Treasury 10 anni | giornaliera | 1962 | 21/10 |
| `T10Y2Y` | curva 10 anni – 2 anni | giornaliera | 1976-06-01 | 22/10 |
| `DFII10` | rendimento reale a 10 anni | giornaliera | 2003-01-02 | 21/10 |
| `DFEDTARU` | tasso Fed, limite alto | giornaliera | 2008-12-16 | 23/10 |
| `WALCL` | bilancio della Fed | **settimanale** | 2002-12-18 | 21/10 |
| `WTREGEN` | conto del Tesoro presso la Fed (TGA) | settimanale | 2002-12-18 | 21/10 |
| `RRPONTSYD` | reverse repo overnight | giornaliera | 2003-02-07 | 23/10 |
| `M2SL` | M2 USA | **mensile** | 1959-01-01 | **agosto 2026** |
| `DTWEXBGS` | dollaro (indice ampio) | giornaliera | 2006-01-02 | 16/10 |
| `VIXCLS` | VIX | giornaliera | 1990-01-02 | 22/10 |
| `NASDAQCOM` | Nasdaq Composite | giornaliera | 1971-02-05 | 22/10 |
| `SP500` | S&P 500 | giornaliera | **2016-10-24** | 21/10 |

La *net liquidity* della Fed si calcola come `WALCL − WTREGEN − RRPONTSYD` (attenzione alle unità
e alle frequenze diverse).

**Limiti da ricordare.** `SP500` su FRED parte solo dal 2016 (limite di licenza dell'editore): per
lo storico più lungo serve un'altra fonte. `M2SL` ha un ritardo di circa due mesi.

## ALFRED: i valori «come erano noti»

Lo stesso servizio dà le **versioni passate** dei dati, con i parametri `realtime_start` e
`realtime_end`. Verificato:

- `fred/series/vintagedates?series_id=CPIAUCSL` → **670 date di revisione** (ultime: 14/10/2026,
  11/09/2026, 12/08/2026);
- `fred/series/observations?series_id=WALCL&realtime_start=2024-01-01&realtime_end=2024-01-10`
  → i valori del bilancio Fed **come erano visibili a inizio gennaio 2024**.

È la base per la regola «dato come era noto quel giorno» (P09).

## Come citarla

«Dati: FRED®, Federal Reserve Bank of St. Louis (fred.stlouisfed.org). Questo prodotto usa l'API
di FRED ma non è approvato né certificato dalla Federal Reserve Bank of St. Louis.»

Esempi: [esempi/fred.json](esempi/fred.json), [esempi/alfred-vintage.json](esempi/alfred-vintage.json)
