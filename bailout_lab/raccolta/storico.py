"""Storico dei prezzi di BTC: candele giornaliere e al minuto da più exchange, con ripresa.

    python -m bailout_lab.raccolta.storico giorno              # giornaliero, tutte le fonti
    python -m bailout_lab.raccolta.storico minuto <exchange>   # al minuto di un exchange

Al minuto ogni lancio riparte dall'ultimo istante già nell'archivio e si ferma allo scadere
del tempo concesso (il giornaliero, poche chiamate, rilegge sempre tutto): il primo
caricamento di anni di candele al minuto richiede qualche lancio, poi ogni giro legge solo gli
ultimi minuti. Si registrano solo candele chiuse.

Onestà sulla data di disponibilità: lo storico caricato oggi ha `disponibile_dal` = istante in
cui l'abbiamo letto, non quello in cui l'exchange lo pubblicò. Per le candele degli exchange,
che a candela chiusa non si ricalcolano, la differenza non cambia i valori; resta vero che
«come era noto» vale davvero solo dal giorno in cui abbiamo iniziato a registrare.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from bailout_lab.archivio import Archivio, Osservazione
from bailout_lab.raccolta import bitview, comune

MINUTO = timedelta(minutes=1)
GIORNO = timedelta(days=1)
CAMPI = ("apertura", "massimo", "minimo", "chiusura", "volume")  # volume in BTC
SOGLIA_SCRITTURA = 20_000  # candele da accumulare prima di scrivere (≈ due settimane al minuto)
ATTESA_MINUTO = timedelta(hours=3)  # a regime si scrive ogni tre ore: pochi file, non uno all'ora
TEMPO_DEFAULT = 2700  # secondi di lavoro per lancio al minuto; il pianificatore ne concede di più

COIN_METRICS = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
PRIMO_COIN_METRICS = "2010-07-18"
PRIMO_BITVIEW = date(2010, 8, 16)  # prima di questo giorno il prezzo è 0 (nessuno scambio noto)


@dataclass(frozen=True)
class Candela:
    istante: datetime  # apertura della candela, UTC
    apertura: float
    massimo: float
    minimo: float
    chiusura: float
    volume: float


# Una pagina = (candele in ordine di tempo, istante da cui chiedere la pagina dopo).
Pagina = tuple[list[Candela], datetime]
Pescatore = Callable[[comune.Scarica, datetime, timedelta], Pagina]


def _ms(istante: datetime) -> int:
    return int(istante.timestamp() * 1000)


def _da_ms(ms: int | str) -> datetime:
    return datetime.fromtimestamp(int(ms) / 1000, UTC)


def _iso(istante: datetime) -> str:
    return istante.strftime("%Y-%m-%dT%H:%M:%SZ")


def binance(scarica: comune.Scarica, da: datetime, passo: timedelta) -> Pagina:
    """BTCUSDT spot, fino a 1000 candele per chiamata a partire da `da`."""
    intervallo = "1m" if passo == MINUTO else "1d"
    righe = scarica(
        "https://api.binance.com/api/v3/klines"
        f"?symbol=BTCUSDT&interval={intervallo}&startTime={_ms(da)}&limit=1000"
    )
    if not isinstance(righe, list):
        raise comune.RaccoltaError("binance: risposta inattesa")
    candele = [Candela(_da_ms(r[0]), *(float(x) for x in r[1:6])) for r in righe]
    return candele, (candele[-1].istante + passo if candele else da + 1000 * passo)


def okx(scarica: comune.Scarica, da: datetime, passo: timedelta) -> Pagina:
    """BTC-USDT spot. `before` e `after` (entrambi esclusi) tagliano una finestra di 100 candele."""
    n = 100
    barra = "1m" if passo == MINUTO else "1Dutc"  # `1D` semplice parte alle 16:00 UTC
    fine = da + n * passo
    r = scarica(
        "https://www.okx.com/api/v5/market/history-candles"
        f"?instId=BTC-USDT&bar={barra}&before={_ms(da) - 1}&after={_ms(fine)}&limit={n}"
    )
    if not isinstance(r, dict) or r.get("code") != "0" or not isinstance(r.get("data"), list):
        raise comune.RaccoltaError("okx: risposta inattesa")
    # La risposta va dalla più recente alla più vecchia; il 9° campo è «1» a candela chiusa.
    candele = [
        Candela(_da_ms(c[0]), *(float(x) for x in c[1:6]))
        for c in reversed(r["data"])
        if c[8] == "1"
    ]
    return candele, fine


def coinbase(scarica: comune.Scarica, da: datetime, passo: timedelta) -> Pagina:
    """BTC-USD, finestre di 300 candele; la fine è inclusa."""
    n = 300
    ultima = da + (n - 1) * passo
    righe = scarica(
        "https://api.exchange.coinbase.com/products/BTC-USD/candles"
        f"?granularity={int(passo.total_seconds())}&start={_iso(da)}&end={_iso(ultima)}"
    )
    if not isinstance(righe, list):
        raise comune.RaccoltaError("coinbase: risposta inattesa")
    # [inizio, minimo, massimo, apertura, chiusura, volume], dalla più recente.
    candele = [
        Candela(
            datetime.fromtimestamp(r[0], UTC),
            float(r[3]),
            float(r[2]),
            float(r[1]),
            float(r[4]),
            float(r[5]),
        )
        for r in reversed(righe)
    ]
    return candele, da + n * passo


@dataclass(frozen=True)
class Fonte:
    nome: str
    coppia: str
    pesca: Pescatore
    pausa: float  # secondi fra due chiamate, per restare sotto i limiti dell'exchange
    inizio_giorno: datetime
    inizio_minuto: datetime


def _utc(*parti: int) -> datetime:
    return datetime(*parti, tzinfo=UTC)


# Inizi misurati il 24/10/2026: Binance 17/08/2017; OKX 11/01/2018; Coinbase luglio 2015.
FONTI: dict[str, Fonte] = {
    "binance": Fonte("binance", "btc_usdt", binance, 0.2, _utc(2017, 8, 17), _utc(2017, 8, 17)),
    "okx": Fonte("okx", "btc_usdt", okx, 0.15, _utc(2018, 1, 11), _utc(2018, 1, 11)),
    "coinbase": Fonte("coinbase", "btc_usd", coinbase, 0.25, _utc(2015, 7, 1), _utc(2015, 7, 1)),
}


def nome_serie(fonte: Fonte, passo: timedelta, campo: str) -> str:
    """`btc_usd_coinbase_chiusura` (giorno, come in P06) o `btc_usdt_binance_1m_chiusura`."""
    sfondo = "_1m" if passo == MINUTO else ""
    return f"{fonte.coppia}_{fonte.nome}{sfondo}_{campo}"


@dataclass
class Esito:
    scritte: int = 0
    pagine: int = 0
    completo: bool = False
    errore: str | None = None
    fino_a: datetime | None = None
    messaggi: list[str] = field(default_factory=list)


def _scrivi(
    archivio: Archivio,
    fonte: Fonte,
    passo: timedelta,
    candele: list[Candela],
    ora: datetime,
    ultimi: dict[str, datetime | None],
) -> int:
    versione = comune.versione_da(ora)
    scritte = 0
    for campo in CAMPI:
        serie = nome_serie(fonte, passo, campo)
        osservazioni = [
            Osservazione(serie, c.istante, ora, getattr(c, campo), fonte.nome, versione)
            for c in candele
        ]
        if passo == GIORNO:
            # Poche migliaia di righe: si confronta con ciò che c'è e si versiona una correzione.
            scritte += comune.registra_se_cambiato(archivio, osservazioni)
            continue
        # Al minuto un'eventuale correzione non c'è: si aggiunge solo ciò che è oltre l'ultimo
        # istante già salvato, campo per campo (una scrittura interrotta può averne lasciati
        # alcuni più avanti degli altri).
        limite = ultimi[campo]
        nuove = [o for o in osservazioni if limite is None or o.istante_valore > limite]
        scritte += archivio.scrivi(nuove)
        if nuove:
            ultimi[campo] = max(o.istante_valore for o in nuove)
    return scritte


def raccogli_candele(
    archivio: Archivio,
    fonte: Fonte,
    passo: timedelta,
    ora: datetime,
    scadenza: float,
    scarica: comune.Scarica = comune.scarica_json,
    dormi: Callable[[float], None] = time.sleep,
    orologio: Callable[[], float] = time.monotonic,
) -> Esito:
    """Scarica le candele chiuse dal punto in cui ci si era fermati, finché c'è tempo."""
    esito = Esito()
    inizio = fonte.inizio_giorno if passo == GIORNO else fonte.inizio_minuto
    ultimi = {c: archivio.ultimo_istante(nome_serie(fonte, passo, c)) for c in CAMPI}
    pieno = None not in ultimi.values()
    if passo == MINUTO and pieno and ora - min(ultimi.values()) < ATTESA_MINUTO:  # type: ignore[type-var]
        esito.completo = True  # già al passo: niente da leggere, niente file piccoli
        esito.fino_a = ultimi["chiusura"]
        return esito
    if passo == GIORNO:
        # Poche chiamate (anni di giorni in una dozzina di pagine): si rilegge sempre tutto. Così
        # la storia si completa anche se la serie esisteva già con gli ultimi giorni (P06) e una
        # correzione della fonte diventa una nuova versione.
        da = inizio
    else:
        # Basta un campo senza dati per ripartire dall'inizio: la scrittura salta ciò che c'è già.
        da = inizio if None in ultimi.values() else min(ultimi.values()) + passo  # type: ignore[type-var]
    accumulo: list[Candela] = []
    try:
        while da + passo <= ora and orologio() < scadenza:
            candele, da = fonte.pesca(scarica, da, passo)
            esito.pagine += 1
            accumulo += [c for c in candele if c.istante + passo <= ora]
            if len(accumulo) >= SOGLIA_SCRITTURA:
                esito.scritte += _scrivi(archivio, fonte, passo, accumulo, ora, ultimi)
                accumulo = []
            dormi(fonte.pausa)
    except comune.RaccoltaError as e:
        esito.errore = str(e)
    finally:
        if accumulo:
            esito.scritte += _scrivi(archivio, fonte, passo, accumulo, ora, ultimi)
    esito.completo = esito.errore is None and da + passo > ora
    esito.fino_a = archivio.ultimo_istante(nome_serie(fonte, passo, "chiusura"))
    return esito


