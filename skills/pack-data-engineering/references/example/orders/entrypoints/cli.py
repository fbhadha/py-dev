"""The command line: the one place the orders example is wired together."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from yourpkg.examples.orders.adapters.csv_source import CsvOrderSource
from yourpkg.examples.orders.adapters.json_cursors import JsonCursorStore
from yourpkg.examples.orders.adapters.sqlite_sink import SqliteOrderSink
from yourpkg.examples.orders.application import run
from yourpkg.examples.orders.domain import OrdersError

logger = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Load orders from a CSV export into SQLite, from where the last run stopped.

    Exit 0 when every row loaded, 1 when rows were rejected (a person must look at
    them), 2 when the run could not happen at all.
    """
    parser = argparse.ArgumentParser(description="Load orders from a CSV export into SQLite.")
    parser.add_argument("--csv", type=Path, required=True, help="the CSV export to read")
    parser.add_argument("--db", type=Path, required=True, help="the SQLite file to load into")
    parser.add_argument("--state", type=Path, required=True, help="the JSON file of cursors")
    parser.add_argument("--name", default="orders-csv", help="this load's cursor name")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        report = run(
            name=args.name,
            source=CsvOrderSource(path=args.csv),
            sink=SqliteOrderSink(path=args.db),
            cursors=JsonCursorStore(path=args.state),
        )
    except OrdersError:
        logger.exception("the run could not complete")
        return 2
    return 1 if report.rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
