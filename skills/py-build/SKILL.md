---
name: py-build
description: "Build one ticket from branch to merge: name the shape, ask Repowise, search before naming, agree the seams, Matt Pocock's implement with tdd, the checks after every green, the gates, the review, the merge question, the handoff. Use when a ticket is ready to build."
---

# Building a ticket

One ticket per session. Voice as the persona says; the user never types a skill name.

## Before the first line

1. Read the ticket by the workflow in `docs/agents/issue-tracker.md`. Its acceptance criteria and the spec's Out of Scope are the fence; anything else is scope creep, parked as a `later` ticket.
2. **Branch.** `git fetch origin && git switch -c ticket/<id>-<two-word-slug> origin/main` (no remote: `main`). Never a commit on `main`. A handoff that names a branch: switch to it instead. Shaped in this session by `py-shape`: the shaping branch, renamed.
3. **Name the shape.** Ask: "This looks like adding another <shape>, correct?" A shape has a how-to in `docs/howto/`. Inside the how-to's layers: build by it. Outside them, or no how-to: a new shape. Skill `grilling`, then Skill `domain-modeling`; extend the how-to and its example first; then build from the edited how-to. Docs first, then code.
4. **Ask the index.** One call for every file you expect to touch: `uv run repowise risk -t <f1> -t <f2> ...`. `uv run repowise why <file>` only for a file that call marks governed or bug-magnet. Tell the user in two sentences what you learned.
5. **Search before you name.** For every new function, type or module: grep `CONTEXT.md` for the term and run `uv run repowise search <name>`. A hit means reuse, or a named difference. Never a second copy.
6. **Agree the seams.** Say which seam each test drives and where its expected values come from (spec, worked example, fixture). Skill `py-design` when a module, class, seam or layout is in question, and the packs listed under `## Packs` in `AGENTS.md` while designing.

## Building

File `implement` (Matt Pocock's), with Skill `tdd` for each slice. Inside every slice:

- Tests are read-only from red to green. Never loosen an assertion, delete a test or add a skip to get green.
- Expected values come from outside the code, never computed the way the code computes them.
- Mock only at system boundaries. Prefer the in-memory adapter the how-to names.
- After each green: `uv run ruff check <files>`, `uv run mypy`, `uv run pytest <that test file>`. Show the last lines.
- Noisy output through `uv run repowise distill <command>` (the full suite, `pre-commit run --all-files`, `git log`); it keeps failures and the exit code and leaves a `[repowise#ref]` marker you can `repowise expand`.
- Never `--no-verify`. Never edit a rule to pass.

Commit as you go, with the ticket id and the decision in the message, never "wip". Update the how-to, `CONTEXT.md` or an ADR when the change touched what they describe.

## Before review

`uv run repowise distill uv run pytest -m "not eval"`, `uv run repowise distill uv run pre-commit run --all-files`, `uv run lint-imports`, `uv run python scripts/check_test_diff.py`, then `DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y` and `uv run python scripts/repowise_gate.py`. A finding the gate or the test-diff check reports is fixed now. Then Skill `py-review`, and fix the 🔴.

## Landing

1. `git push -u origin <branch>`. GitHub or GitLab remote: `gh pr create --title "<ticket id>: <title>" --body-file -` (`glab mr create --title ... --description-file -`) with the ticket, each acceptance criterion ticked with the test that proves it, and the gate output; CI runs there. No remote: skip.
2. Show the merge summary: files outside `src/` and `tests/` first, one sentence each on why they changed; then the commits; then the check results. Ask: "Merge to main?"
3. Yes: `gh pr merge --merge --delete-branch` (`glab mr merge`), or with no remote `git switch main && git merge --no-ff <branch> && git branch -d <branch>`. The hook asks once more; that is the same yes. Merge commits, never squash: Repowise reads the slice history. Not yet: leave the branch and the PR open, say what is missing, stop.
4. Close the ticket with the evidence (test names, gate output, the merge commit). Hand off (the persona's session boundaries).

A command a skill names does not exist, or a check blocks what it should not: a plugin defect; the persona says how to file it.
