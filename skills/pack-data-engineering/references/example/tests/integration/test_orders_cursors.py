"""The CursorStore contract, and the JSON store surviving a restart."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from yourpkg.examples.orders.adapters.json_cursors import JsonCursorStore
from yourpkg.examples.orders.adapters.memory import InMemoryCursorStore
from yourpkg.examples.orders.ports import CursorStore

NINE = datetime(2026, 9, 1, 9, 0, 0, 250, tzinfo=UTC)
TEN = datetime(2026, 9, 1, 10, tzinfo=UTC)


class CursorStoreContract:
    def test_an_unknown_name_has_no_cursor(self, store: CursorStore) -> None:
        assert store.load("orders") is None

    def test_a_saved_cursor_comes_back_exactly(self, store: CursorStore) -> None:
        store.save("orders", NINE)
        assert store.load("orders") == NINE

    def test_names_are_independent(self, store: CursorStore) -> None:
        store.save("orders", NINE)
        store.save("refunds", TEN)
        assert (store.load("orders"), store.load("refunds")) == (NINE, TEN)


class TestInMemoryCursorStore(CursorStoreContract):
    @pytest.fixture
    def store(self) -> CursorStore:
        return InMemoryCursorStore()


class TestJsonCursorStore(CursorStoreContract):
    @pytest.fixture
    def store(self, tmp_path: Path) -> CursorStore:
        return JsonCursorStore(path=tmp_path / "state.json")


def test_the_json_store_survives_a_restart(tmp_path: Path) -> None:
    JsonCursorStore(path=tmp_path / "state.json").save("orders", NINE)
    assert JsonCursorStore(path=tmp_path / "state.json").load("orders") == NINE
    assert [p.name for p in tmp_path.iterdir()] == ["state.json"]  # no temp file left behind
