"""In-memory adapters: the second adapter behind every port, for unit tests and dry runs.

They pass the same contract suites as the real adapters, which is what makes a unit
test that uses them worth trusting.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import datetime

from yourpkg.examples.orders.domain import Order, OrderId, Rejected


class InMemoryOrderSource:
    def __init__(self, items: Iterable[Order | Rejected]) -> None:
        self._items = list(items)

    def read(self, *, since: datetime | None) -> Iterator[Order | Rejected]:
        for item in self._items:
            if isinstance(item, Rejected) or since is None or item.updated_at > since:
                yield item


class InMemoryOrderSink:
    def __init__(self) -> None:
        self._orders: dict[OrderId, Order] = {}

    def write(self, orders: Iterable[Order]) -> int:
        changed = 0
        for order in orders:
            stored = self._orders.get(order.order_id)
            if stored is None or order.updated_at > stored.updated_at:
                self._orders[order.order_id] = order
                changed += 1
        return changed

    def get(self, order_id: OrderId) -> Order | None:
        return self._orders.get(order_id)

    def count(self) -> int:
        return len(self._orders)


class InMemoryCursorStore:
    def __init__(self) -> None:
        self._cursors: dict[str, datetime] = {}

    def load(self, name: str) -> datetime | None:
        return self._cursors.get(name)

    def save(self, name: str, cursor: datetime) -> None:
        self._cursors[name] = cursor
