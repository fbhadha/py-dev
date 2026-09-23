#!/usr/bin/env python3
"""PreToolUse guard for the shell tool: main changes only by a merge the human said yes to.

Denied outright (no asking): force-push, hard reset, history rewrite, --no-verify,
force-deleting a branch, setting PYTHON_DEV_GUARD inside a command, and
`pre-commit uninstall`. These are on the persona's never list.

Asked (the harness prompts the human): anything that lands on main. A commit while
main is checked out, a merge into main (checked out, or switched to in the same
command), a push to main (explicit, or a bare push while on main), and merging a
pull or merge request from the command line (`gh pr merge`, `glab mr merge`). On
a branch, nothing asks: commit, push and merging main into the branch are free.

Also asked: a commit on a `shaping/` branch that carries files under src/ or
tests/ (staged, or modified when the commit has -a). Shaping decides; a ticket
builds; the reason says so and names the files.

Also asked: anything that sends content to a repo other than this project's
`origin`. A `gh` or `glab` command with `-R`/`--repo` naming another repo, a
`gh api` call that writes under another repo's path, a gist, or a `git push` to
a remote or URL that is not origin. Reads (`view`, `list`, `status`, `diff`) do
not ask. The reason names both repos so the human can see what is leaving.

Edit tools are handed to guard_edit.py (no ticket, no code), so one pre-tool
entry per harness covers both. Runs in the project named by the payload's cwd:
Copilot CLI starts plugin hooks in the plugin's own folder.

Reads either harness's payload. Any failure exits 0 with no output.
"""

from __future__ import annotations

import re
import sys

import _common as c
import guard_edit

GIT = r"\bgit\b[^|;&]*"
DENY: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            GIT + r"\bpush\b[^|;&]*(\s--force(-with-lease)?\b|\s-f\b|\s-[a-zA-Z]*f[a-zA-Z]*\b)"
        ),
        "force-push",
    ),
    (re.compile(GIT + r"\breset\b[^|;&]*\s--hard\b"), "hard reset"),
    (re.compile(GIT + r"\brebase\b"), "history rewrite (rebase)"),
    (re.compile(GIT + r"\bcommit\b[^|;&]*\s--amend\b"), "history rewrite (amend)"),
    (re.compile(GIT + r"\b(filter-branch|filter-repo)\b"), "history rewrite"),
    (
        re.compile(GIT + r"\b(commit|push|merge)\b[^|;&]*\s(--no-verify|-n)\b"),
        "skipping the commit hooks",
    ),
    (re.compile(GIT + r"\bbranch\b[^|;&]*\s-D\b"), "force-deleting a branch"),
    (re.compile(r"\bPYTHON_DEV_GUARD\s*="), "turning this guard off from inside a command"),
    (re.compile(r"\bpre-commit\s+uninstall\b"), "uninstalling the commit gate"),
]

MAIN = r"(main|master|trunk)"
COMMIT = re.compile(GIT + r"\bcommit\b")
MERGE = re.compile(GIT + r"\bmerge\b")
PUSH = re.compile(GIT + r"\bpush\b")
PUSH_TO_MAIN = re.compile(GIT + r"\bpush\b[^|;&]*\s(\S+\s+)?(\S+:)?" + MAIN + r"\b")
SWITCH_TO_MAIN = re.compile(GIT + r"\b(switch|checkout)\s+(-q\s+)?" + MAIN + r"\b")
PR_MERGE = re.compile(r"\b(gh\s+pr\s+merge|glab\s+mr\s+merge)\b")
REPO_FLAG = re.compile(r"\b(?:gh|glab)\b[^|;&]*?\s(?:-R|--repo)[\s=]+(\S+)")
API_PATH = re.compile(r"\bgh\s+api\b[^|;&]*?\s(?:/)?(?:repos|projects)/([\w.-]+/[\w.-]+)")
API_WRITE = re.compile(
    r"\bgh\s+api\b[^|;&]*?(\s-X\s*(POST|PUT|PATCH|DELETE)\b|\s(-f|-F|--field|--raw-field|--input)\b)"
)
GIST = re.compile(r"\bgh\s+gist\s+create\b")
READ_VERBS = re.compile(r"\b(?:gh|glab)\s+\w+\s+(view|list|status|diff|checks|download|clone)\b")
PUSH_TARGET = re.compile(r"\bgit\b[^|;&]*\bpush\b(?:\s+-\S+)*\s+(\S+)")
SHAPING = "shaping/"
PRODUCT = re.compile(r"^(src|tests)/")
COMMIT_ALL = re.compile(GIT + r"\bcommit\b[^|;&]*\s-(?:-all|[a-zA-Z]*a[a-zA-Z]*)\b")


def is_shell_tool(name: str) -> bool:
    name = name.lower()
    return not name or "bash" in name or "shell" in name or "terminal" in name or name == "run"


