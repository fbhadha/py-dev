"""Shared pieces for the python-dev hooks: payload shapes, the repo, the current branch.

Every hook fails open: any exception in here must be caught by the caller and
turned into "no decision", so a broken guard can never block ordinary work.

The rule the hooks enforce is small on purpose: `main` changes only by a merge the
human said yes to. Work happens on a branch; the branch is the guard. So the
command guard asks (through the harness's own permission prompt) before a commit,
merge or push that lands on `main`, denies the git commands that destroy history,
and the stop gate refuses to end a turn with red ruff. Nothing watches individual
files: the diff the human reads before saying "merge" is the review of those.

PYTHON_DEV_GUARD=off turns the asks off for one session. The denies stay.

Where a hook runs: Copilot CLI starts plugin hooks in the plugin's install folder,
not the project, so every hook calls enter_project() before its first git call.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAIN_BRANCHES = {"main", "master", "trunk"}
OFF_VALUES = {"off", "0", "false", "no"}
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_ENV = ("COPILOT_PROJECT_DIR", "CLAUDE_PROJECT_DIR")


def enter_project(payload: dict) -> None:
    """Change into the session's project: the payload's cwd, else the harness's project variable."""
    for candidate in (payload.get("cwd"), *(os.environ.get(name) for name in PROJECT_ENV)):
        if isinstance(candidate, str) and candidate and Path(candidate).is_dir():
            os.chdir(candidate)
            return


def plugin_version() -> str:
    try:
        return str(json.loads((PLUGIN_ROOT / "plugin.json").read_text(encoding="utf-8"))["version"])
    except (OSError, ValueError, KeyError):
        return "unknown"


def read_payload() -> dict:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "")


def tool_args(payload: dict) -> dict:
    for key in ("tool_input", "toolArgs", "tool_args"):
        args = payload.get(key)
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                return {}
        if isinstance(args, dict):
            return args
    return {}


def session_id(payload: dict) -> str:
    raw = str(payload.get("session_id") or payload.get("sessionId") or "default")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", raw)[:80]


def guard_off() -> bool:
    return os.environ.get("PYTHON_DEV_GUARD", "").strip().lower() in OFF_VALUES


def repo_root() -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    )
    return Path(result.stdout.strip()) if result.returncode == 0 else None


def current_branch() -> str:
    """The checked-out branch name; empty when detached or outside a repo."""
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def is_main(branch: str) -> bool:
    return branch in MAIN_BRANCHES


def git_lines(*args: str) -> list[str]:
    """The non-empty stdout lines of a git command; empty when it fails."""
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def normalize_repo(ref: str, default_host: str = "github.com") -> str:
    """'host/owner/repo' from a URL, an ssh address, 'host/owner/repo' or 'owner/repo'."""
    ref = re.sub(r"\.git/?$", "", ref.strip().strip("'\""))
    url = re.match(r"^(?:https?|ssh)://(?:[^@/]+@)?([\w.-]+)/(.+)$", ref)
    ssh = re.match(r"^[\w.-]+@([\w.-]+):(.+)$", ref)
    m = url or ssh
    if m:
        return f"{m.group(1)}/{m.group(2).strip('/')}".lower()
    parts = ref.strip("/").split("/")
    if len(parts) >= 3 and "." in parts[0]:
        return "/".join(parts).lower()
    return f"{default_host}/{'/'.join(parts)}".lower()


def remote_repo(name: str = "origin") -> str:
    """The normalized repo a git remote points at; empty when there is no such remote."""
    result = subprocess.run(
        ["git", "remote", "get-url", name], capture_output=True, text=True, check=False
    )
    return normalize_repo(result.stdout) if result.returncode == 0 and result.stdout.strip() else ""


def decision(kind: str, reason: str) -> None:
    """Answer in both harnesses' shapes: Claude Code nested, Copilot top level."""
    json.dump(
        {
            "permissionDecision": kind,
            "permissionDecisionReason": reason,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": kind,
                "permissionDecisionReason": reason,
            },
        },
        sys.stdout,
    )
