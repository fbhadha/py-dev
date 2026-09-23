from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from yourpkg.examples.orders.domain import InvalidOrderError, Order, OrderId

NINE_UTC = datetime(2026, 9, 1, 9, tzinfo=UTC)


def make(*, amount: str = "10.00", currency: str = "CAD", updated_at: datetime = NINE_UTC) -> Order:
    return Order(
        order_id=OrderId("A1"),
        customer="Ada",
        amount=Decimal(amount),
        currency=currency,
        updated_at=updated_at,
    )


def test_a_valid_order_keeps_its_values() -> None:
    order = make()
    assert (order.order_id, order.amount, order.currency) == ("A1", Decimal("10.00"), "CAD")


@pytest.mark.parametrize(
    ("amount", "message"),
    [("-1.00", "negative"), ("NaN", "not a finite number"), ("Infinity", "not a finite number")],
)
def test_an_amount_must_be_finite_and_not_negative(amount: str, message: str) -> None:
    with pytest.raises(InvalidOrderError, match=message):
        make(amount=amount)


@pytest.mark.parametrize("currency", ["cad", "CA", "C4D", "CADX"])
def test_a_currency_must_be_a_three_letter_code(currency: str) -> None:
    with pytest.raises(InvalidOrderError, match="three-letter code"):
        make(currency=currency)


def test_a_time_without_an_offset_is_refused() -> None:
    with pytest.raises(InvalidOrderError, match="not in UTC"):
        make(updated_at=datetime(2026, 9, 1, 9))  # naive on purpose


def test_a_time_in_another_offset_is_refused_until_converted() -> None:
    toronto = timezone(timedelta(hours=-4))
    with pytest.raises(InvalidOrderError, match="not in UTC"):
        make(updated_at=datetime(2026, 9, 1, 5, tzinfo=toronto))
