"""check_upstream_skills.py: a reference repo holds one file for each term the plugin links to."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REFERENCE = {"repo": "someone/dictionary", "dir": "dictionary", "terms": ["Spec", "Ticket"]}


@pytest.fixture
def script(root: Path) -> ModuleType:
    path = root / "scripts" / "check_upstream_skills.py"
    spec = importlib.util.spec_from_file_location("check_upstream_skills", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_term_with_its_file_is_no_problem(script: ModuleType, tmp_path: Path) -> None:
    (tmp_path / "dictionary").mkdir()
    (tmp_path / "dictionary" / "Spec.md").write_text("a spec", encoding="utf-8")
    (tmp_path / "dictionary" / "Ticket.md").write_text("a ticket", encoding="utf-8")

    assert script.check_reference(REFERENCE, tmp_path) == []


def test_a_term_without_its_file_is_reported(script: ModuleType, tmp_path: Path) -> None:
    (tmp_path / "dictionary").mkdir()
    (tmp_path / "dictionary" / "Spec.md").write_text("a spec", encoding="utf-8")

    assert script.check_reference(REFERENCE, tmp_path) == [
        "someone/dictionary: term 'Ticket' not found under dictionary"
    ]
