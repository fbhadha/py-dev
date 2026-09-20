# Canonical examples

Three repos to cite by path when explaining a recommendation, so a reader can go and look at the real thing. Each demonstrates one idea; do not cite one for the others' lesson.

## `psf/requests`: what depth looks like

The public surface is eight functions in `src/requests/api.py` (`request`, `get`, `post`, `put`, `patch`, `delete`, `head`, `options`). Behind them, about six thousand lines: `sessions.py` (connection reuse, redirects, cookies, auth), `adapters.py` (transport), `models.py` (request and response objects), `auth.py`, `cookies.py`. A caller learns one function; the implementation absorbs everything.

- Depth: `api.py` against `sessions.py`.
- A real seam with two adapters: `adapters.py` defines `BaseAdapter` and `HTTPAdapter`; a session mounts adapters by URL prefix, so a test can mount a fake.
- What to say: "callers learn `get()`; retries, pooling and cookies live behind it, which is why nobody outside `sessions.py` has to know about them."

## `cosmicpython/code`: what layering looks like

The reference implementation for *Architecture Patterns with Python* (Percival and Gregory). `src/allocation/`:

- `domain/model.py`, `domain/commands.py`, `domain/events.py`: entities, value objects and rules; imports nothing from the layers below.
- `service_layer/handlers.py`, `service_layer/messagebus.py`, `service_layer/unit_of_work.py`: use cases and the transaction boundary; depends on the domain and on abstract ports.
- `adapters/repository.py`, `adapters/orm.py`, `adapters/notifications.py`, `adapters/redis_eventpublisher.py`: one module per external concern, each satisfying an abstract port.
- `entrypoints/flask_app.py`, `entrypoints/redis_eventconsumer.py`: the outside world calling in.
- `bootstrap.py`: the one composition root, where real or fake adapters are wired.
- `tests/unit/`, `tests/integration/`, `tests/e2e/`: the three tiers, with `tests/unit/` needing no I/O.

What to say: "the domain never imports an adapter; the adapters are swapped in one place; that is why a unit test of allocation runs without a database."

## `dlt-hub/dlt`: the adapter, model, writer shape at scale

A production data-loading library shaped exactly like the worked example in `SKILL.md`, but with many sources and many destinations:

- `dlt/sources/`: one package per external system (the adapters in).
- `dlt/extract/source.py`, `dlt/extract/resource.py`, `dlt/extract/extract.py`: how a source yields items, including incremental state.
- `dlt/normalize/normalize.py` and `dlt/normalize/items_normalizers/`: the one place raw items become a typed schema. Every source flows through it; no source normalises for itself.
- `dlt/load/load.py`: the loader that takes normalised data to any destination.
- `dlt/common/destination/reference.py`, `client.py`, `capabilities.py`: the destination contract (the port), with each backend under `dlt/destinations/impl/` satisfying it.

What to say: "every source produces the same normalised shape and every destination consumes it; a new source or destination is one new package, not a change to the others. When you find each source writing to the table its own way, this is the counter-example to point at."

## How to cite

Name the repo, the path, and the lesson in one sentence, then stop. "See `src/requests/api.py`: eight functions over six thousand lines is what a deep module looks like." A reader who wants more will open the file; a reader who does not is not slowed down.
