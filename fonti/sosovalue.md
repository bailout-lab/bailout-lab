# SoSoValue — flussi degli ETF spot

**Esito: funziona con la chiave gratuita.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `POST https://openapi.sosovalue.com/openapi/v2/etf/historicalInflowChart` con corpo `{"type":"us-btc-spot"}` |
| Chiave | **Sì**, si chiede su `https://sosovalue.com/developer/dashboard` («Apply your Key», approvazione non immediata); va nell'intestazione `x-soso-api-key` e in `SOSOVALUE_API_KEY` nel proprio `.env` |
| Cosa dà | per ogni giorno: flusso netto (`totalNetInflow`), volume scambiato, patrimonio netto degli ETF, flusso cumulato, tutti in dollari |
| Frequenza | giornaliera (ultimo giorno al 23/10: 22/10) |
| Storico | **300 giorni per chiamata**: dal 14/08/2025 al 22/10/2026. Gli ETF spot esistono dal gennaio 2024, quindi per risalire oltre serve verificare se l'endpoint accetta un intervallo (da fare in P22) o altra fonte |
| Limiti | **100 richieste al minuto e 10.000 al mese** (verificato nelle intestazioni `x-ratelimit-*` della risposta; la documentazione parla di numeri diversi: contano quelli reali) |

Per i flussi giornalieri bastano poche chiamate al giorno: i limiti non sono un problema.

## Nota sulla versione dell'API

La documentazione ufficiale indica `/openapi/v1`; la chiamata qui sopra, su `/openapi/v2`, risponde
correttamente. I raccoglitori dovranno controllare ogni giorno che la forma della risposta non
cambi.

## Come citarla

«Dati: SoSoValue.» (condizioni d'uso da rileggere sul sito prima della pubblicazione)

Esempio: [esempi/sosovalue.json](esempi/sosovalue.json)
