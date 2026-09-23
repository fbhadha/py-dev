# How to add a pipeline

Mirrors `src/{{PACKAGE}}/examples/orders/application.py` and `src/{{PACKAGE}}/examples/orders/entrypoints/cli.py`, with their tests `tests/unit/examples/test_orders_run.py` and `tests/integration/examples/test_orders_cli.py`, which compile and pass. When this file and the example disagree, the example is right and this file is wrong; fix the file.

## When this is the right shape

The request is "load dataset X from A into B, on a schedule". It uses sources, transforms and sinks that exist or are added first by their own how-tos, and adds two things: an application function that runs one load, and an entrypoint that wires the real adapters and is what a scheduler calls. If the dataset needs a new record type, a new rule or a new adapter, those come first, each as its own ticket.

## Files you will create

| File | Layer | What goes in it |
|---|---|---|
| `src/{{PACKAGE}}/application.py` (`application/<dataset>.py` once there are several) | application | `run(*, name, source, sink, cursors) -> RunReport`: read since the cursor, transform, write, then move the cursor |
| `src/{{PACKAGE}}/entrypoints/<dataset>.py` | entrypoints | the composition root: settings or arguments in, real adapters built, `run` called, an exit code out |
| `tests/unit/test_<dataset>_run.py` | tests | the run with in-memory adapters |
| `tests/integration/test_<dataset>_cli.py` | tests | the entrypoint end to end, twice, against local files or a local database |

## Steps

1. **Write the run's unit tests first**, with in-memory adapters, one per behaviour: a first run loads everything and sets the cursor; a second run reads only what changed; the same rows run again change nothing; rejected rows are counted while good rows still load; a failed write leaves the cursor where it was. Expected reports are written out by hand.
2. **Write `run`**: load the cursor, read, split good records from rejected ones, transform, write, and only then save the cursor (at-least-once in, stored once, because the sink upserts). Log each rejected row's source, line and reason (never the row's contents) and end with one summary line.
3. **Write the entrypoint**: parse arguments or read the settings class once, build the real adapters, call `run`, and turn the report into an exit code: 0 when everything loaded, 1 when rows were rejected (a person must look), 2 when the run could not happen (log the exception once).
4. **Write the integration test through the entrypoint**: run it twice on the same input and assert the destination holds each record once and the second summary says "written 0".
5. **Schedule it.** A cron line, a CI schedule, or an orchestrator task that calls the entrypoint and nothing else. An Airflow DAG file, a Dagster asset or a Prefect flow is an entrypoint: it wires and calls, it holds no business logic, and it is tested by the integration test above.
6. **Backfill** is a re-run with an earlier cursor: set the load's cursor earlier (or remove it) in the cursor store, with the user's yes, and run the entrypoint. The upserting sink makes the re-read rows harmless. Say how in the pipeline's line in `README.md`.
7. `uv run pytest -m "not eval"` and `uv run pre-commit run --all-files`; add the dataset's name to `CONTEXT.md`.

## What usually goes wrong

- The cursor saved before the write: a crash in between loses those rows for ever.
- The cursor kept in a global, a file in the repo, or a column the sink owns. It belongs to the cursor store, one name per load.
- Logic in the DAG or asset file: untestable without the orchestrator, and parsed on every scheduler loop.
- A pipeline that cannot be re-run safely. If running it twice is harmful, a sink is wrong; fix the sink first.
- A summary that says "done" with no counts. A person must be able to tell from one line whether it worked.
