from datetime import UTC, datetime, timedelta

import pytest

from bailout_lab.archivio import Archivio, Osservazione
from bailout_lab.raccolta import bitview, comune, controllo, etf, fred, mempool, prezzo

ORA = datetime(2026, 10, 23, 22, 34, tzinfo=UTC)


def giorno(g: int) -> datetime:
    return datetime(2026, 10, g, tzinfo=UTC)


def test_registra_se_cambiato_non_ripete_e_versiona(tmp_path):
    a = Archivio(tmp_path)

    def o(valore, ora):
        return Osservazione("s", giorno(20), ora, valore, "f", comune.versione_da(ora))

    assert comune.registra_se_cambiato(a, [o(1.0, giorno(21))]) == 1
    assert comune.registra_se_cambiato(a, [o(1.0, giorno(22))]) == 0  # identico: niente
    assert comune.registra_se_cambiato(a, [o(2.0, giorno(23))]) == 1  # ricalcolato: versione nuova
    assert a.leggi("s", noto_al=giorno(22))[0].valore == 1.0
    assert a.leggi("s")[0].valore == 2.0


def test_errore_http_non_mostra_l_indirizzo(monkeypatch):
    import urllib.error

    def rifiuta(*_a, **_k):
        raise urllib.error.HTTPError("https://x.test/?api_key=SEGRETO", 400, "no", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", rifiuta)
    with pytest.raises(comune.RaccoltaError) as e:
        comune.scarica_json("https://x.test/?api_key=SEGRETO")
    assert "SEGRETO" not in str(e.value) and "HTTP 400" in str(e.value)


def test_prezzo_scrive_solo_candele_chiuse(tmp_path):
    t = lambda g: int(giorno(g).timestamp())  # noqa: E731
    # [inizio, minimo, massimo, apertura, chiusura, volume]; la candela del 23 è ancora aperta
    candele = [[t(23), 1, 2, 3, 4, 5], [t(22), 10, 20, 30, 40, 50]]
    a = Archivio(tmp_path)
    assert prezzo.raccogli(a, ORA, lambda _u: candele) == 5
    chiusura = a.leggi("btc_usd_coinbase_chiusura")
    assert [(o.istante_valore, o.valore) for o in chiusura] == [(giorno(22), 40.0)]
    assert chiusura[0].disponibile_dal == ORA
    assert prezzo.raccogli(a, ORA + timedelta(minutes=20), lambda _u: candele) == 0


def test_bitview_indice_dei_giorni_e_giorni_chiusi(tmp_path):
    assert bitview.indice_giorno(giorno(20).date()) == 6501  # verificato sulla fonte
    primo = bitview.indice_giorno(ORA.date() - timedelta(days=bitview.GIORNI))

    def finta(url):
        assert f"end={ORA.date().isoformat()}" in url
        return {"start": primo, "data": [1.0, 2.0, None, 4.0, 5.0, 6.0, 7.0]}

    a = Archivio(tmp_path)
    assert bitview.raccogli(a, ORA, finta) == 6 * len(bitview.SERIE)  # il None è saltato
    mvrv = a.leggi("bitview_mvrv")
    assert mvrv[-1].istante_valore == giorno(22) and mvrv[-1].valore == 7.0


def test_bitview_si_ferma_se_cambia_la_numerazione(tmp_path):
    with pytest.raises(comune.RaccoltaError, match="indice"):
        bitview.raccogli(Archivio(tmp_path), ORA, lambda _u: {"start": 1, "data": [1.0]})


def test_mempool_fotografia(tmp_path):
    risposta = {"fastestFee": 5, "halfHourFee": 4, "hourFee": 3, "economyFee": 2, "minimumFee": 1}
    a = Archivio(tmp_path)
    assert mempool.raccogli(a, ORA, lambda _u: risposta) == 5
    o = a.leggi("mempool_fee_veloce")[0]
    assert (o.valore, o.istante_valore, o.disponibile_dal) == (5.0, ORA, ORA)
    with pytest.raises(comune.RaccoltaError):
        mempool.raccogli(a, ORA, lambda _u: {"fastestFee": 1})


def test_etf_serve_la_chiave_e_non_ripete(tmp_path, monkeypatch):
    riga = {
        "date": "2026-10-22",
        "totalNetInflow": -5.0,
        "totalValueTraded": 6.0,
        "totalNetAssets": 7.0,
        "cumNetInflow": 8.0,
    }
    visto = {}

    def finta(_u, corpo, intestazioni):
        visto.update(corpo=corpo, chiave=intestazioni["x-soso-api-key"])
        return {"code": 0, "data": [riga]}

    a = Archivio(tmp_path)
    monkeypatch.delenv("SOSOVALUE_API_KEY", raising=False)
    with pytest.raises(comune.RaccoltaError, match="manca"):
        etf.raccogli(a, ORA, finta)
    monkeypatch.setenv("SOSOVALUE_API_KEY", "k")
    assert etf.raccogli(a, ORA, finta) == 4
    assert visto == {"corpo": {"type": "us-btc-spot"}, "chiave": "k"}
    assert etf.raccogli(a, ORA + timedelta(hours=3), finta) == 0
    assert a.leggi("etf_btc_spot_flusso_netto_usd")[0].valore == -5.0


def test_fred_usa_la_data_di_revisione_e_salta_i_mancanti(tmp_path, monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "k")
    osservazioni = [
        {"date": "2026-10-20", "value": "4.9", "realtime_start": "2026-10-21"},
        {"date": "2026-10-21", "value": ".", "realtime_start": "2026-10-22"},
        # revisione: stesso giorno, valore nuovo da una data successiva
        {"date": "2026-10-20", "value": "5.0", "realtime_start": "2026-10-23"},
    ]
    urls = []

    def finta(url):
        urls.append(url)
        return {"observations": osservazioni}

    a = Archivio(tmp_path)
    # SP500 non ha versioni: le due righe dello stesso giorno nello stesso giro ne fanno una sola
    assert fred.raccogli(a, ORA, finta) == 2 * (len(fred.SERIE) - 1) + 1
    assert fred.raccogli(a, ORA, finta) == 0
    dgs10 = "fred_dgs10"
    assert a.leggi(dgs10, noto_al=giorno(22))[0].valore == 4.9
    assert a.leggi(dgs10)[0].valore == 5.0
    assert any("series_id=SP500" in u and "realtime" not in u for u in urls)
    assert all("realtime_end=9999-12-31" in u for u in urls if "series_id=DGS10" in u)


def test_fred_errore_dice_quale_serie_senza_chiave(tmp_path, monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "SEGRETO")

    def rotta(url):
        raise comune.RaccoltaError("api.stlouisfed.org: HTTP 500")

    with pytest.raises(comune.RaccoltaError) as e:
        fred.raccogli(Archivio(tmp_path), ORA, rotta)
    assert "DGS10" in str(e.value) and "SEGRETO" not in str(e.value)


def test_controllo_trova_buchi_e_dati_vecchi(tmp_path):
    a = Archivio(tmp_path)
    assert "bitview_mvrv: nessun dato" in controllo.controlla(a, ORA)
    for g in (20, 21, 22):  # manca solo il 20: con 3 giorni di finestra (20, 21, 22) è presente
        a.scrivi([Osservazione("bitview_mvrv", giorno(g), ORA, 1.0, "f", "1")])
    assert [p for p in controllo.controlla(a, ORA) if p.startswith("bitview_mvrv")] == []
    assert any("manca" in p for p in controllo.controlla(a, ORA + timedelta(days=1)))
    assert controllo.main(["3"]) in (0, 1)  # senza dati veri: solo che parte
