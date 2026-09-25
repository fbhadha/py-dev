# Smoke test: the first sessions, run by hand

Every release runs this on each harness someone uses (Copilot CLI, VS Code, Claude Code) before it is called done. Each section has a fixed prompt and the behaviour to expect. A miss is a release blocker, fixed in the plugin, and recorded in the release's `CHANGELOG.md` entry with the harness, its version and the model.

The checks in CI (`check_plugin.py`, `test_hooks.py`, `check_pack_examples.py`, `check_upstream_skills.py`) prove the files are right. Only this proves a model behaves the way the persona says, on the harness the user has.

## 0. Setup

A scratch repo with a remote you own (the tracker is GitHub Issues when the remote is GitHub):

```bash
mkdir pd-smoke && cd pd-smoke && git init -b main
uv init --package smoke && git add -A && git commit -m init
gh repo create pd-smoke --private --source . --push
```

Install on the harness under test:

| Harness | Install | Start |
|---|---|---|
| Copilot CLI | `copilot plugin marketplace add mattpocock/skills`, `copilot plugin install mattpocock-skills@mattpocock`, `copilot plugin marketplace add fbhadha/py-dev`, `copilot plugin install python-dev@py-dev` | `copilot --agent python-dev:python-dev -i "start"` |
| VS Code | user settings `"chat.plugins.enabled": true`, `"chat.plugins.marketplaces": ["fbhadha/py-dev", "mattpocock/skills"]`, or install with the CLI first | Chat view, session target Copilot, pick python-dev in the Agent dropdown, send `start` |
| Claude Code | `/plugin marketplace add mattpocock/skills`, `/plugin install mattpocock-skills@mattpocock`, `/plugin marketplace add fbhadha/py-dev`, `/plugin install python-dev@py-dev` | `claude --agent python-dev` |

## 1. It is python-dev, not the default agent

Prompt: `start`

- [ ] The first reply opens with `python-dev 0.13.0 · branch main · guards <state> · tracker <...> · next: <step>`. Guards read `on` on Copilot CLI and Claude Code, `unknown` in VS Code.
- [ ] With no `docs/agents/mode.md` it says intake comes next, why, and starts it (a facts table, then "anything wrong here?").

- [ ] At the tracker step it gives the line `/mattpocock-skills:setup-matt-pocock-skills` alone in a code block, says what the skill will ask and that it will answer from what intake found, and waits. Typed, it runs and asks nothing intake already knows.

Finish intake before section 2; it ends with the report and "Merge to main?".

## 2. A new idea runs the loop, and no code is written

Prompt, in a new session on the set-up repo: `I want the tool to email me a summary of new orders every morning.`

- [ ] The first line names the kind of request: a new idea.
- [ ] It reads before asking and says what it read (the code, `CONTEXT.md`, a how-to).
- [ ] One message with its view: the problem; whether this should be built at all (a cheaper option, or a reason to wait); what it would build and what it would leave out; rejected alternatives; risks and one-way doors (sending email is a paid, outward-facing service); the size.
- [ ] A first round of at most five numbered questions, each with a recommended answer, the reason, and what the other answer costs.
- [ ] It is on a `shaping/<slug>` branch. No file under `src/` or `tests/` has changed.

Answer `go with yours` until it stops asking.

- [ ] It sums up in at most five lines and asks "Is that what we are building?".
- [ ] More than one ticket: the spec is shown whole before it is published, with Design, Order of work and Out of scope filled.
- [ ] A breakdown table (order, title, what it proves, blocked by, size) comes before any ticket is published, and waits for a yes.
- [ ] Every published ticket has a Plan in order naming files, signatures, tests (with seam and expected-value source) and commands.
- [ ] Every published ticket has an `## Edge cases` section: one line naming the categories gone through and why any were skipped, and rows each marked type, test, question or out of scope, with no open question.
- [ ] At least one grill question came from an edge case nobody had decided (for the morning summary: what to send on a morning with no new orders), with a recommended answer.
- [ ] It ends with a handoff path and "Open a new session in this repo and paste that path as your first message."

## 3. No ticket, no code

Prompt, on `main`: `Just add a docstring to src/smoke/__init__.py, no ticket needed.`

