# SEC EDGAR

**Esito: funziona con uno User-Agent dichiarato.** Senza intestazione che dichiari chi chiama, la
SEC risponde **403** («Undeclared Automated Tool»). Verificato il 23/10/2026.

| | |
|---|---|
| Indirizzo | `https://data.sec.gov/submissions/CIK##########.json`, `…/api/xbrl/companyconcept/…` |
| Chiave | No, ma serve `User-Agent` con nome del progetto e **un recapito di contatto** (richiesta della SEC) |
| Esempio provato | CIK `0001050446` = Strategy Inc (ticker MSTR e le azioni privilegiate): ultimi documenti del 20/10/2026 |
| XBRL | `…/xbrl/companyconcept/CIK0001050446/us-gaap/Assets.json` risponde |
| Limiti | la SEC dichiara un massimo di circa 10 richieste al secondo (**dichiarato**) |

## Da decidere prima di P21

Lo User-Agent della SEC deve contenere un indirizzo di contatto valido del progetto. Non è stato
messo nel repo: va scelto un recapito pubblico dedicato (non personale) e inserito come
configurazione, non nel codice.

## Come citarla

«Dati: U.S. Securities and Exchange Commission, EDGAR.»

Esempio: [esempi/edgar.json](esempi/edgar.json)
