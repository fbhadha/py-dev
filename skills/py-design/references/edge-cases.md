# Edge cases: find them, decide them, test them

An edge case is an input, a state or a sequence of events at the limit of what a behaviour accepts, or just past it: an empty list, the value 18 when the rule is "18 or older", the second run of the same load, a timeout on the third page. Tests written from the happy path do not reach them, and most escaped bugs sit there. `py-shape` lists a behaviour's edge cases when it cuts a ticket; `py-build` re-checks the list against the code before the first line and turns it into tests; `py-review` checks the ticket's table against the tests.

"The edge" in this plugin is a system boundary (rule 2, [boundaries.md](boundaries.md)). An edge case is a different thing: always write it in full.

## Rules

1. **A type rules out what it can.** Before planning a test, ask whether a type makes the edge case impossible: a constrained field where outside data is parsed (`Annotated[int, Field(ge=0, le=100)]`), an enum instead of a string, a `NewType` id, a constructor that rejects the bad state, keyword-only parameters against a swapped pair. Then one test at the parse covers it instead of a check and a test in every caller (`SKILL.md` rules 2, 7 and 14).
2. **Error paths are behaviours.** Every exception a function raises, and every error a dependency can signal to it, is an edge case with a decided outcome and a test that makes it happen. Test the handler, not only the call: Yuan and others (OSDI 2014) traced most catastrophic failures in five production systems to errors the code had detected and then handled wrongly.
3. **Sequences are short.** A repeat, an out-of-order call, a call on work already done, an interruption after the write and before the cursor moves, then a re-run. The same study found almost every failure needed three events or fewer; a ten-step scenario rarely earns its cost.
4. **An expected value nobody decided is a question.** When no spec line, worked example or user answer says what should happen, the edge case is a decision for the user: a numbered grill question with your recommended answer while shaping; a stop while building, where a change of behaviour is a revision. Never a guess: in PBT-Bench (2026) a made-up expected value was the commonest way an agent's tests went wrong.
5. **Through the seam the ticket names, in proportion.** Matt Pocock's `tdd` puts testing effort on the critical paths and the complex logic instead of every edge case; this list is how you choose. The seams are the ticket's; an edge case is tested through them, never through a seam added to reach it. List only the edge cases that change something: a type, a test or a question. A quick ticket gets a short list; a new adapter or parser gets every category. One line names the categories you went through and why any were skipped. An edge case the public interface cannot reach is impossible (delete the branch) or a sign the seam is wrong (stop and re-plan).
6. **Example tests and property tests, both.** Example tests pin the named edge cases with literal expected values; a property test checks a rule across generated inputs. They catch different bugs.
7. **Check that the tests can fail.** Before review, mutate the modules the ticket changed. A surviving mutant is a missing test, an equivalent mutant or noise: decide which, one line each.

## The categories

For each behaviour (each acceptance criterion), go through these against the spec and the code it touches. Decide each edge case as **type** (ruled out by a type, with one test at the parse), **test** (with the source of its expected value), **eval** (an agent's behaviour, played by a simulated user from scenarios written outside the build session; the row's decided outcome becomes the rubric), **question** (for the user) or **out of scope** (with the ticket that holds it).

| Category | Ask |
|---|---|
| Values | Empty, `None`, zero; one; many. The minimum, the maximum, and one past each: for "1 to 100", test 0, 1, 100 and 101. Negative where only positive makes sense. A tie where a rule picks a winner. |
| Types and formats | What the type hint allows and the domain does not: a `bool` for an `int`, `nan`, `inf`, an empty string that is not `None`, surrounding spaces, case, two Unicode forms of the same text, a date in another format, a row with fewer fields than the header. |
| Domain values | Money, time and identifiers ([boundaries.md](boundaries.md)), and the design rules of each pack under `## Packs` in `AGENTS.md`. |
| Calls out | Each error a dependency can signal: timeout, connection reset, 429, 5xx, a 4xx the input caused, a malformed or partial response, an empty page, the last page. What the code does next: retry, reject, quarantine or fail loudly (the spec's Failure section). |
| State and sequence | Run twice. Run on data already processed. Call out of order. Interrupted after the write and before the cursor moves, then re-run. |
| Concurrency | Two runs at once on one target. A task cancelled during a write. One task in a `TaskGroup` failing, which cancels the others. |
| Scale | The volume the spec names, and ten times it. A page boundary. A batch of exactly the batch size, and one more. |
| Trust | Untrusted input reaching a path, a query, a shell command or a log line. A secret or personal data reaching a log or an error message. |
| Configuration | A setting missing, empty or of the wrong type; a default that is wrong for this deployment. |
| Use | How a person actually calls it: the README's example verbatim; the arguments in another order; a value pasted with a trailing newline or quotes; an agent asked in everyday words, with a detail missing, by someone who has not read its description (`pack-adk`'s outside user). |

## Python traps

