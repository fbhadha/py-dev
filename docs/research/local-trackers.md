# Research: local, open-source issue trackers with blocking edges

Verified 2026-09-20 by reading each project's repository (README, docs, source, releases). Requirements: issues versioned with the repo; native blocked-by edges and a frontier query; labels for the five triage roles plus `later`; an agent-drivable CLI; optional MCP, local board, and GitHub/GitLab sync; OSI licence and 2026 activity; offline, no account.

Yes. There is a good local option, and the Pocock skills already ship a bare fallback that it would replace: `setup-matt-pocock-skills/issue-tracker-local.md` (markdown files under `.scratch/`) has no native blocking and no frontier query; the agent scans files by hand. Every candidate below fixes that except git-bug.

## Comparison

| Candidate | Storage (req 1) | Blocking edges + frontier (req 2) | Labels (req 3) | Agent CLI (req 4) | MCP / UI (req 5) | GitHub sync (req 5) | Licence / activity (req 6) |
|---|---|---|---|---|---|---|---|
| **Backlog.md** v1.52.0 (`backlog`) | One Markdown file per task with YAML frontmatter in `backlog/tasks/`, committed with normal git. `backlog init --defaults --no-git` = no git needed at all. Offline, no account (MANIFESTO.md). | Native `dependencies:` frontmatter; `--dep` on create/edit; self-refs and cycles rejected (commit 1cacf62). Frontier: `task list --ready` (src/cli.ts 2989); JSON carries `isReady`, fails closed on unknown deps. Gap: `edit --dep` replaces the whole list; no single-edge remove (src/cli.ts 3651). | Free-form strings, `--add-label/--remove-label`. All six work as-is. | Full: create, list with filters, edit, comment, `-s Done` (no `close` verb). `--json` with `schemaVersion`, auto `--plain` when piped, lockfile ID allocation. | MCP `backlog mcp start` (task_list has `ready: true`, src/mcp/tools/tasks/handlers.ts 64, 260-263). Web kanban `backlog browser` (127.0.0.1:6420), TUI `backlog board`. | None. Only `--ref <url>` fields and `--json --watch` for a homemade bridge. | MIT. ~6.8k stars, 15 months old, v1.52.0 tagged 2026-09-12, commits 2026-09-19. Single maintainer. Named "mainstream" in mattpocock/skills `.out-of-scope/mainstream-issue-trackers-only.md`. |
| **beads** v1.3.0 (`bd`) | Dolt SQL DB at `.beads/embeddeddolt/`, gitignored by design (cmd/bd/doctor/gitignore.go L12-52). Only `.beads/issues.jsonl` export is git-versionable, opt-in (`export.auto` false), upsert-only on import. | Best in class: typed edges (`blocks`, `parent-child`, `waits-for`...), `bd dep add/remove`, `bd dep cycles`, `bd ready` (with `--claim`), `bd blocked`, `bd defer`. | Free-form; `bd label add/remove`; docs use `needs-triage` as the example. | Full, `--json` everywhere, `--readonly`, `--actor`. Large surface: 70+ commands, 28 schema migrations in 1.3.0. | MCP (`beads-mcp`, Python). `bd graph --html`. No built-in kanban; community `beads-ui`, `bd-board`. | Built in: `bd github sync`, `bd gitlab sync`, plus Jira/Linear/ADO. | MIT. ~27k stars, 11 months old, v1.3.0 2026-09-15, commits 2026-09-19. Moved to gastownhall org. |
| **git-bug** trunk 2f6c384 | Git objects under `refs/bugs/*`; worktree stays clean. Plain `git push`/`clone` do not carry bugs; needs `git bug push/pull`. | **None.** No dependency operation exists (entities/bug/ has 7 op types, none relational; issue #949 open since 2022). No frontier. No negative label filter. | Free-form, `git bug bug label new/rm`. | Good: `--non-interactive`, `--format json`. Identity must be created first. README commands are stale vs trunk. | No MCP. TUI + React web UI with GraphQL. No kanban. | Built in bridges: GitHub, GitLab, Jira (labels, status, comments; no assignee). | GPL-3.0. ~10k stars, 8 years old, but last release v0.10.1 2025-05-18 (16 months); trunk active 2026-09-19. |
| **Taskwarrior** 3.5.0 (`task`) | SQLite `taskchampion.sqlite3`, default `~/.task`; repo-scoping needs `TASKRC`/`TASKDATA` on every call. Versionable only via JSON export discipline or the new encrypted git-sync branch. | Native `depends:`, cycle rejection, `+UNBLOCKED`/`-BLOCKED` virtual tags, `task unblocked` report. | Tags (`+needs-triage`); hyphens allowed since 3.5.0. | Full, non-interactive with `rc.confirmation=0`; JSON export/import; hooks. Numeric IDs renumber after gc (use UUIDs). Single-line descriptions only. | No first-party MCP; third-party ones are thin. TUIs: taskwarrior-tui, vit. No kanban. | Not in core. bugwarrior pulls GitHub issues in (one-way). | MIT. ~6k stars, 20-year project, v3.5.0 2026-08-16, commits 2026-09-15. |
| **ticket / `tk`** v0.3.2 | One Markdown file per ticket in `.tickets/`, plain git. Single bash script. | `tk dep`, `tk undep`, `tk dep cycle`, `tk ready`, `tk blocked`. Verified by execution. | `--tags` at create only; **no command to add/remove a tag later** (rewrite frontmatter or write a plugin). | Good: prints bare ID, partial IDs, `tk add-note`, `tk query` (needs jq). No `--json` on core commands. | None. Plugin system only. | None (`--external-ref` field only). | MIT. ~900 stars, created 2026-01-02, **no commits since 2026-03-15** with 42 open issues/PRs. |

Also examined: chainlink (SQLite gitignored, MIT, last commit 2026-08-09), pad (SQLite in `~/.pad`, cloud upsell). "dex" is the tracker named in mattpocock/skills issue #99 (~300 stars, 3 months old at the time); no matching repo was found.

## Recommendation

**Default local tracker: Backlog.md.**

In plain terms: when a repo has no GitHub or GitLab remote, the skills need somewhere to write tickets that (a) travels with the code when you copy or commit the repo, (b) understands "ticket B cannot start until ticket A is done" and can answer "what can I start right now?", and (c) an agent can drive from the command line without a human clicking anything. Backlog.md is the only candidate that does all three without workarounds:

1. Its tickets are ordinary Markdown files inside the repo. `git add backlog/` and they are versioned, diffable in a PR, and readable in any editor. No database, no daemon, no home-directory state, no account.
2. It has real dependency edges and a `--ready` switch that lists only open, unblocked tickets. It refuses cycles. Its readiness check fails closed: if a dependency is missing or ambiguous the ticket is treated as blocked, which is the safe direction for an unattended agent.
3. The CLI covers every operation the skills call (create, list with filters, relabel, add dependency, comment, close) and prints versioned JSON when piped.
4. It also gives a human a local kanban board (`backlog browser`) and Claude an MCP server, so the "see the frontier visually" requirement in wayfinder is met.
5. It is MIT, released eight days ago, committed to this week, and Matt Pocock's own out-of-scope note already lists it beside GitHub and GitLab as "mainstream", so a Backlog.md backend is the one upstream would plausibly accept.

Its one real gap is no export or sync to GitHub or GitLab issues. For a repo with no remote that is not a blocker today, and the `--ref` field plus `--json --watch` output leaves a path for a script later. Its one CLI wart is that `edit --dep` replaces the whole dependency list, so removing a single edge means re-issuing the remaining ids.

**Runner-up: beads.** It lost because its source of truth is a gitignored Dolt database, so with no remote the issues do not ride in ordinary git commits unless you turn on and commit a JSONL export, and that export cannot express deletions.

Why the rest lost in one line each: git-bug has no dependency edges at all; Taskwarrior keeps its data outside the repo and needs env-var scoping on every call; tk has stalled for six months and cannot relabel a ticket after creation.

## What `docs/agents/issue-tracker.md` would need to say

Mirrors `/tmp/claude-0/-home-user-Skills/0ffd5757-3c3e-5c5b-aacd-7836fc97a45a/scratchpad/pocock/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md`. `docs/agents/triage-labels.md` keeps its right-hand column unchanged; Backlog.md labels are free-form. Optionally list them under `labels:` in `backlog/config.yml` for autocomplete.

```markdown
# Issue tracker: Backlog.md

Issues and specs for this repo live as Markdown task files under `backlog/tasks/`
(one file per task, YAML frontmatter), managed by the `backlog` CLI (npm package
`backlog.md`, or `npx backlog.md`). If `backlog/config.yml` is missing, run
`backlog init --defaults --no-git` once. Commit the `backlog/` directory with the
code. Always pass `--plain` or `--json`; never rely on the interactive UI.

## Conventions

- **Create an issue**: `backlog task create "<title>" -d "<body>" -l needs-triage --plain`.
  Use `-d "$(cat <<'EOF' ... EOF)"` for multi-line bodies. Prints the new id (`task-12`).
- **Read an issue**: `backlog task task-12 --json` (title, body, labels, dependencies,
  comments, `readiness`, `dependencyGraph`), or `--plain` for text.
- **List issues**: `backlog task list --exclude-status Done -l ready-for-agent --json`.
  `-l` requires every listed label (AND). Add `--ready`, `--unassigned`, `--search "<text>"`,
  `--sort id`, `--parent <id>` as needed.
- **Comment on an issue**: `backlog task edit task-12 --comment "<text>" --comment-author @triage`
  (append-only).
- **Apply / remove labels**: `backlog task edit task-12 --add-label ready-for-agent --remove-label needs-triage`.
- **Close**: there is no close verb. Set the terminal status: `backlog task edit task-12 -s Done`
  (the last entry of `statuses` in `backlog/config.yml`). Comment first with a separate
  `--comment` edit. For `wontfix`: `--add-label wontfix`, then `-s Done`. Optionally
  `backlog task complete task-12` moves the file to `backlog/completed/`.
- **"later"**: apply the `later` label and leave the task open.
- **Ids in commits**: reference tasks as `task-12`, never `#12`; `/code-review` reads these.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(This repo has no remote; there are no PRs.)_

## When a skill says "publish to the issue tracker"

`backlog task create "<title>" -d "<spec or ticket body>" -l ready-for-agent --plain`
(`needs-triage` instead when the skill says so). For `/to-tickets`, create blockers first,
then wire edges in a second pass: `backlog task edit <id> --dep <blocker-id>,<blocker-id>`.

## When a skill says "fetch the relevant ticket"

Run `backlog task <id> --json`. If the user passes a file path instead, read
`backlog/tasks/<id> - <slug>.md` directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single task with **child** tasks as tickets.

- **Map**: `backlog task create "<effort> map" -l wayfinder:map -d "<Destination / Notes /
  Not yet specified / Out of scope body>"`. Decisions-so-far is kept in the map's notes so it
  is append-only and safe under concurrent sessions:
  `backlog task edit <map-id> --append-notes "- [<ticket title>](backlog/tasks/<file>): <gist>"`.
- **Child ticket**: `backlog task create "<title>" -p <map-id> -l wayfinder:<type> -d "<question>"`
  (`research`/`prototype`/`grilling`/`task`). List children: `backlog task list --parent <map-id> --json`.
  Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: Backlog.md's **native** `dependencies` field, visible in `backlog browser` and in
  `backlog task <id> --plain` as a dependency graph. Add edges after both tasks exist:
  `backlog task edit <child-id> --dep <blocker-id>,<blocker-id>`. This SETS the full list, so
  to drop one edge re-issue it with the remaining ids, or `--clear-deps`. Self-references and
  cycles are rejected. A ticket is unblocked when every blocker is `Done`; readiness fails
  closed if a blocker id is unknown.
- **Frontier query**:
  `backlog task list --parent <map-id> --ready --unassigned --exclude-status Done --sort id --json`.
  `--ready` alone does not drop Done tasks, hence `--exclude-status`. First row wins.
- **Claim**: `backlog task edit <id> -a @<dev>` (optionally `-s "In Progress"`), the session's
  first write.
- **Resolve**: `backlog task edit <id> --comment "<answer>" --comment-author @<dev>`, then
  `backlog task edit <id> -s Done`, then append the context pointer to the map's notes as above.
- **Out of scope**: `backlog task edit <id> --add-label out-of-scope`, then `-s Done`, and add
  one line to the map's Out of scope section with `-d` (or `backlog task archive <id>` for a
  task that is not yet Done).
