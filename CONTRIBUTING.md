# Come partecipare a Bailout Lab

Grazie per l'interesse. Questa guida spiega come proporre una modifica e quali regole tengono il
progetto affidabile.

## In quattro passi

1. **Leggi** la [roadmap](ROADMAP.md) per capire a che punto siamo.
2. **Scegli un compito** nella scheda Issues (i più adatti per iniziare hanno l'etichetta
   *good first issue*) oppure apri una issue per proporre un'idea. Per i lavori grossi conviene
   parlarne prima, così nessuno lavora a vuoto.
3. **Fai il fork** del repo, lavora su un ramo tuo e apri una **pull request** verso `main`.
4. **Test e revisione.** Prima girano i controlli automatici, poi c'è la revisione. Se tutto va
   bene la modifica viene unita, e il tuo nome resta nella storia del progetto.

Su `main` non si scrive direttamente, nemmeno chi gestisce il progetto: si entra solo con una
pull request che passa i controlli.

## Cosa puoi fare

- una nuova **scheda di studio** o la correzione di una esistente;
- un nuovo **dato**, purché da una fonte gratuita;
- una **correzione di calcolo**, con un test che mostri l'errore;
- la **verifica** di un risultato pubblicato;
- una **traduzione**.

Il modello del Bailout Indicator cambia solo con una nuova versione approvata, mai con una
modifica diretta al modello in uso.

## Regole

- **Mai segreti nel repo.** Niente chiavi, token o password, nemmeno di prova. Le chiavi si
  leggono dalle variabili d'ambiente: i nomi sono in [`.env.example`](.env.example), i valori
  restano sul tuo computer in un file `.env`, che git ignora. Ogni pull request passa da
  [gitleaks](https://github.com/gitleaks/gitleaks), e una chiave trovata la blocca.
- **Il dato come era noto.** Un dato storico si salva con l'istante in cui era davvero
  disponibile, non con quello a cui si riferisce.
- **Niente dati pesanti nel repo.** Vanno nel repo codice, schede e risultati. L'archivio dei
  dati si ricrea con gli script.
- **Solo fonti gratuite,** indicate nella scheda della fonte con le istruzioni per citarla.
- **Licenze compatibili.** Non copiare codice di altri progetti con licenze incompatibili con la
  MIT (per esempio AGPL o GPL): ispirarsi a un'idea va bene, copiarne il codice no.
- **Niente consigli finanziari.** Testi e schede descrivono i dati e i loro limiti. Non dicono
  mai «compra», «vendi» o «quanto».

## Prima di aprire la pull request

Installa gitleaks e controlla di non aver committato segreti:

```sh
gitleaks git --redact -v .
```

Puoi anche farlo controllare a git a ogni commit, aggiungendo questa riga a
`.git/hooks/pre-commit`:

```sh
gitleaks git --pre-commit --staged --redact
```

I controlli automatici rifanno comunque la stessa verifica su tutta la storia.

Il codice è Python (3.12 o più recente) e si gestisce con [uv](https://docs.astral.sh/uv/).
In locale, prima di aprire la pull request:

```sh
uv sync                     # installa le dipendenze bloccate
uv run ruff check .         # controllo dello stile
uv run ruff format --check .
uv run pytest               # test
```

I test non devono scaricare dati da internet né scrivere fuori da una cartella temporanea.

I raccoglitori girano col pianificatore, che li lancia a intervalli fissi e scrive lo stato in
`dati/salute.json`. Un nuovo raccoglitore si aggiunge con una riga in `LAVORI`
(`bailout_lab/pianificatore.py`). Per provarlo in locale:

```sh
uv run python -m bailout_lab.pianificatore           # ciclo continuo, Ctrl+C per fermarlo
uv run python -m bailout_lab.pianificatore salute    # 0 = sano
```

Ogni raccoglitore è un modulo `bailout_lab.raccolta.<nome>` con una funzione `raccogli` (la fonte
si passa come argomento, così i test non usano internet) e un `main`. Si lancia a mano con
`uv run python -m bailout_lab.raccolta.<nome>`. Un valore si registra con l'istante in cui lo
abbiamo conosciuto, e uno già noto e identico non si riscrive. Lo stato dell'archivio si controlla
con `uv run python -m bailout_lab.raccolta.controllo`.

## Lingua

La documentazione è in italiano. Issue e pull request in inglese sono benvenute.

## Licenza dei contributi

Proponendo una modifica accetti che venga distribuita con le licenze del progetto: il codice
sotto [MIT](LICENSE), schede e testi sotto [CC BY 4.0](LICENSE-CC-BY-4.0.txt).

Chi partecipa segue il [codice di comportamento](CODE_OF_CONDUCT.md).
