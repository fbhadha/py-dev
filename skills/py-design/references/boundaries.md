# Boundaries: calls out, data in, errors, config, logs

Where most production Python goes wrong is at the edges: a call with no timeout, a dict that travels three layers, an exception swallowed in an adapter. These rules decide what an adapter, an entrypoint and a port look like. Open this file when a ticket's plan touches an adapter, an entrypoint or a port, and when reviewing one.

## Calls out

- **Every call out has a timeout.** `requests` has none by default and will wait forever; pass one. `httpx` defaults to five seconds; set it on purpose, per client, in settings.
- **Retry only what can succeed on retry**: timeouts, connection resets, 429 and 5xx. Never a 4xx validation error. Exponential backoff with jitter, a cap on attempts, and `Retry-After` honoured when the server sends it.
- **Retry only what is safe to repeat**: reads, idempotent writes, or writes carrying an idempotency key. A retried non-idempotent write is a duplicate charge, a duplicate row, a duplicate email.
- **The adapter translates errors.** It catches the library's exceptions and raises the port's (`SourceUnavailable`, `RecordRejected`) with `raise ... from err`, so the application never imports `httpx` or `sqlalchemy` and the cause is kept.
- **Pagination, batching and rate limits live inside the adapter.** The application sees an iterable of domain records and nothing about pages.

## Data in

- **Parse once, at the edge, into a named type.** Untrusted outside data (an API response, a file, a form) becomes a Pydantic model, which validates and reports what was wrong. Values inside the domain are frozen dataclasses (`@dataclass(frozen=True, slots=True)`). `TypedDict` only describes a dict you pass through untouched.
- **Bad input is rejected or quarantined, with a count**, never coerced into something plausible. The run's summary says how many.
- **Identifiers get their own type**: `OrderId = NewType("OrderId", str)`, so an order id cannot be passed where a customer id belongs.
- **Money is `Decimal`**, never `float`. **Time is a timezone-aware `datetime` in UTC** inside the code; convert at the edges, and name the timezone a person sees.

## Errors

- Each package has a small hierarchy: one base (`class OrdersError(Exception)`) and the few specific errors callers act on differently. A public function's docstring says what it raises when that is not obvious.
- Catch an error where you can do something about it; let the rest reach the entrypoint, which logs it once with context and exits non-zero (a CLI) or answers with the right status (an API).
- Never `except Exception: pass`, never a bare `except:`, never `return None` to mean "it failed". ruff catches the blind forms; review catches the rest.

## Configuration

- One `pydantic-settings` class, read once at the entrypoint, so a missing variable fails before any work starts and names itself. Pass values down; never import the settings object from a domain or application module.
- Every key is in `.env.example` with a comment and no value. Secrets are typed `SecretStr`, so they do not print.

## Logs and run evidence

- `logger = logging.getLogger(__name__)` in each module; logging is configured once, at the entrypoint. Never `print` outside a CLI's output.
- Log events with the ids and counts a person needs to find the problem, not prose. Never a secret, a token or personal data.
- A run ends with one summary line: what came in, what went out, what was rejected, how long it took. A person can tell whether it worked from that line alone.

## Async

- One event loop, started at the entrypoint with `asyncio.run`. No blocking call inside async code: use the async client, or `await asyncio.to_thread(...)` for the one call that has no async form.
- Concurrency is structured (`asyncio.TaskGroup`, Python 3.11 and later) and bounded (an `asyncio.Semaphore` sized in settings), so one slow call cannot fan out into a thousand.

## Contract tests: one suite per port, every adapter runs it

Two adapters justify a seam (`SKILL.md` rule 4). The in-memory adapter is only worth trusting in unit tests if it behaves like the real one, so every port has one contract suite and every adapter runs it: the in-memory one in the unit tier, the real one in the integration tier.

```python
# tests/contract/sink_contract.py
class SinkContract:
    """Every Sink passes these. Subclass it and provide a `sink` fixture."""

    def test_write_returns_the_count(self, sink: Sink) -> None:
        assert sink.write([ORDER_1, ORDER_2]) == 2

    def test_writing_twice_keeps_one_copy(self, sink: Sink) -> None:
        sink.write([ORDER_1])
        sink.write([ORDER_1])
        assert sink.count() == 1


# tests/unit/test_memory_sink.py
class TestInMemorySink(SinkContract):
    @pytest.fixture
    def sink(self) -> Sink:
        return InMemorySink()


# tests/integration/test_sqlite_sink.py
class TestSqliteSink(SinkContract):
    @pytest.fixture
    def sink(self, tmp_path: Path) -> Sink:
        return SqliteSink(path=tmp_path / "orders.db")
```

When the real adapter learns a new behaviour (a conflict rule, an ordering guarantee), the contract gains the test first, and the in-memory adapter must pass it too. `pack-data-engineering`'s example package does exactly this.
