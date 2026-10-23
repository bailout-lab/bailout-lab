"""Pianificatore: fa girare i lavori del progetto a intervalli fissi e tiene un file di salute.

Un processo solo, senza servizi esterni. Ogni lavoro è un modulo Python lanciato in un
sottoprocesso con un tempo massimo: un raccoglitore bloccato non ferma gli altri.

    python -m bailout_lab.pianificatore            # avvia il ciclo
    python -m bailout_lab.pianificatore salute     # esce con 0 se il ciclo è vivo e sano

Cartella dei dati: $BAILOUT_LAB_DATI (default `dati/`). Dentro:
- `archivio/`: le osservazioni (vedi `archivio.py`);
- `stato/<lavoro>.json`: l'ultimo esito di ogni lavoro;
- `salute.json`: riscritto a ogni giro, con spazio occupato, spazio libero e problemi.

Avvisi su Telegram se ci sono AVVISI_TELEGRAM_TOKEN e AVVISI_TELEGRAM_CHAT (facoltativo
AVVISI_TELEGRAM_ARGOMENTO); senza, gli avvisi restano nel log.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

GIRO = 30  # secondi fra due controlli dei lavori
SALUTE_SCADUTA = timedelta(minutes=3)  # oltre, il ciclo si considera fermo
MISURA_ARCHIVIO = timedelta(minutes=10)  # contare i file a ogni giro sarebbe lavoro sprecato
RIPETI_AVVISO = timedelta(hours=24)
GB = 1024**3


@dataclass(frozen=True)
class Lavoro:
    """Un modulo da lanciare con `python -m` ogni `ogni`, per al massimo `tempo_massimo` secondi."""

    nome: str
    modulo: str
    ogni: timedelta
    argomenti: tuple[str, ...] = ()
    tempo_massimo: int = 600


# I raccoglitori si aggiungono qui, uno per riga (dal passo P06 della roadmap).
LAVORI: tuple[Lavoro, ...] = ()


def adesso() -> datetime:
    return datetime.now(UTC)


def leggi_json(percorso: Path) -> dict:
    try:
        return json.loads(percorso.read_text())
    except (OSError, ValueError):
        return {}


def scrivi_json(percorso: Path, valore: dict) -> None:
    """Scrittura atomica: chi legge vede il file vecchio o quello nuovo, mai uno a metà."""
    percorso.parent.mkdir(parents=True, exist_ok=True)
    provvisorio = percorso.with_name(f".{percorso.name}.tmp")
    provvisorio.write_text(json.dumps(valore, ensure_ascii=False, indent=1) + "\n")
    provvisorio.replace(percorso)


def dovuto(lavoro: Lavoro, esito: dict, ora: datetime) -> bool:
    """Vero se il lavoro non è mai partito o se dall'ultimo inizio è passato il suo intervallo."""
    inizio = esito.get("inizio")
    return inizio is None or ora - datetime.fromisoformat(inizio) >= lavoro.ogni


def esegui(lavoro: Lavoro, dati: Path, ambiente: dict[str, str] | None = None) -> dict:
    """Lancia il lavoro, registra l'esito in `stato/<nome>.json` e lo restituisce."""
    percorso = dati / "stato" / f"{lavoro.nome}.json"
    precedente = leggi_json(percorso)
    inizio = adesso()
    scrivi_json(percorso, {**precedente, "inizio": inizio.isoformat(), "in_corso": True})
    env = {**os.environ, **(ambiente or {}), "BAILOUT_LAB_DATI": str(dati)}
    comando = [sys.executable, "-m", lavoro.modulo, *lavoro.argomenti]
    try:
        p = subprocess.run(
            comando, env=env, capture_output=True, text=True, timeout=lavoro.tempo_massimo
        )
        stato = "ok" if p.returncode == 0 else "fallito"
        rc, uscita = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        stato, rc, uscita = "tempo scaduto", None, ""
    fine = adesso()
    righe = [r for r in uscita.splitlines() if r.strip()]
    esito = {
        "inizio": inizio.isoformat(),
        "fine": fine.isoformat(),
        "esito": stato,
        "rc": rc,
        "coda": " ".join(righe[-3:])[:300],
        "ultimo_ok": fine.isoformat() if stato == "ok" else precedente.get("ultimo_ok"),
    }
    scrivi_json(percorso, esito)
    print(f"{lavoro.nome}: {stato} (rc={rc})", flush=True)
    return esito


def dimensione(cartella: Path) -> int:
    """Byte occupati dai file sotto `cartella` (0 se non esiste)."""
    totale = 0
    for radice, _, file in os.walk(cartella):
        for nome in file:
            # Un file rinominato mentre lo contiamo non è un problema.
            with contextlib.suppress(OSError):
                totale += os.lstat(os.path.join(radice, nome)).st_size
    return totale


