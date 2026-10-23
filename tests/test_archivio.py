from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from bailout_lab.archivio import Archivio, Osservazione

GIORNO = datetime(2026, 10, 20, tzinfo=UTC)


def osservazione(**campi) -> Osservazione:
    base = {
        "serie": "btc-prezzo-chiusura",
        "istante_valore": GIORNO,
        "disponibile_dal": GIORNO + timedelta(minutes=5),
        "valore": 68000.5,
        "fonte": "prova",
    }
    return Osservazione(**{**base, **campi})


def test_scrive_e_rilegge(tmp_path):
    archivio = Archivio(tmp_path / "dati")
    o = osservazione()
    assert archivio.scrivi([o]) == 1
    assert archivio.leggi("btc-prezzo-chiusura") == [o]


def test_il_file_resta_nella_cartella_della_serie(tmp_path):
    Archivio(tmp_path).scrivi([osservazione()])
    assert list((tmp_path / "serie=btc-prezzo-chiusura" / "mese=2026-10").glob("*.parquet"))


def test_com_era_noto_non_guarda_nel_futuro(tmp_path):
    archivio = Archivio(tmp_path)
    prima = osservazione(valore=100.0, versione="1")
    corretta = osservazione(valore=105.0, versione="2", disponibile_dal=GIORNO + timedelta(days=3))
    archivio.scrivi([prima, corretta])

    due_giorni_dopo = GIORNO + timedelta(days=2)
    assert [o.valore for o in archivio.leggi("btc-prezzo-chiusura", noto_al=due_giorni_dopo)] == [
        100.0
    ]
    quattro_giorni_dopo = GIORNO + timedelta(days=4)
    assert [
        o.valore for o in archivio.leggi("btc-prezzo-chiusura", noto_al=quattro_giorni_dopo)
    ] == [105.0]


def test_prima_che_fosse_noto_non_c_e_nulla(tmp_path):
    archivio = Archivio(tmp_path)
    archivio.scrivi([osservazione()])
    assert archivio.leggi("btc-prezzo-chiusura", noto_al=GIORNO) == []


def test_riscrivere_la_stessa_osservazione_non_crea_doppioni(tmp_path):
    archivio = Archivio(tmp_path)
    o = osservazione()
    assert archivio.scrivi([o, o]) == 1
    assert archivio.scrivi([o]) == 0
    assert len(archivio.leggi("btc-prezzo-chiusura")) == 1


def test_serie_ordinata_per_istante_su_piu_mesi(tmp_path):
    archivio = Archivio(tmp_path)
    istanti = [datetime(2026, 10, 2, tzinfo=UTC), datetime(2026, 9, 30, tzinfo=UTC), GIORNO]
    archivio.scrivi(
        [osservazione(istante_valore=i, disponibile_dal=i + timedelta(hours=1)) for i in istanti]
    )
    assert [o.istante_valore for o in archivio.leggi("btc-prezzo-chiusura")] == sorted(istanti)


def test_serie_diverse_restano_separate(tmp_path):
    archivio = Archivio(tmp_path)
    archivio.scrivi([osservazione(), osservazione(serie="btc-mvrv", valore=2.1)])
    assert [o.valore for o in archivio.leggi("btc-mvrv")] == [2.1]
    assert archivio.leggi("serie-che-non-esiste") == []


def test_fusi_orari_diversi_vengono_portati_a_utc(tmp_path):
    roma = ZoneInfo("Europe/Rome")
    o = osservazione(
        istante_valore=GIORNO.astimezone(roma), disponibile_dal=(GIORNO + timedelta(hours=1))
    )
    archivio = Archivio(tmp_path)
    archivio.scrivi([o])
    letta = archivio.leggi("btc-prezzo-chiusura")[0]
    assert letta.istante_valore == GIORNO
    assert letta.istante_valore.utcoffset() == timedelta(0)


@pytest.mark.parametrize(
    "campi",
    [
        {"serie": "Nome Con Spazi"},
        {"serie": "../fuori"},
        {"serie": ""},
        {"istante_valore": datetime(2026, 10, 20)},
        {"disponibile_dal": datetime(2026, 10, 20)},
        {"disponibile_dal": GIORNO - timedelta(seconds=1)},
        {"fonte": ""},
    ],
)
def test_osservazioni_non_valide_vengono_rifiutate(campi):
    with pytest.raises(ValueError):
        osservazione(**campi)


def test_nessun_file_provvisorio_resta_dopo_la_scrittura(tmp_path):
    Archivio(tmp_path).scrivi([osservazione()])
    assert not list(tmp_path.rglob("*.tmp"))
