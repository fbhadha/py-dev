# How to add a hook test

Mirrors `tests/hooks/test_guard_eval.py`, the smallest hook test module, and the fixtures in `tests/conftest.py`. When this file and those disagree, the code is right and this file is wrong; fix the file.

## When this is the right shape

The request looks like "the hook must answer <ask, deny, allow or block> when <a command, an edit, a branch, a payload shape>", or "the baseline's script `check_<what>.py` must <pass or refuse> this change". It stays inside `tests/` and, for a new script, `scripts/`. If the work changes what a hook does, that is the hook's own ticket; the test is written first, in the same ticket, by this how-to.

## Files you will create or change

| File | What goes in it |
|---|---|
| `tests/hooks/test_<hook>.py` | one module per hook (`scripts/hooks/<hook>.py`); under 150 lines, or split by the branch or payload shape it covers (`test_guard_command.py`, `test_guard_shaping.py`) |
| `tests/baseline/test_<script>.py` | one module per baseline script (`scripts/check_<what>.py`, `adr_sync.py`), driving this repo's copy under `scripts/` when it has one, with `test_copy_matches_template` |
| `tests/conftest.py` | only when every module needs a new fixture; never a helper for one module |

## Steps

1. Take the fixtures, never a subprocess of your own: `repo` (a scratch git repo on `main`, fresh per test), `git` (a command in it), `hook(name, payload)` (that hook's `Answer`: decision, stdout, exit code), `guard(command)` (the command guard's decision), `check(script, range)` (`passed` or `refused`). `outside=True` and `copilot=True` start the process from above the repo with the repo only in the payload, the way Copilot CLI starts hooks; cover both shapes when the hook reads the payload.
2. Name the test after the decision: `test_write_elsewhere_denied`, `test_main_session_passes`. One decision per test; a table of commands with the same decision is one `@pytest.mark.parametrize` with `ids=`.
3. The expected value is the decision the persona or README promises (`README.md`, "What the hooks guard"), never what the hook printed when you ran it.
4. Run the module alone (`uv run pytest tests/hooks/test_<hook>.py`); it must pass without the others, since every test builds its own repo.
5. `uv run ruff check tests && uv run ruff format --check tests`; the commit gate holds a test module to 150 lines.

## What usually goes wrong

- A test that switches branch and leaves the repo there for the next test. It cannot: `repo` is per test. If a module needs a branch for every test, a module-level fixture that calls `git("switch", "-q", "-c", ...)` is the answer, not a shared repo.
- A skip when a tool is missing. ruff and bash are in the dev group and on every CI runner; `scripts/check_test_diff.py` refuses an added skip.
- Reading the decision from stdout by hand. `hook(...)` already parsed it; a hook that prints nothing allows.
