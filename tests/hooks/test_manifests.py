"""Both hook manifests fail open when the plugin root is not expanded.

Copilot CLI and VS Code deny every tool call when a pre-tool command hook exits
non-zero, and VS Code expands no plugin root for an Agent Plugins manifest. So the
manifest's command exits 0 with no decision when its root variable is empty, and
asks as usual when it is set.
"""

import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

MANIFEST = {
    "copilot": ("com.github.copilot/hooks/hooks.json", "PLUGIN_ROOT"),
    "claude": ("hooks/hooks.json", "CLAUDE_PLUGIN_ROOT"),
}


def command_of(root: Path, harness: str) -> str:
    manifest = json.loads((root / MANIFEST[harness][0]).read_text(encoding="utf-8"))
    if harness == "copilot":
        return manifest["hooks"]["preToolUse"][0]["bash"]
    return manifest["hooks"]["PreToolUse"][0]["hooks"][0]["command"]


def run_manifest(
    root: Path, repo: Path, harness: str, decision: Callable[[str], str], *, expanded: bool
) -> tuple[int, str]:
    var = MANIFEST[harness][1]
    env = {k: v for k, v in os.environ.items() if k not in ("PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT")}
    if expanded:
        env[var] = str(root)
    payload = {
        "sessionId": "s",
        "timestamp": 0,
        "cwd": str(repo),
        "toolName": "bash",
        "toolArgs": {"command": "git commit -m x", "description": "run"},
    }
    result = subprocess.run(
        ["bash", "-c", command_of(root, harness)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=repo.parent,
        env=env,
        check=False,
    )
    return result.returncode, decision(result.stdout)


@pytest.mark.parametrize("harness", ["copilot", "claude"])
def test_unexpanded_plugin_root_exits_0_and_allows(root, repo, harness: str, decision) -> None:
    assert run_manifest(root, repo, harness, decision, expanded=False) == (0, "allow")


@pytest.mark.parametrize("harness", ["copilot", "claude"])
def test_expanded_plugin_root_asks_on_main(root, repo, harness: str, decision) -> None:
    assert run_manifest(root, repo, harness, decision, expanded=True) == (0, "ask")
