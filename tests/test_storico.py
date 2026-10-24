from datetime import UTC, datetime, timedelta

import pytest

from bailout_lab.archivio import Archivio
from bailout_lab.raccolta import comune, storico
from bailout_lab.raccolta.storico import GIORNO, MINUTO, Candela, Fonte

ORA = datetime(2026, 10, 23, 22, 34, tzinfo=UTC)


def t(*parti: int) -> datetime:
    return datetime(*parti, tzinfo=UTC)


def ms(istante: datetime) -> int:
    return int(istante.timestamp() * 1000)


def test_binance_legge_le_candele_e_riparte_dall_ultima():
    da = t(2017, 8, 17)

    def finta(url):
        assert "interval=1d" in url and f"startTime={ms(da)}" in url
        return [
            [ms(da), "4261.48", "4485.39", "4200.74", "4285.08", "795.15", 0],
            [ms(da + GIORNO), "4285.08", "4371.52", "3938.77", "4108.37", "1199.88", 0],
        ]

    candele, prossimo = storico.binance(finta, da, GIORNO)
    assert candele[0] == Candela(da, 4261.48, 4485.39, 4200.74, 4285.08, 795.15)
    assert prossimo == da + 2 * GIORNO
    assert storico.binance(lambda _u: [], da, MINUTO)[1] == da + 1000 * MINUTO  # finestra vuota


def test_okx_finestra_chiusa_giorno_utc_e_solo_candele_confermate():
    da = t(2020, 1, 1)

    def finta(url):
        assert "bar=1Dutc" in url and f"before={ms(da) - 1}" in url
        assert f"after={ms(da + 100 * GIORNO)}" in url
        # dalla più recente: la seconda non è ancora chiusa («0»)
        return {
            "code": "0",
            "data": [
                [str(ms(da + GIORNO)), "2", "3", "1", "2.5", "10", "0", "0", "0"],
                [str(ms(da)), "1", "2", "0.5", "1.5", "7", "0", "0", "1"],
            ],
        }

    candele, prossimo = storico.okx(finta, da, GIORNO)
    assert candele == [Candela(da, 1.0, 2.0, 0.5, 1.5, 7.0)]
    assert prossimo == da + 100 * GIORNO
    with pytest.raises(comune.RaccoltaError):
        storico.okx(lambda _u: {"code": "50011", "data": []}, da, MINUTO)


def test_coinbase_ordine_dei_campi_e_finestra_inclusiva():
    da = t(2018, 1, 1)

    def finta(url):
        assert "granularity=60" in url and "start=2018-01-01T00:00:00Z" in url
        assert "end=2018-01-01T04:59:00Z" in url  # 300 candele: l'ultima è inclusa
        # [inizio, minimo, massimo, apertura, chiusura, volume], dalla più recente
        return [
            [int((da + MINUTO).timestamp()), 5, 9, 6, 8, 2.0],
            [int(da.timestamp()), 1, 4, 2, 3, 1.0],
        ]

    candele, prossimo = storico.coinbase(finta, da, MINUTO)
    assert candele[0] == Candela(
        da, apertura=2.0, massimo=4.0, minimo=1.0, chiusura=3.0, volume=1.0
    )
    assert prossimo == da + 300 * MINUTO


def fonte_finta(candele_per_pagina: int = 3) -> tuple[Fonte, list[datetime]]:
    chiamate: list[datetime] = []

    def pesca(_scarica, da, passo):
        chiamate.append(da)
        candele = [
            Candela(da + i * passo, 1.0 + i, 2.0, 0.5, 1.5, 4.0) for i in range(candele_per_pagina)
        ]
        return candele, da + candele_per_pagina * passo

    return Fonte("prova", "btc_usd", pesca, 0, t(2026, 10, 1), t(2026, 10, 23, 10)), chiamate


def lancia(a, fonte, passo, ora=ORA, scadenza=1e9):
    return storico.raccogli_candele(
        a, fonte, passo, ora, scadenza, lambda _u: None, lambda _s: None
    )