def raccogli_riferimenti(
    archivio: Archivio, ora: datetime, scarica: comune.Scarica = comune.scarica_json
) -> int:
    """Prezzo giornaliero di riferimento di Coin Metrics (dal 2010) e di bitview.space (dal 2010).

    Servono a coprire gli anni senza exchange e come seconda fonte indipendente nei confronti.
    """
    osservazioni: list[Osservazione] = []
    versione = comune.versione_da(ora)
    url: str | None = (
        f"{COIN_METRICS}?assets=btc&metrics=PriceUSD&frequency=1d&start_time={PRIMO_COIN_METRICS}"
        "&paging_from=start&page_size=10000"
    )
    while url:
        r = scarica(url)
        if not isinstance(r, dict) or not isinstance(r.get("data"), list):
            raise comune.RaccoltaError("coinmetrics: risposta inattesa")
        for riga in r["data"]:
            giorno = comune.mezzanotte(riga["time"][:10])
            if giorno + GIORNO <= ora and riga.get("PriceUSD") is not None:
                osservazioni.append(
                    Osservazione(
                        "btc_usd_coinmetrics_chiusura",
                        giorno,
                        ora,
                        float(riga["PriceUSD"]),
                        "coinmetrics",
                        versione,
                    )
                )
        url = r.get("next_page_url")
    oggi = ora.date()
    r = scarica(
        f"{bitview.BASE}/price_close/day1?start={PRIMO_BITVIEW.isoformat()}&end={oggi.isoformat()}"
    )
    if (
        not isinstance(r, dict)
        or not isinstance(r.get("data"), list)
        or r.get("start") != bitview.indice_giorno(PRIMO_BITVIEW)
    ):
        raise comune.RaccoltaError("bitview prezzo: risposta inattesa o indice dei giorni cambiato")
    for posizione, valore in enumerate(r["data"]):
        giorno = PRIMO_BITVIEW + timedelta(days=posizione)
        if valore and giorno < oggi:
            osservazioni.append(
                Osservazione(
                    "btc_usd_bitview_chiusura",
                    comune.mezzanotte(giorno.isoformat()),
                    ora,
                    float(valore),
                    bitview.FONTE,
                    versione,
                )
            )
    return comune.registra_se_cambiato(archivio, osservazioni)