```

## UNVERIFIED

- No candidate binary was installed or run in this session except git-bug (trunk build) and tk. Every Backlog.md, beads and Taskwarrior command above comes from docs and source option definitions (Backlog.md: src/cli.ts, CLI-INSTRUCTIONS.md, README.md), not a live run.
- Whether `backlog task edit` accepts `--comment` and `-s Done` in the same invocation; the doc draft splits them to be safe.
- Whether `backlog task list --parent <id>` returns direct children only or all descendants (src/cli.ts 2971 says "filter tasks by parent task ID"; depth not checked).
- Whether `--append-notes` writes to the "Implementation Notes" section and renders in the web UI for a map task; assumed from the flag name (src/cli.ts 637) and CLI-INSTRUCTIONS.md.
- Whether `--parent`, `--ready`, `--unassigned`, `--exclude-status` and `--sort id` combine without conflict on one `task list` call; they are all options on the same command (src/cli.ts 2964-2989) but no combination error paths were read.
- Whether `backlog init --defaults --no-git` is fully non-interactive in a non-TTY (both flags exist, src/cli.ts 1062-1063; not run).
- Backlog.md `config.yml` `labels:` list is autocomplete only, not validation (src/cli.ts 5163/5484 per candidate report); not re-read here.
- GitHub Releases publish timestamps for Backlog.md v1.52.0, beads v1.3.0 and Taskwarrior v3.5.0 (Releases API blocked); dates are git tag dates.
- Star and fork counts are single GitHub API snapshots from 2026-09-20.
- beads: fresh-clone recovery from a committed `.beads/issues.jsonl` with no Dolt remote is documented (docs/reference/configuration.md `import.auto`, `bd init --from-jsonl`) but untested; community UIs not checked.
- git-bug: bodies of issues #949 and #1519; whether a manual `refs/bugs/*` refspec is safe.
- Taskwarrior: relative `data.location` resolution; hook protocol read only from test scripts; bugwarrior direction inferred from README wording.
- tk: Homebrew/AUR packaging and Windows support not tested; maintainer responsiveness after March 2026 unreadable.
- Whether mattpocock/skills has since added a Backlog.md backend or a dependency-aware local backend; only `.out-of-scope/mainstream-issue-trackers-only.md` and the three shipped templates (`issue-tracker-{github,gitlab,local}.md`) were read.
- "dex": no repository matching an agent issue tracker by that name was found on GitHub; the name comes from mattpocock/skills issue #99 as cited in the out-of-scope note.
