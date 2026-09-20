# Agent mode

The skills read this file at session start. One key per line; unknown keys are ignored.

mode: guide
explain: before-and-after
unattended: never
protect-existing-files: on

<!--
mode        guide is the only mode in v1. partner is reserved.
explain     before-and-after (default) or after-only.
unattended  never (default), or ticket:<id> to allow one unattended run on that
            ticket, which must come from a grilled spec and must end in a PR.
            the agent clears the value when the run ends.
protect-existing-files
            on (default): the harness asks you before the agent changes an
            existing protected file (agent files, packaging, checks, CI, docs),
            once per file per session, and a commit touching one must say
            "approved: <files>". off: the guards stand down. Changing this line
            is itself a protected change, so the harness asks.
-->
