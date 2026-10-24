"""Controllo dello storico dei prezzi: serie continue, buchi elencati, confronto fra fonti.

    python -m bailout_lab.raccolta.controllo_storico

Esce con 0 se: ogni serie giornaliera è continua dal suo primo giorno (i buchi, se ci sono,
sono elencati ma restano un fallimento finché non sono spiegati in `BUCHI_NOTI`) e le coppie di
fonti confrontate concordano entro `SOGLIA` nella quota di giorni dichiarata in `QUOTA`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import duckdb

from bailout_lab.archivio import Archivio
from bailout_lab.raccolta import comune, storico
from bailout_lab.raccolta.storico import FONTI, GIORNO, MINUTO

SOGLIA = 0.005  # scarto relativo massimo fra due fonti: 0,5 %
QUOTA = 0.95  # quota minima di giorni entro la soglia perché le due fonti «concordino»
DAL = date(
    2019, 1, 1
)  # da qui il mercato è unificato; misurato il 24/10/2026: Coinbase/Coin Metrics 95,8 %
RIFERIMENTI = ("btc_usd_coinmetrics_chiusura", "btc_usd_bitview_chiusura")

# Buchi che sappiamo spiegare (data della candela mancante → motivo). Tutto il resto è un difetto.
BUCHI_NOTI: dict[str, dict[date, str]] = {}


def serie_giorno(nome: str) -> str:
    return storico.nome_serie(FONTI[nome], GIORNO, "chiusura")


def serie_minuto(nome: str) -> str:
    return storico.nome_serie(FONTI[nome], MINUTO, "chiusura")


# Coppie da confrontare: due fonti indipendenti dello stesso prezzo in dollari. Binance e OKX
# quotano in USDT, che può scostarsi dal dollaro nei momenti di stress: si confrontano a parte.
# (nome a, nome b, serie a, serie b, giudicata). Solo Coinbase/Coin Metrics, entrambe in dollari e
# indipendenti, decide l'esito; le altre si riportano come informazione.
COPPIE = (
    ("coinbase", "coinmetrics", serie_giorno("coinbase"), RIFERIMENTI[0], True),
    ("coinbase", "bitview", serie_giorno("coinbase"), RIFERIMENTI[1], False),
    ("coinmetrics", "bitview", RIFERIMENTI[0], RIFERIMENTI[1], False),
    ("coinbase (USD)", "binance (USDT)", serie_giorno("coinbase"), serie_giorno("binance"), False),
    ("binance (USDT)", "okx (USDT)", serie_giorno("binance"), serie_giorno("okx"), False),
)


@dataclass
class Copertura:
    serie: str
    primo: date | None
    ultimo: date | None
    giorni: int
    buchi: list[date]


@dataclass
class Confronto:
    a: str
    b: str
    giorni: int
    entro: int
    mediano: float
    peggiori: list[tuple[date, float]]

    @property
    def quota(self) -> float:
        return self.entro / self.giorni if self.giorni else 0.0


def giorni_di(archivio: Archivio, serie: str) -> dict[date, float]:
    """Chiusura di ogni giorno, nell'ultima versione nota."""
    return {o.istante_valore.date(): o.valore for o in archivio.leggi(serie)}


def copertura(archivio: Archivio, serie: str) -> Copertura:
    valori = giorni_di(archivio, serie)
    if not valori:
        return Copertura(serie, None, None, 0, [])
    primo, ultimo = min(valori), max(valori)
    buchi = [
        primo + timedelta(days=n)
        for n in range((ultimo - primo).days + 1)
        if primo + timedelta(days=n) not in valori
    ]
    return Copertura(serie, primo, ultimo, len(valori), buchi)


