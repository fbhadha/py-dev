"""Orders from a CSV export. Each row is parsed here, once, into an Order or a Rejected."""

from __future__ import annotations

import csv
from collections.abc import Iterator, Mapping
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from yourpkg.examples.orders.domain import (
    InvalidOrderError,
    Order,
    OrderId,
    Rejected,
    SourceError,
)

COLUMNS = ("id", "customer", "amount", "currency", "updated_at")
FIRST_DATA_LINE = 2  # line 1 is the header


class CsvOrderSource:
    """Rows of `id,customer,amount,currency,updated_at`; every time carries a UTC offset."""

    def __init__(self, *, path: Path) -> None:
        self._path = path

    def read(self, *, since: datetime | None) -> Iterator[Order | Rejected]:
        if not self._path.exists():
            raise SourceError(f"{self._path} does not exist")
        with self._path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = [column for column in COLUMNS if column not in (reader.fieldnames or [])]
            if missing:
                raise SourceError(f"{self._path.name} has no column {', '.join(missing)}")
            for line, row in enumerate(reader, start=FIRST_DATA_LINE):
                item = self._parse(row, line)
                if isinstance(item, Rejected) or since is None or item.updated_at > since:
                    yield item

    def _parse(self, row: Mapping[str, str | None], line: int) -> Order | Rejected:
        try:
            return Order(
                order_id=OrderId(_field(row, "id")),
                customer=_field(row, "customer"),
                amount=Decimal(_field(row, "amount")),
                currency=_field(row, "currency").upper(),
                updated_at=_utc(_field(row, "updated_at")),
            )
        except InvalidOperation:
            return Rejected(self._path.name, line, f"amount {row.get('amount')!r} is not a number")
        except ValueError as err:  # InvalidOrderError and datetime's parse errors
            return Rejected(self._path.name, line, str(err))


def _field(row: Mapping[str, str | None], column: str) -> str:
    value = (row.get(column) or "").strip()
    if not value:
        raise InvalidOrderError(f"{column} is empty")
    return value


def _utc(text: str) -> datetime:
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        raise InvalidOrderError(f"updated_at {text!r} has no UTC offset")
    return moment.astimezone(UTC)
