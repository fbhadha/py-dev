"""Cursors in one JSON file, replaced atomically, so a crash never leaves half a file."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


class JsonCursorStore:
    def __init__(self, *, path: Path) -> None:
        self._path = path

    def load(self, name: str) -> datetime | None:
        stamp = self._read().get(name)
        return datetime.fromisoformat(stamp) if stamp else None

    def save(self, name: str, cursor: datetime) -> None:
        cursors = {**self._read(), name: cursor.isoformat(timespec="microseconds")}
        handle, temp = tempfile.mkstemp(dir=self._path.parent, prefix=f".{self._path.name}.")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as out:
                json.dump(cursors, out, indent=2, sort_keys=True)
            Path(temp).replace(self._path)
        except BaseException:
            Path(temp).unlink(missing_ok=True)
            raise

    def _read(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return {str(key): str(value) for key, value in data.items()}
