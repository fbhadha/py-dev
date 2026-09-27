"""find_skill.py --typed: the exact line a person types, which the persona gives the user.

Copilot CLI 1.0.88 starts a plugin's user-only skill from `/<plugin>:<skill>` and answers
"Unknown command" to the bare name; a skill installed on its own is `/<skill>`.
"""

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

USER_ONLY = "---\nname: {name}\ndisable-model-invocation: true\n---\n"


@pytest.fixture
def typed(root: Path, tmp_path: Path) -> Callable[[str], tuple[str, int]]:
    """A home with Matt's plugin installed and a project shipping its own `triage` skill."""
    home = tmp_path / "typed-home"
    plugin = home / ".copilot" / "installed-plugins" / "mattpocock" / "mattpocock-skills"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text('{"name": "mattpocock-skills"}')
    skill = plugin / "skills" / "engineering" / "wayfinder"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(USER_ONLY.format(name="wayfinder"))
    project = tmp_path / "typed-project"
    (project / ".claude-plugin").mkdir(parents=True)
    (project / ".claude-plugin" / "plugin.json").write_text('{"name": "their-own-plugin"}')
    own = project / ".agents" / "skills" / "triage"
    own.mkdir(parents=True)
    (own / "SKILL.md").write_text(USER_ONLY.format(name="triage"))

    def call(name: str) -> tuple[str, int]:
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "find_skill.py"), "--typed", name],
            capture_output=True,
            text=True,
            cwd=project,
            env={"HOME": str(home), "PATH": ""},
            check=False,
        )
        return result.stdout.strip(), result.returncode

    return call


def test_a_plugin_skill_carries_its_plugin_name(typed) -> None:
    assert typed("wayfinder")[0] == "/mattpocock-skills:wayfinder"


def test_a_skill_installed_on_its_own_is_bare(typed) -> None:
    assert typed("triage")[0] == "/triage"


def test_a_missing_skill_gets_upstream_json_plugin_and_exits_1(typed) -> None:
    assert typed("teach") == ("/mattpocock-skills:teach", 1)
