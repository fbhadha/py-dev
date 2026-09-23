"""Orders: the one record every source produces and every sink consumes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import NewType

OrderId = NewType("OrderId", str)
CURRENCY_CODE_LENGTH = 3


class OrdersError(Exception):
    """Base for every error the orders example raises."""


class InvalidOrderError(OrdersError, ValueError):
    """A value that breaks one of Order's rules."""


class SourceError(OrdersError):
    """A source that cannot be read at all: a missing file, a missing column."""


@dataclass(frozen=True, slots=True)
class Order:
    """One order after parsing: money as Decimal, time as UTC.

    These rules hold for every Order whichever source it came from, so no transform
    and no sink checks them again.
    """

    order_id: OrderId
    customer: str
    amount: Decimal
    currency: str
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.order_id:
            raise InvalidOrderError("order_id is empty")
        if not self.amount.is_finite():
            raise InvalidOrderError(f"amount {self.amount} is not a finite number")
        if self.amount < 0:
            raise InvalidOrderError(f"amount {self.amount} is negative")
        code = self.currency
        if len(code) != CURRENCY_CODE_LENGTH or not (code.isalpha() and code.isupper()):
            raise InvalidOrderError(f"currency {code!r} is not a three-letter code")
        if self.updated_at.utcoffset() != timedelta(0):
            raise InvalidOrderError("updated_at is not in UTC")


@dataclass(frozen=True, slots=True)
class Rejected:
    """A row a source could not turn into an Order, and why. Counted, never dropped."""

    source: str
    line: int
    reason: str


@dataclass(frozen=True, slots=True)
class RunReport:
    """What one run did: the line a person reads to know whether it worked."""

    read: int
    written: int
    rejected: int
    cursor: datetime | None