def confronta(
    archivio: Archivio, a: str, b: str, nome_a: str, nome_b: str, dal: date | None = None
) -> Confronto:
    va, vb = giorni_di(archivio, a), giorni_di(archivio, b)
    scarti = sorted(
        (abs(va[g] / vb[g] - 1), g)
        for g in va.keys() & vb.keys()
        if va[g] > 0 and vb[g] > 0 and (dal is None or g >= dal)
    )
    if not scarti:
        return Confronto(nome_a, nome_b, 0, 0, 0.0, [])
    valori = [s for s, _ in scarti]
    return Confronto(
        nome_a,
        nome_b,
        len(scarti),
        sum(1 for s in valori if s <= SOGLIA),
        valori[len(valori) // 2],
        [(g, s) for s, g in reversed(scarti[-8:])],
    )


@dataclass
class BucoMinuti:
    da: datetime
    a: datetime
    mancanti: int


def minuti(archivio: Archivio, serie: str) -> tuple[datetime | None, datetime | None, int, list]:
    """Primo e ultimo minuto, quanti ce ne sono e i buchi più lunghi (oltre 1 minuto)."""
    file_serie = archivio.percorsi(serie)
    if not file_serie:
        return None, None, 0, []
    con = duckdb.connect()
    try:
        primo, ultimo, n = con.execute(
            "SELECT min(istante_valore), max(istante_valore), count(DISTINCT istante_valore) "
            "FROM read_parquet(?)",
            [file_serie],
        ).fetchone()
        buchi = con.execute(
            "SELECT prima, dopo, date_diff('minute', prima, dopo) - 1 AS mancanti FROM ("
            " SELECT istante_valore AS prima, lead(istante_valore) OVER (ORDER BY istante_valore)"
            " AS dopo FROM (SELECT DISTINCT istante_valore FROM read_parquet(?))"
            ") WHERE dopo IS NOT NULL AND date_diff('minute', prima, dopo) > 1 "
            "ORDER BY mancanti DESC LIMIT 5",
            [file_serie],
        ).fetchall()
    finally:
        con.close()
    return (
        primo.replace(tzinfo=UTC),
        ultimo.replace(tzinfo=UTC),
        n,
        [BucoMinuti(p.replace(tzinfo=UTC), d.replace(tzinfo=UTC), m) for p, d, m in buchi],
    )


def buchi_veri(c: Copertura) -> list[date]:
    nome = c.serie
    noti = {g for fonte in BUCHI_NOTI for g in BUCHI_NOTI[fonte] if fonte in nome}
    return [g for g in c.buchi if g not in noti]


def rapporto(archivio: Archivio, ora: datetime) -> tuple[list[str], bool]:
    righe: list[str] = []
    ok = True
    righe.append("== Giornaliero: copertura e buchi ==")
    for serie in (*[serie_giorno(n) for n in FONTI], *RIFERIMENTI):
        c = copertura(archivio, serie)
        veri = buchi_veri(c)
        stato = (
            "ok"
            if c.giorni and not veri and c.ultimo >= ora.date() - timedelta(days=3)
            else "DIFETTO"
        )
        ok &= stato == "ok"
        elenco = ", ".join(g.isoformat() for g in veri[:10]) + ("…" if len(veri) > 10 else "")
        righe.append(
            f"{c.serie}: {c.primo} → {c.ultimo}, {c.giorni} giorni, {len(c.buchi)} buchi"
            f"{' (' + elenco + ')' if veri else ''} [{stato}]"
        )
    righe.append("")
    righe.append(
        f"== Confronto fra fonti dal {DAL} (scarto ≤ {SOGLIA:.1%}, serve ≥ {QUOTA:.0%}) =="
    )
    for na, nb, a, b, giudicata in COPPIE:
        r = confronta(archivio, a, b, na, nb, DAL)
        stato = ("ok" if r.quota >= QUOTA else "DIFETTO") if giudicata else "solo informativo"
        if giudicata:
            ok &= r.giorni > 0 and r.quota >= QUOTA
        righe.append(
            f"{na} / {nb}: {r.giorni} giorni, {r.quota:.2%} entro la soglia, "
            f"scarto mediano {r.mediano:.3%} [{stato}]"
        )
        for g, s in r.peggiori[:3]:
            righe.append(f"    peggiori: {g} {s:.2%}")
        if giudicata:
            intera = confronta(archivio, a, b, na, nb)
            righe.append(
                f"    tutta la storia: {intera.giorni} giorni, {intera.quota:.2%} entro la soglia, "
                f"peggiore {intera.peggiori[0][0]} {intera.peggiori[0][1]:.2%}"
                if intera.peggiori
                else "    tutta la storia: nessun giorno in comune"
            )
    righe.append("")
    righe.append("== Al minuto ==")
    for nome in FONTI:
        primo, ultimo, n, buchi = minuti(archivio, serie_minuto(nome))
        if primo is None:
            righe.append(f"{serie_minuto(nome)}: nessun dato")
            ok = False
            continue
        attesi = int((ultimo - primo) / MINUTO) + 1
        if ora - ultimo > timedelta(hours=8):  # il pianificatore lo rilegge ogni 3 ore
            righe.append(f"    in ritardo: ultimo minuto {ultimo:%Y-%m-%d %H:%M}")
            ok = False
        righe.append(
            f"{serie_minuto(nome)}: {primo:%Y-%m-%d %H:%M} → {ultimo:%Y-%m-%d %H:%M}, "
            f"{n} minuti su {attesi} ({attesi - n} mancanti)"
        )
        for b in buchi:
            righe.append(
                f"    buco: {b.da:%Y-%m-%d %H:%M} → {b.a:%Y-%m-%d %H:%M} ({b.mancanti} min)"
            )
    return righe, ok


def main(argv: list[str] | None = None) -> int:
    righe, ok = rapporto(comune.cartella_archivio(), datetime.now(UTC))
    print("\n".join(righe))
    print("ok" if ok else "da correggere")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
