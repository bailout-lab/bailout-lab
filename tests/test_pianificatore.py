import json
from datetime import UTC, datetime, timedelta

from bailout_lab import pianificatore as p

ORA = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


def lavoro(modulo="this", **campi) -> p.Lavoro:
    return p.Lavoro(nome="prova", modulo=modulo, ogni=timedelta(hours=1), **campi)


def test_dovuto_se_mai_partito_o_intervallo_passato():
    lav = lavoro()
    assert p.dovuto(lav, {}, ORA)
    assert not p.dovuto(lav, {"inizio": (ORA - timedelta(minutes=59)).isoformat()}, ORA)
    assert p.dovuto(lav, {"inizio": (ORA - timedelta(hours=1)).isoformat()}, ORA)


def test_esegui_registra_esito_ok(tmp_path):
    esito = p.esegui(lavoro("this"), tmp_path)
    assert esito["esito"] == "ok"
    assert esito["ultimo_ok"] == esito["fine"]
    salvato = json.loads((tmp_path / "stato" / "prova.json").read_text())
    assert salvato == esito


def test_esegui_fallito_conserva_ultimo_ok(tmp_path):
    primo = p.esegui(lavoro("this"), tmp_path)
    secondo = p.esegui(lavoro("modulo_che_non_esiste"), tmp_path)
    assert secondo["esito"] == "fallito"
    assert secondo["ultimo_ok"] == primo["fine"]


def test_esegui_ferma_un_lavoro_bloccato(tmp_path):
    (tmp_path / "dormi.py").write_text("import time\ntime.sleep(30)\n")
    lav = lavoro("dormi", tempo_massimo=1)
    esito = p.esegui(lav, tmp_path / "dati", {"PYTHONPATH": str(tmp_path)})
    assert esito["esito"] == "tempo scaduto"


def test_fotografia_segnala_archivio_oltre_soglia(tmp_path):
    (tmp_path / "archivio").mkdir()
    (tmp_path / "archivio" / "a.bin").write_bytes(b"x" * 2048)
    byte = p.dimensione(tmp_path / "archivio")
    assert byte == 2048
    assert p.fotografia(tmp_path, (), byte, soglia_gb=1)["avvisi"] == []
    avvisi = p.fotografia(tmp_path, (), byte, soglia_gb=1 / p.GB)["avvisi"]
    assert len(avvisi) == 1 and avvisi[0].startswith("archivio oltre")


def test_fotografia_misura_il_disco(tmp_path):
    foto = p.fotografia(tmp_path, (), 0, 20)
    assert 0 < foto["disco_libero_byte"] <= foto["disco_totale_byte"]


def test_salute_sana_scaduta_o_con_problemi(tmp_path):
    assert p.controlla_salute(tmp_path, ORA) == (False, "salute.json assente")
    p.scrivi_json(tmp_path / "salute.json", {"aggiornato": ORA.isoformat(), "problemi": []})
    assert p.controlla_salute(tmp_path, ORA + timedelta(minutes=1)) == (True, "ok")
    sano, motivo = p.controlla_salute(tmp_path, ORA + timedelta(minutes=4))
    assert not sano and motivo.startswith("ciclo fermo")
    p.scrivi_json(
        tmp_path / "salute.json", {"aggiornato": ORA.isoformat(), "problemi": ["prova: fallito"]}
    )
    assert p.controlla_salute(tmp_path, ORA) == (False, "prova: fallito")


def test_un_lavoro_fallito_rende_la_salute_rossa(tmp_path):
    lav = lavoro("modulo_che_non_esiste")
    p.esegui(lav, tmp_path)
    assert p.fotografia(tmp_path, (lav,), 0, 20)["problemi"] == ["prova: fallito"]


def test_avvisi_non_si_ripetono_entro_un_giorno(tmp_path):
    inviati = []
    avvisi = p.Avvisi(tmp_path, inviati.append)
    assert avvisi.manda("archivio", "archivio pieno", ORA)
    assert not avvisi.manda("archivio", "archivio pieno", ORA + timedelta(hours=23))
    assert avvisi.manda("archivio", "archivio pieno", ORA + timedelta(hours=24))
    assert avvisi.manda("altro", "altro problema", ORA)
    assert len(inviati) == 3


def test_comando_salute(tmp_path, monkeypatch):
    monkeypatch.setenv("BAILOUT_LAB_DATI", str(tmp_path))
    assert p.main(["salute"]) == 1
    p.scrivi_json(tmp_path / "salute.json", {"aggiornato": p.adesso().isoformat()})
    assert p.main(["salute"]) == 0


def test_i_lavori_registrati_sono_moduli_con_main():
    import importlib

    nomi = [lav.nome for lav in p.LAVORI]
    assert len(nomi) == len(set(nomi))
    for lav in p.LAVORI:
        assert callable(importlib.import_module(lav.modulo).main)
