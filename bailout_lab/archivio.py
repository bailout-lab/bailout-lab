"""Archivio «come era noto»: ogni valore si salva con l'istante in cui era davvero disponibile.

Il formato è append-only: un valore corretto dalla fonte non sostituisce il vecchio, ne
diventa una nuova versione con il proprio `disponibile_dal`. Così si può ricostruire cosa
sapevamo a una certa data (`leggi(noto_al=...)`) senza guardare nel futuro.

Su disco: file Parquet immutabili, uno per scrittura, raggruppati per serie e per mese del
valore. La lettura passa da DuckDB. Tutti gli istanti sono UTC.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import duckdb

_NOME_SERIE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,99}$")

_SCHEMA = (
    "serie VARCHAR, istante_valore TIMESTAMP, disponibile_dal TIMESTAMP, "
    "valore DOUBLE, fonte VARCHAR, versione VARCHAR"
)


@dataclass(frozen=True)
class Osservazione:
    """Un valore di una serie, con quando vale e quando lo abbiamo potuto conoscere."""

    serie: str
    istante_valore: datetime
    disponibile_dal: datetime
    valore: float
    fonte: str
    versione: str = "1"

    def __post_init__(self) -> None:
        if not _NOME_SERIE.fullmatch(self.serie):
            raise ValueError(f"nome di serie non valido: {self.serie!r}")
        for nome in ("istante_valore", "disponibile_dal"):
            _controlla_utc(nome, getattr(self, nome))
        if self.disponibile_dal < self.istante_valore:
            raise ValueError("un valore non può essere noto prima dell'istante a cui si riferisce")
        if not self.fonte:
            raise ValueError("la fonte è obbligatoria")


def _controlla_utc(nome: str, istante: datetime) -> None:
    if istante.tzinfo is None or istante.utcoffset() is None:
        raise ValueError(f"{nome} deve avere il fuso orario (UTC)")


def _naive_utc(istante: datetime) -> datetime:
    return istante.astimezone(UTC).replace(tzinfo=None)


def _aware_utc(istante: datetime) -> datetime:
    return istante.replace(tzinfo=UTC)


class Archivio:
    """Cartella di file Parquet con le osservazioni di tutte le serie."""

    def __init__(self, radice: str | Path) -> None:
        self.radice = Path(radice)

    def scrivi(self, osservazioni: Iterable[Osservazione]) -> int:
        """Aggiunge le osservazioni e restituisce quante ne ha scritte.

        Una osservazione identica a una già presente (stessa serie, istante, disponibilità e
        versione) viene saltata: rilanciare un raccoglitore non crea doppioni.
        """
        da_scrivere = list(osservazioni)
        if not da_scrivere:
            return 0
        scritte = 0
        per_gruppo: dict[tuple[str, str], list[Osservazione]] = {}
        for o in da_scrivere:
            gruppo = (o.serie, o.istante_valore.astimezone(UTC).strftime("%Y-%m"))
            per_gruppo.setdefault(gruppo, []).append(o)
        for (serie, mese), righe in per_gruppo.items():
            scritte += self._scrivi_gruppo(serie, mese, righe)
        return scritte

    def _scrivi_gruppo(self, serie: str, mese: str, righe: list[Osservazione]) -> int:
        cartella = self.radice / f"serie={serie}" / f"mese={mese}"
        con = duckdb.connect()
        try:
            con.execute(f"CREATE TABLE nuove ({_SCHEMA})")
            con.executemany(
                "INSERT INTO nuove VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        o.serie,
                        _naive_utc(o.istante_valore),
                        _naive_utc(o.disponibile_dal),
                        float(o.valore),
                        o.fonte,
                        o.versione,
                    )
                    for o in righe
                ],
            )
            # Duplicati dentro la stessa scrittura: ne resta uno solo per chiave.
            con.execute(
                "CREATE TABLE uniche AS SELECT DISTINCT ON "
                "(serie, istante_valore, disponibile_dal, versione) * FROM nuove"
            )
            esistenti = list(cartella.glob("*.parquet")) if cartella.is_dir() else []
            if esistenti:
                con.execute(
                    "DELETE FROM uniche WHERE EXISTS (SELECT 1 FROM read_parquet(?) e "
                    "WHERE e.serie = uniche.serie AND e.istante_valore = uniche.istante_valore "
                    "AND e.disponibile_dal = uniche.disponibile_dal "
                    "AND e.versione = uniche.versione)",
                    [[str(p) for p in esistenti]],
                )
            nuove = con.execute("SELECT count(*) FROM uniche").fetchone()[0]
            if nuove == 0:
                return 0
            cartella.mkdir(parents=True, exist_ok=True)
            nome = f"{uuid.uuid4().hex}.parquet"
            provvisorio = cartella / f".{nome}.tmp"
            con.execute("COPY uniche TO ? (FORMAT PARQUET)", [str(provvisorio)])
            provvisorio.rename(cartella / nome)  # il file compare intero o non compare
            return nuove
        finally:
            con.close()

    def percorsi(self, serie: str) -> list[str]:
        """I file Parquet di una serie, per interrogarli direttamente con DuckDB."""
        if not _NOME_SERIE.fullmatch(serie):
            raise ValueError(f"nome di serie non valido: {serie!r}")
        return sorted(str(p) for p in (self.radice / f"serie={serie}").glob("mese=*/*.parquet"))

    def ultimo_istante(self, serie: str) -> datetime | None:
        """Istante del valore più recente di una serie, leggendo solo il mese più recente.

        Serve a riprendere una raccolta lunga senza rileggere tutta la storia.
        """
        file_serie = self.percorsi(serie)
        if not file_serie:
            return None
        ultimo_mese = max(Path(p).parent.name for p in file_serie)
        recenti = [p for p in file_serie if Path(p).parent.name == ultimo_mese]
        con = duckdb.connect()
        try:
            massimo = con.execute("SELECT max(istante_valore) FROM read_parquet(?)", [recenti])
            valore = massimo.fetchone()[0]
        finally:
            con.close()
        return None if valore is None else _aware_utc(valore)

    def leggi(self, serie: str, noto_al: datetime | None = None) -> list[Osservazione]:
        """Restituisce la serie com'era nota a `noto_al` (default: oggi), ordinata per istante.

        Per ogni istante del valore vale la versione più recente tra quelle già disponibili.
        """
        if not _NOME_SERIE.fullmatch(serie):
            raise ValueError(f"nome di serie non valido: {serie!r}")
        file_serie = list((self.radice / f"serie={serie}").glob("mese=*/*.parquet"))
        if not file_serie:
            return []
        limite = datetime.now(UTC) if noto_al is None else noto_al
        _controlla_utc("noto_al", limite)
        con = duckdb.connect()
        try:
            righe = con.execute(
                "SELECT serie, istante_valore, disponibile_dal, valore, fonte, versione "
                "FROM read_parquet(?) WHERE disponibile_dal <= ? "
                "QUALIFY row_number() OVER (PARTITION BY istante_valore "
                "ORDER BY disponibile_dal DESC, versione DESC) = 1 "
                "ORDER BY istante_valore",
                [[str(p) for p in file_serie], _naive_utc(limite)],
            ).fetchall()
        finally:
            con.close()
        return [
            Osservazione(s, _aware_utc(iv), _aware_utc(dd), v, f, ver)
            for s, iv, dd, v, f, ver in righe
        ]
