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
