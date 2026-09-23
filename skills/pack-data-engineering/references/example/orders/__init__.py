"""The orders example: a CSV export loaded incrementally into SQLite.

It is the worked example behind the data-engineering how-tos (add a source, a
transform, a sink, a pipeline). Each how-to mirrors a module here, and the tests
under tests/unit/examples and tests/integration/examples keep it honest.
"""

from yourpkg.examples.orders.application import run
from yourpkg.examples.orders.domain import (
    InvalidOrderError,
    Order,
    OrderId,
    OrdersError,
    Rejected,
    RunReport,
    SourceError,
)
from yourpkg.examples.orders.ports import CursorStore, OrderSink, OrderSource
from yourpkg.examples.orders.transforms import latest_per_order

__all__ = [
    "CursorStore",
    "InvalidOrderError",
    "Order",
    "OrderId",
    "OrderSink",
    "OrderSource",
    "OrdersError",
    "Rejected",
    "RunReport",
    "SourceError",
    "latest_per_order",
    "run",
]
