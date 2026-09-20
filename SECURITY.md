# Security Policy

This plugin ships hook scripts that run on a user's machine, and its baseline writes checks and scripts into target repositories. We take that seriously.

## Reporting a vulnerability

**Do not open a public issue for security problems.**

Report privately via [GitHub Security Advisories](https://github.com/fbhadha/py-dev/security/advisories/new).

Please include:

- The file (and line) affected.
- What the issue is and how to reproduce it.
- The impact (data exfiltration, remote code execution, destructive action, etc.).

We aim to acknowledge reports within 5 business days and to coordinate a fix and disclosure timeline with you.

## What we screen for

Every change is reviewed before merge. We reject or require changes for anything that:

- Fetches and executes remote code (`curl … | sh`, `wget … | bash`, `eval "$(...)"`).
- Exfiltrates files, secrets, or environment variables to third parties.
- Performs destructive filesystem or git operations without explicit user intent. The `guard_command.py` hook exists to deny exactly those.
- Obfuscates behavior or hides network calls.

The `security-scan` CI job surfaces common risky patterns for manual review, but human review is the real gate.

## For users

The plugin runs with your privileges. Before installing it, read `agents/`, `hooks/hooks.json`, `scripts/` and the `skills/py-baseline/templates/` it will copy into your repo. Upstream skills (Matt Pocock's, Repowise's, Google's) are installed from their own repositories; review them there.
