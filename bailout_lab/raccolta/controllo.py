"""Controllo dell'archivio: ogni serie è abbastanza recente e, dove serve, senza buchi?

    python -m bailout_lab.raccolta.controllo [giorni]     # default: 3

Esce con 0 se tutto è a posto. I buchi si cercano solo dove la fonte ha un valore ogni giorno
(prezzo e on-chain); per macro, ETF (niente weekend) e fee si controlla la freschezza.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

from bailout_lab.archivio import Archivio
from bailout_lab.raccolta import bitview, comune, etf, fred, mempool, prezzo

GIORNALIERE = (*bitview.SERIE, prezzo.CAMPI[4])  # una per giorno, weekend compresi
# Quanto vecchio può essere l'ultimo valore prima di dare allarme.
FRESCHEZZA = {
    **{s: timedelta(days=2) for s in GIORNALIERE},
    **{s: timedelta(days=5) for s in etf.CAMPI.values()},
    **{f"fred_{i.lower()}": timedelta(days=10) for i in fred.SERIE},
    "fred_m2sl": timedelta(days=100),
    "fred_walcl": timedelta(days=12),
    "fred_wtregen": timedelta(days=12),
    **{s: timedelta(hours=14) for s in mempool.CAMPI.values()},
}


def controlla(archivio: Archivio, ora: datetime, giorni: int = 3) -> list[str]:
    problemi = []
    for serie, massimo in FRESCHEZZA.items():
        righe = archivio.leggi(serie, noto_al=ora)
        if not righe:
            problemi.append(f"{serie}: nessun dato")
            continue
        # Per le fee l'istante è la lettura; per le altre il giorno a cui il dato si riferisce.
        if ora - righe[-1].istante_valore > massimo:
            problemi.append(f"{serie}: ultimo valore {righe[-1].istante_valore:%d/%m/%Y %H:%M}")
        if serie in GIORNALIERE:
            presenti = {o.istante_valore.date() for o in righe}
            for n in range(1, giorni + 1):
                giorno = (ora - timedelta(days=n)).date()
                if giorno not in presenti:
                    problemi.append(f"{serie}: manca il {giorno:%d/%m/%Y}")
        # Un valore non può essere noto prima del suo istante: l'archivio lo vieta già,
        # ma qui si guarda anche che non ce ne siano di «noti» nel futuro.
        if any(o.disponibile_dal > ora for o in righe):
            problemi.append(f"{serie}: disponibilità nel futuro")
    return problemi


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    giorni = int(argv[0]) if argv else 3
    problemi = controlla(comune.cartella_archivio(), datetime.now(UTC), giorni)
    for p in problemi:
        print(p)
    print("ok" if not problemi else f"{len(problemi)} problemi")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
