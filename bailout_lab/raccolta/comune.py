"""Pezzi comuni ai raccoglitori: scarico da HTTP, cartella dei dati e scrittura senza ripetizioni.

Regola dell'archivio «come era noto»: un valore letto da noi è noto *dall'istante in cui lo
leggiamo* (o dalla chiusura del giorno, se più tardi). Se la fonte lo ricalcola, il nuovo valore
diventa una nuova versione con la propria data; se è identico non scriviamo niente.
"""

from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path

from bailout_lab.archivio import Archivio, Osservazione

USER_AGENT = "bailout-lab/0.1 (+https://github.com/bailout-lab/bailout-lab)"

Scarica = Callable[..., object]


class RaccoltaError(RuntimeError):
    """Errore di un raccoglitore. Mai l'indirizzo nel messaggio: può contenere una chiave."""


def scarica_json(
    url: str,
    corpo: dict | None = None,
    intestazioni: dict[str, str] | None = None,
    tentativi: int = 3,
    timeout: int = 30,
) -> object:
    """GET (o POST se c'è `corpo`) che restituisce il JSON, riprovando con pause crescenti."""
    host = urllib.parse.urlsplit(url).netloc
    campi = {"User-Agent": USER_AGENT, "Accept": "application/json", **(intestazioni or {})}
    dati = None
    if corpo is not None:
        dati = json.dumps(corpo).encode()
        campi["Content-Type"] = "application/json"
    ultimo = "errore sconosciuto"
    for tentativo in range(tentativi):
        if tentativo:
            time.sleep(2**tentativo)
        try:
            richiesta = urllib.request.Request(url, data=dati, headers=campi)
            with urllib.request.urlopen(richiesta, timeout=timeout) as risposta:
                return json.loads(risposta.read())
        except urllib.error.HTTPError as e:
            ultimo = f"HTTP {e.code}"
            if e.code < 500 and e.code != 429:
                break  # un errore nostro non migliora riprovando
        except (OSError, ValueError) as e:
            ultimo = type(e).__name__
    raise RaccoltaError(f"{host}: {ultimo}")


def adesso() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def cartella_archivio() -> Archivio:
    return Archivio(Path(os.environ.get("BAILOUT_LAB_DATI", "dati")) / "archivio")


def versione_da(istante: datetime) -> str:
    """Versione ordinabile in ordine cronologico, ricavata dall'istante di lettura."""
    return istante.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def mezzanotte(giorno: str | datetime) -> datetime:
    """`2026-10-22` (o un istante) → 22/10/2026 00:00 UTC."""
    if isinstance(giorno, str):
        giorno = datetime.fromisoformat(giorno)
    if giorno.tzinfo is None:
        giorno = giorno.replace(tzinfo=UTC)
    return giorno.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


def registra_se_cambiato(archivio: Archivio, osservazioni: Iterable[Osservazione]) -> int:
    """Scrive solo le osservazioni nuove o diverse dall'ultimo valore noto per quell'istante."""
    per_serie: dict[str, list[Osservazione]] = {}
    for o in osservazioni:
        per_serie.setdefault(o.serie, []).append(o)
    scritte = 0
    for serie, righe in per_serie.items():
        noti = {o.istante_valore: o.valore for o in archivio.leggi(serie)}
        nuove = [
            o
            for o in righe
            if o.istante_valore not in noti
            or not math.isclose(noti[o.istante_valore], o.valore, rel_tol=1e-9, abs_tol=1e-12)
        ]
        scritte += archivio.scrivi(nuove)
    return scritte
