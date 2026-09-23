from datetime import UTC, datetime
from decimal import Decimal

from yourpkg.examples.orders.domain import Order, OrderId
from yourpkg.examples.orders.transforms import latest_per_order


def order(order_id: str, amount: str, hour: int) -> Order:
    return Order(
        order_id=OrderId(order_id),
        customer="Ada",
        amount=Decimal(amount),
        currency="CAD",
        updated_at=datetime(2026, 9, 1, hour, tzinfo=UTC),
    )


def test_the_latest_update_of_each_order_wins() -> None:
    kept = latest_per_order(
        [
            order("A1", "10.00", 9),
            order("A1", "12.50", 11),
            order("B2", "5.00", 10),
            order("A1", "11.00", 10),
        ]
    )
    assert [(o.order_id, o.amount) for o in kept] == [
        ("B2", Decimal("5.00")),
        ("A1", Decimal("12.50")),
    ]


def test_the_output_order_does_not_depend_on_the_input_order() -> None:
    rows = [order("B2", "5.00", 10), order("A1", "10.00", 10), order("C3", "1.00", 8)]
    assert [o.order_id for o in latest_per_order(rows)] == ["C3", "A1", "B2"]
    assert [o.order_id for o in latest_per_order(reversed(rows))] == ["C3", "A1", "B2"]


def test_no_orders_give_no_orders() -> None:
    assert latest_per_order([]) == []
