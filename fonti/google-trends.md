# Google Trends

**Esito: non utilizzabile in modo stabile.** Verificato il 23/10/2026.

| | |
|---|---|
| API ufficiale | **Nessuna** disponibile al grande pubblico |
| Endpoint non documentati | `…/trends/api/explore` → HTTP 400, `…/trends/api/dailytrends` → HTTP 404 |
| Librerie non ufficiali | esistono ma si appoggiano proprio a quegli endpoint: fragili e soggette a blocchi |

Non si costruisce un raccoglitore su una cosa che può smettere di funzionare senza preavviso.

## Alternativa candidata: visite di Wikipedia (da valutare in P23)

L'API delle visite di Wikimedia risponde, senza chiave e a costo zero:

```
GET https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/it.wikipedia/all-access/user/Bitcoin/daily/20261020/20261022
```

(provata il 23/10/2026, visite giornaliere della voce «Bitcoin» su it.wikipedia). È un indicatore
di attenzione diverso da Trends: **prima di usarlo va misurato se dice qualcosa sul prezzo**, come
ogni altro dato.

Esempio: [esempi/wikipedia-pageviews.json](esempi/wikipedia-pageviews.json)
