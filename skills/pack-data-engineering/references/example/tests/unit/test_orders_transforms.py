from datetime import UTC, datetime
from decimal import Decimal

from hypothesis import example, given
from hypothesis import strategies as st

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


def test_on_a_tie_the_first_one_seen_wins() -> None:
    first, second = order("A1", "10.00", 9), order("A1", "12.50", 9)
    assert latest_per_order([first, second]) == [first]


# Few ids and few hours, so generated inputs repeat ids and tie on the hour.
orders = st.builds(
    order,
    st.sampled_from(["A1", "B2", "C3"]),
    st.sampled_from(["0.00", "5.00", "10.00", "12.50"]),
    st.integers(min_value=0, max_value=23),
)


@given(st.lists(orders, max_size=8))
@example([])
@example([order("A1", "10.00", 9), order("A1", "12.50", 9)])
def test_one_order_per_id_with_its_latest_time_in_the_stated_order(rows: list[Order]) -> None:
    kept = latest_per_order(rows)
    assert len({o.order_id for o in kept}) == len(kept)
    assert all(o in rows for o in kept)
    assert kept == sorted(kept, key=lambda o: (o.updated_at, o.order_id))
    for o in kept:
        assert o.updated_at == max(r.updated_at for r in rows if r.order_id == o.order_id)


@given(st.lists(orders, max_size=8))
def test_applying_it_twice_changes_nothing(rows: list[Order]) -> None:
    once = latest_per_order(rows)
    assert latest_per_order(once) == once
