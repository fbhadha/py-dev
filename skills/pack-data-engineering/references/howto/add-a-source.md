# How to add a source

Mirrors `src/{{PACKAGE}}/examples/orders/adapters/csv_source.py` and its test, `tests/integration/examples/test_orders_csv_source.py`, which compile and pass. When this file and the example disagree, the example is right and this file is wrong; fix the file.

## When this is the right shape

The request is "get records from another system": another API, another export, another database. It stays inside two layers: one new module in `adapters/`, and one line in the composition root. The records it yields are the same domain type every other source yields. If the new system needs a new field on the domain type, a new rule, or a change to a sink, stop: that is a new shape or a revision, and it goes back to shaping.

## Files you will create

| File | Layer | What goes in it |
|---|---|---|
| `src/{{PACKAGE}}/adapters/<system>_source.py` | adapters | a class satisfying the `OrderSource` port: `read(*, since) -> Iterator[Order | Rejected]` |
| `tests/integration/test_<system>_source.py` | tests | the source against a recorded response or a local file, never the live system |
| `tests/fixtures/<system>/` | tests | the recorded response, trimmed to the rows the tests need, no real personal data |

## Steps

1. **Record a sample** of what the system returns: five or six rows, including one bad row and one row with a time in another offset. Save it under `tests/fixtures/<system>/`. Scrub names, emails and ids.
2. **Write the test first**, from the sample, with the expected records written out by hand: each good row becomes the exact `Order` you expect (amounts as `Decimal`, times converted to UTC), each bad row becomes a `Rejected` with its line or key and the reason. A second test: `read(since=...)` yields only newer rows and still yields every bad row. A third: a missing file, column or credential raises `SourceError`.
3. **Run it and watch it fail** for the right reason: the module does not exist yet.
4. **Create the adapter from `csv_source.py`.** Rename, do not restructure. Parse each record here, once: strings stripped, money through `Decimal`, times through `_utc` (an unlabelled time is rejected, never assumed). Anything that fails becomes a `Rejected`; nothing is dropped, nothing is guessed.
5. **Push `since` down** when the system can filter (a query parameter, a `WHERE` clause) instead of reading everything and filtering in memory. Pagination, timeouts and retries live in this module (`py-design/references/boundaries.md`).
6. **Register it** in the composition root (`src/{{PACKAGE}}/entrypoints/`), behind a setting or a command-line option, with its own cursor name.
7. `uv run pytest tests/integration/test_<system>_source.py`, then `uv run pre-commit run --all-files` and `uv run pytest -m "not eval"`.
8. Add the system's name to `CONTEXT.md` if it introduced a word the repo did not have.

## What usually goes wrong

- A business rule inside the source: de-duplicating, converting currencies, choosing the latest update. Those are transforms, written once, for every source.
- A bad row skipped with `continue` or coerced with `errors="coerce"`. Every bad row is a `Rejected`, counted in the run's summary.
- A naive `datetime`, or a time assumed to be local. Only a time with an offset becomes an `Order`.
- `float` for money. `Decimal`, from the string the system sent.
- A call with no timeout, or a retry on a 4xx. See the boundaries reference.
- A test that calls the live system. That is not a test; record a sample.
