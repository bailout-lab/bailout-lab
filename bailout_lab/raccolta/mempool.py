"""Fee consigliate da mempool.space (sat/vB): una fotografia a ogni giro."""

from __future__ import annotations

import sys
from datetime import datetime

from bailout_lab.archivio import Archivio, Osservazione
from bailout_lab.raccolta import comune

URL = "https://mempool.space/api/v1/fees/recommended"
FONTE = "mempool.space"
CAMPI = {
    "fastestFee": "mempool_fee_veloce",
    "halfHourFee": "mempool_fee_mezzora",
    "hourFee": "mempool_fee_ora",
    "economyFee": "mempool_fee_economica",
    "minimumFee": "mempool_fee_minima",
}


def raccogli(
    archivio: Archivio, ora: datetime, scarica: comune.Scarica = comune.scarica_json
) -> int:
    r = scarica(URL)
    if not isinstance(r, dict) or not all(isinstance(r.get(k), int | float) for k in CAMPI):
        raise comune.RaccoltaError("mempool.space: risposta inattesa")
    # È una fotografia di adesso: vale e si conosce nello stesso istante.
    return archivio.scrivi(
        Osservazione(nome, ora, ora, float(r[campo]), FONTE, comune.versione_da(ora))
        for campo, nome in CAMPI.items()
    )


def main() -> int:
    n = raccogli(comune.cartella_archivio(), comune.adesso())
    print(f"mempool: {n} osservazioni nuove")
    return 0


if __name__ == "__main__":
    sys.exit(main())
