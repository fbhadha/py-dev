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

## How this plugin measures against the findings

Read from the working tree on 2026-10-03.

- `agents/python-dev.md` is 14,000 characters, the exact limit `scripts/check_plugin.py` sets (`PERSONA_MAX_CHARS = 14_000`), loaded every turn. The user's global instructions, `AGENTS.md` and the open skill load on top of it.
- The persona is mostly rules of the "when X, run Y" kind (section 5 is a 24-row routing table), the shape the context-engineering essay calls brittle.
- The rule that failed on #75 (size the need before shaping) was present twice, in `agents/python-dev.md` section 3 and `skills/py-shape/SKILL.md` section 2, and was still skipped: the failure the docs describe for a file that is too long.
- The rules that do hold (branch, commit, merge, the never-list) are hooks under `scripts/hooks/`, which matches the finding that only hooks hold every time.
- The persona's section 6 (one ticket per session, write the handoff, stop) matches the finding that long sessions are reset rather than pushed through. Nothing re-anchors the persona inside a session; the research found a single re-injected anchor is what restores it.
