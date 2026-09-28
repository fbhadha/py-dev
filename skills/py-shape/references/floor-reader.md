# Written for the floor reader

**Floor reader**: The reader everything the agent writes for another session to execute is judged against (a ticket, a handoff, the prompt a dispatched agent gets): a small model in a fresh session that can drive its tools, follows one instruction at a time, and infers nothing that is not written down.

These rules apply to everything written for it: a ticket, a handoff, the prompt a dispatched agent gets.

## The six rules

1. One step is one action, with one command or one file.
   - Not this: "Add the parser and its test, then run the checks."
   - This: "1. Write `tests/unit/test_parser.py::test_parses_header`."
     "2. Run `uv run pytest tests/unit/test_parser.py`."
2. Each condition gets its own line: "If X: do Y".
   - Not this: "Run the migration unless the table exists, in which case skip it."
   - This: "If the table `orders` exists: skip step 3."
     "If it does not: run step 3."
3. Every literal is written out: path, signature, command, expected value.
   - Not this: "Add the timeout to the settings module."
   - This: "In `src/shop/config.py`, add `http_timeout_s: float = 10.0` to `Settings`."
4. A pointer names the path and the heading, and says what to take from it.
   - Not this: "See `edge-cases.md`."
   - This: "Open `py-design`'s `references/edge-cases.md`, heading `## The categories`. Take the category names from its table."
5. The artifact says when to stop, what to report, and that a failed step means stop, never improvise.
   - Not this: "Make sure the checks pass."
   - This: "3. Run `uv run pytest -m "not eval"`."
     "If step 3 fails: stop."
     "Report the command and the last 20 lines of its output."
     "Change nothing else."
6. A word outside `CONTEXT.md` carries its definition beside it.
   - Not this: "Build it at the seam."
   - This: "Build it at the seam (the public function the test calls)."
