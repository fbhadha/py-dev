"""Orders in SQLite, upserted on order_id, so running the same load twice changes nothing."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Iterator
from contextlib import closing, contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from yourpkg.examples.orders.domain import Order, OrderId

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id   TEXT PRIMARY KEY,
    customer   TEXT NOT NULL,
    amount     TEXT NOT NULL,  -- Decimal as text, never a float
    currency   TEXT NOT NULL,
    updated_at TEXT NOT NULL   -- UTC with microseconds, so text order is time order
)
"""
UPSERT = """
INSERT INTO orders (order_id, customer, amount, currency, updated_at)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT (order_id) DO UPDATE SET
    customer = excluded.customer,
    amount = excluded.amount,
    currency = excluded.currency,
    updated_at = excluded.updated_at
WHERE excluded.updated_at > orders.updated_at
"""
SELECT_ONE = """
SELECT order_id, customer, amount, currency, updated_at FROM orders WHERE order_id = ?
"""


class SqliteOrderSink:
    """One table. An older update never replaces a newer one, so late rows are safe."""

    def __init__(self, *, path: Path) -> None:
        self._path = path

    def write(self, orders: Iterable[Order]) -> int:
        rows = [
            (order.order_id, order.customer, str(order.amount), order.currency, _stamp(order))
            for order in orders
        ]
        with self._transaction() as conn:
            return conn.executemany(UPSERT, rows).rowcount

    def get(self, order_id: OrderId) -> Order | None:
        with self._transaction() as conn:
            row = conn.execute(SELECT_ONE, (order_id,)).fetchone()
        if row is None:
            return None
        key, customer, amount, currency, updated_at = row
        return Order(
            order_id=OrderId(key),
            customer=customer,
            amount=Decimal(amount),
            currency=currency,
            updated_at=datetime.fromisoformat(updated_at),
        )

    def count(self) -> int:
        with self._transaction() as conn:
            (total,) = conn.execute("SELECT COUNT(*) FROM orders").fetchone()
        return int(total)

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        with closing(sqlite3.connect(self._path)) as conn, conn:
            conn.execute(SCHEMA)
            yield conn


def _stamp(order: Order) -> str:
    return order.updated_at.isoformat(timespec="microseconds")