def denied(command: str) -> str | None:
    for pattern, label in DENY:
        if pattern.search(command):
            if "guard" in label:
                return (
                    f"python-dev blocks {label}. The human sets PYTHON_DEV_GUARD=off in their "
                    "own shell before the session, or answers the prompt; when no prompt can "
                    "reach them, stop and give them the command to run themselves."
                )
            if "commit gate" in label:
                return (
                    f"python-dev blocks {label}. A check that blocks every commit is a defect "
                    "in the check's placement, not a reason to remove the gate: whole-program "
                    "checks belong in CI (see py-baseline); say what blocked and stop."
                )
            return (
                f"python-dev blocks {label}. This is on the never list: it destroys history "
                "the user or a teammate may depend on. Make a new commit instead, or ask the "
                "user to run it themselves."
            )
    return None


def lands_on_main(command: str, branch: str) -> str | None:
    """What this command would do to main, or None when it stays on a branch."""
    on_main = c.is_main(branch) or bool(SWITCH_TO_MAIN.search(command))
    if PR_MERGE.search(command):
        return "merge a pull request into main"
    if MERGE.search(command) and on_main:
        return "merge into main"
    if PUSH_TO_MAIN.search(command) or (PUSH.search(command) and on_main):
        return "push to main"
    if COMMIT.search(command) and on_main:
        return "commit on main"
    return None


def leaves_project(command: str) -> tuple[str, str] | None:
    """(what, target) when the command sends content outside this project's origin."""
    origin = c.remote_repo("origin")
    host = origin.split("/")[0] if origin else "github.com"
    if GIST.search(command):
        return "create a gist", "a gist outside this repo"
    flagged = REPO_FLAG.search(command)
    if flagged and not READ_VERBS.search(command):
        target = c.normalize_repo(flagged.group(1), host)
        if target != origin:
            return "send to another repo", target
    api = API_PATH.search(command)
    if api and API_WRITE.search(command):
        target = c.normalize_repo(api.group(1), host)
        if target != origin:
            return "write to another repo through the API", target
    push = PUSH_TARGET.search(command)
    if push and not push.group(1).startswith("-"):
        name = push.group(1)
        target = (
            c.remote_repo(name) if not re.search(r"[:/]", name) else c.normalize_repo(name, host)
        )
        if name != "origin" and target and target != origin:
            return "push to another repo", target
    return None


def shaping_builds(command: str, branch: str) -> list[str]:
    """Product files a commit on a shaping branch would carry; empty anywhere else."""
    if not branch.startswith(SHAPING) or not COMMIT.search(command):
        return []
    files = c.git_lines("diff", "--cached", "--name-only")
    if COMMIT_ALL.search(command):
        files += c.git_lines("diff", "--name-only")
    return sorted({path for path in files if PRODUCT.match(path)})


def leaving_reason(command: str) -> str | None:
    found = leaves_project(command)
    if not found:
        return None
    what, target = found
    origin = c.remote_repo("origin") or "no origin remote"
    return (
        f"python-dev: this would {what}: {target}. This project's repo is {origin}. "
        "Approve only if you have seen exactly what will be sent; nothing from this repo's "
        "code, paths, hosts, keys or data should leave without your say-so."
    )


def shaping_reason(command: str, branch: str) -> str | None:
    built = shaping_builds(command, branch)
    if not built:
        return None
    return (
        f"python-dev: this shaping branch is about to commit product code "
        f"({', '.join(built[:5])}). Shaping decides; a ticket builds. Approve only if "
        "you asked for this in your own words; otherwise the change belongs on a "
        "prototype/<slug> branch or in a ticket."
    )


def main_reason(command: str, branch: str) -> str | None:
    action = lands_on_main(command, branch)
    if not action:
        return None
    return (
        f"python-dev: this would {action}. Main changes only by a merge you said yes "
        "to, after the checks and the review. If this is that merge, approve it. If "
        "the agent is committing straight to main, it should be on a branch "
        "(`git switch -c ticket/<id>`)."
    )


def decide(payload: dict) -> tuple[str, str] | None:
    """(decision, reason) for this tool call, or None to let it through."""
    name = c.tool_name(payload)
    if guard_edit.is_edit_tool(name):
        return guard_edit.check(payload)
    command = str(c.tool_args(payload).get("command", ""))
    if not is_shell_tool(name) or not command:
        return None
    reason = denied(command)
    if reason:
        return "deny", reason
    if c.guard_off() or c.repo_root() is None:
        return None
    branch = c.current_branch()
    asked = (
        leaving_reason(command) or shaping_reason(command, branch) or main_reason(command, branch)
    )
    return ("ask", asked) if asked else None


def main() -> int:
    try:
        payload = c.read_payload()
        c.enter_project(payload)
        found = decide(payload)
        if found:
            c.decision(*found)
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
