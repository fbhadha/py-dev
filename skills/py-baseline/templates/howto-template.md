# How to add a {{SHAPE}}

Mirrors `src/{{PACKAGE}}/examples/{{SHAPE}}/`, which compiles and has a test. When this file and the example disagree, the example is right and this file is wrong; fix the file.

## When this is the right shape

One paragraph: the request looks like this, and it stays inside these layers: {{LAYERS}}. If the work needs anything outside them, stop; it is a new shape and needs the interview.

## Files you will create

| File | Layer | What goes in it |
|---|---|---|
| `src/{{PACKAGE}}/adapters/<name>.py` | adapters | the class that talks to the outside system, satisfying the `{{PORT}}` Protocol |
| `src/{{PACKAGE}}/domain/<name>.py` | domain | the frozen dataclass or model, if the shape introduces a new concept |
| `tests/unit/test_<name>.py` | tests | the behaviour, through the public interface, with the in-memory adapter |

## Steps

1. Write the test first, at the seam named above. Expected values come from the spec or a worked example; never compute them the way the code will.
2. Run it and watch it fail for the right reason.
3. Create the adapter from the example. Rename, do not restructure.
4. Register it in the composition root (`src/{{PACKAGE}}/entrypoints/bootstrap.py`).
5. Run `uv run pre-commit run --all-files` and `uv run pytest`.
6. Add the new term to `CONTEXT.md` if it introduced one.

## What usually goes wrong

- A second implementation of something that already exists under another name. Search `CONTEXT.md` first.
- Normalising inside the adapter. Adapters fetch; the domain normalises.
- Testing through mocks of the collaborators instead of through the in-memory adapter.
