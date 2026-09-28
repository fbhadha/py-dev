"""check_plugin.py on a copy of this repo: what it prints, recorded before it was split.

Two seams. A clean copy is checked through the command line of the copy's own script. Each
broken fact is checked through `main()` of this repo's script with its ROOT set to the copy:
coverage measures this repo's `scripts/`, never a copy's, and CI counts the lines a change adds.
Every expected text is the script's own, as it is on `main`.
"""

import importlib.util
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

PY_REVIEW = "skills/py-review/SKILL.md"
CLAUDE_MANIFEST = ".claude-plugin/plugin.json"


@pytest.fixture
def plugin_copy(root: Path, tmp_path: Path) -> Path:
    """This repo without its git history, its environment and its caches."""
    shutil.copytree(
        root,
        tmp_path / "plugin",
        ignore=shutil.ignore_patterns(".git", ".venv", ".repowise", "__pycache__", ".*_cache"),
    )
    return tmp_path / "plugin"


@pytest.fixture
def check_copy(
    root: Path,
    plugin_copy: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> Callable[[], tuple[str, int]]:
    """`check_copy()` runs this repo's check on the copy: what it printed, and its exit code."""
    spec = importlib.util.spec_from_file_location("check_plugin", root / "scripts/check_plugin.py")
    assert spec is not None
    assert spec.loader is not None
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    monkeypatch.setattr(script, "ROOT", plugin_copy)
    monkeypatch.setattr(script, "PERSONA", plugin_copy / "agents" / "python-dev.md")

    def call() -> tuple[str, int]:
        returncode = script.main()
        return capsys.readouterr().out, returncode

    return call


def rewrite(rel: str, change: Callable[[str], str]) -> Callable[[Path], None]:
    def edit(plugin: Path) -> None:
        path = plugin / rel
        path.write_text(change(path.read_text(encoding="utf-8")), encoding="utf-8")

    return edit


def as_json(change: Callable[[dict[str, Any]], object]) -> Callable[[str], str]:
    def apply(text: str) -> str:
        data = json.loads(text)
        change(data)
        return json.dumps(data, indent=2) + "\n"

    return apply


BROKEN_FACTS = {
    "a-manifest-version-differs": (
        rewrite("plugin.json", as_json(lambda data: data.update(version="0.0.0"))),
        "manifest versions differ",
    ),
    "a-manifest-name-differs": (
        rewrite("plugin.json", as_json(lambda data: data.update(name="other"))),
        "  - plugin.json and .claude-plugin/plugin.json name differ\n",
    ),
    "the-persona-names-another-version": (
        rewrite(CLAUDE_MANIFEST, as_json(lambda data: data.update(version="0.0.0"))),
        "  - agents/python-dev.md must name `python-dev 0.0.0` (its status line); "
        "bump it with the manifests\n",
    ),
    "a-skill-folder-is-not-listed": (
        rewrite(CLAUDE_MANIFEST, as_json(lambda data: data["skills"].pop())),
        "do not match the folders under skills/",
    ),
    "the-two-marketplaces-differ": (
        rewrite(".github/plugin/marketplace.json", as_json(lambda data: data.update(x=1))),
        "  - .github/plugin/marketplace.json must be identical to "
        ".claude-plugin/marketplace.json\n",
    ),
    "a-json-file-does-not-parse": (rewrite("hooks/hooks.json", lambda _: "{"), "hooks/hooks.json:"),
    "a-skill-that-does-not-exist": (
        rewrite(PY_REVIEW, lambda text: text + "Skill `no-such-skill`\n"),
        f"  - {PY_REVIEW}: calls skill `no-such-skill`, not in skills/ or upstream.json\n",
    ),
    "a-user-only-skill-called-as-a-skill": (
        rewrite(PY_REVIEW, lambda text: text + "Skill `wayfinder`\n"),
        f"  - {PY_REVIEW}: calls `wayfinder` as a Skill, which no harness allows: only a person "
        "can start it, so give the user the line (User types `wayfinder`)\n",
    ),
    "a-model-skill-given-to-the-user": (
        rewrite(PY_REVIEW, lambda text: text + "User types `py-build`\n"),
        f"  - {PY_REVIEW}: gives the user `py-build` to type, but the agent can start it itself: "
        "Skill `py-build`\n",
    ),
    "a-file-that-does-not-exist": (
        rewrite(PY_REVIEW, lambda text: text + "`references/no-such-file.md`\n"),
        f"  - {PY_REVIEW}: names `references/no-such-file.md`, which does not exist\n",
    ),
    "a-section-number-past-the-last": (
        rewrite("skills/py-shape/SKILL.md", lambda text: text + "see section 99\n"),
        "99; only",
    ),
    "a-pack-without-a-template-section": (
        rewrite("skills/pack-adk/SKILL.md", lambda t: t.replace("## Shapes", "## Shape list")),
        "  - skills/pack-adk/SKILL.md: pack is missing the template section `## Shapes`\n",
    ),
}


def test_a_clean_copy_passes_from_the_command_line(plugin_copy: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(plugin_copy / "scripts" / "check_plugin.py")],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "plugin ok:" in result.stdout


@pytest.mark.parametrize(("edit", "expected"), BROKEN_FACTS.values(), ids=BROKEN_FACTS)
def test_a_broken_fact_is_reported(
    plugin_copy: Path,
    check_copy: Callable[[], tuple[str, int]],
    edit: Callable[[Path], None],
    expected: str,
) -> None:
    edit(plugin_copy)

    output, returncode = check_copy()

    assert returncode == 1
    assert expected in output
