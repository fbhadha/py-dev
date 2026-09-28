"""Fixtures the change gate's test files share: a committed change."""

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def committed(repo: Path, git) -> Callable[[dict[str, str | None]], None]:
    """Commit these files on a new branch; a file whose content is None is deleted."""

    def call(files: dict[str, str | None]) -> None:
        git("switch", "-q", "-c", "ticket/19")
        for name, content in files.items():
            if content is None:
                (repo / name).unlink()
            else:
                (repo / name).write_text(content, encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "change")

    return call
