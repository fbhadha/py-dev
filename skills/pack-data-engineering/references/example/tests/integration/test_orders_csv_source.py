from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from yourpkg.examples.orders.adapters.csv_source import CsvOrderSource
from yourpkg.examples.orders.domain import Order, OrderId, Rejected, SourceError

EXPORT = """id,customer,amount,currency,updated_at
A1,Ada,10.00,cad,2026-09-01T09:00:00+00:00
B2,Grace,5.00,CAD,2026-09-01T06:30:00-04:00
C3,Linus,ten,CAD,2026-09-01T11:00:00+00:00
D4,Barbara,7.25,CAD,2026-09-01T12:00:00
"""


@pytest.fixture
def export(tmp_path: Path) -> Path:
    path = tmp_path / "orders.csv"
    path.write_text(EXPORT, encoding="utf-8")
    return path


def test_each_row_becomes_an_order_or_a_rejected_row(export: Path) -> None:
    items = list(CsvOrderSource(path=export).read(since=None))
    assert items == [
        Order(OrderId("A1"), "Ada", Decimal("10.00"), "CAD", datetime(2026, 9, 1, 9, tzinfo=UTC)),
        Order(
            OrderId("B2"), "Grace", Decimal("5.00"), "CAD", datetime(2026, 9, 1, 10, 30, tzinfo=UTC)
        ),
        Rejected("orders.csv", 4, "amount 'ten' is not a number"),
        Rejected("orders.csv", 5, "updated_at '2026-09-01T12:00:00' has no UTC offset"),
    ]


def test_only_rows_newer_than_the_cursor_come_back_and_bad_rows_always_do(export: Path) -> None:
    items = list(CsvOrderSource(path=export).read(since=datetime(2026, 9, 1, 10, tzinfo=UTC)))
    newer = [item.order_id for item in items if isinstance(item, Order)]
    rejected_lines = [item.line for item in items if isinstance(item, Rejected)]
    assert (newer, rejected_lines) == (["B2"], [4, 5])


def test_a_missing_column_stops_the_run(tmp_path: Path) -> None:
    path = tmp_path / "orders.csv"
    path.write_text("id,customer,amount\nA1,Ada,10.00\n", encoding="utf-8")
    with pytest.raises(SourceError, match="no column currency, updated_at"):
        list(CsvOrderSource(path=path).read(since=None))


def test_a_missing_file_stops_the_run(tmp_path: Path) -> None:
    with pytest.raises(SourceError, match="does not exist"):
        list(CsvOrderSource(path=tmp_path / "nowhere.csv").read(since=None))


def test_a_row_with_fewer_fields_than_the_header_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "orders.csv"
    path.write_text("id,customer,amount,currency,updated_at\nA1,Ada,10.00\n", encoding="utf-8")
    items = list(CsvOrderSource(path=path).read(since=None))
    assert items == [Rejected("orders.csv", 2, "currency is empty")]
