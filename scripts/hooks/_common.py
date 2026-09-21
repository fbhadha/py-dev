"""Shared pieces for the python-dev hooks: payload shapes, the protected-file rule, approvals.

Every hook fails open: any exception in here must be caught by the caller and
turned into "no decision", so a broken guard can never block ordinary work.

The rule the guards enforce: an existing (git-tracked) file on the protected list
below is not changed until the human has approved it once this session. The list
is the same before and after intake (before, the status line says "intake" so the
persona knows the repo is not set up yet). Source files are never on it: the
baseline's formatters rewrite them, and the commit gate and review cover them.
The approval is the harness's own permission prompt: the pre-tool guard answers
`ask`, the post-tool recorder remembers the paths once the call went through, and
the stop gate refuses to end a turn while a protected file is modified without
that record.

Shell commands: a command known to write a protected file (`uv add`, `sed -i
README.md`, `repowise generate-claude-md`) asks, and once approved every tracked
file it actually changed is recorded, so `uv add` rewriting `uv.lock` beside
`pyproject.toml` does not trip the stop gate. A formatter (`pre-commit run`,
`ruff format`, `ruff check --fix`) never asks, and what it changed is recorded as
approved: it is mechanical, and pre-commit runs it on every commit anyway.

Turn it off: `protect-existing-files: off` in docs/agents/mode.md (itself a
protected change, so the harness asks), or PYTHON_DEV_GUARD=off for one session.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROTECTED: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    ".cursor/rules/*",
    ".github/copilot-instructions.md",
    ".github/copilot/*",
    ".github/hooks/*",
    ".github/workflows/*",
    ".gitlab-ci.yml",
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".mcp.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements*.txt",
    "Pipfile",
    "poetry.lock",
    ".python-version",
    ".pre-commit-config.yaml",
    ".gitignore",
    ".env.example",
    ".secrets.baseline",
    "README.md",
    "CONTEXT.md",
    "CONTEXT-MAP.md",
    "docs/adr/*",
    "docs/agents/*",
    "docs/architecture.md",
    "docs/howto/*",
    "scripts/repowise_gate.py",
    "scripts/adr_sync.py",
    "scripts/run_readme_blocks.py",
    "scripts/check_protected_commit.py",
)

MODE_FILE = Path("docs/agents/mode.md")
OFF_VALUES = {"off", "0", "false", "no"}
EDIT_TOOLS = re.compile(r"edit|write|create|replace", re.IGNORECASE)
WRITE_INDICATORS = re.compile(
    r"(^|[\s;&|(])(>>?|sed\s+-i|tee\b|cp\b|mv\b|rm\b|truncate\b|dd\b|patch\b|git\s+apply)"
)
KNOWN_WRITERS: tuple[tuple[re.Pattern[str], tuple[str, ...]], ...] = (
    (re.compile(r"\buv\s+(add|remove|init|lock|sync)\b"), ("pyproject.toml",)),
    (re.compile(r"\buv\s+python\s+pin\b"), (".python-version",)),
    (re.compile(r"\bpre-commit\s+autoupdate\b"), (".pre-commit-config.yaml",)),
    (re.compile(r"\bdetect-secrets\s+scan\b"), (".secrets.baseline",)),
)
GENERATE_MD = re.compile(r"repowise\s+generate-claude-md(?:.*?--output\s+(\S+))?")
FORMATTERS = re.compile(
    r"\b(pre-commit\s+run|ruff\s+format|ruff\s+check\b.*--fix|black\b|isort\b|ruff\s+--fix)"
)


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


def is_edit_tool(name: str) -> bool:
    return bool(EDIT_TOOLS.search(name)) and "view" not in name.lower()


def edit_path(args: dict) -> str:
    for key in ("file_path", "filePath", "path", "notebook_path", "target_file"):
        value = args.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def repo_root() -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    )
    return Path(result.stdout.strip()) if result.returncode == 0 else None


def relative(path: str, root: Path) -> str | None:
    try:
        return Path(path).resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return None


def is_tracked(rel: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", rel], capture_output=True, check=False
    )
    return result.returncode == 0


def is_protected(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pattern) for pattern in PROTECTED)


def guard_mode() -> str:
    """'off', 'intake' (mode.md not written yet) or 'on'. The protected list applies in both."""
    if os.environ.get("PYTHON_DEV_GUARD", "").strip().lower() in OFF_VALUES:
        return "off"
    if not MODE_FILE.exists():
        return "intake"
    for line in MODE_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        key, _, value = line.partition(":")
        if key.strip() == "protect-existing-files" and value.strip().lower() in OFF_VALUES:
            return "off"
    return "on"


def needs_approval(rel: str, mode: str | None = None) -> bool:
    mode = mode or guard_mode()
    if mode == "off" or not is_tracked(rel):
        return False
    return is_protected(rel)


def approvals_file(session: str) -> Path:
    directory = Path(tempfile.gettempdir()) / "python-dev-guard"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{session}.json"


def approved(session: str) -> set[str]:
    path = approvals_file(session)
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return set()
    return set(data) if isinstance(data, list) else set()


def approve(session: str, rels: set[str]) -> None:
    current = approved(session) | rels
    approvals_file(session).write_text(json.dumps(sorted(current)), encoding="utf-8")


def modified_tracked() -> set[str]:
    """Repo-relative paths git reports as modified, deleted or renamed (never untracked)."""
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    found: set[str] = set()
    for line in out.splitlines():
        if line[:2].strip():
            found.add(line[3:].split(" -> ")[-1].strip())
    return found


def snapshot_file(session: str) -> Path:
    return approvals_file(session).with_suffix(".snapshot.json")


def take_snapshot(session: str) -> None:
    snapshot_file(session).write_text(json.dumps(sorted(modified_tracked())), encoding="utf-8")


def changed_since_snapshot(session: str) -> set[str]:
    path = snapshot_file(session)
    before: set[str] = set()
    if path.exists():
        try:
            before = set(json.loads(path.read_text(encoding="utf-8")))
        except ValueError:
            before = set()
    return modified_tracked() - before


def is_formatter(command: str) -> bool:
    return bool(FORMATTERS.search(command))


def command_targets(command: str, root: Path) -> set[str]:
    """Protected, tracked, repo-relative paths a shell command would write."""
    targets: set[str] = set()
    for pattern, paths in KNOWN_WRITERS:
        if pattern.search(command):
            targets.update(paths)
    generate = GENERATE_MD.search(command)
    if generate:
        targets.add(generate.group(1) or "CLAUDE.md")
    if WRITE_INDICATORS.search(command):
        for token in re.findall(r"[\w./@+-]+", command):
            rel = relative(token, root) if "/" in token or "." in token else None
            if rel and is_protected(rel):
                targets.add(rel)
    return {rel for rel in targets if is_tracked(rel)}


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