def test_giorno_solo_giorni_chiusi_nomi_come_in_p06_e_nessun_doppione(tmp_path):
    fonte, _ = fonte_finta(candele_per_pagina=30)
    a = Archivio(tmp_path)
    esito = lancia(a, fonte, GIORNO)
    chiusura = a.leggi("btc_usd_prova_chiusura")
    assert chiusura[0].istante_valore == t(2026, 10, 1)
    assert chiusura[-1].istante_valore == t(2026, 10, 22)  # il 23 è in corso
    assert esito.completo and esito.scritte == 22 * 5
    assert lancia(a, fonte, GIORNO).scritte == 0  # rilanciato: tutto uguale, niente di nuovo


def test_minuto_riprende_dall_ultimo_e_scrive_solo_il_nuovo(tmp_path):
    fonte, chiamate = fonte_finta(candele_per_pagina=100)
    a = Archivio(tmp_path)
    prima = lancia(a, fonte, MINUTO, ora=t(2026, 10, 23, 10, 30))
    assert prima.scritte == 30 * 5 and prima.completo
    ultimo = a.ultimo_istante("btc_usd_prova_1m_chiusura")
    assert ultimo == t(2026, 10, 23, 10, 29)
    chiamate.clear()
    seconda = lancia(a, fonte, MINUTO, ora=t(2026, 10, 23, 11, 0))
    assert chiamate == [t(2026, 10, 23, 10, 30)]  # riparte subito dopo l'ultima, non da capo
    assert seconda.scritte == 30 * 5
    assert len(a.leggi("btc_usd_prova_1m_chiusura")) == 60


def test_minuto_campi_sfasati_dopo_una_scrittura_interrotta_non_duplicano(tmp_path):
    fonte, _ = fonte_finta(candele_per_pagina=100)
    a = Archivio(tmp_path)
    lancia(a, fonte, MINUTO, ora=t(2026, 10, 23, 10, 10))
    # simulo l'interruzione: il campo «volume» manca degli ultimi cinque minuti
    import shutil

    cartella = tmp_path / "serie=btc_usd_prova_1m_volume"
    shutil.rmtree(cartella)
    esito = lancia(a, fonte, MINUTO, ora=t(2026, 10, 23, 10, 10))
    assert len(a.leggi("btc_usd_prova_1m_volume")) == 10  # ricostruito
    assert len(a.leggi("btc_usd_prova_1m_chiusura")) == 10  # e gli altri non raddoppiati
    assert esito.scritte == 10


def test_si_ferma_alla_scadenza_e_salva_quanto_fatto(tmp_path):
    fonte, chiamate = fonte_finta(candele_per_pagina=100)
    a = Archivio(tmp_path)
    orologio = iter([0.0, 99.0])  # tempo che scade dopo la prima pagina
    esito = storico.raccogli_candele(
        a,
        fonte,
        MINUTO,
        t(2026, 10, 23, 12, 0),
        50.0,
        lambda _u: None,
        lambda _s: None,
        lambda: next(orologio),
    )
    assert len(chiamate) == 1 and not esito.completo and esito.scritte == 100 * 5
    assert len(a.leggi("btc_usd_prova_1m_chiusura")) == 100


def test_errore_dopo_una_pagina_tiene_il_lavoro_fatto(tmp_path):
    chiamate = []

    def pesca(_s, da, passo):
        chiamate.append(da)
        if len(chiamate) == 2:
            raise comune.RaccoltaError("x.test: HTTP 429")
        return [Candela(da, 1, 2, 0.5, 1.5, 4)], da + passo

    fonte = Fonte("prova", "btc_usd", pesca, 0, t(2026, 10, 1), t(2026, 10, 23, 10))
    a = Archivio(tmp_path)
    esito = lancia(a, fonte, MINUTO)
    assert esito.errore == "x.test: HTTP 429" and not esito.completo
    assert len(a.leggi("btc_usd_prova_1m_chiusura")) == 1


