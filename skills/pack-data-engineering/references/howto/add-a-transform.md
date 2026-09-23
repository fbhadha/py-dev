# How to add a transform

Mirrors `src/{{PACKAGE}}/examples/orders/transforms.py` and its test, `tests/unit/examples/test_orders_transforms.py`, which compile and pass. When this file and the example disagree, the example is right and this file is wrong; fix the file.

## When this is the right shape

The request is a rule over records you already have: keep the latest update per key, convert an amount, drop cancelled orders, derive a field from other fields. It stays inside the domain layer: one pure function, and one line in the application function that calls it. In the repo it lives under `src/{{PACKAGE}}/domain` (in `domain.py` while the domain is small, `domain/transforms.py` once it is a package), so the import contract that keeps I/O out of the domain covers it; the example keeps it in its own `transforms.py` only because the example is one small package. If the rule needs data you do not have in hand (a lookup, an exchange rate from an API), stop: the data comes through a port and an adapter first, and that is a source or a new shape.

## Files you will create

| File | Layer | What goes in it |
|---|---|---|
| `src/{{PACKAGE}}/domain/transforms.py` (or `domain.py` while it is small) | domain | one function: records in, records out, fully typed |
| `tests/unit/test_<rule>.py` | tests | the rule on a handful of literal records |

## Steps

1. **Write the test first**, with at most five or six literal records and the expected output written by hand from the spec: the exact records, in the exact order. Add a test that the output does not depend on the input's order, and one for no records at all.
2. **Run it and watch it fail**: the function does not exist.
3. **Write the function**: `def <rule>(records: Iterable[Order]) -> list[Order]`. No I/O, no clock, no randomness. A rule that needs the current time takes it as a parameter (`now: datetime`) from the application, which gets it from the entrypoint. Records are frozen: build new ones with `dataclasses.replace`, never mutate.
4. **Make the output order deterministic**: sort by a stated key, so a re-run of the same input writes the same rows in the same order.
5. **Call it** from the application function, between reading and writing, and add a line to that function's unit test that proves the rule runs in the pipeline.
6. `uv run pytest tests/unit/test_<rule>.py`, then `uv run pre-commit run --all-files` and `uv run pytest -m "not eval"`.
7. Add the rule's name to `CONTEXT.md` if the business has a word for it.

## What usually goes wrong

- `datetime.now()` inside the transform: the same input gives different output tomorrow. Pass the time in.
- The expected value computed by calling the function, or by re-implementing it in the test. Write it out by hand.
- A `DataFrame` as the parameter or the return in the domain. Frames stay inside an adapter; the domain works on records (the pack's import-linter contract refuses the import).
- Mutating the input list or a record in place.
- A transform that quietly drops records it does not understand. Make it a `Rejected`, or raise, and say which in the spec.
