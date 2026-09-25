# How to add a plugin check

Mirrors `scripts/check_template_deps.py`, the smallest check, which runs in CI on every pull request. When this file and the example disagree, the example is right and this file is wrong; fix the file.

## When this is the right shape

The request looks like "CI should fail when <some fact about the plugin's own files> stops being true": a manifest lists a skill that is not there, a template does not resolve, a pinned upstream moved. It stays inside `scripts/` and `.github/workflows/validate.yml`. If the work needs a hook, a skill or a template to change, stop; it is a different shape and needs the interview.

## Files you will create or change

| File | What goes in it |
|---|---|
| `scripts/check_<what>.py` | the check: a module docstring that says what must hold and why, constants for the paths it reads, small pure functions, and a `main() -> int` that prints every problem then returns 1, or prints one line of evidence and returns 0 |
| `.github/workflows/validate.yml` | one step under the `plugin` job: `- name: <the sentence that must hold>` and `run: python scripts/check_<what>.py` |
| `README.md`, "Working on this repo" | the check's one line in the list of what CI runs |

## Steps

1. Write the docstring first: the sentence CI will fail on, and where the agent would otherwise have paid for the mistake. That sentence is the workflow step's `name`.
2. Make it fail for the right reason before it passes: break the fact by hand (edit the manifest, move the file), run `python scripts/check_<what>.py`, watch it print the problem and exit 1, then restore the file and watch it exit 0.
3. Read paths through `ROOT = Path(__file__).resolve().parent.parent`, as the example does, so the check runs from any working directory and from CI.
4. Wire the step into `validate.yml` next to the other checks, in the order a reader would want to hear about failures.
5. Run `uv run pre-commit run --files scripts/check_<what>.py`; the commit gate holds every check to ruff, mypy strict and 400 lines.
6. Add the check's line to the README list.

## What usually goes wrong

- A check that reads the installed plugin cache instead of this tree. Everything it reads is under `ROOT`.
- Printing a summary and hiding the reason. Print each problem with its path first; the summary line is last.
- A second check for a fact `check_plugin.py` already covers. Read its docstring before writing a new file.
