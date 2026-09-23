"""Transforms: pure functions from Orders to Orders. No I/O, no clock, no randomness."""

from __future__ import annotations

from collections.abc import Iterable

from yourpkg.examples.orders.domain import Order, OrderId


def latest_per_order(orders: Iterable[Order]) -> list[Order]:
    """Keep one Order per id, its most recent update; on a tie, the first one seen.

    The result is sorted by update time, then id, so the same input always gives the
    same output, whatever order the source yielded it in.
    """
    latest: dict[OrderId, Order] = {}
    for order in orders:
        kept = latest.get(order.order_id)
        if kept is None or order.updated_at > kept.updated_at:
            latest[order.order_id] = order
    return sorted(latest.values(), key=lambda order: (order.updated_at, order.order_id))
