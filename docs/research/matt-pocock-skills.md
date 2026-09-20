# Research: Matt Pocock's skills, what they teach, and what a Python developer agent should take from them

Sources read in full: every `SKILL.md` and reference file in [mattpocock/skills](https://github.com/mattpocock/skills) (v1.2.3, 30+ skills across `engineering/`, `productivity/`, `misc/`, `in-progress/`), the repo's `CLAUDE.md`, `CONTEXT.md`, ADRs, `.agents/` authoring notes, `.out-of-scope/` decisions, the full `CHANGELOG.md`, and all 24 `docs/` pages (these are the source files for the published pages at `aihero.dev/skills-<name>`, which the network proxy blocked directly). Also read: his [AI Coding Dictionary](https://github.com/mattpocock/dictionary-of-ai-coding) (69 terms), his production repo [course-video-manager](https://github.com/mattpocock/course-video-manager) (`CLAUDE.md`, `CONTEXT.md`, 29 ADRs, `CODING_STANDARDS.md`, agent prompts, deep-module package README, AFK platform spec), and transcript summaries of six of his talks and videos (workshop walkthrough, grill-with-docs, handoff, Ralph Wiggum loop, Sandcastle, skills changelog).

---

## 1. The thesis in one paragraph

Agents make coding cheap, so **everything that was already hard about software (alignment, feedback, design, naming) is now the whole job.** His skills are not a framework that owns the process (he names GSD, BMAD, Spec-Kit as the thing he is against). They are small, composable, user-editable habits, each fixing one named failure mode, each producing an artifact the next one consumes. The human stays the strategic programmer: decides what to build, where the seams go, what words mean, what is out of scope. The agent is the tactical programmer inside those bounds. Fundamentals from Ousterhout, Evans, Fowler, Feathers, Beck, and Hunt & Thomas are treated as load-bearing, not nostalgic.

## 2. The four failure modes and their fixes (his README's own framing)

| # | Failure | Root cause | Fix | Skills |
|---|---|---|---|---|
| 1 | "The agent didn't do what I want" | Misalignment. Nobody knows exactly what they want; the agent fills gaps silently with defaults that look like decisions. | A **grilling session** before any code. | `grill-me`, `grill-with-docs`, `grilling` |
| 2 | "The agent is way too verbose" | No shared language. Agent uses 20 words where 1 domain term would do; humans re-explain jargon every session. | A **ubiquitous language** glossary (`CONTEXT.md`) plus ADRs, built inline during grilling. | `domain-modeling`, `grill-with-docs`, `wait-what` |
| 3 | "The code doesn't work" | No feedback loop. Agent flies blind. | **Tight** feedback loops: types, tests, browser. Red-green TDD at pre-agreed seams. A diagnosis discipline that refuses to theorise without a red-capable command. | `tdd`, `diagnosing-bugs`, `implement` |
| 4 | "We built a ball of mud" | Agents accelerate entropy; shallow-module sprawl is the default output. | Care about design every day: **deep modules**, seams, the deletion test. Periodic architecture surveys. | `codebase-design`, `improve-codebase-architecture`, `code-review`, `setup-ts-deep-modules` |

## 3. The skill catalogue

### 3.1 The one axis: user-invoked vs model-invoked

Every skill is one or the other. **User-invoked** (`disable-model-invocation: true`): only a human typing its name fires it; its description is human-facing; it exists to *orchestrate*; no other skill can call it. **Model-invoked**: agent or human can reach it; description carries rich trigger phrasing; it holds the *reusable discipline* or *shared vocabulary*. Rule: a user-invoked skill may call model-invoked skills, never another user-invoked one. Dependencies are expressed as "Call the Skill tool with `"grilling"`", one skill per call, never as prose mentions or cross-folder file links.

The test for model-invoked: *could the model usefully reach for this autonomously?* Reuse alone is not the test.

### 3.2 Engineering skills

| Skill | Invocation | One-line job | Reads | Writes / produces | Depends on |
|---|---|---|---|---|---|
| `setup-matt-pocock-skills` | user | Run once per repo. Configures issue tracker (GitHub / GitLab / local `.scratch/` / other), triage label mapping, domain-doc layout. | git remote, existing `CLAUDE.md`/`AGENTS.md`, monorepo signals | `docs/agents/issue-tracker.md`, `domain.md`, `triage-labels.md`, an `## Agent skills` block in `CLAUDE.md` | none |
| `ask-matt` | user | Router. Describe your situation, get told which skill or flow to type next. Recommends and stops. | its own hand-written map, `PHASE-BOUNDARIES.md` | nothing | none |
| `grill-with-docs` | user | Two-line skill: call `grilling` + `domain-modeling`. The stateful grill for a repo. Head of the main flow. | code, `CONTEXT.md`, ADRs | `CONTEXT.md` terms inline, ADRs when three gates pass | `grilling`, `domain-modeling` |
| `to-spec` | user | Synthesise the conversation into a spec. **No interview.** Sketches test seams first and confirms them. Publishes to tracker with `ready-for-agent`. | conversation, repo, glossary, ADRs | one spec issue (Problem, Solution, long User Stories, Implementation Decisions, Testing Decisions, Out of Scope, Notes). No file paths, no snippets except prototype-derived decision snippets. | setup (hard) |
| `to-tickets` | user | Break spec/plan/conversation into **tracer-bullet** tickets with **blocking edges**. Quizzes user on granularity and edges before publishing. Prefactor first. Wide refactors go expand→migrate→contract. | spec, codebase | one issue per ticket (native blocking links on real trackers; `.scratch/<feature>/issues/NN-slug.md` locally) | setup (hard) |
| `implement` | user | Five lines: build from spec/tickets, use `tdd` at pre-agreed seams, typecheck often, single test files often, full suite once, `code-review`, commit to current branch. Never reopens the plan. | ticket/spec | commit | `tdd`, `code-review` |
| `triage` | user | State machine over *incoming* issues (never your own tickets): `needs-triage` → `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`. Verifies the claim first. Grills if needed. Writes durable **agent briefs**. Rejected enhancements go to `.out-of-scope/`. | tracker, `.out-of-scope/`, codebase | labels, comments prefixed with an AI disclaimer, briefs, `.out-of-scope/*.md` | setup (hard), `grilling`, `domain-modeling` |
| `wayfinder` | user | Plan an effort too big for one session as a **map** issue with **decision tickets** (research / prototype / grilling / task). Plan, don't do. One ticket per session. Fog of war. Hands off to `to-spec`. | tracker | map issue, child tickets, resolution comments | setup, `grilling`, `domain-modeling`, `research`, `prototype` |
| `improve-codebase-architecture` | user | Survey for **deepening opportunities**, scoped to recent hot spots (YAGNI). Self-contained HTML report in temp dir with before/after diagrams and Strong / Worth exploring / Speculative badges. Then grill the candidate you pick. Never changes code. | git log, code, `CONTEXT.md`, ADRs | HTML report, `CONTEXT.md` edits, ADR offers on rejection | `codebase-design`, `grilling`, `domain-modeling` |
| `codebase-design` | model | **Reference, not a process.** The deep-module glossary: module, interface, implementation, depth, seam, adapter, leverage, locality. Four principles. Two disclosed files: `DEEPENING.md` (dependency categories) and `DESIGN-IT-TWICE.md` (parallel sub-agents design 3+ radically different interfaces). | | nothing | none |
| `domain-modeling` | model | The *active* discipline: challenge terms against glossary, sharpen fuzzy words, stress-test with scenarios, cross-reference code, update `CONTEXT.md` inline, offer ADRs sparingly. | `CONTEXT.md`, `CONTEXT-MAP.md`, code | `CONTEXT.md`, `docs/adr/NNNN-slug.md` | none |
| `tdd` | model | Reference for the red→green loop. Tests at **pre-agreed seams** only. Three anti-patterns: implementation-coupled, tautological, horizontal slicing. **No refactor step** (moved to review). | `CONTEXT.md`, ADRs | tests + code | `codebase-design` (for vocabulary) |
| `code-review` | model | Two-axis review of `git diff <fixed>...HEAD` in **parallel sub-agents**: Standards (repo docs + 12 Fowler smells) and Spec (does it match the originating issue?). Never merged, never re-ranked. Fails fast on bad ref / empty diff. | diff, standards files, spec | report | setup (for spec lookup) |
| `diagnosing-bugs` | model | Six gated phases. Phase 1 is the skill: build a **tight, red-capable** feedback loop before any hypothesis. Then minimise, 3–5 falsifiable hypotheses shown to user, instrument one variable at a time with tagged logs, regression test before fix (only at a correct seam), cleanup. Redact secrets. | code, `CONTEXT.md`, ADRs | fix, regression test, commit message naming the true hypothesis | none |
| `prototype` | model | Throwaway code that answers **one** question. Logic branch: single shareable HTML file with a pure liftable module. UI branch: 3–5 radically different variants on one route behind `?variant=`. Prototype kept as a **primary source** on a `prototype/<name>` branch. | | HTML file or variants; the validated decision folds into real code | none |
| `research` | model | Background agent investigates against **primary sources** only, writes one cited Markdown file where the repo keeps notes. | | markdown file | none |
| `resolving-merge-conflicts` | model | Hunk by hunk, resolve by **intent traced to primary sources** (commits, PRs, issues). Never invent behaviour. Never `--abort`. Run the repo's checks. Finish. | git history | resolved commit | none |
| `wizard` | model | Generate a bash wizard from a fixed `template.sh` library for steps only a human can do (credentials, dashboards, cutovers). Agent scopes stages from `.env*`, CI `secrets.*`; never runs it. | repo config | a bash script | none |

### 3.3 Productivity skills

| Skill | Invocation | Job |
|---|---|---|
| `grilling` | model | **The primitive.** Design tree; ask the whole **frontier** per round (numbered, each with a `➡️` recommendation); facts are the agent's job (dispatch sub-agents), decisions are the user's; done when frontier is empty; act only after user confirms shared understanding. Six lines. |
| `grill-me` | user | One line: call `grilling`. Stateless. For anything, anywhere. |
| `handoff` | user | Compact conversation into a portable markdown file in the OS temp dir. Reference other artifacts, don't duplicate. Redact. Include "suggested skills". Narrow: only when something must *travel*. |
| `teach` | user | Stateful teaching workspace: `MISSION.md`, `RESOURCES.md` (never trust parametric knowledge), lessons as HTML, reference sheets, learning records, ZPD. |
| `to-questionnaire` | user | Grill the **send** (who, what you need back), not the subject. Produces a markdown questionnaire for one other person. |
| `wait-what` | user | Three lines. Re-pitch the last message in Simplified Technical English using `CONTEXT.md` vocabulary. The leading word is *wait*: names the listener's state, not the output. |
| `writing-for-agents` | model | The reference for writing any document an agent reads. See §5. |

### 3.4 In-progress and misc (not shipped in the plugin)

`implement-spec` (task-graph implementer subagents in worktrees, merger subagent, single PR), `pr` (PR body: summary visual from primary source, before/after evidence, one-way/two-way door, blast radius; credited to Dex Horthy's `show-me`), `retro` (stub: suggest environment improvements after a session; mechanical rules become deterministic checks, judgement calls go to `CODING_STANDARDS.md`; the review agent enforces standards, not the implementer), `setup-ts-deep-modules` (dependency-cruiser rules: entry points at package root are public, every subfolder private, tests through entry points, no cycles, no barrels, **prove the rule bites**), `loop-me`, `claude-handoff`, `writing-fragments` / `writing-beats` / `writing-shape` (explore vs exploit for prose), `git-guardrails-claude-code`, `setup-pre-commit`, `migrate-to-shoehorn`, `scaffold-exercises`.

### 3.5 How the published site groups them (aihero.dev/skills)

The site index groups by *when you reach for a skill*, which is a better mental model than the repo's engineering/productivity buckets:

| Group | Skills | Site's one-liner |
|---|---|---|
| Getting Started | `setup-matt-pocock-skills`, `ask-matt` | Set up once, then find your way around. |
| The Main Flow | `grill-with-docs` → `to-spec` → `to-tickets` → `implement` → `code-review` | The idea→ship spine, in order. |
| Shaping | `wayfinder`, `prototype`, `research` | Explore an open question and produce a decision or answer that feeds the flow. |
| Upkeep | `improve-codebase-architecture`, `diagnosing-bugs`, `resolving-merge-conflicts`, `triage`, `wizard` | Keep the codebase and issue list healthy; generates work for the flow. |
| Productivity | `grill-me`, `handoff`, `to-questionnaire`, `teach`, `wait-what`, `writing-for-agents` | Human-facing workflows you run, not about code. |
| Reference | `codebase-design`, `domain-modeling`, `grilling`, `tdd` | The reusable layer other skills invoke or cite. |

The site's own definition of a skill, in three beats: **the problem** (an agent is only as good as the process you give it; left to guess, it produces plausible code that quietly rots the codebase), **the fix** (a skill encodes one good habit so the agent runs it the same way every time), **why it compounds** (skills form a chain; each one's output is the next one's input, so the whole workflow gets better as you tune single steps). Everything is MIT and works in any agent (Claude Code, Cursor, Codex, Copilot, Amp, Gemini CLI via skills.sh).

## 4. The flows (from `ask-matt`)

**Main flow, idea → ship:**

```
grill-with-docs → [prototype detour via handoff if a question needs runnable code]
               → small build?  yes → implement (same window)
                                no  → to-spec → to-tickets → implement per ticket (/clear between) → code-review
```

Keep grilling, spec, and tickets in **one unbroken context window**; each `implement` starts fresh from its ticket. The limit is the **smart zone** (~150k tokens on frontier models; quality degrades long before the window is full). If a session nears it before `to-tickets`, `/compact` at a phase boundary.

**On-ramps:** `triage` (work that arrived from others), `diagnosing-bugs` (something broken; hands off to `improve-codebase-architecture` when there's no seam to lock the bug down), `wayfinder` (too foggy and too big for one session; merges back at `to-spec`).

**Codebase health:** `improve-codebase-architecture` every few days; it *generates an idea* that re-enters at `grill-with-docs`.

**Vocabulary underneath:** `domain-modeling` (words of the domain) and `codebase-design` (shape of a module). Every other skill speaks these.

**Phase boundaries** (the decision at the end of a phase, in order; first yes wins):
1. **Continue** if the next phase needs this one as a primary source or there's smart zone left. Rule it out first; it's the only move that keeps the conversation a primary source.
2. **`/clear`** if the context is disposable. Cheapest, one-way.
3. **`/handoff`** only if something must travel (new harness, new directory, colleague, forked side task).
4. **Subagent** if the task is scoped tightly enough to run AFK.
5. **`/compact`** otherwise. The default, at the bottom, never the first reach. Pass it an instruction.

## 5. How he writes for agents (the meta-discipline)

This is the part most transferable to building any agent. From `writing-for-agents` and its `SKILL-MECHANICS.md`:

- **Context pointers.** A skill description or an `AGENTS.md` line is a pointer to out-of-context material; its *wording* decides whether the agent reaches it. Front-load the leading word; one trigger per branch; cut identity the body already carries.
- **The two loads.** *Context load* (always-loaded tokens, paid every turn) vs *cognitive load* (the human remembering what exists). Cognitive load is the price of human agency, not a cost to minimise blindly.
- **Information hierarchy.** In-file steps → in-file reference → disclosed reference behind a pointer. **Progressive disclosure** protects the hierarchy; inline what every branch needs, disclose what only some branches reach. **Co-locate** a concept's definition, rules, and caveats. **Sprawl** is the failure.
- **Completion criteria.** Every step ends on a checkable, demanding done-condition. Vague bounds invite **premature completion**; sharpen the bound before hiding later steps.
- **Leading words.** A pretrained concept the agent thinks with (*tight*, *red*, *tracer bullet*, *fog of war*, *seam*, *frontier*). Repeated as a token, never re-explained. Collapse restatements into one word. Coined words cost definition tokens and recruit no priors.
- **Negation is a weak modifier.** "Don't think of an elephant." State the positive target behaviour; use a prohibition only as a hard guardrail, paired with the positive.
- **Pruning.** Single source of truth (the environment is one too; a doc restating `package.json` is a cache). Relevance check per line. Hunt **no-ops**: a sentence the model already obeys by default pays load to say nothing; delete the sentence, not words. **Sediment** is the default fate without pruning.
- **Splitting.** By sequence (when later steps tempt rushing the current one) or by invocation (when a distinct leading word should trigger it alone). A **router skill** cures piled-up cognitive load.
- **Opinionated over configurable.** "Config is death." Preferences go in the user's own `CLAUDE.md` as plain instructions.
- **Skills are habits, not agents.** Each encodes one good habit so the agent runs the same *process* every time; outputs chain.

Evidence this works: `grilling` is six lines, `grill-me` one, `implement` five, `wait-what` three. The heavy skills (`diagnosing-bugs`, `wayfinder`, `triage`) are heavy because they carry gates and state, not exposition.

## 6. What he teaches about writing code and the workflow

Numbered so they can be argued with.

1. **No one knows exactly what they want** (Hunt & Thomas). So the first act is an interview, not a plan. Grilling inverts the agent's habit of filling gaps with defaults. Facts the environment can answer are the agent's job; decisions are the human's.
2. **Shared understanding is a *design concept*** (Brooks). The conversation, the spec, and the code are all assets trying to capture it. You know it's shared when the other party answers questions you haven't asked the way you would. Writing a spec too early captures misalignment durably.
3. **Ubiquitous language is the compression layer** (Evans). `CONTEXT.md` is a glossary and nothing else: term, one-or-two-sentence definition of what it *is*, `_Avoid_` synonyms. Project-specific concepts only. Opinionated. Written inline the moment a term resolves. Payoff: consistent names in code, files, UI, tickets, and fewer tokens spent thinking. His own repo's `CONTEXT.md` has ~100 terms and a "Flagged ambiguities" section; ADR 0017 documents a three-step rename cascade to free the word "Beat".
4. **ADRs are rare and tiny.** Offer one only when all three hold: hard to reverse, surprising without context, a real trade-off. Title plus one to three sentences. Record the explicit no-s. Their job is to stop the next engineer "fixing" something deliberate.
5. **The spec is a destination document, not a compiler.** It records decisions already made, in the project's words, so a fresh session can pick up without re-explaining. Long user stories, implementation decisions, testing decisions, explicit out-of-scope. No file paths (they go stale). It earns its step only on multi-session work; small builds go straight to implement.
6. **Tracer bullets, not layers** (Hunt & Thomas). Each ticket is a narrow but complete vertical slice through schema, API, UI, tests; demoable alone; sized to one fresh context window. Horizontal slicing (all DB, then all API, then all UI) is how agents code blind and produce slop. The exception is the wide mechanical refactor: expand → migrate in batches → contract.
7. **The rate of feedback is your speed limit.** Types, single test files, full suite once, browser checks, CI. A flaky check is a broken check. Agents are only as reliable as their checks; in AFK runs checks are the only verification happening.
8. **TDD is red→green at pre-agreed seams.** Write the failing test first; only enough code to pass; one slice per cycle. Confirm the seams before any test exists; prefer existing seams, the highest possible, ideally one. Tests describe *what* through the public interface and survive refactors. Expected values come from an independent source of truth (never recomputed the way the code computes them). Mock only at system boundaries (external APIs, time, randomness, sometimes FS/DB); never your own modules. Prefer SDK-style boundary interfaces over generic fetchers. Don't test trivial functions or thin delegation. **Refactoring was removed from the loop** because agents never did it and review works better as a separate session.
9. **Deep modules** (Ousterhout, redefined). Depth is *leverage at the interface*: behaviour exercised per unit of interface learned. Not the line-count ratio (rewards padding). The interface is everything a caller must know: signature, invariants, ordering, error modes, config, performance. Principles: depth is a property of the interface, not the implementation; the **deletion test** (delete it; does complexity vanish or reappear across N callers?); **the interface is the test surface**; **one adapter is a hypothetical seam, two is a real one**. Vocabulary is enforced: never "component", "service", "API", "boundary". Testability rules: accept dependencies, return results, small surface. Enforce with tooling (his TS repo uses dependency-cruiser: root files public, subfolders private, no barrels, prove the rule bites).
10. **Prefactor: make the change easy, then make the easy change** (Beck). Architecture surveys are scoped to where change is landing (git log hot spots), because a deepening in dormant code is a refactor you never cash in.
11. **Review on two axes, separately, from fresh context.** Standards (repo docs first, then Fowler's twelve smells as labelled judgement calls; tooling-enforced things are skipped) and Spec (missing, scope creep, wrong). Never re-rank across axes. The session that wrote the code reviewing it is "confirmation bias with a slash command". Mechanical rules belong in linters and hooks, not prose; prose standards are for judgement calls; the reviewer enforces standards so the implementer's context stays light.
12. **Diagnosis is a feedback loop first.** A bug without a red-capable command is not yet debuggable. Tighten the loop (fast, deterministic, sharp, agent-runnable). Raise the reproduction rate of flakes. Minimise until every element is load-bearing. Rank falsifiable hypotheses before testing any. One variable at a time. No correct seam for the regression test is itself the architectural finding.
13. **Prototype when talking stops working.** Some questions are ungrillable (how it feels, whether an API is ergonomic). Build the throwaway, look, answer in one line. Keep the prototype as a primary source on a branch; only the decision enters main.
14. **Primary sources over secondary.** Code over docs; the diff over the agent's narration; commit messages and issues over "ours/theirs". Every compaction, handoff, subagent report, and summary is lossy by construction; carry a pointer back to the original.
15. **Context is a budget.** Attention per token is fixed; more context dilutes the signal. One task per session. Size tickets to the smart zone. Clear or compact at phase boundaries, never mid-phase. Remove context to recover, don't re-paste.
16. **Human-in-the-loop vs AFK is a deliberate split.** Grilling and prototyping are HITL by nature (your reactions are the input). Well-specified, low-risk, easy-to-verify work is AFK. Resolve ambiguity before an AFK run, gate with automated checks and review during, end in a PR after. Nothing merges to main without a human.
17. **The loop beats the swarm.** Ralph Wiggum: one capable agent in a bounded loop over a backlog, one story per iteration, durable progress memory, a commit per feature, checks non-negotiable. Sandcastle scales this with sandboxes and planner / implementer / reviewer / merger roles; the orchestrator owns tracker mutations, the agent only emits files.
18. **Optional parameters are a bug source.** From his own coding standards: scrutinise them; prioritise correctness over backwards compatibility. Read all config at the edge, at startup, so a missing variable fails before work starts. Filters are part of the entity's definition and must move with the data shape.
19. **Naming is design.** A term that can't get an honest name signals a murky design (Mysterious Name smell). Rename cascades are worth an ADR.
20. **Skills stay opinionated; adapt via your own instructions.** No caps on questions, no config for cadence. Steer with natural language.

## 7. Known failure modes (from the docs pages' "Common questions")

Worth knowing because a Python agent will inherit the same ones.

- A skill that delegates to two others (`grill-with-docs`) sometimes loads only one; the tell is a question dump with no recommendations and no `CONTEXT.md` changes.
- `CONTEXT.md` bloats into a spec unless the "glossary and nothing else" rule is held; the fix is a direct instruction to prune.
- Round-based grilling is contested; a global one-line instruction restores one-at-a-time. No question cap, by design.
- Reference skills (`codebase-design`) invoked as drivers cause runaway re-exploration. Drive with a process skill; consume the reference.
- `to-tickets` over-decomposes and sometimes slices horizontally. Catch at the quiz: "what can I demo when this is done?"
- `implement` never closes tickets or acts on review findings; commits straight to the current branch; runs review before commit so `<fixed>...HEAD` may miss the work.
- `code-review` sub-agents can recursively re-invoke the skill; findings are hypotheses, not evidence; no convergence guarantee.
- `diagnosing-bugs` over-fires on quick questions with some models; there is no gate between instrumentation and fix.
- `research` subagents can nest and duplicate; no source allowlist; no stopping criterion; the file is write-once unless something points at it later.
- `wayfinder` maps of 27 tickets go stale by ticket 13; agents write "this map carries execution" into Notes they own and then build; scope maps to one bounded destination and prototype aggressively.
- Handoff docs capture the what, not the why; a belief written as fact becomes the next session's false premise.

## 8. The canon he draws on, and the Python translation

His references: Hunt & Thomas *The Pragmatic Programmer* (no one knows what they want; tracer bullets; rate of feedback), Evans *Domain-Driven Design* (ubiquitous language, bounded contexts), Beck *Extreme Programming Explained* (invest in design daily; make the change easy), Ousterhout *A Philosophy of Software Design* (deep modules, design it twice), Feathers *Working Effectively with Legacy Code* (seams), Fowler *Refactoring* ch. 3 (smells), Brooks *The Design of Design* (design concept), Michael Nygard (ADRs).

Read for the Python side: Brandon Rhodes' [python-patterns](https://github.com/brandon-rhodes/python-patterns) (composition over inheritance via adapter / bridge / decorator / lists of collaborators; dependency injection as "pass the open file, not the path"; sentinel objects; prebound methods), Percival & Gregory *Architecture Patterns with Python* (domain model as plain classes and dataclasses, entities vs value objects, repository and unit of work as ports, service layer, message bus, DI without a container), faif/python-patterns catalogue, Hynek Schlawack's subclassing/composition work and `typing.Protocol` for structural subtyping.

What translates directly:

- **Module** in Ousterhout's sense maps to a Python package with a small `__init__.py`-free public surface: a few root modules as entry points, `_private/` or leading-underscore subpackages, tests importing only entry points. Enforce with import-linter or a custom check, the way he uses dependency-cruiser.
- **Seam / adapter / port** maps to `typing.Protocol` (structural) or a thin `abc.ABC`, injected through `__init__`. Two adapters (real + in-memory fake) justify the seam; one does not.
- **Deep class** in Python: a small public method set, invariants enforced in `__init__` or a classmethod constructor, `@dataclass(frozen=True)` value objects, no public setters, `__slots__` where it matters. Avoid the subclass explosion; prefer composition and lists of collaborators (the logging-module shape).
- **DRY** the way Fowler means it: one authoritative place per *meaning* (Duplicated Code smell), not identical-looking lines. Speculative Generality is the opposite smell and his review flags it just as hard: abstraction nobody asked for gets deleted, not admired.
- **Ubiquitous language** in Python means module, class, function, and test names drawn from `CONTEXT.md`; enums and status strings especially.
- **Feedback loop** in Python: `mypy --strict` or pyright, `ruff`, pytest on single files while iterating, full suite once, `pre-commit`. A flaky test is a broken check.

Where his TypeScript-shaped advice does not carry over: Effect-style typed errors and DI layers, barrel-file rules, React Router patterns. Python's equivalents are explicit exceptions in the interface contract, constructor injection, and package entry points.

## 9. What this implies for a Python OOP developer agent (first sketch, to be grilled)

The agent is not one prompt. It is a small set of habits with artifacts between them, plus a vocabulary layer, plus deterministic checks in the environment. Proposed shape, mirroring his split:

- **Vocabulary references (model-invoked):** a Python `codebase-design` (deep modules, seams, adapters, Protocols, composition over inheritance, when a class earns its keep, when a function is enough) and a `domain-modeling` that is language-agnostic (reuse his nearly verbatim).
- **Process drivers (user-invoked):** grill-with-docs → to-spec → to-tickets → implement → code-review, adapted only where Python tooling differs.
- **Disciplines (model-invoked):** `tdd` with pytest/hypothesis specifics and the three anti-patterns; `diagnosing-bugs` unchanged; a Python `code-review` whose Standards axis carries Fowler's smells plus a Python baseline (mutable defaults, optional-parameter scrutiny, boolean flags, God objects, inheritance for reuse, `Any` leakage, bare `except`, side effects in `__init__`, module-level state).
- **Environment:** `CONTEXT.md`, `docs/adr/`, `CODING_STANDARDS.md` read by the reviewer not the implementer, import-boundary lint, strict typing, pre-commit.

Open questions that change the design are in the accompanying message.