def fotografia(
    dati: Path, lavori: tuple[Lavoro, ...], archivio_byte: int, soglia_gb: float
) -> dict:
    """Lo stato da scrivere in `salute.json`."""
    disco = shutil.disk_usage(dati)
    esiti = {lav.nome: leggi_json(dati / "stato" / f"{lav.nome}.json") for lav in lavori}
    problemi = [
        f"{nome}: {e['esito']}" for nome, e in esiti.items() if e.get("esito", "ok") != "ok"
    ]
    avvisi = []
    if archivio_byte > soglia_gb * GB:
        avvisi.append(f"archivio oltre {soglia_gb:g} GB: {archivio_byte / GB:.1f} GB")
    return {
        "aggiornato": adesso().isoformat(),
        "versione": os.environ.get("BAILOUT_LAB_VERSIONE", "sviluppo"),
        "archivio_byte": archivio_byte,
        "disco_libero_byte": disco.free,
        "disco_totale_byte": disco.total,
        "lavori": esiti,
        "problemi": problemi,
        "avvisi": avvisi,
    }


def controlla_salute(dati: Path, ora: datetime | None = None) -> tuple[bool, str]:
    """Sano = `salute.json` aggiornato da poco e nessun lavoro fermo all'ultimo errore."""
    salute = leggi_json(dati / "salute.json")
    if "aggiornato" not in salute:
        return False, "salute.json assente"
    ritardo = (ora or adesso()) - datetime.fromisoformat(salute["aggiornato"])
    if ritardo > SALUTE_SCADUTA:
        return False, f"ciclo fermo da {int(ritardo.total_seconds())} s"
    if salute.get("problemi"):
        return False, "; ".join(salute["problemi"])
    return True, "ok"


def telegram(testo: str) -> None:
    token, chat = os.environ.get("AVVISI_TELEGRAM_TOKEN"), os.environ.get("AVVISI_TELEGRAM_CHAT")
    if not token or not chat:
        return
    campi = {"chat_id": chat, "text": testo[:4000], "disable_web_page_preview": "true"}
    if os.environ.get("AVVISI_TELEGRAM_ARGOMENTO"):
        campi["message_thread_id"] = os.environ["AVVISI_TELEGRAM_ARGOMENTO"]
    try:
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage",
            urllib.parse.urlencode(campi).encode(),
            timeout=15,
        ).read()
    except OSError as e:
        # Mai il messaggio d'errore completo: contiene l'indirizzo, cioè il token.
        print(f"avviso non inviato: {type(e).__name__}", flush=True)


class Avvisi:
    """Manda un avviso per chiave al massimo una volta ogni `RIPETI_AVVISO`."""

    def __init__(self, dati: Path, invia: Callable[[str], None] = telegram) -> None:
        self.percorso = dati / "stato" / "avvisi.json"
        self.invia = invia

    def manda(self, chiave: str, testo: str, ora: datetime | None = None) -> bool:
        ora = ora or adesso()
        inviati = leggi_json(self.percorso)
        ultimo = inviati.get(chiave)
        if ultimo and ora - datetime.fromisoformat(ultimo) < RIPETI_AVVISO:
            return False
        print(f"AVVISO {testo}", flush=True)
        self.invia(f"Bailout Lab — {testo}")
        scrivi_json(self.percorso, {**inviati, chiave: ora.isoformat()})
        return True


def ciclo(dati: Path, lavori: tuple[Lavoro, ...] = LAVORI) -> None:
    soglia = float(os.environ.get("BAILOUT_LAB_SOGLIA_ARCHIVIO_GB", "20"))
    avvisi = Avvisi(dati)
    in_corso: dict[str, threading.Thread] = {}
    archivio_byte, misurato = 0, None
    print(f"pianificatore avviato, {len(lavori)} lavori, dati in {dati}", flush=True)
    while True:
        ora = adesso()
        for lav in lavori:
            if lav.nome in in_corso and in_corso[lav.nome].is_alive():
                continue
            if dovuto(lav, leggi_json(dati / "stato" / f"{lav.nome}.json"), ora):
                t = threading.Thread(target=esegui, args=(lav, dati), daemon=True)
                in_corso[lav.nome] = t
                t.start()
        if misurato is None or ora - misurato >= MISURA_ARCHIVIO:
            archivio_byte, misurato = dimensione(dati / "archivio"), ora
        salute = fotografia(dati, lavori, archivio_byte, soglia)
        scrivi_json(dati / "salute.json", salute)
        for testo in salute["problemi"] + salute["avvisi"]:
            avvisi.manda(testo.split(":")[0], testo)
        time.sleep(GIRO)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    dati = Path(os.environ.get("BAILOUT_LAB_DATI", "dati"))
    if argv == ["salute"]:
        sano, motivo = controlla_salute(dati)
        print(motivo)
        return 0 if sano else 1
    if argv:
        print(__doc__)
        return 2
    # Come primo processo di un container Python ignora SIGTERM: senza questo lo spegnimento
    # aspetta il tempo massimo e poi uccide.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    dati.mkdir(parents=True, exist_ok=True)
    ciclo(dati)
    return 0


if __name__ == "__main__":
    sys.exit(main())
