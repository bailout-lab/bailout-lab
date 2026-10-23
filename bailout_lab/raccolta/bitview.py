"""Metriche on-chain giornaliere da bitview.space (Bitcoin Research Kit).

Serie: MVRV, prezzo realizzato, SOPR.

L'API numera i giorni (`day1`) a partire dal 01/01/2009. Si leggono solo i giorni chiusi e
gli ultimi `GIORNI` a ogni giro, perché la fonte ricalcola: un valore cambiato diventa una
nuova versione, con la data in cui ce ne siamo accorti.
"""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime, timedelta

from bailout_lab.archivio import Archivio, Osservazione
from bailout_lab.raccolta import comune

BASE = "https://bitview.space/api/series"
FONTE = "bitview.space"
GIORNO_ZERO = date(2009, 1, 1)  # indice 0 di `day1`; verificato il 24/10/2026 (6501 = 20/10/2026)
GIORNI = 7
SERIE = {
    "bitview_mvrv": "mvrv",
    "bitview_prezzo_realizzato": "realized_price",
    "bitview_sopr_24h": "sopr_24h",
}


def indice_giorno(giorno: date) -> int:
    return (giorno - GIORNO_ZERO).days


def raccogli(
    archivio: Archivio, ora: datetime, scarica: comune.Scarica = comune.scarica_json
) -> int:
    oggi = ora.astimezone(UTC).date()
    primo, ultimo = oggi - timedelta(days=GIORNI), oggi - timedelta(days=1)
    # `end` dell'API è escluso: con end=oggi si ottiene fino a ieri, l'ultimo giorno chiuso.
    osservazioni: list[Osservazione] = []
    errori: list[str] = []
    for nostro, loro in SERIE.items():
        try:
            r = scarica(f"{BASE}/{loro}/day1?start={primo.isoformat()}&end={oggi.isoformat()}")
            if not isinstance(r, dict) or not isinstance(r.get("data"), list):
                raise comune.RaccoltaError(f"bitview {loro}: risposta inattesa")
            if r.get("start") != indice_giorno(primo):
                raise comune.RaccoltaError(f"bitview {loro}: indice dei giorni cambiato")
        except comune.RaccoltaError as e:
            errori.append(str(e))
            continue
        for posizione, valore in enumerate(r["data"]):
            if valore is None:
                continue
            giorno = primo + timedelta(days=posizione)
            if giorno > ultimo:
                break
            osservazioni.append(
                Osservazione(
                    serie=nostro,
                    istante_valore=datetime(giorno.year, giorno.month, giorno.day, tzinfo=UTC),
                    disponibile_dal=ora,
                    valore=float(valore),
                    fonte=FONTE,
                    versione=comune.versione_da(ora),
                )
            )
    scritte = comune.registra_se_cambiato(archivio, osservazioni)
    if errori:
        raise comune.RaccoltaError("; ".join(errori))
    return scritte


def main() -> int:
    n = raccogli(comune.cartella_archivio(), comune.adesso())
    print(f"bitview: {n} osservazioni nuove")
    return 0


if __name__ == "__main__":
    sys.exit(main())
