---
name: py-build
description: "Build one ticket from branch to merge: check its plan against the code, show the plan and get a go, build slice by slice with the test first, the checks after every green, the gates, the review, the merge question, the ticket closed with evidence, the handoff. Use when a ticket is ready to build."
---

# Building a ticket

One ticket per session. Voice is the persona's section 2; the user never types a skill name. The ticket's plan came from `py-shape`; this skill checks it, shows it, and builds it.

## Before the first line

1. **Read the ticket** by the workflow in `docs/agents/issue-tracker.md`, and its spec. Its acceptance criteria and Out of scope are the fence: anything else is scope creep, parked as a `later` ticket. A change to the plan itself is a revision (Skill `py-shape`, its revision route). A ticket with no plan is not ready: write the plan from `py-shape`'s `references/ticket.md` first and show it.
2. **Branch.** `git fetch origin && git switch -c ticket/<id>-<two-word-slug> origin/main` (no remote: `main`). A handoff that names a branch: switch to it instead. Shaped in this session: the renamed shaping branch. Never a commit on `main`.
3. **Name the shape.** "This is another <shape>, built by `docs/howto/<file>`, correct?" Outside every how-to's layers, or no how-to: a new shape. Grill it (`py-shape` section 3), extend the how-to and its example first, then build from the edited how-to. Docs first, then code.
4. **Ask the index, once**: `uv run repowise risk -t <f1> -t <f2> ...` for every file the plan names; `uv run repowise why <file>` for any it marks governed or bug-magnet. Tell the user in two sentences what that means for this ticket.
5. **Search before you name.** For every new function, type or module in the plan: grep `CONTEXT.md` and run `uv run repowise search <name>`. A hit means reuse, or a named difference. Never a second copy.
6. **Check the plan against the code.** Every file it names exists or is marked new; every signature still fits what is there; the order still holds by `py-design`'s `references/planning.md`. Anything that changed since the ticket was written: update the ticket first and say what changed and why. Open the packs listed under `## Packs` in `AGENTS.md` while you do. Re-check the ticket's edge-case list against the code the plan touches (`py-design`'s `references/edge-cases.md`): an exception a called function raises, a `None` it can return, a limit it enforces. A new edge case with a decided outcome joins the ticket's table and a slice; an undecided one is a question before the go.
7. **Show the plan and wait.** The slices in order, each with its tests, the edge-case tests included (name, seam, where the expected value comes from), its files and signatures, and the command that proves it; then the order's reason in one sentence. Ask "Go?". No code before the go.

## Building

One slice at a time, in the plan's order. Skill `tdd` for the red-to-green discipline; if the door check reported it missing, these rules alone, and say so once.

- Write one test, run it, and watch it fail for the reason you expect; then write the least code that passes it. Never all the tests first.
- Tests are read-only from red to green. Never loosen an assertion, delete a test or add a skip to get green.
- Expected values come from outside the code (the spec, a worked example, a fixture), never computed the way the code computes them.
- Mock only at system boundaries. Prefer the in-memory adapter the how-to names.
- Edge-case tests go in the slice that owns the behaviour, through its seam, each red before its code. An edge case the seam cannot reach is impossible or the seam is wrong: remove the dead branch, or stop and re-plan.
- Property tests follow `py-design`'s `references/edge-cases.md`: strategies bounded by the spec, `@example` for every named edge case, no `assume()` on an input because it looks unusual, an oracle that never calls the code under test.
- An edge case found mid-slice: a decided outcome joins the ticket's table and is tested in this slice; an undecided one stops the slice and is asked. A change of behaviour is a revision.
- After each green: `uv run ruff check <files>`, `uv run mypy`, `uv run pytest <that test file>`. Then say in one or two lines what the slice added (the test that passed, the file that changed) and which slice is next.
- Noisy output goes through `uv run repowise distill <command>` (the full suite, `pre-commit run --all-files`, `git log`); it keeps failures and the exit code and leaves a `[repowise#ref]` marker you can `repowise expand`.
- The plan turns out wrong (a file that must change is not in it, a signature does not work, a slice is bigger than it looked): stop, say what and why, update the ticket's plan, and get a go on the change before going on.
- Never `--no-verify`. Never edit a rule to pass.

Commit after each green slice, with the ticket id and the decision in the message, never "wip". Update the how-to, `CONTEXT.md` or an ADR when the change touched what they describe.

## Before review

`uv run repowise distill uv run pytest -m "not eval"`, `uv run repowise distill uv run pre-commit run --all-files`, `uv run lint-imports`, `uv run python scripts/check_test_diff.py`, then `DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y` and `uv run python scripts/repowise_gate.py`. A finding the gate or the test-diff check reports is fixed now. Then `uv run mutmut run "<package>.<module>*"` for each `src/` module the ticket changed and `uv run mutmut results`: kill each survivor with a test, or record it in one line as equivalent or noise (`py-design`'s `references/edge-cases.md`). Then Skill `py-review`, and fix the 🔴.

## Landing

1. `git push -u origin <branch>`. GitHub or GitLab remote: `gh pr create --title "<ticket id>: <title>" --body-file -` (`glab mr create --title ... --description-file -`) with the ticket, each acceptance criterion ticked with the test that proves it, and the gate output; CI runs there. No remote: skip.
2. Show the merge summary: files outside `src/` and `tests/` first, one sentence each on why they changed; then the commits; then the check results. Ask: "Merge to main?"
3. Yes: `gh pr merge --merge --delete-branch` (`glab mr merge`), or with no remote `git switch main && git merge --no-ff <branch> && git branch -d <branch>`. The hook asks once more; that is the same yes. Merge commits, never squash: Repowise reads the slice history. Not yet: leave the branch and the PR open, say what is missing, stop.
4. Close the ticket with the evidence: the test names, the gate output, the mutation survivors and their triage, the merge commit. The tracker file says how.
5. **Handoff.** Write `${TMPDIR:-/tmp}/python-dev/handoff-<ticket id>.md`: the branch and whether it merged; the spec; what this ticket delivered; the next ticket on the frontier and why it is next; the shape and the seams; the terms and ADRs touched; the commands to run first; and anything the next session must not re-ask. No keys, tokens or passwords. Then the persona's session boundary (section 6).

A command a skill names does not exist, or a check blocks what it should not: a plugin defect; the persona says how to file it.
