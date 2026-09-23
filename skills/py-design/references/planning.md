# Planning: what to build first, and in what order

How a spec becomes an ordered set of tickets, and a ticket becomes an ordered plan. `py-shape` cuts the breakdown and writes each ticket's plan from these rules; `py-build` checks the plan against them before the first line. When you show an order, say which rule set it.

## Between tickets

1. **Walking skeleton first.** The first ticket runs end to end through every layer the feature needs (entrypoint, application, domain, one adapter) and does the least that proves the path: one record, one field, the in-memory adapter where the real one is slow to build. Every later ticket thickens a path that already runs, so integration problems surface in week one, not at the end.
2. **Riskiest unknown next.** The part most likely to change the design (an API you have not called, a data shape you have not seen, a volume or latency limit) goes second, while changing course is cheap. If talking cannot settle it, it was a prototype during shaping, not a ticket.
3. **Prefactor before the feature.** Make the change easy, then make the easy change. A ticket that needs existing code reshaped gets a prefactor ticket before it: no behaviour change, the suite green before and after, reviewed on its own.
4. **Expand, migrate, contract** for anything with callers or stored data: add the new form beside the old; move callers or rows over one ticket at a time, each green; delete the old form last, in a ticket blocked by every migrate ticket. Nothing is ever half-moved at a merge.
5. **Vertical slices, never horizontal.** No "all the models" ticket, no "the tests" ticket, no "wire everything up" ticket. Each ticket is a behaviour a user or a test can see, cutting through the layers it needs.
6. **One session per ticket.** Bigger than one session: split by behaviour (happy path, then each failure, then each variant), not by layer.
7. **Blocking edges are real dependencies only.** Two tickets that could land in either order get no edge, so the frontier stays wide and a stuck ticket blocks nothing it does not have to.

## Inside a ticket

The order a slice is written in, outside-in, one test at a time:

1. **The test at the use-case seam, red.** The behaviour from the outside: the application function or entrypoint the acceptance criterion names, with in-memory adapters.
2. **The domain types it needs.** The frozen dataclass or Pydantic model, named from `CONTEXT.md`, with its invariants. Types before logic.
3. **The rule.** The domain function that makes the test pass; pure, no I/O.
4. **The application function** that wires the rule to the ports, still on in-memory adapters.
5. **The real adapter**, in the integration tier: against a recorded response, a local file or a local database (DuckDB, SQLite, a container), never the live service from a unit test.
6. **Wiring** in the composition root, and the one integration test that runs the real path end to end.
7. **Docs** the change touched: the how-to, the `CONTEXT.md` term, the ADR.

The plan lists the behaviours in this order; the tests are still written one at a time, red then green. A plan is a sequence of slices, not a stack of tests written up front.

## Doors

A **two-way door** (a private function's name, a module's internal layout, a library you could swap in an afternoon) gets your recommendation and a move on. A **one-way door** (a public interface, a stored schema, data deleted or migrated, a paid service, a dependency that spreads through the code, anything other teams will call) is named in the spec, decided by the user in words, recorded as an ADR, and gets its own ticket so it can be reviewed alone.

## What every step of a plan names

- the file, checked to exist, or marked new, and its layer
- the function or class, with its full signature and the exceptions it raises
- the test, by name, with its seam and where its expected value comes from
- the command that proves the step

A step that cannot name these is not planned yet; go back to the code or the grill.

## Sizing

- **S**: one slice, one or two files, under an hour of agent time.
- **M**: two to four slices, one layer's worth of new code plus wiring.
- **L**: the most one session holds: five or six slices. Anything bigger is two tickets.

Say the size when you show the breakdown; a user who sees six L tickets knows the cost before the first line.
