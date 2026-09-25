"""The whole path, through the command line, twice: the second run loads nothing new."""

import logging
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from yourpkg.examples.orders.entrypoints.cli import main

GOOD = """id,customer,amount,currency,updated_at
A1,Ada,10.00,CAD,2026-09-01T09:00:00+00:00
B2,Grace,5.00,CAD,2026-09-01T10:00:00+00:00
"""


def rows(db: Path) -> list[tuple[str, str]]:
    with closing(sqlite3.connect(db)) as conn:
        return conn.execute("SELECT order_id, amount FROM orders ORDER BY order_id").fetchall()


def args(tmp_path: Path) -> list[str]:
    return [
        "--csv",
        str(tmp_path / "orders.csv"),
        "--db",
        str(tmp_path / "orders.db"),
        "--state",
        str(tmp_path / "state.json"),
    ]


def test_a_clean_export_loads_once_and_a_rerun_changes_nothing(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    (tmp_path / "orders.csv").write_text(GOOD, encoding="utf-8")
    assert main(args(tmp_path)) == 0
    assert main(args(tmp_path)) == 0
    assert rows(tmp_path / "orders.db") == [("A1", "10.00"), ("B2", "5.00")]
    assert "read 0, written 0, rejected 0" in caplog.text


def test_a_rejected_row_makes_the_run_exit_1(tmp_path: Path) -> None:
    bad = GOOD + "C3,Linus,ten,CAD,2026-09-01T11:00:00+00:00\n"
    (tmp_path / "orders.csv").write_text(bad, encoding="utf-8")
    assert main(args(tmp_path)) == 1
    assert rows(tmp_path / "orders.db") == [("A1", "10.00"), ("B2", "5.00")]


def test_a_missing_export_exits_2(tmp_path: Path) -> None:
    assert main(args(tmp_path)) == 2


@pytest.mark.parametrize("missing", ["--csv", "--db", "--state"])
def test_each_path_argument_is_required(tmp_path: Path, missing: str) -> None:
    given = args(tmp_path)
    at = given.index(missing)
    with pytest.raises(SystemExit) as raised:
        main(given[:at] + given[at + 2 :])
    assert raised.value.code == 2
