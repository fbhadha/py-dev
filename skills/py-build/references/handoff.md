# Handoff template

A handoff is the one file a fresh session reads before it does anything. It is written for the floor reader: follow the six rules under `## The six rules` in `py-shape`'s `references/floor-reader.md`.

How to fill it:

- Keep every heading, in this order.
- If a heading has nothing to say: write one line that says so, for example "none: the spec is complete".
- Write every command on its own line, inside a code block.
- Write every path, branch name, ticket number and commit hash in full.
- Write no key, token or password.

````markdown
# Handoff: after <ticket id>, <what it made true>

Written <date> by the session that <built | shaped> <ticket or spec id>. Repo: <owner/name>. Tracker: <from `docs/agents/issue-tracker.md`>.

## Do this first

1. Run `git fetch origin`.
2. Run `git switch <branch>`.
3. Run `git status -sb`. Expected: `<the exact first line>` and nothing else.
4. If the tree is not clean: stop and report.
5. <The next command, one per step, each with its expected output.>

## Branch

- Branch: `<name>`.
- If it merged: "merged as pull request #<n>, merge commit `<hash>`, branch deleted".
- If it did not merge: "not merged", then the open pull request's number and what is missing.

## Spec

<The spec's id and title, or "none: one-ticket change".>

## What was delivered

- <One line per behaviour the ticket made true, each with the test or the command that proves it.>
- After shaping, with no ticket built: the spec's id, then one line per ticket written.

## Next ticket

- <The next ticket on the frontier (the open tickets that nothing blocks), by id and title.>
- Why it is next: <one sentence>.
- If there is none: "none: the spec is complete".

## Shape and seams

- Shape: <the how-to the work followed, by path, or "none">.
- Seams (the public functions the tests call): <one per line, with its file>.

## Terms and ADRs touched

- <Each `CONTEXT.md` term or `docs/adr/` file that was added or changed, one per line, or "none".>

## Do not ask again

- <Each decision the user already made, one per line, in the user's words where they gave them.>

## If something fails

1. Stop.
2. Report the command and the last 20 lines of its output.
3. Change nothing else.

No keys, tokens or passwords are in this file.
````
