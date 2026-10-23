# Sicurezza

## Come segnalare un problema

Se trovi un problema di sicurezza **non aprire una issue pubblica**. Segnalalo in privato:

- dalla scheda **Security** del repo, con il pulsante **Report a vulnerability**
  ([link diretto](https://github.com/bailout-lab/bailout-lab/security/advisories/new));
- oppure scrivendo a **info@bailout.website**.

Indica cosa hai trovato, dove, come riprodurlo e che conseguenze può avere. Ti rispondiamo
appena possibile, di solito entro una settimana, e ti teniamo aggiornato fino alla correzione.
Se vuoi, il tuo nome verrà citato tra i ringraziamenti.

## Cosa ci interessa

- un segreto (chiave, token, password) finito nel repo o nella sua storia;
- un modo per far eseguire codice non previsto ai controlli automatici o ai raccoglitori;
- dati di una fonte che possono essere manipolati per alterare l'indicatore o il registro
  pubblico;
- dipendenze con vulnerabilità note.

## Cosa facciamo per prevenire

- ricerca automatica di segreti a ogni pull request, su tutta la storia (gitleaks), più secret
  scanning e push protection di GitHub;
- `main` modificabile solo con pull request che passano i controlli;
- controlli automatici eseguiti sui server di GitHub, con permessi di sola lettura;
- azioni dei controlli fissate a una versione precisa e verificata.
