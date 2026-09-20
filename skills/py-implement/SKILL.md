---
name: py-implement
description: "Build one ticket test-first by the repo's how-to, with Repowise pre-edit checks, checks after each slice, review, commit and handoff. Use when a ticket is ready or a handoff names one. One ticket per session."
license: Apache-2.0
metadata:
  author: fbhadha
  version: 0.1.0
  tags: [python, implement, tdd, tickets]
---

# Python implement

Matt Pocock's `implement` says: build what the spec or tickets describe, use `tdd` at pre-agreed seams, typecheck and run single test files often and the full suite once at the end, then `code-review`, then commit. This skill is that, with the Python rules and the repo's memory wired in. Guide voice: before each slice, one plain paragraph on what you are about to build and why it is next; after it, one on what changed and what the checks said.

## 0. What you are building

- If the user's message is a handoff document path, read it first. It answers most of what follows; do not re-ask.
- Fetch the ticket by the workflow in `docs/agents/issue-tracker.md`. Read its body, acceptance criteria and comments. A spec instead of a ticket is fine only when it fits one session; otherwise stop and say `to-tickets` comes first.
- Read `docs/agents/mode.md`. Unattended work is allowed only when it says `unattended: ticket:<this id>`; then every one-way door becomes a question written into the PR body, and the run ends in a PR, never a merge.

## 1. Before the first line

1. **Name the shape.** "This looks like adding another <shape>, correct?" Wait for the answer. Read the matching how-to in `docs/howto/` and its example package. No match, or the work leaves the how-to's layers: it is a new shape; call the Skill tool with "grilling" and "domain-modeling", extend the how-to and its example first, then continue from the edited how-to. Docs first, then code.
2. **Check the scope.** The ticket's acceptance criteria and the spec's Out of Scope are the fence. Anything the user asks for outside it is scope creep: say so, park it as a `later` ticket, do not build it here.
3. **Ask the index.** Call the Skill tool with "pre-modification-check" on every file you expect to touch (callers, co-change partners, bug-magnet flag, governing decisions) and with "architectural-decisions" when a decision governs one of them. Repeat what you learned to the user in two sentences. Without MCP: `uv run repowise why <file>` and `uv run repowise risk -t <file>`.
4. **Search before you name.** For every new function, type or module: the term in `CONTEXT.md`, the name in the index (Skill tool with "codebase-exploration", or `uv run repowise search <name>`). A hit means reuse or a named difference, never a second copy.
5. **Agree the seams.** Say which seam each test will drive (the highest existing one; a new seam only with a second adapter in sight) and the expected values' source (spec, worked example, fixture). Call the Skill tool with "py-design" when a shape question comes up.

## 2. Slices

Call the Skill tool with "tdd". One red, one green, repeat. Each slice is one acceptance criterion or one seam.

Rules that hold inside every slice:

- **Tests are read-only from red to green.** Never loosen an assertion, delete a test, or add a skip to get green. If a test is wrong, stop, say why, and get the user's explicit override in their words before touching it; record the override in the ticket.
- **Expected values come from outside the code.** Never compute them the way the implementation does.
- **Mock only at system boundaries.** Prefer the in-memory adapter the how-to names.
- **After each green:** `uv run ruff check <files>`, `uv run mypy` (src only), `uv run pytest <the test file>`. Show the last lines. Red stays red until fixed; never `--no-verify`, never edit a rule to pass.
- **Fast test loop.** When coverage has been ingested (`uv run repowise coverage status`), `uv run repowise impacted-tests --format list | xargs uv run pytest` runs only the tests the change touches. The full suite still runs once at the end.
- **Comments say why.** A TODO needs an owner and a ticket; anything that reads like an instruction to a model is deleted before commit.

## 3. Before review

1. `uv run pytest -m "not eval"` in full. Show the tail.
2. `uv run pre-commit run --all-files`.
3. `uv run repowise update`, then `uv run python scripts/repowise_gate.py` on the working tree. A finding it introduced is fixed now, not explained away.
4. Docs the change touched: the how-to if the shape moved, `CONTEXT.md` for any new term, an ADR (template, `## Scope`, then `uv run python scripts/adr_sync.py`) for any decision the user made on the way. A junior reader must be able to continue from the docs alone.

## 4. Review, commit, close

1. Call the Skill tool with "py-review" against the branch point. Fix 🔴 findings now; 🟠 and 🟡 with the user's say-so, or as `later` tickets.
2. Commit on the current branch. The message names the ticket id in the tracker's form (`task-12`, `#12`) and the decision the change embodies, never "wip" or "fixes". One commit per slice is fine; squashing is the user's call.
3. Update the ticket by the tracker workflow: comment with what landed and the evidence (the test names, the gate output), then close or set Done. In unattended mode open the PR with before-and-after evidence in the body instead.

## 5. Hand off

One ticket per session. When this one is closed: open Matt Pocock's `handoff` (locate it with `find_skill.py`, read the file, follow it) with the argument "implement the next ready ticket of <spec>", carrying the branch, the how-to and shape, the seams, the terms, the governing ADRs, the commands, and `py-implement` as the suggested skill. Then say: "Open a new session in this repo and paste that path as your first message." Stop.
