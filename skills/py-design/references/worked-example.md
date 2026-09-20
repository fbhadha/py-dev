# The worked shape: adapter, model, writer

Most data projects are this shape. Several external systems in, one common record in the middle, one writer out.

```python
# ports.py
from collections.abc import Iterable
from typing import Protocol
from .domain import Record

class Source(Protocol):
    def records(self) -> Iterable[Record]: ...

class Sink(Protocol):
    def write(self, records: Iterable[Record]) -> int: ...

# domain.py
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class Record:
    key: str
    title: str
    owner: str
    updated_at: datetime

# adapters/jira.py
class JiraSource:
    def __init__(self, *, client: JiraClient, project: str) -> None: ...
    def records(self) -> Iterable[Record]:
        for issue in self._client.search(self._project):      # raw dict from the API
            yield Record(key=issue["key"], title=issue["fields"]["summary"], ...)  # parsed here, once

# adapters/memory.py
class InMemorySource:                       # the second adapter that makes the seam real
    def __init__(self, records: list[Record]) -> None: ...
    def records(self) -> Iterable[Record]: return iter(self._records)

# application.py
def sync(*, sources: Iterable[Source], sink: Sink) -> int:
    return sink.write(r for s in sources for r in s.records())

# entrypoints/cli.py            the one composition root
settings = Settings()           # pydantic-settings; fails here if a variable is missing
sync(sources=[JiraSource(client=..., project=settings.jira_project)], sink=BigQuerySink(...))
```

What makes it right: the API dict dies inside `JiraSource`; `Record` is the only thing that crosses a seam; `sync` is testable with `InMemorySource` and a fake `Sink` and never touches a network; adding ServiceNow is one adapter file and one line in the entrypoint, nothing else. The deep module is `sync` plus the writer: one call, and batching, retries, idempotency and schema evolution live behind it.

