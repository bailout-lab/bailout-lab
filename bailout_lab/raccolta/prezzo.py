"""Prezzo giornaliero di BTC-USD da Coinbase Exchange (candele chiuse, UTC).

Candela = [inizio, minimo, massimo, apertura, chiusura, volume]. Si registrano solo i giorni già
chiusi: quello in corso cambia ogni minuto e non è un dato.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

from bailout_lab.archivio import Archivio, Osservazione
from bailout_lab.raccolta import comune

URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400"
FONTE = "coinbase"
GIORNI = 10  # ultime candele da rileggere a ogni giro: un buco di qualche giorno si ripara da solo
CAMPI = {
    1: "btc_usd_coinbase_minimo",
    2: "btc_usd_coinbase_massimo",
    3: "btc_usd_coinbase_apertura",
    4: "btc_usd_coinbase_chiusura",
    5: "btc_usd_coinbase_volume",
}


def raccogli(
    archivio: Archivio, ora: datetime, scarica: comune.Scarica = comune.scarica_json
) -> int:
    candele = scarica(URL)
    if not isinstance(candele, list):
        raise comune.RaccoltaError("coinbase: risposta inattesa")
    chiuse = [c for c in candele if datetime.fromtimestamp(c[0], UTC) + timedelta(days=1) <= ora]
    chiuse.sort(key=lambda c: c[0])
    osservazioni = [
        Osservazione(
            serie=nome,
            istante_valore=datetime.fromtimestamp(c[0], UTC),
            disponibile_dal=ora,
            valore=float(c[posizione]),
            fonte=FONTE,
            versione=comune.versione_da(ora),
        )
        for c in chiuse[-GIORNI:]
        for posizione, nome in CAMPI.items()
    ]
    return comune.registra_se_cambiato(archivio, osservazioni)


def main() -> int:
    n = raccogli(comune.cartella_archivio(), comune.adesso())
    print(f"prezzo: {n} osservazioni nuove")
    return 0


if __name__ == "__main__":
    sys.exit(main())
