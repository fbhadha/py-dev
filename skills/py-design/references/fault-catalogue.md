# Fault catalogue

The faults LLM-written Python commits by default, each with its tell, the mechanism that catches it, and the fix. The tool named in the third column catches it mechanically; where the column says reviewer, nothing does, and the review's Craft axis (`agents/py-reviewer.md`) has to. Whole-repo signals (duplication, dead code, cohesion, I/O in loops, test hygiene) come from Repowise; line-level ones from ruff, pylint, mypy, import-linter. When a fault has a tool, do not spend review words on it.

## Shape

| Fault | Tell | Caught by | Fix |
|---|---|---|---|
| The giant module | One file keeps growing because it is the one already open. | pylint `too-many-lines` (400 for modules, 150 for tests). | Split by shape: one module per domain concept, entry points at the package root. |
| The grab bag | `utils/`, `helpers/`, `common/`, `misc/`, or a file named after a category instead of a concept. | ruff `TID251` banned imports; import-linter `forbidden` contract. | Move each function to the concept it serves. |
| The shallow module | A class or function that only forwards to the next one down. Delete it and the callers change nothing. | Reviewer: deletion test; Repowise `dead-code` when nothing calls it. | Inline it. |
| The hypothetical seam | A Protocol or base class with exactly one implementation. | Reviewer. | Inline until a second adapter exists. |
| Import-time side effects | A client, a file read, or `logging.basicConfig` at module level. | Reviewer; import-linter catches the layering half. | Construct in the entrypoint; configure at the edge. |
| Circular imports, imports inside functions to dodge them | A symptom of no layering. | import-linter (`lint-imports`). | Introduce the port; move the shared type down to `domain`. |
| Inheritance for reuse | A `Base*` with concrete behaviour and subclasses overriding half of it. | Reviewer: Refused Bequest. | Composition: inject the collaborator. |
| The config dict, the `**kwargs` passthrough, the boolean flag | Interfaces that avoid deciding what they take. | ruff `FBT` for flags; reviewer for the rest. | A typed parameter object; keyword-only arguments; two functions instead of a flag. |

## Content

| Fault | Tell | Caught by | Fix |
|---|---|---|---|
| Instructions to a model in the code | `# TODO: implement error handling`, `# Make sure to`, `# Step 1:`, `# You are`, prompt text pasted as comments, a docstring that starts "This function". | ruff `TD002`/`TD003`/`FIX002` (TODOs), `D401` ("This function" docstrings), `ERA001` (commented-out code). | Delete, or say the why. ADK prompts live in `prompts.py` or a loaded file, never inline in logic. |
| Tutorial comments | `i += 1  # increment i` | Reviewer. | Delete. A comment states what the code cannot. |
| Swallowed exceptions | `except Exception: pass`, `except: return None`, a broad except inside an ADK tool. | ruff `BLE001`, `S110`, `E722`; Repowise `error_handling`. | Catch the specific type you can handle; let the rest propagate; exceptions are part of the interface. |
| Symptom-level fixes | A null check where the value must never be null; a retry where the input was wrong. | Reviewer. | Fix the invariant; the check becomes unnecessary. |
| Mutable defaults, `assert` as validation, `print` as logging, string-built SQL, secrets in code | | ruff `B006`, `B008`, `S101` (src only), `T201`, `S608`, `S105`/`S106`; `detect-secrets`. | `None` sentinel; raise `ValueError`; `logging`; parameters; `pydantic-settings` plus `.env.example`. |
| Undefined names, unused imports, deprecated APIs, invented methods | | ruff `F`; mypy strict. | Read the source of the library before relying on a signature. |
| Duplication under a new name | A second `normalize_date` because the first was not in context. | Reviewer: search `CONTEXT.md` terms before writing a function; Repowise `dry_violation` in `repowise health` and in the CI change gate. | Reuse; if the two differ, name the difference. |
| Excessive complexity | Nested conditionals, 80-line functions, six parameters. | ruff `C901`, `PLR0912`, `PLR0913`, `PLR0915`; Repowise `nested_complexity`, `brain_method`, `god_class`, `low_cohesion`. | Extract until each function reads as one sentence. |
| `Any` and `dict[str, Any]` as domain objects | | mypy strict; reviewer: Primitive Obsession. | A named frozen dataclass or model from `CONTEXT.md`. |

## Tests

| Fault | Tell | Caught by | Fix |
|---|---|---|---|
| The tautological test | The expected value is computed the way the code computes it. | Reviewer; `mutmut` on the changed modules before review. | A literal from the spec or a worked example. |
| The instruction-shaped test | `def test_x(): pass  # TODO`, a body that is a comment, `assert True`. | Repowise `assertion_free_test` (advisory marker in `repowise health --format json`). | Write the behaviour or delete the test. |
| The mock-only test | Every collaborator mocked; the test proves the mocks were called. | Reviewer; Repowise `mock_saturated_test`. | Test through the public interface with a real or in-memory adapter. |
| The weakened test | A loosened assertion, a deleted test, a new `skip`, a hard-coded return for the known input. | `scripts/check_test_diff.py` in CI and before review; reviewer in a fresh context; `CODEOWNERS` on `tests/`. | Tests are read-only from red to green. An intended deletion needs the explicit override and a reason in the commit. |
| The trivial test | A test of a one-line mapping that mirrors the code. | Reviewer. | Delete. Test at the seam. |
| Horizontal slicing | All tests written, then all code. | Reviewer, from the commit history. | One test, one implementation, repeat. |
| The live-model unit test | A unit test that calls the real model. | Reviewer; `tests/evals/` convention. | Fake the model in unit tests; live runs are evals, run on demand. |
| The happy-path-only test | Every test uses a typical valid input; none sits on a boundary, a tie or an error path. | `mutmut` survivors at comparisons and handlers, before review; reviewer against the ticket's `## Edge cases` table. | List the edge cases by `references/edge-cases.md`; one test per decided edge case. |
| The incorrect assertion | An edge-case test whose expected value no spec line, worked example or user answer supports. | Reviewer: every `test` row in the ticket names a source. | Ask; the answer is the expected value. |
| Assume misuse | `assume()` that drops duplicates, empties, equal values or boundaries from a property test. | Reviewer. | Build valid inputs with a strategy; keep the unusual ones. |
| The wrong strategy range | `st.integers()` or `st.text()` where the spec names a range or an alphabet. | Reviewer. | Bound by the spec; `@example` the boundaries. |
| The flaky oracle | A property whose expected value comes from the code under test, or a round trip with no literal example beside it. | Reviewer; `mutmut` survivors. | A reference model in the test, and one literal example. |
| The untested handler | An `except` branch or error return that no test runs. | `diff-cover` on the lines a change added; `mutmut` survivors inside the handler for lines that were already there; reviewer. | A test where the in-memory adapter raises the port's error. |

## Process

| Fault | Tell | Caught by | Fix |
|---|---|---|---|
| Wrong project diagnosis | Proposals that contradict `CONTEXT.md`, an ADR, or the how-to. | Session-start read list; reviewer. | Read first. |
| Scope creep | The diff does more than the ticket. | The shape checkpoint; `code-review` Spec axis. | Park it as `later`. |
| Inaccurate self-reporting | "Verified" with no command output beside it. | The persona rule; the PR body's before-and-after evidence. | Show the output. |
| Constraint violation over time | A rule in prose that stopped being followed. | Move it into a gate. | Mechanical rules live in checks, not in prose. |
