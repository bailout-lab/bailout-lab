# BCE — Statistical Data Warehouse

**Esito: funziona.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://data-api.ecb.europa.eu/service/data/<flusso>/<chiave>` |
| Chiave | **No** |
| Formato | SDMX; `format=jsondata` per il JSON |
| Serie provata | `FM/B.U2.EUR.4F.KR.MRR_FR.LEV`: tasso sulle operazioni di rifinanziamento principali. Ultime 3 osservazioni: 2,15 · 2,40 · 2,65 (le date delle variazioni sono nella risposta) |
| Frequenza | a ogni variazione del tasso (la serie è «a eventi») |
| Limiti | non dichiarati nella risposta |

## Nota

Il formato SDMX è meno immediato di FRED: la risposta separa i valori (`dataSets`) dalle date
(`structure.dimensions.observation`). Il raccoglitore dovrà ricomporle.

## Come citarla

«Dati: Banca Centrale Europea, ECB Data Portal.»

Esempio: [esempi/bce.json](esempi/bce.json)
