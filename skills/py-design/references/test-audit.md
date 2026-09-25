# Test audit

The answer to "my tests are not real tests". Every test gets a class, the class gets evidence, and the proposal is one action per test. Say what each class means in plain words the first time it appears.

## 1. Gather evidence, say nothing yet

1. `DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y`, then `uv run repowise health --format json` filtered to the target directory. The advisory markers: `assertion_free_test` (runs code, checks nothing), `mock_saturated_test` (mostly mock setup), `large_assertion_block`, `duplicated_assertion_block`.
2. Coverage, if present: `uv run repowise coverage status`. Missing: `uv run pytest --cov --cov-report=lcov:coverage.lcov`, then `uv run repowise coverage add coverage.lcov`.
3. Mutation, on request or when the directory finishes in minutes: `uv run mutmut run "<package>.<module>*"` for each module the tests cover (mutmut 3 selects by mutant name, not by path), then `uv run mutmut results` for the survivors and `uv run mutmut show <mutant name>` for what each one changed. Survivors name the code no test constrains.
4. Read every test file in the directory in full, and the module each one imports.

## 2. Classify

One class per test function, with the line that proves it:

| Class | What it is | Evidence |
|---|---|---|
| **Behavioural** | Drives the public interface with a real or in-memory adapter and checks an outcome the spec cares about. | Keep. |
| **Tautological** | The expected value is computed the way the code computes it, or the test re-implements the function. | Quote the expression. A mutation survivor here is proof. |
| **Instruction-shaped** | A body that is `pass`, a comment, `assert True`, or a TODO. | Repowise `assertion_free_test`, or the body. |
| **Mock-only** | Every collaborator mocked; the assertion is that a mock was called. | Repowise `mock_saturated_test`, or the count of mocks against assertions. |
| **Trivial** | Tests a one-line mapping or a getter that mirrors the code. | The function under test. |
| **Live-model** | Calls a real model or a paid API from a unit test. | The import or the network call; belongs in `tests/evals/` with the `eval` marker. |
| **Weakened** | History shows an assertion loosened or a skip added without an override recorded. | `git log -p` on the file. |

## 3. Propose

A table, one row per test: file, test, class, evidence, action. Actions are exactly:

- **keep**
- **delete**, with the reason; trivial and tautological tests cost more than they catch
- **rewrite at <seam>**: name the seam, the in-memory adapter, and where the expected value will come from (spec line, fixture, worked example)
- **move to evals** for live-model tests
- **investigate** when history suggests weakening; write out the question for the user

Then the summary: counts per class, the modules with no behavioural test at all, and the mutation survivor rate where measured.

## 4. Act, one at a time

Nothing is deleted or rewritten without the user's word per row. Rewrites go through Matt Pocock's `tdd`: red first, expected value from outside the code, then green. Deletions are one commit named for the class they remove. Finish with `uv run pytest -m "not eval"` in full and `uv run python scripts/repowise_gate.py`, and show both.
