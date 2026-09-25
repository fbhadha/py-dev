from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from yourpkg.examples.orders.adapters.memory import (
    InMemoryCursorStore,
    InMemoryOrderSink,
    InMemoryOrderSource,
)
from yourpkg.examples.orders.application import run
from yourpkg.examples.orders.domain import Order, OrderId, OrdersError, Rejected, RunReport


def order(order_id: str, amount: str, hour: int) -> Order:
    return Order(
        order_id=OrderId(order_id),
        customer="Ada",
        amount=Decimal(amount),
        currency="CAD",
        updated_at=datetime(2026, 9, 1, hour, tzinfo=UTC),
    )


TEN_UTC = datetime(2026, 9, 1, 10, tzinfo=UTC)


def test_a_first_run_loads_everything_and_sets_the_cursor() -> None:
    source = InMemoryOrderSource([order("A1", "10.00", 9), order("B2", "5.00", 10)])
    sink, cursors = InMemoryOrderSink(), InMemoryCursorStore()
    report = run(name="orders", source=source, sink=sink, cursors=cursors)
    assert report == RunReport(read=2, written=2, rejected=0, cursor=TEN_UTC)
    assert cursors.load("orders") == TEN_UTC


def test_a_second_run_reads_only_what_changed_since_the_cursor() -> None:
    sink, cursors = InMemoryOrderSink(), InMemoryCursorStore()
    run(
        name="orders",
        source=InMemoryOrderSource([order("A1", "10.00", 9)]),
        sink=sink,
        cursors=cursors,
    )
    later = InMemoryOrderSource([order("A1", "10.00", 9), order("A1", "12.50", 11)])
    report = run(name="orders", source=later, sink=sink, cursors=cursors)
    assert (report.read, report.written) == (1, 1)
    assert sink.get(OrderId("A1")) == order("A1", "12.50", 11)


def test_running_the_same_rows_again_changes_nothing() -> None:
    rows = [order("A1", "10.00", 9), order("B2", "5.00", 10)]
    sink = InMemoryOrderSink()
    run(name="orders", source=InMemoryOrderSource(rows), sink=sink, cursors=InMemoryCursorStore())
    again = run(
        name="orders", source=InMemoryOrderSource(rows), sink=sink, cursors=InMemoryCursorStore()
    )
    assert (again.written, sink.count()) == (0, 2)


def test_rejected_rows_are_counted_and_the_good_ones_still_load() -> None:
    bad = Rejected(source="orders.csv", line=3, reason="amount 'ten' is not a number")
    report = run(
        name="orders",
        source=InMemoryOrderSource([order("A1", "10.00", 9), bad]),
        sink=InMemoryOrderSink(),
        cursors=InMemoryCursorStore(),
    )
    assert (report.read, report.written, report.rejected) == (2, 1, 1)


class FailingSink(InMemoryOrderSink):
    def write(self, orders: Iterable[Order]) -> int:
        raise OrdersError("the disk is full")


def test_the_cursor_does_not_move_when_the_write_fails() -> None:
    cursors = InMemoryCursorStore()
    with pytest.raises(OrdersError, match="disk is full"):
        run(
            name="orders",
            source=InMemoryOrderSource([order("A1", "10.00", 9)]),
            sink=FailingSink(),
            cursors=cursors,
        )
    assert cursors.load("orders") is None


def test_a_run_with_nothing_new_writes_nothing_and_keeps_the_cursor() -> None:
    sink, cursors = InMemoryOrderSink(), InMemoryCursorStore()
    cursors.save("orders", TEN_UTC)
    report = run(
        name="orders",
        source=InMemoryOrderSource([order("A1", "10.00", 9)]),
        sink=sink,
        cursors=cursors,
    )
    assert report == RunReport(read=0, written=0, rejected=0, cursor=TEN_UTC)
    assert cursors.load("orders") == TEN_UTC
