# SoSoValue — flussi degli ETF spot

**Esito: in attesa della chiave.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://openapi.sosovalue.com/openapi/v2/etf/historicalInflowChart` (POST) |
| Chiave | **Sì, gratuita**, da richiedere sul sito di SoSoValue; va nell'intestazione `x-soso-api-key` |
| Cosa risponde senza chiave valida | HTTP 401 `{"code":400101,"message":"API Key is invalid or does not exist…"}`: l'endpoint esiste, manca solo la chiave |
| Cosa darà (dalla documentazione) | flussi netti giornalieri degli ETF spot Bitcoin, totali e per fondo |
| Limiti | da misurare dopo l'arrivo della chiave |

## Per chiudere questa scheda

1. Ottenere la chiave gratuita e metterla in `SOSOVALUE_API_KEY` nel proprio `.env`.
2. Rifare la chiamata, salvare la risposta in `esempi/sosovalue.json`, annotare storico (data
   del primo flusso) e limiti, sostituire questa nota.

Finché manca, i flussi ETF non sono recuperabili in modo automatico (vedi [farside.md](farside.md)).

## Come citarla

«Dati: SoSoValue.» (da confermare con le loro condizioni quando la chiave è attiva)
