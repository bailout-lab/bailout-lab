# BGeometrics (bitcoin-data.com)

**Esito: funziona, ma gli ultimi 7 giorni non sono gratuiti.** Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://bitcoin-data.com/v1/<metrica>/last` (ultimo valore) |
| Chiave | No per il livello gratuito |
| Formato | JSON |
| Ritardo | Il valore «ultimo» del 23/10 portava la data **16/10** e il campo `"delayed": true` con il messaggio che i dati in tempo reale (ultimi 7 giorni) richiedono un abbonamento |
| Limiti | 15 richieste al giorno nel livello gratuito (**dichiarato** dalla fonte, non misurato) |

## Uso nel progetto

Non è una fonte continua: ha sempre una settimana di ritardo e poche richieste. Serve **solo per
confronti storici singoli** (es. un valore di MVRV-Z di una settimana fa contro il nostro
calcolo). Non entra nei raccoglitori.

Metriche provate: `mvrv-zscore`, `sopr`.

## Come citarla

«Dati: BGeometrics (bitcoin-data.com).»

Esempi: [esempi/bgeometrics-mvrv-z.json](esempi/bgeometrics-mvrv-z.json),
[esempi/bgeometrics-sopr.json](esempi/bgeometrics-sopr.json)
