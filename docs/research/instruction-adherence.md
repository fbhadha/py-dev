# Research: what keeps an agent on its instructions over a long session

Verified 2026-10-03 by fetching each page below. The question: agents built by others stay on their persona for hours; what do they do that this plugin's `python-dev` persona does not? Asked while shaping ticket #79 (the persona did not size the need for a ticket, although the rule to do so was in two files).

## Findings

- Performance degrades as the context fills: "When the context window is getting full, Claude may start 'forgetting' earlier instructions or making more mistakes." ([Claude Code docs, Best practices](https://code.claude.com/docs/en/best-practices))
- A rule in a long file gets lost: "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost." (same page)
- Advisory rules are pruned or turned into hooks: "If Claude already does something correctly without the instruction, delete it or convert it to a hook." (same page)
- Hooks are the only thing that holds every time: "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens." (same page)
- Emphasis works only when rare: "If Claude keeps skipping one instruction, add emphasis such as 'IMPORTANT' to that line alone. If you emphasize many lines, none of them stands out." (same page)
- Rarely needed rules go in skills, loaded on demand: "For domain knowledge or workflows that are only relevant sometimes, use skills instead. Claude loads them on demand without bloating every conversation." (same page)
- Test a rule change by behaviour: "Treat CLAUDE.md like code: review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts." (same page)
- Long sessions are reset, not pushed through: "After two failed corrections, `/clear` and write a better initial prompt incorporating what you learned." (same page)
- Prompts that encode exact behaviour as rules are brittle: the failure mode is "engineers hardcoding complex, brittle logic in their prompts to elicit exact agentic behavior. This approach creates fragility and increases maintenance complexity over time." The aim is "the minimal set of information that fully outlines your expected behavior." ([Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))
- Attention is a budget: "as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases." Long-horizon work uses compaction, notes written outside the context and re-read, and sub-agents that return a summary. (same page)
- Persona drift is measured and general: across 23 models and three real Claude Code sessions of 3,746 to 9,716 turns, drift appears in every model family; compaction does not restore the register; "a single-shot anchor restores the trained register across measured targets." ([ContextEcho, arXiv 2605.24279](https://arxiv.org/abs/2605.24279))
- A secondary source puts reliable instruction-following at roughly 150 to 200 instructions in total, and notes that Claude Code's own system prompt uses part of that before any user file loads. Not verified against a primary source. ([Medium, Why AI agents ignore your CLAUDE.md](https://medium.com/@bartkru/why-agents-ignore-your-claude-md-2149871647ca))

## Second pass, while shaping ticket #82

Verified 2026-10-03 by fetching each page below. The question: which facts do the decisions on #82 (cut the persona, the routing table, a re-anchor hook) depend on?

- A session agent's file replaces the harness's system prompt: "a custom subagent's system prompt replaces the default Claude Code system prompt entirely, the same way `--system-prompt` does." `CLAUDE.md` and project memory "still load through the normal message flow". ([Claude Code docs, Subagents](https://code.claude.com/docs/en/sub-agents))
- Anthropic's own size figure is per file, in lines: "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." Imports "don't reduce its context cost, because imported files also load at launch". ([Claude Code docs, Memory](https://code.claude.com/docs/en/memory))
- Instruction files are advisory: "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead. The more specific and concise your instructions, the more consistently Claude follows them." (same page)
- Conflicting instructions are resolved arbitrarily: "if two instructions contradict each other, Claude may pick one arbitrarily." `/doctor prompt-audit` reports outdated or conflicting instruction files and takes a path. (same page)
- The primary study of instruction count is IFScale: 500 keyword-inclusion instructions, 20 models; "even the best frontier models only achieve 68% accuracy at the max density of 500 instructions", with a "bias towards earlier instructions". Its abstract gives no 150 to 200 threshold; that figure stays secondary. ([arXiv 2507.11538](https://arxiv.org/abs/2507.11538))
- Claude Code can re-inject text on every message: for `UserPromptSubmit`, "Claude Code adds plain-text stdout as context that Claude can see and act on", placed "alongside the submitted prompt"; output is "capped at 10,000 characters". ([Claude Code docs, Hooks](https://code.claude.com/docs/en/hooks))
- Copilot CLI cannot, from a plugin's hooks file: for `userPromptSubmitted`, "`modifiedPrompt` is honored only by SDK programmatic hooks"; "Only `additionalContext` is consumed for `sessionStart`"; `postToolUse` "can modify the tool result or inject additional context for the model". ([GitHub Docs, Hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference))
- Skill descriptions are what routes a skill, and they can be dropped: "The listing always contains every skill name, but if you have many skills, Claude Code drops some descriptions to fit the listing's character budget, which removes the keywords Claude needs to match your request. The budget scales at 1% of the model's context window." A skill with `disable-model-invocation: true` has its "Description not in context". ([Claude Code docs, Skills](https://code.claude.com/docs/en/skills))
- A loaded skill is cut after compaction: Claude Code "re-attaches the most recent invocation of each skill after the summary, keeping the first 5,000 tokens of each"; "Put the most important instructions near the top of `SKILL.md`". (same page)
- Positive phrasing, reasons, and plain emphasis: "Tell Claude what to do instead of what not to do"; "Providing context or motivation behind your instructions ... can help"; "dial back any aggressive language. Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting". ([Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices))
- ContextEcho's abstract confirms the earlier finding ("in-session compaction does not reliably reset it"; "A single-shot anchor restores the trained register") and does not say how often or where the anchor is injected. ([arXiv 2605.24279](https://arxiv.org/abs/2605.24279))

What this means for the plugin, read from the working tree on 2026-10-03:

- The persona is the system prompt, the strongest position there is; `AGENTS.md` and the user's global file arrive as messages. The persona's first lines carry the most weight (IFScale's bias).
- Routing cannot rest on skill descriptions alone: a machine with many skills installed can have descriptions dropped, and the six typed skills have none in context. The persona needs a routing list; it does not need each row's prose.
- `skills/py-intake/SKILL.md` is about 7,600 tokens (27,482 characters at 3.6 per token), over the 5,000 kept after compaction: its last steps (the harness shells, the finish, `later`) are the part lost.
- A per-message re-anchor is possible in Claude Code only. In Copilot CLI the nearest hook that can inject is `postToolUse`.
- `agents/python-dev.md` holds 26 "never" or "do not" phrasings by a rough count.

## Third pass: long procedure skills, and what GitHub Copilot offers

Verified 2026-10-03 by fetching each page below. The questions: how is a long, many-step skill such as `py-intake` normally built, and which of the mechanisms above exist in Copilot?

- The size limit for a skill's main file: "Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files". ([Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- The main file is an index, the detail is in files read on demand: "SKILL.md serves as an overview that points Claude to detailed materials as needed, like a table of contents"; "If workflows become large or complicated with many steps, consider pushing them into separate files and tell Claude to read the appropriate file based on the task at hand." (same page)
- References go one level deep: "Keep references one level deep from SKILL.md", because "Claude may partially read files when they're referenced from other referenced files." A reference file over 100 lines gets a table of contents. (same page)
- Long procedures carry a checklist: "For particularly complex workflows, provide a checklist that Claude can copy into its response and check off as it progresses"; "Clear steps prevent Claude from skipping critical validation." (same page)
- Steps that must be exact become scripts: "Prefer scripts for deterministic operations"; a low-freedom step is "Run exactly this script"; scripts are "More reliable than generated code" and their contents cost no context, "Only the script's output consumes tokens". (same page)
- Fragile steps get a validator and a loop: "Run validator → fix errors → repeat". (same page)
- Skills are tested by watching a fresh session use them: "Create evaluations BEFORE writing extensive documentation"; "at least three evaluations"; work with one session that writes the skill and a fresh one that uses it, "Observing Claude B's behavior". "There is not currently a built-in way to run these evaluations." (same page)
- Only what the model lacks is written down: "Default assumption: Claude is already very smart. Only add context Claude doesn't already have." (same page)
- A Copilot custom agent's body has a ceiling: "The prompt can be a maximum of 30,000 characters." Its documented frontmatter has no `hooks` key. ([GitHub Docs, Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration))
- Copilot hooks that can put text in front of the model: `sessionStart` ("Only `additionalContext` is consumed") and `postToolUse` ("`additionalContext` (string) — Additional guidance appended to `textResultForLlm`"; several hooks' context is "joined with a double newline and capped at 10 KB"). The page also lists `preCompact`, `subagentStart` and `agentStop` events. Plugin hooks are read from the plugin's `hooks.json`. ([GitHub Docs, Hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference))
- Not found: how Copilot chooses a skill, whether its skill listing is cut, and what happens to a loaded skill when Copilot compacts. The concept page says only that skills are loaded "when relevant". ([GitHub Docs, About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills))

What this means for the plugin, read from the working tree on 2026-10-03:

- `skills/py-intake/SKILL.md` is one 27,482-character file holding eleven steps, six tables and the commands for three harnesses and three trackers. The documented pattern is a short main file (the step list as a checklist, each step's "done when" test) with one reference file per step, and scripts for the steps that must be exact.
- Each step of `py-intake` already has a "done when" test in prose. A script that prints which steps hold would make resuming, and the finish step's walk, deterministic.
- The hook that works in both harnesses for text mid-session is the one after a tool call (`PostToolUse` in Claude Code, `postToolUse` in Copilot CLI). The per-message hook works in Claude Code only.
- `/doctor prompt-audit agents/`, run 2026-10-03 in a headless session on Sonnet: three numeric output caps flagged (`agents/python-dev.md` "never more than twenty lines", `agents/py-reviewer.md` "under 500 words", `agents/py-eval.md` "under ten lines"); every path, flag, version and upstream skill name the agents cite exists.

## How this plugin measures against the findings

Read from the working tree on 2026-10-03.

- `agents/python-dev.md` is 14,000 characters, the exact limit `scripts/check_plugin.py` sets (`PERSONA_MAX_CHARS = 14_000`), loaded every turn. The user's global instructions, `AGENTS.md` and the open skill load on top of it.
- The persona is mostly rules of the "when X, run Y" kind (section 5 is a 24-row routing table), the shape the context-engineering essay calls brittle.
- The rule that failed on #75 (size the need before shaping) was present twice, in `agents/python-dev.md` section 3 and `skills/py-shape/SKILL.md` section 2, and was still skipped: the failure the docs describe for a file that is too long.
- The rules that do hold (branch, commit, merge, the never-list) are hooks under `scripts/hooks/`, which matches the finding that only hooks hold every time.
- The persona's section 6 (one ticket per session, write the handoff, stop) matches the finding that long sessions are reset rather than pushed through. Nothing re-anchors the persona inside a session; the research found a single re-injected anchor is what restores it.