| Code | What happens |
|---|---|
| `isinstance(True, int)` | `True`: a bool passes an int check. |
| `round(2.5)`; `Decimal(0.1)` | `2`, halves round to even; the float's error is kept. Money is `Decimal("0.10")`, quantized with a named rounding mode; `json.dumps` refuses a `Decimal`, so serialise it on purpose. |
| `float("nan")` | Never equal to itself; `sorted` leaves a list containing it unsorted; `min(nan, 1)` and `min(1, nan)` differ. |
| A naive and an aware `datetime` | `<` raises `TypeError`; `==` is silently `False`. |
| `date(2024, 2, 29).replace(year=2025)` | `ValueError`. There is no month arithmetic: decide what "one month after January 31" means. |
| A local time on a daylight-saving change | Happens twice (`fold`) or not at all, and Python raises nothing for the missing hour. UTC inside; convert at the edge. |
| `"ß".casefold()`; NFC and NFD | `"ss"` (`lower()` leaves it); the same accented text has a different `len` in each form. Compare with `casefold()` on one normal form. |
| `max([])`; `zip(a, b)` | `ValueError`; stops at the shorter with no error (`strict=True` raises). Decide every aggregate's empty case. |
| A generator read twice; `os.path.join("data", "/etc/passwd")` | Empty the second time; `"/etc/passwd"`, an absolute second part discards the first. |
| `except Exception` around an awaited call | Does not catch `asyncio.CancelledError`, a `BaseException`. Usually right; do not widen it. |
| An `int` leaving Python | Unbounded here; 64 bits in SQLite, and a JavaScript reader of the JSON loses precision above 2**53. |

## In the ticket

The ticket's `## Edge cases` section (`py-shape`'s `references/ticket.md`): one line naming the categories gone through and why any were skipped, then one row per edge case that changes something.

```markdown
Categories: values, types and formats, calls out, state and sequence. Skipped: concurrency (one run at a time, spec Design), scale (under 1,000 rows by the spec).

| Edge case | Category | Decision | Expected value from | Test |
|---|---|---|---|---|
| Negative quantity | Values | type: `Field(gt=0)` on `OrderLine.quantity` | spec behaviour 2 | `tests/unit/test_orders_domain.py::test_negative_quantity_fails_parse` |
| Second run over the same export | State and sequence | test | spec behaviour 4: writes nothing | `tests/integration/test_orders_cli.py::test_second_run_writes_nothing` |
| Asked for a refund in everyday words, with no order number | Use | eval | spec behaviour 5: asks for the id before it refunds | `tests/evals/orders_agent/targets-12.md` row 1 |
```

A **test** row is a test in the Plan, in the slice that owns the behaviour. A **type** row names the one test at the parse. An **eval** row is a target in `tests/evals/<agent>/targets-<ticket>.md` (`py-build`'s eval step), never a unit test with the author's phrasing. A **question** row goes into the grill before the ticket is published, and the answer turns it into a test or type row; a ticket with an open question row is not `ready-for-agent`.

## Property tests (Hypothesis)

Write one for a transform or a serialiser with a rule that holds for every valid input, and a round trip for a parser. Never for a validator: "rejects what the checks reject" restates the code. Skip adapters, which their contract suite covers ([boundaries.md](boundaries.md)). No quota.

Rules worth checking, strongest first:

- **Round trip**: `parse(render(x)) == x`, always beside one example test with a literal expected value, because a round trip through the same wrong code can pass.
- **Invariant**: one output per key; the output sorted by the stated key; the total equal to the sum of the lines.
- **Idempotence**: `f(f(x)) == f(x)`; a second run writes nothing.
- **Reference model**: a slow, plainly correct version written in the test. Never compute the expected value by calling the code under test.
- **Metamorphic**: reordering the input leaves the output unchanged; a zero-amount line leaves the total unchanged.

How agents get property tests wrong (PBT-Bench's failure modes), and the rule against each:

- **Filtering the bug away.** `assume(a != b)` in a test of a function whose bug is in duplicates. Build valid inputs with strategies instead of filtering, and never `assume()` away an input because it looks unusual: duplicates, empties, equal values and boundaries are where the bugs are.
- **The wrong range.** `st.integers()` where the spec says 0 to 100 almost never produces 100 or 101. Bound strategies by the spec, and include the values just outside when the behaviour is to reject them.
- **Missing the named cases.** Every named edge case goes on the property as `@example(...)`, so it runs every time.
- **Settings.** Leave them alone. Hypothesis 6.154 and later load a built-in `ci` profile whenever the `CI` variable is set: derandomised, no deadline, no example database, so a CI failure reproduces.
- **Sequences.** `hypothesis.stateful.RuleBasedStateMachine`, only when the state and sequence category found a rule that spans calls.

## Mutation: checking that the tests can fail

Before review, for each module the ticket changed under `src/` (a bare `uv run mutmut run` when it changed more than two):

```bash
uv run mutmut run "<package>.<module>*"
uv run mutmut results               # the mutants no test killed
uv run mutmut show <mutant name>    # the change it made
```

A module of a few hundred lines takes seconds, because only the tests that reach each mutant run. Past five minutes, run the domain module only and say so. For each survivor, decide which it is:

- **A missing test.** `return age >= 18`, tested at 12 and 40, leaves two survivors: `age > 18` and `age >= 19`. One test at 18 kills both. That is the boundary test the list should have planned: add it, and its row to the ticket's table.
- **An equivalent mutant**, a change no input can detect. In `if value < low: return low`, the mutant `value <= low` returns the same number when `value == low`. Record its name and one line of why in the ticket's evidence. No test for it, and no `# pragma: no mutate` without the user's word.
- **Noise**, skipped on sight: the text of a log or help message, a keyword argument removed or set to `None` that the type checker or an existing test already constrains, the case of an SQL keyword, JSON formatting. Count them in one line; never triage them one by one.

A survivor can depend on the machine: `astimezone(None)` survives where the local zone is UTC. Say which fact it depends on. The result is read at review; it is never a gate.
