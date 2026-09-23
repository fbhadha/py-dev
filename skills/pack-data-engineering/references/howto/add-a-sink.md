# How to add a sink

Mirrors `src/{{PACKAGE}}/examples/orders/adapters/sqlite_sink.py` and the contract every sink passes, `tests/integration/examples/test_orders_sinks.py`, which compile and pass. When this file and the example disagree, the example is right and this file is wrong; fix the file.

## When this is the right shape

The request is "also write the records to X": another database, a warehouse, a file format, an API. It stays inside two layers: one new module in `adapters/` satisfying the `OrderSink` port, and one line in the composition root. The sink takes the domain records as they are. If X needs the records reshaped, the reshaping is a transform or a new domain type, decided in shaping; a sink that normalises for itself is the shape going wrong.

## Files you will create

| File | Layer | What goes in it |
|---|---|---|
| `src/{{PACKAGE}}/adapters/<destination>_sink.py` | adapters | a class satisfying `OrderSink`: `write` (upsert, newer wins, returns rows changed), `get`, `count` |
| `tests/integration/test_<destination>_sink.py` | tests | one class that subclasses the sink contract and builds the sink against a local substitute |

## Steps

1. **Run the contract against the new sink first.** Add `class Test<Destination>OrderSink(OrderSinkContract)` with a `sink` fixture that builds your adapter against a local substitute (DuckDB or SQLite in `tmp_path`, a container, the destination's own emulator). Every contract test fails: the class does not exist yet.
2. **Create the adapter from `sqlite_sink.py`.** Rename, do not restructure. The rules the contract checks:
   - **Upsert on the key, newer wins.** A re-run of the same batch changes nothing; a late, older update never replaces a newer one. The write returns the rows it actually changed, so the run's summary shows a re-run as "written 0".
   - **One transaction per write.** A failure leaves the destination as it was, so the run can simply be re-run.
   - **Exact types.** Money in a decimal or numeric column (or text), never a float; times in UTC with microseconds; the schema declared in the adapter, never inferred from the first rows.
3. **Run the contract until every test is green.** A behaviour the destination needs that the contract does not test yet goes into the contract first, and the in-memory sink must pass it too.
4. **Register it** in the composition root, behind a setting.
5. `uv run pytest tests/integration/test_<destination>_sink.py`, then `uv run pre-commit run --all-files` and `uv run pytest -m "not eval"`.

## What usually goes wrong

- An append with no key: every re-run duplicates every row.
- A truncate-and-reload inside a loop, or a delete with no transaction around it: a crash halfway leaves the table empty.
- A commit per row: correct, and a hundred times slower. Batch in one transaction.
- A test only this sink runs. If it is a rule of sinks, it belongs in the contract; if it is a detail of this destination (a column type, a partition), it is fine as its own test beside the contract class.
- Credentials in the adapter. They come from settings, which read `.env`; `.env.example` lists the key.
