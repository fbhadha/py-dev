"""The use case: one incremental run from a source to a sink."""

from __future__ import annotations

import logging

from yourpkg.examples.orders.domain import Order, Rejected, RunReport
from yourpkg.examples.orders.ports import CursorStore, OrderSink, OrderSource
from yourpkg.examples.orders.transforms import latest_per_order

logger = logging.getLogger(__name__)


def run(*, name: str, source: OrderSource, sink: OrderSink, cursors: CursorStore) -> RunReport:
    """Load what changed since the last run, and move the cursor only after the write.

    A crash before the write means the next run reads the same rows again, and the
    sink's upsert makes that harmless: rows arrive at least once, are stored once.
    """
    since = cursors.load(name)
    orders: list[Order] = []
    rejected: list[Rejected] = []
    for item in source.read(since=since):
        if isinstance(item, Rejected):
            rejected.append(item)
        else:
            orders.append(item)
    for bad in rejected:
        logger.warning("rejected %s line %d: %s", bad.source, bad.line, bad.reason)
    batch = latest_per_order(orders)
    written = sink.write(batch)
    cursor = max((order.updated_at for order in batch), default=since)
    if cursor is not None and cursor != since:
        cursors.save(name, cursor)
    report = RunReport(
        read=len(orders) + len(rejected), written=written, rejected=len(rejected), cursor=cursor
    )
    logger.info(
        "%s: read %d, written %d, rejected %d, cursor %s",
        name,
        report.read,
        report.written,
        report.rejected,
        cursor.isoformat() if cursor else "none",
    )
    return report
