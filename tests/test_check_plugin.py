"""check_plugin.py, run on a copy of this repo: what it prints today, recorded before it is split.

The seam is the command line. Each row breaks one fact in the copy and expects the message
the script prints for it; the expected text is the script's own, as it is on `main`.
"""

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

PY_REVIEW = "skills/py-review/SKILL.md"


@pytest.fixture
def plugin_copy(root: Path, tmp_path: Path) -> Path:
    """This repo without its git history, its environment and its caches."""
    shutil.copytree(
        root,
        tmp_path / "plugin",
        ignore=shutil.ignore_patterns(".git", ".venv", ".repowise", "__pycache__", ".*_cache"),
    )
    return tmp_path / "plugin"


def run_check(plugin: Path) -> tuple[str, int]:
    result = subprocess.run(
        [sys.executable, str(plugin / "scripts" / "check_plugin.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout, result.returncode


def change_json(rel: str, change: Callable[[dict[str, Any]], object]) -> Callable[[Path], None]:
    def edit(plugin: Path) -> None:
        data = json.loads((plugin / rel).read_text(encoding="utf-8"))
        change(data)
        (plugin / rel).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    return edit


def write(rel: str, text: str) -> Callable[[Path], None]:
    def edit(plugin: Path) -> None:
        (plugin / rel).write_text(text, encoding="utf-8")

    return edit


def append(rel: str, line: str) -> Callable[[Path], None]:
    def edit(plugin: Path) -> None:
        path = plugin / rel
        path.write_text(path.read_text(encoding="utf-8") + line + "\n", encoding="utf-8")

    return edit


def replace(rel: str, old: str, new: str) -> Callable[[Path], None]:
    def edit(plugin: Path) -> None:
        path = plugin / rel
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    return edit


BROKEN_FACTS = [
    pytest.param(
        change_json("plugin.json", lambda data: data.update(version="0.0.0")),
        "manifest versions differ",
        id="a-manifest-version-differs",
    ),
    pytest.param(
        change_json(".claude-plugin/plugin.json", lambda data: data["skills"].pop()),
        "do not match the folders under skills/",
        id="a-skill-folder-is-not-listed",
    ),
    pytest.param(
        change_json(".github/plugin/marketplace.json", lambda data: data.update(x=1)),
        "  - .github/plugin/marketplace.json must be identical to "
        ".claude-plugin/marketplace.json\n",
        id="the-two-marketplaces-differ",
    ),
    pytest.param(
        write("hooks/hooks.json", "{"), "hooks/hooks.json:", id="a-json-file-does-not-parse"
    ),
    pytest.param(
        append(PY_REVIEW, "Skill `no-such-skill`"),
        f"  - {PY_REVIEW}: calls skill `no-such-skill`, not in skills/ or upstream.json\n",
        id="a-skill-that-does-not-exist",
    ),
    pytest.param(
        append(PY_REVIEW, "Skill `wayfinder`"),
        f"  - {PY_REVIEW}: calls `wayfinder` as a Skill, which no harness allows: only a person "
        "can start it, so give the user the line (User types `wayfinder`)\n",
        id="a-user-only-skill-called-as-a-skill",
    ),
    pytest.param(
        append(PY_REVIEW, "User types `py-build`"),
        f"  - {PY_REVIEW}: gives the user `py-build` to type, but the agent can start it itself: "
        "Skill `py-build`\n",
        id="a-model-skill-given-to-the-user",
    ),
    pytest.param(
        append(PY_REVIEW, "`references/no-such-file.md`"),
        f"  - {PY_REVIEW}: names `references/no-such-file.md`, which does not exist\n",
        id="a-file-that-does-not-exist",
    ),
    pytest.param(
        append("skills/py-shape/SKILL.md", "see section 99"),
        "99; only",
        id="a-section-number-past-the-last",
    ),
    pytest.param(
        replace("skills/pack-adk/SKILL.md", "## Shapes", "## Shape list"),
        "pack is missing the template section `## Shapes`",
        id="a-pack-without-a-template-section",
    ),
]


def test_a_clean_copy_passes(plugin_copy: Path) -> None:
    output, returncode = run_check(plugin_copy)

    assert returncode == 0
    assert "plugin ok:" in output


@pytest.mark.parametrize(("edit", "expected"), BROKEN_FACTS)
def test_a_broken_fact_is_reported(
    plugin_copy: Path, edit: Callable[[Path], None], expected: str
) -> None:
    edit(plugin_copy)

    output, returncode = run_check(plugin_copy)

    assert returncode == 1
    assert expected in output
