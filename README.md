# Bailout Lab

**Analisi di Bitcoin aperta, verificabile e spiegata in italiano.** Bailout Lab unisce in un
unico posto i tre modi di guardare Bitcoin: l'analisi grafica e di mercato, l'analisi
fondamentale e macro, l'analisi on-chain. L'obiettivo finale è il **Bailout Indicator**: un
valore per ciascun orizzonte (giorno, settimana, mese, anno), con il metodo pubblico e un
registro dei risultati che nessuno può ritoccare.

È un progetto di [Bailout](https://bailout.website), l'Academy italiana su Bitcoin.

> **Stato: in costruzione.** Il repo è appena nato: per ora contiene le regole del progetto e la
> [roadmap](ROADMAP.md). Il codice arriva passo dopo passo.

*English: Bailout Lab is an open research project on Bitcoin that combines market, macro and
on-chain data into one indicator per time horizon, with a public method and a tamper-evident
track record. Documentation is in Italian; contributions in English are welcome.*

---

## Come è fatto

Tre livelli, uno sopra l'altro.

1. **L'archivio dei dati.** Circa 150 serie (prezzo e derivati, macro e calendario, on-chain),
   ognuna salvata con l'istante in cui il dato era davvero disponibile. Così uno studio sul
   passato usa solo ciò che si poteva sapere in quel momento.
2. **Le schede di studio.** Per ogni dato una scheda: che cos'è, come si calcola, da dove viene e
   soprattutto *quanto ha detto storicamente sul prezzo*, e su quale orizzonte. Sono il cuore
   didattico del progetto e il lavoro che la community può fare insieme a noi.
3. **Il Bailout Indicator.** Combina solo i dati che hanno superato la prova delle schede: un
   valore per orizzonte, da −100 a +100, con la probabilità stimata, la fase di mercato, i tre
   motivi principali e i livelli chiave vicini.

## Il metodo, senza scorciatoie

Prendere 150 serie e tenere quelle che «assomigliano» al prezzo è il modo più sicuro per
costruire qualcosa che funziona sul passato e male da domani. Le regole del progetto:

- **Il dato come era noto quel giorno.** Molti dati vengono rivisti dopo: si usa la versione
  disponibile in quel momento.
- **Un orizzonte alla volta.** On-chain e macro contano su mese e anno; derivati e flusso ordini
  su ore e giorni. Ogni dato si misura su tutti gli orizzonti e si usa solo dove dice qualcosa.
- **Misure oneste**: correlazione di rango, anticipo o ritardo rispetto al prezzo, stabilità
  nei diversi regimi di mercato.
- **Prova fuori campione**, a finestre che avanzano, senza sbirciare il futuro.
- **Battere i riferimenti semplici**: tenere e basta, la media a 200 giorni, il caso. Se una
  versione non li batte, non esce.
- **I limiti si dicono ad alta voce.** Bitcoin ha pochi cicli completi: sull'orizzonte annuale
  gli esempi indipendenti sono una manciata, e lo scriviamo accanto al numero.

Ogni valore emesso dall'indicatore finisce in un registro pubblico, la cui impronta viene
marcata su Bitcoin con [OpenTimestamps](https://opentimestamps.org): i risultati, anche quelli
brutti, restano visibili e non si possono riscrivere.

## Solo dati gratuiti

Il progetto usa esclusivamente fonti gratuite, tra cui:
[bitview.space](https://bitview.space) (istanza pubblica del
[Bitcoin Research Kit](https://github.com/bitcoinresearchkit/mono)),
[Coin Metrics Community](https://docs.coinmetrics.io/packages/coin-metrics-community-data),
[mempool.space](https://mempool.space), le API pubbliche degli exchange e di Deribit,
FRED/ALFRED, BCE, CFTC ed EDGAR. Ogni fonte avrà la sua scheda in `fonti/`, con limiti e
indicazioni su come citarla.

## Come partecipare

Leggi la [roadmap](ROADMAP.md) e la guida [CONTRIBUTING.md](CONTRIBUTING.md). Puoi segnalare un
errore o proporre un dato dalla scheda **Issues**. L'apertura completa alla community, con le
Discussions e i primi compiti per chi inizia, è prevista nella fase 2.

Per un problema di sicurezza non aprire una issue pubblica: segui [SECURITY.md](SECURITY.md).

## Avvertenza

Bailout Lab è un progetto di ricerca e divulgazione. **Niente di quello che trovi qui è una
consulenza finanziaria** né un invito a comprare o vendere. Il Bailout Indicator è un valore per
orizzonte, uguale per tutti: non tiene conto della situazione di chi lo guarda e non dice mai
«compra», «vendi» o «quanto». I risultati passati non garantiscono quelli futuri, e Bitcoin è
un bene molto volatile.

## Licenze

- **Codice:** [MIT](LICENSE).
- **Schede, documentazione e testi:** [Creative Commons Attribuzione 4.0](LICENSE-CC-BY-4.0.txt),
  citando «Bailout Lab — bailout.website».

Il nome e il marchio «Bailout» restano del progetto Bailout e non sono coperti da queste licenze.
