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
- **"later"**: apply the `later` label and leave the task open. `py-intake later` reviews these.
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

<!-- Commands above come from Backlog.md v1.52.0 docs and source (docs/research/local-trackers.md
     in fbhadha/py-dev), not from a live run. If one misbehaves, fix it here and say so in the commit. -->