def test_riferimenti_coinmetrics_e_bitview(tmp_path):
    chiamate = []

    def finta(url):
        chiamate.append(url)
        if "coinmetrics" in url:
            return {
                "data": [
                    {
                        "asset": "btc",
                        "time": "2010-07-18T00:00:00.000000000Z",
                        "PriceUSD": "0.08584",
                    },
                    {"asset": "btc", "time": "2026-10-23T00:00:00.000000000Z", "PriceUSD": "99999"},
                ]
            }
        primo = storico.bitview.indice_giorno(storico.PRIMO_BITVIEW)
        return {"start": primo, "data": [0.06, None, 0.07]}

    a = Archivio(tmp_path)
    assert storico.raccogli_riferimenti(a, ORA, finta) == 1 + 2
    cm = a.leggi("btc_usd_coinmetrics_chiusura")
    assert [(o.istante_valore, o.valore) for o in cm] == [
        (t(2010, 7, 18), 0.08584)
    ]  # il 23/10 è aperto
    bv = a.leggi("btc_usd_bitview_chiusura")
    assert [o.valore for o in bv] == [0.06, 0.07]
    assert f"end={ORA.date().isoformat()}" in chiamate[-1]
    with pytest.raises(comune.RaccoltaError):
        storico.raccogli_riferimenti(
            a, ORA, lambda u: {"data": []} if "coin" in u else {"start": 1, "data": []}
        )


def test_uscita_di_lancia_minuto(tmp_path, monkeypatch):
    fonte, _ = fonte_finta()
    monkeypatch.setitem(storico.FONTI, "prova", fonte)
    a = Archivio(tmp_path)

    def senza_strada(*_a, **_k):
        return storico.Esito(errore="x: HTTP 500")

    monkeypatch.setattr(storico, "raccogli_candele", senza_strada)
    assert storico.lancia_minuto(a, "prova", ORA, 10) == 1  # guasto vero: nessun progresso
    monkeypatch.setattr(
        storico,
        "raccogli_candele",
        lambda *_a, **_k: storico.Esito(scritte=500, pagine=5, errore="x: HTTP 429"),
    )
    assert storico.lancia_minuto(a, "prova", ORA, 10) == 0  # strada fatta: riprende al giro dopo


def test_controllo_buchi_e_confronto(tmp_path):
    from bailout_lab.raccolta import controllo_storico as cs

    a = Archivio(tmp_path)
    ora = t(2026, 10, 5, 12)
    giorni = [t(2026, 10, g) for g in (1, 2, 4)]  # manca il 3
    for serie, fattore in (("btc_usd_coinbase_chiusura", 1.0), (cs.RIFERIMENTI[0], 1.002)):
        a.scrivi(
            Osservazione_(serie, g, 100.0 * fattore if g.day != 4 else 110.0 * fattore)
            for g in giorni
        )
    c = cs.copertura(a, "btc_usd_coinbase_chiusura")
    assert (c.giorni, [g.day for g in c.buchi]) == (3, [3])
    r = cs.confronta(a, "btc_usd_coinbase_chiusura", cs.RIFERIMENTI[0], "cb", "cm")
    assert r.giorni == 3 and r.entro == 3 and r.quota == 1.0
    righe, ok = cs.rapporto(a, ora)
    assert not ok  # buco del 3, altre serie assenti
    assert any("1 buchi" in r_ and "2026-10-03" in r_ for r_ in righe)


def Osservazione_(serie, giorno, valore):  # noqa: N802
    from bailout_lab.archivio import Osservazione

    return Osservazione(serie, giorno, giorno + timedelta(days=1), valore, "f", "1")


def test_controllo_minuti_conta_i_buchi(tmp_path):
    from bailout_lab.raccolta import controllo_storico as cs

    a = Archivio(tmp_path)
    base = t(2026, 10, 1, 10)
    minuti = [base + n * MINUTO for n in (0, 1, 2, 7, 8)]  # mancano 4 minuti
    a.scrivi(Osservazione_("btc_usd_coinbase_1m_chiusura", m, 1.0) for m in minuti)
    primo, ultimo, n, buchi = cs.minuti(a, "btc_usd_coinbase_1m_chiusura")
    assert (primo, ultimo, n) == (minuti[0], minuti[-1], 5)
    assert [(b.da, b.mancanti) for b in buchi] == [(minuti[2], 4)]
