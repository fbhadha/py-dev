# Python developer agent

The shared language for the Python developer agent designed in `docs/design/python-dev-agent.md`.

## Language

**Junior reader**:
The person the agent's output is judged against: can read Python but not write it fluently, has never seen the repo, and cannot ask the author anything. Success means they can understand and modify the code from the docs alone.
_Avoid_: junior dev, human reviewer, senior engineer (the bar is lower and stricter than a senior pick-up)

**Fresh-eyes test**:
The check for the junior reader bar: a brand-new agent session given only the repo's README and docs, no conversation history, is asked to add a small feature; the pass is zero questions back to the user.
_Avoid_: onboarding test, docs test

**Shape**:
A recurring kind of addition the repo already knows how to make (another source adapter, another agent tool, another writer), described by one how-to and backed by one working example. A ticket that matches a shape is built by template; one that matches no shape triggers a grilling session and produces a new shape.
_Avoid_: pattern (overloaded with GoF design patterns), template (the how-to is the template; the shape is the thing it describes)

**How-to**:
One of the repo's human-facing docs, `docs/howto/add-a-<thing>.md`, describing one shape as steps that mirror a real example package. Executed or compiled in CI so it cannot drift.
_Avoid_: guide, tutorial, playbook

**Craft core**:
The judgement layer that applies to every Python repo: design rules, testing rules, the baseline toolchain, the fault catalogue, and the canonical example repos. One skill, always available, never ecosystem-specific.
_Avoid_: persona, system prompt (those are where the core is pointed at from, not the core itself)

**Knowledge pack**:
A reference-only skill in the Agent Skills format, with a fixed shape (trigger dependencies, shapes it knows, canonical example repo, extra checks, fault list), covering one Python ecosystem such as ADK or data engineering. Selected at intake from the repo's dependencies; anyone can write one from the pack template.
_Avoid_: plugin (the harness-level bundle), module, library

**Persona**:
The short, always-loaded file that defines the agent: identity, guide voice, the two-tier pushback, the must-ask list, the checkpoints, and the pointers that say when to load each piece of knowledge. About a page. Holds no craft knowledge itself.
_Avoid_: system prompt (harness term), CLAUDE.md (one container it can live in, not the thing)

**Harness**:
The program that runs the model and its tools: Claude Code, GitHub Copilot, OpenAI Codex. The agent runs inside a harness; the harness decides how a persona is selected, how skills are invoked, and which hooks fire.
_Avoid_: platform, IDE, runtime

**Agent**:
The selectable thing we are building: a persona (system prompt), the tools it may use, the model, and the skills it can reach, running inside a harness. It has no memory beyond what is written in files.
_Avoid_: bot, assistant, copilot (a product name)

**Hook**:
A harness-native script that runs at a lifecycle point (before a tool call, after an edit, at session start, when the agent tries to stop) and can inject context or block the action. Best-effort and harness-specific; never the only enforcement of a rule.
_Avoid_: guardrail (that is the rule; the hook is one place it runs), trigger
