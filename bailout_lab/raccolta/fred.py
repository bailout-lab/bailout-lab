"""Macro da FRED/ALFRED (Federal Reserve di St. Louis): tassi, dollaro, liquidità, indici, M2.

ALFRED conserva ogni versione di ogni dato con la data in cui è comparsa (`realtime_start`):
è già «come era noto», quindi qui la disponibilità è quella della fonte, non la nostra.
Per le serie che ALFRED non ha si registra il valore corrente con la nostra data di lettura.
Finestra di `GIORNI` giorni: l'API rifiuta intervalli con troppe date di revisione (2000).
La chiave sta nell'indirizzo (lo vuole FRED): mai in un messaggio d'errore.
"""

from __future__ import annotations

import os
import sys
import urllib.parse
from datetime import UTC, datetime, timedelta

from bailout_lab.archivio import Archivio, Osservazione
from bailout_lab.raccolta import comune

URL = "https://api.stlouisfed.org/fred/series/observations"
FONTE = "FRED/ALFRED"
GIORNI = 365
SERIE = (
    "DGS10",  # rendimento Treasury 10 anni
    "T10Y2Y",  # curva 10 anni - 2 anni
    "DFII10",  # rendimento reale a 10 anni
    "DFEDTARU",  # tasso Fed, limite alto
    "WALCL",  # bilancio della Fed (settimanale)
    "WTREGEN",  # conto del Tesoro presso la Fed (settimanale)
    "RRPONTSYD",  # reverse repo overnight
    "M2SL",  # M2 USA (mensile, ritardo ~2 mesi)
    "DTWEXBGS",  # dollaro, indice ampio
    "VIXCLS",  # VIX
    "NASDAQCOM",  # Nasdaq Composite
    "SP500",  # S&P 500 (FRED lo dà solo dal 2016)
)
# Serie che ALFRED non ha (risponde 400): niente versioni storiche, vale la nostra data di lettura.
SENZA_VERSIONI = frozenset({"SP500"})


def righe_serie(id_serie: str, risposta: object, ora: datetime) -> list[Osservazione]:
    if not isinstance(risposta, dict) or not isinstance(risposta.get("observations"), list):
        raise comune.RaccoltaError(f"fred {id_serie}: risposta inattesa")
    osservazioni = []
    for riga in risposta["observations"]:
        if riga["value"] == ".":  # dato mancante (festivo, non ancora uscito)
            continue
        valore_dal = comune.mezzanotte(riga["date"])
        if id_serie in SENZA_VERSIONI:
            noto_dal, versione = ora, comune.versione_da(ora)
        else:
            # La data di revisione non può precedere il giorno a cui il dato si riferisce.
            noto_dal = max(comune.mezzanotte(riga["realtime_start"]), valore_dal)
            versione = riga["realtime_start"]
        osservazioni.append(
            Osservazione(
                serie=f"fred_{id_serie.lower()}",
                istante_valore=valore_dal,
                disponibile_dal=noto_dal,
                valore=float(riga["value"]),
                fonte=FONTE,
                versione=versione,
            )
        )
    return osservazioni


def raccogli(
    archivio: Archivio, ora: datetime, scarica: comune.Scarica = comune.scarica_json
) -> int:
    chiave = os.environ.get("FRED_API_KEY")
    if not chiave:
        raise comune.RaccoltaError("fred: manca FRED_API_KEY")
    inizio = (ora.astimezone(UTC) - timedelta(days=GIORNI)).date().isoformat()
    scritte, errori = 0, []
    for id_serie in SERIE:
        campi = {
            "series_id": id_serie,
            "api_key": chiave,
            "file_type": "json",
            "observation_start": inizio,
        }
        if id_serie not in SENZA_VERSIONI:
            campi |= {"realtime_start": inizio, "realtime_end": "9999-12-31"}
        try:
            righe = righe_serie(id_serie, scarica(f"{URL}?{urllib.parse.urlencode(campi)}"), ora)
            scritte += (
                comune.registra_se_cambiato(archivio, righe)
                if id_serie in SENZA_VERSIONI
                else archivio.scrivi(righe)
            )
        except comune.RaccoltaError as e:
            errori.append(f"{id_serie}: {e}")
    if errori:
        raise comune.RaccoltaError("; ".join(errori))
    return scritte


def main() -> int:
    n = raccogli(comune.cartella_archivio(), comune.adesso())
    print(f"fred: {n} osservazioni nuove")
    return 0


if __name__ == "__main__":
    sys.exit(main())
