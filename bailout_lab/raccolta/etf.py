"""Flussi giornalieri degli ETF spot su Bitcoin USA da SoSoValue.

Serve la chiave gratuita SOSOVALUE_API_KEY.

L'endpoint dà gli ultimi 300 giorni a ogni chiamata. Il flusso di un giorno esce la sera dopo
la chiusura di Wall Street: lo registriamo con la data in cui lo leggiamo la prima volta, e a
ogni giro riscriviamo solo ciò che è nuovo o corretto. Nei weekend e nei festivi non ci sono
valori: non sono buchi.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

from bailout_lab.archivio import Archivio, Osservazione
from bailout_lab.raccolta import comune

URL = "https://openapi.sosovalue.com/openapi/v2/etf/historicalInflowChart"
FONTE = "sosovalue"
CAMPI = {
    "totalNetInflow": "etf_btc_spot_flusso_netto_usd",
    "totalValueTraded": "etf_btc_spot_volume_usd",
    "totalNetAssets": "etf_btc_spot_patrimonio_usd",
    "cumNetInflow": "etf_btc_spot_flusso_cumulato_usd",
}


def raccogli(
    archivio: Archivio, ora: datetime, scarica: comune.Scarica = comune.scarica_json
) -> int:
    chiave = os.environ.get("SOSOVALUE_API_KEY")
    if not chiave:
        raise comune.RaccoltaError("sosovalue: manca SOSOVALUE_API_KEY")
    r = scarica(URL, corpo={"type": "us-btc-spot"}, intestazioni={"x-soso-api-key": chiave})
    if not isinstance(r, dict) or r.get("code") != 0 or not isinstance(r.get("data"), list):
        raise comune.RaccoltaError("sosovalue: risposta inattesa")
    osservazioni = [
        Osservazione(
            serie=nome,
            istante_valore=comune.mezzanotte(riga["date"]),
            disponibile_dal=ora,
            valore=float(riga[campo]),
            fonte=FONTE,
            versione=comune.versione_da(ora),
        )
        for riga in r["data"]
        for campo, nome in CAMPI.items()
        if riga.get(campo) is not None
    ]
    return comune.registra_se_cambiato(archivio, osservazioni)


def main() -> int:
    n = raccogli(comune.cartella_archivio(), comune.adesso())
    print(f"etf: {n} osservazioni nuove")
    return 0


if __name__ == "__main__":
    sys.exit(main())
