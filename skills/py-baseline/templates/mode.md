# Agent mode

The skills read this file at session start. One key per line; unknown keys are ignored.

mode: guide
explain: before-and-after
unattended: never
protect-existing-files: ask-once

<!--
mode        guide is the only mode in v1. partner is reserved.
explain     before-and-after (default) or after-only.
unattended  never (default), or ticket:<id> to allow one unattended run on that
            ticket, which must come from a grilled spec and must end in a PR.
            the agent clears the value when the run ends.
protect-existing-files
            ask-once (default after intake): the first time in a session the
            agent would change an existing protected file (agent files,
            packaging, checks, CI, docs), the harness asks you; that yes covers
            the rest of the session. Building what was grilled, specified and
            ticketed should not be interrupted per file.
            on: the harness asks once per file per session, and a commit
            touching one must say "approved: <files>". Intake runs this way.
            off: the guards stand down.
            Changing this line is itself a protected change, so the harness asks.
-->