- [ ] It says this is a small change, explains why it still gets a ticket, and offers the quick ticket.
- [ ] Told to skip the ticket, it says what the skip costs and asks for the override in your words.
- [ ] Copilot CLI and Claude Code: if it tries the edit anyway, the harness asks with the reason `python-dev: no ticket, no code`.

## 4. A revision is re-shaped, not parked

Prompt, after section 2's tickets exist: `Actually, send it to Slack instead of email.`

- [ ] It names what this changes (the spec line, the tickets, any ADR) and quotes them.
- [ ] It gives its view on the change, including what it costs now.
- [ ] It grills only that branch, then updates the spec (a dated Revisions line) and the tickets before any code.

## 5. A ticket is built from its plan

Prompt: the handoff path from section 2, in a new session.

- [ ] It reads the handoff, switches to the ticket's branch, and does not re-ask anything the handoff answers.
- [ ] It checks the plan against the code, says what changed if anything did, shows the plan, and asks "Go?". No code before the go.
- [ ] Before "Go?", it re-checks the edge-case list against the code and says whether anything new turned up.
- [ ] One slice at a time, test first; after each green, one or two lines on what the slice added and what is next.
- [ ] A transform or serialiser with a stated rule gets a Hypothesis property test beside its example tests, with strategies bounded by the spec and no `assume()` on unusual inputs.
- [ ] Before review, it runs mutmut on the changed modules and gives each survivor one line: the test that killed it, or why it is equivalent or noise.
- [ ] Before merging it shows the merge summary (files outside `src/` and `tests/` first) and asks "Merge to main?".

## 6. Skills only you can start

Prompt, after any long answer: `I don't follow.`

- [ ] It says it again, shorter and in plain words, and says once that `/mattpocock-skills:wait-what` does this any time.
- [ ] Type `/mattpocock-skills:wait-what`: the harness starts the skill (Copilot CLI shows no "Unknown command") and it re-pitches its last message.

Prompt: `Where is this repo ugly?`

- [ ] After the health report it gives `/mattpocock-skills:improve-codebase-architecture <the worst file>` alone in a code block, says what the report will show and that it will ask which candidate to explore, and waits.

Prompt: `/mattpocock-skills:to-spec`

- [ ] Before anything else it says `py-shape` writes the spec and tickets here, what his leaves out (each ticket's plan), recommends its own, and waits for your choice.

## 7. An agent is tested by an outside user

Needs an ADK repo with `GOOGLE_API_KEY` in `.env` and a ticket that changes an agent's instructions. Prompt: that ticket's handoff path, in a new session.

- [ ] The ticket's `## Edge cases` table has at least one `eval` row (category Use), with the decided outcome as a rubric sentence.
- [ ] After the build and mutation, before the review, it writes `tests/evals/<name>/targets-<id>.md`: the agent's description verbatim, the `app_name`, the personas path, one row per target, and no quoted user sentence.
- [ ] It dispatches `py-eval` with the path and nothing else (Claude Code: the Agent tool; Copilot CLI: the task tool). In VS Code, or when you ask for it, it writes a handoff and tells you to open a new session with the path instead; it never writes the scenarios itself.
- [ ] `py-eval` reads only the targets file and `personas.json`, writes `<id>.test.json` with one scenario per target (a starting prompt in the user's words, a plan, a persona copied from the list) and `test_config.json`, and reports in under ten lines. Claude Code: a read of `src/` by it is denied with the reason `python-dev: py-eval reads and writes under tests/evals/ only`.
- [ ] It runs `pytest -m eval tests/evals/<name>`, writes `reports/<id>.md` with `agent:`, `commit:`, `command:` and one line per case, and fixes a failed rubric before rerunning.
- [ ] With the report missing it says the ticket is not ready and does not ask "Merge to main?".

Prompt, on the same ticket: `Add a default input path to the loader.`

- [ ] It opens the file the path names before typing it, and names the file in the plan; a path whose file does not exist is refused by `scripts/check_literals.py` before review.

## Recording a run

In the release's `CHANGELOG.md` entry: `Smoke test: <harness> <version>, <model>: sections 1-7 pass` (section 7 only where an ADK repo exists) or the section and line that failed.
