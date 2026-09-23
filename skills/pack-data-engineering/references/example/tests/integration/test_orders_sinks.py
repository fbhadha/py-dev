"""The OrderSink contract: every sink passes it, the in-memory one included."""

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from yourpkg.examples.orders.adapters.memory import InMemoryOrderSink
from yourpkg.examples.orders.adapters.sqlite_sink import SqliteOrderSink
from yourpkg.examples.orders.domain import Order, OrderId
from yourpkg.examples.orders.ports import OrderSink


def order(order_id: str, amount: str, hour: int, minute: int = 0) -> Order:
    return Order(
        order_id=OrderId(order_id),
        customer="Ada",
        amount=Decimal(amount),
        currency="CAD",
        updated_at=datetime(2026, 9, 1, hour, minute, tzinfo=UTC),
    )


class OrderSinkContract:
    """Subclass with a `sink` fixture; a new sink is done when it passes all of these."""

    def test_new_orders_are_written_and_counted(self, sink: OrderSink) -> None:
        assert sink.write([order("A1", "10.00", 9), order("B2", "5.00", 9)]) == 2
        assert sink.count() == 2

    def test_writing_the_same_orders_again_changes_nothing(self, sink: OrderSink) -> None:
        rows = [order("A1", "10.00", 9), order("B2", "5.00", 9)]
        sink.write(rows)
        assert sink.write(rows) == 0
        assert sink.count() == 2

    def test_a_newer_update_replaces_the_stored_one(self, sink: OrderSink) -> None:
        sink.write([order("A1", "10.00", 9)])
        assert sink.write([order("A1", "12.50", 11)]) == 1
        assert sink.get(OrderId("A1")) == order("A1", "12.50", 11)

    def test_a_late_older_update_never_replaces_a_newer_one(self, sink: OrderSink) -> None:
        sink.write([order("A1", "12.50", 11)])
        assert sink.write([order("A1", "10.00", 9)]) == 0
        assert sink.get(OrderId("A1")) == order("A1", "12.50", 11)

    def test_money_and_time_come_back_exactly(self, sink: OrderSink) -> None:
        precise = order("A1", "10.10", 9, minute=7)
        sink.write([precise])
        assert sink.get(OrderId("A1")) == precise

    def test_an_unknown_order_is_none(self, sink: OrderSink) -> None:
        assert sink.get(OrderId("nope")) is None


class TestInMemoryOrderSink(OrderSinkContract):
    @pytest.fixture
    def sink(self) -> OrderSink:
        return InMemoryOrderSink()


class TestSqliteOrderSink(OrderSinkContract):
    @pytest.fixture
    def sink(self, tmp_path: Path) -> OrderSink:
        return SqliteOrderSink(path=tmp_path / "orders.db")