def lancia_giorno(archivio: Archivio, ora: datetime) -> int:
    errori: list[str] = []
    for fonte in FONTI.values():
        esito = raccogli_candele(archivio, fonte, GIORNO, ora, time.monotonic() + 600)
        print(f"{fonte.nome} giorno: {esito.scritte} nuove, fino al {esito.fino_a}", flush=True)
        if esito.errore or not esito.completo:
            errori.append(esito.errore or f"{fonte.nome}: incompleto")
    try:
        print(f"riferimenti: {raccogli_riferimenti(archivio, ora)} nuove", flush=True)
    except comune.RaccoltaError as e:
        errori.append(str(e))
    for e in errori:
        print(e, flush=True)
    return 1 if errori else 0


def lancia_minuto(archivio: Archivio, nome: str, ora: datetime, tempo: int) -> int:
    esito = raccogli_candele(archivio, FONTI[nome], MINUTO, ora, time.monotonic() + tempo)
    stato = "completo" if esito.completo else "da continuare al prossimo giro"
    print(
        f"{nome} minuto: {esito.scritte} nuove in {esito.pagine} pagine, "
        f"fino al {esito.fino_a} ({stato})",
        flush=True,
    )
    if esito.errore:
        print(esito.errore, flush=True)
        # Un errore dopo aver fatto strada non è un guasto: il prossimo giro riprende da qui.
        return 0 if esito.scritte > 0 else 1
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    archivio, ora = comune.cartella_archivio(), comune.adesso()
    if argv == ["giorno"]:
        return lancia_giorno(archivio, ora)
    if len(argv) in (2, 3) and argv[0] == "minuto" and argv[1] in FONTI:
        return lancia_minuto(
            archivio, argv[1], ora, int(argv[2]) if len(argv) == 3 else TEMPO_DEFAULT
        )
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
