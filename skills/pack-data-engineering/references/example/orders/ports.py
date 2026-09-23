"""The seams the run needs. Each has an in-memory adapter and a real one, and one contract."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import datetime
from typing import Protocol

from yourpkg.examples.orders.domain import Order, OrderId, Rejected


class OrderSource(Protocol):
    def read(self, *, since: datetime | None) -> Iterator[Order | Rejected]:
        """Yield orders updated after `since` (all of them when None) and every bad row."""
        ...


class OrderSink(Protocol):
    def write(self, orders: Iterable[Order]) -> int:
        """Upsert on order_id, never replacing a newer update; return the rows changed."""
        ...

    def get(self, order_id: OrderId) -> Order | None: ...

    def count(self) -> int: ...


class CursorStore(Protocol):
    def load(self, name: str) -> datetime | None: ...

    def save(self, name: str, cursor: datetime) -> None: ...
