# Ticket template

A ticket is one session of work with a plan exact enough that the person or session building it decides nothing new. Every file is checked to exist when the ticket is written (or marked new), and `py-build` checks the plan against the code again before the first line. Fill every section; a quick ticket has a short plan and a short edge-case list, never absent ones.

````markdown
# <id>: <what the ticket makes true, as an imperative: "Load orders from the CSV export">

Spec: <link, or "none: one-ticket change"> · Shape: <how-to it follows> · Size: <S | M | L; L still fits one session>
Blocked by: <ids or none> · Blocks: <ids or none>

## Why

Two sentences: the outcome and why now. Quote the spec behaviour it delivers.

## Acceptance criteria

Each one testable; each names the test that proves it.

- [ ] <behaviour> → `tests/<tier>/test_<module>.py::test_<behaviour>`

## Edge cases

Listed by `py-design`'s `references/edge-cases.md`. Categories: <the ones gone through>. Skipped: <each skipped category, with one line of why>.

| Edge case | Category | Decision | Expected value from | Test |
|---|---|---|---|---|
| <the input, state or sequence> | <category> | type · test · question · out of scope | <spec line, worked example, user's answer> | `tests/<tier>/test_<module>.py::test_<behaviour>` (a type row names its one test at the parse) |

## Plan, in order

Why this order: <the planning rule: walking skeleton, riskiest first, prefactor first>.

1. **Prefactor** (only if needed): what moves and why the change is easier after it. No behaviour change; the suite is green before and after.
2. **<Slice name>**
   - Test first: `tests/<tier>/test_<module>.py::test_<behaviour>` (and the edge-case tests this slice owns, from the table); seam: <the public function or port>; expected value from: <spec line, worked example, fixture>.
   - Code: `src/<package>/<layer>/<module>.py` (new | changed): `<signature>`.
   - Done when: that test is green; `uv run ruff check <files>` and `uv run mypy` are clean.
3. **<Next slice>** ...
4. **Wire it**: the composition root `src/<package>/entrypoints/<module>.py`; the one integration test.
5. **Docs**: the how-to, the `CONTEXT.md` term or the ADR this touched, or "none".

## Files

| File | New or changed | What changes | Layer |
|---|---|---|---|

## Interfaces

```python
# every new or changed public signature, fully typed, with the exceptions it raises
```

## Out of scope

What this ticket will not do, and which ticket or `later` item holds it.

## Risks

Each with its mitigation. A one-way door here names its ADR, or the ticket is not ready.

## Verify

```bash
uv run pytest tests/<tier>/test_<module>.py
uv run pytest -m "not eval"
```
````
